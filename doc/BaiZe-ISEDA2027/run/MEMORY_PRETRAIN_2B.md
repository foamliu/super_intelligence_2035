# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-09 02:30 #1754: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·piqa40%/c0 43%/c1 34%/c2 13%/c3 6%·全部推进·异常调查交付物已完成(报告+结论A)·训练健康**·**动作**:①git fetch(proxy,synced,behind0) ②5 llama-server全活(8183-8187,health=ok×5,etime~5h51m) ③5 client全活(1 piqa+4 hellaswag) ④**精确进度(tqdm@02:30)**:piqa 1487/3676(40%,~30s/it,ETA~18h→~20:30)·hs_c0 4348/10044(43%,~4s/it,ETA~6h→~08:30←最快)·hs_c1 3462/10044(34%,~12s/it,ETA~20h→~22:30)·hs_c2 1312/10044(13%,~10s/it,ETA~22h→Nov10~00:30)·hs_c3 636/10036(6%,~30s/it,ETA~73h→Nov12←瓶颈) ⑤**自#1753增量(~16min)**:piqa+63/c0+219/c1+61/c2+66/c3+43→全部推进无停滞 ⑥**异常调查(15:3x令)交付物状态=已完成**:报告report_pretrain_eval_avg7_anomaly_zh.html(27KB,6项全覆盖+phase2稳定,结论A)+speedup报告(17KB)均已commit;v4逐集(arc_cx21.9%/arc_ex26.2%/boolq60%/obqa18.4%/sciq31.6%/wgrille49.6%/piqa54.0%→Avg7=37.40%)vs v5逐集(arc_cx30.4%/arc_ex65.5%/boolq58.7%/obqa26.6%/sciq84.2%/wgrille54.9%→Avg6=53.38%)对照=旧二进制致sciq+52.6pp/arc_ex+39.4pp/arc_cx+8.5pp/obqa+8.2pp,根因铁证 ⑦训练.29健康:iter~132000/700000,8×H100 96-100%util~75GB/卡 ⑧📦TASK=31.2KB/MEMORY=18.5KB(均≤32KB无需归档)·未完成指令:有(运维令15:3x标签仍"未完成",待8集完成后更新报告终版)⇒WAITING:0。
> 📦 #1753（11-09 02:14, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,全部推进无停滞,rebalance watcher v2活。需要时再读。
> 📦 #1752（11-09 02:08, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,全部推进无停滞。需要时再读。
> 📦 #1751（11-09 02:03, v6 eval监控轮·rebalance watcher升级）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,rebalance watcher从等piqa升级为等chunk0(省1h),全部推进无停滞。需要时再读。
> 📦 #1750（11-09 01:49, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,全部推进无停滞。需要时再读。
> 📦 #1749（11-09 01:45, v6 eval监控轮+归档）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done不变,归档#1735-37释放3.3KB。需要时再读。
> 📦 #1748（11-09 01:37, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,全部推进无停滞,报告v3.8已交付。需要时再读。
> 📦 #1747（11-09 01:31, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,全部推进无停滞,报告v3.8覆盖6项全。需要时再读。
> 📦 #1746（11-09 01:22, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,chunk3瓶颈30-55s/it,全部推进无停滞。需要时再读。
> 📦 #1745（11-09 01:15, v6 eval监控+chunk3再分配watcher启动）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,chunk3再分配watcher已启动(等piqa完成→迁chunk3至Node0)。需要时再读。
> 📦 #1744（11-09 01:03, v6 eval监控·NUMA修复验证chunk3 40→17.4s/it）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,chunk3 NUMA修复2.3x改善但仍6.3x慢于chunk0。需要时再读。
> 📦 #1743（11-09 00:55, v6 eval监控+NUMA拓扑纠正）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,发现chunk3=40s/it根因=客户端跨NUMA+HT争抢,已修复3个客户端affinity。需要时再读。
> 📦 #1742（11-09 00:43, v6 eval监控轮·results.json验证）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%(results.json已验证),异常报告v3.8已commit结论A,chunk2=59h瓶颈。需要时再读。

> 📦 #1741（11-09 00:39, v6 eval监控·逐集对照完成）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,逐集对照iter_112000全量vs iter_100000限100差仅-0.45pp,结论A铁证。需要时再读。

> 📦 #1740（11-09 00:32, v6 eval监控+chunk3 NUMA修复+正确active log读取）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,纠正stale log误读,piqa ETA大幅改善~2.8h,chunk3 NUMA修复taskset钉Node1。需要时再读。

> 📦 #1739（11-09 00:21, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,进度确认推进,两报告已交付结论A。需要时再读。

> 📦 #1738（11-09 00:10, v6 eval监控·NUMA修复验证生效·带宽争抢诊断）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,NUMA修复验证生效,带宽争抢是新瓶颈,异常报告v3.8已更新结论A铁证。需要时再读。

> 📦 §#1737（11-08 23:58, v6 eval监控+NUMA亲和性修复·5s+5c全活·6/8done·异常报告v3.7结论A）→ daily-memories/2026-11-08.md「#1737」节；**结论**：chunk2/piqa跨NUMA瓶颈已taskset修复,Avg6=53.38%不变,报告v3.7结论A。需要时再读。

> 📦 §#1736（11-08 23:50, v6 eval监控·5s+5c全活·6/8done·报告v3.6进度更新）→ daily-memories/2026-11-08.md「#1736」节；**结论**：5s+5c全活,Avg6=53.38%不变,chunk0仅23%未完成无法再分配。需要时再读。

> 📦 §#1735（11-08 23:42, v6 eval监控·5s+5c全活·6/8done·chunk2瓶颈ETA57h·异常报告v3.5）→ daily-memories/2026-11-08.md「#1735」节；**结论**：5s+5c全活,Avg6=53.38%不变,chunk2=21.87s/it瓶颈ETA~57h,报告v3.5结论A铁证。需要时再读。

> 📦 §#1734（11-08 23:34, v6 eval监控·5s+5c全活·6/8done·精确速率+再分配计划）→ daily-memories/2026-11-08.md「#1734」节；**结论**：5s+5c全活,Avg6=53.38%不变,精确速率piqa12.6s/doc/hs_c0 4.2s/doc,再分配计划chunk1/0完成→chunk3/2迁Node0。需要时再读。

> 📦 §#1733（11-08 23:24, v6 eval监控+chunk3 Node1重启·5s+5c全活·异常调查已完成结论A）→ daily-memories/2026-11-08.md「#1733」节；**结论**：chunk3重启于Node1 cores96-111,5s+5c全活,Avg6=53.38%不变,报告v3.4结论A确认。需要时再读。

> 📦 §#1732（11-08 23:10, v6 eval监控轮·4s+4c全活2.58h无SIGTERM·异常调查报告v3.4验证完整·结论A铁证）→ daily-memories/2026-11-08.md「#1732」节；**结论**：4s+4c全活,Avg6=53.38%不变,报告v3.4全覆盖6项,结论A确认。需要时再读。

> 📦 §#1731（11-08 23:12, v6 eval监控+chunk3 NUMA修复尝试(失败回滚)·4s+4c活）→ daily-memories/2026-11-08.md「#1731」节；**结论**：chunk3 NUMA修复尝试失败(Node0 3server带宽争抢致piqa暴跌),回滚,chunk3暂停待piqa完成。需要时再读。

> 📦 §#1727（11-08 22:16, v5 eval监控轮·5s+5c全活·6/8done Avg6=53.38%·hs_chunk3=70h瓶颈）→ daily-memories/2026-11-08.md「#1727」节；**结论**：5s+5c全活(后被第4次SIGTERM杀死),Avg6=53.38%不变,报告v3.2已交付结论A。需要时再读。

> 📦 §#1728（11-08 22:30, v6 eval重启轮·第4次SIGTERM后重建·5s+5c全活·6/8done Avg6=53.38%不变·结论A铁证）→ daily-memories/2026-11-08.md「#1728」节；**结论**：v6重启5s+5c全活,Avg6=53.38%不变,报告v3.3已交付。需要时再读。

> 📦 §#1729（11-08 22:37, v6 eval监控轮·2h稳定无SIGTERM·精确进度piqa13.6%/hs4.2%·报告v3.4）→ daily-memories/2026-11-08.md「#1729」节；**结论**：5s+5c全活2h无SIGTERM,Avg6=53.38%不变,piqa13.6%/hs4.2%,报告v3.4已更新。需要时再读。

> 📦 §#1726（11-08 22:09, v5 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·异常报告v3.2已验全6项覆盖）→ daily-memories/2026-11-08.md「#1726」节；**结论**：5s+5c全活,Avg6=53.38%不变,报告v3.2已验证全6项覆盖,结论A确认。需要时再读。

> 📦 §#1725（11-08 22:02, v5 eval监控轮·5s+5c全活·piqa10%+hs6.1%·报告v3.2）→ daily-memories/2026-11-08.md「#1725」节；**结论**：5s+5c全活,Avg6=53.38%不变,报告v3.2已更新,结论A不变。需要时再读。

> 📦 §#1724（11-08 21:56, v5 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变）→ daily-memories/2026-11-08.md「#1724」节；**结论**：5s+5c全活,Avg6=53.38%不变,无server被杀,两报告已交付。需要时再读。

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