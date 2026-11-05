import sys, os, json, glob, time
from rapidocr_onnxruntime import RapidOCR

PAGES = r"d:\Code\MyProject\真题统计\_build\pages"
OUT = r"d:\Code\MyProject\真题统计\_build\ocr"
os.makedirs(OUT, exist_ok=True)
ocr = RapidOCR()

files = sorted(glob.glob(os.path.join(PAGES, "*.png")))
if len(sys.argv) > 1:
    files = [f for f in files if any(k in f for k in sys.argv[1:])]

for f in files:
    outj = os.path.join(OUT, os.path.basename(f).replace(".png", ".json"))
    if os.path.exists(outj):
        print("skip", f)
        continue
    t0 = time.time()
    res, _ = ocr(f)
    items = []
    if res:
        for box, txt, score in res:
            xs = [p[0] for p in box]; ys = [p[1] for p in box]
            items.append({"t": txt, "s": round(float(score), 3), "x0": round(min(xs)), "y0": round(min(ys)),
                          "x1": round(max(xs)), "y1": round(max(ys))})
    with open(outj, "w", encoding="utf-8") as fh:
        json.dump(items, fh, ensure_ascii=False, indent=0)
    print(f"{os.path.basename(f)} lines={len(items)} t={time.time()-t0:.1f}s")
