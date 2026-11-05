/* 常州大学 855 机械设计基础 · 真题题库前端逻辑 */
(function () {
  const D = window.DATA;
  const QS = D.questions;
  const META = D.meta;
  const EXT = window.EXT || { meta: {}, questions: [] };
  const EXT_QS = EXT.questions || [];
  const YEARS = Object.keys(META.years).map(Number).sort((a, b) => a - b);
  const CH = new Map(META.chapters.map(c => [c.code, c.name]));
  const SUBS = new Map(META.subs.map(s => [s.code, s]));
  const TYPES = ["选择", "填空", "判断", "简答", "分析", "计算", "结构"];
  const COLORS = ["#1d4c63", "#2f6b7f", "#4a8391", "#b84c33", "#c76b4c", "#b28b3e", "#8a6d3b", "#6c7f8a"];
  const QS_ID = new Map(QS.map(q => [q.id, q]));

  const BIG_TYPES = [
    {
      code: "FREEDOM", name: "自由度计算",
      desc: "识别复合铰链、局部自由度、虚约束，套用 F=3n−2P_L−P_H 并判断是否具有确定运动，几乎每年一道计算大题。",
      ids: ["2009-四-1", "2010-三-1", "2011-四-1", "2012-五-1", "2013-三-1", "2014-三-1", "2015-四-1", "2017-四-1", "2018-三-1", "2019-六-1", "2020-五-1", "2021-三-1", "2022-三-1", "2024-三-1", "2025-三-1", "2008-三-1"],
    },
    {
      code: "GEAR_GEO", name: "齿轮几何参数计算",
      desc: "分度圆、齿顶/齿根圆、齿距、齿厚、中心距、斜齿轮螺旋角与当量齿数等参数计算，步骤固定、最易拿分。",
      ids: ["2009-四-2", "2010-三-3", "2011-四-3", "2012-五-2", "2013-四-1", "2015-四-2", "2018-四-1", "2020-七-1", "2022-四-1", "2024-三-6"],
    },
    {
      code: "TRAIN", name: "轮系传动比计算",
      desc: "定轴、周转（行星）、复合轮系的传动比与转向判断，含转化机构法。",
      ids: ["2009-四-3", "2010-三-2", "2011-四-2", "2013-六-1", "2014-五-1", "2017-六-1", "2018-五-1", "2019-九-1", "2020-六-1", "2022-五-1", "2024-三-7", "2023-三-3", "2025-三-2", "2008-四-1", "2026-三-6"],
    },
    {
      code: "BOLT", name: "螺栓强度计算",
      desc: "松/紧螺栓强度、预紧力与残余预紧力、螺栓组受力、变载荷疲劳强度，注意许用应力与小径公式。",
      ids: ["2011-四-4", "2012-五-3", "2017-七-1", "2018-六-1", "2019-八-1", "2020-九-1", "2021-三-3", "2022-六-1", "2024-三-4", "2025-三-3", "2025-三-4", "2004-二-1", "2006-二-4", "2007-二-1"],
    },
    {
      code: "BEARING", name: "滚动轴承计算",
      desc: "派生轴向力、轴向力平衡、当量动载荷 P=f_p(XF_r+YF_a)、额定寿命 L_h 计算，角接触/圆锥滚子轴承为重点。",
      ids: ["2009-四-4", "2010-三-5", "2011-四-6", "2012-五-4", "2013-九-1", "2014-六-1", "2015-四-4", "2018-七-1", "2019-七-1", "2020-八-1", "2021-三-2", "2022-八-1", "2023-三-2", "2004-二-3", "2006-二-2", "2007-二-2", "2008-六-1", "2026-三-4"],
    },
    {
      code: "SHAFT", name: "轴系结构改错",
      desc: "从轴向固定、周向固定、轴承组合、密封润滑、工艺等角度找出 6～10 处错误并说明原因。",
      ids: ["2009-五-1", "2010-三-6", "2011-四-5", "2014-七-1", "2017-八-1", "2018-九-1", "2019-五-1", "2020-四-1", "2021-二-1", "2022-九-1", "2024-三-3", "2025-二-2", "2004-三-1", "2006-二-6", "2007-二-3", "2008-八-1", "2026-三-7"],
    },
    {
      code: "FORCE", name: "齿轮/蜗杆受力分析作图",
      desc: "判断螺旋线旋向、转向与轴向力方向，画出圆周力、径向力、轴向力三个分力，常与蜗杆—斜齿轮—锥齿轮组合。",
      ids: ["2009-三-2", "2010-三-4", "2012-四-1", "2013-七-1", "2014-四-1", "2015-四-3", "2017-五-1", "2018-八-1", "2019-四-1", "2020-三-1", "2021-二-3", "2022-七-1", "2024-三-5", "2025-二-1", "2004-二-2", "2006-二-3", "2007-二-4", "2008-五-1"],
    },
    {
      code: "FOURBAR", name: "四杆机构设计与分析",
      desc: "曲柄存在条件、机架选择、急回与死点判断、按杆长条件设计曲柄摇杆/双摇杆机构。",
      ids: ["2009-三-1", "2015-三-1", "2019-三-1", "2021-二-2", "2026-二-4"],
    },
    {
      code: "BALANCE", name: "机械平衡",
      desc: "静平衡与动平衡条件、质径积计算与平衡质量配置（含相关简答）。",
      ids: ["2018-二-2", "2019-二-5", "2020-二-1", "2021-一-5", "2022-二-4", "2024-三-2"],
    },
    {
      code: "SHAFTTYPE", name: "轴的类型判别",
      desc: "按承载情况区分心轴、转轴、传动轴，并在减速器/卷筒等传动系统中逐根判断。",
      ids: ["2013-八-1", "2017-三-1", "2008-一-6"],
    },
    {
      code: "THREADDRAW", name: "螺纹联接结构作图",
      desc: "识别螺栓、双头螺柱、螺钉等联接型式，说明优缺点与适用场合，或画出正确结构。",
      ids: ["2013-五-1", "2015-五-1", "2008-一-4"],
    },
  ];

  const state = {
    view: "overview",
    q: "",
    years: new Set(),
    types: new Set(),
    kps: new Set(),
    subs: new Set(),
    sort: "year-desc",
    page: 1,
    pageSize: 24,
    trendKp: "E",
    train: { mode: "chapter", chapter: "E", sub: "", big: "FREEDOM", list: [], i: 0, shuffle: false, active: false },
    quiz: { year: "all", scope: "all", order: [], i: 0, picks: [], shuffled: false },
    mistakes: { type: "all", chapter: "all", active: false, list: [], i: 0 },
    kpTable: { chapter: "all", sort: "count-desc", q: "" },
    ext: { source: "all", type: "all", exam: "all", chapter: "all", q: "", page: 1, pageSize: 24 },
    answerVersion: "kaoyanqun",
  };

  const MASTER_KEY = "cx855_mastered_v1";
  const mastered = new Set();
  const VIEWS = ["overview", "bank", "ext", "quiz", "mistakes", "train", "stats", "subs", "answers"];
  let lastHashApplied = "";
  let lastBox = null;

  const QUIZ = window.QUIZ || {};

  const ANSWER_VERSIONS = META.answerVersions || {};
  const ANSWER_VER_KEY = "cx855_answer_version_v1";
  try {
    const saved = localStorage.getItem(ANSWER_VER_KEY);
    if (saved && ANSWER_VERSIONS[saved]) state.answerVersion = saved;
  } catch (e) { /* ignore */ }
  try {
    (JSON.parse(localStorage.getItem(MASTER_KEY) || "[]") || []).forEach(id => mastered.add(id));
  } catch (e) { /* ignore */ }
  function saveMastered() {
    try { localStorage.setItem(MASTER_KEY, JSON.stringify(Array.from(mastered))); } catch (e) { /* ignore */ }
  }

  const MISTAKE_KEY = "cx855_mistakes_v1";
  let mistakeIds = [];
  const mistakeSet = new Set();
  try {
    (JSON.parse(localStorage.getItem(MISTAKE_KEY) || "[]") || []).forEach(id => {
      if (typeof id === "string" && QS_ID.has(id) && !mistakeSet.has(id)) { mistakeSet.add(id); mistakeIds.push(id); }
    });
  } catch (e) { /* ignore */ }
  function saveMistakes() {
    try { localStorage.setItem(MISTAKE_KEY, JSON.stringify(mistakeIds)); } catch (e) { /* ignore */ }
  }
  function hasMistake(id) { return mistakeSet.has(id); }
  function updateMistakeBadge() {
    const b = $("#mistakeBadge");
    if (!b) return;
    b.textContent = mistakeIds.length;
    b.hidden = !mistakeIds.length;
  }
  function syncMistakeButtons() {
    $$("[data-mistake]").forEach(b => {
      const on = hasMistake(b.dataset.mistake);
      b.classList.toggle("on", on);
      b.textContent = on ? "移出错题本" : "加入错题本";
    });
  }
  function addMistake(id) {
    if (!id || mistakeSet.has(id)) return false;
    mistakeIds.unshift(id);
    mistakeSet.add(id);
    saveMistakes();
    updateMistakeBadge();
    syncMistakeButtons();
    if (state.view === "mistakes" && !state.mistakes.active) renderMistakes();
    return true;
  }
  function removeMistake(id) {
    if (!mistakeSet.has(id)) return false;
    mistakeSet.delete(id);
    mistakeIds = mistakeIds.filter(x => x !== id);
    saveMistakes();
    updateMistakeBadge();
    syncMistakeButtons();
    const s = state.mistakes;
    if (s.active) {
      s.list = s.list.filter(x => x !== id);
      if (!s.list.length) { exitMistakePractice(false); return true; }
      s.i = Math.min(s.i, s.list.length - 1);
      renderMistakeQ();
    } else if (state.view === "mistakes") {
      renderMistakes();
    }
    return true;
  }
  function toggleMistake(id) { return hasMistake(id) ? removeMistake(id) : addMistake(id); }
  function mistakeBtnHTML(id, extra = "") {
    const on = hasMistake(id);
    return `<button class="mistake-btn${on ? " on" : ""}${extra ? " " + extra : ""}" type="button" data-mistake="${esc(id)}">${on ? "移出错题本" : "加入错题本"}</button>`;
  }
  function bindMistakeButtons(root = document) {
    $$("[data-mistake]", root).forEach(b => b.onclick = e => {
      e.preventDefault();
      toggleMistake(b.dataset.mistake);
    });
  }

  const QUIZ_KEY = "cx855_quiz_v1";
  let quizRec = {};
  try { quizRec = JSON.parse(localStorage.getItem(QUIZ_KEY) || "{}") || {}; } catch (e) { quizRec = {}; }
  function saveQuiz() {
    try { localStorage.setItem(QUIZ_KEY, JSON.stringify(quizRec)); } catch (e) { /* ignore */ }
  }

  /* ---------------- helpers ---------------- */
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));

  function renderMath(root) {
    if (!window.renderMathInElement || !root) return;
    try {
      window.renderMathInElement(root, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\[", right: "\\]", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false },
        ],
        throwOnError: false,
        ignoredTags: ["script", "style", "textarea", "pre", "code"],
      });
    } catch (e) { /* ignore */ }
  }

  const CN_DIGITS = { 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9, 十: 10 };
  function cnOrdinal(section) {
    const m = String(section || "").match(/^([一二三四五六七八九十]+)/);
    if (!m) return 99;
    const t = m[1];
    if (t.length === 1) return CN_DIGITS[t] || 99;
    if (t[0] === "十") return 10 + (CN_DIGITS[t[1]] || 0);
    if (t[1] === "十") return (CN_DIGITS[t[0]] || 0) * 10 + (CN_DIGITS[t[2]] || 0);
    return CN_DIGITS[t[0]] || 99;
  }
  // 原卷顺序：先按卷面大题（一、二、三……），再按题号
  function paperOrder(a, b) {
    const sa = cnOrdinal(a.section), sb = cnOrdinal(b.section);
    if (sa !== sb) return sa - sb;
    const na = parseInt(a.num, 10) || 0, nb = parseInt(b.num, 10) || 0;
    return na - nb || a._order - b._order;
  }

  function answerVerLabel(v) { return (ANSWER_VERSIONS[v] && ANSWER_VERSIONS[v].label) || v; }
  function answerPagesOf(year, ver) {
    const y = META.years[String(year)];
    if (!y || !y.answers) return [];
    if (Array.isArray(y.answers)) return ver === "laowei" || ver === "kaoyanqun" ? y.answers : [];
    return (y.answers[ver] || []).slice();
  }
  function availableAnswerVersions(year) {
    return Object.keys(ANSWER_VERSIONS).filter(v => v !== "default" && answerPagesOf(year, v).length);
  }
  function answerSrc(year, ver, file) { return `assets/answers/${ver}/${file}`; }

  QS.forEach((q, i) => {
    q._s = (q.text + " " + q.options.join(" ")).toLowerCase();
    q._n = parseFloat(q.num) || 0;
    q._order = i;
  });

  function highlight(text) {
    const needle = state.q.trim();
    let html = esc(text);
    if (!needle) return html;
    const safe = needle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return html.replace(new RegExp(safe, "gi"), m => `<mark>${m}</mark>`);
  }

  function countBy(arr, fn) {
    const m = new Map();
    arr.forEach(x => fn(x).forEach(k => m.set(k, (m.get(k) || 0) + 1)));
    return m;
  }

  const kpCount = countBy(QS, q => q.kp);
  const subCount = countBy(QS, q => q.subs);
  const typeCount = countBy(QS, q => [q.type]);
  const yearCount = countBy(QS, q => [String(q.year)]);

  const SUB_QS = new Map(META.subs.map(s => [s.code, []]));
  QS.forEach(q => q.subs.forEach(code => {
    const arr = SUB_QS.get(code);
    if (arr) arr.push(q);
  }));
  const TOTAL_SUB_HITS = Array.from(subCount.values()).reduce((a, b) => a + b, 0);

  /* ---------------- overview ---------------- */
  function renderHero() {
    const fig = QS.find(q => q.id === "2017-四-1") || QS.find(q => q.figs.length);
    const imgs = fig ? fig.figs[0].images : [];
    $("#heroFigure").innerHTML =
      (imgs.length ? `<img src="assets/figs/${imgs[0]}" alt="原卷机构插图">` : "") +
      `<figcaption>原卷插图 · ${fig ? fig.year + " 年第 " + fig.num + " 题" : ""}</figcaption>`;
  }

  function renderStats() {
    const figQ = QS.filter(q => q.figs.length).length;
    const cards = [
      { num: YEARS.length, label: `套历年真题（${YEARS[0]}—${YEARS[YEARS.length - 1]}）` },
      { num: QS.length, label: "道试题 · 逐题校对题号" },
      { num: figQ, label: "道含原卷插图试题" },
      { num: META.subs.length, label: `个细分知识点 · ${META.chapters.length} 个章节` },
    ];
    $("#statRow").innerHTML = cards.map(c =>
      `<div class="stat-card"><div class="num">${c.num}</div><div class="label">${c.label}</div></div>`
    ).join("");
  }

  function barRows(items, max, opts = {}) {
    return items.map(([label, val, key]) => {
      const w = Math.max(2, (val / max) * 100);
      return `<div class="barrow${opts.click ? " click" : ""}" ${opts.click ? `data-key="${esc(key)}"` : ""} ${opts.kind ? `data-kind="${opts.kind}"` : ""}>
        <div class="blabel" title="${esc(label)}">${esc(label)}</div>
        <div class="btrack"><div class="bfill" style="width:${w}%"></div></div>
        <div class="bval">${val}</div>
      </div>`;
    }).join("");
  }

  function goBank(opts) {
    if (opts.clear) { state.years.clear(); state.types.clear(); state.kps.clear(); state.subs.clear(); }
    if (opts.year) state.years = new Set([String(opts.year)]);
    if (opts.kp) state.kps = new Set([opts.kp]);
    if (opts.sub) state.subs = new Set([opts.sub]);
    if (opts.type) state.types = new Set([opts.type]);
    state.view = "bank"; state.page = 1;
    syncTabs(); renderFilters(); renderList(); renderResultCount();
    pushHash("bank");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function renderYearChart() {
    const items = YEARS.map(y => [String(y), yearCount.get(String(y)) || 0, y]);
    const max = Math.max(...items.map(i => i[1]));
    $("#yearChart").innerHTML = barRows(items, max, { click: true });
    $$("#yearChart .barrow").forEach(el => el.onclick = () => goBank({ year: el.dataset.key }));
  }

  function svgArc(cx, cy, r, a0, a1, color) {
    const p = a => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    const large = a1 - a0 > Math.PI ? 1 : 0;
    return `<path d="M${x0} ${y0} A${r} ${r} 0 ${large} 1 ${x1} ${y1}" stroke="${color}" stroke-width="26" fill="none"/>`;
  }

  function renderTypeChart() {
    const total = QS.length;
    $("#typeChartHint").textContent = `共 ${total} 题`;
    const items = TYPES.map(t => [t, typeCount.get(t) || 0]).filter(i => i[1]);
    let a = -Math.PI / 2;
    const paths = items.map(([t, v], i) => {
      const a1 = a + (v / total) * Math.PI * 2;
      const path = svgArc(80, 80, 58, a, Math.max(a + 0.004, a1), COLORS[i % COLORS.length]);
      a = a1;
      return path;
    }).join("");
    $("#typeChart").innerHTML = `
      <div class="donut-wrap">
        <svg class="donut" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r="58" stroke="#efe9dd" stroke-width="26" fill="none"/>
          ${paths}
          <text x="80" y="76" text-anchor="middle" font-size="26" font-family="Georgia, serif" fill="#1d4c63">${total}</text>
          <text x="80" y="94" text-anchor="middle" font-size="12" fill="#7c8a92">道题</text>
        </svg>
        <div class="donut-legend">
          ${items.map(([t, v], i) => `<div><i style="background:${COLORS[i % COLORS.length]}"></i>${t}<b>${v}</b> <span style="color:#7c8a92">${Math.round(v / total * 100)}%</span></div>`).join("")}
        </div>
      </div>`;
  }

  function renderTopKp() {
    const items = Array.from(subCount.entries())
      .sort((a, b) => b[1] - a[1]).slice(0, 12)
      .map(([k, v]) => [`${k} ${SUBS.get(k).name}`, v, k]);
    const max = items[0] ? items[0][1] : 1;
    $("#topKpChart").innerHTML = barRows(items, max, { click: true, kind: "sub" });
    $$("#topKpChart .barrow").forEach(el => el.onclick = () => goBank({ sub: el.dataset.key }));
  }

  function renderYearStrip() {
    $("#yearStrip").innerHTML = YEARS.map(y => {
      const m = META.years[String(y)];
      const note = (META.yearNotes || {})[String(y)];
      return `<button class="year-pill" data-year="${y}" title="${esc(note || "")}">
        <span class="y">${y}</span><span class="c">${m.count} 题${m.marks ? " · " + m.marks + " 分" : " · 分值未标"}</span>${note ? `<span class="ynote">${esc(note)}</span>` : ""}</button>`;
    }).join("");
    $$("#yearStrip .year-pill").forEach(el => el.onclick = () => goBank({ year: el.dataset.year }));
  }

  /* ---------------- bank ---------------- */
  function renderChips(el, items, set, onToggle, labelFn = x => x) {
    el.innerHTML = items.map(it => {
      const val = Array.isArray(it) ? it[0] : it;
      const c = Array.isArray(it) ? it[1] : "";
      const on = set.has(String(val)) ? " on" : "";
      return `<button class="chip${on}" data-val="${esc(val)}">${esc(labelFn(val))}${c !== "" ? `<span class="c">${c}</span>` : ""}</button>`;
    }).join("");
    $$(".chip", el).forEach(b => b.onclick = () => onToggle(b.dataset.val));
  }

  function toggle(set, v) {
    const key = String(v);
    if (set.has(key)) set.delete(key);
    else set.add(key);
  }

  function renderFilters() {
    renderChips($("#yearChips"),
      [["全部", QS.length]].concat(YEARS.map(y => [y, yearCount.get(String(y)) || 0])),
      new Set(state.years.size ? Array.from(state.years) : ["全部"]),
      v => {
        if (v === "全部") state.years.clear();
        else toggle(state.years, v);
        state.page = 1; renderFilters(); renderList(); renderResultCount();
      },
      v => v === "全部" ? "全部年份" : `${v} 年`);
    renderChips($("#typeChips"), TYPES.map(t => [t, typeCount.get(t) || 0]), state.types,
      v => { toggle(state.types, v); state.page = 1; renderFilters(); renderList(); renderResultCount(); });
    renderChips($("#kpChips"), Array.from(kpCount.entries()).sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, v]), state.kps,
      v => { toggle(state.kps, v); state.subs.clear(); syncSubSelect(); state.page = 1; renderFilters(); renderList(); renderResultCount(); },
      v => CH.get(v));

    const sel = $("#subSelect");
    const cur = Array.from(state.subs)[0] || "";
    sel.innerHTML = `<option value="">全部细分知识点</option>` +
      META.chapters.map(c => {
        const opts = c.subs.map(s => {
          const n = subCount.get(s.code) || 0;
          return `<option value="${s.code}" ${s.code === cur ? "selected" : ""}>${s.code} ${s.name}（${n}）</option>`;
        }).join("");
        return `<optgroup label="${c.code} ${c.name}">${opts}</optgroup>`;
      }).join("");
  }
  function syncSubSelect() { const s = $("#subSelect"); if (s) s.value = Array.from(state.subs)[0] || ""; }

  function filtered() {
    const q = state.q.trim().toLowerCase();
    let arr = QS.filter(item => {
      if (state.years.size && !state.years.has(String(item.year))) return false;
      if (state.types.size && !state.types.has(item.type)) return false;
      if (state.kps.size && !item.kp.some(k => state.kps.has(k))) return false;
      if (state.subs.size && !item.subs.some(k => state.subs.has(k))) return false;
      if (q && !item._s.includes(q) && !item.id.includes(q)) return false;
      return true;
    });
    if (state.sort === "year-desc") arr.sort((a, b) => b.year - a.year || paperOrder(a, b));
    else if (state.sort === "year-asc") arr.sort((a, b) => a.year - b.year || paperOrder(a, b));
    else arr.sort((a, b) => (b.marks || 0) - (a.marks || 0) || b.year - a.year || paperOrder(a, b));
    return arr;
  }

  function renderResultCount() {
    const n = filtered().length;
    let extra = "";
    if (state.years.size) extra += " · 年份 " + Array.from(state.years).map(Number).sort((a, b) => a - b).join("、");
    if (state.subs.size) extra += " · " + Array.from(state.subs).map(s => SUBS.get(s).name).join("、");
    if (state.q) extra += ` · 关键词“${state.q}”`;
    $("#resultCount").textContent = `共 ${n} 题${extra}`;
  }

  function questionCard(q) {
    const opts = q.options.length
      ? `<div class="options">${q.options.map((o, i) => `<div class="option"><span class="okey">${"ABCD"[i] || ""}</span><span>${highlight(o)}</span></div>`).join("")}</div>`
      : "";
    const figs = q.figs.map(f => f.images.map((src, i) =>
      `<figure class="qfig" data-src="assets/figs/${src}" data-title="${q.year} 年第 ${q.num} 题 原图">
        <img src="assets/figs/${src}" loading="lazy" alt="${q.year} 年第 ${q.num} 题原图">
        <figcaption class="cap">原卷图 ${q.figs.length > 1 || f.images.length > 1 ? (i + 1) : ""}</figcaption>
      </figure>`).join("")).join("");
    const chapTags = q.kp.map(k => `<span class="kptag" data-kp="${k}">${CH.get(k)}</span>`).join("");
    const subTags = q.subs.map(s => `<span class="kptag sub" data-sub="${s}" title="${CH.get(SUBS.get(s).chap)}">${s} ${SUBS.get(s).name}</span>`).join("");
    const ansVers = availableAnswerVersions(q.year);
    const ansBtn = ansVers.length
      ? `<button class="anslink" data-ans="${q.year}">整卷答案${ansVers.length > 1 ? "（双版本）" : ""} →</button>`
      : `<span class="anslink" style="color:#a9a193;cursor:default">整卷扫描答案未附</span>`;
    const ansFigs = (q.answerFigs || []).map(f =>
      `<figure class="qfig" data-src="assets/figs/${f}" data-title="${q.year} 年第 ${q.num} 题 答案图">
        <img src="assets/figs/${f}" loading="lazy" alt="${q.year} 年第 ${q.num} 题答案图">
        <figcaption class="cap">答案图</figcaption>
      </figure>`).join("");
    const hasOwn = q.answer || q.explanation || ansFigs;
    const ownAns = hasOwn ? `
      <div class="qanswer">
        <button class="qanswer-toggle" type="button" aria-expanded="false">参考答案与解析 <span class="chev">▾</span></button>
        <div class="qanswer-body" hidden>
          ${q.answer ? `<div class="ans-sec"><div class="ans-label">答案</div><div class="ans-text">${esc(q.answer).replace(/\n/g, "<br>")}</div></div>` : ""}
          ${q.explanation ? `<div class="ans-sec"><div class="ans-label">解析</div><div class="ans-text">${esc(q.explanation).replace(/\n/g, "<br>")}</div></div>` : ""}
          ${ansFigs ? `<div class="ans-sec"><div class="ans-label">答案图</div><div class="ans-figs">${ansFigs}</div></div>` : ""}
        </div>
      </div>` : "";
    return `<article class="qcard" id="q-${q.id}">
      <div class="qhead">
        <span class="qid">${q.year} · ${q.section.replace(/^[一二三四五六七八九十]+、/, "")} ${q.num}</span>
        <span class="qtype">${q.type}题</span>
        ${q.marks ? `<span class="qmarks">${q.marks} 分</span>` : ""}
      </div>
      <div class="qtext">${highlight(q.text)}</div>
      ${opts}
      ${figs ? `<div class="qfigs">${figs}</div>` : ""}
      <div class="qfoot">${chapTags}${subTags}${ansBtn}${mistakeBtnHTML(q.id)}</div>
      ${ownAns}
    </article>`;
  }

  function bindCardActions(root) {
    $$(".qfig", root).forEach(el => el.onclick = () =>
      openLightbox(el.dataset.src, el.dataset.title));
    $$(".kptag[data-kp]", root).forEach(el => el.onclick = () =>
      goBank({ kp: el.dataset.kp }));
    $$(".kptag[data-sub]", root).forEach(el => el.onclick = () =>
      goBank({ sub: el.dataset.sub }));
    $$(".anslink[data-ans]", root).forEach(el => el.onclick = () => {
      openAnswerLightbox(el.dataset.ans, 0, state.answerVersion);
    });
    $$(".qanswer-toggle", root).forEach(el => el.onclick = () => {
      const body = el.nextElementSibling;
      const open = body.hidden;
      body.hidden = !open;
      el.setAttribute("aria-expanded", String(open));
      el.classList.toggle("open", open);
    });
    bindMistakeButtons(root);
  }

  function renderList() {
    const arr = filtered();
    const slice = arr.slice(0, state.page * state.pageSize);
    $("#questionList").innerHTML = slice.map(questionCard).join("") ||
      `<div class="panel" style="text-align:center;color:#7c8a92">没有匹配的题目，试试清空筛选条件。</div>`;
    const more = $("#loadMore");
    more.style.display = arr.length > slice.length ? "inline-block" : "none";
    more.textContent = `加载更多（还有 ${arr.length - slice.length} 题）`;
    bindCardActions($("#questionList"));
    renderMath($("#questionList"));
  }

  /* ---------------- stats view ---------------- */
  function renderKpStats() {
    const totalHits = Array.from(subCount.values()).reduce((a, b) => a + b, 0);
    const top = Array.from(subCount.entries()).sort((a, b) => b[1] - a[1])[0];
    const avg = (totalHits / META.subs.length).toFixed(1);
    $("#kpStatRow").innerHTML = [
      [totalHits, "二级知识点命中总次数"],
      [`${top[0]} ${SUBS.get(top[0]).name}`, `最高频细分点 · ${top[1]} 次`],
      [META.subs.length, `个细分知识点 · ${META.chapters.length} 章`],
      [avg, "细分点平均命中"],
    ].map(([n, l], i) => `<div class="stat-card"><div class="num${i === 1 ? " word" : ""}">${n}</div><div class="label">${l}</div></div>`).join("");
  }

  function compactYearText(qs, limit = 6) {
    const m = new Map();
    qs.forEach(q => m.set(q.year, (m.get(q.year) || 0) + 1));
    const arr = Array.from(m.entries()).sort((a, b) => b[0] - a[0]);
    const full = arr.map(([y, n]) => `${y} 年 ${n} 题`).join("、");
    const shown = arr.slice(0, limit).map(([y, n]) => `${y}×${n}`).join("、");
    return { text: shown + (arr.length > limit ? ` 等 ${arr.length} 年` : ""), full };
  }

  function subTypeText(qs) {
    return TYPES.map(t => [t, qs.filter(q => q.type === t).length])
      .filter(([, n]) => n).map(([t, n]) => `${t}${n}`).join(" · ");
  }

  function subRepIds(qs) {
    return qs.slice().sort((a, b) => b.year - a.year || a._order - b._order).slice(0, 3)
      .map(q => `<span class="rep-id" title="${esc(q.text.slice(0, 45))}">${esc(q.id)}</span>`).join("");
  }

  function renderChapterTable() {
    const rows = META.chapters.map(c => {
      const subs = c.subs.map(s => s.code);
      const hits = subs.reduce((a, code) => a + (subCount.get(code) || 0), 0);
      const qs = QS.filter(q => q.kp.includes(c.code));
      const top = c.subs.slice().sort((a, b) => (subCount.get(b.code) || 0) - (subCount.get(a.code) || 0))[0];
      return { c, hits, qs, top, subs };
    });
    const max = Math.max(1, ...rows.map(r => r.hits));
    const totalHits = rows.reduce((a, r) => a + r.hits, 0);
    const body = rows.map(r => {
      const share = totalHits ? (r.hits / totalHits * 100).toFixed(1) : "0.0";
      const w = Math.max(2, r.hits / max * 100);
      return `<tr class="row-click" data-kp="${r.c.code}">
        <td><b>${r.c.code}</b> ${esc(r.c.name)}</td>
        <td class="num">${r.subs.length}</td>
        <td class="num">${r.qs.length}</td>
        <td class="num"><span class="cell-bar"><i style="width:${w}%"></i></span>${r.hits}</td>
        <td class="num">${share}%</td>
        <td>${r.top ? `<span class="kp-code">${r.top.code}</span>${esc(r.top.name)}` : "—"}</td>
        <td class="type-cell">${subTypeText(r.qs) || "—"}</td>
      </tr>`;
    }).join("");
    const foot = `<tr class="total-row"><td>合计</td><td class="num">${META.subs.length}</td><td class="num">${QS.length}</td><td class="num">${totalHits}</td><td class="num">100%</td><td colspan="2">${META.chapters.length} 章 · ${TOTAL_SUB_HITS} 次标注</td></tr>`;
    $("#chapterTable").innerHTML = `<thead><tr><th>章节</th><th class="num">知识点</th><th class="num">题数</th><th class="num">标注次数</th><th class="num">占比</th><th>最高频知识点</th><th>题型构成</th></tr></thead><tbody>${body}${foot}</tbody>`;
    $$("#chapterTable tr[data-kp]").forEach(tr => tr.onclick = () => goBank({ kp: tr.dataset.kp, clear: true }));
  }

  function renderKpTableFilters() {
    const chapItems = [["__all", TOTAL_SUB_HITS]].concat(META.chapters.map(c => [
      c.code, c.subs.reduce((a, s) => a + (subCount.get(s.code) || 0), 0)
    ]));
    renderChips($("#kpTableChapters"), chapItems, new Set([state.kpTable.chapter]), v => {
      state.kpTable.chapter = v === "__all" ? "all" : v;
      renderKpTableFilters(); renderKpTable();
    }, v => v === "__all" ? "全部章节" : `${v} ${CH.get(v)}`);
    const inp = $("#kpSearch");
    if (inp) inp.oninput = e => { state.kpTable.q = e.target.value; renderKpTable(); };
    const sel = $("#kpSort");
    if (sel) {
      sel.value = state.kpTable.sort;
      sel.onchange = e => { state.kpTable.sort = e.target.value; renderKpTable(); };
    }
  }

  function renderKpTable() {
    const st = state.kpTable;
    const needle = st.q.trim().toLowerCase();
    let arr = META.subs.filter(s =>
      (st.chapter === "all" || s.chap === st.chapter) &&
      (!needle || (s.code + " " + s.name).toLowerCase().includes(needle))
    );
    const order = new Map(META.chapters.map((c, i) => [c.code, i]));
    arr.sort((a, b) => {
      const ca = subCount.get(a.code) || 0, cb = subCount.get(b.code) || 0;
      if (st.sort === "count-asc") return ca - cb || a.code.localeCompare(b.code);
      if (st.sort === "code") return (order.get(a.chap) - order.get(b.chap)) || a.code.localeCompare(b.code);
      if (st.sort === "name") return a.name.localeCompare(b.name, "zh");
      return cb - ca || a.code.localeCompare(b.code);
    });
    const max = Math.max(1, ...arr.map(s => subCount.get(s.code) || 0));
    const rows = arr.map((s, i) => {
      const qs = SUB_QS.get(s.code) || [];
      const n = subCount.get(s.code) || 0;
      const cy = compactYearText(qs, 5);
      const w = Math.max(2, n / max * 100);
      const share = TOTAL_SUB_HITS ? (n / TOTAL_SUB_HITS * 100).toFixed(1) : "0.0";
      return `<tr class="row-click" data-sub="${s.code}">
        <td class="num">${i + 1}</td>
        <td><span class="kp-code">${s.code}</span>${esc(s.name)}</td>
        <td class="chapter-name">${s.chap} ${esc(CH.get(s.chap) || "")}</td>
        <td class="num"><span class="cell-bar"><i style="width:${w}%"></i></span>${n}</td>
        <td class="num">${share}%</td>
        <td class="year-cell" title="${esc(cy.full)}">${esc(cy.text) || "—"}</td>
        <td class="type-cell">${subTypeText(qs) || "—"}</td>
        <td class="rep-cell">${subRepIds(qs) || "—"}</td>
      </tr>`;
    }).join("");
    $("#kpTable").innerHTML = `<thead><tr><th class="num">#</th><th>知识点</th><th>章节</th><th class="num">题数</th><th class="num">标注占比</th><th>出现年份</th><th>题型</th><th>代表题</th></tr></thead><tbody>${rows}</tbody>`;
    $("#kpTableCount").textContent = `显示 ${arr.length} / ${META.subs.length} 个知识点 · 共 ${arr.reduce((a, s) => a + (subCount.get(s.code) || 0), 0)} 次标注 · 表内滚动查看全部`;
    $$("#kpTable tr[data-sub]").forEach(tr => tr.onclick = () => goBank({ sub: tr.dataset.sub, clear: true }));
  }

  function renderTopSubChart() {
    const items = Array.from(subCount.entries()).sort((a, b) => b[1] - a[1]).slice(0, 20)
      .map(([code, n]) => [`${code} ${SUBS.get(code).name}`, n, code]);
    const max = items[0] ? items[0][1] : 1;
    $("#topSubChart").innerHTML = barRows(items, max, { click: true });
    $$("#topSubChart .barrow").forEach(el => el.onclick = () => goBank({ sub: el.dataset.key, clear: true }));
  }

  function renderBucketChart() {
    const buckets = [
      ["0 次（未考）", 0],
      ["1—2 次", 0],
      ["3—5 次", 0],
      ["6—10 次", 0],
      ["11—20 次", 0],
      ["20 次以上", 0],
    ];
    META.subs.forEach(s => {
      const n = subCount.get(s.code) || 0;
      const i = n === 0 ? 0 : n <= 2 ? 1 : n <= 5 ? 2 : n <= 10 ? 3 : n <= 20 ? 4 : 5;
      buckets[i][1]++;
    });
    const max = Math.max(1, ...buckets.map(b => b[1]));
    $("#bucketChart").innerHTML = barRows(buckets.map(([l, v]) => [l, v]), max) +
      `<div class="chart-note">共 ${META.subs.length} 个二级知识点；数值为落在该频次区间的知识点个数。</div>`;
  }

  function renderDonut(sel, items, total, center, unit) {
    let a = -Math.PI / 2;
    const paths = items.map(([, v], i) => {
      const a1 = a + (v / total) * Math.PI * 2;
      const path = svgArc(80, 80, 58, a, Math.max(a + 0.004, a1), COLORS[i % COLORS.length]);
      a = a1;
      return path;
    }).join("");
    $(sel).innerHTML = `<div class="donut-wrap">
      <svg class="donut" viewBox="0 0 160 160">
        <circle cx="80" cy="80" r="58" stroke="#efe9dd" stroke-width="26" fill="none"/>
        ${paths}
        <text x="80" y="76" text-anchor="middle" font-size="26" font-family="Georgia, serif" fill="#1d4c63">${center}</text>
        <text x="80" y="94" text-anchor="middle" font-size="12" fill="#7c8a92">${unit}</text>
      </svg>
      <div class="donut-legend">${items.map(([t, v], i) => `<div><i style="background:${COLORS[i % COLORS.length]}"></i>${esc(t)}<b>${v}</b> <span style="color:#7c8a92">${Math.round(v / total * 100)}%</span></div>`).join("")}</div>
    </div>`;
  }

  function renderTypeStats() {
    const items = TYPES.map(t => [t, typeCount.get(t) || 0]).filter(i => i[1]);
    renderDonut("#typeChartStats", items, QS.length, QS.length, "道题");
  }

  function renderChapterTypeMatrix() {
    const types = TYPES;
    const max = Math.max(1, ...META.chapters.flatMap(c => types.map(t => QS.filter(q => q.kp.includes(c.code) && q.type === t).length)));
    const head = `<tr><th class="rowh">章节</th>${types.map(t => `<th>${t}</th>`).join("")}<th>合计</th></tr>`;
    const rows = META.chapters.map(c => {
      const cells = types.map(t => {
        const v = QS.filter(q => q.kp.includes(c.code) && q.type === t).length;
        const alpha = v ? 0.12 + 0.6 * (v / max) : 0;
        return `<td class="n ${v ? "" : "zero"}" style="${v ? `background:rgba(29,76,99,${alpha.toFixed(2)});color:${alpha > .45 ? "#fff" : "#1c2b36"}` : ""}" data-k="${c.code}" data-t="${t}">${v || "·"}</td>`;
      }).join("");
      const sum = QS.filter(q => q.kp.includes(c.code)).length;
      return `<tr><th class="rowh">${c.code} ${c.name}</th>${cells}<td class="n"><b>${sum}</b></td></tr>`;
    }).join("");
    const totals = types.map(t => QS.filter(q => q.type === t).length);
    const foot = `<tr><th class="rowh">合计</th>${totals.map(v => `<td class="n"><b>${v}</b></td>`).join("")}<td class="n"><b>${QS.length}</b></td></tr>`;
    $("#chapterTypeMatrix").innerHTML = `<table class="heat matrix"><thead>${head}</thead><tbody>${rows}${foot}</tbody></table>`;
    $$("#chapterTypeMatrix td[data-k]").forEach(td => td.onclick = () => {
      if (td.classList.contains("zero")) return;
      goBank({ kp: td.dataset.k, type: td.dataset.t, clear: true });
    });
  }

  function renderYearTable() {
    const rows = YEARS.map(y => {
      const qs = QS.filter(q => q.year === y);
      const counts = TYPES.map(t => qs.filter(q => q.type === t).length);
      const tags = qs.reduce((a, q) => a + q.subs.length, 0);
      const kpc = new Map();
      qs.forEach(q => q.kp.forEach(k => kpc.set(k, (kpc.get(k) || 0) + 1)));
      const top = Array.from(kpc.entries()).sort((a, b) => b[1] - a[1])[0];
      return `<tr class="row-click" data-year="${y}">
        <td><b>${y}</b></td>
        <td class="num">${qs.length}</td>
        ${counts.map(v => `<td class="num">${v || "·"}</td>`).join("")}
        <td class="num">${tags}</td>
        <td class="num">${kpc.size}</td>
        <td>${top ? `<span class="kp-code">${top[0]}</span>${esc(CH.get(top[0]) || "")} <span class="muted">${top[1]}</span>` : "—"}</td>
      </tr>`;
    }).join("");
    const totals = TYPES.map(t => typeCount.get(t) || 0);
    const foot = `<tr class="total-row"><td>合计</td><td class="num">${QS.length}</td>${totals.map(v => `<td class="num">${v}</td>`).join("")}<td class="num">${TOTAL_SUB_HITS}</td><td class="num">${META.chapters.length}</td><td>${YEARS.length} 套</td></tr>`;
    $("#yearTable").innerHTML = `<thead><tr><th>年份</th><th class="num">题数</th>${TYPES.map(t => `<th class="num">${t}</th>`).join("")}<th class="num">知识点标注</th><th class="num">覆盖章节</th><th>高频章节</th></tr></thead><tbody>${rows}${foot}</tbody>`;
    $$("#yearTable tr[data-year]").forEach(tr => tr.onclick = () => goBank({ year: tr.dataset.year, clear: true }));
  }

  function renderKpBar() {
    const items = Array.from(kpCount.entries()).sort((a, b) => b[1] - a[1])
      .map(([k, v]) => [CH.get(k), v, k]);
    const max = items[0] ? items[0][1] : 1;
    $("#kpBarChart").innerHTML = barRows(items, max, { click: true, kind: "kp" });
    $$("#kpBarChart .barrow").forEach(el => el.onclick = () => goBank({ kp: el.dataset.key }));
  }

  function renderSubGroups() {
    const opened = new Set(["E", "C", "I", "L", "K"]);
    $("#subGroups").innerHTML = META.chapters.map(c => {
      const subs = c.subs.slice().sort((a, b) => (subCount.get(b.code) || 0) - (subCount.get(a.code) || 0));
      const total = subs.reduce((a, s) => a + (subCount.get(s.code) || 0), 0);
      const max = Math.max(1, ...subs.map(s => subCount.get(s.code) || 0));
      const body = subs.map(s => {
        const n = subCount.get(s.code) || 0;
        const w = Math.max(2, (n / max) * 100);
        return `<div class="subrow click" data-sub="${s.code}">
          <span class="sname"><b>${s.code}</b> ${s.name}</span>
          <span class="strack"><i style="width:${w}%"></i></span>
          <span class="sval">${n}</span>
        </div>`;
      }).join("");
      return `<details class="subgroup" ${opened.has(c.code) ? "open" : ""}>
        <summary><span class="gname">${c.code} ${c.name}</span><span class="gmeta">${subs.length} 个细分点 · ${total} 次</span></summary>
        <div class="subbody">${body}</div>
      </details>`;
    }).join("");
    $$("#subGroups .subrow").forEach(el => el.onclick = () => goBank({ sub: el.dataset.sub }));
  }

  function renderHeatmap() {
    const byKpYear = new Map();
    QS.forEach(q => q.kp.forEach(k => {
      const key = k + "|" + q.year;
      byKpYear.set(key, (byKpYear.get(key) || 0) + 1);
    }));
    let max = 1;
    byKpYear.forEach(v => { max = Math.max(max, v); });
    const head = `<tr><th class="rowh">章节 \\ 年份</th>${YEARS.map(y => `<th>${y}</th>`).join("")}<th>合计</th></tr>`;
    const rows = META.chapters.map(c => {
      const cells = YEARS.map(y => {
        const v = byKpYear.get(c.code + "|" + y) || 0;
        const alpha = v ? 0.12 + 0.6 * (v / max) : 0;
        return `<td class="n ${v ? "" : "zero"}" style="${v ? `background:rgba(29,76,99,${alpha.toFixed(2)});color:${alpha > .45 ? "#fff" : "#1c2b36"}` : ""}" data-y="${y}" data-k="${c.code}">${v || "·"}</td>`;
      }).join("");
      return `<tr><th class="rowh">${c.code} ${c.name}</th>${cells}<td class="n"><b>${kpCount.get(c.code) || 0}</b></td></tr>`;
    }).join("");
    $("#heatmap").innerHTML = `<table class="heat"><thead>${head}</thead><tbody>${rows}</tbody></table>`;
    $$("#heatmap td[data-k]").forEach(td => td.onclick = () => {
      if (td.classList.contains("zero")) return;
      state.kps = new Set([td.dataset.k]); state.subs.clear(); state.years = new Set([td.dataset.y]); state.page = 1;
      state.view = "bank"; syncTabs(); renderFilters(); renderList(); renderResultCount();
      pushHash("bank");
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  function renderTrend() {
    const items = META.chapters.map(c => [c.name, kpCount.get(c.code) || 0, c.code]);
    renderChips($("#trendChips"), items.map(i => [i[2], i[1]]), new Set([state.trendKp]), v => {
      state.trendKp = v; renderTrend();
    }, v => CH.get(v));
    const vals = YEARS.map(y => QS.filter(q => q.year === y && q.kp.includes(state.trendKp)).length);
    const max = Math.max(1, ...vals);
    const W = 1060, H = 220, PAD = 34;
    const step = YEARS.length > 1 ? (W - PAD * 2) / (YEARS.length - 1) : 0;
    const pts = vals.map((v, i) => [PAD + i * step, H - 30 - (v / max) * (H - 70)]);
    const d = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
    const dots = pts.map((p, i) => `<g><circle cx="${p[0]}" cy="${p[1]}" r="4" fill="#b84c33"/>
      <text x="${p[0]}" y="${p[1] - 12}" text-anchor="middle" font-size="11" fill="#43545f">${vals[i] || ""}</text></g>`).join("");
    const labels = YEARS.map((y, i) => `<text x="${PAD + i * step}" y="${H - 8}" text-anchor="middle" font-size="11" fill="#7c8a92">${y}</text>`).join("");
    $("#trendChart").innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto">
      <line x1="${PAD}" y1="${H - 30}" x2="${W - PAD}" y2="${H - 30}" stroke="#ded5c5"/>
      <path d="${d}" stroke="#1d4c63" stroke-width="2.4" fill="none" stroke-linejoin="round"/>
      ${dots}${labels}
    </svg>`;
  }

  /* ---------------- 扩展题 ---------------- */
  function extSourceLabels() {
    const labels = new Set();
    EXT_QS.forEach(e => (e.sources || []).forEach(s => labels.add(s.label)));
    return Array.from(labels);
  }

  function extRefText(r) {
    const sec = String(r.section || "").replace(/第\s*\d+\s*题\s*$/, "").trim();
    return `${r.year} ${sec}第${r.num}题`;
  }

  function extFiltered() {
    const s = state.ext;
    const needle = s.q.trim().toLowerCase();
    return EXT_QS.filter(e => {
      if (s.source !== "all" && !(e.sources || []).some(x => x.label === s.source)) return false;
      if (s.type !== "all" && e.type !== s.type) return false;
      if (s.exam === "exam" && !e.isExam) return false;
      if (s.exam === "none" && e.isExam) return false;
      if (s.chapter !== "all" && !(e.kp || []).includes(s.chapter)) return false;
      if (needle) {
        const hay = (e.text + " " + (e.answer || "") + " " + (e.explanation || "") + " " +
          (e.sources || []).map(x => x.label).join(" ") + " " +
          (e.examRefs || []).map(extRefText).join(" ")).toLowerCase();
        if (!hay.includes(needle)) return false;
      }
      return true;
    });
  }

  function renderExtStats() {
    const exam = EXT_QS.filter(e => e.isExam).length;
    const srcs = extSourceLabels().length;
    const types = countBy(EXT_QS, e => [e.type]);
    const cards = [
      { num: EXT_QS.length, label: "道扩展题 · 独立于真题题库" },
      { num: exam, label: "道标注为历年真题" },
      { num: srcs, label: "个资料来源" },
      { num: QS.length, label: "道真题 · 另见题库" },
    ];
    $("#extStatRow").innerHTML = cards.map(c =>
      `<div class="stat-card"><div class="num">${c.num}</div><div class="label">${c.label}</div></div>`).join("");
    $("#extSub").textContent = `共 ${EXT_QS.length} 道扩展题（选择 ${types.get("选择") || 0}、简答 ${types.get("简答") || 0}），` +
      `独立于 ${QS.length} 条真题；其中 ${exam} 道在历年真题中出现过，卡片会标注全部年份与原卷题号。`;
  }

  function renderExtFilters() {
    const s = state.ext;
    const sources = extSourceLabels().map(label => {
      const n = EXT_QS.filter(e => (e.sources || []).some(x => x.label === label)).length;
      return [label, n];
    }).sort((a, b) => b[1] - a[1]);
    renderChips($("#extSourceChips"), [["全部", EXT_QS.length]].concat(sources),
      new Set([s.source === "all" ? "全部" : s.source]),
      v => { s.source = v === "全部" ? "all" : v; s.page = 1; renderExtFilters(); renderExtList(); },
      v => v);

    const typeItems = ["选择", "简答"].filter(t => EXT_QS.some(e => e.type === t))
      .map(t => [t, EXT_QS.filter(e => e.type === t).length]);
    renderChips($("#extTypeChips"), [["全部", EXT_QS.length]].concat(typeItems),
      new Set([s.type === "all" ? "全部" : s.type]),
      v => { s.type = v === "全部" ? "all" : v; s.page = 1; renderExtFilters(); renderExtList(); },
      v => v);

    renderChips($("#extExamChips"),
      [["全部", EXT_QS.length], ["考过的真题", EXT_QS.filter(e => e.isExam).length], ["未考过", EXT_QS.filter(e => !e.isExam).length]],
      new Set([s.exam === "all" ? "全部" : s.exam === "exam" ? "考过的真题" : "未考过"]),
      v => { s.exam = v === "全部" ? "all" : v === "考过的真题" ? "exam" : "none"; s.page = 1; renderExtFilters(); renderExtList(); },
      v => v);

    const chapCount = countBy(EXT_QS, e => e.kp || []);
    renderChips($("#extChapterChips"), [["全部", EXT_QS.length]].concat(
      META.chapters.filter(c => chapCount.get(c.code)).map(c => [c.code, chapCount.get(c.code)])
    ), new Set([s.chapter === "all" ? "全部" : s.chapter]),
      v => { s.chapter = v === "全部" ? "all" : v; s.page = 1; renderExtFilters(); renderExtList(); },
      v => v === "全部" ? "全部章节" : `${v} ${CH.get(v)}`);
  }

  function extCard(e) {
    const opts = e.options.length
      ? `<div class="options">${e.options.map((o, i) => `<div class="option"><span class="okey">${"ABCD"[i] || ""}</span><span>${esc(o)}</span></div>`).join("")}</div>`
      : "";
    const srcLabel = (e.sources || []).map(s => `${s.label} 第${s.no}题`).join("；");
    const refs = (e.examRefs || []).slice().sort((a, b) => a.year - b.year || String(a.num).localeCompare(String(b.num)));
    const refHtml = refs.length
      ? `<button class="ext-exam" type="button" data-ext-year="${refs[0].year}" title="点击查看该年份真题"><b>真题</b>${refs.map(extRefText).join("、")}</button>`
      : "";
    return `<article class="qcard ext-card" id="ext-${esc(e.id)}">
      <div class="qhead">
        <span class="qid">${esc(e.id)}</span>
        <span class="qtype">${esc(e.type)}题</span>
        <span class="ext-badge">扩展</span>
        ${e.isExam ? refHtml : ""}
      </div>
      <div class="qtext">${esc(e.text)}</div>
      ${opts}
      <div class="qfoot">
        <span class="ext-source">来源：${esc(srcLabel)}</span>
        <span class="kptag">${esc(CH.get((e.kp || [])[0]) || "")}</span>
      </div>
      <div class="qanswer">
        <button class="qanswer-toggle" type="button" aria-expanded="false" data-ext-answer>查看答案 <span class="chev">▾</span></button>
        <div class="qanswer-body" hidden>
          ${e.answer ? `<div class="ans-sec"><div class="ans-label">答案</div><div class="ans-text">${esc(e.answer).replace(/\n/g, "<br>")}</div></div>` : `<div class="ans-sec"><div class="ans-label">答案</div><div class="ans-text">该资料未提供答案。</div></div>`}
          ${e.explanation ? `<div class="ans-sec"><div class="ans-label">解析</div><div class="ans-text">${esc(e.explanation).replace(/\n/g, "<br>")}</div></div>` : ""}
        </div>
      </div>
    </article>`;
  }

  function renderExtList() {
    const arr = extFiltered();
    const slice = arr.slice(0, state.ext.page * state.ext.pageSize);
    $("#extList").innerHTML = slice.map(extCard).join("") ||
      `<div class="panel" style="text-align:center;color:#7c8a92">没有匹配的扩展题，试试清空筛选条件。</div>`;
    const more = $("#extLoadMore");
    more.style.display = arr.length > slice.length ? "inline-block" : "none";
    more.textContent = `加载更多（还有 ${arr.length - slice.length} 题）`;
    $("#extCount").textContent = `共 ${arr.length} 道扩展题 · 已显示 ${slice.length} 道`;
    $$("[data-ext-answer]", $("#extList")).forEach(el => el.onclick = () => {
      const body = el.nextElementSibling;
      const open = body.hidden;
      body.hidden = !open;
      el.setAttribute("aria-expanded", String(open));
      el.classList.toggle("open", open);
      if (open) renderMath(body);
    });
    $$("[data-ext-year]", $("#extList")).forEach(el => el.onclick = () => goBank({ year: el.dataset.extYear }));
    renderMath($("#extList"));
  }

  function renderExt() {
    renderExtStats();
    renderExtFilters();
    renderExtList();
  }

  /* ---------------- 专项训练 ---------------- */
  function trainList() {
    const t = state.train;
    if (t.mode === "big") {
      const bt = BIG_TYPES.find(x => x.code === t.big);
      const arr = bt ? bt.ids.map(id => QS_ID.get(id)).filter(Boolean) : [];
      return arr.sort((a, b) => a.year - b.year || a._order - b._order);
    }
    const arr = QS.filter(q => q.kp.includes(t.chapter) && (!t.sub || q.subs.includes(t.sub)))
      .sort((a, b) => a.year - b.year || a._order - b._order);
    return arr;
  }

  function renderTrainPicker() {
    const t = state.train;
    $$("#trainMode .mode-btn").forEach(b => b.classList.toggle("on", b.dataset.mode === t.mode));
    $("#chapterPicker").hidden = t.mode !== "chapter";
    $("#bigPicker").hidden = t.mode !== "big";

    if (t.mode === "chapter") {
      const chapItems = META.chapters.map(c => [c.code, kpCount.get(c.code) || 0]);
      renderChips($("#trainChapters"), chapItems, new Set([t.chapter]), v => {
        t.chapter = v; t.sub = ""; t.active = false;
        renderTrainPicker(); renderTrainIntro();
      }, v => `${v} ${CH.get(v)}`);
      renderChips($("#trainSubs"), [[`__all`, kpCount.get(t.chapter) || 0]].concat(
        META.chapters.find(c => c.code === t.chapter).subs.map(s => [s.code, subCount.get(s.code) || 0])
      ), new Set(t.sub ? [t.sub] : ["__all"]), v => {
        t.sub = v === "__all" ? "" : v; t.active = false;
        renderTrainPicker(); renderTrainIntro();
      }, v => v === "__all" ? "整章（不细分）" : `${v} ${SUBS.get(v).name}`);
      $("#trainSubHint").textContent = t.sub ? `当前：${SUBS.get(t.sub).name}` : "不选则练整章";
    } else {
      const items = BIG_TYPES.map(b => [b.code, b.ids.filter(id => QS_ID.has(id)).length]);
      renderChips($("#bigChips"), items, new Set([t.big]), v => {
        t.big = v; t.active = false;
        renderTrainPicker(); renderTrainIntro();
      }, v => BIG_TYPES.find(b => b.code === v).name);
    }
  }

  function renderTrainIntro() {
    const t = state.train;
    const list = trainList();
    const years = Array.from(new Set(list.map(q => q.year))).sort();
    const types = countBy(list, q => [q.type]);
    const done = list.filter(q => mastered.has(q.id)).length;
    const typeTxt = TYPES.filter(x => types.get(x)).map(x => `${x} ${types.get(x)}`).join(" · ");
    const big = t.mode === "big" ? BIG_TYPES.find(x => x.code === t.big) : null;
    const title = big ? `大题专项 · ${big.name}` : `${t.chapter} ${CH.get(t.chapter)}${t.sub ? " › " + SUBS.get(t.sub).name : ""}`;
    const desc = big
      ? `${big.desc} 已汇总 ${years.length} 个年份共 ${list.length} 道同类题，按年份先后排列。`
      : `从 ${years.length} 个年份的套卷中抽取出 ${list.length} 道同类题目${t.sub ? "（同一细分考点）" : "（覆盖该章全部考点）"}，按年份先后排列，适合集中突破。`;
    $("#trainIntro").innerHTML = `
      <div class="intro-grid">
        <div>
          <div class="eyebrow">${big ? "跨年份大题整合" : "专项题组"}</div>
          <h2 class="intro-title">${title}</h2>
          <p class="intro-desc">${desc}</p>
          <div class="intro-tags">
            ${years.map(y => `<span class="yr">${y}</span>`).join("")}
          </div>
        </div>
        <div class="intro-metrics">
          <div><b>${list.length}</b><span>题量</span></div>
          <div><b>${years.length}</b><span>覆盖年份</span></div>
          <div><b>${done}</b><span>已掌握</span></div>
        </div>
      </div>
      <div class="intro-types">${typeTxt}</div>
      <div class="intro-actions">
        <button class="btn primary" id="trainStart" ${list.length ? "" : "disabled"}>${list.length ? "开始训练" : "该题型暂无题目"}</button>
        <button class="btn ghost" id="trainShuffle" ${list.length > 1 ? "" : "disabled"}>乱序训练</button>
      </div>`;
    const start = $("#trainStart");
    if (start) start.onclick = () => startTrain(false);
    const sh = $("#trainShuffle");
    if (sh) sh.onclick = () => startTrain(true);
  }

  function startTrain(shuffle) {
    const t = state.train;
    let list = trainList();
    if (shuffle) {
      list = list.slice();
      for (let i = list.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [list[i], list[j]] = [list[j], list[i]];
      }
    }
    t.list = list; t.i = 0; t.active = true;
    $("#trainIntro").hidden = true;
    $(".train-picker").hidden = true;
    $("#trainSession").hidden = false;
    $(".train-controls").style.display = "";
    renderTrainQ();
    pushHash("train-session");
  }

  function renderTrainQ() {
    const t = state.train;
    const q = t.list[t.i];
    if (!q) return;
    $("#trainCard").innerHTML = questionCard(q);
    bindMistakeButtons($("#trainCard"));
    $("#trainPos").textContent = `第 ${t.i + 1} / ${t.list.length} 题 · ${q.year} 年`;
    $("#trainBar").style.width = `${((t.i + 1) / t.list.length) * 100}%`;
    const btn = $("#trainMaster");
    const isDone = mastered.has(q.id);
    btn.textContent = isDone ? "取消已掌握" : "标记已掌握";
    btn.classList.toggle("primary", !isDone);
    btn.classList.toggle("ghost", isDone);
    const ansVers = availableAnswerVersions(q.year);
    $("#trainAnswer").disabled = !ansVers.length;
    $("#trainAnswer").style.opacity = ansVers.length ? 1 : .45;
    $("#trainAnswer").textContent = ansVers.length
      ? `参考答案${ansVers.length > 1 ? "（双版本）" : ""}`
      : "整卷扫描答案未附";
    $("#trainPrev").disabled = t.i === 0;
    $("#trainNext").textContent = t.i === t.list.length - 1 ? "完成训练" : "下一题";
    bindCardEvents($("#trainCard"));
    renderMath($("#trainCard"));
  }

  function bindCardEvents(root) {
    $$(".qfig", root).forEach(el => el.onclick = () => openLightbox(el.dataset.src, el.dataset.title));
    $$(".anslink[data-ans]", root).forEach(el => el.onclick = () => {
      const y = el.dataset.ans;
      if (availableAnswerVersions(y).length) openAnswerLightbox(y, 0, state.answerVersion);
    });
    $$(".kptag[data-kp]", root).forEach(el => el.onclick = () => goBank({ kp: el.dataset.kp }));
    $$(".kptag[data-sub]", root).forEach(el => el.onclick = () => goBank({ sub: el.dataset.sub }));
    $$(".qanswer-toggle", root).forEach(el => el.onclick = () => {
      const body = el.nextElementSibling;
      const open = body.hidden;
      body.hidden = !open;
      el.setAttribute("aria-expanded", String(open));
      el.classList.toggle("open", open);
    });
  }

  function masterCurrent() {
    const t = state.train;
    const q = t.list[t.i];
    if (!q) return;
    if (mastered.has(q.id)) mastered.delete(q.id);
    else mastered.add(q.id);
    saveMastered();
    renderTrainQ();
    renderTrainIntro();
  }

  function finishTrain() {
    const t = state.train;
    const done = t.list.filter(q => mastered.has(q.id)).length;
    $(".train-controls").style.display = "none";
    $("#trainBar").style.width = "100%";
    $("#trainPos").textContent = "训练完成";
    $("#trainCard").innerHTML = `<div class="train-done">
      <div class="eyebrow">本轮结束</div>
      <h2>完成 ${t.list.length} 道专项题</h2>
      <p>已掌握 <b>${done}</b> 题，待复习 <b>${t.list.length - done}</b> 题。掌握状态已保存在本机。</p>
      <div class="intro-actions">
        <button class="btn primary" id="trainAgain">再练一轮</button>
        <button class="btn ghost" id="trainBack">换个专题</button>
      </div>
    </div>`;
    $("#trainAgain").onclick = () => { $(".train-controls").style.display = ""; startTrain(false); };
    $("#trainBack").onclick = exitTrain;
  }

  function exitTrain() {
    if (location.hash === "#train-session") {
      history.back();
      return;
    }
    state.train.active = false;
    $("#trainSession").hidden = true;
    $("#trainIntro").hidden = false;
    $(".train-picker").hidden = false;
    renderTrainIntro();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function showTrainPicker() {
    state.train.active = false;
    $("#trainSession").hidden = true;
    $("#trainIntro").hidden = false;
    $(".train-picker").hidden = false;
  }

  function showTrainSession() {
    state.train.active = true;
    $("#trainSession").hidden = false;
    $("#trainIntro").hidden = true;
    $(".train-picker").hidden = true;
  }

  function trainPrev() {
    if (state.train.i > 0) { state.train.i -= 1; renderTrainQ(); }
  }
  function trainNext() {
    const t = state.train;
    if (t.i < t.list.length - 1) { t.i += 1; renderTrainQ(); }
    else finishTrain();
  }

  /* ---------------- 选择题刷题 ---------------- */
  function quizPool() { return QS.filter(q => q.type === "选择" && QUIZ[q.id]); }

  function quizFiltered() {
    const z = state.quiz;
    return quizPool().filter(q =>
      (z.year === "all" || String(q.year) === z.year) &&
      (z.scope === "all" || (z.scope === "undone" ? !quizRec[q.id] : quizRec[q.id] && !quizRec[q.id].ok))
    ).sort((a, b) => a.year - b.year || a._order - b._order);
  }

  function buildQuizOrder() {
    let arr = quizFiltered();
    if (state.quiz.shuffled) {
      arr = arr.slice();
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
    }
    state.quiz.order = arr.map(q => q.id);
    state.quiz.i = Math.min(state.quiz.i, Math.max(0, arr.length - 1));
    state.quiz.picks = [];
  }

  function quizAnswerLetters(item) {
    const correct = Array.isArray(item.a) ? item.a : [item.a];
    return correct.map(i => "ABCD"[i] || "").join("、");
  }

  function renderQuizFilters() {
    const z = state.quiz;
    const years = Array.from(new Set(quizPool().map(q => String(q.year)))).sort();
    const items = [["all", quizPool().length]].concat(years.map(y => [y, quizPool().filter(q => String(q.year) === y).length]));
    renderChips($("#quizYears"), items, new Set([z.year]), v => {
      z.year = v; z.i = 0; buildQuizOrder(); renderQuiz();
    }, v => v === "all" ? "全部年份" : `${v} 年`);

    const base = quizPool().filter(q => z.year === "all" || String(q.year) === z.year);
    const undone = base.filter(q => !quizRec[q.id]).length;
    const wrong = base.filter(q => quizRec[q.id] && !quizRec[q.id].ok).length;
    renderChips($("#quizScope"), [["all", base.length], ["undone", undone], ["wrong", wrong]],
      new Set([z.scope]), v => {
        z.scope = v; z.i = 0; buildQuizOrder(); renderQuiz();
      }, v => v === "all" ? "全部" : v === "undone" ? "未做" : "错题");
  }

  function renderQuizProgress() {
    const pool = quizPool();
    const answered = pool.filter(q => quizRec[q.id]);
    const right = answered.filter(q => quizRec[q.id].ok);
    const wrong = answered.length - right.length;
    const rate = answered.length ? Math.round((right.length / answered.length) * 100) : 0;
    const allDone = pool.length && answered.length === pool.length;
    $("#quizProgress").innerHTML = `
      <div class="quiz-progress-head">
        <div><b>已答 ${answered.length}</b> / ${pool.length} 题</div>
        <div class="quiz-progress-nums">正确 <b>${right.length}</b> · 正确率 <b>${rate}%</b> · 错题 <b class="bad">${wrong}</b></div>
      </div>
      <div class="train-progress"><i style="width:${(answered.length / pool.length) * 100}%"></i></div>
      ${allDone ? `<div class="quiz-done-tip">全部 ${pool.length} 道选择题已完成，可切到“错题”范围复习。</div>` : ""}`;
  }

  function renderQuizCard() {
    if (!state.quiz.order.length) buildQuizOrder();
    const z = state.quiz;
    const id = z.order[z.i];
    if (!id) {
      $("#quizCard").innerHTML = `<div class="panel quiz-empty">当前范围没有题目，试试切换年份或范围。</div>`;
      $("#quizPrev").disabled = true;
      $("#quizNext").disabled = true;
      $("#quizAnswer").disabled = true;
      return;
    }
    const q = QS_ID.get(id);
    const item = QUIZ[id];
    const rec = quizRec[id];
    const isMulti = Array.isArray(item.a);
    const correct = Array.isArray(item.a) ? item.a : [item.a];
    const picked = rec ? rec.p : z.picks;
    const letters = quizAnswerLetters(item);

    const opts = q.options.map((o, i) => {
      let cls = "qopt";
      if (rec) {
        if (correct.indexOf(i) >= 0) cls += " correct";
        else if (picked.indexOf(i) >= 0) cls += " wrong";
        else cls += " muted";
      } else if (picked.indexOf(i) >= 0) cls += " picked";
      return `<button class="${cls}" data-i="${i}" ${rec ? "disabled" : ""}>
        <span class="okey">${"ABCD"[i]}</span><span class="otext">${highlight(o)}</span></button>`;
    }).join("");

    const figs = q.figs.map(f => f.images.map(src =>
      `<figure class="qfig" data-src="assets/figs/${src}" data-title="${q.year} 年第 ${q.num} 题 原图">
        <img src="assets/figs/${src}" loading="lazy" alt="${q.year} 年第 ${q.num} 题原图">
      </figure>`).join("")).join("");

    const chapTags = q.kp.map(k => `<span class="kptag">${CH.get(k)}</span>`).join("");
    const subTags = q.subs.map(s => `<span class="kptag sub">${s} ${SUBS.get(s).name}</span>`).join("");

    let feedback = "";
    if (rec) {
      feedback = `<div class="quiz-feedback ${rec.ok ? "ok" : "bad"}">
        <div class="fb-head">${rec.ok ? "回答正确" : "回答错误"}<span>正确答案：${letters}</span></div>
        ${item.fix ? `<div class="fb-fix">已校正原答案：${item.fix}</div>` : ""}
        <div class="fb-body">${item.e}</div>
        <div class="fb-foot">${chapTags}${subTags}<button class="btn ghost small" id="quizRetry">重做本题</button></div>
      </div>`;
    } else if (isMulti) {
      feedback = `<div class="quiz-feedback hint">
        本题为多选，需选出 ${item.m || correct.length} 项，已选 ${picked.length} 项。
        <button class="btn primary small" id="quizSubmit" ${picked.length === (item.m || correct.length) ? "" : "disabled"}>提交答案</button>
      </div>`;
    }

    $("#quizCard").innerHTML = `<article class="qcard quiz-card">
      <div class="qhead">
        <span class="qid">${q.year} · 选择题 ${q.num}</span>
        <span class="qtype">${isMulti ? "多选" : "单选"}</span>
        ${q.marks ? `<span class="qmarks">${q.marks} 分</span>` : ""}
        <span class="quiz-count">${z.i + 1} / ${z.order.length}</span>
        ${mistakeBtnHTML(q.id, "mini")}
      </div>
      <div class="qtext">${highlight(q.text)}</div>
      ${figs ? `<div class="qfigs">${figs}</div>` : ""}
      <div class="qopts" id="quizOpts">${opts}</div>
      ${feedback}
    </article>`;

    $("#quizPrev").disabled = z.i === 0;
    $("#quizNext").disabled = z.i >= z.order.length - 1;
    const ansVers = availableAnswerVersions(q.year);
    $("#quizAnswer").disabled = !ansVers.length;
    $("#quizAnswer").textContent = ansVers.length
      ? `原卷答案${ansVers.length > 1 ? "（双版本）" : ""}`
      : "整卷扫描答案未附";

    $$("#quizOpts .qopt").forEach(btn => btn.onclick = () => chooseQuizOption(Number(btn.dataset.i)));
    bindMistakeButtons($("#quizCard"));
    const retry = $("#quizRetry");
    if (retry) retry.onclick = () => { delete quizRec[id]; saveQuiz(); renderQuiz(); };
    const sub = $("#quizSubmit");
    if (sub) sub.onclick = () => submitQuiz();
    $$(".qfig", $("#quizCard")).forEach(el => el.onclick = () => openLightbox(el.dataset.src, el.dataset.title));
    renderMath($("#quizCard"));
  }

  function chooseQuizOption(i) {
    const z = state.quiz;
    const id = z.order[z.i];
    if (!id || quizRec[id]) return;
    const item = QUIZ[id];
    if (Array.isArray(item.a)) {
      const max = item.m || item.a.length;
      const k = z.picks.indexOf(i);
      if (k >= 0) z.picks.splice(k, 1);
      else if (z.picks.length < max) z.picks.push(i);
      renderQuizCard();
    } else {
      z.picks = [i];
      submitQuiz();
    }
  }

  function submitQuiz() {
    const z = state.quiz;
    const id = z.order[z.i];
    if (!id) return;
    const item = QUIZ[id];
    if (!z.picks.length) return;
    const correct = Array.isArray(item.a) ? item.a.slice().sort((a, b) => a - b) : [item.a];
    const mine = z.picks.slice().sort((a, b) => a - b);
    const ok = mine.length === correct.length && mine.every((v, i) => v === correct[i]);
    quizRec[id] = { p: mine, ok };
    z.picks = [];
    if (!ok) addMistake(id);
    saveQuiz();
    renderQuiz();
  }

  function quizMove(d) {
    const z = state.quiz;
    const n = z.i + d;
    if (n < 0 || n >= z.order.length) return;
    z.i = n; z.picks = [];
    renderQuizCard();
  }

  function renderQuiz() {
    if (!state.quiz.order.length) buildQuizOrder();
    renderQuizFilters();
    renderQuizProgress();
    renderQuizCard();
  }

  /* ---------------- 错题本 ---------------- */
  function mistakeQs() {
    return mistakeIds.map(id => QS_ID.get(id)).filter(Boolean);
  }

  function mistakeFiltered() {
    const s = state.mistakes;
    return mistakeQs().filter(q =>
      (s.type === "all" || q.type === s.type) &&
      (s.chapter === "all" || q.kp.indexOf(s.chapter) >= 0)
    );
  }

  function renderMistakeFilters() {
    const s = state.mistakes;
    const all = mistakeQs();
    const tc = countBy(all, q => [q.type]);
    const cc = countBy(all, q => q.kp);
    if (s.type !== "all" && !tc.get(s.type)) s.type = "all";
    if (s.chapter !== "all" && !cc.get(s.chapter)) s.chapter = "all";
    renderChips($("#mistakeTypes"),
      [["all", all.length]].concat(TYPES.filter(t => tc.get(t)).map(t => [t, tc.get(t)])),
      new Set([s.type]), v => { s.type = v; renderMistakes(); },
      v => v === "all" ? "全部" : v);
    renderChips($("#mistakeChapters"),
      [["all", all.length]].concat(META.chapters.filter(c => cc.get(c.code)).map(c => [c.code, cc.get(c.code)])),
      new Set([s.chapter]), v => { s.chapter = v; renderMistakes(); },
      v => v === "all" ? "全部" : `${v} ${CH.get(v)}`);
  }

  function renderMistakes() {
    updateMistakeBadge();
    const s = state.mistakes;
    const all = mistakeQs();
    const typeStats = TYPES.map(t => [t, all.filter(q => q.type === t).length]).filter(x => x[1]);
    $("#mistakePractice").disabled = !all.length;
    $("#mistakeClear").disabled = !all.length;
    $("#mistakeCount").textContent = all.length
      ? `共 ${all.length} 题 · ` + typeStats.map(([t, n]) => `${t} ${n}`).join(" · ")
      : "还没有错题：在题目卡片上点“加入错题本”即可收集。";
    if (s.active && !s.list.length) s.active = false;
    $("#mistakeSession").hidden = !s.active;
    $("#mistakeToolbar").hidden = s.active || !all.length;
    $("#mistakeList").hidden = s.active || !all.length;
    $("#mistakeEmpty").hidden = s.active || !!all.length;
    if (s.active) { renderMistakeQ(); return; }
    if (!all.length) { $("#mistakeList").innerHTML = ""; return; }
    renderMistakeFilters();
    const arr = mistakeFiltered();
    $("#mistakeList").innerHTML = arr.map(questionCard).join("") ||
      `<div class="panel" style="text-align:center;color:#7c8a92">当前筛选下没有错题。</div>`;
    bindCardActions($("#mistakeList"));
    renderMath($("#mistakeList"));
  }

  function renderMistakeQ() {
    const s = state.mistakes;
    const q = QS_ID.get(s.list[s.i]);
    if (!q) { exitMistakePractice(false); return; }
    $("#mistakeCard").innerHTML = questionCard(q);
    $$(".mistake-btn", $("#mistakeCard")).forEach(b => b.remove());
    $("#mistakePos").textContent = `第 ${s.i + 1} / ${s.list.length} 题 · ${q.year} 年 · ${q.type}题`;
    $("#mistakeBar").style.width = `${((s.i + 1) / s.list.length) * 100}%`;
    $("#mistakePrev").disabled = s.i === 0;
    $("#mistakeNext").textContent = s.i >= s.list.length - 1 ? "完成重练" : "下一题";
    bindCardActions($("#mistakeCard"));
    renderMath($("#mistakeCard"));
  }

  function startMistakePractice() {
    const s = state.mistakes;
    const arr = mistakeFiltered();
    if (!arr.length) return;
    s.list = arr.map(q => q.id);
    s.i = 0;
    s.active = true;
    renderMistakes();
    pushHash("mistake-session");
  }

  function exitMistakePractice(push = true) {
    const s = state.mistakes;
    s.active = false; s.list = []; s.i = 0;
    renderMistakes();
    if (location.hash === "#mistake-session") {
      if (push) history.back();
      else {
        lastHashApplied = "mistakes";
        try { history.replaceState(null, "", "#mistakes"); }
        catch (e) { location.hash = "mistakes"; }
      }
    }
  }

  function clearMistakes() {
    if (!mistakeIds.length) return;
    if (!confirm(`确定清空错题本？共 ${mistakeIds.length} 题。`)) return;
    mistakeIds = [];
    mistakeSet.clear();
    saveMistakes();
    updateMistakeBadge();
    const s = state.mistakes;
    s.active = false; s.list = []; s.i = 0;
    renderMistakes();
    syncMistakeButtons();
    if (location.hash === "#mistake-session") {
      lastHashApplied = "mistakes";
      try { history.replaceState(null, "", "#mistakes"); } catch (e) { /* ignore */ }
    }
  }

  /* ---------------- answers ---------------- */
  function saveAnswerVersion() {
    try { localStorage.setItem(ANSWER_VER_KEY, state.answerVersion); } catch (e) { /* ignore */ }
  }

  function renderAnswerVersionChips() {
    const keys = Object.keys(ANSWER_VERSIONS).filter(v => v !== "default");
    renderChips($("#answerVersionChips"),
      keys.map(v => [v, (ANSWER_VERSIONS[v].years || []).length]),
      new Set([state.answerVersion]),
      v => { state.answerVersion = v; saveAnswerVersion(); renderAnswerVersionChips(); renderAnswers(); },
      v => answerVerLabel(v));
    const info = ANSWER_VERSIONS[state.answerVersion] || {};
    $("#answerVersionHint").textContent = info.desc || "";
  }

  function renderAnswers() {
    renderAnswerVersionChips();
    const ver = state.answerVersion;
    $("#answerGrid").innerHTML = YEARS.slice().reverse().map(y => {
      const imgs = answerPagesOf(y, ver);
      const other = availableAnswerVersions(y).filter(v => v !== ver);
      const body = imgs.length
        ? `<div class="sheets">${imgs.map((s, i) => `<div class="sheet" data-year="${y}" data-page="${i}" data-src="${answerSrc(y, ver, s)}" data-title="${y} 年参考答案 · ${answerVerLabel(ver)}">
            <img src="${answerSrc(y, ver, s)}" loading="lazy" alt="${y} 年参考答案 ${i + 1}"></div>`).join("")}</div>`
        : `<p class="none">${other.length ? `该版本无此年份答案，可切换到${answerVerLabel(other[0])}。` : "原卷未附参考答案。"}</p>`;
      return `<div class="answer-card"><h3>${y} 年 <span class="ans-pages">${imgs.length} 页 · ${answerVerLabel(ver)}</span></h3>${body}</div>`;
    }).join("");
    $$(".sheet", $("#answerGrid")).forEach(el => el.onclick = () =>
      openAnswerLightbox(el.dataset.year, Number(el.dataset.page) || 0, ver));
  }

  /* ---------------- lightbox / 路由 / nav ---------------- */
  function pushHash(h) {
    lastHashApplied = h;
    if (location.hash === "#" + h) return;
    try { history.pushState(null, "", "#" + h); }
    catch (e) { location.hash = h; }
  }

  function showBox(b) {
    const srcs = b.srcs || [b.src];
    b.i = Math.min(Math.max(b.i || 0, 0), srcs.length - 1);
    $("#lightboxImg").src = srcs[b.i];
    $("#lightboxTitle").textContent = b.title || "";
    const bar = $("#lightboxBar");
    bar.hidden = srcs.length <= 1;
    $("#lightboxPage").textContent = `${b.i + 1} / ${srcs.length}`;
    $("#lightboxPrev").disabled = b.i === 0;
    $("#lightboxNext").disabled = b.i >= srcs.length - 1;

    const vb = $("#lightboxVersions");
    if (b.year) {
      const vs = availableAnswerVersions(b.year);
      vb.hidden = vs.length <= 1;
      vb.innerHTML = vs.map(v => {
        const pages = answerPagesOf(b.year, v);
        const on = v === b.version;
        return `<button class="ver-btn${on ? " on" : ""}" data-ver="${v}">${answerVerLabel(v)}<span>${pages.length} 页</span></button>`;
      }).join("");
      $$(".ver-btn", vb).forEach(el => el.onclick = () => switchAnswerVersion(el.dataset.ver));
    } else {
      vb.hidden = true;
      vb.innerHTML = "";
    }
    $("#lightbox").classList.add("open");
  }
  function hideBox() { $("#lightbox").classList.remove("open"); }
  function openLightbox(src, title) {
    lastBox = { srcs: [src], i: 0, title };
    showBox(lastBox);
    if (location.hash !== "#box") pushHash("box");
  }
  function openAnswerLightbox(year, index = 0, version = state.answerVersion) {
    const vs = availableAnswerVersions(year);
    if (!vs.length) return;
    const ver = vs.indexOf(version) >= 0 ? version : vs[0];
    const imgs = answerPagesOf(year, ver);
    lastBox = {
      year, version: ver,
      srcs: imgs.map(s => answerSrc(year, ver, s)),
      i: Math.min(Math.max(index, 0), imgs.length - 1),
      title: `${year} 年整卷参考答案 · ${answerVerLabel(ver)}`,
    };
    showBox(lastBox);
    if (location.hash !== "#box") pushHash("box");
  }
  function switchAnswerVersion(ver) {
    if (!lastBox || !lastBox.year || !answerPagesOf(lastBox.year, ver).length) return;
    state.answerVersion = ver;
    saveAnswerVersion();
    const imgs = answerPagesOf(lastBox.year, ver);
    lastBox.version = ver;
    lastBox.srcs = imgs.map(s => answerSrc(lastBox.year, ver, s));
    lastBox.i = 0;
    lastBox.title = `${lastBox.year} 年整卷参考答案 · ${answerVerLabel(ver)}`;
    showBox(lastBox);
    renderAnswers();
  }
  function lightboxStep(d) {
    if (!lastBox || !$("#lightbox").classList.contains("open")) return;
    const n = (lastBox.i || 0) + d;
    if (n < 0 || n >= lastBox.srcs.length) return;
    lastBox.i = n;
    showBox(lastBox);
  }
  function closeLightbox() {
    if (location.hash === "#box") history.back();
    else hideBox();
  }

  $("#lightboxClose").onclick = closeLightbox;
  $("#lightboxPrev").onclick = () => lightboxStep(-1);
  $("#lightboxNext").onclick = () => lightboxStep(1);
  $("#lightbox").onclick = e => { if (e.target.id === "lightbox") closeLightbox(); };
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && $("#lightbox").classList.contains("open")) closeLightbox();
    if (e.key === "ArrowLeft") lightboxStep(-1);
    if (e.key === "ArrowRight") lightboxStep(1);
    if (e.key === "/" && document.activeElement !== $("#globalSearch")) {
      e.preventDefault(); $("#globalSearch").focus();
    }
  });

  function syncTabs() {
    $$(".tab").forEach(t => t.classList.toggle("active", t.dataset.view === state.view));
    $$(".view").forEach(v => v.classList.toggle("active", v.id === "view-" + state.view));
  }

  function switchView(v, push = true) {
    state.view = v;
    if (v !== "train") state.train.active = false;
    if (v !== "mistakes") state.mistakes.active = false;
    syncTabs();
    if (v === "train") { showTrainPicker(); renderTrainPicker(); renderTrainIntro(); }
    if (v === "ext") renderExt();
    if (v === "quiz") renderQuiz();
    if (v === "mistakes") renderMistakes();
    if (v === "stats") renderTrend();
    if (v === "answers") renderAnswers();
    if (push) pushHash(v);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function applyHash(h) {
    if (h === "box") {
      if (lastBox) showBox(lastBox);
      return;
    }
    hideBox();
    if (h === "train-session") {
      state.view = "train"; syncTabs();
      if (state.train.list.length) { showTrainSession(); renderTrainQ(); }
      else { showTrainPicker(); renderTrainPicker(); renderTrainIntro(); }
      return;
    }
    if (h === "mistake-session") {
      state.view = "mistakes"; syncTabs();
      if (!state.mistakes.active) {
        lastHashApplied = "mistakes";
        try { history.replaceState(null, "", "#mistakes"); } catch (e) { /* ignore */ }
      }
      renderMistakes();
      return;
    }
    const v = VIEWS.indexOf(h) >= 0 ? h : "overview";
    state.view = v;
    if (v !== "mistakes") state.mistakes.active = false;
    syncTabs();
    if (v === "train") { showTrainPicker(); renderTrainPicker(); renderTrainIntro(); }
    if (v === "ext") renderExt();
    if (v === "quiz") renderQuiz();
    if (v === "mistakes") renderMistakes();
    if (v === "stats") renderTrend();
    if (v === "answers") renderAnswers();
  }

  function onNav() {
    const h = location.hash.slice(1);
    if (h === lastHashApplied) return;
    lastHashApplied = h;
    applyHash(h);
  }
  window.addEventListener("popstate", onNav);
  window.addEventListener("hashchange", onNav);

  $$(".tab").forEach(t => t.onclick = () => switchView(t.dataset.view, true));
  $$("[data-jump]").forEach(b => b.onclick = () => switchView(b.dataset.jump, true));

  /* ---------------- search / filters / sort ---------------- */
  let timer = null;
  $("#globalSearch").addEventListener("input", e => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      state.q = e.target.value; state.page = 1;
      if (state.q && state.view !== "bank") { state.view = "bank"; syncTabs(); pushHash("bank"); }
      renderList(); renderResultCount();
    }, 180);
  });

  $("#sortSelect").onchange = e => {
    state.sort = e.target.value; state.page = 1; renderList();
  };
  $("#resetFilters").onclick = () => {
    state.years.clear(); state.types.clear(); state.kps.clear(); state.subs.clear(); state.q = "";
    $("#globalSearch").value = ""; state.page = 1;
    renderFilters(); renderList(); renderResultCount();
  };
  $("#subSelect").onchange = e => {
    state.subs = e.target.value ? new Set([e.target.value]) : new Set();
    state.page = 1; renderList(); renderResultCount();
  };
  $("#loadMore").onclick = () => { state.page += 1; renderList(); };

  /* 扩展题交互 */
  let extTimer = null;
  $("#extSearch").addEventListener("input", e => {
    clearTimeout(extTimer);
    extTimer = setTimeout(() => {
      state.ext.q = e.target.value;
      state.ext.page = 1;
      renderExtList();
    }, 160);
  });
  $("#resetExtFilters").onclick = () => {
    state.ext = { source: "all", type: "all", exam: "all", chapter: "all", q: "", page: 1, pageSize: 24 };
    $("#extSearch").value = "";
    renderExtFilters(); renderExtList();
  };
  $("#extLoadMore").onclick = () => { state.ext.page += 1; renderExtList(); };

  /* 专项训练交互 */
  $$("#trainMode .mode-btn").forEach(b => b.onclick = () => {
    state.train.mode = b.dataset.mode;
    state.train.active = false;
    $("#trainSession").hidden = true;
    $("#trainIntro").hidden = false;
    $(".train-picker").hidden = false;
    renderTrainPicker(); renderTrainIntro();
  });
  $("#trainExit").onclick = exitTrain;
  $("#trainPrev").onclick = trainPrev;
  $("#trainNext").onclick = trainNext;
  $("#trainMaster").onclick = masterCurrent;
  $("#trainAnswer").onclick = () => {
    const q = state.train.list[state.train.i];
    if (!q) return;
    if (availableAnswerVersions(q.year).length) openAnswerLightbox(q.year, 0, state.answerVersion);
  };

  /* 选择题刷题交互 */
  $("#quizPrev").onclick = () => quizMove(-1);
  $("#quizNext").onclick = () => quizMove(1);
  $("#quizShuffle").onclick = () => {
    state.quiz.shuffled = !state.quiz.shuffled;
    $("#quizShuffle").textContent = state.quiz.shuffled ? "顺序练习" : "乱序练习";
    state.quiz.i = 0; buildQuizOrder(); renderQuiz();
  };
  $("#quizReset").onclick = () => {
    if (!confirm("确定清空所有选择题答题记录？错题本不会被清空。")) return;
    quizRec = {}; saveQuiz(); state.quiz.i = 0; buildQuizOrder(); renderQuiz();
  };
  $("#quizAnswer").onclick = () => {
    const id = state.quiz.order[state.quiz.i];
    if (!id) return;
    const q = QS_ID.get(id);
    if (availableAnswerVersions(q.year).length) openAnswerLightbox(q.year, 0, state.answerVersion);
  };

  /* 错题本交互 */
  $("#mistakePractice").onclick = startMistakePractice;
  $("#mistakeClear").onclick = clearMistakes;
  $("#mistakeExit").onclick = () => exitMistakePractice(true);
  $("#mistakePrev").onclick = () => {
    const s = state.mistakes;
    if (s.i > 0) { s.i -= 1; renderMistakeQ(); }
  };
  $("#mistakeNext").onclick = () => {
    const s = state.mistakes;
    if (s.i >= s.list.length - 1) exitMistakePractice(true);
    else { s.i += 1; renderMistakeQ(); }
  };
  $("#mistakeRemove").onclick = () => {
    const s = state.mistakes;
    const id = s.list[s.i];
    if (id) removeMistake(id);
  };
  document.addEventListener("keydown", e => {
    const tag = (document.activeElement && document.activeElement.tagName) || "";
    if (state.view !== "quiz" || $("#lightbox").classList.contains("open")) return;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
    if (/^[1-4]$/.test(e.key)) { chooseQuizOption(Number(e.key) - 1); return; }
    if (/^[a-dA-D]$/.test(e.key)) { chooseQuizOption("abcd".indexOf(e.key.toLowerCase())); return; }
    if (e.key === "Enter") { submitQuiz(); return; }
    if (e.key === "ArrowLeft") quizMove(-1);
    if (e.key === "ArrowRight") quizMove(1);
  });
  document.addEventListener("keydown", e => {
    if (state.view !== "train" || !state.train.active) return;
    if (e.key === "ArrowLeft") trainPrev();
    if (e.key === "ArrowRight") trainNext();
  });

  /* ---------------- boot ---------------- */
  renderHero();
  renderStats();
  renderYearChart();
  renderTypeChart();
  renderTopKp();
  renderYearStrip();
  renderFilters();
  renderList();
  renderResultCount();
  renderKpStats();
  renderChapterTable();
  renderKpTableFilters();
  renderKpTable();
  renderTopSubChart();
  renderBucketChart();
  renderTypeStats();
  renderChapterTypeMatrix();
  renderYearTable();
  renderKpBar();
  renderSubGroups();
  renderHeatmap();
  renderTrend();
  renderAnswers();
  renderExt();
  renderTrainPicker();
  renderTrainIntro();
  renderQuiz();
  renderMistakes();

  if (location.hash) {
    lastHashApplied = location.hash.slice(1);
    applyHash(lastHashApplied);
  } else {
    try { history.replaceState(null, "", "#overview"); } catch (e) { /* ignore */ }
    lastHashApplied = "overview";
  }
})();
