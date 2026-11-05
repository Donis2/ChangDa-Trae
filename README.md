# 常州大学 855 机械设计基础真题题库

21 套历年真题（2004—2026，缺 2005、2016）的整理、刷题与统计站点，并收录非真题资料中的扩展题与两版整卷答案。

## 目录结构

```text
Trae版本/
├─ 启动题库.bat                 # 双击启动本地题库（自动开本地服务并打开浏览器）
├─ netlify.toml                 # Netlify 部署配置（publish = 常大真题电子版/web）
├─ .gitignore
├─ 常大真题电子版/
│  └─ web/                      # 站点源码：index.html + data + assets
├─ 题目资料来源/                # 本地原始资料母库（Trae 版 + Workbuddy 版，约 470 MB）
│  ├─ Trae/                     # 考研群真题原卷、两版答案、青蛙题库、简答资料
│  └─ Workbuddy/                # 夸克扫描真题、两版答案、教材与大纲
├─ _build/                      # 数据处理脚本与结构化源数据
│  ├─ merge_projects.py         # 两项目题库合并（补题、导入答案/图片）
│  ├─ build_answers.py          # 生成老魏版 / 考研群版整卷答案页
│  ├─ extract_ext.py            # 抽取扩展题、去重、标注真题
│  ├─ match_short_answers.py    # 回填真题简答答案、输出缺口清单
│  ├─ data1.py ~ data7.py       # 分年份人工录入的真题
│  └─ archive/                  # 临时渲染页、合并前备份等中间产物
├─ docs/
│  ├─ 题目来源与统计说明.md      # 逐题型、逐年、逐文件来源说明
│  ├─ 真题简答答案缺口清单.md    # 未找到专门资料答案的真题
│  ├─ 扩展题来源与真题标注清单.csv
│  └─ 归档/
├─ 导出PDF/                     # 生成的客观题册、答案册、简答详解/记忆版
├─ .workbuddy/                  # 本地工作记录
└─ .git/
```

## 启动

双击根目录 `启动题库.bat`。脚本会进入 `常大真题电子版`，启动本地 HTTP 服务并打开浏览器；未安装 Python 时直接打开 `常大真题电子版/web/index.html`。

## 部署

Netlify 直接读取 `netlify.toml`：

```toml
[build]
  publish = "常大真题电子版/web"
```

无需构建命令与环境变量。站点为纯静态 HTML/CSS/JS，数据通过 `web/data/data.js`、`quiz.js`、`ext.js` 加载。

## 题库口径

- 真题：386 条卷面题（21 套，370 组唯一题干），按年份、卷面大题、题号保留。
- 扩展题：540 道（青蛙题库 191 + 简答资料去重 349），独立成页；其中 54 道标注为历年真题，并列出全部考过年份与原卷题号。
- 整卷答案：老魏版（2009—2024）与考研群资料版（2009—2026），支持在答案页和灯箱内切换。
- 真题简答：87 道中 85 道有专门资料答案，2 道缺口见 `docs/真题简答答案缺口清单.md`。

详细来源、文件清单、readme 要点与统计口径见 [docs/题目来源与统计说明.md](docs/题目来源与统计说明.md)。

## 数据重建

```bash
python _build/merge_projects.py       # 合并两项目题库，补 2017-简答-05、2025-简答-01/02
python _build/build_answers.py        # 生成两版答案页与 meta.answerVersions
python _build/extract_ext.py          # 生成 web/data/ext.json / ext.js
python _build/match_short_answers.py  # 回填简答答案并更新缺口清单
```

说明：`_build` 中早期脚本（`01_scan.py` ~ `11_builddata.py`、`crop_new_figs.py` 等）保留历史绝对路径，复跑前需改到当前目录；上面四个脚本已按仓库相对路径读取。

## Git 说明

`题目资料来源/` 是本地母库，体积约 470 MB，不纳入 Git；站点运行不依赖该目录，部署只需要 `常大真题电子版/web`。中间渲染产物放在 `_build/archive/`，同样不纳入版本控制。
