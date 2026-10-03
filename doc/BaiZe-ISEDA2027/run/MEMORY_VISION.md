# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R10_done · R14 ✅ · E1 ✅ · R11-L 预注册 ✅ · arm② SigLIP ✅（未翻盘）· arm③ LocalLoss ✅（未翻盘）· arm④ CoCa ✅（lp 0.47%≈随机、Δ−5.6 点，首个稠密臂=负结果·未翻盘）· 🚀 R11-L2 文本塔解冻 LoRA 训练中**；臂⑤ GenLIP 🚫 跳过建议 / 臂⑥ AIMv2 ⏸ 暂缓 / R13 ⏸ 只做 OV2 单臂 / R11-E ⏸ 等数据；**R11-L2 已批准并在 `.12` 跑 30k 步（预注册见 ROUND11 §11）** |
| WAITING | 1（**语义=训练 running（异步）**：R11-L2 LoRA 臂 30k 步在 `.12` 跑（`whag0pgpuap12`），`bash r11_run_lora.sh 30000`，日志 `/tmp/r11_lora.log`，ETA ~2h → 置 1 长睡省 token、训练 `ALL DONE` 后回收 IN-1k lp 再置 0） |
| ERROR_COUNT | 1（R9 阶段一 w512 首跑 @~8900 步 crash：CC12M/Amshaker wds 含损坏 jpg → 已由 data.py `ignore_and_continue` 修复） |
| BUDGET_USED | R2–R9 累计 + R10（R10-① IN-1k ~1 GPU·h；R10-③ w384+w640 各 30k 步 ≈2×1.98h×8 卡）+ R11-L arm② SigLIP（1.96h×8 卡）+ arm③ LocalLoss（1.97h×8 卡）+ arm④ CoCa（1.92h×8 卡）+ R11-L2 LoRA（训练中，30k 步 ≈1.9–2.1h×8 卡） |
| 更新 | 2026-10-03 23:56（**R11-L2 文本塔解冻 LoRA 臂 已启动**：smoke 通过 → `r11_run_lora.sh 30000` 在 `.12` 跑；控变量同基线只变「文本塔解冻」；可训 +0.30M 文本 LoRA（q+v r=8 α=16 lr=1e-4）、重跑 C1–C4；预注册见 ROUND11 §11） |
| WINNER | OpenVision2（R8 六架构四指标第一；R9/R10 证「塔越小越高」，w512=126.8M 是既有对比基线，不改架构排名） |

## R9 完成（converged）结论速查（2026-10-03，权威详见 EXPERIMENTS_VISION_ROUND9.md）

- **阶段一缩塔先导**（OpenVision2 × width{512,768,1024} × 30k，同 recipe/数据/batch512）：IN-1k lp = **6.10% / 3.63% / 1.03%**（zs 2.74/1.91/1.02）→ **塔越小每样本效率越高** → 选 **w512（126.8M）**。
- **阶段二**（w512 × 108k 步 = 55.3M 样本）：无坍缩（C1≈0.36 / C2_gap≈+0.10 / loss_ema 5.99→3.71，steady 2904 img/s）；IN-1k lp 峰值 **7.70%**@51.2M，zs top-1 3.59% / top-5 11.47%。
- **scaling 拟合**（11 点 R²≈0.94）：幂律 acc=0.251−0.864·N^−0.090（渐近 **25.1%**）；对数线性 acc=−0.229+0.0398·log10(N)。外推 20% 需 619 亿（对数）/ 41 万亿（幂律）样本 → **本地 ≈118M 唯一对上限（C1 修正）够不到 20%+**。
- **结论**：瓶颈在数据量与目标函数（AIMv2 ≈120 亿对，我们 649× 少），非架构。详见 EXPERIMENTS_VISION_ROUND9.md §4–§5。

## R10（2026-10-03）：补全 M 轴的 scaling law

> 运维指出 R9 只扫了数据侧 N（固定 w512），M 轴没做；R10 复用阶段一已落盘三档塔宽 ckpt 补 M 轴，拟合 (N,M) 二维 scaling law。

- ✅ **R10-① 回收 12 点 IN-1k 完成**：3 塔 × step{10k,20k,30k}，`r10_eval_stage1.sh` → `r8_eval_in1k.py --ckpts`（exit 0）。lp(w512/w768/w1024 @N=5.12/10.24/15.36M)：3.43/5.45/**6.08**%、1.14/2.03/**3.63**%、0.67/0.99/**0.93**%（证据 `/tmp/r10_stage1_in1k.log`）。
- ✅ **R10-② 2D 拟合完成（3 点 M 轴）**：`r10_scaling2d.py`，19 点 → 带交互 R²=0.980：`acc=-1.737+0.333·log10(N)+0.185·log10(M)-0.036·log10(N)·log10(M)`；M 边际效应**全区间为负** ≈ **−2.2 lp pp/参数翻倍**（无交互 c=−0.070，R²=0.975）。→ 数据受限区间**加宽塔是负收益**。
- ✅ **R10-③ 完成（`denseM ALL DONE @13:00:30`，exit 0）**：`r10_run_denseM.sh` 训 w384(71.49M)+w640(197.80M) 各 30k 步（同数据/recipe）+ 自动回收 8 ckpt IN-1k。结果 lp（@N=5.12/10.24/15.36M）：**w384 = 5.77/6.92/7.99%**、**w640 = 1.66/1.99/3.62%**；w384 吞吐 6583 img/s（w640 2418）、final_loss 3.7769（w640 4.3485）。
- ✅ **5 点 M 重拟合完成**：带交互 R²=0.960 `acc=-1.452+0.298·log10(N)+0.150·log10(M)-0.0318·log10(N)·log10(M)`；M 边际 ≈ **−2.2~−2.4 lp pp/参数翻倍**；最优 M 仍在观测下界（71.5M）之下 → **无饱和点、更小塔持续更优**。**w384@15.36M=7.99% 为全部宽度最高**。
- **铁律**：不重跑阶段一训练；每条结论贴证据（命令 + 原始输出 + 路径）；不许猜。

### 🕐 R10-③ 等待已结束（收尾 4 步已执行完毕）
- **结果**：5-M 拟合 R²=0.960（§2.3）+ 最优 N/M（§2.4）+ denseM 8 点表（§3）+ 结论（§4）均已回填 `EXPERIMENTS_VISION_ROUND10.md`；`EXPERIMENTS_VISION.md` 顶部 R10 节 + 本状态头已更新，随后 push。

## R14 官方仓库调研（✅ 全部完成，2026-10-03）

- CPU-only 源码普查，与 R10-③ denseM 训练并行。产物：`VISION_OFFICIAL_REPOS_SURVEY.md`（①目标②数据③config④结构差异⑤可复用资产⑥LICENSE⑦三清单）。
- ✅ 两个 ⭐⭐⭐ 仓库源码普查完成（上一 cycle）：**OpenVision**（JAX/TPU，官方 ViT-L/16 = w1024/d24/h16；文本 = BERT-128 + LLaMA3 dense caption + caption decoder + keep_ratio=0.35）；**ml-aim/AIMv2**（仅模型接口，无训练/损失/数据；LICENSE = Apple Sample Code，🔴 不可 COPY）。
- ✅ 第二阶段（本轮）全部核毕：
  - **OpenVision2 权重 = ✅ 已放出且真带 caption decoder**：HF `UCSC-VLAA/openvision2-vit-{so400m,large,huge,giant}-patch14-{224,336,384,448}-vision-only`；含 `caption_decoder.safetensors` + `text_decoder_config.json`（concat/prefix-LM，非 CoCa cross-attn）。🔑 官方 = **patch14/d24**，我们 = **patch16/d30**（models.py:170）→ R13 需另建官方结构塔才能 load。
  - **FastVLM** = ✅ `apple/ml-fastvlm`（FastViTHD 1024² conv-hybrid RepMixer）；LICENSE = Apple Sample Code（research-only，不可抄）。
  - **MambaEye** = ✅ `usingcolor/MambaEye`（MIT）：纯 Mamba2、**小模型监督分类**（非对比）；**MoE-ViE** = ✅ `facebookresearch/moe_vie`（CC BY-NC 4.0）：CLIP 风格 MoE-ViT，官方权重 HF；**iGVLM(AdaLN)/TuringViT** = 🚫 **未找到官方实现**（iGVLM 同名 IG-VLM 是视频QA；TuringViT 仅项目主页）。
- 关键产出（对 R13/R12）：官方 MoE-ViE/FastVLM/MambaEye/AIMv2 权重均可作「官方 vs 自研」对照标尺；OpenVision2 官方是 patch14/d24，需建官方结构塔。

## E1 GPIC 规模实测（✅ 完成，2026-10-03）

- 抽 **8 个 tar 均匀抽样**（index 0..1212）实测：**12,537 图文对/tar**（稳定 ±2%）→ **GPIC 全量 ≈ 100.3M**（证官方 100M 卡；旧「5 tar=86M」少计 png 作废）；**已下 1213/8000 tar ≈ 15.2M**。
- `caption_type` mix：short **45.0%** / medium 45.1% / long 9.0% / tag 1.0% → **可训练 short 子类：全量 ≈45M / 已下 ≈6.8M**。
- 🔑 **C1 口径定案**：R9 用过 18.5M / 盘上现有 ≈32M / 本地全量 ≈118M（动态、仍在下载）——与 `r9_scaling.py --local-cap-m default=118.0` 一致；R11-E「同 N」可比区间被压到 ≈6.8M（short 已下 < 18.5M），须如实说明。已回填 `VISION_ARCH_FRONTIER_2026.md §5`。

## R11-L 目标函数轴（2026-10-03）：arm② SigLIP ✅ → arm③ LocalLoss ✅ → 臂④ CoCa 待实现

> 只变目标函数，其余控变量（塔 w512 · 冻结 CLIP-768 · CC12M+Amshaker · lr3e-3 · bs512 · N=15.36M/30k 步 · IN-1k frozen-trunk lp）。预注册判据：同 N 下 lp 比基线 +1.5 点 → 局部推翻「25.1%=对比渐近」。

- ✅ **arm② SigLIP 完成（15:26，`ALL DONE`）**：`r9_train.py --loss siglip`（`SigLipLoss` bidir + 可训 `logit_bias` init−10，`r9_train.py:162-165`）。30k 步无坍缩（C1 0.333 / C2_gap +0.103 / C4=OK / final_loss 5.4643 / steady 2448 img/s）。IN-1k lp = **2.19 / 3.13 / 4.36%** @5.12/10.24/15.36M，全 < 基线（3.43/5.45/6.08%）→ **未超 +1.5 阈值、未翻盘**。证据 `/tmp/r11_siglip.log`。
- 🚀 **arm③ LocalLoss 已启动（15:29，.12 全 8 卡）**：`r9_train.py --loss localloss`（`ClipLoss(local_loss=True, gather_with_grad=False)`，`r9_train.py:166-168`）→ `R11L_localloss_w512` 30k 步。⚠️ **更正**：读 open_clip 源码（`loss.py:56-63,116-121`）确认 `local_loss=True` **仍是 512 负样本 all-gather**，只算本地 64 行 logits（省算/内存 + 本地图像不再从 text→image 拿梯度）→ 是「计算/梯度路径」变体、**非「负样本池 512→64」**（此前描述有误，已改）。arm③ 因此可证「损失对 local-vs-global 行是否不变」，但**不再测试负样本池大小**——真正池大小消融需另写不 gather 的自定义 loss（待后续决定）。
- ✅ **arm③ LocalLoss 完成（17:43，`ALL DONE`，收尾已做）**：`[done] total=7076.8s final_loss=4.4774 steady=2343 img/s fused=False`，无坍缩（C1 0.2378 / C2_gap +0.1101 / C4=OK）。IN-1k lp = **1.81 / 3.60 / 4.33%** @5.12/10.24/15.36M，全 < 基线（3.43/5.45/6.08%）→ Δ −1.62~−1.85 点、**未翻盘**。证据 `/tmp/r11_localloss.log`。⚠️ arm②③ 监督密度都 = 1 全局标量 → **「稠密监督翻盘」假说仍未检验**。
- ✅ **臂④ CoCa 已实现并启动（18:05，.12 全 8 卡，hostname=whag0pgpuap12 核验）**：CoCa = 对比 + caption 自回归 = **首个稠密监督臂**。`models.py` 增 `CoCaDecoder`（causal self-attn + cross-attn→patch，共享冻结 CLIP token_embed 49408）+ `OpenVision2.forward(return_patch=True)`；`r9_train.py` 增 `tokenize_cap`/`coca_caption_loss`/`--loss coca`/`--caption-loss-weight 2.0`/`--decoder-depth 4`。decoder 实测 **trainable=76.2M / total=114.1M**（w768·12H·4L + LM head）。smoke 30 步 exit 0（`[step 30] loss=18.61 contrast=6.12 caption=6.25 image/s=2337.9`）。`r11_run_coca.sh 30000` → `R11L_coca_w512`，30k 步（N=15.36M 主锚点），打印 `[start] steps=30000 objective=CoCa shards=419/rank`。日志 `/tmp/r11_coca.log`。ETA ~1.9~2.1h 训完 + 自动回收 4 ckpt IN-1k lp。
- 🔍 **巡检（16:44）**：arm③ LocalLoss @ step 17400/30000（58%），健康——C1 0.22 / C2_gap +0.11 / C4=OK、loss_ema 5.91→~4.64、steady ~2500 img/s；ETA ~17:30（剩 ~46 min）后自动回收 4 ckpt IN-1k lp。无异常，继续 WAITING。
- 🔍 **巡检（17:14）**：arm③ LocalLoss @ step 25850/30000（86%），健康——C1 0.1821 / C2_gap +0.1152 / C4=OK、loss_ema 5.91→~4.78、steady ~2780 img/s；ETA ~17:27 训完（剩 ~13 min）→ 脚本自动回收 4 ckpt IN-1k lp → 下次唤醒（≈17:44）做 arm③ 收尾。无异常，继续 WAITING。
- 📝 **文档修正（17:14，纯 CPU）**：`EXPERIMENTS_VISION_ROUND11.md` §5 状态行原「负样本池 512→64」为误述，已改为「⚠️ 仍 all-gather 512 → 池仍是 512、只算本地 64 行」（对齐 §0 更正）。另注：`r11_run_localloss.sh` 头注释（`negative pool = per-rank 64`）亦含同一旧表述——该 runner 为一次性脚本（正在运行、跑完不复用），故未改运行中脚本，仅在此记录，待跑完若需复用再改。
- 🔍 **巡检（18:39，arm④ CoCa）**：@step 9100/30000（30.3%）健康——C1 0.4362 / C2_gap +0.0600 / C4=OK，loss_ema 22.55→17.77（contrast ~5.6 / caption ~6.0），吞吐 ~2500–4900 img/s（随迭代波动，低值出现在 probe 前后）；单进程组核验（1 master + 8 rank + 48 dataloader worker，**无重复 run**）；8 卡全忙（util 67–88%，显存 22.7/81.6 GB）。ETA ~20:05–20:15 训完 → 脚本自动回收 4 ckpt IN-1k lp → 下次唤醒做 arm④ CoCa 收尾（§9 回填 + §3 公平表 + 判据裁定）。无异常，继续 WAITING。
- 🔍 **巡检（19:13，arm④ CoCa）**：@step 17950/30000（59.8%）健康——C1 0.3704 / C2_gap +0.0637 / C4=OK，loss_ema 22.55→16.93（contrast ~5.6–5.9 / caption ~5.4–6.4），吞吐 ~2270–5100 img/s（前段 ~2400，17450 步后数据加载提速至 ~4900）；进程组**再核验** 1 master(1359723) + 8 rank(1359914–1359921) + 48 dataloader worker（**无重复 run**）；8 卡全忙（util 31–82%，显存 22.7 GB）。ETA ~20:05–20:15 训完 → 脚本自动回收 4 ckpt IN-1k lp → 下次唤醒做 arm④ CoCa 收尾（§9 回填 + §3 公平表 + 判据裁定）。无异常，继续 WAITING。
- ✅ **arm④ CoCa 完成（20:13，`ALL DONE`，收尾 20:32 已做）**：`[done] total=6911.7s final_loss=17.4016 steady=3486.8 img/s fused=False`；探针名义通过但弱（C1 0.339 / C2_diag 0.089 / C2_off +0.021 / C2_gap +0.068，且 C2_gap 从 @300 的 +0.092 单调下滑；caption 项 ~68% 梯度）。IN-1k lp = **0.29 / 0.37 / 0.47%** ≈ 随机（<1/1000），zs 0.40/0.41/0.53% → Δ **−3.14/−5.08/−5.61** 点、**未翻盘且 trunk 被 caption 监督打回随机**。⚠️ 限于「自写 CoCa decoder + 冻结 CLIP-768 + 短 caption + weight2.0（未消融）」，**不得推广到官方 CoCa**。证据 `/tmp/r11_coca.log`。→ **首个稠密监督臂=负结果，「稠密监督翻盘」假说反向**；后续：臂⑤ GenLIP（纯 caption、坍缩先验更强）**建议跳过**，臂⑥ AIMv2 patch（唯一 caption-无关稠密、最贵、需自研）与 R11-L2（文本塔解冻）**待运维裁决**（详见 ROUND11 §9）。

- 📌 **decision gate（2026-10-03 21:31）**：R11-L 四臂（①基线/②SigLIP/③LocalLoss/④CoCa）全部兑现、无一翻盘；GPU 已空。**书面成本/收益判断已交 `EXPERIMENTS_VISION_ROUND11.md §10`**（臂⑤→🚫跳过 / 臂⑥ AIMv2→⏸暂缓 / **R11-L2→✅下一优先级** / R13→⏸批准后只做 OV2 单臂 / R11-E→⏸等 short≥18.5M）。⚠️ 全部**未经批准、不主动起训练**；WAITING 置 1 省 token，等运维在任务书 §3 + §10 勾选后执行。

## R11-L2 文本塔解冻臂（🚀 训练中，2026-10-03）

> 只变「文本塔是否解冻」：基线 = 冻结 CLIP-768（R9 6.08%@15.36M）vs 本臂 = CLIP-768 文本塔 **LoRA 轻量微调**。其余控变量（OV2 w512 · CC12M+Amshaker · 视觉 lr3e-3 · bs512 · N=15.36M/30k 步 · IN-1k frozen-trunk lp）**全固定**；**重跑 R4 坍缩判据 C1–C4**。预注册见 `EXPERIMENTS_VISION_ROUND11.md §11`。

- **实现**：`r9_train.py` 增 `--text-finetune {frozen,lora}` + `--lora-rank/--lora-alpha/--lora-lr`；LoRA = `torch.nn.utils.parametrize` 注入 q_proj+v_proj（r=8 α=16），`lora_B` 零初始化（步 0 == 冻结塔），**可训 +0.30M**；视觉 lr 3e-3、LoRA lr 1e-4（独立参数组）。探针 `pT` 改为每次用当前文本塔重算。
- ✅ **smoke 通过（exit 0）**：8 卡 30 步、`trainable=0.295M`、探针 `C1=0.09–0.34 / C2_gap=+0.03–+0.07 / C4=OK`（无坍缩）；ckpt 字段 `text=lora-CLIP-768 / text_trainable_params=294912`。
- 🚀 **正式 30k 已启动（23:54，`.12` 全 8 卡）**：`bash r11_run_lora.sh 30000` → `R11L2_lora_w512`；日志 `/tmp/r11_lora.log`；hostname `whag0pgpuap12`、GPU 独占核验。ETA ~2h + 自动回收 4 ckpt IN-1k lp。
- **预注册裁定（§11.4）**：坍缩（C1>0.95 / C2_gap≤0.005 / C4 fail）→ 负结果；未坍缩且 lp > 基线+1.5（>7.58%）→ 局部翻盘（冻结文本塔锁上限）；否则未翻盘。
## 历史条目已滚动归档（2026-10-03）

- 更早的全部巡检/流水（R1–R9 完整过程，live MEMORY 原 95.7KB）已滚动归档至 `daily-memories-vision/2026-10-03.md`（追加「滚动归档快照」）+ 各日期 daily 文件（2026-09-30 / 10-01 / 10-02）。live MEMORY 已压至 ≤32KB。
- 结论性产物（架构排名 / scaling / 回填建议）以 `EXPERIMENTS_VISION.md` 顶部与 `EXPERIMENTS_VISION_ROUND{2..9}.md` 为权威，不受滚动影响。
