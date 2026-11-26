# live_eval_summary.md — Lite-500 实跑评估 4-shard 汇总（A 汇总人）

> **生成**：2026-11-26 r1322（shard A 汇总人轮）· **2026-11-27 r1373 刷新**（B REQ 7→12 done / OPT 重分类 8→15 / REQ 40→33；changes.tsv 25→31 行；L2.live 44→49；A OPT-BLOCKED 工具重探 verdi/fm 仍 absent）· **2026-11-27 r1379 刷新**（B REQ done 12→14 [PFDdeadZone 第14条 + 1]、pending 21→19；changes.tsv 31→34 行；L2.live 49→51；A teeth-guard 监控无回归）· **2026-11-27 r1395 刷新**（B REQ done 14→18 [CtleAcChar #15 / DelayChainEdgeMeas #16 / OpampACSpec #17 / VwlpRefDeckSet #18]、pending 19→15；changes.tsv 34→37 行；L2.live 51→55；A teeth-guard 监控无回归；zhulong thermo r1 跑中 MIXED 未出 thermo_feedback）
> **依据**：`designflow/live_eval_review_{A,B,C,D}.tsv`（全量填满，程序化计数）+ 各 shard `MEMORY_DESIGNFLOW_<S>.md` 顶部心跳行 + `designflow/live_eval_changes.tsv`（已登记 L2.live 变更）。
> **令源**：`BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`（2026-11-26 18:5x 用户令）§6.5。
> **口径**：500 恒定（不增题不删题）；三分类 = `LIVE-REQ` / `LIVE-OPT` / `LIVE-NA`；`done` = REQ 已落 `check_live`+`judge_layers=[...,L2.live]` 且 §5 七项全绿 / OPT 已有可核查结论（含 BLOCKED）。B 的 2 条 `cross_shard`（OtaAcReport-001 / PUvddSweep-001）走 cross_shard 流程，**不进**三分类（§1.3）⇒ 三分类有效样本 498 + 2 cross_shard = 500。

---

## 1. 三分类合计（500 条全量 · review tsv 程序化计数）

| shard | 名册 | REQ | OPT | NA | cross_shard | verdict 填满 |
|:--|--:|--:|--:|--:|--:|:--|
| A | 116 | 7 | 3 | 106 | 0 | ✅ 116/116 |
| B | 126 | 33 | 15 | 76 | 2 | ✅ 126/126 |
| C | 137 | 9 | 3 | 125 | 0 | ✅ 137/137 |
| D | 121 | 3 | 9 | 109 | 0 | ✅ 121/121 |
| **合计** | **500** | **52** | **30** | **416** | **2** | ✅ 500/500 |

- 三分类有效样本 498：REQ 52 (10.4%) / OPT 30 (6.0%) / NA 416 (83.5%)。
- **B 重分类说明**：相较 r1338（B REQ=40/OPT=8），B 将 7 条 REQ 重判为 OPT（桩体检后判定静态已足够、真跑仅加硬断言）⇒ 现 B REQ=33/OPT=15。三分类总量不变（B 124 三分类 + 2 cross_shard = 126）。
- NA 占比 416/498 = 83.5%（deliverable 本身是文本/脚本/日志/问答，静态判分足够）。

---

## 2. REQ 改造进度（L2.live 落地）

| shard | REQ 总 | REQ done | REQ pending | L2.live (前→后) | changes.tsv 行 | 收口? |
|:--|--:|--:|--:|:--|--:|:--|
| A | 7 | 7 | 0 | 8→11 | 4 (3 add + 1 backfill) | ✅ 收口 |
| B | 33 | 18 | **15** | 0→18 | 18 (全 add) | ❌ 进行中 |
| C | 9 | 9 | 0 | 16→19 | 3 (全 add) | ✅ 收口 |
| D | 3 | 3 | 0 | 7→7 | 12 (test-field re-sync, 0 add) | ✅ 收口 |
| **合计** | **52** | **37** | **15** | **31→55** | **37** | — |

- **本轮新增 L2.live = 24**（55 − 31），与 `live_eval_changes.tsv` 24 行 L2.live-add 一致（A3 + B18 + C3 + D0）。另：D r1504 登记 12 行 test-field re-sync（jl 不变 `[L0,L1]`，修复 stale test 字段致 ref 误 FAIL/toothless，非 L2.live-add，单独列于 §5）。A 1 行为 review-tsv judge_layers_now backfill（非判分变更）。
- A/C/D 三 shard 的 REQ 全部 done（7+9+3 = 19/19），仅 B 仍有 15 条 REQ 待改造。
- B 33 条 REQ 高度同族（hspice-mock / finesim-mock deck-driven Type A），已获 2026-11-26 用户批准 ≤6–8 条/轮批处理（§4 前提：逐条独立自验 + 单轮 ≤90min + .75 串行）。
- **B 基线歧义说明**：B 心跳行「L2.live →14」的「前」是 B 最近一轮起跑点；本表「前→后」统一以 review 起点为基准（B 预存=0）⇒ B 0→14。两者不矛盾，已由 B changes.tsv 14 行 L2.live-add 交叉确认。

### REQ done 明细（本轮新增 L2.live 20 条 + 预存 31 条）

预存 L2.live（review 前已是 L2.live，不进 changes.tsv）：A 8 + C 16 + D 7 = 31。

本轮新增 L2.live（进 changes.tsv）20 条：
- **A (3)**：VpsRegrErrorEngineer-001（真 vcs）/ TotemSC-001（真 finesim）/ AsyncFifoSim-001（真 VCS，含 ref full-detection top-2-bit 修复 + TB race 修复）
- **B (18)**：见 B `contract_reform_B.md`（hspice-mock/finesim-mock 家族，r1296–r1316 累计 18 条 L2.live-add；最新第18条 VwlpRefDeckSet-001 r1316）
- **C (3)**：DummyQA-001 / DummyDeck-001 / PowerFill-001（calibredrv 家族，OPT→REQ 升级）
- **D (0)**：D 的 3 REQ 均为预存 L2.live（7→7 无新增）

---

## 3. OPT 收口状态（30 条）

| shard | OPT 总 | OPT done(有结论) | 收口方式 |
|:--|--:|--:|:--|
| A | 3 | 3 | 全 BLOCKED-infra：FsdbVerdiInteg（verdi 二进制缺 .75）/ FloatPinToTop（pyAether 缺 dbCreateLabel/dbGetInstByName/dbGetPinShapes）/ CovFMFlow（fm 缺）。**r1373 重探**：.75 which verdi/fm 仍 absent（PATH 全列无命中）⇒ BLOCKED 维持 |
| B | 15 | 0 | 待 B 推进（B 当前聚焦 REQ 改造） |
| C | 3 | 3 | R2.2 closed-with-evidence（skipper×3：Q2 gap-analysis 无静态过/实跑错 gap，mock==real 实证，升 L2.live 违反 §3.5 牙，故 NOT upgraded） |
| D | 9 | 9 | 全有结论：1 BLOCKED-实测(LDOGen .75 ref pass_nf=400 违 pinus ptn)/1 FEASIBLE-WITH-EFFORT(DlySigmaSweep)/4 BLOCKED/AutoCellRmAvPf+HierDescend+RsCalcRnodePlace+InvCSOpt/1 PARTIAL(PyaetherScreenshotVerifyQA)/1 待probe(RsCalcFlow)/1 R1.5收口(DominoPVTsweep) |

- A/C/D 的 OPT 全部有可核查结论（含 BLOCKED）。
- B 的 15 OPT 待推进（B 当前聚焦 REQ 改造）。

---

## 4. 缺口台账（待办）

| 优先级 | shard | 缺口 | 数量 | 说明 |
|:--|:--|:--|--:|:--|
| **P1** | B | REQ pending | 15 | 全 benchmark 最大缺口；hspice-mock/finesim-mock 家族，已批准 ≤6–8/轮批处理 |
| P2 | B | OPT pending | 15 | 待 B REQ 推进后处理 |
| P3 | D | OPT done-but-not-L2.live | 9 | 已有结论（BLOCKED/PARTIAL/待probe），不阻塞收口 |
| P3 | A | OPT BLOCKED-infra | 3 | 工具缺（verdi/pyAether-API/fm），r1373 重探仍缺，infra 限制非能力结论 |
| — | A/C/D | REQ | 0 | 全 done，收口 |

**收口判据**（§8 收口）：REQ 全绿 + OPT 有结论 + NA 有依据。
- A：✅ 收口（REQ 7/7，OPT 3/3 有结论，NA 106）
- C：✅ 收口（REQ 9/9，OPT 3/3 有结论，NA 125）
- D：✅ 收口（REQ 3/3，OPT 9/9 有结论，NA 109）
- B：❌ 未收口（REQ 18/33，OPT 0/15）—— **B 是全 benchmark 收口的唯一阻塞点**

---

## 5. 报 zhulong（辅线跟随）

- 截至 r1395 `live_eval_changes.tsv` 累计 **37 行**：24 行 L2.live-add（A3+B18+C3+D0）+ 12 行 D test-field re-sync（jl 不变 `[L0,L1]`，r1504 修复 stale test 字段致 ref 误 FAIL/toothless，非 L2.live-add）+ 1 行 A review-tsv backfill（非判分变更）。对应 commit 范围见各 `repo_commit` 列。
- A 侧变更 commit 范围（EFB master）：`357f5c571`（r1321 AsyncFifoSim-001）及更早 r1319/r1275/r1274 等（见 changes.tsv A 行）。
- zhulong 辅线：每轮起跑记 `repo_commit`；若该轮期间 `live_eval_changes.tsv` 有新行落入 ⇒ 该 run 标 `MIXED` 剔除，下一轮自然重跑（§1.1）。**当前 zhulong thermo r1 跑中（410/500=82%·Pass@1=15.71%·repo_commit 持续漂移⇒将标 MIXED·未出 thermo_feedback_r1.md）**。
- **不需要等 zhulong 才能改判分**（§1.1 主辅关系：designflow 主线，不设等待）。

---

## 6. 备注

- 本汇总为 A 汇总人依据各 shard 公开心跳 + review tsv（程序化计数）+ changes.tsv 生成；B/C/D 的逐条 REQ 改造明细见各自 `contract_reform_<S>.md`。
- 500 恒定：本轮不增题不删题；审视出「题本身坏了」记 `TODO(BLOCKED)` + 报 A，不许借实跑改造之名退题。
- L2.live 总数 55 = 预存 31 + 本轮新增 24。
- **r1395 A 侧自验**（teeth-guard + 汇总刷新）：① .75 REACH_OK（hfhds201 RC=0 182ms，hspice/finesim/hspice64/vcs/vlogan/calibre 全 in PATH，verdi/fm/icv absent ⇒ A 3 OPT-BLOCKED 维持）② A 3 L2.live neg_selftest 全 OK 无回归（VpsRegr 4-distinct{a,d,g,h} / TotemSC 4-distinct{c,d,f,h} / AsyncFifoSim 3-static{c,d,o}+live-neg）③ A 585 cases judge_layers 齐（574 L0L1 + 11 L2.live 0 missing）④ review tsv 500/500 verdict 全填（A116/B126/C137/D121）⑤ changes.tsv 37 行（A4+B18+C3+D12；B 自 r1379 14→18 done，最新第18条 VwlpRefDeckSet-001 r1316；B #18 行在 SI 工作树 in-flight 待 B 提交）⑥ 两仓 0/0 sync（工作树仅 B changes.tsv in-flight + EFB 别线 scratch 未碰）⑦ 无 thermo_feedback（zhulong thermo r1 跑中 MIXED）/ board/discuss(A.md) ⑧ research daily 2026-11-27 designflow 建议 RTL-testbench（A 已满足 hidden B）。B 仍是全 benchmark 收口唯一阻塞点（REQ 18/33 done，pending 15）。
