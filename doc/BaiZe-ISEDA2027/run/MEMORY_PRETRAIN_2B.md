# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0(✅ **2026-11-22 15:35 #2998 放行autoqueue令·监控巡检·284k eval RUNNING(~56min,lm_eval PID922915,llama-server PID910819,since14:39,results.json未落盘,270k耗时80min→ETA~16:00,daemon将auto-refresh报告)·训练健康iter=284480/700000(40.64%) step DURING eval(n=15:7354.8/7123.8/7127.8/7312.8/7158.6/7196.1/7389.0/7400.7/7176.9/7188.7/7300.2/7140.5/7373.2/7157.1/7182.1ms avg7239ms,1 transient>7.4s非持续✅) loss≈1.98-2.00 grad_norm0.088-0.108 0NaN/0skip✅ lr=1e-3 stable·step time对比:eval前avg7273ms→eval中avg7239ms Δ≈-34ms(NOT elevated,无CPU争抢✅)·load.29=28.22/28.52/29.61·.12=25.22/25.19/25.12✅(ssh实测,无MegaMath争抢,11-18事故未复发)·backlog:270k-282k全清(7ckpt harness Avg:270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62%),284k eval RUNNING·daemon活跃(PID1081392,~70650s≈19.6h)·286k未落盘(ETA~18:36,iter=284480,1520steps×7.2s≈182min)·L1报告33ckpt含282k(284k待eval完daemon自动刷新)·evidence:ckpt=.../checkpoints/iter_0284000/GGUF=.../bz2b-284000-f16.gguf(4.2G)/autoqueue=/tmp/baize_l1_autoqueue_continuous.log/worker=/tmp/baize_s1_baize2b_worker.log/复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯eval/监控未碰train.sh/configs/.bak/训练进程(铁律遵守)·体积MEMORY≈12.4KB<32KB✅ TASK≈25.3KB<32KB✅·research日报11-22无本线可执行项**)
> 📦 #2997（11-22 15:29, 放行autoqueue令·监控巡检·284k eval RUNNING(~50min,lm_eval PID922915,ETA~16:00)·训练健康iter=284430 step DURING eval(n=10:avg7251ms,2 transient>7.4s非持续✅) 0NaN/0skip·step time eval前7273→eval中7251 Δ-22ms(NOT elevated✅)·load.29=28.79/.12=25.97✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2996（11-22 15:23, 放行autoqueue令·监控巡检·284k eval RUNNING(~44min,lm_eval PID922915,llama-server PID910819,step[5/6]since14:39,results.json未落盘,270k耗时80min→ETA~16:00,daemon将auto-refresh报告)·训练健康iter=284380/700000(40.63%) step DURING eval(n=5:7354.8/7123.8/7127.8/7312.8/7158.6ms avg7215.6ms,全<7.4s✅) loss≈1.984-2.000 grad_norm0.087-0.098 0NaN/0skip✅ lr=1e-3 stable·step time对比:eval前avg7273.3ms→eval中avg7215.6ms Δ≈-58ms(NOT elevated✅)·load.29=31.89/31.26/30.99·.12=24.17/24.76/25.01✅·backlog:270k-282k全清,284k eval RUNNING·daemon活跃(PID1081392,~69924s≈19.4h)·286k未落盘(ETA~18:30)·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2995（11-22 15:15, 放行autoqueue令·监控巡检·284k eval RUNNING(36min,lm_eval PID922915,ETA~15:59)·训练健康iter=284310 step DURING eval(n=25:avg7286.5ms,4 transient>7.4s后回落✅) 0NaN/0skip·step time eval前7273→eval中7287 Δ+13ms(NOT elevated✅)·load.29=33.63/.12=23.98✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2994（11-22 15:08, 放行autoqueue令·监控巡检·284k eval RUNNING(lm_eval PID922915 ~30min,results.json未落盘,ETA~16:00)·训练健康iter=284260 step DURING eval(n=8:avg≈7311ms,2 transient>7.4s✅) 0NaN/0skip·step time eval前7253→eval中7311 Δ≈+58ms(NOT elevated✅)·load.29=29.02/.12=25.40✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2993（11-22 15:02, 放行autoqueue令·监控巡检·284k eval RUNNING(llama-server PID910819 ~23min,eval Phase5/6 since14:39,270k耗时80min→ETA~16:00)·训练健康iter=284210 step DURING eval(n=3:7268.6/7241.3/7205.1ms,全<7.4s✅) loss≈1.99 0NaN/0skip·step time eval前7253→eval中7238 Δ-15ms(NOT elevated✅)·load.29=32.23/.12=23.62✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2992（11-22 14:52, 放行autoqueue令·监控巡检·284k eval RUNNING(lm_eval PID922915 ~13min,ETA~15:50)·训练健康iter=284120 step avg7250ms DURING eval(全<7.4s✅) 0NaN/0skip·step time eval前7253→eval中7250 Δ-3ms(NOT elevated✅)·load.29=26.59/.12=27.13✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2991（11-22 14:42, 放行autoqueue令·监控巡检·daemon自动评284k(eval_running,lm_eval RUNNING step5/6,ETA~15:50)·训练健康iter=284040 step avg7222ms DURING eval(全<7.4s✅) 0NaN/0skip·step time eval前7265→eval中7222 Δ-43ms(NOT elevated✅)·load.29=28.07/.12=26.04✅·backlog:270k-282k全清,284k eval RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2990（11-22 14:36, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:37)·训练健康iter=283990 step avg7265ms 0NaN/0skip·step time NO eval load avg7265ms·load.29=28.92/.12=26.29✅·backlog全清(270k-282k 7ckpt)·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2989（11-22 14:22, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:37)·训练健庹iter=283870 step avg7253ms 0NaN/0skip·step time NO eval load avg7253ms·load.29=25.70/.12=25.54✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2988（11-22 14:16, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:36)·训练健庹iter=283830 step avg7296ms 0NaN/0skip·step time NO eval load avg7296ms·load.29=26.09/.12=27.05✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2987（11-22 14:09, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:37)·训练健康iter=283770 step avg7294ms 0NaN/0skip·step time NO eval load avg7294ms·load.29=26.92/.12=24.67✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2986（11-22 14:05, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:38)·训练健康iter=283730 step avg7296ms 0NaN/0skip·step time NO eval load avg7296ms·load.29=30.52/.12=26.92✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2985（11-22 13:57, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:37)·训练健康iter=283670 step avg7262ms 0NaN/0skip·step time NO eval load avg7262ms·load.29=24.92/.12=25.97✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2984（11-22 13:50, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:36)·训练健康iter=283620 step avg7250ms 0NaN/0skip·step time NO eval load avg7250ms·load.29=28.24/.12=25.73✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2983（11-22 13:43, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:36)·训练健康iter=283560 step avg7213ms 0NaN/0skip·step time NO eval load avg7213ms·load.29=27.57/.12=29.10✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2982（11-22 13:36, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:35)·训练健康iter=283500 step avg7189ms 0NaN/0skip·step time NO eval load avg7189ms·load.29=25.70/.12=25.43✅·backlog全清·L1报告33ckpt✅·🧹清理30个stale GGUF(125GB)）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2981（11-22 13:27, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=283420 step avg7230ms 0NaN/0skip·step time NO eval load avg7230ms·load.29=26.81/.12=26.93✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2980（11-22 13:21, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=283370 step avg7254ms 0NaN/0skip·step time NO eval load avg7254ms·load.29=30.24/.12=27.17✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2978（11-22 13:03, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=283230 step avg7228ms 0NaN/0skip·step time NO eval load avg7228ms·load.29=26.30/.12=26.91✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2977（11-22 12:57, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=283170 step avg7.254s 0NaN/0skip·step time NO eval load avg7.254s·load.29=30.92/.12=24.57✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2976（11-22 12:51, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=283120 step avg7.28s 0NaN/0skip·step time NO eval load avg7.28s·load.29=27.68/.12=25.60✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2975及更早（已归档，含 #2970-#2975 监控轮 + #2968-#2969 监控轮 + #2900–#2967 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

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
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448�