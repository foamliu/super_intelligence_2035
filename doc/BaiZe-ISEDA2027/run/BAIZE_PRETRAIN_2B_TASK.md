# BAIZE_PRETRAIN_2B_TASK.md

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### [运维令] 2026-10-26 15:3x（**整理「BaiZe-2B 预训练构想」为中文 HTML 报告 + ETA**）· 用户直令 · 最高优先

> 用户原话：「关于后续的预训练，我有个初步想法想跟 pretrain 商榷。请安排 pretrain 把这个想法整理为中文 HTML 报告，附上 ETA 等信息。」
> 用户构想原文照录如下，请据此整理成报告。

**① 模型与配方**
- 模型：Mamba2-hybrid（56 层，Nemotron-H 式顺序混合），参数量 **2.2B**。
- 训练配方：**16K / 16卡 / CP1 DP16 / graph-OFF = 613,992 tok/s**。
- 学习率：**WSD**，2000 步 warmup，然后 LR **保持 1e-3**。

**② 三阶段计划**
- **S1**：2M tok/step · 1.4T tok · 700,000 steps
- **S2**：4M tok/step · 1.4T tok · 350,000 steps（配比同 S1）
- **Decay**：4M tok/step · 80B tok · 20,000 steps

S1/S2 配比（sampling prop / epochs）：
| dataset | prop | epochs |
|:--|--:|--:|
| en_v1_4 (ultrafineweb_en_v1_4) | 0.65 | 0.81 |
| ufw_l1_en_hq | 0.05 | 0.93 |
| ufw_zh | 0.04 | 0.99 |
| Math-L1 (UltraData-Math-L1) | 0.05 | 0.85 |
| Math-L3 (UltraData-Math-L3) | 0.02 | 0.72 |
| Code-L2 (UltraData-Code-L2) | 0.15 | 1.00 |
| Code-L3 (UltraData-Code-L3) | 0.04 | 0.87 |

Decay 配比（prop）：
ufw_en_l3(qa) 0.18 / ufw_zh 0.04 / Math-L3 0.04 / Code-L3 0.02 / UltraData-SFT-2605 0.60 / UltraData-SFT-Agent-2609 0.12

**③ 报告要求**：输出 `reports/report_pretrain_baize2b_pretrain_plan_zh.html`（自包含中文 HTML）。
- 结构：① 模型与配方 → ② 三阶段计划（各阶段 tok/step、steps、数据配比表）→ ③ **ETA 测算**（按 613,992 tok/s 算 S1/S2/Decay 各阶段 wall-clock 时长 + 总时长；分「纯训练」与「含故障/checkpoint 预留」两口径）→ ④ **商榷点与建议**（例如：4M tok/step 下 16K CP1 DP16 吞吐是否仍 613,992 需重测；LR 保持 1e-3 不改 + WSD 2000 步 warmup 的含义；数据配比 epochs<1 的采样语义；Decay 阶段 SFT/Agent 数据占比 0.72 的合理性；总计耗时与 GPU 预算）。
- 全部数字可溯源（吞吐用 #792 实测 613,992）；commit `pretrain plan:`。

### [运维令] 2026-10-26 14:3x（**补写 #792 双机实测结果进吞吐报告**）· 用户直令 · 最高优先

> 用户原话：「下发指令，让 pretrain 更新报告」
> **问题**：`reports/report_pretrain_seq16k32k_throughput_zh.html` 仍是 #791 旧版（14,208B，正文停在「16K 外推 ~584K + 待实跑确认」），#792 双机 16 卡实测结果没写进去。

**① 补写「双机 16 卡实测」节（数字溯源 `results_dualnode_seq16k32k/` + EXPERIMENTS §五·8）**
- **16K CP1 DP16 graph-OFF accum16 = 613,992 tok/s**（每卡 38,374、peak 75.2GB、0 NaN）→ 600K 目标 **102% 达标**（反超 8K 基线 #770 的 606,300 约 1.3%）；
- **16K CP2 = 281,970（0.459×）**：CP 在 16K 纯亏（激活显存 75.2→49.7GB 但吞吐掉 54%）→ 16K 应关 CP；
- **32K CP2 DP8 = 351,526 tok/s**（每卡 21,970、peak 76GB、0 NaN）= 600K 的 58.6%，结构性受限（32K 强制 CP=2[CP1 OOM@81GB] + 2×上下文 + P2P KV 交换，已≈2×线性外推天花板 366K 的 96%）。

**② 改写「结论与后续」**：16K 从「待实跑确认」改为「已达标 613,992 ≥600K」；32K 写明「结构性到不了 600K，351,526 已≈天花板 96%」；删除/更新过期的「待办 (a) 实跑确认 (b) 32K graph ON」条目。

**③ 纪律**：报告正文必须真含这些数字（🚫 再只在心跳里说、正文不写）；更新后 commit `pretrain perf:` + push，心跳附新字节数（须 >14,208 即证明真更新了）。

### [运维令] 2026-10-26 13:2x（**继续推进 FP8 真实数据 16K/32K 吞吐实测**）· 用户直令 · 最高优先

> 用户原话：「安排 pretrain 继续推进 16K/32K 吞吐实测」

**① 现状（复用，勿重复验证）**：双机 16 卡 BF16 连通性已验证（84% scaling、IB 多通道健康、SSH cleanup 挂起已 kill + 结果解析已修）。**下一步 = 正式 FP8 真实数据的 16K/32K 吞吐实测。**

**② 本轮任务**
1. 修完 `baize_dualnode_16gpu_test.sh` 的 SSH cleanup（等远端 torchrun 干净退出再加超时兜底，不再 `wait` 空挂）后，**去 `--mock`、用 `--fp8-recipe tensorwise` + 关 CUDA Graph + 真实数据**，起双机 16 卡。
2. **seq=16K**（CP=1，accum≥16）实测：目标冲 **≥600K tok/s**；记录全卡 tok/s / 每卡 tok/s / peak 显存 / loss / NaN。
3. **seq=32K**（CP=2）实测：给出**真实可达最优吞吐** + 量化 CP 的 P2P KV 交换开销 + 明确「32K 到不了 600K」的天花板与瓶颈。
4. 每配置写清：seq / DP/CP / accum / MBS / 关graph? / fp8? / tok/s / 显存 / 结论，全部溯源脚本+log。

**③ 交付**：结果追加到 `reports/report_pretrain_seq16k32k_throughput_zh.html`（或新报告）+ EXPERIMENTS 更新；commit `pretrain perf:`。

**④ 纪律**：双机先用 `nvidia-smi` 确认 .12 空、不抢 vision/data/harness；数字不伪造；脚本改动留 diff/备份。

### [运维令] 2026-10-26 11:1x（**双机 16 卡实测调优 seq=16K/32K 训练吞吐**）· 用户直令 · 最高优先

> 用户原话：「安排 pretrain 继续调优双机16卡 seq=16k/32k 的训练吞吐」

**① 目标**：用**真实双机 16 卡**（2×8 H100）实测并调优 seq=16K 与 seq=32K 的训练吞吐（此前只是单机 8 卡 + 外推，未真 16 卡实跑）。

**② 现状（复用你 #791 结论，直接在此基础上继续，勿重复取证）**
- 16K（CP=1，关 graph，accum16）8 卡 = 300,133 tok/s（每卡 37,516），外推 16 卡 ~584K，**尚未真 16 卡实跑**。
- 32K（CP=2，FA3 11 处 patch 后）8 卡 = 183,394 tok/s（每卡 22,924），外推 16 卡 ~322K。

**③ 要求**
1. **真 16 卡跑**：起 2 机（`.29` + 另一台空闲机，先 `nvidia-smi` 确认空闲）DP16 或 DP8×CP2，跑 seq=16K 与 32K，记真实 tok/s（别再只外推）。
2. **调优方向**（可自行调整并记录理由）：16K 冲 600K+（调 accum / CP 开与关 / recompute 粒度 / 通信重叠）；32K 给出**真实可达的最优吞吐**，并量化 CP P2P KV 交换开销，明确「32K 因 2×上下文+CP 固有代价到不了 600K」的具体瓶颈与天花板。
3. 每个配置记录：seq / DP/CP / accum / MBS / 关graph? / tok/s(全卡) / 每卡 tok/s / peak显存 / loss / NaN / 结论。

**④ 交付**：实测结果写入 `reports/report_pretrain_seq16k32k_throughput_zh.html`（在原报告追加 §）或新报告；更新 EXPERIMENTS；commit `pretrain perf:`。

**⑤ 纪律**：16 卡需 2 机，先确认第二台空闲、不抢 vision(.12)/data/harness；数字溯源脚本/日志；不伪造。

### [运维令] 2026-10-26 09:1x（**优化 16K / 32K 训练吞吐至 600K+**）· 用户直令 · 最高优先

> 用户原话：「pretrain：16卡训练吞吐 seq=8k 吞吐（~605K）已达标；现在继续优化16k和32k训练吞吐，争取达到600K以上」

**① 基线（已达标）**：seq=8192 关 graph，16 卡 ~593K（或按你实测 ~605K），以实测为准写明。

**② 目标**：**seq=16K 与 seq=32K 的训练吞吐各 ≥600K tok/s（16 卡）**。

**③ 现状（复用你 #787/#788 结论直接优化，勿重复取证）**
- 16K：关 graph = 561K（0.93×），距 600K 差 ~7%，需继续优化。
- 32K：cp1 OOM@81GB / cp2 被 flash-attn-3 阻断（`window_size=(l,r)` 旧签名，需 patch `window_size_left/right`，调用点在 site-packages）。

**④ 方向（建议，可调整并记录理由）**
1. **16K**：从 561K 找瓶颈（CP 激活重算 / KV cache / 通信重叠），尝试 context parallel、recompute 粒度微调等合法手段冲 600K+。
2. **32K**：先 patch CP 路径 flash-attn-3 的 `window_size` 调用跑通，再优化吞吐冲 600K+；若 32K 物理受限（显存/架构），如实给出「当前最优吞吐 + 阻塞点 + 需要什么（如更多显存/升级 flash-attn/改 CP 实现）」。

**⑤ 交付**：逐档记录（配置 → tok/s → 达标? → 瓶颈/结论），溯源脚本/日志；中文本报告 `reports/report_pretrain_seq16k32k_throughput_zh.html` + EXPERIMENTS 更新；commit `pretrain perf:`。

**⑥ 纪律**：只用 .29（如需 16 卡则 2 机）；🚫 不碰 vision/data/harness；数字不伪造。

### [运维令] 2026-10-26 08:2x（**写最近工作报告 · 中文 HTML**）· 用户直令 · 最高优先

> 用户原话：「关于最近的工作，安排 BaiZe 4个agent各自写一份报告。」

**任务**：写本线（pretrain）最近工作（10-20 起）总结报告 `reports/report_pretrain_recent_work_zh.html`（自包含中文 HTML）。
- 结构：① 本线定位 → ② 近期任务逐个（设置→过程→结果→结论）→ ③ 关键数据速查表 → ④ 阻塞/待拍板 → ⑤ 下一步建议。
- **必覆盖**：① decay 训坏→修复全历程（v2 44.97%/6.21% → 官方 1113.sh decay-5000 58.97%/28.02%，含归因双移位/缺μP/LR）；② 长上下文 seq 扩展排查（CUDA Graph 顶格停滞真因 + seq=8192 关 graph 0.978×满速 + 32K CP 不可跑[flash-attn-3 API 阻断]）；③ 两份 decay 报告交付。
- 数字溯源（log/json 文件:行）；遵守命名规程；commit `pretrain report:`。

### [运维令] 2026-10-25 23:0x（**通宵攻坚：查清 tokens/microbatch 悬崖并给出可用档位；不解决不收工**）· 用户直令 · 最高优先
> 用户原话：「下发指令让 pretrain 这个晚上一直排查这个问题，解决不了不要结束。」
> 已知事实：基线(seq4096/mbs3=12,288 tok/mb/GPU)=606,449 tok/s；cfg0a(seq4096/mbs4=16,384)=113,514；cfg1(seq8192/mbs2=16,384)=108,291；cfg3/4(16K, 16,384)=112,094/121,495 ⇒ **悬崖在 12,288-16,384 tok/microbatch/GPU 之间，与 seq 无关**；四格峰值显存 81.08GB 顶到上限，基线 67.6GB。

**0) 夜间纪律（覆盖其它收尾条文）**
- 本轮起至 **2026-10-26 08:00** 持续攻坚，`WAITING=0`；**不许**以「等用户 / 等运维 / 无新令」结束或空转。
- 每个实验用 `setsid` 后台跑，`sleep 120-300` 轮询判读；**每 30 分钟至少一次 progress commit**（`pretrain rc: ...`），关键发现即时写 MEMORY。
- 08:00 前必须交**早报**：一句话结论 + 档位表 + 证据路径（无论成败）。
- 🚫 不 kill `SWE-bench` 下载与 harness 复跑；🚫 不抢 data 分词资源；每格跑完立刻释放 16 卡；🚫 不许把猜测写成结论、不许编数。

**1) 实验阶梯（按序，能跳就跳但要写理由）**
| 步 | 配置 | tok/mb/GPU | 目的 | 判据 |
|:--|:--|--:|:--|:--|
| E1 | seq4096 / mbs3 / gbs1008（=cfg0b） | 12,288 | 复现基线 | ~606K ⇒ 基线真实；~113K ⇒ 基线来自不同 setup，先查环境 |
| E2 | seq8192 / mbs1 / gbs256（accum16） | 8,192 | **seq 8K 能否满速** | 回到 55-60 万 ⇒ 「8K 满速只要 MBS=1」，这是给用户的答案 |
| E3 | seq12288 / mbs1 | 12,288 | 定位阈值（与 E1 同 tok/mb、不同 seq） | ~606K ⇒ 阈值只与 tok/mb 有关，与 seq 无关（终判） |
| E4 | seq8192 / mbs1.5 不可行 ⇒ seq6144 / mbs2 | 12,288 | 第三个同阈值点交叉验证 | 同上 |
| E5 | 16,384 tok/mb 的最小复现（seq4096/mbs4 已有） | 16,384 | 悬崖边界细分：再插 seq4096/mbs4 与 seq8192/mbs2 均为 16,384 ⇒ 用 seq=8192/mbs2 与 seq=16384/mbs1 已覆盖；补 **seq=4096/mbs3.5 不可行**，改测 **seq=2048/mbs8=16,384** 与 **seq=1024/mbs16=16,384** | 若小 seq 大 mbs 也慢 ⇒ 纯 tok/mb 效应；若快 ⇒ 与 seq 相关 |

**2) 归因（E1-E5 出数后 2 小时内定位）**
- **显存假说（首选）**：16,384 tok/mb 下峰值 81GB 顶格 ⇒ 检查是否触发 activation recompute / offload / 碎片；取 `torch.cuda.memory_summary()` 在 12,288 与 16,384 两侧各一份，比对 reserved/allocated/active 与 fragmentation；核对 `--recompute-*`、`PYTORCH_CUDA_ALLOC_CONF` 实际生效值。
- **kernel 假说**：profile 六类（attention / ssm / mlp / loss / optimizer / data）在 12,288 与 16,384 各 10 步；看是否有算子在某 token 数跨过阈值后换实现（FP8 GEMM tiling、CUDA graph node 数、SSD chunk）。
- **CUDA graph 假说**：确认两侧 graph 是否都 capture 成功、replay 次数与 graph 数量是否爆炸（token 数变化 ⇒ 多 shape ⇒ 多 graph）。
- **数据假说**：data-loading 计时 + util 曲线，两侧对比；若 data 占步时 >30% 记下来但不算主因（除非其它都排除）。

**3) 修复与验收**
- 定位后**只改一项**（MBS/accum、CP、recompute、graph 配置、mamba dtype 之一），在 **seq=8192** 上复测，要求：`tok/s >= 0.7 × 606K`（即降幅 ≤30%）且 loss/gnorm/NaN 正常。
- 若 16K 必须 CP：给 CP=2/4 的可行性 + 预期吞吐（可只跑 20 步 smoke）。
- 产出**档位表**：`seq × MBS × accum → tok/s → per-GPU → 峰值显存`，并给 S1/S2 的推荐档位（含「8K 满速配方」）。

**4) 收敛条件（必须同时满足才算解决）**
1. 能一句话解释 5.5x 的成因，且有实验/证据支撑；
2. 给出可复现的修复配方，且复测达标（≥0.7×基线）；
3. `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html`（≥15KB）+ 修正版 seqlen 报告（旧结论标「已证伪」）+ EXPERIMENTS 新节 + MEMORY 首部新块，全部 commit。
- **若 08:00 仍无解**：必须交「早报 + 已排除清单（每条附证据文件）+ 下一步最小实验（≤30 分钟可跑）+ 需要用户/运维决策的点」，**不许只写「未解决」**，也不许停机。

**5) 交付路径**
**附**：cfg5/cfg6（32K）OOM 重试按「配方变更组」（`--recompute-activations` / `--use-distributed-optimizer`）单列，不混主表。

- 实验日志 `/tmp/baize_rc_<step>/`；结果表 `run/pretrain_rc_ladder_20261026.tsv`（逐格一行）；profile 落 `run/pretrain_rc_profile_<tokmb>.txt`。
- commit 前缀 `pretrain rc:`；报告 08:00 前必须存在（哪怕标 `rev1`）。

### [已归档] §运维令·2026-10-25 20:2x（seq 掉速根因排查初版：H1-H9 假设表 + cfg0a/cfg0b 对照 + web 对标）**已并入 23:0x 通宵令**（cfg0a 已出数并证伪 seq 假设；假设表与外部对标原文见 ARCHIVE）-> 原文归档到 `run/ARCHIVE_OPERATOR_PRETRAIN.md`。需要时再读。

### [已归档] §运维令·2026-10-25 17:5x（seq x tok/step 16 卡吞吐网格）**已完成**（6 格全测：cfg1-4 OK 108K/112K/112K/121K、cfg5-6 OOM@32768；报告 13,565B + 生成器已交付 commit 233c47d0e）-> 原文归档到 `run/ARCHIVE_OPERATOR_PRETRAIN.md`。**注意**：该报告「seq>=8192 崩 5x」的结论已被 cfg0a 证伪，需按 23:0x 块更正。需要时再读。

### [已归档] §运维令·2026-10-25 07:4x（双机 16 卡吞吐报告）**已完成**（#770-#776：报告 `reports/report_pretrain_dualnode_throughput_zh.html` 24,970B + 生成器可确定性重生成 + EXPERIMENTS L3691 指针，独立复核通过）-> 原文归档到 `run/ARCHIVE_OPERATOR_PRETRAIN.md`。需要时再读。

### [已归档] §运维令·2026-10-24 23:5x（双机已调通 -> 转入吞吐优化阶段）**已完成**（Task A/B 全闭合：606,300 tok/s / 99.4%；双机报告 24,970B；Task B 3 TAG 无收益）-> 原文归档到 `run/ARCHIVE_OPERATOR_PRETRAIN.md`。需要时再读。

### [已归档] §运维指令·2026-10-24 16:0x（305K 最佳实践写入任务书 + longctx 报告用 Mamba2-hybrid 重写）**已完成**（#772-#776 交付并复核：longctx 报告 19,158B、0 处 Xmodel）-> 原文归档到 `run/ARCHIVE_OPERATOR_PRETRAIN.md`。需要时再读。

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

