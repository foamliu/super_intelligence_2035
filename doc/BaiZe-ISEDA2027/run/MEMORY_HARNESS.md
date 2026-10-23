# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        T2 Terminal-Bench 7×5 pilot Gen7 RUNNING(bg opencode phase). Gate=7/7✅. Oracle5/5✅. H-B报告✅
已完成:       H-B 7way ctx compression report✅·oracle5/5✅·7adapters✅·28/28mock✅·Gen6 hermes smoke✅·Gate 7/7✅(R466)·Gen7 pilot LAUNCHED(R467)
当前动作:     R468 监控Gen7 pilot. 4/7 harness已完成: oracle5/5✅·cline-patched5/5=100%✅·codex0/5(chmod EROFS FIXED)·hermes5/5=0%(capability). opencode RUNNING(chess-best-move). codex+claude-code adapter chmod+x bug fixed(EROFS on ro NFS mount). fix已提交待push.
下一步:       ①等待opencode/claude-code/deepseek/pi完成②claude-code将自动使用修复后的adapter(去掉chmod)③全部完成→汇总Gen7 pilot结果→决定是否启动7×89全量
阻塞:         无（pilot在后台运行，PID=302224,~73min elapsed,当前opencode phase）
ERROR_COUNT:  0
📦 体积：TASK=31KB / MEMORY=4KB（R35-R467旧流水已归档→daily）
```

### 本唤醒流水
[02:05] R468 **监控Gen7 pilot + 修复codex/claude-code chmod EROFS bug**. pilot进度: oracle5/5✅(2m30s)→cline-patched5/5=**100%**(32m35s,all 5 tasks pass!)→codex0/5(**NonZeroAgentExitCodeError**×5,根因=`chmod +x` on ro NFS mount→EROFS)→hermes5/5=0%(capability,0 errors)→**opencode RUNNING**(chess-best-move). **修复**: codex.py:100+claude_code.py:108去掉`chmod +x`(文件已executable from npm install). py_compile OK. claude-code phase尚未开始→将自动使用修复后版本. git fetch需显式proxy(503 without). WAITING=1(pilot仍在跑).
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
