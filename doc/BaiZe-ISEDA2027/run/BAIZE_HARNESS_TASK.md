# BAIZE_HARNESS_TASK.md

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）（本线现有：`reports/report_harness_glm53_7way_swebench_tb_zh.html`、`reports/report_harness_cline_special_zh.html`、`run/harness/gen_report_glm53_7way.py`、`run/harness/gen_cline_special.py`）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
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

### 🔴 用户令 · 2026-11-12 16:3x（**给两个基准的 ETA**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「请 harness 给个ETA：1.TB-2.1；2.SWE-bench Verified。」

**立即执行**（本轮先做这个，其余照旧；轻量、只统计不新起实验）：

1. 针对 **① TB-2.1（89 题 × 7 路）** 和 **② SWE-bench Verified（500 题 × 7 路）**，各给一个**ETA（预计全部完成的时间,含剩余 wait/predict/eval 各段的拆分）**。
2. ETA 的给出必须**可复算**：基于当前真实进度给证据——各路当前已完成/剩余题目数、每轮 step 耗时、predict 存活路数、eval 是否已追上、gateway 当日额度耗用趋势（是否还会触发 429 打断吞吐）。取不到就标「无法可靠估计 + 理由」，🚫 不拍脑袋。
3. 结果落盘为一条**中文简短结论**，写进本轮 MEMORY 心跳 + 双报告（或单独一小节，位置自定），并在**心跳第一行**把两个 ETA 数字直接写出来，方便运维一眼读到。
4. 保持 `WAITING=0` 继续主线（§22:4x / cline 专项照旧）。

---

### 🔴 用户令 · 2026-11-07 10:10（**按早晨令继续评测；cline 专项加盯**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「harness：按早晨的用户令评测，同时多关注一点 cline。」

#### 1. 主线不变（照 08:1x 令执行，不另起炉灶）

1. 代际审计令（Kimi -> GLM-5.3-Flash、SWE-bench Lite -> Verified、TB2 -> TB4）：代际矩阵表 + 可继承/可修改/应废弃逐项落地；
2. 目标：**消灭 TB4 全 0 passed**（先 1 题 x 1 路验 verifier 非结构性 0，再 oracle 必须 1.0）；
3. §22:4x 两基准 7 路全交付；SWE-bench Verified full500 每路推进到 500；
4. 已知硬故障 `deepseek` `gw_proxy_dsh:9093`（1.1s 空 patch）：继续诊断，修好后重启该路。

#### 2. cline 专项（本轮新增重点，独立考核）

| 序号 | 要求 | 判据 |
|:--|:--|:--|
| C1 | **独立统计** cline 的 real patch / empty patch / 每题耗时分布 | 数字可从 trace 复算，给出复算命令 |
| C2 | **失败原因分类**（适配器 / 网关额度 429 / 上游 5xx / 能力 / 超时 / 格式不可解析 / 环境依赖），逐条可追溯到 trace 文件 | 分类占比之和 = 100%，留 top3 样本原文 |
| C3 | 确认 R1733 定位的 resume 判定问题修复后，**cline 空 patch 是否归零** | 未归零必须给根因证据（trace + 日志行） |
| C4 | 每轮心跳含**一行 cline 专项小结**（real/empty/失败 top1） | 缺该行视为未执行本令 |
| C5 | cline 专题 HTML 报告：固定文件 `reports/report_harness_cline_special_zh.html` **原地覆盖**（🚫 禁止 `_rXXXX` 新文件），写清与 hermes/opencode 的差距来源 | 报告在 `reports/`，自包含、0 外链 |

> 📛 命名纪律照旧：报告正文一律写 `cline`，禁止任何 `cline-patched` 变体。

#### 3. 归因红线

- 网关额度耗尽 / 上游 429 **不得**写成"模型能力"结论；
- 能力差（真实做错）也**不得**用"基础设施问题"掩盖；两者必须用 oracle + trace 证据区分。
- cline 若 REAL patch 明显低于其他路，必须给出**可检验假设 + 下一步实验**，而不是只报数字。

---


### ✅ §用户令·2026-11-07 08:1x（评测脚本代际审计）· ✅ 已交付（R1739）

> 📦 §用户令·2026-11-07 08:1x（评测脚本代际审计：Kimi→GLM-5.3-Flash · Lite/TB2→Verified/TB4）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：代际矩阵报告已交付(17.8KB)·oracle=1.0×3(verifier正常)·TB4全0=429+合理失败(运维预判overlay根因=错误)·resume bug已修(size>50B→model_patch非空)·空patch 51.5%→6.9%。需要时再读。

---

### 🔴 §用户令·2026-11-06 22:4x（glm-5.3-flash 重测：SWE-bench Verified + Terminal Bench 4.0 × 7 路）· 用户直令 · 最高优先 · ⚠️ 未完成

> **用户原话**：「harness：用 glm-5.3-flash 重新测试 (SWE-bench Verified + Terminal Bench 4.0) x7」
>
> **口径（不可改）**：backbone 统一 **glm-5.3-flash**（gateway `http://agi-gateway.cxmt.com/v1`，key 用 `launch_glm53_7x300.sh` 里的 `GLM53_KEY`；开跑前先 curl 探针确认 HTTP 200，非 200 不许开跑）；7 路 = cline / codex / opencode / claude-code / pi / hermes / deepseek-harness；**两个基准都要跑满 7 路**。
>
> **基准 A · SWE-bench Verified（500 题，非 Lite）**
> - 复用既有 full500 链路（`run/harness/swebench_verified_full/run_verified_full.py` + `jobs_*/`），只把模型注入切到 glm53：cline 直连 gateway；codex / opencode / claude-code / pi / hermes 走 gw_proxy **9092**；deepseek-harness 走 gw_proxy_dsh **9093**（**照抄** `launch_glm53_7x300.sh` 的 Step1–Step2 配置块，不要重新发明）。
> - 7 路**限并发/串行**（沿用 chain 脚本的 CPU 护栏），每路跑完即 eval；进度按 **100 / 300 / 500** 三段汇报。
> - 结果落 `swebench_verified_full/reports/eval_glm53_<harness>_*.json`；🚫 结果 JSON 不入库（硬约束③）。
>
> **基准 B · Terminal Bench 4.0**（✅ 已核实可得：`~/terminal-bench-4.0` **66 题**，镜像已齐，7 路 smoke 全通——见 §08:1x 令）
> - 走 `terminalbench/launch_tb4_glm53_full.sh`，7 路全量。⚠️ **但当前全 0 passed 是 verifier infra 问题，非模型问题**，先按 §08:1x 令 P0 修 verifier 再跑全量。
> - 若 verifier 修不动 ⇒ **如实上报 RED**，并仍交付 2.0 × 7 路作对照基线，报告**必须显著标注「版本=2.0」**，🚫 不得把 2.0 写成 4.0。
>
> **交付物**：`reports/report_harness_glm53_7way_swebench_tb_zh.html`（中文单文件、0 script 0 外链；含 ①7×SWE-bench Verified 矩阵 ②7×TB 矩阵 ③与 kimi-k2.6-cloud 历史结果同口径对照 ④TB 版本核实结论与分母口径 ⑤失败归因，infra 单列）+ 生成器脚本 + 本线记录（`MEMORY_HARNESS.md` 心跳 + `run/harness/` 下的进度日志）。
>
> **护栏**：CPU 单进程 >80 核立杀（eval 题重跑）、内存同 10-30/11-02 令；🚫 结果 JSON 入库；报告里写 `cline` 不写 `cline-patched`；每路跑完即 commit（`harness glm53:` 前缀）；TASK/MEMORY ≤32KB。
>
> **带件（用户 22:5x）· 硬盘体检**：开工前先 `df -h /data /` + `docker system df`，算清 **TB 4.0 / SWE-bench 镜像预估占用 vs /data 余量**，写进报告一节；不足则给**清理候选清单**（🚫 不得擅自删他人数据 / 他线镜像）。
> **完成标记**：两基准 7 路全交付后本行改 `✅ 已交付`；未交付 ⇒ `WAITING: 0`。

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

