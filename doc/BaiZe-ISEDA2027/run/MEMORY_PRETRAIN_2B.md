# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-08 23:42 #1735: **v6 eval监控·5s+5c全活·6/8done Avg6=53.38%不变·chunk2瓶颈ETA57h·异常报告v3.5已交付结论A铁证**·**动作**:①git fetch+status(synced,仅vision/harness在途) ②5 llama-server全活(8183-8187 health=ok,8183/8185/8186 etime~3h4m,8184~2h51m,8187~18min) ③5 client全活(piqa PID2097184/hs_c0 PID3765473/hs_c1 PID2097209/hs_c2 PID2097234/hs_c3 PID2669799) ④**精确进度(tqdm)**:piqa 724/3676(20%,18.46s/it,ETA~15h)·hs_c0 2132/10044(21%,4.23s/it,ETA~9h←最快最先完成)·hs_c1 2498/10044(25%,9.43s/it,ETA~20h)·hs_c2 683/10044(7%,21.87s/it,ETA~57h←瓶颈!)·hs_c3 66/10036(1%,7.67s/it,ETA~21h,刚重启18min warming up) ⑤v5已完成6集逐集对照(iter_112000 full vs iter_100000 limit=100):arc_c 0.3038vs0.30(Δ+0.38pp)/arc_e 0.6553vs0.57(Δ+8.53pp)/boolq 0.5872vs0.67(Δ-8.28pp)/obqa 0.266vs0.21(Δ+5.6pp)/sciq 0.842vs0.88(Δ-3.8pp)/wino 0.5485vs0.60(Δ-5.15pp)→Avg6=53.38%vs53.83%差仅-0.45pp ⑥异常报告v3.5(33.7KB)已commit(41b6a7a8d)全覆盖6项+§4phase2稳定性+§八loss曲线+§九GGUF转换,结论A(二因叠加:旧二进制+全量vs限100) ⑦**再分配计划**:chunk0完成(~9h)→kill Node1 chunk2,用释放的8184(Node0)重启chunk2剩余samples·Node0速度~4s/doc可使chunk2 ETA从57h降至~15h ⑧训练.29健康8×H100 **计划**:下次唤醒①确认5s+5c存活②若chunk0已完成→执行chunk2再分配到Node0③监控piqa/chunk1进度④📦TASK=31.2KB/MEMORY=16.9KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。

> 2026-11-08 23:34 #1734: **v6 eval监控·5s+5c全活·6/8done Avg6=53.38%不变·精确速率+再分配计划**·**动作**:①git fetch+status(synced,仅vision/harness在途) ②5 llama-server全活(8183-8187 health=ok,etime~2h56m) ③5 client全活(piqa PID2097184/hs_c0 PID3765473/hs_c1 PID2097209/hs_c2 PID2097234/hs_c3 PID2669799) ④**精确进度(8min增量算真实速率)**:piqa 692/3676(18.8%,12.6s/doc ETA~10.5h)·hs_c0 2047/10044(20.4%,4.2s/doc ETA~9.3h)·hs_c1 2396/10044(23.9%,3.7s/doc ETA~7.9h←最先完成)·hs_c2 652/10044(6.5%,13.7s/doc ETA~36h←瓶颈)·hs_c3 26/10036(0.26%,22.9s/doc warming up ETA~64h但会改善) ⑤NUMA核实:chunk2/3 server内存页在N0但CPU在Node1=跨NUMA慢(~3x) ⑥**再分配计划**(下几轮执行):chunk1完成(~8h)→kill Node1 chunk3,用释放的8185(Node0)重启chunk3剩余samples·chunk0完成(~9h)→kill Node1 chunk2,用释放的8184(Node0)重启chunk2剩余samples·Node0速度~4-6s/doc可使chunk2/3从36h/64h降至~15h/16h ⑦异常报告v3.4(33.7KB)已验全覆盖6项(分集明细/逐集/样本数/后端/精度/fewshot/hellaswag进度/iter_100000/口径/结论A) ⑧训练.29健康8×H100 71-100%util~75GB/卡 **计划**:下次唤醒①确认5s+5c存活②若chunk1已完成→执行chunk3再分配到Node0③监控chunk0/piqa进度④📦TASK=31.2KB/MEMORY=15.5KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。

> 2026-11-08 23:24 #1733: **v6 eval监控+chunk3 Node1重启·5s+5c全活·6/8done Avg6=53.38%不变·异常调查已完成结论A**·**动作**:①git fetch+status(synced,仅vision/harness在途) ②验证4s+4c活(8183-8186 OK,8187 DOWN=chunk3停) ③精确进度:piqa654/3676(18%,34s/it ETA~28h)·hs_c0 1933/10044(19%,2.6s/it ETA~6h←加速)·hs_c1 2266/10044(23%,4s/it ETA~9h)·hs_c2 617/10044(6%,9s/it ETA~24h) ④**chunk3重启决策**:原策略"等piqa完成(~21h)再重启chunk3"=总ETA~50h·改为"chunk3重启于Node1 cores96-111(原位)"=3 server暂占Node1,chunk1~9h完成释放带宽,总ETA~28h(改善~22h) ⑤**执行**:创建/tmp/baize_eval_v5/restart_chunk3_node1.sh·二进制MD5=f95ac952校验PASS·server PID2665866 port8187 health=ok·client PID2669799 已启动(docs7533-10041,2509docs)·chunk3 warming up 5/10036(10.4s/it) ⑥**影响评估**:piqa 25→34s/it(1.36x慢,可接受)·chunk0 7.4→2.6s/it(加速!Node0未受影响)·chunk1 3→4s/it(微慢)·chunk2 9→9s/it(不变) ⑦异常调查报告v3.4(32KB)已完成:结论A(口径差异,非真实下降),二因叠加(旧二进制bug+全量vs限100),v5全量Avg6=53.38% vs 历史限100 Avg6=53.83%差仅-0.45pp ⑧训练.29健康8×H100 100%util~75GB/卡 **计划**:下次唤醒①确认5s+5c存活②监控piqa/chunk3进度③chunk0完成后piqa应加速至~5s/it④全部8集完成后更新报告终版⑤📦TASK=31.2KB/MEMORY=14.5KB·未完成指令:有(v6 eval 5任务运行中)⇒WAITING:0。

> 📦 §#1732（11-08 23:10, v6 eval监控轮·4s+4c全活2.58h无SIGTERM·异常调查报告v3.4验证完整·结论A铁证）→ daily-memories/2026-11-08.md「#1732」节；**结论**：4s+4c全活,Avg6=53.38%不变,报告v3.4全覆盖6项,结论A确认。需要时再读。

> 2026-11-08 23:12 #1731: **v6 eval监控+chunk3 NUMA修复尝试(失败回滚)·4s+4c活(chunk3已停)·piqa正在恢复·Avg6=53.38%不变**·**动作**:①git fetch+status(synced) ②确认5s+5c全活·精确进度piqa546/3676(15%,5.3s/it)·hs_c0 1454/10044(14%,5.1s/it)·hs_c1 1702/10044(17%,3.2s/it)·hs_c2 470/10044(5%,15.8s/it←瓶颈)·hs_c3 473/10036(5%,12.5s/it) ③**NUMA分析**:NUMA拓扑=Node0(cores0-55,112-167)/Node1(cores56-111,168-223)·GGUF页缓存76%在Node0·Node1有3 server(chunk1/2/3)×16线程争抢跨NUMA带宽=chunk2/3慢3-5x ④**chunk3 NUMA修复尝试**:kill chunk3(473/10036进度丢失)·taskset -c 16-31重启server于Node0·client需HF_OFFLINE=1(首次因缺env失败已修)·新chunk3速度8.5s/it(vs旧12.5s/it,warming up) **但piqa从5.3s/it暴跌至24.6s/it**(Node0 3 server带宽争抢) ⑤**回滚**:kill新chunk3于Node0·piqa正在恢复(实测6.7s/item,移动平均仍24.6) ⑥**策略**:chunk3暂停·待piqa完成(~4.5h后)再于Node0 cores32-47重启chunk3·预计总ETA~18h ⑦6/8done不变Avg6=53.38% ⑧报告v3.4不变·异常调查已完成结论A ⑨训练.29健康8×H100 100%util~75GB/卡 **计划**:下次唤醒①确认piqa已恢复至~5s/it②监控4任务进度③piqa完成后于Node0启动chunk3④📦TASK=31.2KB/MEMORY=13.6KB·未完成指令:有(v6 eval运行中,chunk3暂停)⇒WAITING:0。

> 📦 §#1727（11-08 22:16, v5 eval监控轮·5s+5c全活·6/8done Avg6=53.38%·hs_chunk3=70h瓶颈）→ daily-memories/2026-11-08.md「#1727」节；**结论**：5s+5c全活(后被第4次SIGTERM杀死),Avg6=53.38%不变,报告v3.2已交付结论A。需要时再读。

> 📦 §#1728（11-08 22:30, v6 eval重启轮·第4次SIGTERM后重建·5s+5c全活·6/8done Avg6=53.38%不变·结论A铁证）→ daily-memories/2026-11-08.md「#1728」节；**结论**：v6重启5s+5c全活,Avg6=53.38%不变,报告v3.3已交付。需要时再读。

> 2026-11-08 22:37 #1729: **v6 eval监控轮·2h稳定无SIGTERM·精确进度piqa13.6%/hs4.2%·报告v3.4**·**动作**:①git fetch+status(synced,only vision/harness in-flight) ②确认5 llama-server(port8183-8187)全活health=ok×5,etime=7138s(~2h,20:34重启后无第5次SIGTERM) ③确认5 eval client全活(PID2097184=piqa/2097193+2097209+2097234+2097251=hs4shard,etime=7127s) ④精确进度(client tqdm):piqa 502/3676(13.6%,~14s/it,ETA~12h)·hellaswag 4shard各~417/10036(4.2%,~17s/it,ETA~46h) ⑤6/8done不变Avg6(acc)=53.38%(arc_c=0.304/arc_e=0.655/boolq=0.587/obqa=0.266/sciq=0.842/wg=0.549) ⑥报告v3.4更新(piqa/hs精确进度+2h无SIGTERM) ⑦训练.29健康8×H100 100%util~75GB/卡 **计划**:下次唤醒①确认5s+5c存活②监控piqa/hs进度(piqa~12h完成,hs~46h)③piqa完成后合并7集④全部8集完成后更新报告终版⑤📦TASK=31.2KB/MEMORY=12.2KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。

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