import win32gui


def getShell():
    thelist = []

    def findit(hwnd, ctx):
        thelist.append(win32gui.GetWindowText(hwnd))

    win32gui.EnumWindows(findit, None)
    return thelist


b = getShell()
with open("shell.txt", "w") as f:
    for i in b:
        print(i.encode("utf-8"), file=f)
