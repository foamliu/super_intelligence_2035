# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0
> 🛑 **【运维通告 · 2026-11-02 19:51】S1 已由 ops 中继重启并在跑**：`bash scripts/train.sh s1 --nodes 2`，launcher pid **4163528**，从 **ckpt 58000** 续（19:55:40 起 iter **58010**→58030，7.0–7.2 s/step ≈**582K tok/s**，双机 16 卡 **98–100%**、~75GB/卡、~690W）。⇒ **GPU 不再空闲**：🚫 严禁再起任何训练/GPU 评测进程（会双写 ckpt 或 OOM）；"GPU idle → 2.5h 评测"的结论已过期。原 **18:39:51 SIGKILL / 18:50:18 SIGBUS** 的现场日志已归档为 `/tmp/baize_s1_baize2b_worker.log.crash_1102_1839` 与 `..._master.log.crash_1102_1839`（🚫 勿删，待 root 查 dmesg 定 OOM vs 误杀）。CPU 评测继续但**必须降载**：`OMP_NUM_THREADS≤8` + `nice -n 19` + 每机并发 ≤2，**禁止 `pkill python`**（18:39 训练被 -9 的疑似原因）。另：本次 resume **未恢复 scheduler**，LR 从 warmup 重来（58010=5e-6，每 10 步 +5e-6，约 2000 步/3.9h 后回 1e-3）——实验日志须记一笔。详见 `BAIZE_PRETRAIN_2B_TASK.md` 顶部运维令。

> 🆕 2026-11-03 13:00 #1228：**📊 CPU eval·71轮监控——.12 evals ~95-96% ETA~42-54min(→done~13:40-13:52)；.29 iter_30000 236/2599(9.1%,~17.3s/it,ETA~11.4h→done~00:15 Nov4)、iter_50000 427/2599(16.4%,~17.1s/it,ETA~10.3h→done~23:10)；CPU .12~24%/.29~15% <<80%。✅ S1 健康 iter 66750/loss 2.099/lr=1e-3 stable。iter_10000 ✅ Avg=0.499(arc_c=0.29/arc_e=0.49/boolq=0.61/hs=0.36/obqa=0.20/piqa=0.72/sciq=0.79/wg=0.54)。未完成指令：有**。
> **① .12 evals 即将完成**：iter_20000 PID3729981 2472/2599(95.1%) ~25.7s/it elapsed14h58m ETA~54min→done~13:52；iter_40000 PID3898654 2488/2599(95.7%) ~22.9s/it elapsed14h56m ETA~42min→done~13:40。CPU .12: %Cpu~23.9%(8.3us+14.4sy+1.2ni), load38.68, 76.1%idle, <<80%。
> **② .29 evals overnight**：iter_30000 PID1459766 236/2599(9.1%) ~17.3s/it elapsed1h33m ETA~11.4h→done~00:15 Nov4；iter_50000 PID2024390 427/2599(16.4%) ~17.1s/it elapsed2h23m ETA~10.3h→done~23:10。CPU .29: %Cpu~15.1%(5.4us+8.5sy+1.2ni), load34.77, 84.7%idle, <<80%。
> **③ iter_10000 ✅ Avg=0.499**：results.json 已核实，8集 acc 见上。GPU 双机各8卡 100%util/~75GB(训练占用)。
> **📦 体积**：TASK=30602B(29.9KB)/MEMORY=~24KB（均 ≤32KB，无需归档）。
> **下一步**：~13:40-13:52 .12 evals 完成→收集 20000/40000 results.json→.29 双 eval overnight→全部5×8有效后汇总表+HTML报告。未完成指令：有 ⇒ WAITING: 0。



> 📦 §#1155（11-02 20:35, CPU acc=0.0根因+修复）→ daily-memories/2026-11-02.md；**结论**：float32 NaN→bfloat16修复, simple_evaluate重写, sciq limit=4 acc=0.5 PASS。被#1157修正。需要时再读。
> 📦 §#1156（11-02 21:40, CPU ETA报告·sciq-only测速16.44s/req）→ daily-memories/2026-11-02.md；**结论**：推荐limit=100→24h。**⚠️ 被#1157修正**：sciq短序列不代表全部8集，arc_challenge实测45-59s/req（3-4×更慢），真实ETA更长。需要时再读。

> 📦 §#1157（11-02 22:05, CPU eval全量启动+ETA修正）→ daily-memories/2026-11-02.md；**结论**：4 eval启动(limit=100,2599req,~34s/req),ETA~50h≈2天。被#1158监控。需要时再读。
> 📦 §#1158（11-02 22:12, CPU eval监控·ETA修正~3天）→ daily-memories/2026-11-02.md；**结论**：4 eval运行正常,.29~40-50s/req/.12~55-62s/req,ETA~69h≈3天。**⚠️ 被#1159修正**：速度已收敛(.29~33s/.12~43s),ETA修正回~2天。需要时再读。

> 📦 §#1173（11-02 23:43, CPU eval监控·16轮·ETA~10.4-14.5h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.2-16.7s/.12~21.1-21.9s,ETA~10.4-14.5h,S1 iter59930健康。被#1174监控(无变化)。需要时再读。

> 📦 §#1174（11-02 23:48, CPU eval监控·17轮·ETA~10.5-14.1h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.5-17.1s/.12~21.4-21.6s,ETA~10.5-14.1h,S1 iter59970 lr=9.85e-4 warmup爬升中。被#1175监控。需要时再读。

> 📦 §#1154-#1215（11-02 19:55→11-03 08:18, CPU eval监控·1-58轮）→ daily-memories/2026-11-02.md & 2026-11-03.md；**结论**：5 export完成, 4 eval稳定启动, 速度收敛(.29~16s/.12~22s), ETA从~10天下修至.29~2.1h/.12~5.2h, S1 iter59540→64370 warmup完成→lr=1e-3 stable。被#1216监控。需要时再读。
> 📦 §#1216（11-03 08:41, CPU eval监控·59轮）→ daily-memories/2026-11-03.md；**结论**：4 eval正常(.29~85%/.12~69%), ETA .29~1.7h/.12~5.1h, CPU<<80%, S1 iter64540健康。被#1217监控。需要时再读。
> 📦 §#1217（11-03 09:06, CPU eval监控·60轮）→ daily-memories/2026-11-03.md；**结论**：4 eval正常(.29~89%/.12~72%), ETA .29~1.2h/.12~4.7h, CPU<<80%, S1 iter64790健康。被#1218监控。需要时再读。
> 📦 §#1218（11-03 09:27, CPU eval监控·61轮）→ daily-memories/2026-11-03.md；**结论**：4 eval正常(.29~91.8%/.12~73.8%), ETA .29~54-57min/.12~4h, CPU<<80%, S1 iter64940健康。被#1219监控。需要时再读。
> 📦 §#1219（11-03 09:48, CPU eval监控·62轮）→ daily-memories/2026-11-03.md；**结论**：4 eval正常(.29~95%/.12~76%), ETA .29~37-40min/.12~3.8h, CPU<<80%, S1 iter65130健康。被#1220监控。需要时再读。
> 📦 §#1220（11-03 10:10, CPU eval监控·63轮）→ daily-memories/2026-11-03.md；**结论**：.29 evals 97-98%即将完成, .12 78% ETA~3.4h, S1 iter65300健康。被#1221接续。需要时再读。

> 🆕 2026-11-03 12:52 #1227：**📊 CPU eval·70轮监控——.12 evals ~94-95% ETA~50-54min(→done~13:42-13:46)；.29 iter_30000 208/2599(8%,~17.5s/it,ETA~11.4h)、iter_50000 398/2599(15%,~17.5s/it,ETA~10.4h→done~23:20)；CPU .29~14.3%/.12~17.4% <<80%。✅ S1 健康 iter 66700/loss 2.106/lr=1e-3。未完成指令：有**。
> **① .12 evals**：iter_20000 2451/2599(94.3%) ~22.5s/it ETA~54min→done~13:46；iter_40000 2466/2599(94.9%) ~22.5s/it ETA~50min→done~13:42。CPU .12: %Cpu~17.4%(5.6us+11.0sy+0.8ni), load39, 82.4%idle, <<80%。
> **② .29 iter_30000**：PID 1459766, 208/2599(8.0%), elapsed~1h17m, ~17.5s/it(已脱离慢启动), ETA~11.4h→done~00:15 Nov4。config已修复(mamba_dt_limit已删, rope_theta=1M)。
> **③ .29 iter_50000**：PID 2024390, 398/2599(15.3%), elapsed~2h13m, ~17.5s/it, ETA~10.4h→done~23:20。CPU .29: %Cpu~14.3%(4.8us+8.2sy+1.3ni), load36, 85.6%idle, <<80%。
> **④ iter_10000 results✅**：arc_c=0.29/arc_e=0.49/boolq=0.61/hs=0.36/obqa=0.20/piqa=0.72/sciq=0.79/wg=0.54。**Avg=0.5000**（已核实 results.json）。
> **⑤ S1 状态**：iter 66700/700k(9.53%), loss 2.089-2.107, 0 NaN, 0 skip, ~7.0s/step, ~606K tok/s, lr=1e-3 stable, ckpt@66000(next@68000)。
> **📦 体积**：TASK=30602B(29.9KB) / MEMORY=23354B(22.8KB)（均 ≤32KB，无需归档）。
> **下一步**：~13:42 .12 evals完成→收集 20000/40000 results.json→.29 双 eval overnight(iter_50000~23:20, iter_30000~00:15 Nov4)→全部5×8有效结果后汇总表+HTML报告。未完成指令：有。
> 📦 §#1226（11-03 12:30, CPU eval·69轮）→ daily-memories/2026-11-03.md；**结论**：.12~92-93% ETA~1.2h, .29 iter_30000 5%/iter_50000 12%~17s/it, iter_10000✅Avg=0.50, S1 iter66510。被#1227监控。需要时再读。
> 📦 §#1225（11-03 12:10, CPU eval·68轮）→ daily-memories/2026-11-03.md；**结论**：.12~90% ETA~13:45, .29 iter_30000慢启动(0.8%), iter_50000 9.5%~17s/it, iter_10000✅Avg=0.50, S1 iter66330。被#1226监控。需要时再读。
> 📦 §#1224（11-03 11:47, CPU eval·67轮）→ daily-memories/2026-11-03.md；**结论**：.12~88% ETA~13:40, .29 iter_30000启动慢启动, iter_50000降速17→44s/it, iter_10000✅Avg=0.50, S1 iter66140。被#1225监控。需要时再读。
> 📦 §#1223（11-03 11:25, CPU eval·66轮）→ daily-memories/2026-11-03.md；**结论**：iter_30000重跑启动(.29 config修复), .29双eval CPU~14%, .12~86% ETA~13:40, iter_10000✅, S1 iter65930。被#1224监控。需要时再读。
> 📦 §#1222（11-03 11:02, CPU eval·65轮）→ daily-memories/2026-11-03.md；**结论**：.29 iter_50000跑通(1.6%), .12~85%, iter_30000 config修复✅, iter_10000✅。被#1223监控(已启动iter_30000重跑)。需要时再读。
> 📦 §#1221（11-03 10:42, CPU eval·64轮）→ daily-memories/2026-11-03.md；**结论**：.29 evals完成(10000✅+30000❌), iter_50000启动, iter_30000 config修复, .12 ~81%。被#1222监控。需要时再读。
> 📦 §#1151（11-02 12:55, S1健康监控iter55140/loss~2.114/0NaN/~592K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter55140(7.88%), loss~2.114稳态, grad-norm 0.088-0.099(极稳无spike), ~592K tok/s, ckpt@iter_54000(saved@10:41, next@56000)。被#1152监控。需要时再读。
> 📦 §#1150（11-02 12:35, S1健康监控iter54980/loss~2.105/0NaN/~601K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter54980(7.85%), loss~2.105稳态, grad-norm 0.082-0.103(极稳无spike), ~601K tok/s, ckpt@iter_54000(saved@10:41, next@56000)。被#1151监控。需要时再读。
> 📦 §#1148（11-02 11:54, S1健康监控iter54620/loss~2.099/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter54620(7.80%), loss~2.099稳态, grad-norm 0.086-0.099(极稳无spike), ~605K tok/s, ckpt@iter_54000(saved@10:41, next@56000)。被#1149监控。需要时再读。
> 📦 §#1147（11-02 11:36, S1健康监控iter54470/loss~2.102/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter54470(7.78%), loss~2.102稳态, grad-norm 0.082-0.110(极稳无spike), ~605K tok/s, ckpt@iter_54000(saved@10:41, next@56000)。被#1148监控。需要时再读。
> 📦 §#1146（11-02 11:18, S1健康监控iter54310/loss~2.111/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter54310(7.76%), loss~2.111稳态, grad-norm 0.089-0.115(极稳无spike), ~603K tok/s, ckpt@iter_54000(saved@10:41, next@56000)。被#1147监控。需要时再读。
> 📦 §#1145（11-02 11:00, S1健康监控iter54150/loss~2.114/0NaN/~607K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter54150(7.74%), loss~2.114稳态, grad-norm 0.084-0.168(极稳无spike), ~607K tok/s, ckpt@iter_54000(saved@10:41, next@56000)。被#1146监控。需要时再读。
> 📦 §#1143（11-02 10:20, S1健康监控iter53810/loss~2.115/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter53810(7.69%), loss~2.115稳态, grad-norm 0.086-0.470(minor spike 0.470@53750已恢复), ~605K tok/s, ckpt@iter_52000(next@54000)。被#1144监控。需要时再读。
> 📦 §#1142（11-02 10:01, S1健康监控iter53650/loss~2.116/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter53650(7.66%), loss~2.116稳态, grad-norm 0.087-0.112(极稳无spike), ~605K tok/s, ckpt@iter_52000(next@54000)。被#1143监控。需要时再读。
> 📦 §#1141（11-02 09:40, S1健康监控iter53460/loss~2.122/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter53460(7.64%), loss~2.122稳态, grad-norm 0.088-0.124(极稳无spike), ~603K tok/s, ckpt@iter_52000(next@54000)。被#1142监控。需要时再读。
> 📦 §#1140（11-02 09:25, S1健康监控iter53310/loss~2.125/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter53310(7.61%), loss~2.125稳态, grad-norm 0.091-0.220(极稳无spike), ~603K tok/s, ckpt@iter_52000(next@54000)。被#1141监控。需要时再读。
> 📦 §#1120-#1139（11-02 03:28-09:02, S1健康监控iter50250-53140, 共20轮）→ daily-memories/2026-11-02.md；**结论**：S1全程健康, loss~2.11-2.13稳态, 0 NaN, ~603-607K tok/s, grad-norm 0.08-0.22(偶发瞬态spike均自恢复), ckpt iter_50000→52000(next@54000)。被#1140+后续监控。需要时再读。
> 📦 §#1119（11-02 03:11, S1健康监控iter50100/loss~2.127/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter50100(7.16%), loss~2.127稳态, grad-norm 0.092-0.173(minor spike 1.843@50020已恢复), ~605K tok/s, ckpt@iter_50000(已保存, next@52000)。被#1120监控。需要时再读。
> 📦 §#1118（11-02 02:55, S1健康监控iter49950/loss~2.142/0NaN/~598K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter49950(7.13%), loss~2.142稳态, grad-norm 0.087-0.406(minor spike 0.406@49840已恢复), ~598K tok/s, ckpt@iter_48000→50000(已保存)。被#1119监控。需要时再读。
> 📦 §#1117（11-02 02:35, S1健康监控iter49800/loss~2.124/0NaN/~602K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter49800(7.11%), loss~2.124稳态, grad-norm 0.087-0.251(minor spike 0.649@49740已恢复), ~602K tok/s, ckpt@iter_48000(next@50000)。被#1118监控。需要时再读。
> 📦 §#1116（11-02 02:17, S1健康监控iter49640/loss~2.124/0NaN/~602K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter49640(7.09%), loss~2.124稳态, grad-norm 0.083-0.134极稳无spike, ~602K tok/s, ckpt@iter_48000(next@50000)。被#1117监控。需要时再读。
> 📦 §#1115（11-02 01:58, S1健康监控iter49480/loss~2.128/0NaN/~604K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter49480(7.07%), loss~2.128稳态, grad-norm 0.087-0.286(minor spike 2.180@49280已恢复), ~604K tok/s, ckpt@iter_48000(next@50000)。被#1116监控。需要时再读。
> 📦 §#1114（11-02 01:39, S1健康监控iter49320/loss~2.139/0NaN/~606K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter49320(7.05%), loss~2.139稳态, grad-norm 0.083-0.286(minor spike 2.180@49280已恢复), ~606K tok/s, ckpt@iter_48000(next@50000)。被#1115监控。需要时再读。
> 📦 §#1113（11-02 01:22, S1健康监控iter49170/loss~2.121/0NaN/~606K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter49170(7.03%), loss~2.121稳态, grad-norm 0.085-0.162极稳无spike, ~606K tok/s, ckpt@iter_48000(next@50000)。被#1114监控。需要时再读。
> 📦 §#1112（11-02 01:02, S1健康监控iter49000/loss~2.122/0NaN/~607K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter49000(7.00%), loss~2.122稳态, grad-norm 0.090-0.117极稳无spike, ~607K tok/s, ckpt@iter_48000(next@50000)。被#1113监控。需要时再读。
> 📦 §#1111（11-02 00:43, S1健康监控iter48840/loss~2.130/0NaN/~606K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter48840(6.98%), loss~2.130稳态, grad-norm 0.089-0.157(minor spike 1.130@48560已恢复), ~606K tok/s, ckpt@iter_48000(next@50000)。被#1112监控。需要时再读。
> 📦 §#1110（11-02 00:25, S1健康监控iter48680/loss~2.136/0NaN/~606K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter48680(6.95%), loss~2.136稳态, grad-norm 0.090-0.209(minor spike 1.130@48560已恢复), ~606K tok/s, ckpt@iter_48000(next@50000)。被#1111监控。需要时再读。
> 📦 §#1109（11-02 00:08, S1健康监控iter48530/loss~2.116/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter48530(6.93%), loss~2.116稳态, grad-norm 0.084-1.627(minor spike 1.627@48460已恢复), ~605K tok/s, ckpt@iter_48000(next@50000)。被#1110监控。需要时再读。
> 📦 §#1108（11-01 23:49, S1健康监控iter48370/loss~2.114/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter48370(6.91%), loss~2.114稳态, grad-norm 0.087-0.184极稳无spike, ~605K tok/s, ckpt@iter_48000(next@50000)。被#1109监控。需要时再读。
> 📦 §#1107（11-01 23:31, S1健康监控iter48220/loss~2.113/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter48220(6.89%), loss~2.113稳态, grad-norm 0.089-0.150极稳无spike, ~605K tok/s, ckpt@iter_48000(next@50000)。被#1108监控。需要时再读。
> 📦 §#1106（11-01 23:13, S1健康监控iter48060/loss~2.123/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter48060(6.87%), loss~2.123稳态, grad-norm 0.088-0.187极稳无spike, ~605K tok/s, ckpt@iter_48000(next@50000)。被#1107监控。需要时再读。
> 📦 §#1105（11-01 22:55, S1健康监控iter47910/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47910(6.84%), loss~2.13稳态, grad-norm 0.086-0.225极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1106监控。需要时再读。
> 📦 §#1104（11-01 22:38, S1健康监控iter47740/loss~2.131/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47740(6.82%), loss~2.131稳态, grad-norm 0.087-0.143极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1105监控。需要时再读。
> 📦 §#1103（11-01 22:18, S1健康监控iter47580/loss~2.122/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47580(6.80%), loss~2.122稳态, grad-norm 0.083-0.181极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1104监控。需要时再读。
> 📦 §#1102（11-01 22:00, S1健康监控iter47430/loss~2.127/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47430(6.77%), loss~2.127稳态, grad-norm 0.091-0.181极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1103监控。需要时再读。
> 📦 §#1101（11-01 21:42, S1健康监控iter47270/loss~2.122/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47270(6.75%), loss~2.122稳态, grad-norm 0.086-0.137极稳(minor spike 0.987@47220已恢复), ~607K tok/s, ckpt@iter_46000(next@48000)。被#1102监控。需要时再读。
> 📦 §#1100（11-01 21:25, S1健康监控iter47120/loss~2.122/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter47120(6.73%), loss~2.122稳态, grad-norm 0.086-0.112极稳(minor spike 0.947@46910已恢复), ~607K tok/s, ckpt@iter_46000(next@48000)。被#1101监控。需要时再读。
> 📦 §#1099（11-01 21:07, S1健康监控iter46970/loss~2.125/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46970(6.71%), loss~2.125稳态, grad-norm 0.087-0.102极稳(minor spike 0.947@46910已恢复), ~605K tok/s, ckpt@iter_46000(next@48000)。被#1100监控。需要时再读。
> 📦 §#1096（11-01 20:13, S1健康监控iter46500/loss~2.116/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46500(6.64%), loss~2.116稳态, grad-norm 0.082-0.257极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1097监控。需要时再读。
> 📦 §#1095（11-01 19:55, S1健康监控iter46340/loss~2.119/0NaN/~606K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46340(6.62%), loss~2.119稳态, grad-norm 0.082-0.257极稳无spike, ~606K tok/s, ckpt@iter_46000(next@48000)。被#1096监控。需要时再读。
> 📦 §#1094（11-01 19:37, S1健康监控iter46190/loss~2.122/0NaN/~606K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46190(6.60%), loss~2.122稳态, grad-norm 0.083-0.151极稳无spike, ~606K tok/s, ckpt@iter_46000(next@48000)。被#1095监控。需要时再读。
> 📦 §#1093（11-01 19:18, S1健康监控iter46030/loss~2.118/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter46030(6.58%), loss~2.118稳态, grad-norm 0.083-0.099极稳无spike, ~605K tok/s, ckpt@iter_46000(next@48000)。被#1094监控。需要时再读。
> 📦 §#1092（11-01 19:00, S1健康监控iter45870/loss~2.131/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45870(6.55%), loss~2.131稳态, grad-norm 0.088-0.193 minor spike 0.776@45760已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1093监控。需要时再读。
> 📦 §#1091（11-01 18:43, S1健康监控iter45720/loss~2.129/0NaN/~606K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45720(6.53%), loss~2.129稳态, grad-norm极稳无spike, ~606K tok/s, ckpt@iter_44000(next@46000)。被#1092监控。需要时再读。
> 📦 §#1090（11-01 18:26, S1健康监控iter45570/loss~2.123/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45570(6.51%), loss~2.123稳态, grad-norm 0.084-0.408 minor无spike, ~607K tok/s, ckpt@iter_44000(next@46000)。被#1091监控。需要时再读。
> 📦 §#1089（11-01 18:06, S1健康监控iter45410/loss~2.123/0NaN/~607K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45410(6.49%), loss~2.123稳态, grad-norm极稳无spike, ~607K tok/s, ckpt@iter_44000(next@46000)。被#1090监控。需要时再读。
> 📦 §#1087（11-01 17:30, S1健康监控iter45090/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter45090(6.44%), loss~2.13稳态, grad-norm minor spike 0.335@45040已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1088监控。需要时再读。
> 📦 §#1086（11-01 17:11, S1健康监控iter44930/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter44930(6.42%), loss~2.13稳态, grad-norm spike 2.352@44720单步瞬态已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1087监控。需要时再读。
> 📦 §#1085（11-01 16:54, S1健康监控iter44780/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter44780(6.40%), loss~2.13稳态, grad-norm spike 2.352@44720单步瞬态已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1086监控。需要时再读。
> 📦 §#1084（11-01 16:37, S1健康监控iter44630/loss~2.13/0NaN/~605K tok/s）→ daily-memories/2026-11-01.md；**结论**：S1健康iter44630(6.38%), loss~2.13稳态, grad-norm minor spike 0.704@44590已恢复, ~605K tok/s, ckpt@iter_44000(next@46000)。被#1085监控。需要时再读。
> 📦 §#1083及更早流水（11-01 16:17前, iter≤44470, 含S1监控链#1077~#1083）均已归档 → daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt从iter_38000递进至iter_44000; decay 5000步CS8=58.97%; 论文6页ERR=0。需要时再读 daily-memories/2026-11-01.md。
> 📦 §#1076及更早流水（11-01 14:10前, iter≤43360, 含S1监控链#1068~#1076、#1067及更早）均已归档 → daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt从iter_38000递进至iter_42000; decay 5000步CS8=58.97%; 论文6页ERR=0; baize-llm项目目录就绪。需要时再读 daily-memories/2026-11-01.md。
> 📦 §#1067及更早流水（11-01 11:26前, iter≤41950, 含S1监控链#1044~#1067、#1043及更早）均已归档 → daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt从iter_38000递进至iter_42000; decay 5000步CS8=58.97%; 论文6页ERR=0; baize-llm项目目录就绪。需要时再读 daily-memories/2026-11-01.md。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实时日志（NFS `$OUTPUT_DIR/...train.log` 是 .12 旧日志，亦不可作判据，见 16:4x）。
- transformer_engine 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8 / megatron-core 0.16.1 / mamba-ssm 2.2.6.post3（P-9.4 已核实，与任务书预期一致）。
- 结果主文件：R2=`EXP