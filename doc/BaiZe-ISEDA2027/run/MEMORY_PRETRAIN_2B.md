# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0(✅ **2026-11-22 18:53 #3021 放行autoqueue令·监控巡检·286k eval RUNNING(daemon自动检测,GGUF done18:42:49,llama-server PID2142829 -t4/nice19 + lm_eval PID2153755 step5/6,ETA~20:02)·训练健康iter=286090/700000(40.87%) step avg7249ms(n=15,1 transient8244ms>7.4s非持续✅) loss≈1.99 grad_norm0.09-0.14 0NaN/0skip✅ lr=1e-3 stable·step time DURING eval:7180.3/7214.2/7258.5/7129.3/7015.4/6977.2/7103.1 avg7125ms Δ-140ms vs pre-eval7265ms(NOT elevated✅)·load.29=29.60/29.32/28.07·.12=26.46/26.04/25.66✅(无CPU争抢,11-18事故未复发)·daemon活跃(PID1081392,eval_running=286k)·L1报告34ckpt(284k为最新,32505B,refreshed16:05,286k完成后将自动刷新)·backlog全清(270k-284k 9ckpt已评:260k59.00/270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62/284k58.25%)+286k RUNNING·evidence:ckpt=.../checkpoints/iter_0286000(最新)·eval=gguf_iter_286000_fixed_8set(running,results.json待出)/report=.../reports/report_pretrain_llamacpp_scaling_zh.html(32505B,16:05)/daemon=/tmp/baize_l1_autoqueue_continuous.log(PID1081392)/worker=/tmp/baize_s1_baize2b_worker.log/复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程(铁律遵守)·体积MEMORY≈14.2KB<32KB✅ TASK≈25.3KB<32KB✅)
> 📦 #3020（11-22 18:45, 放行autoqueue令·监控巡检·286k eval RUNNING(daemon自动检测,step5/6)·训练健康iter=286040 step avg7309ms(n=15,2 transient>7.4s非持续✅) 0NaN/0skip·step time DURING eval avg7218ms NOT elevated✅·load.29=30.97/.12=26.78✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3019（11-22 18:40, 放行autoqueue令·监控巡检·286k刚落盘(18:39:36)daemon将自动检测·训练健康iter=286000 step avg7264.9ms(n=13全<7.4s✅) 0NaN/0skip·load.29=28.40/.12=23.52✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3018（11-22 18:30, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:40)·训练健康iter=285920 step avg7277ms(n=15,1 transient7429ms>7.4s非持续✅) 0NaN/0skip·load.29=26.92/.12=24.43✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3017（11-22 18:19, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:40)·训练健康iter=285830 step avg7325ms(n=15,4 transient>7.4s非持续✅) 0NaN/0skip·load.29=26.03/.12=28.52✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3016（11-22 18:09, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:40)·训练健康iter=285750 step avg7340.4ms(n=15,5 transient>7.4s非持续✅) 0NaN/0skip·load.29=27.33/.12=23.90✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3015（11-22 18:03, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:40)·训练健康iter=285680 step avg7308.7ms(n=15,2 transient>7.4s非持续✅) 0NaN/0skip·load.29=26.40/.12=24.50✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3009（11-22 17:17, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:39)·训练健康iter=285300 step avg7226ms(n=12,1 transient>7.4s✅) 0NaN/0skip·load.29=30.39/.12=26.29✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3008（11-22 17:07, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:39)·训练健康iter=285240 step avg7236ms(n=20,1 transient>7.4s✅) 0NaN/0skip·load.29=25.57/.12=25.79✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3007（11-22 16:59, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:38)·训练健康iter=285170 step avg7184ms(n=11) 0NaN/0skip·load.29=26.88/.12=22.58✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3006（11-22 16:54, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:39)·训练健康iter=285110 step avg7258ms(n=10,1 transient7432ms>7.4s非持续✅) 0NaN/0skip·load.29=26.01/.12=25.28✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3005（11-22 16:45, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:38)·训练健康iter=285070 step avg7298ms(n=10,1 transient7443ms>7.4s非持续✅) 0NaN/0skip·load.29=26.62/.12=25.65✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3004（11-22 16:39, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:39)·训练健康iter=285000 step avg7267ms(n=10,1 transient7567ms>7.4s非持续✅) 0NaN/0skip·load.29=28.18/.12=24.70✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3003（11-22 16:34, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k)·训练健康iter=284960 step avg7281ms(n=10,1 transient7567ms>7.4s非持续✅) 0NaN/0skip·load.29=25.88/.12=23.71✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3002（11-22 16:25, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k)·训练健康iter=284890 step avg7277ms(n=10,1 transient7412ms>7.4s非持续✅) 0NaN/0skip·load.29=25.41/.12=26.09✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3001（11-22 16:18, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:40)·训练健康iter=284830 step avg7285ms(n=6,1 transient7411ms>7.4s非持续✅) 0NaN/0skip·load.29=24.74/.12=24.86✅·L1报告34ckpt·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3000（11-22 16:11, 放行autoqueue令·监控巡检·daemon idle(284k DONE,等286k ETA~18:38)·训练健康iter=284770 step avg7239ms(n=10,1 transient7415ms>7.4s非持续✅) 0NaN/0skip·load.29=24.83/.12=24.57✅·L1报告34ckpt(284k最新,auto-refreshed16:02)·backlog全清）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2999（11-22 16:03, 放行autoqueue令·监控巡检·284k eval DONE(harness Avg=58.25%,daemon 16:01完成,auto-refresh报告16:02,34ckpt)·backlog 270k-284k全清(8ckpt:270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62/284k58.25%)·训练健康iter=284680 step DURING eval avg7335ms→post-eval avg7324ms 0NaN/0skip·step time eval前7273→eval中7335(Δ+62ms NOT elevated✅)→eval后7324·load.29=43.91/.12=26.45✅·daemon idle等286k ETA~18:40·L1报告34ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2998（11-22 15:35, 放行autoqueue令·监控巡检·284k eval RUNNING(~56min,lm_eval PID922915,ETA~16:00)·训练健康iter=284480 step DURING eval(n=15:avg7239ms,1 transient>7.4s非持续✅) 0NaN/0skip·step time eval前7273→eval中7239 Δ-34ms(NOT elevated✅)·load.29=28.22/.12=25.22✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2997（11-22 15:29, 放行autoqueue令·监控巡检·284k eval RUNNING(~50min,lm_eval PID922915,ETA~16:00)·训练健康iter=284430 step DURING eval(n=10:avg7251ms,2 transient>7.4s非持续✅) 0NaN/0skip·step time eval前7273→eval中7251 Δ-22ms(NOT elevated✅)·load.29=28.79/.12=25.97✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2996（11-22 15:23, 放行autoqueue令·监控巡检·284k eval RUNNING(~44min,lm_eval PID922915,llama-server PID910819,step[5/6]since14:39,results.json未落盘,270k耗时80min→ETA~16:00,daemon将auto-refresh报告)·训练健康iter=284380/700000(40.63%) step DURING eval(n=5:7354.8/7123.8/7127.8/7312.8/7158.6ms avg7215.6ms,全<7.4s✅) loss≈1.984-2.000 grad_norm0.087-0.098 0NaN/0skip✅ lr=1e-3 stable·step time对比:eval前avg7273.3ms→eval中avg7215.6ms Δ≈-58ms(NOT elevated✅)·load.29=31.89/31.26/30.99·.12=24.17/24.76/25.01✅·backlog:270k-282k全清,284k eval RUNNING·daemon活跃(PID1081392,~69924s≈19.4h)·286k未落盘(ETA~18:30)·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2995（11-22 15:15, 放行autoqueue令·监控巡检·284k eval RUNNING(36min,lm_eval PID922915,ETA~15:59)·训练健康iter=284310 step DURING eval(n=25:avg7286.5ms,4 transient>7.4s后回落✅) 0NaN/0skip·step time eval前7273→eval中7287 Δ+13ms(NOT elevated✅)·load.29=33.63/.12=23.98✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2994（11-22 15:08, 放行autoqueue令·监控巡检·284k eval RUNNING(lm_eval PID922915 ~30min,results.json未落盘,ETA~16:00)·训练健康iter=284260 step DURING eval(n=8:avg≈7311ms,2 transient>7.4s✅) 0NaN/0skip·step time eval前7253→eval中7311 Δ≈+58ms(NOT elevated✅)·load.29=29.02/.12=25.40✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2993（11-22 15:02, 放行autoqueue令·监控巡检·284k eval RUNNING(llama-server PID910819 ~23min,eval Phase5/6 since14:39,270k耗时80min→ETA~16:00)·训练健康iter=284210 step DURING eval(n=3:7268.6/7241.3/7205.1ms,全<7.4s✅) loss≈1.99 0NaN/0skip·step time eval前7253→eval中7238 Δ-15ms(NOT elevated✅)·load.29=32.23/.12=23.62✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2992（11-22 14:52, 放行autoqueue令·监控巡检·284k eval RUNNING(lm_eval PID922915 ~13min,ETA~15:50)·训练健康iter=284120 step avg7250ms DURING eval(全<7.4s✅) 0NaN/0skip·step time eval前7253→eval中7250 Δ-3ms(NOT elevated✅)·load.29=26.59/.12=27.13✅·backlog:270k-282k全清,284k RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2991（11-22 14:42, 放行autoqueue令·监控巡检·daemon自动评284k(eval_running,lm_eval RUNNING step5/6,ETA~15:50)·训练健康iter=284040 step avg7222ms DURING eval(全<7.4s✅) 0NaN/0skip·step time eval前7265→eval中7222 Δ-43ms(NOT elevated✅)·load.29=28.07/.12=26.04✅·backlog:270k-282k全清,284k eval RUNNING·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #2990（11-22 14:36, 放行autoqueue令·监控巡检·daemon idle(282k DONE,等284k ETA~14:37)·训练健康iter=283990 step avg7265ms 0NaN/0skip·step time NO eval load avg7265ms·load.29=28.92/.12=26.29✅·backlog全清(270k-282k 7ckpt)·L1报告33ckpt✅）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2989及更早（已归档，含 #2977-#2989 监控轮 + #2900–#2976 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

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