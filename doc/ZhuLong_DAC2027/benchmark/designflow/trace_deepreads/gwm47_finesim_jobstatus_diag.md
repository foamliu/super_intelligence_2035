# Deepread — 1794193758706_gwm47 (FineSim MatrixRun job-status monitor + OOM/EXIT diag)

- session: `1794193758706_gwm47.messages.json` (1.56 MB, 374 msgs: 193 user / 181 assistant)
- user: tongfanl (dandans 账号) | host: hfeg0pkn002 | model: deepseek-v4-flash | match_count: 86
- domain: spice_sim | shard: B | track: B | level: L1
- case: **EDA-Eval-DesignFlow-FineSimJobStatusDiag-001** (round #642, 复活池变现 #24)

## 真实任务
DDR6 项目的 FineSim/PrimeSim 老化仿真矩阵（MatrixRun）跑在 LSF 上。用户反复要求
cline「读这批 Aging 目录的日志，给一份结构化的 job 状态/进度/诊断报告」：
- LSF 状态（bjobs/bmatrix 的 RUN/PEND/DONE/EXIT）；
- si.out 末尾瞬态进度百分数（`<tval>us (NN.N %) at <ts> (<elapsed>)`）；
- si.inp 的 model/aging_model 是否 `current_D5_v0d9_rev01` / `..._relia`；
- si.inp `mosrapath` 是否被 `**` 注释（`_normal` 基线重跑 job，故意不带 aging）；
- si.out 真正的内存报错（`Cannot allocate memory`/`Out of Physical Memory`，区别于
  每个 si.out 都有的正常 `Peak memory usage` 报告）；
- `PrimeSim Successfully Completed` 完成标记；Resource Usage 的 cpu/elapsed total。

## trace 行为统计
- tool uses: 50 × run_approved_command, 35 × read_files, 68 × editor, 8 × list_allowed_files,
  4 × run_commands, 1 × search_codebase, 1 × get_agent_policy_status
- 全程「读日志 + 写检查脚本 + 向用户解释状态表格」，最终交付是 markdown 状态表（非脚本产物）
- 26 个 substantive user turn，多为「再看下状态」「检查 si.inp model」「si.out 末尾报内存
  不足的有哪些」「各 job 消耗时间统计」
- 多次 bmatrix/bjobs 超时（SIGKILL），用户引导用 bmatrix/bjobs 查状态

## 选 trace 依据
- B 复活池（r618 reaudit 191 误杀）mc 排序：jhdvn(492)→D 已造 MBistAnalyze-001（cross-shard
  dup，本轮发现并跳过）；qzva9(253)→D 已造 IVCurveRegionClassify-001（cross-shard dup，跳过）；
  gwm47(86)→他 shard 仅 parked(eda_other) 非 case，B 域 spice_sim 合法认领
- B reaudit 拟造形态: debug-Q&A → 「根因诊断报告」check 验根因定位/证据引用/修复建议覆盖
- 实际合成: L1 离线日志分析器（trace 零脚本产物 ⇒ 把"读日志判状态"固化为 parser）

## 合成 case 设计（B-track L1, B 档 synthesized）
- A 档不可行: 真实任务需 live LSF bjobs/bmatrix + .75 内网 MatrixRun 目录, SUT 沙盒无
  LSF/内网 ⇒ 从 trace read_files tool_result 重建离线日志快照
- **SUT**: `finesim_job_report.py <matrix_run_root> <out_dir>` 解析 bjobs.txt/bmatrix.txt/
  job_index.tsv + 每 job 的 bsub.log/si.inp/si.out → 产出 finesim_job_report.json
  (total_jobs/status_counts/model/aging_model/mosrapath_commented_jobs/oom_jobs/
  max_progress_percent/completed_jobs/jobs[])
- **Asset A**: matrix_run_A (10 jobs, 1 dir Aging_HLTOL_RDBI_1008hr_step1): RUN=8/PEND=1/
  DONE=1/EXIT=0; model G5_CIP_Model_D5_v0d9_rev01; 1 个 _normal baseline(mosrapath ** 注释);
  1 个 OOM(Aging004_HTOL_SS_m40C, Cannot allocate memory); max_progress=80; 1 completed
- **Hidden B**: matrix_run_B (12 jobs, 4 dirs): RUN=6/PEND=2/DONE=3/EXIT=1;
  model G5_CIP_Model_D6_v1d2_rev03(≠A); 2 OOM; 2 mosrapath_commented; max_progress=90;
  3 completed — cross-input guard
- **Hidden B2**: matrix_run_B2 (3 jobs): RUN=1/PEND=1/DONE=1; model D7; 0 OOM/0 mosra;
  max_progress=50 — 确定性(3 rerun byte-identical) + tiny guard

## check.py（13 条断言 a–m, k_check==k_rationale==13）
独立 ground-truth resolver `_gt(root)`（whole-text regex/集合式，与 ref 的 line-by-line
状态机不同实现）+ 硬编码 A_GT 交叉校验。
- a: zip 含 report+script | b: A 顶层键 | c: A total=10 | d: A status 8/1/1/0
- e: A model+aging | f: A mosrapath_commented=[SS_normal] | g: A oom=[SS_m40C](OOM≠Peak mem)
- h: A max_progress=80 | i: A completed=[FF_m40C] + FF_125C elapsed_sec=56953.0
- j: B total=12 status 6/2/3/1 | k: B model≠A/oom=2/mosra=2/max=90/completed=3
- l: cross-input guard A≠B on model/total/oom/max | m: determinism B2 3 rerun identical + B2 值

## 自验
- ref submit.zip → check() **PASS**（all 13）
- 4 negatives → 全 **FAIL**: naive_hardcode_a(cross-input guard l)、empty_shell(b)、
  print_only(a/i)、core_deleted(g OOM=[] + h max=0)
- no-leakage: attachments 34 文件无 hidden/ ✓

## 覆盖分子
spice_sim 域 + FineSim/PrimeSim MatrixRun job 状态监控 + OOM/EXIT 诊断 + si.inp
model/mosrapath 配置核查。B-track L1 离线日志分析器。首例: finesim-job-status-monitor
+ OOM-vs-PeakMemory 区分首例 + mosrapath-commented baseline 检测首例。
