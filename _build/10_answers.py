# -*- coding: utf-8 -*-
import os, json
from PIL import Image

SRC = r"d:\Code\MyProject\真题统计\_build\pages"
OUT = r"d:\Code\MyProject\真题统计\常大真题电子版\web\assets\answers"
os.makedirs(OUT, exist_ok=True)

# (page_no, half) -> year
MAP = {
    (1, "A"): 2013, (1, "B"): 2014,
    (2, "A"): 2015, (2, "B"): 2017,
    (3, "A"): 2018, (3, "B"): 2018,
    (4, "A"): 2017, (4, "B"): 2019,
    (5, "A"): 2020, (5, "B"): 2020,
    (6, "A"): 2021, (6, "B"): 2021,
    (7, "A"): 2021, (7, "B"): 2022,
}

manifest = {}
for (pno, half), year in MAP.items():
    im = Image.open(os.path.join(SRC, f"真题答案2013-2022__p{pno}.png")).convert("L")
    w, h = im.size
    if half == "A":
        box = (int(w * 0.10), int(h * 0.04), int(w * 0.94), int(h * 0.50))
    else:
        box = (int(w * 0.10), int(h * 0.51), int(w * 0.94), int(h * 0.97))
    crop = im.crop(box)
    name = f"ans-{pno}{half}.png"
    crop.save(os.path.join(OUT, name), optimize=True)
    manifest.setdefault(str(year), []).append(name)

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(manifest, ensure_ascii=False))
