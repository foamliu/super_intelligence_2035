监控巡检·322k eval RUNNING(daemon auto-pick@19:22,llama-server PID3743525 -t4 nice19 + lm_eval PID3755748 ~21min in,results dir空待写,ETA~20:40)·autoqueue 52/52ckpt(10k-320k)✅+322k in-progress·报告=40882B(52/52ckpt)·训练健康iter=322220/700000(46.0%) step_avg(pre-eval 26steps)=7217ms(7.22s)→step_avg(during-eval 14steps)=7202ms(7.20s) Δ-0.02s NOT elevated✅·loss=1.99 0NaN/0skip✅·lr=1e-3·grad norm=0.101✅·GPU 8×98-100%✅·load=38.42(eval中)·train.sh PID2547367✅(~5.2d)·324k NOT on disk(lands~23:15)·WAITING=0。
> 📦 #3390（2026-11-25 19:43, 监控巡检·322k eval RUNNING(daemon auto-pick@19:22,GGUF done@19:22:08,llama-server PID3743525+lm_eval PID3755748 ~21min in,results dir空,ETA~20:40)·训练健康iter=322220/700000(46.0%) step_avg(pre-eval 26steps)=7217ms(7.22s,1/26>7.4s非持续✅)→step_avg(during-eval 14steps)=7202ms(7.20s,1/14>7.4s非持续✅) Δ-0.02s NOT elevated✅·loss=1.99 0NaN/0skip✅·lr=1e-3 grad norm=0.101✅·GPU 8×98-100%✅·load=38.42(eval中)✅·eval未拖训练(pre-eval7.22s→during7.20s Δ-0.02s✅)·autoqueue 52/52ckpt(10k-320k)✅+322k in-progress·报告=40882B·324k NOT on disk(lands~23:15)·evidence:worker=/tmp/baize_s1_baize2b_worker.log(iter322220@19:43:32) daemon=/tmp/baize_l1_autoqueue_continuous.log([5/6]eval@19:22:08) ckpt=.../checkpoints(latest iter_0322000) results=.../gguf_iter_322000_fixed_8set/(空,lm_eval running) report=run/reports/report_pretrain_llamacpp_scaling_zh.html(52/52ckpt,40882B)·复现=bash code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh·纯监控未碰train.sh/configs/.bak/训练进程/daemon(铁律悍守)·体积MEMORY≈10KB<32KB✅ TASK≈30.6KB<32KB✅）→ daily-memories/2026-11-25.md

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
 