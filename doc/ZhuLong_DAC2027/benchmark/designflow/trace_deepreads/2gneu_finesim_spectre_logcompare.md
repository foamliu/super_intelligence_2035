# trace_deepread: 1794881885856_2gneu (e0044979@hfeg0pkn002, mc121, spice_sim)

**session**: `1794881885856_2gneu.messages.json` (250 msgs / 1.2 MB / agent=lead)
**user**: e0030760? no — e0044979 (NEW-user check: not in B ledger before this claim; prolific spice-sim user)
**host**: hfeg0pkn002 (10.129.x)
**scan**: b_pool_1118_230537.tsv, kw = `spectre:324;netlist:278;.def:26;rtl:3;cadence:3;schematic:2;analog:2;hspice:1` (spectre-dominant, ratio 0.51)
**domain**: spice_sim (FineSim vs Spectre FX characterization comparison)

## 用户真实意图（5 轮 user turns，原话）

1. `[0]` "In /rundata/lacaa/TV1_FS/.../SRAM_tailor/CXN4HCSPS16384X8M8B8C1R1W1BW1RE1_FS_i4_c4_l6/ I compared log file and measure, python3.10 .../sim_log_compare.py fx_results/.../...spectre.log fsim_results_orig/..._FS_i4_c4_l6.log but the script has two problem: - the log file of Spectre FX - the measure comparison is not in html report"
2. `[152]` "continue to check the failed category of .measure. Why all belongs to unknown."
3. `[200]` "Static html now is OK, I need to fix it in dynamic view of html. Can you also fix it?"
4. `[212]` "If I change the filter of measure comperison, e.g. only print the failed ones, or change the threshold relative/absolute errors, it doesn't work."

→ **用户在做的事**：修一个 FineSim-vs-Spectre-FX 仿真 log 对比工具链（`sim_log_compare.py` + `simlog_parsers.py` + `meas_parsers.py` + `compare_report.py`），让它能正确解析 Spectre FX log 的 runtime/内存、把 measure 对比表静态渲染进 HTML、正确分类 `.measure`（不要全 unknown）、修好动态视图的筛选/阈值交互。

## assistant 工具链与产出（关键）

- 读了 `sim_log_compare.py` / `simlog_parsers.py` / `compare_report.py` / FX log / FS log / `.measure` 文件 / 两个 `.sp` 网表
- 用 node + DOM stub 验证 JS 渲染逻辑（judgeAll → 2771 rows / 958 FAIL）
- `/rundata` 只读 → 在 `/home/e0044979/fix_runner/` 下做 patched 副本，生成 diff/patch
- 端到端验证：`sim_log_compare.py` 重生成 902KB HTML，静态 measTblWrap 含 2772 `<tr>`，JS 仍正常

## 四个真实缺陷（agent 实证根因 + 修复，均已验证）

### 缺陷 1 — Spectre FX log runtime/内存解析失败（runtime 全 "—"）
**根因**：`simlog_parsers.py` 的 FX 正则只支持普通小数 `([\d.]+)`，但真实 FX log（8 小时大仿真）用：
- 科学计数法 `4.382118e+05 s` / `4.38e+05 s`
- 天/时分秒备注 `(5d 1h 43m)`（可无秒，如 `(17d 20h)`）
- 字节+科学计数内存 `4.46e+10 bytes`

旧正则全不匹配 → 20 stage 只认 3 个 → DC/tran 桶 "—"，Total "—"，峰值内存少报（21.9GB vs 真实 41.54GB）。
**修复**：正则用 `_RE_NUM`（含科学计数）+ `_parse_dhms`（d/h/m/s）+ bytes→MB 换算。验证后 Total=29100s / DC=398.6s / tran=26753.7s / Peak=42534MB。

### 缺陷 2 — measure 对比表/统计在 HTML 里空白（JS 没跑就看不到）
**根因**：measure 大表/计数/关键 measure 全部只由嵌入 JS 渲染（`<div id="measTblWrap"></div>` 等容器是空的），数据以 `MEAS_DATA` JSON 嵌入，但查看器不执行 JS（预览/邮件/安全设置）时第 4、5 节空白。
**修复**：服务端先把这三块**静态渲染**进 HTML，JS 只覆盖成可过滤/排序/改阈值的交互版。静态 measTblWrap 含 2771 数据行 + 计数表 + 关键 measure 兜底。

### 缺陷 3 — 所有 measure 分类成 "unknown"（`.measure` 定义在被 `.inc` 的独立文件里）
**根因**：`build_class_map → parse_measure_defs` 只读 `.sp` 网表本身，但网表里**没有** `.measure` 语句，只有一个 `.inc 'CXN4HCSPS..._FS.measure'`；真正的 `.meas tran <名> +trig/+targ` 定义全在被 `.inc` 的文件（8394 行）里。分类器不跟随 include → 0 定义 → 全 unknown（`timing=0/0 ... unknown=1812/958`）。
**修复**：`parse_measure_defs` 递归跟随 `.inc`/`.include`。
**关键坑**：网表还 `.inc` 超大 `.dspf`（gzip 几 GB）/模型库 `.lib` —— 全量展开会卡死（agent 实测 `_iter_includes` 展到 >200k 行）。故加 `_is_measure_def_file()` 门控：文件名含 measure / 前缀 `.meas`/`.mes` / 前 500 行出现 `.meas` 定义才跟随；`.dspf`/`.dspf.gz`/`.gz`/`.lib`/大文件（>50MB）一律跳过；realpath 去重防循环。
验证后：`timing=1806, derived=964, unknown=1`（仅合成 `temper` 列）。

### 缺陷 4 — 动态视图改筛选/改阈值没反应（浏览器-only 故障，node 复现不出）
**根因**：
1. `renderStats()` 用了 `Object.fromEntries(...)`（ES2019），旧版/嵌入式 WebView 直接抛异常；`renderAll()` 调用顺序 `renderStats → renderKeyMeas → renderMeasTable`，renderStats 一抛 → renderMeasTable 不执行 → 点"应用"表不重建。
2. 筛选 checkbox 只绑 `onchange`，很多 WebView 对 checkbox 的 change 在**失焦**才触发 → "只显示非 pass"/分类过滤"点不动"。
**修复**：
- renderStats 去掉 `Object.fromEntries`，改兼容写法；
- `renderAll` 里 renderStats/renderKeyMeas 各包 try/catch，保证 renderMeasTable 每次都重建；
- 分类过滤/"只显示非 pass" checkbox 同时绑 `onclick`+`onchange`，点一下立即生效。
验证（node 模拟真实交互）：勾"只显示非 pass" → 2771→959 行；改阈值+应用 → FAIL 958→52，计数同步 `pass=2718/FAIL=52`。

## reframe 决策（harness-for-teeth，第二十五实证）

trace-faithful A 档不直接可行：用户是 debug-Q&A/修脚本（4 轮交互修一个不可便携的 `/rundata` 本地工具链，真跑要 Spectre/FineSim 二进制 + GB 级 .dspf），判分无法"有牙"。
→ **produce-tool reframe**：把"修好的对比工具链"抽成一个自包含 `sim_log_compare.py`（parse FX/FS log + classify via include-following + 生成静态+JS HTML），判分器在**结构性不同的隐藏 B**（不同科学计数形式 / `.include` 而非 `.inc` / decoy `.dspf.gz`+`.lib` / 不同 measure 名值）上真跑候选 + 独立重算 B 的 Total/tran/Peak 对照 + 静态表/JS 加固/门控逐一断言。判分有牙：退化提交（空壳/print-A/hardcode-A/删核心/always-pass）全 FAIL。

## 选料与可一轮闭环

- b_pool_1118 fresh spice mc≥10，e0044979 mc121 spectre-dominant；trace 250 msgs/1.2MB 可一轮闭环
- 4 缺陷覆盖 trace 全部 4 轮 user intent，harness-for-teeth reframe 第 25 实证（binary-waveform-parse / doc-Q&A / debug-Q&A / multi-round-fix → produce-tool 复合型）
