# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1（✅ 2026-11-12 用户令「L1/L2评测脚本入库+L4移交post-train」已完成·**L1 21/21done(10k-210k,**PEAK 200k=60.12%**·210k=58.50%)·220k autoqueue RUNNING✅(PID203680 on .29,waiting for iter_0220000 ckpt,train@~213.0k ETA~13.6h)**·**L2 🟢HF五重验证全部完成:HumanEval=15.0%+GSM8K=10.0%+MBPP=5.0%+BBH=3.3%+MATH=0.0%·MMLU=23.16%**·**L3 📜pipeline脚本已创建(baize_l3_terminalbench_vllm.sh·vLLM+Harbor+Cline adapter·ready for GPU window)·blocked:.17 SSH timeout+.29/.12 GPU 100%满**·**L4 HANDOFF→post-train（2026-11-12用户令·只读引用）**·**论文§4.6已刷新iter190k+PDF已重编译✅·红线PASS·已提交**·训练健康iter≈213.0k/700k(30.4%) GPU 8×100%/75GB✅）
> 2026-11-15 15:07 #2245: **监控巡检·训练健康iter213010/700k(30.4%) GPU 8×100%/75GB✅**·**动作**：①git pull→already up to date✅ ②训练健康(.29 PID146283 pretrain_launcher.py alive,iter213010/700k,step~7.0s<7.4s✅,loss~2.00,0NaN/0skip,lr=1e-3,GPU 8×100%/~75GB) ③latest ckpt=iter_0212000(212000,no change) ④220k autoqueue RUNNING✅(PID203680 on .29,autoqueue_220k.sh,waiting for iter_0220000,train@213010 ETA~13.6h~Nov16 04:40) ⑤research daily 11-15已查(pretrain建议=「扩窗后短任务回退判据」,非当前可执行项,context window expansion未开始) ⑥L1 trend:10k51.50%→100k57.75%→200k60.12%(peak)→210k58.50%(plateau,limit=100 stderr±4.5%) ⑦📦TASK29.3KB✅/MEMORY~18.2KB✅·**四层评测 · L1=60.12%@200k(21done,220k queue) L2=🟢HF五重done L3=📜pipeline ready(blocked GPU) L4=🟦HANDOFF** · 本轮动作：例行监控commit·未完成指令：有(220k autoqueue waiting)⇒WAITING:1。
> 📦 #2244（11-15 14:47, 监控巡检·训练健康iter212840 GPU 8×95-100%/75GB✅·220k autoqueue RUNNING）→ daily-memories/2026-11-15.md；需要时再读。
> 2026-11-15 14:47 #2244: **监控巡检·训练健康iter212840/700k(30.4%) GPU 8×95-100%/75GB✅**·**动作**：①git pull→already up to date✅ ②训练健康(.29 PID146283 pretrain_launcher.py alive,iter212840/700k,step~7.0s<7.4s✅,loss~2.00,0NaN/0skip,lr=1e-3,GPU 8×95-100%/~75GB) ③latest ckpt=iter_0212000(212000,no change) ④220k autoqueue RUNNING✅(PID203680 on .29,autoqueue_220k.sh,waiting for iter_0220000,train@212840 ETA~13.9h~Nov16 04:40) ⑤research daily 11-15已查(12:12更新,#2240已review,无新可执行项) ⑥ops inbox empty ⑦L1 trend:10k51.50%→100k57.75%→200k60.12%(peak)→210k58.50%(plateau,limit=100 stderr±4.5%) ⑧📦TASK29.3KB✅/MEMORY~18.5KB✅·**四层评测 · L1=60.12%@200k(21done,220k queue) L2=🟢HF五重done L3=📜pipeline ready(blocked GPU) L4=🟦HANDOFF** · 本轮动作：例行监控commit·未完成指令：有(220k autoqueue waiting)⇒WAITING:1。
> 📦 #2243（11-15 14:10, 监控巡检+L3 Terminal-Bench pipeline脚本创建·训练健康iter212520 GPU 8×95-100%/75GB✅·220k autoqueue RUNNING）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2242（11-15 13:48, 监控巡检·训练健康iter212330 GPU 8×95-100%/75GB✅·220k autoqueue RUNNING）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2241（11-15 13:26, 监控巡检·训练健康iter212150 GPU 8×96-100%/75GB✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2240（11-15 13:08, 监控巡检+scaling report run/reports同步·训练健康 GPU 8×95-100%/75GB✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2239（11-15 12:25, 监控巡检+scaling report刷新(补210k)·训练健康iter211620 GPU 8×95-100%/75GB✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2238（11-15 12:05, 监控巡检+220k autoqueue重启·训练健康latest_ckpt=210000(@09:15)·step<7.4s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2236（11-15 11:17, 监控巡检·训练健康iter211040 step6915-7084ms<7.4s✅·220k autoqueue RUNNING ETA~17h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2235（11-15 10:55, 监控巡检+210k eval COMPLETE+scaling report生成器bug修复+四层报告刷新·训练健康iter210820 step<7.4s✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2234（11-15 10:15, 监控巡检+210k eval确认RUNNING+220k autoqueue LAUNCH·训练健康iter210500 step6900-7052ms✅）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2232（11-15 08:00, 监控巡检·训练健康iter209330 step~7.5s✅·210k autoqueue RUNNING ETA~1.4h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2231（11-15 07:40, 监控巡检·训练健康iter209150 step6930ms✅·210k autoqueue RUNNING ETA~1.7h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2229（11-15 07:00, 监控巡检·训练健康iter208820 step6993ms✅·210k autoqueue RUNNING ETA~2.3h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2228（11-15 06:42, 监控巡检·训练健康iter208660 step6994ms✅·210k autoqueue RUNNING ETA~2.6h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2227（11-15 06:25, 监控巡检·训练健康iter208490 step6994ms✅·210k autoqueue RUNNING ETA~2.9h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2226（11-15 06:05, 监控巡检·训练健康iter208310 step6950ms✅·210k autoqueue RUNNING ETA~3.3h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2225（11-15 05:40, 监控巡检·训练健康iter208150 step6929ms✅·210k autoqueue RUNNING ETA~3.6h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2210–#2224（11-15 00:13→05:20, 15轮监控巡检·训练step<7.4s✅·210k autoqueue RUNNING ETA~4-9h）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2209（11-14 23:54, 监控巡检·训练健康iter205180 step~7.0s✅·210k autoqueue RUNNING ETA~9.4h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2208（11-14 23:36, 监控巡检·训练健康iter205030 step~7.0s✅·210k autoqueue RUNNING ETA~9.7h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2207（11-14 23:15, 监控巡检·训练健康iter204850 step~7.0s✅·210k autoqueue RUNNING ETA~10.2h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2206（11-14 22:58, 监控巡检·训练健康iter204700 step~7.0s✅·210k autoqueue RUNNING ETA~10.3h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2205（11-14 22:40, 监控巡检·训练健康iter204540 step~7.0s✅·210k autoqueue RUNNING ETA~10.7h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2204（11-14 22:19, 监控巡检·训练健康iter204370 step~7.0s✅·210k autoqueue RUNNING ETA~10.9h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2203（11-14 22:06, 监控巡检·训练健康iter204210 step7.02s✅·210k autoqueue RUNNING ETA~11.3h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2202（11-14 21:42, 监控巡检·训练健康iter204050 step~6967ms✅·210k autoqueue RUNNING ETA~11.6h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2201（11-14 21:24, 监控巡检·训练健康iter203900 step~7020ms✅·210k autoqueue RUNNING ETA~11.9h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2200（11-14 21:06, 监控巡检·训练健康iter203740 step~7010ms✅·210k autoqueue RUNNING ETA~12.2h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2199（11-14 20:47, 监控巡检·训练健康iter203580 step~7010ms✅·210k autoqueue RUNNING ETA~12.5h）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2185–#2198（11-14 16:20→20:29, 10轮监控巡检·训练step<7.4s✅·200k eval COMPLETE 60.12% NEW PEAK(#2185)+210k autoqueue确认）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2172–#2184（11-14 11:07→15:42, 12轮监控巡检·训练step<7.4s✅·200k ckpt FOUND(#2179)+200k eval进入GGUF→eval phase(#2180-#2184)+210k autoqueue创建启动(#2172)）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2146–#2169（11-14 01:36→10:02, ~17轮监控巡检·训练step<7.4s✅·200k autoqueue polling iter193770→198090·红线PASS）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2110–#2143（11-13 12:02→11-14 00:34, ~18轮监控巡检·训练step<7.4s✅·190k eval=58.13%(#2130)+200k autoqueue创建启动(#2124-#2127)+L1 18/20done·红线PASS）→ daily-memories/2026-11-13.md + 2026-11-14.md；需要时再读。
> 📦 #2064–#2109（11-12 18:35→11-13 11:40, ~23轮监控巡检·训练step<7.4s✅·iter178030→186650·L1 18/20done(180k=57.25%)·L4 HANDOFF→post-train·L1/L2脚本入库确认✅）→ daily-memories/2026-11-12.md + 2026-11-13.md；需要时再读。
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