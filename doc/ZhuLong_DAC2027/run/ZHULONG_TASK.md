# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准（本线消融实验的基座/题量/协议口径不受其影响）。


### 🔴 用户令 · 2026-11-07 08:3x（**两轴消融：cline `--thinking` 档位 × 思维链语言** · 测试集 **EDA-Eval-PyAether 158** · 中文 HTML 报告须含**分数 + 成本**（墙钟/token））· 用户直令 · 最高优先 · ⚠️ 未完成

> **用户原话**：「安排 zhulong agent 做如下消融实验：测试集 EDA-Eval-PyAether（158）。1. 变化 cline 的 thinking 参数：None、Low、Medium等。2. 变化 cline 思维链使用的语言：中文、英文、西班牙文、法文、俄文等，可以通过修改任务提示实现，比如：'请使用XX语言思考'。实验后生成中文 HTML 报告。包含对比表格，不光含不同变体的分数，还应包含成本，比如墙钟、token 等。」

**基座（用户 2026-11-07 明确：GLM-5.3-Flash 或 GLM-5.2，二选一）** —— ⚠️ **两轴实验内必须恒定**（否则 thinking/语言效应被基座差异污染），报告首行写明实际用的哪个。

| 选项 | `-m` | `cline auth`（key 可能过期，**开跑前先 `curl` 探针确认 HTTP 200**）| 既有同臂基线（PyAether 158） |
|:--|:--|:--|:--|
| **① GLM-5.3-Flash**（**首选**：额度新、速度稳、与 harness 线现行一致） | `glm-5.3-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f -b http://agi-gateway.cxmt.com/v1 -m glm-5.3-flash` | `B.glm-5.3-flash` = **86.8 ± 1.6%**（5/5，cline CLI）← **本实验的天然对照锚点** |
| **② GLM-5.2**（备选：①额度耗尽/不可用时改这个） | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` | `B.glm-5.2` = **83.3 ± 3.1%**（5/5，cline CLI） |

> 🚫 **不用 `deepseek-v4-pro-fp4`**（额度已耗尽）。🚫 两轴之间不得换基座。🚫 若两个 GLM 都探针失败 ⇒ **报 blocker 停工**，不许擅自换第三个模型。
> 💡 **优先选 ①**：`B.glm-5.3-flash = 86.8±1.6%` 是既有 cline×PyAether 的正式基线，跑出来的 thinking/语言变体能直接与它做 **Δpp + McNemar** 对照；选 ② 也有一致的基线可用。**选哪个都要在报告里把对应基线拉出来做差**，不能只报绝对值。

**其余口径（不可改）**：测试集 = **EDA-Eval-PyAether 158 题**（`EDA-Scripting-Bench 449` 的 PyAether 子集；🚫 不跑 SKILL/Tcl）· harness = `cline` 3.0.51（🚫 不改版本）· 协议 = Pass@1 单次无 retry `-p 8 -n`（与既有消融同口径）· 环境 = `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`，启动 `setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &`，结束判据 `pgrep -f '^bash scripts/run_cline_script'` 无输出，打分 `$BASE_DIR/venv/bin/python scripts/run_eval.py --latest 1` · 每变体 **3 轮**（成本允许则 5 轮与既有臂对齐，报告写实际 n）。


#### 1. 两轴设计 —— ⚠️ **一次只变一个轴，不做笛卡尔积**

> 5 档 × 5 语言 × 3 轮 × 158 题 ≈ 上万次推理，成本不可控。设计 = **基线 + 单轴扫描**：先固定语言=英，扫完 thinking；再固定 thinking=medium，扫语言。若要交互项只补 2~3 个关键格（如 low×中文、high×中文）。

**轴 A · thinking 档位**（`--thinking <level>`）：`A0 none`（若 cline 不接受 `none` 则**不传该 flag**）→ `A1 low` → `A2 medium`（=既有基线）→ `A3 high`（+ 若 `cline --help` 有第 4 档一并测）。
> **P0（≤15min，先做）**：`cline --help | grep -i thinking` 查**真实枚举**，🚫 不许臆造档位名。`none` 若不被接受，用「不传 flag」代表并在报告**明确标注口径差异**。

**轴 B · 思维链语言**（改 prompt 末尾追加一行，不动 harness）：基线 thinking 固定 `medium`。
| 变体 | 注入后缀 |
|:--|:--|
| `B1 en` | `Think in English.` |
| `B2 zh` | `请使用中文思考。` |
| `B3 es` | `Piensa en español.` |
| `B4 fr` | `Réfléchis en français.` |
| `B5 ru` | `Думай по-русски.` |
| （可选）`B6` 对照 | 不加任何语言指令（原样 prompt）= 真实基线 |

> **注入实现**：在送进 cline 的 prompt **末尾追加**语言指令（不删改原题）。建议给 `run_cline_script.sh` 加 `LANG_HINT` 环境变量透传。
> **⚠️ 必须核验**：①日志可见后缀确实进了 prompt ②**抽 3~5 条 trace 核对思维链真的换了语言**。未生效 ⇒ 停下修注入，🚫 别把无效变体跑满 3 轮；确属未生效则标注「该变体未生效」而非当有效数据。

#### 2. 成本指标（用户明确要求，缺一不可 · 口径照抄 `PLAN_RETEST_READBACK_COST.md` §4）

每变体每轮必报，最终给 `mean ± std`：**Pass@1(%)**（通过/158）· **墙钟·单题均值(s)**（逐题 Step3→Step6，**非** batch 总时长）· **Batch 墙钟(h)**（真实 elapsed）· **Token prompt/completion/reasoning/total**（从 cline session `~/.cline/data/**` 或 trace 聚合，给逐题均值 + 总消耗）· **Token/题**（total/158，横向比贵贱）· **¥（可选）**（有公开单价才换算，🚫 不许编造价）· **Timeout 数**（命中 2500s）· **Converged(%)** · **Gen-fail 数**。
> 判据沿用既有十三：`timeout ≤10`、`0 infra`、`0 exec_err`；Pass@1 任何值有效，**不因低分重跑**。
> **reasoning token 必须单独抽**（thinking 档位直接决定它，是解释「高分是否靠堆思考」的关键）。

#### 3. Trace 保留（硬前置 —— 上次 `(N')` 成本就因 trace 被清而丢失）

每轮结束、清理前：`DEST=/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_ablation_think_lang/<TAG>/<batch>`；`cp -a "$OUT/<batch>" "$DEST"/`（`OUT=.../EDA-Eval-Framework/output_evaluation`），cline session 一并复制。验收：trace 文件数 ≥158（与题一一对应），`du -sh` 记进报告；**不删、不 `git add`**。

#### 4. 执行顺序

1. **P0**：查 thinking 枚举 + 记录基线档；`pgrep` 确认无在跑评测（有则等，🚫 不打断）。
2. **P1 冒烟**：`A0/A2` 各跑 8 题子集（不支持子集则跳过）→ 确认 `--thinking` 真生效（trace 里 reasoning 长度差异）+ 成本抽取脚本跑通。
3. **P2 轴 A 全量**：`A0→A1→A2→A3` 逐档 3 轮，**串行**，每轮即打分 + 落 trace。
4. **P3 轴 B 全量**：固定 `medium`，`B1→B2→B3→B4→B5` 逐语言 3 轮，**每语言先抽 3 条 trace 核对语言真切换**。
5. **P4 报告**。

#### 5. 交付物

- `doc/ZhuLong_DAC2027/reports/report_zhulong_ablation_thinking_language_zh.html` —— **中文单文件自包含，0 script 0 外链**（本线 10-24 常驻规程），必含：①**轴 A 对比表** 变体×{Pass@1, 墙钟/题, Batch 墙钟, prompt/completion/reasoning/total tok, ¥, timeout, converged, gen-fail}，全 `mean±std` ②**轴 B 对比表**（同结构）③**成本-分数象限图**（找性价比最优 / 堆 token 无收益者）④**口径校验节**（thinking 是否真生效 trace 证据 + 各语言是否真切换 trace 原文片段 + `none` 实际实现）⑤**失败归因**（infra/timeout/gen-fail/能力，**infra 单列**）⑥**与既有基线对照**：拉出所选基座的 `B.glm-5.3-flash 86.8±1.6%` 或 `B.glm-5.2 83.3±3.1%`（cline CLI / PyAether 158 / 5-run）做 **Δpp + 配对 McNemar**，逐变体一张小表 ⑦**结论**（边际收益、是否值得改生产配置）。
- 生成器 `run/gen_report_zhulong_ablation_think_lang_zh.py` + 原始数据 `run/ablation_think_lang_results.json`（逐题分数+成本）+ `MEMORY_ZHULONG.md` 心跳 + `daily-memories/` 流水；完成后本行改 `✅ 已交付`。

#### 6. 护栏

🚫 一次只变一轴（两轴同变 ⇒ 效应不可归因）· 🚫 不改 cline 版本/主基座/题面语义（语言指令只追加末尾）· 🚫 不因低分重跑、不用 legacy 数字冒充、不插补缺失轮次 · 🚫 不删 trace，结果 JSON/trace 不入 git · 🚫 不打断其他线（pretrain S1 / vision / data / harness）与在跑评测 · 报告 infra 与能力**分栏**，无效变体必须标注而非丢弃。

> **完成标记**：中文 HTML 报告交付（两表 + 成本列 + 口径校验）⇒ 改 `✅ 已交付`；任一轴未跑完 ⇒ `WAITING: 0`。

---

### 🚨 用户裁定 · 2026-11-05 19:2x（**P0「双盲违规」不成立 —— 论文早已是匿名状态 · 立即闭合**）· 用户直令 · 最高优先

> 用户原话（2026-11-05 19:1x）：「zhulong P0：早已是匿名状态了」

**① 裁定**：撤销长期挂起的「P0 双盲违规仍 OPEN」，**不再等 RUN_ID 143**。运维本地核验（2026-11-05 19:1x，`doc/ZhuLong_DAC2027/ZhuLong_DAC2027/`）：
- `main.tex:1` = `\documentclass[anonymous, sigconf]{acmart}` → anonymous 模式生效（acmart 打印 “Anonymous Author(s)”，且第 54 行注释明确「双盲投稿跳过作者网格改造」）；
- `reference.bib` / `software.bib` 无 `CXMT` / `ChangXin` / `长鑫` 等机构串；无本团队自引（无 `zhulong`/`ZhuLong` 条目）；`liu2025layoutcopilot` / `liu2026agentic` 系**第三方** Liu 姓作者，不构成身份泄露；
- 全部 `.tex` 无 `acknowledg` / `\thanks{}` / `funded` / `grant` 字串。

**② 本轮必做（15 分钟内，写成 1 条心跳）**
1. 把 `MEMORY_ZHULONG.md` 里的 P0 条目改写为 **`CLOSED（2026-11-05 19:2x 用户裁定：早已匿名）`**，并删掉「待运维 RUN_ID 143」表述；§⑧ 跟踪同步改为已闭合。
2. 复核上面 3 条证据仍成立（若 bib 近期有新条目，再扫一次 `CXMT|ChangXin|长鑫|zhulong`），结论 1 行写进心跳。
3. ops inbox 若再出现关于 P0 / RUN_ID 143 的只读回执，只记「已知，已闭合」，不据此恢复阻塞。
4. 若**确实**发现新的可识别信息（作者 / 单位 / 致谢 / 第一人称自引）→ 只做匿名化修正并重编译（`pdflatex×1 + bibtex + pdflatex×2`，ERR=0 / UNDEF=0，页数不变），**不重跑评测**。

**③ 完成标记**：P0 标 CLOSED 且心跳含证据 ⇒ `WAITING: 1`（恢复空巡检）；若发现需改动且未改完 ⇒ `WAITING: 0`。


### 📦 已闭合（batch 15/16，原文见 `ZHULONG_TASK_ARCHIVE.md`）

> 🚨 11-03 21:0x llama.cpp + Qwen3.5-0.8B 安装（smoke 双过）✅ · 11-02 21:3x Tab-3 美观改进（`Tab3_改进建议.html` 已入库，`6_exp.tex` 已落地）✅ · 10-30 22:2x zhulong-full×kimi-k2.6 5-run（**85.0±2.5%**，vs cline 86.8±1.6% Δ−1.8pp）✅ · 10-29 21:5x 论文审阅（92.8KB 报告，P0=1/P1=3/P2=11）✅ · 10-26 08:1x 作废 224219+重跑 glm53-full（已被 10-27 令覆盖）。详情见 archive §batch 15/16。


### 📕 改稿任务令 · 2026-10-25 00:0x（**按外部评审意见改论文（含 57.4pp 归因硬伤）**）· 用户直令 · 与 5-run 并行 ·【保留·与 10-26 令并行】
> **评审原文（必读，逐条对照）**：`doc/ZhuLong_DAC2027/reviews/REVIEW_DAC2027_external_2026-10-24.md`
> 评审结论：**Borderline / major revision**。核心建议 = 「把论文做成**实证 EDA 自动化论文**，grounding-gap 只作**有边界的框架/假设**，不要当成已证明的定理」。

**对：逐条核对（必须先做，别急着改）**
1. 对每条意见给出判定：**成立 / 部分成立 / 不成立**，并**锚定证据**（论文节号/表号/页码，或 `zhulong_results.md` 的行）；
2. **重点核对第 2 条（57.4pp）**：Table 3 里 `no read-back 62.2 → binary 65.5 → full 75.7`，**受控 read-back 轴只有 13.5pp**；57.4pp = 75.7−18.3（含检索+沙盒+自探索的系统级增益）。若核对成立 ⇒ **这是必须改的硬伤**（abstract / 贡献条 / §4.2 / §6.2.1 四处都要改）；
3. 核对第 5 条（SKILL 60.3 vs w/o Self-Expl. 61.5；PyAether 去检索后 81.0 vs 77.3）是否与 `zhulong_results.md` 的 C1/S1 表一致。

**改（P0，必须落地）**
- **A. 57.4pp 归因**：按上面口径拆成三个数并分别表述（受控 read-back 13.5pp / binary 3.3pp / 系统级 57.4pp）；
- **B. 理论降级或补证**：二选一 ——（i）给出显式假设下的 Proposition + 证明；或（ii）把 `D_grounding ≤ g(ε)` 明确写成 **hypothesis/framework**，并把 §4.2 的措辞改到与证据相称（评审给了可直接用的替代句式，见评审 §5）；
- **C. benchmark 可复现性**：补一小节写明「可公开什么 / 受许可限制不能公开什么 / 独立研究者能复现到哪一步 / assertion 如何设计与防假阳性」；
- **D. related work 加强**：对 ChatEDA / AutoEDA / MCP4EDA / LayoutCopilot / ChaTCL / RAG-EDA 逐条写**三句差异**（目标环境 / 统一接口 / 实证贡献），别再只说"我们不同"；
- **E. 参考文献占位符**：修掉 `In Proceedings of . ACM` 这类空字段（ACM-Reference-Format + 缺字段导致）。

**补（强烈建议，能做就做）**
- **F. 成本/延迟/token**：⚠️ **用户提示：陈熙元的版本里已有 cost 数字，可在 git 历史里查到**。请先在 git 里检索（如 `git log --all -S 'cost' -- doc/ZhuLong_DAC2027`、`git log --all --author=Chen`、grep `cost|token|latency|耗时|成本` 于历史版本/`daily-memories`），**找到就直接复用并注明出处 commit**；确实找不到再从 eval log 统计（每任务 token / 墙钟 / tool calls / 约当成本）并标"需补测"。
- **G. SKILL 回归**：回答"为什么离线自探索在 SKILL 上反而 −1.2pp"（给假设 + 可从日志验证的判据）；
- **H. Tcl 拆开报**：WaveView(77) 与 Innovus(57) 分别给数，不要只给 pooled 87.2%；
- **I. 统计**：给 5-run 的 **Wilson CI + 配对 McNemar**（数据已有，不用重跑）；
- **J. 部署声明**：把"服务数百名工程师"改成可核验的表述，或标为"内部部署（细节受限）"。

**交付**
1. `reports/report_zhulong_review_response_zh.html`（中文 HTML，**response-letter 风格**：意见 → 判定 → 证据位置 → 具体改动（原文/新文对照）→ 若未改要写理由）；用 cimi search 时可引用外部资料（给出处）。
2. 论文修订：改完必须 `pdflatex×1 + bibtex + pdflatex×2` 通过，且保持 **7 页（正文 6 + refs 1）**、`0 undefined`、无 Overfull/Underfull 告警（`main.log` 自查）。
3. 更新 `zhulong_results.md` / `MEMORY_ZHULONG.md` 的对应行；commit 前缀 `zhulong paper-review:`。
> 允许为验证关键点打断正在跑的 5-run（先落盘 + 记 MEMORY + 事后 regrade 补记）。**不得编造任何数字或文献**；凡"待补"必须写明怎么补。


### 📦 已归档 batch 13 · 2026-10-27（原文见 `ZHULONG_TASK_ARCHIVE.md` §归档 batch 13）

> 以下均已闭合/已被取代，仅留 1 行指针，需要时读 archive：10-26 ops 中继修复（relay PID118463 活，.last_run_id=128）· 10-26 cimi_search/cimi_fetch 挂载（research MCP 可用）· 10-24 23:0x DAC 审稿+改稿方案（41.6KB 报告已交付）· 10-24 19:0x 论文排版（commit 3651b322）· 10-24 22:23 配置对齐（maxTokens 16384→8192，已被 10-26 令覆盖）· 10-24 22:15 已核实事实（RUN_ID 115/117）· 10-24 22:1x 停 cline-full+重跑 5-run（已被 10-26 令覆盖）· 10-24 20:2x cline vs zhulong-CLI 差异归因（25.9KB）· 10-24 15:4x 引用修正（Lemma→Claim）· 10-24 16:1x refs 单独起页 · 10-24 13:0x 执行令（commit d2d9bb7a）· 10-23 22:1x cline×deepseek-v4-pro×full 5-run（**部分活跃·r1 已硬切留证，r2-r5 待裁决**）· 10-23 09:4x 作废 r1-r3+重跑（已被 10-26 覆盖）· batch 10/11/12 更早指针见 archive。
### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑）。**注**：`wo_sandbox`(=rag 已测) / `wo_selfexpl`(已测·运维令二十六排队干净重测) 不再「暂缓」。 |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 📦 已归档（2026-10-20，batch 6）：运维令 十四 ~ 二十四（10-13 ~ 10-15 批次）

> 均已闭合（echo 数据/消融建议书/paper 编译/SKILL-Tcl 并入/沙盒暂停-恢复撤销等）。**常驻纪律保留**：每次刷新论文前 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；口径=EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）；SKILL/Tcl 数字只认 zhulong_results.md 现存值，未齐标 pending，🚫 凭印象编造。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（06:4x，batch 7）：十三（75% 下限规则）+ 预留追加块

> 均已闭合/长期未使用，原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_ZHULONG.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ZHULONG_TASK_ARCHIVE.md`（无则新建）/ `daily-memories/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `zhulong 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**29KB**（在上限内）⇒ 暂时**无需归档**；一旦 >32KB 即自行滚动。


### 🧭 运维规程 · 2026-10-06（**【每轮唤醒必须自己 commit+push】** —— 不许依赖 loop 兜底）· 常驻

> **用户指令（2026-10-06）**：与 BaiZe 四线同口径 —— **每条线每次唤醒都要推送**。本线此前明文写「靠外层 loop 每 ~5h 兜底」⇒ **自本轮起作废该口径**（§11 已同步修改）。
> **为什么**：运维**只能靠 git 判断你是死是活** —— 2026-10-06 data 线心跳文件近 2h 未更新，被**误判成卡死并上机排查**。🚫「loop 每 N 小时兜底」**不再作为交付保障**，只是保险丝。
> **每轮唤醒结束前，按顺序做完这 4 件事，再置 `WAITING` / 去睡**：
> 1. **写心跳**：更新 `run/MEMORY_ZHULONG.md` 顶部状态头 / 执行看板 / 成绩表 + 追加 1 行操作流水（`[HH:MM] 干了什么 + 关键原始输出 1–2 行`）。
> 2. **写日报**：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮（**当天文件必须建**）。
> 3. **自己提交 + 推送**（🚫 不许等 loop 兜底）：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run doc/ZhuLong_DAC2027/ZhuLong_DAC2027` → `git commit -m "zhulong <阶段/轮次>: <一句话>"` → `git push origin main`。🚫 **绝不用 `git add -A`**（多项目共用工作副本，会卷入别线在途文件）。
> 4. **闭环自检**：`git status -sb` ⇒ 无 ahead / 无 behind。**push 失败**（Forbidden / 网络）重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下轮第一件事补推**。
> ⏱️ **判死判据（硬）**：**心跳文件 >60min 无新提交 ⇒ 按卡死处理**（不再等你）。**你干得再多，心跳不动 = 仍会被判死。**


### 📦 已归档（2026-10-20，batch 4）：运维令 十二 / 十一 / 十 / 九 / (一)~(八)10-10 / (二)~(五)10-09

> 均已闭合（full_v3 5/5=82.1±3.0% 已交付、r2–r5 已完成、RAG/沙盒排查已收口）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。需要时再读。


> **来源**：用户 2026-10-08 观察。根因 = **loop 进程环境里没有 `https_proxy`**（脚本不 export 代理、完全继承启动 shell；只在调 cline 时 `env -u` 剥代理，而 **git 访问 GitHub 必须走代理**）。

**现状（已核对 `zhulong_loop.sh` 源码）**：
- 脚本**无**任何 `export https_proxy=...` —— 代理靠启动 shell 注入。
- 第 117 行 cline 调用 `env -u http_proxy -u https_proxy ...`（剥代理给 cline）—— **这只作用于 cline 那一行**，不影响 loop 自身的 git。
- `git_sync_and_push()`（第 54–103 行）里的 `git fetch origin` / `git push origin main` **直接用 loop 进程的环境** → 若该环境无 `https_proxy` → GitHub 不通 → `timeout 120 git fetch` 触发 → `[push] fetch FAILED (network?) - skip this cycle.` → 永远推不出去 / 拉不回来。

**正确代理值**（与 eval 启动、BaiZe 线一致）：
```
https_proxy=http://172.19.92.23:13128
http_proxy=http://172.19.92.23:13128
```

**你要做的（每次唤醒自检 + 必要时修复）**：

1. **查 loop 进程环境有没有代理**：
   ```bash
   _LPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   [ -n "$_LPID" ] && tr '\0' '\n' < /proc/$_LPID/environ | grep -iE 'https_proxy|http_proxy' || echo "NO_PROXY_IN_LOOP"
   ```
   - 有 `https_proxy=http://172.19.92.23:13128` → ✅ 正常，无需操作。
   - 无 / 值不对 → ❌ 进入第 2 步修复。

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**（详细 bash 脚本已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·该修复已于 10-08 执行完毕，loop 持续带代理运行）：核心 = `pkill -f zhulong_loop.sh` → `export https_proxy=http://172.19.92.23:13128 http_proxy=...` → `setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &` → 复核 `/proc/$PID/environ` 含 `https_proxy`。

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 📦 已归档（2026-10-20，batch 5）：运维令 10-08(一) / 10-05(四~八) / 10-04(全)

> 均已闭合（HTML 报告已交、ops 中继稳定、config dir 隔离已落地、试验次序 B→C1→C2→S1 已生效、环境迁移已落地）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 切臂（5 轮跑完、算好 mean±std 后，启动下一臂前执行）

```bash
cd $BASE_DIR
# 按 STAGE 选一条切换脚本（S1/C1/C2；B 不切 set_ablation，改用 cline auth，见下）
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>      # S1: <ARM>∈{omega_low, readback_binary, readback_none}
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>      # C1: <CONFIG>∈{pure_llm, rag, wo_retrieval, full}
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>           # C2: <ARM>∈{phi_k10, phi_k3, phi_k1, phi_lagged}
bash scripts/stop.sh && bash scripts/start.sh && sleep 3 && tail -20 logs/app.log
```

> ⚠️ **改写 `.env` 的脚本必须串行 `&&` 链执行，严禁并发**（曾并发截断 `.env`）。核对：核心 4 工具 visibility 正确，对应 ENV flag 已写入。

### 启动一轮（脱离进程组）

```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```

> 工具可能超时/无输出，但进程已脱离 → **不算失败**；不要重复启动同一轮。启动后 `PHASE=running`、`WAITING=1`。

### 检查本轮是否结束

```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```

- 有输出 → 还在跑，**什么都不做**退出（`WAITING` 保持 1）。
- 无输出 → 已结束，进入打分。

### 打分（Pass@1；用 grep，别用 run_eval.py）

```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```

> 以 log 里 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评会超时，**不用它做口径**。

### 模型切换（仅 STAGE=B；full 配置不切 set_ablation）

| 模型 | `-m` 参数 | `cline auth` 命令（⚠️ key 可能过期，启动 Phase B 前先核；完整 key 以 `ablation_run_task_model_full.md` 为唯一源）|
|:--|:--|:--|
| `glm-5.2` | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` |
| `deepseek-v4-flash` | `deepseek-v4-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` |
| `kimi-k2.6-cloud` | `kimi-k2.6-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` |
| `doubao-seed-2.0-pro-cloud` | `doubao-seed-2.0-pro-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` |

## 7. 🧭 推进逻辑（每次唤醒严格只走一步）

### 前置校验
读 `MEMORY_ZHULONG.md`「操作流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`；有未处理异常 → 先重试（重打分 / 重启本轮）再按正常流程推进。

### 步骤 0（PHASE=init）
1. infra 三项校验（见运维指令区）：`/home` 磁盘 ≥~8G + 8664/8665/8653/8669 全 OPEN + `run_code` 可执行。
   - 不满足 → `WAITING=1` 原地等，退出（下轮复检）。
2. canary：故意触发一次应被拒的调用，确认反作弊 PreToolUse hook 生效；**未被拒 → 立即停，本批作废**。
3. 切 `S1.omega_low` → 启动 r1 → `PHASE=running`、`WAITING=1`。

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出。
- **pgrep 无输出** → 「打分」：
  - 成功 → 记成绩，`ROUND+=1`：
    - `ROUND<=5` → 启动本臂下一轮（`PHASE=running`、`WAITING=1`）
    - `ROUND>5` → 算 mean±std（± 只加 Pass@1），`PHASE=just_finished`、`WAITING=0`
  - 失败 → `❌ EVAL_FAILED`、`ERROR_COUNT+=1`；<3 重试，>=3 强制推进并照实记。

### 步骤 B（PHASE=just_finished）
按 §5 轮转矩阵切下一臂（或 `done_all`）。切到新 STAGE 先 canary；切完启动该臂 r1。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

### infra 作废规则（吸取旧 S1 停摆教训）
打分时发现整批作废（license 耗尽 / 端口宕 / 磁盘 <8G）→ **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检，三项恢复后再重跑该轮。**绝不拿作废批冒充有效分。**

## 8. ⚠️ S2 Φ 语义约束（最容易做错，逐字遵守）

1. 预算约束的是「能执行 / 能观测多少次」，不是「何时提交」；在工具边界拒绝调用，agent 收 error 后继续自主跑，**严禁**逼迫/提示提前提交。
2. 必须同步报告 `Converged (%)`（`finish_reason==completed` 占比），紧挨 Pass@1。
3. k 臂：`deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 >0，并记 `Mean read-backs`。
4. lagged：单槽缓冲滞后 1 次执行；核对 `reported_call_index` 与实际调用差 ==1（否则该臂作废）。trace_key 已在探路修复（SSE session 身份作键），Phase C2 前 `grep 'ctx.session' main.py` 核修复仍在。
5. 详见 `ablation_run_task_component_s2_full.md` §语义约束 与 `ablation_run_task_s2_1shot.md`。

## 9. 📊 成绩记录口径（README §4.1，写 MEMORY 成绩表）

- `Pass@1` → `mean ± std`（5 轮；`std=sqrt(Σ(xᵢ-μ)²/(n-1))`，1 位小数）。
- `Δ` 列 → 由 mean 相减，**不加 ±**。
- `Converged (%)` / `Mean read-backs` / `Avg/Trace` → 单值，**不加 ±**。
- S2 臂额外记 `Converged (%)` + `Mean read-backs`；模型臂额外记 `Δ vs 主基座`。

## 10. 📉 记忆维护规程（硬性）

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（红线 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
- **任务书自己滚（2026-10-06 用户裁定）**：任务书的归档**由本线 agent 自己做**（与 MEMORY 同机制）—— 只把「已闭合」内容**【原文】搬入** `run/ZHULONG_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**，本区作者仍是运维）。
- 顶部必须保留：`WAITING:`（行首，只出现一次）+ 状态头 + 执行看板 + 成绩记录 + 最近 ~20 条流水。
- 旧文件（`MEMORY.md` / `MEMORY_s1_full.md` / `MEMORY_s2_1shot.md` / 三个 `ablation_run_task_*.md`）为**只读历史参考**，不改。
- `WAITING` 纪律：eval 跑起来置 1；打分推进后视情况置 0；infra 不就绪置 1。

## 11. 🔀 git 规程

- 成果落 `MEMORY_ZHULONG.md` + `daily-memories/` + 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。
- ⚠️ **你自己每轮唤醒必须 commit+push**（见上方「🧭 运维规程 · 2026-10-06」）；外层 loop 每 ~5h 兜底 commit+push **只是保险丝、不是你的交付手段**（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。
