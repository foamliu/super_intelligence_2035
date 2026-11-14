# POSTTRAIN_PLAN_NEXT.md — 今夜计划 + 执行记录（posttrain 线填写）

> 用户令 2026-11-14 21:5x：「基于这份结果，下一步可以请 post-train 出一份计划，然后按此办理。现在夜了，让 post-train 出计划后直接执行，不用等运维批复，明早我看结果即可。」
> **本文件由 posttrain 线自己填写**（运维只写要求）。填完立刻开工，**不要等批复**。
> **填表轮次**：wake505（2026-11-14 22:4x）。本计划已按此办理，执行结果见 §5。

## 0. 起点（wake500 已订正，别再用旧数）

- 36.15 环境 run1 完整结果 = **18.99%（30/158）**；`.17` 旧测法 = 3.04%。两者**同模型**（minicpm5-2b-sft-v39-final / global_step_105，已 curl 核实）；`final_report.model_name=zhulong_deepseek_v32` 是 config 陈旧标签，不是实际模型。
- 分层：生成成功 **36** / 生成失败 **121** / 超时 **1** → **生成后通过率 83.3%**（写出来的代码大多能过）。
- 失败头号 = **T6_tool_format 占 121 个 gen-fail 的 100%（占全 158 题的 76.6%）**。
- 全局被拒 **1304** 次：按原因 `missing-required-field` 527 / `other-type-error` 378 / `string-not-array` 321 / `unavailable-tool` 41 / `wrong-type-boolean` 37；按工具 `run_commands` 1051（80.6%）独大。
- **T6 内部再分**：121 个 gen-fail = **76 拒绝致死**（≥1 次被拒耗尽 turn）+ **45 静默未生成**（零拒绝，从未成功调工具）；gen-fail 任务 `used_search_apis=0` / `used_run_code=0` → 从未进入「检索→执行」回路。

**结论先行**：当前最大的损失不在「会不会写」，而在「**会不会按 MCP 协议调工具/提交**」。计划围绕这一点排 ROI。

## 1. 计划回答的四件事（判据 + 预算 + 回滚）

### ① 口径统一（Task A · A1/A3 两臂优先，A2 可选）

- **做法**：在 36.15 上跑单变量消融，40 题分层子集（`attribution_stratified_40.json`，seed=20261114，已就绪）。每臂只改一项，其余与 36.15 逐字节一致。
  - **A0** = 36.15 现配置（基线对照，可选跑）；**A1** = 提示→no_sandbox 版（只改提示）；**A3** = 沙盒关 + 提示 no_sandbox（≈还原 .17 组合）。
  - 驱动：`bpt_attribution_ablation.sh --arm A1|A3`（`--dry-run` 已验证通过）。
- **判据（预注册，写在跑之前）**：
  - 若 **A3 ≈ 3%** 且 **A1 ≥ 12%** ⇒「prompt 措辞不是主因，反馈回路才是」。
  - 若 **A1 ≤ 8%** ⇒「prompt 是主因」，需解释机制。
  - 若 A1、A2 都下降明显 ⇒ 按 prompt × 沙盒交互解释，不二选一糊弄。
- **预算**：每臂 40 题 `-p 8` ≈ 2h；A1+A3 两臂串行 ≈ 4-5h（含判分）。本轮先各 1 seed。
- **回滚**：若某臂 `final_report.json` 缺失 / infra 断裂 ⇒ 标 BLOCKED + 记卡点，不伪造数字；不与运行中 36.15 baseline 5-run 并跑（runner 头有 status 闸门）。

### ② T6 工具格式专项（最高 ROI · Task B P0）

- **做法**：P0 补丁 = `attribution_prompt_p0_toolfmt.md`（run_commands commands=数组、read_files files=对象数组、submit_and_exit summary/verified 类型、区分 pyAether_MCP_server 与 eda_flow 两 server 参数不互通）。
- **归因表（已交付）**：1304 次拒绝 → 原因分布 → P0 可消比例 ≈ **859/1304 = 65.9%**（详见 `attribution_t6_table.json` + `reports/report_posttrain_attribution_t6_zh.html`）。
  - `string-not-array` 321 → P0 可消 ~90%；`missing-required-field` 527 → ~70%；`wrong-type-boolean` 37 → ~80%；`other-type-error` 378 → ~40%（双 MCP 混淆部分，余为 parser 乱码）；`unavailable-tool` 41 → ~50%。
- **预期回收**：目标 76 个拒绝致死任务，P0 砍 run_commands 拒绝 ~60% → 乐观救回 38 题（+20pp）/ 保守救回 25 题（+13pp）。
- **判据**：dev 上 3 seed，**≥ +3pp 且 submit 报错率降 ≥ 10pp** 才进下一轮（累积组合）。
- **预算**：dev(79) × 1 patch ≈ 2-3h；baseline + p0 各 1 seed 先跑。
- **回滚**：若 P0 dev Pass@1 增量 < +3pp 或 submit 报错率未降 ≥10pp ⇒ 判该补丁「不达门槛」，记为负结果，不进累积组合；**不**事后调门槛。
- **上限警告**：aggregate_tool_calls 里大量乱码工具名（vLLM minicpm5 tool-call parser 问题）非 prompt 可解，P0 只回收「格式可指导」部分；45 个静默未生成任务 P0 不直接覆盖。

### ③ P1/P2/P3 补丁（按 ROI 顺序，一次只加一条）

- 顺序：**P0（最高 ROI）→ P2 submit 风暴 → P1 degenerate guard → P3 检索落地**。
- **P1**（`attribution_prompt_p1_degenerate.md`）：提交前 get/query 反查 + 数值级断言；空实现禁 submit。针对 degenerate pass 回潮。门槛同上；失败放弃条件 = dev 增量 < +1pp（针对性弱于 P0）。
- **P2**（`attribution_prompt_p2_submitstorm.md`）：submit 每任务 ≤2 次、被拒禁原样重提。释放 turn 预算。失败放弃 = dev 增量 < +2pp。
- **P3**（`attribution_prompt_p3_retrieval.md`）：search_apis 命中须经 get_api_details 确认、bm25_fallback 不当 API 名。失败放弃 = dev 增量 < +2pp。
- **预算**：每条 dev 1 seed ≈ 2-3h；本轮力争至少 P0 一条的前后对比。
- **回滚**：任何补丁 dev 不达门槛即判死，记负结果；**一次只加一条**（否则又回到多变量无法归因）。

### ④ 明早交付清单（具体到文件名 + 可进汇报的数字）

| 交付物 | 路径 | 状态 |
|:--|:--|:--|
| 计划填妥 | `run/POSTTRAIN_PLAN_NEXT.md`（本文件） | ✅ 已填 |
| T6 归因表 | `run/attribution_t6_table.json` + `reports/report_posttrain_attribution_t6_zh.html` | ✅ 已交付 |
| EXPERIMENTS 新节 | `run/EXPERIMENTS_POSTTRAIN.md` §R-Attribution-T6 | ✅ 已写 |
| 补丁模板 + runner | `run/attribution_prompt_p{0,1,2,3}_*.md` + `bpt_attribution_prompt_dev_eval.sh` | ✅ run-ready（wake503） |
| 40 题子集 + 79/79 split | `attribution_stratified_40.json` + `attribution_traindev_split.json` | ✅ 已就绪 |
| A1/A3 两臂 40 题结果 | `bpt_attribution_ablation.sh --arm A1\|A3` → `/tmp/posttrain_attribution_ablation/` | ❌ HARD BLOCKED（见 §5） |
| P0 dev 前后对比 | `bpt_attribution_prompt_dev_eval.sh --patch p0 --split dev` → `/tmp/posttrain_attribution_prompt/` | ❌ HARD BLOCKED（见 §5） |

**可直接进汇报/论文的数字**：基线 18.99%（30/158，36.15 run1，同模型 step105）；生成后通过率 83.3%；T6 占失败 76.6%；1304 次拒绝中 run_commands 占 80.6%；P0 估计可消 65.9% 拒绝、乐观 +20pp / 保守 +13pp（**预注册估算，待 36.15 实测 + McNemar 检验后才能定论**）。

## 2. 硬约束（不变）

- 单变量 · 预注册判据 · train/dev 79:79 分离 · 先 dev 后 test · 反作弊钩子常开并报 cheat。
- 🚫 不改 benchmark / `check.py` / 题面、不挑题、不引用未跑完的 run。
- 每轮 `commit + push`（前缀 `posttrain attribution:`），`EXPERIMENTS_POSTTRAIN.md` 有新节。
- 任务书体积：开工前先把已闭合块归档（当前已 ≈27.5KB，未超 40KB 硬限；本令与使命块不归档）。

## 3. 时间表（夜→晨）

| 时段 | 动作 | 实际 |
|:--|:--|:--|
| 22:30-22:50 | 填本计划 + 建 T6 归因表 + HTML 报告 + EXPERIMENTS 节 | ✅ 完成 |
| 22:50-23:10 | 起 36.15 隧道 + A1 起跑 | ❌ 隧道 DOWN，无法起跑（见 §5） |
| 23:10-01:10 | A1 跑 + A3 排队 | ❌ BLOCKED |
| 01:10-04:00 | A3 跑 + P0 dev baseline 起跑 | ❌ BLOCKED |
| 04:00-07:00 | P0 dev 前后对比 + 出数 | ❌ BLOCKED |
| 07:00-09:00 | 汇总 + 报告更新 | ⬜ 待隧道恢复 |

## 4. 回滚总表

| 触发条件 | 动作 |
|:--|:--|
| 隧道断 / 模型端点不可达 | 标 BLOCKED + 记卡点 + ETA，不伪造；待运维重启中继 |
| 任一臂 final_report 缺失 | 该臂标 TODO，不进汇总 |
| P0 dev 增量 < +3pp 或 submit 报错率未降 ≥10pp | 判该补丁不达门槛，记负结果，不进累积组合，不事后调门槛 |
| 与运行中 36.15 baseline 5-run 冲突 | runner status 闸门拦截（exit 2），等其 DONE 再跑 |
| 任何 infra 错误（OOM/serve 死） | 不杀健康 eval，记日志，标 ETA |

## 5. 执行结果与阻塞（诚实记录，非「进行中」）

### ✅ 已完成（CPU，本轮交付，22:30-22:50）
1. **本计划填妥**（含时间表/判据/预算/回滚）。
2. **T6 归因表**：`attribution_t6_table.json` + `reports/report_posttrain_attribution_t6_zh.html`（单文件自包含、3 个内联 SVG 饼图、0 script、0 外链）。1304 次拒绝按原因/工具分布 + P0 可消比例 65.9% + gen-fail 分解（76 拒绝致死 / 45 静默未生成）+ 预期回收 +20pp/+13pp。
3. **EXPERIMENTS_POSTTRAIN.md 新节** §R-Attribution-T6。
4. **前置全部 run-ready**（wake503 遗产）：P0/P1/P2/P3 补丁模板、dev-eval runner、40 题子集、79/79 split 均 `--dry-run` 验证通过。

### ❌ HARD BLOCKED（无法在 .17 单侧完成）—— A1/A3 + P0 dev 前后对比
- **卡在哪**：**36.15 隧道 DOWN**。`dual-nix-tunnel` 需 **Windows 中继 `172.19.195.133` 运行 `tunnel.ps1`**；当前 `.17` 上端口 **3333 未监听**、无 `ssh -p3333` 进程；`.17` 直连 `36.15:22` 被防火墙阻（README：两服务器仅 ICMP 互通）。run1 eval **21:15 完成时隧道尚通**，约 1.5h 前中继掉线。
- **谁在卡**：**运维 / infra** —— 须在 Windows 中继 `172.19.195.133` 重启 `tunnel.ps1`；**无法从 `.17` 单侧修复**（Windows 桌面机，非 .17 可触达）。
- **ETA**：**未知（取决于运维）**。隧道恢复后：A1+A3 约 4-5h、P0 dev eval 约 2-3h，可在天亮后补齐。
- **已就绪等待**：`.17 GPU6:8096 step105-final` 服务健康（`urllib` 实测 `id=minicpm5-2b-sft-v39-final`）；`GPU7:8095 R2-step200` 服务在监听；补丁模板 / split / runner 全 `--dry-run` 通过。**隧道一恢复**即可 `ssh -p3333 -fN -R 18096:localhost:8096 app.e0031982@localhost` 起跑 A1/A3 + P0 dev。
- **为何不在 .17 直接跑**：15:4x 用户令明确「PyAether 评测必须在 36.15 上启动」（只有 36.15 有 RAG API 文档库 + 沙盒 MCP）；在 .17 跑会复现 3.04% 的错误口径，违反口径统一目标。

### 可复算命令
```bash
python3 bpt_attribution_t6_report.py                                   # 复算 T6 归因表 + HTML
bash bpt_attribution_ablation.sh --arm A1 --dry-run                    # 隧道恢复后在 36.15
bash bpt_attribution_ablation.sh --arm A3 --dry-run
bash bpt_attribution_prompt_dev_eval.sh --patch baseline --split dev --dry-run
bash bpt_attribution_prompt_dev_eval.sh --patch p0 --split dev --dry-run
```
