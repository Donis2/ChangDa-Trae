# -*- coding: utf-8 -*-
# 生成客观题题目册、答案册（选择 + 填空 + 判断），按章节排序、连续编号
import json, io, os, sys, datetime, collections
import fitz
from PIL import Image

BASE = r"d:\Code\MyProject\真题统计\常大真题电子版"
BUILD = r"d:\Code\MyProject\真题统计\_build"
sys.path.insert(0, BUILD)
import quizdata
import subrules

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

QBOOK = os.path.join(BASE, "常大855-客观题题目册.pdf")
ABOOK = os.path.join(BASE, "常大855-客观题答案册.pdf")

data = json.load(io.open(os.path.join(BASE, "web", "data", "data.json"), encoding="utf-8"))
CHS = data["meta"]["chapters"]
CH_NAME = {c["code"]: c["name"] for c in CHS}
CH_ORDER = [c["code"] for c in CHS]
SUBS = {s["code"]: s for s in data["meta"]["subs"]}
RAW = data["questions"]

CHOICE_FLAGS = {
    "2018-一-10": "已修正：原数据记为 B，复核选项图后改为 C。",
    "2019-一-8": "选项 C 文字疑为 OCR 误识（“λ≤α/2”不合常理），不影响答案 B。",
    "2018-一-3": "表述瑕疵：题干“小于”严格应为“小于或等于”，标准答案 A 仍成立。",
    "2013-一-5": "原卷手写答案为 D，按教材（刚度取决于 EI，增大轴径最有效）修正为 B。",
    "2017-一-4": "原卷手写答案为 A，按教材（接触强度取决于分度圆直径）修正为 B。",
    "2017-一-6": "原卷手写答案为 C，按教材（合金钢与热处理对刚度无实效）修正为 D。",
}


def letters(a):
    if isinstance(a, list):
        return "、".join("ABCD"[x] for x in a)
    return "ABCD"[a] if isinstance(a, int) else str(a)


# 组装：真题选择/填空/判断 + 补充选择题（按章节合并排序）
SUB_DEF = subrules.SUBS
SUB_MAP = {c: (n, ch) for c, n, ch, _ in SUB_DEF}
SUB_RULES = {c: kw for c, n, ch, kw in SUB_DEF}


def guess_subs(chapter, text):
    scores = collections.Counter()
    for code, words in SUB_RULES.items():
        if SUB_MAP[code][1] != chapter:
            continue
        for w in words:
            n = text.count(w)
            if n:
                scores[code] += n * (3 if len(w) >= 6 else (2 if len(w) >= 3 else 1))
    return [scores.most_common(1)[0][0]] if scores else []


items = []
for t in ("选择", "填空", "判断"):
    qs = [q for q in RAW if q["type"] == t]
    for q in qs:
        if t == "选择":
            item = quizdata.Q[q["id"]]
            ans = letters(item[0])
            expl = item[1]
            flag = CHOICE_FLAGS.get(q["id"]) or (item[2] if len(item) > 2 else None)
        else:
            ans = q["answer"]
            expl = q["explanation"]
            flag = q.get("reviewNote")
        items.append({
            "id": q["id"], "type": t, "year": q["year"], "marks": q.get("marks"),
            "chapter": q["kp"][0], "subs": q.get("subs", []), "source": "真题",
            "src_label": "真题 · %s 年 · %s 第 %s 题" % (q["year"], q["section"], q["num"]),
            "ord": int(q["num"]) if str(q["num"]).isdigit() else 0,
            "text": q["text"], "options": q.get("options", []), "figs": q.get("figs", []),
            "answer": ans, "explanation": expl, "flag": flag,
        })

# 并入青蛙弟弟补充选择题库（已校核、去重）
FROG = json.load(io.open(os.path.join(BUILD, "frog_integrated.json"), encoding="utf-8"))
for q in FROG:
    text = q["stem"] + " " + " ".join(q["options"])
    items.append({
        "id": "F%d" % q["src_no"], "type": "选择", "year": None, "marks": None,
        "chapter": q["chapter"], "subs": guess_subs(q["chapter"], text), "source": "补充题库",
        "src_label": "补充题库 · 原第 %d 题" % q["src_no"], "ord": q["src_no"],
        "text": q["stem"], "options": q["options"], "figs": [],
        "answer": q["answer"], "explanation": q["expl"], "flag": q.get("flag"),
    })

# 选择题按章节 → 二级知识点 → 真题优先 → 年份/原题号 排序，合并为一体
choice = [it for it in items if it["type"] == "选择"]
choice.sort(key=lambda it: (
    CH_ORDER.index(it["chapter"]),
    (it["subs"][0] if it["subs"] else "ZZ"),
    0 if it["source"] == "真题" else 1,
    it["year"] or 9999,
    it["ord"],
))
fill = [it for it in items if it["type"] == "填空"]
fill.sort(key=lambda it: (CH_ORDER.index(it["chapter"]), (it["subs"][0] if it["subs"] else "ZZ"),
                          it["year"], it["ord"]))
judge = [it for it in items if it["type"] == "判断"]
judge.sort(key=lambda it: (CH_ORDER.index(it["chapter"]), (it["subs"][0] if it["subs"] else "ZZ"),
                           it["year"], it["ord"]))
items = choice + fill + judge
for i, it in enumerate(items, 1):
    it["no"] = i

TYPES = [("选择", "一、选择题", "真题 + 补充题合并 · 按章节排序"),
         ("填空", "二、填空题", "在横线处填写正确内容"),
         ("判断", "三、判断题", "判断下列说法是否正确")]

NAVY = (0.114, 0.298, 0.388)
ACCENT = (0.722, 0.298, 0.200)
GRAY = (0.42, 0.47, 0.50)
INK = (0.13, 0.15, 0.16)
LINE = (0.86, 0.84, 0.80)
BAND = (0.93, 0.95, 0.96)

PW, PH = 595, 842
LEFT, RIGHT = 46, PW - 46
TOP, BOTTOM = 66, PH - 52
USABLE = RIGHT - LEFT
font_r = fitz.Font(fontfile=REG)
font_b = fitz.Font(fontfile=BOLD)


class R:
    def __init__(self, doc, header=True):
        self.doc = doc
        self.header = header
        self.page = None
        self.y = 0
        self.no = 1

    def new_page(self):
        self.page = self.doc.new_page(width=PW, height=PH)
        self.no += 1
        self.page.insert_font(fontname="r", fontfile=REG)
        self.page.insert_font(fontname="b", fontfile=BOLD)
        if self.header:
            self.page.insert_text((LEFT, 34), "常州大学 855 机械设计基础", fontname="r",
                                  fontsize=8.5, color=GRAY)
            t = "客观题 · 按章节专题排序"
            self.page.insert_text((RIGHT - font_r.text_length(t, 8.5), 34), t,
                                  fontname="r", fontsize=8.5, color=GRAY)
            self.page.draw_line(fitz.Point(LEFT, 42), fitz.Point(RIGHT, 42), color=LINE, width=.6)
        self.y = TOP

    def need(self, h):
        if self.y + h > BOTTOM:
            self.new_page()

    def put(self, x, s, size, font="r", color=INK):
        self.page.insert_text((x, self.y + size * 0.82), s, fontname=font,
                              fontsize=size, color=color)

    def wrap(self, text, width, size, font="r"):
        f = font_b if font == "b" else font_r
        out = []
        for raw in text.split("\n"):
            cur = ""
            for ch in raw:
                if f.text_length(cur + ch, size) <= width:
                    cur += ch
                else:
                    out.append(cur)
                    cur = ch
            out.append(cur)
        # 避免“。”“，”等标点独占一行；合并后不得超出给定宽度
        clean = []
        punct = "。，；、！？：）】》”’"
        for ln in out:
            if clean and (ln.strip() in punct or (ln and ln.lstrip()[:1] in punct)):
                cand = clean[-1] + ln
                if f.text_length(cand, size) <= width + 1.5:
                    clean[-1] = cand
                    continue
                prev = clean[-1]
                fixed = False
                for k in (1, 2, 3):
                    if len(prev) <= k:
                        break
                    np, nl = prev[:-k], prev[-k:] + ln
                    if f.text_length(np, size) <= width and f.text_length(nl, size) <= width:
                        clean[-1] = np
                        clean.append(nl)
                        fixed = True
                        break
                if not fixed:
                    clean.append(ln)
            else:
                clean.append(ln)
        return clean

    def para(self, text, size=10.5, font="r", color=INK, x=LEFT, width=USABLE,
             leading=1.62, first=0, rest=0):
        lines = self.wrap(text, width - max(first, rest), size, font)
        for i, ln in enumerate(lines):
            x0 = x + (first if i == 0 else rest)
            self.need(size * leading)
            self.put(x0, ln, size, font, color)
            self.y += size * leading

    def section(self, title, sub=""):
        self.need(42)
        self.y += 8
        rect = fitz.Rect(LEFT, self.y, RIGHT, self.y + 28)
        self.page.draw_rect(rect, color=None, fill=ACCENT, width=0)
        self.page.insert_text((LEFT + 10, self.y + 19), title, fontname="b",
                              fontsize=14, color=(1, 1, 1))
        if sub:
            tw = font_b.text_length(title, 14)
            self.page.insert_text((LEFT + 16 + tw, self.y + 18.5), sub, fontname="r",
                                  fontsize=9, color=(1, 0.92, 0.88))
        self.y += 36

    def chapter(self, code, name):
        self.need(36)
        self.y += 4
        rect = fitz.Rect(LEFT, self.y, RIGHT, self.y + 22)
        self.page.draw_rect(rect, color=None, fill=NAVY, width=0)
        self.page.insert_text((LEFT + 9, self.y + 15.5), f"{code}  {name}", fontname="b",
                              fontsize=12, color=(1, 1, 1))
        self.y += 30


def est_q(r, it, ty):
    body = it["text"] + ("（　）" if ty == "判断" else "")
    h = 19 + len(r.wrap(body, USABLE, 11.5)) * 19
    for j, o in enumerate(it["options"]):
        h += len(r.wrap("%s. %s" % ("ABCD"[j], o), USABLE - 26, 10.5)) * 16.3
    if it["figs"]:
        h += 238
    return h


def est_d(r, it):
    e_lines = len(r.wrap("解析：" + (it["explanation"] or ""), USABLE - 28, 10.3))
    f_lines = len(r.wrap("校对说明：" + it["flag"], USABLE - 28, 9.5)) if it["flag"] else 0
    return 18 + 17 + e_lines * 16.3 + (f_lines * 14.3 + 4 if f_lines else 0) + 16


def new_doc():
    return fitz.open()


def cover(doc, kind):
    total = len(items)
    n_choice = sum(1 for i in items if i["type"] in ("选择", "补充选择"))
    n_fill = sum(1 for i in items if i["type"] == "填空")
    n_judge = sum(1 for i in items if i["type"] == "判断")
    rng = {}
    for t in ("选择", "填空", "判断"):
        nos = [i["no"] for i in items if i["type"] == t]
        rng[t] = (min(nos), max(nos)) if nos else (0, 0)
    n_real = sum(1 for i in items if i["type"] == "选择" and i["source"] == "真题")
    n_extra = sum(1 for i in items if i["type"] == "选择" and i["source"] != "真题")
    page = doc.new_page(width=PW, height=PH)
    page.insert_font(fontname="r", fontfile=REG)
    page.insert_font(fontname="b", fontfile=BOLD)
    page.draw_rect(fitz.Rect(0, 0, PW, 250), color=None, fill=NAVY, width=0)
    page.insert_text((56, 92), "常州大学 855 机械设计基础", fontname="b", fontsize=26, color=(1, 1, 1))
    sub = "历年真题 · 客观题题目册" if kind == "q" else "历年真题 · 客观题答案册"
    page.insert_text((58, 132), sub, fontname="b", fontsize=18, color=(0.88, 0.92, 0.94))
    desc = ("真题客观题 + 青蛙弟弟补充题库 · 按章节专题排序 · 题号 1—%d 连续编号" % total if kind == "q"
            else "答案速查 + 逐题详解 · 与题目册题号一一对应")
    page.insert_text((58, 170), desc, fontname="r", fontsize=11, color=(0.86, 0.90, 0.92))
    page.draw_line(fitz.Point(56, 196), fitz.Point(539, 196), color=(0.55, 0.70, 0.76), width=1)

    stats = [(str(total), "客观题"), (str(n_choice), "选择题"), (str(n_fill), "填空题"), (str(n_judge), "判断题")]
    x = 56
    for num, lab in stats:
        page.draw_rect(fitz.Rect(x, 292, x + 112, 372), color=LINE, fill=(0.97, 0.97, 0.96), width=.8)
        page.insert_text((x + 14, 334), num, fontname="b", fontsize=24, color=NAVY)
        page.insert_text((x + 14, 356), lab, fontname="r", fontsize=10, color=GRAY)
        x += 124

    page.insert_text((56, 424), "使用说明", fontname="b", fontsize=13, color=NAVY)
    if kind == "q":
        notes = [
            "1. 真题与补充题已合并，统一按章节专题（A—O）排序，题号 1—%d 连续编号。" % total,
            "2. 选择题 %d—%d（真题 %d + 补充 %d）、填空 %d—%d、判断 %d—%d。"
            % (rng["选择"][0], rng["选择"][1], n_real, n_extra,
               rng["填空"][0], rng["填空"][1], rng["判断"][0], rng["判断"][1]),
            "3. 本册只含题目，不含答案；答案与解析见配套《客观题答案册》。",
            "4. 每题标注来源：真题注明年份与原题号，补充题注明原题库题号。",
            "5. 唯一一道含图填空题（2010-一-15）已附原卷机构简图。",
        ]
    else:
        notes = [
            "1. 第一部分为答案速查：选择题、填空题、判断题全部列出答案。",
            "2. 第二部分为逐题详解，答案与解析的题号同《题目册》完全一致。",
            "3. 真题部分已逐题核对；补充题库亦逐题核对，修正答案 1 处、选项/公式 3 处。",
            "4. 补充题 %d 道已并入各章节，不再单列；所有题目均有答案与解析。" % n_extra,
        ]
    yy = 452
    for n in notes:
        for ln in R(doc).wrap(n, 470, 10.5, "r"):
            page.insert_text((56, yy), ln, fontname="r", fontsize=10.5, color=INK)
            yy += 20
        yy += 4
    if kind == "a":
        page.draw_rect(fitz.Rect(56, yy + 10, 539, yy + 84), color=(0.85, 0.78, 0.64),
                       fill=(0.99, 0.97, 0.93), width=.8)
        page.insert_text((70, yy + 30), "真题部分：答案修正 1 处；原卷答案修正 3 处；选项疑点 1 处；表述瑕疵 1 处。",
                         fontname="b", fontsize=9, color=ACCENT)
        page.insert_text((70, yy + 48), "补充题库：第 207 题答案 D→A；第 138、204 题选项表述更正；第 229 题公式更正。",
                         fontname="b", fontsize=9, color=ACCENT)
        page.insert_text((70, yy + 66), "另：原库第 33 题与真题重复且答案有误（C→B），已去重；详见各题“校对说明”。",
                         fontname="r", fontsize=9, color=ACCENT)
    page.insert_text((56, PH - 46), "整理日期：%s" % datetime.date.today().isoformat(),
                     fontname="r", fontsize=9, color=GRAY)
    return page


# ==================== 题目册 ====================
def build_qbook():
    doc = new_doc()
    cover(doc, "q")
    r = R(doc)
    toc = [[1, "封面", 1]]
    r.new_page()
    toc.append([1, "题目（1—159）", r.no])
    r.para("说明：题目按“选择—填空—判断”分册编排，每类内按章节顺序排列，题号连续，与答案册一一对应。",
           size=10, color=GRAY)
    r.y += 4

    for ty, title, sub in TYPES:
        grp = [it for it in items if it["type"] == ty]
        r.section(title, "共 %d 题 · 题号 %d—%d" % (len(grp), grp[0]["no"], grp[-1]["no"]))
        cur_ch = None
        for it in grp:
            if it["chapter"] != cur_ch:
                cur_ch = it["chapter"]
                toc.append([2, "%s %s（%s）" % (ty, CH_NAME[cur_ch], title), r.no])
                r.need(min(30 + est_q(r, it, ty) + 18, 380))
                r.chapter(cur_ch, CH_NAME[cur_ch])
            sub_code = it["subs"][0] if it["subs"] else ""
            subtxt = ("%s %s" % (sub_code, SUBS.get(sub_code, {}).get("name", ""))).strip()
            r.need(min(est_q(r, it, ty) + 18, 360))
            r.put(LEFT, "%d." % it["no"], 12.5, "b", NAVY)
            if it["source"] == "补充题库":
                meta = it["src_label"]
            else:
                meta = it["src_label"] + ((" · " + subtxt) if subtxt else "")
            r.put(LEFT + 30, meta, 9, "r", GRAY)
            if isinstance(quizdata.Q.get(it["id"], (None,))[0], list):
                r.put(RIGHT - font_r.text_length("多选题", 9), "多选题", 9, "b", ACCENT)
            r.y += 19
            text = it["text"]
            if ty == "判断":
                text = text.rstrip() + "（　）"
            r.para(text, size=11.5, color=INK, leading=1.66)
            r.y += 3
            for j, o in enumerate(it["options"]):
                r.para("%s. %s" % ("ABCD"[j], o), size=10.5, first=16, rest=26,
                       leading=1.55, color=(0.20, 0.22, 0.24))
            for fg in it["figs"]:
                src = os.path.join(BASE, "web", "assets", "figs", fg["images"][0])
                if not os.path.exists(src):
                    continue
                iw, ih = Image.open(src).size
                sc = min(260 / iw, 210 / ih)
                w, h = iw * sc, ih * sc
                r.need(h + 28)
                box = fitz.Rect(LEFT + (USABLE - w) / 2, r.y + 6, LEFT + (USABLE + w) / 2, r.y + 6 + h)
                r.page.insert_image(box, filename=src, keep_proportion=True)
                r.y = box.y1 + 3
                cap = "原卷图"
                r.put(LEFT + (USABLE - font_r.text_length(cap, 8.5)) / 2, cap, 8.5, "r", GRAY)
                r.y += 14
            r.y += 10
            r.need(8)
            r.page.draw_line(fitz.Point(LEFT, r.y), fitz.Point(RIGHT, r.y),
                             color=(0.92, 0.91, 0.88), width=.5)
            r.y += 8

    add_pagenums(doc, font_r)
    doc.set_toc(toc)
    doc.set_metadata({"title": "常州大学 855 机械设计基础 · 客观题题目册（选择+填空+判断）",
                      "author": "855 真题题库整理", "subject": "159 道客观题，按章节专题排序"})
    doc.subset_fonts()
    doc.save(QBOOK, garbage=4, deflate=True)
    doc.close()
    return QBOOK


# ==================== 答案册 ====================
def build_abook():
    doc = new_doc()
    cover(doc, "a")
    r = R(doc)
    toc = [[1, "封面", 1]]

    # ---- 答案速查 ----
    r.new_page()
    toc.append([1, "答案速查", r.no])
    r.para("说明：先在此核对选项或答案，再看后文逐题详解。", size=10, color=GRAY)
    r.y += 4

    # 选择题
    choice = [it for it in items if it["type"] == "选择"]
    r.section("一、选择题答案", "题号 %d—%d" % (choice[0]["no"], choice[-1]["no"]))
    PAIRS = 9
    cellw = USABLE / PAIRS
    cur_ch = None
    col = 0
    for it in choice:
        if it["chapter"] != cur_ch:
            if col > 0:
                r.y += 15
                col = 0
            if cur_ch is not None:
                r.y += 3
            cur_ch = it["chapter"]
            r.need(24)
            rect = fitz.Rect(LEFT, r.y, RIGHT, r.y + 18)
            r.page.draw_rect(rect, color=None, fill=BAND, width=0)
            r.page.insert_text((LEFT + 7, r.y + 13), "%s  %s" % (cur_ch, CH_NAME[cur_ch]),
                               fontname="b", fontsize=10.5, color=NAVY)
            r.y += 23
        if col >= PAIRS:
            col = 0
            r.y += 15
        r.need(16)
        cx = LEFT + col * cellw
        r.page.insert_text((cx + 4, r.y + 12), "%d" % it["no"], fontname="r", fontsize=10, color=GRAY)
        r.page.insert_text((cx + 27, r.y + 12), it["answer"], fontname="b", fontsize=10.5, color=ACCENT)
        col += 1
        if col >= PAIRS:
            r.y += 15
            col = 0
    if col:
        r.y += 18

    # 填空题
    fill = [it for it in items if it["type"] == "填空"]
    r.section("二、填空题答案", "题号 %d—%d" % (fill[0]["no"], fill[-1]["no"]))
    for it in fill:
        lines = r.wrap(it["answer"], USABLE - 34, 9.6, "r")
        h = max(18, len(lines) * 13.5 + 5)
        r.need(h)
        r.page.insert_text((LEFT + 2, r.y + 12), "%d" % it["no"], fontname="r", fontsize=10, color=GRAY)
        yy = r.y + 12
        for ln in lines:
            r.page.insert_text((LEFT + 30, yy), ln, fontname="r", fontsize=9.6, color=INK)
            yy += 13.5
        r.y += h
        r.page.draw_line(fitz.Point(LEFT, r.y), fitz.Point(RIGHT, r.y),
                         color=(0.93, 0.92, 0.89), width=.5)
        r.y += 3

    # 判断题
    judge = [it for it in items if it["type"] == "判断"]
    r.section("三、判断题答案", "题号 %d—%d" % (judge[0]["no"], judge[-1]["no"]))
    cur_ch = None
    col = 0
    for it in judge:
        if it["chapter"] != cur_ch:
            if col > 0:
                r.y += 15
                col = 0
            if cur_ch is not None:
                r.y += 3
            cur_ch = it["chapter"]
            r.need(24)
            rect = fitz.Rect(LEFT, r.y, RIGHT, r.y + 18)
            r.page.draw_rect(rect, color=None, fill=BAND, width=0)
            r.page.insert_text((LEFT + 7, r.y + 13), "%s  %s" % (cur_ch, CH_NAME[cur_ch]),
                               fontname="b", fontsize=10.5, color=NAVY)
            r.y += 23
        if col >= PAIRS:
            col = 0
            r.y += 15
        r.need(16)
        cx = LEFT + col * cellw
        r.page.insert_text((cx + 4, r.y + 12), "%d" % it["no"], fontname="r", fontsize=10, color=GRAY)
        r.page.insert_text((cx + 30, r.y + 12), it["answer"], fontname="b", fontsize=10.5, color=ACCENT)
        col += 1
        if col >= PAIRS:
            r.y += 15
            col = 0
    if col:
        r.y += 20

    # ---- 详细解答 ----
    r.new_page()
    toc.append([1, "详细解答", r.no])
    r.para("说明：逐题给出答案与解析；带“校对说明”的题目为核对中发现的问题。", size=10, color=GRAY)
    r.y += 4

    for ty, title, _ in TYPES:
        grp = [it for it in items if it["type"] == ty]
        r.section(title + "详解", "题号 %d—%d" % (grp[0]["no"], grp[-1]["no"]))
        cur_ch = None
        for it in grp:
            if it["chapter"] != cur_ch:
                cur_ch = it["chapter"]
                r.need(min(20 + est_d(r, it) + 10, 380))
                r.y += 4
                r.put(LEFT, "%s  %s" % (cur_ch, CH_NAME[cur_ch]), 11.5, "b", NAVY)
                r.y += 6
                r.page.draw_line(fitz.Point(LEFT, r.y), fitz.Point(RIGHT, r.y),
                                 color=(0.80, 0.86, 0.89), width=.8)
                r.y += 10
            sub_code = it["subs"][0] if it["subs"] else ""
            r.need(min(est_d(r, it), 360))
            r.put(LEFT, "%d." % it["no"], 12, "b", NAVY)
            if it["source"] == "补充题库":
                meta = it["src_label"]
            else:
                meta = it["src_label"] + ((" · " + sub_code + " " + SUBS.get(sub_code, {}).get("name", "")) if sub_code else "")
            r.put(LEFT + 28, meta, 8.8, "r", GRAY)
            r.y += 18
            label = "答案：" if ty != "判断" else "答案："
            r.put(LEFT + 28, label + it["answer"], 11, "b", ACCENT)
            r.y += 17
            r.para("解析：" + (it["explanation"] or "（暂无解析）"), size=10.3, x=LEFT + 28,
                   width=USABLE - 28, leading=1.58, color=(0.20, 0.22, 0.24))
            if it["flag"]:
                r.y += 3
                r.para("校对说明：" + it["flag"], size=9.5, x=LEFT + 28, width=USABLE - 28,
                       leading=1.5, color=ACCENT)
            r.y += 4
            r.need(12)
            r.page.draw_line(fitz.Point(LEFT, r.y), fitz.Point(RIGHT, r.y),
                             color=(0.92, 0.91, 0.88), width=.5)
            r.y += 9

    add_pagenums(doc, font_r)
    doc.set_toc(toc)
    doc.set_metadata({"title": "常州大学 855 机械设计基础 · 客观题答案册（速查+详解）",
                      "author": "855 真题题库整理", "subject": "159 道客观题的答案速查与逐题详解"})
    doc.subset_fonts()
    doc.save(ABOOK, garbage=4, deflate=True)
    doc.close()
    return ABOOK


def add_pagenums(doc, f):
    total = doc.page_count
    for i in range(1, total):
        txt = "第 %d 页 / 共 %d 页" % (i + 1, total)
        doc[i].insert_text((PW / 2 - f.text_length(txt, 8.5) / 2, PH - 26), txt,
                           fontname="r", fontsize=8.5, color=GRAY)


if __name__ == "__main__":
    p1 = build_qbook()
    p2 = build_abook()
    for p in (p1, p2):
        d = fitz.open(p)
        print("saved:", p, "pages:", d.page_count, "MB:", round(os.path.getsize(p) / 1048576, 2))
        d.close()
