# live_eval_summary.md — Lite-500 实跑评估 4-shard 汇总（A 汇总人）

> **生成**：2026-11-26 r1322（shard A 汇总人轮）· **2026-11-27 r1338 刷新**（B 基线歧义已确认：B 预存 L2.live=0，本轮新增=7 ⇒ 总=7；D r1504 12 条 test-field re-sync 入账）
> **依据**：`designflow/live_eval_review_{A,B,C,D}.tsv`（全量填满）+ 各 shard `MEMORY_DESIGNFLOW_<S>.md` 顶部心跳行 + `designflow/live_eval_changes.tsv`（已登记 L2.live 变更）。
> **令源**：`BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`（2026-11-26 18:5x 用户令）§6.5。
> **口径**：500 恒定（不增题不删题）；三分类 = `LIVE-REQ` / `LIVE-OPT` / `LIVE-NA`；`done` = REQ 已落 `check_live`+`judge_layers=[...,L2.live]` 且 §5 七项全绿 / OPT 已有可核查结论（含 BLOCKED）。

---

## 1. 三分类合计（500 条全量）

| shard | 名册 | REQ | OPT | NA | verdict 填满 |
|:--|--:|--:|--:|--:|:--|
| A | 116 | 7 | 3 | 106 | ✅ 116/116 |
| B | 126 | 40 | 8 | 76 | ✅ 126/126 |
| C | 137 | 9 | 3 | 125 | ✅ 137/137 |
| D | 121 | 3 | 9 | 109 | ✅ 121/121 |
| **合计** | **500** | **59** | **23** | **416** | ✅ 500/500 |

- REQ 占比 59/500 = 11.8%（判分实质依赖真实 EDA 工具产物，必须改造）。
- NA 占比 416/500 = 83.2%（deliverable 本身是文本/脚本/日志/问答，静态判分足够）。
- OPT 占比 23/500 = 4.6%（静态已足够，真跑能再加硬断言）。

---

## 2. REQ 改造进度（L2.live 落地）

| shard | REQ 总 | REQ done | REQ pending | L2.live (前→后) | changes.tsv 登记行 | 收口? |
|:--|--:|--:|--:|:--|--:|:--|
| A | 7 | 7 | 0 | 8→11 | 3 | ✅ 收口 |
| B | 40 | 7 | **33** | 0→7 | 7 | ❌ 进行中 |
| C | 9 | 9 | 0 | 16→19 | 3 | ✅ 收口 |
| D | 3 | 3 | 0 | 7→7 | 0 | ✅ 收口 |
| **合计** | **59** | **26** | **33** | **31→44** | **13** | — |

- **新增 L2.live = 13**（44 − 31），与 `live_eval_changes.tsv` 13 行 L2.live-add 登记一致（A3+B7+C3+D0）。另：D r1504 登记 12 行 test-field re-sync（jl 不变 `[L0,L1]`，非 L2.live-add，单独列于 §5）。
- A/C/D 三 shard 的 REQ 全部 done（7+9+3 = 19/19），仅 B 仍有 33 条 REQ 待改造。
- B 40 条 REQ 高度同族（hspice-mock / finesim-mock deck-driven Type A），已获 2026-11-26 用户批准 ≤6–8 条/轮批处理（§4 前提：逐条独立自验 + 单轮 ≤90min + .75 串行）。
- **B 基线歧义说明**：B 心跳行「L2.live 6→7」的「前」是 B 最近一轮（r1300）起跑点，非整轮 review 起点；本表「前→后」统一以 review 起点为基准（B 预存=0）。两者不矛盾，已由 B r1300 心跳「REQ=40(done 7)」+ changes.tsv 7 行 L2.live-add 交叉确认。

### REQ done 明细（已 L2.live 落地的 23 条 + 31 条预存）

预存 L2.live（review 前已是 L2.live，不进 changes.tsv）：A 8（FindPcells/PyAetherCurDesignApi/RtlDesignScenarioBoot-001/-v2/FmRtl2RtlDemo/NetCellMap/SvIntegrateGen/ViewCopyInstCount）+ C 16 + D 7 = 31。

本轮新增 L2.live（进 changes.tsv）13 条：
- **A (3)**：VpsRegrErrorEngineer-001（真 vcs）/ TotemSC-001（真 finesim）/ AsyncFifoSim-001（真 VCS，含 ref full-detection top-2-bit 修复 + TB race 修复）
- **B (7)**：见 B `contract_reform_B.md`（hspice-mock/finesim-mock 家族，r1296–r1300 累计 7 条 L2.live-add）
- **C (3)**：DummyDeck-001 / PowerFill-001 / 见 C `contract_reform_C.md`（calibredrv 家族）
- **D (0)**：D 的 3 REQ 均为预存 L2.live（7→7 无新增）

---

## 3. OPT 收口状态（23 条）

| shard | OPT 总 | OPT done(有结论) | 收口方式 |
|:--|--:|--:|:--|
| A | 3 | 3 | 全 BLOCKED-infra：FsdbVerdiInteg（verdi 二进制缺 .75）/ FloatPinToTop（pyAether 缺 dbCreateLabel/dbGetInstByName/dbGetPinShapes）/ CovFMFlow（fm 缺） |
| B | 8 | 0 | 待 B 推进 |
| C | 3 | 3 | R2.2 closed-with-evidence（skipper×3：Q2 gap-analysis 无静态过/实跑错 gap，mock==real 实证，升 L2.live 违反 §3.5 牙，故 NOT upgraded） |
| D | 9 | 9 | 全有结论：1 BLOCKED-实测(LDOGen .75 ref pass_nf=400 违 pinus ptn)/1 FEASIBLE-WITH-EFFORT(DlySigmaSweep)/4 BLOCKED/AutoCellRmAvPf+HierDescend+RsCalcRnodePlace+InvCSOpt/1 PARTIAL(PyaetherScreenshotVerifyQA)/1 待probe(RsCalcFlow)/1 R1.5收口(DominoPVTsweep) |

- A/C/D 的 OPT 全部有可核查结论（含 BLOCKED）。
- B 的 8 OPT 待推进（B 当前聚焦 REQ 改造）。

---

## 4. 缺口台账（待办）

| 优先级 | shard | 缺口 | 数量 | 说明 |
|:--|:--|:--|--:|:--|
| **P1** | B | REQ pending | 33 | 全 benchmark 最大缺口；hspice-mock/finesim-mock 家族，已批准 ≤6–8/轮批处理 |
| P2 | B | OPT pending | 8 | 待 B REQ 推进后处理 |
| P3 | D | OPT done-but-not-L2.live | 9 | 已有结论（BLOCKED/PARTIAL/待probe），不阻塞收口 |
| P3 | A | OPT BLOCKED-infra | 3 | 工具缺（verdi/pyAether-API/fm），infra 限制非能力结论 |
| — | A/C/D | REQ | 0 | 全 done，收口 |

**收口判据**（§8 收口）：REQ 全绿 + OPT 有结论 + NA 有依据。
- A：✅ 收口（REQ 7/7，OPT 3/3 有结论，NA 106）
- C：✅ 收口（REQ 9/9，OPT 3/3 有结论，NA 125）
- D：✅ 收口（REQ 3/3，OPT 9/9 有结论，NA 109）
- B：❌ 未收口（REQ 7/40，OPT 0/8）—— **B 是全 benchmark 收口的唯一阻塞点**

---

## 5. 报 zhulong（辅线跟随）

- 截至 r1338 `live_eval_changes.tsv` 累计 **25 行**：13 行 L2.live-add（A3+B7+C3+D0）+ 12 行 D test-field re-sync（jl 不变 `[L0,L1]`，r1504 修复 stale test 字段致 ref 误 FAIL/toothless，非 L2.live-add）。对应 commit 范围见各 `repo_commit` 列。
- A 侧变更 commit 范围（EFB master）：`357f5c571`（r1321 AsyncFifoSim-001）及更早 r1319/r1275/r1274 等（见 changes.tsv A 行）。
- zhulong 辅线：每轮起跑记 `repo_commit`；若该轮期间 `live_eval_changes.tsv` 有新行落入 ⇒ 该 run 标 `MIXED` 剔除，下一轮自然重跑（§1.1）。
- **不需要等 zhulong 才能改判分**（§1.1 主辅关系：designflow 主线，不设等待）。

---

## 6. 备注

- 本汇总为 A 汇总人依据各 shard 公开心跳 + review tsv + changes.tsv 生成；B/C/D 的逐条 REQ 改造明细见各自 `contract_reform_<S>.md`。
- 500 恒定：本轮不增题不删题；审视出「题本身坏了」记 `TODO(BLOCKED)` + 报 A，不许借实跑改造之名退题。
- L2.live 总数 44 = 预存 31 + 本轮新增 13。
