# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | ✅ **ALL CONVERGED — 待运维派新任务**. ④ Arm B-hybrid DONE (30k, no collapse C1~0.48, lp@30k=1.37% vs baseline 13.49%). ✅ 论文 6_vision_encoder.tex 更新 (mask-ratio表+weight-ratio表+§VI-D AR范式探索, main.pdf 11p 0err). ✅ 全线总结报告 report_vision_encoder_final.html (10节/4个SVG/28.6KB). ✅ GPU orphans cleaned (8GPU=4MiB idle). ✅ git commit+push pending. |
| WAITING | 1（✅ **全线实验收敛** — ④ hybrid=1.37% 信息量已获取, Arm A baseline=13.49% 仍最优. 论文+报告均已完成, 待运维审阅+派新任务. 视觉编码器线 R2–R14 全部 closed. |
| ERROR_COUNT | 5（① R9 w512 首跑 crash：损坏 jpg → data.py 修复 ② 续跑首试 crash：r9_train.py `log()` → 改 `print()` 修复 ③ 8-GPU 并行 eval NFS 争用卡死 → 改 4-GPU r12_single_eval.sh ④ lp bridge crash 缺 `import T` → line 39 加 import ⑤ lp bridge crash CUDA OOM → `extract_features_streaming` 加 `torch.no_grad()` + `linear_probe_mainstream` 加 `Xtr.to(device)`） |
| BUDGET_USED | R2–R12 ≈215 + R12b(106.4) + lp bridge(5.8) + mask-ratio(78.4+0.5) + weight-ratio(~65.4+0.5) + ④ AIMv2 AR Arm B(2.1) + Arm B-hybrid(~24) ≈ **累计 ~498 GPU·h**（最终） |
| 更新 | **2026-10-08（全线收敛·论文+报告完成）**: ✅ **④ Arm B-hybrid DONE**: 30k steps, no collapse (C1~0.48 振荡0.30–0.55), lp@30k=1.37% (vs Arm A baseline 13.49%, Δ=−12.1pp). 结论: InfoNCE防AR坍缩, 但causal AR在7.7M短caption数据规模下无法匹敌bidirectional. ✅ **论文 6_vision_encoder.tex 更新**: +Table tab:vismask (mask-ratio倒U形5臂) +Table tab:visweight (weight-ratio 4臂) +§VI-D "Causal Autoregressive Paradigm Exploration" (Table tab:visar, label sec:vis-ar). pdflatex×3+bibtex, 0err, 11p, 无undefined cross-ref for new labels. ✅ **全线总结报告**: report_vision_encoder_final.html (10节: TL;DR/实验设计/架构选型/scaling/消融/AIMv2范式/文本塔/官方对比/正式训练启示/局限, 4个inline SVG数据图, 28.6KB). ✅ GPU orphans cleaned (8×H100 back to 4MiB idle). ✅ EXPERIMENTS_VISION.md updated with final ④ results. 📦 体积：TASK=30.3KB / MEMORY=~21KB（均≤32KB✅）· *[更早见 daily-memories-vision/2026-10-08.md]* |
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
- [06:45] **③ weight-ratio 消融 ALL DONE + 结果记录**: ✅ **4臂全部完成 + 16ckpt IN-1k eval完成@05:27:03**. arm4 cw2_plw1(2:1) DONE@05:05: step30k, 7521s, steady_img_s=2691.8, C1_final=0.3475, C1_peak=0.4177@22500, C4=OK无坍缩, final_loss=7.0765. IN-1k lp结果: arm1(1:2)=13.13%(Δ−0.36不显著), arm2(1:0.5)=10.22%(Δ−3.27显著差), arm3(0.5:1)=13.80%(Δ+0.31不显著, 最优), arm4(2:1)=10.21%(Δ−3.28显著差). Baseline 1:1=13.49%. **结论: 无翻盘; contrast_weight过高/patch_weight过低显著有害; patch-heavy方向更宽容**. 8条结论+完整结果表已写入EXPERIMENTS_VISION.md. GPU已释放(PID 3214830已退出). **消融队列②③已全部完成 → 下一步=④ 官方AIMv2 AR范式**. 📦 体积：TASK=31.9KB / MEMORY=16.3KB（均≤32KB✅, 无需归档）.
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

> 📦 15 条 R12b 巡检流水(10-06 12:33–23:57)已归档 → daily-memories-vision/2026-10-06.md（2026-10-07 13:00 滚动）
> 📦 5 条 R12b 巡检#17-19 + 完成 + eval(10-07 00:33–03:07)已归档 → daily-memories-vision/2026-10-07.md（2026-10-08 03:23 滚动）
- [02:23→03:07] *(R12b 训练完成 + eval完成 + lp协议A/B桥接启动)* — 已归档至 daily-memories-vision/2026-10-07.md（lp_max=18.81%, R12b<R11-G, lp bridge PID 1499158 启动）
- [03:20→23:25] *(lp bridge 完成 + mask-ratio 消融 ALL DONE + 报告HTML交付 + weight-ratio arm1 DONE + arm2 启动)* — 已归档至 daily-memories-vision/2026-10-07.md（lp bridge Δlp≈+10pp 3ckpts极稳定; mask-ratio 0.6最优13.49%倒U; report_vision_mask_ratio.html 34.3KB commit ee9db3ca; arm1 cw1_plw2 DONE C1=0.3546）
- [22:46] *(arm1✅DONE + 脚本异常退出→恢复)* — 已归档至 daily-memories-vision/2026-10-07.md（arm1 cw1_plw2 DONE@22:11, C1=0.3546, 脚本crash→恢复PID 3214830）
- [02:48] **③ weight-ratio arm3巡检#2（CPU-only, 不打断训练）**: PID 3214830健康(ppid=1, etimes~14548s~4h). 🚀 **arm3 cw0p5_plw1(0.5:1) RUNNING step~27300/30k~91%**: loss~1.5-1.8, contrast~2.8-3.2, patch_mse~0.17-0.19, C1 probes: 0.3856@26400→0.3650@26700→0.3367@27000→0.3510@27300(无坍缩, C2_gap~+0.12, C4=OK). **C1 从 11700 低谷(0.2924) 回升到 26400(0.3856) 再回落到 27300(0.3510) → 非单调但稳定, C4=OK 无坍缩**. 2ckpts✅(step10k@01:33+step20k@02:16). img/s~2100-2600(NFS波动, ms/iter~210-240), 8GPU 16.5GB/卡 0-100%util. arm3 ETA~02:55(剩~2700步), arm4(2:1) pending, all+eval ETA~05:10. ⚠️ **git fetch FAILED: Network unreachable(github.com:443)** — repo synced(HEAD=origin/main=5a5ac6c0), push将重试. 📦 体积：TASK=31.2KB / MEMORY=~31.2KB（均≤32KB✅, 无需归档）.
- [03:23] **③ weight-ratio arm3✅DONE + arm4巡检#1（CPU-only, 不打断训练）**: ✅ **arm3 cw0p5_plw1(0.5:1) DONE@02:59**: step30k, total=7829s, steady_img_s=4747.0, final_loss=1.6794, C1_final=0.2816@30000, C1_peak=0.4304@2100, C2_gap=+0.1278, C4=OK(无坍缩). C1非单调: 0.4304@2100→0.2924@11700→0.3589@29100→0.2816@30000. 4ckpts✅+vision.pt. arm3结果已写入EXPERIMENTS_VISION.md. 🚀 **arm4 cw2_plw1(2:1) RUNNING step~5900/30k~20%**: PID 3214830健康(ppid=1,~4.6h), loss~8.0(contrast~4.0,patch_mse~0.38), C1=0.3300@5700(无坍缩,C4=OK,早期偏低但回升中). img/s 2200-5200(NFS波动), 8GPU 16.5GB/卡 59-95%util. arm4 ETA~04:30-05:00, all+eval ETA~05:30-06:00. ⚠️ git fetch FAILED(Network unreachable), repo synced(HEAD=origin/main), push将重试. 📦 体积：TASK=31.2KB / MEMORY=14.8KB（归档~19KB→daily-1007, ≤32KB✅）.
- [04:05] **③ weight-ratio arm4巡检#2（CPU-only, 不打断训练）**: PID 3214830健康(ppid=1,~5.3h). 🚀 **arm4 cw2_plw1(2:1) RUNNING step~15500/30k~52%**: loss~7.5(contrast~3.6,patch_mse~0.37), C1 probes: 0.3017@13800→0.3180@14100→0.3320@14400→0.3765@14700→0.3621@15000→0.3614@15300(无坍缩,C2_gap~+0.11,C4=OK, C1从早期0.26回升到0.37后稳定在0.36). step10k ckpt✅(@03:41,510MB). img/s 2000-2800(NFS波动,ms/iter~185-255), 8GPU 16.5GB/卡 0-100%util(GPU6偶发0%). arm4 ETA~05:00(剩~14500步), all+eval ETA~05:30-06:00. ⚠️ git fetch FAILED(Network unreachable), repo synced(HEAD=origin/main), push将重试. 📦 体积：TASK=31.2KB / MEMORY=14.8KB（均≤32KB✅, 无需归档）.
- [04:38] **③ weight-ratio arm4巡检#3 + mask-ratio报告验证（CPU-only, 不打断训练）**: ✅ **mask-ratio HTML报告已验证完整**（report_vision_mask_ratio.html, 34.3KB, 8节+2内联SVG, commit ee9db3ca, 已在origin/main）— 运维指令2026-10-07③已交付. 🚀 **arm4 cw2_plw1(2:1) RUNNING step~23550/30k~78.5%**: PID 3214830健康(ppid=1,~5.9h), loss~7.2(contrast~3.4,patch_mse~0.33), C1 probes: 0.4066@22800→0.3657@23100→0.3678@23400(无坍缩,C2_gap~+0.10-0.11,C4=OK, C1稳定在0.36-0.41). step10k+20k ckpts✅. img/s 2000-2600(NFS波动,ms/iter~200-255), 8GPU 16.5GB/卡 0-82%util. arm4 ETA~05:02(剩~6450步~24min), all+eval ETA~05:30-06:00. ⚠️ git fetch FAILED(Network unreachable), repo synced(HEAD=origin/main), push将重试. 📦 体积：TASK=31.2KB / MEMORY=14.8KB（均≤32KB✅, 无需归档）.
- [07:53] **④ 官方 AIMv2 AR 范式 Arm B 开跑**: ②③消融全部完成, 8GPU全空闲(nvidia-smi 4MiB/卡). 代码已就绪(models.py: OpenVision2.forward(causal=True)+ARTextDecoder(weight-tied,trainable embed)+PatchPredictor; r9_train.py: --loss aimv2_ar 分支实现 causal ViT→next-patch pixel_loss(shift-by-1)+text AR cap_loss(cross-attn→causal patches)+total=cap+0.4*pixel, 无InfoNCE). 脚本 run_aimv2_ar.sh 已就绪(smoke→30k→eval). 🚀 **smoke test✅**(30步/9.1s/exit0): steady_img_s=2069.5, loss=7.14→6.66(cap=6.77→6.29,pixel=0.94→0.92), 无坍缩(fused=False). Arm B params~203.7M(trunk126.8M+ARdec76.2M+pred0.66M) vs Arm A~127.4M(+67M). 🚀 **30k full run START**@07:58: step100/30000, loss=5.94(cap=5.63,pixel=0.76), ~2185 img/s, 8GPU 22.5GB/卡 48-85%util. 30k ETA~2.1h(~10:00), <3h✅. 脚本自动: 30k→save-every 10000(3ckpts)→IN-1k eval(r8_eval_in1k.py). ⚠️ git fetch FAILED(Network unreachable), repo synced(HEAD=origin/main), push将重试. 📦 体积：TASK=31.9KB / MEMORY=17.2KB（均≤32KB✅, 无需归档）.
- [08:10] **🔴 ④ Arm B 坍缩@step600 + 🟢 hybrid 追加实验 RUNNING**: 🔴 **Arm B (pure AR 无 InfoNCE) 坍缩**: C1=0.8649@300→0.9731@600, fused=True, loss在降(cap 6.77→5.08, pixel~0.73, C4=OK)但特征坍缩. 预注册判据命中"AR无对比项坍缩". **DDP死锁bug**: rank0 fuse→break, 其他rank仍在forward→NCCL hang(216s+), 已kill. **bug修复**: r9_train.py 加 `dist.broadcast(fused_flag, src=0)` 让所有rank同步退出. **关键对比**: R11-H(双向+无InfoNCE)C1=0.43✅不坍缩 vs Arm B(因果+无InfoNCE)C1=0.97🔴坍缩 → **causal比bidirectional更易坍缩**. 🟢 **Arm B-hybrid (AR+InfoNCE) RUNNING@08:13**: 代码改动 r9_train.py aimv2_ar 分支新增 `--contrast-weight` 支持(用causal pooled算InfoNCE). 新脚本 run_aimv2_ar_hybrid.sh(`--contrast-weight 1.0 --c2-collapse-guard 1`). smoke✅(30步, contrast=6.10, exit0). **step300探针: C1=0.2480(健康!), C2_gap=+0.096, C4=OK, contrast=5.10(cap=5.04,pixel=0.73)**. 4臂对比表已写入EXPERIMENTS_VISION.md. 30k ETA~10:45. 📦 体积：TASK=31.9KB / MEMORY=~18KB（均≤32KB✅）.
- [00:01] **③ weight-ratio arm2巡检#2**: PID 3214830健康(ppid=1, etimes~4490s~75min). **arm 2/4 cw1_plw0p5(contrast=1,patch=0.5) 运行中** step 18450/30000 ~61.5%: loss~3.1-3.8, contrast~2.9-3.7, patch_mse~0.28-0.36, C1 probes: 0.3755@17700→0.4043@18000→0.3934@18300(无坍缩, C2_gap~+0.11, C4=OK). step10k ckpt✅(vision_step10000.pt, 510MB, saved 23:25). img/s 2000-5100(NFS波动, ms/iter 100-248), 8GPU 16.5GB/卡, util 44-77%. arm2 remaining ~11550步 ETA~00:47, 2 arms remaining(0.5:1→2:1), all+eval ETA~04:30-05:15. ✅ git synced(fetch✅with proxy, HEAD=origin/main=dd8874ad, 0新vision提交, 无新运维指令). 训练健康, 无需干预. 📦 体积：TASK=31.2KB / MEMORY=30.5KB（均≤32KB✅, 无需归档）.
- [09:05] **④ Arm B-hybrid 巡检#1 + mask-ratio报告验证 + TASK归档（CPU-only, 不打断训练）**: 🟢 **Arm B-hybrid RUNNING step 9350/30000 ~31%**: PID 2382170健康(ppid=1, 8 ranks alive). C1 probes: 0.4863@8100→0.4796@8400→0.5464@8700→0.5089@9000→0.4287@9300. **C1 振荡 0.43–0.55, 高于 Arm A 基线~0.33 但 C4=OK C2_gap~+0.045 无坍缩** — causal+InfoNCE 的对比对齐度比 bidirectional+InfoNCE 更强, 但仍稳定. loss~10.7(contrast~5.78 cap~4.5 pixel~0.87, 降中). img/s~2330(ms/iter~215), 8GPU 22-45GB/卡 64-100%util. step10k ckpt 即将落盘(save-every 10000). ETA~09:45(剩~20650步~1.3h). ✅ **mask-ratio报告验证**: report_vision_mask_ratio.html 34.3KB, 8节+2SVG, commit ee9db3ca, 已在origin/main — 运维指令2026-10-07③已交付. ✅ **TASK.md归档**: 2个已闭合块(2026-10-07③+②)原文搬入ARCHIVE_OPERATOR_VISION.md+留指针, 34872→31766B(≤32KB✅). ✅ git fetch✅with proxy, repo synced(HEAD=origin/main). 无新运维指令(2026-10-08全线总结报告块=等hybrid完成后再写). 📦 体积：TASK=31.8KB / MEMORY=~19KB（均≤32KB✅, 归档~3KB→ARCHIVE）.
- [09:44] **④ Arm B-hybrid 巡检#2 + TASK.md归档(lp协议块) + 论文数据准备（CPU-only, 不打断训练）**: 🟢 **Arm B-hybrid RUNNING step 19200/30000 ~64%**: C1 probes: 0.4076@18000→0.4021@18600→0.4993@18900→0.5087@19200, 振荡0.38-0.57, C4=OK C2_gap~+0.05 无坍缩. loss~10.3(contrast~5.56 cap~3.6-4.7 pixel~0.81, 降中), ~2300 img/s. step10k ckpt✅(vision_step10000.pt 814MB). step20k ckpt即将落盘. ETA~10:24 + IN-1k eval ~60-80min. ✅ **TASK.md归档**: lp协议块(2026-10-06, 已闭合: report_vision_lp_protocol.html已交付21.2KB)原文搬入ARCHIVE_OPERATOR_VISION.md+留1行指针, 34435→30325B(≤32KB✅). ✅ **论文数据准备**: 已读6_vision_encoder.tex(183行)结构+EXPERIMENTS_VISION.md关键段. 已识别需补充论文内容: ①mask-ratio消融(倒U形0.6最优) ②weight-ratio消融(无翻盘,patch-heavy更宽容) ③InfoNCE防AR坍缩(④待完成) ④R13官方OV2 79.81% ⑤更新结论段. ✅ git fetch✅with proxy, repo synced. 📦 体积：TASK=30.3KB / MEMORY=~20KB（均≤32KB✅, 归档~4KB→ARCHIVE）.
- [01:39] **③ weight-ratio arm2✅DONE + arm3巡检#1**: ✅ **arm2 cw1_plw0p5(1:0.5) DONE@00:48**: step30k, total=7383s, steady_img_s=2443.8, final_loss=3.5013, C1_final=0.3517, C1_peak=0.4176@19200, C2_gap=+0.1131, C4=OK(无坍缩), 4ckpts✅. arm2结果已写入EXPERIMENTS_VISION.md. 🚀 **arm3 cw0p5_plw1(0.5:1) RUNNING**: PID 3214830健康(ppid=1,~2.9h), step~11650/30k~39%, C1_peak=0.4304@2100(早现), C1_latest=0.2924@11700(下降趋势但C4=OK), C2_gap~+0.133, loss~1.7-1.8, img/s~2200-2700, 8GPU 16.5GB/卡 55-67%util, step10k ckpt✅. arm3 ETA~02:40, 1 arm remaining(2:1), all+eval ETA~05:10. ⚠️ **git fetch FAILED: Network unreachable(github.com:443)** — HEAD=origin/main=1a36624d(synced), push将重试. 📦 体积：TASK=31.2KB / MEMORY=31.0KB（均≤32KB✅, 无需归档）.

## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
