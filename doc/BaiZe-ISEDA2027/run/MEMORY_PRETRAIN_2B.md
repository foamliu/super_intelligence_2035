# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-09 01:49 #1750: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·piqa 36%/c0 37%/c1 33%/c2 12%/c3 5%·全部推进无停滞·rebalance watcher仍活·报告v3.8已交付·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183/8185/8186 etime~5h13m·8184~4h58m·8187~2h25m=chunk3重启版) ③5 client全活(PID2097184 piqa/3765473 hs_c0/2097209 hs_c1/2097234 hs_c2/2669799 hs_c3) ④**精确进度(tqdm@01:49)**:piqa 1307/3676(36%,~10-45s/it,ETA~6-7h→~08:00)·hs_c0 3740/10044(37%,~4.8s/it,ETA~8.4h→~10:15)·hs_c1 3313/10044(33%,~26s/it,ETA~49h→Nov11)·hs_c2 1157/10044(12%,~20s/it,ETA~50h→Nov11)·hs_c3 493/10036(5%,~9-17s/it,ETA~24h←瓶颈Node1,待piqa完成触发rebalance) ⑤**自#1749增量(~4min)**:piqa+25/c0+94/c1+19/c2+24/c3+33→全部推进无停滞 ⑥**chunk3再分配watcher仍活(PID1390395,etime~33min)**:监控piqa完成→迁chunk3 Node1(8187)→Node0(8183)→预期2.8x加速 ⑦报告v3.8(35.9KB)已交付:结论A(口径差异=旧二进制+全量vs限100),6集Avg6=53.38%≈历史53.83%差-0.45pp ⑧训练.29健康:iter~132000+/700000,8×H100 65-100%util~75GB/卡,latest ckpt iter_0132000,TB:6006可达 ⑨research日报无11-09版(06:00未到) ⑩📦TASK=31.9KB/MEMORY=~31.5KB·未完成指令:有(v6 eval运行中,待8集完成后更新报告终版)⇒WAITING:0。
> 2026-11-09 01:45 #1749: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·piqa 35%/c0 36%/c1 33%/c2 11%/c3 5%·全部推进无停滞·rebalance watcher仍活·归档#1735-37释放3.3KB·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183/8185/8186 etime~5h7m·8184~4h52m·8187~2h19m=chunk3重启版) ③5 client全活(PID2097184 piqa/3765473 hs_c0/2097209 hs_c1/2097234 hs_c2/2669799 hs_c3) ④**精确进度(tqdm@01:43)**:piqa 1282/3676(35%,~4s/it,ETA~2.7h→~04:20)·hs_c0 3646/10044(36%,~5s/it,ETA~9h→~10:30)·hs_c1 3294/10044(33%,~10-20s/it,ETA~18h→~19:30)·hs_c2 1133/10044(11%,~10-13s/it,ETA~24h→~01:30 Nov10)·hs_c3 460/10036(5%,~15-22s/it,ETA~40h←瓶颈Node1) ⑤**自#1748增量(~8min)**:piqa+40/c0+71/c1+25/c2+27/c3+21→全部推进无停滞 ⑥**chunk3再分配watcher仍活(PID1390395,etime~28min)**:监控piqa client退出→迁chunk3 Node1(8187)→Node0(8183)→预期2.8x加速;piqa 35%→ETA~2.7h后触发 ⑦**MEMORY归档**:搬#1735-#1737原文(已在daily-memories/2026-11-08.md)→3行指针,MEMORY 33.3KB→30.0KB(-3.3KB) ⑧报告v3.8(35.9KB)已交付:结论A(口径差异=旧二进制+全量vs限100),6集Avg6=53.38%≈历史53.83%差-0.45pp ⑨训练.29健康:iter133270/700000,loss2.044,0NaN/0skip,~7.4s/step,~970TFLOP/s ⑩📦TASK=31.9KB/MEMORY=30.0KB(归档3.3KB→daily-memories/2026-11-08.md)·未完成指令:有(v6 eval运行中,待8集完成后更新报告终版)⇒WAITING:0。
> 📦 #1748（11-09 01:37, v6 eval监控轮）已归档 → daily-memories/2026-11-09.md；**结论**：5s+5c全活,6/8done Avg6=53.38%不变,全部推进无停滞,报告v3.8已交付。需要时再读。
> 2026-11-09 01:31 #1747: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·piqa 33%/c0 35%/c1 32%/c2 11%/c3 5%·全部推进无停滞·rebalance watcher仍活·报告v3.8已交付覆盖6项全·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183/8185/8186 etime~4h53m·8184 etime~4h39m·8187 etime~2h6m) ③5 client全活(PID2097184 piqa/3765473 hs_c0/2097209 hs_c1/2097234 hs_c2/2669799 hs_c3) ④**精确进度(tqdm@01:31)**:piqa 1217/3676(33%,~12-26s/it,ETA~8-18h)·hs_c0 3485/10044(35%,~4-10s/it,ETA~8h)·hs_c1 3243/10044(32%,~11-28s/it,ETA~22h)·hs_c2 1090/10044(11%,~8.5-14s/it,ETA~29h)·hs_c3 492/10036(5%,~12-15s/it,ETA~35h←瓶颈Node1) ⑤**自#1746增量(~9min)**:piqa+30/c0+75/c1+32/c2+31/c3+86→全部推进无停滞 ⑥**chunk3再分配watcher仍活(PID1390395,etime~15min)**:监控piqa完成→迁chunk3至Node0;piqa 33%→ETA~8h后触发 ⑦**报告v3.8(35.9KB)已交付**:结论A(口径差异=旧二进制+全量vs限100),覆盖6项全(分集明细/样本数/后端精度/fewshot=zero-shot/hs进度/iter_100000对照)+phase2稳定性;6集Avg6=53.38%≈历史53.83%差-0.45pp ⑧训练.29健康:8×H100 100%util~75GB/卡 ⑨research日报11-08已查(无11-09新版),无新增指令 ⑩📦TASK=31.2KB/MEMORY=29.7KB·未完成指令:有(v6 eval运行中,待8集完成后更新报告终版)⇒WAITING:0。
> 2026-11-09 01:22 #1746: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·piqa 32%/c0 34%/c1 32%/c2 11%/c3 4%·chunk3仍是瓶颈(30-55s/it)·rebalance watcher等待piqa完成·两报告已交付·训练健康**·**动作**:①git fetch+status(ahead1,behind0) ②5 llama-server全活(8183-8187,health=ok×5) ③5 client全活(PID2097184 piqa/3765473 hs_c0/2097209 hs_c1/2097234 hs_c2/2669799 hs_c3,etime~4h46m) ④**精确进度(tqdm@01:22)**:piqa 1187/3676(32%,~14s/it近期,ETA~5-10h)·hs_c0 3410/10044(34%,~4.5s/it,ETA~8h)·hs_c1 3211/10044(32%,~13s/it,ETA~15h)·hs_c2 1059/10044(11%,~20s/it,ETA~50h←慢)·hs_c3 406/10036(4%,~30-55s/it,ETA~70h←瓶颈Node1) ⑤**自#1745增量(~7min)**:piqa+47/c0+145/c1+50/c2+48/c3+34→全部推进无停滞 ⑥**chunk3再分配watcher仍活(PID1390395,etime~6min)**:监控piqa client(PID2097184)退出→将chunk3从Node1(8187)迁至Node0(8183)→预期2.8x加速;piqa当前32%→ETA~5-10h后触发 ⑦两报告已交付:异常报告v3.8(35.9KB,结论A旧二进制根因,覆盖6项全+phase2稳定)+speedup报告(17.3KB) ⑧训练.29健康:8×H100 95-100%util~75GB/卡 ⑨📦TASK=31.2KB/MEMORY=29.1KB·未完成指令:有(v6 eval运行中,待8集完成后更新报告终版)⇒WAITING:0。
> 2026-11-09 01:15 #1745: **v6 eval监控+🔑chunk3再分配watcher已启动·5s+5c全活·6/8done Avg6=53.38%不变·piqa 31% ETA~4h→完成后自动将chunk3从Node1(8187)迁至Node0(8183)·预期2.8x加速·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183-8187,health=ok) ③5 client全活(PID2097184/3765473/2097209/2097234/2669799) ④**精确进度(tqdm@01:12)**:piqa 1140/3676(31%,~5.5s/it,ETA~4h→~05:00)·hs_c0 3265/10044(33%,~5.2s/it,ETA~10h→~11:00)·hs_c1 3161/10044(31%,~14.8s/it,ETA~15h→~16:00)·hs_c2 1011/10044(10%,~10.7s/it,ETA~27h→~04:00 Nov10)·hs_c3 372/10036(4%,~14.5s/it,ETA~39h→~16:00 Nov10←瓶颈) ⑤**自#1744增量(~9min)**:piqa+40/c0+100/c1+35/c2+28/c3+33→全部推进无停滞 ⑥**🔑chunk3再分配watcher已启动(PID1390395)**:脚本`/tmp/baize_eval_v5/rebalance_chunk3_on_piqa_done.sh`监控piqa client(PID2097184)退出→kill chunk3 server(8187,Node1,cores96-111)+client(2669799)→在8183(Node0,cores32-47,piqa完成后空闲)上重启chunk3 client(全量shard3=2509docs)→预期14.5s/it→5.2s/it(2.8x)→ETA从39h→~14.5h;同时释放Node1带宽给chunk1/2加速 ⑦两报告已交付:异常报告v3.8(35.9KB,结论A旧二进制根因,覆盖6项全+phase2稳定)+speedup报告(17.3KB) ⑧训练.29健康:iter132000/700000(ckpt Nov8 23:06),8×H100 96-100%util~75GB/卡 ⑨research日报11-08已查:pretrain建议(eval读数口径+长上下文归因)已在报告v3.8覆盖,无新增指令 ⑩📦TASK=31.2KB/MEMORY=28.4KB（归档~4KB→daily-memories/2026-11-08.md）·未完成指令:有(v6 eval运行中,待8集完成后更新报告终版)⇒WAITING:0。
> 2026-11-09 01:03 #1744: **v6 eval监控·5s+5c全活·6/8done Avg6=53.38%不变·NUMA修复验证chunk3 40→17.4s/it(2.3x)但仍6.3x慢于chunk0·两报告已交付·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(port8183-8187) ③5 client全活(PID2097184/3765473/2097209/2097234/2669799) ④**精确进度(client log tqdm@01:02)**:piqa 1100/3676(30%,3.73s/it,ETA~2.7h→~03:40)·hs_c0 3165/10044(32%,2.74s/it,ETA~5.1h→~06:10)·hs_c1 3126/10044(31%,9.66s/it,ETA~18.5h→~19:30)·hs_c2 983/10044(10%,15.44s/it,ETA~38.8h→~15:50 Nov10)·hs_c3 339/10036(3%,17.38s/it,ETA~46.8h→~00:00 Nov11←瓶颈) ⑤**自#1743增量(8min)**:piqa+60/c0+136/c1+26/c2+25/c3+18→全部推进无停滞 ⑥**NUMA修复验证**:chunk3从#1743的40s/it→17.38s/it(2.3x改善✓),但仍6.3x慢于chunk0(2.74s/it);根因=server8187在Node1(cores64-79)GGUF模型内存跨NUMA访问,client affinity修复只解决客户端侧,server侧NUMA距离无法改 ⑦**再分配计划**:chunk0~06:10完成→释放server8184(Node0 cores16-31)→kill chunk3当前server/client→在8184上重启chunk3剩余部分(~9700docs)→预期~2.74s/it→ETA从47h→~7h ⑧两报告已交付:异常报告v3.8(35.9KB,结论A旧二进制根因,覆盖6项全+phase2稳定)+speedup报告(17.3KB) ⑨训练.29健康:iter132950/700000,loss2.058,0NaN/0skip,~7.3s/step,~985TFLOP/s ⑩📦TASK=31.9KB/MEMORY=30.0KB·未完成指令:有(v6 eval运行中,待8集完成后更新报告终版)⇒WAITING:0。
> 2026-11-09 00:55 #1743: **v6 eval监控+🔴NUMA拓扑纠正·5s+5c全活·6/8done Avg6=53.38%不变·发现chunk3=40s/it根因=客户端跨NUMA+HT争抢·已修复3个客户端affinity·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183-8187,health=ok) ③5 client全活 ④**🔑NUMA拓扑纠正(重大)**:lscpu实测Node0=0-55,112-167/Node1=56-111,168-223(HT:cpuN↔cpuN+112);此前#1740误判64-95为Node0→实为Node1;**server实际分布**:8183(32-47,N0)/8184(0-15,N0)/8185(64-79,N1)/8186(80-95,N1)/8187(96-111,N1) ⑤**chunk3=40s/it根因**:client在112-127=Node0-HT(HT兄弟=0-15=server8184)→跨NUMA访问Node1 server8187+与chunk0 server HT争抢;chunk2=15s/it根因:client在48-63=Node0→跨NUMA访问Node1 server8186 ⑥**修复(taskset -cap)**:chunk3→56-63(Node1物理,空闲)/chunk2→168-175(Node1-HT,空闲)/chunk1→168-175(Node1-HT);numa_balancing=1已开(内存页自动迁移) ⑦**修复后即时效果(3min)**:chunk3 302→321(+19,~9.5s/req,从40s/it改善)/chunk2 941→958(+17,~10.6s/req)/chunk1 3085→3100(+15,~12s/req);仍在迁移中预计后续轮次继续改善 ⑧当前进度:piqa 1040/3676(28%)/c0 3029(30%)/c1 3100(31%)/c2 958(10%)/c3 321(3%) ⑨训练.29健康8×H100 62-96%util~75GB/卡 **计划**:下次唤醒①验证NUMA修复效果(chunk3应<10s/it)②确认5s+5c存活③piqa/c0完成→合并7集④📦TASK=31.9KB/MEMORY=27.9KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。
> 2026-11-09 00:43 #1742: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%(results.json已验证)·异常报告v3.8已commit结论A(旧二进制根因)·chunk2=59h瓶颈·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183-8187,etime~4h) ③5 client全活(piqa PID2097184/hs_c0 PID3765473/hs_c1 PID2097209/hs_c2 PID2097234/hs_c3 PID2669799) ④**精确进度**:piqa 1028/3676(28%,6.89s/it,ETA~5h)·hs_c0 2935/10044(29%,2.51s/it,ETA~5h)·hs_c1 3060/10044(30%,6.50s/it,ETA~12.6h)·hs_c2 919/10044(9%,23.22s/it,ETA~59h←瓶颈)·hs_c3 290/10036(3%,11.45s/it,ETA~31h) ⑤**自#1741增量(4min)**:piqa+35/hs_c0+111/hs_c1+31/hs_c2+26/hs_c3+24→全部推进无停滞 ⑥**results.json验证**:arc_c=0.3038(n=1172)/arc_e=0.6553(n=2376)/boolq=0.5872(n=3270)/obqa=0.266(n=500)/sciq=0.842(n=1000)/wg=0.5485(n=1267),Avg6=53.38%,n_samples=9585(全量无limit) ⑦**异常报告v3.8已commit(d2ed8a1d5)**:结论A=旧llama.cpp二进制导致37.40%错误+全量vs限100口径差;v5/v6正确二进制Avg6=53.38%≈历史53.83%差-0.45pp;phase2稳定性+chunk0_missing误杀7.7h已说明 ⑧训练.29健康8×H100 100%util~75GB/卡~7.3s/step~1000TFLOP/s **计划**:下次唤醒①确认5s+5c存活②piqa/c0完成(~5h)→合并7集Avg7③c2/c3仍慢(59h/31h)待c0/c1完成后执行再分配(kill c2/c3重启Node0减带宽争抢)④📦TASK=31.9KB/MEMORY=27.0KB·未完成指令:有(v6 eval运行中,异常报告已交付待终版8集)⇒WAITING:0。

> 2026-11-09 00:39 #1741: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·逐集对照已完成(iter_112000全量vs iter_100000限100)·结论A铁证·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183-8187 health=ok,etime~14451s≈4h,8187=4405s≈1.2h重启) ③5 client全活(piqa PID2097184/hs_c0 PID3765473/hs_c1 PID2097209/hs_c2 PID2097234/hs_c3 PID2669799) ④**精确进度(client log tqdm)**:piqa 993/3676(27%,~15s/it波动4-30s,ETA~11h)·hs_c0 2824/10044(28%,~5s/it)·hs_c1 3029/10044(30%,~10s/it)·hs_c2 893/10044(9%,~15s/it←瓶颈)·hs_c3 266/10036(3%,~15s/it←最慢,Node1重启1.2h) ⑤**🔑逐集对照(本轮iter_112000全量vs历史iter_100000限100)**:arc_c=0.3038(n=1172)vs0.30(+0.4pp)·arc_e=0.6553(n=2376)vs0.57(+8.5pp)·boolq=0.5872(n=3270)vs0.67(-8.3pp)·obqa=0.2660(n=500)vs0.21(+5.6pp)·sciq=0.8420(n=1000)vs0.88(-3.8pp)·wg=0.5485(n=1267)vs0.60(-5.2pp)·**Avg6=53.38%vs53.83%差仅-0.45pp**(limit=100子集偏差,非真实下降) ⑥异常报告v3.8(35.9KB)已验证全覆盖6项(分集/样本数/后端/fewshot/hs进度/iter_100000对照)+训练loss+GGUF转换+phase2稳定性+根因总结,结论A ⑦训练.29健康8×H100 100%util~75GB/卡 **计划**:下次唤醒①确认5s+5c存活②piqa完成后合并7集Avg7③hs c2/c3完成后合并8集Avg8→更新报告终版④📦TASK=31.9KB/MEMORY=25.6KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。

> 2026-11-09 00:32 #1740: **v6 eval监控+chunk3 NUMA修复·5s+5c全活·6/8done Avg6=53.38%不变·正确active log读取(纠正#1739 stale log误读)·piqa ETA大幅改善~2.8h**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(port8183-8187,PID 2083715/3596298/2083721/2083722/2665866) ③5 client全活(PID 2097184/3765473/2097209/2097234/2669799) ④**🔑纠正stale log误读**:初始读client_hellaswag_chunk{0,1,2,3}.log(17:59-18:00旧文件)=错误低进度;正确active log=chunk0_numa_fix.log/chunk1_restart.log/chunk2_restart.log/chunk3_node1_restart.log/piqa_restart.log(mtime~00:29) ⑤**正确精确进度**:piqa 954/3676(26%,3.65s/it,ETA~2.8h←最先完成!)·chunk0 2753/10044(27.4%,6.15s/it,ETA~12h)·chunk1 2994/10044(29.8%,8.61s/it,ETA~17h)·chunk2 867/10044(8.6%,6.79s/it,ETA~17h)·chunk3 239/10036(2.4%,9.53s/it,ETA~26h) ⑥**chunk3 NUMA修复**:server8187在Node1(cores96-111)但client PID2669799 affinity=全CPU lastcpu=56(Node0)=跨NUMA;已taskset钉到Node1(cores96-127 mask=ffff0000000000000000000000000000),验证lastcpu=197✓ ⑦**server NUMA分布**:8183=N0(32-47)/8184=N0(0-15)/8185=N0(64-79)/8186=N0(80-95)/8187=N1(96-111) ⑧两报告已交付(异常v3.8 35.9KB结论A+speedup 17.3KB) ⑨训练.29健康8×H100 91-100%util~75GB/卡,latest ckpt iter_132000(23:06保存) ⑩**piqa ETA从#1739报告的~13h改善到~2.8h**:NUMA修复(#1737钉piqa到N0)已生效 **计划**:下次唤醒①确认5s+5c存活②piqa完成(~2.8h)→合并7集Avg7③chunk3 NUMA修复后s/it验证④📦TASK=31.9KB/MEMORY=24.2KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。

> 2026-11-09 00:21 #1739: **v6 eval监控轮·5s+5c全活·6/8done Avg6=53.38%不变·进度确认推进·两报告已交付结论A·训练健康**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183-8187 health=ok,etime~3.5h) ③5 client全活(piqa PID2097184/hs_c0 PID3765473/hs_c1 PID2097209/hs_c2 PID2097234/hs_c3 PID2669799) ④**精确进度(正确log文件grep)**:piqa 906/3676(24.6%,17.84s/it,ETA~13h)·hs_c0 2671/10044(26.6%,~4.5s/it,ETA~8.6h←NUMA修复后最快)·hs_c1 2954/10044(29.4%,~6.4s/it,ETA~12h)·hs_c2 829/10044(8.3%,~15s/it,ETA~38h←瓶颈)·hs_c3 199/10036(2%,~18.8s/it,ETA~49h) ⑤**自#1738增量**(9min):piqa+28/hs_c0+121/hs_c1+84/hs_c2+36/hs_c3+29→全部推进无停滞 ⑥**两运维令报告状态**:异常报告v3.8(35.9KB,commit d2ed8a1d5)已交付结论A(二因叠加:旧二进制+全量vs限100);speedup报告(17.3KB)已交付 ⑦**再分配计划不变**:c0/c1完成(~9h)→kill c2/c3重启于Node0释放核心(4→2 server竞争带宽) ⑧训练.29健康8×H100 95-100%util~75GB/卡 **计划**:下次唤醒①确认5s+5c存活②若c0完成→执行c2再分配③📦TASK=31.9KB/MEMORY=22.8KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。

> 2026-11-09 00:10 #1738: **v6 eval监控·NUMA修复验证生效·带宽争抢是新瓶颈·异常报告v3.8已更新·6/8done Avg6=53.38%不变·结论A铁证**·**动作**:①git fetch+status(synced,behind0) ②5 llama-server全活(8183-8187 health=ok,etime~3.5h) ③5 client全活 ④**NUMA修复验证**:taskset确认chunk2客户端mask=ffff000000000000(cores48-63 N0) lastcpu=60✓/piqa客户端mask=ffff0000(cores16-31 N0) lastcpu=25✓ ⑤**🔑 带宽争抢诊断**:5个server亲和mask解码→8183=cores32-47(N0)/8184=cores0-15(N0)/8185=cores64-79(N0)/8186=cores80-95(N0)/8187=cores96-111(N1);Node0上4个server×16线程=64线程争抢内存带宽→c0/c1快(~2.3s/it)但c2/piqa慢(~16-23s/it);NUMA修复消除跨节点访问但同节点带宽争抢仍限制吞吐 ⑥**精确进度**:piqa 878/3676(24%,22.8s/it,ETA~18h)·hs_c0 2550/10044(25%,2.3s/it,ETA~4.7h←最先完成)·hs_c1 2870/10044(29%,2.4s/it,ETA~4.8h)·hs_c2 793/10044(8%,16.3s/it,ETA~42h←瓶颈)·hs_c3 170/10036(1.7%,22.5s/it,ETA~62h) ⑦异常报告v3.8(35KB)已更新NUMA验证+带宽争抢分析+进度表,结论A不变 ⑧**再分配计划**:c0/c1完成(~5h)→kill c2/c3,在释放的Node0核心(cores0-15/64-79)重启(4→2个server竞争带宽,预计速率提升1.5-2x) ⑨训练.29健康8×H100 100%util~75GB/卡 **计划**:下次唤醒①确认5s+5c存活②若c0/c1已完成→执行c2/c3再分配到Node0③📦TASK=31.9KB/MEMORY=21.3KB·未完成指令:有(v6 eval运行中)⇒WAITING:0。

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