# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1
> 🛑 **【运维通告 · 2026-11-02 19:51】S1 已由 ops 中继重启并在跑**：`bash scripts/train.sh s1 --nodes 2`，launcher pid **4163528**，从 **ckpt 58000** 续（19:55:40 起 iter **58010**→58030，7.0–7.2 s/step ≈**582K tok/s**，双机 16 卡 **98–100%**、~75GB/卡、~690W）。⇒ **GPU 不再空闲**：🚫 严禁再起任何训练/GPU 评测进程；CPU 评测必须降载：`OMP_NUM_THREADS≤8` + `nice -n 19`，**禁止 `pkill python`**。

> 2026-11-06 16:53 #1519: 例行监控轮·无新运维令·S1健康(worker log活跃 iter105770/700000@16:53:29,loss2.057,6.94-7.21s/it,lr1e-3,0NaN/0skip,grad-norm0.088-0.418稳态(105660/105720瞬态spike0.390/0.418自恢复),consumed27077120)·GPU.29(0-7:95-100%/~75GB/56-64℃/582-657W)全满载,launcher PID146283(etimes334752s≈92.9h)·latest ckpt iter_0104000@~13:26·next ckpt iter_0106000 ETA~17:20(230it×~7s≈27min)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY=27.9KB✓(均远低于32KB,无需归档)·未完成指令:无⇒WAITING:1。


> 2026-11-06 16:35 #1518: 例行监控轮·无新运维令·S1健康(worker log活跃 iter105600/700000@16:33:34,loss2.068,6.99-7.13s/it,lr1e-3,0NaN/0skip,grad-norm0.092-0.127稳态(105560瞬态spike0.785自恢复),consumed27033600)·GPU.29(0-7:96-100%/~75GB/56-66℃/683-695W)+.12(0-7:96-100%/~75GB/56-66℃/680-693W)全满载,launcher PID146283(etimes333610s≈92.7h)·latest ckpt iter_0104000@~13:26·next ckpt iter_0106000 ETA~17:20(400it×~7s≈47min)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(.12无llama-server/lm_eval/convert)·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY=27.1KB✓(均远低于32KB,无需归档)·未完成指令:无⇒WAITING:1。


> 2026-11-06 16:15 #1517: 例行监控轮·无新运维令·S1健康(worker log活跃 iter105440/700000@16:14:21,loss2.056,6.96-7.16s/it,lr1e-3,0NaN/0skip,grad-norm0.085-0.112稳态,consumed26992640)·GPU.29(0-7:100%/~75GB/56-64℃/682-695W)+.12(0-7:93-100%/~75GB/57-66℃/668-693W)全满载,launcher PID4163528(etimes332689s≈92.4h)·loop健康(.29 PID3165013)·latest ckpt iter_0104000@~13:26·next ckpt iter_0106000 ETA~17:19(560it×~7s≈65min)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(.12无llama-server/lm_eval/convert)·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY=26.3KB✓(均远低于32KB,无需归档)·未完成指令:无⇒WAITING:1。

> 2026-11-06 15:53 #1516: 例行监控轮·无新运维令·S1健康(worker log活跃 iter105260/700000@15:53:14,loss2.064,6.99-7.09s/it,lr1e-3,0NaN/0skip,grad-norm0.091-0.107稳态(105240瞬态spike0.985自恢复),consumed26946560)·GPU.29(0-7:96-100%/~75GB/55-65℃/686-697W)+.12(0-7:100%/~75GB/57-66℃/683-696W)全满载,launcher PID146283(etimes331256s≈92.0h)·latest ckpt iter_0104000@~13:26·next ckpt iter_0106000 ETA~17:19(740it×~7s≈86min)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(.12无llama-server/lm_eval/convert)·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,目标PID3640274已不存在;非本线待办)·git clean(pull already up to date,##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY=25.4KB✓(均远低于32KB,无需归档)·未完成指令:无⇒WAITING:1。


> 2026-11-06 15:30 #1515: 例行监控轮·无新运维令·S1健康(worker log活跃 iter105060/700000@15:29:46,loss2.066,6.93-7.12s/it,lr1e-3,0NaN/0skip,grad-norm0.093-0.122稳态,consumed26895360)·GPU.29(0-7:80-100%/~75GB/56-65℃/680-693W)全满载,launcher PID146283·latest ckpt iter_0104000@~13:26·next ckpt iter_0106000 ETA~17:20(940it×~7s≈110min)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY≈26KB✓(滚动#1499-#1507至daily-memories,释放~6.7KB)·未完成指令:无⇒WAITING:1。


> 2026-11-06 15:10 #1514: 例行监控轮·无新运维令·S1健康(worker log活跃 iter104890/700000@15:09:50,loss2.068,6.97-7.15s/it,lr1e-3,0NaN/0skip,grad-norm0.092-0.162稳态,consumed26851840)·GPU.29(0-7:97-100%/~75GB/56-65℃/676-691W)+.12(0-7:97-100%/~75GB/57-67℃/681-691W)全满载,launcher PID146283(etimes328613s≈91.3h)·latest ckpt iter_0104000@~13:26·next ckpt iter_0106000 ETA~17:18(1110it×~7s≈2.2h)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(.12无llama-server/lm_eval/convert)·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY≈30.2KB✓·未完成指令:无⇒WAITING:1。

> 2026-11-06 14:46 #1513: 例行监控轮·无新运维令·S1健康(worker log活跃 iter104660/700000@14:42:51,loss2.08,6.9-7.1s/it,lr1e-3,0NaN/0skip,grad-norm0.087-0.141(14:41瞬态spike0.799自恢复),consumed26792960)·GPU.29(0-7:95-100%/~75GB/58-65℃/676-697W)+.12(0-7:96-100%/~75GB/57-66℃/676-691W)全满载,launcher PID146283·latest ckpt iter_0104000@13:26·next ckpt iter_0106000 ETA~17:20(1340it×~7s≈2.6h)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(.12无llama-server/lm_eval/convert)·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY≈29.5KB✓(滚动#1496-#1498至daily-memories)·未完成指令:无⇒WAITING:1。


> 2026-11-06 14:26 #1512: 例行监控轮·无新运维令·S1健康(worker log活跃 iter104510/700000@14:25:18,loss2.074,6.9-7.1s/it,lr1e-3,0NaN/0skip,grad-norm0.091-0.203稳态,consumed26754560)·GPU.29(0-7:97-100%/~75GB/55-64℃/678-694W)+.12(0-7:97-100%/~75GB/57-65℃/680-695W)全满载,launcher PID146283·latest ckpt iter_0104000(13:26)·next ckpt iter_0106000 ETA~17:20(1490it×~7s≈2.9h)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出·ops/inbox仅RUN_ID245(2026-11-05旧令,已执行,目标PID3640274已不存在;当前.cline_pretrain会话PID63389为本轮新唤醒,非卡死)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY≈30.7KB✓·未完成指令:无⇒WAITING:1。

> 2026-11-06 14:07 #1511: 例行监控轮·无新运维令·S1健康(worker log /tmp/baize_s1_baize2b_worker.log 活跃 iter104350/700000@14:06:40,loss2.051,6.95-7.10s/it,lr1e-3,0NaN/0skip,grad-norm0.087-0.175稳态,consumed26713600)·GPU.29(0-7:95-100%/~75GB/678-695W/55-63℃)+.12(0-7:96-100%/~75GB/668-699W/53-64℃)全满载,launcher PID146283(pretrain_launcher.py --arch mamba2 --name baize2b --dir .../BaiZe-ISEDA2027/nemo_experiments,seq16384/save2000/lr1e-3)·latest ckpt iter_0104000@~13:26·next ckpt iter_0106000 ETA~17:18(1650it×~7s≈3.2h)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出·ops/inbox RUN_ID245属ops中继旧令(2026-11-05,已执行,目标PID已不存在)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY≈30.5KB✓·未完成指令:无⇒WAITING:1。

> 2026-11-06 13:43 #1510: 例行监控轮·无新运维令·S1健康(worker log活跃 iter104150/700000@13:43:23,loss2.061,6.89-7.03s/it,lr1e-3,0NaN/0skip,grad-norm0.091-0.111稳态)·GPU.29(0-7:97-100%/~75GB/58-65℃/679-690W)+.12(0-7:76-100%/~75GB/53-62℃/597-629W)全满载,launcher PID146283 etimes~323359s≈89.8h·latest ckpt iter_0104000@~13:26(新存,前为iter_0102000)·next ckpt iter_0106000 ETA~17:20(1850it×~7s≈3.6h)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(.12无llama-server/lm_eval/convert)·ops/inbox RUN_ID245属ops中继旧令(2026-11-05,已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY≈29.6KB✓·未完成指令:无⇒WAITING:1。


> 2026-11-06 13:22 #1509: 例行监控轮·无新运维令·S1健康(worker log活跃 iter103970/700000@13:22:27,loss2.059,6.94-7.14s/it,lr1e-3,0NaN/0skip,grad-norm0.085-0.132稳态)·GPU.29(0-7:96-100%/~75GB/56-64℃/680-694W)+.12(0-7:96-100%/~75GB/56-65℃/679-698W)全满载,launcher PID146283 etimes~322122s≈89.5h,~1015-1048TFLOP/s/GPU·latest ckpt iter_0102000·next ckpt iter_0104000 ETA~13:26(30it×~7s≈4min)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(无llama-server/lm_eval)·ops/inbox空(无新令)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY=28.3KB✓·未完成指令:无⇒WAITING:1。


> 2026-11-06 13:01 #1508: 例行监控轮·无新运维令·S1健康(worker log活跃 iter103790/700000@13:01:24,loss2.053,6.95-7.12s/it,lr1e-3,0NaN/0skip,grad-norm0.090-0.118稳态)·GPU.29(0-7:96-100%/~75GB/55-66℃/644-686W)+.12(0-7:97-100%/~75GB/58-66℃/676-696W)全满载,launcher PID146283 etimes~320907s≈89.1h,~1019-1046TFLOP/s/GPU·latest ckpt iter_0102000·next ckpt iter_0104000 ETA~13:26(210it×~7s≈25min)·100k eval已于#1490交付(10/10全在,Avg harness 57.75%/raw 54.75%)·eval管线已全退出(无llama-server/lm_eval)·ops/inbox RUN_ID245属ops中继旧令(已执行,非本线待办)·git clean(##main...origin/main无ahead/behind)·未碰他线在途文件·📦体积:TASK=25.8KB✓/MEMORY=27.6KB✓·未完成指令:无⇒WAITING:1。

> 📦 §#1499-#1507（11-06 09:57-12:42, 9轮例行监控）→ daily-memories/2026-11-06.md「归档 #1499-#1507」节；**结论**：S1健康iter102210→103790/700000,0NaN/0skip,ckpt iter_0102000→iter_0104000@13:26,100k eval已交付(10/10,Avg harness 57.75%)。需要时再读。


> 📦 §#1496-#1498（11-06 08:52-09:34, 3轮例行监控）→ daily-memories/2026-11-06.md「归档 #1496-#1498」节；**结论**：S1健康iter101660→102010/700000,0NaN/0skip,ckpt iter_0100000→iter_0102000@09:32,100k eval已交付(10/10)。需要时再读。

> 📦 §#1495（11-06 08:31, 监控轮·iter101480健康）→ daily-memories/2026-11-06.md；**结论**：S1健康iter101480/loss2.056,ckpt iter_0100000,next iter_0102000 ETA~09:32。需要时再读。
> 📦 §#1491-#1494（11-06 07:13→07:52, 3轮例行监控+归档轮）→ daily-memories/2026-11-06.md；**结论**：S1健康iter100980→101143/700000,0NaN/0skip,#1491归档运维令11-05至ARCHIVE_OPERATOR_PRETRAIN.md。被#1494接续。需要时再读。

> 📦 §#1489（11-06 06:35, 监控轮·100k eval进行中·9/9完好）→ daily-memories/2026-11-06.md；**结论**：9/9完好,100k MISSING(eval~52min),ETA~06:44-06:46,双管线自治。被#1490收口(10/10交付)。需要时再读。

> 📦 §#1467-#1475+#1490（11-06 04:10-06:46, 10轮监控+100k交付轮）→ daily-memories/2026-11-06.md「归档 #1467-#1475 + #1490」节；**结论**：双管线自治健康,9/9 results完好,100k(iter_0100000)于#1490交付(10/10,Avg harness 57.75%),训练iter 99.3k→102.6k稳步推进。被#1496确认延续。需要时再读。

> 📦 §#1455-#1467（11-06 02:50-04:10, 13轮监控·均与#1468一致无漂移）→ daily-memories/2026-11-06.md；**结论**：双管线健康,9/9 results完好,100k pending,训练iter 98.5k→99.3k稳步推进,无干预。被#1468确认延续。需要时再读。
> 📦 §#1452-#1454（11-06 02:39-02:46, 3轮监控·均与#1455一致无漂移）→ daily-memories/2026-11-06.md；**结论**：双管线健康,9/9 results完好,100k pending,无干预。被#1455确认延续。需要时再读。
> 📦 §#1451（11-06 02:31, 监控轮·与#1452重复）→ daily-memories/2026-11-06.md；**结论**：与#1452一致,双管线健康,9/9 results完好,100k pending。被#1452确认延续。需要时再读。
> 📦 §#1450（11-06 02:25, 更正#1449误判+补watcher）→ daily-memories/2026-11-06.md；**结论**：旧管线3543961仍活(做100k eval),autopipeline1929017已死;新建report-refresh watcher PID2702412;修正Avg(10k=51.50..90k=57.88)。被#1451确认延续。需要时再读。
> 📦 §#1449（11-06 02:16, 误判更正）→ daily-memories/2026-11-06.md；**结论**：#1449称旧管线已死/autopipeline已启动=**误判**；实测旧管线3543961仍活(做100k eval),autopipeline1929017已死;#1450已更正并补report-refresh watcher。需要时再读。
> 📦 §#1448（11-06 02:02, 监控轮·旧管线仍活·100k pending）→ daily-memories/2026-11-06.md；**结论**：旧管线PID3543961当时健康(后被#1449发现已死),9/9 results完好,100k ETA~05:39。需要时再读。
> 📦 §#1445-#1447（11-06 01:42→01:57, 3轮监控·100k pending）→ daily-memories/2026-11-06.md；**结论**：管线自治健康轮询,9/9 results.json完好,100k ETA~Nov6 05:39。需要时再读。
> 📦 §#1443-#1444（11-06 01:29→01:36, 2轮监控·100k pending）→ daily-memories/2026-11-06.md；**结论**：管线自治健康轮询,9/9 results.json完好,100k ETA~Nov6 05:38。需要时再读。
> 📦 §#1441-#1442（11-06 01:17→01:24, 2轮监控·100k pending）→ daily-memories/2026-11-06.md；**结论**：管线自治健康轮询,9/9 results.json完好,100k ETA~Nov6 05:38。需要时再读。

> 📦 §#1435–#1440（11-06 00:34→00:53, 4轮监控·100k pending）→ daily-memories/2026-11-06.md；**结论**：管线自治健康轮询,9/9 results.json完好,100k ETA~Nov6 05:38。需要时再读。

> 📦 §#1428–#1431（11-05 23:54→11-06 00:12, 4轮监控·100k pending）→ daily-memories/2026-11-06.md；**结论**：管线自治健康轮询,9/9 results.json完好,100k ETA~Nov6 05:38。需要时再读。

> 📦 §#1420–#1427（11-05 23:04→23:48, 5轮监控·100k pending）→ daily-memories/2026-11-06.md「归档 #1420–#1427」节；**结论**：管线自治健康轮询,9/9 results.json完好,90k eval落盘→v2报告9/10,100k ETA~Nov6 05:38。需要时再读。
> 📦 §#1419-#1421（11-05 22:52-23:09 · 90k eval收尾监控轮）→ daily-memories/2026-11-05.md「归档 #1419-#1421」节；**结论**：90k eval落盘→v2报告刷新9/10,管线进入100k轮询态,无干预。需要时再读。
> 📦 §#1413-#1418（11-05 19:17-19:48 · 60k eval 监控轮）→ daily-memories/2026-11-05.md「归档 #1413-#1418」节；**结论**：管线自治健康,60k eval 推进中(5/10→进行中),无干预。需要时再读。

> 📦 §#1409-#1412（11-05 18:52-19:13, 60k eval启动+4轮监控）→ daily-memories/2026-11-05.md；**结论**：60k-100k评测启动,60k GGUF转换DONE,管线PID3543961后台运行,生成器v2(10点)就绪,v2报告5/10(18974B)。被#1413+接续。需要时再读。

> 2026-11-05 18:02 #1407: 例行空唤醒巡检·全绿·S1健康·运维令09:0x已交付。→ daily-memories/2026-11-05.md。被#1409接续。
> 2026-11-05 16:39 #1403: 运维令09:0x·✅5/5 ckpt终版报告交付(report_pretrain_llamacpp_scaling_zh.html 17777B, Avg 51.50→52.00→53.00→55.12→54.25%, 700k外推60.16% R²=0.792, commit b8669b0de+bd812d0c0)。→ daily-memories/2026-11-05.md。被#1409接续(60k-100k继续)。
> 📦 §#1396-#1408（11-05 10:3x–18:21, 11-05 09:0x 5ckpt评测全过程监控轮）→ daily-memories/2026-11-05.md；**结论**：5/5 DONE报告交付,全程管线健康,每ckpt~74min。被#1409接续(扩到10点)。需要时再读。
> 📦 §#1367-#1395（11-05 10:3x–15:18, 5ckpt评测前期监控轮）→ daily-memories/2026-11-05.md；**结论**：管线全程健康,iter_10000@11:40→50000@16:37,生成器口径bug已修。被#1396+收口。需要时再读。
> 📦 §#1360-#1366（11-05 08:0x–10:2x, llama.cpp 3-bug fix+管线启动）→ daily-memories/2026-11-05.md；**结论**：3 bugs fixed(rope_type/build_attention_layer/FFN),commit 5dc38db00,1-token Δmax=0.006,管线启动。需要时再读。

> 📦 §#1363（11-05 09:0x, CPU eval退化根因·SSM数值不稳定）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：退化ckpt 17+ token时logits全NaN;根因=Mamba2 SSM数值不稳定(PyTorch reference CPU float32);退化eval为NaN伪影非真实能力。被#1360 llama.cpp C++ SSM修复(5 ckpt全可出分)取代。需要时再读。

> 📦 §#1359（11-05 06:0x, ROOT CAUSE:Q/K undo_permute损坏）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：Q/K权重被GGUF转换undo_permute损坏(max_diff0.15);Nemotron-H RoPE不需permute;fix=undo_permute=False。被#1360 3-bug fix(commit 5dc38db00,Δmax0.006)落地。需要时再读。
> 📦 §#1357（11-05 04:1x, 22:1x+14:0x执行·静态对照A/B/C已落盘·清理完成）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：A(group)PASS/B(conv1d)PASS/C(dt clamp)FAIL(无clamp);清理llama-server11→1/GGUF去重7→2释放21G;3.6nats偏差需D/E。被#1360 3-bug fix彻底解决。需要时再读。

> 📦 §#1356（11-04 13:2x, logits逐token对齐定案·根因=映射/计算错误）→ daily-memories/2026-11-04.md；**结论**：1-token即偏3.6nats,定案=映射/计算错误(非精度累积),llamacpp.txt §6+§7已更新,commit eca8b7f49。被#1360 3-bug fix取代。需要时再读。

> 🆕 2026-11-04 13:0x #1355：**llama.cpp 深度根因调查轮·GGUF 元数据验证=正确·真根因=C++ Mamba2 计算·报告已更正·50K eval DONE 5/5 完成·报告已更正**。运维令 09:3x（llama.cpp 提速）深度调查结果：① **GGUF 元数据经原始二进制解析验证完全正确**：block_count=56、feed_forward_length 数组(28 MLP=8192/24 SSM=0/4 attn=0)、head_count_kv 数组(4 attn=4/其余=0)→层分类逻辑正确。② **权重值逐一比对一致**(bf16→f16 精度仅)。③ **此前根因"Duplicated key 覆写元数据"不成立**——转换无实质错误。④ **真根因**：C++ `build_mamba2_layer`(基类 `llm_build_mamba_base`)的 Mamba2 SSM 数值实现与 PyTorch reference 有系统性计算差异→56层误差累积→logit 偏移。⑤ **生成质量测试**："The capital of France is"→GGUF 输出"the French department, which is the French department"(重复垃圾)→推理根本损坏。⑥ **llama-bench 测速**：F16 CPU 8线程 pp128=82 t/s / tg64=21 t/s（vs HF float32 ~3 t/s，快约7×但精度不可用）。⑦ **/v1/completions 格式**：返回新版 `logprobs.content[]` 非 `token_logprobs`，需 shim 或 --model gguf 后端（次要矛盾）。⑧ **5/5 eval 全部完成**：iter_10000 Avg=50.0%✅ / iter_30000 Avg=50.25%✅ / iter_20000+40000+50000 均 Avg=28.75%⚠️NaN(sciq=0.0, 三 ckpt 结果完全一致, md5 各不同→NaN 导致 tie-breaking 确定性, FP8 间歇性溢出)。⑨ **报告已更正** §⑤根因+llama-bench+生成测试+格式, §⑥ NaN 更新, 5/5 汇总表填满。**VERDICT: llama.cpp=FAIL(精度不可用)，保留 HF float32，等用户令**。📦 体积：TASK=31KB✅/MEMORY≈16KB✅。未完成指令：无（5/5 eval DONE, 报告已更新, llama.cpp=FAIL 等用户令）⇒ WAITING: 1。
> 📦 §#1322-#1328（11-04 03:28–04:12, 7轮监控·pilot=FAIL等令·4evals推进·S1 iter74190→74580）→ daily-memories/2026-11-04.md；**结论汇总**：4 evals稳定推进(.29~17s/it/.12~28s/it), 最坏ETA~13:05<deadline✅, iter_10000 DONE Avg50%, S1全程0NaN, CPU均<<80%。pilot=FAIL等用户令。需要时再读。

> 📦 §#1332（11-04 08:28, 监控轮·4evals推进正常·S1 iter76780健康）→ daily-memories/2026-11-04.md；**结论**：4 evals推进, 最坏ETA~13:20, iter_10000 DONE Avg50%, S1 iter76780健康0NaN, CPU<<80%。被#1333确认继续有效。需要时再读。

> 📦 §#1334（11-04 08:42, 监控轮+归档pilot块·4evals推进正常·S1 iter76880健康）→ daily-memories/2026-11-04.md；**结论**：4 evals推进, 最坏ETA~13:15, iter_10000 DONE Avg50%, S1 iter76880健康0NaN, CPU<<80%, pilot块已归档。被#1335确认继续有效。需要时再读。

> 📦 §#1339（11-04 09:07, 监控轮·4evals推进正常·S1 iter77120健康·最坏ETA~13:12）→ daily-memories/2026-11-04.md；**结论**：4 evals推进, 最坏ETA~13:12, iter_10000 DONE Avg50%, S1 iter77120健康0NaN, CPU<<80%。被#1340确认继续有效。需要时再读。

> 📦 §#1346（11-04 10:37, llama.cpp重试new binary 149f5641b·Δ16-18pp未修复·HF evals 2/5DONE+3在跑·S1 iter77890健康）→ daily-memories/2026-11-04.md；**结论**：新binary git diff无SSM改动，sciq=0.61/piqa=0.56与旧pilot一致，Δacc仍超标，保留HF float32。被#1347确认。需要时再读。
> 📦 §#1347（11-04 10:48, 监控轮·清理stale pilot server·TASK归档33918→31010B·HF evals 2/5DONE+3在跑·S1 iter77930健康）→ daily-memories/2026-11-04.md；**结论**：kill旧pilot server, TASK归档至30.3KB✅, .12两evals 95-96% ETA~11:28-11:39, .29 iter_50000_f32 80% ETA~13:03。被#1348确认。需要时再读。

> 📦 §#1348（11-04 10:57, 监控轮·HF evals 2/5DONE+3在跑·S1 iter78070健康·ckpt@78000）→ daily-memories/2026-11-04.md；**结论**：.12两evals 96-97% ETA~11:28-11:39, .29 iter_50000_f32 81% ETA~13:07, iter_10000/30000 DONE。被#1349-#1350确认继续有效。需要时再读。

> 📦 §#1349（11-04 11:03, 监控轮·HF evals 2/5DONE+3在跑·.12两evals ETA~11:28-11:39·.29 83% ETA~12:58）→ daily-memories/2026-11-04.md；**结论**：.12两evals即将完成, .29 iter_50000_f32 82.9% ETA~12:58, 2/5有效DONE。被#1350确认继续有效。需要时再读。
> 📦 §#1350（11-04 11:12, 监控轮·4evals推进·.12两evals即将完成）→ daily-memories/2026-11-04.md；**结论**：4evals推进, .12两evals 97-98%即将完成, .29 iter_50000_f32 84% ETA~12:56, iter_10000/30000 DONE Avg50%/50.25%。被#1351确认(.12两evals完成=NaN)。需要时再读。

> 📦 §#1351（11-04 11:40, .12两evals DONE均NaN·NaN=ckpt权重问题非dtype）→ daily-memories/2026-11-04.md；**结论**：iter_20000/40000(f32)NaN=FP8间歇性溢出,iter_10000/30000 Avg50%/50.25%valid。被#1352确认。需要时再读。

> 📦 §#1352（11-04 11:46, .29 50000_f32 90%·20000/40000/50000三者结果完全一致=确定性退化）→ daily-memories/2026-11-04.md；**结论**：NaN权重产生确定性退化(非随机)。被#1353接续。需要时再读。

> 📦 §#1292-#1345（11-03 23:24→11-04 10:03, ~50轮监控·pilot=FAIL等令·4 evals推进·S1 iter72110→77600）→ daily-memories/2026-11-03.md & 2026-11-04.md；**结论汇总**：pilot=FAIL已交付(commit 9cdc4469f,根因=3 Duplicated key覆写hybrid元数据),4 evals稳定推进,iter_10000 DONE Avg50%,iter_30000 DONE Avg50.25%,S1全程0NaN,CPU均<<80%。需要时再读 daily-memories。

> 📦 §#1353（11-04 12:1x, llama.cpp重试·per-token打分打通·pilot DONE=Δacc超标FAIL）→ daily-memories/2026-11-04.md；**结论**：per-token lmeval.py绕echo卡点,sciqΔ=-37pp/piqaΔ=-17pp,FAIL保留HF路线。被#1360 3-bug fix取代。需要时再读。
> 📦 §#1290（11-03 23:12, llama.cpp pilot=FAIL·7.03x加速达标但Δacc=-17pp超标）→ daily-memories/2026-11-03.md；**结论**：iter_10000 F16 GGUF sciq79%→61%(Δ=-18pp),根因=F16在Mamba2 SSM递归累积精度。保留HF float32路线。被#1360 3-bug fix取代。需要时再读。
> 📦 §#1291（11-03 23:17, 监控轮·pilot DONE 等令·3 evals 推进）→ daily-memories/2026-11-03.md；**结论**：iter_30000 29/2599(1.1%)@48s/it(ramping down), iter_40000 956/2599(36.8%)@30.4s/it→done~Nov4 13:15, iter_20000 953/2599(36.7%)@30.3s/it→done~Nov4 13:13, S1 iter72040/loss2.107✅, CPU .29 16.8%/.12 15.3%<<80%✅。被#1292 校正(iter_30000 ramp-down 收敛至16s/it done~Nov4 09:17)。需要时再读。
> 📦 §#1290（11-03 23:12, llama.cpp pilot=FAIL）见上条详述。需要时再读。
> 📦 §#1289（11-03 22:10, 监控轮·iter_50000 96.9%）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 96.9%(2518/2599) ETA~22:31, .12 双 float32 31.6%+31.4% ETA Nov4 13:12-13:15, iter_30000 SIGSTOP(510), S1 iter71470健康。被#1290 接续（pilot 已完成=FAIL）。需要时再读。
> 📦 §#1288（11-03 22:04, 监控轮·iter_50000 95.8%@15.67s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 95.8%(2491/2599) ETA~22:31, .12 双 float32 31.1%+31.0%(808+805)@~30.1s/it ETA Nov4 13:07-13:13, iter_30000 SIGSTOP(510), S1 iter71410/loss2.098健康。被#1289 校正(iter_50000 96.9%(2518)@15.68s/it, .12 820+817@~30.4s/it, S1 iter71470/loss2.101)。需要时再读。
> 📦 §#1287（11-03 21:57, 监控轮·iter_50000 95.0%@15.99s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 95.0% ETA~22:32, .12 双 float32 30.5%+~30%@~29.5s/it ETA Nov4 12:45-12:55, iter_30000 SIGSTOP(510), S1 iter71360/loss2.112健康。被#1288 校正。需要时再读。
> 📦 §#1286（11-03 21:52, 监控轮·iter_50000 94.2%@15.66s/it）→ daily-memories/2026-11-03.md；**结论**：被#1287 校正。需要时再读。
> 📦 §#1285（11-03 21:46, 监控轮·iter_50000 93.3%@~16.1s/it）→ daily-memories/2026-11-03.md；**结论**：被#1286 校正。需要时再读。
> 📦 §CPU-eval-snapshot #1234-#1290（11-02→11-03, 5 ckpt HF float32 CPU eval 监控·iter_10000 Avg=50.0% DONE/iter_50000 bf16 sciq=0 NaN/bf16→float32 修复/OMP=8/SIGSTOP 副作用）→ daily-memories/2026-11-02.md & 2026-11-03.md；**结论**：iter_10000 Avg=50.0%, bf16 NaN→float32 修复, 全 5/5 CPU eval 已被 11-05 llama.cpp 修复管线取代。需要时再读。
> 📦 §#1234-#1283（11-03 14:50→21:34, ~40轮监控·iter_50000 56%→92%·bf16 NaN根因+float32重跑+OMP=8+SIGSTOP优化）→ daily-memories/2026-11-03.md；**结论汇总**：bf16 NaN→float32修复, OMP=8收敛34.78s/it, SIGSTOP优化, 速度收敛(.29~16s/.12~30s), iter_10000 DONE Avg50%, CPU全程<<80%。需要时再读 daily-memories。

> 📦 §#1154-#1241（11-02 19:55→11-03 16:13, CPU eval监控·1-80轮+bf16 NaN根因+float32重跑+OMP优化+SIGSTOP）→ daily-memories/2026-11-02.md & 2026-11-03.md；**结论汇总**：5 export完成, bf16 NaN→float32修复, OMP=8, SIGSTOP优化, 速度收敛(.29~16s/.12~30s), iter_10000 DONE Avg=50%, ETA从~10天下修至<24h, CPU全程<<80%。需要时再读 daily-memories。
> 📦 §#1076-#1151（11-01 11:26→11-02 12:55, S1健康监控iter41950→55140, 共~70轮）→ daily-memories/2026-11-01.md & 2026-11-02.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.10-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt iter_38000→54000, grad-norm极稳(偶发瞬态spike均自恢复), decay 5000步CS8=58.97%, 论文6页ERR=0, baize-llm项目目录就绪。需要时再读 daily-memories。
> 📦 §#1043及更早（11-01 11:26前, iter≤41950, S1监控链#1044~#1067及更早）→ daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, ckpt iter_38000→42000; decay CS8=58.97%; 论文6页ERR=0。需要时再读。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实�