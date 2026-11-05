# -*- coding: utf-8 -*-
# 匹配简答题答案：优先使用常大真题项目中已有的简答答案/解析
import json, io, os, re, difflib

BASE = r"d:\Code\MyProject\真题统计\常大真题电子版"
BUILD = r"d:\Code\MyProject\真题统计\_build"
SRC = r"D:\Code\MyProject\常大真题项目\data\questions.json"

data = json.load(io.open(os.path.join(BASE, "web", "data", "data.json"), encoding="utf-8"))
src = json.load(io.open(SRC, encoding="utf-8"))["questions"]
src = [q for q in src if q["type"] == "short_answer"]


def norm(s):
    s = re.sub(r"\s+", "", s)
    return re.sub(r"[，。；：、？！,.;:?!（）()“”\"'《》]", "", s)


def parse_group(s, i):
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    return None, i


def replace_fracs(s):
    while True:
        m = re.search(r"\\(dfrac|frac|tfrac)", s)
        if not m:
            break
        i = m.end()
        if i >= len(s) or s[i] != "{":
            break
        num, j = parse_group(s, i)
        if num is None or j >= len(s) or s[j] != "{":
            break
        den, k = parse_group(s, j)
        if den is None:
            break
        s = s[:m.start()] + num + "/" + den + s[k:]
    return s


def latex_to_text(s):
    if not s:
        return ""
    s = s.replace("$", "")
    s = replace_fracs(s)
    for a, b in [(r"\le", "≤"), (r"\ge", "≥"), (r"\times", "×"), (r"\circ", "°"),
                 (r"\cdot", "·"), (r"\pm", "±"), (r"\sim", "~"),
                 (r"\psi", "ψ"), (r"\varphi", "φ"), (r"\sigma", "σ"), (r"\beta", "β"),
                 (r"\eta", "η"), (r"\pi", "π"), (r"\alpha", "α"), (r"\gamma", "γ"),
                 (r"\lambda", "λ"), (r"\rho", "ρ"), (r"\mu", "μ"), (r"\omega", "ω"),
                 (r"\varepsilon", "ε"), (r"\cos", "cos"), (r"\sin", "sin"),
                 (r"\tan", "tan"), (r"\arctan", "arctan"), (r"\max", "max"),
                 (r"\min", "min"), (r"\left", ""), (r"\right", ""),
                 (r"\,", " "), (r"\ ", " "), (r"\;", " ")]:
        s = s.replace(a, b)
    s = re.sub(r"\\sqrt\{([^{}]*)\}", r"√(\1)", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"^(\1)", s)
    s = re.sub(r"_\{([^{}]*)\}", r"_\1", s)
    s = re.sub(r"\\mathrm\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\text\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("^°", "°")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


ours = [q for q in data["questions"] if q["type"] == "简答"]
mapping = {}
unmatched = []
for q in ours:
    cands = []
    for s in src:
        yrs = s.get("source_years") or []
        if q["year"] not in yrs and str(q["year"]) not in [str(x) for x in yrs]:
            continue
        r = difflib.SequenceMatcher(None, norm(q["text"]), norm(s["stem"])).ratio()
        cands.append((r, s))
    if not cands:
        unmatched.append((q["id"], 0.0, None))
        continue
    r, s = max(cands, key=lambda x: x[0])
    if r < 0.62:
        unmatched.append((q["id"], r, s["id"]))
        continue
    ans = latex_to_text(s.get("answer")) if s.get("answer") else latex_to_text(s.get("explanation"))
    mapping[q["id"]] = {
        "answer": ans,
        "explanation": "",
        "source_id": s["id"],
        "sim": round(r, 3),
    }

# 手工补全/修正关键结论与公式
FIX = {
    "2014-二-2": "蜗杆传动效率低（一般 0.7~0.9 以下），损失的功率全部转化为热量。闭式传动散热条件差，连续工作时油温不断升高，使润滑油粘度下降、油膜破坏，导致齿面胶合和磨损加剧。故须进行热平衡计算，保证油温 t1≤60~70℃、油温与室温之差不超过 60~70℃；不满足时应加散热片、风扇或油冷却器。",
    "2014-二-5": "螺纹副自锁条件为 ψ≤φv。螺旋升角 ψ=arctan(nP/(πd₂))，升角越小，效率 η=tanψ/tan(ψ+φv) 越低，但自锁越可靠。只要升角不大于当量摩擦角 φv，无论轴向力多大，螺纹副都不会自行松退。故连接用螺纹取小升角（细牙螺纹升角更小、自锁更好），传动用螺纹取大升角（效率高）。",
    "2017-二-3": "① 松螺栓连接：装配时不拧紧，螺栓只承受轴向拉力，强度条件 σ=F/(πd1²/4)≤[σ]。② 紧螺栓连接：装配时需拧紧，螺栓同时承受预紧拉力 F0 和螺纹副的扭转切应力，故把拉应力增大 30%（取系数 1.3）：σ=1.3F0/(πd1²/4)≤[σ]。若还承受轴向工作载荷 F，则总拉力 F2=F0+[Cb/(Cb+Cm)]F，按 σ=1.3F2/(πd1²/4)≤[σ] 计算，并校核残余预紧力 F1=F2−F>0。",
    "2018-二-1": "接触强度主要取决于分度圆直径：d1 越大接触应力越小，故 A 对接触强度较高。弯曲强度在模数和齿宽相同时取决于齿数：A 对 z1=66/2=33，B 对 z1=60/2=30，A 对齿数多、齿形系数小，故 A 对弯曲强度也较高。结论：A 对的接触强度和弯曲强度均高于 B 对。",
    "2018-二-3": "① 不打滑条件：Fe≤Fec=2F0(e^fα−1)/(e^fα+1)，即保证足够的初拉力和包角；② 不疲劳损坏条件：σmax=σ1+σb1+σc≤[σ]，即限制弯曲应力与应力循环次数。",
    "2019-二-2": "由 P=Fe·v/1000 可知，v 越大则所需有效拉力越小、带的根数越少；但 v 过大会使离心力增大、有效拉力下降、带寿命降低。一般取 v=5~25 m/s；高速轴或高速带传动可适当提高，但不宜超过 25~30 m/s。",
    "2020-二-1": "静平衡条件：各偏心质量的离心惯性力矢量和为零；动平衡条件：离心惯性力矢量和与惯性力偶矩矢量和同时为零。本题 D=300 mm、b=20 mm，b/D≈0.067≤0.2（D/b=15≥5），属盘状回转件，只需进行静平衡。",
    "2020-二-3": "按承载情况分为：心轴（只受弯矩，分转动心轴和固定心轴）、传动轴（只受转矩）、转轴（同时受弯矩和转矩）。齿轮减速器中的轴为转轴；铁路车辆轮轴随车轮转动、只受弯矩，为转动心轴。",
    "2020-二-5": "四种轴承内径代号均为 07，故内径 d=35 mm：N307 为直径系列 3 的圆柱滚子轴承，6207 为深沟球轴承，30207 为圆锥滚子轴承，51307 为推力球轴承。极限转速最高的是深沟球轴承 6207；径向承载能力最高的是圆柱滚子轴承 N307；锥齿轮轴系宜用圆锥滚子轴承 30207，可同时承受径向与轴向力。",
    "2021-一-1": "自锁原因：压力角 α 过大时，驱动力沿从动件运动方向的有效分力减小，而法向分力引起的摩擦阻力增大；当 α 超过临界压力角 αc 时，无论驱动力多大都无法推动从动件，机构自锁。避免措施：增大基圆半径、合理选择从动件运动规律（减小加速度与冲击）、采用平底从动件、改善润滑与减小摩擦，使 α≤[α]（推程许用压力角一般 30°~38°）。",
    "2022-二-2": "带传动的最大有效拉力取决于：①初拉力 F0；②小带轮包角 α1；③带与带轮间的摩擦系数 f（带速过高时离心拉力会削弱有效拉力）。由欧拉公式 Fmax=2F0·(e^fα−1)/(e^fα+1) 决定，初拉力、包角、摩擦系数越大，有效拉力越大。若所需圆周力超过极限摩擦力，带将打滑（通常从小带轮开始），传动失效并伴随剧烈磨损与发热。",
}
for qid, txt in FIX.items():
    if qid in mapping:
        mapping[qid]["answer"] = txt

print("ours", len(ours), "matched", len(mapping), "unmatched", len(unmatched))
for qid, r, sid in unmatched:
    print("UNMATCHED", qid, round(r, 3), sid)
print("\nmatches:")
for qid, m in mapping.items():
    print(qid, "<-", m["source_id"], m["sim"], m["answer"][:50])

json.dump(mapping, io.open(os.path.join(BUILD, "short_answers.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
