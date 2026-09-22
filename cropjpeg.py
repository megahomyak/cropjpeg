#!/usr/bin/env python3
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageGrab, ImageTk


def main():
    HANDLE = 8   # handle radius = fit padding = click tolerance
    WIDTH  = 2   # crop rectangle border thickness, in pixels

    root = tk.Tk()
    root.title("cropjpeg: v to paste, drag handles, s to save")
    try:
        root.state("zoomed")              # Windows
    except tk.TclError:
        root.attributes("-zoomed", True)  # Linux / X11

    canvas = tk.Canvas(root, bg="#222", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    img   = None           # PIL image
    photo = None           # tk reference (must outlive the canvas item)
    scale = 0              # image pixels -> canvas pixels
    ox = oy = 0            # canvas position of the image's top-left corner
    p1 = p2 = (0, 0)       # crop corners, in canvas coordinates
    drag = 0               # 0 = none, 1 = p1, 2 = p2

    def render():
        canvas.delete("all")
        if img is None:
            return
        canvas.create_image(ox, oy, anchor="nw", image=photo)
        # Tk centres a rectangle's stroke on its path, so a path drawn on
        # [p1, p2] would bleed WIDTH/2 inward and cover part of the crop.
        # Offset the path outward by WIDTH/2 so the inner stroke edge lands
        # exactly on the crop boundary and nothing inside gets painted over.
        (x1, y1), (x2, y2) = p1, p2
        canvas.create_rectangle(x1 - WIDTH / 2, y1 - WIDTH / 2,
                                x2 + WIDTH / 2, y2 + WIDTH / 2,
                                outline="red", fill="", width=WIDTH)
        for x, y in (p1, p2):
            canvas.create_oval(x - HANDLE, y - HANDLE, x + HANDLE, y + HANDLE,
                               fill="red")

    def paste(_=None):
        nonlocal img, photo, scale, ox, oy, p1, p2
        got = ImageGrab.grabclipboard()
        if not isinstance(got, Image.Image):
            return
        img = got.convert("RGB")
        iw, ih = img.size
        cw, ch = canvas.winfo_width(), canvas.winfo_height()
        scale = min((cw - 2*HANDLE) / iw, (ch - 2*HANDLE) / ih)
        ox, oy = (cw - iw*scale) / 2, (ch - ih*scale) / 2
        photo = ImageTk.PhotoImage(img.resize((int(iw*scale), int(ih*scale))))
        p1, p2 = (ox, oy), (ox + iw*scale, oy + ih*scale)
        render()

    def press(e):
        nonlocal drag
        if img is None:
            return
        drag = 0
        for i, (x, y) in enumerate((p1, p2), 1):
            if abs(e.x - x) <= HANDLE and abs(e.y - y) <= HANDLE:
                drag = i
                return

    def motion(e):
        nonlocal p1, p2
        if not drag:
            return
        x = min(max(e.x, ox), ox + img.width  * scale)
        y = min(max(e.y, oy), oy + img.height * scale)
        if drag == 1:
            p1 = min(x, p2[0]), min(y, p2[1])
        else:
            p2 = max(x, p1[0]), max(y, p1[1])
        render()

    def save(_=None):
        if img is None:
            return
        name = simpledialog.askstring("Save", "File name:")
        if not name:
            return
        box = (int((p1[0] - ox) / scale), int((p1[1] - oy) / scale),
               int((p2[0] - ox) / scale), int((p2[1] - oy) / scale))
        img.crop(box).save(name + ".jpg", "JPEG")

    root.bind("v", paste)
    root.bind("s", save)
    canvas.bind("<Button-1>", press)
    canvas.bind("<B1-Motion>", motion)

    root.mainloop()


main()
