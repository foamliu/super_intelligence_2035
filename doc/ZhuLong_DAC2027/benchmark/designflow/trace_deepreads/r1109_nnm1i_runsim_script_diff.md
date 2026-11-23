# r1109 deepread — nnm1i (thomasz@hfeg0pfn060) — FineSim→PrimeSim runsim script diff

**session**: `1794189436247_nnm1i` · user `thomasz` · host `hfeg0pfn060` (10.129.33.186) · mc=14 · 34 msgs / 154KB
**scan**: ssh_eda_search_20261123_064315/summary.tsv · keywords netlist:68/synopsys:40/mosfet:31/analog:10/pex:9/schematic:7/hspice:5
**ledger**: r1109 cross-shard released from D (D r561 mis-parked as "non produce-task"; FineSim spice_sim is B-domain, D only peek-rejected no case). Removed D ledger row, claimed for B.

## 对话流（完整）

- **U0** (act): `/rundata/commonIP/v1/lp5x/v0/simdir/anasim/yanghao/5_TsTOP/result_high_post/TS_lin_top_ff_step2/TS_lin_top_ff_step2.log 看下这个为什么报错`
- assistant read_files log: FineSim (R) V-2023.12-1, build 8650753. log:50-280 → netlist .presim + .spf_RCC + model .sp includes; WARNING unknown option artist/psf/method/opfile; WARNING node ...drn referenced by isub() not found [ignored]; expand ic 416762 names/234223 nodes; expand probe v(*)/i(*)/isub(*) level 4/5 ~30万探针; #Res 388206 #Cap 323056 POSTLAYOUT (#Res/#MOS=18.15:1); 最大 partition 397498 devices/65346 nodes.
- 关键崩溃段 (log 271-279):
  ```
  271 Starting Transient Analysis ...
  274 Using spicead, important parameter values:
  275   runlvl = 5
  276   tolscale = 5
  277 ERROR: Terminating with signal 11.
  279 Unexpected fatal error. Please contact Synopsys support...
  ```
- assistant 诊断: signal 11 = SIGSEGV，FineSim 内部段错误，发生在瞬态求解启动瞬间。根因：超大 RCC 后仿网表 + runlvl 被 `accurate=1` 从 4 重置到 5 + tolscale=5 → 矩阵过大内存压力/OOM 级段错误。建议：减探针/减.IC/降 runlvl/放宽 gmin/换大内存机器/报 Synopsys。.elog 基本空，sim_log 空，唯一错误就是 signal 11。
- **U15** (act): `我修改了文件，看看差别`
- assistant list_allowed_files 5_TsTOP 目录 → runsim/ 下有 11/09 当天三个新脚本: 091925(09:19 崩溃)、101118(10:11)、103758(10:37)。read_files 三脚本 + 网表 .sp:
  - `runsim_20261109_091925.sh` (崩溃): `module load ds/finesim/2023.12-1`; 9 commands `bsub -q fqueue3 -J TS_lin_top_<corner>_step2 finesim -i TS_lin_top_<corner>_step2.sp -o ... -np 6 &` (corners ff/fs/ft/sf/ss/st/tf/ts/tt)
  - `runsim_20261109_101118.sh` (中间): finesim 但 queue=fqueue3_ams, 1 command
  - `runsim_20261109_103758.sh` (跑通): `module load ds/primesim/2023.12-SP2-3`; 9 commands `bsub -q fqueue3_ams -J TS_lin_top_<corner>_step2 primesim -spice -i TS_lin_top_<corner>_step2.sp -o ... -np 6 &`
  - 网表 TS_lin_top_ff_step2.sp 未改: `.option accurate=1 runlvl=4` / `method=gear` / `gmin=1e-16 gmindc=1e-16` / `finesim_mode=spicead` 等
- assistant 确认新 log: PrimeSim SPICE V-2023.12-SP2-3 build 9344713; `runlvl = 4, tolscale = 10` (accurate 被忽略); Starting Transient Analysis 成功推进到 140us/70% (alter0 -40℃); 有 convergence difficulty with minimum time step at t=1e-14 但没崩。
- **最终差别表** (assistant 给出):
  | 项 | 崩溃 | 修改后 |
  | 命令 | finesim -i ...sp -o ... | primesim -spice -i ...sp -o ... |
  | 工具/版本 | FineSim V-2023.12-1 (build 8650753) | PrimeSim SPICE V-2023.12-SP2-3 (build 9344713) |
  | 队列 | fqueue3 | fqueue3_ams |
  | runlvl | 5 (accurate=1 触发 4→5) | 4 (accurate=1 被忽略) |
  | tolscale | 5 | 10 |
  | 结果 | signal 11 段错误 | 瞬态正常推进 70% |
  结论：用户改的不是 .sp 网表，而是换了解析引擎 FineSim→PrimeSim（+换 ams 队列），绕开 FineSim V-2023.12-1 在超大 RCC 后仿网表上的段错误。

## reframe

把 runsim 脚本对比逻辑抽成 **spec 驱动的 L1 纯 Python runsim 脚本差别分析器**：
- `runsim_diff_analyzer.py <script_a> <script_b> <out.json>`
- 每脚本解析: generated_at / tool / version / module_line / queue / n_commands / jobs[{jobname,binary,spice_flag,spice_input,output_prefix,cores}]
- diff: tool_changed / version_changed / queue_changed / command_changed / spice_flag_changed / same_spice_input / n_commands_changed / jobnames_match
- verdict: tool_switch_finesim_to_primesim / command_changed_same_tool / no_change / partial_change

## case 落库

**case = EDA-Eval-DesignFlow-RunsimScriptDiffProduce-001** (cases/B/)
- A 可见对: thomasz 真实 runsim_crash_A.sh (finesim/fqueue3/9 corners/TS_lin_top) + runsim_success_A.sh (primesim -spice/fqueue3_ams/9 corners/TS_lin_top)
- hidden B: PLL_TOP 对，3 corners (ss/ff/tt)，finesim 2023.12-2/fqueue3/-np 8 vs primesim 2023.12-SP2-3/fsim_ams/-spice/-np 8；**success 脚本重命名 .sp 为 _v2.sp** → same_spice_input=False（核心齿，反 "永远 True" naive）
- check.py 20 条 (a-t): REF 20/20 PASS, NEG 3/3 FAIL (empty→a/b, print_only→d-s 硬编A, core_removed→n/q 硬编 False/True), 3-seed sha256 确定性 ✓
- k_rationale=20 == k_check=20 ✓ (≥8 门槛)
- trace_source 真实溯源 ✓ (thomasz/hfeg0pfn060/1794189436247_nnm1i/mc14)
