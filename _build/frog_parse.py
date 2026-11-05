# -*- coding: utf-8 -*-
import json, io, re, os, difflib
import fitz

BASE = r"d:\Code\MyProject\真题统计\常大真题电子版"
BUILD = r"d:\Code\MyProject\真题统计\_build"
SRC = os.path.join(BASE, "原始资料", "题库来源", "常大855-青蛙弟弟选择题题库.pdf")

d = fitz.open(SRC)
qtxt = []
for i in range(1, 13):
    qtxt.append(d[i].get_text())
atxt = []
for i in range(13, d.page_count):
    atxt.append(d[i].get_text())

Q_RAW = "\n".join(qtxt)
A_RAW = "\n".join(atxt)

SEC_MAP = {
    "一、机械设计总论与机械零件设计": "A",
    "二、平面机构与自由度": "B",
    "三、凸轮机构": "D",
    "四、齿轮机构与齿轮传动": "E",
    "五、蜗杆传动": "E",
    "六、轮系": "F",
    "七、螺纹联接与螺旋传动": "I",
    "八、键、花键、销联接": "J",
    "九、带传动": "G",
    "十、链传动": "H",
    "十一、轴的设计": "K",
    "十二、滚动轴承": "L",
    "十三、滑动轴承": "M",
    "十四、联轴器与离合器": "N",
    "十五、弹簧与其他": "O",
}
SEC_NAME = {k[2:]: v for k, v in SEC_MAP.items()}


def clean(s):
    s = s.replace("青蛙弟弟出版", "")
    s = re.sub(r"===== PAGE \d+ =====", "", s)
    return s


# 题目部分
qtext = clean(Q_RAW)
lines = [l.strip() for l in qtext.split("\n") if l.strip()]
# 重组行，保留题号与板块
merged = []
for l in lines:
    if re.match(r"^[一二三四五六七八九十]+、", l) or re.match(r"^\d+\.\s", l):
        merged.append(l)
    else:
        if merged:
            merged[-1] += " " + l
        else:
            merged.append(l)
blocks = []
cur_sec = None
for l in merged:
    m = re.match(r"^([一二三四五六七八九十]+)、(.*)$", l)
    if m and l in SEC_MAP:
        cur_sec = l
        continue
    m = re.match(r"^(\d+)\.\s*(.*)$", l)
    if m:
        blocks.append({"no": int(m.group(1)), "section": cur_sec, "body": m.group(2)})

# 选项解析
LBL = re.compile(r"([ABCD])\.\s*")
qs = []
bad = []
for b in blocks:
    body = b["body"]
    ms = list(LBL.finditer(body))
    if len(ms) != 4:
        bad.append((b["no"], len(ms), body[:80]))
        continue
    stem = body[:ms[0].start()].strip()
    opts = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i < 3 else len(body)
        opts.append(body[m.end():end].strip())
    qs.append({"src_no": b["no"], "section": b["section"], "stem": stem, "options": opts})

# 答案部分
atext = clean(A_RAW)
alines = [l.strip() for l in atext.split("\n") if l.strip()]
amerged = []
for l in alines:
    if re.match(r"^\d+\.\s*", l):
        amerged.append(l)
    elif amerged and not l.startswith("第二部分"):
        amerged[-1] += " " + l
answers = {}
abad = []
for l in amerged:
    m = re.match(r"^(\d+)\.\s*([ABCD]+)(.*)$", l)
    if not m:
        abad.append(l[:60])
        continue
    answers[int(m.group(1))] = {"letters": m.group(2), "expl": m.group(3).strip()}

for q in qs:
    a = answers.get(q["src_no"], {"letters": "", "expl": ""})
    q["answer"] = a["letters"]
    q["expl"] = a["expl"]
    q["chapter"] = SEC_MAP.get(q["section"], "X")

print("questions", len(qs), "blocks", len(blocks))
print("bad blocks", bad)
print("answers", len(answers), "abad", abad)
print("missing answer", [q["src_no"] for q in qs if not q["answer"]])
dist = {}
for q in qs:
    dist[q["answer"]] = dist.get(q["answer"], 0) + 1
print("answer letters", dist)

json.dump({"questions": qs, "answers": answers},
          io.open(os.path.join(BUILD, "frog_parsed.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 参考项目已有 92 题，用于查重对比
data = json.load(io.open(os.path.join(BASE, "web", "data", "data.json"), encoding="utf-8"))
import sys
sys.path.insert(0, BUILD)
import quizdata

def norm(s):
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"（\s*）|\(　\)|____|___", "", s)
    s = re.sub(r"[，。；：、？！,.;:?!（）()“”\"'《》]", "", s)
    return s

old = []
for q in data["questions"]:
    if q["type"] == "选择":
        old.append((q["id"], norm(q["text"]), quizdata.Q[q["id"]]))

sims = []
for q in qs:
    nq = norm(q["stem"])
    best = None
    for oid, ot, oa in old:
        r = difflib.SequenceMatcher(None, nq, ot).ratio()
        if best is None or r > best[2]:
            best = (oid, ot, r, oa)
    q["match_id"], q["match_sim"] = best[0], round(best[2], 3)
    q["match_old_ans"] = best[3]
    sims.append((q["src_no"], best[2], q["answer"], best[0], best[3]))

print("\n高相似（>=0.80）与答案不一致：")
for no, r, a, oid, oa in sims:
    if r >= 0.80:
        old_ans = "、".join("ABCD"[x] for x in oa[0]) if isinstance(oa[0], list) else "ABCD"[oa[0]]
        if a != old_ans:
            print(no, a, "vs", oid, old_ans, round(r, 2))
