# BAIZE_PRETRAIN_2B_TASK.md
# ══════════════ ROUND 2 · 第二轮任务（2026-10-01 生效，**优先于下方 Round 1**）══════════════

## R2.0 状态切换（**先做**）

**MODE 已从 Round 1 切换为 Round 2。你在 `MEMORY_PRETRAIN_2B.md` 里看到的
`PHASE=converged`、以及"04:03 已 kill `baize_pretrain_loop.sh`"的记录，均已作废——**
**loop 实际仍在运行（已被重新拉起），本任务重新有了工作。**

本唤醒请：
1. 在 `MEMORY_PRETRAIN_2B.md` 里把 `PHASE` 改为 `R2_active`，
   并把 `WAITING` 字段改为纯文本 `0`（**注意**：loop 的正则是 `WAITING:[* ]*1`，
   而你的流水里曾出现过 `WAITING: **1**` 这种散文，会**误触发 30 分钟长睡**——
   请确保**全文除状态字段外不再出现 `WAITING: *1` 字样**，否则本任务会被拖慢）。
2. 流水追加一条"R2 启动"。
3. **Round 1 的结论仍有效，作为 R2 的对照基线；不要重跑 S0–S5。**

## R2.1 为什么要做第二轮（结论需要加固的三处）

Round 1 的 S0–S5 已经收敛，但有三处**在论文里会被审稿人直接打**：

1. **LR 最优解落在网格边界上。** S2 扫了 `2e-4 … 1e-3` 七点，loss **单调改善到网格最大值 1e-3**——
   也就是说**真正的极小值可能在 1e-3 之上，而扫描从未覆盖它**。论文目前只写 "improves monotonically"，
   没交代"最优点在边界"，这是**过度声明**。
2. **Δ 小于噪声。** 论文写 `min_lr=1e-5 narrowly beats 3e-5`（2.7647 vs 2.7679，**Δ≈0.003**），
   但 3-seed 的 **σ≈0.0469** —— **Δ 比噪声小一个量级**。"narrowly beats" 站不住，
   要么补 seed 把 σ 压下来，要么如实写成 "within run-to-run noise"。
3. **架构选型的对比只跑了 1000 步 / 24.6M token**（GBS=6 的早期收敛快照），
   却支撑了论文里"hybrid 更优"的核心 claim。需要延长到与其它实验同口径的 **5000 步**。

## R2.2 实验清单（**保守包 P-1 / P-2 / P-3**，全部沿用 Round 1 的既有脚本与数据）

> 固定口径（除显式改动外，与 Round 1 一致）：8×H100 @ `10.239.2.29`、TP1/DP8、GBS=8、
> seq=4094、bf16、distributed AdamW(0.9,0.95,1e-5,wd0.1)、seed=1234、
> WSD warmup 250 / decay 500 / **min_lr 1e-5**、退火混合 L3(86%)+code(10%)+math(4%)。

| ID | 内容 | 目的 | 估时 |
|:--|:--|:--|:--|
| **P-1** | **LR 网格向上扩展**：stable LR ∈ **{1.5e-3, 2e-3, 3e-3}** × **5000 步**（WSD 固定） | **判定 1e-3 是否真的是最优** | 1.5h |
| **P-2** | **补 2 个新 seed**（5000 步，胜出配置）→ **n=5** | **把 σ 压小 / 证实 Δ 在噪声内** | 1h |
| **P-3** | **架构对比延长到 5000 步**（dense vs hybrid，**保持 Round 1 的 6 卡/GBS=6 口径**） | **让架构选型不再只靠 1000 步快照** | 1.5–2h |

**P-1 细节**
- 三点：`1.5e-3 / 2e-3 / 3e-3`，其余超参与 S2/S3 完全一致，各 5000 步。
- 记录：**val loss@5000（必须匹配步数）**、train tok/s、耗时、GPU·h。
- ⚠️ **若某点 loss 发散/出现 NaN，不要重试超过 1 次**——**发散本身就是结论**（= LR 上界），
  记录下来并把该点标为 `DIVERGED` 即可。这是我们要的边界信息。
- 产出：**10 点 LR 曲线**（Round 1 的 7 点 + 新增 3 点），标出极小值位置，
  并明确回答"最优是否仍在网格边界"。

**P-2 细节**
- Round 1 已有 3 个 seed@5000：`44 → 2.640200 / 777 → 2.653915 / 2024 → 2.727488`（均值 2.673868，σ 0.0469）。
- 新增 **2 个 seed**（任选未用过的，如 `7` 与 `2025`），同配置同 5000 步 → **n=5**。
- 产出：**n=5 的均值 ± σ**，并**明确回答**：`min_lr 1e-5 vs 3e-5 的 Δ≈0.003` 是否落在 n=5 的噪声范围内。
- 同时复核 Round 1 那 3 个 seed 的原始值是否与 `EXPERIMENTS_PRETRAIN_2B.md` 一致（只核对，不重跑）。

**P-3 细节**
- 对象：**dense（MiniCPM5-2B）vs hybrid（Mamba2-hybrid）**，与 Round 1 的架构对比同源。
- ⚠️ **卡数与 GBS 必须沿用 Round 1 的对比口径（6 卡 / TP1/DP6 / GBS=6 / seed=1234）**，
  否则与 Round 1 的 1000 步数据不可比。**这是本次最容易做错的一点。**
- 跑 **5000 步**（Round 1 是 1000 步），并在 **500 / 1000 / 2000 / 3000 / 5000** 步各记一次 loss，
  产出**两条 loss 曲线**而不是单点。
- 同时复核 Round 1 记录的参数量（`sum(numel())`：dense 2.512B / hybrid 2.220B）与
  train tok/s、prefill/decode（沿用 Round 1 的 mcore 直驱口径），确认与论文 `tab:archcomp` 一致。
- 若 dense 在该口径下无法复现启动，**立即记录原因并跳过**（不要为此烧超过 30 分钟），
  P-3 降级为"仅 hybrid 单侧延长"。

## R2.3 交付物

1. **`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`**（新文件）：P-1/P-2/P-3 全部结果表 +
   每条可复现命令 + 与 Round 1 的差异说明 + **「论文回填建议」段落**（给出精确数值与文字建议，
   特别是「最优点是否在边界」「Δ 是否在噪声内」这两个结论该怎么写）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_PRETRAIN_RESULT.html` 或新建 `BAIZE_PRETRAIN_RESULT_ROUND2.html`（自包含）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——
   论文已由外部统一重构并推送，回填由外部完成。你只在报告里给「回填建议」。
4. 正常更新 `MEMORY_PRETRAIN_2B.md` 与 `daily-memories/`。
5. **git commit + push，并严格走本文件顶部的「git 同步规则」**（fetch → 必要时 `pull --rebase` → push → 确认 0/0）。

## R2.4 约束

- **总预算：R2 墙钟 ≤ 5 小时**（下次运维介入前）。超时按 **P-1 > P-2 > P-3** 逆序裁剪，并在报告记录裁剪决策。
- **GPU**：只用 `10.239.2.29` 的 **GPU 0–7**（8 卡）。**绝不杀他人进程**。
  ⚠️ 另有 vision 任务在 **`10.239.2.12`**（另一台机器）跑——**与你无关，不要去动那台**。
- **每次启动训练前后都要记录 GPU 占用核验结果**（`nvidia-smi --query-compute-apps=...`）。
- 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；
  **P-3 若需更长的数据覆盖，先核对再启动**，不要中途断数据。

---



> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（**必读，2026-10-01 新增，每次唤醒都要走**）

本任务与 **vision 任务**（`*_VISION*` / `daily-memories-vision/`）以及**人工在 Windows 侧的提交**
共用同一个 `origin/main`。而 `baize_pretrain_loop.sh` 的兜底 `git_push_if_needed()`
**只做 `add → commit → push`，不做 `pull`**。

后果：一旦远端被别人推进，你的 push 会以
`! [rejected] main -> main (fetch first)` **失败，并且永久卡住**——每 5 小时重试一次、永远失败，
本地提交越积越多。**以前不出问题只是因为你曾经是唯一在推的人。**

**因此每次唤醒必须按顺序执行：**

1. `git fetch origin`
2. `git status -sb`，看是否出现 `## main...origin/main [behind N]` 或 `[ahead M, behind N]`
3. 若 **behind 或 diverged**：执行 `git pull --rebase origin main`
   - 冲突时**优先保留双方各自的新增内容**；本任务只改
     `MEMORY_PRETRAIN_2B.md` / `EXPERIMENTS_PRETRAIN_2B.md` / `daily-memories/`，
     与 vision 任务、以及论文 `ISEDA2027/*.tex` **文件不重叠**，通常不会真冲突
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`（会丢别人的提交）
4. `git push origin main`
5. 确认 `git status -sb` 显示 `## main...origin/main` **无 ahead/behind**，才算同步闭环
6. 在流水里记一行 git 同步结果（沿用你已有的格式）

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——**沿用同一做法**。

---


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
