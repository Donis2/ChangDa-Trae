import json, os, glob, re

FIGS = r"d:\Code\MyProject\真题统计\_build\figs_raw"
OCR = r"d:\Code\MyProject\真题统计\_build\ocr"
OUT = r"d:\Code\MyProject\真题统计\_build\layout.txt"

crops = {}
for fp in glob.glob(os.path.join(FIGS, "*.png")):
    base = os.path.basename(fp)
    stem_page = base.split("__f")[0]
    idx = int(base.split("__f")[-1].split(".")[0])
    crops.setdefault(stem_page, []).append((idx, fp))

# parse bbox from log
bbox = {}
for log in [r"d:\Code\MyProject\真题统计\_build\figs_log3.txt"]:
    for line in open(log, encoding="utf-8"):
        m = re.search(r"(.*__f(\d+)\.png) \{'x': (\d+), 'y': (\d+), 'w': (\d+), 'h': (\d+), 'ink': (\d+)\}", line)
        if m:
            fp, idx, x, y, w, h, ink = m.groups()
            bbox[fp] = (int(x), int(y), int(w), int(h), int(ink))

lines = []
for stem_page, items in sorted(crops.items()):
    if "真题答案" in stem_page:
        continue
    page = int(stem_page.split("__p")[1])
    stem = stem_page.split("__p")[0]
    ocr_json = os.path.join(OCR, os.path.basename(stem_page) + ".json")
    ocr_items = json.load(open(ocr_json, encoding="utf-8")) if os.path.exists(ocr_json) else []
    rows = []
    for idx, fp in sorted(items):
        b = bbox.get(fp)
        if b:
            rows.append((b[1], f"FIG f{idx} x={b[0]} y={b[1]} w={b[2]} h={b[3]} ink={b[4]}"))
    for it in ocr_items:
        rows.append((it["y0"], f"TXT x={it['x0']} y={it['y0']} | {it['t']}"))
    rows.sort(key=lambda r: r[0])
    lines.append(f"\n===== {stem} p{page} =====")
    for y, t in rows:
        lines.append(t)

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(OUT)
