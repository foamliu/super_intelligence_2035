# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0(✅ **2026-11-23 01:02 #3067 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289160/700000(41.31%) step_avg≈7362ms(last5:7559/7404/7338/7305/7202,NOT elevated✅<7.4s,无持续spike,单步7559为偶发) loss≈2.00(1.999-2.008) 0NaN/0skip✅ lr=1e-3 stable grad_norm~0.09-0.11·load:.29=26.72/27.25/27.74✅ .12=28.89/25.97/25.44✅·GPU .29=8×95-100%训练满载✅(~74.7GB)·daemon idle(PID1081392 ppid=1 etimes~104693s alive,sleep300s,等290k ETA~02:43)·290k未落盘(最新ckpt=iter_0288000,save-interval=2000,~840 iters to go)·L1报告36ckpt含288k✅(33469B,288k harness_avg=58.50%)·270k-288k全清scores:270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62/284k58.25/286k59.88/288k58.50·本轮无eval负载step_avg≈7362ms(NOT elevated✅)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter289160@01:01:17 step7202ms✅) daemon=/tmp/baize_l1_autoqueue_continuous.log(idle至01:00:30✅)·report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(33469B,36ckpt)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·训练进程=11-20重启那套(pretrain_loop PID1475330 alive etimes~210959s✅)·纯eval/监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈12.1KB<32KB✅ TASK≈25.3KB<32KB✅)
> 📦 #3066（2026-11-23 00:56, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289110 step_avg≈7172ms(NOT elevated✅)·load .29=27.68/.12=27.21✅·daemon idle等290k ETA~02:40）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3065（2026-11-23 00:49, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289060 step_avg≈7346ms(NOT elevated✅)·load .29=26.21/.12=27.10✅·daemon idle等290k ETA~02:44）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3064（2026-11-23 00:41, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288990 step_avg≈7130ms(NOT elevated✅)·load .29=27.40/.12=26.44✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3063（2026-11-23 00:37, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288960 step_avg≈7210ms(NOT elevated✅)·load .29=24.73/.12=24.62✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3062（2026-11-23 00:34, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288930 step_avg≈7180ms(NOT elevated✅)·load .29=27.64/.12=26.51✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3061（2026-11-23 00:28, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=288880 step_avg=7250ms(NOT elevated✅)·load .29=28.33/.12=正常✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3060（2026-11-23 00:20, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288810 step_avg=7288ms(NOT elevated✅)·load .29=26.76/.12=23.13✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3059（2026-11-23 00:12, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288760 step_avg=7259ms(NOT elevated✅)·load .29=26.98/.12=24.25✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3058（2026-11-23 00:06, 放行autoqueue令·监控巡检·288k eval DONE(harness_avg=58.50%,elapsed4713.7s,daemon auto-refreshed report+cleaned GGUF+killed server)·backlog全清270k-288k 11ckpt·训练健康iter=288700 step POST-eval=7118ms(NOT elevated✅)·load POST-eval .29=28.81/.12=25.77✅·daemon idle等290k）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3047–#3057（2026-11-22 22:31–23:56, 放行autoqueue令·288k eval RUNNING监控轮11条·backlog全清270k-286k·训练健康step~7.1-7.3s·load正常·daemon eval 288k·288k于00:04 DONE harness_avg=58.50%）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3048（2026-11-22 22:31, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:42)·训练健康iter=287910 step avg~7287ms 0NaN/0skip·load.29=26.70/.12=24.29✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3047（2026-11-22 22:24, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:42)·训练健康iter=287850 step avg~7231ms 0NaN/0skip·load.29=30.50/.12=24.88✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3046（2026-11-22 22:09, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:41)·训练健康iter=287730 step avg~7251ms 0NaN/0skip·load.29=30.51/.12=26.26✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3045（2026-11-22 22:02, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:41)·训练健康iter=287680 step avg~7264ms 0NaN/0skip·load.29=31.33/.12=24.68✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3044（2026-11-22 21:54, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:42)·训练健康iter=287610 step avg~7320ms 0NaN/0skip·load.29=28.41/.12=28.27✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3043（2026-11-22 21:48, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:42)·训练健康iter=287560 step avg~7308ms 0NaN/0skip·load.29=26.82/.12=23.92✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3042（2026-11-22 21:39, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:41)·训练健康iter=287490 step avg~7259ms 0NaN/0skip·load.29=27.81/.12=23.57✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3041（2026-11-22 21:30, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:42)·训练健康iter=287410 step avg~7253ms 0NaN/0skip·load.29=28.27/.12=28.27✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3040（2026-11-22 21:25, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:41)·训练健康iter=287370 step avg~7237ms 0NaN/0skip·load.29=28.08/.12=28.44✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3039（2026-11-22 21:18, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:42)·训练健康iter=287310 step avg~7294ms 0NaN/0skip·load.29=27.92/.12=25.03✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3038（2026-11-22 21:06, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:43)·训练健康iter=287210 step avg~7296ms 0NaN/0skip·load.29=24.36/.12=25.44✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3037（2026-11-22 21:00, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:40)·训练健康iter=287170 step~7283ms 0NaN/0skip·load.29=27.03/.12=28.27✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 #3036（2026-11-22 20:54, 放行autoqueue令·监控巡检·daemon idle(286k DONE 20:04,backlog全清270k-286k 10ckpt,等288k ETA~22:42)·训练健康iter=287110 step avg~7332ms 0NaN/0skip·load.29=27.56/.12=25.58✅·daemon idle等288k）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2990–#3034（已归档，含 #3030 286k eval DONE·#3029-#2990 286k/284k/282k eval RUNNING监控轮）→ daily-memories/2026-11-22.md；需要时再读。
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