# BAIZE_POSTTRAIN_TASK.md

> 🔴 **用户直令 · 2026-11-14 19:2x — 「3.04% → 15.82%」≈5× 跳升归因 + prompt 迭代（最高优先，压过例行巡检）**
>
> **用户原话**：「请 posttrain 分析一下这 ≈5 倍跳升从何而来。既然 MCP 工具一样，难道差异仅仅来自于系统 PROMPT 的差异吗？如果系统 PROMPT 差异这么大，那么看看 trace，是否还能继续优化系统 PROMPT 来提分？」
>
> **完整规格 → `run/POSTTRAIN_ENV_ATTRIBUTION_SPEC.md`（先读完再动手）**。要点：
> 1. **前提纠正**：3.04%（.17）与 15.82%（36.15 run1）之间同时变了 4 件事（系统提示 / RAG 后端 / 沙盒可达性 / 网络延迟），**不许**把 5× 直接归给 prompt。
> 2. **任务 A（先做）**：单变量消融 A0–A3，40 题分层子集，出「prompt 占多少 / 反馈回路占多少 / RAG 占多少」。
> 3. **任务 B**：用 **36.15 的 trace**（不是旧环境）做失败分型 → 三条最小补丁 P1/P2/P3（退化提交 / submit 风暴 / 检索不落地）→ **train/dev 79/79 分离**，一次只加一条，dev ≥+3pp 且 submit 报错率降 ≥10pp 才晋级，最后 test 上 5-run + McNemar。
> 4. 🚫 不改 benchmark / 不改 check.py / 不挑题 / 不引用未跑完的 run；每步落 `EXPERIMENTS_POSTTRAIN.md`，报告用中文 HTML，commit 前缀 `posttrain attribution:`。
> 5. ⚠️ **体积**：本任务书已 ≈42KB（>40KB 硬上限）⇒ 下轮**先**把已闭合块滚入 `ARCHIVE_EXPERIMENTS_POSTTRAIN.md` 再执行本令；本条令不得被归档。

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）（本线现有：`reports/report_posttrain_research_zh.html`）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔴 用户令 · 2026-11-14 16:3x（**基于 trace 重写 RCA 报告**：工具调用 1.9 万次为何仍只有 3.04%）· 未完成 · 最高优先

> **用户原话**：「post-train：MiniCPM5-2B 调用了工具这么多次为啥通过率还这么低呢？让 post-train 基于这个 trace 重写 RCA 文档（中文 HTML）。最后 RCA 文档末尾提出提分意见。」

**一、用户提的问题就是报告的主线**

你自己实测的 trace 统计：`search_apis` 4,418 + `search_apis_by_keyword` 2,060 + `get_api_details` 5,436 + `run_code` 1,460 + `run_commands` 6,401 ≈ **19,775 次工具调用**，而 Pass@1 仅 **3.04%**。

> **两者之间的巨大落差，就是这份 RCA 必须解释清楚的核心问题。**
> 「有工具」已经不是问题；要回答的是：**工具用了这么多，为什么还是不通过？**

**二、重写要求（不是修补旧报告，是重写）**

产出**新的**中文 HTML 报告（旧报告保留作历史，顶部加指针说明已被本报告取代）：

`reports/report_posttrain_pyaether_rca_v2_zh.html`

**必含章节**：

1. **口径与数据（可复算）**
   - 基线 ckpt、serve 配置、数据集 md5、trace 根路径、扫描命令；
   - 5-run 通过数、Pass@1 mean±std。

2. **工具调用画像（这是新增的核心章节）**
   - 各工具调用次数、**成功率/失败率**（tool_result 里有无 error）；
   - **每题平均调用次数**、调用次数的分布（是不是少数题疯狂调用、多数题不调）；
   - **调用后是否有"有效结果"**：例如 `search_apis` 返回 sim=0.9375 的高分文档，模型**后续有没有真的用上那个 API**；
   - 有无**重复调用同一 API / 死循环重试**的迹象（占多少题）。

3. **失败归因（自行从 trace 提炼，不预设分类）**

   重点回答这几个**具体**问题（能答就给数字，答不了标 TODO）：
   - **检索到 ≠ 用对**：`get_api_details` 拿到了正确文档，后续生成的代码里有没有出现该 API？还是用了别的（错的）API？
   - **写得出 ≠ 跑得通**：`run_code` 报 `SyntaxError` / `Code contains non-ASCII` 各占多少题？这些题最后有没有修好？
   - **跑得通 ≠ 判得过**：代码执行成功但 check 判 fail 的，占多少？失败在哪个断言？
   - **迭代次数**：`run_commands` 6401 次里，多少是有效迭代、多少是原地打转？
   - **prompt 矛盾的影响**：`.17` 用的 `eval_sys_prompt_template_no_sandbox.md` 明写「本场景无沙箱可实际执行，内部推演唯一校验」，但 agent 仍调用 `run_code` 1,460 次 —— 这种**指令与环境自相矛盾**对模型行为的影响，请在 trace 里找证据（例如模型是否表现出"不敢信执行结果"、是否反复推演）。

4. **图表**：工具调用分布 / 失败漏斗（检索→用对→跑通→判过）/ 各类占比，**内联 SVG，单文件自包含，0 外链 0 script**。

5. **【报告末尾】提分意见（用户明确要求）**

   按 **ROI 排序**给具体可执行的建议，每条写清：
   - **改什么**（数据 / prompt / 工具 schema / 训练 / 评测环境）
   - **依据**（对应上面哪类失败、多少题、trace 证据）
   - **预期收益**（保守估计 + 理由）
   - **成本**（人时 / 机时）
   - **优先级 P0/P1/P2**

   最后给一句 **「如果只做一件事，做哪件」**。

**三、纪律**

- 所有数字**可复算**（路径 + 命令），取不到标 `TODO`；
- 🚫 不许编造 trace 原文；
- 🚫 不要用「模型能力不行」这类空话收尾 —— 必须落到「哪一步断掉了」；
- 报告落 `reports/`，中文、单文件、0 外链、0 script。

---

### 🔴 用户令 · 2026-11-14 16:1x（**看 3.04% 那次 run 的 trace，判定是否有正确的工具调用**）· 未完成 · 最高优先

> **用户原话**：「现在有两种意见：
> 意见A：3.04% 使用了正确的 API 文档检索工具和沙盒
> 意见B：3.04% **没有** 使用正确的 API 文档检索工具和沙盒
> 让 post-train 看看 3.04% 这次 run 的 trace，看看有没有正确的工具调用，有没有正确的结果不就知道了吗？」

**一、要你做什么（用 trace 实证，不要推理）**

去 3.04% 那 5 个 run 的**原始 trace** 里，**逐条统计工具调用**，用事实回答 A/B 之争。

**必须统计的三类事实**（每条都要给出计数 + trace 路径 + 原文摘引）：

1. **API 文档检索工具**是否被调用、调用是否成功：
   - 工具名（你评测配置里 pyAether MCP 的 `search_apis` / `get_api_details` 等，按实际名）
   - **调用次数** / **成功次数** / **失败次数**
   - 失败时的错误原文（如 `NoSuchToolError` / 403 / 超时 / 工具不存在）
   - 若**从未调用**：说明是模型没想到调、还是工具没挂在工具列表里（这两种含义完全不同）

2. **沙盒执行工具**（`run_code` 等）是否被调用、结果如何：
   - 调用次数 / 成功次数 / 失败次数
   - 典型成功返回（例如 `2+2=4` 之类的真实回显）
   - 典型失败返回（连接失败 / 端口不通 / 403 / 超时）
   - 沙盒端口/隧道相关错误原文

3. **是否存在"工具根本没注册"的证据**：
   - trace 里的工具列表快照（system prompt / tools schema 里到底有几个工具、名字是什么）
   - 与 **zhulong 在 36.15 上跑时的工具列表**做对比（可直接问 zhulong 要它的口径）

**二、判定输出（必须二选一，给硬证据）**

在 MEMORY 心跳里用一行给出结论：

```
3.04% trace 判定: [A 有正确工具调用 | B 没有] · 依据: search_apis 调用 n 次/成功 m 次 · run_code 调用 x 次/成功 y 次 · 工具表 z 个
```

- 若 **A**：说明 3.04% 是有效基线，A5 可省；但仍需给出"隧道 vs 直连"的差异说明。
- 若 **B**：说明 3.04% **无效**，须立即在 RCA 报告顶部标「作废 + 原因」，并按方案文档的阶段 A 重做。
- 若**证据不足**（trace 缺失/损坏/只有 stdout 无 tool_calls）：写 `证据不足 + 缺什么`，🚫 不许硬猜。

**三、范围与纪律**

- 只读 trace，**不重跑评测**（本轮只做判定）。
- 统计要能复算：给出你的扫描命令 + trace 根路径。
- 🚫 不许用"应该/大概/可能"下结论；A/B 之争只认 trace 里的原始记录。

---

### 🔴 用户令 · 2026-11-14 15:4x（**PyAether 评测必须在 36.15 上启动，不是 .17** —— 你的 3.04% 基线口径存疑）· 未完成 · 最高优先

> **用户原话**：「通过阅读报告 `report_posttrain_baseline_pyaether_rca_zh.html` 我发现了问题：
> EDA-Eval-PyAether-v20260311_fixed.jsonl 评测 cline agent 是在 .17 服务器（跟 post-train 相同）启动的吧，这样不对。
> 需要跟 zhulong agent 一样，从 36.15 服务器启动。因为只有 36.15 服务器才：1）部署了 API 文档知识库（RAG）服务；
> 2）部署了可以访问沙盒（EDA 环境）的 MCP。所以需要跟 zhulong agent 协调：
> 1）先 serve minicpm5-2b；2）从 36.15 通过隧道打通到 .17 的大模型调用通道；3）zhulong agent 对于如何启动评测非常熟悉。」

**一、这意味着什么（先想清楚再动手）**

- 若基线评测确实在 **.17** 启动，那么 agent **拿不到 RAG（API 文档知识库）**、**也拿不到沙盒 MCP（EDA 环境）**。
- ⇒ **3.04% 这个数不能代表"模型能力"**：它是在缺少工具与知识库的环境下测的，属于**环境缺失**，不是能力上限。
- ⇒ 你已交付的 RCA 报告（`report_posttrain_baseline_pyaether_rca_zh.html`）里的**失败分类与 fix 方案，全部建立在错误口径上**，必须重新评估。
- ⚠️ **不要**把这个当作"模型就是不行"的结论；也**不要**急着重写 RCA —— 先按下面把评测环境修对、重测，再谈归因。

**二、要做的事（与 zhulong 协调，三步）**

1. **serve minicpm5-2b**：在 36.15 上起模型服务（复用你已有的 serve 脚本口径，注意 36.15 路径前缀是 `/nasdata/` 而非 `/nas_train/`）。
2. **打通隧道**：从 36.15 通过 ssh 隧道，把**模型调用通道**暴露给 .17（或反之，按实际调用方向确定；你是被测端，模型端点要可达）。
3. **学 zhulong 的启动方式**：zhulong 的评测 `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`（36.15），
   它的 RAG 服务在 `:9006`、沙盒 MCP 在 `:18891`、沙盒端口 `8650-8654`。
   **请直接向 zhulong 要它的启动命令与环境变量口径**（`RAG_RECALL_URL` / `PROXY_PORTS` / `SANDBOX_ENDPOINTS`），照抄复用，不要自己另造一套。

**三、协作方式（我已下发）**

- 我已通过 zhulong 的 ops 中继下发 **RUN_ID 144**：`doc/ZhuLong_DAC2027/run/ops/inbox.md`
  —— 内容 = 在 36.15 上体检 RAG/MCP/沙盒端口/GPU/现有 serve/.17 隧道/SFT ckpt 路径/eda_fastmcp 启动脚本与环境变量口径。
- **你看它的结果**：`doc/ZhuLong_DAC2027/run/ops/outbox.md` 搜 `RUN_ID 144`，拿到实测现状后按它给的路径起跑。
- 你也可以在本线 MEMORY 写一行协作请求，但**不要改 zhulong 的文件**。

**四、判据**

- 重测后给出**新基线**（同 158 题、同判据），并**明确标注两次评测的环境差异**：
  `旧 = .17 无 RAG/无 MCP` vs `新 = 36.15 有 RAG + 有 MCP + 沙盒可达`。
- **旧 RCA 报告的处置**：在报告顶部加一个显著声明，注明「本次分析基于 .17 环境，缺 RAG/MCP，结论仅作参考；
  `新口径见 <新报告>`」。🚫 不许悄悄保留旧结论当定论。
- 若新基线与 3.04% 差异很大，**如实写**——那说明旧数字是环境问题，这是重要发现，不是失误。

---

### 🔴 用户令 · 2026-11-14 09:0x（**暂停 RL，改为分析 MiniCPM5-2B 基线在 EDA-Eval-PyAether(158) 的 3.04% 与 trace**）· 未完成 · 最高优先

> **用户原话**：「post-train 先花时间分析基线 MiniCPM5-2B 在 EDA-Eval-PyAether（158）跑出的 3.04% 的结果和 trace，暂时不忙做 RL。把失败逐个统计和归因，绘制饼图和表格，挨个类别提出 fix 方案。先给出这份中文 HTML 报告来。」

> ⚠️ **归类方式由你定**：失败分成哪几类，**由你基于 158 题的实际情况（结果 + trace 原文）自行提炼**，不要套用任何预设分类表。下发方不预设类别、不预设数量。

- **暂停**：不再起新 RL 轮次/调参/写 RL 论证；5-run eval 链不 kill（自动跑、结果照常归档），R2 负信号暂不处置。
- **唯一交付物**：一份中文 HTML 报告，落 `reports/report_posttrain_baseline_pyaether_rca_zh.html`（单文件自包含、0 外链、0 script、图表用内联 SVG）。
- **必须包含**：
  1. 基线口径（哪个 ckpt / serve 配置）+ **158 题逐题结果**，pass 数用原始文件核对（与 3.04% 对账）；
  2. **失败逐个统计与归因**：类别由你提炼，每个类别给题数、占比、**trace 原文摘引 + 文件路径**；
  3. **饼图 + 表格**；
  4. **逐类别 fix 方案**：根因 → 具体改动点 → 预期提升（说明依据）→ 成本 → 优先级，最后给"先做哪几件"的排序；
  5. 结论：3.04% 主要卡在哪一层。
- **纪律**：所有数字可复算（路径 + 命令）；取不到就标 `TODO`，🚫 不许估、不许编 trace 原文。
- **完成后** MEMORY 心跳一行写结论。

---


### 🔴 用户令 · 2026-11-12（**L4 领域评测改由 post-train 主责**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「既然后训练说『隧道第 4 次复验 OK』，那么 Pretrain 说的 L4 BLOCKED 就不成立了。这件事 Pretrain 不要管，由 Post-Train 负责。」

**背景**：R331 已实测 `ssh -p 3333 app.e0031982@localhost` → TUNNEL_OK（hfeg0tedaap02 = 10.251.36.15），`run_code` 端到端 PASS（2+2=4，py3.9.0）。即 pretrain 报的「.15/.17 SSH 不通 ⇒ L4 BLOCKED」在你这套隧道方案下**不成立**。

**立即执行**（与现有 post-SFT eval 主线并行，不得因此停 SFT eval）：

1. **L4 定义**：① zhulong 消融评测（EDA-Eval-PyAether 158 题，cline harness，`model` 可配）；② designflow（EDA-LiveFlow-Bench，`cline_eval/`，61 任务）。
2. **先出基线**：选 1 个已导出的 BaiZe ckpt（优先 170k/180k HF 目录），经隧道在 36.15 起 OpenAI-compatible 服务（vLLM/SGLang/llama-server 三选一，按可用性），用两个 bench 的 `--model` 指过去，各跑**最小可跑子集**（zhulong 先 5–10 题、designflow 先 5 个任务）→ 出基线数 + 复现命令。
3. **再扩到全量**：最小子集 PASS 后，zhulong 158 题；designflow 按其 README 全量。记录 Pass@1、耗时、失败分类（infra vs 能力）。
4. **落盘**：`MEMORY_POSTTRAIN.md` 关键事实段写清「隧道→36.15→EDA 环境→bench 启动」的实际命令链；结果进 `EXPERIMENTS_POSTTRAIN.md` 与对应报告；勿把凭证写进仓库/日志。
5. **对 pretrain**：L4 数字由你产出后，pretrain 只读引用；不要再让 pretrain 碰 .15/.17。

**边界**：不改变 Phase1/Phase2/Phase3 主线优先级；L4 是并行交付项，出数即可，不为追分改 benchmark 协议。

---


### 🔴 用户令 · 2026-11-12 11:2x（**沙盒隧道已启动——只用它 SSH 到 36.15 以访问 EDA 环境**）· 用户直令 · 最高优先 · 未完成

> **用户原话（第二轮，覆盖上一号令的细节）**：「沙盒隧道已启动，只要求它使用隧道 SSH 到 36.15，以进一步访问 EDA 环境即可。」

**立即执行**（本轮首要任务；上一号令「自行建立隧道」之细节作废，隧道**已由外部启动好**）：

1. **先读**本机 `.17` 上的 `cat /nas_data/app.e0031982/code/dual-nix-tunnel/README.md`，理解如何使用这条**已就绪的隧道**（ssh 命令、端口/跳板参数、认证方式）。
2. **通过隧道 SSH 到 36.15**（即 `10.251.36.15`，ZhuLong 那台），验证 `ssh` 可达并能登录。
3. 在 36.15 上**进一步访问 EDA 环境**（pyAether Python+SWIG / Virtuoso SKILL 沙盒），用最小用例实测 `run_code` 端到端可达。
4. 把实际可用的连通方式（走哪条 ssh 隧道、目标主机/端口）**更新进** `eda_fastmcp .env`、`MEMORY_POSTTRAIN.md` 关键事实段、以及本任务书隧道说明；替换旧的 `SANDBOX_HOST=10.129.32.75:8664/8665/8653/8669` 失效通路。
5. 隧道打通后，回到 2026-11-10 计划主线：**拆 GPU5/6/7 占位 serve → 用 v11v38 语料重训 SFT → 评测验证 data gap coverage 改善 → baseline eval 5-run → RL R1-R4 起跑**。
6. 凭证/密钥路径一律存仓库外、不入库不入日志（沿用「secret 不入库」纪律）。
7. 完成后在 MEMORY_POSTTRAIN.md 报告：SSH 36.15 是否真正可达（附探测输出证据）、EDA 访问是否通、连通配置落盘位置、下一步动作，保持 `WAITING=0` 继续主线。

---

### 🔴 用户令 · 2026-11-10 17:10（**sandbox 未通前用 serve 占住 GPU5-7，防止被挪用**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「既然阻塞（隧道未通），让post-train先随便起一些长任务把后三卡占用起来（比如也serve MiniCPM5，否则被挪用）。」

**立即执行**：
1. 在 GPU 5/6/7 上各启动一个 vLLM serve MiniCPM5-2B（复用已有 venv 和配置），端口分别 8097/8096/8095。
2. 命令模板（直接跑）：
```bash
CUDA_VISIBLE_DEVICES=<N> HF_HOME=/tmp/hf_home TRANSFORMERS_CACHE=/tmp/hf_home HF_MODULES_CACHE=/tmp/hf_home/modules \
  nohup /tmp/vllm_venv/bin/python -m vllm.entrypoints.openai.api_server \
  --model /nas_data/app.e0031982/models/MiniCPM5-2B \
  --served-model-name minicpm5-2b-gpu<N> --host 0.0.0.0 --port <PORT> \
  --trust-remote-code --gpu-memory-utilization 0.85 --max-model-len 32768 \
  > /tmp/vllm_gpu<N>.log 2>&1 &
```
3. 启动后验证：`curl -s http://localhost:<PORT>/v1/models` 有响应 + `nvidia-smi -i <N>` 显存占用 ~37GB。
4. **注意**：transformers 必须是 4.49（不是 5.x），否则 tokenizer 报错。如果 `import transformers; print(transformers.__version__)` 不是 4.49，先 `uv pip install --python /tmp/vllm_venv/bin/python "transformers>=4.45,<4.50"` 降级再启动。
5. **注意**：启动前先 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv -i <N>` 确认 GPU 无残留进程，有则 `kill -9` 清理。
6. 占住后在 MEMORY_POSTTRAIN.md 记录端口映射表，并保持 WAITING=0 继续做其它可做的事（归档 EXPERIMENTS、准备 SFT 脚本等）。

---

### 🔴 用户令 · 2026-11-10 13:40（**GPU 4-7 已到位，三阶段替身计划启动**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「后四卡已腾出。GPU4 serve MiniCPM5-2B，GPU5 serve Qwen3.5-2B，GPU6-7训练。Qwen3.5-2B先不铺了，剩下的卡用于训练。」

#### 0. 当前 GPU 状态（2026-11-10 实测）

| GPU | 用途 | 状态 |
|:--:|:--|:--|
| 0-3 | root SGLang Qwen3.8-27B（:8099） | 占用中，不可动 |
| **4** | **vLLM serve MiniCPM5-2B（:8098）** | ✅ 已启动，正常响应 |
| 5 | 空闲→**按 17:10 令占住** | 待 serve |
| **6-7** | 空闲→**按 17:10 令占住** | 待 serve |

- vLLM venv：`/tmp/vllm_venv/bin/python`（vLLM 0.7.3 + torch 2.5.1 + CUDA 12.4）
- 环境变量：`HF_HOME=/tmp/hf_home HF_MODULES_CACHE=/tmp/hf_home/modules`
- 驱动限制：NVIDIA 550.54.14 → CUDA 12.4 max（不能用 cu128/cu130）
- 模型路径：`/nas_data/app.e0031982/models/{MiniCPM5-2B,Qwen3.5-2B,gemma-4-E2B-it,Llama-3.2-3B-Instruct}`
- ⚠️ **transformers 版本**：必须 4.49.x；agent 若之前升到 5.x 需降回来（`uv pip install --python /tmp/vllm_venv/bin/python "transformers>=4.45,<4.50"`）

#### 1. Phase 1：基线评测（立即开始，仅用 GPU4 评测 + GPU0-3 的 Qwen3.8-27B）

**目标**：用 EDA-Eval 158 任务，同口径横评三个模型，5-run mean±std。

| 模型 | 端点 | 评测方式 |
|:--|:--|:--|
| MiniCPM5-2B | `http://localhost:8098` (vLLM, GPU4) | cline auth → EDA-Eval harness |
| Qwen3.8-27B | `http://localhost:8099` (root SGLang, GPU0-3) | cline auth → EDA-Eval harness |
| DeepSeek（云端） | `http://agi-gateway.cxmt.com/cloud/v1` (glm-5.2 替身) | 已有 P0 诊断数据 |

- 每模型 5-run，报 mean±std + 配对检验
- 采集真实失败轨迹，**用实测替换 P0 D1-D6 的假设值**
- anti-cheat 全程开，报 cheat rate
- 158 任务污染隔离闸门必须 PASS
- 评测协议冻结，不改

**交付物**：`reports/report_posttrain_baseline_3model_zh.html`（里程碑报告，非 rXXXX）

#### 2. Phase 2：替身 SFT 端到端验证（Phase 1 完成后立即开始，GPU6-7 训练 + GPU4 评测）

- 模型：MiniCPM5-2B（2B, Llama 架构, Apache 2.0）作 BaiZe 替身
- 数据：UltraData-SFT-2605 子集（已在 `.29`/`.12` NFS 分词镜像）
- 脚本：`baize_posttrain_anneal.sh` → `baize_posttrain_sft.sh`
- A40 显存约束：48GB/卡，2B SFT 用 2 卡 TP=2 或 DP=2，batch/seq 按 R92 校准配方
- SFT 前后跑 EDA-Eval 评测，验证 SFT recipe 是否提分
- 报告显著标注「替身预演，收益不可迁移到 BaiZe」

**交付物**：`reports/report_posttrain_sft_surrogate_zh.html`

#### 3. Phase 3：替身 RL/GRPO 端到端验证（Phase 2 SFT ckpt 完成后开始，GPU4-7 全部投入）

- 取 Phase 2 SFT ckpt → `baize_posttrain_rl_grpo.sh`
- 激活 R130-R143 设计的 6 个 hook
- 吞吐预估 666 R/hr → ~3000 步约 2-3 天
- 验证：GRPO 是否在 EDA-Eval 上产生正向增益、hook 系统是否稳定
- 报告显著标注「替身预演，收益不可迁移到 BaiZe」

**交付物**：`reports/report_posttrain_rl_surrogate_zh.html`

#### 4. 执行纪律

- GPU4 的 vLLM serve 是**常驻服务**，不要 kill
- Phase 1 和 Phase 2 可以**并行**：GPU4 评测的同时 GPU6-7 跑 SFT
- 训练脚本用 `--dry-run` 先验证再正式跑
- CUDA 限制：只能用 cu124，不能装 cu128/cu130 的包
- vLLM venv 在 `/tmp`（本地磁盘），重启机器后会丢——需要时重建
- 🚫 不碰 GPU 0-3（root 的 SGLang）
- commit 前缀：`posttrain eval:` / `posttrain sft:` / `posttrain rl:`

---

### 📦 §用户令·2026-11-07 10:10（GPU 11/9 到位是既定安排，不要再问；等待期继续深入调研）· ✅ 已闭合 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：R1-R143 调研全完成（EDA交互RL方案/造题/奖励设计/失败模式/GRPO超参/rollout调度/verl hooks），GPU 11/9 已到位并启动 Phase 1。

> **用户原话**：「posttrain：不是说了11/9吗，还问啥。继续调研啊。」

#### 0. 口径澄清（一次性钉死，之后不得再问）

- `.17` 的 4 张 A40 于 **2026-11-09** 到位，这是**既定安排**，不需要用户再确认、不需要运维协调。
- 后续任何唤醒：🚫 **不得**再把「什么时候给 GPU」「是否现在腾卡」「要不要等 11/9」写成阻塞项或待用户决策。
- 正确做法：按 11/9 倒排准备，**到位当天自动起跑**（不等到下次唤醒再问）。

#### 1. 11-07 -> 11-09 的主任务 = 深入调研（不是例行巡检）

每轮唤醒必须至少产出**一项实质内容**并落盘，从下列任选（鼓励都做）：（🚨 注意：**不是每轮一份 HTML 报告**；HTML 按顶部「报告生成纪律」执行，日常产出写 EXPERIMENTS/MEMORY 即可）

| 编号 | 调研方向 | 必须回答的问题 |
|:--|:--|:--|
| R1 | **EDA 环境交互式 RL 的可执行方案** | 环境接口（SSH/双向隧道/本地 clone）如何稳定调用？奖励如何自动可判定？单题 rollout 预算？超时与部分失败的恢复策略？ |
| R2 | **PyAether 造题与难度分层** | 把 500 题模板扩展到可自动判定正确性的规模（目标 2k-5k）；难度标定方法（pass@8 profiling 还是规则分层）；每档题的区分度证据 |
| R3 | **奖励设计与 GRPO 稳定性** | 连续化/分档混合、省 GPU 的 group 配置、长度与格式作弊的抑制、KL 与 clip 的取值依据；失败模式（对照 vision 线离散奖励教训） |
| R4 | **35% 侧失败模式分类** | 从 MiniCPM5-2B 36% 基线出发，按 API 类别/错误类型（语法错、API 误用、逻辑错、超时、缺依赖）建分类法；等 GPU 后用真实轨迹校正 |

#### 2. 反空转条款

- 🚫 禁止「只写心跳 + 置 `WAITING: 1`」式空转。
- **连续两轮无新增调研产出 = 未完成任务**，必须 `WAITING: 0` 继续做。
- 每轮心跳必须写清：`本轮新增调研产出：<文件/章节/结论>`；没有就说明为什么。

#### 3. 交付物

1. 调研结论写入 `EXPERIMENTS_POSTTRAIN.md` 新节（或扩写既有节），带检索词与来源链接；
2. 需要时产出中文 HTML 报告到 `doc/BaiZe-ISEDA2027/reports/`（单文件自包含）；
3. 可执行脚本/配置/数据落 `run/`，须 `bash -n` / `--help` 可跑通；
4. commit 前缀 `posttrain research:` 或 `posttrain prep:`。

#### 4. 11/9 GPU 到位后的第一件事（预先写死）

1. `vllm serve /tmp/models/MiniCPM5-2B`（venv 已就绪）-> 复测 36% 基线（同口径 5-run）；
2. 采集真实失败轨迹，**用实测替换 R4 调研中的假设**；
3. 按 R1/R2/R3 结论起第一轮 EDA 交互式 RL（替身预演），报告显著标注「收益不可迁移到白泽」。

---


### 📦 §用户令·2026-11-07（替身模型 × EDA 交互式 RL 预演）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：L1.0 eda_fastmcp 本地克隆✅ + L1.1 API 分级(3276纯函数/1652副作用/3535不适用)✅ + L2 500题✅(0污染命中) + synth_rl_plan HTML✅ + Tunnel-SOP✅ + SFT-Verify✅(99.76G=75.87+23.89分词产物,.29/.12 NFS可达)。需要时再读。

---

### 📦 §用户令·2026-11-06 22:5x（后训练各阶段数据调研 + 本机硬盘体检）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`

> 交付：`reports/report_posttrain_stage_data_survey_zh.html`（45.4KB / 10 节 / 0 script / 0 外链）+ `EXPERIMENTS_POSTTRAIN.md` §E + 硬盘体检附节。**关键结论**：`/` 386G 可用(84%)、`/nas_data` 20T 可用(85%)，后训练全流程预估 200–300GB ⇒ **存储非瓶颈**；可清理候选 ≈4.7G（Qwen3.5-2B 4.3G 用途待确认）；`/nas_inference` 与 `/nas_env` 在 .17 **未挂载**。需要细节再读 archive。

### 🆕 2026-11-06 运维直令：建立 post-train 线 · 先做 P0 诊断 + 数据/方案预研（不启训练）

> 这是本线**第一条**指令。post-train 线**新建**，从零起步。
> ⚠️ **当前阶段（架构实验期末尾 → 正式训练前）**：pretrain S1 仍在 `.29` 跑（iter~101320/700000，ETA≈2026-12-25），**post-train 的正式训练依赖 pretrain 收敛 ckpt**。
> ⇒ **本线现在不启任何训练**，先做**零成本/低成本的准备 + 预研**，等 pretrain ckpt 就绪后再起。
> ⏱️ ISEDA 2027 投稿截止 ≈ 2027-02-01，倒推 post-train 正式训练窗口 ≈ **2026-12 下 → 2027-01 中**（约 3 周）。

**P0（本轮起，零 GPU，必须先做）—— §7.0 诊断清单 D1–D6**

> 出处：项目总纲 `README.md` §7.0。这六项**不花任何 GPU**，但直接决定 post-train 该往哪使劲。
> 数据来源：`~/eda_code_eval/*/final_report.json` 的 `details_per_task`（**数据已在手，无需重跑**）。
> 36% 是 MiniCPM5-2B 在 full harness 下已测的 Pass@1（与 94.0% 同口径）；58 pp 差距里有多少是「协议问题（可回收）」vs「真实能力差距」，全靠这六项判。

| # | 诊断项 | 判读 |
|:--|:--|:--|
| D1 | 工具调用合法率（格式合法 tool_call / 总数） | <90% → 协议问题，SFT 可大幅回收 |
| D2 | 工具调用频次（每任务平均调用次数，vs DeepSeek 的） | 显著偏低 → 模型不「用工具」、纯靠回忆 → SFT 可修 |
| D3 | 超上下文/截断比例 | 高 → 长上下文适配是 post-train 的前置项 |
| D4 | 失败类型分解（执行报错 vs 断言失败） | 报错多 → API/领域知识问题（SFT 领域语料）；断言失败多 → 语义推理问题（RL 价值更大） |
| D5 | per-scenario 通过率（Layout 64 / Schematic 47 / Design Mgmt 24 / Others 23） | 决定 SFT 数据的配比 |
| D6 | 平均迭代轮数（Φ）分布 | 显著低于 DeepSeek → 模型不会用执行反馈闭环 |

**交付**：
1. 从 `~/eda_code_eval/*/final_report.json` 提取 D1–D6 六项统计（MiniCPM5-2B 的那次 36% 运行；若有 DeepSeek 94% 的对照运行则一并列出做 diff）。
2. 若 `final_report.json` 字段不足以算某项，**如实标注「字段缺失」**并写明需要补抓什么；🚫 禁止编造。
3. 产出中文 HTML 报告 `reports/report_posttrain_diagnose_d1d6_zh.html`（自包含、0 script、0 外链、≥8 节：摘要 + 六项各一节 + 结论「58 pp 里多少是协议可回收」初步判断 + 对 post-train 三步的侧重建议）。
4. 同步把六项数值写进 `EXPERIMENTS_POSTTRAIN.md` §D（新建）。
5. commit 前缀 `posttrain diag:`。

**P1（P0 完成后，零/低 GPU，并行可做）—— 数据盘点 + 方案预研**

> post-train 正式训练需要的数据**部分已就绪**，部分需补。先盘清。

| 项 | 内容 | 现状（已知） |
|:--|:--|:--|
| P1-a | **SFT 通用指令集** `UltraData-SFT-2605`（319G / 1504 JSONL / 20.97B tok） | ✅ 已分词镜像（`DATA_MAPPING.md` L11） |
| P1-b | **SFT agentic 指令集** `UltraData-SFT-Agent-2609`（51G / 50 shard） | ✅ 已分词（`DATA_MAPPING.md` L12） |
| P1-c | **B 类 agentic 数据**（`to-tool-call-datasets`/`AgentTrove`/`Nemotron-Cascade-SFT-SWE`/`terminal-command-execution-sft` 等，落 `/nas_inference`） | ⏳ 已下载未分词（`DATA_MAPPING.md` §F） |
| P1-d | **PyAether 领域语料**（API 参考 / EDA 工具文档 / HDL 源码，供领域退火 + SFT 合成） | ⚠️ **待确认来源** —— `eda_fastmcp` 的 API 知识库能否导出为纯文本？见总纲 §9 待确认项 |
| P1-e | **EDA-Eval-PyAether 158 任务污染隔离规则**（§5.1 红线） | ⚠️ 必须在合成任何 PyAether 训练对之前定稿 |

**P1 交付**：
1. 盘点 P1-a~P1-c 的**实际可用性**（路径存在 / 字节数 / 是否已分词为 mcore 格式 / token 数），写成 `EXPERIMENTS_POSTTRAIN.md` §Data 表。
2. **P1-d 调研**：`eda_fastmcp` 的 API 知识库（`/nasdata/app.e0031982/code/eda_fastmcp`）能否导出为纯文本文档？能导出多少？格式？→ 写成 `EXPERIMENTS_POSTTRAIN.md` §PyAether-corpus 节 + 在报告里给「领域退火语料组装方案」（来源/配比/预估 token 数）。
3. **P1-e 污染隔离规则草案**：按 API 名 / 函数签名做隔离，确保 158 任务的答案与断言不泄漏；写出可执行的隔离脚本骨架（即使现在不跑，也要先把规则定下来）。🚨 这是红线，违反则整节作废（总纲 §5.1）。
4. 产出中文 HTML 报告 `reports/report_posttrain_data_inventory_zh.html`（自包含、≥10KB）。
5. commit 前缀 `posttrain data:`。

**P2（P1 完成后，零 GPU，纯设计）—— 三步训练方案书**

> 依据 P0 诊断 + P1 数据盘点，写 post-train 三步的**完整方案书**（不启训练，只设计）。

1. **领域退火**：复用 Stage(i) 的 WSD 机制；退火语料配比（通用/code/PyAether）、退火步数、与「仅 SFT」对照组的隔离设计（总纲 §4 Stage(ii) 步骤 0）。
2. **SFT**：数据混合（agentic / +code / +math / +PyAether API 语料）；CoT+工具轨迹 vs 纯代码；LoRA vs 全参；**上下文长度 4096 vs 8192 vs 16384**（总纲 §4 步骤 1，⚠️ agentic 轨迹极易超长，长上下文适配是前置项）。
3. **RL（核心）**：RLVR + GRPO；**奖励设计 4 臂**（R1 二值 / R2 部分分 / R3 R2+工具调用惩罚 / R4 R3+API 合法性，见 `5_llm_posttrain.tex` Table\ref{tab:reward}）；🚨 **Reward hacking 是最大风险** —— anti-cheat + 单独报告 cheat rate；⚠️ **预算口径换算**：带沙盒执行时是沙盒时延 bound，按「沙盒并发数 × 墙钟」规划，不沿用 GPU-hour（总纲 §4 步骤 2）。
4. **评测**：backbone × harness 网格（总纲 §4 步骤 3）；**预注册成功阶梯 M1–M4**（36%→50%→65%→75%→85%，先定后测，避免事后合理化，总纲 §4 步骤 4）。
5. **预注册判定阈值**：点估计 + 配对检验（McNemar / paired bootstrap）显著性 + 成本比 —— **必须先定后测**（总纲 §9 待确认项）。

**P2 交付**：中文 HTML 报告 `reports/report_posttrain_plan_zh.html`（自包含、≥15KB、覆盖三步 + 评测 + 成功阶梯 + 预注册阈值 + 时间线 + 风险）。
commit 前缀 `posttrain plan:`。

**P3（pretrain ckpt 就绪后，需 GPU，正式训练）—— ⬜ 等 pretrain 收敛**

> ⚠️ **依赖**：pretrain S1 ETA≈2026-12-25（iter 700000）。P3 在此之前**不启动**。
> P3 的具体子任务（退火起跑 / SFT 起跑 / RL 起跑 / 评测起跑）将在 pretrain ckpt 就绪后由运维另行下发。
> 现在只做：把 P0/P1/P2 的方案落实到「可执行脚本骨架」（不跑，只写好 `run/baize_posttrain_*.sh` 系列 + 配方文件），等 ckpt 一到即可起。

**P3 预备（本轮可做，零 GPU）**：
1. 参照 `baize_xmodel25_decay_v2.sh` / `baize_p8_train.sh` 的结构，写 `run/baize_posttrain_anneal.sh`（领域退火配方骨架，从 pretrain ckpt resume，换数据 blend）。
2. 写 `run/baize_posttrain_sft.sh`（SFT 配方骨架，从 anneal ckpt 或 pretrain ckpt 起）。
3. 写 `run/baize_posttrain_rl_grpo.sh`（RLVR+GRPO 配方骨架；奖励 4 臂用配置开关切换；沙盒并发参数化）。
4. 写 `run/baize_posttrain_eval.sh`（EDA-Eval-PyAether 评测脚本骨架，5-run、reshuffle、fresh context、2500s timeout，接入 OpenAI-compatible endpoint）。
5. 每个脚本写好后做**语法检查**（`bash -n`）+ **dry-run 打印配方**（不真跑），把输出贴进 `EXPERIMENTS_POSTTRAIN.md` §Scripts。
6. commit 前缀 `posttrain scaffold:`。

---

### 🧹 运维总则 · 2026-10-18（禁令作用域清理，沿用）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的「等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X」只在该块任务内有效；与最新用户令或最新任务块冲突时，以最新块为准。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）

> ⚠️ **红线（违反则整节作废，见总纲 §5）**：
> 1. **污染隔离**：EDA-Eval-PyAether 的 158 个任务（prompt + 函数签名 + 断言代码）**绝对不能进任何训练集**。允许用 API 参考文档合成训练对，但必须按 API 名/函数签名隔离，论文写明隔离规则。
> 2. **反作弊**：`PreToolUse` hook 全程启用，所有实验臂逐字一致；BaiZe 的 RL 也挂同一套 anti-cheat；必须报告 cheat rate。
> 3. **口径一致**：5-run mean ± std，不得报单次值；158 任务固定集上两系统比较优先用配对检验（McNemar / paired bootstrap）。
> 4. **评测协议冻结项不得改动**（总纲 §2）：158 任务 / Pass@1 / 2500s 超时 / 单 trace 原则 / 5 次独立运行 / `-p 8 -n`。

> 📋 **评测关键资产**（总纲 §3）：
> - 代码生成 driver：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh`
> - 评分：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py`
> - 158-case 数据集：`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`
> - `BASE_DIR`：`/nasdata/app.e0031982/code/eda_fastmcp`
> - BaiZe 接入：通过 vLLM/SGLang 暴露 OpenAI-compatible endpoint，`cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，换 backbone 成本≈0。

> 🎯 **成功阶梯（预注册 · 先定后测 · 总纲 §4 步骤 4）**：
> | 里程碑 | Pass@1 | 含义 | 先验判断 |
> |:--|:--|:--|:--|
> | 起点 | 36% | MiniCPM5-2B，通用模型，零适配 | ✅ 已实测 |
> | M1 | 50% | 工具协议修好（D1/D2/D6 改善） | 几近必然 |
> | M2 | 65% | + 领域继续预训练 + SFT | 大概率 |
> | M3 | 75% | + RL | 有望，已是强结果 |
> | M4 | 85%+ | 逼近 DeepSeek-V4-Pro | 惊喜级别 |
> 阶梯意义：无论落在哪一档，结论都能成立且都值得发表（落在 M1/M2 则支持「规模非瓶颈」论，与 ZhuLong 互证）。

### 🧭 运维规程 · 2026-10-06（agent 归档 MEMORY + 任务书，常驻）

> 用户裁定：MEMORY + 任务书两样都由 agent 自己滚。
> 判据：两者均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交。
> 做法 = 只「搬迁」、不改内容：① 已闭合运维块原文搬入 `run/ARCHIVE_OPERATOR_POSTTRAIN.md`（无则新建）；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块；冲突保留双方；提交用 `posttrain 归档:` 前缀。

## ⚠️ git 同步规则（必读，每次唤醒都要走）

## ══════════════ Stage (ii) 任务定义 ══════════════

你是推进 BaiZe Stage(ii) LLM Post-Training（领域退火 → SFT → RLVR-GRPO → EDA-Eval-PyAether 评测）的自动化 agent（Cline），被唤醒时按 `MEMORY_POSTTRAIN.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

### 阶段总览（与论文 `5_llm_posttrain.tex` 对齐）

| 步骤 | 名称 | 论文节 | 依赖 | 状态 |
|:--|:--|:--|:--|:--|
| 0 | 领域退火（Domain Annealing） | §5.1 | pretrain ckpt | ⬜ 等 pretrain |
| 1 | SFT | §5.2 | 退火 ckpt 或 pretrain ckpt + SFT 数据 | ⬜ 等 P0/P1/P2 |
| 2 | RLVR + GRPO（4 臂奖励 R1–R4） | §5.3 | SFT ckpt + 沙盒 | ⬜ 等 SFT |
| 3 | EDA-Eval-PyAether 评测（backbone × harness 网格） | §5.5 | 各阶段 ckpt | ⬜ 等 ckpt |
| — | Anima 协议 + 本地自纠错（部署） | §5.4 | RL ckpt | ⬜ 部署阶段 |

### 当前可做（不依赖 pretrain ckpt，零/低 GPU）

- **P0**：§7.0 诊断清单 D1–D6（从已有 36% 运行的 `final_report.json` 提取，零 GPU）。
- **P1**：数据盘点 + PyAether 语料调研 + 污染隔离规则草案（零/低 GPU）。
- **P2**：三步训练方案书（纯设计，零 GPU）。
- **P3 预备**：训练/评测脚本骨架（零 GPU，只写不跑）。

### 阻塞项（等依赖就绪）

- **正式训练（退火/SFT/RL/评测）** 阻塞于 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。
- **GPU**：post-train 线在 `10.252.32.17`；正式训练的 GPU 待 pretrain 完成或运维协调分卡（见 `GPU29_ALLOC.md`）。P0/P1/P2/P3预备 纯 CPU/IO 在 `.17` 本机跑。

### 红线（违反则整节作废）

1. **污染隔离**（总纲 §5.1）：158 任务的 prompt + 函数签名 + 断言代码绝对不能进任何训练集。
2. **反作弊**（总纲 §5.2）：`PreToolUse` hook 全程启用；RL 挂同一套 anti-cheat；报告 cheat rate。
3. **口径一致**（总纲 §5.3）：5-run mean ± std；配对检验；引用 ZhuLong 数字前确认口径。
4. **评测协议冻结**（总纲 §2）：158 任务 / Pass@1 / 2500s / 单 trace / 5-run / `-p 8 -n` 不得改动。
5. **预注册**：成功阶梯 M1–M4 + 判定阈值先定后测，避免事后合理化。

### 与他线边界

- **pretrain 线**：提供 base ckpt；post-train 从其收敛 ckpt resume。不 kill pretrain 训练。
- **data 线**：提供 SFT/退火语料的分词镜像；PyAether 语料若需新分词，提需求给 data 线或自行分词（避免重 I/O 撞训练）。
- **harness 线**：提供评测 driver / 评分脚本 / 158-case 数据集的接入方式；post-train 评测复用同一套，只换 backbone。
- **vision 线**：独立，post-train（纯文本）不与 vision 交叉；Stage(iv) MLLM 对齐是另一阶段。

---

> ⚠️ 本文件为只读指令文件，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_POSTTRAIN.md`、`EXPERIMENTS_POSTTRAIN.md` 和 `daily-memories-posttrain/`。
