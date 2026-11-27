# live_eval_summary.md — Lite-500 实跑评估 4-shard 汇总（A 汇总人）

> **生成**：2026-11-26 r1322（shard A 汇总人轮）· **2026-11-27 r1373 刷新**（B REQ 7→12 done / OPT 重分类 8→15 / REQ 40→33；changes.tsv 25→31 行；L2.live 44→49；A OPT-BLOCKED 工具重探 verdi/fm 仍 absent）· **2026-11-27 r1379 刷新**（B REQ done 12→14 [PFDdeadZone 第14条 + 1]、pending 21→19；changes.tsv 31→34 行；L2.live 49→51；A teeth-guard 监控无回归）· **2026-11-27 r1395 刷新**（B REQ done 14→18 [CtleAcChar #15 / DelayChainEdgeMeas #16 / OpampACSpec #17 / VwlpRefDeckSet #18]、pending 19→15；changes.tsv 34→37 行；L2.live 51→55；A teeth-guard 监控无回归；zhulong thermo r1 跑中 MIXED 未出 thermo_feedback）· **2026-11-27 r1434 刷新**（B REQ done 18→29 全绿收口 [DelaySigma #19 / PorCapSweep #20 / CmlPvtAcReport #21 / StrongarmFomSweep #22 / BistOscRccReorder #23 / FineSimModelScopeFix #24 / Vcc2scTranGen #25 / FineSimWorkflowRunner #26 / StdLibCharTmpl #27 / SpiceTbGen #28 / SlicerFbTimeOpt #29]、pending 15→0；B OPT 15→19（4 REQ 改造中重判 REQ→OPT，全有结论）；changes.tsv 37→49 数据行；L2.live 55→66；**4 shard live-eval REQ 全绿收口（ABCD REQ 全 done）**；A teeth-guard 监控无回归）
> **依据**：`designflow/live_eval_review_{A,B,C,D}.tsv`（全量填满，程序化计数）+ 各 shard `MEMORY_DESIGNFLOW_<S>.md` 顶部心跳行 + `designflow/live_eval_changes.tsv`（已登记 L2.live 变更）。
> **令源**：`BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`（2026-11-26 18:5x 用户令）§6.5。
> **口径**：500 恒定（不增题不删题）；三分类 = `LIVE-REQ` / `LIVE-OPT` / `LIVE-NA`；`done` = REQ 已落 `check_live`+`judge_layers=[...,L2.live]` 且 §5 七项全绿 / OPT 已有可核查结论（含 BLOCKED）。B 的 2 条 `cross_shard`（OtaAcReport-001 / PUvddSweep-001）走 cross_shard 流程，**不进**三分类（§1.3）⇒ 三分类有效样本 498 + 2 cross_shard = 500。

---

## 1. 三分类合计（500 条全量 · review tsv 程序化计数）

| shard | 名册 | REQ | OPT | NA | cross_shard | verdict 填满 |
|:--|--:|--:|--:|--:|--:|:--|
| A | 116 | 7 | 3 | 106 | 0 | ✅ 116/116 |
| B | 126 | 29 | 19 | 76 | 2 | ✅ 126/126 |
| C | 137 | 9 | 3 | 125 | 0 | ✅ 137/137 |
| D | 121 | 3 | 9 | 109 | 0 | ✅ 121/121 |
| **合计** | **500** | **48** | **34** | **416** | **2** | ✅ 500/500 |

- 三分类有效样本 498：REQ 48 (9.6%) / OPT 34 (6.8%) / NA 416 (83.5%)。
- **B 重分类说明**：相较 r1338（B REQ=40/OPT=8），B 累计将 11 条 REQ 重判为 OPT（桩体检后判定静态已足够、真跑仅加硬断言）⇒ 现 B REQ=29/OPT=19。三分类总量不变（B 124 三分类 + 2 cross_shard = 126）。r1395→r1434 又有 4 条 REQ→OPT（FineSimNoRefCktFix/MinpulseRewriteRun/PlatMosThinIdsatIoffSweep/PwlStimTransform/SpGen/StimPWL/TxRonSize/Vcc2scActDeckGen 等 DOWNGRADE 家族，均带 .75 empirical 证据）。
- NA 占比 416/498 = 83.5%（deliverable 本身是文本/脚本/日志/问答，静态判分足够）。

---

## 2. REQ 改造进度（L2.live 落地）

| shard | REQ 总 | REQ done | REQ pending | L2.live (前→后) | changes.tsv 行 | 收口? |
|:--|--:|--:|--:|:--|--:|:--|
| A | 7 | 7 | 0 | 8→11 | 4 (3 add + 1 backfill) | ✅ 收口 |
| B | 29 | 29 | 0 | 0→29 | 29 (全 add) | ✅ 收口 |
| C | 9 | 9 | 0 | 16→19 | 3 (全 add) | ✅ 收口 |
| D | 3 | 3 | 0 | 7→7 | 12 (test-field re-sync, 0 add) | ✅ 收口 |
| **合计** | **48** | **48** | **0** | **31→66** | **48** | ✅ 全收口 |

- **本轮新增 L2.live = 35**（66 − 31），与 `live_eval_changes.tsv` 35 行 L2.live-add 一致（A3 + B29 + C3 + D0）。另：D r1504 登记 12 行 test-field re-sync（jl 不变 `[L0,L1]`，修复 stale test 字段致 ref 误 FAIL/toothless，非 L2.live-add，单独列于 §5）。A 1 行为 review-tsv judge_layers_now backfill（非判分变更）。
- **4 shard REQ 全部 done**（A7 + B29 + C9 + D3 = 48/48），无 pending。**全 benchmark live-eval 收口**。
- B 29 条 REQ 高度同族（hspice-mock / finesim-mock deck-driven Type A），r1296–r1330 累计 29 条 L2.live-add，末条 SlicerFbTimeOpt-001 r1330 @13:35 落地。
- **B 基线歧义说明**：B 心跳行「L2.live →29」的「前」是 B 最近一轮起跑点；本表「前→后」统一以 review 起点为基准（B 预存=0）⇒ B 0→29。两者不矛盾，已由 B changes.tsv 29 行 L2.live-add 交叉确认。

### REQ done 明细（本轮新增 L2.live 35 条 + 预存 31 条）

预存 L2.live（review 前已是 L2.live，不进 changes.tsv）：A 8 + C 16 + D 7 = 31。

本轮新增 L2.live（进 changes.tsv）35 条：
- **A (3)**：VpsRegrErrorEngineer-001（真 vcs）/ TotemSC-001（真 finesim）/ AsyncFifoSim-001（真 VCS，含 ref full-detection top-2-bit 修复 + TB race 修复）
- **B (29)**：见 B `contract_reform_B.md`（hspice-mock/finesim-mock 家族，r1296–r1330 累计 29 条 L2.live-add；末条 SlicerFbTimeOpt-001 r1330）
- **C (3)**：DummyQA-001 / DummyDeck-001 / PowerFill-001（calibredrv 家族，OPT→REQ 升级）
- **D (0)**：D 的 3 REQ 均为预存 L2.live（7→7 无新增）

---

## 3. OPT 收口状态（34 条）

| shard | OPT 总 | OPT done(有结论) | 收口方式 |
|:--|--:|--:|:--|
| A | 3 | 3 | 全 BLOCKED-infra：FsdbVerdiInteg（verdi 二进制缺 .75）/ FloatPinToTop（pyAether 缺 dbCreateLabel/dbGetInstByName/dbGetPinShapes）/ CovFMFlow（fm 缺）。**r1373 重探**：.75 which verdi/fm 仍 absent（PATH 全列无命中）⇒ BLOCKED 维持；**r1434 重探**：eda_flow MCP run_commands on .75 复核 verdi/fm/icv 仍 ABSENT ⇒ BLOCKED 维持 |
| B | 19 | 19 | 全有结论：11 DOWNGRADE REQ→OPT（.75 empirical 证据：mock 非 GT-replay-by-signature，是 faithful-physics 或 candidate-runs-PROVIDED-deck，真跑无静态过/实跑错 gap，升 L2.live 违反 §3.5 牙）+ 8 Type B（candidate-runs-PROVIDED tb/deck/netlist，静态已足够） |
| C | 3 | 3 | R2.2 closed-with-evidence（skipper×3：Q2 gap-analysis 无静态过/实跑错 gap，mock==real 实证，升 L2.live 违反 §3.5 牙，故 NOT upgraded） |
| D | 9 | 9 | 全有结论：1 BLOCKED-实测(LDOGen .75 ref pass_nf=400 违 pinus ptn)/1 FEASIBLE-WITH-EFFORT(DlySigmaSweep)/4 BLOCKED/AutoCellRmAvPf+HierDescend+RsCalcRnodePlace+InvCSOpt/1 PARTIAL(PyaetherScreenshotVerifyQA)/1 待probe(RsCalcFlow)/1 R1.5收口(DominoPVTsweep) |

- **4 shard 的 OPT 全部有可核查结论**（含 BLOCKED）。全 benchmark OPT 收口。

---

## 4. 缺口台账（待办）

| 优先级 | shard | 缺口 | 数量 | 说明 |
|:--|:--|:--|--:|:--|
| — | A/B/C/D | REQ pending | 0 | **全 benchmark REQ 全绿收口**（A7+B29+C9+D3=48/48 done） |
| — | A/B/C/D | OPT pending | 0 | 全有结论（BLOCKED/PARTIAL/Type-B/DOWNGRADE-with-evidence） |
| P3 | D | OPT done-but-not-L2.live | 9 | 已有结论（BLOCKED/PARTIAL/待probe），不阻塞收口 |
| P3 | A | OPT BLOCKED-infra | 3 | 工具缺（verdi/pyAether-API/fm），r1434 eda_flow MCP 复核仍缺，infra 限制非能力结论 |

**收口判据**（§8 收口）：REQ 全绿 + OPT 有结论 + NA 有依据。
- A：✅ 收口（REQ 7/7，OPT 3/3 有结论，NA 106）
- B：✅ 收口（REQ 29/29，OPT 19/19 有结论，NA 76，cross_shard 2）
- C：✅ 收口（REQ 9/9，OPT 3/3 有结论，NA 125）
- D：✅ 收口（REQ 3/3，OPT 9/9 有结论，NA 109）

**🎉 全 benchmark live-eval 收口（2026-11-27 r1434）**：4 shard REQ 48/48 全 done，OPT 34/34 全有结论，NA 416 全有依据。L2.live 31→66（+35）。

---

## 5. 报 zhulong（辅线跟随）

- 截至 r1434 `live_eval_changes.tsv` 累计 **49 数据行**：35 行 L2.live-add（A3+B29+C3+D0）+ 12 行 D test-field re-sync（jl 不变 `[L0,L1]`，r1504 修复 stale test 字段致 ref 误 FAIL/toothless，非 L2.live-add）+ 1 行 A review-tsv backfill（非判分变更）+ 1 行 shard 字段空（数据卫生瑕疵，非判分变更）。对应 commit 范围见各 `repo_commit` 列。
- A 侧变更 commit 范围（EFB master）：`357f5c571`（r1321 AsyncFifoSim-001）及更早 r1319/r1275/r1274 等（见 changes.tsv A 行）。
- zhulong 辅线：每轮起跑记 `repo_commit`；若该轮期间 `live_eval_changes.tsv` 有新行落入 ⇒ 该 run 标 `MIXED` 剔除，下一轮自然重跑（§1.1）。**全 benchmark live-eval 已收口（r1434），changes.tsv 后续应无新 L2.live-add 行**；zhulong 可基于 r1434 之后的稳定 commit 跑 clean 3-run 验收。
- **不需要等 zhulong 才能改判分**（§1.1 主辅关系：designflow 主线，不设等待）。

---

## 6. 备注

- 本汇总为 A 汇总人依据各 shard 公开心跳 + review tsv（程序化计数）+ changes.tsv 生成；B/C/D 的逐条 REQ 改造明细见各自 `contract_reform_<S>.md`。
- 500 恒定：本轮不增题不删题；审视出「题本身坏了」记 `TODO(BLOCKED)` + 报 A，不许借实跑改造之名退题。
- L2.live 总数 66 = 预存 31 + 本轮新增 35。
- **r1434 A 侧自验**（teeth-guard + 汇总刷新 = 本轮唯一产出）：① .75 REACH_OK（eda_flow MCP open_session→run_commands→close_session RC=0 wall=251ms，hfhds201，hspice/hspice64/finesim/vcs/vlogan/calibre 全 in PATH，verdi/fm/icv ABSENT ⇒ A 3 OPT-BLOCKED 维持）② A 3 L2.live neg_selftest 全 OK 无回归（VpsRegr 4-distinct{a,d,g,h} / TotemSC 4-distinct{c,d,f,h} / AsyncFifoSim 3-static{c,d,o}+live-neg，本机实跑）③ A 585 cases judge_layers 齐（574 L0L1 + 11 L2.live 0 missing，unchanged since r1321）④ review tsv 500/500 verdict 全填（A116/B126/C137/D121）⑤ changes.tsv 49 数据行（A4+B29+C3+D12+1 空shard；B 末条 SlicerFbTimeOpt-001 r1330 @13:35 落地 ⇒ B REQ 29/29 全绿，4 shard REQ 全 done）⑥ 两仓 0/0 sync ⑦ 无 thermo_feedback / board/discuss(A.md 不存在⇒无配额) ⑧ research daily 2026-11-27 designflow 建议 NA-A（A-pure 池枯竭无可执行）。**里程碑：全 benchmark live-eval 收口（4 shard REQ 48/48 全 done，OPT 34/34 全有结论，L2.live 31→66）**。A 三线收口不变（REQ7/7+OPT3 BLOCKED有结论+NA106 / P1-P4 done / 116/116 green），A-pure 池枯竭，0 改判分 0 回归。
