✅ 监控巡检·训练健康iter=337710/700000(48.24%)·loss≈2.00 0NaN/0skip✅·⚠️step avg10=7.47s>7.4s gate(IMPROVING 7.51→7.47s,oscillating 7.24-7.82s,0 outliers>8s,2/10<7.4s,daemon idle=NOT eval-caused,pre-existing since#3413~14h,⚠️待运维处理 per11-26令)·GPU 8×73-100%/74-75GB/53-64°C✅·daemon idle·autoqueue 57/57ckpt(10k-330k✅,330k=57.50%)·eval_next=340k(NOT on disk,ETA~08:28)·WAITING=0。
> #3446（2026-11-27 03:43, 监控巡检·训练健康iter=337710/700000(48.24%) loss≈2.001(lr=1e-3,grad norm=0.089✅,no spikes) 0NaN/0skip✅·**⚠️step avg10=7.47s>7.4s gate**(latest10:7515.9/7415.6/7471.7/7576.2/7821.3/7270.4/7237.5/7402.6/7482.1/7483.3ms,IMPROVING from7.51s(#3445)→7.47s,oscillating 7.24-7.82s,0 outliers>8s,2/10<7.4s(7270.4/7237.5ms),daemon idle=NOT eval-caused,pre-existing since#3413~14h,⚠️待运维处理 per11-26令)·GPU 8×73-100%/74-75GB/53-64°C✅·load .29=28.44/27.54/27.65 .12=26.19/25.57/25.22·daemon PID501728 idle(etimes~25482s,sleeping 300s,last activity 330k DONE@00:24:07)·ckpt on disk:latest=iter_0336000·autoqueue 57/57ckpt(10k-330k✅,330k=57.50% harness_avg)+332k/334k/336k SKIPPED(non-10k)·10k cadence✅·eval_next=340k(NOT on disk,ETA~08:28 11-27,~4.75h,2290 steps×~7.47s)·NOTE:when 340k lands daemon checks step<7.4s gate,if still>7.4s→pause 10min retry·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter337710@03:42,step=7483ms,avg10=7.47s) daemon=/tmp/baize_l1_autoqueue_continuous.log(idle@03:40:00) ckpt=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/ report=run/reports/report_pretrain_llamacpp_scaling_zh.html(43506B,57/57ckpt,density note✅)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈15.0KB<32KB✅ TASK≈31.4KB≤32KB✅）→ daily-memories/2026-11-27.md

> #3445（2026-11-27 03:32, 监控巡检·训练健康iter≈337620/700000(48.23%) loss≈1.995(lr=1e-3,grad norm=0.092✅,no spikes) 0NaN/0skip✅·**⚠️step avg10=7.51s>7.4s gate**(latest10:7571.6/7655.9/7454.4/7358.3/7276.5/7446.0/7593.2/7500.3/7719.3/7515.9ms,IMPROVING from7.78s(#3444)→7.51s,oscillating 7.28-7.72s,0 outliers>8s,2/10<7.4s(7276.5/7358.3ms),daemon idle=NOT eval-caused,pre-existing since#3413~13h,⚠️待运维处理 per11-26令)·GPU 8×96-100%/74-75GB/56-61°C✅·load .29=29.02/27.81/27.83 .12=26.11/25.00/24.80·daemon PID501728 idle(etimes~24774s,sleeping 300s,last activity 330k DONE@00:24:07)·ckpt on disk:latest=iter_0336000·autoqueue 57/57ckpt(10k-330k✅,330k=57.50% harness_avg)+332k/334k/336k SKIPPED(non-10k)·10k cadence✅·eval_next=340k(NOT on disk,ETA~08:30 11-27,~5.0h,2380 steps×~7.51s)·NOTE:when 340k lands daemon checks step<7.4s gate,if still>7.4s→pause 10min retry·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter337610@03:30,step=7719ms,avg10=7.51s) daemon=/tmp/baize_l1_autoqueue_continuous.log(idle@03:29:59) ckpt=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/ report=run/reports/report_pretrain_llamacpp_scaling_zh.html(43506B,57/57ckpt,density note✅)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈14.8KB<32KB✅ TASK≈32.1KB≤32KB✅）→ daily-memories/2026-11-27.md

> 📦 #3444（2026-11-27 03:18, 监控巡检·step avg10=7.78s(>7.4s gate,WORSENING)·训练健康iter=337500·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。

> 📦 #3443（2026-11-27 03:02, 监控巡检·step avg10=7.57s(>7.4s gate)·训练健康iter=337380·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。

> 📦 #3442（2026-11-27 02:53, 监控巡检·step avg10=7.61s(>7.4s gate,WORSENING)·训练健康iter=337310·daemon idle·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3440-#3441（2026-11-27 02:34-02:43, 监控巡检2轮·step avg10=7.49→7.52s(>7.4s gate,SLIGHTLY WORSENING)·daemon idle·训练健康iter=337170-337230·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 §#3431–#3439（2026-11-27 00:55–02:27, 监控巡检9轮·step avg10=7.49-7.78s(>7.4s gate,oscillating WORSENING)·daemon idle·训练健康iter=336360-337100·eval_next=340k·WAITING=0）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3430（2026-11-27 00:29, 330k eval DONE✅ harness_avg=57.50%·step-time三段:pre-eval>7.4s(80min w/o eval)→during-eval peaked 7.97s→post-eval recovering 7.19s·训练iter=336170·daemon idle·autoqueue 57/57ckpt·eval_next=340k）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 §#3412–#3429（2026-11-26 18:41 – 2026-11-27 00:14, 放行autoqueue令+10k cadence变更·监控巡检~18轮·328k eval DONE(58.38%)→330k eval FAILED(killed step>7.4s)→10k cadence implemented(#3418)→330k eval RUNNING(76min)→DONE(57.50%)·step plateau 7.35-7.70s 80min w/o eval(pre-existing)→eval dragging→post-eval recovering·训练健康iter 333420→336060 step~7.0-8.0s·eval未拖训练✅·report 42783B→43506B(56→57ckpt)）→ daily-memories/2026-11-27.md；需要时再读。
> 📦 #3417（2026-11-26 20:01, ⚠️EVAL KILLED—step persistently >7.4s·330k eval killed@~19:58·step avg10 trend 7.39s→8.0s+·per 11-21令 executed·daemon paused·训练健康iter=334050）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 §#3414–#3416（2026-11-26 19:11–19:32, 放行autoqueue令·330k eval RUNNING监控3轮·step avg10从7.39s→7.43s→7.47s(borderline 7.4s gate,eval adds ~0.04-0.08s)·训练健康iter 333660→333830·GPU 8×91-100%✅·autoqueue 56/56ckpt+330k RUNNING→后因step持续>7.4s于#3417 kill eval）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 #3413（2026-11-26 19:01, 监控巡检·daemon paused@19:00:37(step=7.41s>7.4s gate)·step borderline avg10=7.41s·训练健康iter=333570·autoqueue 56/56ckpt）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 #3412（2026-11-26 18:41, 监控巡检·328k eval DONE✅ harness_avg=58.38%·daemon paused@18:40:36(step=7.42s)·训练健康iter=333420·autoqueue 56/56ckpt）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 §#3407–#3411（2026-11-26 17:19–18:23, 监控巡检5轮·328k eval RUNNING监控(17:24 start,daemon 2×pause step>7.4s→resume→eval 76min)·step elevated avg10=7.38-7.61s(>7.4s gate borderline,daemon auto-pause/resume)·训练健康step~7.2-7.7s·328k于18:40 DONE=58.38%见#3412·eval未拖训练✅）→ daily-memories/2026-11-26.md；需要时再读。
> 📦 §#3390–#3406（2026-11-25 19:43 – 2026-11-26 17:11, 监控巡检~17轮·326k eval DONE(58.88%)→328k eval RUNNING/PAUSED/kill/retry·sympy FIX(#3396,daemon stuck 40h→restored)·step spike→kill→recover·backlog全清·eval未拖训练✅·report多次regen）→ daily-memories/2026-11-26.md；需要时再读。

> 📦 #3379-#3380（2026-11-25 16:40-17:08, 监控巡检·320k eval DONE harness_avg=54.62%·⚠️step time spike(320680-320750,7.64-8.14s,harness CPU争抢NOT eval-caused)→17:08已恢复avg=7.22s·报告修复regen→40882B(52/52ckpt)）→ daily-memories/2026-11-25.md；需要时再读。


> 📦 #3381-#3382（2026-11-25 17:21-17:37, 监控巡检2轮·daemon idle无eval负载·训练健康iter321030-321160 step7.21-7.40s(all≤7.4s✅,1单点spike NOT sustained)·GPU 8×81-100%✅·load正常·报告=40882B(52/52ckpt)✅·research日报11-25已noted(长上下文温度校准/loop residual/TinyLlama对照/Llemma三源配比/phi-1.5 synthetic消融),无即时action）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3383-#3384（2026-11-25 18:05-18:12, 监控巡检2轮·daemon idle无eval负载·训练健康iter321400-321450 step7.19-7.22s(all<7.4s✅)·报告修复regen·GPU正常·load正常）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3385（2026-11-25 18:26, 监控巡检·daemon idle·autoqueue令持续履行·训练健康iter321580 step7.22s·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3386（2026-11-25 18:35, 监控巡检·daemon idle·autoqueue令持续履行(52/52ckpt)·322k NOT on disk·训练iter=321640 step7.29s·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3387（2026-11-25 18:52, 监控巡检·daemon idle·autoqueue令持续履行(52/52ckpt)·322k NOT on disk·训练iter=321790 step7.28s·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。
> 📦 #3388（2026-11-25 19:03, 监控巡检·daemon idle·autoqueue 52/52ckpt(10k-320k)✅·322k NOT on disk·训练iter=321880 step7.21s·报告40882B·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3376-#3378（2026-11-25 16:02-16:32, 监控巡检3轮·320k eval RUNNING→DONE·step正常(7.20-7.26s,0>7.4s✅)·eval未拖训练✅·报告修复(regen→40400B 51/51ckpt)）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3375（2026-11-25 15:45, 监控巡检·320k eval RUNNING·step7.25s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3374（2026-11-25 15:33, 监控巡检+报告修复·320k eval RUNNING·报告修复(vision auto-commit revert→regen 51/51ckpt 40400B✅)·step7.24s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 #3373（2026-11-25 15:20, 监控巡检·320k eval RUNNING·step7.22s NOT elevated✅·WAITING=0）→ daily-memories/2026-11-25.md；需要时再读。


> 📦 §#3340–#3372（2026-11-25 08:43–15:10, 放行autoqueue令·监控巡检~30轮·312k/314k/316k/318k eval DONE(harness:312k=55.62%/314k=56.25%/316k=57.38%/318k=56.25%)·daemon print口径修复(#3365 acc_only→harness_avg)·⚠️daemon stuck 9h(312k:01_convert_hf_to_gguf.sh git untrack→recovered 08:32)·训练健康step~7.15-7.50s·backlog 270k-318k全清51/51ckpt·eval未拖训练✅·report多次修复regen(vision auto-commit覆盖→恢复)）→ daily-memories/2026-11-25.md；需要时再读。

> 📦 §#3208–#3338（2026-11-24 00:12–19:15, 放行autoqueue令·监控巡检~40轮·300k/302k/304k/306k/308k/310k eval DONE(300k=56.88%/302k=59.13%/304k=59.00%/306k=59.25%/308k=58.38%)·训练健康step~7.0-7.5s·backlog 270k-310k全清46/46ckpt·270k=59.75%/272k=56.75%积压点已补评✅·eval未拖训练✅·L1报告多次regen·step-time spike(320680-320750,7.64-8.14s,harness CPU争抢NOT eval-caused)）→ daily-memories/2026-11-24.md；需要时再读。

> 📦 §#3170–#3207（2026-11-23 17:23–23:56, 放行autoqueue令·300k eval RUNNING监控+daemon idle监控~25轮·训练健康step~7.12-7.34s(all<7.4s✅)·load正常·backlog 270k-298k全清·含#3201 300k LANDED✅·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 §#3143–#3148（2026-11-23 12:25–13:11, 放行autoqueue令·daemon idle监控巡检6轮·backlog全清270k-294k 14ckpt·训练健康step~7.21-7.34s(all<7.4s gate✅,daemon idle确认非eval致)·load正常·296k NOT on disk ETA≈14:48→daily-memories/2026-11-23.md；需要时再读。）

> 📦 #3142（2026-11-23 12:10, 放行autoqueue令·**294k eval DONE✅Avg=59.00%**(arc_c32/arc_e68/boolq59/hella55/obqa35/piqa77/sciq85/wino61,74min)·训练健康iter=294690 step7.22s·step-time三段:pre7.35s→during7.28s→post7.22s eval未拖训练✅·backlog全清270k-294k 14ckpt·L1报告39/40ckpt含294k✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3138–#3141（2026-11-23 11:16–11:52, 放行autoqueue令·294k eval RUNNING监控4轮·eval未拖训练step~7.35-7.57s(NOT persistent>7.4s)·294k于12:02 DONE Avg=59.00% 见#3142）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 #3137（2026-11-23 10:37, 放行autoqueue令·daemon idle无eval负载·backlog全清270k-292k 13ckpt·训练健康iter=293940 step7.39s<gate·load正常·294k NOT on disk ETA~10:45）→ daily-memories/2026-11-23.md；需要时再读。


> 📦 §#3060–#3166（2026-11-23 00:20–16:41, 放行autoqueue令·监控巡检轮~52条(#3060-#3166含#3127-#3136等)·backlog 270k-296k全清·训练健康step~7.0-7.5s·load正常·含292k=60.63%(历史最高)/294k=59.00%/296k=59.12%/290k=55.25%等eval DONE·daemon idle/eval交替·eval未拖训练✅）→ daily-memories/2026-11-23.md；需要时再读。
> 📦 §#3047–#3057（2026-11-22 22:31–23:56, 放行autoqueue令·288k eval RUNNING监控轮11条·backlog全清270k-286k·训练健康step~7.1-7.3s·load正常·daemon eval 288k·288k于00:04 DONE harness_avg=58.50%）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2990–#3034（已归档，含 #3030 286k eval DONE·#3029-#2990 286k/284k/282k eval RUNNING监控轮）→ daily-memories/2026-11-22.md；需要时再读。
> 📦 §#2900–#2989及更早（已归档，含 #2977-#2989 监控轮 + #2900–#2976 监控轮 + #2778–#2919 监控轮 + #1992及更早批次）→ daily-memories/2026-11-2{0,1,2}.md & ARCHIVE_OPERATOR_PRETRAIN.md；需要时再读。

WAITING: 0

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
 