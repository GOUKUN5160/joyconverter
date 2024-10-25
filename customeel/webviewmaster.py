import multiprocessing
import sys
import webview

if sys.platform == "darwin":
    ctx = multiprocessing.get_context("spawn")
    Process = ctx.Process
    Queue = ctx.Queue
else:
    Process = multiprocessing.Process
    Queue = multiprocessing.Queue

class GUI:
    def __init__(self, title: str, url: str, app_name: str, width: int=800, height: int=600, x: int=0, y: int=0, update_interval: int=5):
        self.webview_process: Process | None = None
        self.title = title
        self.url = url
        self.app_name = app_name
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.update_interval = update_interval
        self.size_que = Queue()
        self.position_que = Queue()
        self._geometry = {"width": width, "height": height, "x": x, "y": y}

    @property
    def geometry(self):
        size = None
        position = None
        while not self.size_que.empty():
            size = self.size_que.get()
        while not self.position_que.empty():
            position = self.position_que.get()
        if size is not None:
            self._geometry["width"] = size["width"]
            self._geometry["height"] = size["height"]
        if position is not None:
            self._geometry["x"] = position["x"]
            self._geometry["y"] = position["y"]
        return self._geometry

    def _run_webview(self):
        window = webview.create_window(self.title, url=self.url)
        window.events.resized += self.on_resized
        window.events.moved += self.on_moved
        webview.settings["ALLOW_DOWNLOADS"] = True
        #"""
        webview.start(self.initialize, window, user_agent=self.app_name)
        """
        webview.start(self.initialize, window, user_agent=self.app_name, debug=True)
        #"""

    def on_resized(self, width: int, height: int):
        self.size_que.put({"width": width, "height": height})
    def on_moved(self, x: int, y: int):
        self.position_que.put({"x": x, "y": y})

    def initialize(self, window: webview.Window):
        window.resize(self.width, self.height)
        window.move(self.x, self.y)

    def _start_webview_process(self, block: bool=False, callback: callable=None):
        self.webview_process = Process(target=self._run_webview)
        self.webview_process.start()
        # print("webview_process started")
        if block:
            self.webview_process.join()
            # print("webview_process finished")
            if callback is not None:
                callback()


    def start(self, block: bool=False):
        if self.webview_process is None or not self.webview_process.is_alive():
            self._start_webview_process(block)

    def stop(self):
        if self.webview_process is not None:
            self.webview_process.terminate()

