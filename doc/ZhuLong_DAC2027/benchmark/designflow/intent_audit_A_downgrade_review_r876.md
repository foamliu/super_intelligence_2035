# intent_audit_A — downgrade 复审异议 · r876 (2026-11-20)

> 背景：2026-11-15 用户令「用新标准重审已造的题」。`intent_audit_A.tsv` 已有 443 行（r842 落库 415/415，后续 r843–r875 增补）。本轮 r876 抽审最近 30 条（jsonl #406–#435），其中 4 条新增入库（VnetDontTouchDiffProduce-001 / RunSimPprNewShAnalyzeQA-001 / LintRptAnalyzeQA-001 / CompressBasicRunbookQA-001，均 keep）。

## 异议：SramGrpStructAnalyze-001 现判 keep，建议改 downgraded

- **case_id**：`EDA-Eval-DesignFlow-SramGrpStructAnalyze-001`（jsonl #424，digital，mc54，user lorikx）
- **现有 audit 判定**：`keep`（reason: "B档 synthesized, analysis-Q&A: 用户真实意图=模仿前次对话整理 SramEDABistGr..."）
- **本轮复审判定**：`downgraded`（建议处置：重做 → 建 `-v2`）

### 依据（溯源到 trace 原文）

`metadata.trace_source.real_task_summary` 原文：
> 模仿前次对话(1793618006543_5qlqi)整理 SramEDABistGrp2 SRAM BIST 选择组模块结构:分析 RTL 选择逻辑(decoder->one_hot->enable->vmux->wsmux),**产出 structure.md+SVG+_draw_structure.py,并对比 DFT 版差异产出 DFT_diff.md** (本 case 取结构分析阶段,B 档...)

用户真实意图是**一整套交付物**：structure.md + SVG + _draw_structure.py + DFT_diff.md（4 件）。本 case 仅取「结构分析阶段」——即把多交付物的真实任务**裁剪为单交付物**，以适配旧「单 case 单交付」模具。

### 为什么判 downgraded 而非 keep

1. 顶部任务初衷铁律 1：「任务形态 = 用户意图。真实用户在 trace 里想干什么，就造什么样的任务」。用户要的是 4 件套结构整理，不是仅「分析 RTL 选择逻辑」。
2. 2026-11-15 令 §一 问题 3：「有没有因为旧配额规则，把用户真实任务降级/裁剪后才入库的？→ 标 `downgraded`，考虑恢复原形态」。本 case 的「取结构分析阶段」正是为适配旧模具的裁剪。
3. 这**不是 off_intent**（结构分析确是真实意图的一个真子集，不是凭空塞入），而是**真子集裁剪** → downgraded。

### 建议处置

- 🚫 不删旧 case、不删 jsonl 行（保留作旧规则产物证据）。
- ✅ 建 `SramGrpStructAnalyze-002`（或 `-v2`），恢复完整形态：交付 structure.md + SVG + _draw_structure.py + DFT_diff.md 四件套，`check()` 校验四件齐全 + 结构正确 + DFT 差异识别。
- 在 MEMORY 说明「v2 相对 v1：恢复 4 件套交付，v1 仅结构分析阶段」。

### 未改动现有 audit 行

为遵守「不删数据」纪律，**未**修改 `intent_audit_A.tsv` 中该 case 的现有 `keep` 行。本文件为异议记录，留待下轮或人工裁决是否将主表该行改判 downgraded + 建 v2。

---

## 本轮审计统计（最近 30 条，jsonl #406–#435）

- 审计 30 题：keep=29 / off_intent=0 / over_constrained=0 / downgraded=1（SramGrpStructAnalyze-001，本文件异议）
- 4 题新增入库 intent_audit_A.tsv（此前未覆盖），均 keep
- 23 题已在现有 audit 中（多数 keep；SramGrpStructAnalyze-001 为本异议）

## ⚠️ 同步阻塞（最高优先报运维）

本轮无法 push super_intelligence_2035。origin/main 顶部两个 ops/pretrain 提交把 `doc/ZhuLong_DAC2027/` 整树移到了断路径 `doc ZhuLong_DAC2027 run ops[0]/ZhuLong_DAC2027/`（commit f2b027e87 误移，2525bc985 仅恢复 pretrain 线文件，designflow/zhulong/vision 等线仍滞留断路径）。

- 影响：**全部 designflow shard（A/B/C/D）+ zhulong + 其它在 doc/ZhuLong_DAC2027/ 下工作的线**都无法干净 pull/rebase（rebase 触发 file-location conflict，见 r876 实测）。
- 本轮处置：按 §同步纪律 事故 2，**不硬推 rebase、不 stash-pop**；本地提交 shard A 文件（intent_audit_A.tsv + 本文件 + MEMORY_A），**未 push**。
- 请运维发 corrective commit：`git mv "doc ZhuLong_DAC2027 run ops[0]/ZhuLong_DAC2027" doc/ZhuLong_DAC2027`（注意 pretrain 已在正确路径恢复，需避免 both-added 冲突），之后各线 rebase 即可恢复。
