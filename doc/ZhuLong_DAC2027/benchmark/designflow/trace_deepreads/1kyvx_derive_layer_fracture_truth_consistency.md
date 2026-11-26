# trace deepread — 1kyvx (xinqiaoz @ 10.129.2.11, mc103)

- session: `1789710025471_1kyvx` (291KB / 52 msgs / 3 real user turns)
- keywords: drc:1093; pdk:277; calibre:84; .gds:12; lvs:5
- tool_use counts: read_files:10, editor:10, run_approved_command:4, search_codebase:1, list_allowed_files:1
- domain: physical_verify (pdkQaSystem DRC issue handler)

## 用户意图（逐字）

- **U#1 (idx 0)**：一段很长的「Issue Handler — pdkQaSystem Issue 处理工作流」skill 定义（10 步流程 + 两层 README.md 维护 + 中断恢复）。这是给 agent 的工作流指令，不是具体任务。
- **U#2 (idx 19)**：「没有问题，下一步」（确认推进）。
- **U#3 (idx 47)**：「进行下一步之前，这里有一个问题：derive layer vs fracture table and device truth table overall 这个检查的初衷是什么？需要这 3 张表完全一致？如果不要求 truth table 和 fracture table 一致，那么是怎么要求 deck 中的 derived layer 和这两个 table 一致的？毕竟这两个 table 本身就不一致。」

## assistant 交付（final answer）

针对 U#3 的语义 Q&A，基于代码与文档解释 `drcDeriveLayerVsFractureAndTruthOverall` 检查项：

- **不要求三张表完全一致**。逻辑：`expected = fracture 层号集合 ∪ truth 层号集合`（并集）。
- **redundant** = `deriveLayers − (fracture ∪ truth)`：Deck 有衍生层但两个 table 都没有该层号；`layerToLayernameData` 会过滤掉名字含 `MARK` 的层。
- **miss** = `(fracture ∪ truth) − deriveLayers`：table 有层号但 Deck 无对应衍生层；**不做 MARK 过滤**。
- 与 `drcDeriveLayerVsFracture` 的区别：后者按层名逐个比对，前者整体集合比对。
- **mark 层处理逻辑不对称**：redundant 方向过滤 MARK，miss 方向不过滤 → truth 中 `purpose=mark` 的 `SN1_mark, 70;1` 被要求必须出现在 Deck 衍生层中，对反馈人不可理解。

assistant 在 issue 目录 `DRC/issues/0915_yifan/drcDeriveLayerVsFractureAndTruthOverall_sn1markMiss/` 维护 README.md（步骤记录）。

## reframe 判定：VIABLE ✓

- 11-15 令§二 analysis-Q&A/explain 类合法 → 本例为 analysis-Q&A revival。
- reframe 为 mock-behavioral 集合一致性分析 `derive-layer-vs-fracture-truth-set-consistency`（physical_verify，r645-r726 family 新子型）：给定 drc_deck/fracture_table/truth_table 三文件 → 纯 stdlib 计算 redundant/miss/matched 层号集合 + MARK 名衍生层过滤 + mark_in_miss 不对称检测 → JSON 报告。
- distinct vs r726 FractureTableSchemaReport=fracture table 字段 schema 发现 / r723 DrcCwdRaceEvidence=drc.summary 头 CWD 竞争 / r725 PdkQaSyncWorkflowAnalyze=workflow 分析 = 本例 **derive-layer vs (fracture ∪ truth) 集合一致性 + MARK 不对称**。
- BUILD → `EDA-Eval-DesignFlow-DeriveLayerFractureTruthConsistency-001`（k=16 a-p）。

## 已造

- ledger: 1kyvx claimed → case (EDA-Eval-DesignFlow-DeriveLayerFractureTruthConsistency-001)
- covered 454→455, physical_verify 210→211
