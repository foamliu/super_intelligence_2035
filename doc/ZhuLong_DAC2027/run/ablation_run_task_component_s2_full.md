# EDA 组件消融 + S2 Φ 轴完整 5-run 自动推进任务书

> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_component_full.md` 和 `daily-memories/`。

你是推进 EDA 组件消融（Phase 1）与 S2 Φ 轴（Phase 2）的自动化 agent。每次被唤醒，**只做一步**：
读 `MEMORY_component_full.md` 恢复当前状态 → 读 `daily-memories/$(date +%F).md` 恢复当日上下文 → 判断下一步 → 执行 → 更新 `MEMORY_component_full.md` 和当日流水 → 立刻退出。

不要 sleep/等待（外层循环脚本负责间隔）。执行 shell 命令直接调用工具，不要调用任何 MCP 工具。

---

## 记忆管理（agent 按此流程维护）

- `MEMORY_component_full.md` — 持久运行时状态文件，由 agent 维护（不提交 git）
  - 内容：当前状态（PHASE/STAGE/CONFIG/ROUND/ERROR_COUNT）、执行看板、成绩记录、操作流水
  - 启动时读取恢复上下文，操作后写入更新
- `daily-memories/` — 每日操作日志目录（不提交 git）
  - 文件：`daily-memories/$(date +%F).md`，每天一个文件
  - 每次操作后追加一条带时间戳的记录到当日文件

### 启动恢复流程

```
1. 读取 MEMORY_component_full.md → 获取 STAGE/CONFIG/ROUND/PHASE/ERROR_COUNT、看板、成绩、流水
2. 读取 daily-memories/$(date +%F).md（如存在）→ 获取当日操作上下文
3. 根据 PHASE 执行推进逻辑
```

### 操作完成写入流程

```
1. 更新 MEMORY_component_full.md 中的：当前状态、执行看板、成绩记录、操作流水
2. 追加一条记录到 daily-memories/$(date +%F).md
```


## 背景（固定，不要改动）

- 评测代码根目录: `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`
- 论文目录: `/nasdata/app.e0031982/code/ZhuLong_DAC2027`
- 基座: `MODEL=deepseek-v4-pro-fp4`（主基座；已配置好，不要动 cline auth / models.json / providers.json）
- 评测协议: 完整 5-run，Pass@1 报告 **mean ± std**（5 轮）；每轮 `-p 8 -n`（8 并发 + 禁 Memory Bank 注入）
- `cimi_search` / `cimi_fetch` / `vqa` 永远关闭，不要碰
- w/o Self-Exploration / w/o Sandbox 暂不做，不要碰
- 检索策略（向量 vs grep）与索引构建消融已删除，不跑
- **反作弊 PreToolUse hook 全程启用、所有臂完全一致（冻结变量，不是消融对象）**



## 消融计划总览

### Phase 1: 组件消融（4 配置，各 5 轮）

| 序号 | 配置 | 说明 | 轮数 |
|:---:|:---|---:|---:|
| 1 | `pure_llm` | 核心 4 工具全关（裸 LLM） | 5 |
| 2 | `rag` | 检索 3 件套开、run_code 关 | 5 |
| 3 | `wo_retrieval` | 检索 3 件套关、run_code 开 | 5 |
| 4 | `full` | 检索开 + sandbox 开（主系统默认，锚点） | 5 |

> `full` 是本轮**锚点配置**：一次 5-run 同时喂饱 5 张表的锚点行——
> `tab:main-ablation`(full)、`tab:omega`(H)、`tab:ablation-harness`(F)、
> `tab:phi-bound`(unbounded ≡ full)、`tab:llm-comparison`(DeepSeek-V4-Pro 主基座)。
> 它与 Phase 2 的 `phi_unbounded` 同义，跑一次、多处引用，不重复跑。

**执行顺序**：`pure_llm` → `rag` → `wo_retrieval` → `full`，各 5 轮。

### Phase 2: S2 Φ 轴（4 臂，各 5 轮，自动衔接 Phase 1）

| 臂 | 配置（改什么） | 说明 | 轮数 |
|:---|:---|---:|---:|
| `Φ k=10` | hook 限 run_code ≤10 次 | 预算宽松作基线 | 5 |
| `Φ k=3` | hook 限 run_code ≤3 次 | 中间档 | 5 |
| `Φ k=1` | hook 限 run_code ≤1 次 | 极紧预算 | 5 |
| `Φ lagged` | 单槽缓冲回上一拍（L=1，trace_key 已修复） | 已修复+canary 通过 | 5 |

> `Φ unbounded` 跳过（≡ Phase 1 的 `full` ×5 锚点，不重复跑）。

**执行顺序**：`k=10` → `k=3` → `k=1` → `lagged(fixed)`。

---

## 语义约束（⚠️ S2 最容易做错，务必逐字遵守）

1. **预算约束的是「agent 能执行/能观测多少次」，绝不是「agent 何时必须提交」。**
2. 实现方式是**在工具边界拒绝调用**（agent 收到 error 后继续自主运行），
   **严禁**中断 trace、改写任务、或以任何方式逼迫/提示 agent 提前提交。
3. **必须同时报告 `Converged (%)`**（=`finish_reason == completed` 的 trace 占比）。
4. `lagged` 定义 = **滞后 1 次执行**：第 n 次 `run_code` 返回第 n−1 次的状态，第 1 次返回
   「尚无先前状态」占位。用**单槽缓冲**（不是队列），在元数据记录 `reported_call_index`。
5. **预算 hook 的错误信息必须带唯一前缀 `[PHI-BUDGET-EXHAUSTED]`**。
6. lagged trace_key 已在探路阶段修复（`MEMORY_s2_1shot.md` ✅ 关键缺陷已修复 #2）：`_trace_key_from_ctx()` 改用 SSE session 对象身份作 dict 键，实现 per-task 隔离。Phase 2 开始前核对该修复是否存在（`grep 'ctx.session' main.py`），若被回退则重新实施。

---


## 固定命令

> 所有 `cd` 用 `BASE_DIR` 展开。

### 切换组件消融配置（pure_llm→rag→wo_retrieval→full）
```bash
cd $BASE_DIR
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>
bash scripts/stop.sh
bash scripts/start.sh
sleep 3
tail -20 $BASE_DIR/logs/app.log
```
核对 visibility：
- `pure_llm`：核心 4 全关
- `rag`：检索 3 件套=ON、run_code=OFF
- `wo_retrieval`：检索 3 件套=OFF、run_code=ON
- `full`：检索 3 件套=ON、run_code=ON（主系统默认）

### 切换 S2 臂
```bash
cd $BASE_DIR
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>
bash scripts/stop.sh
bash scripts/start.sh
sleep 3
tail -20 $BASE_DIR/logs/app.log
```
核对：核心 4 工具全 ON、`EDA_PHI_BUDGET`/`EDA_PHI_LAGGED` 已写入。

### 启动一轮
```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```
注：工具可能显示超时/无输出，但进程已脱离，不要当成失败。

### 检查本轮是否结束
```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```
- 有输出 → 评测进程还在跑（本轮未结束），什么都不做，退出
- 无输出 → 评测进程已退出（本轮已结束，可打分）

### 打分（Pass@1；S2 臂须附加专属核对）
```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```
以 log 内 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评、会超时，不用它做口径。

S2 专属核对（Phase 2 各臂记入成绩记录，缺一不可）：
- `Converged (%)`：trace 中 `finish_reason == completed` 占比（紧挨 Pass@1 记录）。
- k 臂（k10/k3/k1）：统计 deny_reason 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 > 0，并记录 `Mean read-backs`。
- lagged 臂：核对 `reported_call_index` 与真实调用序号差 == 1（否则该臂作废）。


---

## 推进逻辑（每次被唤醒严格只走一步）

### 前置校验

无论何种 PHASE，先做：
1. 读 `MEMORY_component_full.md`「记忆流水」最后 3 条，检查是否有 `❌ EVAL_FAILED` 或 `⚠️`
2. 若有未处理异常 → 优先执行重试逻辑，按正常流程推进

### 步骤 0（PHASE=init 首次唤醒，STAGE 空或 component）

1. canary 验证反作弊 hook 生效
2. 切到 `pure_llm`，启动 r1，PHASE→running，STAGE=component，更新看板/流水

### 步骤 A（PHASE=running）

执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出
- **pgrep 无输出** → 执行「打分」：
  - 成功 → 记录成绩，`ROUND += 1`
    - `ROUND <= 5` → 启动本配置下一轮，PHASE 保持 running
    - `ROUND > 5` → 算 mean±std，PHASE=just_finished
  - 失败 → `❌ EVAL_FAILED`，`ERROR_COUNT+=1`；<3 次重试，>=3 强制推进

### 步骤 B（PHASE=just_finished）

```
STAGE=component 且 ROUND>5:
  CONFIG != full → 切到下一组件配置，ROUND=1，PHASE=running
  CONFIG == full → 「Phase 1 完成」，STAGE→phi，CONFIG→phi_k10，
     ROUND=1，PHASE=running，启动 phi_k10 r1

STAGE=phi 且 ROUND>5:
  CONFIG != phi_lagged → 切到下一 S2 臂，ROUND=1，PHASE=running，启动
  CONFIG == phi_lagged → 「全部完成」，PHASE→done_all
```

轮转：组件 → pure_llm/rag/wo_retrieval/full；S2 → phi_k10/phi_k3/phi_k1/phi_lagged。

### 步骤 C（PHASE=done_all）

什么都不做，退出。

---

## 成绩记录格式

### Phase 1 组件消融
```markdown
| 配置 | N=5 mean±std | 各轮原始值 |
|:---|---:|:---|
| pure_llm | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
| rag | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
| wo_retrieval | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
| full | xx.x ± x.x% | [r1, r2, r3, r4, r5] |
```

### Phase 2 S2 Φ 轴
```markdown
| 臂 | N=5 mean±std | Converged | Mean read-backs | 各轮 |
|:---|---:|:---|:---|:---|
| phi_k10 | xx.x ± x.x% | xx.x% | xx.x | [r1..r5] |
| phi_k3 | xx.x ± x.x% | xx.x% | xx.x | [r1..r5] |
| phi_k1 | xx.x ± x.x% | xx.x% | xx.x | [r1..r5] |
| phi_lagged | xx.x ± x.x% | xx.x% | xx.x | [r1..r5] |
```

std 公式：`sqrt(Σ(xᵢ - μ)² / (n-1))`，n=5。保留 1 位小数。

---

## 执行看板模板

### Phase 1 组件
| 配置 | 轮次 | 状态 |
|:---|---:|:---:|
| pure_llm | 1-5/5 | ⬜ |
| rag | 1-5/5 | ⬜ |
| wo_retrieval | 1-5/5 | ⬜ |
| full | 1-5/5 | ⬜ |

### Phase 2 S2 Φ
| 臂 | 轮次 | 状态 |
|:---|---:|:---:|
| phi_k10 | 1-5/5 | ⬜ |
| phi_k3 | 1-5/5 | ⬜ |
| phi_k1 | 1-5/5 | ⬜ |
| phi_lagged | 1-5/5 | ⬜ |

## Phase 2 代码前置依赖

S2 的 `scripts/set_s2_phi.py`、预算 hook、`run_code.py` lagged 逻辑预计已在探路阶段实现。
若 PHASE=init 且 STAGE=phi 时脚本缺失，agent 须自行实现（参照 `ablation_run_task_s2_1shot.md` 的规格）。
Phase 2 开始前（CONFIG 从 wo_retrieval 切到 phi_k10 时）逐一校验脚本存在且自测通过。


