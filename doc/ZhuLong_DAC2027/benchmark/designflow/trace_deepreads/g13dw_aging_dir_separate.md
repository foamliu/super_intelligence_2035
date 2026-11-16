# trace deepread: g13dw (dandans @ hfhds201) — aging sim dir separation

## session meta
- session: 1791768325372_g13dw (子目录模式，非根 .messages.json)
- user: dandans @ hfhds201 (10.129.32.75 = .75 本机)
- match_count: 16 (spice_sim domain, B shard)
- msgs: 16 (trace 171KB messages.json + 2503B .json metadata)
- agent: lead (cline)
- date: 2026-10-12

## user intent (trace verbatim)
- U0: 「修改aging部分的代码，使得step1的仿真放在同一个目录，step2的仿真统一放在另一个目录」+ attached file: matrixrun (127029B, 3524 行 Perl)
- U13: 补贴 aging 代码片段 (if($aging){... reltotaltime validation ... create step1 sim dir ...})

## current aging structure (matrixrun lines 243-354)
- aging guard: `if($aging) { ... }`
- step1 仿真目录: 建在 `$MatrixDir` 下, 名字 `$Simulator.$regName.$pvt.$width` + `_step1` 后缀
  - `my $simDirName = "$Simulator.$regName.$pvt.$width". "_step1";`
  - `my $oneSimDirPath = createSimDir($MatrixDir, $simDirName, $stimuDir, $width);`
- step2 仿真目录: **嵌套**在 step1 目录内的 AgingStep2Sim 子目录
  - `my $agingStep2SimDir = "$MatrixDir/$simDirName/AgingStep2Sim";`
  - `system("mkdir -p $agingStep2SimDir");`
  - step2 名字带 `_step2` 后缀, 建在 `$agingStep2SimDir` 下
- 保留调用: createSimDir / genSimTestbench / genAgingStep1SimTestbench / genAgingStep2SimTestbench / genSimRunFile / genAgingRunFile / getSimList / SetGlobalPath

## agent 行为
- 读 matrixrun 分析 aging 段, U13 补贴代码, 但 trace 在 U15 截断 (assistant "Let me read the full file..."), **agent 未完成 edit**
- 旧判 parked 理由: "incomplete trace, assistant never produced edit"

## 复活判定 (11-15 标准)
- 11-15 用户令唯一排除: ①无真实 trace ②写不出有牙 check
- 本 session: 真实 trace ✓ (用户原话 + matrixrun 真实附件 + aging 代码 verbatim) ; agent-完成度非排除理由 (ref solution 自撰)
- 可造 ✓ → r697 复活变现 #76

## 合成 case
- EDA-Eval-DesignFlow-AgingDirSeparateTransform-001 (characterization)
- A档 trace-faithful (用户原话作 prompt)
- deliverable: aging_dir_restructure_analyzer.py (Python stdlib, regex 解析 Perl aging 段 → 结构化 JSON 报告)
- fixture: ①档 text-direct (Perl 文本正则解析, 0 EDA-tool mock, 0 仿真器依赖)
- task-form reframe: Q&A-intent(改代码) → produce-deliverable(分析器+JSON 报告)
- hidden B: 结构相同, 命名全异 ($agingEnabled/_phase1/_phase2/$RunDir/Phase2Sims/mempsi/makeSimDir/genSimTb/...)
- check.py: 20 断言 (cross-input guard 7 条 + A-leak 2 条 + B-grounding 1 条 + 确定性 + 结构 + 解嵌套)
- 自验: ref 20/20 PASS + 4 negs 全 FAIL
