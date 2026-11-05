import json, os, glob, re

OCR = r"d:\Code\MyProject\真题统计\_build\ocr"
OUT = r"d:\Code\MyProject\真题统计\_build\texts.txt"

def load(fp):
    items = json.load(open(fp, encoding="utf-8"))
    items.sort(key=lambda it: (it["y0"], it["x0"]))
    return items

groups = {}
for fp in glob.glob(os.path.join(OCR, "*.json")):
    name = os.path.basename(fp).replace(".json", "")
    stem, page = name.rsplit("__p", 1)
    groups.setdefault(stem, []).append((int(page), fp))

lines = []
for stem, pages in sorted(groups.items()):
    lines.append(f"\n\n{'='*20} {stem} {'='*20}")
    for page, fp in sorted(pages):
        lines.append(f"\n--- p{page} ---")
        for it in load(fp):
            lines.append(f"[{it['y0']},{it['x0']}-{it['x1']}] {it['t']}")
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(OUT, len(lines))
