# WATCH_RESEARCH_TASK.md — 观察哨 · research agent 任务书

> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。
> 运行时状态写 `MEMORY_RESEARCH.md` / `daily-memories-research/`；产物写 `research/`。
> ⚠️ 本文件全文 = 每次唤醒的 prompt → 保持精简；历史轮次归档到 `daily-memories-research/`，不进 prompt。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 本节由 supervisor 通过 git 修改，用于远程派活 / 改优先级 / 索取状态 / 暂停。
> agent 禁止修改本节。本节为「无」时，按下方默认顺序自主推进。

### 🆕 运维指令 · 2026-10-15（🩹 **本轮被 `pkill` 自匹配误杀 → 重启补跑；附防坑口径**）· 运维 · 最高优先

> **事实（loop 日志实证）**：本轮 cline **`exit 143`（SIGTERM）**、日志紧跟 `[abort] aborted`，中断点正是你执行
> `pkill -f 'arxiv.org/pdf'` —— **该模式匹配到了你自己那条 `bash -c "... pkill -f 'arxiv.org/pdf' ..."`**（命令行里含同串）⇒ **把自己的 shell/cline 一起杀了**。后果：本轮作废、重试额度用尽、直接睡到 06:00（≈10h 空转）；已下载的 2 个 PDF 被截断（xref 无效）。
>
> **① 必须重做（本轮已由运维重启，请接着做）**：把当日 **5 篇 PDF 重新下载并校验**（`%PDF-` 头 + 字节数 > 阈值 + `pdftotext` 能解析），落 `research/pdf/2026-10-15/`；坏文件删掉重下，🚫 不要把截断文件当成功记录。
> **② 防坑铁律（今后一律遵守）**：**任何 `pkill -f <模式>` 都要用「括号技巧」让模式不匹配自身**：
> - ✅ `pkill -f '[a]rxiv.org/pdf'`（推荐）或 `pkill -f 'arxiv[.]org/pdf'`
> - 🚫 绝不写 `pkill -f 'arxiv.org/pdf'` —— 命令行里含同串 ⇒ **自杀**（同一坑 2026-10-11 在 9222/Chrome 上踩过一次，任务书已记）。
> - 更稳：先 `pgrep -af '<模式>' | grep -v $$ ` 看清目标 PID，再 `kill <PID...>`。
> **③ 收尾**：跑完把「本轮中断+补跑结果」写进 `MEMORY_RESEARCH.md` 与 `daily-memories-research/2026-10-15.md`（如实登记）。

### 🆕 运维指令 · 2026-10-12（🚀 作者信「免审直发」：作废「首 3 封须复核」）· 用户直令 · 覆盖 `RESEARCH_MAIL_SPEC §4` + 10-11 块 ④

> 用户原话（2026-10-12）：「去掉『首 3 封必须先出草稿 + 报运维复核再发』规则，胆子大一点。」
> 改判：作者请教信一律免审直发（❌ 作废「首 3 封试运行须运维复核」）。
> 保留护栏（不变）：① 发送前草稿先入仓 `research/mail/drafts/<arXiv_ID>.md`；② 发送后当轮台账 + 心跳照写（没写=没发）；③ 频率 §3（每轮 ≤3 封 / 同作者 ≤1 / 不群发不催）；④ 红线 §8（不承诺合作署名资助 / 不透露未公开内部信息 / 不夸大 / 不加第三方）。
> 落地：已同步改 `RESEARCH_MAIL_SPEC.md §4`（权威口径以该文件为准）。

### 🆕 运维指令 · 2026-10-12（🈶 作者信语言：作者是中国人 ⇒ 用中文）· 用户直令 · 覆盖 `RESEARCH_MAIL_SPEC §2`

> 用户原话（2026-10-12）：「作者信未必是英文，如果作者是中国人，就用中文。」
> 改判：默认仍英文；若作者是中国人 ⇒ 用中文（判据：中文姓名 / 中国大陆·港澳台机构 / 主页或论文挂中国机构；不确定时按英文）。中文信 ≤300 字（英文 ≤200 词），四段式不变。
> 落地：已同步改 `RESEARCH_MAIL_SPEC.md §2`（权威口径以该文件为准）。

### 🆕 运维指令 · 2026-10-12（📨 每日论文日报：选 3–5 篇 → 下载 PDF → 邮件发 `paul.liu@cxmt.com`）· 用户直令 · ⭐ 最高优先（新职能）

> 用户原话（2026-10-12）：「research：每天选 3–5 篇论文，下载 PDF，发邮件给 `paul.liu@cxmt.com`。」
> 定性：新增一条「每日内部论文日报」职能，与既有「给论文作者发请教信」（`RESEARCH_MAIL_SPEC.md`）并存但独立。

① 频次：每天 1 封（建议 18:00 时窗、当日 5 篇已齐后执行）。

② 选文（3–5 篇）：从当日 `research/daily/<date>.html`（5 篇）或 `TOP_K`/`papers.jsonl` 中选 3–5 篇，优先与 BaiZe/ZhuLong 强相关（复用 §5 口径）；每篇写明 arXiv ID + 原题 + 一行「为何值得读」。

③ 下载 PDF：`https://arxiv.org/pdf/<id>`（本机若需带 proxy）→ 存 `research/pdf/<YYYY-MM-DD>/<arXiv_ID>.pdf`（⚠️ `.gitignore` 已排除 `pdf/`+`*.pdf` ⇒ 不入 git）；照 `research/pdf/README.md` 校验 `%PDF` 头 + 字节 > 0（失败即删、如实记）。

④ 发信：复用 `~/hr_mail.py` + `~/.hr_smtp`（`foamliu@yeah.net`；🚫 不自造；本机无 ⇒ 停手报运维）。
- 收件人 = `paul.liu@cxmt.com`（固定，🚫 不加第三方）。
- 单封附件合计 ≤ 20MB；超 ⇒ 分包（标 `1/2`…）或只附超额篇的链接 + 摘要。
- ⚠️ 本职能覆盖 `RESEARCH_MAIL_SPEC.md §8「不发大附件（≤5MB）」** —— 本日报**允许**附 PDF，**以上限 20MB 为准**。
- 主题：`[论文日报] MM-DD 精选 N 篇（BaiZe/ZhuLong 相关）`；正文中文：日期 + 清单（标题 / ID / 一行价值 / 是否附 PDF）。

⑤ 先审：本职能 = 内部日报 ⇒ 免审直发；但首封发送后当轮在 `MEMORY_RESEARCH.md` 标「首封已发」+ 给路径 / 篇数 / 字节 供运维抽查。

⑥ 台账（硬）：追加 `research/mail/发送记录.md`：`日期 | 类型=论文日报 | 收件人 | 篇数 | arXiv IDs | 附件字节 | 状态`（与「作者请教信」共用本台账、用 `类型` 列区分）；没写 = 没发。

⑦ 与「作者请教信」关系：两条独立职能 —— ①作者请教信＝英文·≤200 词·每轮 ≤3 封·首 3 封须运维复核（规格不变）；②本日报＝中文·每天 1 封·免审。两者互不占配额。

⑧ 红线：PDF 不入 git · 凭据仓外 · 🚫 不加第三方收件人 · 原题照抄（不改写）· 🚫 不夸大。

⑨ 📦 体积：本块加入后任务书 ~41KB 越 40KB 红线（加入前已 40,914 B）⇒ 本轮先自滚归档（已闭合块 → `daily-memories-research/` 或新建 `WATCH_RESEARCH_TASK_ARCHIVE.md`）至 ≤40KB 再提交。

### 🆕 运维指令 · 2026-10-11（✉️ 开启沟通权限：给论文作者发邮件请教 —— 服务于 BaiZe / ZhuLong 研发改进）· 用户直令 · ⭐ 最高优先

> 用户原话：「research：开启沟通权限，可以发邮件（recruit 知道如何发邮件）联系论文作者，请教问题；目标 = 请教论文细节，改进 BaiZe / ZhuLong 研发。」
> 取代 §「运维问答」里「是否给论文作者发邮件」的登记（原：只登记、不实施）⇒ 正式授权（四项前提见规格）；🚫「未获批准绝不发信」仅对本职能解除。
> 📄 完整规格见 `doc/personal-watch/run/RESEARCH_MAIL_SPEC.md` —— 发信前先读它（发件通道/模板/频率/先审/台账/红线全在里边）。
> 要点：① 发件复用 recruit 通道（`~/hr_mail.py` + `~/.hr_smtp` + `foamliu@yeah.net`；凭据仓外）—— 🚫 不自造配置；本机若无则停手报运维。② 英文请教信 ≤200 词 · 四段式 · 2–3 个能回填研发决策的具体问题 · 草稿先落 `research/mail/drafts/`。③ 每轮 ≤3 封 · 同作者/论文 ≤1 封 · 不群发、不催。④ 首 3 封试运行须运维批复后再发；之后免审，但发送前草稿须已入仓。⑤ 台账 `research/mail/发送记录.md`（没写 = 没发）。⑥ 🚫 不承诺合作/署名/资助 · 不透露未公开内部信息 · 不群发 · 不发大附件。
> 收尾：MEMORY + daily + `commit`（前缀 `research mail:`）+ push；`git add` 只加本线文件。

---


### 🆕 运维指令 · 2026-10-09（【第 5 批 · P0】每日 18:00（6PM）：从当日 TOP-5 论文挑 TOP-1 → 制作《论文两分钟》分镜脚本 HTML → `research/video/SCENES/MM_DD.html`）· ⭐ 每轮先读

> 用户原话（2026-10-09）：「明天开始让 research 在 6PM 这次唤醒，找 TOP-5 paper 中挑 TOP-1，制作《论文两分钟》分镜脚本 html。目录 SCENES，每天的分镜脚本放在这个目录下以 MM_DD.html 命名。」
> 生效时窗：自 2026-10-10 起，每天 `18:00`（6PM）唤醒执行一次（当天 `06:00` 轮不执行本批）。
> 输入：当日 `research/daily/<YYYY-MM-DD>.html` 的 5 篇（AM 3 + PM 2 —— 18:00 时已齐，先收口 5/5 再挑）。
> 挑 TOP-1 的判据（= 目的 2「科普」口径 · 不是「借鉴」口径）：从当日 5 篇中选 最适合做两分钟视频 的 1 篇 —— ① 大众能懂（有直观画面 / 反直觉结论）② 有传播力（震撼结果 / 热门话题）③ 可讲清（不必搬全篇）④ 有真实来源（arXiv ID + 链接）；并在脚本里写明「为什么选它」。⚠️ 若当天 5 篇全是难懂的借鉴类 ⇒ 选其中可视化潜力最强的，并注明。
> 交付物（主）：`research/video/SCENES/MM_DD.html`（MM_DD = 本地日期，如 `2026-10-10` → `10_10.html`）—— 自包含单文件（内联 CSS · 🚫 零外链 · 离线双击可开；范式对齐 `research/daily/*.html`）。
> 分镜脚本必备（逐镜 shot）：镜号 · 时间轴 · 口播文案 · 画面描述（自绘/自生成）· 屏幕文字/字幕 · 音效/BGM · 时长；时间轴沿用固定五段：钩子 0–10s → 问题 10–30s → 方法 30–80s → 结果 80–105s → 意义/展望 105–120s；中文口播 ≈350–450 字 ≈ 2 分钟（语速 180–200 字/分）。
> 必带：论文原题（英文照抄，🚫 不改写）· 作者/机构（前 3 + et al）· arXiv abs 链接 · 明标「论文解读」· 免责（非官方 · 非结论）。
> 顺手（低碳）：维护 `research/video/SCENES/index.html`（按日倒序列出、链到各日，每次只动 1–2 行）。
> 红线（硬）：🚫 不盗用论文原图（画面自绘/自生成）· 🚫 不夸大（「SOTA / 颠覆 / 突破」须指到原文出处）· 🚫 不编造数据 · 🚫 不为话题性曲解论文 · 📦 只入 git 文本/小图（单文件 ≥5MB 走网盘，见 §4-9）· 只 `git add` 本线文件。
> 档期 / 优先级：18:00 时窗内 —— 先完成当日 P0 第 4 批（晚报补齐 2 篇 → 5/5 收口），再做本批；额度紧张时 本批 > 常态增量采集。⚠️ V3（真正生成视频）仍待用户确认工具链，🚫 本批不做。
> 完成后：更新 `MEMORY_RESEARCH.md`（快照 + 流水）+ 当日 `daily-memories-research/<date>.md` 心跳；commit → push。

### 🎯 运维指令 · 2026-10-07（【第 4 批 · P0】每天 5 篇推荐论文（早 3 / 晚 2）→ 日报 HTML）· ⭐ 每轮先读

> 用户原话（2026-10-07）：「每天输出 5 篇推荐论文（早 3 晚 2），通过日报 html 输出。」「旧代存档暂停。」
> 定位：本批 = 本线当前最高优先 P0（原「第 3 批 A/B」降为 P1：TOP-K / TAKEAWAYS / 视频线照旧推进，但不挤占本批额度）。
> 额度（硬性）：每天 5 篇，不多不少 —— 06:00 轮出 3 篇、18:00 轮出 2 篇（当天合计 5）。✅ 宁少勿凑：合格论文不足 ⇒ 少收并如实写明「今日合格仅 n 篇 + 为什么」；🚫 不许拿超窗 / 低质 / 重复 / 非一手（摘要页/二手博客）凑数（入账判据 §0.1 不变）。
> 首日口径（2026-10-07 · 本批当天才下发）：今晚 18:00 = 首轮（当天没有早报）⇒ 直接出当日 5 篇（页头写「首日 · 晚报」+ 注明「AM 轮未运行」），并顺手建 `research/daily/index.html`；自 2026-10-08 起严格执行 3 + 2。
> 产出（本批唯一交付口径）：`research/daily/<YYYY-MM-DD>.html` —— 自包含单文件（内联 CSS、零外链、离线双击可开；范式对齐 `run/news/API_COMPARISON.html`）。
>   - 同一文件当天写两遍：06:00 = 生成（当日 3 篇）；18:00 = 优化（补齐第 4/5 篇 + 修订早报内容（错字/口径/补充推荐理由）+ 追加 `## 晚报变更说明（AM → PM）` 小节，逐条写「改了什么 / 为什么」）。
>   - 页头固定块：日期 · 早报/晚报标识 · 今日进度 `3/5 → 5/5` · 数据源（arXiv）· 生成时间 · 免责（「推荐 = 待读线索，非结论」）。
>   - 每条必带 8 字段：① 序号 ② 原文标题（英文原题照抄，🚫 不许改写/翻译成标题）③ 中文一句话（讲清做了什么，不吹）④ 作者/机构（前 3 + et al）⑤ 提交/更新日期 ⑥ 分类 + 标签（`借鉴` / `科普`）⑦ arXiv abs 链接（可点）⑧ 推荐理由（借鉴类：与 BaiZe / ZhuLong / 长鑫存储视角的关系，具体到「能用在哪一步」；科普类：大众看点、有无传播力）。
>   - 每篇须有实测证据：本机 `HTTP 200` + `Content-Type: XML` + 有 `published`（铁律「`200 ≠ 有料`」）；🚫 拿不到即不收。
>   - 去重：与 `SEEN.md` / `papers.jsonl` / `TOP_K.jsonl` / 近 7 天 `daily/*.html` 不得重复（同一 arXiv ID 只许出现一次）。
>   - 顺手（低碳）：维护 `research/daily/index.html`（按日倒序列出、链到各日、每次更新只动 1–2 行）。
> 口径护栏：HTML 里只写「推荐 / 待读」，🚫 不得写成「已验证结论 / 可复现收益 / SOTA 已证」；🚫 不夸大（用「SOTA/首次/颠覆」必须指到原文出处）；标题与一句话摘要不得曲解原文。
> 铁律继承：arXiv 限速 ≥3s · 每轮收尾必须自己 `commit+push`（四件事照做：心跳 / 日报 / 提交推送 / `git status -sb` 自检）。
> 本批不做：🚫 不新增归档 / 回溯类工作（见下方 ⏸ 暂停条）· 🚫 不为凑满 5 篇而放宽入账判据 · 🚫 不动 loop 脚本 · 🚫 不自动发邮件/发稿。

### ⏰ 运维指令 · 2026-10-07（唤醒节律：每 30 分钟 → 每天 2 次 · 06:00 / 18:00）· 常驻 · ⭐ 每轮先读

> 用户原话：「research 和 news 在烧我自己的 token，限制它们的启动频次 —— 从每 30 分钟启动，改成每天启动 2 次：6AM 和 6PM。」
> 新节律（由 loop 强制，不是你选的）：loop 只在时窗 06:00 / 18:00 调你；其余时间纯 bash 分段睡（零 token）。
> ⇒ `WAITING` 不再影响唤醒节律（字段保留，只为人读状态；旧自适应已降级为「仅回退模式」）。
> ⚠️ 因此每轮要「做满」：一次唤醒 ≈ 半天的量 —— 把该干的做完做透（检索/采集 → 去重 → 落盘 → 提交），🚫 别留「等下一轮再说」的碎活（下一轮是 12h 后）。
> ✅ 收尾铁律不变：每轮必须自己 `commit+push`（一次唤醒内可多次提交）；心跳/日报照写（供 supervisor 看进度）。
> ⏱️ 判死判据更替（旧口径作废）：`心跳 >60min 无提交 = 卡死` 对本线不再适用（12h 一提交是正常的）→ 判活改看 `/tmp/watch_research_loop.hb`（loop 每 5 分钟刷新）+ `/tmp/watch_research_loop.log` 的 `⏰ 定时模式：下次唤醒 = …`。
> ✍️ 顺手活（只做一次）：把 `MEMORY_RESEARCH.md` 顶部第 6 行、第 49 行的旧节律口径改成新口径（30min ⇒ 每天 2 次 06:00/18:00）。
> 🚫 不要自己改 loop 脚本；🚫 不要为了「保持心跳」而空唤醒/空跑（那正是要省掉的 token）。
> ℹ️ 本块只改节律，不动 §0.0.x 的架构与两大目的（借鉴 / 视频）。


### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】）· ⏸ 2026-10-07 起暂停（用户令「旧代存档暂停」）

> ⏸ 不再追溯搬迁「旧代」材料（旧批次/旧轮次/已作废运维块/旧节律块一律保持现状；🚫 不许为归档新建文件、不做长期快照存档）。
> ✅ 唯一保留 = 体积纪律「最小滚动」：仅当任务书 >40KB（或 `MEMORY_RESEARCH.md` >32KB）时，只搬刚超出的最少内容（原文搬入 `run/WATCH_RESEARCH_TASK_ARCHIVE.md`，无则新建 / `daily-memories-research/<日期>.md`）+ 留 1 行指针；🚫 不顺手多搬；🔧 不改小节编号/标题、不新增/不改写指令（本区作者仍是 supervisor）。
> 🛡 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块；冲突保留双方；提交写 `research 归档(压红线): …`。


### 🧭 运维规程 · 2026-10-06（【每轮唤醒必须自己 commit+push】 —— 不许依赖 loop 兜底）· 常驻

> 用户指令（2026-10-06）：与 BaiZe 四线同口径 —— 每条线每次唤醒都要推送。本线此前无此硬规则（靠 loop 兜底）⇒ 自本轮起作废「靠兜底」口径。
> 为什么：supervisor 只能靠 git 判断你是死是活 —— 2026-10-06 data 线心跳文件近 2h 未更新，被误判成卡死并上机排查。🚫「loop 每 N 小时兜底」不再作为交付保障，只是保险丝。
> 每轮唤醒结束前，按顺序做完这 4 件事，再置 `WAITING` / 去睡：
> 1. 写心跳：更新 `run/MEMORY_RESEARCH.md` 顶部「进度快照」+ 追加 1 行本轮流水（`[HH:MM] 干了什么 + 关键原始输出 1–2 行`）。
> 2. 写日报：`run/daily-memories-research/<YYYY-MM-DD>.md` 追加本轮（当天文件必须建）。
> 3. 自己提交 + 推送（🚫 不许等 loop 兜底）：`git pull --rebase --autostash` → `git add -- run/MEMORY_RESEARCH.md run/WATCH_RESEARCH_TASK.md run/daily-memories-research run/research` → `git commit -m "research <轮次>: <一句话>"` → `git push origin main`。🚫 绝不用 `git add -A`（共享工作副本，会卷入别线在途文件）。
> 4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind。push 失败（Forbidden / 网络）重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下轮第一件事补推。
> ⏱️ 判死判据（硬 · 2026-10-07 更替）：⚠️ 旧口径「心跳 >60min 无新提交 = 卡死」已作废 —— 本线改为每天 2 次唤醒，12h 一提交是正常的。新口径：① `/tmp/watch_research_loop.hb` 超 30min 未刷新 = loop 卡死（零 token 存活标记，与提交无关）；② 连续 >2 个时窗（>24h）无提交 = 本线卡死（那才要查 cline / 额度 / 网络）。


### 🆕 运维指令 · 2026-10-03（第 3 批：明确本线两大目的 + 启动《两分钟论文》视频线）⭐ 最高优先

> 背景（用户 2026-10-03 明确本线目的）：
> 1. 找与 BaiZe / ZhuLong 有关的前沿研究，以资借鉴（刘杨 = 长鑫存储 AI 研究院）→ 服务于在研工作；
> 2. 找有潜力的论文，做《两分钟论文》科普视频，发 B站 / 抖音，涨粉 → 日后收益。
>
> ⚠️ 两个目的的选题口径不同，必须分开（这是本线最容易混的地方，参照 news 线"口径分开"的教训）：
> 目的 1 看"与我们工作的相关性"；目的 2 看"大众看不看得懂 + 有没有传播力"（可以与我们无关）。

A. 目的 1（借鉴）——强化已有 TOP-K
- 在 `TOP_K.md/.jsonl` 每条新增两个字段：
  - `takeaway` —— 可借鉴点（1–3 句，具体到"我们能用它做什么"，例：它的 WSD 调度/SFT 配方/评测设计可迁移到 BaiZe 的哪一步）；
  - `action` —— 建议动作（`试跑` / `读原文` / `仅备忘`）。
- 另出一份 `research/TAKEAWAYS.md`：≤5 条"对我们工作的可借鉴结论"（每条：来自哪篇 + 能改什么 + 预期收益 + 成本）。宁精勿多。
- 🎯 相关面放宽到"存储/芯片 AI 研究院"视角：LLM 训练与推理效率 · 小模型/端侧 · 多模态 · agent/EDA 自动化 · 数据与评测。与半导体/EDA/存储相关的 AI 论文，`rel` 上调。

B. 目的 2（科普视频）——新建 `research/video/` 线

V1 · 选题（每期先交选题表）
- 候选池：`SEEN.md`/`papers.jsonl` 里 ≤30d 的论文；筛选口径：① 大众能懂（有直观画面/反直觉结论）② 有传播力（震撼结果、热门话题）③ 可讲清（不必搬全篇）④ 有真实来源（arXiv ID + 链接）。
- 产出 `research/video/SHORTLIST.md`：候选 10–20 条，字段 `论文 · 一句话看点 · 为什么大众会看 · 预估难度(易/中/难) · 建议平台(B站/抖音/都) · 备注`。
- 🚫 不许为了话题性曲解论文。

V2 · 脚本（本批主要交付）
- 对 TOP-3 选题各写一份两分钟中文口播稿 → `research/video/scripts/<arXiv_ID>.md`：
  - 结构（固定）：`钩子(0–10s) → 问题(10–30s) → 方法(30–80s) → 结果(80–105s) → 意义/展望(105–120s)`；
  - 长度：中文口播 ≈350–450 字（≈2 分钟，正常语速 180–200 字/分）；分镜提示（每段建议画面，自绘/自生成，🚫 不得盗用论文原图）；
  - 必带：论文标题 + 作者/机构 + arXiv 链接（口播里说一句"论文链接放简介"）。
- 合规红线：不夸大（"SOTA/颠覆"须有出处）· 不编造数据 · 明确标注"论文解读" · 遵守平台规则。

V3 · 视频生成（待确认工具链后再动，本批不强制）
- 需先确认运行机是否有：TTS（配音）/ 文生图（画面）/ 剪辑能力。
- ⚠️ 本批只做到 V1+V2；V3 等你（supervisor/用户）确认工具链再派。

铁律：不许编造 · `200 ≠ 有料` · 字段/来源齐全 · 只 add 本线文件 · ⚠️ 单个文件 ≥5MB 一律不入 git → 走百度云盘（见 §4-9「体积红线」，旧口径 >20MB 已作废）。
完成后：更新 `MEMORY_RESEARCH.md`（快照 + 运维问答）+ 当日流水；commit → push。

### 📦 归档指针 · 2026-10-03（第 2 批 TOP-K 精选排序 + 第 1 批 已实测取源清单）— 已闭合，压红线时原文搬出

> 两块原文已归档 → `run/WATCH_RESEARCH_TASK_ARCHIVE.md`（归档批次 1 · 2026-10-13）：① 第 2 批「TOP-K 精选排序（窗口 ≤30d）」= 已执行完毕（产出 `TOP_K.md`/`TOP_K.jsonl`；强化并入「第 3 批 A 节」）；② 第 1 批「已实测取源清单 + 3 个陷阱」= ✅ 已执行留档。现行口径：取源/限速见「建线首启」块 + §1/§2/§4。

### 🆕 运维指令 · 2026-10-03（建线首启：打通 arXiv API + 建论文采集线）（⬇️ 基础要求仍有效）

> 背景（用户 2026-10-03）：新建 research 线，用于打通 arXiv 下载 API、并持续收集 & 整理 AI 论文
> （重点：LLM / SLM / 多模态 / agent harness）。范式与 news 线一致（见 `WATCH_NEWS_TASK.md`），并继承其全部铁律。

R1 · 打通 arXiv API（先做，必须给实测证据）
- 端点：`http://export.arxiv.org/api/query`（Atom XML）。常用参数：`search_query` / `start` / `max_results` / `sortBy=submittedDate` / `sortOrder=descending`。
- 必须实测：真跑一次查询 → 贴命令 + 原始输出（≥3 条，含 `id`(arXiv ID) / `title` / `published` / `updated` / `primary_category` / `link`）。
- 必须校验：响应 `Content-Type`（应为 `application/atom+xml` 等 XML）+ `published` 日期真实。
  🔴 "接口 200" ≠ "有料"（news 线血的教训）：拿到 HTML/404/空 feed 一律判失败并记录。
- 礼貌限速（arXiv 官方要求）：请求间隔 ≥ 3 秒；单轮查询数受控，勿打爆。
- 产出：`research/ARXIV_API.md`（端点/参数/示例命令/实测输出/坑）。

R2 · 建检索策略（分类 + 关键词）：见 §1。把"每轮要跑的查询清单"固化进脚本/配置（别每轮现拼）。

R3 · 每轮采集 + 去重 + 整理：按 §2 SOP 执行；产出符合 §0.1 的论文条目。

R4 · 产出：`research/<YYYY-MM-DD>.md`（日报）+ `research/SEEN.md`（去重台账，主键 = arXiv ID）+ `research/INDEX.md` + `research/papers.jsonl`（结构化台账）。格式见 §3。

R5（可选，R1–R4 打通后）· PDF 下载：对入选论文下载 `pdf` 链接到 `research/pdf/`，校验是真 PDF（`Content-Type: application/pdf` + 文件头 `%PDF`）。
⚠️ 控制体积：默认只存链接；确需落地才下载，且单轮限量（如 ≤10 篇）。
⚠️ 且：单个文件 ≥5MB 一律不入 git → 下载后先 `ls -l` 量体积，超标就走百度云盘，并立刻 `rm` 本地副本（避免误 add）。见 §4-9。

铁律（继承 news 线，见 §4）：不许编造 · 字段缺一不可 · `200 ≠ 有料`（验 Content-Type + 日期） · 礼貌限速 · 不整篇转载（只做摘要 + 链接）。
完成后：更新 `MEMORY_RESEARCH.md`（快照 `PHASE=arxiv_bootstrap`）+ 当日流水；`git add` 只加本线文件 → commit → push。

---

## 📊 当前指令

| 项 | 当前值 |
|:---|:---|
| 当前指令 | 🎬 【第 5 批 · 2026-10-09 用户直派 · P0】每日 18:00（6PM）：从当日 5 篇论文挑 TOP-1 → 《论文两分钟》分镜脚本 HTML → `research/video/SCENES/MM_DD.html`（自包含；挑 TOP-1 用「科普」口径；逐镜含口播/画面/字幕/音效；V3 不做）。<br>🎯 【第 4 批 · 2026-10-07 用户直派 · 最高优先 P0】每天 5 篇推荐论文（早 3 / 晚 2）→ 日报 HTML：`research/daily/<date>.html`（自包含；06:00 生成 3 篇 / 18:00 优化补齐 2 篇 + `## 晚报变更说明（AM → PM）`）；当天合计 5 篇、宁少勿凑；顺手维护 `daily/index.html`。<br>（P1 · 照旧）第 3 批：A：TOP-K 加 `takeaway`/`action` + `TAKEAWAYS.md`（≤5 条）；B：《两分钟论文》V1 选题表 → V2 三条脚本（`research/video/`）；并行常态增量采集。 |
| 优先级覆盖 | 第 4 批（5 篇/天 HTML）与 第 5 批（18:00 分镜脚本）为 P0（18:00 时窗：先 P0 收口 5/5，再出分镜）> A（借鉴）≈ B 的 V1/V2 > 常态增量采集 > V3（视频生成，待确认工具链）。✅ 免 key。📧 邮件未批准 → 不得发送。⚠️ 两个目的口径不同，选题不得混用（`借鉴` 看与我们在研工作相关性；`科普` 看大众看得懂 + 传播力）。 |
| 状态索取 | `<无>`（若 supervisor 写入具体问题，本轮先答该问题再干活，答案写进 `MEMORY_RESEARCH.md` 顶部「运维问答」区） |
| 暂停标志 | `<无>`（若写入 `STOP`，本轮只更新记忆、不做任何动作，然后退出） |
| 采集节律 | ⏰ 每天 2 次定时唤醒：06:00 / 18:00（2026-10-07 用户令；`SCHEDULE_HOURS=6,18` 本地时区；时窗内零 token 分段睡）。⚠️ `WAITING` 已不影响唤醒节律（仅人读状态）；一次唤醒 ≈ 半天量 ⇒ 当轮做满。回退旧自适应：`WATCH_SCHEDULE_HOURS=` 置空 |

---

## 📊 进度快照（每次唤醒必须更新，供 supervisor 远程巡检）

> 固定格式写在 `MEMORY_RESEARCH.md` 最顶部，便于一条命令读到全局状态。

```
PHASE:        <当前阶段：arxiv_bootstrap / 常态采集>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
本轮新增:     <n> 篇（领域数：m）
阻塞:         <无 / 具体阻塞 + 需要 supervisor 做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_RESEARCH.md` 的顶部单独一行
（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行 —— 否则会误触发长睡。

> 💓 心跳（2026-10-05 新增，硬性）：每轮唤醒必须向 `daily-memories-research/<YYYY-MM-DD>.md` 追加一行：
> ```
> [HH:MM] wake | PHASE=<当前阶段> | 本轮=<做了什么 / 0 变更>
> ```
> 目的：让 supervisor 从 git 端就能区分「在跑长任务」与「已经停了」。
> ⚠️ 即使用户没让做任何事、本轮 0 变更，这一行也必须写（它是"存活证明"，不是产出）。

supervisor 巡检方式：`git pull` 读 `MEMORY_RESEARCH.md` 顶部 + `research/` 下最新日报即可，不需要登录服务器。

---

## 0. 任务概述

本线的两大目的（用户 2026-10-03 明确）：

| # | 目的 | 服务对象 | 选题口径 | 产物 |
|:--|:--|:--|:--|:--|
| 1 | 找与 BaiZe / ZhuLong 有关的前沿研究，以资借鉴 | 在研工作（刘杨 = 长鑫存储 AI 研究院） | 看与我们在研工作的相关性（含半导体/EDA/存储视角） | `TOP_K.*` + `TAKEAWAYS.md` |
| 2 | 找有潜力的论文 → 做《两分钟论文》科普视频 → 发 B站/抖音 → 涨粉变现 | 公众/粉丝 | 看大众能不能懂 + 有没有传播力（可以与我们无关） | `video/SHORTLIST.md` + `video/scripts/*.md`（+ 后续视频） |

> ⚠️ 两个目的口径不同，选题必须分开（勿混，参照 news 线"口径分开"的教训）。

通用目的：为《超级智能2035》（作者刘杨/Foam）提供一手论文与科普素材；只搬运事实 + 忠实摘要，不生产观点。

产出（按用途分目录）：
- 日报/台账（原有）：`research/<YYYY-MM-DD>.md` · `SEEN.md`（主键 arXiv ID）· `INDEX.md` · `papers.jsonl` · `ARXIV_API.md`；
- 借鉴（目的 1）：`research/TOP_K.md` · `TOP_K.jsonl` · `TAKEAWAYS.md`；
- 科普视频（目的 2）：`research/video/SHORTLIST.md` · `research/video/scripts/<arXiv_ID>.md`（+ 后续成片，大文件不入 git）。

---

## 0.1 什么是「可收录的论文」（入账判据 · 硬性）

> ⚠️ 本线只收"一手论文"。不满足下面 4 条的一律不算（可另单列为"相关报道"，不进论文台账）。

可收录论文 = 「arXiv 上的、与关注领域相关的、可核验的一手论文」。4 条必须同时成立：

| # | 判据 | 说明 |
|:--|:--|:--|
| 1 | 来源 | arXiv（一手预印本）；必须给 `arXiv ID` + `abs` 链接（有 pdf 也给）。其它一手源（OpenReview / ACL Anthology）须显式标注。 |
| 2 | 时效 | `published`（首次提交）≤ 72 小时（日报口径）。陈年经典不算（除非 supervisor 点名）。<br>⚠️ 例外：arXiv 周末不公告（见运维指令 R2′）→ 落在周末/周一早时，可放宽到「最近一次公告批次」并如实标注实际日期区间。 |
| 3 | 可核验 | 齐备：`arXiv ID` + `标题` + `作者` + `提交/更新日期` + `主分类` + `链接`。 |
| 4 | 领域相关 | 命中 §1 关注领域。 |

典型反例（不进论文台账）：博客解读 / 媒体转述 / 二手综述 / 知乎推文 / 公众号文章
（若要留，放日报文末「附录 · 相关报道」并标 `🏷 类型：report`，不计入论文数）。

---

## 1. 关注领域（Watch List）

> 每轮由上到下逐领域检索；没有就如实写"本领域无新增"，不要凑数。查询清单应固化进脚本/配置（R2）。

| # | 领域 | arXiv 主分类 | 收什么 | 建议查询词 |
|:--|:--|:--|:--|:--|
| 1 | LLM | cs.CL · cs.LG | 预训练/规模律/指令微调/RLHF/推理/长上下文 | `large language model`、`scaling law`、`reasoning` |
| 2 | SLM（小模型） | cs.CL · cs.LG | 小模型/端侧/蒸馏/量化/高效推理 | `small language model`、`on-device`、`distillation` |
| 3 | 多模态 | cs.CV · cs.MM · cs.CL | VLM / MLLM / 图文视频理解 / 生成 | `vision-language model`、`multimodal`、`MLLM` |
| 4 | agent harness | cs.SE · cs.AI · cs.MA | code agent / tool use / harness / 评测基准 | `agent`、`tool use`、`SWE-bench`、`terminal-bench`、`multi-agent` |
| 5 | 邻域（可选） | cs.AI · cs.LG | RAG / 评测 / 对齐安全（仅当与 1–4 强相关） | `retrieval augmented`、`benchmark`、`alignment` |

> ✅ 关注领域可被 supervisor 修改（改本表即可）。

---

## 2. 每轮采集 SOP（每次唤醒照此执行）

1. 读现状：`MEMORY_RESEARCH.md` 顶部快照 + `research/SEEN.md`（已收录，避免重复）+ 当日日报（已写部分）。
2. 定窗口：确认上次采集时间（见流水）→ 本轮优先覆盖上次之后的新提交。
3. 逐领域检索：对 §1 每领域跑查询（`sortBy=submittedDate&sortOrder=descending`）；
   ⏱ arXiv 礼貌限速：请求间隔 ≥ 3 秒；单轮查询总数受控（建议 ≤ 12 次）。
4. 筛与去重：与 `SEEN.md` 比对 arXiv ID（主键）→ 命中即跳过；只留命中 §1 且满足 §0.1 的条目。
5. 落盘：新条目追加到 `research/<YYYY-MM-DD>.md`（§3 格式）+ 写入 `research/papers.jsonl` + `SEEN.md`。
6. 更新：`research/INDEX.md` 计数；`MEMORY_RESEARCH.md` 快照 + `WAITING`；当日流水。
7. 提交：`git add` 只加本线文件（`MEMORY_RESEARCH.md` `research/` `daily-memories-research/`）→ `commit -m "research <date> <n> 篇"` → `push`。

> ⏱ 不要 sleep / 不要等待：一轮做完就更新记忆并退出（loop 按 `WAITING` 决定何时唤醒下一轮）。

---

## 3. 输出格式

### `research/<YYYY-MM-DD>.md`（当日日报）

```markdown
# 论文日报 · <YYYY-MM-DD>

> 采集窗口：<上次时间> ~ <本次时间> ｜ 本轮新增：<n> 篇 ｜ 查询数：<m>

## 1. LLM
- **[标题]**（arXiv:<ID>，<提交/更新日期>）
  作者：<前 3 + et al>
  分类：<primary_category> ｜ 🏷 领域标签：<LLM/推理/长上下文…>
  一句话摘要：<中文，1~2 句，忠实原文，不抄整段>
  🔗 abs: <...> ｜ pdf: <...>
  （可选）💻 代码：<...>

## 2. SLM（小模型）
- ...（无新增则写：_本领域无新增_）
```

字段硬要求：`arXiv ID` + `标题` + `作者` + `日期` + `分类` + `🔗 abs` 缺一不可。

### `research/daily/<YYYY-MM-DD>.html`（⭐ P0 · 每天 5 篇推荐 · 早 3 晚 2 · 见本区顶部「第 4 批」块）

> 这是本线当前 P0 交付物；`research/<YYYY-MM-DD>.md`（下方）降为配套台账，两者可内容不同口径（md = 采集流水；HTML = 精选推荐）。

```text
结构（自包含单文件，内联 CSS，零外链，离线可开）：
┌ 页头：日期 · 早报/晚报 · 今日进度 3/5 → 5/5 · 数据源(arXiv) · 生成时间 · 免责「推荐 = 待读线索，非结论」
├ 5 条推荐（每条 8 字段：序号 / 原题 / 中文一句话 / 作者机构 / 日期 / 分类+标签(借鉴|科普) / arXiv abs 链接 / 推荐理由）
├ 附录：本轮检索式与命中数（可核验）· 去重剔除条数
└ 18:00 轮追加：## 晚报变更说明（AM → PM）—— 逐条写「改了什么 / 为什么」
```

硬性：① 当天合计 5 篇（3 + 2），宁少勿凑并写明原因；② 每篇必须有实测证据（`HTTP 200` + `XML` + 有 `published`）；③ 与 `SEEN.md` / `papers.jsonl` / `TOP_K.jsonl` / 近 7 天 `daily/` 不重复；④ 每轮必须提交 `research/daily/`（HTML 是交付物 ⇒ 必须入 git）；⑤ 顺手维护 `research/daily/index.html`。

### `research/SEEN.md`（去重台账）

```markdown
# SEEN — 已收录论文去重台账

| 首次收录 | arXiv ID | 标题 | 主分类 |
|:--|:--|:--|:--|
| 2026-10-03 | 2609.xxxxx | <标题> | cs.CL |
```

### `research/papers.jsonl`（结构化台账，一行一篇）

```json
{"arxiv_id":"2609.xxxxx","title":"...","authors":["..."],"submitted":"2026-10-02","updated":"2026-10-03","category":"cs.CL","areas":["LLM"],"summary_zh":"...","abs_url":"...","pdf_url":"...","first_seen":"2026-10-03"}
```

---

## 4. 铁律（红线，违反即失败）

1. 🚫 不许编造：必带 `arXiv ID` + 链接 + 日期 + 作者；无来源不收录。搜不到就写"未找到"。
2. 🚫 `200 ≠ 有料`（news 线血的教训）：必须校验 `Content-Type`（XML）+ `published` 日期真实；
   拿到 HTML / 404 / 空 feed 一律判失败并记录，不得当成"无新增"。
3. 🚫 不整篇转载：摘要自写（1~2 句中文），不得整段抄英文原文；只给链接。
4. 🚫 不把推测写成事实：摘要忠实原文；判断类内容须显式标注"我们的观察"。
5. ⏱ 礼貌限速：arXiv 请求间隔 ≥ 3 秒；单轮查询数受控；不并发打爆。
6. 🚫 不 `git add -A`：只加本线文件（共享工作副本，会卷入他人在途文件）。
7. 🚫 不在正文/快照/流水写以 `WAITING:` 开头的行（会误触发 loop 长睡）。
8. ⚠️ PDF 下载：先验 `Content-Type: application/pdf` + 文件头 `%PDF`；单轮限量（≤10 篇），控制仓库体积。
9. 📦 体积红线（2026-10-05 新增，红线 · 用户明令）：任何单个文件 ≥ 5 MB，一律不得用 GitHub 传输（不 `git add`、不 commit、不 push）。
   适用：论文 PDF、图片、音频、视频、模型权重、数据集分片、`*.zip` / `*.gz` / `*.docx` 等一切大文件。
    - ✅ 正确做法：走百度云盘（首选 `bypy`；备选 `BaiduPCS-Go`），把网盘路径 / 提取码 / 文件名登记进 `research/INDEX.md`（或对应清单）；
    - ✅ 落实手段：`research/pdf/`、`research/raw/`、`research/video/` 等目录必须有 `.gitignore` 规则；
      `git add` 前自查：`git check-ignore -v <file>` 应命中；未命中就先补 `.gitignore`；
    - ⚠️ 元数据仍要入 git：清单里记 路径 / 字节数 / sha256 / 存放位置（`git` 或 `网盘:<路径>`） —— 数据本体不进 git，但「账」必须在 git；
    - 🚫 禁止规避：`git add -f` 强推、先压成 `.zip` 再进、把大文件塞进别的容器 —— 一律按"原始单文件实际字节数"判（`ls -l` / `du -b`）；
    - 🚫 若网盘也不可用：宁可不传（本地保留 + 清单登记 + 在 `MEMORY_RESEARCH.md` 如实写「未上云」），也绝不许塞进 git；
    - 📌 本线现状：`research/raw/topk-fetch.json` ≈ 2.7 MB（<5MB，可留 git）；PDF 线（R5）下载的单个 PDF 极易超 5MB →
      从本轮起，PDF 一律不进 git：只存链接 + 网盘路径。

---

## 5. 记忆维护（硬性）

> 理由：`MEMORY_RESEARCH.md` 每次唤醒都被 agent 全文读取 → 越大越烧 token。

- 上限（两者相同）：`MEMORY_RESEARCH.md` 与本线任务书 `WATCH_RESEARCH_TASK.md`（全文=prompt） 均 ≤ 32KB（红线 40KB）；一旦超限即执行滚动。
- 任务书自己滚（2026-10-06 用户裁定）：任务书的归档由本线 agent 自己做（与 MEMORY 同机制），不再依赖 supervisor —— 只把「已闭合」的历史轮次 / 已执行完的运维块【原文】搬入 `run/WATCH_RESEARCH_TASK_ARCHIVE.md`（留 1 行指针；不新增/不改写任何指令，本区作者仍是 supervisor）。
- 滚动：把较早的流水条目（保留最近 ~20 条）追加到 `daily-memories-research/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 /「进度快照」③ 「运维问答」④ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---

## 6. 附录 · 相关文件

- 本项目总纲：`../README.md`；supervisor 记忆：`../MEMORY.md`；agent 总表：`../AGENTS.md`。
- 姊妹线（范式与铁律来源）：`WATCH_NEWS_TASK.md`（news 线）+ `watch_news_loop.sh`。
- arXiv API：文档 https://info.arxiv.org/help/api/user-manual.html ｜ 端点 `http://export.arxiv.org/api/query`


