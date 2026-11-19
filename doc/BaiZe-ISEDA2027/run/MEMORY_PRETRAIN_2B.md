# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0（✅ **2026-11-19 22:43 #2689 监控巡检·训练健康step~7.13s✅·GPU 93-100%·latest ckpt=260k·260k eval IN PROGRESS(~14min,llama-server PID102521+lm_eval PID115402,Phase5/6,autoqueue PID20989)·270k/280k/290k/300k autoqueue polling·L1=25/25(10k-250k done)·260k eval pending→autoqueue自完成+自刷新report·load=44.14✅·0NaN/0skip·ops inbox RUN_ID281(只读)·research日报11-19 future-planning无紧急·MEMORY≈13KB✅/TASK≈21KB✅·git已同步**）
> 2026-11-19 22:43 #2689: 监控巡检。260k eval仍进行中(~14min,Phase5/6)。训练健康: step~7.13s, GPU 93-100%全8卡(74-75GB/81GB), latest ckpt=260k, 0NaN/0skip。lm_eval PID115402(State=S/sleeping, RSS 981MB, 16 threads, 5.9% CPU)等待llama-server PID102521(265% CPU, -t4)响应。autoqueue PID20989(810s)将自动在eval完成后执行Phase6(报告刷新→report_pretrain_llamacpp_scaling_zh.html)。270k/280k/290k/300k autoqueue均存活polling。250k results: raw AVG=55.87%。ops inbox=RUN_ID281(只读,非pretrain指令)。research日报11-19 pretrain建议均future-planning(long-context验收三列/serving预算/noise ablation/QK-Norm,均decay/post-train阶段)。git pull --rebase(仅ZhuLong改动)。MEMORY≈13KB✅/TASK≈21KB✅。·未完成指令：有(万整数ckpt评测持续跟进,260k eval进行中+270k-300k排队)·WAITING=0。
> 📦 #2688（11-19 22:33, 唤醒巡检+260k autoqueue抢救·260k autoqueue原PID3163084死于NFS Stale file handle→重启PID20989→Phase1-4完成→Phase5 eval进行中·训练健康step=7.13s✅·latest ckpt=260k·250k results verified raw AVG=55.87%·270k-300k autoqueue polling）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2687（11-19 22:13, 监控巡检·训练健康step~7.05s✅·latest ckpt=258k·iter=259948/700k·260k ETA~22:19·260k/270k/280k/290k/300k autoqueue串行排队·L1=25/25·load=44.84✅·ops inbox RUN_ID281(只读)·research日报11-19 future-planning·吞吐闭环~56h·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2686+#2685+#2684（11-19 21:51–22:06, 3轮监控巡检·训练健康GPU 94-100%✅·step avg~7.1s·latest ckpt=258k·iter=259720-259860·260k ETA~22:22-22:23·autoqueue 260k-300k串行排队·L1=25/25·250k results.json verified✅·.29/.12 load正常✅·ops inbox RUN_ID281(只读)·research日报11-19 future-planning·吞吐闭环~56h·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2683–#2630（11-19 13:10–21:43, ~40轮监控巡检·训练健康GPU 83-100%✅·step avg 6.95-7.48s·latest ckpt 254k→256k→258k·iter 255380→259650·260k/270k/280k/290k/300k autoqueue串行排队(逐个创建启动)·L1=25/25(250k eval COMPLETE)·.29/.12 load正常✅·ops inbox RUN_ID281(只读)·research日报11-19 future-planning·论文改进第二轮归档(commit 53985409e)·吞吐闭环34→56h·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2629–#2624（11-19 13:16–13:53, 6轮监控巡检·训练健康step 6.95-7.22s✅·iter=255380-255720·latest ckpt=254k·256k ETA~14:25·260k autoqueue polling·吞吐闭环31.5-34.3h·L1=25/30·.12 load正常✅·ops inbox=RUN_ID281·git已同步）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2513–#2623（11-19 00:08–13:10, ~70轮监控巡检·训练健康step 6.92-7.14s✅·iter 248670→256200·latest ckpt 250k→254k·250k eval COMPLETE 57.50%·260k autoqueue polling·吞吐闭环8.6→31h·L1=25/30·论文改进两轮commit·.12 load正常✅）→ daily-memories/2026-11-19.md；需要时再读。
> 📦 #2434–#2512（11-18 14:50–11-19 00:03, ~80轮监控巡检·吞吐诊断闭环(CPU争抢根因+NVLS禁用,13.2s→6.93s恢复)+246k/248k/250k ckpt保存+250k autoqueue+S1/S2报告commit）→ daily-memories/2026-11-18.md + 2026-11-19.md；需要时再读。
> 📦 #2330–#2433（11-17 04:36–11-18 14:42, ~100轮监控巡检·训练健康step<7.4s✅·240k autoqueue·吞吐事件发现+诊断+首次重启·iter231090-244770）→ daily-memories/2026-11-17.md + 2026-11-18.md；需要时再读。
> 📦 #2033–#2329（11-12 05:45–11-17 04:31, ~300轮监控巡检+评测·170k-230k eval+L2 HF五重验证+L4 HANDOFF→post-train+论文刷新+L1/L2脚本入库·训练step<7.4s✅·iter175710-231580）→ daily-memories/2026-11-{12..17}.md；需要时再读。

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

**L4 已移交 post-train（2026-11-12 用户令）**：L4（zhulong 消融评测 + designflow/EDA-Flow-Bench）不再由 pretrain 负责。post-train 隧道已 4 次复验 OK、run_code 端到端 PASS。Pretrain 从本轮起 L4 统一写「HANDOFF→post-train」，不再做 L4 资源调查/SSH .15/.17 直连。四层口径：L1/L2/L3 由 pretrain 负责；L4 只读引用（post-train 出数后引用）。

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