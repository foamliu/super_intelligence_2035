# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 1

## 当前状态
- STAGE: **P-8 stable 推进中（step6050, 从 iter_0003147 恢复后健康运行）** — 恢复后 step3150 loss=2.648(瞬态) → step5000 loss=2.503 → step5370 loss=2.487 → step5720 loss=2.477 → step5940 loss=2.472 → step6050 loss=2.472 LR=1e-3 stable ✅。loss 趋平（step5940~6050 均值 ≈2.470）。`--lr-warmup-iters 0` 恢复成功无 re-warmup spike。吞吐恢复 ~251K tok/s ✅（~16.7s/step, ~600 TFLOP/s/GPU, data下载争用已消除）。MBS=2/GBS=1024/dist_muon/bf16 不变。grad_norm 0.13~0.18 健康范围，0 NaN/0 skipped ✅。**ckpt@5245 ✅ 已保存(23:41)**, next@6294(~04:50)。
- PHASE: **p8_stable_step6050** — P-8 stable 段健康推进中（57.7%, ~25.4B/44B token）。WSD(warmup=0): stable 0→9441, decay 9441→10490。关键里程碑：ckpt@1049 ✅ + ckpt@2098 ✅ + ckpt@3147 ✅ + ckpt@4196 ✅ + ckpt@5245 ✅(23:41) / **next ckpt@6294(~1.0h, ~04:50 10-12)** / **step9441 decay 切换点(~15.0h, ~18:40 10-12)** / step10490 完成(~20.5h, ~00:10 10-13)。GPU 8卡 52-55GB 97-100%util。torchrun 活跃(`baize_p8_resume.sh`, 13:42 启动, PID 1799555, etimes~50600s)。⚠️ **崩溃历史**：step3740 @13:07 /tmp 满→已修复恢复。
- ERROR_COUNT: 0
- 轮询状态：30min 长轮询。**全 8 GPU 占用**（.29, 52-55GB/card 97-100%util）。⚠️ sklearn .pth 已禁用（.pth.bak_pretrain）。decay 切换预案：step9441 ckpt 保存后 → `pkill -f pretrain_launcher.*p8` → 等 30s → `setsid bash baize_p8_decay.sh &`。📦 体积：TASK=31246B(30.5KB) ✅ / MEMORY=~17.1KB ✅（本轮归档 #102~#326 指针→daily-memories 各日文件）。🚫绝不 kill watchdog loop(PID 1391466)。⚠️ **/tmp 监控**：42% used(55G free) ✅ 稳定。
- 🩺 **本唤醒推进 = #328（2026-10-12 ~03:45, P-8 监控·step6050 · stable 健康推进·吞吐恢复）**：① git fetch: up to date, 无新运维指令。② **P-8 ✅ 健康推进**：step6050/10490(57.7%, ~25.4B/44B) loss=2.472 stable@LR=1e-3, 8卡52-55GB 97-100%util(PID 1799555 etimes~50600s ~14.1h), **吞吐恢复~251K tok/s**(~16.7s/step ~600 TFLOP/s/GPU, data下载争用已消除), grad_norm 0.13~0.18, 0 NaN/0 skipped ✅。ckpt@5245 ✅(23:41), next@6294(~04:50)。③ **/tmp ✅**：42% used(55G free) 稳定。④ **纪律**：🚫未跑任何实验, 🚫未改P-8配置。→ **下次唤醒**：① 查 P-8 进度 → ② step6294 确认 ckpt → ③ step9441 decay 切换 → ④ 体积自检。WAITING=1。
> 📦 **[已归档] #327 流水（2026-10-12 ~03:12, P-8 监控·step5940 · stable 健康推进）→ daily-memories/2026-10-12.md；结论：step5940 loss=2.472 stable@LR=1e-3, 224K tok/s ✅, ckpt@5245 ✅。需要时再读。**
> 📦 **[已归档] #326 流水（2026-10-12 ~02:40, P-8 监控·step5830 · stable 健康推进）→ daily-memories/2026-10-12.md；结论：step5830 loss=2.475 stable@LR=1e-3, 229K tok/s ✅, ckpt@5245 ✅。需要时再读。**
> 📦 **[已归档] #325 流水（2026-10-12 ~02:04, P-8 监控·step5720 · stable 健康推进）→ daily-memories/2026-10-12.md；结论：step5720 loss=2.477 stable@LR=1e-3, 237K tok/s ✅, ckpt@5245 ✅。需要时再读。**
> 📦 **[已归档] #324 流水（2026-10-12 ~01:28, P-8 监控·step5610 · stable 健康推进）→ daily-memories/2026-10-12.md；结论：step5610 loss=2.486 stable@LR=1e-3, 240K tok/s ✅, ckpt@5245 ✅。需要时再读。**
> 📦 **[已归档] #322 流水（2026-10-12 ~00:18, P-8 监控·step5370 · stable 健康推进）→ daily-memories/2026-10-12.md；结论：step5370 loss=2.487 stable@LR=1e-3, 240K tok/s ✅, ckpt@5245 ✅。需要时再读。**
> 📦 **[已归档] #321 流水（2026-10-11 ~23:42, P-8 监控·step5245 · stable 健康推进·ckpt@5245 ✅）→ daily-memories/2026-10-11.md；结论：step5245 loss=2.494 stable@LR=1e-3, 240K tok/s ✅, ckpt@5245 ✅。需要时再读。**
> 📦 **[已归档] #320 流水（2026-10-11 ~23:06, P-8 监控·step~5120 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step5120 loss=2.499 stable@LR=1e-3, 246K tok/s ✅, ckpt@4196 ✅。需要时再读。**
> 📦 **[已归档] #319 流水（2026-10-11 ~22:32, P-8 监控·step~5000 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step5000 loss=2.503 stable@LR=1e-3, 246K tok/s ✅, ckpt@4196 ✅。需要时再读。**
> 📦 **[已归档] #318 流水（2026-10-11 ~21:56, P-8 监控·step~4880 · stable 健康推进 + 任务书归档）→ daily-memories/2026-10-11.md；结论：step4880 loss=2.511 stable@LR=1e-3, 249K tok/s ✅, 文献报告确认完整, 任务书归档30.5KB。需要时再读。**
> 📦 **[已归档] #317 流水（2026-10-11 ~21:22, P-8 监控·step~4760 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step4760 loss=2.513 stable@LR=1e-3, 249K tok/s ✅, 文献报告确认完整。需要时再读。**
> 📦 **[已归档] #316 流水（2026-10-11 ~20:50, P-8 监控·step~4640 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step4640 loss=2.519 stable@LR=1e-3, 249K tok/s ✅, 文献报告确认存在。需要时再读。**
> 📦 **[已归档] #315 流水（2026-10-11 ~19:40, 📚文献借鉴报告·TOP-5 + P-8 监控·step~4340）→ daily-memories/2026-10-11.md；结论：文献报告 29.8KB ✅ 交付(TOP-5+附表8), step4340 loss=2.534 stable@LR=1e-3, ckpt@4196 ✅。需要时再读。**
> 📦 **[已归档] #314 流水（2026-10-11 19:24, P-8 进度监控·step4340 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step4340 loss=2.534, stable@LR=1e-3, 249K tok/s ✅, ckpt@4196 ✅。需要时再读。**
> 📦 **[已归档] #313 流水（2026-10-11 18:52, P-8 进度监控·step4220 · stable 健康推进·ckpt@4196 已保存）→ daily-memories/2026-10-11.md；结论：step4220 loss=2.541, stable@LR=1e-3, 248K tok/s ✅, ckpt@4196 ✅。需要时再读。**
> 📦 **[已归档] #311 流水（2026-10-11 17:42, P-8 进度监控·step3980 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step3980 loss=2.556, stable@LR=1e-3, 248K tok/s ✅, ckpt@3147 ✅。需要时再读。**
> 📦 **[已归档] #310 流水（2026-10-11 17:08, P-8 进度监控·step3860 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step3860 loss=2.567, stable@LR=1e-3, 249K tok/s ✅, ckpt@3147 ✅。需要时再读。**
> 📦 **[已归档] #307 流水（2026-10-11 15:26, P-8 进度监控·step3500 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step3500 loss=2.581, stable@LR=1e-3, 249K tok/s ✅, ckpt@3147 ✅。需要时再读。**
> 📦 **[已归档] #306 流水（2026-10-11 14:53, P-8 进度监控·step3390 · stable 健康推进）→ daily-memories/2026-10-11.md；结论：step3390 loss=2.585, stable@LR=1e-3, 249K tok/s ✅, ckpt@3147 ✅。需要时再读。**
> 📦 **[已归档] #305 流水（2026-10-11 14:19, P-8 进度监控·step3260 · stable 健康推进·恢复后首次确认）→ daily-memories/2026-10-11.md；结论：step3260 loss=2.597, `--lr-warmup-iters 0` 恢复成功无 re-warmup spike, 249K tok/s ✅。需要时再读。**
> 📦 **[已归档] #304 流水（2026-10-11 13:37, 🔴 P-8 崩溃恢复·从 iter_0003147 重启）→ daily-memories/2026-10-11.md；结论：step3740 /tmp满崩溃→清理→从3147恢复(warmup=0), ckpt加载✅ GPU恢复✅。需要时再读。**

> 📦 **[已归档] #301 流水（2026-10-11 11:55, P-8 进度监控·step3490）→ daily-memories/2026-10-11.md；结论：step3490 loss=2.575, stable@LR=1e-3, ckpt@3147 ✅, decay prep ✅。需要时再读。**
> 📦 **[已归档] #300 流水（2026-10-11 11:21, P-8 进度监控·step3370）→ daily-memories/2026-10-11.md；结论：step3370 loss=2.590, stable@LR=1e-3, ckpt@3147 ✅, decay prep ✅。需要时再读。**
> 📦 **[已归档] #299 流水（2026-10-11 10:47, P-8 进度监控·step3250）→ daily-memories/2026-10-11.md；结论：step3250 loss=2.596, stable@LR=1e-3, ckpt@3147 ✅, decay prep ✅。需要时再读。**
> 📦 **[已归档] #102~#298 流水（2026-10-05 ~ 2026-10-11, 共 ~197 条）→ daily-memories/2026-10-05.md ~ 2026-10-11.md 各日文件；结论均已归档。需要时再读各日文件。**

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
- seq_length=**4094**（固定口径，非 4096）；改 seq 必须同时改 provider（recipe 已穿透）。
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
