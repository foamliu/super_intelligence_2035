# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-09 17:01 #1830: **运维令11-09执行轮·140k eval运行中~38min(server task21561活跃)·pipeline自洽·训练健康step7062ms✅(铁律满足)·核心11w/12w/13w已完成**·**动作**:①git fetch origin(ref lock报错但已拉到627e3ac8b,status synced,仅别线在途文件未碰) ②训练核查(.29 /tmp/baize_s1_baize2b_worker.log):iter140740/700k,step6931-7218ms✅(<7.4s铁律),loss2.029-2.049,0NaN/0skip ③**140k eval运行中~38min**:pipeline PID636198(etimes3613s)自洽,llama-server PID2950224(-t4,nice19,port8190)+lm_eval PID2966176(etimes2282s),server log task21561(活跃推进),140k output dir空(eval进行中results.json未落盘),ETA~17:22(130k耗时~59min参照) ④110k/120k/130k results.json全✅确认(22804-22810B,核心任务已完成) ⑤报告=23195B(13/20ckpt),pipeline完成后自动调gen_llamacpp_scaling_report.py刷新14/20 ⑥无150k ckpt(最新140k,150k~18h后~10:00) ⑦📦TASK=27.2KB/MEMORY=10.1KB(归档0KB,均≤32KB✅)·未完成指令:有(140k eval运行中,pipeline自动完成报告刷新)⇒WAITING:0。
> 📦 #1829（11-09 16:53, 运维令11-09执行轮·140k eval运行中~31min·pipeline自洽·训练step7038ms✅）→ daily-memories/2026-11-09.md「#1829」节；**结论**：140k eval运行中ETA~17:25,pipeline PID636198自洽,核心11w/12w/13w已完成。需要时再读。
> 📦 #1828（11-09 16:45, 运维令11-09执行轮·140k eval运行中~22min·pipeline自洽·训练step6.97-7.25s✅）→ daily-memories/2026-11-09.md「#1828」节；**结论**：140k eval运行中ETA~17:50,pipeline PID636198自洽,训练step<7.4s铁律满足。需要时再读。
> 📦 #1827（11-09 16:37, 运维令11-09执行轮·140k eval运行中~14min·pipeline自洽·训练step6.97-7.17s✅）→ daily-memories/2026-11-09.md「#1827」节；**结论**：140k eval运行中ETA~17:50,pipeline PID636198自洽,训练step<7.4s铁律满足。需要时再读。
> 📦 #1826（11-09 16:32, 运维令11-09执行轮·140k eval运行中·pipeline自洽·训练step7.0-7.17s✅）→ daily-memories/2026-11-09.md「#1826」节；**结论**：140k eval运行中ETA~17:50,pipeline PID636198自洽,训练step<7.4s。需要时再读。
> 📦 #1825（11-09 16:25, 运维令11-09执行轮·11w/12w/13w三ckpt补评全部完成✅·报告刷新13/20·140k eval运行中）→ daily-memories/2026-11-09.md「#1825」节；**结论**：110k✅58%/120k✅56.75%/130k✅58%核心完成,报告13/20,140k eval运行中ETA~17:50,pipeline自洽。需要时再读。
> 📦 #1824（11-09 16:01, 运维令11-09执行轮·140k HF导出+GGUF转换完成·140k eval pipeline排队等130k·训练step7.0s✅）→ daily-memories/2026-11-09.md「#1824」节；**结论**：140k HF/GGUF就绪,pipeline排队等130k完成,step7.0s<7.4s。需要时再读。
> 📦 #1823（11-09 15:38, 运维令11-09执行轮·铁律越界处置SIGSTOP/CONT·130k eval恢复·pipeline自洽）→ daily-memories/2026-11-09.md「#1823」节；**结论**：step time破7.4s根因=ckpt save+harness,我的eval非主因,SIGSTOP/CONT护训练,130k eval恢复运行ETA~16:20。需要时再读。
> 📦 #1822（11-09 15:23, 运维令11-09执行轮·130k eval运行中·pipeline自洽）→ daily-memories/2026-11-09.md「#1822」节；**结论**：130k eval运行中ETA~16:14,pipeline自洽,训练step≤7.4s。需要时再读。
> 📦 #1821（11-09 15:15, 运维令11-09执行轮·报告刷新含110k/120k·130k eval运行中·pipeline自洽）→ daily-memories/2026-11-09.md「#1821」节；**结论**：报告12/20ckpt含110k(58%)+120k(56.75%),130k eval运行中ETA~16:10,pipeline自洽将自动完成130k→报告,训练step<7.4s。需要时再读。
> 📦 #1820（11-09 15:04, 运维令11-09执行轮·130k eval运行中~35%·pipeline自洽）→ daily-memories/2026-11-09.md「#1820」节；**结论**：130k eval运行中,110k✅58%/120k✅56.75%,pipeline自洽将自动完成130k→报告,训练step<7.4s。需要时再读。
> 📦 #1819（11-09 14:57, 运维令11-09执行轮·120k eval✅56.75%·130k eval启动·pipeline自洽）→ daily-memories/2026-11-09.md「#1819」节；**结论**：120k done Avg=56.75%,130k eval启动,pipeline自洽将自动完成130k→报告,训练step<7.4s。需要时再读。
> 📦 #1818（11-09 14:44, 运维令11-09执行轮·120k eval运行中~72min·pipeline自洽）→ daily-memories/2026-11-09.md「#1818」节；**结论**：120k eval ~72min运行中,server task 37352,pipeline自洽将自动完成120k→130k→报告,训练step<7.4s。需要时再读。
> 📦 #1817（11-09 14:38, 运维令11-09执行轮·120k eval运行中~66min·pipeline自洽）→ daily-memories/2026-11-09.md「#1817」节；**结论**：120k eval ~66min运行中,server task 33228,pipeline自洽将自动完成120k→130k→报告,训练step<7.4s。需要时再读。
> 📦 #1816（11-09 14:25, 运维令11-09执行轮·120k eval运行中·pipeline自洽）→ daily-memories/2026-11-09.md「#1816」节；**结论**：120k eval ~52min运行中,pipeline自洽将自动完成120k→130k→报告,训练step7.09s<7.4s。需要时再读。
> 📦 #1815（11-09 14:14, 运维令11-09执行轮·杀冗余followup防冲突·120k eval继续运行）→ daily-memories/2026-11-09.md「#1815」节；**结论**：kill了会在120k未完成时pkill_server的followup PID3420260,原pipeline(1682543)自洽将自动串行完成120k→130k→报告,训练step7.08s<7.4s。需要时再读。
> 📦 #1814（11-09 14:06, 运维令11-09执行轮·120k eval近完成·followup管道守护）→ daily-memories/2026-11-09.md「#1814」节；**结论**：120k eval server task18402近完成,followup PID3420260等120k→130k→报告,训练step<7.4s。注:#1815发现followup 40min timeout会冲突,已kill。需要时再读。
> 📦 #1813（11-09 13:50, 运维令11-09执行轮·120k eval 54%运行中·followup管道守护启动·报告含110k）→ daily-memories/2026-11-09.md「#1813」节；**结论**：110k done Avg=58%,120k eval 54%运行中,followup管道(PID3420260)等120k→130k→报告,训练step<7.4s。需要时再读。
> 📦 #1812（11-09 13:33, 运维令11-09执行轮·修复重复pipeline致120k eval卡死·干净重启pipeline）→ daily-memories/2026-11-09.md「#1812」节；**结论**：杀重复pipeline+干净重启,flock防重,120k eval启动。注:#1812管道wrapper后被#1813发现已死但eval存活。需要时再读。
> 📦 #1811（11-09 13:16, 运维令11-09执行轮·110k eval✅完成·120k eval运行中·pipeline守护化）→ daily-memories/2026-11-09.md「#1811」节；**结论**：110k eval done 8/8集有效,120k eval运行中,130k排队,训练step7133ms<7.4s。需要时再读。
> 📦 #1807（11-09 12:40, 运维令11-09执行轮·110k eval 72%推进中·训练健康·pipeline排队）→ daily-memories/2026-11-09.md「#1807」节；**结论**：110k eval 72%(1875/2599),120k/130k pipeline排队,训练step time<7.4s健康。需要时再读。
> 📦 #1806（11-09 12:50, 运维令11-09执行轮·110k eval 71%·TASK归档→27.9KB·训练健康）→ daily-memories/2026-11-09.md「#1806」节；**结论**：110k eval 71%(1844/2599),120k/130k pipeline排队,训练step time<7.4s健康,TASK归档34.6KB→27.9KB。需要时再读。
> 📦 #1805（11-09 12:24, 运维令11-09执行轮·110k eval 51%推进中·训练健康·全链自动化确认）→ daily-memories/2026-11-09.md「#1805」节；**结论**：110k eval 51%运行中,120k/130k pipeline排队,训练step time<7.4s健康。需要时再读。
> 📦 #1804（11-09 12:19, 运维令11-09执行轮·110k eval 46%推进中·全链自动化就绪）→ daily-memories/2026-11-09.md「#1804」节；**结论**：110k eval 46%运行中,120k/130k pipeline排队,训练吞吐未受影响。需要时再读。
> 📦 #1803（11-09 12:09, 运维令11-09执行轮·110k eval client存活确认42%·120k/130k pipeline排队）→ daily-memories/2026-11-09.md「#1803」节；**结论**：110k eval client非死继续运行,120k/130k pipeline排队自动续跑。需要时再读。
> 📦 #1802（11-09 11:58, 运维令11-09执行轮·110k eval启动+GGUF重转+pipeline排队）→ daily-memories/2026-11-09.md「#1802」节；**结论**：110k eval client启动后继续运行(非死),120k/130k pipeline排队。需要时再读。

> 📦 §#1043–#1801（11-01→11-09, v4/v5/v6 eval监控+anomaly调查+100k eval交付, 共~800轮）→ daily-memories/2026-11-{01..09}.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：①100k eval 10/10 ckpt harness Avg 51.50→57.75%已交付 ②anomaly调查=口径差异(结论A):stale results.json缺piqa致低估37.4%,补全后Avg7=55.96% ③v4旧二进制回归致sciq=0.44(修复后0.88) ④llama.cpp PR#31703修复混合架构权重错位 ⑤S1训练全程健康0NaN/0skip,loss~2.05-2.16,ckpt iter_38000→138000. 需要时再读 daily-memories。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实际日志。