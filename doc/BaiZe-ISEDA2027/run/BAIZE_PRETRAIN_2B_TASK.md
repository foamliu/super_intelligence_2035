# BAIZE_PRETRAIN_2B_TASK.md

> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块任务是否**已产出交付物并 commit** 或运维已标「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档完立即回到运维指令区，从最上面那条**未完成**指令开始做。
> 3. **禁止**「只归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 60 秒后再唤醒），直到交付。
> 4. 心跳里必须写这一句：`未完成指令：<有/无>`；有 ⇒ `WAITING: 0` 且本轮内完成。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### [运维令] 2026-10-25 20:2x（seq 4096->8192 掉速 5.6x 的根因排查：补对照 + 时间分解 + web search 对标）· 用户直令 · 最高优先
> 用户原话：「让 pretrain 排查一下为啥 seq 从 4096 翻到 8192 吞吐掉这么多，也可以web search，这个不符合常识，因为阿里等公司用8192预训练还是常见的，而且我们又是Memba2-hybrid，理应对长上下文更加友好。」
> 现状（实测）：cfg1（seq8192 / 2M tok/step）**108,291 tok/s** vs 基线（seq4096 / 4.13M）**606,449 tok/s**；per-GPU 6,768 vs 37,900（-82%）；峰值显存 79.2 vs 67.6 GB。
> 运维判定：**该降幅不符合常识** —— BaiZe-2B 只有 4/56 层带 attention、24 层 Mamba2（线性于 seq）、28 层纯 MLP；同 tok/step 下 seq 翻倍的合理代价约 **+10~30%**。**证据不齐前，禁止把「Mamba2 SSM 超线性」写进报告/MEMORY 结论**（MEMORY #779 已有此句，本轮改为「推测·待验证」）。

**1) 先补对照（现在的网格不是单变量：GBS 1008->256、MBS 3->2 一起变了）**
- `cfg0a`：seq=4096 / S1 / mbs=4 / gbs=512（tok/step=2,097,152，与 cfg1 **只差 seq**）
- `cfg0b`：seq=4096 / S2 / mbs=3 / gbs=1008（tok/step=4,128,768，**用同一脚本重跑基线**）
- 判据：`tok/s(cfg0a) / tok/s(cfg1)`；`tok/s(cfg0b) / 606,449`。若 cfg0b 偏差 >5% ⇒ **先查环境/脚本差异**（CUDA graph、fp8、NCCL 变量、数据 blend、launcher 参数），不得继续谈 seq。

**2) 时间分解（归因核心证据，每格都要）**
- 开 Megatron 计时（`--log-timers-to-tensorboard --timing-log-level 2` 或等价），取 step 30-80 的 `forward-compute / backward-compute / optimizer / data-loading` 均值。
- 每格采一次 `nvidia-smi dmon -s u -m -c 60`：GPU util 均值、util <10% 的时间占比。
- 查 CUDA graph 是否真生效（log 里 capture 成功/失败、是否回退 eager），4096 与 8192 对比。
- 查数据侧：seq=8192 时每步读几个 shard、是否跨 shard 重打包、worker 数 / CPU 饱和 / 队列空转；与 4096 用同 16 个 `p5b_l3` shard 对比。
- 查 kernel/精度：`--mamba-ssm-dtype` 实际取值（recipe 内是否强制 float32）、chunk_size、sequence parallel / TP 在 8192 下是否被关、TE/fused kernel 是否回退。

**3) web search 对标（用户点名，必须真检索并引用）**
- 检索方向：Qwen2.5 / Qwen3 预训练序列长度与吞吐；Llama 3（8K 预训练）；Megatron-LM 长序列最佳实践（sequence parallel / context parallel / activation recompute）；`mamba_ssm` 与 Megatron-Core hybrid Mamba 的已知性能坑（chunk scan、fp32 state、TP 下 scan 切分）；「同 tok/step 下 seq 翻倍的合理吞吐损失区间」。
- 每条写：来源（标题 + arXiv 号 / 官方文档 / 博客 + 年份 + **检索日期 2026-10-25**）、结论、与本项目可比性；**查不到就写「未查到」**，不许凭印象。

**4) 假设-检验表（报告必须逐行给实测结果）**
| 假设 | 检验方式 | 若成立的特征 | 实测 | 结论 |
|:--|:--|:--|:--|:--|
| H1 数据管线在 8192 下重打包/跨 shard，GPU 饥饿 | data-loading 计时 + util 曲线 | data-loading 占步时 >50%，util 长期 <20% | | |
| H2 CUDA graph 在 8192 回退 | log capture 行 | 出现 fallback / capture failed | | |
| H3 Mamba2 fp32 SSM + chunk scan 长序列低效 | 改 chunk_size / 临时 bf16 对比（标为配方变更组） | 改后 tok/s 明显回升 | | |
| H4 小 GBS/MBS 导致 overlap 与利用率下降 | cfg0a 对照 | 4096 也掉到 ~110K ⇒ 与 seq 无关 | | |
| H5 8K 本身计算更贵 | 排除 H1-H4 后 | compute 占比接近 100% 且随 seq 增长 | | |

**5) 修复与复测**
- 定位主因后**只改那一项**（如 seq 粒度预打包 / 加 dataloader worker / mamba dtype / 恢复 CUDA graph），用同一 `cfg0a` 复测，给修复前后 tok/s、step time、显存对比。
- 判据：修复后 `cfg0a` 相对基线同 tok/step 的降幅 **≤30%**；若仍 >50% ⇒ 保留现场证据上报，不许硬编结论。

**6) 交付**
- `reports/report_pretrain_seq8192_slowdown_rootcause_zh.html`（中文 HTML 自包含、0 `<script>` / 0 外链、≥15KB）：摘要 / 现象与口径 / 对照实验 / 时间分解与 util / 假设检验表 / 外部对标 / 根因 / 修复与复测 / 复现命令 / 数据溯源。
- 更新 `reports/report_pretrain_seqlen_throughput_zh.html` 与 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新节；生成器 `run/gen_seq8192_rootcause_report.py`（重跑 diff 空）。
- 修正 MEMORY #779 机制结论标注；commit 前缀 `pretrain rc:`。
- **排期调整（20:5x 运维追加，优先级高于主表）**：`cfg3` 跑完后**先插 `cfg0a` + `cfg0b`**（两个合计约 20 分钟：cfg0a 3.5s/step x80 + 起停，cfg0b 6.8s/step x80 + 起停），**再续 cfg4-cfg6**。做法：cfg3 结束、`release_gpus` 返回后，SIGTERM 编排器 `baize_seqlen_grid_test.sh`（只杀编排进程，不碰 torchrun 子进程——此刻应已退出），把 `CONFIGS` 改成 `cfg0a cfg0b cfg4 cfg5 cfg6`，重新 `setsid` 起；若来不及在 cfg4 启动前拦住，就等 6 格全跑完立刻补跑，**不许省这一步**。
- **模块级 profile（H6/H7 的唯一判据）**：在 `cfg0a`（4096）与 `cfg1`（8192，可重跑 10 步）上各用 torch profiler / Nsight 采 10 步，输出 `attention / ssm(chunk scan) / mlp / loss / optimizer / data` 六类的时间占比与绝对毫秒；判据：若 `attention` 占比随 seq 平方增长 ⇒ H6 成立；若 `ssm` 绝对耗时随 seq 明显超线性 ⇒ H7 成立；两者都不成立再看 data。
- 总 ETA 相应调整：cfg3 ~21:10 -> cfg0a/cfg0b ~21:40 -> cfg4-cfg6 ~22:40 -> profile + 修复复测 ~23:40 -> 报告次日 00:30 前。

**补充观测（20:40，cfg2/cfg3 出来后，归因更清楚了）**
| cfg | seq | tok/step | tok/s | per-GPU | 相对基线(606,449) |
|:--|--:|--:|--:|--:|--:|
| 基线 e18 | 4096 | 4.13M | 606,449 | 37,903 | 1.00x |
| cfg1 | 8192 | 2.10M | 108,291 | 6,768 | -82% |
| cfg2 | 8192 | 4.19M | 111,897 | 6,993 | -82% |
| cfg3（在跑） | 16384 | 2.10M | ~62,000（step 33.81s 折算） | ~3,875 | -90% |
- **同 seq 下把 tok/step 翻倍，tok/s 只 +3%** ⇒ 吞吐被某个与批大小无关的固定项卡住；
- **seq 再翻倍，tok/s 再近减半** ⇒ 该项随 seq 超线性增长（4096->8192 掉 5.5x，8192->16384 再掉 1.8x，拟合约 seq^1.6）。
- 结论：**不是「小 GBS/MBS 的 overlap 问题」（H4 基本可排除），也不是纯数据饥饿**（数据饥饿不会随 seq 超线性）；最可能是**与 seq 相关的算子路径变慢**（4 层 attention 的 O(seq^2) 或 Mamba2 SSD chunk scan 的 fp32 路径），或**该路径下 kernel/attention backend 回退**。必须用 profile 定位到模块级。

**追加假设**
| H6 | 4 层 attention 在 seq>=8192 走了非 flash/未融合路径（O(seq^2) 主导） | torch profiler / Nsight 按模块取时间占比；查 attention backend 与 flash 可用性日志 | attention 模块占比随 seq 平方增长 | | |
| H7 Mamba2 SSD chunk scan 在长 seq 下走 fp32 逐 chunk 扫描（非融合） | 对比 `chunk_size` 与 dtype；查是否命中 PyTorch 2026-02 所述「五算子融合」前的慢路径（该博文实测融合可提速 1.50-2.51x） | 改 chunk/融合后 tok/s 明显回升 | | |

### [运维令] 2026-10-25 17:5x（**seq 增大 x 每步 token 数固定（2M / 4M）的 16 卡吞吐网格**）· 用户直令 · 最高优先
> 用户原话：「pretrain：测试下列配置的16卡训练吞吐 1）seq=8192, 2M tok/step 2）seq=8192, 4M tok/step 3）seq=16384, 2M tok/step 4）seq=16384, 4M tok/step 5）seq=32768, 2M tok/step 6）seq=32768, 4M tok/step 也就是在每步训练数据量不变（2M/4M,对应S1和S2）的情况下，看看增大seq对训练吞吐的影响。」

**1) 网格（唯一变量 = seq；同组内 tok/step 与数据配比不变）**
| # | seq | tok/step | GBS(seq) | DP16 每卡 seq/步 | MBS x 累积 建议 | 备注 |
|:--|--:|--:|--:|--:|:--|:--|
| 1 | 8192 | 2,097,152 | 256 | 16 | 2x8 或 4x4 | S1 组 |
| 2 | 8192 | 4,194,304 | 512 | 32 | 2x16 或 4x8 | S2 组，约等于基线 tok/step |
| 3 | 16384 | 2,097,152 | 128 | 8 | 1x8 | S1 组 |
| 4 | 16384 | 4,194,304 | 256 | 16 | 1x16 | S2 组 |
| 5 | 32768 | 2,097,152 | 64 | 4 | 1x4 | S1 组 |
| 6 | 32768 | 4,194,304 | 128 | 8 | 1x8 | S2 组 |

- GBS 必须整除 DP16；`tok/step = GBS x seq` 必须**逐项核对等于表内值**（256x8192=2,097,152 等）。
- 配方冻结：**DP16 / TP1 / PP1 + FP8 tensorwise + CUDA Graphs + 真数据**（与双机 e18 同口径）；Mamba2 侧沿用 `--mamba-ssm-dtype float32`。**除 seq 与随之变化的 MBS / 累积外，一律不许改**。
- 数据：**2M 组用 S1 配比、4M 组用 S2 配比**；同组 3 个 seq 必须来自**同一条 token 流**（同一批 packed shard，仅切块长度不同），并把打包命令写进报告，证明单变量。
- 基线参考行（不计入 6 格，单独标注）：seq=4096 / 4,128,768 tok/step / DP16 e18 = **606,300 tok/s**（`/tmp/baize_dualnode_16gpu/`）。

**2) 测法（与既有口径一致）**
- 每配置 `ITERS=80`；取 **step 30-80 的 median step time**（6 点，与双机 e18 同规则）。
- 必报：`tok/s`（主指标，= tok/step 除以 median step 秒）、`step/s`、median step ms、per-GPU tok/s、峰值显存（GB）、loss、gnorm、NaN 计数。
- 每组内派生：**每翻倍 seq 的吞吐损失百分比**（vs 同组 seq=8192），并列「2M 与 4M 的绝对吞吐差」。
- **OOM 处理**：只许两种回退，且必须**标为「配方变更组」单列、不混进主表**：(a) MBS 降到 1、用累积补回 tok/step；(b) 加 `--recompute-activations` 或 `--use-distributed-optimizer`。仍 OOM 就把该格写「OOM（峰值显存 xx GB，卡 x）」+ 已试过的回退，**不许留空、不许编造**。
- 每格跑完立刻释放 16 卡（`nvidia-smi` 全 0 MiB 再起下一格）；**不许为写报告保占**。

**3) 结论要求（报告的落点）**
- 主表 6 行全填；再给「tok/s 随 seq 变化」双曲线（2M / 4M 各一条，同图）。
- 机制解释**必须带实测支撑**：seq 变大则激活 / 显存变大、MBS 被迫变小、每步通信 / 调度占比变化；BaiZe-2B 是 **Mamba2-hybrid（24 SSM + 4 Attn + 28 MLP-only，只有 4/56 层带 KV）**，注意力成本结构性低于纯 Transformer，此点**须用本网格数据印证，未验证就标「推测·未验证」**。
- 给 **S1 / S2 该选多大 seq** 的可执行结论（若 seq 增大导致吞吐降幅大于 10%，明确建议维持 4096 / 8192 并说明理由）。
- 预计机时：单格 80 步 x (2-25 s) + 起停约 5 min，**6 格合计 2-5h**；先跑第 1 格标定，再回写总 ETA。

**4) 产出**
- `reports/report_pretrain_seqlen_throughput_zh.html`（中文 HTML 自包含、0 `<script>` / 0 外链、不低于 15KB）
- 生成器 `run/gen_seqlen_throughput_report.py`（数据字典写脚本顶部，重生成 `diff` 必须为空）
- `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新节「seq 长度 x tok/step 吞吐网格」+ MEMORY 首部新块 + daily；commit 前缀 `pretrain seqlen:`（只 add 本次动的文件）。

**铁律**
- 不用 mock 数据出主表；配方变更组不许混进主表；报告禁 N/A / 空单元格（OOM 也写清原因）。
- 不动单机 e18 与双机 e18 的既有结论 / 日志；新实验日志进 `/tmp/baize_seqlen_grid/<cfg>/`。

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

