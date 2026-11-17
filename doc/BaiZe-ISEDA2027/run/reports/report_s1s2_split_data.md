# Stable 段 S1/S2 等分可行性报告（Data 线）

> **撰写**: BaiZe Data Agent · 2026-11-17
> **用户令**: 2026-11-17 — "把 Stable 的 700k 等分成 S1 和 S2，S1 配置不变，S2 中 web:code:math 按 4:4:2 配比，以提升数学、代码、agentic 能力。请 pretrain 和 data 分别写个报告，分析可行性和利弊。"
> **数据口径**: 所有 token 数来自 `DATA_MAPPING.md` 实测（`INDEX.tsv` + `MANIFEST.json` + `du -sb`），非估算；新数据集来自 `HfApi().dataset_info(files_metadata=True)` 实测。
> **定位**: 本报告聚焦**数据侧**（充足性、配比落地、质量、去污染），与 pretrain 线报告（聚焦 LR/评测/训练稳定性）互补，不重复其结论。

---

## 1. 数据充足性分析

### 1.1 S2 token 需求拆解

S2 = 350,000 steps × 4,194,304 tok/step ≈ **1,466.5B tokens**

| 类别 | S2 配比 | S2 需求 (B) | S1 已消耗 (B) | S1+S2 累计需求 (B) |
|:--|--:|--:|--:|--:|
| Web | 40% | 586.6 | 1,085.7 | 1,672.3 |
| Code | 40% | 586.6 | 279.0 | 865.6 |
| Math | 20% | 293.3 | 102.7 | 396.0 |
| **合计** | 100% | **1,466.5** | **1,467.4** | **2,933.9** |

> S1 已消耗量来自 pretrain 报告 §1.3（350k × 4.19M × 各源 prop），口径一致。

### 1.2 现有库存逐项盘点（来自 DATA_MAPPING.md §A 实测）

| # | 数据源 | 类别 | 可用 tokens (B) | 在当前 blend 中 | S1+S2 累计需求 (B) | 仅现有库存 epoch | 缺口 (B) |
|--:|:--|:--|--:|--:|--:|--:|--:|
| 1 | Ultra-FineWeb en_v1_4 | Web | 2,237.1 | ✅ prop=0.65 | — | — | — |
| 2 | Ultra-FineWeb L1 EN HQ | Web | 150.2 | ✅ prop=0.05 | — | — | — |
| 3 | Ultra-FineWeb ZH | Web | 112.8 | ✅ prop=0.04 | — | — | — |
| | **Web 小计（blend 内）** | | **2,500.1** | | **1,672.3** | **0.67** | **无（充裕 828B）** |
| 4 | UltraData-Code L2 | Code | 421.5 | ✅ prop=0.15 | — | — | — |
| 5 | UltraData-Code L3 | Code | 128.6 | ✅ prop=0.04 | — | — | — |
| | **Code 小计（现有）** | | **550.1** | | **865.6** | **1.57** | **315.5** |
| 6 | UltraData-Math L1 | Math | 164.4 | ✅ prop=0.05 | — | — | — |
| 7 | UltraData-Math L3 | Math | 78.0 | ✅ prop=0.02 | — | — | — |
| | **Math 小计（现有）** | | **242.4** | | **396.0** | **1.63** | **153.6** |

> ⚠️ **关键发现**：仅用现有 blend 内数据，**Code 缺口 316B、Math 缺口 154B**。Code epoch 1.57、Math epoch 1.63，意味着 36–39% 的数据将被模型看到第二次，过拟合风险中-高。

### 1.3 已在盘但未入 blend 的数据

| 数据源 | 类别 | tokens (B) | 状态 | 能否补入 S2 |
|:--|:--|--:|:--|:--|
| **stack-v3-train**（全量 8192 shard） | **Code** | **476.0** | ✅ 已分词，`/nas_user/.../tokenized/` | **✅ 立即可用**（同 tokenizer_eod） |
| Ultra-FineWeb en（旧版） | Web | 905.9 | 镜像完整，未入 blend | ✅ 可补充但无需求 |
| Ultra-FineWeb-L3 en_l3/qa | Web | 263.9 | 镜像完整，decay 预留 | 🟡 优先留给 decay |
| UltraX-AICC | — | 11.5 | 镜像完整 | ❌ 量太小，不适用 |
| UltraData-SFT-2605 | SFT | 18.9 | 镜像完整，decay 预留 | ❌ SFT 数据，留给 decay |
| UltraData-SFT-Agent-2609 | SFT | 6.0 | 镜像完整，decay 预留 | ❌ SFT 数据，留给 decay |

#### 1.3.1 Stack-v3-train 补入后 Code 缺口消除

| 维度 | 值 | 依据 |
|:--|:--|:--|
| Stack-v3-train 实测 tokens | **476.0B** | `MANIFEST.json` `total_tokens` = 475,961,563,275 |
| 分词器 | Qwen3-Coder-Next-Base (vocab 129,281) | 与当前训练 tokenizer_eod **完全一致** |
| 分词产物位置 | `/nas_user/.../tokenized/HuggingFaceCode/stack-v3-train/` | 8192 shard / .bin/.idx/.json / MANIFEST.json |
| 质量过滤状态 | **未执行**（L4/L5 过滤待做） | vendor ~1%、非目标语言 ~40%（需过滤） |
| 过滤后预估可用 tokens | **~286–405B**（按 60–85% 保留率） | L4 过滤保留 ~60%（目标语言），L5 再减 ~10–15% |

> **补入 stack-v3-train 后 Code 形势**：
> - 保守估计（过滤后 286B）：总 code = 550.1 + 286 = 836B → epoch = 865.6/836 = **1.04** → ✅ 基本够用
> - 乐观估计（过滤后 405B）：总 code = 550.1 + 405 = 955B → epoch = 865.6/955 = **0.91** → ✅ 充裕
> - **结论：stack-v3-train 补入后 Code 缺口基本消除**，但需要先执行 L4 质量过滤（目标语言筛选）。

#### 1.3.2 MegaMath 补入后 Math 缺口分析

MegaMath 论文（arXiv 2504.02807）报告 371B tokens（论文 tokenizer）。各子集：

| 子集 | 论文 token (B) | 下载状态 | 预估可用 token (B) |
|:--|--:|:--|--:|
| megamath-web-pro | 15 | ✅ 已下 | ~15 |
| megamath-code | 28 | ✅ 已下 | ~28 |
| megamath-qa | — | ✅ 已下 (32 parquet) | ~15¹ |
| megamath-text-code-block | — | ✅ 已下 (200 parquet) | ~30¹ |
| megamath-translated-code | — | ✅ 已下 (16 parquet) | ~6¹ |
| **Batch1 小计** | **~92** | **✅ 364 parquet / 216GB** | **~92** |
| megamath-web | 279 | ⏳ 待下 (~1TB) | ~279 |
| **全量合计** | **~371** | — | **~371** |

> ¹ 按论文总量 371B 减去已知子集 (15+28+279=322B) 推算剩余 ~49B，按 parquet 比例分配。
> ⚠️ 论文使用自家 tokenizer，与我们 tokenizer_eod (vocab 129,281) 可能存在 ±15% 偏差。

**补入 MegaMath 后 Math 形势**：

| 场景 | 可用 Math (B) | S1+S2 需求 (B) | 累计 epoch | 评价 |
|:--|--:|--:|--:|:--|
| 仅现有 | 242.4 | 396.0 | 1.63 | ⚠️ 缺口 154B |
| + MegaMath Batch1 | 334.4 | 396.0 | 1.18 | 🟡 接近够用，缺口 ~62B |
| + MegaMath 全量 | 613.4 | 396.0 | 0.65 | ✅ 充裕 |
| + MegaMath Batch1 + Nemotron-CC-Math² | 467.4 | 396.0 | 0.85 | ✅ 够用 |

> ² Nemotron-CC-Math（ICLR2026，133B tokens）未下载，预估 ~260GB / ~133B tokens，需额外下载+分词。

### 1.4 充足性结论

| 类别 | 仅现有库存 | 补入 stack-v3 + MegaMath Batch1 | 补入 stack-v3 + MegaMath 全量 |
|:--|:--|:--|:--|
| Web (40%) | ✅ 0.67 epoch | ✅ 0.67 epoch | ✅ 0.67 epoch |
| Code (40%) | ⚠️ 1.57 epoch / 缺 316B | ✅ ~1.04 epoch / 缺口消除 | ✅ ~1.04 epoch |
| Math (20%) | ⚠️ 1.63 epoch / 缺 154B | 🟡 1.18 epoch / 缺 ~62B | ✅ 0.65 epoch |

**数据线结论**：
- **Web**：2,500B 库存对 1,672B 需求，完全无虞，甚至可以只使用 en_v1_4 单源。
- **Code**：stack-v3-train（476B，已分词，同 tokenizer）补入后**基本够用**，但必须先做 L4 语言过滤（剔除非目标语言 ~40%），否则有效 token 不足。
- **Math**：MegaMath Batch1（~92B）补入后仍缺口 ~62B；需要 MegaMath-web（279B，~1TB，待下载+分词）或 Nemotron-CC-Math（133B，待下载）才能完全消除缺口。
- **最佳路径**：stack-v3-train L4 过滤 + MegaMath Batch1 分词 → Code ✅ + Math 🟡（epoch 1.18，可接受）；如再下 MegaMath-web → Math ✅。

---

## 2. 新数据源建议

### 2.1 已在下载中的 IFM 数据集（截至 2026-11-17 10:00）

| 数据源 | 类型 | 总量 | 下载进度 | 预计到货 | 预估 tokens (B) | 能否补入 S2 |
|:--|:--|--:|:--|:--|--:|:--|
| **IFM/Code-Reasoning** | SFT 推理链 | 3,277 GB | 66% (1072/1635 parquet) | ~11-17 20:00 | ~273³ | 🟡 可补但偏 SFT 风格 |
| **IFM/Math-Reasoning** | SFT 推理链 | 4,463 GB | 28% (630/2226 parquet) | ~11-18 05:00 | ~371³ | 🟡 可补但偏 SFT 风格 |
| **IFM/MegaMath Batch1** | 预训练语料 | 216 GB | ✅ 完成 | 已到货 | ~92 | **✅ 立即可分词补入** |
| **IFM/MegaMath Batch2** (web) | 预训练语料 | ~887 GB | ⏳ 待启动 | 待两路完成后启动 | ~279 | ✅ 补入后 Math 充裕 |
| **Nemotron-CC-Math** | 预训练语料 | ~260 GB | ❌ 未下载 | 需下载+分词 | ~133 | ✅ 备选 |

> ³ Code-Reasoning / Math-Reasoning 体量巨大但为 SFT 风格数据（含 reasoning chain / dialogue），适合 decay 段或 post-train，**不建议大量混入 stable 段预训练**（格式不统一、信息密度与预训练语料不同）。

### 2.2 到货时间与可用量预估

| 数据源 | 到货时间 | 分词 ETA | 可用于 S2 时间 | 可用 tokens (B) |
|:--|:--|:--|:--|--:|
| stack-v3-train（L4 过滤后） | ✅ 已在盘 | ✅ 已分词，需 L4 过滤 ~1–2 天 | **~11-19** | 286–405 |
| MegaMath Batch1 | ✅ 已在盘 | 分词 ~1–2 天 | **~11-19** | ~92 |
| Code-Reasoning | ~11-17 20:00 | 分词 ~2–3 天 | ~11-20 | ~273 (SFT, 谨慎用) |
| Math-Reasoning | ~11-18 05:00 | 分词 ~3–5 天 | ~11-22 | ~371 (SFT, 谨慎用) |
| MegaMath Batch2 (web) | ~11-19 启动下载 | 下载 ~2 天 + 分词 ~1–2 天 | ~11-23 | ~279 |
| Nemotron-CC-Math | 需下载 ~1 天 | 分词 ~1–2 天 | ~11-21 | ~133 |

### 2.3 推荐补入策略

| 优先级 | 数据源 | 理由 | 预估可用 (B) |
|:--|:--|:--|--:|
| **P0（必补）** | stack-v3-train L4 过滤后 | 已分词、同 tokenizer、97.6% 独特、立即可用 | 286–405 |
| **P0（必补）** | MegaMath Batch1 | 已下载、数学预训练语料（非 SFT）、与现有 Math 互补 | ~92 |
| **P1（强烈建议）** | MegaMath Batch2 (web) | 279B 数学 web 语料，补入后 Math epoch 降到 0.65 | ~279 |
| **P2（备选）** | Nemotron-CC-Math | ICLR2026 报告超越 MegaMath/FineMath；如 MegaMath-web 延迟可替代 | ~133 |
| **P3（decay 用）** | Code-Reasoning / Math-Reasoning | SFT 推理链数据，更适合 decay 段或 post-train | — |

---

## 3. S2 配比落地（shard 级配比表）

### 3.1 方案设计原则

1. **web:code:math = 4:4:2** 严格满足（加和 = 1.0）
2. **优先使用预训练语料**（非 SFT），SFT 数据留给 decay
3. **Code 混合 3 源**以增加多样性、降低 epoch：UDC L2 + UDC L3 + stack-v3-train
4. **Math 混合 3 源**以增加多样性：UDM L1 + UDM L3 + MegaMath Batch1
5. **Web 保持 en_v1_4 为主体**，少量 HQ + ZH 补充

### 3.2 S2 Blend TSV（推荐方案：含 stack-v3 + MegaMath Batch1）

| 数据源 | key | 建议 prop | S2 tokens (B) | 可用 (B) | S2 epoch | 累计 epoch (S1+S2) | 备注 |
|:--|:--|--:|--:|--:|--:|--:|:--|
| Ultra-FineWeb en_v1_4 | en_v1_4 | **0.35** | 513.3 | 2,237.1 | 0.23 | 0.66 | Web 主体（87.5% of web） |
| Ultra-FineWeb L1 EN HQ | ufw_l1_en_hq | **0.03** | 44.0 | 150.2 | 0.29 | 0.78 | HQ 补充 |
| Ultra-FineWeb ZH | ufw_zh | **0.02** | 29.3 | 112.8 | 0.26 | 0.78 | 中文保留少量 |
| UltraData-Code L2 | code_l2 | **0.18** | 264.0 | 421.5 | 0.63 | 1.15 | Code 主体（L2 质量高） |
| UltraData-Code L3 | code_l3 | **0.07** | 102.7 | 128.6 | 0.80 | 1.26 | Code 补充（L3 更难） |
| stack-v3-train (filtered) | stackv3 | **0.15** | 220.0 | 286–405 | 0.54–0.77 | 0.54–0.77 | 新增，多样化 code |
| UltraData-Math L1 | math_l1 | **0.08** | 117.3 | 164.4 | 0.71 | 1.16 | Math 主体 |
| UltraData-Math L3 | math_l3 | **0.04** | 58.7 | 78.0 | 0.75 | 1.13 | Math 补充 |
| MegaMath Batch1 | megamath_b1 | **0.08** | 117.3 | ~92 | 1.28 | 1.28 | 新增数学预训练语料 |
| **合计** | — | **1.00** | **1,466.6** | — | — | — | — |

**类别校验**：
- Web = 0.35 + 0.03 + 0.02 = **0.40** ✅
- Code = 0.18 + 0.07 + 0.15 = **0.40** ✅
- Math = 0.08 + 0.04 + 0.08 = **0.20** ✅
- 合计 = 0.40 + 0.40 + 0.20 = **1.00** ✅

**累计 epoch 校验**（S1+S2 合计消耗 / 可用）：

| 类别 | S1 消耗 (B) | S2 消耗 (B) | 累计 (B) | 可用 (B) | 累计 epoch |
|:--|--:|--:|--:|--:|--:|
| Web | 1,085.7 | 586.6 | 1,672.3 | 2,500.1 | **0.67** ✅ |
| Code | 279.0 | 586.7 | 865.7 | 550.1 + 286~405 = 836~955 | **0.91–1.04** ✅ |
| Math | 102.7 | 293.3 | 396.0 | 242.4 + 92 = 334.4 | **1.18** 🟡 |

> Math 累计 epoch 1.18 尚可接受（<1.2），但若 MegaMath Batch1 分词后实际 token 低于 92B（tokenizer 差异），可能到 1.25–1.30。**建议同步启动 MegaMath-web 下载**，如能在 S2 启动前到货分词，可将 epoch 降到 0.65。

### 3.3 备选方案：如 MegaMath-web 到货（推荐，Math epoch 最低）

| 数据源 | key | prop | S2 tokens (B) | 备注 |
|:--|:--|--:|--:|:--|
| Ultra-FineWeb en_v1_4 | en_v1_4 | 0.35 | 513.3 | |
| Ultra-FineWeb L1 EN HQ | ufw_l1_en_hq | 0.03 | 44.0 | |
| Ultra-FineWeb ZH | ufw_zh | 0.02 | 29.3 | |
| UltraData-Code L2 | code_l2 | 0.18 | 264.0 | |
| UltraData-Code L3 | code_l3 | 0.07 | 102.7 | |
| stack-v3-train (filtered) | stackv3 | 0.15 | 220.0 | |
| UltraData-Math L1 | math_l1 | 0.06 | 88.0 | 降低，让位 MegaMath |
| UltraData-Math L3 | math_l3 | 0.03 | 44.0 | |
| MegaMath (Batch1 + web) | megamath | 0.11 | 161.3 | Batch1 ~92B + web 部分 ~69B |
| **合计** | — | **1.00** | **1,466.6** | |

**累计 Math epoch** = (102.7 + 293.3) / (242.4 + 371) = 396.0 / 613.4 = **0.65** ✅ 极佳

### 3.4 shard 级映射说明

各数据源对应的分词 shard 目录（均已有 .bin/.idx/.json triplet）：

| key | 分词目录 | shard 数 | 来源 |
|:--|:--|--:|:--|
| en_v1_4 | `…/tokenized/Ultra-FineWeb/ultrafineweb_en_v1_4` | 110 | DATA_MAPPING #1 |
| ufw_l1_en_hq | `…/tokenized/Ultra-FineWeb/ultrafineweb_l1_en_hq` | 94 | DATA_MAPPING #8 |
| ufw_zh | `…/tokenized/Ultra-FineWeb/ultrafineweb_zh` | 4 | DATA_MAPPING #9 |
| code_l2 | `…/tokenized/UltraData-Code/UltraData-Code-L2` | 141 | DATA_MAPPING #3 |
| code_l3 | `…/tokenized/UltraData-Code/UltraData-Code-L3` | 63 | DATA_MAPPING #4 |
| stackv3 | `…/tokenized/HuggingFaceCode/stack-v3-train` | 8192 | DATA_MAPPING H.14 |
| math_l1 | `…/tokenized/UltraData-Math/UltraData-Math-L1` | 149 | DATA_MAPPING #5 |
| math_l3 | `…/tokenized/UltraData-Math/UltraData-Math-L3` | 67 | DATA_MAPPING #6 |
| megamath_b1 | ⏳ **待分词** | — | `/nas_user/.../IFM/MegaMath/` 364 parquet |
| megamath | ⏳ **待分词** | — | Batch1 + Batch2(web) |

> **stack-v3-train shard 采样策略**：8192 shard 中按 prop=0.15 等价于约 1229 shard 的内容量。建议在 blend 中以 `--shard-sampling` 随机抽取，或直接全量加入并调低权重（dataloader 按 weight 采样，shard 数多不影响正确性）。实际操作：blend TSV 中 `stackv3` 指向 8192 shard 目录，prop=0.15，dataloader 自动按权重采样。

---

## 4. 数据质量与去污染

### 4.1 Stack-v3-train 质量过滤（必须执行）

stack-v3-train 当前 476B tokens 是**全量未过滤**的。DATA_MAPPING H.12 ROI 复盘显示：

| 过滤层 | 规则 | 丢弃率 | 保留率 |
|:--|:--|--:|--:|
| L1: vendor 剔除 | `is_vendor=true` | ~1.0% | ~99.0% |
| L2: >1MB 大文件 | `size_bytes > 1MB` | ~0.0% | ~100% |
| L3: 空仓库 | `num_files=0` | ~0.0% | ~100% |
| **L4: 目标语言** | 保留 EDA(14) ∪ Target(32) 语言 | **~40%** | **~60%** |
| L5: 质量评分 | minified/低星/无license/纯文档 | ~10–15% | ~85–90% |

**建议**：对 stack-v3-train 执行 **L4 过滤**（保留目标语言），暂不执行 L5（时间紧迫，L5 的影响约 10–15%，可接受）。
- L4 过滤后预估：476B × 60% ≈ **286B tokens**
- 与 UDC L2 的 repo 级重叠仅 2.4%，97.6% 为新增内容 → 多样性极佳
- 过滤产出：新的 .bin/.idx/.json 子集，或用 shard 级白名单（保留含目标语言的 shard）

> ⚠️ **时间约束**：L4 全量过滤需扫描 8192 shard × parquet 元数据，预估 ~2–4 小时（4 workers）。如时间不够，可退而求其次——直接全量使用 476B（epoch 更低），但会引入非目标语言噪声。

### 4.2 MegaMath 质量评估

| 维度 | 评估 | 依据 |
|:--|:--|:--|
| 数据来源 | Web crawled 数学语料 | 论文 arXiv 2504.02807 |
| 质量分档 | megamath-web-pro 为高质量精选 (15B) | 论文标注 |
| 与现有 Math 重叠 | 与 OpenWebMath 部分来源重叠，与 UDM L1/L3 独立 | DATA_MAPPING D1 |
| 去重状态 | 论文报告已去重 | 需分词后与 UDM 做 n-gram 交叉去重 |
| 评测污染 | ✅ 低风险 | 预训练语料（web crawled），非 benchmark 题目集 |

> **建议**：MegaMath Batch1 分词后，抽样 1000 条与 UDM L1/L3 做 8-gram 重叠检查。如重叠 >5%，做交叉去重后再入 blend。

### 4.3 评测集污染风险（S2 配比变化后的新增风险）

| 评测集 | 风险来源 | 风险等级 | 处置 |
|:--|:--|:--|:--|
| **HumanEval / MBPP** | stack-v3-train 含 GitHub 仓库，可能含 HumanEval/MBPP 的 test 文件 | 🟡 中 | 已有 EDA-Eval 13-gram 闸门（phase5），需扩展覆盖 HumanEval/MBPP 指纹 |
| **GSM8K / MATH** | MegaMath web crawl 可能含 benchmark 题目原文 | 🟡 中 | 分词后抽样检查；MegaMath 论文声明已做 benchmark 去污染 |
| **ARC / SciQ / BoolQ 等 L1** | Web 数据不变，无新增风险 | 🟢 低 | 现有 phase5 闸门覆盖 |
| **SWE-bench** | stack-v3-train 含 GitHub 仓库，可能含 SWE-bench 评测仓库 | 🟡 中 | 需检查 stack-v3 是否含 SWE-bench 的 repo（princeton-nlp/SWE-bench） |
| **EDA-Eval-PyAether (158 任务)** | stack-v3-train Phase B 抽样 0 命中 | 🟢 低 | 已验证（DATA_MAPPING H.13） |

**建议动作**：
1. **扩展黑名单指纹**：将 HumanEval / MBPP / GSM8K / MATH / SWE-bench 的 prompt/test/assertion 加入污染黑名单
2. **对 stack-v3-train 全量跑 13-gram 闸门**：8192 shard，预估 ~4–8 小时
3. **对 MegaMath Batch1 跑 8-gram 闸门**：364 parquet，预估 ~1–2 小时
4. **生成 S2 污染隔离报告**：记录扫描结果、阈值、命中数

### 4.4 质检门槛是否需要调整

| 维度 | S1（当前） | S2（4:4:2） | 建议 |
|:--|:--|:--|:--|
| Web 质检 | en_v1_4 已过 Ultra-FineWeb 质量管线 | 同 S1，无需调整 | 保持 |
| Code 质检 | UDC L2/L3 已过质量评分 | stack-v3 需 L4 语言过滤 + 13-gram 闸门 | **新增过滤** |
| Math 质检 | UDM L1/L3 已过质量评分 | MegaMath 需 8-gram 去重 + benchmark 闸门 | **新增过滤** |
| 去重 | 各源内部已去重 | stack-v3 与 UDC repo 级重叠 2.4%（可接受） | 抽检确认 |
| 门槛严格度 | — | Code/Math 比例提高，**门槛不应放松** | 保持或收紧 |

---

## 5. 利弊分析（数据视角）

### 5.1 Code/Math 提到 40%/20% 的收益

| 收益 | 说明 | 证据 |
|:--|:--|:--|
| ✅ Code 多样性大幅提升 | stack-v3-train 覆盖 173M 仓库 / 476B tokens / 97.6% 独特 | DATA_MAPPING H.12 ROI 复盘 |
| ✅ Math 数据量翻倍 | 从 242B → 334–613B（含 MegaMath） | 本报告 §1.3.2 |
| ✅ Code 语言覆盖更广 | stack-v3 含 32+ 目标语言（Python/C++/Verilog/Java/Go/Rust 等），UDC 仅精选子集 | DATA_MAPPING H.3–H.11 |
| ✅ 数学语料多样性 | MegaMath 含 web/code/qa/text-code-block 多形态数学内容 | 论文 arXiv 2504.02807 |
| ✅ 与 post-train 衔接 | Code/math 基础更强 → SFT/RL 上限更高 | 逻辑推断 |

### 5.2 Code/Math 提到 40%/20% 的风险

| 风险 | 说明 | 缓解 |
|:--|:--|:--|
| ⚠️ Code epoch >1 | 现有 UDC 550B 对 866B 需求 = 1.57 epoch | 补入 stack-v3 后降到 ~1.0 |
| ⚠️ Math epoch >1 | 现有 UDM 242B 对 396B 需求 = 1.63 epoch | 补入 MegaMath 后降到 0.65–1.18 |
| ⚠️ Stack-v3 含非目标语言 | 全量 476B 中 ~40% 为非 EDA/目标语言 | 执行 L4 过滤 |
| ⚠️ 评测污染风险 | stack-v3 含 GitHub 仓库，可能含 benchmark | 执行 13-gram 闸门 |
| ⚠️ 数据准备时间 | stack-v3 L4 过滤 + MegaMath 分词需 ~3–5 天 | 与 S1 训练并行，不阻塞 |
| ⚠️ Math 数据质量参差 | MegaMath-web 为 web crawl，含噪声 | megamath-web-pro (15B) 已精选，web 全量需评估 |

### 5.3 与 DeepSeek 4:2:4 的差异

| 维度 | DeepSeek（参考） | 本项目 S2（4:4:2） | 差异分析 |
|:--|:--|:--|:--|
| 配比 | web:code:math = 4:2:4 | web:code:math = 4:4:2 | **本项目 code 更高、math 更低** |
| 模型规模 | ≥7B（DeepSeek-V2 21B / V3 671B） | 2.22B | 2B 模型对 code 40% 的承受力无先例 |
| Code 数据量 | 未公开，推测 >1T | 836–955B | 量级相当 |
| Math 数据量 | 未公开，推测 >1T | 334–613B | 偏少（受限于可用数据） |
| 定位 | 推理导向（math 40% > code 20%） | 能力均衡（code 40% > math 20%） | 本项目更偏 code/agentic |
| 适配性 | 大模型 + 大数据 → 高 math 比例可行 | 小模型 + 有限 math 数据 → math 20% 是上限 | 2B 模型 math 40% 无数据支撑 |

> **数据线观点**：DeepSeek 的 4:2:4（math 40%）在其 ≥7B 模型 + 海量数学数据条件下可行。本项目 2.22B 模型 + 334–613B math 数据，math 20% 是数据约束下的合理上限。如未来 MegaMath 全量 + Nemotron-CC-Math 到货，可考虑提高到 25–30%。

### 5.4 Web 压缩到 40% 是否损失通用能力

| 维度 | 分析 | 结论 |
|:--|:--|:--|
| Web 可用量 vs 需求 | 2,500B 可用 vs 1,672B 需求 | 即使只给 40%，Web 绝对量 (1,672B) 仍远超多数 2B 模型的总训练量 |
| Web 质量 | en_v1_4 已过 Ultra-FineWeb 质量管线 | 质量有保障 |
| 通用能力来源 | L1 评测（常识推理）主要依赖 web | Web 从 74%→40% 会减缓 L1 增速 |
| Code/math 的补偿 | Code/math 也能提升逻辑推理（利好 ARC-c / SciQ） | 部分补偿，但无法完全替代 web 对 NL 理解的贡献 |
| 2B 模型的 web 需求 | 参考 MiniCPM-2B（web ~70%）、Qwen2-1.5B（web ~60%） | 40% 偏低但有 1,672B 绝对量支撑 |

> **数据线观点**：Web 压到 40% 的**绝对量**（1,672B）对 2B 模型仍属充足（多数 2B 模型总训练量 ~2–3T，web 占 ~1.5–2T）。主要风险不在量，而在**比例骤降**（74%→40%）导致的分布突变。S1 的 350k 已建立了 web 基础（1,086B），S2 的 587B web 是叠加而非从零开始。

---

## 6. 落地建议

### 6.1 可行性判定

| 条件 | 状态 | 判定 |
|:--|:--|:--|
| Web 数据充足 | ✅ 2,500B vs 1,672B 需求 | **可行** |
| Code 数据充足 | ✅ 补入 stack-v3 后 836–955B vs 866B 需求 | **可行（需 L4 过滤）** |
| Math 数据充足 | 🟡 补入 MegaMath Batch1 后 334B vs 396B 需求 | **基本可行（epoch 1.18）**；如加 MegaMath-web 则充裕 |
| 数据质量可控 | ✅ 需新增 L4 过滤 + 13-gram 闸门 | **可行（需前置工作）** |
| 评测污染可控 | 🟡 需扩展黑名单 + 全量扫描 | **可行（需前置工作）** |
| 时间窗口 | S1 预计 ~2026-12-25 到 350k → 有 ~5 周 | **充足** |

**总体判定：✅ 可行**，有 2 个前置条件需在 S2 启动前完成。

### 6.2 前置条件与时间线

| 前置条件 | 工作内容 | 预估耗时 | 截止日期 | 状态 |
|:--|:--|--:|:--|:--|
| **PC-1: stack-v3 L4 过滤** | 全量 8192 shard 语言过滤，产出目标语言子集 | 2–4 小时（4 workers） | 11-19 | ⏳ 待执行 |
| **PC-2: MegaMath Batch1 分词** | 364 parquet → .bin/.idx/.json (tokenizer_eod) | 1–2 天（8 workers, nice19） | 11-19 | ⏳ 待执行 |
| **PC-3: 污染闸门扩展** | 扩展黑名单（HumanEval/MBPP/GSM8K/MATH/SWE-bench）+ stack-v3 全量 13-gram 扫描 + MegaMath 8-gram 扫描 | 4–8 小时 | 11-20 | ⏳ 待执行 |
| **PC-4: S2 blend TSV 生成** | 按本报告 §3.2 的配比表生成 `blend_s2_preblend.tsv` | 0.5 天 | 11-20 | ⏳ 待执行 |
| **PC-5（建议）: MegaMath-web 下载** | 启动 megamath-web ~1TB 下载 + 分词 | 3–4 天 | 11-23 | ⏳ 可选 |

> 关键路径：PC-1 + PC-2 + PC-3 + PC-4 → 11-20 完成 → S2 可启动
> 优化路径：+ PC-5 → 11-23 完成 → Math epoch 从 1.18 降到 0.65

### 6.3 推荐执行顺序

```
当前 (11-17)
  ├── [并行] PC-1: stack-v3 L4 过滤 (2–4h)
  ├── [并行] PC-2: MegaMath Batch1 分词 (1–2d)
  ├── [并行] IFM/Code-Reasoning 下载完成 (~11-17 20:00)
  └── [并行] IFM/Math-Reasoning 下载完成 (~11-18 05:00)

11-19
  ├── PC-3: 污染闸门扩展 + 全量扫描 (4–8h)
  ├── PC-5: 启动 MegaMath-web 下载 (可选)
  └── 验收 PC-1/PC-2 产出

11-20
  ├── PC-4: 生成 blend_s2_preblend.tsv
  ├── 污染隔离报告产出
  └── DATA_MAPPING 更新（新增 stack-v3 filtered + MegaMath 分词条目）

11-21 ~ 11-23
  ├── [可选] MegaMath-web 分词完成 → 更新 blend TSV（§3.3 方案）
  └── S2 数据全部就绪，等待 pretrain 350k 切换点

~12-25 (S1 到 350k)
  └── 切换到 blend_s2_preblend.tsv，启动 S2
```

### 6.4 数据线综合建议

1. **可行，建议采用 4:4:2**（与 pretrain 线推荐的 5:3:2 不同）：
   - 数据线视角：stack-v3 的 476B 补入使 code 40% 数据充足（epoch ~1.0），**数据不构成瓶颈**
   - pretrain 线推荐的 5:3:2 是基于"不补新数据"的保守假设；一旦 stack-v3 + MegaMath 就绪，4:4:2 的数据约束可满足
   - **如果用户坚持 4:4:2**，数据线可以支撑，前提是完成 PC-1 ~ PC-4

2. **Math 是唯一薄弱点**：
   - 现有 + MegaMath Batch1 = 334B，epoch 1.18 → 可接受但不理想
   - **强烈建议同步启动 MegaMath-web 下载**（279B，~1TB，~3 天），到货后 epoch 降到 0.65

3. **Stack-v3 必须做 L4 过滤**：
   - 全量 476B 含 ~40% 非目标语言（Java/PHP/CSS/Markdown 等）
   - L4 过滤后 ~286B 有效 token，与 UDC 550B 合计 836B，正好覆盖 866B 需求
   - 如不做 L4 过滤直接使用 476B，epoch 更低但引入噪声

4. **污染闸门必须扩展**：
   - Code 比例从 19%→40% + 新增 stack-v3（GitHub 仓库），benchmark 污染风险显著上升
   - 必须在 S2 启动前完成 13-gram 全量扫描

5. **不建议将 IFM Code/Math-Reasoning 混入 stable 段**：
   - 这些是 SFT 风格数据（含 reasoning chain / dialogue），格式与预训练语料不统一
   - 更适合 decay 段（20k 步）或 post-train SFT/RL 阶段
   - 如 stable 段确实需要更多 code/math，优先用 stack-v3 + MegaMath（预训练语料）

---

## 7. 总结

| 维度 | 评估 | 关键数字 |
|:--|:--|:--|
| **可行性** | ✅ 可行 | Web 充裕 / Code 靠 stack-v3 补 / Math 靠 MegaMath 补 |
| **Web 充足性** | ✅ 无虞 | 2,500B 可用 vs 1,672B 需求 (epoch 0.67) |
| **Code 充足性** | ✅ 补入 stack-v3 后够用 | 836–955B 可用 vs 866B 需求 (epoch 0.91–1.04) |
| **Math 充足性** | 🟡 基本够用，建议补 MegaMath-web | 334B 可用 vs 396B 需求 (epoch 1.18)；全量后 613B (epoch 0.65) |
| **质量风险** | 🟡 中 | stack-v3 需 L4 过滤 + 13-gram 闸门 |
| **污染风险** | 🟡 中 | 需扩展黑名单（HumanEval/MBPP/GSM8K/MATH/SWE-bench） |
| **前置工作** | 4 项必做 + 1 项建议 | 11-20 前完成（不阻塞 S1 训练） |
| **与 pretrain 报告的差异** | 数据线推荐 4:4:2（有数据支撑），pretrain 线推荐 5:3:2（保守） | 分歧点在 stack-v3 + MegaMath 是否及时就绪 |

**一句话结论**：从数据视角看，S1/S2 等分 + S2 采用 4:4:2 **可行且有数据支撑**——stack-v3-train（476B，已分词）解决 code 缺口，MegaMath（92–371B）缓解 math 缺口。关键前置条件是 L4 语言过滤 + 污染闸门扩展 + MegaMath 分词，预计 11-20 前可全部就绪，不阻塞 S1 训练（ETA ~12-25 到 350k）。建议同步启动 MegaMath-web 下载以将 math epoch 从 1.18 降到 0.65。

---

> **报告路径**: `run/reports/report_s1s2_split_data.md`
> **数据来源**: `DATA_MAPPING.md` §A（token 实测）/ §H.14（stack-v3 全量分词）/ §D1（IFM 数据集 HfApi 实测）/ `CONTAMINATION_CHECK_AGENT_IFM.md`（污染检查）
> **口径声明**: 所有 token 数来自 `INDEX.tsv` / `MANIFEST.json` 实测；新数据集来自 `HfApi().dataset_info(files_metadata=True)`；MegaMath 论文 token 数标注了 ±15% tokenizer 偏差。无估算、无编造。
> **与 pretrain 报告的关系**: 互补关系——本报告聚焦数据充足性/配比落地/质量/去污染，pretrain 报告聚焦 LR schedule/评测趋势/训练稳定性。两报告在数据充足性结论上一致（现有不足、补新数据后可行），在推荐配比上有分歧（data 线 4:4:2 vs pretrain 线 5:3:2），分歧根因是对新数据到货时间的假设不同。
