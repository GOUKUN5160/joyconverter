import customeel as eel
import os
from threading import Thread
from datetime import datetime
from json import dumps
from base64 import b64encode
import module
import keymouse
import logger
import memory
import units
from typing import Optional
import sys

EXPORTED_PROFILE_SAVE_DIR = os.path.join(os.path.dirname(__file__), "web/expoted_profiles")

class Window:
    def __init__(self, controller: module.Controller, inputter: keymouse.Inputs) -> None:
        self.controller = controller
        self.inputter = inputter
        self.web_dir = os.path.join(os.path.dirname(__file__), "web")
        self.is_running: bool = False
        self.is_send_key_data: bool = False
        self.is_send_mouse_data: list[str] = []
        self.is_send_joycon_data: dict[str, str | bool] = {"serial": "", "button": False, "stick": False}
        self.close_callback: Optional[callable] = None
        global_info = memory.load("global_info") or {"theme": "light", "geometry": {"size": (None, None), "position": (None, None)}}
        self.size: list[int] = global_info["geometry"]["size"]
        self.position: list[int] = global_info["geometry"]["position"]
        self.theme: str = global_info["theme"]
        self.logger = logger.get_logger("Window")
        if sys.platform == "win32":
            self.platform = "windows"
            def win32_event_filter(event_type, data):
                KEY_DOWN = 256
                KEY_UP = 257
                vk = data.vkCode
                self.logger.debug(f"suppresser(win32_event_filter): {event_type=}, {vk=}, {self.is_send_key_data=}")
                if (event_type == KEY_DOWN or event_type == KEY_UP) and self.is_send_key_data == "prevent":
                    self.inputter.set_keyboard_suppress(True)
                else:
                    self.inputter.set_keyboard_suppress(False)
                return True
            keyboard_kwarg = {"win32_event_filter": win32_event_filter}
        elif sys.platform == "darwin":
            self.platform = "mac"
            self.for_mac_previous_key = None
            def darwin_intercept(event_type, event):
                KEY_DOWN = 10
                KEY_UP = 11
                if not (event_type == KEY_DOWN or event_type == KEY_UP):
                    return event
                vk = self.for_mac_previous_key
                self.logger.debug(f"suppresser(darwin_intercept): {event_type=}, {vk=}, {self.is_send_key_data=}")
                if self.is_send_key_data == "prevent":
                    return None
                return event
            keyboard_kwarg = {"darwin_intercept": darwin_intercept}
            def on_press(key_id, key_name):
                self.for_mac_previous_key = key_id
            self.inputter.add_keyboard_listener("press", on_press)
        else:
            self.platform = "unknown"
            keyboard_kwarg = {}
        def on_release(key_id: str, key_name: str):
            if self.is_send_key_data == "keyboard" or self.is_send_key_data == "prevent":
                self.logger.debug(f"[EEL] sendKeyUp: {key_name}({key_id})")
                if hasattr(eel, "onKeyUp"):
                    eel.onKeyUp(key_name, key_id)
        def on_move(x: int, y: int):
            if "move" in self.is_send_mouse_data:
                if hasattr(eel, "onMouseMove"):
                    eel.onMouseMove(x, y)
        def on_click(x: int, y: int, button_id: keymouse.mouse.Button, pressed: bool):
            if "click" in self.is_send_mouse_data:
                b = keymouse.mouse.Button
                match button_id:
                    case b.left:
                        button = "left"
                    case b.middle:
                        button = "middle"
                    case b.right:
                        button = "right"
                    case _:
                        button = "unknown"
                if button == "unknown":
                    return
                self.logger.debug(f"[EEL] sendMouseClick: {x=}, {y=}, {button=}, {pressed=}")
                if hasattr(eel, "onMouseClick"):
                    eel.onMouseClick(x, y, button, pressed)
        def on_joycon_disconnect(number: int):
            self.logger.debug(f"[EEL] on_joycon_disconnect: {number}")
            self.on_joycon_list_change()
            self.send_message(f"JoyConが1本切断されました", "info")
        self.controller.set_disconnected_handler(on_joycon_disconnect)
        def joycon_listener(serial, event, status):
            if serial == self.is_send_joycon_data["serial"]:
                if event == "button" and self.is_send_joycon_data["button"] and hasattr(eel, "onJoyConButton"):
                    self.logger.debug(f"[EEL] sendJoyConButton: {serial=}, {status=}")
                    eel.onJoyConButton(serial, status["button"], True if status["status"] == 1 else False)
                elif event == "stick" and self.is_send_joycon_data["stick"] and hasattr(eel, "onJoyConStick"):
                    eel.onJoyConStick(serial, self.controller.calc_stick_position(serial, status))
        self.listener_id = self.controller.add_listener(joycon_listener)
        self.inputter_listener_ids = []
        self.inputter_listener_ids.append(self.inputter.add_mouse_listener("move", on_move))
        self.inputter_listener_ids.append(self.inputter.add_mouse_listener("click", on_click))
        self.inputter_listener_ids.append(self.inputter.add_keyboard_listener("release", on_release))
        self.inputter.start(keyboard_kwarg=keyboard_kwarg)
    def __del__(self):
        self.stop()

    @eel.expose
    def set_is_send_joycon_data(self, serial: str, funcs: list[str]=[]) -> None:
        self.logger.debug(f"[EEL] updated is_send_joycon_data: {serial=}, {funcs=}")
        button = True if "button" in funcs else False
        stick = True if "stick" in funcs else False
        self.is_send_joycon_data = {"serial": serial, "button": button, "stick": stick}
        if not serial == "":
            targets = [joycon for joycon in self.controller.joycons if joycon.serial == serial]
            if len(targets) <= 0:
                return
            target = targets[0]
            joycon_type = "left" if target.device_type == "L" else "right"
            buttons = target.get_status()["buttons"]
            for button, status in {**buttons[joycon_type], **buttons["shared"]}.items():
                if status == 1:
                    self.logger.debug(f"[EEL] sendJoyConButton: {serial=}, {button=}, {status=}")
                    if hasattr(eel, "onJoyConButton"):
                        eel.onJoyConButton(serial, button, True)
    @eel.expose
    def set_is_send_data(self, device: str, is_prevent: bool) -> None:
        if device == "keyboard":
            self.logger.debug(f"[EEL] updateed is_send_key_data: {is_prevent}")
            if is_prevent:
                self.is_send_key_data = "keyboard"
            else:
                self.is_send_key_data = ""
        elif device == "keyPrevent":
            self.logger.debug(f"[EEL] updateed is_prevent_key: {is_prevent}")
            if is_prevent:
                self.is_send_key_data = "prevent"
            else:
                self.is_send_key_data = ""
        elif device == "mouseMove":
            self.logger.debug(f"[EEL] updated is_send_mouse_data (move): {is_prevent}")
            if is_prevent:
                self.is_send_mouse_data.append("move")
            else:
                if "move" in self.is_send_mouse_data:
                    self.is_send_mouse_data = [data for data in self.is_send_mouse_data if data != "move"]
        elif device == "mouseClick":
            self.logger.debug(f"[EEL] updated is_send_mouse_data (click): {is_prevent}")
            if is_prevent:
                self.is_send_mouse_data.append("click")
            else:
                if "click" in self.is_send_mouse_data:
                    self.is_send_mouse_data = [data for data in self.is_send_mouse_data if data != "click"]

    @eel.expose
    def get_open_apps(self) -> dict[str, str]:
        apps = units.get_open_apps()
        self.logger.debug(f"[EEL] get_open_apps: {len(apps)} apps")
        return apps

    @eel.expose
    def regist_app(self, app_path: str, app_name: str | None=None) -> bool:
        if app_path in self.get_app_config():
            return False
        app_name = app_name or os.path.splitext(os.path.basename(app_path))[0]
        result = self.set_app_config(app_path, app_name=app_name)
        self.logger.debug(f"[EEL] regist_app: {app_path=}, {app_name=}, {result=}")
        return result
    @eel.expose
    def delete_app(self, app_path: str) -> bool:
        config = memory.load("app_config")
        if not app_path in config:
            return False
        del config[app_path]
        memory.save("app_config", config)
        return True
    @eel.expose
    def rename_app(self, app_path: str, new_name: str) -> bool:
        return self.set_app_config(app_path, app_name=new_name)
    @eel.expose
    def get_app_list(self) -> list[dict[str, str]]:
        apps = []
        app_config = self.get_app_config()
        for app_path in app_config:
            config = app_config[app_path]
            apps.append({
                "path": app_path,
                "name": config["name"],
                "default": config["default_name"],
                "icon_path": self.get_app_icon_path(app_path),
            })
        self.logger.debug(f"[EEL] get_app_list: {len(apps)} apps")
        return apps
    @eel.expose
    def get_convert_info(self, app_path: str) -> dict[str, str]:
        config = self.get_app_config(app_path)
        return config["convert_data"]["data"], config["convert_data"]["use_joycon"]
    @eel.expose
    def set_convert_info(self, app_path: str, convert_data: list, use_joycon: dict[str, dict[str, bool | list[dict[str, str]]]]) -> bool:
        return self.set_app_config(app_path, convert_data={"data": convert_data, "use_joycon": use_joycon})
    @eel.expose
    def export_profile(self, profile: dict) -> None:
        timestr = datetime.now().strftime("%Y%m%d%H%M%S")
        name = f"{timestr}{profile['name']}.jcp"
        if not os.path.exists(EXPORTED_PROFILE_SAVE_DIR):
            os.makedirs(EXPORTED_PROFILE_SAVE_DIR)
        data = b64encode(dumps(profile).encode("utf-8")).decode("utf-8")
        with open(os.path.join(EXPORTED_PROFILE_SAVE_DIR, name), "w") as f:
            f.write(data)
        self.logger.debug(f"[EEL] export_profile: {name}")
        return os.path.join("/expoted_profiles", name), name


    @eel.expose
    def reload_joycon(self) -> None:
        self.logger.debug("[EEL] reload_joycon")
        joycon_ids = self.controller.get_joycon_ids()
        try:
            self.controller.set_joycons(joycon_ids=joycon_ids)
        except (IOError, OSError, AssertionError) as e:
            self.logger.error(f"[EEL] reload_joycon error: {e}")
            return False
        self.on_joycon_list_change()
        return True
    @eel.expose
    def start_calibration(self, serial: str) -> bool:
        if not serial in self.controller.get_current_joycon_serials():
            return False
        self.logger.debug(f"[EEL] start_calibration: {serial}")
        self.controller.start_stick_calibration(serial)
        return True
    @eel.expose
    def cancel_calibration(self) -> bool:
        self.logger.debug(f"[EEL] cancel_calibration")
        self.controller.cancel_stick_calibration()
        return True
    @eel.expose
    def save_calibration(self, serial: str) -> bool:
        self.logger.debug(f"[EEL] save_calibration")
        self.controller.stop_stick_calibration()
        config = memory.load("joycon_config") or {}
        if not serial in config:
            return False
        data = self.controller.get_calibration_data(serial)
        if len(data) <= 0:
            data = None
        config[serial]["calibration"] = data
        memory.save("joycon_config", config)
        self.on_joycon_list_change()
        return True
    @eel.expose
    def delete_joycon(self, serial: str) -> bool:
        config = memory.load("joycon_config") or {}
        if not serial in config:
            return False
        del config[serial]
        memory.save("joycon_config", config)
        self.controller.delete_calibration_data(serial)
        self.on_joycon_list_change()
        return True
    @eel.expose
    def rename_joycon(self, serial: str, new_name: str) -> bool:
        config = memory.load("joycon_config") or {}
        if not serial in config:
            return False
        config[serial]["name"] = new_name
        memory.save("joycon_config", config)
        self.on_joycon_list_change()
        return True
    @eel.expose
    def get_joycons(self) -> list[dict[str, str | int | tuple[int, int] | None]]:
        data = []
        connected_joycons = []
        config = memory.load("joycon_config") or {}
        for joycon in self.controller.joycons:
            if joycon.serial not in config:
                config = self.set_joycon_config(joycon.serial, joycon=joycon, config=config)
            data.append({
                "name": config[joycon.serial]["name"],
                "serial": joycon.serial,
                "type": joycon.device_type,
                "battery_level": joycon.get_battery_level(),
                "is_battery_charging": True if joycon.get_battery_charging() == 1 else False,
                "color_body": f"rgb({', '.join(map(str, config[joycon.serial]['color_body']))})",
                "color_btn": f"rgb({', '.join(map(str, config[joycon.serial]['color_btn']))})",
                "is_calibrated": config[joycon.serial]["calibration"] is not None,
                "is_connected": True,
            })
            connected_joycons.append(joycon.serial)
            if config[joycon.serial]["calibration"] is not None:
                self.controller.set_calibration_data(joycon.serial, config[joycon.serial]["calibration"])
        memory.save("joycon_config", config)
        for serial, conf in config.items():
            if not serial in connected_joycons:
                data.append({
                    "name": conf["name"],
                    "serial": serial,
                    "type": conf["type"],
                    "battery_level": None,
                    "is_battery_charging": None,
                    "color_body": f"rgb({', '.join(map(str, conf['color_body']))})",
                    "color_btn": f"rgb({', '.join(map(str, conf['color_btn']))})",
                    "is_calibrated": conf["calibration"] is not None,
                    "is_connected": False,
                })
        self.logger.debug(f"[EEL] get_joycons: {len(data)} JoyCons")
        return data

    @eel.expose
    def set_geometry(self, geometry: dict) -> None:
        if not eel._start_args["mode"] == "webview":
            self.size = geometry.get("size", self.size)
            self.position = geometry.get("position", self.position)
            memory.save("global_info", {"theme": self.theme, "geometry": {"size": self.size, "position": self.position}})
            self.logger.debug(f"[EEL] set_geometry: {self.size=}, {self.position=}")
    @eel.expose
    def set_theme(self, theme: str) -> None:
        self.theme = theme
        memory.save("global_info", {"theme": self.theme, "geometry": {"size": self.size, "position": self.position}})
        self.logger.debug(f"[EEL] set_theme: {self.theme=}")
    @eel.expose
    def get_theme(self) -> str:
        self.logger.debug(f"[EEL] get_theme: {self.theme}")
        return self.theme

    # ------------------- Windows only ------------------- #
    @eel.expose
    def open_startup_folder(self):
        if self.platform == "windows":
            startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            os.startfile(startup_folder)
    @eel.expose
    def open_current_propgram_directory(self):
        if self.platform == "windows":
            absolute_path = os.path.abspath(__file__)
            units.open_folder_app(absolute_path)
    # ---------------------------------------------------- #

    @eel.expose
    def get_platform(self) -> str:
        return self.platform
    @eel.expose
    def open_config_folder(self):
        units.open_folder_app(memory.SAVE_DIR)
    @eel.expose
    def get_config_path(self) -> str:
        return memory.SAVE_DIR

    def on_joycon_list_change(self):
        self.logger.debug("[EEL] on_joycon_list_change")
        data = self.get_joycons()
        if hasattr(eel, "onUpdatedJoyconList"):
            eel.onUpdatedJoyconList(data)
    def send_message(self, message: str, color: str) -> None:
        if hasattr(eel, "onMessage"):
            eel.onMessage(message, color)

    def get_app_config(self, app_path: str | None=None) -> dict:
        config = memory.load("app_config")
        if config is None or len(config) == 0:
            self.set_app_config("ALL_init", app_name="全てのアプリ")
            return memory.load("app_config")
        if app_path is None:
            return config or {}
        if (config is None) or (app_path not in config):
            return {}
        return config[app_path]
    def get_app_icon_path(self, app_path: str) -> str:
        if app_path == "ALL":
            return ""
        icon_dir = os.path.join(self.web_dir, "assets", "icons")
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)
            self.logger.debug(f"Create icon directory: {icon_dir}")
        icon_path = os.path.join(icon_dir, os.path.splitext(os.path.basename(app_path))[0] + ".png")
        if not os.path.exists(icon_path):
            try:
                units.save_app_icon(app_path, icon_path)
            except Exception as e:
                self.logger.error(f"get_app_icon_path error: {e}")
                return ""
        icon_path = os.path.relpath(icon_path, self.web_dir)
        return icon_path
    def set_app_config(self, app_path: str, convert_data: dict[str, list | dict] | None=None, app_name: str | None=None) -> bool:
        if app_path == "ALL_init":
            config = {"ALL": {"convert_data": {"data": [], "use_joycon": {"l": {"isAll": True, "list": []}, "r": {"isAll": True, "list": []}}}, "name": "全てのアプリ", "default_name": "全てのアプリ"}}
            memory.save("app_config", config)
            self.logger.debug(f"Set app config: ALL")
            return True
        config = self.get_app_config()
        if convert_data is None:
            if app_path in config:
                convert_data = config[app_path]["convert_data"]
            else:
                convert_data = {"data": [], "use_joycon": {"l": {"isAll": True, "list": []}, "r": {"isAll": True, "list": []}}}
        if not app_name is None:
            if not app_path in config:
                default_name = app_name
            else:
                default_name = config[app_path]["default_name"]
        else:
            if not app_path in config:
                return False
                # raise ValueError(f"app_name is required on a new app({app_path}).")
            default_name = config[app_path]["default_name"]
        config[app_path] = {"convert_data": convert_data, "name": app_name or config[app_path]["name"], "default_name": default_name}
        memory.save("app_config", config)
        self.logger.debug(f"Set app config: {app_path=}, {convert_data=}, {app_name=}")
        return True
    def set_joycon_config(self, serial: str, data: dict | None=None, joycon: module.AdvancedJoyCon | None=None, config: dict | None=None) -> bool | dict:
        if config is None:
            config = memory.load("joycon_config") or {}
            return_config_flag = False
        else:
            return_config_flag = True
        if data is None:
            if joycon is None:
                return False
            new_name = f"JoyCon({joycon.device_type})-{joycon.serial}"
            new_data = {
                "name": new_name,
                "calibration": None,
                "type": joycon.device_type,
                "color_body": joycon.color_body,
                "color_btn": joycon.color_btn
            }
            config[joycon.serial] = new_data
            self.logger.debug(f"New JoyCon config: {new_name}")
        else:
            if not serial in config:
                self.logger.warning(f"JoyCon({serial}) is not found in config.")
            config[serial] = data
        if return_config_flag:
            return config
        memory.save("joycon_config", config)
        return True


    def _close_callback(self, page, sockets, geometry=None):
        if geometry is not None:
            self.logger.debug(f"close_callback: {page=}, {sockets=}, {geometry=}")
            self.size = [geometry["width"], geometry["height"]]
            self.position = [geometry["x"], geometry["y"]]
            memory.save("global_info", {"theme": self.theme, "geometry": {"size": self.size, "position": self.position}})
            self.logger.debug(f"Geometry saved: {self.size=}, {self.position=}")
        self.is_running = False
        self.controller.remove_listener(self.listener_id)
        for listener_id in self.inputter_listener_ids:
            self.inputter.delete_listener(listener_id)

        try:
            if self.close_callback is not None:
                self.close_callback()
        except Exception as e:
            self.logger.error(f"close_callback error: {e}")
    def _start(self):
        # CHROME_ARGS = [
        #     "--incognit",            # シークレットモード
        #     "--disable-http-cache",  # キャッシュ無効
        #     "--disable-plugins",     # プラグイン無効
        #     "--disable-extensions",  # 拡張機能無効
        #     "--disable-dev-tools",   # デベロッパーツールを無効にする
        # ]
        # CHROME_ARGS = [
        #     r"C:\Users\goukun\AppData\Local\min\min.exe",
        #     "http://localhost:8000",
        # ]
        ALLOW_EXTENSIONS = [".vue", ".html", ".css", ".js", ".ts", ".ico", ".png", ".ttf", ".woff", ".woff2", ".eot"]

        eel.init(self.web_dir, allowed_extensions=ALLOW_EXTENSIONS)
        # eel.start("index.html", port=0, cmdline_args=CHROME_ARGS, size=self.size, position=self.position, close_callback=self._close_callback, class_instance=self)
        eel.start("index.html", port=0, size=self.size, position=self.position, close_callback=self._close_callback, class_instance=self, mode="webview", app_name="JoyConverter/0.0", title="Settings - JoyConverter")
    def start(self, on_close: Optional[callable]=None, block: bool=False):
        self.logger.debug("start")
        self.close_callback = on_close
        if block:
            self.is_running = True
            self._start()
        else:
            Thread(target=self._start).start()
            self.is_running = True
    def stop(self):
        # eel.set_js_result_timeout(10)
        self.inputter.stop()
        if eel.webview is not None:
            eel.webview.stop()
        self.logger.debug("stop window")
        if self.is_running:
            if hasattr(eel, "closeWindow"):
                eel.closeWindow()
            self.is_running = False
