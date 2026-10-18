# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区
### 🆕 运维指令 · 2026-10-18 16:2x（🚨 P0：立即 resume 80B decay v2 + **长期授权：训练挂了自行重启，不再等许可**）· 用户直令 · 最高优先

> 用户令（2026-10-18）：「pretrain：重启 resume 训练，以后这种事不需要运维许可，自己的训练挂了，唤醒时看到了立刻修。」
> 现状：#548 已确认 **15:53:22 step 9400 后训练死亡**（GPU 全空、无 torchrun、日志无错）；最新 ckpt = **step_8000**（11:15）；step 8001–9400 将丢。**本轮直接 resume，不要等许可。**

**① 立即 resume（本轮唤醒）**
1. 确认 `nvidia-smi` 8 卡空、无 `torchrun`；确认 ckpt：
   ```bash
   ls -l /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/step_8000/model.safetensors
   ```
   若 `step_8000` 缺失，选最新的 `step_*`（必须含 `model.safetensors`）。
2. 给 `run/baize_xmodel25_decay_v2.sh` 加可选 resume（或直接改 torchrun 参数）：
   ```bash
   RESUME_DIR="${RESUME_DIR:-}"
   RESUME_ARG=""
   [ -n "$RESUME_DIR" ] && RESUME_ARG="--resume $RESUME_DIR"
   # 在 baize_xmodel25_decay_v2.py 参数末尾加 $RESUME_ARG
   ```
   启动：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
   RESUME_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay/step_8000 \
     setsid bash baize_xmodel25_decay_v2.sh > /tmp/baize_xmodel25_decay_v2_resume.log 2>&1 < /dev/null &
   ```
   `--resume` 会从 step_8000 续跑（LR schedule 按 8000 起算；optimizer 状态不恢复，属已知小 transient）。脚本内部日志仍写 `$OUTPUT_DIR/baize_xmodel25_decay_v2_train.log`。
3. 判据：torchrun PID + 8 workers；8 卡 100%；train_log 从 **step 8001** 继续增长、无 error/traceback/OOM/CUDA；`--resume` 打印 `start_step=8000`。
4. 记录：MEMORY + daily + commit `pretrain resume:`。

**② 长期规则（立即生效，覆盖旧的「等运维许可」）**
- 以后唤醒先查训练：`pgrep -af torchrun`、`nvidia-smi`、train_log 尾部。
- **训练进程消失 / 崩溃 / 被杀** ⇒ 自查日志 → 选最新有效 `step_*` ckpt → **立即 `--resume` 重启**，不需要逐次等运维许可。
- 仅以下情况停手报 blocker：① 没有任何有效 ckpt；② 同一原因 1h 内连续崩 ≥2 次；③ 硬件/磁盘/网络错误明确；④ 重启命令本身失败。
- 仍禁止：kill 健康训练、改配方/数据、动别的线。

### 🆕 运维指令 · 2026-10-18 12:0x（🚨 P0：立即修复 `.29` 的 ops 中继；先于一切巡检/写作）· 用户直令 · 最高优先

> **背景**：`run/ops/inbox.md` 的 RUN_ID 123（09:54 推送）至今无回执，`run/ops/.last_run_id` 仍为 **122**；而 pretrain（11:42）/vision（11:21）仍能正常 push ⇒ `.29` 本机 ops 中继停摆/冻死，不是网络。你与中继同在 `.29`，由你修复。
> ⚠️ 历史事故：命令行里把 `pkill -f "ops_relay.sh"` 与启动命令写在一起 → 自匹配，把中继和执行 shell 一起杀。**必须写进脚本文件再执行**。

**① 安全重启（照抄执行，一次跑完）**
```bash
cat > /tmp/fix_relay_29_1018.sh <<'EOF'
set -u
R=/nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "=== BEFORE $(date '+%F %T') ==="
pgrep -af 'bash [o]ps_relay[.]sh' | cut -c1-160 || true
echo -n "last_run_id="; cat "$R/ops/.last_run_id" 2>/dev/null || echo MISSING
pgrep -f 'bash [o]ps_relay[.]sh' | xargs -r kill
sleep 2
cd "$R"
env -u http_proxy -u https_proxy -u ALL_PROXY -u all_proxy setsid bash ops_relay.sh > /tmp/baize_ops_relay_29.log 2>&1 < /dev/null &
sleep 3
echo "=== AFTER ==="
pgrep -af 'bash [o]ps_relay[.]sh' | cut -c1-160 || true
tail -10 /tmp/baize_ops_relay_29.log
EOF
bash /tmp/fix_relay_29_1018.sh
```
- **判据**：≥1 个 `bash ops_relay.sh` 进程；**60–120s 内** `.last_run_id` 从 **122 → 123**，且 `run/ops/outbox.md` 末尾出现 `RUN_ID 123` 回执（含 `.29` loop/GPU + `.12` git 只读诊断）。
- 若 2 次仍不起：贴 `pgrep -af 'bash [o]ps_relay[.]sh'`、`tail -40 /tmp/baize_ops_relay_29.log`、`ls -l run/ops/.last_run_id` 原文报 blocker，🚫 不再反复 kill。
- 🚫 红线：不碰 torchrun/训练/ckpt；不 kill pretrain loop；不改 `ops_relay.sh` 本体；不清理 `/tmp`。
- ✅ 完成后在本轮 MEMORY 记：中继 PID、`.last_run_id`、outbox 的 RUN_ID 123 摘要、error scan；commit 前缀 `pretrain ops:`。



### 🆕 运维指令 · 2026-10-18②（📄 补交 v5 中文 HTML + 🔧 启动 v5 的数据前置实测：分词吞吐与 500B 可行性）· 用户直令 · 最高优先（纯 CPU，零 GPU）

> **背景**：`run/PLAN_V5_STABLE_1.5T.md` 已交付（69.7 天 / 250 ckpt / ABF 次序采纳 ✅）。但 **① 中文 HTML 还没出**；**② 计划里把 `en_v1_4` 未分词列为 🔴 阻塞项（R3），却写了"分词吞吐未知，需实测后补 ETA"**。本令把这两件补上，**不动 `.29` 正在跑的 80B decay**。

**① 交付中文 HTML（零 GPU，先做）**
- 路径：`reports/report_pretrain_formal_v5_plan_zh.html`（自包含、与既有 `reports/*.html` 同风格）。
- 必须与 `PLAN_V5_STABLE_1.5T.md` **数字一致**（宁可少写，不能两处不一致）：S1 500B/23.2 天、S2 1T/46.5 天、合计 **69.7 天**、250 ckpt、2M/4M per-step → 8.0s/16.1s、LR 恒定 1e-3、**吞吐基准 249K（TP1/DP8/MBS2/seq4096/GBS1024/bf16）**、并显式注明"298.6K 是 Xmodel-2.5 80B decay，不可用作本模型基准"。
- 必须含 **长上下文章**（ABF vs YaRN、推理侧 1M PPL 53–56 无退化、训练侧必须真实长文档、seq 课程、1M 独立 ETA）与 **次序裁定：decay → 1M → SFT/RL 采纳**。
- 必须含 **风险表**（6 条）+ **前置条件表**。⚠️ `PLAN` 里写"HQ 预训练 1.415T、余量 1.82×"等数字，**必须能在 `DATA_LEDGER.md` 找到出处**，找不到就改成实测值或标 `[待核]`。

**② 启动 v5 数据前置实测（本令核心，纯 CPU）**
> 目的：把 R3 阻塞项变成**有数字的排期**。分工：**下载/分词由 data 线执行**（已同步下发 10-18② 令），你负责**给出 v5 侧的口径与验收**，避免两边算出两套数。

1. **换算基线（用实测而非估算）**：拿 `en_v1_4` 已下部分（43,520 parquet / 4.1T bytes）做**抽样分词测速**：抽 2–3 个 shard，`preprocess_data.py` 单进程测 **tokens/s（tok/s）** 与 **bytes→tokens 比例**（每字节多少 token）。以此推算：
   - 全量 6.75T bytes → **总 token 数**（现有台账写 ≈2.2T，需你验证是否成立）；
   - **500B token 需要多少 bytes / 多少 shard**；
   - 按实测 tok/s 与给定并发（4/8/16 三档）分别给出 **500B 的分词天数**。
2. **产出**：`run/PLAN_V5_DATA_PREREQ.md`，含：抽样原文、tok/s 实测、三档并发 ETA、**500B 最早可开工日期**、以及"若分词成为瓶颈，S1 是否可先用已分词部分起跑（如 100B）"的建议（只是建议，不擅自改配方）。
3. **与 data 线口径对齐**：同一组数字写进 `DATA_LEDGER.md`（你只提交 `PLAN_V5_DATA_PREREQ.md`，不改 data 的文件）。

**③ 纪律**
- 🚫 不动 `.29` 的 80B decay（不重启、不 kill、不抢卡）；🚫 不改 v5 配方/判据（要改先报批）。
- 🚫 分词只跑 `nice -19` 小并发抽样（2–3 shard），**不要**在 `.29` 上开全量分词（那是 data 线的活，且会拖慢训练 IO）。
- ✅ commit 前缀 `pretrain plan-v5:`；`MEMORY_PRETRAIN_2B.md` 加一行指针（≤32KB 自滚）。


> **用户令（2026-10-18）**：写《BaiZe 2.22B Mamba2-hybrid 正式训练计划 v5》，主要写 Stable 部分，使用 1.5T tok；warmup=2000 步；S1 每 batch 2M tok 共 500B；S2 每 batch 4M tok 共 1T；学习率 warmup 后恒定 1e-3；数据 S1 用 en_v1_4，S2 混入 20% code、1–2% math 和高质量预训练数据；每 2000 步存 ckpt，用 CS8 评测；估计训练时长。
> 🚫 **本轮只产出文档，不动 `.29` 在跑的训练**（80B decay 健康，见状态头），不占 GPU、不改 `baize_xmodel25_decay_v2.sh`。

**① 交付物（必须两个文件都出）**
1. `reports/report_pretrain_formal_v5_plan_zh.html` —— **中文自包含 HTML**（与既有 `reports/*.html` 同风格：`<table>` 数据表 + 结论框，无外链、无 JS 依赖）。
2. `run/PLAN_V5_STABLE_1.5T.md` —— 纯文本/Markdown 版本（便于 diff 与后续任务书引用）。

**② 用户给定参数 = 逐字植入（不得改名、不得改值）**

| # | 参数 | 值 |
|:--|:--|:--|
| 1 | warmup | **2000 步** |
| 2 | S1 每 batch token | **2M tok/step**，总量 **500B tok** |
| 3 | S2 每 batch token | **4M tok/step**，总量 **1T tok** |
| 4 | 学习率 | warmup 后**恒定 1e-3**（S1、S2 全程同一常数，不做 cosine/decay） |
| 5 | S1 数据 | **en_v1_4 单一来源（100%）** |
| 6 | S2 数据 | code **20%** + math **1–2%** + 高质量预训练数据（其余 S2 份额） |
| 7 | ckpt | **每 2000 步**保存 |
| 8 | 评测 | 每个 ckpt **CS8**（Common8，0-shot；口径见 §最佳实践，`CS8 Avg`） |
| 9 | 总量 | Stable 段 **1.5T tok** |
| 10 | 后续次序（用户追加） | **S2 → decay → 长上下文（ABF）拉到 1M → SFT/RL**（长上下文阶段单独算 ETA、单独成章，见 ④-bis） |

派生（必须自己算、把算式写进文档，不要只给结果）：
- S1 步数 = 500B / 2M = **250,000 步**；S2 步数 = 1T / 4M = **250,000 步**；合计 **500,000 步**（+2000 warmup）
- ckpt 数 = 500,000 / 2,000 = **250 个**（S1 125 + S2 125）
- S2 各源 token：code = 20%×1T = **200B**；math = 1%～2% → **10B～20B**；高质量预训练 = 其余 **780B～790B**
- tokens/param = 1.5T / 2.22B ≈ **676 tok/param**
- 每 2000 步的 token 量：S1 = 2M×2000 = **4B tok**、S2 = 4M×2000 = **8B tok** ⇒ 按 BaiZe 基准吞吐（249K tok/s）ckpt 间隔约 **4.5h（S1）/ 8.9h（S2）**

**③ 时长估算（硬性要求：给口径 + 三档情景，禁止只给一个数）**
- 🔴 **基准吞吐 = BaiZe 2.22B Mamba2-hybrid 实测 249K tok/s**，配置 **TP1·DP8·MBS2·seq 4096·GBS 1024·bf16**（来源：T3 / P-9.6–9.7「P-8 最优 = TP1·MBS2·bf16 = 249K tok/s」，见 `MEMORY_PRETRAIN_2B.md` 与 `ARCHIVE_OPERATOR_PRETRAIN.md`）。
  - ⚠️ **不要把 298.6K tok/s 当成本模型基准**：那是 **Xmodel-2.5 80B decay** 在 `.29` 的实测（seq 3712 / GBS 960），**模型与序列都不同**，只能当"同机上限"参考，不可混用。
  - 该基准下 1 step = 4096×1024 = **4.19M tok ⇒ 16.84 s/step**。
- 纯训练（按 249K）：S1 500B/249K = **557.8h**；S2 1T/249K = **1,115.6h**；合计 **1,673.4h ≈ 69.7 天**。
- **v5 的 2M/4M tok per step 与基准 4.19M 不同** ⇒ 必须按 token 数折算（假设吞吐与 batch 组合无关，写进文档）：
  - 2M tok/step（seq 4096 ⇒ GBS 488）⇒ **8.0 s/step**
  - 4M tok/step（seq 4096 ⇒ GBS 976）⇒ **16.1 s/step**
- **必须同时给出吞吐敏感性表**（用户会据此排期）：

| 吞吐 | 1.5T 纯训练 | 说明 |
|:--|:--|:--|
| 218K tok/s | **79.6 天** | P-9.1 同配置早测值（疑有争用，保守下界） |
| **249K tok/s（BaiZe 基准）** | **69.7 天** | T3/P-9.6–9.7：TP1·DP8·MBS2·seq4096·GBS1024·bf16 |
| 280K tok/s | 62.0 天 | 若 S1 纯 web 短样本、packing 更满 |
| 320K tok/s | 54.3 天 | 需 FP8 / 更优 kernel（T3 实测 FP8 在 TP1 s=0.915 未提速） |

- **必须给 FLOPs 交叉验证**：总 FLOPs = 6×N×T = 6×2.22e9×1.5e12 ≈ **2.0e22**；8×H100 bf16 dense 989 TFLOPS ⇒ 时长 = FLOPs/(8×989e12×MFU)。
  - **249K tok/s 反推 MFU ≈ 41.9%**（6·N·249K / (8×989T)）→ FLOPs 口径同 MFU 下 = **33.2 天**（与 69.7 天差 2.1×）。
  - MFU 30% → 97.4 天；MFU 37% → 79.0 天。
  - ⚠️ **两个口径差 2.1×，必须在文档里解释**：token 口径来自**真机实测吞吐**（含 SSM scan、通信、优化器、packing 填充与 dataloader），FLOPs 的 6ND 只算 dense matmul（Mamba2 的 scan/conv 不计入、且 2.22B 未含 embedding 以外的稀疏开销）。**结论以 token 吞吐口径（69.7 天）为准，FLOPs 仅作 sanity check**。
- **另给"含评测的真实日历时间"**：250 个 ckpt × CS8 评测（用既有 8 GPU 并行评测流程的处理时间；若未知，用 3–5 min/ckpt 的区间并标注为假设 ⇒ 12.5–20.8h）+ 启动/重启/故障余量 5% ⇒ 给出 **日历天数区间**（以 69.7 天为底 ⇒ **约 74–76 天**）。

**④-bis 🧵 长上下文能力注入（用户追加令 2026-10-18，必须单独成章）**

> **用户令**：写计划时考虑长上下文能力如何注入；之前比较过 **ABF vs YaRN，倾向 ABF**；次序为 **S2 之后先 decay → 长上下文拉到 1M → SFT/RL**。要求回答"这个次序怎么样"。

1. **注入方案 = ABF（不是 YaRN），且分两层写清**：
   - **推理侧（零训练）**：`rope_theta 1e4 → 1e6` + `max_position_embeddings 4096 → 1048576`（沿用 `baize_b1_longctx_extend.py` 的 B1 写法）。既有实测：**PPL 4K 83.24 → 128K 54.66 → 1M 55.42，全程 53–56 无退化**；机制解释必须写——**56 层里只有 4 层 full_attention 吃 RoPE，Mamba2 层无位置编码** ⇒ ABF 只需适配 4/56 层，这是 hybrid 相对 dense 的结构性优势。
   - **训练侧（真正"注入"）**：ABF 免训练只保 PPL，**不产生 needle/多跳检索能力**（B1 已证 passkey 0%，且明确"是模型能力问题不是 ctx 问题"）⇒ 1M 能力必须在**长上下文续训阶段**用真实长文档训练，不能只靠配置外推。
2. **ABF vs YaRN 对比表必须写全（含代价，不得只写优点）**：
   - ABF：**税 = PPL@4K +10.5%**（75.36→83.24），换来免训练到 1M；实现零依赖（改 config）。
   - YaRN：需 rope_scaling 参数（factor/original_max_pos/attn_factor），对只作用于 4 层的 hybrid 收益有限、且引入新的超参面；仓库既有结论是 **hybrid 应沿用 B1 的 ABF 写法，dense 才需 YaRN/rope_scaling**（`ARCHIVE_OPERATOR_PRETRAIN.md`）。
   - 结论：**v5 采用 ABF**；YaRN 仅作对照/兜底（若长上下文阶段发现 ABF 在 1M 的 attention 稀释问题严重，再评估 YaRN + 更长 RoPE 训练）。
3. **次序评估（正面回答"decay → 1M → SFT/RL 怎么样"）**：给出结论 + 理由 + 风险，逐条：
   - **decay 在 1M 之前**：✅ 合理——先让 Stable 段收敛（LR 从 1e-3 降下来），再进长上下文；否则恒定 1e-3 在 1M 长度上会破坏已学分布。
   - **1M 在 SFT/RL 之前**：✅ 合理——对齐阶段（SFT/RL）的样本要"装得进"上下文，长上下文能力必须先具备；顺序颠倒会逼 SFT 用短样本、再返工。**但要求写成"长上下文阶段也是预训练的一部分"，用 pretraining 数据（长文档/代码库/多文件仓库），不是 SFT 数据。**
   - **风险 1（必须给对策）**：1M 阶段吞吐会崩（attention 占比 ~77%，1M PPL 单次 172s，既有实测）⇒ 需给出 **seq 课程**（如 32K→128K→256K→512K→1M 阶梯）、每档 token 预算、以及"用 ABF 外推 + 只在 128K 做训练、1M 靠外推"的**降本方案**。
   - **风险 2**：decay 之后 LR 已降到低值，长上下文阶段 LR 若继续低位会学不动 ⇒ 建议该阶段**单独设 LR（小幅回升，需用户批准，不得擅改）**。
   - **风险 3**：SFT/RL 前必须做**长上下文能力门禁**（needle/RULER/长文档 QA），不达标不进 SFT。
4. **篇幅与产出**：在 v5 文档中**新增独立章节「长上下文注入（ABF）」**，含：注入时序图（文字版）、各阶段 seq/LR/token 预算表、ABF 配置表（含 key/value 级 diff）、能力评测矩阵、以及 **对"decay→1M→SFT/RL"次序的明确裁定（采纳/调整建议 + 理由）**。同时在计划里把这三段并入总时长估算（**1M 阶段单列 ETA，不与 1.5T Stable 混算**）。

**⑤ 必须在文档中正面回答的 4 个可行性问题（这是本计划的核心价值）**
1. **学习率 1e-3 恒定**：与历史对照（P-8 用 3e-3；decay run 用 1.67e-3→1e-5；R3 BO best 的 LR）——给出「1e-3 恒定」是否会**欠拟合/后期不收敛**的判断，并给出**监控判据**（每 2000 步 recorded loss 若在 S2 后半段仍单调不降 ⇒ 建议在 S2 末端加短 decay，需用户批准，**不得擅改**）。
2. **batch 从 2M 跳到 4M**：v5 的 per-step token 变了 ⇒ 必须给出 **seq/GBS 的等效组合**（保持 seq 4096、MBS 2 时：2M tok/step ⇒ **GBS 488**、4M tok/step ⇒ **GBS 976**；若改成 seq 4096/GBS 1024 则 4.19M tok/step，需说明是否接受），以及切换时**梯度累积步数**、**每 step 时间**（8.0s → 16.1s@249K）、**S1 末 vs S2 初的 loss 断点**记录方式。
3. **数据量核对**：S1 需要 **500B tok** en_v1_4 ⇒ 按 2.2T tok 全量 ≈ 23%；但**当前 en_v1_4 只下完 85/110 shard（≈4.1T bytes）且尚未分词** ⇒ 500B 可行性取决于「剩余 25 shard 续传（`.23+hf-mirror` 已实测 200）+ 分词吞吐」。给出**前置条件表**：需要多少 TB、分词多少 B tok/天、按现速多少天。
4. **S2 混料供给**：code 需 200B，而 UltraData-Code 全量 ≈411B（够）；math 需 10–20B，UltraData-Math ≈303B（够）；高质量预训练（780–790B）从 `ultraweb_en`(≈1T tok) + `l1_en_hq`(152B) + `zh`(112B) + `UltraX`(31B) 取。**逐项写"需求 vs 可用 vs 余量倍数"，并标出哪个是瓶颈**（以 `DATA_LEDGER.md` 为唯一数据源，🚫 凭印象编造 token 数）。

**⑥ 文档结构（必须齐全）**
0. 一页结论（总量/时长/风险/所需前置；**含"decay→1M→SFT/RL"次序是否采纳的一句话裁定**）
1. 模型与并行配置（2.22B Mamba2-hybrid；TP/PP/DP、MBS、seq、GBS、bf16、compile）
2. 两阶段配方表（S1/S2 的 tokens/step、总 token、步数、LR、数据配比）
3. 数据配比与来源（逐项 token 需求/库存/余量）
4. 时长估算（基准 + 敏感性 + FLOPs 校验 + 日历时间）
5. ckpt 与评测（每 2000 步、CS8 口径、250 次评测的调度与耗时）
6. **长上下文注入（ABF）**：ABF vs YaRN 对比（含 +10.5% PPL 税）、推理侧配置 diff、训练侧 seq 课程与 token 预算、1M 阶段独立 ETA、能力门禁（见 ④-bis）
7. **风险与待拍板项**（至少含：LR 恒定、2M→4M 跳变、en_v1_4 未分词、250 个 ckpt 的存储/评测开销、**单机连续 70 天的故障恢复**、1M 阶段吞吐塌陷与长上下文阶段 LR）
8. 里程碑表（按周：第 N 周应到 S1/S2 的哪个 checkpoint、期望 CS8 区间；以 249K 基准推算，S1 需 **23.2 天**、S2 再需 **46.5 天**；之后单列 decay / 1M / SFT-RL 的里程碑）

**⑦ 写作纪律**
- 🚫 数字必须可追溯：每个 token 数/吞吐/时长后面括号注来源（**BaiZe 吞吐引 T3/P-9.6–9.7 的 249K**；数据引 `DATA_LEDGER.md`；算式自带）。**禁止把 Xmodel-2.5 的 298.6K tok/s 当作本模型基准**（那是 80B decay 在 `.29` 的实测，模型/seq 都不同，只能作同机上限参考）。
- 🚫 不把"计划"写成"已完成"；未验证的假设（如 CS8 评测 3–5 min/ckpt）要**标 `[假设]`**。
- ✅ commit 前缀 `pretrain plan-v5:`；写完在 `MEMORY_PRETRAIN_2B.md` 顶部加一行指针（体积 ≤32KB，超了自滚）。
- ✅ 本令**不改变**正在跑的 80B decay v2（🚫 不重启、不 kill）；两者独立。


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

