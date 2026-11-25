# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> 🎯 **现行路线 = F 自定义改造（权重热更新 + per-source 游标映射）** · patch/验证状态 = 7/7 standalone PASS + 5/5 Megatron-integration PASS（2026-11-23）· 零重叠实测 = 0（standalone overlap_docs=0 + integration total_overlap=0，第425次 fresh 复验）· 350k 倒计时 ≈ 2d → ~11-28（patch + 零重叠验证已完成，早于 11-27 截止）· **Megatron-LM 源码集成已完成**：dev copy `code/Megatron-LM-blendswitch` branch `blend-hot-switch` commit `011a05b`，5 文件 patch + 2 新文件，base `14c215d`，未 merge 主线

> 🟢 **心跳 · 2026-11-25 16:34 (R633) — 例行巡检 + blendswitch 第425次 fresh 复验 7/7 PASS zero_overlap=0**：①✅git synced(fetch origin·HEAD=510087769f·0新data令·所有用户令已交付)；②✅blendswitch 7/7 PASS(第425次 fresh 复验 py310 test_blend_switch.py)·zero_overlap_pass=True·overlap_docs=0(7源全0)·flag_off_equivalence=True·ratio_switch_pass=True·ratio max dev=0.0087%·new_source_zero_overlap_pass=True·epoch_wrap_pass=True·json_roundtrip_pass=True·perf_pass=True·7文件全tracked·复跑后verify_results.json已checkout还原；③✅integration 5/5 PASS total_overlap=0(commit 011a05b base 14c215d·本轮未复跑)；④✅3关键报告 size 合规(v5=13,813B≤20KB / v4=14,625B≤15KB / F-explainer=40,743B≤80KB)·0 `<script>`·0外链；⑤✅pretrain iter≈320,450/700k(45.78%)·step7.24s·320k eval RUNNING·318k eval DONE harness_avg=56.25%·350k倒计时≈2d→~11-28；⑥✅.12 load25.02/25.98/26.22·0下载进程·/nas_user 42T余(63%)>5T红线✅；⑦✅research日报data建议(1T token配方对照/程序化轨迹配比/数学代码独立源)均为借鉴类已评估记录；⑧✅所有用户令已交付。WAITING=0。
> 📦 R632 心跳（例行巡检+blendswitch第424次复验7/7 PASS·iter≈320,450 step7.24s·320k eval RUNNING·318k eval DONE harness_avg=56.25%·.12 load25.77/26.35/26.42·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R631 心跳（例行巡检+blendswitch第423次复验7/7 PASS·iter≈320,390 step7.26s·320k eval RUNNING·318k eval DONE harness_avg=56.25%·.12 load27.32/27.06/26.45·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R630 心跳（例行巡检+blendswitch第422次复验7/7 PASS·iter≈320,390 step7.26s·320k eval RUNNING·318k eval DONE harness_avg=56.25%·.12 load25.76/26.12/25.90·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R629 心跳（例行巡检+blendswitch第421次复验7/7 PASS·iter≈320,250 step7.25s·320k eval RUNNING·318k eval DONE harness_avg=56.25%·.12 load26.27/26.31/25.95·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R628 心跳（例行巡检+blendswitch第420次复验7/7 PASS·iter≈320,250 step7.25s·320k eval RUNNING·318k eval DONE harness_avg=56.25%·.12 load26.86/26.06/25.72·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R627 心跳（例行巡检+blendswitch第419次复验7/7 PASS·iter≈320,130 step7.24s·320k eval RUNNING·318k eval DONE harness_avg=56.25%·.12 load25.14/25.05/25.38·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R626 心跳（例行巡检+blendswitch第418次复验7/7 PASS·iter≈320,000 step7.24s·318k eval DONE harness_avg=56.25%·320k ckpt已落盘待eval·.12 load24.90/25.40/25.55·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R625 心跳（例行巡检+blendswitch第417次复验7/7 PASS·iter≈319,950 step7.24s·318k eval DONE harness_avg=56.25%·.12 load26.08/25.87/25.45·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R623 心跳（例行巡检+blendswitch第415次复验7/7 PASS·iter≈319,880 step7.26s·318k eval DONE harness_avg=56.25%·.12 load25.58/25.41/25.41·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R622 心跳（例行巡检+blendswitch第414次复验7/7 PASS·iter≈319,720 step8.53s·318k eval DONE harness_avg=56.25%·.12 load24.93/25.65/25.52·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R620 心跳（例行巡检+blendswitch第412次复验7/7 PASS·iter≈319,750 step7.42s·318k eval DONE harness_avg=56.25%·.12 load24.34/24.44/24.72·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R619 心跳（例行巡检+blendswitch第411次复验7/7 PASS·iter≈319,620 step7.42s·318k eval DONE harness_avg=56.25%·.12 load25.55/24.20/24.79·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R618 心跳（例行巡检+blendswitch第410次复验7/7 PASS·iter≈319,520 step7.89s·318k eval DONE harness_avg=56.25%·.12 load24.85/25.79/25.50·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R616 心跳（例行巡检+blendswitch第408次复验7/7 PASS·iter≈319,500 step7.91s·318k eval DONE harness_avg=56.25%·.12 load25.23/24.49/25.15·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R614 心跳（例行巡检+blendswitch第406次复验7/7 PASS·iter≈319,390 step7.91s·318k eval DONE harness_avg=56.25%·.12 load29.22/26.14/26.02·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R611 心跳（例行巡检+blendswitch第403次复验7/7 PASS·iter≈319,300 step7.80s·318k eval DONE harness_avg=56.25%·.12 load27.76/26.18/26.54·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R610 心跳（例行巡检+blendswitch第402次复验7/7 PASS·iter≈319,250 step7.19s·318k eval RUNNING·.12 load26.95/26.86/27.29·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R607 心跳（例行巡检+blendswitch第399次复验7/7 PASS·iter≈319,060 step7.32s·.12 load27.58/27.60/27.64·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R605~R596 心跳（例行巡检+blendswitch第397~388次复验全7/7 PASS·iter318,760~318,940·step7.29~7.34s·.12 load25~29·0下载进程）已批量归档 → daily-memories-data/2026-11-25.md
> 📦 R594~R580 心跳（例行巡检+blendswitch第386~372次复验全7/7 PASS·iter317,340~318,170·step7.26~7.50s·.12 load25~29·0下载进程）已批量归档 → daily-memories-data/2026-11-25.md + 2026-11-24.md
> 📦 R600~R580 心跳（例行巡检+blendswitch第392~372次复验全7/7 PASS·iter317,340~318,700·step7.25~7.50s·.12 load25~30·0下载进程）已批量归档 → daily-memories-data/2026-11-25.md
> 📦 R579~R570 心跳（例行巡检+blendswitch第371~363次复验全7/7 PASS·iter316,900~317,340·step7.02~7.36s·.12 load27~36·0下载进程·R574=zhulong误删81文件已恢复·R570=git merge修复）已批量归档 → daily-memories-data/2026-11-25.md
> 📦 R565~R569 心跳（例行巡检+blendswitch第358-362次复验均7/7 PASS·iter≈310,160-310,490 step7.02s·.12 load26-30·0下载进程）已批量归档 → daily-memories-data/2026-11-24.md
> 📦 R564 心跳（例行巡检+blendswitch第357次复验7/7 PASS·iter≈310,160 step7.02s·.12 load28.43/26.65/26.18·0下载进程）已归档 → daily-memories-data/2026-11-24.md
> 📦 R563 心跳（例行巡检+blendswitch第356次复验7/7 PASS·iter≈310,040 step7.29s·.12 load25.90/25.10/25.28·0下载进程）已归档 → daily-memories-data/2026-11-24.md

> 📦 R546~R13 心跳（534轮例行巡检+blendswitch第1~350次复验全7/7 PASS·iter260k~309.6k·step7.0~8.1s·300k~308k eval DONE/RUNNING·.12 load均<36·0下载进程·R363=Megatron集成完成5/5 PASS·R170=v5报告+blend_switcher.py交付·R171=v4报告结论段修正·R348=R548=numpy修复）已批量归档 → daily-memories-data/2026-11-20.md ~ 2026-11-24.md
> _(R9, R8, R7, R4 心跳已归档 daily-memories-data/2026-11-19.md · iter~260k step~7.05s Nemotron 82-88% MM-web分词启动(ETA~40h) Math-Reasoning 72%)_
> 📦 旧已交付用户令摘要（2026-11-13 ~ 11-18：S2 overlap研究/PC-4 blend TSV/Nemotron+finemath分词/CPU僵尸清理/stack-v3全量下载/下载优先级/IFM数据集/agent datasets — 全部已交付，S2三源下载全100%）已归档 → daily-memories-data/2026-11-23.md「归档块1」
> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 📦 旧详细报告条目（vision图文对调研/stack-v3下载+分词+EDA脚本价值分析 — 全部已交付，报告均落 reports/）已归档 → daily-memories-data/2026-11-23.md「归档块2」
> 📦 唤醒1522-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC完成+IFM下载启动+Code-Reasoning崩溃修复重启+多轮巡检,共10轮,详见日文件）
> 📦 唤醒1493-1520 原文已归档 → daily-memories-data/2026-11-14.md~2026-11-15.md（StepB完成+StepC分词启动+崩溃修复+IFM/agent datasets进度,共~25轮,详见日文件）
> 📦 唤醒1490-1492 原文已归档 → daily-memories-data/2026-11-13.md（StepB下载进度巡检+StepC auto-wait修复重启×3轮,详见日文件）
> ⚠️ [11-14 19:2x] 运维介入修复记录：StepC 16workers在shard5350处BrokenPipeError崩溃(OOM→Pool pipe断裂→NFS写入未flush→989新shard输出丢失)→修复:fsync+maxtasksperchild50+BrokenPipeError异常处理+workers 16→8→PID1677655重启,nice19/ionice3,日志/tmp/tokenize_stackv3_new.log

> 📦 唤醒1489 原文已归档 → daily-memories-data/2026-11-13.md（ETA审计完成+StepC护栏修复+任务书归档,详见日文件）
> 📦 唤醒1487-1488 原文已归档 → daily-memories-data/2026-11-13.md（StepA DONE确认+StepB下载进度巡检×2轮,旧ETA~3.3h已被本轮纠正,详见日文件）
> 📦 唤醒1483-1486 原文已归档 → daily-memories-data/2026-11-13.md（StepA DONE确认+StepB下载进度巡检+StepC launch启动,共4轮,详见日文件）
> 📦 唤醒1471-1482 原文已归档 → daily-memories-data/2026-11-13.md（分词完成+全量下载启动+rsync 2TB+源删除+hf download全量+用户令11-13b启动,共12轮,详见日文件）

> 📦 迁移完成块(运维令13:3x+SFT/Agent分词+5源+4源+3稳定源+ufw_en,共9源705shard~8.3TB→/nas_env)已归档 → daily-memories-data/2026-11-13.md；结论见DATA_MAPPING.md

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        S2前置+污染闸门全完成 — PC-1✅~PC-5✅ + 扩展黑名单✅ + S2新源扫描✅(48K docs/0命中) + 方案F blendswitch交付✅(7/7零重叠=0) → WAITING=0
已完成:       ✅PC-1 L4过滤(430.7B/90.5%);✅PC-2 MegaMath分词ALL DONE(5 subsets/364 shards/243GB);✅PC-3污染闸门(6benchmark/9277tasks);✅PC-4 main版blend_s2_preblend.tsv(12源/含nemotron 0.067+megamath_web 0.060+finemath 0.005/weight_sum=1.0/gen_blend --verify通过);✅S2重叠研究报告;✅finemath-4plus分词DONE(9.4B tok);✅v3报告(R136刷新main版/pushed);✅MegaMath-web下载DONE(4950parquet/826GB);✅MegaMath-web分词DONE(4950/4950=100%/218.1B tok);✅Code-Reasoning下载DONE(1637parquet/0inc);✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors);✅Math-Reasoning下载DONE(2228parquet/0inc);✅DATA_MAPPING.md更新;✅论文Fig-1三饼图+Fig-2调优+TABLE IV精简+数据源/Decay/LongCtx引用补齐(latexmk 0err);✅EDA-Eval 536-task黑名单重跑复现(R137/正控158/158);✅扩展黑名单blacklist_extended建成(R138/5359tasks/4847354 13-gram/正控164/164);✅S2新源污染扫描(R139/4源×12K=48K docs/全0命中);✅方案F blendswitch交付(R170-R171/commit 68742cfbe4/blend_switcher.py+v5报告+v4修正+CPU验证7/7零重叠=0)
当前动作:     R633例行巡检:iter≈320,450/700k(45.78%) step7.24s 训练健康✅ loss=1.989 0NaN/0skip lr=1e-3(320k eval RUNNING·318k eval DONE harness_avg=56.25%)；方案F blendswitch第425次fresh复验7/7 PASS(zero_overlap=0)+Megatron源码集成5/5 PASS(commit 011a05b未merge主线)；git synced(0新data令)；PC-1~PC-5全✅/S2三下载全100%/无后台任务/.12 load=25.02/25.98/26.22✅/350k倒计时≈2d→~11-28
下一步:       ①等pretrain到350k(~11-28)启动S2(blend TSV已就绪/SEED=5678待转告pretrain线) ②S2投料前可按S1口径对4新源做全量扫描(>150K docs)作为加强验证(非阻塞/contam_venv已就绪) ③research日报建议均为借鉴类,已评估忽略
阻塞:         无(全部前置完成;S2三下载全100%;无后台任务;.12 load≈25.02/25.98/26.22<120✅;/nas_user 42T可用✅>5T红线)
ERROR_COUNT:  0
未完成指令:   无(全部用户令已交付;PC-1~PC-5全部完成;main版blend TSV已就绪)→WAITING=0
```

> 📦 唤醒1521-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC巡检+Agent/IFM下载进度+Code-Reasoning重启+IFM多轮巡检,详见日文件）

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [11-21 16:2x] 唤醒1557（v3报告R116刷新·例行巡检·所有用户令已交付）：①🔄MegaMath-web分词RUNNING(4445/4950=89.8%/~195.9B tok/ETA~4.7h/PID3028119+3028124/nice19/ionice3/RAYON=8/428%CPU=4核/etime~1d17h)；②✅Nemotron-CC-Math分词DONE(193/193/195.4B tok)；③✅finemath分词DONE(9.4B tok)；④✅Math-Reasoning下载DONE(2228/0inc)；⑤✅Code-Reasoning下载DONE(1637/0inc)；⑥✅.12 load=29.7✅<120红线；⑦✅.29 load=26.6✅；⑧✅磁盘/nas_user 113T/71T已用/42T可用(63%)→✅红线≥5T；⑨✅pretrain训练正常(iter~273.0k/step~7.13s/latest ckpt=272k)；⑩✅v3报告R116刷新(MegaMath-web 4445/4950=89.8%/load 29.7)；⑪✅git up-to-date with origin(无新data令/所有用户令已交付)；⑫下一步：等MegaMath-web分词完成(~4.7h)→更新main版blend TSV(加Nemotron)→逐源13-gram污染扫描→commit+push
> [11-20 10:00] 唤醒1556（v3报告R36刷新·2后台任务巡检·所有用户令已交付）：①🔄MegaMath-web分词RUNNING(1398/4950=28.2%/~55.4B tok/ETA~28.3h/PID3028124/nice19/ionice3/RAYON=8/438%CPU=4核)；②🔄Math-Reasoning下载RUNNING(1994/2228=89.5%/2inc/ETA~4.1h/PID3697171/nice19/ionice3/max-workers2)；③✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors)；④✅Code-Reasoning下载DONE(1635/0inc)；⑤✅.12 load=11.40✅<120红线；⑥✅磁盘/nas_user 113T/70T已用/43T可用(63%)→✅红线≥5T；⑦✅v3报告R36刷新(MegaMath-web 1398/4950=28.2%/Math-Reasoning 89.5%/load 11.40)；⑧✅git up-to-date with origin(无新data令)；⑨所有3条11-19用户令(v3报告/Fig-2饼图+TABLE IV/数据源引用+Fig-1三饼图)均已交付✅；⑩下一步：等MegaMath-web分词完成(~28h)→更新main版blend TSV(加Nemoton)→13-gram污染扫描→commit+push
> [11-20 ~04:00] 唤醒1555（v3报告R20刷新·3后台任务巡检）：①✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors)；②🔄MegaMath-web分词RUNNING(702/4950=14.2%/~26.4B tok/ETA~31h/PID3028119/nice19/ionice3/RAYON=8)；③🔄Math-Reasoning下载RUNNING(1764/2228=79.1%/3.3TB/2inc/ETA~8h/PID3697171/nice19/ionice3/max-workers2)；④✅.12 load=9.59✅<120红线；⑤✅磁盘/nas_user 113T/70T已用/44T可用(62%)→✅红线≥5T；⑥✅v3报告R20刷新(MegaMath-web 702/4950=14.2%/Math-Reasoning 79.1%/load 11.97)；⑦✅git pulled origin(d950d2c09/无新data令/所有用户令已交付)；⑧下一步：等MegaMath-web分词完成(~31h)→更新main版blend TSV→13-gram污染扫描→commit+push
> [11-20 02:10] 唤醒1554（例行巡检·v3报告刷新·3后台任务健康·Nemotron即将完成）：①🔄Nemotron-CC-Math分词 RUNNING(189/193=97.9%/~150B tok已产出/ETA~38min即将完成/PID1791934/nice19/ionice3/RAYON=8)；②🔄MegaMath-web分词 RUNNING(426/4950=8.6%/~15.7B tok/ETA~35h/PID3028124/nice19/ionice3/RAYON=8)；③🔄Math-Reasoning下载 RUNNING(1690/2228=76%/ETA~9h/PID3697171/nice19/ionice3/max-workers2)；④✅.12 load=13.34✅<120红线；⑤✅磁盘/nas_user 113T/70T已用/44T可用(62%)→✅红线≥5T；⑥✅v3报告已刷新最新live numbers(Nemotron 97.9%/MegaMath-web 8.6%/Math-Reasoning 76%/load 13.34)；⑦✅git up-to-date with origin；⑧下一步：Nemotron分词即将完成(~38min)→完成后立即更新main版blend TSV(加入Nemotron源/下调megamath prop/epoch从1.69降到~0.62)→更新v3报告→commit+push

> 📦 唤醒1552 原文已归档 → daily-memories-data/2026-11-19.md（例行巡检·4后台任务健康·Code-Reasoning 93%·Nemotron 21/193,详见日文件）

> 📦 唤醒1549-1551 原文已归档 → daily-memories-data/2026-11-18.md（例行巡检×3轮·4后台任务健康·Code-Reasoning渐进93%·Nemotron分词21/193,详见日文件）

> 📦 唤醒1548 原文已归档 → daily-memories-data/2026-11-18.md（3个崩溃下载重启+finemath分词DONE+Nemotron进度巡检,详见日文件）

> 📦 唤醒1547 原文已归档 → daily-memories-data/2026-11-18.md（后台任务巡检+IFM下载重启+进度更新,详见日文件）

> 📦 唤醒1536-1546 原文已归档 → daily-memories-data/2026-11-16.md~2026-11-17.md（IFM下载多轮巡检+Code-Reasoning崩溃修复重启+MegaMath batch2启动+HfApi实测,共11轮,详见日文件）
> 📦 唤醒1457-1465 原文已归档 → daily-memories-data/2026-11-12.md~2026-11-13.md（例行巡检×9轮,stack-v3-train稳定1.9T,无新data令,详见日文件）
> 📦 唤醒1458 原文已归档 → daily-memories-data/2026-11-13.md（例行巡检,无新data令,详见日文件）
> 📦 唤醒1410-1420 原文已归档 → daily-memories-data/2026-11-13.md（batch6-7进度巡检×11轮,batch6完成1.813TB+batch7启动,2TB预算92.4%,详见日文件）
> 📦 唤醒1444-1456 原文已归档 → daily-memories-data/2026-11-11.md~2026-11-12.md（例行巡检+vision图文对调研报告交付,共13轮,详见日文件）
> 📦 唤醒1425-1440 原文已归档 → daily-memories-data/2026-11-10.md（例行巡检+staleness审计+论文数据节更新+TASK.md标记更新,共16轮,详见日文件）
> 📦 唤醒1422-1424 原文已归档 → daily-memories-data/2026-11-10.md（batch7完成+QC+2TB ROI复盘+例行巡检,共3轮,详见日文件）
> 📦 唤醒1385 原文已归档 → daily-memories-data/2026-11-13.md（11-07运维令执行:代码语料放行ROI下载,详见日文件）
> 📦 唤醒1374-1384 原文已归档 → daily-memories-data/2026-11-07.md（例行空唤醒巡检,共11轮,详见日文件）
> 📦 唤醒1346-1373 原文已归档 → daily-memories-data/2026-11-06.md~2026-11-07.md（例行空唤醒巡检,共28轮,详见日文件）
> 📦 唤醒1319-1345 原文已归档 → daily-memories-data/2026-11-06.md（例行空唤醒巡检,共27轮,详见日文件）
> 📦 唤醒1283-1318 原文已归档 → daily-memories-data/2026-11-06.md（例行空唤醒巡检,共36轮,详见日文件）
> 📦 唤醒1282-1241 原文已归档 → daily-memories-data/2026-11-05.md（例行空唤醒巡检,共42轮,详见日文件）
> 📦 唤醒1240-1213 原文已归档 → daily-memories-data/2026-11-05.md（例行空唤醒巡检,共28轮,详见日文件）
> 📦 唤醒1180-1212 原文已归档 → daily-memories-data/2026-11-04.md（例行空唤醒巡检+09:2x下载巡检+09:4x报告复核,共33轮,详见日文件）
> 📦 唤醒1161-1179 原文已归档 → daily-memories-data/2026-11-04.md（运维令10-31交付物v6例行复核+85M下载进度巡检+09:2x下载巡检,共19轮,详见日文件）
> 📦 唤醒1117-1160 原文已归档 → daily-memories-data/2026-11-04.md（运维令10-31交付物v6例行复核+85M下载进度巡检,共44轮,详见日文件）
> 📦 唤醒1107-1116 原文已归档 → daily-memories-data/2026-11-03.md（运维令10-31交付物v5例行复核+85M下载进度巡检+HF链接真实性抽检7个数据集HTTP 200全PASS,共10轮,详见日文件）

> 📦 唤醒1065-1106 原文已归档 → daily-memories-data/2026-11-03.md（运维令10-31交付物v4-v5例行复核+85M下载进度巡检,共42轮,详见日文件）
> 📦 唤醒1030-1063 原文已归档 → daily-memories-data/2026-10-31.md（运维令10-31报告v3-v4复核+85M下载进度巡检,详见日文件）
> 📦 唤醒833-1023 原文已归档 → daily-memories-data/2026-10-30.md ~ 2026-10-31.md（例行巡检+85M字节增长复核,详见日文件）
## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。
### ①-⑧ 已归档（详见 `daily-memories-data/2026-10-06.md`）

| # | 主题 | 结论 | 日期 |
|:--|:--|:--|:--|
| ① | SFT-2605 重下 | ✅ 1504 jsonl / 318.99 GB，与 HF 官方清单逐字节一致 | 10-02 |
| ②-④ | D-CLEAN-1/2/3 | ✅ 盘点 + 删除 servers(974G)+nemo R1(310G)+laion(7.8G)+pip(3.3G) ≈1.3T；nemo R2 ckpt 保留 | 10-03 |
| ⑤ | 下载白名单 | ✅ 停 en_v1_4，只下 l1_en_hq+zh+GPIC | 10-03 |
| ⑥-⑦ | D-CLEAN-4 + LLaVA ckpt | ✅ 盘点：本用户可回收 ≈11.4TiB(含 LLaVA-OV 22TiB iter ckpt)，待运维拍板 | 10-04 |
| ⑧ | LIT_IDEAS HTML | ✅ 产出 `LIT_IDEAS_2026-10-05.html`（52 entries/0 unverified/62% turnover），含成本专章+ISEDA投稿要求(4-6页) | 10-04 |
> 📦 §⑨ 配比实验可行性核查 + §⑩ 运维三问 + 旧状态头（2026-10-05~07）已归档 → `daily-memories-data/2026-10-10.md`（唤醒305归档）；**结论**：⑨GPU2-7当时被P-9.8/9.9占满(现已释放)⑩三问已答(GPIC无加速/base下载全满/BO波次锯齿非I/O)。需要时再读。

> 📦 §⑪ 分词5worker+85M线路（2026-10-24 用户质询）已归档 → daily-memories-data/2026-10-24.md；**结论**：Q1=5worker因串行+剩余shard少,升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT)。需要时再读。

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| R research（🎯 只答 §0 两问） | ✅ 完成（DATA_RESEARCH v1.1：LLM 够/走路线A；Vision 换 GPIC short 消截断） |
| R2 LLM 数据侧调研（任务书两项优先） | ✅ 完成（DATA_RESEARCH R2 节：8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B = base-en(86):code(10):math(4)；base 2.99TB 下载已启动） |
| R2 视觉侧调研（§0.4 去 HF 找通用图文对） | ✅ 完成（DATA_RESEARCH R2-视觉侧：本地 12 源图像形态+≤77 实测 / 13 HF 候选其中 7 URL-only 淘汰 / 前 3 推荐 CC12M≈11M + Amshaker≈6M + LLaVA≈1.15M，50 万→1800 万对 ×35，无需新下载） |
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | ✅ 完成（v0.3：536 任务 + NFKC/Unicode 归一化 + 8-gram 兜底 + **SFT 嵌套 jsonl 目录同闸扫描**，全快照正控 100%） |
| phase1 validate（完整性校验） | 🟡 校验脚本已备（validate_data.py），全量跑待下载完成后 |
| phase2 text（通用文本 .bin/.idx） | 🟡 分词打包 wrapper 已备（preprocess_text.sh + 污染闸门），跑待下载完成后 |
| phase3 domain（EDA 领域语料排查） | 🚫 **已取消**（运维 2026-10-01 夜：评测 prompt 由 docstring 生成、与语料天然同源，入库无意义）；但 EDA-Eval 158 任务黑名单红线**依然有效、继续执行** |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [x] ~~EDA API 知识库能否导出纯文本~~ → **已确认可行**：`eda_fastmcp/docs/` 本就是 md/json 纯文本（≈45MB，见 DATA_LEDGER §5）。
- [x] ~~EDA 语料入库授权~~ → **整条线已取消**（运维 2026-10-01 夜）：评测 prompt 由 docstring 生成、与语料天然同源，"把测试集放进训练集"无意义 → phase3_domain 不再调研/入库。**但 EDA-Eval-PyAether 158 任务黑名单红线照常执行。**
- [x] ~~内部培训材料 / 脱敏 CAD 案例能否用于训练~~ → 随 phase3_domain 一并取消。
- [ ] 多模态下载预计完成时间
- [x] ~~`UltraData-SFT-2605/-Agent-2609` 具体存储格式~~ → **已实测**：Agent-2609 = **jsonl**（50 shard / 51 GiB，2GB/shard）；**2605 = 落盘为空**（仅 179 个 `.lock` 缓存文件 / 22.4KiB，无数据，需重下）
- [x] ~~`UltraData-SFT-2605` 重新下载~~ → **✅ 已下满并核验一致（2026-10-02 唤醒 37）**：落盘 **1504 jsonl / 318,990,252,711 B = 318.99GB（297.08 GiB）**，`.incomplete` = 0，**与 HF 官方清单（1504 文件 / 318,990,252,711 B）逐字节完全一致**；逐子目录 `no_think` 855✓（CG 50/Code 300/IF 20/Kn 80/Math 300/ML-Kn 50/ML-Math 55）+ `think` 649✓（CG 50/Code 279/IF 20/Kn 50/Math 250）。token `hf_lqLxH…`（用户 foamliu）。

> 📦 旧流水（唤醒111-145, S0a训练+分词+kill改道全程）已归档 → `daily-memories-data/2026-10-05.md` 及 `2026-10-06.md`
> 关键结论：①base分词22.05B tok✅ ②SFT-2605 20.97B+Agent-2609 全4shard✅ ③S0a 2.2B单臂浪费~100 GPU·h→改道proxy BO搜索 ④proxy模型92.7M(d=512/L=14)标定s/step=1.5s ⑤smoke test✅

> 📦 §s_step归因实验（2026-10-06）已归档 → `daily-memories-data/2026-10-06.md`；**结论**：MBS=16使s_step 1432ms→166ms(8.6×),overhead-bound,D=0.5B/trial→205trial/24h。需要时再读。
## �