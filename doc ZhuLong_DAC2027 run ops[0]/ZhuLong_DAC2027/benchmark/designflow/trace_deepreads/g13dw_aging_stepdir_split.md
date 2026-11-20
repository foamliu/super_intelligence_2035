# trace_deepread: g13dw — aging step1/step2 sim dir split

- **session**: `1791768325372_g13dw.messages.json` · user `dandans` · host `hfeg0pkn002` · mc=58 · 16 msgs
- **tools**: netlist:9 hspice (FineSim matrix coverage sim-runner Perl script editing)
- **attachment**: `matrixrun` = `cxmt_runMatrixSim.pl` (3523-line internal CXMT FineSim coverage sim runner Perl script)

## User turns (verbatim)
- **U#0 (msg#0)** — 提需求（A-faithful 候选，未指根因/未给修复）:
  > 修改aging部分的代码，使得step1的仿真放在同一个目录，step2的仿真统一放在另一个目录
  （附带 matrixrun = cxmt_runMatrixSim.pl）
- **U#1 (msg#13)** — 用户贴回 aging 代码块（context，非新需求；含 `if($aging){... reltotaltime 校验 ... eageba_source_file sprintf finesim.mraprint@ra=...}` 片段）

## Assistant 行为
- A#1 read_files（attached matrixrun）→ A#3 search_codebase（aging）→ A#5 read_files（policy 拒）→ A#7/A#9 run_commands（policy 拒）→ A#11 editor placeholder（policy 拒）→ A#14 run_commands grep aging subs → **msg#15 tool_result: "Agent policy unavailable; fail-closed denial"** → 会话终止，agent 未完成修复。

## A#14 thinking 揭示的修复结构（金标准依据）
当前布局（matrixrun aging 块）：
```
$MatrixDir/<sim>_step1/                          <- step1 仿真直接挂 MatrixDir
$MatrixDir/<sim>_step1/AgingStep2Sim/<sim>_step2/   <- step2 仿真嵌在各自 step1 下
```
用户要求的新布局：
```
$MatrixDir/step1/<sim>/    <- 所有 step1 仿真同一目录
$MatrixDir/step2/<sim>/    <- 所有 step2 仿真另一目录
```

## 造题决策
- **trace 无用户接受结果**（agent 因 agent-policy 拒绝未产出）→ 不能做 A-faithful（无金标准）；A#14 thinking 已清晰给出目标结构 → **B-grade synthesized**。
- 真实 matrixrun 是 3523 行内部 CXMT Perl（私有/敏感 + 过大）→ 复刻为精简版 `matrixrun_A.pl`（保留 aging 两步目录构建 + write_runfile + GetOptions/--aging/--dryrun）。
- 候选交付 = `aging_dir_rewrite.py <input.pl> <output.pl>`，参数化改写器（非一次性文件编辑），便于隐藏 B 跨输入验证。
- 隐藏 B：`matrixrun_B.pl` 结构不同（`$MatrixBase`/hspice/`_step_one`+`_step_two`/`StepTwoSims`/reg,corner,w/--matrixbase/--simtool/build_sim_name+emit_runfile/cfg saRef,saDrv,saPipe），反硬编码。
- 判分 L2：真跑 `perl <out>.pl --aging` 生成目录树 + 文件系统巡检（非纯文本相似）。
- 15 条 a-o：含 A 实跑目录树(step1/step2 顶层+无 AgingStep2Sim+子目录数与 .run 内容)、隐藏 B 跨输入实跑(无 StepTwoSims)、反硬编码(out_B 不含 A token)、3-seed 确定性。
- 自验：ref PASS 15/15 + §4.9 三假(empty→c / print_only→d / core_deleted→f)全 FAIL distinct + 2 naive(hardcode_a→n / only_step1→g)全 FAIL distinct + negative_selftest NEG_RC=0 + 3-run md5 一致。

## 与已有 case 的区分
- 非重复：本 case 改 Perl 仿真器**目录布局**（aging step1/step2 分目录），与 NetlistStructDiff(网表 subckt diff)/CapInsertStgOut(.sp 插电容)/SPFNetlistCompare(SPF 寄生 diff) 文件格式+操作维度均不同。
