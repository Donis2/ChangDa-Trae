# -*- coding: utf-8 -*-
"""合并 Trae 题库与 Workbuddy 题库：补齐 3 个卷面题，导入答案/解析/图片/多年份标注。"""
import json, os, re, sys, shutil, difflib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAE_DATA = os.path.join(ROOT, "常大真题电子版", "web", "data", "data.json")
WB_DATA = r"d:\Code\MyProject\常大真题\Workbuddy版本\data\questions.json"
WB_IMG = r"d:\Code\MyProject\常大真题\Workbuddy版本\public\images\questions"
OUT_JSON = os.path.join(ROOT, "常大真题电子版", "web", "data", "data.json")
FIGS_DIR = os.path.join(ROOT, "常大真题电子版", "web", "assets", "figs")

sys.path.insert(0, os.path.join(ROOT, "_build"))
import subrules

META_SUBS = {c: (n, ch) for c, n, ch, _ in subrules.SUBS}
SUB_RULES = {c: kw for c, n, ch, kw in subrules.SUBS}


def dedupe_refs(refs):
    out, seen = [], set()
    for r in refs:
        key = (r.get("year"), r.get("num"))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def norm(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "", s)
    return s.lower()


def guess_subs(text):
    scores = collections.Counter()
    for code, words in SUB_RULES.items():
        for w in words:
            n = text.count(w)
            if n:
                weight = 3 if len(w) >= 6 else (2 if len(w) >= 3 else 1)
                scores[code] += n * weight
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


TRAE = json.load(open(TRAE_DATA, encoding="utf-8"))
WB = json.load(open(WB_DATA, encoding="utf-8"))["questions"]
QS = TRAE["questions"]
for q in QS:
    q["_n"] = norm(q["text"])
for q in WB:
    q["_n"] = norm(q["stem"])

# 低相似度但确认为同一题的人工映射：Workbuddy id -> Trae id
MANUAL = {
    "2008-计算-01": "2008-三-1",
    "2008-计算-02": "2008-四-1",
    "2008-分析-01": "2008-五-1",
    "2008-分析-02": "2008-八-1",
    "2010-计算-06": "2010-三-6",
    "2011-计算-01": "2011-四-1",
    "2007-分析-01": "2007-二-3",
    "2007-分析-02": "2007-二-4",
    "2007-计算-01": "2007-二-1",
    "2007-计算-02": "2007-二-2",
    "2015-分析-03": "2015-五-1",
    "2017-分析-01": "2017-三-1",
    "2018-简答-01": "2018-二-1",
    "2026-综合-04": "2026-三-4",
    "2026-综合-06": "2026-三-7",
}
NEW_IDS = {"2017-简答-05"}

# 1) 匹配 Workbuddy -> Trae（按年份，允许跨题型组）
matches = {}       # wb id -> list[trae id]
unmatched = []
for w in WB:
    wid = w["id"]
    years = w.get("source_years") or [int(wid[:4])]
    if wid in NEW_IDS:
        continue
    if wid in MANUAL:
        matches[wid] = [MANUAL[wid]]
        continue
    found = []
    for y in years:
        pool = [t for t in QS if t["year"] == y]
        if not pool:
            continue
        scored = sorted(((difflib.SequenceMatcher(None, w["_n"], t["_n"]).ratio(), t) for t in pool),
                        key=lambda x: x[0], reverse=True)
        r, t = scored[0]
        if r >= 0.70:
            found.append(t["id"])
    if not found:
        unmatched.append(wid)
    else:
        matches[wid] = found
print("unmatched WB:", unmatched)

# 2) 补 2017-简答-05
w = next(x for x in WB if x["id"] == "2017-简答-05")
q = {
    "id": "2017-二-5",
    "year": 2017,
    "section": "二、简答题",
    "num": "5",
    "type": "简答",
    "text": w["stem"],
    "options": [],
    "marks": w.get("score") or 5,
    "figs": [],
    "kp": ["M"],
    "subs": guess_subs(norm(w["stem"])),
    "answer": w.get("answer"),
    "explanation": w.get("explanation"),
    "difficulty": w.get("difficulty"),
}
QS.append(q)
q["_n"] = norm(q["text"])

# 3) 补 2025 简答 1、2（与 2024 卷面同题）
for num, src_id in (("1", "2024-二-1"), ("2", "2024-二-2")):
    src = next(x for x in QS if x["id"] == src_id)
    copy = {k: (list(v) if isinstance(v, list) else v) for k, v in src.items() if not k.startswith("_")}
    copy.update({
        "id": f"2025-一-{num}", "year": 2025, "section": "一、简答题", "num": num,
        "type": "简答", "text": src["text"],
    })
    QS.append(copy)
    copy["_n"] = norm(copy["text"])

# 4) 把 Workbuddy 的答案/解析/标签/多年份标注导入 Trae
by_id = {t["id"]: t for t in QS}
for wid, tids in matches.items():
    w = next(x for x in WB if x["id"] == wid)
    for tid in tids:
        t = by_id.get(tid)
        if not t:
            continue
        # 多年份出现位置
        refs = []
        for y, desc in (w.get("original_numbers") or {}).items():
            m = re.search(r"第?(\d+)题", desc)
            refs.append({"year": int(y), "section": desc, "num": m.group(1) if m else ""})
        if refs:
            t["alsoYears"] = dedupe_refs(refs)
        # 答案/解析：Trae 缺失时补；解析优先选更长的 Workbuddy 版
        if w.get("answer") and not t.get("answer"):
            t["answer"] = w["answer"]
            t["answerSource"] = w.get("source") or "Workbuddy"
        if w.get("explanation"):
            if not t.get("explanation") or len(w["explanation"]) > len(t.get("explanation") or ""):
                t["explanation"] = w["explanation"]
                t["explainSource"] = "Workbuddy"
        for tag in (w.get("tags") or []):
            t.setdefault("tags", [])
            if tag not in t["tags"]:
                t["tags"].append(tag)
        if w.get("difficulty"):
            t.setdefault("difficulty", w["difficulty"])
        t["source"] = "真题"

# 2017 新题 + 2025 两题也要有 alsoYears
new_2017 = by_id["2017-二-5"]
new_2017["alsoYears"] = [{"year": 2017, "section": "二、简答题 第5题", "num": "5"}]
for tid in ("2025-一-1", "2025-一-2"):
    t = by_id[tid]
    ref_year = 2024 if tid.endswith("-1") else 2024
    src = by_id["2024-二-" + tid[-1]]
    refs = (src.get("alsoYears") or [{"year": 2024, "section": "二、简答题", "num": tid[-1]}]) + [
        {"year": 2025, "section": "一、简答题 第" + tid[-1] + "题", "num": tid[-1]}
    ]
    t["alsoYears"] = dedupe_refs(refs)

# 5) 复制 Workbuddy 题图/答案图（Trae 没有时才补）
os.makedirs(FIGS_DIR, exist_ok=True)
copied = 0
for w in WB:
    tid = None
    for t in (matches.get(w["id"]) or []):
        if t:
            tid = t
            break
    if not tid and w["id"] == "2017-简答-05":
        tid = "2017-二-5"
    if not tid:
        continue
    t = by_id.get(tid)
    if not t:
        continue
    if not t.get("figs") and w.get("images"):
        imgs = []
        for i, src in enumerate(w["images"]):
            name = os.path.basename(src)
            dst_name = "wb-" + re.sub(r"[^\w\-.]", "_", name)
            dst = os.path.join(FIGS_DIR, dst_name)
            if os.path.exists(os.path.join(WB_IMG, name)) and not os.path.exists(dst):
                shutil.copy2(os.path.join(WB_IMG, name), dst)
                copied += 1
            if os.path.exists(dst):
                imgs.append(dst_name)
        if imgs:
            t["figs"] = [{"key": "wb-" + tid, "images": imgs}]
    if not t.get("answerFigs") and w.get("answer_images"):
        imgs = []
        for src in w["answer_images"]:
            name = os.path.basename(src)
            dst_name = "wb-ans-" + re.sub(r"[^\w\-.]", "_", name)
            dst = os.path.join(FIGS_DIR, dst_name)
            if os.path.exists(os.path.join(WB_IMG, name)) and not os.path.exists(dst):
                shutil.copy2(os.path.join(WB_IMG, name), dst)
                copied += 1
            if os.path.exists(dst):
                imgs.append(dst_name)
        if imgs:
            t["answerFigs"] = imgs
print("copied images:", copied)

# 6) 重建 meta
CH_ORDER = [c["code"] for c in TRAE["meta"]["chapters"]]
qs_clean = [{k: v for k, v in q.items() if not k.startswith("_")} for q in QS]
qs_clean.sort(key=lambda q: (q["year"], CH_ORDER.index(q["kp"][0]) if q["kp"] else 99, str(q["num"])))
years = sorted({q["year"] for q in qs_clean})
years_meta = {}
for y in years:
    ys = [q for q in qs_clean if q["year"] == y]
    years_meta[str(y)] = {
        "count": len(ys),
        "marks": TRAE["meta"]["years"].get(str(y), {}).get("marks", 150),
        "sections": list(dict.fromkeys(q["section"] for q in ys)),
        "answers": [],  # 稍后由答案脚本填充双版本
        "paperSources": ["考研群资料版真题原卷", "Workbuddy 夸克扫描版真题"],
    }
TRAE["meta"]["years"] = years_meta
TRAE["meta"]["total"] = len(qs_clean)
TRAE["meta"]["withFigure"] = sum(1 for q in qs_clean if q.get("figs"))
TRAE["meta"]["counts"] = {
    "entries": len(qs_clean),
    "unique": len({q["id"] for q in qs_clean}),
    "choice": sum(1 for q in qs_clean if q["type"] == "选择"),
    "fill": sum(1 for q in qs_clean if q["type"] == "填空"),
    "judge": sum(1 for q in qs_clean if q["type"] == "判断"),
    "short": sum(1 for q in qs_clean if q["type"] == "简答"),
    "analysis": sum(1 for q in qs_clean if q["type"] == "分析"),
    "calc": sum(1 for q in qs_clean if q["type"] == "计算"),
    "structure": sum(1 for q in qs_clean if q["type"] == "结构"),
}
TRAE["meta"]["source"] = (
    "真题：21 套原卷（2004、2006—2015、2017—2026；2005、2016 缺卷）。"
    "Trae 版采用考研群公开资料扫描件（2004—2008 取自夸克扫描版），"
    "Workbuddy 版采用夸克扫描件；两版题干经逐题比对为同一套题。"
    "答案：老魏版（2009—2024）与考研群资料版（2009—2026）双版本。"
)
TRAE["meta"]["sourceNotes"] = [
    "2004—2008 年为江苏工业学院 455 机械设计 / 机械设计基础 A 卷，原卷未附答案",
    "2009—2012 年考研群资料版答案借用老魏版",
    "2017 年老魏版答案缺标题页",
    "2023、2025、2026 为回忆版，题量不完整；2026 答案原件仅含第 5—10 页",
]
TRAE["questions"] = qs_clean

json.dump(TRAE, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
js = "window.DATA = " + json.dumps(TRAE, ensure_ascii=False, separators=(",", ":")) + ";\n"
open(os.path.join(ROOT, "常大真题电子版", "web", "data", "data.js"), "w", encoding="utf-8").write(js)

print("total", len(qs_clean), "unique ids", len({q["id"] for q in qs_clean}))
print("types", collections.Counter(q["type"] for q in qs_clean))
print("years", dict(sorted(collections.Counter(q["year"] for q in qs_clean).items())))
print("answers", sum(1 for q in qs_clean if q.get("answer")),
      "explanations", sum(1 for q in qs_clean if q.get("explanation")),
      "figs", sum(1 for q in qs_clean if q.get("figs")))
print("missing answers by type", collections.Counter(q["type"] for q in qs_clean if not q.get("answer")))
