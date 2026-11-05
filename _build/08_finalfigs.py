# -*- coding: utf-8 -*-
import os, re, json
from PIL import Image

BUILD = r"d:\Code\MyProject\真题统计\_build"
PAGES = os.path.join(BUILD, "pages")
OUT = r"d:\Code\MyProject\真题统计\常大真题电子版\web\assets\figs"
os.makedirs(OUT, exist_ok=True)

# f-index bboxes from detection log
BB = {}
for line in open(os.path.join(BUILD, "figs_log4.txt"), encoding="utf-8-sig"):
    m = re.search(r"\\([^\\]+)__p(\d+)__f(\d+)\.png \{'x': (\d+), 'y': (\d+), 'w': (\d+), 'h': (\d+)", line)
    if m:
        stem, page, idx, x, y, w, h = m.groups()
        BB[f"{stem}__p{page}:f{idx}"] = (int(x), int(y), int(w), int(h))

STEMS = {
    2009: "常州大学855机械设计基础2009年",
    2010: "常州大学855机械设计基础2010年",
    2011: "常州大学855机械设计基础2011年",
    2012: "常州大学855机械设计基础2012年",
    2013: "常州大学855机械设计基础2013年",
    2014: "常州大学855机械设计基础2014年",
    2015: "常州大学855机械设计基础2015年",
    2017: "常州大学855机械设计基础2017年",
    2018: "常州大学855机械设计基础2018年",
    2019: "常州大学855机械设计基础2019年",
    2020: "常州大学855机械设计基础2020年",
    2021: "常州大学855机械设计基础2021年",
    2022: "常州大学855机械设计基础2022年真题",
    2024: "2024常州大学真题",
}

def ref(year, page, fid=None, rect=None):
    if rect:
        return [("rect", STEMS[year], page, rect)]
    return [(f"{STEMS[year]}__p{page}:f{fid}")]

FIGMAP = {
    "2009-3-2": ref(2009, 1, None) + ref(2009, 1, None),  # placeholder, replaced below
}

# build explicitly
def R(year, page, fid):
    return [f"{STEMS[year]}__p{page}:f{fid}"]

def RC(year, page, rect):
    return [(STEMS[year], page, rect)]

FIGMAP = {
    "2009-3-2": R(2009, 1, 2) + RC(2009, 1, (1062, 1896, 288, 288)),
    "2009-4-1": R(2009, 2, 1),
    "2009-4-3": R(2009, 2, 2),
    "2009-4-4": R(2009, 2, 3),
    "2009-5-1": R(2009, 2, 4),

    "2010-1-15": RC(2010, 1, (150, 1228, 345, 128)),
    "2010-3-1": R(2010, 1, 4),
    "2010-3-2": R(2010, 1, 3),
    "2010-3-4": R(2010, 2, 1),
    "2010-3-5": R(2010, 2, 2),
    "2010-3-6-1": R(2010, 3, 2),
    "2010-3-6-2": R(2010, 3, 1),
    "2010-3-6-3": R(2010, 3, 3),
    "2010-3-6-4": R(2010, 3, 4),
    "2010-3-6-5": R(2010, 3, 5),

    "2011-4-1a": R(2011, 1, 5),
    "2011-4-1b": R(2011, 1, 6),
    "2011-4-2": RC(2011, 2, (200, 285, 950, 210)),
    "2011-4-5": R(2011, 2, 3),
    "2011-4-6": R(2011, 2, 5),

    "2012-4-1": R(2012, 2, 4),
    "2012-5-1a": R(2012, 3, 1),
    "2012-5-1b": R(2012, 3, 2),
    "2012-5-3": R(2012, 3, 4),
    "2012-5-4": R(2012, 3, 5),

    "2013-3-1": R(2013, 2, 4),
    "2013-5-1": R(2013, 2, 6),
    "2013-5-2": R(2013, 2, 7),
    "2013-6-1": R(2013, 2, 8),
    "2013-7-1": R(2013, 3, 1),
    "2013-7-2": R(2013, 3, 2),
    "2013-8-1": R(2013, 3, 3),
    "2013-9-1": R(2013, 3, 4),

    "2014-3-1a": R(2014, 2, 1),
    "2014-3-1b": R(2014, 2, 2),
    "2014-4-1a": R(2014, 3, 1),
    "2014-4-1b": RC(2014, 3, (1320, 420, 690, 570)),
    "2014-5-1": R(2014, 3, 5),
    "2014-6-1": RC(2014, 3, (1140, 1340, 880, 400)),
    "2014-7-1": R(2014, 3, 12),

    "2015-4-1": R(2015, 2, 1),
    "2015-4-3": R(2015, 2, 2),
    "2015-4-4": R(2015, 2, 3),
    "2015-5-1": R(2015, 2, 4),

    "2017-3-1": R(2017, 2, 4),
    "2017-4-1": R(2017, 2, 5),
    "2017-5-1": R(2017, 2, 7),
    "2017-6-1": R(2017, 3, 1),
    "2017-7-1": R(2017, 3, 2),
    "2017-8-1": R(2017, 3, 4),

    "2018-1-10": RC(2018, 1, (260, 1950, 640, 180)),
    "2018-2-2": RC(2018, 2, (185, 550, 1240, 185)),
    "2018-2-5": RC(2018, 2, (180, 945, 1100, 170)),
    "2018-3-1": R(2018, 3, 3),
    "2018-5-1": R(2018, 3, 4),
    "2018-6-1": R(2018, 3, 5),
    "2018-7-1": R(2018, 3, 6),
    "2018-8-1": RC(2018, 3, (205, 1485, 430, 350)),
    "2018-9-1": RC(2018, 3, (575, 1485, 800, 460)),

    "2019-2-5": R(2019, 1, 3),
    "2019-3-1": R(2019, 2, 3),
    "2019-4-1": R(2019, 2, 2),
    "2019-5-1": RC(2019, 3, (110, 550, 850, 440)),
    "2019-6-1": R(2019, 3, 2),
    "2019-7-1": R(2019, 3, 4),
    "2019-8-1": R(2019, 3, 3),
    "2019-9-1": R(2019, 3, 5),

    "2020-3-1": R(2020, 2, 2),
    "2020-4-1": R(2020, 2, 6),
    "2020-5-1": R(2020, 2, 4),
    "2020-6-1": R(2020, 2, 3),
    "2020-8-1": R(2020, 2, 5),
    "2020-9-1": RC(2020, 2, (1080, 1360, 500, 300)),

    "2021-2-1": RC(2021, 2, (200, 330, 590, 350)),
    "2021-2-3": R(2021, 2, 2),
    "2021-3-1a": RC(2021, 2, (320, 845, 330, 300)),
    "2021-3-1b": RC(2021, 2, (645, 855, 330, 295)),
    "2021-3-2": RC(2021, 2, (987, 850, 415, 320)),

    "2022-2-4": R(2022, 2, 2),
    "2022-3-1": R(2022, 3, 3),
    "2022-5-1": R(2022, 3, 4),
    "2022-7-1": R(2022, 3, 5),
    "2022-8-1": R(2022, 3, 6),
    "2022-9-1": R(2022, 3, 7),

    "2024-3-1": R(2024, 2, 2),
    "2024-3-2": R(2024, 2, 3),
    "2024-3-3": R(2024, 2, 4),
    "2024-3-4": R(2024, 3, 2),
    "2024-3-5": R(2024, 3, 3),
    "2024-3-7": R(2024, 4, 2),
}

# merge adjacent refs of same page into union? No: keep separate images; but for multiple refs, emit suffix
manifest = {}
for key, refs in FIGMAP.items():
    imgs = []
    for i, r in enumerate(refs):
        if isinstance(r, str):
            stem, fid = r.split(":")
            page_no = int(re.search(r"__p(\d+)", stem).group(1))
            page_stem = stem.split("__p")[0]
            x, y, w, h = BB[r]
            src = os.path.join(PAGES, stem + ".png")
            x, y, w, h = x - 6, y - 6, w + 12, h + 12
        else:
            page_stem, page_no, (x, y, w, h) = r
            src = os.path.join(PAGES, f"{page_stem}__p{page_no}.png")
        im = Image.open(src).convert("L")
        W, H = im.size
        box = (max(0, x), max(0, y), min(W, x + w), min(H, y + h))
        crop = im.crop(box)
        # upscale small crops for readability
        if crop.width < 500:
            f = min(2.0, 600 / crop.width)
            crop = crop.resize((int(crop.width * f), int(crop.height * f)), Image.LANCZOS)
        name = f"{key}{'' if len(refs) == 1 else chr(97 + i)}.png"
        crop.save(os.path.join(OUT, name), optimize=True)
        imgs.append(name)
    manifest[key] = imgs

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(manifest), "figures,", sum(len(v) for v in manifest.values()), "images")
