# BAIZE_HARNESS_TASK.md

> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不编造数字、infra≠能力、判据不放宽）。判断标准只有一条：**这条约束是为了「防止说谎」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主决定排查路径、复现手段与修复方案。**

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

> 🔴 **用户令 · 2026-11-15 10:2x（并发放量 + 429 自适应回退）· 最高优先 · ✅ 机制已落码，待下一轮 rerun 实跑验证**
>
> **用户原话**：「harness：趁周末并发可以开的高一些。评测是否可以有些放量和回退机制。
> 长鑫工作时间是:8:30-17:30，工作时间内如果遇到 429 就回退减少并发；
> 工作时间之外如果一段时间没有 429 就增加并发。」
>
> **已交付（代码，可直接用）**：
> - `run/harness/adaptive_concurrency.py`：并发控制器。时段 `work=周一~周五 08:30–17:30`（上限 **4**）/`off=其余含周末`（上限 **10**）；**429 ⇒ 立即减半**（最低 1）并冷却 20min；**非冷却期连续 20min 无 429 ⇒ +1**；两次调整最小间隔 10min；`off→work` 切换时把并发压回工作日上限。状态/事件落 `run/harness/manifests/`（已 gitignore）。
> - `run/harness/terminalbench/rerun_tb21_cline_quota.py`：新增 `--n-concurrent auto`、`--chunk-size N`、`--adaptive-state`。分块串行跑，**每块结束扫日志里的 429/quota**（`429`/`Too Many Requests`/`rate limit`/`额度已用完`/`Token额度`），据此记录升降，**下一块即生效**。
> - `run/harness/terminalbench/launch_tb21_adaptive.sh`：一行封装（默认 `chunk=12`，可用 `HARNESS_CHUNK_SIZE` 覆盖）。
> - `rerun_tb21_7way_quota.py`：支持 `RERUN_N_CONCURRENT=auto` / `RERUN_CHUNK_SIZE=N` 环境变量透传。
>
> **纪律**：
> 1. **默认行为不变**：不显式传 `auto` 时并发仍是 1（历史分数可比性优先）。
> 2. **正在跑的 cc rerun 不打断**（`--n-concurrent` 在 harbor 启动时固定，不可热改）；本轮令从**下一路（opencode/pi/deepseek）或下一次重跑**开始生效。
> 3. **429 归因红线不变**：命中 429 的 trial 仍按「quota-blocked」单列，**不得计入能力失败**；报告分母/口径不变。
> 4. 并发调高只影响**吞吐**，不得改变单题超时、判据、题集；报告需注明「本轮并发为自适应，区间 n=a..b」。
>
> **验收（下一轮唤醒必做）**：
> - `python3 run/harness/adaptive_concurrency.py status` 打印 `mode/current/cap/next/reason`；
> - 用 `--now` 注入 4 个时刻自检：周末 03:00→off（8 起步）、工作日 10:00→work（≤4）、`record --event 429` 后 5min→冷却不减不加、再 25min→+1；
> - 实跑时日志里应能看到 `[adaptive] part k: 429 xN -> n_concurrent=...`；报告里写明实际并发区间。
> - 用 `--dry-run` 验证分块计划时**不得推进状态**（已实现 `persist=not dry`）。

> 📦 §用户令·2026-11-15 07:5x（重构 report_harness_tb21_7way_zh.html：只留两张表、分母统一为题集总数）**✅ 已交付（R2508）** → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：报告重构完成——表一(7路矩阵 Harness|Passed|题集总数|Pass%|墙钟|Token)+表二(失败分析 Failed|Infra|能力不足|其他·逐行守恒✅合计471=7×89−152)+表三(Infra修复台账)·分母统一89(grep eval=0)·成本列=未采集+补采方案(7路token/wall全null·宁缺勿编)·旧版详表归档 reports/archive/harness_tb21_7way/·生成器 gen_report_tb21_7way.py 重写(修count_route用task_name去重+跳job级result.json→evaluated=89)·cc rerun继续不中断。需要时再读。
> 📦 §用户令·2026-11-14 10:0x（hermes python3 not found 修复）**✅ 核心修复已交付 (R2464-R2500)·hermes rerun COMPLETE 38/89·qemu=BLOCKED(Py3.9<3.11)·mteb=infra BLOCKED** → ARCHIVE_OPERATOR_HARNESS.md；根因=a(容器无py3)·_ensure_python()+_ensure_pip()·setup_fail 4→0✅。需要时再读。
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

> 📦 §用户令·2026-11-14 08:0x（TB-2.1 七路额度诊断+重跑）**A+C ✅ DONE / B cc rerun 15/82 in progress**（opencode38→pi46→deepseek48 待跑·用 adaptive_concurrency auto·rerun_tb21_7way_quota.py 就绪）→ ARCHIVE_OPERATOR_HARNESS.md；7路审计:cline=Q0/S8·codex=Q0/S5·opencode=Q15/S23·cc=Q0/S0·pi=Q0/S45·hermes=Q39/S43·deepseek=Q0/S48·rerun_targets=227。需要时再读。
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

> 📦 🔍 既有同类研究线（2026-10-02 勘察，已闭合）→ ARCHIVE_OPERATOR_HARNESS.md；`/nas_train/app.e0031982/harness/` 下 9 月线产物作纯输入复用，loop.sh 已停不重启。需要时再读。

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

