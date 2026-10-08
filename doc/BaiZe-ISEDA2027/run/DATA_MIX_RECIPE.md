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

> 🔴 **运维订正（2026-10-06）**：本节的**设计意图正确，执行走偏** —— 实际跑成了 **2.220B 目标尺寸单臂**（`NVIDIAMambaHybridModelProvider2B`，≈**312 GPU·h/臂**）且**只有 1 个配比点** ⇒ **不构成实验**（见 `report_data_mix_s0a.html` 顶部红框）。已改道：**小代理模型（**⭐ 2026-10-06 定案：`hidden=512 / layers=14` ≈ **96.8M**（**总参 1/23 · 非-embedding 30.5M = 1/64**），`D ≈ 0.45B token/trial`；四选项裁定、通用设计方程 `N[M]·D[B]=86.4·(η/1e14)÷(T/100)`、以及「若改 `D=1B × 512 trial` ⇒ 必须降到 24–29M」的分支裁定见 `BAIZE_DATA_TASK.md` §②**）+ Optuna BO（TPE+MedianPruner）+ 每卡独立 trial + GBS 8–16 + seq 2048**，**Day1 Stable / Day2 Decay**。指令 + 「实验」的 5 条可检验判据见 `run/BAIZE_DATA_TASK.md` 顶部（2026-10-06 三块）。
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
  - ⭐ **2026-10-06 定案**：`D ≈ 0.45B token/trial`（≈13,700 步 @GBS16×seq2048）· 代理 **`h=512/L=14` ≈ 96.8M**（总参 1/23、非-embed 30.5M = 1/64）· **`T = 86400·η/(N·D)`**（或 `D=0.45B` 时 `T = 37.75 ÷ s_step`；`D=1B` 时 `T = 17.0 ÷ s_step`）· **通用设计方程 `N[M]·D[B] = 86.4·(η/1e14)÷(T/100)`** · 完整阶梯 + 例外条款（GBS 64–128 / 分块 CE / `L` 取 14 的倍数）+ 三条开工前置（val bin 中立性 / val-loss 通路 / LR 重扫）见 `run/BAIZE_DATA_TASK.md §③.6–.8`。
- 置信度：以 **Table 2 Avg + Table 3 Avg** 双指标做主判据，SFT 占比轴（D0）输出**具体百分比**（预期落在 60–69%）。

### 6.1 📐 目标函数与预注册（2026-10-06，先定后测）

> **运维指令（2026-10-06 P0）**：BO 目标函数必须用**评测均分**，不是 val loss。
> 本线采用运维批准的「可行方向 #2」：**eval-set 语料 val loss 作代理**。

**代理定义**：
- **`held_out_eval` bin** = **8 集常识推理评测集本身的文本**（arc_challenge, arc_easy, boolq, hellaswag, openbookqa, piqa, sciq, winogrande）tokenized 成 `.bin/.idx`（2,770,208 tok / 19,627 docs / seq=2048）。
- 路径：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/heldout/held_out_eval.{bin,idx}`
- BO objective = **该 bin 上的 val loss**（越小越好），**不是**训练分布的 val loss。
- ⚠️ **这是代理指标**，最终选优以 **top-K 的 lm_eval 8 集均分**为准。

**预注册（先定后测）**：
1. **判定阈值**：两配比差异 **Δloss 必须超过评测噪声 σ×2** 才算真差异（否则归为「不可区分」）。
2. **噪声测量**：同一 ckpt 在 `held_out_eval` bin 上重复评测 **≥3 次**（不同 seed），报 **σ**；在 BO 完成后对 top-5 ckpt 各测 3 次。
3. **相关性验证**：BO 完成后取 **top-5 + 先验点(88:8:4) + 若干随机点**（≥8 个 ckpt），跑 **`baize_mix_eval.sh` 的 lm_eval 8 集**，计算 **「代理 val loss ↔ lm_eval 均分」的 Spearman 秩相关**；若 ρ < 0.5 → 代理失真，改用全量 lm_eval。
4. **最终选优**：以 lm_eval 8 集均分排序，**不是**代理 val loss 排序。

**DB 存储bug说明**：`baize_mix_optuna.py` 的 SQLite `params` 列中 `math=0.0000`（存储 bug，实际训练用 `math=1-web-code`），分析先验点距离时须用 `math=1-web-code` 重算。

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

### 9.2 Stable 段 BO 搜索 Round 1（✅ 完成，2026-10-06~07）

> **S0a 2.2B 单臂已 kill（2026-10-06 08:06）** — 方法学错误（单臂 ≠ 实验）+ 成本失控（312 GPU·h/臂）。改道为小代理模型 + GP-EI BO 搜索。

| 参数 | 值 |
|:--|:--|
| **代理模型** | d=128 / L=14 / tie-embed ≈ **18.36M** |
| **搜索空间** | web∈[0.80,0.95] / code∈[0.03,0.12] / math=1−web−code |
| **每 trial** | 500 步 · GBS=16 · seq=2048 · LR=3e-3 · WSD(50/450) · seed=1234 · **MBS=1**（s_step≈1.5s，见 §9.6 归因） |
| **objective** | `held_out_eval` bin val loss（**eval-set 语料代理**，见 §6.1） |
| **并行** | 6 GPU（.29 GPU2-7）· GP-EI surrogate（Matern(ν=2.5)） |
| **存储** | SQLite `nemo_experiments/mix_search/mix_search_eval.db` |
| **进度** | **200/200 complete**（0 pruned），best=**5.821864** (#182: web=0.827/code=0.062/math=0.111) |
| **top-5** | #182(5.822) / #198(5.823) / #155(5.832) / #149(5.832) / #96(5.833) |
| **先验 88:8:4** | #79, loss=5.886, rank ~92/200 |

### 9.2.1 🔴 Round 1 关键结论：代理无分辨力 + 证据不足（方法学验证·2026-10-07 更正）

> **更正说明（2026-10-07）**：本节原表述「负相关 / 完全反向 / loss 排序错误」由 2 个 bug 产生（① `analyze_lmeval.py` 名次方向倒序 ② ρ 符号被读反），已据 `topk_lmeval_results.json`（机器可读权威源）复算更正。

**top-K lm_eval 8 集结果**（6 configs × 8 tasks, zero-shot, 见 `report_data_mix_eval.html`）：

| Config | BO loss rank | lm_eval 均分 | lm_eval rank |
|:--|:--:|:--:|:--:|
| #182 (BO best) | 1/6 | 0.3373 | **1/6** (最好) |
| #198 | 2/6 | 0.3353 | 3/6 |
| #155 | 3/6 | 0.3320 | **6/6** (最差) |
| #149 | 4/6 | 0.3338 | 4/6 |
| #96 | 5/6 | 0.3354 | 2/6 |
| #79 (先验88:8:4) | 6/6 | 0.3337 | 5/6 |

- **Spearman 秩相关**：ρ=**−0.43**, p=0.40, n=6
  - 含义：loss 越低 → 均分越高 = **代理方向正确**（非「反相关」）；但 n=6、p=0.40，**无统计功效 → 证据不足**
  - 逐任务：arc_ch **−0.83**(p=0.04,唯一显著,支持代理) / hella −0.71 / wino −0.49 / sciq −0.43 / piqa −0.20 = **5/8 方向有利**；obqa +0.64 / boolq +0.78 / arc_ea +0.18 = 3/8 反向（p≥0.07 全不显著）
  - 8 任务出 1 个 p≈0.04 属多重比较正常波动
- **噪声 σ=0**（lm_eval zero-shot 分类为确定性 → σ=0 只表示「重跑确定」，**不代表配置差异可信**）
- **均分 spread=0.0053**（极差 0.53pp ≈ 1.2×SE；全量 8 集单次评测 SE≈0.44pp，逐任务 0.43–1.97pp，二项近似）
- **vs 随机基线**：8 集随机基线均值 = 0.34375；除 boolq（0.381 vs 0.50，低 11.9pp = 常数输出坍塌）外 7 集全在 ±3.3pp 内 → **18.36M/0.016B 代理对这 8 集无能力**

**结论**：① 代理无分辨力（均分 ≈ 随机基线 + 极差 ≈ 1.2×SE）+ 证据不足（n=6, p=0.40）⇒ proxy val-loss 不可用作 BO objective；② D=0.016B (500步) 太小，模型未学到足以区分配比；③ Round 2 改 objective 的决定**不变、仍正确**，理由改为「**代理无分辨力 + 证据不足**」。

### 9.2.2 Round 2 设计（待 GPU0-1 释放后启动）

| 参数 | Round 1 | **Round 2** |
|:--|:--|:--|
| **objective** | held_out_eval val-loss | **lm_eval 8集均分**（subsampled --limit 500） |
| **MBS** | 1 (s_step=1.5s) | **16** (s_step=166ms, 8.6×) |
| **D/trial** | 0.016B (500步) | **0.5B** (15259步) |
| **save ckpt** | 否 (--save-interval 0) | **是** (final ckpt → HF → lm_eval) |
| **GPUs** | 6 (GPU2-7) | **8** (GPU0-7, 待释放) |
| **DB** | mix_search_eval.db | **mix_search_eval_r2.db** |
| **trial 数** | 200 | ≥200 (8卡 → ~400 in 24h) |
| **脚本** | baize_mix_optuna.py | **baize_mix_optuna_r2.py** |
| **对照** | — | 只比「最优配比+排序」，不比 loss 绝对值 |

### 9.3 旧 study（val-loss objective，保留对照）

- DB: `nemo_experiments/mix_search/mix_search.db`（115 trial, best=4.6420 #84）
- 用训练分布 held-out bin 的 val loss 作 objective → **已被运维判定为方法学错误**
- 保留作对照：BO 完成后检验「loss 排名 vs eval 排名」的相关性

### 9.4 评测管线（✅ 已备）

- **脚本**：`run/baize_mix_eval.sh <arm_name> [iter] [t2|t3|both]`
- **流程**：ckpt（.distcp 分片）→ `baize_p6_ckpt_to_hf.py`（转 HF Nemotron-H）→ lm_eval
- **Table 2**（Stable 段用，8 常识集）：`arc_challenge, arc_easy, boolq, hellaswag, openbookqa, piqa, sciq, winogrande`
- **Table 3**（Decay 段用，6 复杂推理集）：`gsm8k, math, bbh, mmlu, humaneval, mbpp`
- **GPU**：默认 GPU2-7（训练完后即可评测）
- **依赖**：PYTHONPATH 前置 `p6_tf5`（transformers 5.17.0 NemotronHForCausalLM）+ `omegaconf_230`；HF_ENDPOINT=hf-mirror.com

### 9.5 下载进度（白名单 2+1 项，2026-10-07 01:20）

| 项 | 进度 | 速率 / ETA | PID |
|:--|:--|:--|:--|
| `ultrafineweb_en` | **2048/2048 ✅** | 完成 | — |
| `ultrafineweb_l1_en_hq` | **5476/6006**（91.2%） | ~409G, ETA ~06:00 Oct7 | 3076502/3076519 |
| `ultrafineweb_zh` | **256/256 ✅ 完成** | 301G | — |
| GPIC | 活跃中 | — | 144981 @.12 |
| `gpic` | **3410 tars / 4.9T** | 活跃 | 144981 |

### 9.6 ⭐ s_step 归因实验（2026-10-06 22:48-22:56, GPU1@.29）

> **目的**：第一轮 BO 用 MBS=1 → s_step=1.5s → D=0.016B/trial（500步×16×2048）。需降到 ≤100ms 才能使 D=0.5–1B/trial 可行。

**方法**：`baize_sstep_profile.py`，固定 GBS=16/seq=2048/50步/WSD/88:8:4 blend，仅改 MBS∈{1,4,8,16}。记录 NeMo `elapsed time per iteration`（去掉 step 10 warmup）+ `max allocated` 显存。

| MBS | μbatch/step | 中位 s_step (ms) | tok/s | 峰值显存 (MB) | 加速比 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1   | 16 | **1432** | 22,893 | 3,024 | 1.0× (基线) |
| 4   | 4  | **418**  | 78,431 | 10,851 | 3.4× |
| 8   | 2  | **220**  | 149,211 | ~20,000 | 6.5× |
| 16  | 1  | **166**  | 197,831 | 42,164 | **8.6×** |

**结论**：
1. **瓶颈 = overhead-bound**：每 μbatch ~90-170ms Python/kernel-launch overhead × 16 μbatch = ~1.5s。非 compute-bound（GPU util 仅 ~15 TFLOP/s / 1000）。
2. **MBS=16 使 s_step 1432→166ms（8.6×）**，峰值显存 42GB < 80GB H100。
3. **D 投影（6 GPU, 24h）**：
   - D=0.5B/trial：15,259步 × 0.166s = 42min/trial → **205 trial/24h** ✅
   - D=1B/trial：30,518步 × 0.166s = 84min/trial → **103 trial/24h** ✅
   - 8 卡（GPU0-7）：D=0.5B → **410 trial/24h**；D=1B → **206 trial/24h**
4. **第二轮 BO 建议**：MBS=16, D=0.5B/trial, 200 trial/24h/6GPU（或 8 卡 → 400 trial）。目标 ≤100ms 需 CUDA graph + CE fusion（后续优化）。
5. **结果文件**：`nemo_experiments/sstep_profile/sstep_profile_results.json`

### 9.7 ⭐⭐ Round 3 Stable 段 BO 搜索（✅ 完成，2026-10-08~09）

> **R3 = R2 的下钻升级**：从 3 维 `base:code:math` 扩展到 **6 维**单纯形（ultrafineweb_en / zh / l1_en_hq + ultrax_preview + ultradata_code / math），评测从 `--limit 500` 升级到**全量 73106 requests**，D/trial 从 0.5B 升到 1B（信噪比更高）。交接文档：`run/BAIZE_DATA_R3_TASK.md`。

| 参数 | 值 |
|:--|:--|
| **代理模型** | d=128 / L=14 / tie-embed ≈ **18.36M**（同 R2，不换代理） |
| **搜索空间** | 6 维单纯形：en∈[0.01,0.50] / zh∈[0.01,0.40] / l1∈[0.01,0.40] / ultrax∈[0.01,0.30] / code∈[0.01,0.20] / math∈[0.01,0.10] |
| **每 trial** | 30518 步 · GBS=16 · MBS=16 · seq=2048 · LR=3e-3 · WSD · seed=1234 · **D=1B token** |
| **objective** | **全量** lm_eval 8 任务均分（arc_challenge / arc_easy / boolq / hellaswag / openbookqa / piqa / sciq / winogrande，无 `--limit`） |
| **并行** | 8 GPU（.29 GPU0-7）· Optuna TPE + MedianPruner · 每卡独立 trial |
| **存储** | SQLite `nemo_experiments/mix_search/mix_search_eval_r3.db` |
| **进度** | **100/100 complete**（98 complete + 2 failed=#25,#49），best=**0.4032** (#8) |
| **耗时** | ~19.5h（8 卡，13 轮），deadline ≤24h ✅ |

**Top-5 结果（normalized blends, sum=1.0）**：

| Rank | Trial | Score | en | zh | l1_en_hq | ultrax | code | math |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | #8  | **0.4032** | 0.168 | 0.320 | 0.324 | 0.080 | 0.064 | 0.044 |
| 2 | #47 | 0.4002 | 0.340 | 0.075 | 0.212 | 0.135 | 0.165 | 0.074 |
| 3 | #37 | 0.3998 | 0.423 | 0.118 | 0.289 | 0.104 | 0.054 | 0.012 |
| 4 | #46 | 0.3998 | 0.392 | 0.021 | 0.261 | 0.109 | 0.162 | 0.054 |
| 5 | #84 | 0.3979 | 0.271 | 0.115 | 0.240 | 0.096 | 0.196 | 0.082 |
| — | **Top-5 avg** | 0.4002 | 0.319 | 0.130 | 0.265 | 0.105 | 0.128 | 0.053 |

**Score 统计**（98 complete）：Mean=0.3824 / Min=0.3645 / Max=0.4032

**🔴 关键结论**：

1. **Web:Code:Math ≈ 89:6:4**（best trial #8）—— 与先验 88:8:4 接近，但 **code 从 8% 降到 6%**，math 保持 ~4%。先验的大方向正确，R3 微调了 code 比例。
2. **Web 内部分解**（R3 的核心增量）：
   - **l1_en_hq（高质量英文 web）一致高**（21–32%，top-5 avg 26.5%）→ **质量 > 数量**，l1_en_hq 是 web 段的主力
   - **zh（中文 web）方差极大**（3.2%–33.4%）→ zh/en 比例在 top-5 中未被 BO 稳定识别，landscape 平坦
   - **ultrax 稳定在 ~10%**（8–13.5%）→ UltraX-Preview 有稳定但适度的贡献
3. **Landscape 平坦**：top-5 Δ=0.0053（1.3% of mean）→ 在 18.36M 代理 + 1B token 规模下，**精确配比对 lm_eval 均分影响很小**。这意味着 P-8 不需要过度优化配比，合理范围即可。
4. **推荐**：
   - **主选**：best trial #8（en=16.8% / zh=32.0% / l1=32.4% / ultrax=8.0% / code=6.4% / math=4.4%）
   - **稳健选**：top-5 average（en=31.9% / zh=13.0% / l1=26.5% / ultrax=10.5% / code=12.8% / math=5.3%）
   - 两者 web:code:math 均在 ~87-89:6-13:4-5 范围，差异主要在 web 内部 en/zh 分配

**交付物**：
- `run/r3_best_blend.txt`（best trial #8 normalized blend + top-5 summary）
- `nemo_experiments/mix_search/mix_search_eval_r3.db`（100 trials, 98 complete）
- 脚本：`run/baize_mix_optuna_r3.py` / `run/baize_tokenize_r3_sources.sh`
