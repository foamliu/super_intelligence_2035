# Shard C 判分契约改造进度（contract_reform_C.md）

> **Owner**：shard C（physical_layout: layout_aether / layout_virtuoso / pg_layout / physical_verify）
> **启动**：2026-11-26（运维令「判分契约改造 check_static/check_live 拆分」+「P4 实跑适合性分析」）
> **指南**：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/CONTRACT_REFORM_GUIDE.md`

## 总览

| 优先级 | 状态 | 数量 | 说明 |
|:--|:--|:--|:--|
| P1 — pilot 12 case | ✅ DONE | 5/5 pilot + 2 cleanup = 7/7 | r1204 修 5 pilot + r1207 修 PowerFillMergeGen/RsCalcChkPtGen |
| P2 — 真-EDA L2.live 扩展 | 🔄 进行中 | 4 L2.live done（Lite 内 0 余 / Lite 外 27 候选） | 见 §P2 |
| P3 — mock case 声明 judge_layers | ✅ DONE | 620/620 | r1208 收口；C 全量 629/629 = 618 [L0,L1] + 11 [L0,L1,L2.live] |
| P4 — Lite 实跑适合性分析 | ✅ DONE (r1210) | 137/137 | 见 §P4，Lite-137 内 T1 已全部闭合 |

**CONTRACT 心跳**：`P1=7/7 done · P2=4 L2.live (Lite 内 6 T1 全闭合, Lite 外 27 候选 19T/7F/2P 待转) · P3=620/620 judge_layers · P4=137/137 (T1=6 done / T2=16 / T3=115)`

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

### 已转换（4 条）

| case_id | domain | 轮次 | judge_layers | 自验 |
|:--|:--|:--|:--|:--|
| TrMatchHelperGen-001 | layout_aether | r1205 | [L0,L1,L2.live] ✅ | check_static+check_live PASS, 5 neg FAIL |
| RedundantPinRemoval-* | layout_aether | r1206 | [L0,L1,L2.live] ✅ | PASS |
| AdjViaSelect-001 | layout_aether | r1208 | [L0,L1,L2.live] ✅ | PASS（Lite 内） |
| ListInstCV-001 | layout_aether | r1209 | [L0,L1,L2.live] ✅ | PASS |

注：ListInstCV-001 / RedundantPinRemoval 不在 Lite-137（Lite 外的 P2 推进）。

### 待转换（Lite 外，按 MEMORY r1209 排序）

下一轮 P2 优先非-dict TRUE 候选：`SelFigReport-001` / `CstViewPrecheck-001` / `DecqaRwaBusCount-001`。4 条 `retDict=True`（TopCellNameProduce / ViaOptimGds / AetherStandaloneInstList / AutoCellRmAvPf）需 special wrap（passed==total → pass）后才能转。

FALSE 候选（7 条，mock-only attrs）改造工作量 L（需 strategy-2 强一致或重写 ref），暂缓。

---

## P3 — mock case 声明 judge_layers（620/620 DONE）

- r1208-r1209: 全量 C mock case 声明 `judge_layers=["L0","L1"]`
- C 全量 coverage：629/629
  - `judge_layers=["L0","L1","L2.live"]`：11 条（P1 pilot 5 + cleanup 2 + P2 已转 4）
  - `judge_layers=["L0","L1"]`：618 条（mock，框架回退旧式 check()）
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

## 纪律

- 🚫 未改 check.py / 断言逻辑 / prompt / assets / hidden（P4 只读分析）
- 🚫 未碰别 shard 文件
- 🚫 未碰 jsonl
- ✅ P1 > P4(只读) ≈ P2 > P3 优先级遵循
- ✅ P4 结论：Lite-137 内 T1 已全闭合；P2 继续推 Lite-外候选，与 Lite-500 全绿不冲突
