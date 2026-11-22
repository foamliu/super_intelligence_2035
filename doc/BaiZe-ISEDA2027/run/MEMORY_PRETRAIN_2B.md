# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0(✅ **2026-11-22 14:52 #2992 放行autoqueue令·监控巡检·284k eval RUNNING(lm_eval PID922915 ~13min,ETA~15:50,daemon将auto-refresh报告)·训练健康iter=284120/700000(40.59%) step avg7250ms DURING eval(n=11:7281/7106/7171/7214/7341/7299/7300/7271/7221/7225/7316ms,全<7.4s✅) loss≈1.99(last:1.981303) grad_norm0.088 0NaN/0skip✅·step time对比:eval前avg7253ms(14:18-14:38 n=13)→eval中avg7250ms(14:39-14:51 n=11) Δ≈-3ms(NOT elevated,无CPU争抢✅)·load.29=26.59/28.88/28.31·.12=27.13/25.96/25.62✅(ssh实测)·backlog:270k-282k全清(7ckpt harness Avg:270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62%),284k eval RUNNING·daemon活跃(PID1081392,~68054s≈18.9h,auto-detected 284k 14:38)·286k未落盘(ETA~18:40,iter=284120,1880steps×7.3s≈229min)·L1报告32KB 33ckpt含282k(284k待eval完自动刷新)·evidence:ckpt=.../checkpoints/iter_0284000/GGUF=.../bz2b-284000-f16.gguf(4.2G)/autoqueue=/tmp/baize_l1_autoqueue_continuous.log/worker=/tmp/baize_s1_baize2b_worker.log/复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯eval/监控未碰train.sh/configs/.bak/训练进程(铁律遵守)·体积MEMORY≈11.4KB<32KB✅ TASK≈25.3KB<32KB✅·research日报11-22无本线可执行项**)
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
> 📦 #2975（11-22 12:41, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=283052 step avg7.24s 0NaN/0skip·step time NO eval load avg7.24s·load.29=30.16/.12=23.56✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2974（11-22 12:30, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=282950/700000(40.42%) step avg7.24s loss≈1.99 0NaN/0skip·step time NO eval load avg7.24s·load.29=28.57/.12=25.47✅·backlog全清·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2973（11-22 12:22, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=282890/700000(40.41%) step avg7.27s 0NaN/0skip·step time NO eval load avg7.27s·load.29=31.31/.12=26.84✅·backlog全清·L1报告33/35ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2972（11-22 12:16, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k)·训练健康iter=282830 step avg7.27s(n=15,全<7.4s✅) loss≈2.00 0NaN/0skip·step time NO eval load avg7.27s(Δ≈0)·load.29=30.53/.12=27.02✅·backlog全清·L1报告33/35ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2971（11-22 12:05, 放行autoqueue令·监控巡检·282k L1 DONE harness Avg=58.62%(raw56.25%)·训练iter=282730 step avg7247ms(全<7.4s✅) 0NaN/0skip·DURING eval avg7247ms(Δ≈+0.08s,NOT persistent>7.4s✅)·load.29=32.88/.12=26.64✅·backlog全清·L1报告33/35ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2970（11-22 11:52, 放行autoqueue令·监控巡检·训练健康iter=282640 step avg7342ms(2 transient>7.4s后回落<7.4s✅) 0NaN/0skip·282k eval RUNNING(73min,ETA~12:00)·DURING eval avg7342ms(Δ≈+0.1s,NOT persistent>7.4s✅)·load.29=32.18/.12=24.71✅·backlog全清·L1报告32/34ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2969及更早（已归档，含 #2968-#2969 监控轮 + #2900–#2967 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

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