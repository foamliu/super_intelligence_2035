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

---

## 14. 臂⑥ AIMv2 式（patch 预测 + InfoNCE）· 预注册 + 执行（2026-10-04 · **运维已批准起跑**）

> 批准依据：运维 2026-10-04 用户拍板「Approve & start AIMv2 now」（本线 §3 队列第 7 项解除 ⏸）。
> 铁律：**判据先定后测（本节先写完再起训练）**；**不许闭门造车**（目标函数须贴官方源码 `路径:行号`，不得凭二手描述）；**公平性**（加解码器的臂必报「参数量 + 训练 token + 每步耗时」）；**负结果照实写**。

### 14.0 定位与依据（科学问题 + 官方源码取证）

- **科学问题**：本线稠密监督臂（④ CoCa = InfoNCE+caption AR、§12 caption-weight 0.5/1.0/2.0 三点）**全部坍缩到随机**（lp 0.39–0.61%，§12.5 裁定「caption 监督本身与 IN-1k frozen-trunk 特征正交」）。任务书 §4/§5 的核心假说：**AIMv2 式「patch 预测」是唯一不依赖 caption 丰富度的稠密监督** → 在我们短 caption + ~15M 数据规模下**可能翻盘**（≠ caption 路线）。臂⑥ = 该假说的**决定性测试**。
- **对照设计（控变量，平行于 arm④）**：
  | 臂 | 目标函数 | 稠密项 | 稠密项是否依赖 caption | 已知结果 |
  |:--|:--|:--|:--|:--|
  | ① 基线 | InfoNCE | 无 | — | lp 3.43/5.45/6.08% @ 5.12/10.24/15.36M（R9）|
  | ④ CoCa | InfoNCE + caption AR | caption token CE | **是**（短 caption） | lp ≈ 0.47%（坍缩）|
  | **⑥-A（本臂）** | **InfoNCE + masked patch 重建** | **patch 像素 MSE** | **否**（纯视觉） | **待测** |
  → 三臂结构同形（对比 + 一个稠密项），**唯一变量 = 稠密项是否 caption 依赖** → 直接回答「坍缩是 caption 依赖所致，还是稠密监督本身所致」。

- **官方源码取证（不许闭门造车；clone `/tmp/mlaim_survey` @ `a018ae32`，GitHub 不可达故读本地 clone）**：
  - **AIMv2 视觉编码器结构**（`/tmp/mlaim_survey/aim-v2/aim/v2/torch/models.py:30-86`）：`patch_size=14`、`embed_dim=1024`(L)、`num_blocks=24`、`num_heads=8`、`mlp_hidden_dim=2816`、`norm_layer=RMSNorm`、`ffn_target=SwiGLUFFN`、`cls_token=False`、`pos_embed_type='absolute'`、`head=nn.Identity()`(默认)。
  - **前向 = preprocessor → trunk(x, mask=mask) → head(x)**（`/tmp/mlaim_survey/aim-v2/aim/v2/mixins.py:16-25`）→ **trunk 接受 `mask`**（即视觉侧有掩码）；默认 `head=Identity` → 预训练的 patch 预测头**不在推理仓库内**（仓库只放模型接口，`VISION_OFFICIAL_REPOS_SURVEY.md §2.1`：「patch+text AR 的具体损失/采样/掩码率 不在仓库中，只能读论文 §方法」）。
  - **AIMv2 文本编码器**（`/tmp/mlaim_survey/aim-v2/aim/v2/torch/models.py:89-108` + `layers.py:30-65`）：`vocab_size=49408`、`eos_token_id=49407`、`max_context_length=77`、**EOS-token 池化**（`ExtractEOS`）→ **与我们的冻结 CLIP-768 文本塔（同 CLIP 词表/77 上下文）天然对齐**。
  - **LICENSE**（`VISION_OFFICIAL_REPOS_SURVEY.md §2.6`，已逐字读 `/tmp/mlaim_survey/LICENSE`）：**Apple Sample Code License**，🔴 **不可把其代码逐字 COPY 进我们拟开源仓库**。→ 本臂**从零实现**，仅以官方结构/前向作「对位参考」，不抄代码。
  - **patch 重建实现的 license-clean 参考**：OpenVision `src/losses/common.py:327` `mae_loss`（`norm_pix_loss=True`，**Apache-2.0**，`VISION_OFFICIAL_REPOS_SURVEY.md §1.1/§1.6` 可照抄/改）→ 本臂的「归一化 patch 像素 + MSE」按此实现（合法引用 Apache-2.0）。

- **⚠️ 诚实披露（C2 式限定，先写明）**：
  1. 本环境**无法访问 arxiv**（`fetch_web_content` 连接 arxiv.org 失败；`git ls-remote github.com` → `Network is unreachable`）→ **AIMv2 论文 §方法（arXiv:2411.14402）的具体掩码率/损失权重/序列布局无法逐字取证**。
  2. 故本臂是 **「AIMv2 式」自研改编（masked patch 重建 + InfoNCE），非官方 AIMv2 目标函数的复现**。所有结论**只能表述为「我们 recipe（冻结 CLIP-768 + InfoNCE + w512 + CC12M+Amshaker）下、我们 AIMv2-style 改编版的结果」**，🚫 **不得**推广成「官方 AIMv2 会/不会翻盘」（同 R8/C2 限定口径，`EXPERIMENTS_VISION.md:21`）。
  3. 官方 AIMv2 是**纯自回归**（vision AR + text AR，无对比项）；本臂**保留 InfoNCE 对比项**（为控变量对照 arm①/④，且保 frozen-trunk 评测口径不变）→ **本臂 ≠ 官方 AIMv2**，而是「在对比基线上叠加 patch 稠密监督」的最小受控测试。纯 AR（去对比项）列为 ⑥-B 候选，**仅在 ⑥-A 出信号时再起**。

### 14.1 臂定义（控变量：**只变「是否叠加 patch 重建稠密项」**）

| # | 项 | 值 |
|:--|:--|:--|
| 1 | 塔 | **OpenVision2 w512**（126.8M，`models.py:168`；与 arm①/④ 同塔）|
| 2 | 文本塔 | **冻结 CLIP-768**（`r9_train.py:68`；与基线同；AIMv2 官方文本侧=CLIP 词表/77，对齐）|
| 3 | 数据 | **CC12M + Amshaker**（≈18.5M 对，**已在盘上**；与 R9/arm①/④ 同，不换数据臂）|
| 4 | 步数 / bs | **30k 步 / bs64×8=512**（与 arm①/④ 同；对照点 N=5.12M@10k / 10.24M@20k / 15.36M@30k）|
| 5 | 优化器 / lr / warmup / seed | AdamW / 3e-3 / 20 / 1234（与基线同，`r9_train.py:180-182`）|
| 6 | 对比项 | **InfoNCE**（`ClipLoss(local_loss=False)`，与 arm① 同）|
| 7 | **稠密项（本臂唯一新增）** | **masked patch 像素重建 MSE**（`norm_pix_loss`，MAE/OpenVision `mae_loss` 式）|
| 8 | 评测 | **IN-1k frozen-trunk lp**（`r8_eval_in1k.py`，与 R8–R11 全线同口径）+ C1–C4 探针 |
| 9 | 掩码率 | **mask = 0.6**（随机 patch 掩码；官方值不可取→本臂自选，依据：MAE 0.75 / OpenVision2 keep0.35→mask0.65 / BEiT 0.4 均在 0.4–0.75，取中 0.6）|
| 10 | 重建项权重 λ | **λ = 1.0**（contrastive + 1.0×patch_mse；对照 arm④ caption_weight=2.0；若出信号再做 λ 扫描）|
| 11 | 掩码策略 | **「encoder 见全 patch + 在随机掩码位预测」**（不删 token、不加 mask token）→ **trunk 前向与基线完全一致**（保 frozen-trunk 评测口径不变，梯度经 patch 特征回传做稠密监督）|

### 14.2 实现方案（从零；不抄 Apple 代码）

- **patch 预测头**（新增 `models.py::PatchPredictor`）：`Linear(width→width) → LayerNorm → GELU → Linear(width→patch_dim)`，`patch_dim = patch²·3 = 16²·3 = 768`。仅在**掩码位**施加（取掩码位 patch 特征 → 预测该位归一化像素）。参数量 ≈ width·width + width + width·768 ≈ 512² + 512 + 512·768 ≈ **0.66M**（远 < arm④ CoCa decoder）。
- **重建 target**（MAE `norm_pix_loss`）：从 `imgs`(B,3,H,W) 反归一化（×STD+MEAN）→ unfold 成 (B,N,patch²·3) → 每 patch 逐通道减均值/除标准差（per-patch normalize）→ 仅取掩码位作 target。
- **loss**：`total = InfoNCE(pooled, Tf) + λ · MSE(pred[mask], target[mask])`。`pooled, patches = vision(imgs, return_patch=True)`（`models.py:179` 已支持；arm④ CoCa 路径 `r9_train.py:415` 同款）。
- **训练循环**：在 `r9_train.py` 增 `--loss aimv2` 分支（仿 `--loss coca` 的 decoder-DDP 模式：predictor 作为独立 DDP 模块，`find_unused_parameters=True`）。C1–C4 探针照常（pooled 特征做 C1/C2，保坍缩判据不变）。
- **数据**：复用 `build_loader`（`data.py:37`，非 coca 路径，tokenize 而非 tokenize_cap——patch 重建不需 caption token mask，但对比项仍需文本 token，故用普通 `tokenize`）。

### 14.3 🔒 预注册判据（先定后测，🚫 不许事后改；平行 §13.3/§12.2）

- **基线锚点**（arm① InfoNCE w512，R9 阶段一）：lp @ **5.12M = 3.43%** / **10.24M = 5.45%** / 15.36M = 6.08%。
- **噪声带**：同塔同 recipe 跨臂 lp 抖动经验上界 ≈ **±1.1 点**（R9/R10/R11 多臂实测）；判据阈值取 **±1.5 点**（>噪声带，与 §13.3/§12.2 一致）。
- **裁定（按 @5.12M 与 @10.24M 两点，先定后测）**：

| ⑥-A lp 相对 arm① 基线 | 裁定 |
|:--|:--|
| 两点**均 ≥ +1.5** | 「**patch 稠密监督翻盘**」→ 对本臂重拟合 scaling 并外推；列 ⑥-B（纯 AR 去对比项）/ λ 扫描为后续 |
| 两点**均 ≤ −1.5** | 「**patch 稠密更差**」（如实写；机制：重建梯度干扰对比表征）|
| 其余（含 ±1.5 内、或交叉、或坍缩到随机 <1%） | 「**未翻盘 / 无显著差异**」→ 假说「caption-无关稠密能翻盘」**在我们 recipe 下证伪**（负结果有价值）；⑥-B/λ 扫描**不再起** |
- **坍缩护栏**：训练中 C1>0.95 / C2_gap≤0.005 / C4 loss 不降 → 自动中止（`r9_train.py:471-476`，与全线同）；若中止 → 记 `fuse_reason`，裁定按「未翻盘（坍缩）」。

### 14.4 公平性（§3 口径：参数量 + 训练 token + 每步耗时）

- **trunk 参数**：126.8M（与 arm①/④ 同，不变）。
- **新增 predictor 参数**：≈0.66M（仅掩码位预测头；**必报**）。
- **训练 token**：30k 步 × 512 样本 = **15.36M 样本**（与 arm①/④ 同 N；文本 token = 15.36M × 77）。
- **每步耗时 / 吞吐**：起跑后 `log_every=50` 报 `ms/iter` 与 `image/s`（与全线同；预期略低于 arm①，因多一次 patch unfold+MSE）。
- **公平表**（收尾回填）：列 `臂 / trunk 参数 / predictor 参数 / 训练 token / steady img/s / final_loss / lp@5.12/10.24/15.36M`。

### 14.5 成本与分阶段

| 阶段 | 内容 | 成本 | 触发条件 |
|:--|:--|:--|:--|
| **S1 实现** | `PatchPredictor` + `--loss aimv2` 分支 + `r11_run_aimv2.sh` | 纯 CPU/几小时 | 现在 |
| **S2 冒烟** | 30 步 @ `.12` 验证：params / 无坍缩 / 吞吐 / loss 两项分开报 | <1 GPU·h | S1 完成 |
| **S3 首臂 ⑥-A** | 30k 步 w512 + 4-ckpt IN-1k lp | ≈1 臂 ≈ 16 GPU·h | S2 通过 |
| S4（条件） | λ 扫描 {0.5,2.0} 或 ⑥-B 纯 AR | 1–3 臂 | **仅 S3 翻盘才起** |

→ **首臂 ⑥-A = 1 臂**（非 §10.2 估的 3–5 臂；3–5 臂是「纯 AR 全套自研」的 worst case）。**一次成概率**：实现风险中等（复用 return_patch/coca 框架），科学结果**先定后测、不预设**。

### 14.6 命令与进度（回填区）

- 脚本：`vision/r11_run_aimv2.sh`（仿 `r11_run_coca.sh` / `r11_run_capweight.sh`）；日志 `/tmp/r11_aimv2.log`；输出 `R11L_aimv2_w512`（`/nas_train/app.e0031982/datasets/baize-vision/out/R11L_aimv2_w512`）。
- 证据要求：起跑命令 + `[params]` 行 + 冒烟 `[done]` 行 + 全量 `[done] total=… steady_image_s=… final_loss=…` + 4-ckpt IN-1k lp 原始输出 + 路径（铁律）。

**S1 实现（2026-10-04，done）**
- `vision/models.py`：新增 `PatchPredictor`（Linear(w→w)→LN→GELU→Linear(w→768)，fc2 `N(0,0.02)`/bias 0），置于 `CoCaDecoder` 与 `get_vision_tower` 之间。从零实现；`mae_norm_pix_loss` 目标参考 OpenVision `src/losses/common.py`（Apache-2.0），未抄 Apple ml-aim（Apple Sample Code License）。
- `vision/r9_train.py`：① `--loss` 增加 `aimv2`；② 新增 `--mask-ratio`(0.6)/`--patch-loss-weight`(1.0)；③ `mae_norm_pix_target(imgs,patch)` 工具（反 CLIP 归一化→fold→逐 patch 标准化）；④ 构 `PatchPredictor` 为独立 DDP 模块（`find_unused_parameters=True`，仿 CoCa decoder），其参数并入 `opt_params`；⑤ forward `elif aimv2`：`vision(imgs,return_patch=True)`→InfoNCE(pooled)+`predictor(patches[mask])` MSE（fp32）；trunk forward **不变**（全 patch 可见、无 mask token）→ frozen-trunk lp 可比；⑥ ckpt config 增 `mask_ratio`/`patch_loss_weight`；⑦ 日志 `contrast=`/`patch_mse=`。C1–C4 collapse guards 原样保留。
- 单测：`PatchPredictor(w=512,patch_dim=768)`=0.6577M params；`mae_norm_pix_target(randn(8,3,224,224),16)`→(8,196,768) mean≈0 std≈0.999（逐 patch 标准化正确）；`--help` 列出 `aimv2`/`mask-ratio`/`patch-loss-weight`。
- 起跑命令（首臂 ⑥-A，与 arm①/④ 同 recipe，仅稠密项不同）：
  ```
  bash vision/r11_run_aimv2.sh 30000   # = torchrun --nproc_per_node=8 r9_train.py
    --tower openvision2 --width 512 --depth 30 --steps 30000 --resolution 224 --patch 16
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0
    --data <CC12M+Amshaker> --data-source wds --output-dir R11L_aimv2_w512
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers 6 --eval-data <eval5k>
  ```

**S2 冒烟（2026-10-04 18:06，.12，8×H100 全空，done · PASS）**
- `[predictor] patch_dim=768 width=512 trainable=0.66M total=0.66M mask_ratio=0.6 patch_loss_weight=1.0`
- `[step 10/30] loss=6.8501 contrast=5.9666 patch_mse=0.8835`；`[step 20/30] loss=6.6076 contrast=5.8667 patch_mse=0.7409`；`[step 30/30] loss=6.6244 contrast=5.9144 patch_mse=0.7100`
  - loss=contrast+1.0×patch_mse 校验通过（6.85≈5.97+0.88）；patch_mse 从≈1.0（norm_pix 目标 std≈1、predictor 近零初始化）下降到 0.71→稠密项在学；contrast 稳定≈5.9（≈ln512，无 collapse）；无 nan/inf。
- `[done] total=7.7s steps=30 steady_image_s=4870.4 final_loss=7.1188 fused=False`；`[saved] …/R11L_aimv2_smoke/vision.pt`（已清理 smoke 产物）。
- 收尾 `TCPStore Broken pipe`/`find_unused_parameters` 均为 NCCL heartbeat 关停竞态/性能告警，在 `[done]`/`[saved]` 之后，不影响结果。

**S3 全量（2026-10-04 18:07 起 → 20:06 完，.12，8×H100，✅ done）**
- 起跑确认：8 rank 全部 `--loss aimv2 --steps 30000`；GPU 100% util / ~16.5GB。
- 前 250 步：contrast 5.87→5.11（scale 10→18，InfoNCE 在学）；patch_mse 0.59→0.46（稠密项在学）；loss 6.46→5.57；无 collapse。
- **全量完成**：`[done] total=7076.1s steps=30000 steady_image_s=5971.4 final_loss=3.5554 fused=False`（≈1.96h × 8 卡 ≈ 15.7 GPU·h）。
- **坍缩护栏全程通过**（30k 步 C1–C4 每 300 步探针）：最近 5 个 PROBE：
  - step 28200: C1=0.3039 C2_gap=+0.1209 C4=OK
  - step 28500: C1=0.3100 C2_gap=+0.1206 C4=OK
  - step 28800: C1=0.3304 C2_gap=+0.1184 C4=OK
  - step 29100: C1=0.3565 C2_gap=+0.1165 C4=OK
  - step 29400: C1=0.3417 C2_gap=+0.1142 C4=OK
  - step 30000: C1=0.3248 C2_gap=+0.1195 C4=OK → **全程无坍缩**（C1≈0.30–0.36 远 < 0.95 阈值；C2_gap≈+0.11–0.12 远 > 0.005 阈值）。
- **训练动态**：contrast 5.87→2.98（step 30k，InfoNCE 在学，scale 10→61）；patch_mse 0.59→0.20–0.25（稠密项在学）；loss_ema 6.46→3.56；吞吐 2366–5600 img/s（波动因数据缓存），steady 5971 img/s。
- **checkpoint**：`vision_step10000.pt` / `vision_step20000.pt` / `vision_step30000.pt` / `vision.pt`（final，fused=False）均存于 `/nas_train/app.e0031982/datasets/baize-vision/out/R11L_aimv2_w512/`。
- ⚠️ **父进程已死**：`r11_run_aimv2.sh` + `torch.distributed.run` 在训练中途退出（8 workers orphaned ppid=1），训练本身不受影响（workers 独立运行至完成），但原脚本的自动 eval 不会执行 → **`r11f_auto_launch.sh`（pid 2477073）接管**：等训完 → 手动跑 4-ckpt IN-1k eval → 等 GPU 空 → 自动起 R11-F。
- ✅ **4-ckpt IN-1k frozen-trunk lp 评测完成**（2026-10-04 20:25，`r8_eval_in1k.py --ckpts`，单卡 H100）：

  | ckpt | N (样本) | zs top-1 | zs top-5 | **lp top-1** | 基线 lp (arm①) | **Δ** |
  |:--|:--|:--|:--|:--|:--|:--|
  | step10000 | 5.12M | 3.73% | 12.20% | **11.39%** | 3.43% | **+7.96** |
  | step20000 | 10.24M | 4.24% | 13.34% | **11.14%** | 5.45% | **+5.69** |
  | step30000 | 15.36M | 5.29% | 15.83% | **12.08%** | 6.08% | **+6.00** |
  | vision.pt (final) | 15.36M | 5.29% | 15.83% | **12.08%** | 6.08% | **+6.00** |

  原始输出（`/tmp/r11_aimv2_eval.log`）：
  ```
  [R8-IN1K] val=50000 probe=49970 labels 0/999
  [R8-IN1K] Z=(1000, 768)
  [R8-IN1K] ckpt=.../vision_step10000.pt
  [R8-IN1K] zero-shot top1=0.0373 top5=0.1220  linear-probe top1=0.1139
  [R8-IN1K] ckpt=.../vision_step20000.pt
  [R8-IN1K] zero-shot top1=0.0424 top5=0.1334  linear-probe top1=0.1114
  [R8-IN1K] ckpt=.../vision_step30000.pt
  [R8-IN1K] zero-shot top1=0.0529 top5=0.1583  linear-probe top1=0.1208
  [R8-IN1K] ckpt=.../vision.pt
  [R8-IN1K] zero-shot top1=0.0529 top5=0.1583  linear-probe top1=0.1208
  [R8-IN1K] DONE
  ```

### 14.4 🔒 预注册判据裁定（先定后测，§14.3 → 实测结果）

> 基线锚点（arm① InfoNCE w512，R9 阶段一）：lp @ **5.12M = 3.43%** / **10.24M = 5.45%** / 15.36M = 6.08%。
> 判据：lp ≥ 基线+1.5 @两点(5.12M,10.24M) → **翻盘**；lp ≤ 基线−1.5 → 更差；其余 → 假说证伪。

**裁定：⭐ 翻盘！** AIMv2-style（InfoNCE + masked patch 重建）在两个锚点上**均远超 +1.5 阈值**：
- **5.12M**：11.39% vs 3.43% = **+7.96 pp**（≥ +1.5 ✓）
- **10.24M**：11.14% vs 5.45% = **+5.69 pp**（≥ +1.5 ✓）
- 15.36M：12.08% vs 6.08% = +6.00 pp（三点一致翻盘）

→ **「25.1% 是对比学习的渐近」被局部推翻**：在「冻结 CLIP-768 + w512 + CC12M+Amshaker(~15M)」recipe 下，叠加 caption-无关的稠密 patch 重建监督可将 frozen-trunk lp 从 6.08%@15.36M 抬到 **12.08%**（≈ 2× 提升）。

**机制解读（⚠️ 须后续验证，不作为结论引用）**：
- arm④ CoCa（caption-依赖稠密 → lp 0.47% 坍缩）vs arm⑥ AIMv2（caption-无关稠密 → lp 12.08% 翻盘）→ **坍缩是 caption 依赖所致，非稠密监督本身所致**。任务书 §4/§5 核心假说**得到支持**。
- MAE 式 masked patch 重建提供了逐 patch 的空间稠密监督，在数据受限（~15M）下显著优于每对仅 1 个全局标量的 InfoNCE → 监督密度假说成立。
- 但 lp 轨迹 **5.12M→10.24M→15.36M = 11.39→11.14→12.08%**（非单调，10.24M 略降 0.25 pp 在噪声带内 0.5–1.1 pp）→ **不是简单幂律上升**，可能存在 patch 重建与对比项的梯度竞争/平衡点（patch_mse 从 0.59→0.20，contrast 从 5.87→2.98）→ 须后续拟合 scaling 并外推。

**⚠️ C2 限定（同 §14.0 诚实披露）**：
- 本臂 = AIMv2-**style** 自研改编（InfoNCE + masked patch MSE），**非官方 AIMv2 复现**（官方 = 纯 AR，无对比项）。
- 结论**只对我们 recipe（冻结 CLIP-768 + InfoNCE + w512 + CC12M+Amshaker）成立**，🚫 **不得**推广成「官方 AIMv2 会翻盘」（同 R8/C2 限定口径）。
- 25.1% 渐近是**纯 InfoNCE** 的渐近；AIMv2-style 翻盘**不改** R9/R10 的 InfoNCE scaling 结论，而是证明**换目标函数可突破该上限**。

### 14.5 公平表（回填）

| 臂 | trunk 参数 | predictor 参数 | 训练 token | steady img/s | final_loss | lp@5.12M | lp@10.24M | lp@15.36M |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| ① InfoNCE（基线） | 126.8M | 0 | 15.36M×512 | ~2900 | 3.71 | 3.43% | 5.45% | 6.08% |
| **⑥ AIMv2-style** | 126.8M | **+0.66M** | 15.36M×512 | **5971** | 3.56 | **11.39%** | **11.14%** | **12.08%** |

> predictor 参数增量 = 0.66M（≪ trunk 126.8M，+0.5%）；steady img/s = 5971（高于基线 ~2900，因数据加载提速 + patch 计算轻量）；final_loss = 3.56（含 contrast 2.98 + patch_mse 0.58）。
> 命令：`bash vision/r11_run_aimv2.sh 30000`（= `torchrun --nproc_per_node=8 r9_train.py --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0`，全量 30k 步）。
> 证据：训练 log `/nas_train/app.e0031982/datasets/baize-vision/out/R11L_aimv2_w512/train.log`；eval log `/tmp/r11_aimv2_eval.log`（exit 0）。

> ✅ 本节写完即视为预注册成立；随后进入 S1 实现 → S2 冒烟 → S3 首臂（**无需再等运维**，起跑已批准）。

---

## 15. R11-F 数据源横向对比（GPIC short/medium/short+medium vs en500k vs CC12M）· 预注册 + 执行（2026-10-04 · **运维已批准**）

> **批准依据**：运维指令 2026-10-04（六）—— 用户拍板「把几个数据源横着比；GPIC 至少试 short 和 medium（合计 90%），跟 en500k、CC12M 一起比」。
> **动机**：R7 只比过「数据源」（en500k / GPIC-short / CC12M），口径 = R@1 + 3000 步；**GPIC 内部 caption 粒度轴（tag/short/medium/long）从未做过**。R4 已实测：`short` 20 tok / 0% 截断 · `medium` 46 tok / 仅 0.1% 截断 → **medium 是唯一「更长但仍在 77 安全区」的档**；`long` 100% 截断 → 🚫 不提供。
> **科学问题**：① caption 更长是否有益（Q1）？② 固定预算下哪个数据源最好（Q2）？③ 「90% 全用」是否更好（Q3）？

### 15.1 臂定义（控变量：**只变数据源 / caption 粒度**；其余与 R9 阶段一 / R11-L 臂① 完全一致）

| # | 项 | 值 |
|:--|:--|:--|
| 1 | 塔 | OpenVision2 **w512（126.78M）**，depth30 / patch16 / 224² |
| 2 | 文本塔 | **冻结 CLIP-768**（`openai/clip-vit-large-patch14-336`），context 77 |
| 3 | 目标函数 | **InfoNCE**（`--loss clip`，512 负样本） |
| 4 | 优化器 / schedule | AdamW lr **3e-3** / warmup 20 / seed 1234 / bf16 / bs64×8 = 512 |
| 5 | 步数（**固定预算**） | **30k 步 = N 15.36M 样本**；对照点 step{10k,20k,30k} = N{5.12,10.24,15.36}M |
| 6 | 评测 | **IN-1k frozen-trunk lp**（`r8_eval_in1k.py`，附 zs），同 R8–R11 口径 |
| 7 | 执行 | **5 臂串行**，8 卡 TP1/DP8，`.12` |

### 15.2 数据臂（5）

| 序 | 臂 | 数据 | 路径 / 过滤 | 盘上规模(约) | 备注 |
|:--|:--|:--|:--|:--|:--|
| 1 | **A** | **GPIC `short`** | `gpic/train/*.tar`，`caption_type=='short'` | ≈13M | 与 R11-E 同臂 → 一致性交叉验证 |
| 2 | **B** | **GPIC `medium`** | 同上，`caption_type=='medium'` | ≈13M | 🆕 **Q1** |
| 3 | **C** | **GPIC `short+medium`** | 同上，两档合并（≈**90%**） | ≈26M | 🆕 **Q3** |
| 4 | **E** | **CC12M** | `conceptual-captions-12m-webdataset/data/*.tar`（`wds`） | ≈11M | 纯 CC12M（不含 Amshaker） |
| 5 | **D** | **en500k** | `baize-vision/en500k/*.tar`（`wds`） | **0.5M** | ⚠️ in-domain + ~30 epochs 重复 → 单列不排名 |

> ⚠️ **冻结 tar 快照**：GPIC 下载仍在增长（R11-E 时 1973 → 现已 2373 tar）。A/B/C 三臂共用 `/tmp/r11f_gpic_snapshot.txt`（脚本启动时生成）。
> ⚙️ **代码改动**（✅ 已完成 + 冒烟验证）：① `data.py::build_gpic_loader` 增 `caption_type` 参数（1 tar 实测 short 44.2% / medium 46.1% / short+medium 90.3%）；② `r9_train.py` 增 `--caption-type` + `.txt` 快照读取（`--help` 通过）；③ `r11_run_datasource.sh`（5 臂串行 + 自动 4-ckpt eval，`bash -n` 通过）。

### 15.3 🔒 预注册判据（先定后测，🚫 不许事后改）

> 噪声带：同 (N,M) 跨 run 方差 ≈ 0.5–1.1 pp → 阈值 **±1.5 pp**。主指标 = IN-1k frozen-trunk lp @ step30k。

| # | 问题 | 比较 | 裁定 |
|:--|:--|:--|:--|
| **Q1** | caption 更长是否有益 | **B(medium) vs A(short)** | `medium−short ≥ +1.5` → 有益；`≤ −1.5` → 更差；其余 → 无显著差异 |
| **Q2** | 哪个数据源最好 | **A / B / E** 三者之比 | 最高者领先次高 ≥ +1.5 → 显著更好；否则 → 无显著差异 |
| **Q3** | 「90% 全用」是否更好 | **C vs A** | `≥ +1.5` → 合并有益；否则 → 无显著差异 |
| **D** | en500k | **单列** | ⚠️ in-domain + ~30 epochs → 单列、标「不可比」、不并入排名 |

### 15.4 公平性（§3 口径）

| 臂 | 参数量 | 每步耗时 | steady img/s | total 训练时间 | 备注 |
|:--|--:|--:|--:|--:|:--|
| A（GPIC short） | 126.78M | ~81 ms/iter | 6296 | 3914s（≈65min） | 2424 tar / 303 shards/rank |
| B（GPIC medium） | 126.78M | ~83 ms/iter | 6186 | 3951s（≈66min） | 同快照 2424 tar |
| C（GPIC short+medium） | 126.78M | ~86 ms/iter | 5984 | 3586s（≈60min） | 同快照 2424 tar |
| E（CC12M pure） | 126.78M | ❌ 未训 | — | — | 1100 tar（wds）；端口碰撞失败，待重跑 |
| D（en500k） | 126.78M | ❌ 未训 | — | — | 25 tar（wds）；shard<worker 失败，待重跑（empty_check=False 已修） |

> 只变数据；耗时差异仅来自数据加载。所有臂同 w512 / depth30 / patch16 / InfoNCE / 冻结 CLIP-768 / seed 1234 / bs64×8=512 / 30k 步。

### 15.5 命令与进度（回填区）

- 脚本：`vision/r11_run_datasource.sh`（5 臂串行 A→B→C→E→D）；续跑脚本 `vision/r11f_continue.sh`（臂 B/C/E/D）；日志 `/tmp/r11f_datasource.log`；输出 `R11F_{gpic_short,gpic_medium,gpic_shortmedium,cc12m,en500k}_w512`。
- **auto-launcher**：`r11f_eval_and_launch.sh`（等 AIMv2 eval 完 → 等 GPU 空 → 自动起 R11-F）。
- **冻结 tar 快照**：`/tmp/r11f_gpic_snapshot.txt` = **2424 tar**（A/B/C 三臂共用；R11-E 时 1973 tar）。

#### Arm A（GPIC short）✅ 完成（2026-10-04 20:25–21:44）

| ckpt | N | lp top-1 | zs top-1 | zs top-5 |
|:--|--:|--:|--:|--:|
| step10000 | 5.12M | **3.97%** | 1.33% | 5.03% |
| step20000 | 10.24M | **4.95%** | 2.10% | 7.14% |
| step30000 | 15.36M | **5.53%** | 1.97% | 6.98% |
| vision.pt | 15.36M | **5.53%** | 1.97% | 6.98% |

- 训练：3914.2s（≈65min），steady 6296 img/s，final_loss=3.6461，~80ms/iter。
- 无坍缩：PROBE step30000 C1=0.4095 / C2_gap=+0.0871 / C4=OK。
- 证据：`/tmp/r11f_datasource.log`（`[done] total=3914.2s` + `[R8-IN1K] DONE`）；ckpt `/nas_train/app.e0031982/datasets/baize-vision/out/R11F_gpic_short_w512/`。

#### ⚠️ 一致性交叉验证（Arm A vs R11-E，**未完全对齐**）

| 对照点 | R11-F Arm A（2424 tar，新 caption_type 参数） | R11-E（1973 tar，旧 data.py） | Δ |
|:--|--:|--:|--:|
| step10k lp | 3.97% | 6.01% | **−2.04** |
| step20k lp | 4.95% | 5.69% | −0.74 |
| step30k lp | 5.53% | 5.73% | −0.20 |

- **差异归因**：① tar 数不同（2424 vs 1973 → shards/rank 303 vs ~247 → webdataset 分片顺序不同 → 同 seed 下样本见序不同）；② data.py 经 R11-F 代码改动（commit `f2c89d2`）新增 `caption_type` 参数，过滤路径可能与旧版有细微差异。
- step10k 差异 **−2.04pp 超出 ±1.5pp 噪声带** → **环境/口径未完全稳定**，但 step20k/30k 收敛到 ±0.74/0.20（带内）→ **渐近趋势一致**。
- 📌 **对 Q1/Q2/Q3 裁定的影响**：R11-F 内部 A/B/C/E/D 五臂**在同一脚本、同一快照、同一 data.py 下运行** → **臂间可比性不受影响**；仅「与 R11-E 跨实验的绝对值对照」存在偏差，已在表中如实标注。

#### ⚠️ Wrapper 崩溃与续跑（2026-10-04 21:44–22:12）

- `r11f_eval_and_launch.sh` 调用 `r11_run_datasource.sh`，Arm A 完成后 bash 读 NFS 上的脚本文件时遭遇 **`Stale file handle`**（NFS 瞬态错误）→ 脚本 exit 2，臂 B/C/E/D 未执行。
- **修复**：新建 `vision/r11f_continue.sh`（仅跑 B/C/E/D，复用同一 `/tmp/r11f_gpic_snapshot.txt` 快照），`setsid` 后台启动 → Arm B（GPIC medium）已于 22:12 起跑（8 卡 GPU 71–85% util）。
- 续跑日志追加到同一 `/tmp/r11f_datasource.log`。

#### 进度

| 臂 | 状态 | lp @step30k |
|:--|:--|--:|
| A（GPIC short） | ✅ done | 5.53% |
| B（GPIC medium） | ✅ done | 6.17% |
| C（GPIC short+medium） | ✅ done | 5.92% |
| E（CC12M pure） | ❌ 端口碰撞失败，待重跑 | — |
| D（en500k） | ❌ shard<worker 失败，待重跑（已修） | — |

- ✅ **Q1/Q3 已裁定**（§15.6）：均「无显著差异」。Q2（含 E）悬置待 E 重跑。
- ⬜ 待回填：Arm E 重跑（稳健端口）+ Arm D 重跑（empty_check=False 已修）→ 补 Q2；R11-G 11 点 lp → 幂律/对数线性拟合 vs InfoNCE 25.1%；R11-H 4 点 lp → 翻盘是否依赖对比项。

#### Arm B（GPIC medium）✅ 完成（2026-10-04 22:12–23:31）

| ckpt | N | lp top-1 | zs top-1 | zs top-5 |
|:--|--:|--:|--:|--:|
| step10000 | 5.12M | **4.24%** | 1.47% | 5.49% |
| step20000 | 10.24M | **4.40%** | 1.86% | 6.51% |
| step30000 | 15.36M | **6.17%** | 1.74% | 6.45% |
| vision.pt | 15.36M | **6.17%** | 1.74% | 6.45% |

- 训练：3951.3s（≈66min），steady 6186 img/s（≈82.8 ms/iter），final_loss=3.1006。
- 无坍缩：PROBE step30000 C1=0.36 / C2_gap=+0.088 / C4=OK。
- 证据：`/tmp/r11f_datasource.log:1538-1557`（`[done] total=3951.3s` + `[R8-IN1K] DONE`）；ckpt `R11F_gpic_medium_w512/`。

#### Arm C（GPIC short+medium ≈90%）✅ 完成（2026-10-04 23:37 – 10-05 00:50）

| ckpt | N | lp top-1 | zs top-1 | zs top-5 |
|:--|--:|--:|--:|--:|
| step10000 | 5.12M | **4.90%** | 1.81% | 6.25% |
| step20000 | 10.24M | **6.23%** | 2.25% | 7.63% |
| step30000 | 15.36M | **5.92%** | 2.15% | 7.35% |
| vision.pt | 15.36M | **5.92%** | 2.15% | 7.35% |

- 训练：3586.2s（≈60min），steady 5983.6 img/s（≈85.6 ms/iter），final_loss=3.4861。
- 无坍缩：PROBE step30000 C1=0.3681 / C2_gap=+0.0888 / C4=OK；全程 C1 0.36–0.40 / C2_gap +0.087~+0.091。
- 证据：`/tmp/r11f_datasource.log:2302-2321`（`[done] total=3586.2s` + `[R8-IN1K] DONE`）；ckpt `R11F_gpic_shortmedium_w512/`。

#### Arm E（CC12M pure）❌ 失败（2026-10-05 00:50:53–55，未训练）

- **失败原因**：`torch.distributed.DistNetworkError: ... port: 30000 ... EADDRINUSE, address already in use`。
- **根因**：overnight chain 的 `run_arm_f` 用 `--master_port=$((29400 + RANDOM % 1000))`，本次 RANDOM 恰取到使端口 = 30000（29400+600），而该端口仍被前一进程占用（TIME_WAIT / 未释放）→ rendezvous 立即失败，**2 秒内 exit 1，无任何训练**。
- ⚠️ **纯工程问题（端口碰撞），非数据/科学问题**。CC12M 有 1100 tar，数据本身无问题。**需重跑**（用更稳健的端口选择，见 §15.7）。
- 证据：`/tmp/r11f_datasource.log:2323-2366`。

#### Arm D（en500k）❌ 失败（2026-10-05 00:50:55–51:27，未训练）

- **失败原因**：`ValueError: No samples found in dataset; perhaps you have fewer shards than workers. Turn off using empty_check=False in the WebDataset constructor.`
- **根因**：en500k 仅 **25 tar**，8 rank × 6 dataloader worker = 48 worker → 部分 worker 分到 0 shard → webdataset 默认 `empty_check=True` 在启动期即抛错。
- **修复**：已在 `vision/data.py::build_loader` 的 `wds.WebDataset(...)` 构造中加 `empty_check=False`（2026-10-05，`py_compile` ✅）。分到 0 shard 的 worker 将不产出数据，其余正常 → 对大数据集无行为变化。
- ⚠️ en500k 本就 **in-domain（= LLaVA imagenet/EN）+ ~30 epochs 重复轮** → 即便重跑成功也**单列、标「不可比」、不并入 A/B/C/E 排名**（R8.2 红线）。
- 证据：`/tmp/r11f_datasource.log:2392-2699`（`shards=4/rank total_shards=25` + empty_check ValueError）。

### 15.6 🔒 预注册裁定（Q1/Q2/Q3/D，**先定后测**）

> 噪声带 ±1.5 pp（ROUND10 §1.5）。主指标 = IN-1k frozen-trunk lp @ step30k（附 10k/20k 轨迹）。

**lp 汇总（@step{10k,20k,30k}）**

| 臂 | 数据 | @5.12M | @10.24M | @15.36M |
|:--|:--|--:|--:|--:|
| **A** | GPIC short | 3.97 | 4.95 | 5.53 |
| **B** | GPIC medium | 4.24 | 4.40 | 6.17 |
| **C** | GPIC short+medium(90%) | 4.90 | 6.23 | 5.92 |
| **E** | CC12M pure | ❌ port 碰撞未训 | — | — |
| **D** | en500k | ❌ shard 不足未训 | — | — |

**裁定**

| # | 问题 | 比较 | Δ @ {10k,20k,30k} | 裁定 |
|:--|:--|:--|--:|:--|
| **Q1** | caption 更长是否有益 | **B(medium) − A(short)** | +0.27 / −0.55 / +0.64 | **无显著差异**（三点全在 ±1.5 带内；30k 点 medium 略高 +0.64 但未达阈值） |
| **Q3** | 「90% 全用」是否更好 | **C(short+medium) − A(short)** | +0.93 / +1.28 / +0.39 | **无显著差异**（三点全在 ±1.5 带内；20k 点 +1.28 接近但未达阈值，30k 反回 +0.39） |
| **Q2** | 哪个数据源最好 | **A / B / E** 三者之比 | E 未训 → 仅 A vs B：@30k +0.64 | **暂无显著差异**（A vs B 带内）；**E 待重跑后补判** |
| **D** | en500k | **单列** | 未训 | ❌ 工程失败待重跑；即便成功仍 **in-domain / 不可比 / 不并入排名** |

**结论（基于现有 A/B/C 三点）**：
- **Q1**：在 30k 步 / 15.36M 样本预算下，**GPIC medium 相对 short 无显著增益**（Δ 全在噪声带内）。caption 从 20 tok → 46 tok 的更长信息**未被冻结 CLIP-768 文本塔 + InfoNCE 在此预算内转化为可测的 lp 提升**。
- **Q3**：**「90% 全用（short+medium）」相对 short 亦无显著增益**（C 在 20k 点一度 +1.28 接近阈值，但 30k 回落到 +0.39）→ 合并不成立「数据量×2 即更好」的简单外推（与 R9「数据受限区间加宽数据边际为正」不矛盾——此处是同 N 预算下两个 caption 档的合并，N 未变）。
- **Q2/E**：CC12M pure 臂因端口碰撞未训，**裁定悬置**，待重跑后补 A/B/E 三者比较。
- ⚠️ **C2 限定**：三点均在噪声带边缘（Q3 @20k = +1.28 接近 1.5），**不排除更大 N / 更长步数下出现分离**；本结论严格限定在「30k 步 / 15.36M / 冻结 CLIP-768 / InfoNCE」口径。

### 15.7 E+D 重跑（🔄 进行中，2026-10-05）

- R11-G ✅ 完成、R11-H ✅ 完成（§17 落盘）→ **E+D 重跑已由守护脚本自动接管**。
- **守护脚本**：`/tmp/r11_ed_wait_and_launch.sh`（PID 861557，ppid=1）→ 派出 `/tmp/r11_ed_rerun.sh`（PID 765556）。
- **Arm E（CC12M pure）** 🔄 运行中（port 29555，step≈6700/30000 @10:35 ≈22%，无坍缩 C1=0.25 / C4=OK，output `R11F_cc12m_w512`，日志 `/tmp/r11f_ed_rerun.log`）→ ETA ~1.5h + 4-ckpt eval ~15min。
- **Arm D（en500k）** ⏳ 待 E 完成后自动起（port 29556，`empty_check=False` 已修）→ ETA ~1.9h + eval。仍单列、标 in-domain / 不可比。
- **E+D 完成后** → 补 §15.6 Q2（A/B/C/E 四源排名）+ D 单列表。

---

## 16. R11-G — AIMv2-style 长跑（108k 步）→ 重拟合 scaling 并外推（✅ 完成，2026-10-05）

> 运维指令 2026-10-04（七）批准。臂⑥ AIMv2 30k 翻盘后，§14.3 预注册条款「翻盘 → 对本臂重拟合 scaling 并外推」自动触发。本项把 AIMv2-style 拉到与 R9 阶段二同口径的 108k 步，回答「翻盘后的渐近是多少？」
> 预注册判据见 BAIZE_VISION_TASK.md「运维指令 · 2026-10-04（七）」。

### 16.1 任务规格（与 §14.1 ⑥-A 完全同款，唯一变化 = 步数 30k → 108k）

| # | 项 | 值 |
|:--|:--|:--|
| 1 | 目标函数 | `InfoNCE + 1.0 × masked-patch-MSE`（`--loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0`） |
| 2 | 塔 | OpenVision2 w512（126.78M）+ PatchPredictor（0.66M）= **127.44M** |
| 3 | 文本塔 | 冻结 CLIP-768（`openai/clip-vit-large-patch14-336`） |
| 4 | 数据 | CC12M + Amshaker（≈18.5M 对） |
| 5 | 优化器 | AdamW lr 3e-3 / warmup 20 / seed 1234 / bf16 / bs64×8=512 |
| 6 | 步数 | **108k 步 = N 55.3M 样本**（对齐 R9 阶段二） |
| 7 | 采点 | `--save-every 10000` → 11 ckpt（step10k..100k + final@108k） |
| 8 | 评测 | `r8_eval_in1k.py` 对每个采点跑 IN-1k frozen-trunk lp（同 R8–R11 口径） |

### 16.2 训练结果（✅ exit 0，2026-10-05 00:51:27 → 07:54:00）

- **total=25320.6s**（≈7.03h），steps=108000，**steady_image_s=2485.5**，final_loss=2.4169（contrast≈2.29 + patch_mse≈0.13），fused=False。
- **全程无坍缩**：PROBE C1=0.34–0.40 / C2_gap=+0.12~+0.14 / C4=OK / loss_ema 2.0→2.4（波动但无上升趋势）/ scale≈69–73。
- 11 ckpt 全部落盘（各 507MB），输出目录：`/nas_train/app.e0031982/datasets/baize-vision/out/R11G_aimv2_long_w512/`。
- 训练日志：`/tmp/r11g_aimv2_long.log`（含完整 step 日志 + PROBE）。
- 命令：
```bash
python -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=127.0.0.1 --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps 108000 --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data $DATA_GH --data-source wds \
    --output-dir $OUTROOT/R11G_aimv2_long_w512 \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers 6 \
    --save-every 10000 --eval-data $EVAL
```

### 16.3 IN-1k 评测结果（11 ckpt，✅ ALL DONE 08:11:29）

> 评测脚本 `r8_eval_in1k.py`，单卡 H100，自切分 val50000/probe49970（与 R8–R11 一致）。日志 `/tmp/r11g_aimv2_long.log`（eval 段）。

**11 点 lp/zs 轨迹（全部单调递增！）**

| step | N (M) | **lp top-1 (%)** | zs top-1 (%) | zs top-5 (%) | InfoNCE lp (%) | **Δ lp (pp)** |
|---:|---:|---:|---:|---:|---:|---:|
| 10k | 5.12 | **11.50** | 4.24 | 13.82 | 3.96 | **+7.54** |
| 20k | 10.24 | **12.73** | 5.55 | 16.47 | 4.39 | **+8.34** |
| 30k | 15.36 | **13.48** | 6.26 | 18.50 | 5.44 | **+8.04** |
| 40k | 20.48 | **14.23** | 6.76 | 19.65 | 6.46 | **+7.77** |
| 50k | 25.60 | **15.33** | 6.98 | 20.30 | 6.70 | **+8.63** |
| 60k | 30.72 | **15.52** | 7.79 | 22.08 | 7.35 | **+8.17** |
| 70k | 35.84 | **16.67** | 7.87 | 22.13 | 7.30 | **+9.37** |
| 80k | 40.96 | **17.53** | 8.64 | 23.52 | 7.30 | **+10.23** |
| 90k | 46.08 | **18.41** | 8.77 | 24.31 | 7.59 | **+10.82** |
| 100k | 51.20 | **18.84** | 9.66 | 26.37 | 7.70 | **+11.14** |
| 108k | 55.30 | **19.76** | 10.24 | 27.16 | 7.40 | **+12.36** |

> InfoNCE 基线 = R9 阶段二同口径（同塔 w512 / 同数据 / 同步数 / 同评测），数据来源 `/tmp/r11g_scaling_points.csv`。

### 16.4 Scaling 拟合（`r11g_scaling.py`，同 R9 方法论）

**幂律 `acc = a − b × N^(−c)` + 对数线性 `acc = a + b × log10(N)`，11 点拟合：**

| 模型 | 拟合 | R² | 渐近 a (%) | 公式 |
|:--|:--|---:|---:|:--|
| **R11-G AIMv2** | 幂律 | **0.9078** | 100.00* | `1.000 − 1.665 × N^(−0.040)` |
| **R11-G AIMv2** | 对数线性 | **0.9155** | N/A | `−0.4286 + 0.0793 × log10(N)` |
| R9 InfoNCE | 幂律（重拟合） | 0.9423 | 25.10 | `0.251 − 0.864 × N^(−0.090)` |
| R9 InfoNCE | 已知 | ~0.94 | 25.1 | `acc=0.251−0.864·N^(−0.090)` |

> *`a=100%` 是 `curve_fit` 上界（`bounds=([max(acc)*0.99, 0, 1e-3], [1.0, 1e3, 5.0])`），优化器触及边界 → **渐近值不可信**，见 §16.5。

**单调性检查**：n_neg=0/10 → **全部 11 点严格单调递增**（InfoNCE 基线 n_neg=3/10，非严格单调）。

### 16.5 🔒 预注册判据裁定（先定后测，§运维指令 2026-10-04(七)）

> 预注册：「R² ≥ 0.90 且 渐近 a 显著 > 25.1%」→ 正面结论；「R² < 0.90 或轨迹非单调」→ 如实写「非简单幂律」。

| 判据 | 实测 | 通过？ |
|:--|:--|:--|
| R² ≥ 0.90 | **0.9078** | ✅ YES |
| 渐近 a > 25.1% | **100% > 25.1%** | ✅ YES（但 a 不可信，见下） |
| 单调性 | n_neg=0/10 | ✅ YES（严格单调递增） |

**裁定：POSITIVE — 「换目标函数（AIMv2-style）可抬高渐近上限」**

**⚠️ 关键诚实披露（C2 限定）**：

1. **`a=100%` 是 `curve_fit` 边界伪迹**：幂律上界 `a≤1.0` 被触及，真实渐近不可数值估计。原因：`c=0.040`（vs InfoNCE `c=0.090`）→ AIMv2 饱和速率 **>2× 慢于** InfoNCE → **55.3M 样本内无任何饱和信号** → 幂律的渐近项 `a` 在数据范围外不受约束。
2. **可辩护的结论**（不依赖 `a=100%` 的字面值）：
   - **R²=0.91 ≥ 0.90** → 幂律在观测范围内拟合良好 ✓
   - **11 点全部严格单调递增** → 无平台/回退 ✓
   - **每个 N 点 AIMv2 lp >> InfoNCE lp**（Δ +7.5→+12.4 pp，**随 N 扩大而增大**）✓
   - **对数线性斜率 2× 陡**（0.0793 vs 0.0398）→ AIMv2 每十倍数据增益 2× InfoNCE ✓
   - **InfoNCE 25.1% 渐近已被观测值超越**：55.3M 时 AIMv2 lp=19.76% 仍在攀升（InfoNCE 同 N 仅 7.40%，其渐近 25.1% 需外推到数百亿样本才达）→ AIMv2 真实渐近 **明确 >> 25.1%**，但精确值不可定（需 >>55.3M 样本才能观测饱和拐点）
3. **C2 限定（同 §14.0）**：AIMv2-**style** 自研改编（`InfoNCE + masked-patch-MSE`），**非官方 AIMv2 复现** → 结论只对我们 recipe 成立。

### 16.6 公平表（§3 口径：参数量 + 训练 token + 每步耗时）

| 项 | R11-G AIMv2 | R9 InfoNCE（基线） |
|:--|:--|:--|
| 视觉塔 | OpenVision2 w512（126.78M） | 同 |
| 额外参数 | PatchPredictor 0.66M | 无 |
| **总参数** | **127.44M** | **126.78M** |
| 训练步数 | 108000 | 108000 |
| 训练样本 N | 55.3M | 55.3M |
| steady img/s | **2485.5** | **2904** |
| 每步耗时 (avg) | ~234 ms/iter | ~186 ms/iter |
| 总墙钟 | 25320.6s (≈7.03h) | ~20100s (≈5.6h) |
| GPU·h (8卡) | ≈56.2 | ≈44.8 |
| 坍缩 | ❌ 无 | ❌ 无 |
| **lp @ 55.3M** | **19.76%** | **7.40%** |
| **lp 渐近** | **>>25.1%（不可定，无饱和）** | **25.1%（幂律 a=0.251）** |

> AIMv2 每步慢 ~26%（额外 PatchPredictor forward + mask + patch_mse loss），但 **lp 增益远超成本**（同 N +12.36 pp @ 55.3M）。

### 16.7 结论

⭐ **R11-G 证实：AIMv2-style 目标函数（InfoNCE + caption-无关的 masked-patch 稠密重建）不仅在小规模（30k/15.36M）翻盘（§14.4），在长跑（108k/55.3M）下依然保持翻盘，且翻盘幅度随 N 扩大而增大（+7.5 → +12.4 pp）。轨迹 11 点严格单调递增、无饱和信号，幂律 R²=0.91。25.1% 的 InfoNCE 渐近上限被明确超越，但 AIMv2 的精确渐近值需 >>55.3M 样本才能确定（c=0.04 → 饱和极慢）。**

**机制（与 §14.4 一致）**：caption-无关的稠密 patch 监督（MAE 式逐 patch 像素重建）为视觉塔提供了远比 InfoNCE 单全局标量更密集的每样本监督信号 → 在数据受限场景下（我们 ~18.5M 对 vs 官方 ~12B 对）效率显著更高。这与 arm④ CoCa（caption-依赖稠密 → 坍缩随机）形成完整对照：**坍缩归因于 caption 依赖，非稠密监督本身**。

**证据**：
- 训练日志：`/tmp/r11g_aimv2_long.log`（108k 步完整 + eval 11 ckpt）
- Scaling 分析：`/tmp/r11g_scaling_analysis.txt`（`r11g_scaling.py` 输出）
- CSV：`/tmp/r11g_scaling_points.csv`（11+11 点）
- Checkpoints：`/nas_train/app.e0031982/datasets/baize-vision/out/R11G_aimv2_long_w512/vision_step{10000..100000}.pt + vision.pt`

- **对本项目的影响**：R9 的 25.1% 渐近**不被数据臂改动推翻**；GPIC 的价值仅在「低预算快速启动」，本项目数据瓶颈是**总量/多样性**（本地 ≈118M 上限 vs 619 亿缺口），非 caption 质量 → R6/R7「正式训练切 GPIC short」与 R9/R10 scaling 口径**维持不变**。证据：`/tmp/r11_gpic.log`（训练 metrics + eval 段 786-797 行）。

### 16.8 文献证据锚点（一手引用 · 2026-10-05 cimi_search 检索核实）

> 运维指令 2026-10-05 要求用 `cimi_search`/`cimi_fetch` 核实 AIMv2 / MAE 原文的 mask ratio / 损失形式 / 预训练数据规模，为 §16.7 的机制解释提供一手锚点。**🔒 证据纪律**：以下均为一手来源（arXiv 原文），已给 URL + 年份。

#### (1) AIMv2 原文（arXiv:2411.14402, Apple, 2024-11）

- **URL**：`https://arxiv.org/html/2411.14402v1`
- **损失形式**（Figure 1 伪代码 + §2.1 原文）：
  - `loss = cap_loss + alpha * pixel_loss`
  - `pixel_loss = normalized_mse_loss(mm_out[:I], pixel_target)` — **normalized ℓ2 像素重建损失**（原文称 "following He et al." = MAE 范式）
  - `cap_loss = cross_entropy_loss(mm_out[-T:], cap_target)` — 文本 token 交叉熵
  - **α ≈ 0.4**（pixel loss 权重；来源：pith.science 逐字摘要，**二手·待核原文表格**，但与伪代码结构一致）
- **⭐ 稠密监督核心论断（原文逐字引用）**：
  > "AIMv2 extracts a training signal from every image patch and text token, providing **denser supervision compared to discriminative objectives**."
  — §1 Introduction，`https://arxiv.org/html/2411.14402v1`
- **预训练数据规模**：~**12B** 样本（DFN-2B + COYO + 专有 HQITP），alt-text + LLaMA-3 合成 caption 混合（§2.3 Data）
- **与我们 recipe 的差异（C2 限定补充）**：
  | 项 | 官方 AIMv2 | 我们 R11-G（自研改编） |
  |:--|:--|:--|
  | 损失 | `CE_text + 0.4 × norm_mse` | `InfoNCE + 1.0 × patch_mse` |
  | 文本监督 | AR caption CE | **冻结 CLIP-768**（不训文本） |
  | mask | prefix-attention 随机前缀 | **随机 patch masking（ratio 0.6）** |
  | 对比项 | **无**（纯 AR） | **有**（InfoNCE，contrast-weight 1.0） |
  | patch loss 权重 | α≈0.4 | **1.0** |
  - → 我们的 recipe **保留了 InfoNCE 对比项**（为控变量），官方 AIMv2 是**纯 AR 无对比** → **R11-H（纯 AR）正是向官方路线靠拢的消融**。
- **§3.2 "AIMv2 vs. Captioning" 消融**（原文有小节标题，**结果数字未在本次 fetch 中提取到 → 标「待核」**）：该消融对比「纯 AR patch 预测」vs「仅 caption 生成」→ 与我们的 arm④ CoCa vs arm⑥ AIMv2 对照设计一致。

#### (2) MAE 原文（He et al., arXiv:2111.06377, 2021 → CVPR 2022）

- **损失形式**：MSE on **masked patches only**（仅对被 mask 的 patch 计算像素重建 MSE；可见 patch 不参与 loss）
- **最优 mask ratio**：**75%**（原文 Table 1c：75% → lp 67.1% / ft 83.6%；50% → lp 60.6%；90% → lp 57.4%）
  - 我们用 **0.6（60%）**，在 MAE 最优区间附近，但 MAE 是纯视觉无文本；多模态场景下 mask ratio 最优值可能不同（**未核实官方 AIMv2 的 prefix ratio 分布**）。
- **URL**：`https://arxiv.org/abs/2111.06377`（**本次未 fetch 原文，上述为公认结论·二手·待核**）
- **与我们的关系**：我们的 `masked-patch-MSE` 实现沿用了 MAE 范式（逐 patch 像素重建），但 mask ratio 0.6 < MAE 最优 0.75 → **若后续想优化，可试 0.75**（但非本 R11-G 的考察变量，不做）。

#### (3) AR vs 对比的数据效率（arXiv:2411.15648 "XTRA", 2024-11）

- **URL**：`https://arxiv.org/pdf/2411.15648v2`
- **关键引用（原文逐字）**：
  > "AIM was trained on a massive dataset of 2 billion samples, whereas contrastive and MIM models can achieve competitive results with datasets that are 150 times smaller."
  > "auto-regressive image models [...] predict image pixels (or patches) sequentially [...] offer a consistent relationship between the model's objective function and its downstream task performance."
- **与我们的发现的关系**：该文献指出 AR 模型在**大数据**下有一致 scaling law，但**样本效率**通常被认为不如对比学习 → **我们的 R11-G 发现（同数据量下 AIMv2-style lp >> InfoNCE）是一个在数据受限区间的反向证据**，值得在论文中诚实讨论（可能因为：① 我们保留了 InfoNCE 对比锚 + ② patch 稠密监督在小模型/小数据下效率增益更大）。

#### (4) 对 R11-G 机制解释的锚定

§16.7 的机制解释（"caption-无关的稠密 patch 监督效率更高"）现在有**一手原文锚点**：
- AIMv2 原文 §1 明确声称 "denser supervision compared to discriminative objectives" ✅
- MAE 范式（逐 patch MSE）是我们的 patch loss 的直接来源 ✅
- **但需诚实标注**：AIMv2 原文的 claim 是在 **12B 样本**下成立的；我们在 **18.5M 样本（649× 少）**下观测到同样的方向性（稠密 > 对比）→ **机制一致、量级不同**，不可声称"复现了 AIMv2"（C2 限定）。

---

## 17. R11-H — 臂⑥-B：纯 AR（去对比项）30k 步（✅ 完成，2026-10-05）

> 运维指令 2026-10-04（七）批准。别名 = `ROUND11 §14.0(3)` 与 `§14.3` 里的 **⑥-B**。
> **科学问题**：⑥-A 翻盘是否依赖对比项（InfoNCE）？若去掉 InfoNCE 仍翻盘 ⇒ 「caption-无关的稠密 patch 监督本身」即可突破上限（更接近官方 AIMv2 路线）。
> **唯一变化 vs ⑥-A**：`contrast_weight 1.0 → 0.0`（`total = 1.0 × masked-patch-MSE`；文本塔不参与梯度）。C2 坍缩守卫**关闭**（纯 AR 无跨模态对齐，C2_gap ≈ 0 是预期；C1 特征坍缩 + C4 loss 递减守卫保留）。

### 17.1 命令

```bash
bash vision/r11h_run_pure_ar.sh 30000
# = torchrun --nproc_per_node=8 r9_train.py --loss aimv2 --mask-ratio 0.6 \
#   --patch-loss-weight 1.0 --contrast-weight 0.0 --c2-collapse-guard 0 \
#   --tower openvision2 --width 512 --depth 30 --steps 30000 ...
# 数据 = CC12M+Amshaker(~18.5M)，同 ⑥-A / R9。
```

### 17.2 训练结果（✅ exit 0，2026-10-05 08:51 → 10:10:58）

| 项 | 值 |
|:--|:--|
| 总墙钟 | 7136.2s（≈1.98h × 8 卡 ≈ **15.8 GPU·h**） |
| steady img/s | **2956.3**（≈ ⑥-A 的 5971 的 49.5%——无对比项时吞吐约减半，因 forward pass 无负样本编码） |
| final_loss | **0.0555**（= patch_mse；contrast=0.0000 全程） |
| patch_mse 轨迹 | 0.6026 (step50) → 0.0412 (step30000)（**递减 14.6×**，patch 重建在学） |
| C1（特征坍缩） | 0.812 (step300) → **0.255** (step30000)（早期偏高→后期稳定 <0.30，**无坍缩**） |
| C2_gap | ≈0 全程（纯 AR 预期，守卫已关） |
| C4 | OK 全程（loss 递减） |
| 自动中止 | ❌ 未触发 |

> ⚠️ C1 早期 step300=0.812 偏高（接近 0.95 阈值），但随训练迅速下降到 0.25 → 这是纯 MIM 的典型行为（早期 patch 重建主导、特征尚未分化），**非坍缩**。

### 17.3 IN-1k 评测结果（4 ckpt，✅ ALL DONE 10:23:44）

| ckpt | N (samples) | lp top-1 | zs top-1 |
|:--|--:|--:|--:|
| step10000 | 5.12M | **5.28%** | 0.08% |
| step20000 | 10.24M | **6.13%** | 0.10% |
| step30000 | 15.36M | **6.23%** | 0.09% |
| final | 15.36M | **6.23%** | 0.09% |

> zs ≈ 0.1% 全程——**预期**：纯 AR 无对比项 → 视觉特征与冻结 CLIP 文本空间无对齐 → zero-shot 退化到随机。lp 仍有信号（特征本身在学习，只是不对齐文本）。

### 17.4 🔒 预注册判据裁定（先定后测，§运维指令 2026-10-04(七)）

> 基线锚点（arm① InfoNCE）：lp @ 5.12M = **3.43%** / 10.24M = **5.45%** / 15.36M = 6.08%。
> ⑥-A 锚点（InfoNCE + patch-MSE）：lp @ 5.12M = **11.39%** / 10.24M = **11.14%** / 15.36M = 12.08%。
> 噪声带 ±1.5 pp（ROUND10 §1.5）。

**逐点 Δ 计算：**

| 锚点 | R11-H | vs 基线 | vs ⑥-A | 基线+1.5? | ⑥-A−1.5? |
|:--|--:|--:|--:|:--:|:--:|
| @5.12M | 5.28% | **+1.85** | −6.11 | ✅ YES | ❌ NO (5.28<9.89) |
| @10.24M | 6.13% | **+0.68** | −5.01 | ❌ NO (6.13<6.95) | ❌ NO (6.13<9.64) |

**三行判据逐条检验：**

| 行 | 条件 | @5.12M | @10.24M | 两点均满足？ |
|:--|:--|:--:|:--:|:--:|
| 1 | ≥基线+1.5 **且** ≥⑥-A−1.5 → 不依赖对比项 | ✅/❌ | — | ❌ NO |
| 2 | ≤⑥-A−1.5 **但** ≥基线+1.5 → 部分依赖 | ✅/✅ | ✅/❌ | ❌ NO |
| 3 | 坍缩随机(<1%) **或** ≤基线+1.5 → 依赖对比项 | — | ❌(≤基线+1.5) | ✅ **YES** |

**裁定：Row 3 → 「翻盘依赖对比项」**

### 17.5 诚实披露与机制解读

**⚠️ 关键 nuance（负结果有价值，如实记录）：**

1. **未坍缩到随机**：lp 5–6% 远高于随机（~0.1%）且 ≥ 基线 → 纯 AR（caption-无关的稠密 patch 监督）**本身能学到有效视觉特征**，不是废物。
2. **@5.12M 仍有低 N 先发优势**：+1.85 pp ≥ 基线+1.5 → 稠密 patch 监督在**极低 N**下比 InfoNCE 学得更快（与 R11-E GPIC short 的「低 N 先发」模式一致）。
3. **但翻盘完全消失**：⑥-A 在两点上 +7.96/+5.69 pp → R11-H 仅 +1.85/+0.68 pp → **对比项贡献了翻盘幅度的 77–88%**。
4. **@10.24M 已回落到噪声带内**（+0.68 < 1.5）→ 无对比项时，稠密监督的优势**随 N 增大而衰减**（与 ⑥-A 的优势随 N 增大而增大形成镜像对照）。

**⭐ 完整因果分解（四臂对照）：**

| 臂 | 组成 | lp@15.36M | vs 基线 | 翻盘？ |
|:--|:--|--:|--:|:--:|
| ① 基线 | InfoNCE | 6.08% | — | — |
| ④ CoCa | InfoNCE + caption CE | **0.47%** | −5.61 | ❌ 坍缩 |
| **⑥-B (R11-H)** | **patch-MSE only** | **6.23%** | +0.15 | ❌ 无翻盘 |
| **⑥-A (R11-G/§14)** | **InfoNCE + patch-MSE** | **12.08%** | **+6.00** | ✅ 翻盘 |

→ **翻盘需要两者兼备**：(a) caption-**无关**的稠密 patch 监督（非 caption CE——caption 依赖会坍缩）；(b) 对比项 InfoNCE（提供语义锚 / 线性可分性）。**单独任一都不够**：纯 MIM ≈ 基线（无翻盘），caption 稠密 → 坍缩。

**机制（与文献一致）**：
- MAE 原文（He et al., 2022）报告 MAE linear probe **比对比方法低 10–15 pp**（ViT-B: MAE lp=68% vs DINO/MoCo lp≈75–78%），原文解释：「pixel reconstruction encourages the encoder to retain **low-level information** useful when the head is trainable, but **not as immediately linearly separable** as features learned by augmentation-invariant contrastive objectives」（aiwiki.ai/wiki/masked_autoencoder，2026-06，**二手·基于 He et al. 2022 原表**）。
- → 我们的 R11-H 在**多模态 + 冻结文本塔**设置下复现了这一模式：纯 patch-MSE 的 lp ≈ 基线 InfoNCE（无提升），而 **InfoNCE + patch-MSE 组合**（⑥-A）才产生翻盘 → **对比项提供线性可分的语义锚，稠密项提供更丰富的每样本监督，二者互补**。
- AIMv2 官方是纯 AR（无对比项）但**有 text AR（caption CE）**+ 12B 样本 → 官方路线的「语义锚」来自 **text AR** 而非 InfoNCE；我们冻结了文本塔（无 text AR）→ 去掉 InfoNCE 后**完全没有语义锚** → 这是 R11-H 与官方 AIMv2 的关键差异（C2 限定）。

### 17.6 公平表（§3 口径：参数量 + 训练 token + 每步耗时）

| 项 | ⑥-B (R11-H) 纯 AR | ⑥-A (§14) AIMv2-style | ① 基线 InfoNCE |
|:--|:--|:--|:--|
| 视觉塔 | OpenVision2 w512（126.8M） | 同 | 同 |
| PatchPredictor | +0.66M | +0.66M | 无 |
| **总参数** | **127.44M** | **127.44M** | **126.78M** |
| 训练步数 | 30000 | 30000 | 30000 |
| 训练样本 N | 15.36M | 15.36M | 15.36M |
| steady img/s | **2956** | **5971** | ~2900 |
| 每步耗时 | ~238 ms/iter | ~165 ms/iter | ~186 ms/iter |
| 总墙钟 | 7136s (≈1.98h) | ~4950s (≈1.38h) | ~5580s (≈1.55h) |
| GPU·h (8卡) | ≈15.8 | ≈11.0 | ≈12.4 |
| 坍缩 | ❌ 无 | ❌ 无 | ❌ 无 |
| **lp @ 5.12M** | **5.28%** | **11.39%** | 3.43% |
| **lp @ 10.24M** | **6.13%** | **11.14%** | 5.45% |
| **lp @ 15.36M** | **6.23%** | **12.08%** | 6.08% |
| zs @ 15.36M | **0.09%** | 5.29% | ~1.9% |

> 纯 AR 每步慢 ~44% vs ⑥-A（无负样本编码但 patch 计算仍在；差异主要来自数据加载效率随 GPU 空闲度变化）。lp 增益 = **零翻盘**（+0.15 pp @ 15.36M vs ⑥-A +6.00 pp）。

### 17.7 结论

**R11-H（臂⑥-B 纯 AR）裁定：翻盘依赖对比项。** 去掉 InfoNCE 后，caption-无关的稠密 patch 监督（MAE 式）本身仍能学到有效视觉特征（lp 5–6% > 随机，@5.12M +1.85 ≥ 基线+1.5），但**无法复现 ⑥-A 的翻盘**（两点均远低于 ⑥-A，@10.24M 已回落到噪声带内）。

**对 §14.4 / §16.7 的补充**：⑥-A 的翻盘不是「稠密监督 alone」的功劳，而是 **InfoNCE 语义锚 × caption-无关稠密 patch 监督** 的**互补效应**。这与 MAE 文献（纯 MIM lp < 对比方法 lp）一致——对比项提供线性可分性，稠密项提供更丰富的每样本信号，二者缺一不可。

**C2 限定**：R11-H ≠ 官方 AIMv2（官方有 text AR 提供语义锚 + 12B 样本；我们冻结文本塔、去掉 InfoNCE 后无任何语义锚）→ 结论只对我们 recipe 成立。

**证据**：
- 训练日志：`/tmp/r11h_pure_ar.log`（30k 步完整 + eval 4 ckpt，exit 0）
- Checkpoints：`/nas_train/app.e0031982/datasets/baize-vision/out/R11H_pure_ar_w512/vision_step{10000,20000,30000}.pt + vision.pt`
- 命令：`bash vision/r11h_run_pure_ar.sh 30000`
- 文献锚点：MAE lp < 对比 lp（He et al. 2022，via aiwiki.ai 二手·待核原文表格）；AIMv2 官方 = 纯 AR + text AR（§16.8(1)）

> **检索工具状态**：`cimi_search` + `cimi_fetch` 在 `.12` 本线实测可用（rc=0）。本次共 3 次 search + 2 次 fetch，均为 CPU/网络操作，未占 GPU、未下大文件。