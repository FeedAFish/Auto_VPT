from utils import func
from PIL import Image

img = func.screenshot_window_to_gray_numpy("Main", *func.DICT["Auto"])

im = Image.fromarray(img)
im.save("test.png")
