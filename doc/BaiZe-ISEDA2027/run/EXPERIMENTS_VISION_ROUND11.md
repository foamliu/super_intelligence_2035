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
| ④ | **CoCa**（对比 + caption 生成） | 对比 + 自回归 caption CE（OpenVision `caption CE` + `coca_caption_loss_weight=2`） | 需**新写 caption decoder**（OpenVision2 权重 = concat/prefix-LM，**非 CoCa cross-attn**）；R14 可抄 Apache-2.0 的 caption CE 写法 | 高（新 decoder + 参数量/token 报备） | ✅ 完成（lp 0.29/0.37/0.47%≈随机、Δ −3.1~−5.6 点、未翻盘，见 §9） |
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
| ④ CoCa | **+76.2M 可训**（decoder w768·12H·4L + LM head 49408；总 114.1M 含冻结 CLIP token_embed 37.9M 不更新） | +caption 自回归（≈24–40 tok/样本×bs512，逐 token masked CE） | **≈0.97×**（实跑 6911.7s ≈1.92h vs 基线 ~1.98h；steady 3487 img/s 反而略高于基线，因数据加载提速） | depth=4/w768/h12，vocab=CLIP 49408，caption_weight=2.0 |
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
- ✅ **臂 ④ CoCa 完成（2026-10-03 20:13，`ALL DONE`）**：+76.2M decoder + caption CE（weight 2.0）30k 步无强制融合、但 IN-1k frozen-trunk lp **0.29 / 0.37 / 0.47%** @5.12/10.24/15.36M（≈随机 1/1000）→ **Δ −3.14 / −5.08 / −5.61 点，未翻盘且把 trunk 打回随机**（total loss 里 caption 项 ≈68% 梯度、盖过对比项）。**首个稠密监督臂 = 负结果** → 「25.1%=对比渐近」未被颠覆、反被强化。详见 §9。
- ✅ **R11-L2 文本塔解冻臂 完成（2026-10-04 02:12，运维已批准）**：`r9_train.py --loss clip --text-finetune lora`（CLIP-768 文本塔 LoRA q+v r=8 α=16 lr=1e-4），30k 步（N=15.36M），冻塔(w512)/数据/步数/优化器/评测全固定、只变「文本塔是否解冻」。**未坍缩 + IN-1k lp 3.13/4.75/5.28% < 基线 6.08%@15.36M → 未翻盘**（Δ −0.30~−0.80）。详见 §11.7。
- 📌 **后续臂（运维已裁定 2026-10-03（三））**：臂⑤ GenLIP **🚫 跳过** → 替代 = `caption-loss-weight` 三点消融（✅ 已完成 2026-10-04，见 §12.5）；臂⑥ AIMv2 ⏸ 暂缓（等 R11-L2 结果——现已出、仍未翻盘）；R13 ⏸ 批准后只做 OV2 单臂；R11-E ⏸ 等 GPIC short ≥18.5M。
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
- **✅ 实现完成（2026-10-03）**：`models.py` 增 `CoCaDecoder`（causal self-attn + cross-attn→patch，共享冻结 CLIP token embedding vocab 49408）+ `OpenVision2.forward(return_patch=True)` patch 路径；`r9_train.py` 增 `tokenize_cap()`、`coca_caption_loss()`、`--loss coca`、`--caption-loss-weight`(default 2.0)、`--decoder-depth`(default 4)。decoder 实测 `trainable=76.2M / total=114.1M`（w768·12H·4L + LM head 37.9M + 冻结 token_embed 37.9M）。
- **✅ smoke 通过（exit 0）**：`bash r11_run_coca.sh 30` → 8 卡 DDP 全链路 OK；`[decoder] depth=4 dim=768 heads=12 trainable=76.2M total=114.1M vocab=49408 caption_weight=2.0`；`[step 30/30] loss=18.6150 contrast=6.1165 caption=6.2493 scale=10.182 image/s=2337.9`；`[done] total=8.6s ... fused=False`。ckpt 字段核验：`vision`(277 keys) / `decoder_params=76166400` / `loss=coca` / `objective=CoCa`。
- ✅ **正文 smoke 已清理，正式 30k 已启动（2026-10-03 ~18:05，.12 全 8 卡，hostname=whag0pgpuap12 核验）**：`cd run/vision && bash r11_run_coca.sh 30000` → `R11L_coca_w512`，30k 步（N=15.36M 主锚点）。启动打印 `[start] steps=30000 objective=CoCa shards=419/rank`；日志 `/tmp/r11_coca.log`；稳态吞吐 smoke≈2267 img/s。**正式结果见 §9**。
---

## 9. 臂 ④ CoCa 结果（✅ 完成，2026-10-03）

> 命令：`cd run/vision && bash r11_run_coca.sh 30000`（`r9_train.py --loss coca --caption-loss-weight 2.0 --decoder-depth 4`，8 卡 `.12`）；
> 证据：`/tmp/r11_coca.log`，末行 `R11-L arm4 CoCa ALL DONE 2026-10-03 20:13:06`（exit 0）。
> decoder：`[decoder] depth=4 dim=768 heads=12 trainable=76.2M total=114.1M vocab=49408 caption_weight=2.0`。

- **训练健康（探针名义通过，但图文对齐已明显弱化）**：`[done] total=6911.7s steps=30000 steady_image_s=3486.8 final_loss=17.4016 fused=False`（全程未触发强制融合）。
  末点探针 `C1=0.3390 C2_diag=0.0892 C2_off=+0.0213 C2_gap=+0.0679 loss_ema=17.4016 loss_early=22.5549 C4=OK`。
  ⚠️ 但看**趋势与数值**：`C2_gap` 从 @300 的 **+0.0924** 单调下滑到 @30000 的 **+0.0679**；`C2_diag` 仅 **~0.08–0.09**、`C2_off=+0.02` 为**正**——对照 arm② SigLIP（diag 0.045 / off **−0.058** / gap +0.103）与 arm③ LocalLoss（diag 0.103 / off **−0.0075** / gap +0.110），CoCa 的对齐**远弱**。即探针阈值（C2 gap>0.005）很松、判「无坍缩」，但对比对齐实际已**几近随机**（diag 0.089 vs 随机≈0）。
- **IN-1k frozen-trunk lp / zs**（`r8_eval_in1k.py --ckpts step{10k,20k,30k}+final`，与 R9/R10 同口径）：

| N | 步 | lp top-1 | zs top-1 | InfoNCE 基线 lp | Δ lp |
|:--|:--|--:|--:|--:|--:|
| 5.12M | 10k | **0.29%** | 0.40% | 3.43% | **−3.14** |
| 10.24M | 20k | **0.37%** | 0.41% | 5.45% | **−5.08** |
| 15.36M | 30k | **0.47%** | 0.53% | 6.08% | **−5.61** |

- **裁定（预注册 §1）**：三档 N 的 Δ lp 全为**大幅负**（−3.14 ~ −5.61 点，lp 已≈随机 1/1000=0.1%），**无一超 +1.5 点阈值** →
  **「25.1% 是对比学习的渐近」未被 CoCa 颠覆，反而被强化**：首个稠密监督臂（caption 逐 token CE）不仅没翻盘，还把 frozen-trunk lp 打回随机。**已测目标中 InfoNCE 仍最优**。
- **机制解读（⚠️ 推断，须实测，不得当结论引用）**：total loss = contrast（≈5.43）+ **2.0×caption（≈5.86）** ≈ 17.15 → **caption 项占 ~68% 梯度**。我们 caption 偏短（CC12M alt-text 短句 / Amshaker 中长，任务书 §5 数据侧硬约束），caption CE 是「监督容量被短 caption 封顶、且与 IN-1k 分类正交性弱」的稠密信号 → 在 weight=2.0 下**压过对比项、洗掉全局可分类特征**；C2 探针仍名义通过只因此对比项仍在跑、但已弱到 diag≈0.09。故「数据越少稠密监督越可能翻盘」在本臂**不成立且方向相反**。
- ⚠️ **限定（铁律，不得过度推广）**：本结果为「**我们自写** CoCa cross-attn decoder + 冻结 CLIP-768 文本塔 + 短 caption + caption_weight=2.0 单点（未消融）」下成立；🚫 **不得**推出「官方 CoCa / OpenVision2 caption 训练会坍缩」——官方 = concat/prefix-LM + BERT-128 + LLaMA-3 ReCap 长合成 caption（`VISION_OFFICIAL_REPOS_SURVEY.md §1`）。weight 消融（0.5/1.0）未做。
- **公平性（§3）**：decoder **+76.2M 可训**（总 114.1M）+ caption 逐 token CE（`max_length=77`，实际短 caption，**未逐 token 计数**，口径同 §5）；总墙 **6911.7s ≈ 1.92h vs 基线 ~1.98h → ≈0.97×**（无实质开销，steady 3487 img/s 反略高因数据加载提速）。
- **对后续臂的影响（决策建议，待运维裁决）**：
  ① 臂⑤ GenLIP（纯 caption 生成、无对比项）= 去掉唯一仍在工作的对比项的臂④ → **坍缩先验更强、边际价值低**；建议**跳过**，或降级为「caption_weight 消融（0.5/1.0/2.0）」替代（成本更低、信息更准）。
  ② 臂⑥ AIMv2 式 patch 预测 = **唯一不依赖 caption 丰富度的稠密监督**（任务书 §5），是「稠密监督能否翻盘」的**决定性检验**；但「最贵 + 需自研 mask/双流 AR（Apple Sample Code 不可抄）」→ 建议**先交书面值不值/成本判断、运维批准后再起**（同 R13 口径）。
  ③ 备选更高杠杆轴：**R11-L2（文本塔解冻 LoRA/Adapter）**——冻结 CLIP-768 把上限锁死在外来静态文本空间，可能才是真天花板；比继续踩「caption 稠密」更值得试。

---

## 10. 后续抉择 · 书面成本/收益判断（2026-10-03 · **待运维拍板**）

> R11-L 已跑的 4 臂（①基线 / ②SigLIP / ③LocalLoss / ④CoCa）**全部兑现、无一翻盘**（④ CoCa 为首个稠密臂且为负结果）。
> 剩余选择都需要「烧 GPU + 自研改动」，故**先交书面值不值 / 成本判断**（铁律：🚫 未经运维批准**不得起训练**）。
> 成本单位 ≈ **1 个 30k 步 w512 训练 ≈ 1.9–2.0h × 8 卡 ≈ 16 GPU·h**（臂②③④ 实测 total 7050.6s / 7076.8s / 6911.7s）。

### 10.1 臂⑤ GenLIP（纯 caption 自回归）—— 🚫 建议跳过

- **是什么**：去掉对比项、只留 caption 自回归生成（= 臂④ 去掉唯一仍在工作对比项的版本）。
- **值不值**：⚠️ 不值。臂④ CoCa（对比 + caption）已实证：caption 项占 **~68% 梯度**，在 weight=2.0 + 短 caption 下把 frozen-trunk lp **打回随机（0.47%）**。臂⑤ = 连对比项也去掉 → **坍缩先验更强、几乎必然更差**。
- **成本**：实现现成（复用 `CoCaDecoder` / `--loss coca`，对比项权重置 0），≈ 1 臂训练。
- **更便宜的替代**（信息更准）：把 `--caption-loss-weight` 做 **0.5 / 1.0 / 2.0 三点消融**，可直接回答「是 caption 监督本身与 IN-1k 正交、还是 weight=2.0 压死 trunk」，成本 ≈ 0.5–1 臂。
- **建议**：**跳过臂⑤**，或以 caption_weight 消融替代。

### 10.2 臂⑥ AIMv2 式（patch 预测 + text 双流 AR）—— ⏸ 条件触发，建议暂缓

- **是什么**：唯一**不依赖 caption 丰富度**的稠密监督（任务书 §5），是「稠密监督翻盘」假说的**决定性**臂。
- **值不值**：**科学价值最高，但成本最高、可抄性最低**。
  - R14 已核：`ml-aim`（AIMv2）仓库**只有模型接口、无 loss/训练代码**，LICENSE = **Apple Sample Code（不可抄）**（`VISION_OFFICIAL_REPOS_SURVEY.md §2`）→ mask + 双流 AR **需纯自研**。
  - 官方参照（README）：AIMv2-L 0.3B = 87.6% frozen-trunk / 77.0% LiT zero-shot，量级比我们 7.99% 高 ~10×，但那是「自监督 patch 预测 + 数十亿对 + 0.3B 网」叠加；**单扒 patch 项能否在 15.36M 规模翻身无先验**。
- **成本**：自研 mask 策略 + patch 解码头 + 双流 AR 训练循环 + 调参 ≈ **3–5 臂 GPU + 1–2 天自研**，**一次做成概率低**。
- **建议**：**暂缓**；等 R11-L2（文本塔解冻，成本更低、可能才是真天花板）先出结果再决定是否启用这条最贵的路。

### 10.3 R11-L2 文本塔解冻（LoRA/Adapter vs 冻结）—— ✅ 建议下一优先级

- **是什么**：R4 因「随机 text 塔坍缩」而冻结 CLIP-768，但**冻结 = 上限锁死在外来静态文本空间**（任务书 R11-L2 节）。
- **值不值**：✅ 值得、且可能是当前**最高杠杆**。R9/R10 已把数据轴、塔宽轴都证到头（更小塔更优、加宽负收益）；R11-L 又把稠密监督证为负/无效；剩下能动的最大旋钮 = **文本塔是否解冻**。
- **臂**：冻结（现状基线）vs **LoRA/Adapter 轻量微调** vs 重训 text 塔（最贵）。⚠️ 必须**重跑 R4 坍缩判据 C1–C4**（防重蹈「随机 text 塔坍缩」）。
- **成本**：LoRA/Adapter 臂 ≈ **1–2 臂 GPU**（text 塔独立可插 LoRA、改动小）；重训臂 ≈ 3+ 臂。
- **建议**：**先做 LoRA/Adapter 臂**（成本低、风险小）；若 C1–C4 不坍缩且 lp 走高，再决定是否升级到重训。

### 10.4 R13 官方实现 vs 自研改编对照 —— ✅ 已批准并完成（2026-10-04）：官方 OV2 L/14@224 IN-1k frozen-trunk lp=79.81% vs 自研 7.99% → 补结论边界「上限低是因数据少、非塔烂」（见 `EXPERIMENTS_VISION.md` 顶部 R13 单列表）。书面判断如下

- **是什么**：R8 六架构全是**自研 from-scratch 等参改编**（C2 限定），「SSM 坍缩」等结论**只对我们 recipe 成立**。R13 = 加载**官方权重/官方结构塔**做 IN-1k 对照，回答「前沿架构（官方协议）在我们场景行不行」。⚠️ 协议不同（官方预训练 vs 我们从零）→ **单列一张表、不并入排名**。
- **值不值**：✅ 有价值但**优先级低于 R11-L2**（补「结论边界」而非「抬上限」）——确认「上限低是因数据少、不是因我们塔写得烂」。
- **可做对象（R14 已核）**：
  - **OpenVision2 权重**（Apache-2.0，✅ 含 caption decoder）：但官方 = **patch14/d24**，我们 = **patch16/d30**（`models.py:170`）→ **需另建官方结构塔才能 load**。
  - **MoE-ViE**（CC BY-NC 4.0 **非商用**）：官方权重 HF `facebook/MoEViE-*`，但 IN-1k 已 79–85%（预训练好的大模型），与我们 7.99% 不可比，只能当「官方好好训时的上限」参照。
  - **MambaEye**（MIT）：官方 = 小模型（5.8–21.3M）**监督分类**、非对比 → 协议完全不同，只能证「SSM 在监督分类下不坍缩」。
  - **FastVLM / AIMv2**：Apple Sample Code（research-only）→ ⚠️ 只可作一次性私有参照，不可进拟开源仓库。
- **成本**：建 1–2 个官方结构塔 + 权重转换 + IN-1k 评测（不训或只 lp）≈ **0.5–1 臂 GPU + ~半天塔结构重建**。
- **建议**：**批准后只做「OpenVision2 官方权重 + p14/d24 塔」单臂对照**（信息最对位、Apache-2.0 干净）；MoE-ViE 可选；其余因 LICENSE/协议差异价值低。

### 10.5 R11-E GPIC 数据轴 —— ⏸ 已具备触发条件、但仍受数据下载限制

- **是什么**：固定塔/loss/评测，只把数据臂换成 GPIC `short`，与 CC12M+Amshaker 同 N 对照，回答「GPIC 是否把上限抬高」。
- **现状（E1 实测）**：GPIC `short` 已下 **≈6.8M 唯一对**（< R9 的 18.5M），**可比 N 区间被压到 ≈6.8M**；数据仍在下载（全量 short ≈45M）。
- **值不值**：✅ 有价值（数据轴是三大瓶颈之一），但**当前可比区间太窄、结论说服力弱**。
- **建议**：**等 GPIC short ≥18.5M 再跑**（届时可比区间对齐 R9），或先跑一个 **6.8M 同 N 试点**若想早看信号（成本 ≈ 1 臂）。

### 10.6 汇总建议（给运维的一句话）

| 项 | 建议 | 成本 | 理由（一句话） |
|:--|:--|:--|:--|
| 臂⑤ GenLIP | 🚫 跳过（或以 caption_weight 消融替代） | 0 | 臂④ 已证 caption 项压死 trunk |
| 臂⑥ AIMv2 | ⏸ 暂缓 | 3–5 臂 + 自研 | 最贵 + 无官方代码可抄 + 一次成概率低 |
| **R11-L2 文本塔解冻** | ✅ **下一优先级** | 1–2 臂 | 冻结文本塔才是真天花板、最高杠杆 |
| R13 官方对照 | ⏸ 批准后只做 OV2 单臂 | 0.5–1 臂 | 补结论边界、不抬上限 |
| R11-E GPIC 数据轴 | ⏸ 等 short ≥18.5M（或先 6.8M 试点） | 1 臂 | 数据仍在下载、当前区间太窄 |

> ⚠️ **本表为书面判断**：**R11-L2 已获运维批准并启动**（见 §11）；臂⑥ / R13 / R11-E **仍未经批准、不主动起训练**；等运维在任务书 §3 队列 + 上表勾选后再执行。

---

## 11. R11-L2 文本塔解冻臂（LoRA vs 冻结）· 预注册 + 进行中（2026-10-03）

> **批准依据**：§10.3 已把 R11-L2 列为「✅ 建议下一优先级」（当前最高杠杆）；运维已批准立即执行（本臂无需再等拍板）。
> **预注册原则（铁律）**：判据先定后测——以下 C1–C4 坍缩判据与「翻盘」阈值在拿到评测结果前**冻结不变**。

### 11.1 臂定义（控变量：**只变「文本塔是否解冻」**）

| 控制变量 | 值（与基线臂① / R9 阶段一 **完全一致**） |
|:--|:--|
| 视觉塔 | OpenVision2 **w512（126.78M）**，depth30 / patch16 / 224² |
| 数据 | CC12M + Amshaker ≈18.5M 对（同 glob、`--data` 同路径） |
| 步数 / 样本预算 | **30k 步 = N 15.36M**（= R9 阶段一主锚点） |
| 优化器 / schedule | AdamW(0.9, 0.95, eps 1e-6)；视觉 lr 3e-3、warmup 20、cosine；seed 1234；bf16；bs64×8=512 |
| 目标函数 | InfoNCE（`--loss clip`，512 负样本池）—— 与基线臂①**同目标** |
| 评测 | IN-1k **frozen-trunk lp**（`r8_eval_in1k.py`，step{10k,20k,30k}+final）+ 坍缩探针 C1–C4 |
| **唯一变化** | **文本塔：冻结 CLIP-768（基线） vs LoRA 轻量微调（本臂）** |

### 11.2 LoRA 配置（文本塔 = `openai/clip-vit-large-patch14-336` 的 `text_model`）

- **注入位置**：12 个 BERT encoder 层的 `self_attn` 的 **q_proj + v_proj**（各 Linear 768×768、无 bias）。预训练权重**原地冻结**，仅 `lora_A/lora_B` 可训。
- **rank r=8、alpha=16（scale=α/r=2）**；`lora_A` Kaiming 初始化、`lora_B` **零初始化** → 步 0 有效权重 == 冻结文本塔（无冷启动漂移，臂从与基线字节一致的点出发）。
- **可训参数量 = 12 层 × 2 投影 × (8×768×2) = 294,912 ≈ 0.30M**（已实测 `[text-finetune] trainable=0.295M`）。
- **LoRA 独立参数组**：lr **1e-4**（warmup 20、wd=0），视觉 lr 仍 3e-3 —— 理由：「文本塔解冻」本质要求给新增可训参数一个 lr；沿用 3e-3 会违背「轻量微调」、极可能重蹈 R4「随机 text 塔坍缩」。⚠️ 此 lr 为预注册值，出结果前不变。

### 11.3 重跑 R4 坍缩判据 C1–C4（probe-every 300，自动中止）

| 判据 | 定义 | 判阈值 |
|:--|:--|:--|
| C1（视觉特征坍缩） | probe 128 图视觉特征两两 cosine 上三角均值 | `C1 > 0.95` |
| C2（图文跨塔对齐） | probe 图文对 diag 均值 − 非对角均值 的 gap | `gap ≤ 0.005` |
| C4（损失形态） | total loss 相对早期指不异常回升 | 末点 loss 相对 early 异常回升 |

⚠️ **本臂文本塔可训** → 探针 `pT`（probe 文本特征）改为**每次探针用当前文本塔重算**（`text.text_module().get_text_features(...)`），不再像基线那样预计算常量 `pT`（`r9_train.py` 已改）。任一判据触发 → 训练自动中止（FUSED），记为**负结果**。

### 11.4 「翻盘」阈值（预注册）

- **坍缩（C1/C2/C4 任一触发）→ 负结果**：文本塔解冻@本 recipe 重蹈 R4 坍缩。
- **未坍缩且 IN-1k lp > 基线（6.08%@15.36M）+ 1.5 点（即 >7.58%）→ 局部翻盘**：支持「冻结 CLIP-768 文本塔正锁死渐近上限」→ 后续可升级重训文本塔。
- **未坍缩且 lp ≤ 基线+1.5 → 未翻盘**：「冻结文本塔最优」不变（同 R11-L 前四臂）。

### 11.5 公平性（§3 口径）

| 臂 | 参数量增量 | 每步额外 token | 每步耗时 |
|:--|:--|:--|:--|
| 基线① InfoNCE | 0 | 0 | 1.0× |
| **R11-L2 LoRA** | **+0.30M 可训**（文本塔 LoRA；视觉 trunk 仍 126.78M，lp 只读 trunk） | 0（无 decoder） | 待实测（应≈1.0×，LoRA 前向开销极小） |

### 11.6 实现 & 进度

- **训练**：`r9_train.py` 新增 `--text-finetune {frozen,lora}` + `--lora-rank/--lora-alpha/--lora-lr`；`FrozenClipText` 加 `LoRAParam`（`torch.nn.utils.parametrize`）；文本塔可训时 `DDP(text.clip, find_unused_parameters=True)` 包裹 + 独立参数组 + 探针重算 pT。ckpt 记录 `config['text']='lora-CLIP-768'` + `text_trainable_params/lora_rank/alpha/lr` 字段。
- **启动脚本**：`r11_run_lora.sh 30000`（镜像 `r11_run_siglip.sh`；`--loss clip --text-finetune lora --lora-rank 8 --lora-alpha 16 --lora-lr 1e-4`）。
- ✅ **smoke 通过（exit 0）**：8 卡 30 步；`[text-finetune] trainable=0.295M`；探针（probe-every 5）`C1=0.09–0.34 / C2_gap=+0.03–+0.07 / C4=OK`，无坍缩；ckpt 字段核验 `text=lora-CLIP-768 / text_trainable_params=294912 / params_active=126779392`。
- 🚀 **正式 30k 已启动（2026-10-03 23:54，`.12` 全 8 卡）**：`cd run/vision && bash r11_run_lora.sh 30000` → `R11L2_lora_w512`；日志 `/tmp/r11_lora.log`；hostname `whag0pgpuap12` + GPU 独占核验（0 MiB 占用）。**下文 §11.7 为结果与裁定。**

### 11.7 结果与裁定（✅ 完成，2026-10-04）

> 命令：`cd run/vision && bash r11_run_lora.sh 30000`（`r9_train.py --loss clip --text-finetune lora --lora-rank 8 --lora-alpha 16 --lora-lr 1e-4`，8 卡 `.12`）；证据：`/tmp/r11_lora.log`，末行 `R11-L2 LoRA(w512) ALL DONE 2026-10-04 02:12:53`（exit 0）。

- **训练健康（无坍缩）**：`[done] total=7530.7s steps=30000 steady_image_s=2480.1 final_loss=3.7105 fused=False`；末点探针 `C1=0.2839 C2_diag=0.1978 C2_off=0.0872 C2_gap=+0.1106 loss_ema=3.7105 loss_early=5.9503 C4=OK`。全程 C1 ~0.24–0.31（≪0.95）、C2_gap +0.11~+0.14（≫0.005）、C4=OK → **未触发 R4 坍缩**。
- **IN-1k frozen-trunk lp / zs**（`r8_eval_in1k.py --ckpts step{10k,20k,30k}+final`，同 R9/R10 口径）：

| N | 步 | lp top-1 | zs top-1 | zs top-5 | InfoNCE 基线 lp | Δ lp |
|:--|:--|--:|--:|--:|--:|--:|
| 5.12M | 10k | **3.13%** | 1.10% | 3.94% | 3.43% | **−0.30** |
| 10.24M | 20k | **4.75%** | 1.61% | 5.78% | 5.45% | **−0.70** |
| 15.36M | 30k | **5.28%** | 1.77% | 6.36% | 6.08% | **−0.80** |

- **裁定（预注册 §11.4）**：**未坍缩**；lp @15.36M = **5.28% < 基线 6.08% + 1.5 = 7.58%** → **未翻盘**；三档 N 的 Δ lp 全为微负（−0.30 ~ −0.80，落在 run 噪声带 0.5–1.1 pp 内）→ **「冻结 CLIP-768 文本塔锁死渐近上限」假说未获支持**：轻量 LoRA 解冻（+0.30M、零初始化起点）不抬高 frozen-trunk lp、反略低 → **冻结文本塔在本 recipe 下仍最优**（与 R11-L 前四臂一致）。
- **科学意义**：LoRA 解冻**不坍缩**（零初始化 + lr1e-4 防住 R4「随机 text 塔坍缩」）但**也无正收益** → 「文本塔解冻」在当前数据/塔规模**不是杠杆**；**重训文本塔（≈3+ 臂）不再推荐**。
- **公平性（§11.5）**：参数量 **+0.30M 可训**（文本塔 LoRA；vision trunk 仍 126.78M，lp 只读 trunk）、额外 token=0；总墙 **7530.7s ≈ 2.09h**、`steady_image_s=2480.1`（vs 基线 ~1.98h / arm② 2447.7 img/s）→ 每步耗时 **≈1.0×**（LoRA 前向开销可忽略）。

---

## 12. R11-L `caption-loss-weight` 三点消融（替代臂⑤ GenLIP）· 预注册 + 启动（2026-10-04）

> **批准依据**：运维指令 2026-10-03（三）row #2 —— 臂⑤ GenLIP 🚫 跳过，替代为 `--caption-loss-weight` **{0.5, 1.0, 2.0}** 三点消融（2.0 已 = arm④ CoCa，lp 0.47%≈随机），**排期：R11-L2 之后**。回答「是 caption 监督本身与 IN-1k frozen-trunk 特征正交，还是 weight=2.0 压死 trunk」。

### 12.1 臂定义（只变 caption weight，其余同 arm④）

- 复用 arm④ CoCa 全配置：OV2 w512 + 冻结 CLIP-768 + `CoCaDecoder`（depth4/w768/h12，+76.2M 可训）+ 短 caption 数据（CC12M+Amshaker）+ 30k 步（N=15.36M）+ IN-1k frozen-trunk lp。
- **唯一变化**：`--caption-loss-weight` ∈ **{0.5, 1.0}**（2.0 已 = arm④，作对照第三点）。

### 12.2 预注册判据（先定后测，不许改）

- 参照：InfoNCE 基线 lp = **6.08%@15.36M**；arm④ CoCa weight=2.0 lp = **0.47%@15.36M**（≈随机）。
- **假设 A（weight 是压死 trunk 主因）**：若 weight=0.5 **或** 1.0 的 lp@15.36M **≥ 基线 −1.5 = 4.58%** → caption 监督与 IN-1k 非正交，weight=2.0 是「打回随机」主因；低 weight 下对比+生成可兼容。
- **假设 B（caption 监督本身与 IN-1k 正交）**：若 0.5 **与** 1.0 两点的 lp@15.36M **都 < 4.58%**（仍≈随机）→ caption 监督与 IN-1k frozen-trunk 特征正交（无论 weight 都破坏 trunk）→ 稠密 caption 路径判死，臂⑤ GenLIP 跳过结论坐实。
- **单调性增量判据**：若 lp 随 weight↓（2.0→1.0→0.5）单调回升 → 主因是 weight（A 增强）；若三点 lp 都≈随机、无单调 → 主因是 caption 监督本身（B）。

### 12.3 公平性（§3 口径，同 arm④）

| 臂 | 参数量增量 | 额外 token | 每步耗时 |
|:--|:--|:--|:--|
| arm④ CoCa w=2.0 | +76.2M decoder | +caption CE | 0.97×（6911.7s） |
| caption_weight 0.5 / 1.0 | +76.2M decoder（同） | +caption CE（同） | 待实测（应 ≈0.97–1.0×） |

### 12.4 启动脚本与进度

- 脚本：`r11_run_capweight.sh`（循环 weight ∈ {0.5, 1.0}，各训 30k 步 + 自动回收 4 ckpt IN-1k lp）；日志 `/tmp/r11_capweight.log`；输出 `R11L_capw0p5_w512` / `R11L_capw1p0_w512`。
- 🚀 **启动（2026-10-04 02:15，`.12` 全 8 卡，GPU 已核空闲）**；✅ **两点均训完+评测完（06:54 `ALL DONE`）** → 结果与裁定见 §12.5。
### 12.5 结果与裁定（✅ 完成，2026-10-04）

> 命令：`cd run/vision && bash r11_run_capweight.sh 30000`（`r9_train.py --loss coca --caption-loss-weight {0.5,1.0}`，8 卡 `.12`）；证据：`/tmp/r11_capweight.log`，末行 `R11-L caption-weight ablation ALL DONE 2026-10-04 06:54:08`（exit 0）。

- **训练健康（两点均无坍缩）**：weight0.5 `[done] total=7261.3s steps=30000 steady_image_s=2628.7 final_loss=8.3768`，末点探针 C1=0.3422 / C2_gap=+0.0760 / C4=OK；weight1.0 `[done] total=7440.6s steps=30000 steady_image_s=2796.3 final_loss=11.3492`，末点探针 C1=0.3217 / C2_gap=+0.0729 / C4=OK。两点对比项 loss 全程健康（contrast ~5.3–5.6）。
- **IN-1k frozen-trunk lp / zs（各 4 ckpt 回收，同 R9 口径）**：

| 臂（caption weight） | lp @5.12M | lp @10.24M | lp @15.36M | zs top-1 @15.36M | zs top-5 @15.36M |
|:--|--:|--:|--:|--:|--:|
| InfoNCE 基线 | 3.43% | 5.45% | **6.08%** | — | — |
| arm④ CoCa w=2.0 | 0.29% | 0.37% | **0.47%** | 0.53% | — |
| caption w=1.0 | 0.39% | 0.34% | **0.61%** | 0.62% | 2.78% |
| caption w=0.5 | 0.45% | 0.43% | **0.60%** | 0.68% | 3.11% |

> lp 原始浮点：w=0.5 四点 = 0.0045 / 0.0043 / 0.0060 / 0.0060；w=1.0 四点 = 0.0039 / 0.0034 / 0.0061 / 0.0061（`/tmp/r11_capweight.log:774-780` / `:1543-1549`）。

- **裁定（预注册 §12.2）**：三点 lp@15.36M = **0.47 / 0.61 / 0.60%**，**全部 ≈ 随机、全部 << 4.58% 阈值**，**无单调回升**（0.47→0.61→0.60 为噪声平台）→ **假设 B 成立：caption 监督本身与 IN-1k frozen-trunk 特征正交（非 weight=2.0 压死）**。
- **科学意义**：caption 生成式监督（即便 weight 降到 0.5 = 对比项 5 倍权重）在小规模短 caption 下**一致地**把 frozen-trunk IN-1k 特征打回随机 → 臂⑤ GenLIP（纯 caption、无对比项）**坍缩先验更强、跳过结论坐实**；「稠密 caption 路径」在本 recipe 判死。AIMv2 式是唯一 **caption-无关**的稠密监督 → 仍是「稠密监督翻盘」假说的唯一未检验且决定性的路径（⏸ 待运维裁决）。
---

## 13. R11-E GPIC 数据轴（「10.9M 同 N 两点」版）· 预注册 + 执行（2026-10-04）

> **批准依据**：运维指令 2026-10-04（四）——R11-E 数据对比实验不再等 18.5M，改用现有 GPIC `short`（≈10.9M 对）做同 N 两点对照，即刻执行。
> **预注册原则（铁律）**：以下对照点与阈值先定后测，出评测结果前冻结不变。

### 13.1 臂定义（控变量：**只变「数据臂」**，其余全固定 = R9 阶段一 w512 / R11-L 臂①）

| 控制变量 | 值 |
|:--|:--|
| 塔 | OpenVision2 **w512（126.78M）**，depth30 / patch16 / 224² |
| **数据臂 A（基线，已落盘）** | CC12M + Amshaker ≈18.5M 对（`--data-source wds`，同 R9 glob） |
| **数据臂 B（待测，本臂）** | **GPIC `short` ≈10.9M 对**（`--data-source gpic`，从已下 tar 的 `caption_type=='short'` 过滤） |
| 步数 / 样本预算 | 30k 步 × bs64×8=512 = N 15.36M（**对照点取 step 10k / 20k**） |
| 优化器 / schedule | AdamW lr 3e-3 / warmup 20 / seed 1234 / bf16 / bs64×8=512 |
| 目标函数 | InfoNCE（`--loss clip`，512 负样本池）—— 两臂同 |
| 评测 | IN-1k frozen-trunk lp（`r8_eval_in1k.py`，step{10k,20k,30k}+final）+ 坍缩探针 C1–C4 |

### 13.2 对照点（沿用 R9 阶段一已有锚点原值）

| 对照点 N | step（bs512） | 基线 CC12M+Amshaker 的 IN-1k lp（已落盘） |
|:--|:--|--:|
| **5.12M** | 10000 | **3.43%** |
| **10.24M** | 20000 | **5.45%** |

> ⚠️ **可比区间**：GPIC `short` 当前 ≈10.9M 唯一对（1,926~1,969 tar × ≈5.6k short/tar，数据仍在下载、动态值）。
> → **只对 N ≤ 10.24M 做裁定**；step 30k（N=15.36M > 10.9M）进入数据重复轮，仅作补充、不参与裁定。
> 🚫 **不得把结论外推到 18.5M 以上**。

### 13.3 预注册裁定（先定后测，🚫 不许事后改）

| 判据 | 裁定 |
|:--|:--|
| 两点 lp 均 ≥ 基线+1.5（N=5.12M ≥ **4.93%** 且 N=10.24M ≥ **6.95%**） | 「GPIC 抬高上限」→ 后续把 GPIC 列为主力数据臂 |
| 两点 lp 均 ≤ 基线−1.5（N=5.12M ≤ **1.93%** 且 N=10.24M ≤ **3.95%**） | 「GPIC 更差」（如实写） |
| 其余（含 ±1.5 内的交叉） | 「未抬高 / 无显著差异」 |

### 13.4 公平性（§3 口径：参数量 + token + 每步耗时）

| 臂 | 参数量 | 训练 token | 30k 步耗时 |
|:--|:--|:--|:--|
| 基线 CC12M+Amshaker（R9 stage-1 w512） | 126.78M（vision trunk） | 0（对比学习，无生成 token） | ~6948s / steady ~2939 img/s |
| GPIC short（本臂） | 126.78M（同） | 0（同） | **3892.7s / steady 5918.6 img/s**（≈0.56× 基线耗时、≈2.0× 吞吐） |

### 13.5 命令与进度

- 脚本：`r11_run_gpic.sh`（`r9_train.py --loss clip --data-source gpic --data <gpic train glob>`，8 卡 `.12`）；日志 `/tmp/r11_gpic.log`；输出 `R11E_gpic_w512`。
- （进度与结果见下方追加条目）
- **公平性（§12.3 回填）**：参数量 +76.2M、额外 token +caption CE（同 arm④）；每步耗时 weight0.5 ≈ 7261.3s、weight1.0 ≈ 7440.6s → 均 ≈ 0.97–1.0×（arm④ 6911.7s），无通缩。

### 13.6 结果（2026-10-04 11:19 评测完成，训 exit 0，全程无坍缩）

- 训练：`[done] total=3892.7s steps=30000 steady_image_s=5918.6 final_loss=3.7010 fused=False`（日志 `/tmp/r11_gpic.log`）；全程无坍缩——末点探针 **C1=0.3428 / C2_gap=+0.0869 / C4=OK**，全程 C1 0.33–0.40、C2_gap +0.087~+0.095。
- IN-1k frozen-trunk（`r8_eval_in1k.py` 4 ckpt；zs top1/top5 + lp top1）：

| 对照点 N | step | GPIC short zs top1 / top5 | GPIC short lp | 基线 CC12M+Amshaker lp（已落盘） | Δ lp |
|:--|:--|--:|--:|--:|--:|
| 5.12M | 10000 | 1.91% / 6.83% | **6.01%** | 3.43% | **+2.58** |
| 10.24M | 20000 | 2.22% / 7.37% | **5.69%** | 5.45% | **+0.24** |
| 15.36M（补充①） | 30000 | 2.01% / 7.11% | 5.73% | 6.08% | −0.35 |
| 15.36M（final） | 30000 | 2.01% / 7.11% | 5.73% | 6.08% | −0.35 |

> ① 补充点：step 30k（N=15.36M）> GPIC short 唯一对（训练起跑时 **1973 tar** × ≈5.64k ≈ **11.1M**，下载仍在继续、动态）→ 进入数据重复轮，**不参与裁定**。

### 13.7 裁定（按 §13.3 预注册门槛，先定后测）

- N=5.12M：6.01% **≥ 4.93%**（≥基线+1.5）→ 该点「抬高」✓
- N=10.24M：5.69% vs 门槛 6.95% ✗（+0.24，落在 **±1.5 内**）→ 该点「未抬高」
- → 两点**交叉**（一点过线、一点在带内）→ 裁定 = **「未抬高 / 无显著差异」**。

### 13.8 结论与解读（如实；🚫 不外推到 18.5M 以上）

- **GPIC short 有显著先发优势、但不抬高 ceiling**：@5.12M 领先基线 **+2.58 点**（> 阈值 1.5 且 > 噪声带上界 1.1）；@10.24M 优势收敛到 **+0.24**（噪声带 0.5–1.1 内）；@15.36M（补充、>唯一对）反略低于基线（**5.73% vs 6.08%**，−0.35，噪声带内）。
- **机制（如实标注为推断）**：GPIC `short`（20 tok 精选 caption）单样本质量更高 → **早期收敛更快**；但其唯一对 ≈11M 在 N≈10M 处近乎耗尽 → lp 平台化在 ~5.7%；基线 CC12M+Amshaker 的 18.5M 唯一多样性继续把 lp 抬到 6.08%@15.36M。→ 「**数据质量加速早期；数据总量/多样性决定 ceiling**」。
- **公平性（§13.4 回填）**：GPIC 吞吐 5918.6 img/s ≈ **2.0×** 基线（~2939）→ 30k 步仅 3892.7s（≈0.56× 基线的 ~6948s）。对照在**同 N（样本预算）**下，故不改变「不抬高 ceiling」；若按**同 GPU·h** 比，GPIC 的低 N 先发优势会被进一步放大。
- **对本项目的影响**：R9 的 25.1% 渐近**不被数据臂改动推翻**；GPIC 的价值仅在「低预算快速启动」，本项目数据瓶颈是**总量/多样性**（本地 ≈118M 上限 vs 619 亿缺口），非 caption 质量 → R6/R7「正式训练切 GPIC short」与 R9/R10 scaling 口径**维持不变**。证据：`/tmp/r11_gpic.log`（训练 metrics + eval 段 786-797 行）。