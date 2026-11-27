# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 回信跟踪已真实打通）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r276 · 2026-11-28 03:00 时窗：**A 轨今日已满 5/5 ⇒ 0 新收**（不凑第 6 篇）＋ **B 轨 +3 → 455**（Show, Attend and Tell 10,308 / SQuAD 11,133 / PointNet 11,443）＋ **作者网 +3 → 422**（X +1 → 165）＋ **发信 +1 → 190**（#190 Aaron Courville 英文 199 词 `SENT OK 03:03:37`）＋ **回信再核**（IMAP 只读：INBOX 70、与 00:00 持平、0 新实质/0 新退信）]
  前一（r275）: [r275 · 00:00：A 5/5（DiversePlace / CPU-Eval / NEVA / SPLICE / Solve Vision with Code）＋ B +3 → 452 ＋ 作者网 +3 → 419 ＋ 发信 +1 → 189（#189 Zhiyao Xie 中文 248 汉字）＋ 回信 0 新] 详情见 `daily-memories-research/2026-11-28.md`。
  ① 回信再核（r276）：INBOX **70 封**（00:00 为 70 ⇒ **+0**）；`SINCE 25-Nov-2026` 11 封，最新 Ultralytics 订阅；作者来信仍只有已知 **#187 Petar 回复**（已落盘 `replies/1710.10903.md`）。**无新实质回信、无新退信**。
  ② 累计分账（190）：实质 **8 信 / 7 人 ≈4.3%** · 自动 1 · 退信 9 · 无应答(>14d) 32 · 未到期 140 ⇒ 8+1+9+32+140 = 190 ✔；送达 8/181 ≈4.4%。
  ③ A 轨 **0 新收**（今日已满 5/5，守「宁少勿凑」，不凑第 6 篇）；本窗不做 A 检索。
  ④ B 轨 **+3 → 455**（第一百二十九轮）：Show, Attend and Tell `1502.03044`（10,308，2015；软注意力 196 位置期望 + 硬注意力变分下界，注视可视化）/ SQuAD `1606.05250`（11,133，EMNLP 2016；10 万+ 问题、答案必为原文片段，F1 51.0% vs 20%，人类 86.8%）/ PointNet `1612.00593`（11,443，CVPR 2017；直接消费点云、置换不变、分类/分割/语义解析统一）；arXiv API `200` + atom（`published` 逐字）+ OpenAlex 3/3 `200`（查询日 2026-11-28）；查重 0 命中；Show Attend 另用 ar5iv `200` 核 196×512 / 14×14。
  ⑤ 作者网 **+3 → 422**（X +1 → 165）：#420 Aaron C. Courville（Mila / 蒙特利尔大学，A 级 `courvila@mila.quebec`，X 未找到；已发信 #190）/ #421 Pranav Rajpurkar（Harvard Medical School，主页无邮箱，X `@pranavrajpurkar` 双源；仅建档）/ #422 Kelvin Xu（Google DeepMind，A 级 `kelvinxx@google.com`，X 未找到；仅建档，守「同一论文 ≤1」）。三人同属 Show Attend / SQuAD。
  ⑥ 发信 **+1 → 190**（今日 2/12）：#190 Courville 英文 **199 词** `SENT OK 03:03:37`；落款两行、其后无行；专属细节 = 196（14×14）软注意力期望 / 硬注意力采样 + 变分下界 / 细长高分辨率波形图 / 注意力熵诊断 / 冻结编码器只训注意力与解码器；与 #187/#184 零共用。
  ⑦ 交付：`research/2026-11-28.md`（03:00 补记）· `daily/2026-11-28.html`（新增 03:00 块 + footer/meta 更新）· `PAPERS.md` #453–#455 + 快照 455 · `AUTHORS.md` #420–#422 + 计数 422/165 · `发送记录.md` §17/§18 · drafts/bodies 各 1。
  ⑧ 网络：arXiv `200` + atom；OpenAlex `200`（加 mailto + ≥3s）；X 经代理 `200`；SMTP `SENT OK`；IMAP `LOGIN OK` / 70 封。
当前动作:     ✅ 03:00 时窗闭环：A 0 新收（已满 5/5）；B +3 → 455；作者网 +3 → 422；发信 +1 → 190；回信 0 新。
下一步:       ① 下一时窗（06:00 · 新一天 A 额度按日界？本日 11-28 仍为 5/5 ⇒ 只要日期未变仍 0 新收，做 B / 作者网 / 发信 / 回信）；② B 轨继续补真空白；③ 作者网 +3（优先 EDA 学者，找可核邮箱）；④ 每轮先读收件箱；⑤ 发信守 A 级 + 同论文 ≤1（今日余 10 封）；⑥ 运维待办（显示名 / 额度 / 任务书 44KB / 台账缺口 / loop 兜底与假阳性）。
本轮新增:     A +0（5/5）· B +3（455）· 作者网 +3（422）· X +1（165）· 作者信 +1（190）· 实质回信 0 新（8 封/7 人）· voice_ready 0 · news_ready 0
阻塞:         ① 🔴 昨日 03:00–18:00 六窗曾因 `Insufficient Balance` 未执行（00:00 起恢复）⇒ 仍需运维确认额度稳定/轮换；② 显示名仍 `AI+EDA 招聘 · 自动`（`~/.hr_smtp` name）⇒ 需运维改学术署名；③ SMTP 只发不收 ⇒ 每轮须 agent 主动 IMAP 只读；④ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且只读 ⇒ 需授权；⑤ 台账 #164–#170 缺口待核查；⑥ #168/#175 地址有效性存疑；⑦ loop 兜底 `git add` 范围待核查；⑧ loop 假阳性（工具回显含自检正则字样）；⑨ SPEC 仅三值，实际出现第 4 类「退信(反垃圾/无效)」待追认。
ERROR_COUNT:  124（r276 本身 0 错误；累计为历史 loop 误判重试计数，本窗未增）
```

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（运维第 2 批登记）**：是否要**给论文作者发邮件**做学术交流/技术沟通？
  **A（本线）**：**已登记为未来职能，本批只登记、不实施**。启用**前提（须用户明确批准）**：① 发件邮箱/身份/署名；② 邮件模板；③ 频率上限；④ 每封是否需用户先审。
  **红线**：**未获批准，绝不自动发送任何邮件**。当前各线上均**无任何发信动作**。

- **Q（运维第 3 批 B 节 · 视频线）**：`V3`（把口播稿变成成片）什么时候能启动？需要用户/环境确认什么？
  **A（本线）**：**V1/V2 已交付**（选题表 + 3 份口播稿，纯文本）；**V3 会用到运行机可能没有的工具链**，故**本批不做**，先把**待确认清单**摆出来，获批后再动：
  ① **TTS / 配音**：用哪个引擎（系统 `espeak`？本机有无可用的中文 TTS？还是要用户自录口播）；② **文生图/画面**：运行机是否可访问图像生成服务（**HF 本机不可达**，需另定；否则退化为**纯自绘 SVG/图表**）；
  ③ **剪辑**：有无 `ffmpeg`；成片**>20MB 不入 git**（走外部目录 + 清单）；④ **栏目名**：本线**须自起**（避免与已有知名频道「两分钟论文」混淆）；
  ⑤ **发布**：B站/抖音账号、实名与平台规则在**用户侧**，**发布由用户本人执行**。
  **红线**：**不盗用论文原图、不夸大、不曲解**；未获确认**不擅自生成/发布成片**。
- **Q（运维指令 2026-10-12 · 📨 每日论文日报）**：选 3–5 篇 → PDF → 邮件发 `paul.liu@cxmt.com`，是否已执行？
  **A（现行口径）**：旧「每日论文日报邮件」职能已由 **2026-11-07 10:50 用户令**停止 —— 日报唯一出口 = `research/daily/<YYYY-MM-DD>.html` + `daily/index.html`；历史发送细节（第 1–23 封、分包、PDF 体积）已归档到 `WATCH_RESEARCH_TASK_ARCHIVE.md` 与 `daily-memories-research/`，此处不再复述。**作者请教信**是另一职能，口径见 `RESEARCH_MAIL_SPEC.md`（免审直发、每轮 ≤3 / 每日 ≤12）。


---

## 1. 状态头

- **线**：research（arXiv 论文采集/整理）
- **任务书**：`WATCH_RESEARCH_TASK.md`（只读）
- **产物**：`research/<YYYY-MM-DD>.md`（日报）· `research/SEEN.md`（去重台账，主键 arXiv ID）· `research/INDEX.md`（索引）· `research/papers.jsonl`（结构化台账）· `research/ARXIV_API.md`（R1）· **`research/TOP_K.md` + `research/TOP_K.jsonl`**（精选排序；源 `TOP_K_notes.md` + **`TOP_K_takeaways.json`**）· **`research/TAKEAWAYS.md`**（第 3 批 A 节：≤5 条可借鉴结论）· **`research/video/SHORTLIST.md` + `research/video/scripts/<arXiv_ID>.md`**（第 3 批 B 节：视频线 V1/V2）
- **工具/回归**：`research/arxiv_fetch.py` + `research/test_arxiv_fetch.py`（49/49）· **`research/top_k.py`（含 `--takeaways-json`）+ `research/test_top_k.py`（25/25）**
- **日流水**：`daily-memories-research/<YYYY-MM-DD>.md`
- **关注领域**：LLM · SLM · 多模态 · agent harness（+ 邻域，见任务书 §1）
- **采集节律**：⏰ **每天 8 个时窗 · 0/3/6/9/12/15/18/21（本地时区）**（`RESEARCH_MAIL_SPEC §3` 与 loop 现行口径；`WAITING` 字段保留仅供人读、**已不影响唤醒节律**）；回退：`WATCH_SCHEDULE_HOURS=` 置空 ⇒ `WAITING=1` 睡 **30min** / `WAITING=0` 短睡 **60s**
- **上次采集窗口**：`2026-11-28 00:0x`（**第二百七十五轮 · 00:00 时窗**〔新一天首窗，A 额度重置〕：A 轨 **5/5**（DiversePlace / CPU-Eval / NEVA / SPLICE / Solve Vision with Code）；B 轨 **+3 → 452**（Sparse Transformers / DALL·E / MLP-Mixer）；作者网 **+3 → 419**（X 164）；发信 **+1 → 189**（#189 Zhiyao Xie，中文 248 汉字）；**回信再核**：INBOX 70（+0）、无新实质回信、无新退信 ⇒ 退信累计 9）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`papers.jsonl` 现 **422 行**（A 轨结构化台账；`SEEN.md` 为唯一防重台账；本日 A 轨 +5 → 今日 5/5）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**452 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**一百二十八轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**419 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`。**回信摘录 `research/mail/replies/<arXiv_ID>.md`（2026-11-26 起真实落盘 8 份）**


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-28（本地 03:0x · 03:00 时窗 · r276 · 🅰 A 轨 0 新收〔今日 5/5 已满〕＋ 🅱 B +3 → 455 ＋ 作者网 +3 → 422（X +1 → 165）＋ 发信 +1 → 190（今日 2/12）＋ 回信再核 0 新）** —— **第二百七十六轮**：① 回信再核（IMAP 只读）：INBOX **70**（00:00 为 70 ⇒ +0）；`SINCE 25-Nov` 11 封，最新 Ultralytics 订阅；作者来信仍只有已知 #187 Petar 回复；无新实质回信、无新退信。② 累计（190）：实质 8 信 / 7 人 ≈4.3% · 自动 1 · 退信 9 · 无应答>14d 32 · 未到期 140 ⇒ 8+1+9+32+140=190 ✔；送达 8/181 ≈4.4%。③ A 轨 **0 新收**：今日已满 5/5，守「宁少勿凑」，不凑第 6 篇。④ B +3 → 455：Show, Attend and Tell `1502.03044`（10,308）/ SQuAD `1606.05250`（11,133，EMNLP 2016）/ PointNet `1612.00593`（11,443，CVPR 2017）；arXiv API `200` + atom（`published` 逐字 `2015-02-10T19:18:29Z` / `2016-06-16T16:36:00Z` / `2016-12-02T08:40:40Z`）+ OpenAlex 3/3 `200`（查询日 2026-11-28）；查重 0 命中；Show Attend 另用 ar5iv `200`（192,682 B）核到 196×512 / 14×14。⑤ 作者网 +3 → 422（X +1 → 165）：#420 Aaron C. Courville（Mila，A 级 `courvila@mila.quebec`，X 未找到；已发信 #190）/ #421 Pranav Rajpurkar（Harvard Medical School，主页无邮箱，X `@pranavrajpurkar` 双源；仅建档）/ #422 Kelvin Xu（Google DeepMind，A 级 `kelvinxx@google.com`，X 未找到；仅建档，守「同一论文 ≤1」）。⑥ 发信 +1 → 190（今日 2/12）：#190 Courville 英文 199 词 `SENT OK 03:03:37`；落款两行；专属细节 = 196（14×14）软注意力期望 / 硬注意力采样 + 变分下界 / 细长高分辨率波形图 / 注意力熵诊断 / 冻结编码器只训注意力与解码器；与 #187/#184 零共用。⑦ 交付：`research/2026-11-28.md` 03:00 补记 · `daily/2026-11-28.html` 03:00 块 + meta/footer · `PAPERS.md` #453–#455 + 快照 455 · `AUTHORS.md` #420–#422 + 计数 422/165 · `发送记录.md` §17/§18 · drafts/bodies 各 1。详见 `daily-memories-research/2026-11-28.md`。
- **2026-11-28（本地 00:0x · 00:00 时窗 · r275 · 🅰 A 轨收满 5/5 ＋ 🅱 B +3 → 452 ＋ 作者网 +3 → 419（X 164）＋ 发信 +1 → 189（今日 1/12）＋ 回信再核 0 新）** —— **第二百七十五轮**（新一天首窗，A 额度重置）：① 回信再核（IMAP 只读）：INBOX **70**（21:00 为 70 ⇒ +0）；`SINCE 25-Nov` 11 封，最新 Ultralytics 订阅；作者来信仍只有已知 #187 Petar 回复；无新实质回信、无新退信。② 累计（189）：实质 8 信 / 7 人 ≈4.3% · 自动 1 · 退信 9 · 无应答>14d 32 · 未到期 139 ⇒ 8+1+9+32+139=189 ✔；送达 8/180 ≈4.4%。③ A 轨 **5/5**：DiversePlace `2611.34472`（宏单元布局质量受控多样性 + 课程 PPO；ISPD2005 top-5/10/20 归档多样性提升、HPWL 持平或更低）/ CPU-Eval `2611.32405`（339 题 / 6 真实 CPU；七模型平均 pass@1 比 VerilogEval v2 低 45.14pp；行数越多、HDL 越少见越低）/ NEVA `2611.33346`（NL 架构规格演化 + 约束校验；Claude Opus 5.5 单核最高 +4.8%，40 候选/2.2 天/~$320，多核无显著差异）/ SPLICE `2611.34777`（all-fail 组局部拼接 RL；比 GRPO 高 2.8–9.8pp，初始失败 SWE 毕业率 +10.8pp）/ Solve Vision with Code `2611.34813`（500 实例；闭源 agent 0.923/0.894/0.893，各比最强视频模型高 >0.22，开源最好 GLM-5 0.572）；5 查询全 `200` + atom（`published` 上界 `2026-11-25T18:59:59Z`≈45h，去重后候选 142），abs 5/5 `200`，五 ID 查重 0 命中。④ B +3 → 452：Sparse Transformers `1904.10509`（3,468）/ DALL·E `2102.12092`（6,727）/ MLP-Mixer `2105.01601`（4,393，NeurIPS 2021）；API + atom + OpenAlex 3/3 `200`（查询日 2026-11-28），查重 0 命中；⚠️ `2206.10658` 实测为 ART、`2206.07682` 已在表内 ⇒ 弃。⑤ 作者网 +3 → 419（X 仍 164）：#417 Zhiyao Xie（HKUST，A 级 `eezhiyao@ust.hk`，X 未找到）/ #418 Ling Pan（HKUST，A 级 `lingpan@ust.hk`，X 未找到）/ #419 Wenrui Zhou（HKUST，无邮箱，X 未找到）；同一 DiversePlace ⇒ 只发资深作者。⑥ 发信 +1 → 189（今日 1/12）：#189 Zhiyao Xie 中文 248 汉字 `SENT OK 00:03:59`；落款两行；专属细节 = 质量门控多样性门限 / HPWL oracle 偏差 / 归档下游敏感度 / 扩张时域课程；与 #186/#188 零共用。⑦ 交付：`research/2026-11-28.md` · `daily/2026-11-28.html` · `daily/index.html` · `PAPERS.md` #450–#452 + 快照 452 · `AUTHORS.md` #417–#419 + 计数 419/164 · `发送记录.md` §15/§16 · drafts/bodies 各 1 · `SEEN.md`/`papers.jsonl` +5。详见 `daily-memories-research/2026-11-28.md`。 —— **第二百七十四轮**：① 背景：03:00–18:00 六窗 loop 均按时唤醒，但 opencode 返回 `Error: Insufficient Balance`（重试 1 次仍失败）⇒ 六窗无产出、无提交（infra 额度失败，非本线逻辑）。② 回信再核（IMAP 只读）：INBOX **70**（00:2x 为 69 ⇒ +1 = 已知 #187 Petar 回复，已落盘 `replies/1710.10903.md`）；`SINCE 26-Nov` 6 封；无新实质回信、无新退信。③ 累计（188）：实质 8 信 / 7 人 ≈4.3% · 自动 1 · 退信 9 · 无应答>14d 32 · 未到期 138 ⇒ 8+1+9+32+138=188 ✔。④ B +3 → 449：LSSL/S4 `2110.13985`（1,300，NeurIPS 2021）/ GLU `1612.08083`（1,589）/ P-Tuning `2103.10385`（1,626，AI Open 2023）；arXiv API `200` + atom + OpenAlex 3/3 `200`；查重 0 命中。⚠️ 候选 RTLLM `2309.05076` 实测无关、真 ID `2308.05345` 已在表内 ⇒ 弃。⑤ 作者网 +3 → 416（X 162→164）：#414 Jie Tang（A 级 `jietang@tsinghua.edu.cn`，X `@jietang` 双源）/ #415 Michael Auli（无邮箱，X `@MichaelAuli` 双源，仅建档）/ #416 Zhilin Yang（主页 200 无邮箱/无本人 X，仅建档）。⑥ 发信 +1 → 188（今日 4/12）：#188 Jie Tang 中文 219 汉字 `SENT OK 21:04:58`；落款两行；专属细节 = prompt encoder + anchor / prompt 长度 / LoRA 顺序；与 #185/#186/#187 零共用。⑦ 交付：`research/2026-11-27.md` 21:00 节 · `daily/2026-11-27.html` 21:00 块 · `daily/index.html` 当日行 · `PAPERS.md` #447–#449 + 快照 449 · `AUTHORS.md` #414–#416 + 计数 416/164 · `发送记录.md` §13/§14 · drafts/bodies 各 1。详见 `daily-memories-research/2026-11-27.md`。
- **2026-11-27（本地 00:2x · 00:2x 补轮 · r273 · A 0 新收 ＋ B +3 → 446 ＋ 作者网 +3 → 413（X 162）＋ 发信 +1 → 187（今日 3/12）＋ 回信再核 0 新）** —— **第二百七十三轮**：① 回信再核（IMAP 只读）：INBOX **69** 持平；`SINCE 26-Nov` 5 封（腾讯云 / Ollama / 已知 #183 退信 / Facebook / 招聘群发）；无新实质、无新退信。② 累计（187）：实质 8 信 / 7 人 ≈4.3% · 自动 1 · 退信 9 · 无应答>14d 32 · 未到期 137 ⇒ 8+1+9+32+137=187 ✔。③ A 轨 0 新收（今日 5/5 已满，不凑第 6 篇）。④ B +3 → 446：OpenAI Gym `1606.01540`（9,534）/ GAT `1710.10903`（24,761，ICLR 2018）/ MobileNetV2 `1801.04381`（37,626，CVPR 2018）；arXiv API `200` + atom（3 entries，`published` 逐字）+ OpenAlex 3/3 `200`；查重 0 命中。⑤ 作者网 +3 → 413（X 162）：#411 Petar Veličković（A 级 `petarv@google.com`，X `@PetarV_93` 双源）/ #412 Greg Brockman（无公开邮箱，X `@gdb` 双源，仅建档）/ #413 Mark Sandler（停放页无邮箱，仅建档）。⑥ 发信 +1 → 187：#187 Petar Veličković 英文 194 词 `SENT OK 00:22:09`；落款两行；GAT 专属细节（`e_ij` / `K=8` / GATv2 静态注意力）；今日 3/12。⑦ 交付：`research/2026-11-27.md` 补轮节 · `daily/2026-11-27.html` 补轮块 · `daily/index.html` 当日行 · `PAPERS.md` #444–#446 · `AUTHORS.md` #411–#413 · `发送记录.md` §11/§12 · drafts/bodies 各 1。详见 `daily-memories-research/2026-11-27.md`。
- **2026-11-27（本地 00:0x · 00:00 时窗 · 🅰 **A 轨收满 5/5** ＋ 🅱 B 轨第一百二十五轮 +3 → 443 ＋ 作者网 +3 → 410（X 160）＋ 发信 2 封 → 186（今日 2/12）＋ 回信再核：0 新实质 / 0 新退信）** —— **第二百七十二轮**：① 回信再核（IMAP 只读）：INBOX **69 封**（21:00 为 71 ⇒ 少 2，本线只读未删信，推测邮箱端清理，如实记）；`SINCE 26-Nov` 5 封 = 腾讯云 / Ollama / 系统退信（已知 #183）/ Facebook / 招聘群发；无新实质回信、无新退信。② 累计（186）：实质 **8 信 / 7 人 ≈4.3%** · 自动 1 · 退信 9 · 无应答>14d **32** · 未到期 **136**；#22–#32（11-13 发出，11 封）今日满 14 天转无应答。③ A 轨 **5/5**（72h，15 查询全 `200` + atom，去重后候选 242）：Kolpona `2611.33973` / AgentDRC `2611.31876` / ZeroHero `2611.34635` / RoboEvo² `2611.34675` / Over-edit `2611.34875`；API `id_list` `200` + 5 entries，abs 页 4/5 `200`（RoboEvo² 3 次 SSL `000` ⇒ 以 API 为准），Over-edit PDF `200`/546,699 B/30 页 + pdftotext 复核 p.1/p.7；五 ID 查重 0 命中。④ B +3 → 443：MAGE `2412.07822`（153，DAC 2025 口径，<500 按本领域权威收）/ NTM `1410.5401`（3,139）/ HER `1707.01495`（2,803，NeurIPS 2017）；abs 3/3 `200` + OpenAlex 3/3 `200`（查询日 2026-11-27）；三 ID 查重 0 命中。⑤ 作者网 +3 → 410（X 160）：#408 Alex Graves（A 级 `graves@cs.toronto.edu`）/ #409 Jishen Zhao（A 级 `jzhao@ucsd.edu`）/ #410 Yujie Zhao（B 级 PDF 地址、仅建档）；三人 X 均未找到、不猜。⑥ 发信 2 → 186： #185 英文 197 词 `SENT OK 00:09:21` / #186 中文 218 汉字 `SENT OK 00:09:25`；落款两行、其后无行；两封开头句与问句零共用。⑦ 交付：`research/2026-11-27.md` · `daily/2026-11-27.html`（6 线建议齐全；news_ready 1 / voice_ready 0）· `daily/index.html` 新行 · `PAPERS.md` #441–#443 · `AUTHORS.md` #408–#410 · `SEEN.md` +5 · `papers.jsonl` +5 · `发送记录.md` §9/§10 + #22–#32 转无应答 · drafts/bodies 各 2。详见 `daily-memories-research/2026-11-27.md`。
- **2026-11-26（本地 21:0x · 21:00 时窗 · 🅰 A 轨 0 收（5/5 已满）＋ 🅱 B 轨第一百二十四轮 +3 → 440 ＋ 作者网 +3 → 407（X 160）＋ 发信 0（今日 12/12）＋ 回信再核：0 新实质回信、0 新退信）** —— **第二百七十一轮**：① 回信再核（IMAP 只读）：INBOX **71 封**（与 18:00 持平、+0）；无新实质回信、无新退信。② 累计（184）：实质 **8 信 / 7 人 ≈4.3%** · 自动 1 · 退信 9 · 无应答>14d 21 · 未到期 145。③ B +3 → 440（补真空白）：VGG `1409.1556`（**111,603**，2014/ICLR 2015）/ Focal Loss `1708.02002`（**10,051**，ICCV 2017）/ A3C `1602.01783`（**11,372**，ICML 2016）；abs 3/3 `200` + OpenAlex 3/3 `200`；三 ID 查重 0 命中。⚠️ 先误猜 3 个无关 ID（1904.08478/2312.05303/2211.16495，abs 核实无关）⇒ 改标题检索得真 ID。④ 作者网 +3 → 407（X 160）：#405 Zisserman（A 级 `az@robots.ox.ac.uk`）/ #406 Simonyan（仅建档）/ #407 Tsung-Yi Lin（A 级 + X `@TsungYiLinCV` 双源）。⑤ 发信 0（今日 12/12）。⑥ 交付：`PAPERS.md` #438–#440 + 快照 440；`AUTHORS.md` #405–#407；`发送记录.md` §8；`daily/2026-11-26.html` 21:00 节；`research/2026-11-26.md` §21:00；`daily/index.html` 当日行。详见 `daily-memories-research/2026-11-26.md`。
- **2026-11-26（本地 18:0x · 18:00 时窗 · 🅰 A 轨 0 收（5/5 已满）＋ 🅱 B 轨第一百二十三轮 +3 → 437 ＋ 作者网 +3 → 404（X 159）＋ 发信 0（今日 12/12）＋ 回信再核：+1 退信、0 新实质回信）** —— **第二百七十轮**：① 回信再核（IMAP 只读）：INBOX **71 封**（15:00 为 67 ⇒ +4：Ollama/Facebook/招聘群发 + 1 退信）；**无新实质回信**。新退信 **#183**（`lqiang@cs.utexas.edu`，Rectified Flow）15:10:33 被 `cs.utexas.edu` 以 `550 5.7.1 Blocked by SpamAssassin` 拦截 ⇒ 地址有效、反垃圾拦截，改判 `退信(反垃圾拦截)`。② 累计（184）：实质 **8 信 / 7 人 ≈4.3%** · 自动 1 · **退信 9** · 无应答>14d 21 · 未到期 145（=184 ✔）。③ B +3 → 437：MobileNets `1704.04861`（34,220）/ TD3 `1802.09477`（9,037）/ pix2pix `1611.07004`（28,513）；abs 3/3 `200` + OpenAlex 3/3 `200`；三 ID 查重 0 命中。④ 作者网 +3 → 404（X 159）：#402 Phillip Isola（A 级 `philipi@mit.edu`）/ #403 Scott Fujimoto（A 级未找到、仅建档）/ #404 Alexei Efros（A 级 `efros@eecs.berkeley.edu`）；三人 X 均未找到、不猜。⑤ 发信 0（今日 12/12 已满，只建档）。⑥ 交付：`发送记录.md` §18:00 + #183 改判 + 累计 9/145；`replies/README.md` 增量；`PAPERS.md` #435–#437；`AUTHORS.md` 404 + #402–#404；`daily/2026-11-26.html` 18:00 节；`research/2026-11-26.md` §18:00；`daily/index.html` 当日行。详见 `daily-memories-research/2026-11-26.md`。
- **2026-11-26（本地 15:0x · 15:00 时窗 · r269）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-26.md`「r269」；结论不变（回信核验首落地：实质 **7 人 / 8 封信 ≈4.3%**；B +3 → 434；作者网 401；发信 #183/#184 → 184，今日 12/12）。
- **2026-11-26（本地 12:0x · 12:00 时窗 · 🅰 A 轨 0 收（5/5 已满）＋ 🅱 B 轨第一百二十一轮 +3 → 431 ＋ 作者网 +3 → 398（X 158）＋ 发信 2 封 → 182（今日 10/12）＋ 回信率 0/182）** —— **第二百六十八轮**：① 网络：B abs 3/3 `200`（41,755 / 42,768 / 44,035 B，`citation_title` + `citation_date` 逐字；ViT `comments` 明文 *ICLR camera-ready*，VAE / Neural ODE `comments` 为空）+ OpenAlex 3/3 `200`（47,417 / 8,138 / 71,599，查询日 2026-11-26；Neural ODE = conference-paper / NeurIPS）；X 经代理 `200`（RickyTQChen / giffmana / wellingmax）；`x.com` 自检 `200`；A 列表未重复请求。② B +3 → 431：VAE `1312.6114`（ICLR 2014 社区口径，47,417；重参数化变分下界 → SGVB + recognition model）/ Neural ODE `1806.07366`（NeurIPS 2018，8,138；参数化导数 + 黑盒求解器 + 常数显存 + 伴随法 + CNF）/ ViT `2010.11929`（ICLR 2021，71,599；patch 序列 + 纯 Transformer）；三 ID 查重 0 命中。③ 作者网 +3 → 398（X 156 → 158）：#396 Max Welling（UvA 页明文 `m.welling@uva.nl` ⇒ 已发信 #181；X `@wellingmax` 单源待核不计入）/ #397 Ricky T. Q. Chen（`rtqichen.github.io` 明文 gmail + X 双源 ⇒ 已发信 #182，中文）/ #398 Lucas Beyer（无邮箱、X `@giffmana` 双源 ⇒ 仅建档）；VAE 一作 Kingma 已在 #99/#363，去重不新增。④ 发信 2 → 182（今日 10/12）：#181 荷兰语称谓 + 英文 166 词 `SENT OK 12:04:18` / #182 中文 229 汉字 `SENT OK 12:04:22`；落款两行、其后无行；正文无项目名；两封开头句/三问句式零共用。⑤ 回信率 0/182（已回复 0 / 无应答>14d 21 / 未到期 161）；本轮无新增到期；`replies/` 仍只有 `README.md`。⑥ voice_ready 0 / news_ready 0。⑦ 交付：`PAPERS.md` #429–#431 + `AUTHORS.md` #396–#398 + `research/2026-11-26.md` §121 + `daily/index.html` 当日行（431 · 398 · 158 · 182 · 0/182）+ `发送记录.md` §12:0x + draft / body 各 2。⑧ 运维根因补足：显示名 = `~/.hr_smtp` 的 `name` 字段 `AI+EDA 招聘 · 自动`（`~/hr_mail.py` L29/36）⇒ 本线不改他线配置，待运维改为学术署名。
- **2026-11-26 09:1x 补轮（r267）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-26.md`（B +3 → 428 CycleGAN / ControlNet / EfficientNet；作者网 395；发信 #179 / #180；回信 0/180）。
- **2026-11-26 09:00 时窗（r266）**：原文已归档 → 同上（B +3 → 425 GCN / WaveNet / PixelRNN；作者网 392；发信 #178；回信 0/178）。
- **2026-11-26 06:1x 补轮（r265）**：原文已归档 → 同上（B +3 → 422 TRPO / DenseNet / Score-SDE；作者网 389；发信 #176 / #177；回信 0/177）。
- **2026-11-26 06:0x（第二百六十四轮 · r264）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-26.md`「归档 · r269 后折出」；结论不变（B +3 → 419 Adapter / Flow Matching / PipeDream；作者网 386；发信 #174/#175；回信率 0/175）。
- **2026-11-26 03:2x 补轮（第二百六十三轮 · r263）**：原文已归档 → 同上（B +3 → 416 Prefix-Tuning / Prompt Tuning / ELMo；作者网 383；发信 0；回信率 0/173）。
- **2026-11-26 03:00 时窗（r262）**：原文已按 §5 滚动归档（r275 后折出）→ `daily-memories-research/2026-11-26.md`；结论不变。
- **2026-11-25 22:4x loop 重启补跑（r260）**：原文已按 §5 滚动归档（r275 后折出）→ `daily-memories-research/2026-11-25.md`；结论不变。
- **2026-11-25 09:00 时窗（r259）**：原文已按 §5 滚动归档（r275 后折出）→ `daily-memories-research/2026-11-25.md`；结论不变。
- **2026-11-25 06:0x（第二百五十八轮）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-25.md`；结论不变（B +3 → 401 Imagen / Llemma / MMLU-Pro；作者网 368；发信 #167/#168；回信率 0/168）。
- **2026-11-25 03:0x（第二百五十七轮）**：原文已归档 → 同上；结论不变（A +2 → 5/5；B +3 → 398 VAE / PAL / TinyLlama；作者网 365；发信 #166 Luyu Gao；回信率 0/166）。
- **2026-11-25 00:0x（第二百五十六轮）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-25.md`「归档 · r267 后折出」；结论不变（B 轨 +3 → 395；作者网 +3 → 362；发信 1 → 165；回信率 0/165，首 #1–#9 转无应答）。
- **2026-11-24 21:0x（第二百五十五轮）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-24.md`「归档 · r266 后折出」；结论不变（B 轨 392 / 作者网 359 / 发信 #164 / 回信率 0/164）。
- **2026-11-24 06:0x & 09:0x & 15:0x（已折出）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-24.md`（归档 · r265 后折出；含本 r265 折出的 15:0x 原文）。



- **2026-11-24 00:0x & 03:0x（已折出）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-24.md`「归档 · MEMORY 滚动（r259 后折出）」；结论不变，勿以指针替代原文。
- **2026-11-23 18:0x ~ 2026-11-22 18:0x（更早 8 条）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-23.md`「归档 · MEMORY 滚动（r249 后折出）」；结论不变，勿以指针替代原文。

- **2026-11-22 06:0x ~ 2026-11-19（更早轮次）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-22.md`「归档 · MEMORY 滚动（第九十四轮后折出）」与 `daily-memories-research/2026-11-21.md` / `2026-11-20.md` / `2026-11-19.md` / `2026-11-18.md`；结论不变，勿以指针替代原文。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
