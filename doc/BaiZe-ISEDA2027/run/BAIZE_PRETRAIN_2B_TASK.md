# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_PRETRAIN_2B.md` / `daily-memories/` / `EXPERIMENTS_*`）。本节为「无」时按下方 Round 2 默认顺序推进。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_PRETRAIN.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。


### 🆕 运维指令 · 2026-10-06（🔭 **B1 的 ctx 曲线扩到 256K / 512K / 1M** ＋ 判定「下一个瓶颈是谁」）· 高优先

> **用户追问（2026-10-06）**：「**ctx 可以继续扩张吗？128k → 256k → 512k → 1M**」。你 B1 步骤 1 已证明 **128K 能跑通（正确尺寸 prompt → HTTP200，3.79s）** ⇒ 请把 **B1 步骤 2/3 的 ctx 档位从 `{4K…128K}` 扩到含 `256K / 512K / 1M`**，并回答「**再往上谁先顶不住**」。
>
> **要做**：
> 1. **逐档实测（免训练优先）**：ctx ∈ {4K, 8K, 16K, 32K, 64K, 128K, **256K, 512K, 1M**} —— 每档报 **HTTP 可跑性 / TTFT / prefill 时间 / 峰值显存 / PPL（或 passkey 检索）**；⚠️ **prompt 一律用 tokenizer 精确计数**（别再踩 128K 那个构造 bug）。
> 2. **判定「下一个瓶颈」——分三类，逐档给数**：
>    - **(a) RoPE 外推质量**：只影响 **4 层 attention**；**24 层 SSM 无位置编码 ⇒ 无位置 OOD**。⇒ 给出「**质量开始明显掉**」的 ctx 拐点。
>    - **(b) KV cache / 显存**：只随 **4 层**线性增长（对比稠密 56 层全 KV）⇒ 给出「**哪一档开始触顶/OOM**」。
>    - **(c) 那 4 层 attention 的 O(n²)**：SSM 是 O(n)，但 attention 部分在极长 ctx 下可能**反超为主导** ⇒ 给「**attention 占 prefill 的比例随 ctx 上升**」的曲线。**若 (c) 先顶住** ⇒ **架构级对策 = 把这 4 层改成局部窗口/sliding 或 NoPE**（**属 P-8 启动前才可定的议题**，先只做**可行性判断 + 成本**，🚫 不动架构）。
> 3. **对齐真实需求（别为 1M 而 1M）**：**先量「agentic EDA 到底要多长」** —— 可参考 **ZhuLong 评测里的轨迹 token 长度分布**、或 **harness 侧 SWE-bench 的上下文长度** ⇒ 给出「**目标 ctx 应该是多少**」的建议。
> 4. **产出**：并入 `report_pretrain_hybrid_longctx_advantage.html` 新增一节「**可扩展到多长**」（含 1M 档结论 + 瓶颈归属 (a)/(b)/(c)）。
>
> 🚫 铁律不变：不占 GPU2-7、不改 P-5b recipe、不存 ckpt、🚫 绝不 kill watchdog；时间盒内做不完**如实写卡点**。


### 🆕 运维指令 · 2026-10-06（⭐⭐ **【长上下文：B 扩展 + hybrid 优势论证】** —— 为 **P-8 正式训练申请足量资源**供弹药）· 高优先

> **用户口径（2026-10-06）**：「把**长上下文场景下 Mamba2-hybrid 相对于 MiniCPM5 的优势谈清楚**，这样**有利于为 P-8 正式训练申请足量资源**。」
> **已核准的配置事实（据此出发）**：HF 转换写出的 `nemotron_h` config **只有 `max_position_embeddings=4096`，没有 `rope_theta`/`rope_scaling`**（⇒ 走 transformers 默认 **rope_theta=1e4**）；而**对照 MiniCPM5-2B 是 `rope_theta=5e6` + `max_position_embeddings=131072`** ⇒ **基线天生为长上下文配置，我们不是**。而 P-9.11 的 128K 失败（e2e≈0.5s、`total_completion_tokens=0`、**非 OOM/非超时**）= **被拒**（4K/16K/64K 均成功）。

> **A. 把已批准的「B（长上下文 4096→8192+）」扩成三步（仍在原预算：1 卡 · ~2–3h；铁律不变）**
> - **B1（~1h · 免训练诊断 · 先做）**：
>   1. **先查 128K 的"拒绝原因"**（sglang 日志 + 直接构造 128K 请求看**返回体**；核 `--max-total-tokens`、KV+mamba-state 容量核算、后端对该模型的 ctx 校验）→ **如实贴原文**；
>   2. 改 HF config：**`max_position_embeddings` → 131072**；**`rope_theta` 1e4 → 5e5/1e6（ABF，对齐基线量级）**；可选加 `rope_scaling`（**PI / dynamic-NTK / YaRN** 三选）。⚠️ **每次只改一个变量**；
>   3. 跑 **ctx ∈ {4K, 8K, 16K, 32K, 64K, 128K}** 的 **PPL + passkey/needle 检索 + 8 集 eval** → **出退化曲线**；
>   4. **判据**：8 集降幅 **<10%** 且 PPL 不炸 ⇒ 该长度"免训练可用"。**每个数字都必须标清 config/栈**。
> - **B2（~2–3h · 条件触发）**：若 B1 显示 **≥16K 明显退化** ⇒ 做**阶梯式长度扩展续训（4K→8K→16K，每档 0.5–2B token）**。⭐ **只有 4 层 attention 吃 RoPE（24 层 SSM 无位置编码）⇒ 待适应面小、应收敛很快** —— 请把**实际收敛速度**记下来（**这本身就是 hybrid 优势的量化证据**）。
> - **B3（0 成本 · 决策输入）**：整理成**给 P-8 seq 的决策答案**：「**P-8 的 seq 定 4096 / 8192 / 还是 decay 段升 8192–16384？**」并给**成本差**（decay 段 token 占比小 ⇒ 升长几乎免费）。⚠️ **必须在 P-8 启动前定案，否则 P-8 作废。**

> **B. ⭐ 交付 `report_pretrain_hybrid_longctx_advantage.html`** —— 面向资源申请的**一页摘要**（自包含）
> 📌 **已有运维侧草稿可作底稿**：`doc/BaiZe-ISEDA2027/report_hybrid_longctx_case.html`（已含：三笔账 / 劣势与边界 / config 事实对比 / 中英双语可引用措辞 / **出处与口径表**）—— **请在其基础上用 B1 实测数据刷新数字，不要从零重写**。
> **必须含**：
> 1. **三笔账（按 ctx 画曲线，ctx ∈ {4K,16K,32K,64K,128K}）**：
>    - **prefill / TTFT**：SSM **O(n)** vs attention **O(n²)** ⇒ 已测 **3.7×–23×**（P-9.10③ 自定义 benchmark，4K→128K 递增）· **2.18×@64K**（P-9.11 sglang 生产栈）· **3.6×@128K**（P-9.10② eager 下界）—— **请补 B1 之后口径统一的一组**；
>    - **显存 / KV（决定"能不能服务"）**：已测 **0.22×–0.44×**（128K×bs1：**13 GB vs 61 GB**），且 **dense 在 128K×bs8 直接 OOM**；
>    - **每 token 缓存搬运**：hybrid **5.1× 更低**（P-9.10② H3：cache 18.2× 但 per-token 更低）。
> 2. **如实写劣势与边界（不许夸大）**：
>    - **decode 吞吐**：短 ctx 下 **dense 快 1.2–1.6×**（transformers KV cache 优化）；**sglang 生产栈 1.18×@64K、crossover ≈50K** ⇒ 请给出「**ctx ≥ X 时 hybrid 反超/持平**」的边界；
>    - **训练吞吐 −8%**（P-7 真值）—— ⚠️ **论文原写的 −24% 是跨节点 artifact，不得再引用**；
>    - **未测项（如 1M ctx）一律标"未测/外推"**，不许当结论。
> 3. **一句话可引用结论（模板，用你们实测数替换）**：
>    > 「在 128K×bs1 下，**2.22B Mamba2-hybrid 只用 0.22× 显存完成 prefill；2.512B 稠密基线在 bs8/128K 直接 OOM**。prefill 优势随 ctx 从 4K 的 3.7× 拉到 128K 的 23×；代价仅为训练吞吐 **−8%**。」
> 4. **与 P-8 资源申请的挂钩段（1 段）**：**"给 P-8 足量资源（100B token / ~12.5 天 / 8×H100）产出的，是一个在 agentic EDA 的 32K–128K 场景下 prefill 快数倍、显存省 2–4 倍、且比稠密基线少 11.6% 参数的 2.2B 模型"** ⇒ 正是「**harness 解决后，小模型也能顶用**」的降本论据。
> 5. **口径纪律**：所有数字标 **栈（mcore eager / 自定义 / sglang）+ 后端 + bs + mem-fraction + config**；**不许混口径**；未实测的标来源或标「待测」。

> **C. 与「提速令」的关系**：本块与 Step 2 提速**并行不冲突**（都只用 GPU0-1）。**顺序建议**：**B1（~1h）→ 提速清单 → B2（若需要）→ A（复杂推理 6 集）→ D（P-9.11 缺口）**。


### 🆕 运维指令 · 2026-10-06（⭐ **【裁决 + 提速令】** 批准 **A/B/D**；**C 暂不动 / E 不做**；**当前主线 = 用 GPU0-1 优化训练配置、争取提速**）· **最高优先**

> **一、对你「空窗提案」的裁决（用户 2026-10-06）**
> - ✅ **批准 A（复杂推理 6 集）**：按你写的方案执行（GPU0 · 1 卡 · ≤6h 时间盒）→ 产出 `report_pretrain_complex6_scaling.html`。
> - ✅ **批准 B（长上下文 4096→8192+）**：执行（GPU0 · 1 卡 · ≤4h）→ 产出 `report_pretrain_longctx.html`。⚠️ 你自己指出的"RoPE 只影响 4 层 attention ⇒ 收益可能有限"**要实测检验，不得预设结论**。
> - ✅ **批准 D（P-9.11 缺口补测：128K + H3 sglang）**：执行（GPU0 · 1 卡 · ≤2h）。
> - ⏸ **C（P-8 dry-run）＝ 暂不动**（用户：「**P-8 暂时不动**」）⇒ 🚫 不要启动。
> - 🚫 **E（ckpt → OpenAI 兼容服务 + 接 Cline harness）＝ 不做**（用户：「**现在模型能力太弱，距离能作为 harness 底模还很远**」）⇒ 本阶段**不投入**；将来若要，由运维点名。
>
> **二、⭐ 当前最高优先 =【提速】：用 GPU0-1 优化训练配置、争取提速**（用户原话：「pretrain 当前的重要任务，还是用这两张卡优化训练配置，争取提速」）
> **第 1 步（你已点名的假设，必须实测证伪/证实）——NCCL / NVLink 拓扑核查**（源自 `report_pretrain_p95_profiler.html`）：
> - **假设（用户提出）**：若当前 **NCCL 实际走的是 PCIe P2P（而非 NVLink）**，换成更好的 **NVLink 拓扑**会有改善。
> - **必须取证**：① `nvidia-smi topo -m`（PIX/PXB/PHB/**NV#** 矩阵）；② `nvidia-smi nvlink -s` / `-c`（链路 UP？速率？）；③ **`NCCL_DEBUG=INFO` 真跑一次**（抓 `Channel…via P2P/IPC/NVLS`、`via NET`、`P2P is enabled/disabled`、`NVLS` 是否启用）；④ **`nccl-tests` 的 `all_reduce_perf`**（若无该工具，就用你自己的 DP2/DP8 微基准）量 **busbw**。
> - **对照实验（每次只改一个变量）**：`NCCL_P2P_DISABLE` · `NCCL_P2P_LEVEL` · `NCCL_TOPO_FILE`（自定义拓扑）· `NCCL_IB_DISABLE` · `NCCL_SHM_DISABLE` · `NCCL_ALGO`（ring/tree）· `NCCL_PROTO` · **NVLS/`NCCL_NVLS_ENABLE`** —— 各测 **busbw + 端到端 tok/s**。
> - **判据（必须给）**：① **当前实际通道构成**（NVLink / P2P / NET 各占几成）② **最佳 env 组合** ③ **相对 baseline 的 tok/s 提升 %** ④ **该提升能否迁移到 8 卡**（对照 **P-9.7 的 249K tok/s** 基线）。
> - **产出**：`report_pretrain_nccl_topo.html`（自包含：topo 矩阵 + NCCL 日志关键行原文 + busbw 表 + tok/s 表 + 结论）。
> **第 2 步 —— 训练提速候选清单**（都用 GPU0-1 可实测）：MBS/GBS/seq 组合 · `--recompute` 档位 · CUDA-graph/静态形状 · 数据管线（`num_workers`/预取/阻塞点）· TP/DP 拓扑 · kernel/backend 选择（TE、attention backend）· 以及 **P-9.7「249K tok/s」口径复核**。
> - **每条给**：实测 **tok/s** + **判据** + **是否可迁移 8 卡** + **时间盒**。
> - **优先「不改 recipe、只改运行时/并行/IO」的项**（这类最可能迁移到 P-8 且不污染既有结论）；**凡涉及改 recipe 的，先报提案再动**。
> **建议顺序**：① NCCL 拓扑核查（~1h）→ ② 提速清单（挑 2–3 条最可能见效的）→ ③ A → B → D（纯推理，可插空）。
>
> **三、纪律（不变）**
> - 🚫 **不占 GPU2-7**（data 配比 BO，ETA ~16:00）；🚫 **不启动 P-8**；🚫 不改 P-5b 已定稿 recipe、不回训、不囤无关 ckpt；🚫 **绝不 kill watchdog loop**。
> - 每项都有 **时间盒 + 判据 + 可否中断**；产出写进 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` + HTML，并按「收尾铁律」commit + push。
> - 做不了/做不完 ⇒ **如实写"卡点 + 需要什么"，不许凑数**。


### 🆕 运维指令 · 2026-10-06（⭐ **【空窗提案】P-8 未启动期间，请你自己提一份"可用 GPU0–1"的实验提案**）· 高优先 · **本轮只交提案，未批准不得启动**

> **背景**：P-8 本体因两个前置（① base 全量未齐 ② 配比未定稿）**暂缓** ⇒ **`.29` 的 GPU0–1 目前空转**，而你已连续多轮（#128–#133）只做"状态核查"。用户要求：**由你**（最熟悉既有脚本/ckpt/数据/交付物的人）提出**空窗期可做的实验**——运维不替你想。
>
> **交付格式**：**3–5 条候选**，每条一小节，**必须**含：
> ① **一句话目标**（回答什么科学/工程问题）；
> ② **占卡与墙钟**（1 卡 / 2 卡；预计小时；**不得占用 GPU2–7** —— 那是 data 的配比 BO，ETA ~17:00）；
> ③ **可复用的既有资产**（脚本 / ckpt / 数据 / HTML，**给绝对路径**，如 `nemo_experiments/p3_hybrid/hf_iter_5000/`、`data/p5b_l3/p5b_l3_train_s*`）；
> ④ **产出物**（报告节 / HTML / 表 + 落盘路径）；
> ⑤ **与 P-8 前置的关系**（"解 P-8 的前置" / "与 P-8 并行不冲突" / "纯论文补强"）；
> ⑥ **成本与风险**（GPU·h、失败模式、**时间盒**、可否中断）。
> **另附一行**：**你的推荐排序 + 理由**（为什么第 1 条最值）。
>
> **候选方向（供参考，不强制；你若认为不合适，请写明理由）**：
> 1. ⭐ **长上下文适配 4096 → 8192+**：README 风险表 **#3 🔴**「4096 对 agentic 轨迹过短」是 **(ii) SFT/RL 的前置硬约束**；且 **P-9.11② 的 128K 格 failed（`max_pos=4096`）** 正指向这里。可评估 RoPE/NTK/YaRN 扩展或短程长 ctx 续训 + 8K 零样本评测。
> 2. ⭐ **ckpt → OpenAI 兼容推理服务 + 接入 Cline harness**（README 待办）：P-9.11 只做到"起服 + 测矩阵"，**"接 harness"未做**；这是论文**推理成本卖点**的落地证据。
> 3. **P-9.11 缺口补测**：128K 格 failed；H3 在 sglang 下被 `--mem-fraction-static 0.85` 预分配掩盖。
> 4. **复杂推理 6 集**（GSM8K/MATH/BBH/MMLU/HE/MBPP）：任务书 §(3)(4) 要求"常识 8 集 **+ 复杂 6 集**"两条曲线，**目前只见常识 8 集** ⇒ 请**确认是否做过**；没做就补（任务书已预告"很可能贴地板，量出来本身就是结论"）。
> 5. **P-8 dry-run（预演）**：用 GPU0–1 跑 1–2B token 的 WSD 小预演，验 P-8 的启动脚本 / **FP8 delayed** 配置 / ckpt 与磁盘清理策略 → 给 12.5 天长跑降风险。
>
> **纪律**：
> - 🚫 **本块只要"提案"**：写进 `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`（新增「空窗提案」节）**或** `MEMORY_PRETRAIN_2B.md`，然后 git commit+push；**未经运维批准，不得启动任何训练/长跑**。
> - 🚫 **不占 GPU2–7**；🚫 不改 P-5b recipe、不回训、不囤无关 ckpt；🚫 **绝不 kill watchdog loop**。
> - **P-8 状态不变**：仍暂缓（前置未齐前不启动，见下方 P-8 节）。
> - 每条提案都要有**判据**（怎么算成功/失败）+ **时间盒** + **可否中断**。

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

