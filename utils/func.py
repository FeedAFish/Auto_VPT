import ctypes
from ctypes import windll
import win32gui
import win32ui
import win32con
import numpy as np
import ast
import subprocess
from PIL import Image
import threading

# Define constants for mouse events
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202

with open("note.txt", "r") as file:
    content = file.read()

DICT = ast.literal_eval(content)
AUTO_ON_1 = Image.open("img/auto_available.png")
AUTO_ON_1 = np.asarray(AUTO_ON_1)
AUTO_ON_2 = Image.open("img/auto_available_2.png")
AUTO_ON_2 = np.asarray(AUTO_ON_2)
AUTO_CB = Image.open("img/AutoCB.png")
AUTO_CB = np.asarray(AUTO_CB)
del content


def click_window(hwnd, x, y):
    # Get the handle of the window
    if hwnd:
        # Convert coordinates to LPARAM
        lparam = (y << 16) | x

        # Send the click messages
        ctypes.windll.user32.SendMessageW(hwnd, WM_LBUTTONDOWN, 0, lparam)
        ctypes.windll.user32.SendMessageW(hwnd, WM_LBUTTONUP, 0, lparam)
    else:
        raise Exception("Window not found.")


class WindowCapture:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        self.bitmap = win32ui.CreateBitmap()

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        if hasattr(self, "bitmap"):
            win32gui.DeleteObject(self.bitmap.GetHandle())
            self.saveDC.DeleteDC()
            self.mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, self.hwndDC)

    def capture_gray(self, x, y, w, h):
        if x is None or y is None or w is None or h is None:
            left, top, right, bot = win32gui.GetClientRect(self.hwnd)
            x, y, w, h = left, top, right - left, bot - top
        self.bitmap.CreateCompatibleBitmap(self.mfcDC, w, h)
        self.saveDC.SelectObject(self.bitmap)
        self.saveDC.BitBlt((0, 0), (w, h), self.mfcDC, (x, y), win32con.SRCCOPY)

        bmpstr = self.bitmap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype=np.uint8)
        img.shape = (h, w, 4)
        return np.dot(img[..., :3], [0.114, 0.587, 0.299]).astype(np.uint8)


class Auto_VPT:
    def __init__(self, title):
        self.hwnd = win32gui.FindWindow(None, title)
        self.capture = WindowCapture(self.hwnd)
        self.ava = self.capture.capture_gray(*DICT["Ava"])
        self.auto = True

    def auto_is_on(self):
        auto_available = self.capture.capture_gray(*DICT["Auto"])
        return np.array_equal(auto_available, AUTO_ON_1) or np.array_equal(
            auto_available, AUTO_ON_2
        )

    def not_in_fight(self):
        return np.array_equal(self.capture.capture_gray(*DICT["Ava"]), self.ava)

    def auto_off_in_fight(self):
        return np.array_equal(self.capture.capture_gray(*DICT["AutoCB"]), AUTO_CB)

    def auto_toggle(self):
        if self.not_in_fight() and not self.auto_is_on():
            print(1)
            click_window(self.hwnd, *DICT["Auto Click"][:2])
        if not self.not_in_fight() and self.auto_off_in_fight():
            print(2)
            click_window(self.hwnd, *DICT["CB Click"][:2])


def run_flash(name, server, user, password):
    def to_link(server, user, password):
        return rf"https://s3-vuaphapthuat.goplay.vn/s/{server}/GameLoader.swf?user={user}&pass={password}&isExpand=true"

    subprocess.Popen(["./flash.exe", to_link(server, user, password)])
    threading.Event().wait(1)

    def f(hwnd, name):
        title = win32gui.GetWindowText(hwnd)
        if title == "Adobe Flash Player 34":
            win32gui.SetWindowText(hwnd, name)

    win32gui.EnumWindows(f, name)
