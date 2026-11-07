# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-08 03:05 #1628: 运维令11-07 15:2x·**hellaswag 5路并行优化**·①v4 eval(112k)进度@03:05:**6/8完成**(arc_easy 0.2618+arc_challenge 0.2193+boolq 0.60+openbookqa 0.184+sciq 0.316+winogrande 0.4964);运行中=piqa **85%(1555/1838@~20s/it,ETA~1.5h)**;hellaswag **5 chunk并行**:chunk0a 47%(4693/10040@10s/it,8083独占),chunk0b 1%(82/10048@2.8s/it,8085新),chunk1a 0%(18/10044@14s/it,8086新),chunk1b_a 1%(55/5024@13s/it,8080),chunk1b_b 0%(4/5020,8084新)·②**关键优化:杀orchestrate(防重复启动chunk0b/chunk1a)+杀chunk1b(仅1%可弃)+启动3新server(8084-8086,taskset 0-55/56-111/112-167)+5路并行**→原来只有chunk0a+chunk1b跑(其余3等piqa完),现5路同跑·③chunk1b已拆为chunk1b_a(7531-8786)+chunk1b_b(8787-10041)各1255doc·④merge脚本v2已就绪(/tmp/baize_eval_v4/merge_parallel_results_v2.py)支持hs_chunk*+piqa_part*·⑤ETA:piqa~04:30done→释放8081/8082→可帮跑慢chunk→hs总done~08:00-12:00 Nov8·⑥训练健康·⑦git up-to-date·📦TASK=27.8KB✓/MEMORY=7.5KB✓(归档0KB)·未完成指令:有(v4 eval运行中→完成后:耗时对照表+8集分数+一致性校验+报告最终更新)⇒WAITING:0。
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