import fitz, os, json, glob, re

SRC = r"d:\Code\MyProject\真题统计\常大真题电子版"
OUT = r"d:\Code\MyProject\真题统计\_build\pages"
os.makedirs(OUT, exist_ok=True)

def year_of(name):
    m = re.search(r"(20\d\d)", name)
    return int(m.group(1)) if m else 0

for p in sorted(glob.glob(os.path.join(SRC, "*.pdf"))):
    name = os.path.basename(p)
    stem = os.path.splitext(name)[0]
    doc = fitz.open(p)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        fp = os.path.join(OUT, f"{stem}__p{i+1}.png")
        pix.save(fp)
        print(fp, pix.width, pix.height)
    doc.close()
