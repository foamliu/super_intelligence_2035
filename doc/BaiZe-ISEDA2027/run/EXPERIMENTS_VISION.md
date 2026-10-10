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

#### 8.2.4 E2fair — 🔄 Training In Progress

E2fair training started 09:20:12 Oct 10 (auto-chained after E1fair eval completed). Currently at step ~9,850/187,101 (~5.3%), ~4,900 img/s, loss_ema ~0.6, 33 PROBE events all C4=OK, 0 fusing, no collapse. GPU: 8/8 active, 67–92% util, ~24.9 GB/card. lr=4.98e-04 (warmup phase). ETA: train done ~14:30 Oct 10 (~5.2h total) → eval ~3.5h → all done ~18:00 Oct 10.

**E2fair [start] line** (from `/tmp/scaling_e2fair.log`):
```
[start] tower=openvision2 lr=0.0005 warmup=2000 bs=64 world=8 steps=187101 res=224 patch=16 seed=1234 shards=1349/rank objective=AIMv2-style(MIM+InfoNCE) scheduler=cosine min_lr=5e-05 text=frozen-CLIP-768(r=8,a=16.0,lr=0.0001) negatives=512 data_source=mixed caption_type=all total_shards=10787
[lr-selfcheck] lr@step0=0.00000000  lr@warmup(2000)=0.00050000  lr@50%(93550)=0.00027882  lr@last(187100)=0.00005000
[lr-selfcheck] OK: lr monotonically decreasing after warmup
```

E2fair's `[start]` line and lr self-check are byte-identical to E1fair's — confirming only `--width 768` differs. `total_shards=10787` matches exactly.

#### 8.2.5 Δlp Comparison — ⏳ Pending

Δlp = lp(E2fair_ProtB) − lp(E1fair_ProtB) = ⏳ − 62.34%. E2fair Protocol B result needed. ETA ~18:00 Oct 10.
