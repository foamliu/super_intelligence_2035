# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **R2843 · 2026-11-21 13:59 — 16:3x解冻令·监控轮#35·Step2.3 MM 2×3 predict 2880/2880·has_patch1427(+11)·error1150(↓11收敛)·判据全绿**·**心跳第一行**: ✅自检clean✅ ①guard PID931671存活(~22.7h·ppid1·guard log仅启动行=零越界~22.7h)✅ ②mem avail1371G≥512G✅ ③load30.32/224≤120✅ ④pretrain step~7.14s≤7.4s✅(data R106·iter~271.4k) ⑤无失控进程✅(无>8000%) ⑥docker ps空✅. **Step1护栏LIVE**(/proc ulimit200GiB=214748364800B 5procs全核HARD VERIFIED✅·OMP8/MKL8/OPENBLAS8✅·nice19✅·guard零越界~22.7h✅). **Step2.1 COMPLETE·Step2.2 backlog=0✅**. **Step2.3 MM 6路全2880/2880**: has_patch1427(↑+11)·error1150(↓−11收敛)·blocked188·empty_patch61·failed32·infra22·oc_doubao DONE(448). **🔴本轮根因突破·error全量扫描**: 1150error=**1141 Errno11(EAGAIN瞬态)**+**6 Errno7(E2BIG永久·prompt>128KB MAX_ARG_STRLEN)**+3other. **ZERO EAGAIN in当前run logs**(5路log全grep=0)→1141 EAGAIN全来自pre-freeze前次run(6路并发资源争用)·当前post-freeze retry pass成功率87-97%(cline_dsh 84/94=89%·cline_doubao 244/251=97%·cline_kimi 74/85=87%·oc_dsh 96/103=93%·oc_kimi 82/86=95%)→has_patch将在pass完成时跳膳~2100+(ETA~10-20h·5路各25-97%进度). **无需改码**(retry机制正确·EAGAIN已自愈)·processes退出后re-launch清剩余. 无新eval→7way不REGEN. 📦 TASK32.2KB MEMORY~21KB
> 📦 R2842 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#34·Step2.3 MM 2880/2880·has_patch1416·error1161↓收敛·判据全绿·guard零越界~21.9h·pretrain7.17s·mem1373G·load31.52·/proc ulimit200GiB 5procs HARD VERIFIED·error sample拆解=Errno7永久+Errno11瞬态·WAITING=1）。需要时再读。
> 📦 R2841 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#33·Step2.3 MM 2880/2880·has_patch1399(+9)·error1180(↓9收敛)·判据全绿·guard PID931671零越界~21.7h·pretrain7.21s·mem1375G·load26.51·/proc ulimit200GiB 5procs HARD VERIFIED·WAITING=1）。需要时再读。
> 📦 R2840 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#32·Step2.3 MM 2880/2880·has_patch1390(+3)·error1189(↓4收敛)·判据全绿·guard PID931671零越界~21.3h·pretrain7.14s·mem1377G·load29.66·/proc ulimit200GiB 5procs HARD VERIFIED·WAITING=1）。需要时再读。
> 📦 R2839 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#31·Step2.3 MM 2880/2880·has_patch1387(+13)·error1193(↓14收敛)·判据全绿·guard PID931671零越界~20.8h·pretrain7.13s·mem1377G·load29.95·/proc ulimit200GiB HARD VERIFIED·WAITING=1）。需要时再读。
> 📦 R2838 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x 解冻令·监控轮#30·Step2.3 MM 2880/2880·has_patch1374(+34)·error1207(↓35收敛)·判据全绿·guard PID931671零越界~20.4h·pretrain7.12s·mem1374G·load30.39·/proc ulimit200GiB HARD VERIFIED·WAITING=1）。需要时再读。
> 📦 R2837 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#29·Step2.3 MM 2880/2880·has_patch1340(+20)·error1242(↓22收敛)·判据全绿·guard PID931671零越界~19.8h·pretrain7.15s·mem1378G·load30.54·/proc ulimit200GiB HARD VERIFIED·WAITING=1）。需要时再读。
> 📦 R2836 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#28·Step2.3 MM 2880/2880·has_patch1320(+37)·error1264·判据全绿·guard PID931671零越界·pretrain7.16s·mem1384G·load31.38·WAITING=1）。需要时再读。
> 📦 R2835 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#27·Step2.3 MM 2880/2880·has_patch1283(+18)·error1304·判据全绿·guard PID931671零越界·pretrain7.37s·mem1385G·load28.07·WAITING=1）。需要时再读。
> 📦 R2834 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#26·Step2.3 MM 2880/2880·has_patch1265(+19)·error1323·判据全绿·guard PID931671零越界·pretrain7.16s·mem1388G·load29.04·WAITING=1）。需要时再读。
> 📦 R2833 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#25·Step2.3 MM 2880/2880·has_patch1246(+20)·判据全绿·guard PID931671零越界·pretrain7.11s·mem1389G·load30.06·WAITING=1）。需要时再读。
> 📦 R2832 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#24·Step2.3 MM 2880/2880·has_patch1226(+21)·判据全绿·guard PID931671零越界·pretrain7.11s·mem1392G·load30.82·WAITING=1）。需要时再读。
> 📦 R2831 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#23·Step2.3 MM 2880/2880·has_patch1205·判据全绿·guard PID931671零越界·pretrain7.08s·mem1392G·load29.99·WAITING=1）。需要时再读。
> 📦 R2830 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#22·Step2.3 MM 2880/2880 attempted·has_patch1180·判据全绿·guard PID931671零越界·pretrain7.12s·mem1393G·load28.70·WAITING=1）。需要时再读。
> 📦 R2829 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#21·Step2.3 MM 1251/2880(+28)·has_patch1158(92.6%)·判据全绿·guard PID931671零越界·pretrain7.08s·mem1393G·load28.33·WAITING=1）。需要时再读。
> 📦 R2828 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#20·Step2.3 MM 1223/2880(+22)·has_patch1130(92.4%)·判据全绿·guard PID931671零越界·pretrain7.11s·mem1397G·load28.47·WAITING=1）。需要时再读。
> 📦 R2827 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#19·Step2.3 MM 1201/2880(+19)·has_patch1108(92.3%)·判据全绿·guard PID931671零越界·pretrain7.11s·mem1396G·load29.48·WAITING=1）。需要时再读。
> 📦 R2826 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#18·Step2.3 MM 1182/2880(+22)·has_patch1089(92.1%)·判据全绿·guard PID931671零越界·pretrain7.08s·mem1400G·load29.32·WAITING=1）。需要时再读。
> 📦 R2825 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#17·Step2.3 MM 1160/2880(+44)·has_patch1067(92.0%)·判据全绿·guard PID931671零越界·pretrain7.10s·mem1402G·load26.56·WAITING=1）。需要时再读。
> 📦 R2824 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#16·Step2.3 MM 1116/2880(+9)·has_patch1035(92.7%)·error仅11(1.0%)·判据全绿·guard PID931671零越界·pretrain7.04s·mem1403G·load30.42·WAITING=1）。需要时再读。
> 📦 R2823 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#15·Step2.3 MM 1107/2880(+39)·has_patch1018·判据全绿·guard PID931671零越界·pretrain7.02s·mem1403G·load29.86·WAITING=1）。需要时再读。
> 📦 R2822 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#14·Step2.3 MM 1068/2880(+8)·has_patch994·判据全绿·guard PID931671零越界·pretrain7.02s·mem1408G·load29.84·WAITING=1）。需要时再读。
> 📦 R2821 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#13·Step2.3 MM 1060/2880(+17)·has_patch975·判据全绿·guard PID931671零越界·pretrain7.03s·mem1406G·load29.29·WAITING=1）。需要时再读。
> 📦 R2820 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#12·Step2.3 MM 1043/2880(+25)·has_patch958·判据全绿·guard PID931671零越界·pretrain7.02s·mem1410G·load30.72·WAITING=1）。需要时再读。
> 📦 R2819 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#11·Step2.3 MM 1018/2880(+23)·has_patch935·判据全绿·guard PID931671零越界·pretrain6.98s·mem1410G·load31.16·WAITING=1）。需要时再读。
> 📦 R2818 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#10·Step2.3 MM 995/2880(+17)·has_patch912·判据全绿·guard PID931671零越界·pretrain7.06s·mem1413G·load26.16·WAITING=1）。需要时再读。
> 📦 R2816 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#8·Step2.3 MM 940/2880(+25)·has_patch857·判据全绿·guard PID931671零越界·pretrain7.05s·mem1421G·load26.86·WAITING=1）。需要时再读。
> 📦 R2815 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#7·Step2.3 MM 915/2880(+33)·has_patch832·判据全绿·guard PID931671零越界·pretrain7.02s·mem1423G·load26.57·WAITING=1）。需要时再读。
> 📦 R2814 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#6·Step2.3 MM 882/2880(+31)·has_patch800·判据全绿·guard PID931671零越界·pretrain7.01s·mem1429G·load26.82·WAITING=1）。需要时再读。
> 📦 R2813 流水已归档 → daily-memories-harness/2026-11-21.md（16:3x解冻令·监控轮#5·Step2.3 MM 851/2880(+104)·has_patch772·判据全绿·guard PID931671零越界·pretrain7.03s·mem1422G·load29.12·WAITING=1）。需要时再读。
> 📦 R2812 流水已归档 → daily-memories-harness/2026-11-20.md（16:3x解冻令·监控轮#4·Step2.3 MM 747/2880(+24)·判据全绿·guard PID931671零越界·pretrain7.02s·mem1431G·load28.05·WAITING=1）。需要时再读。
> 📦 R2811 流水已归档 → daily-memories-harness/2026-11-20.md（16:3x解冻令·监控轮#3·Step1护栏LIVE·Step2.3 MM 723/2880(+19)·判据全绿·guard PID931671零越界·pretrain7.02s·mem1435G·load27.23·WAITING=1）。需要时再读。
> 📦 R2810 流水已归档 → daily-memories-harness/2026-11-20.md（16:3x解冻令·监控轮#2·Step1护栏LIVE·Step2.3 MM 704/2880(+18)·判据全绿·guard PID931671零越界·pretrain7.08s·mem1440G·load25.29·WAITING=1）。需要时再读。
> 📦 R2809 流水已归档 → daily-memories-harness/2026-11-20.md（16:3x解冻令·监控轮·Step1护栏HARD VERIFIED·Step2.3 MM 686/2880·判据全绿·guard PID931671零越界·pretrain7.05s·WAITING=1）。需要时再读。
> 📦 R2808 流水已归档 → daily-memories-harness/2026-11-20.md（16:3x解冻令·Step2.1/2.2 COMPLETE→Step2.3 MM 2×3 predict STARTED·6路全RUN·7way报告REGEN R2808·cline303/pi247/dsh195/codex115/hermes444/opencode415/cc295·guard PID931671·load24.96·mem1452G·pretrain7.05s·WAITING=1）。需要时再读。
> 📦 R2807 流水已归档 → daily-memories-harness/2026-11-20.md（16:3x解冻令·Step2.1 codex→deepseek调度·Step2.2 R2800 5-matplotlib COMPLETE·deepseek195/500=39.0%·7way报告REGEN·guard PID931671·load24.5·mem1476G·pretrain7.21s·WAITING=1）。需要时再读。
> 📦 R2806 流水已归档 → daily-memories-harness/2026-11-20.md（16:3x解冻令·Step1硬护栏全落地验证✅·docker eval mem128g/cpu16 monkey-patch HARD VERIFIED·predict_guarded.sh ulimit200GiB·guard PID931671·Step2.1 codex+pi RUNNING·Step2.2 deepseek incr_eval matplotlib-26113 RUNNING·load28·mem1483G·pretrain7.28s·WAITING=1）。需要时再读。
> 📦 R2804 流水已归档 → daily-memories-harness/2026-11-20.md（Phase 0 监控轮#3·git pull up to date·guard PID931671存活·loop PID45764节流LIVE·自检clean·无eval容器·无predict/eval进程·pretrain 7.28s·WAITING=1）。需要时再读。
> 📦 R2803 流水已归档 → daily-memories-harness/2026-11-20.md（Phase 0 监控轮#2·loop 已重启 PID45764→CPU 节流 LIVE·自检clean·无 eval 容器·无 predict/eval 进程·pretrain 7.1s·WAITING=1）。需要时再读。
> 📦 R2802 流水已归档 → daily-memories-harness/2026-11-20.md（Phase 0 首轮·护栏守护启动PID931671·loop CPU 节流写入+bash -n·自检clean·无 eval 容器·杀停在途 opencode×deepseek MM predict PID962346·pretrain step7.1s·WAITING=1·待 loop 重启生效）。需要时再读。
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
> 📦 R2782及更早(R2782~R2683, Gen7 pilot, R474-R477) 流水已归档 → daily-memories-harness/2026-11-18~19.md + 2026-10-24~28.md。需要时再读。

## 📊 进度快照

PHASE:        16:3x 解冻令·Step 1✅·Step 2.1 predict COMPLETE(pi500/dsh332/codex442quota)·Step 2.2 incr_eval backlog=0✅·Step 2.3 MM 2×3 predict 6路全2880/2880(5路仍RUN retry pass·oc_doubao DONE·has_patch1427↑·error1150↓收敛·根因突破:1141 Errno11瞬态全自pre-freeze·ZERO EAGAIN in当前run·retry成功率87-97%)
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·SWE-bench Verified predict 7路·§11-19报告重写✅(R2758)·MM容器下载COMPLETE(580/580)✅·Phase 0 冻结验收通过✅·Step 1 硬护栏全落地✅(swebench_guarded_eval.py docker mem128g/cpu16 monkey-patch HARD VERIFIED✅·predict_guarded.sh ulimit200GiB+OMP8+nice19/ionice3✅·guard PID931671✅)·**Step 2.1 Verified predict COMPLETE**: pi500/500·dsh332/500·codex442/500(quota)·**Step 2.2 incr_eval backlog=0**(deepseek+pi全评测)·**7way报告REGEN R2808**(cline303/pi247/dsh195/codex115)·**Step 2.3 MM 2×3 predict 6路全2880/2880 attempted**(has_patch1320·processes仍RUN retry error/blocked)·TASK归档14:5x+08:2x已搬ARCHIVE✅
当前动作:     R2843: 监控轮#35·MM 2×3 predict 6路全2880/2880·has_patch1427(+11)·error1150(↓11收敛)·oc_doubao DONE(448)·5路仍RUN retry pass·判据全绿(load30.32/mem1371G/pretrain~7.14s data R106·guard PID931671零越界~22.7h·/proc HARD VERIFIED ulimit200GiB 5procs全核/OMP8/nice19)·无新eval→7way不REGEN·🔴根因突破: error全量扫描=1141 Errno11(EAGAIN瞬态·ZERO in当前run logs·全自pre-freeze·retry成功87-97%)+6 Errno7(E2BIG永久·prompt>128KB MAX_ARG_STRLEN)·has_patch将跳膳~2100+(ETA~10-20h)·无需改码(EAGAIN已自愈)
下一步:       ①监控MM 2×3 predict 5路 retry pass(has_patch爬升膳~2100+·ETA~10-20h·pretrain≤7.4s/mem≥512G/load≤120·越界降载/暂停)→②processes退出后re-launch清剩余(仅Errno7 6项永久·其余EAGAIN已自愈)→③MM eval(全部has_patch走guarded容器mem128g/cpu16·串行)→④codex quota恢复后rerun 256 quota_blocked+predict 442→500→⑤deepseek predict 4 no-patch refill(低价值可选)
阻塞:         无
ERROR_COUNT:  0
 体积: TASK32.2KB（✅<40KB硬限·贴32KB软限·14:5x/08:2x已归档）/ MEMORY20.4KB（✅≤32KB·R2840及更早指针已折叠）
 SWE-bench Verified Pass%(分母恒500·incr_eval backlog=0): hermes444/500=88.8%·opencode415/500=83.0%·cline303/500=60.6%·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%·（MM 2×3 predict 6路全2880/2880 attempted·processes retry中）
 真实 Pass% (layer-A/B, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%
   SWE-bench Multimodal 2×3 predict(全2880/2880·R2808重启·480题/路·5路processes仍RUN retry·oc_doubao DONE): cline×deepseek480/125·cline×doubao480/423·cline×kimi480/113·opencode×deepseek480/166·opencode×doubao480/448(DONE)·opencode×kimi480/124=2880/2880·has_patch1427(↑from1416)·5路processes仍RUN(retry error/blocked·nice19/ionice3/ulimit200GiB·/proc HARD VERIFIED 5procs全核)·error1150(↓from1161·rc=None·retry-pending·非永久失败·非能力·↓from1189收敛中)·blocked190(API rate-limit·非能力)·infra20·failed32·empty_patch59
  research日报11-19 harness建议: ①完成判据三分法 ②MM判分格式合法率vs正确率分两列+四组分组 ③20480生成上限写进评测配置 ④两档prompting分任务族报分 → 解冻后纳入(来自 research 日报 2026-11-19)
  research日报11-21 harness建议: ①记忆模块按「记录条数」+「检索上下文token」双预算报告(ref MemFolder 50%记录/99%保留) ②SFT数据skill前缀消融(判据六设置均分) ③评测脚本报单请求延迟分解(prefill/decode/工具等待) → 报告格式改进·待MM eval出结果后纳入(来自 research 日报 2026-11-21)
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