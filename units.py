import threading
import ctypes
from os import path
import subprocess
import sys
import logger as lg
import random
import string


logger = lg.get_logger("units")

if sys.platform == "win32":
    from psutil import Process
    import win32process
    import win32gui
    import ctypes
    from ctypes.wintypes import *
    from enum import Enum
    from PIL import Image
    import numpy as np
    import win32con
    from win32com.client import GetObject
    import pythoncom

    UNIQUE_STRING = "JoyConverter-mutex"

    def singleton():
        Kernel32 = ctypes.windll.Kernel32
        mutex = Kernel32.CreateMutexA(0, 1, UNIQUE_STRING)
        result = Kernel32.WaitForSingleObject(mutex, 0)
        if result == 0x00000102:
            logger.error("Check singleton: NG")
            sys.exit(-1)
        logger.debug("Check singleton: OK")

    # ----- get_active_app ----- #
    def get_active_app_path() -> str:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        path = Process(pid).exe()
        logger.debug(f"Active app path: {path}")
        return path

    # ----- get_open_apps ----- #
    class Win32Window:
        def __init__(self, hWnd: int):
            self._hWnd = hWnd
        @property
        def title(self) -> str:
            name = win32gui.GetWindowText(self._hWnd)
            if isinstance(name, bytes):
                name = name.decode()
            return name or ""
        @property
        def path(self) -> str:
            _, pid = win32process.GetWindowThreadProcessId(self._hWnd)
            return Process(pid).exe()
        def getHandle(self) -> int:
            return self._hWnd
    def _find_window_handles(parent: int | None = None, window_class: str | None = None, title: str | None = None, onlyVisible: bool = True) -> list[int]:
        handle_list: list[int] = []
        def findit(hwnd: int, _) -> bool:
            if window_class and window_class != win32gui.GetClassName(hwnd):
                return True
            if title and title != win32gui.GetWindowText(hwnd):
                return True
            if not onlyVisible or (onlyVisible and win32gui.IsWindowVisible(hwnd)):
                handle_list.append(hwnd)
            return True
        if not parent:
            parent = win32gui.GetDesktopWindow()
        win32gui.EnumChildWindows(parent, findit, None)
        return handle_list
    def _findMainWindowHandles() -> list[tuple[int, int]]:
        class TITLEBARINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", DWORD),
                ("rcTitleBar", RECT),
                ("rgstate", DWORD * 6)
            ]
        def win_enum_handler(hwnd: int, ctx: any):
            if not win32gui.IsWindowVisible(hwnd):
                return
            title_info = TITLEBARINFO()
            title_info.cbSize = ctypes.sizeof(title_info)
            ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(title_info))
            isCloaked = ctypes.c_int(0)
            DWMWA_CLOAKED = 14
            ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(isCloaked), ctypes.sizeof(isCloaked))
            title = win32gui.GetWindowText(hwnd)
            if win32gui.IsWindowVisible(hwnd) and title != "" and isCloaked.value == 0:
                if not (title_info.rgstate[0] & win32con.STATE_SYSTEM_INVISIBLE):
                    handle_list.append((hwnd, win32process.GetWindowThreadProcessId(hwnd)[1]))
        handle_list: list[tuple[int, int]] = []
        win32gui.EnumWindows(win_enum_handler, None)
        return handle_list
    def _get_all_apps():
        pythoncom.CoInitialize() # for in case of called as a thread
        WMI = GetObject("winmgmts:")
        mainWindows = [w[1] for w in _findMainWindowHandles()]
        return [(p.Properties_("ProcessID").Value, p.Properties_("Name").Value) for p in WMI.InstancesOf("Win32_Process") if p.Properties_("ProcessID").Value in mainWindows]
    def __remove_bad_windows(windows: list[int] | None) -> list[Win32Window]:

        outList = []
        if windows is not None:
            for window in windows:
                try:
                    outList.append(Win32Window(window))
                except:
                    pass
        return outList
    def get_open_apps() -> dict[str, str]:
        process_list = _get_all_apps()
        result: dict[str, str] = {}
        for win in __remove_bad_windows(_find_window_handles()):
            pID = win32process.GetWindowThreadProcessId(win.getHandle())
            for item in process_list:
                appPID = item[0]
                appName = str(item[1])
                if appPID == pID[1]:
                    if not appName in result:
                        result[appName] = win.path
                    break
        logger.debug(f"Open apps: {result}")
        return result

    # ----- get_app_icon ----- #
    BI_RGB = 0
    DIB_RGB_COLORS = 0

    class ICONINFO(ctypes.Structure):
        _fields_ = [
            ("fIcon", BOOL),
            ("xHotspot", DWORD),
            ("yHotspot", DWORD),
            ("hbmMask", HBITMAP),
            ("hbmColor", HBITMAP)
        ]

    class RGBQUAD(ctypes.Structure):
        _fields_ = [
            ("rgbBlue", BYTE),
            ("rgbGreen", BYTE),
            ("rgbRed", BYTE),
            ("rgbReserved", BYTE),
        ]

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", DWORD),
            ("biWidth", LONG),
            ("biHeight", LONG),
            ("biPlanes", WORD),
            ("biBitCount", WORD),
            ("biCompression", DWORD),
            ("biSizeImage", DWORD),
            ("biXPelsPerMeter", LONG),
            ("biYPelsPerMeter", LONG),
            ("biClrUsed", DWORD),
            ("biClrImportant", DWORD)
        ]

    class BITMAPINFO(ctypes.Structure):
        _fields_ = [
            ("bmiHeader", BITMAPINFOHEADER),
            ("bmiColors", RGBQUAD * 1),
        ]


    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

    gdi32.CreateCompatibleDC.argtypes = [HDC]
    gdi32.CreateCompatibleDC.restype = HDC
    gdi32.GetDIBits.argtypes = [
        HDC, HBITMAP, UINT, UINT, LPVOID, ctypes.c_void_p, UINT
    ]
    gdi32.GetDIBits.restype = ctypes.c_int
    gdi32.DeleteObject.argtypes = [HGDIOBJ]
    gdi32.DeleteObject.restype = BOOL
    shell32.ExtractIconExW.argtypes = [
        LPCWSTR, ctypes.c_int, ctypes.POINTER(HICON), ctypes.POINTER(HICON), UINT
    ]
    shell32.ExtractIconExW.restype = UINT
    user32.GetIconInfo.argtypes = [HICON, ctypes.POINTER(ICONINFO)]
    user32.GetIconInfo.restype = BOOL
    user32.DestroyIcon.argtypes = [HICON]
    user32.DestroyIcon.restype = BOOL


    class IconSize(Enum):
        SMALL = 1
        LARGE = 2

        @staticmethod
        def to_wh(size: "IconSize") -> tuple[int, int]:
            size_table = {
                IconSize.SMALL: (16, 16),
                IconSize.LARGE: (32, 32)
            }
            return size_table[size]


    def extract_icon(filename: str, size: IconSize=IconSize.LARGE) -> ctypes.Array[ctypes.c_char]:
        dc: HDC = gdi32.CreateCompatibleDC(0)
        if dc == 0:
            raise ctypes.WinError()

        hicon: HICON = HICON()
        extracted_icons: UINT = shell32.ExtractIconExW(
            filename,
            0,
            ctypes.byref(hicon) if size == IconSize.LARGE else None,
            ctypes.byref(hicon) if size == IconSize.SMALL else None,
            1
        )
        if extracted_icons != 1:
            raise ctypes.WinError()

        def cleanup() -> None:
            if icon_info.hbmColor != 0:
                gdi32.DeleteObject(icon_info.hbmColor)
            if icon_info.hbmMask != 0:
                gdi32.DeleteObject(icon_info.hbmMask)
            user32.DestroyIcon(hicon)

        icon_info: ICONINFO = ICONINFO(0, 0, 0, 0, 0)
        if not user32.GetIconInfo(hicon, ctypes.byref(icon_info)):
            cleanup()
            raise ctypes.WinError()

        w, h = IconSize.to_wh(size)
        bmi: BITMAPINFO = BITMAPINFO()
        ctypes.memset(ctypes.byref(bmi), 0, ctypes.sizeof(bmi))
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = w
        bmi.bmiHeader.biHeight = -h
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = BI_RGB
        bmi.bmiHeader.biSizeImage = w * h * 4
        bits = ctypes.create_string_buffer(bmi.bmiHeader.biSizeImage)
        copied_lines = gdi32.GetDIBits(
            dc, icon_info.hbmColor, 0, h, bits, ctypes.byref(bmi), DIB_RGB_COLORS
        )
        if copied_lines == 0:
            cleanup()
            raise ctypes.WinError()

        cleanup()
        return bits
    def win32_icon_to_image(icon_bits: ctypes.Array[ctypes.c_char], size: IconSize=IconSize.LARGE) -> Image:
        w, h = IconSize.to_wh(size)
        img = Image.frombytes("RGBA", (w, h), icon_bits, "raw", "BGRA")
        return img
    def save_app_icon(app_path: str, file_path: str) -> None:
        icon_bits = extract_icon(app_path)
        img = win32_icon_to_image(icon_bits)
        img.save(file_path)
        logger.debug(f"Saved icon: {file_path}")

    def open_folder_app(path: str) -> None:
        subprocess.Popen(["explorer.exe", f"/select,{path}"])
elif sys.platform == "darwin":
    from AppKit import NSWorkspace, NSBitmapImageRep, NSBitmapImageFileTypePNG
    def singleton():
        pass
    def get_open_apps():
        apps = NSWorkspace.sharedWorkspace().launchedApplications()
        data = {app["NSApplicationName"]: app["NSApplicationPath"] for app in apps}
        logger.debug(f"Open apps: {data}")
        return data
    def get_active_app_path() -> str:
        apps = NSWorkspace.sharedWorkspace().activeApplication()
        path = apps["NSApplicationPath"]
        logger.debug(f"Active app path: {path}")
        return path
    def save_app_icon(app_path: str, file_path: str) -> None:
        icon = NSWorkspace.sharedWorkspace().iconForFile_(app_path)
        bitmap = NSBitmapImageRep(data=icon.TIFFRepresentation())
        bitmap.representationUsingType_properties_(NSBitmapImageFileTypePNG, None).writeToFile_atomically_(file_path, False)
        logger.debug(f"Saved icon: {file_path}")
    def open_folder_app(path: str) -> None:
        subprocess.Popen(["open", "-R", path])

# TODO: 多分使わない
class CancelableThread(threading.Thread):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._run = self.run
        self.run = self.set_id_and_run
        self.daemon = True

    def set_id_and_run(self) -> None:
        self.id = threading.get_native_id()
        self._run()

    def get_id(self) -> int:
        return self.id

    def raise_exception(self) -> bool:
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.get_id()),
            ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.get_id()),
                0
            )
            return False
        return True

# TODO: 未完成
def is_working() -> bool:
    file_name = path.basename(__file__)
    p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", file_name], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["grep", "python"], stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen(["wc", "-l"], stdin=p3.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()
    p3.stdout.close()
    output = p4.communicate()[0].decode("utf8").replace('\n','')

    if int(output) != 1:
        return True
    return False

def randstr(n: int) -> str:
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return "".join(randlst)
