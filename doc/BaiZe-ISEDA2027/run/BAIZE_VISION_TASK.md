# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔥 运维令 · 2026-10-19 22:5x（**立即启动 ArmD，不要再 idle**）· 用户直令「vision：尽快启动」

> 用户令：「vision：尽快启动」（针对 21:26 下发的 ArmD 块，直到 22:35 仍未启动 ⇒ 现予明确催促）。
> **现状核查（运维侧 22:35 实测）**：`run/vision/` 下**无任何 armD 脚本**；`data.py` 仍是 10-18 07:16 版本未被修改；`MEMORY_VISION.md` 停在 21:26。⇒ **ArmD 完全未开工。**
> **本轮必须完成（按顺序，全部在 `.12`）**：

**① 先做数据前置（阻塞项，二选一，**默认走 A**）**
- **A（默认·推荐）**：给 `run/vision/data.py::build_mixed_loader` **加 parquet 直读分支**（按文件扩展名分流：`.parquet` → pyarrow 逐 row-group 读 `image.bytes`+`caption`；`.tar` → 走现有 wds 路径）。**零转码、省 2.2TB**。
  - 参考已有实现：`run/vision/prep_data.py` 里 `sniff_ext()` + `pf.read_row_group(i)` + `tbl['image'].to_pylist()` 的写法可直接复用。
  - ⚠️ WebMix-38M 与 wit_base 的列名若是 `image`(struct{bytes,path}) + `caption`，与 LLaVA 一致；**若列名不同，先 `pq.ParquetFile(fn).schema_arrow` 打印前 3 个字段名再适配**，并把实际列名写进日志。
- **B（仅当 A 实在做不出来）**：`prep_data.py` 转 tar；**必须先 `df -BG` 确认落地盘 ≥2.3TB**（`/home` 96%、`/nas_train` 85%），否则禁用 B。
- 🚫 **禁止**把 parquet 路径直接塞 `--data`：`empty_check=False` 会把 0 样本静默吞掉。

**② 生成 6 源快照并报数（起训前必做）**
- 写 `run/vision/data_snapshot_20261019_armD.txt`，逐行绝对路径，6 源 = GPIC(8000 tar) + CC12M(1100 tar) + Amshaker(2250 tar) + WebMix(3886 parquet 或转出的 tar) + wit_base(330 parquet) + InternVL(2000 tar)。
- **实测并打印**：每源文件数、总 pair 数（parquet 用 `metadata.num_rows` 累加；tar 按已知估计）。
- **算 3-epoch 步数**：`steps = ceil(3 × 总pairs / 8192)`，**先把数字贴进日志再起训**（不得沿用 57250）。

**③ 起训（`run_armD_openclip.sh`，复制 `run_armC_openclip.sh` 只改 5 处）**
- `OUT=/nas_train/app.e0031982/datasets/baize-vision/out/armD_20261019_aimv2_openclip_vitb16_224`
- `--lr 2e-3 --min-lr 2e-5`（cosine 保持）、`--steps <②算出的值>`
- `--data` = 6 源（快照文件 + 新三源路径）
- **其余逐字不动**：塔/目标/mask 0.6/**wd 0.01（ArmC 值，不是 0.1）**/GBS 8192/MBS 512/accum 2/**warmup 2000**/seed 1234/save 10k keep 2。
- 启动：`setsid bash run_armD_openclip.sh > /tmp/armD_openclip_train.log 2>&1 < /dev/null &`

**④ 起训后 ≤30min 回报**：数据解法(A/B) + 各源文件数/pair 数 + **3ep 实际步数** + 首 loss + 显存峰值 + 预计耗时（按 ArmC 0.78 it/s 外推）+ **四变量披露声明**（数据/epoch/LR/min_lr）。

**⑤ 边界**：🚫 不覆盖 `armB_*`/`armC_*` 产物；🚫 不杀 `.29` pretrain（~02:50 收尾）；🚫 不动 harness relay。

### 🆕 运维指令 · 2026-10-19 21:2x（🚀 **ArmD：数据扩到 6 源 + 3 epoch + LR 2e-3 / min_lr 2e-5**）· 用户直令 · **最高优先**（覆盖 ArmC 块的"idle"状态）

> 用户令（原文）：「vision: 启动 ArmD。数据：ArmC数据+新下载的三个数据集 -> 3 epoches。学习率: LR=2e-3, min_LR = 2e-5, cosine。其它跟 ArmC一致不变。」
> 已确认（用户答）：「对，就是 **WebMix-38M + wit_base + InternVL-SA1B** 这三套（纳入 ArmC 的 GPIC8000+CC12M+Amshaker 后一起训）」

#### 0. 配方（ArmD vs ArmC，逐项标注是否变量）

| 项 | ArmC（基线） | **ArmD（本次）** | 变量? |
|:--|:--|:--|:--|
| 视觉塔 | open_clip ViT-B/16 224（86.2M） | 同左 | 否 |
| 目标 | AIMv2-style：InfoNCE 1.0 + masked-patch-MSE 1.0，mask 0.6 | 同左 | 否 |
| **数据** | GPIC 8000 + CC12M 1100 + Amshaker 2250 = **11,350 shards** | 同左 **+ WebMix-38M + wit_base + InternVL-SA1B** = **变量①** | **是** |
| **epoch / 步数** | 4 epoch = **57,250 步** | **3 epoch**（步数须按新数据量重算，见 §2） | **是** |
| LR | 1e-3 | **2e-3** | **是** |
| scheduler | cosine | **cosine**（保持） | 否 |
| min_lr | 1e-5 | **2e-5** | **是** |
| warmup | 2000 | **2000（不变）** ⚠️ 见 §3 | 否 |
| GBS / MBS / accum | 8192 / 512 / 2（OOM 回退 4096/256） | 同左 | 否 |
| wd / betas / 精度 | **0.01** / (0.9,0.98) / bf16 / grad_clip 1.0 | **同左（沿用 ArmC，不回退到 ArmB 的 0.1）** | 否 |
| seed / save | 1234 / save-every 10000 / keep 2 | 同左 | 否 |
| 输出目录 | `armC_20261018_aimv2_openclip_vitb16_224` | **`armD_20261019_aimv2_openclip_vitb16_224`**（独立，🚫 不覆盖 ArmB/ArmC） | — |

> ⚠️ **ArmD = 四变量改动**（数据 + epoch + LR + min_lr）。**报告中不得把 ArmD vs ArmC 的任何 Δ 归因于单一变量**，与 ArmC 的两变量披露框同等对待。
> ⚠️ **wd 必须保持 0.01（ArmC 值）**，不是 ArmB 的 0.1 —— "其它跟 ArmC 一致" 的准确读法。

#### 1. 🔴 **前置阻断：两套新数据集是 parquet，训练脚本只吃 tar**（必须先解决，否则起不了）

实测格式（`DATA_LEDGER.md`）：

| 数据集 | 落盘 | 物理格式 | 训练脚本兼容性 |
|:--|:--|:--|:--|
| MVRL/WebMix-38M | `/nas_user/app.e0031982/datasets/MVRL/WebMix-38M/` · 3886 parquet / 1.9TB / ~38.8M pairs | **parquet** | ❌ 需转换 |
| VedaLabs/wit_base | `/nas_user/app.e0031982/datasets/` · 330 parquet / 287GB / ~6.48M pairs | **parquet** | ❌ 需转换 |
| hanlincs/InternVL-SA1B-Caption-WebDataset | `/nas_user/app.e0031982/datasets/` · 2000 tar / 1.5TB / ~22.4M pairs | **tar (wds)** | ✅ 直读 |

**`data.py::build_mixed_loader` 只认 tar 内 `txt` 或 `json`+`caption` 字段**，不读 parquet。

**处置（A→B 顺序，A 优先，因为磁盘紧张）**：
- **A（推荐，零转码、省 2.2TB）**：给 `data.py` 加 **parquet 直读分支**（在 `build_mixed_loader` 里按扩展名分流，用 pyarrow 逐 row-group 读 `image.bytes` + `caption` 列）。**属训练侧代码改动，须在回报里列 diff 并在报告披露**。
- **B**：用 `prep_data.py`（**已有**，正是 parquet→wds tar 工具，`--src/--out/--max/--shard`）转成 tar。⚠️ **`/home` 已 96%、`/nas_train` 85%** ⇒ **必须先确认落地盘有 ≥2.3TB 余量再动手**；余量不足则走 A。
- **🚫 禁止**：把 parquet 路径直接塞进 `--data` 让训练静默跑空；`empty_check=False` 会把"0 样本"吞掉而不报错。

#### 2. 步数计算（3 epoch，必须先报数再起训）
- 先用实测 pair 数算出 `总 pairs = 11350 shards 对应 pairs + WebMix 38.8M + wit_base 6.48M + InternVL 22.4M`；**不得沿用 shard 数当 pair 数**。
- `steps = ceil(3 × 总pairs / GBS)`；GBS=8192；OOM 回退 GBS=4096 时步数 ×2。**报出实际值后才起训**。

#### 3. ⚠️ warmup 与 LR 的交互（须如实记录，不擅自改）
- LR 翻倍（1e-3→2e-3）但 warmup 仍 2000 步 ⇒ **warmup 期间等效学习率也翻倍**，峰值 2e-3 到达得更陡。用户令「其它跟 ArmC 一致不变」⇒ **保持 2000 不动**，但在报告与回报里**写明这一交互**（若起训 500 步内出现 loss 爆炸/nan，先停下报 blocker，🚫 不自行改 warmup）。

#### 4. 执行顺序（严格串行，与 ArmC chain 同构）
1. **前置**：`.12` 8 卡确认空闲（ArmC 已闭环，armC #173 idle 已确认 0MiB）→ 查 pretrain 是否在 `.12`（应无，pretrain 在 `.29`）
2. **数据前置**：解决 §1 → 生成 `data_snapshot_20261019_armD.txt`（6 源合并清单，逐行绝对路径）→ **核验 shard 数 = 11350 + 新三套实际文件数**，并在日志打印
3. **训练**：`run_armD_openclip.sh`（复制 `run_armC_openclip.sh` 改：OUT 目录名、`--lr 2e-3`、`--min-lr 2e-5`、`--steps <3epoch值>`、`--data` 六源、其余逐字不动）→ `setsid` 后台 + 日志 `/tmp/armD_openclip_train.log`
4. **② ProtB**：`run_armD_protb_eval.sh`（同 ArmC 口径，输出 `armD_20261019_protb_vitb16_224_results.json`）
5. **③ MLLM 三阶段**：Stage-1(2500) → Stage-1.5 LoRA(20000) → Stage-2(3500)，**仅换视觉塔 ckpt**
6. **④ 12 集评测**：**必须离线缓存模式**（`rerun_failed_benchmarks_armC_offline.sh` 同类做法：两处缓存指 `/tmp`、`HF_HUB_OFFLINE=1`、**不走代理**）—— 这是 ArmC 当时 8/12 MISSING 的教训，**别再踩**
7. **⑤ 报告**：`generate_armD_mllm_report.py` → `report_vision_armD_20261019_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §14`

#### 5. 回报要求（起训后 ≤30min 内）
- 数据前置解法（A 还是 B）+ 实际 shard/pair 数 + 落地盘余量
- 3 epoch 实际步数、GBS、warmup、预计耗时（按 ArmC 实测 0.78 it/s 外推）
- 多变量披露声明（数据/epoch/LR/min_lr 四项）
- 首 ckpt 时间、8 卡显存峰值

#### 6. 边界
- ✅ **只**改：`--lr`、`--min-lr`、`--steps`、`--data`、`--output-dir`（+ §1 的数据侧改动）
- 🚫 不改：视觉塔、目标函数、mask 0.6、GBS/MBS、**wd 0.01**、seed、save 策略
- 🚫 不覆盖 `armB_*` / `armC_20261018_*` 任何产物
- 🚫 不杀 `.29` 的 pretrain（decay 预计 10-20 ~02:50 收尾）
- 🚫 不动 harness 的 `.12` 侧 relay（双 relay 问题待运维裁定）

---

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


### 📦 运维指令 · 2026-10-18 17:1x（ArmC：min_lr 1e-4→1e-5 + wd 0.1→0.01 · 4 阶段）— 已归档

> **已闭合**（ArmC 全链路 DONE 2026-10-19）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-19 归档）。**结论**：ArmC = 两变量；训练 57250 步 ✓ / ProtB lp 62.332·5-NN 54.718 / MLLM 三阶段 ✓ / 12 集 12/12 DONE avg 25.78%（vs ArmB 26.10%，**不可分辨**）。ArmC 配置已被 ArmD 承接（见顶部 ArmD 块，**wd 0.01 沿用**）。需要时再读。

### 📦 运维指令 · 2026-10-17 12:4x/12:2x/12:0x（kill .12 pretrain→起 ArmB / .12 专属 / 启动 ArmB）— 已归档

> **已闭合**：ArmB 已训完并评测（ProtB 62.093/58.102、MLLM 26.10%），ArmC/ArmD 依次承接。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

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
