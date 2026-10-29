# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

### 🔴 运维指令 · 2026-10-29 21:5x（**论文审阅：参考文献 + 逻辑链 + 数字↔措辞一致性**）· 用户直令 · 最高优先 · 覆盖一切

> 用户原话：「数字是没错的，主要核对参考文献，和论文逻辑。以及数字和措辞是否一致。」
> 对象 = **DAC2027 论文权威树** `doc/ZhuLong_DAC2027/ZhuLong_DAC2027/`（`main.tex` + `DAC2027/0~9_*.tex` + `reference.bib` + `software.bib` + `figures/*.pdf`）。**只审不改**。
> ⚠️ **口径（覆盖上一条 21:3x 令）**：**数值正确性已由用户确认 ⇒ 不需要回溯 batch / regrade log 去验数**。只查三件事：**① 参考文献 ② 论文逻辑 ③ 数字与措辞是否一致**。仅当同一数字在文中互相矛盾时，才允许去产物里查一次定位。

**① 重点一：参考文献（权重最高——逐条 + 逐引用上下文）**
1. **逐条核元数据**：`reference.bib` + `software.bib` 每一条 → 标题 / 全部作者 / 年份 / venue（会议或期刊全称）/ volume / pages / DOI / arXiv id；与 Crossref / DBLP / arXiv / Semantic Scholar / doi.org **原始记录**比对。
2. **查幻觉**：条目是否真实存在（非"标题相似的另一篇"）；作者顺序是否被改；年份是否错位（arXiv v1 vs 正式发表年）；venue 是否把 workshop 写成主会、把 arXiv 预印本写成已发表。
3. **逐引用上下文核验（最关键）**：正文每一处 `\cite{...}` 都打开该文献，判断**被引结论是否真由该文支持** ⇒ 标 `✅支持` / `⚠️部分支持` / `❌不支持`（张冠李戴、夸大、方法名错配、把他人不同设置下的数字拿来用）。
4. **覆盖度**：同方向关键基线/近两年工作是否漏引（EDA LLM agent、scripting benchmark、execution feedback / self-debug、RAG for code、EDA benchmark）；是否存在**自引堆砌**或**凑数引用**。
5. **格式**：字段缺失（doi / pages / publisher）、重复条目、key 命名不一致、`\cite` 未定义、孤儿条目（bib 有但正文从未引用）。

**② 重点二：论文逻辑（贯穿全篇的论证链）**
1. 建一张 **claim → 证据 → 结论** 映射表：摘要 / intro 的每条主张，在 §3–§6 是否有对应实验或论证；反之每个实验是否回扣某条主张。
2. **定义—方法—实验闭环**：§4 的理论（如 L4 不可见性、observation fidelity）是否真的被 §6 的 ablation 检验；该检验能否区分它与替代解释。
3. **因果 vs 相关**：凡 `because / therefore / thus / due to / attribute to` 的句子，检查有无对照实验，还是只凭相关性下结论。
4. **ablation 归因**：组件贡献是否单变量、差值是否可加自洽、**改数后归因叙述是否仍成立**（例：回读阶梯跨度 13.5pp→7.1pp 后，围绕 13.5pp 的 "substantial/large" 措辞是否还站得住）。
5. **前后自洽**：§1 承诺 → §6 兑现；§6 结果 → §7/§8 不引入新主张；limitation / threat-to-validity 是否覆盖真实弱点（而非安全项）。
6. **逻辑断点单列**：跳跃（缺中间步）、循环论证、以个例代证明、把 harness 现象当模型能力。

**③ 重点三：数字 ↔ 措辞一致性**
1. **同一数字的多处出现**：摘要 / intro / 正文 / 表 / 图注 / 结论逐处比对（含四舍五入后是否仍相等，如 76.9 vs 76.86）。
2. **措辞强度 vs 数值**：`significant / substantial / large / marginal / comparable / consistent / robust / up to / nearly / over / outperforms` 是否与差值、方差匹配；**差值 ≤ 1 倍 sd 时不得写 "substantially"**。
3. **百分比口径**：pp 与 % 混用、相对提升（+x%）与绝对提升（+x pp）是否写错；"from A to B" 方向是否正确。
4. **表格 ↔ 正文**：正文引用值与表中是否一致；表格加粗（最优）是否与正文 "best/outperforms" 一致；`mean ± sd` 与逐轮数据是否自洽（只查表内自洽，不回溯 batch）。
5. **限定条件**：结论句是否带实验条件（slice / runs / toolchain），有没有把单切片结论写成全称判断。
6. 每条给「原文摘录 → 数值 → 判定 → 建议改法」。

**④ 结构与元数据（轻量，勿喧宾夺主）**
`main.tex`（anonymous·sigconf·作者/邮箱/单位·CCS·keywords）+ **DAC 2027 规则 web 核实**（页数上限、模板版本、双盲、图表与引用格式）+ **页数实测**（`pdfinfo main.pdf`；无则 `pdftotext main.pdf - | grep -c $'\f'`；都没有写「未实测」）。

**⑤ 次要项（有则记，不占主篇幅）**：术语首现定义（Pass@1、Ω、L1–L4）、caption↔正文、单位、`\label`/`\ref` 缺失、语法拼写、`.tex` 残留中文注释、商业工具许可与数据可得性表述。

**⑥ web 核验手段（每条结论留 URL + 抓取时间）**
`https://api.crossref.org/works/<DOI>` · `https://doi.org/<DOI>` · `https://dblp.org/search/publ/api?q=<title>&format=json` · `http://export.arxiv.org/api/query?id_list=<id>` · `https://api.semanticscholar.org/graph/v1/paper/search?query=...` · GitHub API（软件条目）· DAC 官网 / ACM 作者指南 · `cn.bing.com` RSS / DuckDuckGo html。
**必须打开原始页面**，🚫 不得把搜索摘要当证据。
网络：`export https_proxy=http://172.19.92.23:13128; export http_proxy=$https_proxy`；不可达如实写「未核实 + 命令 + 报错」。

**⑦ 交付物**
1. `doc/BaiZe-ISEDA2027/reports/report_zhulong_paper_detail_audit_zh.html` — 中文、单文件自包含、**0 `<script>` / 0 外链资源**、**≥25KB**、标题注明「基于 main.tex@`<HEAD>`」。必含：
   - **TL;DR**（可投 / 需修 / 需重做）+ 问题分级 **P0/P1/P2**
   - **参考文献核对表**：`key | 文献 | 核对源 URL | 元数据 ✅/❌ | 引用上下文 ✅支持/⚠️部分/❌不支持 | 建议`
   - **逻辑链审查表**：`claim | 出处 | 支撑证据 | 强度 | 判定 | 建议` + 逻辑断点清单
   - **数字↔措辞一致性表**：`数值 | 出现位置 | 原文措辞 | 是否匹配 | 建议`
   - **未核实清单**（含已尝试命令与报错）
2. `doc/ZhuLong_DAC2027/run/paper_audit_progress.md`：逐项进度 + 计数（bib 已核/总数、`\cite` 已核/总数、claim 已核/总数）
3. `MEMORY_ZHULONG.md` 顶部：一句话结论 + 报告路径 + P0/P1 计数

**⑧ 判据（缺一不算完成）**
- bib 条目 **100%** 外部核验；正文**每一处 `\cite`** 的上下文都判过（✅/⚠️/❌）
- 摘要 + intro 每条 claim 都进映射表；章级逻辑断点有清单
- **所有出现过的数字**都做过多处一致性比对，且**措辞强度逐句判过**
- 报告 ≥25KB、0 script、0 外链、标签配平；每个 ❌/⚠️ 可复现（URL 或 `文件:行`）

**⑨ 红线**
- 🚫 不改 `.tex` / `.bib` / `figures/`（改法只写进报告）
- 🚫 不编造 DOI / 页码 / 文献；查不到写「查无 / 未核实」
- 🚫 **不得因"数字已确认"就跳过数字↔措辞比对**（这是三大重点之一）
- 🚫 不覆盖旧报告；不碰评测进程 / 端口 / batch；纯离线审阅
- 🚫 不把「未核实」写成「已核实」

**⑩ 节奏**
- `WAITING=0` 立即执行；顺序：通读全文 → 建 claim 表 → bib 逐条 + cite 上下文 → 数字↔措辞 → 写 HTML
- 允许 2–3 轮，每轮必须更新进度文件并 commit（前缀 `zhulong paper-audit:`）+ push
- 完成后置 `WAITING=1`，MEMORY 顶部写「✅ 完成 + 报告路径 + P0/P1 计数」

> 📦 §运维令·2026-10-28 14:4x（r2 收口 67.1% · 端口回自有池 8664/8665/8653/8669 · 继续 r3-r5）**✅ 已完成** → `ARCHIVE_ZHULONG_TASK.md §归档 batch 14`；结论：r3–r5 全部收口，**5/5 = 69.0±2.3%**（r1 71.5 / r2 67.1 / r3 67.1 / r4 71.5 / r5 67.7），vs cline 86.8±1.6% ⇒ **−17.8pp**；全程 0 exec_err / 0 infra / timeout≤6；报告 §9 已更新。

> 📦 §运维令·2026-10-28 11:0x（换端口 8663/8666/8667 重跑 r2）→ 已被 14:4x 端口裁决取代 → `ARCHIVE §归档 batch 14`。

> 📦 §运维令·2026-10-28 10:3x（重跑 r2 regrade + 推进 r3-r5）→ 已由 14:4x 及后续完成 → `ARCHIVE §归档 batch 14`。

> 📦 §运维令·2026-10-27 09:0x（maxTokens 8192→16384 修正 · 作废 8192 5-run）**✅ 已执行** → `ARCHIVE §归档 batch 14`；**关键事实**：cline 基线 = maxTokens **16384** / `-p 4` / batch `2026_1019_005714`；8192 5-run（70.8±7.7%）作废不进对比。

### 🟠 历史指令 · 2026-10-26 08:1x（**作废 224219（配置错误）→ 已修复 worker 配置源 → 重启 loop → 用正确配置重跑 zhulong×glm-5.3-flash×full 5-run**）· 已被 10-27 令覆盖

> ⚠️ **本块已被 10-27 令覆盖**：本块里所有"maxTokens=8192"的硬约束**作废**，cline 基线实测 maxTokens = 16384（见 10-27 令 ④）。本块保留仅供历史追溯。

```text

> 用户原话（10-26）：「作废224219，重启 agent loop。你现在 36.15机器上，可以直接操作。」
> **背景**：10-24 22:1x 令要求「停 cline-full → zhulong 配置对齐 cline（maxTokens 8192）→ zhulong 重跑 5-run」。但 224219 起跑时 **worker 复制了 stale providers.json**（`~/.cline/data/settings/providers.json` = `deepseek-v4-pro + maxTokens=16384`），而非令要求的 `glm-5.3-flash + maxTokens=8192`。根因：`run_cli.sh` 默认 `CLI_DATA_DIR=~/.cline/data`，而 `run_zhulong_script.sh` 的 `export CLI_DATA_DIR=~/.zhulong` 在某些启动路径下未生效。此外 agent loop 在 10-24 22:46 执行 `pkill -f 'zhulong'` 杀 cline-full r1 时**误杀了自己**（zhulong_loop.sh 匹配了 `zhulong`），导致 loop 死亡 ~34h。

**① 已由运维完成（勿重复）**
1. **作废 224219**：已写 `VOID_REASON.txt` 到 `2026_1024_224219/`；数据留证不删；不进 5-run。
2. **修复 worker 配置源**：已把 `~/.zhulong/settings/providers.json`（正确值 `glm-5.3-flash + maxTokens=8192 + baseUrl /v1`）复制到 `~/.zhulong/data/settings/providers.json`（run_cli.sh 复制源）。验证：模拟 worker 复制 → 得 `glm-5.3-flash + 8192` ✅。
3. **确认当前配置全对**：`.env` `CLI_AGENT=zhulong / READBACK=full / PROXY_PORTS=8650,8651,8652,8654`；`~/.zhulong/settings/providers.json` `model=glm-5.3-flash / maxTokens=8192 / baseUrl=http://agi-gateway.cxmt.com/v1 / reasoning.enabled=false`；8090 PID 2778637 活 + full readback 四字段 ✅；4 端口 8650/8651/8652/8654 全 OK。
4. **重启 agent loop**：用**登录 shell** 启动（`setsid bash -lc "exec bash <...>/zhulong_loop.sh" > /tmp/zhulong_loop.log 2>&1 < /dev/null &`），确保 PATH 有 `zhulong`。启动后自检 `command -v zhulong` 有输出 + log 无 `No such file`。

**② 你（agent）要做的（按序）**
1. **读 MEMORY 顶部状态头** → 确认 `STAGE = zhulong×glm-5.3-flash×full 5-run（配置对齐后重跑）`、`PHASE = running`、`WAITING = 0`（loop 刚重启，需起 r1）。
2. **起 r1**（zhulong × glm-5.3-flash × full × maxTokens=8192 × 8650 组 × `-p 4`）：
   - `cd /nasdata/app.e0031982/code/eda_fastmcp && export PYTHON=$PWD/venv/bin/python && unset http_proxy https_proxy ALL_PROXY && export NO_PROXY="10.129.32.75,localhost,127.0.0.1" && export https_proxy="http://172.19.92.23:13128" && CLI_AGENT=zhulong EDA_RUNCODE_READBACK=full setsid bash scripts/run_zhulong_script.sh -p 4 -n > /tmp/ABL_glm-5.3-flash_zl_aligned_r1.log 2>&1 < /dev/null &`
   - **关键**：`run_zhulong_script.sh` 会 `export CLI_DATA_DIR=~/.zhulong`（已确认 line 28），worker 会复制 `~/.zhulong/settings/providers.json`（= `glm-5.3-flash + 8192` ✅）。
3. **起跑后验证 worker 用的模型**：从 `<batch>/cli_data/worker_1/data/settings/providers.json` grep `model` 应为 `glm-5.3-flash`、`maxTokens` 应为 `8192`。**这条必须贴证据**（若仍是 `deepseek-v4-pro` 或 `16384` 立即停跑报错）。
4. **r1 → 手动 regrade（Step7.1 auto-grade 有已知 bug）→ 记 `pass/158` + `gen-fail` + 耗时 + `-32001` + `sandbox-timeout` → r2 → ... → r5 → 5/5 mean±std**。
5. **与 cline 基线 86.8±1.6% 对比**，更新 `reports/report_zhulong_agent_compare_cline_vs_zhulongcli_full_zh.html`（新增"配置对齐后重测"一节）。

**③ 验收判据（不达标要如实报，不得粉饰）**
1. `maxTokens` 等配置 **diff 为空**（除 CLI 名/路径）—— **worker providers.json 必须 = glm-5.3-flash + 8192**；
2. 单轮 **gen-fail ≤ 5/158**（对齐前 12–27）—— 这是本次对齐最该改善的指标；
3. 5 轮判据十三有效（timeout≤10、exec_err=0、infra 0）；
4. 若对齐后 zhulong 仍显著低于 cline，**必须**在报告里给出"已排除配置混杂"的结论。

**④ ⚠️ loop 自杀防护（血泪教训）**
- **禁止用 `pkill -f 'zhulong'`**（会匹配 `zhulong_loop.sh` 自己 → loop 自杀）。如需停 eval，用**精确 PID**：`kill <launcher_PID>`，或 `pkill -f 'run_zhulong_script.sh'`（不含 `zhulong` 字样）。
- **禁止用 `pkill -f 'cline'`**（同理会匹配 cline 相关非目标进程）。停 cline eval 用 `pkill -f 'run_cline_script.sh'`。

**⑤ 作废明细（留证不删）**
- `2026_1024_224219`：worker stale providers.json = `deepseek-v4-pro + maxTokens=16384`（应为 `glm-5.3-flash + 8192`）→ ❌ 作废（已写 `VOID_REASON.txt`）。
- 上一线 ZL-flash full 5/5（10-23，原始配置 maxTokens=16384）= **75.6±4.4%** ✅ 已收口（但 maxTokens 未对齐，不作为 CLI 对比锚点）。
- cline-full r1 `2026_1023_231253` / r2 `2026_1024_141148`：被 22:1x 令停，r2 未 regrade（可补 regrade 留档，但不进 5-run）。

**⑥ 口径备注**
- 本线 = **zhulong×glm-5.3-flash×full×maxTokens=8192**（配置对齐 cline 后），目的是与 **cline×glm-5.3-flash×full×maxTokens=8192**（基线 86.8±1.6%）做"只差 CLI 二进制"的干净对比。
- 新线（glm-5.3-flash × zhulong）**不纳入论文**（用户 10-23 直令）。论文锚点仍用旧线 (N′) fp4×cline 4 轮 mean=76.7% provisional。
- 论文已砍到正文 6 页（DAC 限制达成，commit `e7de188d` + `3651b322`）。

**⑦ 与 10-25 论文改稿令的关系**
- 10-25 00:0x 令（按外部评审意见改论文）**与 5-run 并行**，不冲突。5-run 照跑，论文改稿在等待空档推进。
- 若论文改稿需打断 5-run 验证关键点，按 10-25 令「先落盘 + 记 MEMORY + 事后 regrade 补记」执行。
```

---

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


### 📦 已归档 batch 13 · 2026-10-27（10-24 全批 + 10-23 22:1x + 10-23 09:4x 等已闭合块原文搬入 ZHULONG_TASK_ARCHIVE.md §归档 batch 13）

> 以下均已闭合/已被取代，1-line 指针，需要时读 archive §归档 batch 13。**当前活跃块 = 上方 🟢 2026-10-26 08:1x 与 📕 2026-10-25 00:0x**。
>
> - 🩺 2026-10-26 ops 中继修复（已修复·relay PID118463 活·.last_run_id=128=inbox 顶部）→ archive §batch 13
> - 🔧 2026-10-26 cimi_search/cimi_fetch 挂载（已通过 research MCP server 可用·无需再修）→ archive §batch 13
> - 📝 2026-10-24 23:0x DAC 标准审稿 + 改稿方案（已交付 `reports/report_zhulong_dac_readiness_review_zh.html` 41.6KB）→ archive §batch 13
> - 📐 2026-10-24 19:0x 论文排版（commit 3651b322·已闭合）→ archive §batch 13
> - ✅ 2026-10-24 22:23 配置对齐（maxTokens 16384→8192·已被 10-26 令覆盖）→ archive §batch 13
> - 🔬 2026-10-24 22:15 已核实事实（RUN_ID 115/117 实测·历史参考）→ archive §batch 13
> - 🔴 2026-10-24 22:1x 停 cline-full + zhulong 对齐 + 重跑 5-run（已被 10-26 令覆盖）→ archive §batch 13
> - 📊 2026-10-24 20:2x cline vs zhulong-CLI 差异归因报告（已交付 25.9KB）→ archive §batch 13
> - 📐 2026-10-24 15:4x 引用修正（Lemma→Claim + delage2010percentile·已执行）→ archive §batch 13
> - 📄 2026-10-24 16:1x refs 单独起页（已执行·commit 3651b322）→ archive §batch 13
> - ✅ 2026-10-24 13:0x 执行令（②A+③删附录B+④TikZ 重画·已执行 commit d2d9bb7a）→ archive §batch 13
> - 🆕 2026-10-23 22:1x cline×deepseek-v4-pro×full 5-run（**部分活跃·pending 用户决策 (b) 引用·r1 batch 2026_1023_231253 已硬切留证·是否起 r2-r5 待裁决**）→ archive §batch 13
> - 🟢 2026-10-23 09:4x 作废 r1-r3 + 改 full + 重跑 5 轮（已被 10-26 令覆盖·r1-r3 N′ 数据作废留证）→ archive §batch 13
> - 📦 batch 12 / batch 10 / batch 11 等更早归档指针 → 见 ZHULONG_TASK_ARCHIVE.md 各 §归档 batch N

> 📄 **报告格式常驻规程（2026-10-24 用户令·保留）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

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