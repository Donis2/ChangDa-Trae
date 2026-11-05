# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os

SRC = r"d:\Code\MyProject\真题统计\_build\new_pages"
FIG = r"d:\Code\MyProject\真题统计\常大真题电子版\web\assets\figs"

CROPS = {
    "2004-二-1": ("2004__p1.png", 400, 1360, 1590, 2140),
    "2004-二-2": ("2004__p2.png", 310, 800, 1360, 1270),
    "2004-二-4": ("2004__p3.png", 380, 190, 910, 950),
    "2004-三-1": ("2004__p3.png", 130, 1370, 1290, 1760),
    "2006-二-1": ("2006__p2.png", 890, 520, 1480, 930),
    "2006-二-2": ("2006__p3.png", 100, 80, 860, 480),
    "2006-二-3": ("2006__p3.png", 950, 530, 1600, 1080),
    "2006-二-4": ("2006__p3.png", 970, 1390, 1610, 1675),
    "2006-二-6": ("2006__p4.png", 600, 970, 1800, 1620),
    "2007-一-1": ("2007__p1.png", 380, 1050, 1480, 1490),
    "2007-二-1": ("2007__p2.png", 390, 730, 2100, 1550),
    "2007-二-2": ("2007__p3.png", 520, 690, 1540, 1260),
    "2007-二-3": ("2007__p4.png", 400, 520, 2100, 1320),
    "2007-二-4": ("2007__p6.png", 170, 330, 2090, 1350),
    "2008-三-1": ("2008__p3.png", 320, 685, 1060, 1550),
    "2008-四-1": ("2008__p4.png", 340, 100, 1000, 880),
    "2008-五-1": ("2008__p3.png", 1100, 655, 2120, 1550),
    "2008-六-1": ("2008__p4.png", 1090, 140, 2100, 800),
    "2008-八-1": ("2008__p5.png", 410, 210, 2050, 920),
}

for name, (f, x0, y0, x1, y1) in CROPS.items():
    im = Image.open(os.path.join(SRC, f))
    box = (max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1))
    crop = im.crop(box)
    crop.save(os.path.join(FIG, name + ".png"), optimize=True)
    print(name, crop.size)

# contact sheet
font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 28)
cols, thumb_w, thumb_h = 4, 460, 340
rows = (len(CROPS) + cols - 1) // cols
sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 45)), "white")
d = ImageDraw.Draw(sheet)
for i, (name, _) in enumerate(CROPS.items()):
    im = Image.open(os.path.join(FIG, name + ".png")).convert("RGB")
    im.thumbnail((thumb_w - 12, thumb_h - 8))
    x = (i % cols) * thumb_w; y = (i // cols) * (thumb_h + 45)
    sheet.paste(im, (x + 6, y + 40))
    d.text((x + 6, y + 6), name, fill="black", font=font)
sheet.save(r"d:\Code\MyProject\真题统计\_build\fig_contact.png")
