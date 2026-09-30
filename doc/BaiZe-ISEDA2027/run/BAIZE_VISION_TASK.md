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
<!--MORE-->