import json, os
from PIL import Image, ImageDraw, ImageFont

DIR = r"d:\Code\MyProject\真题统计\常大真题电子版\web\assets\figs"
OUT = r"d:\Code\MyProject\真题统计\_build\verify"
os.makedirs(OUT, exist_ok=True)
man = json.load(open(os.path.join(DIR, "manifest.json"), encoding="utf-8"))

def font(sz):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", sz)
    except Exception:
        return ImageFont.load_default()

groups = {}
for k in man:
    y = int(k.split("-")[0])
    groups.setdefault(y, []).append(k)

for y, keys in sorted(groups.items()):
    keys.sort(key=lambda k: (int(k.split("-")[1]), k))
    cols, cw, ch = 3, 420, 360
    rows = (len(keys) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * ch), "white")
    d = ImageDraw.Draw(sheet)
    f = font(18)
    for i, k in enumerate(keys):
        img = Image.open(os.path.join(DIR, man[k][0])).convert("RGB")
        img.thumbnail((cw - 16, ch - 46))
        x = (i % cols) * cw + 8
        yy = (i // cols) * ch + 30
        sheet.paste(img, (x, yy))
        d.text((x, yy - 24), k, fill=(200, 0, 0), font=f)
    sheet.save(os.path.join(OUT, f"{y}.png"))
    print(y, len(keys))
