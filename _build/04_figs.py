import cv2, numpy as np, json, os, glob, sys
from PIL import Image

def imread_u(path):
    return np.array(Image.open(path).convert("L"))

def imwrite_u(path, arr):
    Image.fromarray(arr).save(path)

PAGES = r"d:\Code\MyProject\真题统计\_build\pages"
OCR = r"d:\Code\MyProject\真题统计\_build\ocr"
OUT = r"d:\Code\MyProject\真题统计\_build\figs_raw"

def detect(png, ocr_json):
    img = imread_u(png)
    H, W = img.shape
    ink = (img < 175).astype(np.uint8) * 255
    items = json.load(open(ocr_json, encoding="utf-8")) if os.path.exists(ocr_json) else []
    mask = ink.copy()
    # remove page frame lines (long thin components)
    n0, lab0, st0, _ = cv2.connectedComponentsWithStats(ink)
    for i in range(1, n0):
        x, y, w, h, area = st0[i]
        if (w > 0.8 * W and h < 0.06 * H) or (h > 0.8 * H and w < 0.06 * W):
            mask[lab0 == i] = 0
    for it in items:
        txt = it["t"].strip()
        # assume lines with >=4 chars and width >= 90 are text, not figure labels
        if len(txt) >= 4 and (it["x1"] - it["x0"]) >= 90:
            pad = 4
            x0, y0 = max(0, it["x0"] - pad), max(0, it["y0"] - pad)
            x1, y1 = min(W, it["x1"] + pad), min(H, it["y1"] + pad)
            mask[y0:y1, x0:x1] = 0
    mask[: int(H * 0.03), :] = 0
    mask[int(H * 0.96):, :] = 0
    mask[:, : int(W * 0.015)] = 0
    mask[:, int(W * 0.985):] = 0
    dil = cv2.dilate(mask, np.ones((41, 41), np.uint8), iterations=1)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(dil)
    boxes = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        sub = mask[y:y + h, x:x + w]
        inkpx = int((sub > 0).sum())
        if inkpx < 700 or w < 75 or h < 40:
            continue
        if w > 0.94 * W and h < 0.12 * H:
            continue
        # tight bbox: rows/cols with ink
        rows = (sub > 0).sum(axis=1)
        cols = (sub > 0).sum(axis=0)
        ys = np.where(rows > 0)[0]
        xs = np.where(cols > 0)[0]
        if len(ys) == 0 or len(xs) == 0:
            continue
        y_a, y_b = y + ys[0], y + ys[-1]
        x_a, x_b = x + xs[0], x + xs[-1]
        boxes.append({"x": int(x_a), "y": int(y_a), "w": int(x_b - x_a), "h": int(y_b - y_a), "ink": inkpx})
    boxes.sort(key=lambda b: (b["y"], b["x"]))
    return img, boxes

if __name__ == "__main__":
    keys = sys.argv[1:]
    for png in sorted(glob.glob(os.path.join(PAGES, "*.png"))):
        if keys and not any(k in png for k in keys):
            continue
        ocr_json = os.path.join(OCR, os.path.basename(png).replace(".png", ".json"))
        img, boxes = detect(png, ocr_json)
        base = os.path.basename(png).replace(".png", "")
        for j, b in enumerate(boxes):
            pad = 10
            H, W = img.shape
            crop = img[max(0, b["y"] - pad): min(H, b["y"] + b["h"] + pad), max(0, b["x"] - pad): min(W, b["x"] + b["w"] + pad)]
            fp = os.path.join(OUT, f"{base}__f{j+1}.png")
            imwrite_u(fp, crop)
            print(fp, b)
