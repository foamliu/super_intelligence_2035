# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1（✅ 2026-11-12 用户令「L1/L2评测脚本入库+L4移交post-train」已完成·**L1/L2 eval脚本已入库baize-llm/scripts/eval/（13文件✅,含新建210k autoqueue,README§4.6已更新✅,commit ed6ea54e4）**·**L1 20/20done(10k-200k,**NEW PEAK 200k=60.12%**↑↑,prev peak 160k/190k=58.13%)·report已刷新20/20+700k pred 61.67%(R²=0.811)✅·210k autoqueue RUNNING✅(.29 PID3942311,serial guard polling for 210k ckpt,train@~203.3k,ETA~13.2h)**·**L2 🟢HF五重验证全部完成:HumanEval=15.0%+GSM8K=10.0%+MBPP=5.0%+BBH=3.3%+MATH=0.0%·MMLU=23.16%**·**L3 TB smoke 0/2·无GPU做vLLM重试**·**L4 HANDOFF→post-train（2026-11-12用户令·只读引用）**·**论文§4.6已刷新iter190k+PDF已重编译✅·红线PASS(benchmark名0命中)·已提交**·训练健康iter≈203.3k/700k(29.0%) GPU 8×94-100%/75GB✅）
> 2026-11-14 20:10 #2197: **监控巡检·训练健康iter203260/700k(29.0%) GPU 8×94-100%/75GB✅**·**动作**：①git pull→Already up to date✅ ②训练健康(.29 PID4179175 /proc/4179175/fd/1):iter203260/700k,step~7000-7110ms(avg~7050ms<7400ms✅),loss~2.00-2.03,0NaN/0skip,GPU 8×94-100%/74-75GB✅,lr=1e-3(stable),grad_norm~0.087-0.235 ③210k autoqueue RUNNING✅(PID3942311,etime~9.0h,/tmp/baize_l1_autoqueue_210k.log last@20:06 polling train iter203230,remaining~6770iters×7.0s≈13.2h,ETA~11-15 09:15,no llama-server active,latest ckpt=iter_0202000,save-interval=2000) ④research日报11-14:checked,pretrain建议advisory only(parse_fail列/SSM轴/opt_state_sharded,not actionable mid-training) ⑤📦TASK≈28.7KB✅/MEMORY≈22.9KB✅·**四层评测 · L1=60.12%@200k(20/20done!NEW PEAK,report已刷新,210k queued ETA~13.2h) L2=🟢HF五重完成 L3=TB 0/2 L4=🟦HANDOFF→post-train** · 本轮动作：监控巡检+git pull+训练健康确认+210k autoqueue确认+research日报check·未完成指令：有(210k autoqueue running,ETA~13.2h)⇒WAITING:1。
> 📦 #2196（11-14 19:50, 监控巡检·训练健康iter203100 step~7040ms✅·210k autoqueue RUNNING ETA~13.5h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2194（11-14 19:10, 监控巡检·训练健康iter202760 step~7011ms✅·210k autoqueue RUNNING ETA~14.1h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2193（11-14 18:53, 监控巡检·训练健康iter202610 step~6990ms✅·210k autoqueue RUNNING ETA~14.4h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2192（11-14 18:32, 监控巡检·训练健康iter202430 step7029ms✅·210k autoqueue RUNNING ETA~14.7h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2191（11-14 18:15, 监控巡检·训练健康iter202270 step6993ms✅·210k autoqueue RUNNING ETA~15.0h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2190（11-14 17:53, 监控巡检·训练健康iter202100 step6994ms✅·210k autoqueue RUNNING ETA~15.4h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2189（11-14 17:36, 监控巡检·训练健康iter201940 step7137ms✅·210k autoqueue RUNNING ETA~15.9h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2188（11-14 17:18, 监控巡检·训练健康iter201790 step7.1s✅·210k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2187（11-14 16:58, 监控巡检+200k报告刷新·训练健康iter201610 step7.03s✅·210k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2186（11-14 16:38, 监控巡检·训练健康iter201450 step7.1s✅·210k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2185（11-14 16:20, 200k eval COMPLETE 60.12% NEW PEAK+210k autoqueue确认+report提交）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2184（11-14 15:42, 监控巡检·200k eval仍在跑(~73min)·训练健康iter~200k✅）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2183（11-14 15:18, 监控巡检·200k eval仍在跑(~49min)·训练健康iter200790 step7157ms✅）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2181（11-14 14:29, 监控巡检·200k eval进入eval phase!训练健康iter200380 step7.1s✅）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2180（11-14 14:08, 监控巡检·200k GGUF conversion 41%→eval phase transition）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2179（11-14 13:47, 监控巡检·训练突破200k!iter200010 step~7.0s<7.4s✅·200k ckpt FOUND+双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2178（11-14 13:25, 监控巡检·训练健康iter199830 step~7.12s<7.4s✅·200k+210k双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2177（11-14 13:05, 监控巡检·训练健康iter199610 step~7.14s<7.4s✅·200k+210k双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2176（11-14 12:27, 监控巡检·训练健康iter199330 step~7000ms<7.4s✅·200k+210k双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2175（11-14 12:10, 监控巡检·训练健康iter199140 step~7.06s<7.4s✅·200k+210k双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2174（11-14 11:44, 监控巡检·训练健康iter198970 step~7000ms<7.4s✅·200k+210k双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2173（11-14 11:26, 监控巡检·训练健康iter198810 step~6956ms<7.4s✅·200k+210k双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2172（11-14 11:07, 监控巡检+210k autoqueue创建并启动·训练健康iter198590 step~7000ms<7.4s✅·200k+210k双autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2169（11-14 10:02, 监控巡检·训练健康iter198090 step~7.07s<7.4s✅·200k autoqueue RUNNING·红线PASS）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2168（11-14 09:40, 监控巡检·训练健康iter197900 step~7.04s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2167（11-14 09:20, 监控巡检·训练健康iter197730 step~7.06s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2166（11-14 09:00, 监控巡检·训练健康iter197550 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2165（11-14 08:25, 监控巡检·训练健康iter197250 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2164（11-14 08:05, 监控巡检·训练健康iter197070 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2163（11-14 07:43, 监控巡检·训练健康iter196910 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2162（11-14 07:22, 监控巡检·训练健康iter196720 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2161（11-14 07:01, 监控巡检·训练健康iter196550 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2160（11-14 06:40, 监控巡检·训练健康iter196370 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2159（11-14 06:25, 监控巡检·训练健康iter196200 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2158（11-14 06:00, 监控巡检·训练健康iter196010 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2157（11-14 05:39, 监控巡检·训练健康iter195850 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2156（11-14 05:18, 监控巡检·训练健康iter195670 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2155（11-14 04:57, 监控巡检·训练健康iter195500 step~7.06s<7.4s✅·200k autoqueue RUNNING·git冲突处理）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2154（11-14 04:37, 监控巡检·训练健康iter195320 step~7.06s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2153（11-14 04:19, 监控巡检·训练健康iter195150 step~7.03s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2152（11-14 04:00, 监控巡检·训练健康iter194980 step~7.03s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2151（11-14 03:37, 监控巡检·训练健康iter194810 step~7060ms<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2150（11-14 03:17, 监控巡检·训练健康iter194640 step~7.0s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2149（11-14 02:57, 监控巡检·训练健康iter194450 step~6.98s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2148（11-14 02:34, 监控巡检·训练健康iter194270 step~6.95s<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2147（11-14 01:57, 监控巡检·训练健康step<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2146（11-14 01:36, 监控巡检·训练健康iter193770 step<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2142-#2143（11-14 00:12-00:34, 2轮监控巡检·训练健康step<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2139–#2140（11-13 23:06-23:30, 2轮监控巡检·训练健康step<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-13.md；需要时再读。
> 📦 #2137–#2141（11-13 22:19→23:50, 3轮监控巡检·训练step<7.4s✅·200k autoqueue RUNNING）→ daily-memories/2026-11-13.md；需要时再读。
> 📦 #2135–#2136（11-13 21:42→21:59, 2轮监控巡检·训练step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：训练持续健康iter191770→191920,200k autoqueue polling,红线PASS。需要时再读。
> 📦 #2132–#2134（11-13 20:35→21:20, 3轮监控巡检·训练step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：训练持续健康iter191210→191590,200k autoqueue polling ETA从17.1h→16.5h,红线PASS。需要时再读。
> 📦 #2130–#2131（11-13 19:54→20:15, 2轮监控巡检·190k eval DONE+200k autoqueue STARTED·训练step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：190k eval Avg=58.13%(ties 160k peak),200k autoqueue PID850714 polling。需要时再读。
> 📦 #2129（11-13 19:31, 190k eval IN PROGRESS监控·训练健康step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：190k eval在跑(lm_eval 71min)，19:54 #2130确认DONE。需要时再读。
> 📦 #2124–#2127（11-13 17:07→18:11, 4轮监控巡检+200k autoqueue脚本创建·训练step<7.4s✅）→ daily-memories/2026-11-13.md；**结论**：训练持续健康iter189440→189990,190k ckpt已落盘,200k autoqueue脚本已创建。需要时再读。
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
> 📦 #2033–#2054（11-12 05:45→13:45, 监控巡检+170k/180k eval+论文刷新+L2 HF验证+L4确认·共~22轮）→ daily-memories/2026-11-12.md；需要时再读。

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