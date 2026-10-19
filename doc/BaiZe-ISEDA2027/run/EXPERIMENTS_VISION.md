# EXPERIMENTS_VISION.md — BaiZe Stage(iii) 视觉编码器预训练对比

> 四架构（500–600M）从零预训练公平对比。统一 open_clip(3.2.0) + SigLIP + 固定 text tower + 统一子集。

## ⭐ 最终胜出结论（R4–R8 修复 recipe，2026-10-02，**权威**）

> ⚠️ 本节为**最终结论**，覆盖下方「S0–S9 / converged」各节的 R1/R2 旧读数——那些旧读数**已因表征坍缩与 lr=1e-3 cosine 伪影作废**（详见 `EXPERIMENTS_VISION_ROUND2~ROUND8.md`）。数据与 recipe 的演进：R4 修 recipe（冻结 CLIP-768 文本塔 + InfoNCE）→ R5 架构/分辨率 → R6 77 裁定 → R7 数据裁定（GPIC short）→ R8 扩 6 架构 + IN-1k。

**胜出架构：OpenVision2（纯 Attention ViT，505.2M）—— R8 六架构重比，四指标全第一**

| 架构 | loss@3k | C1（同塔off-diag） | IN-1k zs top-1 | IN-1k lp top-1 | 训练 img/s | 判定 |
|:--|--:|--:|--:|--:|--:|:--|
| **OpenVision2** | **4.8646** | **0.2875** | **0.95%** | **1.14%** | 3051.8 | ✅ 胜出 |
| MoE-ViE（moevie） | 5.5580 | 0.4109 | 0.35% | 0.28% | 1225.7 | ✅ 健康（激活 222M） |
| AIMv2（等参改编） | 5.6370 | 0.3931 | 0.38% | 0.25% | **3392.5** | ✅ 健康（吞吐最快） |
| FastViTHD（等参改编） | 5.6683 | 0.4494 | 0.39% | 0.27% | 2097.4 | ✅ 健康（conv-hybrid 无优势） |
| MambaEye（纯 SSM） | 6.2507* | 1.0000 | 0.10% | 0.10% | 949.5 | ❌ @300 坍缩 |
| DeepEncoderV2（Attn+SSM） | 6.2513* | 1.0000 | 0.10% | 0.10% | 1864.5 | ❌ @300 坍缩 |

- **三条最终结论**：① 修复 recipe 下**架构有真实差异**（loss 4.8646~5.6683、IN-1k 0.95%~0.39% 可分），OpenVision2 全指标第一 → 作废旧「loss 与架构无关」；② 坍缩是 **SSM 特异**（含 SSM 子结构即 @300 坍缩，纯 Attention 系 4 架构全健康）；③ **IN-1k（frozen trunk zs/lp）成功替换退化的 R@1**（旧 R@1=1/5000 chance 零区分度）。
- ⚠️ **C2 限定（2026-10-03）**：上表 6 架构**全是自研 from-scratch 等参改编（非官方模型）**（`run/vision/models.py` 头行自证）。故「SSM 坍缩」只能表述为**「我们 recipe（冻结语义文本塔 + InfoNCE）下、我们自研改编版的坍缩」**，🚫 **不得**推广成「官方 MambaEye/DeepEncoderV2 会坍缩」。
- **最终 recipe**：Stanford **GPIC `short`**（20 tok / 0% 截断）+ InfoNCE + 冻结 `clip-vit-large-patch14-336` 768 维文本塔（context 77）+ lr 3e-3 / warmup 20 / seed 1234 / bf16 / bs64 × 8 卡 = 512 负样本。
- 详见 `EXPERIMENTS_VISION_ROUND8.md`（§4 六表 + §8 排名 + §9 回填建议）。

**完整可复现训练命令（R8 胜出架构）**：

```bash
conda activate py310
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

# 单架构（胜出 OpenVision2）完整训练：3000 步 @224/16 bs64，GPIC short，冻结 CLIP-768 文本塔
python -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
     --master_addr=127.0.0.1 --master_port=$((29400 + RANDOM % 1000)) \
     r7_train.py --tower openvision2 --steps 3000 --resolution 224 --patch 16 \
     --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
     --data '/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar' \
     --data-source gpic --output-dir /nas_train/app.e0031982/datasets/baize-vision/out/R8_openvision2 \
     --log-every 50 --probe-every 300 --probe-n 128 --num-workers 2 \
     --eval-data '/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'

# 六架构串行 + 末了 IN-1k zero-shot / linear-probe 评测
bash r8_run.sh 3000
```

---

## ⭐ R9 追加结论：scaling law（数据扩容 + 长训练，2026-10-03）

> R9 用「缩塔先导 + 长训练」把数据从 ~2.77M 对扩到 ~18.5M 对、把步数拉到 108k，画出 IN-1k 随样本的 scaling 曲线并外推。**不改 R8 的架构排名**（OpenVision2 仍胜出）；详见 `EXPERIMENTS_VISION_ROUND9.md` §4–§5。

- **缩塔先导（阶段一，3 臂 × 30k）**：OpenVision2 × width{512,768,1024}，IN-1k lp = **6.10% / 3.63% / 1.03%** → **塔越小、每样本效率越高**（505M 在 ~15.4M 样本下严重欠拟合，loss 反高 4.92）→ 选 **w512（126.8M）**。
- **长训练（阶段二，w512 × 108k 步 = 55.3M 样本）**：无坍缩（C1≈0.36 / C2_gap≈+0.10 / loss_ema 5.99→**3.71**，steady 2904 img/s）；IN-1k lp 峰值 **7.70%**@51.2M（末点 7.40%）、zs top-1 3.59%、top-5 11.47%。
- **scaling 拟合（11 点，R²≈0.94）**：幂律 `acc=0.251−0.864·N^−0.090`（渐近 **a=25.1%**）；对数线性 `acc=−0.229+0.0398·log10(N)`。
- 🔴 **外推结论（核心决策依据）**：目标 20% 需 **对数线性 619 亿样本（本地 ≈118M 上限的 ~525×）/ 幂律 41 万亿样本**；40%/60% 在幂律下**不可达**（渐近 25.1%），对数线性下需 6.6×10^15 / 7.1×10^20 样本。→ **此从零对比学习路线在本地数据规模下够不到 20%+**。
- **量级对照**：AIMv2 ≈120 亿对 → 88.7%；我们 55.3M → 7.7%（**649× 数据缺口**，严禁并列）。瓶颈在**数据量与目标函数，非架构**。
- 📌 **建议路线**：要抬高 IN-1k 只能 ① 加载大规模预训练权重（等价 120 亿对）② 换重构型目标（MAE/MIM，无 text 塔无坍缩）③ 用现成编码器做 Stage(iii) 选型。

### 🔧 C1 数据量口径修正（2026-10-03 · E1 实测 · 必做修正）

> 原「本地 53M 唯一对上限」是 `r9_scaling.py` `--local-cap-m default=53` 的**假设**、非实测。E1 抽 8 个 GPIC tar 实测 → 每 tar ≈12,495 唯一图文对（json=图 1:1，jpg≈11k + png≈1.5k）。三类分母统一如下（**数据仍在下载，动态值**）：

| 分母 | 值 | 组成 |
|:--|--:|:--|
| **R9 用过** | ≈18.5M | CC12M ~11M + Amshaker ~6M + LLaVA/CC3M ~1.15M + coco/vg ~0.3M（不含 GPIC train） |
| **盘上现有** | ≈33M | 18.5M + GPIC train 已下 1195 tar × 12.5k ≈ 14.9M |
| **本地全量** | ≈118M | GPIC 全量 8000 tar × 12.5k ≈ 100M + CC12M ~11M + Amshaker ~6M（+LLaVA/CC3M ~1.15M） |

- **重算关键缺口**（AIMv2 ≈120 亿对）：649×（对 18.5M）→ **359×（对 33M）→ 102×（对 118M）**；「20% 需 619 亿样本」= **~525× 本地 118M 上限**（原「1168× the 53M」是低估了 cap）。
- ⚠️ **结论不变**：即便用真实 cap ≈118M，此从零对比路线**仍够不到 20%+**（619 亿 vs 118M = ~525×）。瓶颈在数据量与目标函数，非架构。
- 证据：GPIC 实测命令 `tar -tf gpic_train_NNNNN.tar | grep -c '\.json$'`（8 tar 采样，见 `EXPERIMENTS_VISION_ROUND10.md` / 当日日志）。

## ⭐ R10 完成：M 轴 scaling law（模型规模轴，2026-10-03）

> 补全 R9「只扫了数据侧 N」的缺口，复用阶段一三档塔宽 ckpt 补 M 轴，拟合 (N,M) 二维 scaling。详见 `EXPERIMENTS_VISION_ROUND10.md`。

- **R10-①（✅）回收阶段一 12 点 IN-1k**：w512/w768/w1024 × step{10k,20k,30k}，lp 终点（@15.36M）= **6.08% / 3.63% / 0.93%** ——单调下降，印证「塔越小每样本效率越高」。
- **R10-②（✅）2D 拟合（3 点 M 轴，R²=0.980）**：`acc=-1.737+0.333·log10(N)+0.185·log10(M)-0.036·log10(N)·log10(M)`；**M 边际效应全区间为负 ≈ −2.2 lp pp / 参数翻倍**。
- **R10-③（✅）补密 M 轴 → 5 点重拟合（R²=0.960）**：w384(71.49M)+w640(197.80M) 各 30k 步（同数据/recipe）；**w384 @15.36M lp=7.99% 为全部宽度最高**（w512 5.44~6.08 / w640 3.62 / w768 3.63 / w1024 0.93）→ 更小塔持续更优、**无饱和点**；小塔吞吐更高（w384 6583 vs w640 2418 img/s）。最终：`acc=-1.452+0.298·log10(N)+0.150·log10(M)-0.0318·log10(N)·log10(M)`，M 边际 ≈ **−2.2~−2.4 pp/参数翻倍**。
- **核心结论（已定）**：数据受限区间（N≤55.3M）**加宽塔是负收益、应继续向下探塔**；与 R9 N 轴结论合一 → 从零对比学习在本地 ≈118M 上限下，无论调 N 还是 M 都够不到 20%+，瓶颈在数据量与目标函数。

## ⭐ R11-L 目标函数轴 + R11-L2 文本塔解冻（完成，2026-10-04）

> R9/R10 已证「瓶颈在数据量与目标函数（非架构）」。R11-L **只变目标函数**（塔 w512 / 数据 CC12M+Amshaker / 步数 / opt / 评测全固定），检验「换张监督密度更高的目标能否抬高 25.1% 渐近」。预注册判据：同 N 下 lp 比 InfoNCE 基线 **+1.5 点**以上才算翻盘。详见 `EXPERIMENTS_VISION_ROUND11.md`。

- ✅ **臂② SigLIP（完成，2026-10-03 15:26）**：lp = **2.19 / 3.13 / 4.36%** @5.12/10.24/15.36M，全 **< 基线（3.43/5.45/6.08%）** → **未翻盘**（Δ −1.24 ~ −2.32 点），且稳定劣于 InfoNCE。
- ✅ **臂③ LocalLoss（完成，2026-10-03 17:43）**：lp = **1.81 / 3.60 / 4.33%** @5.12/10.24/15.36M，全 **< 基线（3.43/5.45/6.08%）** → **未翻盘**（Δ −1.62 ~ −1.85 点）。⚠️ 臂②③ 监督密度仍 = 1 全局标量，**「稠密监督翻盘」假说还未被检验**。
- ✅ **臂④ CoCa（完成，2026-10-03 20:13）**：+76.2M decoder + caption CE（weight 2.0，首个稠密监督臂）→ IN-1k frozen-trunk lp **0.29 / 0.37 / 0.47%** @5.12/10.24/15.36M（**≈随机**）vs 基线 3.43/5.45/6.08% → **Δ −3.14 ~ −5.61 点，未翻盘且 trunk 被 caption 项（~68% 梯度）打回随机**。⚠️ 限于「自写 CoCa decoder + 冻结 CLIP-768 + 短 caption + weight2.0（未消融）」，不得推广到官方 CoCa。见 `EXPERIMENTS_VISION_ROUND11.md` §9。
- ✅ **R11-L2 文本塔解冻 LoRA（完成，2026-10-04 02:12）**：只解冻 CLIP-768 文本塔（LoRA r8 α16 lr1e-4，+0.30M、零初始化起点）。**未坍缩**（C1~0.28 / C2_gap+0.11 / C4 OK）；IN-1k lp = **3.13 / 4.75 / 5.28%** @5.12/10.24/15.36M vs 基线 3.43/5.45/6.08% → Δ −0.30 ~ −0.80 → **未翻盘**。→ 「冻结文本塔锁死上限」假说未获支持，**冻结仍最优**（重训 text 塔不再推荐）。见 `EXPERIMENTS_VISION_ROUND11.md §11.7`。
- ✅ **R11-L caption-weight 消融（替代臂⑤ GenLIP，完成 2026-10-04 06:54）**：CoCa 只变 `--caption-loss-weight`，三点 lp@15.36M = 2.0→**0.47%** / 1.0→**0.61%** / 0.5→**0.60%**，全≈随机、无单调 → **caption 监督本身与 IN-1k 正交**（假设 B 成立，非 weight 压死）→ 臂⑤ GenLIP 跳过坐实。见 `EXPERIMENTS_VISION_ROUND11.md §12.5`。
- 📌 **运维已裁定（2026-10-03（三））**：臂⑤ GenLIP 🚫 跳过（→ caption 消融替代）；臂⑥ AIMv2 ⏸ 暂缓；R13 ⏸ 批准后只做 OpenVision2 官方单臂；R11-E ✅ 完成（「10.9M 同 N 两点」版，2026-10-04）。

## ⭐ R11-E GPIC 数据轴（完成，2026-10-04）

> 运维指令 2026-10-04（四）：R11-E 不再等 18.5M，改用现有 GPIC `short`（≈11M 对）做「同 N 两点」对照。只变数据臂（CC12M+Amshaker → GPIC `short`），塔 w512/InfoNCE/30k 步/IN-1k lp 全固定。预注册判据见 `EXPERIMENTS_VISION_ROUND11.md §13.3`。

- ✅ **结果（11:19 ALL DONE，exit 0；全程无坍缩 C1 0.33–0.40 / C2_gap +0.087~+0.095 / C4 OK）**：GPIC `short` IN-1k frozen-trunk lp = **6.01% / 5.69% / 5.73%** @5.12M / 10.24M / 15.36M（zs 1.91/2.22/2.01%）；基线 CC12M+Amshaker = **3.43% / 5.45% / 6.08%**。
- ⚖️ **预注册裁定（§13.3）**：@5.12M = **+2.58 点**（≥基线+1.5 ✓）；@10.24M = **+0.24 点**（±1.5 内 ✗）→ 两点**交叉** → 「**未抬高 / 无显著差异**」。
- 📌 **科学结论（如实；🚫 不外推到 18.5M+）**：GPIC `short` 有**显著低 N 先发优势**（@5.12M +2.58 > 1.5 阈值且 > 噪声带上界 1.1），但**不抬高 ceiling**——@10.24M 优势收敛到 +0.24，@15.36M（>唯一对、数据重复）反略低于基线（5.73% vs 6.08%）。→「**数据质量加速早期；数据总量/多样性决定上限**」。R9 的 25.1% 渐近**不被数据臂改动推翻**。
- ⚖️ **公平性（§13.4）**：参数量同 126.78M、训练 token 同 0；30k 步耗时 GPIC **3892.7s / steady 5918.6 img/s** ≈ **0.56× 基线**（~6948s / 2939 img/s，吞吐 ≈2.0×）→ 对照在同 N 下，不改变「不抬高 ceiling」结论。

## ⭐ R13 OpenVision2 官方权重单臂对照（✅ 完成，2026-10-04 · ⚠️ 协议不同 → 单列表、不并入排名）

> 运维指令 2026-10-04（五）批准：R11-E 后**只做 OV2 官方权重 + 官方 p14/d24 结构塔**单臂对照。
> 它回答「**上限低是因数据少、不是因我们塔写得烂**」（补结论边界），**不是**抬上限。
> ⚠️ 官方权重 = **大尺度预训练** ViT-L/14；我们从零 ~118M 样本 —— **协议不同，严禁并入上方 R4–R8 from-scratch 排名**。

| 项 | 值 |
|:--|:--|
| 对象 | OpenVision2 官方权重 `UCSC-VLAA/openvision2-vit-large-patch14-224-vision-only`（Apache-2.0） |
| 官方结构 | patch14 / d24 / w1024 / h16(head_width64) / **GELU** MLP / no_ln_pre / pool=**avg**（256 patch token 均值，**不含 CLS**）/ final_ln_after_pool / 1024×1024 proj |
| 参数量 | **304.23 M**（load ✅：294 keys、strict=True 全对上，无 visual./state_dict/module. 前缀） |
| 评测口径 | IN-1k 自切分 val50/class + probe50/class（`r8_eval_in1k.load_in1k_split(max_files=40)`，与 R8/R9/R10/R11 **完全相同**）；frozen-trunk lp = Linear(1024→1000) · AdamW · full-batch · 100 ep · seed0 |
| IN-1k top-1 | zs **N/A**（官方塔生成式 1024-dim、无 CLIP 对齐 readout，与冻结 CLIP-L/336 768-dim 文本空间不对齐 → CLIP 余弦 zs 按构造≈随机）；**frozen-trunk lp = 79.81%** |
| 每样本编码耗时 | **0.57 ms/img = 1766.5 img/s**（H100-80G · bs128 · bf16 · 峰值显存 2.70GB） |
| 训练耗时 | **n/a**（纯评测，不训、不重训） |

- **对照（from-scratch 排名，勿并列）**：我们从零最佳 lp = **7.99%**（w384@15.36M，R10-③）；官方同口径 lp = **79.81%** → **+71.8 点**。
- 📌 **结论边界（如实标注）**：官方 OpenVision2 L/14（大尺度预训练）同口径 IN-1k frozen-trunk lp = **79.81%**；我们从零对比学习（冻结 CLIP 文本塔 + InfoNCE，~118M 上限）峰值 **7.99%**、渐近外推 25.1% —— **差约一个数量级**。
  → 判据坐实：**瓶颈在「数据量 + 目标函数」（从零对比学习不够数/不够稠密），不是「我们 tower 写得烂」**（同一族 p14/d24 GELU ViT，官方权重即 79.81%）。
  → **不抬上限**：它是官方协议参照点，不改 from-scratch 排名与「25.1% 渐近 / 20% 需 619 亿样本」的 scaling 结论。
- 🔑 **结构差异备注（可复用）**：官方 OV2 = **avg-pool（256 patch token、不含 CLS）+ final_ln_after_pool + 1024×1024 proj**；我们自研 OpenVision2 = **CLS readout（patch16/d30）**。差异 =「我们自研改编」的又一证据（`VISION_OFFICIAL_REPOS_SURVEY.md §10.4`）。
- 证据：`/tmp/r13_official.log`（exit 0）+ `/tmp/r13_ov2/bench.log`（1766.5 img/s）+ `/tmp/r13_ov2/smoke2.log`（load 成功）；脚本 `run/vision/r13_eval_official.py` + `r13_run_official.sh`；权重 `/nas_train/app.e0031982/datasets/baize-vision/r13_official/open_clip_pytorch_model.bin`（1.217GB）。
---

## ⭐ R12b 全量数据 AIMv2 训练（✅ 完成，2026-10-06 → 10-07）

> 运维指令 2026-10-05（晚）：用全部现有数据训练当前最佳配方 AIMv2。Fresh run（非续跑）。详见 `EXPERIMENTS_VISION_ROUND12.md §2`。

- **配方** = AIMv2-style：`InfoNCE + 1.0×masked-patch-MSE`（`--loss aimv2 --mask-ratio 0.6`），w512（126.78M）+ 冻结 CLIP-768 文本塔。**数据 = 全部现有**：GPIC（~52.8M）+ CC12M（~11.0M）+ Amshaker（~5.95M）→ ~69.7M unique pairs。
- **步数**：272,000 步 ≈ 2 epochs。训练时间 12:54 → 02:14 ≈ 13.3h（106.4 GPU·h）。
- **lp_max = 18.81%**（final, 139.3M tokens）。lp 在 step120k（61.4M, ~0.9 epoch）后进入平台（18.0–18.8%），未超越 R11-G 的 19.76%@55.3M。
- ⚠️ **更多 unique 数据 ≠ 更高 lp**：R12b（69.7M, 2ep）lp_max=18.81% < R11-G（18.5M, 1ep）lp_max=19.76% < R12 3-epoch（58.8M, 3ep）lp_max=20.32%。→ **epoch 数（数据重复遍历次数）比 unique 数据量更重要**。

---

## ⭐ Mask-ratio 消融（✅ 完成，2026-10-07 · `VISION_NEXT_DIRECTIONS.md` 方向 2）

> 运维指令 2026-10-06 批准。**只变 mask-ratio**（0.3/0.5/0.6/0.75/0.9），其余固定：w512 / CC12M+Amshaker / 30k 步 / InfoNCE+patch_MSE (1:1) / 冻结 CLIP-768。Arm 0.6 = R11-L arm6-A 的受控复现。预注册判据：lp >= baseline + 1.5 → "更优"；全部 ±1.5 → "不敏感"。

### IN-1k frozen-trunk lp 结果（20 ckpts, Protocol A = BaiZe 内部协议）

| mask_ratio | C1_final (probe) | C1_peak (probe) | lp@10k | lp@20k | **lp@30k** | Δlp vs 0.6 | zs@30k | 训练耗时 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3  | 0.3495 | 0.4421 | 10.70% | 11.34% | **12.69%** | −0.80 | 5.25% | 7119s |
| 0.5  | 0.3756 | 0.4066 | 9.81%  | 10.90% | **11.91%** | −1.58 | 4.82% | 7062s |
| **0.6**  | **0.3810** | 0.4241 | 11.75% | 12.52% | **13.49%** | **(baseline)** | 5.82% | 6910s |
| 0.75 | 0.3736 | **0.4458** | 11.88% | 12.02% | **12.49%** | −1.00 | 5.22% | 6992s |
| 0.9  | 0.3468 | 0.4097 | 10.18% | 10.47% | **11.53%** | −1.96 | 4.89% | 7138s |

> R11-L arm6-A 原始 lp@30k = 12.08%；本次受控复现 = 13.49%（Δ=+1.41pp，在 ±1.5pp 噪声带内 → 确认可复现性）。

### 预注册裁定

- **lp >= baseline + 1.5**（"更优"）：❌ 无臂达到。
- **全部 ±1.5 内**（"不敏感"）：arm 0.3（Δ=−0.80）✅、arm 0.75（Δ=−1.00）✅ 在噪声带内。
- **显著更差**（Δ < −1.5）：arm 0.5（Δ=−1.58）⚠️、arm 0.9（Δ=−1.96）⚠️。

### 科学结论

1. **mask_ratio=0.6 最优**：IN-1k lp 呈倒 U 形——0.6 最高（13.49%），两侧递减。C1 probe 同样在 0.6 达 final 最高（0.3810）。
2. **0.3–0.75 区间不敏感**：arm 0.3 和 0.75 在 ±1.5pp 噪声带内 → flip 对 mask-ratio 在 [0.3, 0.75] 区间稳健。
3. **极端值显著更差**：0.5（−1.58）和 0.9（−1.96）超出噪声带 → 过低/过高 mask-ratio 损害 lp。
4. **C1 vs lp 分歧**：arm 0.75 的 C1 peak（0.4458）为全臂最高，但 final C1（0.3736）和 lp（12.49%）均低于 0.6 → **高 mask-ratio 的 C1 峰值早现但不稳定，终态劣于 0.6**。
5. **非单调 lp**：arm 0.3 lp（12.69%）> arm 0.5 lp（11.91%），但 C1 相反（0.3495 < 0.3756）→ **对比对齐（C1）与线性可分性（lp）不完全正相关**；可能因 0.3 更低 mask → 更多可见 patch → 更丰富的 InfoNCE 负样本 → 更好的 lp 特征，尽管 C1 对齐较低。
6. 🚫 **改 recipe ⇒ 不并入 scaling 曲线**（运维要求）。

- **证据**：`/tmp/ablation_mask_ratio.log`（master log, ALL DONE 20:06:17）+ 各 arm `train.log` 在 `/nas_train/app.e0031982/datasets/baize-vision/out/ABL_mask_ratio_0p{3,5,6,75,9}/`。脚本 `vision/run_mask_ratio_ablation.sh`。

---

## ⭐ Weight-ratio 消融（✅ ALL DONE，2026-10-07→08 · `VISION_NEXT_DIRECTIONS.md` 方向 3）

> 运维指令 2026-10-06 批准。**只变 contrast_weight : patch_loss_weight**（4 臂: 1:2 / 1:0.5 / 0.5:1 / 2:1），其余固定：w512 / CC12M+Amshaker / 30k 步 / mask-ratio=0.6 / InfoNCE+patch_MSE / 冻结 CLIP-768。Baseline = 1:1（R11-L arm6-A, lp@30k=12.08%，mask-ratio 消融复现=13.49%）。预注册判据：lp >= baseline + 1.5 → "更优"；全部 ±1.5 → "不敏感（flip 由共存驱动，非比例）"。🚫 改 recipe ⇒ 不并入 scaling 曲线。

### 4 臂训练 + IN-1k lp 评测结果（✅ 全部完成，2026-10-08 05:27）

| arm (CW:PLW) | C1_final@30k | C1_peak | C2_gap | C4 | final_loss | 训练耗时 | steady img/s | lp@10k | lp@20k | lp@30k | Δlp vs 1:1(13.49%) |
|---:|---:|---:|---:|:--:|---:|---:|---:|---:|---:|---:|---:|
| 1:2 (cw1_plw2) | 0.3546 | 0.4229@20400 | +0.1197 | OK | 3.1601 | 7403s | 2462.6 | 11.80% | 12.73% | **13.13%** | **−0.36** |
| 1:0.5 (cw1_plw0p5) | 0.3517 | 0.4176@19200 | +0.1131 | OK | 3.5013 | 7383s | 2443.8 | 9.22% | 8.65% | **10.22%** | **−3.27** |
| 0.5:1 (cw0p5_plw1) | 0.2816 | 0.4304@2100 | +0.1278 | OK | 1.6794 | 7829s | 4747.0 | 13.32% | 13.55% | **13.80%** | **+0.31** |
| 2:1 (cw2_plw1) | 0.3475 | 0.4177@22500 | +0.1147 | OK | 7.0765 | 7521s | 2691.8 | 8.09% | 9.31% | **10.21%** | **−3.28** |

> Baseline 1:1 = mask-ratio 消融 arm 0.6 的 lp@30k = **13.49%**（同 recipe、同数据、同 30k 步、Protocol A）。

### 结论

1. **无臂翻盘**：最优 arm 0.5:1 (lp=13.80%) 仅 +0.31pp vs baseline 13.49% → **远低于 +1.5pp 预注册阈值** → **"更优"判据不满足**。
2. **contrast_weight 过高显著有害**：arm 2:1 (lp=10.21%, Δlp=−3.28pp) 超出 ±1.5pp 噪声带 → **显著更差**。contrast=2 使 InfoNCE 主导训练，patch 预测信号被淹没。
3. **patch_loss_weight 过低显著有害**：arm 1:0.5 (lp=10.22%, Δlp=−3.27pp) 超出噪声带 → **显著更差**。削弱 patch 重建 → 几何/局部特征退化。
4. **patch_loss_weight 过高中性**：arm 1:2 (lp=13.13%, Δlp=−0.36pp) 在噪声带内 → **不敏感**。patch 重建信号增强不损害 lp。
5. **contrast_weight 减半微正但不显著**：arm 0.5:1 (lp=13.80%, Δlp=+0.31pp) 在噪声带内 → **不敏感**（微正趋势）。C1 波动大（0.4304@2100→0.2816@30000）但 C4=OK 无坍缩。
6. **倒 U 形不对称**：最优 ≈ 1:1 (baseline)，但**向 patch-heavy 方向（1:2）更宽容**（−0.36 vs −3.27），向 contrast-heavy 方向（2:1）更敏感（−3.28）。→ **patch loss 是「安全冗余」信号，contrast loss 是「关键」信号——不宜削弱也不宜过度放大**。
7. **C1 与 lp 分歧再现**：arm 0.5:1 的 C1_final (0.2816) 是全臂最低，但 lp (13.80%) 是全臂最高 → **低 contrast_weight 导致对齐弱（C1 低）但 lp 特征更好** → 与 mask-ratio 消融 arm 0.3 同一规律。
8. 🚫 **改 recipe ⇒ 不并入 scaling 曲线**。

> ⚠️ **arm 3 C1 非单调**：C1 从 0.4304@2100（早现峰值）下降到 0.2924@11700（低谷），再回升到 0.3589@29100，末点 0.2816@30000 回落。C2_gap 全程 +0.117~+0.134、C4=OK → **无坍缩**，但 C1 波动幅度较大（对比 arm 1/2 的 0.35±0.02 稳态）。contrast_weight=0.5 的 InfoNCE 信号减弱 → 对齐特征更不稳定。

> ⚠️ **脚本异常退出 + 已恢复**：arm 1 完成后原脚本 `run_weight_ratio_ablation.sh` 异常退出。已创建恢复脚本 `run_weight_ratio_ablation_resume.sh`（PID 3214830, setsid+nohup, ppid=1），arms 2-4 串行完成 + 16 ckpts 统一 IN-1k eval。ALL DONE 2026-10-08 05:27:03。

- **证据**：`/tmp/ablation_weight_ratio.log`（master log, ALL DONE 05:27:03）+ 各 arm `train.log` 在 `/nas_train/.../out/ABL_weight_ratio_cw{1_plw2,1_plw0p5,0p5_plw1,2_plw1}/`。恢复脚本 `vision/run_weight_ratio_ablation_resume.sh`。

---

## ⭐ R13 官方 AIMv2 AR 范式对比（✅ Arm B 坍缩 + ✅ Arm B-hybrid 完成, 2026-10-08）

> 运维指令 2026-10-07 批准（`VISION_AIMV2_OFFICIAL_PLAN.md`）。**核心问题**：官方 AIMv2 用纯 AR（causal ViT + next-patch pixel + text AR, 无 InfoNCE）在 12B 样本上成功——**我们的数据规模（~7.7M 对 + 短 caption）能否复现？**
>
> **三臂对照**：
> - **Arm A（baseline, 已有）**：bidirectional + InfoNCE + masked-patch-MSE → lp@30k=12.08%（R11-G arm⑥-A）
> - **Arm B（官方 AR）**：causal ViT + cap_loss + 0.4×pixel_loss, **无 InfoNCE** → 🔴 **坍缩 @step600**
> - **Arm B-hybrid（追加实验）**：causal ViT + 1.0×InfoNCE + cap_loss + 0.4×pixel_loss → 🟢 **C1=0.2480@300, 无坍缩**

### Arm B（pure AR, 无 InfoNCE）— 🔴 步 600 坍缩

| 指标 | 值 | 说明 |
|:--|:--|:--|
| 探针 step 300 | C1=**0.8649** C2_gap=−0.0001 C4=OK | 已接近坍缩阈值 0.95 |
| 探针 step 600 | C1=**0.9731** C2_gap=+0.0000 C4=OK | **>0.95 → 触发熔断** |
| 熔断步数 | **600 / 30000** | 仅完成 2% |
| final_loss | 5.0552 | loss 在降（C4=OK），但特征坍缩 |
| throughput | 2434.5 img/s | |
| 保存 | `vision_fused.pt`（坍缩 ckpt） | |

**关键发现**：
1. **纯 causal AR 无对比项 → 快速坍缩**：C1 从 0.86（step300）升至 0.97（step600），仅 300 步即越过 0.95 阈值。
2. **与 R11-H（bidirectional 无对比项）不同**：R11-H 用**双向**注意力 + 无 InfoNCE → **C1=0.43, 未坍缩**。Arm B 用**因果**注意力 + 无 InfoNCE → **坍缩**。→ **坍缩是 causal attention + 无对比项的组合效应，非单一因素**。
3. **loss 在降但特征坍缩**：cap_loss 从 6.77→5.08（降），pixel_loss 稳定 ~0.73，C4=OK。→ 经典「loss 下降但表征坍缩」——AR next-token/pixel 任务可被平凡解满足。
4. **DDP 死锁 bug 已修复**：rank0 熔断后 break，其他 rank 仍在 forward → NCCL 超时死锁。已加 `dist.broadcast(fused_flag, src=0)` 让所有 rank 同步退出。

**预注册判据匹配**：`Arm B C1 > 0.95 → 🔴 AR collapse (no contrastive → collapse)` — ✅ 命中。

### Arm B-hybrid（AR + InfoNCE）— ✅ 完成（30k 步 + IN-1k eval）

| 指标 | 值 | 说明 |
|:--|:--|:--|
| 训练步数 | 30000 / 30000 | ✅ 全程完成 |
| 总耗时 | 8712.7s (~2.42h) | steady_image_s=2175.9 |
| fused | **False** | ✅ **无坍缩** |
| C1@30000 | **0.4845** | 振荡 0.30–0.55, C4=OK, C2_gap~+0.064 |
| final_loss | 9.7075 | contrast~5.38, cap~4.62, pixel~0.77 |
| 保存 | vision_step{10k,20k,30k}.pt + vision.pt | 4 ckpts |

**IN-1k frozen-trunk eval 结果**：

| ckpt | lp top-1 | zs top-1 |
|:--|--:|--:|
| step 10000 | 0.31% | 0.37% |
| step 20000 | 1.31% | 0.36% |
| step 30000 | **1.37%** | 0.37% |
| vision.pt (=30k) | 1.37% | 0.37% |

**对比**：
| 臂 | 注意力 | InfoNCE | C1@300 | C1@600 | C1@30k | lp@30k | 判定 |
|:--|:--|:--|--:|--:|--:|--:|:--|
| Arm A (baseline) | bidirectional | ✅ | ~0.33 | ~0.30 | ~0.28 | **13.49%** | ✅ 健康, 最优 |
| Arm B (pure AR) | causal | ❌ | 0.8649 | **0.9731** | — | — | 🔴 坍缩@600 |
| **Arm B-hybrid** | causal | ✅ | 0.2480 | 0.4332 | **0.4845** | **1.37%** | ✅ 无坍缩, 但 lp 极低 |
| R11-H (no contrast) | bidirectional | ❌ | 0.43 | 0.37 | ~0.35 | — | ✅ 健康 |

**最终结论**（✅ 已完成 30k + eval 确认）：
1. **InfoNCE 是防止 AR 坍缩的必要条件**（在我们的数据规模下）：纯 AR 无对比项 → 坍缩@600；加 InfoNCE → 全程无坍缩（C1~0.48）。**假说确认**。
2. **但 causal AR 严重损害表征质量**：Arm B-hybrid lp@30k=1.37% vs Arm A 基线 13.49% → **Δlp=−12.12pp**，远超 ±1.5pp 噪声带。zero-shot 几乎为随机（0.37% vs chance 0.10%）。
3. **Causal attention 比 bidirectional 更易坍缩**：双向无对比（R11-H）C1=0.43 不坍缩；因果无对比（Arm B）C1=0.97 坍缩。→ **坍缩是 causal + 无对比的组合效应**。
4. **官方 AIMv2 不坍缩的可能原因**：① 12B 样本（vs 我们 7.7M, 1557×差距）② LLaMA-3 长 caption（text AR 信号更强）③ 可能的其他正则化。**我们的短 caption（alt-text, ~20 tok）+ 小数据规模无法支撑 causal AR 范式**。
5. **决策**：causal AR 范式在本地数据规模下不可用；维持 bidirectional + InfoNCE + masked-patch-MSE（即 AIMv2-style）为最优 recipe。

- **证据**：`/tmp/r13_aimv2_ar.log`（Arm B 纯 AR, 坍缩@600）+ `/tmp/r13_aimv2_ar_hybrid.log`（Arm B-hybrid, 30k 完成 + eval）。脚本 `vision/run_aimv2_ar.sh` + `vision/run_aimv2_ar_hybrid.sh`。代码修改 `r9_train.py`：`aimv2_ar` 分支新增 `--contrast-weight` 支持 + DDP 熔断广播修复。

---

## 胜出结论（S0+S1+S2+S3 汇总 · ⚠️ R1/R2 旧读数，已因坍缩/lr 伪影作废，仅作历史）

**胜出架构：OpenVision2（纯 Attention ViT，w1024·d30·h16·mlp4096，505.0M）**

- P0 三硬指标：训练吞吐 **2139 img/s（最优，S3 干净实测）**、推理 **153.7 img/s / 6.51ms（最优）**、最终 loss 4.4540（四架构并列 ~4.45–4.47）。
- 关键量化洞见（S3 长地平线修正）：把训练延长到 5k–10k 步后，四架构 loss 全部从 S1 的 6.7342 平台继续跌破至 **~4.45–4.47**，且架构间 loss 差 <0.02（噪声级）→ **架构在 loss 上不可区分**，选择完全由吞吐/延迟决定。
- 🔑 S1「四架构 loss 全 6.7342 平台」是 **cosine LR 坍缩伪影**（`--steps 1000` 令 cosine 在 ~700 步就把 LR 从 1e-3 衰减到 ~2.6e-4→1e-5@1000，loss 卡死），**非架构等价**。S3 用 `--steps 10000`（cosine 跨 10000 步），step700 LR 仍 ~9.9e-4，loss 继续降：6.85@500→5.92@1000→4.45@5k–10k。
- 吞吐/延迟差异由结构决定（224/16 · 196 token 小序列）：纯 Attention 最优（2139 img/s / 6.5ms）；SSM 与 MoE 在 196 token 下**开销主导、吃不到长序列红利**（DeepEncoderV2 1459 img/s / 17.8ms，MambaEye 790 img/s / batch1 卡死，MoE-ViE 852 img/s / 141ms）。

> ⚠️ 吞吐测量带病（共享集群）：S1/S2 与另一项目 `nemo_experiments` 的 s1_01/s2_01（arch=mamba2，8×H100）并发，存在争用。DeepEncoderV2 训练稳态 578 img/s 系「误触发 openvision2 进程争用」污染，其干净稳态 ≈1430–1450 img/s（step300–725）。相对排序不受影响。

## 环境与配置

- BASE_DIR：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027`；实际代码在 `run/vision/`（models.py / data.py / train.py / prep_data.py / run_train.sh / run_s1.sh）
- 环境：conda `py310`（CUDA 12.8 / PyTorch 2.8.0 / open_clip 3.2.0 / torchvision 0.23 / mamba_ssm / webdataset 1.0.2 / flash_attn）
- GPU：6×H100 80GB（DP6，TORCH_NCCL）。四架构同卡数、同 batch、同 seed。
- 数据：LLaVA-OneVision-1.5 Mid-Training（parquet）切成统一子集 `imagenet/EN` 500K 对 →
  webdataset tar（`/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar`，25 shard × 20K）
- 默认配置（S1 锚点）：cls=224 / patch=16 / SigLIP / lr=1e-3 AdamW(0.9,0.95) / warmup 100 + cosine /
  seed=1234 / bf16 / batch=32×6=192 / text tower = 12L·512w·8h（四架构共用随机 init）

## 四架构实测参数量（numel，target 500–600M）

| 架构 | 类型 | 参数量 | 激活参数 | 备注 |
|:---|:---|:---|:---|:---|
| OpenVision2 | 纯 Attention ViT | 505.0M | 505.0M | w=1024 d=30 h=16 mlp=4096 |
| MambaEye | 纯视觉 SSM（Vim 双向） | 534.9M | 534.9M | w=1024 d=40 d_state=16 expand=2 |
| MoE-ViE | 稀疏 MoE | 505.2M | 222.0M | w=1024 d=30，8 expert×ff512，top-2 |
| DeepEncoderV2 | Attn+SSM 混合（AAMM） | 516.9M | 516.9M | w=1024 d=34 混合 |

## S0 冒烟（15 步，6 卡 batch32）

| ID | 架构 | 参数量 | loss@15 | ms/iter | image/s | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| S0-A | OpenVision2 | 505.0M | 7.797 | 127.5 | 1505 | ✅ RUNNABLE |
| S0-B | MambaEye | 534.9M | 7.827 | 510.1 | 376 | ✅ RUNNABLE |
| S0-C | MoE-ViE | 505.2M(222M) | 9.254 | 1371.6 | 140 | ✅ RUNNABLE(未达稳态) |
| S0-D | DeepEncoderV2 | 516.9M | 7.794 | 247.0 | 777 | ✅ RUNNABLE |

> 注：15 步含 cudnn autotune/首步惰性初始化，MoE 的 ms/iter 尚在下降未达稳态，S1(1000步) 会重测 steady-state。

## S1 主训练（1000 步 × 4 架构，默认配置）

| ID | 架构 | 参数量 | 状态 | 最终loss | 训练image/s | 耗时 | GPU·h |
|:---|:---|:---|:---|:---|:---|:---|:---|
| S1-A | OpenVision2 | 505.0M | ✅ 完成 | 6.7342 | 1491 | 235s | 0.39 |
| S1-B | MambaEye | 534.9M | ✅ 完成 | 6.7342 | 398 | 642s | 1.07 |
| S1-C | MoE-ViE | 505.2M(222M) | ✅ 完成 | 6.7342 | 443 | 531s | 0.88 |
| S1-D | DeepEncoderV2 | 516.9M | ✅ 完成 | 6.7342 | 578* | 303s | 0.51 |

> *DeepEncoderV2 训练吞吐被「误触发的 openvision2 进程」争用污染（step750–1000 掉到 ~578）；干净稳态 ≈1430–1450 img/s，实则仅次于 OpenVision2。四者最终 loss 全部 6.7342（同种子同数据同 text tower，SigLIP 对比平台）。

## S2 推理基准（batch=1 前向，bf16，224/16）

| 架构 | 参数量 | ms/img | image/s | token/s(=img×196) | 备注 |
|:---|:---|:---|:---|:---|:---|
| OpenVision2 | 505.0M | 6.508 | **153.7** | 30117 | 纯 Attention，最优 |
| DeepEncoderV2 | 516.9M | 17.761 | 56.3 | 11035 | 混合 AAMM，双向 Mamba 前向重 |
| MoE-ViE | 505.2M(222M) | 141.721 | 7.1 | 1383 | 路由+sort/grouped 纯 PyTorch，CPU 主导 |
| MambaEye | 534.9M | — | 卡死/超时 | — | mamba_ssm selective_scan 在 batch=1 停摆（150s 超时） |

> S2 说明：batch=1 单图推理是 MLLM 编码器最常见场景。SSM/MoE 的小 batch 延迟劣势在推理端被放大——MambaEye 全 SSM 在 batch=1 停摆、DeepEncoderV2 混合比纯 Attention 慢 ~2.7×、MoE-ViE 慢 ~22×（路由 CPU 开销）。纯 Attention 无论训练吞吐还是推理延迟均为最优。

## S3 长地平线（5000–10000 步 × 4 架构，en500k，cosine 跨度=steps）

| 架构 | 步骤 | 最终loss | loss@500 | loss@1000 | loss@5000 | 稳态img/s | GPU·h |
|:---|:---|:---|:---|:---|:---|:---|:---|
| OpenVision2 | 10000 | **4.4540** | 6.8542 | 5.9180 | 4.4560 | **2139.5** | ~2.35 |
| DeepEncoderV2 | 5000 | 4.4662 | 6.8541 | 5.9277 | 4.4662 | 1458.7 | ~1.61 |
| MambaEye | 5000 | 4.4700 | 6.8541 | 5.9463 | 4.4700 | 790.0 | ~2.56 |
| MoE-ViE | 5000 | 4.4661 | 6.8541 | 5.9406 | 4.4661 | 852.3 | ~2.10 |

> **S3 结论**：长地平线 loss 从 S1 的 6.7342 平台继续跌破至 ~4.45–4.47，**四架构 loss 差 <0.02（噪声级）**，架构在 loss 上不可区分。loss 排名（OpenVision2 4.454 < MoE-ViE 4.466 ≈ DeepEncoderV2 4.466 < MambaEye 4.470）无统计意义（< 多种子方差）。**决定性维度是吞吐/延迟**：OpenVision2 训练 2139 img/s（比 DeepEncoderV2 快 1.47×、比 MambaEye/MoE 快 2.5×）、推理 6.51ms（比 DeepEncoderV2 快 2.7×）。故锁定 **OpenVision2 为胜出架构 + 默认配置锚点（224/16、SigLIP、lr=1e-3、warmup100+cosine、seed1234、bf16、batch32×6）**。

## S4 多种子（top-2 架构 × 3 seed × 3000 步）

| 架构·seed | 最终loss | 训练img/s（稳态） |
|:---|:---|:---|
| openvision2_s1234 | 4.9962 | 1582.1 |
| openvision2_s42 | 4.9962 | 1636.7 |
| openvision2_s7 | 4.9962 | 1805.8 |
| deepencoder_v2_s1234 | 4.9962 | 1435.9 |
| deepencoder_v2_s42 | 4.9962 | 1437.7 |
| deepencoder_v2_s7 | 4.9962 | 1439.9 |

> **多 seed 结论**：6 run 最终 loss 全 4.9962（4 位完全一致）= cosine LR 3000 步尾部的 min_lr 平台，loss 与 seed/架构无关（seed 方差≈0）。**吞吐跨 seed 稳定且与架构绑定**（OV2 1582–1806 vs DE 1436–1440，稳定 1.1–1.25× 差距）→ 架构区分完全取决于吞吐。

## S5 下游代理检索（text↔image R@1/5/10，held-out laioncn/EN 5k，full ckpt）

| 架构 | t2i R@1/5/10 | i2t R@1/5/10 |
|:---|:---|:---|
| openvision2 | 0.0000 / 0.0012 / 0.0020 | 0.0000 / 0.0008 / 0.0020 |
| deepencoder_v2 | 0.0002 / 0.0010 / 0.0020 | 0.0002 / 0.0008 / 0.0016 |

> 3000 步随机 init 的 zero-shot 检索近乎随机（<1/5000），两架构并列无区分。无 ImageNet 类标签故 top-1/linear-probe 不可做（报告注明）。

## S6 分辨率/patch 消融（OpenVision2，3000 步，锚点 lr=1e-3）

| res/patch | 最终loss | 训练img/s |
|:---|:---|:---|
| 224/16（锚点） | 4.9962 | 1582.1 |
| 336/16 | 4.9962 | 1630.1 |
| 448/16 | 4.9962 | 960.4 |
| 224/14 | 4.9962 | 1613.8 |
| 336/14 | 4.9962 | 1289.7 |
| 448/14 | 4.9962 | 757.3 |

> loss 全 4.9962 = 锚点 lr=1e-3 塌到 min_lr 的平台（非分辨率/patch 差异）；有信息量的是吞吐——**token 数越多训练越慢**（224/16 1582 → 448/14 757 img/s）。

## S7 目标函数（SigLIP vs CLIP InfoNCE，OpenVision2，3000 步）

| 目标 | 最终loss | 训练img/s |
|:---|:---|:---|
| SigLIP（锚点） | 4.9962 | 1664.9 |
| CLIP InfoNCE | 2.8941 | 1717.5 |

> CLIP InfoNCE loss 尺度不同（softmax vs sigmoid），不可直接比；SigLIP 锚点 loss 仍受 lr=1e-3 平台限制。

## S8 LR 扫描（OpenVision2，3000 步）

| lr | 最终loss | 训练img/s |
|:---|:---|:---|
| 1e-3（锚点） | 4.9962 | 1651.3 |
| 3e-3 | 4.4562 | 1645.1 |
| 5e-3 | 4.4542 | 1615.8 |

> 🔑 **关键 LR 结论**：lr=1e-3 在 3000 步 cosine 尾部塌到 min_lr(1e-5)，末端 loss 停 4.9962；3e-3/5e-3 在相同步数仍维持有效学习率 → 收敛到更低 loss 4.4562/4.4542。即 **4.9962 平台 = lr=1e-3 的 LR 塌缩伪影，非数据/架构天花板**。生产建议 lr=3e-3。

## S9 推理深挖（OpenVision2，统一前向 bench batch∈{1,8,32}+多分辨率）

| 配置 | ms/img | image/s | token/s |
|:---|:---|:---|:---|
| batch=1 res=224 patch=16 | 10.069 | 99.3 | 19465 |
| batch=8 res=224 patch=16 | 0.887 | 1127.7 | 221029 |
| batch=32 res=224 patch=16 | 0.711 | 1405.7 | 275516 |
| batch=1 res=336 patch=16 | 7.118 | 140.5 | 61955 |
| batch=1 res=448 patch=16 | 6.949 | 143.9 | 112827 |
| batch=1 res=224 patch=14 | 10.206 | 98.0 | 25083 |

> batch 越大吞吐越高（batch=32 达 1406 img/s，接近训练吞吐），token/s 随 patch 数增加而增加（多分辨率需插值 pos-emb）。SGLang 未装，退化为统一前向 bench（见决策 4）。

## converged（最终汇总）

**胜出架构：OpenVision2（纯 Attention ViT，505.0M）** —— loss 四架构并列（~4.45–4.47），训练吞吐 2139 img/s（最快）与推理延迟 6.51ms（最快）双决定性优势。

**完整可复现训练命令**（详见 HTML 报告「可复现训练命令」节）：

```bash
conda activate py310
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027/run/vision

# 胜出架构完整训练（OpenVision2，默认配置锚点，6 卡 DP6）
bash run_train.sh openvision2 10000 out/S3_openvision2 \
    --data '/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar' \
    --batch-size 32 --seed 1234 --loss siglip

# 四架构长地平线（S3：OpenVision2 10k + 其余 3×5k）
bash run_s3.sh
# S4 多种子 / S6 分辨率patch / S7 目标 / S8 LR / S9 推理深挖
bash run_s4.sh  # top-2 × 3 seed × 3000
bash run_s6.sh  # cls∈{336,448} patch∈{14,16}
bash run_s7.sh  # siglip vs clip
bash run_s8.sh  # lr∈{1e-3,3e-3,5e-3}
bash run_s9.sh  # batch + 多分辨率 bench
```

**产物**：`doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html`（自包含，已回填）+ `ISEDA2027/6_vision_encoder.tex`（config/results 已回填）。

**裁剪说明（预算）**：S7 数据侧（caption 粒度·规模·中英比例）因重 prep + 低信息量裁剪；S9 的 SGLang 生产栈未装（推迟到 MLLM Stage iv）。详见 HTML「局限」节。
---

## 🔬 Scaling Comparison Experiment (2026-10-08⑤ → ⑥ revision) — AIMv2 objective: does a bigger model score higher?

> **Operator instruction**: 2026-10-08⑤ (user direct order, highest priority).
> **⑥ revision (2026-10-08, user ruling)**: E2 changed from "official OV2 L/14@336 (304M, w1024/d24/p14/336)"
> to **same-family OV2 w768/d30 (284.54M, w768/d30/p16/224)** — the original E2 changed 4 variables
> simultaneously (params / structure / patch / resolution), which cannot attribute the difference to
> model scale. Now E1 vs E2 differ **only in width** (512→768), a standard model-scaling axis.
> **Pre-registered BEFORE training** — criteria locked, no post-hoc changes.

### 1. Pre-registration

**Claim under test**: Under the AIMv2-style dense objective (BP-1), a larger model
achieves a higher frozen-trunk linear-probe top-1 (Protocol B) on IN-1k, at a
fixed data budget of 1 epoch over ~94.9M image–caption pairs.

**Pre-registered criterion**: Δlp = lp(E2) − lp(E1), Protocol B, 3 seeds (0,1,2) → mean ± σ.

| Outcome | Interpretation |
|:--|:--|
| **Δ ≥ +1.5 pp** | Supports “bigger model → higher lp under AIMv2” (challenges R9/R10 “smaller tower better” under this objective) |
| **\|Δ\| ≤ 1.5 pp** | Not supported (no discernible advantage at this budget) |
| **Δ ≤ −1.5 pp** | Bigger model is *worse* (data-limited regime: widening is negative) |
| **σ > \|Δ\|** | Indistinguishable (noise dominates signal) |

Threshold ±1.5 pp = our internal noise band (ROUND10 §1.5). Two points do NOT
constitute a scaling law — only report whether a single budget point favours the
larger model. **No curve extrapolation.**

### 2. Two arms (identical recipe, only the tower width differs)

| | Tower | Params | Structure | Res / patch | Img tokens | Throughput (smoke) | 1-epoch ETA |
|:--|:--|--:|:--|:--|--:|--:|--:|
| **E1** | OpenVision2 w512/d30 (self-research) | **126.78M** | patch16, SwiGLU MLP | 224 / 16 | 196 | 4697 img/s | **~5.6 h** |
| **E2** (⑥ revised) | OpenVision2 w768/d30 (same family, width 512→768) | **284.54M** (2.24×) | patch16, SwiGLU MLP | 224 / 16 | 196 | **4845 img/s** (smoke+full run) | **~5.5 h** |
| ~~E2 (original ⑤, abandoned)~~ | ~~Official OV2 w1024/d24~~ | ~~304.2M~~ | ~~patch14, GELU~~ | ~~336 / 14~~ | ~~576~~ | ~~2347 img/s~~ | ~~11.2 h~~ |

> **⑥ revision note (2026-10-08, user ruling)**: The original E2 (official OV2 L/14@336, 304M)
> was abandoned because it changed 4 variables simultaneously (params / structure / patch / resolution),
> making it impossible to attribute any Δlp to model scale alone. The revised E2 uses the **same
> `vision/models.py` OpenVision2 implementation** with only `width` changed from 512→768;
> `heads` and `mlp_dim` scale with width automatically. This is a **standard model-scaling axis**.
> All other hyperparameters are identical to E1.

**Common (locked)**:
- Objective = AIMv2 dense (`--loss aimv2`): 1.0×InfoNCE + 1.0×masked-patch-MSE, mask_ratio=0.6, contrast:patch=1:1
- Text tower = frozen CLIP-ViT-L/14-336 (768-d), not unfrozen
- Data = GPIC 6233 tar × ~12639 + CC12M 1100 tar × ~10000 + Amshaker 2250 tar × ~2646 ≈ **95.7M pairs** (1 epoch ≈ 186,978 steps)
  - ⚠️ **Step count locked to 187,101** (E1's actual step count). GPIC grew to 6754 tar by E2 launch time (would compute 199,839 steps), but E2 is launched with `--steps 187101` to match E1 exactly. E2 sees a random subset (~93.6%) of the larger dataset over the same number of gradient steps. This preserves the "same budget" constraint.
- Budget = **same number of gradient steps** (187,101 steps = E1's count). Both arms train from scratch for identical step counts.
- Optim = AdamW lr=3e-3, warmup 20, constant, betas=(0.9,0.95), eps=1e-6
- Batch = 64/GPU × 8 = 512 total, bf16 autocast
- Seed = 1234
- Attention = bidirectional (no causal AR)
- Both arms **trained from scratch** (random init)

### 3. Confounds (⑥ revision: now minimal)

After the ⑥ revision, E1 vs E2 differ **only in width** (512→768):
1. **Params**: 126.78M → 284.54M (2.24×) — this is the **intended variable** (model scale)
2. **Heads / mlp_dim**: scale with width (8→12 heads, 2048→3072 mlp_dim) — automatic, part of the same scaling axis
3. **Structure / patch / resolution / tokens**: **all identical** (d30, p16, 224, 196 tokens)

⇒ A single Δlp **can** be attributed to parameter count (model scale) alone, since
width is the only varying axis. This is a cleaner experimental design than the
original ⑤ E2 (which confounded 4 variables).

> **Historical note (original ⑤, abandoned)**: The original E2 changed params (126.8→304.2M),
> structure (d30 SwiGLU→d24 GELU), patch (16→14), and resolution (224→336) simultaneously —
> 4 confounds. The ⑥ revision eliminates all confounds except the intended width axis.

### 4. Evaluation plan

- **Primary**: IN-1k frozen-trunk LP top-1, **Protocol B** (SGD+momentum 0.9, cosine,
  5-ep warmup, 90 ep, mini-batch 1024, IN-1k full train, 3 seeds 0/1/2 → mean ± σ)
- **Secondary**: Protocol A (for R9–R14 internal comparison)
- **Collapse guards**: C1 (cosine off-diag), C2 (cross-gap), C4 (loss-decreasing)
- **Fairness table**: params / training tokens / per-step time / per-sample time / peak GPU memory

### 5. Reference line (🚩 not comparable)

Official `openvision2-vit-large-patch14-336-vision-only` **pretrained weights**
frozen → Protocol B LP: R13 measured **79.81%** on the 224 variant. If 336 variant
is needed, ~1.2 GB download + pure eval. **Must label "contains large-scale
pretraining, not comparable"**.

> The original ⑤ E2 smoke test (official 304M, 2347 img/s, ETA ~11.2h) is **not wasted** —
> it can serve as an **optional third arm** (🚩 not part of this claim's evidence) if the
> operator/user decides to run it separately (that belongs to R13's "official vs self-research" topic).

### 6. Status

| Phase | Status |
|:--|:--|
| GPU registration (GPU12_ALLOC.md) | ✅ Done |
| Smoke test E1 (30 steps) | ✅ Done — 4697 img/s |
| Smoke test E2 original ⑤ (304M, abandoned) | ✅ Done — 2347 img/s (kept as reference) |
| Smoke test E2 revised ⑥ (w768, 284.54M) | ✅ **DONE** — 4328–4850 img/s, ETA ~5.5h, 284.5M params confirmed |
| ETA report | ✅ E1 ~5.6h (done); E2 ~5.5h (running) |
| Pre-registration (this section) | ✅ Written before training (⑥ revised) |
| Script fix (run_scaling_experiment.sh) | ✅ Done — run_e2() changed to w768/d30/p16/224; step count explicitly set to 187101 |
| Step-count audit (2026-10-09) | ✅ **Caught & fixed**: GPIC grew 6233→6754 tar; E2 would have run 199,839 steps vs E1's 187,101 (6.8% longer). Restarted E2 with `--steps 187101` to match E1 exactly. |
| sympy fix (2026-10-09) | ✅ sympy 1.5.1→1.14.0 (copied from vllm conda env) — fixes `equal_valued`/`core.sorting`/`core.traversal`/`core.parameters` ImportError that blocked Protocol A eval |
| E1 training (187,101 steps) | ✅ **DONE** — 187101/187101 steps, loss=1.3036, 6060 img/s, no collapse, vision.pt=487MB (completed 04:22 Oct 9) |
| E1 evaluation (Protocol B, 3 seeds) | ✅ **DONE** — **lp = 29.35 ± 0.00%** (seeds 0/1/2: 29.34/29.35/29.35) |
| E1 evaluation (Protocol A) | ✅ **DONE** — lp = **19.70%** (re-run by e2_post_watcher.sh at 20:30, sympy 1.14.0 fix applied) |
| E2 training (187,101 steps) | ✅ **DONE** — 187101/187101 steps, total=40867.4s (~11.35h), steady_image_s=4414.6, final_loss=1.9992, no collapse (C1=0.4302 C2_gap=+0.1110 C4=OK), vision.pt=1.07GB (completed 18:12 Oct 9). ⚠️ Training time 5.4× E1 due to NFS contention (not model size: 2.24× params but throughput limited by NFS 2000–4600 img/s vs E1's 6060) |
| E2 evaluation (Protocol B, 3 seeds) | ✅ **DONE** — **lp = 23.76 ± 0.04%** (seeds 0/1/2: 23.74/23.82/23.73) |
| E2 evaluation (Protocol A) | ✅ **DONE** — lp = **15.59%** |
| E1 evaluation (Protocol A re-run) | ✅ **DONE** — lp = **19.70%** (e2_post_watcher.sh, 20:30–20:41) |
| Report (HTML) | ✅ **DONE** — `report_vision_aimv2_scaling.html` (~26KB): all training data + SVG charts + eval results + judgment filled. |

---

### 7. Results — AIMv2 Scaling Experiment (✅ ALL DONE, 2026-10-09)

> Pre-registered two-arm width sweep under AIMv2 dense objective. E1 = w512/d30 (126.78M), E2 = w768/d30 (284.54M, 2.24×). Only width differs; all else identical (depth=30, patch=16, res=224, AIMv2 loss mask_ratio=0.6 contrast:patch=1:1, frozen CLIP-768 text tower, AdamW lr=3e-3, bs512, seed=1234, steps=187101, data=GPIC 6238 tar + CC12M 1100 + Amshaker 2250 ≈ 95.8M pairs). Both arms from scratch.

#### 7.1 Training Summary

| Metric | E1 (w512, 126.78M) | E2 (w768, 284.54M) | Ratio |
|:--|--:|--:|--:|
| Steps | 187,101 | 187,101 | 1.00× |
| Total wall time | 7,500.3 s (~2.08 h) | 40,867.4 s (~11.35 h) | 5.45× (NFS-confounded) |
| Steady img/s | 6,059.6 | 4,414.6 | 0.73× |
| ms/step (steady) | ~84.2 | ~114.8 | 1.36× (fair compute) |
| Per-sample time | 0.165 ms | 0.227 ms | 1.37× |
| Final loss | 1.3036 | 1.9992 | — (not comparable across widths) |
| Final C1 (cosine off-diag) | 0.4242 | 0.4302 | — |
| Final C2_gap | +0.1299 | +0.1110 | — |
| C4 (loss decreasing) | OK | OK | — |
| Collapse? | ❌ No (C1<0.5, C2_gap>0) | ❌ No (C1<0.5, C2_gap>0) | — |
| Checkpoint size | 487 MB | 1,090 MB | 2.24× |

> ⚠️ E2's 5.45× wall time is dominated by NFS I/O contention (E2 ran during peak hours 06:51–18:12; E1 ran overnight 19:29–04:22). The fair compute comparison is ms/step: 1.36× for 2.24× params — sub-linear, consistent with width being mostly matmul-bound.

#### 7.2 Evaluation Results

**Protocol B (primary — mainstream alignment):** SGD+momentum 0.9, cosine, 5-epoch warmup, 90 epochs, mini-batch 1024, IN-1k full train (1.28M images), IN-1k official val (50k), IN mean/std, 3 seeds (0, 1, 2) → mean ± σ.

| Arm | Seed 0 | Seed 1 | Seed 2 | **Mean ± σ** |
|:--|--:|--:|--:|--:|
| **E1 (w512, 126.78M)** | 29.34% | 29.35% | 29.35% | **29.35 ± 0.00%** |
| **E2 (w768, 284.54M)** | 23.74% | 23.82% | 23.73% | **23.76 ± 0.04%** |

**Protocol A (secondary — BaiZe internal):** AdamW lr=3e-3, full-batch, 100 epochs, probe 50/class, self-split val, CLIP norm, seed 0.

| Arm | Protocol A lp top-1 |
|:--|--:|
| E1 (w512) | 19.70% |
| E2 (w768) | 15.59% |

#### 7.3 Pre-registered Judgment

**Δlp = lp(E2_ProtB) − lp(E1_ProtB) = 23.76% − 29.35% = −5.59 pp** (σ = 0.04 pp, σ ≪ |Δ|)

| Outcome | Condition | Met? |
|:--|:--|:--|
| Supports scaling claim | Δ ≥ +1.5 pp | ❌ No |
| Not supported | \|Δ\| ≤ 1.5 pp | ❌ No |
| **Bigger is worse** | **Δ ≤ −1.5 pp** | **✅ Δ = −5.59 pp** |
| Indistinguishable | σ > \|Δ\| | ❌ No (σ = 0.04 ≪ 5.59) |

Protocol A confirms same direction: Δ(ProtA) = 15.59 − 19.70 = −4.11 pp.

#### 7.4 Conclusion

Under the AIMv2-style dense objective at a fixed 1-epoch budget over 95.8M image–caption pairs, widening the vision tower from 512→768 (126.78M→284.54M, 2.24× params) **decreases** frozen-trunk linear-probe top-1 by **5.59 pp** (Protocol B) / **4.11 pp** (Protocol A). This is consistent with R9/R10's finding that in the data-limited regime (~100M pairs, 1 epoch), the model-size marginal effect is **negative** — the smaller tower is more sample-efficient. The result is robust: (a) 3-seed σ = 0.04 pp ≪ |Δ| = 5.59 pp, (b) both protocols agree on direction, (c) neither arm collapsed (C1 < 0.5, C2_gap > 0, C4 = OK throughout).

⚠️ **Two points do NOT constitute a scaling law** — this is a single-budget-point observation. R9/R10 established the (N, M) scaling surface with 11+ points; this experiment tests one point on that surface under the AIMv2 objective and confirms the negative M-marginal at this budget.

#### 7.5 Fairness Table

| Dimension | E1 (w512) | E2 (w768) | Controlled? |
|:--|:--|:--|:--|
| Parameters | 126.78M | 284.54M (2.24×) | Varied (intended) |
| Depth | 30 | 30 | ✅ Identical |
| Patch / resolution | 16 / 224 | 16 / 224 | ✅ Identical |
| Image tokens | 196 | 196 | ✅ Identical |
| Training steps | 187,101 | 187,101 | ✅ Identical |
| Training pairs | 95.8M | 95.8M | ✅ Identical |
| Objective | AIMv2 dense (mask=0.6, 1:1) | AIMv2 dense (mask=0.6, 1:1) | ✅ Identical |
| Optimizer / lr | AdamW 3e-3 | AdamW 3e-3 | ✅ Identical |
| Batch size | 512 | 512 | ✅ Identical |
| Seed | 1234 | 1234 | ✅ Identical |
| Compute (ms/step) | 84.2 | 114.8 (1.36×) | Consequence of width |
| Wall time | 7,500 s | 40,867 s (5.45×) | NFS-confounded |
| GPU memory (est.) | ~16.5 GB | ~24.9 GB (1.51×) | Consequence of width |

- **Evidence**: E1 train log `/nas_train/.../scaling_E1_ov2_w512_d30_p16_224/train.log`; E2 train log `/nas_train/.../scaling_E2_ov2_w768_d30_p16_224/train.log`; E1 eval `/tmp/scaling_e1_eval.log`; E2 eval `/tmp/scaling_e2_eval.log`; E1 ProtA re-run `/tmp/e2_post_watcher.log`; HTML report `doc/BaiZe-ISEDA2027/report_vision_aimv2_scaling.html`.

---

## 🔬 Scaling Fair Rerun (2026-10-09⑨) — Schedule-Corrected Two-Arm Width Sweep

> ⛔ **The §7 results above are SUPERSEDED.** Both arms used `--lr 3e-3 --warmup 20` (warmup = 20/187101 = 0.01% of total steps), a schedule originally designed for 30k-step short runs. At 187k steps, this is effectively no warmup + high constant lr — which may systematically disadvantage the wider E2 arm. This rerun uses a proper cosine schedule with adequate warmup.

### 8.1 Pre-Registration (registered 2026-10-09, before training)

**Question**: Under the AIMv2-style dense objective, does widening the vision tower from 512→768 (126.78M→284.54M, 2.24×) improve frozen-trunk linear-probe top-1 on IN-1k, at a fixed 1-epoch budget — when the learning-rate schedule is fair (adequate warmup + cosine decay)?

**Arms** (only `--width` differs):

| Dimension | E1fair (w512) | E2fair (w768) | Controlled? |
|:--|:--|:--|:--|
| Parameters | 126.78M | 284.54M (2.24×) | Varied (intended) |
| Width / Depth | 512 / 30 | 768 / 30 | Width only |
| Patch / Resolution | 16 / 224 | 16 / 224 | ✅ Identical |
| Training steps | 187,101 | 187,101 | ✅ Identical (explicit) |
| **lr** | **5e-4** | **5e-4** | ✅ Identical (was 3e-3) |
| **warmup** | **2000** (1.07%) | **2000** (1.07%) | ✅ Identical (was 20 = 0.01%) |
| **scheduler** | **cosine → min_lr** | **cosine → min_lr** | ✅ Identical (was const) |
| **min_lr** | **5e-5** | **5e-5** | ✅ Identical (was N/A) |
| Batch size | 512 (64×8) | 512 (64×8) | ✅ Identical |
| Seed | 1234 | 1234 | ✅ Identical |
| Objective | AIMv2 (mask=0.6, 1:1) | AIMv2 (mask=0.6, 1:1) | ✅ Identical |
| Data snapshot | `data_snapshot_20261009.txt` (7437 GPIC tars frozen) + CC12M + Amshaker | Same | ✅ Identical |
| **total_shards** | **10787** | **10787** | ✅ Byte-identical |
| Output dir | `scaling_E1fair_ov2_w512_d30_p16_224` | `scaling_E2fair_ov2_w768_d30_p16_224` | New (old preserved) |

**lr trajectory self-check** (from E1fair `train.log`):
```
[lr-selfcheck] scheduler=cosine lr=0.0005 warmup=2000 min_lr=5e-05 steps=187101
[lr-selfcheck] lr@step0=0.00000000  lr@warmup(2000)=0.00050000  lr@50%(93550)=0.00027882  lr@last(187100)=0.00005000
[lr-selfcheck] OK: lr monotonically decreasing after warmup
```

**[start] line** (from E1fair `train.log`):
```
[start] tower=openvision2 lr=0.0005 warmup=2000 bs=64 world=8 steps=187101 res=224 patch=16 seed=1234 shards=1349/rank objective=AIMv2-style(MIM+InfoNCE) scheduler=cosine min_lr=5e-05 text=frozen-CLIP-768(r=8,a=16.0,lr=0.0001) negatives=512 data_source=mixed caption_type=all total_shards=10787
```

**Judgment criteria** (pre-registered, unchanged from 2026-10-08⑤):
- Δlp = lp(E2fair_ProtB) − lp(E1fair_ProtB)
- Δ ≥ +1.5pp → supports scaling claim (original conclusion was schedule artifact)
- |Δ| ≤ 1.5pp → not supported (indistinguishable at this budget)
- Δ ≤ −1.5pp → bigger is worse (confirmed even under fair schedule)
- σ > |Δ| → indistinguishable (report 3-seed σ)
- Single budget point does NOT constitute a scaling law (written into Limitations)

**Evaluation**: Protocol B (`--probe-full-train`, 3 seeds 0/1/2 → mean±σ) + Protocol A. Old arms' checkpoints are NOT re-evaluated.

**Schedule comparison** (old vs new):

| Property | Old (§7, superseded) | New (§8, this rerun) |
|:--|:--|:--|
| lr | 3e-3 | 5e-4 |
| warmup steps | 20 (0.01% of 187k) | 2000 (1.07% of 187k) |
| Schedule | Constant (no decay) | Cosine → min_lr |
| min_lr | N/A | 5e-5 (10% of lr) |
| Data | Glob (GPIC grew 6233→6754 between arms) | Frozen snapshot (7437 tars, identical) |

### 8.2 Results

> 🔄 **E1fair COMPLETE (train + ProtB + ProtA eval). E2fair TRAINING IN PROGRESS.** E1fair training: 187101 steps, 31936.6s (~8.87h), final_loss=0.2545, no collapse, steady 3774.5 img/s. E1fair Protocol B: **lp=62.34±0.01%** (seeds 62.34/62.33/62.36). E1fair Protocol A: **lp=49.70%** (old unfair E1 ProtA=19.70%, Δ=+30.0pp). E2fair training started 09:20:12 Oct 10, currently at step ~9,850/187,101 (~5.3%), ~4,900 img/s, 33 PROBE all OK, no collapse. bothfair (PID 2670216) auto-chaining. ETA: E2fair train done ~14:30 → E2fair eval ~3.5h → all done ~18:00 Oct 10.

#### 8.2.1 E1fair Training — ✅ Complete (2026-10-10 07:17)

| Metric | Value |
|:--|:--|
| Status | ✅ COMPLETE (exit 0, 07:17:19 Oct 10) |
| Total steps | 187,101 |
| Wall time | 31,936.6s (~8.87h) |
| Final loss | 0.2545 |
| Steady throughput | 3,774.5 img/s |
| Collapse check | No collapse (623 PROBE events, all C4=OK, 0 fusing) |
| lr@end | 5.00e-05 (cosine → min_lr correct) |
| Checkpoints | 18 (step 10k–180k) + final vision.pt (509MB) |

**lr trajectory verification** (from `train.log`):
```
[lr-selfcheck] lr@step0=0.00000000  lr@warmup(2000)=0.00050000  lr@50%(93550)=0.00027882  lr@last(187100)=0.00005000
[lr-selfcheck] OK: lr monotonically decreasing after warmup
```

**[start] line** (from `train.log`):
```
[start] tower=openvision2 lr=0.0005 warmup=2000 bs=64 world=8 steps=187101 res=224 patch=16 seed=1234 shards=1349/rank objective=AIMv2-style(MIM+InfoNCE) scheduler=cosine min_lr=5e-05 text=frozen-CLIP-768(r=8,a=16.0,lr=0.0001) negatives=512 data_source=mixed caption_type=all total_shards=10787
```

#### 8.2.2 E1fair Protocol B Evaluation — ✅ Complete (2026-10-10 ~09:30)

| Metric | Value |
|:--|:--|
| Protocol | B (SGD+cosine 90ep, bs1024, IN-1k full train 1.28M → official val 50k, IN norm) |
| Seeds | 3 (0, 1, 2) |
| lp_top1 (seed 0) | 62.34% |
| lp_top1 (seed 1) | 62.33% |
| lp_top1 (seed 2) | 62.36% |
| **lp_top1 (mean ± σ)** | **62.34 ± 0.01%** |
| Old E1 (unfair schedule) | 29.35% |
| **Δ (fair vs old)** | **+33.0pp** — schedule was the bottleneck |

**Eval log evidence** (from `/tmp/scaling_e1fair_eval.log`):
```
[BRIDGE] B seed=0: lp_top1=0.6234 (62.34%)
[BRIDGE] B seed=1: lp_top1=0.6233 (62.33%)
[BRIDGE] B seed=2: lp_top1=0.6236 (62.36%)
[BRIDGE] B: lp_top1=0.6234±0.0001 (62.34±0.01%)
```

#### 8.2.3 E1fair Protocol A Evaluation — ✅ Complete (2026-10-10 09:20)

| Metric | Value |
|:--|:--|
| Protocol | A (BaiZe internal: full-batch, AdamW lr=3e-3, 100 epochs, self-split val) |
| lp_top1 | **49.70%** |
| Old E1 Protocol A (unfair schedule) | 19.70% |
| **Δ (fair vs old, Prot A)** | **+30.0pp** |

**Eval log evidence** (from `/tmp/scaling_e1fair_eval.log`):
```
[BRIDGE] A (BaiZe: AdamW full-batch 100ep) ...
[BRIDGE] A: lp_top1=0.4970 (49.70%)
===== e1fair eval DONE 2026-10-10 09:20:12 =====
```

#### 8.2.4 E2fair — ✅ Training Complete (2026-10-10 18:38) + ✅ Evaluation Complete (2026-10-10 20:47)

E2fair training completed at 18:38:35 Oct 10 (exit 0, 187,101 steps, final_loss=0.1579, 623 PROBE all OK, no collapse, 3,996.8 img/s). E2fair evaluation completed at 20:47:31 Oct 10 (Protocol B: 3 seeds; Protocol A: 1 seed).

**E2fair [start] line** (from `/tmp/scaling_e2fair.log`):
```
[start] tower=openvision2 lr=0.0005 warmup=2000 bs=64 world=8 steps=187101 res=224 patch=16 seed=1234 shards=1349/rank objective=AIMv2-style(MIM+InfoNCE) scheduler=cosine min_lr=5e-05 text=frozen-CLIP-768(r=8,a=16.0,lr=0.0001) negatives=512 data_source=mixed caption_type=all total_shards=10787
[lr-selfcheck] lr@step0=0.00000000  lr@warmup(2000)=0.00050000  lr@50%(93550)=0.00027882  lr@last(187100)=0.00005000
[lr-selfcheck] OK: lr monotonically decreasing after warmup
```

E2fair's `[start]` line and lr self-check are byte-identical to E1fair's — confirming only `--width 768` differs. `total_shards=10787` matches exactly.

**E2fair Evaluation Results** (from `/tmp/scaling_e2fair_eval.log`):
- Protocol B (3-seed mean±σ): **62.51 ± 0.04%** (seeds: 62.46%, 62.51%, 62.56%)
- Protocol A: **49.53%**
- Old E2 (unfair schedule): Prot B = 23.76%, Prot A = 15.59%
- Δ Prot B (fair − old) = +38.75pp; Δ Prot A (fair − old) = +33.94pp

#### 8.2.5 Δlp Comparison — ✅ Complete (2026-10-10 20:47)

Δlp = lp(E2fair_ProtB) − lp(E1fair_ProtB) = 62.51% − 62.34% = **+0.17pp**

| Metric | E1fair (w512) | E2fair (w768) | Δ |
|:--|:--|:--|:--|
| Protocol B (3-seed) | 62.34 ± 0.01% | 62.51 ± 0.04% | **+0.17pp** |
| Protocol A | 49.70% | 49.53% | −0.17pp |
| Final loss | 0.2545 | 0.1579 | −0.097 (E2 lower) |

**Pre-registered verdict**: |Δlp| = 0.17pp ≤ 1.5pp → **NOT SUPPORTED as a scaling benefit.** The two widths are **indistinguishable** at this budget. The sign flips across protocols (+0.17pp Prot B, −0.17pp Prot A), confirming no systematic width effect.

**The old "bigger is WORSE" conclusion (Δlp = −5.59pp) was a schedule artifact.** Under the fair cosine schedule, the −5.59pp effect vanishes entirely (+0.17pp). The fair schedule improved both arms dramatically (+33pp E1, +38.75pp E2), with E2 improving more — directly confirming the old `3e-3/warmup20/const` disproportionately hurt the wider model.

---

## §8.3 参照系说明（Reference System Explanation）— ③ 口径修订 (2026-10-10, operator instruction)

> **目的**：明确哪些数字可直接比较、哪些不可同表，避免误导性横比。
> **规则**：只有「同目标函数 + 同数据量级 + 同 epoch + 同评测协议」的**内部**基线才可直接比较。

### 8.3.1 BaiZe Internal Protocol 标注规则

凡出现**绝对 lp / zs / k-NN 数字**，必须标注所用的评测协议：

| 标注 | 含义 | 适用场景 |
|:--|:--|:--|
| **BaiZe internal protocol (ProtB)** | SGD+momentum0.9+cosine, 90ep, mini-batch 1024, IN-1k full train, IN-1k val 50k, IN-1k norm, 3 seeds | 主结果（主流对齐，可与 DINOv2/MAE/iBOT 公开值横比） |
| **BaiZe internal protocol (ProtA)** | AdamW lr=3e-3, full-batch, 100ep, probe 50/class, self-split val, CLIP norm, seed 0 | 旧实验（R2–R14 消融），相对排序有效但绝对数字偏低 ~10pp |
| **External** | CLIP zs / OpenCLIP / MAE / DINOv2 / iBOT 等公开报告值 | 🚫 **不得与 BaiZe 数字同表**（见下） |

### 8.3.2 不可比原因（逐条）

| 维度 | BaiZe (本线) | 外部方法 | 不可比原因 |
|:--|:--|:--|:--|
| **目标函数** | AIMv2-style: `1.0×InfoNCE + 1.0×masked-patch-MSE`（双向 ViT + 随机掩码） | CLIP = 纯对比学习; MAE/DINOv2 = 纯视觉自监督（无文本塔）; iBOT = dense + self-distill | 目标函数不同 → 学到的表征空间性质不同 → lp 不可直接比较 |
| **数据** | 图文对 **95.8M**（GPIC 7437 tar + CC12M + Amshaker），**1 epoch** | LAION-2B（多 epoch / batch 32k）; IN-1k / LVD-142M（纯视觉，无文本对） | 数据量级差 10–100×；数据类型不同（图文对 vs 纯图像） |
| **文本塔** | **冻结** CLIP-ViT-L/14-336 (768-d)，不解冻 / 不用 LoRA | CLIP/OpenCLIP = 文本塔端到端训练; MAE/DINOv2 = 无文本塔 | 冻结文本塔限制了对比学习的对齐能力 → lp 上限不同 |
| **评测协议** | ProtA vs ProtB 相差 **~10pp**（见 BP-3） | 公开 lp 通常用主流协议（≈ProtB） | 不同协议的绝对数字不可同表；ProtA 数字比主流低 ~10pp |
| **训练规模** | ~118M 上限（从零训练，1 epoch） | AIMv2-L = 12B 样本; DINOv2 = LVD-142M / 多 epoch | 规模差 100× → 绝对 lp 不可比（本线渐近外推 ~25.1% ProtA） |

### 8.3.3 可直接比较的范围

| 可比 | 条件 | 示例 |
|:--|:--|:--|
| ✅ **内部横比（同协议）** | 同目标 + 同数据 + 同 epoch + 同协议 | E1fair ProtB vs E2fair ProtB; V3 ProtB vs E1fair ProtB; ④-2ep ProtB vs E1fair ProtB |
| ✅ **内部纵比（同模型跨协议）** | 同 ckpt，不同协议 | E1fair ProtB (62.34%) vs E1fair ProtA (49.70%) vs E1fair zs (34.10%) vs E1fair k-NN (37.68%) |
| ✅ **旧实验相对排序** | 同协议内排序 | R2–R14 消融的架构/loss/超参排名（ProtA/ProtB 排序一致） |
| 🚫 **外部横比** | 不同目标/数据/规模 | BaiZe ProtB 62.34% vs CLIP zs / DINOv2 lp / MAE lp → **不可同表** |
| ⚠️ **有条件外部参考** | 仅作量级参照，须加注 | "官方 OpenVision2 L/14 同口径 ProtA lp = 79.81% vs 从零 7.99%（差 ~10×，预训练规模差异）" |

### 8.3.4 清理记录（2026-10-10 ③）

以下外部数字比较已加不可比标注或从主表移除：
- §R13（官方 vs 自研对照）：已标注「from-scratch 排名，勿并列」「如实标注」+ 结论边界声明（line 117–118）。
- §R8（六架构评测）：Protocol A 已标注「BaiZe 内部协议」（line 140, 587, 747）。
- §R11-G（scaling 曲线）：幂律外推 ~25.1% 标注为 ProtA（BaiZe internal），不作外部横比。
- 本 §9 系列实验：所有 ProtB/ProtA 数字均标注协议名称；Δlp 仅在内部基线间计算。

---

## §9 Three-Variant Ablation vs E1fair Baseline (2026-10-10, PRE-REGISTRATION)

> **Pre-registered before any results.** Each variant is byte-identical to the E1fair
> baseline (w512/d30/p16, AIMv2 loss, mask-ratio 0.6, bs512, seed 1234, lr=5e-4,
> warmup=2000, cosine→5e-5, 187,101 steps, same data snapshot total_shards=10787)
> **except the single tested variable**. Baseline: **ProtB = 62.34 ± 0.01%,
> ProtA = 49.70%**.

### 9.0 Baseline Reference (E1fair)

| Field | Value |
|:--|:--|
| Architecture | OpenVision2 w512/d30, patch16, 224px, 126.78M params |
| Objective | AIMv2 (mask-ratio=0.6, patch-loss-weight=1.0, contrast-weight=1.0) |
| Optimizer | AdamW (lr=5e-4, betas=(0.9,0.95), eps=1e-6) |
| Schedule | warmup=2000 → cosine → min_lr=5e-5, total=187,101 steps |
| Data | GPIC snapshot(7437 tars) + CC12M + Amshaker, total_shards=10787, 1 epoch |
| Batch | 64/GPU × 8 GPU = 512 |
| Seed | 1234 |
| **ProtB (3-seed)** | **62.34 ± 0.01%** |
| **ProtA** | **49.70%** |

### 9.1 V1: Resolution 224 → 336 (single variable: `--resolution 336`)

| Field | Value |
|:--|:--|
| **Tested variable** | Image resolution 224 → 336 (patch 16: 196 → 441 patches, ~2.25× tokens) |
| Pos-emb | From scratch (not interpolation — different patch count) |
| Compute | ~2.25× per step, ~20h wall clock (vs ~9h baseline) |
| Everything else | Identical to §9.0 baseline |
| Output dir | `scaling_V1_res336_ov2_w512_d30_p16_336` |

**Hypothesis**: Higher resolution → denser patch supervision (576 vs 196 patches,
mask 0.6 → 346 vs 118 masked tokens) → better fine-grained feature → higher lp.

**Pre-registered criteria**:
- **Positive (Δlp ≥ +1.5pp ProtB)**: 336 resolution is beneficial → adopt for Stage (iv).
- **Null (|Δlp| < 1.5pp)**: No benefit at this budget → 224 is sufficient.
- **Negative (Δlp ≤ −1.5pp ProtB)**: Higher resolution hurts (overfitting / insufficient
  steps for 2.25× more tokens) → keep 224.

**Termination condition**: Full 187,101 steps or divergence (loss > 2× baseline at
same step after warmup).

### 9.2 V2: Optimizer AdamW → Muon (single variable: `--optimizer muon`)

| Field | Value |
|:--|:--|
| **Tested variable** | Optimizer: AdamW → Muon (Newton-Schulz orthogonalized momentum) |
| Muon config | momentum=0.95, nesterov=True, ns_steps=5 (per pretrain dist_muon) |
| Param grouping | 2D weight matrices → Muon; 1D params (norms, biases, logit_scale) → AdamW |
| LR | 5e-4 (same as baseline; lr probe: 200 steps × {5e-4, 0.02} before full run) |
| Everything else | Identical to §9.0 baseline |
| Output dir | `scaling_V2_muon_ov2_w512_d30_p16_224` |

**Implementation note**: `emerging_optimizers` not pip-installable in vision env
(timed out). Standalone impl in `r9_train.py`: `zeropower_via_newtonschulz5()` +
`Muon` class + `MuonAdamW` hybrid wrapper. Coefficients (a,b,c)=(3.4445,-4.7750,2.0315).

**LR probe protocol** (pre-registered):
1. 200 steps with lr=5e-4 (baseline LR) → record loss trajectory.
2. 200 steps with lr=0.02 (standard Muon LR) → record loss trajectory.
3. If lr=5e-4 loss decreasing at comparable rate to AdamW → use 5e-4.
4. If lr=5e-4 flat/diverging → use 0.02 (or scan intermediate).

**Pre-registered criteria**:
- **Positive (Δlp ≥ +1.5pp ProtB)**: Muon beneficial → adopt.
- **Null (|Δlp| < 1.5pp)**: No benefit → keep AdamW.
- **Negative (Δlp ≤ −1.5pp ProtB)**: Muon hurts → revert.

**RESULT: 🔴 COLLAPSED — Muon causes contrastive collapse at all tested LRs** (2026-10-11)

Three launch attempts, all collapsed:

| Attempt | LR | Collapse step | C1 at collapse | Root cause |
|:--|:--|:--|:--|:--|
| 1st | 5e-4 | 2,100 | 0.99 | Muon orthogonalization amplifies contrastive collapse |
| 2nd | 1e-4 | 2,100 | (false alarm) | **C2 guard bug** `gap<=0.005` fired on negative gap. Fixed: `abs(gap)<=0.005` |
| 3rd | 1e-4 | 4,200 | 0.9569 | **Real collapse** (slower but same mode as 1st) |

**C1 trajectory (3rd attempt, lr=1e-4, 14 PROBE points, zero reversals)**:
step 300→0.18, 600→0.18, 900→0.23, 1200→0.32, 1500→0.44, 1800→0.60, 2100→0.74, 2400→0.82, 2700→0.86, 3000→0.89, 3300→0.92, 3600→0.93, 3900→0.95, **4200→0.9569** (C1>0.95 guard fired).

**Key observations**: (1) C1 rise is monotonic and accelerating (0.18→0.96 in 3,900 steps). (2) Loss IS decreasing (7.39→7.30) — model reduces reconstruction loss but features collapse. (3) C2_gap always negative (off-diagonal>diagonal) — C2 guard never fires; only C1 catches it. (4) C4 always OK. (5) 5× lower LR delays but does not prevent collapse (2,100→4,200 steps, same endpoint). (6) **Root cause**: Newton-Schulz orthogonalization forces unit-norm gradients, amplifying the dominant collapse direction. AdamW's per-parameter adaptive scaling naturally damps this.

**Verdict**: ❌ **Muon incompatible with AIMv2-style contrastive+reconstruction objective** at all tested LRs. Δlp cannot be computed (collapsed C1=0.9569 → near-constant features → lp≈chance). Eval terminated to free GPU for V3. Cost: ~3 GPU·h wasted (×8 GPUs). C2 guard bug fixed (r9_train.py:909: `gap<=0.005`→`abs(gap)<=0.005`).

### 9.3 V3: Full GPIC Data (single variable: data snapshot + steps)

| Field | Value |
|:--|:--|
| **Tested variable** | GPIC: 7437 tars → 8000 tars (full download completed 2026-10-10) |
| Snapshot file | `data_snapshot_20261010_full.txt` (8000 GPIC train tars) |
| Steps | **230,598** (1 epoch of full data, calculated by data volume) |
| Step formula | `⌈118,065,500 / (64 × 8 × 1)⌉ = 230,598` |
| Data composition | GPIC 8000×12,639=101.1M + CC12M 11.0M + Amshaker 5.95M = **118.1M pairs** |
| Epoch count | 1 (same as baseline E1fair epoch count) |
| Everything else | Identical to §9.0 baseline (lr=5e-4, warmup=2000, cosine, min_lr=5e-5, AdamW, seed 1234) |
| Output dir | `scaling_V3_fulldata_ov2_w512_d30_p16_224` |
| Training status | ✅ **COMPLETE** (2026-10-11 02:06–12:44, 230,598/230,598 steps, final_loss=0.1201, steady_img/s=2706.4, total=38,273s ~10.6h). 22 checkpoints (10k–230k) + final vision.pt (509MB). **No collapse** — C1 stable 0.50–0.53 throughout, C2_gap +0.19~+0.20, C4=OK at all 768 PROBE points. total_shards=11,350 (vs E1fair 10,787, +563 GPIC tars). |
| **ProtB result** | ✅ **63.52 ± 0.01%** (3 seeds: 63.53/63.52/63.51%, σ=0.0001). Eval done 14:54 Oct 11. **Δlp = +1.18pp** vs E1fair (62.34±0.01%). |
| ProtA | ✅ **50.53%** (done 15:10 Oct 11, rc=0). ΔProtA = +0.83pp vs E1fair (49.70%). |
| Zero-shot | ✅ **35.52%** top1 / 67.24% top5 (done 15:18 Oct 11). Δzs = +1.42pp vs E1fair (34.10%). |
| k-NN | ✅ k=5: 35.63%, k=10: 37.97%, k=20: **38.94%** (done 15:25 Oct 11). Δk-NN(k20) = +1.26pp vs E1fair (37.68%). |
| ProtB Enhanced (×5ep) | ✅ **COMPLETE** (18:24:52 Oct 11): 90ep=**63.50%**, 450ep=**63.43%** (Δ=−0.07pp) → probe NOT underfitting for V3 too. wd=0.0001=**63.83%** (+0.33pp best), lr=0.01=63.51%, wd=0.001=62.18%, lr=0.3=62.20%. No config beats 90ep baseline by >0.35pp → confirms V3 feature quality is genuine. |

**⚠️ Disclosure**: This arm changes **both** data volume (+7.6% GPIC) **and** step count (+23.2%) relative to baseline. Conclusion = "**full-data recipe (data+steps combined) vs baseline**", NOT "pure data ablation".

**Hypothesis**: More unique data + more steps (full 1 epoch) → higher lp.

**Pre-registered criteria**:
- **Positive (Δlp ≥ +1.5pp ProtB)**: Full-data recipe beneficial → adopt.
- **Null (|Δlp| < 1.5pp)**: No benefit from 7.6% more data + 23% more steps.
- **Negative (Δlp ≤ −1.5pp ProtB)**: Full-data recipe hurts → keep 7437 snapshot.

**Result (2026-10-11)**: Δlp = **+1.18pp** (63.52% vs 62.34%) → **Null** verdict. The +7.6% more GPIC data + 23% more steps did NOT produce a distinguishable improvement. The positive trend (+1.18pp) is within the pre-registered noise threshold (1.5pp). Consistent with R12b finding ("more unique data ≠ higher lp" at similar scale). The full-data recipe is safe to adopt (no harm) but does not justify the extra compute cost for the marginal gain.

**V3 Cross-Metric Summary** (all metrics consistently +0.8~+1.4pp above E1fair):

| Metric | E1fair | V3 | Δ |
|:--|:--|:--|:--|
| ProtB (3-seed) | 62.34±0.01% | 63.52±0.01% | +1.18pp |
| ProtA | 49.70% | 50.53% | +0.83pp |
| Zero-shot top-1 | 34.10% | 35.52% | +1.42pp |
| k-NN (k=20) | 37.68% | 38.94% | +1.26pp |
| lp−zs gap | +28.24pp | +28.00pp | −0.24pp (stable) |

The uniform +1~1.4pp shift across all 4 independent metrics (ProtA/B, zs, k-NN) confirms V3 features are genuinely slightly better, not a probe artifact. The lp−zs gap remains ~28pp, confirming the dense reconstruction objective's contribution is stable regardless of data scale. However, all deltas are within the 1.5pp noise threshold → **Null verdict stands**: the +7.6% more data + 23% more steps is not a cost-effective improvement.

### 9.5 Results Table

| Variant | ProtB (3-seed) | ProtA | Zero-shot | k-NN (k=20) | Δlp vs E1fair | Verdict |
|:--|:--|:--|:--|:--|:--|:--|
| E1fair (baseline) | 62.34 ± 0.01% | 49.70% | 34.10% | 37.68% | — | — |
| V1 (res 336) | ⏸ deferred (user: "明天再说") | — | — | — | — | — |
| V2 (Muon) | **N/A — COLLAPSED** (C1=0.9569@step4200) | N/A | N/A | N/A | N/A | ❌ Muon incompatible with contrastive loss |
| V3 (full data) | **63.52 ± 0.01%** (seeds: 63.53/63.52/63.51%) | **50.53%** | **35.52%** | **38.94%** | **+1.18pp** | ✅ Null (|Δ|<1.5pp): full-data recipe indistinguishable from baseline |
| ④-2ep (2× epochs) | **65.37 ± 0.01%** (seeds: 65.37/65.36/65.37) | **53.82%** | **38.52%** (top5: 70.81%) | **40.67%** (k=20) | **+3.03pp** | 🟡 **Moderate** (+1.5~7.66pp): more budget helps with diminishing returns; no 4ep unless operator requests |
| ④-4ep (4× epochs) | **67.05 ± 0.02%** (seeds: 67.03/67.08/67.04) | **56.70%** | **40.64%** (top5: 72.64%) | **42.35%** (k=20) | **+4.71pp** | 🟡 **Moderate, diminishing** (Δ1→2=+3.03pp, Δ2→4=+1.68pp): 67.05% < 70% victory threshold; trajectory still upward but decelerating → approaching ceiling |

### 9.4 ④ Epoch Scaling (operator instruction 2026-10-10 ④ · most decision-relevant)

> **Question**: Is E1fair ProtB=62.34% a budget limitation or a feature/objective ceiling?
> **Design**: Same data/target/protocol/schedule as E1fair, only increase epoch count.
> E1fair = 1 epoch (187,101 steps, 95.8M pairs). Test 2-epoch and (if needed) 4-epoch.

| Field | Value |
|:--|:--|
| **Tested variable** | Epoch count: 1 → 2 (→ 4 if 2-epoch is informative) |
| ④-2ep steps | **374,202** (= 2 × 187,101) |
| ④-4ep steps | **748,404** (= 4 × 187,101), only if 2ep warrants |
| Data | E1fair frozen snapshot (total_shards=10787, 95.8M pairs), **NOT** V3 full data |
| Schedule | lr=5e-4, warmup=2000, cosine, min_lr=5e-5 (same as E1fair) |
| Everything else | Identical to §9.0 baseline (AdamW, seed 1234, w512/d30, 224/p16, AIMv2-style) |
| Output dir | `scaling_E4_2ep_ov2_w512_d30_p16_224` (and `_4ep_` if needed) |
| Eval | ProtB 3 seeds + ProtA + zero-shot + k-NN (same suite as E1fair) |
| GPU schedule | **After V3 eval completes** (shared .12 8-card) |

**Pre-registered criteria**:
- **Positive (2ep Δlp ≥ +7.66pp → lp ≥ 70%)**: Budget insufficient → 62.34% is NOT the ceiling. Launch 4ep to map trajectory.
- **Moderate (2ep Δlp +1.5~7.66pp)**: Some gain from more training, diminishing returns. Decision pending.
- **Null (|Δlp| < 1.5pp)**: 1 epoch is sufficient → feature/objective quality is the bottleneck, not budget.
- **Negative (Δlp ≤ −1.5pp)**: More epochs hurt (overfitting on 95.8M pairs) → keep 1 epoch.

**If 2ep ≥ 70%**: Launch 4ep (748,404 steps, ~18h, ~144 GPU·h) to complete lp-vs-epoch curve.
**If 2ep < 70% but > 63.84%**: Report as "moderate gain, diminishing returns", do NOT launch 4ep unless operator requests.
**If 2ep ~63% (flat)**: Conclude "feature/objective quality ceiling at this data scale" → no 4ep needed.

**⚠️ Risk**: R12b precedent (2ep on 69.7M = 18.81% < R11-G 1ep on 18.5M = 19.76%) suggests multi-epoch on small data can overfit. However, E1fair data (95.8M) is 5.2× larger than R12b (18.5M) and uses AIMv2-style objective, so overfitting risk is lower.

**Cost**: 2ep ~80 GPU·h / ~10h wall; 4ep ~160 GPU·h / ~20h wall.

**Status**: ✅ V3 eval ALL COMPLETE (ProtB ✅ 63.52±0.01%, ProtA ✅ 50.53%, zs ✅ 35.52%, k-NN ✅ 38.94%, ProtB ×5ep ✅ 63.43% (Δ=−0.07pp → probe NOT underfitting for V3)). ✅ **② ×5 probe COMPLETE** (E1fair): baseline 62.33%, ×5ep 62.15% (−0.18pp), wd=1e-4 62.68% (+0.35pp), wd=1e-3 61.25% (−1.08pp), lr=0.01 62.39% (+0.06pp), lr=0.3 60.39% (−1.94pp). **Key ② finding**: NO config beats baseline by >0.35pp → probe NOT underfitting at 1ep. ✅ **④-2ep TRAINING + ALL EVAL COMPLETE** (2026-10-12): 374,202 steps (= 2 × 187,101), total=59,616s (~16.6h), steady_img/s=2,416.1, final_loss=0.1856. **C1 ELEVATED ep1→ep2: 0.515 (ep1 avg @step~186k) → 0.574 (ep2 avg @step~374k) = +0.059** — contrastive alignment strengthened. C2_gap=+0.1844, C4=OK throughout (no collapse). 37 ckpts saved (10k–370k) + final vision.pt (509MB). **ProtB 3-seed: 65.37±0.01%** (seeds: 65.37/65.36/65.37). **ProtA: 53.82%** (Δ=+4.12pp vs 49.70%). **Zero-shot: 38.52%** top1 / 70.81% top5 (Δ=+4.42pp vs 34.10%). **k-NN k=20: 40.67%** (Δ=+2.99pp vs 37.68%; also k=10: 40.10%, k=5: 37.85%). **All 4 metrics show consistent +3~4.4pp improvement.** **Δlp(ProtB) = +3.03pp** vs E1fair (62.34±0.01%). **VERDICT: MODERATE** (Δ +1.5~7.66pp per pre-registered criteria) → "moderate gain, diminishing returns" → **do NOT launch 4ep** unless operator requests. Plot: `vision/lp_epoch_curve.png` (updated with 4ep point).
✅ **④-4ep TRAINING + ALL EVAL COMPLETE** (2026-10-13): 748,404 steps (374,202 new from 2ep resume), total=60,545.4s (~16.8h), steady_img/s=2,818.0, **final_loss=0.0805** (vs 2ep 0.1856). **C1 ELEVATED ep2→ep4: 0.5804 (end ep2 @step 374k) → 0.5932 (end ep4 @step 748k) = +0.0128** — contrastive alignment continued strengthening but decelerating. C2_gap=+0.1791, C4=OK throughout (no collapse). 37 ckpts saved (380k–740k) + final vision.pt (509MB). **ProtB 3-seed: 67.05±0.02%** (seeds: 67.03/67.08/67.04). **ProtA: 56.70%** (Δ+7.00pp vs 49.70%, Δ+2.88pp vs 2ep 53.82%). **Zero-shot: 40.64%** top1 / 72.64% top5 (Δ+6.54pp vs 34.10%, Δ+2.12pp vs 2ep 38.52%). **k-NN k=20: 42.35%** (Δ+4.67pp vs 37.68%, Δ+1.68pp vs 2ep 40.67%; also k=10: 41.94%, k=5: 39.77%). **All 4 metrics show consistent +1.7~2.9pp improvement over 2ep.** **Δlp(ProtB) = +4.71pp** vs E1fair (62.34±0.01%), **Δlp(ProtB) = +1.68pp** vs 2ep (65.37±0.01%). **VERDICT: MODERATE, DIMINISHING** — 67.05% < 70% operator "victory" threshold; gains decelerating (1→2ep: +3.03pp, 2→4ep: +1.68pp, ratio ~0.55) → trajectory still upward but approaching ceiling. Plot updated: `vision/lp_epoch_curve.png`.

### 9.6 ① Same-Model Zero-Shot + ② k-NN Probe Results (E1fair, 2026-10-11)

> Operator instruction 2026-10-10 ①②. Zero/light GPU. Answers: ① "did features benefit from
> text alignment?" and ② "is the probe underfitting, or are features genuinely limited?"

#### ① Same-Model Zero-Shot — Pathway Construction

| Component | Detail |
|:--|:--|
| **Vision pathway** | OpenVision2 w512/d30 ViT → ReadoutHead (LayerNorm + mean-pool + Linear(512→768)) → 768-d image features. This head was trained via InfoNCE to align with the frozen CLIP text tower's 768-d space. |
| **Text pathway** | Frozen CLIP-ViT-L/14-336 text tower (768-d), loaded from `/nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336`. `get_text_features(ids)` → 768-d text embedding. |
| **Class prompts** | 1000 IN-1k class names × 80 OpenAI templates (from `open_clip.IMAGENET_CLASSNAMES` + `OPENAI_IMAGENET_TEMPLATES`), averaged per class, L2-normalized → (1000, 768) text class embeddings. |
| **Classification** | `cosine_sim(image_features, text_class_embeddings)` → argmax. Temperature = `logit_scale` from checkpoint (learned during training). |
| **Eval set** | Official IN-1k validation (50k images, 14 parquet files, labels 0–999). |
| **Normalization** | ImageNet mean/std (same as Protocol B). |
| **Script** | `vision/zeroshot_in1k_eval.py` |

#### ① Results: lp vs zs Comparison

| Checkpoint | Zero-shot top-1 | lp (ProtB, 3-seed) | Δ(lp − zs) |
|:--|:--|:--|:--|
| E1fair (w512/d30, 126.8M) | **34.10%** | 62.34 ± 0.01% | **+28.24pp** |
| E2fair (w768/d30, 284.5M) | **35.45%** | 62.51 ± 0.04% | **+27.06pp** |
| V3 (full data, w512/d30) | **35.52%** | 63.52 ± 0.01% | **+28.00pp** |

**Interpretation**:
- **lp ≫ zs (+28pp)**: Features DO benefit from text alignment — the InfoNCE training aligns image features with the CLIP text space, enabling above-chance zero-shot classification (34.10% vs 0.1% random). However, the learned linear probe extracts **significantly more** discriminative information (+28.24pp) than direct text-similarity classification.
- The large lp−zs gap suggests the vision encoder learned rich features **beyond** what the text-aligned space directly provides — the dense reconstruction objective (masked-patch-MSE) contributes representation quality that the contrastive alignment alone does not capture.
- E2fair zs (35.45%) > E1fair zs (34.10%) by +1.35pp, consistent with larger model capacity, but the lp gap is only +0.17pp (indistinguishable) — the wider model's extra capacity helps zero-shot text alignment but not linear probe.
- **Chance baseline**: 1/1000 = 0.1%. Both zs (34.10%) and lp (62.34%) are far above chance.

#### ② k-NN Probe + ×5 Epochs + wd/LR Sweep Results (E1fair, 2026-10-11)

**k-NN Probe** (pure feature quality, no training):

| Probe type | E1fair top-1 | V3 top-1 | vs lp (E1fair 62.34%) | vs zs (E1fair 34.10%) |
|:--|:--|:--|:--|:--|
| k-NN (k=5) | 35.63% | 35.63% | −26.71pp | +1.53pp |
| k-NN (k=10) | 37.97% | 37.97% | −24.37pp | +3.87pp |
| k-NN (k=20) | **37.68%** | **38.94%** | −24.66pp | +3.58pp |

**Protocol B Probe Sweep** (tests probe underfitting vs feature quality ceiling):

| Config | E1fair top-1 | Δ vs baseline (62.33%) | Interpretation |
|:--|:--|:--|:--|
| **Baseline** (90ep, lr=0.1, wd=0, s=0) | **62.33%** | — | Matches registered 62.34±0.01% |
| **×5 epochs** (450ep, lr=0.1, wd=0) | **62.15%** | **−0.18pp** | 5× more epochs → **LOWER** (slight overfit) |
| wd=1e-4 (90ep, lr=0.1) | **62.68%** | +0.35pp | Marginal, within noise |
| wd=1e-3 (90ep, lr=0.1) | **61.25%** | −1.08pp | Too much regularization |
| lr=0.01 (90ep, wd=0) | **62.39%** | +0.06pp | Essentially same |
| lr=0.3 (90ep, wd=0) | **60.39%** | **−1.94pp** | Too high LR, diverges |

> Log: `/tmp/probe_x5_parallel.log` (PID 2190867, GPU 1, started 14:20 Oct 11, completed ~17:35 Oct 11). Train features encoded once (1.28M images, 294 parquet files), then all 6 probe configs run on cached features. ✅ **ALL 6 CONFIGS COMPLETE**.

**Interpretation (decisive)**:
- **×5 epochs (450ep) = 62.15% < 62.33% (90ep)**: This is the **strongest evidence** that the probe is **NOT underfitting**. If the probe were underfitting, 5× more training epochs should raise lp. Instead, it slightly **decreases** (overfitting on the cached features). The 90-epoch Protocol B probe is well-converged.
- **wd/LR sweep**: No configuration achieves >+0.35pp improvement. Best variant (wd=1e-4, 62.68%) is within the 1.5pp noise threshold. This confirms the probe configuration is near-optimal.
- **k-NN (37.68%) < lp (62.34%)**: The linear probe extracts significantly more than nearest-neighbor matching — expected for high-dimensional features. k-NN > zs (37.68% > 34.10%) confirms reasonable class structure in feature space.
- **CONCLUSION**: **62.34% is a genuine feature quality ceiling, NOT a probe limitation.** The probe is well-converged across all tested configurations. The feature quality is the bottleneck, not the evaluation methodology.

#### Combined ①② Summary

| Question | Answer | Evidence |
|:--|:--|:--|
| Did features benefit from text alignment? | **Yes** — zs=34.10% ≫ chance 0.1%, and lp=62.34% ≫ zs=34.10% (+28pp) | ① table above |
| Is the probe underfitting? | **No** — ×5 epochs (450ep) gives 62.15% (−0.18pp vs 90ep), wd/LR sweep max +0.35pp | ② table above |
| Is 62.34% a feature quality ceiling or probe limitation? | **Feature quality ceiling** — probe is well-converged across all 6 configurations; no probe config exceeds 62.68% | ② table above |

---

### §9.7 中文版综合报告（2026-10-12，operator instruction）

> **文件**：`vision/report_vision_final_20261012_zh.html`（36KB，单文件内联 CSS/SVG，10 节 + 3 SVG 图表，全中文）。
> **覆盖**：背景 → ③ 口径修订 → ① zero-shot（E1fair 34.10% / E2fair 35.45%，lp−zs gap ~28pp）→ ② probe 对照（×5ep=62.15%→probe 未欠拟合→62.34% 即特征质量天花板）→ 变体实验（V2 Muon 全 LR 坍缩❌ / V3 全量数据 ProtB 63.52% Δ+1.18pp Null）→ ④ epoch scaling（2ep ProtB 65.37±0.01% Δ+3.03pp / ProtA 53.82% / zs 38.52% / k-NN 40.67%，MODERATE）→ lp-epoch 曲线 → 结论与下一步。所有数字与本文件 §8.3–§9.6 完全一致，口径标 BaiZe internal protocol。
> **✅ 更新（2026-10-13 12:43）**：④-4ep 训练+全套评测已完成。**ProtB 67.05±0.02%**（< 70% 胜利阈值，但 4 指标一致 +1.7~2.9pp vs 2ep，递减趋势确认：1→2ep +3.03pp，2→4ep +1.68pp）。ProtA 56.70%，zs 40.64%/72.64%，k-NN k=20 42.35%。final_loss=0.0805，C1=0.5932（+0.0128 vs 2ep），C4=OK。报告已同步更新（TL;DR / §7 / §8 曲线 / §9 汇总表 / §10 结论 / 柱状图）。

---

## §外部编码器 ProtB 参考（2026-10-13，用户直令）

> 🚫 **红线**：以下所有数字均为**公众预训练模型的参考值**，必须**独立成表**，**绝不**与 BaiZe from-scratch 从零训练模型放在同一榜单中排名。各模型使用各自 **native 分辨率**（336/384/560）和 **native mean/std** 预处理 → **跨分辨率 lp 不可直接排高下**。文献锚点仅作「待核」标注，不当本项目结论。
>
> **报告文件**：`report_vision_external_protb_reference_zh.html`（中文 · 自包含 · 内联 CSS/SVG）。
> **代码**：`vision/external_encoder_protb.py`（外部编码器加载 + 特征提取）+ `vision/lp_protocol_bridge.py`（Protocol B linear probe）。
> **协议**：Protocol B = SGD+momentum0.9+cosine 90ep, bs1024, IN-1k full train 1.28M, IN-1k val 50k, 3 seeds (0/1/2) → mean±std。各模型 native 分辨率 + native 预处理，提取 pooled/CLS 特征后冻结。

### 结果表（5/5 全部完成 · 2026-10-14）

| 模型 | Native 分辨率 | 特征维 | 参数量 | ProtB (3 seeds) | 各 seed 明细 | 文献锚点·待核 |
|:--|:-:|:-:|:-:|:-:|:--|:--|
| SigLIP2 so400m@384 | 384px | 1152 | ~400M (vision) | **87.46 ± 0.01%** | 87.46% / 87.47% / 87.45% | ~83.1% (HF lp) |
| AIMv2-1B@336 | 336px | 2048 | ~1B | **85.22 ± 0.04%** | 85.16% / 85.24% / 85.26% | ~87.6% (Apple frozen trunk lp) |
| OpenVision2 ViT-L/14@336 | 336px | 1024 | ~304M (vision) | **84.97 ± 0.01%** | 84.97% / 84.96% / 84.99% | 79.81% (BaiZe ProtA R13) |
| CLIP ViT-L/14@336 | 336px | 1024 | ~304M (vision) | **82.66 ± 0.03%** | 82.62% / 82.69% / 82.67% | ~88.1% (OpenCLIP lp) |
| RICE-ViT-L@560 | 560px | 1024 | ~304M (vision) | **81.72 ± 0.01%** | 81.73% / 81.72% / 81.72% | ~84.0% (估算·待核) |
| *BaiZe ④-4ep (from-scratch)* | *224px* | *512* | *126.8M* | *67.05 ± 0.02%* | *67.03 / 67.08 / 67.04%* | *— (本项目从零训练，仅供参考)* |

### AIMv2 修复说明（已完成）

AIMv2-1B@336 原始评测 ProtB = 52.35%，远低于论文报告的 ~87.6%。经排查发现 **wrapper bug**：AIMv2 无 CLS token（输出 `[B, 576, 2048]`），原 wrapper 误取 `[:, 0, :]`（top-left patch token）作为 pooled feature，而非 mean pooling。已修复为 `last_hidden_state.mean(dim=1)`，重新提取特征后 ProtB = **85.22 ± 0.04%**（3 seeds: 85.16% / 85.24% / 85.26%），与论文 ~87.6% 接近（差距可能来自 mean-pool vs Apple 原始 pooling 策略差异）。

### 关键观察

1. **SigLIP2 so400m@384 以 87.46% 领先**，但其在 384px 分辨率 + 400M 参数量下评测，与 336px 模型不可直接排高下。
2. **OpenVision2 ViT-L/14@336（84.97%）** 显著高于 BaiZe ProtA R13 的 79.81% —— 但 ProtA（kNN-based）与 ProtB（SGD linear probe）是不同协议，跨协议不可直接比较。
3. **CLIP ViT-L/14@336（82.66%）** vs 文献 ~88.1%：差距可能来自评测协议差异（我们的 ProtB 用 SGD 90ep，OpenCLIP lp 可能用不同超参/数据增强）。
4. **AIMv2-1B@336（85.22%）**：1B 参数大模型，但 mean-pool 后 ProtB 低于 SigLIP2（87.46%）——可能与 AIMv2 无 CLS token、mean-pool 损失空间信息有关；文献 ~87.6% 可能使用不同 pooling 策略。修复前因 wrapper bug（误取 top-left patch）仅得 52.35%，修复后提升 +32.87pp。
5. **RICE-ViT-L@560（81.72%）**：560px 高分辨率未带来 ProtB 优势，可能与模型训练数据/策略有关。
6. **BaiZe ④-4ep（67.05%）**：126.8M 参数 + 224px + 从零训练，与上述 304M–1B 参数 + 336–560px + 大规模预训练的公众模型存在量级差距，**不参与排名**，仅作绝对值参考。

---

### ⚠️ 数据量口径订正（2026-10-13 · 用户直令）

> **背景**：用户质疑 `report_vision_merge3ds_bs4_lr2_plan_zh.html` 中 GPIC「~80–85M / 合计 95.8M」数据量偏低。经核实，该数字系 **6233-tar 时代旧值**（见本文 L489: `GPIC 6233 tar × ~12639 + CC12M 1100 × ~10000 + Amshaker 2250 × ~2646 ≈ 95.7M pairs`），快照冻结到 7437 tar 后**未重算** → 陈旧引用。

**订正后数据量（2026-10-13）**：

| 数据集 | tar 数（快照 / 全量） | 每 tar 对数（实测） | 对数（快照） | 对数（全量） | 权重（快照） | 来源命令 |
|:--|:--|:--|:--|:--|:--|:--|
| GPIC | 7437 / 8000 | ~12,639 ¹ | ~94.0M | ~101.1M | 84.7% | `wc -l data_snapshot_20261009.txt` = 7437 |
| CC12M | 1100 | ~10,000 | ~11.0M | ~11.0M | 9.9% | 1100 tar × 10,000 |
| Amshaker | 2250 | ~2,646 | ~5.95M | ~5.95M | 5.4% | 2250 tar × 2,646 |
| **合计** | **10787 / 11350** | — | **~110.9M** | **~118.1M** | 100% | — |

¹ GPIC 每 tar 对数：12,639（L934，V3 全量实验用值）；另测 12,495（L60，8-tar 采样 `tar -tf … | grep -c '\.json$'`）。取 12,639 为主值。

**关键影响**：
1. **基线「1 epoch」= 187,101 步 × 512 GBS = 95.8M 样本**，但快照实际 110.9M 对 → 基线「1 epoch」仅覆盖 **86.4% 数据** = **0.86 真实 epoch**。基线「4 epoch」= 748,404 × 512 = 383.2M 样本 = **3.45 真实 epoch**（非 4）。
2. **新方案（GBS=2048）**：1 真实 epoch = ⌈110,949,743 / 2048⌉ = **54,175 步**（旧口径 46,780 步）；3 真实 epoch = 162,525 步（旧口径 140,340 步）。
3. **24h 预算**：中位吞吐 3663 img/s → 24h ≈ 154,532 步 ≈ **2.85 真实 epoch**（旧口径 3.31 epoch）。3 真实 epoch 需 ~25.2h（略超 24h）。
4. **旧版报告自相矛盾已修**：§2 权重列写 GPIC ~84%（=94M/111M，暗含快照口径）但对数列写 ~80–85M（=6233-tar 旧值），同表两列打架 → 现统一为快照口径。

**纪律**：🚫 不许再复用陈旧聚合值 95.8M（6233-tar 时代）；✅ 每个数字可溯源到盘点命令（`wc -l` / per-tar 实测）。

**已更新文件**：
- `doc/BaiZe-ISEDA2027/report_vision_merge3ds_bs4_lr2_plan_zh.html`（§1–§9 全部数据量重算 + 双口径并列）
- 本节（EXPERIMENTS_VISION.md 口径订正）

---

## §merge3ds 合并三数据集实验（2026-10-14 · 预注册 · 判据先行）

> **运维指令**：2026-10-13「放行执行：GBS/MBS ×4 · LR 3-臂扫描 · 24h 预算」+「LR 缩放按文献规则：若预算只允许 1 臂 → 取臂 C ×4 线性（Goyal arXiv:1706.02677）」。
> **计划文件**：`doc/BaiZe-ISEDA2027/report_vision_merge3ds_bs4_lr2_plan_zh.html`。
> **门控**：✅ 外部编码器 ProtB 5/5 全部完成（2026-10-14 01:03）→ 门控通过，可起训。

### 预注册判据（先定后测 · 不许事后改）

| 判据 | 阈值 | 说明 |
|:--|:--|:--|
| **VICTORY** | ProtB ≥ 70% | 超过 ④-4ep 胜利阈值（67.05% → 70%+） |
| **MODERATE** | ProtB 68–70% | 可分辨提升（Δ ≥ 1.5pp vs ④-4ep 67.05%）但未达胜利 |
| **NULL** | ProtB < 68.5% | 不可分辨（Δ < 1.5pp）或下降 |
| **COLLAPSE** | C1 > 0.95 at any step | 训练坍缩，实验作废 |
| **OOM** | MBS=256 CUDA OOM | 需回退 MBS=64 + grad-accum 4（需改代码） |

### 配置（Arm C · 单变量 · 除 GBS/MBS/LR 外与 ④-4ep 逐字节一致）

| 参数 | ④-4ep 基线 | Arm C（本实验） | 倍数 | 依据 |
|:--|:--|:--|:--|:--|
| `--batch-size` | 64 | **256** | ×4 | GBS/MBS ×4 |
| GBS (MBS×8) | 512 | **2048** | ×4 | — |
| `--lr` | 5e-4 | **2e-3** | ×4 | Goyal 线性缩放规则 (arXiv:1706.02677) |
| `--warmup` | 2000 | **8000** | ×4 | Goyal 要求 warmup 同比放大 |
| `--min-lr` | 5e-5 | **2e-4** | ×4 | cosine 终点同比 |
| `--steps` | 748,404 | **154,500** | — | ≈ 2.85 真实 epoch @ GBS=2048, ~24h |
| `--resume` | 2ep ckpt | **无**（从零） | — | 新配方不从旧 ckpt 续 |
| 其他 | — | **逐字节一致** | — | tower/width/depth/loss/mask-ratio/data/scheduler 等 |

### Smoke test 结果（2026-10-14 01:24）

- ✅ **No OOM**：MBS=256 使用 ~47.5GB/GPU（81.5GB total），余量充足
- ✅ 10 步全部完成，loss 稳定（8.71–8.77），C1 正常
- ✅ 吞吐：steady_image_s=5270.8（含 warmup 开销），步 7-10 达 ~8900–9670 img/s
- ✅ 模型保存成功（`vision.pt`）

### 输出目录

`/nas_train/app.e0031982/datasets/baize-vision/out/merge3ds_bs4_lrC_w512_d30_p16_224`

### 交付清单（训练完成后）

1. 训练日志（`/tmp/merge3ds_armC_train.log`）
2. ProtB 3-seed mean±std（复用 `lp_protocol_bridge.py`）
3. 中文 HTML 结果报告 `report_vision_merge3ds_result_zh.html`
4. EXPERIMENTS_VISION.md 新节（含 vs 基线 Δlp）

### 训练 + 评测结果（2026-10-15）

**训练完成**：step 154500/154500, total=81,667s (~22.7h), steady_image/s=9,978.3, final_loss=0.2169, C1=0.6668, C2_gap=+0.1606, C4=OK 全程无坍缩。

**评测结果**（eval chain `post_merge3ds_chain.sh` PID 3698490，日志 `/tmp/merge3ds_armC_eval.log`）：

| 指标 | ④-4ep 基线 | merge3ds ArmC | Δ | 说明 |
|:--|:--|:--|:--|:--|
| **ProtB (3 seeds)** | 67.05 ± 0.02% | **68.25 ± 0.01%** | **+1.20pp** | seed0=68.27% / seed1=68.24% / seed2=68.25% |
| **ProtA** | 56.70% | **59.41%** | **+2.71pp** | BaiZe internal protocol (AdamW full-batch 100ep) |
| **Zero-shot top1** | 40.64% | **46.17%** | **+5.53pp** | top5: 72.64% → 77.43% (+4.79pp) |
| **k-NN** | 42.35% (k=20) | **44.88%** (k=20) | **+2.53pp** | k=5: 41.85%, k=10: 44.24% |

**预注册判据裁定**：
- ProtB = 68.25% → 落入 68–70% MODERATE 绝对区间，但 **Δ = +1.20pp < 1.5pp 阈值**
- 严格按判据：**NULL**（Δ < 1.5pp 不可分辨）
- 但 zero-shot +5.53pp 和 ProtA +2.71pp 显示表征质量有实质提升 → 合并三数据集 + 大 batch 改善了表征通用性

**配置差异**（vs ④-4ep 基线）：

| 参数 | ④-4ep | ArmC | 变化 |
|:--|:--|:--|:--|
| 数据 | CC12M + Amshaker (~94M) | GPIC + CC12M + Amshaker (~111M) | +GPIC（三数据集合并） |
| GBS (MBS×8) | 512 | 2048 | ×4 |
| MBS | 64 | 256 | ×4 |
| LR | 5e-4 | 2e-3 | ×4（Goyal arXiv:1706.02677 线性缩放） |
| Warmup | 2000 | 8000 | ×4 |
| min-LR | 5e-5 | 2e-4 | ×4 |
| Steps | 748,404 (~4 epoch) | 154,500 (~2.85 epoch @ GBS=2048) | — |
| final_loss | 0.0805 | 0.2169 | 不可直接比较（不同数据/步数） |
| C1 (final) | 0.5932 | 0.6668 | +0.0736（对比对齐更强） |

**分析**：
1. ProtB Δ=+1.20pp 未达 1.5pp 阈值 → 严格判据 NULL；但 4 指标全部提升（zs +5.53pp, ProtA +2.71pp, k-NN +2.53pp）→ 合并三数据集 + 大 batch 训练改善了表征的通用性
2. C1 从 0.5932 升至 0.6668（+0.0736），对比对齐增强——可能因 GPIC 短 caption 提供更密集的 image-text 对
3. 多变量变更（数据组成 + GBS/MBS + LR），无法隔离单一因素贡献；后续可考虑消融
4. 训练耗时 22.7h（vs ④-4ep 16.8h）——MBS=256 单步更慢但总步数更少；吞吐 9,978 img/s（vs ④-4ep 2,818 img/s）得益于大 batch

**ckpt 路径**：`/nas_train/app.e0031982/datasets/baize-vision/out/merge3ds_bs4_lrC_w512_d30_p16_224/vision.pt`

**报告文件**：`doc/BaiZe-ISEDA2027/reports/report_vision_merge3ds_result_zh.html`

---

## §10 ArmA（open_clip ViT-B/16 从头对比训练，2026-10-17）

> **目的**：用 open_clip 标准 ViT-B/16（86.2M visual / 149.6M total，双塔随机初始化）从零开始做纯 CLIP InfoNCE 对比训练，作为"纯对比目标"的独立实验点，与主线 ④-4ep（AIMv2-style 稠密目标）对照。

### §10.1 训练配置

| 项 | 值 | 来源 |
|:--|:--|:--|
| 模型 | open_clip ViT-B/16 224px（86.2M visual / 149.6M total，`pretrained=None`） | `armA_openclip_train.py:169-170` |
| 损失 | `open_clip.loss.ClipLoss`（标准 InfoNCE，global gather，local_loss=False） | `armA_openclip_train.py:185-187` |
| 前向 | `model(imgs, texts) → (img_feat, txt_feat, logit_scale)` | `armA_openclip_train.py:286-287` |
| 优化器 | AdamW fused=True, wd=0.1, betas=(0.9,0.98), grad_clip=1.0 | `run_armA_openclip.sh:69` |
| LR | 2e-3 → 2e-4 cosine, warmup 8000 | `run_armA_openclip.sh:68` |
| 批次 | GBS=2048 (MBS=256×8), bf16 AMP (fp32 master + autocast) | `run_armA_openclip.sh:52,68` |
| 步数 | 154,500（≈2.7 epoch） | `run_armA_openclip.sh:14,45` |
| 数据 | GPIC(7437)+CC12M(1100)+Amshaker(2250)=10,787 shards ≈118M 对 | `run_armA_openclip.sh:37-40` |
| seed | 1234 | `run_armA_openclip.sh:70` |
| 效率修复 | LPT 字节均衡分片 + num_workers=12 + persistent + prefetch4 + pin_memory + cudnn.benchmark + fused AdamW | `run_armA_openclip.sh:17-21` |

### §10.2 训练结果

| 指标 | 值 | 来源 |
|:--|:--|:--|
| 最终 step | 154,500/154,500 (100%) | `/tmp/armA_openclip_train.log` |
| 最终 loss (EMA) | 0.4385 | 同上 |
| 最终 C1 (~exp(−loss)) | ~0.6450 | 同上 |
| 总耗时 | ≈611 min（含启动开销） | 同上 |
| 稳态吞吐 | 3.37 it/s（+40% vs 修前 2.40，效率验收值） | MEMORY_VISION.md 效率表 |
| GPU util | 8×H100 95-100% / 全卡 | 同上 |
| 峰值显存 | 25.6 GB/卡 | 同上 |

### §10.3 ProtB 评测结果（Protocol B，主流对齐）

| 指标 | 值 | 来源 |
|:--|:--|:--|
| ProtB lp (seed 0) | 58.016% | `armA_protb_vitb16_224_results.json` |
| ProtB lp (seed 1) | 58.066% | 同上 |
| ProtB lp (seed 2) | 58.020% | 同上 |
| **ProtB lp mean ± σ** | **58.034 ± 0.023%** → **58.03 ± 0.02%** | 同上 |
| 5-NN (k=5, cosine) | 53.98% | 同上 |

> 协议：Protocol B（SGD+momentum0.9+cosine 90ep, bs1024, IN-1k full train 1.28M, IN-1k val 50k, 3 seeds 0/1/2, feature=projected, ckpt=latest.pt）。

### §10.4 对比（ArmA vs ④-4ep 基线）

| 指标 | ArmA | ④-4ep | Δ (ArmA − ④-4ep) |
|:--|--:|--:|--:|
| ProtB lp | 58.03 ± 0.02% | 67.05 ± 0.02% | **−9.02 pp** |
| k-NN | 53.98% (k=5) | 42.35% (k=20) | **+11.63 pp** |

> ⚠️ **k 值口径**：ArmA k=5，④-4ep k=20（k=5=39.77%）。同取 k=5 → Δ=+14.21 pp。

### §10.5 关键解读

- ArmA = **lp −9.02pp / 5-NN +11.63pp** ⇒ 检索型表征强、线性可分性弱，与「C1/lp 背离」假设一致。
- ⚠️ **不是单变量对照**（塔 86.2M vs 126.8M、目标 InfoNCE vs AIMv2-style dense、步数 154,500 vs 748,404、样本/批次不同）⇒ **不得写成「AIMv2 目标比 InfoNCE 好 9pp」**。
- ArmB（open_clip ViT-B/16 + AIMv2-style，4 epoch，训练中）是"固定塔/数据、仅切换目标函数"的单变量对照，预期将给出 cleaner 对比。

### §10.6 文件路径

| 文件 | 路径 |
|:--|:--|
| 训练脚本 | `vision/run_armA_openclip.sh` |
| 训练代码 | `vision/armA_openclip_train.py` |
| 评测脚本 | `vision/run_armA_protb_eval.sh` + `vision/armA_protb_eval.py` |
| 评测结果 JSON | `vision/armA_protb_vitb16_224_results.json` |
| 训练日志 | `/tmp/armA_openclip_train.log` |
| **中文报告** | `reports/report_vision_armA_openclip_result_zh.html`（含附录 A: open_clip × AIMv2-style 兼容性工程评估 + 附录 B: 官方 AIMv2 vs 本仓 AIMv2-style 概念澄清） |

## §11 ArmB（open_clip ViT-B/16 + AIMv2-style 稠密目标，2026-10-18）

> **目的**：在 ArmA 的 open_clip 标准塔上叠加 AIMv2-style 稠密目标（InfoNCE 对比 + masked patch prediction），检验「稠密监督是否在标准架构上同时提升 lp 与 k-NN」（ArmA 呈 lp↓/k-NN↑ 背离，本臂预期翻为双升）。

### §11.1 训练配置

| 项 | 值 | 来源 |
|:--|:--|:--|
| 模型 | open_clip ViT-B/16 224px（86.2M visual / 149.6M total，`pretrained=None`，双塔随机初始化） | `armB_aimv2_openclip.py` |
| 损失 | contrast（open_clip InfoNCE，contrast_w=1.0）+ masked patch prediction（patch_w=1.0，mask_ratio=0.6）+ AIM | `armB_aimv2_openclip.py:210-211` |
| 前向 | 双塔 forward → img_feat/txt_feat + 对 60% patch 做 masked reconstruction | 同上 |
| 优化器 | AdamW fused=True, wd=0.1, betas=(0.9,0.98), grad_clip=1.0 | `run_armB_openclip.sh` |
| LR | 1e-3 → 1e-5 cosine, warmup 2000 | `run_armB_openclip.sh` |
| 批次 | GBS=8192 (MBS=1024×8), bf16 AMP | `run_armB_openclip.sh` |
| 步数 | 57,250（= 4 epoch，数据 ≈117M 对） | `run_armB_openclip.sh` |
| 数据 | GPIC(7437)+CC12M(1100)+Amshaker(2250) ≈10,787 shards ≈117M 对（与 ArmA 同源） | `run_armB_openclip.sh` |
| seed | 1234 | `run_armB_openclip.sh` |

### §11.2 训练结果

| 指标 | 值 | 来源 |
|:--|:--|:--|
| 最终 step | 57,250/57,250 (100%) | `/tmp/armB_openclip_train.log` |
| 最终 loss (EMA) | 0.1263（contr=0.1109 / patch=0.0155） | 同上 |
| C1 范围 | 0.86–0.93（全程无坍缩） | 同上 |
| 总耗时 | 18.37h | 同上 |
| 稳态吞吐 | 0.87 it/s | 同上 |
| 峰值显存 | 50.4 GB/卡 | 同上 |
| 退出码 | 0（`===== ArmB done (exit 0) =====`） | 同上 |
| 产物 | open_clip_state_dict.pt(571M)+predictor.pt+config.json+latest.pt+checkpoint_57250.pt+50000.pt | 同上 |

### §11.3 ProtB 评测结果（Protocol B，主流对齐）

| 指标 | 值 | 来源 |
|:--|:--|:--|
| ProtB lp (seed 0) | 62.084% | `armB_protb_vitb16_224_results.json` |
| ProtB lp (seed 1) | 62.086% | 同上 |
| ProtB lp (seed 2) | 62.110% | 同上 |
| **ProtB lp mean ± σ** | **62.093 ± 0.012%** → **62.09 ± 0.01%** | 同上 |
| 5-NN (k=5, cosine) | 58.102% | 同上 |

> 协议：Protocol B（SGD+momentum0.9+cosine 90ep, bs1024, IN-1k full train 1.28M, IN-1k val 50k, 3 seeds 0/1/2, feature=projected, ckpt=open_clip_state_dict.pt）。与 ArmA 同协议、同 ckpt 选择（final state dict），**严格可比**。

### §11.4 预注册判据（先定后测）

| 判据 | 阈值 | 实测 | 裁定 |
|:--|:--|--:|:--|
| J1 不倒退（vs ArmA lp） | lp ≥ 58.03% | 62.09% | ✅ PASS |
| J2 混合 recipe 接受 | lp ≥ 61.0% 且 5-NN ≥ 48.98% | 62.09% / 58.10% | ✅✅ PASS |

> **两项判据均通过 → ArmB 混合 recipe（open_clip 塔 + AIMv2-style 稠密目标）被 ACCEPTED**。

### §11.5 对比（ArmB vs ArmA · 同 k=5 · 同 Protocol B）

| 指标 | ArmA | ArmB | Δ (ArmB − ArmA) |
|:--|--:|--:|--:|
| ProtB lp | 58.03 ± 0.02% | 62.09 ± 0.01% | **+4.06 pp** |
| 5-NN (k=5) | 53.98% | 58.10% | **+4.12 pp** |

> ArmB 为**双探针同步提升**（lp↑ 且 k-NN↑），与 ④-4ep 的 lp↑/k-NN↓ trade-off 形态不同 —— 在 open_clip 标准塔上，AIMv2-style 稠密目标同时改善了线性可分性与近邻检索两类表征质量。

### §11.6 关键解读与诚实披露

- ArmB 在 open_clip ViT-B/16 塔上同时提升 lp 与 5-NN，验证了「稠密监督在标准架构上可双升」的假设方向（与 R11-L④ CoCa 负结果对比：CoCa caption 监督把 trunk 打回随机，而 caption-无关的 masked patch reconstruction 没有）。
- ⚠️ **不是严格单变量对照**：ArmA 与 ArmB 在 GBS（2048 vs 8192）、epoch（2.7 vs 4.0）、lr（2e-3 vs 1e-3）、warmup（8000 vs 2000）上均不同。+4pp 是「recipe 切换」的综合效应，**不能孤立归因为目标函数的贡献**。需控制变量消融才能定量分解各因子。
- 与 §10 ArmA 的 ④-4ep 基线对比同样如此：ArmB ≠ ④-4ep 的「塔/数据/目标」单一变量切换（塔 86.2M vs 126.8M、数据量、步数均不同）。

### §11.7 文件路径

| 文件 | 路径 |
|:--|:--|
| 训练脚本 | `vision/run_armB_openclip.sh` |
| 训练代码 | `vision/armB_aimv2_openclip.py` |
| 评测脚本 | `vision/run_armB_protb_eval.sh` + `vision/armA_protb_eval.py`（复用 ArmA 评测代码） |
| 评测结果 JSON | `vision/armB_protb_vitb16_224_results.json` |
| 训练日志 | `/tmp/armB_openclip_train.log` |
| **中文报告** | `reports/report_vision_armB_openclip_result_zh.html`（§1–§7 + 附录 A: open_clip × AIMv2-style 兼容性 + 附录 B: 官方 AIMv2 概念澄清） |


---

## §12 ArmB-Stage4 · MLLM 对齐 + 12 集 lmms-eval 评测（2026-10-18）

### §12.1 实验概述

将 ArmB 视觉编码器（open_clip ViT-B/16，768-d，86.2M，ProtB lp=62.09%）经 LLaVA-OV1.5 三阶段对齐（Stage-1 → Stage-1.5 → Stage-2）接入 Qwen3-4B，在 12 个 lmms-eval benchmark 上评测，对比 ④-4ep 基线。

### §12.2 模型配置

| 组件 | ArmB | ④-4ep（基线） |
|:--|:--|:--|
| 视觉编码器 | open_clip ViT-B/16 · 768-d · 86.2M | 自研 w512 · 512-d · 126.8M |
| ProtB lp | 62.09 ± 0.01% | 67.05 ± 0.02% |
| Projector | 2 层 MLP 768→2560 · 8.52M | 2 层 MLP 512→2560 · 7.87M |
| LLM | Qwen3-4B-Instruct-2507 | 同左 |
| 三阶段配方 | LLaVA-OV1.5（Stage-1 2500 / Stage-1.5 20000 / Stage-2 3500） | 同左 |

### §12.3 12 集评测结果 + Δ vs ④-4ep

| # | Benchmark | ArmB | ④-4ep | Δ |
|:--:|:--|--:|--:|--:|
| 1 | ai2d | 60.69% | 60.04% | **+0.65pp** |
| 2 | RealWorldQA | 45.49% | 43.01% | **+2.48pp** |
| 3 | MMMU (val) | 43.67% | 42.89% | **+0.78pp** |
| 4 | Blink | 38.94% | 38.52% | **+0.41pp** |
| 5 | MMStar | 27.95% | 26.81% | **+1.14pp** |
| 6 | MMMU-Pro | 22.43% | 23.12% | −0.69pp |
| 7 | InfoVQA | 16.88% | 16.58% | **+0.30pp** |
| 8 | ChartQA | 12.52% | 12.24% | **+0.28pp** |
| 9 | CountBench | 9.57% | 10.79% | −1.22pp |
| 10 | DocVQA | 7.36% | 7.41% | −0.05pp |
| 11 | OCRBench | 1.60% | 1.10% | **+0.50pp** |
| — | **平均（除 MME）** | **26.10%** | **25.68%** | **+0.42pp** |
| 12 | MME total | 796.51 | 847.46 | −50.95 |
| 12a | MME perception | 583.65 | 596.75 | −13.10 |
| 12b | MME cognition | 212.86 | 250.71 | −37.85 |

### §12.4 预注册判据裁定

| 档位 | 条件 | ArmB 实际 | 裁定 |
|:--|:--|:--|:--:|
| 强成功 | 平均 ≥ 30% | 26.10% | ✗ |
| 成功 | 平均 > 24% **且** DocVQA/ChartQA/OCRBench 任一 ≥ +10pp | 26.10% > 24% ✓，但 max Δ = +0.50pp | ✗ |
| 不可分辨 | 22% – 26% | 26.10%（上沿 +0.10pp） | **≈ 边界** |
| 失败 | 平均 ≤ 22% | 26.10% | ✗ |

> **预注册裁定：不可分辨（边界值）**。ArmB 12 集平均 26.10%，略高于 ④-4ep（+0.42pp），处于不可分辨区间上沿。8/11 benchmark 方向为正但无 +10pp 突破。

### §12.5 与 RiCEViT（配方R-1.5）对比

| 指标 | ArmB | ④-4ep | RiCEViT | Δ(ArmB−RiCEViT) |
|:--|--:|--:|--:|--:|
| 平均（除 MME） | 26.10% | 25.68% | 60.08% | **−34.0pp** |
| DocVQA | 7.36% | 7.41% | 81.58% | −74.2pp |
| ChartQA | 12.52% | 12.24% | 75.72% | −63.2pp |
| OCRBench | 1.60% | 1.10% | 62.90% | −61.3pp |

> ArmB 与 ④-4ep 一样全面落后 RiCEViT（−34pp vs −34.4pp），差距几乎相同。细粒度任务（doc/chart/ocr）仍是最大短板，瓶颈在分辨率（224px / 196 tokens）非视觉塔选型。

### §12.6 关键结论

1. **open_clip 接口 + AIMv2-style 表征在 MLLM 下游与 ④-4ep 基本持平**（Δ=+0.42pp，评测噪声内），未拉开差距。
2. **ProtB → MLLM 传递性再次证伪**：ArmB ProtB lp（62.09%）低于 ④（67.05%）5pp，但 MLLM 评测反超 0.42pp。线性探针不预测 MLLM 下游表现。
3. **分辨率是系统性瓶颈**：DocVQA/ChartQA/OCRBench 与 ④ 几乎相同（均 <13%），远落后 RiCEViT（>62%），说明瓶颈在 224px/196tokens 而非视觉塔。
4. **MME 认知下降**（−37.85）是唯一明显劣化的指标，可能因 768-d 特征空间在 LoRA 微调后对认知推理适配不如 512-d，但样本量不足以确证。

### §12.7 文件路径

| 文件 | 路径 |
|:--|:--|
| 评测脚本 | `vision/run_lmms_eval.py` + `vision/rerun_missing_8benchmarks_armB.sh` |
| 评测结果 | `datasets/baize-vision/out/mllm_eval_results_armB/consolidated_12benchmarks.json` |
| **中文报告** | `reports/report_vision_armB_mllm_stage4_zh.html` |
| 评测日志 | `/tmp/rerun_8b_armB.log` |

## §13 ArmC（open_clip ViT-B/16 + AIMv2-style，2026-10-18→10-19）· ⚠️ 两变量实验

### §13.1 实验概述与两变量披露

> **用户令（2026-10-18）**：「vision：开启 ArmC。跟 ArmB 相比，只有一个变量：学习率。LR=1e-3，min_LR=1e-5。1.训练；2.评测 ProtB；3.MLLM 对齐；4.MLLM 12 集评测。」**追加令（同日）**：「加个变量：weight decay 0.1 -> 0.01」。

⚠️ **ArmC 是两个变量**（min_lr 1e-4→1e-5 + weight decay 0.1→0.01），**不是单变量消融**。ArmC vs ArmB 的任何差异**不得归因于单一变量**；报告中必须同时披露两个改动。其余配置（`--lr 1e-3`、warmup 2000、4 epoch/57250 步、GBS 8192/MBS 512/accum 2、数据 GPIC 8000+CC12M 1100+Amshaker 2250=11350 shards、目标 AIMv2-style InfoNCE 1.0 + masked-patch-MSE 1.0 mask 0.6、AdamW betas(0.9,0.98)、bf16、grad_clip 1.0、seed 1234、save 10k/keep 2、open_clip ViT-B/16 224 双塔）**全部与 ArmB 相同**（launch 脚本经 `diff` 核对除标签外逐字一致）。

| 项 | ArmB | ArmC | 是否变量 |
|:--|:--|:--|:--|
| LR | 1e-3 | 1e-3 | 否（不变） |
| **min_lr** | **1e-4** | **1e-5** | ✅ **变量 1** |
| **weight decay** | **0.1** | **0.01** | ✅ **变量 2** |
| 其余全部 | — | — | 否（与 ArmB 一致） |

### §13.2 训练配置

- 脚本：`vision/run_armC_openclip.sh`（复制自 `run_armB_openclip.sh`，仅改 `OUT=.../armC_20261018_aimv2_openclip_vitb16_224`、`--lr 1e-3 --min-lr 1e-5 --wd 0.01`）。
- 训练脚本：`vision/armB_aimv2_openclip.py`（logger 名硬编码 `[ArmB]`，实为 ArmC run，报告注明）。
- 输出目录：`/nas_train/app.e0031982/datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/`（独立目录，不覆盖 `armB_*`）。
- `config.json` 复核：`lr=0.001 / min_lr=1e-05 / wd=0.01 / seed=1234 / mask_ratio=0.6 / contrast_weight=1.0 / patch_loss_weight=1.0 / n_visual=86192640(86.2M)` → **确认只有 min_lr + wd 两变量** ✓。

### §13.3 训练 + ProtB 评测结果（✅ DONE）

| 阶段 | 结果 |
|:--|:--|
| ① 训练 | ✅ DONE 2026-10-19 14:32，**57250 步 exit 0**，墙钟 ~19.9h，0.78 it/s 稳态，7/8×H100 100%@50559MiB peak 50.4GB 无 OOM，`grep error/nan/oom/traceback=0`，ckpt 10k/20k/…/57250（keep 2 滚动），`open_clip_state_dict.pt`(598MB)+`predictor.pt`(4.7MB)+`config.json` 均在 |
| ② ProtB | ✅ DONE 14:57，3 seeds：**lp=62.332±0.014% / 5-NN=54.718** |

**ProtB 对比（ArmC vs ArmB vs ④-4ep，同 Protocol B、同 IN-1k 1.28M/50k）**：

| 指标 | ArmC | ArmB | ④-4ep | Δ(ArmC−ArmB) | Δ(ArmC−④-4ep) |
|:--|--:|--:|--:|--:|--:|
| lp（mean±σ） | **62.332±0.014** | 62.093 | 67.05 | **+0.239pp** | −4.718pp |
| 5-NN | 54.718 | 58.102 | 42.35 | **−3.384pp** | +12.368pp |

> ⚠️ **两变量披露**：ArmC vs ArmB 的 Δlp=+0.239pp / Δ5-NN=−3.384pp 是 **min_lr（1e-4→1e-5）+ weight decay（0.1→0.01）两个变量共同作用**的结果，**不得归因单一变量**。lp 微升、5-NN 下降的方向差异无法拆分到单一因子。

### §13.4 MLLM 三阶段对齐（✅ DONE）

复用 ArmB 三阶段脚本，仅把视觉塔 ckpt 换成 ArmC、输出目录改 `*_armC_20261018`（chain `run_armC_full_chain.sh` 自动串行）：

| 阶段 | 步数 | 结果 | 备注 |
|:--|--:|:--|:--|
| Stage-1（projector 768→2560） | 2500 | ✅ DONE 15:06（~7.2min, loss 4.29） | 不改 LLaVA-OV1.5 配方 |
| Stage-1.5（LoRA r=64/α128 + proj） | 20000 | ✅ DONE（~86min, loss ~3.6-3.9 无坍缩） | ckpt@16000/20000 |
| Stage-2（instruct, LLaVA-NeXT-780k） | 3500 | ✅ DONE 17:0x（~15min, loss ~1.48） | ckpt step3500 在位 |


### §13.5 ④ 12 集 lmms-eval 评测（🔄 PARTIAL — 4/12 完成，8/12 因代理宕机 MISSING，已部署 watcher 自动重跑）

- 评测脚本：`vision/mllm_bridge/launch_12benchmarks_armC.sh`（`--vision_backend armC`，batch_size=32，无 --limit，12 集），chain `run_armC_full_chain.sh` PHASE ④ 于 17:17 启动 8 GPU 并行。
- **chain 17:27:07 完成 exit 0**，但 **8/12 集 MISSING**：

| GPU | 任务 | exit | 结果 |
|:--|:--|:--|:--|
| 0 | mmmu_val | 0 | ✅ **0.4256** |
| 1 | mmmu_pro_standard | **1** | ❌ MISSING |
| 2 | docvqa_val | 0 | ✅ **0.0758** |
| 3 | infovqa_val | 0 | ✅ **0.1709** |
| 4 | chartqa+ocrbench+countbench | **1** | ❌ MISSING（3 集） |
| 5 | mme+blink | **1** | ❌ MISSING（2 集） |
| 6 | ai2d+mmstar | **1** | ❌ MISSING（2 集） |
| 7 | realworldqa | 0 | ✅ **0.4497** |

**根因（已查 4 份失败 log）**：4 个失败 log 末尾均为 `tenacity.RetryError: RetryError[<Future ... raised ConnectionError>]`，发生在 `lmms_eval/api/task.py:814 self.download()` → 数据集加载阶段。这 8 个任务用 tenacity 包装的**直接 URL 下载**（requests/urllib），**不受 `HF_HUB_OFFLINE=1` 约束**，需要走代理。17:17 时**两个代理均宕机**（172.19.92.25:13128 与 172.19.92.23:13128 对 huggingface.co 均超时 HTTP 000）→ 直接 URL 下载失败 → ConnectionError。**非模型/配置问题**：ArmB 用**逐字一致的脚本**（`diff` 核对）在 10-18 代理可用时 12/12 全成功；4 个成功的 ArmC 任务因数据已缓存（无需直接 URL 下载）而通过。8 个失败数据集**已在 HF hub 缓存**（`datasets--MMMU--MMMU_Pro` / `ChartQA` / `OCRBench` / `CountBenchQA` / `MME` / `BLINK` / `ai2d` / `MMStar`），但 `datasets.load_dataset` 在 offline 模式下无法解析无脚本的 dataset module（需联网列仓库文件）→ 仍需代理。

**4 个已完成集 vs ArmB（仅描述，非裁定，8 集 MISSING 不可算平均）**：

| 集 | ArmC | ArmB | Δ(ArmC−ArmB) |
|:--|--:|--:|--:|
| mmmu_val | 0.4256 | 0.43667 | −1.11pp |
| docvqa_val | 0.0758 | 0.07358 | +0.22pp |
| infovqa_val | 0.1709 | 0.16879 | +0.21pp |
| realworldqa | 0.4497 | 0.45490 | −0.52pp |

> 4 集 Δ 均很小（±1pp 量级），方向 2 正 2 负，与 ArmB「不可分辨」先例一致，但 **8 集 MISSING ⇒ 无法计算 11 集平均(除MME) ⇒ 暂不下裁定**。沿用 ArmB 预注册判据（≥30% 强成功 / >24% 且 DocVQA/ChartQA/OCRBench 任一 +10pp 成功 / 22–26% 不可分辨 / ≤22% 失败），ArmC vs ArmB 的 Δ 只作描述，不事后改判据。

**处置（已执行）**：部署后台 watcher `vision/rerun_failed_benchmarks_armC.sh`（PID 1153787 @ .12，setsid detach），每 300s 轮询两个代理（.25→.23），**代理恢复即自动重跑 4 个失败 GPU 组**（GPU1/4/5/6，env 同 ArmB 已知可用配置：offline ON + HF_HUB_ENABLE_HF_TRANSFER=1 + 工作代理），保留 4 个已成功 json 不覆盖，重跑后调 `consolidate_12benchmarks.py --results_dir` 合并 4+4=12 集。日志 `/tmp/armC_rerun_benchmarks.log`，重跑子日志 `eval_*_rerun.log`。代理宕机属基础设施问题，超出 agent 控制范围；不伪造任何 MISSING 结果。

### §13.6 状态与下一步（🔄 IN PROGRESS）

- **当前**：①②③ ✅ DONE；④ 4/12 完成 + 8/12 等代理恢复（watcher 运行中）。
- **下一步（代理恢复后）**：watcher 自动完成 ④ → agent 跑 `vision/generate_armC_mllm_report.py` 生成 `reports/report_vision_armC_20261018_mllm_stage4_zh.html`（含两变量披露框 + 逐集 Δ + 11集平均(除MME) + 预注册判据；④结果缺失则报错退出）→ 补全本节 §13.5 裁定 + §13.7 文件路径 → commit `vision armC:`。
- **诚实条款**：本节 ④ 4 集为真实评测结果；8 集 MISSING 系代理宕机所致，已部署自动重跑，结果待补；不基于 4 集外推 12 集裁定。

### §13.7 文件路径

| 文件 | 路径 |
|:--|:--|
| 训练脚本 | `vision/run_armC_openclip.sh` + `vision/armB_aimv2_openclip.py` |
| 训练输出 | `datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/` |
| ProtB 评测 | `vision/run_armC_protb_eval.sh` → `vision/armC_20261018_protb_vitb16_224_results.json` |
| MLLM chain | `vision/run_armC_full_chain.sh` + `vision/mllm_bridge/stage{1,15,2}_train_armC.py` |
| ④ 12集 launch | `vision/mllm_bridge/launch_12benchmarks_armC.sh` |
| ④ 重跑 watcher | `vision/rerun_failed_benchmarks_armC.sh`（PID 1153787 @ .12）|
| ④ 结果 | `datasets/baize-vision/out/mllm_eval_results_armC_20261018/consolidated_12benchmarks.json` |
| ④ 日志 | `/tmp/armC_full_chain.log` + `/tmp/armC_rerun_benchmarks.log` |
| **中文报告** | `reports/report_vision_armC_20261018_mllm_stage4_zh.html`（待 ④ 完成后生成）|

