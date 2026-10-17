# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

## 当前状态
- STAGE: **🚀 Xmodel-2.5 80B decay v2 训练 RUNNING @.29**（08:44 启动, torchrun PID2597555 + 8 rank workers 2605722-29，step~3780/19980(18.9%), loss~1.34(1.3448@3780), lr~6.68e-4, ~298.3K tok/s, 8卡全占~100%/51.7GB, 0 crash, elapsed ~752.8min, **ETA ~53.7h → 2026-10-20 03:0x**）。**✅ 首真实 ckpt step_2000 已保存(15:23) → _orig_mod 修复真实保存验证通过、无崩溃、已续跑到 step3780**。**.12 由 vision ArmB 占用（8 vision 进程 PID1203297-304, 无 pretrain 进程）；.29 08:44 run 是唯一有效 pretrain 训练**。起点=step_532000。RUNNING 进程 save_interval=**2000**（下一 ckpt@step4000≈22:2x；.sh 已改 SAVE=500 供未来重启，当前 run 不重启）。目标:14集超 Xmodel-2.5 final(CS8 65.40%/CX 32.90%)。
  - PHASE: **decay80b_v2_dot29** — 80B decay v2 在 .29 健康 RUNNING（08:44 起, step~3780, loss~1.34, ~298.3K tok/s, 0 crash, 8×H100 .29 全占~100%/51.7GB, elapsed ~752.8min, **ETA ~53.7h → 2026-10-20 03:0x**）。**✅ 首真实 ckpt step_2000 已保存(15:23) → _orig_mod 修复真实保存验证通过、无崩溃**。运维令「停 .12 迁 .29」+ 用户令⑤「.29 固定 pretrain」目标已达成 → **无需重启**。下一 ckpt@step4000≈22:2x（save_interval=2000；.sh 已改 500 供未来重启）。
  - 轮询状态：v2 健康 RUNNING（step3780 @21:17, loss1.3448@3780, lr6.68e-4, tok/s298.3K, 0 crash, 8卡全占~100%/51763MiB/81559MiB, 进程 uptime ~12h33m）。s/step≈11.93s（t_fwd_bwd≈391.6ms/micro、t_opt≈152-195ms、t_data≈0.5ms→fast_data+GC off 生效）→ compile 生效（非 ~20s/step 回落 → 非 ~108h 悲观口径）。error scan：train_log grep error/traceback/nan/inf/_orig_mod/oom/killed/NCCL = **0 命中** ✅。→ **下一步**：监控下一 ckpt@step4000≈22:2x；**ETA (19980−3780)=16200步×11.93s≈53.7h → 2026-10-20 03:0x**。✅ .12 由 vision ArmB 占用（PID1203297-304, 无 pretrain 进程）；🚫 勿动 .29 健康训练、不重启。
> 📦 **[已归档] #512 流水（2026-10-17 ~21:17, 🩺 v2 训练监控·step3780 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step3780 健康, s/step≈11.93s, ETA~53.7h→10-20 03:0x, .12 vision ArmB 确认无 pretrain 进程。需要时再读。**
  > 📦 **[已归档] #476 流水（2026-10-17 ~03:48, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step740 loss1.8562 tok/s297.1K 健康, et=148min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #478 流水（2026-10-17 ~04:24, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step920 loss1.8969 lr1.36e-3 tok/s297.4K 健康, et=184min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #479 流水（2026-10-17 ~04:56, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step1080 loss1.7348 tok/s297.6K 健康, et=216min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #482 流水（2026-10-17 ~07:26, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step1840 loss1.5710 tok/s298.1K 健康, et=366.8min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #483 流水（2026-10-17 ~08:50, 🔧 修复 80B decay 崩溃 KeyError:_orig_mod + 重启续跑）→ daily-memories/2026-10-17.md；结论：save_hf_checkpoint 换出 _orig_mod 子模块修复 accelerate has_compiled_regions bug，verify_save@step20 ✅，从 step_532000 重启（无中间 ckpt，损失~2000步）。需要时再读。**
  > 📦 **[已归档] #484 流水（2026-10-17 ~09:28, 🩺 v2 重启后监控·step210 健康）→ daily-memories/2026-10-17.md；结论：v2 RUNNING step210 loss2.1771, decay-fix commit 609ffee9 已 push, verify_save@step20 log 佐证成功, 无第二实例。需要时再读。**
  > 📦 **[已归档] #485 流水（2026-10-17 ~10:02, 🩺 v2 训练监控·step380 健康）→ daily-memories/2026-10-17.md；结论：v2 RUNNING step380 loss2.08 tok/s295.0K 健康, verify_save@step20 ✅。需要时再读。**
  > 📦 **[已归档] #486 流水（2026-10-17 ~10:50, 🔧 纠正「迁 .12」误报）→ daily-memories/2026-10-17.md；结论：.12 10:30 run(PID593086) 10:45 SIGTERM(step70)，.29 08:44 run 从未被杀是唯一有效训练。需要时再读。**
  > 📦 **[已归档] #487 流水（2026-10-17 ~11:24, 🩺 v2 监控 step790 + 纠正 #486 + commit crash2 fix）→ daily-memories/2026-10-17.md；结论：step790 健康, .sh SAVE_INTERVAL=500 已 commit(efc5a66f), MEMORY 归档旧流水。需要时再读。**
  > 📦 **[已归档] #488 流水（2026-10-17 ~11:37, 🩺 v2 监控 step860 + 确认「停 .12 迁 .29」运维令已达成）→ daily-memories/2026-10-17.md；结论：step860 健康, .12 无 pretrain 进程, 运维令目标已达成无需动作。需要时再读。**
  > 📦 **[已归档] #489 流水（2026-10-17 ~12:02, 🩺 v2 监控 step980 + 上报 ETA）→ daily-memories/2026-10-17.md；结论：step980 健康, s/step≈11.95s, ETA~63h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #490 流水（2026-10-17 ~12:34, 🩺 v2 监控 step1149 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step1149 健康, s/step≈11.9s, ETA~62.4h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #491 流水（2026-10-17 ~12:49, 🩺 v2 监控 step1224 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step1224 健康, s/step≈11.93s, ETA~62.1h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #492 流水（2026-10-17 ~13:07, 🩺 v2 监控 step1310）→ daily-memories/2026-10-17.md；结论：step1310 健康, s/step≈11.9s, ETA~61.7h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #494 流水（2026-10-17 ~14:02, 🩺 v2 监控 step1594 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step1594 健康, s/step≈11.92s, ETA~60.9h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #495 流水（2026-10-17 ~14:14, 🩺 v2 监控 step1640 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step1640 健康, s/step≈11.91s, ETA~60.7h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #498 流水（2026-10-17 ~15:25, 🩺 v2 监控 step2010 + ✅首真实 ckpt step_2000 验证通过 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step2010 健康, step_2000 ckpt 已保存无 _orig_mod 崩溃, ETA~59.5h→10-20 02:5x。需要时再读。**
  > 📦 **[已归档] #499 流水（2026-10-17 ~15:59, 🩺 v2 监控 step2180 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step2180 健康, s/step≈11.92s, ETA~58.9h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
  > 📦 **[已归档] #500 流水（2026-10-17 ~16:26, 🩺 v2 监控 step2310 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step2310 健康, s/step≈11.92s, ETA~58.5h→10-20 02:5x, step_2000 ckpt 续跑无崩溃, .12=vision占用。需要时再读。**
  > 📦 **[已归档] #502 流水（2026-10-17 ~17:04, 🩺 v2 监控 step2500 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step2500 健康, s/step≈11.90s, ETA~57.8h→10-20 02:5x, step_2000 ckpt 续跑无崩溃, .12=vision占用。需要时再读。**
  > 📦 **[已归档] #507 流水（2026-10-17 ~18:52, 🩺 v2 监控 step3050 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step3050 健康, s/step≈11.92s, ETA~56.3h→10-20 03:1x, step_2000 ckpt 续跑无崩溃, .12=vision占用。需要时再读。**
  > 📦 **[已归档] #509 流水（2026-10-17 ~20:04, 🩺 v2 监控 step3410 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step3410 健康, s/step≈11.91s, ETA~54.8h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
> 📦 **[已归档] #510 流水（2026-10-17 ~20:27, 🩺 v2 监控 step3530 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step3530 健康, s/step≈11.92s, ETA~54.5h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
> 📦 **[已归档] #511 流水（2026-10-17 ~21:00, 🩺 v2 监控 step3694 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step3694 健康, s/step≈11.92s, ETA~53.9h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
- 🔧 **本唤醒推进 = #513（2026-10-17 ~22:07, 🚨 P0 抢修：重启 ops 中继）**：① **中继已恢复 ✅ PID=2706247**（`bash ops_relay.sh` 真守护, ppid=1/Ss, 22:07 起）→ `/tmp/baize_ops_relay.log` 无 error（`started ... poll=20s fetch_every=3x`）。② **自匹配根因修正**：运维原脚本 `pgrep -f 'bash [o]ps_relay[.]sh'` 会**误匹配 agent 进程**（其 argv 含任务书全文字面量 `bash ops_relay.sh`）→ 改用 **`^bash ops_relay[.]sh` 锚定 cmdline 开头**只杀真守护，落地 `/tmp/fix_relay_2040.sh` 再运行（遵守「写成脚本、禁止命令行组合 kill+启动」）。③ **判据三件套**：真 relay ≥1 ✅（2706247 ppid=1）；日志无 error ✅；`ops/.last_run_id` 仍 117 ✅（中继正执行 pending **RUN_ID 118**「sg docker 跑 oracle×3」，完成后自动→118）。④ **红线遵守**：🚫 未碰 torchrun/训练/loop/ckpt（训练 PID2597555+8rank 仍健康 RUNNING，仅只读核验）；🚫 未清 /tmp；🚫 未改训练配置。⑤ 注 `2708354 bash ops_relay.sh` = 2706247 在 `run_once` 命令替换 fork 的子 shell（pstree 其下才是 `timeout→bash→sg→harbor` 即 RUN_ID 118），**非第二实例**。⑥ 📦 体积：TASK=29.3KB(29984B)/MEMORY=21.4KB(21884B) 归档 0KB，均 ≤32KB ✅；WAITING=1。
  > 📦 **[已归档] #508 流水（2026-10-17 ~19:20, 🩺 v2 监控 step3190 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step3190 健康, s/step≈11.90s, ETA~55.5h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
  > 📦 **[已归档] #506 流水（2026-10-17 ~18:46, 🩺 v2 监控 step3020 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step3020 健康, s/step≈11.91s, ETA~56.1h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
  > 📦 **[已归档] #505 流水（2026-10-17 ~18:11, 🩺 v2 监控 step2840 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step2840 健康, s/step≈11.96s, ETA~56.9h→10-20 03:0x, step_2000 ckpt 续跑无崩溃。需要时再读。**
  > 📦 **[已归档] #504 流水（2026-10-17 ~17:40, 🩺 v2 监控 step2680 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step2680 健康, s/step≈11.92s, ETA~57.3h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
  > 📦 **[已归档] #503 流水（2026-10-17 ~17:37, 🩺 v2 监控 step2674 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step2674 健康, s/step≈11.90s, ETA~57.2h→10-20 02:5x, step_2000 ckpt 续跑无崩溃。需要时再读。**
  > 📦 **[已归档] #497 流水（2026-10-17 ~15:14, 🩺 v2 监控 step1955 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step1955 健康, s/step≈11.92s, ETA~59.7h→10-20 02:5x, .12=vision占用。需要时再读。**
  > 📦 **[已归档] #496 流水（2026-10-17 ~14:45, 🩺 v2 监控 step1804 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step1804 健康, s/step≈11.92s, ETA~60.2h→10-20 02:5x。需要时再读。**
  > 📦 **[已归档] #493 流水（2026-10-17 ~13:39, 🩺 v2 监控 step1470 + 续报 ETA）→ daily-memories/2026-10-17.md；结论：step1470 健康, s/step≈11.92s, ETA~61.3h→10-20 03:0x。需要时再读。**
  > 📦 **[已归档] #481 流水（2026-10-17 ~06:14, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step1470 loss1.6829 tok/s297.9K 健康, et=293.3min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #480 流水（2026-10-17 ~05:01, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step1110 loss1.8341 tok/s297.6K 健康, et=221.7min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #477 流水（2026-10-17 ~03:52, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step760 loss1.8031 lr1.42e-3 tok/s297.1K 健康, et=152min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #475 流水（2026-10-17 ~03:20, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step600 loss1.967 tok/s296.7K 健康, et=122min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #474 流水（2026-10-17 ~02:48, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step440 loss2.0914 tok/s296.1K 健康, et=88min 无崩溃环。需要时再读。**
  > 📦 **[已归档] #472 流水（2026-10-17 ~02:16, 🩺 v2 训练监控）→ daily-memories/2026-10-17.md；结论：step280 loss2.11 tok/s294.9K 健康, et=57min 无崩溃环。需要时再读。**

## 🗣️ 运维问答 · 2026-10-09（补测对比报告 · 先报后跑门控）

> **运维令**：补测 + 中文对比报告：BaiZe-Hybrid 2.220B ⚔ 参数匹配 Dense Llama，SGLang，ctx 持续 ×2 直到 hybrid OOM。门控：先报「参数匹配方案 + 测试矩阵 + ETA + 占用卡」，再开跑。

### ① 参数匹配方案

**主对手臂 = Dense Llama 36L（随机初始化）**
- 构建：复用 `p3_dense`（MiniCPM5-2B, 42L）的架构配置，**仅减层数 42→36**，使总参数对齐 hybrid。
- 架构配置（`config.json` 将照此生成）：

| 参数 | 值 | 来源 |
|:--|:--|:--|
| `architectures` | `LlamaForCausalLM` | 标准 Llama |
| `vocab_size` | 129,408 | 与 hybrid/dense 同 tokenizer |
| `hidden_size` | 2,048 | 同 p3_dense |
| `intermediate_size` | 6,144 | 同 p3_dense（SwiGLU 3×H） |
| `num_hidden_layers` | **36**（从 42 减 6） | 调此值对齐参数 |
| `num_attention_heads` | 16 | 同 p3_dense |
| `num_key_value_heads` | 2 | 同 p3_dense（GQA） |
| `head_dim` | 128 | 同 p3_dense |
| `hidden_act` | silu | SwiGLU |
| `tie_word_embeddings` | false | 同 p3_dense |
| `max_position_embeddings` | 4096 | 同 p3_dense（推理时 SGLANG_ALLOW_OVERWRITE 扩展） |
| `rope_theta` | 5,000,000.0 | 同 p3_dense |

- **精确参数量**（Python 实算）：
  - Embedding: 129,408 × 2,048 = 265,090,048
  - LM head: 265,090,048（不 tie）
  - 每层 attn: q 4,194,304 + k 524,288 + v 524,288 + o 4,194,304 = 9,437,184
  - 每层 MLP: 3 × 2,048 × 6,144 = 37,748,736
  - 每层 norms: 2 × 2,048 = 4,096
  - 每层合计: 47,190,016
  - 36 层: 1,698,840,576
  - Final norm: 2,048
  - **总计: 2,228,897,792 = 2.229B**
  - **vs hybrid 2,220,268,032 = +0.389%（±1% 内 ✅）**
- ⚠️ **权重随机初始化**（`torch.randn` × `initializer_range=0.02`）—— 本次比的是**速度/显存**，与权重值无关；报告中将显式标注。
- tokenizer 文件直接复制 `p3_dense`（同 vocab=129,408）。

**参考臂 = p3_dense（MiniCPM5-2B, 2.512B, 42L）**：附录/脚注用，佐证「未做参数匹配时偏袒 dense 约 +13% 参数」。

**备选方案（若运维要求更紧匹配）**：L=35, kv_heads=4（匹配 hybrid 的 4 KV heads）→ 2,218,407,936 = −0.084%。但 KV cache 翻倍（kv=4 vs kv=2）会使 dense 更早 OOM，可能不是「公平」的解读。

### ② 测试矩阵

| 维度 | 取值 | 说明 |
|:--|:--|:--|
| **模型** | {hybrid 2.220B, **dense-matched 2.229B**, p3_dense 2.512B(ref)} | 主对比 = hybrid vs dense-matched |
| **ctx** | 128K→256K→512K→1M→2M→4M→8M（×2） | 持续 ×2 直到 **hybrid 自己 OOM** 才停 |
| **mem-frac** | {0.6, 0.85} | ≥0.6（旧 0.3 太低致 dense 假 OOM）；同 ctx 两臂同值 |
| **bs** | {1, 8} | 至少两档 |
| **gen_len** | 64 | 同 P-9.11 |
| **WARMUP** | 1 | 丢弃首请求（消除 CUDA kernel 编译冷启动） |
| **REPEATS** | 3（取 median） | 公平口径 |
| **per-B 归一化** | tok/s ÷ B | 报告中每格同时报原始和 per-B |

**SGLang flags（两臂一致，仅 hybrid 额外加 SSM dtype）**：
```
--mem-fraction-static {0.6|0.85}
--attention-backend flashinfer
--dtype bfloat16
--context-length {ctx}
--disable-radix-cache
SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
# hybrid 额外: --mamba-ssm-dtype float32
```
- 环境：`vllm` conda env（sglang 0.5.9），与训练 env 隔离。
- prompt 构造：tokenizer 精确计数（`len(tok(prompt))` = ctx − 128 safety margin），复用 `p911d_sglang_vram_bench.py` 的 `make_prompt_precise()`。
- 每格记录：prefill tok/s / TTFT / decode tok/s / e2e / 峰值 VRAM / pool tokens / prompt 实 token 数 / status(SERVED/OOM/TIMED_OUT)。

**已有数据可复用**：P-9.11-E 的 mem-frac=0.3 结果（`p911e_results/*.json`）作为**低 mem-frac 对照**附录，不作为主表数据（口径不同）。

**终止条件**：hybrid 在某 ctx × mem-frac 下 OOM/不可服务 → 该 mem-frac 的扫描到此 ctx 为止；但**另一 mem-frac 继续扫**直到也 OOM。两 mem-frac 都 OOM → 全停。

### ③ ETA

| 阶段 | 墙钟 | 说明 |
|:--|:--|:--|
| 创建随机 Dense 模型 | ~10 min | Python 脚本生成 config.json + safetensors + 复制 tokenizer |
| 128K–512K（3 ctx × 2 mf × 3 model × 2 bs） | ~1–2h | 低 ctx 每格 <1min，4–6 GPU 并行 |
| 1M（2 mf × 3 model × 2 bs） | ~1–2h | hybrid 1M prefill ~7min/req，dense 可能 OOM |
| 2M（2 mf × 2 model × 2 bs） | ~2–3h | hybrid 2M ~30min/req（P-9.11-F TTFT=427s@mf0.6） |
| 4M–8M（若 hybrid 存活） | ~2–3h | 4M 已知 TIMED OUT@mf0.85；8M 可能不可服务 |
| **合计** | **~6–10h** | 可跨多个唤醒分阶段完成 |

### ④ 占用卡

- **.29 GPU 0–7**（8×H100 80GB），**纯推理**（无训练、无重 I/O）。
- 同时活跃 2–4 个 SGLang server（每个占 1 GPU），其余 GPU 空闲。
- 🚫 不碰 .12（vision 节点）。
- 🚫 不启动 P-8、不改 P-5b recipe、不 kill watchdog。

### ⑤ Warmup 24× 归因（证据）

- **现象**：P-9.11-E hybrid 128K bs=1 prefill=1,591 tok/s（TTFT=79.1s）vs bs=8 prefill=447,796 tok/s（TTFT=2.25s）→ **281× 差距**。
- **归因**：bs=1 是 server 启动后**第一个请求** → SGLang/flashinfer 首次执行时触发 CUDA kernel JIT 编译 + cuBLAS handle 初始化 + memory pool 首次分配 → **冷启动开销 ~77s**。bs=8 紧随其后，kernel 已编译 → 正常速度。
- **证据**：(a) 2M ctx 的结果（`p911e_hybrid_ctx2097152_gpu5.json`）TTFT=8.49s/prefill=237,575 tok/s → 比 128K bs=1 快 150× → **不是 ctx 越大越慢**，而是首请求冷启动；(b) dense 128K bs=1 TTFT=23.97s 也偏慢（但比 hybrid 好，因 dense 无 SSM kernel 需编译）。
- **修正**：本次 **WARMUP=1** 丢弃首请求 → REPEATS=3 均为 warm 状态 → 消除冷启动偏差。旧 P-9.11-E 的 bs=1 数据**不应作为公平对比基线**（无 warmup）。

### ⑥ 下一步（等运维确认后执行）

1. 创建随机初始化 Dense Llama 36L → `hf_checkpoints/dense_matched_2.22b/`
2. 落地 SGLang 基准脚本（复用 `p911d_sglang_vram_bench.py`，加 WARMUP/REPEATS）
3. 分阶段跑：先 128K–512K（快速验证）→ 1M–2M → 4M+（直到 hybrid OOM）
4. 生成 `report_pretrain_baize_vs_dense_fair_zh.html`（中文，≤5 表，内联 SVG）

---

> 📦 **[已归档] 🗣️ 运维问答「提 3 个实验 idea」（2026-10-09, #251 已交付）→ daily-memories/2026-10-09.md；结论：3 idea 按价值排序（①P-8彩排续跑 ②P-8 44B下限档 ③R3配比迁移A/B），建议「立即起P-8」。需要时再读。**

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- transformer_engine 2.12.0+5671fd36 / torch 2.8.0+cu128 / CUDA 12.8 / megatron-core 0.16.1 / mamba-ssm 2.2.6.post3（P-9.4 已核实，与任务书预期一致）。
- 结果主文件：R2=`EXPERIMENTS_PRETRAIN_2B_ROUND2.md`；Round1=`EXPERIMENTS_PRETRAIN_2B.md` + `BAIZE_PRETRAIN_RESULT.html` + `ISEDA2027/4_llm_pretrain.tex`。
- ckpt：p3_hybrid/iter_0005000 → **HF nemotron_h ✅**（`nemo_experiments/p3_hybrid/hf_iter_5000/`，323 keys, 2.220B）+ p3_dense/iter_0005000 → **HF Llama ✅**（`nemo_experiments/p3_dense/hf_iter_5000/`，381 keys, 2.512B）；原始 mcore distcp @ `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`。

## GPU / 进程
- 主训练 10.239.2.29（8×H100 GPU0~7）：P-5b ✅ 已结束；P-9.1~P-9.7 全 ✅ 定稿；P-9.8 ✅ / P-9.9 ✅ / P-9.10 ①②③ ✅ / **P-5b 8-set eval ✅ COMPLETE**（GPU0-1 已释放）；**⭐ 全 8 GPU 空闲**（data agent @08:06 kill S0a → GPU2-7 释放；proxy 标定尚未起跑）；**P-9.11 ① HF 转换 ✅ BOTH DONE**（p3_hybrid→nemotron_h + p3_dense→Llama，待 sglang 起服）。
- watchdog `baize_pretrain_loop.sh` PID 1391466 必须 7×24 存续，🚫 绝不 kill。
- P-9（P-9.1 ✅ / P-9.2 ✅ / P-9.3 ✅ / P-9.4 ✅ / **P-9.5 ✅ COMPLETE** — 崩溃修复 + 5-way 归因 + HTML / P-9.6①② ✅ / P-9.7 ✅ / P-9.8 ✅ COMPLETE → delayed FP8 可用于 P-8 / **P-9.9 ✅ COMPLETE → tensorwise T1/T4 FAIL → P-8 沿用 delayed** / **P-9.10 ① ✅ sglang ✅ 可用(vllm env) [第109次更正] → eager 下界✅已测 + sglang 上界待 HF 转换补测，② ✅ COMPLETE eager 下界 H1✅H2❌H3❌H4✅**）；🚫 不对 live 长跑做 nsys/ncu attach。
