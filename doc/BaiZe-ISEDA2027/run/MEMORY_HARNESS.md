# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R629 SWE-bench全量500 predict 5路后台运行中(07:1x)·健康·opencode91/500接近100阈值·总361.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R629巡检✅
当前动作:     R629:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds(swebench_verified_full/predictions/文件计数):opencode91/500·cline86/500·claude-code70/500·pi64/500·codex50/500(5路总361). 自R628增量:cline+4·claude-code+2·opencode+1·pi/codex+0(pi/codex正处理大实例,孙etimes:pi1531·codex645<timeout1800s,正常). 最新pred时间:cline01:08·opencode01:08·claude-code01:05·codex00:59·pi00:44. 5父全ALIVE(etimes~42574-42694s≈11.8h)+5子run_verified_full.py+5孙run_single.py全ALIVE(孙etimes:pi1531·codex645·claude-code276·opencode78·cline73,全<1800s). 当前实例:cline→django-12308·codex→django-14053·claude-code→matplotlib-22865·opencode→sphinx-11445·pi→sympy-16766. 429错误=4个实例文件(极低,非系统级)·no-patch率:opencode3/91=3.3%·pi6/64=9.4%·cline10/86=11.6%·codex13/50=26%·claude-code19/70=27.1%·hermes/deepseek闸门FAIL未进全量(进程0,残留9+9 gate文件)·Docker0(predict阶段)·/data6.0T free(15% used)·mem1466G avail·load27.03·/dev/shm949G free(6% used).
下一步:       ①监控full_predict(每~100题报一次,opencode91接近100阈值,下次达100正式报进度)→②五路predict全完(ETA最慢codex~105h≈Nov3-4,最快opencode~53h≈Oct31-Nov1)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③).
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=~29.0KB(≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[01:12] R629 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode91/500·cline86/500·claude-code70/500·pi64/500·codex50/500(5路总361). 自R628增量:cline+4·claude-code+2·opencode+1·pi/codex+0. 最新pred时间:cline01:08·opencode01:08·claude-code01:05·codex00:59·pi00:44. 5父全ALIVE(etimes~42574-42694s≈11.8h)+5子+5孙run_single.py全ALIVE(孙etimes:pi1531·codex645·claude-code276·opencode78·cline73,全<1800s). 当前实例:cline→django-12308·codex→django-14053·claude-code→matplotlib-22865·opencode→sphinx-11445·pi→sympy-16766. 核查:①429错误=4个实例文件(极低,非系统级)②no-patch率:opencode3.3%·pi9.4%·cline11.6%·codex26%·claude-code27.1%③5父+5子+5孙全ALIVE④断点续跑正常⑤hermes/deepseek闸门FAIL未进全量(进程0,残留9+9 gate文件)⑥Docker0(predict阶段)⑦/data6.0T free(15%)·mem1466G avail·load27.03·/dev/shm949G free(6%). opencode91接近100阈值,ETA~1.2h≈02:20达100,下次正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~29.0KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[01:05] R628 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康. 权威落盘preds:opencode90/500·cline82/500·claude-code68/500·pi64/500·codex50/500(5路总354). 自R627增量:codex+1·claude-code+1·cline/opencode/pi+0(均处理大实例). 最新pred时间:claude-code01:02·codex00:59·cline00:55·opencode00:54·pi00:44. 5父全ALIVE(etimes~42226-42316s≈11.7h)+5子+5孙run_single.py全ALIVE(孙etimes:pi1168·opencode581·cline492·codex282·claude-code59,全<1800s). 当前实例:cline→django-12273·codex→django-14053·claude-code→matplotlib-22719·opencode→sphinx-10673·pi→sympy-16766. 核查:①预测阶段错误扫描=0真实predict-phase错误②5父+5子+5孙全ALIVE③断点续跑正常④hermes/deepseek闸门FAIL未进全量(进程0,残留9+9 gate文件)⑤Docker0(predict阶段)⑥/data6.0T free(15% used)·mem1468G avail·load34.79·/dev/shm948G free(61G used). ETA:最快opencode90→~53h≈Oct31-Nov1·最慢codex50→~103h≈Nov3-4. opencode90接近100阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~30.1KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[00:58] R627 巡检·5路健康·总352(opencode90·cline82·claude-code67·pi64·codex49)·增量+3·5父+5子+5孙全ALIVE·0错误·资源正常·WAITING=0.

> [00:51] R626 及更早巡检流水已归档 → daily-memories-harness/2026-10-28.md（5路健康·opencode89·总349·增量+0·大实例耗时正常·资源稳定）。需要时再读。

[00:45] R625 巡检SWE-bench全量500 predict·5路健康·opencode89·cline80·总374(含hermes/deepseek gate残留9+9). 自R624增量:opencode+2·cline+1·claude-code+2·pi+1·codex+0. 5父+5子+5孙全ALIVE(孙etimes全<1800s). 精确HTTP429/403扫描=0真实错误. /data6.0T·mem1474G·load28.95. WAITING=0.

[00:33] R623 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(flat dir文件计数):opencode87/500·cline75/500·codex49/500·claude-code65/500·pi63/500(总364). 自R622增量:cline+2·codex+1·其余+0(opencode/pi/claude-code正处理大实例). 最新pred时间:cline00:31·codex00:33·opencode00:23·pi00:22·claude-code00:22. 5父全ALIVE(etimes~40349-40469s≈11.2h)+5子+5孙run_single.py全ALIVE(孙etimes:cline54·codex~1139·opencode530·pi618·claude-code598,全<1800s). 当前实例:cline→django-12050·codex→django-14034·claude-code→matplotlib-20826·opencode→sphinx-10435·pi→sympy-16597. 核查:①精确HTTP429/403扫描(predict logs)=0真实错误(旧eval test_output里的"test_ticket17429"等是测试名含429数字,非API错误)②5父+5子+5孙全ALIVE③断点续跑正常④hermes/deepseek闸门FAIL未进全量⑤Docker0(predict阶段)⑥/data6.0T free·mem1475G avail·load30.14. ETA:最快opencode87→~53h≈Oct31·最慢codex49→~103h≈Nov2-3. opencode87/500接近100阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~28.5KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[00:27] R622 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(文件计数):opencode87/500·cline73/500·claude-code65/500·pi63/500·codex48/500. 自R621增量:opencode+1·cline+1·claude-code+1·pi+1·codex+0(6min间隔,符合预期). 最新pred时间:cline00:25·opencode00:24·claude-code00:23·pi00:22·codex00:14. 5父全ALIVE(etimes~39997-40117s≈11.1h)+5子+5孙run_single.py全ALIVE(孙etimes:cline108·opencode178·claude-code246·pi266·codex787,全<1800s). 当前实例:cline→django-11999·codex→django-14017·claude-code→matplotlib-20826·opencode→sphinx-10435·pi→sympy-16597. 核查:①精确HTTP429/403扫描=0行(launcher log grep命中1条=PID"142978"含"429"子串误匹配)②5父+5子+5孙全ALIVE③断点续跑正常④hermes/deepseek闸门FAIL未进全量⑤/data6.0T free·mem1475G avail·load27.85. ETA:最快opencode87→~53h≈Oct31·最慢codex48→~105h≈Nov3-4. opencode87/500接近100阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~28.0KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[00:21] R621 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(文件计数):opencode86/500·cline72/500·claude-code64/500·pi62/500·codex48/500. 自R620增量:pi+1·其余+0(6min间隔,符合预期). 最新pred时间:pi00:17·codex00:13·opencode00:13·claude-code00:11·cline00:06. 5父全ALIVE(etimes~39662-39782s≈11.03h)+5子+5孙run_single.py全ALIVE(孙etimes:pi248·codex452·opencode462·claude-code576·cline866,全<1800s). 当前实例:cline→django-11964·codex→django-14017·claude-code→matplotlib-20676·opencode→scikit-learn-9288·pi→sympy-16450. 核查:①精确HTTP429/403扫描=0行(launcher log grep命中1条=PID"142978"含"429"子串误匹配)②5父+5子+5孙全ALIVE③断点续跑正常④hermes/deepseek闸门FAIL未进全量⑤/data6.0T free·mem1475G avail·load30.02. ETA:最快opencode86→~53h≈Oct31·最慢codex48→~103h≈Nov2-3. opencode86/500接近100阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~28.0KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

> 📦 R619-R620 流水(2026-10-29 00:09~00:15, predict巡检)已归档 → daily-memories-harness/2026-10-29.md。需要时再读。

[00:04] R618 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(文件计数):opencode85/500·cline71/500·claude-code63/500·pi60/500·codex47/500. 自R617增量:cline+1·claude-code+1·opencode+0·pi+0·codex+0. 最新pred时间:cline00:03·claude-code00:02·opencode23:59·pi23:56·codex23:43(codex孙etimes=1206s<timeout1800s仍在跑django-14011,未超时). 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~38611-38731s≈10.75h)+5子run_verified_full.py+5孙run_single.py全ALIVE(孙etimes:codex1206·pi441·opencode276·claude-code101·cline2). 当前实例:cline→django-11951·codex→django-14011·claude-code→matplotlib-20488·opencode→scikit-learn-26323·pi→sympy-15875. 核查:②5父+5子+5孙全ALIVE③gw网关正常(5路仍在产pred)④log无429/quota/error/forbidden(全5路grep=0)⑤断点续跑正常⑥hermes(deepseek闸门FAIL未进全量⑦/data6.0T free·mem1476G avail·load29.45. opencode85/500接近100阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~22.0KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:59] R617 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(文件计数):opencode85/500·cline70/500·claude-code62/500·pi60/500·codex47/500. 自R616增量:opencode+1·pi+1·cline+0·claude-code+0·codex+0. 最新pred时间:opencode23:59·pi23:56·claude-code23:48·codex23:43·cline23:34(全在25min内✅=活). 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~38417-38447s≈10.7h)+5子+5孙run_single.py全ALIVE(孙etimes:opencode462·cline1462·codex922·claude-code609·pi157). 当前实例:cline→django-11885·codex→django-14011·claude-code→matplotlib-14623·opencode→scikit-learn-26194·pi→sympy-15875. 核查:②5父+5子+5孙全ALIVE③gw9090=curl超时(本shell无proxy,但5路仍在产pred=网关正常)④log无429/quota/error/forbidden(全5路0行)⑤断点续跑正常⑥hermes/deepseek闸门FAIL未进全量⑦/data6.0T free·mem1479G avail·load29.91. opencode85/500接近100阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY~20.0KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:53] R616 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(逐文件解析list[0].model_patch):opencode84/500(patch81,no_patch3,err0)·cline70/500(patch62,no_patch8,err0)·claude-code62/500(patch45,no_patch17,err0)·pi59/500(patch53,no_patch6,err0)·codex47/500(patch35,no_patch12,err0). 自R615增量:opencode+1·claude-code+1·pi+1·cline+0·codex+0. 最新pred时间:pi23:53·opencode23:51·claude-code23:48·codex23:43·cline23:34(全在19min内✅=活). 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~37967-38087s≈10.6h,13:17-18启动)+5子run_verified_full.py+5孙run_single.py全ALIVE(孙etimes:opencode102·codex562·claude-code249·cline1102·pi3). 当前实例:cline→django-11885·codex→django-14011·claude-code→matplotlib-14623·opencode→scikit-learn-26194·pi→sympy-15809. 核查:②5父+5子+5孙全ALIVE③gw9090=200✅④no_patch单列(claude-code17=适配器健康度偏低但闸门已过,patch45>0)⑤log无429/quota/error/forbidden(全5路0行)⑥断点续跑正常⑦hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑧/data6.0T·/dev/shm949G·mem1478G avail·load29.00. ETA(10.6h):opencode~52h·cline~64h·claude-code~75h·pi~79h·codex~100h(≈Nov2-3). 最高opencode84/500,接近~100题报进度阈值. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY=19.8KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:46] R615 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(逐文件解析model_patch):opencode83/500(patch80,no_patch3,err0)·cline70/500(patch62,no_patch8,err0)·claude-code61/500(patch44,no_patch17,err0)·pi58/500(patch52,no_patch6,err0)·codex47/500(patch35,no_patch12,err0). 自R614增量:claude-code+2·codex+1·opencode+0·cline+0·pi+0. 最新pred时间:claude-code23:46·codex23:43·opencode23:40·cline23:34·pi23:25(全在22min内✅=活). 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~37589-37709s≈10.4h,13:18启动)+5子run_verified_full.py+5孙run_single.py全ALIVE(各孙etimes:cline724·codex184·claude-code47·opencode372·pi1300). 核查:②5父+5子+5孙全ALIVE③gw9090=200·gw9091=403(auth-gated✅)④no_patch单列(claude-code17=适配器健康度偏低但闸门已过,patch44>0)⑤log无429/quota/error/forbidden(全5路0行)⑥断点续跑正常⑦hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑧/data6.0T·/dev/shm949G·mem1478G avail·load28.63(↓). ETA(10.4h):opencode~52h·cline~64h·claude-code~75h·pi~79h·codex~100h(≈Nov2-3). 最高opencode83/500,接近~100题报进度阈值. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY=18.5KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:40] R614 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 权威落盘preds(逐文件解析model_patch):opencode83/500(patch80,no_patch3,err0)·cline70/500(patch62,no_patch8,err0)·claude-code59/500(patch42,no_patch17,err0)·pi58/500(patch52,no_patch6,err0)·codex46/500(patch35,no_patch11,err0). 自R613增量:opencode+2·cline+1·claude-code+1·pi+0·codex+0. 最新pred时间:opencode23:40·cline23:34·claude-code23:36·pi23:25·codex23:13(全在30min内✅=活). 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~37149-37269s≈10.3h,13:18启动)+5子run_verified_full.py+5孙run_single.py全ALIVE. 核查:②5父+5子+5孙全ALIVE③gw9090/9091=000(本会话无proxy不可直连,进程仍在产pred=网关活)④no_patch单列(claude-code17=适配器健康度偏低但闸门已过,patch42>0)⑤log无429/quota/error/forbidden⑥断点续跑正常(resume loaded10)⑦hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑧/data6.0T·/dev/shm949G·mem1479G avail·load28.02(↓). ETA(10.3h):opencode~52h·cline~61h·claude-code~75h·pi~77h·codex~99h(≈Nov2-3). 最高opencode83/500,接近~100题报进度阈值. 体积自检:TASK=33364B(32.6KB,无已闭合块可归档)·MEMORY=17215B(16.8KB≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:34] R613 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~36838-36958s≈10.27h,13:18启动)+5子run_verified_full.py+5孙run_single.py全ALIVE(codex django-14007 1237s·pi sympy-15599 549s·opencode sklearn-25747 415s·claude-code django-17087 111s·cline django-11880 73s). 权威progress:opencode82/500(patch78,infra1,quota0,no_patch3)·cline72/500(patch61,infra3,quota1,no_patch7)·claude-code60/500(patch41,infra2,quota2,no_patch15)·pi59/500(patch52,infra1,quota2,no_patch4)·codex47/500(patch35,infra1,quota2,no_patch9). 自R612增量:cline+1·claude-code+1·opencode+0·pi+0·codex+0. 落盘preds:cline69·opencode81·codex46·pi58·claude-code58. 核查:②5父+5子+5孙全ALIVE③gw9090=403·9091=403(活着,auth-gated✅)④infra单列(均git-fetch-timeout,符合铁律3)⑤timeout=0⑥quota(codex2·pi2·claude-code2·cline1,已单列)⑦断点续跑正常⑧hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑨/data6.0T·/dev/shm949G·mem1480G avail·load28.44(↓)·docker perm-denied(predict不用)·log无429/error. ETA(10.27h):opencode~52h·cline~61h·claude-code~75h·pi~77h·codex~99h(≈Nov2-3). 最高opencode82/500,接近~100题报进度阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB)·MEMORY=~15.6KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:31] R612 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~36556-36676s≈10.2h,13:18启动)+5子run_verified_full.py+5孙run_single.py全ALIVE(opencode133s·cline289s·pi267s·codex955s·claude-code1633s). 权威progress:opencode82/500(patch78,infra1,quota0,no_patch3)·cline71/500(patch60,infra3,quota1,no_patch7)·pi59/500(patch52,infra1,quota2,no_patch4)·claude-code59/500(patch41,infra2,quota2,no_patch14)·codex47/500(patch35,infra1,quota2,no_patch9). 自R611增量:opencode+1·cline+1·pi+1·claude-code+0·codex+0. 落盘preds:cline68·opencode81·codex46·pi58·claude-code57. 核查:②5父+5子+5孙全ALIVE③gw9090=403·9091=403(活着,auth-gated✅)④infra单列(均git-fetch-timeout,符合铁律3)⑤timeout=0⑥quota(codex2·pi2·claude-code2·cline1,已单列)⑦断点续跑正常⑧hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑨/data6.0T·/dev/shm948G·mem1479G avail·load32.25·docker0·log无error/429. ETA(10.2h):opencode~52h·cline~61h·claude-code~76h·pi~76h·codex~98h(≈Nov2). 最高opencode82/500,接近~100题报进度阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB)·MEMORY=~14.2KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:19] R610 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~35812-35932s≈10.0h,13:18启动)+5子run_verified_full.py ALIVE+5孙run_single.py ALIVE(cline73s·opencode249s·codex211s·pi178s·claude-code889s). 权威progress:opencode81/500(patch77,infra1,quota0,no_patch3)·cline69/500(patch58,infra3,quota0,no_patch8)·claude-code59/500(patch41,infra2,quota2,no_patch14)·pi57/500(patch50,infra1,quota2,no_patch4)·codex47/500(patch35,infra1,quota2,no_patch9). 自R609增量:cline+1·codex+1·opencode+1·pi+1·claude-code+0. 落盘preds:cline66·opencode80·codex46·pi56·claude-code57. 核查:②5父+5子+5孙全ALIVE③gw_proxy9090=403·9091=403(活着,auth-gated✅)④infra单列(均git-fetch-timeout,符合铁律3)⑤timeout=0⑥quota低(codex2·pi2·claude-code2,已单列)⑦断点续跑正常⑧hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑨/data6.0T free·mem1481G avail·docker0(predict不用)·log无error/429. ETA(~10h速率):opencode~52h·cline~62h·claude-code~75h·pi~78h·codex~96h(最慢~Nov1). 最高opencode81/500,接近~100题报进度阈值. 体积自检:TASK=33364B(32.6KB)·MEMORY=11301B(11.0KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:24] R611 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~36227-36347s≈10.1h,13:18启动)+5子run_verified_full.py+5孙run_single.py全ALIVE(cline195s·opencode664s·codex626s·pi255s·claude-code1304s). 权威progress:opencode81/500(patch77,infra1,quota0,no_patch3)·cline70/500(patch59,infra3,quota1,no_patch7)·claude-code59/500(patch41,infra2,quota2,no_patch14)·pi58/500(patch51,infra1,quota2,no_patch4)·codex47/500(patch35,infra1,quota2,no_patch9). 自R610增量:cline+1·pi+1·opencode+0·claude-code+0·codex+0(cline quota现1,was0). 落盘preds:cline67·opencode80·codex46·pi57·claude-code57. 核查:②5父+5子+5孙全ALIVE③gw9090=403·9091=403(活着,auth-gated✅)④infra单列(均git-fetch-timeout,符合铁律3)⑤timeout=0⑥quota(codex2·pi2·claude-code2·cline1,已单列)⑦断点续跑正常⑧hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑨/data6.0T·/dev/shm948G·mem1479G avail·load35.7·docker0·log无error/429. ETA(10.1h):opencode~52h·cline~62h·claude-code~76h·pi~77h·codex~97h(≈Nov1). 最高opencode81/500,接近~100题报进度阈值,下次达100正式报进度. 体积自检:TASK=33364B(32.6KB)·MEMORY=~13.0KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[23:11] R609 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·稳步推进. 5父全ALIVE(cline4184703·codex32831·claude-code62463·opencode106230·pi142978,etimes~35463-35583s≈9.9h,13:18启动)+5子run_verified_full.py ALIVE+5孙run_single.py ALIVE(cline200s·opencode712s·codex1353s·pi44s·claude-code540s). 权威progress:opencode80/500(patch76,infra1,quota0,no_patch3)·cline68/500(patch57,infra3,quota0,no_patch8)·claude-code59/500(patch41,infra2,quota2,no_patch14)·pi56/500(patch49,infra1,quota2,no_patch4)·codex46/500(patch34,infra1,quota2,no_patch9). 自R608增量:cline+1·pi+1·opencode+0·claude-code+0·codex+0. 落盘preds:cline65·opencode79·codex45·pi55·claude-code57. 核查:②5父+5子+5孙全ALIVE③gw_proxy9090=200·9091=403(活着,auth-gated✅)④infra单列(均git-fetch-timeout,符合铁律3)⑤timeout=0⑥quota低(cline0·opencode0·codex2·pi2·claude-code2)⑦断点续跑正常⑧hermes(no_patch5>2)/deepseek(patch0)闸门FAIL未进全量⑨/data6.0T free·mem1481G avail·docker0(predict不用)·log无error/429. 最高opencode80/500,未到~100题报进度阈值. 体积自检:TASK=33364B(32.6KB)·MEMORY=11093B(10.9KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

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
