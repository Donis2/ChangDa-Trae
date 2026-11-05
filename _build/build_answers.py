# -*- coding: utf-8 -*-
"""生成老魏版 / 考研群资料版两套整卷答案图片，并写入题库 meta。"""
import os, json, io, fitz
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "题目资料来源")
LW_DIR = os.path.join(SRC, "Trae", "题库来源", "真题", "答案原件", "老魏版本的2009-2024答案")
KQ_DIR = os.path.join(SRC, "Workbuddy", "真题答案", "考研群资料版本2009-2026答案")
OUT = os.path.join(ROOT, "常大真题电子版", "web", "assets", "answers")
DATA_JSON = os.path.join(ROOT, "常大真题电子版", "web", "data", "data.json")

LW = {
    2009: "常大2009年答案.pdf", 2010: "常大2010年答案.pdf", 2011: "常大2011年答案.pdf",
    2012: "常大2012年答案.pdf", 2013: "常大2013年答案.pdf", 2014: "常大2014年答案.pdf",
    2015: "常大2015年答案.pdf", 2017: "常大2017年答案.pdf", 2018: "常大2018年答案.pdf",
    2019: "常大2019年答案.pdf", 2020: "常大2020年答案.pdf", 2021: "常大2021年答案.pdf",
    2022: "常大2022年答案.pdf", 2024: "常大2024年答案.pdf",
}
KQ = {
    2009: "2009年答案.pdf", 2010: "2010年答案.pdf", 2011: "2011年答案.pdf",
    2012: "2012年答案.pdf", 2013: "2013年答案.pdf", 2014: "2014年答案.pdf",
    2015: "2015年答案.pdf", 2017: "2017年答案.pdf", 2018: "2018年答案.pdf",
    2019: "2019年答案.pdf", 2020: "2020年答案.pdf", 2021: "2021年答案.pdf",
    2022: "2022年答案.pdf", 2023: "2023年答案.pdf", 2024: "2024年答案.pdf",
    2025: "2025年答案.pdf", 2026: "2026年答案.pdf",
}

MANIFEST = {"laowei": {}, "kaoyanqun": {}}


def render(pdf, version, year, dpi=150):
    outdir = os.path.join(OUT, version)
    os.makedirs(outdir, exist_ok=True)
    doc = fitz.open(pdf)
    names = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        name = f"{year}-{i + 1}.webp"
        img.save(os.path.join(outdir, name), "WEBP", quality=80, method=6)
        names.append(name)
    doc.close()
    return names


for ver, table, folder in (("laowei", LW, LW_DIR), ("kaoyanqun", KQ, KQ_DIR)):
    for year, fname in sorted(table.items()):
        path = os.path.join(folder, fname)
        if not os.path.exists(path):
            print("MISSING", ver, year, path)
            continue
        MANIFEST[ver][str(year)] = render(path, ver, year)
        print(ver, year, len(MANIFEST[ver][str(year)]))

# 写 manifest 供构建/排查
with open(os.path.join(OUT, "manifest-v2.json"), "w", encoding="utf-8") as f:
    json.dump(MANIFEST, f, ensure_ascii=False, indent=1)

# 更新 data.json / data.js
data = json.load(open(DATA_JSON, encoding="utf-8"))
meta = data["meta"]
meta["answerVersions"] = {
    "laowei": {
        "label": "老魏版",
        "desc": "2009—2024 年，2017 年标题页缺失；2023/2025/2026 无此版本",
        "years": sorted(int(y) for y in MANIFEST["laowei"]),
    },
    "kaoyanqun": {
        "label": "考研群资料版",
        "desc": "2009—2026 年；2009—2012 年沿用老魏版答案",
        "years": sorted(int(y) for y in MANIFEST["kaoyanqun"]),
    },
    "default": "kaoyanqun",
}
for y, info in meta["years"].items():
    info["answers"] = {
        "laowei": MANIFEST["laowei"].get(y, []),
        "kaoyanqun": MANIFEST["kaoyanqun"].get(y, []),
    }

json.dump(data, open(DATA_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
js = "window.DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
open(os.path.join(ROOT, "常大真题电子版", "web", "data", "data.js"), "w", encoding="utf-8").write(js)

print("laowei years", len(MANIFEST["laowei"]), "pages", sum(len(v) for v in MANIFEST["laowei"].values()))
print("kaoyanqun years", len(MANIFEST["kaoyanqun"]), "pages", sum(len(v) for v in MANIFEST["kaoyanqun"].values()))
