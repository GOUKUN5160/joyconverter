from pystray import Icon, MenuItem, Menu
from PIL import Image
import time
import threading
import schedule
from gui import Window
from module import Controller
from keymouse import Inputs
from action import Action
from memory import load
import units
import logger
import os
import shutil
import config as c

class JoyConverter:
    def __init__(self, controller: Controller, inputter: Inputs):
        self.logger = logger.get_logger("main")
        self.interval = 15
        self.controller = controller
        self.inputter = inputter
        self.joycon_listener_id = None
        self.status: bool = False
        image = Image.open(c.get_path("icons/active.png"))
        menu = Menu(
            MenuItem("設定", self.open_setting),
            MenuItem("JoyConをリロード", self.reload_joycon),
            Menu.SEPARATOR,
            MenuItem("終了", self.stop),
        )
        self.icon = Icon(name="joyconverter", title="JoyConverter", icon=image, menu=menu)
        self.window: Window | None = None
        self.action = Action(self.inputter, self.controller)
        self.reload_joycon()
        self.set_app_data()
        self.update_current_app()
        self.inputter.add_keyboard_listener("press", self.key_press_listener)
        self.inputter.add_mouse_listener("click", self.mouse_click_listener)
        self.controller.add_listener(self.joycon_listener)
        self.logger.debug("JoyConverter initialized.")

    def set_app_data(self, immediate: bool=False):
        config = load("app_config") or {}
        if len(config) == 0:
            self.open_setting()
            self.logger.error("No app data found.")
            return
        data = {path: config[path]["convert_data"] for path in config}
        self.action.set_app_data(data, immediate=immediate)

    def joycon_listener(self, serial: str, event: str, status: dict | list):
        if event == "button":
            if self.window:
                self.set_app_data()
            self.update_current_app()
        matched_joycon = self.controller.get_joycon_from_serial(serial)
        if matched_joycon is None:
            return
        self.action.take_action(serial, matched_joycon.device_type, event, status)

    def key_press_listener(self, key_id, key_name):
        if self.window:
            self.set_app_data()
        self.update_current_app()

    def mouse_click_listener(self, x, y, button, pressed):
        if self.window:
            self.set_app_data()
        self.update_current_app()

    def update_current_app(self):
        active = units.get_active_app_path()
        if active == "":
            return
        self.action.set_current_app(active)
        if self.window:
            self.window.current_app_hook(active)

    def on_close(self):
        self.window = None
        self.set_app_data(True)
        self.set_calibration_data()
        self.logger.debug("Setting window closed.")

    def open_setting(self):
        if self.window:
            return
        self.logger.debug("Opening setting window.")
        self.window = Window(self.controller, self.inputter)
        self.window.start(on_close=self.on_close)

    def reload_joycon(self):
        if self.window:
            self.window.reload_joycon()
        else:
            self.controller.update_joycon_list()
        self.set_calibration_data()
        self.logger.debug("JoyCon reloaded.")

    def set_calibration_data(self):
        config = load("joycon_config") or {}
        for joycon in self.controller.joycons:
            if joycon.serial in config and config[joycon.serial]["calibration"] is not None:
                self.controller.set_calibration_data(joycon.serial, config[joycon.serial]["calibration"])

    def run_schedule(self):
        schedule.every(self.interval).seconds.do(self.reload_joycon)
        while self.status:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.status = False
        if self.window:
            self.window.stop()
        self.icon.stop()
        for joycon in self.controller.joycons:
            joycon.set_led_flashing(15)
        self.controller.clear_listeners()
        self.inputter.clear_listeners()
        self.inputter.stop()
        self.logger.debug("JoyConverter stopped.")

    def run(self):
        self.status = True
        task_thread = threading.Thread(target=self.run_schedule, daemon=True)
        task_thread.start()
        self.icon.run()


def blank_callback(*args, **kwargs):
    pass

def clean_up_internal_files():
    if os.path.exists(c.get_path("web/exported_profiles")):
        shutil.rmtree(c.get_path("web/exported_profiles"))

if __name__ == "__main__":
    units.singleton()
    clean_up_internal_files()
    controller = Controller()
    inputter = Inputs()
    inputter.add_keyboard_listener("press", blank_callback)
    inputter.add_keyboard_listener("release", blank_callback)
    inputter.add_mouse_listener("click", blank_callback)
    inputter.add_mouse_listener("scroll", blank_callback)
    inputter.add_mouse_listener("move", blank_callback)
    inputter.start()
    system_tray = JoyConverter(controller, inputter)
    system_tray.run()
