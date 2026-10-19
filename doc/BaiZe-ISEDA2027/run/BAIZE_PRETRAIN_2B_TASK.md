# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 📄 运维指令 · 2026-10-20 06:1x（**事故复盘报告已由运维编写 → 你去核实数据 + 落地 P0 两项**）· 用户直令

> 用户令：「先让 pretrain 写个中文 html 报告 复盘昨夜发生的问题和解法建议」
> **报告已由运维全部写完并入库**：`reports/report_pretrain_crash_20261020_zh.html`（15KB，自包含单文件，无外链/无脚本）。
> **你不需要重写报告**，只需做下面 3 件事：

**① 核实报告中的事实（与你手里的 log/进程对账）**
逐条核对并在 `daily-memories/2026-10-20.md` 写出「核对结论」：
- 崩溃时刻 **02:45:25**、错误 `NCCL collective timeout (rank6) → SIGABRT`、最后 step **19,920/19,980**
- resume 起点 **step_18000（10-19 20:21）**、损失 **1,920 步 ≈ 6.4h**
- 无人处理窗口 **02:45→04:00 = 75 分钟**
- resume 后 **~12s/step、8×GPU 96-100%、0 error**（与崩溃前一致，无降频）
- **代码事实**：`baize_xmodel25_decay_v2.py` 的 `dist.init_process_group(backend='nccl')` **无 timeout 参数**；`.sh` 中 `NCCL_*` / `TORCH_NCCL_*` **0 处**
- **SAVE_INTERVAL**：脚本现值 500（原 2000）
> 若任一项与你的证据不符 → **以你的实测为准**，在 daily 里写明差异 + 证据，并回报运维（报告可修正）。

**② 落地 P0 两项（不碰运行中进程，全部为增量）**
- **P0-a `TORCH_NCCL_DUMP_ON_TIMEOUT`**：**只写进脚本文件供下次 resume 生效**，🚫 **不要为此重启当前 run**（当前 92%+，重启代价远大于收益）。即：在 `.sh` 的 env 段追加
  ```bash
  export TORCH_NCCL_DUMP_ON_TIMEOUT=1
  export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
  export NCCL_ASYNC_ERROR_HANDLING=1
  ```
  并**在下次 resume 日志里确认这些变量生效**（`tr '\0' '\n' < /proc/<pid>/environ | grep NCCL`）。
- **P0-b 崩溃自动重启 watchdog**：新建 `run/baize_decay_watchdog.sh`（**新文件，不改现有脚本**），要求：
  - 每 **5 分钟** 检查 `pgrep -f 'xmodel25_decay_v2'`；
  - 进程消失 且 最近 step < ITERS 且 **24h 内崩溃 < 3 次** ⇒ 自动 `RESUME_DIR=<最新完好 ckpt> setsid bash baize_xmodel25_decay_v2.sh`；
  - **防死循环**：崩溃计数落文件（如 `/tmp/decay_watchdog.crashcnt`），24h ≥3 次则**停止自动重启并写 blocker**；
  - **判活必须用 `strings /tmp/baize_xmodel25_decay_v2_train.log | grep '^\[step'`**（该 log 是 sparse file，`tail` 不可靠）；
  - 🚫 **当前 run 未结束时先不要启动该 watchdog**，或启动时加 `--dry-run` 只记录不动作（避免与人工 resume 冲突）。

**③ 回填 P2 数据（硬件是否永久故障）**
在**训练收尾后**（预计 ~10:30）执行一次只读硬件检查，结论补进报告 §3 与 `MEMORY_PRETRAIN_2B.md`：
```bash
nvidia-smi -q | grep -iE 'Xid|ECC|Remapped|Retired'
nvidia-smi --query-gpu=index,temperature.gpu,clocks_throttle_reasons.active --format=csv
dmesg -T 2>/dev/null | grep -iE 'xid|nvrm|fallen off' | tail -20
```
> 判据：无 Xid 且可纠正 ECC=0 ⇒ 瞬时；有 Xid / ECC 增长 ⇒ 该卡有隐患，报 blocker 建议巡检。

**纪律**：🚫 不重启当前训练（92%+，稳中）· 🚫 不改 ITERS/LR/数据 · 🚫 不动 `.12` 的 vision ArmD · 报告文件**不要改**（如需修正请写差异给运维）。commit 前缀 `pretrain report:`。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 🆕 运维指令 · 2026-10-18 16:4x（✅ 更正：#548 是误判，训练未死——**不要重启**）· 运维 sudo 实测

> **实测**：`.29` **PID 2597555 从 10-17 08:44 一直存活**（etimes ~115000s）；GPU **8×100%/51763 MiB**；`/tmp/baize_xmodel25_decay_v2_train.log` 当前 **step 9630/19980（48.2%）**，loss 1.3255，lr 1.61e-4，298.8K tok/s，**0 error**。
> **#548 误判根因**：它读的 `$OUTPUT_DIR/baize_xmodel25_decay_v2_train.log` 是 **`.12` 旧 run** 的日志（10-17 10:45 SIGTERM traceback），不是 `.29` 的实时日志。
> **判活规则（立即生效）**：先 `pgrep -af torchrun` + `nvidia-smi` + **`tail /tmp/baize_xmodel25_decay_v2_train.log` 看 step 是否增长**；**NFS `$OUTPUT_DIR/...train.log` 不能作为判据**（那是 `.12` 旧日志）。
> **本块覆盖 16:2x 的“立即 resume”**：训练活着 ⇒ **不要重启/不要 resume**。只有确认 `torchrun` 消失 + GPU 空闲 + `/tmp` log 停止增长，才按 16:2x 的长期规则 resume。

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
> ⚠️ **作用域**：旧块（12:0x / 10-18② / 其它）里的「不重启 / 不碰训练 / 等运维裁定」只适用于各自任务；**训练已死时一律按本块 resume**。

- 以后唤醒先查训练：`pgrep -af torchrun`、`nvidia-smi`、train_log 尾部。
- **训练进程消失 / 崩溃 / 被杀** ⇒ 自查日志 → 选最新有效 `step_*` ckpt → **立即 `--resume` 重启**，不需要逐次等运维许可。
- 仅以下情况停手报 blocker：① 没有任何有效 ckpt；② 同一原因 1h 内连续崩 ≥2 次；③ 硬件/磁盘/网络错误明确；④ 重启命令本身失败。
- 仍禁止：kill 健康训练、改配方/数据、动别的线。

> 📦 §2026-10-18 12:0x（P0 修复 .29 ops 中继）+ 2026-10-18②（v5 中文 HTML + 数据前置实测）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：中继已修复闭环（PID1972249 存活、.last_run_id 123→125）；v5 三交付物（HTML+PLAN_V5_STABLE_1.5T.md+PLAN_V5_DATA_PREREQ.md）均 committed，分词实测 474K/375K tok/s·0.343 tok/B·2.31T·16并发≈1天·开工~10-20。需要时再读。


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

