# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🆕 运维指令 · 2026-10-23 22:1x（**优化 BaiZe-2B 训练吞吐：目标 > 249K tok/s**）· 用户直令 · 最高优先

> 用户原话：「pretrain：尝试各种方法优化 BaiZe-2B 的训练吞吐 目前最大值是 249K tok/sec，想办法超过这个值。」

**① 基线口径（先钉住，后面所有对比都靠它）**
- 用**当前已知最优配置**复跑 1 次基线：warmup ≥20 step 后取 **≥50 step 稳态**的 `tok/s`（中位数，别取峰值）+ 峰值显存 + s/step + grad_norm + loss。
- 记录到 `MEMORY_PRETRAIN_2B.md`：**baseline = 249K tok/s @ <配置指纹>**（TP/PP/DP、MBS×accum、GBS、seq_len、FP8 开否、compile 开否、模型并行组合）。**之后每次实验只改 1 个变量。**

**② 候选优化轴（按性价比顺序推进，逐条试，别一次改俩）**
1. **FP8 配方**：blockwise vs tensorwise scaling；first/last layer 排除 FP8；`--fp8-amax-history-len`/`amax-epsilon` 微调。
2. **计算图**：`torch.compile`（`--use-torch-compile` / fullgraph）· **CUDA graphs** · `--use-flash-attn-v3` · TransformerEngine 融合算子（LayerNorm/RoPE/SwiGLU）。
3. **并行度**：TP ∈ {1,2,4,8} × **SP** 开关；`--sequence-parallel`；DP/ZeRO-1（`--use-distributed-optimizer`）；`--overlap-grad-reduce` / `--overlap-param-gather`。
4. **批次**：MBS × accum 网格（固定 GBS），找 **tokens/step 最大且不 OOM** 的点；显存够就把 activation recompute 关掉。
5. **数据侧**：bin 读取预取 / `num_workers` / mmap / 避免 host 侧成瓶颈（`nproc`、`OMP_NUM_THREADS`、pin memory）。
6. **通信**：`NCCL_ALGO`/`NCCL_PROTO`/NVLink 亲和、`NCCL_IB_DISABLE`、网卡绑定（8 卡单机优先 P2P）。
7. **其它**：fused Adam / emerging-optimizers 的 fused 版、loss 计算融合、`--seq-length` 与 packed 序列对齐（避免 padding 浪费）。

**③ 每轮实验协议（严格，防「跑快了但训坏了」）**
- 单次实验 **≥50 step 稳态**（warmup 20 步不计），单次总时长 **≤30min**，**每改一个变量就 commit 一次**。
- 必须同时记录：**tok/s（中位数）/ 峰值显存 / s/step / grad_norm / 前 200 步 loss**。
- **正确性闸门**：与基线相比，同 step 的 loss 偏差 **≤5%**、`grad_norm` 无数量级跳变、**0 NaN/inf**；任一不满足 ⇒ 该配置判「快但不可用」，只记录不采用。
- OOM / 卡死 ⇒ 记下配置即放弃，🚫 不反复调参死磕。

**④ 交付**
- **至少 8 个候选**跑完（总量 ≤6h，分多轮唤醒做，每轮做完先落盘再继续）。
- 产出一张表（配置指纹 × tok/s × 相对基线增益 × 显存 × 是否通过正确性闸门）写进 `MEMORY_PRETRAIN_2B.md`，并生成中文 HTML：`reports/report_pretrain_2b_throughput_optim_zh.html`（自包含；含基线复现命令、每个候选的命令与数字、结论与「下一步还能挖什么」）。
- **超过 249K 就明确写「新纪录 = X K tok/s（+Y%）@ <配置>」**；若全都超不过，也要给「瓶颈归因」（算力/通信/数据/显存）+ 2–3 个更激进方案（如换并行度到头、换 attention 实现、改 GBS/seq）。
- commit 前缀 `pretrain perf:`。

**⑤ 纪律**：只在 **`.29` 8×H100** 上做；🚫 不碰 `.12`（vision 训练中）/ data / harness；每个数字必须能追到 log 或脚本输出；🚫 编造 tok/s。

### 🧪 运维指令 · 2026-10-23（**长上下文推理成本评测：BaiZe-2B / MiniCPM5-2B / Qwen3.5-2B**）· 用户直令 · 最高优先

> 用户原话：「pretrain：再做一次长上下文推理成本评测，对比模型 BaiZe-2B、MiniCPM5-2B、Qwen3.5-2B。推理框架统一用SGLang，上下文长度从64K开始翻倍，直到全部OOM。实验后写实验报告（中文HTML），列表对比各模型显存、推理速度等详细信息。」

**① 三个模型（报告须写明各自 HF 版本/commit + 参数量 + 架构）**
- **BaiZe-2B**（自有）：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/Xmodel-2.5-code/out/decay_5000_hf`（XmodelForCausalLM，即 decay-5000 产物）。
- **MiniCPM5-2B**：`openbmb/MiniCPM5-2B`（Llama 架构，max_pos 131072）—— 无权重先 HF 下载（工作目录已有 `MiniCPM5-2B.config.json` 可作参考）。
- **Qwen3.5-2B**：Qwen3.5 系列 2B —— 无权重先 HF 下载（本机现只有 Qwen3.5-4B / Qwen3-VL-2B 等，缺纯文本 2B）。

**② 评测方法（统一 SGLang）**
- 框架**统一 SGLang**（勿混 vllm）；每模型独立起服、独立测。
- 上下文长度**从 64K 翻倍**：64K → 128K → 256K → 512K → 1M → 2M → …，**直到该模型 OOM**（记录 OOM 点 = 实测上下文上限）。
- 每档记录（列表可溯源）：
  - **显存**：峰值/稳态 VRAM(GB)、KV cache 占用；
  - **推理速度**：prefill 吞吐(tok/s)、decode 速度(tok/s)、端到端延时；
  - **成功/OOM**。
- 复用/参考 `run/` 下既有 SGLang 长上下文脚本（`benchmark_p911_sglang.py`、`p911d_sglang_vram_bench.py`、`start_sglang_*.sh` 等），不足再新建。

**③ 报告（中文 HTML）**
- `reports/report_pretrain_longctx_infer_cost_3x2b_zh.html`（自包含）。
- **对比表**：三模型 × 各上下文档 的显存/速度/延时/OOM 点；突出「最大可服务上下文长度」与「同长度最快的模型」。
- 附：实验环境（GPU/驱动/SGLang 版本）、每模型复现命令、结论与建议。commit `pretrain eval:`。

**④ 纪律**：评测在 .29（8×H100 已空）；🚫 不碰 vision(.12)/data/harness；每个数字溯源到脚本输出/log；不伪造。

### 📄 运维指令 · 2026-10-23（**写 decay 修复完整中文 HTML 报告 + 下一步建议**）· 用户直令 · 最高优先

> 用户原话：「pretrain：写个HTML中文报告，包含对下一步实验的建议。」

**报告文件**：`reports/report_pretrain_decay_repair_zh.html`（自包含中文 HTML，内联样式、无外链/无脚本）。

**① 内容主线（decay「训坏 → 修复」全历程）**
1. **decay v2（自写脚本 · 失败）**：71.2B decay → CS8 **44.97%** / CX6 **6.21%**，vs Xmodel-2.5 官方 final 65.40%/32.90%（Δ **−20.43 / −26.69pp**）→ 判定「decay 训坏」。
2. **归因**：双移位 bug（py:547-548 + 567-568 双重移位）、peak LR 1.67e-3 过高、自写脚本缺 **μP**、code 过采样、step0 loss 11.72 异常。
3. **排查实验（自写脚本）**：L1（修双移位+LR5e-4+warmup100）→ CS8 **59.03%**；L2（只修双移位+高LR）被直令 kill 转官方方案。
4. **decay-5000（官方 1113.sh · 修复）**：官方 `train_decay_fp8_1113.sh`（use-mup + **Muon 0.2** + FP8 hybrid + 无 warmup + MBS=5 + WSD exponential 5000 步）→ **CS8 58.97% / CX6 28.02%**，vs 旧 decay v2 **+14.0 / +21.8pp**，vs 起点基线 61.03%（Δ −2.06pp）。
5. **结论**：官方 μP+Muon+FP8 修复了 decay 训坏，能力基本回到起点；残余 gap 归因写入。

**② 下一步建议（必写，给 ≥3 个候选，按价值排序，各附预期成本/风险/ETA）**
1. **延长 decay**：5000 → 20000 步（对齐官方 71.2B），看 CS8 是否逼近 65.40%（成本 ~3× 当前 GPU 时）。
2. **对齐数据配比**：官方 1113.sh 的 11 源配比（当前仅 4 源 64/24/8/4），隔离数据贡献。
3. 其他（可选）：min-lr / decay-iters 微调、更长 warmup、或更大 decay 数据量。

**③ 纪律**：对比口径统一用 Xmodel-2.5 官方 final（65.40%/32.90%）+ 起点基线 61.03%，**不用 P-8 作主对照**；数字溯源 `eval_summary.txt`/各 log；commit `pretrain report:`。

### 🆕 运维指令 · 2026-10-22 13:5x（**decay 5000 步 + 复用官方 MBS=5 排障**）· 用户直令 · 最高优先 · 覆盖 08:5x 的 train-iters/decay-iters/MBS 口径

> 用户原话要点：① 训练效率不高，为何不能复用官方脚本（MBS=5、FP8 等）；② decay steps 设 **5000 步取整**；③ 用下方指定 LR/decay 参数；④ 用 Muon（0.2）；⑤ 不用 warmup。

**① decay = 5000 步**：`--train-iters 5000`（≈18.1B token，取整接受）；`--lr-decay-iters 5000` + `--lr-wsd-decay-iters 5000`（覆盖之前 5560 / 20000）。

**② LR / decay / optimizer 参数（照抄，勿改）**：
```
--lr 1.66667e-3
--decoupled-lr 1e-2
--lr-decay-style WSD
--lr-wsd-decay-style exponential
--min-lr 1.041667e-4
--decoupled-min-lr 6.25e-4
--lr-decay-iters 5000
--lr-wsd-decay-iters 5000
--lr-warmup-iters 0
--optimizer muon
--muon-matched-adamw-rms 0.2
```

**③ MBS 复用官方 5（先排障，勿懒省事降 2）**：官方 1113.sh 就是 MBS=5/GBS=960/seq3776/FP8 hybrid 跑 8×H100-80GB；我们 MBS=5 仅报 ~81GB（超 ~1GB）。**先排查根因再谈降 MBS**：
- 检查缺 activation recompute（Megatron `--recompute-granularity selective|full`、`--recompute-method uniform`、`--recompute-num-layers`）；
- 检查 FP8 TE 的 amax/history buffer 与 distributed-optimizer 的显存占比；
- 优先靠「开 recompute / 关冗余 buffer」腾出 1–2GB 保住 MBS=5；**仅在 80GB 内确实无法跑通时才降 MBS**，并在报告写明降级原因与可行区间（如 4）。

**④ 其余**：配置沿用 1113.sh（use-mup/muon/FP8 hybrid/TP1 PP1 DP8/distributed-optimizer/tokenizer dsv3），`--load` 转换后 ckpt、`--finetune`。commit `pretrain decay:`。

### 🆕 运维指令 · 2026-10-22 08:5x（**decay 参考官方 train_decay_fp8_1113.sh + 20B 数据**）· 用户直令 · 最高优先

> 用户原话：「pretrain 的 xmodel decay 参考这个 https://github.com/XiaoduoAILab/Xmodel-2.5/blob/main/examples/xmodel/train_decay_fp8_1113.sh，使用20B数据」

**① 参考脚本（官方 `examples/xmodel/train_decay_fp8_1113.sh`，已核内容，照此落地，勿用自写脚本）**
- 模型：48L / hidden1536 / 24head / GQA8 / ffn3840 / rope / swiglu / RMSNorm / **use-mup（12.0 / 1.0 / 1.4 / 1.4）**
- 训练：GBS **960** / MBS 5 / seq **3776** / **optimizer muon**（muon-matched-adamw-rms 0.2）/ lr **1.66667e-3**（decoupled 1e-2）/ min-lr 1.04e-4 / **WSD** exponential / **lr-decay-iters 20000** / warmup 0 / wd 0.1 / clip 1.0 / bf16
- FP8：`--transformer-impl transformer_engine` / fp8-format hybrid / amax-history 128 / amax-compute-algo max
- 并行：TP1/PP1 纯 DP8 + `--use-distributed-optimizer` + overlap-grad-reduce/param-gather
- tokenizer deepseekv3 / vocab 129280

**② 数据量 = 20B**：`--train-iters` 重算 = 20e9 / (960 × 3776) ≈ **5560 步**（覆盖脚本原 550000）；decay 从起点 step_532000 ckpt 加载（HF→Megatron 转换后）。

**③ 前置（顺序）**：① 起点 HF ckpt → Megatron 转换（官方 convert.py + loader）；② DATA_PATH 用 `full_*` 6 源权重（若实测 0 shard 立即定位，报差异）；③ 100 步冒烟确认 loss 接得住 stable 末点 → 再起 20B decay。

**④ 纪律**：不抢 .12；每轮报 step/loss/0error；commit `pretrain decay:`；若此前 A 方案 1120.sh 与 1113.sh 冲突，**以 1113 为准**。⚠️ 写入前先归档旧闭合块，保证 TASK ≤ 32KB。

> 📦 §2026-10-09:3x（写两份中文 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：两份报告已交付（v2_result + short_experiment, commit c44ef1fea）。需要时再读。

> 📦 §2026-10-02:3x（授权自主排查根因）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：L1 CS8=59.03% / L2 kill@step2370 / L3 作废，方向转 A方案官方 Megatron。需要时再读。

> 📦 §2026-10-21:5x（decay v2 对照口径纠错）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 CS8=44.97% vs 官方 65.40% Δ−20.43pp，起点 61.03%⇒decay 训坏。需要时再读。

> 📦 §2026-10-14:2x（评测 decay v2 final）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：14集eval CS8=44.97%/CX6=6.21%，报告已交付。需要时再读。

> 📦 §2026-10-06:1x（事故复盘报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：crash@02:45 NCCL timeout→resume step_18000→收尾，P0-a/b 已落地，硬件=transient。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

> 📦 §2026-10-16:4x（#548 误判更正）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#548 误判根因=NFS 旧日志，判活规则已修正。需要时再读。

> 📦 §2026-10-16:2x（P0 resume + 长期授权）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 resume 闭环，长期授权训练挂了自行重启。需要时再读。


> 📦 §2026-10-17 两块（P0 中继抢修 / `_orig_mod` 崩溃修复）均已闭合 → 原文已在 `daily-memories/2026-10-17.md`；结论：中继 PID2706247 健康（RUN_ID118-122 exit=0）；`_orig_mod` 修复验证通过，断点续跑至 6890/19980 无崩。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）
> 📦 已归档（R3配比 / LaTeX / R2收官 / T3）→ `ARCHIVE_OPERATOR_PRETRAIN.md`。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）原文搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` / `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）/ `daily-memories/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `pretrain 归档: …` 前缀。
> 本轮动作：本任务书现 ≈40KB（已过 40KB 红线）⇒ 下次唤醒先归档到 ≤32KB，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_PRETRAIN.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_PRETRAIN.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_PRETRAIN_2B.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B.md \
              doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/daily-memories
   git commit -m "pretrain #<轮次>: <一句话>"   # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

> 📦 §2026-10-05（3项：sglang上界+对比+环境）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；结论：sglang vllm env 可用(0.5.9), proxy=172.19.92.25:13128, P-9.11 prefill 2.18×, 128K failed。需要时再读。
### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_PRETRAIN_2B_TASK.md` ≈ 38KB、`MEMORY_PRETRAIN_2B.md` ≈ 14KB。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` 等；
  ④ 较早的唤醒流水（保留最近 ~20 条） → `daily-memories/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 /「进度快照」③ 最近 ~20 条流水。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变（正文/流水/快照里不得再出现以 `WAITING:` 开头的行）。

---



# ══════════════ ROUND 2 · 现行部分（只保留仍未完成/仍有效的）══════════════

> R2.0/R2.1/R2.2 清单 · R9.0-bis · P-4R · P-5a 与 Round 1（S0–S5） 均已完成并归档 →
> `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md`（需要时再去读，不要把整份读进上下文）。

> 📦 §P-6 lm_eval 8集+scaling law（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；结论：P-6① Avg=0.4395@655M, P-6② 48/48 runs Avg 33.26%→49.22% R²=0.986, 55%→~55B tok. 需要时再读。
> 📦 §P-7 训练吞吐核查（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；结论： dense +8% (not +24%), hybrid 85.6K vs dense 89.7K. 需要时再读。

> 📦 §P-8 细节 + R2.3 交付物（P-8 已完成：10590步/44.4B tok/final loss 1.357）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-8 AdamW 44.4B 训练完成，14集eval CS8=49.21%/CX=6.81%，ckpt@iter_1149 已保存。需要时再读。

## R2.4 约束

- 总预算（分三档）：
  - P-1 / P-2 / P-3 / P-4 / P-6 / P-7：短程实验，≤ 5 小时墙钟（P-6 视加载路径难度可到 6 h；P-7 ≤1h）。
  - ⭐ P-5 是独立长任务，≤ 8 天墙钟（P-5a 4–5 h + P-5b 20B token ≈ 2.5 天；预算允许可延到 60B ≈ 7.5 天）。
  - 超时按 P-5a > P-6 第 1 步（现有 ckpt 的 8 集）> P-1/P-2 > P-4 > P-5b > P-6 第 2 步 逆序裁剪，并在报告记录裁剪决策。
- GPU：只用 `10.239.2.29` 的 GPU 0–7（8 卡）。绝不杀他人进程。
  ⚠️ 另有 vision 任务在 `10.239.2.12`（另一台机器）跑——与你无关，不要去动那台。
- 每次启动训练前后都要记录 GPU 占用核验结果（`nvidia-smi --query-compute-apps=...`）。
- ⚠️ NFS 与 vision 任务共享（重要）：两台 GPU 节点用的是同一块 `/nas_train` 盘。
  vision 任务的 R2-4 需要"无争用的干净吞吐测量"，而你启动训练同样会打这块盘。
  → 启动 P-1 之前，先读 `run/MEMORY_VISION.md`（共享盘，你直接可见）看它的 R2 进度：
  - 若 R2-4 尚未完成：先做不占 GPU 的准备工作（代码/数据核对、P-3 的 Round 1 基线复核、脚本落地），
    每轮唤醒重查一次它的进度；
  - 最多等 2 小时；超过 2 小时则照常启动 P-1，并在报告里注明"当时 vision 任务在并发"。
  → 你的每次测量都要记录"当时 vision 任务在跑什么"。
- 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；
  P-3 若需更长的数据覆盖，先核对再启动，不要中途断数据。
- 收尾不杀 loop（关键）：R2 的 P-1/P-2/P-3 全部完成（或按预算裁剪到只剩需等待的项）后，把结果写进报告并 git push，然后停在原地：`MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（30 分钟长轮询）；🚫 绝不 kill / pkill `baize_pretrain_loop.sh`。loop 必须持续运行，以便运维远程下发新任务（会改写本任务书，下次唤醒即按新指令执行）。

---



> ⚠️ 本文件为只读指令文件，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（必读，2026-10-01 新增，每次唤醒都要走）

### 前提：这是一个共享工作副本

vision 任务的 agent 与本任务共用同一份工作副本——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

因此：
- 只需一个人 pull，另一个立刻看到：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。
  不要重复 pull，也不要因为"工作区里出现了别的任务的改动"而困惑。
- 工作区里陌生的未提交改动很可能是 vision 任务的在途文件。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 两个 loop 每 5 小时各自 `git add -A && commit && push`，会互相把对方在途的文件一起提交。
  这是既有设计的已知副作用，不要试图"修正"它。

### 但 loop 本身只 push 不 pull

`baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。
一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。
所以 pull 必须由你（agent）来做。

每次唤醒按顺序执行：

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. 提交时显式指定你自己的文件：
   `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`
   🚫 不要用 `git add -A`——那会把 vision 任务的在途文件卷进你的提交。
3. 若显示 behind / diverged：`git pull --rebase origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是双方的在途改动：
     先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → 另一个 agent 正在做 git 操作：
     等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并跳过本次 git 操作，下次唤醒再试。
   - 🚫 绝不 `git push --force`；🚫 绝不 `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind 才算闭环。
5. 流水记一行 git 结果（沿用你已有格式）。

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——沿用同一做法。

---


---

