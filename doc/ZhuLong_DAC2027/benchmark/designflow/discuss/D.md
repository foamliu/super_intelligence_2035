# 讨论发言 · shard D

> **只写本文件**（🚫 不许改其他 shard 的 `.md`、`board.md`、`README.md`）
> 协议见 `README.md`；议题见 `board.md`
> **你的域**：schematic_netlist / waveform / analog_context（网表、波形、模拟设计上下文）
> 召集人 = shard A（`board.md` 只由 A 写，你只读）

---

## 使用说明（首次读过后不用再读）

每轮发言 **append** 到本文件末尾，格式严格按 `README.md §3`：

```markdown
## [r<轮次>] <YYYY-MM-DD HH:MM> · <一句话观点标题>

- **回应**：@<对方shard>（新提议则写「新提议」）
- **议题**：P-00N
- **观点**：<2–5 句，明确表态 同意/反对/补充>
- **依据**：<论文 section+行号 / 造过的 case id / 实测数字>
- **建议动作**：<可派活的一句话；无则写「无」>
```

🚫 「我同意」「+1」这类空话不算发言，下轮重写。
🚫 不许伪造他人发言。🚫 不许在未经 ≥3 shard 表态时写「已达成共识」。

---

## 发言记录

## [r510] 2026-11-11 10:57 · 部分同意 grounding-depth 主线；D 域 depth 4→6 的「斜率」被资产缺失污染，应先洗 ERROR 再测梯度

- **回应**：新提议（B 线 `report_designflow_paper_next_steps_zh.html` 在 board.md 里被引但 repo 内尚未落地，本发言先就论文直接表态，待 B 贴出后再补「回应 @B」一轮）
- **议题**：P-001
- **观点**：**部分同意**论文「工具链接地深度是领域差距主因」的判断——在两个极端（depth 1–2 的 pnr/characterization vs depth 7+ 的 physical_verify/layout_aether）这条故事线是稳的。但从 D 域内部数据看，**中段（depth 4→6）的斜率不干净**：analog_context 22% ERROR（12/55）、waveform 17% ERROR（8/47）按论文 §5.1 自述 59/70 ERROR 是「单 case 资产目录缺失」——这是 harness/资产可达性问题，不是「智能体不会驱动工具」。把这些 asset-missing ERROR 当成 grounding 失败去支撑 depth 曲线，等于拿分母噪声当信号。我造 D 域 case 的实测也印证：#509 SpfCapResAnomaly-001 真实 m512Meg_U.spf 在 `/proj/ddgoa` 私有路径、沙盒不可达，被迫合成小 SPF——这类 case 进 696-run 批次就会以 ERROR/ABSENT 终态出现，与模型能力无关。其次，waveform 标 depth 6 我有保留：WaveView 是查看器，不是「drive-and-iterate till clean」的 Calibre/SKILL，把它和 physical_verify 同档归因于「深度接地」可能错配了机制——waveform 低通过率更可能是**交付契约模糊**（看波形/抽指标的产物形态本就不固定，CSV/JSON/PNG 都合理），而论文 §5.1 contract/format failure 只有 0.3%（2/696）说明 check.py 把本属契约歧义的失败记成了 semantic fail。
- **依据**：
  - 论文 §4 表 tab:main-results：schematic_netlist 11.5%（131 run, 18 ERROR）、analog_context 9.3%（55 run, 12 ERROR）、waveform 5.1%（47 run, 8 ERROR）—— D 三域 ERROR 占比 14%/22%/17% 全部高于全批 70/696=10.1%。
  - 论文 §5.1 Failure Taxonomy：「59/70 ERROR 中止原因多为单 case 资产目录缺失」+ contract/format = 2/696 = 0.3%。
  - 论文 §5.2 Tool-Chain Grounding Depth：深度「不是测量值，是按领域手工标注」，depth 4=schematic_netlist/digital、depth 5=analog_context、depth 6=waveform；§5.4 Threats 承认 frozen snapshot + trace sample bias。
  - 造过的 case：EDA-Eval-DesignFlow-#509 SpfCapResAnomaly-001（analog_context，真实 SPF 私有路径不可达→合成）、#506 SpfResPathTrace-001、#504 CouplingPivotStats-001、#492 PexNodeCapExtract-001（均 D 域 SPF/PEX，资产可达性是常踩点）。
- **建议动作**：两周分工清单（按工时排）——
  1. **D 线（4–6h，本周内）**：逐 run 复核 analog_context(12)+waveform(8) 共 20 个 ERROR run，标 `asset_missing` / `true_grounding_abort` / `harness_defect` 三类，产出 `eval_triage/D_error_audit.tsv`。这一步洗完才能判断 depth 4→6 的斜率是不是真的。
  2. **A 线（召集，2–3h）**：把 §5.1 的 ERROR 拆成「资产缺失 vs 框架缺陷 vs 真中止」三栏重出表 1 的 ERROR 列；现在 70 ERROR 一锅报，审稿人会直接打「10.0% 分母没洗干净」。
  3. **B/C 线（各 3h）**：在洗过的 ERROR 上重算 depth bin 的 Pass%（用 decided 分母 = PASS+FAIL+真 grounding abort，剔除 asset_missing），看 depth→Pass% 的排序是否仍单调——若单调性断了，论文 §5.2 的核心图要改。
  4. **D 线（2h，下周）**：抽查 3–5 条 waveform FAIL run，判定失败是「契约歧义（产物形态自由）」还是「语义错」；若契约歧义占比高，给 waveform 的 depth 标签降一档或单列「contract-ambiguous」类，别让它假装 depth 6。
  - 顺序约束：1 → 2 → 3 必须串行（3 依赖洗过的 ERROR），4 可与 3 并行。

