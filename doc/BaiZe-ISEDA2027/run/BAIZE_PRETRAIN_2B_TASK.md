# BAIZE_PRETRAIN_2B_TASK.md

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 预算约束超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

---

## 任务目标

在**已选定**的 Mamba2-hybrid（2.220B）骨架上，完成受预算约束的超参搜索（S1–S4），最终产出：

1. 一条**胜出配置**（stable LR + 调度族），val loss 优于其它候选
2. 一份**实验记录表**（`EXPERIMENTS_PRETRAIN_2B.md`），含所有配置的 ID / 超参 / 结果 / GPU·h
3. 一条**可复现训练命令**，能从头训练胜出配置
4. 一份 HTML 结果报告 `BAIZE_PRETRAIN_RESULT.html`

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
| 数据（stable 主体）| Ultra-FineWeb-L3 英文 `BASE_DIR/data/ultrafineweb_l3_qa`（`.bin/.idx` 已切）|
| 环境 | CUDA 12.8 / PyTorch 2.8.0 / Python 3.10；`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230` |
| GPU | 主训练 **`10.239.2.29`（8×H100，GPU0~7）**；辅助 `10.239.2.12`（GPU0~5）|

> 启动器：`BASE_DIR/scripts/train.sh <arch> <name> <master_port> [nproc]`（arch=`mamba2`，nproc 传 **8** 以用满 `10.239.2.29` 全 8 卡），内部调 `pretrain_launcher.py`。**需先扩展 launcher** 支持 `--lr-decay-style`（WSD/linear/cosine）、`--lr-warmup-iters`、`--lr-decay-iters`、`--seq-length=4094`，并把硬编码的 `--global-batch-size 6` / 默认 `nproc 6` 改为 8 卡口径（GBS=8、TP=1/DP=8）（当前 train.sh 缺这些，见 S0）。

---

## 搜索矩阵（S1–S4，每组 1000 步）

WSD 调度：warmup 固定 **5%＝50 步**、decay 固定 **10%＝100 步**、stable 85%＝850 步。唯一自由轴是 **stable LR**，S3 只对比**调度族**。

| 阶段 | 配置 | stable LR | 调度族 | 步数 | 产出 |
|:---|:---|:---|:---|:---|:---|
| S1 baseline | 复现参考配置 | 3e-4 | WSD | 1000 | S1-01 |
| S2 LR 扫描 | 4 个 LR 值 | **2e-4 / 3e-4 / 6e-4 / 1e-3** | WSD | 1000 | S2-01…S2-04 |
| S3 调度族 | WSD vs cosine | S2 胜出 LR | WSD / cosine | 1000 | S3-01 / S3-02 |
| S4 验证 | 胜出组合从零复跑 | S3 胜出 LR | S3 胜出族 | 1000 | S4-01（winner）|

### 固定超参（跨配置一致，不扫）
- **8 卡（`10.239.2.29`，TP=1/DP=8）**、GBS=8（短地平线代理；**全量训练固定 GBS=1024**、seq 4094、每步 ~4M token）、mb=1、seq=4094、bf16
- optimizer distributed AdamW（β1=0.9 β2=0.95 eps=1e-5 wd=0.1）、seed=1234
- eval：`--eval-interval 100 --eval-iters 0`（关闭避免除零）

### decay 数据（退火，明确可用）
decay 尾段（100 步）可混入代码（UltraData-Code）、数学（UltraData-Math）、SFT 语料做退火，**无需为 post-train 预留**（预训练退火与 post-train SFT 属不同阶段）。首版可先用 L3 高质量子集退火，再视需要引入代码/数学。

---

## 推进状态机（PHASE）

- **S0 launcher 适配**：扩展 `pretrain_launcher.py` / `scripts/train.sh` 支持 `--lr-decay-style`（WSD/cosine）、`--lr-warmup-iters`、`--lr-decay-iters`、`--seq-length`，并把 GBS/nproc 改为 8 卡口径（GBS=8、DP=8）；确认 `arch=mamba2` 在 `10.239.2.29` 从零可跑 10 步冒烟 → `PHASE=s1`
- **S1 基线**：跑 S1-01（lr 3e-4 / WSD / 1000 步），记录 loss / tok/s → `PHASE=s2`
- **S2 LR 扫描**：依次跑 4 个 LR（2e-4/3e-4/6e-4/1e-3），每次 1000 步，记录 val loss@匹配步数 → 选最优 LR → `PHASE=s3`
- **S3 调度族**：用 S2 胜出 LR 跑 WSD vs cosine 各 1000 步 → 选胜出族 → `PHASE=s4`
- **S4 验证**：胜出组合从零 1000 步复跑，确认收敛+可复现 → `PHASE=converged`
- **converged**：输出胜出配置 + 可复现命令 + `BAIZE_PRETRAIN_RESULT.html`，git push 后退出

每步先核对 `BUDGET_USED`（≤84 GPU·h）。val loss 必须在匹配步数下比较。

---

## 记忆管理

- `MEMORY_PRETRAIN_2B.md` — 运行时状态（STAGE/PHASE/ERROR_COUNT/BUDGET_USED/看板/流水）
- `EXPERIMENTS_PRETRAIN_2B.md` — 实验记录表（核心产出）
  `| ID | 阶段 | stable LR | 调度族 | warmup | decay | 状态 | val loss | 训练tok/s | 耗时 | GPU·h | 备注 |`
- `daily-memories/$(date +%F).md` — 当日操作日志

启动恢复：读 MEMORY → EXPERIMENTS → 当日日志 → 判断下一步 → 执行 → 回写。

---

## GPU 资源与进程管理

- **主训练节点 `10.239.2.29`（8×H100，GPU0~7）**，本计划超参搜索 S1–S4 均在此节点 8 卡（TP1/DP8）运行；辅助 `10.239.2.12`（GPU0~5，GPU6~7 被占）。ssh 免密已通。
- 检查占用：`nvidia-smi` / `ssh 10.239.2.29 nvidia-smi` / `ssh 10.239.2.12 nvidia-smi`（`--query-compute-apps=pid,process_name,used_memory`）。
- 只杀本项目残留（`pgrep -af 'megatron|torchrun|pretrain_launcher'`），杀前记 PID 到 MEMORY 流水；不杀他人进程。
- 卡数对齐：两组对比须同卡数（各 8 卡 TP1/DP8）；主训练统一在 `10.239.2.29` 串行 8 卡。

---

## 时间估计

- 单步 ~350ms/iter（8 卡 TP1/DP8；SSM 串行是 bottleneck，6 卡基准 ~340ms 外推，S0 冒烟实测校准）
- 每组含一次性启动开销（SSM 编译 ~12s + CUDA-graph 捕获/初始化 ~5s ≈ 17s）+ 1000 步 ≈ **~6.1 min**（≈0.81 GPU·h）

| 阶段 | 组数 | 单组墙钟 | 小计墙钟 | 小计 GPU·h |
|:---|:---|:---|:---|:---|
| S0 冒烟 | 1（10 步）| ~0.3 min | ~0.3 min | ~0.04 |
| S1 baseline | 1 | ~6.1 min | ~6.1 min | ~0.81 |
| S2 LR 扫描 | 4 | ~6.1 min | ~24.4 min | ~3.26 |
| S3 调度族 | 2 | ~6.1 min | ~12.2 min | ~1.63 |
| S4 验证 | 1 | ~6.1 min | ~6.1 min | ~0.81 |
| **合计** | **8** | | **~49 min** | **~6.5** |

- 纯训练（S1–S4，8 组）在 `10.239.2.29` 单节点 8 卡串行 ≈ **~49 min** 墙钟 / **~6.5 GPU·h**（8 卡跑满不闲置）
- 端到端（含 S0 launcher 扩展 ~30–45 min 编码）≈ **~1.5 h** 墙钟
- 预算 84 GPU·h 余量 >77 GPU·h，可容纳多轮重试与抖动。

---

## 验收产出

1. 胜出配置（stable LR + 调度族）+ 可复现命令（写 `EXPERIMENTS_PRETRAIN_2B.md` 顶部）
2. `BAIZE_PRETRAIN_RESULT.html`（自包含：搜索矩阵 + 各配置 loss 表 + 胜出结论 + 命令）
3. git commit + push（只提交 `doc/` 文本 md/html，checkpoint/.bin/.idx 不入库）