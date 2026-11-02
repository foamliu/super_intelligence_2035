# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0
> 🛑 **【运维通告 · 2026-11-02 19:51】S1 已由 ops 中继重启并在跑**：`bash scripts/train.sh s1 --nodes 2`，launcher pid **4163528**，从 **ckpt 58000** 续（19:55:40 起 iter **58010**→58030，7.0–7.2 s/step ≈**582K tok/s**，双机 16 卡 **98–100%**、~75GB/卡、~690W）。⇒ **GPU 不再空闲**：🚫 严禁再起任何训练/GPU 评测进程（会双写 ckpt 或 OOM）；"GPU idle → 2.5h 评测"的结论已过期。原 **18:39:51 SIGKILL / 18:50:18 SIGBUS** 的现场日志已归档为 `/tmp/baize_s1_baize2b_worker.log.crash_1102_1839` 与 `..._master.log.crash_1102_1839`（🚫 勿删，待 root 查 dmesg 定 OOM vs 误杀）。CPU 评测继续但**必须降载**：`OMP_NUM_THREADS≤8` + `nice -n 19` + 每机并发 ≤2，**禁止 `pkill python`**（18:39 训练被 -9 的疑似原因）。另：本次 resume **未恢复 scheduler**，LR 从 warmup 重来（58010=5e-6，每 10 步 +5e-6，约 2000 步/3.9h 后回 1e-3）——实验日志须记一笔。详见 `BAIZE_PRETRAIN_2B_TASK.md` 顶部运维令。



> 📦 §#1155（11-02 20:35, CPU acc=0.0根因+修复）→ daily-memories/2026-11-02.md；**结论**：float32 NaN→bfloat16修复, simple_evaluate重写, sciq limit=4 acc=0.5 PASS。被#1157修正。需要时再读。
> 📦 §#1156（11-02 21:40, CPU ETA报告·sciq-only测速16.44s/req）→ daily-memories/2026-11-02.md；**结论**：推荐limit=100→24h。**⚠️ 被#1157修正**：sciq短序列不代表全部8集，arc_challenge实测45-59s/req（3-4×更慢），真实ETA更长。需要时再读。

> 📦 §#1157（11-02 22:05, CPU eval全量启动+ETA修正）→ daily-memories/2026-11-02.md；**结论**：4 eval启动(limit=100,2599req,~34s/req),ETA~50h≈2天。被#1158监控。需要时再读。
> 📦 §#1158（11-02 22:12, CPU eval监控·ETA修正~3天）→ daily-memories/2026-11-02.md；**结论**：4 eval运行正常,.29~40-50s/req/.12~55-62s/req,ETA~69h≈3天。**⚠️ 被#1159修正**：速度已收敛(.29~33s/.12~43s),ETA修正回~2天。需要时再读。

> 📦 §#1173（11-02 23:43, CPU eval监控·16轮·ETA~10.4-14.5h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.2-16.7s/.12~21.1-21.9s,ETA~10.4-14.5h,S1 iter59930健康。被#1174监控(无变化)。需要时再读。

> 📦 §#1174（11-02 23:48, CPU eval监控·17轮·ETA~10.5-14.1h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.5-17.1s/.12~21.4-21.6s,ETA~10.5-14.1h,S1 iter59970 lr=9.85e-4 warmup爬升中。被#1175监控。需要时再读。

> 🆕 2026-11-02 23:55 #1175：**📊 CPU eval 进度监控·18轮——4 eval 全部正常推进，速度稳定，ETA ~10.6-14.7h。✅ S1 warmup 已完成（lr 回 1.0e-3@iter~60010）。lm_eval_results 仍空（4 eval 均未完成）**。
> **① 4 eval 运行正常**（limit=100, 8集, 2599 total req, bfloat16, batch_size=1, nice 19, OMP=8, CUDA_VISIBLE_DEVICES=""）：
> - .29: hf_iter_10000 (PID 992664, **336/2599=12.9%**, 16.81s/req, 已 ~112min, ETA ~10.6h→done~10:30 Nov3) + hf_iter_30000 (PID 1196989, **326/2599=12.5%**, 17.67s/req, 已 ~109min, ETA ~11.2h→done~11:05 Nov3)
> - .12: hf_iter_20000 (PID 3729981, **244/2599=9.4%**, ~22.4s/req, 已 ~112min, ETA ~14.7h→done~14:35 Nov3) + hf_iter_40000 (PID 3898654, **~244/2599=9.4%**, ~22.4s/req, 已 ~109min, ETA ~14.7h→done~14:35 Nov3)
> - hf_iter_50000: 已 export 完成（config.json 1312B + model.safetensors 4.4GB 在位），待空槽（两机均 2/2 满载）。.29 iter_10000 预计 ~10:30 Nov3 先完成→立即启动 50000（.29 空槽，单 ckpt ~12h→done~22:30 Nov3）。
> - ⚠️ lm_eval_results/ 仍空（4 eval 均未跑完，最早 ~10:30 Nov3 才出第一个 results.json）。注：hf_iter_10000/results.json(20:53,9.2KB) 是早期 sciq limit=4 冒烟遗留，非本轮全量结果，将被覆盖。
> **② 速度**：.29 ~16.8-17.7s/req；.12 ~22.4s/req。与#1174(7min前)一致，速度稳定收敛。
> **③ CPU 负载**：.29 load 36.98/224 (~16.5%)；.12 load 35.44/224 (~15.8%) → 均 <<80% 上限，不影响 S1。
> **④ S1 状态**：iter **60030**/700k (8.58%), loss **2.084**, 0 NaN, 0 skip, ~6.9s/step, ~590K tok/s, GPU 8卡 100%/~75GB, lr=**1.0e-3**（✅ warmup 已完成，从 58010 爬升至 ~60010 回到 stable 1e-3，耗时 ~2000 步/~3.9h）。launcher pid 4163528。
> **📦 体积**：TASK=30.6KB / MEMORY=29.4KB（归档 0KB）。
> **下一步**：持续监控；.29 iter_10000 ~10:30 Nov3 完成→立即启动 hf_iter_50000（.29 空槽）→全部 5×8 完成后(~Nov3 22:30)收集 5 个 results.json→汇总表+曲线→生成 reports/report_pretrain_cpu_eval_8sets_zh.html。未完成指令：有。WAITING: 0。
> 📦 §#1172（11-02 23:34, CPU eval监控·15轮·ETA~10.9-14.4h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.7-16.8s/.12~21.3-21.6s,ETA~10.9-14.4h,S1 iter59880健康。被#1173监控(无变化)。需要时再读。
> 📦 §#1171（11-02 23:30, CPU eval监控·14轮·ETA~11-14.5h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.8-16.9s/.12~21.3-21.6s,ETA~11-14.5h,S1 iter59840健康。被#1172监控(无变化)。需要时再读。
> 📦 §#1170（11-02 23:25, CPU eval监控·13轮·ETA~11-15h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.6-16.7s/.12~21.5-22.0s,ETA~11-14.9h,S1 iter59790健康。被#1171监控(无变化)。需要时再读。
> 📦 §#1169（11-02 23:19, CPU eval监控·12轮·ETA~11-14.5h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.6-16.7s/.12~20.5-21.3s,ETA~11-14.5h,S1 iter59740健康。被#1170监控(无变化)。需要时再读。
> 📦 §#1168（11-02 23:13, CPU eval监控·11轮·ETA~11-14.5h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.9-17.0s/.12~21.1-21.3s,ETA~11-14.5h,S1 iter59700健康。被#1169监控(无变化)。需要时再读。
> 📦 §#1167（11-02 23:08, CPU eval监控·10轮·ETA~11-14h稳定）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.6-17.4s/.12~20.7-21.0s,ETA~11-14h,S1 iter59650健康。被#1168监控。需要时再读。
> 📦 §#1166（11-02 23:03, CPU eval监控·9轮·ETA~12-14h）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.6-18.0s/.12~20.7-20.8s,ETA~12-14h,S1 iter59610健康。被#1167监控。需要时再读。
> 📦 §#1165（11-02 22:54, CPU eval监控·8轮·ETA~24h）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~16.8s/.12~20.3s,ETA~24h,S1 iter59540健康。被#1166监控。需要时再读。
> 📦 §#1164（11-02 22:47, CPU eval监控·7轮·ETA~24h）→ daily-memories/2026-11-02.md；**结论**：.12大幅加速(40.9→20.9s/req),ETA下修至~24h。被#1165监控(速度稳定ETA不变)。需要时再读。
> 📦 §#1163（11-02 22:41, CPU eval监控·6轮·ETA~29h）→ daily-memories/2026-11-02.md；**结论**：.29加速至17s/req ETA~12h, .12仍41s/req, 总ETA~29h。被#1164修正(.12加速ETA下修至~24h)。需要时再读。
> 📦 §#1162（11-02 22:36, CPU eval监控·5轮·ETA~2天）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~33s/.12~41s,ETA~48h≈2天,S1 iter59380健康。被#1163监控(.29加速ETA下修)。需要时再读。
> 📦 §#1161（11-02 22:32, CPU eval监控·4轮·ETA~2天）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~33-34s/.12~40-41s,ETA~48h≈2天,S1 iter59340健康。被#1162监控。需要时再读。
> 📦 §#1160（11-02 22:25, CPU eval监控·3轮·ETA~2天）→ daily-memories/2026-11-02.md；**结论**：4 eval稳定,.29~33s/.12~41s,ETA~47h≈2天,S1 iter59280健康。被#1161监控。需要时再读。
> 📦 §#1159（11-02 22:20, CPU eval监控·2轮·ETA下修~2天）→ daily-memories/2026-11-02.md；**结论**：速度收敛(.29~33s/.12~43s),ETA~48h≈2天,S1 iter59230健康。被#1160监控。需要时再读。
> 📦 §#1154（11-02 19:55, CPU ETA+GPU发现）→ daily-memories/2026-11-02.md；**结论**：5 export 完成, float32 CPU冒烟11.7s/req, ETA 9.9天, GPU空闲建议（已被19:51令否决—GPU重新满载）。被#1155修正。需要时再读。
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
> 📦 §#1139（11-02 09:02, S1健康监控iter53140/loss~2.110/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter53140(7.59%), loss~2.110稳态, grad-norm 0.090-0.220(minor spike 0.220@53140单步瞬态已恢复), ~603K tok/s, ckpt@iter_52000(next@54000)。被#1140监控。需要时再读。
> 📦 §#1138（11-02 08:45, S1健康监控iter52990/loss~2.114/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter52990(7.57%), loss~2.114稳态, grad-norm 0.091-0.129(极稳无spike), ~605K tok/s, ckpt@iter_52000(next@54000)。被#1139监控。需要时再读。
> 📦 §#1137（11-02 08:27, S1健康监控iter52840/loss~2.117/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter52840(7.55%), loss~2.117稳态, grad-norm 0.087-0.335(minor spike 0.335@52820已恢复), ~605K tok/s, ckpt@iter_52000(next@54000)。被#1139监控。需要时再读。
> 📦 §#1136（11-02 08:09, S1健康监控iter52680/loss~2.118/0NaN/~602K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter52680(7.53%), loss~2.118稳态, grad-norm 0.084-0.142(极稳无spike), ~602K tok/s, ckpt@iter_52000(next@54000)。被#1137监控。需要时再读。
> 📦 §#1134（11-02 07:34, S1健康监控iter52380/loss~2.117/0NaN/~606K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter52380(7.48%), loss~2.117稳态, grad-norm 0.089-0.782(minor spike 0.782@52270已恢复), ~606K tok/s, ckpt@iter_52000(next@54000)。被#1135监控。需要时再读。
> 📦 §#1133（11-02 07:16, S1健康监控iter52220/loss~2.122/0NaN/~604K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter52220(7.46%), loss~2.122稳态, grad-norm 0.085-0.479(minor spike 0.479@52160已恢复), ~604K tok/s, ckpt@iter_52000(next@54000)。被#1134监控。需要时再读。
> 📦 §#1132（11-02 06:59, S1健康监控iter52070/loss~2.124/0NaN/~604K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter52070(7.44%), loss~2.124稳态, grad-norm 0.087-0.112(极稳无spike), ~604K tok/s, ckpt@iter_52000(next@54000)。被#1133监控。需要时再读。
> 📦 §#1131（11-02 06:42, S1健康监控iter51930/loss~2.134/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter51930(7.42%), loss~2.134稳态, grad-norm 0.088-0.170(极稳无spike), ~603K tok/s, ckpt@iter_50000(next@52000)。被#1132监控。需要时再读。
> 📦 §#1128（11-02 05:49, S1健康监控iter51470/loss~2.14/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter51470(7.35%), loss~2.14稳态, grad-norm 0.083-0.146(极稳无spike), ~603K tok/s, ckpt@iter_50000(next@52000)。被#1129监控。需要时再读。
> 📦 §#1127（11-02 05:29, S1健康监控iter51300/loss~2.124/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter51300(7.33%), loss~2.124稳态, grad-norm 0.089-0.173(极稳无spike), ~603K tok/s, ckpt@iter_50000(next@52000)。被#1128监控。需要时再读。
> 📦 §#1126（11-02 05:13, S1健康监控iter51160/loss~2.14/0NaN/~603K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter51160(7.31%), loss~2.14稳态, grad-norm 0.088-0.198(极稳无spike), ~603K tok/s, ckpt@iter_50000(next@52000)。被#1127监控。需要时再读。
> 📦 §#1125（11-02 05:00, S1健康监控iter51000/loss~2.13/0NaN/~607K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter51000(7.29%), loss~2.13稳态, grad-norm 0.088-0.198(minor spike 0.773@50800已恢复), ~607K tok/s, ckpt@iter_50000(next@52000)。被#1126监控。需要时再读。
> 📦 §#1124（11-02 04:37, S1健康监控iter50850/loss~2.124/0NaN/~607K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter50850(7.26%), loss~2.124稳态, grad-norm 0.088-0.133(minor spike 1.287@50650+0.773@50800已恢复), ~607K tok/s, ckpt@iter_50000(next@52000)。被#1125监控。需要时再读。
> 📦 §#1123（11-02 04:20, S1健康监控iter50700/loss~2.124/0NaN/~605K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter50700(7.24%), loss~2.124稳态, grad-norm 0.088-0.126(minor spike 1.287@50650已恢复), ~605K tok/s, ckpt@iter_50000(next@52000)。被#1124监控。需要时再读。
> 📦 §#1122（11-02 04:05, S1健康监控iter50560/loss~2.127/0NaN/~607K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter50560(7.22%), loss~2.127稳态, grad-norm 0.088-0.129(minor spike 1.053@50310+0.338@50490已恢复), ~607K tok/s, ckpt@iter_50000(next@52000)。被#1123监控。需要时再读。
> 📦 §#1121（11-02 03:45, S1健康监控iter50400/loss~2.129/0NaN/~607K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter50400(7.20%), loss~2.129稳态, grad-norm 0.088-0.129(minor spike 1.053@50310已恢复), ~607K tok/s, ckpt@iter_50000(next@52000)。被#1122监控。需要时再读。
> 📦 §#1120（11-02 03:28, S1健康监控iter50250/loss~2.124/0NaN/~606K tok/s）→ daily-memories/2026-11-02.md；**结论**：S1健康iter50250(7.18%), loss~2.124稳态, grad-norm 0.091-0.173(minor spike 1.843@50020已恢复), ~606K tok/s, ckpt@iter_50000(next@52000)。被#1121监控。需要时再读。
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