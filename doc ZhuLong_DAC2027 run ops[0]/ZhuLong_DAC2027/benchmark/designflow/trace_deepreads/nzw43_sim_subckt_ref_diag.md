# 深读笔记 · 1794649204800_nzw43 (ericw@hfeg0plg07, mc=33)

- trace: `/home/ericw/.cline/data/sessions/1794649204800_nzw43/1794649204800_nzw43.messages.json` (357KB, 50 msgs)
- 时间: 2026-11-14 17:40~17:56, 2 user turn
- 域: spice_sim (FineSim/PrimeSim 仿真错误诊断) — **新 archetype: netlist subckt-reference-missing diagnosis**

## 真实任务（user 原话两 turn）
1. `/rundata/drdxq/V0/simdir/finesim/drdxqF/MatrixRun/MatrixRun_Netlist_Vcap_20261113PM/primesim.Perbank001_ActWrRdPre_WPre_2_tCH_50_BL16_4b8g_B0_100_TT.X4.TT0.98V25C.X4` 的 `si.out` 报错，分析：
   - `WARNING! node 'cmd_string118' was not found in the design (stimulus.list:1)`
   - `ERROR! no reference ckt ntk_wl for xmmn0(netlist:19025) of t_pmringoscpwrngutvdd1`
   - `ERROR! no reference ckt ptn_lv_pc60 for xmmp0(netlist:21863) of t_invlv_pc60x1pgni_pm`
   - `ERROR! no reference ckt ntn_lv_pc60 for xmmn1(netlist:21864) of t_invlv_pc60x1pgni_pm`
   - `ERROR! no reference ckt ntn_lv_pc60 for xmmn0(netlist:21865) of t_invlv_pc60x1pgni_pm`
   - `ERROR! no reference ckt ntn_lv_pc60 for xmmp0(netlist:21866) of t_invlv_pc60x1pgn_pm`
   - `ERROR! no reference ckt ntk_sv4 for xmmn0(netlist:21900) of t_nand2lv_pc60x1pgni_pm`
2. 「是因为没有在 incFile_T1_HKMG 里定义吗」
3. 「这些都是 nmos 或者 pmos 三极管吗」

## assistant 诊断（关键产出）
- 仿真器: PrimeSim Pro V-2023.12 (Synopsys), `primesim si.inp -np 6`, 仿真 17:33:25~17:34:11 (47s), `PrimeSim Completed with error(s)`
- 致命错误: `no reference ckt <subckt> for xmX(netlist:LINE) of <parent_cell>` — 缺失子电路定义
- 在 `incFile_T1_HKMG` (`/apps/imctf/models/T1/model_local/T1_HK_Model_PF_v0d1_Rev06/incFile_T1_HKMG`) 搜索缺失名:
  | 缺失名 | incFile 中 .SUBCKT 定义? | 详情 |
  |---|---|---|
  | `ntk_wl` | ⚠️ 有但名字带尾缀 `_` | `.subckt ntk_wl_ DRN GATE SRC` (L186143) — `.ends ntk_wl`，网表引用 `ntk_wl`，命名不一致 |
  | `ntk_sv4` | ❌ 完全找不到 | 既无 .SUBCKT 也无 .MODEL |
  | `ptn_lv_pc60` | ❌ 完全找不到 | |
  | `ntn_lv_pc60` | ❌ 完全找不到 | |
  - `T1_HK_Model_PF_v0d1_Rev06.sp` 只做 `.lib` 调用 incFile，一个都没定义
- 两类缺失: (1) 命名不一致 (defined with suffix `ntk_wl_` vs referenced `ntk_wl`); (2) 真缺失
- 器件类型确认: 都是 GAA 纳米片 FET (BSIM-CMG level=72):
  - `ntk_wl` → NMOS, 3 端 (DRN GATE SRC, 无 BULK), `.MODEL ntk_wl. nmos level=72 tfin=1.3E-8 hfin=1.2E-8 eot=4.0E-9 nbody=2.2E24`
  - `ntk_sv4`/`ntn_lv_pc60` → NMOS (ntk_/ntn_ 前缀)
  - `ptn_lv_pc60` → PMOS (ptn_ 前缀)
- 工具链: read_files(si.out 多段) → read_files(incFile_T1_HKMG + .sp) → editor 创建 grep_models.py → run_approved_command(python-runner) 搜索 .SUBCKT/.MODEL → read_files(incFile L186135-186280 确认 ntk_wl_ 定义)

## 合成方案 → EDA-Eval-DesignFlow-SimErrSubcktRefDiag-001 (spice_sim L2 便携 A 档 trace-faithful)
- 任务: 写 `analyze.py` (CLI `python3 analyze.py <si_out> <inc_file> <netlist> <out_dir>`) → `diag_report.json`, 打包 `submit.zip`
- A 档 (可见): synthesized si.out (保真实错误格式 + 真实 subckt 名 ntk_wl/ptn_lv_pc60/ntn_lv_pc60/ntk_sv4 + 真实 parent cell 命名 t_pmringoscpwrngutvdd1/t_invlv_pc60x1pgni_pm/...) + incFile_T1_HKMG (保真实 .subckt ntk_wl_/.MODEL ntk_wl. nmos level=72/tfin/hfin/eot/nbody 结构) + netlist.sp
- hidden B 档 (2 变体不同结构): 不同 subckt 名 (ptk_vs2/ntn_hv33/wl_drv_p/ptk_lp) + 不同 parent cells + 不同 netlist 行号 + 不同 naming-mismatch 变体 (ptk_vs2x vs ntk_wl_) + 不同 device type 分布 (B: pmos/nmos/unknown/pmos vs A: nmos/pmos/nmos/nmos) + 不同 terminal_count (B: 4 vs A: 3) + 不同 model params (tfin=1.1e-8/hfin=1.5e-8 vs 1.3e-8/1.2e-8) — cross-input 防硬编码
- 12 断言 a-l 含 cross-input guard(l): 随机选 B 重跑候选 analyze.py, B' missing subckt 名/parent_cells/netlist_lines/device_types 必须与 A 全不同 + B report 与 B ground_truth 匹配
- 输出 schema: {simulator, errors_total, missing_subckts:[{name, occurrence_count, parent_cells, netlist_lines, definition_status(naming_mismatch|truly_missing), defined_as, device_type(nmos|pmos|unknown), device_evidence, model_level, terminal_count}], summary:{distinct_missing_count, naming_mismatch_count, truly_missing_count, nmos_count, pmos_count, unknown_count}}
