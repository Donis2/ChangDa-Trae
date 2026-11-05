import fitz, os, json, glob

SRC = r"d:\Code\MyProject\真题统计\常大真题电子版"
out = []
for p in sorted(glob.glob(os.path.join(SRC, "*.pdf"))):
    doc = fitz.open(p)
    pages = []
    imgs = 0
    for i, page in enumerate(doc):
        t = page.get_text("text")
        pages.append({"page": i + 1, "chars": len(t.strip()), "images": len(page.get_images(full=True))})
        imgs += len(page.get_images(full=True))
    out.append({"file": os.path.basename(p), "size": os.path.getsize(p), "pages": len(doc), "images": imgs, "perpages": pages})
    doc.close()

print(json.dumps(out, ensure_ascii=False, indent=1))
