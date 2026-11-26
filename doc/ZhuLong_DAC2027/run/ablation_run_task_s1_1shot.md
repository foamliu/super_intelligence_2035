# EDA S1 保真度消融评测自动推进任务书（1-shot 探路版）

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_s1_1shot.md` 和 `daily-memories/`。

你是推进 EDA S1 保真度消融（Ω 文档轴 + readback 回读轴）的自动化 agent。每次被唤醒，**只做一步**：
读 `MEMORY_s1_1shot.md` 恢复当前状态 → 读 `daily-memories/$(date +%F).md` 恢复当日上下文 → 判断下一步 → 执行 → 更新 `MEMORY_s1_1shot.md` 和当日流水 → 立刻退出。

不要 sleep/等待（外层循环脚本负责间隔）。执行 shell 命令直接调用工具，不要调用任何 MCP 工具。

---

## 记忆管理（agent 按此流程维护）

- `MEMORY_s1_1shot.md` — 持久运行时状态文件，由 agent 维护（不提交 git）
  - 内容：当前状态（CONFIG/ROUND/PHASE/ERROR_COUNT）、执行看板、成绩记录、操作流水
  - 启动时读取恢复上下文，操作后写入更新
- `daily-memories/` — 每日操作日志目录（不提交 git）
  - 文件：`daily-memories/$(date +%F).md`，每天一个文件
  - 每次操作后追加一条带时间戳的记录到当日文件

### 启动恢复流程

```
1. 读取 MEMORY_s1_1shot.md → 获取 CONFIG/ROUND/PHASE/ERROR_COUNT、看板、成绩、流水
2. 读取 daily-memories/$(date +%F).md（如存在）→ 获取当日操作上下文
3. 根据 PHASE 执行推进逻辑
```

### 操作完成写入流程

```
1. 更新 MEMORY_s1_1shot.md 中的：当前状态、执行看板、成绩记录、操作流水
2. 追加一条记录到 daily-memories/$(date +%F).md
```

---

## 背景（固定，不要改动）

- 评测代码根目录: `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`
- 论文目录: `/nasdata/app.e0031982/code/ZhuLong_DAC2027`（论文权威树）
- 基座: `deepseek-v4-pro-fp4`（默认，不要动 cline auth / models.json / providers.json）
- 评测协议: Pass@1、单次无 retry；一律 `-p 8 -n`（8 并发 + 禁 Memory Bank 注入）
- **反作弊 PreToolUse hook 全程启用、所有臂完全一致（冻结变量，不是消融对象）**
- `cimi_search` / `cimi_fetch` / `vqa` 永远关闭，不要碰
- self-exploration（(H+E) 档）、Φ 预算（S2）、检索 index 重建（RQ4）——**本轮不做**

---

## 消融计划总览

S1 = 两条单轴阶梯。本轮 1-shot 探路，只跑「新出现」的 3 臂：

| 轴 | 臂 | 配置（改什么） | README 表 | 状态 |
|:---|:---|:---|:---|:---|
| Ω 文档轴 | (N) | `pure_llm` 核心 4 全关 | `tab:omega` (N) | ✅ 11.4% |
| Ω 文档轴 | (L) | `omega_low`：search 只回名字+相似度 | `tab:omega` (L) | ⬜ 本轮 |
| Ω 文档轴 | (H) | `full` 默认 | `tab:omega` (H) | ✅ 84.8% |
| Ω 文档轴 | (H+E) | + 离线自探索结论 | `tab:omega` (H+E) | ⏸ 不做 |
| readback 轴 | (N) | `readback_none`：run_code 只回“已执行” | `tab:ablation-harness` (N) | ⬜ 本轮 |
| readback 轴 | (B) | `readback_binary`：run_code 只回过/不过 | `tab:ablation-harness` (B) | ⬜ 本轮 |
| readback 轴 | (F) | `full` 默认 | `tab:ablation-harness` (F) | ✅ 84.8% |

**执行顺序**：`omega_low` → `readback_binary` → `readback_none`，各 1 轮。

---

## 代码前置依赖（⚠️ 跑之前必须已实现，否则切配置会静默失效）

1. `server/rag_server/query_knowledge.py`：`search_apis()` / `search_apis_by_keyword()` 支持
   `EDA_OMEGA_FIDELITY=low`——返回剥离 `description`、跳过 BM25 补充、跳过双向缩写展开与同义词重定向，只留 name+similarity。
2. `tools/run_code.py`：支持 `EDA_RUNCODE_READBACK=binary|none`——binary=只回 PASS/FAIL；none=只回 `executed`；
   两者均不返回 error_log/print_log/result。
3. `scripts/set_s1_fidelity.py <ARM>`：先确保核心 4 工具全开（等价 `set_ablation.py full`），
   再写上述两个 flag 到 `.env`（缺省 high/full）。ARM ∈ {omega_low, readback_binary, readback_none}。

---

## 开跑前 canary（README §8 强制，每批做一次）

首次唤醒且 PHASE=init 时，先验证反作弊 hook 生效：
故意触发一次应被拒绝的调用（`run_commands`，或读工作区外路径），确认它真的被拒。
**若未被拒 → 立即停止，本批数据作废，退出。** 通过后 PHASE→running，启动第一臂 `omega_low`。

---

## 固定命令

> 所有 `cd` 用 `BASE_DIR` 展开；`<ARM>` 替换为臂名（omega_low / readback_binary / readback_none）。

### 切换 S1 臂
```bash
cd $BASE_DIR
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>
bash scripts/stop.sh
bash scripts/start.sh
sleep 3
tail -20 $BASE_DIR/logs/app.log
```
核对：核心 4 工具 visibility 正常、对应 flag 生效。

### 启动一轮
```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<ARM>_r1.log 2>&1 < /dev/null &
```
注：工具可能显示超时/无输出，但进程已脱离，不要当成失败；启动后不要重复启动同一轮。

### 检查本轮是否结束
```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```
- 有输出 → 评测进程还在跑（本轮未结束），什么都不做，退出
- 无输出 → 评测进程已退出（本轮已结束，可打分）

### 打分
```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<ARM>_r1.log | tail -5
```
以 log 内 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评、会超时，不用它做口径。

---

## 推进逻辑（每次被唤醒严格只走一步）

### 前置校验

无论何种 PHASE，先做：
1. 读 `MEMORY_s1_1shot.md` 中「记忆流水」最后 3 条，检查是否有 `❌ EVAL_FAILED` 或 `⚠️` 异常尚未处理
2. 若有未处理的异常 → 优先执行重试逻辑（重新打分或重启本轮），写入流水中，再按正常流程推进

### 步骤 A（PHASE=running）

执行「检查本轮是否结束」：
- **pgrep 有输出**（还在跑）→ 什么都不做，退出
- **pgrep 无输出**（本轮结束）→ 执行「打分」，提取 pass 百分比：
  - 成功 → 更新执行看板（勾选当前项 + 记录分数）、成绩记录、流水；PHASE=just_finished；追加当日流水 → 退出
  - 失败（无输出/格式异常）→ 流水追加 `❌ EVAL_FAILED`，`ERROR_COUNT+=1`：
    - 若 `ERROR_COUNT < 3` → 本轮重打分，成功则按正常流程
    - 若 `ERROR_COUNT >= 3` → 标记看板当前项为 ❌，追加流水后强制推进到下一臂

### 步骤 B（PHASE=just_finished）

```
ROUND < 1 → 启动下一轮（ROUND+1），PHASE→running
（1-shot 模式下 ROUND < 1 不会发生，保留以保持逻辑一致性）

ROUND == 1 且 CONFIG != readback_none → 切换到下一臂，CONFIG→下一个、ROUND=1、PHASE=running，启动该臂第 1 轮
ROUND == 1 且 CONFIG == readback_none → 写「S1 保真度探路 3 臂完成」，PHASE→done_all
```

更新 `MEMORY_s1_1shot.md` 中的当前状态和看板，追加当日流水。

### 步骤 C（PHASE=done_all）

什么都不做，退出。