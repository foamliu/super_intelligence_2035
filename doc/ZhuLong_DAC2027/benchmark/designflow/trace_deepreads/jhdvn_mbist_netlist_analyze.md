# Deepread — 1793017339067_jhdvn (mBist netlist topology analyze)

- session: `1793017339067_jhdvn.messages.json` (2.72 MB, 298 msgs: 156 user / 142 assistant)
- user: t0002805  | host: hfeg0pgn145 | model: deepseek-v4-flash | match_count: 492
- domain: schematic_netlist  | shard: D | track: B | level: L1
- case: **EDA-Eval-DesignFlow-MBistAnalyze-001** (round #182)

## 真实任务
DDR5 DRAM 项目的 mBist（memory built-in self-test）电路以 HSPICE 网表给出。
用户让 cline **自顶向下**分析 mBist 电路拓扑：解释每个 `.SUBCKT` 的端口、
X-实例调用关系、晶体管叶子单元 vs 复合单元、哪些是 mBist 专用 cell、哪个子电路最大。

## trace 行为统计（30 substantive user turns）
- tool uses: 72 × read_files, 33 × list_allowed_files, 5 × search_codebase,
  2 × run_commands, 2 × run_approved_command
- 无任何脚本产物 / 无 run_code 写文件。全程是「读网表 chunk + 向用户解释拓扑」。
- 主要网表：`mBistPat`（2170 行，49 .SUBCKT）与 `mBistTop`（4625 行，18 .SUBCKT）。
- 模型解释了 mBistRowFast / mBistColFastRd / mBistColFastWr / mBistLdCm / mBistRefresh
  等子电路的端口语义与实例构成。

## 选 trace 依据
- shard-D 排序 top：schematic_netlist 重权，layout/calibre 负权；mc=492 居前。
- 排除 38 个已记账 session + cross-shard A/B/C/D 已用 session + tckme/fkprl（layout，非 D）。
- trace 是纯 netlist 阅读+拓扑解释，零脚本 → 天然适配 L1「把读网表并结构化」固化为离线分析器。

## 合成 case 设计（B-track L1）
- **SUT**：`mbist_analyze.py <netlist.sp> <out.json>` —— 解析 `.SUBCKT` 块，提取
  端口 / X-实例 / 晶体管判定 / cell_counts / is_mbist / is_leaf，产出 summary +
  largest_subckt + mbist/leaf/compound 名单（字典序）+ per-subckt detail JSON。
- **Asset A**：从 trace `read_files` tool_result 重建的真实 `mBistPat` 网表（40 个干净
  `.SUBCKT`，442 实例，7 mBist cell，最大 mBistColFastRd:92，11 叶 / 29 复合）。
  去掉 40 行 `.map` 污染 + 修正一处错标 `.ENDS mBistRefresh`→`mBistColFastRd`。
- **Hidden B**：合成 `mBistTop_B.sp`（19 subckt，226 inst，5 mBist cell，最大
  mBistRefresh:68）—— 结构上与 A 完全不同（不同最大子电路、不同 mBist cell 集、不同总数），
  杀 A 硬编码。
- **Cross-input guard B2**：合成 `mBistTiny_B2.sp`（3 subckt，8 inst，1 mBist cell，
  最大 nand2:4）—— 极小，杀 B 硬编码 / print_expected。

## check.py（19 条断言 a–s）
独立 ground-truth resolver `_gt`（与 ref 不同实现：状态机+分趟）+ 固定 sanity 常量自检。
A: 8 条（zip/compile/exit0/total_subckts=40/total_instances=442/mbist=7/largest=mBistColFastRd:92/
leaf=11/mBistRowFast.inst=84/mBistColFastWr.inst=82/mBistLdCm.ports 精确列表）。
B: 3 条（total_subckts=19/largest=mBistRefresh:68/mbist=5）。B2: 2 条（total_subckts=3/
largest=nand2:4）。cross-input guard: 1 条（A/B/B2 最大子电路名两两不同）。
k_rationale == k_check == 19 ≥ 8 ✓

## 自验
- ref submit.zip → check() **PASS**（all 19）。
- 3 naive negatives + 3 §4.9 fakes → 全 **FAIL**，6 个 distinct label：
  naive_hardcode_a→[m]（pass A, fail B 证 hidden-B guard）、naive_no_largest→[g]、
  naive_leaf_only→[f]、fake_empty_shell→[c]、fake_print_expected→[i]、fake_core_deleted→[d]。
- test==disk roundtrip OK；no-leakage（attachments 不含 reference/hidden/jsonl/test）✓

## 覆盖分子
schematic_netlist 域 + netlist 拓扑解析（端口/实例/分类/largest）。B-track L1 离线脚本。
