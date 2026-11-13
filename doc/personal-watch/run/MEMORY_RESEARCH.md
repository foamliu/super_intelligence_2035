# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；06:00 / 18:00 主轮（loop 实际按 0,3,6,9,12,15,18,21 八时窗唤）
已完成:       [r166 · 本地 2026-11-13 18:0x · 18:00 时窗：**索引未再变动** + A 轨 0 新收 + B 轨第二十二轮] ① A 轨单分类 5 查询 **5/5 `200`+atom**（4.69/1.93/3.64/6.42/2.67s，串行 ≥3.2s）；`totalResults` = 125,322/213,258/299,025/212,730/31,041，与 15:00 轮**逐值相同** ⇒ 如实记「索引没动」（≠「无新提交」）；merged 391 / seen 2 / fresh **389**（`raw/2026-11-13-18h-candidates-r166.json`）；当日 5/5 已收口 ⇒ **0 新收**；② **B 轨 +4 → 87**：Distilling the Knowledge `1503.02531`（**26,232**，NIPS 2014 DL Workshop，无会场 DOI）· GQA `2305.13245`（**1,522**，EMNLP 2023 DOI `10.18653/v1/2023.emnlp-main.298`，pp. 4895–4901）· Orca `2306.02707`（**622**，预印本）· Mistral 7B `2310.06825`（**10,625**，Apache 2.0）；arXiv `id_list` 4 ID `200`+atom（10,007 B；⚠️ **`http://` 端点 `301`+0 B ⇒ 改 `https://` 才 `200`**，已写入 `ARXIV_API §9.166`）+ OpenAlex 4/4 `200`；必读清单仍 **10/10 组、37/37 条目**；③ **作者网 +3 → 93**：Geoffrey Hinton `@geoffreyhinton`（邮箱 `geoffrey.hinton@gmail.com` 取自本人当前主页明文 `geoffrey [dot] hinton [at] gmail [dot] com`，**已发信**）· Jeff Dean `@JeffDean`（bio 自述 `Co-founder & CEO of Discovery Loop`，无邮箱 ⇒ 不发信）· Joshua Ainslie（`research.google` 两次超时 / MSR 页 `404` ⇒ 邮箱与 X 均**未找到**）；另**更正** Arthur Mensch `@arthurmensch`；X 已核验 **53**、待 follow **46**、已 follow **0**；④ **发信 1 封 `SENT OK 18:05:17`**（Hinton，英文 **186** 词，发送前 `wc -w` 已核）；今日累计 **10**、累计 **31**；⑤ `voice_ready` **2 条**（**V21** Tim Dettmers 2026-10-18 + **V22** Jeff Dean 2026-11-06，均推文页 `og:title`/`og:description` 全文核验）；`news_ready` **0**（不硬凑）；⑥ **交付**：`daily/2026-11-13.html` **117,085 B**（div 128/128、table 32/32、tr 183/183、td 684/684、th 145/145、h2 45/45、details 5/5、footer 1/1、**0 script**、0 残留 `**`；并补上历史遗留无开标签的 `</footer>`）+ `daily/index.html`（87 篇 / 93 人 / 31 封 / 114.3 KB）；`PAPERS.md` **87** / `AUTHORS.md` **93**；`2026-11-13.md §11`；`ARXIV_API.md §9.166`；`发送记录.md` +1；⑦ 6 线新增建议 **5 条**（pretrain / data / harness / zhulong；**vision · designflow 明写「无」**）。
当前动作:     ✅ 本轮闭环：A 轨复核（索引未动、额度满 ⇒ 0 新收）+ B 轨第二十二轮（4 篇 + 3 人 + 1 封信 + V21/V22 投料）+ 日报 / index / 记忆 + 提交推送。
下一步:       ① **11-14 00:00 轮优先从 368 + 389 条候选里选 5 篇**（按 published ≤72h 重筛；注意 11-13 批已落盘未收）；② B 轨继续「补充 / 更正」候选：Leveling Up（OpenROAD 轨迹 2022，13 ⇒ 只作补充）/ 其余见 `PAPERS.md` 候选池；③ 关注 31 封回信（退信记「通道失效」不重发）；④ 用户手动 follow 46 个已核验 handle 后改「已follow」；⑤ 若 X 写操作仍不可用，继续只做「待 follow 清单」。
本轮新增:     A 轨 **0**（额度 5/5 已满）· B 轨 **+4 经典**（87）· 作者网 **+3 人**（93）· 作者信 **1 封**（累计 31）· **0 follow** · `voice_ready` **2 条**（V21/V22）· `news_ready` 0
阻塞:         ① **X 写操作需登录态** ⇒ follow 无法自动执行；② Joshua Ainslie 无可核验邮箱 / X、Jeff Dean 无个人邮箱 ⇒ 按令**不猜、不发信**；③ 本 shell 不继承 `HTTPS_PROXY` ⇒ 抓 X 必须显式 `-x http://127.0.0.1:7897`；④ **arXiv `http://` 端点返回 `301`** ⇒ 一律用 `https://export.arxiv.org`；⑤ 外部站点（`research.google` / `microsoft.com/research` / `mistral.ai/team`）直连易超时 ⇒ 必要时走代理或写「未找到」。
ERROR_COUNT:  15（本轮 0 新增：arXiv 5/5、arXiv id_list 4/4、OpenAlex 4/4、作者页 2/2 尝试、X profile 3/3、推文页 2/2 均成功；`http://` 的 `301` 已按流程改 https，不计为错误）
```

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
- **上次采集窗口**：`2026-11-12`（**第一百五十七轮 · 本地 2026-11-12 15:0x（15:00 时窗：A 轨重扫 0 新收 + B 轨第十三轮）**；公告批最新 `2026-11-10`（未刷新）；单分类 5/5 `200`+atom；B 轨 `id_list` 3 次 `200`+atom；B 轨 +4 → 51；作者网 +3 → 57；发信 2 封）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`341` 篇（另候选 **4,558** 篇 + **候选（RSS补充）507** 篇 ⇒ 状态行合计 **5,406**；`SEEN.md` 文件 **5,665 行**；仅存 `SEEN.md` 防重；**本轮 +2 收录**（`2611.14459` / `2611.13560`，2026-11-10 公告批次；当日累计 +5）；`papers.jsonl` **341** 行）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**51 篇**，8 字段 + OpenAlex 单源被引 + Crossref 会议/页码 + 首次收录日；**十三轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**57 人**关系网 + X 只读证据 + 待 follow 清单 **33** 个 + 发信记录 **16 封** + 言论台账 V1–V14（V13/V14 作者不符⇒作废））；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`（与日报草稿同目录，用文件名区分）。


---



## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-12（本地 03:0x–15:2x · 03/06/09/12/15 五轮，r152–r157 及更早）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-13 r161 唤醒时执行）」；含 B 轨第九至十三轮、A 轨补齐 5/5 与各轮发信/作者网增量，勿以本指针替代结论。


- **2026-11-12（本地 18:0x · 18:00 时窗 · 🅱 B 轨第十四轮）** —— **第一百五十八轮**：① **A 轨重扫 5/5 `200`+atom**（6.78/3.34/2.02/3.38/2.65s，串行 ≥3.2s），`totalResults` 与 06/09/12/15 点逐字节同值 ⇒ 批仍 **2026-11-10**；merged 410 / seen 13 / fresh 397；当日 5/5 已满 ⇒ **0 新收**（`raw/2026-11-12-18h-candidates-r158.json`）。② **B 轨 +4 → 55**：SimPO `2405.14734`（**560**，NeurIPS 2024，pp.124198–124235）· Zephyr `2310.16944`（**867**，预印本）· CircuitNet `2208.01040`（**44**⚠️，Sci China Inf Sci 65(12)）· Sutton《The Bitter Lesson》（博客 2019-03-13，无 arXiv/DOI，单列）；③ **作者网 +4 → 61**：Danqi Chen / Yibo Lin（未找到 X）/ Nathan Lambert / Lewis Tunstall；X 已核验 **35**。④ **发信 3 封 `SENT OK 18:06:04 / :07 / :13`**（中文 296 字 / 中文 262 字 / 英文 178 词，发送前已核）；今日累计 **10 封**。⑤ `voice_ready` 维持 2（V15/V16 作者不符作废）；`news_ready` 0。⑥ 交付：日报 **120,019 B**（0 script、标签全配平）+ `daily/index.html`；`PAPERS.md` 55 / `AUTHORS.md` 61；`ARXIV_API.md §9.158`；台账 +3。

- **2026-11-12（本地 21:0x · 21:00 时窗 · 🅱 B 轨第十五轮）** —— **第一百五十九轮**：① **A 轨重扫 15/15 `200`+atom**（`arxiv_fetch.py` 全 `queries.json`），窗口内 **173** 条、最晚 `published 2026-11-10T18:59:54Z` ⇒ 批仍 **2026-11-10**；当日 5/5 已满 ⇒ **0 新收**。② **B 轨 +4 → 59**：ORPO `2403.07691`（**586**，EMNLP 2024）· IPO `2310.12036`（**285**⚠️，按「奠基」收录）· Lost in the Middle `2307.03172`（**3,578**，TACL 2024）· vLLM `2309.06180`（**3,869**，SOSP 2023）；arXiv `id_list` `200`+atom（9,897 B）+ OpenAlex 4/4 `200`。③ **作者网 +4 → 65**：Percy Liang `@percyliang` / James Thorne `@j6mes` / Nelson F. Liu（X bio 空 ⇒ 不登记）/ Woosuk Kwon（未找到 X，`@woosuk_kwon` 3 followers 判非本人）；X 已核验 **37**。④ **发信 2 封 `SENT OK 21:07:24 / :44`**（英文 162 / 159 词，发送前 `wc -w` 已核）；今日累计 **12 封**；Stanford 今日 2 封达上限。⑤ **V17**（Percy Liang 2026-11-11 原推）入账，本期 `voice_ready` 已满 2 条 ⇒ 下期首发；`news_ready` 0 条。⑥ **日报补齐历史缺口**：B 轨表 #52–#59、作者表 #58–#65（18:00 轮只改了标题计数）；`daily/2026-11-12.html` 134,521 B（div 113/113、table 21/21、tr 204/204、td 729/729、details 2/2、0 script）。⑦ 收尾：`research/2026-11-12.md` 21:00 节 + `ARXIV_API.md §9.159` + `发送记录.md` +2 + 心跳。

- **2026-11-13（本地 00:0x · 00:00 时窗 · 早报 3/5 + 🅱 B 轨第十六轮）** —— **第一百六十轮**：① **A 轨 5/5 `200`+atom**，`totalResults` 与 11-12 各轮逐字节同值 ⇒ 批仍 **2026-11-10**；merged 303 / seen 9 / fresh 294；**转正 3 篇强候补**（`2611.13713` Dr. RTL / `2611.13931` TAPCO-G / `2611.14285` LM-SimBench，均 ≤72h），今日 **3/5**。② **B 轨 +4 → 63**：KTO（**951**）· H₂O（**423**⚠️ 按奠基收录）· Self-Instruct（**2,477**）· Switch Transformer（**1,665**）；arXiv `id_list` `200`+atom（10,883 B）+ OpenAlex 4/4 `200`（2026-11-13）。③ **作者网 +4 → 69**：`@yizhongwyz` / `@Muennighoff` / `@BeidiChen` 新核验；Kawin Ethayarajh 主页 `000`、X `404` ⇒ **未找到**；X 已核验 **40**。④ **发信 3 封** `SENT OK 00:06:16/:16/:17`（中文 224 字 / 英文 181 词 / 英文 165 词），今日累计 3 封。⑤ **`voice_ready` 1 条**（V17 Percy Liang 首发，链接修正为 `2120378748457607431`）；`news_ready` 0 条。⑥ 交付：`daily/2026-11-13.html` **28,204 B**（标签全配平、0 script、0 残留 `**`）+ `index.html`；`PAPERS.md` 63 / `AUTHORS.md` 69；`2026-11-13.md` / `ARXIV_API.md §9.160` / `发送记录.md` +3 / `SEEN.md` 3 条转收录 / `papers.jsonl` +3。
- **2026-11-13（本地 03:0x · 03:00 时窗 · 5/5 收口 + 🅱 B 轨第十七轮）** —— **第一百六十一轮**：① **A 轨 5/5 `200`+atom**（1.25/1.40/1.19/1.70/1.28s），`totalResults` 与 00:00 轮**逐字节同值** ⇒ 批仍 **2026-11-10**、无新论文；merged 303 / seen 9 / fresh 294；**候补转正 2 篇**补齐 5/5（`2611.13925` OpenRE-Bench / `2611.13543` Sanity Checks，后者 ≈71h 已在卡内标注）。② **B 轨 +4 → 67**：Chip Placement / AlphaChip 预印本（Nature 版 **704** / 预印本 **274**）· YaRN（**591**）· Speculative Decoding（**354**⚠️ 按奠基收）· GPTQ（**2,195**）；arXiv `id_list` 6 ID 一次 `200`+atom（15,717 B）+ OpenAlex 5/5 `200`。③ **作者网 +4 → 73**：`@Azaliamirh` / `@theemozilla` 新核验；Elias Frantar、Dan Alistarh 未找到 X（不猜）；X 已核验 **42**。④ **发信 1 封** `SENT OK 03:05:47`（Dan Alistarh · GPTQ，英文 187 词），今日累计 4 封。⑤ **`voice_ready` 2 条**（V17 Percy Liang + **V18 Jason Wei 2026-11-12**，推文页 `og:description` 全文核验）；`news_ready` 0。⑥ 交付：`daily/2026-11-13.html` **43,441 B**（标签全配平、0 script、0 残留 `**`、5 卡）+ `index.html`（5/5 + footer）；`PAPERS.md` 67 / `AUTHORS.md` 73；`2026-11-13.md` 03:00 节 / `ARXIV_API.md §9.161` / `发送记录.md` +1 / `SEEN.md` 2 条转收录 / `papers.jsonl` +2。

- **2026-11-13（本地 06:0x · 06:00 时窗 · A 轨复核 + 🅱 B 轨第十八轮）** —— **第一百六十二轮**：① **A 轨 5/5 `200`+atom**（1.21/1.14/1.26/1.15/1.46s），`totalResults` 与 00:00/03:00 轮**逐字节同值** ⇒ 批仍 **2026-11-10**、当日 5/5 已满 ⇒ **0 新收**；merged 303 / seen 9 / fresh 294。② **B 轨 +4 → 71**：OpenROAD DAC 2019（**216**，无 arXiv）· LongRoPE `2402.13753`（**302**⚠️ 按奠基收）· Ramulator IEEE CAL 2015（**799**，无 arXiv）· RowHammer ISCA 2014（ACM **967** / IEEE **528** 双记录，同一篇取高并注明）；OpenAlex **5/5 `200`**（2 精确检索 + 3 DOI 直查）；必读清单仍 **37/37**。③ **作者网 +4 → 77**：Andrew B. Kahng（`abk@ucsd.edu` 主页 `mailto:` 已核；`@AndrewKahng` 无 bio 不登记）· Li Lyna Zhang `@LynaZhang`（三重核验）· Yoongu Kim / Tutu Ajayi（X 无 bio 不登记）；X 已核验 **43**、待 follow 36。④ **发信 1 封** `SENT OK 06:09:06`（Andrew B. Kahng · OpenROAD，英文 **180** 词，发送前 `wc -w` 已核）；今日累计 **5**、累计 **26**。⑤ `voice_ready` **0 新增**（本期已满 2）；`news_ready` 0。⑥ 交付：`daily/2026-11-13.html` **55,848 B**（标签全配平、0 script、0 残留 `**`）+ `index.html`（71 篇/77 人/26 封 + footer）；`PAPERS.md` 71 / `AUTHORS.md` 77；`2026-11-13.md §7` / `ARXIV_API.md §9.162` / `发送记录.md` +1 / AUTHORS 第三节 +1。
- **2026-11-13（本地 09:0x · 09:00 时窗 · A 轨复核 + 🅱 B 轨第十九轮）** —— **第一百六十三轮**：① **A 轨 5/5 `200`+atom**（2.36/2.06/1.47/3.74/1.94s），`totalResults` 与 00:00/03:00/06:00 轮**逐字节同值** ⇒ 批仍 **2026-11-10**、当日 5/5 已满 ⇒ **0 新收**；merged 303 / seen 9 / fresh 294。② **B 轨 +4 → 75**：Megatron-LM `1909.08053`（**3,281**）· DeepSeek-V3 `2412.19437`（**7,939**）· GAIA `2311.12983`（**526**）· A Case for Intelligent RAM（IEEE Micro 1997，**729**，无 arXiv）；arXiv `id_list` 3 ID `200`+atom（GAIA 首次 **`429`**、间隔约 5 分钟重试成功）+ OpenAlex **4/4 `200`**。③ **作者网 +5 → 82**：Thomas Wolf `@Thom_Wolf`（邮箱已核）· Patterson（EECS 现行页邮箱；`@DavePatterson` 判非本人）· Catanzaro `@ctnzr` · Fourrier `@clefourrier` · DeepSeek-AI `@deepseek_ai`；X 已核验 **47**、待 follow **40**。④ **发信 2 封** `SENT OK 09:06:34 / :36`（英文 180 / 190 词），今日累计 **7**、累计 **28**。⑤ `voice_ready` **0 新增**（本期满 2；**V19 = Thomas Wolf 2026-11-07 原推**，下期首发）；`news_ready` 0。⑥ 交付：`daily/2026-11-13.html` **68,922 B**（标签全配平、0 script、0 残留 `**`）+ `index.html`；`PAPERS.md` 75 / `AUTHORS.md` 82；`2026-11-13.md §8` / `ARXIV_API.md §9.163` / `发送记录.md` +2。

- **2026-11-13（本地 12:0x · 12:00 时窗 · A 轨复核「批已刷新」+ 🅱 B 轨第二十轮）** —— **第一百六十四轮**：① A 轨 5/5 `200`+atom（2.44/1.81/1.41/2.53/3.95s），`totalResults` = 125,239/213,092/298,825/212,481/31,015，较 09:00 轮**全部上升** ⇒ **公告批已刷新**（新批首发集中 2026-11-11）；merged 373 / seen 5 / fresh 368；当日 5/5 已收口 ⇒ **0 新收**（不超额），新候选落盘 `raw/2026-11-13-12h-candidates-r164.json`。② B 轨 +4 → 79：BERT `1810.04805`（arXiv **76,688** / NAACL **57,751**，不相加）· CLIP `2103.00020`（**19,245**）· DeepSeek-R1 `2501.12948`（**16,824**，Nature 645:633–638）· DRAMsim3 IEEE CAL 2020（**372**⚠️ 按「方法论常青」收，无 arXiv）；arXiv id_list 3 ID `200`+atom + OpenAlex 5/5 `200`。③ 作者网 +4 → 86：Ankur Srivastava（`ankurs@umd.edu` 已核、已发信）· Bruce Jacob（邮箱为图片 ⇒ 不猜）· Jacob Devlin / Ming-Wei Chang（X 无身份信息 ⇒ 不登记）；新增 handle 0，X 已核验 47。④ 发信 1 封 `SENT OK 12:05:50`（英文 172 词），今日 8 / 累计 29。⑤ `voice_ready` 2 条（V19 Thomas Wolf + V20 Albert Gu，推文页 `og` 核验）；`news_ready` 0。⑥ 交付：`daily/2026-11-13.html` **84,589 B**（标签全配平、0 script、0 残留 `**`）+ `index.html`（79 篇 / 86 人 / 29 封 / 82.5 KB，修掉 1 个多余 `<td>`）；`PAPERS.md` 79 / `AUTHORS.md` 86；`2026-11-13.md §9` / `ARXIV_API.md §9.164` / `发送记录.md` +1。



- **2026-11-13（本地 15:0x · 15:00 时窗 · A 轨复核「批再次刷新」+ 🅱 B 轨第二十一轮）** —— **第一百六十五轮**：① A 轨 5/5 `200`+atom（23.84/12.52/25.81/31.91/5.39s），`totalResults` = 125,322/213,258/299,025/212,730/31,041，较 12:00 轮**全部上升** ⇒ 批持续刷新；merged 391 / seen 2 / fresh **389**（落盘 `raw/2026-11-13-15h-candidates-r165.json`）；当日 5/5 已收口 ⇒ **0 新收**。② B 轨 +4 → 83：QLoRA `2305.14314`（**4,052**，NeurIPS 2023）· T5 `1910.10683`（**13,437**，JMLR 21(140):1–67 与 preprint 并列不相加）· RAG `2005.11401`（**6,188**，仅 arXiv comment 证据、无会场 DOI）· Toolformer `2302.04761`（**3,245**，NeurIPS 2023）；arXiv `id_list` 4 ID `200`+atom（10,900 B）+ OpenAlex 4/4 `200`；必读清单仍 37/37。③ 作者网 +4 → 90：Tim Dettmers `@Tim_Dettmers`（`dettmers@cmu.edu` 取自本人页 `lastname@cmu.edu` 反爬写法，**已发信**）· Patrick Lewis `@PSH_Lewis`（邮箱模板占位 ⇒ 不发信）· Timo Schick `@timo_schick`（无邮箱 ⇒ 不发信）· Colin Raffel（无邮箱 / `@colinraffel` 404 ⇒ 未找到）；X 已核验 **50**、新增 handle 3、待 follow 43。④ 发信 1 封 `SENT OK 15:05:32`（QLoRA，英文 **175** 词，发送前 `wc -w` 已核）；今日 9 / 累计 30。⑤ `voice_ready` **0 新增**（本期满 2）；**V21 = Tim Dettmers 2026-10-18 原推**（`og:title` 核验本人）备下期；**剔除 1 条他人推文**（`og:title` = David Hall `@dlwh`）；`news_ready` 0。⑥ 交付：`daily/2026-11-13.html` **97,571 B**（div 122/122、table 26/26、tr 146/146、td 556/556、th 119/119、details 4/4、0 script、0 残留 `**`、h2 37/37）+ `index.html`（83 篇 / 90 人 / 30 封 / 95.3 KB）；`PAPERS.md` 83 / `AUTHORS.md` 90；`2026-11-13.md §10` / `ARXIV_API.md §9.165` / `发送记录.md` +1。



- **2026-11-13（本地 18:0x · 18:00 时窗 · A 轨复核「索引未再变动」+ 🅱 B 轨第二十二轮）** —— **第一百六十六轮**：① A 轨 5/5 `200`+atom（4.69/1.93/3.64/6.42/2.67s），`totalResults` = 125,322/213,258/299,025/212,730/31,041，与 15:00 轮**逐值相同** ⇒ 记「索引没动」（不等于「无新提交」）；merged 391 / seen 2 / fresh 389；当日 5/5 已收口 ⇒ **0 新收**。② B 轨 +4 → 87：Distilling the Knowledge `1503.02531`（**26,232**）· GQA `2305.13245`（**1,522**，EMNLP 2023）· Orca `2306.02707`（**622**）· Mistral 7B `2310.06825`（**10,625**）；arXiv `id_list` 4 ID `200`+atom（10,007 B）+ OpenAlex 4/4 `200`。③ 作者网 +3 → 93：Geoffrey Hinton `@geoffreyhinton`（主页明文邮箱，**已发信**）· Jeff Dean `@JeffDean`（无邮箱 ⇒ 不发信）· Joshua Ainslie（未找到）；**更正** Arthur Mensch `@arthurmensch`；X 已核验 **53**、待 follow 46。④ 发信 1 封 `SENT OK 18:05:17`（英文 **186** 词），今日 10 / 累计 31。⑤ `voice_ready` **2 条**（V21 Tim Dettmers 2026-10-18 + V22 Jeff Dean 2026-11-06，均 `og` 全文核验）；`news_ready` 0。⑥ 交付：`daily/2026-11-13.html` **117,085 B**（div 128/128、table 32/32、tr 183/183、td 684/684、th 145/145、h2 45/45、details 5/5、footer 1/1、0 script、0 残留 `**`）+ `index.html`（87 篇 / 93 人 / 31 封 / 114.3 KB）；`PAPERS.md` 87 / `AUTHORS.md` 93；`2026-11-13.md §11` / `ARXIV_API.md §9.166` / `发送记录.md` +1。


## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
