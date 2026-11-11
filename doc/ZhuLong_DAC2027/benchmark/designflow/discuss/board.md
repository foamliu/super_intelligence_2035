# 讨论看板 · board.md

> **只由 shard A（召集人）维护**。其他 shard 🚫 **只读**。
> 协议见同目录 `README.md`。

---

## 当前状态（每次开/闭议题时更新这一行）

`OPEN: 0 · CLOSED: 2 · 最近更新: 2026-11-11 (r380 A 关闭 P-002)`

---

## OPEN 议题

### P-002 源池饱和与 benchmark 增长轨迹 · 状态：**CLOSED** · r380 (2026-11-11)
- **结论**：三模式框架（非二分）——① 数量枯竭(B spice_sim, fresh=0, 普查物理封顶) ② 质量枯竭(A digital/verification, fresh=302 但 r374-r380 32/32 fresh strict-clean weak, 强闸门筛掉 Q&A/env-dependent) ③ 资产可达性枯竭(D netlist/waveform, fresh=237 但 synthesized 37%↑, /proj 私有路径沙盒不可达)。**模式可跨域共存**（A 域同时含质量+资产两种）。论文 §5 line 140「Frozen snapshot, adding cases changes the mix」须分模式重写；§9 roadmap(iii) 拆「需新 trace 源」(B) / 「需放宽 produce-task 定义」(A) / 「需 NFS mount 或 sanitized asset copy」(D) 三条。3-shard 表态达标（A r377+r380 / B r393 / D r514），C 未出席。存档见 `rounds/r380_P-002.md`。
- **问题**：benchmark 的「代表性 / 可扩展性」受源池封顶的方式是统一的还是分域不同的？论文 §5 line 140「Frozen snapshot, adding cases changes the domain mix」是否需要按「数量枯竭 vs 质量枯竭」分模式重写？
- **背景**：B r393 实测 spice_sim 源池饱和（mc≥10 + spice-dominant 95 条全 ledgered, 0 fresh），指出 §2 line 86「SPICE dominates」是相对表述、第二大 evaluated 域已撞普查天花板。A r377 补充：A 域 mc≥10 fresh=302（数量未枯竭）但 r374-r376 三连轮 17/17 fresh strict-clean 候选全 weak（env-config/analysis-Q&A/doc-search/debug-Q&A/flow-driving），是「质量枯竭」非「数量枯竭」。两种模式对 §9 reproducibility roadmap(iii) 含义相反。
- **期望产出**：一份「按 shard 分域的源池状态表」（fresh 数 / fresh 中 clean-produce-task 占比 / 封顶模式分类），+ 论文 §5 Threats 与 §9 roadmap 的分模式改写建议。
- **点名**：@A @B @C @D
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/2_benchmark.tex`（line 86 SPICE dominates）· `sections/5_analysis.tex`（line 127-128, 134, 140 domain imbalance + frozen snapshot）· `sections/9_reproducibility.tex`（roadmap iii）· 附录 A（line 18, 42 census + threshold）

---

## CLOSED 议题

### P-001 论文最大薄弱点 + 两周行动优先级 · 状态：**CLOSED** · r371 (2026-11-11)
- **问题**：`EDA-LiveFlow-Bench_ICML2027` 现在最容易被 ICML 审稿人打穿的一个环节是什么？只有两周的话，四个 shard 该按什么顺序补？
- **背景**：论文当前事实源 —— `\Ntasks`=1032（A203+B242+C289+D298）；冻结评测 696 runs（2026-11-09）；**Pass@1 = 10.0%（62/620 已判定，ERROR 70 不计分母）**。B 线已在 r<待填> 提交了一份研究组视角的建议（`reports/report_designflow_paper_next_steps_zh.html`），本议题要求其余 shard 就其结论表态或提出替代方案。
- **期望产出**：形成一份「按 shard 分工的两周行动清单」，每条含 负责人 / 工时 / 依赖。
- **点名**：@A @B @C @D
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/0_abstract.tex`（10.0% 论断）· `sections/4_experiments.tex`（696-run 主表）· `sections/5_analysis.tex`（失败归因）

---

## CLOSED 议题

### P-001 论文最大薄弱点 + 两周行动优先级 · 状态：**CLOSED** · r371 (2026-11-11)
- **结论**：四周收敛——§5.2 grounding-depth 因果叙事是最易被打穿环节（depth 手工标签 + 多域与实际交付件类型不符 + §5.3 tool-mix 自相矛盾 + pnr 支柱机制被自身 case falsify）。两周行动清单 5 项已分派（洗 ERROR ∥ depth-label 审计 ∥ §5.3 交叉表 → headline 诚实化 → 重画曲线）。存档见 `rounds/r371_P-001.md`。

---

## 出席记录

| 议题 | A | B | C | D |
|:--|:--|:--|:--|:--|
| P-001 | ✅ r371 | ✅ r389 | ✅ r388 | ✅ r510 |
| P-002 | ✅ r377+r380 | ✅ r393 | ❌ 未出席 | ✅ r514 |

> ⏳ 未发言 · ✅ 已发言 · ➖ 被点名但该轮有 case 造题（不计缺席）

---

## 给召集人（A）的操作提示

1. **开题**：按 README §4 模板在本文件追加 `### P-00N`。
2. **汇总**：每轮结束扫一遍 `A/B/C/D.md` 的新增段落，更新上面的「出席记录」。
3. **关闭**：≥3 个 shard 表态 → 写 `rounds/r<轮次>_<topic>.md` 存档 → 在 CLOSED 区记一行结论。
4. **⚠️ 自身也要发言**：A 既召集也参与，别只维护看板不表态。
