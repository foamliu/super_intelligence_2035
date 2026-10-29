# BAIZE_PRETRAIN_2B_TASK.md

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### [运维令] 2026-10-29 14:1x（**整理并提交 baize-llm 独立仓库**）· 用户直令 · 最高优先

> 用户原话（2026-10-29 14:1x）：「请 pretrain 把 baize-llm 这个仓库整理提交一下」

**① 现状（运维已核）**：
- `/nas_train/app.e0031982/code/baize-llm/` 是**独立 git 仓库**，remote = `ssh://git@devops.cxmt.com:8022/git/AIX/PAI/eda/baize-llm.git`，当前只有 `Initial commit`；`README.md` 是 582B 的**空模板**（「请介绍一下你的项目吧」）；工作树里还有一个**未跟踪的 symlink** `baize-llm -> super_intelligence_2035/code/baize-llm`（`git status` 显示 `?? baize-llm`）。
- 真实代码（`configs/` 10 个、`scripts/` 18 个、`docs/` 2 个、`README.md` 19.6KB）全在**主仓库** `super_intelligence_2035/code/baize-llm/` 下，已随主仓库持续提交（最近 `281384228 pretrain train`）。

**② 要求（整理 + 提交，按序）**：
1. **补全独立仓库 README.md**：把 582B 空模板替换为真实项目说明（项目定位 / 目录结构 / 三阶段 S→S2→Decay 口径 / 启动命令 `bash scripts/train.sh <stage>` / 配置说明 / 依赖环境），与主仓库 `code/baize-llm/README.md`（19.6KB）口径一致、可照做。
2. **把真实代码纳入独立仓库**：将 `configs/`、`scripts/`、`docs/`（去 `__pycache__`、`.pyc`）整理进独立仓库工作树，`git add` 后 `git commit`（commit 信息带 `pretrain 项目:` 前缀）。
3. **push 到 origin/devops**：`git push origin master`（若 push 失败带代理重试：`https_proxy=$P http_proxy=$P git push origin master`），确认 devops `baize-llm.git` 上已可见完整代码。
4. **symlink 处置**：那个未跟踪的 `baize-llm` symlink 要么纳入 `.gitignore`、要么删除，🚫 不许把 symlink 当真实文件提交。

**③ 判据**：`git -C /nas_train/app.e0031982/code/baize-llm status` 干净；`git -C ... log --oneline` 最新提交为本轮；`git -C ... push` 后 `git ls-remote origin` 可见新 commit；README 非空模板。

**④ 纪律**：不打断 S1 主线（iter 9600+ 在跑，纯 git/文件整理零 GPU）；不碰 vision/data/harness；心跳写 `未完成指令：有` ⇒ `WAITING: 0` 直到 push 成功；只提交 baize-llm 独立仓库相关文件。

### [运维令] 2026-10-28 17:0x（**预训练项目目录定位：脚本&文档落在 `/nas_train/app.e0031982/code/baize-llm/baize-llm`，后续训练从此启动**）· 用户直令 · 最高优先

> 用户原话（2026-10-28 17:0x）：「安排 pretrain 往项目目录 /nas_train/app.e0031982/code/baize-llm/baize-llm 写脚本&文档。后续训练从项目目录启动。」

**① 项目目录定位（运维已核现状）**：`/nas_train/app.e0031982/code/baize-llm/baize-llm` 当前是 symlink → `super_intelligence_2035/code/baize-llm`（已含 `configs/`/`scripts/`/`docs/`/`README.md` 14.3KB）。外层 `/nas_train/app.e0031982/code/baize-llm/` 是独立 git 仓库（README 仅 582B、另有 symlink）。

**② 要求**：脚本（`train.sh`/`pre_blend.py`/`gen_blend.py`/`check_rope.py`/`check_longctx_data.py`/`activate_preblend.sh` 等）与文档**全部落在该项目目录并 git 提交**；`README.md` 补全到「从零按 README 即可在项目目录启动训练」的程度（目录结构 / 启动命令 / 三阶段 S→S2→Decay 口径 / 配置说明 / 依赖环境）。

**③ 后续训练启动口径（硬性）**：一律 `bash /nas_train/app.e0031982/code/baize-llm/baize-llm/scripts/train.sh <stage>` 启动；🚫 不再从 `run/` 散落脚本启动。`common.env` 的 `BAIZE_TRAIN_CODE` 与启动文档与此路径对齐。

**④ 优先级**：不打断主线——先续跑 en_v1_4 pre-blend 剩余 s012-s015 → activate → 起 S（双机 16 卡 GBS256）；本令的「脚本&文档落项目目录」可在起 S 后的空档补齐。

commit `pretrain 项目:`。

> 📦 §运维令 2026-10-28 11:5x（blend 逻辑中文 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：报告已交付 `reports/report_pretrain_blend_logic_zh.html`（11KB, commit aa6d3eddf），澄清训练时不会串行出不同源（索引层交错）。需要时再读。

### [运维令] 2026-10-28 10:0x（**预训练计划定稿：Stable 4M/step × 70w 步 = 2.94T + 数据 pre-blend → nw=8 保 613K**）· 用户直令 · 最高优先

> 用户原话（2026-10-28 10:0x）：「训练计划已定稿，成文见 `doc/BaiZe-ISEDA2027/reports/report_pretrain_baize2b_training_plan_final_zh.html`；把 S 换成 4M tok/step（2.94T），数据做 pre-blend（只 Stable），pre-blend 不用等全部完成即可开训。」

**① 定稿口径（取代 09:3x 的 spawn 调试路径，spawn 不再是主路）**
- 配方冻结不变：16K / CP1 / DP16 / **mbs=1 / gbs=256 / accum=16** / FP8 tensorwise / graph OFF = **613,992 tok/s**。🚫 不许再为吞吐改 seq/TP/CP/精度/graph。
- **Stable（S1+S2 合并为 S）**：`GBS=256`、`ITERS=700000`、seq=16384 → **4.19M tok/step → 2.94T token**。config 落点：`s1.env` GBS 128→256（ITERS 保持 700000）。
- **Decay**：4M/step、80B、~20000 步（80B vs 83.9B 的 5% 出入 Decay 起跑前定夺）；`UltraData-SFT-2605`/`SFT-Agent-2609` 未分词 → 后置。
- **LR**：AdamW + WSD（2000 步 warmup → 1e-3 恒定；Decay 段指数衰减）。7 源配比沿用 `blend_s1.tsv`。

**② 吞吐恢复改为「pre-blend → nw=8」**
- 根因已定：627 片小 shard 的 blend 采样/索引撑大 fork-COW → OOM → 被迫 nw=0 → 数据/计算串行（308K）。pre-blend 把各源合并成 **~16–32 片大 shard**（对齐 613K 基线用的 16 片 p5b_l3 结构）后索引骤小、COW 可忽略 → **恢复 nw=8（fork 即可，不必 spawn）**。
- 只 pre-blend **Stable 7 源**（Decay 暂不）；输出目录 `/nas_user/app.e0031982/datasets/pre-blend`；.12/.29 并发多开；**按源分开做，每源做完即可换入 gen_blend，无需等全部完成**。
- pre-blend 完成前可用现有 tokenized 数据先起 smoke/验证；全量 S 起跑前至少把 en_v1_4（0.65 主源）pre-blend 完并换入。

**③ 长上下文 / 监控（不变）**：ABF θ=1e6 + RoPE max_position=1048576（4 层注意力）；TB 常驻 `.29:6006`。

**④ 交付**：① 改 `train.sh`/`configs`（GBS=256）+ 重生成 blend；② 8 卡 smoke（gbs256 + pre-blend 后 nw=8）验证 0 NaN + 吞吐 ≥500K，16 卡稳态对齐 613K；③ 起跑 S 前 `check_rope.py` PASS；④ 计划报告在位 `doc/BaiZe-ISEDA2027/reports/report_pretrain_baize2b_training_plan_final_zh.html`；commit `pretrain train:` / `pretrain run:`。

**⑤ 纪律**：不碰 vision/data/harness；盯内存/swap/磁盘余量（pre-blend 写 ~6TB）；心跳写 `未完成指令：有` ⇒ `WAITING: 0` 直到 smoke 交付；只 add 自己线文件。

> 📦 §运维令 2026-10-28 09:3x（锁定 613K 配置 + spawn 调优）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：613K 配方已冻结（16K/CP1/DP16/FP8/graph-OFF），根因=数据加载串行化(nw=0)，spawn 路径被 10:0x pre-blend 取代。需要时再读。

### [运维提示] 2026-10-27 15:2x（**cimi MCP web search 已配好，可用于调研**）· 用户直令 · 最高优先

> 用户原话：「可以提醒 pretrain 可以 web search（cimi search）」
> **本线 MCP 工具已就绪**：`cimi_search`（web 搜索）/ `cimi_fetch`（抓网页全文）/ `vqa` / `text_to_image`（cline MCP，type=streamableHttp，指向 `http://10.239.2.29:8092/mcp`）。下一轮唤醒（新 cline 进程）即生效。
> **排查/调研时直接用 `cimi_search`**——查 fork-COW 免 OOM、16K 吞吐优化、DataLoader 最佳实践等。🚫 别再只依赖 fetch_web_content 或被 proxy 卡住。

> 📦 §运维令 2026-10-27 13:1x（杀掉 S1 + spawn smoke）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：S1 已杀，spawn 方案被 2026-10-28 10:0x pre-blend 取代。需要时再读。
> 📦 §运维令 2026-10-27 10:4x（不放弃：spawn 验证 + web 调研）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：spawn 被 pre-blend 取代；web 调研授权仍有效（见 15:2x）。需要时再读。
> 📦 §运维提示 2026-10-27 09:2x（DataLoader OOM fork-COW 根因 + spawn 方案）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：fork-COW 是 RSS 累积根因，spawn 方案被 pre-blend 取代。需要时再读。

### [运维提示] 2026-10-27 08:4x（**内存使用率 >95% 会触发告警，调试时注意**）· 用户直令 · 最高优先

> 用户原话：「告诉 pretrain 内存使用率>95%会导致告警，让它调试时注意。」
> 刚从 #802/#803 的 DataLoader OOM（.29 swap 耗尽 → SIGKILL）时也印证：调试/测吞吐务必盯 **内存 + swap**，避免把内存打到 >95% 触发告警。措施：num_workers 节制、并发/预留窗口适度、及时释放不再用的进程/张量；若逼近 95% 先降载并上报，不要硬顶。

> 📦 §运维令 2026-10-26 22:0x（S1 吞吐对齐 613,992：归因 + 方案 A/B/C）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：#798 归因=gbs128 固定开销摊薄不足；吞吐目标 ≥600K 由后续 10:4x/13:1x 令推进（spawn 验证中）。参数口径 2.220B 仍有效。需要时再读。


> 📦 §运维令 2026-10-26 21:3x（RoPE θ 未生效：评估 + 方案 + 重启）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：θ=1e6 实现路径(ii) `--rotary-base` CLI + recipe 透传，commit ae3a093，三重验证 PASS；#799 运行时确认 θ=1e6 + 0崩；rank15 崩因=DDP DETAIL wrapper（非θ）；--dir 修正已落地。**仍有效红线**：check_rope.py PASS 需 ckpt（待 S1 重启）；lr-decay-shape exponential Decay 前验证。需要时再读。


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
- 报告已按六条修订：`doc/BaiZe-ISEDA2027/reports/report_pretrain_baize2b_pretrain_plan_zh.html`（新增 §五「执行口径与工程落地」；§4.2 改为「已定案」；**μP 内容全删**）。
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
> 📦 §运维令 2026-10-25 20:2x（seq 掉速排查初版）已并入 23:0x 通宵令 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-25 17:5x（seq×tok/step 16卡网格）已完成（cfg1-4 OK）→ ARCHIVE_OPERATOR_PRETRAIN.md；注意「seq≥8192 崩 5x」已被 cfg0a 证伪。需要时再读。
> 📦 §运维令 2026-10-25 07:4x（双机 16 卡吞吐报告）已完成（#770-#776）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维令 2026-10-24 23:5x（双机调通→吞吐优化）已完成（606,300 tok/s）→ ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。
> 📦 §运维指令 2026-10-24 16:0x（305K 最佳实践+longctx 报告）已完成 → ARCHIVE_OPERATOR_PRETRAIN.md。需要时再读。

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

> 📦 §R2.4 约束（R2 实验预算/超时裁剪/vision 让行；R2 P-1~P-8 已全部完成）已归档 → run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md。**仍有效条款**：绝不杀他人进程 / 收尾不杀 loop（见 git 同步规则）。需要时再读。

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

