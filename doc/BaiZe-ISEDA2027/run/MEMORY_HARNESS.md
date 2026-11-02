# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1327 内存自检366th PASS+CPU自检PASS+incr_eval 1item RESOLVED✅·eval TOTAL=2307/1767(+1/+1)·predict:cline500(DONE)·opencode500(DONE)·pi475(DONE)·claude-code433(DONE)·codex361(alive,跑sphinx-7748)·hermes205(alive,跑xarray-6461)·deepseek128(alive,跑django-14089)(3路alive:codex 361/500·hermes 205/500·deepseek 128/500)
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1325 incr_eval链+内存/CPU自检+体积归档✅·R1326 内存自检365th+CPU自检PASS✅·R1327 内存自检366th+CPU自检PASS+incr_eval hermes xarray-4966 RESOLVED✅
当前动作:     R1327:内存自检366th PASS(运维令10-30)+CPU自检PASS(运维令11-02)+incr_eval 1item DONE:MemAvail≈1.4TiB(426G used)·load28/224核≈12%busy·无本线>50GB(最大本线=opencode 1.16GB)·无本线>8000%CPU(本线最高=opencode 6.5%·hermes kernel 7.7%;pretrain 140%非本线不碰)·无partitions()/list()失控✅·eval容器短暂运行(xarray-4966 eval,containerd-shim 0.0%CPU,正常完成已stop)✅·docker 0 running✅. scan_backlog=1(hermes xarray-4966 patchlen=3278)→setsid incr_eval_backlog.py(EVAL_MAX_WORKERS=1):hermes pydata__xarray-4966 RESOLVED✅(~53s,21:55:10→21:56:03,rc=0,FAIL_TO_PASS 4/4+PASS_TO_PASS 22/22全通过,0 infra). eval TOTAL 2306/1766→2307/1767(+1 eval,+1 resolved):cline442(326)·codex276(217)·opencode497(401)·pi463(333)·claude-code358(273)·hermes149(116,+1/+1)·deepseek122(101). 复scan_backlog=0✅. 3路alive:codex跑sphinx-7748·hermes跑xarray-6461·deepseek跑django-14089·均未stuck. 硬约束:eval_*.json gitignored✅·predictions 0 tracked✅·/data 6.0T free(15%)✅·docker 0 running✅
下一步:       ①3路predict alive(codex 361/500·hermes 205/500·deepseek 128/500) ②每轮scan_backlog(with-patch)→incr_eval新产出 ③predict全完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ④infra单列(铁律③) ⑤永久硬约束:禁止commit结果JSON ⑥TASK=34.9KB·MEMORY≤32KB
阻塞:         无(3路predict alive;本轮自检quiet无失控,无kill;incr_eval 1item RESOLVED). git:clean(behind=0).
ERROR_COUNT:  0
  📦 体积：TASK=35757B(34.9KB,>32KB,2活跃块不可归档,<40KB红线OK) / MEMORY=归档后≤32KB(本轮归档R1324-R1325→daily-memories-harness/2026-11-02.md)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> 📦 R1324 流水(21:21,内存自检363rd+incr_eval 2items both FAILED)已归档 → daily-memories-harness/2026-11-02.md。结论：codex sphinx-7462 FAILED+hermes xarray-4687 FAILED·eval 2304→2306(+2/+0)·3路predict alive。需要时再读。
> 📦 R1325 流水(21:32,内存自检364th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-02.md。结论：scan_backlog=0无incr_eval·eval 2306/1766 unchanged·3路predict alive。需要时再读。
> 📦 R1326 流水(21:38,内存自检365th+CPU自检PASS,无kill)已归档 → daily-memories-harness/2026-11-02.md。结论：自检quiet·eval 2306/1766 unchanged·hermes→204·3路predict alive。需要时再读。
> [21:45] R1327 内存自检366th PASS+CPU自检PASS+incr_eval 1item RESOLVED✅ DONE:MemAvail≈1.4TiB(426G used)·load28/224核≈12%busy·无本线>50GB(最大opencode 1.16GB)·无本线>8000%CPU(本线最高opencode 6.5%·hermes kernel 7.7%;pretrain 140%非本线不碰)·无partitions()/list()失控✅·docker 0 running(eval前0,eval中1容器xarray-4966 0.0%CPU正常,eval后0)✅. scan_backlog=1(hermes xarray-4966 patchlen=3278)→第1次nohup被tool timeout杀→清理orphaned docker container(docker rm -f)→第2次setsid detached成功:incr_eval_backlog.py(EVAL_MAX_WORKERS=1):hermes pydata__xarray-4966 RESOLVED✅(~53s,21:55:10→21:56:03,rc=0,FAIL_TO_PASS 4/4+PASS_TO_PASS 22/22全通过,0 infra,无CPU失控). eval TOTAL 2306/1766→2307/1767(+1 eval,+1 resolved):cline442(326)·codex276(217)·opencode497(401)·pi463(333)·claude-code358(273)·hermes149(116,+1/+1)·deepseek122(101). 复scan_backlog=0✅. predict FILES:codex361(+1,跑sphinx-7748)·hermes205(+1,跑xarray-6461)·deepseek128(unchanged,跑django-14089). 3路alive且活跃·均未stuck. 硬约束:eval_*.json gitignored✅·predictions 0 tracked✅·disk /data 6.0T free(15%)✅·docker 0 running✅·未完成指令:有(10-30内存自检常驻+11-02 CPU自检常驻+10-28full500 3路predict仍跑)⇒WAITING=0.

> 📦 R1322 流水(20:44,内存自检361st+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-02.md。结论：MemAvail≈1.5TiB PASS·scan_backlog=1(codex sphinx-7440 no_patch)→TRUE_backlog=0·eval TOTAL=2302/1764 unchanged·3路predict alive。需要时再读。
> [20:56] R1323 内存自检362nd PASS+CPU自检PASS+incr_eval 2items全RESOLVED✅ DONE:MemAvail≈1482GB(422G used)·load24.86/224核≈11%busy·无本线>50GB(最大本线=predict runners~241MB)·无本线>8000%CPU(本线predict runners 0.0%等API;最高CPU=pretrain lmeval 516%非本线,不碰)·无partitions()/list()失控✅·docker 0 running(eval前后均0)✅. scan_backlog=2(hermes xarray-4356 patchlen=986·hermes xarray-4629 patchlen=501)→re-merge predictions_hermes.json(147 preds)→incr_eval_backlog.py(EVAL_MAX_WORKERS=2,nice -n 19,setsid detached):hermes pydata__xarray-4356 RESOLVED✅+pydata__xarray-4629 RESOLVED✅(~73s,20:54:18→20:55:31,rc=0,无CPU失控,0 infra,2/2 ran successfully). eval TOTAL 2302/1764→2304/1766(+2 eval,+2 resolved):cline442(326)·codex275(217)·opencode497(401)·pi463(333)·claude-code358(273)·hermes147(115,+2/+2)·deepseek122(101). 复scan_backlog=0✅. predict FILES:codex358(unchanged,跑sphinx-7454)·hermes202(+2,跑xarray-4687)·deepseek128(unchanged,跑django-14034). 3路alive且活跃·均未stuck. 硬约束:eval_*.json gitignored✅(0 tracked,500 tracked全为instances/input)·predictions 0 tracked✅·disk /data 6.0T free(15%)✅·docker 0 running✅. git:发现ZhuLong report_benchmark_11_02.html stale UU冲突态(无活跃merge/rebase,文件含<<<<<<<冲突标记,他线在途文件)阻塞共享仓库pull/commit→`git reset HEAD -- <该文件>`清除index冲突态(工作树md5未变e8704458...,未暂存/未提交该他线文件,留为他线M态)·index.lock因pretrain agent并发git偶现→待重试pull/commit/push. 未完成指令:有(10-30内存自检常驻+11-02 CPU自检常驻+10-28full500 3路predict仍跑)⇒WAITING=0.
> [20:33] R1321 内存自检360th PASS+CPU自检PASS(运维令10-30 11:1x+11-02 11:2x)+incr_eval 2items全RESOLVED✅ DONE:MemAvail≈1.5TiB(417G used)·load24.9→29.1/224核≈13%busy·无本线>50GB(最大本线=opencode 3.7GB)·无本线>8000%CPU(eval swebench 43%=0.43核;hermes predict 1.7%;runners<1%)·无partitions()/list()失控✅·docker 0 running(eval前后均0)✅. scan_backlog=2(hermes xarray-4075 patchlen=1363·hermes xarray-4094 patchlen=1393)→re-merge predictions_hermes.json(145 preds)→incr_eval_R1321.sh(swebench docker,max_workers=2):hermes pydata__xarray-4075 RESOLVED✅+pydata__xarray-4094 RESOLVED✅(~36s total,20:32:23→20:33:03,rc=0,无CPU失控,0 infra,2/2 ran successfully). eval TOTAL 2300/1762→2302/1764(+2 eval,+2 resolved):cline442(326)·codex275(217)·opencode497(401)·pi463(333)·claude-code358(273)·hermes145(113,+2)·deepseek122(101). 复scan_backlog=0✅·TRUE_backlog=0. predict FILES:codex357(unchanged,跑sphinx-7440)·hermes200(+2,跑xarray-4356)·deepseek128(unchanged,跑django-14017). no_patch:cline58·codex82·opencode3·pi12·claude-code75·hermes55·deepseek6(共291). 3路alive且活跃·均未stuck. 硬约束:eval_*.json gitignored✅(0 tracked)·predictions 0 tracked✅·disk /data 6.0T free(15%)✅·docker 0 running✅·未完成指令:有(10-30内存自检常驻+11-02 CPU自检常驻+10-28full500 3路predict仍跑)⇒WAITING=0.
> [20:19] R1320 内存自检359th PASS+CPU自检PASS+incr_eval 3items全RESOLVED✅:codex sphinx-11510+hermes xarray-3305/3677(3/3 RESOLVED)·eval 2297/1759→2300/1762(+3)·scan_backlog=0·3路predict alive. (详见 daily-memories-harness/2026-11-02.md)
> 📦 R1319 流水(2026-11-02 19:56,内存自检358th+CPU自检+incr_eval 3items hermes xarray-2905/3095/3151全RESOLVED)已归档 → daily-memories-harness/2026-11-02.md。结论：eval 2294/1756→2297/1759(+3)·scan_backlog=0·3路predict alive。需要时再读。
> 📦 R1317-R1318 流水(2026-11-02 19:27~19:39,内存自检356th-357th+scan_backlog=0维护轮)已归档 → daily-memories-harness/2026-11-02.md。结论：内存/CPU全PASS·scan_backlog=0无incr_eval·eval 2294/1756·3路predict alive。需要时再读。
> 📦 R1315-R1316 流水(2026-11-02 19:01~19:18,内存自检354th-355th+incr_eval 2items)已归档 → daily-memories-harness/2026-11-02.md。结论：内存/CPU全PASS·incr_eval hermes django-14373 RESOLVED✅·django-14376 FAILED·eval 2294/1756·scan_backlog=0·3路predict alive。需要时再读。
> 📦 [18:52] R1314 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval deepseek django-13964 RESOLVED✅·eval 2292/1755·3路predict alive。需要时再读。
> 📦 [18:42] R1313 流水已归档 → daily-memories-harness/2026-11-02.md。结论：scan_backlog=0(维护轮)·eval 2291/1754·3路predict alive。需要时再读。
> 📦 [18:36] R1312 流水已归档 → daily-memories-harness/2026-11-02.md。结论：scan_backlog=0(维护轮)·eval 2291/1754·3路predict alive。需要时再读。
> 📦 [18:27] R1311 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval hermes django-14349 RESOLVED✅·eval 2291/1754·3路predict alive。需要时再读。
> 📦 [18:17] R1310 流水已归档 → daily-memories-harness/2026-11-02.md。结论：scan_backlog=0(维护轮)·eval 2290/1753·3路predict alive。需要时再读。
> 📦 [18:01] R1309 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 4items(codex sphinx-10466 RESOLVED✅+deepseek django-13933 RESOLVED✅+hermes django-14311 FAILED+hermes django-14315 FAILED)·eval 2286/1751→2290/1753·3路predict alive。需要时再读。
> 📦 [17:50] R1308 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 2items(hermes django-14238 RESOLVED✅+deepseek django-13925 RESOLVED✅)·eval 2286/1751·3路predict alive。需要时再读。
> 📦 [17:34] R1307 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 1item(hermes django-14170 FAILED)·eval 2284/1749·3路predict alive。需要时再读。
> 📦 [17:22] R1306 流水已归档 → daily-memories-harness/2026-11-02.md。结论：scan_backlog=0(维护轮)·eval 2283/1749·3路predict alive。需要时再读。
> 📦 [17:07] R1305 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 2items(deepseek django-13821 RESOLVED✅+deepseek django-13837 FAILED)·eval 2283/1749·3路predict alive。需要时再读。
> 📦 [16:43] R1303 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 2items(codex scikit-learn-9288 RESOLVED✅+hermes django-14140 FAILED)·eval 2281/1748·3路predict alive。需要时再读。
> 📦 [16:33] R1302 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 1item(hermes django-14122 RESOLVED✅)·eval 2279/1747·3路predict alive。需要时再读。
> 📦 [15:47~16:22] R1299-R1301 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 6items(5resolved)+内存/CPU自检PASS。需要时再读。
> 📦 [15:27] R129 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 1item+内存/CPU自检PASS。需要时再读。
> 📦 [14:52] R129 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 1item+内存/CPU自检PASS。需要时再读。
> 📦 [14:34] R129 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 1item+内存/CPU自检PASS。需要时再读。
> 📦 [14:22] R1294 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval codex scikit-learn-25232 RESOLVED✅·eval 2269/1738·3路predict alive。需要时再读。
> 📦 [14:10] R1293 流水已归档 → daily-memories-harness/2026-11-02.md。需要时再读。
> 📦 [13:47] R1292 流水已归档 → daily-memories-harness/2026-11-02.md。需要时再读。
> 📦 [13:19] R1291 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 4items(codex15100 RESOLVED+codex14710 running+deepseek13590+hermes13964 pending)·eval 2261/1730。需要时再读。

> 📦 [13:12] R1290 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 4items ALL RESOLVED✅·eval 2259/1729·3路predict alive。需要时再读。

> 📦 [12:51] R1289 流水已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 6items(4RESOLVED+2FAILED)+2items in-progress·eval 2255/1725·3路predict alive。需要时再读。

> 📦 R1288 流水(12:22,内存自检327th+scan_backlog=0 quiet+硬约束清理.bak2)已归档 → daily-memories-harness/2026-11-02.md。结论：MemAvailable≈1.3TiB PASS·scan_backlog=0·eval TOTAL=2249/1721 unchanged·3路predict alive·硬约束tracked=0✅。需要时再读。

> 📦 R1287 流水(12:10,内存自检326th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-02.md。结论：MemAvailable≈1.4TiB PASS·scan_backlog=0·eval TOTAL=2249/1721 unchanged·3路predict alive。需要时再读。

> 📦 R1286 流水(12:02,内存自检325th+incr_eval 4items ALL RESOLVED✅)已归档 → daily-memories-harness/2026-11-02.md。结论：codex+hermes+deepseek 4/4 resolved,eval 2245/1717→2249/1721。需要时再读。

> 📦 R1285 流水(11:34,内存自检324th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-02.md。结论：MemAvailable≈1.34TiB PASS·scan_backlog=0·eval TOTAL=2245/1717 unchanged·3路predict alive。需要时再读。

> 📦 R1282-R1284 流水(11:01~11:24,内存自检321st-323rd+incr_eval 7items混RESOLVED+FAILED)已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 7items(6RESOLVED+1FAILED)·eval TOTAL渐进2238→2245·3路predict alive。需要时再读。

> 📦 R1281 流水(10:47,内存自检320th+incr_eval 4items ALL RESOLVED)已归档 → daily-memories-harness/2026-11-02.md。结论：incr_eval 4items全RESOLVED·eval TOTAL 2234/1707→2238/1711·3路predict alive。需要时再读。


> 📦 R1154-R1169 流水(2026-11-01 10:34~13:36,内存自检193rd-208th,~16轮incr_eval+quiet)已合并归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·多条incr_eval混RESOLVED+FAILED·predict 5路alive·tracked=0✅。需要时再读。

> 📦 R1154-R1159 流水(2026-11-01 10:34~11:32,6轮内存自检193rd-198th+incr_eval多条BACKLOG)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1159 hermes astropy-14508 RESOLVED·R1158 deepseek django-11790 FAILED·R1157 claude-code pytest-5840 FAILED·R1156 deepseek django-11749 FAILED+opencode/pi重启·R1155 codex+deepseek各1 RESOLVED·R1154 hermes astropy-14365 FAILED。需要时再读。
> 📦 R1152-R1153 流水(2026-11-01 09:56~10:22,2轮内存自检191st-192nd+incr_eval R1153 3backlog全RESOLVED+R1152 5/7 predict DONE里程碑)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1153 incr_eval 3resolved(claude-code pylint-6528+hermes astropy-14182/14309)·R1152 5/7 predict DONE里程碑(claude-code·codex刚完成500/500)·硬约束0结果JSON tracked✅. 需要时再读。
> 📦 R1132-R1151 流水(2026-11-01 06:08~09:33,~20轮内存自检171th-190th+incr_eval多条混RESOLVED/FAILED+scan_backlog逐轮清零)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS无失控·incr_eval多条(deepseek django-11603/11551·hermes astropy-13453/13398等)·5/7 predict DONE里程碑·硬约束0结果JSON tracked✅。需要时再读。

> 📦 R1125-R1131 流水(2026-11-01 04:40~05:52,7轮内存自检164th-170th+incr_eval 6 BACKLOG处理+scan_backlog)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·incr_eval 6题(hermes sympy-24539/24562/24213 RESOLVED×deepseek django-11333 RESOLVED×claude-code django-16819 RESOLVED×R1127 kill stale pi runtests.py树)·eval hermes38→43/50→56·deepseek50→51/62→65·4路orch alive·硬约束tracked=0✅。需要时再读。

> 📦 R1118-R1124 流水(2026-11-01 03:21~04:25,4轮内存自检+incr_eval 5题(3 RESOLVED)+scan_backlog+硬约束复核)已归档 → daily-memories-harness/2026-11-01.md。结论：R1123 incr_eval 3routes(codex+deepseek RESOLVED·claude-code FAILED)·R1118 incr_eval 2routes(both RESOLVED)·R1124/R1119-R1122 scan_backlog=0·4路predict持续(claude-code430·codex303·hermes77-78·deepseek65-66,均活跃未卡)。需要时再读。

> 📦 R1089-R1117 流水(2026-11-01 01:25-03:12, 11轮内存自检+incr_eval+scan_backlog)已归档 → daily-memories-harness/2026-11-01.md。结论：scan_backlog每轮清0·incr_eval共resolved 10+题(hermes6·deepseek2·codex2)·eval渐进:hermes32→38/44→50·deepseek46→49/58→61·codex172→174/219→221·4路orch alive·硬约束0结果JSON tracked✅. 需要时再读。

> [00:50] R1103 incr_eval 2routes(both resolved)+内存自检142th PASS. (详细已归档→本日日志)
> [00:38] R1102/R1100/R1097 流水(incr_eval+内存自检,3轮)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1096 流水(2026-10-31 23:23)已归档 → daily-memories-harness/2026-10-31.md。需要时再读。

> 📦 R1087-R1091 流水(2026-10-31 21:23-22:22, 5轮incr_eval+内存自检)已归档 → daily-memories-harness/2026-10-31.md。结论：scan_backlog每轮清0·claude-code250→256/326→332·codex166→168·deepseek37→42·hermes29→31·cline326/442·opencode395/488·pi298/410·4路orch alive·硬约束0结果JSON tracked✅. 需要时再读。

> 📦 R1085+R1086 流水(2026-10-31 21:00-21:13,内存自检124th/125th+incr_eval 3 BACKLOG)已归档 → daily-memories-harness/2026-10-31.md。结论：deepseek astropy-7671 RESOLVED✅·claude-code django-13512 FAILED·codex django-12262 RESOLVED✅。需要时再读。
> 📦 R1083+R1084 流水(2026-10-31 20:32-20:49,内存自检122nd/123rd+incr_eval 8 BACKLOG处理)已归档 → daily-memories-harness/2026-10-31.md。结论：claude-code django-13417/13410 RESOLVED✅·codex django-12193/12262 RESOLVED✅·deepseek astropy-7166/14995 RESOLVED✅·hermes sympy-19954/20154 RESOLVED✅·deepseek astropy-7336/7606 FAILED·hermes sympy-20428 FAILED·claude-code django-13512 FAILED。需要时再读。
> 📦 R1082 流水(2026-10-31 20:13,内存自检121st+incr_eval 2 BACKLOG全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：claude-code django-13401/codex django-12155 各RESOLVED✅·scan_backlog残留1(django-13410 transient,R1083已清)·eval claude-code247/codex164 post-regen。需要时再读。
> 📦 R1081 流水(2026-10-31 19:50,内存自检120th+scan_backlog=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code411/codex288/hermes56/deepseek47)。需要时再读。
> 📦 R1079 流水(2026-10-31 19:34,内存自检118th+incr_eval 3 BACKLOG全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG 3项(hermes sympy-19637/deepseek astropy-14539/claude-code django-13363)incr_eval全RESOLVED✅·eval hermes27/deepseek34/claude-code246 post-regen·HTML刷新·predict 4路alive(claude-code411/codex287/hermes56/deepseek47)。需要时再读。
> 📦 R1076-R1078 流水(2026-10-31 18:58-19:20,内存自检115th-117th+incr_eval多条BACKLOG)已归档 → daily-memories-harness/2026-10-31.md。结论：R1076 codex/hermes/deepseek 3项全RESOLVED✅(codex161/hermes26/deepseek32)·R1077 codex django-12050 RESOLVED✅+deepseek astropy-14508 RESOLVED✅·R1078 BACKLOG=0监控轮·predict 4路alive(claude-code410/codex286/hermes55/deepseek46)。需要时再读。
> 📦 R1075 流水已归档 → daily-memories-harness/2026-10-31.md（原文不改）。需要时再读。
> 📦 R1071-R1074 流水(2026-10-31 18:02-18:36,内存自检110th-113th+incr_eval多条BACKLOG)已归档 → daily-memories-harness/2026-10-31.md。结论：claude-code django-13315 RESOLVED✅·codex django-11999 RESOLVED✅·deepseek astropy-14309 re-eval RESOLVED✅·hermes sympy-18763 unresolved·deepseek astropy-14365 unresolved·scan_backlog逐轮清零。需要时再读。
> 📦 R1070 流水(2026-10-31 17:52,内存自检109th+监控轮BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·stale pi eval PID3747564(240MB,16.4d hung)未达杀阈·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code405/codex282/hermes50/deepseek43)。需要时再读。
> 📦 R1069 流水(2026-10-31 17:42,内存自检108th+监控轮BACKLOG=0)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·BACKLOG=0无incr_eval·eval全7路unchanged·predict 4路alive(claude-code405/codex282/hermes50/deepseek43)。需要时再读。
> 📦 R1050-R1068 流水(2026-10-31 13:52~17:32, 内存自检89th~107th, ~19轮incr_eval+监控)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·多条BACKLOG incr_eval(claude-code/codex/hermes/deepseek混RESOLVED+UNRESOLVED)·eval稳步增长·predict 4路alive·硬约束tracked=0✅。需要时再读。
> 📦 R1043-R1049 流水(2026-10-31 12:32~13:44,内存自检82th~88th)已归档 → daily-memories-harness/2026-10-31.md。结论：内存全PASS·多轮incr_eval(4新patch全RESOLVED·2新patch全empty等)·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1002-R1042 流水(2026-10-31 04:00~12:09,内存自检40th~81th+incr_eval chain step1-7全DONE+恒0分调试收尾+predict监控,~40轮)已归档 → daily-memories-harness/2026-10-31.md。结论：incr_eval_all7 chain 7路串行270新patch全eval DONE(cline325/442·opencode394/488·pi298/410·claude-code227/299·codex150/191·hermes12/18·deepseek21/26)·scikit-learn-14710 timeout→infra单列·恒0分调试verify5b hermes4/5+deepseek3/5·predict 3路DONE+4路alive·硬约束tracked=0✅。需要时再读。
> 📦 R927-R1001 流水(2026-10-30 13:13~10-31 03:49,内存自检1st~39th+incr_eval chain+恒0分复核+硬约束修复,~75轮)已归档 → daily-memories-harness/2026-10-30.md + 2026-10-31.md。结论：内存自检全PASS无失控·incr_eval chain 5路全DONE(opencode383/467·cline302/413·pi270/363·claude-code194/257·codex129/163)·首版full500 HTML报告生成(partial banner+Wilson CI+McNemar)·4个verify5结果JSON硬约束违规修复(git rm --cached+.gitignore)·hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R821-R926 巡检流水(2026-10-30 00:04~13:50,约100轮常态巡检)已合并归档 → daily-memories-harness/2026-10-30.md。结论：5路predict持续健康推进,进度1183→1743,全路ALIVE·timeout=0·429=0·tracked=0✓,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R609-R820 巡检流水(2026-10-29 00:58~18:28,~90轮常态巡检)已合并归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline70→232·opencode80→227·pi56→195·claude-code59→188·codex47→121),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> [00:51] R626 及更早巡检流水已归档 → daily-memories-harness/2026-10-28.md（5路健康·opencode89·总349·增量+0·大实例耗时正常·资源稳定）。需要时再读。

> 📦 R619-R620 流水(2026-10-29 00:09~00:15, predict巡检)已归档 → daily-memories-harness/2026-10-29.md。需要时再读。

> 📦 R590-R605 巡检流水(2026-10-28 21:08~22:47,16轮常态巡检)已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续健康运行,稳步推进(cline56→66·opencode58→77·codex40→46·pi48→53·claude-code45→57),全路timeout=0,gw_proxy=200,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R581-R589 巡检流水(2026-10-28 19:44~21:01,9轮常态巡检)已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续健康运行,稳步推进(cline50→56·opencode46→55·codex31→40·pi40→47·claude-code34→42),全路timeout=0,gw_proxy=200,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R568-R578 巡检流水(2026-10-28 17:47~19:02,11轮常态巡检)已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续健康运行,全路增量稳定,无error/timeout,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R559-R564 流水（2026-10-28 16:30-17:07, SWE-bench full500 predict 巡检, 6 条）已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续ALIVE·稳步推进(cline29→31·codex18→19·claude-code22→24·opencode30→33·pi22→28);无429·无error·gw_proxy=200·infra单列·闸门FAIL路未进全量。需要时再读。

> 📦 R553-R558 流水（2026-10-28 15:43-16:23, SWE-bench full500 predict 巡检, 6 条）已归档 → daily-memories-harness/2026-10-28.md。结论：5路predict持续ALIVE·稳步推进(cline23→31·codex16→19·claude-code20→23·opencode26→33·pi21→26);无429·无error·gw_proxy=200·infra单列·闸门FAIL路未进全量。需要时再读。

> 📦 R549-R552 流水（2026-10-28 12:20-15:1x, GATE v2 predict+eval+全量500启动+TB整改, 4条）已归档 → daily-memories-harness/2026-10-28.md。结论：GATE v2 5路PASS(cline/codex/claude-code/opencode/pi)·2路FAIL(hermes/deepseek)·全量500 predict 5路后台启动·TB整改5问已交付。需要时再读。

> 📦 R536-R548 流水(2026-10-27 19:0x ~ 2026-10-28 10:15, R536-R548共13轮:pilot20交付+TB报告+心跳防判死+GATE v2启动+config修复)已归档 → daily-memories-harness/2026-10-28.md。结论：pilot20两报告已交付(cline 13/20=65%·hermes 11/20=55%);GATE v2 predict全7路完成(5路PASS:cline/codex/claude-code/opencode/pi·2路FAIL:hermes/deepseek)。需要时再读。

> 📦 R527-R530 流水(2026-10-28 09:3x~14:2x, TB报告交付+20条试点编排器smoke+启动)已归档 → daily-memories-harness/2026-10-28.md。结论：R527 TB报告交付(commit92ce36995)·R528编排器就绪+gold eval验通·R529 smoke修复(short-hash→full40sha+setsid)·R530端到端pipeline验通+20条试点启动。需要时再读。
> 📦 R518-R526 流水(2026-10-27 22:4x ~ 2026-10-28 08:0x, 9轮:就绪核查R518+防判死心跳R519-R526)已归档 → daily-memories-harness/2026-10-28.md。结论：就绪状态活性复检全通过(swebench500/500·gateway200·/data6.0T·harness loop在跑),运维待批20条Verified试点决策有效。需要时再读。

> 📦 R507-R517+R485-R506 长流水原文已归档 → daily-memories-harness/2026-10-26.md（结论：R517归档bookkeeping+报告复核;R509近期工作报告交付;R508/R507复跑进度刷新+3件deliverable;R502-R506复跑进度;R497-R500审计核验+复跑监控;R492-R496全7路FIN87/87+McNemar+适配器修复smoke;R485-R488双线并列监控TB+SWE-bench下载）。需要时再读。
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
