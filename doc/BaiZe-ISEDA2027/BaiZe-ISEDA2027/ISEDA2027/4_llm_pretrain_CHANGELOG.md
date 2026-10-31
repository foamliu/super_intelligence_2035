# BaiZe-2B 论文「预训练」章节 · 长上下文训练修订 —— 改动位置一览

> 目标文件：`BaiZe-ISEDA2027/ISEDA2027/4_llm_pretrain.tex`（另改 `main.tex` 1 行、`reference.bib` 3 条）
> 编译验证：`pdflatex → bibtex → pdflatex ×2`，**0 error / 0 未定义引用 / 0 未定义引文 / 0 重复标签**，15 页。
> 改动定位的两种办法：① 本文档（逐条）；② `4_llm_pretrain_EDITS.txt`（9 条 `<!-- CHANGED -->` 标注原文）；
> ③ `4_llm_pretrain.tex.bak_annotated`（带内联标注的全文副本，便于 diff；正式稿已把标注全部移除，避免进编译产物）。

---

## 一、删掉的古旧内容（不符合现实，直接删）

| # | 位置 | 原内容 | 为何删除 |
|:--|:--|:--|:--|
| D1 | Full-Scale Production Training（旧 L202–221） | 「10,590 步 / ≈44.4B token / ≈412 GPU-hours／Chinchilla-optimal」的完整生产跑，含 stable loss 3.734→2.456、decay loss 1.914→1.357、`iter_0001149` | 该跑法与现行预训练（2.94T、16K/GBS256/CP1/DP16、WSD 两段 decay）完全不同，属旧实验；其数字新跑不具备，不能沿用 |
| D2 | 同上 | 生产配置 `GBS=1024, seq=4096, TP=1/DP=8, BF16` | 现行配置为 `seq=16384, GBS=256, CP=1/DP=16`, FP8 tensorwise |
| D3 | Throughput 段 | 「We therefore adopt BF16 for the production run」，并把 249,040 tok/s 当生产吞吐 | 与现行 FP8 + 613,992 tok/s 直接冲突 |
| D4 | Data | 「complementary corpora … **reserved for post-training**」；「production run 用 ≈2.66 TB / 6000 shard base corpus」；「packed to a sequence length of 4096」 | 现有 7 源 stable blend（含 L1/L2 高质层，code L2 占 0.15）已进预训练；主训练长度是 16K 不是 4K |
| D5 | Search 标题/首句 | 「Budget-Constrained Search Protocol」，把 S1–S5 搜索当作生产配方 | 搜索是前置代理实验；生产配方由 WSD 预算表定义 |
| D6 | Results 首句 | 「The **winning** configuration is …」（暗示搜索结论即最终配方） | 改为「搜索选出的配方被带入生产跑，只放大 token 预算与序列阶梯」 |

**保留未删**（仍有效，是论文证据基座）：架构选型对比（Tab. archcomp）、S1–S5 表（Tab. configs）与三种子方差、ABF 4K→1M 的 PPL 表（Tab. longctx-ppl）、长上下文推理成本表（Tab. longctx-cost）。这些只改表述定位，未改数值。

---

## 二、章节骨架（★ = 本次改动）

```
4  LLM Pretraining
   4.1  Architecture Selection Rationale                         未改
   4.2  Training Framework and Reduced-Horizon Search             未改
   4.3  Learning-Rate Schedule: WSD with a Two-Segment Decay   ★ 改写 + 新表 tab:wsd
   4.4  Search Protocol Preceding the Production Run           ★ 改写定位（S1–S5 保留）
   4.5  Data                                                   ★ 改写 + 新表 tab:stable-blend
   4.6  Long-Context Data Prerequisites                        ★ 全新 + 新表 tab:longctx-data
   4.7  Data Mixture Proportion Search                            未改
   4.8  Search Budget                                             未改
   4.9  Results of the Search                                  ★ 首句改写
   4.10 Full-Scale Production Training                         ★ 整节重写 + 新表 tab:prod-budget
   4.11 Long-Context Training: The Decay Tail of the WSD Schedule  ★★ 全新（本次主体）
   4.12 Long-Context Capability and Inference Cost                原有一节，未改
```

---

## 三、逐处改动清单

### 3.1 章节导语（L3–L5）
把「recipe」表述改为「WSD 的 decay 阶段含两个子段：短上下文退火段 + 长上下文扩展段」，并前向引用 4.11。

### 3.2 §4.3 学习率调度（L18–49）★
- 标题改为 **Learning-Rate Schedule: WSD with a Two-Segment Decay**。
- bullet 明确三段：① warmup+stable（700k 步 / 4.19M tok/step / 2.94T）；② decay-A 短上下文退火（60–70% decay 预算）；③ decay-B 长上下文扩展（30–40% decay 预算）。
- 写入 **16K 主训练长度的理由**（吞吐最优 613,992 tok/s；到 1M 只 64× 外推，而非 4K 的 256×）。
- 写入 decay 公式 $lr(p)=lr_{peak}(lr_{min}/lr_{peak})^{p}$，$p{=}0.25/0.5/0.75\to5.62/3.16/1.78\times10^{-4}$ —— 这正是 decay-B 所处的 LR。
- **新增 Tab. `tab:wsd`**：stable 2.94T、decay-A 58.7B、decay-B 25.2B、合计 3.02T / 720k 步。
- 修正 **`\ref{sec:results}` 悬空引用**（该 label 全篇不存在，已指向 `sec:llm-results`）。

### 3.3 §4.5 数据（L67–95）★
- 删 D4 三句，改为现行 **7 源 blend** + pre-blend 动机（每 rank 只开 O(10) 个 index 而非 O(600)，是吞吐前提）。
- **新增 Tab. `tab:stable-blend`**：7 源比例与 epochs（合计 1.000）。

### 3.4 §4.6 长上下文数据前置条件（L97–128）★全新
把「前置条件」落成 **章节 + 表 + 三条准入门槛**：
- 实测：≥32K 仅 **2.52%**、≥128K 仅 **0.03%**、平均文档 889 token（8 shard / 8.59B token / 9.66M 文档）。
- **Tab. `tab:longctx-data`**：实测 vs 目标（≥20% / ≥5%），结论「未达标」。
- 三条准入条件：(a) 补自然长文档至 ≥20%/≥5%，未达标则阶梯止于 64K；(b) **doc-level reset**（EOD 处重置注意力与 Mamba-2 状态），否则学到的是「跨文档拼接」的假长文；(c) 长文档去重。

### 3.5 §4.10 生产训练（L202–237）★整节重写
- 生产配置：`CP=1 / DP=16`（2×8 H100）、16,384 × GBS256 = 4.19M tok/step、FP8 tensorwise、**关 CUDA graph**、AdamW、EOD tokenizer。
- 实测现状：**iter 29,900 / 700k（4.3%）**、**≈590K tok/s**（7.08–7.32 s/step）、loss **2.166**、grad-norm 0.09–0.10、**0 NaN**、ckpt 每 2000 步。
- **新增 Tab. `tab:prod-budget`**：三阶段 token / 步数 / 墙钟（估算）/ 状态。
- decay-A 的配比，并说明「instruction data 在此仅当**文本**用，不是教 tool-call」（衔接 SFT 的一句话）。
- decay-B 指向 §4.11，并注明被 §4.6 数据闸门 gate 住。

### 3.6 §4.11 长上下文训练（本次主体，L240–349）★★全新
七个 `\paragraph`，逐条对应用户要求：

1. **Positioning（阶段定位）**：明确是 decay 的组成部分（后半段），不是独立阶段；三条理由 —— LR 已低（分布切换破坏最小）／SFT 只教指令遵循、RL 只优化偏好，均不承担基础检索能力建立／长上下文必须在 post-training 之前建成。**Tab. `tab:llm-stages`** 把 A/B 段画在训练轴上。
2. **Data budget**：decay = 主训练 **10–15%**（294–441B）；长上下文占 decay **30–40%**（88–176B）；阶梯 **40/30/20–30%** 分给 32K/64K/128K；参考点取 12%（353B）→ 42.4/31.8/21.2B。**Tab. `tab:longctx-budget`** 给出 10/12/15% 三档全表（含 16K 保护量）。
3. **Composition**：合成 needle 占长上下文 **20–40%**，覆盖单针 NIAH / 多针 MK-NIAH（全中才算对）/ 多跳 VT / 变长针 / 改写+噪声；**禁止纯合成**；自然侧 40% 书籍论文 + 20% 仓库级代码 + 其余标准法规文档；深度 0–100% 均匀。
4. **Training configuration**：32K→64K→128K 阶梯，CP 2/4/8，DP 8/4/2，每级 tok/GPU 恒 16,384；**LR 沿 decay 末端、不回升**；**ABF θ=1e6 从头即生效**、128K 由训练达成、1M 只 8× 外推；**不启 PI/NTK/YaRN**；**doc-level reset 强制**。**Tab. `tab:longctx-train`**：三级 rung 的 seq/CP/DP/GBS/token/吞吐（32K 实测 351,526；64K/128K 标 est.）。
5. **Evaluation checkpoint**：WSD 全部结束后一次快照 —— CS8/CX（退化 ≤1pp）、passkey+RULER（1M ≥95%）、PPL 外推（1M/4K ≤1.10×）、基础格式遵循；复杂推理与 agentic **只记基线**，提升留给 SFT/RL（一句话衔接）。**Tab. `tab:longctx-eval`**。
6. **Cost**：参考轮 ≈118 GPU·h（其中 32K 轮 33 h），上界 ≈220 GPU·h；32K 吞吐为 16K 的 59%。
7. **Why the budget is this small**：引 ICML 2024 数据工程研究（128K 只需 0.5–5B token）、ProLong、LongRoPE2（10–40B 量级）；并说明 2.2B 小模型需求量不高于 8B 级，故 35B 量级已充裕。

### 3.7 §Throughput / Precision（L404–414）★改写
- 保留 249,040 tok/s 作为 **单机 4K/BF16 参照**，新增 16K/FP8 的 613,992 tok/s 与实跑 ≈590K tok/s，并写入「关 CUDA graph 是满速前提」。
- 把「生产用 BF16」改为 **per-configuration 决策**：4K 屏（FP8 tile M=8192 < 交叉点 M*≈30–32K）选 BF16；16K（M=16,384）选 FP8。**明确声明同形状 BF16 未实测**，不虚构对比数。

### 3.8 其他文件
- `main.tex`：+`\usepackage{tabularx}`（1 行；原文件已定义 `Y` 列型却未 load 该宏包）。
- `reference.bib`：新增 `chen2024dataeng`、`gao2024prolong`、`shang2025longrope2` 三条。**`chen2024dataeng` 的作者/venue 请在投稿前核对**（bib 的 note 内已标注）。

---

## 四、数字来源对照（实测 vs 估算）

| 数字 | 值 | 来源 | 论文中的标注 |
|:--|:--|:--|:--|
| stable 总 token | 2.94T | `configs/s1.env`：700,000 × 4,194,304 | 配置口径 |
| decay 参考量 | 58.7B + 25.2B = 83.9B | `configs/decay.env`：20,000 × 4,194,304 | 配置口径 |
| 总 token | 3.02T | 2.94T + 83.9B | 配置口径 |
| 实跑吞吐 | ≈590K tok/s | S1 实跑 7.08–7.32 s/step（`MEMORY_PRETRAIN_2B` #993） | 实测 |
| 16K 峰值吞吐 | 613,992 tok/s | 双机 16 卡实测 #792 E1 | 实测 |
| 32K rung 吞吐 | 351,526 tok/s | 实测 #792 E3 | 实测 |
| 64K / 128K 吞吐 | ≈180K / ≈90K | 按 per-GPU 线性缩放外推 | 估算（表内 est.） |
| 当前 iter / loss | 29,900 / 2.166 | `MEMORY_PRETRAIN_2B` #993 | 实测 |
| ≥32K / ≥128K 占比 | 2.52% / 0.03% | `check_longctx_data.py`，en_v1_4，8 shard | 实测 |
| 平均文档长度 | 889 token | 同上 | 实测 |
| decay 10–15%、LC 30–40% | 294–441B、88–176B | 用户指定 + 2.94T 换算 | 估算 |
| 阶梯 token 分配 | 42/32/32B | 12% × 30% × 12:9:6 | 估算 |
| 墙钟 / GPU·h | ≈56 d；≈118 / ≈220 GPU·h | 按实测吞吐折算 | 估算（表内 est.） |
| CS8/CX ≤1pp、1M ≥95%、PPL ≤1.10× | 门槛 | 用户指定（沿用 10-26 长上下文方案口径） | 门槛，非实测 |

---

## 五、仍待补的实测（论文中已如实标为待测/估算）

1. **decay-B 未开跑**：受 §4.6 数据闸门阻塞（长文档占比未达标）。
2. **64K / 128K 吞吐未实测**：表内标 est.，正式跑完须回填。
3. **同形状 BF16 vs FP8**：只有 4K 屏（M=8192）与 M=65,536 的 A/B；**16K（M=16,384）两种精度的直接对比未做**，正文已声明。
4. **WSD 结束后的能力快照**：全部 gate 均待测。
5. **decay-A 的 loss 曲线**：开跑后补入 §4.10。

---

## 六、编译复核

```bash
cd BaiZe-ISEDA2027
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
grep -c '^!' main.log                                     # 0
grep 'LaTeX Warning: \(Reference\|Citation\)' main.log    # 空
grep 'Overfull \\hbox' main.log                           # 仅 2 条，均在 6_vision_encoder.tex（本次未动）
```

> 注：`BaiZe-ISEDA2027/` 自 2026-10-28 后无提交，本次改动**尚未 commit**（按要求仅交付修订稿）。
> 若要入库，建议 message：
> `BaiZe paper: 预训练章节改写——删除 44.4B 旧生产跑，新增 WSD decay 两段制与长上下文训练（32K→128K 阶梯 + ABF 1M）`
