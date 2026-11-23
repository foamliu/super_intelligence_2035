# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r249 · 本地 2026-11-24 00:0x · 00:00 时窗：A 轨 +3 → 今日 3/5 ＋ B 轨 +3 → 374 ＋ 作者网 +3 → 341（X 仍 130）＋ 发信 3 封 → 155 ＋ 回信率 0/155]
  ① 网络（arXiv）：**`http://export.arxiv.org` 现返回 `301`** ⇒ 改用 `https://export.arxiv.org`；`cat:cs.CL&max_results=15`（`--noproxy '*'`）**`200` + `application/atom+xml`**（36,805 B / 15 entry），`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗（11-23 16:00 UTC）约 **69.1h < 72h**；A 轨 abs 页 **3/3 `200`**（41,235 / 41,958 / 38,934 B，`citation_title` + `citation_date` 逐字）；B 轨 `id_list` 批量 **`200` + atom**（10,081 B）+ abs **3/3 `200`**（41,847 / 41,473 / 45,205 B）+ ar5iv **3/3 `200`**（236,747 / 296,786 / 228,755 B）+ OpenAlex **3/3 `200`**（1,835 / 1,142 / 6,929，查询日 2026-11-24）；X 自检经 Mihomo `x.com` **`200`**。
  ② A 轨 **+3（今日 3/5）**：TEA-Bench-BR `2611.27895`（cs.SE，单作者；144 tasks / **6,798 隐藏用例**杀死全部 **1,955** 个非等价变异体；Gemma 4 12B 单表 38.0% / FHIR 0，31B 77.8% / 85.2% / 78.7%；Kaggle Gemma 4 赛道 7 页短文、未经同行评审）/ RoSci `2611.27750`（cs.CL；Information Error / Loss 两大类六种退化，**1,220** seed-variant 样本；Parse-Verify-Decide）/ Higher-Order Attention `2611.27764`（cs.CL，单作者；CMI 分解 + 相邻 key/query 相关 + 广义最大熵；**摘要无实验数字 ⇒ 理论线索**）；三 ID 查重 0 命中，已入 `SEEN.md` / `papers.jsonl`；同批 MemOnce / Tasklets 已于 11-23 收录 ⇒ 跳过。
  ③ B 轨 **+3 → 374**：ViLT `2102.03334`（**1,835**，ICML 2021 Long，OpenAlex `conference-paper`；convolution-free patch 投影、去 region 监督；称快数十倍）/ FLAVA `2112.04482`（**1,142**，CVPR 2022；单一整体模型覆盖视觉 / 语言 / 跨模态 / 多模态，**35** 任务）/ ALIGN `2102.05918`（**6,929**，ICML 2021、OpenAlex 记 `preprint`；Conceptual Captions **>10 亿**对、不做昂贵过滤，简单双塔 + 对比损失，主张规模补偿噪声）；三 ID 条目级查重 0 命中；⚠️ 候选池旧 ID 当场纠错：`2309.05076` = 情感对话 / `2111.05477` = 多重分形 / `2012.00571` = RDF 复述 / `2206.10537` = X 射线偏振仪 ⇒ 均弃。
  ④ 作者网 **+3 → 341**：#339 Wonjae Kim（韩文；Kakao Brain；`wonjae.kim@navercorp.com` 来自 ar5iv `2102.03334` `200` / 236,747 B，**2021 旧地址 ⇒ 仅建档**）/ #340 Amanpreet Singh（英文；Meta AI；**无明文邮箱**，`amanpreetsingh.github.io` 实测 **`000`** ⇒ 仅建档）/ #341 Chao Jia（中文；Google Research；`chaojia@google.com` 来自 ar5iv `2102.05918` `200` / 228,755 B，**单源旧地址待核**）；X **+0 → 130**（三人均无 X 外链，不猜）。
  ⑤ 发信 **3 封**（累计 **155**）：#153 Di He 中文 **197** 字 `SENT OK 00:05:35` / #154 Mingjie Liu 中文 **208** 字 `00:05:37` / #155 Jiawei Zhao 中文 **234** 字 `00:05:37`；发前地址复核 3/3 `200`（`dihe-pku.github.io` / ar5iv VerilogEval / `jiaweizhao.com`）；落款两行、其后无行；三封开头句与问句零共用；今日 **3/12**。
  ⑥ 回信率 **0 / 155**，**0 封到期**（最早 2026-11-25，#1–#7 剩 1 天）；`replies/` 仍只有 `README.md`；通道只发不收。
  ⑦ voice_ready **0**（X 推文页需登录态，未双源核验）/ news_ready **0**（2021–2023 方法 / 视觉基础模型，无本窗事件点）。
  ⑧ 交付：`daily/2026-11-24.html`（A 轨 3 卡 + B 轨 3 行 + 作者 3 行 + 信件 3 卡 + 6 线建议 6 条 + 附录 5 行）+ `daily/index.html` 当日行（3/5 · 374 · 341 · 130 · 155 · 0/155）+ `research/2026-11-24.md` + `PAPERS.md` #372–#374（含新「本轮快照 374」）+ `AUTHORS.md` #339–#341（+ 新计数行 341）+ `发送记录.md` §00:00 + drafts / bodies 各 3。

  前一: [r248 · 2026-11-23 21:00 时窗 · A 0 新收（5/5 满）· B +3 → 371 · 作者网 +3 → 338 · 信 0 · 回信率 0/152] 详情见 `daily-memories-research/2026-11-23.md`。

当前动作:     ✅ 00:00 时窗闭环：A 轨 +3 → 今日 3/5（公告批 69.1h < 72h，额度重置），B 轨 +3 → 374，作者网 +3 → 341，发信 3 封 → 155，回信率 0/155。
下一步:       ① 下一时窗（03:00）：A 轨补 2 篇至 5/5（公告批仍在 72h 内），优先从同批未收录里选，选前先查 `SEEN.md`；② B 轨候选：OWL-ViT `2205.06230`（361，需按「本领域权威」判） / MoCo `1911.05722` / 其他必读清单外高引且未收录者；③ 发信队列（先核地址）：Rico Sennrich（UZH 页今日 `404`，暂缓） / Victor Sanh（旧 HF 地址） / Mostafa Dehghani（单源）；④ 11-25 首批到期 → #1–#7 转 `无应答(>14d)`，并做地址级别 × 论文年代分层；⑤ 运维：发件显示名 / SMTP 只发不收 / 任务书 44 KB 超红线。
补推记录:     2026-11-24 00:0x · 本轮 commit 前 `git pull --rebase --autostash`；若 push 被拒按 `fetch + rebase origin/main` 重试（最多 5 次），不 `add -A`。
本轮新增:     A 轨 +3（今日 3/5）· B 轨 +3（374）· 作者网 +3（341）· X 已核验 +0（130）· 作者信 +3（155，今日 3/12）· voice_ready 0 · news_ready 0 · 回信率 0/155
阻塞:         ① 🔴 发件显示名 `AI+EDA 招聘 · 自动`（最可能的 0 回信原因），需运维改配置；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到；③ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且 agent 只读 ⇒ 需授权；④ arXiv `http://export` 端点改 301 ⇒ 已切 https（无需运维，仅记录）；⑤ 部分作者无公开明文邮箱 / 地址过期（Amanpreet Singh / Wonjae Kim / Rico Sennrich 页面 404）⇒ 只建档、不猜地址。
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
- **上次采集窗口**：`2026-11-24 00:0x`（**第二百四十九轮 · 00:00 时窗**：A 轨 **+3 → 今日 3/5**（TEA-Bench-BR / RoSci / Higher-Order Attention，公告批 69.1h < 72h）；B 轨 **+3 → 374**（ViLT / FLAVA / ALIGN）；作者网 **+3 → 341**（X 仍 130）；发信 **3**（#153–#155，今日 3/12））
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`371` 篇（A 轨；本轮 **+3**：`2611.27895` / `2611.27750` / `2611.27764`；`SEEN.md` 为唯一防重台账）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**371 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**一百零一轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**338 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-24（本地 00:0x · 00:00 时窗 · 🅰 A 轨 +3 → 今日 3/5 ＋ 🅱 B 轨第一百零二轮 +3 → 374 ＋ 作者网 +3 → 341（X 130）＋ 发信 3 封 → 155 ＋ 回信率 0/155）** —— **第二百四十九轮**：① 网络：**`http://export.arxiv.org` 改返回 `301`** ⇒ 切 `https://export.arxiv.org`；`cat:cs.CL&max_results=15`（`--noproxy '*'`）**`200` + `application/atom+xml`**（36,805 B / 15 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-23 16:00 UTC 约 **69.1h < 72h**）；A 轨 abs 3/3 `200`（41,235 / 41,958 / 38,934 B）；B 轨 `id_list` 批量 `200` + atom（10,081 B）+ abs 3/3 `200`（41,847 / 41,473 / 45,205 B）+ ar5iv 3/3 `200`（236,747 / 296,786 / 228,755 B）+ OpenAlex 3/3 `200`（1,835 / 1,142 / 6,929）；X 自检 `200`。② A 轨 **+3（今日 3/5）**：TEA-Bench-BR `2611.27895`（144 tasks / 6,798 隐藏用例 / 杀死 1,955 个非等价变异体；12B 单表 38.0%、FHIR 0；31B 77.8% / 85.2% / 78.7%）/ RoSci `2611.27750`（1,220 样本、六类退化、Parse-Verify-Decide）/ Higher-Order Attention `2611.27764`（CMI + 相邻 key/query + 广义最大熵；摘要无实验 ⇒ 理论线索）；三 ID 查重 0 命中；同批 MemOnce / Tasklets 已收录 ⇒ 跳过。③ B 轨 **+3 → 374**：ViLT `2102.03334`（1,835，ICML 2021 Long）/ FLAVA `2112.04482`（1,142，CVPR 2022，35 任务）/ ALIGN `2102.05918`（6,929，ICML 2021，>10 亿噪声图文对 + 简单双塔）；⚠️ 候选池旧 ID 纠错：`2309.05076` / `2111.05477` / `2012.00571` / `2206.10537` 实测均为无关论文 ⇒ 弃。④ 作者网 **+3 → 341**：#339 Wonjae Kim（`wonjae.kim@navercorp.com`，2021 旧地址 ⇒ 仅建档）/ #340 Amanpreet Singh（无邮箱，主页 `000`）/ #341 Chao Jia（`chaojia@google.com` 单源待核）；X +0（130）。⑤ 发信 **3 封**：#153 Di He 中文 197 字 `SENT OK 00:05:35` / #154 Mingjie Liu 中文 208 字 `00:05:37` / #155 Jiawei Zhao 中文 234 字 `00:05:37`；发前地址复核 3/3 `200`；今日 3/12。⑥ 回信率 **0/155**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-24.html`（3 卡 + B 3 行 + 作者 3 行 + 信 3 卡 + 6 线建议 6 条 + 附录）+ `daily/index.html` 当日行（3/5 · 374 · 341 · 130 · 155 · 0/155）+ `research/2026-11-24.md` + `PAPERS.md` #372–#374 + `AUTHORS.md` #339–#341 + `发送记录.md` §00:00 + drafts / bodies 各 3。
- **2026-11-23（本地 21:0x · 21:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第一百零一轮 +3 → 371 ＋ 作者网 +3 → 338（X +1 → 130）＋ 发信 0（今日 12/12）＋ 回信率 0/152）** —— **第二百四十八轮**：① 网络：`cat:cs.CL&max_results=5`（`--noproxy '*'`）**`200` + atom**（13,309 B / 5 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-23 13:00 UTC 约 **66.1h < 72h**）；B 轨批量 `id_list` 先遇 **`429`**，改 `search_query=id:<ID>` 单查 **3/3 `200` + atom**（`published` = 2023-11-10T18:59:08Z / 2021-10-15T17:08:57Z / 2022-05-10T19:32:20Z）；abs 3/3 `200`（41,312 / 50,287 / 45,566 B）+ ar5iv 3/3 `200`（597,282 / 309,166 / 633,921 B）+ OpenAlex 3/3 `200`（861 / 2,273 / 627）；X 自检 `200`。② A 轨 **0 新收**：今日 5/5 已满 ⇒ 不凑第 6 篇。③ B 轨 **+3 → 371**：Florence-2 `2311.06242`（861，CVPR 2024；统一任务提示 seq2seq；FLD-5B 54 亿标注 / 1.26 亿图；CIDEr 133.0 / 135.6）/ T0 `2110.08207`（2,273，ICLR 2022 Spotlight；62 数据集 / 12 任务 + 多套模板；零样本超 16× 大模型）/ UL2 `2205.05131`（627；MoD R/S/X，`r ∈ {0.15,0.5}`、`μ ∈ {3,8,64}`；20B、50 任务 SOTA、胜 175B GPT-3 零样本 SuperGLUE）。④ 作者网 **+3 → 338**：#336 Bin Xiao（中文，无公开明文邮箱 ⇒ 仅建档）/ #337 Victor Sanh（旧 HF 地址不用于发信；X `@VictorSanh` 双源）/ #338 Mostafa Dehghani（`dehghani@google.com` 单源待核；`@m_dehghani` 1 follower 判他人）；X **130**。⑤ 发信 **0 封**（累计 152）：今日 12/12 硬上限 ⇒ 只选题建档；待发 Victor Sanh / Mostafa Dehghani / Rico Sennrich / Jiawei Zhao / Di He / Mingjie Liu。⑥ 回信率 **0/152**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-23.html` 21:00 节（A 证据 + B 3 行 + 作者 3 行 + 信件 0 + 6 线建议 6 条 + 附录）+ `daily/index.html` 当日行（371 · 338 · 130 · 152 · 0/152）+ `research/2026-11-23.md` + `PAPERS.md` #369–#371 + `AUTHORS.md` #336–#338 + `发送记录.md` §21:00。

- **2026-11-23（本地 18:0x · 18:00 时窗 · 🅰 A 轨不动（今日 5/5 已满）＋ 🅱 B 轨第一百轮 +3 → 368 ＋ 作者网 +3 → 335（X +2 → 129）＋ 发信 0（今日 12/12）＋ 回信率 0/152）** —— **第二百四十七轮**：① 网络：`search_query=cat:cs.CL&max_results=5`（`--noproxy '*'`）**`200` + atom**（13,309 B / 5 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-23 10:00 UTC 约 **63.1h < 72h**）；B 轨 `id_list=1910.07467,2403.03507,2407.10671` **`200` + atom**（10,910 B / 3 entry，`published` = 2019-10-16T16:44:22Z / 2024-07-15T12:35:42Z / 2024-03-06T07:29:57Z；`comment` = NeurIPS 2019 / `26 pages, 1 figure` / `ICML 2024 (Oral)`）；abs 页 3/3 `200`（42,264 / 51,347 / 43,302 B，`citation_title` + `citation_date` 逐字）；ar5iv 3/3 `200`（208,520 / 346,984 / 558,608 B）；Qwen2 arXiv HTML `2407.10671v4` `200` / 355,126 B（页内核实 3T→7T、12T 无显著提升、131,072 tokens）；OpenAlex 3/3 `200`（1,903 / 5,530 / 648，查询日 2026-11-23）；X 自检经代理 `200`。② A 轨**不动**：今日 5/5 已满（00:00–15:00 完成）⇒ 即使上界 63.1h < 72h 也不凑第 6 篇。③ B 轨 **+3 → 368**：RMSNorm `1910.07467`（**1,903**，NeurIPS 2019，`conference-paper`；丢掉 re-centering、只按 RMS 归一化 + pRMSNorm；与 LayerNorm 持平而运行时间降 **7%~64%**）/ GaLore `2403.03507`（**648**，ICML 2024 Oral、OpenAlex `preprint`；梯度低秩投影保持全参数学习，优化器状态内存降 **65.5%**、8-bit 再降 **82.5%**、总训练内存降 **63.3%**；LLaMA 1B/7B + C4 **19.7B** token；24GB RTX 4090 预训练 7B）/ Qwen2 `2407.10671`（**5,530**，`preprint`；0.5–72B dense + **57B-A14B MoE**；预训练 **3T → 7T** token，放宽质量阈值得到 **12T** 反而无显著提升 ⇒ 选 7T；72B base MMLU **84.2** / GPQA 37.9 / HumanEval 64.6 / GSM8K 89.5 / BBH 82.4，Instruct MT-Bench **9.1** / Arena-Hard 48.1 / LiveCodeBench 35.7，约 **30** 语）；三 ID 条目级查重 0 命中；⚠️ 候选池把 GaLore 记成 `2402.04347`，abs 实测为 *The Hedgehog & the Porcupine*（无关）⇒ 真 ID `2403.03507` 复核后收录。④ 作者网 **+3 → 335**：#333 Rico Sennrich（`rico.sennrich@uzh.ch`，UZH 官方人员页 `200` / 65,239 B 页内 `mailto:`，未用论文旧写法 `sennrich@cl.uzh.ch`）/ #334 Jiawei Zhao（`jwzhao@meta.com`，本人主页 `www.jiaweizhao.com` `200` / 18,586 B 页内 `jwzhao at meta dot com`，未用旧 `jiawei@caltech.edu`）/ #335 Biao Zhang（Google DeepMind，**无当前可核地址** ⇒ 仅建档，不用旧 Edinburgh 地址、不猜 `@google.com`）；X **+2 → 129**：`@RicoSennrich`（`x.com` `200` / 160,280 B + `og:title`/`og:description`）、`@jiawzhao`（主页外链 + 推文页 `og:title`/`og:description` 双源）。⑤ 发信 **0 封**（累计 **152**）：今日 **12/12** 达每日硬上限 ⇒ 只选题、建档、备问题；下一自然日待发 = Rico Sennrich / Jiawei Zhao / Di He / Mingjie Liu（同一论文 ≤1；Qwen2 62 位作者无公开邮箱 ⇒ 不建联系人）。⑥ 回信率 **0 / 152**，0 封到期（最早 2026-11-25，#1–#7 剩 2 天）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-23.html` 18:00 节（B 轨 3 行 + 作者 3 行 + 信件段 0 封 + 6 线建议 6 条 + 附录 7 行 + footer）+ `index.html` 当日行（368 · 335 · 129 · 152 · 0/152）+ `research/2026-11-23.md` 18:00 节 + `PAPERS.md` #366–#368 + `AUTHORS.md` #333–#335 + `发送记录.md` §18:00。


- **2026-11-23（本地 15:3x · B 轨补轮 · 🅰 A 轨不动（今日 5/5 已满）＋ 🅱 B 轨第九十九轮 +3 → 365 ＋ 作者网 +3 → 332 ＋ 发信 0（今日 12/12）＋ 回信率 0/152）** —— **第二百四十六轮**：① 网络：arXiv `id_list=2205.11916,2012.12877,2002.04745` **`200` + atom**（8,506 B / 3 entry，`published` = 2020-02-12T00:33:03Z / 2022-05-24T09:22:26Z / 2020-12-23T18:42:10Z）；abs 页 3/3 `200`（44,669 / 45,193 / 42,739 B，`citation_title` + `citation_date` 逐字）；ar5iv 2/2 `200`（392,812 / 213,678 B）；OpenAlex 3/3 `200`（查询日 2026-11-23）；X 自检经代理 `200`。② A 轨**不动**：今日 5/5 已满 ⇒ 不凑第 6 篇。③ B 轨 **+3 → 365**：DeiT `2012.12877`（**5,971**，`preprint`；ImageNet-only、无外部数据；86M / 单机 <3 天 / 单裁 top-1 **83.1%**；distillation token 经注意力学习、带 convnet 教师 **85.2%**）/ Pre-LN `2002.04745`（**1,133**，`preprint`；均值场：Post-LN 初始化时近输出层期望梯度大 ⇒ 必须 warm-up，Pre-LN 可去掉）/ Zero-shot-CoT `2205.11916`（**10,093**，NeurIPS 2022；一句 `Let's think step by step`、无 few-shot；MultiArith **17.7% → 78.7%**、GSM8K **10.4% → 40.7%**）；三 ID 条目级查重 0 命中；⚠️ 同批候选 VerilogEval 旧记 ID `2309.07635` 实测为 math-ph 无关论文，真 ID `2309.07544` 复核**已在表内 #7** ⇒ 剔除不重复收。④ 作者网 **+3 → 332**：#330 Di He 贺笛（`di_he@pku.edu.cn`，主页 `200` / 27,555 B；未用旧 `dihe@microsoft.com`）/ #331 Mingjie Liu（`mingjiel@nvidia.com`，ar5iv `200` / 181,517 B）/ #332 Haoxing Ren（`haoxingr@nvidia.com`）；X 仍 **127**（三人无依据 ⇒ 不猜）。⑤ 发信 **0 封**（累计 **152**）：今日 **12/12** 达每日硬上限 ⇒ 只选题建档；待发 = Di He / Mingjie Liu。⑥ 回信率 **0 / 152**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-23.html` 补轮节 + `research/2026-11-23.md` 补轮节 + `PAPERS.md` #363–#365 + `AUTHORS.md` #330–#332 + `发送记录.md` §15:3x。

- **2026-11-23（本地 15:0x · 15:00 时窗 · 🅰 A 轨 +2 → 今日 5/5（公告批续进至 11-20 18:51Z，60.0h < 72h）＋ 🅱 B 轨第九十八轮 +3 → 362 ＋ 作者网 +3 → 329 ＋ 信 1 封 → 152 ＋ 回信率 0/152）** —— **第二百四十五轮**：① 网络：`cat:cs.CL&max_results=20`（`--noproxy '*'`）`200` / **48,824 B / 20 entry** / atom；`published` 上界 **`2026-11-20T18:51:29Z`**，距本窗（11-23 07:00 UTC）约 **60.0h < 72h** ⇒ A 轨补收 2 篇凑满 5/5；交叉核 cs.LG `200` / 25,815 B（`18:58:45Z`）、cs.CV `200` / 25,495 B（`18:44:57Z`）、cs.SE `200` / 25,167 B（`18:18:55Z`）。② A 轨 **+2（今日 5/5）**：MemOnce `2611.27973`（cs.CL，Nanjing University / USTC；只缓存最后一层少量隐藏状态为 memory + 按需解码回 KV + 稀疏索引跨层只算一次；Qwen3.5-4B 在 1M 下 1313× / 6.9× / 3.5× / +5.77%）/ THOT `2611.27951`（cs.LG，单作者；hub-and-spoke OT + 有界支撑容量门控 sparsemax O(L log L) / thresholded ReLU O(L)；L=128 训练、L=262,144 零样本召回 97.40% / 98.83%，softmax 门控 3.52%；L=65K 多针 128/128 vs 0.78%）；`id_list` 单批 `200` + atom（5,890 B / 2 entry）+ abs 2/2 `200`（42,477 / 42,903 B，`citation_title` + `citation_date` = 2026/11/20 逐字）+ MemOnce arXiv HTML `200` / 625,847 B；两 ID 查重 0 命中，已入 `SEEN.md` / `papers.jsonl`。③ B 轨 **+3 → 362**：Sparsely-Gated MoE `1701.06538`（**7,067**，预印本；数千 FFN 专家 + 可训练门控，>1000× 容量、137B）/ LLM.int8() `2208.07339`（**2,757**，NeurIPS 2022；向量级量化 + 混合精度分解，离群维度 16-bit、>99.9% 数值 8-bit，175B 无退化）/ SimCSE `2104.08821`（**5,562**，EMNLP 2021；dropout 即最小增广，NLI entailment 正例 + contradiction 硬负例，STS 76.3% / 81.6%）；abs 3/3 `200`（45,350 / 44,198 / 43,059 B）+ OpenAlex 3/3 `200`（查询日 2026-11-23）；三 ID 查重 0 命中。④ 作者网 **+3 → 329**：#327 Chang Nie（`changnie@smail.nju.edu.cn`，arXiv HTML `200` / 625,847 B 首页 `Main Contact`，单源）/ #328 Chaoyou Fu（`bradyfu24@gmail.com`，同页；主页 `bradyfu.github.io` `200` / 11,511 B）/ #329 Songlin Liu（无公开明文邮箱，只建档）；X 仍 **127**（三人无 X 依据 ⇒ 不猜）。⑤ 发信 **1 封**（累计 **152**）：#152 MemOnce 一作 Chang Nie，中文 **251** 汉字，`SENT OK 15:06:02`；落款两行、其后无行；正文无项目名；专属细节 = 最后一层 memory + 稀疏索引跨层只算一次 + 1313× / 6.9× / 3.5× / +5.77%；今日 **12/12**。⑥ 回信率 **0 / 152**，0 封到期（最早 2026-11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-23.html` 15:00 节（A 卡片 4/5 + B 3 行 + 作者 3 行 + 信件 1 卡 + 建议 6 条 + 附录）+ `index.html` 当日行（5/5 · 362 · 329 · 127 · 152 · 0/152）+ `research/2026-11-23.md` + `PAPERS.md` #360–#362 + `AUTHORS.md` #327–#329 + `发送记录.md` §15:0x + draft / body 各 1。

- **2026-11-23 12:0x ~ 2026-11-22 18:0x（更早 5 条）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-23.md`「归档 · MEMORY 滚动（r249 后折出）」；结论不变，勿以指针替代原文。

- **2026-11-22 06:0x ~ 2026-11-19（更早轮次）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-22.md`「归档 · MEMORY 滚动（第九十四轮后折出）」与 `daily-memories-research/2026-11-21.md` / `2026-11-20.md` / `2026-11-19.md` / `2026-11-18.md`；结论不变，勿以指针替代原文。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
