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
- 日志 `/tmp/baize_s1_01.log`（在 10.239.2.29）；torchrun master PID 825166。
- ETA ~28min；完成后回收 loss@5000 / tok/s → PHASE=s2。

## 关键笔记
- seq_length=**4094**（任务固定口径，非 4096）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段（5000 步口径 500）；stable 段 = train_iters - warmup - decay 自动。
- 数据：`data/ultrafineweb_l3_qa.bin/.idx`（200k docs / 164.75M token，int32）；S5-01 需补切 ≥700M（用 `mamba2_hybrid_2b/preprocess_data.py`）。
- 环境：`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；train.sh 已内置。

## GPU / 进程
- 主训练节点 10.239.2.29（8×H100，GPU0~7，本会话全空）。
- S1-01 占用 8 卡（~32GB/卡）。只杀本项目残留（pgrep pretrain_launcher/torchrun），不杀他人进程。

## 操作流水
| 时间 | 步骤 | 记录 |
|------|------|------|
| 2026-09-30 | init | ✅ 读 BAIZE_PRETRAIN_2B_TASK.md（新任务，无 MEMORY_PRETRAIN_2B.md），初始化本记忆 |
| 2026-09-30 | s0 | ✅ launcher/recipe/train.sh 扩 WSD+cosine 调度族 + seq4094 + 8 卡 GBS8 参数化；minicpm5 补穿透；8 卡冒烟 30 步实测 ~330ms/iter ≈99K tok/s、WSD 调度验证通过、ckpt 保存 ✅ |
| 2026-09-30 | s1 | ✅ 启动 S1-01（lr3e-4/WSD/5000 步）8 卡后台训练，WAITING=1 |