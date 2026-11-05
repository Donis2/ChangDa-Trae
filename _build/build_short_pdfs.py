# -*- coding: utf-8 -*-
# 生成简答题两册：详细版 + 记忆压缩包版
import json, io, os, sys, datetime, re
import fitz

BASE = r"d:\Code\MyProject\真题统计\常大真题电子版"
BUILD = r"d:\Code\MyProject\真题统计\_build"
sys.path.insert(0, BUILD)
import short_qa

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
PDF_FULL = os.path.join(BASE, "常大855-简答题详解.pdf")
PDF_MEM = os.path.join(BASE, "常大855-简答题记忆版.pdf")

data = json.load(io.open(os.path.join(BASE, "web", "data", "data.json"), encoding="utf-8"))
CHS = data["meta"]["chapters"]
CH_NAME = {c["code"]: c["name"] for c in CHS}
CH_ORDER = [c["code"] for c in CHS]
SUBS = {s["code"]: s for s in data["meta"]["subs"]}
QS = [q for q in data["questions"] if q["type"] == "简答"]
QS.sort(key=lambda q: (CH_ORDER.index(q["kp"][0]), (q["subs"][0] if q["subs"] else "ZZ"),
                       q["year"], int(q["num"]) if str(q["num"]).isdigit() else 0))

NAVY = (0.114, 0.298, 0.388)
ACCENT = (0.722, 0.298, 0.200)
GRAY = (0.42, 0.47, 0.50)
INK = (0.13, 0.15, 0.16)
LINE = (0.86, 0.84, 0.80)
PW, PH = 595, 842
LEFT, RIGHT = 46, PW - 46
TOP, BOTTOM = 66, PH - 52
USABLE = RIGHT - LEFT
font_r = fitz.Font(fontfile=REG)
font_b = fitz.Font(fontfile=BOLD)



def topic_of(q):
    """取答案分点与记忆链：优先用 short_qa 的知识主题，其次用题目自带的文字答案"""
    if q["id"] in short_qa.MAP:
        t = short_qa.TOPICS[short_qa.MAP[q["id"]]]
        return t["points"], t["memory"]
    pts = []
    for line in (q.get("answer") or "").split("\n"):
        line = line.strip()
        if not line:
            continue
        pts.append(re.sub(r"^[（(][0-9一二三四五六][）)]\s*", "", line))
    if not pts:
        pts = ["（本题原卷未附答案，详见教材相应章节）"]
    # 记忆链：按分号/逗号切出要点首句，最多 5 段，每段不超过 16 字
    chain = []
    for line in pts:
        for seg in line.split("；"):
            seg = seg.strip()
            if not seg:
                continue
            head, sep, rest = seg.partition("：")
            if sep and len(head) <= 8:
                clause = re.split(r"[，。、]", rest)[0]
                item = head + "—" + clause
            else:
                item = re.split(r"[：，。、]", seg)[0]
            item = re.sub(r"（[^）]*$", "", item).strip()
            item = item.rstrip("、，。；")
            if len(item) > 18:
                item = item[:18]
            if item and item not in chain:
                chain.append(item)
    return pts, " → ".join(chain[:5])


class R:
    def __init__(self, doc, header):
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
            self.page.insert_text((LEFT, 34), "常州大学 855 机械设计基础", fontname="r", fontsize=8.5, color=GRAY)
            t = "简答题 · 按章节知识排序"
            self.page.insert_text((RIGHT - font_r.text_length(t, 8.5), 34), t, fontname="r", fontsize=8.5, color=GRAY)
            self.page.draw_line(fitz.Point(LEFT, 42), fitz.Point(RIGHT, 42), color=LINE, width=.6)
        self.y = TOP

    def need(self, h):
        if self.y + h > BOTTOM:
            self.new_page()

    def put(self, x, s, size, font="r", color=INK):
        self.page.insert_text((x, self.y + size * 0.82), s, fontname=font, fontsize=size, color=color)

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
        return out

    def chapter(self, code, name):
        self.need(38)
        self.y += 6
        rect = fitz.Rect(LEFT, self.y, RIGHT, self.y + 24)
        self.page.draw_rect(rect, color=None, fill=NAVY, width=0)
        self.page.insert_text((LEFT + 9, self.y + 17), "%s  %s" % (code, name), fontname="b",
                              fontsize=12.5, color=(1, 1, 1))
        self.y += 32


def cover(doc, kind):
    page = doc.new_page(width=PW, height=PH)
    page.insert_font(fontname="r", fontfile=REG)
    page.insert_font(fontname="b", fontfile=BOLD)
    page.draw_rect(fitz.Rect(0, 0, PW, 250), color=None, fill=NAVY, width=0)
    page.insert_text((56, 92), "常州大学 855 机械设计基础", fontname="b", fontsize=26, color=(1, 1, 1))
    sub = "简答题详解 · 按章节知识排序" if kind == "full" else "简答题记忆压缩包 · 按章节知识排序"
    page.insert_text((58, 132), sub, fontname="b", fontsize=17, color=(0.88, 0.92, 0.94))
    desc = ("逐题分点作答 · 可直接用于考试答题" if kind == "full"
            else "关键词链 + 展开点数 · 看提示即可还原完整答案")
    page.insert_text((58, 170), desc, fontname="r", fontsize=11, color=(0.86, 0.90, 0.92))
    page.draw_line(fitz.Point(56, 196), fitz.Point(539, 196), color=(0.55, 0.70, 0.76), width=1)

    years = len(set(q["year"] for q in QS))
    chs = len(set(q["kp"][0] for q in QS))
    stats = [(str(len(QS)), "简答题"), (str(years), "覆盖年份"), (str(chs), "章节"),
             (str(len(set(short_qa.MAP.values()))), "知识主题")]
    x = 56
    for num, lab in stats:
        page.draw_rect(fitz.Rect(x, 286, x + 112, 366), color=LINE, fill=(0.97, 0.97, 0.96), width=.8)
        page.insert_text((x + 14, 328), num, fontname="b", fontsize=24, color=NAVY)
        page.insert_text((x + 14, 350), lab, fontname="r", fontsize=10, color=GRAY)
        x += 124

    page.insert_text((56, 414), "使用说明", fontname="b", fontsize=13, color=NAVY)
    if kind == "full":
        notes = [
            "1. 全部简答题按章节知识（A—O）排序，章内按二级知识点归并，同一知识点集中作答。",
            "2. 每题按“题目—参考答案”编排，答案已拆成分点，逐条分行，避免一大段堆叠。",
            "3. 答案覆盖 %d 题，包含 2004—2008、2009—2012 年原卷未附答案的题目（按教材补写）；可直接作为答题模板。" % len(QS),
            "4. 配套另有《简答题记忆压缩包》，用于考前快速回忆。",
        ]
    else:
        notes = [
            "1. 本册是答案的“压缩包”：每题只保留记忆链、关键词与展开点数。",
            "2. 看到记忆链后，按“定义→原因→位置→后果/措施”的顺序展开成完整答案。",
            "3. 同一知识点在多个年份重复出现，记忆链通用；题号后标注年份便于对照真题。",
            "4. 需要完整表述时，翻看配套《简答题详解》。",
        ]
    yy = 442
    for n in notes:
        for ln in R(doc, False).wrap(n, 470, 10.5, "r"):
            page.insert_text((56, yy), ln, fontname="r", fontsize=10.5, color=INK)
            yy += 19
        yy += 3
    page.insert_text((56, PH - 46), "整理日期：%s" % datetime.date.today().isoformat(),
                     fontname="r", fontsize=9, color=GRAY)


def add_pagenums(doc):
    total = doc.page_count
    for i in range(1, total):
        txt = "第 %d 页 / 共 %d 页" % (i + 1, total)
        doc[i].insert_text((PW / 2 - font_r.text_length(txt, 8.5) / 2, PH - 26), txt,
                           fontname="r", fontsize=8.5, color=GRAY)


def source_label(q):
    return "真题 · %s 年 · %s 第 %s 题" % (q["year"], q["section"], q["num"])


def build_full():
    doc = fitz.open()
    cover(doc, "full")
    r = R(doc, True)
    toc = [[1, "封面", 1]]
    r.new_page()
    r.put(LEFT, "说明", 11, "b", NAVY)
    r.y += 16
    for ln in r.wrap("下列答案按章节知识排序，每题分点排列。答题时先写结论，再按要点展开，关键公式与数字单独成行。", USABLE, 10, "r"):
        r.put(LEFT, ln, 10, "r", GRAY)
        r.y += 16
    r.y += 6

    cur = None
    n = 0
    for q in QS:
        n += 1
        ch = q["kp"][0]
        if ch != cur:
            cur = ch
            toc.append([2, "%s %s" % (ch, CH_NAME[ch]), r.no])
            r.chapter(ch, CH_NAME[ch])
        points, _mem = topic_of(q)
        sub = q["subs"][0] if q["subs"] else ""
        subt = ("%s %s" % (sub, SUBS.get(sub, {}).get("name", ""))).strip()
        # 估算高度，尽量整题不跨页
        body = q["text"]
        ph = 18 + len(r.wrap(body, USABLE, 11.5)) * 19 + 16
        for p in points:
            ph += len(r.wrap("• " + p, USABLE - 14, 10.2)) * 15.8 + 4
        r.need(min(ph + 16, 420))

        r.put(LEFT, "%d." % n, 12.5, "b", NAVY)
        r.put(LEFT + 32, source_label(q), 9, "r", GRAY)
        if subt:
            r.put(LEFT + 32 + font_r.text_length(source_label(q), 9) + 8, "· " + subt, 8.5, "r", GRAY)
        r.y += 19
        for ln in r.wrap(body, USABLE, 11.5):
            r.put(LEFT, ln, 11.5, "r", INK)
            r.y += 19
        r.y += 2
        r.put(LEFT, "参考答案", 9.5, "b", ACCENT)
        r.y += 15
        for p in points:
            lines = r.wrap("• " + p, USABLE - 14, 10.2)
            for j, ln in enumerate(lines):
                r.need(16)
                x = LEFT + 2 if j == 0 else LEFT + 16
                r.put(x, ln, 10.2, "r", (0.18, 0.20, 0.21))
                r.y += 15.8
            r.y += 4
        r.y += 4
        r.need(8)
        r.page.draw_line(fitz.Point(LEFT, r.y), fitz.Point(RIGHT, r.y), color=(0.92, 0.91, 0.88), width=.5)
        r.y += 9

    add_pagenums(doc)
    doc.set_toc(toc)
    doc.set_metadata({"title": "常州大学 855 机械设计基础 · 简答题详解（按章节知识排序）",
                      "author": "855 真题题库整理", "subject": "%d 道简答题分点详解" % len(QS)})
    doc.subset_fonts()
    doc.save(PDF_FULL, garbage=4, deflate=True)
    doc.close()
    return PDF_FULL


def build_mem():
    doc = fitz.open()
    cover(doc, "mem")
    r = R(doc, True)
    toc = [[1, "封面", 1]]
    r.new_page()
    r.put(LEFT, "使用方式", 11, "b", NAVY)
    r.y += 16
    for ln in r.wrap("先看“记忆链”回忆框架，再按展开点数逐条还原；卡住时回看详细版对应题。记忆链中的箭头表示答题顺序。", USABLE, 10, "r"):
        r.put(LEFT, ln, 10, "r", GRAY)
        r.y += 16
    r.y += 6

    cur = None
    n = 0
    for q in QS:
        n += 1
        ch = q["kp"][0]
        if ch != cur:
            cur = ch
            toc.append([2, "%s %s（记忆）" % (ch, CH_NAME[ch]), r.no])
            r.chapter(ch, CH_NAME[ch])
        points, mem = topic_of(q)
        pts = len(points)
        body = q["text"]
        h = 18 + len(r.wrap(body, USABLE - 30, 9.2)) * 13.5 + 18
        for ln in r.wrap(mem, USABLE - 58, 10.2):
            h += 15.5
        r.need(min(h + 10, 220))

        r.put(LEFT, "%d." % n, 11.5, "b", NAVY)
        r.put(LEFT + 26, "%s｜%s 年" % (q["id"], q["year"]), 8.5, "b", GRAY)
        r.put(RIGHT - font_r.text_length("展开 %d 点" % pts, 8.5), "展开 %d 点" % pts, 8.5, "r", GRAY)
        r.y += 16
        for ln in r.wrap(body, USABLE - 30, 9.2):
            r.put(LEFT + 26, ln, 9.2, "r", (0.33, 0.36, 0.38))
            r.y += 13.5
        r.y += 3
        r.put(LEFT + 26, "记忆链", 9.5, "b", ACCENT)
        r.put(LEFT + 62, "", 9, "r", GRAY)
        r.y += 2
        for ln in r.wrap(mem, USABLE - 58, 10.2):
            r.need(16)
            r.put(LEFT + 62, ln, 10.2, "r", INK)
            r.y += 15.5
        r.y += 6
        r.need(8)
        r.page.draw_line(fitz.Point(LEFT, r.y), fitz.Point(RIGHT, r.y), color=(0.92, 0.91, 0.88), width=.5)
        r.y += 8

    add_pagenums(doc)
    doc.set_toc(toc)
    doc.set_metadata({"title": "常州大学 855 机械设计基础 · 简答题记忆压缩包",
                      "author": "855 真题题库整理", "subject": "%d 道简答题记忆链与展开提示" % len(QS)})
    doc.subset_fonts()
    doc.save(PDF_MEM, garbage=4, deflate=True)
    doc.close()
    return PDF_MEM


if __name__ == "__main__":
    for p in (build_full(), build_mem()):
        d = fitz.open(p)
        print("saved:", p, "pages:", d.page_count, "MB:", round(os.path.getsize(p) / 1048576, 2))
        d.close()
