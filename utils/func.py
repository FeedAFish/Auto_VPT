import ctypes
from ctypes import windll
import win32gui
import win32ui
import win32con
import numpy as np
import ast
import time
from PIL import Image

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
del content


def click_window(title, x, y):
    # Get the handle of the window
    hwnd = win32gui.FindWindow(None, title)
    if hwnd:
        # Convert coordinates to LPARAM
        lparam = (y << 16) | x

        # Send the click messages
        ctypes.windll.user32.SendMessageW(hwnd, WM_LBUTTONDOWN, 0, lparam)
        ctypes.windll.user32.SendMessageW(hwnd, WM_LBUTTONUP, 0, lparam)
    else:
        raise Exception("Window not found.")


def screenshot_window_to_gray_numpy(title, x=None, y=None, w=None, h=None):
    hwnd = win32gui.FindWindow(None, title)
    if x is None or y is None or w is None or h is None:
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        x, y, w, h = left, top, right - left, bot - top
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)

    saveDC.BitBlt((0, 0), (w, h), mfcDC, (x, y), win32con.SRCCOPY)

    bmpstr = saveBitMap.GetBitmapBits(True)
    img_array = np.frombuffer(bmpstr, dtype=np.uint8)
    img_array.shape = (h, w, 4)  # BGR format

    img_array = img_array[..., :3]

    gray = np.dot(img_array, [0.114, 0.587, 0.299]).astype(np.uint8)
    return gray


def get_ava_available(title):
    x, y, w, h = DICT["Ava"]
    screenshot_window_to_gray_numpy(title, x, y, w, h)


class Auto_VPT:
    def __init__(self, title):
        self.title = title
        self.ava = get_ava_available(self.title)
        self.auto = True
        # self.auto_toggle()

    def auto_is_on(self):
        auto_available = screenshot_window_to_gray_numpy(self.title, *DICT["Auto"])
        return np.array_equal(auto_available, AUTO_ON_1) or np.array_equal(
            auto_available, AUTO_ON_2
        )

    def not_in_fight(self):
        return np.array_equal(get_ava_available(self.title), self.ava)

    def auto_toggle(self):
        if self.not_in_fight() and not self.auto_is_on():
            click_window(self.title, *DICT["Auto Click"][:2])

    def loop_auto(self):
        while self.auto:
            self.auto_toggle()
            time.sleep(2)
