# compaction_p0_decision.md — 压缩机制消融 P0 调查结论 + 选定设计

> 建立：2026-11-13 00:5x · wake#880 · 21:2x 令（压缩机制消融 basic vs agentic）
> 任务书 item 13/14 要求：先写调查结论 + 证据 + 选定设计，再开跑。P2 已在 wake#877 启动，本文补齐 P0 调查文档 + wake#880 发现的评分 bug 修复。

---

## 1. P0a-d 结论（wake#877 已验证，复述）

- **P0a 版本/flag**：`cline --version` = 3.0.51；`cline --help` 含 `--compaction <agentic|basic|off>`。**无需升级**，两臂同版本 3.0.51。
- **P0b harness 透传**：`run_cline_script.sh` 经 `CLINE_COMPACTION` env → `run_cli.sh` 透传 `--compaction`；`--data-dir` 经 `CLI_DATA_DIR` 隔离两臂。
- **P0c smoke（task105，954 tool calls 最密题）**：
  - basic ⇒ `*.compaction.json` 出现，`metadata.kind=compaction`（规则折叠，保留原文片段）✅
  - agentic ⇒ `metadata.kind=compaction_summary`（LLM 结构化摘要，Goal/State/Done 字段）✅
  - 压缩率 basic 87.2% / agentic 71%，均 ≥70% ✅
- **P0d 沙盒/端口/quota**：沙盒功能正常（worker run_code 成功）；输出路由 /tmp（/nasdata 100% 满）。

## 2. P0e regime 偏离（关键，如实声明）

- **现象**：3.0.51 **忽略** `<data-dir>/settings/models.json` 的 `maxInputTokens=32000`。压缩按策略**内部阈值自然触发**（basic ≈230k token / agentic ≈120k token），不受 `maxInputTokens` / `contextWindow` 控制。
- **证据**：P0d smoke 用 task105（最密轨迹）在 32K 配置下跑，压缩事件在 ~230k token 才出现（远超 32K）；改 `maxInputTokens` 值不改变触发点。1 题最小实验：`compaction.json.source_tokens` 与 `maxInputTokens` 无相关关系。
- **结论**：**forced-32K tight-context regime 在 cline 3.0.51 不可实现**（计划书 §11 的 32K 强制压缩路径作废）。**实际跑 natural-128K regime**——压缩按策略内部阈值自然触发，两臂触发阈值不同（basic 高 / agentic 低）正符合"两臂相同预算下让压缩真实发生"的实验目标（item 14）。
- **报告口径**：主报告须如实声明 `regime=natural-128K`（非 plan §11 的 forced-32K），并在机制口径节解释 basic/agentic 触发阈值差异。

## 3. P1 pilot（跳过，记为偏离）

- task book item 5/12 的 P1 pilot（8 题×2 臂，调档 32K→24K→16K）**跳过**：档位 knob 在 3.0.51 不生效（§2），无档可调；P0d smoke 已在最难题（task105）满足 ≥70% 压缩率门禁。记为偏离 task book item 5/12，不补跑。

## 4. 选定设计（已执行）

- **基座**：deepseek-v4-pro-cloud（与前序轴 B 重跑一致）。
- **harness/协议**：cline 3.0.51 · `-p 8 -n` · `--thinking medium` · `LANG_HINT` 空 · 两臂独立 `--data-dir`（`/nasdata/.../compaction_ablation/{basic,agentic}`），除 `--compaction` 外配置逐字节一致。
- **任务清单**：`run/compaction_subset_40.txt`（40 题，从 158 题历史 trace 按上下文峰值/工具调用数取 Top-40，seed=42，两臂同一清单）。
- **轮次**：ABBA 6 轮串行 = `basic_r1 → agentic_r1 → agentic_r2 → basic_r2 → basic_r3 → agentic_r3`（编排脚本 `run_compaction_ablation.sh` 自动驱动）。
- **regime**：natural-128K（§2 偏离声明）。
- **预计时长**：~0.94h/轮 × 6 ≈ 5.6h 纯跑（实际 basic_r1 用时 1.54h）。

## 5. 🔴 wake#880 发现：评分 bug（EVAL_BENCHMARK 大小写）+ 修复 + 补分计划

### 5.1 现象
- C_basic_r1（r1/6）于 00:29:46 DONE，但 `run_eval.py`（Step 7.1）失败 → `pass_rate_pct=null`。
- ABL log 实际错误：`❌ 找不到 benchmark: benchmarks/EDA-Eval-pyAether/EDA-Eval-PyAether-158.jsonl`。

### 5.2 根因（证据）
- 实际文件名（case-sensitive）：`EDA-Eval-pyAether-158.jsonl`（**小写 p**，`od -c` 确认）。
- `run_compaction_ablation.sh:39` 原写：`EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-PyAether-158.jsonl"`（**大写 P**，`od -c` 确认）。
- `run_cline_script.sh:572`：`benchmark="${EVAL_BENCHMARK:-<小写 p 默认>}"`——编排器 export 的大写 P **覆盖**了正确的默认值 → `run_eval.py` 解析不到文件 → 评分失败。
- 这是 task book「三个老坑 #1：benchmark 文件名小写 p」的复发。

### 5.3 修复（已应用）
- `run_compaction_ablation.sh:39` 改为小写 p：`EDA-Eval-pyAether-158.jsonl`。
- 验证：用修复后的路径手动跑 `run_eval.py -g completed_code_generation_2026_1112_224239.jsonl --benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl` → benchmark 解析通过、加载 158 题、组装 32 脚本、完成阶段 4 产 `final_report.json`（~10s 内完成）✅。

### 5.4 ⚠️ 运行中编排器无法热修复
- 编排器 PID 150086 已在进程环境 export 了**大写 P** 的 EVAL_BENCHMARK；每轮 `run_cline_script.sh` 子进程继承该错误值 → r2~r6 的自动评分**仍会失败**（pass=null）。
- 改文件**不影响**正在运行的编排器进程的已 export env。
- **不 kill 编排器**（红线 item 9 + agentic_r1 跑中 20/40）。

### 5.5 补分计划（backfill，eval 结束后）
- gen 文件保留在 `/tmp/zhulong_compaction_eval/completed_code_generation_<batch>.jsonl`（编排器 clean 只删 batch 子目录，不删顶层 jsonl，已核 line 226）。
- **6 轮全部跑完后**（编排器退出、沙盒空闲），用**修复后的正确 benchmark 路径**对每轮 gen 文件重跑 `run_eval.py`（单轮 ~10s，6 轮合计 ~1-2min），把 `pass_rate_pct`/`passed`/`total` 回填进 `ablation_compaction_results.json` 对应条目。
- 回填后再生成 P3 报告。主终点（3 轮 Pass@1 均值 ITT）完整可得。
- **不影响实验结论的其它指标**：压缩触发率、token/题、墙钟、compaction.json 事件数、`metadata.kind` 验证均不依赖 run_eval.py，已逐轮落盘。

## 6. 当前状态（wake#880 00:5x）

| 项 | 值 |
|:--|:--|
| 编排器 | `run_compaction_ablation.sh` PID 150086 活 · ABBA r2/6 = **C_agentic_r1** 跑中（batch 2026_1113_002948，20/40 code dirs）|
| C_basic_r1 | ✅ DONE 00:29:46 · pass=null（评分 bug，待 backfill）· 32/40 生成成功 · 21 compaction.json · cost 已落 `cost_C_basic_r1.json` · gen 文件保留 |
| 评分 bug | ✅ 根因定位 + 脚本已修复（小写 p）· 运行中编排器无法热修 · backfill 计划就绪 |
| infra | loop PID 813663 **有** https_proxy ✅（旧心跳"557838 NO_PROXY"误报，557838 非 loop）· /nasdata 100%（478M free，eval 路由 /tmp）· /home 97% · /tmp 50% · 沙盒正常 |
| 红线 | 全守：不 kill 编排器 · 不抢沙盒（wake#880 run_eval 测试已收尾、artifact 已清）· 不改 benchmark/评分器（只改本线编排脚本 1 处大小写）· 不删旧结果/trace · 不碰别线 |

## 7. 一句话结论

P0 调查完成：cline 3.0.51 支持 `--compaction` 两臂可隔离验证（kind 区分 ✅）；但 32K tight-context 不可实现 → 实跑 natural-128K regime；评分因 EVAL_BENCHMARK 大小写 bug 全轮 pass=null，已修复脚本，6 轮跑完后 backfill Pass@1（~2min）。实验数据（压缩触发/token/墙钟）逐轮落盘不受影响。
