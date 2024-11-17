import json
import module
import keymouse
from keymouse import mouse
import logger
import time
from threading import Thread
from screeninfo import get_monitors

class Action:
    def __init__(self, inputter: keymouse.Inputs, controller: module.Controller) -> None:
        self.inputter = inputter
        self.controller = controller
        self.logger = logger.get_logger("Action")
        self.current_switched_profile = {}
        self.current_app = ""
        self.app_data = {}
        self.pressed_keys: dict[str, float] = {}
        self.continuous_keys: dict[str, tuple[int, float]] = {}
        self.switch_count: dict[str, tuple[bool, float, int]] = {}
        self.pressing_another_profiles: list[str, dict[str, str | dict]] = []
        self.switched_profile = {}
        self.pre_profile_id: str = ""
        self.primary_monitor = [monitor for monitor in get_monitors() if monitor.is_primary][0]
        self.gyro_x = self.primary_monitor.width // 2
        self.gyro_y = self.primary_monitor.height // 2

        self.is_using_gyro_pointer = False
        self.is_using_stick_keyboard = False
        self.is_using_stick_pointer = False
        self.is_using_stick_wheel = False
    def set_current_app(self, app_path: str) -> None:
        flag = False
        if "ALL" not in self.app_data:
            return
        if app_path != self.current_app:
            if self.current_app in self.current_switched_profile:
                del self.current_switched_profile[self.current_app]
            flag = True
        if app_path not in self.app_data:
            self.current_app = "ALL"
        else:
            self.current_app = app_path
        if len(self.pressing_another_profiles) <= 0:
            if self.current_app not in self.switched_profile:
                self.current_switched_profile[self.current_app] = ""
            else:
                profile_id = self.switched_profile[self.current_app]
                matched_profiles = [profile for profile in self.app_data[self.current_app]["data"] if profile["value"] == profile_id]
                self.current_switched_profile[self.current_app] = matched_profiles[0] if len(matched_profiles) > 0 else ""
        else:
            self.current_switched_profile[self.current_app] = self.pressing_another_profiles[-1]["profile"]
        if flag:
            self.update_led()

    def update_led(self) -> None:
        profile = self._get_current_profile()
        if profile is None:
            return
        for joycon in self.controller.joycons:
            if self.check_use_joycon(joycon.serial, joycon.device_type):
                joycon.set_led_on(profile["led"])
                self.logger.debug(f"Set LED: {profile['led']} ({joycon.serial})")

    def set_app_data(self, app_data: dict, immediate: bool=False) -> None:
        self.app_data = app_data
        if immediate:
            self.set_current_app(self.current_app)

    def take_action(self, serial: str, device_type: str, joycon_event: str, joycon_status: dict | list) -> bool:
        if not self.check_use_joycon(serial, device_type):
            self.logger.debug(f"JoyCon not in use: {serial}")
            return False
        profile = self._get_current_profile()
        if profile is None:
            self.logger.debug("Profile not found.")
            return False
        Thread(target=self._analyze_action, args=(serial, profile["convert"], joycon_event, joycon_status, profile["value"], device_type), daemon=True).start()
        return True

    def check_use_joycon(self, serial: str, device_type: str) -> bool:
        if self.current_app not in self.app_data:
            return False
        use_l = self.app_data[self.current_app]["use_joycon"]["l"]
        use_r = self.app_data[self.current_app]["use_joycon"]["r"]
        if device_type.lower() == "l":
            if not (use_l["isAll"] or serial in [l["serial"] for l in use_l["list"]]):
                return False
        elif device_type.lower() == "r":
            if not (use_r["isAll"] or serial in [r["serial"] for r in use_r["list"]]):
                return False
        else:
            return False
        return True

    def _get_current_profile(self) -> str | None:
        switched = self.current_switched_profile[self.current_app]
        if switched == "":
            if "ALL" not in self.app_data and self.current_app == "ALL":
                return None
            profiles = [profile for profile in self.app_data[self.current_app]["data"] if profile["main"]]
        else:
            try:
                profiles = [profile for profile in self.app_data[self.current_app]["data"] if profile["value"] == switched["value"]]
            except KeyError:
                return None
        if len(profiles) == 0:
            return None
        return profiles[0]

    def _analyze_action(self, serial: str, convert_data: dict, joycon_event: str, joycon_status: dict | list, profile_id: str, device_type: str) -> bool | None:
        if profile_id != self.pre_profile_id:
            if self.pre_profile_id in self.switch_count and self.switch_count[self.pre_profile_id][0]:
                del self.switch_count[self.pre_profile_id]
                self.logger.debug(f"Switch action: reset")
            self.pre_profile_id = profile_id
        if joycon_event == "gyro":
            gyro_key = "left_gyro" if device_type.lower() == "l" else "right_gyro"
            actions = [convert for convert in convert_data if convert["input"]["value"] == gyro_key]
            if len(actions) == 0:
                return None
            action = actions[0]
            action_type = action["value"]["actionType"]
            action_data = action["value"]["data"]
            if action_type == "cursor":
                if self.is_using_gyro_pointer:
                    return None
                pointer = joycon_status[0]
                if pointer is None:
                    return
                pointer[0] *= int(action_data["cursorSpeed"])
                pointer[1] *= -int(action_data["cursorSpeed"])
                pointer[0] += self.gyro_x
                pointer[1] += self.gyro_y
                self.is_using_gyro_pointer = True
                self.inputter.mouse_move(pointer[0], pointer[1], absolute=True)
                self.is_using_gyro_pointer = False
        elif joycon_event == "stick":
            stick_key = "left_stick" if device_type.lower() == "l" else "right_stick"
            actions = [convert for convert in convert_data if convert["input"]["value"] == stick_key]
            if len(actions) == 0:
                return None
            action = actions[0]
            action_type = action["value"]["actionType"]
            action_data = action["value"]["data"]
            is_cardinal = action["value"]["cardinal"]
            stick_data = self.controller.calc_stick_position(serial, joycon_status)
            if stick_data is None or "horizontal" not in stick_data or "vertical" not in stick_data:
                return None
            if is_cardinal:
                stick_data = self.inputter.stick2cardinal(stick_data)
            if action_type == "keyboard":
                if self.is_using_stick_keyboard:
                    return None
                key_data = {
                    "up": [key_data["id"] for key_data in json.loads(action_data["up"][0]["args"])["value"]],
                    "down": [key_data["id"] for key_data in json.loads(action_data["down"][0]["args"])["value"]],
                    "left": [key_data["id"] for key_data in json.loads(action_data["left"][0]["args"])["value"]],
                    "right": [key_data["id"] for key_data in json.loads(action_data["right"][0]["args"])["value"]]
                }
                self.inputter.convert_config["key"]["speed"] = int(action_data["speed"]) / 1000
                self.inputter.convert_config["key"]["is_constant"] = action_data["noaccel"]
                self.inputter.convert_config["key"]["threshold"] = (self.inputter.convert_config["splitted_num"] / 2) * (int(action_data["threshold"]) / 100)
                keys, duration = self.inputter.stick2key(stick_data, key_data)
                self.is_using_stick_keyboard = True
                self.inputter.press_keys(keys, duration)
                self.is_using_stick_keyboard = False
            elif action_type == "cursor":
                if self.is_using_stick_pointer:
                    return None
                self.inputter.convert_config["pointer"]["speed"] = int(action_data["speed"]) / 1000
                self.inputter.convert_config["pointer"]["shifting"] = int(action_data["accel"]) / 10
                x, y, duration = self.inputter.stick2mouse_movement(stick_data)
                self.is_using_stick_pointer = True
                self.inputter.mouse_move(x, y, absolute=False, duration=duration, steps_per_second=120)
                self.is_using_stick_pointer = False
            elif action_type == "wheel":
                if self.is_using_stick_wheel:
                    return None
                self.inputter.convert_config["scroll"]["duration"] = int(action_data["speed"]) / 1000
                self.inputter.convert_config["scroll"]["shifting"] = int(action_data["accel"]) / 10
                x, y, duration = self.inputter.stick2scroll(stick_data)
                if action_data["direction"] == "wheelVertical":
                    x = 0
                elif action_data["direction"] == "wheelHorizontal":
                    y = 0
                self.is_using_stick_wheel = True
                self.inputter.mouse_scroll(-x, y, duration)
                self.is_using_stick_wheel = False
        elif joycon_event == "button":
            deleted_pressing_key_and_value: list | None = None
            if joycon_status["status"] == 0:
                if joycon_status["button"] in self.pressed_keys:
                    deleted_pressing_key_and_value = [joycon_status["button"], self.pressed_keys[joycon_status["button"]]]
                    del self.pressed_keys[joycon_status["button"]]
                pressing_another_profiles_key = [another["key"] for another in self.pressing_another_profiles]
                if joycon_status["button"] in pressing_another_profiles_key:
                    index = pressing_another_profiles_key.index(joycon_status["button"])
                    self.pressing_another_profiles = self.pressing_another_profiles[:index]
                    # del self.switched_profile[self.current_app]
                    self.set_current_app(self.current_app)
                    self.update_led()
                    self.logger.debug(f"Brought back to original profile: {self.current_app}")
                    return
            actions = [convert for convert in convert_data if convert["input"]["value"] == joycon_status["button"]]
            if len(actions) == 0:
                return None
            action = actions[0]
            action_type = action["value"]["actionType"]
            action_data = action["value"]["data"]

            if action_type == "basic":
                if joycon_status["status"] == 1:
                    self.pressed_keys[joycon_status["button"]] = self._get_current_time()
                    for press in action_data["press"]:
                        self._basically_functions(press["type"], press["args"], serial)
                    if action_data["keep"]["type"] == "rapid":
                        if action_data["keep"]["value"]["delay"]:
                            time.sleep(int(action_data["keep"]["value"]["delayTime"]) / 1000)
                        interval = int(action_data["keep"]["value"]["interval"]) / 1000
                        while joycon_status["button"] in self.pressed_keys:
                            flag = False
                            for key in action_data["keep"]["value"]["key"]:
                                result = self._basically_functions(key["type"], key["args"], serial, interval)
                                if result == 0:
                                    flag = True
                            if not flag:
                                time.sleep(interval)
                    elif action_data["keep"]["type"] == "another-profile":
                        if action_data["keep"]["value"]["delay"]:
                            time.sleep(int(action_data["keep"]["value"]["delayTime"]) / 1000)
                        if joycon_status["button"] in self.pressed_keys:
                            profile = action_data["keep"]["value"]["profile"]
                            if len(profile) <= 0:
                                return
                            self.pressing_another_profiles.append({"key": joycon_status["button"], "profile": action_data["keep"]["value"]["profile"]})
                            self.set_current_app(self.current_app)
                            self.update_led()
                            self.logger.debug(f"Switched profile to {self.current_switched_profile[self.current_app]["value"]}: {self.current_app} (temporary)")
                else:
                    for release in action_data["release"]:
                        self._basically_functions(release["type"], release["args"], serial)
            elif action_type == "switch":
                if joycon_status["status"] == 1:
                    if profile_id not in self.switch_count:
                        is_reset = action_data["reset"]
                        index = 0
                        self.switch_count[profile_id] = (is_reset, self._get_current_time(), index)
                    else:
                        is_reset, start, index = self.switch_count[profile_id]
                        if action_data["delay"] and self._get_current_time() - start > int(action_data["delayTime"]) / 1000:
                            index = 0
                            self.logger.debug(f"Switch action: reset")
                        else:
                            index += 1
                            if index >= len(action_data["functions"]):
                                index = 0
                                self.logger.debug(f"Switch action: loop")
                        self.switch_count[profile_id] = (is_reset, self._get_current_time(), index)
                    self.pressed_keys[joycon_status["button"]] = self._get_current_time()
                    self._basically_functions(action_data["functions"][index]["type"], action_data["functions"][index]["args"], serial)
                    self.logger.debug(f"Switch action: {index}")
            elif action_type == "count":
                if joycon_status["status"] == 1:
                    if joycon_status["button"] not in self.continuous_keys:
                        data = (0, self._get_current_time())
                        self.continuous_keys[joycon_status["button"]] = data
                    else:
                        count, start = self.continuous_keys[joycon_status["button"]]
                        data = (count + 1, self._get_current_time())
                        self.continuous_keys[joycon_status["button"]] = data
                    time.sleep(int(action_data["interval"]) / 1000)
                    if joycon_status["button"] in self.continuous_keys and self.continuous_keys[joycon_status["button"]] == data:
                        del self.continuous_keys[joycon_status["button"]]
                        functions = action_data["functions"]
                        index = data[0] - (data[0] // len(functions)) * len(functions)
                        self._basically_functions(functions[index]["type"], functions[index]["args"], serial)
                        self.logger.debug(f"Count action (count: {data[0]}): {index}")
            elif action_type == "length":
                line_msec = int(action_data["time"]) / 1000
                if joycon_status["status"] == 1:
                    now = self._get_current_time()
                    self.pressed_keys[joycon_status["button"]] = now
                    time.sleep(line_msec)
                    if joycon_status["button"] in self.pressed_keys and self.pressed_keys[joycon_status["button"]] == now:
                        for over in action_data["over"]:
                            self._basically_functions(over["type"], over["args"], serial)
                        self.logger.debug(f"Length {len(action_data['over'])} action ({line_msec}ms): over")
                else:
                    if deleted_pressing_key_and_value is not None and deleted_pressing_key_and_value[0] == joycon_status["button"]:
                        if deleted_pressing_key_and_value[1] + line_msec > self._get_current_time():
                            for under in action_data["under"]:
                                self._basically_functions(under["type"], under["args"], serial)
                            self.logger.debug(f"Length {len(action_data['under'])} action ({line_msec}ms): under")
                    for release in action_data["release"]:
                        self._basically_functions(release["type"], release["args"], serial)
                    self.logger.debug(f"Length {len(action_data['release'])} action ({line_msec}ms): released")

    def _get_current_time(self) -> float:
        return time.time()

    def _basically_functions(self, action_type: dict, args: str, serial: str, interval: int=0) -> int | None:
        if action_type == "keyboard":
            event = json.loads(args)
            if event["action"] == "touch":
                key_codes = [key["id"] for key in event["value"]]
                self.inputter.press_keys(key_codes)
                self.logger.debug(f"Touch keys: {key_codes}")
            elif event["action"] == "press":
                for key in event["value"]:
                    self.inputter.keyboard_controller.press(str(key["id"]))
                self.logger.debug(f"Press key: {len(event['value'])} keys")
            elif event["action"] == "release":
                for key in event["value"]:
                    self.inputter.keyboard_controller.release(str(key["id"]))
                self.logger.debug(f"Release key: {len(event['value'])} keys")
        elif action_type == "mouse":
            event = json.loads(args)
            if event["action"] == "leftClick":
                if event["value"] == "click":
                    self.inputter.mouse_controller.click(mouse.Button.left)
                    self.logger.debug("Left click")
                elif event["value"] == "press":
                    self.inputter.mouse_controller.press(mouse.Button.left)
                    self.logger.debug("Left click pressed")
                elif event["value"] == "release":
                    self.inputter.mouse_controller.release(mouse.Button.left)
                    self.logger.debug("Left click released")
            elif event["action"] == "rightClick":
                if event["value"] == "click":
                    self.inputter.mouse_controller.click(mouse.Button.right)
                    self.logger.debug("Right click")
                elif event["value"] == "press":
                    self.inputter.mouse_controller.press(mouse.Button.right)
                    self.logger.debug("Right click pressed")
                elif event["value"] == "release":
                    self.inputter.mouse_controller.release(mouse.Button.right)
                    self.logger.debug("Right click released")
            elif event["action"] == "middleClick":
                if event["value"] == "click":
                    self.inputter.mouse_controller.click(mouse.Button.middle)
                    self.logger.debug("Middle click")
                elif event["value"] == "press":
                    self.inputter.mouse_controller.press(mouse.Button.middle)
                    self.logger.debug("Middle click pressed")
                elif event["value"] == "release":
                    self.inputter.mouse_controller.release(mouse.Button.middle)
                    self.logger.debug("Middle click released")
            elif event["action"] == "scroll":
                scroll_values = event["value"]
                dx = int(scroll_values["right"]) - int(scroll_values["left"])
                dy = int(scroll_values["up"]) - int(scroll_values["down"])
                self.inputter.mouse_scroll(dx, dy, duration=interval)
                self.logger.debug(f"Scroll: ({dx}, {dy})")
                if interval != 0:
                    return 0
            elif event["action"] == "moveAbsolute":
                position = event["value"]
                self.inputter.mouse_move(position["x"], position["y"], absolute=True, duration=interval)
                self.logger.debug(f"Move mouse to ({event['value']['x']}, {event['value']['y']})")
                if interval != 0:
                    return 0
            elif event["action"] == "moveRelative":
                position = event["value"]
                self.inputter.mouse_move(position["x"], position["y"], absolute=False, duration=interval)
                self.logger.debug(f"Move mouse by ({event['value']['x']}, {event['value']['y']})")
                if interval != 0:
                    return 0
        elif action_type == "other":
            event = json.loads(args)
            if event["action"] == "sleep":
                time.sleep(int(event["value"]) / 1000)
                self.logger.debug(f"Sleep: {event['value']}ms")
            elif event["action"] == "changeProfile":
                profile_id = event["value"]
                print("これ！", profile_id)
                if profile_id == "":
                    return
                self.switched_profile[self.current_app] = profile_id
                self.set_current_app(self.current_app)
                self.update_led()
                self.logger.debug(f"Switched profile to {self.current_switched_profile[self.current_app]['value']}: {self.current_app}")
            elif event["action"] == "resetGyro":
                self.controller.get_joycon_from_serial(serial).reset_orientation()
                self.logger.debug(f"Reset gyro ({serial})")
            elif event["action"] == "rumble":
                msec = int(event["value"])
                Thread(target=lambda: self.controller.get_joycon_from_serial(serial).rumble(msec), daemon=True).start()
                self.logger.debug(f"Rumble: {msec}ms (async)")
