# EDA S1 保真度消融 5-run 完整版自动推进任务书

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_s1_full.md` 和 `daily-memories/`。

你是推进 EDA S1 保真度消融（Ω 文档轴 + readback 回读轴）的自动化 agent。每次被唤醒，**只做一步**：
读 `MEMORY_s1_full.md` 恢复当前状态 → 读 `daily-memories/$(date +%F).md` 恢复当日上下文 → 判断下一步 → 执行 → 更新 `MEMORY_s1_full.md` 和当日流水 → 立刻退出。

不要 sleep/等待（外层循环脚本负责间隔）。执行 shell 命令直接调用工具，不要调用任何 MCP 工具。

---

## 记忆管理（agent 按此流程维护）

- `MEMORY_s1_full.md` — 持久运行时状态文件，由 agent 维护（不提交 git）
  - 内容：当前状态（CONFIG/ROUND/PHASE/ERROR_COUNT）、执行看板、成绩记录、操作流水
  - 启动时读取恢复上下文，操作后写入更新
- `daily-memories/` — 每日操作日志目录
  - 文件：`daily-memories/$(date +%F).md`，每天一个文件；每次操作后追加一条带时间戳的记录

启动恢复：读 `MEMORY_s1_full.md` 获取 CONFIG/ROUND/PHASE/ERROR_COUNT → 读当日 daily → 按 PHASE 推进。
操作完成：更新 `MEMORY_s1_full.md` 状态/看板/成绩/流水 → 追加当日流水。

---

## 背景（固定，不要改动）

- 评测代码根目录: `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`
- 论文目录: `/nasdata/app.e0031982/code/ZhuLong_DAC2027`
- 基座: `deepseek-v4-pro-fp4`（默认，不要动 cline auth / models.json / providers.json）
- 评测协议: 完整 5-run，Pass@1 报告 **mean ± std**（5 轮）；每轮 `-p 8 -n`（8 并发 + 禁 Memory Bank 注入）
- **反作弊 PreToolUse hook 全程启用、所有臂完全一致（冻结变量，不是消融对象）**
- `cimi_search` / `cimi_fetch` / `vqa` 永远关闭，不要碰
- self-exploration（(H+E) 档）、Φ 预算（S2）、检索 index 重建 —— 本轮不做

---

## 消融计划总览

S1 = 两条单轴阶梯。本轮 5-run 完整版只跑「新出现」的 3 臂，各 5 轮：

| 轴 | 臂 | 配置（改什么） | README 表 | 状态 |
|:---|:---|:---|:---|:---|
| Ω 文档轴 | (N) | `pure_llm` 核心 4 全关 | `tab:omega` (N) | ✅ 流C 已有 |
| Ω 文档轴 | (L) | `omega_low`：search 只回名字+相似度 | `tab:omega` (L) | ⬜ 本轮 ×5 |
| Ω 文档轴 | (H) | `full` 默认 | `tab:omega` (H) | ✅ 流C `full`×5 锚点 |
| Ω 文档轴 | (H+E) | + 离线自探索结论 | `tab:omega` (H+E) | ⏸ 不做 |
| readback 轴 | (N) | `readback_none`：run_code 只回“已执行” | `tab:ablation-harness` (N) | ⬜ 本轮 ×5 |
| readback 轴 | (B) | `readback_binary`：run_code 只回过/不过 | `tab:ablation-harness` (B) | ⬜ 本轮 ×5 |
| readback 轴 | (F) | `full` 默认 | `tab:ablation-harness` (F) | ✅ 流C `full`×5 锚点 |

**执行顺序**：`omega_low` → `readback_binary` → `readback_none`，各 5 轮。

> 注：(N) 档含义在两轴不同——Ω 轴的 (N)=pure_llm（流C 组件消融跑）；readback 轴的 (N)=readback_none（本轮跑）。勿混淆。

---

## 代码前置依赖（⚠️ 已实现；跑前校验，缺失则停止并报告）

1. `server/rag_server/query_knowledge.py`：`EDA_OMEGA_FIDELITY=low`（search 只回 name+similarity）。
   校验：`grep -n 'EDA_OMEGA_FIDELITY' $BASE_DIR/server/rag_server/query_knowledge.py`
2. `tools/run_code.py`：`EDA_RUNCODE_READBACK=binary|none`。
   校验：`grep -n 'EDA_RUNCODE_READBACK' $BASE_DIR/tools/run_code.py`
3. `scripts/set_s1_fidelity.py <ARM>`：先确保核心 4 工具全开（等价 set_ablation full），再写上述两个 flag 到 `.env`。
   ARM ∈ {omega_low, readback_binary, readback_none}。

---

## 开跑前 canary（README §8 强制，每批做一次）

首次唤醒且 PHASE=init 时，先验证反作弊 hook 生效：
故意触发一次应被拒绝的调用（`run_commands`，或读工作区外路径），确认它真的被拒。
**若未被拒 → 立即停止，本批数据作废，退出。** 通过后 PHASE→running，启动第一臂 `omega_low`。

---

## 固定命令

> 所有 `cd` 用 `BASE_DIR` 展开；`<ARM>` ∈ {omega_low, readback_binary, readback_none}，`<N>` 为轮次 1..5。

### 切换 S1 臂
```bash
cd $BASE_DIR
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>
bash scripts/stop.sh
bash scripts/start.sh
sleep 3
tail -20 $BASE_DIR/logs/app.log
```
核对：核心 4 工具 visibility 正常、`.env` 里 `EDA_OMEGA_FIDELITY` / `EDA_RUNCODE_READBACK` 已写入对应值。

### 启动一轮
```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<ARM>_r<N>.log 2>&1 < /dev/null &
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
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<ARM>_r<N>.log | tail -5
```
以 log 内 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评、会超时，不用它做口径。

---

## 推进逻辑（每次被唤醒严格只走一步）

### 前置校验
1. 读 `MEMORY_s1_full.md`「记忆流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`
2. 若有未处理异常 → 优先执行重试逻辑（重新打分或重启本轮），再按正常流程推进

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出**（还在跑）→ 什么都不做，退出
- **pgrep 无输出**（本轮结束）→ 「打分」：
  - 成功 → 记录成绩，`ROUND += 1`
    - `ROUND <= 5` → 启动本配置下一轮，PHASE 保持 running
    - `ROUND > 5` → 算 mean±std，PHASE=just_finished
  - 失败 → `❌ EVAL_FAILED`，`ERROR_COUNT+=1`；`ERROR_COUNT<3` 重试，`>=3` 强制推进

### 步骤 B（PHASE=just_finished）
```
CONFIG != readback_none → 切到下一臂，ROUND=1，PHASE=running，启动该臂 r1
CONFIG == readback_none → 「S1 保真度 3 臂 ×5 完成」，PHASE→done_all
```
轮转：`omega_low` → `readback_binary` → `readback_none`。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

---

## 成绩记录格式

```markdown
| 臂 | N=5 mean±std | 各轮原始值 |
|:---|---:|:---|
| omega_low (Ω L) | xx.x ± x.x% | [r1..r5] |
| readback_binary (B) | xx.x ± x.x% | [r1..r5] |
| readback_none (N) | xx.x ± x.x% | [r1..r5] |
```

std 公式：`sqrt(Σ(xᵢ - μ)² / (n-1))`，n=5。保留 1 位小数。

---

## 执行看板模板

| 臂 | 轮次 | 状态 |
|:---|---:|:---:|
| omega_low | 1-5/5 | ⬜ |
| readback_binary | 1-5/5 | ⬜ |
| readback_none | 1-5/5 | ⬜ |