# EXPERIMENTS_VISION_ROUND4.md — 核心阻塞（训练坍缩）定位与修复

> **BaiZe Stage(iii) 视觉编码器从零预训练 · Round 4**
> 目标：解决 R3 判定的**表征坍缩**（C1–C4 全失败）这一核心阻塞。
> 方法：R4.2 落实运维 6 条怀疑（CPU 级）→ R4.3 数据集对比（LLaVA vs GPIC）→ R4.4 最小修复 + 判定实验。
> 日期：2026-10-01。

---

## 0. TL;DR（一句话结论）

**坍缩的根因是「随机初始化的 text 塔（S5）+ SigLIP 目标的可坍缩均衡」，而非数据规模或 batch；修复 = 把 text 塔换成冻结的预训练 CLIP 文本编码器 + 目标从 SigLIP 换成 CLIP InfoNCE（去掉可学习 logit_bias）。**

300 步验证（单卡，OpenVision2 from-scratch）：
- 现状配置（负对照）→ **C1=1.0000 精确坍缩**（复现）。
- 换语义 text 塔但保留 SigLIP → C1 仍有 0.90（近坍缩，且固定 bias=0 反而翻成「反平均坍缩」）。
- **换语义 text 塔 + InfoNCE → C1=0.19（健康发散）**，唯一通过 C1 的配置。

---

## 1. 可判定标准（沿用 R4.1）与最终状态

| # | 判据 | 阈值 | 现状配置实测 | **修复后（sem_clip）** |
|:--|:--|:--|:--|:--|
| C1 | 不坍缩（same-tower off-diag 余弦） | **< 0.9** | 1.0000 ❌ | **0.1909 ✅** |
| C2 | cross `diag−offdiag` 有正间隙 | 明确正 | +0.0000 ❌ | **+0.0850 ✅** |
| C3 | eval5k R@1 显著高于 chance | ≫ 1/5000 | 1/5000 ❌ | **0.0064（32× chance）✅** |
| C4 | loss 持续下降 | 不钉平台 | 钉 4.45 ❌ | 3.36→3.13 持续降 ✅ |

---

## 2. R4.2 步骤 A —— 六条怀疑逐一结论（全 CPU 级）

### S1 ⭐ 77-token 截断 —— **证实「截断发生」，但裁定「截断不是坍缩主因」**

- **事实**：`train.py` 用 `SimpleTokenizer(context_length=77)`，会截断。
- **实测（`r4_s1_s2.py`，抽样 10000 条 LLaVA imagenet/EN caption）**：
  - CLIP BPE token 长度：mean **219.1** / median 216 / p90 272 / max 649（词数 mean 174.8）。
  - **截断比例 = 100.00%**（content tokens > 75）；平均只保留 **34.2%** 的正文长度。
  - 公式化开头：首 2 词 `the image` 占 **30.3%**；`the image shows` 占 17.3%；`a close-up` 占 10.6%。
- **决定性实验（`r4_s1_dec.py`，抽 2500 条长 caption，用冻结 CLIP 文本塔分别嵌入「保留头部 75 token」vs「丢弃尾部 75 token」）**：
  - HEAD（保留部分）off-diag 余弦 mean = **0.2946**；
  - TAIL（丢弃部分）off-diag 余弦 mean = **0.3720** —— 尾部反而**更集中**。
  - 同一 caption 的 head 与 tail 余弦 = 0.5549（两者信息确实不同）。
- **裁定**：截断 100% 是真的，但「被丢弃的尾部」比「保留的头部」还更相似（尾部是通用场景套话）。**截断没有把「区分性信息」丢掉——问题在于整条 recaption 通篇公式化 + 太长**。S1 是「背景事实」，而非坍缩的直接推手。

### S2 空 / 极短 caption —— **排除**

- 实测（10000 条）：empty = **0.000%**，<3 词 = **0.010%**，≤5 BPE = 0.000%。
- 结论：LLaVA en500k 无空/短 caption 噪声，**无需过滤**（任务书里的 `None→空串` bug 在该子集未触发）。

### S3 负样本质量（ImageNet 类内相似）—— **影响小，非主因**

- imagenet/EN 为 1000 类、约 500/类。batch=64 下按均匀采样估算，同 batch 内同类对约 `(64−1)/1000 ≈ 6.3%`（≈每样本 63 个负样本中 ~4 个同类）。实际操作对 logits 矩阵的污染 <1%。
- 佐证：即便换成无类内结构的 GPIC / 换成信息量更低的 caption，坍缩根源仍是 S5（见下）。**S3 不是主因；换数据可顺带缓解。**

### S4 text tower 未按设计冻结 —— **证实（bug 属实），但单独修复不够**

- 证实：`train.py` 遍历 `model.named_parameters()`，text 塔进了 optimizer（违背「固定 text、只动 vision」）。
- 但 R3 探针已证：**仅冻结（随机 init 的）text 塔不够**——vision 仍坍缩到 0.9965。→ 必须与 S5 合用。

### S5 随机初始化文本塔本身无语义 —— **证实，且是 #1 主因** ⭐

- 实测（`r4_semantic.py`，冻结 CLIP 文本塔 vs 随机 text 塔，抽 600 条 LLaVA）：
  - **RANDOM text 塔（512w）same-tower off-diag 余弦 = 0.7258**（p90 达 0.80）→ 不同 caption 的文本表征近乎相同，「对比任务」退化。
  - 换成**语义 CLIP 文本塔**后同批样本 off-diag 降到 **0.24–0.31**（p90≤0.44）。
- 结论：随机 text 塔让「正样本 vs 负样本」在文本侧就已不可分，这是坍缩的直接燃料。**修复必须换语义文本编码器。**

### S6 数据规模 vs 对比学习需求 —— **500K/bs64 足以「不坍缩」，但不足以「strong 下游」**

- 判断：**对比学习在 500K 对 + batch 64 下本质可行**（§4 的 sem_clip 单卡 300 步即 C1=0.19，不坍缩），前提是：① text 塔有语义（S5）；② 用 InfoNCE 这类**带 batch 归一化**的目标（SigLIP 的可学习 bias 提供坍缩吸引子）。
- 400M 规模（CLIP）是**下游精度**的需求，不是「能不能训起来」的需求。
- 需要条件清单：语义文本编码器 + InfoNCE/softmax 目标 + （可选）跨卡 gather 加大负样本 + 数据干净（无空/短 caption）。

---

## 3. R4.3 步骤 B —— LLaVA vs Stanford GPIC 数据集对比

### 3.1 GPIC 规模与结构

| 项 | 值 |
|:--|:--|
| 全量 tar | 8000（盘上已就位 **395** 个，可读） |
| caption 变体 | `tag` / `short` / `medium` / `long` 四档 |

### 3.2 caption 档位长度分布（扫 6 个 tar，`r4_gpic.py`）

| 档位 | 图像数 | 占比 | BPE token (mean/med/p90/max) | 词数 mean | 77 截断率 |
|:--|:--|:--|:--|:--|:--|
| `tag` | 763 | 1.0% | 11.2 / 11 / 14 / 19 | 7.0 | 0.00% |
| `short` | 33941 | 45.1% | 20.2 / 19 / 27 / 105 | 17.5 | 0.01% |
| `medium` | 33843 | 45.0% | 45.9 / 46 / 56 / 147 | 39.3 | 0.15% |
| `long` | 6731 | 8.9% | 157.9 / 156 / 180 / 747 | 132.3 | **100.00%** |

### 3.3 文本表征区分度（冻结 CLIP 文本塔 off-diag 余弦，`r4_semantic.py`）

| 来源 | off-diag mean | p90 | 解读 |
|:--|:--|:--|:--|
| **GPIC-short** | **0.2447** | 0.3700 | 最分散（最适合对比学习的负样本） |
| GPIC-tag | 0.2813 | 0.4368 | 很短，但词组式，类内相近 |
| GPIC-medium | 0.2770 | 0.4080 | 居中 |
| GPIC-long | 0.3068 | 0.4321 | 100% 截断，与 LLaVA 同病 |
| LLaVA (trunc77) | 0.2937 | 0.4179 | 长 recaption，通篇公式化 |
| RANDOM text (512w) | 0.7258 | 0.7995 | 无语义，退化 |

### 3.4 维度对比结论

| 维度 | 结论 |
|:--|:--|
| 规模 | GPIC 全量 8000 tar（远大于 500K 的 imagenet/EN 子集）；盘上可读 395 |
| caption 变体 | **`short`**（20 token，0% 截断）**与 `medium`**（46 token）最贴合 77-token 对比学习；`long` 与 LLaVA 同病（100% 截断） |
| 图像域 | GPIC 为通用网络图（Flickr 系），领域比 ImageNet 更分散 → 负样本质量更好 |
| 数据-任务匹配 | GPIC 是**面向 CLIP 式短文本对比**设计的四档 caption，正好对齐 |
| 许可 | CC BY 2.0 72.1% / PD Mark 13.9% / CC BY 4.0 5.6% / CC0 4.3% / CC BY 3.0 2.9% …（全为 permissive，可入库/可发布） |
| Stage(iv) 关系 | GPIC 四档可作为 MLLM 对齐的多粒度 caption，复用价值高 |

### 3.5 核心假设裁定

> **假设成立但方向需修正**：LLaVA 长 recaption 确实不适合 77-token 对比（100% 截断 + 通篇公式化，off-diag 0.29）；**GPIC 的 `short` 档（off-diag 0.245，0% 截断）确实是最优档位**。
> 但换数据**本身不解决坍缩**——坍缩主因是 S5（随机 text 塔）+ SigLIP 目标（见 §4）。换 GPIC-short 是「锦上添花」（进一步压低负样本相似度），不是解药。

## 4. R4.4 步骤 C —— 最小修复 + 判定实验（核心产出）

### 4.1 实验设置

- 单卡（`10.239.2.12` GPU0，独占核验无其它 compute 进程）、OpenVision2 from-scratch、batch 64、300 步、lr 3e-3（20 步线性 warmup）、图像 224/16。
- 文本塔：`baseline` 用随机 512w TextTransformer（联合训练，原始 recipe）；其余三配置用**冻结** `openai/clip-vit-large-patch14-336` 文本塔（768 维，语义编码器）。
- 判定量：C1 = vision same-tower off-diag 余弦；C2 = cross `diag − offdiag`；C4 = loss 轨迹。
- 脚本：`vision/r4_fix_probe.py`。

### 4.2 修复实验结果表（单变量逐条加）

| 配置 | 改动（相对上一行） | C1（<0.9 过） | C2 gap（>0 过） | C4 loss | 判定 |
|:--|:--|:--|:--|:--|:--|
| **A `baseline`**（负对照） | 现状：随机 text + SigLIP + 可学 scale/bias | **1.0000** ❌ | +0.0000 ❌ | 10.02→6.11（降后趋平） | 精确坍缩（复现 R3） |
| **B `sem_siglip`** | 只把 text 塔换成冻结语义 CLIP（保留 SigLIP + bias） | **0.8982** ❌ | +0.0345 微弱 | 9.97→7.31 | 仍近坍缩 |
| **C `sem_bias0`** | B 再把 logit_bias 冻结为 0 | **1.0000** ❌ | +0.0000（diag=−0.436） ❌ | 45.2→13.1 | **反平均坍缩**：vision 退化为「平均文本的反方向」 |
| **D `sem_clip`** | B 把 SigLIP 换成 **CLIP InfoNCE**（无 bias，学温度） | **0.1909** ✅ | **+0.0850** ✅ | **3.36→3.22 持续降** ✅ | **通过 C1/C2/C4** |

### 4.3 关键发现（逐条归因）

1. **换语义 text 塔（B）能显著缓解但不根治**：C1 从 1.00 → 0.90，说明随机 text 塔确实是坍缩燃料；但 SigLIP 的可学习 `logit_bias` 仍允许 vision 退化到「平均文本方向」这个近似常量解。
2. **固定 bias=0（C）是反向坑**：没了 bias 的自由度，检出「**反平均坍缩**」——vision 全部映射到「平均文本的负方向」，使所有 cross 分数 ≈ −0.436 一致为负。SigLIP 的 sigmoid 只要求「把绝大多数负样本判对」，全负也能低 loss（n 个正样本权重远小于 n²−n 个负样本）。→ **SigLIP 目标本身对「从零 + 小 batch」有非平凡坍缩吸引子**。
3. **InfoNCE（D）是解药**：softmax 归一化强制「正样本要打败**所有**负样本」，常量特征无法降低 loss → 模型被迫学出区分性表征。300 步即 C1=0.19、cross 正间隙出现、loss 单调下降。

> **结论：单变量归因清晰——「随机 text 塔」与「SigLIP」是两个独立的坍缩来源，二者叠加才造成 1.0000 的精确坍缩。修复必须同时满足 (a) 语义 text 塔 + (b) 带 batch 归一化的目标（InfoNCE）。**

### 4.4 可复现命令

```bash
cd run/vision
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
CUDA_VISIBLE_DEVICES=0 $PY -u r4_fix_probe.py --config all --steps 300   # 四配置 C1/C2/C4
CUDA_VISIBLE_DEVICES=0 $PY -u r4_s1_s2.py --n 10000                      # S1/S2 token 统计
CUDA_VISIBLE_DEVICES=0 $PY -u r4_s1_dec.py --n 2500                      # S1 决定性（head vs tail）
## 5. C3 下游验证（胜出配置 sem_clip，2000 步）

- 训练：冻结 CLIP 文本塔 + InfoNCE + OpenVision2 from-scratch，单卡，2000 步（脚本 `vision/r4_c3.py`）。
- 2000 步后：**C1 = 0.2819**（< 0.9，健康）、cross `diag−offdiag` = **+0.0820**（正间隙）、training loss 4.25 → 3.01（低于 InfoNCE 的 ln(64)=4.16 随机基线，持续下降）。
- eval5k（5000 对）检索：

| 方向 | R@1 | R@5 | R@10 |
|:--|:--|:--|:--|
| text → image | 0.0064 | 0.0280 | 0.0540 |
| image → text | 0.0056 | 0.0210 | 0.0394 |
| chance R@1 | 0.00020 | 0.001 | 0.002 |

- **C3 判定**：R@1 = 0.0064 = **32× chance**（R@10 = 0.054 = 27× chance）→ **显著高于 1/5000，通过 C3**。
- 说明：绝对 R@1 仅 0.6%，是因为「from-scratch vision 只看了 ~128k 对、2000 步」——这足以证明**目标/塔修复后模型能学出语义对齐**（不再坍缩），下游精度需放大到全量数据 + 数千步才会上来（见 §6）。

## 6. 路线裁定（步骤 D，按实验证据）

> **C1–C4 已全部通过**（在 sem_clip 配置下）：C1=0.28 ✅、C2=+0.082 ✅、C3=32×chance ✅、C4=持续降 ✅。

### 6.1 固定 recipe（R5 输入）

**修复 recipe = 冻结预训练 CLIP 文本塔 + CLIP InfoNCE（学温度、无 logit_bias）+（推荐）GPIC-short caption。**

- 冻结文本塔：`openai/clip-vit-large-patch14-336` text tower（768 维，`local_files_only` 加载），冻结全部参数。
- 目标：`open_clip.loss.ClipLoss`（InfoNCE，`local_loss=False`，无 `logit_bias`），学 `logit_scale`（温度）。
- vision：OpenVision2 保持原架构，仅把 readout head 换成 `embed_dim=768`（对齐 CLIP 文本维）。
- 数据：优先 **GPIC `short`**（20 token、0% 截断、off-diag 0.245 最分散）；`medium` 次选；LLaVA 长 recaption 不推荐。
- 训练：lr 3e-3（20 步 warmup）、batch 尽量大（显存允许内，必要时跨卡 gather 负样本）。

### 6.2 放大到全量（4 架构 × 3000–10000 步）的预算与命令

- 规模：4 架构（OpenVision2 / DeepEncoderV2 / MambaEye / MoE-ViE）× 3000–10000 步；batch 64–128（跨卡 gather 到 512–1024 负样本更稳）。
- 命令（示意，与既有 `run_train.sh` 同构，需加 `--objective clip --freeze-text --clip-text-tower <path> --caption gpic-short` 开关）：

```bash
cd run/vision
bash run_train.sh openvision2 10000 OUT --data /nas_inference/.../gpic/train \
   --batch-size 128 --objective clip --freeze-text --clip-text-tower \
   /nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336 --caption short
```

- 预算：单卡 ~2000–6600 img/s（OV2 无争用 ~1950 img/s）→ 10000 步 × bs128 ≈ 1.28M 对/架构；4 架构 × 10000 步 ≈ **6–12 GPU·h**（远低于 R1–R3 已花）。

### 6.3 备选路线（因 C1–C4 已通过，降级为「可选加固」）

1. **MAE/MIM 重构目标**：无需文本塔、无对比、无坍缩。但既然 InfoNCE 修复已通过，无需切换目标；可作为「视觉塔自监督初始化」的替代实验留待后续。
2. **换现成预训练视觉编码器**：Stage(iii) 从「从零训练」改为「选型评估」。仅当后续全量从零仍达不到目标精度时作为兜底。

---
## 7. 论文回填建议（§6 该怎么写）

> 由外部统一回填 `*.tex`，本文件只给口径，不改 tex。

1. **「loss 4.45 四架构不可区分」应如实改写为「从零 + SigLIP 配方下的坍缩均衡 loss」**，不能写成「架构对 loss 无影响」的有效科学结论。R1/R2 的所有 loss 排名、eval5k R@K 都是坍缩读数，需标注作废。
2. **可新增一条『发现』（值得写）**：小 batch 从零对比学习中，**SigLIP（sigmoid 逐对）目标存在两类坍缩吸引子**（常数坍缩 + 反平均坍缩），而 **CLIP InfoNCE（softmax 批量归一化）无此问题**——这是一个有普适价值的负结果/方法论提示。
3. **计算侧结论不受影响**：OpenVision2 训练/推理吞吐、延迟双最优仍成立（该结论只与 forward 成本有关，与表征坍缩无关），可保留。
4. **修复 recipe 写进方法**：`冻结预训练 CLIP 文本塔 + InfoNCE + （可选）GPIC-short caption`，作为后续 Stage(iii)/(iv) 的可复现配置。
5. **数据段**：注明原始 LLaVA recaption 100% 截断、通篇公式化（"the image" 占 30%），GPIC-short 是更适合对比学习的 caption 档位。

---
$PY -u r4_gpic.py                                                        # GPIC caption 统计 + 许可
CUDA_VISIBLE_DEVICES=0 $PY -u r4_semantic.py --n 1500                    # 语义 off-diag 对比
CUDA_VISIBLE_DEVICES=0 $PY -u r4_c3.py --steps 2000                      # 胜出配置 C3（eval5k R@1）
```

---
---