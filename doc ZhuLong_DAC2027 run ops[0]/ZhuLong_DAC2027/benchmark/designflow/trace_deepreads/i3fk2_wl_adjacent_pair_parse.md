# Deepread: i3fk2 — WL adjacent-pair calibre DRC parse pipeline

- **trace**: `1793696115600_i3fk2` (leozhao @ hfeg0plg36, mc=106, physical_verify)
- **size**: 306KB, 83 msgs, 26 user msgs
- **tools**: 364 calibre + 10 hspice + 2 pyAether (keywords: calibre:471, drc:185, synopsys:37, .gds:31, aether:26, skipper:19, verilog:11, hspice:10)
- **scanned**: 2026-11-08 (shard C r228 选料, layout-affinity score=720, NEW user leozhao, mc>=15 pool)

## 真实任务流

- **U#0**: `/home/leozhao/wl-adjacent-detection.md 先了解下背景` — agent 读 concept 笔记：从版图找相邻 WL 对，命名规则 `sec<S>m<M>wl[O|E]<B>`（S=0–72, M=mat 1–56, O/E=奇偶行, B=bit）。label 在顶层 HSP_pin 层 ATTACH 到 HSP，金属图形在 subcell 内。
- **U#8** (核心需求轮): `deck已经生成：/proj/ddgoa/V0/ver/drc/ddgoa_array_core/Ary_m512Meg_U_fbcc_leo/agent/wl_adjacent.drc` + `处理report的脚本：.../parse_wl_pairs.py` + `你先跑一下全流程，就在deck所在目录跑，不要上bsub，留log`
- **A#9–A#50** (calibre 运行): agent 读 deck（518 行，12 个 `wl_pairs_{m1,m2,m3}_{hsp,m1a,m2a,m3a}.rep` 报告 + debug GDS + `wldrc.results/summary`），写 probe_env.sh 确认 calibre 2020.1_36 + GDS 223MB 在位，启动 `calibre -drc -hier`。**首次秒退报错 VCO 不匹配**（环境判 aok，树只装 aoi），用 `USE_CALIBRE_VCO=aoi` 强制重跑 → **46s 跑完**（CPU 42s/REAL 46s，13 rulecheck 全执行，无 unattached label 错误，TOTAL DFM RDB Result Count = 862014）。
- **A#56–A#76** (parse 运行): 检查 log（ordinal out-of-range 928 次 <0.2%、3 Short circuit 告警），peek 12 个 .rep 格式：`m1_hsp.rep` 574329 行有真名对（`CLUSTER <"s00m0wle<576>"> <"s00m0wle<512>"> CELL Ary_m512Meg_U_fbcc 0.66 78.1418 ...`），三个非 hsp 链（m1a/m2a/m3a）md5 相同且为 `<empty vector with tuple size 1>` 行。跑 `parse_wl_pairs.py`（先因 PYTHONHOME 冲突失败，unset 后重试）→ **917349 行 → 合并 766242 簇 → 222243 根 WL 有相邻对** → `wl_adjacent_table.rep`（13MB）；one-sided(邻接未命名网络)=0；≥3 成员簇 231 个进审计；无严格名簇 10285；无同名多链告警。
- **A#78–A#82** (验证交付): verify_output.sh 验证表格格式/抽查一致性/审计文件，全通过。交付：deck 目录跑完全流程，log 全留存。

## 关键产物（金标准来源）

1. **`wl_adjacent.drc`** — calibre DRC deck（518 行，layer map + ATTACH HSP_pin→HSP + CONNECT 链 + 12 个 rulecheck 输出 `wl_pairs_*.rep`）。SUT 不需要重写 deck。
2. **`parse_wl_pairs.py`** — 176 行 Python3 stdlib 解析器（**本案金标准**）：
   - 解析 `CLUSTER <"nameA" "nameB" ...> CELL <cell> x1 y1 x2 y2 ...` 行（DFM RDB ASCII）
   - 也接受 legacy `PAIR a b` 行
   - metal tag 从文件名 `_m([123])_` 提取
   - 按 `(metal, cell, normalized_tail)` merge → union(names)
   - 严格名 regex `^s[0-9]+m[0-9]+wl[oe]<[0-9]+>$` 过滤
   - 每簇：0 严格名→no-strict-name(n_noname)；1→one-sided/unnamed adjacency；≥3→audit；所有 distinct 对→adjacency
   - 输出 `wl_adjacent_table.rep`（name<TAB>comma-sorted-neighbors）、`wl_multicluster_audit.rep`、`wl_unnamed_adjacency.rep`
   - stdout summary：cluster lines / merged clusters / multi-member / one-sided / no-strict-name / WLs with adjacents / chain-dup warnings
3. **`.rep` 格式**（calibre DRC CLUSTER 报告）：
   - `CLUSTER <"s00m0wle<576>"> <"s00m0wle<512>"> CELL Ary_m512Meg_U_fbcc 0.66 78.1418 0.724 78.1418 0.724 81.316 0.66 81.316`
   - `CLUSTER <empty vector with tuple size 1> CELL lwx592o_odd_sec_WLstrapping_M1A_gut 1.145 73.89 ...`（空 vector = 无名 → no-strict-name）
   - 12 文件：`wl_pairs_{m1,m2,m3}_{hsp,m1a,m2a,m3a}.rep`
4. **运行结果**：917349 行 → 766242 簇 → 222243 WL 有相邻对；one-sided=0；≥3 成员=231；no-strict-name=10285；chain-dup=0。

## 选料判断：SEED ✓ (physical_verify)

- **真跑商业工具**：calibre 2020.1_36 -drc -hier 在 223MB GDS 上跑 46s 产 862014 DFM results（L2 真跑；本案抽取其 report-parse 闭环作 L1-boundary 评测，但 report 格式真来自 calibre DRC）。
- **完整闭环**：env-probe → calibre 运行（含 VCO 诊断修复）→ log 检查 → parse → 验证交付。
- **DISTINCT**：与 r220 SvrfTvfLayerMapGen（SVRF/TVF layer map 生成）、r208 DrcUnusedVarClassify（DRC deck 变量分类）、r217 DrcExtendRuleValidator（DRC extend 规则校验）不重叠 —— 本案首次 ground on **calibre DRC CLUSTER report 多链 merge → 相邻 WL 对表 + 审计分类**（DFM RDB ASCII 解析 + 跨源 merge + 严格名过滤 + one-sided/≥3-member 分类）。
- **NEW user leozhao**（台账无），未饱和。
- **可合成**：.rep 格式结构化、parse 逻辑明确、金标准可独立重跑验证 → 适合 L1-boundary design_flow（SUT 写 parser，check 在隐藏 B .rep 上跑）。

## 深读结论

→ 合成 `EDA-Eval-DesignFlow-WlAdjacentPairParse-001`（physical_verify, B-synthesized, L1-boundary）。SUT 写 `wl_adjacent_parse.py`（CLI 2 参，stdlib，解析 calibre DRC CLUSTER report 多链 → 相邻 WL 对表 + audit + summary）。A_run=trace grounded（Ary_m512Meg_U_fbcc, 12 链, s00m0wle<576>/s00m0wle<512> 对, empty vector no-name）；隐藏 B=不同 WL 名/簇结构；B2 clean guard；B3 heavy guard。
