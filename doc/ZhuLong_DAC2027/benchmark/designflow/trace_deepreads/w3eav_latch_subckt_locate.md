# trace_deepreads/w3eav_latch_subckt_locate.md — zxtu @ hfeg0pkn001, session 1791969171304_w3eav

## trace 来源
- **user**: zxtu
- **host**: hfeg0pkn001 (10.129.2.10)
- **session_file**: 1791969171304_w3eav.messages.json (168 msgs, dir-based `<sid>/<sid>.messages.json`)
- **match_count**: 341 (spice-dominant: 24 hspice / 341 total tools)
- **发现方式**: 11-05 重扫令 · 11-09 cron log (eda_trace_20261109.log, mtime 2026-11-09 00:00:59) spice-dominant 过滤 (sp≥10 ∧ ratio≥0.35) → 132 strict cands → 排除 ledger_B 518 anchors (normalized+short) → 16 unprospect → peek top reachable (pkn001) → w3eav CLEAN

## 选轮（A-faithful）
- **U#0** (msg#0): 「bash怎么获得终端输入参数」— trivial，不入 prompt
- **U#1** (msg#2): 「解析 .../si.out 中的 warning」— FineSim 日志 warning 解析（提出需求，无根因 → 可 A-档，但本轮选 U#2 更贴 spice_netlist 域）
- **U#2** (msg#25): **「找出这份网表文件中的latch subckt： /rundata/ddgoa/V0/simdir/finesim/workdir/caozhang/simulation/Netlist_Vcap_20261012PM/netlist.presim」** — 提出需求，无根因/无修复方向 → **A-档 ✓ → 本 case 任务说明**
- **U#3** (msg#38): 「从网表提取 cck 文件 template，格式 Subckt,refname,signame,data,RN,SN,R,S」— 含格式约束的提取任务（可另出 case，本轮不用）
- **U#4** (msg#148): 「网表中 subckt：AF_latqYx1 为什么没有写进 cck_template_auto」— 含根因质疑（"为什么没有"），**不入 prompt**（A-档选轮规则：凡指出根因/修复方案的轮不得用作任务说明）

## 金标准（assistant msg#37 + find_latch_subckt.py msg#29/33）
agent 写 `find_latch_subckt.py`：
1. 正则 `^\s*\.subckt\s+(\S+)` (IGNORECASE) 匹配 `.subckt` 定义行
2. 取 subckt 名（.subckt 后第一个非空白 token）
3. 若 "latch" in name.lower()（大小写不敏感子串匹配）→ 记录 (lineno, name)
4. 在 118MB 网表中找到 **52 个** latch subckt（如 CmLatchX5Unit/cmllatchV3IP/R1in1Latch/SpareFuseLatch_CML/LATCH_CML_OSC/...）
5. 输出 `latch_subckt_list.txt`（行号→名称，每行一条）

关键判分点（对事实，不对措辞）：
- 只匹配 `.subckt` 定义行，不匹配 `.ends` / X 实例 / 注释
- 大小写不敏感（UPPER/lower/Mixed 都要命中）
- "latch" 在 subckt **名**里，不在端口名/参数名里（decoy: BufEn en in out latch_ctrl → 名=BufEn 不命中）
- 子串匹配（RelatchBuf 含 "latch" → 命中）

## 本 case 抽取
- **域**: spice_sim (SPICE 网表 subckt 定位)
- **档**: A-faithful (prompt = U#2 逐字)
- **层**: L1 (离线 Python 复刻：正则扫描网表文本)
- **可复用子流**: "SPICE 网表 .subckt 定义按名定位（大小写不敏感子串）"
- **关键 trap**: 端口名含 keyword 的 decoy / .substk 拼写错误 / .ends 与 X 实例排除 / 大小写覆盖 / A≠B 非硬编码 / 子串匹配
