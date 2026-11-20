# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **R2802 · 2026-11-20 15:2x — Phase 0 监控冻结态（OOM 事故后带护栏分批灰度重启·14:5x 令）·未自动续跑任何在途任务**·**心跳第一行**: ✅Phase 0 monitor-only·①护栏守护已运行(PID931671·ppid1·15:16启动·MemAvail<400G|load>160→docker kill harness 评测容器·只识别 sweb.eval.*/swebench/*/alexgshaw/*·绝不碰别线/宿主进程)②loop CPU 节流已写入 baize_harness_loop.sh(HARNESS_NICE19/IONICE3/OMP8/LOAD_MAX120 + taskline=nice/ionice + OMP env + pretrain load 闸·bash -n 过✅·待 loop 重启生效·本轮不自行重启以免 §3.5(4) PATH/proxy 静默空转陷阱 + 双 agent 竞态)③自检clean(load27.6/224=12%✅·mem avail1498G✅·无失控进程)④docker ps 无 harness 评测容器✅⑤**按「全部暂停」冻结令杀停在途 opencode×deepseek MM predict(PID962346·启动14:19=14:5x令前·非失控 CPU53%/RSS1.2G·属无 ulimit 宿主 predict=OOM 风险向量·SIGTERM 已终止✅·未碰父 bash/pretrain cline/hub daemon)**⑥pretrain step~7.1s<7.4s✅(judge 满足·因 harness 冻结非因节流 live)·**在途任务全暂停待解冻令放行**: R2800 deepseek incr_eval(5 matplotlib)·MM 2×3 predict 6路·Verified predict codex438/pi447/dsh329 3路·**下轮计划**: 持续 Phase 0 监控(每~15min·WAITING=1)直到运维「解冻」令；解冻前落地硬护栏(docker eval --memory128g/--cpus16·宿主 predict ulimit -v 200GiB·.12 均摊)·🚫不跑 eval/不起 docker 评测/不起新 predict·WAITING=1·📦 TASK≈29.4KB(✅≤32KB) MEMORY≈31KB(✅≤32KB)
> 📦 R2800 流水已归档 → daily-memories-harness/2026-11-20.md（incr_eval轮·R2799 setsid根因修复重跑·codex R2800 COMPLETE 9658 FAILED+9673/9698 RESOLVED→115/23.0%+2·deepseek R2800 RUNNING 5 matplotlib·7way REGEN R2800·MM 633/2880·自检clean）。需要时再读。
> 📦 R2799 流水已归档 → daily-memories-harness/2026-11-20.md（incr_eval轮·R2799未用setsid→sg docker被SIGHUP杀→9673孤儿·codex 9658 FAILED·R2800 setsid修复重跑codex 9673+9698 RESOLVED→115·deepseek R2800 RUNNING·7way REGEN·MM 633/2880·自检clean）。需要时再读。
> 📦 R2798 流水已归档 → daily-memories-harness/2026-11-20.md（监控轮·incr_eval R2796 deepseek matplotlib-23314仍RUNNING·codex113已REGEN入7way报告·MM 2×3 620/2880·6路全RUN·自检clean）。需要时再读。
> 📦 R2797 流水已归档 → daily-memories-harness/2026-11-20.md（监控轮·incr_eval R2796 deepseek matplotlib-23314仍RUNNING·codex113已REGEN入7way报告·MM 2×3 617/2880·6路全RUN·自检clean）。需要时再读。
> 📦 R2796 流水已归档 → daily-memories-harness/2026-11-20.md（incr_eval轮·codex sphinx-9367 RESOLVED→113/22.6%+1·deepseek django-16950 FAILED(ability)+matplotlib-23314 docker eval RUNNING·MM 2×3 612/2880·6路全RUN·自检clean）。需要时再读。
> 📦 R2795 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM 2×3 591/2880(+8)·6路全RUN·backlog=1<2阈值→skip incr_eval·Verified predict codex427/pi444/dsh307 alive·自检clean）。需要时再读。
> 📦 R2794 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2794 COMPLETE: codex sphinx-8593 RESOLVED→112/22.4%+1·dsh django-16642 RESOLVED→191/38.2%+1·MM 2×3 583/2880·6路全RUN·自检clean）。需要时再读。
> 📦 R2793 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2793 COMPLETE: dsh+3→190/38.0%·7way REGEN 5177B·MM 2×3 564/2880·自检clean）。需要时再读。
> 📦 R2792 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2792 COMPLETE: 4 instances全RESOLVED·pi+1→247/49.4%·dsh+3→187/37.4%·7way REGEN 5177B·MM 2×3 556/2880·自检clean）。需要时再读。
> 📦 R2786 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2786 COMPLETE: pi+1→244/48.8%·codex+1→111/22.2%·dsh+1→178/35.6%·7way REGEN 4859B·MM 2×3 459/2880·自检clean）。需要时再读。
> 📦 R2785 流水已归档 → daily-memories-harness/2026-11-19.md（sympy-24661 docker eval STALL修复→RESOLVED→cline303/60.6%·7way REGEN R2785·MM 431/2880·自检clean）。需要时再读。
> 📦 R2787 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2787 COMPLETE: pi matplotlib-14623→FAILED→pi不变244/48.8%·deepseek 3 new(django-16100/16116/16136)全RESOLVED→dsh178→181/36.2%(+3)·7way REGEN R2787 5176B·MM 2×3 515/2880·自检clean）。需要时再读。
> 📦 R2788 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+incr_eval R2787结果收集+7way报告REGEN·MM 2×3 515/2880·6路全RUN·Verified predict codex413/pi438/dsh280 alive·自检clean）。需要时再读。
> 📦 R2789 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2789 COMPLETE(pi+1/dsh+3)+merge_empties(21空patch)+7way报告REGEN·MM 2×3 526/2880·6路全RUN·Verified predict codex414/pi440/dsh283 alive·自检clean）。需要时再读。
> 📦 R2790 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2790 COMPLETE: codex sphinx-8035 FAILED+pi xarray-6744 RESOLVED✅re-eval·pi245→246/49.2%+1·7way REGEN 5177B·MM 540/2880·自检clean）。需要时再读。
> 📦 R2791 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM 2×3 551/2880·backlog=1<2阈值→skip incr_eval·7way无需REGEN·自检clean）。需要时再读。
> 📦 R2782 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval_R2777 COMPLETE+7way报告REGEN·MM 2×3 358/2880·6路全RUN·Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2781 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·incr_eval_R2777 RUNNING(matplotlib-24026)·MM 2×3 346/2880 has_patch319=92%·6路全RUN·Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2780 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·incr_eval_R2777 RUNNING(matplotlib-24026 docker up16min)·MM 2×3 327/2880 has_patch300=92%·6路全RUN·Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2779 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·incr_eval_R2777 RUNNING(matplotlib-24026)·MM 2×3 314/2880·6路全RUN·Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2778 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·incr_eval_R2777 RUNNING·MM 2×3 299/2880·6路全RUN·Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2777 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval_R2777 RUNNING·MM 2×3 276/2880·6路全RUN·Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2776 流水已归档 → daily-memories-harness/2026-11-19.md（deepseek 2路quota重启✅·MM 2×3 225/2880·6路全RUN·Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2775 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2771 COMPLETE+7way报告REGEN·MM 2×3 444/2880·2 deepseek STOPPED quota reset~18:10·4路RUN·自检clean）。需要时再读。
> 📦 R2774 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM 2×3 419/2880·2 deepseek路由STOPPED·4路RUN·incr_eval R2771 cline done·pi仍running·自检clean）。需要时再读。
> 📦 R2773 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+动作·MM 2×3 405/2880·2 deepseek路由STOPPED防quota污染·4路RUN·自检clean）。需要时再读。
> 📦 R2772 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM 2×3 378/2880·deepseek双路quota确认228 blocked(reset~18:10)·6路全RUN·自检clean）。需要时再读。
> 📦 R2771 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·cline +1 RESOLVED=301/500=60.2%·7way报告REGEN R2771·MM 2×3 356/2880·pi+deepseek eval后台运行·自检clean）。需要时再读。
> 📦 R2770 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·cline__deepseek quota-blocked(84)·MM 2×3 224/2880·Verified deltas<2不跑incr_eval·cumulative不变·无REGEN·自检clean）。需要时再读。
> 📦 R2768 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·自检clean·MM 2×3 76/2880(88%非空patch)·Verified 4路alive·pi incr_eval R2765 still running·无REGEN·cumulative不变）。需要时再读。
> 📦 R2767 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·自检clean·MM 2×3 65/2880(89%非空patch)·Verified 4路alive·pi incr_eval R2765 still running·无REGEN·cumulative不变）。需要时再读。
> 📦 R2766 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+incr_eval R2765结果收集: cline+4/codex+1/deepseek+7 RESOLVED·pi 10inst still running·7way报告REGEN R2766·MM 2×3 51/2880·Verified 4路alive·自检clean）。需要时再读。
> 📦 R2765 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+incr_eval R2765 launched·cline6 sphinx+codex2 sklearn+pi10 django/mpl+dsh7 django·MM 2×3 predict 6路RUN中·kimi慢已解·Verified 4路alive·自检clean）。需要时再读。
> 📦 R2764 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM 2×3 predict 6路RUN中·doubao最快5-6/480·deepseek2/480 text-only·kimi0/480慢(instance1跑12min)·Verified predict 4路alive(cline474/pi419/codex398/dsh270)·自检clean(load37/224=16.6%)·kimi慢标下轮复查）。需要时再读。
> 📦 R2763 流水已归档 → daily-memories-harness/2026-11-19.md（MM容器下载COMPLETE 580/580·gate 4/4 met·2×3 predict全6路启动·nice19/ionice3·实测opencode×doubao has_patch patch=598B✅·6路全RUN可恢复·SWE-bench Verified predict 4路alive·自检clean）。需要时再读。
> 📦 R2762 流水已归档 → daily-memories-harness/2026-11-19.md（MM 2×3 cline×doubao/deepseek silent-exit根因修复=sanitize_cline_prompt U+200B→ASCII空格·smoke全6路PASS: cline×kimi2284B/doubao1770B/deepseek4300B·opencode×kimi2441B/doubao1627B/deepseek6832B）。需要时再读。
> 📦 R2761 流水已归档 → daily-memories-harness/2026-11-19.md（MM 2×3 cline管线3bug修复+cline×kimi smoke PASS patch=2284B 51calls 491s+opencode×kimi PASS patch=2441B·两harness MM管线全通）。需要时再读。
> 📦 R2757 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval(cline+1 pi+2 RESOLVED)+MM 2×3可行性核查+6路配置落盘+7way报告REGEN·MM容器521/580=89.8%）。需要时再读。
> 📦 R2756 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器465/580=80.2%·pretrain未受影响·predict+2新各路<2阈值→不跑incr_eval·自检clean）。需要时再读。
> 📦 R2755 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器448/580=77.2%·predict自R2754仅+2新各路<2阈值→不跑incr_eval·predict 4路alive·cumulative不变·自检clean·pretrain未受影响）。需要时再读。
> 📦 R2754 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2752 merge确认(cline+3→295 dsh+2→168) 监控轮 codex 1empty merged 7way报告REGEN MM容器440/580 predict 4路alive 自检clean）。需要时再读。
> 📦 R2753 流水已归档 → daily-memories-harness/2026-11-19.md（MM容器下载巡检433/580+I/O清理kill 4 orphaned find / trees→load81→45·incr_eval R2752 running·predict 4路alive·自检clean）。需要时再读。
> 📦 R2752 流水已归档 → daily-memories-harness/2026-11-19.md（CPU螺旋kill 162核sklearn pytest+incr_eval R2752 CPU-limited launched·sklearn-13496 RESOLVED·MM容器429/580=74%·predict 4路alive·自检clean）。需要时再读。
> 📦 R2751 流水已归档 → daily-memories-harness/2026-11-19.md（§用户令11-19 08:2x交付·两份7way中文HTML报告REGEN主表置顶·TB-2.1主表opencode50.6/cline47.2/hermes46.1/pi39.3/cc33.7/codex28.1/deepseek12.4·SWE-bench Verified主表hermes88.8/opencode83.0/cc59.0/cline58.4/pi46.6/deepseek33.2/codex21.6·0script/0外链✅）。需要时再读。
> 📦 R2750 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·MM容器409/580=70.5%·incr_eval R2750 DONE: cline+5 RESOLVED→292/500=58.4%·deepseek+4 RESOLVED→166/500=33.2%·pi 1 FAILED+1 empty·codex 1 empty·CPU_SPIRAL_SKIP guard·7way报告REGEN·predict 4路alive·自检clean）。需要时再读。
> 📦 R2749 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器404/580·dsh 1 empty merged(django-14539)·无incr_eval(无路≥2 real_new)·7way报告REGEN(18720B)·predict 4路alive·自检clean）。需要时再读。
> 📦 R2748 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·+5 RESOLVED跨4路(cline+1/codex+1/dsh+1/pi+2)·13 empties merged·MM容器402/580·7way报告REGEN·predict 4路alive·自检clean）。需要时再读。
> 📦 R2747 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器397/580·1 empty merged(pi django-15128)·无incr_eval·7way报告REGEN(18720B)·predict 4路alive·自检clean）。需要时再读。
> 📦 R2746 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器395/580·0 empties merged·无incr_eval·7way报告REGEN(18720B)·predict 4路alive·自检clean）。需要时再读。
> 📦 R2745 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器393/580·pi 1 empty merged(django-15037)·无incr_eval(无路≥2 real_new)·2 real-patch pending(cline pytest-7521·codex scikit-learn-11310)·7way报告REGEN(18720B)·predict 4路alive·自检clean）。需要时再读。
> 📦 R2744 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·3 real-patch eval跨2路: cline +3 RESOLVED(pytest-7324/7432/7490)+cc +1 RESOLVED(sympy-13647)·dsh +1 empty merged·7way报告REGEN(18720B)·MM容器393/580·predict 4路alive·自检clean）。需要时再读。
> 📦 R2743 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器387/580·4 empties merged(cline1+codex2+dsh1)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2742 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器384/580·9 empties merged(cline1+codex6+pi2)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2741 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器382/580·10 empties merged(cline2+codex5+dsh2+pi1)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2740 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器379/580·5 empties merged(cline1+codex2+pi2)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2739 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器377/580·9 empties merged(cline1+codex6+dsh1+pi1)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2738 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器374/580·8 empties merged(cline1+codex5+dsh1+pi1)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2737 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器373/580·7 empties merged(cline1+codex4+dsh1+pi1)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2736 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器371/580·7 empties merged(cline1+codex5+pi1)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2735 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器369/580·13 empties merged(cline2+codex7+dsh2+pi2)·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 4路alive·自检clean）。需要时再读。
> 📦 R2732 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器361/580·11 empties merged·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2731 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器359/580·13 empties merged·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2730 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器357/580·10 empties merged·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2729 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器355/580·21 empties merged·1 pending real(cc sympy-13647<2阈值)·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2728 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器353/580·real_new=1<2阈值→不跑eval·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2727 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·16 empties merged·1 pending real(cc sympy-13647<2阈值)·resolved不变·MM容器351/580·predict 5路alive·自检clean）。需要时再读。
> 📦 R2726 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·2 real-patch评估(1 RESOLVED+1 FAILED)+16 empties merged·MM容器349/580·7way报告REGEN(18817B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2725 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·6 real-patch评估(5 RESOLVED+1 FAILED)+11 empties merged·MM容器345/580·7way报告REGEN(18817B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2724 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·4 real-patch评估(3 RESOLVED+1 FAILED)+6 empties merged·MM容器339/580·7way报告REGEN(18736B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2723 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·7 real-patch评估(5 RESOLVED+2 FAILED)+2 empties merged·MM容器332/580·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2722 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·5 real-patch评估完成(cline +2+codex +1 RESOLVED)·MM容器326/580·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2721 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·3 codex real-patch全RESOLVED(django-15368+15380+15467)+cc sympy-13031 FAILED+dsh django-13401 FAILED·7 empties merged·7way报告REGEN 18736B·MM容器323/580·predict 5路alive·自检clean）。需要时再读。
> 📦 R2720 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·4 real-patch全RESOLVED·48 empties merged·race-condition dedup fix·7way报告REGEN 18734B·MM容器322/580·predict 5路alive·自检clean）。需要时再读。
> 📦 R2719 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器320/580·real_new(pending)=0<2阈值→不跑eval·17 empties merged入failed·resolved不变·7way报告无需REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2718 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器319/580·real_new(pending)=0<2阈值→不跑eval·11 empties merged入failed·resolved不变·7way报告无需REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2717 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器318/580·real_new(pending)=0<2阈值→不跑eval·13 empties merged入failed·resolved不变·7way报告无需REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2716 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+merge-empties·MM容器317/580·real_new(pending)=0<2阈值→不跑eval·41 empties merged入failed·resolved不变·7way报告无需REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2715 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器316/580·real_new=1(pi django-13033)<2阈值→不跑eval·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2714 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器315/580·0新real-patch(21新预测全empty)·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2713 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器314/580·0新real-patch(14新预测全empty)·1 pending未达阈值·resolved不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2712 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器313/580·0新real-patch达阈值·empties合并入failed·predict 5路alive·自检clean）。需要时再读。
> 📦 R2711 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮·MM容器311/580·0新real-patch·predict 5路alive·自检clean）。需要时再读。
> 📦 R2710 流水已归档 → daily-memories-harness/2026-11-19.md（监控轮+incr_eval merge-only·0 real-patch→15 empty merge入failed·n更新 Pass%不变·7way报告REGEN(18814B)·MM容器310/580·predict 5路alive·自检clean）。需要时再读。
> 📦 R2709 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·2 real-patch跨2路(cline1+pi1全RESOLVED)+codex7empty merge·MM容器308/580·路径bug修复后首次自动正确·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2708 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval轮·4 real-patch跨3路(cline4全RESOLVED+pi1 FAILED+dsh1 RESOLVED)·MM容器306/580·路径bug发现并修复(EVAL_LOG_ROOT logs/run_evaluation→logs/evaluation)·6题误标infra手动修正·7way报告REGEN(18814B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2707 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器303/580·1新real-patch(cline)不足阈值·cumulative不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2706 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器301/580·0新incr_eval·cumulative不变·predict 5路alive·自检clean）。需要时再读。
> 📦 R2705 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器300/580·2 real-patch跨2路(deepseek django-12774+pi django-12858)全RESOLVED✅·FALSE INFRA路径bug复发已手动修正·7way报告REGEN(15506B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2704 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器298/580·1 real-patch(cline django-15957)FAILED(ability·patch applied but tests fail)·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2703 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器295/580·1 real-patch(codex django-13109)RESOLVED+5 empty-patch merge→failed·FALSE INFRA路径bug复发已手动修正·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2702 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器293/580·3 real-patch跨2路(pi1+dsh2)全RESOLVED·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2701 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮+FALSE INFRA路径bug修复·MM容器290/580·5 real-patch跨2路全RESOLVED+codex/dsh empty→failed·fix_r2701_eval_path.py修正5题误标infra·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2700 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器286/580·predict 5路alive·0新incr_eval·cumulative不变·自检clean）。需要时再读。
> 📦 R2699 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器283/580·predict 5路alive·0新incr_eval·cumulative不变·自检clean）。需要时再读。
> 📦 R2698 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮+FALSE INFRA修复·MM容器281/580·7 real-patch跨3路eval: cline5全RESOLVED+pi1 FAILED+dsh1 RESOLVED·fix_false_infra_R2698.py交叉校验修正7题误标infra·incr_eval模板已修·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2697 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器243/580·predict cline+1(django-15380)·无incr_eval(1新real-patch不足阈值)·cumulative不变·自检clean）。需要时再读。
> 📦 R2696 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载225/580·cline django-15375 RESOLVED·hermes infra修正 django-14631/14725 从infra→failed(能力·patch-apply-fail)·hermes infra 2→0·7way报告REGEN(18730B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2695 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载194/580·3 real-patch跨3路eval全FAILED(能力)·path bug致3题误标infra→fix_r2695修正为failed·75 empty-patch merge入failed·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2694 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载167/580·7 instances 4 routes·cline django-15268+15277 RESOLVED·cc django-14500 RESOLVED·pi django-11820 FAILED·hermes 14631/14725 infra第5次·deepseek django-12304 RESOLVED·7way报告REGEN(18741B)·predict 5路alive·自检clean）。需要时再读。
> 📦 R2693 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载133/580·3 instances 3 routes·cc django-14434 RESOLVED·deepseek django-12276 RESOLVED·hermes 14631/14725 infra第4次·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2692 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载117/580·4 instances 3 routes·+1 RESOLVED(pi django-11749)+2 FAILED+2 infra(hermes 14631/14725 第3次)·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2691 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载104/580·6 instances 4 routes·+4 RESOLVED+0 FAILED+2 infra·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2690 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载90/580·10 instances 6 routes·+7 RESOLVED+1 FAILED+2 infra·cline django-14725 race-fix·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2689 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·dedup修正+MM容器下载56/580·3 instances·dsh django-11603 RESOLVED·hermes 2 infra仍NO report.json·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2688 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·MM容器下载42/580·11 instances 6 routes·+6 RESOLVED+3 FAILED+2 infra·CPU_SPIRAL_SKIP added·pi infra dedup·7way报告REGEN·predict 5路alive·自检clean）。需要时再读。
> 📦 R2683及更早(R2683~R2481, Gen7 pilot, R474-R477) 流水已归档 → daily-memories-harness/2026-11-14~18.md + 2026-10-24~28.md。需要时再读。

## 📊 进度快照

PHASE:        Phase 0 监控冻结态（OOM 事故后带护栏分批灰度重启·2026-11-20 14:5x 令）·未自动续跑任何在途任务·WAITING=1
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·ability桶拆两层✅·SWE-bench Verified predict 7路·opencode415/500=83.0%✅·hermes444/500=88.8%✅·cc295/500=59.0%✅·cline-patched 500/500✅·§11-19报告重写✅(R2758)·MM容器下载COMPLETE(580/580)✅·2×3 predict 6路启动✅(R2763)·**Phase 0**: 护栏守护启动✅(PID931671)·loop CPU 节流写入+bash -n✅(待重启生效)·自检clean✅·无 eval 容器✅·在途 opencode×deepseek MM predict 按冻结令杀停✅
当前动作:     Phase 0 monitor-only：git pull→自检CPU/内存(load27.6/mem1498G)→核验无 eval 容器→杀停在途 predict(PID962346)→loop 节流改写+bash -n→写心跳→commit+push
下一步:       持续 Phase 0 监控(每~15min·WAITING=1)直到运维「解冻」令；解冻前落地硬护栏(docker eval --memory128g/--cpus16 wrapper·宿主 predict ulimit -v 209715200=200GiB+nice19+OMP≤8·.12 均摊 load 闸阈值80)；loop 重启使 CPU 节流生效（推荐: 登录 shell 或显式注入 PATH=$HOME/.local/bin + https_proxy=http://172.19.92.25:13128，见 AGENTS.md §3.5(4)）
阻塞:         无（冻结态·待运维解冻令）
ERROR_COUNT:  0
 体积: TASK≈29.4KB（✅≤32KB） / MEMORY≈31KB（✅≤32KB）
 SWE-bench Verified Pass%(分母恒500·冻结前最后值·解冻后续跑可能变): hermes444/500=88.8%·opencode415/500=83.0%·cline303/500=60.6%·cc295/500=59.0%·pi247/500=49.4%·dsh191/500=38.2%·codex115/500=23.0%·(predict 3路 codex438/pi447/dsh329 已冻结暂停)
 真实 Pass% (layer-A/B, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%
   SWE-bench Multimodal 2×3 predict(冻结暂停·R2763 14:56启动·480题/路): opencode×doubao212·cline×doubao194·opencode×deepseek74·opencode×kimi49·cline×kimi42·cline×deepseek49·6路已按14:5x冻结令暂停(opencode×deepseek PID962346已杀停)
  research日报11-19 harness建议: ①完成判据三分法 ②MM判分格式合法率vs正确率分两列+四组分组 ③20480生成上限写进评测配置 ④两档prompting分任务族报分 → 解冻后纳入(来自 research 日报 2026-11-19)
## 启动说明（首次唤醒）

1. **先读** `BAIZE_HARNESS_TASK.md` 全文。
2. **第一条命令**：`ls -la /nas_train/app.e0031982/harness/` —— 看清**有哪些 harness、各自什么形态**。
3. **然后**按任务书：**H-B 源码分析（cline 起）> H-A SWE-bench**。
4. ⚠️ **不许猜**；**每条结论贴 `路径:行号` 原文**。

## 关键路径速查

- **harness 源码**：`/nas_train/app.e0031982/harness/`（⚠️ **只读参考，不要改动上游代码**）
- **产物目录**：`doc/BaiZe-ISEDA2027/run/harness/`
- **共享工作副本**：`/nas_train/app.e0031982/code/super_intelligence_2035`（同一 NFS · git pull 后各线共享）
- **SWE-bench Verified 预测**：`run/harness/swebench_verified_full/predictions_glm53/`
- **SWE-bench Verified 评测**：`run/harness/swebench_verified_full/reports/eval_glm53_*.json`
- **双报告**：`reports/report_harness_glm53_7way_swebench_tb_zh.html` + `reports/report_harness_cline_special_zh.html`
- **报告生成器**：`run/harness/gen_report_glm53_7way.py` + `run/harness/gen_cline_special.py`