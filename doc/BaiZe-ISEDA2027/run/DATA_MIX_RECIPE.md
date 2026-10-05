# DATA_MIX_RECIPE.md — P-8 数据配方（WSD 双阶段，follow MiniCPM5 / Xmodel-2）

> 本文件 = `BAIZE_DATA_TASK.md` §0.6 的交付物。**当前主攻：为 Stage (i) 的 P-8 训练定"用什么数据、什么配比"。**
> 依据：本地 `doc/BaiZe-ISEDA2027/Xmodel-2/xmodel-2.tex`（下文引行号）＋ MiniCPM5 公开材料。
> 状态：**方案定稿 + Stable S0a 臂 🚀 运行中（step60/5000, ETA~Oct7 20:00）**。
> 更新：2026-10-05 16:05（唤醒 132）。

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

> 🔴 **运维订正（2026-10-06）**：本节数值是 **未验证先验（占位）**，**不是实验结论**，也**不是「最优」**。它们将由 **§6 的 Optuna BO study 作为候选点之一被检验**（指令与 5 条可检验判据见 `run/BAIZE_DATA_TASK.md` 顶部 2026-10-06 两块）。

> 单位 = **该段内占比**。两段的 token 切分见 §5。

| 段 | 源 | 未验证先验占比（待 BO 检验，非结论） | 备注 |
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

> 🔴 **运维订正（2026-10-06）**：本节的**设计意图正确，执行走偏** —— 实际跑成了 **2.220B 目标尺寸单臂**（`NVIDIAMambaHybridModelProvider2B`，≈**312 GPU·h/臂**）且**只有 1 个配比点** ⇒ **不构成实验**（见 `report_data_mix_s0a.html` 顶部红框）。已改道：**小代理模型（~50–150M，按「24h 跑 200–400 trial」反推规模）+ Optuna BO（TPE+MedianPruner）+ 每卡独立 trial + GBS 8–16 + seq 2048**，**Day1 Stable / Day2 Decay**。指令 + 「实验」的 5 条可检验判据见 `run/BAIZE_DATA_TASK.md` 顶部（2026-10-06 两块）。
> ⚠️ 本节文内 **`88:8:4` 与 **SFT 60–69%（64%）** 一律是 **未验证先验锚点，不是答案**；模型尺寸口径以 `NVIDIAMambaHybridModelProvider2B` = **2.220B** 为唯一准据（旧文「2.47B / 3B」的写法一并作废）。

**原理**：`xmodel-2.tex:142` 引 `ye2024datamixinglawsoptimizing` —— 小模型上的配比实验可迁移到大模型 → **短地平线、小/同规模短跑即可**。

**搜索轴**（照 Xmodel-2 思路，收敛到少数几问）：

| 轴 | 内容 | 候选 |
|:--|:--|:--|
| **S0（Stable 主体构成）** | web:Code:Math（单纯形采样） | **未验证先验锚点 88:8:4**（Round 1 经验值，**作为候选点被 BO 检验，非答案**）；连续域 `web∈[0.80,0.95] / code∈[0.03,0.12] / math=1−web−code` |
| **S1（Stable web 内部）** | base vs UltraX-Preview 占比 | 仅 base / 仅 UltraX / 50:50 / 70:30（4 点） |
| **D0（Decay SFT 占比，最关键）** | SFT 总量 | **未验证先验锚点** 55% / 60% / **64%** / 69% / 72%（Xmodel-2 的 60–69% 是**文献值不是答案**；**由 BO 在 `SFT∈[0.40,0.80]` 连续搜索**） |
| **D1（Decay SFT 内部 5 类）** | Math/Code/Logic/Knowledge/Commonsense | 均匀 20%×5 起步 + 3 组重点扰动 |

**实验规格（2026-10-06 订正版）**：**`.29` GPU2–7（6 卡）· 每卡独立 trial（TP1/DP1、各自 `master_port`、6 并行）** · **GBS 8–16** · **seq 2048** · **Optuna TPE + MedianPruner** · **Day1 Stable / Day2 Decay** · 跑完对 **top-K（K≥3）** 跑 §4 两套指标。
- 试验次数：**≥ 200 trial / 段 / 天**（**硬指标**；对齐 Xmodel-2 的 400+ 次试验——其真义是**很多次试验**，不是「一次大模型跑」）。
- 成本估算（**订正**）：原估算「每组 0.5–1 GPU·h×8」**实测偏 ~50×**（S0a 实测 ≈**312 GPU·h/臂**）。新方案硬算：**6 卡 × 24h = 144 GPU·h/天 ÷ 200–400 trial = 0.36–0.72 GPU·h/trial**（单 trial 22–43 min）；**两天总计 ≈288 GPU·h 出两段配方** —— 这正是 S0a 一条无效臂的成本量级。
- 🔢 标定公式（先测 1 卡再定规模）：`N_trial/天 ≈ 6×86400 ÷ (步数 × s/step)`，即要求 **`步数 × s/step ≤ 1728 s`**（=300 trial/天）；**跑不到 200 trial → 缩小模型**（先减层数、再减 hidden），**不许延长时间**；反之**预算富余就调大模型**（更大代理 = 更好迁移性）。
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

---

## 9. 🚀 实验执行状态（2026-10-05 16:05，唤醒 132）

### 9.1 数据就绪状态（实测）

| 源 | 分词状态 | 路径 | token 数 | 备注 |
|:--|:--|:--|--:|:--|
| `Ultra-FineWeb (base)` en | ✅ 4 shard 完成 | `data/mix_base/mix_base_train_s{0..3}` | **22.05B** | s0=5.51B / s1=5.52B / s2=5.51B / s3=5.51B |
| `UltraData-Code` (anneal) | ✅ 已有 | `data/anneal_code.bin` | ~180M | pretrain Round 1 产出 |
| `UltraData-Math` (anneal) | ✅ 已有 | `data/anneal_math2.bin` | ~860M | pretrain Round 1 产出 |
| `UltraData-SFT-2605` shard s2 | ✅ 完成 | `data/mix_sft_tok/mix_sft_train_s2` | **3.58B** | 4.85M docs |
| `UltraData-SFT-2605` shard s3 | ✅ 完成 | `data/mix_sft_tok/mix_sft_train_s3` | **521M** | 1.40M docs |
| `UltraData-SFT-2605` shard s0 | 🟡 进行中 | `data/mix_sft_tok/mix_sft_train_s0` | ~?B（.bin 28G） | no_think_Math 13.2G 源, PID 2013637, 3.7h |
| `UltraData-SFT-2605` shard s1 | 🟡 进行中 | `data/mix_sft_tok/mix_sft_train_s1` | ~?B（.bin 12G） | clean restart, PID 2868155, 1.5h |
| `UltraData-SFT-Agent-2609` | ❌ 未分词 | `/nas_inference/.../UltraData-SFT-Agent-2609/` | ~?B | 50 shard jsonl / 51 GiB，待 s0/s1 完后启动 |

### 9.2 Stable 段 S0a 臂（基线，🚀 运行中）

| 参数 | 值 |
|:--|:--|
| **配比** | base:code:math = **88:8:4**（4 base shards × 22 = 88, code 8, math 4） |
| **GBS** | 1020（6×170，基线 1024 因 DP6 整除要求调为 1020，-0.4%） |
| **口径** | 6 卡 · TP1/DP6 · seq=4094 · mb=1 · 5000 步 · bf16_mixed · seed=1234 · WSD(warmup=250, decay=0=纯 stable) |
| **GPU** | .29 GPU2-7（CUDA_VISIBLE_DEVICES=2,3,4,5,6,7） |
| **PID** | 1995742 (bash) / 1995914 (torchrun) / 1998724-738 (6 workers) |
| **脚本** | `run/baize_mix_stable_s0a.sh` |
| **SAVE_INTERVAL** | 5000（仅在末尾存 ckpt，无中间 ckpt） |
| **当前进度** | step 60/5000, loss 10.84→7.16（step10→60，稳定下降） |
| **速率** | ~37.8 s/iter（warmup 后稳定，358 TFLOP/s/GPU） |
| **ETA** | (5000-60) × 37.8s ≈ **51.9 小时 → ~Oct 7 20:00** |
| **ckpt 路径** | `nemo_experiments/mix_stable_s0a/checkpoints/iter_0005000/`（训练完后产出） |

### 9.3 ⚠️⚠️ ETA 重大更正（运维请注意）

**原 §6 估算**（2026-10-02）："每组 ~5000 步 × GBS；以 Round 1/2 的 2.2B 8 卡吞吐（~85–90K tok/s 混合）计，每组 ≈ 0.5–1 GPU·h×8 ≈ 可批跑，整轮 ~1–2 天"

**实际**（2026-10-05 实测）：
- 6 卡（非 8 卡），3B mamba2-hybrid 模型
- GBS=1020 × seq=4094 = **4.18M tok/step**
- 5000 步 = **~20.9B tokens**
- 实测吞吐 ~112K tok/s（6 卡合计）
- **每臂 = 6 GPU × 52h = 312 GPU·h**（比估算大 **~50×**）

**影响**：按 12+ 臂计 → **总耗 ~24+ 天**，远超"1–2 天"估算。

**建议**（不改 S0a，已运行不 kill）：
- **方案 A**：保持 S0a 为完整 5000 步基线；**后续臂降至 1000–2000 步**（~10–21h/臂）。任务书明确允许"5000 步短地平线（**或更短**，但所有臂必须一致）"——若后续臂缩短，S0a 也可在 step1000/2000 时另存 ckpt 评测对比（需改 SAVE_INTERVAL，但 S0a 已在跑无法改）。
- **方案 B**：所有臂均 5000 步，接受 ~24 天总耗。优先跑最关键的 D0 轴（SFT 占比 55/60/64/69/72%，5 臂 × 52h = ~11 天）。
- **方案 C**：kill S0a，重启所有臂为 1000 步（~10h/臂，12 臂 = ~5 天）。代价 = 已跑 60 步（~38 min）的浪费。

### 9.4 评测管线（✅ 已备）

- **脚本**：`run/baize_mix_eval.sh <arm_name> [iter] [t2|t3|both]`
- **流程**：ckpt（.distcp 分片）→ `baize_p6_ckpt_to_hf.py`（转 HF Nemotron-H）→ lm_eval
- **Table 2**（Stable 段用，8 常识集）：`arc_challenge, arc_easy, boolq, hellaswag, openbookqa, piqa, sciq, winogrande`
- **Table 3**（Decay 段用，6 复杂推理集）：`gsm8k, math, bbh, mmlu, humaneval, mbpp`
- **GPU**：默认 GPU2-7（训练完后即可评测）
- **依赖**：PYTHONPATH 前置 `p6_tf5`（transformers 5.17.0 NemotronHForCausalLM）+ `omegaconf_230`；HF_ENDPOINT=hf-mirror.com

### 9.5 下载进度（白名单 4 项）

| 项 | 进度 | 速率 / ETA | PID |
|:--|:--|:--|:--|
| `ultrafineweb_en` | **2048/2048 ✅** | 完成 | — |
| `ultrafineweb_l1_en_hq` | **2795/6006**（46.5%） | ~0.8 MB/s, ETA ~15 天 | 3076502/3076519 |
| `ultrafineweb_zh` | **171/256**（冻结） | 低优先级，等 l1_en_hq 完 | 3076502 |
| `gpic` | **3410 tars / 4.9T** | 活跃 | 144981 |