# r599 deepread — e0014566/1n299 (RscalcFlowDocGen-001, layout_virtuoso)

## trace
- sid: `1786439419749_1n299`  user: `e0014566`  host: `hfeg0plg58` (10.129.8.221)  mc=64
- keywords: `virtuoso:240; .gds:73; drc:28; cadence:28; cellview:15; calibre:11`
- msgs: 124 total / 62 user_input
- working dir on .75-host: `/home/e0014566/test_layout_rscalc_flow_9/`

## user intent (real, trace-faithful)
- UI#0: 「请你结合 prompt_flow.md 这个流程说明，对我们这个流程做个详细的说明，出个文档。」
- UI#29: 「标题和内容都改为英文，不然有乱码」
- => produce-task: 读流程说明 + 配置，写结构化英文文档。

## what the agent did (real trace)
- run_commands (eda_flow MCP) on .75-host: ls/find 流程目录 → 读 prompt_flow.md(16KB) +
  common.config + rscalc.config + 各 runner SKILL.md + adaptive_tuner_design.md +
  adaptive_plan_iter*.json + *.log/.out 交叉印证。
- 写 `流程详细说明文档.md` (中文初版) → 按 UI#29 改写为 `flow_documentation.md`
  (768行/37KB/11章节全英文) → 删除中文版 → grep 确认无 CJK 残留。
- 11 章节: Goal / Config / Metric&Convergence / DataFlow / Environment / Runbook /
  AdaptiveTuning / ToolInternals / Troubleshooting / FlowDiagram / FileInventory。

## source spec (prompt_flow.md, A 输入)
Resistance-Reduction Flow — RsCalc + AutoVia + PowerFill:
- 3 tools: RsCalc(virtuoso-rscalc-runner) / AutoVia(virtuoso-autovia-runner) / PowerFill(virtuoso-powerfill-runner)
- loop: RsCalc(baseline) -> [AutoVia -> PowerFill -> RsCalc] x N
- convergence: R_i(p) <= R_0(p) * (1 - targetReduction) for all p (per-check-point)
- resistance column #12 in *.rvn; position key net_layer_x_y (cols 3,4,5,6)
- cell scheme: <orig>_via<i> (AutoVia), <orig>_opt<i> (PowerFill)
- common.config: process=cxmt10G4plus, project=train, libName=austin_rscalc2,
  cellName=testa, viewName=layout, targetReduction=0.5, maxIterations=5
  (实际运行态 common.config: targetReduction=0.3, maxIterations=3, cellName=testpg1_opt2)
- 4 config files: common.config / rscalc.config / run_autovia_config.il / run_powerfill_config.il
- pwrNets NOT shared: RTEXT(vdd) / GDS-text(vdd!) / GDS-text(vdd!)
- env: env -u ARGUS_HOME _CXMT_SH_PROJ_WRITE_CHECK=1 OA_UNSUPPORTED_PLAT=... LD_PRELOAD=...

## B档 mock-behavioral reframe (承 r597/r594/r588 script-task 模式)
- 把"读流程说明+配置写英文文档"参数化为纯 Python3 `rscalc_flow_doc_gen.py <flow_spec.md> <common.config> <rscalc.config> <out.md>`
- 脚本解析(非硬编): 标题(首#行) / 3工具名+skill-dir+用途(`N. **Tool** (\`dir\`)`) /
  电阻列号(`column #N = resistance`) / 收敛公式 / cell scheme(`<orig>_xxx<i>`) /
  配置文件表 / pwrNets变体 / 环境变量 / goal+loop / notes(section 7) ;
  common.config 解析 process/project/libName/cellName/viewName/targetReduction/maxIterations ;
  rscalc.config 解析 pwrNets/version/runDir/metalOption/divMetRatio/parallel.
- 输出 7 ## 章节英文 markdown.

## hidden B / B2 (反硬编)
- B: IR-Drop Reduction Flow — ResCalc + ViaBoost + RailFill
  common_B: process=cxmt10G5, project=ddgot, libName=irdb_austin, cellName=irnp1,
  targetReduction=0.4, maxIterations=6; column #14; scheme vb/rf
- B2: Electromigration Reduction Flow — EmCalc + WireWiden + VoidFill
  common_B2: process=cxmt10G7, project=drgqa, libName=emdb_chip, cellName=emnet0,
  targetReduction=0.25, maxIterations=4; column #10; scheme ww/vf
- B 不含 A 工具名/列号/scheme; B2 不含 B 工具名 + B2 自有 tr/scheme → 测真解析.

## check.py — 15 条 a-o (k=15>=8)
a zip含脚本 / b py_compile / c B exit0产非空md / d #标题 / e 纯英文无CJK /
f B三工具名全有 / g 无A工具名 / h B的tr(0.4) / i B的max(6) / j B的process(cxmt10G5) /
k 收敛公式 / l B列号(#14)非A(#12) / m B scheme(vb/rf)非A(via/opt) / n >=6 ##章节 /
o B2反硬编(B2工具名+tr0.25非B工具名)+确定性(B重跑字节一致除生成时间行).

## 自验
- SELFTEST ref 15/15 PASS ✓
- 3 neg (empty/print_only/deleted_core) 全 FAIL ✓ ; NEGATIVE_SELFTEST ALL-FAIL-OK ✓
- §4.9 三假 (empty_zip/print/deleted_core) 全 FAIL ✓
- framework wrapper bool(check)=True ✓
- embedded test==disk roundtrip ✓ (hash 00ebc0999577)
- k_rationale==k_check==15 >= 8 ✓
- C.jsonl 365→366 ; ledger_C case 366→367 (layout_virtuoso 68→69)

## 谱系
- produce-task 子型: doc-generation-from-flow-spec (layout_virtuoso 域)
- mock-behavioral check mode 第七实例化 (承 r539/r528/r530/r541/r542/r544 pg_layout + r588/r593/r594/r597/r598 physical_verify)
- anti-hardcode dual-hidden-fixture (B双工具组/B2三工具组)
