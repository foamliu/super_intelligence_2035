# Trace deepread — 1794797385862_khobz (tongfanl@hfhds201, mc=119)

**Session**: 1794797385862_khobz, 1.59MB, 290 msgs, 141 assistant, 131 tool calls, mtime 2026-11-18 17:13
**Domain**: spice_sim (FineSim aging matrix 仿真状态检测)
**Real task** (from 19 user prompts + 131 tool calls):

## 用户真实意图
用户在跑 DDR6 PowerFill V0d9 的 Aging matrix 仿真，42 个 MatrixRun 文件夹在 `/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun`，前缀 `MatrixRun_Netlist_SpfBA_20261106PM_DDR6TOP_PowerFill_V0d9_Rev02_t01_COMPRESS_Aging`。每个文件夹下多个 `primesim.*` 子目录 = 一个 FineSim 仿真 job。用户要用 `/home/tongfanl/bmatrix_tf`（Perl 脚本，`perl bmatrix_tf -E -D -K`）逐文件夹独立判 job 状态，出「哪些文件夹有 Pending/Unknown/Exited」的表。

## 用户迭代多轮纠正的口径误区（红线）
1. **绝不用 `-i dir1 dir2 ...` 多目录模式**：`bmatrix_tf` 的 `getBatchMatrixStatus` 按子目录 basename 去重，多个文件夹里同名的 `primesim.*` 只保留后一个，**Exited 漏报**。
2. **逐文件夹独立跑**：要么 `cd` 进文件夹不带 `-i`，要么 `-i` 只传一个文件夹。
3. **按状态行计数比数列表行更稳**：汇总数字可能来自多目录 bug，必须直接数 `Exited`/`Pending`/`Unknown` 开头的状态行数。
4. **subprocess `cwd=` 不更新 `$ENV{PWD}`**：必须显式 `env["PWD"]=folder`，否则脚本扫错目录返回空。
5. **状态口径**：`Pass`/`Fail` 都算 Done（已结束），只有 `Running` 算运行中；`Exited` 异常退出（被 kill/仿真失败，单独报）；`Pending` 排队；`Unknown` 无法判定。

## bmatrix 输出格式（faithful 重建自 trace msg #114/#156/#178/#198 等）
```
Exited   primesim.<jobname>
Pending  primesim.<jobname>
Unknown  primesim.<jobname>
...（0 行或多行）
Total Pass Fail Exited Comparing Running Pending Unknown
<N> <N> <N> <N> <N> <N> <N> <N>
```
- 状态行：以 `Exited`/`Pending`/`Unknown` 开头，单空格分隔，后跟 `primesim.*` job 名
- 汇总：`Total Pass Fail Exited Comparing Running Pending Unknown` 是**表头**，下一行才是 8 个数字
- **汇总数字不可信**（多目录 -i bug），必须数状态行

## 交付（用户最终要的）
1. `check_matrix_status.py` helper 脚本（参数化 base + prefix，逐文件夹 subprocess 调 bmatrix_tf，env[PWD]=folder，数状态行出表）
2. `matrix-job-status` SKILL.md（含 3 红线 + 状态判定口径）
3. `references/why_bmatirx_workflow.md`（前因后果 + 工具内部机制）

## 本 case 抽取的 testable core
agent 须交付 `matrix_status_parser.py`：参数化 `--indir <dir>`，读目录下所有 `.txt`（每个 = 一个 MatrixRun 文件夹的 `bmatrix_tf -E -D -K` 输出），**数状态行**计数 Exited/Pending/Unknown（不读汇总数字），输出 flagged 表 + 总数。

## 访问约束
- trace 文件可读：`/home/tongfanl/.cline/data/sessions/1794797385862_khobz/1794797385862_khobz.messages.json`（1.59MB, .75-local）
- 真实 `/home/tongfanl/bmatrix_tf` Perl 工具：未读取（不需，输出格式从 trace msg 重建）
- 真实 MatrixRun 文件夹：未访问（用户路径 `/rundata/dscqa_sim/...` 属 dsgao/dscqa 组，可能权限拒访；A/B fixtures 由 trace 输出格式 faithful 重建）

## case 落地
- case_id: EDA-Eval-DesignFlow-MatrixJobStatusParse-001
- domain: spice_sim / layer L1 / track faithful / tier B
- k_check = k_rationale = 14 (a-n) ≥ 8 ✓
- A: 5 bmatrix 输出文件（assets/.../bmatrix_A/）
- Hidden B: 6 bmatrix 输出文件（assets/.../hidden/bmatrix_B/，含 MultiDirTrap_Aging_step1 trap：4 行 Exited 但汇总谎报 Exited=0）
- §4.9: 5 neg（empty_shell/print_expected/hardcode_a/summary_reader/core_deleted）全 FAIL NEG_RC=5/5 ✓
- ref 14/14 PASS ✓
