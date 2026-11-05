# -*- coding: utf-8 -*-
"""抽取非真题资料中的扩展题，去重并标注其中出现过的真题。"""
import json, os, re, sys, glob, difflib, collections, csv, io
import fitz
from docx import Document

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "题目资料来源", "Trae", "题库来源")
DATA = json.load(open(os.path.join(ROOT, "常大真题电子版", "web", "data", "data.json"), encoding="utf-8"))
QS = DATA["questions"]
sys.path.insert(0, os.path.join(ROOT, "_build"))
import subrules

META_SUBS = {c: (n, ch) for c, n, ch, _ in subrules.SUBS}
SUB_RULES = {c: kw for c, n, ch, kw in subrules.SUBS}
CH_ORDER = [c["code"] for c in DATA["meta"]["chapters"]]


def clean_text(s):
    s = (s or "").replace("\x00", "")
    s = re.sub(r"(?<=[\u4e00-\u9fff0-9])\s+(?=[\u4e00-\u9fff0-9])", "", s)
    s = re.sub(r"\s+([，。；：、？！])", r"\1", s)
    s = re.sub(r"([（【])\s+", r"\1", s)
    s = re.sub(r"\s+([）】])", r"\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def norm(s):
    s = re.sub(r"\s+", "", s or "")
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "", s)
    return s.lower()


def guess_subs(text):
    scores = collections.Counter()
    for code, words in SUB_RULES.items():
        for w in words:
            n = text.count(w)
            if n:
                scores[code] += n * (3 if len(w) >= 6 else (2 if len(w) >= 3 else 1))
    if not scores:
        return []
    ranked = scores.most_common()
    top = ranked[0][1]
    picked, chapters = [], set()
    for i, (code, s) in enumerate(ranked):
        if i > 0 and s < max(1.5, top * 0.45):
            continue
        ch = META_SUBS[code][1]
        if ch in chapters and len(picked) >= 2:
            continue
        picked.append(code)
        chapters.add(ch)
        if len(picked) >= 3:
            break
    return picked


def parse_numbered(text):
    text = text.replace("\r", "")
    parts = re.split(r"(?m)^\s*(\d{1,3})\s*[.、．]\s*", text)
    out = []
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        lines = [l.strip() for l in body.split("\n") if l.strip()]
        lines = [l for l in lines if not re.search(r"(简答题汇编|简答题专项训练|机械设计基础|第\s*\d+\s*页)", l)]
        stem, ans = [], []
        for l in lines:
            if re.match(r"^(答|【答案】|【参考答案】)", l):
                ans.append(re.sub(r"^(答|【答案】|【参考答案】)[:：]?\s*", "", l))
            elif ans:
                ans.append(l)
            else:
                stem.append(l)
        stem = re.sub(r"^.*?共\s*\d+\s*题.*$", "", " ".join(stem)).strip()
        out.append({"no": int(parts[i]), "stem": " ".join(stem), "answer": " ".join(ans)})
    return out


def is_question(p):
    if re.match(r"^\d{1,2}\s*[.、．]", p):
        return True
    if p.endswith("?") or p.endswith("？"):
        return True
    return bool(re.match(r"^(简述|试述|什么|为什么|如何|何谓|说明|比较|指出|画出|计算|分析|论述|解释|列举|判断|写出|求)", p))


def parse_docx(path):
    """《简答题（30题）.docx》无稳定编号，按人工核对过的题干段落索引切分。"""
    doc = Document(path)
    ps = [x.text.strip() for x in doc.paragraphs if x.text.strip()]
    qidx = [1, 3, 7, 10, 12, 15, 19, 21, 23, 25, 27, 29, 33, 35, 37, 39, 41, 43,
            45, 48, 51, 53, 55, 62, 64, 67, 69, 71, 73, 74]
    out = []
    for k, idx in enumerate(qidx):
        if idx >= len(ps):
            continue
        end = qidx[k + 1] if k + 1 < len(qidx) else len(ps)
        ans = " ".join(ps[idx + 1:end]).strip()
        out.append({"no": k + 1, "stem": re.sub(r"^\d{1,2}\s*[.、．]\s*", "", ps[idx]), "answer": ans})
    return out


ext = []  # dict: id later, type, stem, options, answer, source list, chapter/subs


def add(stem, answer, srcfile, no, typ="简答", options=None, chapter=None, source_label=None,
        explanation=""):
    stem = clean_text(stem)
    if not stem or len(norm(stem)) < 4:
        return
    if typ == "简答" and re.match(r"^\d", stem):
        return
    ext.append({
        "type": typ, "text": stem, "options": options or [], "answer": clean_text(answer),
        "explanation": clean_text(explanation),
        "sources": [{"file": srcfile, "no": no, "label": source_label or srcfile}],
        "chapter": chapter, "subs": guess_subs(stem),
    })


# 1) 青蛙题库
frog = json.load(open(os.path.join(ROOT, "_build", "frog_integrated.json"), encoding="utf-8"))
for f in frog:
    add(f["stem"], f.get("answer") or "", "常大855-青蛙弟弟选择题题库.pdf", f.get("no"),
        typ="选择", options=f.get("options") or [], chapter=f.get("chapter"),
        source_label="青蛙弟弟选择题题库", explanation=f.get("expl") or "")

# 2) 六份简答专项
labels = {"一": "轴系综合与机械原理", "二": "齿轮传动", "三": "蜗杆带链传动",
          "四": "轴承", "五": "螺纹键轴", "六": "联轴器平衡轮系"}
for p in sorted(glob.glob(os.path.join(SRC, "简答题", "常州大学855简答题*.pdf"))):
    name = os.path.basename(p)
    no_cn = re.search(r"简答题([一二三四五六])", name).group(1)
    d = fitz.open(p)
    txt = "\n".join(pg.get_text() for pg in d)
    for q in parse_numbered(txt):
        add(q["stem"], q["answer"], name, q["no"], source_label=f"简答专项训练（{no_cn}）·{labels[no_cn]}")

# 3) 简答汇编
p = os.path.join(SRC, "简答题", "常大简答题汇编（背诵精简版）.pdf")
d = fitz.open(p)
txt = "\n".join(pg.get_text() for pg in d)
for q in parse_numbered(txt):
    add(q["stem"], q["answer"], os.path.basename(p), q["no"], source_label="简答汇编（背诵精简版）")

# 4) 简答题（30题）docx
p = os.path.join(SRC, "简答题", "简答题（30题）.docx")
for q in parse_docx(p):
    add(q["stem"], q["answer"], os.path.basename(p), q["no"], source_label="简答题（30题）.docx")

print("raw ext", len(ext))

# 去重（同源/跨源近似题合并，保留更多来源和更长答案）
uniq = []
for e in ext:
    n = norm(e["text"])
    hit = None
    for u in uniq:
        # 选择题只在题干完全一致时合并，避免把选项不同的相似题误合并
        threshold = 1.0 if e["type"] == "选择" else 0.90
        if difflib.SequenceMatcher(None, n, u["_n"]).ratio() >= threshold:
            hit = u
            break
    if hit:
        for s in e["sources"]:
            if s not in hit["sources"]:
                hit["sources"].append(s)
        if len(e["answer"]) > len(hit["answer"]):
            hit["answer"] = e["answer"]
        if len(e.get("explanation") or "") > len(hit.get("explanation") or ""):
            hit["explanation"] = e["explanation"]
        if not hit["chapter"] and e["chapter"]:
            hit["chapter"] = e["chapter"]
        if not hit["subs"] and e["subs"]:
            hit["subs"] = e["subs"]
    else:
        e["_n"] = n
        uniq.append(e)
print("unique ext", len(uniq))

# 标注真题
t_sel = [q for q in QS if q["type"] == "选择"]
t_short = [q for q in QS if q["type"] == "简答"]
for q in t_sel + t_short:
    q["_n"] = norm(q["text"])

# 人工复核过的低相似度同题（只收录确认为同一道真题的条目）
MANUAL_EXAM = [
    ("当行程速比系数K", "2009-一-2"),
    ("渐开线标准直齿圆柱齿轮发生根切", "2018-一-2"),
    ("蜗杆传动的正确啮合条件", "2023-二-2"),
    ("什么是滚动轴承的基本额定寿命", "2014-二-4"),
]

review = []
for e in uniq:
    pool = t_sel if e["type"] == "选择" else t_short
    scored = sorted(((difflib.SequenceMatcher(None, e["_n"], q["_n"]).ratio(), q) for q in pool),
                    key=lambda x: x[0], reverse=True)
    best_r = scored[0][0] if scored else 0
    exam = []
    if best_r >= 0.80:
        cut = max(0.80, best_r - 0.02)
        for r, q in scored:
            if r < cut:
                break
            refs = q.get("alsoYears") or [{"year": q["year"], "section": q["section"], "num": q["num"]}]
            for ref in refs:
                item = {"year": ref["year"], "section": ref["section"], "num": ref.get("num", "")}
                if item not in exam:
                    exam.append(item)
    elif best_r >= 0.68:
        review.append({"stem": e["text"], "type": e["type"], "ratio": round(best_r, 3),
                       "candidate": scored[0][1]["id"], "candidate_text": scored[0][1]["text"]})
    if not exam:
        for kw, tid in MANUAL_EXAM:
            if kw in e["text"]:
                q = next(x for x in QS if x["id"] == tid)
                refs = q.get("alsoYears") or [{"year": q["year"], "section": q["section"], "num": q["num"]}]
                for ref in refs:
                    item = {"year": ref["year"], "section": ref["section"], "num": ref.get("num", "")}
                    if item not in exam:
                        exam.append(item)
                break
    exam.sort(key=lambda x: (x["year"], str(x["num"])))
    e["examRefs"] = exam
    e["isExam"] = bool(exam)
    e["bestRatio"] = round(best_r, 3)

# 编号、章节、输出
for i, e in enumerate(uniq, 1):
    e["id"] = f"EXT-{i:04d}"
    if e.get("chapter"):
        e["kp"] = [e["chapter"]]
    else:
        subs = e.get("subs") or []
        e["kp"] = list(dict.fromkeys(META_SUBS[s][1] for s in subs)) or ["A"]
    if not e.get("subs") and not e.get("chapter"):
        e["subs"] = guess_subs(e["text"])
    for k in ("_n", "chapter", "bestRatio"):
        e.pop(k, None)

meta = {
    "total": len(uniq),
    "examMatched": sum(1 for e in uniq if e["isExam"]),
    "byType": dict(collections.Counter(e["type"] for e in uniq)),
    "bySource": dict(collections.Counter(s["label"] for e in uniq for s in e["sources"])),
    "source": "青蛙弟弟选择题题库 + 简答专项训练（一至六）+ 简答汇编（背诵精简版）+ 简答题（30题）.docx",
    "note": "扩展题独立于真题题库；其中与真题相同的题目保留原样，并标注全部考过年份与原卷题号。",
}
OUT = {"meta": meta, "questions": uniq}
base = os.path.join(ROOT, "常大真题电子版", "web", "data")
json.dump(OUT, open(os.path.join(base, "ext.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(base, "ext.js"), "w", encoding="utf-8").write(
    "window.EXT = " + json.dumps(OUT, ensure_ascii=False, separators=(",", ":")) + ";\n")

# CSV
os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
with open(os.path.join(ROOT, "docs", "扩展题来源与真题标注清单.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["扩展题编号", "题型", "题干", "来源文件", "来源题号", "是否真题", "真题年份与原题号"])
    for e in uniq:
        w.writerow([
            e["id"], e["type"], e["text"][:180],
            "；".join(f'{s["file"]} 第{s["no"]}题' for s in e["sources"]),
            "；".join(str(s["no"]) for s in e["sources"]),
            "是" if e["isExam"] else "否",
            "；".join(f'{r["year"]} {r["section"]}第{r["num"]}题' for r in e["examRefs"]),
        ])

json.dump(review, open(os.path.join(ROOT, "_build", "ext_review.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("exam matched", meta["examMatched"], "review borderline", len(review))
print("by source", meta["bySource"])
print("by type", meta["byType"])
