# EXPERIMENTS_VISION_ROUND11.md — R11 目标函数（loss）轴：监督密度 vs 渐近上限

> 第十一轮：R9/R10 已证「瓶颈在数据量与目标函数（非架构）」。本轮**只变目标函数**，检验
> 「InfoNCE 每对只给 1 个全局标量（监督密度最低）→ 换成稠密监督（逐 patch/token）能否把 25.1% 渐近抬高」。
> **预注册**：判据先定后测，不许事后改。**控变量**：除目标函数外全部固定。

---

## 0. 定位与动机（一句话）

R9 幂律渐近 `acc=0.251−0.864·N^−0.090`（R²≈0.94）→ **25.1% 上限**是「从零 + InfoNCE」路线的如实渐近；
本轮的机制假说（⚠️ 须实测，不得当结论）：**InfoNCE 监督密度最低（1 个全局标量/对），数据越少越可能被稠密监督翻盘**。
→ 官方 AIMv2 / OpenVision2 都是**逐 patch / token 的稠密监督**。

> ⚠️ **更正（2026-10-03 · arm③ 启动时）**：原「臂③ LocalLoss = 负样本池 512→64」是**误述**。实测 `open_clip/loss.py`：`ClipLoss(local_loss=True)` 在 `gather_features`（`loss.py:56-63`）**仍 `all_gather` 全部 512 特征**，`get_logits`（`loss.py:116-121`）用 `image_features @ all_text_features.T` → **负样本池仍是 512**；它只把 loss 算在**本地 rank 的 64 行**（省显存/算），且因 gather 特征被 detach，本地图像**不再从 text→image 方向拿梯度**。→ arm③ 实为「local-行 vs global-行」的计算/梯度路径变体（预期≈基线，可验证损失实现不变性），**不是**「负样本池大小」消融。真正的池大小消融需另写不跨卡 gather 的损失。

---

## 1. ⚖️ 预注册判据（先定后测，不许改）

> 固定「同 N、同口径」：塔 w512（126.78M）· 数据 CC12M+Amshaker · 步数/样本预算 · 优化器 · 评测 IN-1k **frozen-trunk lp**（同 R9）。

- **基线**：InfoNCE（R9 阶段一 w512 = 6.08%@15.36M；阶段二 7.70%@51.2M，lp 渐近 25.1%）。
- **判据**：某臂同 N 下 **lp 比基线 > +1.5 点** → 「25.1% 是对比学习的渐近」**局部推翻** → 对该臂**重拟合 scaling 并外推**。
  - ≤ +1.5 点 → 维持「对比/稠密监督在本数据规模下不改变 25.1% 上限」。
  - ⚠️ 本线 pre-commit 口径：run variance 同 (N,M) 两 run 差 **0.5–1.1 pp**（R10 §1.5）→ +1.5 点阈值 > 噪声带上界，公平。
- **公平性铁律**：加 decoder/生成头的臂**必须报「参数量 + 训练 token + 每步耗时」**，不许只比 acc（见 §3 公平表）。

---

## 2. 臂定义（6 臂，按 R14 官方实现对齐；全部固定 w512 + 冻结 CLIP-768 文本塔 — 仅 arm ⑤⑥ 例外见备注）

> 现状代码：`r9_train.py` 用 `open_clip.loss.ClipLoss`（InfoNCE，`local_loss=False`）；`train.py` 另有 `SigLipLoss`（旧 S 系列栈，随机 text 塔，R4 用其在 ~0.5M 坍缩）。

| # | 臂 | 目标函数 | 实现来源 | 成本/风险 | 状态 |
|:--|:--|:--|:--|:--|:--|
| ① | **InfoNCE（基线）** | `open_clip.loss.ClipLoss(local_loss=False)` | 已有（R9/R10） | — | ✅ 已有 |
| ② | **SigLIP** | `open_clip.loss.SigLipLoss`（双向 sigmoid；`r9_train.py:162-165`） | R14 `sigmoid_xent`(OpenVision `losses/common.py:40`) 同源 | 低（改 1 处 loss + 保留冻结文本塔） | ✅ 完成（lp 2.19/3.13/4.36% < 基线，未翻盘） |
| ③ | **LocalLoss** | InfoNCE 的 `local_loss=True`（⚠️ **仍 all-gather → 负样本池仍是 512**；只把 loss 算在本地 64 行（省内存/算），且本地图像不再从 text→image 方向拿梯度（`open_clip/loss.py:56-63,116-121`）；`r9_train.py:166-168`） | `open_clip.loss.ClipLoss(local_loss=True)` | 低（改 1 参数；⚠️ **非「负样本池缩小」**，见 §0 更正） | ✅ 完成（lp 1.81/3.60/4.33% < 基线，未翻盘，见 §7） |
| ④ | **CoCa**（对比 + caption 生成） | 对比 + 自回归 caption CE（OpenVision `caption CE` + `coca_caption_loss_weight=2`） | 需**新写 caption decoder**（OpenVision2 权重 = concat/prefix-LM，**非 CoCa cross-attn**）；R14 可抄 Apache-2.0 的 caption CE 写法 | 高（新 decoder + 参数量/token 报备） | ⏸ |
| ⑤ | **GenLIP / AR（纯生成）** | caption-only 自回归（无对比项） | 需 caption decoder；⚠️ 我们 caption 偏短（CC12M=Amshaker alt-text 短句 / GPIC short=20 tok）→ 生成监督密度被短 caption 拖累（机制推断须实测） | 高 | ⏸ |
| ⑥ | **AIMv2 式（patch+text 双 AR）** | patch 预测 + text token 自回归（多模态 AR） | 官方 `ml-aim` 仅模型接口、**无 loss/训练代码 + Apple Sample Code 不可抄**；需自研 mask+双流 AR | 🔴 最贵；**条件触发**（臂②–⑤无翻盘迹象才做） | ⏸ |

- **执行顺序（成本递增）**：①（基线）→ ② SigLIP → ③ LocalLoss → ④ CoCa → ⑤ GenLIP → ⑥ AIMv2（条件）。
- **R11-L2 单独成题**（文本塔解冻 LoRA/Adapter vs 现状冻结），不在本表内，另测。

---

## 3. ⚖️ 公平表（加 decoder 的臂必填；无 decoder 臂与基线同参数量）

| 臂 | 参数量增量 | 每步额外 token | 每步耗时（相对基线） | 备注 |
|:--|:--|:--|:--|:--|
| ① InfoNCE | 0（基线） | 0 | 1.0× | w512=126.78M |
| ② SigLIP | +1（logit bias 标量） | 0 | ≈1.0× | 无 decoder |
| ③ LocalLoss | 0 | 0 | ≈1.0×（仍 all-gather，仅算本地 64 行 logits） | 同 512 负样本（非池缩小） |
| ④ CoCa | +decoder（≈参考 OpenVision2 `text_decoder w768·12L`） | +caption 自回归 | 待实测 | 须报 decoder 层数/宽度 |
| ⑤ GenLIP | +decoder（同上） | +caption 自回归 | 待实测 | — |
| ⑥ AIMv2 式 | +patch head + text AR | +patch/text token | 待实测（最贵） | — |

---

## 4. 协议（控变量，全部固定）

- 塔：OpenVision2 **w512（126.78M）**，depth30 / patch16 / 224²。
- 文本塔：冻结 `clip-vit-large-patch14-336` 768 维（context 77）（臂⑤⑥ 若需改动，须在下表报备并重跑 R4 坍缩判据 C1–C4）。
- 数据：CC12M ~11M + Amshaker ~6M（R9 同源，`r9_train.py --data` 同路径）。
- 优化器/schedule：AdamW、lr 3e-3、warmup 20、cosine、seed 1234、bf16、bs64×8=512。
- **样本预算（同 N 对照）**：主锚点 **N=15.36M（30k 步，= R9 阶段一）**；胜负臂延至 108k（55.3M）复证。
- 评测：IN-1k **frozen-trunk lp**（`r8_eval_in1k.py`，同 R9/R10）+ 坍缩探针 C1–C4（同 R4）。
- 证据纪律：每条结论贴命令 + 原始输出 + 路径。

---

## 5. 状态

- ✅ **臂 ② SigLIP 完成（2026-10-03 15:26，`ALL DONE`）**：`r9_train.py --loss siglip` 30k 步无坍缩（C1 0.333 / C2_gap +0.103 / C4=OK）；IN-1k lp **2.19 / 3.13 / 4.36%** @5.12/10.24/15.36M，全 < 基线（3.43/5.45/6.08%）→ **未超 +1.5 点阈值、未翻盘**。详见 §6。
- ✅ **臂 ③ LocalLoss 完成（2026-10-03 17:43，`ALL DONE`）**：`r9_train.py --loss localloss`（`ClipLoss(local_loss=True)`：⚠️ 仍 all-gather 512 → **负样本池仍是 512**，只算本地 64 行 logits，见 §0 更正）+ `r11_run_localloss.sh`（`R11L_localloss_w512`）。30k 步无坍缩；IN-1k lp **1.81 / 3.60 / 4.33%** @5.12/10.24/15.36M，全 < 基线（3.43/5.45/6.08%）→ **未超 +1.5 点阈值、未翻盘**。详见 §7。
- ⏸ **臂 ④ CoCa 决策（2026-10-03）**：见 §8（预注册 + 值不值得/成本 + 启动前核 GPU 空闲）。
- 每臂训练需 8 卡（`.12`），启动前先核 GPU 空闲（同 R10-③ 的 GPU 核验）。

---

## 6. 臂 ② SigLIP 结果（✅ 完成，2026-10-03）

> 命令：`cd run/vision && bash r11_run_siglip.sh 30000`（`r9_train.py --loss siglip`，8 卡 `.12`）；
> 证据：`/tmp/r11_siglip.log`，末行 `R11-L arm2 SigLIP ALL DONE 2026-10-03 15:26:20`（exit 0）。

- **训练健康（无坍缩）**：`[done] total=7050.6s steps=30000 steady_image_s=2447.7 final_loss=5.4643 fused=False`；
  末点探针 `C1=0.3333 C2_diag=0.0451 C2_off=-0.0579 C2_gap=+0.1030 loss_ema=5.4643 loss_early=8.2429 C4=OK`（判阈 C1≤0.95 / gap≤0.005 / C4）。
  可训 `logit_scale=41.17`、`logit_bias=−6.197`（init −10 → 收敛到小负偏置，正常）。
- **IN-1k frozen-trunk lp / zs**（`r8_eval_in1k.py --ckpts step{10k,20k,30k}+final`，与 R9/R10 同口径）：

| N | 步 | lp top-1 | zs top-1 | InfoNCE 基线 lp | Δ lp |
|:--|:--|--:|--:|--:|--:|
| 5.12M | 10k | **2.19%** | 0.95% | 3.43% | **−1.24** |
| 10.24M | 20k | **3.13%** | 1.45% | 5.45% | **−2.32** |
| 15.36M | 30k | **4.36%** | 1.95% | 6.08% | **−1.72** |

- **裁定（预注册 §1）**：同 N 同口径下，三档 N 的 Δ lp 全为**负**（−1.24 ~ −2.32 点），**无一超 +1.5 点阈值** →
  **「25.1% 是对比学习的渐近」未被 SigLIP 颠覆**；SigLIP（双向 sigmoid，512 负样本池）在本数据/塔/预算下**稳定劣于 InfoNCE**。
  注：loss 量纲不同（SigLIP 末 5.4643 vs InfoNCE 3.71）**不可跨目标比较**，主指标只看 IN-1k lp（同 R2-2 口径）。
- **公平性（§3）**：参数量 = 基线 +1（可训 `logit_bias` 标量，`r9_train.py:163-164`）；额外 token = 0；总墙 7050.6s ≈ 1.96h ≈ 基线 w512 30k（~1.98h）→ 每步耗时 **≈1.0×**。

---

## 7. 臂 ③ LocalLoss 结果（✅ 完成，2026-10-03）

> 命令：`cd run/vision && bash r11_run_localloss.sh 30000`（`r9_train.py --loss localloss`，8 卡 `.12`）；
> 证据：`/tmp/r11_localloss.log`，末行 `R11-L arm3 LocalLoss ALL DONE 2026-10-03 17:43:31`（exit 0）。

- **训练健康（无坍缩）**：`[done] total=7076.8s steps=30000 steady_image_s=2343.0 final_loss=4.4774 fused=False`；
  末点探针 `C1=0.2378 C2_diag=0.1026 C2_off=-0.0075 C2_gap=+0.1101 loss_ema=4.4774 loss_early=5.9065 C4=OK`（判阈 C1≤0.95 / gap≤0.005 / C4）。
  可训 `logit_scale=37.46`（`logit_bias` 无）。
- **IN-1k frozen-trunk lp / zs**（`r8_eval_in1k.py --ckpts step{10k,20k,30k}+final`，与 R9/R10 同口径）：

| N | 步 | lp top-1 | zs top-1 | InfoNCE 基线 lp | Δ lp |
|:--|:--|--:|--:|--:|--:|
| 5.12M | 10k | **1.81%** | 0.87% | 3.43% | **−1.62** |
| 10.24M | 20k | **3.60%** | 1.42% | 5.45% | **−1.85** |
| 15.36M | 30k | **4.33%** | 1.67% | 6.08% | **−1.75** |

- **裁定（预注册 §1）**：同 N 同口径下，三档 N 的 Δ lp 全为**负**（−1.62 ~ −1.85 点），**无一超 +1.5 点阈值** →
  **「25.1% 是对比学习的渐近」未被 LocalLoss 颠覆**；LocalLoss（仍 512 负样本 all-gather、仅算本地 64 行 logits）在本数据/塔/预算下**稳定劣于 InfoNCE（−1.6~−1.9 点）**。
- **科学意义（⚠️ 重要）**：arm③ 是「local-行 vs global-行」的**计算/梯度路径变体**，**监督密度仍是 1 个全局标量/对**（与基线同）→ 它**未检验「稠密监督翻盘」假说**，只证「损失对 local/global 行的实现选择基本不变（且 local 行略差）」。臂② SigLIP 同理（仍是 1 全局标量）。→ **假说「数据越少稠密监督越可能翻盘」迄今未被检验**，需臂④ CoCa（首个自带逐 token caption 监督的臂）才能开始测。
- **公平性（§3）**：参数量 = 基线 +0；额外 token = 0；总墙 7076.8s ≈ 1.97h ≈ 基线 w512 30k（~1.98h）→ 每步耗时 **≈1.0×**。

---

## 8. 臂 ④ CoCa 决策与预注册（2026-10-03）

> 臂② SigLIP / 臂③ LocalLoss 均**未翻盘**，且两者监督密度仍 = 1 全局标量（非稠密）。按预注册成本递增序，下一臂 = **④ CoCa（对比 + caption 自回归）**，是**首个带稠密（逐 token）监督**的臂 → 真正开始检验「数据少时稠密监督能否翻盘」。

- **值不值得**：✅ 值得。R11-L 的核心科学问题是「叠加逐 token 稠密监督能否抬高 25.1% 渐近」；CoCa（OpenVision 官方主目标之一，`coca_caption_loss_weight=2`，`openvision2.py:236`）是成本最低的稠密臂。⚠️ **已知 handicap**：我们 caption 偏短（CC12M alt-text / Amshaker 中长 / GPIC short=20 tok），caption 生成项的监督密度会被拖累（任务书 §5 数据侧硬约束，机制推断、须实测）。
- **成本**：需**新写 caption decoder**。R14 已查明 OpenVision2 官方 decoder = **concat/prefix-LM**（`text_decoder_v2`，`fusion_style='concat'`，vocab 32000，BERT-128 tokenizer），**非 CoCa cross-attn**（`VISION_OFFICIAL_REPOS_SURVEY.md §1`）；Apache-2.0 可参考写法（JAX→PyTorch 要改）。我们塔是 frozen CLIP-768（context 77，CLIP tokenizer）→ tokenizer/vocab 需另接（BERT/CLIP 待定），属**一次性重建、复用价值低**（R13 若要 load 官方 decoder 需官方 patch14/d24 结构，与本塔不同）。
- ⚖️ **公平性预注册（先定后测）**：decoder 参数量 / 额外 caption token / 每步耗时**必须实测并报在 §3 公平表**（不许只比 acc）。对照基线 = InfoNCE w512 同 N 同口径。
- **判据**：沿用 §1（同 N 同口径 lp 比基线 > +1.5 点才算翻盘）。
- **实施**：先在 `r9_train.py` 增加 `--loss coca` 分支（+caption decoder）；启动前核 `.12` 8 卡空闲（同 R10-③ 核验），跑 30k 步（N=15.36M 主锚点）。