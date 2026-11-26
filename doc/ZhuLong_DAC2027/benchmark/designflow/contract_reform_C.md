# Shard C 判分契约改造进度（contract_reform_C.md）

> **Owner**：shard C（physical_layout: layout_aether / layout_virtuoso / pg_layout / physical_verify）
> **启动**：2026-11-26（运维令「判分契约改造 check_static/check_live 拆分」+「P4 实跑适合性分析」）
> **指南**：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/CONTRACT_REFORM_GUIDE.md`

## 总览

| 优先级 | 状态 | 数量 | 说明 |
|:--|:--|:--|:--|
| P1 — pilot 12 case | ✅ DONE | 5/5 pilot + 2 cleanup = 7/7 | r1204 修 5 pilot + r1207 修 PowerFillMergeGen/RsCalcChkPtGen |
| P2 — 真-EDA L2.live 扩展 | 🔄 进行中 | 7 L2.live done（Lite 内 0 余 / Lite 外 1 C-owned 候选待转） | 见 §P2 |
| P3 — mock case 声明 judge_layers | ✅ DONE | 620/620 | r1208 收口；C 全量 629/629 = 618 [L0,L1] + 11 [L0,L1,L2.live] |
| P4 — Lite 实跑适合性分析 | ✅ DONE (r1210) | 137/137 | 见 §P4，Lite-137 内 T1 已全部闭合 |

**CONTRACT 心跳**：`P1=7/7 done · P2=8 L2.live (Lite 内 6 T1 全闭合, Lite 外 6 C-owned TRUE 候选已转 3: WheelZoom r1212 + RnodeScatterScript r1213 + AetherHiliteCmd r1214; C-owned TRUE 候选已清零) · P3=620/620 judge_layers · P4=137/137 (T1=6 done / T2=16 / T3=115)`

---

## P1 — pilot 12 case（C 份额 5/5 DONE + 2 cleanup）

pilot 12 清单中 5 条归 shard C（物理在 `cases/C/`，domain 属 layout_aether/layout_virtuoso）：

| case_id | domain | judge_layers | ref check.py | test 字段同步 | L2.live 自验 |
|:--|:--|:--|:--|:--|:--|
| FindCircuitByPath-001 | layout_aether | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | ✅ | PASS |
| HierJump-001 | layout_aether | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | ✅ | PASS |
| HierSearchDFS-001 | layout_aether | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | ✅ | PASS |
| PortPropagate-001 | layout_aether | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | ✅ | PASS |
| PyLibApiDocGen-001 | layout_aether | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | ✅ | PASS |

r1207 cleanup（指南表标 shard=A 系误标，物理在 `cases/C/` domain=layout_virtuoso ⇒ 归 C）：

| case_id | domain | 改动 | 状态 |
|:--|:--|:--|:--|
| PowerFillMergeGen-001 | layout_virtuoso | 补 judge_layers=[L0,L1,L2.live] + check_live 已有 | ✅ DONE |
| RsCalcChkPtGen-001 | layout_virtuoso | 补 judge_layers=[L0,L1,L2.live] + check_live 已有 | ✅ DONE |

改造手法：非侵入包装（原 `check` → `_check_static_impl` 一字不动 + `check_static` try/except 收口三元组 + `check_live` + `check` 兼容包装）。check_live 采用 strategy-1（AST 收 candidate `<alias>.<api>` calls ∪ MANDATED_LIVE_APIS → .75 pyAether hasattr+callable 探针）。

---

## P2 — 真-EDA L2.live 扩展（进行中）

### 候选扫描（r1208/r1209）

`designflow/p2_candidates_C.tsv`：扫「no-live pyAether-mention check.py」共 28 条（全量 C，非仅 Lite），按 ref solve 的 `ae.*` attrs 是否在真 pyAether (.75) 存在分类：

| 分类 | 数量 | 含义 |
|:--|:--|:--|
| TRUE | 19 | ref solve 仅用真 pyAether 顶层 attrs → strategy-1 check_live 可行 |
| FALSE | 7 | ref solve 用 mock-only attrs（11 个：aeAttachTech/aeAutoPlacementFromDesign/aeConnect/aeExportNetlist/aeGetInstByName/dbCellViewExist/dbCreatePin/dbCrtLib/pycClose/pycErrorDialog/getCellView）→ strategy-1 会让 ref FAIL，需 strategy-2/3 或重写 |
| PURE | 2 | ref solve 无 ae.* 调用（pure-python candidate）→ 非 T1，归 P3 |

**关键发现（P4 复核）**：28 条 p2 候选里**只有 1 条（AdjViaSelect-001）在 Lite-137 内**，其余 27 条都在 Lite-137 之外。Lite-137 内的真-EDA case 已在 P1/r1204-r1209 全部转 L2.live（6 条）。所以 **P2 后续推进的是 Lite-外** 的 19 TRUE 候选，不影响 Lite-500 全绿状态。

### 已转换（6 条）

| case_id | domain | 轮次 | judge_layers | 自验 |
|:--|:--|:--|:--|:--|
| TrMatchHelperGen-001 | layout_aether | r1205 | [L0,L1,L2.live] ✅ | check_static+check_live PASS, 5 neg FAIL |
| RedundantPinRemoval-* | layout_aether | r1206 | [L0,L1,L2.live] ✅ | PASS |
| AdjViaSelect-001 | layout_aether | r1208 | [L0,L1,L2.live] ✅ | PASS（Lite 内） |
| ListInstCV-001 | layout_aether | r1209 | [L0,L1,L2.live] ✅ | PASS |
| SchematicPinAdd-001 | layout_aether | r1211 | [L0,L1,L2.live] ✅ | PASS（ref check_static+check_live .75 实跑 PASS；teeth-verified：candidate 调 nonexistent api `dbCreateSchPinExFake` 被 check_live FAIL；negative_selftest 5 neg ALL-FAIL；附修 ListInstCV negative_selftest leak r1209 遗留） |
| WheelZoom-001 | layout_aether | r1212 | [L0,L1,L2.live] ✅ | PASS（ref check_static 15 conds PASS + check_live .75 实跑 PASS；7 mandated APIs aeSetBindKey/aeGetBindKey/aeZoomInAtMouse/aeZoomOutAtMouse/aeZoomWindowAtMouse/guScroll/aeGetwtWndId 全 callable 已预探；teeth-verified：candidate 调 nonexistent `aeSetBindKeyFake` 被 check_live FAIL missing=[aeSetBindKeyFake]；negative_selftest 6 neg ALL-FAIL distinct d/f/g/m/i/h，§4.9 trio {empty→d,print→f,core→g}=3-distinct；附修 negative_selftest leak：check compat 返回 bool 不 raise → 改调 _check_static_impl） |
| RnodeScatterScript-001 | layout_aether | r1213 | [L0,L1,L2.live] ✅ | PASS（ref check_static 14 conds PASS + check_live .75 实跑 PASS；20 mandated APIs aeGetCurDesign/dmGetObj/dbCVExist/dbNewCellView/dbGetTrueOverlapsEx/dbCrtLabel/dbCrtRect3X/dbCrtInst/dbSaveCV/dbCloseCV/emyPointF/emyInitAether/aeMessage/aeCreateAppForm/aeCreateStringField/aeCreateFormButton/aeDisplayForm/aeSetCallbackStatus/aeToggleCallBack/aeBaseAppFormCallBack 全 callable 已预探；teeth-verified：candidate 调 nonexistent `dbCrtLabelFake` 被 check_live FAIL missing=[dbCrtLabelFake]；negative_selftest 4 neg ALL-FAIL distinct cond1/cond3/cond14/cond5，§4.9 trio {empty→cond1,print→cond3,core→cond5}=3-distinct；附修 negative_selftest leak：原 check __main__ 无条件 print PASS → 改 check_static 三元组 + sys.exit(1) on FAIL；附修 assets dir 命名不一致：stale short-name `RnodeScatterScript-001` 清理对齐 HEAD full-prefix `EDA-Eval-DesignFlow-RnodeScatterScript-001` + case JSON attachments 路径同步；check_live 收 candidate `ae.<attr>` Call ∪ Attribute(类子类化 ae.aeToggleCallBack) ∪ MANDATED_LIVE_APIS → .75 hasattr+callable 探针） |
| AetherHiliteCmd-001 | layout_aether | r1214 | [L0,L1,L2.live] ✅ | PASS（ref check_static 11 conds PASS + check_live .75 实跑 PASS；14 mandated APIs aeGetCurDesign/aeGetInstHier/aeClearHighLight/aeAddHighLightObj/aeSelectObject/aeMakeProbeWithColor/sleGuiDescendEdit/leGuiReturnOneLevel/sleGuiReturnToTop/aeSetCmdPort/aeRunCmdWithSocket/aeCloseCmdProcessByPort/emyString/SleAeSocketRequestCallback 全 callable 已预探；teeth-verified：candidate 调 nonexistent `aeAddHighLightObjFake` 被 check_live FAIL missing=["aeAddHighLightObjFake"]；negative_selftest 3 neg ALL-FAIL distinct first-fail labels {(a)aether_client.py not found / (c)missing clear/add calls=[] / (c)single-name missing aeSelectObject}，§4.9 trio {empty→(a),print→(c)missing-clear-add,core→(c)missing-select}=3-distinct by first-fail label；附修 negative_selftest leak：legacy check compat 返回 bool 不 raise → 改调 _check_static_impl；双文件交付(server_start.py+aether_client.py)，check_live AST 扫两文件 pyAether import alias(<alias>.<attr> Call ∪ Attribute 涵盖 class 子类化 RequestCB(pyScript.SleAeSocketRequestCallback))∪MANDATED_LIVE_APIS → .75 hasattr+callable 探针） |

注：ListInstCV-001 / RedundantPinRemoval / SchematicPinAdd / WheelZoom 不在 Lite-137（Lite 外的 P2 推进）。

### 待转换（Lite 外，按 r1211 复核排序）

**候选复核修正（r1211）**：原 p2_candidates_C.tsv 的 28 条「no-live pyAether-mention」扫描是按 reference/check.py 文件做的，未校核 case JSON 归属。逐条 cross-ref `cases/` 后发现：
- **3 条 D-owned 误入 C 池**：SelFigReport-001 / CstViewPrecheck-001 / DecqaRwaBusCount-001 物理在 `cases/D/`（domain=analog_context / schematic_netlist），归 shard D，C 不碰。
- **6 条 orphan reference**（有 reference/check.py 但无 case JSON）：AeDelCellCurCellProduce / AetherStandaloneInstList / NicapBlockCreatePlanner / SchPinAddProduce / TopCellNameProduce / ViaOptimGds —— 无 case JSON 即不在评测集，转了也无意义，skip。
- **AutoCellRmAvPf / AnalogCmpSchemBuild / PyaetherScreenshotVerifyQA** 在 `cases/D/`（D-owned），DecoderSchemGen 在 `cases/A/`（A-owned）。

剩余 **C-owned 且有 case JSON 的 TRUE 候选**（0 条 — C-owned TRUE 已清零）：

| case_id | domain | judge_layers | ref_ae_attrs | 备注 |
|:--|:--|:--|:--|:--|
| _(无)_ | | | | C-owned TRUE 候选已全部转 L2.live |

（WheelZoom-001 已于 r1212 转换；RnodeScatterScript-001 已于 r1213 转换；AetherHiliteCmd-001 已于 r1214 转换，见上「已转换」表。C-owned TRUE 候选清零，P2 主线收口。）

FALSE 候选（7 条，mock-only attrs）改造工作量 L（需 strategy-2 强一致或重写 ref），暂缓。

---

## P3 — mock case 声明 judge_layers（620/620 DONE）

- r1208-r1209: 全量 C mock case 声明 `judge_layers=["L0","L1"]`
- C 全量 coverage：629/629
  - `judge_layers=["L0","L1","L2.live"]`：15 条（P1 pilot 5 + cleanup 2 + P2 已转 8）
  - `judge_layers=["L0","L1"]`：614 条（mock，框架回退旧式 check()）
  - 无 judge_layers：0 条

**行为保持**：框架对 `[L0,L1]` + 旧式 `check()` 走 fallback，L2.live 不触发 ⇒ 与改造前完全一致。已抽样跑 reference solution `check()` 均 PASS。

---

## P4 实跑适合性分析 (r1210 · 2026-11-26)

**方法**：对 Lite-137（`eval/cases_lite.txt` 中 shard C 的 137 条）逐个读 case JSON 的 `prompt` + `test`（check.py 源），用「核心一问」判档：「如果 candidate 的输出能让 check.py 的文本断言全过，但 EDA 工具实际跑不起来/结果全错，这个 pass 算不算数？」

**分类规则**：
- **T1 适合实跑**：check.py 用 fake pyAether stub 跑 candidate（candidate 调 `ae.*` API 拿 canned 返回值再产出）→ candidate 可对 stub「瞎写」即过，但真 EDA 跑不起来 ⇒ 必须改 L2.live。
- **T2 可选增强**：case 本质是「写 SKILL/脚本」类文本判分（check.py 断言脚本结构/AST/输出文本），可加「脚本能否 load 进 Virtuoso 不报错」的 L2.live 辅助断言；改不改看工作量收益比。
- **T3 不适合**：纯文本/JSON/AST 分析（parse rule deck、count DRC 结果、比对 config），candidate 必须实际算对才能过，无「真 EDA 执行结果」可验 ⇒ 保持 mock。

**辅助证据**：
- 全量 Lite-137 与 `p2_candidates_C.tsv`（28 条 pyAether-mention 候选）交叉比对：仅 1 条（AdjViaSelect-001，已转）落入 Lite-137。
- 对 T3 抽样（CalibreLvsRepDiag-001 / ConnChkSummaryGen-001 等）确认 check.py 只 parse 文本/rule deck，不 subprocess 调真 calibre 二进制。
- 2 条初判 T1_maybe（AutoViaSelAnalyze-001 / CombCellNetlistSyn-001）复核：`import pyAether` 出现在 candidate 的 **banned list** 里（明确禁止 candidate 调 EDA，要求纯 python）⇒ 降为 T3。

### 统计

本 shard Lite-500 case 数: **137**

| 档位 | 数量 | 说明 |
|------|------|------|
| T1 适合实跑 | 6 | **全部已转 L2.live**（见清单），Lite-137 内无剩余 T1 |
| T2 可选增强 | 16 | agent 自决，见清单 |
| T3 不适合 | 115 | 保持 mock，不逐条列出（按域分布：physical_verify 65 / layout_aether 25 / pg_layout 14 / layout_virtuoso 11） |

### T1 清单（优先改造顺序）

| case_id | domain | 当前判分方式 | 实跑要调什么 | assets 齐备? | .75 可复跑? | 改造工作量(S/M/L) |
|---------|--------|-------------|-------------|-------------|------------|------------------|
| AdjViaSelect-001 | layout_aether | 已 L2.live (r1208) | pyAether strategy-1 (AST 收 ae.* 探针) | Y | Y | S (done) |
| FindCircuitByPath-001 | layout_aether | 已 L2.live (r1204 pilot) | pyAether | Y | Y | S (done) |
| PortPropagate-001 | layout_aether | 已 L2.live (r1204 pilot) | pyAether | Y | Y | S (done) |
| PowerFillMergeGen-001 | layout_virtuoso | 已 L2.live (r1207 cleanup) | pyAether | Y | Y | S (done) |
| RsCalcChkPtGen-001 | layout_virtuoso | 已 L2.live (r1207 cleanup) | pyAether | Y | Y | S (done) |
| TrMatchHelperGen-001 | layout_aether | 已 L2.live (r1205) | pyAether | Y | Y | S (done) |

**结论**：Lite-137 内 T1 已 6/6 闭合，无剩余 T1 需改造。P2 后续推进的是 Lite-**外**的 19 TRUE 候选（不影响 Lite-500 全绿）。

### T2 清单

| case_id | domain | 可加什么 L2.live 辅助断言 | 工作量 |
|---------|--------|--------------------------|--------|
| CmMaOpTableGen-001 | layout_aether | 复刻 `CXMTseGetAllLatchInfo` 逻辑生成 CSV；可加「CSV schema 与真 API 返回字段一致」探针 | M |
| ConvexEnclosePcellGen-001 | layout_virtuoso | SKILL pcell→Python 转写；可加「原 .il 能 load 进 Virtuoso 不报错」 | M |
| DRQAPlan2Skill-001 | layout_virtuoso | DRC QA 流水线 SKILL 封装；可加「skill 文件 load 进 Virtuoso」 | M |
| HeadlessLatchSkillGen-001 | layout_virtuoso | 流程包装成 skill；可加「生成的 skill 命令可被 skill loader 解析」 | S |
| MaxAreaRatioSidewallSolver-001 | physical_verify | ANT 天线比例规则函数（SKILL→Python 转写）；可加「规则函数对边界输入返回正确数值」 | M |
| NetlistExtractSkill-001 | layout_virtuoso | schematic 导出 SPICE netlist skill；可加「skill load + netlist 结构断言」 | M |
| RTextChkPlan-001 | pg_layout | RsCalc 检查点规划；可加「生成的 checkPoints 与真 RsCalc config schema 一致」 | M |
| ResFlow-001 | layout_virtuoso | RsCalc IR-drop 迭代 SKILL runner；可加「runner .il load 进 Virtuoso」 | M |
| RsCalcCfgSync-001 | pg_layout | rsclac.config 同步；文本判分够用，L2.live 收益低 | L (不建议) |
| RsCalcMesh-001 | layout_virtuoso | 流程梳理（分析为主）；本质是文档输出，L2.live 不适用 | — (归 T3 更合适) |
| SchNetPrefixHilightGen-001 | layout_virtuoso | SKILL 高亮 net；可加「skill load 进 Virtuoso + 高亮 API 存在」 | S |
| SkillFlowAnalyzer-001 | layout_virtuoso | 分析 IMCutRscalcFlow.il 脚本；本质是分析报告，L2.live 不适用 | — (归 T3 更合适) |
| SkillM1ShapeDeleteAudit-001 | layout_virtuoso | SKILL 按层删除图形 + pitfall 审计；可加「.il load + 删除仿真」 | M |
| SkillMenuRoute-001 | layout_virtuoso | SKILL pull-down menu trigger 注册；可加「trigger 文件 load」 | S |
| AutoViaGen-001 | layout_virtuoso | AutoVia 后端（沙盒注 L1 占位）；本质占位题 | — (占位) |
| VirtuosoLaunchRecipeGen-001 | layout_virtuoso | Virtuoso 启动 recipe（env/config 文本）；本质文档，L2.live 不适用 | — (归 T3 更合适) |

**T2 处置建议**：大多数 T2 是 SKILL 脚本生成/分析类，文本判分是主意图，加「.il load 进 Virtuoso 不报错」的 L2.live 辅助断言收益有限（load 成功 ≠ 逻辑对）。agent 自决：**暂不转**，保持 mock；若后续 P2 主线（Lite-外 19 TRUE）闭合后有余力，再挑 2-3 条 SKILL 类做 L2.live 辅助增强试点。其中 RsCalcMesh / SkillFlowAnalyzer / VirtuosoLaunchRecipeGen / AutoViaGen 本质是分析/占位/文档，建议归 T3，不增强。

---

## Live-eval 审视（2026-11-26 用户令 · `BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`）

> **R1 只读审视 · r1228 · 冻结窗口内（zhulong r3' 41% 进行中）**。逐条重判 lite-137 全量，按 §2.1 三条硬规则（mock 桩体检 Q1/Q2 + 工具名出现≠真跑 + 旧 P4 不作数）。
> **方法**：脚本扫 137 条 check.py → 检 spice_mock / fake_tool / real-EDA-binary subprocess / check_live → 人工深读桩体检可疑项 + 16 T2 全量 + 抽样 T3。

### 三分类合计

| verdict | 数量 | 说明 |
|:--|--:|:--|
| **LIVE-REQ (done)** | 6 | 已 L2.live（T1=6 闭合，r1204-r1214 完成） |
| **LIVE-OPT** | 6 | faithful stdlib mock 替代真二进制；Q1=yes Q2=not-fooled；.75 真跑可加 mock-fidelity 辅助断言 |
| **LIVE-NA** | 125 | deliverable 本身=脚本/文本/CSV/config；静态判分为主意图且充分；无自写假工具 |
| **合计** | 137 | lite-137 全量 |

### REQ 清单（6 · 已闭合，无需再改）

`AdjViaSelect-001` / `FindCircuitByPath-001` / `PortPropagate-001` / `PowerFillMergeGen-001` / `RsCalcChkPtGen-001` / `TrMatchHelperGen-001` —— judge_layers=`[L0,L1,L2.live]`，check_live + check_static 拆分已完成，ref L2.live PASS on .75（pyAether ae* hasattr+callable 探针）。

### OPT 清单（6 · 本轮新发现 · 旧 P4 误归 T3）

| case_id | mock | 桩体检 Q1/Q2 | 缺什么 |
|:--|:--|:--|:--|
| DummyDeck-001 | calibredrv_mock.py | Q1=faithful：解析真实 GDSII LAYER/DATATYPE record；Q2=not-fooled：候选拿到真实 layer 数据无法伪造 | real calibredrv GUI 二进制（.75 可能无 GUI 工具） |
| PowerFill-001 | calibredrv_mock.py | Q1=faithful：解析真实 GDSII（topcell/bbox/layers/cells/celltext/units）；Q2=not-fooled | real calibredrv（同上） |
| DummyMeas-001 | skipper_mock.py | Q1=faithful：解析真实 GDSII + tclsh8.6 db* procs；Q2=not-fooled：AUDIT vs guideline_B GT + 独立 parse | real skipper GUI 二进制 |
| GDSBump2-001 | skipper_mock.py | Q1=faithful：解析真实 GDSII db* API；Q2=not-fooled：reimport GDS vs 真实 layer set GT | real skipper（同上） |
| PGLayout-001 | skipper_mock.py | Q1=faithful：解析真实 GDSII db* API；Q2=not-fooled：produced GDS vs 真实 geometry GT | real skipper（同上） |
| DummyQA-001 | rules_syntax_checker_mock.py | Q1=faithful：逐条解析真实 SVRF deck vs 真 SVRF 关键词白名单（非 hardcode-B）；Q2=not-fooled：check 独立重跑 mock 验候选 verdict（cond h） | real Calibre rules_syntax_checker |

> **OPT 处置**：6 条 mock 均为「真实输入文件的 stdlib 解析器」（读真实 GDSII 二进制 / 真 SVRF 文本），非编造数据桩。判分已足够（候选无法伪造几何/语法数据）。.75 真跑 real binary 仅能 cross-validate mock 保真度，不能多抓候选 ⇒ OPT 非 REQ。若 .75 无 calibredrv/skipper GUI 二进制 ⇒ 记 `BLOCKED: 缺 GUI 工具`，保持 mock（铁律 2 infra，不写成能力结论）。

### NA 清单（125 · 16 T2 + 109 T3）

- **16 T2（旧 P4 待审）**：全部 NA。deliverable=SKILL/.il 生成器或分析器脚本，check.py 跑候选 Python + 断言生成文本/AST/结构（无自写假工具）。Q2：text-check 可被「形状对但 runtime 逻辑错」的 SKILL 骗过，**但** L2.live load-check 同样无法验证逻辑（load 成功 ≠ 逻辑对，旧 P4 论点仍成立）⇒ deliverable 本身是脚本 = NA。含 CmMaOpTableGen / ConvexEnclosePcellGen / DRQAPlan2Skill / HeadlessLatchSkillGen / MaxAreaRatioSidewallSolver / NetlistExtractSkill / RTextChkPlan / ResFlow / RsCalcCfgSync / RsCalcMesh / SchNetPrefixHilightGen / SkillFlowAnalyzer / SkillM1ShapeDeleteAudit / SkillMenuRoute / AutoViaGen / VirtuosoLaunchRecipeGen。
- **109 T3**：NA。deliverable=Python 脚本/文本/JSON/config/CSV；check.py 跑候选 + 断言输出结构/数值（hidden-B 重参 + anti-hardcode）；无 spice_mock / 无 real-EDA-binary subprocess（脚本扫 137 条 0 命中）。

### 与旧 P4 的差异

1. **口径统一**：旧 P4 按 585/609 全量 + 关键词扫，本轮按 lite-137 全量 + 桩体检复验。
2. **T2=16 全降 NA**：旧 P4 标「待审/可选增强」，本轮按 §2.1 Q2 判定 deliverable=脚本 ⇒ NA（L2.live load-check 不验证逻辑）。
3. **T3 挖出 6 OPT**（旧 P4 漏报）：DummyDeck/PowerFill/DummyMeas/GDSBump2/PGLayout/DummyQA 用 faithful mock 替代真二进制 —— 旧 P4 关键词扫未识别「自写假工具」类（§2.1 规则 1 本轮重点）。本轮判定 mock 读真实输入 ⇒ Q1 faithful Q2 not-fooled ⇒ OPT（非 REQ），但需 .75 真工具 cross-validate 保真度才算收口。
4. **0 REQ 待改造**：lite-137 内无新增 REQ（6 REQ 已闭合；6 OPT 为增强非必须；125 NA 保持 mock）。

### 下一步（R2，待冻结窗口解除）

- 冻结窗口内（zhulong r3' 未收口）🚫 改 check.py / cases/*.json。
- 解冻后：6 OPT 逐条探 .75 可达性（calibredrv / skipper / rules_syntax_checker），可达则加 check_live mock-fidelity 断言（≤3 条/轮）；不可达记 `BLOCKED: 缺 <工具>`。
- 125 NA 无需改造（R1 写完理由即结束，不占轮次）。

---

## 纪律

- 🚫 未改 check.py / 断言逻辑 / prompt / assets / hidden（P4 只读分析）
- 🚫 未碰别 shard 文件
- 🚫 未碰 jsonl
- ✅ P1 > P4(只读) ≈ P2 > P3 优先级遵循
- ✅ P4 结论：Lite-137 内 T1 已全闭合；P2 继续推 Lite-外候选，与 Lite-500 全绿不冲突

### R2-prep · .75 真工具可达性探针（r1229，冻结窗口内只读）

**用户令**：BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER §4「.75 实跑纪律」+ §1.1 冻结窗口允许只读探针（open_session/run_commands 不触 check.py / cases/*.json）。

**方法**：eda_flow MCP `open_session`（workdir `.../shardC_C-r1229-readprobe_live-opt-probe_0`）→ `run_commands` 探 .75（hfhds201）真工具 PATH + 版本 + 功能冒烟。

**结果（6 OPT 背后的 4 个真二进制全部 PRESENT + FUNCTIONAL）**：

| 真工具 | .75 路径 | 版本 | 功能确认 |
|:--|:--|:--|:--|
| `calibre` | /apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/calibre | v2020.1_36.18 | `calibre -version` OK |
| `calibredrv` | 同上/bin/calibredrv | Calibre DESIGNrev v2020.1_36.18 | ✅ `calibredrv -a layout peek tiny.gds -layers` → `{5 0} {6 2}` == mock LAYER/DATATYPE 解析（**cross-validated 语义保真**） |
| `rules_syntax_checker` | 同上/bin/rules_syntax_checker | v2020.1_36.18 | `rules_syntax_checker -help` OK（valid SVRF RC=0） |
| `skipper` | /apps/empyrean/tools/skipper/bin/skipper | (Empyrean) | 二进制 present（GUI，run_code host=skipper 通路可用，未做 full GUI 冒烟） |

**关键发现**：r1228 tsv 中 6 OPT 的 live_evidence 原写「GUI binary may be absent / Calibre may be absent」—— **被推翻**。.75（hfhds201）实际装有 Mentor Calibre 2020.1_36（**正是 mock 校准所对版本**，见 PowerFill tsv r1228「mock calibrated vs real calibredrv 2020.1_36」）+ Empyrean Skipper。

**cross-validation 证据（calibredrv 家族，2 OPT）**：构造最小 GDSII（layer 5/dt0 + layer 6/dt2 的两个 boundary），真 `calibredrv -layers` 输出 `{5 0} {6 2}`，与 calibredrv_mock.py 解析同 GDS 的 LAYER(0x0D)+DATATYPE(0x0E) record 结果逐字一致 ⇒ **mock 语义保真经真工具交叉验证**（Q1=yes 硬证据，不再是「自述 faithful」）。

**R2-readiness 结论**：6 OPT 全部 R2-READY——解冻后可直接为每条加 `check_live(sess)`：在 .75 跑真工具（calibredrv/skipper/rules_syntax_checker）交叉验证 mock 输出一致性（≤3 条/轮，§4 预算）。无 BLOCKED。

**冻结纪律**：本轮 0 改动 reference/*/check.py、0 改动 cases/*.json、0 改 EDA-Flow-Bench 仓库；仅更新 designflow/live_eval_review_C.tsv（evidence 列，§1.1 明确允许）+ 本文件 + MEMORY。

### R2 设计草案（r1230 · 冻结窗口只读 prep · 解冻后 ≤2 轮可执行）

**背景**：r1229 R2-prep 已证 4 真二进制 PRESENT+FUNCTIONAL on .75。本节把「6 OPT 全 R2-ready」落到**逐条可执行设计**：每条给出 check_live 的 (a) .75 真工具命令 (b) 交叉验证对象 (c) 断言 (d) live-neg (e) 风险/降级。解冻后照此执行，无需再设计。

**判分契约约束（§3）**：原 `check` → `_check_static_impl` 一字不动；`check_static` 包 try/except 收口三元组；`check_live(sess)` 经 eda_flow 在 .75 真跑；`judge_layers` 追加 `L2.live`；JSON `test` 字段与 check.py sha 同步；≥1 live-neg（静态全过、实跑产物错）。

---

#### R2.1 批次（解冻首轮 · 3 条 · calibredrv + rules_checker 家族 · 低风险）

**1. DummyDeck-001**（calibredrv_mock · `CALIBREDRV_BIN` env 可换真二进制）
- .75 命令：`calibredrv -a layout peek <gds_B> -layers` + 同 gds_A；版本 v2020.1_36.18（= mock 校准版本）。
- 交叉验证：mock `calibredrv_mock.py <gds_B> -layers` 的 LAYER/DATATYPE 集合 == 真工具输出。r1229 已在 tiny.gds 证逐字一致，本条扩到 case 真实 hidden-B/A。
- check_live 断言（≥2 独立可 FAIL）：① 真 calibredrv 在 gds_B 上 layer 集合 == mock 解析（逐 layer/datatype 对）② 同断言在 gds_A 上成立 ③ 真 calibredrv 退出码 0（GDS 合法）。
- live-neg：喂一个 LAYER record 故意错位（layer 号改坏）的 GDS → 真工具与 mock 必须都报不同 layer 集；候选若伪造 layer 数据 → 静态过但 check_live 抓到真工具 layer 集不符。
- 风险：低。env-swap 机制已就绪，r1229 cross-val 已通。

**2. PowerFill-001**（calibredrv_mock · 同 env-swap · 13 静态断言含 cross-input guard cond m）
- .75 命令：`calibredrv -a layout peek <gds_B> -topcell -cellcount -bbox -units -precision -format -layers` + 同 gds_A。
- 交叉验证：真工具 topcell/cellcount/bbox/units/precision/format/layers == mock 解析 == check.py 内 GT_B/GT_A（三者一致 ⇒ mock 保真 ⇒ 静态 GT 硬证据）。
- check_live 断言：① 真 calibredrv gds_B topcell==testa_opt1 / cellcount==31 / bbox==GT_B ② 同 gds_A topcell==testa_via1 / cellcount==29 ③ filesize(真工具报)==GT_B 243712。
- live-neg：候选 pf_audit.py 喂 GT_B 硬编码值但真工具跑 gds_B 报不同 cellcount → check_live FAIL（静态 cond d/e 过、live 抓）。
- 风险：低。

**3. DummyQA-001**（rules_syntax_checker_mock · check.py cond h 已有真工具基建！）
- 现状：check.py L95-130 `_resolve_rc()` 优先真 `/apps/mentor/.../rules_syntax_checker`，fallback mock；cond h 断言「真 rules_syntax_checker 对 b_syntax_good=exit0 / b_syntax_bad=exit≠0」。eval host 无真二进制 ⇒ cond h 跑 mock（自测 mock）；.75 有真二进制 ⇒ cond h 跑真工具。
- check_live 升级：在 .75 显式 RC=真路径，跑 cond h 的真工具路径，断言 ① b_syntax_good 真 exit0 ② b_syntax_bad 真 exit≠0 ③ mock exit == 真 exit（3 个 hidden deck 逐个比对）。
- live-neg：mock 对某 deck 误判 exit0（应 exit1）→ check_live 真工具 exit1 抓到 mock 保真度破裂。
- 风险：最低（基建已在 check.py，check_live 仅「在 .75 强制走真二进制」）。

---

#### R2.2 批次（解冻次轮 · 3 条 · skipper 家族 · PROBE-THEN-DECIDE）

**关键不确定**：r1229 只确认 skipper 二进制 **PRESENT**（`/apps/empyrean/tools/skipper/bin/skipper`），**未确认 headless/batch 模式可跑**（skipper 是 GUI 应用）。mock 是用 tclsh8.6 + 合成 db* procs 驱动候选 Tcl，并非直接调真 skipper。⇒ R2.2 首步必须探真 skipper 是否有 batch CLI（如 `skipper -b <tcl> <gds>` 或 `skipper -noterm` 之类）能 dbImport+dbLibSummary 并打印结果。

**4-6. DummyMeas-001 / GDSBump2-001 / PGLayout-001**（skipper_mock · db* API）
- 探针（解冻后 R2.2 第一步，≤5 min）：.75 跑 `skipper --help` / `skipper -noterm dummy.tcl LTM.gds` 看是否非 GUI 跑通 + 产出 dbLibSummary 文本。
  - **若 headless 可跑** → check_live：真 skipper dbImport gds_B + dbLibSummary/dbLibLayers/dbCellGetBBox 输出 == mock 解析（topcell/cell count/layer 表/bbox）。
    - live-neg：mock layer 表少一层 → 真工具报全 layer → check_live FAIL。
    - 风险：中（真 skipper db* 语义 vs mock 合成 procs 可能有细节差，需逐 proc 比对；GDSBump2 涉及 dbLayerMove 写回 + dbLibExport，真工具 round-trip 与 mock 导出字节比对）。
  - **若 GUI-only 不可 headless** → 降级结论：记 `BLOCKED: skipper GUI-no-headless-mode`（铁律 2 infra，不写能力结论），3 条 OPT **收口为「mock sufficient」**：Q1=faithful（mock GDSII parser 经 calibredrv 交叉验证语义保真，r1229 已证 LAYER/DATATYPE record 解析与真工具一致）+ Q2=not-fooled（cross-input guard + 独立 re-parse）⇒ 静态判分已足够，保持 `[L0,L1]`，不加 check_live，不改判分。此为 OPT verdict 的合法收口路径（§2 OPT 行「做不了写清缺什么」）。

---

#### 收口判定（解冻后 2 轮内必达）

- **R2.1 3 条**（calibredrv×2 + rules_checker×1）：解冻即做，预期全 PASS → 3 条升 `L2.live`，`judge_layers=[L0,L1,L2.live]`，§5 七项全勾。
- **R2.2 3 条**（skipper×3）：探针决断 —— headless 可跑则升 L2.live；GUI-only 则 OPT 收口 mock-sufficient（不加层、不改判分）。
- **最坏情况**：6 OPT 中 3 条升 L2.live + 3 条收口 mock-sufficient（BLOCKED:skipper-GUI）。无论哪种，6 OPT 全部「有结论」⇒ LIVE 收口条件满足（§8 收口「OPT 有结论」）。
- **报 zhulong**：若有 N 条升 L2.live ⇒ A 汇总通报「Lite-500 C 侧 N 条判分层变更 [L0,L1]→[L0,L1,L2.live]」，是否重跑由 zhulong 定（§6.6）。

**冻结纪律**：本节为只读设计草案，0 改 check.py / cases/*.json / EDA-Flow-Bench 仓库。解冻凭据 = `run/MEMORY_ZHULONG.md` 首行 r3' 收口（§1.1）。
