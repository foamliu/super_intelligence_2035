# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | ✅ **② mask-ratio 消融 ALL DONE**（5 arms 09:52→19:42, IN-1k eval 20 ckpts done 20:06）. **结果已写入 EXPERIMENTS_VISION.md**: 0.6 最优(lp=13.49%), 倒U形, 0.3/0.75 在±1.5pp噪声带内, 0.5/0.9 显著更差. 🚀 **③ weight-ratio 消融运行中**（PID 187262, arm cw1_plw2 step~550/30k, 4 arms total, ETA ~04:00+eval）. ✅ lp 协议 A/B 桥接完成(Δlp~+10pp). ✅ R12b 训练+eval 完成(lp_max=18.81%). ✅ 论文 §6 改写完成. ✅ AIMv2 提速归因完成. ✅ 官方 AIMv2 范式方案已批准+6点修订已落实 |
| WAITING | 1（🚀 **③ weight-ratio 消融运行中** PID 187262, arm cw1_plw2(contrast=1,patch=2) step~550/30k, ~2857-5160 img/s, loss~5.4, 8 GPU 16.5GB/卡 65-80%util. 4 arms: (1:2)→(1:0.5)→(0.5:1)→(2:1), ~7000s/arm, ETA all+eval ~04:30. ✅ **② mask-ratio 消融 ALL DONE**: 0.6 最优(lp=13.49%@30k), 0.3(12.69%,Δ-0.80), 0.5(11.91%,Δ-1.58), 0.75(12.49%,Δ-1.00), 0.9(11.53%,Δ-1.96). **完成后 = ④ 官方 AIMv2 AR 范式(方案+6点修订已就绪)**）|
| ERROR_COUNT | 5（① R9 w512 首跑 crash：损坏 jpg → data.py 修复 ② 续跑首试 crash：r9_train.py `log()` → 改 `print()` 修复 ③ 8-GPU 并行 eval NFS 争用卡死 → 改 4-GPU r12_single_eval.sh ④ lp bridge crash 缺 `import T` → line 39 加 import ⑤ lp bridge crash CUDA OOM → `extract_features_streaming` 加 `torch.no_grad()` + `linear_probe_mainstream` 加 `Xtr.to(device)`） |
| BUDGET_USED | R2–R12 累计 ≈215 GPU·h + 归因实测 ~0.5 GPU·h + R12b 训练完成（~106.4 GPU·h）+ R12b eval（~0.5 GPU·h）+ lp bridge 完成（~5.8 GPU·h）+ mask-ratio 消融完成（~9.8h×8卡≈78.4 GPU·h）+ mask-ratio IN-1k eval（~0.5 GPU·h）+ weight-ratio 消融进行中（~2h×8卡≈16 GPU·h so far） |
| 更新 | **2026-10-07 20:12（✅ ② mask-ratio 消融 ALL DONE + IN-1k eval done → 结果写入 EXPERIMENTS_VISION.md → 🚀 ③ weight-ratio 消融已开跑）**: 5 arms 09:52→19:42 全部 exit 0, IN-1k eval 20 ckpts done 20:06. **lp@30k: 0.3=12.69%, 0.5=11.91%, 0.6=13.49%(best), 0.75=12.49%, 0.9=11.53%**. 倒U形: 0.6 最优. 0.3/0.75 在±1.5pp噪声带内, 0.5/0.9 显著更差. C1 vs lp 分歧: 0.75 C1 peak(0.4458)最高但 final lp<0.6. R11-L arm6-A 复现=13.49% vs 原12.08%(Δ+1.41pp, 在噪声带内). 结果已写入 EXPERIMENTS_VISION.md(新增 R12b + mask-ratio 两节). 🚀 ③ weight-ratio 消融已开跑(PID 187262, arm cw1_plw2 step~550/30k, 4 arms: (1:2)/(1:0.5)/(0.5:1)/(2:1), ETA all+eval ~04:30). ✅ git synced(fetch✅with proxy, HEAD=origin/main=42ffb925). disk: /nas_train 85% /nas_inference 71% OK. 📦 体积：TASK=29.5KB / MEMORY=~29KB（均≤32KB✅, 归档4条巡检#1-4→daily-1007）· *[更早见 daily-memories-vision/2026-10-07.md]* |
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

> 📦 15 条 R12b 巡检流水(10-06 12:33–23:57)已归档 → daily-memories-vision/2026-10-06.md（2026-10-07 13:00 滚动）
- [00:33] **R12b 心跳巡检#17（CPU-only, 不打断 R12b）**：step~241700/272000 ~88.9%, loss~1.4–1.6 (contrast~1.3–1.5, patch_mse~0.14), C4=OK (probe@241500: C1=0.4895/C2_diag=0.1641/C2_off=0.0416/C2_gap=+0.1225/loss_ema=1.5195). 24 ckpts(step10k–240k, latest 240000@00:26, ~510MB each). **吞吐已恢复至稳态**: img/s~5300 (ms/iter~97, vs 稳态~93), GPU util 28–100%, mem 16.5GB each. 剩余~30.3k 步, ETA~Oct7 01:22(~49min, 按~5300 img/s). watcher PID 3926100 健康(子进程 sleep 300 PID 2846208). GPIC 下载 4608/8000 tar(~57.6%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main=049231d1, last vision ops=ff48cfa6). ✅ **再次核验所有排队项脚本就绪**: lp bridge(`bash -n`✅) + mask-ratio ablation(`bash -n`✅) + weight-ratio ablation(`bash -n`✅) + AIMv2 plan 6 点修订(grep 核验: ①AR≠MAE ②cross-attend causal ③handicap ④smoke test ⑤缩宽度 ⑥中间态, 全部✅). 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=26KB（无归档）.
- [01:06] **R12b 心跳巡检#18（CPU-only, 不打断 R12b）**：step~252800/272000 ~92.9%, loss~1.5-2.1 (contrast~1.3-2.0, patch_mse~0.13-0.17), C4=OK (probe@252600: C1=0.4666/C2_diag=0.1503/C2_off=0.0271/C2_gap=+0.1232/loss_ema=1.8758). 25 ckpts(step10k–250k, latest 250000@00:57, ~510MB each). **NFS吞吐dip持续**: img/s~2600 (ms/iter~195, vs 稳态~93), GPU util 54-85%, mem 16.5GB each. 剩余~19.2k 步, ETA~Oct7 02:09(~63min, 按~2600 img/s). watcher PID 3926100 健康(etimes~7.1h). GPIC 下载 4633/8000 tar(~57.9%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main=4865a566, last vision ops=6c40f1c6). 所有排队项 prep 已完成+核验, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=31KB / MEMORY=27KB（无归档）.
- [01:47] **R12b 心跳巡检#19（CPU-only, 不打断 R12b）**：step~264800/272000 ~97.4%, loss~1.5-2.0 (contrast~1.3-2.0, patch_mse~0.13-0.16), C4=OK (probe@264600: C1=0.4566/C2_diag=0.1555/C2_off=0.0258/C2_gap=+0.1297/loss_ema=1.6851). 26 ckpts(step10k–260k, latest 260000@01:36, ~510MB each). **NFS吞吐dip持续**: img/s~2500 (ms/iter~200, vs 稳态~93), GPU util 66-80%, mem 16.5GB each. 剩余~7.2k 步, ETA~Oct7 02:11(~24min, 按~2500 img/s). watcher PID 3926100 健康(latest 01:46 step 264050). GPIC 下载 4663/8000 tar(~58.3%). disk: /nas_train 84%(34T avail) /nas_inference 69%(15T avail) OK. 无新运维指令(git fetch✅ with proxy, HEAD=origin/main=55bb94f9 同步). 所有排队项 prep 已完成+核验, 仅待 R12b 训完. 训练健康, 无需干预. 📦 体积：TASK=32KB / MEMORY=27KB（无归档）.
- [02:23] **R12b 训练完成 + auto-eval 进行中**：272k 步全部跑完(12:54–02:14, ~13.3h), 28 ckpts(step10k–270k+final vision.pt, 510MB each)已落盘. built-in r8_eval_in1k.py 正在逐 ckpt 评估(sequential, 1 GPU): 已出 step10k(lp=11.77%/zs=4.20%) + step20k(lp=12.44%/zs=4.98%), 均显著高于 R11-G 同期(step10k~7.4%) — 大数据集(69.7M vs 18.5M)起效. eval 进度~3/28, ETA~03:00. watcher PID 3926100 健康(等待 built-in eval 完成后自动跑 r12b_scaling.py). ✅ 资源核查: IN-1k official val=50k/14 parquet(labels 0-999) ✅ + full train=1.28M/294 parquet ✅ → lp 协议 B 组可用全量. ✅ R13 奇偶控制已验证(r13_eval_official.py L10 → 79.81% 用 Protocol A → 协议不压低强模型). run_lp_protocol_bridge.sh(bash -n ✅) 配置: R12b final+R12 1epoch+R11G AIMv2 ckpts. 无新运维指令. GPIC 下载~58%. 下一步: eval 完成 → ① lp 协议 A/B → ② mask-ratio → ③ weight-ratio → ④ 官方 AIMv2. 📦 体积：TASK=32KB / MEMORY=29KB（无归档）.
- [03:07] **R12b eval 完成 + lp 协议 A/B 桥接启动**：R12b 28/28 ckpts eval 全部完成(02:45 ALL DONE). **lp_max=18.81%(final vision.pt, 139.3M token)**. Scaling: R²=0.8867, power law `0.4781-1.1757·N^(-0.0749)`, 渐近47.8%. ⚠️ **关键发现**: R12b(69.7M data, 2ep, 139M token) lp_max=18.81% **< R11-G(18.5M, 1ep, 55.3M) 19.76%** → 更多 unique 数据(GPIC 短 caption 占76%)不改善 lp; R12 3-epoch(58.8M, 3ep, 174M) 20.32% 仍是最高. 归因: GPIC 短 caption 稀释信号 + 2ep<3ep. R12b 结果已写入 `EXPERIMENTS_VISION_ROUND12.md §2`. ✅ lp 协议 A/B 桥接已启动: PID 1499158, GPU0, 3 ckpts(R12b final+R12 1ep+R11G AIMv2) × Protocol A(BaiZe)+B(SGD+cosine 90ep bs1024 IN-norm full-train 1.28M) × 3 repeats. 日志 `/tmp/lp_bridge_full.log`. 无新运维指令(git fetch✅, origin/main=4ede00bc). GPIC 下载~58%. 8 GPU 全空闲(bridge 仅用 GPU0). 📦 体积：TASK=32KB / MEMORY=29KB（无归档）.
- [03:20] **lp bridge bug 修复 + 重启**：首次启动的 bridge (PID 1499158) crash — `NameError: name 'T' is not defined` in `lp_protocol_bridge.py:57 get_transform()` → 缺 `import torchvision.transforms as T`. **已修复**（line 39 加 import）+ py_compile ✅ + `get_transform('clip'/'imagenet')` 均返回正确 Compose ✅. **重启** PID 2227716, GPU0, 同配置(3 ckpts × both protocols × full-train 1.28M × 3 repeats). 正在加载 Protocol A 数据(NFS I/O, ETA~03:30 开始 GPU 编码). 📦 体积：TASK=32KB / MEMORY=30KB（无归档）.
- [06:35] **lp bridge 巡检#2**：PID 807654 健康(etimes~9633s~2.7h, GPU0 2.4GB 0%util=数据加载阶段). **ckpt1(R12b final) ✅全部完成**: Protocol A=18.79%, Protocol B seed0=28.88%/seed1=28.82%/seed2=28.81% → **B=28.84±0.03%, Δlp=+10.05pp** ⇒ BaiZe 协议系统性低估 lp ~10pp(3 seed σ=0.03pp, 极稳定). **ckpt2(R12 1ep) 进行中**: Protocol A=20.22%, Protocol B streaming 51/294 parquet(NFS I/O bound). ckpt3(R11G AIMv2) 待跑. ETA~10:00-11:00(ckpt1耗时~2h, 2 ckpt剩余~3-4h). GPIC 4845/8000 tar(~60.6%). GPUs 1-7 空闲(②③④需8GPU⇒须等bridge). git synced(7cfd9d26, fetch✅ with proxy, 无新运维指令). 📦 体积：TASK=32098B(31.3KB) / MEMORY=~32KB（均≤32KB, 无归档）.
- [07:12] **lp bridge 巡检#3（用户手动唤醒, 与 loop cline PID 2504046 并发）**：PID 807654 健康(etimes~11838s~3.3h, 88%CPU, GPU0 2.4GB/39%util). ckpt1(R12b final)✅全完成: A=18.79%, B=28.84±0.03%(3seed: 28.88/28.82/28.81), Δlp=+10.05pp⭐. ckpt2(R12 1ep)进行中: A=20.22%✅, B streaming 151/294 files~51%(658058/1281167 imgs, NFS I/O bound). ckpt3(R11G AIMv2)待跑. ETA~10:00-11:00. GPUs 1-7全空闲(②mask-ratio/③weight-ratio/④AIMv2 AR 需8GPU⇒须等bridge完成). GPIC下载~60.6%(上次实测06:35, 本次NFS慢find超时未更新). git synced(fetch✅with proxy, HEAD=origin/main, 0新提交, 无新运维指令). 📦 体积：TASK=32098B(31.3KB)/MEMORY=30594B→+流水≈30.3KB(归档2条旧流水, ≤32KB✅).
- [07:52] **📋 昨夜工作汇报 HTML 已产出**（用户直令 2026-10-07）：`doc/BaiZe-ISEDA2027/report_10_07_vision_overnight.html`（自包含, 27.7KB, 内联 SVG 管线图, 零外部依赖, 外链检查✅空, @import✅无, wc -c✅≤200KB）。窗口 2026-10-06 22:00→10-07 07:52(数据截止)。8 章节: HERO/TL;DR/KPI/时间线/证据(含 2 次 bridge crash 原文)/卡点/今晨现状/commit 列表(17 条)。核心结论: R12b 训练+eval完成(lp_max=18.81%) + lp 协议 A/B ckpt1 Δlp=+10.05pp + AIMv2 AR 代码 smoke test 通过. 📦 体积：TASK≈31.3KB / MEMORY≈30.8KB（≤32KB✅, 无归档）.
- [11:46] **② mask-ratio 消融巡检#3**：PID 1752298 健康(etimes~6875s~1h54m). arm 0.3 **step~29400/30000 ~98%** 即将完成→arm 0.5 自动启动: loss~2.9-3.5, contrast~2.7-3.3, patch_mse~0.22-0.24, C1=0.3441(probe@29400, 无坍缩, C2_gap=+0.12, C4=OK). 10k+20k ckpt✅(各510MB). img/s 2000-2900(NFS波动), ms/iter 178-250. 8 GPU 16.4GB/卡, util 100%(GPU5 偶发 0%=数据加载). arm 0.3 ETA ~11:50, 全 5 arms+eval ETA ~17:00-18:00. pretrain GPU1-7 已归还(09:44). pretrain 10:30 申请1卡但 8 GPU 全被 vision 占用⇒按优先序 vision>pretrain推理. git synced(fetch✅with proxy, 0新提交). 📦 体积：TASK=29.5KB / MEMORY=30.9KB（≤32KB✅）.
- [12:22] **② mask-ratio 消融巡检#4**：PID 1752298 健康(etimes~9002s~2h30m). **arm 0.3 ✅DONE**(09:52→11:51, 7119s, steady 2375 img/s, final C1=0.3495, 3 ckpts✅: step10k/20k/30k+vision.pt). **arm 0.5 运行中** step~8450/30000 ~28%: loss~3.9-4.2, contrast~3.6-3.9, patch_mse~0.29, C1=0.3357(probe@8400, 无坍缩, C2_gap=+0.114, C4=OK). img/s 2200-4800(NFS波动大), ms/iter 107-230. 8 GPU 16.4GB/卡, util 6-100%. 3 arms remaining(0.6/0.75/0.9), ETA all+eval ~19:00-20:00. 归档5条旧流水(10-06 12:33–18:10)→daily-1006. git synced(fetch✅with proxy, HEAD=origin/main, 0新提交, 无新运维指令). 📦 体积：TASK=29.5KB / MEMORY=30.4KB→+流水≈30.7KB（归档5条→daily-1006, ≤32KB✅）.




- [13:00] **② mask-ratio 消融巡检#5**：PID 1752298 健康(etimes~11316s~3h9m). **arm 0.3 ✅DONE**(09:52→11:51, 7119s, steady 2375 img/s, final C1=0.3495, 3ckpts✅+vision.pt). **arm 0.5 运行中** step~17800/30000 ~59%: loss~3.7, contrast~3.5, patch_mse~0.25, C1=0.3409(probe@17700, 无坍缩, C2_gap=+0.119, C4=OK). ⚡ **img/s回升至~5000**(ms/iter~100, vs 前段~200-230 NFS慢). step10k ckpt✅已落盘(510MB). 8 GPU 16.4GB/卡, 7/8 GPU 100%util(GPU0 0%=数据加载). 3 arms remaining(0.6/0.75/0.9), arm0.5剩余~12200步 ETA~20-40min, all+eval ETA~17:00-19:00. git synced(fetch✅with proxy, HEAD=origin/main, 0新提交, 无新运维指令). 归档10条R12b旧流水(10-06 18:41-23:57)→daily-1006. 📦 体积：TASK=29.5KB / MEMORY=~22KB（归档10条→daily-1006, ≤32KB✅）.
- [13:39] **② mask-ratio 消融巡检#6**：PID 1752298 健康(etimes~13564s~3h47m). **arm 0.3 ✅DONE**(09:52→11:51, 7119s, C1=0.3495, 3ckpts✅+vision.pt). **arm 0.5 即将完成** step~27550/30000 ~92%: loss~3.0-3.2, contrast~2.8-3.0, patch_mse~0.22-0.23, C1=0.3705@27300(无坍缩, C2_gap=+0.113, C4=OK). img/s 2000-2600(NFS波动), ms/iter 200-250. step10k+20k ckpt✅(各510MB). 8 GPU 16.4GB/卡, util 0-100%(GPU3偶发0%=数据加载). arm0.5剩余~2450步 ETA~13:50, 3 arms remaining(0.6/0.75/0.9), all+eval ETA~19:30-20:30. ✅ 运维指令2026-10-07②(GPU分配)已resolve: pretrain 09:44归还GPU1-7, vision 09:52占8卡开跑mask-ratio. ✅ ⓪归档已完成(昨夜HTML块已在ARCHIVE, 指针在TASK). git synced(fetch✅with proxy, HEAD=origin/main, 0新提交, 无新运维指令). 📦 体积：TASK=29.5KB / MEMORY=~22KB（均≤32KB✅, 无归档）.
- [16:35] **② mask-ratio 消融巡检#11**：PID 1752298 健康(etimes~24198s~6.7h, ppid=1). **arm 0.3 ✅DONE**(09:52→11:51, 7119s, C1=0.3495, 3ckpts✅+vision.pt). **arm 0.5 ✅DONE**(11:51→13:49, 7062s, C1=0.3756, 3ckpts✅+vision.pt). **arm 0.6 ✅DONE**(13:49→15:45, 6910s, final C1=0.3810@30000, C2_gap=+0.116, C4=OK, 3ckpts✅+vision.pt). **arm 0.75 运行中** step~12850/30000 ~43%: loss~2.8-3.6, contrast~2.6-3.4, patch_mse~0.20-0.28, C1 probes: 0.3442@11400→0.3588@11700→0.3701@12000→0.4241@12300→0.4073@12600 (无坍缩, C2_gap~+0.11-0.12, C4=OK). ⚡ **C1峰值0.4241@12300已超前arm0.6同期(0.4023@6900)**. step10k ckpt✅(16:24, 510MB). img/s 2200-5400(NFS波动), ms/iter 95-230. 8 GPU 16.5GB/卡, util 36-96%(NFS bound). 1 arm remaining(0.9), arm0.75剩余~17150步 ETA~17:24, arm0.9 ETA~19:21, all+eval ETA~21:00(脚本自动 eval 20 ckpts). ⚡ **C1趋势: 0.3→0.3495, 0.5→0.3756, 0.6→0.3810(随mask-ratio递增, 全臂无坍缩)**. ✅ git synced(fetch✅with proxy, HEAD=origin/main=aeccb047, 3新提交=pretrain+supervisor(非vision), 无新运维指令). disk: /nas_train 85%(33T) /nas_inference 71%(14T) OK. 训练健康, 无需干预. 📦 体积：TASK=29.5KB / MEMORY=27.8KB（均≤32KB✅, 无归档）.
- [17:10] **② mask-ratio 消融巡检#12**：PID 1752298 健康(etimes~26270s~7.3h, ppid=1). **arm 0.3 ✅DONE**(09:52→11:51, 7119s, C1=0.3495). **arm 0.5 ✅DONE**(11:51→13:49, 7062s, C1=0.3756). **arm 0.6 ✅DONE**(13:49→15:45, 6910s, final C1=0.3810@30000, C2_gap=+0.116, C4=OK). **arm 0.75 运行中** step~21500/30000 ~72%: loss~3.0-3.8, contrast~2.7-3.6, patch_mse~0.20-0.26, C1 probes: 0.4023@19200→0.4206@19500→**0.4458@19800(全臂峰值!)**→0.4068@20100→0.3942@20400→0.3888@20700→0.3919@21000→0.3576@21300 (无坍缩, C2_gap~+0.11, C4=OK). step10k+20k ckpt✅(各510MB). img/s 2000-5400(NFS波动), ms/iter 170-250. 8 GPU 16.5GB/卡, util 63-91%. 1 arm remaining(0.9), arm0.75 ETA~17:40, arm0.9 ETA~19:25, all+eval ETA~20:30(脚本自动 eval 20 ckpts). ⚡ **C1峰值0.4458@19800为全5臂最高(超前arm0.6 final 0.3810), 但步21k后略回落~0.36**. ⚡ **C1趋势: 0.3→0.3495, 0.5→0.3756, 0.6→0.3810, 0.75 peak→0.4458(随mask-ratio递增, 全臂无坍缩)**. ✅ git synced(fetch✅with proxy, HEAD=origin/main=4dfb6504, 0新vision提交, 无新运维指令). disk: /nas_train 85%(33T) /nas_inference 71%(14T) OK. 训练健康, 无需干预. 📦 体积：TASK=29.5KB / MEMORY=29.3KB（均≤32KB✅, 无归档）.
- [18:18] **② mask-ratio 消融巡检#13**：PID 1752298 健康(etimes~30401s~8.4h, ppid=1). **arm 0.3 ✅DONE**(09:52→11:51, 7119s, C1=0.3495). **arm 0.5 ✅DONE**(11:51→13:49, 7062s, C1=0.3756). **arm 0.6 ✅DONE**(13:49→15:45, 6910s, final C1=0.3810@30000, C2_gap=+0.116, C4=OK). **arm 0.75 ✅DONE**(15:45→17:42, 6992s, final C1=0.3736@30000, peak C1=0.4458@19800, C2_gap=+0.1162, C4=OK, 3ckpts✅+vision.pt). **arm 0.9 运行中** step~9600/30000 ~32%: loss~3.6-4.0, contrast~3.3-3.7, patch_mse~0.25-0.29, C1 probes: 0.3779@7800→0.3766@8100→0.3586@8400→0.3601@8700→0.3572@9000→0.3793@9600 (无坍缩, C2_gap~+0.11, C4=OK). img/s 2200-2800(NFS波动), ms/iter~210. 8 GPU 16.5GB/卡, util 68-100%. arm0.9 ETA~19:33, all+eval ETA~20:30(脚本自动 eval 20 ckpts). ⚡ **C1趋势(final@30k): 0.3→0.3495, 0.5→0.3756, 0.6→0.3810(best final), 0.75→0.3736(peak 0.4458@19800 but declined)**. ⚠️ arm0.75峰值超前(0.4458)但final(0.3736)回落<arm0.6(0.3810) → 高mask-ratio可能峰值早现但终态不稳定. ✅ git synced(fetch✅with proxy, HEAD=origin/main=00eee482, 0新vision提交, 无新运维指令). disk: /nas_train 85%(33T) /nas_inference 71%(14T) OK. 📦 体积：TASK=29.5KB / MEMORY=30.7KB（均≤32KB✅, 无归档）.
- [18:58] **② mask-ratio 消融巡检#14**：PID 1752298 健康(etimes~32745s~9.1h, ppid=1). **arm 0.3 ✅DONE**(09:52→11:51, 7119s, C1=0.3495). **arm 0.5 ✅DONE**(11:51→13:49, 7062s, C1=0.3756). **arm 0.6 ✅DONE**(13:49→15:45, 6910s, final C1=0.3810@30000, C2_gap=+0.116, C4=OK). **arm 0.75 ✅DONE**(15:45→17:42, 6992s, final C1=0.3736@30000, peak 0.4458@19800, C2_gap=+0.1162, C4=OK). **arm 0.9 运行中** step~19250/30000 ~64%: loss~3.5-3.9, contrast~3.2-3.5, patch_mse~0.23-0.26, C1 probes: 0.3265@18000→0.3439@18300→0.3529@18600→0.3380@18900→0.3876@19200 (无坍缩, C2_gap~+0.11, C4=OK). step10k ckpt✅(18:22, 510MB). img/s 1900-5400(NFS波动, 近期回升5000+), ms/iter 95-276. 8 GPU 16.5GB/卡, util 0-100%. arm0.9 ETA~19:35, all+eval ETA~20:30(脚本自动 eval 20 ckpts). ⚡ **C1趋势(final@30k): 0.3→0.3495, 0.5→0.3756, 0.6→0.3810(best final), 0.75→0.3736(peak 0.4458@19800 but declined)**. arm0.9 at 64% C1~0.33-0.39(与0.75同期接近, 需等final). ✅ git synced(fetch✅with proxy, HEAD=origin/main, 0新vision提交, 无新运维指令). disk: /nas_train 85%(33T) /nas_inference 71%(14T) OK. 📦 体积：TASK=29.5KB / MEMORY=~27KB（归档4条#7-#10→daily-1007, ≤32KB✅）.
- [20:12] **✅ ② mask-ratio 消融 ALL DONE + IN-1k eval done → 🚀 ③ weight-ratio 消融已开跑**: 5 arms 09:52→19:42 全部 exit 0. **arm 0.9 ✅DONE**(17:42→19:42, final C1=0.3468@30k, peak 0.4097, 7138s, 无坍缩 C4=OK, 3ckpts✅+vision.pt). IN-1k frozen-trunk lp eval 20 ckpts done 20:06(~25min: 7min load+96s/ckpt×20). **lp@30k: 0.3=12.69%(Δ-0.80), 0.5=11.91%(Δ-1.58⚠️), 0.6=13.49%(BASELINE/best), 0.75=12.49%(Δ-1.00), 0.9=11.53%(Δ-1.96⚠️)**. ⚡ **倒U形: 0.6 最优**. 0.3/0.75 在±1.5pp噪声带内(不敏感), 0.5/0.9 显著更差. C1_final: 0.6=0.3810(best), 0.75=0.3736(peak 0.4458 but declined). R11-L arm6-A 复现=13.49% vs 原12.08%(Δ+1.41pp, 噪声带内→可复现). ✅ **结果已写入 EXPERIMENTS_VISION.md**(新增 R12b 全量数据 + mask-ratio 消融两节, 含完整表+6条科学结论). 🚀 **③ weight-ratio 消融已开跑**(PID 187262, nohup, arm cw1_plw2=contrast1:patch2 step~550/30k, loss~5.4, ~2857-5160 img/s, 8 GPU 16.5GB/卡 65-80%util, ETA all+eval ~04:30). 4 arms: (1:2)→(1:0.5)→(0.5:1)→(2:1). ✅ git synced(fetch✅with proxy, HEAD=origin/main=42ffb925, 0新vision提交, 无新运维指令). 📦 体积：TASK=29.5KB / MEMORY=~27KB（归档4条#lp-bridge+巡检#1-3→daily-1007, ≤32KB✅）.


## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
