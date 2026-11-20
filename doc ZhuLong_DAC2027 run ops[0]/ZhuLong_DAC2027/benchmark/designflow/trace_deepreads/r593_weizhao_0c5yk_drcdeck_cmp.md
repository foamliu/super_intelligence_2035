# r593 deepread — weizhao / 1790065302917_0c5yk (DRC deck value comparison)

- session: `1790065302917_0c5yk.messages.json` (weizhao @ hfeg0pkn001 / 10.129.2.10, mc=409)
- domain: physical_verify (Calibre DRC rule deck comparison)
- keywords: drc:1281;calibre:294;pdk:245;lvs:4 → strong PV signal, new user (not prior C case)
- NMSG: 243, 11 user_input (produce-task, iterative script dev)

## User intent (trace-faithful)
weizhao 在两份 Calibre DRC rule deck 之间做"shrink factor 缩放校验"：
- UI#1: 对比 `/home/pdk/weizhao/00_drc/LDDB/G4B/LDDB2.0_drc_SF1_v0d5_rev14/calibreDRC.rule`（SF=1）与 `LDDB2.0_drc_v0d5_rev14/calibreDRC.rule`（SF=0.318），分析两份是否**只有数值差别**且 check 数值是 0.318 倍关系。
- UI#2: 把每条 rule 数值对比结果整理成可读性高的 `drcvaluecompare.txt`，输出到 `/home/weizhao/`。
- UI#3: 用 SF=0.318 / SF=1 计算比率（得 0.318 而非 3.145）。
- UI#4: 输出 txt 全英文，不要中文。
- UI#5: 忽略开关定义，对比**所有开关下所有 rule**，输出到一个 txt。
- UI#6/7/8: 用 python 脚本实现（修复 libpython3.6m.so 缺失 → 改纯 python）。
- UI#9: 回滚到最佳版本 `drcvaluecompare_en.txt`。
- UI#10: 重申 0.318 方向。
- UI#11: 把 `_F` 无数值 rule 也统计；同类 rule 放一起；不区分 Group。

## Deliverable (gold = actual artifact)
最终交付脚本 `/home/weizhao/.cline/scripts/data/drc_full_compare.py`（162 行，已 scp 验证）：
- 读两份 deck，逐行 zip 对比
- 抽取所有 `VARIABLE NAME value` 定义
- 数值差异分类：`num_re.sub('@N@')` 后相同 → Numeric-only，否则 Structural
- VARIABLE 比率 = SF0.318/SF1，分类 Scaled(0.318)/Area(0.318^2=0.101)/Unchanged/Other/Non-numeric
- 输出 4 section 报告：① ALL VARIABLE DEFINITIONS（含 Summary 计数）② ALL DIFFERING LINES ③ STRUCTURAL DIFFERENCES ④ INLINE NUMERIC VALUES + CONCLUSION（structural==0 → CONFIRMED only-numeric；≤2 → Nearly identical）
- 真实 deck：14285 vs 14282 行，SF1 deck 的 VARIABLE 值约为 SF0.318 的 1/0.318≈3.14 倍

## Case synthesis (B档 mock-behavioral)
- 真实 deck 太大（14K 行）且含 PDK 专有规则 → 合成小规模忠实 fixture（保留 #DEFINE/VARIABLE/GROUP/DRC CHECK 结构与 0.318 缩放语义）
- 输入 A（可见）：calibreDRC_SF0318_A.rule + calibreDRC_SF1_A.rule（8 VARIABLE：4 scaled + 1 area + 2 unchanged + 1 non-numeric；1 structural diff = GROUP 多一成员）
- 隐藏 B：8 VARIABLE（3 scaled + 1 area + 2 unchanged + 1 other + 1 non-numeric；structural=0 → CONFIRMED）
- 隐藏 B2：4 VARIABLE（1 scaled + 1 area + 1 unchanged + 1 non-numeric；structural=1 → Nearly identical）—— B vs B2 计数/结论不同，反硬编
- 接口参数化：`python3 drc_full_compare.py <sf0318> <sf1> <out_txt>`（真实脚本硬编码路径，本 case 要求 argv 参数化以利离线判分）
- check() 跑 B+B2，解析报告断言 12 条 a-l（见 check.py docstring）

## Real task summary (for metadata.trace_source)
User (weizhao) comparing two Calibre DRC rule decks (SF=0.318 vs SF=1) to verify check values scale by 0.318× (linear) / 0.318^2 (area); wants a Python script that diffs all VARIABLE definitions and all lines across every switch, classifies numeric-only vs structural diffs, computes per-VARIABLE ratios, and writes a structured all-English 4-section comparison report. Iteratively refined direction (0.318 not 3.145), language (English-only), coverage (all switches, _F no-value rules), and format.
