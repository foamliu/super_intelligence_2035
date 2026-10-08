# BAIZE_HARNESS_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_HARNESS.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。
> 运行时状态写 `MEMORY_HARNESS.md` / `daily-memories-harness/` / `harness/`（产物）。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_HARNESS.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**。本节为「无」时，按下方默认顺序自主推进。
### 🆕 运维指令 · 2026-10-08⑦（📋 **R2 口径披露 ＋ 并发变更追认 ＋ 报告落位**）· 高优先

> **已收到 R187**（`f85f6332`）：② 轨迹报告 ✅ 交付（38307B / 7 节 / 5 SVG；**诚实声明 per-turn 轨迹仅 `stdout_tail` 存活、完整轨迹需重跑** —— 这点做得对）· ① Round-2 已起跑（100 = **30 R1 + 70 stratified**，**含首轮 30** ⇒ 可比 ✅）· ④ 已归档。

**⚠️ 一处程序偏差（予以追认，但必须留痕）**：⑤ 写明「**若为压缩 ETA 想改并发 ⇒ 先报方案，不得擅自改口径**」，而你在**未先报方案**的情况下把 7 个 harness 改成**全并行**（serial=1 → 7 路并发），ETA 从 ~110h 压到 ~10h。
- ✅ **决定：追认**（11× 收益太大；7 个 harness 处于**同一并发条件**，轮内公平性不破）。
- ❗**但由此产生两条「口径事实」，必须写进最终报告**：
  1. **跨轮不可严格比**：首轮 = **serial=1**、本轮 = **7 路并行** ⇒ 网关限流 / 超时 / 沙箱争用条件不同；且**本轮 30 条 R1 实例是 `--resume` 复用的首轮（串行）结果**，**70 条新题才是本轮并行结果** ⇒ **同一张 7×100 表里混了两种运行条件** —— **必须在表头/脚注标明「哪 30 行是复用、哪 70 行是新跑」**。
  2. **必须监控并报告**：本轮 **`quota-blocked` / `timeout` / `no-patch` 率** vs 首轮**同 30 条** —— **若显著上升 ⇒ 判「并行污染」，相应结论要打折**。

**你要做的（本轮内完成，不必停链）**
1. 在 `MEMORY_HARNESS.md` ＋ 最终报告**显式新增一节「口径与并发」**（串行 vs 并行 · 30 条复用 · 上述监控指标对比）——**不许只在对话里说**。
2. **把 `report_harness_interaction_traces.html` 补一份到 `doc/BaiZe-ISEDA2027/` 根目录**（与其它线报告一致；你现有那份只在 `run/harness/`）。
3. 每完成一个 harness 即刷新 `SWEBENCH_COMPARE.html`（照旧），并**在表里加「复用 / 新跑」标记列**。

**纪律不变**：模型 `kimi-k2.6-cloud` · 同沙箱 · 同 `PreToolUse`/anti-cheat · 同判据；🚫 不删 `kimi_pilot_results.json`；🚫 不 `git add -A`；收尾 commit+push（前缀 `harness R<N>: …`）。
> 📦 体积：加块后自检 `wc -c`，>32KB 先归档已闭合旧块。


### 🆕 运维指令 · 2026-10-08⑤（**① 启动第二轮 7×100 横评 ② 深挖第一轮 7×30 的「交互轨迹」→ 列表对比各 harness 特点**）· **用户直令** · 最高优先

> **用户令（2026-10-08 晚）**：「**① 启动第二轮 7×100 横评；② 深入分析第一轮 7×30 横评的交互轨迹，列表对比各 harness 的特点。**」
> 现状（运维已核）：7-way × 30 全完成（cline-patched 60.0% · Pi 60.0% · Hermes 53.3% · opencode 50.0% · codex 46.7% · claude-code 43.3% · deepseek-harness 40.0%），**无运行中 chain**。数据 = `run/harness/kimi_pilot_results.json`（480 entries）。

**① 第二轮：7 harness × 100 条（同一固定题集）**
- **题集**：**固定 100 条 SWE-bench Lite**，**7 个 harness 全部跑同一份**（🚫 不许各自换题）。**选法先写进 MEMORY 再跑**，给**可复现的选取规则**（如按 `instance_id` 排序取前 100，或 django/sympy 各 N 条…），并**明确标注是否包含第一轮的 30 条**（**建议包含** ⇒ 两轮直接可比）。
- **口径必须与第一轮逐字一致**（否则两轮不可比）：同 backbone `kimi-k2.6-cloud`、**同并发设置**、同沙箱、同 `PreToolUse`/anti-cheat、同判据。**若为压缩 ETA 想改并发 ⇒ 先报方案，不得擅自改口径。**
- **7 harness**：`cline-patched` · `codex` · `opencode` · `claude-code` · `deepseek-harness` · `pi` · `hermes`。
- **⭐ 先报 ETA 再全速跑**：第一轮 210 run ≈ 34h 串行 ⇒ 700 run 同速 ≈ **4.5–5 天**。**第一个动作 = 用实测 s/inst 算总 ETA 并写进心跳**；然后 `--resume` 增量跑，**每完成一个 harness 即刷新 + commit**。
- **交付**：`SWEBENCH_COMPARE.html` → **7 行 × 100 条** + 汇总表（scored/resolved/pbf/quota-blocked/rate）+ 口径表。
- **铁律**：🚫 不删 `kimi_pilot_results.json`（保留第一轮 210 entries，可 `--resume`）；🚫 不打断正在跑的 chain。

**② 深挖第一轮「交互轨迹」+ 逐 harness 特点对比表（纯 CPU，本块先做）**
- **数据源**：`kimi_pilot_results.json` 的 `harness_result` 字段（已知含 `stdout_tail` / `eval` / `wall_s` / `returncode`）。**第一件事 = 盘点「轨迹还剩多少」**：逐字段列可用信息；**若完整逐轮交互（每轮 prompt/工具调用/输出）已被 `/dev/shm` 清掉 ⇒ 如实写「仅 `stdout_tail` 可用 / 需重跑才有完整轨迹」**（🚫 不得猜、不得编）。
- **产出 A**：**7 行 × N 列「harness 特点对比表」**（HTML，house style，内联 SVG，零外链，≤200KB）。列建议：**启动方式/入口 · 交互轮次与自主性 · 工具调用风格与频次 · 是否用执行反馈闭环 · 平均 `wall_s` · 典型失败模式 · patch 规模 · resolved 率**。**每格数字/结论须可由 JSON 或源码 `path:line` 复算**。
- **产出 B**：回答「**为何同 backbone 下差 20pp（40.0%–60.0%）？是 harness 架构差异，还是交互轨迹差异？**」——**证据化**归因，不许泛泛。
- **交付**：`report_harness_interaction_traces.html`（新）+ 刷新 `HARNESS_7WAY_COMPARISON.html` 相关节。

**顺序**：**② 先做**（纯 CPU/写作，不占串行槽）→ **① 同步报 ETA 并起跑**（后台 `--resume` 增量）。
**收尾**：按「收尾铁律」commit+push（前缀 `harness R<N>: …`）+ 心跳 + WAITING=1。🚫 不 `git add -A`。
> 📦 体积提醒：本块加入后请先 `wc -c` 自检，>32KB 先归档已闭合旧块再提交。


> 📦 §运维指令·2026-10-08④（下一步工作建议 Q&A）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：Q1–Q4 已在 R184 回答（commit 27859f2e），写进 MEMORY_HARNESS.md「运维问答」小节。需要时再读。


> 📦 §运维指令·2026-10-08（📄 SWE-bench 横评分析报告 HTML）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：report_harness_swebench_analysis.html 已交付（75647B, 9 sections + §4.5, 10 inline SVG, 自包含 ≤200KB）。需要时再读。


### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**（「收尾铁律」第 0 步已同步此判据）。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）**原文**搬入 `run/ARCHIVE_OPERATOR_HARNESS.md` / `run/ARCHIVE_HARNESS_SPEC_HISTORY.md`（无则新建）/ `daily-memories-harness/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `harness 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**32KB**（已贴上限）⇒ **下次唤醒先归档到 ≤32KB**，并把 `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB）` 抄进心跳。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> **为什么新增（真实事故）**：2026-10-06 06:55 → 08:30，**data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新**（其间 agent 在改别的文件、push 得出去），**外部运维只能靠 git 判断死活** ⇒ 被**误判成静默卡死并上机排查**。
> 根因：**「更新记忆 + push」以前只是建议、没有硬约束**；loop 的兜底 push 间隔是 **5h**（本日已缩短），且只覆盖固定白名单 —— **不许依赖兜底**。
> 🚫 **旧口径（已废）**：「每 5 小时由 loop 兜底同步一次」**不再作为交付保障** —— 兜底只是保险丝，**不是你的提交手段**。

**每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：**

0. **体积自检（先跑，数字要抄进下一步的心跳）**：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 **≤ 32KB**；**任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档**（见本文件「📉 体积维护规程」：只把**已闭合**内容**原文**移入 `run/ARCHIVE_OPERATOR_HARNESS.md`、留 1 行指针），直到两者都 ≤ 32KB；**> 40KB（红线）⇒ 必须先归档再提交**（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_HARNESS.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. **写心跳**：更新 `run/MEMORY_HARNESS.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并**追加 1 行「本唤醒流水」**：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories-harness/<YYYY-MM-DD>.md` 追加本轮记录（**当天文件必须建**）。
3. **自己提交 + 推送**（**不许等 loop 兜底**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md \
              doc/BaiZe-ISEDA2027/run/harness doc/BaiZe-ISEDA2027/run/daily-memories-harness
   git commit -m "harness R<N>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 **绝不用 `git add -A`** —— 这是**共享工作副本**，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是**提交归属不可溯**（运维查不出谁在干活）。
4. **闭环自检**：`git status -sb` ⇒ **无 ahead / 无 behind**；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   **push 失败（`error: Forbidden` / 网络）**：重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下一轮唤醒第一件事就是补推**。

> ⏱️ **运维判死判据（硬）**：**心跳文件 >60 min 无新提交 ⇒ 按卡死处理**，**不再等你**。**你干得再多，心跳不动 = 仍会被判死。**
> 📦 §运维口径（2026-10-05 深夜4 · Claude Code 合规口径）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：遥测已关、claude-code 已恢复横评。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · 授权自装 deepseek-harness 工具链）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：node22+rust 已装、deepseek-harness 已 build，待并入横评。需要时再读。

> 📦 §运维指令·2026-10-07（📊 昨夜工作汇报 HTML）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：report_10_07_harness_overnight.html 已交付（27187B，自包含内联SVG，R118→R134，codex 43/96/161，总 resolved 61）。需要时再读。

> 📦 §运维指令·2026-10-07⑥（7-way: Hermes + Pi）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：7-way 横评全完成（cline-patched 60.0% · Pi 60.0% · Hermes 53.3% · opencode 50.0% · codex 46.7% · claude-code 43.3% · deepseek-harness 40.0%）。需要时再读。


> 📦 §运维指令·2026-10-07（30 × 5 harness 横评）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：5-way 横评完成（cline-patched 18/30, codex 14/30, opencode 7/30, claude-code 19/30, deepseek-harness 进行中 22/30）。已被 10-07⑥「7-way」取代。需要时再读。


> 📦 §运维指令·2026-10-05（晚 · 扩 300）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：被 10-07「先做 30 横评」取代。需要时再读。


### 🆕 运维口径 · 2026-10-05（**你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测**）

> **定位（运维 2026-10-05 13:2x，跨线）**：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（见 `baize_data_loop.sh:114-120` / `baize_harness_loop.sh:106-116`）——**目的是给内网网关鉴权**（不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ **你（agent）会话里每条命令都继承了「无代理」env。**
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 **`Network is unreachable`（Errno 101）/ http `000`** 是**预期现象**：🚫 **不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题**——**别把它写进结论**。
> 🔧 **正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）**：**凡访问外网的那一条命令，自己显式带上代理**（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都**不要**带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> ✅ **同机反证**：`run/harness/r1_eval.py:144-148` 正是**显式钉 proxy + 阿里云索引**，所以**同一台 `.29`** 上 pip 装包一直成功；relay 侧 git 也通（`run/ops/outbox.md` RUN_ID 28：「外网 无 proxy=FAIL / 有 proxy=OK」，内网网关两种都 200）。
> 🚫 **装包别动共享 py310 env**（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令·2026-10-05（🔄 横评换「冷门模型」+ 严格串行）已归档 → run/ARCHIVE_OPERATOR_HARNESS.md；**结论**：已切换 kimi-k2.6-cloud + 串行=1 + quota 三列报告，被 2026-10-07「30×5」块取代。需要时再读。

### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` **都每次唤醒被全文读进 prompt**（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_HARNESS_TASK.md` ≈ **30KB**、`MEMORY_HARNESS.md` ≈ **30KB**（**两者都已贴上限**）。
- **上限（两者相同）**：**≤ 32KB**；**红线 40KB** ⇒ **超红线当轮必须先归档才能收尾**。
- **自检**：见「收尾铁律」第 0 条（`wc -c` 两文件，**数字抄进心跳**）。
- **归档去向（只归档「历史」，🚫 不许归档「活口径」）**：
  ① 已执行完/已作废的**运维指令块** → `run/ARCHIVE_OPERATOR_HARNESS.md`（**留下 1 行指针**）；
  ② 被取代的**候选表/推导过程**（保留现行档 + 实测结果） → `run/ARCHIVE_HARNESS_SPEC_HISTORY.md`（无则新建）；
  ③ 较早的**巡检条目**（保留最近 ~20 条） → `daily-memories-harness/<条目日期>.md`（原文不改）。
- 🚫 **不许归档**：硬规则 / 验收标准 / **现行口径** / `WAITING:` 状态头 / 「运维问答」区。
- 指针（**必须留、只 1 行**）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 **不许改小节编号/标题**（别处有交叉引用）。
- **谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）**：`MEMORY_*.md` 一直由 agent 自滚，**任务书同理** —— **本线 agent 自己**把「已闭合」内容**原文**移入对应归档文件、留 1 行指针。⚠️ **本文件「agent 只读」的唯一例外 = 仅此「搬迁」**：原文一字不改、不动小节编号/标题、**不新增/不改写任何运维指令**（本区作者仍是运维）。**并发安全**：归档前先 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `<线> 归档: …` 前缀。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 ③ 「运维问答」④ 最近 ~20 条。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---



| 项 | 当前值 |
|:---|:---|
| **当前指令** | 🎯 **（2026-10-02 首启）两条线，按序做**：<br>**① H-B 源码分析（先开始）** —— 分析 `/nas_train/app.e0031982/harness` 下各 harness 的源码，**从 cline 开始**，产出**自包含 HTML 报告**。分析主线见 §2。<br>**② H-A SWE-bench 横评** —— 用 **SWE-bench** 评测几个 agent harness（cline / opencode / deepseek harness 等）并**对比**。⚠️ **先做可行性核查（§1.1），再定规模**，不要一上来跑全量。<br>🚫 **两条铁律**：<b>不许猜</b>（源码结论必须贴文件+行号原文）；<b>每个结论必须可复现</b>（命令+输出）。 |
| **优先级覆盖** | **H-B（源码分析）> H-A（SWE-bench）**；<br>H-A 只在**环境与数据集核查通过后**才进入实跑。 |
| **状态索取** | `<无>`（若运维写入具体问题，本轮**先答该问题**再干活，答案写进 `MEMORY_HARNESS.md` 顶部「运维问答」区） |
| **暂停标志** | `<无>`（若写入 `STOP`，本轮**只更新记忆、不做任何动作**，然后退出） |

---

## 📊 进度快照（**每次唤醒必须更新**，供远程巡检）

> 固定格式写在 **`MEMORY_HARNESS.md` 最顶部**，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ **`WAITING` 只写在 `MEMORY_HARNESS.md` 的顶部单独一行**
（`baize_harness_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
**绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行** —— 否则会误触发 30 分钟长睡。

**运维巡检方式**：外部运维 `git pull` 读 `MEMORY_HARNESS.md` 顶部 + `harness/` 下的报告即可，**不需要登录服务器**。

---

## 0. 任务概述

**目的**：横向理解「agent harness」这一类系统 —— **它们的工程实现差异**，以及**它们在真实软件工程任务上的能力差异**。

| 线 | 内容 | 产出 |
|:--|:--|:--|
| **H-B** | **源码分析**（从 **cline** 开始） | `harness/<name>_SOURCE_ANALYSIS.html`（自包含） |
| **H-A** | **SWE-bench 横评**（cline / opencode / deepseek harness 等） | `harness/SWEBENCH_COMPARE.html` + 结果表 |

**代码位置**：`/nas_train/app.e0031982/harness/`

> ## 🔍 **重要：该目录下已存在一条「同类研究线」（运维 2026-10-02 指示：可以合并）**
>
> 首次勘察（RUN_ID 5）发现 `/nas_train/app.e0031982/harness/` 里**不只有 5 个 harness 源码**，还有：
> ```
> claude-code/  cline/  codex/  deepseek-harness/  opencode/     ← 5 个 harness
> loop.sh                                                          ← 它自己的 loop
> MEMORY.md                                                        ← 它自己的状态文件
> daily-memories/  evidence/  mechanisms/                          ← 它自己的记忆与证据目录
> analyze_harness_sources.md   (11.8 KB)                           ← 已有源码分析文档
> report.html                  (24.6 KB)                           ← 已有报告
> ```
> **文件日期为 Sep 4 – Sep 15**，**早于本线创建（Oct 2）**，**非本线产物**。
>
> ### ✅ 运维确认 + 指示（2026-10-02）
> - **运维确认**：**9 月初确实下发过一次「5 个 harness 比较」的任务**（就是这条线）；
> - **⚠️ 它的 `loop.sh` 早已停掉** → **不会与我们冲突**，也**不要**去重启它；
> - **指示：可以合并**。
>
> **→ 所以它的产物是「纯输入」**：`analyze_harness_sources.md` / `report.html` / `evidence/` / `mechanisms/`
> 都是**可复用的既有素材**，但**其结论需要按我们的 5 条主线重新审视**（它的分析角度可能不同）。
>
> **你要做的（H-B 开始前先做）**：
> 1. **先把这条既有线的家底摸清**（**只读**，不要改动它）：
>    - `MEMORY.md`：它的 PHASE / 已完成 / 产出
>    - `loop.sh`：它跑什么、是否还在运行（`pgrep -af 'harness/loop.sh'`）
>    - `analyze_harness_sources.md`：已有的分析**到什么程度**
>    - `report.html`：已有报告**覆盖什么**
>    - `evidence/` `mechanisms/`：已有的证据与机制梳理
> 2. **出一份「重合与差异对照表」**：它的产出 vs 本任务书 §2.2 的 5 条主线 ——
>    **哪些已经做过（可直接引用）· 哪些做了但不符合我们的分析要求（需重做）· 哪些完全没做（我们的增量）**。
> 3. **产出统一落到本线的 `harness/` 目录**（`doc/BaiZe-ISEDA2027/run/harness/`），
>    **旧的 `report.html` / `analyze_harness_sources.md` 作为输入引用**（给出路径）。
> 4. ⚠️ **不要删、不要改** `/nas_train/app.e0031982/harness/` 里的任何东西 ——
>    **合并 = 在我们这边整合，不是去动它的目录**。
> 5. 🚫 **不要**去启动它的 `loop.sh`（避免两个同类 loop 抢 token）。


---

## 1. H-A —— SWE-bench 横评

### 1.1 🔴 第 0 步（**必做，先做**）：可行性核查

**在跑任何评测之前**，逐条查清并**报给运维**：

| # | 查什么 | 怎么查 |
|:--|:--|:--|
| 1 | `harness/` 下**有哪些 harness**、各自**版本 / 形态**（CLI？插件？）| `ls -la` + 各自 `README` / `package.json` / `pyproject.toml` |
| 2 | 每个 harness **怎么启动**、**接什么模型**（是否要 API key、能否接本地模型）| 读文档 + 试 `--help` |
| 3 | **模型可用性**：本机能调哪些模型？（DeepSeek API？本地 vLLM？）| 实测一次最小调用 |
| 4 | **SWE-bench 数据集**：能否取到？取哪个子集？ | `swebench` 包 / HF 数据集；**建议先 `SWE-bench Lite`(300) 或再抽 50 条** |
| 5 | **评测容器 / 沙箱**：见下方「§1.1-bis 无 Docker 路线」 | `docker info`；**不可用就按 §1.1-bis 改道** |
| 6 | **磁盘/时长预估**：跑 N 条大概要多久、多少磁盘 | 按单条实测反推 |

🚫 **第 0 步没通过之前，不许"假装跑了"或"用其他指标冒充 SWE-bench"** —— 如实报告阻塞。

### 1.1-bis ⚠️ **无 Docker 路线（运维 2026-10-02 明确：公司内网无法 `docker pull`）**

> **已查实的事实（官方仓库原文）**：
> - SWE-bench 官方 harness **默认绑 Docker**（README：「SWE-bench uses **Docker** for reproducible evaluations」；
>   2024-06-27 起改为「**fully containerized** evaluation harness using Docker」）。
> - **官方唯一的"无 Docker"本地后端是 Modal（云）**：`--modal true` —— 但要外网。
> - **`SWE-ReX`**（SWE-agent 家族）支持 **local / remote / Docker / Modal 等后端**，
>   原文：「…executed **locally** or remotely in Docker containers, AWS remote machines, Modal, or something else…」+
>   「Support a broad range of platforms, **including non-Linux machines without Docker**」。
> - 🚫 **`SWE-MiniSandbox`** —— **在官方仓库中未找到该名称**。**请自行查证**（有就给 URL + 它解决什么）；**查不到就写"未找到"，不要猜**。

> ### 🔑 关键认知：Docker 在这里**不只是"隔离"，更是"per-instance 依赖环境的分发机制"**
> 每个 instance 一个**预构建镜像**，装着**该 repo 在该 `base_commit` 下正确的依赖**。
> **换掉"隔离"很容易**（bwrap / nsjail / local）；**换掉"环境供应链"很难**。

---

#### ⭐ 第 0 步（**先做**）：**连通性测试 —— 分清「事实」与「推测」**

> ### ⚠️ 运维更正（2026-10-02）：**github 是可达的**
> **`.29` / `.12` 都能从 github `git clone` 代码** —— **本任务线用于发布任务的仓库本身就在 github 上**，
> 所有 agent 的 `git fetch/pull/push` **一直正常**。
> → **不要把"github 不可达"当作前提**（那是把"爬取层面不可达"错当成了"git 不可达"）。
>
> ### 🔑 还必须分清另外两件**被我混淆过**的事
> | | 实际状态 | 依据 |
> |:--|:--|:--|
> | **`docker` 命令可用吗** | ❌ **不可用**（`docker info` → `NOT AVAILABLE`）| **实测（RUN_ID 5）** |
> | **能不能 `docker pull`** | ❓ **从未测过** | **此前只是推测，不要当事实** |
> → **"没装 Docker" 与 "装了也 pull 不到镜像" 是两件完全不同的事**，**都要实测**。

**要测的清单（逐条记 `http_code` 或错误原文）**

```bash
echo "=== A. GitHub（已知可达，复核 git 通道） ==="
timeout 20 git ls-remote https://github.com/SWE-bench/SWE-bench.git HEAD 2>&1 | head -2

echo "=== B. 依赖源（E′ 的关键待验项） ==="
for u in https://pypi.org/simple/ https://files.pythonhosted.org/ ; do
  printf '%-38s : ' "$u"; curl -sS -m 10 -o /dev/null -w '%{http_code}\n' "$u" 2>&1 | tail -1
done
# 内网镜像？（替换成你们实际的内网源）
pip config list 2>/dev/null; cat /etc/pip.conf ~/.pip/pip.conf ~/.config/pip/pip.conf 2>/dev/null

echo "=== C. Docker 相关（注意：docker 命令本身当前不可用） ==="
which docker dockerd podman nerdctl 2>/dev/null || echo "(no docker/podman CLI)"
curl -sS -m 10 -o /dev/null -w 'registry-1.docker.io : %{http_code}\n' https://registry-1.docker.io/v2/ 2>&1 | tail -1
curl -sS -m 10 -o /dev/null -w 'ghcr.io             : %{http_code}\n' https://ghcr.io/v2/ 2>&1 | tail -1

echo "=== D. SWE-bench 云（sb-cli 的命门） ==="
for u in https://api.swebench.com/ https://www.swebench.com/ ; do
  printf '%-38s : ' "$u"; curl -sS -m 10 -o /dev/null -w '%{http_code}\n' "$u" 2>&1 | tail -1
done
timeout 60 pip download sb-cli -d /tmp/sbcli_probe --no-deps 2>&1 | tail -3
```

**判定（据此选路线）**
| 测试结果 | 结论 |
|:--|:--|
| **B（pypi/内网镜像）通** | ✅ **E′ 完全可行** —— `git clone`（已成立）+ 装依赖 → 不需要 Docker |
| **C 里能看到内网 registry 或 `docker pull` 成功** | ✅ 原路可行（最省事） |
| **D 通（且合规批准）** | ✅ sb-cli 可用 → 给最强 harness 拿标准分数 |
| **B/C/D 全不通** | ⚠️ 才需要考虑自建沙箱 / 换口径 |

#### 🚫 关于 sb-cli 的合规红线（**必须先确认，再上传任何东西**）

`sb-cli` 的工作方式是 **把 `predictions.json`（含 `model_patch`）上传到 SWE-bench 云端评测**。
- ✅ **缓解**：patch 针对的是**开源 repo**（django / sympy 等），**不是我们的私有代码**。
- ⚠️ **但**：**这是把代码片段发到外部服务** —— **公司政策可能不允许**。
- **→ 要求**：**上传前必须由运维/合规确认**。**未经确认，不得使用 sb-cli 上传任何东西。**
- 📌 另：sb-cli 需要**邮箱 + 邮件验证码**注册（`sb-cli gen-api-key <email>` → `verify-api-key <code>`），
  且**有配额**（`sb-cli quota <subset> <split>`）—— 这两条也要先记下来。

---

#### 路线优先级（**连通性测试之后**据此执行）

1. **若 `docker pull` 实测可行**（或内网有 Harbor 镜像代理）→ **原路最省事**（写清证据）。
2. **⭐ 路线 E′（推荐）：只挑 1–3 个高频 repo 的 instance**
   - 统计 `SWE-bench Lite`(300) 的 **repo 分布** → 挑**占比最高的 1–3 个 repo**。
   - **`git clone` 该 repo @ `base_commit`**（✅ github 已确认可达）+ **装该 repo 的依赖**（待验 pypi/内网镜像）。
   - 几个 harness 跑**同一批 instance** → **公平横评成立**。
   - ⚠️ **报告里必须标注**：这是**内部横评口径**，**不是标准 SWE-bench 分数，不能与 leaderboard 直接比**。
   - 💡 **加强版**：`SWE-bench` 仓库里带着**每个 instance 的镜像构建规格**（`swebench/harness/`）——
     **可直接照规格 build env**，完全绕开 Docker Hub。
3. **路线 sn（若 D 通 且 合规批准）：`sb-cli`** —— 给最强 harness 拿**与 leaderboard 可比**的标准分数。
4. **备选：自建轻量沙箱** —— `conda env per repo` + **`bwrap` / `nsjail`**（只替代"隔离"职责）。
5. **若以上都不可行** → 明确写"**H-A 在受限前提下无法按标准口径进行**"，
   并给**替代评测口径**建议，**但不得把它称作 SWE-bench 结果**。







### 1.2 评测设计（**核查通过后**）

1. **统一口径**（否则不可比）：
   - **同一子集**（同一批 instance_id）
   - **同一模型**（同一 provider / 同一 checkpoint）
   - **同一 timeout**、**同一 max turns / 预算**
   - **同一评测脚本**（SWE-bench 官方 harness）
2. **规模**：**先 20–50 条**跑通全流程 → 报初步结果 → **再由运维决定是否放大**。
3. **每个 harness 报**：`resolve rate（主）` · `平均轮数` · `平均 token` · `平均墙钟` · `成本` · `失败模式分类`
4. **诚实性**：失败的实例要**保留日志**；**不许只报成功案例**。

### 1.3 H-A 交付物
1. `harness/SWEBENCH_COMPARE.html`（自包含：口径 · 结果表 · 每个 harness 的失败模式 · 原始日志路径）
2. `harness/swebench_runs/`（原始预测 patch + 评测输出，**不入库**）
3. `MEMORY_HARNESS.md` 记录**可复现命令**

---
## 3. 约束

- **仓库与产物**：分析产物写 `doc/BaiZe-ISEDA2027/run/harness/`（**文本 md/html 入库**）；
  **原始仓库副本 / 大数据 / 日志不入库**。
- **共享工作副本**：`run/` 是**多 agent 共享**的（vision / pretrain / data 也在用）——
  🚫 **不要 `git add -A`**，只提交本任务的 `harness/` 与 `MEMORY_HARNESS.md`、`daily-memories-harness/`。
- **git 规则**：push 前**先 `fetch` + `pull --rebase --autostash`**（照抄 `baize_data_loop.sh` 的做法）。
- **资源**：SWE-bench 评测可能**很吃 CPU/磁盘/Docker** —— **先报预算再跑**，
  ⚠️ 注意 `.12`/`.29` 上另有训练在下（见 `AGENTS.md`），**重 I/O 要避让**。
- 🚫 **不碰**其他 agent 的任务书与记忆文件。
- **诚实**：**没跑通就写没跑通**；**没查到就写没查到**。**不要编造 API 行为。**

---

## 4. 记忆管理

- `run/MEMORY_HARNESS.md` — 运行时状态（PHASE / WAITING / ERROR_COUNT / 看板 / 流水）
- `run/daily-memories-harness/$(date +%F).md` — 当日操作日志
- `run/harness/` — 分析报告与（不入库的）运行产物

启动恢复：读 `MEMORY_HARNESS.md` → 当日日志 → 判断下一步 → 执行 → 回写。



