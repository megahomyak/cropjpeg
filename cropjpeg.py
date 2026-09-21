#!/usr/bin/python3

import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageGrab, ImageTk

img = ImageGrab.grabclipboard()
if not isinstance(img, Image.Image):
    raise SystemExit("No image found in clipboard")

root = tk.Tk()
root.attributes("-fullscreen", True)

W, R, M = 2, 14, 20
cw, ch = root.winfo_screenwidth(), root.winfo_screenheight()
scale = min(1.0, (cw - 2 * M) / img.width, (ch - 2 * M) / img.height)
dw, dh = round(img.width * scale), round(img.height * scale)
tkimg = ImageTk.PhotoImage(img.resize((dw, dh), Image.LANCZOS))

canvas = tk.Canvas(root, highlightthickness=0, bg="gray20")
canvas.pack(fill="both", expand=True)
ox, oy = (cw - dw) // 2, (ch - dh) // 2
canvas.create_image(ox, oy, anchor="nw", image=tkimg)

p = [[ox, oy], [ox + dw, oy + dh]]
outline = canvas.create_rectangle(0, 0, 0, 0, outline="red", width=W)
dragging = None
cancelled = False

def redraw():
    (x0, x1), (y0, y1) = sorted((p[0][0], p[1][0])), sorted((p[0][1], p[1][1]))
    canvas.coords(outline, x0 - W / 2, y0 - W / 2, x1 + W / 2, y1 + W / 2)

def start_drag(h, pos):
    def _start(_e):
        global dragging
        dragging = (h, pos)
    return _start

def on_drag(e):
    if dragging is None:
        return
    h, pos = dragging
    pos[:] = [max(ox, min(ox + dw, e.x)), max(oy, min(oy + dh, e.y))]
    canvas.coords(h, pos[0]-R, pos[1]-R, pos[0]+R, pos[1]+R)
    redraw()

def on_release(_e):
    global dragging
    dragging = None

def on_enter(_e):
    root.quit()

def on_escape(_e):
    global cancelled
    cancelled = True
    root.quit()

for pos in p:
    h = canvas.create_oval(pos[0]-R, pos[1]-R, pos[0]+R, pos[1]+R,
                           fill="red", outline="white", width=2)
    canvas.tag_bind(h, "<Button-1>", start_drag(h, pos))
redraw()

canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)
root.bind("<Return>", on_enter)
root.bind("<Escape>", on_escape)
root.mainloop()

if cancelled:
    root.destroy()
    raise SystemExit("Cancelled")

(x0, x1), (y0, y1) = sorted((p[0][0], p[1][0])), sorted((p[0][1], p[1][1]))
cropped = img.crop((round((x0-ox)/scale), round((y0-oy)/scale),
                    round((x1-ox)/scale), round((y1-oy)/scale))).convert("RGB")

root.withdraw()
name = simpledialog.askstring("Save", "File name (no extension):", parent=root)
root.destroy()
if name:
    cropped.save(name + ".jpg", "JPEG")
    print(f"Saved {name}.jpg")
