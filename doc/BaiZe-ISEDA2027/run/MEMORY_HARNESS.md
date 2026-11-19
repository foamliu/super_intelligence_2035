# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0
> 🆕 **R2755 · 2026-11-19 10:2x — 监控轮·MM容器448/580=77.2%·pretrain未受影响**·**心跳第一行**: 📦 **SWE-bench Multimodal容器下载**(用户令11-18 最高优先): **448/580 pulled=77.2%**(0 FAILED✅)·pull_all_images.sh alive(PID 3749136·NI=19·etime~17.4h)·当前拉img#449(highlightjs_1776_highlight.js-2726)·顺序拉/nice19/ionice3·不抢.29 CPU✅·速率~16/hr·余132→ETA~8h(≈18:30)·docker 1218 imgs/1.346TB·disk 27T avail✅·SWE-bench Verified 7路 cumulative(resolved/500·**不变**): **hermes444=88.8%**·**opencode415=83.0%**·**claude-code295=59.0%**·**cline295=59.0%**·**pi233=46.6%**·**deepseek168=33.6%**·**codex108=21.6%**·📌 **R2755监控轮**: predict自R2754仅+2新(cline+1 sklearn-25931·pi+1 django-16100)各路<2阈值→不跑incr_eval·codex/dsh无新增·predict 4路alive(cline456/codex387/pi400/dsh259·cc+opencode+hermes COMPLETE 500/500)·0 429✅·**自检**: load41/224≈18%busy✅·无本线proc>8000%CPU(top=cline-hub-daemon 35.5%+cline agent 49.2%)✅·disk /nas_train 27T avail✅·mem 1272G avail✅·pretrain GPU 68-100%util 74.8GB/81.5GB 未受影响✅·**全部运维令✅已交付**·WAITING=0·📦 TASK≈31.2KB MEMORY≈21.6KB(✅≤32KB)
> 📦 R2754 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2752 merge确认(cline+3→295 dsh+2→168) 监控轮 codex 1empty merged 7way报告REGEN MM容器440/580 predict 4路alive 自检clean）。需要时再读。
> 📦 R2753 流水已归档 → daily-memories-harness/2026-11-19.md（MM容器下载巡检433/580+I/O清理kill 4 orphaned find / trees→load81→45·incr_eval R2752 running·predict 4路alive·自检clean）。需要时再读。
> 📦 R2752 流水已归档 → daily-memories-harness/2026-11-19.md（CPU螺旋kill 162核sklearn pytest+incr_eval R2752 CPU-limited launched·sklearn-13496 RESOLVED·MM容器429/580=74%·predict 4路alive·自检clean）。需要时再读。
> 🆕 **R2752 · 2026-11-19 09:2x — CPU螺旋kill+incr_eval R2752 launched(CPU-limited)**·**心跳第一行**: 📌 **CPU自检(运维令11-02硬判据)**: 09:18发现cline-patched sklearn eval pytest(PID 284539)占**16199%CPU≈162核**→load 224/224饱和→**立即kill-9**→load 224→200→44✅·pretrain 143%未受干扰✅·📌 **incr_eval R2752** launched(setsid·CPU-limited: taskset -ac 0-15 + OMP=1·max 1600%<<8000%kill阈值): cline 3 real_new(sklearn-13496/15100/25102)+1 empty→EVAL·deepseek 2 real_new(django-14752/14765)→EVAL·pi 2 real_new(django-15629/15814)+2 empty→EVAL·codex 1 empty→merge·**sklearn-13496 RESOLVED✅**(FAIL_TO_PASS+PASS_TO_PASS全通过·cline 292→293/500=58.6% pending merge)·15100/25102 eval running in docker container(CPU-limited)·**taskset CPU限制验证有效**: eval pytest max 256%CPU(非162核)·load稳定44✅·📦 **SWE-bench Multimodal容器下载**(用户令11-18): **429/580 pulled=74.0%**(0 FAILED✅)·pull_all_images.sh alive(PID 3749136·NI=19)·顺序拉/nice19/ionice3·不抢.29 CPU✅·predict 4路alive(cline454/codex385/dsh259/pi397·cc+opencode+hermes COMPLETE 500/500)·0 429✅·**自检**: load44.55/224≈20%busy✅·无本线proc>8000%CPU✅·disk 27T avail✅·mem 1277G avail✅·incr_eval_all_R2752.py新增CPU限制(taskset+OMP env)·**全部运维令✅已交付**·WAITING=0·📦 TASK≈31.2KB MEMORY≈20.9KB(✅≤32KB)
> 📦 R2751 流水已归档 → daily-memories-harness/2026-11-19.md（§用户令11-19 08:2x交付·两份7way中文HTML报告REGEN主表置顶·TB-2.1主表opencode50.6/cline47.2/hermes46.1/pi39.3/cc33.7/codex28.1/deepseek12.4·SWE-bench Verified主表hermes88.8/opencode83.0/cc59.0/cline58.4/pi46.6/deepseek33.2/codex21.6·0script/0外链✅）。需要时再读。
> 🆕 **R2750 · 2026-11-19 08:4x — incr_eval轮·MM容器下载409/580=70.5%(0 FAILED)·incr_eval R2750 DONE: **cline +5 RESOLVED**(pytest-7982/8399·sklearn-10297/10908/13328全RESOLVED→292/500=58.4%)·**deepseek +4 RESOLVED**(django-14559/14580/14608/14672全RESOLVED→166/500=33.2%)·pi 1 real FAILED+1 empty merged·codex 1 empty merged·CPU_SPIRAL_SKIP guard re-added to incr_eval_all_R2750.py✅·7way报告REGEN(18718B·08:46)·predict 4路alive**·心跳第一行: SWE-bench Verified 7路 cumulative: **hermes444/500=88.8%**·**opencode415/500=83.0%**·**claude-code295/500=59.0%**·**cline292/500=58.4%**(+5)·**pi233/500=46.6%**·**deepseek166/500=33.2%**(+4)·**codex108/500=21.6%**·📦 **SWE-bench Multimodal容器下载**(用户令11-18): **409/580 pulled=70.5%**(0 FAILED✅)·pull_all_images.sh alive(PID 3749136·NI=19·etime~15.7h)·顺序拉/nice19/ionice3·不抠.29 CPU✅·predict 4/7 alive(raw predictions_glm53 total: cline-patched450·codex384·dsh257·pi393·cc+opencode+hermes COMPLETE 500/500)·0 429✅·**自检**: load52.09/224≈23%busy✅·无本线proc>8000%CPU·disk /nas_train 27T avail✅·mem 1278G avail✅·**全部运维令✅已交付**·WAITING=0·📦 TASK≈30.9KB MEMORY≈20.7KB(✅≤32KB)
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
> 📦 R2687 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器下载31/580·predict 5路alive·无incr_eval·自检clean·research日报已读）。需要时再读。
> 📦 R2685 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·5 instances 4 routes·+2 RESOLVED+0 FAILED+3 infra·7way报告REGEN·SWE-bench Multimodal容器下载17/580·scikit-learn CPU kill）。需要时再读。
> 📦 R2684 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·8 instances 5 routes·+5 RESOLVED+0 FAILED+3 infra·7way报告REGEN·SWE-bench Multimodal容器下载启动6/580·scikit-learn CPU kill）。需要时再读。
> 📦 R2683及更早(R2683~R2481, Gen7 pilot, R474-R477) 流水已归档 → daily-memories-harness/2026-11-14~18.md + 2026-10-24~28.md。需要时再读。

## 📊 进度快照

PHASE:        R2755 监控轮·MM容器448/580=77.2%·predict 4路alive·pretrain未受影响
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·10:3x ability桶拆两层✅·SWE-bench predict 7路resume LAUNCHED(R2665)·opencode 500/500 COMPLETE+eval 415/500=83.0%✅·hermes 500/500 COMPLETE+eval 444/500=88.8%✅·cc 500/500 COMPLETE+eval 295/500=59.0%✅·incr_eval R2680~R2752 DONE·merge_empties R2727~R2754 DONE·§用户令11-19 08:2x 两份7way报告REGEN主表置顶✅·**SWE-bench Multimodal容器下载进行中**(580 images·448/580 pulled=77.2%·0 FAILED)·CPU螺旋kill(09:18 sklearn 162核)+incr_eval R2752 CPU-limited(taskset 0-15+OMP=1)✅·I/O清理(kill 4 orphaned find / trees)✅
当前动作:     R2755: 自检clean(load41/224≈18%·无本线proc>8000%CPU·disk 27T·mem 1272G·pretrain GPU 68-100%未受影响)→监控轮(predict自R2754仅+2新 cline+1/pi+1 各路<2阈值→不跑incr_eval)·MM容器448/580=77.2%(PID 3749136 NI=19 etime~17.4h·当前拉img#449·速率~16/hr·余132 ETA~8h≈18:30)·predict 4路alive(cline456/codex387/pi400/dsh259)
下一步:       继续监控MM容器下载(448/580→580)·4路predict继续·累积real_new≥2/路时跑incr_eval(CPU-limited)→merge→刷新7way报告·Multimodal下载完成后(~18:30)准备MM评测
阻塞:         无
ERROR_COUNT:  0
 体积: TASK≈31.2KB / MEMORY≈21.6KB（✅≤32KB）
 SWE-bench Verified Pass%(cumulative resolved/500, after R2752 merge·R2755不变): hermes444=88.8%·opencode415=83.0%·cc295=59.0%·cline295=59.0%·pi233=46.6%·dsh168=33.6%·codex108=21.6%·(partial·predict still running for 4 routes: cline456/codex387/dsh259/pi400)
 真实 Pass% (layer-A/B 拆分后, 分母=89): cline 42/89=47.2%[真38/超8/环1|47.2~57.3%] · codex 25/89=28.1%[真59/超3/环1|28.1~32.6%] · opencode 45/89=50.6%[真31/超1/环8|50.6~60.7%] · cc 30/89=33.7%[真51/超0/环8|33.7~42.7%] · pi 35/89=39.3%[真48/超1/环5|39.3~46.1%] · hermes 41/89=46.1%[真27/超2/环19|46.1~69.7%] · deepseek 11/89=12.4%[真41/超0/环36|12.4~52.8%] · layer-B=93题(66确认infra+9 ability_lean+18 ambiguous)
  SWE-bench Multimodal容器下载(用户令11-18 最高优先): run/harness/swebench_mm/pull_all_images.sh·pull_progress.log·pull_state.txt·580 images total·448 pulled=77.2%(0 FAILED)·PID 3749136 NI=19 etime~17.4h·nice19/ionice=idle·不抢.29 CPU✅·ETA~8h(≈18:30)
  research日报11-19 harness建议: ①完成判据改三分法(fact/verdict/scope·PASS回执绑定最终源码摘要+两项具名检查+终止后可见检查仍PASS·只报标签正确率不算通过) ②20,480生成上限写进评测配置 ③entity-tool graph造题(必须跨≥2工具·执行日志三态判分) → 纳入未来计划(来自 research 日报 2026-11-19)
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