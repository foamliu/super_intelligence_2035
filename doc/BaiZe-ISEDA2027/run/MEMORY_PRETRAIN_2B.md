# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-08 18:30 #1705: **v5异常报告v2修订·3/7集v5已完成(boolq0.587/sciq0.842/openbookqa0.266)·二因结论推翻v1**·**动作**:① v5 eval(修复版二进制,全量,iter_112000)进度:boolq DONE(0.5872,n=3270)·sciq DONE(0.842,n=1000)·openbookqa DONE(0.266,n=500)·winogrande 91%(2295/2534,ETA~3min)·arc_challenge 56%(2643/4687,ETA~65min)·arc_easy 39%(3704/9501,ETA~174min)·piqa待独占重启·hellaswag待跑 ② **二因分解**:sciq二进制效应+52.6pp(主因)/全量vs限100仅3.8pp；boolq二进制效应-1.3pp(微)/全量vs限100+8.3pp(主因)；openbookqa二进制+8.2pp/全量vs限100-5.6pp(反向) ③ **v1报告「100%来自二进制」被v5 boolq数据推翻**→修订v2:二因叠加,因任务而异 ④ 报告v2已交付(22.7KB,12节,0脚本0外链),含三口径逐集对照表+二因分解表+⑥决定性实验补v5证据 ⑤ v4样本数:arc_challenge1172/arc_easy2376/boolq3270/openbookqa500/piqa919/sciq1000/winogrande1267 ⑥ 历史100k配置:全limit=100(effective=100),num_fewshot=0(zero-shot) ⑦ ⑦ S1健康(iter~128000/700k) **计划**:下次唤醒①查winogrande/arc_challenge是否完成→补入报告②arc_easy最慢(ETA~3h)③全部完成后算v5 Avg7④启动piqa_alone+hellaswag独占·📦TASK=31.2KB✓/MEMORY=~30.5KB✓(归档0)·未完成指令:有(v5 eval运行中,待出结果)⇒WAITING:0。

> 🔑 **v5三集结果(18:30)**: boolq=0.5872/sciq=0.842/openbookqa=0.266 → **二因确认**:sciq二进制主因(+52.6pp),boolq全量vs限100主因(+8.3pp),v1「100%二进制」结论被推翻→报告v2已修订为「二因叠加,因任务而异」。

> 📦 §#1704（11-08 18:14, v5 eval优化轮·杀piqa瓶颈·boolq首批结果0.5872确认二因）→ daily-memories/2026-11-08.md「#1704」节；**结论**：v5 boolq=0.5872证明binary对boolq几乎无影响,full-vs-limit100是主因,异常报告需修订为二因。需要时再读。

> 📦 §#1703（11-08 18:12, v5 eval优化轮·杀4 hellaswag shard释放带宽·7非HS任务加速·运维令6项已交付）→ daily-memories/2026-11-08.md「#1703」节；**结论**：v5 eval杀掉hellaswag 4 shard释放带宽,7非HS任务推进中,运维令6项异常报告已交付。需要时再读。

> 📦 §#1702（11-08 17:52, v5 eval监控轮·全11路健康·0/11完成·openbookqa最近ETA~30min）→ daily-memories/2026-11-08.md「#1702」节；**结论**：v5 eval 11/11健康0/11完成,运维令6项异常报告+speedup报告均已交付。需要时再读。


> 📦 §#1701（11-08 17:42, v5 eval监控轮·全11路健康·0/11完成·运维令6项报告均已交付）→ daily-memories/2026-11-08.md「#1701」节；**结论**：v5 eval 11/11健康0/11完成,运维令6项异常报告+speedup报告均已交付。需要时再读。
> 📦 §#1700（11-08 17:33, v5 eval监控轮·全11路健康·0/11完成·小任务即将出首批结果）→ daily-memories/2026-11-08.md「#1700」节；**结论**：v5 eval 11/11健康0/11完成,带宽争抢piqa/hellaswag极慢,异常报告12节确认完整。需要时再读。

> 📦 §#1699（11-08 17:41, v5 eval监控轮·全11路运行·异常报告验证完整）→ daily-memories/2026-11-08.md「#1699」节；**结论**：v5 eval 11/11健康0/11完成,异常报告12节确认覆盖6项①-⑥+结论A。需要时再读。

> 📦 §#1698（11-08 17:24, v5 eval监控轮·健康但慢·杀残留port8092）→ daily-memories/2026-11-08.md「#1698」节；**结论**：v5 eval 11/11健康,杀掉旧port8092决定性实验遗留server,异常报告12节确认完整。需要时再读。
> 📦 §#1697（11-08 17:12, v5修复版全量eval启动·11路并行·修复版二进制MD5=f95ac952）→ daily-memories/2026-11-08.md「#1697」节；**结论**：杀掉全部v4旧二进制eval，创建baize_eval_v5_correct.sh(code/llama.cpp修复版+11路任务并行+HF离线)，11/11 server+client运行中。需要时再读。
> 📦 §#1696（11-08 16:56, Avg7=37.40%异常根因定位=llama-server旧二进制回归·决定性实验sciq旧0.44/新0.88·报告15KB·结论A口径差异）→ daily-memories/2026-11-08.md「#1696」节；**结论**：根因=v4用旧二进制(tools/llama.cpp,缺nemotron-h logits修复)，同GGUF旧sciq=0.44/新sciq=0.88，loss平滑无退化，结论A非真实下降，报告report_pretrain_eval_avg7_anomaly_zh.html已交付。需要时再读。
> 📦 §#1694（11-08 15:25, phase2误杀chunk0_missing(70%丢失)→修复+恢复+切v4 watcher·S1 iter~128000/700k）→ daily-memories/2026-11-08.md「#1694」节；**结论**：phase2误杀chunk0_missing导致docs 0-1757覆盖缺口→#1695创建fill_gap脚本修复。需要时再读。
> 📦 §#1692（11-08 14:55, chunk0b_b崩溃修复·重启llama-server 8083+创建split1/split2·phase2 get_port()bug待修·S1 iter~128200/700k）→ daily-memories/2026-11-08.md「#1692」节；**结论**：phase2 bug杀死chunk0b_b eval client未启动替代,手动创建split1/split2修复,phase2 get_port()bug待下次唤醒修→#1693已修。需要时再读。
> 📦 §#1691（11-08 14:38, v4 eval+phase2动态再分配激活·kill v3改phase2动态瓶颈优先·chunk0b_b27.6%瓶颈·S1 iter~128000/700k）→ daily-memories/2026-11-08.md「#1691」节；**结论**：phase2激活但首次再分配因get_port()bug崩溃,杀死chunk0b_b未启动替代→#1692修复。需要时再读。
> 📦 §#1690（11-08 14:23, v4 eval监控轮·7chunk全健康·chunk0_missing63%首trigger ETA~18:27·chunk0b_b26.5%瓶颈·S1 iter127910/700k）→ daily-memories/2026-11-08.md「#1690」节；**结论**：7chunk全健康,chunk0_missing63%/chunk0b_b26.5%瓶颈,v3 4trigger全pending,phase2等待DONE_FILE。需要时再读。
> 📦 §#1688（11-08 14:08, v4 eval监控轮+phase2再分配脚本创建启动·7chunk全健康·chunk0_missing60.6%首trigger ETA~18:05·S1 iter~127750/700k GPU全100%）→ daily-memories/2026-11-08.md「#1688」节；**结论**：phase2脚本(PID597587)已部署等待v3 DONE_FILE,7chunk全健康,chunk0_missing60.6%/chunk0b_b25.5%瓶颈,首trigger ETA~18:05。需要时再读。

> 📦 §#1687（11-08 13:55, v4 eval监控轮·7chunk全健康·chunk0_missing58.0%首trigger ETA~19:42·S1 iter127700/700k GPU全100%）→ daily-memories/2026-11-08.md「#1687」节；**结论**：7chunk全健康推进,chunk0_missing58.0%/chunk0b_a68.7%,7/8非hellaswag集已完成,首trigger ETA~19:42。需要时再读。
> 📦 §#1686（11-08 13:48, v4 eval监控轮·7chunk全健康·chunk0_missing57.0%首trigger ETA~18:47·S1 iter~127640/700k GPU45-100%）→ daily-memories/2026-11-08.md「#1686」节；**结论**：7chunk全健康推进,chunk0_missing57.0%/chunk0b_a68.2%,7/8非hellaswag集已完成,首trigger ETA~18:47。需要时再读。
> 📦 §#1685（11-08 13:43, v4 eval监控轮·7chunk全健康·chunk0_missing56.4%首trigger ETA~17:44·S1 iter127610/700k GPU37-100%）→ daily-memories/2026-11-08.md「#1685」节；**结论**：7chunk全健康推进,chunk0_missing56.4%/chunk0b_a67.9%,7/8非hellaswag集已完成,首trigger ETA~17:44。需要时再读。
> 📦 §#1684（11-08 13:36, v4 eval监控轮·7chunk全健康·chunk0_missing55.4%首trigger ETA~17:10·S1 iter~127560/700k GPU74-100%）→ daily-memories/2026-11-08.md「#1684」节；**结论**：7chunk全健康推进,chunk0_missing55.4%/chunk0b_a67.5%,7/8非hellaswag集已完成,首trigger ETA~17:10。需要时再读。
> 📦 §#1683（11-08 13:31, v4 eval监控轮·7chunk全健康·chunk0_missing54.3%首trigger ETA~18:51·S1 iter~127500/700k GPU88-100%）→ daily-memories/2026-11-08.md「#1683」节；**结论**：7chunk全健康推进,chunk0_missing54.3%/chunk0b_a67.0%,7/8非hellaswag集已完成,首trigger ETA~18:51。需要时再读。
> 📦 §#1682（11-08 13:22, v4 eval监控轮·7chunk全健康·chunk0_missing53.0%首trigger ETA~18:12·S1 iter~127500/700k GPU95-100%）→ daily-memories/2026-11-08.md「#1682」节；**结论**：7chunk全健康推进,chunk0_missing53.0%/chunk0b_a66.4%,7/8非hellaswag集已完成,首trigger ETA~18:12。需要时再读。
> 📦 §#1681（11-08 13:17, v4 eval监控轮·7chunk全健康推进无SIGSTOP·chunk0_missing52.1%@~16.7/min→ETA~17:05首trigger·chunk0b_a66.0%·S1 iter~127420/700k GPU全100%）→ daily-memories/2026-11-08.md「#1681」节；**结论**：7chunk全健康推进,chunk0_missing52.1%/chunk0b_a66.0%,7/8非hellaswag集已完成,首trigger ETA~17:05。需要时再读。
> 📦 §#1680（11-08 13:12, v4 eval监控轮·7chunk全健康推进无SIGSTOP·chunk0_missing51.1%加速至~19.75/min→ETA~17:18首trigger·chunk0b_a65.5%·S1 iter127380/700k loss2.055）→ daily-memories/2026-11-08.md「#1680」节；**结论**：7chunk全健康推进,chunk0_missing51.1%/chunk0b_a65.5%,7/8非hellaswag集已完成,首trigger ETA~17:18。需要时再读。
> 📦 §#1679（11-08 13:03, v4 eval监控轮·7chunk全健康推进无SIGSTOP·chunk0_missing49.5%·S1 iter127327/700k loss1.980）→ daily-memories/2026-11-08.md「#1679」节；**结论**：7chunk全健康推进,chunk0_missing49.5%/chunk0b_a64.9%,7/8非hellaswag集已完成。需要时再读。
> 📦 §#1678（11-08 12:56, v4 eval监控轮·7chunk全健康推进无SIGSTOP·chunk0_missing48.2%·S1 iter127260/700k loss2.048）→ daily-memories/2026-11-08.md「#1678」节；**结论**：7chunk全健康推进,chunk0_missing48.2%/chunk0b_a64.3%,7/8非hellaswag集已完成。需要时再读。
> 📦 §#1677（11-08 12:49, v4 eval监控轮·7chunk全健康推进·chunk0_missing47%·S1 iter127210/700k loss2.043）→ daily-memories/2026-11-08.md「#1677」节；**结论**：7chunk全健康推进,chunk0_missing47.2%/chunk0b_a64.0%,7/8非hellaswag集已完成。需要时再读。
> 📦 §#1676（11-08 12:43, v4 eval监控轮·SIGSTOP恢复后7chunk全健康推进·S1 iter127170/700k loss2.039）→ daily-memories/2026-11-08.md「#1676」节；**结论**：12:24→12:33全部7 eval client被SIGSTOP恆起已恢复+guard部署，12:40确认7chunk全健康推进。需要时再读。
> 📦 §#1675（11-08 12:35, 🔴CRITICAL: 7 eval client被SIGSTOP挂起·已恢复+建guard）→ daily-memories/2026-11-08.md「#1675」节；**结论**：12:24→12:33全部7 eval client被SIGSTOP(T态,stall~9min),kill -CONT恢复,guard_sigcont.sh看门狗(PID3749711)已部署。#1676确认恢复后7chunk全健康推进,guard无复发。需要时再读。
> 📦 §#1674（11-08 12:22, v4 eval监控轮·7chunk全健康·hellaswag 42.7%·4 trigger全pending·首trigger=chunk0_missing ETA~5.1h~17:30）→ daily-memories/2026-11-08.md「#1674」节；**结论**：chunk0_missing加速至18.3/min(ETA~5.1h~17:30),chunk0b_a加速至4.3/min(ETA~7.3h),整体ETA~17h~05:00Nov9。#1675发现12:24后全部7 eval client被SIGSTOP挂起(T态,stall~9min),已SIGCONT恢复+建guard看门狗。需要时再读。
> 📦 §#1673（11-08 12:05, v4 eval监控轮·7chunk全健康·hellaswag 40.9%·4 trigger全pending·首trigger=chunk0_missing ETA~6.8h~19:00）→ daily-memories/2026-11-08.md「#1673」节；**结论**：chunk0_missing加速至14.3/min(ETA~6.8h~19:00),chunk0b_a加速至2.9/min(ETA~11.1h),整体ETA~17.5h~05:30Nov9。需要时再读。
> 📦 §#1672（11-08 12:00, v4 eval监控轮·7chunk全健康·v3脚本核查+4 trigger确认·ETA~17.5h~05:30Nov9）→ daily-memories/2026-11-08.md「#1672」节；**结论**：4 trigger全pending,首trigger=chunk0_missing ETA~8h~20:00,速率修正chunk0b_a 2.0/min。#1673确认hellaswag 40.9%,chunk0_missing加速至14.3/min(ETA~6.8h~19:00),chunk0b_a加速至2.9/min(ETA~11.1h),整体ETA不变~17.5h。需要时再读。
> 📦 §#1670（11-08 11:42, v4 eval监控轮·7chunk全健康·速率稳定(16min窗口)·chunk0b_a 59.6%→ETA~10h）→ daily-memories/2026-11-08.md「#1670」节；**结论**：7chunk全RUNNING,chunk0b_a 59.6%(ETA~10h trigger~21:40),post-split整体~16.8h→~04:25 Nov9。#1671确认7/8 DONE分数已收,chunk0_missing为实际首trigger(ETA~6.6h~18:24)。需要时再读。
> 📦 §#1669（11-08 11:35, v4 eval监控轮·7chunk全健康·chunk0b_a 59.1%→ETA~5.1h首trigger~16:40·瓶颈chunk0b_b ETA~20.8h待split）→ daily-memories/2026-11-08.md「#1669」节；**结论**：7chunk全RUNNING,chunk0b_a 59.1%(ETA~5.1h→trigger~16:40)。#1670确认速率稳定3.4/min(ETA修正~10h,前估5.1h偏乐观),post-split整体~16.8h→~04:25 Nov9。需要时再读。
> 📦 §#1667（11-08 11:22, v4 eval监控轮·7chunk全健康·chunk0b_a 56.8%加速→ETA~2.1h·瓶颈chunk0b_b待split）→ daily-memories/2026-11-08.md「#1667」节；**结论**：7chunk全RUNNING,chunk0b_a 56.8%(ETA~2.1h→trigger~13:25)。#1668确认chunk0b_a 58.6%(ETA~3.9h→trigger~15:20),chunk1b_b为新worst bottleneck(ETA~28.4h,待chunk0_missing完成split)。需要时再读。
> 📦 §#1666（11-08 11:13, v4 eval监控轮·7chunk全健康·chunk0a_half1=stale死进程·chunk0b_a 54.6% ETA~5.8h）→ daily-memories/2026-11-08.md「#1666」节；**结论**：7chunk全RUNNING,chunk0a_half1确认为stale死进程(端口映射已核实),chunk0b_a 54.6%。需要时再读。
> 📦 §#1665（11-08 11:02, v4 eval监控轮·7chunk全健康·chunk0b_a 51.7%逼近trigger）→ daily-memories/2026-11-08.md「#1665」节；**结论**：7chunk全RUNNING无异常,chunk0b_a 51.7%→ETA~13:50首触发,编排链5脚本全活。#1666确认chunk0b_a 54.6%(ETA~5.8h)+chunk0a_half1=stale死进程。需要时再读。
> 📦 §#1664（11-08 10:55, v4 eval监控轮·7chunk全健康·首个trigger ETA~13:45·无异常）→ daily-memories/2026-11-08.md「#1664」节；**结论**：7chunk全RUNNING无异常,chunk0b_a 50%→ETA~13:45首触发,编排链5脚本全活。#1665确认chunk0b_a 51.7%逼近trigger。需要时再读。
> 📦 §#1663（11-08 10:48, v3端口冲突修复+phase3/4部署轮·ETA ~13h→~9.5h）→ daily-memories/2026-11-08.md「#1663」节；**结论**：修复v3端口冲突(8084→8085/8082)+部署phase3/4进一步优化,总ETA~9.5h(完成~20:15)。#1664确认全健康无异常。需要时再读。
> 📦 §#1662（11-08 10:31, phase2 redistribute部署轮·复用空闲server·ETA ~12h→~7h）→ daily-memories/2026-11-08.md「#1662」节；**结论**：部署phase2(chunk0b_b完成后3-way拆分chunk1a_h1),总ETA~7h。#1663已修复v3端口冲突并部署phase3/4进一步优化。需要时再读。
> 📦 §#1661（11-08 10:14, v3 rate-balanced redistribute部署轮·ETA 24h→~9.5h·替换v1+v2）→ daily-memories/2026-11-08.md「#1661」节；**结论**：部署v3(速率均衡拆分+提前触发1b_a),总ETA 24h→~9.5h。#1662已部署phase2进一步优化。需要时再读。
> 📦 §#1660（11-08 09:55, v4 eval监控轮·7chunk全健康·瓶颈ETA~18h·v1待触发）→ daily-memories/2026-11-08.md「#1660」节；**结论**：7chunk全RUNNING,chunk0b_b瓶颈,v1+v2等待触发。#1661已用v3替换v1+v2。需要时再读。
> 📦 §#1659（11-08 09:48, v4 eval监控轮·7chunk全健康·瓶颈ETA~15h·无空闲物理核）→ daily-memories/2026-11-08.md「#1659」节；**结论**：7chunk全RUNNING,chunk0b_b瓶颈ETA~18h,v1待chunk0b_a完成(~3h)触发拆分,无空闲物理核增server。需要时再读。
> 📦 §#1658（11-08 09:40, chunk1b_a再分配部署轮·覆盖v1盲区·ETA 20h→15h）→ daily-memories/2026-11-08.md「#1658」节；**结论**：部署auto_redistribute_v2(PID2752593)覆盖chunk1b_a,final_watcher_v3更新。需要时再读。
> 📦 §#1657（11-08 09:24, eval client CPU亲和性优化轮·chunk0b_b 24→14.5s/it 1.66x）→ daily-memories/2026-11-08.md「#1657」节；**结论**：7 client全移HT核112-223,bottleneck ETA 31h→19h;chunk1b_a ETA~20h(未覆盖,#1658已补)。需要时再读。
> 📦 §#1656（11-08 09:12, auto-redistribute部署轮·瓶颈ETA 21.6h→~11h）→ daily-memories/2026-11-08.md「#1656」节；**结论**：诊断7x速率差异根因(prompt长度2x+NUMA带宽3x),部署auto_redistribute.sh(PID4094387)监控chunk0b_a→拆分chunk0b_b+chunk0_missing→拆分chunk1b_b,配套final_watcher_v2+merge脚本。需要时再读。
> 2026-11-08 09:12 #1656: **auto-redistribute部署轮·瓶颈ETA 21.6h→~11h**·**本轮动作**:①git pull同步 ②**深度诊断7-chunk速率7x差异**:NUMA topology(node0=0-55,node1=56-111,HT=112-223),7server全~650-700%CPU/~75-85tok/s,但s/it=2.25-19.3→根因=prompt长度(快chunk~50tok vs 慢~100tok=2x)+node0上3server共享内存带宽(3x)=7x总差异;NUMA内存布局已验证正确(各server内存本地到CPU节点) ③**部署auto_redistribute.sh(PID4094387)**:监控chunk0b_a完成(ETA~2.7h)→kill chunk0b_b+拆分剩余到8082(split1)+8085(split2);监控chunk0_missing完成(ETA~5.8h)→kill chunk1b_b+拆分到8084(split1)+8087(split2);配套final_watcher_v2.sh处理split目录;merge脚本glob("hellaswag_chunk*")自动收集split→加权平均合并安全 ④S1健康(iter~125600/700000,8GPU59-100%,~75GB/卡,.29) ⑤进度@09:00:7/8完成,chunk0b_b=222/5024@16.2s/it(4.4%,bottleneck,ETA~21.6h)|chunk1b_b=1397/5020@19.3s/it(28%,ETA~19.4h)|chunk0b_a=763/5024@2.25s/it(15%,ETA~2.7h)|chunk0_missing=1313/10040@2.4s/it(13%,ETA~5.8h)|chunk1a_h1=1263/5024@11.35s/it(25%)|chunk1a_h2=1313/5020@9.8s/it(26%)|chunk1b_a=1461/5024@12.1s/it(29%) ⑥7集分数同#1655(Avg7=0.3729)·📦TASK=27.8KB✓/MEMORY=14.9KB✓(归档0KB)·未完成指令:有(v4 eval 7chunk运行中+auto_redistribute已部署→下次唤醒检查再分配是否触发+进度→完成后收8集分数+耗时对照+报告最终更新)⇒WAITING:0。
> 📦 §#1655（11-08 08:52, core rebalance优化轮·8082(24→16核)+8085(8→16核)）→ daily-memories/2026-11-08.md「#1655」节；**结论**：taskset 8082 32-47+8085 48-63各16核,全7server覆盖0-111。需要时再读。
> 📦 §#1654（11-08 08:39, CPU亲咆性全量重均衡轮·7server全移物理核+eval client钉HT核）→ daily-memories/2026-11-08.md「#1654」节；**结论**：3/7 server跑HT核→3-4x慢+client抢核→rebalance全server钉物理核(0-111)+client钉HT核(112-223),bottleneck ETA 32h→20h。需要时再读。
> 📦 §#1653（11-08 08:22, 关键修复轮·merge脚本IndentationError致命bug修复）→ daily-memories/2026-11-08.md「#1653」节；**结论**：merge_metric_chunks函数return语句误放模块级→IndentationError→已修好,AST+dry-run验证PASS。需要时再读。
> 📦 §#1652（11-08 08:10, 监控轮·7chunk全健康·速率极波动·报告已更新）→ daily-memories/2026-11-08.md「#1652」节；**结论**：7eval客户端+7server全活,瓶颈chunk0b_b@20s/it,ETA~Nov9 00-06h,报告已更新。**#1653发现并修复merge脚本IndentationError致命bug**。需要时再读。
> 📦 §#1651（11-08 08:02, chunk0b瓶颈分裂轮·34h→14.5h+修复broken watcher）→ daily-memories/2026-11-08.md「#1651」节；**结论**：发现8083 DOWN+chunk0a死+watcher broken→修复watcher(检查7chunk+7server)+分裂chunk0b为chunk0b_a/b+第7台server 8082,ETA 34h→14.5h。**#1652确认全健康+速率波动+chunk0b_b为新瓶颈**。需要时再读。
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