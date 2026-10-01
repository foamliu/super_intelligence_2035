# OPS OUTBOX — 中继回收的执行结果

> **只增不改（append-only）**：每次执行在**文件末尾**追加一节。
> **最新结果在文件最下方**——`git pull` 后 `tail` 即可。
> 由 `ops_relay.sh` 写入；**运维只读**，人不要手改本文件。

---

_（尚无执行结果。等待 `ops/inbox.md` 的 RUN_ID 1 被执行。）_

---

## RUN_ID 1 · 2026-10-01 16:11:49 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "=========== BASIC ==========="
hostname; date; whoami; uname -r
echo
echo "=========== CPU / MEM ==========="
lscpu 2>/dev/null | grep -E '^Model name|^CPU\(s\):|^Socket' || true
free -g
echo
echo "=========== DISK ==========="
df -h 2>/dev/null | grep -E 'Filesystem|nas_train|nas_inference|/nas|/$' || df -h
echo
echo "=========== GPU (local node) ==========="
nvidia-smi
echo
echo "=========== RUNNING PROCESSES ==========="
echo "-- loops --"
pgrep -af 'baize_.*_loop\.sh|ops_relay\.sh' || echo "(no loop processes)"
echo "-- training --"
pgrep -af 'torchrun|megatron|pretrain_launcher|open_clip|train\.py' || echo "(no training processes)"
echo
echo "=========== REMOTE NODE 10.239.2.12 ==========="
ssh -o BatchMode=yes -o ConnectTimeout=8 10.239.2.12 'hostname; echo "-- gpu --"; nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader; echo "-- loops/training --"; pgrep -af "baize_.*_loop\.sh|torchrun|open_clip|train\.py" || echo "(none)"' 2>&1 | head -40
echo
echo "=========== GIT (shared working copy) ==========="
cd /nas_train/app.e0031982/code/super_intelligence_2035 && git status -sb | head -5 && git log --oneline -3
echo
echo "=========== DATA ROOTS ==========="
echo "-- /nas_inference/app.e0031982/datasets --"
ls -1 /nas_inference/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo "-- openbmb --"
ls -1 /nas_inference/app.e0031982/datasets/openbmb 2>/dev/null || echo "MISSING"
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo
echo "=========== KEY DATASET SIZES (timeout 90s each) ==========="
for d in \
  /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3 \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Code \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Math \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent \
  /nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M \
  /nas_train/app.e0031982/datasets/baize-vision ; do
  if [ -e "$d" ]; then
    echo "-- $d"
    timeout 90 du -sh "$d" 2>/dev/null || echo "   (du timed out or failed)"
    timeout 30 find "$d" -maxdepth 1 -type f 2>/dev/null | wc -l | sed 's/^/   files at depth1: /'
  else
    echo "-- $d  : MISSING"
  fi
done
echo
echo "=========== PYTHON / TORCH ==========="
P=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
[ -x "$P" ] && "$P" -c "import sys,torch;print('python',sys.version.split()[0]);print('torch',torch.__version__);print('cuda',torch.version.cuda);print('gpu_count',torch.cuda.device_count())" 2>&1 | head -10 || echo "python not found at $P"
echo
echo "=========== REPO / CODE LAYOUT ==========="
ls -1 /nas_train/app.e0031982/code 2>/dev/null | head -20
echo "-- BaiZe-ISEDA2027 --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027 2>/dev/null | head -20
echo "-- BaiZe-ISEDA2027/data --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data 2>/dev/null | head -20
echo
echo "=========== DONE ==========="
```

**输出**
```
=========== BASIC ===========
whag0pgpuap29
Thu Oct  1 04:11:49 PM CST 2026
app.e0031982
5.15.0-141-generic

=========== CPU / MEM ===========
CPU(s):                               224
Model name:                           Intel(R) Xeon(R) Platinum 8480+
Socket(s):                            2
               total        used        free      shared  buff/cache   available
Mem:            2015          41          45           0        1928        1963
Swap:              7           2           5

=========== DISK ===========
Filesystem                                                                                    Size  Used Avail Use% Mounted on
/dev/mapper/vgroot-lv_root                                                                    384G   13G  351G   4% /
10.239.23.31:/vol_CTE0_data01                                                                 207T  175T   33T  85% /nas_train
10.239.23.32:/vol_CTE0_data02                                                                 108T   80T   29T  74% /nas_user
10.239.23.32:/vol_CTE0_data03                                                                  45T   24T   22T  54% /nas_inference
10.239.23.32:/vol_CTE0_data04                                                                  10T   14G  9.9T   1% /nas_env

=========== GPU (local node) ===========
Thu Oct  1 16:11:49 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.195.03             Driver Version: 570.195.03     CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 80GB HBM3          On  |   00000000:16:00.0 Off |                    0 |
| N/A   25C    P0             71W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA H100 80GB HBM3          On  |   00000000:17:00.0 Off |                    0 |
| N/A   26C    P0             69W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   2  NVIDIA H100 80GB HBM3          On  |   00000000:40:00.0 Off |                    0 |
| N/A   28C    P0             70W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   3  NVIDIA H100 80GB HBM3          On  |   00000000:41:00.0 Off |                    0 |
| N/A   26C    P0             68W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   4  NVIDIA H100 80GB HBM3          On  |   00000000:96:00.0 Off |                    0 |
| N/A   29C    P0             71W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   5  NVIDIA H100 80GB HBM3          On  |   00000000:97:00.0 Off |                    0 |
| N/A   27C    P0             71W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   6  NVIDIA H100 80GB HBM3          On  |   00000000:C0:00.0 Off |                    0 |
| N/A   25C    P0             70W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   7  NVIDIA H100 80GB HBM3          On  |   00000000:C1:00.0 Off |                    0 |
| N/A   25C    P0             68W /  700W |       0MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+

=========== RUNNING PROCESSES ===========
-- loops --
2425284 bash baize_pretrain_loop.sh
2425291 bun /home/app.e0031982/.bun/bin/cline -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --auto-approve true -m deepseek-v4-pro-fp4 -t 1500 # BAIZE_PRETRAIN_2B_TASK.md # ══════════════ ROUND 2 · 第二轮任务（2026-10-01 生效，**优先于下方 Round 1**）══════════════  ## 🚫 铁律（最高优先级，先于本文件一切指令）  - **无论任务是否收敛、是否还有剩余工作，一律绝对禁止 `kill` / `pkill` / `stop` `baize_pretrain_loop.sh`（即 watchdog loop）。** - 任务收敛/完成后：只允许把 `MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（进入 30 分钟长轮询），然后**停在原地，让 watchdog 继续跑**。 - 🚫 **不得以「空转烧 token」之类的理由去 kill watchdog**——空转开销已由 `WAITING=1` 的 30 分钟长轮询兜底，属设计内行为。 - watchdog 必须 **7×24 持续运行**：运维会随时远程下发新任务（直接改写本任务书），下次唤醒即按新指令执行。  ## R2.0 状态切换（**先做**）  **MODE 已从 Round 1 切换为 Round 2。你在 `MEMORY_PRETRAIN_2B.md` 里看到的 `PHASE=converged`、以及"04:03 已 kill `baize_pretrain_loop.sh`"的记录，均已作废——** **loop 实际仍在运行（已被重新拉起），本任务重新有了工作。**  本唤醒请： 1. 在 `MEMORY_PRETRAIN_2B.md` 里把 `PHASE` 改为 `R2_active`，    并把 `WAITING` 字段改为纯文本 `0`（**注意**：loop 的正则是 `WAITING:[* ]*1`，    而你的流水里曾出现过 `WAITING: **1**` 这种散文，会**误触发 30 分钟长睡**——    请确保**全文除状态字段外不再出现 `WAITING: *1` 字样**，否则本任务会被拖慢）。 2. 流水追加一条"R2 启动"。 3. **Round 1 的结论仍有效，作为 R2 的对照基线；不要重跑 S0–S5。**  ## R2.1 为什么要做第二轮（结论需要加固的三处）  Round 1 的 S0–S5 已经收敛，但有三处**在论文里会被审稿人直接打**：  1. **LR 最优解落在网格边界上。** S2 扫了 `2e-4 … 1e-3` 七点，loss **单调改善到网格最大值 1e-3**——    也就是说**真正的极小值可能在 1e-3 之上，而扫描从未覆盖它**。论文目前只写 "improves monotonically"，    没交代"最优点在边界"，这是**过度声明**。 2. **Δ 小于噪声。** 论文写 `min_lr=1e-5 narrowly beats 3e-5`（2.7647 vs 2.7679，**Δ≈0.003**），    但 3-seed 的 **σ≈0.0469** —— **Δ 比噪声小一个量级**。"narrowly beats" 站不住，    要么补 seed 把 σ 压下来，要么如实写成 "within run-to-run noise"。 3. **架构选型的对比只跑了 1000 步 / 24.6M token**（GBS=6 的早期收敛快照），    却支撑了论文里"hybrid 更优"的核心 claim。需要延长到与其它实验同口径的 **5000 步**。  ## R2.2 实验清单（**保守包 P-1 / P-2 / P-3**，全部沿用 Round 1 的既有脚本与数据）  > 固定口径（除显式改动外，与 Round 1 一致）：8×H100 @ `10.239.2.29`、TP1/DP8、GBS=8、 > seq=4094、bf16、distributed AdamW(0.9,0.95,1e-5,wd0.1)、seed=1234、 > WSD warmup 250 / decay 500 / **min_lr 1e-5**、退火混合 L3(86%)+code(10%)+math(4%)。  | ID | 内容 | 目的 | 估时 | |:--|:--|:--|:--| | **P-1** | **LR 网格向上扩展**：stable LR ∈ **{1.5e-3, 2e-3, 3e-3}** × **5000 步**（WSD 固定） | **判定 1e-3 是否真的是最优** | 1.5h | | **P-2** | **补 2 个新 seed**（5000 步，胜出配置）→ **n=5** | **把 σ 压小 / 证实 Δ 在噪声内** | 1h | | **P-3** | **架构对比延长到 5000 步**（dense vs hybrid，**保持 Round 1 的 6 卡/GBS=6 口径**） | **让架构选型不再只靠 1000 步快照** | 1.5–2h |  **P-1 细节** - 三点：`1.5e-3 / 2e-3 / 3e-3`，其余超参与 S2/S3 完全一致，各 5000 步。 - 记录：**val loss@5000（必须匹配步数）**、train tok/s、耗时、GPU·h。 - ⚠️ **若某点 loss 发散/出现 NaN，不要重试超过 1 次**——**发散本身就是结论**（= LR 上界），   记录下来并把该点标为 `DIVERGED` 即可。这是我们要的边界信息。 - 产出：**10 点 LR 曲线**（Round 1 的 7 点 + 新增 3 点），标出极小值位置，   并明确回答"最优是否仍在网格边界"。  **P-2 细节** - Round 1 已有 3 个 seed@5000：`44 → 2.640200 / 777 → 2.653915 / 2024 → 2.727488`（均值 2.673868，σ 0.0469）。 - 新增 **2 个 seed**（任选未用过的，如 `7` 与 `2025`），同配置同 5000 步 → **n=5**。 - 产出：**n=5 的均值 ± σ**，并**明确回答**：`min_lr 1e-5 vs 3e-5 的 Δ≈0.003` 是否落在 n=5 的噪声范围内。 - 同时复核 Round 1 那 3 个 seed 的原始值是否与 `EXPERIMENTS_PRETRAIN_2B.md` 一致（只核对，不重跑）。  **P-3 细节** - 对象：**dense（MiniCPM5-2B）vs hybrid（Mamba2-hybrid）**，与 Round 1 的架构对比同源。 - ⚠️ **卡数与 GBS 必须沿用 Round 1 的对比口径（6 卡 / TP1/DP6 / GBS=6 / seed=1234）**，   否则与 Round 1 的 1000 步数据不可比。**这是本次最容易做错的一点。** - 跑 **5000 步**（Round 1 是 1000 步），并在 **500 / 1000 / 2000 / 3000 / 5000** 步各记一次 loss，   产出**两条 loss 曲线**而不是单点。 - 同时复核 Round 1 记录的参数量（`sum(numel())`：dense 2.512B / hybrid 2.220B）与   train tok/s、prefill/decode（沿用 Round 1 的 mcore 直驱口径），确认与论文 `tab:archcomp` 一致。 - 若 dense 在该口径下无法复现启动，**立即记录原因并跳过**（不要为此烧超过 30 分钟），   P-3 降级为"仅 hybrid 单侧延长"。  ## R2.3 交付物  1. **`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`**（新文件）：P-1/P-2/P-3 全部结果表 +    每条可复现命令 + 与 Round 1 的差异说明 + **「论文回填建议」段落**（给出精确数值与文字建议，    特别是「最优点是否在边界」「Δ 是否在噪声内」这两个结论该怎么写）。 2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_PRETRAIN_RESULT.html` 或新建 `BAIZE_PRETRAIN_RESULT_ROUND2.html`（自包含）。 3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——    论文已由外部统一重构并推送，回填由外部完成。你只在报告里给「回填建议」。 4. 正常更新 `MEMORY_PRETRAIN_2B.md` 与 `daily-memories/`。 5. **git commit + push，并严格走本文件顶部的「git 同步规则」**（fetch → 必要时 `pull --rebase` → push → 确认 0/0）。  ## R2.4 约束  - **总预算：R2 墙钟 ≤ 5 小时**（下次运维介入前）。超时按 **P-1 > P-2 > P-3** 逆序裁剪，并在报告记录裁剪决策。 - **GPU**：只用 `10.239.2.29` 的 **GPU 0–7**（8 卡）。**绝不杀他人进程**。   ⚠️ 另有 vision 任务在 **`10.239.2.12`**（另一台机器）跑——**与你无关，不要去动那台**。 - **每次启动训练前后都要记录 GPU 占用核验结果**（`nvidia-smi --query-compute-apps=...`）。 - ⚠️ **NFS 与 vision 任务共享（重要）**：两台 GPU 节点用的是**同一块 `/nas_train` 盘**。   vision 任务的 **R2-4 需要"无争用的干净吞吐测量"**，而你启动训练同样会打这块盘。   → **启动 P-1 之前**，先读 `run/MEMORY_VISION.md`（共享盘，你直接可见）看它的 R2 进度：   - 若 **R2-4 尚未完成**：先做**不占 GPU** 的准备工作（代码/数据核对、P-3 的 Round 1 基线复核、脚本落地），     **每轮唤醒重查一次**它的进度；   - **最多等 2 小时**；超过 2 小时则照常启动 P-1，并在报告里注明"当时 vision 任务在并发"。   → 你的**每次测量都要记录"当时 vision 任务在跑什么"**。 - 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；   **P-3 若需更长的数据覆盖，先核对再启动**，不要中途断数据。 - **收尾不杀 loop（关键）**：R2 的 P-1/P-2/P-3 全部完成（或按预算裁剪到只剩需等待的项）后，把结果写进报告并 git push，然后**停在原地**：`MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（30 分钟长轮询）；🚫 **绝不 kill / pkill `baize_pretrain_loop.sh`**。loop 必须持续运行，以便运维远程下发新任务（会改写本任务书，下次唤醒即按新指令执行）。  ---    > ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。  你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。  ## ⚠️ git 同步规则（**必读，2026-10-01 新增，每次唤醒都要走**）  ### 前提：这是一个**共享工作副本**  vision 任务的 agent 与本任务**共用同一份工作副本**——同一个 NFS 路径 `/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。  **因此：** - **只需一个人 pull，另一个立刻看到**：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。   **不要重复 pull**，也不要因为"工作区里出现了别的任务的改动"而困惑。 - 工作区里**陌生的未提交改动很可能是 vision 任务的在途文件**。🚫 绝不为此执行   `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。 - 两个 loop 每 5 小时各自 `git add -A && commit && push`，**会互相把对方在途的文件一起提交**。   这是既有设计的已知副作用，**不要试图"修正"它**。  ### 但 loop 本身**只 push 不 pull**  `baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。 一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。 **所以 pull 必须由你（agent）来做。**  **每次唤醒按顺序执行：**  1. `git fetch origin` + `git status -sb`，看 ahead/behind。 2. **提交时显式指定你自己的文件**：    `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`    🚫 **不要用 `git add -A`**——那会把 vision 任务的在途文件卷进你的提交。 3. 若显示 **behind / diverged**：`git pull --rebase origin main`。    - 报 `cannot rebase: You have unstaged changes` → 是**双方的在途改动**：      先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。    - 报 `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：      等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并**跳过本次 git 操作**，下次唤醒再试。    - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。 4. `git push origin main`；确认 `git status -sb` **无 ahead/behind** 才算闭环。 5. 流水记一行 git 结果（沿用你已有格式）。  > 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式 > `git pull --rebase` 合并远端后 push 成功——**沿用同一做法**。  ---   ---  ## 任务目标  在**已选定**的 Mamba2-hybrid（2.220B）骨架上，完成受 **24h 墙钟（≈192 GPU·h @ 8 卡）** 预算约束的高置信度超参搜索（S0–S5），最终产出：  1. 一条**胜出配置**（stable LR + 调度族 + 关键轴 + 退火数据混合） 2. 一份**实验记录表**（`EXPERIMENTS_PRETRAIN_2B.md`），含所有配置的 ID / 超参 / 结果 / GPU·h 3. 一条**20000 步长跑收敛曲线**（胜出配置）+ **多 seed 复现**（3 seed，报均值±σ） 4. 一条**可复现训练命令** + 一份 HTML 报告 `BAIZE_PRETRAIN_RESULT.html`  对应论文 `ISEDA2027/4_llm_pretrain.tex` 与计划 `BAIZE_LLM_PRETRAIN_PLAN.html`。  ---  ## 已定前提（固定，不要更改）  | 项 | 值 | |:---|:---| | 架构 | **Mamba2-hybrid**（56 层，Nemotron-H 式顺序混合，**2.220B**）| | 框架 | NVIDIA/NeMo recipe + Megatron-Core（`NVIDIAMambaHybridModelProvider2B`），torchrun 直驱 | | **BASE_DIR** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027` | | provider/recipe | `BASE_DIR/mamba2_hybrid_2b/`（provider.py / recipe.py，已有）| | tokenizer | DeepSeek-V4.1-Flash，`BASE_DIR/data/tokenizer_eod`（vocab 129281 / pad 129408）| | 数据（stable 主体）| Ultra-FineWeb-L3 英文 `BASE_DIR/data/ultrafineweb_l3_qa`（`.bin/.idx` 已切 200k docs / 165M token）| | 环境 | CUDA 12.8 / PyTorch 2.8.0 / Python 3.10；`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230` | | GPU | 主训练 **`10.239.2.29`（8×H100，GPU0~7）**；辅助 `10.239.2.12`（GPU0~5）|  > 启动器：`BASE_DIR/scripts/train.sh <arch> <name> <master_port> [nproc]`（arch=`mamba2`，nproc 传 **8** 以用满 `10.239.2.29` 全 8 卡），内部调 `pretrain_launcher.py`。**需先扩展 launcher** 支持 `--lr` / `--lr-warmup-iters` / `--lr-decay-iters` / `--lr-decay-style`（WSD|cosine）/ `--min-lr` / `--seq-length=4094`，并把硬编码的 `--global-batch-size 6` / 默认 `nproc 6` / `--train-iters 1000` 改为可按参数传（默认 8 卡：GBS=8、DP=8、步数可变）（见 S0）。  ---  ## 搜索矩阵（S0–S5，24h 预算）  预算：**24 h 墙钟 ≈ 192 GPU·h**（8 卡满载）。计划用量 **~92 GPU·h**，余 **~100 GPU·h** 供重试/扩展。  短地平线统一 **5000 步/组**（GBS=8 × seq4094 = 32.7K tok/步，5000 步 ≈ 164M token）。长跑 S5-1 用 **20000 步**。  | 阶段 | 内容 | 组数 | 步数 | 备注 | |:---|:---|:---|:---|:---| | S0 | launcher 适配 + 8 卡冒烟 | 1 | ~10 | 实测 step time 校准预算 | | S1 | baseline（lr 3e-4 / WSD）| 1 | 5000 | 建 loss/吞吐基线，产出 S1-01 | | S2 | stable LR 加密扫描（7 点）| 7 | 5000 | WSD
[relay] ⚠️ 输出超长，已截断到 20000 字符
```

---

## RUN_ID 2 · 2026-10-01 17:51:42 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "=========== LOOPS (line-truncated) ==========="
ps -eo pid=,comm=,args= 2>/dev/null | grep -E 'baize_.*_loop\.sh|ops_relay\.sh' | grep -v grep | cut -c1-140 || echo "(none)"
echo
echo "=========== TRAINING PROCESSES (line-truncated) ==========="
ps -eo pid=,comm=,args= 2>/dev/null | grep -E 'torchrun|megatron|pretrain_launcher|open_clip|train\.py' | grep -v grep | cut -c1-140 || echo "(none)"
echo
echo "=========== DATA ROOTS ==========="
echo "-- /nas_inference/app.e0031982/datasets --"
ls -1 /nas_inference/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo "-- openbmb --"
ls -1 /nas_inference/app.e0031982/datasets/openbmb 2>/dev/null || echo "MISSING"
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null || echo "MISSING"
echo "-- /nas_train/app.e0031982 (top-level) --"
ls -1 /nas_train/app.e0031982 2>/dev/null | head -20
echo
echo "=========== KEY DATASET SIZES (du timeout 90s each) ==========="
for d in \
  /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3 \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Code \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-Math \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605 \
  /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609 \
  /nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M \
  /nas_train/app.e0031982/datasets/baize-vision ; do
  if [ -e "$d" ]; then
    printf '%-95s : ' "$d"
    timeout 90 du -sh "$d" 2>/dev/null | cut -f1 || echo "(du timeout)"
  else
    echo "$d : MISSING"
  fi
done
echo
echo "=========== DISK FREE SPACE (matters for data prep) ==========="
df -h /nas_train /nas_inference /nas_user / 2>/dev/null
echo
echo "=========== PYTHON / TORCH ==========="
P=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
if [ -x "$P" ]; then "$P" -c "import sys,torch;print('python',sys.version.split()[0]);print('torch',torch.__version__);print('cuda',torch.version.cuda);print('gpu_count',torch.cuda.device_count())" 2>&1 | head -10; else echo "python not found at $P"; fi
echo
echo "=========== REPO / CODE LAYOUT ==========="
ls -1 /nas_train/app.e0031982/code 2>/dev/null | head -20
echo "-- BaiZe-ISEDA2027 --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027 2>/dev/null | head -25
echo "-- BaiZe-ISEDA2027/data --"
ls -1 /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data 2>/dev/null | head -20
echo
echo "=========== BAZE-VISION (derived, for stage iii/iv) ==========="
ls -1 /nas_train/app.e0031982/datasets/baize-vision 2>/dev/null || echo "MISSING"
du -sh /nas_train/app.e0031982/datasets/baize-vision/* 2>/dev/null | cut -f1,2 | head -10
echo
echo "=========== DONE ==========="
```

**输出**
```
=========== LOOPS (line-truncated) ===========
1276654 bash            bash ops_relay.sh
2425284 bash            bash baize_pretrain_loop.sh
2489749 bash            bash ops_relay.sh

=========== TRAINING PROCESSES (line-truncated) ===========
 317775 pt_elastic      /nas_train/app.e0031982/miniforge3/envs/py310/bin/python /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun 
 319613 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 319614 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 319615 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 319616 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 319617 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 319618 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 319619 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 319620 python          /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345850 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345851 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345852 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345853 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345854 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345855 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345856 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345857 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345858 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345859 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345860 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345861 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345862 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345863 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345864 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345865 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345866 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345867 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345868 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345869 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345870 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345871 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345872 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345873 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345874 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345875 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345876 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345877 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345878 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345879 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345880 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345881 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345882 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345883 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345884 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345885 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345886 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345887 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345888 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345889 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345890 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345891 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345892 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345893 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345894 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345895 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345896 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345897 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345898 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345899 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345900 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345901 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345902 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345903 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345904 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345905 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345906 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345907 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345944 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345946 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345949 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345962 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345967 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir
 345977 pt_data_worker  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name p2_seed7 --dir

=========== DATA ROOTS ===========
-- /nas_inference/app.e0031982/datasets --
AlienKevin
download_agent.sh
download_it_pairs.sh
download.sh
gijl
HuggingFaceFW
jasperai
kshitijthakkar
nohup.out
nvidia
openbmb
stanford-vision-lab
visionscaper
zhangdw
-- openbmb --
UltraData-Code
UltraData-Math
UltraData-SFT-2605
UltraData-SFT-Agent-2609
Ultra-FineWeb-L3
-- /nas_train/app.e0031982/datasets --
allenai
AMSbench
armanakbari4
baize-vision
check_parquet.py
coco
conceptual-captions-12m-webdataset
download2.sh
download_llava_onevision_fixed.sh
download_llava_onevision.sh
download_llava_onevision_subset.sh
download.log
download_missing_files.py
download.sh
FineVision
gqa
HuggingFaceFW
imagenet-1k
laion2B-en-aesthetic
LLaVA-CC3M-Pretrain-595K
LLaVA-Instruct-150K
LLaVA-OneVision-1.5-Instruct-Data-webdataset-16384
LLaVA-Pretrain
lmms-lab
MMMU
mvp-lab
nohup.out
ocr_vqa
openbmb
red_caps
stack.txt
stanford-corenlp-full-2016-10-31
stanford-corenlp-full-2016-10-31.zip
textvqa
vg
-- /nas_train/app.e0031982 (top-level) --
agents
author.txt
cache
chip_expert
cline
code
core
datasets
download
Downloads
harness
hello.py
hf_cache
load_model_arch.py
midtraining_checksums_partial.txt
midtraining_filelist_20260316_1610.txt
miniforge3
models
omegaconf_230
outputs

=========== KEY DATASET SIZES (du timeout 90s each) ===========
/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3                                   : 1.8T
/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code                                     : 1.2T
/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math                                     : 515G
/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605                                 : 152K
/nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-Agent-2609                           : 51G
/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M                   : 26T
/nas_train/app.e0031982/datasets/baize-vision                                                   : 179G

=========== DISK FREE SPACE (matters for data prep) ===========
Filesystem                     Size  Used Avail Use% Mounted on
10.239.23.31:/vol_CTE0_data01  207T  175T   33T  85% /nas_train
10.239.23.32:/vol_CTE0_data03   45T   25T   21T  54% /nas_inference
10.239.23.32:/vol_CTE0_data02  108T   80T   29T  74% /nas_user
/dev/mapper/vgroot-lv_root     384G   13G  351G   4% /

=========== PYTHON / TORCH ===========
/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/cuda/__init__.py:63: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
python 3.10.18
torch 2.8.0+cu128
cuda 12.8
gpu_count 8

=========== REPO / CODE LAYOUT ===========
apex
AReaL
backup
BaiZe-ISEDA2027
benchmarks
chip-mllm
circuitvision-encoder
claude-code-main
cline-langfuse.md
DataFlow
EDA-Eval-Framework
eda_fastmcp
emotion
EvolvingLMMs-Lab
flash-attention
hell
langfuse
LLaVA
LLaVA-OneVision-1.5
LLaVA-OneVision-1.5-RL
-- BaiZe-ISEDA2027 --
BaiZe-ISEDA2027
BAIZE_PRETRAIN_RESULT.html
BAIZE_PRETRAIN_TASK.md
baize_search_loop.sh
bridge_compat.py
daily-memories
data
EXPERIMENTS.md
EXPERIMENTS_PRETRAIN_2B.md
gen_model_variant.py
infer_benchmark.py
infer_diag.py
infer_prof.py
mamba2_hybrid_2b
MEMORY.md
MEMORY_PRETRAIN_2B.md
minicpm5_2b
models
nemo_experiments
output
pretrain_launcher.py
__pycache__
README.md
scripts
train_s1_01.sh
-- BaiZe-ISEDA2027/data --
anneal_code
anneal_code.bin
anneal_code.idx
anneal_code.json
anneal_math
anneal_math2
anneal_math2.bin
anneal_math2.idx
anneal_math2.json
anneal_math.bin
anneal_math.idx
anneal_math.json
tokenizer_eod
ultrafineweb_l3_qa
ultrafineweb_l3_qa_700m
ultrafineweb_l3_qa_700m.bin
ultrafineweb_l3_qa_700m.idx
ultrafineweb_l3_qa_700m.json
ultrafineweb_l3_qa.bin
ultrafineweb_l3_qa.idx

=========== BAZE-VISION (derived, for stage iii/iv) ===========
en500k
eval5k
out
smoke
69G	/nas_train/app.e0031982/datasets/baize-vision/en500k
1.3G	/nas_train/app.e0031982/datasets/baize-vision/eval5k
106G	/nas_train/app.e0031982/datasets/baize-vision/out
3.3G	/nas_train/app.e0031982/datasets/baize-vision/smoke

=========== DONE ===========
```

---

## RUN_ID 3 · 2026-10-01 19:07:58 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "=========== DF -H (ALL MOUNTS) ==========="
df -h
echo
echo "=========== DF -H (NAS + ROOT, explicit) ==========="
df -h /nas_train /nas_inference /nas_user /nas_env / 2>/dev/null
echo
echo "=========== DF -I (INODES — large-corpus trap) ==========="
df -i /nas_train /nas_inference /nas_user / 2>/dev/null
echo
echo "=========== TARGETED DU (bounded, timeout 150s each) ==========="
for d in \
  /nas_train/app.e0031982/datasets/baize-vision \
  /nas_train/app.e0031982/datasets/baize-data \
  /nas_train/app.e0031982/datasets/mvp-lab \
  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data \
  /nas_train/app.e0031982/models \
  /nas_inference/app.e0031982/datasets/openbmb ; do
  if [ -e "$d" ]; then
    printf '%-58s : ' "$d"
    timeout 150 du -sh "$d" 2>/dev/null | cut -f1 || echo "(du timeout/fail)"
  else
    echo "$d : MISSING"
  fi
done
echo
echo "=========== TOP-LEVEL LISTING (no du, just names) ==========="
echo "-- /nas_train/app.e0031982 --"
ls -1 /nas_train/app.e0031982 2>/dev/null | head -20
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null | head -40
echo "-- /nas_user/app.e0031982/datasets --"
ls -1 /nas_user/app.e0031982/datasets 2>/dev/null | head -40
echo
echo "=========== BAZE-VISION DETAIL (stage iii/iv) ==========="
ls -1 /nas_train/app.e0031982/datasets/baize-vision 2>/dev/null || echo "MISSING"
timeout 60 du -sh /nas_train/app.e0031982/datasets/baize-vision/* 2>/dev/null | cut -f1,2 | head -10
echo
echo "=========== ANY IN-PROGRESS DOWNLOAD? ==========="
ps -eo pid=,etime=,comm=,args= 2>/dev/null | grep -E 'wget|curl|hf_transfer|datasets|nohup' | grep -v grep | cut -c1-140 | head -10 || echo "(none)"
echo "-- nohup.out tail (if a download is logging) --"
for f in /nas_inference/app.e0031982/datasets/nohup.out /nas_train/app.e0031982/datasets/nohup.out; do
  [ -f "$f" ] && { echo "== $f"; tail -5 "$f" | cut -c1-140; }
done
echo
echo "=========== DONE ==========="
```

**输出**
```
=========== DF -H (ALL MOUNTS) ===========
Filesystem                                                                                    Size  Used Avail Use% Mounted on
tmpfs                                                                                         202G  379M  202G   1% /run
/dev/mapper/vgroot-lv_root                                                                    384G   13G  351G   4% /
/dev/disk/by-id/dm-uuid-LVM-7REZHedvpF4bkkJNhmRZBzI5uNORjyT0tXXhvbSyDpfPi1ITi32wKNaWxz2MpChC   98G   25G   69G  27% /usr
tmpfs                                                                                        1008G  2.4G 1006G   1% /dev/shm
tmpfs                                                                                         5.0M     0  5.0M   0% /run/lock
/dev/sdb2                                                                                     2.0G  346M  1.5G  19% /boot
/dev/sdb1                                                                                     1.1G  6.1M  1.1G   1% /boot/efi
/dev/mapper/vgroot-lv_home                                                                    196G  163G   24G  88% /home
/dev/mapper/vgroot-lv_tmp                                                                      98G   55G   39G  59% /tmp
/dev/mapper/vgroot-lv_var                                                                      98G  6.1G   87G   7% /var
/dev/mapper/vgdata-lv_data                                                                    7.0T  510G  6.5T   8% /data
10.239.23.31:/vol_CTE0_data01                                                                 207T  176T   32T  85% /nas_train
10.239.23.32:/vol_CTE0_data02                                                                 108T   80T   29T  74% /nas_user
10.239.23.32:/vol_CTE0_data03                                                                  45T   25T   21T  54% /nas_inference
10.239.23.32:/vol_CTE0_data04                                                                  10T   14G  9.9T   1% /nas_env
tmpfs                                                                                         202G  4.0K  202G   1% /run/user/6203
tmpfs                                                                                         202G  4.0K  202G   1% /run/user/6218

=========== DF -H (NAS + ROOT, explicit) ===========
Filesystem                     Size  Used Avail Use% Mounted on
10.239.23.31:/vol_CTE0_data01  207T  176T   32T  85% /nas_train
10.239.23.32:/vol_CTE0_data03   45T   25T   21T  54% /nas_inference
10.239.23.32:/vol_CTE0_data02  108T   80T   29T  74% /nas_user
10.239.23.32:/vol_CTE0_data04   10T   14G  9.9T   1% /nas_env
/dev/mapper/vgroot-lv_root     384G   13G  351G   4% /

=========== DF -I (INODES — large-corpus trap) ===========
Filesystem                          Inodes     IUsed        IFree IUse% Mounted on
10.239.23.31:/vol_CTE0_data01 987842478080 246253507 987596224573    1% /nas_train
10.239.23.32:/vol_CTE0_data03 214748364800    308022 214748056778    1% /nas_inference
10.239.23.32:/vol_CTE0_data02 515396075520 154161191 515241914329    1% /nas_user
/dev/mapper/vgroot-lv_root        25608192      7521     25600671    1% /

=========== TARGETED DU (bounded, timeout 150s each) ===========
/nas_train/app.e0031982/datasets/baize-vision              : 179G
/nas_train/app.e0031982/datasets/baize-data : MISSING
/nas_train/app.e0031982/datasets/mvp-lab                   : /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data          : 7.1G
/nas_train/app.e0031982/models                             : 452G
/nas_inference/app.e0031982/datasets/openbmb               : 3.4T

=========== TOP-LEVEL LISTING (no du, just names) ===========
-- /nas_train/app.e0031982 --
agents
author.txt
cache
chip_expert
cline
code
core
datasets
download
Downloads
harness
hello.py
hf_cache
load_model_arch.py
midtraining_checksums_partial.txt
midtraining_filelist_20260316_1610.txt
miniforge3
models
omegaconf_230
outputs
-- /nas_train/app.e0031982/datasets --
allenai
AMSbench
armanakbari4
baize-vision
check_parquet.py
coco
conceptual-captions-12m-webdataset
download2.sh
download_llava_onevision_fixed.sh
download_llava_onevision.sh
download_llava_onevision_subset.sh
download.log
download_missing_files.py
download.sh
FineVision
gqa
HuggingFaceFW
imagenet-1k
laion2B-en-aesthetic
LLaVA-CC3M-Pretrain-595K
LLaVA-Instruct-150K
LLaVA-OneVision-1.5-Instruct-Data-webdataset-16384
LLaVA-Pretrain
lmms-lab
MMMU
mvp-lab
nohup.out
ocr_vqa
openbmb
red_caps
stack.txt
stanford-corenlp-full-2016-10-31
stanford-corenlp-full-2016-10-31.zip
textvqa
vg
-- /nas_user/app.e0031982/datasets --
Amshaker
ayoubkirouane
BLIP3o
cxmt
download_llava_onevision.sh
mvp-lab
nohup.out
Recap-DataComp-1B
UCSC-VLAA

=========== BAZE-VISION DETAIL (stage iii/iv) ===========
en500k
eval5k
out
smoke
69G	/nas_train/app.e0031982/datasets/baize-vision/en500k
1.3G	/nas_train/app.e0031982/datasets/baize-vision/eval5k
106G	/nas_train/app.e0031982/datasets/baize-vision/out
3.3G	/nas_train/app.e0031982/datasets/baize-vision/smoke

=========== ANY IN-PROGRESS DOWNLOAD? ===========
-- nohup.out tail (if a download is logging) --
== /nas_inference/app.e0031982/datasets/nohup.out
Downloading 'train/gpic_train_00387.tar' to 'stanford-vision-lab/gpic/.cache/huggingface/download/train/qo9scC0lAH5lXSrbMaIGuOigvic=.1db0df7
Download complete. Moving file to stanford-vision-lab/gpic/train/gpic_train_00387.tar
Downloading 'train/gpic_train_00388.tar' to 'stanford-vision-lab/gpic/.cache/huggingface/download/train/qSz-eSgMvaxRnKkN840JB_XZIEs=.4daf090
Download complete. Moving file to stanford-vision-lab/gpic/train/gpic_train_00388.tar
Downloading 'train/gpic_train_00389.tar' to 'stanford-vision-lab/gpic/.cache/huggingface/download/train/6cHk59ZFbwYmYNnHedG-RPgzuLQ=.56d3ac4
== /nas_train/app.e0031982/datasets/nohup.out
Downloading 'obelics/EN/part47/train-00061-of-00063.parquet' to 'mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/.cache/huggingface/download/ob
Download complete. Moving file to mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/obelics/EN/part47/train-00061-of-00063.parquet
Downloading 'obelics/EN/part47/train-00062-of-00063.parquet' to 'mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/.cache/huggingface/download/ob
Download complete. Moving file to mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/obelics/EN/part47/train-00062-of-00063.parquet
Downloading 'obelics/EN/part48/train-00000-of-00063.parquet' to 'mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/.cache/huggingface/download/ob

=========== DONE ===========
```
