# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        T2 Terminal-Bench. IMAGE PULL 81/89 (8 missing, both pull scripts running). v2 serial: cline 0/15(bug), codex 6/14 PASS, hermes 0/9, opencode RUNNING(~68min). 7x89 launcher FIXED+READY. H-B报告✅
已完成:       H-B 7way ctx compression report✅·Gate 7/7✅(R466)·Gen7 pilot 7/7 done✅·Oracle 15/15✅·Docker pull WORKS✅(R474)·daemon.json proxy confirmed✅(R474/R476)·cline-patched bug fixed✅(R474)·7x89 concurrent launcher created+FIXED✅(R476/R477)·v2 codex done 6/14✅·v2 hermes done 0/9✅·v2 cline-patched done 0/15(bug)✅
当前动作:     R477: ①Image pull 81/89 (8 missing: make-mips-interpreter, mcmc-sampling-stan, merge-diff-arc-agi-task, model-extraction-relu-logits, modernize-scientific-stack, mteb-leaderboard, mteb-retrieve, multi-source-data-merger) — retry script + helper pull script both running ②v2 serial: opencode RUNNING (~68min on build-pmars), 3 harnesses remain (claude-code, deepseek-harness, pi) ③FIXED critical bug in 7x89 launcher: FULL_DATASET was defined AFTER the harbor loop that uses it — moved to before loop ④Collected v2 results: cline-patched 0/15(RuntimeError), codex 6/14 PASS(42.9%), hermes 0/9(6 RuntimeError)
下一步:       ①Wait for 8 remaining images (ETA ~30min, both scripts pulling) ②Once 89 images present: record v2 progress, stop v2 (or let opencode finish), launch 7x89 concurrent (launcher fixed+ready) ③7x89 = 623 trials, 7-way concurrent, ETA ~2.5-3h ④Report with McNemar + "89/89 full coverage" + "7-way concurrent" declaration
阻塞:         无. Pull scripts actively downloading remaining 8. /data 6.4TB free. Retry script 0 failures.
ERROR_COUNT:  0
📦 体积：TASK=32KB / MEMORY=14KB
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

### 🔴 R475 关键发现：28 images failed due to transient auth.docker.io outage + retry script started

**① Image pull progress (40/89 present, 49 missing)**
- Original pull script (_pull_all_tb_images.sh, PID 2611629): 22 OK, 28 FAIL, 16 skipped
- **28 failures root cause**: ALL same error — `auth.docker.io/token?... Service Unavailable` (503)
  - This is a **transient Docker Hub auth service outage**, NOT a network/proxy issue
  - Failures spanned tasks e→o alphabetically (extract-moves-from-video through openssl-selfsigned-cert)
  - After the outage, pulls resumed succeeding (pulled went 11→22), confirming auth.docker.io recovered
- Original script has NO retry logic — moved to next image on failure
- **Retry script started** (_retry_pull_tb_images.sh, PID 3788007): 3 attempts per image, 30s delay between retries
  - Already succeeding: extract-moves-from-video downloading layers (auth.docker.io back up)
- Both scripts running in parallel (idempotent docker pull, skip already-present images)

**② daemon.json proxy confirmed (no change from R474)**
```json
"proxies": {
    "http-proxy": "http://172.19.92.25:13128",
    "https-proxy": "http://172.19.92.25:13128",
    "no-proxy": "localhost,127.0.0.1,::1"
}
```
- `systemctl show docker --property=Environment` = empty (no systemd drop-in, but daemon.json proxies sufficient)
- Docker 27.5.1 supports daemon.json `proxies` field
- Docker Root Dir = `/data/docker`, /data has 6.4TB free (10% used)

**③ v2 run status (codex harness)**
- cline-patched: 0/15 (15 RuntimeError) — known bug (missing export TB_API_KEY), fixed for future reruns
- codex: 11/15 completed, 3 PASS (adaptive-rejection-sampler=1.0, build-pov-ray=1.0, configure-git-webserver=1.0), filter-js-from-html in progress, 3 more tasks to go
- v2 run will continue through remaining 5 harnesses after codex (hermes, opencode, claude-code, deepseek-harness, pi)

**④ 7 concurrency plan (P2, after images complete)**
- Cannot switch to 7 concurrency until all 89 images are present
- Current v2 run is serial (7 harness × 15 tasks), ETA ~17h total
- After 89 images: launch 7×89=623 full run with 7 concurrency (each harness 1 slot, independent /tmp jobs-dir)

### 🔴 R476 关键发现：09:2x指令P0全部已解 + 7x89并发启动器已就绪 + 镜像55/89

**① 09:2x 补充令 P0 回报（全部已被 R474/R475 解决，本轮复核确认）**
- **P0-镜像来源**：89个镜像均为 `alexgshaw/*:20251031`（Docker Hub pull）。`docker history` 确认 buildkit 层（COPY/WORKDIR/CMD），**非 docker load**。15个已有镜像 = pull来的，非tar导入。
- **P0-dockerd代理**：`/etc/docker/daemon.json` 已配 `proxies` 字段（http/https-proxy=`http://172.19.92.25:13128`，no-proxy=localhost,127.0.0.1,::1）。无 systemd drop-in（`/etc/systemd/system/docker.service.d/` 不存在）。`systemctl show docker --property=Environment`=空。**daemon.json proxies 方式生效**（Docker 27.5.1支持）。
- **P0-hello-world pull**：`sg docker -c 'docker pull hello-world'` → **SUCCESS**（Image is up to date）。两个pull脚本持续下载证明 pull 稳定可用。
- **结论**：09:2x 指令中的"MITM proxy blocks = 不可解"已被 R474 推翻。92.25 代理通过 daemon.json proxies 已配置并验证通过。无需切换 92.23。

**② 镜像拉取进度（55/89 present, 34 missing）**
- 主pull脚本 (_pull_all_tb_images.sh, PID 2611629, ~2.5h): 持续下载中
- 重试脚本 (_retry_pull_tb_images.sh, PID 3788007, ~1.3h): **0 failures**，已拉10个（auth.docker.io 恢复）
- 从49→55在数分钟内增长，预计~1h完成剩余34个
- /data: 7.0T total, 678G used, **6.4T free (10%)** — 空间充足

**③ v2 串行运行状态**
- cline-patched: DONE 0/15 (15 RuntimeError — bug已修, launcher line 30 已有 export TB_API_KEY)
- codex: DONE **6/14 PASS (42.9%)** — PASS: adaptive-rejection-sampler, build-pov-ray, configure-git-webserver, fix-git, git-multibranch, log-summary-date-ranges; FAIL: bn-fit-modify, break-filter-js-from-html, build-cython-ext, build-pmars, caffe-cifar-10, cancel-async-tasks, chess-best-move, count-dataset-tokens; Exceptions: 6 AgentTimeoutError + 1 VerifierTimeoutError; runtime 3h6m
- hermes: RUNNING (started 12:05:25)
- 剩余: opencode, claude-code, deepseek-harness, pi

**④ 7×89 并发启动器已创建（R476）**
- `_full_7x89_concurrent_launcher.sh` (147行, syntax OK, chmod+x)
- 7个harbor进程并行启动，各独立 `/tmp/tb_7x89/jobs_<harness>` (非NFS)
- 共享 gw_proxy (9090/9091), nice -n 19, 5s stagger
- 前置检查：89镜像全齐才启动（否则exit 3）
- 资源评估已写入脚本：224 CPU / 2TB RAM / 6.4TB disk → 7并发充裕

**⑤ 资源评估（30秒）**
- CPU: 224核, load avg 19.63/17.12/13.45 → 每harness可分~30核（需2-4）
- RAM: 2.0TB total, 1.8TB available → 每harness ~250GB（需数GB）
- Disk: /data 6.4TB free → 7容器同时跑充裕
- 当前运行容器: 5个（v2 hermes的env容器）

### 🔴 R477 关键发现：7x89启动器关键BUG修复 + 镜像81/89 + v2 opencode运行中

**① 7x89 并发启动器关键BUG修复（R477）**
- **BUG**: `_full_7x89_concurrent_launcher.sh` 中 `FULL_DATASET` 和 `N_TASKS` 变量在脚本**末尾**定义（原line 141-147），但harbor run循环在**中间**就引用了它们（line 103/112）→ 启动后所有harbor进程会拿到空`-p ""`参数导致失败
- **修复**: 将`FULL_DATASET`创建块（mktemp+symlink farm+N_TASKS计数）移到harbor循环**之前**（新line 88-94），确保`-p "${FULL_DATASET}"`引用有效
- 验证: `bash -n` syntax OK，grep确认FULL_DATASET在line 88（harbor loop在line 112之前）
- **这是R476创建脚本时遗留的顺序错误，若不修复7x89并发会全部失败**

**② 镜像拉取进度（81/89 present, 8 missing）**
- 从R476的55/89增长到81/89（+26个，retry脚本pulled=18 + 主脚本 + helper）
- 8个仍缺失: make-mips-interpreter, mcmc-sampling-stan, merge-diff-arc-agi-task, model-extraction-relu-logits, modernize-scientific-stack, mteb-leaderboard, mteb-retrieve, multi-source-data-merger
- 两个脚本并行拉取: ①retry脚本(PID 3788007)在make-mips-interpreter ②helper pull脚本(PID 2248679)在multi-source-data-merger（已拉nginx-request-logging+openssl-selfsigned-cert）
- ETA: ~30min完成剩余8个

**③ v2 串行运行状态（3/7 harness DONE, opencode RUNNING）**
- cline-patched: DONE 0/15 (15 RuntimeError — TB_API_KEY未export bug, 已修)
- codex: DONE 6/14 PASS (42.9%) — PASS: adaptive-rejection-sampler, build-pov-ray, configure-git-webserver, fix-git, git-multibranch, log-summary-date-ranges; 7 exceptions (6 AgentTimeout + 1 VerifierTimeout); runtime 3h6m
- hermes: DONE 0/9 (6 RuntimeError exceptions, 9 completed all 0.0); runtime 37m46s
- opencode: RUNNING (~68min, on build-pmars task)
- 剩余: claude-code, deepseek-harness, pi
- **v2只跑15题（镜像不全时的子集），7x89将覆盖全量89题**

**④ 切换计划（镜像补齐后）**
- 镜像89/89后: 记录v2进度（3 DONE + opencode partial），可停v2或等opencode完成
- 启动7x89并发（launcher已修复）: 623 trials, 7-way concurrent, ETA ~2.5-3h
- v2的15题结果作为preliminary sanity check，7x89的89题结果作为正式报告数据

### 本唤醒流水
[13:51] R477 **7x89启动器BUG修复+镜像81/89+v2 opencode运行中**. ①FIXED critical bug: FULL_DATASET defined after harbor loop → moved before loop ②Images 55→81/89, 8 missing, both pull scripts running ③v2: cline 0/15(bug), codex 6/14 PASS(42.9%), hermes 0/9(6 RuntimeError), opencode RUNNING(~68min) ④Helper pull script started for remaining images ⑤Volume: TASK=32KB/MEMORY=14KB. WAITING=1.
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
