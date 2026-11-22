# MEMORY_HARNESS.md — BaiZe Harness 研究线 · 运行时状态

WAITING: 1
> 🆕 **R2927 · 2026-11-23 02:20 — 16:3x解冻令·监控轮#119·Step2.3 MM retry pass进行中·has_patch=2267(+5·retry churn·4路仍RUN)·判据全绿**·**心跳第一行**: ✅自检clean✅ ①guard PID931671存活(~58.9h·ppid1·etimes212538s·State=S sleeping·VmRSS3536kB·零越界·guard log仅启动行无kill)✅ ②mem avail1251G≥512G✅ ③load1=27.08/load5=26.90/load15=27.41≤120✅ ④pretrain step avg~7122ms=7.12s(iter289810·41.40%·last5:7073/7077/7230/7053/7176·全≤7400·NOT elevated✅≤7.4s·loss≈1.99·0NaN/0skip✅·lr=1e-3 stable·master Step Time7.25s)[源:MEMORY_PRETRAIN_2B #3077@02:19] ⑤无失控进程✅(top CPU=pretrain launcher PID2601331~145%[训练·正常]·本线harness procs全nice19未进top·无>5000%pcpu) ⑥docker ps空✅(ps -a 63 stopped历史容器无资源影响). **Step1护栏LIVE**(4/4 predict workers HARD VERIFIED✅·PID2131912/2131930/2132137/2140501·etimes~212000s~58.8h·Max address space=214748364800 bytes=200GiB·nice19✅·OMP_NUM_THREADS=8✅·/proc/environ HARD VERIFIED✅·guard零越界✅·predict_guarded.sh ulimit200GiB+OMP8+nice19/ionice3✅·swebench_guarded_eval.py docker mem128g/memswap128g/nano_cpus16 monkey-patch在位✅). **Step2.1 COMPLETE·Step2.2 backlog=0✅**. **Step2.3 MM retry pass进行中·has_patch=2267(progress_2x3 classification实查·live 02:17·retry churn·净趋势上行2262@R2926→2267)·per-route has_patch: cline×dsh349·cline×kimi258(+1)·cline×doubao466(=DONE)·oc×dsh439(+1)·oc×kimi307(+3)·oc×doubao448(=DONE)→retry剩余448(error418+blocked30·4 routes)·predictions_2x3=2432 files(climbing·recent mtime 02:16✅活跃)**: 4路RUN(predict python3 PID2131912/2131930/2132137/2140501·etimes~212000s~58.8h·均活跃无stall·retry机制正确·kimi路最慢). 无新eval→7way不REGEN. 📦 TASK32.2KB MEMORY~16.9KB
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

PHASE:        16:3x 解冻令·Step 1✅·Step 2.1 predict COMPLETE(pi500/dsh332/codex442quota)·Step 2.2 incr_eval backlog=0✅·Step 2.3 MM 2×3 predict 4路仍RUN retry pass(has_patch=2267(progress_2x3 classification实查·live 02:17·retry churn)·retry剩余448·retry机制正确)
已完成:       H-B OK·Gate7/7·TB-2.1 oracle5/5·TB-2.1 7路rerun COMPLETE·codex.py fix①②③✅·SWE-bench Verified predict 7路·§11-19报告重写✅(R2758)·MM容器下载COMPLETE(580/580)✅·Phase 0 冻结验收通过✅·Step 1 硬护栏全落地✅(swebench_guarded_eval.py docker mem128g/cpu16 monkey-patch HARD VERIFIED✅·predict_guarded.sh ulimit200GiB+OMP8+nice19/ionice3✅·guard PID931671✅)·**Step 2.1 Verified predict COMPLETE**: pi500/500·dsh332/500·codex442/500(quota)·**Step 2.2 incr_eval backlog=0**(deepseek+pi全评测)·**7way报告REGEN R2808**(cline303/pi247/dsh195/codex115)·**Step 2.3 MM 2×3 predict 6路全2880/2880 attempted**(has_patch2262·4路processes仍RUN retry error/blocked)·TASK归档14:5x+08:2x已搬ARCHIVE✅
当前动作:     R2927: 监控轮#119·MM 2×3 predict 6路全2880/2880 attempted·has_patch=2267(+5·retry churn·4路仍RUN retry pass)·判据全绿(load27.08/mem1251G/pretrain step avg~7122ms=7.12s(iter289810·41.40%·last5:7073/7077/7230/7053/7176·全≤7400·NOT elevated✅≤7.4s)[源#3077@02:19·loss≈1.99·0NaN/0skip])·guard PID931671零越界~58.9h etimes212538s·/proc HARD VERIFIED ulimit200GiB 4/4 predict workers(PID2131912/2131930/2132137/2140501·etimes~212000s~58.8h·Max address space=214748364800 bytes·nice19·OMP8·/proc/environ HARD VERIFIED)·无失控·top CPU=pretrain launcher PID2601331~145%[训练·正常]·本线harness procs全nice19·docker ps空·ps -a 63 stopped历史)·无新eval→7way不REGEN·per-route has_patch: cline×dsh349/cline×kimi258(+1)/cline×doubao466(=DONE)/oc×dsh439(+1)/oc×kimi307(+3)/oc×doubao448(=DONE)·retry剩余448(error418+blocked30·4 routes)·predictions_2x3=2432 files(climbing·mtime02:16✅)·4路predict python3 alive(PID2131912/2131930/2132137/2140501 etimes~212000s~58.8h)·均活跃无stall·kimi路最慢·无需改码(retry机制正确)
下一步:       ①监控MM 2×3 predict 4路 retry pass(has_patch爬升至2267+·ETA~10-20h(kimi路瓶颈·retry剩余448)·pretrain≤7.4s/mem≥512G/load≤120·越界降载/暂停)→②processes退出后re-launch清剩余(仅Errno7 6项永久·其余EAGAIN已自愈)→③MM eval(全部has_patch走guarded容器mem128g/cpu16·串行)→④codex quota恢复后rerun 256 quota_blocked+predict 442→500→⑤deepseek predict 4 no-patch refill(低价值可选)
阻塞:         无
ERROR_COUNT:  0
 体积: TASK32.2KB（✅<40KB硬限·贴32KB软限·14:5x/08:2x已归档）/ MEMORY≈16.9KB（✅≤32KB·R2926及更早指针已归档→daily-memories-harness）
 SWE-bench Verified Pass%(分母恒500·incr_eval backlog=0): hermes444/500=88.8%·opencode415/500=83.0%·cline303/500=60.6%·cc295/500=59.0%·pi247/500=49.4%·dsh195/500=39.0%·codex115/500=23.0%·（MM 2×3 predict 6路全2880/2880 attempted·processes retry中）
 真实 Pass% (layer-A/B, 分母=89): cline42/89=47.2%·codex25/89=28.1%·opencode45/89=50.6%·cc30/89=33.7%·pi35/89=39.3%·hermes41/89=46.1%·deepseek11/89=12.4%
   SWE-bench Multimodal 2×3 predict(4路仍RUN retry pass·480题/路): cline×deepseek349has/cline×doubao466has(DONE)·cline×kimi258has·opencode×deepseek439has·opencode×doubao448has(DONE)·opencode×kimi307has=2267/2880files·has_patch=2267(progress_2x3 classification实查·live 02:17·retry churn·净趋势上行2262@R2926→2267)·4路processes仍RUN(retry error/blocked·predict python3 PID2131912/2131930/2132137/2140501 etimes~212000s~58.8h·nice19/OMP8/ulimit200GiB·/proc HARD VERIFIED 4/4 predict workers·Max address space=214748364800 bytes)·predictions_2x3=2432 files(climbing·recent mtime 02:16✅活跃)·retry pass推进中·retry剩余448(error418+blocked30·4 routes)·kimi路最慢·无error新增·retry机制正确·非永久失败·非能力
  research日报11-19 harness建议: ①完成判据三分法 ②MM判分格式合法率vs正确率分两列+四组分组 ③20480生成上限写进评测配置 ④两档prompting分任务族报分 → 解冻后纳入(来自 research 日报 2026-11-19)
  research日报11-21 harness建议: ①记忆模块按「记录条数」+「检索上下文token」双预算报告(ref MemFolder 50%记录/99%保留) ②SFT数据skill前缀消融(判据六设置均分) ③评测脚本报单请求延迟分解(prefill/decode/工具等待) → 报告格式改进·待MM eval出结果后纳入(来自 research 日报 2026-11-21)
  research日报11-22 harness建议: ①「先观测后生成」两段式(task-guided inspection+API grounding·+15.7pp不训练可拿) ②按阶段隔离训练(生成/复核分开·易定位退化) ③执行结果一致性投票替代多数投票(环境信号>模型自评) → 风险:仅4B级验证/表格任务易验证/数字作者自报 → 待MM eval出结果后纳入(来自 research 日报 2026-11-22)
  research日报11-23 harness建议: 把CAMEL四类失败(role flipping/repeats instruction/flake reply/infinite loop)做成自动检测器·先跑100条现有多轮轨迹(①承诺式动词后无工具调用 ②角色关键词翻转 ③连续两轮指令嵌入余弦>0.9 ④连续3轮无新工具调用/无状态变化)·预注册判据:若≥30%轨迹命中至少一类则该批次不得作「能力提升」证据只能作失败分析 → 失败分析工具·待MM eval出结果后纳入(来自 research 日报 2026-11-23)

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