# BAIZE_PRETRAIN_2B_TASK.md

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### [运维令] 2026-10-26 22:0x（**S1 吞吐对齐 613,992：先解释 ~480K 的差距，再选方案**）· 用户直令「目标是复现 613,992 基线」· 最高优先

> 用户原话：「pretrain 需要想办法提高S1吞吐，目标是复现 613,992 基线」。
> **实测（ops 中继 RUN_ID 217，S1 当前跑法）**：gbs=128 ⇒ 2,097,152 tok/step；step time **4.09 / 4.87 / 5.20 s** ⇒ **≈400–510K tok/s**，
> 仅为 #792 基线 **613,992 的 65–83%**。#792 基线档 = `seq16384 / mbs1 / gbs256 / accum16 / CP1 / DP16 / FP8 tensorwise / graph OFF / 2 节点 16 卡`。

**请按序给结论（不要一次改一堆参数）**
1. **归因（必须先做）**：用 Megatron timers 或 nsys 抓 step 50–200，给 **per-step 分解**（forward / backward / optimizer / grad-allreduce / dataloader / 空隙）。
   判据：明确说出「613K→480K 的差额主要落在哪一项」——固定每步开销、计算效率、还是通信/数据。
2. **方案三选一并给证据**：
   - **A（最直接，优先验证）**：S1 的 `gbs 128 → 256`（=4,194,304 tok/step，与 #792 E1 完全同档），步数 `700k → 334k`，**总 token 仍 1.4T 不变**。
     预期 ~614K、墙钟不增；须交代「S1 小 batch 阶段」的意图保留还是放弃（+理由）。
   - **B（保持 gbs=128，压固定开销）**：`--overlap-grad-reduce` / `--overlap-param-gather` / `--use-distributed-optimizer` / dataloader workers 数量与 prefetch / NCCL env，
     **一次只改一项**，每项 ≥30 步取稳态，逐项记录（收益/副作用）。
   - **C（折中）**：`gbs=192`（3,145,728 tok/step）测一档，把 2.1M/3.1M/4.2M 三点连成 tok/s 曲线。
3. **红线**：🚫 不许开 CUDA Graph（tok/mb=16384 下会崩到 ~110K）；🚫 tok/mb/GPU 必须 ≤16,384；🚫 FP8 tensorwise 不改；🚫 不许用「更多 token/step」冒充提速（验收看 **tok/s**）。
4. **验收**：稳态（step 50–200 中位数）**≥ 600K tok/s**（≥0.98×613,992）。达不到 ⇒ 给「可行上限 + 结构性原因」的量化结论，并同步改报告 §3 ETA
   （按 480K 算 S1 已从 27.7 天变 **~36 天**，必须让 ETA 不再用 613,992 那一档）。
5. **与 21:3x 令（θ=1e6）同批交付**：θ 未生效（无 `check_rope.py` PASS / 无 provider 打印证据）前，不许起 700k 步正式跑。
6. **附带（阻塞项，先修）**：21:40:43 停机的直接原因是
   `[rank2] RuntimeError: DataLoader worker (pid 3102075) is killed by signal: Killed`
   （主机 2TB 内存 free 1.9TB，但 swap 7G 已满、`dmesg` 无权限）⇒ 请给结论：是 cgroup/单进程上限还是 worker 泄漏；
   建议同时降 `num_workers`（当前 64/节点）并用 `TORCH_DISTRIBUTED_TORCH_TRACE=/tmp/td_trace_%rank` 抓下次失败的 rank traceback（别再出现 `error_file=<N/A>`）。


### [运维令] 2026-10-26 21:3x（**RoPE θ 未生效：请你评估并给出方案，再重启 S1**）· 用户直令「把这个问题跟 pretrain 沟通，让它考虑」· 最高优先

> 用户原话：「把这个问题跟 pretrain 沟通，让它考虑。」
> 这不是命令你照做，而是**把现场证据交给你判断**：请给出你的结论 + 实现选择 + 理由，我们保留否决权。

**一、现场事实（全部来自 ops 中继只读探针，可复核）**
1. S1 确实跑起来过：21:12 起 16 卡（.29 8 + .12 8），**19,049 MiB/卡 · 100% util**；TB 6006 `http=200`；blend 627 shards。`--optimizer adam` ✓ `--lr-decay-style WSD` ✓ `--save-interval 2000` ✓ 无 `--enable-cuda-graph` ✓ `--fp8-recipe tensorwise` ✓（RUN_ID 214）
2. **但实际命令里没有 `--rotary-base`**；`pretrain_launcher.py --help` 无该参数；`mamba2_hybrid_2b/recipe.py` 只有 `apply_rope_fusion`，**没有 `rotary_base`** ⇒ θ 走 Megatron 默认 **1e4**（RUN_ID 215/216）。
3. 21:18:34 **rank 15（.12 / local_rank 7）exitcode=1**，`error_file=<N/A>` 无 traceback；21:22 前后主进程收到 **SIGTERM(15)** 被整体停掉；21:24 16 卡回 4 MiB（RUN_ID 216）。
4. `nemo_experiments/` 里**没有 `baize2b*` 目录/ckpt**，只有 `/tmp/baize_s1_baize2b_smoke*.log` ⇒ 正式 run 的 `--dir` 可能指到 `/tmp`（RUN_ID 215）。
5. blend 跳了 1 片坏 shard：`env14_CC-MAIN-2023-23: ptr overflow max_ptr=122,496,093,768 >= bin_size=49,025,167,172` ⇒ 109/110，权重已摊平。**这是 data 侧问题，你不用改数据**，只需在心跳里记一行。

**二、为什么必须先解决（不能带着跑）**
- θ 是**训练期固定量**，训完不能补；用户 20:1x 令「56 层中 4 层注意力的 RoPE max position = 1M」，落地口径 = `max_pos=1,048,576` + `θ=1e6`。
- 本项目 2026-10-06 B1 实测：**只抬 max_pos 不改 θ ⇒ 全 NaN（连 4K 都 NaN）**；`θ=1e6` 才能从 16K 外推到 1M（PPL 32K/128K/1M = 58.55/53.34/55.42）。
- 即：**现在这套跑法训出来的 ckpt 不具备 1M 能力**，而 1M 是产品目标（用户明确「要不为啥预训练就用 16K 这么长」）。

**三、请你给结论（按这四点回）**
1. **实现路径二选一 + 理由**：
   (i) `mamba2_hybrid_2b/recipe.py::pretrain_config` 增 `rotary_base: int = 1_000_000` 并 `kwargs["rotary_base"]=rotary_base`（改动小、影响该 arch 全配方）；
   (ii) `pretrain_launcher.py` 增 `--rotary-base`（显式可配，但要同时改 CLI 与 provider 透传）。
   请说明你选哪个、对现有其它配方（minicpm5 5e6 / xmodel 5e5）有无副作用。
2. **生效证据怎么给**（任选其一并写进心跳）：① provider 初始化时打印 `transformer_config.rotary_base`；② 导出 HF 后 `python code/baize-llm/scripts/check_rope.py --hf-dir <dir>` **PASS**（56 层 / attention=4 / max_pos=1048576 / θ=1e6 / no scaling）；③ 4K PPL 与 θ=1e4 基线对比。
3. **rank 15 exit1 的定位结论**：不要盲重启。建议加 `TORCH_DISTRIBUTED_TORCH_TRACE=/tmp/td_trace_%rank` 或先**单机 8 卡 50 步**复现；给出你判断的最可能原因。
4. **`--dir` 修正**：ckpt 必须落 `nemo_experiments/baize2b_s1`（用户令 ckpt 每 2000 步）；写进 `/tmp` 会在重启/清理时全丢。

**四、红线**
- 🚫 θ 未验证（无生效证据）不许起 700k 步正式 S1；「能跑起来」不算验收。
- 🚫 不许只改 `max_position_embeddings` 不改 θ。
- 🚫 不许为了让 smoke 过而把 warmup/decay 语义改成与正式不一致（`--lr-decay-shape exponential` 仍缺，Decay 阶段前必须补上并留证据）。

**五、交付**
- 心跳写清：**θ 实现方式 / 生效证据 / rank15 结论 / 重启命令（含 --dir 与 --rotary-base 或 recipe 默认值）**；
- commit 前缀 `pretrain train:`（代码）/ `pretrain run:`（实跑）；**只 add 自己线文件**。


### [运维令] 2026-10-26 19:2x（**预训练正式落地并开跑：AdamW / WSD-D 指数 / TensorBoard 6006 / code/baize-llm 项目化**）· 用户直令 · 最高优先

> 用户原话（逐条照录，六条）：
> 1. 监控使用 tensorboard，在 `.29` 服务器监听 `6006` 端口
> 2. WSD 的 **D 段使用 exponential 衰减**
> 3. 优化器用 **AdamW**
> 4. 训练脚本放置在 **`code/baize-llm`** 目录，组织好预训练项目目录结构，写 **README**
> 5. 「你混乱了，**跟 μP 没有一毛钱关系**。」（指上一版报告 §4.2 的 μP 归因 —— 已删除，禁止再提）
> 6. **开始执行**

**已由运维预置（你不需要重写，直接复用）**
- `code/baize-llm/` 全套：`README.md` + `configs/{common,s1,s2,decay}.env` + `configs/blend_{s1,decay}.tsv` + `scripts/{lib,preflight,gen_blend,train,tb_6006,lr_schedule,status}` + `docs/LAUNCHER_PATCH_EXP_DECAY.md`。
- 报告已按六条修订：`run/reports/report_pretrain_baize2b_pretrain_plan_zh.html`（新增 §五「执行口径与工程落地」；§4.2 改为「已定案」；**μP 内容全删**）。
- 关键口径（写死在 `configs/`）：16K / CP1 / DP16 / graph-OFF / FP8 tensorwise / AdamW / WSD-D 指数 1e-3→1e-4 / 三阶段累计 iters 700k→1,050k→1,070k / `--name baize2b`。

**执行步骤（按序，每步留证据）**
1. **部署目录**：`ln -sfn /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm /nas_train/app.e0031982/code/baize-llm`（git pull 后再做一遍）；`ls -l` 确认。
2. **launcher 特性**：`bash code/baize-llm/scripts/preflight.sh`。若报「不支持 `--lr-decay-shape`」⇒ 按 `code/baize-llm/docs/LAUNCHER_PATCH_EXP_DECAY.md` 打补丁（新增一个参数 + WSD 分支，**默认 linear 不变**），并把 `pretrain_launcher.py` 的 diff 存入 `run/` 后 commit。
3. **TensorBoard**：`bash code/baize-llm/scripts/tb_6006.sh start`。判据：`ss -ltn | grep 6006` 见 `0.0.0.0:6006`、`curl 127.0.0.1:6006` 有 HTTP 响应、日志 `/tmp/baize_tb_6006.log` 无 traceback。**必须能在 .29 上常驻**（跨轮询存活）。
4. **冒烟（单机 8 卡）**：`bash code/baize-llm/scripts/train.sh s1 --smoke 20`。判据：0 NaN、`--optimizer adam` 生效、日志无 graph capture、峰值显存 ≤78GB、吞吐落在 480–550K（S1 2.097M tok/step 档）。
5. **LR 指数形状验收**：`python code/baize-llm/scripts/lr_schedule.py --peak 1e-3 --min 1e-4 --warmup 2000 --decay-iters 20000 --total-iters 1070000`，并从 TB 导出 `learning-rate` 做 `--tb-csv` 对账（p=0.25/0.5/0.75 = 5.623e-4/3.162e-4/1.778e-4，相对误差 ≤0.1%）。**若 launcher 无 shape 支持且暂不打补丁，必须显式 `LR_DECAY_SHAPE=linear` 并在心跳写「降级」，不许假装已指数。**
6. **正式开跑 S1（16 卡）**：先核 `.12` 空闲（`train.sh` 会自动拒绝非空闲）；`setsid bash code/baize-llm/scripts/train.sh s1 > /tmp/baize_s1_launch.log 2>&1 < /dev/null &`。起跑后 30 分钟内交 `pretrain run:` 心跳，必须含：`tok/s`、`per-GPU tok/s`、峰值显存、`--train-iters/from`、TB URL、`AdamW` 与 `lr_decay_shape` 实值。
7. **S2 / Decay**：S1 收尾后 `train.sh s2`；Decay **当前禁止开跑**（见下）。
8. **Checkpoint（用户 2026-10-26 补令）**：三阶段 `--save-interval` 统一 **2000 步**（`configs/s1|s2|decay.env` 已改，`train.sh` 自动带上）。起跑后用 `ls nemo_experiments/baize2b/checkpoints/iter_* | wc -l` 确认按 2000 步递增（首个点 = 2000）。**同时必须控盘**：每 20k 步跑 `bash scripts/prune_ckpts.sh --keep-last 3 --milestone-every 25000`（dry-run），每 50k 步 `--apply`；保留最近 3 + 每 25k 里程碑 + `latest_checkpointed_iteration.txt` 指向者。S1 350 个 ckpt 全留会占 1.5–10.5TB。
9. **RoPE / 1M（用户 2026-10-26 补令）**：56 层中 **4 层全注意力**，RoPE **max embedding position = 1,048,576**（1M）；`configs/common.env` 已设 `ROPE_MAX_POS=1048576` + `ROPE_THETA=1000000`（ABF）。`train.sh` 自动传 `--rotary-base 1000000`；launcher 若无该参数会**直接拒绝开跑**（`ROPE_REQUIRED=1`），按 `code/baize-llm/docs/LAUNCHER_PATCH_EXP_DECAY.md` §5 打补丁。导出 HF 后必须 `python scripts/check_rope.py --hf-dir <dir>` **PASS**（56 层 / attention=4 / max_pos=1048576 / theta=1e6 / rope_scaling=None）。冒烟后核对：0 NaN、前 500 步 loss 与 baseline 抬升 ≤5%。
10. **长上下文 ABF 准备（用户 2026-10-26 补令「长上下文用 ABF，要为此做好准备」）**：口径 = **产品目标 1M**（用户 2026-10-26 明确「产品目标自然是长上下文 1M，要不为啥预训练就用 16K 这么长」）、训练保持 **16K**（16K→1M 外推 64×，优于 4K→1M 的 256×）、路径 = **ABF（θ=1e6）外推** + **32K→64K→128K→256K 阶梯**（16 卡上限 256K[CP16/DP1]；1M 原生训练需 ≥64 卡）（`configs/longctx_ladder.tsv` + `scripts/longctx_ladder.sh`，每级保持 tok/mb/GPU=16384）。**本轮必做三件**：① `python scripts/check_longctx_data.py --shards <tokenized源目录> --eod-id 129280 --targets 32768,131072 --sample 8` 出 token 占比（≥32K 应 ≥20%、≥128K ≥5%），写进心跳；② 首个可导出 ckpt 上跑一次**零训练** PPL/passkey 基线（4K→1M，复用 `run/baize_b1_longctx_extend.py`），并补 **RULER/needle**（1M 目标 RULER ≥70%），留档到 `run/`；③ `python scripts/abf_plan.py` 复核 θ/CP 表（默认**不抬 θ**，只在实测退化时升级，升级后必须复测 16K）。完整方案 `code/baize-llm/docs/LONGCTX_ABF_PLAN.md`。

**阻塞与红线**
- 🚫 **Decay 不得开跑**：`UltraData-SFT-2605`（0.60）/ `UltraData-SFT-Agent-2609`（0.12）仍「未分词」（`run/data/DATA_MAPPING.md` 0 shard），`gen_blend.py` 会 rc=2 直接退出。需 data 线分词后才能跑；不许用别的数据偷偷替代。
- 🚫 **不抢 vision**：16 卡 = 借 `.12`；`.12` 非空闲即停手，改单机 8 卡（`--nodes 1`）并在心跳说明。
- 🚫 **不许开 CUDA Graph**：16K 下会掉到 ~110K tok/s（#786/#788 已实测定性）。
- 🚫 不许把「2M/4M」当精确值对外：DP16×16K = 262,144，落地档 = gbs128(2,097,152) / gbs256(4,194,304)。
- 🚫 **磁盘红线**：`/nas_train` 可用 <15TB ⇒ 先 `prune_ckpts.sh --apply` 再继续训练；不许为保 ckpt 把盘写满（会连带卡死 data 迁移与 eval）。
- 🚫 **RoPE 红线**：不许只改 `max_position_embeddings` 不改 `rope_theta`（实测全 NaN）；不许把「训练跑起来了」当成 1M 配置达标（`max_pos` 只在导出 config 生效，必须过 `check_rope.py`）。
- 🚫 **长上下文红线**：不许拿「跨文档拼接出来的长序列」冒充长上下文收益（先看 `check_longctx_data.py` 的 token 占比）；θ 若升级必须复测 16K PPL（退化 ≤1%），否则回退。

**交付物**
- `code/baize-llm/`（已随仓库预置；若你补丁/微调则 commit `pretrain train:`）
- `run/MEMORY_PRETRAIN_2B.md` 心跳（AdamW / shape / TB URL / 冒烟数值 / 起跑状态）
- `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加「§五·9 预训练落地（AdamW + WSD-exp + TB6006 + 项目化）」
- commit 前缀：脚本/配置 = `pretrain train:`；实跑 = `pretrain run:`


> 📦 §运维令 15:3x（预训练构想报告 + ETA）**已完成**（#794：`report_pretrain_baize2b_pretrain_plan_zh.html` 22.5KB；§五执行口径已补）→ 原文归档 run/ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 14:3x（补写 #792 双机实测进吞吐报告）**已完成**（#793：报告 14,208→20,888B）→ 原文同上归档。
> 📦 §运维令 13:2x（FP8 真实数据 16K/32K 实测）**已完成**（#792：16K=613,992 / 32K CP2=351,526）→ 原文同上归档。
> 📦 §运维令 11:1x（双机 16 卡调优 seq16K/32K）**已完成**（#791 8卡首跑 + #792 双机实测覆盖）→ 原文同上归档。
> 📦 §运维令 09:1x（优化 16K/32K 吞吐至 600K+）**已完成**（#791 8卡 + #792 双机 16K=613,992 ≥600K）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
> 📦 §运维令 08:2x（写最近工作报告 · 中文 HTML）**已完成**（#790，report_pretrain_recent_work_zh.html 20KB）→ 原文同上归档。
> 📦 §运维令 2026-10-25 23:0x（通宵攻坚：tokens/microbatch 悬崖）**已完成**（#784–#789：真因=CUDA Graph 顶格停滞·关 graph 修复·16K 双机 613,992 达标；根因报告 + seqlen rev3）→ 原文归档 ARCHIVE_OPERATOR_PRETRAIN.md。
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

