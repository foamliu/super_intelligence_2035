# 判分契约改造 · shard D 进度 (r1441 起 · 2026-11-26)

> 指南：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/CONTRACT_REFORM_GUIDE.md`
> 心跳格式：`CONTRACT: P1=<done>/<12> · P2=<n> L2.live · P3=<n>/<total> judge_layers`

## 本轮 r1441 交付

- **P1（pilot 12）**：D 唯一 pilot case `SkillToAether-001` 已验证完整
  - `metadata.judge_layers = ["L0","L1","L2.live"]` ✅
  - reference/check.py 含 `_check_static_impl` / `check_static` / `check_live` / `check` 兼容包装 ✅
  - case JSON `test` 字段已同步（含 check_live）✅
  - **P1 D = 1/1 done**（全 bench P1 = 12/12 待其他 shard 确认）
- **P3（mock case 声明 judge_layers）**：本轮批量声明 **497/608**
  - 497 个 mock case 加 `judge_layers=["L0","L1"]`（commit `581a5b7fa`，EDA-Flow-Bench master）
  - 行为保持：框架对 `["L0","L1"]` + 旧式 `check()` 走 fallback，L2.live 不触发 → 与改造前完全一致
  - 验证：直接对 `Backannot-001` / `Characterization-001` 跑 reference_submit.zip 经 `check()` fallback → REF PASS；SKIP_RUN 行为不变
  - 110 个 real-EDA 指标 case **未声明**，留待 P2 分类（避免误把真 EDA case 标 mock 而跳过 L2.live）
- **P2（扩展真 EDA case 到 L2.live）**：本轮完成 **scoping**（未实现 check_live）
  - 候选池：`designflow/contract_reform_p2_pool_D.tsv`（110 条）
  - **api 子类（强 P2，直调 pyAether/SKILL/Tcl）= 13 条**（优先做）
  - sim-keyword 子类（hspice/finesim/virtuoso 关键词，多为 netlist 文本/注释假阳性）= 97 条（需逐题读，多数仍是 mock）

## 心跳

`CONTRACT: P1=1/1 done · P2=2 L2.live (TrMatchHelper-001 + FullAdderSchemBuild-001 done) · P3=497/608 judge_layers`

## r1443 交付：P2 第 2 条 check_live（FullAdderSchemBuild-001）

- **候选选择**：从 13 条 api 子类候选中选第 2 条。实测 .75 pyAether API：
  FullAdderSchemBuild 候选用 10 个 API（emyInitAether/aeOpenDesign/aeGetCurDesign/
  aeDesignIsEditable/dbOpenCVByType/dbCreateInst/dbCrtNet/dbCrtTerm/aeSaveDesign/emyString）
  全部 present（与 r1442 TrMatchHelper 的 8 API 子集完全不重叠，除 emyInitAether/aeGetCurDesign
  公共底座；P2 API 覆盖从 match-helper 扩展到 schematic-build）。
- **非侵入包装**：_check_static_impl = 原 check 函数体逐字保留（原 check 已是 raise-on-fail +
  return True，无 teeth bug）；check_static 三元组包装；check_live 新增；check 兼容包装。
- **check_live 策略** = strategy 1+（fake-input graceful path + spec-driven 探针）：
  upload LIVE 探针 spec.json（LiveProbeLib/ProbeCell, 2 gates，结构上与 A=FullAdder_3 5 gates /
  B=Mux2to1 4 gates 都不同）-> monkey-patch ae.* 记录调用 + SIGALRM 90s -> 断言调了
  emyInitAether+aeOpenDesign+aeGetCurDesign + aeOpenDesign 用 LIVE spec 的(lib,cell) 不是硬编码
  A/B cell + 禁 mock-B token。
- **关键设计**：候选在 .75 必然 crash（LiveProbeLib/ProbeCell 不存在）-> crash 是 ACCEPTABLE
  （证候选走到 design-handle 步骤），只 reject 无 engagement / 用错 cell。
- **自验**（全 PASS）：reference check_static PASS（16/16）+ check_live PASS（infra_fail=0）；
  框架 L0+L1+L2.live 全路径 PASS；negative_selftest 6neg ALL FAIL；check_live 单测 7 候选
  ref PASS / neg_empty+neg_print_expected FAIL / neg_hardcode_fulladder FAIL / 
  neg_core_deleted+neg_no_save+neg_wrong_topology PASS（spec-driven, static catches）。
- **case JSON**：metadata.judge_layers=[L0,L1,L2.live] + test 同步（24630 chars）+
  check_sha256/check_size 更新；reference_submit.zip 已存在不动。

## 下一轮计划

1. P2：从余 11 条 api 子类候选中选下一条（OpenDmViewsProduce / AeDelCellCurCellProduce / WtmWriteCheckReviewQA / DirectivePairAudit / ExprLogicCheck / FindCir4CrossProbe / LvsConnDiagnose / McpSseApiDocParseProduce / VerdictJoinPassLib 等），按 SkillToAether 模板实现 `check_live`
2. P3：继续逐批把 sim-keyword 子类中确属 mock 的 case 补声明（需逐题读 check.py 区分 netlist-text 假阳性 vs 真二进制调用）
3. 造新题让位给 P2（运维令：P1>P2>P3，造题让位 P1/P2）

## P2 api 子类 13 条（强候选）

见 `contract_reform_p2_pool_D.tsv` subclass=api 行（AeDelCellCurCellProduce / SelFigReport / OpenDmViewsProduce / TrMatchHelper / FullAdderSchemBuild / WtmWriteCheckReviewQA / AutoPR / DirectivePairAudit / ExprLogicCheck / FindCir4CrossProbe / LvsConnDiagnose / McpSseApiDocParseProduce / VerdictJoinPassLib）。
