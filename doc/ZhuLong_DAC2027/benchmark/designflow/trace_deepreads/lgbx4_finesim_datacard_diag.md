# lgbx4 — FineSim `.enddata`→`.data` datacard 根因诊断 deepread

**session**: `1793843108682_lgbx4` (thomasz @ hfeg0pkn002, mc=16, spice_sim)
**fetched**: 554KB / 88 msgs, agent=lead, model=deepseek-v4-flash, 2026-11-05
**real tool**: FineSim (Synopsys) U-2023.03-2, spicead mode, V2B HKMG model (24nm-class)
**host file access**: .75(e0031982) 对 hfeg0pkn002 的 /proj/drvqa / /rundata **无读权限**（thomasz 私有）⇒ A 资产从 trace tool_results verbatim 重建（A档 trace-faithful + verbatim asset）

## 用户原话链（4 substantive user turns）
- U0 (MSG 0): `/proj/drvqa/V0/workdir/alieenwu/simulation/A_TestBench/4_DqIoTop/IPWM/result_IPWM_FFE_wiCH/pvt.log` + "看下这个log"
- U1 (MSG 9): "你要进Inc的各种文件中去看，找到根因"
- U2 (MSG 80): "这是把.enddata写成了.data导致的" ← **用户给出真根因，纠正 agent 之前的 model-param-scope 误判**
- U3 (MSG 86): ".data的机制是什么，我说的引出来可能不够专业" ← 要求专业机制讲解

## agent 行为链
1. 读 pvt.log → 定位 fatal `can't resolve parameter 'rdsw' for model 'ntn.51' (incFile_V2b_HKMG:30102)` + 大批 `undefined parameter 'dxl_ntn'/'dxw_ntn'/'dtoxe_ntn'/'dvfb_ntn'/'drdsw_ntn'`
2. 进 model include chain（model_corners.sp → model_env.sp → V2B model.sp → incFile_V2b_HKMG），映射 `.LIB MOS_TT/mos_tt/mos` 段结构，**初判**为 FineSim 跨 `.lib` 段 sigma 参数作用域问题（**误判**）
3. 用户纠正后，核实 stimulus 第 74 行：旧版（产生 failing log 的那次）是 `.data`（应为 `.enddata`），当前已改回 `.enddata`
4. 确认根因 = `.enddata`→`.data` 笔误；`dxx_ntn` 报错是 datacard 未闭合导致的参数展开上下文错乱级联误报
5. 给出 `.data`/`.enddata` DATACARD 机制专业讲解：block-read 卡片，`sweep data=NAME` 按行批量跑，缺 `.enddata` → 块未闭合 → 解析上下文错乱 → 模型参数被误报 undefined

## 关键 verbatim 数据（从 trace tool_results 抽取，用于 A 资产）
- FineSim 版本: `U-2023.03-2 for linux64 - Apr 25, 2023`
- include chain (log 行 44-53): option_finesim.sp / pwr_noise.sp / speed.sp / netlist.presim / GNRAP_connect / model_corners.sp / model_env.sp / V2B_HK_Model_D5_v0d1_Rev02_t01.sp / incFile_V2b_HKMG
- log 行 61-64: `WARNING! missing '.enddata' keyword for '.data' (stimulus:65)` ×2 + `(stimulus:74)` ×2
- undefined params: `dxl_ntn`(for xl, incFile 行 19707/19914/...) / `dxw_ntn`(for xw) / `dtoxe_ntn`(for toxe) / `dvfb_ntn`(for vfb) / `drdsw_ntn`(for rdsw)
- fatal: `ERROR! can't resolve parameter 'rdsw' for model 'ntn.51' (incFile_V2b_HKMG:30102)`
- 终止: `FineSim Completed with error(s) at Wed Nov  4 17:28:11 2026` (run 17:28:04→17:28:11, 7s, 0 fsdb)
- stimulus 行 35: `.data FFECode a b c`; 行 36-43: 8 行数据 `+ 0 0 0`...`+ 1 1 1`; 行 44: `.data`(BUGGY, 应 .enddata) — 重建版行号(原 trace 因 header 更长在 65/74)
- stimulus 行 78: `.lib '/proj/drvqa/V0/workdir/alieenwu/model_file/01_Corner/model_corners.sp' ttt_25_1.1` (corner TT/25°C/1.1V, 已正确选中)
- 分析语句: `.tran 1p 100n sweep data=FFECode`

## 意图判定
debug-Q&A（看 log 找根因）+ explain（要 .data 机制）→ 按 11-15 用户新标准恢复可造。
reframe: produce-deliverable（产结构化 JSON 根因诊断报告），check 验根因定位/证据/机制/修复/cascade 判定，stub 必 FAIL。
旧判 parked "L1 read-log diagnostic; no produce deliverable; spice ratio 4%" — 新标准下 debug-Q&A 是合法 spice_sim 真实意图。

## 拟造
EDA-Eval-DesignFlow-FineSimDatacardDiag-001
- 通用 `finesim_block_diag.py(workdir, out_dir)`：解析 pvt.log + stimulus，检测 block-terminator 笔误（.data/.enddata, .lib/.endl, .alter），产 JSON 根因诊断报告
- A: FineSim IPWM_FFE flow, `.enddata`→`.data` datacard 笔误
- hidden B: 不同 FineSim testbench（comparator DC sweep），`.endl`→`.end` library 段笔误（cross-input guard，全异命名/模型/参数/corner）
- check: ≥18 断言 + A-leak + B-grounding + 确定性 + 4 假提交
