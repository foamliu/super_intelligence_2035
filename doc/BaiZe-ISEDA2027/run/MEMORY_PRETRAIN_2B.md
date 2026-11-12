# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1（🔴 2026-11-11 用户令「四层评测拿更好结果」执行中·**L1 17/17done(10k-170k,峰值160k=58.13%)·180k autoqueue运行中(PID152293,.29,~3h elapsed)ETA~11.7h**·**L2 6/6完成(全0%除MMLU=23.16%·llama.cpp SSM bug+24.8%训练=L2弱)**·**L3 TB smoke 0/2(pipeline✅,2/2 reward=0.0)**·**L4🔴SSH.15/.17timeout**·**论文§4.6已刷新iter171.8k+PDF 0err✅·红线PASS**·训练健康iter≈174.15k/700k(24.9%) GPU 8×94-100%/75GB step~7050ms<7.4s✅）
> 2026-11-12 10:58 #2048: **监控巡检+MEMORY归档瘦身轮·训练健康iter174150/700k(24.9%) step6910-7324ms(均~7050ms<7.4s✅) loss2.03-2.06 0NaN/0skip GPU 8×94-100%/75GB·180k autoqueue运行中(PID152293,.29,elapsed~11083s≈3.1h,polling iter_0180000,ETA~11.7h)**·**动作**：①git pull --rebase(同步✅,already up to date) ②训练健康(.29 /proc/146283/fd/1):iter174150/700k,step6910-7324ms(均~7050ms<7.4s✅),loss2.03-2.06,0NaN/0skip,GPU 8×94-100%/75GB·注意iter174060 loss spike(2.497/grad_norm73.7)已立即恢复 ③autoqueue健康:PID152293 alive(elapsed~11083s≈3.1h),正确polling;latest ckpt=iter_0174000(174k),180k ETA~11.7h(需~5850 iter×7s≈40950s) ④L4重测:SSH .15/.17均timeout(ConnectTimeout=10)→仍BLOCKED ⑤红线检查:4_llm_pretrain.tex grep benchmark名0命中 PASS✅ ⑥无eval运行(CPU干净✅,pgrep llama-server/lm_eval 0进程) ⑦research日报11-12:pretrain建议=Day-0探针+RL token budget,均mid-training不actionable ⑧**MEMORY归档瘦身**:6条full entry(#1992/#1991/#1990/#1984/#1983/#1979)转为📦指针,30KB→~22KB ⑨📦TASK≈27KB✅/MEMORY≈22KB✅(归档6条)·四层评测 · L1=57.75%@170k(17/17,峰值160k=58.13%) L2=6/6完成(全0%除MMLU=23.16%) L3=TB 0/2(pipeline✅) L4=🔴BLOCKED(SSH) · 本轮动作：监控巡检+autoqueue健康确认+红线检查+L4重测+MEMORY归档瘦身·未完成指令：无(等180k ckpt落盘~11.7h,autoqueue自动处理)⇒WAITING:1。
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

## 🔴 待决策区（需用户拍板 · 2026-11-12 #2026 更新 · HF生成发现修正诊断）

**背景**：L2 GSM8K=0% / BBH=0% / MATH≈0% / MMLU=23.16%(≈随机25%)。L3 TB 0/2。L4 BLOCKED。

**🟢 2026-11-12 重大发现修正诊断**：用 HF transformers (sglang env, transformers 5.18.0, CPU bfloat16) 对 160k ckpt 做 3-prompt 生成测试 → **全部生成连贯文本**：
- "The capital of France is" → "Paris, and the capital of the French Republic is Paris..." ✅
- GSM8K → "48" (答案错误正确=72, 但生成连贯) → 数学能力不足但生成正常
- def fibonacci(n) → 正确的迭代实现 + assert 测试 ✅
- **结论：L2 生成任务 0% 主要由 llama.cpp SSM 生成 bug 导致, 不是模型完全无能力**
- GSM8K 10-sample HF 重评运行中 (PID 2300774, .29 CPU, nice 19)
- 待决策：L2 全部生成任务应用 HF transformers 重评 (而非继续用 llama.cpp)

**三重根因（修正后）**：
1. **llama.cpp SSM 生成 bug（主因）**：HF transformers 生成正常, 证明模型权重/SSM 计算正确, 问题在 llama.cpp 的 SSM 生成实现 (PR #31703)。**修复路径：用 HF transformers/vLLM 替代 llama.cpp 做生成评测**。
2. **数据配比不足**：code 19% + math 7% = 26%, 但 HF 测试显示 code 生成有效 (Fibonacci 正确), math 不足 (GSM8K 答错)。仍需 decay 阶段增加 math 比例。
3. **Decay 阶段未配置**：`--lr-decay-iters 0`, 一直在 stable 段。Decay 是注入 domain data 的最佳时机。

**方案 A（推荐）**：decay 阶段混入 code:math:language=4:2:4 + L2 切换到 HF transformers 评测
**方案 B**：post-train SFT 补数学推理 + L2 用 HF 重评
**方案 C**：A+B 组合

**其他待解**：.17/.15 SSH 不通 → vLLM 验证 + L4 designflow 数据不可达（需运维检查网络）

> 📦 #1992（11-11 20:21, 论文§4.6刷新+PDF编译+四层报告更新·训练step~7.1s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：§4.6 iter166730+PDF 0err,v5 MATH 30/100。需要时再读。
> 📦 #1991（11-11 20:12, v6脚本创建+启动+四层报告刷新·训练step~7.0s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：v6修复confirm_run_unsafe_code+RP=1.3,等port8083。需要时再读。
> 📦 #1990（11-11 20:05, v5重启+L1验证+数据配比确认+四层报告刷新·训练step7043ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：L1 160k harness Avg=58.13%逐集验证✅,code19%+math7%=26%。需要时再读。
> 📦 #1989（11-11 19:42, GSM8K诊断完成+RP=1.3测试+四层报告刷新·训练step7156ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：GSM8K=0%(双重根因:llama.cpp SSM bug+模型能力不足),RP=1.3=0%。需要时再读。
> 📦 #1988（11-11 19:20, BBH v4完成+v5 NFS崩溃+GSM8K诊断启动·训练step7018ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：BBH=0%,GSM8K诊断启动。需要时再读。
> 📦 #1987（11-11 19:00, vLLM调查+生成退化根因更新+BBH监控·训练step7156ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：vLLM有原生NemotronH支持,BBH 83/100。需要时再读。
> 📦 #1986（11-11 18:36, BBH监控+训练健康确认+四层报告刷新·训练step7163ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：BBH 64/100，训练健康。需要时再读。
> 📦 #1985（11-11 18:30, BBH监控+训练健康+L1 160k验证·训练step7027ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：L1 160k harness Avg=58.13%逐集验证✅,BBH 59/100。需要时再读。
> 📦 #1984（11-11 18:10, 生成退化诊断+BBH监控+四层报告刷新·训练step7092ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：首token正确但多tokenSSM崩溃,repeat_penalty可部分修复。需要时再读。
> 📦 #1983（11-11 18:00, 数据配比修正+BBH监控+四层报告刷新·训练step7.04s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：S1 blend实际含26% code+math(非"无code/math"),BBH 32/100。需要时再读。
> 📦 #1982（11-11 17:50, GSM8K诊断启动+BBH监控·训练step7.0s<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：GSM8K诊断脚本已建(baize_l2_gsm8k_diag.sh),BBH 23/100。需要时再读。
> 📦 #1981（11-11 17:38, v5 HF_ALLOW_CODE_EVAL修复+BBH监控·训练step7100ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：v5脚本已修复HF_ALLOW_CODE_EVAL,BBH 14/100。需要时再读。
> 📦 #1980（11-11 17:25, L2 v3✅完成+v4启动+四层报告刷新·训练step7150ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：v3 GSM8K=0%+MMLU=23.16%✅,v4启动。需要时再读。
> 📦 #1979（11-11 16:56, L3 pipeline创建+L2 v3监控+四层报告刷新·训练step7020ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：L3脚本已建,MMLU~90%运行中。需要时再读。
> 📦 #1978（11-11 16:39, L2 v3监控(MMLU~82%)+四层报告刷新·训练step7059ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~82%运行中,v4等v3。需要时再读。
> 📦 #1977（11-11 16:32, L2 v3监控(MMLU~80%)+四层报告刷新·训练step7100ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~80%运行中,v4等v3。需要时再读。
> 📦 #1976（11-11 16:20, L2 v3监控(MMLU~74%)+P2数据配比调研(DeepSeek 4:2:4)+四层报告刷新·训练step7088ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：P2 DeepSeek消融4:2:4最优,建议decay混入code+math(方案A)。需要时再读。
> 📦 #1975（11-11 16:15, L2 v3监控(MMLU~70%)+四层报告刷新·训练step7144ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~70%运行中,v4等v3。需要时再读。
> 📦 #1974（11-11 16:10, L2 v3监控(MMLU~64%)+四层报告刷新·训练step7075ms<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~64%运行中,v4等v3。需要时再读。
> 📦 #1972–#1973（11-11 15:48→15:55, L2 v3监控+四层报告刷新·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~58%运行中,v4等v3。需要时再读。
> 📦 #1971（11-11 15:38, L2 v3监控+四层报告刷新·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~49%运行中,v4等v3。需要时再读。
> 📦 #1970（11-11 15:29, L2 v3监控+四层报告刷新·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~43%运行中,v4等v3。需要时再读。
> 📦 #1969（11-11 15:22, L2 v3监控+四层报告刷新·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~37%运行中,v4等v3。需要时再读。
> 📦 #1967（11-11 15:00, L2 v3监控+四层报告刷新·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：MMLU~24%运行中,v4等v3。需要时再读。
> 📦 #1966（11-11 14:50, L3/L4可行性调研完成+定性测试+四层报告更新·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：L3/L4低分/空白同一根因=训练数据缺code+math。需要时再读。
> 📦 #1965（11-11 14:33, L2 v3监控+v4启动+§4.6刷新·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：v4已启动轮询port8082,§4.6刷新iter163790。需要时再读。
> 📦 #1961–#1964（11-11 13:5x→14:2x, L2 v3进度监控+v4脚本准备+L3/L4调研+GSM8K=0%诊断定案+四层报告归位·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：GSM8K=0%是真能力问题(数据缺math/code,退化重复"1"),L3/L4调研完成(designflow 61任务/TB 89题需本地API),四层报告归位run/reports/。需要时再读。
> 📦 #1959–#1960（11-11 10:0x→13:3x, 四层评测启动+L2 v2崩溃修复+v3重评启动·训练step<7.4s✅）→ daily-memories/2026-11-11.md；**结论**：L2 v2 MMLU崩溃=llama-server不返回token_logprobs→v3改用gguf_lmeval_run.py logit_bias。需要时再读。
> 📦 #1943–#1958（11-11 06:28→09:44, 论文§4.6刷新轮+160k eval交付+GGUF转换修复·训练step<7.4s✅）→ daily-memories/2026-11-11.md；需要时再读。

> 📦 #1888–#1923（11-10 11:59-22:25, 论文刷新#1918-#1921+stale PDF修正+15轮状态确认·训练健康iter150350-155620 step<7.4s✅·15/15eval全完成·等160k~8-18h后）→ daily-memories/2026-11-10.md；**结论**：论文§4.6刷新完成(#1918),§4.7撤回(#1921),stale PDF修正(#1921),后续状态确认均无新ckpt,训练健康。需要时再读。
> 📦 #1924–#1940（11-10 22:48→11-11 04:40, 论文§4.6刷新轮·训练健康step<7.4s✅）→ daily-memories/2026-11-11.md；需要时再读。

> 📦 #1802–#1887（11-09 11:58→11-10 10:54, 110k/120k/130k/140k eval pipeline+状态确认·训练step<7.4s✅·14/14eval全完成）→ daily-memories/2026-11-{09,10}.md；需要时再读。


> 📦 §#1043–#1801（11-01→11-09, v4/v5/v6 eval监控+anomaly调查+100k eval交付, 共~800轮）→ daily-memories/2026-11-{01..09}.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：①100k eval 10/10 ckpt harness Avg 51.50→57.75%已交付 ②anomaly调查=口径差异(结论A):stale results.json缺piqa致低估37.4%,补全后Avg7=55.96% ③v4旧二进制回归致sciq=0.44(修复后0.88) ④llama.cpp PR#31703修复混合架构权重错位 ⑤S1训练全程健康0NaN/0skip,loss~2.05-2.16,ckpt iter_38000→138000. 需要时再读 daily-memories。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log �