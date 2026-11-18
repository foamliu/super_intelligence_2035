# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0（✅ **2026-11-18 23:36 #2507 监控巡检**：训练健康step mean~6.98s(6.93-7.11s,last40)/1020-1047TFLOP iter~248370/700000·latest_ckpt=248000·250k autoqueue运行中(PID 651752,~7.4h)·吞吐闭环无复发~25h+·11-18全部用户令已完成·250k ETA~3.1h(~02:40 11-19)**）
> 2026-11-18 23:36 #2507: 监控巡检。①**训练健康**：master日志434 step-time lines,last5 mean~6.99s(6.94-7.09s)/1023-1044TFLOP,lr=1e-3,NVLS=0(NCCL_NVLS_ENABLE=0)。②**迭代进度**：iter~248340/700000(434 lines×10≈4340步自244000),latest_ckpt=248000(next 250k ETA~3.2h≈02:42 11-19)。③**250k autoqueue**：PID 651752运行中(elapsed~26158s≈7.3h),polling for iter_0250000,24h timeout剩余~16.7h。④**吞吐事件闭环**：无复发~25h+,根因确证=data线pc2_fast.py CPU争抢+NVLS绑定失败(已修复:NCCL_NVLS_ENABLE=0+data线清理CPU)。⑤**机器健康**：.29 GPU 8卡96-100%util/~75GB/682-694W/56-63°C✅;.12 GPU 8卡98-100%util/~75GB/684-698W/55-63°C✅;pretrain loop PID 1221991运行中✅;无eval/llama-server进程。⑥**eval状态**：L1 8-set 10k-240k全完成(24 sets),250k autoqueue运行中。⑦**11-18用户令全部完成**：10:5x排查✅/11:1x授权✅/13:1x重启✅(NCCL_NVLS_ENABLE=0)/14:2x接管监控✅/S1/S2报告✅(36.7KB,commit c21a716ce)。⑧**MEMORY体积**：~17KB(✅≤32KB)。·**四层评测 · L1=57.88%@240k L2=🟢@200k L3=📜 L4=🟦HANDOFF** · 未完成指令：有(万整数ckpt评测持续跟进,250k autoqueue运行中)·WAITING: 0。
> 📦 #2503–#2505（11-18 23:13–23:24 监控巡检 — 训练健康step~6.95-7.11s/1020-1047TFLOP iter~248180-248270, 250k autoqueue运行中(7.1-7.2h), 吞吐闭环无复发~24.5h, 11-18全部用户令已完成）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2494–#2502（11-18 22:22–23:07 监控巡检 — 训练健康step~6.93-7.11s/1020-1047TFLOP iter~247760-248140, 248k ckpt已保存, 250k autoqueue运行中(6.2-7h), 吞吐闭环无复发~24h, 11-18全部用户令已完成）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2445–#2493（11-18 16:31–22:13, ~50轮监控巡检 — 训练健康step~6.9-7.1s/1020-1047TFLOP iter~244770-247680, 246k/248k ckpt已保存, 250k autoqueue运行中, 吞吐事件闭环无复发, S1/S2报告已commit, 11-18全部用户令已完成）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2434–#2444（11-18 14:50–16:23 吞吞吐诊断+恢复+事件闭环 — CPU争抢(根因,data线pc2_fast.py)+NVLS禁用, 13.2s→6.93s恢复, TFLOP 548→1046, 250k autoqueue启动, S1/S2报告commit）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2433（11-18 14:42 吞吐诊断·**结论有误**(data线CPU未释放被误判为已释放;.29 GPU power 125W实为.12数据)·已由#2434纠正）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2432（11-18 14:30 监控巡检·二次重启后首次·step~13s·data线ETA~4h）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2431（11-18 14:0x 二次重启resume(NVLS禁用)·step~13s·双因叠加根因·S1/S2报告✅）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2430（11-18 13:5x 首次重启resume·NVLS available·step~11.5s·同样data线CPU争抢根因）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2429（11-18 12:30 吞吐降级根因定位·NVLS绑定失败CUDA error 802·已通过重启修复）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2429（11-18 12:30 吞吐降级根因定位·NVLS绑定失败CUDA error 802·已通过重启修复）→ daily-memories/2026-11-18.md；需要时再读。
> 📦 #2417–#2428（11-17 08:55–10:05, 12轮例行监控·训练健康iter234340–234943 step≈7.0s✅·240k autoqueue polling·all healthy）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2391–#2416（11-17 04:45–08:48, ~25轮例行监控·训练健康iter232200–234280 step<7.2s✅·240k autoqueue polling·all healthy）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2392（11-17 06:36, 例行监控·训练健康iter233160 step~7041ms✅·240k autoqueue polling ETA~13.3h·all healthy）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2391–#2372（11-17 04:45–06:30, ~20轮例行监控·训练健康iter232200→233110 step<7.5s✅·240k autoqueue polling·all healthy）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2371（11-17 04:36, 例行监控+MEMORY归档瘦身·训练健康iter232130 step~6936ms✅·240k autoqueue polling ETA~15.3h·MEMORY 30.7→24.4KB）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2360（11-17 03:33, 例行监控+四层报告刷新·训练健康iter231580 step7044ms✅·240k autoqueue polling·report_pretrain_eval_4tier_zh.html刷新(补L1 180k-230k+L2 200k MMLU)）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2357–#2370, #2359（11-17 03:19–04:31, 14轮例行监控·训练健康iter231460–232080 step<7.4s✅·240k autoqueue polling·all healthy）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2356（11-17 03:11, 例行监控·训练健康iter231410 step7143ms✅·240k autoqueue polling ETA~16.9h·research日报11-17已查·MEMORY归档瘦身）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2355（11-17 03:06, 例行监控·训练健康iter231350 step7001ms✅·240k autoqueue polling ETA~16.8h·research日报11-17已查）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2354（11-17 02:59, 例行监控·训练健康iter231310 step7060ms✅·240k autoqueue polling ETA~17h·research日报11-17已查）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2353（11-17 02:55, 例行监控·训练健康iter231270 step7128ms✅·240k autoqueue polling ETA~17h·research日报11-17已查）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2351（11-17 02:48, 例行监控·训练健康iter231160 step~7.2s✅·240k autoqueue polling ETA~17h·research日报11-17已查）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2350（11-17 02:40, 例行监控·训练健康iter231140 step7096ms✅·240k autoqueue polling ETA~17.5h·research日报11-17已查）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2349（11-17 02:33, 例行监控·训练健康iter231090 step7040ms✅·240k autoqueue polling ETA~17.3h·research日报11-17已查）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2343–#2348（11-17 02:06–02:28, 6轮例行监控·训练健康iter230860-231050·240k autoqueue polling）→ daily-memories/2026-11-17.md；需要时再读。
> 📦 #2270–#2342（11-16 00:29–23:14, ~70轮例行监控·220k eval COMPLETE+报告刷新+230k eval COMPLETE→240k autoqueue STARTED·训练step<7.4s✅·iter221050-229400）→ daily-memories/2026-11-16.md；需要时再读。
> 📦 #2210–#2269（11-15 00:13→23:53, ~50轮例行监控·220k eval+230k eval COMPLETE+240k autoqueue STARTED+L2@200k五重完成+MMLU@200k+210k eval+L3 TB脚本创建·训练step<7.4s✅·iter208150-216650）→ daily-memories/2026-11-15.md；需要时再读。
> 📦 #2146–#2209（11-14 01:36→23:54, ~30轮例行监控·200k eval COMPLETE 60.12% NEW PEAK+210k autoqueue STARTED·训练step<7.4s✅·iter203580-205180）→ daily-memories/2026-11-14.md；需要时再读。
> 📦 #2064–#2145（11-13 12:02→11-14 00:34, ~18轮例行监控·190k eval=58.13%+200k autoqueue STARTED+L1 18/20done·训练step<7.4s✅·iter178030-204050）→ daily-memories/2026-11-13.md + 2026-11-14.md；需要时再读。
> 📦 #2033–#2063（11-12 05:45→18:10, ~25轮例行监控+评测·170k/180k eval+论文刷新+L2 HF五重验证(HumanEval15%+GSM8K10%)+L4 HANDOFF→post-train+L1/L2脚本入库确认·训练step<7.4s✅·iter175710-177810）→ daily-memories/2026-11-12.md；需要时再读。
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