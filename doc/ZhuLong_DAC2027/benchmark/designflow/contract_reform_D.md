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

`CONTRACT: P1=1/1 done · P2=1 L2.live (TrMatchHelper-001 done) · P3=497/608 judge_layers`

## r1442 交付：P2 首条 check_live（TrMatchHelper-001）

- **候选选择**：实测 .75 pyAether API 存在性 → TrMatchHelper 候选用的 8 个 API
  （`aeGetCurDesign`/`aeGetSelectedSet`/`aeEmyInstGetParameter`/`cdfGetInstCDF`/
  `aeSetBindKeys`/`leGuiDeviceMatch`/`leGuiDistrAlign`/`emyInitAether`）**全部 present**
  （对比 SelFigReport 的 `cv.getSelectedFigs` / AutoPR 的 `aeAutoPlacementFromDesign`+`doLogicRouter`
  均为 mock-invented，MISSING on real pyAether → 弃选）。TrMatchHelper 是全 real-API 候选，
  清单见 `contract_reform_p2_pool_D.tsv` subclass=api。
- **非侵入包装**：`_check_static_impl` = 原 `check` 函数体逐字保留；`check_static` 三元组包装；
  `check_live` 新增；`check` 兼容包装。
- **顺带修 2 个 pre-existing teeth bug**（2026-11-24 运维令覆盖）：
  1. `check()` 末尾 `return True` 无条件（teeth bug，bad candidate 一律 PASS）→ 改为
     `raise AssertionError(列失败条件)` restore teeth。
  2. `negative_selftest.py` 期望 `ok,res,msg = check(...)` 3-tuple 但 check 返 bool →
     `TypeError: cannot unpack` → 改调 `check_static` 3-tuple。§4.9 三假
     (empty/print_only/core_deleted) 之前因 teeth bug 全 PASS，现全 FAIL。
- **check_live 策略** = strategy 1（fake-input graceful path，最稳）：
  - upload+unzip+py_compile candidate on .75
  - probe real pyAether：8 个 API 均为 real callable（证候选 API 名真实，非 invent）
  - exec 候选源码进 real pyAether 解释器（SIGALRM 90s 防 GUI hang）
  - 实测 .75 无 design open 时 `aeGetCurDesign()` 返真实 emyDesign（empty selection）→
    候选 graceful 打印 `need >=2`（证真实读 selection，非硬编码 8 MOS）
  - 禁 mock-B 硬编码 token（`Total: 8 MOS` / `[ptn_lv][ntn][ptn_m]`）→ 实跑抓到硬编码候选 FAIL
- **framework 兼容修复**：`_check_static_impl` 的 `_load_mock` 经 importlib 导入 mock_pyAether_B.py
  会副作用写 `hidden/__pycache__`，让 run_one.sh L2.live 的 `for hf in os.listdir('hidden'): open(...)`
  循环 `IsADirectoryError` 崩 → `check_static` 包 `sys.dont_write_bytecode=True` + `finally` 清
  `__pycache__`（wrapper 层修复，不动断言逻辑）。
- **自验**：
  - reference `check_static` PASS（14/14 conditions）+ `check_live` PASS（infra_fail=0）
  - 框架 L0+L1+L2.live 全路径 PASS（复刻 run_one.sh judge python）
  - `negative_selftest.py` 4 neg ALL FAIL（empty/print_only/core_deleted/hardcode_A）
  - `check_live` 单测：ref PASS / neg_print_only FAIL（mock-B tokens）/ neg_empty FAIL（no engagement）
  - neg_core_deleted / neg_hardcode_A 在 check_live PASS（call real pyAether）但被 check_static 捕获
    → static+live 组合正确：硬编码 mock-B 候选过不了 live，缺逻辑候选过不了 static
- **case JSON**：`metadata.judge_layers=["L0","L1","L2.live"]` + `test` 字段同步 + 新增 `reference_submit.zip`。
- **EDA-Flow-Bench 净变更**：4 files（check.py / negative_selftest.py / case JSON / reference_submit.zip）。

## 下一轮计划

1. P2：从 13 条 api 子类候选中选 1 条，按 SkillToAether 模板实现 `check_live` + `judge_layers=["L0","L1","L2.live"]`，SKIP_RUN + 真 L2.live 验证
2. P3：继续逐批把 sim-keyword 子类中确属 mock 的 case 补声明（需逐题读 check.py 区分 netlist-text 假阳性 vs 真二进制调用）
3. 造新题让位给 P2（运维令：P1>P2>P3，造题让位 P1/P2）

## P2 api 子类 13 条（强候选）

见 `contract_reform_p2_pool_D.tsv` subclass=api 行（AeDelCellCurCellProduce / SelFigReport / OpenDmViewsProduce / TrMatchHelper / FullAdderSchemBuild / WtmWriteCheckReviewQA / AutoPR / DirectivePairAudit / ExprLogicCheck / FindCir4CrossProbe / LvsConnDiagnose / McpSseApiDocParseProduce / VerdictJoinPassLib）。
