# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-08 08:02 #1651: **chunk0b瓶颈分裂轮·34h→14.5h(2.3x)+修复broken watcher**·**7/8完成**(Avg7=0.3740)·**本轮动作**:①git fetch已同步(无behind) ②**发现server 8083 DOWN+chunk0a死**(stuck 4693/10040,eval进程已不存在) ③**修复broken watcher**:rebalance_and_split.sh的step9检查死chunk0a的results.json→merge永远不会触发;且不检查chunk0_missing → kill PID3398461,启动final_watcher.sh(检查正确7chunk+7server) ④**taskset移8085**:112-167(HT)→56-83(socket1物理),消除socket0 3-way争用,chunk0b速率2.78→3.25/min(+17%) ⑤**🔥chunk0b瓶颈分裂**:kill chunk0b(3427/10048,ETA~34h),分2路:chunk0b_a(2510-3765,1256实例)on8085(56-83物理)+chunk0b_b(3766-5021,1256实例)on新server8082(112-167 HT,此前idle) ⑥**7th llama-server**:port8082,cores112-167(socket0 HT,此前56核全idle) ⑦**当前7个eval进程跨7个server**:8080(chunk1b_a,0-27phys)|8081(chunk1a_half2,84-111phys)|8082(chunk0b_b,112-167HT)|8084(chunk1b_b,28-55phys)|8085(chunk0b_a,56-83phys)|8086(chunk1a_half1,168-195HT)|8087(chunk0_missing,196-211HT) ⑧**新ETA**:bottleneck=chunk1a_half1/chunk1b_a~14.5h→finish~Nov8 22:30(原~Nov9 18:00,省~20h) ⑨S1健康(iter124000/700000,8GPU100%,~75GB/卡,step~7.5s) ⑩7集分数同#1650(boolq=0.600,sciq=0.316,winogrande=0.496,arc_easy=0.262,arc_challenge=0.219,openbookqa=0.184,piqa=0.540,Avg7=0.3740)·📦TASK=27.8KB✓/MEMORY=13.7KB✓(归档0KB)·未完成指令:有(v4 eval hellaswag 7chunk运行中→完成后:耗时对照表+8集分数+一致性校验+报告report_pretrain_cpu_eval_speedup_zh.html最终更新)⇒WAITING:0。
> 📦 §#1650（11-08 07:37, taskset CPU亲和性修复轮·chunk1a 1.6x提速）→ daily-memories/2026-11-08.md「#1650」节；**结论**：taskset修复8086→168-195HT+8081→84-111phys,chunk1a从22.9→14s/req(1.6x),省~12h。**#1651发现8083 DOWN+chunk0a死+watcher broken→分裂chunk0b瓶颈**。需要时再读。
> 📦 §#1649（11-08 07:30, 关键修复轮·chunk0a_half1已死→启动第6台server 8087补缺）→ daily-memories/2026-11-08.md「#1649」节；**结论**：7/8完成,chunk0a_half1已死+watcher空等8h→kill watcher+启动第6台server 8087(port8087,cores196-211)直接补缺samples 0-2509。需要时再读。
> 📦 §#1648（11-08 07:13, 优化轮·增强watcher加chunk0b检查）→ daily-memories/2026-11-08.md「#1648」节；**结论**：7/8完成,启动enhanced watcher v2(PID540135)检查chunk0b。**#1649发现chunk0a_half1已死+watcher空等8h→kill watcher+启动第6台server 8087直接补缺**。需要时再读。
> 📦 §#1647（11-08 07:01, 监控轮·5chunk稳步推进+ETA修正0.8-1天）→ daily-memories/2026-11-08.md「#1647」节；**结论**：7/8完成,5chunk@15-32%,ETA~0.8-1天,watcher检查8080/8081/8084。**#1648发现chunk0b最快但watcher未检查它→已优化**。需要时再读。
> 📦 §#1646（11-08 06:56, 监控轮·5chunk正常推进+8083无空闲核+ETA 1.7天）→ daily-memories/2026-11-08.md「#1646」节；**结论**：7/8完成,5chunk@14-32%,ETA 1.7天(被#1647修正为~0.8-1天,实测速率更高)。需要时再读。
> 📦 §#1645（11-08 06:46, 关键优化轮·kill 2旧watcher+chunk0_missing精准补缺）→ daily-memories/2026-11-08.md「#1645」节；**结论**：7/8完成,kill chunk0a_half1/half2冗余watcher,仅跑缺失0-2509(10040req vs旧20080req),ETA 4.7天→1.2天。**#1646确认chunk0a已死+8083无空闲核**。需要时再读。
> 📦 §#1643（11-08 06:11, 关键修复轮·chunk0a卡死进程修复+HT核竞争实验）→ daily-memories/2026-11-08.md「#1643」节；**结论**：7/8完成,chunk0a卡死已kill+重启chunk0a_half1于8083 HT核。**#1644发现HT核跑19.42s/it=107h瓶颈,已kill改8086物理核**。需要时再读。
> 📦 §#1642（11-08 05:48, 监控轮·chunk0a进度修正+HS总进度20.8%）→ daily-memories/2026-11-08.md「#1642」节；**结论**：7/8完成(Avg7=0.3740),HS 20.8%(8348/40180),chunk0a 33%(3358/10044),S1健康。**#1643发现chunk0a实际已卡死**。需要时再读。
> 📦 §#1641（11-08 05:38, 监控轮·HS进度推进+chunk0a误读47%）→ daily-memories/2026-11-08.md「#1641」节；**结论**：7/8完成(Avg7=0.3740),HS 23.4%(误读,实20.8%),chunk0a误读47%实33%(重启),S1健康。**#1642已修正**。需要时再读。
> 📦 §#1640（11-08 05:32, 监控轮·chunk0a进度修正）→ daily-memories/2026-11-08.md「#1640」节；**结论**：7/8完成(Avg7=0.3740),HS 19.1%(7659/40180),chunk0a=31%修正#1639误读,S1健康,ETA~20h。需要时再读。
> 📦 §#1639（11-08 05:24, 监控轮·chunk0a误读为100%完成）→ daily-memories/2026-11-08.md「#1639」节；**结论**：7/8完成(Avg7=0.3740),HS误报35.7%(chunk0a误读tokenizing100%为eval完成,实31%),S1健康。**#1640已修正**。需要时再读。
> 📦 §#1638（11-08 05:18, 监控轮·CPU pinning实验+报告修复）→ daily-memories/2026-11-08.md「#1638」节；**结论**：7/8完成(Avg7=0.3740),CPU pinning实验扩核无收益已revert,报告修复6 NUMA,HS 17.3%,chunk0a 29%。需要时再读。
> 📦 §#1637（11-08 05:01, 监控轮·修正chunk0a误读）→ daily-memories/2026-11-08.md「#1637」节；**结论**：7/8完成(Avg7=0.3740),HS 6chunk 15.2%,chunk0a=27%非47%误读已修正,报告15305B,S1健康。需要时再读。
> 📦 §#1636（11-08 04:55, 监控轮·hellaswag误报19.6%）→ daily-memories/2026-11-08.md「#1636」节；**结论**：7/8完成(Avg7=0.3740),HS 6chunk运行中,chunk0a进度误读为47%(实27%),报告15305B,维持暂不调NUMA。需要时再读。
> 📦 §#1635（11-08 04:45, 合并+报告更新轮）→ daily-memories/2026-11-08.md「#1635」节；**结论**：7/8合并到顶层results.json(Avg7=0.3740),报告修复read_live_progress+正则,15305B/0script/0ext,HS~19%。需要时再读。
> 📦 §#1634（11-08 04:34, NUMA HT竞争优化轮）→ daily-memories/2026-11-08.md「#1634」节；**结论**：8083限16HT核,8081扩56核获HT sibling~25%提速,8086移socket0失败已回退,decongest_v3部署,7/8完成HS~10%。需要时再读。
> 📦 §#1633（11-08 04:1x, NUMA修复轮·8085重绑定+decongest部署）→ daily-memories/2026-11-08.md「#1633」节；**结论**：8085重绑定到112-167(socket0 HT),decongest_v2部署,7/8完成HS运行中。需要时再读。
> 📦 §#1632（11-08 03:46, 监控轮·piqa即将完成）→ daily-memories/2026-11-08.md「#1632」节；**结论**：piqa_part1 100%/part2 98%,rebalance脚本等待触发,NUMA根因=8085核心重叠,HS 6chunk进度2-15%。需要时再读。
> 📦 §#1631（11-08 03:40, NUMA重平衡+chunk1a分裂）→ daily-memories/2026-11-08.md「#1631」节；**结论**：orchestrator已死,手写rebalance_and_split.sh后台启动等piqa完成,NUMA=2socket×56核,8083在HT,piqa ETA~31min。需要时再读。
> 📦 §#1630（11-08 03:22, 监控轮）→ daily-memories/2026-11-08.md「#1630」节；**结论**：v4 eval 6/8完成,piqa 89%,hs总13.4%,瓶颈chunk1a ETA~41h,S1健康。需要时再读。
> 📦 §#1629（11-08 03:10, NUMA重平衡干预）→ daily-memories/2026-11-08.md「#1629」节；**结论**：v4 eval 6/8完成,NUMA重平衡(3慢chunk HT→物理核),piqa 86-87%,hs总5372/40176(13.4%),瓶颈chunk1a ETA~41h。需要时再读。
> 📦 §#1627（11-08 02:26, 监控轮+进程修复）→ daily-memories/2026-11-08.md「#1627」节；**结论**：v4 eval 6/8完成,piqa 72%/piqa_part2 73%/hs_chunk0a新启,chunk1b 1%@8080,ETA~10:00-14:00。需要时再读。
> 📦 §#1626（11-08 02:07, 监控轮）→ daily-memories/2026-11-08.md「#1626」节；**结论**：v4 eval 6/8完成,piqa 67%/piqa_part2 70%/hs_chunk0a 44%,chunk1b启动,ETA~14:00-18:00。需要时再读。
> 📦 §#1625（11-08 01:53, 监控轮）→ daily-memories/2026-11-08.md「#1625」节；**结论**：v4 eval 5/8不变,openbookqa 25%,piqa_part2 62%,hs_chunk0a 41%,ETA~08-12:00 Nov8。需要时再读。

> 📦 §#1624（11-08 01:48, 监控轮）→ daily-memories/2026-11-08.md「#1624」节；**结论**：v4 eval 4/8不变,arc_challenge 98%即将done,piqa_part2 61%,hs_chunk0a 40%,ETA~06-10:00 Nov8。需要时再读。
> 📦 §#1623（11-08 01:39, 监控轮+杀重复进程）→ daily-memories/2026-11-08.md「#1623」节；**结论**：v4 eval 4/8不变,arc_challenge 86%,杀port8080重复arc_challenge孤儿进程消除竞争,报告重生成。需要时再读。
> 📦 §#1622（11-08 01:29, 监控轮+报告修复）→ daily-memories/2026-11-08.md「#1622」节；**结论**：v4 eval 4/8不变,arc_challenge 81%,报告修复4 NUMA+实时进度函数。需要时再读。
> 📦 §#1619-#1620（11-08 01:01-01:11, 2条监控轮）→ daily-memories/2026-11-08.md「#1619-#1620」节；**结论**：v4 eval 4/8不变,arc_challenge 67→71%,piqa_part2速度骤降70s/it后回落27s/it,hs_chunk0a 33%,ETA~10:00-13:00。需要时再读。
> 📦 §#1618（11-08 00:55, 监控轮）→ daily-memories/2026-11-08.md「#1618」节；**结论**：v4 eval 4/8不变,arc_challenge 63%,piqa_part2 48%,hs_chunk0a 30%,ETA~12:00-13:00 Nov8,4 servers全alive。需要时再读。

> 📦 §#1614-#1616（11-08 00:22-00:35, 3条监控轮）→ daily-memories/2026-11-08.md「归档 #1614-#1616」节；**结论**：v4 eval 4/8不变,GGUF精度回归PASS,piqa split+orchestration修复ETA~08-11h。需要时再读。
> 📦 §#1617（11-08 00:43, 监控轮+sample ordering调查解决）→ daily-memories/2026-11-08.md「#1617」节；**结论**：lm_eval --limit N=instances[:N]取前N非随机;10点scaling curve(全n=100)高估模型能力,full eval更真实;#1614"数学不一致"=误报(不同ckpt)。需要时再读。
> 📦 §#1580-#1613（11-07 14:26→11-08 00:05, ~34条v4 eval监控/精度回归/修复轮）→ daily-memories/2026-11-08.md「归档 #1580-#1613」节；**结论**：v4 eval从18:25启动→4/8完成@23:00(arc_easy/boolq/sciq/winogrande)→精度回归PASS(iter_10000 HF vs GGUF max Δacc=0.02)→piqa 2-way split+固定orchestration修复→ETA从22天→~11-17h(~08:00-11:00 Nov8). 需要时再读。
> 📦 §#1569-#1576（11-07 10:37-13:48, 8条例行监控轮）→ daily-memories/2026-11-07.md「归档 #1569-#1576」节；**结论**：S1健康全程0NaN/0skip,全量eval后台串行运行@~27s/req(ETA~22天),探测报告#1570已交付。需要时再读。



> 📦 §#1565（11-07 08:17, 监控轮·iter113620/700000）→ daily-memories/2026-11-07.md「归档 #1564-#1565」节；**结论**：S1健康0NaN/0skip,loss2.065,ckpt iter_0112000。需要时再读。



> 📦 §#1564（11-07 07:55, 监控轮·iter113440/700000）→ daily-memories/2026-11-07.md「归档 #1564-#1565」节；**结论**：S1健康0NaN/0skip,loss2.074,ckpt iter_0112000。需要时再读。


> 📦 §#1563（11-07 07:35, 监控轮·iter113260/700000）→ daily-memories/2026-11-07.md「归档 #1562-#1563」节；**结论**：S1健康0NaN/0skip,loss2.079,ckpt iter_0112000。需要时再读。



> 📦 §#1561（11-07 06:54, 监控轮·iter112920/700000）→ daily-memories/2026-11-07.md「#1561」节；**结论**：S1健康0NaN/0skip,loss2.075,ckpt iter_0112000。需要时再读。


> 📦 §#1562（11-07 07:16, 监控轮·iter113110/700000）→ daily-memories/2026-11-07.md「归档 #1562-#1563」节；**结论**：S1健康0NaN/0skip,loss2.075,ckpt iter_0112000。需要时再读。


> 📦 §#1560（11-07 06:32, 监控轮·iter112740/700000）→ daily-memories/2026-11-07.md「归档 #1560」节；**结论**：S1健康0NaN/0skip,loss2.074,latest ckpt iter_0112000,next iter_0114000 ETA~Nov7 09:00。被#1562确认延续。需要时再读。


> 📦 §#1559（11-07 06:12, 监控轮·iter112560/700000）→ daily-memories/2026-11-07.md「归档 #1558-#1559」节；**结论**：S1健康0NaN/0skip,loss2.064,latest ckpt iter_0112000,next iter_0114000 ETA~Nov7 09:00。需要时再读。


> 📦 §#1558（11-07 05:52, 监控轮·iter112400/700000）→ daily-memories/2026-11-07.md「归档 #1558-#1559」节；**结论**：S1健康0NaN/0skip,loss2.076,latest ckpt iter_0112000,next iter_0114000 ETA~Nov7 09:05。需要时再读。




> 📦 §#1043–#1555（11-01→11-07, S1健康监控iter41950→111880 + CPU eval 5ckpt + llama.cpp pilot + 100k eval交付, 共~500轮）→ daily-memories/2026-11-{01..07}.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.05–2.16稳态, ckpt iter_38000→116000, 100k eval已交付(10/10,Avg harness 57.75%), llama.cpp pilot=FAIL(保留HF float32), CPU eval thread scaling报告已交付. 需要时再读 daily-memories。


---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实�