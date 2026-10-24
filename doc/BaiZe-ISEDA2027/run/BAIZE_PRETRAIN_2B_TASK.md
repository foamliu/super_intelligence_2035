# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🚀 运维令 · 2026-10-24 23:5x（**双机已调通 ⇒ 转入「双机吞吐优化」阶段**）· 用户直令 · 最高优先
> **已调通（23:22–23:37，16 卡 DP=2×8，`baize_dualnode_16gpu_test.sh`）**：median **512,801 tok/s** / mean 508,860 / **扩展效率 84.0%** / 每卡 32,050 / 峰值显存 **64.4 GB** / loss 0.3695 / gnorm 0.72 / **0 NaN、0 skip**；NCCL 走 `NET/IB/0,2,6…` 多通道。
> ⚠️ **口径陷阱**：这次是 **BF16 mixed + `--mock` 数据**，而单机基线 305,098 是 **FP8 tensorwise + CUDA Graphs + 真数据** ⇒ 84% 只能证明"IB 健康"，**不能**直接当扩展效率结论。
> ⚠️ **launcher bug**：`baize_dualnode_16gpu_test.sh:114/115  WORKER_SSH_PID: unbound variable`（`set -u` 下 worker 收尾即报错，导致脚本"挂在 SSH 清理"）→ **先修**（`WORKER_SSH_PID=${WORKER_SSH_PID:-}`，或在 worker 分支前置空）。
>
> **优化任务（按序执行，每项固定 80 步；每次跑完立刻释放 16 卡）**
> - **A. 口径对齐（必做第一步）**：16 卡跑 **e18 配方（MBS3 + FP8 TW + CUDA Graphs + 真数据）** ⇒ 得到与 305K 可比的真实扩展效率（预期 ~0.84）；同时留 BF16 组作对照。
> - **B. NCCL/IB 调参**（每项单独跑）：`NCCL_IB_QPS_PER_CONNECTION` 1/4/8 · `NCCL_MAX_NCHANNELS` 32/64 · `NCCL_ALGO`(Ring/Tree)×`NCCL_PROTO`(LL/LL128/Simple) · `NCCL_NET_GDR_LEVEL` 2/3 · `NCCL_IB_HCA` 子集（**排除 `.29` 的 `mlx5_7`/`mlx5_15` 两个 PORT_DOWN**）· `NCCL_CROSS_NIC=1`
> - **C. 通信/计算重叠**：`--overlap-grad-reduce` / `--overlap-param-gather`（DP=16、TP=1 下是否有收益）
> - **D. MBS/GBS**：MBS3→**4**（64.4 GB 尚有 ~15 GB 余量）· GBS 1008→2016
> - **E. 分布式优化器**：`--use-distributed-optimizer`（用显存换更大 MBS）
> **判据**：每项报 `tok/s`、`扩展效率`、`median step ms`、`峰值显存`、`loss/gnorm`（与 e18 对齐，Δloss ≤5%）；最优组合写进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新节「双机吞吐优化」+ 中文 HTML 报告 `reports/report_pretrain_dualnode_throughput_zh.html`（含每项对比表与结论）。
> 🚫 不得改单机 e18 配方本身；🚫 不要再用 mock 数据下的数字对外宣称"扩展效率"。


> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。
> 📦 §运维实测·2026-10-24 21:45（2-rank NCCL打通）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：4个NCCL IB变量(GID_INDEX=3/MTU=4096/TC=106/TIMEOUT=22)必须照抄主从两侧,busbw≈46GB/s。需要时再读。

> 📦 §运维令·2026-10-24 21:0x（NCCL卡在worker初始化）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：最小复现2rank打出Init COMPLETE,锁RoCE环境变量缺失。需要时再读。

> 📦 §应急令·2026-10-24 19:2x（loop卡死29h重启）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：loop已重启,16卡双机测试已执行。需要时再读。

> 📦 §运维指令·2026-10-24 16:2x（双机16卡联合训练测最大吞吐）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：双机16卡e18=606K tok/s,扩展效率99.4%(已纠正#767误报512K/84%)。需要时再读。

> 📦 §补正·2026-10-24 16:2x（SGLang对Mamba2支持已验证）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：sglang 0.5.9原生支持nemotron_h,照抄P-9.11配置,加--mamba-ssm-dtype float32。需要时再读。
### 🚀 运维指令 · 2026-10-24 16:0x（**① 305K 最佳实践写入任务书 ② longctx 报告用错模型：重测重写**）· 用户直令 · 最高优先

> 用户原话：「1. 把第二轮最佳：**MBS3+FP8 TW+CG=305K tok/s（+2.6% vs 第一轮 / +21.0% vs 基线）**作为**最佳实践简要写入任务书**；2. 早上提交的 `report_pretrain_longctx_infer_cost_3x2b_zh.html` **有问题，BaiZe-2B 不应该采用 Xmodel-2.5 模型，而是应该沿用一直实验的 BaiZe-2B (Mamba2-hybrid）模型。重新测试，重写报告。**」

---

**① 最佳实践（写入本任务书「💡 最佳实践 / 硬口径」区，常驻）**

> **BaiZe-2B 训练吞吐最佳配置（2026-10-24 第二轮定档，勿再重复扫描）**
> - **配置**：`MBS3 + FP8 tensorwise + CUDA Graphs`（即 e18）
> - **吞吐**：**305K tok/s**
>   - **+2.6%** vs 第一轮最佳 e09（297K）
>   - **+21.0%** vs 基线 252K / **+22.5%** vs 历史 249K
> - **关键机理**：FP8 tensorwise **单独用反而 -10%**（Mamba2 SSM 小 GEMM 的量化 kernel launch 开销 > 计算节省）；**必须叠加 CUDA Graphs** 让量化 kernel 被图捕获，FP8 带宽收益才释放。
> - **显存**：MBS3 下需确认峰值；80GB 内已知可行。
> - **上限已确认 = 305K**（5 条依据闭合：VRAM / 计算（GPU 100%）/ 通信（NCCL 无收益）/ 软件栈（compile 崩溃）/ FP8 blockwise 驱动级阻塞）。
> - **CUDA 12.9 不可用**：驱动 570.195.03 最高支持 12.8，12.9 需驱动 ≥575 → **驱动级 BLOCKED**（即使新建 conda env 也不行），升级需 root。
> - 🚫 后续全量预训练**直接用 e18 配置**，不必再扫吞吐。

---

**② longctx 报告重测重写（核心问题）**

**问题定位（运营方已核实报告内容）**：当前报告的"BaiZe-2B"写的是：
```
BaiZe-2B ~1.35B
架构 LlamaForCausalLM (由 XmodelForCausalLM 转换)   ← ❌ 错
层数 48 / hidden 1536 / 24 heads / GQA 8 KV / vocab 129,280 / 权重共享
来源 自有模型 decay-5000 (Xmodel-2.5-code)          ← ❌ 错
```
**这是 Xmodel-2.5 的 Dense 架构（decay 后转换），不是 BaiZe-2B。**

**BaiZe-2B 的真实规格**（必须以此为准）：
- **架构：Mamba2-hybrid**（56 层 = 28 SSM + 28 Attention，hidden=2048，heads=16，**真实参数量 2.220B**）
  - ⚠️ **口径订正（历史遗留错误）**：**不是 3.00B**。`3.00B` 来自 mcore 打印 `transformer layers 2.47 + embedding 0.53`，该打印**对 Mamba/hybrid 误把 56 层全按 full attention+MLP 计**。真实值以 `sum(numel())` = **2,220,268,032 = 2.220B** 为准（见 `EXPERIMENTS_2B.md` L7、`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` L79）。
  - **对比参照**：MiniCPM5-2B 实测 **2.512B**（transformer 1.98B + embedding 0.53B，tie=False 双嵌入）⇒ **BaiZe 反而更小**（2.220B < 2.512B）。**报告中若做对比，必须写"BaiZe 参数量更小的前提下达到/超过"**，这是加分点，不要写反。
- **不是 Dense Transformer，不是 XmodelForCausalLM**
- 模型路径请从 Baize-ISEDA2027 里**实际训好的 BaiZe-2B 权重**取（`nemo_experiments/` 下与 pretrain_launcher `--arch mamba2` 对应的产物）

**重测要求**
1. **确认模型**：加载前打印 `arch` / 层类型统计（SSM vs Attention 层数）/ 参数量，**贴在报告里**，证明是 Mamba2-hybrid。
2. **SGLang 支持性核查**：Mamba2-hybrid 在 SGLang 0.5.9 下是否有专门支持（mamba backend / `--mamba-ssm-dtype`）？**若需特定 flag 或版本，先报再测**；若确实不支持，如实写"该架构在 SGLang 下不可服务"而不是拿 Dense 模型顶替。
3. **三模型同口径重测**：BaiZe-2B(Mamba2-hybrid) / MiniCPM5-2B / Qwen3.5-2B，**同样的上下文阶梯 64K→2M、同样的测量协议**（1 预热 + 2 次取中位、生成 128 tok、`--disable-radix-cache`、mem-fraction 0.88）。
4. **关键对比维度（Mamba2 的意义就在这）**：
   - **KV cache 增长曲线**：Mamba2 只有 Attention 层有 KV（28/56 层），**显存增长应显著慢于 Dense**
   - **TTFT / Decode 吞吐随上下文的退化斜率**
   - **能服务的最大上下文**（谁先 OOM）
5. **必须加一节"架构差异说明"**：讲清 Mamba2-hybrid 的 SSM 层是**常数状态**（不随上下文增长），这是它与 Dense 在长上下文成本上的**结构性差异**——这正是本报告的价值所在。

**③ 交付**
- 重写 `reports/report_pretrain_longctx_infer_cost_3x2b_zh.html`（**覆盖旧版，旧版先备份为 `.bak`**）
- 报告中**必须写明**："旧版误用 Xmodel-2.5 Dense ckpt，本版改用 BaiZe-2B (Mamba2-hybrid) 重测"
- 数据可溯源：每个数字对应 `logs/` 或 `/tmp` 中的原始测量文件
- commit 前缀 `pretrain report:`

**④ 纪律**
- 🚫 不再扫吞吐（305K 已定档）
- 🚫 不动 vision（`.12`）/ 不改 5 源分词产物
- ✅ 每轮落 MEMORY + daily



> 📦 §运维令·2026-10-24 09:3x（放行继续优化吞吐）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：R2c完成,e18=305K定档,7/7建议闭合。需要时再读。

> 📦 §运维指令·2026-10-23 22:1x（优化吞吐>249K）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：10/10候选完成,297K→305K新纪录,HTML报告已交付。需要时再读。

> 📦 §运维指令·2026-10-23（长上下文推理成本评测3模型）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：Qwen3.5-2B独享1M上下文最快,HTML报告已交付。需要时再读。

> 📦 §运维指令·2026-10-23（decay修复中文HTML报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：decay-5000官方μP+Muon修复,CS8=58.97%,报告已交付。需要时再读。

> 📦 §运维指令·2026-10-22 13:5x（decay 5000步+MBS5排障）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：decay=5000步,MBS5+recompute排障,官方1113.sh口径。需要时再读。

> 📦 §运维指令·2026-10-22 08:5x（decay参考官方1113.sh+20B）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：参考官方train_decay_fp8_1113.sh,20B数据,5560步。需要时再读。
> 📦 §2026-10-09:3x（写两份中文 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：两份报告已交付（v2_result + short_experiment, commit c44ef1fea）。需要时再读。

> 📦 §2026-10-02:3x（授权自主排查根因）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：L1 CS8=59.03% / L2 kill@step2370 / L3 作废，方向转 A方案官方 Megatron。需要时再读。

> 📦 §2026-10-21:5x（decay v2 对照口径纠错）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：v2 CS8=44.97% vs 官方 65.40% Δ−20.43pp，起点 61.03%⇒decay 训坏。需要时再读。

> 📦 §2026-10-14:2x（评测 decay v2 final）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：14集eval CS8=44.97%/CX6=6.21%，报告已交付。需要时再读。

> 📦 §2026-10-06:1x（事故复盘报告）已归档 → run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论**：crash@02:45 NCCL timeout→resume step_18000→收尾，P0-a/b 已落地，硬件=transient。需要时再读。

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

