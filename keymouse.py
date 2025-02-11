from pynput import mouse, keyboard
from enum import Enum
import platform
import time
import math
import logger
import units

system = platform.system()
if system == "Windows":
    from pynput.mouse._win32 import WHEEL_DELTA
    def change_scroll_speed(speed: int) -> None:
        WHEEL_DELTA = speed
    def get_scroll_speed() -> int:
        return WHEEL_DELTA
elif system == "Darwin":
    from pynput.mouse._darwin import Controller
    def change_scroll_speed(speed: int) -> None:
        Controller._SCROLL_SPEED = speed
    def get_scroll_speed() -> int:
        return Controller._SCROLL_SPEED
elif system == "Linux":
    def change_scroll_speed(speed: int) -> None:
        pass
    def get_scroll_speed() -> int:
        return 1
else:
    raise Exception("Unsupported OS")

class Buttons(Enum):
    if system == "Windows":
        left = mouse.Button.left.value
        right = mouse.Button.right.value
        middle = mouse.Button.middle.value
        x1 = mouse.Button.x1.value
        x2 = mouse.Button.x2.value
    elif system == "Darwin":
        from pynput.mouse._darwin import _button_value
        left = mouse.Button.left.value
        right = mouse.Button.right.value
        middle = mouse.Button.middle.value
        x1 = _button_value("kCGEventOther", 3)
        x2 = _button_value("kCGEventOther", 4)
    elif system == "Linux":
        pass

class Inputs:
    def __init__(self, is_mouse_listener: bool=True, is_keyboard_listener: bool=True) -> None:
        self.is_mouse_listener = is_mouse_listener
        self.is_keyboard_listener = is_keyboard_listener
        self.mouse_listener = None
        self.keyboard_listener = None
        self._listeners: dict[str, dict[str, list[callable]]] = {"mouse": {"click": [], "scroll": [], "move": []}, "keyboard": {"press": [], "release": []}}
        self._listener_ids: dict[str, tuple[str, int]] = {}
        self.convert_config: dict[str, int | dict[str, float]] = {"splitted_num": 40, "pointer": {"duration": 0.005, "shifting": 3.5}, "scroll": {"duration": 0.02, "shifting": 3}, "key": {"speed": 0.02, "is_constant": False, "threshold": 15}}
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.logger = logger.get_logger("Inputs")
    def set_keyboard_suppress(self, is_suppress: bool):
        if self.is_keyboard_listener:
            self.keyboard_listener._suppress = is_suppress
    def set_mouse_suppress(self, is_suppress: bool):
        if self.is_mouse_listener:
            self.keyboard_listener._suppress = is_suppress
    def start(self, keyboard_kwarg: dict={}, mouse_kwarg: dict={}) -> None:
        self.stop()
        if self.is_mouse_listener:
            self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click, on_scroll=self._on_mouse_scroll, on_move=self._on_mouse_move, **mouse_kwarg)
            self.mouse_listener.start()
        if self.is_keyboard_listener:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release, **keyboard_kwarg)
            self.keyboard_listener.start()
    def stop(self) -> None:
        if self.is_mouse_listener and self.mouse_listener is not None:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.is_keyboard_listener and self.keyboard_listener is not None:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
    def delete_listener(self, listener_id: str) -> bool:
        if listener_id in self._listener_ids:
            place, index = self._listener_ids[listener_id]
            tmp = place.split("-")
            self._listeners[tmp[0]][tmp[1]].pop(index)
            del self._listener_ids[listener_id]
            self.logger.debug(f"Delete listener: {listener_id} ({place})")
            return True
        else:
            return False
    def clear_listeners(self) -> None:
        self._listeners = {"mouse": {"click": [], "scroll": [], "move": []}, "keyboard": {"press": [], "release": []}}
        self._listener_ids = {}

    def mouse_click(self, button: str = "left", times: int = 1) -> None:
        if button == "left":
            self.mouse_controller.click(mouse.Button.left, times)
        elif button == "right":
            self.mouse_controller.click(mouse.Button.right, times)
        elif button == "middle":
            self.mouse_controller.click(mouse.Button.middle, times)
    def mouse_press(self, button: str = "left") -> None:
        if button == "left":
            self.mouse_controller.press(mouse.Button.left)
        elif button == "right":
            self.mouse_controller.press(mouse.Button.right)
        elif button == "middle":
            self.mouse_controller.press(mouse.Button.middle)
    def mouse_release(self, button: str = "left") -> None:
        if button == "left":
            self.mouse_controller.release(mouse.Button.left)
        elif button == "right":
            self.mouse_controller.release(mouse.Button.right)
        elif button == "middle":
            self.mouse_controller.release(mouse.Button.middle)
    def mouse_scroll(self, dx: int | float, dy: int | float, duration: float = 0, scroll_speed: int=0, scroll_lock: bool=False) -> None:
        if (not scroll_speed == 0) and (not get_scroll_speed() == scroll_speed):
            change_scroll_speed(scroll_speed)
        dx, dy = int(dx), int(dy)
        if (dx != 0 or dy != 0) or scroll_lock:
            self.mouse_controller.scroll(dx, dy)
        time.sleep(duration)
    def mouse_move(self, x: int | float, y: int | float, absolute: bool = False, duration: float = 0, steps_per_second: int = 120) -> None:
        x, y = int(x), int(y)
        position_x, position_y = self.mouse_controller.position
        if not absolute:
            x = position_x + x
            y = position_y + y
        if duration:
            start_x = position_x
            start_y = position_y
            dx = x - start_x
            dy = y - start_y
            if dx == 0 and dy == 0:
                time.sleep(duration)
            else:
                steps = max(1.0, float(int(duration * float(steps_per_second))))
                for i in range(int(steps) + 1):
                    self.mouse_controller.position = (int(start_x + dx * i / steps), int(start_y + dy * i / steps))
                    time.sleep(duration / steps)
        else:
            self.mouse_controller.position = (x, y)
        # time.sleep(duration)
    def _on_mouse_click(self, x, y, button, pressed) -> None:
        if self._listeners["mouse"]["click"] is not None:
            result = []
            for listener in self._listeners["mouse"]["click"]:
                result.append(listener(x, y, button, pressed))
            if False in result:
                return False
            else:
                return True
        else:
            self.logger.debug(f"Mouse click at ({x}, {y}) with {button} button {'pressed' if pressed else 'released'}")
    def _on_mouse_scroll(self, x, y, dx, dy) -> None:
        if self._listeners["mouse"]["scroll"] is not None:
            result = []
            for listener in self._listeners["mouse"]["scroll"]:
                result.append(listener(x, y, dx, dy))
            if False in result:
                return False
            else:
                return True
        else:
            self.logger.debug(f"Mouse scrolled at ({x}, {y}) with ({dx}, {dy})")
    def _on_mouse_move(self, x, y) -> None:
        if self._listeners["mouse"]["move"] is not None:
            result = []
            for listener in self._listeners["mouse"]["move"]:
                result.append(listener(x, y))
            if False in result:
                return False
            else:
                return True
        else:
            self.logger.debug(f"Mouse moved to ({x}, {y})")
    def add_mouse_listener(self, name: str, callback: callable, *args, **kwargs) -> str | None:
        if name not in self._listeners["mouse"]:
            return None
        self._listeners["mouse"][name].append(lambda *argments: callback(*argments, *args, **kwargs))
        listener_id = units.randstr(10)
        self._listener_ids[listener_id] = (f"mouse-{name}", len(self._listeners["mouse"][name]) - 1)
        self.logger.debug(f"Add listener: {listener_id} (mouse-{name})")
        return listener_id

    def press_key(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if isinstance(key, str):
            key = keyboard.KeyCode.from_vk(int(key))
        self.keyboard_controller.press(key)
    def release_key(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if isinstance(key, str):
            key = keyboard.KeyCode.from_vk(int(key))
        self.keyboard_controller.release(key)
    def touch_keys(self, keys: list[keyboard.Key | keyboard.KeyCode], duration: float=0) -> None:
        key_list = self._str2key(keys)
        [self.keyboard_controller.press(key) for key in key_list]
        time.sleep(duration)
        [self.keyboard_controller.release(key) for key in reversed(key_list)]
    def _on_key_press(self, key) -> None:
        key_id, key_name = self._key2str(key)
        if self._listeners["keyboard"]["press"] is not None:
            result = []
            for listener in self._listeners["keyboard"]["press"]:
                result.append(listener(key_id, key_name))
            if False in result:
                return False
            else:
                return True
        else:
            self.logger.debug(f"Key {key_name}({key_id}) pressed")
    def _on_key_release(self, key) -> None:
        key_id, key_name = self._key2str(key)
        if self._listeners["keyboard"]["release"] is not None:
            result = []
            for listener in self._listeners["keyboard"]["release"]:
                result.append(listener(key_id, key_name))
            if False in result:
                return False
            else:
                return True
        else:
            self.logger.debug(f"Key {key_name}({key_id}) released")
    def add_keyboard_listener(self, name: str, callback: callable, *args, **kwargs) -> str | None:
        if name not in self._listeners["keyboard"]:
            return None
        self._listeners["keyboard"][name].append(lambda key_id, key_name: callback(key_id, key_name, *args, **kwargs))
        listener_id = units.randstr(10)
        self._listener_ids[listener_id] = (f"keyboard-{name}", len(self._listeners["keyboard"][name]) - 1)
        self.logger.debug(f"Add listener: {listener_id} (keyboard-{name})")
        return listener_id

    def _key2str(self, key: keyboard.Key | keyboard.KeyCode) -> tuple[str, str]:
        if isinstance(key, keyboard.KeyCode):
            vk = str(key.vk)
            if key.char is not None:
                key_id, key_name = vk, key.char if key.char != " " else f"({key.vk})"
            else:
                key_id, key_name = vk, f"Key{vk}"
        elif isinstance(key, keyboard.Key):
            key_id, key_name = key.value.vk, key.name
        return key_id, key_name
    def _str2key(self, key_ids: str | list[str]) -> list[keyboard.Key | keyboard.KeyCode]:
        if isinstance(key_ids, str):
            key_ids = [key_ids]
        return [keyboard.KeyCode.from_vk(int(key_id)) for key_id in key_ids]
    def stick2mouse_movement(self, data: dict[str, int]) -> tuple[float, float, float]:
        # DURATION = 0.005 # 0.001 ~ 0.01
        # SHIFTING = 3.5 # 1 ~ 3
        data["horizontal"] -= self.convert_config["splitted_num"] / 2
        data["vertical"] -= self.convert_config["splitted_num"] / 2
        x_sign = 1 if data["horizontal"] > 0 else -1
        y_sign = -1 if data["vertical"] > 0 else 1
        x, y = abs(data["horizontal"]) * 0.2, abs(data["vertical"]) * 0.2
        x, y = math.ceil((x ** self.convert_config["pointer"]["shifting"]) * x_sign), math.ceil((y ** self.convert_config["pointer"]["shifting"]) * y_sign)
        x, y = x / 2, y / 2
        return int(x), int(y), self.convert_config["pointer"]["duration"]
    def stick2scroll(self, data: dict[str, int]) -> tuple[float, float, float]:
        # DURATION = 0.02 #
        # SHIFTING = 3 #
        data["horizontal"] -= self.convert_config["splitted_num"] / 2
        data["vertical"] -= self.convert_config["splitted_num"] / 2
        x_sign = -1 if data["horizontal"] > 0 else 1
        y_sign = 1 if data["vertical"] > 0 else -1
        x, y = abs(data["horizontal"]) * 0.2, abs(data["vertical"]) * 0.2
        x, y = math.ceil((x ** self.convert_config["scroll"]["shifting"]) * x_sign), math.ceil((y ** self.convert_config["scroll"]["shifting"]) * y_sign)
        x, y = x / 10, y / 10
        return int(x), int(y), self.convert_config["scroll"]["duration"]
    def stick2key(self, data: dict[str, int], keys: dict[str, list[int]], axis: str | list[str]=["horizontal", "vertical"]) -> tuple[list[keyboard.Key | keyboard.KeyCode], float]:
        if isinstance(axis, str):
            axis = [axis]
        if "left" not in keys:
            keys["left"] = []
        if "right" not in keys:
            keys["right"] = []
        if "up" not in keys:
            keys["up"] = []
        if "down" not in keys:
            keys["down"] = []
        if len(axis) > 1:
            result = self.stick2cardinal(data, is_convert=False)
            stick_data = result[0] - self.convert_config["splitted_num"] / 2
            keys_list = [keys["right"], keys["left"]] if result[1] == "horizontal" else [keys["up"], keys["down"]]
        else:
            stick_data = data[axis[0]] - self.convert_config["splitted_num"] / 2
            keys_list = [keys["right"], keys["left"]] if axis[0] == "horizontal" else [keys["up"], keys["down"]]
        if stick_data == 0:
            return [], 0
        elif stick_data > 0:
            press_keys = keys_list[0]
        else:
            press_keys = keys_list[1]
        if abs(stick_data) < self.convert_config["splitted_num"] / 10:
            return [], 0
        if self.convert_config["key"]["is_constant"]:
            if abs(stick_data) > self.convert_config["key"]["threshold"]:
                duration = self.convert_config["key"]["speed"]
            else:
                return [], 0
        else:
            duration = (self.convert_config["splitted_num"] / 2 - abs(stick_data)) * self.convert_config["key"]["speed"]
        return press_keys, duration
    def stick2cardinal(self, data: dict[str, int], is_convert: bool=True) -> dict[str, int] | list[int, str]:
        data["horizontal"] -= self.convert_config["splitted_num"] / 2
        data["vertical"] -= self.convert_config["splitted_num"] / 2
        if abs(data["horizontal"]) > abs(data["vertical"]):
            if not is_convert:
                return [data["horizontal"] + self.convert_config["splitted_num"] / 2, "horizontal"]
            data["vertical"] = 0
        else:
            if not is_convert:
                return [data["vertical"] + self.convert_config["splitted_num"] / 2, "vertical"]
            data["horizontal"] = 0
        data["horizontal"] += self.convert_config["splitted_num"] / 2
        data["vertical"] += self.convert_config["splitted_num"] / 2
        return data
