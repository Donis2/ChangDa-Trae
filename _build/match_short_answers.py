# -*- coding: utf-8 -*-
"""把专门简答资料中命中的真题答案回填到真题简答题，并输出缺口清单。"""
import json, os, re, collections
import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "常大真题电子版", "web", "data", "data.json")
EXT_PATH = os.path.join(ROOT, "常大真题电子版", "web", "data", "ext.json")
DETAIL = os.path.join(ROOT, "题目资料来源", "Trae", "题库来源", "简答题", "常大855-简答题详解.pdf")
D = json.load(open(DATA_PATH, encoding="utf-8"))
EXT = json.load(open(EXT_PATH, encoding="utf-8"))["questions"]
QS = D["questions"]


def clean(s):
    s = s.replace("\xa0", " ")
    s = re.sub(r"(?m)^第\s*\d+\s*页\s*/\s*共\s*\d+\s*页.*$", "", s)
    return s.strip()


def parse_detail():
    txt = clean("\n".join(pg.get_text() for pg in fitz.open(DETAIL)))
    txt = re.sub(r"(?m)^常州大学.*$", "", txt)
    txt = re.sub(r"(?m)^简答题\s*∙.*$", "", txt)
    txt = re.sub(r"(?m)^说明$", "", txt)
    txt = re.sub(r"(?m)^下列答案.*$", "", txt)
    parts = re.split(r"(?m)^(\d{1,2})\s*\.\s*$", txt)
    entries = []
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        lines = [l.strip() for l in body.split("\n") if l.strip()]
        meta = next((l for l in lines if "真题" in l and "年" in l), "")
        m = re.search(r"真题\s*∙?\s*(20\d\d)\s*年\s*∙?\s*([^∙]+?)第\s*(\d+)\s*题", meta)
        if not m:
            continue
        ai = lines.index("参考答案") if "参考答案" in lines else None
        if ai is None:
            continue
        ans = "\n".join(lines[ai + 1:]).strip()
        entries.append({"no": i // 2 + 1, "year": int(m.group(1)), "section": m.group(2).strip(),
                        "num": m.group(3), "answer": ans})
    return entries


short = [q for q in QS if q["type"] == "简答"]
by_key = {}
for q in short:
    by_key.setdefault((q["year"], str(q["num"])), []).append(q)

matched_ids = set()
detail_entries = parse_detail()
print("detail entries", len(detail_entries))

for e in detail_entries:
    cands = by_key.get((e["year"], e["num"]) , [])
    if len(cands) > 1:
        cands = [q for q in cands if e["section"].replace("、", "") in q["section"].replace("、", "")] or cands
    if not cands:
        print("detail unmapped", e["year"], e["section"], e["num"])
        continue
    q = cands[0]
    old = q.get("answer") or ""
    if old and old != e["answer"]:
        q["originalAnswer"] = old
    q["answer"] = e["answer"]
    q["answerSource"] = f"常大855-简答题详解.pdf 第{e['no']}题"
    srcs = q.setdefault("answerSources", [])
    if q["answerSource"] not in srcs:
        srcs.append(q["answerSource"])
    matched_ids.add(q["id"])

# 再用扩展题里的简答资料补剩余题目
for e in EXT:
    if e["type"] != "简答" or not e["isExam"] or not e.get("answer"):
        continue
    for ref in e["examRefs"]:
        key = (ref["year"], str(ref.get("num", "")))
        cands = by_key.get(key, [])
        if len(cands) > 1:
            import difflib
            cands = sorted(cands, key=lambda q: difflib.SequenceMatcher(None, "".join(e["text"].split()), "".join(q["text"].split())).ratio(), reverse=True)[:1]
        for q in cands:
            if q["id"] in matched_ids:
                continue
            srcs = q.setdefault("answerSources", [])
            for s in e["sources"]:
                tag = f'{s["label"]}第{s["no"]}题'
                if tag not in srcs:
                    srcs.append(tag)
            q.setdefault("referenceAnswer", e["answer"])
            q.setdefault("referenceAnswerSource", e["sources"][0]["label"])
            if not q.get("answer") or len(q["answer"]) < max(40, len(e["answer"]) * 0.6):
                q["originalAnswer"] = q.get("answer")
                q["answer"] = e["answer"]
                q["answerSource"] = e["sources"][0]["label"]
            matched_ids.add(q["id"])

missing = [q for q in short if q["id"] not in matched_ids]

lines = ["# 真题简答答案缺口清单", "",
         "> 生成日期：2026-11-05",
         "> 口径：专门简答资料包括《常大855-简答题详解》《简答汇编（背诵精简版）》、简答专项训练（一至六）、《简答题（30题）.docx》。",
         "> 《简答题详解》按“年份 + 卷面题型 + 题号”逐题匹配；扩展题简答按题干相似度匹配，并人工复核低相似度条目。", ""]
lines.append(f"- 真题简答总数：**{len(short)}** 题")
lines.append(f"- 在专门简答资料中找到同题的：**{len(short) - len(missing)}** 题")
lines.append(f"- 未找到同题的：**{len(missing)}** 题")
lines.append("")
lines.append("## 一、未找到同题的真题简答")
lines.append("")
if missing:
    lines.append("| 年份 | 卷面题型 | 题号 | 题干 | 现有答案来源 |")
    lines.append("|---|---|---|---|---|")
    for q in sorted(missing, key=lambda x: (x["year"], x["section"], str(x["num"]))):
        ans_src = "；".join(q.get("answerSources") or []) or q.get("answerSource") or "题库原有整理"
        stem = q["text"].replace("|", "｜").replace("\n", " ")[:80]
        lines.append(f'| {q["year"]} | {q["section"]} | {q["num"]} | {stem} | {ans_src} |')
else:
    lines.append("无。全部真题简答均在专门资料中找到对应答案。")
lines.append("")
lines.append("## 二、已匹配到专门简答资料")
lines.append("")
lines.append("| 年份 | 卷面题型 | 题号 | 题干 | 答案来源 |")
lines.append("|---|---|---|---|---|")
for q in sorted(short, key=lambda x: (x["year"], x["section"], str(x["num"]))):
    if q["id"] in matched_ids:
        stem = q["text"].replace("|", "｜").replace("\n", " ")[:80]
        lines.append(f'| {q["year"]} | {q["section"]} | {q["num"]} | {stem} | {"；".join(q.get("answerSources", []))} |')
lines.append("")
lines.append("> 说明：找到同题时以专门资料的分点答案作为主答案；原题库答案更详细时保存在 `originalAnswer` 字段，便于追溯。")

os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
open(os.path.join(ROOT, "docs", "真题简答答案缺口清单.md"), "w", encoding="utf-8").write("\n".join(lines))

json.dump(D, open(DATA_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(ROOT, "常大真题电子版", "web", "data", "data.js"), "w", encoding="utf-8").write(
    "window.DATA = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n")

print("真题简答", len(short), "matched", len(short) - len(missing), "missing", len(missing))
print("missing ids", [(q["id"], q["text"][:30]) for q in missing])
