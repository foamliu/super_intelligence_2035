# 运维令（建议稿）· RUN_ID 83 — 切实排查 `timeout 2500` 为何"以前有效、现在无效"

> 起草：运维（2026-10-19 18:5x）· 依据：用户指令「安排 zhulong agent 切实排查这次超时的真实根因，上报时带上根因和建议的修复方法，由运维决策」
> 状态：**待写入 `run/ops/inbox.md`（RUN_ID 82 → 83）** · 本文件仅为可追溯的指令稿 + 运维侧已掌握的初步根因（供 agent 核对/推翻）

---

## 0. 运维侧初步根因（**不是结论，是要 agent 核对的对象**）

从 `run/ops/outbox.md` 的 **RUN_ID 81** 输出（14:50:51，源码级）已可读出机制：

```
run_cli.sh:199:  local timeout_sec=2500
run_cli.sh:212|219:  timeout $timeout_sec $COMMAND -c "$ws_dir" $data_dir_flag -t $timeout_sec "$task_content" < /dev/null
run_cli.sh:228:  print_warning "[worker-${worker_slot}] 任务 $task_name 超时 (${timeout_sec}s)"
run_cli.sh:230:  increment_stat "timeout"
```

**初步判断（三条，agent 须逐条证实或推翻）**：

| # | 假设 | 现有旁证 |
|:--|:--|:--|
| **H1** | `timeout` 外层**只发 SIGTERM**、无 `-k/--kill-after`，且 `timeout` **只杀 leader 进程**（`$COMMAND` 是 node/cline 的 shell 包装，真正的 cline 是它的子孙）。cline 收到 TERM 后进入"优雅收尾"（落盘 session / 关 MCP / 写 trace），在网络 hang 时收尾本身阻塞 ⇒ 进程不死、`increment_stat timeout` 这行**永远执行不到** | r2 `task 119` 21,600s=8.6×2500；r3 `task 130` 6,582s=2.6×2500；r2 task 119 的 ws 文件 14:09 仍 +20B（进程活着在写） |
| **H2** | 双保险其实变成了"两个软墙"：外层 `timeout 2500`（SIGTERM）+ cline 自身 `-t 2500`（内部计时器）。**两者都是软中止**，没有一个 SIGKILL 兜底 | 同 cmdline 同时出现 `timeout 2500` 与 `-t 2500` |
| **H3** | "以前有效"是**幸存者偏差**：legacy/fresh 各轮单题 wall 均值 ≈578s，2500s 的墙本来就设在分布尾部，绝大多数题自己就结束了；timeout 计数只有 1–13（(B) 5 轮 13/8/7/6/4）。**墙从来未被真正压到**，所以没暴露"杀不死" | (B) 5-run：Wall per task 578.6±77.0s；legacy (N′) timeout ≈1 |

> ⚠️ 另有两个**必须排除的干扰项**（否则修复白做）：
> - `data-dir` 落在 **NAS**（cmdline 有 `--data-dir /nasdata/...`）⇒ NFS 抖动会让收尾卡住（与"Stale file handle"同源）；
> - `(N′)` 即 **readback=none**，agent 拿不到 `run_code` 回读 ⇒ 无法判断自己失败 ⇒ 反复重来、单题时间无限拉长 ⇒ **这本身就是造长尾的变量**（不能只当 bug 修，要分清"环境 bug"与"该臂固有属性"）。

---

## 1. 给 agent 的排查要求（只读优先，不改训练/配置）

### A. 源码级（只读，`sed -n` 打行号，不整文件 cat）
1. `run_cli.sh` **190–240 行**原文（确认 `timeout` 是否带 `-k`、是否 `&` 后台 + `wait`、`$COMMAND` 到底是什么、`increment_stat` 在哪条分支）。
2. `run_cline_script.sh` 里 **`-p`/`-n` 的含义**、它如何调 `run_cli.sh`、**是否又套了一层 `timeout`**。
3. 全仓 `grep -rn 'kill-after\|-k [0-9]' scripts/` —— 确认**全项目没有一个 SIGKILL 兜底**。
4. `grep -n 'timeout' run_cli.sh` 全部命中行（判断是否还有第二处计数/兜底路径）。

### B. 现场级（**r3 batch `2026_1019_145634` 的 5 个 timeout 逐一定性**）
对这 5 题逐个产出**一行事实**：`task_name | worker | 起止时刻 | 实际耗时 | 是否 >2500 | 收尾是被谁终止的 | 结束时 stats/timeout 是否已 +1`。
- 判据：`实际耗时 > 2500` 且 `stats/timeout` 正常 +1 ⇒ **H1 成立（软墙杀不死、最终靠别的东西收口）**；
- 若 5 题全部 `≤2500` ⇒ **H3 成立（根本不是超时失效，是误读）**，须如实改口径。
- 同时给出 `2026_1019_145634/stats/total_time` 与 **理论最短耗时**（158 题 ÷ 8 并发 × 单题均值 578s ≈ 3.2h）对照，判断 11,742s（3h15m）是否本就正常。

### C. 排除干扰（择一，只读即可）
- `df -BG /home`（**已知 /home 96%，8G 门槛**）+ `--data-dir` 所在 NAS 是否可写（`timeout 10 touch` 测试后删除）；
- r2 task 119 的 **ws 文件在 2500s 后是否仍在增长**（用 r2 日志回溯即可，不用复现）；
- `(N′)` 与其他臂（(B)/(F)）**同一 task 的 `run_code` 调用次数对比**：若 (N′) 明显更高 ⇒ 说明"无反馈→反复重试"是长尾来源。

### D. 结论要求（**必须分三档，不许合并**）
1. **真 bug**：代码层面可修（如缺 `-k`）；
2. **该臂固有属性**：`readback=none` 导致无法收敛（**属实验现象，不是 bug**，应考虑写进论文讨论）；
3. **环境**：NAS/代理/`/home` 满等外部因素。

---

## 2. 候选修复方案（agent 只做**评估**，不得自行上线；由运维拍板）

| 方案 | 内容 | 优点 | 风险/代价 |
|:--|:--|:--|:--|
| **F1** | `timeout` 加 `-k 60`（`timeout -k 60 2500 ...`），并在 `increment_stat timeout` 前后加日志 | 一行修改，根治"杀不死" | **改评测环境须论文披露**；`-k` 只杀 leader 仍可能留孤儿（需 `--foreground` 或进程组 kill） |
| **F2** | 外层不动，**加外部 watchdog**（每 60s 扫 `ps`，单 task >3750s 即 SIGKILL 并写 `stuck` 标记） | **harness 参数零改动，论文口径干净**；可精确记录"哪几题被兜底" | 多一个常驻进程；时序细节需写清 |
| **F3** | 用 `setsid` + 杀**进程组**（`kill -TERM -$PGID`）替代单 PID kill | 连子孙一起收 | 需改 `run_cli.sh` 启动方式，影响面大 |
| **F4** | 缓冲层：`--data-dir` 从 NAS 改本地（或先本地后同步） | 消除 NFS 收尾卡顿（H1 的触发条件之一） | 占用 `/home`（已 96%！需先清） |
| **F5** | **不改代码**，只在报告里把 `stuck_count`（>2500s 未自然收口）与 `timeout` 分列 | 零风险、最快 | 每轮可能白等数小时（r2 白等 6h） |

> 运维倾向：**F2 + F5 组合**（先挂 watchdog 兜住 r4/r5，统计 `stuck_count` 进报告；**不动 2500 与 harness 参数**，避免重蹈 10-10 `timeout:180` 被"全部回退"的覆辙）。F1/F3 等根因确认、且 r4/r5 已收口后再议。

---

## 3. 纪律（沿用，硬）

- **只读优先**：A/B/C 全部可只读完成；**不得**改 `run_cli.sh`/`run_cline_script.sh`/`.env`/cline 版本；
- **不重启 r3、不 kill r3**（已结束，等 Step 7.1）；
- 🚫 禁止 `pkill -f '<含自身命令行子串>'`（用括号技巧）；
- 长输出 `cut -c1-140`；🚫 整树 `du`；
- 回报写 `MEMORY_ZHULONG.md` 心跳 + `daily-memories/2026-10-19.md`，commit 前缀 `zhulong diag:`。

---

## 4. 期望交付（给运维决策用）

1. **一张定性表**：5 个 timeout × (实际耗时 / 是否 >2500 / 收口方式)；
2. **根因结论**：H1/H2/H3 各自成立/不成立（附证据行号或日志时间戳）；
3. **修复建议排序**：F1–F5 里推荐哪个 + 为什么 + 需不需要在论文披露；
4. **对 `tab:readback-cost` 的影响**：r1=78.5% / r2=70.9% 的 7.6pp 差距里，有多少可能与"墙"有关（若能量化）。
