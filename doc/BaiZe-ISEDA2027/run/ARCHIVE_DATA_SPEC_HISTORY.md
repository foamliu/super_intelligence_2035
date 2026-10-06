# ARCHIVE — 被取代的候选表 / 推导过程 / 已完成轮次（源自 BAIZE_DATA_TASK.md）

> 2026-10-06 agent 自滚归档（原文未改，不改任何结论）。需要查历史推导细节时再读。

---

### 🔴 运维指令 · 2026-10-06（配比实验改道）② 硬约束 + ③ 标定 —— 已执行/被第5轮块覆盖

> ②③ 的候选表/推导过程已被「第5轮 d=128/L=14」块覆盖；标定结果见 MEMORY_DATA.md「开工前 5 项必验结果」。

#### ② 硬约束（**用户给定，不许自行放宽**）

| 项 | 值 |
|:--|:--|
| **算力** | `.29` **GPU2–7（6 卡）**（卡账本见 `run/GPU29_ALLOC.md`） |
| **并行方式** | ⭐ **每张卡独立跑一个 trial**（`torchrun --nproc_per_node=1`，**TP1 / DP1**，**各自 `master_port`**，`CUDA_VISIBLE_DEVICES=<i>`）→ **6 个 trial 并行**；🚫 **不要**再用 DP6 跑单个大模型 |
| **GBS** | **8–16**（小 batch，用户指定） |
| **seq_len** | **2048**（用户指定；可更小，但**同一 study 内必须固定**） |
| **吞吐目标（硬指标）** | **24h（6×H100）跑 200–400 个 trial**（**或 `D=1B` 档的 512 个，见 §② 末两行**） → 即 **≈144 GPU·h ÷ (200–400) ≈ 0.36–0.72 GPU·h/trial**，换算**单 trial wall ≈ 22–43 min**；**按富余取 ≤ ~20–30 min/trial** |
| **代理模型**<br>⭐ **2026-10-06 现场定案，🚫 不许自行改** | 🚫 **不是 2.2B**。**锁死配置**：同族 mamba2-hybrid · **`hidden=512 / layers=14 / ffn=2048 / attn heads=4 / query_groups=1 / mamba d_inner=1024 (=2h) / ssm_state=128 / n_groups=2`**（`L=14` = 2B 的 56 层 pattern 的最小完整周期 `6M/1*/7-`，**严格保持 24M:4*:28- 比例**；`L=16` 会破坏比例，已作废） · **tie embed（`share_embeddings_and_output_weights=True`）** · pattern 保持 **24M:4*:28-** 的比例与层序（按 2B 的 `_HYBRID_OVERRIDE_PATTERN` 同比截取）· **实测 `numel()` ≈ 96.8M**。<br>**口径（两个都要报）**：**总参 = 2.220B 的 1/23**（与 Xmodel-2 tiny 的 1/22 同档）；**非-embedding 30.5M = 目标非-embed 的 1/64**（目标非-embed = 1.955B@tie / 1.690B@untie —— 开工前用分模块 `numel()` 核一遍并记进 `MEMORY_DATA.md`）。<br>**四选项裁定**：**`1/20` ✅ 定案** ｜ `1/10`（`d1024/L12`≈237M）❌（`T` 掉到 135–200 且 `D` 只 0.24–0.36B = 1.5 token/参，配比信号与 warmup 暂态混在一起）｜ `1/50`（`d256/L14`≈40.8M，**非-embed 仅 7.6M = 19%**）❌ ｜ `1/100`（`d160/L14`≈23.7M，**非-embed 3.0M = 13%**）❌（两者在 V=129,408 下**本质是「一张查表 + 微网络」**）。<br>**推导（三条独立约束夹住）**：`① 上界（默认档 `D ≥ 0.5B`、`T ≥ 200`）N ≤ 173M`（`N = C·η/(6·T·D)`，`C=518,400 GPU·s/天`、`η≈2e14 FLOP/s/卡`；**换成 `D=1B`、`T=512` 则只有 34M，见下一行**）｜`② 下界 = `d ≥ 512` 且 `L ≥ 14`（**V=129,408 × tie 下，`d<512` 时 embedding 占比 >68%、body <30M** ⇒ 容量塌陷）｜`③ D 的独立依据` = **Xmodel-2 风洞代理实测 token/trial：nano `433.8M`（`xmodel-2.tex:470`）· tiny `1B`（`:437`）**，且 tiny(54M) 就是他们做**配比优化**的代理（`:420`）＝ 目标 1.2B 的 **1/22**（**非-embed ≈1/52** —— 与我们 96.8M 的 1/64 **同档**）。<br>文献旁证：RegMix（arXiv 2407.01492）512 × 1M 参 × 1B token 代理 → 迁移 1B/25B 且胜过人类选择；Data Mixing Laws（arXiv 2403.16952）嵌套 scaling law 小尺度外推 1B/100B。<br>**口径复用**：`recipe`/provider 只加尺寸参数，**🚫 不改 mamba2-hybrid 的实现与 tokenizer**（否则「代理 ≠ 同族」）。 |
| **单 trial token 预算 `D`**<br>（**新增硬指标 · 两档**） | **默认档 `D ≈ 0.45B`**（GBS16×seq2048 → **13,700 步/trial**；`T = 37.75 ÷ s_step`）· **追问档 `D = 1B`**（= RegMix 口径，**30,518 步/trial**；**`T = 17.0 ÷ s_step`**，512 trial 要求 **`s_step ≤ 33.2 ms`**）⇒ 该档下模型必须降到 **≈24–29M**（见下一行）。<br>**通用设计方程（唯一换算公式，两档通用）**：**`N[M] × D[B] = 86.4 × (η/1e14) ÷ (T/100)`**（`N` 单位 M 参、`D` 单位 B token、`η` = 每卡实测 FLOP/s）—— 例：`η=2e14、T=512` ⇒ `N×D = 33.8` ⇒ `D=1B` 时 **`N ≤ 33.8M`**；`η=2e14、T=400` ⇒ `N×D = 43.2` ⇒ `D=0.45B` 时 `N ≤ 96M`（= 定案配置恰好落在此线上）。<br>**优先级（冲突时按此让路）：保 `D` 与 `T` 优先，最后才缩 `N`**；🚫 不许为省时间缩 `D`、不许把 `T` 降到 200 以下。<br>**why**：`D` 决定「配比信号能否压过噪声」—— 我们自己唯一有实测噪声锚点的口径是 **2.2B @ 655M token、3-seed σ=0.0469**（`MEMORY_PRETRAIN_2B.md`），`D` 若只有 65–130M（旧建议）则信号埋进 warmup 暂态。 |
| ⭐ **分支裁定：若 `D=1B` × `T=512`/天**<br>（用户 2026-10-06 追问「1B × 512 组」） | **答案 = 「1/50–1/100 档」⇒ 代理 ≈ 24–29M（`hidden=160–192 / layers=14`），其中 embedding 占 85–87%、可训 body 仅 3.0–4.3M**。⇒ **定案配置 `d=512/L=14`（96.8M）在此预算下不可能**（需 **58% MFU**，小模型在 H100 上做不到）。<br>**推导（embedding 优先，三步）**：`① 预算` = 518,400 ÷ 512 = **1012.5 GPU·s/trial** ⇒ 需 **`η_req = 6·N·D ÷ 1012.5 = 5.93e6·N`** FLOP/s/卡。`② embedding + LM head 与 body 无关、单独就要 `6·V·d·D` FLOPs` ⇒ **`d ≤ 1012.5·η ÷ (6×129,408×1e9)` = `1.30 × (η/1e14)`**（`η=1e14`→`d≤130`；`2e14`→`d≤260`；`3e14`→`d≤390`）—— **这一条与模型多大完全无关，是 `V=129,408` 的硬上限**。`③ 再给 body 留约一半预算` ⇒ `d=160–192`、`body = 8.32·d²·L`（系数由 **2.220B / 56 层 / d=2048** 反标定：`1955M ÷ (2048²×56) = 8.32`）⇒ `L=14` 时 body = **3.0M / 4.3M** ⇒ **`N = 23.7M / 29.1M`**。<br>**四档在 `D=1B×T=512` 下的判决**：`1/10`（242M，非-embed 110M）❌ 需 **1.43e15 = 145% MFU** ｜ `1/20`（96.8M）❌ 需 **5.74e14 = 58%** ｜ `1/50`（`d256/L14`，40.8M，body 7.6M，E 81%）⚠ 需 **2.42e14 = 24%** —— **只有把 GBS 提到 64–128 才有希望** ｜ **`1/100`（`d160/L14`=23.7M 或 `d192/L14`=29.1M，body 3.0–4.3M，E 85–87%）✅ 需 1.4–1.7e14 = 14–17%，可行**。<br>⚠️ **两条硬约束在 `D=1B` 下互斥**：`GBS 8–16` ⇒ 30,518 步/trial ⇒ 需 **33.2 ms/步**（= kernel-launch 地板附近，固定 overhead 会吃掉 25–45% 预算）⇒ **要在 24M 以上必须把 GBS 提到 64–128**（步数降到 3.8–7.6K）⇒ **已批例外条款，见 §③.8**。<br>**迁移性辩护（为何 24–29M 仍可信）**：`D/N` = 1B/24M = **42 token/参**，与 Xmodel-2 的 nano（433.8M/21.69M = 20）· tiny（1B/54M = 18.5）**同档且更偏数据侧**；RegMix 更极端（1B token / **1M 非-embed body** = 1000 token/参）**且迁移成功** —— 而 RegMix 的「1M」正是**非-embed**（其 embedding 6.4M 另计、占总量 86%），**这就是「必须考虑 embedding」的文献印证**。<br>**换档建议（若要求代理保持定案的 96.8M）**：`D=1B` ⇒ `T=163`（= **3.1 天**，不是 1 天）；或 `T=512` ⇒ `D ≤ 0.32B`。**二选一，不许两头都要。** |
| **搜索算法** | **Optuna**（`TPESampler` 贝叶斯优化 + `MedianPruner` 早停）—— **用户指定**（他此前即用 Optuna 做 BO） |
| **预算** | ⭐ **Day1 = 搜 Stable 段配比；Day2 = 搜 Decay 段配比**，**各 1 天** |

#### ③ 标定（**先标定，再开搜 —— 不许跳过**）

1. **先跑 1 个 trial（1 卡）**，实测 **tok/s** 与 **s/step**（固定 `GBS=16` / `seq=2048`）→ 贴**原始输出**。
2. **反推**：`单 trial 时长 = 步数 × s/step`；**若 > 30 min → 继续缩小模型**（**先减层数，再减 hidden**），直到满足 **200–400 trial / 24h**。
   - 🔢 **可直接算的公式**：`N_trial/天 ≈ 6 × 86400 ÷ (步数 × s/step)`；即要求 **`步数 × s/step ≤ 1728 s`**（= 300 trial/天）；`≤ 2160 s` 对应 240 trial/天。
   - 💡 反过来：**若标定后 24h 能跑远超 400 trial → 把模型调大**（larger proxy = 更好的迁移性），**而不是**把 trial 数堆到上千。
3. ⚠️ **订正（2026-10-06 定案）：旧建议「~2000–4000 步/trial（≈65–130M token）」作废** —— 那只有 0.6–1.3 token/参，**配比信号出不来**（损失还在 warmup 暂态）。**改为：`D ≈ 0.45B token/trial` ⇒ GBS16×seq2048 下 ≈ `13,700 步/trial`**；`D` 的依据见 §② 新增行（Xmodel-2 代理实测 0.43–1B token/trial）。
4. 把 **实测 tok/s · s/step · 选定模型配置（层数/hidden/参数量）· 预计总 trial 数 · 预计总时长** 写进 `MEMORY_DATA.md` + 报告。
5. ⚠️ **标定若显示 24h 跑不到 200 trial → 再缩小模型**，**不是**延长时间、**不是**减 trial 数。

6. ⭐ **预注册规模阶梯（先定后测：测完直接查表，🚫 不许事后改判据）** —— 在 **`h=512 / L=14 / GBS16 / seq2048 / 1 卡`（= 定案 96.8M）** 上实测 `s_step`（记为 `X`；跑 ≥50 步取中位数，**贴原始输出**）：
   - 🔢 换算（**通用式：`T = 86400·η/(N·D)`，或 `T = 6×86400 ÷ (步数 × s_step)`；`步数 = D ÷ (GBS×seq)`**）：`D = 0.45B` + GBS16×seq2048（32,768 token/step）⇒ **13,700 步/trial** ⇒ **`T = 37.75 ÷ X`**（**与 `N` 无关**，只由步数决定）；`D = 1B` ⇒ **30,518 步/trial** ⇒ **`T = 17.0 ÷ X`**（512 trial 要求 `X ≤ 33.2 ms`，而 33.2 ms 已在 launch 地板附近 ⇒ 见 §③.8 例外条款）。
   - 📐 候选规模表（`D=0.45B` 档的目标 = `T ≥ 400`；`body = 8.32·d²·L`，`E = 129,408·d`，**`L` 一律取 14**）：

   | 候选（`L=14`） | 总参 `N` | embedding 占 | 需 `X ≤`（=37.75/400） | 说明 |
   |:--|--:|:--|:--|:--|
   | `h=768` | 168.1M | 59% | 0.0952 s ×(1.74×) = 0.166 s | 仅当 `h=512` 实测 **≤0.055 s**（富余）才上调 |
   | **`h=512`（定案）** | **96.8M** | **68%** | **0.0952 s** | ✅ 主选 |
   | `h=448` | 81.4M | 71% | 0.0952×0.84 = 0.080 s | 第一档降级 |
   | `h=384` | 66.9M | 74% | 0.0952×0.69 = 0.066 s | 第二档降级 |
   | `h=256` | 40.8M | 81% | 0.0952×0.42 = 0.040 s | 兜底（body 仅 7.6M） |
   | `h=160` | 23.7M | 87% | 0.023 s | **`D=1B/T=512` 档才用** |
   | **`h=128`（RegMix 同族口径）** | **18.5M** | **90%** | 见下注 | **body 仅 1.91M**（非-embed = 目标的 1/1027，≈ RegMix 的 1/1000）；`D=1B` 档可用（`T ≈ 400–860`，见 §③.9）；⚠️ `heads = d/128 = 1`（结构边界，需冒烟验证） |

   > ⚠️ **`N < 40M` 后瓶颈从算力转为「每步固定开销」**：`T ≈ 6×86400 ÷ [步数 × (6·N·(GBS·seq)/η + t_fixed)]`，`t_fixed ≈ 3–8 ms`（launch+Adam+sync）⇒ 小模型的 `T` 实际**封顶 ~800–1200/天**（此时唯一杠杆是提 GBS，见 §③.8-a）。

   | 实测 `X`（h512/L14） | 判定 | 动作 |
   |:--|:--|:--|
   | **≤ 0.095 s** | 富余/达标 | `T ≥ 400` → **锁定 `h=512/L=14`**；若 `X ≤ 0.055 s` → 上调 **`h=768/L=14`（168.1M，总参 1/13）**并重测 |
   | **0.095–0.126 s** | 达标 | `T = 300–400` → **锁定 `h=512/L=14`**，如实报 `T` |
   | **0.126–0.19 s** | 偏慢 | `T = 200–300` → 降到 **`h=448/L=14`（81.4M）** 重测；仍 >0.15 s → **`h=384/L=14`** |
   | **> 0.19 s** | 太慢 | `T < 200` → 降到 **`h=256/L=14`（40.8M）**；**仍不许延长时间、不许减 `D`、不许把 `T` 降到 200 以下** |
   - ⚠️ **若 `X > 0.19 s` 但「按 §③.8-a 把 GBS 提到 64–128 后 `X` 明显下降」⇒ 判为 overhead 主导，先提 GBS 再定模型**（否则会把「每步固定开销慢」误判成「模型太大」，白缩一半容量）。
   - 🚫 缩规模**只许按同比例动 `hidden` / `layers`（`L` 取 14 的倍数），并同步按同族比例缩 `ffn`（=4d）· `d_inner`（=2d）· `heads`（=d/128）；保持 **24M:4*:28-** 的 pattern 比例与层序、**tie embed**、**同 tokenizer**）；最终以 **`numel()` 实测 + 分模块（embed / body）计数**为准并写进 `MEMORY_DATA.md`。
7. 🔴 **开工前必须先验掉的 3 件事（比「模型多大」更致命；不验 = 两天的结果作废）**：
   - **① 验证集必须与 trial 配比无关** ⇒ 🚫 **不得**用「与训练同配比」的 bin（那会把 objective 变成「谁多喂谁得分」的同义反复，搜出来的必然是把 val 集喂满的配比）。**做法**：从 3 个域**各自**留 1–2M token held-out（⚠️ `anneal_code` 全量仅 ~180M，至少留 1–2M），**objective = 固定权重加权 loss**（权重**先定后测、全程不变**，建议先在 `MEMORY_DATA.md` 写死再开搜）；**同时报 3 个域的分域 loss**（便于事后换权重，不必重跑）。**held-out 必须在 tokenize 之前从源 jsonl 按 hash 切出**，训练 `.bin` 不得含它（= 防泄的物理保证）。
   - **② 先验掉 val-loss 通路**：现脚本是 `--eval-interval 250 --eval-iters 0`（`run/baize_mix_stable_s0a.sh:64`）⇒ **很可能根本没有真正的 eval loss**。必须先确认 `pretrain_launcher.py` 如何产出「**固定 bin** 的 val loss」，**贴 20 步冒烟原始输出**；🚫 不许拿 train loss 顶替（train loss 受配比影响的方式与 val 不同，会系统性骗过 BO）。
   - **③ LR 必须重扫（proxy 的 LR ≠ 2.2B 的 `1e-3`）**：标定批**顺带**跑 `LR ∈ {3e-4, 1e-3, 3e-3}` 三点（4 卡并行 × ~0.4 GPU·h，墙钟 ~25 min，**不额外花时间**），按 train/val loss 选一个并**全程固定**。不扫 = **把「LR 不对」误判成「配比不好」**（这正是 `MEMORY_PRETRAIN_2B.md` 里 min_lr「Δ<噪声」同类错误的翻版）。
8. ⭐ **已批例外条款（2026-10-06，仅当 `D ≥ 0.5B` 时生效 —— 用于 `D=1B/T=512` 那一档）**：
   - **a) `GBS` 上限放宽到 64–128**（用 `mb=16 × accum=4~8` 凑出 `GBS = mb×accum`；**同一 study 内固定**）。理由：步数 `= D ÷ (GBS×seq)` ∝ `1/GBS`，`D=1B` + GBS16 ⇒ 30,518 步/trial ⇒ launch/Adam/sync 的**固定开销**（经验 ~10 ms/step ⇒ ~305 s）会吃掉 **~30%** 的 1012 s 预算；GBS=128 ⇒ 3,815 步 ⇒ 开销降到 ~4%，且**大 batch 本身把 MFU 从 10–20% 抬到 25–35%**（= 把 `N` 上限从 ~24M 抬到 ~40M）。🚫 但 GBS 提高到 128 时**必须同步**：`warmup` 步数同比下调（保 warmup token 数不变）、LR 按 `√GBS` 或线性重定标一次（写进 `MEMORY_DATA.md`）。
   - **b) 必须启用 fused / chunked cross-entropy**（**硬前置**）：`V=129,408` 下 `GBS16×seq2048` 的 logits = **4.24e9 个元素** = **17 GB(fp32) / 8.5 GB(bf16)**，CE 读写 2–3 遍 ≈ **25–50 GB/step ≈ 8–15 ms @3.35 TB/s**（**TP1/DP1 无 TP 可切**，分块 CE 是唯一出路）。💡 这也是「embedding 的第二笔账」：**它不是参数账，是每-step 的内存/带宽账，且与 body 大小无关** —— 缩 body 缩不掉它。
   - **c) `layers` 取 14 的整数倍**：2B 的 pattern = **24 M + 4 `*` + 28 `-`（56 层）**，**最小完整周期 = 14 层 = `6M/1*/7-`** ⇒ 代理用 **`L = 14`（首选）或 `28`**，以**严格保持混合比例**（否则「代理 ≠ 同族结构」，迁移性论证要打折）；最终以 `sum(p.numel())` 实测 + 逐层类型清点为准，贴进 `MEMORY_DATA.md`。

9. ⭐ **评测（eval）的时间账 —— `T` 的第二约束（2026-10-06 补，用户追问「**要算上评测时间**」）**：
   - **公式**：`T = 6×86400 ÷ [ 步数 × s_step × (1+ε) ]`，`ε` = 评测 + ckpt 占的墙钟比例 ⇒ **`ε` 随「协议」差 3 个数量级**：

   | 评测协议 | 单次成本（`N≈18.5M` 例） | 次数/trial | `ε` | 512 组可行性 |
   |:--|:--|:--|:--|:--|
   | **in-process + 固定 bin + 末次 1 点**（≤20M token） | ≈ **9 s**（fwd 4.9 s + 610 步×5 ms + setup ~1 s） | 1 | **~1%** | ✅ |
   | 同上 **+ 中间 6–8 点**（每点 2M token，供 `MedianPruner`） | ≈ **1.8 s/点** | 8 | **~1.5%** | ✅ **净收益为正**（见下） |
   | **每 trial 起独立评测进程**（NeMo import 30–60 s） | **+30–60 s** | 1 | **4–7%** | ⚠️ 勉强 |
   | **每 trial 跑 `lm_eval`（Table 2/3 式）** | **20 min–2 h** | 1 | **120–710%** | ❌ **禁止**（512 组 ⇒ **170–1000 GPU·h/天 > 全天 144**） |

   - 🔑 **关键事实：eval 的前向 FLOPs 可忽略**（`fwd ≈ 2·N·tokens`；20M token 只 = 训练算力的 **0.6%**）⇒ 成本**几乎全在「固定开销 × 评测步数」与「进程启动」**。⇒ **硬规则**：eval 必须 **in-process**；单次 **≤20M token**（≈610 步 @GBS16）；**总评测点 ≤8**；🚫 不许每 trial 起新进程；🚫 `lm_eval` **只对搜索结束后的 top-K（K≤5）**跑（5×30 min = 2.5 GPU·h ≈ 全天预算 1.7%）。
   - ⭐ **中间评测是「负成本」**：1 个中间点 ≈ 2 s，而一次 prune 平均省 `0.4×1012 ≈ 400 s` ⇒ **只要 prune 率 > 1% 就回本**；`MedianPruner` 常砍 30–70% 的 trial ⇒ **等效 `T` ×1.25–1.5**（把 480 变成 600–720）⇒ **`MedianPruner` 要按「收益项」写进 `T` 预算，不是可选项**。
   - ⚠️ **seed 乘数（最易漏的时间项）**：`T=512` 是按 **1 seed/trial** 算的。噪声锚点 **σ=0.0469** 是 **2.2B/655M/3-seed** 的口径，**小代理的 `σ` 必须实测**（3 seed 跑同一先验配比）⇒ 若 `Δloss` 逼近 `σ` 而需要 3-seed 平均，**`T` 直接 ÷3（512 → 171）**。🚫 不许用「改判据 / 挑好看的 seed」代替补 seed。
   - 🚫 **ckpt**：搜索期间 `save_interval = 0`；**只对 top-K 存**（18.5M 的 bf16+Adam ≈ 150 MB/份 ⇒ 512 份 = 77 GB + NFS 写 1–5 s/次，可忽略）。

   > 📌 **`D=1B` 档 `T` 预算表（`N=18.5M`，已含 ε≈3%）**：`η=1e14` → **394（GBS16）/ 448（GBS128）**；`1.5e14` → **548 / 660**；`2e14` → **681 / 863**。⇒ **512 组要求 `η ≥ ~1.4e14`（GBS16）或 `≥ ~1.15e14`（GBS128）**，配 `MedianPruner` 后 **≈ 500–1200**。⇒ **`d=128/L=14`（18.5M = 2.220B 的 1/120、非-embed 的 1/1027）是「1B token × 512 组 × 24h」这条硬约束推出来的自然规模 —— 与 RegMix 选 1–2M 非-embed body 是同一个约束的不同解。**



---

### §0 当前主攻 + §0.6 R4阶段 —— 已被运维指令区改道方案覆盖

> §0.1-§0.4 已归档至 ARCHIVE_DATA_R_AND_R2_RESEARCH.md；§0/§0.6 的实验设计已被改道方案（小代理+BO）取代。

## 0. 🎯 当前主攻

> **R 阶段（只答两问）✅ 已收敛** → 产出 `run/DATA_RESEARCH.md` v1.1（事实层扎实）。
>
> | 节 | 状态 |
> |:--|:--|
> | §0.1 / §0.2 | ⏹ **历史**（R 阶段的两问，已完成；§0.2 已被 §0.4 取代） |
> | **§0.3** | 🔴 **当前主攻（LLM 侧）** —— P-8 数据方案 |
> | **§0.4** | 🔴 **当前主攻（视觉侧）** —— vision encoder 训练数据：去 HF 找更多通用图文对 |
>
> 原因：上一轮 R 的**事实层合格、结论层不合格**（两处，详见 §0.3 与 §0.4 开头）。
> **本轮两份都必须给出可执行的结论。**

---


---

## 📁 调研轮次已归档（**为省 prompt token**）

`§0.1 / §0.2 / §0.3 / §0.4`（R 与 R2 调研）的完整任务原文已移至 **`run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md`**。

- 这些**均已完成**；结论以 `DATA_RESEARCH.md` / `DATA_LEDGER.md` / `MEMORY_DATA.md` 为准。
- **需要时再去读归档**；**不要**把整份归档读进上下文。
- 当前主攻 = **§0.5 / §0.6 / §0.7**（见下方）。

## 0.6 🎯 R4 阶段 —— **P-8 数据配方：follow MiniCPM5 / Xmodel-2 的 WSD 双阶段配比**（运维 2026-10-02 指令）

> ### 定位
> 运维明确：**P-8 的数据方案要「follow MiniCPM5」** —— 即 **WSD 的两段各用不同配比**：
>
> | 阶段 | 数据源（运维给的假设） | 主次 |
> |:--|:--|:--|
> | **Stable**（WSD 的 S 段） | `Ultra-FineWeb`(**base**) · `UltraX-Preview` · `UltraData-Math` · `UltraData-Code` | **以前两者为主** |
> | **Decay**（WSD 的 D 段） | `Ultra-FineWeb-L3` · `UltraData-Math` · `UltraData-Code` · **`UltraData-SFT-2605`** · **`UltraData-SFT-Agent-2609`** | 适当配比 |
>
> **配比不是拍的，要做实验定** —— 由你（data agent）来设计并跑。

### 🔴 一条可能改变全局的发现（来自 `Xmodel-2/xmodel-2.tex:144-154`，请务必读原节）

Xmodel-2 的 decay 段配比搜索结论：

> - 把搜索空间收敛到**两个问题**：**① SFT 数据的总体占比；② SFT 内部的类别分布**
> - **跑了 400+ 次试验** → 最优 **SFT 占比落在 60%–69%**，实际取 **64%**
> - SFT-Mixed 由 **5 类构成：Mathematics / Code / Logic / Knowledge / Commonsense**（**CoT 归入 Logic**）
> - **数学与代码的「指令格式」数据 > 「预训练格式」数据**
> - SimHash 去重（bucket 1M）**+1.7%**；整体复杂推理 **+29.31%**

⚠️ **关键含义**：**SFT 数据是进到「预训练 decay 段」里的，而不是事后再做一遍独立的 SFT** ——
这与运维给的 decay 假设（含 `SFT-2605` + `SFT-Agent-2609`）**一致**，也与 MiniCPM 的路线一致。
→ **它模糊了 Stage (i)/(ii) 的边界**：**decay 段本身就是"带 SFT 数据的退火"**。
→ **必须在报告里点明这一点**（这是 P-8 配方的核心）。

**另一条法理依据**（供报告引用）：`xmodel-2.tex:142` 引 `ye2024datamixinglaws` ——
**「小模型上的配比实验可以有效迁移到更大模型」** → **所以我们可以在小规模上搜配比**，不必在全量上试。

### A. 先**核实**运维的假设（不许直接采信，也不许否掉）

1. **MiniCPM5 的 stable/decay 两段各用了哪些源、什么占比？**
   - 上轮结论是「模型卡**未公开逐源百分比**」→ **本轮再查**：模型卡 / 技术报告 / `openbmb/MiniCPM5` collection 的 dataset card / UltraData 平台论文（arxiv 2602.09003）。
   - **若仍查不到** → 写「未找到」+ 列出查阅清单，**但运维给的这张表就作为"待验证的工作假设"直接用**（见 B）。
2. **确认 `UltraX-Preview` 与 `Ultra-FineWeb`(base) 的关系**（上轮已知 UltraX 里有一支叫 `UltraX-Ultra-FineWeb`）→ **是否重复**？

### B. ⭐⭐ 配比搜索实验（**本轮的核心**）

**搜索设计（照 Xmodel-2 的思路收敛空间）**：

| 段 | 候选源 | 代理指标 | 备注 |
|:--|:--|:--|:--|
| **Stable** | `base` · `UltraX-Preview` · `Math` · `Code` | **Xmodel-2 Table 2 的 8 个**（Commonsense） | 运维假设"以 base / UltraX 为主" |
| **Decay** | `L3` · `Math` · `Code` · `SFT-2605` · `SFT-Agent-2609` | **Xmodel-2 Table 3 的 6 个**（Complex Reasoning） | ⚠️ **必查 SFT 占比**（Xmodel-2 是 **60–69%**） |

**两套代理指标的确切清单**（已从本地 tex 核出，照用）：
- **Table 2（8 个）**：`ARC-C` · `ARC-E` · `BoolQ` · `HellaSwag` · `OpenBookQA` · `PiQA` · `SciQ` · `Winogrande`（+ Avg）
  —— 出处 `Xmodel-2/xmodel-2.tex:198,207`
- **Table 3（6 个）**：`GSM8K` · `MATH` · `BBH` · `MMLU` · `HumanEval` · `MBPP`
  —— 出处 `Xmodel-2/xmodel-2.tex:73,253,260`

**执行要求**：
1. **不要在 2.2B 全量上试** —— 用**小模型 / 短跑**搜（依据 Data Mixing Laws）。
   **基线口径**：复用 Round 1/2 的 8 卡 setup 与 5000 步短地平线，或更短。
2. **每轮训练后跑上面两套指标**（**评测基建已就绪**：P-6 已把 `ckpt → HF → lm_eval 8 集` 打通，
   见 `MEMORY_PRETRAIN_2B.md`；Table 3 的 6 个需另接，评估一下工作量）。
3. **给出可执行的配比建议**（不是"趋势"，是**具体百分比**），并说明**试验次数与置信度**。
4. **明确 SFT 占比**：这是 Xmodel-2 说最关键的一个轴。

> ### 🎯 **用哪台机器 —— 运维定的规则（2026-10-02）**
> **配比实验用「它所服务的那个正式训练」所用的机器**（因为配比实验与正式训练之间有依赖关系）：
>
> | 配比实验服务于谁 | 用哪台 | 卡 |
> |:--|:--|:--|
> | **LLM pretrain（P-8，即 §0.6 的 WSD 双阶段）** | **`.29`** | LLM 的卡 |
> | **vision（若将来也做配比）** | **`.12`** | vision 的卡 |
>
> **→ 本节 §0.6 的配比实验用 `.29`**（运维原话：**LLM pretrain 的正式训练依赖配比实验**）。
> ⚠️ **`.29` 上的排期**：P-4R（1 卡，≤2h）→ **配比实验** → 恢复 P-5b。
> **三者都在 `.29`，需要串行/让卡 —— 请先出方案与 ETA，再由运维排。**
> ⚠️ **`.12` 上 vision 的 R9 正在用 8 卡 → 不要占 `.12`。**

### C. 交付物
1. **`run/DATA_MIX_RECIPE.md`**（新文件）：
   - 运维假设的**核实结论**（或"未找到"+采纳为工作假设）
   - **两段的配比建议**（具体百分比 + 理由 + 试验次数）
   - **代理指标的实测值**（Table 2 / Table 3 分项 + Avg）
   - **可复现命令**
2. **P-8 数据就绪清单**：每个源是否就位、缺多少、下载/切分 ETA。
3. 更新 `MEMORY_DATA.md` + `DATA_LEDGER.md` + git push。

### 完成判据
- [ ] 运维假设**已核实**（或明确"未找到"+ 列出查阅清单）
- [ ] **Stable 段**配比给出**具体百分比** + Table 2 实测
- [ ] **Decay 段**配比给出**具体百分比**（**含 SFT 占比**）+ Table 3 实测
- [ ] 报告里**点明"decay 段即带 SFT 的退火"**这一含义
- [ ] 🚫 **全轮不得出现领域化相关内容**（运维硬规矩）

---



---

### §1.1 数据落盘地图 —— 已归档（2026-10-06，详见 DATA_LEDGER.md）

## 1.1 数据落盘地图（实测背景 · 2026-10-01 勘定）

> 本节由**实地探查**得出，用于纠正本任务书成稿时对数据位置的误记。
> 每轮唤醒 / phase 复核时以此节为索引，`DATA_LEDGER.md` 为实测明细，二者互相印证；**最终一律以实测为准**。

**三块挂载 + 三条 HF 组织名线索**（HuggingFace 数据集按 `org/repo` 落盘）：

| 挂载 | 定位 | 关键内容 |
|:---|:---|:---|
| `/nas_train/app.e0031982/datasets/` | **多模态主库**（生产 + 派生） | `mvp-lab/`（LLaVA-OneVision-1.5 全家桶）、`baize-vision/`、coco/gqa/imagenet/laion2B/FineVision/LLaVA-Pretrain/MMMU… |
| `/nas_inference/app.e0031982/datasets/` | **只读源 / 下载中转**（**纯文本主力在此**） | `openbmb/`（Ultra-FineWeb-L3、UltraData-Code/Math/SFT-2605/SFT-Agent-2609）、`stanford-vision-lab/gpic` |
| `/nas_user/app.e0031982/datasets/` | 少量多模态 / 领域语料 | `mvp-lab/`（OV1.5 webdataset、OV2）、`BLIP3o/`、`UCSC-VLAA/`、`Amshaker/`、`ayoubkirouane/`、`cxmt/` |

**① 多模态主库 —— `/nas_train/app.e0031982/datasets/`**
- `mvp-lab/`（⚠️ 是连字符 **`mvp-lab`**，不是 `mvp_lab`）— LLaVA-OneVision-1.5 系列：
  - `LLaVA-OneVision-1.5-Instruct-Data`（183 个任务子集，SFT / 对齐主体）
  - `LLaVA-OneVision-1.5-Mid-Training-85M`（子集 coyo/datacomp1b/imagenet/laioncn/mint/obelics —— 即 phase0 已盘点项）
  - webdataset 派生：`-packed-webdataset` / `-webdataset` / `-webdataset-16384` / `Quick-Start-3M` / `MultiMixQA-opt46|47`
  - `LLaVA-OneVision-1.5-RL-Data`、`LLaVA-558K-Webdataset`、`LLaVA-NeXT-780k*`
- `openbmb/Ultra-FineWeb`（纯文本，**仅** Ultra-FineWeb 基础版，非完整 Ultra-* 套件）
- `baize-vision/`（en500k / eval5k —— vision agent 派生产出）
- 其他多模态（可选补充源）：`coco`、`gqa`、`imagenet-1k`、`laion2B-en-aesthetic`、`FineVision`(188 子集)、`LLaVA-Pretrain`(664 子集)、`MMMU`、`ocr_vqa`、`textvqa`、`vg`、`conceptual-captions-12m-webdataset`、`LLaVA-CC3M-Pretrain-595K`、`LLaVA-Instruct-150K`
- 非数据（勿混）：`stanford-corenlp-full-2016-10-31`（NLP 工具，非斯坦福视觉数据）

**② 纯文本主力 —— `/nas_inference/app.e0031982/datasets/openbmb/`**
- `Ultra-FineWeb-L3`（Stage(i) 主体）、`UltraData-Code` / `UltraData-Math`（退火源）、`UltraData-SFT-2605` / `UltraData-SFT-Agent-2609`（Stage(ii) SFT）
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/openbmb`，实际在 **`/nas_inference`** 挂载。

**③ 斯坦福视觉数据 —— `/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic`**
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/stanford-vision-lab`，实际在 **`/nas_inference`**。`gpic`（含 train / test / reference_stats）。

**④ 少量多模态 / 领域 —— `/nas_user/app.e0031982/datasets/`**
- `mvp-lab/`：`LLaVA-OneVision-1.5-Mid-Training-85M-webdataset`、`LLaVA-OneVision-2-Data`、`ov2_quickstart`
- `BLIP3o/BLIP3o-Pretrain-Long-Caption`、`UCSC-VLAA/Recap-DataComp-1B`、`Recap-DataComp-1B`
- `Amshaker/Mobile-O-Pre-Train`、`ayoubkirouane/CircuitVQA`
- `cxmt/`（EDA / 电路相关标注与 benchmark —— ~~phase3 领域排查时可查~~ **🚫 该线已取消，不再排查**）

> 对数据 agent 的影响：phase0 已盘点的主路径（`/nas_inference/openbmb`、`/nas_train/datasets/mvp-lab`）正确；
> 但 phase0 尚未覆盖 `②` 里的 Ultra-FineWeb 基础版（`/nas_train/.../openbmb`）、`③ stanford-vision-lab/gpic`、`④ /nas_user` 整块 —— 后续 phase 复核时把这些补齐进 DATA_LEDGER。

---


---

### §2 阶段与推荐执行顺序 —— 已归档（2026-10-06，多数阶段已完成）

## 2. 阶段与推荐执行顺序

```
推荐顺序： 【🎯 当前】phase1 validate（含 ① SFT-2605 重下） → phase0 inventory ✅ → phase5 isolation ✅ → phase2 text → phase4 mm → phase6 handoff
🚫 phase3 domain —— **已取消，从流水线移除**（见运维指令区 ②）
```

> **为什么 phase5（污染隔离）排在最前**：它必须在**任何"训练可消费产物"产出之前**就位。
> 如果先切了数据再立闸，已经切好的数据要全部重扫、甚至重切——**白做一遍**。

| 阶段 | 做什么 | 完成判据 |
|:---|:---|:---|
| **R** `research` 🎯 **当前主攻** | 用 `cimi-search` / `cimi-fetch` **只回答 §0 的两个问题**（LLM 数据够不够+配比 / Vision 数据够不够+配比） | `DATA_RESEARCH.md`：两问各四小项全有结论 |
| **phase0** `inventory` ✅ | 对 `/nas_inference` 与 `/nas_train` 上每条数据线**实测**：文件数、总字节、目录结构、抽样看格式；确认哪些路径真实存在 | `DATA_LEDGER.md` 初版；**与方案 §1 的差异逐条列出** |
| **phase5** `isolation` | 建 EDA-Eval-PyAether 的黑名单指纹 + 训练集侧扫描脚本 + SFT 同闸 | `CONTAMINATION_CHECK.md` 初版 + 可复用脚本 |
| **phase1** `validate` | 下载完整性（parquet 全量可开 / tar 可解 / shard 无缺号）；损坏清单 | 损坏/缺失清单 + 校验命令 |
| **phase2** `text` | 通用文本分词打包成 `.bin/.idx`（stable 主体 + 退火源），**复用 Round 1 脚本** | 训练实测能加载并跑 10 步冒烟 |
| **phase3** `domain` 🚫 **已取消** | ~~EDA 领域语料排查（有哪些、在哪、能否导出/授权）→ 确认后入库并过闸~~<br>**运维 2026-10-01 正式取消**：评测 prompt 由 docstring 生成、**与语料天然同源**，"把测试集放进训练集"没有意义 | —（不再产出） |
| **phase4** `mm` | 多模态下载完成后：校验 → 统计 → 切子集 → webdataset 打包 → held-out 评估集 | Stage (iii) 能直接开跑 |
| **phase6** `handoff` | 清单终版 + 污染报告终版 + 结果 HTML + 可复现命令 | 可交接给训练 |

---


---

### §4 git 与共享工作区规则 —— 已归档（2026-10-06，详见 AGENTS.md + 收尾铁律）

## 4. git 与共享工作区规则

### 4.1 前提：这是一个**共享工作副本**

**本任务、vision 任务、pretrain 任务共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

- **只需一个人 pull，其余立刻看到**：别的 agent 拉取后，你读到的 `$TASK_MD` 与所有文件同步更新。**不要重复 pull。**
- 工作区里**陌生的未提交改动很可能是别的任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉别人的成果。
- 多个 loop 各自 `git add -A && commit && push`（每 5 小时），**会互相把对方在途文件一起提交**，这是既有设计的已知副作用，**不要去"修正"它**。

### 4.2 你的 git 操作规程

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_DATA.md DATA_LEDGER.md CONTAMINATION_CHECK.md run/data_pipeline/ daily-memories-data/`
   🚫 **不要用 `git add -A`**——会把别的任务的在途文件卷进你的提交。
3. 若 behind / diverged：`git pull --rebase origin main`。
   - `cannot rebase: You have unstaged changes` → 是**多方在途改动**：先 commit 自己要提交的文件再 rebase；🚫 不要 stash/丢弃别人的改动。
   - `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：等 30–60 秒重试（≤3 次）；仍失败就记一行流水并**跳过本次 git 操作**。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind。
5. 流水记一行 git 结果。

> 参照：vision agent 在 `daily-memories-vision/2026-10-01.md:198` 用 `git pull --rebase` 恢复过，沿用同一做法。

### 4.3 数据产物**不入库**

`.bin/.idx`、webdataset tar、原始数据集**一律不提交 git**。只提交：`doc/` 下的文本（md/html/json）与 `run/` 下的**脚本**。
在报告与流水中写清产物的**绝对路径 + 规模 + 校验和**，训练侧据此取用。

---


---

### §5 资源与约束 —— 已归档（2026-10-06，资源分配见运维指令区各块）


- **节点**：本 agent 常驻 `10.239.2.12`（主机 `whag0pgpuap12`）；数据在 NFS（`/nas_inference` 只读源、`/nas_train` 产出）。
- ⚠️ **与 GPU 任务共享 NFS 与带宽**：
  - **本节点 `.12` 有 2 个 HF 下载任务在跑**（`hf download`，2026-10-01 实测，各已运行约 1 小时+）：
    1. `mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M` → 写入 `/nas_train/app.e0031982/datasets/`（多模态下载进行中）
    2. `stanford-vision-lab/gpic` → 写入 `/nas_inference/app.e0031982/datasets/`（带 HF token；⚠️ token 已暴露在进程参数里，建议轮换，勿写进文档/日志）
    **下载期间不要做重 I/O / 全量扫描**，会互相拖慢
  - vision 任务需要一次"**无争用的干净吞吐测量**（R2-4）" → 启动重 I/O 前先读 `run/MEMORY_VISION.md` 看它进度，**优先避让**
  - pretrain 任务在 `10.239.2.29` 跑训练（另有协调规则）
- **不占用 GPU**（本任务不是 GPU 任务）；也**绝不杀他人进程**。
- **每轮唤醒单次预算 ≈ 25 分钟**；有长时任务时把 `WAITING` 置 1 让 loop 拉长睡眠。

---
