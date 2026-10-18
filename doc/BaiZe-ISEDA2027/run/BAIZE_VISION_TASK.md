# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🆕 运维指令 · 2026-10-18（📊 ArmB 的 **1/2/3 epoch 检查点**也要测 ProtB，并与**历史最好结果**对比，写进中文 HTML）· 用户直令 · 最高优先

> **用户令（2026-10-18）**：「让 vision 把这次 1,2,3 epoch 检查点的 ProtB 也测一下，在中文 html 报告中，跟原来的最好结果做下对比」

**① 先认清现实：这三个 ckpt 现在盘上没有，必须"回放到那个时刻"取**
- ArmB 训练脚本是 `--save-every 10000 --keep-ckpts 2`（`run/vision/run_armB_openclip.sh:70-72`）⇒ **只留最近 2 个 `checkpoint_*.pt`**，日志里可见 `[ArmB] removed old ckpt checkpoint_30000.pt`。
- 已知步数换算（GBS 8192、4 epoch=57250 步 ⇒ **每 epoch ≈ 14,313 步**）：**1ep≈14313 · 2ep≈28626 · 3ep≈42939**（以 `--steps 42940`=3ep 的历史记录为准，四舍五入到 10000 的整倍数没有意义，**就用这三个精确步数**）。
- ⇒ **取证**：先 `ls -lt $OUT/checkpoint_*.pt $OUT/latest.pt`，若 `14313/28626/42939` 不在盘上（几乎必然），走 ② 的 **resume-and-stop 回放**；🚫 **不要**用 `checkpoint_10000/20000/40000` 冒充 1/2/3 epoch。

**② 回放取 ckpt（推荐做法，成本远低于重跑）**
- 若能拿到**当时的 `latest.pt`**（含完整 optimizer 状态）→ 直接 `--resume` 到目标步再停，最省；
- 若拿不到（只剩 final 的 `open_clip_state_dict.pt`）→ **从零重训**，只跑到目标步即停（数据/seed/超参必须与本次 ArmB **完全一致**：`data_snapshot_20261017_gpic8000.txt`、seed 1234、GBS 8192、MBS 512、lr 1e-3/warmup 2000、mask 0.6）。
- 每个目标步都保存**干净权重**（`open_clip_state_dict.pt` 形式，直接喂 `armB_protb_eval.py`），命名 `armB_ep{N}_step{step}_openclip.pt`，放在 `$OUT/epoch_ckpts/`。
- 回放**必须**先报成本：每 epoch ≈ **18.37h/4 ≈ 4.6h**（本次实测 57250 步 18.37h）⇒ 到 1/2/3ep 合计 ≈ **27.6h**（8 卡）。**开跑前先报这个数给运维确认**（若 `.12` 已有其它任务占用则先报排期）。

**③ ProtB 评测（口径与正式 ProtB 完全一致，才有可比性）**
- 用 `run/vision/armB_protb_eval.sh` + `armB_protb_eval.py`：**full IN-1k 1.28M train + 50k val、SGD 90ep、seeds 0/1/2、feature=projected、5-NN**。
- 每个 epoch ckpt 出一份 `armB_protb_ep{N}_results.json`（字段与 `armB_protb_vitb16_224_results.json` 对齐：lp_mean/lp_std/5nn/zs 等）。
- 4 个点（1ep/2ep/3ep/4ep-final）**必须用同一个 eval 口径**；4ep 已有结果就直接引用，**不重跑**。
- 若要省时间：特征提取可复用同一套 IN-1k 图像缓存（8 shard 已落盘），只换 backbone 权重。

**④ 中文 HTML 报告（交付物）**
- 路径：`reports/report_vision_armB_epoch_curve_zh.html`（自包含、无外链）。
- **必须包含**：
  1. **主表**：epoch=1/2/3/4 → `lp mean±std`（3 seeds）、`5-NN`、`zs@IN-1k`、`C1`、训练 loss/contr/patch；
  2. **折线图**（内联 SVG）：lp / 5-NN 随 epoch 的曲线，标出预注册阈值 **lp=58.03%**（不倒退）与 **61.0% + 5-NN 48.98%**（接受混合）；
  3. **与历史结果的对比表（分两层写，禁止把不同配方混成一行）**：
     - **第 1 层 · 与 ArmB 同族/同口径可比**：
       - `ArmA`（open_clip ViT-B/16 86.2M + **InfoNCE**，ProtB）：**58.03±0.02% / 5-NN 53.98%** → 这是 ArmB 的直接对照（只差目标函数）。
       - 预注册阈值：lp ≥ 58.03%（不倒退）、≥ 61.0% 且 5-NN ≥ 48.98%（接受混合）。
     - **第 2 层 · 历史基线（塔更大/配方不同，只能作"项目最好结果"参看，🚫 不参与 ArmB 优劣判断）**：
       - `④-4ep`（**126.8M** 自研塔，ProtB）：**67.05±0.02%**（ProtA 56.70 / zs 40.64→72.64 / k-NN 42.35；`EXPERIMENTS_VISION.md §9.5/§9.7`）
       - `ArmC（merge3ds）`：**68.25±0.01%**（**GBS 2048 / LR 2e-3 / warmup 8000 / 154,500 步**，与 ④-4ep *逐字节一致除 batch/LR*；判据 NUL/MODERATE→按 Δ+1.20pp 判 NULL、但 zs +5.53pp / ProtA +2.71pp）
       - ⇒ 表头必须写清：**ArmB 是 86.2M 塔 + AIMv2-style 目标，与 ④/ArmC 差 3 个变量（塔规模、目标、数据/步数）**，只能作"距项目最好结果还差多少"的参照。
     - **一行"项目最好结果"**：`ArmC 68.25±0.01%`（当前最高；`④-4ep 67.05%` 次之）。
  4. **一段诚实结论**：ArmB 每 epoch 的边际增益（lp/5-NN 是否仍在涨或已饱和）、是否越过 61% 门槛、与 58.03%（ArmA）的 Δ、以及与 67.05/68.25 的差距；**差异归因必须列全变量**（塔 86.2M vs 126.8M、InfoNCE vs AIMv2-style、数据 11350 shard vs ④ 的数据、GBS/LR/步数）。🚫 不得写"AIMv2 优于/劣于 InfoNCE X pp"这类单因果结论（ArmA vs ArmB 才是单变量，且只在同塔同数据前提下成立）。
  5. **附录**：每个 ckpt 的训练步数/时间戳/文件大小/评测命令原文/随机种子。

**⑤ 顺序与纪律**
- **P0 不打断**：正在跑的 4ep ProtB（`run_armB_protb_eval.sh`）**先跑完**，其结果是④表里的第 4 行；🚫 不要 kill、不要抢卡。
- **P0.5**：4ep 结果一出 → 先出中文报告 v1（ArmA/④/ArmC/ArmB-4ep 对比），**不含 1/2/3ep**，让用户先看到 ArmB 是否达标。
- **P1**：再按 ②③ 回放 1/2/3ep → 报告 v2（补全 epoch 曲线）。
- commit 前缀 `vision armB-epochs:`；`MEMORY_VISION.md` 顶部加一行指针（≤32KB 自滚）。


### 🆕 运维指令 · 2026-10-17 12:4x（⚔️ 立即 kill `.12` pretrain 进程 → 起 ArmB；**改 4 epoch** → 训完评 ProtB）· 用户直令 · 最高优先
> ⏩ 已执行并归档（杀 pretrain → ArmB 4-epoch）已完成；详情 → `daily-memories-vision/2026-10-17.md`。

### 🆕 运维指令 · 2026-10-17 12:2x（🖥️ `.12` 专属 vision；pretrain 迁 `.29`）· 用户直令 · 最高优先
> ⏩ 已执行并归档（`.12` 专属 vision）已生效；详情 → `daily-memories-vision/2026-10-17.md`。

### 🆕 运维指令 · 2026-10-17 12:0x（🚀 启动 ArmB：open_clip ViT-B/16 + AIMv2-style · 全量 8000 GPIC · 3 epoch）· 用户直令 · 最高优先

> **用户令（原文）**：「vision：启动下边实验 目标=AIMv2-style 数据=全量8000 tar GPIC + CC12M + Amshaker 塔=open_clip ViT-B/16 86.2M warmup=2000步 LR=1e-3，min_lr=1e-4 GBS=8192，MBS=512(如果OOM，则GBS=4096，MBS=256) epoch=3 按照这个配方训练，给个ETA 使用 open_clip接口（便于嵌入LLaVA-OneVision架构用lmms-eval评测）」

**⓪ 与上一条的关系**：本块**取代**上一条（2026-10-17 报告块）的 ③ ArmB 配方与排队；上一条的 **① ArmA 报告 / ② 兼容性附录仍要交**（训练起来后 CPU 补，见 ⑤）。

**① 配方（逐字执行，不改）**：
- 目标：**AIMv2-style** = `contrast_weight×InfoNCE + patch_loss_weight×MSE(predictor(patches[mask]), target[mask])`；`contrast_weight=1.0, patch_loss_weight=1.0, mask_ratio=0.6`（沿用 `r9_train.py:782-807` 口径；报告写清）。
- 数据：**GPIC 全量 8000 tar + CC12M 1100 + Amshaker 2250 = 11,350 shards ≈117.3M 对**；新建 `data_snapshot_20261017_gpic8000.txt`；起训前 `ls | wc -l` + `find -name '*.incomplete'` 核，**实际数字写进 log/report**（若不足/路径不同，按实际并声明）。
- 塔：**open_clip ViT-B/16 224**（visual 86.2M / total 149.6M，双塔随机初始化）。
- 优化：**warmup=2000 步**；**LR 1e-3 → min 1e-4（cosine）**；AdamW wd=0.1、betas=(0.9,0.98)、grad_clip=1.0、bf16、seed=1234（未指定项沿用 ArmA，报告列明）。
- 批：**GBS=8192, MBS=512/卡（累加 2）**；**OOM 回退 GBS=4096, MBS=256/卡（累加 2）**；实际档位 + 峰值显存必须记录。
- 步数：**3 epoch**；N≈117.25M → **GBS8192 ≈42,940 步**（14,313/epoch）；回退 GBS4096 ≈85,876 步；以实际 N 重算并写进报告。
- save every **10,000** 步 + final；保留 latest + 最近 2 个 ckpt（省盘）。

**② open_clip 接口（硬要求）**：
- 必须 `open_clip.create_model_and_transforms('ViT-B-16', pretrained=None)`；不得改模型类/换自研塔。
- **predictor 只作训练辅助头**；取 patch tokens 必须**复用同一次 vision 前向**（forward hook / `forward_intermediates`），**禁止二次 forward**（否则 ETA +35–45%）。
- 保存：`open_clip_state_dict.pt`（**剥离 predictor**）+ `predictor.pt` + `config.json`；验收 `open_clip.create_model_and_transforms('ViT-B-16', pretrained=<ckpt>)` **strict load 通过**。
- LLaVA-OV/lmms-eval：新增 `mllm_bridge/open_clip_vitb16_768.py`（注册 `baize-vitb16-768`；`encode_image` → `[B,196,768]`；image_size 224 / patch 16 / 无 spatial merge）+ `export_for_llava_ov.py`；CPU 单测：open_clip 加载 / `encode_image` 形状 / wrapper 与原生 allclose / projector 768→LLM dim 形状。lmms-eval 用 1 个小样本冒烟（不阻塞训练）。

**③ 起训（先探再起；🚫 不 kill pretrain）**：
- 起训前 `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv` 原文落盘。
- `.12` 8×H100 正被 **pretrain 80B decay** 全占（ETA ~10-20 02:30）⇒ **不得 kill/降速/抢卡**。
- 先试 `.29`（`ssh -o BatchMode=yes -o ConnectTimeout=5 10.239.2.29 'nvidia-smi'`）：若 8 卡空闲且同一 NFS 的 `py310` + open_clip 可用 → **立即在 .29 起训**；SSH 不通/环境缺 ⇒ 记 blocker（原文），**不得擅自装包/改共享 env**。
- `.29` 不可用 ⇒ 写 `run/vision/run_armB_when_free.sh`：每 5min 轮询 `.12` 8 卡（无 compute apps 且每卡显存 >70GB）→ 满足即 `setsid` 起训；记录 pretrain 实际结束时间。
- 若用户明确要求「停 pretrain 抢卡」才可停；本指令默认**不抢**。

**④ ETA（按实测公式，起训后用自己的实测值刷新）**：
- N≈117.3M（GPIC 8000×12,537≈100.3M + CC12M 11.0M + Amshaker 6.0M）；3 epoch = **351.9M samples**。
- 吞吐：ArmA 实测 **3.37 it/s @ GBS2048 = 6,902 samples/s**；MBS512 预计 +0–5%，AIMv2 头 <1%（前提 = 复用前向）⇒ **6,900–7,300 samples/s**。
- **纯训练 ≈13.4–14.2h**；+启动/ckpt/最终 ProtB（3 seeds）≈1–2h ⇒ **总 ETA ≈15–16.5h**；GPU·h ≈ **110–120**。
- 若二次前向（禁止）→ 19–21h；若实测吞吐 6,000 → 16.3h 纯训练。
- **两条起训情景**：① `.29` 空 → 代码 1–2h 后起（约 13:00–14:00）→ **10-18 04:00–06:30 完成**；② 只能等 `.12` → 10-20 02:30 起 → **10-20 17:00–19:00 完成**。
- 报告必须给：实际 N / steps / samples/s / 墙钟 / 峰值显存 / 是否 OOM 回退。

**⑤ 交付与次序**：
1. **P0**：`run/vision/armB_aimv2_openclip.py` + `run/vision/run_armB_openclip.sh` + `run/vision/run_armB_when_free.sh` + CPU 单测（1–2h）。
2. **P0**：起训（.29 优先，否则排队 .12）。
3. **P1**：训练起来后用 CPU 补 **ArmA 中文报告 + 兼容性附录**（上一条要求）。
4. `MEMORY_VISION.md` 状态头 + `daily-memories-vision/2026-10-17.md`；commit `vision armB:`。

**⑥ 纪律**：不改配方；不 kill pretrain；不伪造 ETA/结果；不占 GPU 做 CPU 工作；任务书/MEMORY ≤32KB 自滚。


### 🆕 运维指令 · 2026-10-17（📄 ArmA 结果中文报告 + 归档 · 🔌 open_clip × AIMv2-style 兼容性工程评估）· 用户直令 · 最高优先

> **用户令（2026-10-17）**：「vision：把 ArmA 结果写成中文报告并归档。问题：open_clip 接口和AIMv2-style不能兼容吗？」

**① 报告（先做，纯写作零 GPU）**：`reports/report_vision_armA_openclip_result_zh.html`，中文自包含，必须含：
- **协议**：ProtB（full IN-1k 1.28M train + 50k val，SGD 90 epochs，seeds 0/1/2），`feature=projected`，ckpt=`latest.pt`；数字取 `run/vision/armA_protb_vitb16_224_results.json`（lp 58.02/58.07/58.02 → **58.03±0.02%**；5-NN **53.98%**）。
- **训练口径**：open_clip **ViT-B/16 224**（visual 86.2M / total 149.6M，双塔随机初始化）、**ClipLoss InfoNCE**、GBS 2048（MBS 256×8）、LR 2e-3→2e-4（warmup 8000）、**154,500 步**、数据 GPIC(7437)+CC12M(1100)+Amshaker(2250)=10,787 shards ≈118M 对；证据 `run_armA_openclip.sh:13-15,45-52` + `armA_openclip_train.py:169-187,256-316`。
- **对比表**（同表列：协议/塔/参数量/目标/步数/数据/ProtB lp/5-NN）：ArmA vs **④-4ep（67.05±0.02 / 42.35）**、④-2ep、V3、R11-G 等，数值以 `EXPERIMENTS_VISION.md` 既有记录为准。
- **关键解读（必须写）**：ArmA = **lp −9.02pp / 5-NN +11.63pp** ⇒ 检索型表征强、线性可分性弱，与「C1/lp 背离」假设一致；⚠️ **不是单变量对照**（塔 86.2M vs 126.8M、目标 InfoNCE vs AIMv2-style dense、步数/样本不同）⇒ **不得写成「AIMv2 目标比 InfoNCE 好 9pp」**。
- **诚实条款**：内部 ProtB 口径、非官方榜；单 backbone/单预算点；5-NN 与 lp 口径不同；仅评测 3 seeds（训练单 seed）。
- **归档**：报告 + 结果 JSON + 训练/评测日志路径写入 `MEMORY_VISION.md` 与 `EXPERIMENTS_VISION.md` 新 §「ArmA（open_clip ViT-B/16, 2026-10-17）」；commit `vision armA:`。

**② 回答问题（报告附录 A，必须给结论 + 代码行号）**：
- **结论：分两层 —— 模型/推理接口兼容；open_clip 自带「训练损失/循环」不兼容（需自定义，不是不能做）。**
- **兼容证据**：ArmA 用的就是 open_clip 模型，`model(imgs, texts) → (img_feat, txt_feat, logit_scale)` + `ClipLoss`（`armA_openclip_train.py:286-287`）；导出侧只需 `encode_image` 的 pooled/patch 输出（`mllm_bridge/open_clip_baize.py:8-16,26-34`）。predictor 是训练期辅助头，**不进入推理图** ⇒ 不影响 open_clip 加载/评测。
- **不兼容点**：open_clip 的 loss 家族（Clip/SigLIP/CoCa/GenLIP…）**没有 patch 级重建目标**；其训练循环只吃 `(image,text)`，不提供 mask 采样/patch 目标。我们这套 AIMv2-style 是**自研训练环**：`loss = contrast_weight×InfoNCE + patch_loss_weight×MSE(predictor(patches[mask]), target[mask])`，`mask_ratio=0.6`（`r9_train.py:782-807`；实现说明 `reports/report_vision_aimv2_impl.html`）。
- **做「open_clip 模型 + AIMv2-style」需要 4 件事（≈1–2 人日，纯 CPU）**：
  1. 在 open_clip ViT 上挂 `PatchPredictor`（≈0.66M）；
  2. 取 patch tokens（按 open_clip 版本用 `visual.forward_features` / `visual.trunk.patch_embed` / `forward_intermediates` 之一，或用 forward hook **复用同一次前向**，避免二次算力；实现前先 `python -c` 打印 `type(model.visual)` 与可用方法并截图/日志存证）；
  3. 自定义 loss + 训练步（照 ArmA 循环改 ≈50 行）；
  4. ckpt 存 predictor；**导出 open_clip 权重时必须剥离 predictor**（或单独存 `predictor.pt`），否则 `load_state_dict(strict=True)` 会报 unexpected keys；若 `contrast_weight=0`（纯 AR）→ `find_unused_parameters=True` 或冻结文本塔（ArmA 现为 `False`）。
- **概念澄清**：官方 AIMv2 = 多模态自回归（图文 token + decoder，弃用对比），open_clip 的对比接口无法表达；本仓 `r9_train.py` 的 `aimv2_ar` + `decoder_depth` 才是那一支。报告须分开写，避免混淆。

**③ ArmB**：配方/起训/排队**已被 2026-10-17 12:0x 顶部指令取代**（open_clip ViT-B/16 + AIMv2-style，全量 8000 GPIC，3 epoch）；本条只保留 **① 报告** 与 **② 兼容性附录**。预注册判据仍有效：lp ≥58.03% 不倒退；≥61.0% 且 5-NN ≥48.98% → 接受混合；否则写负面结论。

**④ 纪律**：不占 GPU（除放行）；每个数字可溯源到 `文件:行`/原始日志；不改已发布数值；与 pretrain 线 IO 错峰。


> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> 不得回退：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| 损失 | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| 文本塔 | 冻结 CLIP-ViT-L/14-336（768-d），不解冻 / 不用 LoRA |
| 注意力 | 双向（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| 证据 | R11-G：lp 7.40% → 19.76%（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 20.27% |
| 否决项 | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| 报告 | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | 0.6 | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | 1.0 / 1.0（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | SGD + momentum 0.9 + cosine（5-ep warmup） |
| Batch size | full-batch（49,970） | mini-batch 1024 |
| Epochs | 100（= 100 次梯度更新） | 90（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | IN-1k full train = 1,281,167 张 |
| Eval 集 | 自切分 val（50/类 = 5,000） | IN-1k 官方 validation（50k） |
| Normalization | CLIP mean/std | ImageNet mean/std |
| 重复 | seed 0 单次 | 3 seeds（0,1,2）→ mean ± σ |
| 证据 | Δlp ≈ +10.05 pp（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| 内部横比 | 旧实验（R2–R14）均用 Protocol A，相对排序仍有效（A/B 排序一致）；但绝对数字须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；与 DINOv2/MAE/iBOT 等公开值可直接横比 |

> ⚠️ Protocol A → B 迁移说明：旧实验的相对结论（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，不混表。

---


> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `vision 归档: …` 前缀。
> 本轮动作：本任务书现 ≈24KB（在上限内）⇒ 暂时无需归档；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，优先滚它）。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）


- 🚫 不许闭门造车：涉及"别人怎么做"（架构/loss/评测/数据）必须去读官方仓库或论文原文（能 clone 就 clone）—— 不得凭二手描述下结论（本线已因此出错一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂必须报「参数量 + 训练 token + 每步耗时」，不许只比 acc。
- 预注册：判据先定后测，不许事后改。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ 21KB、`MEMORY_VISION.md` ≈ 32KB（已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_VISION.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的巡检/流水条目（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
