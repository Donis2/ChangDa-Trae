# -*- coding: utf-8 -*-
import fitz, os, glob, json, re, time
from rapidocr_onnxruntime import RapidOCR

BASE = r"d:\Code\MyProject\真题统计\常大真题电子版\原始资料\真题原卷"
OUT = r"d:\Code\MyProject\真题统计\_build\new_pages"
OCR = r"d:\Code\MyProject\真题统计\_build\new_ocr"
os.makedirs(OUT, exist_ok=True)
os.makedirs(OCR, exist_ok=True)

years = ["2004", "2006", "2007", "2008"]
for y in years:
    p = os.path.join(BASE, f"常大{y}年真题.pdf")
    d = fitz.open(p)
    for i, page in enumerate(d):
        # 横向页面可能为双页扫描，按原方向渲染 200dpi
        pix = page.get_pixmap(dpi=200, alpha=False)
        pix.save(os.path.join(OUT, f"{y}__p{i+1}.png"))
    d.close()

ocr = RapidOCR()
for y in years:
    for f in sorted(glob.glob(os.path.join(OUT, f"{y}__p*.png"))):
        outj = os.path.join(OCR, os.path.basename(f).replace(".png", ".json"))
        if os.path.exists(outj):
            continue
        t0 = time.time()
        res, _ = ocr(f)
        items = []
        if res:
            for box, txt, score in res:
                xs = [p[0] for p in box]; ys = [p[1] for p in box]
                items.append({"t": txt, "s": round(float(score), 3),
                              "x0": round(min(xs)), "y0": round(min(ys)),
                              "x1": round(max(xs)), "y1": round(max(ys))})
        json.dump(items, open(outj, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(os.path.basename(f), len(items), f"{time.time()-t0:.1f}s")
