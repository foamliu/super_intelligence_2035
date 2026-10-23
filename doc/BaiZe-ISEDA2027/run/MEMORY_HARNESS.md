# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        T2 Terminal-Bench 7×5 pilot Gen7 RERUN(codex+claude-code). Gate=7/7✅. Oracle5/5✅. H-B报告✅
已完成:       H-B 7way ctx compression report✅·oracle5/5✅·7adapters✅·28/28mock✅·Gate 7/7✅(R466)·Gen7 pilot 5/7 done(R467)·codex/claude-code infra fix(R468-R469)
当前动作:     R469 Gen7 pilot rerun codex+claude-code. codex rerun RUNNING(bn-fit-modify trial,codex--version=0.164.0 confirmed in-container✅). claude-code PENDING(after codex). NFS perms fixed:chmod 755 on @anthropic-ai/+claude-code/+@openai/+codex/ dirs(were 750,agent user exit127).
下一步:       ①等codex rerun完成(5 trials)②等claude-code rerun完成③汇总Gen7最终结果(7/7)④决定是否启动7×89全量
阻塞:         无（rerun在后台nohup运行,/tmp/tb_rerun_codex_claude.log）
ERROR_COUNT:  0
📦 体积：TASK=31KB / MEMORY=4KB
```

### 本唤醒流水
[03:15] R469 **Gen7 pilot完成5/7→诊断codex/claude-code失败→修复NFS权限→启动rerun**. Gen7完整结果: oracle5/5✅·cline-patched5/5=**100%**✅·codex0/5❌(NonZeroAgentExitCodeError,chmod EROFS,R468已修adapter但codex用旧adapter跑的)·hermes0/5(capability,0err)·opencode3/5=**60%**(1 timeout chess)·claude-code0/5❌(RuntimeError exit127,根因=NFS dirs 750→agent user无法traverse)·deepseek0/5(capability,0err)·pi5/5=**100%**✅. **R469修复**: chmod 755 on claude-code-npm/@anthropic-ai/{,claude-code/}+codex-npm/@openai/{,codex/,bin/,codex.js}(NFS chmod OK,exit=0). **验证**: `docker exec ... codex --version`→`codex-cli 0.164.0`✅,`which codex`→`/usr/local/bin/codex`✅. **rerun启动**: `_rerun_codex_claude.sh`(nohup bg,gw_proxy restarted on 9090/9091). codex trial1 bn-fit-modify RUNNING(Docker container up 4min). WAITING=1.
> 📦 R460-R465 (2026-10-23, H-B报告完成+复验×4+Gen6 hermes smoke) 已归档 → daily-memories-harness/2026-10-23.md。结论：H-B 7way上下文压缩报告58KB已push(e8f2da3e3), Gen6 hermes smoke PASS(R457 fix confirmed), gate was 5/7. 需要时再读。

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
