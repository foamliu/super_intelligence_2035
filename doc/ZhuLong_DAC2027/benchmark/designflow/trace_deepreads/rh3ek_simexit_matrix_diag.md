# trace_deepread: rh3ek — NanoSpice matrix-run sim exit diagnosis

**session**: 1793667622298_rh3ek · **user**: ypzheng · **host**: hfeg0pkn003 · **mc**: 180 · **spice_score**: 11
**domain**: spice_sim · **track**: A-faithful · **level**: L1

## 用户意图流（关键 user turns）
- **U#0 (msg#0) — A-faithful 任务说明轮**（逐字）:
  `/proj/ddgoa/V0/simdir/finesim/workdir/ypzheng/ddgoaF/MatrixRun_Netlist_SpfBa_20261031PM_wisteria/去这个目录，看看仿真exit的原因是什么，应该怎么解决`
  → 提出需求（诊断仿真退出原因 + 解决方案），**未给根因/未给修复** → 符合 A 档选轮 ✓
- U#41 (msg#41): "WARNING: The available physical memory is only 3-20GB...这一句在哪能找到" — 定位追问（不入 prompt）
- U#47 (msg#47): "rm -rf ...Device or resource busy 这是报的什么错" — NFS silly-rename 诊断（独立子问题，不入 prompt）

## 金标准（assistant msg#40 + scan_sim_exit3.py）
扫描 NanoSpice matrix-run 目录（24 个 run 子目录），逐个读 `si.out` 分类：
- **COMPLETE** (1): si.out 含 `Simulation completed successfully`
- **FAILED** (6): si.out 含 `Simulation failed`，分两型：
  1. **verilog_a_bsource** (4 runs): `!!NanoSpice-ERROR: Cannot found shared object library for VerilogA module: bsource_primarius_3.` + `Verilog-A error: Cannot find shared object library for bsource module. Maybe other NanoSpice process is running this netlist, please rerun with a new work dir.` — 并发编译 Verilog-A bsource 共享库冲突
  2. **transient_convergence** (2 runs): `Transient analysis my_tran did not converge` + `time step too small` — 瞬态不收敛
- **RUNNING** (17): si.out 部分输出，无 completion/failure marker

根因分析：24 个 job 同一 netlist 并发 bsub → Verilog-A bsource 共享库编译互踩 compile.info/.so。

## 可复用子流（case 抽取点）
「NanoSpice/FineSim matrix-run 仿真退出诊断」：扫描 run 子目录 → 读 si.out → 按 marker 分类 COMPLETE/FAILED/RUNNING → FAILED 按 error 关键词细分 verilog_a_bsource / transient_convergence → 提取 failure reason 行 → 输出结构化 JSON。

## 合成（SimExitMatrixDiag-001）
- A (assets/matrix_run_A): 16 run dirs + 1 A-only marker = 17 → 3 COMPLETE(含marker) / 8 FAILED(5 bsource+3 conv) / 6 RUNNING
- hidden B (matrix_run_B): 14 run dirs → 3 COMPLETE / 6 FAILED(4 bsource+2 conv) / 5 RUNNING，目录名/rid/分布均不同
- reference sim_exit_diag_ref.py: classify_siout() 按 marker + 关键词分类
- check.py: 14 断言 (a-n)，B 真值重算 + A 泛化 + 非硬编码 marker + 3x 幂等
- 4 negative: naive_all_complete / always_running / hardcoded_b / print_expected — 全 FAIL
- §4.9 三假: empty/print-expected/del-core — 全 FAIL

## 关键 trap
- bsource 关键词检测须用 "shared object library"（header 行含 "bsource instances" 误触）→ 用 specific error pattern
- A-only marker 目录 (ZZA_ONLY_MARKER) 在 A 但不在 B → 非硬编码闸门
- stray file (README_matrix.txt) 须被 scanner 忽略
- failure_types 须含两种类型（区分两类失败）
