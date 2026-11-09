# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

> 2026-11-09 18:28 #1837: **运维令11-09执行轮·状态确认轮·无新ckpt可评·训练健康step7150ms<7.4s✅·14/14eval全完成·等150k**·**动作**:①git fetch+status(同步✅,无ahead/behind) ②训练核查(.29 /tmp/baize_s1_baize2b_worker.log):iter141480/700k,step6958-7186ms✅(<7.4s铁律),loss2.034,0NaN/0skip,GPU95-100%满载 ③eval核查:pgrep llama-server/lm_eval=0(无残留),14/14 results.json全在(10k-140k) ④报告report_pretrain_llamacpp_scaling_60k_100k_zh.html=23577B(17:48更新,含140k)✅ ⑤无150k ckpt(latest=140k,iter141480→150000~8520步×7.1s≈16.8h后~11-10 11:10) ⑥research日报2026-11-09已读:pretrain建议(四件套工件+审计脚本+5×参考观测)为参考非指令,当前无新ckpt故不行动 ⑦📦TASK=27.9KB/MEMORY=10.6KB(均≤32KB✅,归档0KB)·未完成指令:无(11w-14w全完成,下个万整数150k~17h后)⇒WAITING:1。
> 📦 #1836（11-09 18:08, 运维令11-09执行轮·状态确认轮·无新ckpt·训练step<7.4s✅·14/14eval全完成）→ daily-memories/2026-11-09.md「#1836」节；**结论**：状态确认轮,无新万整数ckpt可评,14/14 eval全完成,训练step6988-7328ms<7.4s,等150k~17h后。需要时再读。
> 📦 #1835（11-09 17:46, 运维令11-09执行轮·140k eval✅完成Avg55.25%·报告刷新14/14·核心11w/12w/13w+14w全完成）→ daily-memories/2026-11-09.md「#1835」节；**结论**：140k eval DONE Avg=55.25%,报告14/14 ckpt刷新,pipeline自洽无残留,训练step<7.4s。需要时再读。
> 📦 #1830（11-09 17:01, 运维令11-09执行轮·140k eval运行中~38min·pipeline自洽·训练step7062ms✅）→ daily-memories/2026-11-09.md「#1830」节；**结论**：140k eval运行中ETA~17:22,pipeline PID636198自洽,核心11w/12w/13w已完成。需要时再读。
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