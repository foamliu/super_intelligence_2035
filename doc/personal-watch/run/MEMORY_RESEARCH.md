# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r253 · 本地 2026-11-24 15:0x · 15:00 时窗：A 轨 0 新收（今日 5/5 已满；公告批已刷新至 11-23 15:43Z，15.3h 在窗但额度已满）＋ B 轨 +3 → 386（ALBERT / XLNet / REALM）＋ 作者网 +3 → 353（X 132）＋ 发信 2 封 → 161 ＋ 回信率 0/161]
  ① 网络：`cat:cs.CL&max_results=5&sortBy=submittedDate`（`--noproxy '*'`）**`200` + `application/atom+xml`**（13,309 B / 5 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-24 01:00 UTC 约 **78.1h > 72h** ⇒ 已出窗）；B 轨 arXiv 批量 `id_list` 两次 **`429`** ⇒ 改单查 `search_query=id:<ID>` **3/3 `200` + atom**（2,567 / 3,739 / 3,382 B）+ abs 3/3 `200`（41,707 / 46,461 / 44,439 B）+ ar5iv 2/3 部分（258,225 / 81,023 B，25s 截断）+ OpenAlex 3/3 `200`（94→会议版 24,624 / 2,546 / 2,592，查询日 2026-11-24）。
  ② A 轨 **0 新收**：今日 5/5 已满且公告批 78.1h 出窗 ⇒ 不凑第 6 篇。
  ③ B 轨 **+3 → 383**：Sentence-BERT `1908.10084`（**24,624** 会议版 DOI `10.18653/v1/d19-1410`；arXiv DOI 记 94，分列；siamese/triplet，10,000 句找最相似对 65h → ~5s）/ DeBERTa `2006.03654`（**2,546**，2020 预印本；content/position 解耦注意力 + enhanced mask decoder，半数据超 RoBERTa-Large，1.5B 单模型 SuperGLUE 89.9）/ Test-time compute scaling `2408.03314`（**2,592**，ICLR 2025；compute-optimal 分配 >4× best-of-N，FLOPs 对齐胜 14× 大模型）；三 ID 条目级查重 0 命中。
  ④ 作者网 **+3 → 350**：#348 Nils Reimers（德文；`info@nils-reimers.de` 站点 contact 当前地址，已发信）/ #349 Charlie Snell（英文；`csnell22@berkeley.edu` 主页 mailto 当前地址，X `@sea_snell` 双源，已发信）/ #350 Pengcheng He（中文；仅 2020 论文页地址、MSR 人员页重定向 ⇒ 仅建档）；X +1 → 131。
  ⑤ 发信 **2 封**（累计 **159**）：#158 德文问候 + 英文 191 词 `SENT OK 09:06:52`、#159 英文 197 词 `09:06:52`；落款两行、其后无行；正文无项目名；与今日 #153–#157 开头句 / 问句零共用；今日 **7/12**。
  ⑥ 回信率 **0 / 159**，**0 封到期**（最早 2026-11-25，#1–#7 剩 1 天）；`replies/` 仍只有 `README.md`；通道只发不收。
  ⑦ voice_ready **0** / news_ready **0**（方法 / 基准类，无本窗事件点）。
  ⑧ 交付：`daily/2026-11-24.html` 09:00 节 + `daily/index.html` 当日行（5/5 · 383 · 350 · 131 · 159 · 0/159）+ `research/2026-11-24.md` §8 + `PAPERS.md` #381–#383（+ 新快照 383）+ `AUTHORS.md` #348–#350（+ 计数行 350）+ `发送记录.md` §09:00 + draft / body 各 2。

  前一: [r251 · 2026-11-24 06:00 时窗 · A 0 新收 · B +3 → 380（BYOL / DINO / ColBERT）· 作者网 +3 → 347 · 信 1 → 157 · 回信率 0/157] 详情见 `daily-memories-research/2026-11-24.md`。

当前动作:     ✅ 15:00 时窗闭环：A 轨 0 新收（今日 5/5 已满；公告批已刷新至 11-23 15:43Z、15.3h 在窗但额度已满 ⇒ 次日 00:00 起可收，已登记 5 条候选）；B 轨 +3 → 386；作者网 +3 → 353（X 132）；发信 2 封 → 161；回信率 0/161。
下一步:       ① 下一时窗（18:00）：A 轨今日已 5/5 ⇒ 0 新收；**公告批已刷新**（上界 11-23T15:43:16Z，次日 00:00 时约 24h ≤72h）⇒ 次日 00:00 起按 §0.1 收 3 篇，选前查重；② B 轨 +3：从必读清单外高引且未收录的经典里选，**选前先条目级查重**（`grep arxiv.org/abs/<ID>`）；③ 发信队列：Rico Sennrich（UZH 人员页仍 404）/ Mostafa Dehghani（单源待核）/ Victor Sanh（旧 HF 地址）⇒ 均需先核当前地址，核不到不发；④ 11-25 首批到期 → #1–#7 转 `无应答(>14d)`，做地址级别 × 论文年代分层；⑤ 运维：发件显示名 / SMTP 只发不收 / 任务书 44 KB 超红线。
补推记录:     2026-11-24 09:0x · 本轮 commit 前 `git pull --rebase --autostash`；若 push 被拒按 `fetch + rebase origin/main` 重试（最多 5 次），不 `add -A`。
本轮新增:     A 轨 0（今日 5/5）· B 轨 +3（386）· 作者网 +3（353）· X 已核验 +1（132）· 作者信 +2（161，今日 9/12）· voice_ready 0 · news_ready 0 · 回信率 0/161
阻塞:         ① 🔴 发件显示名 `AI+EDA 招聘 · 自动`（最可能的 0 回信原因），需运维改配置；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到；③ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且 agent 只读 ⇒ 需授权；④ 多数新收作者无当前可核地址（Mathilde Caron 仅 2021 旧地址 / BYOL 作者仅 2020 论文页地址）⇒ 只建档、不猜地址；⑤ `mostafadehghani.com` 已被博彩站占用，**不可**当作者主页/邮箱来源。
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
- **上次采集窗口**：`2026-11-24 15:0x`（**第二百五十三轮 · 15:00 时窗**：A 轨 **0 新收**（今日 5/5 已满；公告批已刷新至 `2026-11-23T15:43:16Z`、15.3h 在窗但额度已满）；B 轨 **+3 → 386**（ALBERT / XLNet / REALM）；作者网 **+3 → 353**（X 132）；发信 **2**（#160 蓝振忠 / #161 Kelvin Guu，今日 9/12））
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`371` 篇（A 轨；`SEEN.md` 为唯一防重台账；本日 A 轨已收 5 篇 → 今日 5/5）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**386 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**一百零五轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**353 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-24（本地 15:0x · 15:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满；公告批已刷新）＋ 🅱 B 轨第一百零六轮 +3 → 386 ＋ 作者网 +3 → 353（X +1 → 132）＋ 发信 2 封 → 161 ＋ 回信率 0/161）** —— **第二百五十三轮**：① 网络：`cat:cs.CL&max_results=5&sortBy=submittedDate`（`--noproxy '*'`）**`200` + `application/atom+xml`**（11,865 B / 5 entry）；⚠️ `published` 上界由 `2026-11-20T18:51:29Z` **前移至 `2026-11-23T15:43:16Z`**（其后 15:23:50Z / 15:14:32Z / 15:11:05Z / 14:44:59Z），距本窗 2026-11-24 07:00 UTC 约 **15.3h < 72h** ⇒ 公告批回到 §0.1 窗内。② A 轨 **0 新收**：今日额度 5/5 已满（00:00 收 3 + 03:00 补 2）⇒ 不凑第 6 篇；只登记「次日 00:00 起可收」+ 同批 5 条候选。③ B 轨 **+3 → 386**：ALBERT `1909.11942`（**8,430**，2019 预印本；factorized embedding `V×H → V×E + E×H` + 跨层参数共享 + SOP 替换 NSP）/ XLNet `1906.08237`（**8,627**，NeurIPS 2019；排列式广义自回归 + Transformer-XL，20 任务超 BERT）/ REALM `2002.08909`（**1,345**，2020 预印本；隐变量知识检索器 + MLM 作唯一信号端到端反传，Open-QA 绝对 +4~16 点）；三 ID 条目级查重 0 命中。④ 作者网 **+3 → 353**：#351 蓝振忠（**lanzhenzhong@westlake.edu.cn**，西湖大学官方师资页 `200` / 45,856 B ⇒ 已发信）/ #352 杨植麟（`kimiyoung.github.io` `200` / 91,449 B 无邮箱、`cs.cmu.edu/~zhiliny/` `503`、`zhiliny.com` 邮箱判另一人 ⇒ 仅建档）/ #353 Kelvin Guu（**kelvin@kelvinguu.com**，主页 `200` / 16,482 B Contact 节 `kelvin 🐌 kelvinguu.com`；X `@kelvin_guu` 双源 ⇒ 已发信）；X **+1 → 132**。⑤ 发信 **2 封**：#160 蓝振忠 中文 185 汉字 `SENT OK 15:04:58`、#161 Kelvin Guu 英文 159 词 `15:05:03`；落款两行、其后无行；正文无项目名；与今日 #153–#159 开头句 / 问句零共用；今日 **9/12**。⑥ 回信率 **0/161**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ **如实记**：ar5iv **0/3**（ALBERT 30s 超时）⇒ 三篇数字仅到摘要粒度；首次落盘后共享副本被并发 git 操作回滚，已按原文重放后提交（发信不受影响）。⑨ 交付：`daily/2026-11-24.html` 15:00 节 + `daily/index.html` 当日行（5/5 · 386 · 353 · 132 · 161 · 0/161）+ `research/2026-11-24.md` §9 + `PAPERS.md` #384–#386 + `AUTHORS.md` #351–#353 + `发送记录.md` §15:00 + draft / body 各 2。
- **2026-11-24（本地 09:0x · 09:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第一百零五轮 +3 → 383 ＋ 作者网 +3 → 350（X +1 → 131）＋ 发信 2 封 → 159 ＋ 回信率 0/159）** —— **第二百五十二轮**：① 网络：`cat:cs.CL&max_results=5&sortBy=submittedDate`（`--noproxy '*'`）**`200` + `application/atom+xml`**（13,309 B / 5 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-24 01:00 UTC 约 **78.1h > 72h** ⇒ 已出公告批窗口）；B 轨 arXiv 批量 `id_list` 两次 **`429`** ⇒ 改单查 `search_query=id:<ID>`（≥3s 间隔）**3/3 `200` + atom**（2,567 / 3,739 / 3,382 B）+ abs 3/3 `200`（41,707 / 46,461 / 44,439 B，`citation_title` + `citation_date` 逐字）+ ar5iv 2/3 部分取回（258,225 / 81,023 B，25s 超时截断）+ OpenAlex 3/3 `200`（94→会议版 24,624 / 2,546 / 2,592，查询日 2026-11-24）。② A 轨 **0 新收**：今日 5/5 已满且公告批出窗 ⇒ 不凑第 6 篇。③ B 轨 **+3 → 383**：Sentence-BERT `1908.10084`（**24,624** 会议版 DOI `10.18653/v1/d19-1410`；arXiv DOI 记 94 分列；siamese/triplet 句向量，10,000 句最相似对 65h → ~5s）/ DeBERTa `2006.03654`（**2,546**，2020 预印本；content/position 解耦注意力 + enhanced mask decoder，半数据超 RoBERTa-Large，1.5B 单模型 SuperGLUE 89.9、集成 90.3）/ Test-time compute scaling `2408.03314`（**2,592**，ICLR 2025；compute-optimal 分配 >4× best-of-N，FLOPs 对齐胜 14× 大模型）；三 ID 条目级查重 0 命中。④ 作者网 **+3 → 350**：#348 Nils Reimers（德文；`info@nils-reimers.de` 站点 contact 页 200 / 11,424 B 当前地址 ⇒ 已发信）/ #349 Charlie Snell（英文；`csnell22@berkeley.edu` 主页 200 / 23,486 B 当前地址；X `@sea_snell` 主页外链 + `x.com/sea_snell` 200 / 165,575 B `og:title` 双源 ⇒ 已发信）/ #350 Pengcheng He（中文；仅 2020 论文页 `penhe@microsoft.com`、MSR 人员页重定向 ⇒ 仅建档）；X **+1 → 131**。⑤ 发信 **2 封**：#158 德文称谓问候 + 英文 191 词 `SENT OK 09:06:52` / #159 英文 197 词 `09:06:52`；落款两行、其后无行；正文无项目名；与今日 #153–#157 开头句 / 问句零共用；今日 **7/12**。⑥ 回信率 **0/159**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-24.html` 09:00 节 + `daily/index.html` 当日行（5/5 · 383 · 350 · 131 · 159 · 0/159）+ `research/2026-11-24.md` §8 + `PAPERS.md` #381–#383 + `AUTHORS.md` #348–#350 + `发送记录.md` §09:00 + draft / body 各 2。
- **2026-11-24（本地 06:0x · 06:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第一百零四轮 +3 → 380 ＋ 作者网 +3 → 347（X 130）＋ 发信 1 封 → 157 ＋ 回信率 0/157）** —— **第二百五十一轮**：① 网络：`cat:cs.CL&max_results=5&sortBy=submittedDate`（`--noproxy '*'`）**`200` + `application/atom+xml`**（13,309 B / 5 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-23 22:00 UTC 约 **75.1h > 72h** ⇒ 已出公告批窗口）；B 轨 `id_list=2006.07733,2103.16302,2004.12832` 批量 `200` + atom（7,976 B / 3 entry）+ DINO 单批 `id_list=2104.14294` `200` + atom（2,699 B）+ abs 3/3 `200`（45,586 / 42,724 / 43,149 B）+ ar5iv 3/3 `200`（904,685 / 640,182 / 201,593 B）+ OpenAlex 3/3 `200`（8,808 / 11,688 / 453）。② A 轨 **0 新收**：今日 5/5 已满（00:00 三篇 + 03:00 两篇）且公告批 75.1h 出窗 ⇒ 不凑第 6 篇。③ B 轨 **+3 → 380**：BYOL `2006.07733`（8,808，NeurIPS 2020；online/target + 慢速 EMA、无负样本；ResNet-50 线性 74.3% / 更大 ResNet 79.6%）/ DINO `2104.14294`（11,688，ICCV 2021；自监督 ViT 特征含分割结构，小 ViT k-NN 78.3%、ViT-Base 线性 80.1%；动量编码器 + multi-crop + 小 patch）/ ColBERT `2004.12832`（453 <500 按「方法论常青」收；BERT 分别编码 + MaxSim late interaction，文档向量离线预计算、剪枝友好；每查询快两个数量级 / FLOPs 少四个数量级）；候选 `2103.16302` 实测为 PiT 非 DINO ⇒ 弃、改用 `2104.14294`。④ 作者网 **+3 → 347**：#345 Omar Khattab（`okhattab@mit.edu`，`omarkhattab.com` 200 / 17,356 B 当前地址 ⇒ 已发信）/ #346 Matei Zaharia（`matei@berkeley.edu`，Berkeley 主页 200 / 57,922 B 当前地址，同论文不发）/ #347 Mathilde Caron（仅 2021 `mathilde@fb.com` 旧地址、主页 404 ⇒ 仅建档）；X +0（130）。⑤ 发信 **1 封**：#157 Omar Khattab 英文 199 词 `SENT OK 06:04:34`；落款两行、其后无行；今日 5/12。⑥ 回信率 **0/157**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-24.html` 06:00 节（A 复核 + B 3 行 + 作者 3 行 + 信 1 卡 + 6 线建议 6 条 + 附录 5 行 + 变更说明）+ `daily/index.html` 当日行（5/5 · 380 · 347 · 130 · 157 · 0/157）+ `research/2026-11-24.md` §7 + `PAPERS.md` #378–#380 + `AUTHORS.md` #345–#347 + `发送记录.md` §06:00 + draft / body 各 1。
- **2026-11-24（本地 03:0x · 03:00 时窗 · 🅰 A 轨 +2 → 今日 5/5 ＋ 🅱 B 轨第一百零三轮 +3 → 377 ＋ 作者网 +3 → 344（X 130）＋ 发信 1 封 → 156 ＋ 回信率 0/156）** —— **第二百五十轮**：① 网络：`cat:cs.CL&max_results=20`（`--noproxy '*'`）**`200` + `application/atom+xml`**（48,824 B / 20 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-23 19:00 UTC 约 **72.1h**，略超 72h ⇒ 按周末/公告批放宽口径入账并如实标注）；A 轨 abs 2/2 `200`（41,095 / 43,285 B）+ arXiv HTML 2/2 `200`（625,184 / 659,504 B，页内无明文邮箱）；B 轨 `id_list` 批量 `200` + atom（8,424 B / 3 entry）+ PaLI 单批 `200`（4,394 B）+ abs 3/3 `200`（42,639 / 43,027 / 45,703 B）+ ar5iv 3/3 `200`（658,843 / 422,625 / 397,253 B）+ OpenAlex 3/3 `200`（19,477 / 362 / 976）。② A 轨 **+2（今日 5/5）**：AutoOntologyBench `2611.27734`（19,947 审计任务 / 18 知识源 / 7 领域；自建本体比检索 +6.1、落后专家本体 13.0）/ DistDNA `2611.27831`（prompt 条件响应分布 + promptwise MMD；方差项 O(1/R)；115 checkpoint 比 LLM DNA +10.36%）；查重 0 命中；`2611.27506` / `2611.27607` / `2611.27973` 已收录 ⇒ 跳过。③ B 轨 **+3 → 377**：MoCo `1911.05722`（19,477，CVPR 2020）/ OWL-ViT `2205.06230`（362 <500 按「本领域权威」收）/ PaLI `2209.06794`（976，ICLR 2023 Notable-top-5%；4B ViT-e、10B 图 / 100+ 语言）；候选 `2301.03728` 经 OpenAlex 实测为另一篇论文 ⇒ 弃。④ 作者网 **+3 → 344**：#342 Matthias Minderer（`mjlm@google.com` 旧地址 ⇒ 仅建档）/ #343 Alexey Gritsenko（`agritsenko@google.com` 单源旧地址 ⇒ 仅建档）/ #344 Bingsheng He 何炳生（`dcsheb@nus.edu.sg`，NUS 官方主页 `200` / 18,121 B 当前地址）；X +0（130）。⑤ 发信 **1 封**：#156 Bingsheng He 中文 202 字 `SENT OK 03:03:29`；落款两行、其后无行；今日 4/12。⑥ 回信率 **0/156**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-24.html`（5 卡 + B 6 行 + 作者 6 行 + 信 4 卡 + 6 线建议 + 附录 7 行 + 变更说明）+ `daily/index.html` 当日行（5/5 · 377 · 344 · 130 · 156 · 0/156）+ `research/2026-11-24.md` 03:00 节 + `PAPERS.md` #375–#377 + `AUTHORS.md` #342–#344 + `发送记录.md` §03:00 + draft / body 各 1。

- **2026-11-24（本地 00:0x · 00:00 时窗 · 🅰 A 轨 +3 → 今日 3/5 ＋ 🅱 B 轨第一百零二轮 +3 → 374 ＋ 作者网 +3 → 341（X 130）＋ 发信 3 封 → 155 ＋ 回信率 0/155）** —— **第二百四十九轮**：① 网络：**`http://export.arxiv.org` 改返回 `301`** ⇒ 切 `https://export.arxiv.org`；`cat:cs.CL&max_results=15`（`--noproxy '*'`）**`200` + `application/atom+xml`**（36,805 B / 15 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-23 16:00 UTC 约 **69.1h < 72h**）；A 轨 abs 3/3 `200`（41,235 / 41,958 / 38,934 B）；B 轨 `id_list` 批量 `200` + atom（10,081 B）+ abs 3/3 `200`（41,847 / 41,473 / 45,205 B）+ ar5iv 3/3 `200`（236,747 / 296,786 / 228,755 B）+ OpenAlex 3/3 `200`（1,835 / 1,142 / 6,929）；X 自检 `200`。② A 轨 **+3（今日 3/5）**：TEA-Bench-BR `2611.27895`（144 tasks / 6,798 隐藏用例 / 杀死 1,955 个非等价变异体；12B 单表 38.0%、FHIR 0；31B 77.8% / 85.2% / 78.7%）/ RoSci `2611.27750`（1,220 样本、六类退化、Parse-Verify-Decide）/ Higher-Order Attention `2611.27764`（CMI + 相邻 key/query + 广义最大熵；摘要无实验 ⇒ 理论线索）；三 ID 查重 0 命中；同批 MemOnce / Tasklets 已收录 ⇒ 跳过。③ B 轨 **+3 → 374**：ViLT `2102.03334`（1,835，ICML 2021 Long）/ FLAVA `2112.04482`（1,142，CVPR 2022，35 任务）/ ALIGN `2102.05918`（6,929，ICML 2021，>10 亿噪声图文对 + 简单双塔）；⚠️ 候选池旧 ID 纠错：`2309.05076` / `2111.05477` / `2012.00571` / `2206.10537` 实测均为无关论文 ⇒ 弃。④ 作者网 **+3 → 341**：#339 Wonjae Kim（`wonjae.kim@navercorp.com`，2021 旧地址 ⇒ 仅建档）/ #340 Amanpreet Singh（无邮箱，主页 `000`）/ #341 Chao Jia（`chaojia@google.com` 单源待核）；X +0（130）。⑤ 发信 **3 封**：#153 Di He 中文 197 字 `SENT OK 00:05:35` / #154 Mingjie Liu 中文 208 字 `00:05:37` / #155 Jiawei Zhao 中文 234 字 `00:05:37`；发前地址复核 3/3 `200`；今日 3/12。⑥ 回信率 **0/155**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-24.html`（3 卡 + B 3 行 + 作者 3 行 + 信 3 卡 + 6 线建议 6 条 + 附录）+ `daily/index.html` 当日行（3/5 · 374 · 341 · 130 · 155 · 0/155）+ `research/2026-11-24.md` + `PAPERS.md` #372–#374 + `AUTHORS.md` #339–#341 + `发送记录.md` §00:00 + drafts / bodies 各 3。
- **2026-11-23（本地 21:0x · 21:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第一百零一轮 +3 → 371 ＋ 作者网 +3 → 338（X +1 → 130）＋ 发信 0（今日 12/12）＋ 回信率 0/152）** —— **第二百四十八轮**：① 网络：`cat:cs.CL&max_results=5`（`--noproxy '*'`）**`200` + atom**（13,309 B / 5 entry，`published` 上界仍 `2026-11-20T18:51:29Z`，距本窗 2026-11-23 13:00 UTC 约 **66.1h < 72h**）；B 轨批量 `id_list` 先遇 **`429`**，改 `search_query=id:<ID>` 单查 **3/3 `200` + atom**（`published` = 2023-11-10T18:59:08Z / 2021-10-15T17:08:57Z / 2022-05-10T19:32:20Z）；abs 3/3 `200`（41,312 / 50,287 / 45,566 B）+ ar5iv 3/3 `200`（597,282 / 309,166 / 633,921 B）+ OpenAlex 3/3 `200`（861 / 2,273 / 627）；X 自检 `200`。② A 轨 **0 新收**：今日 5/5 已满 ⇒ 不凑第 6 篇。③ B 轨 **+3 → 371**：Florence-2 `2311.06242`（861，CVPR 2024；统一任务提示 seq2seq；FLD-5B 54 亿标注 / 1.26 亿图；CIDEr 133.0 / 135.6）/ T0 `2110.08207`（2,273，ICLR 2022 Spotlight；62 数据集 / 12 任务 + 多套模板；零样本超 16× 大模型）/ UL2 `2205.05131`（627；MoD R/S/X，`r ∈ {0.15,0.5}`、`μ ∈ {3,8,64}`；20B、50 任务 SOTA、胜 175B GPT-3 零样本 SuperGLUE）。④ 作者网 **+3 → 338**：#336 Bin Xiao（中文，无公开明文邮箱 ⇒ 仅建档）/ #337 Victor Sanh（旧 HF 地址不用于发信；X `@VictorSanh` 双源）/ #338 Mostafa Dehghani（`dehghani@google.com` 单源待核；`@m_dehghani` 1 follower 判他人）；X **130**。⑤ 发信 **0 封**（累计 152）：今日 12/12 硬上限 ⇒ 只选题建档；待发 Victor Sanh / Mostafa Dehghani / Rico Sennrich / Jiawei Zhao / Di He / Mingjie Liu。⑥ 回信率 **0/152**，0 封到期（最早 11-25）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-23.html` 21:00 节（A 证据 + B 3 行 + 作者 3 行 + 信件 0 + 6 线建议 6 条 + 附录）+ `daily/index.html` 当日行（371 · 338 · 130 · 152 · 0/152）+ `research/2026-11-23.md` + `PAPERS.md` #369–#371 + `AUTHORS.md` #336–#338 + `发送记录.md` §21:00。


- **2026-11-23 18:0x ~ 2026-11-22 18:0x（更早 8 条）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-23.md`「归档 · MEMORY 滚动（r249 后折出）」；结论不变，勿以指针替代原文。

- **2026-11-22 06:0x ~ 2026-11-19（更早轮次）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-22.md`「归档 · MEMORY 滚动（第九十四轮后折出）」与 `daily-memories-research/2026-11-21.md` / `2026-11-20.md` / `2026-11-19.md` / `2026-11-18.md`；结论不变，勿以指针替代原文。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
