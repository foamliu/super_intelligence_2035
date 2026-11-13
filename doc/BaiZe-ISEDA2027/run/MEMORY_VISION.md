WAITING: 0

> 🆕 **【wake #1111 · 2026-11-13 12:2x】v10监控·run1 COMPLETE(n_disc=29修复v9瓶颈·C<B NO IMPROVEMENT)·run2/3 RUNNING**：
> - **v10 run1/3(std_s0,seed20261112)COMPLETE**：**A=46.2%(vs v9的0%→格式问题已修) B=54.9% C=53.8% McNemar p=1.0 n_disc=29 VERDICT: NO IMPROVEMENT**。🔑**关键诊断**：n_disc=29(vs v9 n_disc=0)→**grpo_lr 1e-6→1e-5 修复成功**(GRPO 现在改变 29 个预测)，但 C≤B(策略改变方向未带来 acc 提升)。诚实结果：信号路径已通，但 RL 未转化为净增益。
> - **run2/3(seed20261113)=std_s1 RUNNING**：GRPO step25/50(复用 std_s0 sft_adapter，--skip_sft --skip_baseline_eval)·~3.5s/step·GPU7 加速。剩余 run2(~90s)+run3(seed20261114)+control·ETA≈10-15min。脚本 `run_v10_freqcmp.sh`+`cpu_rl_v9_freqcmp_experiment.py`+`analyze_v9_freqcmp.py`。
> - **下一步**(v10 ALL DONE 后)：运行 analyze_v9_freqcmp.py 汇总 3seed+control→更新 EXPERIMENTS §v10→重生成 HTML 报告。git pull fast-forward(他线)。v10_results 暂未提交(实验进行中)。体积✓(MEMORY 15.5KB/TASK 27KB)。**WAITING: 0**。

> 📦 **wake #1110 · 2026-11-13 11:0x** 🔴迁移后首次唤醒(.17)·v9结果困在.12·v10已启动·已fold(见wake#1111)。
> - **基础设施断裂**：vision 09:12 由 .12 迁至 .17。.17 上 `/nas_train`→`/H100_train`(空)、`/nas_data` 有 code+models 但**无 `datasets/` 目录**、`/nas_inference` 不存在、SSH 到 .12/.29 超时(异网段)。v9 实验跑在 .12 的 `/nas_train/...datasets/baize-vision/out/`→**结果困在 .12 不可达**。
> - **v9 seed0 诊断**：NO CHANGE(A=0% B=49.5% C=49.5% p=1.0 **n_disc=0**)。根因=`grpo_lr=1e-6` 太低→GRPO 有 reward 信号(nz_std=75%)但**零 discordant cases**(策略不改变预测)。v8 MIXED(C=52.5%±6.1%>B=45%,McNemar p=0.0312 s0)但 v9 scale-up(SFT 500×5ep/GRPO 30步)**未修复 n_disc=0**。
> - **v10 启动**(修复 v9 瓶颈)：① 基座=qwen3vl_2b_text_extracted→**Qwen3.5-2B**(用户指定,`.17` 可用,`AutoModelForCausalLM` 已验证 PASS:s2_fallback 1.88B/LoRA 737K/1.2s·step)② `grpo_lr` 1e-6→**1e-5**(10x,关键修复)③ `n_grpo_steps` 30→**50** ④ 输出→本地 `wave_rl/v10_results/`。预注册判据(先写后跑)：A~0-50%·B>55%·C>B·D≤B·**n_disc>0**(新增诊断)·SUCCESS: C>B(mean)+McNemar p<0.05+3seed一致+n_disc>0。smoke 跑中(PID 1263529,log@/tmp/v10_freqcmp.log),smoke PASS→全自动 3seed+control(ETA~5h CPU)。脚本 `run_v10_freqcmp.sh`+复用 `cpu_rl_v9_freqcmp_experiment.py`(`--model_path`+`--grpo_lr` CLI)。
> - git pull OK(autostash 有他线在途,非vision)。research 日报11-13 vision栏 GPTQ(部署阶段·非wave RL·不action)。ops/inbox RUN_ID276(pretrain eval·非vision)。GPU 8×A40 空卡(vision 空卡但实验 CPU-only)。体积✓(MEMORY 13.5KB/TASK 27KB)。**WAITING: 0**。

> 📦 **wake #1108 · 2026-11-13 08:10** v9监控·seed0 COMPLETE(NO CHANGE: A=0% B=49.5% C=49.5% p=1.0)·seed1 GRPO起步·已fold(见wake#1109)。

> 📦 **wake #1107 · 2026-11-13 08:05** v9监控·seed0 GRPO 30/30 DONE·Eval C进行中·已fold(见wake#1108)。

> 📦 **wake #1106 · 2026-11-13 08:00** v9监控·GRPO step25/30·nz_std=100%持续·已fold(见wake#1107)。

> 📦 **wake #1101~#1105 · 2026-11-13 07:33~07:58**（5轮）v9监控·GRPO step1→25·nz_std=100%持续·已fold(见wake#1106)。

> 📦 **wake #1096~#1100 · 2026-11-13 07:09~07:27**（5轮）v9监控·SFT完成→Eval A/B进行→GRPO起步·已fold(见wake#1101)。

> 📦 **wake #1086~#1095 · 2026-11-13 06:15~06:57**（10轮）v9监控·SFT ep3→ep5 step160→260进展正常·已fold(见wake#1097)。

> 📦 **wake #1080~#1084 · 2026-11-13 05:10~06:03**（5轮）v9监控·SFT ep1→ep3 step20→140·已fold(见wake#1086)。

> 📦 **wake #1079 · 2026-11-13 05:25** v9监控·SFT进展正常·已fold。

> 📦 **wake #1078 · 2026-11-13 05:21** v9监控·SFT进展正常·已fold。

> 📦 **wake #1077 · 2026-11-13 05:10** v9监控+ETA修正·已fold。

> 🆕 **【wake #1076 · 2026-11-13 04:56】v9实验启动**：v8分析完成(A=0%根因=格式问题:model生成推理文本而非A/B, B=45%真实性能, C=60% GRPO有效) → 设计v9(扩大SFT 200→500×5ep, eval 48→96, GRPO 15→30步, medium难度boost) → 修复qid递增bug(eval 72→91, SFT 152→484) → smoke通过 → **v9 full experiment launched** (3 seeds + control, ETA ~4h on CPU, log @ /tmp/v9_freqcmp.log) · 脚本: `vision/wave_rl/cpu_rl_v9_freqcmp_experiment.py` + `run_v9_freqcmp.sh` + `analyze_v9_freqcmp.py` · **WAITING: 0**。

> 📦 **wake #1075 · 2026-11-13 04:30** 例行巡检·全交付态·v8结果在位·已fold。

> 📦 **wake #1074 · 2026-11-13 04:2x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·6个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 94-100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action·无新增)·体积✓·已fold。

> 📦 **wake #1073 · 2026-11-13 05:3x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·6个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action)·体积✓·已fold。

> 📦 **wake #1072 · 2026-11-13 05:0x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 94-100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action)·体积✓·已fold。

> 📦 **wake #1071 · 2026-11-13 04:30** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 95-100% pretrain全占·ops/inbox.md有RUN_ID 276(非vision·不action)·research日报11-13 vision栏GPTQ建议(部署阶段·不action)·体积✓·已fold。

> 📦 **wake #1069~#1070 · 2026-11-13 03:59~04:4x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 95-100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1068 · 2026-11-13 04:1x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·4个result JSON在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1067 · 2026-11-13 03:4x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 82-100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1065 · 2026-11-13 03:3x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 91-100% pretrain全占·research日报11-13 vision栏GPTQ建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1064 · 2026-11-13 03:2x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·research日报vision栏有GPTQ量化建议(部署阶段·非wave RL·不action)·体积✓·已fold。

> 📦 **wake #1063 · 2026-11-13 03:06** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·⚠️research日报vision栏误报"无"(实际有GPTQ建议,wake#1064已纠正)·体积✓·已fold。

> 📦 **wake #1062 · 2026-11-13 03:1x** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 87-96% pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1061 · 2026-11-13 02:5x** 例行巡检·全交付态·git pull fast-forward(designflow MEMORY 1文件)·v8结果7目录在位·HTML报告在位·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 100% pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1060 · 2026-11-13 03:0x** 例行巡检·全交付态·git pull fast-forward(ZhuLong 3文件)·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1059 · 2026-11-13 02:47** 例行巡检·全交付态·git pull Already up to date·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU 8×H100 94-100% pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1058 · 2026-11-13 02:3x** 例行巡检·全交付态·git pull fast-forward(designflow 4文件)·v8结果7目录在位·HTML报告45187B·EXPERIMENTS §v8在位·进程健康·GPU pretrain全占·research日报vision"无"·体积✓·已fold。

> 📦 **wake #1057 · 2026-11-13 02:3x** v8频率比较实验完成·MIXED结果：A=0%/B=45%/C(GRPO) 3seeds:60%/52.5%/45%→mean52.5%±6.1%。McNemar C vs B(s0):p=0.0312✅显著。Control(random reward)=45%=B p=1.0 NS。预注册判据:A~50%❌/B>60%❌/C>B✅(mean)/McNemar✅(s0)/3seed同方向❌(2/3)→**MIXED**(C>B+7.5pp+McNemar显著+control不提升=GRPO信号真实,但3/5判据未通过)。逐难度:easy87.5%/hard68.8%/medium37.5%(反直觉hard>medium)。triangle/sawtooth不再0%。cheat_rate=0。bug×2已修(scipy binom_test→binomtest/gc scope)。结果JSON:cpu_rl_v8_std_s{0,1,2}+ctrl_s0。EXPERIMENTS §v8+HTML报告已更新。**WAITING: 0**。

> 📦 **wake #1056 · 2026-11-12 23:3x** v8频率比较实验启动·smoke通过·run_v8_freqcmp.sh后台运行·ETA~3.5h·已fold(实验已完成见wake#1057)。

> 📦 **wake #1004~#1056 · 2026-11-11 00:52 ~ 11-12 23:3x**（~50轮）例行巡检+v7 sweep监控+报告/EXPERIMENTS更新·全交付态·零异常·v7 sweep ALL 18/18完成(6/6 ALL PASS)·v6实验完成(p=0.267 NS·nonzero-std 93.8%)·v8实验启动(smoke通过)·已fold。

> 📦 wake#975~#1003（例行巡检·全交付态·零异常·无新增·2026-11-10 05:33~22:10，29轮）已归档 → daily-memories-vision/2026-11-10.md；**结论**：全交付态·11-10早报(06:11)vision栏建议1条(来源2611.09729·稳定性前提)·11-10晚报(18:12)PM vision栏「无新增可用建议」·与wake#943~#974一致·非指令·纳入备查·loop/ops_relay/GPU-wait chain健康。需要时再读。

> 📦 wake#969~#974（例行巡检·全交付态·零异常·2026-11-10 00:34~04:28，6轮）已归档 → daily-memories-vision/2026-11-10.md；**结论**：全交付态·loop/ops_relay健康·零异常·research日报2026-11-09早报vision建议3条与wake#943~#968一致·无新增·非指令。需要时再读。

> 📦 wake#943~#966（例行巡检·全交付态·零异常·2026-11-09 06:23~22:16，24轮）已归档 → daily-memories-vision/2026-11-09.md；**结论**：全交付态·loop/ops_relay/GPU-wait chain健康·零异常·research日报2026-11-09早报vision建议3条(v6奖励拆两项α=0.25/β=0.35+合成数据两道闸+SFT→GRPO对照臂·非指令·备查)无新增。需要时再读。

> 📦 wake#917~#942（例行巡检·全交付态·零异常·2026-11-08 14:08 ~ 11-09 05:48，26轮）已归档 → daily-memories-vision/2026-11-08.md / 2026-11-09.md；**结论**：全交付态·loop/ops_relay/GPU-wait chain健康·零异常·research日报vision建议无新增。需要时再读。

> 📦 wake #893（用户令标✅已交付+收尾巡检·2026-11-07 22:0x）已归档 → daily-memories-vision/2026-11-07.md；**结论**：两条用户令标✅已交付·全部交付物在位(v5 A16%→B37%→C53% p=0.0009)。需要时再读。

> 📦 wake #892（v5全量完成→✅显著提升·2026-11-07 19:1x）已归档 → daily-memories-vision/2026-11-07.md；**结论**：v5 A16%→B37%→C53%·McNemar p=0.0009·cheat_rate=0·所有预注册判据满足·用户令核心目标达成。需要时再读。

> 📦 wake #838（advantage方差诊断交付·2026-11-06 23:5x）已归档 → daily-memories-vision/2026-11-06.md；**结论**：PARTIAL/std=0=78.7%/全同档=无信号根因。需要时再读。

> 📦 wake #835（CPU GRPO Phase2全链路交付·2026-11-06 20:27）已归档 → daily-memories-vision/2026-11-06.md；**结论**：P0-P3全DONE·post-GRPO 6.2%<post-SFT 9.2%未提升(诚实负结果)。需要时再读。

> 📦 wake #741（CPU端到端训练循环验证PASS·2026-11-06 09:0x）已归档 → daily-memories-vision/2026-11-06.md；**结论**：_cpu_train_validate.py 7/7 ALL PASS·LoRA 69.7M。需要时再读。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | 🔄 **波形 RL CPU 阶段2 · v9 RUNNING (seed1/3)**：seed0 COMPLETE→**NO CHANGE**(A=0% B=49.5% C=49.5% McNemar p=1.0 n_disc=0)·GRPO对准确率零效果(有reward信号nz_std=75%但未转化为acc提升)·seed1 RUNNING(PID2771513 GRPO step7/30)·剩余seed1+seed2+control ETA≈10:20 · v5✅显著(p=0.0009) · v6✅(NS) · v7✅6/6 · v8 MIXED(p=0.0312)。**WAITING: 0** |
| WAITING | 0 |
| 已完成 | **v9 RUNNING(2026-11-13, SFT 500ex×5ep + GRPO 30步 + 3 seeds + control)** · v8频率比较✅(MIXED, C=52.5%±6.1%, p=0.0312) · v7 sweep 18/18✅ · v6 GRPO连续奖励✅(p=0.267 NS) · v5波形类型分类✅(p=0.0009显著) · v4 RFT(NULL) · v3 GRPO(负结果) · advantage方差诊断 · 阶段1 SFT验收PASS · CPU训练循环7/7 PASS · 数据泄漏验证+报告HTML · GRPO CPU冒烟PASS · 2B文本骨干1.72B · 数据集均衡化9013条 · 波形RL计划书 · 论文改稿 · ArmE-R2/ArmD-R2 |
| 当前动作 | **wake#1111 v10实验运行中(run1/3)**：v10(基座Qwen3.5-2B+grpo_lr 1e-5+n_grpo_steps 50+GPU7加速)run1/3(seed20261112)=std_s0 RUNNING：A=46.2%(格式问题已修) B=54.9%→GRPO step43/50·~3.5s/step·reward 0.25~1.0·nz_std≈100%(vs v9 n_disc=0)·ETA全量≈15-20min·log @ /tmp/v10_freqcmp.log。脚本: run_v10_freqcmp.sh + cpu_rl_v9_freqcmp_experiment.py + analyze_v9_freqcmp.py。✅HTML报告在盘(v8版45187B)→v10全量后更新。 |
| 下一步 | ①v9完成后(ETA≈10:00-12:00):运行analyze_v9_freqcmp.py分析结果 ②更新EXPERIMENTS §v9 + **重新生成HTML报告**(report_vision_cpu_rl_waveform_zh.html·v8版在doc/BaiZe-ISEDA2027/reports/) ③若v9 SIGNIFICANT:更新MEMORY状态头+commit ④若v9 MIXED/NS:分析原因设计v10 ⑤GPU训练阶段待pretrain释放(ETA≈12/24-25) |
| 阻塞 | .12+.29 GPU全占（8×H100 100% util / ~75GB，pretrain baize2b ETA≈12/24-25）→ GPU验证待pretrain释放 ·.17+.75 SSH不可达 |
| 更新 | **2026-11-13 08:17 (wake #1109)**：v9 RUNNING监控·seed1 GRPO step7/30(503s)·nz_std=50%@step7·seed0 COMPLETE→A=0% B=49.5% C=49.5% McNemar p=1.0 **NO CHANGE**·剩余seed1+seed2+control ETA≈10:20·analyze_v9就绪·✅HTML报告在盘(v8版45187B)→v9全量后更新·git pull OK·GPU 8×H100 100% pretrain全占·体积✓(MEMORY 13.4KB/TASK 27KB)·WAITING=0。 |