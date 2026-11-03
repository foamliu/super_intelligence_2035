# trace deepread: 1792562147898_ygrxp — run_sweep per-corner parallelization

- session: `1792562147898_ygrxp.messages.json` · user `johnl` · host `hfeg0pfn119` · mc=100 · 94 msgs · 405KB
- domain: **digital** (drcoa_digital_T_IsmTop_schematic_ALPS, FineSim ALPS 仿真 sweep)
- shard A ✓ (digital)

## 用户意图轮（A-档 faithful 候选）
- UI#0 (逐字): `/rundata/drcoa/V0/simdir/finesim/workdir/johnl/simulation/drcoa_digital_T_IsmTop_schematic_ALPS  这个目录 我的run_sweep脚本的内容 现在是几个corner在一个任务太慢了 一个corner一个任务 做必要修改，并行的跑 修改后与原来的对比检查`
  - 规则②判定：用户表达**目标**（每 corner 一个并行任务 + 对比检查），**未给实现方案**（模型须自读 run_sweep.sh + IsmOscTestSweep.sp，识别 `.alter` corner 结构，写 netlist 拆分器 + per-corner bsub 提交）。"一个corner一个任务" 是 desired outcome 不是 fix recipe。→ **A-faithful ✓**
- UI#1 "完成修改后提交任务" — 依赖 UI#0 状态，非独立意图
- UI#2 "你只接本地运行run脚本不就行了吗" — 给修复方向（②排除）
- UI#3 "你要在这个文件夹生成一个记忆文件 介绍这个工程目录 脚本使用方法 脚本修改记录" — 干净意图但依赖前序修改状态
- UI#4 "为什么限制了你 你还是能写到这个目录" — 提问非任务

## 金标 = trace 助手 [1]-[91]
1. [1-14] 探查目录 → 定位 `run_sweep.sh`（top level）+ `IsmOscTestSweep.sp` 网表
2. [14-15] 读 original `run_sweep.sh`（16 行）：单 `bsub` 跑 `finesim ../IsmOscTestSweep.sp -np 4`，4 corner 经 `.alter` 在单 job 内**串行**仿真 → 慢
3. [22-26] 读 `IsmOscTestSweep.sp`（~205 行）：header（params+stimulus+.tran sweep+.meas 50+ 测量）+ 4 PVT corner 经 `.alter`：
   - corner0 (base): FF 1.3V -40C（`.TEMP -40` + `.lib ... FF`）
   - `.alter FF_1p3V_110`: pvcc=1.3, TEMP=110, FF
   - `.alter TT_1p1V_m10`: pvcc=1.1, TEMP=-10, TT
   - `.alter TT_1p21V_98`: pvcc=1.21, TEMP=98, TT
   - `.end`
4. [27-45] 写 `split_test.py`：按首个 `.TEMP` 切 header，`.alter` 切 corner block，生成 4 per-corner .sp（header+单 corner+.end）。修 bug：`.end` 正则误匹配 `.ends`（subckt 终止符）→ 改 `^\s*\.end\s*$`。验证 4 corner netlist 完整。
5. [46-47] 写 gold `run_sweep.sh`：
   - `set -euo pipefail`
   - env 覆盖：`QUEUE`/`CPU_CORE`/`DRY_RUN`
   - `here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`, `src="$here/$netlist"`
   - `module unload primesim 2>/dev/null || true` + `module load prime/2023.12-SP4`
   - **step1** 内嵌 Python heredoc 拆 netlist：按 `.TEMP`/`.alter`/`.end` 切，写 per-corner .sp + `corner_list.txt` manifest（idx name filename）。corner0→`IsmOscTestSweep.sp`，cornerN→`IsmOscTestSweep#N.sp`（保持 fsdb 命名兼容原单 job 输出）
   - **step2** 读 manifest，per-corner `bsub -q $queue -J osc_sweep_c${idx} "cd $PWD/$run_dir && finesim '$spname' -np $cpu_core > run_corner${idx}.log 2>&1"`。`DRY_RUN=1` 时只打印不提交。
6. [48-53] 测试：stub `bsub`/`module`（`_rtest/bin/`）+ `test_run.sh`，DRY_RUN 验证 4 corner 提交行正确
7. [54-57] 验证 gold readback 一致
8. [58-60] 清理临时文件（policy 只允许写 /home/johnl，ALPS 目录经 shell here-doc 写入）
9. [61-85] 用户要提交任务 → 探测 LSF env → 本地跑（UI#2）
10. [86-91] 用户要记忆文件 → 写 `PROJECT_MEMORY.md`（工程结构/脚本用法/修改记录）到 ALPS 目录
11. [92-93] 用户问为何 policy 限制仍能写 → 解释 editor 工具按 writableRoots 限制，shell 经 run_approved_command 不受限

## case 设计
- task_id: `EDA-Eval-DesignFlow-SweepParallel-001` · digital · L2 · A-faithful
- A 资产：prompt.txt（UI#0 逐字）+ task_brief.md（3 行交付接口）+ `run_sweep.sh`（original 16 行）+ `IsmOscTestSweep.sp`（A 网表 4 corner）
- 金标交付件：`run_sweep.sh`（gold 并行版）+ `compare_report.md`（diff vs original + 必要性）
- 隐藏 B：`IsmOscTestSweep_B.sp`（**6** corner，不同 PVT/name：SS_1p0V_0C / FF_1p4V_125C / TT_1p2V_25C / SS_0p9V_m40C / FF_1p35V_85C / TT_1p1V_60C）+ `run_sweep_B.sh`（同单任务结构，不同 queue/cpu_core）。判分在 B 上 DRY_RUN 跑候选 run_sweep.sh，验拆出 6 per-corner .sp + manifest。anti-hardcode：B corner 数（6）≠ A（4），name 不同 → 候选不得硬编码 "4" 或 A 的 corner name。
- L2：subprocess 在 B fixture 上跑候选 run_sweep.sh（DRY_RUN + stub module/bsub），结构判分（拆分正确性 + per-corner netlist 结构 + manifest）。不跑真实 finesim/LSF。
