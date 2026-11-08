# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-08 21:56 #1724: **v5 eval监控轮·5s+5c全活·6/8done Avg6(acc)=53.38%/Avg6(norm)=51.25%不变·piqa+4hs chunk运行中·无server被杀·训练健康**·**动作**:①git fetch+status(synced,HEAD=vision#928 21:53) ②5 llama-server全活(8183-8187,固定二进制code/llama.cpp/build,MD5=f95ac952,bz2b-112000-f16.gguf) ③5 eval client全活:piqa(PID2097184,port8183,~80min)+hs_c0(PID3765473,port8184,~64min←NUMA修复版)+hs_c1(PID2097209,port8185,~80min)+hs_c2(PID2097234,port8186,~80min)+hs_c3(PID2097251,port8187,~80min) ④6/8done不变:arc_c=0.3038/n1172·arc_e=0.6553/n2376·boolq=0.5872/n3270·obqa=0.266/n500·sciq=0.842/n1000·wino=0.5485/n1267→Avg6(acc)=53.38% ⑤5个运行中输出目录仍空(results.json仅完成时写) ⑥训练.29健康8×H100=91-100%~75GB/pretrain_launcher PID146283活/iter~131000/700k ⑦两报告已交付:异常调查31KB v3.1结论A(口径差异非真实下降)+speedup17KB **计划**:下次唤醒①⭐确认5 server存活(防再被SIGTERM)②监控eval→待piqa+4hs完成→算Avg8+更新异常报告终版③📦TASK=31.2KB/MEMORY=10.8KB·未完成指令:有(v5 eval运行中)⇒WAITING:0。

> 📦 §#1723（11-08 21:49, v5 eval监控轮·5s+5c全活·chunk2瓶颈22s/it ETA~59h）→ daily-memories/2026-11-08.md「#1723」节；**结论**：5s+5c全活,Avg6=53.38%不变,chunk0 NUMA修复后2.3s/it最快,chunk2=22s/it瓶颈。需要时再读。

> 📦 §#1722（11-08 21:37, v5 eval监控轮·5s+5c全活·chunk3瓶颈27s/it）→ daily-memories/2026-11-08.md「#1722」节；**结论**：5s+5c全活,Avg6=53.38%不变,chunk3=27s/it瓶颈ETA~74h。需要时再读。

> 📦 §#1721（11-08 21:27, v5 eval监控轮·tqdm精确进度·hs chunk2/3木桶3x慢）→ daily-memories/2026-11-08.md「#1721」节；**结论**：5s+5c全活,Avg6=53.38%不变,chunk2/3比chunk0/1慢3x,不rebalance。需要时再读。

> 📦 §#1720（11-08 21:17, v5 eval监控轮·5 server全活·speedup报告§六已更新·异常调查已完成）→ daily-memories/2026-11-08.md「#1720」节；**结论**：5 server全活,Avg6=53.38%不变,报告§六更新v5正确分数,异常调查运维令(15:3x)已完成结论A。需要时再读。

> 📦 §#1719（11-08 21:0x, v5 eval确认存活轮·5 server全活·异常调查已完成）→ daily-memories/2026-11-08.md「#1719」节；**结论**：5 server全活,4/5原始client存活+chunk0 NUMA修复版,piqa 4.1%/hs 1.8%,异常调查报告v3.1已交付结论A。需要时再读。

> 📦 §#1718（11-08 20:55, v5 eval NUMA修复轮·chunk0跨NUMA瓶颈4.3→29tok/s）→ daily-memories/2026-11-08.md「#1718」节；**结论**：chunk0(8184)被pin到跨NUMA cores48-63→4.3tok/s, kill+重启于cores0-15(纯node0)→29tok/s(6.7x), Avg6=53.38%不变。需要时再读。

> 📦 §#1717（11-08 20:34, v5 eval恢复轮·5 server被SIGTERM·从零重启piqa/hs）→ daily-memories/2026-11-08.md「#1717」节；**结论**：5 server被外部SIGTERM(~20:12), 客户端空转挂起, kill+从零重启, 6/8不变Avg6=53.38%。需要时再读。

> 📦 §#1716（11-08 20:28, v5 eval监控轮·6/8done·报告v2.9·5 llama-server全活[实为误报]）→ daily-memories/2026-11-08.md「#1716」节；**结论**：v5 6/8不变Avg6=53.38%,报告v2.9,但"5 server全活"系误报(实际~20:12已死),由#1717发现并修复。需要时再读。

> 📦 §#1715（11-08 20:13, v5 eval监控轮·6/8done·报告v2.8·投影Avg8）→ daily-memories/2026-11-08.md「#1715」节；**结论**：v5 6/8不变Avg6=53.38%,报告v2.8,运维令6项全覆盖结论A确认。需要时再读。

> 📦 §#1714（11-08 20:02, v5 eval监控轮·6/8done·报告v2.7·arc_easy完成）→ daily-memories/2026-11-08.md「#1714」节；**结论**：v5 6/8完成Avg6=53.38%,报告v2.7。需要时再读。

> 📦 §#1713（11-08 19:49, v5 eval监控轮·5/8done·报告v2.5·吞吐瓶颈说明）→ daily-memories/2026-11-08.md「#1713」节；**结论**：v5 5/8完成Avg5=50.95%,报告v2.5更新hellaswag shard表+吞吐瓶颈说明。需要时再读。

> 📦 §#1712（11-08 19:38, v5 eval监控轮·5/8done·报告v2.4·归档#1700-#1709）→ daily-memories/2026-11-08.md「#1712」节；**结论**：v5 5/8完成Avg5=50.95%,报告v2.4,归档释放MEMORY2.1KB。需要时再读。

> 📦 §#1711（11-08 19:30, v5 eval监控轮·5/8done·报告v2.3+hellaswag shard明细·运维令6项全覆盖）→ daily-memories/2026-11-08.md「#1711」节；**结论**：v5 5/8完成Avg5=50.95%,运维令6项全覆盖,结论A确认。需要时再读。

> 📦 §#1700-#1709（11-08 17:33-19:12, 10轮v5 eval监控·0→5/8done·报告v1→v2.3迭代）→ daily-memories/2026-11-08.md「#1700-#1709」节；**结论**：v5 eval从0→5/8完成,报告从v1迭代至v2.3覆盖6项+结论A。需要时再读。

> 🔑 **v5五集结果(19:19)**: arc_challenge=0.3038/boolq=0.5872/openbookqa=0.266/sciq=0.842/winogrande=0.5485 → **v5 Avg5=50.95%**,远高于v4 Avg7=37.4%,接近历史limit=100 Avg8=54.75%。结论A(口径差异)确认。

> 📦 §#1696-#1697（11-08 16:56-17:12, 根因定位+v5修复版eval启动）→ daily-memories/2026-11-08.md「#1696-#1697」节；**结论**：根因=v4旧二进制(sciq 0.44→0.88),v5修复版二进制MD5=f95ac952,11路并行eval启动。需要时再读。
> 📦 §#1696（11-08 16:56, Avg7=37.40%异常根因定位=llama-server旧二进制回归·决定性实验sciq旧0.44/新0.88·报告15KB·结论A口径差异）→ daily-memories/2026-11-08.md「#1696」节；**结论**：根因=v4用旧二进制(tools/llama.cpp,缺nemotron-h logits修复)，同GGUF旧sciq=0.44/新sciq=0.88，loss平滑无退化，结论A非真实下降，报告report_pretrain_eval_avg7_anomaly_zh.html已交付。需要时再读。
> 📦 §#1694（11-08 15:25, phase2误杀chunk0_missing(70%丢失)→修复+恢复+切v4 watcher·S1 iter~128000/700k）→ daily-memories/2026-11-08.md「#1694」节；**结论**：phase2误杀chunk0_missing导致docs 0-1757覆盖缺口→#1695创建fill_gap脚本修复。需要时再读。
> 📦 §#1623-#1692（11-08 01:39-14:55, ~70轮v4 eval监控/phase2再分配/NUMA修复）→ daily-memories/2026-11-08.md「#1623-#1692」节；**结论汇总**：v4 eval 7/8完成Avg7=37.4%(旧二进制),hellaswag 6chunk逐步推进,phase2动态再分配多次修复(get_port/find_free_port/port unbound),NUMA重平衡多次(chunk0a卡死/HT核竞争/跨NUMA带宽),S1训练全程健康iter~127-128k。需要时再读。

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