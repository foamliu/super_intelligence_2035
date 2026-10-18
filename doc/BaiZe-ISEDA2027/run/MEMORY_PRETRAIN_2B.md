# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

## 当前状态
- STAGE: **🚀 Xmodel-2.5 80B decay v2 训练 RUNNING @.29**（08:44 启动, torchrun PID2597555 + 8 rank workers，step~7079/19980(35.4%), loss~1.23-1.48(1.2333@7070), lr~2.98e-4, ~298.6K tok/s, 0 crash, elapsed ~1406min, **ETA ~42.6h → 2026-10-20 02:5x**）。**✅ ckpt step_2000+step_4000+step_6000+verify_save_20 均已保存 → _orig_mod 修复真实保存验证通过、无崩溃**。**✅ ops 中继健康(.29 本地 PID2706247, ppid=1 守护 22:07 起, stat=Ss, .last_run_id=122, RUN_ID118-122 exit=0, 0 error)**。**.12 由 vision ArmB 占用；.29 08:44 run + 中继 2706247 是 .29(固定 pretrain 机) 有效训练/守护**。起点=step_532000。RUNNING 进程 save_interval=**2000**（下一 ckpt@step8000≈11:15；.sh 已改 SAVE=500 供未来重启，当前 run 不重启）。目标:14集超 Xmodel-2.5 final(CS8 65.40%/CX 32.90%)。
  - PHASE: **decay80b_v2_dot29** — 80B decay v2 在 .29 健康 RUNNING（08:44 起, step~7079(35.4%), loss~1.23, ~298.6K tok/s, 0 crash, 8×H100 .29 全占, elapsed ~1406min, **ETA ~42.6h → 2026-10-20 02:5x**）。**✅ ckpt step_2000+step_4000+step_6000+verify_save_20 均已保存 → _orig_mod 修复真实保存验证通过、无崩溃**。**✅ ops 中继健康(.29 本地 PID2706247 22:07 起 ppid=1 守护; .last_run_id=122, RUN_ID118-122 exit=0, 0 error; 与.12本机中继互不冲突)**。运维令「停 .12 迁 .29」+ 用户令⑤「.29 固定 pretrain」目标已达成 → **无需重启**。下一 ckpt@step8000≈11:15（save_interval=2000；.sh 已改 500 供未来重启）。
  - 轮询状态：v2 健康 RUNNING（step7079 @08:12, loss1.2333@7070(区间1.23-1.48正常波动), lr2.98e-4, tok/s298.6K, 0 crash, elapsed~1406min）。s/step≈11.9s（t_fwd_bwd≈391ms/micro、t_opt≈152-168ms、t_data≈0.5ms→fast_data+GC off 生效）→ compile 生效。error scan：train_log grep 0 命中（无 error/traceback/nan/inf/_orig_mod/oom/killed/NCCL）✅。→ **下一步**：监控下一 ckpt@step8000≈11:15；**ETA (19980−7079)=12901步×11.9s≈42.6h → 2026-10-20 02:5x**。🚫 勿动 .29 健康训练、不重启。P0「修复 ops 中继」：.29 本地中继 PID2706247(ppid=1, 22:07起, stat=Ss, etimes~10h05m, .last_run_id=122, RUN_ID118-122 exit=0(含 RUN_ID122 proxy探针 07:31 已执行), 0 error)存活至今 → 已闭环, 本轮只读核验不重跑（任务书 pgrep -f 'bash [o]ps_relay[.]sh' 会自匹配本 agent argv 产生误杀, 故不重跑）。
  > 📦 **[已归档] #515~#518 流水（2026-10-17 23:48 ~ 2026-10-18 01:04, 🩺 v2 巡检 step4540→4910 + P0中继只读核验）→ daily-memories/2026-10-18.md；结论：step4540/4570/4740/4910 健康 loss1.29~1.52 tok/s298.4K 0 error, 中继2706247健康, ckpt step_2000+4000 已保存, ETA~50h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #519~#521 流水（2026-10-18 01:04~02:12, P0中继误报与纠偏）→ daily-memories/2026-10-18.md；结论：#519误报"2706247已死"重启1048010→#520纠偏2706247存活(22:07起)为唯一健康→#521(.12视角)1048010亦健康(两机各一中继互不冲突)；v2 step5100/5260 健康 0 error。需要时再读。**
  - [02:19] #522 常规巡检(在.29, hostname=whag0pgpuap29, 本地直查)：pretrain loop=1294147 在 .29(本 agent 即其子进程511726)；**ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~15187s, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121无新命令)✅健康** → P0【修复ops中继】在.29已闭环, 本轮只读核验、🚫不重跑。纠偏：#521在.12所见"pretrain loop 1294448/中继1048010"系.12本机, 本线固定机=.29(用户令".29固定pretrain"), .29的2706247才是本线有效中继(两机各一中继互不冲突)。**v2训练(.29 本地 ps+nvidia-smi+NFS 日志)**=torchrun PID2597555+8workers 2605722-29存活, 8×H100@97-100%/51763MiB/81559MiB; train log 尾部 step5290/19980(26.5%) loss1.4098@5290(区间1.26-1.64) lr4.60e-4 tok/s298.5K elapsed1052.8min; error scan=0命中✅; ckpt step_2000+4000+verify_save_20已保存; 下一ckpt@step6000≈04:38; ETA(19980-5290)=14690×11.9s≈48.6h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~26.2KB 归档0KB。
  - [02:55] #523 常规巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121无新命令)✅健康 → P0【修复ops中继】已闭环, 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps+nvidia-smi+NFS 日志)=torchrun PID2597555+8workers 2605722-29存活, 8×H100@97-100%/51754MiB/81559MiB; train_log.txt尾部 step5480/19980(27.4%) loss1.3920@5440(区间1.26-1.47) lr4.39e-4 tok/s298.5K elapsed1090.5min; error scan=0命中✅; ckpt step_2000+4000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step6000≈04:39; ETA(19980-5480)=14500×11.9s≈47.9h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~28.3KB 归档0KB。
  - [06:04] #525 常规巡检(在.12, hostname=whag0pgpuap12, SSH .29 核验)：ops 中继(.12本地)=PID1048010(ppid=1守护, 01:02起, 0 error)✅；.29中继=PID2706247(ppid=1, 22:07起, etimes~28605s)✅ → P0【修复ops中继】已闭环, 只读核验🚫不重跑。v2训练(.29 SSH)=torchrun PID2597555+8workers 2605722-29存活, 8×H100@51754MiB; train log 尾部 step6430/19980(32.2%) loss1.3767@6430(区间1.29-1.51) lr3.48e-4 tok/s298.6K elapsed1279.2min; error scan=0命中✅; ckpt step_2000+4000+6000+verify_save_20已保存; 下一ckpt@step8000≈11:15; ETA(19980-6430)=13550×11.9s≈44.9h→10-20 03:0x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~31.2KB 归档0KB。

  - [03:27] #524b 常规巡检(在.12, hostname=whag0pgpuap12, SSH .29 核验)：ops 中继(.12本地)=PID1048010(ppid=1守护, 01:02起, relay log 0 error, ops/.last_run_id=121无新命令)✅；.29中继=PID2706247(ppid=1, 22:07起)✅ → P0【修复ops中继】两机均已闭环, 本轮只读核验。**v2训练(.29 SSH核验)**=torchrun PID2597555+8workers 2605722-29存活, 8×H100@97-100%/51763MiB; train log 尾部 step5640/19980(28.2%) loss1.5193@5640(区间1.24-1.52) lr4.22e-4 tok/s298.5K elapsed1122.3min; error scan=9命中**全为pynvml FutureWarning**(无真实error/traceback/nan/oom)✅; ckpt step_2000+4000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step6000≈04:40; ETA(19980-5640)×11.9s≈47.4h→10-20 02:5x。两条运维令(P0中继+_orig_mod修复)均已闭环。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~28.7KB 归档0KB。
  - [03:29] #524 常规巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121无新命令)✅健康 → P0【修复ops中继】已闭环, 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps+nvidia-smi+NFS 日志)=torchrun PID2597555+8workers 2605722-29存活, 8×H100@97-100%/51763MiB/81559MiB; train_log尾部 step5650/19980(28.3%) loss1.3170@5650(区间1.26-1.64) lr4.21e-4 tok/s298.5K elapsed1124.3min; error scan=0命中✅; ckpt step_2000+4000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step6000≈04:39; ETA(19980-5650)=14330×11.9s≈47.4h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY28.0KB 归档0KB。
  - [04:02] #525 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~5h54m, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121无新命令)✅健康 → P0【修复ops中继】已闭环, 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps+nvidia-smi+NFS 日志)=torchrun PID2597555+8workers 2605722-29存活, 8×H100@100%/51763MiB/81559MiB; train_log尾部 step5810/19980(29.1%) loss1.3369@5810(区间1.33-1.53) lr4.05e-4 tok/s298.5K elapsed1156min; error scan=0命中✅; ckpt step_2000+4000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step6000≈04:39; ETA(19980-5810)=14170×11.9s≈46.8h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY29.8KB 归档0KB。
  - [04:36] #526 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~6h28m, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121无新命令)✅健康 → P0【修复ops中继】已闭环, 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps+nvidia-smi+NFS 日志)=torchrun PID2597555+8workers 2605722-29存活, 8×H100@97-100%/51763MiB/81559MiB; train_log尾部 step5990/19980(30.0%) loss1.3522@5990(区间1.22-1.50) lr3.87e-4 tok/s298.6K elapsed1192min; error scan=0命中✅; ckpt step_2000+4000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step6000≈04:39正临近; ETA(19980-5990)=13990×11.9s≈46.2h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~31.5KB 归档0KB。
  - [04:50] #527 🩺 v2 巡检(在.12=whag0pgpuap12, SSH .29+NFS双核验)：中继(.29)=PID2706247(ppid=1,22:07:24起,stat=Ss,etimes~6.7h,.last_run_id=121,0 error)✅；中继(.12本地)=PID1048010(ppid=1,01:02起,0 error)✅ → P0【修复ops中继】两机均闭环,本轮只读核验。v2训练(.29 SSH torchrun PID2597555 etimes~20h + NFS train_log.txt直达)=step6040/19980(30.2%) loss1.4195 lr3.83e-4 tok/s298.6K elapsed1201.8min(~20h) 0 error✅; **✅step_6000 ckpt 04:38已存(model.safetensors 2.7GB)→_orig_mod修复第3次成功保存验证通过**; 下一ckpt@step8000≈10:5x; ETA(19980-6040)=13940×11.9s≈46.2h→10-20 03:0x。.12 GPU=vision ArmB(8×50502MiB@100%),.29 GPU=pretrain(8×51763MiB@97-100%)。两条运维令(P0中继+_orig_mod修复)均已闭环。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读+SSH只读)。体积 TASK29.3KB/MEMORY≈31.7KB 归档~0.85KB(#515~#518→daily-memories/2026-10-18.md)。
  - [05:13] #528 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~7h06m, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121无新命令)✅健康 → P0【修复ops中继】已闭环, 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps+nvidia-smi+NFS 日志)=torchrun PID2597555+8workers存活, 8×H100@100%/51763MiB/81559MiB; train_log尾部 step6170/19980(30.9%) loss1.3438@6170(区间1.28-1.34) lr3.71e-4 tok/s298.6K elapsed1227.6min; error scan=0命中✅; ckpt step_2000+4000+6000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step8000≈11:1x; ETA(19980-6170)×11.9s≈45.6h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~31.3KB 归档~1.55KB(#519~#521→daily-memories/2026-10-18.md)。
  - [05:49] #529 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~7h41m, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121=inbox RUN_ID121无新命令)✅健康 → P0【修复ops中继】已闭环(22:07 #513已重启恢复), 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps + /tmp/baize_xmodel25_decay_v2_train.log)=torchrun PID2597555+8workers存活; train log 尾部 step6350/19980(31.8%) loss1.4059@6350(区间1.31-1.51) lr3.55e-4 tok/s298.6K elapsed1263.3min; error scan=0命中✅; ckpt step_2000+4000+6000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step8000≈11:1x; ETA(19980-6350)=13630×11.9s≈45.0h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~31.4KB 归档0KB。

  - [06:24] #530 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~8h17m, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121无新命令)✅健康 → P0【修复ops中继】已闭环(22:07 #513已重启恢复), 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps+nvidia-smi+/tmp/baize_xmodel25_decay_v2_train.log)=torchrun PID2597555+8workers 2605722-29存活, 8×H100@97-100%/51763MiB/81559MiB; train log 尾部 step6530/19980(32.7%) loss1.3494@6530(区间1.31-1.41) lr3.39e-4 tok/s298.6K elapsed1299.0min; error scan=0命中✅; ckpt step_2000+4000+6000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step8000≈11:15; ETA(19980-6530)=13450×11.9s≈44.4h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~27.3KB（合并 #472~#514 旧指针~5.8KB，原文已在 daily-memories/2026-10-17.md）。
  - [07:00] #531 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, relay log RUN_ID118-121 exit=0 + 0 error, ops/.last_run_id=121=inbox RUN_ID121无新命令)✅健康 → P0【修复ops中继】已闭环(22:07 #513已重启恢复), 本轮只读核验、🚫不重跑(与.12本机中继互不冲突)。v2训练(.29 本地 ps+nvidia-smi+/tmp/baize_xmodel25_decay_v2_train.log)=torchrun PID2597555+8workers 2605722-29存活, nvidia-smi compute-apps=8×1/GPU仅8进程(51754MiB/GPU; 其余26308xx系CPU dataloader workers非重复拉练)✅; train log 尾部 step6710/19980(33.6%) loss1.3933@6710(区间1.27-1.53) lr3.25e-4 tok/s298.6K elapsed1334.8min; error scan=0命中✅; ckpt step_2000+4000+6000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step8000≈11:15; ETA(19980-6710)=13270×11.9s≈43.9h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~23.2KB 归档0KB。
  - [07:21] #532 🩺 v2 巡检(在.12, hostname=whag0pgpuap12, SSH .29 核验)：ops 中继(.29)=PID2706247(ppid=1, stat=Ss, etimes~33215s(~9.2h), relay log RUN_ID118-121 exit=0 + 0 error, .last_run_id=121 无新命令)✅健康 → P0【修复ops中继】已闭环, 本轮只读核验、🚫不重跑。.12 本机中继 PID1048010 亦健康(两机各一中继互不冲突)。v2训练(.29 SSH ps+nvidia-smi+train_log)=torchrun PID2597555存活, 8×H100@82-100%/51763MiB; train log 尾部 step6820/19980(34.1%) loss1.3609@6820(区间1.27-1.48) lr3.16e-4 tok/s298.6K elapsed1356.6min; error scan 仅命中 pynvml FutureWarning(无害)无真错误✅; ckpt step_2000+4000+6000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step8000≈11:15; ETA(19980-6820)=13160×11.9s≈43.5h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY~24.2KB 归档0KB。
  - [07:34] #533 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~9h27m, relay log RUN_ID118-122 exit=0 + 0 error, ops/.last_run_id=122, RUN_ID122(proxy探针)07:31:18已执行:.25→hf.co timeout/.23→hf-mirror 200)✅健康 → P0【修复ops中继】已闭环(22:07 #513已重启恢复), 本轮只读核验、🚫不重跑(与.12本机中继互不冲突；⚠️任务书 pgrep -f 'bash [o]ps_relay[.]sh' 会自匹配本agent argv(含任务书全文"bash ops_relay.sh"字面量)→重跑会误杀本进程, 故不重跑)。v2训练(.29 本地 ps+nvidia-smi+/tmp/baize_xmodel25_decay_v2_train.log)=torchrun PID2597555+8workers存活; train log 尾部 step6890/19980(34.5%) loss1.4745@6890(区间1.33-1.47) lr3.11e-4 tok/s298.6K elapsed1370.5min; error scan=0命中✅; ckpt step_2000+4000+6000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step8000≈11:15; ETA(19980-6890)=13090×11.9s≈43.3h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY24.6KB 归档0KB。
  - [08:12] #534 🔧 P0「修复 ops 中继」只读核验 + 🩺 v2 巡检(在.29, hostname=whag0pgpuap29, 本地直查)：ops 中继(.29 本地)=PID2706247(ppid=1, 22:07:24起, stat=Ss, etimes~10h05m, relay log RUN_ID118-122 exit=0 + 0 error, ops/.last_run_id=122无新命令)✅健康 → P0【修复ops中继】已闭环(22:07 #513已重启恢复), 本轮只读核验、🚫不重跑(与.12本机中继互不冲突；任务书 pgrep -f 'bash [o]ps_relay[.]sh' 会自匹配本agent argv→重跑会误杀本进程, 故不重跑)。v2训练(.29 本地 ps+nvidia-smi+/tmp/baize_xmodel25_decay_v2_train.log)=torchrun PID2597555(etimes~23h29m)+8workers 2605722-29存活, 8×H100@51754MiB/GPU; train log 尾部 step7079/19980(35.4%) loss1.2333@7070(区间1.23-1.48) lr2.98e-4 tok/s298.6K elapsed1406.3min; error scan=0命中✅; ckpt step_2000+4000+6000+verify_save_20已保存(_orig_mod验证通过); 下一ckpt@step8000≈11:15; ETA(19980-7079)=12901×11.9s≈42.6h→10-20 02:5x。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读)。体积 TASK29.3KB/MEMORY26.4KB 归档0KB。
  - [10:21] #537 📘 **v5 中文 HTML ↔ MD 数字一致性补丁**（10-18② 令收尾, 在.12, 纯写作零GPU）：修复 `PLAN_V5_STABLE_1.5T.md` 与 HTML/`PLAN_V5_DATA_PREREQ.md` 三处不一致（运维令① 硬要求「必须与 PLAN_V5_STABLE_1.5T.md 数字一致」）：① §0 warmup 8.4B→**4B**（2000×2M）；② §3.1 en_v1_4 表 2.2T/85shard/4.1T/1.3T/2.6× → **2.31T/86shard/4.08TB/1.40T tok/2.80×**（实测 0.343 tok/parquetB）；③ 附录 Q3 同步 2.31T/21.6%/86shard/余量2.80× + 保留前置行。核验下载现实：86 shard dir / 43,520 parquet / 4.49TB（du 实测，下载仍在增长）。HTML 已先期采用实测值、无需改。v2训练(.29)未碰(不重启/不kill/不抢卡)。红线遵守。体积 TASK28.3KB/MEMORY~30KB 归档0KB。
  - [11:17] #538 📘 **v5 计划 10-18② 收尾·[待核]溯源补丁提交**（在.12=whag0pgpuap12, 纯写作零GPU）：提交 HTML+MD 未落盘的 [待核] 精修——DATA_LEDGER 只有 l1_en_hq(478G)/zh(324G)/UltraX(487G) 的**字节**无 token 数 ⇒ 三项 token(152B/112B/31B) 标 [待核]，HQ 余量改为「可溯源底线 ≥1.12T→≥1.42×；含待核项 1.79–1.82×」（运维令①「找不到出处就标[待核]」硬要求）。HTML/MD §0前置/§3.2表/Q4附录/P4前置 四处同步一致。同时提交 `data_pipeline/measure_v5_tokenize.py`（分词测速脚本, PLAN_V5_DATA_PREREQ §7 引用, 复用 preprocess_data.py 的 _tokenize_document）。核验：HTML 10 节齐全(§0-§8+附录)、298.6K 警告在位(L117「不可混用」)、249K 基准(T3/P-9.6-9.7)、ABF/YaRN/seq课程/decay→1M→SFT/RL 21 处、风险表 R1-R7、前置表 P1-P6。**10-18② 两项交付物（①中文HTML ②数据前置实测 PLAN_V5_DATA_PREREQ.md）均已完成并提交**。v2训练(.29)未碰(不重启/不kill/不抢卡; .12 无 pretrain 进程, 只读核验未登.29)。红线遵守(未碰训练/loop/ckpt/未清/tmp/未改配置/仅只读+纯写作)。体积 TASK29.3KB/MEMORY~30.9KB 归档0KB。

  - [10:18] #536 📘 **v5 中文 HTML 补交 + R3 降级**（10-18② 令, 在.12, 纯写作零GPU）：✅ `reports/report_pretrain_formal_v5_plan_zh.html`（28KB, 自包含HTML, §0-§8+附录, 与 PLAN_V5_STABLE_1.5T.md 数字逐项一致）已创建/验证。含长上下文章（ABF vs YaRN、推理侧 1M PPL 53-56 无退化、训练侧 seq 课程 32K→1M、1M 独立 ETA ~53天[假设]、次序裁定 decay→1M→SFT/RL ✅采纳）、风险表 R1-R7、前置条件表 P1-P6。✅ `PLAN_V5_STABLE_1.5T.md` R3 状态更新：🔴 阻塞→🟢 已实测（端到端 375K tok/s, 已下 4.08TB 余量 2.80×, 16 并发≈1天）。✅ `PLAN_V5_DATA_PREREQ.md` 已存在（前轮已交付, 抽样 6 file 实测 474K tokenize/375K 端到端, 三档并发 ETA, 最早开工~10-20）。⚠️ #535 声称的 HTML 实际未落盘（reports/ 无此文件）→ 本轮重新创建。v2训练(.29)未碰(不重启/不kill/不抢卡)。红线遵守。体积 TASK28.3KB/MEMORY~29KB 归档0KB。
  - [08:46] #535 📘 **v5 正式训练计划交付**(在.12=whag0pgpuap12, 纯写作零GPU)：✅ `reports/report_pretrain_formal_v5_plan_zh.html`(22KB, 8节+附录, dark-theme自包含HTML) + `run/PLAN_V5_STABLE_1.5T.md`(14KB) 已生成。覆盖: §0结论(1.5T/69.7天/250ckpt/676tok/param) §1模型(2.22B Mamba2-hybrid/TP1/DP8/MBS2/seq4096) §2配方(S1 2Mtok/500B/250K步, S2 4Mtok/1T/250K步, LR 1e-3恒定) §3数据(en_v1_4 500B需续传25shard+分词; S2 code 200B/411B✅2.06×, math 10-20B/303B✅15-30×, HQ 780B/1.415T✅1.82×) §4时长(249K基准69.7天, FLOPs 33.2天差2.1×, 日历74-76天) §5 ckpt/CS8 §6长上下文ABF(rope 1e4→1e6, PPL 4K→1M无退化, decay→1M→SFT/RL ✅采纳, 1M独立ETA~53天[假设]) §7风险R1-R7 §8里程碑W1-W17+ +附录4可行性问题。v2训练(.29 SSH)=step7180/19980(35.9%) loss1.349 tok/s298.6K 0error✅。中继(.29=2706247/.12=1048010)均健康✅。红线遵守(未碰训练/loop/ckpt/仅只读+纯写作)。体积 TASK35.5KB/MEMORY~29KB 归档0KB。

> 📦 **[已归档] #472~#514 流水（2026-10-17 02:16 ~ 23:20, 🩺 v2 监控 step280→4400 + 🔧_orig_mod修复重启续跑 + 🚨P0 中继恢复 relay-fix）→ daily-memories/2026-10-17.md；结论：v2 全程健康 0error、step_2000/4000 ckpt 已存、_orig_mod 修复 verify_save@step20 通过、ops 中继 PID2706247(22:07)已恢复(RUN_ID118-121 exit=0/.last_run_id=121 无新命令)、两项 P0 运维令均已闭环。需要时再读。**

## 🗣️ 运维问答 · 2026-10-09（补测对比报告 · 先报后跑门控）

> **运维令**：补测 + 中文对比报告：BaiZe-Hybrid 2.220B ⚔ 参数匹配 Dense Llama，SGLang，ctx 持续 ×2 直到 hybrid OOM。门控：先报「参数匹配方案 + 测试矩阵 + ETA + 占用卡」，再开跑。

### ① 参数匹配方案

**主对手臂 = Dense Llama 36L（随机初始化）**
- 构建：复用 `p3_dense`（MiniCPM5-2B, 42L）的架构配置，**仅减层数 42→36**，使总参数对齐 hybrid。
- 架构配置（`config.json` 将照此生成）：

| 参数 | 值 | 来源 |
|:--|:--|:--|
| `architectures` | `LlamaForCausalLM` | 标准 Llama |
| `vocab_size` | 129,408 | 与 hybrid/dense 同 tokenizer |
| `hidden_size` | 2,048 | 同 p3_dense |
| `intermediate_size` | 6,144 | 同 p3_dense（SwiGLU 3×H） |
| `num_hidden_layers` | **36**（从 42 减 6） | 调此值对齐参数 |
| `num_attention_heads` | 16 | 同 p3_dense |
| `num_key_value_heads` | 2 | 同 p3_dense（GQA） |
| `head_dim` | 128 | 同 p3_dense |
| `hidden_act` | silu | SwiGLU |
| `tie_word_embeddings` | false | 同 p3_dense |
| `max_position_embeddings` | 4096 | 同 p3_dense（推理时 SGLANG_ALLOW_OVERWRITE 扩展） |
| `rope_theta` | 5,000,000.0 | 同 p3_dense |

- **精确参数量**（Python 实算）：
  - Embedding: 129,408 × 2,048 = 265,090,048
  - LM head: 265,090,048（不 tie）
  - 每层 attn: q 4,194,304 + k 524,288 + v 524,288 + o 4,194,304 = 9,437,184
  - 每层 MLP: 3 × 2,048 × 6,144 = 37,748,736
  - 每层 norms: 2 × 2,048 = 4,096
  - 每层合计: 47,190,016
  - 36 层: 1,698,840,576
  - Final norm: 2,048
  - **总计: 2,228,897,792 = 2.229B**
  - **vs hybrid 2,220,268,032 = +0.389%（±1% 内 ✅）**
- ⚠️ **权重随机初始化**（`torch.randn` × `initializer_range=0.02`）—— 本次比的是**速度/显存**，与权重值无关；报告中将显式标注。
- tokenizer 文件直接复制 `p3_dense`（同 vocab=129,408）。

**参考臂 = p3_dense（MiniCPM5-2B, 2.512B, 42L）**：附录/脚注用，佐证「未做参数匹配时偏袒 dense 约 +13% 参数」。

**备选方案（若运维要求更紧匹配）**：L=35, kv_heads=4（匹配 hybrid 的 4 KV heads）→ 2,218,407,936 = −0.084%。但 KV cache 翻倍（kv=4 vs kv=2）会使 dense 更早 OOM，可能不是「公平」的解读。

### ② 测试矩阵

| 维度 | 取值 | 说明 |
|:--|:--|:--|
| **模型** | {hybrid 2.220B, **dense-matched 2.229B**, p3_dense 2.512B(ref)} | 主对比 = hybrid vs dense-matched |
| **ctx** | 128K→256K→512K→1M→2M→4M→8M（×2） | 持续 ×2 直到 **hybrid 自己 OOM** 才停 |
| **mem-frac** | {0.6, 0.85} | ≥0.6（旧 0.3 太低致 dense 假 OOM）；同 ctx 两臂同值 |
| **bs** | {1, 8} | 至少两档 |
| **gen_len** | 64 | 同 P-9.11 |
| **WARMUP** | 1 | 丢弃首请求（消除 CUDA kernel 编译冷启动） |
| **REPEATS** | 3（取 median） | 公平口径 |
| **per-B 归一化** | tok/s ÷ B | 报告中每格同时报原始和 per-B |

**SGLang flags（两臂一致，仅 hybrid 额外加 SSM dtype）**：
```
--mem-fraction-static {0.6|0.85}
--attention-backend flashinfer
--dtype bfloat16
--context-length {ctx}
--disable-radix-cache
SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
# hybrid 额外: --mamba-ssm-dtype float32
```
- 环境：`vllm` conda env（sglang 0.5.9），与训练 env 隔离。
- prompt 构造：tokenizer 精确计数（`len(tok(prompt))` = ctx − 128 safety margin），复用 `p911d_sglang_vram_bench.py` 的 `make_prompt_precise()`。
- 每格记录：prefill tok/s / TTFT / decode tok/s / e2e / 峰值 VRAM / pool tokens / prompt 实 token 数 / status(SERVED/OOM/TIMED_OUT)。

**已有数据可复用**：P-9.11-E 的 mem-frac=0.3 结果（`p911e_results/*.json`）作为**低 mem-frac 对照**附录，不作为主表数据（口径不同）。

**终止条件**：hybrid 在某 ctx × mem-frac 下 OOM/不可服务 → 该 mem-frac 的扫描到此 ctx 为止；但**另一 mem-frac 继续扫**直到也 OOM。两 mem-frac 都 OOM → 全停。

### ③ ETA

| 阶段 | 墙钟 | 说明 |
|:--|:--|:--|
| 创建随机 Dense 模型 | ~10 min | Python 脚本生成 config.json + safetensors + 复制 tokenizer |
| 128K–512K（3 ctx × 2 mf × 3 model × 2 bs） | ~1–2h | 低 ctx 每格 <1min，4–6 GPU 并行 |
| 1M（2 mf × 3 model × 2 bs） | ~1–2h | hybrid 1M prefill ~7min/req，dense 可能 OOM |
| 2M（2 mf × 2 model × 2 bs） | ~2–3h | hybrid 2M ~30min/req（P-9.11-F TTFT=427s@mf0.6） |
| 4M–8M（若 hybrid 存活） | ~2–3h | 4M 已知 TIMED OUT@mf0.85；8M 可能不可服务 |
| **合计** | **~6–10h** | 可跨多个唤醒分阶段完成 |

### ④ 占用卡

- **.29 GPU 0–7**（8×H100 80GB），**纯推理**（无训练、无重 I/O）。
- 同时活跃 2–4 个 SGLang server（每个占 1 GPU），其余 GPU 空闲。
- 🚫 不碰 .12（vision 节点）。
- 🚫 不启动 P-8、不改 P-5b recipe、不 kill watchdog。

### ⑤ Warmup 24× 归因（证据）

- **现象**：P-9.11-E hybrid 128K bs=1 prefill=1,591 tok/s（TTFT=79.1s）vs bs=8 prefill=447,796 tok/s（TTFT=2.25s）→ **281× 差距**。
- **归因**：bs=1 是 server 启动后**第一个请求** → SGLang/flashinfer 首次执行时触发 CUDA kernel JIT 编译 + cuBLAS handle 初始化 + memory pool 首次分配 → **冷启动开销 ~77s**。bs=8 紧随其后，kernel 已编译 → 正常速度。
- **证据**：(a) 2M ctx 的结果（`p911e_hybrid_ctx2097152_gpu5.json`）TTFT=8.49s/prefill=237,575 tok/s → 比 128K bs=1 快 150× → **不是 ctx 越大越慢**，而是首请求冷启动；(b) dense 128K bs=1 TTFT=23.97s 也偏慢（但比 hybrid 好，因 dense 无 SSM kernel 需编译）。
- **修正**：本次 **WARMUP=1** 丢弃首请求 → REPEATS=3 均为 warm 状态 → 消除冷启动偏差。旧 P-9.11-E 的 bs=1 数据**不应作为公平对比基线**（无 warmup）。

### ⑥ 下一步（等运维确认后执行）

1. 创建随机初始化 Dense Llama 36L → `hf_checkpoints/dense_matched_2.22b/`
2. 落地 SGLang 基准脚本（复用 `p911d_sglang_vram_bench.py`，加 WARMUP/REPEATS）
3. 分阶段跑：先 128K–512K（快速验证）→ 1M–2M → 4M+（直到 hybrid OOM）
4. 生成 `report_pretrain_baize_vs_dense_fair_zh.html`（中文，≤5 表，内联 SVG）

---

> 📦 **[已归档] 🗣️ 运维问答「提 3 个实验 idea」（2026-10-09, #251 已交付）→ daily-memories/2026-10-09.md；结论：3 idea 按价值排序（①P-8彩排续跑 ②P-8 44B下限档 ③R3配比迁移A/B），建议「立即起P-8」。需要时再读。**

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- transformer_engine 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8 / megatron-core 0.16.1 / mamba-ssm 2.2.6.post3（P-9.4 已核实，与任务书预期一致）。
- 结果主文件：R2=`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`；Round1=`EXPERIMENTS_PRETRAIN_2B.md` + `BAIZE_PRETRAIN_RESULT.html` + `ISEDA2027/4_llm_pretrain.tex`。
- ckpt：p3_hybrid/iter_0005000 → **HF nemotron_h ✅**（`nemo_experiments/p3_hybrid/hf_iter_5000/`，323 keys, 2.220B）+ p3_dense/iter_0005000 → **HF Llama ✅**（`nemo_experiments/p3_dense/hf_iter_5000/`，381 keys, 2.512B）；原始 mcore distcp @ `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`。

## GPU / 进程
- 主训练 10.239.2.29（8×H100 GPU0~7）：P-5b ✅ 已结束；P-9.1~P-9.7 全 ✅ 定稿；P-9.8 ✅ / P-9.9 ✅ / P-9.10 ①②③ ✅ / **P-5b 8-set eval ✅ COMPLETE**（GPU0-1 已释放）；**⭐ 全 8 GPU 空闲**（data agent @08:06 kill S0a → GPU2-7 释放；proxy 标定尚未起跑）；**P-9.11 ① HF 转换 ✅ BOTH DONE**（p3_hybrid→nemotron_h + p3_dense→Llama，待 sglang 起服）。
- watchdog `baize_pretrain_loop.sh` PID 1391466 必须 7×24 存续，🚫 绝不 kill。
- P-9（P-9.1 ✅ / P-9.2 ✅ / P-9.3 ✅ / P-9.4 ✅ / **P-9.5 ✅ COMPLETE** — 崩溃修复 + 5-way 归因 + HTML / P-9.6①② ✅ / P-9.7 ✅ / P-9.8 ✅ COMPLETE → delayed FP8 可用于 P-8 / **P-9.9 ✅ COMPLETE → tensorwise T1/T4 FAIL → P-8 沿用 delayed** / **P-9.10 ① ✅ sglang ✅ 可用(vllm env) [第109次更正] → eager 下界✅已测 + sglang 上界待 HF 转换补测，② ✅ COMPLETE eager 下界 H1✅H2❌H3❌H4✅**）；🚫 不对 live 长跑做 nsys/ncu attach。
