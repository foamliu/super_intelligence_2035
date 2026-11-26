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

`CONTRACT: P1=1/1 done · P2=7 L2.live 全闭合 · P3=609/609 judge_layers 全声明 · P4=done`

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

## r1449 交付：P3 批量收口（105 case 补声明 judge_layers）

- **背景**：D shard P1/P2/P4 全闭合后，唯一余 contract 工作 = P3 批量声明。
  r1441 已声明 497/608，余 105 case 无 judge_layers（8 api 假阳性 + 97 sim-keyword，
  均经 r1446 逐题核验 reference_solution 无真实 pyAether 调用 + r1447 P4 复核为 T3 mock）。
- **本轮**：对 105 case 批量加 `metadata.judge_layers=["L0","L1"]`。
  - 104 case 多行 metadata：在 `"metadata": {` 后插入首键。
  - 1 case（BtopPoststressJobs-001）单行 compact metadata：在 `"metadata":{` 后插入。
- **结果**：609/609 全声明（602 L0L1 + 7 L2.live）。行为保持 check() fallback（框架对
  ["L0","L1"] + 旧式 check() 走 fallback，L2.live 不触发，与改造前完全一致）。
- **自验**：SKIP_RUN=1 eval/run_one.sh AgingStepDirSplit-001 --shard D → judge 步骤无报错
  （verdict=FAIL 仅因 SKIP_RUN 无 submit.zip，非 check.py 回归）。
- **D shard CONTRACT 全闭合**：P1=1/1 · P2=6(+1 pilot=7 L2.live) · P3=609/609 · P4=done。

## r1448 交付：P2 收尾第 6 条 check_live（IOBufTune-001）— D shard P2 全闭合

- **候选选择**：P4 实跑适合性分析（r1447）确认 D shard lite-128 中真需 L2.live 的 T1
  仅 4 条，3 条已 done（SkillToAether / AeDelCellCurCellProduce / SelFigReport），**唯一
  余项 = IOBufTune-001**（当前 check_static 用 `hspice_mock`：reference/hspice_mock/hspice
  是 python Shichman-Hodges transient mock，prepend PATH，候选与 grader 的 _rerun_hspice
  均命中 mock 非 real hspice；jl 未声明）。本轮实现 check_live 把判分从 mock 升级到
  .75 real PrimeSim HSPICE，闭合 D shard P2。
- **.75 实跑通路核验**（probe）：`which hspice` = `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/
  hspice/linux64/hspice`，单 deck `.tran 0.02n 10n` 0.1s/run，license checkout OK
  （`lic: Release primesim token(s)`）。real `.mt0` 格式：
  `$DATA1 SOURCE='PrimeSim HSPICE' ...` + `.TITLE` + 头 `data_h data_l temper alter#`
  + 数据行——候选的 `run_hspice` 解析器（hdr 含 data_h+data_l → 首行首字符数字/-）兼容。
- **关键发现（probe bug 排查）**：首次 probe 用相对 `--outdir out_B`，候选 `run_hspice`
  设 `cwd=run_dir` 但传相对 sp/lis 路径 → hspice cwd 错位找不到 .sp → 全 40 trial meas=None
  → satisfied=false。根因是候选的路径逻辑依赖绝对 outdir（check.py 的 `_run_candidate`
  用 `tempfile.mkdtemp` 绝对路径，故历史 mock 路径一直正常）。check_live 改用**绝对
  outdir**（`wd + "/live/out_B"`）即正常：B trial5(LR56=125.97) data_h=1.1996≥1.188 /
  data_l=2.32e-4≤0.001；B2 trial2(LR56=178.6) data_h=0.9991≥0.95 / data_l=3.17e-4≤0.0005；
  B vs B2 distinct=True。
- **非侵入包装**：`_check_static_impl` = 原 check 函数体逐字保留（原 raise-on-fail +
  return True，无 teeth bug）；`check_static` 三元组包装；`check_live` 新增；`check`
  兼容包装；`__main__` 改用 check_static 三元组（保持 rc=1/FAIL 给 negative_selftest）。
  check_static 仍用 `hspice_mock`（eval host 无 real hspice），行为不变。
- **check_live 策略** = real-hspice rerun（无 mock）：upload submit.zip + hidden spec_B/B2
  （框架已 upload_text 到 wd root）→ unzip + py_compile + 验 real hspice present →
  anti-hardcode-A（源码无 A 字面量）→ 候选用 **real hspice** 跑 B（绝对 outdir）→
  读 tuned_params 验 satisfied=True + 5 参数在 B 范围 → `_live_rerun` 上传 `live_rerun.py`
  helper（纯 ASCII，镜像 _rerun_hspice+_parse_mt0）用 real hspice 重跑 tuned params →
  断言 data_h≥0.99*VDDQ_B / data_l≤0.001 → 同样跑 B2 + real rerun 断言 data_h≥0.95*VDDQ_B2
  / data_l≤0.0005 → B vs B2 distinct。
- **L2.live 价值/teeth**：mock 是 level-1 Shichman-Hodges 的 python 近似（LAMBDA=0.05，
  forward-Euler），real 是工业 PrimeSim HSPICE。check_live 让候选在 real hspice 下搜索
  参数并 real rerun 确认，凡过拟合 mock 数值怪癖（LAMBDA/积分误差）的候选在 real 下
  data_h/data_l 不达标 → FAIL。B2 cross-input guard + real rerun 同时打掉 hardcode-A
  （A 的 WP1=3.0 在 B2 range [0.8,2.5] 外）。
- **自验**（全 PASS）：check_static REF PASS（L0+L1 16 条件 a-p，mock）；negative_selftest
  6 neg ALL FAIL（empty/print_expected/core_deleted/naive_stub/no_target_check/hardcode_a
  走 check() compat 全 FAIL，NEG_RC=0 CRASH_RC=0）；check_live(ref) via EDASession 框架
  完整路径 PASS（L0+L1+L2.live all PASS，infra_fail=0）；check_live(6 neg) 直接调 ALL FAIL
  （hardcode_a=A-literals / naive_stub+print_expected=B live data_h=1.1779<1.188 /
  no_target_check=B live data_h=1.0603<1.188 / empty=tuned_params unparseable /
  ref_core_deleted=A-literals 12345）。pure ASCII 探针代码。
- **case JSON**：metadata.judge_layers=[L0,L1,L2.live] + test 同步（24939 chars ==
  check.py 字节一致）commit `0d240e9e4` 已 push master；check.py（含 check_static/
  check_live/compat）由 shard B 的 broad `git add` commit `a68b3b6da` 一并入库（边界
  注记见下，内容正确未回退）。
- **边界注记**：shard B commit `a68b3b6da`（2026-11-26 12:00:09）broad `git add` 把
  D shard 的 IOBufTune-001/check.py（+225 行 = 我的 check_live 实现）连同 A 的
  NetCellMap-001/check.py 等多 shard 文件一并提交——B 越界 + broad add 违纪。但 D 的
  check.py 内容正确（我的实现逐字），未回退；D 只单独 commit 自己的 case JSON
  （0d240e9e4）。已在 discuss/D.md 留观察项。

## 下一轮计划

1. **D shard CONTRACT 全闭合**（r1449）：P1=1/1 · P2=7 L2.live · P3=609/609 · P4=done。
   contract 改造工作全部完成，无遗留。
2. 造题恢复（运维令：P1>P2>P3，三者既闭合，造题不再让位）。下一轮走 trace_ledger
   --shard D next → claim → 深读 → 合成 → 自验。
3. 跨 shard P0 监控：OpampChar-001（B-shard，挂 101+ 轮）待 B 接管。

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

---

## Live-eval 审视（2026-11-26 用户令 · R1 只读重判）

> 规格：`BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`。本节为 D shard R1 产出（冻结窗口 zhulong r3' 进行中，**只读审视、未落盘判分**）。名册 `live_eval_review_D.tsv`（121 条）全量填满 verdict/reason/evidence/round。id 归一化：短名匹配前统一剥 `EDA-Eval-DesignFlow-` 前缀。

### 三分类合计

| verdict | 数 | 说明 |
|:--|--:|:--|
| LIVE-REQ | 3 | 3 已 L2.live（IOBufTune/SelFigReport/SkillToAether，r1442-1448 改造完成）—— **REQ 轨全部闭合，0 pending** |
| LIVE-OPT | 9 | mock-pyAether 编排族 5（AutoCellRmAvPf/HierDescend/RsCalcFlow/RsCalcRnodePlace/PyaetherScreenshotVerifyQA）+ 优化/sweep 族 3（DlySigmaSweep/LDOGen/DominoPVTsweep）+ **InvCSOpt-001（R2-prep 探针证 check_live 物理验证 BLOCKED，降 REQ→OPT）**|
| LIVE-NA | 109 | deliverable=文本/脚本/日志分析/网表变换/诊断报告/问答 + python模型独立复算族（IOBufParamTune-001）；check 跑候选 python 脚本校验输出结构，EDA 工具名仅作断言 token |
| **合计** | **121** | |

> **R1.5 深读复验（2026-11-26 19:3x，冻结窗口只读）**：对 R1 判的 2 新 REQ + DominoPVTsweep Vm 来源做深读 check.py 复验。**IOBufParamTune-001 改判 REQ→NA**（R1 误判「无独立复算」，实为条件 (f)(g) 经 `evaluate()`=Shichman-Hodges RC 模型独立复算 dataH/dataL，(h)(i) 验目标，Q2 不会判过；prompt 显式 level-1 模型 + deck level=1，真 HSPICE 无增量；与 IOBufTune-001 不同族——后者 hspice_mock 假仿真输出，本例纯 python 模型独立复算）。**InvCSOpt-001 维持 REQ**（gap 在条件 (p)：best_design.json 的 delay/idd/duty 为候选自报无独立复算/真跑，(m)(n) parse_meas 仅验 parser 于 pre-baked mt0 不连 best_design；Q2 会判过=候选写 fake feasible 通过）。**DominoPVTsweep-001 维持 OPT**（Vm 来源已确认=hidden B mt0 CSV 经 `_recompute()` 独立复算，非候选自报；条件 (o) 公式 guard 防 VMLH-only；Q2 不会判过，不升 REQ）。

> **R2-prep 探针（2026-11-26 19:5x，冻结窗口只读 .75 探针）**：对 R1.5 判的 1 pending REQ（InvCSOpt-001）做 check_live 可行性实跑探针（规格 §2.1 桩体检 + §3.6 BLOCKED 判定）。经 eda_flow MCP 在 .75（hfhds201）实测：① FineSim V-2023.12-1（PATH 内，license OK，4s）跑候选 deck（ref 设计点 Wp=0.5/Wn=0.3/L=39/M=1）→ `ERROR! FMI library not provided for user model 'ptn_mra' level=109`，无 .mt0/.lis；② HSPICE V-2023.12-SP1-1 跑同 deck → `job aborted`，无 .lis；③ 资产核查：model lib `/apps/imctf/.../V2_HK_Model_D5_v0d5_Rev07_relia.sp`（15962B 可读）+ `mosra_so/libmosapi.so` + `agemodel/*.mdl` + `agemodel_entry.mdl` 齐全，`LD_LIBRARY_PATH` 加 mosra_so 仍 FMI 失败；④ 模型 `.appendmodel ntn_mra/ptn_mra mosra`（level=109 user model）依赖 FMI/agemodel 用户模型库，.75 沙盒未配置；⑤ trace_source 记原用户真实 FineSim 亦 rc=1 全失败。**结论**：check_live 物理验证（真跑验 delay<20/idd<100/duty∈[45,55]）在 .75 不可达 → 按规格 §3.6 降级 **InvCSOpt-001 REQ→LIVE-OPT（BLOCKED: 缺 FMI/agemodel user-model lib on .75）**。REQ 轨收口=3/3 全闭合（0 pending）。

### REQ 清单（须改造为 L2.live）

**已闭合（3）**：
- `IOBufTune-001` — hspice_mock→real PrimeSim HSPICE on .75（r1448）
- `SelFigReport-001` — stub→real pyAether aeGetCurDesign（r1446）
- `SkillToAether-001` — SKILL stub→real pyAether（r1442）

**新判 REQ（1，冻结窗口 TODO R2）**：
- ~~`InvCSOpt-001`~~ — R1.5 判 REQ（条件 (p) best_design.json 自报 delay/idd/duty 无独立复算/真跑，Q2 会判过）。**R2-prep（r1478）.75 实跑探针证 check_live 物理验证 BLOCKED**：FineSim V-2023.12-1 + HSPICE 在 .75 均无法加载 level-109 mosra aging user-model `ntn_mra`/`ptn_mra`（"FMI library not provided"），无 .mt0 产出；model lib + libmosapi.so + agemodel/*.mdl 齐全但 FMI/agemodel 用户模型层不可加载；trace_source 记原用户真实 FineSim 亦 rc=1 全失败。**按规格 §3.6 降级 REQ→LIVE-OPT（BLOCKED: 缺 FMI/agemodel user-model lib on .75）**。物理 delay/idd/duty 不可真验；可选 OPT：真 FineSim 跑标准 BSIM 模型验 parse_meas 于真实 .mt0（物理值不可验）。详见下 OPT 清单。

**R1.5 改判 REQ→NA（1）**：
- `IOBufParamTune-001` — R1 误判 REQ（理由「无独立复算」事实错误）。深读 check.py 条件 (f)(g) 经 `evaluate()`=Shichman-Hodges RC 模型**独立复算** dataH/dataL，(h)(i) 验目标；prompt 显式 level-1 模型 + deck level=1，真 HSPICE 会得同结果无增量；Q2 不会判过（独立复算 + 目标 check）。与 IOBufTune-001 **不同族**（后者 hspice_mock 假仿真输出 + GT 常量，本例纯 python 模型独立复算）。改判 **LIVE-NA**。

### OPT 清单（静态足够，真跑可加硬断言）

| case_id | 静态判分依据 | 真跑可加的硬断言 | Q2 风险 |
|:--|:--|:--|:--|
| AutoCellRmAvPf-001 | official mock_pyAether 记录 API 调用序，check 数据驱动校验 aeOpenDesign(B) + 调用序 | 真pyAether 验 geometry 实际删除 | 低（mock 镜像真 API surface，无假物理输出） |
| HierDescend-001 | official mock_oa_db 记录 open_view 序列，check 校验 B descend 序 + stops-at | 真OA 验 descend 返回真 cell | 低 |
| RsCalcFlow-001 | official mock_tools + 阻力模型(rf**iter)，check 独立 replay 验迭代数/调用序 | 真rscalc 验电阻实际降低 | 低（独立 replay） |
| RsCalcRnodePlace-001 | official pyAether_mock 记录调用，check 校验编排 | 真pyAether 验 RNODE 实际打齐 | 低 |
| PyaetherScreenshotVerifyQA-001 | official pyaether_mock 记录 emyInitAether/aeOpenDesign/aeCapture 序+ordering | 真pyAether 验真截图产物 | 低 |
| DlySigmaSweep-001 | hidden measure_B.py 模型独立复算每 B 采样点 sigma | 真MC sim 验真实 sigma | 低（独立复算无假阳） |
| LDOGen-001 | check 验 netlist 结构 + R1/R2 比值=vout/vref-1（核心设计方程） | 真spectre/hspice AC 验 PSRR/gain/PM | 低（设计方程校验） |
| DominoPVTsweep-001 | check 独立 recompute pass-counts from VMLH/VMHL | 真FineSim 验真实 Vm 产物 | **待 R2 确认 Vm 来源**（候选自报无独立校验则升 REQ） |
| InvCSOpt-001 | 条件 (p) best_design.json 自报 delay/idd/duty **无独立复算**（Q2 会判过）；(m)(n) parse_meas 仅验 parser 于 pre-baked mt0 | 真FineSim 验候选 deck 物理 delay/idd/duty 达标 | **BLOCKED**：.75 上 FineSim+HSPICE 均无法加载 level-109 mosra aging user-model ntn_mra/ptn_mra（FMI lib not provided）；model lib+libmosapi.so+agemodel 齐全但 FMI/agemodel 层不可加载；trace 原用户 FineSim 亦 rc=1。**降 REQ→OPT(BLOCKED)** per §3.6。物理值不可真验；可选 OPT=真 FineSim 跑标准 BSIM 验 parse_meas 于真实 .mt0（物理值仍不可验）|

> mock-pyAether 编排族（5 条）关键判据：mock **记录 API 调用**（非假物理输出），check 比对 B spec 数据驱动；与 hspice_mock（假仿真输出+GT 常量）本质不同。r1446 已核验 ref solution 无真实 pyAether 调用=关键字误命中，本轮 R1 复验确认 Q2 低风险。

### NA 清单（108 条，保持 [L0,L1]）

deliverable = 文本/脚本/日志分析/网表变换/诊断报告/问答。check 经 `subprocess`（sys.executable python 候选脚本）校验输出结构/文本；EDA 工具名（hspice/finesim/calibre/vcs/verdi）仅作 deck/option/log 断言 token 或 forbidden-import，**非真二进制调用**。典型子类：
- 网表分析/QA（RasNetlistAnalyze/MBistTopoExplainQA/NetlistHierarchyExtractQA/…）
- 网表变换脚本（NetlistDCE/NetlistCxiFilter/Schematic-001/…）
- SPICE deck / 激励生成（SpiceDeckGen/SpStimGen/FifoTbStimGen/…）
- 波形分析（解析已抽取 CSV/txt：TempSelWaveform/WaveView/GrDecPwrMeasure/ToggleTrTf/TskewCalc/…）
- 既有 sim log 解析（CTLEAcMetric/RonMismatchMd0/SiOutDiag/…）
- 配置/脚本修复（PwrIremCfgFix/VecgenIncSrcPatch/GenSPv2/…）

### 与旧 P4 的差异

| 项 | 旧 P4（r1447） | 本轮 R1 | 说明 |
|:--|:--|:--|:--|
| 口径 | lite-128 关键词扫 | lite-500 逐条静态重判 + Q1/Q2 桩体检 | 口径统一，关键词扫法已证伪 |
| IOBufParamTune-001 | mock（T3） | **NA**（R1.5 改判） | R1 误判 REQ「无独立复算」；R1.5 深读：条件 (f)(g) 经 `evaluate()` 独立复算，Q2 不会判过；prompt 显式 level-1 模型，真 HSPICE 无增量→改判 NA |
| InvCSOpt-001 | mock（T3） | **OPT（BLOCKED）** | 旧 P4 按关键字扫归 mock；R1.5 读 check 发现条件 (p) 自报值无独立校验=Q2 会判过→REQ；R2-prep .75 实跑探针证 FineSim+HSPICE 均无法加载 level-109 mosra user-model（FMI lib not provided），物理验证 BLOCKED→降 REQ→OPT(BLOCKED) per §3.6 |
| DominoPVTsweep-001 | mock（T3） | **OPT**（Vm 来源已确认） | 旧 P4 归 mock；R1.5 深读：Vm 来源=hidden B mt0 CSV 经 `_recompute()` 独立复算（非自报），条件 (o) 公式 guard；Q2 不会判过，不升 REQ |
| mock-pyAether 编排族 5 | 关键字误命中=mock | **OPT** | 旧 P4 已判 mock 正确；本轮 R1 复验 Q2 低风险，但真 pyAether 可加硬断言→标 OPT（非 REQ，因 mock 非假物理输出） |
| hspice_mock 族 | 仅 IOBufTune=REQ | 一致 | 本轮复验确认 D lite-121 内 hspice_mock 族仅 IOBufTune-001（已 L2.live），无遗漏 |

### 缺口台账 / 下一步

- 🔴 **冻结窗口**：zhulong r3' 进行中（ETA ~00:08 Nov-27），**R2 改造必须等 `run/MEMORY_ZHULONG.md` 首行 r3' 收口**。
- R1.5 深读复验完成：REQ 5→4（IOBufParamTune-001 改判 NA），NA 108→109，OPT 8 不变（DominoPVTsweep Vm 来源已确认不升 REQ）。
- **R2-prep 探针（r1478）**：对 1 pending REQ（InvCSOpt-001）做 .75 check_live 可行性实跑探针 → FineSim+HSPICE 均无法加载 level-109 mosra user-model（FMI lib not provided），物理验证 BLOCKED → **降 REQ→OPT(BLOCKED) per §3.6**。三分类：**REQ 4→3（全闭合，0 pending）· OPT 8→9 · NA 109**。
- **REQ 轨收口**：3/3 已 L2.live（IOBufTune/SelFigReport/SkillToAether），0 pending。D shard 无待改造 REQ。
- OPT 9 条：mock-pyAether 编排族 5（Q2 低风险，真 pyAether 可加 geometry 硬断言）+ 优化 sweep 族 3（DominoPVTsweep Vm 来源已确认=独立复算；DlySigmaSweep/LDOGen 静态独立复算/设计方程已足够）+ InvCSOpt-001（BLOCKED: 缺 FMI/agemodel user-model lib，物理值不可真验；可选 OPT=真 FineSim 跑标准 BSIM 验 parse_meas 于真实 .mt0）。
- NA 109 条不占轮次（R1/R1.5 写完理由即结束）。
- 📌 **InvCSOpt-001 判分弱点备案**：条件 (p) best_design.json 自报值无独立物理校验（Q2 会判过）这一 gap 在 .75 当前环境下**不可闭合**（专有 mosra aging 模型 FMI 库缺失）。非「题坏了」（deck-gen/parse 逻辑健全、ref PASS、neg 全 FAIL），但物理可行性断言不可加。已记 BLOCKED，**不退题**（规格 §1.4）；若日后 .75 配置 FMI/agemodel 环境或换标准 BSIM 模型可重启 REQ 改造。

### R2-prep 探针·OPT 可行性体检（r1479，冻结窗口只读）

> **目的**：REQ 轨已 3/3 闭合（0 pending），对 9 条 OPT 逐条做 `.75` 实跑/API 可行性探针，把模糊的「真跑能加」落成具体的 **FEASIBLE / FEASIBLE-WITH-EFFORT / BLOCKED** 三态，供解冻后 R2 改造排期。冻结窗口内**只读探针，未落盘改 check.py/cases**。

**A. 仿真类 OPT（2 条）—— model lib 替代可行性**

项目模型路径 `/proj/dscqa/V0/model/current/model.sp` 在 .75 上 **Permission denied**（不可用）。替代库 `/apps/imctf/models/cxmt10G3/v1.0/Model_v1d0_pinus.sp` 经核查定义 `.subckt ntn/ptn/ntn_m/ntn_lv/ptn_lv`，9 corners（tt/ft/st/tf/ts/ff/ss/fs/sf）。

| case | 模型卡 | 探针结果 | check_live 可行性 |
|:--|:--|:--|:--|
| **LDOGen-001** | bare `ntn`/`ptn`/`ntn_m` | 裸 ntn/ptn smoke test **PASS**（hspice V-2023.12-SP1-1 `job concluded`, tt corner, w=2u/l=180n） | **FEASIBLE**：供 `.lib pinus tt` + 建 AC testbench 测 PSRR/gain/PM 即可。维持 OPT（静态验设计方程 R1/R2=vout/vref-1 防 Q2）。 |
| **DlySigmaSweep-001** | `ntn_lv`/`ptn_lv` | incFile_pinus 定义 `.subckt ntn_lv`(L3228)/`.subckt ptn_lv`(L6317)，但 tt corner 加载报 `ptn_lv not found or w/l out of range`（w/l 经 scale=0.728u/65.52n）；v0.8p1/incFile_pinus_lp 有 ntn_lv/ptn_lv **带默认 w=5u/l=0.22u** | **FEASIBLE-WITH-EFFORT**：需选 v0.8p1 或调 corner + 建 MC deck（netlist_B 无 `.var`/`.monte`，需补 montecarlo setup）。维持 OPT（静态 measure_B.py 独立复算防 Q2）。 |

**B. mock-pyAether 编排类 OPT（5 条）—— pyAether API 可用性体检**

经 `get_api_details` 体检 + A r1292 实证：`aeOpenDesign`/`aeGetCurDesign`/`aeCapture`/`emyInitAether` **存在**；`dbCreateLabel`/`dbGetInstByName`/`dbGetPinShapes`/`dbDeleteInst`/`dbDeleteFig`/`dbGetInsts`/`hierDescend`/`dbOpenCellViewByType` **NOT in pyAether KB**（A r1292 实证 .75 pyAether 沙盒无 db* geometry API）。

| case | 想加的硬断言 | 探针结果 | check_live 可行性 |
|:--|:--|:--|:--|
| AutoCellRmAvPf-001 | geometry 实际删除 | dbDeleteInst/dbGetInsts 缺 | **BLOCKED**(缺 pyAether db* geometry API) |
| HierDescend-001 | 实际 descend 返回 | hierDescend/dbOpenCellViewByType 缺 | **BLOCKED**(缺 pyAether hierDescend/db* API) |
| RsCalcRnodePlace-001 | RN place geometry | db* geometry API 缺 | **BLOCKED**(缺 pyAether db* geometry API) |
| PyaetherScreenshotVerifyQA-001 | 截图存在性 | aeCapture 存在（可存 PNG） | **PARTIAL**(aeCapture 可行但调用序/校验本质已由 mock 覆盖，真跑增量低) |
| RsCalcFlow-001 | 电阻降低真验 | rscalc/autovia/powerfill 为 CXMT 内部工具，非标准 EDA 二进制 | **待 probe**(rscalc binary availability on .75，本轮未探) |

> 以上 5 条均 **维持 OPT**（Q2 低风险：mock 记录调用序非假物理输出，静态判分足够）。其中 3 条 BLOCKED（缺 pyAether db* API）、1 条 PARTIAL（增量低）、1 条待 probe。**结论：mock-pyAether 编排族在 .75 当前 pyAether 沙盒下无 geometry 层 check_live 升级路径**。

**C. 已收口 OPT（2 条）—— 无需新探针**

| case | 状态 | 依据 |
|:--|:--|:--|
| DominoPVTsweep-001 | OPT（R1.5 收口） | Vm 来源=hidden B mt0 CSV 经 `_recompute()` 独立复算（非自报），Q2 不会判过，不升 REQ |
| InvCSOpt-001 | OPT(BLOCKED)（r1478 收口） | .75 上 FineSim+HSPICE 均无法加载 level-109 mosra aging user-model（FMI lib not provided），物理验证 BLOCKED |

**D. R2-prep 探针小结（r1479）**

- 9 条 OPT 全部有结论：**FEASIBLE 1**（LDOGen）+ **FEASIBLE-WITH-EFFORT 1**（DlySigmaSweep）+ **BLOCKED 4**（AutoCellRmAvPf/HierDescend/RsCalcRnodePlace/InvCSOpt）+ **PARTIAL 1**（PyaetherScreenshotVerifyQA）+ **待 probe 1**（RsCalcFlow）+ **R1.5 收口 1**（DominoPVTsweep）。
- **解冻后 R2 排期建议**：仅 **LDOGen-001** 与 **DlySigmaSweep-001** 值得做 OPT→L2.live 升级（仿真类，model lib 替代可行）；mock-pyAether 族因 .75 pyAether 沙盒缺 db* geometry API 无升级路径，维持 OPT 不排期；InvCSOpt 维持 BLOCKED。
- 三分类**不变**：REQ=3（全闭合）· OPT=9 · NA=109。本轮仅丰富 OPT 的「缺什么」证据，无 verdict 变更、无落盘改判分（冻结窗口）。
