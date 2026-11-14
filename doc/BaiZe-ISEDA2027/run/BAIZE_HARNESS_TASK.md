# BAIZE_HARNESS_TASK.md

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）（本线现有：`reports/report_harness_glm53_7way_swebench_tb_zh.html`、`reports/report_harness_cline_special_zh.html`、`run/harness/gen_report_glm53_7way.py`、`run/harness/gen_cline_special.py`）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
   **🔴 `reports/` 只放人读 HTML（2026-11-14 用户令）**：机器逐轮中间产物（`*_<YYYYMMDD>_<HHMM>.json/.log/.txt` 快照、逐题证据、harbor 原始日志）**一律写 `run/harness/terminalbench/manifests/` 与 `traces/`，两处均已 .gitignore**。
   事故复盘：`tb21_cline_quota_rerun_<tag>.json` 曾逐轮写进 `reports/`，随自动提交累积 **27 个 × 1.3k 行**（首犯 `c63912b22` R2391 2026-11-13 19:13），2026-11-14 已 `git rm` 全清。
   提交前自查：`git status --porcelain` 里**不许出现** `reports/` 下的 .json/.log/.txt；`git check-ignore -v <file>` 应命中。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

> 📦 §运维令·2026-11-07 15:2x（TB4 换 TB-2.1 的时限与路径）**✅ 已交付（R1770）** → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：TB4 截止 2026-11-07 未达成「≥1题×≥1路reward非0」(661结果全reward=0=能力·R1743)→16:04 **切换 TB-2.1**→oracle 5/5 PASS✅(break-filter/bn-fit/log-summary/cancel-async/fix-git全reward=1)+7路全量启动(89题×7·/tmp·口径=TB-2.1/89题/7way不可比TB4)+报告 `reports/report_harness_tb21_7way_zh.html` 已交付(含oracle证据/7路矩阵/空patch归因/不可比性说明)。需要时再读。



> 📦 §运维令·2026-10-30 22:2x（把恒为 0 分的 harness 调试跑通）**✅ R988** → `run/ARCHIVE_OPERATOR_HARNESS.md`；hermes 根因=PYTHONPATH 中毒、deepseek 根因=网关 SSE 非标字段+超时 patch 丢弃，均已修复（verify5b 4/5、3/5）。

### 🧷 📛 命名与归档纪律（常驻）
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区，自上而下找第一条「未完成」的指令执行

### 🔴 用户令 · 2026-11-14 10:0x（**排查/修复 hermes 重跑的 `python3 not found` setup 失败；善用 web search 参考他人做法**）· 未完成 · 最高优先

> **用户原话**：「harness：python3 not found 的 setup 失败需要排查/修复。请 harness 善用 web search，看看这种类型的问题别人是怎么处理的。」

**一、现象（你 R2463 自己的心跳）**
- `hermes rerun 8/82`，其中 **4 题 setup fail = `python3 not found`**，另 4 题 ability fail。
- 这 4 题**不是能力问题、不是额度问题**，是**环境 setup 失败**——按你自己的归因红线，**setup fail 不得计入能力**。

**二、必须先做的排查（用证据，别猜）**

1. **抓到 4 个具体 task 名**，逐题贴出：
   - 该 task 的基础镜像（`Dockerfile` 的 `FROM`，例如是否 `oven/bun`、`alpine`、`distroless` 这类**默认不带 python3** 的镜像）
   - 容器内实际执行的 install 命令与**完整 stderr**（含 `HERMES_NO_PYTHON:` 标记是否出现）
2. **关键疑点（我已看过 `agents/hermes.py`，请你核实）**：
   - 适配器 L115-118 已有 `command -v python3 / python` 的探测，L117 打印 `HERMES_NO_PYTHON: no python interpreter in task image` 后 `exit 127`；L103 还调用了 `_ensure_pip()`。
   - **既然有这层回退，为什么还会 `python3 not found`？** 请查清是：
     a) 容器内**确实没有** python3/python（distroless / scratch / 极简镜像）；
     b) 有 python 但**不在 PATH**（如 `/usr/local/bin/python3` 未进 PATH，或 login shell 与非 login shell 差异）；
     c) `_ensure_pip()` 在那 4 题上**本身失败**（preceded error 被你只看最后 5 行 tail 截掉了）；
     d) 镜像里是 `python3.x` 但无 `python3` symlink。
   - **这四种成因的修法完全不同**，请先定性再动手。
3. 顺带核实：这 4 题在**其他 7 路**（cline/opencode/pi/deepseek/codex/cc）跑时是否也 setup fail？若有路跑通了，**对比它怎么处理 python**——这是最直接的答案。

**三、善用 web search（用户明确要求）**

- 检索方向（你自己再扩展）：
  - Terminal-Bench / harbor / 类似 agent benchmark 里，**容器缺 python3 的通用处理方式**（官方 issue、社区 workaround）
  - `python3: not found` in **distroless / alpine / bun / node** base images 的标准解法
  - agent harness 安装 Python CLI 工具的**健壮 install 脚本模式**（探测多候选解释器、`ensurepip` vs `get-pip.py`、`--break-system-packages`、PEP 668 externally-managed-environment 冲突）
  - `PATH` 在 `docker exec` vs `bash -lc` 下的差异导致命令找不到的经典坑
- **要求**：把检索到的**具体做法与来源（URL/项目名）**写进报告，并说明**你采用了哪条、为什么**。🚫 不要只列链接不落地。

**四、修复与验证**

- 按定性的根因修（可能落在 adapter 的 install 阶段，也可能需要给特定 image 预置 python）。
- 修完**先单题冒烟**：确认 `HERMES_NO_PYTHON` 消失、install 成功、hermes CLI 可用、`iterations>0`。
- 再把这 4 题（或受影响题）重跑，结果并回。
- **判据**：`hermes rerun` 完成后，setup fail 数应为 **0**（或每一条都有明确 BLOCKED 理由与证据）。

**五、报告与落盘**

- 归因与修复过程写进 `report_harness_tb21_7way_zh.html` 的 infra 归因节 + MEMORY 心跳一行：
  `hermes python3 修复: 根因=<a/b/c/d> · 参考=<来源> · 改动=<...> · 冒烟=OK · setup_fail 4→N`
- 若确属镜像根本无 python（如 distroless），写 `BLOCKED + 证据 + 需要什么`，并说明这 4 题应如何从分母中**如实剔除或标注**（🚫 不得悄悄算成能力失败）。

---

### 🔴 用户令 · 2026-11-14 09:3x（**修复 claude-code ConnectionRefused → 重测 TB-2.1 89 题**）· 未完成 · 最高优先

> **用户原话**：「harness，既然 claude-code TB-2.1 89 个题都归因为 connection_refused。那需要修复问题 -> 重新测试。」

**一、已知事实（你报告里的原文）**
- `claude-code TB-2.1 = 0/89`，`ConnectionRefused 88/89 (98.9%)` + `CLI 解析 bug 1/89`
- 样本：`exception_message = "Claude-Code exited with code 1: API Error: Unable to connect to API (ConnectionRefused)"`
- 你报告结论：模型从未运行，`tokens=0`；真实能力**无法从本批数据评估**

**二、必做步骤**

1. **定位根因**（先查再改，别直接重跑）：
   - 适配器 `terminalbench/agents/claude_code.py` L174-182 把 `ANTHROPIC_BASE_URL = TB_GW_PROXY_BASE`（`http://127.0.0.1:9092`）、`OPENAI_BASE_URL = TB_GW_PROXY_URL`（`http://127.0.0.1:9092/v1`）注入**容器内**环境。
   - **重点核实**：容器内的 `127.0.0.1` 指向的是**容器自己**，不是宿主机。若 gw_proxy 跑在宿主 9092，容器内必须用宿主地址（`host.docker.internal` / docker bridge 网关 / `--network host`）。请用**实际命令验证**（如容器内 `curl -s -o /dev/null -w '%{http_code}' <url>`），把实测输出贴进 MEMORY 与报告。
   - 同时核实 `--extra-docker-compose` overlay（`overlay-network-host.yml`）在该次运行中**是否真的生效**；以及 7 路里 `cline/pi/opencode` 能连通、`claude-code` 不能，**差异在哪**（这是最有价值的对照证据）。

2. **修复**：按实测根因改（可能是 base_url 换成宿主可达地址、或补 network 配置、或 overlay 未生效）。🚫 不许改判据、不许放宽 timeout 来"刷分"。

3. **重测**：修复后用**与 7 路完全相同的口径**重跑 claude-code TB-2.1 全 89 题（`-k 1`、`n-concurrent 1`、`nice -n 19`、`TB_AGENT_TIMEOUT=3600`、jobs-dir=/tmp）。
   - 重跑前先做**连通性冒烟**（1 题即可）：确认 `ConnectionRefused` 消失、`iterations>0`、`tokens>0`，再跑全量。

4. **出结果**：
   - 更新 `report_harness_cc_tb21_attribution_zh.html`（新跑一轮的逐题归因）
   - 更新 `report_harness_tb21_7way_zh.html`（claude-code 行从 `0/89` 换成真实数字）
   - 若重跑后仍有失败，**必须给非额度/非连接的证据**（iterations / exception_info / finishReason）

**三、判据**
- MEMORY 心跳一行：`cc修复: 根因=<实测结论> · 修复=<改动> · 冒烟=<OK> · 重测=passed/N · vs 旧 0/89`
- 若根因判定为「评测环境限制、无法在离线容器内连通」，写 `BLOCKED + 实测证据 + 需要什么`，🚫 不许把它当成能力结论留着。

**四、提醒**
- 这是**你上一轮自己给出的结论**（「需修复网关连接后重跑才能获得能力数字」），现在按它执行即可。
- 现有 `0/89` 是**无效数字**，修完重测才有意义。

---

> 📦 §用户令·2026-11-14 08:4x（解释cc Q0/S0/0p自相矛盾）**✅ 已交付（R2462）** → ARCHIVE；**结论**：cc 0/89=100%infra(88ConnRefused+1CLIbug·模型从未运行·tokens=0)·真正"模型跑过且答错"=0题·详见 `reports/report_harness_cc_tb21_attribution_zh.html`。需要时再读。

---

> 📦 §用户令·2026-11-14 08:2x（报告整改4条·用户判「不合格」）**✅ 已交付（R2462）** → ARCHIVE；**结论**：①kimi分母统一说明 ②TB4降附录 ③cc0p归因=100%infra+重跑 ④§1§2合并。需要时再读。

---

### 🟡 用户令 · 2026-11-14 08:0x（**TB-2.1 七路「网关 Token 额度耗尽」诊断 + 按需重跑（含 other-6 路与 synthetic 假结果）**）· A+C ✅ / B 脚本就绪待跑

> **R2461 进度**：**A ✅ DONE**（`audit_tb21_quota_7way.py` 创建+运行→7路五桶落盘 `reports/tb21_quota_audit_7way_20261114_0802.json`：cline=Q0/S8·codex=Q0/S5·opencode=Q15/S23·cc=Q0/S0·pi=Q0/S45·hermes=Q39/S43·deepseek=Q0/S48·rerun_targets=226）·**C ✅ DONE**（`gen_report_tb21_7way.py` 增 7路归因表+旧 cline 结论作废戳+38/89 现口径·双报告 REGEN✅）·**B 脚本就绪**（`rerun_tb21_7way_quota.py` 编排器 dry-run OK·226 targets·等 train-fasttext + 5th-batch 跑完启动）。

> **用户原话**：「安排 harness 查一下，cline 和其他 harness 是否仍然有（网关 token 额度耗尽）导致失败的 Case，有则重跑。现在是周末。」

- **下发时的现状（08:0x 复核，勿重复劳动）**：cline 侧 `quota_lost` 已 = **0**（R2460：main+2nd+3rd+4th-batch ALL MERGED，cline=38/90=42.2%）；R2460 另发现 **8 个 synthetic placeholder**（2nd-batch 来源 `rerun_2nd_batch_synthetic`、`has_run_result=false`、`stdout=0` ⇒ **agent 从未真跑**）已起 5th-batch。**⇒ cline 的「额度」问题已闭环，本令剩余价值只在两处：① 其他 6 路从未做过额度口径归因；② 用同一口径复核「假结果/未真跑」是否也存在于其他路。**
- **范围（勿扩大）**：只做 **TB-2.1 / 89 题 / 7 路**。**SWE-bench 侧不查不跑**（cline 专项 C2 已证：网关额度 429 = 0 题 0.0%，66 个失败 100% 能力）。

**A. 诊断（必做，只读）— 覆盖全部 7 路，而不是只有 cline**

1. 新建 `run/harness/terminalbench/audit_tb21_quota_7way.py`：对 **7 路**逐路扫 `/tmp/tb21_glm53_jobs/<harness>/` 的 dated 子目录 `result.json`（过滤口径同 `gen_report_tb21_7way.py::count_route`：`"/20" in str(f)`）。
2. 判定口径**逐字复用** `rerun_tb21_cline_quota.py::classify` 与 `gen_report_tb21_7way.py::_cline_attrtribution`：stdout 含 `额度已用完` 或 `Token额度` ⇒ quota trial；**task 级 `best_reward<1.0` 且全部 trial 均 quota ⇒ `quota_only`**。
3. 关键新增（R2460 教训）：额外标出 **`synthetic_or_never_ran`** —— `agent_result.metadata` 无 `run_result`（或 `stdout` 长度=0 / `"run_result"` 不在 stdout）且 reward<1.0 的 trial → 这**不是能力，也不能算额度**，是「**假结果/未真跑**」，需单列并进重跑队列。
4. 每路四桶 + 一标记，落 `run/reports/tb21_quota_audit_7way_<tag>.json`：`quota_only_tasks` / `mixed_fail_tasks`（不重跑）/ `ability_fail_tasks` / `synthetic_or_never_ran` / `not_evaluated`（89−evaluated，**先补跑非重跑**）。
5. MEMORY 心跳写一行汇总：`7路 quota_only: cline=0 · pi=? · opencode=? · deepseek=? · hermes=? · codex=? · cc=? | synthetic: <各数> | evaluated: <各值>/89`。

**B. 重跑（只跑 A 里非空的桶；空的就记「0」不跑）**

1. 前置：`curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9092/v1/models` = 200；确认**无 SWE-bench predict 抢同一额度池**（周末窗口独占）；S1 训练（10.239.2.29 pretrain）不挤；`df`/`nvidia-smi` 自检照常。
2. 排队顺序：**5th-batch（8 synthetic）先跑完** → 再跑本次审计新增的 `quota_only`/`synthetic` 题；**逐路串行，一路 merge 完再起下一路**（避免 R2454 踩过的 cline-hub 冲突）。
3. cline 路：沿用 `rerun_tb21_cline_quota.py --launch`（判定口径不许改）。
4. 其他路：把 `rerun_tb21_cline_quota.py::launch()` 的 `HARNESS`/`AGENT` **参数化**（新增 `--harness <name>`，或另建 `rerun_tb21_quota_7way.py`，**沿用其 judge/merge/落盘逻辑**），agent 映射照抄 `launch_tb21_glm53_7way.sh:67-73`：`codex=terminalbench.agents.codex:CodexTB` · `hermes=…hermes:HermesTB` · `opencode=…opencode:OpenCodeTB` · `claude-code=…claude_code:ClaudeCodeTB` · `deepseek-harness=…deepseek_harness:DeepseekHarnessTB` · `pi=…pi:PiTB`。
5. 参数不得放宽：`-k 1`、`--n-concurrent 1`、`nice -n 19`、`TB_AGENT_TIMEOUT=3600`、`sg docker` 兜底、jobs-dir=/tmp。
6. 跑完：`--merge /tmp/tb21_glm53_jobs/<harness>_rerun_<tag>` → `gen_report_tb21_7way.py` + `../gen_cline_special.py` REGEN → commit（`harness:` 前缀，只 add 本线路径）。

**C. 报告口径修正（本轮必做）**

- `gen_report_tb21_7way.py`：① 额度归因从 cline 单路扩为 **7 路表**；② 顶部「结论一句话」改**数据驱动**（合计 0 时写「无额度失败；失败=timeout/ability/假结果」）；③ 旧文字「主因=额度耗尽…原始 10/89=11.2%…公平 40%」加「~~作废~~ 见 R<本轮>」时点戳，并补 R2460 后的 38/90=42.2% 现口径。
- `report_harness_cline_special_zh.html` 的 TB-2.1 段（仍写「65 题 81%…公平 40%」）同步改「已清 0 + 现 38/90」。
- 🚫 不手改 HTML，改生成器后 REGEN。

**D. 判据**：重跑前后 `quota_lost` 与 `synthetic` 题数、各路 passed/fair-pass **同框**写进心跳；重跑后仍 0 分的题必须给**非额度证据**（iterations/exception_info/finishReason），否则不得下能力结论；`synthetic` 重跑后若仍无 run_result ⇒ 报 infra bug，禁写「模型不会」。

**E. 红线**：🚫 不改 SWE-bench 口径/数字；🚫 额度失败≠能力、假结果≠能力（三者必须分开记账）；🚫 同题多 trial 只按 unique task 计一次；🚫 不放宽 timeout/并发刷分；🚫 无实测 `http_code`+trial 证据不得断言「额度已恢复」。

**F. 落盘**：`run/reports/tb21_quota_audit_7way_<tag>.json` + `run/reports/tb21_quota_rerun_7way_<tag>.json` + `run/harness/terminalbench/traces/tb21_quota_rerun_7way_<tag>.log` + MEMORY 心跳 + 双报告。

**G. 节奏**：本轮先做 **A+C**（诊断+口径，纯只读/生成器），把 7 路清单落盘；**同轮内网关 200 且无 predict 竞争就顺势进 B**（周末额度补充窗口，别拖到工作日）。不能跑就写 `BLOCKED: <原因> + 清单已落盘`，不许空转。
**H. 体积提示**：本令下发时 `MEMORY_HARNESS.md` 已 31.4KB（贴 32KB 上限）⇒ 本轮先按 §工作约定 把已闭合的 R24xx 流水 fold 到 `daily-memories-harness/`，再写心跳。

---

> 📦 §用户令·2026-11-13 18:2x（cline额度耗尽重跑）**✅ 已交付（R2460）** → ARCHIVE；**结论**：cline TB-2.1 quota_lost=65→0✅·cline=38/89=42.7%·8synthetic待5th-batch·已被11-14 08:0x七路令取代。需要时再读。

---

> 📦 §用户令·2026-11-13 15:5x（cline低分根因）**✅ 已交付（R2386）** → ARCHIVE；**结论**：cline 10/89=11.2%低分非能力·主因=网关额度耗尽(65/80=81%)·公平10/25=40%·值得rerun。需要时再读。

---

> 📦 §用户令·2026-11-12 16:3x（两基准ETA）**✅ 已交付（R2279）** → ARCHIVE；**结论**：TB-2.1已交付·SWE-bench Verified~15天(codex瓶颈@25/天)。需要时再读。

---

> 📦 §用户令·2026-11-07 10:10（cline专项加盯）**✅ C1-C5 已交付** → ARCHIVE；**结论**：C1-C5全done(332real/empty=0/74.7%/报告R2453)·代际审计见08:1x·TB4→TB-2.1见15:2x·deepseek已修(R988)·剩余TB-2.1 rerun由08:0x覆盖。需要时再读。

---



### ✅ §用户令·2026-11-07 08:1x（评测脚本代际审计）· ✅ 已交付（R1739）

> 📦 §用户令·2026-11-07 08:1x（评测脚本代际审计：Kimi→GLM-5.3-Flash · Lite/TB2→Verified/TB4）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：代际矩阵报告已交付(17.8KB)·oracle=1.0×3(verifier正常)·TB4全0=429+合理失败(运维预判overlay根因=错误)·resume bug已修(size>50B→model_patch非空)·空patch 51.5%→6.9%。需要时再读。

---

> 📦 §用户令·2026-11-06 22:4x（glm53重测SWE-bench+TB×7路）**✅ SWE-bench 7路全交付 / TB→TB-2.1(由08:0x覆盖)** → ARCHIVE；**结论**：SWE-bench Verified 7路done(cline356/opencode401/pi333/codex291/cc273/deepseek212/hermes184)·TB4切换TB-2.1(✅R1770)·TB-2.1 rerun由08:0x覆盖·报告已交付。需要时再读。

> 📦 历史已闭合指针（原文见 ARCHIVE）：10-28 19:1x+20:0x（结果 JSON 不入库 → R584 `git rm --cached` 15 个；**③ 硬约束仍生效**）· 10-28 12:0x（TB 7way 整改）· 11-04 13:5x（修适配器 → cline **356/500=71.3%**）· 11-04 13:1x（cline 326 vs opencode 401）· 11-06 17:1x（差距 86% 为能力差，p=6.27e-08）。
### 🚀 运维令 · 2026-11-02 11:2x（**自检同时盯 CPU：本线评测进程 CPU 不许失控，容器内失控用 sudo/docker kill**）· 用户直令 · 最高优先

> 用户原话（2026-11-02 11:2x）：「让 harness 持续关注自己的评测进程，不光内存，CPU 也不能超过 80%。」

**① 背景（运维已核）**：11-02 harness **eval 阶段**失控——sklearn 一个 pytest 吃掉 **185 核**（`%cpu=18500%`），整机 load 顶到 234/224，抢 S1 训练 CPU。**两个新事实**：① 是 **CPU 失控**（n_jobs 失控拉起全 224 核）而非内存；② 跑在 **eval 容器内**（`containerd-shim-runc-v2` + `/opt/miniconda3/envs/testbed`）⇒ 普通 `kill -9` 杀不掉（EPERM），必须 `sudo kill -9` 或 `docker kill <容器id>`。

**② CPU 硬判据（每次唤醒自检，与内存并列，先于一切业务）**：
- `ps -eo pid=,ppid=,pcpu=,rss=,args=` 检查**本线**评测进程（predict 的 7 路 agent + eval 容器进程）CPU。
- **单进程 `%cpu` 持续 > 8000%（=80 核）→ 立即 kill**；或**整机 CPU busy 被本线评测顶到 >80%**（≈179/224 核，`top` 的 %Cpu 判断）→ 定位最高 CPU 的本线进程 kill。
- **杀法**：宿主机进程用 `kill -9`；**容器内进程（父链含 containerd-shim/runc 或路径含 `/opt/miniconda3/envs/testbed`）必须 `sudo -S kill -9` 或 `docker kill <id>`**（运维已留 sudo 密码）。

**③ 杀掉后果处理**：eval 题 → **该题重新 eval**（predict 结果不丢）；predict 题 → **重新 predict**；每次 kill 记录 `harness 内存/CPU:` 心跳 + 题目即时重跑。

**④ 纪律**：只清本线，🚫 不碰 S1 训练 / vision / data / zhulong；心跳写 `未完成指令：有` ⇒ `WAITING: 0`；commit `harness 内存:`。

### 🚀 运维令 · 2026-10-30 11:1x（**唤醒后首事：自检本线评测进程内存，失控先杀再重测**）· 用户直令 · 最高优先

> 用户原话（2026-10-30 11:1x）：「这些 agent 不是应该在容器中运行吗？内存过高可否限制？…harness 唤醒后先看看自己的评测是否占用过多内存，如果是，先杀掉，再想办法重测。」

**① 背景（运维已核）**：10-29 cline 路在 `.29` **宿主机**上跑 SWE-bench sympy 时失控——`list(partitions(200))` + `pytest test_fancysets.py` 吃掉 **~1.2TB** 内存，威胁 S1 训练（运维已 kill）。**predict 阶段跑在宿主机（非容器），不受内存限制**＝根因。

**② 硬要求（每次唤醒第一件事，先于一切业务）**：
- `ps -eo pid=,ppid=,rss=,args=` 检查**本线**评测相关进程（predict 的 cline/codex/opencode/pi/claude-code/hermes/deepseek 及其子 bash/python/pytest 子树）内存。
- 判据：任何**本线**进程（或同 bash 进程树）RSS 异常高（单进程 >50GB，或多棵进程树累计吃掉宿主机 available 的显著份额）→ **先 kill -9 整棵失控进程树**（含父 bash），再记录。
- 特别警惕缩放型失控 cmdline：`partitions(`、`list(...)`、无界 `pytest`（内存爆炸测试）等。

**③ kill 掉的是正在跑的预测子任务** → **该题重新 predict**（不丢题、不重复 eval）；并评估加内存护栏（cgroup / ulimit / 改评测触发方式）后再重测。

**④ 纪律**：只清本线，🚫 不碰 S1 训练 / vision / data / zhulong 进程；心跳写 `未完成指令：有` ⇒ `WAITING: 0`；commit `harness 内存:`。

**⑤ loop 已改（运维改好了，无需你动）**：`SLEEP_WAIT`/`PUSH_INTERVAL` 30→15min。

> 📦 §运维令·2026-10-28 07:1x（SWE-bench Verified 全量 500 题）**✅ 已完成** → ARCHIVE；7 路全量完成：**cline356 / opencode401 / pi333 / codex291 / claude-code273 / deepseek212 / hermes184**。
> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。
### 📦 历史已闭合指针 · 2026-10-17 ~ 10-24（原文见 `run/ARCHIVE_OPERATOR_HARNESS.md`）

> 均已闭合/交付（原文见 ARCHIVE）：10-24 16:3x（TB7并发+Verified镜像，**Verified=500 非 Lite**）· 10-24 09:2x（92.25 配 dockerd，TB 镜像齐）· 10-24 09:0x（7 并发）· 10-23 22:1x（npm -g，Gate 7/7 R466）· 10-23（落盘写报告 / 上下文压缩 7 路报告）· 10-19 23:1x（kill .12 双 loop + R457 hermes fix）· 10-18 10:2x（ops 中继已修）。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 📦 历史已闭合指针 · 2026-10-16 ~ 10-17（详情见 `daily-memories-harness/` 对应日期 + ARCHIVE）

> 全部已闭合/交付：10-17 20:0x（oracle **5/5**，中继已恢复）· 10-17（TB2 · 7×89 · kimi；**结论**：TB2=89 tasks、oracle 须 5/5、7 路不得替换/合并）· 10-16（补完 188 条 → glm53 **2100/2100**）· 10-16（`report_harness_glm53_7x300_zh.html` 已交付）。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_HARNESS.md` / `run/ARCHIVE_HARNESS_SPEC_HISTORY.md`（无则新建）/ `daily-memories-harness/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `harness 归档: …` 前缀。
> 本轮动作：本任务书现 ≈32KB（已贴上限）⇒ 下次唤醒先归档到 ≤32KB，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。

### 🆕 运维口径 · 2026-10-05（你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测）

> 定位（2026-10-05，跨线）：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（目的是给内网网关鉴权：不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ 你（agent）会话里每条命令都继承了「无代理」env。
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 `Network is unreachable`（Errno 101）/ http `000` 是预期现象：🚫 不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题——别把它写进结论。
> 🔧 正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）：凡访问外网的那一条命令，自己显式带上代理（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都不要带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> ✅ 同机反证：`run/harness/r1_eval.py:144-148` 显式钉 proxy + 阿里云索引，pip 一直成功；relay 侧 git 同理（内网网关两种都 200）。
> 🚫 装包别动共享 py310 env（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 10-05「换冷门模型+严格串行」已归档 → 被 10-07 7-way 取代。

## 📊 进度快照（每次唤醒必须更新，供远程巡检）

> 固定格式写在 `MEMORY_HARNESS.md` 最顶部，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_HARNESS.md` 的顶部单独一行
（`baize_harness_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行 —— 否则会误触发 30 分钟长睡。

运维巡检方式：外部运维 `git pull` 读 `MEMORY_HARNESS.md` 顶部 + `harness/` 下的报告即可，不需要登录服务器。

---

## 0. 任务概述

目的：横向理解「agent harness」这一类系统 —— 它们的工程实现差异，以及它们在真实软件工程任务上的能力差异。

| 线 | 内容 | 产出 |
|:--|:--|:--|
| H-B | 源码分析（从 cline 开始） | `harness/<name>_SOURCE_ANALYSIS.html`（自包含） |
| H-A | SWE-bench 横评（cline / opencode / deepseek harness 等） | `harness/SWEBENCH_COMPARE.html` + 结果表 |

代码位置：`/nas_train/app.e0031982/harness/`

> ## 🔍 既有同类研究线（2026-10-02 勘察，已闭合 → 详见 `run/ARCHIVE_OPERATOR_HARNESS.md`）
>
> `/nas_train/app.e0031982/harness/` 下另有一条 9 月创建的同类线（5 个 harness 源码 + `loop.sh` + `MEMORY.md` + `evidence/` + `mechanisms/` + `analyze_harness_sources.md` 11.8KB + `report.html` 24.6KB）。
> 运维 2026-10-02 确认：其 `loop.sh` **早已停掉**，⚠️ **不要重启它**；指示「可以合并」——其产物作**纯输入**复用，结论按我方主线重新审视。
> 纪律：① 只读不改它的目录 ② 产出统一落我方 `run/harness/` ③ 🚫 不启动它的 `loop.sh`（避免两个同类 loop 抢 token）。

---

## 1. H-A —— SWE-bench 横评

### 1.1 🔴 第 0 步（必做，先做）：可行性核查

在跑任何评测之前，逐条查清并报给运维：

| # | 查什么 | 怎么查 |
|:--|:--|:--|
| 1 | `harness/` 下有哪些 harness、各自版本 / 形态（CLI？插件？）| `ls -la` + 各自 `README` / `package.json` / `pyproject.toml` |
| 2 | 每个 harness 怎么启动、接什么模型（是否要 API key、能否接本地模型）| 读文档 + 试 `--help` |
| 3 | 模型可用性：本机能调哪些模型？（DeepSeek API？本地 vLLM？）| 实测一次最小调用 |
| 4 | SWE-bench 数据集：能否取到？取哪个子集？ | ⚠️ **现行口径 = SWE-bench Verified 500 题（不是 Lite 300）**；见 §用户令·2026-11-06 22:4x |
| 5 | 评测容器 / 沙箱：见下方「§1.1-bis 无 Docker 路线」 | `docker info`；不可用就按 §1.1-bis 改道 |
| 6 | 磁盘/时长预估：跑 N 条大概要多久、多少磁盘 | 按单条实测反推 |

🚫 第 0 步没通过之前，不许"假装跑了"或"用其他指标冒充 SWE-bench" —— 如实报告阻塞。

> 📦 §1.1-bis 无 Docker 路线 + 连通性测试 + sb-cli 合规 + 路线优先级 已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；结论：R1 unshare 沙箱路线已选定并实现，2100 条评测已完成，pypi/内网镜像可用，docker 不可用。需要时再读。

### 1.2 评测设计（核查通过后）

