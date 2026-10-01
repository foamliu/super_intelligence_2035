# BAIZE_PRETRAIN_2B_TASK.md
# ══════════════ ROUND 2 · 第二轮任务（2026-10-01 生效，**优先于下方 Round 1**）══════════════

## 🚫 铁律（最高优先级，先于本文件一切指令）

- **无论任务是否收敛、是否还有剩余工作，一律绝对禁止 `kill` / `pkill` / `stop` `baize_pretrain_loop.sh`（即 watchdog loop）。**
- 任务收敛/完成后：只允许把 `MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（进入 30 分钟长轮询），然后**停在原地，让 watchdog 继续跑**。
- 🚫 **不得以「空转烧 token」之类的理由去 kill watchdog**——空转开销已由 `WAITING=1` 的 30 分钟长轮询兜底，属设计内行为。
- watchdog 必须 **7×24 持续运行**：运维会随时远程下发新任务（直接改写本任务书），下次唤醒即按新指令执行。

## R2.0 状态切换（**先做**）

**MODE 已从 Round 1 切换为 Round 2。你在 `MEMORY_PRETRAIN_2B.md` 里看到的
`PHASE=converged`、以及"04:03 已 kill `baize_pretrain_loop.sh`"的记录，均已作废——**
**loop 实际仍在运行（已被重新拉起），本任务重新有了工作。**

本唤醒请：
1. 在 `MEMORY_PRETRAIN_2B.md` 里把 `PHASE` 改为 `R2_active`，
   并把 `WAITING` 字段改为纯文本 `0`（**注意**：loop 的正则是 `WAITING:[* ]*1`，
   而你的流水里曾出现过 `WAITING: **1**` 这种散文，会**误触发 30 分钟长睡**——
   请确保**全文除状态字段外不再出现 `WAITING: *1` 字样**，否则本任务会被拖慢）。
2. 流水追加一条"R2 启动"。
3. **Round 1 的结论仍有效，作为 R2 的对照基线；不要重跑 S0–S5。**

## R2.1 为什么要做第二轮（结论需要加固的三处）

Round 1 的 S0–S5 已经收敛，但有三处**在论文里会被审稿人直接打**：

1. **LR 最优解落在网格边界上。** S2 扫了 `2e-4 … 1e-3` 七点，loss **单调改善到网格最大值 1e-3**——
   也就是说**真正的极小值可能在 1e-3 之上，而扫描从未覆盖它**。论文目前只写 "improves monotonically"，
   没交代"最优点在边界"，这是**过度声明**。
2. **Δ 小于噪声。** 论文写 `min_lr=1e-5 narrowly beats 3e-5`（2.7647 vs 2.7679，**Δ≈0.003**），
   但 3-seed 的 **σ≈0.0469** —— **Δ 比噪声小一个量级**。"narrowly beats" 站不住，
   要么补 seed 把 σ 压下来，要么如实写成 "within run-to-run noise"。
3. **架构选型的对比只跑了 1000 步 / 24.6M token**（GBS=6 的早期收敛快照），
   却支撑了论文里"hybrid 更优"的核心 claim。需要延长到与其它实验同口径的 **5000 步**。

## R2.2 实验清单（**保守包 P-1 / P-2 / P-3**，全部沿用 Round 1 的既有脚本与数据）

> 固定口径（除显式改动外，与 Round 1 一致）：8×H100 @ `10.239.2.29`、TP1/DP8、GBS=8、
> seq=4094、bf16、distributed AdamW(0.9,0.95,1e-5,wd0.1)、seed=1234、
> WSD warmup 250 / decay 500 / **min_lr 1e-5**、退火混合 L3(86%)+code(10%)+math(4%)。

> ## 🚦 执行顺序（**运维 2026-10-01 定，必须遵守**）
>
> **P-4 → P-7 → P-6（第 1 步）→ P-5b → P-8（完整训练）**
>
> - **P-6 第 2 步**（「能力 vs token」曲线）依赖 **P-5b 的 6 个 checkpoint**，故**放在 P-5b 之后**做。
> - **P-5b 的 loss-vs-tokens 曲线直接决定 P-8 的 token 预算** —— 这是把 P-5b 排在 P-8 前面的**唯一理由**。
> - ⚠️ **P-5b 一旦启动会独占 8 卡 ≈2.5 天**（到 60B 则 ≈7.5 天）→ **P-4 / P-7 / P-6 必须在它之前清掉**，
>   否则会被整整挡住 2.5 天。
> - 🚫 **Stage (i) 的 scope 不变 = LLM 预训练（from scratch）**。P-1…P-7 都是**前置选型实验**，
>   **P-8 才是 Stage (i) 本体**。不要因为"实验做完了"就认为 Stage (i) 完成了。

| ID | 内容 | 目的 | 估时 |
|:--|:--|:--|:--|
| **P-1** | **LR 网格向上扩展**：stable LR ∈ **{1.5e-3, 2e-3, 3e-3}** × **5000 步**（WSD 固定） | **判定 1e-3 是否真的是最优** | 1.5h |
| **P-2** | **补 2 个新 seed**（5000 步，胜出配置）→ **n=5** | **把 σ 压小 / 证实 Δ 在噪声内** | 1h |
| **P-3** | **架构对比延长到 5000 步**（dense vs hybrid，**保持 Round 1 的 6 卡/GBS=6 口径**） | **让架构选型不再只靠 1000 步快照** | 1.5–2h |
| **P-4** | ⭐ **FP8 可行性评估**（**先 profile，再决定**） | 判定 FP8 对 **Mamba-hybrid** 是否真的加速 | ≤2h |
| **P-5** | ⭐⭐ **LR@目标 GBS 验证 + 训练量 scaling 曲线**（**最高优先**） | 决定**正式训练会不会白跑** | a:4–5h<br>b:~2.5 天 |
| **P-6** | ⭐ **lm_eval 零样本评测**（对齐 Xmodel-2 Table 2 的 **8 个评测集**） | **摸底训练效果**（Stage (i) 是通用模型，**不做 EDA-Eval**） | ~2–6h |
| **P-7** | ⭐ **训练吞吐幅度核查**（P-3 补充）：论文写 **+24%**，P-3 实测只有 **+4.8%**，**必须查明** | 决定论文 `tab:archcomp` 那一列怎么写 | ~1h |
| **P-8** | 🏁 **Stage (i) 完整训练（正式预训练）** —— 用 P-5a/P-5b 定下的 GBS·LR·调度，在**真实语料**上**从零**训到 **P-5b 曲线决定的 token 预算** | **产出 Stage (i) 的最终模型**（Stage (ii)–(v) 的基座）；**这是 Stage (i) 的本体** | **≥5.5 天**（见下方 P-8 细节） |

**P-1 细节**
- 三点：`1.5e-3 / 2e-3 / 3e-3`，其余超参与 S2/S3 完全一致，各 5000 步。
- 记录：**val loss@5000（必须匹配步数）**、train tok/s、耗时、GPU·h。
- ⚠️ **若某点 loss 发散/出现 NaN，不要重试超过 1 次**——**发散本身就是结论**（= LR 上界），
  记录下来并把该点标为 `DIVERGED` 即可。这是我们要的边界信息。
- 产出：**10 点 LR 曲线**（Round 1 的 7 点 + 新增 3 点），标出极小值位置，
  并明确回答"最优是否仍在网格边界"。

**P-2 细节**
- Round 1 已有 3 个 seed@5000：`44 → 2.640200 / 777 → 2.653915 / 2024 → 2.727488`（均值 2.673868，σ 0.0469）。
- 新增 **2 个 seed**（任选未用过的，如 `7` 与 `2025`），同配置同 5000 步 → **n=5**。
- 产出：**n=5 的均值 ± σ**，并**明确回答**：`min_lr 1e-5 vs 3e-5 的 Δ≈0.003` 是否落在 n=5 的噪声范围内。
- 同时复核 Round 1 那 3 个 seed 的原始值是否与 `EXPERIMENTS_PRETRAIN_2B.md` 一致（只核对，不重跑）。

**P-3 细节**
- 对象：**dense（MiniCPM5-2B）vs hybrid（Mamba2-hybrid）**，与 Round 1 的架构对比同源。
- ⚠️ **卡数与 GBS 必须沿用 Round 1 的对比口径（6 卡 / TP1/DP6 / GBS=6 / seed=1234）**，
  否则与 Round 1 的 1000 步数据不可比。**这是本次最容易做错的一点。**
- 跑 **5000 步**（Round 1 是 1000 步），并在 **500 / 1000 / 2000 / 3000 / 5000** 步各记一次 loss，
  产出**两条 loss 曲线**而不是单点。
- 同时复核 Round 1 记录的参数量（`sum(numel())`：dense 2.512B / hybrid 2.220B）与
  train tok/s、prefill/decode（沿用 Round 1 的 mcore 直驱口径），确认与论文 `tab:archcomp` 一致。
- 若 dense 在该口径下无法复现启动，**立即记录原因并跳过**（不要为此烧超过 30 分钟），
  P-3 降级为"仅 hybrid 单侧延长"。

**P-4 细节 —— FP8 可行性评估（先 profile，再决定）**

> **背景**：Xmodel-2.5（同为自研，Megatron-LM + TransformerEngine）**从 BF16 切到 FP8 混合精度，吞吐 +≈30%**
> （见 `doc/BaiZe-ISEDA2027/Xmodel-2.5/ACL2026/method.tex` §FP8）。
> 但 **Xmodel-2.5 是稠密 Transformer**（几乎全是 GEMM），而 **BaiZe 只有 4/56 层是 attention**，
> 其余是 Mamba-2 SSM + MLP。**TE 的 FP8 加速的是 GEMM / LayerNorm / GeLU，不含 SSM 的 selective-scan。**
> → **不能假定 +30% 会平移过来**，必须先量出 GEMM 占比（Amdahl 定律）。

**第 1 步（先做，便宜）：profile，量出上限**
- 用现有 BF16 配置跑 ~100 步，`torch.profiler` 拆时间：`GEMM（linear/attn/MLP）` / `SSM selective-scan` / `norm+act` / `通信` / `数据加载`。
- 给出 GEMM 占比 `g`，则 **FP8 理论加速上限 = 1/(1-g)**。
- ⚠️ 本任务书自己写着「**SSM 串行是 bottleneck**」——**若 profile 证实 scan 占大头，FP8 收益有限，到此即可结论，不必接 FP8**。

**第 2 步（仅当 g ≳ 0.5）：试接 FP8**
- **照抄 Xmodel-2.5 的既有配方**：forward **E4M3**（activations）、backward **E5M2**（gradients）、**master weights 保持 bf16**；
  TE delayed-scaling `amax-history-len=128` / `amax-compute-algo=max`；经 `--transformer-impl transformer_engine` 启用（kernel 自动选择，无需改源码）。
- 先确认环境：`transformer_engine` 是否已装、版本与 torch 2.8 / CUDA 12.8 是否匹配。
- **冒烟**：能否跑通 10 步（不 OOM、不 NaN）。
- **吞吐对比**：同配置 BF16 vs FP8，各 500–1000 步，报 tok/s 与 ms/iter。
- **精度对齐**：同 seed 比较**前 200 步 loss 曲线**是否吻合；若出现尖峰/NaN，**如实记录，不要强行调参掩盖**。

**第 3 步：结论** —— FP8 是否可行 / 实测增益 / 精度影响 / 是否建议正式训练采用。
🚫 **不替换 BF16 基线**：Round 1/2 结果保持 BF16 口径，FP8 作为**并列报告**。

**时间盒 ≤2h**；若第 1 步即显示 scan 主导，15 分钟内收尾并记录结论。

---

## 🔴 P-4R（**P-4 重开** · 运维 2026-10-02 指令）—— 上一轮的「不接 FP8」结论**判定依据有误，必须重做**

> ### 为什么重开
> 上一轮结论是：**「Amdahl 上限 <2× → 不接 FP8」**。运维审查后判定**该推理用错了 `g`**：
> - 它用的是 **GBS=8/MBS=1（搜索口径）** 的墙钟 `g = 0.286`，
>   **而任务书自己的 caveat 就写着**：「comm 占 41.7% 是小 batch 下偏高、会**高估高 GBS 生产场景**的 comm 占比」，
>   并明确「**此时回到纯计算口径 `g≈0.49`**」。
> - **P-5a 刚刚定稿：生产口径就是 GBS=1024** → 也就是说 **P-8 的真实场景恰恰是 `g≈0.49`**。
> - 更关键的是：**「上限 <2×」说的是 GEMM *单算子* 的上限，不是端到端收益。**
>   这是典型的 Amdahl 口径混淆。
>
> **用 `g=0.49` 重算端到端收益**（`speedup = 1/((1-g) + g/s)`）：
>
> | FP8 GEMM 单算子加速 s | 端到端收益 |
> |:--|--:|
> | 1.35（**反推自 Xmodel-2.5 的 +30%**：稠密 Transformer g≈0.9 → s≈1.35） | **+14.5%** |
> | 1.6 | **+22.6%** |
> | 2.0 | **+32.6%** |
>
> **→ 真实预期是 +14.5% ~ +30%，不是"不值得"。**
> **对 P-8（≈12.5 天）：+22% 省 ≈2.3 天；对 690B 全语料（≈86 天）：+22% 省 ≈19 天。**
> **长训练里这个量级非常有诱惑力**（运维原话：100 天省 1 个月）。

### P-4R 要做什么（**只做一件事：把 `s` 量出来**）

🚫 **不要再用假设的 s 下结论** —— 上一轮就是栽在这。

1. **FP8 GEMM 微基准**：在**我们自己的 GEMM 形状**上（56 层 hybrid 的真实 hidden/FFN 尺寸、
   以及 Mamba-2 的 in/out proj 尺寸），用 TE 的 FP8 路径 vs BF16，**实测单算子加速 `s`**。
   - 至少覆盖：**大 FFN GEMM**、**小/瘦 GEMM**（attention qkv/o）、**MoE 的 expert GEMM**。
   - 报 **s 的分布**，不要只给一个数。
2. **端到端重算**：用 `g=0.49`（生产口径）+ 实测 `s` → 给出**端到端收益区间**。
3. **明确回答**：**接 / 不接 FP8**，并给出**收益数字**与**代价**（扩展 launcher 的工作量）。
4. （若判定"接"）再做第 2 步的冒烟 + 500–1000 步 BF16/FP8 吞吐对比 + **前 200 步 loss 对齐**。

### P-4R 的约束
- **≤ 2 小时**（微基准很便宜）。
- ⚠️ **只占 1 张卡**（`CUDA_VISIBLE_DEVICES=0`）—— **微基准不需要 8 卡**，
  而 **P-5b 正在 `.29` 上用着 8 卡**。→ **P-4R 与 P-5b 共存，不要等 P-5b 跑完 2.5 天再动。**
  （若显存吃紧，可退到 CPU 或等一个 5 分钟空窗。）
- ⚠️ **必须报「哪个 `g`、为什么」** —— 明确写出 GBS 口径，不许再混。
- ⚠️ 若实测 `s` 确实很低（如 <1.2），**也要如实说**，并给出"到此不接"的结论 ——
  **本轮要的是正确的数字，不是"必须接"**。
- ✅ **收益若 ≥15%，对 P-8（12.5 天）就是 ≥1.9 天** —— 这是决策线，请在结论里点明。


**P-5 细节 —— LR@目标 GBS 验证 + 训练量 scaling 曲线（⭐ 最高优先，直接决定正式训练是否会白跑）**

> **为什么最重要**：
> ① 现有胜出 `LR=1e-3` 是**在 GBS=8 下**搜出来的，而本任务书写着「**全量训练固定 GBS=1024**」——**128× 的批大小差**。
> Adam 类优化器的**最优 LR 随 batch size 变化**（线性或 sqrt 缩放），P-1 那个"1e-3 是 U 形谷底"的结论**只在 GBS=8 下成立**。
> ② 现有最长跑只有 **655M token**，而 2.2B 模型的 Chinchilla 最优是 **44B**——**只跑了 1.5%**。
> 这两件事都直接决定**周级**的正式训练会不会白跑。
>
> ⚠️ **两者不能"同一次跑"同时产出**：GBS 扫描必须先跑完才能定下长跑的 LR。
> 因此设计为 **P-5a（前置、便宜、去风险）→ P-5b（长跑）**，**顺序不可颠倒**。

### P-5a　GBS × LR 扫描（**先做**，~4–5 小时）

**两条口径铁律（做错就白做）**
1. **变 GBS 时按 token 匹配，不是按 step 匹配** —— 否则大 batch 多吃的 token 会被误记成 LR 的功劳。
2. **WSD 调度必须按比例重标定** —— 保持 `5% warmup / 85% stable / 10% decay` 的**形状**。
   （例：GBS=1024 时只有 39 步，原 warmup=250 步根本放不下；必须等比缩到 ~2 步。）

| GBS | steps（匹配 164M token） | LR 取值 | 状态 |
|:--|:--|:--|:--|
| **8**（基线） | 5000 | 1e-3 / 1.5e-3 / 2e-3 / 3e-3 | ✅ P-1 已给（谷底 1e-3） |
| **64** | 625 | 1e-3 / 2e-3 / 4e-3 | ⬜ 待跑 |
| **256** | 156 | 1e-3 / 2e-3 / 4e-3 | ⬜ 待跑 |
| **1024**（生产口径） | 39 | 1e-3 / 2e-3 / 4e-3 | ⬜ 待跑 |

**判读**
- **最优 LR 是否随 GBS 右移？** 若右移 → 给出 GBS=1024 下的**推荐 LR**，并说明外推依据；
  若**不右移** → "1e-3 可跨 GBS 迁移"本身也是**有价值的结论**，如实报告。
- ⚠️ **若 39 步太少、噪声压过信号** → 改为**加大 token 预算**（如 GBS=1024 跑 128 步 = 537M token），
  并**把 GBS=8 也补到同一 token 预算**以保持可比。**不要用不足的步数硬下结论。**

### P-5b　训练量 scaling 曲线（长跑，**用 P-5a 选定的 GBS 与 LR**）

- 从零训练，**用 P-5a 推荐的 GBS（尽量接近 1024）与 LR**。
- 在 **655M / 1.3B / 2.6B / 5.2B / 10.5B / 20B token** 各记一次 **val loss**（附带 train loss、grad norm）。
- 产出 **loss vs tokens 曲线**（log-x）。**这条曲线直接用来定正式训练的 token 预算。**
- **若 20B 处仍未明显变平** → 在预算允许内继续延长到 **40–60B**。
- ⚠️ **与既有 `2.2054@655M` 不可直接比较**（那是 GBS=8）：报告须注明口径差异；
  必要时**在 GBS=8 下也补一个 20B 点**作为对照，隔离"GBS 变了"与"token 变多了"两个因素。

**预算**
- P-5a：≈ 9 次 × 164M token ≈ 1.5B token ≈ **4–5 小时墙钟**
- P-5b：20B token ≈ **60 小时墙钟（≈2.5 天 / 478 GPU·h）**；到 60B ≈ 7.5 天
- 合计 **≤ 8 天墙钟**。**先 a 后 b。**

**产出（写进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md`）**
1. GBS × LR 的**完整结果表** + "最优 LR 是否右移"的**明确结论** + GBS=1024 的推荐 LR
2. **loss vs tokens 曲线** + "曲线何时变平"的判断 + **正式训练的 token 预算建议**
3. 论文回填建议：§4 该怎么写（是否要把"655M token 只是 1.5% Chinchilla"如实写进 Limitations）

**P-6 细节 —— lm_eval 零样本评测（对齐 Xmodel-2 Table 2 的 8 个评测集）**

> **目的**：Stage (i) 的定位是**通用模型**，**本任务不做 EDA-Eval**。
> 唯一目标是**摸底训练效果**——让 Stage (i) 的结论**不只是 loss 数字**。
>
> **口径严格对齐 Xmodel-2 论文**（`doc/BaiZe-ISEDA2027/Xmodel-2/xmodel-2.tex:198,207`）：
> - Harness：**EleutherAI Language Model Evaluation Harness（lm-eval）**
> - **zero-shot**、**raw accuracy**
> - **8 个评测集**（与 Table 2 的 8 列一致），另报 **Avg**：
>   `ARC-Challenge` · `ARC-Easy` · `BoolQ` · `HellaSwag` · `OpenBookQA` · `PiQA` · `SciQ` · `Winogrande`
> - ⚠️ 论文正文还提到 **TriviaQA**，但 **Table 2 里没有这一列** → **以表为准，只跑这 8 个**，并在报告里注明此差异。

**第 1 步（最便宜，先做）：评测现有的 20000 步 checkpoint**
- 它就是 Stage (i) 的最终产物；**先拿到它的 8 集分数**，立刻就有"摸底"数据。

**第 2 步（最有价值）：与 P-5b 结合 → 「能力 vs token」曲线**
- 在 P-5b 的 **6 个 checkpoint**（655M / 1.3B / 2.6B / 5.2B / 10.5B / 20B token）上**各跑一次**同样的 8 集评测。
- 产出 **「8 集平均分 vs 训练 token」曲线** —— 这比 loss 曲线**更能回答"训到多少才够"**，
  也**正面回应"训练量太小"的质疑**。

**执行路径（⚠️ 以你们**自己已查证过的结论**为准，不要另起炉灶）**

> 你们在 **2026-09-29** 已经查清过这条路
> （`run/daily-memories/2026-09-29.md:201,207,223` 与 `run/BAIZE_2B_ARCH_SEARCH_TASK.md:218`）：
> - **既定路径就是「ckpt → HF → SGLang 起服」**；当时的阻碍只是 **vLLM（`_C.abi3.so` 崩）与 `sglang`（未装）**，
>   于是退到 mcore 直驱，并明确注明那是**下界测量**（"如需精确 decode 数后续 SGLang 起服复核"）。
> - 那次也写明：**真正的坑是「mcore 分布式 ckpt → HF 格式转换」**（无现成 bridge，需把
>   `NVIDIAMambaHybridModelProvider2B` 权重映射到 **Nemotron-H / Llama HF 结构** + DeepSeek tokenizer）；
>   **mcore 手写前向只是 fallback**。
> - **SGLang 原生支持 `nemotron_h`**（`--mamba-ssm-dtype float32` / `--mamba-full-memory-ratio`）——
>   这正是当初选 SGLang 的原因。

**推荐路径（标准做法；不需要写自定义 lm_eval model 类）**

1. **转 HF**：mcore 分布式 ckpt → **Nemotron-H HF 结构**（含 DeepSeek-V4.1-Flash tokenizer）。
2. **SGLang 起服**（若 `sglang` 未装，先 `pip install sglang`）：
   `python -m sglang.launch_server --model-path <hf> --port 30000 --mamba-ssm-dtype float32 --mamba-full-memory-ratio <按需>`
3. **lm_eval 用内置模型类型直连，无需改接口**：
   `lm_eval --model local-completions --model_args base_url=http://localhost:30000/v1,model=<name>,tokenizer=<hf> --tasks arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande --num_fewshot 0`
   （`local-completions` / `local-chat-completions` 可接**任何 OpenAI 兼容服务**——这是标准用法。）

**⚠️ 先验证一件事（成败所系，第一步就做）**
这 8 个任务里 **7 个是 multiple-choice**，lm_eval 的 `local-completions` 靠 **`loglikelihood`** 打分，
即需要服务端在 `/v1/completions` 上支持 **`echo=True` 且返回 prompt 的 `logprobs`**。
→ **先用一个最小请求验证这一点**；若不支持，再考虑 `local-chat-completions`，
**最后**才回退到自定义 model 类包 mcore 前向。

**时间盒**：转换 + 起服 **≤ 2 小时**；超时就记录卡点并转 fallback，不要无限调试。

**产出**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加一节；
并给出**论文回填建议**（§4 是否加一张"通用能力零样本"表）。

**P-7 细节 —— 训练吞吐幅度核查（P-3 的补充，**必须查明**）**

> **问题**：论文 `tab:archcomp` 写 **dense 89K vs hybrid 72K（dense +24%）**；
> 而 **P-3 在同一口径下**（6 卡 / TP1/DP6 / GBS=6 / seq 4096）实测
> **dense 89.7K vs hybrid 85.6K（dense 仅 +4.8%）**。
> - dense 侧几乎一致（89K → 89.7K）✅
> - **是 hybrid 从 72K 涨到 85.6K（+19%）**，即 ms/iter 由 ~340 降到 ~287。
>
> **为什么必须查明**：**训练吞吐代价是 hybrid 论证里唯一的「成本侧」数字**。
> 若真值接近 +5% 而非 +24%，hybrid 的性价比论证会**明显更强**；
> 反之若是 Round 1 的测量本身有问题，论文里那个 `+24%` 就**站不住**。两种情况都直接决定 `tab:archcomp` 怎么写。

**要做的核查**
1. **先算一笔账**：Round 1 是 **1000 步**短跑；若把 SSM 首步编译开销（记录中的 **~12.3s**）摊进平均，
   相对稳态只抬高约 **3.6%**（12.3s ÷ (1000 × 0.34s)）——**不足以解释 340ms → 287ms 的 16%**。
   → 因此**一定还有别的原因**，继续查。
2. **比对两次测量的差异项**：micro-batch / gradient-accumulation 设置、`--recompute` 档位、并行度、
   mcore / `transformer_engine` / 容器版本、以及**当时的集群争用状态**——是同一套配置吗？**逐项列出**。
3. **在同一环境、同一配置下重测一遍** hybrid 与 dense 的**稳态** ms/iter（各 ≥300 步，**剔除首步**），
   得到可复现的干净数字；记录 **GPU 独占核验原文**（沿用 R2-4 做法）。
4. **给结论**：`tab:archcomp` 的 "Training tok/s" 一列应写**哪两个值**、差距**百分之几**；
   并说明 Round 1 的 72K 究竟属于「含首步开销的短跑均值」还是「另一环境下的值」。

**产出**：写入 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 的 P-3 节 + 更新「论文回填建议」，
明确指出 `tab:archcomp` 该改成什么。**时间盒 ≤1h。**

**P-8 细节 —— 🏁 Stage (i) 完整训练（正式预训练）**

> ## 🎯 这是 Stage (i) 的**本体**
> **Stage (i) 的 scope 不变 = LLM 预训练（from scratch）。**
> P-1…P-7 全部只是**前置选型实验**（token 量级 164M–655M，合计 ~85 GPU·h）。
> **P-8 才是真正把 2.22B hybrid 训出来**，作为 Stage (ii)–(v) 的基座。
> 🚫 **不要**因为"实验都做完了"就把 Stage (i) 标成完成。

**输入（全部来自前序任务，不要自行改动）**

| 项 | 来自 |
|:--|:--|
| **GBS** | P-5a 的 GBS×LR 扫描结论（若无右移则沿用 GBS=8；若 P-5a 指向更优大 GBS 则采用并注明） |
| **LR / 调度 / 退火配比** | Round 1 胜出配置（LR 1e-3 / WSD / warmup 250 / decay 500 / min_lr 1e-5 / L3(86%)+code(10%)+math(4%)）；若 P-5a 给出新 LR 则改用并注明 |
| **token 预算** | ⭐ **由 P-5b 的 loss-vs-tokens 曲线决定**（曲线何时变平 → 就在那附近取预算） |
| **精度** | 若 P-4 证明 FP8 对本架构确有加速且**不劣化 loss**，可用 FP8；否则 bf16。**必须记录采用与否及理由** |

**token 预算的三档参照（按实测吞吐 8×H100 ≈ 92.6K tok/s 折算）**

| 档位 | token | 墙钟 | GPU·h | 说明 |
|:--|:--|:--|:--|:--|
| **下限** | **44 B** | **≈5.5 天** | ≈1056 | Chinchilla 最优（2.22B × 20）。**低于此不足以称为"训练好的模型"** |
| **推荐** | **100 B** | **≈12.5 天** | ≈2400 | 超 Chinchilla ≈2.3×；契合论文**推理效率**卖点（推理最优需过训练） |
| **上限** | 200 B | ≈25 天 | ≈4800 | 仅在预算与时间都宽裕时 |
| ⚠️ 不计入 | 690 B（真实全语料） | **≈86 天** | ≈16560 | **2027-02-01 前不可能** + `/nas_train` 只剩 32T，**不要定这个档** |

> **默认按「推荐档 100B」准备**；**P-5b 曲线出来后，若曲线在更早处变平，就下调**（省钱省时）。
> ⚠️ **最终 token 预算定下后，必须在 `MEMORY_PRETRAIN_2B.md` 里写明并上报**，再启动长跑。

**训练要求**

1. **从零开始**（不加载任何预训练权重），**真实语料**（`Ultra-FineWeb-L3` 全量 en 子集 + code + math 退火配比），
   **不是** `ultrafineweb_l3_qa_700m` 那个 742M 小分片 —— **本次必须跑真正的全量语料**。
2. **WSD 完整走完**：warmup 250 → stable → **decay 尾段必须真的吃到退火混合**（这是 Stage (i) 的核心配方之一）。
3. **checkpoint 规划**：至少保留 `final` + **每 10% 一个**（供 Stage (ii) 选起点、供 P-6 画能力曲线）。
   ⚠️ 每个 ckpt（2.22B 含 AdamW 状态）≈ **~30 GB**；**`/nas_train` 只剩 32T**，先算好 ckpt 留存策略与清理时机。
4. **训练中每 500 步**记 `train loss` / `val loss` / `grad norm` / `tok/s` / **GPU 独占核验**。
5. **禁止在 P-8 期间叠加其它重 I/O 或抢卡任务**（vision / data 侧要避让）。
6. **失败即如实记录**：NaN / 发散 / OOM 一律记录**并保留当时的 ckpt 与日志**，不要静默重启掩盖。

**产出**

1. **Stage (i) 最终 checkpoint**（Stage (ii)–(v) 的基座）—— 这是本项目**最关键的单个产物**。
2. `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加 **P-8 节**：完整 loss 曲线、实际 token 数、实际 GPU·h、
   最终 `val loss`、与 P-5b 曲线预测值的对照（**预测量 vs 实测量**，这是对 scaling 曲线的一次真检验）。
3. **论文回填建议**：§4 应写清 **实际训练 token 数 / GPU·h / 最终 loss**，
   把"从零训练一个 2.22B hybrid"的**规模与代价如实写出来**（并处理 §6 #13 的 1.8T 误读问题）。
4. `BAIZE_PRETRAIN_RESULT.html` 更新为**含 P-8 的最终版**。
5. git commit + push（**只提交文本**；checkpoint 不入库）。

**时间盒**：**下限 5.5 天 / 推荐 12.5 天**（按 token 预算）。**超时或连续失败不要硬撑**，
记录卡点并上报 —— 但**除非运维叫停，P-8 应跑到底**。


## R2.3 交付物

1. **`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`**（新文件）：P-1/P-2/P-3 全部结果表 +
   每条可复现命令 + 与 Round 1 的差异说明 + **「论文回填建议」段落**（给出精确数值与文字建议，
   特别是「最优点是否在边界」「Δ 是否在噪声内」这两个结论该怎么写）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_PRETRAIN_RESULT.html` 或新建 `BAIZE_PRETRAIN_RESULT_ROUND2.html`（自包含）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——
   论文已由外部统一重构并推送，回填由外部完成。你只在报告里给「回填建议」。
4. 正常更新 `MEMORY_PRETRAIN_2B.md` 与 `daily-memories/`。
5. **git commit + push，并严格走本文件顶部的「git 同步规则」**（fetch → 必要时 `pull --rebase` → push → 确认 0/0）。

## R2.4 约束

- **总预算**（分三档）：
  - **P-1 / P-2 / P-3 / P-4 / P-6 / P-7**：短程实验，≤ 5 小时墙钟（P-6 视加载路径难度可到 6 h；P-7 ≤1h）。
  - ⭐ **P-5 是独立长任务，≤ 8 天墙钟**（P-5a 4–5 h + P-5b 20B token ≈ 2.5 天；预算允许可延到 60B ≈ 7.5 天）。
  - 超时按 **P-5a > P-6 第 1 步（现有 ckpt 的 8 集）> P-1/P-2 > P-4 > P-5b > P-6 第 2 步** 逆序裁剪，并在报告记录裁剪决策。
- **GPU**：只用 `10.239.2.29` 的 **GPU 0–7**（8 卡）。**绝不杀他人进程**。
  ⚠️ 另有 vision 任务在 **`10.239.2.12`**（另一台机器）跑——**与你无关，不要去动那台**。
- **每次启动训练前后都要记录 GPU 占用核验结果**（`nvidia-smi --query-compute-apps=...`）。
- ⚠️ **NFS 与 vision 任务共享（重要）**：两台 GPU 节点用的是**同一块 `/nas_train` 盘**。
  vision 任务的 **R2-4 需要"无争用的干净吞吐测量"**，而你启动训练同样会打这块盘。
  → **启动 P-1 之前**，先读 `run/MEMORY_VISION.md`（共享盘，你直接可见）看它的 R2 进度：
  - 若 **R2-4 尚未完成**：先做**不占 GPU** 的准备工作（代码/数据核对、P-3 的 Round 1 基线复核、脚本落地），
    **每轮唤醒重查一次**它的进度；
  - **最多等 2 小时**；超过 2 小时则照常启动 P-1，并在报告里注明"当时 vision 任务在并发"。
  → 你的**每次测量都要记录"当时 vision 任务在跑什么"**。
- 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；
  **P-3 若需更长的数据覆盖，先核对再启动**，不要中途断数据。
- **收尾不杀 loop（关键）**：R2 的 P-1/P-2/P-3 全部完成（或按预算裁剪到只剩需等待的项）后，把结果写进报告并 git push，然后**停在原地**：`MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（30 分钟长轮询）；🚫 **绝不 kill / pkill `baize_pretrain_loop.sh`**。loop 必须持续运行，以便运维远程下发新任务（会改写本任务书，下次唤醒即按新指令执行）。

---



> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（**必读，2026-10-01 新增，每次唤醒都要走**）

### 前提：这是一个**共享工作副本**

vision 任务的 agent 与本任务**共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

**因此：**
- **只需一个人 pull，另一个立刻看到**：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。
  **不要重复 pull**，也不要因为"工作区里出现了别的任务的改动"而困惑。
- 工作区里**陌生的未提交改动很可能是 vision 任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 两个 loop 每 5 小时各自 `git add -A && commit && push`，**会互相把对方在途的文件一起提交**。
  这是既有设计的已知副作用，**不要试图"修正"它**。

### 但 loop 本身**只 push 不 pull**

`baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。
一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。
**所以 pull 必须由你（agent）来做。**

**每次唤醒按顺序执行：**

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`
   🚫 **不要用 `git add -A`**——那会把 vision 任务的在途文件卷进你的提交。
3. 若显示 **behind / diverged**：`git pull --rebase origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是**双方的在途改动**：
     先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：
     等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并**跳过本次 git 操作**，下次唤醒再试。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` **无 ahead/behind** 才算闭环。
5. 流水记一行 git 结果（沿用你已有格式）。

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——**沿用同一做法**。

---


---

## 任务目标

在**已选定**的 Mamba2-hybrid（2.220B）骨架上，完成受 **24h 墙钟（≈192 GPU·h @ 8 卡）** 预算约束的高置信度超参搜索（S0–S5），最终产出：

1. 一条**胜出配置**（stable LR + 调度族 + 关键轴 + 退火数据混合）
2. 一份**实验记录表**（`EXPERIMENTS_PRETRAIN_2B.md`），含所有配置的 ID / 超参 / 结果 / GPU·h
3. 一条**20000 步长跑收敛曲线**（胜出配置）+ **多 seed 复现**（3 seed，报均值±σ）
4. 一条**可复现训练命令** + 一份 HTML 报告 `BAIZE_PRETRAIN_RESULT.html`

对应论文 `ISEDA2027/4_llm_pretrain.tex` 与计划 `BAIZE_LLM_PRETRAIN_PLAN.html`。

---

## 已定前提（固定，不要更改）

| 项 | 值 |
|:---|:---|
| 架构 | **Mamba2-hybrid**（56 层，Nemotron-H 式顺序混合，**2.220B**）|
| 框架 | NVIDIA/NeMo recipe + Megatron-Core（`NVIDIAMambaHybridModelProvider2B`），torchrun 直驱 |
| **BASE_DIR** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027` |
| provider/recipe | `BASE_DIR/mamba2_hybrid_2b/`（provider.py / recipe.py，已有）|
| tokenizer | DeepSeek-V4.1-Flash，`BASE_DIR/data/tokenizer_eod`（vocab 129281 / pad 129408）|
| 数据（stable 主体）| Ultra-FineWeb-L3 英文 `BASE_DIR/data/ultrafineweb_l3_qa`（`.bin/.idx` 已切 200k docs / 165M token）|
| 环境 | CUDA 12.8 / PyTorch 2.8.0 / Python 3.10；`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230` |
| GPU | 主训练 **`10.239.2.29`（8×H100，GPU0~7）**；辅助 `10.239.2.12`（GPU0~5）|

> 启动器：`BASE_DIR/scripts/train.sh <arch> <name> <master_port> [nproc]`（arch=`mamba2`，nproc 传 **8** 以用满 `10.239.2.29` 全 8 卡），内部调 `pretrain_launcher.py`。**需先扩展 launcher** 支持 `--lr` / `--lr-warmup-iters` / `--lr-decay-iters` / `--lr-decay-style`（WSD|cosine）/ `--min-lr` / `--seq-length=4094`，并把硬编码的 `--global-batch-size 6` / 默认 `nproc 6` / `--train-iters 1000` 改为可按参数传（默认 8 卡：GBS=8、DP=8、步数可变）（见 S0）。

---

## 搜索矩阵（S0–S5，24h 预算）

预算：**24 h 墙钟 ≈ 192 GPU·h**（8 卡满载）。计划用量 **~92 GPU·h**，余 **~100 GPU·h** 供重试/扩展。

短地平线统一 **5000 步/组**（GBS=8 × seq4094 = 32.7K tok/步，5000 步 ≈ 164M token）。长跑 S5-1 用 **20000 步**。

| 阶段 | 内容 | 组数 | 步数 | 备注 |
|:---|:---|:---|:---|:---|
| S0 | launcher 适配 + 8 卡冒烟 | 1 | ~10 | 实测 step time 校准预算 |
| S1 | baseline（lr 3e-4 / WSD）| 1 | 5000 | 建 loss/吞吐基线，产出 S1-01 |
| S2 | stable LR 加密扫描（7 点）| 7 | 5000 | WSD 固定，产出 S2-01…S2-07 |
| S3 | 关键轴微调 | 5 | 5000 | 胜出 LR 上单变量，产出 S3-01…S3-05 |
| S4 | 退火数据混合消融 | 3 | 5000 | 产出 S4-01…S4-03 |
| S5 | 长跑 + 多 seed | 4 | 20000 / 5000 | 收敛曲线 + 可复现，产出 S5-01…S5-04 |

### S2 stable LR（WSD 固定，7 点）
`2e-4 / 3e-4 / 4e-4 / 5e-4 / 6e-4 / 8e-4 / 1e-3`

### S3 关键轴（S2 胜出 LR 基础上，每次只动一个变量）
- S3-01/S3-02 调度族：WSD vs cosine（2 组）
- S3-03 decay ratio：5% （默认 10%，增量扫 15% 可选；warmup 固定 5%，stable 相应调整）
- S3-04 warmup：占比 5% vs 固定 2000 步（1 组）
- S3-05 min_lr：3e-5 vs 1e-5（1 组）

### S4 退火数据混合（胜出配置，decay 尾段混入）
- S4-01 纯 L3 高质量子集 | S4-02 L3+代码（UltraData-Code）| S4-03 L3+代码+数学（UltraData-Math）

### S5 长跑 + 多 seed
- S5-01 胜出配置从零 **20000 步**，产出论文 loss 收敛曲线
- S5-02…S5-04 胜出配置 3 seed × 5000 步，报 loss 均值±σ（可复现）

### 固定超参（跨配置一致，不扫）
- **8 卡（`10.239.2.29`，TP=1/DP=8）**、GBS=8（短地平线；**全量训练固定 GBS=1024**）、mb=1、seq=4094、bf16
- optimizer distributed AdamW（β1=0.9 β2=0.95 eps=1e-5 wd=0.1）、seed=1234
- WSD：warmup 5%=250、decay 10%=500、stable 85%=4250（均 5000 步口径）
- eval：`--eval-interval 250 --eval-iters 0`（关闭避免除零）

### 数据需求（关键，超步数前先核对）
- S1–S4（5000 步/组）：现有 200k docs / 165M token 已够（5000 步≈164M），各组独立从头复用同一份
- S5-01（20000 步≈655M token）：**需先补切数据**到 ≥700M token（用 L3 主数据 `preprocess_data`，按需混代码/数学退火源）再启动

---

## 推进状态机（PHASE）

- **S0 launcher 适配**：扩展 `pretrain_launcher.py` / `scripts/train.sh` 支持 `--lr` / `--lr-decay-style`（WSD/cosine）/ `--lr-warmup-iters` / `--lr-decay-iters` / `--min-lr` / `--seq-length=4094`，把 GBS/nproc/train-iters 参数化（默认 8 卡、GBS=8、DP=8）；确认 `arch=mamba2` 在 `10.239.2.29` 从零可跑 10 步冒烟，实测 step time → `PHASE=s1`
- **S1 基线**：跑 S1-01（lr 3e-4 / WSD / 5000 步），记录 loss / tok/s → `PHASE=s2`
- **S2 LR 扫描**：依次跑 7 个 LR（2e-4…1e-3），每个 5000 步，记录 val loss@匹配步数 → 选最优 LR → `PHASE=s3`
- **S3 关键轴**：胜出 LR 上单变量跑 5 组（调度族/decay/warmup/min_lr）→ 确定胜出配置 → `PHASE=s4`
- **S4 退火消融**：跑 3 组退火数据混合，量化退火质量增益 → `PHASE=s5`
- **S5 长跑+多seed**：先补切数据到 ≥700M，跑 winner 20000 步收敛曲线 + 3 seed 复现 → `PHASE=converged`
- **converged**：输出胜出配置 + 可复现命令 + `BAIZE_PRETRAIN_RESULT.html` 并 git push；**完成后停在原地：保持 `PHASE=converged`、把 `WAITING` 置 `1`（进入 30 分钟长轮询），🚫 绝不 kill / pkill `baize_pretrain_loop.sh`**——loop 必须持续运行，以便运维远程下发新任务（改写本任务书后，下次唤醒即按新指令执行）。

每步先核对 `BUDGET_USED`（≤192 GPU·h）。val loss 必须在匹配步数下比较。

---

## 记忆管理

- `MEMORY_PRETRAIN_2B.md` — 运行时状态（STAGE/PHASE/ERROR_COUNT/BUDGET_USED/看板/流水）
- `EXPERIMENTS_PRETRAIN_2B.md` — 实验记录表（核心产出）
  `| ID | 阶段 | stable LR | 调度族 | decay/warmup/min_lr | 退火混合 | 状态 | val loss | 训练tok/s | 耗时 | GPU·h | 备注 |`
- `daily-memories/$(date +%F).md` — 当日操作日志

启动恢复：读 MEMORY → EXPERIMENTS → 当日日志 → 判断下一步 → 执行 → 回写。

---

## GPU 资源与进程管理

- **主训练节点 `10.239.2.29`（8×H100，GPU0~7）**，本计划 S1–S5 均在此节点 8 卡（TP1/DP8）串行运行；辅助 `10.239.2.12`（GPU0~5，GPU6~7 被占）。ssh 免密已通。
- 检查占用：`nvidia-smi` / `ssh 10.239.2.29 nvidia-smi` / `ssh 10.239.2.12 nvidia-smi`（`--query-compute-apps=pid,process_name,used_memory`）。
- 只杀本项目残留（`pgrep -af 'megatron|torchrun|pretrain_launcher'`），杀前记 PID 到 MEMORY 流水；不杀他人进程。
- 卡数对齐：两组对比须同卡数（各 8 卡 TP1/DP8）；主训练统一在 `10.239.2.29` 串行 8 卡。

---

## 时间估计

- 单步 ~350ms/iter（8 卡 TP1/DP8；SSM 串行是 bottleneck，6 卡基准 ~340ms 外推，S0 冒烟实测校准）
- 5000 步/组 ≈ **~30 min**（≈4.0 GPU·h）；20000 步 ≈ **~2 h**（≈15.6 GPU·h）

| 阶段 | 组数 | 步数 | 小计墙钟 | 小计 GPU·h |
|:---|:---|:---|:---|:---|
| S0 冒烟 | 1 | ~10 | ~1 min | ~0.1 |
| S1 baseline | 1 | 5000 | ~30 min | 4.0 |
| S2 LR×7 | 7 | 5000 | ~3.5 h | 28 |
| S3 关键轴×5 | 5 | 5000 | ~2.5 h | 20 |
| S4 退火×3 | 3 | 5000 | ~1.5 h | 12 |
| S5 长跑+3seed | 4 | 20000/5000 | ~3.5 h | 27.6 |
| **合计** | **21** | | **~11 h** | **~92** |

- 纯训练 ~11 h 墙钟 / ~92 GPU·h，24h 预算余 ~13 h / ~100 GPU·h 供重试与抖动
- 端到端（含 S0 launcher 扩展 + S5 补切数据）≈ **~14 h** 墙钟

---

## 验收产出

1. 胜出配置（stable LR + 调度族 + 关键轴 + 退火混合）+ 可复现命令（写 `EXPERIMENTS_PRETRAIN_2B.md` 顶部）
2. 20000 步 loss 收敛曲线 + 3 seed 均值±σ（回填论文图表）
3. `BAIZE_PRETRAIN_RESULT.html`（自包含：搜索矩阵 + 各配置 loss 表 + 胜出结论 + 命令）
4. git commit + push（只提交 `doc/` 文本 md/html，checkpoint/.bin/.idx 不入库）
