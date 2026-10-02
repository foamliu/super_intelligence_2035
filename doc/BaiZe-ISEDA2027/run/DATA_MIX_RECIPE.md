# DATA_MIX_RECIPE.md — P-8 数据配方（WSD 双阶段，follow MiniCPM5 / Xmodel-2）

> 本文件 = `BAIZE_DATA_TASK.md` §0.6 的交付物。**当前主攻：为 Stage (i) 的 P-8 训练定"用什么数据、什么配比"。**
> 依据：本地 `doc/BaiZe-ISEDA2027/Xmodel-2/xmodel-2.tex`（下文引行号）＋ MiniCPM5 公开材料。
> 状态：**方案定稿（含具体百分比 + 实验设计 + 数据就绪清单）**；配比**实验**尚无 GPU（.29 排队中，见 §6）。
> 更新：2026-10-02。

---

## 0. 一句话结论（先给答案）

1. **P-8 用 WSD 两段各配一套比，不是全程单一比**：Stable 段以 **web 主体（base + UltraX-Preview）**为主，Decay 段把 **SFT 数据压到 ~64%**（Xmodel-2 实测最优 60–69%）。
2. **"decay 段 = 带 SFT 数据的退火"**，SFT 不是事后单独做一遍 —— 这直接模糊 Stage (i)/(ii) 的边界，是 P-8 配方的核心含义（见 §2）。
3. 百分比**不是拍的**：按 Xmodel-2 结论，**小模型上的配比实验可迁移到大模型**（`ye2024datamixinglawsoptimizing`），所以用 **8 卡短跑（≤5000 步）** 跑 ~24–40 组配比做代理指标（Table 2 常识 8 集 + Table 3 复杂推理 6 集），把两段各轴收敛到具体数字。

---

## 1. 运维假设的核实结论（§0.6 A）

**结论：MiniCPM5 未公开逐源百分比 → "未找到"，采纳运维表格为「待验证工作假设」**（§0.6 明确允许此路径）。

| 项 | 查证结果 |
|:--|:--|
| MiniCPM5 **模型卡**（`openbmb/MiniCPM5` HF） | 未公开 stable/decay 逐源占比（只列数据源清单，见 `DATA_RESEARCH.md` R2-D） |
| MiniCPM5 技术报告 / `openbmb/MiniCPM5` collection 各 dataset card | 未公开逐源百分比 |
| arXiv 2602.09003《Tiered Data Management》全文 | 平台/流程，未给逐源配比 |
| **Xmodel-2**（本地 `xmodel-2.tex`） | ✅ **公开了 decay 段配比搜索结论**（§3）；stable 段给了数据**构成**（CC_Chn / FineWeb-Edu / Dolma / Code），未给百分比 |

→ 采纳运维下表作为工作假设，并**由 §6 的配比实验来证实/修正**。

**`UltraX-Preview` 与 `Ultra-FineWeb`(base) 的关系（§0.6 A.2）**：上轮 R2 已查明 UltraX 里有一支叫 `UltraX-Ultra-FineWeb`，`UltraX-Preview` 是 MiniCPM5 相对前代**新增的 web 源**；与 base 的 `ultrafineweb_en` **同族但不完全同集**（UltraX 是精筛/重配后的 web 子集，规模待核实，见 `DATA_RESEARCH.md` R2-D）。二者**大概率部分重叠**，是否作为独立投料、占多少，属 Stable 段待实验搜索的一个轴（§6 轴 S1）。

---

## 2. 🔴 关键含义：decay 段即"带 SFT 的退火"

Xmodel-2 原文（`xmodel-2.tex:138,144-146,152-154`）：

- Decay 用指数退火 `f(s-T)=0.5^{(s-S)/T}`，`T=5000 步（20B token）`。
- Decay 段"**把预训练数据与高质量 SFT 数据混合**"；配比搜索收敛为两问：**① SFT 总体占比；② SFT 内部类别分布**。
- **400+ 次试验 → 最优 SFT 占比 60%–69%，实际取 64%**；SFT-Mixed 由 **5 类构成：Mathematics / Code / Logic / Knowledge / Commonsense（CoT 归入 Logic）**；数学与代码的**指令格式 > 预训练格式**；SimHash 去重（bucket 1M）**+1.7%**；整体复杂推理 **+29.31%**。

**含义**：`SFT-2605` / `SFT-Agent-2609` 是**喂进预训练 decay 段**的，而不是等 model 训完再独立 SFT。这与运维给的 decay 假设（含 SFT-2605 + SFT-Agent-2609）**一致**，也与 MiniCPM 路线一致 → **Stage (i) 的 decay 段本身就在做"带 SFT 的退火"**。

---
## 3. Stable 段 + Decay 段：工作假设配比表

> 单位 = **该段内占比**。两段的 token 切分见 §5。

| 段 | 源 | 工作假设占比 | 备注 |
|:--|:--|:--|:--|
| **Stable（S）** | `Ultra-FineWeb (base)` + `UltraX-Preview`（web 主体） | **~88%** | 现阶段 web 主体；base 与 UltraX 各自占比 = 待实验轴 S1 |
| | `UltraData-Code` | **~8%** | StarCoder/The Stack 同级 |
| | `UltraData-Math` | **~4%** | 预训练格式数学 |
| **Decay（D）** | `UltraData-SFT-2605` + `UltraData-SFT-Agent-2609`（SFT-Mixed） | **~64%** | Xmodel-2 最优 60–69%，取 64% |
| | `Ultra-FineWeb-L3`（web）+ `UltraData-Code` + `UltraData-Math`（预训练格式） | **~36%** | L3:~24% / Code:~8% / Math:~4%（待实验） |

**SFT-Mixed 内部 5 类分布（Decay 段的第二问，待实验）**：Mathematics / Code / Logic / Knowledge / Commonsense（`think` 类 CoT 数据归 Logic）。初始均分 20%×5 起步，按 Table 3 的 6 集实测调度。

---

## 4. 代理指标（两套，实测后用）

| 段 | 指标套 | 来源（xmodel-2.tex） | lm_eval 任务 |
|:--|:--|:--|:--|
| **Stable / 常识** | Table 2（8 个 + Avg） | `:198,207` | `arc_challenge` `arc_easy` `boolq` `hellaswag` `openbookqa` `piqa` `sciq` `winogrande` |
| **Decay / 复杂推理** | Table 3（6 个 + Avg） | `:73,253,260` | `gsm8k`(5-shot) `math`(4-shot) `bbh`(3-shot) `mmlu`(0-shot) `humaneval`(pass@1) `mbpp`(pass@1) |

> 口径：全部走 **lm_eval**（P-6 已把 `ckpt→HF→lm_eval 8 集` 打通，见 `MEMORY_PRETRAIN_2B.md`；Table 3 的 6 个 lm_eval **原生支持**，HumanEval/MBPP 开代码执行开关即可，**无需另起 bigcode-harness**——见 `BAIZE_PRETRAIN_2B_TASK.md` §P-7 口径澄清）。

---

## 5. P-8 token 切分（100B 基准，另给 44B / 200B）

| 预算 | Stable（S） | Decay（D） |
|:--|:--|:--|
| **100B（推荐）** | ~80B | ~20B |
| **44B（下限）** | ~36B | ~8B |
| **200B（上限）** | ~160B | ~40B |

> Decay 的 `T` 在 Xmodel-2 = 20B token；100B 预算下正好取 20B；44B/200B 按 ~20% 同比缩放。

---

## 6. ⭐⭐ 配比实验设计（§0.6 B，无需全量 2.2B）

**原理**：`xmodel-2.tex:142` 引 `ye2024datamixinglawsoptimizing` —— 小模型上的配比实验可迁移到大模型 → **短地平线、小/同规模短跑即可**。

**搜索轴**（照 Xmodel-2 思路，收敛到少数几问）：

| 轴 | 内容 | 候选 |
|:--|:--|:--|
| **S0（Stable 主体构成）** | web:Code:Math 三点消融 | 88:8:4（基线，Round 1 已得出）→ ±2% 微调 |
| **S1（Stable web 内部）** | base vs UltraX-Preview 占比 | 仅 base / 仅 UltraX / 50:50 / 70:30（4 点） |
| **D0（Decay SFT 占比，最关键）** | SFT 总量 | 55% / 60% / **64%** / 69% / 72%（5 点，Xmodel-2 说 60–69 最优） |
| **D1（Decay SFT 内部 5 类）** | Math/Code/Logic/Knowledge/Commonsense | 均匀 20%×5 起步 + 3 组重点扰动 |

**实验规格**：8 卡（`.29`，LLM 的卡，串行 P-4R → 配比 → P-5b 之前）、**5000 步短地平线（或更短）**、每组跑完跑 §4 两套指标。
- 试验次数：**~24–40 组**（远少于 Xmodel-2 的 400+，靠小模型+数据混合定律压缩）。
- 成本估算：每组 ~5000 步 × GBS；以 Round 1/2 的 2.2B 8 卡吞吐（~85–90K tok/s 混合）计，**每组 ≈ 0.5–1 GPU·h×8 ≈ 可批跑**，整轮 ~1–2 天排队窗口内可完成（.29 串行由运维排）。
- 置信度：以 **Table 2 Avg + Table 3 Avg** 双指标做主判据，SFT 占比轴（D0）输出**具体百分比**（预期落在 60–69%）。

---

## 7. P-8 数据就绪清单（§0.6 C.2，截至 2026-10-02）

| 源 | 是否就位 | 状态 / 缺口 |
|:--|:--|:--|
| `Ultra-FineWeb (base)` | 🟡 下载中 | en 配置 **1787/2048**（复用旧 1286 续推，0 .incomplete），剩 ~261 en + en_v1_4 + zh + l1_en_hq |
| `UltraX-Preview` | ❌ 未下 | 规模/重叠待实测（§1） |
| `Ultra-FineWeb-L3` | ✅ 就绪 | 1764 parquet / 617.6 GiB（4 config） |
| `UltraData-Code` | ✅ 就绪 | 1121 parquet |
| `UltraData-Math` | ✅ 就绪 | 1823 parquet |
| `UltraData-SFT-2605` | ✅ 就绪 | **1504/1504 jsonl = 318,990,252,711 B，与 HF 官方清单逐字节一致（0 .incomplete）** |
| `UltraData-SFT-Agent-2609` | ✅ 就绪 | 50 shard jsonl / 51 GiB |

---

## 8. 可复现命令 / 下一步

- **下载**（正在跑，见 `MEMORY_DATA.md` 快照）：
  - base（en 配置，复用 1286）：`hf download --repo-type dataset openbmb/Ultra-FineWeb --include 'data/ultrafineweb_en/*' --local-dir /nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb`
  - SFT-2605：`hf download --repo-type dataset openbmb/UltraData-SFT-2605 --local-dir /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605 --token <HF_TOKEN>`
- **配比实验**（.29 上，脚本待 base 落地后由 phase2 复用 `preprocess_data.py` 切 `.bin/.idx` 各配比，再短跑）—— 出方案后报运维排期。
- **污染闸**：base / SFT-2605 落地后一律过 `check_contamination.py`（EDA-Eval 158 任务红线）再投料。

> 🚫 全篇未涉及任何"领域化"（EDA/领域语料）—— 遵循运维 10 月硬规矩，领域化一律留白。