# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        T2 Terminal-Bench. 7×15 v2 RUNNING (codex harness, 6/7 valid). BULK IMAGE PULL IN PROGRESS (73 missing images). H-B报告✅
已完成:       H-B 7way ctx compression report✅·Gate 7/7✅(R466)·Gen7 pilot 7/7 done✅·Oracle 15/15✅·7×15 v2 RUNNING(R474)·Docker pull WORKS✅(R474)·cline-patched bug found+fixed✅(R474)
当前动作:     R474: ①7×15 v2 run in background (codex harness active, PID 1068001) ②Bulk pulling 73 missing TB images (PID 2611629, _pull_all_tb_images.sh) ③Found+fixed cline-patched 0/15 bug: v2 launcher missing `export TB_API_KEY` → cline got dummy key → 401. Fix applied to launcher for future re-runs.
下一步:       ①Wait for bulk pull to complete (~73 images, shared layers cached, ETA ~1-2h) ②Monitor v2 run (6/7 harnesses valid, cline-patched needs rerun) ③After pull done + v2 done: re-run cline-patched with fixed launcher ④Scale to 7×89=623 full run ⑤Report with McNemar
阻塞:         无(之前"MITM proxy blocks Docker Hub"是误判 — daemon.json proxies已配172.19.92.25:13128且实测docker pull成功). 73 images pulling now.
ERROR_COUNT:  0
📦 体积：TASK=31KB / MEMORY=6KB
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

### 🔴 R474 关键发现：Docker pull WORKS + cline-patched 0/15 根因

**① Docker pull 实测成功（推翻"MITM proxy blocks Docker Hub"误判）**
- daemon.json 已配 `proxies` → `http://172.19.92.25:13128`（Docker 27.5.1 支持 daemon.json proxies 字段）
- `systemctl show docker --property=Environment` = 空（无 systemd drop-in），但 daemon.json proxies 已足够
- 实测 `docker pull alexgshaw/circuit-fibsqrt:20251031` → 成功（392MB，共享 base layer "Already exists"）
- 15 个已有镜像均为 `alexgshaw/*:20251031`（Docker Hub pull 来的，非 docker load）
- **结论：之前"MITM proxy blocks"是误判**（可能当时 daemon.json proxies 还没配或 daemon 没重启）
- 已启动 `_pull_all_tb_images.sh`（PID 2611629）批量拉取剩余 73 个镜像

**② Terminal-Bench 任务数 = 89（全量）**
- `ls ~/terminal-bench/` = 89 个任务目录
- 15 个有本地镜像（alexgshaw/*:20251031），74 个缺失（1 个已拉，73 个正在拉）
- 之前 7×15 = 105 trials 是因镜像不全，**非任务集本身只有 15 题**

**③ cline-patched 0/15 RuntimeError 根因 = `export TB_API_KEY` 缺失**
- v2 launcher `_full_7x15_v2_launcher.sh:30` 设 `TB_API_KEY="..."` 但**没 `export`**
- Gen7 pilot launcher `_pilot_gen7_launcher.sh:14` 有 `export TB_API_KEY=...`
- cline-patched 用直连网关 `TB_BASE_URL=http://agi-gateway.cxmt.com/cloud/v1`（需真实 key）
- 其余 6 harness 用 gw_proxy (127.0.0.1:9090/9091，gw_proxy 注入真实 key from GW_API_KEY) → **不受影响**
- **已修复**：launcher line 30 改为 `export TB_API_KEY=...`（下次重跑生效）
- v2 run 已在跑 codex（不 kill），cline-patched 结果待 v2 完成后单独重跑

**④ v2 run 状态**
- cline-patched: 0/15 (15 RuntimeError) — 已保存，待重跑
- codex: RUNNING (5 env containers up, ~08:59 开始)
- log=/tmp/tb_full_7x15_v2.log, jobs=/tmp/tb_full_v2/jobs_*

### 本唤醒流水
[10:00] R474 **Docker pull 突破 + cline-patched bug 定位修复**. 响应用户 09:2x 补充令：①查清 15 镜像来源=alexgshaw/*:20251031 全部 Docker Hub pull ②查 dockerd 代理=daemon.json proxies 已配 172.19.92.25:13128（systemctl Environment=空但 daemon.json 足够）③实测 docker pull hello-world OK + circuit-fibsqrt OK(392MB) ④启动 _pull_all_tb_images.sh 批量拉 73 个缺失镜像(PID 2611629) ⑤定位 cline-patched 0/15 根因=v2 launcher 缺 export TB_API_KEY(已修复) ⑥v2 run 继续跑 codex(不 kill). WAITING=1.
> 📦 R460-R469 (2026-10-23~24, H-B报告完成+Gen7 pilot+codex/claude-code infra fix+rerun) 已归档 → daily-memories-harness/2026-10-23.md + 2026-10-24.md。结论：H-B报告58KB已push, Gen7 pilot 5/7(cline+pi=100%,opencode=60%), codex 0.164.0 API兼容性修复(config.toml), claude-code NFS perms修复(chmod755). 需要时再读。

> 📦 R431-R447 (2026-10-18~19, TB pilot Gen2-Gen3 + Docker blockers + relay checks, ~20 rounds) 已归档 → daily-memories-harness/2026-10-18.md + 2026-10-19.md。结论：Docker 只在 .29 可用, pilot Gen3 1/7→gw_proxy 修复→逐路定根因→Gen5 7/7 完。需要时再读。

> 📦 R352-R430 (2026-10-13~18, glm53 7×300 监控/修复/报告 + TB T2 前置 + Docker networking, ~60 rounds) 已归档 → daily-memories-harness/2026-10-13.md ~ 2026-10-18.md。结论：glm53 7×300 2100/2100 完成, SWEBENCH_COMPARE 报告交付, TB T2 Docker networking 突破。需要时再读。

> 📦 R113-R351 (2026-10-04~13, SWE-bench 7×300 pipeline 建立 + 早期 harness 横评, ~100 rounds) 已归档 → daily-memories-harness/2026-10-04.md ~ 2026-10-13.md。结论：SWE-bench pipeline 打通, R1 unshare 沙箱可行, 早期 5-way/7-way 横评完成。需要时再读。

> 📦 §P1/FIX2 (2026-10-13) 已归档 → run/ARCHIVE_OPERATOR_HARNESS.md。结论：P1-2 rerun DONE, fix2 32 条重评 9 FLIPPED, kimi 574→621 resolved。需要时再读。

## 🗣️ 运维问答

> **Q1 (09:0x令): Terminal-Bench 一共多少题？**
> **A**: 89 题（全量）。`ls ~/terminal-bench/` = 89 个任务目录。之前 7×15 = 105 trials 是因本地只有 15 个镜像，**非任务集只有 15 题**。

> **Q2 (09:0x令): 为什么只有 15 题参与？**
> **A**: 本地只有 15 个 `alexgshaw/*:20251031` 镜像（Docker Hub pull 来的）。其余 74 个之前没拉成功——但**根因不是"MITM proxy blocks"**，而是当时 daemon.json proxies 可能还没配或 daemon 没重启。**现在 daemon.json 已配 172.19.92.25:13128，实测 docker pull 成功**。

> **Q3 (09:0x令): 能不能把剩下 74 个镜像拉下来？**
> **A**: **能！** 实测 `docker pull alexgshaw/circuit-fibsqrt:20251031` 成功（392MB）。已启动 `_pull_all_tb_images.sh`（PID 2611629）批量拉取 73 个缺失镜像。共享 base layer 已缓存，预计 ~1-2h 完成。/data 剩余 6.4TB，空间充足。

> **Q4 (09:0x令): 改成 7 并发？**
> **A**: 当前 v2 run 是串行（7 harness × 15 tasks）。用户要求 7 并发。但**镜像还没补齐**（73 个正在拉），且 v2 正在跑（不 kill）。计划：①等镜像拉完 ②v2 跑完（或记录进度后停） ③用 89 个镜像启动 7×89 并发 run（每 harness 1 并发槽，独立 jobs-dir 在 /tmp）。

> **Q5 (09:2x令): 同事通过 92.25 代理成功拉过 Docker 镜像？**
> **A**: **确认！** daemon.json `proxies` 字段已配 `http://172.19.92.25:13128`，Docker 27.5.1 支持。实测 pull 成功。**无需额外配 systemd drop-in**（daemon.json proxies 已足够）。

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
