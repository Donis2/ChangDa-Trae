# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os

SRC = r"d:\Code\MyProject\真题统计\_build\p2026"
FIG = r"d:\Code\MyProject\真题统计\常大真题电子版\web\assets\figs"

CROPS = {
    "2026-三-4": ("2026__p3.png", 150, 1330, 1450, 1670),
    "2026-三-6": ("2026__p3.png", 640, 110, 1430, 680),
    "2026-三-7": ("2026__p4.png", 330, 640, 1300, 1045),
}

for name, (f, x0, y0, x1, y1) in CROPS.items():
    im = Image.open(os.path.join(SRC, f))
    crop = im.crop((max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1)))
    crop.save(os.path.join(FIG, name + ".png"), optimize=True)
    print(name, crop.size)

font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 28)
cols, tw, th = 3, 520, 380
sheet = Image.new("RGB", (cols * tw, th + 50), "white")
d = ImageDraw.Draw(sheet)
for i, (name, _) in enumerate(CROPS.items()):
    im = Image.open(os.path.join(FIG, name + ".png")).convert("RGB")
    im.thumbnail((tw - 12, th - 8))
    d.text((i * tw + 6, 6), name, fill="black", font=font)
    sheet.paste(im, (i * tw + 6, 44))
sheet.save(r"d:\Code\MyProject\真题统计\_build\fig_contact_2026.png")
