# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1

## 📊 进度快照

```
PHASE:        T2 Terminal-Bench 7x89 CONCURRENT RUNNING (~10.3h elapsed, 5/7 harbor alive) + SWE-bench Verified 后台下载进行中(152/500 pulled). 两线并列.
已完成:       H-B 7way ctx compression report✅·Gate 7/7✅(R466)·7x89 concurrent LAUNCHED✅(R479)·SWE-bench Verified 体积估算✅(R480)·下载脚本+后台启动✅(R480)·TASK归档✅(R481)·hermes+deepseek 87/87 FINISHED✅(R484)·R485双线监控✅
当前动作:     R486: 双线并列监控. ①TB 7×89 并发~10.3h(16:21起,现02:42),5 harbor alive(hermes+deepseek已FINISHED 87/87). 精确统计(verifier/reward.txt口径,/tmp/tb_7x89/jobs_*): cline-patched 46dirs/43done(25P/18F=58.1%,2err), codex 72dirs/30done(13P/17F=43.3%,41err!), opencode 41dirs/35done(20P/15F=57.1%,5err), pi 45dirs/40done(19P/21F=47.5%,5err), claude-code 32dirs/15done(0P/15F=0%,16err), hermes 87/87 FIN(0P/50F,37err), deepseek 87/87 FIN(0P/50F,37err). 5 containers running,load 11.53(TB未受下载影响). ⚠️codex 41err/71attempted(58%错误率,适配器问题);hermes/deepseek 0%+37err(疑似适配器bug);claude-code最慢32/87(0%+16err);cline/opencode/pi三路健康47-58%. ②SWE-bench Verified 下载: 152/500 pulled,0 failed,PID 1199724 alive(~7.3h=26366s). 实测~20.8/h,ETA~17h→10-25 19:30. Docker 263 images(152 swebench),/data 764G used/6.3T free(11%). ③体积估算(R480已交付):500镜像,dedup~30-60GB,sum(raw)~575GB,磁盘6.3T free→✅够;瓶颈=Docker Hub匿名限速(100 manifest/h/共享IP),非磁盘/带宽.
下一步:       ①TB 5存活harness待完成(claude-code 32/87最慢约18h,codex 72/87近完成,cline/opencode/pi ~41-46/87),全量完成后→McNemar配对报告(中文HTML),codex/hermes/deepseek/claude-code高err需标注"疑似适配器bug" ②SWE-bench 下载持续(~20.8/h,ETA~10-25 19:30),监控pull_progress.txt ③TB完成后:7 harness × 500 题 SWE-bench Verified 横评
阻塞:         无. TB 在跑(5路存活,claude-code拖长至~18h); SWE-bench 下载受 Docker Hub 匿名限速(100 manifest/h,共享IP 203.127.181.131),实测~20.8/h. ⚠️codex 41err(适配器问题); hermes/deepseek 37err(RuntimeError/NonZeroAgentExit,适配器bug);claude-code 16err.
ERROR_COUNT:  1
📦 体积：TASK=29KB / MEMORY=24KB（归档 0KB）
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
[02:42] R486 **双线并列监控(TB 10.3h + SWE-bench 152/500)**. ①TB 7×89 并发~10.3h(16:21起,现02:42),5 harbor alive(hermes+deepseek已FINISHED 87/87). 精确统计(verifier/reward.txt口径, 遍历 /tmp/tb_7x89/jobs_<h>/2026-10-24__16-21-*/<task>/): cline-patched 46dirs/43done(25P/18F=58.1%,2err), codex 72dirs/30done(13P/17F=43.3%,41err!), opencode 41dirs/35done(20P/15F=57.1%,5err), pi 45dirs/40done(19P/21F=47.5%,5err), claude-code 32dirs/15done(0P/15F=0%,16err), hermes 87/87 FIN(0P/50F,37err), deepseek 87/87 FIN(0P/50F,37err). 5 docker containers running(gcode-to-text/make-mips-interpreter/largest-eigenval/make-doom-for-mips/reshard-c4-data),load 11.53(TB未受下载影响). ⚠️codex 41err/71attempted(58%错误率,适配器问题);hermes/deepseek 0%+37err(疑似适配器bug);claude-code最慢32/87(0%+16err);cline/opencode/pi三路健康47-58%. ②SWE-bench Verified下载: 152/500 pulled,0 failed,PID 1199724 alive(etimes=26366s~7.3h,父1199726睡+子537227拉django-14351). 实测~20.8/h,ETA~17h→10-25 19:30. Docker 263 images(152 swebench),/data 764G used/6.3T free(11%). ③体积估算(R480已交付swebench_verified_volume_estimate.txt):500镜像,75manifest实测dedup 85.3%共享层,去重后~30-60GB,sum(raw)~575GB,磁盘6.3T free→✅够;瓶颈=Docker Hub匿名限速(100 manifest/h/共享IP 203.127.181.131),非磁盘/带宽. ④git:工作副本有未提交swebench_verified_pull_progress.txt(loop外实时更新,本轮将提交). ⑤体积:TASK=29KB/MEMORY=24KB. WAITING=1.

[01:27] R485 **双线并列监控(TB 9.1h + SWE-bench 127/500)**. ①TB 7×87 并发~9.1h(16:21起,现01:27),5 harbor alive(hermes+deepseek已FINISHED 87/87). 精确统计(per-task result.json存在+verifier/reward.txt==1): cline-patched 39/87 done(19P=48.7%,11err), codex 68/87 done(11P=16.2%,50err!), opencode 36/87(16P=44.4%,13err), pi 40/87(15P=37.5%,11err), claude-code 31/87(0P=0%,24err), hermes 87/87 FIN(0P=0%,37err=36RuntimeError+1VerifierTimeout), deepseek 87/87 FIN(0P=0%,37err=35NonZeroAgentExit+2VerifierTimeout). ⚠️codex 50err/68done(74%错误率!);claude-code最慢31/87且0%+24err;cline/opencode/pi三路健康37-49%. ②SWE-bench Verified下载: 127/500 pulled(astropy22+django105),0 failed, PID 1199724 alive(etimes=22027s~6.1h,正在拉django-13794). 实测~20.8/h,ETA~18h→10-25 19:25. Docker 239 images(128 swebench),/data 757G used/6.3TB free(11%). load avg 27.4/224CPU,5 docker containers running(TB未受下载影响). ③hermes/deepseek trace确认:总runtime 6h57m/7h03m,harbor表格reward 0.0|50,异常=36 RuntimeError(hermes)/35 NonZeroAgentExitCode(deepseek)→高度疑似适配器bug非能力(LiteLLM model cost fetch Errno101是预期,loop剥代理所致). ④git pull:origin/main领先(loop R484 auto-commit db23500a8@00:20已推,本工作副本有未提交swebench_verified_pull_progress.txt是loop外更新). ⑤体积:TASK=29KB/MEMORY=22KB. WAITING=1.

[00:18] R484 **双线并列监控(TB 7.9h + SWE-bench 94/500)**. ①TB 7×87 并发~7.9h(16:21起),5 harbor alive(hermes+deepseek已FINISHED 87/87). 精确统计(top-level result.json→stats.evals.metrics[0].mean): cline-patched 33/87 done(17P/14F=51.5%,8err), codex 60/87 done(10P/13F=16.7%,46err!), opencode 30/87(14P/13F=46.7%,11err), pi 33/87(14P/16F=42.4%,9err), claude-code 26/87(0P/13F=0.0%,22err), hermes 87/87 FIN(0P/50F=0.0%,37err), deepseek 87/87 FIN(0P/50F=0.0%,37err). ⚠️codex 60done但46err(76%错误率!仅23 eval trial=非error完成);claude-code最慢26/87且0%+22err; cline/opencode/pi三路健康42-52%. ②SWE-bench Verified下载: 94/500 pulled(astropy22+django72),0 failed, PID 1199724 alive(etimes=17622s~4.9h). 实测~19/h,ETA~21h→10-25 21:00. Docker 207 images,/data 752G used/6.3TB free(11%). load avg 11.8/224CPU(TB未受下载影响). ③R483 push已通过(loop auto-commit fe4c147a9@23:07已推,git status无ahead). ④体积:TASK=29KB/MEMORY=21KB. WAITING=1.

[23:01] R483 **双线并列监控(TB 6.7h + SWE-bench 65/500)**. ①TB 7×87 并发~6.7h(16:21起),7 harbor alive. 实测完成(reward=verifier_result.rewards.reward>0): cline-patched 31/87(16P=51.6%), opencode 28/87(12P=42.9%), pi 31/87(13P=41.9%), codex 27/87(9P=33.3%), hermes 82/87(0P=0%,35exc), deepseek-harness 82/87(0P=0%,35exc), claude-code 24/87(0P=0%,19exc). ⚠️hermes/deepseek近完成(82/87)但全fail+35exc(快速空提交/适配器bug?),claude-code最慢且全fail; cline/opencode/pi/codex四路健康33-52%. ②SWE-bench Verified下载: 65/500 pulled(astropy22+django43),0 failed, PID 1199724 alive(3h43m,原始进程). 实测~17/h(含首张429退避),稳定后~20/h,ETA~26h→10-26 01:00. Docker 175 images/407.5GB,/data 6.3TB free. ③load avg 17/224CPU(TB未受下载影响). ④kill了2个重复pull进程(PID 758911@22:58 + 882408@23:00,疑似loop重复启动;只留原始PID 1199724). ⑤体积:TASK=29KB/MEMORY=20KB. WAITING=1.

[21:50] R482 **双线并列监控(TB 5.5h + SWE-bench 30/500)**. ①TB 7×87 并发~5.5h(16:21起),7 harbor alive. 实测完成: cline-patched 27/87(13P=48%), opencode 24/87(11P=46%), pi 25/87(10P=40%), codex 21/87(9P=43%), hermes 74/87(0P=0%), deepseek-harness 74/87(0P=0%), claude-code 21/87(0P=0%). ⚠️hermes/deepseek近完成但全fail(快速空提交),claude-code慢且全fail; cline/opencode/pi/codex四路健康40-48%. ②SWE-bench Verified下载: 30/500 pulled(astropy22+django8),0 failed, PID 1199724 alive(etimes~8900s). 首张429退避40min后恢复,image10/30各遇1-2次Service Unavailable(30s退避恢复). 实测~17/h,ETA~28h→10-26 02:00. Docker 140 images/400.6GB,/data 6.3TB free. ③load avg 124/224CPU,TB未受下载影响(TB 89张已全拉完,不竞争Docker Hub限速). ④体积:TASK=29KB/MEMORY=19KB. WAITING=1.

[20:33] R481 **双线并列监控+TASK归档**. ①TB 7×87 并发~4.1h(16:21起),7 harbor alive. 实测完成进度(verify reward.txt): cline-patched 20/87(10P=50%), opencode 19/87(10P=52.6%), pi 20/87(10P=50%), codex 14/87(6P=42.9%), claude-code 8/87(0P=0%), hermes 36/87(0P=0%), deepseek-harness 37/87(0P=0%). ⚠️hermes/deepseek 快但全 fail(疑似快速空提交),claude-code 慢且全 fail. ②SWE-bench Verified 下载: 4/500 pulled(astropy 4张),脚本PID 1199724运行中,限速窗口已滑动(首张429退避8×300s=40min后成功,后续3张连续成功). /data 6424GB free,Docker Root=/data/docker,116 images. ③TASK归档: 09:2x+09:0x两块原文移入ARCHIVE_OPERATOR_HARNESS.md(留指针),TASK 35KB→29KB. ④sg docker -c 可用(无需sudo). ⑤体积:TASK=29KB/MEMORY=19KB. WAITING=1.

[19:20] R480 **SWE-bench Verified 镜像下载启动(后台)+体积估算交付**. ①TB 7×87 并发仍在跑(16:21启动,~2.7h,7 harbor alive,load 7.6). ②查清 SWE-bench Verified 镜像命名=swebench/sweb.eval.x86_64.<instance_id,__→_1776_>:latest(swebench harness expected_image/namespace=swebench;实测 docker manifest inspect OK). ③去重体积估算: 抓 75/500 manifest(受 Docker Hub 限速,见下),实测 85.3% 层共享,raw 86.1GB/75张,dedup 12.0GB/75张,单张 avg 1.15GB,外推500张 raw~575GB/dedup~30-60GB. 磁盘 /data 6.3TB free → 充足. ④🔴关键发现: Docker Hub 匿名限速 Ratelimit-Limit=100;w=3600(100 manifest请求/1h滑动窗口),出口IP=203.127.181.131(92.25代理共享),当前 Remaining=0. layer 下载不计入限速(TB 89张2.5h拉完=吻合). docker pull 遇 429 立即失败(daemon不重试). ⑤写限速下载脚本 swebench_verified_pull.sh(429→退避300s×15次,串行,TB在跑pause 5s,批间查磁盘<50GB暂停,幂等跳过已存在)+后台启动(PID 1199724,当前 429 退避中,等窗口滑动). ⑥交付: swebench_verified_volume_estimate.txt(报告)+estimate.py(脚本)+manifests.json(75缓存)+image_list.txt(500清单)+pull.sh(下载脚本). ⑦体积: TASK=34KB(>32KB目标但<40KB红线,3个活跃运维块不可归档)/MEMORY=18KB. WAITING=1.

[16:25] R479 **v2串行已kill+7x89并发已启动(7-way concurrent, 609 trials)**. ①Auto-transition timed out (60min, only 87/89). ②Updated v2 partial results: cline-patched 0/15, codex 6/15 PASS, hermes 0/15, opencode 6/15 PASS (13/15 completed, 5 AgentTimeoutError). ③Killed v2 serial (PID 1068001) + gw_proxy + all leftover containers. ④Modified _full_7x89_concurrent_launcher.sh: skip missing images (filtered dataset of 87 tasks, not hard-exit). ⑤Launched 7x89 concurrent at 16:21: 7 harnesses × 87 tasks = 609 trials, 7-way concurrent. All 7 harbor processes alive (PIDs 536814-578125), 7 Docker containers running. cline-patched TB_API_KEY fix verified (agent setting up, no RuntimeError). gw_proxy healthy on 9090/9091. ⑥Resources: 224 CPUs, 2TB RAM, load 9.15, 92% CPU idle — ample. ⑦2 images still pulling in background (mteb-leaderboard, mteb-retrieve). ⑧Volume: TASK=32KB/MEMORY=17KB. WAITING=1.

[15:06] R478 **镜像87/89+v2部分结果已保存+auto-transition脚本已启动**. ①Images 81→87/89. ②v2 serial: 4/7 harnesses have results. ③Saved v2 partial results. ④Created+launched auto-transition script. ⑤Resources ample. WAITING=1.
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
> **A**: **已完成！** R479 (16:21) 启动 7x89 并发：7 harnesses × 87 tasks = 609 trials, 7-way concurrent。每 harness 独立 jobs-dir 在 /tmp（避免 NFS stale handle），共享 gw_proxy (9090/9091)。v2 串行已 kill（部分结果已保存）。ETA ~2.5-3h。口径声明：7-way concurrent（与之前串行结果不可直接比）。

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
