# EDA S2 Φ 轴消融评测自动推进任务书（1-shot 探路版）

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_s2_1shot.md` 和 `daily-memories/`。

你是推进 EDA S2 Φ 轴消融（k 预算 + lagged 滞后）的自动化 agent。每次被唤醒，**只做一步**：
读 `MEMORY_s2_1shot.md` 恢复当前状态 → 读 `daily-memories/$(date +%F).md` 恢复当日上下文 → 判断下一步 → 执行 → 更新 `MEMORY_s2_1shot.md` 和当日流水 → 立刻退出。

不要 sleep/等待（外层循环脚本负责间隔）。执行 shell 命令直接调用工具，不要调用任何 MCP 工具。

---

## 记忆管理（agent 按此流程维护）

- `MEMORY_s2_1shot.md` — 持久运行时状态文件，由 agent 维护（不提交 git）
  - 内容：当前状态（CONFIG/ROUND/PHASE/ERROR_COUNT）、执行看板、成绩记录、操作流水
  - 启动时读取恢复上下文，操作后写入更新
- `daily-memories/` — 每日操作日志目录（不提交 git）
  - 文件：`daily-memories/$(date +%F).md`，每天一个文件
  - 每次操作后追加一条带时间戳的记录到当日文件

### 启动恢复流程

```
1. 读取 MEMORY_s2_1shot.md → 获取 CONFIG/ROUND/PHASE/ERROR_COUNT、看板、成绩、流水
2. 读取 daily-memories/$(date +%F).md（如存在）→ 获取当日操作上下文
3. 根据 PHASE 执行推进逻辑
```

### 操作完成写入流程

```
1. 更新 MEMORY_s2_1shot.md 中的：当前状态、执行看板、成绩记录、操作流水
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
- S2 只动「Φ 信念更新」：k 预算（hook 层）与 lagged 滞后（handler 层）。**观测 Ω 与先验 K 不变**

---

## 消融计划总览

S2 = 一条锚点 + 三条 k 预算 + 一条 lagged。本轮 1-shot 探路，跳过锚点（=full 基线），只跑 4 个新臂：

| 臂 | 配置（改什么） | README 表 | 状态 |
|:---|:---|:---|:---|
| `Φ unbounded` | 无预算上限（≡ full 基线） | `tab:phi-bound` unbounded | ✅ 84.8%（=full，跳过不跑） |
| `Φ k=10` | hook 限 run_code ≤10 次 | `tab:phi-bound` k=10 | ⬜ 本轮 |
| `Φ k=3` | hook 限 run_code ≤3 次 | `tab:phi-bound` k=3 | ⬜ 本轮 |
| `Φ k=1` | hook 限 run_code ≤1 次 | `tab:phi-bound` k=1 | ⬜ 本轮 |
| `Φ lagged` | handler 返回上一拍状态（L=1） | `tab:phi-bound` lagged | ⬜ 本轮 |

**执行顺序**：`k=10` → `k=3` → `k=1` → `lagged`，各 1 轮。
理由：先 k=10（预算宽松，用来验证 hook 计数正确、不误杀），再逐档收紧到 k=1，最后跑机制独立的 lagged。

---

## 语义约束（⚠️ S2 最容易做错，务必逐字遵守）

1. **预算约束的是「agent 能执行/能观测多少次」，绝不是「agent 何时必须提交」。**
2. 实现方式是**在工具边界拒绝调用**（agent 收到 error 后继续自主运行），
   **严禁**中断 trace、改写任务、或以任何方式逼迫/提示 agent 提前提交。
   ——一旦改变终止行为，测到的就是「人为干预」而非 Φ。
3. **必须同时报告 `Converged (%)`**（=`finish_reason == completed` 的 trace 占比），
   否则紧预算造成的提前停止会被误读为「收敛」。报数时 `Converged (%)` 紧挨 Pass@1。
4. `lagged` 定义 = **滞后 1 次执行**：第 n 次 `run_code` 返回第 n−1 次的状态，第 1 次返回
   「尚无先前状态」占位（占位，不是空错误）。用**单槽缓冲**（不是队列），并在元数据记录
   `reported_call_index` 以便审计滞后量恰好 = 1。
5. **预算 hook 的错误信息必须带唯一前缀 `[PHI-BUDGET-EXHAUSTED]`**——反作弊 hook 与预算 hook
   的拒绝原因会被换行拼接，无前缀就无法区分是哪条 hook 拒的（归因会错标）。
6. 若 L=1 测不出效应，再上 L=2，并在正文如实报告「L=1 无效应」；本轮探路先用 L=1。
---

## 你需要实现的脚本（首个唤醒周期完成；这些文件当前尚不存在，由你实现）

> 现状：`scripts/set_ablation.py` 与反作弊 `scripts/cline_hooks/PreToolUse` **已存在**；
> `scripts/set_s2_phi.py`、预算 hook 逻辑、`tools/run_code.py` 的 lagged 逻辑 **尚不存在**。
> 因此本轮第一个唤醒周期（PHASE=init）必须由你**自己实现**以下脚本，自测通过后才开始跑分；否则切配置会静默失效。
> 实现方式用 shell heredoc（`cat > file <<'EOF' ... EOF`）写文件、或你自己的文件编辑工具皆可；**但不要调用任何 EDA MCP 工具**（search_apis / get_api_details / run_code）。

1. `scripts/cline_hooks/PreToolUse`（已存在，**在反作弊逻辑之外追加** Φ 预算计数，不得破坏反作弊）：
   同一 trace 内对 `run_code` 调用计数（按 session/trace id 归零），超 k 时返回
   `{"cancel": true, "errorMessage": "[PHI-BUDGET-EXHAUSTED] k=<N>"}`；拒绝需落到 trace 元数据的
   `denied_by_hook` / `deny_reason`。
2. `tools/run_code.py`（已存在，追加 lagged 逻辑，缺省关闭）：支持 `EDA_PHI_LAGGED=1`——
   单槽缓冲返回上一拍状态（第 1 次回「尚无先前状态」占位），并记录 `reported_call_index`；
   `EDA_PHI_LAGGED` 缺省为 0（关闭）。
3. `scripts/set_s2_phi.py`（不存在，**新写**，模仿 `scripts/set_ablation.py` 风格）：ARM ∈ {phi_unbounded, phi_k10, phi_k3, phi_k1, phi_lagged}。
   写 `.env`（`EDA_PHI_BUDGET=<N>` / `EDA_PHI_LAGGED=0|1`），并启用/停用预算 hook；缺省 unbounded（不设限）。
4. trace 元数据须采集：`finish_reason`、`run_code_calls`、`denied_by_hook`、`deny_reason`、`reported_call_index`
   （README §4）。否则 `Converged (%)` 与滞后量无法核对；若 harness 现有采集点不足，在本次实现时一并补齐。

---

## 脚本自测 + canary（在 PHASE=init 内完成；不通过 → 修复后重试，上限 3 次）

实现完脚本后、启动任一评测前，先自测 + canary：
0. 脚本语法自测：`python -m py_compile scripts/set_s2_phi.py scripts/cline_hooks/PreToolUse tools/run_code.py`；
   跑一次 `$BASE_DIR/venv/bin/python scripts/set_s2_phi.py phi_k10`，再 `grep -E 'EDA_PHI_BUDGET|EDA_PHI_LAGGED' $BASE_DIR/.env` 确认写入，并 `bash scripts/stop.sh && bash scripts/start.sh` 重启生效。
1. 故意触发一次应被拒绝的调用（`run_commands`，或读工作区外路径），确认反作弊 hook **真的被拒**。
   **若未被拒 → 立即停止，本批数据作废，退出。**
2. 额外确认「预算 hook 与反作弊 hook 能并存且拒绝原因可区分」：故意让 `run_code` 超预算一次，
   核对 `deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]`、且不与反作弊拒绝混淆（§3.4）。
3. 全部通过 → PHASE→running，启动第一臂 `k=10`；任一失败 → 修复 → 重试（上限 3 次），
   超过 3 次仍失败 → 流水记 `❌ BLOCKED` → 退出等待人工介入。

---

## 固定命令

> 所有 `cd` 用 `BASE_DIR` 展开；`<ARM>` 替换为臂名（k10 / k3 / k1 / lagged）。

### 切换 S2 臂
```bash
cd $BASE_DIR
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>
bash scripts/stop.sh
bash scripts/start.sh
sleep 3
tail -20 $BASE_DIR/logs/app.log
```
核对：核心 4 工具 visibility 正常（full 配置）、`EDA_PHI_BUDGET` / `EDA_PHI_LAGGED` 已写入、预算 hook 已装载。

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

### 打分（Pass@1 + S2 专属核对项）
```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<ARM>_r1.log | tail -5
```
以 log 内 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评、会超时，不用它做口径。

S2 专属核对（记入成绩记录，缺一不可）：
- `Converged (%)`：trace 中 `finish_reason == completed` 占比（须紧挨 Pass@1 记录）。
- k 臂（k10/k3/k1）：统计 `deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 > 0（证明预算 hook 确实拒过），
  并记录 `run_code_calls` 均值（`Mean read-backs`）。
- lagged 臂：核对 `reported_call_index` 与真实调用序号的差 == 1（滞后量恰好为 1），否则该臂数据作废。

---

## 推进逻辑（每次被唤醒严格只走一步）

### 前置校验

无论何种 PHASE，先做：
1. 读 `MEMORY_s2_1shot.md` 中「记忆流水」最后 3 条，检查是否有 `❌ EVAL_FAILED` 或 `⚠️` 异常尚未处理
2. 若有未处理的异常 → 优先执行重试逻辑（重新打分或重启本轮），写入流水中，再按正常流程推进

### 步骤 0（PHASE=init 首次唤醒；若 MEMORY_s2_1shot.md 不存在或 PHASE 为空，也按 init 处理）

1. 按「你需要实现的脚本」一节，**自己实现** 4 项（新写 `set_s2_phi.py`、追加预算 hook、追加 lagged、补齐元数据采集）。
2. 按「脚本自测 + canary」一节的 0/1/2 逐项自测。
3. 通过 → 用「固定命令」切到 `phi_k10` 并启动第一轮，PHASE→running，更新看板/流水 → 退出。
4. 任一自测失败 → 修复后重试（上限 3 次）；超上限 → 流水记 `❌ BLOCKED` → 退出等待人工介入。

### 步骤 A（PHASE=running）

执行「检查本轮是否结束」：
- **pgrep 有输出**（还在跑）→ 什么都不做，退出
- **pgrep 无输出**（本轮结束）→ 执行「打分 + S2 专属核对」，提取 pass 百分比：
  - 成功（Pass@1 提取成功，且 S2 核对项齐全）→ 更新执行看板（勾选当前项 + 记录分数/Converged）、成绩记录、流水；PHASE=just_finished；追加当日流水 → 退出
  - 失败（无输出/格式异常/核对项缺失）→ 流水追加 `❌ EVAL_FAILED`，`ERROR_COUNT+=1`：
    - 若 `ERROR_COUNT < 3` → 本轮重打分（含核对项），成功则按正常流程
    - 若 `ERROR_COUNT >= 3` → 标记看板当前项为 ❌，追加流水后强制推进到下一臂

### 步骤 B（PHASE=just_finished）

```
ROUND < 1 → 启动下一轮（ROUND+1），PHASE→running
（1-shot 模式下 ROUND < 1 不会发生，保留以保持逻辑一致性）

ROUND == 1 且 CONFIG != lagged → 切换到下一臂，CONFIG→下一个、ROUND=1、PHASE=running，启动该臂第 1 轮
  （轮转顺序: k10 → k3 → k1 → lagged）

ROUND == 1 且 CONFIG == lagged → 写「S2 Φ 轴探路 4 臂完成」，PHASE→done_all
```

更新 `MEMORY_s2_1shot.md` 中的当前状态和看板，追加当日流水。

### 步骤 C（PHASE=done_all）

什么都不做，退出。