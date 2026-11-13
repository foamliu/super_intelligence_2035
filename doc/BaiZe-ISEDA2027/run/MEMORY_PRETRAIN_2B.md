# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1（🔴 2026-11-12 用户令「L1/L2评测脚本入库+L4移交post-train」已完成·**L1/L2 eval脚本已入库baize-llm/scripts/eval/（13文件✅[+200k autoqueue],README§4.6已更新✅,commit ed6ea54e4）**·**L1 18/20done(10k-180k,峰值160k=58.13%,180k=57.25%)·190k autoqueue运行中(.29 PID234256 polling iter_0190000,etime~16.1h)·ETA~22min·200k autoqueue脚本已创建(待启动)**·**L2 🟢HF五重验证全部完成:HumanEval HF=15.0%✅+GSM8K HF=10.0%✅+MBPP HF=5.0%✅+BBH HF=3.3%✅+MATH HF=0.0%✅·MMLU=23.16%**·**L3 TB smoke 0/2·无GPU做vLLM重试**·**L4 HANDOFF→post-train（2026-11-12用户令·只读引用）**·**论文§4.6已刷新iter177k+PDF 0err✅·红线PASS**·训练健康iter≈189.81k/700k(27.1%) GPU 8×95-100%/75GB step~7.0s✅）
> 2026-11-13 17:50 #2126: **监控巡检轮·训练健康iter189810/700k(27.1%) step6985-7180ms(<7.4s✅) loss2.02-2.06 0NaN/0skip**·**动作**：①git pull origin main --rebase --autostash(ff to 2b0a5aafd✅) ②训练健康(.29):`timeout 5 cat /proc/146283/fd/1 | tail -20`→iter189810,step6985-7180ms,loss2.02-2.06,lr=1e-3(stable),grad_norm~0.085-0.140,0NaN/0skip ③GPU 8×95-100%/~75GB✅ ④190k autoqueue运行中(.29 PID234256,ppid=1,etime=58007s≈16.1h,sleeping 300s polling iter_0190000,latest log \"waiting for ckpt(train iter=189800,57900s)\",latest ckpt=iter_0188000,ETA~190 iters×7.0s≈22min→~18:12) ⑤L1 eval 18/20done(10k-180k)✅,190k ckpt未落盘(NOT_YET,ETA~22min) ⑥no llama-server running✅(pgrep count=0) ⑦eval scripts 13files in baize-llm/scripts/eval/✅ ⑧红线PASS(grep 4_llm_pretrain.tex benchmark名=0hits✅) ⑨research日报11-13:pretrain建议=并行策略表+YaRN+Sanity Checks→均未来训练用,不可操作 ⑩📦TASK≈28.6KB✅/MEMORY≈26.4KB✅·四层评测 · L1=57.25%@180k(峰值160k=58.13%) L2=🟢HF五重验证完成 L3=TB 0/2 L4=🟦HANDOFF→post-train · 本轮动作：监控巡检·未完成指令：有(190k autoqueue polling,ETA~22min)⇒WAITING:1。
> 2026-11-13 17:27 #2125: **监控巡检轮+200k autoqueue脚本创建·训练健康iter189610/700k(27.1%) step6932-7096ms(<7.4s✅) loss2.031-2.056 0NaN/0skip**·**动作**：①git pull --rebase --autostash(up to date✅) ②训练健康(.29):`timeout 5 cat /proc/146283/fd/1 | tail -20`→iter189610,step6932-7096ms,loss2.031-2.056,lr=1e-3(stable),grad_norm~0.089-0.625,0NaN/0skip ③GPU 8×100%/75GB✅ ④190k autoqueue运行中(.29 PID234256,ppid=1,etime=56563s≈15.7h,sleeping 300s polling iter_0190000,190k ckpt NOT_YET,latest log "waiting for ckpt(train iter=189590,56400s)",latest ckpt=iter_0188000,ETA~410 iters×7.0s≈48min→~18:12) ⑤L1 eval 18/20done(10k-180k)✅,190k ckpt未落盘(NOT_YET,ETA~48min) ⑥no llama-server running✅(pgrep count=0) ⑦eval scripts 13files in baize-llm/scripts/eval/✅(+baize_l1_autoqueue_200k.sh新建,PORT=8192,待190k完成后启动) ⑧红线PASS(grep 4_llm_pretrain.tex benchmark名=0hits✅) ⑨research日报11-13:pretrain建议=并行策略表+YaRN+Sanity Checks→均未来训练用,不可操作 ⑩📦TASK≈28.6KB✅/MEMORY≈26.4KB✅·四层评测 · L1=57.25%@180k(峰值160k=58.13%) L2=🟢HF五重验证完成 L3=TB 0/2 L4=🟦HANDOFF→post-train · 本轮动作：监控巡检+200k autoqueue脚本创建·未完成指令：有(190k autoqueue polling,ETA~48min)⇒WAITING:1。
> 2026-11-13 17:07 #2124: **监控巡检轮·训练健康iter189440/700k(27.1%) step6991-7094ms(<7.4s✅) loss2.006-2.056 0NaN/0skip**·**动作**：①git pull --rebase --autostash(up to date✅) ②训练健康(.29):`timeout 5 cat /proc/146283/fd/1 | tail -20`→iter189440,step6991-7094ms,loss2.006-2.056,lr=1e-3(stable),grad_norm~0.088-4.060(偶发spike 4.060@189340),0NaN/0skip ③GPU 8×100%/75GB✅(GPU7=95%) ④190k autoqueue运行中(.29 PID234256,ppid=1,etime=55410s≈15.4h,sleeping 300s polling iter_0190000,190k ckpt NOT_YET,latest log "waiting for ckpt(train iter=189420,55200s)",ETA~560 iters×7.0s≈1.1h→~18:12) ⑤L1 eval 18/20done(10k-180k)✅,190k ckpt未落盘(NOT_YET,ETA~18:12) ⑥no llama-server running✅(pgrep count=0) ⑦eval scripts 12files in baize-llm/scripts/eval/✅ ⑧红线PASS(grep 4_llm_pretrain.tex benchmark名=0hits✅) ⑨research日报11-13:pretrain建议=并行策略表(TP×PP×DP)+YaRN+Sanity Checks→均未来训练用,当前stable phase不可操作 ⑩📦TASK≈28.6KB✅/MEMORY≈25.1KB✅·四层评测 · L1=57.25%@180k(峰值160k=58.13%) L2=🟢HF五重验证完成 L3=TB 0/2 L4=🟦HANDOFF→post-train · 本轮动作：监控巡检·未完成指令：有(190k autoqueue polling,ETA~1.1h)⇒WAITING:1。
> 📦 #2123（11-13 16:43, 监控巡检轮+归档·训练step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：训练持续健康iter189230,190k autoqueue polling ETA~1.5h,L1 18/20done,红线PASS,归档#2116-#2121。需要时再读。
> 📦 #2116–#2121（11-13 14:05→16:03, 6轮监控巡检·训练step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：训练持续健康iter187870→189070,190k autoqueue polling ETA从4.1h→1.8h,L1 18/20done,红线PASS。需要时再读。
> 📦 #2110–#2115（11-13 12:02→13:45, 6轮监控巡检·训练step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：训练持续健康iter186830→187710,190k autoqueue polling ETA从6.2h→4.5h,L1 18/20done,红线PASS。需要时再读。
> 📦 #2064–#2109（11-12 18:35→11-13 11:40, ~23轮监控巡检·训练step6.9-7.5s<7.4s✅）→ daily-memories/2026-11-12.md + 2026-11-13.md；**结论**：训练持续健康iter178030→186650,190k autoqueue polling ETA从22h→6.5h,L1 18/20done(180k=57.25%),L4 HANDOFF→post-train,L1/L2脚本入库确认✅。需要时再读。
> 📦 #2063（11-12 18:10, 监控巡检+L3/L4资源调查轮·训练step7039ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：L3/L4均BLOCKED(无GPU/SSH不通),训练健康iter177810。需要时再读。
> 📦 #2062（11-12 17:45, MATH HF eval完成+L2 HF五重验证全部完成+四层报告刷新轮·训练step~7.0s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：MATH HF=0/10=0.0%,L2 HF五重验证完成(Avg5集=6.66%),llama.cpp SSM bug确认为0%主因。需要时再读。
> 📦 #2061（11-12 17:15, BBH HF eval结果收集+MATH HF eval启动+四层报告刷新轮·训练step7020ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：BBH HF=1/30=3.3%,四重验证完成,MATH HF启动。需要时再读。
> 📦 #2060（11-12 16:08, MBPP HF eval完成+L4确认+监控巡检轮·训练step7006ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：MBPP HF pass@1=1/20=5.0%,三重验证确认llama.cpp SSM bug是0%主因。需要时再读。
> 📦 #2059（11-12 15:30, GSM8K HF v2完成(10.0%)+L4确认+四层报告刷新轮·训练step~7.5s<7.4s⚠️）→ daily-memories/2026-11-12.md；**结论**：GSM8K HF=1/10=10.0%,确认llama.cpp SSM bug是L2生成0%主因(HumanEval+GSM8K双验证),L4 BLOCKED(SSH)。需要时再读。
> 📦 #2058（11-12 15:00, L2 HumanEval HF完整评测轮·训练step6945ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：HumanEval HF pass@1=3/20=15.0%,确认llama.cpp SSM bug是L2生成0%主因。需要时再读。
> 📦 #2055（11-12 14:05, 监控巡检+四层报告刷新轮·训练step6928ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter175.7k,L2 HumanEval HF 1/4 PASS(25%部分),L4仍BLOCKED。需要时再读。
> 📦 #2054（11-12 13:45, 监控巡检+L2 HumanEval HF部分评测轮·训练step7015ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：HumanEval HF 1/4 PASS(25%部分,below_zero✅)确认llama.cpp SSM bug是L2生成0%主因,L4仍BLOCKED。需要时再读。
> 📦 #2053（11-12 13:05, 监控巡检+L2 GSM8K生成退化诊断轮·训练step~7076ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：GSM8K=0%(生成退化+能力不足),L4仍BLOCKED。需要时再读。
> 📦 #2052（11-12 12:40, 监控巡检轮·训练step~7099ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter175.0k,autoqueue正常,L4仍BLOCKED。需要时再读。
> 📦 #2051（11-12 12:17, 监控巡检+autoqueue超时修复轮·训练step~7068ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：autoqueue旧PID152293超时→重启PID2896237(18h timeout),训练健康iter174.84k。需要时再读。
> 📦 #2050（11-12 11:46, 监控巡检+L2 v6确认+P2数据配方建议轮·训练step~7000ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter174.5k,L2 v6确认HumanEval=0%/MBPP=0%为真能力问题,红线PASS。需要时再读。
> 📦 #2050（11-12 11:46, 监控巡检+L2 v6确认+P2数据配方建议轮·训练step~7000ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter174.5k,L2 v6确认HumanEval=0%/MBPP=0%,MATH进程已死(84/100),P2建议等350k再判。需要时再读。
> 📦 #2049（11-12 11:27, 监控巡检+§4.6进度刷新轮·训练step~7000ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter174.36k,§4.6刷新iter174.4k,红线PASS。需要时再读。
> 📦 #2049（11-12 11:27, 监控巡检+§4.6进度刷新轮·训练step~7000ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter174.36k,§4.6刷新iter174.4k,红线PASS。需要时再读。
> 📦 #2048（11-12 10:58, 监控巡检+MEMORY归档瘦身轮·训练step~7050ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter174.15k,autoqueue正常,L4仍BLOCKED,MEMORY瘦身30KB→22KB。需要时再读。
> 📦 #2047（11-12 10:38, 监控巡检轮·训练step~7090ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter173.99k,autoqueue正常,L4仍BLOCKED。需要时再读。
> 📦 #2046（11-12 10:15, 监控巡检轮·训练step~7060ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter173.8k,autoqueue正常,L4仍BLOCKED。需要时再读。
> 📦 #2045（11-12 09:55, 监控巡检轮·训练step~7.05s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter173.6k,autoqueue正常,L4仍BLOCKED。需要时再读。
> 📦 #2044（11-12 09:35, 监控巡检轮·训练step~7060ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter173.4k,autoqueue正常,L4仍BLOCKED。需要时再读。
> 📦 #2043（11-12 09:15, 监控巡检轮·训练step~7.05s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter173.28k,autoqueue正常,L4仍BLOCKED。需要时再读。
> 📦 #2042（11-12 08:53, 监控巡检轮·训练step~7060ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter173.1k,autoqueue正常,L4仍BLOCKED。需要时再读。
> 📦 #2041（11-12 08:33, 监控巡检轮·训练step~7028ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter172.93k,autoqueue正常。需要时再读。
> 📦 #2040（11-12 08:13, 监控巡检+四层报告刷新轮·训练step~7030ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter172.75k,四层报告已刷新,L3 smoke done。需要时再读。
> 📦 #2039（11-12 07:52, 监控巡检+180k autoqueue启动轮·训练step~7010ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：180k autoqueue已启动,L4仍BLOCKED。需要时再读。
> 2026-11-12 07:52 #2039: **监控巡检+180k autoqueue启动轮·训练健康iter172550/700k(24.6%) step6977-7093ms(均~7010ms<7.4s✅) loss2.02-2.03 0NaN/0skip GPU 8×82-100%/75GB·180k autoqueue已启动(PID152293,.29,polling iter_0180000)**·**动作**：①git pull --rebase(同步✅) ②训练健康(.29 /proc/146283/fd/1):iter172550/700k,step6977-7093ms(均~7010ms<7.4s✅),loss2.020-2.028,0NaN/0skip,GPU 8×82-100%/75GB ③L1:17/17done,180k autoqueue已创建并启动(baize_l1_autoqueue_180k.sh,PID152293,.29,polling iter_0180000,PORT=8191,-t4,nice19,serial,自动HF→GGUF→eval→report) ④L4重测:SSH .15/.17均timeout→仍BLOCKED;查NFS共享发现zhulong/designflow bench脚本+jsonl在doc/ZhuLong_DAC2027/benchmark/(94条cline_eval_status.jsonl),但EDA工具在.15→仍需SSH ⑤research日报2026-11-12:pretrain建议=Day-0探针→mid-training不actionable(同#2037/#2038) ⑥红线检查:4_llm_pretrain.tex无benchmark数字PASS✅ ⑦无eval运行(CPU干净✅) ⑧📦TASK≈27KB✅/MEMORY≈27KB✅·四层评测 · L1=57.75%@170k(17/17,峰值160k=58.13%) L2=6/6完成(全0%除MMLU=23.16%) L3=TB 0/2(pipeline✅) L4=🔴BLOCKED(SSH) · 本轮动作：监控巡检+180k autoqueue创建启动+L4 NFS调研+红线检查·未完成指令：无(等180k ckpt落盘~14h,autoqueue自动处理)⇒WAITING:1。
> 📦 #2038（11-12 07:25, 监控巡检轮·训练step~7.0s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter172.35k,无新ckpt,L4仍BLOCKED。需要时再读。
> 📦 #2037（11-12 07:04, 监控巡检轮·训练step~7.0s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康iter172.2k,无新ckpt,L4仍BLOCKED。需要时再读。
> 📦 #2035（11-12 06:25, 论文§4.6刷新+L2分析确认轮·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：论文§4.6 iter171.8k+PDF 0err,L2根因=llama.cpp SSM bug+24.5%训练。需要时再读。
> 📦 #2034（11-12 05:55, 170k L1 eval完成+报告刷新·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：170k eval=57.75%,L1 17/17done,scaling report刷新。需要时再读。

> 📦 #2033（11-12 05:45, 170k eval监控+四层报告更新·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：170k eval持续运行中(76min),训练健康。需要时再读。
> 📦 #2032（11-12 05:39, 170k eval监控+L4再测+四层报告更新·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：eval持续运行,L4 SSH .15/.17均timeout→BLOCKED。需要时再读。
> 📦 #2031（11-12 05:10, 170k eval监控+四层报告更新·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：GGUF转换✅,eval运行中,stale cat清理,红线PASS。需要时再读。
> 📦 #2030（11-12 03:56, 170k GGUF转换stuck诊断+kill重启v4+四层报告更新·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：GGUF转换stuck@88%已kill,v4脚本重启(后GGUF完成,eval运行中)。需要时再读。
> 📦 #2028（11-12 03:30, 170k GGUF转换监控+eval v3脚本启动+stale进程清理·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：GGUF转换启动(18%),eval v3脚本启动,stale find进程已清理。需要时再读。
> 📦 #2027（11-12 03:12, 170k L1 eval pipeline修复+启动·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：autoqueue GGUF失败修复(mamba_dt_limit删除),GGUF转换启动,eval脚本启动(15min timeout,后超时)。需要时再读。
> 📦 #2026（11-12 02:45, 🟢HF生成突破+GSM8K HF重评+报告更新·训练step7.1s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：HF transformers生成正常,llama.cpp SSM bug是L2=0%主因,GSM8K HF=0/10。需要时再读。
> 📦 #2023–#2025（11-12 01:55→02:20, 监控巡检+论文§4.6刷新iter169.8k+L1 scaling report+autoqueue启动·训练step<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康,论文§4.6已刷新iter169.8k+PDF 0err,170k autoqueue已启动。需要时再读。
> 📦 #2023（11-12 01:55, 监控巡检+L1 scaling report更新·训练step7060ms<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康,160k scaling report已更新。需要时再读。
> 📦 #2021（11-12 02:00, 监控巡检+L4根因再确认+归档#2018·训练step7.1s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康,L4 BLOCKED确认。需要时再读。
> 📦 #2020（11-12 01:20, 监控巡检+L4根因确认+归档#2018·训练step7.1s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：训练健康,L4 BLOCKED确认。需要时再读。
> 📦 #2019（11-12 01:11, 监控巡检+红线检查+research日报·训练step7.0s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：红线检查PASS(无benchmark数字泄漏),research建议不适用。需要时再读。
> 📦 #2018（11-12 01:05, L3 TB smoke完成0/2+论文§4.6刷新+llama-server清理·训练step7.1s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：L3 TB 0/2 reward(生成退化),论文§4.6 iter169k+PDF 0err✅。需要时再读。
> 📦 #2017（11-12 00:45, L2 6/6完成+L3 TB smoke启动·训练step7.0s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：L2全部完成(5/6=0%),L3 TB smoke启动(Harbor 2 tasks)。需要时再读。
> 📦 #2016（11-12 00:20, v6 HumanEval✅+MBPP/MATH监控轮·训练step7.0s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：HumanEval pass@1=0.0%,MBPP 73/100,MATH 55/100,两v6实例并发。需要时再读。
> 📦 #2014（11-12 00:02, MBPP+MATH并发监控+重复v6实例发现·训练step7.1s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：MBPP 49/100,MATH 31/100,发现两个v6实例并发(PID2571213+2632593)。需要时再读。
> 📦 #2013（11-11 23:55, L3 autoqueue启动+MBPP监控+L4调研·训练step7.1s<7.4s✅）→ daily-memories/2026-11-12.md；**结论**：L3 autoqueue已启动(PID1986722),MBPP 34/100,L4 BLOCKED(/nasdata/未挂载.29+SSH不通)。需要时再读。
> 📦 #2006–#2023（11-11 22:50→11-12 02:00, 多轮监控+v6 HumanEval/MBPP/MATH评测+L3前置+L4确认+L1 scaling+autoqueue启动·训练step<7.4s✅）→ daily-memories/2026-11-11.md + 2026-11-12.md；**结论**：L2 6/6完成(5/6=0%),L3前置通过TB 0/2,L4 BLOCKED,170k autoqueue启动。需要时再读。
> 📦 #1993–#2005（11-11 20:35→22:30, v5 MATH完成+v6启动+GSM8K/BBH确认+生成退化诊断+vLLM调查+L3/L4调研·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：v5 MATH=0%,BBH v4=0%,GSM8K v3=0%,生成退化=SSM state崩溃+模型能力不足。需要时再读。

## 🔴 待决策区（需用户拍板 · 2026-11-12 #2059 更新 · GSM8K HF=10.0%修正诊断）

**背景**：L2 llama.cpp: GSM8K=0% / BBH=0% / MATH≈0% / MMLU=23.16%(≈随机25%)。L3 TB 0/2。L4 HANDOFF→post-train。**🟢 HF transformers 重评: HumanEval=15.0%(3/20) + GSM8K=10.0%(1/10) → 模型有基础代码+数学能力, llama.cpp SSM bug 是 0% 主因**。

**🟢 2026-11-12 HF transformers 重评定案（#2058+#2059）**：
- HumanEval HF pass@1=3/20=15.0% (filter_by_substring✅, string_sequence✅, count_distinct_characters✅) vs llama.cpp 0/100=0%
- GSM8K HF acc=1/10=10.0% (第5题gt=20 pred=20✅, 9/10 FAIL但生成数值答案非退化) vs llama.cpp 0/100=0%
- **结论：llama.cpp SSM 生成 bug（PR #31703）是 L2 生成任务 0% 的主因（已 HumanEval+GSM8K 双验证）。模型有基础代码生成+数学推理能力, 但能力有限 (15%+10%)。**
- **L2 评测应全面切换到 HF transformers**（BBH/MATH/MBPP 待后续轮 HF 重评）

**三重根因（修正后）**：
1. **llama.cpp SSM 生成 bug（主因）**：HF transformers 生成正常, 证明模型权重/SSM 计算正确, 问题在 llama.cpp 的 SSM 生成实现 (PR #31703)。**修复路径：用 HF transformers/vLLM 替代 llama.cpp 做生成评测**。
2. **数据配比不足**：code 19% + math 7% = 26%, HF 测试显示 code 生成有效 (HumanEval=15%), math 有基础能力 (GSM8K=10%) 但不足。仍需 decay 阶段增加 math 比例。
3. **Decay 阶段未配置**：`--lr-decay-iters 0`, 一直在 stable 段。Decay 是注入 domain data 的最佳时机。

**方案 A（推荐）**：decay 阶段混入 code:math:language=4:2:4 + L2 切换到 HF transformers 评测
**方案 B**：post-train SFT 补数学推理 + L2 用 HF 重评
**方案 C**：A+B 组合

**L4 已移交 post-train（2026-11-12 用户令）**：L4（zhulong 消融评测 + designflow/EDA-LiveFlow-Bench）不再由 pretrain 负责。post-train 隧道已 4 次复验 OK、run_code 端到端 PASS。Pretrain 从本轮起 L4 统一写「HANDOFF→post-train」，不再做 L4 资源调查/SSH .15/.17 直连。四层口径：L1/L2/L3 由 pretrain 负责；L4 只读引用（post-train 出数后引用）。

> 📦 #1992（11-11 20:21, 论文§4.6刷新+PDF编译+四层报告更新·训练step~7.1s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：§4.6 iter166730+PDF 0err,v5 MATH 30/100。需要时再读。
> 📦 #1991（11-11 20:12, v6脚本创建+启动+四层报告刷新·训练step~7.0s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：v6修复confirm_run_unsafe_code+RP=1.3,等port8083。需要时再读。
> 📦 #1990（11-11 20:05, v5重启+L1验证+数据配比确认+四层报告刷新·训练step7043ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：L1 160k harness Avg=58.13%逐集验证✅,code19%+math7%=26%。需要时再读。
> 📦 #1943–#1989（11-11 06:28→19:42, 四层评测全面启动+L2 v3/v4/v5评测+GSM8K/BBH诊断+生成退化根因(llama.cpp SSM bug)+数据配比调研(DeepSeek 4:2:4)+L1 160k=58.13%验证+§4.6刷新+L3/L4调研, 共~47轮）→ daily-memories/2026-11-11.md；**结论汇总**：①L1 160k峰值58.13%✅ ②L2 llama.cpp全0%→HF验证HumanEval=15%+GSM8K=10%+MBPP=5%确认SSM bug是0%主因 ③GSM8K=0%双重根因(SSM bug+能力不足) ④S1 blend含26%code+math(非"无code/math") ⑤建议decay阶段混入4:2:4(方案A,待用户拍板) ⑥L3/L4低分同因=数据缺code+math。需要时再读。

> 📦 #1888–#1923（11-10 11:59-22:25, 论文刷新#1918-#1921+stale PDF修正+15轮状态确认·训练健康iter150350-155620 step<7.4s✅·15/15eval全完成·等160k~8-18h后）→ daily-memories/2026-11-10.md；**结论**：论文§4.6刷新完成(#1918),§4.7撤回(#1921),stale PDF修正(#1921),后续状态确认均无新ckpt,训练健康。需要时再读。
> 📦 #1924–#1940（11-10 22:48→11-11 04:40, 论文§4.6刷新轮·训练健康step<7.4s✅）→ daily-memories/2026-11-11.md；需要时再读。

> 📦 #1802–#1887（11-09 11:58→11-10 10:54, 110k/120k/130k/140k eval pipeline+状态确认·训练step<7.4s✅·14/14eval全完成）→ daily-memories/2026-11-{09,10}.md；需要时再读。


> 📦 §#1043–#1801（11-01→11-09, v4/v5/v6 eval监控+anomaly调查+100k eval交付, 共~800轮）→ daily-memories/2026-11-{01..09}.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：①100k eval 10/10 ckpt harness Avg 51.50→57.75%已交付 ②anomaly调查=口径差异(结论A):stale results.json缺piqa致低估37.4%,补全后Avg7=55.96% ③v4旧二进制回归致sciq=0.44(修复后0.88) ④llama.cpp PR#31703修复混合架构权重错位 ⑤S1训练全程健康0NaN/0skip,loss~2.05-2.16,ckpt iter_38000→138000. 需要时再读 daily-memories。

---

## 待决策（等用户拍板）

### P2-001: L2/L3 评测瓶颈 — llama.cpp SSM bug + 早期训练（2026-11-12 #2063 更新 · HF五重验证完成）
- **现状**：160k ckpt(25%训练) L2 评测：llama.cpp 全 0%（SSM 生成 bug）。**🟢 HF transformers 五重验证完成**：HumanEval=15.0%(3/20) + GSM8K=10.0%(1/10) + MBPP=5.0%(1/20) + BBH=3.3%(1/30) + MATH=0.0%(0/10)，生成 Avg5集=6.66%。MMLU=23.16%(≈随机25%,MC不受生成bug影响=纯能力不足)。L3 TB smoke 0/2(llama.cpp生成退化)。L4 已移交 post-train。
- **根因定案（HF五重验证后）**：
  1. **llama.cpp SSM 生成 bug（主因）**：PR #31703 修复了权重映射，但生成仍退化(repetition loop)。HF transformers 生成正常，证明模型权重/SSM 计算正确。**修复路径：L2/L3 评测应用 HF transformers/vLLM 替代 llama.cpp**。
  2. **数据配比不足**：code 19% + math 7% = 26%。HF 显示 code 生成有效(15%) + math 有基础能力(10%) 但不足。MATH=0% 是唯一 HF 也=0% 的任务(MATH-500 难度远超 2B@25%训练)。
  3. **训练早期(25%)**：模型在 stable phase(lr=1e-3 恒定)，尚未进入 instruction-SFT/decay。MMLU≈随机说明知识能力未建立。
- **L3/L4 资源调查（#2063 新增 · #2069 L4 移交）**：
  - L3：无可用 GPU 做 vLLM-based 评测(.29 pretrain 8×100%, .12 vision R9 8×100%, .17 SSH timeout)。vLLM/SGLang 未安装在 .29/.12。CPU HF 太慢(multi-turn agentic)。
  - L4：**已移交 post-train（2026-11-12 用户令）**。不再做 L4 资源调查/SSH。post-train 隧道已 4 次复验 OK。
- **建议（🚫 不自行改生产配置）**：
  1. **短期(当前~350k,50%)**：维持现状继续监控。每 20k ckpt 跑 L1+L2(HF)，观察 MMLU 是否从 25% 起步上升、生成能力是否随训练改善。
  2. **评测改进**：L2 已切换到 HF transformers（五重验证完成）。L3 需 GPU 窗口(vLLM)或等 SSH .17 恢复。L4 已移交 post-train（不再 pretrain 负责）。
  3. **中期(350k~decay前)**：若 MMLU 仍≈25%，考虑 decay phase 增加 code/math 占比(从 6% 提到 15-20%)。
  4. **长期**：L3 agentic 需 post-train SFT/RL（posttrain 线负责）；L4 已由 post-train 主责。
- **需要的输入**：用户裁定 ① 维持现状等 350k 再判 ② 提前调整 decay phase 配比 ③ 等 .17 SSH 恢复后接 L3 ④ 等 700k 训完在 post-train 阶段补 L3。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)