# BAIZE_PRETRAIN_2B_TASK.md

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

---

## 任务目标

在**已选定**的 Mamba2-hybrid（2.220B）骨架上，完成受 **24h 墙钟（≈192 GPU·h @ 8 卡）** 预算约束的高置信度超参搜索（S0–S5），最终产出：

1. 一条**胜出配置**（stable LR + 调度族 + 关键轴 + 退火数据混合）
2. 一份**实验记录表**（`EXPERIMENTS_PRETRAIN_2B.md`），含所有配置的 ID / 超参 / 结果 / GPU·h
3. 一条**20000 步长跑收敛曲线**（胜出配置）+ **多 seed 复现**（3 seed，报均值±σ）
4. 一条**可复现训练命令** + 一份 HTML 报告 `BAIZE_PRETRAIN_RESULT.html`

对应论文 `ISEDA2027/4_llm_pretrain.tex` 与计划 `BAIZE_LLM_PRETRAIN_PLAN.html`。

---

## 已定前提（固定，不要更改）

| 项 | 值 |
|:---|:---|
| 架构 | **Mamba2-hybrid**（56 层，Nemotron-H 式顺序混合，**2.220B**）|
| 框架 | NVIDIA/NeMo recipe + Megatron-Core（`NVIDIAMambaHybridModelProvider2B`），torchrun 直驱 |
| **BASE_DIR** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027` |
| provider/recipe | `BASE_DIR/mamba2_hybrid_2b/`（provider.py / recipe.py，已有）|
| tokenizer | DeepSeek-V4.1-Flash，`BASE_DIR/data/tokenizer_eod`（vocab 129281 / pad 129408）|
| 数据（stable 主体）| Ultra-FineWeb-L3 英文 `BASE_DIR/data/ultrafineweb_l3_qa`（`.bin/.idx` 已切 200k docs / 165M token）|
| 环境 | CUDA 12.8 / PyTorch 2.8.0 / Python 3.10；`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230` |
| GPU | 主训练 **`10.239.2.29`（8×H100，GPU0~7）**；辅助 `10.239.2.12`（GPU0~5）|

> 启动器：`BASE_DIR/scripts/train.sh <arch> <name> <master_port> [nproc]`（arch=`mamba2`，nproc 传 **8** 以用满 `10.239.2.29` 全 8 卡），内部调 `pretrain_launcher.py`。**需先扩展 launcher** 支持 `--lr` / `--lr-warmup-iters` / `--lr-decay-iters` / `--lr-decay-style`（WSD|cosine）/ `--min-lr` / `--seq-length=4094`，并把硬编码的 `--global-batch-size 6` / 默认 `nproc 6` / `--train-iters 1000` 改为可按参数传（默认 8 卡：GBS=8、DP=8、步数可变）（见 S0）。

---

## 搜索矩阵（S0–S5，24h 预算）

预算：**24 h 墙钟 ≈ 192 GPU·h**（8 卡满载）。计划用量 **~92 GPU·h**，余 **~100 GPU·h** 供重试/扩展。

短地平线统一 **5000 步/组**（GBS=8 × seq4094 = 32.7K tok/步，5000 步 ≈ 164M token）。长跑 S5-1 用 **20000 步**。

| 阶段 | 内容 | 组数 | 步数 | 备注 |
|:---|:---|:---|:---|:---|
| S0 | launcher 适配 + 8 卡冒烟 | 1 | ~10 | 实测 step time 校准预算 |
| S1 | baseline（lr 3e-4 / WSD）| 1 | 5000 | 建 loss/吞吐基线，产出 S1-01 |
| S2 | stable LR 加密扫描（7 点）| 7 | 5000 | WSD 固定，产出 S2-01…S2-07 |
| S3 | 关键轴微调 | 5 | 5000 | 胜出 LR 上单变量，产出 S3-01…S3-05 |
| S4 | 退火数据混合消融 | 3 | 5000 | 产出 S4-01…S4-03 |
| S5 | 长跑 + 多 seed | 4 | 20000 / 5000 | 收敛曲线 + 可复现，产出 S5-01…S5-04 |

### S2 stable LR（WSD 固定，7 点）
`2e-4 / 3e-4 / 4e-4 / 5e-4 / 6e-4 / 8e-4 / 1e-3`

### S3 关键轴（S2 胜出 LR 基础上，每次只动一个变量）
- S3-01/S3-02 调度族：WSD vs cosine（2 组）
- S3-03 decay ratio：5% （默认 10%，增量扫 15% 可选；warmup 固定 5%，stable 相应调整）
- S3-04 warmup：占比 5% vs 固定 2000 步（1 组）
- S3-05 min_lr：3e-5 vs 1e-5（1 组）

### S4 退火数据混合（胜出配置，decay 尾段混入）
- S4-01 纯 L3 高质量子集 | S4-02 L3+代码（UltraData-Code）| S4-03 L3+代码+数学（UltraData-Math）

### S5 长跑 + 多 seed
- S5-01 胜出配置从零 **20000 步**，产出论文 loss 收敛曲线
- S5-02…S5-04 胜出配置 3 seed × 5000 步，报 loss 均值±σ（可复现）

### 固定超参（跨配置一致，不扫）
- **8 卡（`10.239.2.29`，TP=1/DP=8）**、GBS=8（短地平线；**全量训练固定 GBS=1024**）、mb=1、seq=4094、bf16
- optimizer distributed AdamW（β1=0.9 β2=0.95 eps=1e-5 wd=0.1）、seed=1234
- WSD：warmup 5%=250、decay 10%=500、stable 85%=4250（均 5000 步口径）
- eval：`--eval-interval 250 --eval-iters 0`（关闭避免除零）

### 数据需求（关键，超步数前先核对）
- S1–S4（5000 步/组）：现有 200k docs / 165M token 已够（5000 步≈164M），各组独立从头复用同一份
- S5-01（20000 步≈655M token）：**需先补切数据**到 ≥700M token（用 L3 主数据 `preprocess_data`，按需混代码/数学退火源）再启动

---

## 推进状态机（PHASE）

- **S0 launcher 适配**：扩展 `pretrain_launcher.py` / `scripts/train.sh` 支持 `--lr` / `--lr-decay-style`（WSD/cosine）/ `--lr-warmup-iters` / `--lr-decay-iters` / `--min-lr` / `--seq-length=4094`，把 GBS/nproc/train-iters 参数化（默认 8 卡、GBS=8、DP=8）；确认 `arch=mamba2` 在 `10.239.2.29` 从零可跑 10 步冒烟，实测 step time → `PHASE=s1`
- **S1 基线**：跑 S1-01（lr 3e-4 / WSD / 5000 步），记录 loss / tok/s → `PHASE=s2`
- **S2 LR 扫描**：依次跑 7 个 LR（2e-4…1e-3），每个 5000 步，记录 val loss@匹配步数 → 选最优 LR → `PHASE=s3`
- **S3 关键轴**：胜出 LR 上单变量跑 5 组（调度族/decay/warmup/min_lr）→ 确定胜出配置 → `PHASE=s4`
- **S4 退火消融**：跑 3 组退火数据混合，量化退火质量增益 → `PHASE=s5`
- **S5 长跑+多seed**：先补切数据到 ≥700M，跑 winner 20000 步收敛曲线 + 3 seed 复现 → `PHASE=converged`
- **converged**：输出胜出配置 + 可复现命令 + `BAIZE_PRETRAIN_RESULT.html`，git push 后退出

每步先核对 `BUDGET_USED`（≤192 GPU·h）。val loss 必须在匹配步数下比较。

---

## 记忆管理

- `MEMORY_PRETRAIN_2B.md` — 运行时状态（STAGE/PHASE/ERROR_COUNT/BUDGET_USED/看板/流水）
- `EXPERIMENTS_PRETRAIN_2B.md` — 实验记录表（核心产出）
  `| ID | 阶段 | stable LR | 调度族 | decay/warmup/min_lr | 退火混合 | 状态 | val loss | 训练tok/s | 耗时 | GPU·h | 备注 |`
- `daily-memories/$(date +%F).md` — 当日操作日志

启动恢复：读 MEMORY → EXPERIMENTS → 当日日志 → 判断下一步 → 执行 → 回写。

---

## GPU 资源与进程管理

- **主训练节点 `10.239.2.29`（8×H100，GPU0~7）**，本计划 S1–S5 均在此节点 8 卡（TP1/DP8）串行运行；辅助 `10.239.2.12`（GPU0~5，GPU6~7 被占）。ssh 免密已通。
- 检查占用：`nvidia-smi` / `ssh 10.239.2.29 nvidia-smi` / `ssh 10.239.2.12 nvidia-smi`（`--query-compute-apps=pid,process_name,used_memory`）。
- 只杀本项目残留（`pgrep -af 'megatron|torchrun|pretrain_launcher'`），杀前记 PID 到 MEMORY 流水；不杀他人进程。
- 卡数对齐：两组对比须同卡数（各 8 卡 TP1/DP8）；主训练统一在 `10.239.2.29` 串行 8 卡。

---

## 时间估计

- 单步 ~350ms/iter（8 卡 TP1/DP8；SSM 串行是 bottleneck，6 卡基准 ~340ms 外推，S0 冒烟实测校准）
- 5000 步/组 ≈ **~30 min**（≈4.0 GPU·h）；20000 步 ≈ **~2 h**（≈15.6 GPU·h）

| 阶段 | 组数 | 步数 | 小计墙钟 | 小计 GPU·h |
|:---|:---|:---|:---|:---|
| S0 冒烟 | 1 | ~10 | ~1 min | ~0.1 |
| S1 baseline | 1 | 5000 | ~30 min | 4.0 |
| S2 LR×7 | 7 | 5000 | ~3.5 h | 28 |
| S3 关键轴×5 | 5 | 5000 | ~2.5 h | 20 |
| S4 退火×3 | 3 | 5000 | ~1.5 h | 12 |
| S5 长跑+3seed | 4 | 20000/5000 | ~3.5 h | 27.6 |
| **合计** | **21** | | **~11 h** | **~92** |

- 纯训练 ~11 h 墙钟 / ~92 GPU·h，24h 预算余 ~13 h / ~100 GPU·h 供重试与抖动
- 端到端（含 S0 launcher 扩展 + S5 补切数据）≈ **~14 h** 墙钟

---

## 验收产出

1. 胜出配置（stable LR + 调度族 + 关键轴 + 退火混合）+ 可复现命令（写 `EXPERIMENTS_PRETRAIN_2B.md` 顶部）
2. 20000 步 loss 收敛曲线 + 3 seed 均值±σ（回填论文图表）
3. `BAIZE_PRETRAIN_RESULT.html`（自包含：搜索矩阵 + 各配置 loss 表 + 胜出结论 + 命令）
4. git commit + push（只提交 `doc/` 文本 md/html，checkpoint/.bin/.idx 不入库）
