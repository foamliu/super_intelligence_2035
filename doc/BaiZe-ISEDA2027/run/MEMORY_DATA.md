# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> 🎯 **现行路线 = F 自定义改造（per-source 游标映射）** · **🔴 Bridge Edition 重大更新（2026-11-27）**：原 `blend_hotswitch.patch` 针对标准 Megatron-LM，但 BaiZe 用 **Megatron Bridge**（pip 包）→ 改用 **runtime monkey-patch shim**（`blend_hot_switch_bridge_compat.py`，同 `bridge_compat.py` 模式）· 已修改 `pretrain_launcher.py`（第302-310行加 try/import shim）· 切换方式 = **冷切换**（stop→apply→restart）· 开关 = 环境变量 `BLEND_CURSOR_OFFSETS_JSON`（不设=stock 零开销）· cursor_offsets_350k.json 已预计算（89.6M samples，7共享源+5新源）· Bridge Edition 验证 **10/10 PASS**（含 shim 真实 import 成功）· 零重叠 = 0 · SWITCH_RUNBOOK.md 已更新为 Bridge Edition · `blend_s2_preblend.tsv` 已复制到 `code/baize-llm/configs/`

> 🟢 **心跳 · 2026-11-28 04:0x (R987) — fresh复验25/25 PASS(第742次) + 交付物全量在位✅ + 基础设施5项确认✅ + pretrain无待答(grep=0) + ckpt=344000 + WAITING=0**：①✅fresh复验25/25 PASS(本次实跑)：standalone 8/8(zero_overlap=0,real S1→S2 7→12 zero overlap=0,ratio max_dev=0.0000%,flag-off byte-identical) + bridge 10/10(shim importable,cursor offset sum=10000,zero overlap=0,flag-off di_same+dsi_same,ratio max_dev=0.000000%,Bresenham 70/30) + integration 7/7(zero overlap=0,ratio max_dev=0.0027%,checkpoint roundtrip,stock sampler epoch bug,BlendedDataset compat)；②✅交付物全量在位(blend_hotswitch.patch 43650B/blend_switcher.py 17966B/README_PATCH.md 10603B/s2_blend_switch_config.json 1298B/test_blend_switch.py 14307B/verify_results.json 8954B/verify_results_integration.json 6282B/blend_s2_preblend.tsv@baize-llm/configs 3625B/SWITCH_RUNBOOK.md 11236B 9节/bridge_compat_shim@BAIZE_TRAIN_CODE 4226B/compute_cursor_offsets.py 9762B/cursor_offsets_350k.json 1093B/test_bridge_compat.py 8562B/verify_results_bridge.json 1247B)；③✅基础设施5项确认：shim@BAIZE_TRAIN_CODE(4226B)✅·pretrain_launcher.py L306 shim import✅·train.sh L202/L206 BLEND_CURSOR_OFFSETS_JSON SSH透传✅·blend_s1+s2 TSV@configs✅·cursor_offsets_350k.json(12源89.6M)✅；④pretrain MEMORY_PRETRAIN_2B.md 无data待答(grep=0)✅·pretrain ckpt=344000·350k ETA~05:30 on 11-28·用户令4项职责复查全✅；⑤WAITING=0。
> 📦 R986 心跳（2026-11-28 03:2x·fresh复验25/25 PASS(第741次)+交付物全量+基础设施5项确认+pretrain无待答+WAITING=0）已归档 → daily-memories-data/2026-11-28.md
> 📦 R985 心跳（2026-11-27 20:3x·fresh复验25/25 PASS(第740次)+交付物全量+基础设施5项确认+pretrain iter=345510·350k ETA~05:35·WAITING=0）已归档 → daily-memories-data/2026-11-27.md
> 📦 R984 心跳（2026-11-27 20:2x·fresh复验25/25 PASS(第739次)+交付物全量+基础设施5项确认+pretrain iter=345510·350k ETA~05:35·WAITING=0）已归档 → daily-memories-data/2026-11-27.md
> 📦 R983 心跳（2026-11-27 20:1x·fresh复验25/25 PASS(第738次)+交付物全量+基础设施5项确认+pretrain iter=345380·350k ETA~05:50·WAITING=0）已归档 → daily-memories-data/2026-11-27.md
> 📦 R977 心跳（2026-11-28 02:0x·fresh复验25/25 PASS(第732次)+交付物全量+基础设施5项确认+pretrain iter=345060·350k ETA~05:30·WAITING=0）已归档 → daily-memories-data/2026-11-28.md
> 📦 R976 心跳（2026-11-27 20:0x·fresh复验25/25 PASS(第731次)+用户令11-27 4项职责复查全✅+交付物全量+基础设施5项确认+pretrain无待答·WAITING=0）已归档 → daily-memories-data/2026-11-27.md
> 📦 R975 心跳（2026-11-27 19:3x·fresh复验25/25 PASS(第730次)+交付物全量+基础设施5项确认+pretrain iter=345060·WAITING=0）已归档 → daily-memories-data/2026-11-27.md
> 📦 R973 心跳（2026-11-27 19:0x·fresh复验25/25 PASS(第728次)+交付物全量+基础设施5项确认+pretrain iter=344910·WAITING=0）已归档 → daily-memories-data/2026-11-27.md
> 📦 R972 心跳（2026-11-28 01:3x·fresh复验25/25 PASS+交付物全量+基础设施确认+pretrain iter=344820·WAITING=0）已归档 → daily-memories-data/2026-11-28.md
> 📦 R971 心跳（2026-11-28 01:0x·fresh复验25/25 PASS+交付物全量+基础设施确认+pretrain iter=344820·WAITING=0）已归档 → daily-memories-data/2026-11-28.md
> 📦 R936~R970 心跳（2026-11-27 15:30~2026-11-28 00:3x·多次fresh复验25/25 PASS+交付物全量+基础设施4项确认+pretrain ALL READY无待答·iter≈343100~344820·WAITING=0）已批量归档 → daily-memories-data/2026-11-27.md
> 📦 R898~R935 心跳（2026-11-27·多次fresh复验25/25 PASS+交付物全量+shim实机确认+pretrain无待答·WAITING=0）已批量归档 → daily-memories-data/2026-11-27.md

> 📦 致 pretrain 线回复（2026-11-27 11:0x，回应 #3475/#3476 patch 不兼容 → Bridge Edition shim 已解决）已归档 → daily-memories-data/2026-11-27.md。**结论**：pretrain #3477/#3479/#3481 已确认 ALL VERIFIED READY，此回复已闭环。
> 📦 R836~R869 心跳（2026-11-27 01:47~08:50·多次巡检+fresh复验8/8+7/7 PASS zero_overlap=0·iter≈336k~340k·330k eval DONE harness_avg=57.50%·/nas_user 42T余✅·所有用户令已交付·WAITING=0）已批量归档 → daily-memories-data/2026-11-27.md
> 📦 R825~R835 心跳（2026-11-26 23:52~2026-11-27 01:30·例行巡检+blendswitch复验全PASS zero_overlap=0·iter≈335k~336k·330k eval RUNNING·/nas_user 42T余✅·WAITING=0）已批量归档 → daily-memories-data/2026-11-26.md
> 📦 R825 心跳（2026-11-26 23:52·例行巡检+blendswitch第616次fresh复验8/8 PASS+integration 7/7 PASS zero_overlap=0·iter≈335,790 step avg10≈7.40s·330k eval RUNNING·.12 load25.61/25.78/25.64·0下载·/nas_user 42T余✅·git synced·所有用户令已交付·WAITING=0）已归档 → daily-memories-data/2026-11-26.md
> 📦 R748~R824 心跳（例行巡检+blendswitch第539~615次复验全8/8(后7/7)PASS zero_overlap=0·iter329,174~335,700·step7.20~8.09s·latest ckpt 332k→334k·322k~328k eval DONE harness_avg55~58.88%·330k eval KILLED/BLOCKED/RUNNING·.12 load20~32·0下载进程·/nas_user 42T余(63%)>5T红线✅·git synced各HEAD=origin/main·所有用户令已交付·WAITING=0）已批量归档 → daily-memories-data/2026-11-26.md

> 📦 R747~R695 心跳（例行巡检+blendswitch第487~538次复验7/7 PASS zero_overlap=0·iter≈325,400~328,705 step7.3-7.5s·322k eval DONE harness_avg=56.88%·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R693 心跳（例行巡检+blendswitch第485次复验7/7 PASS zero_overlap=0·iter≈325,300 step7.5s·322k eval DONE harness_avg=56.88%·.12 load27.53/26.53/26.14·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R691 心跳（例行巡检+blendswitch第483次复验7/7 PASS zero_overlap=0·iter≈325,150 step7.5s·322k eval DONE harness_avg=56.88%·.12 load25.20/25.81/26.03·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R690 心跳（例行巡检+blendswitch第482次复验7/7 PASS zero_overlap=0·iter≈325,100 step7.5s·322k eval DONE harness_avg=56.88%·.12 load26.74/26.02/26.13·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R686 心跳（例行巡检+blendswitch第478次复验7/7 PASS zero_overlap=0·iter≈324,850 step7.5s·322k eval DONE harness_avg=56.88%·.12 load26.11/26.03/26.04·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R685 心跳（例行巡检+blendswitch第477次复验7/7 PASS zero_overlap=0·iter≈324,800 step7.5s·322k eval DONE harness_avg=56.88%·.12 load25.95/26.10/26.12·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R684 心跳（例行巡检+blendswitch第476次复验7/7 PASS zero_overlap=0·iter≈324,800 step7.53s·322k eval DONE harness_avg=56.88%·.12 load27.18/26.31/26.13·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R683 心跳（例行巡检+blendswitch第475次复验7/7 PASS zero_overlap=0·iter≈324,700 step7.53s·322k eval DONE harness_avg=56.88%·.12 load27.38/26.53/26.23·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R682 心跳（例行巡检+blendswitch第474次复验7/7 PASS zero_overlap=0·iter≈324,600 step7.53s·322k eval DONE harness_avg=56.88%·.12 load24.92/25.35/25.86·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R680 心跳（例行巡检+blendswitch第472次复验7/7 PASS zero_overlap=0·iter≈324,000 step7.5s·322k eval DONE harness_avg=56.88%·.12 load25.79/26.57/26.48·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R678 心跳（例行巡检+blendswitch第470次复验7/7 PASS zero_overlap=0·iter≈324,000 step7.5s·322k eval DONE harness_avg=56.88%·.12 load25.21/25.91/26.23·0下载进程）已归档 → daily-memories-data/2026-11-26.md
> 📦 R674 心跳（例行巡检+blendswitch第466次复验7/7 PASS zero_overlap=0·iter≈322,820 step7.53s·322k eval DONE harness_avg=56.88%·.12 load24.83/25.50/25.42·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R673 心跳（例行巡检+blendswitch第465次复验7/7 PASS zero_overlap=0·iter≈322,820 step7.53s·322k eval DONE harness_avg=56.88%·.12 load26.13/25.49/25.33·0下载进程）已归档 → daily-memories-data/2026-11-25.md

> 📦 R668 心跳（例行巡检+blendswitch第460次复验7/7 PASS zero_overlap=0·iter≈322,820 step7.53s·322k eval DONE harness_avg=56.88%·.12 load28.20/26.02/25.88·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R667 心跳（例行巡检+blendswitch第459次复验7/7 PASS zero_overlap=0·iter≈323,280 step7.53s·322k eval DONE harness_avg=56.88%·.12 load27.49/26.78/26.24·0下载进程）已归档 → daily-memories-data/2026-11-25.md
> 📦 R642~R665 心跳（例行巡检+blendswitch第434~457次复验全7/7 PASS zero_overlap=0·iter321,160~323,120·step7.21~7.53s·320k/322k eval DONE/RUNNING harness_avg=54.62~56.88%·.12 load24~29·0下载进程）已批量归档 → daily-memories-data/2026-11-25.md
> 📦 R611~R639 心跳（例行巡检+blendswitch第403~431次复验全7/7 PASS·iter319,300~321,100·step7.22~8.53s·318k/320k eval DONE harness_avg=54.62~56.25%·.12 load24~29·0下载进程）已批量归档 → daily-memories-data/2026-11-25.md

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
PHASE:        S2前置全完成 — 用户令11-27 4项职责复查全✅ + 方案F Bridge Edition交付✅(shim+launcher+cursor_offsets+SWITCH_RUNBOOK 9节+25/25 PASS zero_overlap=0) + 交付物全量复查✅ + 基础设施5项确认✅ + pretrain无待答 → WAITING=0
已完成:       ✅PC-1~PC-5;✅方案F blendswitch Bridge Edition(14文件全完整);✅bridge 10/10+standalone 8/8+integration 7/7 PASS zero_overlap=0(第742次fresh复验);✅SWITCH_RUNBOOK.md 9节完整;✅基础设施确认(shim@BAIZE_TRAIN_CODE 4226B+train.sh L202/L206+launcher L306+blend_s1+s2 TSV+cursor_offsets_350k.json);✅pretrain无待答
当前动作:     R987:第742次fresh复验全PASS(8/8+10/10+7/7 zero_overlap=0)+交付物完整性复查✅+基础设施5项确认✅+pretrain无待答(grep=0)+ckpt=344000→WAITING=0
下一步:       ①保持复验节奏直到350k切换完成(ETA~05:30 on 11-28) ②pretrain执行冷切换时配合答疑
阻塞:         无(全部前置完成;交付物全完整;pretrain无待答;基础设施全确认;无后台任务)
ERROR_COUNT:  0
未完成指令:   无(全部用户令已交付)→WAITING=0
```

> 📦 唤醒1521-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC巡检+Agent/IFM下载进度+Code-Reasoning重启+IFM多轮巡检,详见日文件）

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒1554-1557（2026-11-20~21, v3报告刷新+MegaMath-web分词巡检+Nemotron/finemath/Math-Reasoning/Code-Reasoning下载+分词进度,共4轮）已归档 → daily-memories-data/2026-11-20.md~2026-11-21.md

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
> 关键结论：①base分词22.05B tok✅ ②SFT-2605 20.97B+Agent-2609 全4shard✅ ③S0a 2.2B单臂浪费~100 GPU·h→改道proxy BO搜索 ④proxy模型92.7M(d=512/L=14)标定s/step=1.5s ⑤smoke te