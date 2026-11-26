# BaiZe 2.22B Mamba2-hybrid 正式训练计划 v5（Stable 段 1.5T token）

> 生成：2026-10-18 · 纯写作（零 GPU）· commit 前缀 `pretrain plan-v5:`
> 配套 HTML：`reports/report_pretrain_formal_v5_plan_zh.html`
> 数据源：`DATA_LEDGER.md`（唯一数据源）· 吞吐源：T3/P-9.6–9.7 实测 249K tok/s
> ⚠️ **数据口径（2026-10-18 用户纠正）**：分词按**数据源全量**（当前 `en_v1_4` 110/110 shard）执行；**1.5T 是训练 token 预算，不是分词目标/上限**。不得按 500B/1.5T 截断分词。


---

## 0. 一页结论

| 项 | 值 |
|:--|:--|
| 模型 | BaiZe 2.22B Mamba2-hybrid（56 层 = 52 Mamba2 + 4 full_attention）|
| 总训练量 | **1.5T token**（Stable 段；warmup 2000 步 ≈ 4B tok 另计）|
| 阶段 | S1（500B, en_v1_4 单源, 2M tok/step）→ S2（1T, 混料, 4M tok/step）|
| 步数 | S1 250,000 + S2 250,000 = **500,000 步**（+ 2,000 warmup）|
| 学习率 | warmup 2000 步后**恒定 1e-3**（S1/S2 全程同一常数，不做 cosine/decay）|
| ckpt | 每 2000 步 → **250 个**（S1 125 + S2 125）|
| 评测 | 每个 ckpt **CS8**（Common8, 0-shot, raw accuracy + Avg）|
| 基准吞吐 | **249K tok/s**（TP1/DP8/MBS2/seq4096/GBS1024/bf16, T3/P-9.6–9.7 实测）|
| 纯训练 | **69.7 天**（249K 基准）|
| 含评测日历 | **约 74–76 天**（+ 250×CS8 12.5–20.8h [假设] + 5% 余量）|
| tokens/param | 1.5T / 2.22B ≈ **676 tok/param** |

**次序裁定**：✅ **采纳** decay → 1M 长上下文（ABF）→ SFT/RL。1M 阶段独立 ETA（见 §6），不与 1.5T Stable 混算。

**主要风险**：① LR 恒定后期可能欠拟合 ② 2M→4M batch 跳变 loss 断点 ③ en_v1_4 尚未分词 ④ 单机连续 ~70 天故障恢复 ⑤ 1M 阶段吞吐塌陷 ⑥ 250 ckpt 存储/评测开销。

**前置条件**：① en_v1_4 分词 500B tok（🟢 已实测：已下 4.08TB ≈ 1.40T tok，余量 2.80×，16 并发 ≈ 1 天，见 `PLAN_V5_DATA_PREREQ.md`） ② S2 混料源就绪（code 411B ✅ / math 303B ✅ / HQ ≥1.12T 可溯源 ✅，含 [待核] 项合计 ≈1.415T，余量 ≥1.42×）。

---

## 1. 模型与并行配置

| 参数 | 值 | 来源 |
|:--|:--|:--|
| 架构 | Mamba2-hybrid | BaiZe Stage(i) |
| 总参数 | 2.22B | 实算（embed 265M×2 + 56 层 + norm）|
| 层数 | 56（52 Mamba2 + 4 full_attention）| 架构定义 |
| hidden_size | 2,048 | P-3/P-8 config |
| vocab_size | 129,408 | DeepSeek tokenizer（pad 129408 / eod 129280）|
| seq_length | **4096** | 用户直令（2¹²，非 4094）|
| 并行 | **TP1 · DP8** | T3/P-9.6 最优 |
| micro_batch_size | 2 | T3 实测最优 |
| global_batch_size | S1: 488 / S2: 976 | 由 tok/step 推导（见 §2）|
| 精度 | bf16 | 基准配置 |
| torch.compile | ✅ default | P-8/v2 已验证 |
| 优化器 | AdamW fused | P-8 最终选择（Muon 在 44B 发散，不用于 stable）|

---

## 2. 两阶段配方表

| 项 | S1 | S2 |
|:--|:--|:--|
| 每 step token | **2M tok** | **4M tok** |
| 总 token | **500B** | **1T** |
| 步数 | 500B/2M = **250,000** | 1T/4M = **250,000** |
| seq × GBS | 4096 × 488 = 2.00M | 4096 × 976 = 4.00M |
| MBS / DP | 2 / 8 → grad accum = 31 | 2 / 8 → grad accum = 61 |
| 学习率 | 1e-3 恒定（warmup 2000 步线性）| 1e-3 恒定 |
| 数据 | en_v1_4 **100%** | code 20% + math 1–2% + HQ 预训练 |
| 每 step 时间 | 2M/249K = **8.0 s** | 4M/249K = **16.1 s** |
| 纯训练时长 | 250K×8.0 = 557.9h = **23.2 天** | 250K×16.1 = 1,115.6h = **46.5 天** |
| ckpt 数 | 125 | 125 |

**warmup**：2000 步线性 0→1e-3，消耗 2000 × 2M = 4B tok（S1 预算内）。

**S1→S2 切换**：batch 从 2M 跳到 4M（GBS 488→976），grad accum 31→61，per-step 8.0→16.1s。切换时记录 loss 断点（预期 loss 短暂下降，因有效 batch 增大）。

---

## 3. 数据配比与来源

> 唯一数据源：`DATA_LEDGER.md`（2026-10-01 实测盘点 v0）

### 3.1 S1 数据

| 源 | 需求 | 可用 | 状态 | 余量 |
|:--|:--|:--|:--|:--|
| en_v1_4 | 500B tok | ≈2.31T tok（6.75T bytes, 56,461 文件, 实测 0.343 tok/parquetB）| 🟠 86/110 shard 已下（≈4.08TB ≈ 1.40T tok）, **未分词** | 2.80×（已下部分）|

**前置**：① 续传剩余 25/110 shard（proxy .23→hf-mirror 已实测 200）② 分词 500B tok（`preprocess_data.py` → `.bin/.idx`）。**已实测**：端到端 375K tok/s/进程，16 并发 ≈ 1 天切完 500B（见 `PLAN_V5_DATA_PREREQ.md`）。已下 4.08TB ≈ 1.40T tok，余量 2.80×，不依赖续传即可开工。

### 3.2 S2 数据

| 源 | 需求 | 可用 | 状态 | 余量倍数 |
|:--|:--|:--|:--|:--|
| code（UltraData-Code）| **200B**（20%）| 411B（L2 355B + L3 56B）| ✅ 已下满 | **2.06×** |
| math（UltraData-Math）| **10–20B**（1–2%）| 303B（L1 184B + L2p 32B + L3 87B）| ✅ 已下满 | **15–30×** |
| HQ 预训练（组合）| **780–790B**（~79%）| — | — | — |
| ├ ultraweb_en（base）| — | ≈1.12T tok（2.66T, 2048 文件）| ✅ 已下满 | — |
| ├ l1_en_hq | — | 152B tok **[待核]**（478G, 6006 文件；字节可溯源 DATA_LEDGER §0，token 数为估值）| ✅ 已下满 | — |
| ├ zh | — | 112B tok **[待核]**（324G, 256 文件；字节可溯源 DATA_LEDGER §0，token 数为估值）| ✅ 已下满 | — |
| └ UltraX | — | 31B tok ⚠️ **[待核]**（DATA_LEDGER 记 UltraX-Preview ≈100B/487G，与 31B 不符）| 🟡 见注 | — |
| **HQ 合计** | 780–790B | **≥1.12T 可溯源**（含 [待核] 项 ≈1.415T）| ✅ | **≥1.42×**（可溯源）；含待核项 1.79–1.82× |

**瓶颈**：HQ 预训练余量最低，但充足——即便**只算可溯源的 ultraweb_en 1.12T**，对 780–790B 也有 1.42–1.44× 余量；code 余量 2.06×，math 极充足。**溯源**：code/math/ultraweb_en 的 token 数在 DATA_LEDGER（D10/§0）有出处；l1_en_hq(152B)/zh(112B)/UltraX(31B) 的 token 数**不在 DATA_LEDGER**（台账只有字节 478G/324G/487G），系用户令估值 → 标 [待核]，待 data 线分词核实回填。

---

## 4. 时长估算

### 4.1 基准

- **基准吞吐 = 249K tok/s**（来源：T3/P-9.6–9.7「P-8 最优 = TP1·MBS2·bf16 = 249K tok/s」）
- ⚠️ **不要把 298.6K tok/s 当成本模型基准**：那是 Xmodel-2.5 80B decay 在 .29 的实测（seq 3712/GBS 960），模型与序列都不同，只能当同机上限参考。
- 基准 1 step = 4096 × 1024 = 4.19M tok → 16.84 s/step

### 4.2 纯训练（按 249K）

| 阶段 | 计算 | 时长 |
|:--|:--|:--|
| S1 | 500B / 249K = 2,008,032s | 557.8h = **23.2 天** |
| S2 | 1T / 249K = 4,016,064s | 1,115.6h = **46.5 天** |
| **合计** | 1.5T / 249K | **1,673.4h ≈ 69.7 天** |

### 4.3 吞吐敏感性表

| 吞吐 | 1.5T 纯训练 | 说明 |
|:--|:--|:--|
| 218K tok/s | **79.6 天** | P-9.1 早测值（疑有争用，保守下界）|
| **249K tok/s** | **69.7 天** | T3/P-9.6–9.7 基准 |
| 280K tok/s | 62.0 天 | 若 S1 纯 web 短样本、packing 更满 |
| 320K tok/s | 54.3 天 | 需 FP8 / 更优 kernel（T3 实测 FP8 在 TP1 未提速）|

### 4.4 FLOPs 交叉验证

- 总 FLOPs = 6 × N × T = 6 × 2.22e9 × 1.5e12 ≈ **2.0 × 10²²**
- 8×H100 bf16 dense peak = 8 × 989 TFLOPS = 7.912 × 10¹⁵ FLOPS
- 249K tok/s 反推 MFU = 6 × 2.22e9 × 249K / 7.912e15 ≈ **41.9%**
- FLOPs 口径（6ND, 同 MFU）→ 2.0e22 / (7.912e15 × 0.419) ≈ **33.2 天**
- ⚠️ **两个口径差 2.1×**：token 口径来自真机实测吞吐（含 SSM scan、通信、优化器、packing 填充与 dataloader），FLOPs 的 6ND 只算 dense matmul（Mamba2 的 scan/conv 不计入）。**结论以 token 吞吐口径（69.7 天）为准，FLOPs 仅作 sanity check。**
- MFU 30% → 97.4 天；MFU 37% → 79.0 天。

### 4.5 含评测的真实日历时间

| 项 | 时长 | 说明 |
|:--|:--|:--|
| 纯训练 | 69.7 天 | 249K 基准 |
| 250 次 CS8 评测 | 12.5–20.8h [假设] | 3–5 min/ckpt × 250（8 GPU 并行评测流程）|
| 启动/重启/故障余量 | 5% × 69.7 = 3.5 天 | 保守 |
| **日历合计** | **约 74–76 天** | — |

---

## 5. ckpt 与评测

| 项 | 值 |
|:--|:--|
| 保存间隔 | 每 **2000 步** |
| 总 ckpt 数 | **250**（S1: 125, S2: 125）|
| 每个 ckpt 大小 | ≈2.7 GB（model.safetensors, bf16 2.22B）|
| 存储总量 | 250 × 2.7 ≈ **675 GB** [假设]（需确认 NFS 余量：/nas_train 31T free）|
| 评测口径 | CS8（Common8, 0-shot, raw accuracy + Avg）|
| CS8 集 | ARC-Challenge, ARC-Easy, BoolQ, HellaSwag, OpenBookQA, PiQA, SciQ, Winogrande |
| 评测耗时 | 3–5 min/ckpt [假设]（8 GPU 并行 lm-eval）|
| 评测调度 | 每 2000 步保存后立即跑 CS8；结果记入 scaling 曲线 |

> ⚠️ ckpt 存储需规划：675 GB 在 31T free 中可行，但建议保留最新 N 个 + 定期清理旧 ckpt。

---

## 6. 长上下文注入（ABF）

### 6.1 注入方案 = ABF（不是 YaRN），分两层

**推理侧（零训练）**：
- `rope_theta` 1e4 → **1e6**
- `max_position_embeddings` 4096 → **1,048,576**（1M）
- 沿用 `baize_b1_longctx_extend.py` 的 B1 写法
- 既有实测：PPL 4K=83.24 → 128K=54.66 → 1M=55.42，全程 53–56 **无退化**
- 机制：**56 层里只有 4 层 full_attention 吃 RoPE**，Mamba2 层无位置编码 ⇒ ABF 只需适配 4/56 层 → hybrid 相对 dense 的结构性优势

**训练侧（真正注入）**：
- ABF 免训练只保 PPL，**不产生 needle/多跳检索能力**（B1 已证 passkey 0%，且明确"是模型能力问题不是 ctx 问题"）
- 1M 能力必须在**长上下文续训阶段**用真实长文档训练，不能只靠配置外推

### 6.2 ABF vs YaRN 对比

| 方案 | 代价 | 收益 | 结论 |
|:--|:--|:--|:--|
| **ABF** | PPL@4K **+10.5%**（75.36→83.24）| 免训练到 1M；零依赖（改 config）| ✅ **v5 采用** |
| YaRN | 需 rope_scaling 参数（factor/original_max_pos/attn_factor）| 对只 4 层 attention 的 hybrid 收益有限 | 仅作对照/兜底 |

> 仓库既有结论：hybrid 应沿用 B1 的 ABF 写法，dense 才需 YaRN/rope_scaling（`ARCHIVE_OPERATOR_PRETRAIN.md`）。

### 6.3 次序评估：decay → 1M → SFT/RL

| 段 | 评估 | 理由 |
|:--|:--|:--|
| decay 在 1M 前 | ✅ 合理 | 先让 Stable 段收敛（LR 从 1e-3 降下来），再进长上下文 |
| 1M 在 SFT/RL 前 | ✅ 合理 | 对齐阶段样本要"装得进"上下文，长上下文能力必须先具备 |
| 长上下文 = 预训练的一部分 | ⚠️ 要求 | 用 pretraining 数据（长文档/代码库/多文件仓库），**不是 SFT 数据** |

**裁定**：✅ 采纳 decay → 1M → SFT/RL。

### 6.4 风险与对策

| 风险 | 对策 |
|:--|:--|
| 1M 吞吐崩塌（attention ~77%, 1M PPL 单次 172s）| seq 课程：32K→128K→256K→512K→1M 阶梯；每档 token 预算；"ABF 外推 + 只在 128K 训练、1M 靠外推"降本方案 |
| decay 后 LR 已低，长上下文学不动 | 长上下文阶段**单独设 LR**（小幅回升，需用户批准，不得擅改）|
| SFT/RL 前无能力门禁 | 必须做 needle/RULER/长文档 QA 门禁，不达标不进 SFT |

### 6.5 1M 阶段独立 ETA（单列，不与 1.5T Stable 混算）

- seq 课程预算 [假设]：32K(50B) + 128K(100B) + 256K(50B) + 512K(20B) + 1M(10B) = 230B tok
- 吞吐估算：1M 阶段 attention 占比高，吞吐预计降至 **30–80K tok/s** [假设]（1M PPL 单次 172s 反推）
- 粗估时长：230B / 50K = 4,600,000s ≈ **53 天** [假设，待实测修正]

---

## 7. 风险与待拍板项

| # | 风险 | 影响 | 对策 / 监控判据 | 状态 |
|:--|:--|:--|:--|:--|
| R1 | **LR 1e-3 恒定**后期欠拟合 | S2 后半段 loss 不降 | 每 2000 步监控 loss；若 S2 后半段仍单调不降 → 建议加短 decay（**需用户批准，不得擅改**）| 🟡 待监控 |
| R2 | **2M→4M batch 跳变** loss 断点 | S1→S2 切换时 loss 短暂波动 | 记录断点；预期 loss 短暂下降（有效 batch 增大）；若 loss 跳升 >0.3 → 暂停并排查 | 🟢 低风险 |
| R3 | **en_v1_4 分词** | S1 数据管线 | 已实测：端到端 375K tok/s/进程，已下 4.08TB（≈1.40T tok）余量 2.80×，16 并发 ≈ 1 天切完 500B（见 `PLAN_V5_DATA_PREREQ.md`）| 🟢 已实测 |
| R4 | **250 ckpt 存储/评测** | 675 GB 存储 + 12.5–20.8h 评测 | 保留最新 N + 定期清理旧 ckpt；评测并行化 | 🟢 可控 |
| R5 | **单机 ~70 天故障恢复** | 节点宕机/NCCL/磁盘故障 | 健壮 ckpt + `--resume`；每 2000 步存 ckpt（最多丢 4B tok）；运维监控 | 🟡 需预案 |
| R6 | **1M 吞吐塌陷** | 长上下文阶段极慢 | seq 课程阶梯；ABF 外推兜底；1M 阶段独立 ETA（§6.5）| 🟡 待实测 |
| R7 | **长上下文阶段 LR** | decay 后 LR 太低学不动 | 单独设 LR（小幅回升，**需用户批准**）| 🟡 待拍板 |

---

## 8. 里程碑表（按周，249K 基准）

> S1 = 23.2 天 ≈ 3.3 周 · S2 = 46.5 天 ≈ 6.6 周

| 周 | 阶段 | 步数范围 | ckpt # | 预期 CS8 [假设] |
|:--|:--|:--|:--|:--|
| W1 | S1 | 0–60K | 0–30 | ~35–40% (起步) |
| W2 | S1 | 60K–120K | 30–60 | ~40–45% |
| W3 | S1 | 120K–180K | 60–90 | ~45–48% |
| W3.3 | S1 | 180K–252K | 90–125 | ~48–50% (S1 终) |
| W4–5 | S2 | 252K–372K | 125–185 | ~50–53% |
| W6–7 | S2 | 372K–502K | 185–250 | ~53–56% (S2 终) |
| W10 | decay | — | — | LR 1e-3→1e-5, ~5 天 |
| W10–17 | 1M 长上下文 | — | — | seq 课程, ~53 天 [假设] |
| W17+ | SFT/RL | — | — | Stage(ii) |

> ⚠️ CS8 预期区间为 [假设]（基于 P-6/P-8 scaling 外推：44.4B→49.21%, 1.5T→待实测）。Xmodel-2.5（1.4T tok）CS8=65.40% 可作远期参考。

---

## 附录：可行性问题正面回答

**Q1: LR 1e-3 恒定是否会欠拟合？**
- 历史对照：P-8 用 3e-3（44B, 发散后换 1e-3 AdamW 重启）；decay run 用 1.67e-3→1e-5。
- 判断：1e-3 介于 P-8（3e-3）和 decay min（1e-5）之间，**合理但偏保守**。1.5T token 量大，恒定 LR 可能在 S2 后半段收敛放缓。
- 监控判据：每 2000 步记录 loss；若 S2 后半段（步 370K+）loss 仍单调不降 → 建议在 S2 末端加短 decay（需用户批准）。

**Q2: batch 从 2M 跳到 4M 怎么处理？**
- seq 4096 / MBS 2 时：2M tok → GBS 488（grad accum 31）；4M tok → GBS 976（grad accum 61）。
- per-step 时间：8.0s → 16.1s（@249K）。
- 切换记录：S1 最后一个 ckpt 的 loss vs S2 第一个 ckpt 的 loss（断点监控）。

**Q3: en_v1_4 数据量够吗？**
- 需 500B tok，全量 ≈2.31T tok（实测 0.343 tok/parquetB × 6.75TB；台账 ≈2.2T 成立 +5.1%）。500B = 全量的 21.6%。
- 当前：86/110 shard 已下（≈4.08TB ≈ 1.40T tok），**已下部分就够 500B**（余量 2.80×）。
- 前置：续传剩余 25 shard（proxy .23→hf-mirror 已实测 200 ✅）+ 分词 500B tok。**已实测**：端到端 375K tok/s/进程，16 并发 ≈ 1 天切完 500B（见 `PLAN_V5_DATA_PREREQ.md`）。已下部分余量 2.80×。

**Q4: S2 混料供给够吗？**
- code 200B：UltraData-Code 411B ✅（余量 2.06×）
- math 10–20B：UltraData-Math 303B ✅（余量 15–30×）
- HQ 780–790B：ultraweb_en(1.12T ✅可溯源) + l1_en_hq(152B [待核]) + zh(112B [待核]) + UltraX(31B [待核，台账≈100B]) = 1.415T；仅可溯源项 1.12T 已给 1.42–1.44× 余量，含待核项 1.79–1.82×
- **瓶颈 = HQ 预训练**（余量最低，但充足：仅可溯源 1.12T 已覆盖 780–790B，底线 1.42×）
