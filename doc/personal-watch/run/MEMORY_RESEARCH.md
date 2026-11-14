# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；主轮 06:00 / 18:00（loop 实际按 0,3,6,9,12,15,18,21 八时窗唤）
已完成:       [r174 · 本地 2026-11-14 22:3x · 21:00 时窗：A 轨复核 0 新收 + B 轨第三十轮 + 第 40–43 封信（#42 为重复事故） + voice_ready V28] ① A 轨 `cat:cs.CL` 单查询 **`200` + atom**（87,661 B / 0.94 s），`totalResults` **125,322**（与 12:00 / 15:00 逐值相同）、最新 30 条 `published` 上界 **`2026-11-12T18:59:52Z`** ⇒ 批未前进；当日 5/5 ⇒ **0 新收**。② **B 轨 +4 → 119**：GPT-4 `2303.08774`（**38,329**，预印本，281 署名）· Roofline（CACM 52(4):65–76，**2,165**，Crossref，无 arXiv）· SigLIP `2303.15343`（**1,884**，ICCV'23 Oral pp. 11941–11952）· 去重 `2107.06499`（ACL 2022 pp. 8424–8445，**226**，Crossref）；arXiv `id_list` `200`+atom（32,678 B，作者数 281/4/7 逐字核）；必读清单仍 **37/37**。③ **作者网 +3 → 122**：Xiaohua Zhai（`@XiaohuaZhai` 已核；`xiaohuazhai[at]gmail.com` 取自本人页 Contact 区块，218,511 B ⇒ **已发信**）· Samuel Williams（LBNL/NERSC 页无明文邮箱 ⇒ 仅建档）· Katherine Lee（ACL 页无邮箱 ⇒ 仅建档）；Bei Yu 转 **已发信**；X 已核验 **67**、待 follow **57**、已 follow **0**。④ **发信 2 封（均中文）** `SENT OK 22:39:11`（Bei Yu，272 字）/ `22:39:19`（Xiaohua Zhai，293 字），今日 **11** / 累计 **43**（含并行会话造成的 1 封重复：#42 与 #40 同收件人 Bei Yu，74 秒内两封 ⇒ 已记 `research/mail/INCIDENT-2026-11-14-duplicate-send.md`，本轮起停止继续发信）。⑤ **回信率 0 / 43**（`replies/` 仅 README；另有 `REPLY_DIAGNOSIS.md` 诊断：样本年龄 0–3 天、全部未到期、无退信可视）；新诊断：**发件通道无 IMAP/POP3**、发件显示名为招聘配置 ⇒ 待运维决策。⑥ `voice_ready` **1**（Tri Dao 2026-10-28 H-Net 动态分词 vs BPE，`og:title`+`og:description` 双源一致 ⇒ **V28**）；`news_ready` **0**。⑦ **交付**：`daily/2026-11-14.html` **134,156 B**（div 137/137、table 30/30、tr 179/179、td 558/558、th 122/122、details 5/5、h2 44/44、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html`（119 篇 / 122 人 / 43 封 / 131.0 KB）；`PAPERS.md` 119 / `AUTHORS.md` 122；`2026-11-14.md` 21:00 节 / `ARXIV_API.md §9.174` / `发送记录.md` +2；6 线建议 6 条。
当前动作:     ✅ 本轮闭环：A 轨 0 新收 + B 轨 119 + 作者网 122 + 2 封信 + voice_ready 1 + 日报 / index / 记忆 + 提交推送。
下一步:       ① **次日 00:00 轮**：A 轨新批落地则补 3 篇（否则复核）；② B 轨候选：AgentBench / Qwen 技术报告 / BLIP-2 / Constitutional AI（须实测被引）；③ 关注 43 封回信（0/43，最早 2026-11-25 到期）；④ 找 Samuel Williams / Katherine Lee 的现行邮箱；⑤ 待用户手动 follow 57 条已核验 handle 后改「已follow」。
本轮新增:     A 轨 **0（5/5 已收口）** · B 轨 **+4**（119）· 作者网 **+3**（122）· 作者信 **4**（累计 43；含 1 封重复事故 #42）· **0 follow** · `voice_ready` **1** · `news_ready` **0** · 回信率 **0/43**
阻塞:         ① **X 写操作需登录态** ⇒ follow 无法自动执行；② **OpenAlex 当日免费额度用尽**（`Rate limit exceeded`）⇒ 改用 Crossref 单源；③ 发件通道**只发不收**（无 IMAP/POP3）⇒ 回信无法自动读取；④ 发件显示名为招聘配置，学术信可能被误判群发（待运维）；⑤ 高知名度作者邮箱多在反爬页/无明文 ⇒ 覆盖率受限，不猜。
ERROR_COUNT:  27（本轮 +4：**重复发信事故 #42**（同收件人 74 秒内两封）计 1、OpenAlex `Rate limit exceeded` 计 1、Crossref 旧 DOI `404` 计 1、LBNL profile JS 页 + NERSC 页无明文邮箱计 1；arXiv 2/2 `200`、OpenAlex 3/3、Crossref 4/4、邮箱页 4/4、X profile 4/4、推文页 1/1）
```

> ⚠️ **22:4x 勘误（并行事故事件 · 第二个会话追加）**：本轮实际发出 **4 封**（22:39:11 Bei Yu / 22:39:19 Xiaohua Zhai / **22:40:25 Bei Yu（重复，违规）** / 22:40:45 Chunyuan Li）⇒ 累计 **43** 封，其中 **1 封属同作者重复**（违反「同作者 ≤1」）；**累计回信率 0 / 43**，**0 封到期**（最早 2026-11-25）。事故根因 = 两个 agent 会话共用同一工作副本且无互斥锁；已入仓 `research/mail/INCIDENT-2026-11-14-duplicate-send.md`（时间线 + 防再犯 4 条）与 `research/mail/REPLY_DIAGNOSIS.md`（分日/语言/地址分层 + 五个竞争假设 + 11-18 / 11-25 / 11-28 观察点）。本轮**已停止继续发信**，**未补发道歉信**（避免第三次触达）。

---

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
  **A（本线）**：**✅ 首封已发（2026-10-13 18:22:07，`SENT OK`）**。收件人 `paul.liu@cxmt.com`（固定）；主题 `[论文日报] 10-13 精选 5 篇（BaiZe/ZhuLong 相关）`；选文 5 篇（3 借鉴 `2610.12995`/`2610.13835`/`2610.13889` + 2 科普 `2610.13917`/`2610.12866`）；**附件 4 个 PDF · 8,601,183 B（8.20 MB）≤ 20MB**；PDF 路径 `research/pdf/2026-10-13/`（**不入 git**）；**`2610.13917` PDF 17.2MB 超单篇预算 ⇒ 不附、正文给链接 + 摘要**（符合「超 ⇒ 只附超额篇的链接 + 摘要」）；草稿 `research/mail/drafts/2026-10-13-daily-report.md`；台账 `research/mail/发送记录.md`（**没写=没发**）。**最近一封（第 23 封）：2026-11-04 18:09:25 `SENT OK`（11-04 当日 5/5 收口；5 个 PDF / 16.97 MiB ≤ 20 MB 单封；主题 `[论文日报] 11-04 精选 5 篇（BaiZe/ZhuLong 相关）· 当日 5/5 收口`；正文 `mail/2026-11-04-body.txt`、日志 `/tmp/mail_send_r132b.log`）**；上一封（第 22 封）：2026-11-04 06:09:26 `SENT OK`（**日报第 22 封 · 11-03 当日 5/5 收口（含中断补跑）**；5 个 PDF / **7,617,754 B ≈ 7.27 MiB**；主题 `[论文日报] 11-03 精选 5 篇（BaiZe/ZhuLong 相关）· 当日 5/5 收口（含中断补跑）`；正文 `mail/2026-11-03-body.txt`、日志 `/tmp/mail_send_r131.log`）**；再上一封：2026-10-31 18:32:24 + 18:33:51 `SENT OK`（**日报第 19 封 · 分包 2 封**：`1/2` 附早 3 篇 = 5,988,962 B ≈ 5.71 MB、`2/2` 附 PhysCount = 14,658,374 B ≈ 13.98 MB；`2610.38957` 的 **23.13 MB** PDF 超 20 MB ⇒ **只给链接 + 摘要**；主题 `[论文日报] 10-31 精选 5 篇（BaiZe/ZhuLong 相关）(1/2)(2/2)`；正文 `mail/2026-10-31-body-{1of2,2of2}.txt`、草稿 `mail/drafts/2026-10-31-daily-report.md`、日志 `/tmp/mail_send_r124_{1,2}.log`）**；上一封：2026-10-23 18:13:47 + 18:15:12 `SENT OK`（第 8 封 · 5 篇 PDF 合计 22,690,111 B ≈ 21.64 MB > 20 MB ⇒ 分包 2 封：1/2 附 `2610.29352`+`2610.29171`+`2610.29870` = 6,213,148 B ≈ 5.93 MB、2/2 附 `2610.31651`+`2610.30769` = 16,476,963 B ≈ 15.71 MB）**；上一封：2026-10-22 18:11:41 + 18:12:25 `SENT OK`（第 7 封，因 5 篇 PDF 合计 26,222,619 B ≈ 25.01 MB > 20 MB ⇒ **按规格分包 2 封**：1/2 附 `2610.28500`+`2610.28385` = 19,240,987 B ≈ 18.35 MB、2/2 附 `2610.28380`+`2610.29025`+`2610.30035` = 6,981,632 B ≈ 6.66 MB，两封合计 5 篇 / 附 5，5/5 校验通过）**；**本职能免审直发**，频次 每天 1 封，与「作者请教信」**互不占配额**。


---

## 1. 状态头

- **线**：research（arXiv 论文采集/整理）
- **任务书**：`WATCH_RESEARCH_TASK.md`（只读）
- **产物**：`research/<YYYY-MM-DD>.md`（日报）· `research/SEEN.md`（去重台账，主键 arXiv ID）· `research/INDEX.md`（索引）· `research/papers.jsonl`（结构化台账）· `research/ARXIV_API.md`（R1）· **`research/TOP_K.md` + `research/TOP_K.jsonl`**（精选排序；源 `TOP_K_notes.md` + **`TOP_K_takeaways.json`**）· **`research/TAKEAWAYS.md`**（第 3 批 A 节：≤5 条可借鉴结论）· **`research/video/SHORTLIST.md` + `research/video/scripts/<arXiv_ID>.md`**（第 3 批 B 节：视频线 V1/V2）
- **工具/回归**：`research/arxiv_fetch.py` + `research/test_arxiv_fetch.py`（49/49）· **`research/top_k.py`（含 `--takeaways-json`）+ `research/test_top_k.py`（25/25）**
- **日流水**：`daily-memories-research/<YYYY-MM-DD>.md`
- **关注领域**：LLM · SLM · 多模态 · agent harness（+ 邻域，见任务书 §1）
- **采集节律**：⏰ **每天 2 次定时唤醒 · 06:00 / 18:00（本地时区）**（2026-10-07 用户令：由「每 30min」改为「每天 2 次」，`SCHEDULE_HOURS=6,18`，时窗内零 token 分段睡）；`WAITING` 字段保留仅供人读、**已不影响唤醒节律**；回退：`WATCH_SCHEDULE_HOURS=` 置空 ⇒ `WAITING=1` 睡 **30min** / `WAITING=0` 短睡 **60s**
- **上次采集窗口**：`2026-11-14`（**第一百七十轮 · 本地 2026-11-14 06:0x（06:00 时窗：A 轨复核 0 新收 + B 轨第二十六轮 + 第 35 封信）**；窗口内最晚 `published = 2026-11-12T18:59:55Z`（批未前进）；A 轨 5/5 `200`+atom；B 轨 4 篇（3 条走 `id_list` `200`+atom，DREAMPlace 无 arXiv 经两次检索确认）；B 轨 +4 → 103；作者网 +7 → 106；发信 1 封）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`341` 篇（另候选 **4,558** 篇 + **候选（RSS补充）507** 篇 ⇒ 状态行合计 **5,406**；`SEEN.md` 文件 **5,665 行**；仅存 `SEEN.md` 防重；**本轮 +2 收录**（`2611.14459` / `2611.13560`，2026-11-10 公告批次；当日累计 +5）；`papers.jsonl` **341** 行）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**119 篇**，8 字段 + OpenAlex 单源被引 + Crossref 会议/页码 + 首次收录日；**二十六轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**106 人**关系网 + X 只读证据 + 待 follow 清单 **51** 个 + 发信记录 **35 封** + 言论台账 V1–V24（第二十六轮 0 新增））；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`（与日报草稿同目录，用文件名区分；无 arXiv 的用 `<会议>-<年份>.md`）。


---



## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-14（本地 22:3x · 21:00 时窗 · A 轨复核「批未前进」+ 🅱 B 轨第三十轮 + 第 40–43 封信（#42 重复事故））** —— **第一百七十四轮**：① A 轨 `cat:cs.CL` 单查询 **`200` + atom**（87,661 B / 0.94 s），`totalResults` **125,322**、`published` 上界 `2026-11-12T18:59:52Z` ⇒ 批未前进，当日 5/5 ⇒ **0 新收**。② B 轨 **+4 → 119**：GPT-4 `2303.08774`（38,329）· Roofline（CACM 52(4):65–76，2,165，Crossref）· SigLIP `2303.15343`（1,884，ICCV'23 Oral）· 去重 `2107.06499`（ACL 2022，226，Crossref）；OpenAlex 当日额度用尽 ⇒ 后两篇改 Crossref；Roofline 旧 DOI `404` 已更正。③ 作者网 **+3 → 122**：Xiaohua Zhai（`@XiaohuaZhai` 已核、已发信）· Samuel Williams / Katherine Lee（无明文邮箱，仅建档）；Bei Yu 转已发信；X 已核验 67、待 follow 57、已 follow 0。④ 发信 **2 封中文** `SENT OK 22:39:11`（Bei Yu 272 字）/ `22:39:19`（Xiaohua Zhai 293 字）；今日 9 / 累计 41；回信率 **0/41**，新诊断＝发件通道无 IMAP/POP3、发件显示名为招聘配置。⑤ `voice_ready` 1（Tri Dao 2026-10-28，V28）；`news_ready` 0。⑥ 交付：`daily/2026-11-14.html` 130,686 B（标签全配平、0 script、0 残留 `**`）+ `index.html`（119 篇 / 122 人 / 43 封 / 131.0 KB）；`PAPERS.md` 119 / `AUTHORS.md` 122；`ARXIV_API.md §9.174`；6 线建议 6 条。
- **2026-11-12（18:00 / 21:00 两轮，r158–r159）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-14 r170 唤醒时执行）」；含 B 轨第十四 / 十五轮、作者网与发信增量，勿以本指针替代结论。
- **2026-11-14（本地 09:0x · 09:00 时窗 · A 轨复核「批未前进」+ 🅱 B 轨第二十七轮）** —— **第一百七十一轮**：① A 轨 5/5 `200`+atom（1.24/2.48/1.97/2.23/1.43s），`totalResults` 与 06:00 逐值相同、窗口上界仍 `2026-11-12T18:59:55Z` ⇒ 批未前进；merged 391 / SEEN 7 / fresh 384；当日 5/5 ⇒ **0 新收**。② B 轨 +4 → 107：**Latent Diffusion `2112.10752`（20,670，CVPR 2022）· MuZero `1911.08265`（2,075，Nature 2020 588:604–609）· AutoDMP（ISPD 2023，67，pp.149–157，无 arXiv）· DREAM-GAN（ISPD 2023，16，pp.141–148，无 arXiv）**；OpenAlex 4/4 + Crossref 3/3 `200`；⚠️ **更正**：候选池 `2207.11240` 实为 Discrete Key-Value Bottleneck ⇒ LDM 真 ID `2112.10752`；必读清单仍 37/37。③ 作者网 +4 → 110：`@robrombach`（核验）· Ommer（`b.ommer@lmu.de` 已发信）· Lim（`sl186@gatech.edu` 已发信）· Patrick Esser（未找到）；X 已核验 62、待 follow 52。④ 发信 2 封 `SENT OK 09:09:16`（英文 188 / 184 词，发送前 `wc -w` 已核），今日 5 / 累计 37。⑤ `voice_ready` **1**（Hassabis 2026-11-11 AlphaGenome 2，`og` 全文核验）；`news_ready` 1（不新增）。⑥ 交付：`daily/2026-11-14.html` **80,669 B**（标签全配平、0 script、0 残留 `**`）+ `index.html`（107 篇 / 110 人 / 37 封）；`PAPERS.md` 107 / `AUTHORS.md` 110；`2026-11-14.md` 09:00 节 / `ARXIV_API.md §9.171` / `发送记录.md` +2。
- **2026-11-14（本地 06:0x · 06:00 时窗 · A 轨复核「批未前进」+ 🅱 B 轨第二十六轮）** —— **第一百七十轮**：① A 轨 5/5 `200`+atom（1.74/1.67/1.65/1.19/6.60s），`totalResults` 与 11-13 各轮**逐值相同**、窗口上界仍 `2026-11-12T18:59:55Z` ⇒ 批未前进；merged 391 / SEEN 7 / fresh 384；当日 5/5 ⇒ **0 新收**。② B 轨 +4 → 103：**Adam `1412.6980`（101,807，ICLR 2015）· BatchNorm `1502.03167`（34,937，ICML 2015 PMLR 37:448–456）· GAN `1406.2661`（9,668，仅预印本记录）· DREAMPlace（DAC 2019，177；TCAD 205 不相加；`ti:`/`all:` 两次检索 0 entry ⇒ 无 arXiv）**；OpenAlex 4/4 `200`；S2 `429` 未取；必读清单仍 37/37。③ 作者网 +7 → 106：**Ian Goodfellow `@goodfellow_ian`**（bio 含 Inventor of GANs）· **Jim Fan `@DrJimFan`** · **David Z. Pan**（`dpan@ece.utexas.edu` 取自 UT Austin 现行页，已发信）· Kingma / Jimmy Ba / Ioffe / Szegedy 未找到邮箱或 X；`@diederikkingma` 17 followers、`@davidzpan` 0 followers、`@jimmyba` 无账号信息 ⇒ 不登记；X 已核验 61、待 follow 51。④ 发信 1 封 `SENT OK 06:08:21`（英文 **190** 词，发送前 `wc -w` 已核），今日 3 / 累计 35。⑤ `voice_ready` **0**（Goodfellow pinned 玩笑 / Jim Fan 无 `og:description` / Tri Dao 已用 / Andrew Ng 活动公告）；`news_ready` 1。⑥ 交付：`daily/2026-11-14.html` **65,131 B**（标签全配平、0 script、0 残留 `**`）+ `index.html`（103 篇 / 106 人 / 35 封）；`PAPERS.md` 103 / `AUTHORS.md` 106；`2026-11-14.md` 06:00 节 / `ARXIV_API.md §9.170` / `发送记录.md` +1。
- **2026-11-13（00:00 / 03:00 两轮，r160–r161）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-13.md`「归档 · MEMORY 滚动（2026-11-14 r171 唤醒时执行）」；含 B 轨第十六 / 十七轮与发信增量，勿以本指针替代结论。
- **2026-11-12（本地 03:0x–15:2x · 03/06/09/12/15 五轮，r152–r157 及更早）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-13 r161 唤醒时执行）」；含 B 轨第九至十三轮、A 轨补齐 5/5 与各轮发信/作者网增量，勿以本指针替代结论。






- **2026-11-13（本地 12:0x · 12:00 时窗）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-14.md`「归档 · MEMORY 滚动（2026-11-14 r174 唤醒时执行）」。



- **2026-11-13（本地 15:0x · 15:00 时窗）** 原文已按 §5 滚动归档 → 同上「归档 · MEMORY 滚动（r174）」。



- **2026-11-13（本地 18:0x · 18:00 时窗）** 原文已按 §5 滚动归档 → 同上「归档 · MEMORY 滚动（r174）」。
- **2026-11-13（本地 21:0x · 21:00 时窗）** 原文已按 §5 滚动归档 → 同上「归档 · MEMORY 滚动（r174）」。


- **2026-11-14（本地 00:0x · 00:00 时窗 · A 轨新批首次落地 ＋ 早报 3/5 ＋ 🅱 B 轨第二十四轮 ＋ 第 33 封信）** —— **第一百六十八轮**：① **判据纠正**：A 轨单分类 5 查询 **5/5 `200`+atom**（13.52 / 5.40 / 17.91 / 19.45 / 11.40 s），`totalResults` 与 11-13 各轮**逐值相同**，但独立校验 feed `updated=2026-11-13T15:21:17Z`、窗口内最晚 `published` 由 `2026-11-10T18:59:54Z` 推进到 `2026-11-12T18:59:55Z` ⇒ **「总数不变 ≠ 索引没动」**；merged 368 / seen 0 / fresh 368（`raw/2026-11-14-00h-candidates-r168.json`）。② **A 轨 +3（3/5）**：`2611.16991` AnalogLayoutWorld（40 任务 / 13 配置 / 91.1% 产出 vs 23.0% 验收）· `2611.16913` CADET（100k 零 DRV 合成板 / 17 统计 vs 142 真实板 / 38.0%→67.2%）· `2611.15006` EvoX（691 对 56.2%、+3.0pp）。③ **B 轨 +4 → 95**：PPO `1707.06347`（**31,326**）· DDPM `2006.11239`（**11,034**）· ZeRO `1910.02054`（**1,432**，SC 2020）· SAM `2304.02643`（**16,904**，ICCV 2023）；arXiv `id_list` `200`+atom（8,918 B）+ OpenAlex 4/4 `200`。④ **作者网 +2 → 97**：John Schulman `@johnschulman2`（`joschu.net` 无邮箱 ⇒ 不发信）· Pieter Abbeel `@pabbeel`（`pabbeel AT cs.berkeley.edu` 取自 contact 页 ⇒ **已发信**）；Jonathan Ho / Alexander Kirillov 未找到、`@akirillov` 判非本人；X 已核验 **57**、待 follow **47**。⑤ **发信 1 封 `SENT OK 00:08:31`**（英文 **194** 词，发送前 `wc -w` 已核），今日 1 / 累计 33。⑥ `voice_ready` **0（本期无）**（3 条候选推文正文均截断）；`news_ready` **1**（AnalogLayoutWorld）。⑦ **交付**：`daily/2026-11-14.html` **30,283 B**（div 70/70、table 5/5、tr 24/24、td 76/76、th 18/18、h2 8/8、details 1/1、footer 1/1、0 script、0 残留 `**`）+ `index.html`（95 篇 / 97 人 / 33 封）；`PAPERS.md` 95 / `AUTHORS.md` 97；`2026-11-14.md` / `ARXIV_API.md §9.168` / `发送记录.md` +1；6 线建议 6 条（逐线覆盖）。


- **2026-11-14（本地 03:0x · 03:00 时窗 · A 轨补满 5/5 ＋ 🅱 B 轨第二十五轮 ＋ 第 34 封信）** —— **第一百六十九轮**：① A 轨**复用 00:00 轮 368 条候选**（不重复请求列表接口），`id_list` 6 ID ⇒ **`200` + atom（15,365 B / 6 entry）**；补 2 篇：`2611.17334` Unbundling（视觉先验非必需 / 专用容量是关键 / 融合中加入可降首 token 时延）· `2611.17304` 数据库调试（8 起事故，5/5 并发事故均有访问缺口，主张取证层）⇒ 今日 **5/5**。② **B 轨 +4 → 99**：GRPO `2402.03300`（**11,153**）· MAE `2111.06377`（**10,217**，CVPR 2022）· S4 `2111.00396`（**2,741**，ICLR 2022 HM）· DreamerV3 `2301.04104`（**1,962**，Nature 2025）；OpenAlex 4/4 `200`；**更正**候选「S4 = `2110.13985`」实为 LSSL。③ 作者网 **+2 → 99**：Saining Xie `@sainingxie`（`saining.xie@nyu.edu` 由本人页拼装 ⇒ **已发信**）· Danijar Hafner `@danijarh`（无邮箱 ⇒ 不发信）；X 已核验 **59**、待 follow **49**、已 follow 0。④ 发信 1 封 `SENT OK 03:02:54`（英文 **197** 词，发送前 `wc -w` 已核），今日 2 / 累计 **34**。⑤ `voice_ready` **0**（5 条推文页逐条核 `og:title`；1 他人推文 / 2 上下文依赖 / 2 已用 / 1 超 30 天）；`news_ready` **1**。⑥ 交付：`daily/2026-11-14.html` **47,966 B**（div 111/111、table 6/6、tr 39/39、td 125/125、th 21/21、h2 10/10、details 1/1、0 script、0 残留 `**`）+ `index.html`（99 篇 / 99 人 / 34 封）；`PAPERS.md` 99 / `AUTHORS.md` 99；`2026-11-14.md` / `发送记录.md` +1；另修 Abbeel 词数 187 → 194。⑦ 6 线增量建议 **6 条**（逐线覆盖）。


- **2026-11-14（本地 12:0x · 12:00 时窗 · A 轨复核「批未前进」+ 🅱 B 轨第二十八轮）** —— **第一百七十二轮**：① A 轨 5/5 `200`+atom（7.02/3.53/5.30/3.92/7.17s），`totalResults` 与 09:00 **逐值相同**（125,322/213,258/299,025/212,730/31,041），窗口 `published` 上界仍 **`2026-11-12T18:59:55Z`** ⇒ 批未前进；merged 391 / SEEN 7 / 新候选 384 ⇒ 当日 5/5 ⇒ **0 新收**。② B 轨 +4 → **111**：Genie `2402.15391`（**258**；⚠️ `2402.08015` 实为 **Walia-LLM** ⇒ 已更正）· Hitting the Memory Wall（**1,783**，ACM SIGARCH CAN 23(1):20–24，1995，无 arXiv）· Deep Learning（**90,176**，Nature 521:436–444）· AlexNet（**114,712**，CACM 60(6):84–90 / NeurIPS 2012，两版不相加）；OpenAlex 4/4、Crossref 3/3 `200`；arXiv API 持续 `429` ⇒ Genie 元数据取 **abs 页**（`200` / 45,346 B）。③ 作者网 +6 → **116**：`@ylecun` · `@Yoshua_Bengio` · `@_rockt` · `@jeffclune`（四者 X 已核验；Clune `jeff.clune@ubc.ca` 取自 UBC 现行人员页 ⇒ **已发信**）· Krizhevsky / McKee 未找到 X；X 已核验 **66**、待 follow **56**、已 follow **0**。④ 发信 1 封 `SENT OK 12:06:47`（Clune · Genie，英文 **175** 词），今日 **6** / 累计 **38**。⑤ `voice_ready` **1**（Bengio 2026-11-13 safe-by-design，V26）；`news_ready` **0 新增**。⑥ 交付：`daily/2026-11-14.html` **98,274 B**（div 127/127、table 21/21、tr 131/131、td 418/418、th 85/85、h2 31/31、details 3/3、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html`（111 篇 / 116 人 / 38 封）；6 线建议 **6 条**。

- **2026-11-14（本地 15:0x · 15:00 时窗 · A 轨复核「批未前进」+ 🅱 B 轨第二十九轮 + 第 39 封信 + 🆕 回信跟踪制度化）** —— **第一百七十三轮**：① A 轨 `cat:cs.CL` 单查询 `200`+atom（87,661 B / 1.24 s），`totalResults` **125,322**（与 12:00 逐值相同）、最新 30 条 `published` 上界 **`2026-11-12T18:59:52Z`** ⇒ 0 新收（当日 5/5）。② B 轨 **+4 → 115**：phi-1 `2306.11644`（1,104）· OSWorld `2404.07972`（686，NeurIPS 2024 pp. 52040–52094）· ML-for-EDA `2102.03357`（388，TODAES 26(5):1–46）· PIM Primer `2012.03112`（92）；arXiv `id_list` `200`+atom（12,315 B）+ OpenAlex 4/4 `200`。③ 作者网 **+3 → 119**：Tianbao Xie（官方 README 维护者邮箱 ⇒ 已发信）· Bei Yu（`byu[at]cse.cuhk.edu.hk` ⇒ 待跟踪）· Suriya Gunasekar（`404` ⇒ 未找到）；X 已核验 66、待 follow 56、0 新增 handle。④ 发信 1 封 `SENT OK 15:04:20`（OSWorld，**中文 296 字**，落款两行），今日 7 / 累计 **39**。⑤ **回信跟踪落地**：`replies/` README 在仓 + `发送记录.md` 39 行状态表（三值 + 到期日）；**回信率 0/39**。⑥ voice_ready 1（Percy Liang 2026-11-10 Marin 设计权衡，V27）；另两条候选实为他人推文（`@classiclarryd` / `@suze_va`）⇒ 丢弃；`news_ready` 0。⑦ 交付：`daily/2026-11-14.html` **115,244 B**（div 132/132、table 26/26、tr 157/157、td 494/494、th 106/106、h2 38/38、details 4/4、footer 1/1、0 script、0 残留 `**`）+ `index.html`（115 篇 / 119 人 / 39 封 / 112.6 KB）；`PAPERS.md` 115 / `AUTHORS.md` 119；`ARXIV_API.md §9.173`；6 线建议 6 条。

- **2026-11-13（06:00 / 09:00 两轮，r162–r163）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-13.md`「归档 · MEMORY 滚动（2026-11-14 r172 唤醒时执行）」。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
