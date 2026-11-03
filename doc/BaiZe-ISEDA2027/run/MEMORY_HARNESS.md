# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1424 incr_eval轮:CPU/MEM自检PASS+scan_backlog=1→0·predict:cline500(DONE)·opencode500(DONE)·pi475(DONE)·claude-code433(DONE)·codex406/500(alive)·hermes268/500(alive)·deepseek163/500(alive)
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1423 incr_eval链+内存/CPU自检+体积归档✅·R1409 CPU失控kill+护栏修复✅·R1424 incr_eval 1项+CPU/MEM自检PASS
当前动作:     R1424:CPU自检PASS(运维令11-02:load34/224≈15%busy,无本线>8000%CPU,无容器失控)+内存自检PASS(运维令10-30:MemAvailable1.41TB,无本线RSS>50GB)·scan_backlog=1→0(hermes scikit-learn-25973)·incr_eval 1项:hermes scikit-learn-25973 RESOLVED✅(OMP_NUM_THREADS=8,nice19,EVAL_MAX_WORKERS=1护栏)·eval TOTAL 2420/1858(+1/+1)(权威:cline442(326)·opencode497(401)·pi463(333)·claude-code358(273)·codex303(239)·hermes200(156)·deepseek157(130))·3路predict alive无stuck:codex406/500·hermes268/500·deepseek163/500·硬约束:predictions 0 tracked✅·eval 0 tracked✅·docker 0 running✅·/data 6.0T free✅·load34/224✅·无kill·无失控·未完成指令:有(3路predict仍跑)⇒WAITING=0.
下一步:       ①3路predict alive(codex406/500·hermes268/500·deepseek163/500) ②每轮scan_backlog→incr_eval新完成predict ③监控CPU(护栏OMP_NUM_THREADS=8) ④predict全完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ⑤infra单列(铁律④) ⑥永久硬约束:禁止commit结果JSON ⑦TASK=34.9KB·MEMORY≤32KB
阻塞:         无(3路predict alive progressing·CPU护栏已加·load34/224健康). git:需提交(R1424心跳).
ERROR_COUNT:  0
  📦 体积：TASK=35757B(34.9KB,>32KB,3活跃块不可归档,<40KB红线OK) / MEMORY≈17.5KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[14:32] R1424 incr_eval轮: CPU自检PASS(load34/224≈15%busy,无本线>8000%CPU,无容器/pytest失控,docker ps空)+内存自检PASS(1.41TB avail,无本线RSS>50GB)·scan_backlog=1→0(hermes scikit-learn-25973)·incr_eval 1项:hermes scikit-learn-25973 RESOLVED✅(OMP_NUM_THREADS=8,nice19,EVAL_MAX_WORKERS=1,setsiddetach)·eval 2420/1858(+1/+1,hermes200(156))·3路predict alive无stuck(codex406·hermes268·deepseek163)·硬约束全PASS·无kill·无失控

> 📦 R1423 流水(14:21,incr_eval轮:CPU/MEM自检PASS+scan_backlog=1→0,deepseek django-15368 RESOLVED,eval 2419/1857)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1422 流水(14:13,incr_eval轮:CPU/MEM自检PASS+scan_backlog=3→0,hermes scikit-learn-25931 RESOLVED+codex sympy-13798 FAILED+deepseek django-15315 RESOLVED,eval 2418/1856)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1421 流水(13:55,incr_eval轮:CPU/MEM自检PASS+scan_backlog=1→0,codex sympy-13757 RESOLVED,eval 2415/1854)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1420 流水(13:46,incr_eval轮:CPU/MEM自检PASS+scan_backlog=1→0,codex sympy-13647 RESOLVED,eval 2414/1853)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1419 流水(13:32,quiet监控轮:CPU/MEM自检PASS+scan_backlog=0,eval 2413/1852 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1418 流水(13:23,incr_eval轮:CPU/MEM自检PASS+scan_backlog=1→0,deepseek django-15278 RESOLVED,eval 2413/1852)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1401 流水(10:35,quiet监控轮:内存自检440th+CPU PASS+scan_backlog=0,eval 2401/1840 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1402 流水(10:43,quiet监控轮:内存自检441st+CPU PASS+scan_backlog=0,eval 2401/1840 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。

> 📦 R1403 流水(10:58,incr_eval轮:内存自检442nd+CPU PASS+scan_backlog=1→0,hermes sklearn-14087 FAILED)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2402/1841(+1/+1)·3路predict alive。需要时再读。

> 📦 R1404 流水(11:06,incr_eval轮:内存自检443rd+CPU PASS+scan_backlog=1→0,hermes sklearn-14141 RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2403/1842(+1/+1)·3路predict alive。需要时再读。

> 📦 R1405 流水(11:16,incr_eval轮:内存自检444th+CPU PASS+scan_backlog=1→0,hermes sklearn-14496 RESOLVED,eval 2404/1843)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。
> 📦 R1406-R1408 流水(11:15~11:39,quiet+incr_eval轮:内存自检445th~447th+CPU PASS,scan_backlog 0→1→0,hermes sklearn-14629 RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2405/1844·3路predict alive。需要时再读。
> 📦 R1409-R1412 流水(11:52~12:24,CPU失控kill+护栏修复+incr_eval链:codex+2·hermes+3 resolved,eval渐进2405→2410/1844→1849)已合并归档 → daily-memories-harness/2026-11-03.md。结论：CPU护栏OMP=8已加·eval稳步增长·3路predict alive。需要时再读。
> 📦 R1413 流水(12:34,quiet监控轮:CPU/MEM自检PASS+scan_backlog=0,eval 2410/1849 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。
> 📦 R1414 流水(12:42,incr_eval轮:CPU/MEM自检PASS+scan_backlog=1→0,deepseek django-15277 RESOLVED,eval 2411/1850(+1/+1))已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek resolved 127(+1)·3路predict alive。需要时再读。
> 📦 R1415 流水(12:52,quiet监控轮:CPU/MEM自检PASS+scan_backlog=0,eval 2411/1850 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。
> 📦 R1416 流水(13:02,quiet监控轮:CPU/MEM自检PASS+scan_backlog=0,eval 2411/1850 unchanged)已归档 → daily-memories-harness/2026-11-03.md。结论：3路predict alive。需要时再读。
[13:13] R1417 incr_eval轮:CPU自检PASS(运维令11-02:load36.71/224≈16%busy,无本线>8000%CPU,无容器失控)+内存自检PASS(运维令10-30:MemAvailable1.41TB,无本线RSS>50GB,最高cline-hub3.5GB)·scan_backlog=1→0(hermes sklearn-25232 real patch patchlen=4309,run_single已EXITED→final)·incr_eval_R1417.sh(OMP=8护栏,max_workers=2):merge hermes 198 real patches→sg docker swebench run_evaluation→regen_eval_summaries→hermes sklearn-25232 RESOLVED·eval TOTAL 2412/1851(+1/+1)(权威:cline442(326)·opencode497(401)·pi463(333)·claude-code358(273)·codex300(237)·hermes198(154)·deepseek154(127))·3路predict alive无stuck:codex402/500(sympy-13615,same)·hermes265/500(advanced to sklearn-25747)·deepseek161/500(django-15278 done,transitioning to next)·硬约束:predictions 0 tracked✅·eval 0 tracked✅·docker 0 running✅·/data 6.0T free✅·load36/224✅·无kill·无失控·未完成指令:有(3路predict仍跑)⇒WAITING=0.

> 📦 R1400 流水(10:27,incr_eval轮:内存自检439th+CPU PASS+scan_backlog=1→0,hermes sklearn-14053 RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2401/1840(+1/+1)·3路predict alive。需要时再读。

> 📦 R1399 流水(10:12,incr_eval轮:内存自检438th+CPU PASS+scan_backlog=3→0,hermes sklearn-13496/13779 both RESOLVED+deepseek django-15127 RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2400/1839(+3/+3)·3路predict alive。需要时再读。

> 📦 R1398 流水(10:00,incr_eval轮:内存自检437th+CPU PASS+scan_backlog=2→1→0,hermes sklearn-13439 unresolved+deepseek django-15103/15104 both RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2397/1837(+3/+2)·3路predict alive。需要时再读。

> 📦 R1397 流水(09:47,incr_eval轮:内存自检436th+CPU PASS+scan_backlog=1→0,hermes sklearn-13328 unresolved/ambiguous)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2394/1834(+1/+0)·3路predict alive。需要时再读。

> 📦 R1396 流水(09:33,incr_eval轮:内存自检435th+CPU PASS+scan_backlog=1→0,hermes sklearn-13142 RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2393/1834(+1/+1)·3路predict alive。需要时再读。

> 📦 R1395 流水(09:19,quiet监控轮:内存自检434th+CPU PASS+scan_backlog=0)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2392/1833 unchanged·3路predict alive。需要时再读。

> 📦 R1394 流水(09:12,incr_eval轮:内存自检433rd+CPU PASS+scan_backlog=2→0,2items 1RESOLVED+1FAILED)已归档 → daily-memories-harness/2026-11-03.md。结论：codex sympy-12096 RESOLVED✅+hermes sklearn-13135 FAILED·eval 2392/1833(+2/+1)·3路predict alive。需要时再读。

> 📦 R1393 流水(09:04,quiet监控轮:内存自检432nd+CPU PASS+scan_backlog=0)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2390/1832 unchanged·3路predict alive。需要时再读。

> 📦 R1392 流水(08:52,incr_eval轮:内存自检431st+CPU PASS+scan_backlog=1→1→0,2backlog ALL RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：codex sphinx-9711+hermes sklearn-13124 BOTH RESOLVED·eval 2390/1832(+2/+2)·3路predict alive。需要时再读。

> 📦 R1391 流水(08:41,incr_eval轮:内存自检430th+CPU PASS+scan_backlog=4→0,2/3 RESOLVED+1 FAILED)已归档 → daily-memories-harness/2026-11-03.md。结论：codex sphinx-9673+9698 BOTH RESOLVED·hermes sklearn-12682 RESOLVED+sklearn-12973 FAILED·eval 2388/1830(+4/+3)·3路predict alive。需要时再读。

> 📦 R1390 流水(08:27,quiet监控轮:内存自检429th+CPU PASS+scan_backlog=0)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2384/1827 unchanged·3路predict alive。需要时再读。

> 📦 R1389 流水(08:21,quiet监控轮:内存自检428th+CPU PASS+scan_backlog=0)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2384/1827 unchanged·3路predict alive。需要时再读。

> 📦 R1388 流水(08:14,incr_eval轮:内存自检427th+CPU PASS+incr_eval 2items 1RESOLVED+1FAILED)已归档 → daily-memories-harness/2026-11-03.md。结论：hermes sklearn-11578 RESOLVED+hermes sklearn-12585 FAILED·eval 2384/1827(+2/+1)·3路predict alive。需要时再读。

> 📦 R1387 流水(08:05,incr_eval轮:内存自检426th+CPU PASS+incr_eval 2items ALL RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：deepseek django-14999+hermes scikit-learn-11310 both RESOLVED·eval 2382/1825(+2/+2)·3路predict alive。需要时再读。

> 📦 R1386 流水(07:52,quiet监控轮:内存自检425th+CPU PASS+scan_backlog=0)已归档 → daily-memories-harness/2026-11-03.md。结论：eval 2380/1824 unchanged·3路predict alive。需要时再读。

> 📦 R1385 流水(07:46,incr_eval轮:内存自检424th+CPU PASS+incr_eval 1item RESOLVED)已归档 → daily-memories-harness/2026-11-03.md。结论：hermes scikit-learn-10908 RESOLVED·eval 2380/1824(+1/+1)·3路predict alive。需要时再读。

> 📦 R1383-R1375 流水(06:00~07:3x,~9轮incr_eval+quiet:内存自检414th~423rd+CPU PASS,scan_backlog逐轮清零)已合并归档 → daily-memories-harness/2026-11-03.md。结论：eval渐进2358→2380/1803→1824·3路predict alive。需要时再读。

> 📦 R1374-R1365 流水(04:17~05:39,~10轮incr_eval+quiet+scan_backlog:内存自检401st~412th+CPU PASS)已合并归档 → daily-memories-harness/2026-11-03.md。结论：eval渐进2349→2358/1794→1803·3路predict alive。需要时再读。

> 📦 R1364-R1342 流水(00:38~04:17,~23轮incr_eval+quiet:内存自检380th~400th+CPU PASS)已合并归档 → daily-memories-harness/2026-11-03.md。结论：eval渐进2324→2351/1778→1797·3路predict alive。需要时再读。

> 📦 R1341-R1135 流水(2026-11-02 21:21~2026-11-03 00:29,~21轮incr_eval+quiet+scan_backlog:内存自检363rd~380th+CPU PASS)已合并归档 → daily-memories-harness/2026-11-02.md + 2026-11-03.md。结论：eval渐进2304→2324/1766→1776·3路predict alive。需要时再读。
> 📦 R1335-R1313 流水(2026-11-02 18:01~23:22,~23轮incr_eval+quiet+scan_backlog:内存自检363rd~374th+CPU PASS,eval渐进2291→2318/1754→1775)已合并归档 → daily-memories-harness/2026-11-02.md。结论：多条incr_eval混RESOLVED/FAILED·3路predict alive·硬约束tracked=0✅。需要时再读。
> 📦 R1313-R1281 流水(2026-11-02 10:47~18:42,~33轮incr_eval+quiet:内存自检320th~362nd,eval渐进2234→2291/1707→1754)已合并归档 → daily-memories-harness/2026-11-02.md。结论：多条incr_eval混RESOLVED/FAILED·3路predict alive·硬约束tracked=0✅。需要时再读。


> 📦 R1169-R1002 流水(2026-10-31~11-01,~170轮incr_eval+quiet+内存自检:5/7 predict DONE里程碑·eval稳步增长·4-5路predict alive)已合并归档 → daily-memories-harness/2026-11-01.md + 2026-10-31.md + 2026-10-30.md。结论：内存全PASS无失控·多条incr_eval混RESOLVED/FAILED·硬约束tracked=0✅。需要时再读。

> 📦 R1002-R821 流水(2026-10-30~10-31,~215轮incr_eval+监控+predict推进)已归档 → daily-memories-harness/2026-10-30.md + 2026-10-31.md。结论：eval稳步增长·predict 4路alive·硬约束tracked=0✅。需要时再读。

> 📦 R820-R113 流水(2026-10-04~29,~700轮: 早期SWE-bench pipeline+7×300横评+glm53报告+TB pilot+H-B源码分析+适配器修复+full500 predict启动+GATE v2+常态巡检)已合并归档 → daily-memories-harness/2026-10-04.md~2026-10-29.md + run/ARCHIVE_OPERATOR_HARNESS.md。结论：5路predict持续健康推进·全路timeout=0·infra单列·hermes/deepseek闸门FAIL未进全量·pilot20已交付(cline13/20=65%·hermes11/20=55%)·GATE v2 5路PASS·2路FAIL。需要时再读。

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

> 📦 R35-R112 (2026-10-02~04, H-B 源码分析启动 + SWE-bench 可行性核查) 已归档 → daily-memories-harness/2026-10-02.md ~ 2026-10-04.md。需要时再读。最新流水见上方「本唤醒流水」。
