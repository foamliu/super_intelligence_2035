# BAIZE_VISION_TASK.md

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入本任务专属的 `MEMORY_VISION.md`、`EXPERIMENTS_VISION.md` 和 `daily-memories-vision/`（**不要**写入 1B 的 `MEMORY.md`/`EXPERIMENTS.md` 或 2B 的 `MEMORY_2B.md`/`EXPERIMENTS_2B.md`）。

你是推进 **BaiZe Stage(iii) 视觉编码器预训练** 的自动化 research agent（Cline），每次被唤醒后：读 `MEMORY_VISION.md` 恢复状态 → 读 `EXPERIMENTS_VISION.md` 看进展 → 读 `daily-memories-vision/$(date +%F).md` 恢复当日上下文 → 判断下一步 → **连续执行**（无阻塞时一口气做完可立即完成的步骤）→ 更新记忆文件 → 退出。

**持续推进原则（关键，避免「做一小步就睡」）**：
- **无阻塞任务时**：把能立即做完的步骤一口气连续做完（可跨越多个 PHASE），直到遇到必须等待的异步任务或单次预算将尽（约 25 分钟），不要做一小步就退出。
- **有异步阻塞任务时**（训练 running 等）：回写记忆并把 `MEMORY_VISION.md` 的 `WAITING` 置为 `1`，记录「等待什么、如何判断结束」，然后退出（loop.sh 据此拉长睡眠省 token）。下次唤醒先检查该任务是否结束，结束后把 `WAITING` 置回 `0` 再继续。

---

## 任务目标（24 小时预算，三层次结论）

在 **24 小时墙钟预算**内，对四个 **500–600M** 候选视觉编码器做**从零预训练**（随机初始化）的公平对比，分三层次产出：

1. **P0 基础（必做）——三组硬指标**：对比 loss 曲线（早期收敛 ~1000 步）、训练吞吐（image/s）、推理吞吐（图像→token/s）。锁定「默认配置 + 胜出架构」。
2. **P1 稳健（优先）——让排名可信**：长地平线（5k–10k 步）、多种子复现、下游代理评估（zero-shot / linear-probe 检索）。
3. **P2 核心自由度（论文重点）**：分辨率 / patch / 对比目标函数 / 数据侧（caption 粒度·规模·中英比例）消融。
4. **P3 训练超参与推理深度（有余量才做）**：LR / warmup 扫描、推理 batch/量化/分辨率深挖、装 SGLang 补生产级推理数据。

最终输出：一份胜出架构 + 完整可复现训练命令 + 多阶段对比报告（写入 `EXPERIMENTS_VISION.md` 顶部）+ HTML 结果报告 `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html`（自包含、可离线打开），并把胜出配置回填论文 `ISEDA2027/6_vision_encoder.tex`。

对应论文 `ISEDA2027/6_vision_encoder.tex`（当前 `[TBD]`）与计划 `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_PRETRAIN_PLAN.html`。

---

## 已定前提（固定，不要更改）

| 项 | 值 |
|:---|:---|
| 规模 | 500–600M / 架构（实测 `numel()`，±10% 内） |
| 四个候选架构 | **OpenVision 2**（纯 Attention）/ **MambaEye**（视觉 SSM）/ **MoE-ViE**（稀疏 MoE）/ **DeepEncoder V2**（Attention+SSM 混合） |
| **BASE_DIR** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027` |
| 训练栈 | **OpenCLIP（open_clip 3.2.0）**，SigLIP/CLIP 对比学习，固定 text tower（只动 vision tower）；torchrun 直驱 |
| 训练数据 | LLaVA-OneVision-1.5（parquet）或 GPIC（tar），切一个**统一固定子集**供四架构复用 |
| 环境 | conda env `py310`（CUDA 12.8 / PyTorch 2.8.0 / torchvision 0.23.0 / open_clip 3.2.0 / timm 1.0.3 / mamba_ssm 2.2.6.post3 / flash_attn 2.8.4 / webdataset） |
| GPU | `10.239.2.12` **前 6 卡（GPU 0–5，已实测空闲）**；GPU 6–7 被占（~72GB），如显存不够可杀后两卡进程（杀前先确认占用者） |
| **预算上限** | **24 小时墙钟**（按 P0 > P1 > P2 > P3 优先级裁剪，见「时间估计」） |

> 数据路径：
> - LLaVA-OneVision：`/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/`（子集 imagenet/laioncn/datacomp1b/coyo/mint/obelics × EN/CN，parquet 图像+caption）
> - GPIC：`/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/`（tar 内 `{key}.json`+`{key}.jpg/png`，caption 分 tag/short/medium/long）
---

## 试验矩阵（S0–S9，按 P0→P1→P2→P3 优先级推进）

> **锚点原则（关键）**：先跑完 S0–S2 锁定「默认配置 + 胜出架构」，再以该配置为**锚点**做单变量扫描（S3+），避免过早并行把预算烧在低信息维度。所有新增试验延续「单变量、锚点对照」的公平口径。

### P0 基础（必做）：三项硬指标

| 阶段 | 内容 | 规模 | 产出 |
|:---|:---|:---|:---|
| S0 冒烟 | 4 架构 × 10–20 步 | 10–20 步/架构 | 可跑性 + 实测参数量 + 吞吐基线 |
| S1 主训练 | 4 架构 × 1000 步（默认配置） | 1000 步/架构 | loss 曲线 + image/s |
| S2 推理基准 | 4 架构 | batch=1 前向 | 图像→token/s |

**默认配置（S1 锚点，后续消融的对照基线）**：cls=224、patch=16、SigLIP、统一子集（如 LLaVA-OneVision imagenet-EN 前 100–200 万对 或 GPIC 1–2 tar + medium caption）、text tower=同一 small transformer、lr=1e-3、warmup+cosine、seed=1234、bf16。

### P1 稳健（优先）：让排名可信

| 阶段 | 内容 | 规模 |
|:---|:---|:---|
| S3 长地平线 | **胜出架构**（+可并列次优）延长训练，看 loss 排名是否翻转 | 5000–10000 步 |
| S4 多种子 | **决胜局**（前 2 架构）多 seed 复现 | 3 seed × 1000 步 |
| S5 下游代理 | zero-shot top-1（ImageNet 或适配 val）或 text→image retrieval R@K、linear-probe | 各架构 1 次 |

### P2 核心自由度（论文重点，锚点单变量扫描）

| 阶段 | 变量 | 取值 |
|:---|:---|:---|
| S6 分辨率 + patch | cls / patch | cls ∈ {224, 336, 448}；patch ∈ {14, 16}（各 1000 步） |
| S7 目标函数 + 数据侧 | 对比目标 / caption 粒度 / 规模 / 语言 | SigLIP vs CLIP InfoNCE；GPIC tag/short/medium/long；子集扩到千万级；中英比例 |

### P3 训练超参与推理深度（有余量才做）

| 阶段 | 变量 | 取值 |
|:---|:---|:---|
| S8 训练超参 | LR / warmup | lr ∈ {1e-3, 3e-3, 5e-3}；warmup 档位 |
| S9 推理深挖 | batch / 量化 / 分辨率 / SGLang | batch ∈ {1,8,32}；bf16 vs fp8；多分辨率；装 SGLang 补生产级吞吐 |

`EXPERIMENTS_VISION.md` 建议表头：
`| ID | 阶段 | 架构 | 参数量 | 变量 | 状态 | 最终loss | 训练image/s | 推理token/s | 耗时 | GPU·h | 备注 |`
---

## 四个必须遵守的关键决策

### 决策 1：统一「从零」——四架构均随机初始化
四架构均**随机初始化**，不加载任何 ImageNet/CLIP/SigLIP 上游权重（禁用 timm/open_clip 的 pretrained 入口）。仅对比架构本体。

### 决策 2：统一训练栈与目标函数
- 统一 **open_clip（3.2.0）** 训练栈：自定义 vision tower 注册到 open_clip + 固定 text tower；Mamba/MoE 层需手写模型（mamba_ssm 2.2.6 已装，可直接用）。
- 同一对比目标：**SigLIP**（sigmoid 对比，推荐）或 CLIP InfoNCE（默认选 SigLIP；S7 可做两者 A/B）。
- 同一 text tower（固定同一 small transformer + 同一 BPE，四架构共用，只动 vision tower）。
- 同一分辨率 / patch / 增强（除 S6 显式消融外）。

### 决策 3：参数量对齐 500–600M
四架构实测参数量（`sum(numel())`）须落 500–600M；偏差 >10% 需在报告注明「非等参对比」。MoE 需同时报告「总参数」与「每 token 激活参数」。

### 决策 4：推理基准——SGLang 未装，退化到统一前向 bench
⚠️ **已实测 `sglang` 未装**（`import sglang` ModuleNotFoundError）。**P0 主口径退化为统一前向 benchmark 脚本**（`torch.cuda.Event` / `torch.benchmark`），四架构同一代码路径、同一 batch=1 / 固定分辨率 / bf16 测量图像→token/s。相对结论可信；**S9 阶段可选择性安装 SGLang**（MLLM Stage iv 反正要用）补生产级吞吐，并在报告注明测量栈。
---

## 推进状态机（PHASE，按 S0→S9 顺序，每阶段前核对预算）

- **S0 data_check + smoke**：确认可用数据子集（选 LLaVA-OneVision 一段 或 GPIC 1–2 tar），验证 caption 可读、可切图像-文本对；`conda activate py310` 后确认 open_clip / mamba_ssm / flash_attn / webdataset 可 import、GPU 0–5 可见；落地 4 个 vision tower（open_clip 注册），跑 10–20 步冒烟，记录实测参数量 + 吞吐（image/s），参数量调平到 500–600M。某架构连续 3 次失败标记 `❌ NOT_RUNNABLE` 跳过 → `S1`
- **S1 main**：4 架构 × 1000 步（默认配置），记录 loss + image/s → `S2`
- **S2 infer**：统一前向 bench 测各架构图像→token/s（batch=1、固定分辨率）→ 汇总三指标，**确定胜出架构 + 默认配置锚点** → `S3`
- **S3 long_horizon**：胜出架构（+可并列次优）延长 5000–10000 步，看排名是否翻转 → `S4`
- **S4 multi_seed**：决胜局（前 2 架构）3 seed × 1000 步复现 → `S5`
- **S5 downstream**：zero-shot top-1（open_clip 内置 `/ val-data`）或检索 R@K、linear-probe → `S6`
- **S6 scale_ablation**：cls ∈ {224,336,448}、patch ∈ {14,16}（锚点单变量，各 1000 步）→ `S7`
- **S7 objective_data**：SigLIP vs CLIP；GPIC caption 粒度；子集规模；中英比例 → `S8`
- **S8 hparam**：lr ∈ {1e-3,3e-3,5e-3}、warmup 档位 → `S9`
- **S9 infer_deep**：batch ∈ {1,8,32}、bf16 vs fp8、多分辨率；（可选）装 SGLang 补生产级吞吐 → `converged`
- **converged**：汇总各阶段对比表 + 胜出架构 + 可复现命令到 EXPERIMENTS_VISION.md 顶部；生成 HTML 结果报告；回填 `6_vision_encoder.tex`；git commit + push；停止新实验

> **预算守卫**：每阶段启动前核对 `BUDGET_USED`（≤ 24h）。逼近上限时按 P3 → P2 → P1 逆序裁剪（P0/P1 必保），并在 EXPERIMENTS_VISION.md 注明裁剪决策。
---

## 记忆管理

- `run/MEMORY_VISION.md` — 运行时状态（PHASE/WAITING/ERROR_COUNT/BUDGET_USED/看板/流水）
- `run/EXPERIMENTS_VISION.md` — 实验记录表（核心产出）
- `run/daily-memories-vision/$(date +%F).md` — 当日操作日志

启动恢复：读 MEMORY_VISION → EXPERIMENTS_VISION → 当日日志 → 判断下一步 → 执行 → 回写。

---

## GPU 资源与进程管理

- 主节点 `10.239.2.12`，用 **GPU 0–5**（已实测空闲 0 MiB）。
- 检查占用：`ssh 10.239.2.12 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'`
- 只杀本项目残留（`pgrep -af 'torchrun|open_clip_train|open_clip|pretrain'`），杀前记 PID 到 MEMORY_VISION 流水；**不杀他人进程**。GPU 6–7 被他人占 ~72GB，非本项目，默认不动；确需扩展先确认 pid 归属再 kill。
- 卡数对齐：四架构须同卡数（6 卡 TP1/DP6），训练 image/s 才可比。

---

## 时间估计（24 小时墙钟，量级 + 以冒烟实测反推）

| 优先级 | 阶段 | 内容 | 估时（串行 6 卡） |
|:---|:---|:---|:---|
| P0 | S0–S2 | 冒烟 + 主训练 + 推理基准（4 架构） | 2–4 h |
| P1 | S3–S5 | 长地平线 + 多种子 + 下游代理 | 3–6 h |
| P2 | S6–S7 | 分辨率/patch + 目标函数/数据 | 4–8 h |
| P3 | S8–S9 | LR/warmup + 推理深挖 + SGLang | 2–6 h |
| — | 余量/重试 | OOM / 报错重跑 / 抖动 | 2–4 h |
| **合计** | S0–S9 | — | **约 13–28 h，上限 24 h** |

> 反推口径：S0 冒烟读 steady-state `ms/iter → image/s → N 步 ETA = N × ms/iter / 1000`。每阶段启动前用实测吞吐校准该阶段 ETA；若逼近 24h 上限，按「预算守卫」裁剪低优先级阶段（P3 → P2 → P1 逆序），并在 EXPERIMENTS_VISION.md 记录。

---

## 验收产出

1. 胜出架构 + 完整可复现训练命令（写 `EXPERIMENTS_VISION.md` 顶部）
2. `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html`（自包含：四架构 loss/训练/推理对比 + 稳健性 + 消融 + 胜出结论 + 命令）
3. 回填 `ISEDA2027/6_vision_encoder.tex` 的 config/results（表格与文字）
4. git commit + push（只提交 `doc/` 文本 md/html/sh/json；checkpoint/图像中间产物不入库）