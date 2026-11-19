# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 0
> 🆕 **R2770 · 2026-11-19 16:28 — 监控轮·自检clean·🔴cline__deepseek quota-blocked(84·reset~18:09)·MM 2×3 224/2880·Verified 4路alive deltas<2→不跑incr_eval·cumulative不变·无REGEN**·**心跳第一行**: ✅自检clean(load37.86/224=17%✅·无CPU失控✅·无内存失控✅·pretrain未受影响✅)·🔴**cline__deepseek-v4-flash quota耗尽**(Token额度已用完·since16:04·reset~18:09:50·84实例quota-failed=NOT ability红线·3 has_patch pre-quota·route仍RUN低耗churn·rerun计划:18:09后删progress_2x3中stderr含"额度已用完"条目+re-predict该route)·opencode__deepseek(同key直连gateway·不经proxy)24/480=10 has_patch/14 failed=real text-only ability(76s实跑·非quota)·MM 2×3 224/2880(6路RUN·nice19/ionice3·0 literal-429·quota仅cline__deepseek): opencode×doubao50(39 has_patch=78%)·cline×doubao36(35 has_patch=97%)·cline×deepseek98(3 has_patch+84quota)·opencode×deepseek24·opencode×kimi8(8 has_patch)·cline×kimi8(6 has_patch)·kimi慢~11min/inst·doubao最快·Verified predict 4路alive(cline-patched482/codex400/pi422/dsh271·deltas自R2769均<2→不跑incr_eval)·cumulative不变(hermes444=88.8/opencode415=83.0/cline300=60.0/cc295=59.0/pi242=48.4/dsh175=35.0/codex109=21.8)·无REGEN·/dev/shm110G/1008G·/nas_train88%(27T free)·WAITING=0·📦 TASK=29.4KB(✅≤32KB) MEMORY≈25.9KB(✅≤32KB)
> 📦 R2769 流水已归档 → daily-memories-harness/2026-11-19.md（incr_eval R2765收尾 pi+7 RESOLVED pi242/500=48.4%·7way报告REGEN R2769·MM 2×3 146/2880·Verified 4路alive deltas<2·cumulative不变·自检clean）。需要时再读。
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
> 📦 R2687 流水已归档 → daily-memories-harness/2026-11-18.md（监控轮·MM容器下载31/580·predict 5路alive·无incr_eval·自检clean·research日报已读）。需要时再读。
> 📦 R2685 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·5 instances 4 routes·+2 RESOLVED+0 FAILED+3 infra·7way报告REGEN·SWE-bench Multimodal容器下载17/580·scikit-learn CPU kill）。需要时再读。
> 📦 R2684 流水已归档 → daily-memories-harness/2026-11-18.md（incr_eval轮·8 instances 5 routes·+5 RESOLVED+0 FAILED+3 infra·7way报告REGEN·SWE-bench Multimodal容器下载启动6/580·scikit-learn CPU kill）。需要时再读。
> 📦 R2683及更早(R2683~R2481, Gen7 pilot, R474-R477) 流水已归档 → daily-memories-harness/2026-11-14~18.md + 2026-10-24~28.md。需要时再读。

## 📊 进度快照

PHASE:        R2770 监控轮·自检clean·🔴cline__deepseek quota-blocked(84·reset~18:09·rerun计划)·MM 2×3 predict 6路RUN中(224/2880·doubao/kimi健康)·Verified predict 4路alive(deltas<2→不跑incr_eval)·cumulative不变·无REGEN
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·ability桶拆两层✅·SWE-bench predict 7路resume·opencode500/500+eval415/500=83.0%✅·hermes500/500+eval444/500=88.8%✅·cc500/500+eval295/500=59.0%✅·incr_eval R2680~R2766 DONE·§用户令11-19 08:2x 两份7way报告REGEN主表置顶✅·§用户令11-19 报告重写✅已交付(R2758)·pi incr_eval R2765 DONE(pi242/500=48.4%)·7way报告REGEN R2769✅·**MM容器下载COMPLETE(580/580·0FAILED·12:14:49)**✅·**2×3 predict全6路启动✅**(R2763 14:56·480题/路·nice19/ionice3)
当前动作:     R2770: 自检clean(load37.86/224=17%·无CPU/内存失控·pretrain未受影响)→🔴发现cline__deepseek-v4-flash quota耗尽(Token额度已用完·since16:04·reset~18:09:50·84实例quota-failed=NOT ability红线·route仍RUN低耗churn)→opencode__deepseek(同key直连gateway)=real text-only ability(76s实跑·非quota)确认→MM 2×3 224/2880统计→Verified 4路alive(cline-patched482/codex400/pi422/dsh271·deltas均<2→不跑incr_eval)→cumulative不变→无REGEN→写心跳+commit+push
下一步:       ① 继续监控2×3 predict(6路×480·`bash launch_mm_2x3_full.sh status`) ② 🔴18:09后rerun cline__deepseek quota-blocked实例(删progress_2x3中stderr_tail含"额度已用完"的条目→re-predict该route·resumes+reattempts) ③ predict完成后merge+eval(Docker·CPU限制taskset 0-15+OMP=1) ④ eval后出2×3中文HTML报告(落reports/·MM判分格式合法率vs正确率分列) ⑤ SWE-bench Verified predict继续+incr_eval(≥2阈值) ⑥ 每轮自检CPU/内存(运维令11-02/10-30)
阻塞:         无（cline__deepseek quota为transient·reset~18:09·已计划rerun·非硬阻塞）
ERROR_COUNT:  0
 体积: TASK=29.4KB（✅≤32KB） / MEMORY≈25.9KB（✅≤32KB）
 SWE-bench Verified Pass%(分母恒500·resolved/500·单数字无区间): hermes444/500=88.8%·opencode415/500=83.0%·cline300/500=60.0%·cc295/500=59.0%·pi242/500=48.4%·dsh175/500=35.0%·codex109/500=21.8%·(4路predict仍alive: cline-patched482/codex400/dsh271/pi422)
 真实 Pass% (layer-A/B 拆分后, 分母=89): cline 42/89=47.2% · codex 25/89=28.1% · opencode 45/89=50.6% · cc 30/89=33.7% · pi 35/89=39.3% · hermes 41/89=46.1% · deepseek 11/89=12.4% · layer-B=93题(66确认infra+9 ability_lean+18 ambiguous)
  SWE-bench Multimodal 2×3 predict(R2763 14:56启动·6路RUN·480题/路·nice19/ionice3·224/2880): opencode×doubao50/480(39 has_patch=78%·最快)·cline×doubao36/480(35 has_patch=97%)·cline×deepseek98/480(3 has_patch+🔴84 quota-blocked·Token额度已用完·reset~18:09·NOT ability红线)·opencode×deepseek24/480(10 has_patch/14 failed=real text-only ability·非quota)·opencode×kimi8/480(8 has_patch)·cline×kimi8/480(6 has_patch·kimi慢~11min/inst)·可恢复progress_2x3逐题落盘·不抢.29 CPU✅
  research日报11-19 harness建议: ①完成判据改三分法(fact/verdict/scope·PASS回执绑定最终源码摘要+两项具名检查+终止后可见检查仍PASS·只报标签正确率不算通过) ②MM判分格式合法率vs任务正确率分两列·MM评测分四组(VQA/captioning/纯文本/混合)缺组不参与排名 ③20,480生成上限写进评测配置 ④两档prompting(answer-only/CoT)分任务族报分 → 纳入未来计划(来自 research 日报 2026-11-19)
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