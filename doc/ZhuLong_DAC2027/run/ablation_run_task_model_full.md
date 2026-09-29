# EDA 模型消融自动推进任务书（完整 5-run 版）

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_model_full.md` 和 `daily-memories/`。

你是推进 EDA 模型消融的自动化 agent。每次被唤醒，**只做一步**：
读 `MEMORY_model_full.md` 恢复当前状态 → 读 `daily-memories/$(date +%F).md` 恢复当日上下文 → 判断下一步 → 执行 → 更新 `MEMORY_model_full.md` 和当日流水 → 立刻退出。

不要 sleep/等待（外层循环脚本负责间隔）。执行 shell 命令直接调用工具，不要调用任何 MCP 工具。

---

## 记忆管理（agent 按此流程维护）

- `MEMORY_model_full.md` — 持久运行时状态文件，由 agent 维护（不提交 git）
  - 内容：当前状态（MODEL/ROUND/PHASE/ERROR_COUNT）、执行看板、成绩记录、操作流水
  - 启动时读取恢复上下文，操作后写入更新
- `daily-memories/` — 每日操作日志目录（不提交 git）
  - 文件：`daily-memories/$(date +%F).md`，每天一个文件
  - 每次操作后追加一条带时间戳的记录到当日文件

### 启动恢复流程

```
1. 读取 MEMORY_model_full.md → 获取 MODEL/ROUND/PHASE/ERROR_COUNT、看板、成绩、流水
2. 读取 daily-memories/$(date +%F).md（如存在）→ 获取当日操作上下文
3. 根据 PHASE 执行推进逻辑
```

### 操作完成写入流程

```
1. 更新 MEMORY_model_full.md 中的：当前状态、执行看板、成绩记录、操作流水
2. 追加一条记录到 daily-memories/$(date +%F).md
```

---

## 背景（固定，不要改动）

- 评测代码根目录: `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`
- 论文目录: `/nasdata/app.e0031982/code/ZhuLong_DAC2027`
- 评测协议: 完整 5-run，Pass@1 报告 **mean ± std**（5 轮）；每轮用 `-p 8 -n`（8 并发 + 禁 Memory Bank 注入）
- `cimi_search` / `cimi_fetch` / `vqa` 三个工具永远关闭，不要碰
- w/o Self-Exploration 消融暂不做，不要碰
- **所有模型均使用 full 配置**（检索开 + sandbox 开，默认配置，不切 set_ablation）

---

## 模型消融计划

| 序号 | 模型名 | `cline auth` 命令 | 启动 `-m` 参数 | 轮数 |
|:---:|:---|---:|---:|:---:|
| 1 | `GLM-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` | `-m glm-5.2` | 5 |
| 2 | `DeepSeek-V4-Flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` | `-m deepseek-v4-flash` | 5 |
| 3 | `Kimi-K2.6-Cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` | `-m kimi-k2.6-cloud` | 5 |
| 4 | `Doubao-Seed-2.0-Pro-Cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` | `-m doubao-seed-2.0-pro-cloud` | 5 |

> 主基座 `deepseek-v4-pro-fp4` 已有数据（~84.8%），不重跑。

`MODEL` 值使用简短标识：`glm-5.2` / `deepseek-v4-flash` / `kimi-k2.6-cloud` / `doubao-seed-2.0-pro-cloud`。

**执行顺序**：`glm-5.2` → `deepseek-v4-flash` → `kimi-k2.6-cloud` → `doubao-seed-2.0-pro-cloud`，各 5 轮。
每模型 5 轮结束后，算 mean±std 记录到成绩表，然后切下一模型。

---

## 固定命令

> 所有 `cd` 用 `BASE_DIR` 展开；`<MODEL>` 替换为模型名，`<N>` 替换为轮次（1-5）。

### 切换模型（当前模型 5 轮完成后，切到下一个模型前执行）
```bash
cd $BASE_DIR
# 执行对应模型的 cline auth 命令
cline auth -p openai -k <API_KEY> -b <BASE_URL> -m <MODEL_ID>
```

### 启动一轮
```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<MODEL>_r<N>.log 2>&1 < /dev/null &
```
注：工具可能显示超时/无输出，但进程已脱离，不要当成失败；启动后不要重复启动同一轮。

### 检查本轮是否结束
```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```
- 有输出 → 评测进程还在跑（本轮未结束）
- 无输出 → 评测进程已退出（本轮已结束，可打分）

### 打分（单轮）
```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<MODEL>_r<N>.log | tail -5
```
以 log 内 `pass (xx.x%)` 为 Pass@1 口径。不要用 `run_eval.py --latest 1`。

---

## 推进逻辑（每次被唤醒严格只走一步）

### 前置校验

无论何种 PHASE，先做：
1. 读 `MEMORY_model_full.md` 中「记忆流水」最后 3 条，检查是否有 `❌ EVAL_FAILED` 或 `⚠️` 异常尚未处理
2. 若有未处理的异常 → 优先执行重试逻辑（重新打分或重启本轮），写入 `MEMORY_model_full.md` 的流水，再按正常流程推进

### 步骤 0（PHASE=init 首次唤醒）

1. 校验反作弊 hook 生效（canary）
2. 切到第一个模型 `glm-5.2`（执行 `cline auth`）
3. 启动 r1，PHASE→running，更新看板

### 步骤 A（PHASE=running）

执行「检查本轮是否结束」：
- **pgrep 有输出**（还在跑）→ 什么都不做，退出
- **pgrep 无输出**（本轮结束）→ 执行「打分」，提取 pass 百分比：
  - 成功 → 更新成绩记录（`<MODEL> r<N>: xx.x%`）、看板；`ROUND += 1`
    - 若 `ROUND <= 5` → 启动本轮（下一轮），PHASE 保持 running
    - 若 `ROUND > 5`（即 5 轮全部结束）→ 算 mean±std，写入成绩记录；PHASE=just_finished
  - 失败（无输出/格式异常）→ 在流水中追加 `❌ EVAL_FAILED`，`ERROR_COUNT+=1`：
    - 若 `ERROR_COUNT < 3` → 本轮重打分，成功则按正常流程
    - 若 `ERROR_COUNT >= 3` → 标记看板当前轮为 ❌，追加流水后强制推进

### 步骤 B（PHASE=just_finished）

```
当前模型不是 doubao-seed-2.0-pro-cloud →
  1. 读取模型轮转顺序，找到下一个模型
  2. 执行「切换模型」: cline auth 切换到下一个模型
  3. 更新 MODEL → 下一个模型名、ROUND=1、PHASE=running
  4. 启动该模型第 1 轮

当前模型是 doubao-seed-2.0-pro-cloud →
  写「模型消融完整 5-run 全部完成」，PHASE→done_all
```

更新 `MEMORY_model_full.md` 中的当前状态和看板，追加当日流水。

### 步骤 C（PHASE=done_all）

什么都不做，退出。

---

## 成绩记录格式（每模型 5 轮结束后写 mean±std）

```markdown
| 模型 | N=5 mean±std | 各轮原始值 |
|:---|---:|:---|
| glm-5.2 | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
| deepseek-v4-flash | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
| kimi-k2.6-cloud | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
| doubao-seed-2.0-pro-cloud | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
```

std 计算公式：`sqrt(Σ(xᵢ - μ)² / (n-1))`，n=5。保留 1 位小数。

---

## 执行看板示例

| 模型 | 轮次 | 状态 |
|:---|---:|:---:|
| glm-5.2 | 1/5 | ✅ 或 ⬜ |
| glm-5.2 | 2-5/5 | ⬜ |
| deepseek-v4-flash | 1-5/5 | ⬜ |
| kimi-k2.6-cloud | 1-5/5 | ⬜ |
| doubao-seed-2.0-pro-cloud | 1-5/5 | ⬜ |
