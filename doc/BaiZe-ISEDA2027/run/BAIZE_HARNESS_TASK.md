# BAIZE_HARNESS_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_HARNESS.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。
> 运行时状态写 `MEMORY_HARNESS.md` / `daily-memories-harness/` / `harness/`（产物）。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_HARNESS.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**。本节为「无」时，按下方默认顺序自主推进。

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

### 🆕 运维指令 · 2026-10-07⑥（🔧 **30 条 SWE-bench 横评再加 2 个 harness ⇒ 7-way**：`Hermes Agent` ＋ `Pi`）· **用户直令** · 高优先

> **用户直令（2026-10-07 21:4x）**：「**harness 的 SWE-Bench（30）对比加两个 harness：Hermes Agent 和 pi。**」
> ⇒ 现有 5 个（cline-patched / codex / opencode / claude-code / deepseek-harness）＋ **新 2 个** = **7-way × 同一 30 条**。

**① 我已替你定位（🚫 但你要自己复核版本/commit 并贴来源 URL —— 「不许猜」）**

| harness | 是什么 | 入口 | 接自定义/兼容 endpoint | 非交互 |
|:--|:--|:--|:--|:--|
| **Hermes Agent** | **`NousResearch/hermes-agent`**（MIT，251.8k★，Python；含 `hermes_cli` / `providers` / `evals` / `docker`；文档 hermes-agent.nousresearch.com/docs） | `hermes`（`hermes setup` 向导） | ✅ **Providers / Environment Variables 可配**（含 OpenAI 兼容） | CLI/headless；**有 Docker 镜像** |
| **Pi** | **`pi.dev`**（GitHub **`fleetagent/pi`**，Earendil Inc.，MIT，Node/npm；**已发 Pi 1.0**；文档 pi.dev/docs/latest） | npm 装后 `pi` | ✅ **Add Custom Providers / Run Local Models / 兼容 endpoint** | ⭐ **自带 print mode**（脚本化一次性）+ **JSON event stream** + **RPC** + **TS SDK** |

**② 口径（与现有 5 个完全一致，不许破口径）**
- **同一批 30 条**（现有 pilot `instances/`，**不许换题**）；**同一模型 `kimi-k2.6-cloud`**；**并发 = 1 严格串行**；**quota 失败单列**（不计入失败率）。
- **评分同口径**：产出的 `model_patch` 走**同一个 `r1_eval.py`（unshare 沙箱）** + **同一 timeout**；报告三列 `resolved / patch-but-failed / quota-blocked`。

**③ 做法（每步都要贴证据）**
1. **写适配层**：照现有 `run_harness.py` 的 driver，为两个新 harness 各加一个 driver（启动 → 指向 `gw_proxy`@`.29` + 指定 model → **产出 `model_patch`** → 交 `r1_eval.py`）。⚠️ **非交互 flag 必须从官方文档核实并贴 URL**（**Pi 用 print mode**；**Hermes 用其 CLI/headless 方式**）。
2. **安装**：**显式带 proxy**；**用独立 env / `--target`**，🚫 **别动共享 `py310`**；node/rust 已装过，缺件按老规矩走镜像。
3. **先 smoke 1 条**（端到端：装 → 起 → 产 patch → 评分），**跑通再上 30 条**；smoke 不通就**如实报卡点（含报错原文）**。
4. 🚫 **不许打断**正在跑的 chain（`deepseek-harness×30`，PID 1292346）—— **新 harness 排在它之后**（若另起并行槽，**仍必须保持「同一 harness 内并发 = 1」**）。

**④ 交付**
- `run/harness/SWEBENCH_COMPARE.html` 扩到 **7 行**（每行 `scored / resolved / pbf / quota-blocked / rate`）；`kimi_pilot_results.json` 同步；**口径表**写清：同 30 条 / 同模型 / 并发=1 / 时间窗 / **各 harness 版本或 commit**。
- 收尾按「收尾铁律」commit+push（前缀 `harness R<n>: …`）。

**时间盒**：装机+打通 ≈ 数小时/个；30 条 × ~5–9 min ≈ **2.5–4.5 h/个** ⇒ **两个 ≈ 1 天（不含装机）**。**先报你的估算**。
> 📦 体积提醒：本块加入后 `BAIZE_HARNESS_TASK.md` ≈34KB ⇒ 收尾前先归档已闭合旧块（确切字节以你自己 `wc -c` 为准）。


### 🆕 运维指令 · 2026-10-07（⏸ 300 全量先搁置 → **立即做「30 × 5 harness 横评」，先把 5 个 harness 对比结果拿到**）⭐ 最高优先 · **已批准**

> **用户直令（2026-10-07 原文口径）**：「**harness 拖了太久了，先做 30 横评，把 5 个 harness 对比的结果拿到。**」
> **本次任务一句话**（用户 2026-10-07 复述确认）：「找 SWE-bench 里 **30 个相同的任务**，**评测 5 个 harness**，**得到分数**，**列表对比**。」
> **运维判断（为什么读成「先停下 300」）**：横评口径是 **并发=1 严格串行**，而 **`codex ×300 --resume`（PID 2151526）正占着这唯一的串行槽**（已 14h+，尚有 **151 blocked**；按 ~30 条/10h 还须 **~50h**；其后还要 cline/opencode/claude-code/deepseek 各 ×300）⇒ **第一个「5 harness 对比」要等好几天**。用户要的是**先拿到「30 规模」的 5-way 对比**，再谈扩量。

**① 先腾出串行槽（本轮第一件事）**
- **停掉 `codex ×300` 的 `--resume`**：`kill` PID 2151526（或让它跑完当前 instance 后**不再取新 instance**）—— **二选一，把选择与理由写进心跳**。
- 🚫 **不要删** `run/harness/kimi_pilot_results.json`；**已得的 330 entries / codex×300 的 43 resolved 全部保留**（将来 `--resume` 可续）。
- ✅ 停下后确认串行槽空闲（无 `run_serial_kimi.py` 进程在跑）。

**② 把「同一 30 条」在 5 个 harness 上补齐（本次唯一 KPI）**
- **题集 = 固定的那 30 条**（**15 django + 15 sympy**，`instances/` 已备好的一批）；🚫 不许换题、不许增删。
- **模型 = 统一 `kimi-k2.6-cloud`**；**并发 = 1 严格串行**（沿用已批口径）；**quota 失败单列**、不计入失败率。
- **已有可复用**：`cline-patched ×30 ✅ 18/30 = 60.0%`、`codex ×30 ✅ 14/30 = 46.7%`（若二者与本题集**同批**则直接引用；**不同批则补跑**——同批与否要写清）。
- **待跑（按此顺序）**：`opencode ×30` → `claude-code ×30` → `deepseek-harness ×30`。
  - ⚠️ **5 个都要有分**：`deepseek-harness` 若工具链仍不通（`pnpm install` ECONNRESET / 镜像全 000）⇒ **本轮先把它修通**（node22+rust 已装、`build` 待 `pnpm`；**显式带 proxy + 用镜像**，🚫 勿动共享 `py310`）；**实在不通**才标「未参与」并回报，🚫 **不许因它卡住前两个**。

**③ 交付（本轮必须落地）**
- 刷新 `run/harness/SWEBENCH_COMPARE.html` ⇒ **只含「这 30 条 × 5 harness」的对比**（自包含、可复算）。
- **一张 5 行汇总表**：`harness | scored | resolved | patch-but-failed | quota-blocked | resolve rate`。
- **写清口径**：同 30 条 / 同模型 `kimi-k2.6-cloud` / 并发=1 / 时间窗 / 各 harness 版本。
- 结论**跑完即固化**；按「收尾铁律」commit + push。

**④ 300 全量**：**本轮不做** —— 等这 5-way 结果出来、用户/运维**再拍板**是否 `--resume` 续扩。

**判据**：`SWEBENCH_COMPARE.html` 出现 **5 行**对照表（**同一 30 条**），每行的 `scored / resolved / patch-but-failed / quota-blocked / rate` 均可由 `kimi_pilot_results.json` 复算；若 `deepseek-harness` 确不可用，**表内保留该行**并标注「工具链未通·未参与」+ 已尝试的取证。
**时间盒**：3 harness × 30 × ~8 min ≈ **~12h**（**先报你实测的 s/inst 估算**；若显著超 1 天须立即回报）。
**铁律**：同一轮**只用 kimi 一个模型**（换模型必须重跑）；不改选题；不缩水；不改论文；不占 GPU。

> 📦 **体积提醒**：本块加入后 `BAIZE_HARNESS_TASK.md` **≈34.1KB（>32KB）** ⇒ **你本轮收尾前先按「📉 体积维护规程」把已闭合旧块归档到 ≤32KB 再提交**（确切字节以你自己 `wc -c` 实测为准；**未到 40KB 红线**）。


### 🆕 运维指令 · 2026-10-05（晚 · ✅ 批准「扩 300」= **先扩 kimi**；+ 环境隔离纪律）· 高优先 · **已批准**

> **用户拍板（2026-10-05 晚）**：「harness 扩 300 的 quota 瓶颈 —— **按你的建议先扩 kimi**。」

**① 范围与口径（先扩 kimi）**
- 模型 = **`kimi-k2.6-cloud`**（已实测 **0 quota 阻塞**、cline-patched 30 条 **18 resolved = 60.0%**）；🚫 **不混模型**（`deepseek-v4-flash` 被 5h 窗口挡掉 17/22）。
- 规模 = **把「300 条」跑出来**（原提案 = 300 × 5 harness）。**先扩 kimi**：可先在已完成/在跑的 harness（cline-patched ✅ / codex 🔄）上把 **30 → 300**，再逐步换 harness；**同一 harness 内不得混模型**。
- **并发 = 1 严格串行**（保持现状）；一条跑完立即固化（json + HTML）。
- **quota 纪律不变**：命中 429/额度 → **暂停等窗口**（记录时长），🚫 不空刷；**空 patch / quota 失败单列**，不计入 harness 失败率。
- **报告三列**：`resolved / patch-but-failed / quota-blocked`；写清 **模型名 / 时间窗 / 并发=1**；最终刷新 `SWEBENCH_COMPARE.html`（自包含、可复算）。

**② 环境隔离纪律（治「同机争用」—— 用户裁定）**
- **训练/长跑 = 共享 `py310`**（不动）；**需要大量装包时另起独立 conda env**（别再把共享 env 装脏 —— P-9.8 armB 崩溃的元凶就是共享 `py310` 被 `pip install -e` 污染）。
- harness 反复跑 `pip install -e` 的 SWE-bench 工作区**尤其要隔离**（例：`conda create -n harness python=3.10`，或 `--target` / 容器内装），并**每轮复核 `easy-install.pth` / `.egg-link` 未被写回**。

**③ 边界**：不占 GPU；重 I/O 避让 `.29` 训练（GPU0–1 P-9.10 / GPU2–7 data 配比）；不改论文。

> ✅ 本块生效即视为已批准 —— 按上表执行，无需再等。


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



