# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0

> 2026-11-07 23:07 #1607: 运维令11-07 15:2x监控轮·①v4 eval(112k)进度核查@23:07:✅4/8完成=boolq(acc0.60,n3270)+sciq(acc0.316/norm0.264,n1000)+winogrande(acc0.4964,n1267)+arc_easy(acc0.2618/norm0.2740,n2376,刚完成@22:59);运行中=arc_challenge 2%(86/4687@~4.15s/it,ETA~5h)on N0/8080→openbookqa→hs_chunk1b(chained);piqa_part1 15%(272/1838@~9.5s/it,ETA~4h)on N1/8081→hs_chunk0b;piqa_part2 11%(202/1838@~7.4s/it,ETA~3.3h)on N2/8082→hs_chunk1a;hs_chunk0a 10%(1036/10040@~3.4s/it avg,ETA~5h)on N3/8083·②orchestration PID882130 alive,4 NUMA-pinned servers(8080-8083)全alive(taskset cores 0-55/56-111/112-167/168-223)·③ETA投影:bottleneck=N0 chain(arc_challenge~5h+openbookqa~2h+hs_chunk1b~5h=~12h)→done~11:00 Nov8(总~17h from 18:25 start,在1-2天目标内)·④partial merge已运行(arc_easy加入results.json→4/8),报告regenerated 13075B(4/8 partial,显示"进行中 已运行4.7h")·⑤piqa split merge逻辑已确认:orchestrate_fixed.sh L67-82在piqa+piqa_part2双results.json到位时自动加权平均→merge脚本最终pick up·⑥S1健康(.29 GPU 76-100%/75GB/56-64℃/675-692W,8卡全满载)·load~58/224,mem~756/2015GB·📦TASK=27.8KB✓/MEMORY=25.5KB✓(归档#1594-#1601→daily-memories,释放~7KB)·未完成指令:有(v4 eval运行中→完成后填耗时+8集分数+一致性校验+报告最终更新)⇒WAITING:0。

> 2026-11-07 22:59 #1606: 运维令11-07 15:2x监控轮·①v4 eval(112k)进度核查@22:59:✅3/8完成=boolq(acc0.60,n3270)+sciq(acc0.316/norm0.264,n1000)+winogrande(acc0.4964,n1267);arc_easy 98%(9289/9501@~1.85it/s,ETA~2min→即将4/8)→arc_challenge→openbookqa→hs_chunk1b(chained N0/8080);piqa_part2 9%(164/1838@~8s/it,ETA~3.8h)on N2/8082→hs_chunk1a;hs_chunk0a 9%(885/10040@~5s/it,ETA~14h)on N3/8083·②orchestration PID882130 alive(2123s),4 servers全alive(8080-8083 health=ok)·③ETA投影:hs各shard~14h(staggered),N2 hs_chunk1a最晚~16:00 Nov8→总~22h from 18:25 start(在1-2天目标内)·④报告regenerated 13075B(3/8 partial,显示"进行中 已运行4.6h")·⑤一致性校验素材已就位:gguf_iter_100000_fixed_8set(limit100,8集)+PR#31703 logitsΔmax=0.006+PRECISION_10K表(已编入gen脚本);HF全量112k基线不存在(22天run已kill让位v4),将以fixed GGUF精度验证+thread-scaling probe分数一致性(#1570)替代·⑥S1健康(.29 GPU全满/75GB)·📦TASK=27.8KB✓/MEMORY=30.5KB✓(归档#1556-#1557指针→daily-memories已存,释放~0.5KB)·未完成指令:有(v4 eval运行中→完成后填耗时+8集分数+一致性校验+报告最终更新)⇒WAITING:0。


> 2026-11-07 22:54 #1605: 运维令11-07 15:2x监控轮·①v4 eval(112k)进度核查@22:54:✅3/8完成=boolq(acc0.60,n3270)+sciq(acc0.316/norm0.264,n1000)+winogrande(acc0.4964,n1267);arc_easy 94%(8973/9501@~1.4it/s,ETA~5min)→arc_challenge→openbookqa→hs_chunk1b(chained N0/8080);piqa_p1 ~17%(~310/1838 est@~10s/it,ETA~4h)on N1/8081→hs_chunk0b;piqa_p2 8%(149/1838@~9s/it,ETA~4.2h)on N2/8082→hs_chunk1a;hs_chunk0a 8%(831/10040@~3.4s/it avg,ETA~9h)on N3/8083·②orchestration PID882130 alive(1712s),4 servers全alive(8080-8083)·③ETA投影:bottleneck=N0(arc~2h+hs_chunk1b~8h=~10h)+N2(piqa~4h+hs_chunk1a~8h=~12h)→done~11:00 Nov8(总~17h from 18:25 start,在1-2天目标内)·④报告regenerated 13075B(3/8 partial,显示"进行中 已运行4.5h")·⑤S1健康(.29 GPU 54-100%/75GB/54-63℃/553-610W)·load55/224,mem754/2015GB·📦TASK=27.8KB✓/MEMORY=30.2KB✓·未完成指令:有(v4 eval运行中→完成后填耗时+分数+一致性校验+报告最终更新)⇒WAITING:0。

> 2026-11-07 22:47 #1604: 运维令11-07 15:2x监控轮·①v4 eval(112k)进度核查@22:47:✅3/8完成=boolq(acc0.60,n3270)+sciq(acc0.316/norm0.264,n1000)+winogrande(acc0.4964,n1267);arc_easy 87%(8270/9501@~1.3it/s,ETA~15min)→arc_challenge→openbookqa→hs_chunk1b(chained N0/8080);piqa_p1 8%(146/1838@~9.5s/it avg,ETA~4.5h)on N1/8081→hs_chunk0b;piqa_p2 6%(113/1838@~12.4s/it avg,ETA~6h)on N2/8082→hs_chunk1a;hs_chunk0a 7%(707/10040@~3.4s/it avg,ETA~8.8h)on N3/8083·②orchestration PID882130 alive(1390s),4 servers全alive(8080-8083 health=ok)·③ETA投影:bottleneck=piqa_p2(~6h)+hs_chunk1a(~9h)=~15h from 18:25 start→done~09:30 Nov8(在1-2天目标内)·④报告regenerated 13075B(3/8 partial,显示"进行中 已运行4.4h")·⑤S1健康(.29 GPU 8/8 100%/75GB/54-61℃)·load59.5/224,mem756/2015GB·📦TASK=27.8KB✓/MEMORY=29.3KB✓·未完成指令:有(v4 eval运行中→完成后填耗时+分数+一致性校验+报告最终更新)⇒WAITING:0。

> 2026-11-07 22:41 #1603: 运维令11-07 15:2x监控+报告修复轮·①验证orchestration PID882130存活(581s)+4 NUMA-pinned servers(8080-8083)全alive·②进度@22:31:✅3/8完成=boolq(acc0.60,n3270)+sciq(acc0.316/norm0.264,n1000)+winogrande(acc0.4964,n1267);运行中=arc_easy 73%(6978/9501@~1.1it/s,ETA~38min)→arc_challenge→openbookqa→hs_chunk1b;piqa_p1 3%(66/1838@~9s/it,ETA~4.4h)on N1;piqa_p2 2%(38/1838@~9s/it,ETA~4.5h)on N2;hs_chunk0a 5%(475/10040@~3.5s/it,ETA~9.3h)on N3·③ETA投影:bottleneck=hs_chunk0b/1a(待piqa完成后~03:00启动,各~9.8h→完成~12:50次日)=总~14h from 18:25 start→done~08:30次日·④**修复gen_eval_speedup_report.py bug**:eval_done原只检查results.json存在(中间merge仅3/8任务→误报"done")→改为检查len(full)>=8;wall_sec_live改为not eval_done时计算;加partial results显示(已完成N/8集表格)·⑤更新报告文本"8服务器"→"4 NUMA-pinned服务器"(6处)·⑥报告regenerated:13075B/0script/0外链/显示"进行中 已运行4.2h"+3/8 partial scores·⑦S1健康(.29 GPU 76-100%/75GB/57-63℃,ckpt iter_0120000)·load58/224,mem752/2015GB·📦TASK=27.8KB✓/MEMORY=28.0KB✓·未完成指令:有(v4 eval运行中→完成后填耗时+分数+一致性校验+报告最终更新)⇒WAITING:0。

> 2026-11-07 22:25 #1602: 运维令11-07 15:2x执行轮·**piqa 2-way split + 固定orchestration修复(N2空闲→瓶颈消除)**·①发现4way orchestration脚本crash(line104读不存在arc_challenge.log+set -e)+N2/8082完全空闲(piqa_part2因piqa k=1838索引越界FAIL)→②kill全量piqa(仅2%进度,极小损失)→③piqa 2-way split:part1[0,919)on N1/8081+part2[919,1838)on N2/8082→各1838 req,ETA~3-5h(原全量~9.6h)→④写baize_eval_v4_orchestrate_fixed.sh(set -uo pipefail无-e,修复crash)→⑤orchestration PID882130自动链:N0=arc_easy(65%)→arc_challenge→openbookqa→hs_chunk1b(7531-10042);N1=piqa_p1→hs_chunk0b(2510-5021);N2=piqa_p2→hs_chunk1a(5021-7531);N3=hs_chunk0a(3%running)→⑥清理stale hellaswag日志/shard dirs→⑦新ETA:bottleneck=piqa_split(~3-5h)+hs_chunk(~8-11h)=~13-16h(vs原~18-21h,省~5h)·⑧3/8完成=boolq0.60+sciq0.316+winogrande0.4964·S1健康(.29 GPU100%/75GB)·load58/224,mem752/2015GB·📦TASK=27.8KB✓/MEMORY=27.6KB✓·未完成指令:有(v4 eval运行中→完成后填耗时+分数+一致性校验+更新报告)⇒WAITING:0。

> 📦 §#1594-#1601（11-07 20:05-22:05, 8条v4 eval监控/修复轮心跳）→ daily-memories/2026-11-07.md；**结论**：v4 eval从sciq精度异常诊断→4-NUMA并行优化→piqa 2-way split+固定orchestration,3/8完成,ETA从22h→~13-17h. 需要时再读。


> 2026-11-07 19:33 #1592: 运维令11-07 15:2x监控轮·v4全量GGUF eval运行中(~1h08m,8 llama-server全alive)·**确认hellaswag分片正确**(chunk0=0-2510/chunk1=2511-5021/chunk2=5022-7532/chunk3=7533-10041,进度条10044=2511docs×4choices)·精确进度@19:30:boolq 84%(5503/6540,1.50it/s,ETA~12min→winogrande)arc_challenge 58%(2711/4687,2.20s/it,ETA~1h12m→openbookqa)sciq 30%(1214/4000,2.43it/s,ETA~19min→piqa)arc_easy 7%(630/9501,1.44s/it,ETA~3.5h)hellaswag chunk0=147/10044(4.75s/it,~13h)chunk1=199/10044(2.77s/it,~7.7h)chunk2=30/10044(17.74s/it,~49h⚠️)chunk3=33/10036(12.31s/it,~34h⚠️)·**关键判断**:chunk2/3 ETA 34-49h为悲观估值(假设当前争用速度持续);随非hellaswag任务完成(servers 8084-8087逐个空闲)带宽压力下降→hellaswag应从12-17s/it加速至~4-5s/it;投影总耗时=arc_easy~3.5h(最后非HS)+hellaswag全带宽~14h≈~17h≈0.7天(在运维1-2天目标内)·launcher脚本已死(NFS stale handle杀wait循环)但setsid worker存活,无需干预·报告重生成10717B/0script/0外链/进行中正确显示·S1健康(GPU 82-100%/~75GB/49-60℃,ckpt iter_112000)·CPU load116/224,mem803/2015GB(1087GB可用)·ops/inbox无新令(RUN_ID245已执行)·📦TASK=27.8KB✓/MEMORY=21.6KB✓·未完成指令:有(v4 eval运行中→完成后填实测耗时+分数+一致性校验)⇒WAITING:0。


> 2026-11-07 19:24 #1591: 运维令11-07 15:2x执行轮·**v4 eval 3个崩溃/挂起问题诊断+修复+重启**·①logit_bias崩溃(sciq/piqa RuntimeError got=3982 want=85)→修复:bias 100→1000+降级处理(不崩溃返回logprob=-100)·②hellaswag chunk0/1挂起(37min无进度,State=S 150线程,HTTP请求永久挂起)→修复:timeout 600→120s+(10,120)连接超时+kill重启·③arc_easy也挂起(14min无进度,旧脚本timeout=600)→kill+修复版重启·修复后全部8任务正常运行:boolq 76%(4992/6540 ETA~20min)arc_challenge 53%(2461/4687 ETA~59min)sciq 14%(542/4000@1.46it/s **无崩溃✓**)hellaswag chunk0=71/10044(5.16s/it)chunk1=86/10044(1.97s/it)chunk2=14/10044(21.2s/it⚠️)chunk3=16/10036(15.8s/it⚠️)arc_easy=132/9501(2.33it/s重启)·chunk2/3仍慢(内存带宽争用)但不再挂起;非hellaswag~1-2h完成后servers 8084-8087释放→hellaswag应加速·报告更新10715B/0script/0外链/新增「三c v4问题诊断与修复」节·S1健康(GPU全100%/75GB/55-64℃,ckpt iter_0118000)·CPU load120/224,mem800/2015GB(1090GB可用)·ops/inbox无新令(RUN_ID245已执行)·📦TASK=27.8KB✓/MEMORY=20.3KB✓·未完成指令:有(v4 eval运行中→完成后重新生成报告填实测耗时+分数+一致性校验)⇒WAITING:0。

> 2026-11-07 19:00 #1590: 运维令11-07 15:2x监控轮·v4全量GGUF eval运行中(~34min,8 llama-server全health OK,marker epoch=1794047138)·精确进度@18:59:hellaswag chunk0=72/10044(0.7%,4.86s/it,日志stale26min因\r缓冲)chunk1=132/10044(1.3%,4.82s/it,stale21min)chunk2=99/10044(1.0%,21.5s/it,ETA~59h⚠️)chunk3=92/10036(0.9%,14.2s/it,ETA~39h⚠️)·非hellaswag:arc_easy 2389/9501(25%,3.3it/s,ETA~36min)boolq 2778/6540(42%,1.6it/s,ETA~39min+winogrande~26min)arc_challenge 1423/4687(30%,1.2it/s,ETA~47min+openbookqa~29min)sciq 772/4000(19%,1.6it/s,ETA~34min+piqa~39min)·瓶颈=hellaswag chunk2/3极慢(14-21s/it vs chunk0/1 4.8s/it),根因=8并发llama-server内存带宽争用·计划:非hellaswag首批~19:32(sciq+arc_easy)完成后servers 8084-8087释放→带宽压力减半→hellaswag应自然加速;若加速不足→追加hellaswag workers到释放的servers·worst-case ETA~3d(best-case~1.4d)·报告9412B/进行中正确显示·S1健康(GPU.29全100%/75GB/45-63℃,ckpt iter_0118000)·CPU load108/224,mem796/2015GB(1093GB可用)·ops/inbox无新令(RUN_ID245已执行)·research日报11-07 pretrain建议已被v4覆盖·📦TASK=27.8KB✓/MEMORY=19.0KB✓·未完成指令:有(v4 eval运行中→完成后重新生成报告填实测耗时+分数+一致性校验)⇒WAITING:0。

> 2026-11-07 18:52 #1589: 运维令11-07 15:2x监控轮·v4全量GGUF eval继续运行(~27min,8 llama-server×16threads全health OK,marker epoch=1794047138)·进度@18:52:hellaswag chunk0=72/10044(0.7%,4.86s/it,ETA~13.5h)chunk1=132/10044(1.3%,4.82s/it,ETA~13.3h)chunk2=78/10044(0.8%,14.41s/it,ETA~40h⚠️)chunk3=68/10036(0.7%,25.51s/it,ETA~70h⚠️⚠️),arc_easy 1846/9501(19%,ETA~1h),boolq 2215/6540(34%,ETA~36min),sciq 772/4000(19%,ETA~34min),arc_challenge 1155/4687(25%,ETA~1.8h)·⚠️新发现=hellaswag chunk2/3比chunk0/1慢3-5x(14-25s/it vs 4.8s/it),根因=8并发llama-server内存带宽争用(hellaswag长序列memory-bound),servers 8085/8086跑非hellaswag占CPU最高1261%/1047%加剧争用·计划:非hellaswag任务~2h完成后servers 8084-8087释放→内存带宽压力下降→hellaswag可能自然加速;届时再评估是否追加workers(若瓶颈=带宽则加workers无益反而有害)·加速=22.5d基线→worst-case~3d(best-case~1.4d)·报告9412B/进行中正确显示·S1健康(iter_0118000 ckpt在盘,GPU80-100%/75GB/53-64℃)·CPU load99/224,mem796/2015GB(1093GB可用)·ops/inbox无新令(RUN_ID245已执行)·research日报11-07 pretrain建议已被v4覆盖·📦TASK=27.8KB✓/MEMORY=18.2KB✓·未完成指令:有(v4 eval运行中→完成后重新生成报告填实测耗时+分数+一致性校验)⇒WAITING:0。

> 2026-11-07 18:47 #1588: 运维令11-07 15:2x监控轮·v4全量GGUF eval继续运行(~22min,8 llama-server×16threads,marker epoch=1794047138)·进度@18:41:hellaswag chunk0=72/10044 chunk1=132/10044 chunk2=42/10044 chunk3=40/10036(~0.7%瓶颈,长序列SSM慢),arc_easy 938/9501(10%),boolq 1134/6540(17%),sciq 772/4000(19%),arc_challenge 644/4687(14%)·ETA:hellaswag瓶颈~28-33h(4 chunks×~10044 req@~6 req/min/chunk),非hellaswag任务~1.5-4h(servers 8084-8087完成后空闲,可追加hellaswag workers但协调复杂/风险高,留待未来轮)·加速=22.5d基线→~1.4d=~26x(在运维1-2天目标内,不扰乱运行中eval)·报告重生成9412B/0script/0外链/进行中正确显示·S1健康(iter~118100,GPU100%/91%/75GB/55-60℃)·CPU load101/224,mem796/2015GB充裕·📦TASK=27.8KB✓/MEMORY=17.3KB✓·未完成指令:有(v4 eval运行中→完成后重新生成报告填实测耗时+分数+一致性校验)⇒WAITING:0。

> 2026-11-07 18:30 #1587: 运维令11-07 15:2x继续执行·v4全量GGUF eval监控+报告生成器修复·eval运行中(8 llama-server×16threads,启动~5min)·进度:hellaswag 4chunks ~55/10044(~5s/it→~14h ETA瓶颈),arc_easy 203/9501,boolq 309/6540,sciq 394/4000,arc_challenge 152/4687,各任务正常推进无报错·CPU load101/224,mem782/2015GB充裕·修复gen_eval_speedup_report.py:eval_done改为results.json存在即true(不再依赖END marker),wall_sec缺失END时用results.json mtime回退,修v3→v4日志引用,更新docstring·修复baize_llamacpp_full_eval.sh:加END marker写入(供报告读耗时)·报告重新生成9412B/0script/0外链/"进行中"正确显示·S1健康(iter118000,GPU73-100%/75GB/52-61℃/637-690W)·research日报11-07:pretrain建议=StrataFlux量化+HST状态复用提速eval→已被v4 llama.cpp并行方案覆盖,无需额外动作·📦TASK=28.5KB✓/MEMORY=16.8KB✓·未完成指令:有(v4 eval运行中→完成后重新生成报告填实测耗时+分数+一致性校验)⇒WAITING:0。

> 2026-11-07 18:26 #1586: 运维令11-07 15:2x继续执行·v4全量GGUF eval已启动(hellaswag分片4 servers+其余7 tasks分4 servers,8 llama-server×16 threads,8进程并行)·v3失败根因=NFS "Stale file handle"杀死bash脚本→v4修复=脚本+Python全复制到/tmp执行·v4新增hellaswag --samples分片(10042 docs→4 shards×2511 docs,消除木桶效应)·所有8 servers已READY(eval PID3912298+,marker epoch=1794047138)·精度回归已PASS(#1585:iter_10000 HF vs GGUF max Δacc=0.02<n=100 stderr 0.045)·gen_eval_speedup_report.py已指向v4路径·报告9382B/0script/0外链·S1健康(GPU 100%/75GB)·📦TASK=28.5KB✓/MEMORY=15.9KB✓·未完成指令:有(v4 eval运行中→完成后填耗时对照+分数→报告最终更新)⇒WAITING:0。

> 2026-11-07 17:24 #1585: 运维令11-07 15:2x继续执行·精度回归结论=PASS(iter_10000 HF vs GGUF 8集逐比对:arc_challenge Δ0.02/arc_easy Δ0/boolq Δ0.01/hellaswag Δ0.01/openbookqa Δ0.01/piqa Δ0/sciq Δ0/winogrande Δ0,max Δacc=0.02<n=100 stderr 0.045→PASS;iter_100000 GGUF trend raw Avg=54.75%单调上升→converter一致性OK)·iter_112000精度回归卡住41%(1075/2599,28min无进度=HTTP挂起,冗余已kill)·全量GGUF eval已启动(PID3418162,4 servers×56 threads,8 tasks并行,hellaswag+openbookqa→server0,arc_challenge+piqa→server1,arc_easy+sciq→server2,boolq+winogrande→server3)·各任务进度@17:24:openbookqa 6%/boolq 1%/sciq 1%/arc_challenge 0%/arc_easy 0%/winogrande 1%/piqa 0%/hellaswag tokenizing 85%·merge_parallel_results.py修复hellaswag单目录处理·报告更新8796B/0script/0外链·S1健康(GPU 100%/75GB)·load130/224·📦TASK=27.8KB✓/MEMORY=14.5KB✓·未完成指令:有(全量eval运行中→完成后填耗时对照+分数→报告最终更新)⇒WAITING:0。

> 2026-11-07 17:05 #1584: 运维令11-07 15:2x继续执行·精度回归进行中(PID3439735,1075/2599=41%,llama-server 3 req processing,ETA~20min)·验证iter_10000 HF results.json存在(n=100,与GGUF对比max Δacc=0.02 PASS确认)·验证iter_100000 GGUF trend(n=100,raw Avg=54.75%,分数随训练上升→converter一致性OK)·报告更新:gen_eval_speedup_report.py加§三b GGUF跨ckpt一致性表+iter_112000精度回归状态,报告8104B/0script/0外链·全量eval脚本baize_llamacpp_full_eval.sh已确认(4 servers×56 threads,hellaswag独占server0,无--limit=全量73k req)·S1健康(GPU.29 97-100%/75GB)·下一步:精度回归完成→检查NaN+趋势→kill llama-server:8080→启动全量GGUF eval·📦TASK=28.5KB✓/MEMORY=14KB✓·未完成指令:有(精度回归→全量eval→报告最终更新)⇒WAITING:0。

> 2026-11-07 16:50 #1583: 运维令11-07 15:2x执行中·精度回归运行中(PID3439735,1075/2599=~41%,速度降至~0.3req/s因hellaswag长序列,ETA~35min)·llama-server健康(port8080,64线程,8 parallel)·已验证iter_10000 HF vs GGUF:max Δacc=0.02 PASS·全部脚本已创建并提交(cpu_lmeval_run.py/baize_cpu_lmeval.sh加--samples,baize_cpu_lmeval_parallel.sh 11进程,merge_parallel_results.py,baize_llamacpp_full_eval.sh多服务器,gen_eval_speedup_report.py,gguf_lmeval_run.py加--samples)·报告report_pretrain_cpu_eval_speedup_zh.html(7023B)已生成·GGUF转换成功(4.2GB)·串行HF eval已kill(仅0.9%完成)·S1健康·📦TASK=28.5KB✓/MEMORY=13.5KB✓·未完成指令:有(精度回归待完成→全量eval→报告更新)⇒WAITING:0。

> 2026-11-07 15:32 #1581: 例行监控轮·无新运维令·S1健康(iter117220/700000@15:32,loss2.042,7.6-8.5s/it,grad-norm0.087-0.115,0NaN/0skip,GPU.29全满载81-100%/~75GB/139-183W/41-50℃,858-955TFLOP/s/GPU)·ckpt iter_0116000在盘(checkpoints/),HF导出112000在盘,next iter_0118000 ETA~17:00·全量eval后台继续(PID3726478,~4.5h,867%CPU≈8.7核,~10.3GB RSS,nice19,不抢S1)·内存689GB/2015GB(1201GB可用)充裕·load57.7/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·git up-to-date·📦TASK=31.2KB✓/MEMORY=12.3KB✓·未完成指令:无⇒WAITING:1。

> 2026-11-07 15:12 #1580: 例行监控轮·无新运维令·S1健康(iter117080/700000@15:12,7.26-7.42s/it,~980-998TFLOP/s/GPU,GPU.29全满载95-100%/~75GB/~685W/54-63℃)·ckpt iter_0116000在盘(checkpoints/),HF导出110k/112k在盘,next iter_0118000 ETA~17:00·全量eval后台继续(PID3726478,538/73106req@4h11m,~26.7s/req稳定,868%CPU≈8.7核,10.4GB RSS,nice19,不抢S1,ETA~22天)·内存690GB/2015GB(1200GB可用)充裕·load48.9/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·git up-to-date·📦TASK=31.2KB✓/MEMORY=11.3KB✓·未完成指令:无⇒WAITING:1。


> 2026-11-07 14:50 #1579: 例行监控轮·无新运维令·S1健康(GPU.29全满载94-100%/~75GB/~690W/55-65℃@14:49 nvidia-smi确认;SSH.29后续超时疑似瞬态负载,非S1问题)·ckpt iter_0116000在盘(同#1578,下一iter_0118000 ETA~17:00)·全量eval后台继续(PID3726478,487/73106req@3h49m,~26.8s/req稳定,868%CPU≈8.7核,11.7GB RSS,nice19,不抢S1,ETA~22.5天)·内存692GB/2015GB充裕·load47/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·⚠️L2日志尾部见error traceback但系另一实验(step2370/5611/loss0.94≠S1)非S1,S1 GPU仍94-100%·git up-to-date·📦TASK=31.2KB✓/MEMORY=11.3KB✓·未完成指令:无⇒WAITING:1。


> 2026-11-07 14:26 #1578: 例行监控轮·无新运维令·S1健康(iter~116690/700000@14:26,loss~2.04,~7s/it,0NaN/0skip,GPU.29全满载96-100%/~75GB/665-696W/54-63℃)·ckpt iter_0116000在盘(同#1577)·全量eval后台继续(PID3726478,434/73106req@3h26m,~26.4s/req稳定,867%CPU≈8.7核,11.4GB RSS,nice19,不抢S1,ETA~22天)·内存686GB/2015GB充裕·load40.9/224核·ops/inbox无新令(RUN_ID245旧令已执行)·research日报11-07无pretrain建议·git up-to-date·📦TASK=31.2KB✓/MEMORY=10.5KB✓(归档#1043-#1555→summary pointer,释放~21KB)·未完成指令:无⇒WAITING:1。


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