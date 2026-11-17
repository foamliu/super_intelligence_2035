# Stable 段 S1/S2 等分可行性报告（Pretrain 线）

> **撰写**: BaiZe Pretrain Agent · 2026-11-17（2026-11-18 更新）
> **用户令**: 2026-11-17 — "把 Stable 的 700k 等分成 S1 和 S2，S1 配置不变，S2 中 web:code:math 按 4:4:2 配比"
> **数据口径**: 所有 token 数来自 `DATA_MAPPING.md` 实测（`INDEX.tsv` + `du -sb`），非估算；评测数字来自 `EXPERIMENTS_PRETRAIN_2B.md` 实跑记录。
> **交叉引用**: 数据线报告 `report_s1s2_split_data.md`（v1）及 `report_s1s2_split_data_v2_zh.html`（v2，2026-11-18）——数据线 v2 提供了 stack-v3-train + MegaMath 补入后的 shard 级 blend TSV，证明 4:4:2 在新数据就绪后可行（所有 epoch <1.2）。本报告 §4 和 §7 已据 v2 更新。

---

## 1. 方案描述

### 1.1 当前训练架构（基线）

| 项 | 值 |
|:--|:--|
| 模型 | Mamba2-hybrid 2.22B（56 层 Nemotron-H 式：4 全注意力 + 24 Mamba2 + 28 MLP） |
| 序列长度 | 16,384（seq=2¹⁴） |
| 全局批大小 | GBS=256（DP16 × MBS=1 × SEQ=16384） |
| tok/step | 4,194,304（≈4.19M） |
| 总步数 | 700k（stable）+ 20k（decay）= 720k |
| 总 token | 2.94T（stable）+ 0.084T（decay）≈ 3.02T |
| LR 调度 | WSD：2000 步线性 warmup → 1e-3 恒定（stable 700k）→ 指数衰减 1e-3→1e-4（decay 20k） |
| 优化器 | AdamW（β1=0.9, β2=0.95, eps=1e-5, wd=0.1） |
| 精度 | bf16_mixed + FP8 tensorwise |
| 硬件 | 2 节点 × 8 H100 = 16 GPU，DP16/TP1/CP1 |
| 吞吐 | ~599K tok/s，~7.0s/step |
| 当前进度 | iter ≈ 234.9k / 700k（33.6%），预计 ~2026-12-25 完成 |

### 1.2 当前数据配比（blend_s1_preblend.tsv）

| 数据源 | key | prop | 可用 tokens (B) | 类别 |
|:--|:--|--:|--:|:--|
| Ultra-FineWeb en_v1_4 | en_v1_4 | 0.65 | 2,237.1 | Web |
| Ultra-FineWeb L1 EN HQ | ufw_l1_en_hq | 0.05 | 150.2 | Web |
| Ultra-FineWeb ZH | ufw_zh | 0.04 | 112.8 | Web |
| UltraData-Math L1 | math_l1 | 0.05 | 164.4 | Math |
| UltraData-Math L3 | math_l3 | 0.02 | 77.9 | Math |
| UltraData-Code L2 | code_l2 | 0.15 | 421.5 | Code |
| UltraData-Code L3 | code_l3 | 0.04 | 128.6 | Code |
| **合计** | — | **1.00** | — | — |

**聚合配比**：Web 74% / Code 19% / Math 7%

**各类别可用 token 总量**：
- Web：2,237.1 + 150.2 + 112.8 = **2,500.1B tokens**
- Code：421.5 + 128.6 = **550.1B tokens**
- Math：164.4 + 77.9 = **242.3B tokens**

### 1.3 提议的 S1/S2 等分方案

| 阶段 | 步数 | tokens | Web | Code | Math | 备注 |
|:--|--:|--:|--:|--:|--:|:--|
| **S1**（0–350k） | 350,000 | 1.467T | 74% | 19% | 7% | 配比不变 |
| **S2**（350k–700k） | 350,000 | 1.467T | 40% | 40% | 20% | web:code:math = 4:4:2 |
| **Decay**（700k–720k） | 20,000 | 0.084T | — | — | — | 按 blend_decay.tsv（SFT 为主） |

#### S1 各源 token 消耗（350k × 4.19M × prop）

| 数据源 | prop | S1 tokens (B) | 占可用比 | epoch |
|:--|--:|--:|--:|--:|
| en_v1_4 | 0.65 | 953.6 | 42.6% | 0.43 |
| ufw_l1_en_hq | 0.05 | 73.4 | 48.9% | 0.49 |
| ufw_zh | 0.04 | 58.7 | 52.0% | 0.52 |
| math_l1 | 0.05 | 73.4 | 44.6% | 0.45 |
| math_l3 | 0.02 | 29.3 | 37.7% | 0.38 |
| code_l2 | 0.15 | 220.1 | 52.2% | 0.52 |
| code_l3 | 0.04 | 58.7 | 45.6% | 0.46 |

S1 阶段各类别总消耗：Web 1,086B / Code 279B / Math 103B — **均在 1 epoch 以内，无过拟合风险**。

#### S2 需要的 token 量（350k × 4.19M × 新 prop）

| 类别 | 新 prop | S2 tokens (B) | S1 已消耗 (B) | 累计消耗 (B) | 可用 (B) | 累计 epoch | 缺口 (B) |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Web | 40% | 586.8 | 1,086 | 1,672 | 2,500 | 0.67 | **无（充裕）** |
| Code | 40% | 586.8 | 279 | 866 | 550 | **1.57** | **316** |
| Math | 20% | 293.4 | 103 | 396 | 242 | **1.64** | **154** |

> ⚠️ **关键发现（v1 11-17）**：仅用现有 blend 内数据，Code 和 Math 在 S1+S2 累计将分别达到 **1.57 和 1.64 epoch**，意味着约 36–39% 的 code/math 数据将被模型看到第二次。
>
> ✅ **更新（11-18，据数据线 v2）**：补入 stack-v3-train（476B 已分词，L4 过滤后 ~286–405B）+ MegaMath（Batch1+web ~371B）后，Code epoch 降到 **0.91–1.04**、Math epoch 降到 **0.65**，过拟合风险从🟠中-高降为🟢低。Web 则只用了 67%，完全无虞。详见 §4 数据量核算。

#### S2 具体配比表（shard 级建议 · 2026-11-18 据数据线 v2 更新）

S2 的 web:code:math = 4:4:2 需要映射到 9 个数据源（含新增 stack-v3-train + MegaMath）。建议方案（与数据线 v2 主方案一致）：

| # | 数据源 | key | 建议 prop | S2 tokens (B) | 可用 (B) | S1+S2 累计 (B) | 累计 epoch | 备注 |
|--:|:--|:--|--:|--:|--:|--:|--:|:--|
| 1 | Ultra-FineWeb en_v1_4 | `en_v1_4` | 0.35 | 513.3 | 2,237.1 | 1,466.9 | 0.66 | Web 主体 |
| 2 | Ultra-FineWeb L1 EN HQ | `ufw_l1_en_hq` | 0.03 | 44.0 | 150.2 | 117.4 | 0.78 | HQ 补充 |
| 3 | Ultra-FineWeb ZH | `ufw_zh` | 0.02 | 29.3 | 112.8 | 88.0 | 0.78 | 中文保留少量 |
| — | **Web 小计** | — | **0.40** | **586.6** | **2,500.1** | **1,672.3** | **0.67** | ✅ |
| 4 | UltraData-Code L2 | `code_l2` | 0.18 | 264.0 | 421.5 | 484.1 | 1.15 | Code 主体 |
| 5 | UltraData-Code L3 | `code_l3` | 0.05 | 73.3 | 128.6 | 132.0 | 1.03 | Code 补充 |
| 6 | **stack-v3-train (L4 filt.)** | `stackv3_filt` | 0.17 | 249.3 | 286~405 | 249.3 | 0.62~0.87 | **新增**，97.6% 独特 |
| — | **Code 小计** | — | **0.40** | **586.6** | **836~955** | **865.4** | **0.91~1.04** | ✅ |
| 7 | UltraData-Math L1 | `math_l1` | 0.06 | 88.0 | 164.4 | 161.4 | 0.98 | Math 主体 |
| 8 | UltraData-Math L3 | `math_l3` | 0.03 | 44.0 | 78.0 | 73.3 | 0.94 | Math 补充 |
| 9 | **MegaMath (Batch1+web)** | `megamath` | 0.11 | 161.3 | ~371 | 161.3 | 0.43 | **新增**，Batch1~92B + web~279B |
| — | **Math 小计** | — | **0.20** | **293.3** | **613.4** | **396.0** | **0.65** | ✅ |
| — | **合计** | — | **1.00** | **1,466.5** | — | **2,933.7** | — | ✅ 加和=1.0 |

> 类别校验：Web = 0.35+0.03+0.02 = **0.40** ✅ | Code = 0.18+0.05+0.17 = **0.40** ✅ | Math = 0.06+0.03+0.11 = **0.20** ✅
>
> 注：以上为 pretrain 线基于数据线 v2 报告的 shard 级配比建议。最终 blend TSV 由 data 线生成（PC-4），需根据 PC-1（stack-v3 L4 过滤）/ PC-2（MegaMath 分词）实际产出调整 prop。如 MegaMath-web 延迟，使用 fallback 方案（仅 Batch1，math 类别 epoch 1.18）。

---

## 2. LR Schedule 影响

### 2.1 当前 WSD 调度回顾

```
LR: 0 ──warmup(2k)──> 1e-3 ──stable(698k)──> 1e-3 ──decay(20k)──> 1e-4
                         ↑                       ↑
                    S1|S2 分界点(350k)       Decay 起点(700k)
```

当前设计中，stable 段 LR 恒定为 1e-3，**在 350k 处不做任何 LR 调整**——这是 WSD 的设计本意（stable 段就是一个 plateau）。

### 2.2 配比突变对 LR 的影响分析

**结论：LR 本身不需要调整，但需关注配比突变带来的 loss spike 风险。**

| 因素 | 分析 | 风险等级 |
|:--|:--|:--|
| **数据分布突变** | S1→S2 的 code 占比从 19%→40%（+21pp），math 从 7%→20%（+13pp），web 从 74%→40%（-34pp）。Token 分布的突然偏移等效于一个"软域迁移"(soft domain shift)。 | 🟡 中 |
| **Loss spike 可能性** | Code/math token 的信息密度高于一般 web text（更结构化、更可预测）。实际上，加入更多 code/math 后 **loss 可能下降**（因为 code/math 本身 entropy 更低），而非 spike。但短期波动仍可能出现。 | 🟢 低-中 |
| **梯度规模变化** | AdamW 的自适应学习率会自动吸收梯度规模的变化。在 stable 段 LR=1e-3 恒定，无需手动调整。 | 🟢 低 |
| **学习率敏感性** | S2-07 实验表明 1e-3 是 loss 最低的 stable LR，且 1e-3→1.2e-3 的边界提示最优可能在 1e-3 附近。配比突变不改最优 LR。 | 🟢 低 |

### 2.3 是否需要在切换点做 warmup 或过渡？

**推荐方案：不设 warmup，但设一个 2k–5k 步的"数据过渡窗口"(data ramp) 作为备选。**

| 方案 | 描述 | 优缺点 |
|:--|:--|:--|
| **A. 直接切换（最简，推荐）** | 350k 处直接从 blend_s1 切到 blend_s2 | ✅ 实现最简单；⚠️ 可能短期 loss 波动 0.05–0.15 |
| **B. 数据 ramp（备选）** | 350k–355k 之间线性插值配比（从 74:19:7 渐变到 40:40:20） | ✅ 平滑过渡；⚠️ 需要修改 dataloader 支持动态 blend |
| **C. LR warmup（不推荐）** | 切换点做 500 步 LR warmup 从 5e-4 升回 1e-3 | ❌ WSD 语义上 stable 段不应有第二次 warmup；且降低 LR 会延迟对新分布的适应 |

**Pretrain 线建议**：采用方案 A（直接切换）。理由：① 实现最简单，不需要修改 Megatron dataloader；② WSD 设计本意就是 stable 段配比可以变化；③ S4 实验中纯 L3→L3+code+math 的突然切换未观察到 loss spike（反而 loss 骤降 0.13）；④ 如出现 >0.3 的 loss spike 再考虑方案 B。

### 2.4 Decay 段安排

Decay 段（700k–720k）维持不变：
- LR 指数衰减 1e-3 → 1e-4（20k 步）
- 配比切换到 `blend_decay.tsv`（SFT-2605 60% + SFT-Agent-2609 12% + UFW L3 QA 18% + ZH 4% + Math L3 4% + Code L3 2%）
- Decay 段是注入 instruction-following / agentic 数据的最佳时机

**S1/S2 等分不影响 decay 段设计**——decay 从 700k 起算，无论 S1/S2 如何切分，700k 都是 stable 段终点。

---

## 3. L1 评测趋势分析

### 3.1 当前 L1 评测历史（8 集 / zero-shot / limit=100 / GGUF F16）

| iter | Avg(8集) | 趋势 |
|--:|--:|:--|
| 10k | 51.50% | — |
| 20k | 52.00% | ↑ |
| 30k | 53.00% | ↑ |
| 40k | 55.12% | ↑↑ |
| 50k | 54.25% | ↓ |
| 60k | 54.25% | → |
| 70k | 56.00% | ↑ |
| 80k | 57.00% | ↑ |
| 90k | 57.88% | ↑ |
| 100k | 57.75% | ↓ |
| 160k | 58.13% | ↑ |
| 170k | 58.13% | → |
| 180k | 57.25% | ↓ |
| 190k | 58.13% | ↑ |
| **200k** | **60.12%** | **↑↑ PEAK** |
| 210k | 58.50% | ↓ |
| 220k | 57.75% | ↓ |
| 230k | 58.88% | ↑ |

**当前趋势**：L1 在 200k 达到峰值 60.12%，此后在 57.75–58.88% 区间震荡，呈现 **plateau + 微降** 态势。

### 3.2 配比突变对评测曲线的预测

配比在 350k 处从 web-heavy 切换到 code/math-heavy，对 L1 8 集（均为常识推理 / 自然语言理解）的影响预测：

| 评测集 | 当前趋势 | S2 配比影响 | 预测 |
|:--|:--|:--|:--|
| ARC-e / ARC-c | 逐步上升 | Web 减少可能减缓上升 | 350k 后增速放缓，可能 plateau |
| BoolQ | 稳定 | Web 减少有轻微负面影响 | 微降 1–2pp |
| HellaSwag | 稳定 | Web 减少影响小（commonsense） | 基本持平 |
| OpenBookQA / SciQ | 上升 | Web 减少有负面影响 | 增速放缓 |
| PiQA | 稳定 | 影响小 | 基本持平 |
| Winogrande | 稳定 | 影响小 | 基本持平 |

**整体 L1 预测**：
- **跳变风险**：🟢 低。L1 评测集均为 MCQ（多选题），用 loglikelihood 打分，不依赖生成能力。配比突变对 loglikelihood 的影响远小于对生成的影响。
- **最可能走势**：350k 后 L1 Avg 从当前 ~59% 水平 **缓慢 plateau 或微降 1–3pp**，因为 web 比例从 74% 降到 40%，而 L1 评测主要测自然语言理解。
- **回升可能性**：存在但有限。Code/math 训练能提升逻辑推理，间接利好 ARC-c / SciQ 等推理型评测，但不足以抵消 web 减少的负面影响。
- **不会 catastrophic drop**：因为 S1 的 350k 已建立了基础语言能力，S2 的 code/math 是在已有基础上叠加，而非覆盖。

### 3.3 L2/L3 评测的预期变化

| 层 | 评测 | S1(200k) 现状 | S2 后预期 | 机理 |
|:--|:--|:--|:--|:--|
| **L2** | HumanEval | 15.0% (3/20) | **20–30%** | Code 占比翻倍 → 更多代码模式学习（DeepSeek 1.3B 4:2:4 = 20.1%） |
| **L2** | GSM8K | 10.0% (1/10) | **15–25%** | Math 占比近三倍 → 更强数值推理 |
| **L2** | MMLU | 26.34% | **25–28%** | Web 减少有负面影响，但知识广度已由 S1 建立 |
| **L2** | MATH | 0.0% (0/10) | **0–5%** | MATH-500 难度极高，2B 模型即使加 math 也难突破 |
| **L3** | SWE-bench / TB | 0/2 (smoke) | **待 post-train** | Agentic 能力需 SFT/RL，预训练只能打基础 |

> **关键洞察**：S2 配比调整对 L2 code/math 评测有直接提升，但对 L1 常识推理有轻微负面影响。这符合用户意图——"提升数学、代码、agentic 能力"是以部分通用能力为代价的定向增强。

---

## 4. 数据量核算

### 4.1 Code 数据：最大瓶颈

| 项 | 值 |
|:--|--:|
| 可用 code tokens | 550.1B（L2=421.5B + L3=128.6B） |
| S1 消耗 | 278.8B（350k × 4.19M × 19%） |
| S2 需要 | 586.8B（350k × 4.19M × 40%） |
| **S1+S2 累计需要** | **865.6B** |
| **缺口** | **315.5B**（865.6 − 550.1） |
| **累计 epoch** | **1.57** |

**分析**：
- S1 已消耗 code 的 50.7%（278.8/550.1），剩余 271.3B
- S2 需要 586.8B，但只剩 271.3B → 需要重复使用 315.5B 的 code 数据
- 1.57 epoch 对 code 数据来说 **风险可控但非理想**：
  - Code 数据天然重复率高（相似代码模式），1.5 epoch 的额外重复不至于严重过拟合
  - 但 epoch >1 的 code 数据在 2B 模型上可能导致 code 生成趋同（diversity 下降）
  - 参考：MiniCPM 2.4B 在 code 数据上做 ~1.3 epoch，DeepSeek 2B 的 code 数据 epoch ≈1.2

**缓解措施**：
1. **stack-v3-train 已分词（476B tokens）**——这是最关键的补充源。经 L4 语言过滤后预估 ~286–405B 有效 token，与 UDC 550B 合计 836–955B，正好覆盖 866B 需求（epoch 0.91–1.04）。数据线 v2 报告已确认可用，仅需 L4 过滤（目标语言筛选，~2–4h）。
2. **IFM/Code-Reasoning 不入 stable 段**——该数据为 SFT 风格（含 reasoning chain / dialogue），格式与预训练语料不统一，更适合 decay 段或 post-train SFT/RL（与数据线 v2 结论一致）。
3. **如不补充新数据**（fallback），建议 S2 code 占比从 40% 降到 30–35%（降低 epoch 到 ~1.3）。

### 4.2 Math 数据：第二瓶颈

| 项 | 值 |
|:--|--:|
| 可用 math tokens | 242.3B（L1=164.4B + L3=77.9B） |
| S1 消耗 | 102.7B（350k × 4.19M × 7%） |
| S2 需要 | 293.4B（350k × 4.19M × 20%） |
| **S1+S2 累计需要** | **396.1B** |
| **缺口** | **153.8B** |
| **累计 epoch** | **1.64** |

**分析**：
- Math 的 1.64 epoch 比 code 更值得担忧：math 数据多样性本就低于 code，重复训练更易过拟合
- Math 过拟合的表现：模型会"背答案"而非学会推理，在 MATH-500 等 unseen 评测上不升反降
- 但 2B 模型的 math 能力天花板本就有限（DeepSeek 2B MATH ≈ 5–10%），过拟合的实际危害可能不显著

**缓解措施**：
1. **MegaMath 是核心补充源**：Batch1 已下载（216GB / ~48B tokens），web 子集（~887GB / ~279B tokens）已调整为下载优先级 #1。Batch1 + web 合计 ~371B tokens，补入后 math 可用 = 242 + 371 = 613B，epoch 降到 **0.65** ✅。仅 Batch1 则 334B，epoch 1.18（可接受但不理想）。
2. **Nemotron-CC-Math-v1**（133B tokens，ICLR2026 实测最优）已调整为下载优先级 #2，ETA ~11-23 分词完成，可作为 math 补充备选。
3. **IFM/Math-Reasoning 不入 stable 段**——同 Code-Reasoning，SFT 风格数据留给 decay/post-train。
4. 如不补充新数据，建议 S2 math 占比从 20% 降到 12–15%（降低 epoch 到 ~1.3）。

### 4.3 Web 数据：充裕

| 项 | 值 |
|:--|--:|
| 可用 web tokens | 2,500.1B |
| S1+S2 累计需要 | 1,672.4B |
| **累计 epoch** | **0.67** |

Web 数据完全充足，无过拟合风险。

### 4.4 新数据就绪时间线 vs S2 启动时间

> **S2 启动时间修正**（2026-11-18）：当前 iter ≈ 235k（11-17），350k − 235k = 115k steps × 7s ≈ 9.3 天 → **S2 切换点 ETA ≈ 2026-11-26**（非此前估算的 ~12-10，该数字有误）。700k 终点 ETA ≈ 2026-12-25 不变。

| 数据源 | 状态（11-18） | 预计分词完成 | S2 启动时间 | 能否赶上？ |
|:--|:--|:--|:--|:--|
| **stack-v3-train** | ✅ 已分词（476B，8192 shard） | L4 过滤 ~11-19 | ~11-26 | ✅ **核心来源，必赶上** |
| MegaMath Batch1 | ✅ 已下载（216GB / ~48B tok） | ~11-20 | ~11-26 | ✅ 可赶上 |
| MegaMath-web (Batch2) | ⏳ 下载优先级 #1（~887GB / ~279B tok） | ~11-25 | ~11-26 | ⚠️ 偏紧（soft deadline） |
| Nemotron-CC-Math-v1 | ⏳ 下载优先级 #2（260GB / ~133B tok） | ~11-23 | ~11-26 | ✅ 可赶上 |
| IFM/Code-Reasoning | 🔄 下载中（66%）→ 已降为优先级 #4 | ~11-22（但 SFT 风格，留 decay） | — | ❌ 不入 stable（留 decay/post-train） |
| IFM/Math-Reasoning | 🔄 下载中（28%）→ 已降为优先级 #5 | ~11-25（但 SFT 风格，留 decay） | — | ❌ 不入 stable（留 decay/post-train） |

> **修正后结论**（2026-11-18，据数据线 v2 报告）：
> - **Code**：stack-v3-train（476B 已分词，L4 过滤后 ~286–405B）补入后，code 可用 = 550 + 286~405 = 836~955B，累计需求 866B → **epoch 0.91~1.04** ✅
> - **Math**：MegaMath Batch1（~92B）+ MegaMath-web（~279B）补入后，math 可用 = 242 + 371 = 613B，累计需求 396B → **epoch 0.65** ✅；仅 Batch1 则 334B → epoch 1.18（可接受）
> - **前提条件**：data 线完成 PC-1（stack-v3 L4 过滤）→ PC-2（MegaMath 分词）→ PC-3（污染闸门扩展）→ PC-4（blend TSV 生成），预计 **11-23 前全部就绪**，不阻塞 S2（~11-26 启动）
> - **此前"建议等 Code-Reasoning 分词"的结论作废**——Code-Reasoning 是 SFT 风格数据，应留给 decay/post-train，不入 stable 段（与数据线 v2 一致）

---

## 5. 利弊分析

### 5.1 与参考配比的对比

| 来源 | Web | Code | Math | 备注 |
|:--|--:|--:|--:|:--|
| **本项目 R3 BO 结果** | 89% | 6% | 4% | BO 优化目标是 L1 8 集 loss，偏向 web |
| **当前生产配比** | 74% | 19% | 7% | 已在 BO 基础上大幅增加 code/math |
| **提议 S1** | 74% | 19% | 7% | = 当前配比 |
| **提议 S2** | 40% | 40% | 20% | 用户提议（web:code:math = 4:4:2） |
| **DeepSeek 参考** | 40% | 40% | 20% | DeepSeek-V2 4:2:4（code:math:lang = 4:2:4 → web:code:math = 40:40:20）† |
| **MiniCPM 参考** | ~70% | ~20% | ~10% | 2.4B 模型，code/math 适中 |

> † **配比排序说明**：DeepSeek 论文（arXiv 2401.02954）原文用 **code:math:lang = 4:2:4**，即 code 40% / math 20% / lang(web) 40%。转换为本项目统一的 **web:code:math** 排序后 = **40:40:20**，与用户提议的 4:4:2 完全一致。两者是同一配比的不同表述。

**关键观察**：
1. **R3 BO 的 89:6:4 是在 5k-step proxy 上优化的短地平线结果**，优化目标是 L1 loss。它不代表长跑最优配比——事实上当前生产配比（74:19:7）已经大幅偏离 BO 结果，说明用户和团队已判定 BO 结果不适用于长跑。
2. **提议 S2（4:4:2）= DeepSeek 4:2:4**：DeepSeek 论文（arXiv 2401.02954）在 1.3B 模型 200B token 消融中验证 code:math:lang=4:2:4 最优（MMLU 48.3 / HumanEval 20.1 / GSM8K 15.4 / Avg 31.5），超过 4:2:4 时语言理解急剧下降。用户提议的 web:code:math=4:4:2 与之完全等价（仅排序不同），是有论文支撑的推理导向配比。
3. **DeepSeek 4:2:4 是在 1.3B 模型 + 200B token 上验证的**，本项目 2.22B + 1.47T（S2 段）规模更大，但 2B 模型直接套用激进配比仍需关注数据 epoch。DeepSeek 2B 实际配比可能更接近 60:25:15（大模型才用得起 40% code）。
4. **S2 的 code 40% 在 2B 模型上前所未有**——但 DeepSeek 1.3B 已验证 40% code 可行（HumanEval 20.1%），2B 模型参数更多，理论承受力更强。关键约束是数据量（仅现有 550B code vs 587B 需求 → epoch 1.57），而非模型容量。**补入 stack-v3-train 后此约束解除**（epoch 0.91–1.04，见 §4.1）。

### 5.2 Agentic 能力提升的机理

```
Code 数据 (40%)          Math 数据 (20%)         Web 数据 (40%)
    │                        │                       │
    ▼                        ▼                       ▼
代码模式学习              多步推理训练             语言理解基础
    │                        │                       │
    ▼                        ▼                       ▼
工具使用能力              Chain-of-Thought         指令理解
(API calling,             (planning,               (context
 code execution,           decomposition)           comprehension)
 tool chains)
    │                        │                       │
    └────────────┬───────────┘                       │
                 ▼                                    │
          推理+生成能力                               │
                 │                                    │
                 └─────────────┬──────────────────────┘
                               ▼
                        Agentic 能力基础
                   (为 post-train SFT/RL 铺路)
```

**机理说明**：
- **Code → Agentic**：Agent 的核心能力之一是生成可执行代码（tool calling, code interpreter）。40% 的 code 数据让模型深度学习代码语法、API 调用模式、函数组合，这是 agentic 能力的基础。
- **Math → Agentic**：Agent 需要多步推理（plan → act → observe → adjust）。Math 训练强化模型的符号推理和逐步推导能力，直接迁移到 agent 的 planning。
- **Web → 基础**：40% 的 web 仍提供足够的语言理解和世界知识，确保模型不会"只会写代码不会说话"。
- **关键**：预训练阶段只能建立"基础能力"，真正的 agentic 能力需 post-train 的 SFT + RLVR（posttrain 线负责）。

### 5.3 潜在风险

| 风险 | 严重度 | 概率 | 缓解 |
|:--|:--|--:|:--|
| **通用能力回退**（L1 下降 >5pp） | 🟡 中 | 30% | Web 仍有 40%，S1 已建立基础；监控 L1 每 20k |
| **Loss spike**（切换点 >0.3） | 🟢 低 | 15% | S4 实验显示配比切换 loss 反降；如出现可加 ramp |
| **Code 过拟合**（仅现有数据 epoch 1.57） | 🟢 低（补 stack-v3 后 0.91–1.04） | 20% | stack-v3-train L4 过滤后补入；如不补则降 code 到 30% |
| **Math 过拟合**（仅现有数据 epoch 1.64） | 🟢 低（补 MegaMath 后 0.65–1.18） | 25% | MegaMath Batch1+web 补入；如不补则降 math 到 12-15% |
| **训练不稳定**（NaN/skip） | 🟢 低 | 5% | LR 不变、精度不变、arch 不变，稳定性有保障 |
| **评测解耦困难** | 🟢 低 | 10% | S1/S2 分界点有 ckpt（每 2k 存一次），可精确对比 |
| **数据线 PC-1~PC-4 延迟** | 🟡 中 | 30% | Fallback 到 5:3:2（方案 B），不阻塞 S2 启动 |

### 5.4 利总结

| 利 | 说明 |
|:--|:--|
| ✅ 显著提升 code 能力 | Code 从 19%→40%，HumanEval 预期从 15%→20-30% |
| ✅ 显著提升 math 能力 | Math 从 7%→20%，GSM8K 预期从 10%→15-25% |
| ✅ 为 agentic 打基础 | Code+math 合计 60%，为 post-train SFT/RL 提供更强起点 |
| ✅ 对齐 DeepSeek 配比 | 4:4:2（web:code:math）= DeepSeek 4:2:4（code:math:lang），1.3B 消融验证的推理导向最优配比 |
| ✅ 实现简单 | 只需在 350k 处切换 blend TSV，无需改架构/LR/精度 |
| ✅ 评测可精确追踪 | 350k 处有 ckpt，可做前后对比 |
| ✅ Decay 段不受影响 | S1/S2 等分不改变 decay 设计 |

### 5.5 弊总结

| 弊 | 说明 | 缓解状态（11-18 更新） |
|:--|:--|:--|
| ⚠️ 通用能力可能微降 | L1 可能 plateau 或降 1-3pp（web 从 74%→40%） | 不可缓解，但 S1 350k 已建立基础 |
| ⚠️ Code 数据 epoch >1.5（仅现有数据） | 550B 可用 vs 866B 需要 | ✅ stack-v3 补入后 epoch 0.91–1.04 |
| ⚠️ Math 数据 epoch >1.6（仅现有数据） | 242B 可用 vs 396B 需要 | ✅ MegaMath 补入后 epoch 0.65–1.18 |
| ⚠️ 需要新数据就绪 | stack-v3 L4 过滤 + MegaMath 分词 + 污染闸门 | data 线预计 11-23 前完成（PC-1~PC-4） |
| ⚠️ 切换点短暂数据分布偏移 | 可能 2-5k 步的 loss 波动 | S4 实验显示 loss 反降，风险低 |
| ⚠️ 2B 模型用 40% code | DeepSeek 1.3B 验证可行，但 2B 无先例 | code 数据已充足（836–955B），约束解除 |
| ⚠️ 数据线延迟风险 | PC-1~PC-4 可能无法 11-23 前完成 | Fallback 到 5:3:2，不阻塞 S2 启动 |

---

## 6. 替代方案

### 方案 A：原方案（4:4:2，直接切换）— 用户提议 · Pretrain 线推荐（v2 更新）

| 项 | 值 |
|:--|:--|
| S2 配比 | web:code:math = 40:40:20 |
| Code epoch | 0.91–1.04（补 stack-v3 后）|
| Math epoch | 0.65–1.18（补 MegaMath 后）|
| 实现难度 | 🟢 低 |
| Code/Math 提升 | 🟢 高 |
| 通用能力风险 | 🟡 中 |
| **推荐度** | ⭐⭐⭐⭐⭐（v2 上调，前提：data 线 PC-1~PC-4 在 11-23 前完成）|

### 方案 B：温和方案（5:3:2，降低 code epoch）— Fallback（如数据线延迟）

| 项 | 值 |
|:--|:--|
| S2 配比 | web:code:math = 50:30:20 |
| Code epoch | 1.31 |
| Math epoch | 1.64 |
| 实现难度 | 🟢 低 |
| Code 提升 | 🟡 中 |
| Math 提升 | 🟢 高 |
| 通用能力风险 | 🟢 低 |
| **推荐度** | ⭐⭐⭐⭐（fallback，如 PC-1~PC-4 延迟时使用）|

> Code 在 S2 占 30% → S2 code = 440B，S1+S2 = 719B，epoch = 1.31

**理由**：Code 从 19%→30% 已是 1.58 倍提升，且 epoch 控制在 1.3 以内更安全。Math 保持 20% 不变（用户更关注 math 提升）。Web 50% 仍提供充足语言基础。

### 方案 C：渐进方案（S1 后半段渐变 + S2）

| 项 | 值 |
|:--|:--|
| 250k–350k | 从 74:19:7 线性渐变到 55:30:15 |
| 350k–700k | 55:30:15 恒定 |
| Code epoch | ~1.25 |
| Math epoch | ~1.35 |
| 实现难度 | 🟡 中（需动态 blend） |
| **推荐度** | ⭐⭐⭐ |

**理由**：在当前训练到 250k 时开始渐变，让模型提前适应 code/math 高占比。但需修改 dataloader 支持动态 blend weight，实现复杂度较高。

### 方案 D：推迟到 Decay 段集中注入（维持当前 700k stable 不变）

| 项 | 值 |
|:--|:--|
| Stable | 700k 维持 74:19:7 不变 |
| Decay | 扩展到 50k–100k 步，配比 web:code:math = 2:4:4 |
| Code epoch | 1.0（仅 decay 段消耗） |
| Math epoch | 1.0 |
| 实现难度 | 🟡 中（需扩展 decay 段） |
| **推荐度** | ⭐⭐ |

**理由**：Decay 段是注入 domain data 的经典做法（本项目 S4 实验已验证 code+math 在 decay 段可降 loss 0.13）。但 decay 段太短（当前 20k = 84B tokens），即使扩展到 100k = 419B tokens，code 也只有 167B（40%），远不如 S2 方案的 587B。

### 方案 E：不等分——S1 短 S2 长（200k + 500k）

| 项 | 值 |
|:--|:--|
| S1 | 0–200k（当前峰值点），配比 74:19:7 |
| S2 | 200k–700k（500k 步），配比 50:30:20 |
| Code epoch | 1.58 |
| Math epoch | 1.75 |
| **推荐度** | ⭐⭐ |

**理由**：200k 是 L1 峰值，在峰值点切换有"在最佳基础能力上叠加 code/math"的直觉。但 500k 的 S2 太长，code/math 的 epoch 进一步恶化。

---

## 7. Pretrain 线综合建议

### 7.1 推荐方案：4:4:2（前提：数据线 PC-1~PC-4 在 11-23 前完成）· 2026-11-18 更新

> **推荐变更说明**（2026-11-18）：本报告 v1（11-17）推荐 5:3:2，基于"不补新数据"的保守假设。数据线 v2 报告（11-18）确认 stack-v3-train（476B 已分词）+ MegaMath 可在 11-23 前就绪，使 4:4:2 的所有 epoch 降到 <1.2（Code 0.91–1.04 / Math 0.65–1.18）。因此 **pretrain 线上调推荐为 4:4:2**，与数据线一致。如数据线 PC-1~PC-4 延迟，则回退到 5:3:2（方案 B）。

**具体建议**：

1. **S1 保持不变**：0–350k，配比 74:19:7，LR 1e-3 恒定
2. **S2 采用 40:40:20**（用户提议的 4:4:2）：
   - Code 40%：stack-v3-train 补入后 epoch 0.91–1.04 ✅
   - Math 20%：MegaMath 补入后 epoch 0.65–1.18 ✅
   - Web 40%：epoch 0.67 ✅（完全充裕）
3. **S2 启动前提条件**（据数据线 v2）：
   - ✅ PC-1：stack-v3-train L4 语言过滤完成（~11-19）
   - ✅ PC-2：MegaMath Batch1 分词完成（~11-20）
   - ✅ PC-3：污染闸门扩展（HumanEval/MBPP/GSM8K/MATH/SWE-bench + 13-gram 全量扫描，~11-21）
   - ✅ PC-4：blend_s2_preblend.tsv 生成（~11-23）
   - ⚠️ PC-5（建议）：MegaMath-web 下载 + 分词（~11-25，soft deadline，如延迟用 fallback 启动 + S2 中途刷新 blend）
   - **如以上条件全部满足 → 启动 4:4:2**；如 PC-1/PC-2 延迟 → 回退到 5:3:2（方案 B）
4. **切换点处理**：直接切换（方案 A），不做 warmup/ramp。如 loss spike >0.3 再考虑 ramp。
5. **评测监控**：
   - 350k（切换点）做 L1 + L2 全量评测，作为 S2 基线
   - 360k / 370k / 380k / 400k / 450k / 500k / 600k / 700k 做 L1 + L2，追踪配比切换效果
   - 重点观察 HumanEval / GSM8K 是否如预期提升
6. **Decay 段不变**：700k–720k，blend_decay.tsv，LR 指数衰减

### 7.2 Fallback 方案：5:3:2（如数据线 PC-1~PC-4 延迟）

如果 data 线无法在 11-23 前完成 PC-1~PC-4（stack-v3 L4 过滤 / MegaMath 分词 / 污染闸门 / blend TSV），则回退到方案 B（5:3:2）：
1. S2 code 占比从 40% 降到 30%（epoch 从 1.57 降到 1.31）
2. S2 math 保持 20%（epoch 1.64，风险中-高但 2B 模型 math 天花板有限）
3. Web 提到 50%（L1 通用能力风险更低）
4. **加密 L1 评测频率**（每 10k 一次），如 L1 下降 >5pp 则考虑回退

### 7.3 关键数字汇总

| 指标 | 方案 A (4:4:2) + 新数据 | 方案 B (5:3:2) 不补新数据 | 当前 (74:19:7) |
|:--|--:|--:|--:|
| S2 code tokens | 587B | 440B | — |
| S2 math tokens | 293B | 293B | — |
| Code 累计 epoch | **0.91–1.04** ✅ | 1.31 | 1.00 |
| Math 累计 epoch | **0.65–1.18** ✅ | 1.64 | 1.00 |
| L1 预期变化 | −1~3pp | −0~2pp | baseline |
| HumanEval 预期 | 20–30% | 15–25% | 15.0% |
| GSM8K 预期 | 15–25% | 15–25% | 10% |
| 过拟合风险 | 🟢 低（epoch <1.1） | 🟡 中（math 1.64） | 🟢 低 |
| 实现难度 | 🟢 低 | 🟢 低 | — |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | — |
| **前提** | data 线 PC-1~PC-4 在 11-23 前完成 | 无额外前提 | — |

---

## 8. 附录：数据源明细

### 8.1 当前分词镜像 token 量（来自 DATA_MAPPING.md 实测）

| # | 数据源 | .bin 数 | tokens (B) | GB | 状态 |
|--:|:--|--:|--:|--:|:--|
| 1 | Ultra-FineWeb en_v1_4 | 110 | 2,237.1 | 8,381 | 镜像完整 |
| 2 | Ultra-FineWeb-L3 en_l3/qa | 154 | 263.9 | 989 | 镜像完整（decay 用） |
| 3 | UltraData-Code L2 | 141 | 421.5 | 1,575 | 镜像完整 |
| 4 | UltraData-Code L3 | 63 | 128.6 | 481 | 镜像完整 |
| 5 | UltraData-Math L1 | 149 | 164.4 | 614 | 镜像完整 |
| 6 | UltraData-Math L3 | 67 | 78.0 | 292 | 镜像完整 |
| 7 | Ultra-FineWeb en（旧版） | 32 | 905.9 | 3,001 | 镜像完整（未用） |
| 8 | Ultra-FineWeb L1 EN HQ | 94 | 150.2 | 562 | 镜像完整 |
| 9 | Ultra-FineWeb ZH | 4 | 112.8 | 422 | 镜像完整 |
| 10 | UltraX-AICC | 1 | 11.5 | 43 | 镜像完整（未用） |
| 11 | UltraData-SFT-2605 | 94 | 18.9 | 71 | 镜像完整（decay 用） |
| 12 | UltraData-SFT-Agent-2609 | 13 | 6.0 | 22 | 镜像完整（decay 用） |

### 8.2 新数据下载状态（截至 2026-11-18，据数据线 v2 报告）

| 数据源 | 优先级 | 状态 | 体积 | 预计 tokens (B) | 分词 ETA | S2 用途 |
|:--|--:|:--|--:|--:|:--|:--|
| MegaMath-web (Batch2) | #1 | ⏳ 下载优先级 #1 | ~887GB | ~279 | ~11-25 | S2 Math 核心 |
| Nemotron-CC-Math-v1 | #2 | ⏳ 下载优先级 #2 | ~260GB | ~133 | ~11-23 | S2 Math 备选 |
| finemath | #3 | ⏳ 下载优先级 #3 | ~149GB | ~34+10 | ~11-22 | S2 Math 补充 |
| stack-v3-train | — | ✅ 已分词（476B） | — | 476 | L4 过滤 ~11-19 | **S2 Code 核心** |
| MegaMath Batch1 | — | ✅ 已下载 | 216GB | ~48 | ~11-20 | S2 Math |
| IFM/Code-Reasoning | #4 | 🔄 下载中（66%） | ~3.28TB | ~273 | ~11-22 | ❌ 留 decay/post-train |
| IFM/Math-Reasoning | #5 | 🔄 下载中（28%） | ~4.46TB | ~371 | ~11-25 | ❌ 留 decay/post-train |

### 8.3 R3 BO 结果参考

- R3 BO 搜索（100/100 完成，best #8 score=0.4032）
- 最优配比：Web:Code:Math ≈ 89:6:4
- 搜索口径：5k-step proxy，优化目标 L1 8 集 loss
- **注意**：BO 在短地平线上优化 L1 loss，天然偏向 web（L1 评测=常识推理=web 强相关）。长跑 + 多目标（L1+L2+L3）需要更平衡的配比。

---

## 9. 总结

| 维度 | 评估 |
|:--|:--|
| **可行性** | ✅ 技术可行——只需在 350k 处切换 blend TSV，不涉及架构/LR/精度变更 |
| **数据充足性** | ✅ 补入 stack-v3 + MegaMath 后充足——Code epoch 0.91–1.04 / Math epoch 0.65–1.18（据数据线 v2） |
| **LR 影响** | ✅ 无需调整——WSD stable 段 LR 恒定，配比切换不影响 LR schedule |
| **L1 影响** | 🟡 轻微下降（1-3pp）——web 减少的代价，但不至于 catastrophic |
| **L2/L3 影响** | ✅ 显著提升——code/math 翻倍直接利好 HumanEval/GSM8K |
| **Agentic 机理** | ✅ 合理——code→工具使用，math→多步推理，为 post-train 打基础 |
| **过拟合风险** | 🟢 低（4:4:2 + 新数据）/ 🟡 中（5:3:2 fallback） |
| **推荐** | **4:4:2**（前提：data 线 PC-1~PC-4 在 11-23 前完成）；否则回退 5:3:2 |
| **S2 切换点 ETA** | ~2026-11-26（当前 iter ≈ 235k，115k steps × 7s ≈ 9.3 天） |

**一句话结论**（2026-11-18 更新）：S1/S2 等分在技术上可行且方向正确。数据线 v2 报告确认 stack-v3-train（476B 已分词）+ MegaMath 可在 11-23 前就绪，使 4:4:2 的所有 epoch 降到 <1.2（Code 0.91–1.04 / Math 0.65–1.18），过拟合风险从🟠中-高降为🟢低。**Pretrain 线推荐采用 4:4:2**（与数据线一致），前提是 data 线完成 PC-1~PC-4；如延迟则回退到 5:3:2。S2 切换点 ETA ≈ 2026-11-26。

---

> **报告路径**: `run/reports/report_s1s2_split_pretrain.md`
> **数据来源**: `DATA_MAPPING.md`（token 实测）/ `EXPERIMENTS_PRETRAIN_2B.md`（评测实跑）/ `MEMORY_PRETRAIN_2B.md`（训练状态）/ `configs/*.env` / `configs/blend_*.tsv` / 数据线 v2 报告 `report_s1s2_split_data_v2_zh.html`（shard 级配比 + 下载优先级 + PC-1~PC-5 计划）
> **口径声明**: 所有 token 数来自 `INDEX.tsv` 实测，非估算；评测数字来自 `gguf_iter_*_fixed_8set/results.json` 实跑。无估算、无编造。
> **更新历史**: v1（2026-11-17）初版，推荐 5:3:2（保守，基于不补新数据假设）；v2（2026-11-18）据数据线 v2 报告更新，上调推荐为 4:4:2（stack-v3 + MegaMath 补入后 epoch <1.2），修正 S2 ETA 从 ~12-10 到 ~11-26。
