# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_PRETRAIN_2B.md` / `daily-memories/` / `EXPERIMENTS_*`）。本节为「无」时按下方 Round 2 默认顺序推进。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_PRETRAIN.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。

> 📦 **2026-10-06 已归档**：「B1 ctx 扩到 1M」+「hybrid 优势论证」两个运维块均已完成，原文见 `ARCHIVE_OPERATOR_PRETRAIN.md`。结论：PPL 1M=55.42 无退化，bottleneck=(c) attention O(n²) ≥512K，目标 ctx=32K–128K，advantage report 已交付。

> 📦 §运维指令·2026-10-07⑤（T1 bf16-SSM重跑+T2公平对比+T3提速+T4效果）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：T1/T2 v2 ✅ warmup-corrected — float32 vs bf16 SSM **无差异**(1.00×)，hybrid 比 dense 快 2.8-4.3×(128K-256K)，「dense 3.3× faster」是 warmup 假象已撤回；T3 短名单(C1 FP8-TP1/C2 recompute+MBS4) + T4 短名单(Q1 100B tokens/Q2 data mixture) 已交付。需要时再读。

> 📦 §运维指令·2026-10-07④（5份研究型HTML报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：5份报告(r1-r5)全 ✅ 交付，r4 去重完成。需要时再读。

> 📦 §运维指令·2026-10-07③（hybrid ctx扩2M-16M+显存归因）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.11-F ✅ — 2M@0.6 SERVED(TTFT=427s), 4M@0.85 TIMED OUT(servable but ~33min), 8M/16M单卡不可服务；VRAM恒定=mem-frac=0.3预分配假象(0.6→76GB)；V4② bf16 vs f32 1.67× **已更正为warmup假象**。需要时再读。

> 📦 §运维指令·2026-10-07②（长上下文推理成本矩阵 128K-1M）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.11-E COMPLETE — Dense OOMs@512K(KV pool=455K tokens), Hybrid serves 1M@~26GB(near-constant = `--mem-fraction-static 0.3` 预分配 ~24GB, 与 ctx 无关); 128K-256K Dense faster 1.7-3.3x prefill / 2.2-2.6x decode。**sglang flag 沿用**：`--mem-fraction-static 0.3 --attention-backend flashinfer --mamba-ssm-dtype float32` + `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。需要时再读。
> 📦 §运维指令·2026-10-07（📊 交付：昨夜工作汇报 HTML）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：report_10_07_pretrain_overnight.html 已由 #164 交付(26.5KB,自包含,全自检过)。需要时再读。


### 🆕🆕 运维指令 · 2026-10-09（⚡ **T3 提速验证：立即在 .29 空闲 GPU 上跑 C1/C2/C2+**）· **最高优先 — R3 BO 已完成，8 卡全空，P-8 暂缓，正是跑实验的时候** · 用户直令

> **用户直令（2026-10-09）**：「T3 报告写了 2 天了还没跑，.29 全空，跑起来」
>
> **现状**：
> - .29 8×H100 **全空**（0 MiB / 0% util），R3 BO 已完成，P-8 暂缓令未撤 → **空窗期正好利用**
> - T3 短名单（`report_pretrain_t3_train_speed_shortlist.html`）列了 C1–C5 候选，**一个都没跑**
> - P-9.6② 已证明 FP8 在 M=65536 转正（s=1.21–1.24, 235K tok/s），但用的是 TP4（通信开销 -6% vs TP1 的 249K）
> - **核心问题**：FP8 能不能在 **TP1**（无通信税）上转正？如果能，就能同时拿到 FP8 加速 + 长上下文 + >249K
> - **关键阻碍**：TP1 下 MBS4 OOM（79.8GB），seq8192 OOM → M 上不去 → **recompute 是唯一可能解锁的杠杆**
>
> **🔑 解冻 recompute**：此前 launcher 只暴露 MBS/TP/SP/seq/precision，recompute 属于「B 类冻结」。**本指令解冻**：允许你扩展 `pretrain_launcher.py` 添加 `--recompute-num-layers` 参数，在 recipe 的 `model_config()` 中设置 `recompute_granularity="full"` / `recompute_method="uniform"` / `recompute_num_layers=N`。改完 commit。
>
> **测试顺序（按价值排序，每点 60 步，`--save-interval 0`，不存 ckpt）**：

**Test 1（C2）: TP1·MBS4·seq4096·recompute·bf16 — recompute 能否解锁 MBS4 on TP1？**
- 配置：TP=1, DP=8, MBS=4, seq=4096, GBS=1024, bf16, `--recompute-num-layers 28`（56 层的一半）
- 基线对照：P-9.2 TP1·MBS4 无 recompute = OOM 79.8GB；P-9.7 TP1·MBS2 = 54.7GB / 249K tok/s
- **判据**：VRAM < 80GB 且 60 步 rc=0 → **recompute 解锁成功**；OOM → recompute 不够，跳到 Test 4
- 成本：~0.5 GPU·h
- **如果成功**：报 ms/iter + tok/s + peak VRAM + loss（对比 P-9.7 baseline 16,841.9 ms/iter / 249K）

**Test 2（C2+）: TP1·MBS4·seq8192·recompute·bf16 — M=32768 on TP1，命中 FP8 交叉点**
- 配置：TP=1, DP=8, MBS=4, seq=8192, GBS=512, bf16, `--recompute-num-layers 28`
- M = 4×8192 = 32768 = FP8 交叉点（P-9.4 微基准 M*≈30–32K）
- **前提**：Test 1 成功才跑
- **判据**：VRAM < 80GB 且 60 步 rc=0 → **M=32768 on TP1 落地**；OOM → seq8192 放不下，回退 Test 1 结果
- 成本：~0.5 GPU·h

**Test 3（C2+FP8）: TP1·MBS4·seq8192·recompute·FP8 — 🎯 梦幻配置**
- 配置：同 Test 2 + `--precision bf16_with_fp8_delayed_scaling_mixed` + `CUDA_DEVICE_MAX_CONNECTIONS=1`
- bf16 基线 = Test 2 的 ms/iter
- **判据（预注册）**：`s = t_bf16 / t_fp8 > 1.05` → **FP8 在 TP1 转正** → P-8 最优配置 = 此配置
- **如果 s > 1.05**：FP8 加速 + TP1 无通信税 + seq8192 长上下文 = **三合一**，可能 > 249K tok/s
- **如果 s ≤ 1.05**：FP8 在 M=32768 也不够，定论 = TP1 上 FP8 不可行
- 成本：~0.5 GPU·h

**Test 4（C1）: TP1·MBS2·seq4096·FP8 — 快速确认（预期失败但便宜）**
- 配置：TP=1, DP=8, MBS=2, seq=4096, GBS=1024, FP8, `CUDA_DEVICE_MAX_CONNECTIONS=1`
- M = 2×4096 = 8192，远低于 FP8 交叉点 → **预期 s < 1.0**（P-9.4 微基准 M=8192 s≈0.90）
- **为什么仍跑**：这是 P-8 baseline 配置（249K），如果 FP8 在这里意外不降速（s≈1.0），说明 FP8 overhead 可忽略，对 Test 3 的解读更有信心
- 成本：~0.5 GPU·h
- **可与 Test 1 并行跑**（Test 1 用 8 卡，Test 4 等 Test 1 结束后跑，或如果 Test 1 OOM 快速退出则立即接上）

**总成本**：≤3 GPU·h（如果 Test 1 OOM → Test 2/3 跳过，只跑 Test 4 = 0.5h）

**脚本**：照抄 `baize_p96b_fp8_e2e.sh` 模板，改 TP/MBS/seq/precision/recompute 参数。每个 test 一个 `/tmp/baize_t3_testN.log` + summary。

**报告要求（跑完立即报）**：
```
T3 提速验证结果：
- Test 1 (C2 recompute+MBS4 TP1): [OK/OOM] ms/iter=X tok/s=Y peak=ZGB
- Test 2 (C2+ seq8192 M=32768 TP1): [OK/OOM] ms/iter=X tok/s=Y peak=ZGB  
- Test 3 (C2+FP8 M=32768 TP1): s=X.XX [转正/不转正] ms/iter=X tok/s=Y
- Test 4 (C1 FP8 TP1 MBS2): s=X.XX [预期<1.0] ms/iter=X tok/s=Y
→ P-8 最优配置 = [结论]
```

**铁律**：
- 🚫 不改 P-5b recipe 的超参（LR / arch / optimizer），只加 recompute
- 🚫 不存 ckpt（`--save-interval 0`）
- 🚫 不打断 .12 上的 data 分词 / vision R9 训练
- ✅ 改 launcher 添加 recompute 参数 → commit
- 每个测试 rc=0 或 OOM 都如实记录
- 跑完 commit + push，前缀 `pretrain T3:`


### 🆕 运维指令 · 2026-10-08（🔬 **数据配比 Round 3 搜索：接收 data agent 交接，在 P-8 前跑完**）· **R3 已完成 — 归档至 git 历史**

> **背景**：data agent 已完成 R3 方案定型，正式交接给 pretrain 团队执行。
> **交接文档**：`run/BAIZE_DATA_R3_TASK.md`（👈 **你启动前先通读此文**，以下是指令摘要）。
> **为什么现在做、而不是等 P-8 再搜**：P-8 的前置（全量分词 + GPIC 下载）至少还需要 2–3 天；
> 而 R3 只需要小样本分词（~30 分钟）+ 100 trial BO（~19.5h），**8 卡空闲期正好利用**，
> 跑完直接决定 P-8 的 Stable 段配比，**不占 P-8 启动后的时间**。

**① R3 vs R2 的本质区别**
| 对比项 | R2（已完成） | R3（本次） |
|:--|:--|:--|
| 搜索空间 | 3 维 `base:code:math` | **6 维** `ultrafineweb_en / ultrafineweb_zh / ultrafineweb_l1_en_hq / UltraX-Preview / UltraData-Code / UltraData-MATH` |
| 评测 | `--limit 500`（sampled） | **全量** 73106 requests（无 `--limit`） |
| trial 数 | 200 | **100**（预算压缩到 ≤24h） |
| D/trial | 0.5B | **1B**（信噪比更高） |
| 代理规模 | d=128/L=14 (18.36M) | **同**（不换代理） |
| 前置 | 已有 8 源分词 bin | 需跑 **小样本分词**（6 源 × 2 parquet，~30 min） |

**② 执行顺序（对照交接文档 §6）**

```text
Step 0  ⭐ 先通读 run/BAIZE_DATA_R3_TASK.md（尤其是 §5 代码改造规格 + §3.2 小样本分词路径）
Step 1  备份 R2 脚本 → 改出 baize_mix_optuna_r3.py（按 §5 改造）
        - 搜索空间从 3-dim 改为 6-dim（6 个单源名）
        - 新增 build_blend_stable() 函数
        - objective = lm_eval 全量 8 任务均分（无 --limit）
        - 沿用 Optuna TPE+MedianPruner + MBS=16 + GBS=16 + seq=2048 + D=1B
Step 2  跑 baize_tokenize_r3_sources.sh（6 源小样本分词, ~30 min）
        - 数据源位置见交接文档 §3.1 Table
        - 每源取 2 parquet（路径已列出），参考 baize_mix_tokenize_base.sh
        - 输出到 {BASE}/data/r3_sources/
Step 3  python baize_mix_optuna_r3.py --phase stable --n-trials 100 \\
            --gpus 0,1,2,3,4,5,6,7   # ~19.5h（8 卡满）
Step 4  等 100 trial 完成（第 13 轮最后 4-trial 收尾）
Step 5  top-K（K≥5）全量 lm_eval 验证
Step 6  输出 r3_best_blend.txt → 供 P-8 Stable 热身引用
```

**③ 关键改动点（相对于 R2 的 `baize_mix_optuna_r2.py`）**
- 搜索空间：`ultrafineweb_en, ultrafineweb_zh, ultrafineweb_l1_en_hq, ultrax_preview, ultradata_code, ultradata_math`
- 不搜索 `decay` 段（Decay 段保持 R2 的 3-dim 原样，R3 只搜 Stable）
- 每 trial D=1B 而非 0.5B（训练步数 30518 步 @ MBS=16, GBS=16, seq=2048）
- `lm_eval` 不加 `--limit`（全量 73106 requests，~3.6 分钟/trial）
- 末轮不足 8 trial 时 `--gpus` 改传实际空闲卡号

**④ 预算确认（交接文档 §2 实测锚点）**
| 操作 | 单 trial | 100 trial |
|:--|:--|:--|
| 训练 (1B tok, MBS=16, 166ms/step) | 84.4 min | — |
| HF 转换 | 2 min | — |
| 全量 lm_eval（8 任务, 无 limit） | 3.6 min | — |
| 单 trial 合计 | ~90 min | — |
| 100 ÷ 8 GPU = 13 轮 × 90min | — | **~19.5h ≤ 24h** ✅ |

**⑤ 同期义务（不冲突的，可后台并行）**
- 论文更新（纯 CPU 工作）：等 R3 跑起来之后（Step 3 已启动、稳态运行后），**抽空做**，不占 GPU。
- R2 收官报告（纯 CPU 自包含 HTML 写作）：同理，R3 跑起来之后抽空做，不占 GPU。
- ⚠️ **不得因写论文/报告而延迟 Step 1–3**：R3 的主干是先改代码 + 分词 + 起跑，**写报告是后台 CPU 活**。

**⑥ 收尾**
- R3 搜索完成后（r3_best_blend.txt 已生成），把结果回写到 `DATA_MIX_RECIPE.md` 更新 Stable 段推荐配比。
- 在 `MEMORY_PRETRAIN_2B.md` 记录 R3 结论 + best trial 详情。
- **不 kill loop**：跑完后 `WAITING=1` 回原位等 P-8 启动令。

> 📦 本块加入后 TASK 约 28KB，仍 ≤32KB ✅。

### 🆕 运维指令 · 2026-10-08（📝 **更新论文 LaTeX：把 R2 实测数据写入 `4_llm_pretrain.tex` / `3_architecture.tex`**）· **用户直令：各线自己更新论文** · 高优先

> **用户令**：「让 pretrain，vision 和 data 更新一下论文。」
> ⚠️ **不要代笔写 LaTeX** —— 你只负责把你自己的实验数据填入对应的 `.tex` 文件，然后编译 `main.pdf`。
> ⚠️ **论文在 `BaiZe-ISEDA2027/` 目录下，与任务书同在一个 repo** —— 你直接可见可改。

**① 当前论文中 `4_llm_pretrain.tex` 已有 R1（S1–S5）的基础数据，但 R2 的大量新结果完全没有反映**。你需要审阅 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md`，判断哪些值得写入论文。

**② 建议更新的内容（自行判断，不一定要全写）：**
1. **长上下文能力**（B1 实验）：1M PPL=55.42 无退化 → 可补入 §4.2 或新增一段，说明 hybrid 的 long-context 优势（只需 4 层 attention 可见状态增长）。
2. **推理成本对比**（P-9.11 系列）：128K–256K 下 hybrid vs dense 加速比 2.8–4.3×（prefill 1.7–3.3×，decode 2.2–2.6×）→ 强化 Table~8 或新增一段。
3. **FP8 训练可行性**（P-9.8/P-9.9）：delayed FP8 可用于 P-8，但 tensorwise FP8 因 T1/T4 失败 → 可加一句预算说明。
4. **更新 Table~8（tab:archcomp）**：若有新的更精确的数据（如 decode gap 在 sglang 下的实测），可更新。
5. **Training throughput 数据**：P-9.7 定稿的 249K tok/s 可更新到相关位置。

**③ 格式纪律**
- 🚫 **不改 § 编号、不改 label、不改 cross-ref** —— 只更新数字、表格行、段落描述。
- ✅ **可以加子节**（`\subsection{...}`）/ 加段落 / 加表 / 加图 —— 但 label 和 cross-ref 不能冲突。
- **编译前先 `cd doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027 && rm -f main.aux main.bbl main.blg main.log`，然后 `pdflatex main && bibtex main && pdflatex main && pdflatex main`，确认 0 error。
- 编译后的 `main.pdf` **一起 commit**（审稿人看 PDF）。
- **git 前缀**：`pretrain 论文更新: ...`

**④ 本块不撤销之前的报告任务** —— 写报告和更新论文是两件事，**都要做**。
- 推荐顺序：**先更新论文（简短任务），再写报告（深度任务）**。

> 📦 本块加入后 TASK 约 24KB，仍 ≤32KB ✅。


### 🆕 运维指令 · 2026-10-08（📄 **R2 全线实验收官总报告 HTML**）· **用户直令：各线自己写报告** · 高优先

> **用户令**：「把任务下发给各 agent，由 agent 自己写报告，不要替代他们写。」
> ⚠️ **本线 R2 所有实验已完成**（P-1~P-9.13 全 ✅），长期空转心跳不是正事。**用户点名要 agent 自己写报告**。

**① 交付**：`report_pretrain_r2_final.html`（落 `doc/BaiZe-ISEDA2027/`）

**② 格式（沿用 house style）**
- **自包含**：内联 CSS + **数据图优先内联 SVG**；**零外链**；**HTML 本体 ≤200KB**。
- 位图一律 **JPEG、长边 ≤1280、q85**、单图 ≤400KB/总量 ≤4MB、**落本地并 commit**；🚫 严禁外链、🚫 严禁用文生图「编」数据图（曲线必须由 **真实实测数据** 生成）。
- 若引用已有报告（如 `BAIZE_PRETRAIN_RESULT.html` / `report_pretrain_research{1..5}.html`），只给链接指针，**不重复贴全文**。

**③ 建议 10 节**
1. **TL;DR**（3–5 条：架构锁定为 hybrid 56L/4-attn，LR 1e-3 WSD，val loss 2.2054，hybrid vs dense 加速比 2.8–4.3×@128K–256K，FP8 裁定为 delayed 可用于 P-8）；
2. **实验设计总览**：R1（架构搜索 S0–S5）→ R2（P-1~P-9.13），各阶段目的与预算；
3. **架构选型**：dense vs hybrid vs 其他，**hybrid 锁定为正式架构**（附 P-3 5000 步对比 + B1 1M PPL=55.42 无退化）；
4. **超参搜索**：P-1 LR 扫描（1e-3 最优）+ P-2 3-seed 复现（2.6739±0.0469）+ P-4 退火消融；
5. **FP8 裁定**：P-9.8 armA/armB + P-9.9 tensorwise → 结论：delayed FP8 可用于 P-8；
6. **长上下文能力**：P-9.11 系列（2M served / 4M timeout / 显存归因）+ 推理成本矩阵；
7. **提速实验**：T1 bf16-SSM（无差异 1.00×）/ T2 公平对比 / T3 短名单（C1 FP8-TP1 / C2 recompute+MBS4）/ T4 效果短名单（Q1 100B tokens / Q2 data mixture）；
8. **复杂推理**：A 36/36（BBH 峰值 14.26%@2.62B）/ B ABF（+2.71pp）/ D VRAM 5.35GB 恒定；
9. **对 P-8 的建议**：配方 88:8:4 / FP8 delayed / hybrid 架构 / 数据就绪条件；
10. **局限与诚实交代**：655M token 代理实验 / 未收敛 / 单 seed 方差 / 待正式训练验证。

**④ 纪律**
- **数字必须真**：每个数字可由 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` / 原始日志复算；
- **结论跑完即固化**：不新增实验、不改已有结论；
- **收尾按「收尾铁律」commit+push**（前缀 `pretrain R2收官: …`）；
- 写完本报告后，**不要回到空转心跳** —— 改做 **P-8 前置预研**（若运维尚未撤暂缓令，预研 P-8 recipe / 数据配方复算 / 训练脚本核验）。

> 📦 本块加入后 TASK 约 23KB，仍 ≤32KB ✅。如需归档，只归档下方已闭合旧块。

> 📦 §运维指令·2026-10-06（裁决+提速令：批准A/B/D，C暂不动/E不做，NCCL拓扑核查+提速清单）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.12 NCCL已在用NVLink(P2P 100%,用户PCIe假设证伪,busbw 164.56GB/s),P-9.13 env无提速(249K tok/s上界),A 36/36✅(BBH峰值14.26%@2.62B),B✅(ABF不降反升+2.71pp,passkey 0%),D✅(VRAM 5.35GB恒定4K→128K)。需要时再读。

> 📦 §运维指令·2026-10-06（空窗提案：5条候选A-E）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：运维裁决✅A/B/D批准,⏸C暂不动,🚫E不做。A/B/D均已✅COMPLETE。需要时再读。

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**（「收尾铁律」第 0 步已同步此判据）。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ARCHIVE_OPERATOR_PRETRAIN.md` / `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）/ `daily-memories/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `pretrain 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**40KB**（已过 40KB 红线）⇒ **下次唤醒先归档到 ≤32KB**，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> **为什么新增（真实事故）**：2026-10-06 06:55 → 08:30，**data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新**（其间 agent 在改别的文件、push 得出去），**外部运维只能靠 git 判断死活** ⇒ 被**误判成静默卡死并上机排查**。
> 根因：**「更新记忆 + push」以前只是建议、没有硬约束**；loop 的兜底 push 间隔是 **5h**（本日已缩短），且只覆盖固定白名单 —— **不许依赖兜底**。
> 🚫 **旧口径（已废）**：「每 5 小时由 loop 兜底 push 一次」**不再作为交付保障** —— 兜底只是保险丝，**不是你的提交手段**。

**每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：**

0. **体积自检（先跑，数字要抄进下一步的心跳）**：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 **≤ 32KB**；**任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档**（见本文件「📉 体积维护规程」：只把**已闭合**内容**原文**移入 `run/ARCHIVE_OPERATOR_PRETRAIN.md`、留 1 行指针），直到两者都 ≤ 32KB；**> 40KB（红线）⇒ 必须先归档再提交**（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_PRETRAIN.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. **写心跳**：更新 `run/MEMORY_PRETRAIN_2B.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并**追加 1 行「本唤醒流水」**：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮记录（**当天文件必须建**）。
3. **自己提交 + 推送**（**不许等 loop 兜底**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B.md \
              doc/BaiZe-ISEDA2027/run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md doc/BaiZe-ISEDA2027/run/daily-memories
   git commit -m "pretrain #<轮次>: <一句话>"   # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 **绝不用 `git add -A`** —— 这是**共享工作副本**，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是**提交归属不可溯**（运维查不出谁在干活）。
4. **闭环自检**：`git status -sb` ⇒ **无 ahead / 无 behind**；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   **push 失败（`error: Forbidden` / 网络）**：重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下一轮唤醒第一件事就是补推**。

> ⏱️ **运维判死判据（硬）**：**心跳文件 >60 min 无新提交 ⇒ 按卡死处理**，**不再等你**。**你干得再多，心跳不动 = 仍会被判死。**

> 📦 §运维指令·2026-10-05深夜2（sglang上界+P-5b 8集+P-6②+P-9.5）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：4项全COMPLETE，4 HTML在doc/BaiZe-ISEDA2027/。
> 📦 §运维指令·2026-10-05深夜（sglang可用→BaiZe vs MiniCPM5推理对比）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：P-9.11 COMPLETE，H1✅prefill 2.18×, H2⚠decode 1.18×, 128K failed。
> 📦 §运维指令·2026-10-05晚（sglang conda env+proxy口径+环境隔离）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：sglang在vllm env可用(0.5.9)，proxy=http://172.19.92.25:13128，训练=py310/推理=vllm env隔离。
### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` **都每次唤醒被全文读进 prompt**（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_PRETRAIN_2B_TASK.md` ≈ **38KB**、`MEMORY_PRETRAIN_2B.md` ≈ **14KB**。
- **上限（两者相同）**：**≤ 32KB**；**红线 40KB** ⇒ **超红线当轮必须先归档才能收尾**。
- **自检**：见「收尾铁律」第 0 条（`wc -c` 两文件，**数字抄进心跳**）。
- **归档去向（只归档「历史」，🚫 不许归档「活口径」）**：
  ① 已执行完/已作废的**运维指令块** → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（**留下 1 行指针**）；
  ② 被取代的**候选表/推导过程**（保留现行档 + 实测结果） → `run/ARCHIVE_PRETRAIN_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` 等；
  ④ 较早的**唤醒流水**（保留最近 ~20 条） → `daily-memories/<条目日期>.md`（原文不改）。
- 🚫 **不许归档**：硬规则 / 验收标准 / **现行口径** / `WAITING:` 状态头 / 「运维问答」区。
- 指针（**必须留、只 1 行**）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 **不许改小节编号/标题**（别处有交叉引用）。
- **谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）**：`MEMORY_*.md` 一直由 agent 自滚，**任务书同理** —— **本线 agent 自己**把「已闭合」内容**原文**移入对应归档文件、留 1 行指针。⚠️ **本文件「agent 只读」的唯一例外 = 仅此「搬迁」**：原文一字不改、不动小节编号/标题、**不新增/不改写任何运维指令**（本区作者仍是运维）。**并发安全**：归档前先 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `<线> 归档: …` 前缀。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变（正文/流水/快照里**不得**再出现以 `WAITING:` 开头的行）。

---



# ══════════════ ROUND 2 · **现行部分**（只保留仍未完成/仍有效的）══════════════

> R2.0/R2.1/R2.2 清单 · R9.0-bis · P-4R · P-5a 与 **Round 1（S0–S5）** 均已**完成并归档** →
> **`run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md`**（**需要时再去读，不要把整份读进上下文**）。

> 📦 §P-6 lm_eval 8集+scaling law（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；**结论**：P-6① Avg=0.4395@655M, P-6② 48/48 runs Avg 33.26%→49.22% R²=0.986, 55%→~55B tok. 需要时再读。
> 📦 §P-7 训练吞吐核查（已完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md；**结论**： dense +8% (not +24%), hybrid 85.6K vs dense 89.7K. 需要时再读。

**P-8 细节 —— 🏁 Stage (i) 完整训练（正式预训练）**

> ## ⏸ **运维 2026-10-02 指令：P-8 暂缓启动**
>
> **原话**：「**测数据配比需要时间，下载 base 也需要时间…因此 P-8 暂缓启动，先做配比实验和下载 base。**」
>
> **原因（两条前置都未就绪）**：
> 1. **`Ultra-FineWeb`(base) 还在下载**（115/64624，2.99 TB）—— 而它是 **stable 段的主力数据**；
> 2. **WSD 双阶段配比实验还没做**（见 `BAIZE_DATA_TASK.md` §0.6）—— **P-8 吃什么配比是它要定的**。
>
> **→ 所以：不要因为"P-5b 快跑完了"就顺手启动 P-8。** 前置未齐之前，P-8 不启动。
> **→ 本唤醒及后续唤醒：做完 P-4R / 恢复 P-5b 之后，仍然等 data agent 的配比方案 + base 就绪。**

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

