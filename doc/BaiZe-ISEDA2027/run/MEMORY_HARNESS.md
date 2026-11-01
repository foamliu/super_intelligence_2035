# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1168 内存自检207th PASS→scan_backlog 1backlog→incr_eval 1item(1RESOLVED)·eval:cline326/442·opencode399/493·pi301/414·codex176/224·claude-code263/344·hermes52/70·deepseek58/74. infra单列✅.
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1167 incr_eval链+内存自检+体积归档✅·R1168 内存自检207th+incr_eval 1item(1resolved)+报告regen✅
当前动作:     R1168 内存自检207th PASS(运维令10-30 11:1x):avail~1.4TiB(505Gi used/2.0Ti total)·无本线>50GB(总harness predict RSS~2.7GB·最大opencode605MB·hermes30MB·deepseek30MB)·无partitions()/list()失控. scan_backlog=1→incr_eval:①hermes astropy-8707→RESOLVED(r51→52 n69→70)·re-scan=0✅·HTML报告regen(15384B,13:26)✅. 硬约束:predictions/logs tracked=0✅(reports/仅backlog_scan artifact,eval_*.json全gitignored). /data6.0Tfree.
下一步:       ①5路predict runner仍跑(cline·opencode DONE·pi441/codex303/claude-code430/hermes104/deepseek78持续) ②每轮scan_backlog→有新real-patch则incr_eval ③predict全完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ④infra单列(铁律③) ⑤永久硬约束:禁止commit结果JSON ⑥TASK=34.9KB·MEMORY≤32KB✅
阻塞:         无.
ERROR_COUNT:  0
  📦 体积：TASK=34.9KB(35757B,>32KB,2活跃块不可归档,<40KB红线OK) / MEMORY≈31.6KB(≤32KB✅,本轮归档R1160-R1161)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [13:27] R1168 内存自检207th PASS+incr_eval 1item(1RESOLVED)✅:avail~1.4TiB(505Gi used/2015Gi total)·无本线>50GB(总harness predict RSS~2.7GB·最大opencode605MB·hermes30MB·deepseek30MB)·无partitions()/list(). scan_backlog=1→incr_eval:①hermes astropy-8707→RESOLVED(r51→52 n69→70)·re-scan=0✅·HTML报告regen(15384B,13:26)✅. predict:cline500(DONE)·opencode500(DONE)·pi441·codex303·claude-code430·hermes104·deepseek78(5路runner仍跑). eval:cline326/442·opencode399/493·pi301/414·codex176/224·claude-code263/344·hermes52/70·deepseek58/74·infra单列✅·/data6.0Tfree·硬约束predictions/logs tracked=0✅(reports/仅backlog_scan artifact)·TASK34.9KB·MEMORY≈31.6KB→归档R1160-R1161≤32KB·未完成指令:有(10-30内存自检常驻+10-28full500 5路predict仍跑)⇒WAITING=0.

> [13:18] R1167 内存自检206th PASS+incr_eval 3items(3RESOLVED)✅:avail~1.4TiB(517Gi used)·总harness predict RSS~2.7GB·无>50GB·无partitions()/list(). scan_backlog=3→incr_eval:①opencode sympy-19040→RESOLVED(r398→399 n492→493)②hermes astropy-7671→RESOLVED(r50→51 n68→69)③deepseek django-11880→RESOLVED(r57→58 n73→74)·re-scan=0✅·HTML报告regen(15374B,13:18)✅. predict:cline500(DONE)·opencode500(DONE)·pi441·codex303·claude-code430·hermes103·deepseek78(5路runner仍跑). eval:cline326/442·opencode399/493·pi301/414·codex176/224·claude-code263/344·hermes51/69·deepseek58/74·infra单列✅·/data6.0Tfree·硬约束predictions/logs tracked=0✅(501tracked=500instances+enriched)·TASK34.9KB·MEMORY≈31.2KB·未完成指令:有(10-30内存自检常驻+10-28full500 5路predict仍跑)⇒WAITING=0.

> [13:01] R1166 内存自检205th PASS+incr_eval 4items(3RESOLVED)✅:avail~1.4TiB(504Gi used)·总harness RSS~7.1GB·无>50GB·无partitions()/list(). scan_backlog=4→incr_eval:①opencode sympy-13878→RESOLVED(r397→398)②pi sympy-13852→FAILED(f112→113)③pi sympy-16766→RESOLVED(r299→300)④pi sympy-23413(新产)→RESOLVED(r300→301)·re-scan=0✅·HTML报告regen(15374B,含398/301)✅. predict:cline500(DONE)·opencode500(DONE)·pi441·codex303·claude-code430·hermes103·deepseek77(5路runner仍跑). eval:cline326/442·opencode398/492·pi301/414·codex176/224·claude-code263/344·hermes50/67·deepseek57/73·infra单列✅·/data6.0Tfree·硬约束predictions/logs/eval-summary tracked=0✅(525tracked=500instances输入+25合法)·TASK34.9KB·MEMORY≈31.7KB→归档R1152-R1153≤32KB·未完成指令:有(10-30内存自检常驻+10-28full500 5路predict仍跑)⇒WAITING=0.

> [12:33] R1165 内存自检204th PASS+🔧backlog_scan修复+incr_eval 5items DONE✅:avail~1.4TiB(504Gi used)·总harness RSS 7.14GB·无>50GB·无partitions()/list(). 🔧关键修复:预测文件是JSON list格式(非dict)→之前scan用p.get('model_patch')静默跳过所有项→修正为isinstance(p,list)取p[0]→发现5条被遗漏的backlog. incr_eval 3route:①opencode sphinx-doc__sphinx-10435→FAILED(report已存在,仅regen拾取 r397 f93→94 n490→491)②pi sympy__sympy-12419→RESOLVED(r298→299 n410→411)③hermes astropy-7166/7336/7606→1RESOLVED+2FAILED(r49→50 f16→18 n65→68)·regen_eval_summaries✅·HTML报告regen(15374B)✅. predict:cline500(DONE)·opencode500·pi441+·codex303+·claude-code430+·hermes102+·deepseek77+(6路runner仍跑). eval:cline326/442·opencode397/491·pi299/411·codex176/224·claude-code263/344·hermes50/68·deepseek57/73·infra单列✅·/data6.0Tfree·硬约束0结果JSON tracked✅·TASK34.9KB·MEMORY≈31.4KB·未完成指令:有(10-30内存自检常驻+10-28full500 6路predict仍跑)⇒WAITING=0.

> [12:10] R1163 内存自检202nd PASS+scan_backlog=0+硬约束复核✅:avail~1.4TiB(502Gi used)·无本线>50GB(6路runner·最大cline-hub daemon3.5GB非predict·opencode1.1GB·deepseek SDK261MB·claude-code229MB·hermes child186MB·其余<15MB)·无partitions()/list()·docker=0(eval时短暂起容器). scan_backlog=0(全real-patch已evald)·7路real=evald=0backlog✅. 硬约束tracked=502(500instances+enriched+verify5/verified_full manifests+1backlog_scan artifact)·predictions/logs report.json=0 tracked·0结果JSON✅. predict:cline500(DONE)·opencode499·pi441·codex303·claude-code430·hermes97·deepseek77. eval:cline326/442·codex176/224·opencode396/489·pi298/410·claude-code263/343·hermes48/64·deepseek57/73·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY≈29.7KB·R1162心跳已被pretrain #1069 commit(12:04)的git add -A扫入(共享副本已知副作用,心跳已落盘无判死风险)·未完成指令:有(10-30内存自检常驻+10-28full500 6路predict仍跑)⇒WAITING=0.

> [12:02] R1162 内存自检201st PASS+incr_eval 1backlog RESOLVED:avail~1.4TiB(501Gi used)·无本线>50GB(6路runner·最大cline-hub daemon3.0GB非predict·opencode1.1GB·deepseek SDK269MB·hermes child186MB·其余<33MB)·无partitions()/list()·docker=0(eval时短暂起容器). scan_backlog:1项→opencode pylint-dev__pylint-7080(patchlen=3649)→incr_eval(docker sweb.eval容器)→RESOLVED(n488→489 r395→396)·7路real=evald=0backlog✅. 硬约束tracked=501全合法instances+enriched+manifests·0结果JSON✅. predict:cline500(DONE)·opencode499·pi441·codex303·claude-code430·hermes97·deepseek77. eval:cline326/442·codex176/224·opencode396/489·pi298/410·claude-code263/343·hermes48/64·deepseek57/73·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY≈29.4KB·未完成指令:有(10-30内存自检常驻+10-28full500 6路predict仍跑)⇒WAITING=0.

> 📦 R1160-R1161 流水(2026-11-01 11:46~11:54,内存自检199th-200th+incr_eval 2backlog全RESOLVED+scan_backlog=0)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1160 incr_eval deepseek django-11815+hermes astropy-14539均RESOLVED·R1161 scan_backlog=0·predict 5路alive·硬约束tracked=0✅。需要时再读。

> [11:32] R1159 内存自检198th PASS+incr_eval 1backlog(hermes astropy-14508 RESOLVED):avail~1.4TiB(501Gi used)·无本线>50GB(6路runner·最大opencode619MB·deepseek SDK254MB·hermes child180MB·gw_proxy223MB)·无partitions()/list()·docker=0(eval时短暂起容器). scan_backlog:仅1 hermes astropy-14508(real patch 1265B)→incr_eval R1159→RESOLVED(n62→63 r46→47 f16)·6路real=evald=0backlog✅. 硬约束tracked=525全合法instances+enriched+manifests·0结果JSON✅. predict:cline500(DONE)·opencode499·pi441·codex303·claude-code430·hermes96·deepseek76(log217). eval:cline326/442·codex176/224·opencode395/488·pi298/410·claude-code263/343·hermes47/63·deepseek56/72·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY26.4KB·未完成指令:有(10-30内存自检常驻+10-28full500 6路predict仍跑)⇒WAITING=0.

> [11:21] R1158 内存自检197th PASS+incr_eval 1backlog:avail~1.4TiB(499Gi used)·无本线>50GB(6路runner·最大opencode611MB·claude-code bun211MB·pi32MB)·无partitions()/list()·docker=0. scan_backlog:仅1 deepseek django-11790(real patch 712B)→incr_eval R1158→FAILED(n71→72 r56 f15→16)·6路real=evald=0backlog✅. 硬约束tracked=525全合法instances+enriched+manifests·0结果JSON✅. predict:cline500(DONE)·opencode499·pi441·codex303·claude-code430·hermes95·deepseek76(log217). eval:cline326/442·codex176/224·opencode395/488·pi298/410·claude-code263/343·hermes46/62·deepseek56/72·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY25.6KB·未完成指令:有(10-30内存自检常驻+10-28full500 6路predict仍跑)⇒WAITING=0.

> [11:13] R1157 内存自检196th PASS+incr_eval 1backlog:avail~1.4TiB(500Gi used)·无本线>50GB(6路runner<32MB)·无partitions()/list()·docker=0. scan_backlog:仅1 claude-code pytest-5840(real patch 1595B)→incr_eval R1157→FAILED(ambiguous failure,n342→343 r263 f80)·6路real=evald=0backlog✅. 硬约束tracked=520instances+2enriched·0结果JSON✅. predict:cline500(DONE)·opencode499·pi441·codex303·claude-code430·hermes95·deepseek75(log216). eval:cline326/442·codex176/224·opencode395/488·pi298/410·claude-code263/343·hermes46/62·deepseek56/71·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY25.3KB·未完成指令:有(10-30内存自检常驻+10-28full500 6路predict仍跑)⇒WAITING=0.
> [11:03] R1156 内存自检195th PASS+incr_eval 1backlog+opencode/pi重启:avail~1.4TiB(502Gi used)·无本线>50GB(6路runner<33MB·deepseek SDK267MB·claude-code bun223MB·hermes child184MB·cline-hub daemon8.5GB非predict)·无partitions()/list()·docker=0. 1452xxx树(16.7GB)=S1 pretrain训练(非本线,未碰). scan_backlog:仅1 deepseek django-11749(real patch)→incr_eval R1156→FAILED(n71 r56 f15)·6路real=evald=0backlog✅. opencode(499/500)+pi(441/500)died10-28→重启✅(setsid,checkpoint resume,opencode→pylint-6528·pi→sphinx-8621). 硬约束tracked=500全instances·0结果JSON✅. predict:cline500(DONE)·opencode499·pi441·codex303·claude-code430·hermes95·deepseek75(log216). eval:cline326/442·codex176/224·opencode395/488·pi298/410·claude-code263/342·hermes46/62·deepseek56/71·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY24.3KB·未完成指令:有(10-30内存自检常驻+10-28full500 6路predict仍跑)⇒WAITING=0.
> [10:48] R1155 内存自检194th PASS+incr_eval 2backlog全RESOLVED:avail~1.4TiB(498Gi used)·无本线>50GB(5路runner<33MB·hermes child54MB·deepseek SDK267MB·claude-code bun223MB+pytest29MB·cline-hub daemon4.2GB非predict·stale opencode非runaway)·无partitions()/list()·docker=0. incr_eval:①codex/django-15382→RESOLVED(eval 10:48,175→176)②deepseek/django-11740→RESOLVED(eval 10:48,55→56). scan_backlog=0✅. 硬约束eval-result tracked=0✅·500tracked全合法instances✅. predict:5DONE+2跑(hermes[94/500,~3inst/h,ETA~5d]·deepseek[215/500,~3.5inst/h,ETA~4d]). eval:cline326/442·codex176/224·opencode395/488·pi298/410·claude-code263/342·hermes46/62·deepseek56/70·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY≈23.4KB·未完成指令:有(10-30内存自检常驻+10-28full500 hermes/deepseek仍跑)⇒WAITING=0.
> [10:34] R1154 内存自检193rd PASS+incr_eval 1backlog(hermes astropy-14365 FAILED):avail~1.4TiB(497Gi used)·无本线>50GB(4路runner<33MB·hermes child183MB·deepseek SDK267MB·claude-code bun200MB·cline-hub daemon4.1GB非predict)·无partitions()/list()·docker=0(eval时短暂起容器). incr_eval:hermes/astropy-14365→FAILED(eval 10:30,hermes 46/15→46/16). scan_backlog=0✅. 硬约束eval-summary tracked=0✅·500tracked全合法instances✅. predict:5DONE+2跑(hermes[87/500]on astropy-14369,~3inst/h,ETA~5d·deepseek[210/500]on django-11740,~3.5inst/h,ETA~4d)+codex runner alive(recovery django-15382). eval:cline326/442·opencode395/488·pi298/410·claude-code263/342·codex175/223·hermes46/62·deepseek55/69·infra单列✅·/data6.0Tfree·TASK34.9KB·MEMORY≈17.8KB·未完成指令:有(10-30内存自检常驻+10-28full500 hermes/deepseek仍跑)⇒WAITING=0.
> 📦 R1152-R1153 流水(2026-11-01 09:56~10:22,2轮内存自检191st-192nd+incr_eval R1153 3backlog全RESOLVED+R1152 5/7 predict DONE里程碑)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1153 incr_eval 3resolved(claude-code pylint-6528+hermes astropy-14182/14309)·R1152 5/7 predict DONE里程碑(claude-code·codex刚完成500/500)·硬约束0结果JSON tracked✅. 需要时再读。
> 📦 R1144-R1151 流水(2026-11-01 08:32~09:33,8轮内存自检183th-190th+incr_eval R1147 deepseek django-11603 RESOLVED+scan_backlog逐轮清零)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS无失控·R1147 incr_eval deepseek django-11603 RESOLVED✅(deepseek 54→55)·R1144-R1146/R1148-R1151 scan_backlog=0无incr_eval·4路predict持续推进(claude-code→430/codex→303/hermes→90/deepseek→73)·硬约束0结果JSON tracked✅. 需要时再读。

> 📦 R1143 流水(2026-11-01 08:25,内存自检182th+scan_backlog=0+硬约束tracked=0✅)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1142 流水(2026-11-01 08:12,内存自检181st+incr_eval deepseek django-11551 RESOLVED+scan_backlog=0+硬约束tracked=0✅)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1139-R1141 流水(2026-11-01 07:38~08:03,3轮内存自检178th-180th+incr_eval R1139(2题both RESOLVED)+R1140(hermes astropy-13398 FAILED)+R1141(hermes astropy-13453 RESOLVED))已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1132-R1136 流水(2026-11-01 06:08~07:0x,5轮内存自检171st-175th+incr_eval R1132(3题1resolved)+R1135(1题failed)+R1133/R1134/R1136 scan_backlog=0)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

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
> 📦 R1049 流水(2026-10-31 13:44,内存自检88th+incr_eval 4新patch全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·4新patch全RESOLVED(claude-code+1·hermes+1·deepseek+2)·eval更新·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1048 流水(2026-10-31 13:29,内存自检87th+无incr_eval 2新patch全empty)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·2新patch全empty→无incr_eval·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1046 流水(2026-10-31 13:14,内存自检85th+无incr_eval无新patch)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·无新patch→无incr_eval·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1045 流水(2026-10-31 13:07,内存自检84th+incr_eval 2新patch全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·2新patch全RESOLVED(claude-code+1·hermes+1)·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1044 流水(2026-10-31 12:51,内存自检83th+incr_eval 4新patch全RESOLVED)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·4新patch全RESOLVED(claude-code+1·codex+2·hermes+1)·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
> 📦 R1043 流水(2026-10-31 12:32,内存自检82th+无incr_eval全empty patch)已归档 → daily-memories-harness/2026-10-31.md。结论：内存PASS·3新prediction全empty patch→无incr_eval·eval全量验证current·predict 4路alive·tracked=0✅。需要时再读。
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
