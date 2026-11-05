import json, os, glob, math
from PIL import Image, ImageDraw, ImageFont

FIGS = r"d:\Code\MyProject\真题统计\_build\figs_raw"
OUT = r"d:\Code\MyProject\真题统计\_build\sheets"
os.makedirs(OUT, exist_ok=True)

def font(size=18):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", size)
    except Exception:
        return ImageFont.load_default()

groups = {}
for fp in glob.glob(os.path.join(FIGS, "*.png")):
    base = os.path.basename(fp)
    stem_page = base.split("__f")[0]
    groups.setdefault(stem_page, []).append(fp)

for stem, files in sorted(groups.items()):
    files = sorted(files, key=lambda f: int(f.split("__f")[-1].split(".")[0]))
    cols = 3
    cell_w, cell_h = 360, 300
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    d = ImageDraw.Draw(sheet)
    fnt = font(16)
    for i, f in enumerate(files):
        img = Image.open(f).convert("RGB")
        img.thumbnail((cell_w - 16, cell_h - 46))
        x = (i % cols) * cell_w + 8
        y = (i // cols) * cell_h + 26
        sheet.paste(img, (x, y))
        d.text((x, y - 22), f.split("__f")[-1].split(".")[0], fill="red", font=fnt)
    out = os.path.join(OUT, stem + ".png")
    sheet.save(out)
    print(out, len(files))
