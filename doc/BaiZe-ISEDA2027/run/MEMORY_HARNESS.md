# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **R2994 · 2026-11-24 11:17 — 11-24令·cline PREDICT并行化收尾监控轮·LIVE predict仍RUN·判据全绿**·**心跳第一行**: ✅自检clean✅ ①guard PID931671存活~92h✅零越界 ②mem avail1177G≥512G✅ ③load28.9≤120✅ ④pretrain step~7.1s≤7.4s✅ ⑤无失控进程✅ ⑥docker已prune(6.47GB回收·0活容器). **LIVE predict PID1891311**(--workers 8·10:46起): 34 nonempty/96·62空patch在补·**全部62返回空**(白天429·8→4→2退回·11:14爬回3)·~11题剩余(900s超时中)·**未结束**(log无merged N/96). **incr eval(R2993 PID3639172)已FINISH**→7way报告REGEN@11:16·**cline=328/500=65.6%**. 白天predict回收0/62→真回收推迟今晚21:00窗口. **下一步**: poll predict→结束后`incremental_eval_merge.py --route cline-patched --regen`. **并行MM 2×3**: 2路kimi仍RUN. 📦 TASK~34KB MEMORY~31KB
> 📦 R2993 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·park轮·incr eval reconcile RUNNING→FINISH·cline328/500=65.6%·判据全绿·watcher re-armed·MM 2路kimi RUN）。需要时再读。
> 📦 R2991 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·09:00窗口结束过渡·手动kill orch+启动incr eval+re-arm watcher·判据全绿·cline325/500=65.0%·MM has_patch2545）。需要时再读。
> 📦 R2990 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#21·08:40监控+清理·cline325/500=65.0%·8 IDs待09:00 stop·判据全绿·orchestrator 34/96 nonempty·MM has_patch2545）。需要时再读。
> 📦 R2989 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#20·incr eval+merge@08:02→cline325/500=65.0%·判据全绿·orchestrator 96/96 predicted·431nonempty·MM has_patch2545）。需要时再读。
> 📦 R2988 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#19·incr eval+merge@07:27→cline324/500=64.8%·判据全绿·orchestrator 30/96·MM has_patch2545）。需要时再读。
> 📦 R2987 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#18·incr eval+merge@05:54→cline321/500=64.2%·判据全绿·orchestrator 22/95·MM has_patch2545）。需要时再读。
> 📦 R2985 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#16·incr eval+merge@04:52→cline316/500=63.2%·判据全绿·orchestrator 18/95·MM has_patch2532）。需要时再读。
> 📦 R2984 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#15·incr eval+merge@04:22→cline316/500=63.2%·判据全绿·orchestrator 17/95·MM has_patch2527）。需要时再读。
> 📦 R2983 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#14·incr eval+merge@03:50→cline315/500=63.0%·判据全绿·orchestrator 15/95·MM has_patch2524）。需要时再读。
> 📦 R2982 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#13·incr eval+merge@03:17→cline314/500=62.8%·判据全绿·orchestrator 14/95·MM has_patch2517）。需要时再读。
> 📦 R2981 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#12·incr eval+merge@02:47→cline313/500=62.6%·判据全绿·orchestrator 12/95·MM has_patch2511）。需要时再读。
> 📦 R2980 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#11·incr eval+merge@02:19→cline311/500=62.2%·判据全绿·orchestrator 10/95·MM has_patch2508）。需要时再读。
> 📦 R2979 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#10·稳态监控·无新增nonempty·判据全绿·cline=310/500=62.0%·orchestrator 9/95·MM has_patch2486）。需要时再读。
> 📦 R2978 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#9·稳态监控·无新增nonempty·判据全绿·cline=310/500=62.0%·orchestrator position12/95·MM has_patch2486）。需要时再读。
> 📦 R2976 流水已归档 → daily-memories-harness/2026-11-24.md（11-23令·infra重跑LIVE轮#7·★增量eval+merge交付·cline Pass%=310/500=62.0%(+7 infra回收✅)·incremental_eval_merge.py新建·EVAL_LOG_ROOT path bug修复·stop script升级·orchestrator PID4191374 9/95 nonempty·判据全绿）。需要时再读。
> 📦 R2975 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·infra重跑LIVE轮#6·stop-script bug修复+orchestrator重启PID4191374@23:49·09:00 stop ARMED✅·首轮7/95(6非空+1空)·判据全绿·MM has_patch2486）。需要时再读。

> 📦 R2969 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#160·Step1交付物在位·判据全绿·Step2重跑ARMED(watcher alive→21:00 fire)·MM has_patch2465(+2)·2路kimi仍RUN·guard零越界~77.4h·pretrain step7.26s）。需要时再读。
> 📦 R2968 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#159·Step1交付物在位·判据全绿·Step2重跑ARMED全链路复验✅·MM has_patch2463(+6)·2路kimi仍RUN·guard零越界~77h·pretrain step7.24s）。需要时再读。
> 📦 R2967 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#158·Step1交付物在位·判据全绿·Step2重跑ARMED(launch脚本修复+21:00 watcher已起)·MM has_patch2457(+1)·2路仍RUN·guard零越界~76.5h·pretrain step7.13s）。需要时再读。
> 📦 R2966 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#157·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2456(+3)·2路仍RUN·guard零越界~76.2h·pretrain step7.12s）。需要时再读。
> 📦 R2964 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#155·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2452(+7)·4路DONE·guard零越界~75.4h·pretrain step7.19s·2路仍RUN）。需要时再读。
> 📦 R2963 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#154·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2445(+6)·4路DONE·guard零越界~74.8h·pretrain step7.16s·2路仍RUN）。需要时再读。
> 📦 R2962 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#153·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2439(+2)·4路DONE·guard零越界~74.4h·pretrain step7.12s·2路仍RUN）。需要时再读。
> 📦 R2961 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#152·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2437持平·4路DONE·guard零越界~74.0h·pretrain step7.11s·2路仍RUN）。需要时再读。
> 📦 R2960 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#151·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2437(+2)·4路DONE·guard零越界~73.5h·pretrain step7.26s·2路仍RUN）。需要时再读。
> 📦 R2959 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#150·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2435·guard零越界~73.2h·pretrain step~7.10s·2路仍RUN）。需要时再读。
> 📦 R2958 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#149·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2432(+2)·cline×dsh DONE@15:47·guard零越界~73.6h·pretrain step7.06s·2路仍RUN）。需要时再读。
> 📦 R2957 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#148·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2430(+1)·guard零越界~72.4h·pretrain step7025ms·3路仍RUN）。需要时再读。
> 📦 R2956 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#147·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2429(+1)·guard零越界~72h·pretrain step~7.02s·3路仍RUN）。需要时再读。
> 📦 R2955 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#146·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2428(+3)·guard零越界~71.6h·pretrain step~7.46s baseline漂移无eval致·3路仍RUN）。需要时再读。
> 📦 R2954 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#145·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2425(+3)·guard零越界~71.2h·pretrain step~7.39s·3路仍RUN）。需要时再读。
> 📦 R2953 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#144·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2422(+5)·guard零越界~70.9h·pretrain step~7.42s微超0.02s非eval致·3路仍RUN）。需要时再读。
> 📦 R2952 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#143·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2417(+4)·guard零越界~70.5h·pretrain step7.33s·3路仍RUN）。需要时再读。
> 📦 R2951 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#142·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2413持平·guard零越界~70.2h·pretrain step7.28s·3路仍RUN）。需要时再读。
> 📦 R2950 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#141·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2413(+11)·guard零越界~69.8h·pretrain step7.21s·3路仍RUN）。需要时再读。
> 📦 R2948 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#139·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2393·guard零越界~68.2h·pretrain step7.42s非eval致·3路仍RUN）。需要时再读。
> 📦 R2947 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#138·Step1交付物在位·判据全绿·Step2重跑PARKED等21:00·MM has_patch2390·guard零越界~67.8h·pretrain step7.39s非eval致·3路仍RUN）。需要时再读。
> 📦 R2945 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令·park/监控轮#136·Step1交付物复核全在·判据全绿·Step2重跑PARKED等21:00·MM has_patch2368·guard零越界~66.9h·pretrain step7.41s非eval致·3路仍RUN）。需要时再读。
> 📦 R2944 流水已归档 → daily-memories-harness/2026-11-23.md（11-23令Step1全量7路infra排查COMPLETE·报告交付·infra446+pending554=1000题PARKED等21:00·判据全绿·3路MM仍RUN）。需要时再读。
> 📦 R2943 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#135·has_patch2368(+4)·判据全绿·guard零越界~65.6h·pretrain step avg7337ms=7.34s≤7.4s✅·3路仍RUN·WAITING=1）。需要时再读。
> 📦 R2941 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#133·has_patch2360(+3)·判据全绿·guard零越界~65.3h·pretrain step avg7208ms(iter292850·≤7.4s✅)·3路仍RUN·WAITING=1）。需要时再读。
> 📦 R2940 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#132·has_patch2357(+6)·判据全绿·guard零越界~64.8h·pretrain step avg7199ms(iter292610·≤7.4s✅)·3路仍RUN·WAITING=1）。需要时再读。
> 📦 R2939 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#131·has_patch2351(+17)·判据全绿·guard零越界~64.5h·pretrain step avg7170ms(iter292480·≤7.4s✅)·3路仍RUN·WAITING=1）。需要时再读。
> 📦 R2938 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#130·has_patch2334(+6)·判据全绿·guard零越界~63.7h·pretrain step-time-during-eval=7159ms(iter292100·≤7.4s✅)·3路仍RUN·WAITING=1）。需要时再读。
> 📦 R2937 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#129·has_patch2328(+7)·判据全绿·guard零越界~63.0h·pretrain step avg7238ms=7.24s(iter291780)≤7.4s✅·3路仍RUN·oc×dsh新DONE(453)·WAITING=1）。需要时再读。
> 📦 R2936 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#128·has_patch2321(+3)·判据全绿·guard零越界~62.6h·pretrain step avg7206ms=7.21s(iter291530)≤7.4s✅·4路仍RUN·WAITING=1）。需要时再读。
> 📦 R2935 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#127·has_patch2318(+5)·判据全绿·guard零越界~62.3h·pretrain step avg7158ms=7.16s(iter291340)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2934 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#126·has_patch2313(+11)·判据全绿·guard零越界~61.8h·pretrain step avg7242ms=7.24s(iter291190)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2933 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#125·has_patch2302(+9)·判据全绿·guard零越界~61.4h·pretrain step avg7095ms=7.10s(iter289530)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2932 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#124·has_patch2293(+3)·判据全绿·guard零越界~60.97h·pretrain step avg7339ms=7.34s(iter290800)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2931 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#123·has_patch2290(+7)·判据全绿·guard零越界~60.7h·pretrain step avg7346ms=7.35s(iter290590)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2930 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#122·has_patch2283(+7)·判据全绿·guard零越界~60.3h·pretrain step avg7327ms=7.33s(iter290360)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2928 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#120·has_patch2270(+3)·判据全绿·guard零越界~59.6h·pretrain step avg7136ms=7.14s(iter289910)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2927 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#119·has_patch2267(+5)·判据全绿·guard零越界~58.9h·pretrain step avg7122ms=7.12s(iter289810)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2926 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#118·has_patch2262(+25)·判据全绿·guard零越界~58.7h·pretrain step avg7126ms=7.10s(iter289580)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2925 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#117·has_patch2237·判据全绿·guard零越界~58.3h·pretrain step avg7101ms=7.10s(iter289430)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2924 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#116·has_patch2247(+12)·判据全绿·guard零越界~57.9h·pretrain step avg7270ms=7.27s(iter289160)≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2922 流水已归档 → daily-memories-harness/2026-11-23.md（16:3x解冻令·监控轮#114·has_patch2228(+12)·判据全绿·guard零越界~57h·pretrain step avg7298ms=7.30s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2921 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#113·has_patch2216(+8)·判据全绿·guard零越界~56.6h·pretrain step avg7185ms=7.18s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2919 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#111·has_patch2198(+3)·判据全绿·guard零越界~56h·pretrain step avg7167ms=7.17s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2918 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#110·has_patch2195(+10)·判据全绿·guard零越界~55.2h·pretrain step avg7363ms=7.36s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2917 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#109·has_patch2185(+13)·判据全绿·guard零越界~54.76h·pretrain step avg7320ms=7.32s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2916 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#108·has_patch2172(+11)·判据全绿·guard零越界~54.3h·pretrain step avg7300ms=7.30s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2915 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#107·has_patch2161(+3)·判据全绿·guard零越界~53.8h·pretrain step avg7283ms=7.28s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2914 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#106·has_patch2158(+8)·判据全绿·guard零越界~53.4h·pretrain step avg7270ms=7.27s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2913 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#105·has_patch2150(+9)·判据全绿·guard零越界~52.7h·pretrain step avg7333ms=7.33s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2912 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#104·has_patch2141(+8)·判据全绿·guard零越界~52.5h·pretrain step avg7130ms=7.13s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2911 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#103·has_patch2133(+8)·判据全绿·guard零越界~52.05h·pretrain step avg7196.5ms=7.196s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2910 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#102·has_patch2125(+14)·判据全绿·guard零越界~51.6h·pretrain step7.09s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2909 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#101·has_patch2111(+6)·判据全绿·guard零越界~51.2h·pretrain step7.33s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2908 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#100·has_patch2105(+13)·判据全绿·guard零越界~50.8h·pretrain step7.31s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2907 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#99·has_patch2092(+4)·判据全绿·guard零越界~50.3h·pretrain step7.30s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2906 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#98·has_patch2088(+10)·判据全绿·guard零越界~50h·pretrain step7.24s≤7.4s✅·WAITING=1）。需要时再读。
> 📦 R2905 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#97·Step2.3 MM has_patch2078(+6)·4路仍RUN·判据全绿·guard零越界~49.6h·pretrain step avg7298ms=7.30s(iter285070@16:45·n=10·1瞬态7443ms>7.4s NOT persistent)·mem1273G·load26.10·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2903 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#95·Step2.3 MM has_patch2065(+13)·4路仍RUN·判据全绿·guard零越界~48.8h·pretrain step avg7335ms=7.34s(#2999@16:03·DURING eval n=20·4瞬态>7.4s NOT persistent)·mem1274G·load28.86·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2902 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#94·Step2.3 MM has_patch2052(+4)·4路仍RUN·判据全绿·guard零越界~48.4h·pretrain step avg7239ms=7.24s(#2998@15:35·n=15·1瞬态>7.4s NOT persistent)·mem1264G·load29.07·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2901 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#93·Step2.3 MM has_patch2048(+10)·4路仍RUN·判据全绿·guard零越界~48.05h·pretrain step avg7238ms=7.24s·mem1264G·load29.76·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2900 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#92·Step2.3 MM has_patch2038(+6)·4路仍RUN·判据全绿·guard零越界~47.6h·pretrain step avg7230-7342ms=7.23-7.34s(全≤7.4s✅)·mem1267G·load27.32·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2899 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#91·Step2.3 MM has_patch2032(+7)·4路仍RUN·判据全绿·guard零越界~47.2h·pretrain step avg7296ms=7.30s(n=5:7379/7357/7149/7479/7116ms·max7479ms·1/5瞬态>7.4s非持续·4/5≤7.4s✅)·mem1267G·load26.19·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2898 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#90·Step2.3 MM has_patch2025(+14)·4路仍RUN·判据全绿·guard零越界~46.8h·pretrain avg7250ms=7.25s(pretrain daily 13:57:avg7262ms/max7369ms全≤7.4s)·mem1268G·load28.52·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2897 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#89·Step2.3 MM has_patch2011(+8)·4路仍RUN·判据全绿·guard零越界~46.3h·pretrain avg7200ms=7.2s(last12全≤7.4s)·mem1269G·load24.60·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2896 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#88·Step2.3 MM has_patch2003(+13)·4路仍RUN·判据全绿·guard零越界~45.9h·pretrain avg7228ms=7.23s(last10:7071-7563ms·1瞬时>7.4s@7563ms NOT persistent)·mem1271G·load24.38·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2895 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#87·Step2.3 MM has_patch1990(+5)·4路仍RUN·判据全绿·guard零越界~45.2h·pretrain avg7280ms=7.28s(last10:7087-7415ms·1瞬时>7.4s@iter282910 NOT persistent)·mem1277G·load29.39·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。
> 📦 R2894 流水已归档 → daily-memories-harness/2026-11-22.md（16:3x解冻令·监控轮#86·Step2.3 MM has_patch1985(+7)·4路仍RUN·判据全绿·guard零越界~44.7h·pretrain avg7342ms=7.34s(last10:7218-7482ms·2瞬时>7.4s@11:47-48 NOT persistent)·mem1266G·load47.83·/proc ulimit200GiB 4/4 predict workers HARD VERIFIED·cline×doubao DONE(466)·oc×doubao DONE(448)·WAITING=1）。需要时再读。

## 📊 进度快照

PHASE:        11-23用户令(infra排查+夜间重跑)·Step1全量7路infra排查COMPLETE✅·Step2重跑PARKED(09:00窗口结束·orchestrator killed·incr eval PID3117624 running --all --regen: cline✅codex✅dsh✅cc✅ pi41/42→hermes→oc→auto-REGEN·watcher PID3117637 armed for 21:00)·cline-patched rerun 34/96 nonempty·cline434/500 nonempty·cline328/500=65.6%·并行:16:3x解冻令·Step2.3 MM 2×3 predict 6路全480/480(has_patch2545·2路kimi retry仍RUN)
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·SWE-bench Verified predict 7路·§11-19报告重写✅(R2758)·MM容器下载COMPLETE(580/580)✅·Phase 0 冻结验收通过✅·Step 1 硬护栏全落地✅(swebench_guarded_eval.py docker mem128g/cpu16 monkey-patch HARD VERIFIED✅·predict_guarded.sh ulimit200GiB+OMP8+nice19/ionice3✅·guard PID931671✅)·**Step 2.1 Verified predict COMPLETE**: pi500/500·dsh332/500·codex442/500(quota)·**Step 2.2 incr_eval backlog=0**(deepseek+pi全评测)·**7way报告REGEN R2808**(cline303/pi247/dsh195/codex115)·**Step 2.3 MM 2×3 predict 6路全2880/2880 attempted**(has_patch2432·4路DONE: cline×dsh393/cline×doubao466/oc×dsh453/oc×doubao448·2路processes仍RUN: cline×kimi/oc×kimi)·**Step1全量7路infra排查COMPLETE**·**Step2 Night1 cline-patched rerun 34/96 nonempty**(baseline303→325=+22 resolved)·TASK归档已搬ARCHIVE✅
当前动作:     R2992: 11-23令park轮·判据全绿(guard PID931671零越界~90.3h·mem1185G·load31.6·pretrain正常✅)·监控incr eval PID3117624(--all --regen 83 targets: cline9✅r=328+3·codex10✅·dsh1✅·cc6✅·pi42 41/42 scikit-learn14710 running→hermes9→oc6→auto-REGEN 7way报告)·watcher PID3117637 re-armed(→21:00)·cline-patched rerun 34/96 nonempty(overall 434/500)·cline=328/500=65.6%(incr eval merged)·MM 2×3 has_patch=2545·2路kimi retry pass仍RUN
下一步:       ①下轮唤醒验证incr eval PID3117624完成+auto-REGEN 7way报告(pi42+hermes9+oc6 tail·预计~10:00完成)→报最终Pass%·②21:00 watcher PID3117637 fire→resume cline-patched predict(剩余62/96 rerun IDs)→eval→merge→REGEN·cline完成后→codex365→deepseek273→cc184→pi284→hermes101→opencode54=1357题·每路predict→eval(mem128g/cpu16)→merge回eval_glm53_*.json→REGEN 7way报告·守护栏(docker mem128g/cpu16·ulimit200GiB·nice19·guard PID931671·pretrain≤7.4s·越界降载·限并发≤2路·429退避)→③并行:监控MM 2×3 predict 2路 retry pass(has_patch爬升→processes退出后re-launch清error→MM eval)→④codex quota恢复后predict 442→500
阻塞:         无
ERROR_COUNT:  0
 体积: TASK~34KB（✅<40KB硬限·超32KB软限·下次唤醒归档） / MEMORY≈31KB（✅≤32KB·R2990及更早指针已归档→daily-memories-harness）
 SWE-bench Verified Pass%(分母恒500·incr_eval进行中): hermes444/500=88.8%·opencode415/500=83.0%·cline328/500=65.6%(+3 incr eval)·cc295/500=59.0%·pi247/443=55.8%(待pi incr eval)·dsh195/311=62.7%·codex115/428=26.9%·（MM 2×3 predict 6路全480/480 attempted·2路kimi retry pass仍RUN·has_patch=2545）
 真实 Pass% (layer-A/B, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%
  SWE-bench Multimodal 2×3 predict(6路全480/480 entries·2路kimi retry pass仍RUN): cline×deepseek393has(DONE)·cline×doubao466has(DONE)·cline×kimi368has(400/480·retry pass)·opencode×deepseek453has(DONE)·opencode×doubao448has(DONE)·opencode×kimi417has(432/480·retry pass)=2545/2880 has_patch(progress entries·live 05:55·净趋势上行2439@R2962→2486@R2979→2511@R2981→2524@R2983→2537@R2986→2545@R2987→2545@R2988)·4路DONE·2路processes仍RUN(retry error·PID2131928/2140487~82h·nice19/OMP8/ulimit200GiB·CPU 0.0%·RSS低✅无失控)·retry机制正确·EAGAIN[Errno11]=infra非永久·非能力
  research日报11-19 harness建议: ①完成判据三分法 ②MM判分格式合法率vs正确率分两列+四组分组 ③20480生成上限写进评测配置 ④两档prompting分任务族报分 → 解冻后纳入(来自 research 日报 2026-11-19)
  research日报11-21 harness建议: ①记忆模块按「记录条数」+「检索上下文token」双预算报告(ref MemFolder 50%记录/99%保留) ②SFT数据skill前缀消融(判据六设置均分) ③评测脚本报单请求延迟分解(prefill/decode/工具等待) → 报告格式改进·待MM eval出结果后纳入(来自 research 日报 2026-11-21)
  research日报11-22 harness建议: ①「先观测后生成」两段式(task-guided inspection+API grounding·+15.7pp不训练可拿) ②按阶段隔离训练(生成/复核分开·易定位退化) ③执行结果一致性投票替代多数投票(环境信号>模型自评) → 风险:仅4B级验证/表格任务易验证/数字作者自报 → 待MM eval出结果后纳入(来自 research 日报 2026-11-22)
  research日报11-23 harness建议: ①CAMEL四类失败(role flipping/repeats instruction/flake reply/infinite loop)做成自动检测器·先跑100条多轮轨迹·判据≥30%命中→该批次不得作「能力提升」证据 → 待infra rerun完成后纳入(来自 research 日报 2026-11-23)
  research日报11-23 harness建议: 把CAMEL四类失败(role flipping/repeats instruction/flake reply/infinite loop)做成自动检测器·先跑100条现有多轮轨迹(①承诺式动词后无工具调用 ②角色关键词翻转 ③连续两轮指令嵌入余弦>0.9 ④连续3轮无新工具调用/无状态变化)·预注册判据:若≥30%轨迹命中至少一类则该批次不得作「能力提升」证据只能作失败分析 → 失败分析工具·待MM eval出结果后纳入(来自 research 日报 2026-11-23)
  research日报11-24 harness建议: ①部署模型核验协议(2611.27831):验收「部署模型=声称ckpt」时固定每prompt采样条数R·列temp/top-p档位·报同家族ckpt混淆率·缺R与解码档位的「指纹一致」不算证据 ②知识表示对照(2611.27734):同题集跑无知识/检索/agent自建本体/专家本体四档·报每档绝对分与差值 ③TEA-Bench-BR(2611.27895):变异体杀灭率作为判分充分性证据(1955个非等价变异体全杀) ④RoSci(2611.27750):Parse-Verify-Decide作为harness低成本基线 → 待infra rerun完成后纳入(来自 research 日报 2026-11-24)

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