# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 回信跟踪已真实打通）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
  已完成:       [r290 · 2026-11-29 00:0x 定时唤醒（新一天首窗）：A 轨 **+5 → 今日 5/5**（MoLT `2611.34923` / AgenTAP `2611.34943` / Can image gen help visual reasoning `2611.34935` 科普 / DRBench Pro `2611.34852` / Repairing Distilled LMs `2611.34831`）· B **+3 → 476**（Deep Compression `1510.00149` **9,997** / Lottery Ticket `1803.03635` **3,391** / VQ-GAN `2012.09841` **5,237**）· 作者网 **+3 → 443**（X **+3 → 172**）· 发信 **+1 → 197**（#197 Jonathan Frankle，英文 169 词，`SENT OK 00:05:00`，今日 1/12）· 回信 0 新（INBOX 71 持平）]
  前一（r289）: 21:12 伪重试唤醒（0 重复工作 + 修 loop 假阳性根因：MEMORY 脱敏 + 裁剪 36.5→31.7KB），INBOX 71
  回信累计（197）: 实质 8 信 / 7 人 ≈4.1% · 自动 1 · 退信 9 · 无应答(>14d) 32 · 未到期 147 ⇒ 197 ✔；送达 8/188 ≈4.3%
  ① 本窗 voice_ready **0**（A 无本人推文原文；新增 @songhan_mit / @jefrankle / @robrombach 均无本人推文原文，宁缺勿滥）/ news_ready **1**（Can image gen help visual reasoning：13 对模型平均 −3.7pp）
  ② A 轨核验：arXiv API 6 查询均 `200` + atom + 真实 `published`（上界 `2026-11-25T18:59:58Z`，约 50h<72h）+ abs 5/5 `200`；五 ID 收录前查重 0 命中
  当前动作:     ✅ r290 已完成：A 5/5 + B 476 + 作者网 443（X 172）+ 发信 #197 + 回信再核（INBOX 71，+0）+ 日报 HTML + index + 6 线建议 + MEMORY 心跳；待 commit+push
  下一步:       ① 下一时窗 **03:00**：A 轨今日 5/5 已满 ⇒ 0 新收（守「宁少勿凑」）；② B 轨补真空白（先按标题核 ID，勿信记忆 ID）；③ 作者网 +3（优先 EDA / 可核邮箱）；④ 每轮先读收件箱；⑤ 发信今日 1/12，可继续（≤12/日）；⑥ 运维待办（显示名 / 额度 / 任务书 44KB 只读 / loop FATAL_RE 假阳性 patch）
  本轮新增:     r290：A +5 · B +3 · 作者网 +3（X +3）· 发信 +1 · 回信 0 新（INBOX 71 持平；8 信/7 人≈4.1%）
  阻塞:         ① 🟡 **loop 假阳性（历史复发 7 次）**：r289 已脱敏 MEMORY 断源，预期不再复发；脚本仍待运维 patch（`grep -viE 'FATAL_RE=|grep -qiE'` 或 `rc!=0 && grep` 双条件）；② 显示名仍 `AI+EDA 招聘 · 自动`（`~/.hr_smtp` name）⇒ 需运维改学术署名；③ SMTP 只发不收 ⇒ 每轮须 agent 主动 IMAP 只读；④ `WATCH_RESEARCH_TASK.md` **44 KB 超红线且只读** ⇒ 需授权；⑤ 台账 #164–#170 缺口已查明（`发送记录.md:1438`，不臆造补齐）；⑥ #168/#175 地址有效性存疑；⑦ loop 兜底 `git add` 范围待核查；⑧ SPEC 仅三值，实际出现第 4 类「退信(反垃圾/无效)」待追认
  ERROR_COUNT:  124（r290 本身 0 错误；历史累计口径不变，loop 假阳性不计入）
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
- **上次采集窗口**：`2026-11-29 00:0x`（**第二百九十轮 · 00:00 新一天首窗**：A 轨 **+5 → 今日 5/5**（MoLT `2611.34923` / AgenTAP `2611.34943` / Can image gen help visual reasoning `2611.34935` / DRBench Pro `2611.34852` / Repairing Distilled LMs `2611.34831`）；B 轨 **+3 → 476**（Deep Compression / Lottery Ticket / VQ-GAN）；作者网 **+3 → 443**（X 172）；发信 **+1 → 197**（#197 Jonathan Frankle，英文 169 词，今日 1/12）；**回信再核**：INBOX 71（+0）、无新实质回信、无新退信 ⇒ 退信累计 9）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`papers.jsonl` 现 **427 行**（A 轨结构化台账；`SEEN.md` 为唯一防重台账；本日 A 轨 +5 → 今日 5/5）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**476 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**一百三十六轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**443 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`。**回信摘录 `research/mail/replies/<arXiv_ID>.md`（2026-11-26 起真实落盘 8 份）**


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-29（本地 00:0x · 00:00 新一天首窗 · r290）** —— **第二百九十轮**：① 回信再核（IMAP 只读）：INBOX **71**（r289 为 71 ⇒ **+0**）；`SINCE 27-Nov` 3 封（#187 Petar 已知 / Ultralytics / ChatGPT 营销）、`SINCE 29-Nov` **0 封**；**无新实质回信、无新退信**。② 累计（197）：实质 **8 信 / 7 人 ≈4.1%** · 自动 1 · 退信 9 · 无应答(>14d) 32 · 未到期 147 ⇒ 8+1+9+32+147=197 ✔；送达 8/188 ≈4.3%。③ A 轨 **+5 → 今日 5/5**（新一天额度重置）：MoLT `2611.34923`（loop 架构；700M 验证 CE token 效率 1.7×）/ AgenTAP `2611.34943`（VLM agent 点追踪）/ Can image gen help visual reasoning `2611.34935`（**科普**；13 对模型平均 −3.7pp）/ DRBench Pro `2611.34852`（知识树 benchmark，44,102 细则，最好 57.04%）/ Repairing Distilled LMs `2611.34831`（PBRF 修复蒸馏小模型可信性，最多 +8%）；arXiv API 6 查询均 `200` + atom + `published`（上界 `2026-11-25T18:59:58Z`，约 50h<72h）+ abs 5/5 `200`；五 ID 查重 0 命中。④ B +3 → 476：Deep Compression `1510.00149`（**9,997**，ICLR 2016 oral；剪枝+量化+Huffman，存储降 35×–49× 不掉精度）/ Lottery Ticket `1803.03635`（**3,391**，ICLR 2019；中奖彩票 <10–20%）/ VQ-GAN `2012.09841`（**5,237**，CVPR 2021；离散词表+Transformer 兆像素语义合成）；arXiv API + abs 页 + OpenAlex 各 3/3 `200`（查询日 2026-11-29），查重 0 命中。⑤ 作者网 +3 → 443（X +3 → 172）：#441 Song Han（MIT，B 级 `hanlab@mit.edu`，X `@songhan_mit` 双源）· #442 Jonathan Frankle（Databricks，A 级 `jfrankle@databricks.com`，X `@jefrankle` 双源；已发信 #197）· #443 Robin Rombach（Black Forest Labs，X `@robrombach` 双源，无 A 级邮箱仅建档）。⑥ 发信 +1 → 197（今日 1/12）：#197 Jonathan Frankle 英文 **169 词** `SENT OK 00:05:00`；专属细节 = winning ticket <10–20% / 高于该规模更快 / MNIST-CIFAR10 口径；三问 = warmup+迭代预算 / 结构化稀疏阈值 / 非平稳下初始化 vs 数据顺序；落款两行、与 #195/#196 零共用。⑦ voice_ready 0 / news_ready 1。⑧ 交付：`research/2026-11-29.md` · `daily/2026-11-29.html`（新建）+ `daily/index.html`（新行 + 旧行降级 + footer）· `PAPERS.md` #474–#476 + 快照 476 · `AUTHORS.md` #441–#443 + 计数 443/172 · `发送记录.md` §31/§32 · drafts/bodies 各 1。详见 `daily-memories-research/2026-11-29.md`。
- **2026-11-28（本地 21:12 · 伪重试唤醒 · r289 · 0 重复工作 + **修 loop 假阳性根因**：MEMORY 脱敏断源 + 裁剪至 31.7KB）** —— **第二百八十九轮（非时窗）**：① 事实链：r288 于 **21:07:18** `opencode returned (exit 0)` 且已 push（`bafe3c9888`，`0/0`），loop 对 r288 日志再误命中 `FATAL_RE`（`watch_research_loop.sh:167`）⇒ **21:12** 多烧本轮（本日第 7 次：r277/r279/r281/r283/r285/r287/r289），**非额度/网络故障**。② **根因补全并修复**：真正触发源 = agent 每轮必读的 MEMORY 里逐字抄了 4 个 FATAL 触发串（命令未找到 ×2 / 用法提示 / API 调用错误），读进 `$CLINE_LOG` 即必中；r288 为正常时窗仍触发即铁证。r289 已把 MEMORY 内这 4 串脱敏（连字符/去冒号/描述式），逐 token 复检 `REMAINING_BAD=[]`；**脚本未改**（守「不动 loop」禁令）。③ 只做必修项：IMAP 只读复核 **INBOX 71**（r288 为 71 ⇒ +0）；`SINCE 27-Nov` 3 封（#69 Petar 已知 / #70 Ultralytics / #71 ChatGPT 营销），`SINCE 28-Nov` 1 封（=#71）；**0 新实质回信、0 新退信**；累计（196）不变：实质 8 信/7 人 ≈4.1% · 自动 1 · 退信 9 · 无应答>14d 32 · 未到期 146。④ 顺带裁剪：流水折叠 r273/r272/r271 为 1 行指针（原文已在 daily），MEMORY 36.5KB → 31.7KB（≤32KB）。⑤ 交付：仅本 MEMORY + `daily-memories-research/2026-11-28.md` r289 段 + commit/push；**未发信、未新增论文、未改任务书/loop**。
- **2026-11-28（本地 21:0x · 21:00 时窗 · r288 · 🅰 A 轨 0 新收〔今日 5/5 已满〕＋ 🅱 B +3 → 473 ＋ 作者网 +3 → 440（X 169）＋ 发信 +1 → 196（今日 8/12）＋ 回信再核 0 新）** —— **第二百八十八轮**：① 回信再核（IMAP 只读）：INBOX **71**（18:00 为 70 ⇒ **+1**，为 ChatGPT 营销订阅，非作者邮件）；`SINCE 26-Nov-2026` 8 封；`SINCE 28-Nov-2026` 1 封；**无新实质回信、无新退信**。② 累计（196）：实质 **8 信 / 7 人 ≈4.1%** · 自动 1 · 退信 9 · 无应答(>14d) 32 · 未到期 146 ⇒ 8+1+9+32+146 = 196 ✔；送达 8/187 ≈4.3%。③ A 轨 **0 新收**：今日已满 5/5，守「宁少勿凑」，不凑第 6 篇。④ B +3 → 473：BigGAN `1809.11096`（**5,601**，2018-09-28；正交正则化 + truncation trick，ImageNet 128×128 IS 166.5 / FID 7.4）/ LLM4EDA `2401.12224`（**118**，2023-12-28；**<500 按「本领域权威 / LLM-for-EDA 分类综述」收**，chatbot / HDL 与脚本生成 / HDL 验证与分析三类）/ Dawn of AI-Native EDA `2403.07257`（**100**，2024-03-12；OpenAlex 记 Science China Information Sciences；**<500 按「本领域权威 / 方向性论文」收**，AI4EDA → AI-native EDA + LCMs 统一 spec/RTL/netlist/layout）；arXiv API `200` + atom（`published` 逐字 `2018-09-28T15:38:49Z` / `2023-12-28T15:09:14Z` / `2024-03-12T02:26:30Z`）+ abs 页 3/3 `200`（41,711 / 42,933 / 51,205 B）+ OpenAlex 3/3 `200`（查询日 2026-11-28）；查重 0 命中。⚠️ **记忆里的 4 个候选 ID（2308.09853 / 2308.12234 / 2401.12244 / 2203.10008）经 arXiv API 核实全部无关** ⇒ 改按标题检索得真 ID（2309.07544 VerilogEval 与 2208.01040 CircuitNet 已在表；最终取 1809.11096 / 2401.12224 / 2403.07257）。⑤ 作者网 +3 → 440（X +1 → 169）：#438 Qiang Xu（CUHK CSE，A 级 `qxu@cse.cuhk.edu.hk`〔本人主页 200 / 9,571 B 反爬明文〕，X 未找到；已发信 #196）/ #439 Jeff Donahue（Google DeepMind，无 A 级邮箱〔主页 JS 混淆〕，X `@jeffdonahue` 双源；仅建档）/ #440 Mingxuan Yuan（华为，B 级 `yuan.mingxuan@huawei.com`〔论文 contact 单源〕，X 未找到；仅建档，守「同一论文 ≤1」）。⑥ 发信 +1 → 196（今日 8/12）：#196 Qiang Xu 中文 **202 汉字** `SENT OK 21:03:56`；落款两行（`祝好，` / `Yang Liu`，其后无行）；专属细节 = 四类数据 → LCM / AI4EDA → AI-native EDA / shift-left 的 PPA 或迭代轮次量化 / 多模态判分不泄题；与 #195 零共用。⑦ voice_ready 0 / news_ready 0（A 无新收；@jeffdonahue 无本人推文原文）。⑧ 交付：`research/2026-11-28.md` 21:00 节 · `daily/2026-11-28.html` 21:00 块 + header/footer/附录 · `daily/index.html` 当日行 + footer · `PAPERS.md` #471–#473 + 快照 473 · `AUTHORS.md` #438–#440 + 计数 440/169 · `发送记录.md` §29/§30 · drafts/bodies 各 1。详见 `daily-memories-research/2026-11-28.md`。
- **2026-11-28 18:18 · 伪重试 · r287**：原文已归档 → `daily-memories-research/2026-11-28.md`；结论不变（伪重试，0 重复工作，INBOX 70 持平）。
- **2026-11-28 18:0x · r286**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-28.md`；结论不变（A 0〔5/5〕· B +3 → 470〔Rainbow/IMPALA/Chip-Chat〕· 作者网 +3 → 437（X 168）· 发信 #195 Jason Blocklove 英文 198 词 · 回信 0 新）。
- **2026-11-28 12:0x · r282**：原文已归档 → `daily-memories-research/2026-11-28.md`；结论不变（A 0〔5/5〕· B +3 → 464〔Rethinking Gen/SSD/GroupNorm〕· 作者网 +3 → 431 · 发信 #193 Tsung-Yi Lin 中文 209 汉字 · 回信 0 新）。
- **2026-11-28 09:13 · 伪重试 · r281**：原文已归档 → `daily-memories-research/2026-11-28.md`；结论不变（伪重试，0 重复工作，INBOX 70 持平）。
- **2026-11-28 09:0x · r280**：原文已归档 → `daily-memories-research/2026-11-28.md`；结论不变（A 0〔5/5〕· B +3 → 461〔Gumbel-Softmax/WGAN/DDPG〕· 作者网 +3 → 428（X +1）· 发信 #192 Ben Poole 英文 182 词 · 回信 0 新）。
- **2026-11-28（本地 06:10 · 伪重试唤醒 · r279 · 0 重复工作：A/B/作者网/发信均不重做；仅 IMAP 复核 + 假阳性根因定位）** —— **第二百七十九轮（非时窗）**：① 事实链：r278 于 **06:05** `opencode returned (exit 0)` 且已 push（`e5deb4514e`、`ahead/behind 0/0`），loop 对 r278 日志**再误命中 `FATAL_RE`**（`watch_research_loop.sh:167`）⇒ **06:10** 多烧本轮（与 r277 03:10 同类）。② 根因**实测定位**：`FATAL_RE` 的 15 个 token（含 `cline-not-found` / `opencode-not-found` / `USAGE` / `AI-API-call-error`）会因 agent 用 `grep -n FATAL_RE` 读 loop 脚本而原样进入 `$CLINE_LOG` ⇒ `grep -qiE "$FATAL_RE"` 必中；**非额度/网络故障**。③ 建议（未改脚本）：`grep -viE 'FATAL_RE=|grep -qiE' "$CLINE_LOG" | grep -qiE "$FATAL_RE"` 或 `rc!=0 && grep`。④ 只做必修项：IMAP 只读复核 **INBOX 70**（06:00 为 70 ⇒ +0）；`SINCE 26-Nov` 7 封均已知非作者邮件；**0 新实质回信、0 新退信**；累计（191）不变：实质 8 信/7 人 ≈4.3% · 自动 1 · 退信 9 · 无应答>14d 32 · 未到期 141。⑤ 交付：仅本 MEMORY + `daily-memories-research/2026-11-28.md` r279 段 + commit/push；**未发信、未新增论文、未改任务书/loop**。
- **2026-11-28 06:0x · r278**：原文已归档 → `daily-memories-research/2026-11-28.md`；结论不变（A 0〔5/5〕· B +3 → 458〔GELU/Dreamer/XGBoost〕· 作者网 +3 → 425（X +2）· 发信 #191 Tianqi Chen 中文 279 汉字 · 回信 0 新）。
- **2026-11-28（本地 03:1x · 伪重试唤醒 · r277 · 0 重复工作：A/B/作者网/发信均不重做；仅 IMAP 复核 + 伪重试诊断）** —— **第二百七十七轮（非时窗）**：① 事实链：r276 于 **03:05:24** `opencode returned (exit 0)` 且已 push（`ahead=0 behind=0` / `push OK`），但 loop 对 r276 日志**误命中 `FATAL_RE`**（`watch_research_loop.sh:167`）⇒ 打印「检测到 opencode 失败/报错 → 本时窗内重试 1/1（sleep 300s）」⇒ **03:10:31 重新唤醒**（本窗）。② 判定为**伪重试**（非额度/网络故障）：故本窗**不重复** r276 的 A/B/作者网/发信。③ 只做必修项：IMAP 只读复核 **INBOX 70 封**（与 03:00 持平）、`SINCE 26-Nov` 7 封均为 26–27 Nov 已知非作者邮件、作者来信仍仅 #187 Petar ⇒ **0 新实质回信、0 新退信**；累计分账（190）不变：实质 8 信/7 人 ≈4.3% · 自动 1 · 退信 9 · 无应答>14d 32 · 未到期 140。④ 顺带销项：`发送记录.md:1438` 已载明 #164–#170 缺口成因（并发回滚未落盘）与 6 封可核收件人/论文/时间 ⇒ 缺口「有据可查、不臆造补齐」，运维如需补全 7 行须授权。⑤ 交付：仅本 MEMORY + `daily-memories-research/2026-11-28.md` r277 行 + commit/push；**未改任务书**、未发信、未新增论文。
- **2026-11-28 03:0x · r276**：原文已归档 → `daily-memories-research/2026-11-28.md`；结论不变（A 0〔5/5〕· B +3 → 455〔Show Attend/SQuAD/PointNet〕· 作者网 +3 → 422（X +1）· 发信 #190 Courville 英文 199 词 · 回信 0 新）。
- **2026-11-28（本地 00:0x · 00:00 时窗 · r275）**：原文已按 §5 滚动归档（r281 后折出）→ `daily-memories-research/2026-11-28.md`「归档 · r275」；结论不变（A 5/5 · B +3 → 452 · 作者网 419 · 发信 #189 Zhiyao Xie · 回信 0 新）。
- **2026-11-27 r273/r272 · 2026-11-26 r271**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-27.md`（r272/r273）/ `2026-11-26.md`（r271）；结论不变（r273 A0/B446/作者网413/发信#187 Petar；r272 A5/5/B443/作者网410/发信#185·#186；r271 A0/B440/作者网407/发信0）。
- **2026-11-26（本地 18:0x · 18:00 时窗 · r270）**：原文已按 §5 滚动归档（r278 后折出）→ `daily-memories-research/2026-11-26.md`；结论不变（A 0（5/5）· B +3 → 437 · 作者网 +3 → 404 · 发信 0（12/12）· +1 退信）。
- **2026-11-26（本地 15:0x · 15:00 时窗 · r269）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-26.md`「r269」；结论不变（回信核验首落地：实质 **7 人 / 8 封信 ≈4.3%**；B +3 → 434；作者网 401；发信 #183/#184 → 184，今日 12/12）。
- **2026-11-26 12:0x ~ 2026-11-24 21:0x（更早 13 条，r268–r255）**：原文见 `daily-memories-research/2026-11-26.md` / `2026-11-25.md` / `2026-11-24.md`；结论不变。
- **2026-11-24 06:0x & 09:0x & 15:0x & 00:0x & 03:0x（已折出）**：原文均按 §5 滚动归档 → `daily-memories-research/2026-11-24.md`（r265 / r259 后折出）；结论不变，勿以指针替代原文。
- **2026-11-23 18:0x ~ 2026-11-22 18:0x（更早 8 条）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-23.md`「归档 · MEMORY 滚动（r249 后折出）」；结论不变，勿以指针替代原文。

- **2026-11-22 06:0x ~ 2026-11-19（更早轮次）**：原文见 `daily-memories-research/2026-11-22.md`（第九十四轮后折出）与 `2026-11-21.md` / `2026-11-20.md` / `2026-11-19.md` / `2026-11-18.md`；结论不变。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
