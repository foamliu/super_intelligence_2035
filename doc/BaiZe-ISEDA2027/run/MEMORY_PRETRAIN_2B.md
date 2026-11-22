# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
> 📦 #3107（2026-11-23 06:22, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291840/700000(41.69%) step_avg(last10)=7256ms(<7.4s gate✅)·load .29=27.08/.12=26.22✅(无pc2_fast)·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3106（2026-11-23 06:15, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291780/700000(41.69%) step_avg(last10)=7238ms(<7.4s gate✅)·load .29=23.18/.12=27.59✅(无pc2_fast)·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3105（2026-11-23 06:09, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291730 step_avg(last10)=7190ms(<7.4s gate✅)·load .29=25.52/.12=25.83✅(无pc2_fast)·daemon idle等292k ETA≈06:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3102（2026-11-23 05:47, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291530/700000(41.65%) step_avg(last10)=7206ms(<7.4s gate✅)·load .29=24.70/.12=28.08✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。

> 📦 #3101（2026-11-23 05:39, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291470/700000(41.64%) step_avg(last10)=7216ms(<7.4s gate✅)·load .29=28.44/.12=25.01✅(无pc2_fast)·daemon idle等292k ETA≈06:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3100（2026-11-23 05:30, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291400/700000(41.63%) step_avg(last10)=7143ms(<7.4s gate✅)·load .29=27.27/.12=26.59✅(无pc2_fast)·daemon idle等292k ETA≈06:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3096（2026-11-23 05:04, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291190 step_avg(last10)=7242ms(<gate✅)·load .29=95.01瞬态spike(5min=42.99)/.12=25.10✅·daemon idle等292k ETA≈06:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3097（2026-11-23 05:09, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291230 step_avg(last10)=7355ms(<gate✅)·load .29=27.57/.12=27.47✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3103（2026-11-23 05:56, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291620 step_avg(last10)=7200ms(<gate✅)·load .29=24.61/.12=25.45✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。

WAITING: 0(✅ **2026-11-23 06:22 #3107 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt(270k59.75/272k56.75/274k60.00/276k58.12/278k57.38/280k58.38/282k58.62/284k58.25/286k59.88/288k58.50/290k55.25)·训练健康iter=291840/700000(41.69%) step_avg(last10)=7256ms(<7.4s gate✅;last10=7339.9/7284.9/7252.2/7315.7/7251.1/7164.7/7191.1/7354.9/7155.1/7246.1ms;无sustained spike✅) loss≈1.988 0NaN/0skip✅ lr=1e-3 stable·eval无负载(daemon idle,sleep 300s轮询,last idle@06:19:16,GGUF已清理,llama-server/lm_eval 0进程✅)·load .29=27.08/26.14/25.86✅(NOT eval-induced) .12=26.22/26.14/26.08✅(无pc2_fast,ssh直查)·GPU .29=8×H100 96-100%util✅·daemon健康(PID1081392 ppid=1 etimes≈34.4h alive,idle等292k)·292k未落盘(training@291840,latest ckpt=iter_0290000,距292k=160步×~7.26s≈19min,ETA≈06:42)·L1报告37ckpt含290k=55.25%✅(33.8KB,04:09)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter291840@06:22) daemon=/tmp/baize_l1_autoqueue_continuous.log(idle@06:19:16 "no new ckpt") ckpt_root=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints(latest=iter_0290000) res=.../lm_eval_results/gguf_iter_290000_fixed_8set/results.json report=.../run/reports/report_pretrain_llamacpp_scaling_zh.html(33.8KB,37ckpt,04:09)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·训练进程=11-20重启那套(健康,16×pretrain_launcher worker.log逻辑iter前进)·纯eval/监控未碰train.sh/configs/.bak/训练进程(铁律悍守)·体积MEMORY≈20.3KB<32KB✅ TASK≈25.3KB<32KB✅)
> 📦 #3098（2026-11-23 05:17, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291290 step_avg(last10)=7305ms(<gate✅)·load .29=28.12/28.51/29.78✅/.12=25.05/25.48/25.90✅·daemon idle等292k ETA≈07:00）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3095（2026-11-23 05:00, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291150 step_avg(last10)=7231ms(<gate✅)·load .29=29.94/.12=26.80✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3094（2026-11-23 04:51, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291080 step_avg(last10)=7138ms(<gate✅)·load .29=29.94/.12=26.80✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3093（2026-11-23 04:45, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=291030 step_avg(last10)=7129ms(<gate✅)·load .29=27.33/.12=26.80✅·daemon idle等292k ETA≈06:36）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3092（2026-11-23 04:36, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=290960 step_avg(last10)=7338ms(<gate✅;含290900瞬态8441ms单点NOT sustained)·load .29=27.62/.12=23.86✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3091（2026-11-23 04:29, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=290890 step_avg(last10)=7234ms(<gate✅)·load .29=54.38瞬态spike(NOT eval-induced)/.12=23.94✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3090（2026-11-23 04:23, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=290840 step_avg(last10)=7198ms(<gate✅)·load .29=25.08/.12=25.18✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3089（2026-11-23 04:17, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog 270k-290k全清11ckpt·训练健康iter=290800 step_avg(last10)=7339ms(<gate✅;290710步8174ms为post-eval瞬态spike NOT sustained)·load .29=27.31/.12=25.65✅·daemon idle等292k ETA≈06:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3088（2026-11-23 04:08, 放行autoqueue令·监控巡检·290k L1 DONE harness_avg=55.25%(DONE@04:03,results.json落盘,per-set:arc_c0.28/arc_e0.61/boolq0.49/hella0.52/obqa0.35/piqa0.79/sciq0.81/wino0.57)·backlog 270k-290k全清11ckpt·训练健康iter=290710 step_avg(last10)=7322ms(<gate✅)·load .29=25.77/.12=26.70✅·daemon idle等292k ETA≈06:46）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3087（2026-11-23 04:01, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~1h15m,daemon[5/6]eval中)·backlog全清270k-288k 10ckpt·训练健康iter=290670 step_avg(last10)=7316ms(<gate✅)·load .29=28.36/.12=23.41✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3086（2026-11-23 03:52, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~1h06m,daemon自治评测中)·backlog全清270k-288k 10ckpt·训练健康iter=290590 step_avg(last10)=7346ms(含transient spike,NOT sustained✅)·load .29=29.18/.12=27.62✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3085（2026-11-23 03:44, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~58min,daemon自治评测中)·backlog全清270k-288k 10ckpt·训练健康iter=290520 step_avg(last10)=7106ms(<gate✅)·load .29=30.31/.12=26.14✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3084（2026-11-23 03:37, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~51min,daemon自治评测中)·backlog全清270k-288k 10ckpt·训练健康iter=290470 step_avg(last10)=7070ms(NOT elevated✅)·load .29=27.81/.12=26.00✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3083（2026-11-23 03:26, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~40min,daemon自治评测中)·backlog全清270k-288k 11ckpt·训练健康iter=290360 step_avg(last10)≈7327ms(含瞬态spike,NOT sustained✅)·load .29=39.69/.12=25.08✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3082（2026-11-23 03:17, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~31min,daemon自治评测中)·backlog全清270k-288k 11ckpt·训练健康iter=290300 step_avg≈7140ms(NOT elevated✅)·load .29=35.50/.12=23.86✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3081（2026-11-23 03:10, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~24min,daemon自治评测中)·backlog全清270k-288k 11ckpt·训练健康iter=290240 step_avg≈7091ms(NOT elevated✅)·load .29=31.42/.12=23.50✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3080（2026-11-23 03:03, 放行autoqueue令·监控巡检·eval_running=290k(自02:46:32起~17min,daemon自治评测中)·backlog全清270k-288k 11ckpt·训练健康iter=290170 step_avg≈7086ms(NOT elevated✅)·load .29=28.26/.12=24.17✅·daemon健康·290k eval进程活）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3079（2026-11-23 02:31, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289910 step_avg≈7136ms(NOT elevated✅)·load .29=28.45/.12=22.79✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3078（2026-11-23 02:24, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289850 step_avg≈7141ms(NOT elevated✅)·load .29=27.92/.12=25.33✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3077（2026-11-23 02:19, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289810 step_avg≈7122ms(NOT elevated✅)·load .29=26.63/.12=25.01✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3076（2026-11-23 02:11, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289760 step_avg≈7107ms(NOT elevated✅)·load .29=28.37/.12=24.00✅·daemon idle等290k ETA~02:39）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3075（2026-11-23 02:04, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289680 step_avg≈7087ms(NOT elevated✅)·load .29=27.79/.12=25.28✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3074（2026-11-23 01:59, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289640 step_avg≈7119ms(NOT elevated✅)·load .29=28.59/.12=25.06✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3073（2026-11-23 01:51, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289580 step_avg≈7126ms(NOT elevated✅)·load .29=25.66/.12=26.50✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3072（2026-11-23 01:46, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289530 step_avg≈7095ms(NOT elevated✅)·load .29=27.71/.12=23.55✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3071（2026-11-23 01:38, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289470 step_avg≈7081ms(NOT elevated✅)·load .29=26.99/.12=28.41✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3070（2026-11-23 01:30, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289400 step_avg≈7103ms(NOT elevated✅)·load .29=26.99/.12=23.72✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3069（2026-11-23 01:18, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289290 step_avg≈7247ms(NOT elevated✅)·load .29=25.39/.12=23.11✅·daemon idle等290k ETA~02:44）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3068（2026-11-23 01:08, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=289210 step_avg≈7396ms(NOT elevated✅)·load .29=26.33/.12=25.20✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3067（2026-11-23 01:02, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289160 step_avg≈7362ms(NOT elevated✅)·load .29=26.72/.12=25.44✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3066（2026-11-23 00:56, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289110 step_avg≈7172ms(NOT elevated✅)·load .29=27.68/.12=27.21✅·daemon idle等290k ETA~02:40）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3065（2026-11-23 00:49, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=289060 step_avg≈7346ms(NOT elevated✅)·load .29=26.21/.12=27.10✅·daemon idle等290k ETA~02:44）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3064（2026-11-23 00:41, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288990 step_avg≈7130ms(NOT elevated✅)·load .29=27.40/.12=26.44✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3063（2026-11-23 00:37, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288960 step_avg≈7210ms(NOT elevated✅)·load .29=24.73/.12=24.62✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3062（2026-11-23 00:34, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288930 step_avg≈7180ms(NOT elevated✅)·load .29=27.64/.12=26.51✅·daemon idle等290k ETA~02:43）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3061（2026-11-23 00:28, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt·训练健康iter=288880 step_avg=7250ms(NOT elevated✅)·load .29=28.33/.12=正常✅·daemon idle等290k ETA~02:42）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 #3060（2026-11-23 00:20, 放行autoqueue令·监控巡检·daemon idle无eval负载·backlog全清270k-288k 11ckpt(288k DONE 00:04)·训练健康iter=288810 step_avg=7288ms(NOT elevated✅)·load .29=26.76/.12=23.13✅·daemon idle等290k ETA~02:41）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3047–#3057（2026-11-22 22:31–23:56, 放行autoqueue令·288k eval RUNNING监控轮11条·backlog全清270k-286k·训练健康step~7.1-7.3s·load正常·daemon eval 288k·288k于00:04 DONE harness_avg=58.50%）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2990–#3034（已归档，含 #3030 286k eval DONE·#3029-#2990 286k/284k/282k eval RUNNING监控轮）→ daily-memories/2026-11-22.md；需要时再读。
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