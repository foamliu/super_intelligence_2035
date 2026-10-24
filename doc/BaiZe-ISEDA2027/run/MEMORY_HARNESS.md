# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        T2 Terminal-Bench 7×15 full run v2 RUNNING. Gen7 pilot 7/7 COMPLETE. Gate=7/7✅. Oracle 15/15(mean 0.733)✅. H-B报告✅
已完成:       H-B 7way ctx compression report✅·Gate 7/7✅(R466)·Gen7 pilot 7/7 done✅·Oracle 15/15✅·7×15 v1 crashed(NFS Stale handle)·7×15 v2 STARTED(R473)
当前动作:     R473 7×15 full run v2 RUNNING in background. v1 crashed with NFS "Stale file handle"(Errno 116) during oracle cleanup — harbor --jobs-dir was on NFS. v2 fix: redirect --jobs-dir to /tmp/tb_full_v2/(local disk). cline-patched running first task(adaptive-rejection-sampler). log=/tmp/tb_full_7x15_v2.log, ETA ~17h.
下一步:       ①监控7×15 v2进度(tail /tmp/tb_full_7x15_v2.log)②每个harness完成后检查result.json③全部完成后收集结果生成report_harness_terminalbench_7way_zh.html④McNemar配对检验⑤诚实条款声明15/89限制
阻塞:         15/89 task images only(MITM proxy blocks Docker Hub pull). 报告须声明"15/89 tasks, 非全量89"
ERROR_COUNT:  0
📦 体积：TASK=31KB / MEMORY=5KB
```

### Gen7 pilot 最终结果(7×5=35 trials)
| Harness | Pass Rate | Errors | Notes |
|:--|:--|:--|:--|
| cline-patched | 5/5 (100%) | 0 | ✅ Perfect |
| pi | 5/5 (100%) | 0 | ✅ Perfect |
| codex (rerun) | 3/5 (60%) | 0 | ✅ config.toml fix worked |
| opencode | 3/5 (60%) | 1/5 | ⚠️ 1 AgentTimeoutError |
| hermes | 0/5 (0%) | 0 | Genuine 0% (no errors) |
| deepseek-harness | 0/5 (0%) | 0 | Genuine 0% (no errors) |
| claude-code (rerun3) | 0/5 (0%) | 3/5 | 🔴 1 RuntimeError(exit1)+2 AgentTimeoutError |

### Oracle check (15 tasks, R473)
- 15/15 completed, mean reward 0.733 (11/15 solvable by oracle)
- Failed by oracle: build-pmars, caffe-cifar-10(AgentTimeoutError), configure-git-webserver, git-multibranch

### 本唤醒流水
[08:40] R473 **7×15 full run v1 crashed → v2 started with NFS fix**. v1(R472) crashed with OSError: [Errno 116] Stale file handle — harbor wrote --jobs-dir to NFS, NFS gave stale handle during log handler cleanup. Oracle check completed(15/15 mean 0.733) but crash prevented harness runs from starting. Root cause: all harbor --jobs-dir and trace tee paths were on NFS. Fix: created _full_7x15_v2_launcher.sh redirecting --jobs-dir to /tmp/tb_full_v2/(local disk, 73GB free). v2 started via `setsid sg docker -c "bash _full_7x15_v2_launcher.sh"`, cline-patched running first task. gw_proxy up on 9090/9091. ETA ~17h. WAITING=1.
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
