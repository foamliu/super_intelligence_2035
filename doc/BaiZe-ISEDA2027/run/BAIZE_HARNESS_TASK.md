# BAIZE_HARNESS_TASK.md

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。


> 📦 §运维令·2026-10-30 22:2x（把恒为 0 分的 harness 调试跑通）**✅ R988** → `run/ARCHIVE_OPERATOR_HARNESS.md`；hermes 根因=PYTHONPATH 中毒、deepseek 根因=网关 SSE 非标字段+超时 patch 丢弃，均已修复（verify5b 4/5、3/5）。

### 🧷 📛 命名与归档纪律（常驻）
> 🧷 **归档与执行纪律（2026-10-25 用户令 · 最高优先 · 覆盖任何其它归档/收尾条文）**
> 用户原话：「agent 看到任务书 >32k 后要滚动归档，但是它们**在滚动归档时不要碰没有完成的运维指令**，而且在**归档后立即执行运维指令**，而不是立刻睡去等下次唤醒。」
> 1. **未完成的运维指令一律不许归档**：判断标准 = 该块里的任务是否**已产出交付物并 commit**、或运维已标注「已闭合」。**没有 `✅ 已完成/已交付` 标记的一律视为未完成**，不许搬进 ARCHIVE。
> 2. **归档完必须原地继续执行**：归档只是「清理」，**不是本轮交付物**。归档结束后立即回到运维指令区，从最上面那条**未完成**的指令开始做，做完再收尾。
> 3. **禁止**「只做归档 + 写心跳 + 提交 → 置 `WAITING: 1` 睡 30 分钟」。**只要有未完成指令，`WAITING` 必须置 0**（loop 会 60 秒后立即再唤醒），直到该指令交付。
> 4. 判据自检（写进心跳）：`本轮是否还有未完成的运维指令？` 若「是」→ `WAITING: 0` 并在本轮内完成它。

> 📛 **命名常驻规程（2026-10-25 用户令 · 所有线通用的报告纪律）**：**报告里一律写 `cline`，🚫 不许写 `cline-patched`**。
> - 同理：`ClinePatched` / `cline_patched` / `Cline-patched` 等任何变体**均禁止出现在报告正文、表格、图例、TL;DR、结论**里。
> - 理由（用户原话）：「以后在报告里不要写 cline-patched，就写 cline，否则容易造成误解。」——读者会误以为"只跑了被改造过的 Cline"，而实际差异只在接入层（装 CLI / 写 baseUrl / 参数大小写），原生工具循环未改。
> - **代码/脚本/配置里的标识符不改**（`cline_patched.py`、`terminalbench.agents.cline_patched:ClinePatched`、`jobs_cline-patched/` 是真实路径，改了会跑不起来）；**但报告里凡引用必须转写成 `cline`**。
> - 如需交代接入层适配，放在**附录或脚注**写一次即可，正文一律 `cline`。

> 📁 **报告目录纪律（2026-10-28 用户直令 · 全局常驻 · 覆盖一切旧报告路径）**：所有 HTML/中文报告**一律产出在 `doc/BaiZe-ISEDA2027/reports/`**。🚫 **禁止产出到 `run/reports/` 或项目根 `reports/`**（生成器输出路径必须指向项目级 reports；run/reports 历史文件不得再新增）。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区，自上而下找第一条「未完成」的指令执行

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
| C5 | cline 专题 HTML 报告（已有则增量更新），写清与 hermes/opencode 的差距来源 | 报告在 `reports/`，自包含、0 外链 |

> 📛 命名纪律照旧：报告正文一律写 `cline`，禁止任何 `cline-patched` 变体。

#### 3. 归因红线

- 网关额度耗尽 / 上游 429 **不得**写成"模型能力"结论；
- 能力差（真实做错）也**不得**用"基础设施问题"掩盖；两者必须用 oracle + trace 证据区分。
- cline 若 REAL patch 明显低于其他路，必须给出**可检验假设 + 下一步实验**，而不是只报数字。

---


### ✅ §用户令·2026-11-07 08:1x（**评测脚本代际审计：Kimi→GLM-5.3-Flash · Lite/TB2→Verified/TB4** 可继承的继承、不可用的改掉，目标消灭 TB4 全 0 passed）· 用户直令 · ✅ 已交付（R1739）

> **用户原话**：「安排 Harness 重新审视一下以前的评测脚本。从前的脚本是为 Kimi 模型调试的，现在是 GLM-5.3-Flash。从前的脚本是为 SWE-bench Lite/TB2，现在是 SWE-bench Verified/TB4。可用的就继承，不可用的就修改。争取解决 TB4 全 0 passed 等问题。」
>
> **核心认知（先看，别重复踩）**：现有 7 路链路是 **kimi-k2.6-cloud + SWE-bench Lite + TB 2.0** 时代调出来的，现在同时换了两代（模型 + 基准）。**必须逐层审计，不许「整体照搬」**。审计结论要落成一张**代际矩阵表**（维度 × 7 路 × 继承/改/废），写进交付报告。

#### ⭐ 已定位的 TB4 全 0 passed 头号根因（运维侧预查，供你验证而非照抄）

> **现象**：`traces/tb4_glm53_full_*.log` **7 路全部恰好 844 字节且内容相同** → 7 路死在同一处，与 harness 无关。
> **日志原文**：`Configured runtime overrides apply only to the agent environment and are not propagated to separate verifier environments (extra_docker_compose: .../overlay-network-host.yml). Bake grading dependencies into the verifier image under tests/ ...`
> smoke 佐证：`1/1 Mean: 0.000` / `Reward 0.0: 1`，agent 仅跑 1m48s 即结束。
> **根因**：`overlay-network-host.yml` 经 `harbor run --extra-docker-compose` 注入，**只作用于 agent 容器**。TB4 的 **verifier 是独立容器**，拿不到 overlay ⇒ 无 `network_mode: host`（连不上内网）+ 无 `~/.local/bin/env` 与 `uvx` 预挂载（test.sh `source env` 失败）+ 无 pip/uv 镜像 ⇒ **test.sh 崩 ⇒ 无论 agent 干得多好一律 reward 0**。
> ⚠️ 这是 `overlay-network-host.yml` 注释里 R433 同一根因在 TB4 上的**复现**（TB2 靠 `main` 服务名侥幸命中，TB4 拆出独立 verifier 后失效）。
> **修法（择一，须实测）**：**A（首选）** 查 harbor 是否支持 overlay 同时作用于 verifier（`harbor run --help` + 源码，找 `--verifier-*`/作用域参数）；**B** 按日志提示把 grading 依赖烘焙进 verifier 镜像（`tests/` 下 setup 或 prebuild）；**C** 若 harbor 有入口，给 verifier 单独开 overlay（`network_mode: host` + 同 volumes）。
> 🚫 **禁止**把 `Reward 0.0` 当「模型能力差」写进结论。**验证判据**：先 **1 题 × 1 路** 确认 test.sh 能在 verifier 内 `uvx` 起来、reward 非结构性 0；**再跑 oracle 必须得 1.0**，否则仍是 infra 问题。

#### 审计任务（结论写进报告「代际矩阵」节）

> **维度 1 · kimi-k2.6-cloud → glm-5.3-flash**
> - [ ] `grep -rn 'kimi' run/harness/` 实测 **450 处 / 156 文件**，分三类：①**死代码**（`incr_eval_r1570..R1649` 等 40+ 一次性历史脚本）→ 只读留档，**不改不删**；②**活代码**（`run_harness.py:42` `UNIFIED_MODEL`、`incr_eval_backlog.py:67`、`swebench_verified_full/*`）→ 必须切 glm53；③**注释/docstring**（`_base.py:4,41,43`）→ 同步改正，**防止下个 agent 再被误导**（codex 的 `kimi`+`responses` 就是这么来的）。
> - [ ] **协议层**：kimi 时代 `responses` 已废，glm 走 `chat`。核查 7 路协议（codex=chat / claude-code=Anthropic `/v1/messages`→gw_proxy 转 / deepseek=dsh 剥参 / 其余 OpenAI chat）是否都指 **9092/9093**；`_base.py` 的 `TB_MODEL` 默认值不得再是 kimi。
> - [ ] **model 名**：`glm-5.3-flash` vs gateway 实际接受名，逐路 `curl` 探针 200。
> - [ ] **429/额度**：当前 gateway 429（ETA~09:25）与 kimi 时代限流语义是否一致，重试/退避是否需区分。

> **维度 2 · SWE-bench Lite → Verified / TB2 → TB4**
> - [ ] **Verified 500 ≠ Lite 300**：确认 `run_verified_full.py` 实例清单/镜像名/`FAIL_TO_PASS` 解析走 Verified 500。
> - [ ] **空 patch resume 判据 bug**：现按文件 `size>50B` 判 done，空 patch 是 125B ⇒ 永远跳过不重跑，已污染 **205/398=51.5%** → **改判 `model_patch` 字段非空** + 写清理脚本 + 单题验证。
> - [ ] **TB2→TB4 差异**：题数（TB2 89 / TB4 66，须以官方为准并写明）、harbor 版本、dataset 结构、**verifier 拆分**（← 头号根因）、`--agent-timeout-multiplier` 是否仍存在（`launch_tb4_glm53_full.sh` 注释称「removed」，须核实真实参数，别照抄注释）。
> - [ ] **镜像**：TB4 66 张是否全齐；`docker system df` + `/data` 余量核算。

> **维度 3 · 7 路适配器逐个体检（继承 / 修改 / 废弃）**
> 逐路结论表：`cline_patched / codex / opencode / claude_code / pi / hermes / deepseek_harness`
> - [ ] 每路四项：①`install()` 快路径在本代镜像是否仍成立（node/uv/cline ELF/codex npm/claude ELF 挂载点有无变）②`run()` 的 CLI 参数本代是否仍有效（`codex exec` / `claude -p` / `opencode run`…）③超时 `TB_AGENT_TIMEOUT=3600` 是否匹配 TB4 实际耗时 ④退出码处理（现非 0 一律 `raise RuntimeError` ⇒ errored 被当失败，是否该允许「非 0 但已产出结果」）。
> - [ ] **codex 专项**：`config.toml` 曾写死 kimi+responses（已修）→ **确认生效**。其 `tb4_glm53_full_codex.log` 现仅 844B＝连 task 都没跑到，被 verifier 问题掩盖，根因解除后**必须重验**。

#### 执行顺序（严格按此）

1. **P0（≤30min）根因验证**：读 harbor 源码/`--help` 找 verifier overlay 入口 → **1 题 × 1 路** 验证 reward 非 0 → **oracle 必须 1.0**。**这一步不过，后面全部无意义**。
2. **P1 修 resume 判据**：改代码 + 清理脚本 + 单题验证。
3. **P2 代际矩阵审计**：完成上述 3 维逐项结论表（只读代码审计，无需 GPU）。
4. **P3 小规模回归**：TB4 **3 题 × 7 路** + SWE-bench **20 题 × 7 路**，确认 7 路均产出非空结果、无结构性 0。
5. **P4 全量**：等 429 恢复后按 §22:4x 口径跑满；存量 205 个空 patch **作废重跑，不许混进最终分母**。

#### 交付物

- `reports/report_harness_script_audit_gen_matrix_zh.html`：中文单文件、**0 script 0 外链**，含 ①代际矩阵表（维度 × 7 路 × 继承/修改/废弃 + 依据）②TB4 全 0 根因链 ③修复前后 1 题对照证据（含 oracle=1.0）④`kimi` 残留分类清单 ⑤7 路适配器体检表 ⑥残余风险（**infra 单列**）。
- 生成器脚本 + `MEMORY_HARNESS.md` 心跳；完成后本行改 `✅ 已交付`。

#### 护栏

- 🚫 结构性 infra 失败**不得**写成模型能力结论；报告 infra 与能力分栏并给判定依据。
- 🚫 结果 JSON 不入库（硬约束③）；🚫 不改 `run/harness/` 之外的他线上游代码。
- 历史一次性脚本（`incr_eval_r15xx/R16xx` 等）**不改不删**，仅在矩阵表标「历史/死代码」。
- CPU 单进程 >80 核立杀、内存失控先杀再重测（沿用 10-30 / 11-02 令）。
- TASK/MEMORY ≤32KB（运维已归档瘦身到 32KB，**执行本令时继续滚动已闭合块**，别涨回去）；每个 P 阶段即 commit（`harness audit:` 前缀）。

> **完成标记**：代际矩阵报告交付 **且** TB4 ≥1 题 × 1 路 reward 非 0（oracle=1.0 已验证）⇒ 改 `✅ 已交付`；否则 `WAITING: 0`。

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

### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底同步一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_HARNESS.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_HARNESS.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_HARNESS.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-harness/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md \
              doc/BaiZe-ISEDA2027/run/harness doc/BaiZe-ISEDA2027/run/daily-memories-harness
   git commit -m "harness R<N>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。
> 📦 历史已闭合指针 · 2026-10-05~07（原文见 ARCHIVE）：Claude Code 合规口径（遥测已关）· deepseek-harness 工具链自装 · 10-07 汇报 HTML 已交付 · 10-07⑥ **7-way 全完成**（cline 60.0 / Pi 60.0 / Hermes 53.3 / opencode 50.0 / codex 46.7 / claude-code 43.3 / deepseek 40.0%）。

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

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_HARNESS_TASK.md` ≈ 30KB、`MEMORY_HARNESS.md` ≈ 30KB（两者都已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_HARNESS.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_HARNESS_SPEC_HISTORY.md`（无则新建）；
  ③ 较早的巡检条目（保留最近 ~20 条） → `daily-memories-harness/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 「运维问答」④ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---

| 项 | 当前值 |
|:---|:---|
| 当前指令 | 🎯 （2026-10-02 首启）两条线，按序做：<br>① H-B 源码分析（先开始） —— 分析 `/nas_train/app.e0031982/harness` 下各 harness 的源码，从 cline 开始，产出自包含 HTML 报告。分析主线见 §2。<br>② H-A SWE-bench 横评 —— 用 SWE-bench 评测几个 agent harness（cline / opencode / deepseek harness 等）并对比。⚠️ 先做可行性核查（§1.1），再定规模，不要一上来跑全量。<br>🚫 两条铁律：<b>不许猜</b>（源码结论必须贴文件+行号原文）；<b>每个结论必须可复现</b>（命令+输出）。 |
| 优先级覆盖 | H-B（源码分析）> H-A（SWE-bench）；<br>H-A 只在环境与数据集核查通过后才进入实跑。 |
| 状态索取 | `<无>`（若运维写入具体问题，本轮先答该问题再干活，答案写进 `MEMORY_HARNESS.md` 顶部「运维问答」区） |
| 暂停标志 | `<无>`（若写入 `STOP`，本轮只更新记忆、不做任何动作，然后退出） |

---

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

