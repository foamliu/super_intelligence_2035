# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        T2 Terminal-Bench 7×5 pilot Gen7. 6/7 done, claude-code rerun3 RUNNING. Gate=7/7✅. Oracle5/5✅. H-B报告✅
已完成:       H-B 7way ctx compression report✅·oracle5/5✅·7adapters✅·28/28mock✅·Gate 7/7✅(R466)·Gen7 pilot 6/7 done·codex rerun3✅(3/5=60%)·claude-code rerun3 RUNNING
当前动作:     R471 监控 Gen7 rerun3. codex rerun3 COMPLETE: 5/5 trials, 0 errors, mean=0.6 (3/5 passed: bn-fit-modify, fix-git, log-summary-date-ranges). claude-code rerun3 RUNNING (harbor PID 4062894, etimes~35min): 2nd attempt has 1 errored(bn-fit-modify RuntimeError exit code1 empty stderr), 1 running(break-filter-js-from-html), 3 pending. Not interfering with running rerun.
下一步:       ①等claude-code rerun3完成②汇总Gen7最终结果(7/7)③决定是否启动7×89全量④若claude-code仍失败,调查exit code1根因(gw_proxy连接?Docker cold start race?)
阻塞:         无（claude-code rerun3在后台setsid运行, /tmp/tb_rerun3.log）
ERROR_COUNT:  0
📦 体积：TASK=31KB / MEMORY=4KB
```

### 本唤醒流水
[06:05] R471 **Gen7 pilot 6/7 results collected, codex rerun3✅, claude-code rerun3 still RUNNING**. Codex rerun3 (2026-10-24__04-55-49): 5/5 completed, 0 errors, mean=0.6, passed=bn-fit-modify+fix-git+log-summary-date-ranges, failed=break-filter-js-from-html+chess-best-move. Config.toml fix confirmed working. Claude-code rerun3: 1st attempt(04-43-02) 5/5 RuntimeError(exit code1,empty stderr); 2nd attempt(05-34-18) 1 errored+1 running+3 pending. harbor PID 4062894 alive(etimes~35min). NOT interfering with running rerun. Gen7 table: cline=100%, pi=100%, codex=60%, opencode=60%, hermes=0%, deepseek=0%, claude-code=RUNNING. Committed codex results, updated MEMORY. WAITING=1.
> 📦 R460-R469 (2026-10-23~24, H-B报告完成+Gen7 pilot+codex/claude-code infra fix+rerun) 已归档 → daily-memories-harness/2026-10-23.md + 2026-10-24.md。结论：H-B报告58KB已push, Gen7 pilot 5/7(cline+pi=100%,opencode=60%), codex 0.164.0 API兼容性修复(config.toml), claude-code NFS perms修复(chmod755). 需要时再读。

> 📦 R431-R447 (2026-10-18~19, TB pilot Gen2-Gen3 + Docker blockers + relay checks, ~20 rounds) 已归档 → daily-memories-harness/2026-10-18.md + 2026-10-19.md。结论：Docker 只在 .29 可用, pilot Gen3 1/7→gw_proxy 修复→逐路定根因→Gen5 7/7 完。需要时再读。

> 📦 R352-R430 (2026-10-13~18, glm53 7×300 监控/修复/报告 + TB T2 前置 + Docker networking, ~60 rounds) 已归档 → daily-memories-harness/2026-10-13.md ~ 2026-10-18.md。结论：glm53 7×300 2100/2100 完成, SWEBENCH_COMPARE 报告交付, TB T2 Docker networking 突破。需要时再读。

> 📦 R113-R351 (2026-10-04~13, SWE-bench 7×300 pipeline 建立 + 早期 harness 横评, ~100 rounds) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-13.md。结论：SWE-bench pipeline 打通, R1 unshare 沙箱可行, 早期 5-way/7-way 横评完成。需要时再读。

> 📦 §P1/FIX2 (2026-10-13) 已归档 → run/ARCHIVE_OPERATOR_HARNESS.md。结论：P1-2 rerun DONE, fix2 32 条重评 9 FLIPPED, kimi 574→621 resolved。需要时再读。

## 🗣️ 运维问答

> **当前无待答运维问题**。

> 📦 R113-R202 (2026-10-04~09, 早期 SWE-bench 横评 + SWEBENCH_COMPARE 监控 + 7-way harness 横评) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-09.md。需要时再读。

## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（**多 agent 共用**，见 `AGENTS.md`）
- **同级任务线**（🚫 不要碰）：`MEMORY_VISION.md` / `MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md`

## 流水

> 📦 R35-R459 流水条目（2026-10-02~20, H-B 源码分析 + H-A SWE-bench 7×300 + TB pilot Gen2-Gen5, ~400 rounds）已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-20.md。需要时再读。最新流水见上方「本唤醒流水」。
