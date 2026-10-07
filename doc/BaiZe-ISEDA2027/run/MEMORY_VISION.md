# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | 🚀 **② mask-ratio 消融运行中**（PID 1752298, arm 0.3 step~9550/30k ~32%, ~36min elapsed, ~265 steps/min, NFS 波动 113-242ms/iter, ETA all-5-arms+eval ~17:00-18:00）. ✅ **lp 协议 A/B 桥接全部完成**（3 ckpts Δlp 极稳定 ~+10pp）. ✅ R12b 训练+eval 全部完成. ✅ 论文 §6 改写完成. ✅ 前置 AIMv2 提速归因实测完成. ✅ 两份 HTML 报告+方向建议已交. ✅ **官方 AIMv2 范式方案已批准+6 点修订已落实(本轮 grep 复验 13 处关键词✅)**. ✅ **mask-ratio+weight-ratio 消融脚本就绪+AIMv2 AR 代码 smoke test 通过** |
| WAITING | 1（🚀 **② mask-ratio 消融运行中** PID 1752298, arm 0.3 step~9550/30k ~32%, NFS 波动 img/s 2300-4500, C1=0.32(无坍缩), ETA all-5-arms+eval ~17:00-18:00. 5 arms: 0.3/0.5/0.6/0.75/0.9, 30k steps/arm, save@10k/20k/30k, eval at end. ✅ **lp bridge 全部完成**: ckpt1 Δlp=+10.05pp, ckpt2 Δlp=+10.05pp, ckpt3 Δlp=+10.17pp ⇒ BaiZe 协议系统性低估 lp ~10pp. ✅ pretrain GPU1-7 已归还(09:44). **完成后 = ③ weight-ratio 消融(4臂,脚本就绪) → ④ 官方 AIMv2 AR 范式(方案+6点修订已就绪)**）|
| ERROR_COUNT | 5（① R9 w512 首跑 crash：损坏 jpg → data.py 修复 ② 续跑首试 crash：r9_train.py `log()` → 改 `print()` 修复 ③ 8-GPU 并行 eval NFS 争用卡死 → 改 4-GPU r12_single_eval.sh ④ lp bridge crash 缺 `import T` → line 39 加 import ⑤ lp bridge crash CUDA OOM → `extract_features_streaming` 加 `torch.no_grad()` + `linear_probe_mainstream` 加 `Xtr.to(device)`） |
| BUDGET_USED | R2–R12 累计 ≈215 GPU·h + 归因实测 ~0.5 GPU·h + **R12b 训练完成**（~13.3h×8卡≈106.4 GPU·h）+ R12b eval 完成（~0.5 GPU·h）+ lp bridge 进行中（~5.8 GPU·h, 1 GPU×5.8h） |
| 更新 | **2026-10-07 10:28（🚀 ② mask-ratio 消融巡检#1: arm 0.3 step~9550/30k ~32%, 36min elapsed, loss~3.8/contrast~3.5/patch_mse~0.28, C1=0.32(无坍缩), NFS 波动 img/s 2300-4500(113-242ms/iter), 8 GPU 16.4GB/卡. ETA all-5-arms+eval ~17:00-18:00. AIMv2 plan 6点修订 grep 复验✅(13处). weight-ratio 脚本就绪. git synced(fetch✅with proxy). 📦 体积：TASK=29.5KB / MEMORY=30.9KB（均≤32KB✅）· *[更早见 daily-memories-vision/2026-10-06.md]* |
| WINNER | OpenVision2（R8 六架构四指标第一；R9/R10 证「塔越小越高」，w512=126.8M 是既有对比基线，不改架构排名） |

## R9 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND9.md）

- 阶段一：w512/w768/w1024 lp = 6.10/3.63/1.03% → 选 **w512（126.8M）**。阶段二：w512×108k=55.3M，lp 峰值 7.70%@51.2M。
- **scaling 拟合**（11 点 R²≈0.94）：幂律 `acc=0.251−0.864·N^−0.090`（渐近 **25.1%**）；外推 20% 需 41 万亿样本 → **本地 ≈118M 上限够不到**。
- **结论**：瓶颈在数据量与目标函数（AIMv2 ≈120 亿对 vs 我们 649× 少），非架构。

## R10 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND10.md）

- 2D 拟合（19 点 R²=0.980）：M 边际效应**全区间为负** ≈ −2.2 lp pp/参数翻倍 → 数据受限区间**加宽塔是负收益**。
- **w384@15.36M=7.99% 为全部宽度最高**；最优 M 仍在观测下界（71.5M）之下 → 无饱和点、更小塔持续更优。

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

## R11-L / R11-L2 / caption-weight / R11-F / R11-G / R11-H / R12 / 3-epoch 全部完成

> 📦 以上全部已闭合实验（R11-L 四臂→R11-L2→caption-weight→R11-F→R11-G→R11-H→R12→3-epoch 续跑）的详细流水已滚动归档 → `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（**原文未改**）。**结论以 `EXPERIMENTS_VISION_ROUND11.md` + `EXPERIMENTS_VISION_ROUND12.md` 为权威。**

**一句话结论**：R11-L 四臂（SigLIP/LocalLoss/CoCa/基线）**无一翻盘**；R11-L2 文本塔解冻（LoRA）**未翻盘**（−0.80 pp）；caption-weight 三点消融 → **caption 监督与 IN-1k 正交**；R11-F 数据源横比 → GPIC short/medium/short+medium **无显著差异**；⭐ **R11-G AIMv2 长跑翻盘**（lp@55.3M=19.76% vs 基线 7.40%，R²=0.91，渐近 >>25.1%）；R11-H 纯 AR **无翻盘**（翻盘依赖对比项）；R12 全量 58.8M 1.05 epoch lp@61.4M=17.57%（< R11-G 同 N）；3-epoch 续跑 344k/176M lp=20.27%，35 点 scaling R²=0.94，非单调 7/34，a 撞上界不可定。

## AIMv2 提速归因实测（✅ 完成，2026-10-06 12:33–12:44）

> 运维指令「运维前置 · AIMv2 提速」（已归档 → `ARCHIVE_OPERATOR_VISION.md`）。目的：bs 64/128/256 归因 + num_workers 扫描 → 判断瓶颈是数据/IO 还是算力。详见 `EXPERIMENTS_VISION_ROUND12.md §1`。

### batch size 扫描（nw=6 固定）

| BS | Global | steady img/s | ms/iter | Mem(GB) | GPU util |
|---:|---:|---:|---:|---:|:---|
| 64 | 512 | **4993** | ~102 | 16.5 | 62–83% (~70%) |
| 128 | 1024 | **6293** | ~134 | 26.8 | 49–95% |
| 256 | 2048 | **8314** | ~250 | 47.6 | 48–100% |

### num_workers 扫描（bs=64 固定）

| NW | steady img/s | Notes |
|---:|---:|:---|
| 6 | **4993** | baseline |
| 12 | **4262** | 更差（NFS 争用） |
| 16 | **5311** | 略好（噪声范围） |

### 诊断：**bs=64 下数据/IO 受限（非算力受限）**

1. GPU util ~70%（未饱和）→ 符合「util≲70% = 数据/IO 受限」判据
2. image/s 随 MBS 上升（4993→8314, +66%）= 每步开销摊销，**非**算力受限标志
3. ms/iter 亚线性增长（64→256 = 4×, ms/iter 2.45×）→ 混合瓶颈，以数据/IO 为主
4. 显存远未满（16.5/81.6 GB = 20%）；num_workers 无显著效果（NFS 带宽是瓶颈）
5. 无本地 NVMe；1.7 TiB RAM 但数据 ~742 GB（预热增益有限，NFS 波动仍存）

### 处方：保持 bs=64 / global 512 / nw=6

- ❌ 加 MBS → 改 recipe → 不并入 scaling 曲线
- ❌ 加 num_workers → NFS 争用（nw=12 实测更差）
- ❌ 无本地 NVMe 可用
- **当前 ~5000 img/s 是 NFS 架构下可达到吞吐率**

### 全量训练时长估算（实测 img/s）

- 总 unique pairs ≈ 58.8M；1 epoch ≈ 114,844 步
- 实测 ~5000 img/s → **1 epoch ≈ 3.3h**；保守 ~4500 img/s → **1 epoch ≈ 3.7h**
- R12 3-epoch 实测平均 4470 img/s → 1 epoch ≈ 3.7h（吻合）
- **>1 epoch？是。** 2 epoch ≈ 7.2h, 3 epoch ≈ 10.8h
- 从零 1 epoch ≈ 29.6 GPU·h；从零 3 epoch ≈ 88.8 GPU·h

### 脚本路径

- `vision/r12_throughput_bench.sh`（bs 扫描）+ `r12_throughput_bench_128_256.sh` + `r12_throughput_bench_nw.sh`
- 日志：`/tmp/bench_bs{64,128,256}.log` + `/tmp/bench_nw{12,16}.log`
## 本唤醒流水

- [12:33–12:44] **AIMv2 提速归因实测**：bs 64/128/256 各 250 步 + nw 6/12/16 各 250 步 → bs=64 steady 4993 img/s (GPU util~70%), bs=128 6293, bs=256 8314; nw 6=4993, nw=12=4262(更差), nw=16=5311 → **诊断数据/IO 受限**, 1 epoch≈3.3–3.7h. 详见 `EXPERIMENTS_VISION_ROUND12.md §1`.
- [12:45] 归档 R11-L→3-epoch 完成段到 `daily-memories-vision/2026-10-06.md`（MEMORY 31KB→9KB 腾位）；写 `EXPERIMENTS_VISION_ROUND12.md`.
- [12:50–15:25] R12b 训练早期巡检#1–#3 + 论文 §6 改写 + commit → 已归档至 daily-memories-vision/2026-10-06.md「滚动归档」节
- [16:00–16:50] R12b 巡检#4–#5 + TASK 归档 + lp 协议桥接 prep → 已归档至 daily-memories-vision/2026-10-06.md「滚动归档(07:12)」节
- [18:00–18:10] **R12b 心跳巡检#6 + watcher + scaling + AR 方案（CPU-only, 不打断 R12b）**：step~110300/272000 ~40.6%, loss~1.68 (contrast~1.56, patch_mse~0.13), C4=OK, 11 ckpts(step10k–110k). NFS 波动 img/s 5500→1990, avg~370 steps/min, 剩余~162k 步, ETA~02:00. 训练健康, 无需干预. **本轮交付**: ① **`r12b_eval_watcher.sh`** backup watcher 已启动(PID 3926100, setsid+orphan-resilient) — 防 R12 orphan 问题复发: 训完自动检测 built-in eval 是否触发, 若未触发则 4-GPU 并行 eval + `r12b_scaling.py` 分析; `bash -n` 通过. ② **`r12b_scaling.py`** R12b 专用 scaling 分析脚本(py_compile OK) — 解析 r8_eval_in1k 输出, 幂律+对数线性拟合, 对比 R12 3-epoch/R11-G/R9 InfoNCE. ③ **`VISION_AIMV2_OFFICIAL_PLAN.md`** 官方 AIMv2 AR 范式实现方案(队列④, 待运维批准): 含规格对照表 + 代码修改清单(复用 CoCaDecoder/PatchPredictor/Attention.attn_mask) + 参数量对比(Arm A 127.4M vs Arm B ~194.3M) + 成本估算(30k≈20GPU·h / 108k≈72 / 272k≈182) + 预注册判据(lp±1.5pp + C1-C4 + 公平性表) + 许可证合规(Apple Sample Code 不可抄). 📦 体积：TASK=28KB / MEMORY=14KB（无归档）.
- [18:41] **R12b 心跳巡检#7（CPU-only, 不打断 R12b）**：step~120550/272000 ~44.3%, loss~1.7 (contrast~1.55, patch_mse~0.14), C4=OK (probe@120000: C1=0.3924/C2_gap=+0.1300/loss_ema=1.82). 12 ckpts 已落盘（step10k–120k, ~510MB each）. 7/8 GPU util 71-100%（GPU4 transient 0% — 数据加载瞬时）, mem 16.5GB each. NFS 波动 img/s 5479→2375, ckpt-to-ckpt~294-323 steps/min, 剩余~152k 步, ETA~03:00（NFS 波动致吞吐波动, 原 ETA~02:00 略滑）. watcher PID 3926100 健康（5min 间隔日志正常, 57 ranks alive）. GPIC 下载 4384/8000 tar(~54.8%) 仍在进行. 无新运维指令（git fetch: HEAD=origin/main 同步）. 所有排队项 prep 已完成. 训练健康, 无需干预. 📦 体积：TASK=28KB / MEMORY=15KB（无归档）.
- [19:18] **运维指令执行：AIMv2 官方范式方案 6 点修订（CPU-only, 不打断 R12b）**：R12b step~130800/272000 ~48%, loss~1.5, C4=OK. 运维已批准 `VISION_AIMV2_OFFICIAL_PLAN.md` 但要求先落实 6 点审阅意见 → **已逐项修订**：① §3.2 加「AR≠MAE 语义说明」（AR=给定前文预测后文≠MAE双向重建；位置0只见patch0自身、位置195无target被shift掉）；② §3.1 加「cross-attn→causal vision patches 声明」（🚫 若attend双向patch则非官方范式）；③ §6 caption handicap 显著标注（官方LLaMA-3长caption~12B vs 我们短alt-text→text AR信号天然弱）；④ §4 吞吐预留3500-4000 img/s + smoke test + 若30k>3h重新评估；⑤ §3.3 B' 改「缩宽度(hidden~256)非减深度」+ 同时报cap_loss/pixel_loss隔离原因；⑥ §5.2 加中间态(+0.5<Δlp<+1.5=趋势性优势)+组合判定(Δlp大但C1≈0.90=表征退化). 文件 7.1KB→12.0KB(+41/-17). 📦 体积：TASK=32KB / MEMORY=16KB（无归档）.
- [19:55] **R12b 心跳巡检#9 + 消融脚本 prep（CPU-only, 不打断 R12b）**：step~141050/272000 ~52%, loss~1.6 (contrast~1.45, patch_mse~0.15), C4=OK (probe@141000: C1=0.4140/C2_gap=+0.1240/loss_ema=1.5589). 14 ckpts(step10k–140k, ~510MB each). NFS dip: img/s 5547→1661 (GPU1 瞬时 0%), ms/iter 92→316, 剩余~131k 步, ETA~03:00–07:00（NFS 波动致吞吐大幅下降，可能恢复）. 53 r9_train 进程存活（watcher 计 41 为 ps 时序伪警，非真崩溃）. watcher PID 3926100 健康. GPIC 下载 4425/8000 tar(~55.3%). 无新运维指令（git fetch 失败=proxy 未带，HEAD=origin/main 同步）. ✅ **新交付**: ① `run_mask_ratio_ablation.sh`（队列②, 5 臂 mask_ratio=0.3/0.5/0.6/0.75/0.9, 30k 步/臂, 同 R11-L 口径 CC12M+Amshaker, `bash -n` 通过）; ② `run_weight_ratio_ablation.sh`（队列③, 4 臂 contrast:patch=1:2/1:0.5/0.5:1/2:1, 30k 步/臂, `bash -n` 通过）—— 两脚本均含预注册判据注释 + 自动 ckpt 收集 + eval, R12b 训完即可按序开跑. 📦 体积：TASK=31KB / MEMORY=18KB（无归档）.
- [20:31] **R12b 心跳巡检#10（CPU-only, 不打断 R12b）**：step~159900/272000 ~58.7%, loss~1.8 (contrast~1.66, patch_mse~0.15), C4=OK (probe@159900: C1=0.4712/C2_gap=+0.1211/loss_ema=1.8278). 15 ckpts(step10k–150k, ~510MB each). 吞吐恢复: img/s~5300–5700, ms/iter~92, GPU util 66–92%, mem 16.5GB each. 剩余~112k 步, ETA~00:30 Oct7(~3.9h). watcher PID 3926100 健康(57 ranks alive, 5min 间隔日志正常). GPIC 下载 4448/8000 tar(~55.6%). 无新运维指令(git fetch✅ with proxy, HEAD=origin/main 同步). 所有排队项 prep 已完成, 仅待 R12b 训完. 📦 体积：TASK=31KB / MEMORY=18KB（无归档）.
- [21:05] **R12b 心跳巡检#11（CPU-only, 不打断 R12b）**：step~175200/272000 ~64.4%, loss~1.6 (contrast~1.48, patch_mse~0.15), C4=OK (probe@175200: C1=0.4434/C2_diag=0.1672/C2_off=0.0450/C2_gap=+0.1222/loss_ema=1.6663). 17 ckpts(step10k–170k, latest 170000@20:53, ~510MB each). **NFS争用致吞吐波动**: img/s ~2300–5600 (ms/iter 93–223), 当前 dip~2300–2800; 7/8 GPU 100% util (GPU3 瞬时0%=数据加载瞬时), mem 16.5GB each. 剩余~96.8k 步, ETA~Oct7 00:00–02:30(NFS争用致吞吐波动, 若恢复5500则~2.5h, 若持续dip~2500则~5.4h). watcher PID 3926100 健康(57 ranks alive, 5min 间隔日志正常, latest 21:05:56). GPIC 下载 4473/8000 tar(~55.9%). disk: /nas_train 84%(34T avail) /nas_inference 68%(15T avail) OK. 无新运维指令(git fetch✅ HEAD=origin/main=6fe1c304 同步). 所有排队项 prep 已完成, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=31KB / MEMORY=19KB（无归档）.
- [21:40] **R12b 心跳巡检#12（CPU-only, 不打断 R12b）**：step~185250/272000 ~68.1%, loss~2.0 (contrast~1.85, patch_mse~0.14), C4=OK (probe@185400: C1=0.4103/C2_diag=0.1658/C2_off=0.0332/C2_gap=+0.1326/loss_ema=1.7821). 18 ckpts(step10k–180k, latest 180000@21:22, ~510MB each). **吞吐已恢复**: img/s~5300–5600 (ms/iter~92–97), 8/8 GPU util 70–82%, mem 16.5GB each. 剩余~86.8k 步, ETA~Oct7 00:00(~2.3h, 按~5400 img/s 估算). watcher PID 3926100 健康(etimes~13224s, 57 ranks alive, 5min 间隔日志正常). GPIC 下载 4499/8000 tar(~56.2%). disk: /nas_train 84%(34T avail) /nas_inference 68%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main 同步). 所有排队项 prep 已完成, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=20KB（无归档）.
- [22:14] **R12b 心跳巡检#13（CPU-only, 不打断 R12b）**：step~197650/272000 ~72.7%, loss~1.9 (contrast~1.78, patch_mse~0.13), C4=OK (probe@197400: C1=0.4695/C2_diag=0.1627/C2_off=0.0418/C2_gap=+0.1208/loss_ema=1.7154). 20 ckpts(step10k–190k, latest 190000@21:55, ~510MB each). **吞吐稳定**: img/s~5300–5700 (ms/iter~93–96), 8/8 GPU util 46–100%, mem 16.5GB each. 剩余~74.4k 步, ETA~Oct7 00:10(~1.9h, 按~5400 img/s 估算). watcher PID 3926100 健康(etimes~15242s, 57 ranks alive). GPIC 下载 4523/8000 tar(~56.5%). disk: /nas_train 84%(34T avail) /nas_inference 68%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main=c2c2cc41 同步). 所有排队项 prep 已完成, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=21KB（无归档）.
- [22:48] **R12b 心跳巡检#14（CPU-only, 不打断 R12b）**：step~208700/272000 ~76.7%, loss~1.8–2.3 (contrast~1.60–2.19, patch_mse~0.12–0.16), C4=OK (probe@208500: C1=0.4075/C2_diag=0.1640/C2_off=0.0310/C2_gap=+0.1330/loss_ema=2.0818). 20 ckpts(step10k–200k, latest 200000@22:22, ~510MB each). **NFS吞吐dip**: img/s~2900–3700 (ms/iter~137–176, vs 稳态~93), GPU util 0–100%(GPU5瞬时0%=数据加载瞬时), mem 16.5GB each. 剩余~63.3k 步, ETA~Oct7 00:30–01:45(NFS-dependent, 若恢复~5400则~1.7h, 若持续dip~3100则~2.9h). watcher PID 3926100 健康(etimes~17270s). GPIC 下载 4548/8000 tar(~56.9%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, origin/main=b2eef0e3 同步, 最后vision ops=6c40f1c6@18:40). 所有排队项 prep 已完成, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=22KB（无归档）.
- [23:25] **R12b 心跳巡检#15（CPU-only, 不打断 R12b）**：step~220000/272000 ~80.9%, loss~1.5–1.9 (contrast~1.37–1.75, patch_mse~0.13–0.16), C4=OK (probe@219900: C1=0.4266/C2_diag=0.1582/C2_off=0.0308/C2_gap=+0.1274/loss_ema=1.7355). 21 ckpts(step10k–220k, latest 220000@23:24, ~510MB each). **NFS吞吐dip持续**: img/s~2300–2700 (ms/iter~188–226, vs 稳态~93), GPU util 0–100%(GPU3瞬时0%=数据加载瞬时), mem 16.5GB each. 剩余~52k 步, ETA~Oct7 00:54–02:20(NFS-dependent, 若恢复~5400则~1.3h, 若持续dip~2500则~2.9h). watcher PID 3926100 健康(etimes~5.4h). GPIC 下载 4572/8000 tar(~57.2%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, origin/main=08ab285d 同步). ✅ **本轮核验所有排队项脚本就绪**: lp bridge(`run_lp_protocol_bridge.sh`+`lp_protocol_bridge.py`✅) + mask-ratio ablation(`bash -n`✅) + weight-ratio ablation(`bash -n`✅) + AIMv2 plan 6 点修订(逐项 grep 核验: ①AR≠MAE ②cross-attend causal ③handicap ④smoke test/吞吐 ⑤缩宽度非减深度 ⑥中间态+0.5<Δlp<1.5, 全部✅). 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=23KB（无归档）.
- [23:57] **R12b 心跳巡检#16（CPU-only, 不打断 R12b）**：step~231300/272000 ~85.0%, loss~2.0 (contrast~1.88, patch_mse~0.14), C4=OK (probe@231300: C1=0.4467/C2_diag=0.1563/C2_off=0.0296/C2_gap=+0.1267/loss_ema=2.0070). 23 ckpts(step10k–230k, latest 230000@23:42, ~510MB each). **NFS吞吐dip持续但偶有恢复**: img/s~2470–2900 (ms/iter~177–207, vs 稳态~93), 偶见5900 img/s瞬时; GPU util 0–100%, mem 16.5GB each. 剩余~40.7k 步, ETA~Oct7 01:30–02:30(NFS-dependent, 若恢复~5400则~1.1h, 若持续dip~2700则~2.5h). watcher PID 3926100 健康(etimes~5.9h, 5min日志正常 latest 23:56:00 step 230650). GPIC 下载 4582/8000 tar(~57.3%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, origin/main=e13549b5, last vision ops=6c40f1c6@18:40). 所有排队项 prep 已完成+核验, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=25KB（无归档）.
- [00:33] **R12b 心跳巡检#17（CPU-only, 不打断 R12b）**：step~241700/272000 ~88.9%, loss~1.4–1.6 (contrast~1.3–1.5, patch_mse~0.14), C4=OK (probe@241500: C1=0.4895/C2_diag=0.1641/C2_off=0.0416/C2_gap=+0.1225/loss_ema=1.5195). 24 ckpts(step10k–240k, latest 240000@00:26, ~510MB each). **吞吐已恢复至稳态**: img/s~5300 (ms/iter~97, vs 稳态~93), GPU util 28–100%, mem 16.5GB each. 剩余~30.3k 步, ETA~Oct7 01:22(~49min, 按~5300 img/s). watcher PID 3926100 健康(子进程 sleep 300 PID 2846208). GPIC 下载 4608/8000 tar(~57.6%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main=049231d1, last vision ops=ff48cfa6). ✅ **再次核验所有排队项脚本就绪**: lp bridge(`bash -n`✅) + mask-ratio ablation(`bash -n`✅) + weight-ratio ablation(`bash -n`✅) + AIMv2 plan 6 点修订(grep 核验: ①AR≠MAE ②cross-attend causal ③handicap ④smoke test ⑤缩宽度 ⑥中间态, 全部✅). 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=26KB（无归档）.
- [01:06] **R12b 心跳巡检#18（CPU-only, 不打断 R12b）**：step~252800/272000 ~92.9%, loss~1.5-2.1 (contrast~1.3-2.0, patch_mse~0.13-0.17), C4=OK (probe@252600: C1=0.4666/C2_diag=0.1503/C2_off=0.0271/C2_gap=+0.1232/loss_ema=1.8758). 25 ckpts(step10k–250k, latest 250000@00:57, ~510MB each). **NFS吞吐dip持续**: img/s~2600 (ms/iter~195, vs 稳态~93), GPU util 54-85%, mem 16.5GB each. 剩余~19.2k 步, ETA~Oct7 02:09(~63min, 按~2600 img/s). watcher PID 3926100 健康(etimes~7.1h). GPIC 下载 4633/8000 tar(~57.9%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main=4865a566, last vision ops=6c40f1c6). 所有排队项 prep 已完成+核验, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=31KB / MEMORY=27KB（无归档）.
- [01:47] **R12b 心跳巡检#19（CPU-only, 不打断 R12b）**：step~264800/272000 ~97.4%, loss~1.5-2.0 (contrast~1.3-2.0, patch_mse~0.13-0.16), C4=OK (probe@264600: C1=0.4566/C2_diag=0.1555/C2_off=0.0258/C2_gap=+0.1297/loss_ema=1.6851). 26 ckpts(step10k–260k, latest 260000@01:36, ~510MB each). **NFS吞吐dip持续**: img/s~2500 (ms/iter~200, vs 稳态~93), GPU util 66-80%, mem 16.5GB each. 剩余~7.2k 步, ETA~Oct7 02:11(~24min, 按~2500 img/s). watcher PID 3926100 健康(latest 01:46 step 264050). GPIC 下载 4663/8000 tar(~58.3%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main=55bb94f9 同步). 所有排队项 prep 已完成+核验, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=27KB（无归档）.
- [02:23] **R12b 训练完成 + auto-eval 进行中**：272k 步全部跑完(12:54–02:14, ~13.3h), 28 ckpts(step10k–270k+final vision.pt, 510MB each)已落盘. built-in r8_eval_in1k.py 正在逐 ckpt 评估(sequential, 1 GPU): 已出 step10k(lp=11.77%/zs=4.20%) + step20k(lp=12.44%/zs=4.98%), 均显著高于 R11-G 同期(step10k~7.4%) — 大数据集(69.7M vs 18.5M)起效. eval 进度~3/28, ETA~03:00. watcher PID 3926100 健康(等待 built-in eval 完成后自动跑 r12b_scaling.py). ✅ 资源核查: IN-1k official val=50k/14 parquet(labels 0-999) ✅ + full train=1.28M/294 parquet ✅ → lp 协议 B 组可用全量. ✅ R13 奇偶控制已验证(r13_eval_official.py L10 → 79.81% 用 Protocol A → 协议不压低强模型). run_lp_protocol_bridge.sh(bash -n ✅) 配置: R12b final+R12 1epoch+R11G AIMv2 ckpts. 无新运维指令. GPIC 下载~58%. 下一步: eval 完成 → ① lp 协议 A/B → ② mask-ratio → ③ weight-ratio → ④ 官方 AIMv2. 📦 体积：TASK=32KB / MEMORY=29KB（无归档）.
- [03:07] **R12b eval 完成 + lp 协议 A/B 桥接启动**：R12b 28/28 ckpts eval 全部完成(02:45 ALL DONE). **lp_max=18.81%(final vision.pt, 139.3M token)**. Scaling: R²=0.8867, power law `0.4781-1.1757·N^(-0.0749)`, 渐近47.8%. ⚠️ **关键发现**: R12b(69.7M data, 2ep, 139M token) lp_max=18.81% **< R11-G(18.5M, 1ep, 55.3M) 19.76%** → 更多 unique 数据(GPIC 短 caption 占76%)不改善 lp; R12 3-epoch(58.8M, 3ep, 174M) 20.32% 仍是最高. 归因: GPIC 短 caption 稀释信号 + 2ep<3ep. R12b 结果已写入 `EXPERIMENTS_VISION_ROUND12.md §2`. ✅ lp 协议 A/B 桥接已启动: PID 1499158, GPU0, 3 ckpts(R12b final+R12 1ep+R11G AIMv2) × Protocol A(BaiZe)+B(SGD+cosine 90ep bs1024 IN-norm full-train 1.28M) × 3 repeats. 日志 `/tmp/lp_bridge_full.log`. 无新运维指令(git fetch✅, origin/main=4ede00bc). GPIC 下载~58%. 8 GPU 全空闲(bridge 仅用 GPU0). 📦 体积：TASK=32KB / MEMORY=29KB（无归档）.
- [03:20] **lp bridge bug 修复 + 重启**：首次启动的 bridge (PID 1499158) crash — `NameError: name 'T' is not defined` in `lp_protocol_bridge.py:57 get_transform()` → 缺 `import torchvision.transforms as T`. **已修复**（line 39 加 import）+ py_compile ✅ + `get_transform('clip'/'imagenet')` 均返回正确 Compose ✅. **重启** PID 2227716, GPU0, 同配置(3 ckpts × both protocols × full-train 1.28M × 3 repeats). 正在加载 Protocol A 数据(NFS I/O, ETA~03:30 开始 GPU 编码). 📦 体积：TASK=32KB / MEMORY=30KB（无归档）.
- [03:55] **lp bridge OOM 修复 + 第 3 次重启**：PID 2227716 crash — `CUDA OOM` in `extract_features_streaming` L150 `vision(b)` (GPU0 80GB 满). **根因**: `extract_features_streaming` 缺 `torch.no_grad()` → 每个 batch 的计算图累积在 GPU 不释放 → ~100 batches 后 80GB 满. **修复 3 处**: ① `lp_protocol_bridge.py` L149 加 `torch.no_grad()` (with `torch.autocast`) ② L186 加 `Xtr=Xtr.to(device)` ③ wrapper 加 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. **重启** PID 807654, GPU0. GPIC 4756/8000 tar(~59.5%). 📦 体积：TASK=31KB/MEMORY=30KB.
- [04:35] **lp bridge 巡检 + mask-ratio NW bug 修复**：PID 807654 健康(etimes~2440s, GPU0 40% util, read_bytes 17.8GB). Protocol A ckpt1(R12b final) lp=18.79%✅. Protocol B streaming 51/294 parquet(~222K imgs encoded, NFS I/O bound, ETA~9h ~13:00). **修复 `run_mask_ratio_ablation.sh` NW bug**：`$NW` 未定义(`set -u` 会 crash)→ 加 `NW=6`（与 weight-ratio 脚本一致）. bash -n✅. 验证: weight-ratio 脚本 OK, r9_train.py `--contrast-weight`/`--patch-loss-weight`/`--mask-ratio` 均存在✅. AIMv2 plan 6 点修订已核验✅(①AR≠MAE ②causal cross-attn ③short caption handicap ④smoke test+吞吐 ⑤B'缩宽度 ⑥中间态判定). GPIC 4784/8000 tar(~59.8%). git synced(HEAD=origin/main=0d48aad4). 8 GPU 全空闲(bridge 仅用 GPU0). 无新运维指令. 📦 体积：TASK=32KB/MEMORY=31KB（无归档）.
- [06:35] **lp bridge 巡检#2**：PID 807654 健康(etimes~9633s~2.7h, GPU0 2.4GB 0%util=数据加载阶段). **ckpt1(R12b final) ✅全部完成**: Protocol A=18.79%, Protocol B seed0=28.88%/seed1=28.82%/seed2=28.81% → **B=28.84±0.03%, Δlp=+10.05pp** ⇒ BaiZe 协议系统性低估 lp ~10pp(3 seed σ=0.03pp, 极稳定). **ckpt2(R12 1ep) 进行中**: Protocol A=20.22%, Protocol B streaming 51/294 parquet(NFS I/O bound). ckpt3(R11G AIMv2) 待跑. ETA~10:00-11:00(ckpt1耗时~2h, 2 ckpt剩余~3-4h). GPIC 4845/8000 tar(~60.6%). GPUs 1-7 空闲(②③④需8GPU⇒须等bridge). git synced(7cfd9d26, fetch✅ with proxy, 无新运维指令). 📦 体积：TASK=32098B(31.3KB) / MEMORY=~32KB（均≤32KB, 无归档）.
- [07:12] **lp bridge 巡检#3（用户手动唤醒, 与 loop cline PID 2504046 并发）**：PID 807654 健康(etimes~11838s~3.3h, 88%CPU, GPU0 2.4GB/39%util). ckpt1(R12b final)✅全完成: A=18.79%, B=28.84±0.03%(3seed: 28.88/28.82/28.81), Δlp=+10.05pp⭐. ckpt2(R12 1ep)进行中: A=20.22%✅, B streaming 151/294 files~51%(658058/1281167 imgs, NFS I/O bound). ckpt3(R11G AIMv2)待跑. ETA~10:00-11:00. GPUs 1-7全空闲(②mask-ratio/③weight-ratio/④AIMv2 AR 需8GPU⇒须等bridge完成). GPIC下载~60.6%(上次实测06:35, 本次NFS慢find超时未更新). git synced(fetch✅with proxy, HEAD=origin/main, 0新提交, 无新运维指令). 📦 体积：TASK=32098B(31.3KB)/MEMORY=30594B→+流水≈30.3KB(归档2条旧流水, ≤32KB✅).
- [07:52] **📋 昨夜工作汇报 HTML 已产出**（用户直令 2026-10-07）：`doc/BaiZe-ISEDA2027/report_10_07_vision_overnight.html`（自包含, 27.7KB, 内联 SVG 管线图, 零外部依赖, 外链检查✅空, @import✅无, wc -c✅≤200KB）。窗口 2026-10-06 22:00→10-07 07:52(数据截止)。8 章节: HERO/TL;DR/KPI/时间线/证据(含 2 次 bridge crash 原文)/卡点/今晨现状/commit 列表(17 条)。核心结论: R12b 训练+eval完成(lp_max=18.81%) + lp 协议 A/B ckpt1 Δlp=+10.05pp + AIMv2 AR 代码 smoke test 通过. 📦 体积：TASK≈31.3KB / MEMORY≈30.8KB（≤32KB✅, 无归档）.
- [09:42] **⭐ lp bridge 全部完成! + 归档2块（TASK 40.6KB→29.5KB）**：PID 807654 已退出, GPU0 释放. **3 ckpts 全部完成**: ckpt1(R12b) A=18.79% B=28.84±0.03% Δlp=+10.05pp, ckpt2(R12 1ep) A=20.22% B=30.27±0.03% Δlp=+10.05pp, ckpt3(R11G AIMv2) A=19.77% B=29.94±0.04% Δlp=+10.17pp. ⭐ **Δlp~+10pp 极稳定 across all 3 ckpts** ⇒ BaiZe 协议系统性低估 lp ~10pp. 8 GPU 全空闲(nvidia-smi 0-4MiB). ⚠️ GPU1-7 运维指令借给 pretrain 至 11:00(GPU12_ALLOC.md) 但 nvidia-smi 显示全空闲. 归档2块→ARCHIVE_OPERATOR_VISION.md(昨夜汇报HTML + 2026-10-05全量训练). 滚动2条流水→daily. git synced(fetch✅with proxy, HEAD=origin/main=5a04e51e). 📦 体积：TASK=29.5KB / MEMORY=30.7KB（均≤32KB✅）.
- [09:55] **🚀 ② mask-ratio 消融已开跑**：8 GPU 全空闲 + lp bridge 完成 + 运维指令「8卡硬需求⇒写申请行」⇒ 在 GPU12_ALLOC.md 申请区写行 + 立即开跑 `run_mask_ratio_ablation.sh`（5 arms: 0.3/0.5/0.6/0.75/0.9, 30k steps/arm, PID 1752298). arm 0.3 step200/30k: loss=5.68, contrast=5.23, patch_mse=0.45, ~4500 img/s, 8 GPU 16.4GB/卡 47-73%util. ETA~14:30(5arms×~54min+eval). pretrain 矩阵若启动会检测到 GPU 占用并等待. commit a2b8d9ae pushed✅(with proxy). 📦 体积：TASK=29.5KB / MEMORY=30.4KB（均≤32KB✅）.
- [10:28] **② mask-ratio 消融巡检#1**：PID 1752298 健康(etimes~2169s~36min). arm 0.3 **step~9550/30000 ~32%**: loss~3.8, contrast~3.5, patch_mse~0.28, C1=0.3211(probe@9300, 无坍缩, C2_gap=+0.124, C4=OK). NFS 波动大: ms/iter 113-242, img/s 2300-4500, avg~265 steps/min. 8 GPU 16.4GB/卡, util 0-100%(GPU6 偶发 0%=数据加载). ckpt1@step10k 即将落盘. ETA: arm0.3 完成~11:45, 全 5 arms+eval ~17:00-18:00. ✅ AIMv2 plan 6 点修订 grep 复验(13处关键词命中). ✅ weight-ratio 脚本就绪. ✅ pretrain GPU1-7 已归还(09:44, GPU12_ALLOC.md). git synced(fetch✅with proxy, Already up to date). 无新运维指令. 📦 体积：TASK=29.5KB / MEMORY=30.9KB（均≤32KB✅, 无归档）.



## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
