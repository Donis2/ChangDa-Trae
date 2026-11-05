# -*- coding: utf-8 -*-
# 整理青蛙题库：校核修正、去重、编号
import json, io, re, difflib, sys
sys.path.insert(0, r"d:\Code\MyProject\真题统计\_build")
import quizdata

BASE = r"d:\Code\MyProject\真题统计\常大真题电子版"
BUILD = r"d:\Code\MyProject\真题统计\_build"

parsed = json.load(io.open(BUILD + r"\frog_parsed.json", encoding="utf-8"))
qs = parsed["questions"]
data = json.load(io.open(BASE + r"\web\data\data.json", encoding="utf-8"))


def norm(s):
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"（\s*）|\(　\)|____|___", "", s)
    return re.sub(r"[，。；：、？！,.;:?!（）()“”\"'《》]", "", s)


old = []
for q in data["questions"]:
    if q["type"] == "选择":
        old.append({"id": q["id"], "stem": q["text"], "ans": quizdata.Q[q["id"]][0]})

# 校核修正
FIX = {
    138: {
        "options": ["轻载联接", "传递大转矩的场合（对中性较差）", "轴向滑动", "高速联接"],
        "answer": "B",
        "flag": "选项表述已更正：切向键适用于传递大转矩，但对中性较差，原“对中要求高”不准确。",
    },
    204: {
        "options": ["背对背布置（反装）", "面对面布置（正装）", "任意", "与外载荷无关"],
        "answer": "A",
        "flag": "选项术语已按标准更正：正装=面对面，反装=背对背；背对背支承刚度较大，故选 A。",
    },
    207: {
        "answer": "A",
        "expl": "滑动轴承径向尺寸小、轴向尺寸大，轴向尺寸小的场合更宜采用滚动轴承，故 A 不适宜；高精度、低速场合可用滑动轴承。",
        "flag": "原答案 D 有误，已改为 A：滑动轴承轴向尺寸较大，不适宜轴向尺寸小的场合。",
    },
    229: {
        "expl": "圆柱螺旋压缩弹簧刚度 F'=Gd⁴/(8D³n)，与簧丝直径、中径、圈数及材料有关。",
        "flag": "解析中的刚度公式已按教材更正为 F'=Gd⁴/(8D³n)。",
    },
}

for q in qs:
    f = FIX.get(q["src_no"])
    if f:
        if "options" in f:
            q["options"] = f["options"]
        if "answer" in f:
            q["answer"] = f["answer"]
        if "expl" in f:
            q["expl"] = f["expl"]
        q["flag"] = f.get("flag")

# 跨库去重
skip = set()
for q in qs:
    nq = norm(q["stem"])
    best = 0
    for o in old:
        r = difflib.SequenceMatcher(None, nq, norm(o["stem"])).ratio()
        if r > best:
            best = r
    if best >= 0.90:
        skip.add(q["src_no"])
        q["dup_old"] = round(best, 3)

# 库内去重
used = set()
for i, q in enumerate(qs):
    if q["src_no"] in skip or i in used:
        continue
    used.add(i)
    for j in range(i + 1, len(qs)):
        if j in used or qs[j]["src_no"] in skip:
            continue
        if difflib.SequenceMatcher(None, norm(q["stem"]), norm(qs[j]["stem"])).ratio() >= 0.92:
            used.add(j)
            skip.add(qs[j]["src_no"])
            qs[j]["dup_in"] = q["src_no"]

kept = [q for q in qs if q["src_no"] not in skip]
chapter_order = [c["code"] for c in data["meta"]["chapters"]]
kept.sort(key=lambda q: (chapter_order.index(q["chapter"]), q["src_no"]))

for i, q in enumerate(kept, 160):
    q["no"] = i
    q["source"] = "青蛙题库"
    q["type"] = "补充选择"

json.dump(kept, io.open(BUILD + r"\frog_integrated.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("kept", len(kept), "skipped", len(skip), "range", kept[0]["no"], kept[-1]["no"])
print("cross-dups", sum(1 for q in qs if "dup_old" in q), "internal-dups", sum(1 for q in qs if "dup_in" in q))
print("fixes", [q["src_no"] for q in kept if q.get("flag")])
