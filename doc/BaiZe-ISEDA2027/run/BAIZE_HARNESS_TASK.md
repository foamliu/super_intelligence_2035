# BAIZE_HARNESS_TASK.md

### 🔴 用户令 · 2026-11-23（**全量 infra 排查 + 夜间重跑（21:00–09:00）· 从 cline 起**）

> **背景（已核实）**：7-way 里 cline 的 Pass% 被 93 个空 patch 拖低（opencode 仅 1 / hermes 仅 4）。运维已初查：cline 这 93 个空 patch 中 **58 个是 infra**（38 Token 额度 429 + 13 超时 + 5 上游 5xx + 2 鉴权），但最终 eval 的 `infra_or_quota` 却记为 0 —— infra 失败被并进「能力失败」桶，夸大了能力差距。详见 `reports/report_harness_cline_lag_analysis_zh.html`。

#### 第一步 — 深入排查各线真实 infra failed case 数量（7 路全查）

1. 对**每一路**（cline-patched / codex / opencode / claude-code / pi / hermes / deepseek-harness），把 eval 里所有未 resolved 的 case，按 `progress_glm53_*.json` 的 `stdout_tail`/`stderr_tail`/`quota_blocked`/`timeout` 逐题分类（复用并推广 `swebench_verified_full/c2_cline_R2233.py` 的框架）：
   - **infra**：Token 额度/429/rate-limit、超时、上游 500/502/503/504、鉴权 401/403/forbidden/适配器、`quota_blocked`/`timeout` 标志位。
   - **ability**：确实产出了 real patch、但 apply+test 失败（这是能力，不重跑）。
   - **待定**：空 patch 且 rc=0 无报错（无法从 tail 判定，如实标注、不强挤进任一桶）。
2. 产出**每路一张表**：`infra_failed（需重跑）/ ability_failed（不重跑）/ 待定（需 transcript）` 三列 + 逐题清单，落一份中文 HTML（复用报告纪律：0 script/0 外链）。

#### 第二步 — 重跑 infra failed（从 cline 起，按 infra 数量降序）

1. **只重跑 infra 类**（含「待定」里的空 patch —— 空 patch 重跑成本低、大概率能出分），🚫 不重跑 ability 类（那是能力，重跑无意义、属造假风险）。
2. **顺序**：cline → 其余按 infra 数量降序。
3. 重跑 = 重新 predict（对 infra 空 patch 题再跑一次 cline 出 patch）→ 复核 → eval → 把 resolved/failed/infra 结果**合并回** `eval_glm53_*.json`，并 REGEN 7way 报告。

#### 第三步 — 重跑时间窗：每晚 21:00 – 次日 09:00（12 小时，避高峰）

1. **只在窗口内启动/继续重跑**；判断 = 本地时间小时数：
   ```bash
   H=$(date +%H); [ "$H" -ge 21 ] || [ "$H" -lt 9 ] && echo 窗口内 && run_rerun || echo 窗口外 && park
   ```
2. 窗口外（09:00–21:00）：**只 park**——不启动新 predict/eval，把重跑队列存着，等下一个 21:00 窗口。
3. 原因：避开 glm-5.3-flash 网关白天使用高峰（额度 429 正是高峰产物）+ 白天 CPU 争抢。

#### 纪律（沿用既有护栏，不得因"夜间"放松）

- 重跑过程**必须继续守硬护栏**：docker eval `--memory 128g --cpus 16`、宿主 predict `ulimit -v 209715200` + nice19 + OMP≤8、`harness_resource_guard.sh`（PID931671）常开、pretrain step ≤7.4s 越界即降载、load 闸。
- 并发克制：夜间重跑也**限并发 ≤2 路**，别再触发额度。
- 只动本线文件；不碰 pretrain/data/vision/zhulong。额度 429 重试要带**退避**（如指数退避 + 重试上限），不要裸刷网关。
- 诚实：重跑结果标注「夜间重跑」口径；`WAITING` 按窗口与在途任务管理。

#### 交付

- ① 中文 HTML：`reports/report_harness_infra_rerun_plan_zh.html`（各线 infra/ability/待定 三列清单 + 重跑顺序 + 窗口策略 + 每晚进度）。
- ② 每晚窗口结束后，7way 报告 REGEN（resolved 更新后按 resign 序重排）；`MEMORY` 心跳记「infra 重跑：已回收 X 题」。

### 🔴 用户令 · 2026-11-20 16:3x（**harness 解冻 · 恢复评测 · 覆盖 14:5x 冻结令**）

> Phase 0 冻结态已验收通过（loop CPU 节流 LIVE / 护栏守护 PID931671 存活 / 自检 clean / pretrain step~7.28s≤7.4s / 无 eval 容器）。现**解冻**，恢复被打断的评测。🚫 解冻 ≠ 回到无护栏态：**Step 1 硬护栏必须先落地，Step 2 再分批恢复**。

#### Step 1 — 先落地硬护栏（本令最高优先，做完才动评测）

1. **docker eval 加内存/CPU 上限**：eval 入口统一注入 `--memory 128g --memory-swap 128g --cpus 16`（包 wrapper，或核实 swebench harness 是否支持透传 docker 参数；做不成就如实报「未做」并让该路 eval 串行+降并发，不得裸跑）。
2. **宿主 predict 加 `ulimit -v 209715200`**（=200GiB，单位 KB）+ 既有 `nice -n 19` `ionice -c3` + `OMP_NUM_THREADS≤8`。
3. **护栏守护保持运行**：`harness_resource_guard.sh`（现 PID931671）不得停；若不在先重启它。

#### Step 2 — 分批恢复（由轻到重，逐步）

1. **先**：Verified predict 3 路（codex/pi/dsh）续跑，限并发 ≤2 路。
2. **再**：incr_eval backlog（含 deepseek R2800 的 5 个 matplotlib），必须走受限容器，串行。
3. **最后**：MM 2×3 predict 6 路（最重），待前两项护栏验证稳定后再开，限并发。

#### 判据（每轮自检，越界即降载/暂停）

- pretrain step ≤7.4s；超了立即暂停 predict/eval 让 pretrain。
- 宿主 mem avail ≥ 512G（护栏守护 400G 是最后防线；到 512G 先自己降载）。
- `docker ps` 里每个 harness eval 容器都带 `--memory` 限制。

#### 纪律

- `WAITING` 交回你自己按业务管理（有长任务 RUNNING=1，否则=0），不再强制 1。
- 只动本线；不碰 pretrain/data/vision/zhulong。
- `.12` 均摊（incr_eval docker/报告生成迁 `.12`）作可选优化；若做，`.12` 上 nice19 + load 闸阈值 80，且不得影响 data 线分词。
- TASK 37.9KB 超软限：本轮顺带把已闭环旧运维块（含下方 14:5x 冻结令、08:2x 令）迁到 `ARCHIVE_OPERATOR_HARNESS.md` 留指针。
- 诚实底线：护栏会拖慢评测 ETA，报告里明写，不藏。

### 🔴 用户令 · 2026-11-20 14:5x（**OOM 事故后带护栏分批灰度重启**）· ✅ 已闭环（Phase 0 完成·16:3x 解冻令覆盖）→ ARCHIVE_OPERATOR_HARNESS.md「归档 2026-11-20」节；护栏定义已由 16:3x 令 Step 1 落地。需要时再读。

### 🔴 用户令 · 2026-11-20 08:2x（**限制 CPU 占用·.29+.12 均摊**）· ✅ 已闭环（CPU 节流 LIVE·Phase 0 验收通过）→ ARCHIVE_OPERATOR_HARNESS.md「归档 2026-11-20」节；结论：loop 受控(nice19/ionice3/OMP8/load闸120)·pretrain step 7.28s≤7.4s✅。需要时再读。

### ✅ 用户令 · 2026-11-19（**SWE-bench Verified 报告重写**）· 用户直令 · ✅ 已交付（R2758）

> **交付结论（R2758 · 2026-11-19 11:4x）**：报告 `report_harness_glm53_7way_swebench_tb_zh.html` 已重写（23748→4840B）。①★主表 SWE-bench Verified 7路置顶·Pass%=resolved/500·单数字无区间无~·按降序：hermes444/500=88.8%·opencode415/500=83.0%·cline296/500=59.2%·cc295/500=59.0%·pi235/500=47.0%·deepseek168/500=33.6%·codex108/500=21.6%。②删 Terminal-Bench表/ETA/磁盘/kimi对比。③保留 predict进度+待跑backlog(deepseek241/codex109/pi95/cline40)+待重跑infra(pi1+codex1)。④生成器 `gen_report_glm53_7way.py` 重写(537→162行)·footer stray text已清。0script/0外链✅。

> 🔴 **用户令 · 2026-11-19 — SWE-bench Multimodal 2×3 评测（排队，MM 容器下载完后启动）**

> **用户原话**：「SWE-bench Multimodal 下载完后，起如下的 2x3 评测。2 个 harness：cline+opencode。3 个 LLM：DeepSeek-V4-flash、Kimi-K2.6 和 Doubao」

> **评测矩阵（2 harness × 3 LLM = 6 路）**：

> | Harness | LLM | API key | Base URL | Model |
> |:--|:--|:--|:--|:--|
> | cline | DeepSeek-V4-flash | `02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3` | `http://agi-gateway.cxmt.com/v1` | `deepseek-v4-flash` |
> | cline | Kimi-K2.6 | `02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f` | `http://agi-gateway.cxmt.com/cloud/v1` | `kimi-k2.6-cloud` |
> | cline | Doubao | `02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f` | `http://agi-gateway.cxmt.com/cloud/v1` | `doubao-seed-2.0-pro-cloud` |
> | opencode | DeepSeek-V4-flash | 同上 | 同上 | 同上 |
> | opencode | Kimi-K2.6 | 同上 | 同上 | 同上 |
> | opencode | Doubao | 同上 | 同上 | 同上 |

> **排队条件**：SWE-bench Multimodal 容器下载完成（✅ 580/580=100% · 2026-11-19 12:14 · 0 FAILED）后启动。不抢 pretrain CPU。**→ 2×3 predict 已于 R2763 14:56 启动（6 路全 RUN，nice19/ionice3）。**

> ✅ **用户令 · 2026-11-18 — 下载 SWE-bench Multimodal 评测容器（最高优先）· ✅ 已交付（R2763）**

> **用户原话**：「一边补 SWE-bench Verified 评测，一边下载 SWE-bench Multimodal 的评测容器」

> **指令**：在继续补 SWE-bench Verified 评测的同时，并行下载 SWE-bench Multimodal 的评测容器。不要影响 pretrain 训练吞吐（nice19/ionice3，不抢 .29 CPU）。

> **交付结论（R2763 · 2026-11-19 14:5x）**：MM 容器下载 **COMPLETE**——`pull_state.txt`=580、`pull_progress.log` 末行 `=== DOWNLOAD COMPLETE === Total: 580 | Pulled: 580 | Skipped: 0 | Failed: 0`（2026-11-19 12:14:49）。全程 nice19/ionice=idle、不抢 .29 CPU✅。SWE-bench Verified 评测并行补跑未中断（4 路 predict alive）。下载产物落 `run/harness/swebench_mm/`（images/instances/test.parquet/dev.parquet，均 gitignored 机器产物）。

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

> 📦 §用户令·2026-11-19 08:2x（重新输出两份7way报告主表置顶）**✅ 已交付（R2751）** → run/ARCHIVE_OPERATOR_HARNESS.md「归档 2026-11-19」节；**结论**：两份中文HTML主表置顶✅·TB-2.1 7路opencode50.6/cline47.2/hermes46.1/pi39.3/cc33.7/codex28.1/deepseek12.4·SWE-bench Verified hermes88.8/opencode83.0/cc59.0/cline58.4/pi46.6/deepseek33.2/codex21.6。需要时再读。

> 📦 §用户令·2026-11-18 10:3x（ability桶拆两层）**✅ 已交付（R2664）** → run/ARCHIVE_OPERATOR_HARNESS.md「归档 2026-11-19」节；**结论**：layer-A真能力/layer-B infra嫌疑(6子桶)·93题layer-B: 66题infra+9题ability_lean+18题ambiguous·deepseek12.4%上界52.8%·hermes46.1%上界69.7%。需要时再读。

### ✅ 用户令 · 2026-11-17 14:5x（**修复 codex 适配器假低分 + 重跑**）· 用户直令 · ✅ 已交付（R2661）

> **交付结论**：codex.py 修复①（exit-code非0不误杀·解析stdout NDJSON·agent_worked→verifier照常判分）+ ②（429退避重试2/4/8/16s上限4次）+ ③（turn.failed记录与适配器掐断分开归类）均已实现并验证。全部89题重跑COMPLETE（83题第一轮+55题第三轮·网关已清）+merge→**codex 25/89=28.1%**（从修复前1/89=1.1%回升✅fix①生效）。audit_tb21_review_7way.py 已同步修正（codex_agent_worked&&!has_verifier→rate_limit=infra·lines169-180）。三报告codex行已更新为「修复前1/89=1.1%系适配器假低分（82题被exit-code误杀），修复重跑后25/89=28.1%」。心跳第一行已给：codex 修复重跑后新 Pass%=28.1%。

---

### ✅ 用户令 · 2026-11-17 10:2x（**纠正归因口径：未真跑题必须重跑，不得「剔除分母假设计入」**）· 用户直令 · ✅ 已交付（R2661）

> **交付结论**：「修正后 Pass%」已从两份报告撤回（仅保留口径纠正声明）。全部7路 infra/synthetic/quota/conn_refused 题已全部重跑COMPLETE（待重跑=0）。真实 Pass% = passed/89（分母恒89）已为最终值：cline 42/89=47.2% · **codex 25/89=28.1%**（从1/89=1.1%回升✅fix①生效） · opencode 45/89=50.6% · cc 30/89=33.7% · pi 35/89=39.3% · hermes 41/89=46.1% · deepseek 11/89=12.4%。BLOCKED(infra) 硬约束题（hermes qemu/mteb Py3.9<3.11·cline pytorch-model-recovery CLI崩溃3attempts）显式注明原因、单列不误算为通过。能力题重跑仍fail已计为fail。两报告「失败归因复核」节已改为「重跑完成」真实口径。心跳第一行已给：撤回修正后Pass%声明+各路真实Pass%。

---

> 📦 §用户令·2026-11-17 08:5x（复核 7-way 失败 case：是否均为能力不足）**✅ 已交付（R2600）** → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：合并 original+rerun 后四桶归因——TB-2.1 修正后 Pass%: cline47.2→47.7%(inf1) · codex1.1→1.1%(inf2·86ability=真能力) · opencode48.3→54.4%(inf10) · cc33.7→34.1%(inf1) · pi39.3→47.3%(inf15) · hermes42.7→50.0%(inf13) · deepseek12.4→13.1%(inf5) · SWE-bench patch非空率98%+→失败为能力非infra · 新增 `audit_tb21_review_7way.py` + 两报告新增§失败归因复核 · 0 script/0外链✅。需要时再读。

---

> 📦 §用户令·2026-11-17 08:2x（交付 TB-2.1 + SWE-bench Verified 两份 7-way 中文 HTML 报告）**✅ 已交付（R2598·commit e09da6fd2）** → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：两份报告已交付(①`report_harness_glm53_7way_swebench_tb_zh.html`·SWE-bench Verified 500+TB-2.1 89×7路·13.1KB ②`report_harness_tb21_7way_zh.html`·TB-2.1 7路专项·10.6KB)·TB-2.1 7路=opencode48.3/cline47.2/hermes42.7/pi39.3/cc33.7/deepseek12.4/codex1.1·SWE-bench进行中/partial(cline249/332·codex91/144·opencode414/498·cc286/348·pi216/296·hermes435/480·deepseek141/175)·0 script/0外链✅·porcelain=0✅·combined生成器TB计数bug已修(task_name去重+扫rerun dir+PASS优先)。需要时再读。

---

> ✅ **用户令 · 2026-11-15 10:2x（并发放量 + 429 自适应回退）· 已交付+验收4/4通过(R2512)+实跑验证(R2503-R2593·cc/opencode/hermes rerun 均用 adaptive auto·0 累计429)**
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

> 📦 §用户令·2026-11-14 09:3x（修复 claude-code ConnectionRefused → 重测 TB-2.1 89 题）**✅ 已交付（R2593）** → ARCHIVE_OPERATOR_HARNESS.md；**结论**：cc修复 COMPLETE 30/89=33.7%(R1+R2 merged·0ConnRefused✅HARD VERIFIED)·根因=容器内127.0.0.1指向容器自身·修复=overlay network_mode:host·冒烟=OK·4报告全REGEN(cc归因/7way/cline_special/glm53_7way)·7way:opencode48.3/cline47.2/hermes42.7/pi39.3/cc33.7/deepseek12.4/codex1.1。需要时再读。

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

