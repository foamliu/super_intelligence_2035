# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R1236 内存自检275th PASS+scan_backlog=1→incr_eval pi scikit-learn-10844 RESOLVED✅·TOTAL=2176/1659(+1/+1)·eval:cline442(326)·opencode497(401)·pi456(327)·claude-code355(270)·codex232(181)·hermes97(75)·deepseek97(79). backlog=0✅. 5路predict alive(pi+claude-code+codex+hermes+deepseek)⚠️
已完成:       H-B✅·Gate7/7·TB报告✅·pilot20✅·R984-R988恒0调试✅·R989 incr_eval全链✅·R997硬约束修复✅·R998-R1235 incr_eval链+内存自检+体积归档✅·R1236 内存自检275th+incr_eval 1item(pi RESOLVED)✅
当前动作:     R1236 DONE:内存自检275th PASS(运维令10-30 11:1x):avail~1.3Ti(547Gi used/2.0Ti total)·无本线>50GB(最高opencode 1133MB;deepseek SDK 260MB;gw_proxy 228MB;claude-code bun 229MB;hermes 183MB)·无partitions()/list()失控✅. scan_backlog=1→pi scikit-learn-10844(patchlen=1793)incr_eval→RESOLVED✅. rescan=0✅. eval TOTAL=2176/1659(+1/+1):cline442(326)·opencode497(401)·pi456(327)·claude-code355(270)·codex232(181)·hermes97(75)·deepseek97(79). predict:cline500(DONE)·opencode500(DONE)·pi470·claude-code430·codex303·hermes140·deepseek102(5路alive). 硬约束:eval result JSON全gitignored✅·HTML报告已regen(15380B,项目级reports/).
下一步:       ①5路predict alive(pi+claude-code+codex+hermes+deepseek)等待新预测落盘 ②每轮scan_backlog→有新real-patch则incr_eval ③hermes/deepseek predict远未达500,继续等待 ④predict全完成后final eval+full500最终报告(7路总表+Wilson CI+McNemar 7×7) ⑤infra单列(铁律③) ⑥永久硬约束:禁止commit结果JSON ⑦TASK=34.9KB·MEMORY≤32KB
阻塞:         无(5路runner alive产出中,hermes/deepseek predict极慢但仍在产出,不kill).
ERROR_COUNT:  0
  📦 体积：TASK=35757B(34.9KB,>32KB,2活跃块不可归档,<40KB红线OK) / MEMORY≈31.8KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
> [02:14] R1236 内存自检275th PASS+incr_eval 1item(pi RESOLVED)✅:avail~1.3Ti(547Gi used/2.0Ti total)·无本线>50GB(最高opencode 1133MB;deepseek SDK 260MB;gw_proxy 228MB;claude-code bun 229MB;hermes 183MB)·无partitions()/list()失控✅. scan_backlog=1→pi scikit-learn-10844(patchlen=1793)incr_eval→report.json resolved=true✅. rescan=0✅. eval TOTAL=2176/1659(+1/+1):cline442(326)·opencode497(401)·pi456(327)·claude-code355(270)·codex232(181)·hermes97(75)·deepseek97(79). predict:cline500(DONE)·opencode500(DONE)·pi470·claude-code430·codex303·hermes140·deepseek102(5路alive;runner etime:pi~15h·claude-code~25h·codex~25h·hermes~48h·deepseek~48h). 硬约束:reports/eval_*.json+predictions/+logs/全gitignore✅·/data6.0Tfree·HTML报告15380B(项目级reports/)·TASK34.9KB·MEMORY≈31.8KB·未完成指令:有(10-30内存自检常驻+10-28full500 5路predict仍跑)⇒WAITING=0.
> 📦 R1235 流水(2026-11-02 02:07,内存自检274th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·backlog=0无incr_eval·eval TOTAL=2175/1658 unchanged·tracked=522✅。需要时再读。
> 📦 R1233 流水(2026-11-02 01:41,内存自检272nd+incr_eval 2items ALL RESOLVED)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·scan_backlog=1→codex xarray-6721 RESOLVED;rescan=1→pi pytest-7571 RESOLVED;final scan=0✅·eval TOTAL=2172/1655(+2/+2)。需要时再读。
> 📦 R1232 流水(2026-11-02 01:28,内存自检271st+incr_eval 6items 4RESOLVED+2FAILED)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·scan_backlog=6→incr_eval 6items(hermes/deepseek/pi/claude-code各路;4 RESOLVED+2 FAILED)·eval TOTAL=2170/1653(+6/+4)。需要时再读。
> 📦 R1231 流水(2026-11-02 01:14,内存自检270th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·backlog=0无incr_eval·eval TOTAL=2164/1649 unchanged·tracked=522✅。需要时再读。
> 📦 R1230 流水(2026-11-02 01:06,内存自检269th+incr_eval 4items ALL RESOLVED)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·scan_backlog=1→pi pytest-7236 RESOLVED;再scan=2→claude-code django-11964+pi pytest-7324 ALL RESOLVED;再scan=1→pi pytest-7432 RESOLVED;final scan=0✅·eval TOTAL=2164/1649(+4/+4)·tracked=0✅。需要时再读。
> 📦 R1229 流水(2026-11-02 00:45,内存自检268th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·backlog=0无incr_eval·eval TOTAL=2160/1645 unchanged·归档R1165-R1169指针·tracked=0✅。需要时再读。
> 📦 R1228 流水(2026-11-02 00:36,内存自检267th+incr_eval 2items 1RESOLVED+1FAILED)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·hermes django-11551 RESOLVED·pi pytest-7205 FAILED·eval TOTAL=2160/1645·tracked=0✅。需要时再读。
> 📦 R1227 流水(2026-11-02 00:21,内存自检266th+incr_eval 2items ALL RESOLVED)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·deepseek django-13028 RESOLVED·pi pytest-6202 RESOLVED·eval TOTAL=2158/1644·tracked=0✅。需要时再读。
> 📦 R1226 流水(2026-11-02 00:16,内存自检265th+scan_backlog=0+regen无变化)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·backlog=0·eval TOTAL=2156/1642 unchanged·tracked=0✅。需要时再读。
> 📦 R1225 流水(2026-11-02 00:08,内存自检264th+incr_eval 2items 1RESOLVED+1FAILED)已归档 → daily-memories-harness/2026-11-02.md。结论：内存PASS·claude-code django-11820 FAILED·hermes django-11532 RESOLVED·eval TOTAL=2156/1642·tracked=0✅。需要时再读。
> 📦 R1224 流水(2026-11-01 23:58,内存自检263rd+incr_eval 2items 1RESOLVED+1FAILED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·codex xarray-4687 FAILED·deepseek django-13023 RESOLVED·eval TOTAL=2154/1641·tracked=0✅。需要时再读。
> 📦 R1223 流水(2026-11-01 23:48,内存自检262nd+incr_eval 4items 2RESOLVED+2FAILED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·deepseek django-13012 RESOLVED·hermes 11477 FAILED·pi pytest-5840 FAILED·hermes 11490 RESOLVED·eval TOTAL=2152/1640·tracked=0✅。需要时再读。
> 📦 R1222 流水(2026-11-01 23:35,内存自检261st+scan_backlog=0)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·backlog=0·eval TOTAL=1638/2148 unchanged·tracked=0✅。需要时再读。
> 📦 R1220 流水(2026-11-01 23:18,内存自检259th+incr_eval 4items all RESOLVED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·pi5787+pi5809+claude-code11490+hermes11451 all RESOLVED·eval TOTAL=1638/2148·tracked=0✅。需要时再读。
> 📦 R1219 流水(2026-11-01 23:05,内存自检258th+incr_eval 3items all RESOLVED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·pi5262+pi5631+hermes11433 all RESOLVED·eval TOTAL=1634/2144·tracked=0✅。需要时再读。
> 📦 R1218 流水(2026-11-01 22:50,内存自检257th+incr_eval 1item FAILED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·pi pytest-10356 FAILED·eval TOTAL=1631/2141·tracked=0✅。需要时再读。
> 📦 R1217 流水(2026-11-01 22:41,内存自检256th+incr_eval 1item RESOLVED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·pi pytest-10081 RESOLVED·eval TOTAL=1631/2139·tracked=0✅。需要时再读。

> 📦 R1214 流水(2026-11-01 22:01,内存自检253rd+incr_eval 1item pi pylint-7080 FAILED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·pi pylint-7080 already-eval→FAILED·eval TOTAL=1626/2133·progress发现5路done=500·tracked=0✅。需要时再读。
> 📦 R1213 流水(2026-11-01 21:47,内存自检252nd+incr_eval 3items hermes+pi)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·hermes django-11299 RESOLVED·pi pylint-6528 FAILED·pi pylint-6903 RESOLVED·eval TOTAL=1626/2132·tracked=0✅。需要时再读。
> 📦 R1212 流水(2026-11-01 21:35,内存自检251st+incr_eval 2items/2routes claude-code astropy-14182+deepseek django-12741 both RESOLVED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·claude-code astropy-14182 RESOLVED·deepseek django-12741 RESOLVED·eval TOTAL=1624/2129·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R1211 流水(2026-11-01 21:24,内存自检250th+incr_eval 3items/2routes deepseek django-12713 RESOLVED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·deepseek django-12713 RESOLVED·pi pylint-4661/6386 FAILED·eval TOTAL=1622/2127·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R1209-R1210 流水(2026-11-01 21:01~21:13,内存自检248-249th)已归档 → daily-memories-harness/2026-11-01.md。结论：R1210 deepseek django-12708 RESOLVED·R1209 pi pylint-4604 FAILED·eval TOTAL=1620~1621·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R1208 流水(2026-11-01 20:51,内存自检247th+incr_eval 1route pi pylint-4551 FAILED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·pi pylint-4551 FAILED·eval TOTAL=1620/2122·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R1205 流水(2026-11-01 20:17,内存自检244th+incr_eval 2routes 1RESOLVED 1FAILED)已归档 → daily-memories-harness/2026-11-01.md。结论：内存PASS·claude-code astropy-13236 FAILED·deepseek django-12419 RESOLVED✅·eval deepseek69/86·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R1188-R1204 流水(2026-11-01 17:31~20:03,内存自检227th-243th,~17轮incr_eval+quiet)已合并归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·多条incr_eval混RESOLVED+FAILED·eval稳步增长·predict 5路alive·tracked=0✅。需要时再读。
> 📦 R1187 流水(2026-11-01 17:23,内存自检226th+incr_eval 2items(+1resolved))已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1186 流水(2026-11-01 17:09,内存自检225th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1184 流水(2026-11-01 16:50,内存自检223rd+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1183 流水(2026-11-01 16:41,内存自检222nd+incr_eval 3items(+3resolved))已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1182 流水(2026-11-01 16:28,内存自检221st+incr_eval 5items(+5resolved))已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1181 流水(2026-11-01 16:09,内存自检220th+incr_eval 3items(+3resolved))已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1180 流水(2026-11-01 15:55,内存自检219th+incr_eval 1item RESOLVED(+1))已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1179 流水(2026-11-01 15:42,内存自检218th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1178 流水(2026-11-01 15:36,内存自检217th+incr_eval 1item RESOLVED(+1))已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1172-R1176 流水(2026-11-01 14:09~15:14,内存自检211th-215th+incr_eval 多items)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。
> 📦 R1170-R1171 流水(2026-11-01 13:45~13:59,内存自检209th-210th+incr_eval 多items)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。



> 📦 R1169 流水(2026-11-01 13:36,内存自检208th+scan_backlog=0 quiet)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1167 流水(2026-11-01 13:18,内存自检206th+incr_eval 3items ALL RESOLVED)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1166 流水(2026-11-01 13:01,内存自检205th+incr_eval 4items 3RESOLVED)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1165 流水(2026-11-01 12:33,内存自检204th+🔧backlog_scan修复+incr_eval 5items)已归档 → daily-memories-harness/2026-11-01.md。需要时再读。

> 📦 R1160-R1161 流水(2026-11-01 11:46~11:54,内存自检199th-200th+incr_eval 2backlog全RESOLVED+scan_backlog=0)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1160 incr_eval deepseek django-11815+hermes astropy-14539均RESOLVED·R1161 scan_backlog=0·predict 5路alive·硬约束tracked=0✅。需要时再读。

> 📦 R1154-R1159 流水(2026-11-01 10:34~11:32,6轮内存自检193rd-198th+incr_eval多条BACKLOG)已归档 → daily-memories-harness/2026-11-01.md。结论：内存全PASS·R1159 hermes astropy-14508 RESOLVED·R1158 deepseek django-11790 FAILED·R1157 claude-code pytest-5840 FAILED·R1156 deepseek django-11749 FAILED+opencode/pi重启·R1155 codex+deepseek各1 RESOLVED·R1154 hermes astropy-14365 FAILED。需要时再读。
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
