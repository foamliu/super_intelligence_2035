# BAIZE_PRETRAIN_TASK.md

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY.md`、`EXPERIMENTS.md` 和 `daily-memories/`。

你是推进 **BaiZe 1B LLM 架构与超参搜索** 的自动化 agent（Cline），**每小时被唤醒一次**。每次被唤醒，**只做一步**：
读 `MEMORY.md` 恢复当前状态 → 读 `EXPERIMENTS.md` 获取实验进展 → 读 `daily-memories/$(date +%F).md` 恢复当日上下文 → 判断下一步 → 执行 → 更新记忆文件 → 立刻退出。

不要 sleep/等待。执行 shell 命令直接调用工具。**允许调用 `cimi-search` 和 `cimi-fetch` 两个 web 搜索工具**，用于查找数据预处理脚本、Megatron-SWIFT 配置等公开信息。不要调用任何其他 MCP 工具。

---

## 任务目标

**探索一个最优的 1B 级 LLM 训练架构与超参数集合**，最终产出：

1. 一份**胜出配置**（架构 + 超参），在验证集 loss 或下游基准上优于其他候选
2. 一份**实验记录表**（`EXPERIMENTS.md`），包含所有试过的配置及其结果与耗时
3. 一条**可复现的训练命令**，能从头训练该胜出配置

搜索维度包括但不限于：层数、GQA 头数、MLA/标准注意力、嵌入共享、优化器、学习率、WSD 衰减比例、batch size、seq-len、μP 基座宽度、**架构类型（MiniCPM5-1B / Nemotron / Hymba）**。

---

## 记忆管理（agent 按此流程维护）

- `MEMORY.md` — 持久运行时状态文件，由 agent 维护（不提交 git）
  - 内容：当前状态（STAGE/PHASE/ERROR_COUNT/BUDGET_USED）、实验看板、操作流水
  - 启动时读取恢复上下文，操作后写入更新
- `EXPERIMENTS.md` — 实验记录表，由 agent 维护
  - 内容：每次实验的配置 ID、架构参数、超参、状态、结果（loss/吞吐/耗时）
  - 这是任务的核心产出，每次实验后必须更新
- `daily-memories/` — 每日操作日志目录（不提交 git）
  - 文件：`daily-memories/$(date +%F).md`，每天一个文件
  - 每次操作后追加一条带时间戳的记录到当日文件

### 启动恢复流程

```
1. 读取 MEMORY.md → 获取 STAGE/PHASE/ERROR_COUNT/BUDGET_USED、实验看板、流水
2. 读取 EXPERIMENTS.md → 获取所有已跑/在跑/待跑的配置及其结果
3. 读取 daily-memories/$(date +%F).md（如存在）→ 获取当日操作上下文
4. 根据 PHASE 执行推进逻辑
```

### 操作完成写入流程

```
1. 更新 MEMORY.md：当前状态、实验看板、累计预算消耗、操作流水
2. 更新 EXPERIMENTS.md：本次实验的配置、结果与耗时
3. 追加一条记录到 daily-memories/$(date +%F).md
```

---

## 背景（固定，不要改动）

- 项目名称: **BaiZe**（1B LLM）
- 训练框架: **Megatron-SWIFT**
- **BASE_DIR**: `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`
- **ms-swift 源码**: `/nas_train/app.e0031982/code/ms-swift`
- **ms-swift 版本**: **v4.5.3**
- 数据根目录: `/nas_inference/app.e0031982/datasets/openbmb/`
- 基线架构: **MiniCPM5-1B**（LlamaForCausalLM 标准架构，24 层，GQA，~1.1B 参数）
- 超参迁移: **μP（最大更新参数化）**
- 学习率调度: **WSD**，Stable 阶段学习率 = **6e-4**
- 序列长度: **4096**
- 全局 Batch Size: **1024**（单步 ~4M tokens）
- **权重衰减率: 0.1**
- **搜索预算: 20 小时**（GPU 总时长上限，所有实验累计）
- 环境（锁定，不可变更）:
  - CUDA **12.8**
  - PyTorch **2.8.0**
  - Python **3.10**
  - Conda 环境 **py310**

> **数据原则**：本任务不负责数据下载。agent 只使用数据目录中**已经下载完成**的数据子集进行训练试验，不等待、不补下、不检查未完成项。

---

## GPU 资源与进程管理

### 硬件

| 节点 | 可用 GPU | 说明 |
|:---|:---|:---|
| **10.239.2.29** | **8 张 H100** | 主训练节点 |
| **10.239.2.12** | **前 6 张 H100**（GPU 0~5） | 辅助训练节点 |
- 可能存在其他进程占用 GPU，启动实验前需检查目标节点的 GPU 空闲情况
- 节点间通过分布式通信（如 torchrun 多节点）或独立分配实验，由 agent 根据队列和资源决定

### 权限与规则

- **允许在必要时杀掉占用 GPU 的进程**，但必须遵守以下约束：
  1. **仅在启动实验前发现 GPU 资源不足时**才执行，不得在实验运行期间随意杀进程
  2. **优先杀自己项目的历史残留进程**：先识别进程命令行，确认是本项目（BaiZe / Megatron-SWIFT / swift / megatron）相关的进程再杀
  3. **不要杀其他用户的进程**：除非确认无其他可用 GPU，且已通过 `nvidia-smi` 确认占用进程属于本项目或当前用户
  4. **杀进程前必须记录**：把被杀的 PID、进程名、占用显存写入 `MEMORY.md` 流水，便于追溯

### 检查 GPU 占用（需指定目标节点）

```bash
# 主节点
ssh 10.239.2.29 nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

# 辅助节点
ssh 10.239.2.12 nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
```

### 按项目关键字识别可杀进程

```bash
# 查看占用 GPU 的进程详情（替换 <NODE_IP> 为目标节点 IP）
ssh <NODE_IP> nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader

# 查看进程完整命令行，确认是否属于本项目
for pid in $(ssh <NODE_IP> nvidia-smi --query-compute-apps=pid --format=csv,noheader); do
  echo "PID $pid: $(ssh <NODE_IP> ps -p $pid -o args= 2>/dev/null)"
done
```

### 杀进程（确认属于本项目后）

```bash
# 替换 <NODE_IP> 和目标 <PID>
ssh <NODE_IP> kill -9 <PID>
```

> **原则**：能用就先用，资源不够才清理；清理优先清自己的残留，最后才考虑其他。每次清理都要留痕。

---

## 数据清单（仅使用已下载完成的部分）

| 数据集 | 类型 | 使用条件 |
|--------|------|----------|
| UltraData-Code | 代码预训练 | 目录存在且非空即可用 |
| UltraData-Math | 数学预训练 | 目录存在且非空即可用 |
| UltraData-SFT-2605 | 指令微调 | 目录存在且非空即可用 |
| UltraData-SFT-Agent-2609 | Agent 微调 | 目录存在且非空即可用 |
| Ultra-FineWeb-L3 | 通用网页 | 目录存在且非空即可用 |

### 可用数据判定命令

```bash
DATA_DIR=/nas_inference/app.e0031982/datasets/openbmb
for d in UltraData-Code UltraData-Math UltraData-SFT-2605 UltraData-SFT-Agent-2609 Ultra-FineWeb-L3; do
  if [ -d "$DATA_DIR/$d" ] && [ "$(ls -A $DATA_DIR/$d 2>/dev/null)" ]; then
    echo "$d: AVAILABLE ($(du -sh $DATA_DIR/$d 2>/dev/null | cut -f1))"
  else
    echo "$d: NOT_AVAILABLE"
  fi
done
```

> **规则**：只要**至少一个**数据集可用，即可进入环境校验与实验流程。全部不可用才停下等待。

---

## 数据预处理（优先查本地 ms-swift 源码）

### 已知信息

- **ms-swift 源码就在本机**: `/nas_train/app.e0031982/code/ms-swift`（v4.5.3）
- **Ultra-FineWeb-L3**：parquet 格式，`original text + Q&A pairs` 拼接，token count 基于 MiniCPM5 tokenizer
- **UltraData-SFT-2605**：messages JSONL，每行 `{"messages": [{"role": "...", "content": "..."}]}`，分 think/no_think 两种 split
- **Megatron-SWIFT 标准流程**：HF→Megatron 权重转换 → Megatron 格式训练 → Megatron→HF 权重转换
- **预处理目标**：将原始数据转换为 Megatron 可读的 tokenized 格式（`.bin` + `.idx` 或 indexed dataset）

### agent 需要做的事（按优先级）

1. **优先查本地源码**（最快、最准）：
   ```bash
   ls /nas_train/app.e0031982/code/ms-swift
   find /nas_train/app.e0031982/code/ms-swift -name "*.py" | xargs grep -l "megatron" | head
   find /nas_train/app.e0031982/code/ms-swift -path "*megatron*" -name "*.md" | head
   ls /nas_train/app.e0031982/code/ms-swift/docs/source/Instruction/ 2>/dev/null
   ```
   重点看：
   - `docs/source/Instruction/Megatron-SWIFT训练.md`
   - `swift/megatron/` 或 `swift/llm/` 下的数据预处理模块
   - `scripts/` 下的数据转换脚本

2. **本地找不到时，再用 `cimi-search` / `cimi-fetch`** 搜索：
   - `ms-swift v4.5.3 megatron dataset preprocessing`
   - `MiniCPM5 pretrain data preprocessing`
   - `Ultra-FineWeb-L3 tokenize Megatron`

3. **找到后写入 `MEMORY.md`**：记录预处理脚本路径、命令、依赖

4. **找不到时**：记录 `⚠️ PREPROCESS_SCRIPT_NOT_FOUND`，尝试基于已知格式手写转换脚本，或跳过预处理直接用 Megatron-SWIFT 支持的原始格式

### 数据预处理命令（待 agent 搜索后补充）

```bash
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027
# 待 agent 查本地 ms-swift 源码后补充
```

---

## 搜索策略

### 阶段划分

| 阶段 | 目标 | 实验规模 |
|:---|:---|---:|
| **S1 基线复现** | 用基线配置跑通，建立 loss/吞吐基准 | 1 组 |
| **S2 单变量扫描** | 每次只改一个维度，定位敏感参数 | 5~8 组 |
| **S3 组合优化** | 在 S2 胜出值附近做组合与微调 | 3~5 组 |
| **S4 择优收敛** | 确认胜出配置，跑较长步数验证 | 1 组 |

### 搜索维度与候选值

| 维度 | 候选值 | 优先级 | 说明 |
|:---|:---|:---|:---|
| **架构类型** | **MiniCPM5-1B / Nemotron / Hymba** | **高** | **S2 先验证框架兼容性，只跑可用的** |
| 层数 | 24 / 28 / 32 | 高 | |
| GQA KV 头数 | 2 / 4 / 8 | 高 | |
| 注意力类型 | 标准 GQA / MLA | 中 | |
| 嵌入共享 | on / off | 高 | |
| 优化器 | AdamW / Muon（衰减阶段） | 中 | |
| Stable LR | 3e-4 / 6e-4 / 1e-3 | 高 | |
| WSD 衰减比例 | 10% / 20% | 中 | |
| Batch Size | 512 / 1024 / 2048 | 中 | |
| Seq Len | 2048 / 4096 / 8192 | 低 | |

### 实验预算控制

- 每个候选配置先跑 **200~500 steps** 的短程试验，看 loss 曲线和吞吐
- 短程胜出者才进入更长步数的验证
- 所有实验共用同一份数据子集，保证可比性

### 预算约束（20 小时硬上限）

- **总预算**：20 小时 GPU 时长，所有实验累计
- **单次短程试验**：建议 1~2 小时（对应 100~200 steps），架构验证可用更低步数
- **预算分配建议**：
  - S1 基线：1 组 × 2h = 2h
  - S2 单变量扫描（含架构对比）：3~4 组 × 2h = 6~8h
  - S3 组合优化：2 组 × 3h = 6h
  - S4 择优验证：1 组 × 2~3h = 2~3h
  - 预留缓冲：1~2h（应对失败重跑）
- **预算追踪**：每次实验结束后，在 `EXPERIMENTS.md` 记录本次实际耗时，累计消耗写入 `MEMORY.md`
- **预算耗尽处理**：当累计消耗 ≥ 20 小时，立即停止新实验，`PHASE=converged`，用当前最佳配置收敛

---

## 固定命令

> 所有 `cd` 用 `BASE_DIR` 展开。

### 进入工作目录
```bash
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027
```

### 检查可用数据
```bash
DATA_DIR=/nas_inference/app.e0031982/datasets/openbmb
ls -lh $DATA_DIR/
```

### 检查环境
```bash
conda activate py310
python -c "import torch; print(torch.__version__, torch.version.cuda)"
python -c "import megatron; print(megatron.__version__)"
```

### 检查 GPU 占用
```bash
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
```

### 查底层 megatron-core 模型支持（先于 swift 注册表检查）
```bash
# megatron-core 安装路径
MCORE=$(python -c "import megatron; print(megatron.__path__[0])" 2>/dev/null)
echo "megatron path: $MCORE"

# 查 megatron-core models 注册表
python -c "
from megatron.core import models
avail = [m for m in dir(models) if not m.startswith('_')]
print('mcore models:', avail)
"

# 找 Hymba/Nemotron 模型定义文件
find $MCORE -name "*hymba*" -o -name "*nemotron*" -o -name "*mamba*" 2>/dev/null
```

### 查本地 ms-swift 源码（若底层 megatron-core 支持，再查 swift 如何桥接）
```bash
ls /nas_train/app.e0031982/code/ms-swift
cd /nas_train/app.e0031982/code/ms-swift
git log --oneline -1 2>/dev/null
find . -path "*megatron*" -name "*.md" | head
find . -name "*.py" | xargs grep -l "preprocess\|tokenize" 2>/dev/null | head
```

### 启动一次实验
```bash
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027
setsid bash <训练脚本> --config <CONFIG_ID> > /tmp/BAIZE_<CONFIG_ID>.log 2>&1 < /dev/null &
```

### 检查实验是否结束
```bash
pgrep -f 'megatron' | head
pgrep -f 'swift' | head
```
- 有输出 → 实验还在跑，本轮什么都不做，退出
- 无输出 → 实验已结束，进入结果记录流程

### 提取实验结果
```bash
tail -50 /tmp/BAIZE_<CONFIG_ID>.log
# 提取最终 loss、tokens/sec、checkpoint 路径
```

---

## 推进逻辑（每次被唤醒严格只走一步）

### 前置校验

无论何种 PHASE，先做：
1. 读 `MEMORY.md` 中「记忆流水」最后 3 条，检查是否有 `❌` 或 `⚠️` 异常尚未处理
2. 若有未处理的异常 → 优先执行修复逻辑，写入 `MEMORY.md` 的流水，再按正常流程推进

### 步骤 A（PHASE=data_check）

执行「检查可用数据」：
- **至少一个数据集可用** → 记录可用数据集清单到 `MEMORY.md`，`PHASE=env_check`，追加流水 → 退出
- **全部不可用** → 追加流水「无可用数据，等待」，退出（不报错、不递增 ERROR_COUNT）

### 步骤 B（PHASE=env_check）

执行「检查环境」：
- **环境验证通过** → `PHASE=data_preprocess`，追加流水 → 退出
- **环境异常** → 记录 `❌ ENV_FAILED`，`ERROR_COUNT+=1`，追加流水 → 退出

### 步骤 C（PHASE=data_preprocess）

- **先查本地 ms-swift 源码**（`/nas_train/app.e0031982/code/ms-swift`）找预处理脚本
- 本地找不到 → 用 `cimi-search` / `cimi-fetch` 搜索
- 找到脚本 → 执行预处理，写入 `MEMORY.md`，`PHASE=experiment_plan`，追加流水 → 退出
- 未找到但可用原始格式 → 跳过预处理，直接进入 `PHASE=experiment_plan`，追加流水 → 退出
- 预处理未完成 → 追加流水 → 退出

### 步骤 D（PHASE=experiment_plan）

- **先检查累计 GPU 时长**：若 ≥ 20 小时 → `PHASE=converged`，追加流水 → 退出
- 读取 `EXPERIMENTS.md`，判断当前处于哪个搜索阶段（S1~S4）
- 若实验表中无任何记录 → 规划 S1 基线实验，写入 `EXPERIMENTS.md` 待跑队列，`PHASE=experiment_run`，追加流水 → 退出
- 若 S2 扫描未完成 → 从候选维度中选下一个未跑的配置，加入待跑队列，`PHASE=experiment_run`，追加流水 → 退出
- 若 S2 完成、S3 未开始 → 基于 S2 结果规划组合实验，`PHASE=experiment_run`，追加流水 → 退出
- 若 S3 完成 → 确认胜出配置，规划 S4 验证实验，`PHASE=experiment_run`，追加流水 → 退出
- 若 S4 完成 → `PHASE=converged`，追加流水 → 退出

### 步骤 E（PHASE=experiment_run）

- 检查 GPU 资源；若不足，按「GPU 资源与进程管理」规则清理本项目残留进程
- 从 `EXPERIMENTS.md` 待跑队列取出下一个配置，记录实验开始时间到 `MEMORY.md`，启动实验 → `PHASE=experiment_wait`，追加流水 → 退出

### 步骤 F（PHASE=experiment_wait）

执行「检查实验是否结束」：
- **实验仍在跑** → 什么都不做，退出
- **实验结束** → 执行「提取实验结果」：
  - 成功提取 loss/吞吐 → 计算本次实际耗时（当前时间 - 开始时间），更新 `EXPERIMENTS.md` 该配置的结果与耗时，更新 `MEMORY.md` 累计消耗，`PHASE=experiment_plan`，追加流水 → 退出
  - 提取失败 → 记录 `❌ EVAL_FAILED`，`ERROR_COUNT+=1`：
    - `ERROR_COUNT < 3` → 重试提取
    - `ERROR_COUNT >= 3` → 标记该配置为 ❌，`PHASE=experiment_plan`，追加流水 → 退出

### 步骤 G（PHASE=converged）

- 输出最终胜出配置与可复现训练命令到 `EXPERIMENTS.md` 顶部
- 什么都不做，退出

---

## Cline 执行注意事项

- **每小时只走一步**：严格按 PHASE 推进，不要在一次唤醒内连续执行多个步骤
- **启动实验后立即退出**：实验进程用 `setsid` 或 `nohup` 脱离，不要在当前会话中等待
- **判断实验是否结束**：用 `pgrep` 检查训练进程，不要依赖日志尾部
- **日志位置**：所有启动命令的 stdout/stderr 重定向到 `/tmp/BAIZE_<CONFIG_ID>.log`
- **异常处理**：连续 3 次同一步骤失败才标记 `❌` 并强制推进，否则只记录并重试
- **实验记录必须完整**：每个配置的架构参数、超参、结果、耗时都要写入 `EXPERIMENTS.md`，否则搜索无法收敛
- **预算优先**：任何规划前先确认剩余预算，避免规划超出预算的实验
- **搜索工具使用**：优先查本地 ms-swift 源码，找不到再用 `cimi-search` / `cimi-fetch`，不要滥用
- **架构类型处理**：在 S2 阶段优先安排架构类型扫描（MiniCPM5-1B / Nemotron / Hymba 各跑一组验证框架兼容性），然后才深入调参。框架不支持的架构标记为 `❌ NOT_SUPPORTED`，跳过。
- **检查顺序修正**：判断架构是否支持时，**先查底层 megatron-core 模型库**（`megatron.core.models`），再查 swift 层的 model_type/template 注册表。megatron-core 有模型定义但 swift 未暴露的，记录为 `⚠️ NOT_EXPOSED`（标记可手动桥接），而非直接 NOT_SUPPORTED。

---

## EXPERIMENTS.md 建议格式

```markdown
# BaiZe 1B 架构与超参搜索记录

## 胜出配置
（待 S4 完成后填写）

## 累计预算消耗
（待每次实验后更新，单位：小时）

## 实验记录

| ID | 阶段 | 架构 | 层数 | KV头 | 注意力 | 嵌入共享 | 优化器 | LR | Batch | SeqLen | 状态 | 最终Loss | 吞吐(tok/s) | 耗时(h) | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| S1-01 | S1 | MiniCPM5-1B | 24 | 2 | GQA | on | AdamW | 6e-4 | 1024 | 4096 | pending | - | - | - | - | 基线 |
| S2-01 | S2 | MiniCPM5-1B | 28 | 2 | GQA | on | AdamW | 6e-4 | 1024 | 4096 | pending | - | - | - | - | 层数↑ |
| S2-02 | S2 | Nemotron | 24 | 2 | GQA | on | AdamW | 6e-4 | 1024 | 4096 | pending | - | - | - | - | 架构对比 |
| S2-03 | S2 | Hymba | 24 | 2 | hybrid | on | AdamW | 6e-4 | 1024 | 4096 | pending | - | - | - | - | 架构对比 |
| ... | | | | | | | | | | | | | | | | |
```

---

## 待确认事项

1. **数据预处理脚本**：agent 优先查本地 `/nas_train/app.e0031982/code/ms-swift`（v4.5.3），找不到再用 `cimi-search` / `cimi-fetch`
2. **短程试验步数**：建议 200~500 steps
3. **UltraData-Code / UltraData-Math 层级**：使用 L2 还是 L3？
4. **单次实验时长上限**：短程试验建议不超过 2 小时，架构验证可低至 0.5 小时
5. **20 小时预算口径**：按 8 卡 × 实际运行小时（GPU·小时）计算，还是按墙上时钟计算？建议按 GPU·小时。
