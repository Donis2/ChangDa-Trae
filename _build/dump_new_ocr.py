# -*- coding: utf-8 -*-
import json, glob, os
OCR = r"d:\Code\MyProject\真题统计\_build\new_ocr"
for f in sorted(glob.glob(os.path.join(OCR, "*.json"))):
    items = json.load(open(f, encoding="utf-8"))
    items.sort(key=lambda a: (a["y0"], a["x0"]))
    print("\n===== " + os.path.basename(f) + " =====")
    for it in items:
        print(f"[{it['y0']:4d},{it['x0']:4d}] {it['t']}")
