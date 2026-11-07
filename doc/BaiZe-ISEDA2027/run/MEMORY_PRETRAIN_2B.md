# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-07 18:26 #1586: 运维令11-07 15:2x继续执行·v4全量GGUF eval已启动(hellaswag分片4 servers+其余7 tasks分4 servers,8 llama-server×16 threads,8进程并行)·v3失败根因=NFS "Stale file handle"杀死bash脚本→v4修复=脚本+Python全复制到/tmp执行·v4新增hellaswag --samples分片(10042 docs→4 shards×2511 docs,消除木桶效应)·所有8 servers已READY(eval PID3912298+,marker epoch=1794047138)·精度回归已PASS(#1585:iter_10000 HF vs GGUF max Δacc=0.02<n=100 stderr 0.045)·gen_eval_speedup_report.py已指向v4路径·报告9382B/0script/0外链·S1健康(GPU 100%/75GB)·📦TASK=28.5KB✓/MEMORY=15.9KB✓·未完成指令:有(v4 eval运行中→完成后填耗时对照+分数→报告最终更新)⇒WAITING:0。

> 2026-11-07 17:24 #1585: 运维令11-07 15:2x继续执行·精度回归结论=PASS(iter_10000 HF vs GGUF 8集逐比对:arc_challenge Δ0.02/arc_easy Δ0/boolq Δ0.01/hellaswag Δ0.01/openbookqa Δ0.01/piqa Δ0/sciq Δ0/winogrande Δ0,max Δacc=0.02<n=100 stderr 0.045→PASS;iter_100000 GGUF trend raw Avg=54.75%单调上升→converter一致性OK)·iter_112000精度回归卡住41%(1075/2599,28min无进度=HTTP挂起,冗余已kill)·全量GGUF eval已启动(PID3418162,4 servers×56 threads,8 tasks并行,hellaswag+openbookqa→server0,arc_challenge+piqa→server1,arc_easy+sciq→server2,boolq+winogrande→server3)·各任务进度@17:24:openbookqa 6%/boolq 1%/sciq 1%/arc_challenge 0%/arc_easy 0%/winogrande 1%/piqa 0%/hellaswag tokenizing 85%·merge_parallel_results.py修复hellaswag单目录处理·报告更新8796B/0script/0外链·S1健康(GPU 100%/75GB)·load130/224·📦TASK=27.8KB✓/MEMORY=14.5KB✓·未完成指令:有(全量eval运行中→完成后填耗时对照+分数→报告最终更新)⇒WAITING:0。

> 2026-11-07 17:05 #1584: 运维令11-07 15:2x继续执行·精度回归进行中(PID3439735,1075/2599=41%,llama-server 3 req processing,ETA~20min)·验证iter_10000 HF results.json存在(n=100,与GGUF对比max Δacc=0.02 PASS确认)·验证iter_100000 GGUF trend(n=100,raw Avg=54.75%,分数随训练上升→converter一致性OK)·报告更新:gen_eval_speedup_report.py加§三b GGUF跨ckpt一致性表+iter_112000精度回归状态,报告8104B/0script/0外链·全量eval脚本baize_llamacpp_full_eval.sh已确认(4 servers×56 threads,hellaswag独占server0,无--limit=全量73k req)·S1健康(GPU.29 97-100%/75GB)·下一步:精度回归完成→检查NaN+趋势→kill llama-server:8080→启动全量GGUF eval·📦TASK=28.5KB✓/MEMORY=14KB✓·未完成指令:有(精度回归→全量eval→报告最终更新)⇒WAITING:0。

> 2026-11-07 16:50 #1583: 运维令11-07 15:2x执行中·精度回归运行中(PID3439735,1075/2599=~41%,速度降至~0.3req/s因hellaswag长序列,ETA~35min)·llama-server健康(port8080,64线程,8 parallel)·已验证iter_10000 HF vs GGUF:max Δacc=0.02 PASS·全部脚本已创建并提交(cpu_lmeval_run.py/baize_cpu_lmeval.sh加--samples,baize_cpu_lmeval_parallel.sh 11进程,merge_parallel_results.py,baize_llamacpp_full_eval.sh多服务器,gen_eval_speedup_report.py,gguf_lmeval_run.py加--samples)·报告report_pretrain_cpu_eval_speedup_zh.html(7023B)已生成·GGUF转换成功(4.2GB)·串行HF eval已kill(仅0.9%完成)·S1健康·📦TASK=28.5KB✓/MEMORY=13.5KB✓·未完成指令:有(精度回归待完成→全量eval→报告更新)⇒WAITING:0。

> 2026-11-07 15:32 #1581: 例行监控轮·无新运维令·S1健康(iter117220/700000@15:32,loss2.042,7.6-8.5s/it,grad-norm0.087-0.115,0NaN/0skip,GPU.29全满载81-100%/~75GB/139-183W/41-50℃,858-955TFLOP/s/GPU)·ckpt iter_0116000在盘(checkpoints/),HF导出112000在盘,next iter_0118000 ETA~17:00·全量eval后台继续(PID3726478,~4.5h,867%CPU≈8.7核,~10.3GB RSS,nice19,不抢S1)·内存689GB/2015GB(1201GB可用)充裕·load57.7/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·git up-to-date·📦TASK=31.2KB✓/MEMORY=12.3KB✓·未完成指令:无⇒WAITING:1。

> 2026-11-07 15:12 #1580: 例行监控轮·无新运维令·S1健康(iter117080/700000@15:12,7.26-7.42s/it,~980-998TFLOP/s/GPU,GPU.29全满载95-100%/~75GB/~685W/54-63℃)·ckpt iter_0116000在盘(checkpoints/),HF导出110k/112k在盘,next iter_0118000 ETA~17:00·全量eval后台继续(PID3726478,538/73106req@4h11m,~26.7s/req稳定,868%CPU≈8.7核,10.4GB RSS,nice19,不抢S1,ETA~22天)·内存690GB/2015GB(1200GB可用)充裕·load48.9/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·git up-to-date·📦TASK=31.2KB✓/MEMORY=11.3KB✓·未完成指令:无⇒WAITING:1。


> 2026-11-07 14:50 #1579: 例行监控轮·无新运维令·S1健康(GPU.29全满载94-100%/~75GB/~690W/55-65℃@14:49 nvidia-smi确认;SSH.29后续超时疑似瞬态负载,非S1问题)·ckpt iter_0116000在盘(同#1578,下一iter_0118000 ETA~17:00)·全量eval后台继续(PID3726478,487/73106req@3h49m,~26.8s/req稳定,868%CPU≈8.7核,11.7GB RSS,nice19,不抢S1,ETA~22.5天)·内存692GB/2015GB充裕·load47/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·⚠️L2日志尾部见error traceback但系另一实验(step2370/5611/loss0.94≠S1)非S1,S1 GPU仍94-100%·git up-to-date·📦TASK=31.2KB✓/MEMORY=11.3KB✓·未完成指令:无⇒WAITING:1。


> 2026-11-07 14:26 #1578: 例行监控轮·无新运维令·S1健康(iter~116690/700000@14:26,loss~2.04,~7s/it,0NaN/0skip,GPU.29全满载96-100%/~75GB/665-696W/54-63℃)·ckpt iter_0116000在盘(同#1577)·全量eval后台继续(PID3726478,434/73106req@3h26m,~26.4s/req稳定,867%CPU≈8.7核,11.4GB RSS,nice19,不抢S1,ETA~22天)·内存686GB/2015GB充裕·load40.9/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·git up-to-date·📦TASK=31.2KB✓/MEMORY=10.5KB✓(归档#1043-#1555→summary pointer,释放~21KB)·未完成指令:无⇒WAITING:1。


> 2026-11-07 13:48 #1576: 例行监控轮·无新运维令·S1健康(iter116370/700000@13:48,loss2.047,7.0-7.2s/it,0NaN/0skip,grad-norm0.097-0.142,GPU.29全满载94-100%/~75GB/677-697W/57-65℃)·ckpt116000在盘(torch_dist,HF导出100k/110k/112k在盘)·全量eval后台继续(PID3726478,348/73106req@2h46m,~26.3s/req稳定,865%CPU≈8.6核,9.6GB RSS,nice19,不抢S1,ETA~22天)·内存687GB/2015GB充裕·load47/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·git ahead2(harness+merge非本线)/behind0·📦TASK=31.2KB✓/MEMORY=30.3KB✓(均<32KB无需归档)·未完成指令:无⇒WAITING:1。
> 2026-11-07 14:07 #1577: 例行监控轮·无新运维令·S1健康(iter116530/700000@14:07,loss2.041,7.07s/it,0NaN/0skip,grad-norm0.086-0.123,GPU.29全满载95-100%/~75GB/682-689W/53-64℃)·新ckpt iter_0116000在盘(上轮iter_0114000)·全量eval后台继续(PID3726478,391/73106req@3h05m,~26.0s/req稳定,866%CPU≈8.7核,9.9GB RSS,nice19,不抢S1,ETA~22天)·内存685GB/2015GB充裕·load44.6/224核·ops/inbox无新令·research日报11-07无pretrain建议·git up-to-date·📦TASK=31.2KB✓/MEMORY=31.0KB✓(均<32KB无需归档)·未完成指令:无⇒WAITING:1。


> 2026-11-07 12:40 #1575: 例行监控轮·无新运维令·S1健康(iter115800/700000@12:39,loss2.049,7.3-7.4s/it,0NaN/0skip,grad-norm0.082-0.098稳态,GPU.29全满载95-100%/~75GB/635-685W/55-63℃)·三ckpt 110k/112k/114k全在.29·全量eval后台继续(PID3726478,195/73106req@1h40m,~27s/req,861%CPU≈8.6核,11.3GB RSS,nice19,不抢S1,ETA~22.7天)·内存682GB/2015GB充裕·load47/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·📦TASK=31.2KB✓/MEMORY=30.5KB✓(归档#1564-#1565→daily-memories)·未完成指令:无⇒WAITING:1。


> 2026-11-07 12:22 #1574: 例行监控轮·无新运维令·S1健康(iter115640/700000@12:20,loss2.043,7.2-7.4s/it,0NaN/0skip,grad-norm0.089-0.098稳态,GPU.29全满载96-100%/~75GB/672-687W/55-63℃)·ckpt iter_0114000在盘(三ckpt 110k/112k/114k全在)·全量eval后台继续(PID3726478,154/73106req@1h20m,~28s/req稳定,859%CPU≈8.6核,9.5GB RSS,nice19,不抢S1,ETA~23.6天)·内存684GB/2015GB充裕·load50/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·pretrain_launcher PID146283活·📦TASK=31.2KB✓/MEMORY=30.9KB✓(均<32KB无需归档)·未完成指令:无⇒WAITING:1。


> 2026-11-07 12:03 #1573: 例行监控轮·无新运维令·S1健康(iter115500/700000@12:03,loss2.052,7.0-7.5s/it,0NaN/0skip,grad-norm0.085-0.125稳态,GPU.29全满载97-100%/~75GB/676-699W/56-64℃,GPU.12全满载88-100%/~75GB/638-691W/57-64℃)·新ckpt iter_0114000在盘(上轮iter_0112000)·全量eval后台继续(PID3726478,116/73106req@62min,~27s/req,847%CPU≈8.5核,8.1GB RSS,nice19,不抢S1,ETA~23天)·内存682GB/2015GB充裕·load49.7/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·pretrain_launcher PID146283活(~112h)·📦TASK=31.2KB✓/MEMORY=30.2KB✓(均<32KB无需归档)·未完成指令:无⇒WAITING:1。

> 2026-11-07 11:45 #1572: 例行监控轮·无新运维令·S1健康(iter115340/700000@11:44,loss2.042,7.1s/it,0NaN/0skip,grad-norm0.099-0.113,GPU.29全满载94-100%/~75GB/655-690W/55-65℃)·全量eval后台继续(PID3726478,75/73106req@43min,速度从41s/req加速至~27s/req,839%CPU≈8核,7.3GB RSS,nice19,不抢S1)·evalETA下修:27s/req→~23天(vs #1571估35天@41s/req)·内存681GB/2015GB充裕·load54/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·📦TASK=31.2KB✓/MEMORY=29.7KB✓(均<32KB无需归档)·未完成指令:无⇒WAITING:1。

> 2026-11-07 11:27 #1571: 监控+收尾轮·运维令11-07 09:1x标记✅已交付(完成标记达标:报告已交付+8/16/32/80线程×bs1/bs2覆盖)·报告ETA修正(探测估9.9天→实测~35天,hellaswag长序列致41s/req vs探测14s/req)·报告9936B·全量eval后台运行中(PID3726478,30/73106req,16线程bs=1,nice19,806%CPU≈8核,不抢S1)·S1健康(iter115160/700000@11:22,loss2.074,0NaN/0skip,7.96s/it,GPU.29全满载70-100%/~75GB/600-694W)·ckpt iter_0112000在盘·📦TASK=31.2KB✓/MEMORY=29.1KB✓(均<32KB无需归档)·未完成指令:无⇒WAITING:1。


> 2026-11-07 11:02 #1570: ✅运维令11-07 09:1x**已交付**·探测矩阵8/8全完成+t线程×batch二维热点表+中文HTML报告已交付·报告`reports/report_pretrain_cpu_eval_thread_scaling_zh.html`(9427B/5表/0script/0外链)·探测结果(3样本×openbookqa+arc_challenge/24req):t8b1=443s(基线)/t8b2=541s(0.82x更慢)/t16b1=359s(1.23x)/t16b2=385s(1.15x)/t32b1=364s(1.22x)/t32b2=376s(1.18x)/t80b1=392s(1.13x)/t80b2=325s(1.36x最优)·核心发现:线程扩展16线程饱和(SSM顺序扫描不可并行),80线程bs=1反而因调度开销变慢;但80线程+bs=2利用富余核心处理batch维度达最优·内存峰值50.3GB/2TB安全·全量eval(16线程bs=1无limit,PID3726478)已在后台启动但需~12天(CPU推理73K请求@15s/req)·已kill旧orchestrator(改用16线程最优)·gen_cpu_eval_scaling_report.py已修(load_est=30s固定,关键发现文案更新)·orchestrator脚本改16线程·probe结果落lm_eval_results/probe_scaling_112000.json·S1健康·📦TASK=30.4KB✓/MEMORY≈30KB·未完成指令:无(报告已交付,全量eval后台继续)⇒WAITING:1。

> 2026-11-07 10:37 #1569: 运维令11-07执行中·探测矩阵config5/8(t32_b1)运行中·已修gen_cpu_eval_scaling_report.py(加load_est估算)·探测已完成4/8:t8b1=443s/t8b2=541s(更慢)/t16b1=359s/t16b2=385s·S1健康·峰值50.3GB/2TB安全·未完成指令:有⇒WAITING:0。



> 📦 §#1565（11-07 08:17, 监控轮·iter113620/700000）→ daily-memories/2026-11-07.md「归档 #1564-#1565」节；**结论**：S1健康0NaN/0skip,loss2.065,ckpt iter_0112000。需要时再读。



> 📦 §#1564（11-07 07:55, 监控轮·iter113440/700000）→ daily-memories/2026-11-07.md「归档 #1564-#1565」节；**结论**：S1健康0NaN/0skip,loss2.074,ckpt iter_0112000。需要时再读。


> 📦 §#1563（11-07 07:35, 监控轮·iter113260/700000）→ daily-memories/2026-11-07.md「归档 #1562-#1563」节；**结论**：S1健康0NaN/0skip,loss2.079,ckpt iter_0112000。需要时再读。



> 📦 §#1561（11-07 06:54, 监控轮·iter112920/700000）→ daily-memories/2026-11-07.md「#1561」节；**结论**：S1健康0NaN/0skip,loss2.075,ckpt iter_0112000。需要时再读。


> 📦 §#1562（11-07 07:16, 监控轮·iter113110/700000）→ daily-memories/2026-11-07.md「归档 #1562-#1563」节；**结论**：S1健康0NaN/0skip,loss2.075,ckpt iter_0112000。需要时再读。


> 📦 §#1560（11-07 06:32, 监控轮·iter112740/700000）→ daily-memories/2026-11-07.md「归档 #1560」节；**结论**：S1健康0NaN/0skip,loss2.074,latest ckpt iter_0112000,next iter_0114000 ETA~Nov7 09:00。被#1562确认延续。需要时再读。


> 📦 §#1559（11-07 06:12, 监控轮·iter112560/700000）→ daily-memories/2026-11-07.md「归档 #1558-#1559」节；**结论**：S1健康0NaN/0skip,loss2.064,latest ckpt iter_0112000,next iter_0114000 ETA~Nov7 09:00。需要时再读。


> 📦 §#1558（11-07 05:52, 监控轮·iter112400/700000）→ daily-memories/2026-11-07.md「归档 #1558-#1559」节；**结论**：S1健康0NaN/0skip,loss2.076,latest ckpt iter_0112000,next iter_0114000 ETA~Nov7 09:05。需要时再读。


> 📦 §#1557（11-07 05:29, 监控轮·iter112210/700000）→ daily-memories/2026-11-07.md「归档 #1557」节；**结论**：S1健康0NaN/0skip,loss2.087(含3次grad-norm瞬态spike自恢复),latest ckpt iter_0112000,next iter_0114000 ETA~Nov7 09:05。被#1560确认延续。需要时再读。


> 📦 §#1556（11-07 05:12, 监控轮·iter112050/700000）→ daily-memories/2026-11-07.md「归档 #1556」节；**结论**：S1健康0NaN/0skip,loss2.068,latest ckpt iter_0112000(新),next iter_0114000 ETA~Nov7 09:00。被#1557确认延续。需要时再读。

> 📦 §#1043–#1555（11-01→11-07, S1健康监控iter41950→111880 + CPU eval 5ckpt + llama.cpp pilot + 100k eval交付, 共~500轮）→ daily-memories/2026-11-{01..07}.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.05–2.16稳态, ckpt iter_38000→116000, 100k eval已交付(10/10,Avg harness 57.75%), llama.cpp pilot=FAIL(保留HF float32), CPU eval thread scaling报告已交付. 需要时再读 daily-memories。


---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实�