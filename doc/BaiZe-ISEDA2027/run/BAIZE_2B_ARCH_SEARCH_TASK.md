# BAIZE_2B_ARCH_SEARCH_TASK.md

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入本任务专属的 `MEMORY_2B.md`、`EXPERIMENTS_2B.md` 和 `daily-memories-2b/`（**不要**写入 1B 任务的 `MEMORY.md` / `EXPERIMENTS.md`）。

你是推进 **BaiZe 2B 架构搜索** 的 research agent，在 **2026-09-30 ~ 2026-10-08（十一假期）** 期间持续推进。每次被唤醒，**只走一步**：
读 `MEMORY_2B.md` 恢复状态 → 读 `EXPERIMENTS_2B.md` 看进展 → 读 `daily-memories-2b/$(date +%F).md` 恢复当日上下文 → 判断下一步 → 执行 → 更新记忆文件 → 退出。

---

## 任务目标

对两个 **~2B** 候选架构做**从零预训练**的公平对比，产出三组结论：

1. **loss 曲线对比**（早期收敛）
2. **训练速度对比**（tokens/sec）
3. **推理速度对比**（tokens/sec，prefill 与 decode 分开）

最终输出：一份胜出架构 + 完整的可复现训练命令 + 对比报告（写入 `EXPERIMENTS_2B.md` 顶部）+ **一份 HTML 报告**（路径 `doc/BaiZe-ISEDA2027/BAIZE_2B_ARCH_RESULT.html`，自包含、可离线打开，参照已存在的 `MAMBA2_HYBRID_2B_FEASIBILITY_REPORT.html` 的风格）。

### 两套候选架构（固定）

| 架构 | 参考文件 | 结构 |
|:---|:---|:---|
| **MiniCPM5-2B**（Llama 式） | `doc/BaiZe-ISEDA2027/MiniCPM5-2B.config.json` | 42 层 / hidden 2048 / intermediate 6144 / 16 attn heads / 2 KV heads / silu / RoPE θ=5e6 |
| **Mamba2-hybrid 2B**（attention+SSM 混合） | `doc/BaiZe-ISEDA2027/MAMBA2_HYBRID_2B_FEASIBILITY_REPORT.html` + 代码 `code/BaiZe-ISEDA2027/mamba2_hybrid_2b/` | 56 层 hybrid（`M`=SSM / `*`=attention / `-`=MLP）|

### 固定资源

- **Tokenizer**: `/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash/`（vocab **129280**，追加 `<|endoftext|>` EOD 后 **vocab=129281 / eod=129280**，模型侧 pad 到 **129408**）
- **训练数据**: `/nas_inference/app.e0031982/datasets/openbmb/`（选一个子集，如 Ultra-FineWeb-L3，切一段即可）
- **从零训练**：两架构均**随机初始化，不加载任何官方预训练权重**
- **少量训练**：目标 ~1000 步（seq 4096），用同一份数据子集保证可比

---

## 三个必须遵守的关键决策（防止 agent 走弯路）

### 决策 1：统一到 NVIDIA/NeMo recipe 路径（公平 + 真正"从零"）

两个架构存在**训练入口不对等**的问题，必须统一，否则三组指标不可比：

- **Mamba2-hybrid 2B**：只能走 NVIDIA/NeMo recipe（路径 A）——
  `megatron.bridge.training.pretrain.pretrain(pretrain_config(...), forward_step_func)`。
  已有 provider/recipe（`code/BaiZe-ISEDA2027/mamba2_hybrid_2b/`），但**步骤 4 launcher + forward_step + GPU 冒烟尚未落地**（见 FEASIBILITY.md）。
- **MiniCPM5-2B**：走 swift `megatron pt --model_type llama` 虽成熟，但有两个坑：
  1. swift 的 `--finetune` 语义是「加载 HF 权重微调(finetune=true) / 恢复 mcore ckpt(finetune=false)」，**没有纯随机初始化入口**（见 `ms-swift/swift/megatron/trainers/base.py::_load_checkpoint`）。
  2. 其 config `vocab_size=130560`（自带 tokenizer）与指定的 DeepSeek（129281）**不匹配**。

**结论**：两架构都走 **NVIDIA/NeMo recipe**，各写一个 2B provider + recipe（Mamba 已有；MiniCPM5-2B 需新建一个 42 层 Llama-style 的 `GPTModelProvider`，并手动把 `vocab/heads/layers` 设成 MiniCPM5-2B 的 config，tokenizer 用 DeepSeek）。
- 参考：`megatron.bridge.recipes.gpt.*`（mcore 官方 gpt recipe）+ 本仓库 `mamba2_hybrid_2b/recipe.py` 的写法。
- 若 MiniCPM5-2B 确需走 swift，agent 必须先在 `EXPERIMENTS_2B.md` 记录「随机初始化可行性」的验证结论，不得擅自用官方权重冒充"从零"。

### 决策 2：tokenizer / 词表统一为 DeepSeek

- 两架构嵌入层词表都按 **DeepSeek vocab=129281 → pad 129408**，**不要用 MiniCPM5-2B config 里的 130560**。
- 数据必须用**同一份 DeepSeek 切词的 `.bin/.idx`**（已有 `code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py` 可复用/参考）。
- 数据切词产物只生成一次，两架构共用，避免 tokenizer 影响对比。

### 决策 3：训练口径对齐（公平对比的前提）

两架构必须满足以下完全一致，**除了架构本身**：
- seq_length = 4096、micro_batch_size = 1（共享 GPU 下 mb2 易 OOM）
- 相同 global_batch_size（按 tokens 对齐或按 DP 卡数对齐，二选一并在 `EXPERIMENTS_2B.md` 注明）
- 相同 optimizer（AdamW）、相同 LR（建议 3e-4）、相同 warmup/decay、相同 weight_decay
- 相同 train_iters（~1000）、相同数据子集、相同随机 seed
- bf16 混合精度

---

## 记忆管理

- `MEMORY_2B.md` — 本任务运行时状态（STAGE/PHASE/ERROR_COUNT/BUDGET_USED、实验看板、操作流水）。不提交 git。
- `EXPERIMENTS_2B.md` — 本任务实验记录表（两架构的配置/结果/吞吐/耗时）。核心产出。
- `daily-memories-2b/$(date +%F).md` — 每日操作日志，每步追加一条带时间戳记录。

启动恢复：先读上述三个文件。操作后按「更新 MEMORY_2B → EXPERIMENTS_2B → daily-memories-2b」顺序回写。

---

## 背景（固定，勿改）

- 项目：**BaiZe**（2B LLM 架构搜索）
- 框架：**megatron-core / NVIDIA-NeMo recipe**（统一路径）；swift 仅作 Fallback 调研
- **BASE_DIR**: `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`
- **ms-swift 源码**: `/nas_train/app.e0031982/code/ms-swift`（v4.5.3）
- **megatron site-packages**: `/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/megatron`
- 数据根：`/nas_inference/app.e0031982/datasets/openbmb/`
- 环境（锁定）：CUDA 12.8 / PyTorch 2.8.0+cu128 / Python 3.10 / conda py310
- 序列长度 4096；micro_batch 1；预算：无硬上限，但建议单架构总 GPU·h ≤ 20
- ⚠️ **omegaconf 阻塞已规避**：`import megatron.bridge` 前需 `PYTHONPATH=/tmp/omegaconf_230:$PYTHONPATH`（OmegaConf 2.3.0，已装在 `/tmp/omegaconf_230`）
- **git 仓库**：根目录 `/nas_train/app.e0031982/code/super_intelligence_2035`（本任务记忆/报告在 `doc/BaiZe-ISEDA2027/run/` 内，会被提交）；remote `https://github.com/foamliu/super_intelligence_2035.git`（分支 main）。训练代码在 `BASE_DIR`（git 仓库外），训练产物（checkpoint/.bin/.idx 大文件）天然不被提交。

---

## 阶段划分与推进顺序

| 阶段 | 目标 | 说明 |
|:---|:---|:---|
| **S1 打通从零冒烟** | 两架构都能随机初始化、跑 10 步前向+反向、输出 loss | 关键：落地 NeMo launcher（torchrun + forward_step）；MiniCPM5-2B 新建 GPT/Llama provider。任一架构 3 次冒烟失败→记录 `❌ NOT_RUNNABLE` 并跳过 |
| **S2 1000 步训练** | 两架构各跑 ~1000 步，输出 loss 曲线 + 训练 tok/s | 相同数据/超参，只换架构 |
| **S3 推理 benchmark** | 两架构测推理 tok/s（prefill/decode 分开） | 统一口径：batch=1、固定 seq（如 4096→2048 生成），注明实现栈（HF vs mcore forward）|
| **S4 收敛报告** | 汇总三张对比表 + 胜出架构 + 可复现命令 + 生成 HTML 报告 | 写入 EXPERIMENTS_2B.md 顶部，并生成 `BAIZE_2B_ARCH_RESULT.html` |

搜索维度即「架构类型」两种；如时间富余，可在胜出架构上微调 LR（3e-4 vs 6e-4）各补一组，但不强求。

---

## GPU 资源与进程管理（双节点）

| 节点 | 可用 GPU | 说明 |
|:---|:---|:---|
| **10.239.2.29** | 8×H100 80GB（GPU 0~7） | 主训练节点 |
| **10.239.2.12** | 前 6×H100 80GB（GPU 0~5） | 辅助训练节点 |

- 两节点间 ssh 免密已通（`ssh 10.239.2.29` / `ssh 10.239.2.12` 直接可用），可用 torchrun 多节点或各自独立分配实验。
- **公平对比关键约束**：两架构必须用**相同卡数**训练（建议都用 6 卡，两节点可真正并行跑两个架构，节省假期时间；或都串行用 2.29 的 8 卡）。卡数不同会导致训练 tok/s 不可比，务必在 `EXPERIMENTS_2B.md` 注明每个架构的卡数/DP。
- 建议分配：MiniCPM5-2B 用 10.239.2.29（GPU0~5），Mamba2-hybrid 用 10.239.2.12（GPU0~5），剩余 2.29 的两卡（GPU6~7）留给冒烟/推理 benchmark。
- 启动前 `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`（本机）或 `ssh <节点> nvidia-smi ...`（远端）检查占用；共享时保持 mb=1。
- 允许清理本项目（BaiZe/2B）残留进程，杀前记录 PID/进程名/显存到 MEMORY_2B.md；不杀他人进程。
- 训练用 `setsid`/`nohup` 脱离，日志重定向 `/tmp/BAIZE2B_<ARCH>.log`；判断结束用 `pgrep -f 'megatron|swift|torchrun'`，不依赖日志尾。

## git 提交与保存（每 4~6 小时 push 一次）

- **agent 每次操作后**：在 git 根目录执行 `git add -A && git commit -m "<一句话描述>"`（提交记忆文件、脚本、报告等文本变更）。
- **push**：由 loop.sh 每约 5 小时兜底自动 push（`git push origin main`）；agent 也可在关键里程碑（arch_prepare 打通、1000 步完成、HTML 报告生成）主动 push。
- **认证已配好**：credential.helper=store + `~/.git-credentials` 已写入 PAT，`git push` 无需交互，不要在任何被提交的文件里明文写 token。
- **提交范围**：git 根目录 `/nas_train/app.e0031982/code/super_intelligence_2035`，只提交 `doc/` 下的文本（md/html/json/sh）；训练产物（checkpoint/.bin/.idx/tb 日志）在 `BASE_DIR`（git 外），**不要**把大文件 `git add` 进仓库。
- git 身份已配置：`Yang Liu <paul.liu@cxmt.com>`。

## 数据准备

- 切一段 Ultra-FineWeb-L3（如 `data/ultrafineweb_en_l3/qa` 前 N 个 part）够 1000 步即可（~4M tok/步 × 1000 ≈ 4B tokens，磁盘预算需提前估计）。
- 用 `code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py` 生成 `.bin/.idx`（DeepSeek 切词 + EOD），两架构共用。

---

## 固定命令

```bash
# 环境与阻塞规避
export PYTHONPATH=/tmp/omegaconf_230:$PYTHONPATH   # import megatron.bridge 必需
conda activate py310
python -c "import torch, megatron; print(torch.__version__, torch.version.cuda)"

# GPU（本机 + 双节点）
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
ssh 10.239.2.29 nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
ssh 10.239.2.12 nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

# 数据
ls -lh /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa/

# mcore GPT/Llama recipe 参考（MiniCPM5-2B 需据此新建）
python -c "import megatron.bridge.recipes.gpt as g; print([x for x in dir(g) if 'provider' in x.lower() or 'config' in x.lower()])"

# Mamba2-hybrid 现有产物
ls -R /nas_train/app.e0031982/code/BaiZe-ISEDA2027/mamba2_hybrid_2b/

# 启动实验（S1 冒烟 / S2 训练）
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027
setsid bash scripts/<脚本> > /tmp/BAIZE2B_<ARCH>.log 2>&1 < /dev/null &
```

---

## 推进逻辑（每次只走一步）

### 前置校验（所有 PHASE 先做）
读 MEMORY_2B.md 流水末 3 条，有未处理的 `❌`/`⚠️` 先处理，再正常推进。

### 状态机
- **PHASE=data_check**：确认至少一个可用数据子集 → 记录 → `PHASE=env_check`。
- **PHASE=env_check**：验证环境 + omegaconf 规避 + megatron.bridge 可 import → `PHASE=arch_prepare`。
- **PHASE=arch_prepare**（关键新步骤）：
  1. Mamba：落地 NeMo launcher（torchrun + `pretrain(pretrain_config(...), forward_step_func=gpt_step.forward_step)`），跑 10 步 GPU 冒烟。
  2. MiniCPM5-2B：新建 42 层 Llama-style 的 `GPTModelProvider` + recipe（vocab/heads/layers 取自 MiniCPM5-2B config，tokenizer=DeepSeek），同样跑 10 步冒烟。
  3. 记录每架构「从零可跑性」「参数量(实测 numel())」「冒烟 loss/吞吐」→ `PHASE=experiment_run`。
  - 某架构连续 3 次失败 → 标记 `❌ NOT_RUNNABLE`，跳过该架构，另一架构继续。
- **PHASE=experiment_run**：挑一个「已打通未跑完 1000 步」的架构，启动 1000 步训练 → `PHASE=experiment_wait`。
- **PHASE=experiment_wait**：`pgrep` 检查结束与否；结束后提取 loss 曲线 + tok/s，写 EXPERIMENTS_2B.md，更新累计耗时 → 回 `experiment_run`（换下一架构）或进 `infer_bench`。
- **PHASE=infer_bench**：为每个已训出 ckpt 的架构测推理 tok/s（统一口径），写入 EXPERIMENTS_2B.md → `PHASE=converged`。
- **PHASE=converged**：汇总三张对比表 + 胜出架构 + 可复现命令到 EXPERIMENTS_2B.md 顶部，输出结论，停止新实验。

---

## EXPERIMENTS_2B.md 建议格式

```markdown
# BaiZe 2B 架构搜索记录（从零训练）

## 胜出架构（待 S4 填写）

## 对比结论（loss / 训练速度 / 推理速度 三张表）

## 实验记录
| ID | 架构 | 参数量 | 状态 | 最终loss | 训练tok/s | 耗时 | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| A1-01 | MiniCPM5-2B(42层 Llama) | - | pending | - | - | - | 从零 |
| A2-01 | Mamba2-hybrid(56层) | ~2B | pending | - | - | - | 从零 |
```

---

## 待确认 / 风险提示（agent 需在 arch_prepare 阶段落地并记录）

1. **MiniCPM5-2B 随机初始化的 GPT provider**：mcore 哪套 recipe 可复用来构造 42 层 Llama（`GPTModelProvider` + Llama layer spec）？需查 `megatron.bridge.recipes.gpt`。
2. **NeMo launcher 的最小可用形态**：`nemo_run` 未装，需 torchrun + `nvidia_resiliency_ext.CallWrapper` 直驱（FEASIBILITY.md 已确认 bypass 可行）。
3. **参数量对齐**：如两端参数量差 >10%，需在报告注明「非等参对比」并说明影响。
4. **推理 benchmark 的实现栈**：Mamba2-hybrid 无 HF 推理，需在 mcore 上写前向/generate；MiniCPM5-2B 可用 HF generate。两者栈不同，报告必须注明，且统一测速口径（batch=1、固定 seq、prefill/decode 分列）。

> **搜索工具**：优先查本地 ms-swift / megatron-core 源码，其次用 `cimi-search` / `cimi-fetch`，不滥用。
