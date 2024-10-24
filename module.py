from customjoycon import get_device_ids, is_id_L, ButtonEventJoyCon, GyroTrackingJoyCon
from threading import Thread
from time import sleep
import logger
import memory
import units

class AdvancedJoyCon(ButtonEventJoyCon, GyroTrackingJoyCon):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, track_sticks=True)
        self.joycon_id = (self.vendor_id, self.product_id, self.serial)
        self.device_type = "L" if is_id_L(self.joycon_id) else "R" if not is_id_L(self.joycon_id) else "Unknown"
        self.product_string = self._joycon_device.get_product_string()
        self.is_pause = False
        self.pause_checked_flag = False
        self.logger = logger.get_logger("AdvancedJoyCon")
        self.is_disconnected = False
    def events(self):
        for event_type, status in super().events():
            yield "button", {"button": event_type, "status": status}
        yield "stick", {"horizontal": super().get_stick_right_horizontal() if self.device_type == "R" else super().get_stick_left_horizontal(), "vertical": super().get_stick_right_vertical() if self.device_type == "R" else super().get_stick_left_vertical()}
        yield "gyro", [super().pointer, super().rotation, super().direction]
        # yield "accel", [super().get_accel_x(), super().get_accel_y(), super().get_accel_z()]
    def _update_input_report(self) -> None:
        while True:
            if hasattr(self, "is_pause"):
                if self.is_pause:
                    self.pause_checked_flag = False
                    self.logger.debug("Pausing...")
                    sleep(0.2)
                    continue
                if self.pause_checked_flag:
                    self.logger.debug("Disconnected.")
                    break
            try:
                report = self._read_input_report()
                # TODO, handle input reports of type 0x21 and 0x3f
                while report[0] != 0x30:
                    report = self._read_input_report()

            except OSError:
                self.logger.debug("Catch 'OSError: read error' because of pause. Ignored.")
                self.pause_checked_flag = True
                continue
            self._input_report = report

            for callback in self._input_hooks:
                callback(self)
        self.is_disconnected = True
    def disconnect(self) -> None:
        self.is_pause = True
        self._joycon_device.close()
        self.logger.debug(f"Disconnected, is_pause: {self.is_pause}.")
    def reconnect(self) -> None:
        self.is_pause = False
        self._joycon_device.open(*self.joycon_id)
        self.logger.debug(f"Reconnected, is_pause: {self.is_pause}.")
    def rumble(self, msec: int, _recursion: bool=False) -> None:
        base = 1000
        if msec > base:
            for _ in range(msec // base):
                self.rumble(base, True)
            self.rumble(msec % base, True)
            self._enable_vibration(False)
        else:
            self._enable_vibration()
            self._send_rumble(b"\x98\x1e\xc6\x47\x98\x1e\xc6\x47")
            sleep(msec / 1000)
            self._send_rumble()
            if not _recursion:
                self._enable_vibration(False)
    def _send_rumble(self, data=b"\x00\x00\x00\x00\x00\x00\x00\x00") -> None:
        self._RUMBLE_DATA = data
        self._write_output_report(b"\x10", b"", b"")
    def _enable_vibration(self, enable=True) -> None:
        self._write_output_report(b"\x01", b"\x48", b"\x01" if enable else b"\x00")

class Controller:
    def __init__(self) -> None:
        self.disconnected_handler = None
        self.listeners: list[str] = []
        self._joycons: list[AdvancedJoyCon] = []
        self.stick_calibration_data: dict[str, dict[str, str | dict[str, int | None]]] = {}
        self.stick_calibrater: dict[str, str | dict | None] | None = None
        self.stick_split_num = 40
        self.logger = logger.get_logger("Controller")
    def __del__(self) -> None:
        self.clear_listeners()
    @property
    def joycons(self) -> list[AdvancedJoyCon]:
        previouse_joycons = [joycon.serial for joycon in self._joycons]
        [self._joycons.remove(disconnected_controller) for disconnected_controller in [joycon for joycon in self._joycons if joycon.is_disconnected]]
        if not previouse_joycons == [joycon.serial for joycon in self._joycons]:
            self.logger.debug(f"Disconnected joycons removed: {len(previouse_joycons) - len(self._joycons)}")
            if self.disconnected_handler is not None:
                self.disconnected_handler(len(previouse_joycons) - len(self._joycons))
        return self._joycons
    @joycons.setter
    def joycons(self, value: list[AdvancedJoyCon]) -> None:
        self._joycons = value
    @property
    def current_stick_position(self) -> dict[str, dict[str, int | None]]:
        result = {}
        for joycon in self.joycons:
            if not joycon.serial in self.stick_calibration_data:
                # self.logger.error(f"Calibration data not found for {joycon.serial}.")
                continue
            if joycon.device_type == "L":
                data = {"horizontal": joycon.get_stick_left_horizontal(), "vertical": joycon.get_stick_left_vertical()}
            elif joycon.device_type == "R":
                data = {"horizontal": joycon.get_stick_right_horizontal(), "vertical": joycon.get_stick_right_vertical()}
            else:
                self.logger.error(f"Unknown device type: {joycon.device_type}")
                continue
            result[joycon.serial] = self._calc_stick_position(data, self.stick_calibration_data[joycon.serial], split_num=self.stick_split_num)
        return result
    def calc_stick_position(self, serial: str, data: dict[str, int | None]) -> dict[str, int | None]:
        if not serial in self.stick_calibration_data:
            # self.logger.error(f"Calibration data not found for {serial}.")
            return {}
        return self._calc_stick_position(data, self.stick_calibration_data[serial], split_num=self.stick_split_num)
    def get_joycon_ids(self) -> list[tuple]:
        joycon_ids = get_device_ids()
        self.logger.debug(f"JoyCon IDs: {joycon_ids}")
        return joycon_ids
    def get_joycon_from_serial(self, serial: str) -> AdvancedJoyCon | None:
        for joycon in self.joycons:
            if joycon.serial == serial:
                return joycon
        return None
    def update_joycon_list(self, retry_count: int=5) -> None:
        for i in range(retry_count):
            break_flag = True
            joycon_ids = self.get_joycon_ids()
            for joycon_id in joycon_ids:
                if joycon_id[2] in [joycon.serial for joycon in self.joycons]:
                    continue
                try:
                    self.logger.debug(f"Connecting: {joycon_id[2]}")
                    new_joycon = AdvancedJoyCon(*joycon_id)
                    self.logger.debug(f"Connected: {joycon_id[2]}")
                    new_controllers = self.joycons
                    new_controllers.append(new_joycon)
                    self.set_joycons(instance=new_controllers)
                    new_joycon.set_led_flashing(15)
                except Exception as e:
                    self.logger.debug(f"Connecting failed: {e}")
                    break_flag = False
                    continue
            if break_flag:
                break
            if i + 1 < retry_count:
                self.logger.debug(f"Retrying({i + 1}/{retry_count - 1})...")
            sleep(0.1)
    def set_joycons(self, joycon_ids: tuple[int, int, str] | list[tuple[int, int, str]] | None=None, instance: AdvancedJoyCon | list[AdvancedJoyCon] | None=None) -> None:
        if joycon_ids is None:
            if instance is None:
                raise ValueError("Either joycon_ids or instance must be provided.")
            self.joycons = [instance] if isinstance(instance, AdvancedJoyCon) else instance
        else:
            joycon_ids = [joycon_ids] if isinstance(joycon_ids, tuple) else joycon_ids
            self.joycons = [AdvancedJoyCon(*joycon_id) for joycon_id in joycon_ids]
    def get_current_joycon_serials(self) -> list[str]:
        return [joycon.serial for joycon in self.joycons]
    def set_disconnected_handler(self, callback: callable) -> None:
        self.disconnected_handler = callback
    def add_listener(self, callback: callable) -> str:
        listener_id = units.randstr(10)
        self.listeners.append({"id": listener_id, "callback": callback})
        if len(self.listeners) == 1:
            self._run_listeners()
        self.logger.debug(f"Add listener: {listener_id}")
        return listener_id
    def _run_listeners(self, interval=0.015) -> None:
        def joycon_listeners():
            while True:
                if len(self.listeners) == 0:
                    self.logger.debug("No listeners.")
                    break
                for joycon in self.joycons:
                    for event_type, status in joycon.events():
                        for listener in self.listeners:
                            result = listener["callback"](joycon.serial, event_type, status)
                            if result == False:
                                self.remove_listener(listener["id"])
                sleep(interval)
        Thread(target=joycon_listeners, daemon=True).start()
    def remove_listener(self, listener_id: str) -> None:
        for listener in self.listeners:
            if listener["id"] == listener_id:
                self.listeners.remove(listener)
                self.logger.debug(f"Remove listener: {listener_id}")
                return
    def clear_listeners(self) -> None:
        for listener_id in [listener["id"] for listener in self.listeners]:
            self.remove_listener(listener_id)
        if not self.stick_calibrater is None:
            self.cancel_stick_calibration()
    def _calc_stick_position(self, current_data: dict[str, int], stick_calibration_data: dict[str, dict[str, int | None]], split_num: int) -> dict[str, int | None]:
        positions = {"horizontal": None, "vertical": None}
        for key, d in stick_calibration_data.items():
            if current_data[key] == None:
                self.logger.debug(f"Stick {key} is None.")
                continue
            splitted_num = (d["max"] - d["min"]) / split_num + 1
            splitted_list = [d["min"] + splitted_num * i for i in range(split_num + 1)]
            splitted_list.append(current_data[key])
            splitted_list.sort()
            result = splitted_list.index(current_data[key]) - 1
            if result < 0:
                self.logger.warning(f"Stick {key}({current_data[key]}) less than min({d['min']}). This indicates a possible calibration failure.")
                result = 0
            elif result > split_num - 1:
                self.logger.warning(f"Stick {key}({current_data[key]}) more than min({d['max']}). This indicates a possible calibration failure.")
                result = split_num - 1
            positions[key] = result
        return positions
    def _listener_calibrate_stick(self, serial, event_type: str, status: dict):
        if event_type == "stick" and serial == self.stick_calibrater["serial"]:
            if not serial in self.stick_calibration_data:
                self.stick_calibration_data[serial] = {"horizontal": {"min": None, "max": None}, "vertical": {"min": None, "max": None}}
            for axis in ["horizontal", "vertical"]:
                for minmax in ["min", "max"]:
                    if self.stick_calibration_data[serial][axis][minmax] == None:
                        self.stick_calibration_data[serial][axis][minmax] = status[axis]
                    elif (self.stick_calibration_data[serial][axis][minmax] < status[axis]) and minmax == "max":
                        self.stick_calibration_data[serial][axis][minmax] = status[axis]
                    elif (self.stick_calibration_data[serial][axis][minmax] > status[axis]) and minmax == "min":
                        self.stick_calibration_data[serial][axis][minmax] = status[axis]
    def start_stick_calibration(self, target_serial: str) -> None:
        if self.stick_calibrater is not None:
            raise RuntimeError("Already calibrating.")
        previous_data = self.stick_calibration_data[target_serial] if target_serial in self.stick_calibration_data else None
        self.delete_calibration_data(target_serial)
        self.stick_calibrater = {"serial": target_serial, "previouse_data": previous_data}
        listener_id = self.add_listener(self._listener_calibrate_stick)
        self.stick_calibrater["id"] = listener_id
    def cancel_stick_calibration(self) -> None:
        if self.stick_calibrater is None:
            raise RuntimeError("Not calibrating.")
        if self.stick_calibrater["previouse_data"] is not None:
            self.stick_calibration_data[self.stick_calibrater["serial"]] = self.stick_calibrater["previouse_data"]
        else:
            self.delete_calibration_data(self.stick_calibrater["serial"])
        self.stop_stick_calibration()
    def stop_stick_calibration(self) -> None:
        if self.stick_calibrater is None:
            raise RuntimeError("Not calibrating.")
        self.remove_listener(self.stick_calibrater["id"])
        self.stick_calibrater = None
    def save_calibration_data(self, key: str) -> None:
        memory.save(key, self.stick_calibration_data)
    def load_calibration_data(self, key: str) -> None:
        self.stick_calibration_data = memory.load(key) or {}
    def set_calibration_data(self, serial: str, data: dict[str, dict[str, int | None]]) -> None:
        self.stick_calibration_data[serial] = data
    def delete_calibration_data(self, serial: str) -> None:
        if serial in self.stick_calibration_data:
            del self.stick_calibration_data[serial]
    def get_calibration_data(self, serial: str) -> dict[str, dict[str, int | None]]:
        return self.stick_calibration_data[serial] if serial in self.stick_calibration_data else {}
