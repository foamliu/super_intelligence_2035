# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态

## 当前状态
- STAGE: **运行中**（S0 完成，S1 baseline 已启动 training）
- PHASE: **s1**（S1-01 running）
- WAITING: **1**（S1-01 异步训练 running，5000 步 ≈ 28min）
- ERROR_COUNT: 0
- BUDGET_USED（GPU·小时）: ~0.3（S0 冒烟 8 卡×~2.2min ≈ 0.3；S1-01 训练中未计入）

## S0 结论（launcher 适配 + 8 卡冒烟，2026-09-30 完成 ✅）
- 启动器扩展（`pretrain_launcher.py`）：新增 `--lr-decay-style`（WSD|cosine，默认 WSD）/ `--lr-warmup-iters`（250）/ `--lr-decay-iters`（500，WSD=退火尾段）/ `--min-lr` / `--seq-length`（默认 4094）；`--global-batch-size` 默认 6→**8**；train-iters 可变。
- `mamba2_hybrid_2b/recipe.py`：新增 `_build_optimizer_and_scheduler()`（WSD/cosine 双族，默认 WSD + linear 退火），并把 `seq_length` 穿透进 `model_config()`（**修复 mcore `model.seq_length==dataset.sequence_length` 断言**，seq 4094 必须同时改 provider）。
- `minicpm5_2b/recipe.py`：补 `lr_decay_style` + `seq_length` 穿透（保持共享 launcher 通用，不动其 cosine 行为）。
- `scripts/train.sh`：环境变量参数化（`TRAIN_ITERS/LR/MIN_LR/WARMUP_ITERS/DECAY_ITERS/DECAY_STYLE/SEQ_LENGTH/GBS/EVAL_INTERVAL`），默认 8 卡 / GBS=8 / seq=4094 / WSD warmup250 decay500。
- **冒烟实测（8×H100，TP1/DP8，30 步）**：
  - 稳态 **~330ms/iter**（iter20=336ms / iter30=329ms）→ 吞吐 **~99K tok/s**（8×4094/0.330）。
  - 首 10 步均 12.6s/iter（首步 SSM 编译/CUDA-graph 一次性开销）。
  - loss 11.37(iter10)→8.43(iter20)→**7.90(iter30)**；WSD 调度验证：LR 3e-4(stable)→3e-5(decay 尾)。
  - 总样本 **40243**（seq 4094 对 164.75M token）；5000 步需 40000（8×5000），余 243 样本（~0.6% margin，**偏紧**，S1 需观察是否够）。
  - ckpt 已存 `nemo_experiments/s0_smoke_8gpu/checkpoints/iter_0000030`。
  - ⚠️ 日志打印「参数 3.00B」为 mcore 对 Mamba 计数 bug，真实 **2.220B**（见 EXPERIMENTS_2B.md 关键修正）。
- 预算校准：稳态 330ms → 5000 步 ≈ 27.5min ≈ 3.7 GPU·h/组（任务估算 30min/4.0 GPU·h，吻合）；20000 步 ≈ 1.83h ≈ 14.7 GPU·h。

## S1 baseline（已启动 running）
- S1-01：lr 3e-4 / WSD / 5000 步 / GBS=8 / seq=4094 / mb=1 / TP1/DP8 / warmup=250 / decay=500 / min-lr=3e-5 / seed=1234 / bf16。
- 命令：`ssh 10.239.2.29 'cd $BASE && TRAIN_ITERS=5000 bash scripts/train.sh mamba2 s1_01 29652 8'`
- 日志 `/tmp/baize_s1_01.log`（在 10.239.2.29）；torchrun master PID 825166；8 worker 825236-825243（每卡 ~39GB）。
- **2026-09-30 11:44 快照**：iter 1420/5000，loss **4.09**（自 7.90@30 稳步收敛），~300ms/iter，无 NaN/skip。ETA 完成 ≈ ~12:00（余 ~18min）。单任务健康（nvidia-smi 8 卡各 1 进程）。
- **2026-09-30 11:46 快照**：iter 1950/5000，loss **~3.49**（4.09@1420 → 3.49@1950 收敛正常），~310-420ms/iter（均值~330ms），无 NaN/skip。nvidia-smi 8 卡各 1 进程（~39GB/卡，util 69-100%）。进度 39%，ETA 完成 ≈ ~12:00。单任务健康。
- **2026-09-30 11:48 快照**：iter 2210/5000（44%），loss **~3.38**（3.49@1950 → 3.38@2210 继续收敛），~288-312ms/iter（均值~300ms），无 NaN/skip。consumed samples 17680/40000，数据余量 243 样本足。torchrun master 825166 + 8 worker 825236-825243 均存续，master_port=29652。ETA 完成 ≈ **~12:02**（余 ~14min）。未完成，退出等待下一轮回收 loss@5000/tok/s → 启动 S2 LR 扫描。
- **2026-09-30 11:50 快照**：iter **2510/5000**（50%），loss **~3.29**（3.38@2210 → 3.29@2510 继续收敛），无 NaN/skip。⚠️ **首次发现 GPU 抢占**：同行 vision 任务（`BAIZE_VISION`，openvision2 `S1_openvision2`，6 进程各 ~25GB，PPID 1911560）在 ~11:48 于 **10.239.2.29 GPU0~5** 启动，与本 8 卡 S1-01 抢占 GPU0~5；step time 由 ~310ms 飙升至 **~840ms**（iter2500+，DP=8 all-reduce 以最慢卡为准）。**不杀他人进程**，仅记录。影响：S1-01 ETA 后移、且 S1 的 `tok/s` 基线被污染（后续 S2 比较需在 8 卡独占时重测吞吐）。仍未完成，退出等待回收。
- **2026-09-30 11:53 快照**：iter **2760/5000**（55%），loss **~3.17**（3.29@2510 → 3.17@2760 继续收敛），无 NaN/skip。⚠️ GPU 抢占持续：vision 任务 6 进程仍占 GPU0~5（PID 1912130/33/34/35/37/38），step time 稳定 ~840-870ms/iter（较独占 ~330ms 慢 ~2.6×）。consumed samples 22080/40000，数据余量 243 样本足。torchrun master 825166 + 8 worker 825236-825243 存续，master_port=29652 一致。剩余 2240 步 × ~0.84s ≈ ~31min，ETA ≈ **~12:25**（抢占持续时；若 vision 结束恢复独占则提前 ~12:05）。仍未完成，退出等待回收。
- **2026-09-30 11:57 快照**：iter **3020/5000**（60%），loss **~3.13-3.23**，无 NaN/skip，grad norm ~0.5 健康。⚠️ GPU 抢占持续但 vision 负载波动：step time ~320ms（独占态）与 ~850-970ms（抢占态）抖动。澄清 860xxx~862xxx 为 pt_data_worker 非重复拉练。未完成，退出。
- **2026-09-30 11:59 快照**：iter **3210/5000**（64%），loss **~3.12-3.19**（3.15@3020 → 3.14@3210 收敛趋缓，正常），无 NaN/skip，grad norm ~0.51-0.54 健康。consumed samples 25680/40000，数据余量 243 样本足。⚠️ **vision 任务重启**：原 PID 1912130（6 进程）已被新一批 **8 进程**（PID 2225700-2225707，各 ~24GB）取代，仍占 GPU0~5；GPU0~5 ≈64GB（vision 24GB + 本任务 39GB）、GPU6~7 ≈39GB（本任务独占）。step time 稳定 ~740-950ms（抢占态，均 ~850ms）——较 S0 独占 ~330ms 慢 ~2.6×。剩余 1790 步 × ~0.85s ≈ **~25min**，ETA ≈ **~12:25**。仍未完成，退出等待回收。
- **2026-09-30 12:02 快照**：iter **3400/5000**（68%），loss **~3.07-3.15**（3.14@3210 → 3.14@3400 收敛趋缓，正常），无 NaN/skip，grad norm ~0.49-0.54 健康。consumed samples 27200/40000，数据余量 243 样本足（未耗尽）。⚠️ vision 8 进程（2225700-2225707）仍占 GPU0~5，step time ~780-990ms（抢占态，均 ~850ms）。torchrun master 825166 + 8 worker 825236-825243 存续，master_port=29652 一致，无重复拉练。剩余 1600 步 × ~0.85s ≈ **~23min**，ETA ≈ **~12:25**（vision 持续时）。仍未完成，退出等待回收。
- **2026-09-30 12:04 快照**：iter **3570/5000**（71%），loss **~3.04-3.12**（3.12@3510 → 3.13@3540 附近，收敛趋缓正常），无 NaN/skip，grad norm ~0.49-0.52 健康。consumed samples 28560/40000，数据余量 243 样本足。⚠️ vision 8 进程（2225700-2225707）仍占 GPU0~5，step time 抖动 ~710-900ms（偶现 110TFLOP/s 峰值说明 vision 负载间歇性释放，均 ~820ms）。torchrun master 825166 + 8 worker 825236-825243 存续、master_port=29652 一致，无重复拉练。剩余 1430 步 × ~0.82s ≈ **~19min**，ETA ≈ **~12:23**（vision 持续时）。仍未完成，退出等待回收。
- **2026-09-30 12:09 快照**：iter **4200/5000**（84%），loss **~2.97-3.08**（2.99@3870 → 3.07@4200，收敛趋缓正常），无 NaN/skip，grad norm ~0.48-0.53 健康。consumed samples 33600/40000，数据余量 243 样本足。⚠️ **vision 任务再次重启**：新一批 **6 进程**（PID 3032678/3032690/3032696/3032703/3032713/3032718，~24GB/卡）仍占 GPU0~5；step time 较前回落至 ~480-525ms（均 ~485ms，介于独占 330ms 与抢占 850ms 间，说明 vision 负载部分释放），GPU util ~160 TFLOP/s/GPU。torchrun master 825166 + 8 worker 825236-825243 存续、master_port=29652 一致，无重复拉练。剩余 800 步 × ~0.49s ≈ **~6.5min**，ETA ≈ **~12:16**。仍未完成，退出等待回收。
- 完成后回收 loss@5000 / tok/s → PHASE=s2（LR 扫描 2e-4…1e-3，需 8 卡独占重测 tok/s 避免基线污染）。

## 关键笔记
- seq_length=**4094**（任务固定口径，非 4096）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段（5000 步口径 500）；stable 段 = train_iters - warmup - decay 自动。
- 数据：`data/ultrafineweb_l3_qa.bin/.idx`（200k docs / 164.75M token，int32）；S5-01 需补切 ≥700M（用 `mamba2_hybrid_2b/preprocess_data.py`）。
- 环境：`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；train.sh 已内置。
- 进程识别：单次 8 卡训练 = 1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11 个 `pt_data_worker`（PyTorch dataloader，comm=pt_data_worker）。pgrep 看到多段 PID（825xxx master/worker + 860xxx~862xxx data_worker）是**同一任务**，勿误判为重复拉练。

## GPU / 进程
- 主训练节点 10.239.2.29（8×H100，GPU0~7）。
- ⚠️ **2026-09-30 11:48 起**：同行 vision 任务（openvision2 / S1_openvision2，6 进程各 ~25GB，PPID 1911560，PID 1912130/1912133/1912134/1912135/1912137/1912138）占用 **GPU0~5**，与本项目 S1-01（8 卡）抢占 GPU0~5 → step time ~310→~840ms。**属他人任务，禁止击杀**；需关注其对 S1 吞吐基线与后续 S2~S5 逐点扫描的时间影响（可能拖长墙钟预算）。
- S1-01 占用 8 卡（~39GB/卡，PID 825236-825243，master 825166）。只杀本项目残留（pgrep pretrain_launcher/torchrun），不杀他人进程。

## 操作流水
| 时间 | 步骤 | 记录 |
|------|------|------|
| 2026-09-30 | init | ✅ 读 BAIZE_PRETRAIN_2B_TASK.md（新任务，无 MEMORY_PRETRAIN_2B.md），初始化本记忆 |
| 2026-09-30 | s0 | ✅ launcher/recipe/train.sh 扩 WSD+cosine 调度族 + seq4094 + 8 卡 GBS8 参数化；minicpm5 补穿透；8 卡冒烟 30 步实测 ~330ms/iter ≈99K tok/s、WSD 调度验证通过、ckpt 保存 ✅ |
| 2026-09-30 | s1 | ✅ 启动 S1-01（lr3e-4/WSD/5000 步）8 卡后台训练，WAITING=1 |
| 2026-09-30 | s1 | 🔍 快照：S1-01 iter1420/5000 loss4.09 ~300ms/iter 健康；单任务确认（8 卡各1进程）；未完成，退出等待下一轮回收 |
| 2026-09-30 | s1 | 🔍 快照：S1-01 iter2210/5000 loss3.38 ~300ms/iter 健康无NaN；数据余量足；未完成，退出等待下轮回收 |
 | 2026-09-30 | s1 | ⚠️ 快照：S1-01 iter2510/5000 loss3.29 健康；发现同行 vision 任务抢占 GPU0~5，step time 310→840ms，仅记录不杀他人；退出等待回收 |
| 2026-09-30 | s1 | 🔍 快照：S1-01 iter2760/5000 loss3.17；GPU 抢占持续 step time 840ms（慢2.6×）ETA~12:25；数据余量足无NaN；未完成，退出等待回收 |
| 2026-09-30 | s1 | 🔍 快照：S1-01 iter3020/5000 loss3.15；step time 320~970ms 抖动（vision 负载波动）；澄清 860xxx 段 PID 为 pt_data_worker 非重复拉练；ETA~12:20；退出等待回收 |
| 2026-09-30 | s1 | 🔍 快照：S1-01 iter3400/5000 loss3.14 无NaN；vision 8 进程继续抢占 GPU0~5 step time~850ms；数据余量足；ETA~12:25；退出等待回收 |
| 2026-09-30 | s1 | 🔍 快照：S1-01 iter3570/5000(71%) loss~3.08-3.12 无NaN grad~0.50；vision 8 进程仍占 GPU0~5 step time~710-900ms 抖动；数据余量足；ETA~12:23；退出等待回收 |