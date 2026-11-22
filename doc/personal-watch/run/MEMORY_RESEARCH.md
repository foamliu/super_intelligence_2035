# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r240 · 本地 2026-11-23 00:0x · 00:00 时窗：A 轨 0/5（72h 窗内无新公告，不凑数）＋ B 轨 +3 → 347 ＋ 作者网 +2 → 314 ＋ 发信 1 封 → 141 ＋ 回信率 0/141]
  ① 网络：`cat:cs.CL&max_results=5`（`--noproxy '*'` 直连 https）**`200` / 13,563 B / 5 entry / atom**；`published` 上界仍为 **`2026-11-19T18:57:25Z`**（**连续第 19 窗未前进**），距本窗约 **77h > 72h** ⇒ A 轨显式 0 篇、不拿超窗论文凑数；交叉核 cs.LG `18:59:53Z` / cs.CV `18:59:57Z` / cs.SE `18:54:19Z`（均 `200`）。
  ② B 轨 **+3 → 347**：Gopher `2112.11446`（**1,730**，预印本；280B dense，152 任务多数 SOTA，规模收益集中在阅读理解 / 事实核查 / 毒性识别，逻辑与数学推理收益小）/ CAMEL `2303.17760`（**2,892**，NeurIPS 2023；role-playing + inception prompting + task specifier，50×50 角色 × 10 任务 = **25,000** 段对话，四类协作失败）/ WebGPT `2112.09332`（**2,810**，预印本；GPT-3 + 文本浏览器，模仿学习 + 人类偏好拒绝采样，答案须带引用，ELI5 上 56% / 69% 胜）；arXiv `id_list` `200` + atom（12,641 B / 3 entry）+ abs 3/3 `200`（55,213 / 44,311 / 43,980 B，`citation_title` + `citation_date` 逐字）+ OpenAlex 3/3 `200`（查询日 2026-11-23，均 preprint）；三 ID 条目级查重 0 命中（PaLM / Voyager / Generative Agents / AutoGen 已在表内 ⇒ 剔除）。
  ③ 作者网 **+2 → 314**：#313 Guohao Li 李国豪（`guohao.li@eigent.ai` 取自本人主页 `ghli.org` `200` / 72,157 B 页内 `mailto:` 明文；X `@guohao_li` 双源 `200` / 195,418 B；反例 `guohao.ai` 为「国皓会展集团」同名站 ⇒ 拒用）/ #314 Bernard Ghanem（`bernard.ghanem@kaust.edu.sa` 取自 KAUST 官方页经代理 `200` / 57,887 B 页内明文；`@bernardghanem` / `@bernard_ghanem` 均同名他人 ⇒ X 未找到）。X 已核验 **122**（本轮 +1）。
  ④ 发信 **1 封**（累计 **141**）：#141 CAMEL 一作 Guohao Li，中文 **244** 汉字（`re.findall('[一-鿿]')` 逐字核），`SENT OK 00:04:47`；发前主页 `200` / 72,157 B 复核；落款严格两行 `祝好，` / `Yang Liu`，其后无行；正文无项目名；专属细节 = 25,000 段对话 + task specifier + 四类失败原名；三问分别回填 harness / designflow / zhulong；今日 1/12。
  ⑤ 回信率 **0 / 141**，**0 封到期**（最早 2026-11-25，#1–#7 剩 2 天）；`replies/` 仍只有 `README.md`；通道只发不收。
  ⑥ voice_ready **0**（X 推文页需登录态，未双源核验）/ news_ready **0**（2021–2023 方法论文，非本窗事件点）。
  ⑦ 交付：`daily/2026-11-23.html`（0/5 + B 轨 3 行 + 作者 + 信件段 + 6 线建议 6 条 + 附录 5 行）+ `daily/index.html` 当日行（0/5 · 347 · 314 · 122 · 141 · 0/141）+ `research/2026-11-23.md` + `PAPERS.md` #345–#347 + `AUTHORS.md` #313–#314 + `发送记录.md` §00:0x + draft / body 各 1。

当前动作:     ✅ 00:00 时窗闭环：A 轨 0/5（77h 超窗，显式 0 篇），B 轨 +3（Gopher / CAMEL / WebGPT），作者网 +2（Guohao Li / Bernard Ghanem），发信 1（CAMEL，中文 244），回信率 0/141。
下一步:       ① 03:00 时窗：先查公告批是否推进；若推进则按 72h 窗补 A 轨，未推进继续 0 篇并说明；② B 轨候选：HBM / JEDEC 一手、训练稳定性 spike 侧、检测后续（DINO-X 类）、视觉塔对照（InternViT 一代）、长上下文位置编码对照（NTK）；③ 11-25 首批到期 → #1–#7 转 `无应答(>14d)` 并做地址级别 × 论文年代分层；④ 运维：发件显示名 / SMTP 只发不收 / 任务书 44 KB 超红线。
补推记录:     2026-11-23 00:1x · 本轮 commit 前 `git pull --rebase --autostash`；若 push 被拒按 `fetch + rebase origin/main` 重试（最多 5 次），不 `add -A`。
本轮新增:     A 轨 0（0/5）· B 轨 +3（347）· 作者网 +2（314）· 作者信 +1（141）· voice_ready 0 · news_ready 0 · 回信率 0/141 · X 已核验 122
阻塞:         ① 🔴 发件显示名 `AI+EDA 招聘 · 自动`（最可能的 0 回信原因），需运维改配置；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到；③ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且 agent 只读 ⇒ 需授权；④ 公告批连续 19 窗未前进（A 轨 0 篇的唯一原因）；⑤ Gopher / WebGPT 一作无公开明文邮箱 ⇒ 只建档，不猜地址。
ERROR_COUNT:  118（本轮 0 新增）

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
- **上次采集窗口**：`2026-11-23 00:0x`（**第二百四十轮 · 00:00 时窗**：A 轨 0/5（`published` 上界 `2026-11-19T18:57:25Z`，距本窗约 77h > 72h ⇒ 不凑数）；B 轨第九十三轮 +3 → 347）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`363` 篇（A 轨；本窗 0 篇，未变）（11-20 A 轨 +5：`2611.24849` / `2611.24844` / `2611.24071` / `2611.24809` / `2611.24540`；`SEEN.md` 为唯一防重台账）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**347 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**七十六轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**314 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-23（本地 00:0x · 00:00 时窗 · 🅰 A 轨 0/5（77h 超窗，不凑数）＋ 🅱 B 轨第九十三轮 +3 → 347 ＋ 作者网 +2 → 314 ＋ 信 1 封 → 141 ＋ 回信率 0/141）** —— **第二百四十轮**：① 网络：`cat:cs.CL&max_results=5`（`--noproxy '*'`）`200` / **13,563 B / 5 entry** / atom；`published` 上界仍 **`2026-11-19T18:57:25Z`**（连续第 19 窗未前进），距本窗约 **77h > 72h** ⇒ A 轨显式 0 篇；交叉核 cs.LG / cs.CV / cs.SE 均 `200`（上界 `18:59:53Z` / `18:59:57Z` / `18:54:19Z`）。② B 轨 **+3 → 347**：Gopher `2112.11446`（**1,730**，预印本；280B dense / 152 任务 / 规模收益集中在阅读、事实核查、毒性识别，逻辑与数学推理收益小）/ CAMEL `2303.17760`（**2,892**，NeurIPS 2023；role-playing + task specifier，25,000 段对话，四类协作失败）/ WebGPT `2112.09332`（**2,810**，预印本；浏览器 + 模仿学习 + 人类偏好，答案带引用，ELI5 56% / 69% 胜）；`id_list` `200` + atom（12,641 B / 3 entry）+ abs 3/3 `200`（55,213 / 44,311 / 43,980 B，`citation_title` + `citation_date` 逐字）+ OpenAlex 3/3 `200`（查询日 2026-11-23）；三 ID 条目级查重 0 命中（PaLM / Voyager / Generative Agents / AutoGen 已在表内 ⇒ 剔除）。③ 作者网 **+2 → 314**：#313 Guohao Li 李国豪（`guohao.li@eigent.ai` 取自 `ghli.org` `200` / 72,157 B 页内 `mailto:` 明文；X `@guohao_li` 双源 `200` / 195,418 B；反例 `guohao.ai` 为同名会展公司 ⇒ 拒用）/ #314 Bernard Ghanem（`bernard.ghanem@kaust.edu.sa` 取自 KAUST 官方页经代理 `200` / 57,887 B 页内明文；两个同名 X 号均 3–4 followers ⇒ 判他人，X 未找到）；X 已核验 **122**。④ 发信 **1 封**（#141 CAMEL 一作 Guohao Li，中文 **244** 汉字，`SENT OK 00:04:47`；发前主页 `200` / 72,157 B 复核；落款两行、其后无行；正文无项目名；专属细节 = 25,000 段对话 + task specifier + 四类失败原名），累计 **141**、今日 1/12、待发队列空。⑤ 回信率 **0/141**，0 封到期（最早 2026-11-25）。⑥ voice_ready 0 / news_ready 0。⑦ 交付：`daily/2026-11-23.html`（0/5 + B 轨 3 行 + 作者 + 信件段 + 6 线建议 6 条 + 附录）+ `index.html` 当日行（0/5 · 347 · 314 · 122 · 141 · 0/141）+ `research/2026-11-23.md` + `PAPERS.md` #345–#347 + `AUTHORS.md` #313–#314 + `发送记录.md` §00:0x + draft / body 各 1。
- **2026-11-22（本地 18:0x · 18:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第九十二轮 +3 → 344 ＋ 作者网 +2 → 312 ＋ 信 0 封（今日 12/12 已满）＋ 回信率 0/140）** —— **第二百三十九轮**：① 网络：`cat:cs.CL&max_results=3`（`--noproxy '*'`）`200` / **8,529 B / 3 entry** / atom；公告批仍停在 **`2026-11-19T18:57:25Z`**（**连续第 18 窗未前进**，仍在 72h 窗内）⇒ A 轨 5/5 不凑第 6 篇。② B 轨 **+3 → 344**：word2vec `1301.3781`（**44,294**，preprint；CBOW / skip-gram，1.6B 词 <1 天，句法 + 语义相似度双榜 SOTA）/ Dropout `1207.0580`（**9,564**，preprint；每样本随机丢弃一半特征检测器阻断 co-adaptation）/ BLIP `2201.12086`（**8,544**，preprint；captioner + filter 自举清洗噪声图文对，检索 avg recall@1 +2.7% / CIDEr +2.8% / VQA +1.6%）；arXiv `id_list` `200` + atom（5,836 B / 3 entry）+ abs 3/3 `200`（40,906 / 40,988 / 42,767 B，`citation_title` + `citation_date` 逐字）+ OpenAlex 3/3 `200`（44,294 / 9,564 / 8,544，均 preprint，查询日 2026-11-22）；三 ID 三处查重 0 命中（Let's Verify `2305.20050` 已是表内 #159 ⇒ 剔除）。③ 作者网 **+2 → 312**：#311 Ruslan Salakhutdinov（`rsalakhu@cs.cmu.edu` 取自 CMU 本人主页 `200` / 9,400 B 页内明文 `rsalakhu[at]cs.cmu.edu`；X `@rsalakhu` `200` 双源）/ #312 Caiming Xiong（无邮箱：`caimingxiong.github.io` `404`、`www.caimingxiong.com` `000`、Recursive 团队页 `404`/`000` ⇒ 不猜地址；X `@CaimingXiong` `200` 双源）。X 已核验 **121**（+2）；反例 `@JunnanLi` 实为「雷弟尬尬」（他人）、`@tmikolov` / `@MikolovTomas` `404` ⇒ 均不记。④ 发信 **0 封**（累计仍 **140**）：今日 **12/12** 达每日硬上限 ⇒ 本窗只选题与建档；#311 有邮箱无专属问题清单、#312 无邮箱 ⇒ 不硬发，待发队列空。⑤ 回信率 **0/140**，0 封到期（最早 11-25，#1–#7 剩 3 天）。⑥ voice_ready 0 / news_ready 0（2012–2022 年方法论文，非本窗事件点）。⑦ 交付：`daily/2026-11-22.html` 18:00 节（why + 作者 / 信件段 + news/voice + 建议 3 条 + 附录 7 行 + header/footer 更新）+ `index.html` 当日行（344 · 312 · 121 · 140 · 0/140）+ `research/2026-11-22.md` 18:00 节 + `PAPERS.md` #342–#344 + `AUTHORS.md` #311–#312。
- **2026-11-22（本地 15:0x · 15:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第九十一轮 +3 → 341 ＋ 作者网 +2 → 310 ＋ 信 1 封（累计 140，今日 12/12 满）＋ 回信率 0/140）** —— **第二百三十八轮**：① 网络：`cat:cs.CL&max_results=3`（`--noproxy '*'` 直连 https）`200` / **8,529 B / 3 entry** / atom；公告批仍停在 **`2026-11-19T18:57:25Z`**（**连续第 17 窗未前进**，仍在 72h 窗内）⇒ A 轨 5/5 不凑第 6 篇。② B 轨 **+3 → 341**：Bahdanau attention `1409.0473`（**32,083**，arXiv `comment` = `Accepted at ICLR 2015 as oral presentation`；定长向量瓶颈 → 可微软对齐，长句更稳）/ Qwen2.5-VL `2502.13923`（**10,565**，预印本技术报告；动态分辨率 + 绝对时间编码，框/点定位、文档结构化抽取、小时级视频秒级定位）/ RAFT `2403.10131`（**524**，预印本；golden/distractor 混训 + 逐字引用 + CoT，表 1 RAFT (LLaMA2-7B) **73.30 / 35.28 / 74.00 / 84.95 / 86.86**，正文 35.25% / 76.35%）；arXiv `id_list` `200` + atom（11,306 B / 3 entry）+ abs 3/3 `200`（41,842 / 46,388 / 43,549 B）+ OpenAlex 3/3 `200`（查询日 2026-11-22）+ RAFT 表 1 用 ar5iv `200` / 150,398 B 核；三 ID 三处查重 0 命中（word2vec `1301.3781` 44,294 / Dropout `1207.0580` 9,564 / BLIP `2201.12086` 8,544 / Let's Verify `2305.20050` 2,661 留作下轮）。③ 作者网 **+2 → 310**：#309 Tianjun Zhang 张天俊（`tianjunz@berkeley.edu` 取自本人主页 `200` / 6,538 B 页内明文，与论文 PDF 首页同址；X `@tianjun_zhang` `200` / 190,919 B 双源）/ #310 Dzmitry Bahdanau（Mila 目录页 `200` / 125,911 B 无个人明文邮箱，`bahdanau.github.io` `404`、`www.bahdanau.com` `000` ⇒ 不猜地址；X `@DBahdanau` `200` / 199,403 B 双源）；X 已核验 **119**（+2）。④ 发信 **1 封**（#140 RAFT 中文 **242** 汉字 `SENT OK 15:05:49`；发前主页 `200` / 6,538 B 复核；落款两行、其后无行；正文无项目名；开头句 / 问句零共用），累计 **140**、今日 **12/12 达硬上限**、待发队列空。⑤ 回信率 **0/140**，0 封到期（最早 11-25）。⑥ voice_ready 0 / news_ready 0（2014–2025 年方法 / 技术报告，非本窗事件点）。⑦ 交付：`daily/2026-11-22.html` 15:00 节（why + 作者 / 信件段 + news/voice + 建议 6 条 + 附录 10 行 + header/footer 更新）+ `index.html` 当日行（341 · 310 · 119 · 140）+ `research/2026-11-22.md` 15:00 节 + `PAPERS.md` #339–#341 + `AUTHORS.md` #309–#310 + `发送记录.md` §15:0x + draft / body 各 1。
- **2026-11-22（本地 12:0x · 12:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第九十轮 +3 → 338 ＋ 作者网 +2 → 308 ＋ 信 2 封（累计 139，今日 11/12）＋ 回信率 0/139）** —— **第二百三十七轮**：① 网络：`cat:cs.CL&max_results=2`（`--noproxy '*'`）`200` / **4,815 B / 2 entry** / atom；公告批仍停在 **`2026-11-19T18:57:25Z`**（**连续第 16 窗未前进**，仍在 72h 窗内）⇒ A 轨 5/5 不凑第 6 篇。② B 轨 **+3 → 338**：RetNet `2307.08621`（**1,135**，preprint；保留机制，并行 / 循环 / 分块循环三范式共用权重，O(1) 推理）/ U-Net `1505.04597`（**18,157**，MICCAI 2015；收缩-扩张 + 跳连，强数据增强，512×512 分割 <1 秒）/ ILSVRC `1409.0575`（**1,893**，OpenAlex 仅计 arXiv 记录、IJCV 正式版未合并；2010 年起年度赛 / 数百类数百万图 / 50+ 机构 / 机器-人类精度对比）；`id_list` `200` + atom（6,740 B / 3 entry）+ abs 3/3 `200`（42,591 / 42,533 / 43,947 B，`citation_title` 逐字）+ OpenAlex 3/3 `200`；三 ID 三处查重 0 命中（`2306.12464` 实为天体物理、`2304.07972` 实为控制论 ⇒ 剔除；OSWorld 真 ID `2404.07972` 已在表内 #113）。③ 作者网 **+2 → 308**：#307 Olaf Ronneberger（`ronneber@informatik.uni-freiburg.de` 取自 ar5iv 63,422 B 首页邮箱块；现行主页 `200` / 9,182 B 邮箱为图片 ⇒ 不可验证；X 未找到）/ #308 Jia Deng 邓嘉（`jiadeng@princeton.edu` 取自本人主页 `200` / 5,495 B 页内 JS `showemail('princeton.edu','jiadeng')` 明文；X 未找到）；X 保持 **117**（本轮 0 新增，不猜 handle）。④ 发信 **2 封**（#138 Ronneberger 德文称谓问候 + 英文 **195** 词 `SENT OK 12:06:31` / #139 邓嘉 汉字 **238** `12:06:39`；发前地址页 2/2 `200` 复核；落款两行、其后无行；正文无项目名；开头句 / 问句零共用），累计 **139**、今日 11/12、待发队列空。⑤ 回信率 **0/139**，0 封到期（最早 11-25）。⑥ voice_ready 0 / news_ready 0（2014–2023 年奠基论文，非本窗事件点）。⑦ 交付：`daily/2026-11-22.html` 12:00 节（why + 主表 3 行 #336–#338 + 作者 / 信件段 + news/voice + 建议 6 条 + 附录 7 行 + footer；div 16/16、table 7/7、tr 78/78、td 172/172、th 32/32、0 script）+ `index.html` 当日行（338 · 308 · 117 · 139）+ `research/2026-11-22.md` 12:00 节 + `PAPERS.md` #336–#338 + `AUTHORS.md` #307–#308 + `发送记录.md` §12:0x + drafts 2 / bodies 2。
- **2026-11-22（本地 09:0x · 09:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十九轮 +3 → 335 ＋ 作者网 +2 → 306 ＋ 信 3 封（累计 137，今日 9/12）＋ 回信率 0/137）** —— **第二百三十六轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 15 窗未前进**，仍在 72h 窗内）⇒ A 轨不凑第 6 篇。② B 轨 **+3 → 335**（文生图三件套）：unCLIP / DALL·E 2 `2204.06125`（**10,659**，preprint；CLIP 嵌入先验 + diffusion 解码，AR vs diffusion prior，零样本语言引导编辑）/ Parti `2206.10789`（**1,827**，OpenAlex `type=article` = TMLR；ViT-VQGAN 离散 token 纯自回归，编码器-解码器 20B，零样本 FID **7.23** / 微调 **3.22**，PartiPrompts **1600+**）/ CFG `2207.12598`（**7,405**，preprint，`comment` = NeurIPS 2021 Workshop 短版；条件 + 无条件联合训练，score 线性组合，无需分类器）；arXiv `id_list` `200` + atom（7,556 B / 3 entry，一次 `429` 后按 ≥3 s 限速重试成功）+ abs 3/3 `200`（40,571 / 45,080 / 41,707 B，`citation_title` 逐字）+ OpenAlex 3/3 `200`；三 ID 三处查重 0 命中（Switch Transformer / QLoRA / PagedAttention / RoPE / AdamW / GPT-4 / Toolformer / WebArena / GAIA / DeepSeek-V3 / Qwen2.5 已在表内 ⇒ 剔除）。③ 作者网 **+2 → 306**：#305 Jiahui Yu（邮箱 `jiahuiyu@google.com` 取自 ar5iv 613,481 B 首页邮箱块；X `@jiahuiyu` 双源 `200` / 191,153 B + bio 自述 Startup / 前 OpenAI / 前 DeepMind；主页 `jiahuiyu.com` `200` / 23,467 B 无邮箱）/ #306 Aditya Ramesh（邮箱 `aramesh@openai.com` 取自 ar5iv 274,460 B；X 未找到——`@adityaramesh` bio 为 `A+ : Indic : …` 系他人，`@tim_salimans` `404`、`@jonathanho` 为 Chicago 另一账号 ⇒ 均不记）；X 已核验 **117**。④ 发信 **3 封**（#135 Ramesh 英文 **197** 词 `SENT OK 09:05:25` / #136 Jiahui Yu 汉字 **252** `09:05:27` / #137 Salimans 荷兰语问候 + 英文 **189** 词 `09:05:29`；发前 ar5iv 全文页 3/3 `200` 且页内邮箱逐字；落款两行；开头句 / 问句零共用；三地址均 2022 年论文内地址 ⇒ 标注送达率不可验证），累计 **137**、今日 9/12、待发队列空。⑤ 回信率 **0/137**，0 封到期（最早 11-25）。⑥ voice_ready 0 / news_ready 0（2022 年奠基论文，非本窗事件点）。⑦ 交付：`daily/2026-11-22.html` 09:00 节（why + 3 行 + 作者 / 信件段 + 建议 4 条 + 附录 7 行 + footer）+ `index.html` 当日行（335 · 306 · 117 · 137）+ `research/2026-11-22.md` 09:00 节 + `PAPERS.md` #333–#335 + `AUTHORS.md` #305–#306 + `发送记录.md` §09:0x + drafts/bodies 各 3。

- **2026-11-22（本地 06:0x · 06:00 时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-22.md`「归档 · MEMORY 滚动（第九十轮后折出）」；结论不变，勿以指针替代原文。

- **2026-11-22（本地 03:0x · 03:00 时窗 · 🅰 A 轨 +2（今日 5/5）＋ 🅱 B 轨第八十七轮 +3 → 329 ＋ 作者网 +2 → 302 ＋ 信 1 封（累计 132，今日 4/12）＋ 回信率 0/132）** —— **第二百三十四轮**：① 网络：`cat:cs.CV&max_results=40`（`--noproxy '*'`）`200` / **107,965 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:59:57Z`**（公告批仍未前进；与 00:00 的 cs.CL 上界 `18:57:25Z` 同批，仍在 72h 窗内）。② A 轨 **+2（今日 5/5）**：WeMM-Video `2611.26409`（cs.CV；2B/4B/9B/35B-A3B omni-modal，约 1.2T token 渐进预训练 + 多教师 OPD / MrDPO / 专家 RL，120+ 基准，9B 超过 Qwen3-Omni-30B-A3B-Instruct）/ TRQ `2611.26334`（cs.CV；视频 DiT KV cache 2-bit 量化，2×2 平面旋转树每颗 2 bit + 共享 Hadamard，在线无梯度，VBench 主体一致性 90.38→92.02 / 86.33→87.61）；五 ID 三处查重 0 命中；abs 2/2 `200`（43,294 / 41,727 B）且 `citation_title` 逐字一致。③ B 轨 **+3 → 329**：EVA-02 `2303.11331`（**683**，Image and Vision Computing）/ Sequence Parallelism `2105.13120`（**258**，ACL 2023；未达 500 按「开创范式 / 常青」入选）/ ViT registers `2309.16588`（**821**，ICLR 2024）；`id_list` `200` + atom（7,486 B / 3 entry）+ abs 3/3 `200`（43,667 / 44,844 / 40,626 B）+ OpenAlex 3/3 `200`；同批排除已收 Transfusion / Janus / Ring Attention。④ 作者网 **+2 → 302**：#301 Timothée Darcet **无邮箱**（`timdarcet.github.io` `200` / 2,363 B）但 X `@timdarcet` `200` / 181,126 B（`og:title` + `og:description` 双源）/ #302 Changli Tang（清华大学电子系博士生；WeMM-Video 一作）无邮箱（`github.com/TCL606` `200` / 196,169 B）、X `@TCL606` `404` ⇒ 只建档；反例 `@xgwang` 实为 Montréal 的 3 followers 账号 ⇒ 不记；X 已核验 **115**。⑤ 发信 **1 封**（#132 Show-o / Mike Zheng Shou，汉字 203，`SENT OK 03:02:36`；发前 `sites.google.com/view/showlab` `200` / 162,233 B 且页内邮箱逐字；落款两行），累计 **132**、今日 4/12、待发队列清空。⑥ 回信率 **0/132**，0 封到期（最早 11-25）。⑦ voice_ready 0（未抓到可双源核验的单条推文）/ news_ready 0（五篇均方法 / 框架类，无事件点，不硬凑）。⑧ 交付：`daily/2026-11-22.html`（5/5；补 2 卡 + B 轨 3 行 + 作者 / 信件段 + 晚报变更说明 + 03:00 建议 + 附录）+ `index.html` 当日行（5/5 · 329 · 302 · 115 · 132）+ `research/2026-11-22.md` + `PAPERS.md` #327–#329 + `AUTHORS.md` #301–#302 + `发送记录.md` §03:0x + `SEEN.md`/`papers.jsonl` 2 条 + draft Show-o 回填「已发送」。

- **2026-11-22（本地 00:0x · 00:00 时窗 · 🅰 A 轨 +3（今日 3/5）＋ 🅱 B 轨第八十六轮 +3 → 326 ＋ 作者网 +2 → 300 ＋ 信 3 封（累计 131，今日 3/12）＋ 回信率 0/131）** —— **第二百三十三轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 13 窗未前进**，仍在 72h 窗内）。② A 轨 **+3**：SheetAlign `2611.26069`（cs.CL，表格 agent 三段式；Qwen3-4B 仅换接口 13.5%→29.2%，加训练 32.8%，Domain-Spreadsheet 30.1%）/ RL Can Only Reinforce `2611.26084`（cs.LG；约 35 组成功尝试为胜负各半阈值，4–256 次尝试、1.3M–85M 参数成立）/ dLoop `2611.26275`（cs.CL；Prelude–Loop–Coda 循环潜变量，TPF 折算下优于 Fast-dLLM 四项）；六 ID 三处查重 0 命中；abs 3/3 `200`（41,201 / 40,874 / 43,057 B）且 `citation_title` 逐字一致。③ B 轨 **+3 → 326**：EVA-CLIP `2303.15389`（**1,204**）/ RefinedWeb `2306.01116`（**1,221**）/ SD3 `2403.03206`（**5,735**），均 preprint；`id_list` `200` + atom（7,923 B / 3 entry）+ abs 3/3 `200`（40,797 / 41,829 / 43,894 B）+ OpenAlex 3/3 `200`；同批排除已收 Muon / Qwen2-VL / RoPE 外推 / The Pile / HumanEval / DataComp / DINOv2 / SAM / Chameleon / Emu3。④ 作者网 **+2 → 300**：#299 Robin Rombach **无邮箱**（`rombach.me` / `www.robrombach.com` 均 `000`）但 X `@robrombach` `200` / 188,334 B 且 `og:title` 逐字 / #300 Patrick Esser 邮箱·主页·X 均未找到 ⇒ 只建档；⚠️ 三处同名反例拦下：`@guipenedo`（巴西灯光从业者）、`@PatrickEsser`（= patrick goncalves）、`@EsserPatrick`（= Patrick Esser JR）⇒ 不记。⑤ 发信 **3 封**（#129 Grounding DINO 汉字 187 `00:02:06` / #130 EAGLE 汉字 200 `00:02:08` / #131 Depth Anything 汉字 241 `00:02:09`；发前地址页 3/3 `200` 且页内邮箱逐字；落款两行），累计 **131**、今日 3/12、待发余 1 封（Show-o）。⑥ 回信率 **0/131**，0 封到期（最早 11-25）。⑦ voice_ready 0（未抓到可双源核验的单条推文）/ news_ready 0（无事件点，不硬凑）。⑧ 交付：`daily/2026-11-22.html`（新建，div 11/11 · table 5/5 · tr 28/28 · td 46/46 · th 22/22 · 0 script · 0 残留 `**`）+ `index.html` 当日行（3/5 · 326 · 300 · 114 · 131）+ `research/2026-11-22.md` + `PAPERS.md` #324–#326 + `AUTHORS.md` #299–#300 + `发送记录.md` §00:0x + `SEEN.md`/`papers.jsonl` 3 条。

- **2026-11-21（更早时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`（本轮追加）；结论不变，勿以指针替代原文。

- **2026-11-21（更早时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`（本轮追加）；结论不变，勿以指针替代原文。

- **2026-11-21（本地 15:0x · 15:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十三轮 +3 → 317（Grounding DINO 2,415 / AndroidWorld 525 / EAGLE 499）＋ 作者网 +2 → 294（Shilong Liu A 级 / Hongyang Zhang A 级，X 已核验 111）＋ 信 0 封（当日 12/12 硬上限，备 2 封中文草稿 198 / 209 汉字）＋ 回信率 0/128，0 封到期；两处 ID 误记写入前拦截（2303.19588⇒2303.05499、2502.05907 实为 EvolvingAgent）** —— 核验：arXiv `id_list` `200` + atom、abs 3/3 `200`、OpenAlex 3/3 `200`；`x.com` 经代理 `200`，`@atasteoff` `404` 不记；交付 `daily/2026-11-21.html` +15:00 节、`index.html` 当日行、`PAPERS.md` #315–#317、`AUTHORS.md` #293–#294、`发送记录.md` §15:0x、draft 2 个。

- **2026-11-21（更早时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`（本轮追加）；结论不变，勿以指针替代原文。
- **2026-11-21（本地 09:00 · 09:00 时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`「归档 · MEMORY 滚动（第八十七轮后折出）」；结论不变，勿以指针替代原文。

- **2026-11-21（本地 09:00 · 09:00 时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`「归档 · MEMORY 滚动（第八十七轮后折出）」；结论不变，勿以指针替代原文。




- **2026-11-21（更早时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`（本轮追加）；结论不变，勿以指针替代原文。

- **更早轮次 2026-11-20（12:0x / 18:0x）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-20.md`「归档 · MEMORY 滚动（第八十二轮折出）」。

- **2026-11-19（本地 21:0x · 21:00 时窗）** —— 第二百一十五轮（B 轨 +4 → 264 / 作者网 245 / 信 0）；原文已 fold 至 `daily-memories-research/2026-11-19.md`「归档 · MEMORY 滚动（第七十九轮折出）」。



- **2026-11-18（本地 12:1x · 12:00 时窗）** —— **第二百零三轮**：B 轨 +3 → 222 / 作者网 203 / 信 90 / H4 启动；细节已 fold 至 `daily-memories-research/2026-11-18.md`。

- **更早轮次（2026-11-12 ~ 2026-11-16，r152–r183）**：原文已按 §5 滚动归档 → `daily-memories-research/` 各日文件的「归档 · MEMORY 滚动」段（2026-11-13 / 14 / 15 / 16 等），此处只留指针，勿以指针替代结论。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
