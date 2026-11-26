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

`CONTRACT: P1=1/1 done · P2=5 L2.live (TrMatchHelper-001 + FullAdderSchemBuild-001 + OpenDmViewsProduce-001 + AeDelCellCurCellProduce-001 + SelFigReport-001 done) · P3=497/608 judge_layers`

## r1446 交付：P2 第 5 条 check_live（SelFigReport-001）

- **候选选择**：对余 9 条 api 子类候选逐个核验 reference_solution 是否真调 pyAether
  （p2_pool 的 `pyAether-import` 指标来自关键字扫描，含假阳性）。核验结果：
  **仅 SelFigReport-001 真调 pyAether**（`sel_fig_report_ref.py` 里 `import pyAether as ae` +
  `ae.aeGetCurDesign()` + `cv.getSelectedFigs()`）。其余 8 条（WtmWriteCheckReviewQA /
  AutoPR / DirectivePairAudit / ExprLogicCheck / FindCir4CrossProbe / LvsConnDiagnose /
  McpSseApiDocParseProduce / VerdictJoinPassLib）的 reference solution 均无真实 pyAether
  调用——指标来自 check.py 注释/docstring 的关键字误命中，应归 P3（mock）。本轮选
  SelFigReport-001 实现 check_live（与 r1442-r1445 API 覆盖不重叠：r1442=match-helper,
  r1443=schematic-build, r1444=dm-views-open, r1445=cell-delete-current, 本轮=cur-design-selected-figs）。
- **原 check 状态**：已是 raise-on-fail（`_cond` raise AssertionError）+ `return True`，
  无 teeth bug；负样本 6 条全 FAIL（negative_selftest 走 `check()` compat 仍全 FAIL，无需改）。
- **非侵入包装**：`_check_static_impl` = 原 check 函数体逐字保留；`check_static` 三元组
  包装；`check_live` 新增；`check` 兼容包装。无需 abspath 修复（check.py 读 `workdir/spec_A.json`
  + `workdir/hidden`，框架 cd 到 g1/g2（workdir='.'）下 spec_A.json+hidden 均在，相对路径解析正确）。
- **check_live 策略** = strategy 1（fake-input graceful probe + spec-driven 探针）：
  upload submit.zip → .75 import 真实 pyAether 验证 `aeGetCurDesign` 属性存在 → monkey-patch
  `ae.aeGetCurDesign` 返回 LIVE fake cv（`type(LIVE_CV_TYPE, ...)` 动态类，`__name__`=
  `emyLiveProbe`，`getSelectedFigs` 返回 3 个 LIVE fig：Bus/Pin/Label）→ SIGALRM 90s →
  设 sys.argv 调候选 `main()`（候选 `import pyAether as ae` 在 main 内，拿已 patch 的模块）→
  断言 aeGetCurDesign+getSelectedFigs 被调 + exit0 + report 4 键齐全 + cv_type==`emyLiveProbe`
  （forces `type(cv).__name__`，非硬编码 emyDesign）+ n_selected==3 + 3 fig 的
  objType/n_points/width/layerName/selFigPoint 全匹配 LIVE spec（Bus 2pts/0.42/LiveLyr/[T,F,T]，
  Pin 1pt/0.77/PinLyr/[F]，Label 无 points/width→n_points=0/width=null/TxtLyr/[T]）+
  report blob 含 `emyLiveProbe`。
- **关键设计**：LIVE spec 与 A/B/B2/B3 结构性不相交——A/B/B2/B3 全用 cv_type=`emyDesign` +
  objType∈{Path,ArrayInst,Rect,Polygon}；LIVE 用 cv_type=`emyLiveProbe` + objType∈{Bus,Pin,Label}
  + 3 figs（A=2, B=1, B2=2, B3=0）。硬编码 A/B 的候选（如 naive_hardcode_a 写死 Path/M2/emyDesign）
  在 LIVE 下 cv_type/objType/layerName 全错 → FAIL；忽略 pyAether 的候选（naive_static_figs）
  aeGetCurDesign 未调 → FAIL。
- **自验**（全 PASS）：check_static REF PASS（L0+L1，原 16 条件 a-p 全过）；
  negative_selftest 6 neg ALL FAIL（empty_shell/print_expected/core_deleted/naive_hardcode_a/
  naive_no_selfig/naive_static_figs 走 `check()` compat 全 FAIL）；check_live(ref) via .75
  PASS（status=ok，aeGetCurDesign=1/getSelectedFigs=1/exit0/cv_type=emyLiveProbe/n_selected=3，
  infra_fail=0）；check_live(naive_static_figs) FAIL（aeGetCurDesign 未调 + cv_type=emyDesign +
  n_selected=2）；check_live(naive_hardcode_a) FAIL（cv_type=emyDesign + fig0 objType=Path≠Bus +
  layerName=M2≠LiveLyr + fig2 objType=Path≠Label）；**框架完整 L0+L1+L2.live 路径 PASS**
  （importlib 加载 check.py → check_static(submit.zip,'.')→(True,'','') → EDASession check_live→
  (True,'','')，infra_fail=0）。pure ASCII 探针代码。
- **case JSON**：metadata.judge_layers=[L0,L1,L2.live] + test 同步（21133 chars）+
  check_sha256=d33fd210...d161edbc + check_size=21169。

## r1445 交付：P2 第 4 条 check_live（AeDelCellCurCellProduce-001）

- **候选选择**：从余 10 条 api 子类候选中选第 4 条。AeDelCellCurCellProduce-001 是
  pyAether-import=3 的最强剩余候选（p2_pool_D.tsv 中 api 子类指标最高），候选
  del_cell.py 调 3 个真实 pyAether API（emyInitAether / mdeGetCurrentLibCellView /
  aeDelCell）。实测 .75 pyAether：3 API 全部 present。与 r1442/r1443/r1444 API 覆盖
  不重叠（r1442=match-helper 8 API, r1443=schematic-build 10 API, r1444=dm-views-open
  8 API，本轮=cell-delete-current 3 API）。
- **非侵入包装**：_check_static_impl = 原 check 函数体逐字保留（原 check 已是
  raise-on-fail + return True，无 teeth bug）；check_static 三元组包装（含 abspath
  修复，见下）；check_live 新增；check 兼容包装。negative_selftest 走 check() compat
  仍全 FAIL（无需改）。
- **路径健壮性修复（check_static wrapper 内）**：框架调 check_static 时传 workdir='.'
  而 _check_static_impl 把 candidate subprocess 跑在另一个 cwd (tempfile run_dir)，
  hidden B 的 cfg 路径 os.path.join(workdir,"hidden",...) 是相对的，从 candidate cwd
  解析不到。在 check_static wrapper 里加 `workdir = os.path.abspath(workdir)` 一行
  修复（不动 _check_static_impl 函数体，不改任何断言/严格度）。此 bug 此前未暴露因
  本 case 不在 lite-500 且从未经框架实跑。
- **check_live 策略** = strategy 1（fake-input graceful probe）：upload submit.zip →
  .75 import 真实 pyAether 验证 3 required API 属性存在 → monkey-patch 3 API
  （emyInitAether 记录、mdeGetCurrentLibCellView 返回 LIVE tuple 并记录、aeDelCell
  记录 + return True）→ SIGALRM 90s → 跑候选 del_cell.py（main 在 import 时执行）→
  断言 emyInitAether+mdeGetCurrentLibCellView 被调 + aeDelCell 恰好 1 次 + aeDelCell
  args == LIVE tuple (AeDelLiveLib/AeDelProbeCell/abstract) + 禁 A/B/A' token 泄漏
  (analogLib_A/invA/digitalLib_B/nandB/ioLib_B/bufB/rfLib_B/lcB/powerLib_Q/dffQ) +
  exit 0。LIVE tuple 与 A (analogLib_A/invA/schematic)、B 三 seed、A'-gold
  (powerLib_Q/dffQ/symbol) 全部结构性不相交 → B-hardcode / A-hardcode / file-reading
  stub 都打不掉 LIVE tuple。
- **关键设计**：候选在 .75 必然走 graceful（monkey-patch 后 mdeGetCurrentLibCellView
  返回 LIVE tuple，aeDelCell 返回 True，不 crash）。"live" 价值 = 真实 pyAether 模块
  在 .75 导入成功 + 3 API 属性名真实存在（typo API 会 AttributeError）+ LIVE spec
  防硬编码 A/B/A'。
- **自验**（全 PASS）：check_static REF PASS（L0+L1 17 条件 a-q）；
  negative_selftest 4 neg ALL FAIL（empty_shell/print_expected/hardcoded_a/
  neg_fake_hardcode_b）；check_live(ref) via EDASession PASS（infra_fail=0）；
  check_live(4 neg) ALL FAIL（no-engagement / A-tuple ≠ LIVE tuple / crash）；
  框架完整 L0+L1+L2.live 路径 PASS（judge_layers=[L0,L1,L2.live]，infra_fail=0）。
  pure ASCII 探针代码。
- **case JSON**：metadata.judge_layers=[L0,L1,L2.live] + test 同步（21963 chars）；
  reference_submit.zip 新建（1041B，含 del_cell.py）。

## r1444 交付：P2 第 3 条 check_live（OpenDmViewsProduce-001）

- **候选选择**：从余 11 条 api 子类候选中选第 3 条。OpenDmViewsProduce-001 是
  pyAether-import=8 的最强候选（p2_pool_D.tsv 中 api 子类指标最高），候选
  open_dm_and_views.py 调 8 个真实 pyAether API（emyInitAether/aeDMShow/
  aeGetDmWindow/aeOpenDesign/aeGetWndList/dbOpenCV/aeCreateWindow/aeDisplayWindow）。
  实测 .75 pyAether：8 API 全部 present（aeCloseAllWindows 缺失，但候选必须 NOT
  调它——anti-close 断言），与 r1442/r1443 API 覆盖不重叠（r1442=match-helper,
  r1443=schematic-build，本轮=dm-views-open）。
- **非侵入包装**：_check_static_impl = 原 check 函数体逐字保留（原 check 已是
  raise-on-fail + return True，无 teeth bug）；check_static 三元组包装；check_live
  新增；check 兼容包装。negative_selftest 改用 check_static（新契约返回值）。
- **check_live 策略** = strategy 1（fake-input graceful probe + spec-driven 探针）：
  upload LIVE 探针 lib+cells（OdvLiveProbeLib/OdvProbeCellA/B/C，与 A=ztest/AG_* 和
  B=analog_lib/pll_aux/rf_rx 都结构性不同）→ .75 上 import 真实 pyAether 验证 8 个
  required API 属性存在 → monkey-patch 设计类 API 记录调用 + 返回 graceful fake
  （候选不 crash）→ SIGALRM 90s → 跑候选 sut.main() with LIVE argv → 断言调了
  emyInitAether+aeDMShow(True)+每个 LIVE cell 的 aeOpenDesign(schematic+layout)+
  dbOpenCV+aeCreateWindow+aeDisplayWindow fallback + 禁 A/B token 泄漏 + 禁 aeClose* +
  exit_code==0。
- **关键设计**：monkey-patch 拦截设计类 API（aeOpenDesign 等返回 True/graceful），
  emyInitAether 也被 patch 记录（避免真实 init 需要 display/license）。"live" 价值
  = 真实 pyAether 模块在 .75 导入成功（证 `import pyAether` 工作）+ 8 个 API 属性名
  真实存在（typo'd API 如 ae.opnDesign 会 AttributeError）+ LIVE spec 防硬编码 A/B。
- **自验**（全 PASS）：check.py SELF-TEST PASS（L0+L1 12 断言）；negative_selftest
  3neg ALL FAIL（empty_shell/print_expected/delcore）；check_live(ref) via EDASession
  PASS（infra_fail=0）；check_live(3 neg) ALL FAIL（no-engagement / missing calls）；
  check_live(hardcode-B 候选) FAIL（不用 LIVE lib/cells）。pure ASCII 探针代码。
- **case JSON**：metadata.judge_layers=[L0,L1,L2.live] + test 同步（20189 chars）+
  check_sha256/check_size 更新；reference_submit.zip 新建（4530B，parity with FullAdderSchemBuild）。

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

1. P2 api 子类 13 条中已核验：5 条真调 pyAether 已完成 check_live（TrMatchHelper /
   FullAdderSchemBuild / OpenDmViewsProduce / AeDelCellCurCellProduce / SelFigReport）；
   **余 8 条（WtmWriteCheckReviewQA / AutoPR / DirectivePairAudit / ExprLogicCheck /
   FindCir4CrossProbe / LvsConnDiagnose / McpSseApiDocParseProduce / VerdictJoinPassLib）
   经 r1446 逐题核验 reference_solution 均无真实 pyAether 调用——指标来自 check.py
   注释/docstring 关键字误命中，应归 P3（mock），不再做 check_live**。⇒ **P2 api 子类
   已穷尽，D shard P2 实质闭合**（剩余真 EDA 候选须从 sim-keyword 97 条逐题深读发掘，
   多为 netlist 文本/注释假阳性，工作量大收益低，转 P4 适合性分析主导）。
2. P3：把上述 8 条假阳性 api 候选 + sim-keyword 子类中确属 mock 的 case 批量补声明
   `judge_layers=["L0","L1"]`（需逐题读 check.py 区分 netlist-text 假阳性 vs 真二进制调用）。
3. 造新题让位给 P2（运维令：P1>P2>P3）。P2 api 子类既已穷尽，下一轮转 P3 批量声明 +
   P4 实跑适合性分析。

## P2 api 子类 13 条（强候选 · r1446 核验后）

见 `contract_reform_p2_pool_D.tsv` subclass=api 行。r1446 逐题核验 reference_solution
真实 pyAether 调用情况：
- **真调 pyAether（5 条，已完成 check_live）**：TrMatchHelper / FullAdderSchemBuild /
  OpenDmViewsProduce / AeDelCellCurCellProduce / SelFigReport
- **假阳性（8 条，归 P3 mock）**：WtmWriteCheckReviewQA / AutoPR / DirectivePairAudit /
  ExprLogicCheck / FindCir4CrossProbe / LvsConnDiagnose / McpSseApiDocParseProduce /
  VerdictJoinPassLib（指标来自 check.py 注释/docstring 关键字误命中，reference_solution
  无 `import pyAether` / `ae.<api>` 真实调用）

---

## P4 实跑适合性分析 (r1447 · 2026-11-26)

本 shard Lite-500 case 数: 131（lite_health_D.tsv green 去重 133，剔除 2 条
REGRESSION-SWEEP/SPOTCHECK 非真实 case；磁盘 cases/D/ 实存 128 个，3 条 done-L2.live
之外另有 3 条 done case 不在 lite 集）。本轮逐 case 读 prompt+test(check.py)，按
「核心一问」判档：candidate 输出能让文本断言全过但 EDA 实跑不起/结果全错，pass 算不算数。

### 判档汇总

| 档位 | 数量 | 说明 |
|------|------|------|
| T1 适合实跑 | 4 | 3 条已 done(L2.live) + 1 条新候选 IOBufTune-001 |
| T2 可选增强 | 0 | 无收益足够高的可执行子部分（见下「T2 判定」） |
| T3 不适合 | 124 | 文本/结构判分够用，保持 mock |

### 判定方法与证据

全 128 lite case 扫 check.py（test 字段）的「真实 EDA 工具二进制调用」与
「pyAether 真实 import」，结果：
- **subprocess 调 EDA 工具二进制**：仅 1 条 `IOBufTune-001`
  （`subprocess.run(["hspice", "-i", sp, "-o", lis], ...)`）。
- **check.py 内 `import pyAether`**：2 条（SelFigReport-001 / SkillToAether-001），
  均已 done L2.live。
- **AeDelCellCurCellProduce-001**：check_live 经 sess.run_code 探针调 pyAether
  （非 check.py 顶层 import），已 done L2.live。
- 其余 124 条：check.py 要么纯文本/结构断言（regex/zipfile/json 字段比对），
  要么 subprocess 跑 candidate 的 python 脚本（sys.executable）后验输出结构；
  "hspice"/"calibre"/"finesim" 字样均为断言 token / forbidden-import 名单 /
  config 字段值 / pre-baked 仿真产物（.mt0/.csv/.fsdb）的文件名，非真跑。

### T1 清单（优先改造顺序）

| case_id | domain | 当前判分方式 | 实跑要调什么 | assets 齐备? | .75 可复跑? | 改造工作量(S/M/L) |
|---------|--------|-------------|-------------|-------------|------------|------------------|
| SkillToAether-001 | schematic_netlist | check_live 已 done（pyAether import+monkey-patch 探针） | 已 done | Y | Y | - |
| AeDelCellCurCellProduce-001 | schematic_netlist | check_live 已 done（sess.run_code pyAether 探针） | 已 done | Y | Y | - |
| SelFigReport-001 | analog_context | check_live 已 done（pyAether getSelectedFigs LIVE spec） | 已 done | Y | Y | - |
| IOBufTune-001 | analog_context | check_static 用 **hspice_mock**（reference/hspice_mock/hspice 是 python Shichman-Hodges transient mock，prepend PATH，候选与 grader 的 _rerun_hspice 均命中 mock 非 real hspice）；jl=[] 未声明 | check_live：upload submit.zip + spec_B/B2 到 .75 → 候选产 tuned params → **real hspice**（.75 PATH /apps/synopsys/...）rerun on hidden B/B2 → 断言 data_H≥0.99*vddq / data_L≤0.001；_rerun_hspice 逻辑已在 check.py 复用 | Y（spec_A/B/B2 + hidden_manifest 齐） | Y（hspice+hspice64+finesim 在 .75 PATH，MEMORY r1440 实测 exit=0） | M（2-4h：_rerun_hspice 改 sess.run_commands on .75，去 mock，补 check_live 三元组+judge_layers+test 同步+neg 重跑） |

### T2 清单

（空）候选复核：NetPathHL-001 / PGcheckTcl-001 / AutoCellDrcFlowGen-001 /
RsCalcFlow-001 等「写 SKILL/Tcl 脚本」类 case，check.py 均做文本结构断言
（API 名出现 / proc 存在 / 实例放置命令 / 正则）。可加 L2.live 辅助断言
（source TCL 进 Innovus / load .il 进 Virtuoso 验语法）但：① .75 无
Virtuoso/Innovus/calibre（shard C/A 工具域），② 语法 load 过≠语义对，收益
低于 env 搭建成本，③ 核心一问：脚本结构对即算交付（用户要的是正确结构的
编排脚本）→ 判 T3，不加 L2.live。

### T3 说明（124 条 · 不逐一列出）

分四子类，均为「文本/结构判分够用，保持 mock」：
1. **代码生成 + subprocess 跑 candidate python 脚本验输出结构**（~79 条）：
   candidate 写 parser/generator/report 脚本，check.py 跑它（sys.executable）
   验 JSON/文件结构/字段。EDA 工具不参与 candidate 任务（如 AddrRtlGateMap /
   CellMap / DecoderNetlistGen / LatchListMatch）。
2. **网表/波形文本分析 QA**（~25 条）：candidate 解析 .sp/.svwf/.fsdb/.mt0.csv
   文本，check.py 比对结构/数值。仿真产物 pre-baked（如 FineSimTskew /
   FsdbMeasRunGen / DominoPVTsweep / NetlistStructDiff）。
3. **deck/stimulus/脚本生成**（~15 条）：candidate 产 .sp deck / .svwf / TCL，
   check.py regex 验 .tran/.measure/proc 结构（如 BitcellMcSpGen / SpiceDeckGen /
   FifoTbStimGen / FinesimIgnoreGen）。结构对即交付。
4. **诊断/报告 QA**（~5 条）：candidate 产 Markdown/JSON 报告，check.py 验内容
   字段（如 Characterization / Backannot / FineSimJobMonitorImproveQA）。

### 与 P2 的关系 / 结论

P4 是 P2 前置分析。D shard lite-128 中真需 L2.live 的 T1 仅 4 条（3 已 done +
1 新候选 IOBufTune-001）。P2 api 子类既已穷尽（r1446），**唯一剩余 P2 工作 =
IOBufTune-001 加 check_live**（hspice 真跑 on .75，去 hspice_mock）。
T3 的 124 条保持 mock 判分，P3 批量声明 `judge_layers=["L0","L1"]` 即可。

下一轮：P2 收尾 IOBufTune-001 check_live（M 工作量），完成后 D shard P2 全闭合。
