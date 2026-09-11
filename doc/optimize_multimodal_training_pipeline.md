# 任务：优化多模态训练流水线 `train_baize_4b.sh`

> **记忆驱动型任务** — 本任务通过外部 Markdown 文件维护长期状态，支持跨会话持续推进。

---

## 零、记忆系统（必须遵守，最高优先级）

### 0.1 记忆文件路径

所有记忆文件统一存放在 `docs/agent_tasks/` 目录下：

| 文件 | 路径 | 用途 | 更新频率 |
|------|------|------|---------|
| **主记忆库** | `docs/agent_tasks/MEMORY.md` | 项目目标、当前状态、已完成试验、决策记录 | 每次关键进展后立即更新 |
| **情景记忆** | `docs/agent_tasks/daily-memories/YYYY-MM-DD.md` | 当日工作计划、实时进度、临时发现 | 每次会话开始时创建/加载，工作中持续追加 |

**示例**：今天是 2026-08-14，则情景记忆文件为：
```
docs/agent_tasks/daily-memories/2026-08-14.md
```

### 0.2 强制工作流程

**每个会话开始时，必须按以下顺序执行：**

1. **切换工作目录**：`cd /nas_train/app.e0031982/code/LLaVA-OneVision-1.5/`
2. **读取主记忆库**：加载 `docs/agent_tasks/MEMORY.md`，理解项目全局状态
3. **读取/创建当日情景记忆**：
   - 若 `docs/agent_tasks/daily-memories/$(date +%Y-%m-%d).md` 存在，读取并了解今日进展
   - 若不存在，创建该文件，记录今日计划
4. **确认当前任务**：基于上述记忆，明确本次会话要推进的具体工作
5. **开始执行**

**每个关键节点（如试验启动/完成、发现新线索、遇到阻塞），必须立即更新：**
- `docs/agent_tasks/MEMORY.md` 中的"当前状态"和"试验记录"部分
- 当日情景记忆文件中追加时间戳记录

**每个会话结束时，必须：**
1. 更新 `docs/agent_tasks/MEMORY.md` 的"最后更新"时间戳
2. 在当日情景记忆中记录会话摘要（完成了什么、下一步计划）
3. 确认所有变更已写入文件

### 0.3 主记忆库模板 (`docs/agent_tasks/MEMORY.md`)

```markdown
# 项目记忆库：LLaVA-OneVision-1.5 训练优化

| 字段 | 内容 |
|------|------|
| **项目目标** | 最大化 12 项多模态评测指标均值 |
| **最后更新** | [自动填充时间戳] |
| **当前阶段** | [等待基线 / 试验中 / 分析结果] |
| **活动会话** | [会话ID或描述] |

## 1. 基线记录

| 基线名称 | Stage1.5 数据 | Stage1.5 iters | Stage2 数据 | Stage2 iters | 12项均值 | 状态 |
|----------|--------------|----------------|-------------|--------------|---------|------|
| `train_4b.sh` | 3M Quick-Start | 20000 | 780K | 3500 | 待评测 | 🔄 待运行 |
| `train_baize_4b.sh` | 85M Mid-Training | 75000 | 780K | 3500 | 待评测 | 🏃 运行中 (12号机, iter 57600/75000) |

## 2. 试验记录（按时间倒序）

| 试验ID | 描述 | 变量变更 | 状态 | 12项均值 | 备注 |
|--------|------|---------|------|---------|------|
| - | - | - | - | - | - |

## 3. 当前进行中

| 项目 | 详情 |
|------|------|
| 正在运行 | [描述当前正在执行的任务] |
| 下一步计划 | [明确的下一个动作] |
| 阻塞项 | [如有] |

## 4. 关键决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| - | - | - |

## 5. 可用资源清单

| 资源 | 路径/信息 |
|------|----------|
| 工作目录 | `/nas_train/app.e0031982/code/LLaVA-OneVision-1.5/` |
| 任务说明 | `docs/agent_tasks/optimize_multimodal_training_pipeline.md` |
| 主记忆库 | `docs/agent_tasks/MEMORY.md` |
| 情景记忆 | `docs/agent_tasks/daily-memories/` |
| 评测框架 | `/nas_train/app.e0031982/code/lmms-eval/` |
| 模型基座 | `/nas_train/app.e0031982/models/lmms-lab/LLaVA-OneVision-1.5-4B-stage0/` |
| Conda环境 | `py310` (`source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh && conda activate py310`) |
| 12号机 | 10.239.2.12, 8×H100 80GB (Stage1.5 运行中，约 3.5h 后进入 Stage2，整条流水线预计 16-24h 完成) |
| 29号机 | 10.239.2.29, 8×H100 80GB (完全空闲) |

### 数据清单

| 数据路径 | 用途 | 状态 |
|---------|------|------|
| `LLaVA-OneVision-1.5-Mid-Training-85M-packed-webdataset` | Stage1.5 | ✅ 可用 |
| `LLaVA-NeXT-780k-webdataset` | Stage2 | ✅ 可用 |
| `LLaVA-OneVision-1.5-Instruct-Data-packed-webdataset` | Stage2 备选 | ⚠️ 打包中 |
| `FineVision/` | Instruct 格式 | ❌ 未使用 |
| `BLIP3o/BLIP3o-Pretrain-Long-Caption/` | 图文对 | ❌ 未使用 |
| `Amshaker/Mobile-O-Pre-Train/` | 图文对 | ❌ 未使用 |
```

---

## 一、优化目标

**最大化最后 12 项评测指标的均值**。评测任务为：

```
ai2d, blink, chartqa, docvqa_val, infovqa_val, mme, mmmu_val, mmstar, ocrbench, realworldqa, countbench, mmmu_pro_standard
```

通过 `lmms-eval` 框架执行评测，命令格式为：

```bash
cd /nas_train/app.e0031982/code/lmms-eval/
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_OFFLINE=1
accelerate launch --num_processes=8 --main_process_port 12399 -m lmms_eval \
  --model=llava_onevision1_5 --batch_size=1 \
  --tasks ai2d,blink,chartqa,docvqa_val,infovqa_val,mme,mmmu_val,mmstar,ocrbench,realworldqa,countbench,mmmu_pro_standard \
  --model_args=pretrained=<HF_MODEL_PATH>,max_pixels=3240000
```

---

## 二、当前 Baseline 流水线（`train_baize_4b.sh`）

完整流水线位置：`/nas_train/app.e0031982/code/LLaVA-OneVision-1.5/train_baize_4b.sh`

### Stage 1.5 — Mid-Training

- 脚本：`examples/baize_4b/stage_1.5_mid_training_llava_ov_4b.sh`
- 数据：`/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M-packed-webdataset`（16TB，offline packed）
- `seq_len=8192`，`mbs=1`，`gbs=16`，`train_iters=75000`
- 优化器：Adam，`lr=1e-5`，`beta=(0.9,0.95)`，`weight_decay=0.01`
- **当前状态**：正在 10.239.2.12 运行中，约 iter 57600/75000（~77%），Stage1.5 约 3.5 小时后完成。之后将自动执行 Stage2 训练 → HF 模型转换 → 12 项评测，**整条流水线预计还需 16-24 小时**（其中 Stage2 ~3500 iters 为主要耗时环节）

### Stage 2 — Instruct Training

- 脚本：`examples/baize_4b/stage_2_instruct_llava_ov_4b.sh`
- 数据：`/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-NeXT-780k-webdataset`
- `seq_len=32768`，`mbs=1`，`gbs=224`，`train_iters=3500`
- 优化器：Adam，`lr=1e-5`，`beta=(0.9,0.99)`，`weight_decay=0`

### 模型转换 + 评测

见 `train_baize_4b.sh` 第 22–42 行。

---

## 三、可选更快速基线：`train_4b.sh`

`train_4b.sh` 使用更小的 mid-training 数据（3M Quick-Start），训练速度远快于 baize 版本，且**已知评测结果更优**，适合作为快速迭代的基线。

| 对比 | `train_baize_4b.sh` | `train_4b.sh` |
|------|---------------------|---------------|
| Stage1.5 数据 | 85M packed（16TB） | 3M Quick-Start |
| Stage1.5 seq_len | 8192 | 32768 |
| Stage1.5 train_iters | 75000 | 20000 |
| Stage1.5 脚本 | `examples/baize_4b/stage_1.5_...` | `examples/llava_ov_1_5/quick_start/stage_1.5_...` |
| Stage2 数据 | 780K（相同） | 780K（相同） |
| Stage2 脚本 | `examples/baize_4b/stage_2_...` | `examples/llava_ov_1_5/quick_start/stage_2_...` |
| 评测任务数 | 12 项 | 17 项（多 5 项，但 12 项交集可对比） |

---

## 四、可调变量

### 1. 训练数据（关键变量）

| 数据路径 | 状态 | 说明 |
|---------|------|------|
| `LLaVA-OneVision-1.5-Mid-Training-85M-packed-webdataset` | ✅ 当前使用 | 16TB，85M 样本，offline packed，stage1.5 |
| `LLaVA-NeXT-780k-webdataset` | ✅ 当前使用 | ~780K 样本，stage2 instruct |
| `LLaVA-OneVision-1.5-Instruct-Data-packed-webdataset` | ⚠️ 处理中 | 5.5TB 原始数据，`.work_16k/` 子目录正在打包中 |
| `FineVision/` | ❌ 未使用 | 186 个子数据集，instruct 格式 |
| `BLIP3o/BLIP3o-Pretrain-Long-Caption/` | ❌ 未使用 | 图文对（长描述），webdataset 格式 |
| `Amshaker/Mobile-O-Pre-Train/` | ❌ 未使用 | 图文对，webdataset 格式 |

**可探索方向**：
- 在 stage1.5 混入更多数据或替换数据源
- 在 stage2 使用更大的 instruct 数据集（如等待打包完成的 `Instruct-Data-packed-webdataset`）
- 混入 BLIP3o/Amshaker 图文对数据作为正则化
- FineVision 中筛选与评测任务相关的子集加入训练

### 2. 超参数

- GBS / MBS（全局/微批次大小）
- 学习率 `--lr`、`--min-lr`
- 优化器：`--optimizer adam/muon`（Muon 是否可用需验证 `aiak_training_llm/train.py`）
- `--adam-beta1/2`、`--adam-eps`
- `--weight-decay`
- `seq_len`（stage1.5: 8192 → 可尝试 16384/32768；stage2: 32768）
- `train_iters`（stage1.5: 75000 → 可增减；stage2: 3500）
- 其他：`--clip-grad`、`--lr-warmup-fraction`、`--recompute-num-layers`

### 3. 计算资源

| 服务器 | IP | GPU | 当前状态 |
|-------|-----|-----|---------|
| 12 号机 | 10.239.2.12 | 8×H100 80GB | Stage1.5 运行中（iter 57600/75000），约 3.5h 后进入 Stage2，整条流水线预计 16-24h 完成 |
| 29 号机 | 10.239.2.29 | 8×H100 80GB | **完全空闲** |

- 两台机器可 SSH 互通（已验证）
- **重要约束**：12 号机当前任务不要杀，等它跑完
- 多节点训练参考脚本：`scripts/start_2_node_training.sh`（需修改 IP 为 `10.239.2.12,10.239.2.29`）
- 训练脚本已内置多节点支持（`list_ip` 数组），只需修改 IP 列表即可 2 机 16 卡训练

---

## 五、关键注意事项：共享 NFS 与目录隔离

⚠️ **12 号机和 29 号机共享 NFS `/nas_train`**。多个试验同时运行时，输出目录会互相覆盖，**每次试验必须使用独立目录**。

### 目录冲突来源

当前脚本的输出目录由脚本文件名自动派生：`SAVE_CKPT_PATH=$(basename "$0" .sh)`。

| 阶段 | baize 脚本（示例） | 默认输出目录 |
|------|-------------------|-------------|
| Stage 1.5 | `stage_1.5_mid_training_llava_ov_4b.sh` | `stage_1.5_mid_training_llava_ov_4b/` |
| Stage 2   | `stage_2_instruct_llava_ov_4b.sh` | `stage_2_instruct_llava_ov_4b/` |
| HF 转换   | 在流水线脚本中硬编码 | `LLaVA-OneVision-1.5-4B-3M-Mid-Training-780K-Instruct/` |

### 隔离方案

每次新试验需要修改以下路径，确保不与正在运行的任务冲突：

1. **修改 stage 脚本文件名**（推荐）：复制脚本并重命名，如 `stage_1.5_mid_training_llava_ov_4b_exp1.sh` → 自动变更 `SAVE_CKPT_PATH`
2. **修改流水线脚本中的硬编码路径**：
   - Stage 1.5/2 的 `CHECKPOINT_PATH` 变量
   - HF 转换的目标目录 `FINAL_HF_DIR`
   - 评测命令中的 `--model_args pretrained=...` 路径

### 快速基线模板

以 `train_4b.sh` 为例，创建隔离版本需修改的关键行：

```bash
# train_4b.sh 中需改的目录：
STAGE15_OUTPUT_DIR="stage_1.5_mid_training_llava_ov_4b/iter_0020000"   # → 改为独立目录
STAGE2_OUTPUT_DIR="stage_2_instruct_llava_ov_4b/iter_0003500"           # → 改为独立目录
FINAL_HF_DIR="LLaVA-OneVision-1.5-4B-3M-Mid-Training-780K-Instruct"    # → 改为独立目录
```

---

## 六、约束条件

1. **不要杀掉 12 号机当前运行的 Stage1.5 训练**（约 3.5h 后自然结束，随后自动进入 Stage2）
2. 每次试验需走完整流水线：Stage1.5 → Stage2 → HF转换 → 评测
3. 评测在 8 卡单机执行（当前脚本使用 `--num_processes=8`）
4. 所有脚本和数据路径均在 `/nas_train/app.e0031982/` 下
5. **时间预期**：单次完整试验（Stage1.5 + Stage2 + 转换 + 评测）约需 **16-24 小时**。其中：
   - `train_4b.sh`：Stage1.5 20,000 iters + Stage2 3,500 iters
   - `train_baize_4b.sh`：Stage1.5 75,000 iters + Stage2 3,500 iters（当前 12 号机运行中）
   - 建议利用 29 号机并行开展试验，避免串行等待浪费时间

---

## 七、建议试验策略

> ⏰ **时间预期提醒**：单次完整试验（Stage1.5 + Stage2 + HF转换 + 评测）约需 **16-24 小时**。请据此规划试验节奏。

1. **先跑 `train_4b.sh` 快速基线**：在 29 号机（完全空闲）上以独立目录运行（参考第五节隔离方案），建立当前最佳分数基线。完整流水线（Stage1.5 + Stage2 + 转换 + 评测）预计需要 **16-24 小时**，请合理安排等待时间

2. **`train_baize_4b.sh` 基线**：当前 12 号机 Stage1.5 约 3.5h 后完成，随后自动执行 Stage2 → 转换 → 评测，自然获得 baize 基线。整条流水线预计还需 16-24 小时

3. **后续试验统一规范**：每次试验创建独立的输出目录（复制脚本重命名，或修改 CHECKPOINT_PATH/FINAL_HF_DIR），避免共享 NFS 冲突

4. **优先试验方向**：换更大 instruct 数据集（等 `Instruct-Data-packed-webdataset` 打包完成）→ 调 stage2 超参数 → 调 stage1.5 超参数

5. **12 号机空闲后**：可两台机器做 2 机 16 卡训练（修改 `list_ip` 为 `10.239.2.12 10.239.2.29`），加速大 batch 试验

---

## 八、工作目录与文件索引

| 资源 | 路径 |
|------|------|
| **工作目录** | `/nas_train/app.e0031982/code/LLaVA-OneVision-1.5/` |
| **任务说明** | `docs/agent_tasks/optimize_multimodal_training_pipeline.md`（本文件） |
| **主记忆库** | `docs/agent_tasks/MEMORY.md` |
| **情景记忆目录** | `docs/agent_tasks/daily-memories/` |
| 训练脚本模板 | `examples/baize_4b/` |
| 评测框架 | `/nas_train/app.e0031982/code/lmms-eval/` |
| 模型基座 | `/nas_train/app.e0031982/models/lmms-lab/LLaVA-OneVision-1.5-4B-stage0/` |
| Conda 环境 | `py310`（`source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh && conda activate py310`） |

---

## 九、Agent 执行逻辑：智能判断与退出

### 9.1 工作流决策树

每次会话启动时，按以下顺序判断：

```
1. 读取 MEMORY.md
   ↓
2. 检查是否所有基线/试验已完成？
   → 是：标记"已完成"，退出 (exit 0)
   ↓
3. 检查是否有正在运行的训练/评测？
   → 是：记录当前进度，主动退出 (exit 0)，等待下次唤醒
   ↓
4. 检查是否有已完成的 Stage1.5 等待 Stage2 启动？
   → 是：启动 Stage2 训练，更新 MEMORY.md，退出
   ↓
5. 检查是否有已完成的模型等待评测？
   → 是：启动评测，更新 MEMORY.md，退出
   ↓
6. 检查是否有新的试验设计等待启动？
   → 是：启动 Stage1.5 训练，更新 MEMORY.md，退出
   ↓
7. 若以上皆非：进入"主动规划"模式
   → 分析已有结果，设计下一个试验，更新 MEMORY.md 中的"下一步计划"，退出
```

### 9.2 检查训练/评测是否运行中的方法

```bash
# 检查是否有正在运行的训练进程（示例）
ps aux | grep -E "train.py|torchrun|accelerate" | grep -v grep

# 检查是否有正在运行的评测进程（示例）
ps aux | grep -E "lmms_eval|accelerate" | grep -v grep

# 检查指定机器的训练状态
ssh 10.239.2.12 "ps aux | grep train.py | grep -v grep"

# 检查训练日志的最后几行，判断是否仍在写入
tail -f /path/to/training/log  # 或检查日志文件的最新修改时间
```

### 9.3 状态标记规范

在 `MEMORY.md` 中，使用以下状态标记：

| 状态标记 | 含义 | Agent 行为 |
|---------|------|-----------|
| `**项目状态**：已完成` | 所有目标达成 | 立即退出，脚本终止 |
| `**当前阶段**：等待训练中` | 训练已提交，正在运行 | 记录进度，立即退出 |
| `**当前阶段**：等待评测中` | 评测已提交，正在运行 | 记录进度，立即退出 |
| `**当前阶段**：准备启动训练` | 空闲，准备提交新任务 | 启动训练，更新状态后退出 |
| `**当前阶段**：准备启动评测` | 模型已就绪，准备评测 | 启动评测，更新状态后退出 |
| `**当前阶段**：分析结果` | 评测已完成，待分析 | 分析结果，设计下一步，更新状态后退出 |
