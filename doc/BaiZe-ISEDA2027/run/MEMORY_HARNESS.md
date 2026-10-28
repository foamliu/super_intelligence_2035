# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0

## 📊 进度快照

```
PHASE:        R680 SWE-bench全量500 predict 5路后台运行中(07:1x令)·健康·总596·常规巡检.
已完成:       H-B ctx压缩✅·Gate7/7(R466)·三路7x89(R479)·R527 TB报告✅·R539 pilot20报告✅·GATE v2全完成·R552 TB整改(QA 5问✅)✅·R584 补令-R580顶层结果JSON补齐untrack+gitignore加固✅·R582-R679巡检✅
当前动作:     R680:巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总596(与R679持平,当前题mid-run)·常规巡检. 权威progress JSON(06:39-06:48更新,本轮无新完成):cline-patched144(patch130,infra3,quota3,no_patch8)·opencode142(patch137,infra1,quota2,no_patch2)·pi114(patch104,infra1,quota3,no_patch6)·claude-code113(patch86,infra1,quota3,no_patch23)·codex83(patch65,infra1,quota2,no_patch15). 总596/2500 done(patch522,infra7,quota13,no_patch54,timeout0). 落盘predictions:cline141·opencode140·pi113·claude-code112·codex82. 自R679增量:+0(仅过7min,5孙run_single全mid-run). 5父orchestrator全ALIVE(etimes~63236-63356s≈17.6h,ppid=1)+5孙run_single全ALIVE(etimes348-872s,<1800s). 当前实例:cline→django-13964(348s)·codex→django-14999(872s)·pi→astropy-13977(488s)·opencode→sympy-13757(394s)·claude-code→pydata-xarray-4356(620s). no_patch率:opencode1.4%✅·cline5.6%✅·pi5.3%✅·codex18.1%🟠·claude-code20.4%🟠. timeout=0. hermes(10题no_patch5>2)/deepseek(10题patch0)闸门FAIL未进全量. Docker0(predict阶段). /data6.0T free(15%)·load28.38·mem1350G avail. gw_proxy9090/v1/models=200✅. log grep 429=0/quota=0/error=0全5路. ETA(17.6h速率):cline~Nov1·opencode~Nov1·pi~Nov2·claude-code~Nov2-3·codex~Nov3-4. 硬约束核验:predictions tracked=0✅·永久硬约束满足.
下一步:       ①继续监控full_predict(下次某路破150题时报进度)→②五路predict全完(ETA cline~Nov1·codex~Nov3-4)→全量eval(docker workers8-12)→③交付report_harness_swebench_verified_full500_zh.html. ④永久硬约束:禁止commit评测结果JSON(补令③)·已验predictions tracked=0✅.
阻塞:         无.
ERROR_COUNT:  0
📦 体积：TASK=33364B(32.6KB,略超32KB软标·<40KB红线·无可归档已闭合块) / MEMORY=28182B(27.5KB,≤32KB✅)
```

> 📦 Gen7 pilot(7×5) + Oracle check(R473) 已归档 → daily-memories-harness/2026-10-28.md。结论：cline/pi=100%,codex/opencode=60%,hermes/deepseek/claude-code=0%;oracle 15/15 mean=0.733(11/15可解)。需要时再读。

> 📦 R474-R477 关键发现详细块（2026-10-23~24, Docker pull/daemon.json proxy/cline TB_API_KEY root cause/7x89 launcher/镜像进度, ~120行）已归档 → daily-memories-harness/2026-10-24.md。结论：Docker pull 经 daemon.json proxies(172.19.92.25:13128)实测成功(推翻MITM误判); TB=89题(非15); cline-patched 0/15根因=launcher缺 export TB_API_KEY(已修); 7x89并发启动器就绪。需要时再读。

### 本唤醒流水
[06:55] R680 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总596(与R679持平,当前题mid-run)·常规巡检. 权威progress JSON(06:39-06:48更新,本轮无新完成):cline-patched144(patch130,infra3,quota3,no_patch8)·opencode142(patch137,infra1,quota2,no_patch2)·pi114(patch104,infra1,quota3,no_patch6)·claude-code113(patch86,infra1,quota3,no_patch23)·codex83(patch65,infra1,quota2,no_patch15). 总596/2500 done(patch522,infra7,quota13,no_patch54,timeout0). 落盘predictions:cline141·opencode140·pi113·claude-code112·codex82. 自R679增量:+0(仅过7min,5孙run_single全mid-run). 5父orchestrator全ALIVE(etimes~63236-63356s≈17.6h,ppid=1)+5孙run_single全ALIVE(etimes348-872s,<1800s). 当前实例:cline→django-13964(348s)·codex→django-14999(872s)·pi→astropy-13977(488s)·opencode→sympy-13757(394s)·claude-code→pydata-xarray-4356(620s). no_patch率:opencode1.4%✅·cline5.6%✅·pi5.3%✅·codex18.1%🟠·claude-code20.4%🟠. timeout=0. gw_proxy9090/v1/models=200✅. /data6.0T free(15%)·load28.38·mem1350G avail·Docker0(predict阶段). log grep 429=0/quota=0/error=0全5路. 硬约束核验:predictions tracked=0✅·永久硬约束满足. 体积自检:TASK=33364B(32.6KB)·MEMORY=28182B(27.5KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:48] R679 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总596·常规巡检. 权威progress JSON(06:39-06:48更新):cline-patched144(patch130,infra3,quota3,no_patch8)·opencode142(patch137,infra1,quota2,no_patch2)·pi114(patch104,infra1,quota3,no_patch6)·claude-code113(patch86,infra1,quota3,no_patch23)·codex83(patch65,infra1,quota2,no_patch15). 总596/2500 done(patch522,infra7,quota13,no_patch54,timeout0). 落盘predictions:cline141·opencode140·pi113·claude-code112·codex82. 自R678增量:+5(cline+1·opencode+2·pi+1·claude-code+1·codex+0). 5父orchestrator全ALIVE(etimes~62900-63016s≈17.5h,ppid=1)+5孙run_single全ALIVE(etimes8-532s,<1800s). 当前实例:cline→django-13964(8s)·codex→django-14999(532s)·pi→astropy-13977(148s)·opencode→sympy-13757(54s)·claude-code→pydata-xarray-4356(280s). no_patch率:opencode1.4%✅·cline5.6%✅·pi5.3%✅·codex18.1%🟠·claude-code20.4%🟠. timeout=0. gw_proxy9090/v1/models=200✅. /data6.0T free(15%)·load28.19·Docker0(predict阶段). log grep 429=0/quota=0/error=0全5路. 硬约束核验:predictions tracked=0✅·tracked JSON=498(474 instance输入+20 pilot instance+4 manifest,0结果JSON)·永久硬约束满足. 体积自检:TASK=33364B(32.6KB)·MEMORY=~26.8KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:44] R678 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总591·常规巡检. 权威progress JSON(06:32-06:39更新):cline-patched143(patch129,infra3,quota3,no_patch8)·opencode140(patch135,infra1,quota2,no_patch2)·pi113(patch103,infra1,quota3,no_patch6)·claude-code112(patch85,infra1,quota3,no_patch23)·codex83(patch65,infra1,quota2,no_patch15). 总591/2500 done(patch517,infra7,quota13,no_patch54,timeout0). 落盘predictions:cline140·opencode139·pi112·claude-code112·codex82. 自R677增量:+9(cline+1·opencode+1·pi+2·claude-code+2·codex+3). 5父orchestrator全ALIVE(etimes~62582-62702s≈17.4h,ppid=1)+5孙run_single全ALIVE(etimes218-672s,<1800s). 当前实例:cline→django-13933(553s)·codex→django-14999(218s)·pi→astropy-13579(484s)·opencode→sympy-13615(672s)·claude-code→pydata-xarray-4094(261s). no_patch率:opencode1.4%✅·cline5.6%✅·pi5.3%✅·codex18.1%🟠·claude-code20.5%🟠. timeout=0. gw_proxy9090/v1/models=200✅. /data6.0T free(15%)·load33.30·Docker0(predict阶段). log grep 429=0/quota=0/error=0全5路. 硬约束核验:predictions tracked=0✅. 体积自检:TASK=33364B(32.6KB)·MEMORY=25310B(24.7KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:37] R677 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总581·常规巡检. 落盘predictions权威计数:cline-patched140(patch129,no_patch11)·opencode138(patch135,no_patch3)·pi112(patch103,no_patch9)·claude-code110(patch84,no_patch26)·codex81(patch64,no_patch17). 总581/2500 done(patch515,no_patch66,timeout0). 自R676增量:+7. 5父orchestrator全ALIVE(etimes~62200-62330s≈17.3h)+5孙run_single全ALIVE(etimes12-327s). 当前实例:cline→django-13933·codex→django-14855·pi→astropy-13579·opencode→sympy-13615·claude-code→pydata-xarray-4075. no_patch率:opencode2.2%✅·cline7.9%✅·pi8.0%✅·codex21.0%🟠·claude-code23.6%🟠. log grep 429=0/quota=0/error=0全5路. gw_proxy9090/v1/models=200✅. /data6.0T free(15%)·load27.51·Docker0(predict阶段). 硬约束核验:predictions tracked=0✅. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:30] R676 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总582·常规巡检. 权威progress JSON(06:00-06:28更新):cline142(patch128,infra3,quota3,no_patch8)·opencode139(patch134,infra1,quota2,no_patch2)·pi111(patch102,infra1,quota3,no_patch5)·claude-code110(patch83,infra1,quota3,no_patch23)·codex80(patch63,infra1,quota2,no_patch14). 总582/2500 done(patch510,infra7,quota13,no_patch52,timeout0). 落盘predictions:cline-patched139·opencode137·pi110·claude-code109·codex79. 自R675增量:+7(cline+2·opencode+3·claude-code+2). 5父orchestrator全ALIVE(etimes~61750-61873s≈17.2h)+5孙run_single全ALIVE(etimes66-1751s,<1800s). 当前实例:cline→django-13925(154s)·codex→django-14792(1737s)·pi→astropy-13398(1751s)·opencode→sympy-13551(392s)·claude-code→pydata-xarray-3993(66s). no_patch率:opencode1.4%✅·cline5.6%✅·pi4.5%✅·codex17.5%🟠·claude-code20.9%🟠. timeout=0. gw_proxy9090/v1/models=200✅. /data6.0T free(15%)·load31.05·Docker0(predict阶段). log grep 429=0/quota=0/error=0全5路. 硬约束核验:predictions tracked=0✅·progress tracked=0✅·永久硬约束满足. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:18] R675 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总575·常规巡检. 权威progress JSON(05:59-06:16更新):cline140(patch126,infra3,quota3,no_patch8)·opencode136(patch131,infra1,quota2,no_patch2)·pi111(patch102,infra1,quota3,no_patch5)·claude-code108(patch81,infra1,quota3,no_patch23)·codex80(patch63,infra1,quota2,no_patch14). 总575/2500 done(patch503,infra7,quota13,no_patch52,timeout0). 落盘predictions:cline-patched137·opencode134·pi110·claude-code107·codex79(另gate hermes9·deepseek-harness9). 自R674增量:+2(cline+1·claude-code+1). 5父orchestrator全ALIVE(etimes~61100-61200s≈17h)+5孙run_single全ALIVE(etimes60-1110s,<1800s). 当前实例:cline→django-13821(60s)·codex→django-14792(1030s)·pi→astropy-13398(1044s)·opencode→sympy-13091(1110s)·claude-code→pydata-xarray-3305(310s). no_patch率:opencode1.5%✅·cline5.7%✅·pi4.5%✅·codex17.5%🟠·claude-code21.3%🟠. timeout=0. hermes(10题no_patch5>2)/deepseek(10题patch0)闸门FAIL未进全量. Docker0(predict阶段). /data6.0T free(15%)·load30.40. progress JSON 05:59-06:16实时更新+gw_proxy9090/v1/models=200✅. ETA(17h速率):cline~Nov1·opencode~Nov1·pi~Nov2·claude-code~Nov2-3·codex~Nov3. 硬约束核验:predictions tracked=0✅·progress tracked=0✅·永久硬约束满足. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:11] R674 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总573·常规巡检. 权威progress JSON(05:59-06:09更新):cline139(patch125,infra3,quota3,no_patch8)·opencode136(patch131,infra1,quota2,no_patch2)·pi111(patch102,infra1,quota3,no_patch5)·claude-code107(patch80,infra1,quota3,no_patch23)·codex80(patch63,infra1,quota2,no_patch14). 总573/2500(patch501,infra7,quota13,no_patch52,timeout0). 落盘predictions:cline-patched136·opencode134·pi110·claude-code106·codex79·gate(hermes9·deepseek-harness9). 自R673增量:+2(cline+1·claude-code+1). 5父orchestrator全ALIVE(etimes~60686-60806s≈16.9h,ppid=1)+5孙run_single全ALIVE(etimes110-750s,<1800s). 当前实例:cline→django-13820(126s)·codex→django-14792(670s)·pi→astropy-13398(684s)·opencode→sympy-13091(750s)·claude-code→pydata-xarray-3151(294s). no_patch率:opencode1.5%✅·cline5.8%✅·pi4.5%✅·codex17.5%🟠·claude-code21.5%🟠. timeout=0. gw_proxy9090/v1/models=200✅·progress 05:59-06:09实时更新✅. /data6.0T free(15%)·load29.36·Docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅. 体积自检:TASK=33364B(32.6KB)·MEMORY=30894B(30.2KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[06:06] R673 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总571·常规巡检. 权威progress JSON(05:59-06:03更新):cline138(patch124,infra3,quota2,no_patch9)·opencode136(patch131,infra1,quota2,no_patch2)·pi111(patch102,infra1,quota3,no_patch5)·claude-code106(patch79,infra1,quota3,no_patch23)·codex80(patch63,infra1,quota2,no_patch14). 总571/2500(patch499,infra7,quota12,no_patch53,timeout0). 落盘predictions:cline-patched135·opencode134·pi110·claude-code105·codex79·gate(hermes9·deepseek-harness9). 自R672增量:+6(cline+1·opencode+1·pi+1·claude-code+2·codex+1). 5父orchestrator全ALIVE(etimes~60196-60316s≈16.75h,ppid=1)+5孙run_single全ALIVE(etimes30-264s,<1800s). 当前实例:cline→django-13810(264s)·codex→django-14792(180s)·pi→astropy-13398(194s)·opencode→sympy-13091(260s)·claude-code→pydata-xarray-3095(30s). no_patch率:opencode1.5%✅·cline6.5%✅·pi4.5%✅·codex17.5%🟠·claude-code21.7%🟠. timeout=0. progress 05:59-06:03实时更新证gateway在服务✅. /data6.0T free(15%)·load27.34·Docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅. 体积自检:TASK=33364B(32.6KB)·MEMORY=29771B(29.1KB,≤32KB✅). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[05:53] R672 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总565·常规巡检. 权威progress JSON(05:46-05:52更新):cline137(patch123,infra3,quota2,no_patch9)·opencode135(patch130,infra1,quota2,no_patch2)·pi110(patch101,infra1,quota3,no_patch5)·claude-code104(patch78,infra1,quota2,no_patch23)·codex79(patch62,infra1,quota2,no_patch14). 总565/2500(patch494,infra7,quota11,no_patch53,timeout0). 落盘predictions:cline133·opencode133·pi109·claude-code103·codex77·gate(hermes9·deepseek0). 自R671增量:+6(cline+2·opencode+1·pi+1·claude-code+1·codex+1). 5父orchestrator全ALIVE(etimes~59483-59603s≈16.5h,ppid=1)+5孙run_single全ALIVE(etimes228-571s,<1800s). 当前实例:cline→django-13807(246s)·codex→django-14771(571s)·pi→astropy-13236(285s)·opencode→sympy-13031(228s)·claude-code→psf-requests-5414(257s). no_patch率:opencode1.5%✅·cline6.6%✅·pi4.5%✅·codex17.7%🟠·claude-code22.1%🟠. timeout=0. gw_proxy探针curl=000(需auth)但progress 05:46-05:52实时更新证gateway在服务✅. /data6.0T free(15%)·load27.32·Docker0. 硬约束:predictions tracked=0✅·progress tracked=0✅·17 tracked"result-ish"全为.py+.html(非结果JSON,允许)✅. 体积自检:TASK=33364B(32.6KB)·MEMORY≈32400B(31.6KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.


[05:50] R671 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总559·常规巡检. 权威progress JSON(05:38-05:45更新):cline135(patch121,infra3,quota2,no_patch9)·opencode134(patch129,infra1,quota2,no_patch2)·pi109(patch100,infra1,quota3,no_patch5)·claude-code103(patch77,infra1,quota2,no_patch23)·codex78(patch61,infra1,quota2,no_patch14). 总559/2500(patch488,infra7,quota11,no_patch53,timeout0). 落盘predictions:cline132·opencode132·pi108·claude-code101·codex77·gate(hermes9·deepseek10). 自R670增量:+7(cline+1·opencode+1·pi+1·claude-code+2·codex+2). 5父orchestrator全ALIVE(etimes~59000-59168s≈16.4h)+5孙run_single全ALIVE(etimes51-417s,<1800s). 当前实例:cline→django-13794(227s)·codex→django-14771(318s)·pi→astropy-13033(417s)·opencode→sympy-12489(162s)·claude-code→psf-requests-2931(51s). no_patch率:opencode1.5%✅·cline6.7%✅·pi4.6%✅·codex17.9%🟠·claude-code22.3%🟠. timeout=0. gw_proxy9090/9091=403(alive✅). /data6.0T free(15%)·load28.41·Docker0(predict阶段). 硬约束核验:predictions tracked=0✅·progress tracked=0✅·非instance结果JSON tracked=0✅·instance定义tracked=458(允许). 体积自检:TASK=33364B(32.6KB)·MEMORY≈32700B(31.9KB). 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[05:38] R670 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总552·常规巡检. 权威progress JSON(05:35-05:38):cline134(patch120,infra3,quota2,no_patch9)·opencode133(patch128,infra1,quota2,no_patch2)·pi108(patch99,infra1,quota3,no_patch5)·claude-code101(patch75,infra1,quota2,no_patch23)·codex76(patch59,infra1,quota2,no_patch14). 总552/2500(patch481,infra7,quota11,no_patch53,timeout0). 落盘predictions:cline130·opencode131·pi107·claude-code100·codex74·gate(hermes9·deepseek10). 自R669增量:+10(cline+3·opencode+1·pi+1·claude-code+4·codex+1). 5父orchestrator全ALIVE(etimes~58700s≈16.3h)+5孙run_single全ALIVE(etimes9-1770s,<1800s). 当前实例:cline→django-13741(200s)·codex→django-14725(1770s近超时)·pi→sympy-24661(142s)·opencode→sympy-12481(103s)·claude-code→psf-requests-1921(9s). no_patch率:opencode1.5%✅·cline6.7%✅·pi4.6%✅·codex18.4%🟠·claude-code22.8%🟠. timeout=0. gw_proxy=403(alive✅). /data6.0T free(15%)·load26.23·Docker0(predict阶段). 硬约束核验:predictions tracked=0✅·progress tracked=0✅·非instance结果JSON tracked=0✅·instance定义tracked=458(允许). 体积自检:TASK=33364B(32.6KB)·MEMORY≈30.8KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[05:30] R669 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总542·常规巡检. 权威progress JSON(05:01-05:30更新):opencode132(patch127,infra1,quota2,no_patch2)·cline131(patch117,infra3,quota2,no_patch9)·pi107(patch98,infra1,quota3,no_patch5)·claude-code97(patch72,infra1,quota2,no_patch22)·codex75(patch59,infra1,quota2,no_patch13). 总542/2500 done(patch473,infra7,quota11,no_patch51,timeout0). 落盘predictions=541(cline-patched131·opencode132·pi107·claude-code97·codex75·hermes9gate). 自R668增量:+4(cline+2·pi+2). 5父orchestrator全ALIVE(etimes~58135-58256s≈16.2h)+5孙run_single全ALIVE(etimes25-1740s,<1800s). 当前实例:cline→新(25s)·codex→django-14725(1373s)·pi→新(105s)·opencode→sympy-12419(989s)·claude-code→seaborn-3187(1740s近超时). no_patch率:opencode1.5%✅·cline6.9%✅·pi4.7%✅·codex17.3%🟠·claude-code22.7%🟠. timeout=0. gw_proxy9090=403(alive✅). /data6.0T free(15%)·load27.73·Docker0(predict阶段). 硬约束核验:predictions tracked=0✅·progress_*tracked=0✅. 体积自检:TASK=33364B(32.6KB)·MEMORY≈29.6KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.

[05:23] R668 巡检SWE-bench全量500 predict(运维令10-28 07:1x)·5路健康·总538·常规巡检. 权威progress JSON(05:01-05:23更新):opencode132(patch127,infra1,quota2,no_patch2)·cline129(patch115,infra3,quota2,no_patch9)·pi105(patch96,infra1,quota3,no_patch5)·claude-code97(patch72,infra1,quota2,no_patch22)·codex75(patch59,infra1,quota2,no_patch13). 总538/2500 done(patch469,infra7,quota11,no_patch51,timeout0). 落盘predictions=538(cline-patched126·opencode130·pi103·claude-code96·codex74·hermes9). 自R667增量:+2(cline+1·pi+1). 5父orchestrator全ALIVE(etimes~57778-57898s≈16.1h,ppid=1祖)+5孙run_single全ALIVE(etimes55-1275s,均<1800s超时). 当前实例:cline→django-13569(55s)·codex→django-14725(908s)·pi→sympy-24213(301s)·opencode→sympy-12419(524s)·claude-code→seaborn-3187(1275s). no_patch率:opencode1.5%✅·cline7.0%✅·pi4.8%✅·codex17.3%🟠·claude-code22.7%🟠. timeout=0. gw_proxy9090=403(alive✅). /data6.0T free(15%)·load26.98·Docker0(predict阶段). 硬约束核验:predictions tracked=0✅·progress_*tracked=0✅·harness JSON tracked=445(instance定义). 体积自检:TASK=33364B(32.6KB)·MEMORY≈29.4KB. 判据自检:07:1x全量500运维令仍在跑(predict运行中,未交付)→WAITING=0.


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
