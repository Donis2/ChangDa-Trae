# -*- coding: utf-8 -*-
import json, os, sys, re, collections

BUILD = r"d:\Code\MyProject\真题统计\_build"
OUT = r"d:\Code\MyProject\真题统计\常大真题电子版\web\data"
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, BUILD)
import data1, data2, data3, data4, data5, data6, data7
import subrules
import filljudge_answers
import short_qa
QS = data1.Q + data2.Q + data3.Q + data4.Q + data5.Q + data6.Q + data7.Q
FJ = filljudge_answers.A
SHORT = json.load(open(os.path.join(BUILD, "short_answers.json"), encoding="utf-8"))
SUB_DEF = subrules.SUBS
SUB_MAP = {c: (n, ch) for c, n, ch, _ in SUB_DEF}
SUB_RULES = {c: kw for c, n, ch, kw in SUB_DEF}

FIGS = os.path.join(os.path.dirname(OUT), "assets", "figs", "manifest.json")
figman = json.load(open(FIGS, encoding="utf-8"))
ansman = json.load(open(os.path.join(os.path.dirname(OUT), "assets", "answers", "manifest.json"), encoding="utf-8"))

CHAPTERS = [
    ("A", "机械设计总论"),
    ("B", "机构组成与自由度"),
    ("C", "平面连杆机构"),
    ("D", "凸轮机构"),
    ("E", "齿轮传动"),
    ("F", "轮系"),
    ("G", "带传动"),
    ("H", "链传动"),
    ("I", "螺纹联接"),
    ("J", "键联接与其他联接"),
    ("K", "轴与轴系结构"),
    ("L", "滚动轴承"),
    ("M", "滑动轴承"),
    ("N", "联轴器与离合器"),
    ("O", "机械平衡与运转"),
]

RULES = [
    ("O", ["平衡", "飞轮", "速度波动", "质径积", "动平衡", "静平衡", "周期性波动"]),
    ("M", ["滑动轴承", "动压油膜", "油膜", "pv值", "轴瓦", "非液体摩擦"]),
    ("N", ["联轴器", "离合器"]),
    ("L", ["滚动轴承", "轴承", "额定寿命", "当量动载荷", "角接触", "深沟球", "圆锥滚子", "7307", "7209", "6208", "3312", "7310", "6350", "7250", "7309", "61313", "轴承代号", "派生轴向力", "内部轴向力"]),
    ("I", ["螺纹", "螺栓", "螺钉", "双头螺柱", "自锁", "预紧", "防松", "牙型", "螺旋升角", "螺旋", "粗牙", "细牙", "单线", "双线"]),
    ("J", ["键联接", "平键", "楔键", "花键", "销", "过盈", "铆", "焊接", "松键"]),
    ("H", ["链传动", "滚子链", "链条", "节距"]),
    ("G", ["带传动", "V带", "弹性滑动", "打滑", "包角", "张紧", "初拉力", "紧边", "松边", "带轮", "单根带", "带的", "带速"]),
    ("F", ["轮系", "行星架", "系杆", "周转轮", "定轴轮", "传动比"]),
    ("D", ["凸轮", "从动件", "基圆", "滚子", "推杆", "运动规律", "刚性冲击", "柔性冲击", "压力角"]),
    ("C", ["曲柄", "摇杆", "连杆", "极位夹角", "急回", "死点", "传动角", "行程速比", "四杆机构", "四连杆"]),
    ("E", ["齿轮", "模数", "齿数", "分度圆", "齿顶圆", "齿根圆", "渐开线", "螺旋角", "根切", "变位", "啮合", "重合度", "斜齿", "锥齿轮", "圆锥齿轮", "齿厚", "齿槽宽", "中心距", "齿廓", "蜗杆", "蜗轮"]),
    ("B", ["自由度", "复合铰链", "局部自由度", "虚约束", "运动简图", "活动构件", "运动副", "高副", "低副"]),
    ("K", ["轴系", "结构设计", "轴的结构", "转轴", "心轴", "传动轴", "轴的刚度", "轴的强度", "轴的作用"]),
    ("A", ["机器", "机构", "零件", "构件", "失效形式", "设计准则", "制造单元", "标准化"]),
]

MANUAL_KP = {
    "2010-3-1": ["B"], "2010-3-6": ["K"], "2009-5-1": ["K"], "2011-4-5": ["K"],
    "2014-7-1": ["K"], "2015-5-1": ["I"], "2017-3-1": ["K"], "2017-8-1": ["K"],
    "2018-9-1": ["K"], "2019-5-1": ["K"], "2020-4-1": ["K"], "2021-2-1": ["K"],
    "2022-9-1": ["K"], "2024-3-3": ["K"], "2013-5-1": ["I"], "2013-8-1": ["K"],
    "2009-4-2": ["E"], "2010-3-3": ["E"], "2011-4-3": ["E"], "2019-3-1": ["C"],
    "2024-3-4": ["I"], "2020-9-1": ["I"], "2024-3-2": ["O"], "2022-2-4": ["O"],
}


SEC_INDEX = {}
for q in QS:
    k = (q["y"], q["sec"])
    if k not in SEC_INDEX:
        SEC_INDEX[k] = len([1 for kk in SEC_INDEX if kk[0] == q["y"]]) + 1


def subs_of(q):
    sec_no = SEC_INDEX[(q["y"], q["sec"])]
    key = f"{q['y']}-{sec_no}-{q['n']}"
    if key in subrules.MANUAL_SUBS:
        return subrules.MANUAL_SUBS[key]
    text = q["txt"] + " " + " ".join(q["opts"])
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
    picked = []
    chapters = set()
    for i, (code, s) in enumerate(ranked):
        if i > 0 and s < max(1.5, top * 0.45):
            continue
        ch = SUB_MAP[code][1]
        if ch in chapters and len(picked) >= 2:
            continue
        picked.append(code)
        chapters.add(ch)
        if len(picked) >= 3:
            break
    return picked


def kp_of(q):
    sec_no = SEC_INDEX[(q["y"], q["sec"])]
    key = f"{q['y']}-{sec_no}-{q['n']}"
    for mk, v in MANUAL_KP.items():
        if key == mk:
            return v
    text = q["txt"] + " " + " ".join(q["opts"])
    scores = collections.Counter()
    for code, words in RULES:
        for w in words:
            n = text.count(w)
            if n:
                scores[code] += n * (2 if len(w) >= 4 else 1)
    if q["ty"] in ("填空", "判断", "选择") and scores.get("B", 0) == 0:
        pass
    if not scores:
        return ["A"]
    ranked = [(c, s) for c, s in scores.most_common() if c != "A"]
    if not ranked:
        return ["A"]
    top = [ranked[0]]
    if len(ranked) > 1 and ranked[1][1] >= 0.6 * ranked[0][1]:
        top.append(ranked[1])
    return [c for c, _ in top]


def qid(q):
    return f"{q['y']}-{q['sec'].split('、')[0]}-{q['n']}"

years_meta = {}
for y in sorted({q["y"] for q in QS}):
    ys = [q for q in QS if q["y"] == y]
    years_meta[y] = {
        "count": len(ys),
        "marks": 0 if y == 2024 else 150,
        "sections": list(dict.fromkeys(q["sec"] for q in ys)),
        "answers": ansman.get(str(y), []),
    }
out_qs = []
missing = []
for q in QS:
    if q.get("kp") is not None:
        chapters = q["kp"]
        subs = q.get("subs") or []
    else:
        subs = subs_of(q)
        chapters = []
        for c in subs:
            ch = SUB_MAP[c][1]
            if ch not in chapters:
                chapters.append(ch)
        if not chapters:
            chapters = kp_of(q)
            subs = []
    rec = {
        "id": qid(q),
        "year": q["y"],
        "section": q["sec"],
        "num": q["n"],
        "type": q["ty"],
        "text": q["txt"],
        "options": q["opts"],
        "marks": q["marks"],
        "figs": [],
        "kp": chapters,
        "subs": subs,
    }
    if q.get("answer"):
        rec["answer"] = q["answer"]
    if q.get("expl"):
        rec["explanation"] = q["expl"]
    if q.get("ansfig"):
        rec["answerFigs"] = q["ansfig"]
    fj = FJ.get(rec["id"])
    if fj:
        if fj.get("text"):
            rec["text"] = fj["text"]
        rec["answer"] = fj["a"]
        rec["explanation"] = fj["e"]
        if fj.get("flag"):
            rec["reviewNote"] = fj["flag"]
    sm = SHORT.get(rec["id"])
    if rec["type"] == "简答" and rec["id"] in short_qa.MAP:
        rec["answer"] = "\n".join(short_qa.TOPICS[short_qa.MAP[rec["id"]]]["points"])
    elif rec["type"] == "简答" and sm and not rec.get("answer"):
        rec["answer"] = sm["answer"]
        if sm.get("explanation"):
            rec["explanation"] = sm["explanation"]
    for f in q["fig"]:
        if f in figman:
            rec["figs"].append({"key": f, "images": figman[f]})
        else:
            missing.append((rec["id"], f))
    out_qs.append(rec)

DATA = {
    "meta": {
        "subject": "常州大学 855 机械设计基础 历年真题题库",
        "years": years_meta,
        "chapters": [{"code": c, "name": n, "subs": [{"code": sc, "name": sn} for sc, sn, sch, _ in SUB_DEF if sch == c]} for c, n in CHAPTERS],
        "subs": [{"code": sc, "name": sn, "chap": sch} for sc, sn, sch, _ in SUB_DEF],
        "total": len(out_qs),
        "withFigure": sum(1 for q in out_qs if q["figs"]),
        "source": "2004–2026 年真题扫描件（2005、2016 年缺卷，2023/2024/2025/2026 年为回忆版）；2004–2008 为江苏工业学院时期 455 机械设计/机械设计基础卷；答案 2009–2022、2024 采用老魏版及原完整参考答案扫描件，2023/2025/2026 为参考答案扫描件或整理后的文字答案，2004–2008 年原卷未附答案；2026 年答案原件仅含第 5–10 页",
        "yearNotes": {
            "2004": "江苏工业学院 · 455 机械设计",
            "2006": "江苏工业学院 · 455 机械设计",
            "2007": "江苏工业学院 · 455 机械设计",
            "2008": "江苏工业学院 · 机械设计基础 A 卷",
            "2023": "回忆版",
            "2024": "回忆版",
            "2025": "回忆版",
            "2026": "回忆版 · 仅收录已回忆题目（选择 6—9、简答 4—5、综合 4/6，第3题仅记页码）",
        },
    },
    "questions": out_qs,
}
json.dump(DATA, open(os.path.join(OUT, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

js = "window.DATA = " + json.dumps(DATA, ensure_ascii=False, separators=(",", ":")) + ";\n"
open(os.path.join(OUT, "data.js"), "w", encoding="utf-8").write(js)

# stats
kc = collections.Counter()
for q in out_qs:
    for k in q["kp"]:
        kc[k] += 1
tyc = collections.Counter(q["type"] for q in out_qs)
yc = collections.Counter(q["year"] for q in out_qs)
print("questions:", len(out_qs))
print("missing figs:", missing)
print("types:", dict(tyc))
print("chapters:", dict(kc))
print("years:", dict(sorted(yc.items())))
sc = collections.Counter()
for q in out_qs:
    for s in q["subs"]:
        sc[s] += 1
print("subs used:", len(sc), "of", len(SUB_DEF))
print("no-sub questions:", sum(1 for q in out_qs if not q["subs"]))
