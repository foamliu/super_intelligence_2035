# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R689 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总635(+3)·稳步推进.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R688巡检✅
当前动作:     R689:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总635(+3). 权威progress JSON(07:47-08:02更新):cline155(patch141,infra3,quota3,no_patch8)·opencode147(patch141,infra1,quota2,no_patch3)·pi128(patch116,infra1,quota3,no_patch8)·claude-code119(patch91,infra1,quota3,no_patch24)·codex86(patch66,infra1,quota2,no_patch17). 总635/2500 done(patch555,infra7,quota13,no_patch60,timeout0). 落盘predictions:cline-patched152·opencode145·pi127·claude-code118·codex85=627. 5父orchestrator全ALIVE(etimes~67395-67515s≈18.7h,ppid=1)+5孙run_single全ALIVE(etimes68-971s,<1800s). no_patch率:opencode2.0%✅·cline5.2%✅·pi6.3%✅·codex19.8%🟠·claude-code20.2%🟠. timeout=0. 429 count=0全5路. Docker0(predict阶段). /data6.0T free(15%)·load26.33·mem1325G avail. gw_proxy9090/v1/models=200✅. ETA(18.7h速率):cline~Nov2·opencode~Nov3·pi~Nov3·claude-code~Nov4·codex~Nov6. 硬约束核验:predictions tracked=0✅·progress JSON tracked=0✅·永久硬约束满足.
下一步:       ①继续监控full_predict(下次某路破200题时报进度,cline155/opencode147最近)→②五路predict全完(ETA cline~Nov2·codex~Nov6)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③)·已验predictions tracked=0✅.
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=23934B(23.4KB,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[08:03] R689 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总635(+3)·常规巡检. 权威progress JSON(07:47-08:02更新):cline155(patch141,infra3,quota3,no_patch8)·opencode147(patch141,infra1,quota2,no_patch3)·pi128(patch116,infra1,quota3,no_patch8)·claude-code119(patch91,infra1,quota3,no_patch24)·codex86(patch66,infra1,quota2,no_patch17). 总635/2500 done(patch555,infra7,quota13,no_patch60,timeout0). 落盘predictions:cline-patched152·opencode145·pi127·claude-code118·codex85=627. 自R688增量:+3(cline+2,pi+1,opencode+0,claude-code+0,codex+0). 5父orchestrator全ALIVE(etimes~67395-67515s≈18.7h,ppid=1)+5孙run_single全ALIVE(etimes68-971s,<1800s). 当前实例:cline→django-14238(68s)·codex→django-15098(439s)·pi→astropy-8707(206s)·opencode→sympy-13974(734s)·claude-code→pydata-xarray-6599(971s). no_patch率:opencode2.0%✅·cline5.2%✅·pi6.3%✅·codex19.8%🟠·claude-code20.2%🟠. timeout=0. 429 count=0全5路. Docker0(predict阶段). /data6.0T free(15%)·load26.33·mem1325G avail·gw_proxy9090/v1/models=200✅. 硬约束核验:predictions tracked=0✅·progress JSON tracked=0✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块)·MEMORY=23934B(23.4KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[07:58] R688 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总632(+7)·常规巡检. 权威progress JSON(07:47-07:56更新):cline153(patch139,infra3,quota3,no_patch8)·opencode147(patch141,infra1,quota2,no_patch3)·pi127(patch115,infra1,quota3,no_patch8)·claude-code119(patch91,infra1,quota3,no_patch24)·codex86(patch66,infra1,quota2,no_patch17). 总632/2500 done(patch552,infra7,quota13,no_patch60,timeout0). 落盘predictions:cline150·opencode145·pi126·claude-code118·codex85=624. 自R687增量:+7(cline+2,opencode+1,pi+3,claude-code+0,codex+1). 5父orchestrator全ALIVE(etimes~67029-67149s≈18.6h,ppid=1)+5孙run_single全ALIVE(etimes73-605s,<1800s). 当前实例:cline→django-14155(272s)·codex→django-15098(73s)·pi→astropy-7671(190s)·opencode→sympy-13974(368s)·claude-code→pydata-xarray-6599(605s). no_patch率:opencode2.0%✅·cline5.2%✅·pi6.3%✅·codex19.8%🟠·claude-code20.2%🟠. timeout=0. Docker0(predict阶段). /data6.0T free(15%)·load30.10·mem1328G avail·gw_proxy9090/v1/models=200✅. 硬约束核验:predictions tracked=0✅·progress JSON tracked=0✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块)·MEMORY=22566B(22.0KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[07:47] R687 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总625(+2)·常规巡检. 权威progress JSON(07:21-07:47更新):cline151(patch137,infra3,quota3,no_patch8)·opencode146(patch141,infra1,quota2,no_patch2)·pi124(patch112,infra1,quota3,no_patch8)·claude-code119(patch91,infra1,quota3,no_patch24)·codex85(patch66,infra1,quota2,no_patch16). 总625/2500 done(patch547,infra7,quota13,no_patch58,timeout0). 落盘predictions:cline148·opencode144·pi123·claude-code117·codex84=616. 自R686增量:+2(pi+1,claude-code+1). 5父orchestrator全ALIVE(etimes~66379-66499s≈18.4h,ppid=1)+5孙run_single全ALIVE(etimes209-1510s,<1800s). 当前实例:cline→django-14122(375s)·codex→django-15037(1213s)·pi→astropy-7166(209s)·opencode→sympy-13878(1510s)·claude-code→pydata-xarray-6461(518s). no_patch率:opencode1.4%✅·cline5.3%✅·pi6.5%✅·codex18.8%🟠·claude-code20.2%🟠. timeout=0. Docker0(predict阶段). /data6.0T free(15%)·load28.63·mem1332G avail·gw_proxy9090/v1/models=200✅. 硬约束核验:predictions tracked=0✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块)·MEMORY归档R671-R680后≈28KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[07:40] R686 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总623(+7)·cline破150报进度. 权威progress JSON(07:21-07:40更新):cline151(patch137,infra3,quota3,no_patch8)·opencode146(patch141,infra1,quota2,no_patch2)·pi123(patch111,infra1,quota3,no_patch8)·claude-code118(patch90,infra1,quota3,no_patch24)·codex85(patch66,infra1,quota2,no_patch16). 总623/2500 done(patch545,infra7,quota13,no_patch58,timeout0). 落盘predictions:cline147·opencode144·pi122·claude-code117·codex84=614. 自R685增量:+7(cline+3,pi+2,claude-code+2). 5父orchestrator全ALIVE(etimes~65965-66085s≈18.3h,ppid=1)+5孙run_single全ALIVE(etimes14-1110s,<1800s). 当前实例:cline→django-14089(14s)·codex→django-15037(813s)·pi→astropy-14995(85s)·opencode→sympy-13878(1110s)·claude-code→pydata-xarray-6461(118s). no_patch率:opencode1.4%✅·cline5.3%✅·pi6.5%✅·codex18.8%🟠·claude-code20.3%🟠. timeout=0. Docker0(predict阶段). /data6.0T free(15%)·load29.28·mem1334G avail·gw_proxy9090=200✅. ETA(18.3h速率):cline~Oct31·opencode~Oct31·pi~Nov1·claude-code~Nov1·codex~Nov3. 硬约束核验:predictions tracked=0✅·tracked JSON=475 instances+1 enriched(均为输入数据,0结果JSON)✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块)·MEMORY=~32.6KB(≤32KB软标附近·<40KB红线✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[07:30] R685 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总616(+3)·常规巡检. 权威progress JSON(07:19-07:30更新):cline148(patch134,infra3,quota3,no_patch8)·opencode146(patch141,infra1,quota2,no_patch2)·pi121(patch110,infra1,quota3,no_patch7)·claude-code116(patch89,infra1,quota3,no_patch23)·codex85(patch66,infra1,quota2,no_patch16). 总616/2500 done(patch540,infra7,quota13,no_patch56,timeout0). 落盘predictions:cline145·opencode144·pi120·claude-code115·codex84=608. 自R684增量:+3(cline+1,pi+1,codex+1). 5父orchestrator全ALIVE(etimes~65395-65515s≈18.2h,ppid=1)+5孙run_single全ALIVE(etimes45-631s,<1800s). 当前实例:cline→django-14034(45s)·codex→django-15037(243s)·pi→(重启中)·opencode→sympy-13878(540s)·claude-code→pydata-xarray-4695(631s). no_patch率:opencode1.4%✅·cline5.4%✅·pi5.8%✅·codex18.8%🟠·claude-code19.8%🟠. timeout=0. Docker0(predict阶段). /data6.0T free(15%)·load27.71·mem1.3Ti avail·gw_proxy9090=200✅·log grep 429=0/quota=0全5路. 硬约束核验:predictions tracked=0✅·非instance JSON tracked=4(0结果JSON)✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块)·MEMORY=32589B(31.8KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[07:22] R684 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总613(+5)·常规巡检. 权威progress JSON(07:09-07:22更新):cline147(patch133,infra3,quota3,no_patch8)·opencode146(patch141,infra1,quota2,no_patch2)·pi120(patch109,infra1,quota3,no_patch7)·claude-code116(patch89,infra1,quota3,no_patch23)·codex84(patch65,infra1,quota2,no_patch16). 总613/2500 done(patch537,infra7,quota13,no_patch56,timeout0). 落盘predictions:cline144·opencode144·pi119·claude-code115·codex83=605. 自R683增量:+5(cline+1,opencode+1,pi+2,claude-code+1,codex+0). 5父orchestrator全ALIVE(etimes~64934-65054s≈18h)+5孙run_single全ALIVE(etimes19-625s,<1800s). 当前实例:cline→django-14011(450s)·codex→django-15022(705s)·pi→astropy-14508(110s)·opencode→sympy-13878(19s)·claude-code→pydata-xarray-4695(110s). no_patch率:opencode1.4%✅·cline5.4%✅·pi5.8%✅·codex19.0%🟠·claude-code19.8%🟠. timeout=0. /data6.0T free(15%)·load28.89·mem1338G avail·Docker0(predict阶段). gw_proxy9090/v1/models=200✅. log grep 429=0/quota=0全5路. 硬约束核验:predictions tracked=0✅·reports JSON tracked=0✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB)·MEMORY=~30KB(≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[07:14] R683 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总608(+5)·常规巡检. 权威progress JSON(07:02-07:14更新):cline146(patch132,infra3,quota3,no_patch8)·opencode145(patch140,infra1,quota2,no_patch2)·pi118(patch108,infra1,quota3,no_patch6)·claude-code115(patch88,infra1,quota3,no_patch23)·codex84(patch65,infra1,quota2,no_patch16). 总608/2500 done(patch533,infra7,quota13,no_patch55,timeout0). 落盘predictions:cline142·opencode142·pi116·claude-code114·codex83=597. 自R682增量:+5(cline+1,opencode+1,pi+2,claude-code+0,codex+1). 5父orchestrator全ALIVE(etimes~64355-64475s≈17.9h,ppid=1)+5孙run_single全ALIVE(etimes67-625s,<1800s). 当前实例:cline→django-14007(625s)·codex→django-15022(125s)·pi→astropy-14309(67s)·opencode→sympy-13852(404s)·claude-code→pydata-xarray-4687(585s). no_patch率:opencode1.4%✅·cline5.5%✅·pi5.1%✅·codex19.0%🟠·claude-code20.0%🟠. timeout=0. /data6.0T free(15%)·load30.15·mem1343G avail·Docker0(predict阶段). gw_proxy9090/v1/models=200✅. log grep 429=0/quota=0全5路. 硬约束核验:predictions tracked=0✅·reports JSON tracked=0✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB)·MEMORY=32131B(31.4KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[07:07] R682 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总603(+6)·常规巡检. 权威progress JSON(07:07更新):cline-patched145(patch131,infra3,quota3,no_patch8)·opencode144(patch139,infra1,quota2,no_patch2)·pi116(patch106,infra1,quota3,no_patch6)·claude-code115(patch88,infra1,quota3,no_patch23)·codex83(patch65,infra1,quota2,no_patch15). 总603/2500 done(patch529,infra7,quota13,no_patch54,timeout0). 落盘predictions:cline142·opencode142·pi115·claude-code114·codex82=620. 自R681增量:+6. 5孙run_single全ALIVE(etimes115-1641s,<1800s). 当前实例:cline→django-14007(336s)·codex→django-14999(1641s)·pi→astropy-14182(253s)·opencode→sympy-13852(115s)·claude-code→pydata-xarray-4687(296s). no_patch率:opencode1.4%✅·cline5.5%✅·pi5.2%✅·codex18.1%🟠·claude-code20.0%🟠. timeout=0. /data6.0T free(15%)·load30.50·mem1345G avail·Docker0(predict阶段). gw_proxy9090/v1/models=200✅. log grep 429=0/quota=0全5路. 硬约束核验:predictions tracked=0✅·reports JSON tracked=0✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB)·MEMORY=30811B(30.1KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:59] R681 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总597(+1,pi完成1题)·常规巡检. 权威progress JSON(06:39-06:55更新):cline-patched144(patch130,infra3,quota3,no_patch8)·opencode142(patch137,infra1,quota2,no_patch2)·pi115(patch105,infra1,quota3,no_patch6)·claude-code113(patch86,infra1,quota3,no_patch23)·codex83(patch65,infra1,quota2,no_patch15). 总597/2500 done(patch523,infra7,quota13,no_patch54,timeout0). 落盘predictions:cline141·opencode140·pi114·claude-code112·codex82. 自R680增量:+1(pi 114→115,仅过4min). 5孙run_single全ALIVE(etimes293-1211s,<1800s). 当前实例:cline→django-13964(687s)·codex→django-14999(1211s)·pi→astropy-14096(293s)·opencode→sympy-13757(733s)·claude-code→pydata-xarray-4356(959s). no_patch率:opencode1.4%✅·cline5.6%✅·pi5.2%✅·codex18.1%🟠·claude-code20.4%🟠. timeout=0. gw_proxy9090/v1/models=200✅. /data6.0T free(15%)·load28.12·mem1349G avail·Docker0(predict阶段). log grep 429=0/quota=0/error=0全5路. 硬约束核验:predictions tracked=0✅·reports JSON tracked=0✅(496 tracked=instance定义文件,非结果)·永久硬约束满足. 体积自检:TASK=33364B(32.6KB)·MEMORY=29512B(28.8KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

> 📦 R671-R680 巡检流水(2026-10-29 05:50-06:55,10轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline135→148·opencode132→146·pi105→123·claude-code97→117·codex75→85),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R668-R670 巡检流水(2026-10-29 05:23~05:38,3轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline129→134·opencode132→133·pi105→108·claude-code97→101·codex75→76),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。


> 📦 R656-R664 巡检流水(2026-10-29 04:16~05:01,9轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(cline117→125·opencode121→128·pi93→100·claude-code90→96·codex72→73),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R652-R655 巡检流水(2026-10-29 03:50~04:12,4轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode118→120·cline116·pi90→93·claude-code89→90·codex68→72),全路timeout=0,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。






> 📦 R637-R651 巡检流水(2026-10-29 02:03~03:43,15轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode101→118·cline91→116·claude-code77→89·pi73→91·codex55→69),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。
> 📦 R627-R636 巡检流水(2026-10-29 00:58~02:03,10轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode90→101·cline82→91·claude-code67→77·pi64→73·codex49→55),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。

> 📦 R609-R625 巡检流水(2026-10-28 23:11~2026-10-29 00:45, R609-R625共~12轮常态巡检)已归档 → daily-memories-harness/2026-10-29.md。结论：5路predict持续健康运行,稳步推进(opencode80→89·cline70→80·claude-code59→68·pi56→64·codex47→50),全路timeout=0,无429系统级错误,infra单列,hermes/deepseek闸门FAIL未进全量。需要时再读。


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
