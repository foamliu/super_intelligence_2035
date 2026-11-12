# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；06:00 / 18:00 主轮（loop 实际按 0,3,6,9,12,15,18,21 八时窗唤）
已完成:       [r161 · 本地 2026-11-13 03:0x · 03:00 时窗：A 轨补齐 5/5 + **B 轨第十七轮**] ① A 轨 `raw/candidates_r161.py` 单分类 5 查询 **5/5 `200` + `atom+xml`**（cs.CL 125,187 / cs.CV 213,062 / cs.LG 298,685 / cs.AI 212,409 / cs.SE 30,986；1.25/1.40/1.19/1.70/1.28s，串行 ≥3.2s）—— 与 00:00 轮**逐字节同值** ⇒ 批仍 **`2026-11-10`**、本轮无新论文；merged 303 / seen 9 / fresh 294；② **A 轨 +2 → 今日 5/5 收口**：转正 `2611.13925` OpenRE-Bench（共享 run harness + 单适配器 + issue 挖掘管线；651 测试 / 1,396 issue 池）· `2611.13543` Sanity Checks（9 模型 5,408 head；预注册 3 臂 × 8 种子，自指方向 −0.0029 nats Holm p=0.0023；距本轮 ≈71h 已在卡内标注）；③ **B 轨 +4 → 67**：Chip Placement / AlphaChip 预印本 `2004.10746`（OpenAlex：Nature 版 **704** / 预印本 **274**，Nature DOI `10.1038/s41586-021-03544-w`；⚠️ 先试的 `...03517-z` 实为另一篇，已按精确标题检索更正）· YaRN `2309.00071`（**591**）· Speculative Decoding `2211.17192`（**354**⚠️<500，按「奠基」收，ICML 2023 Oral）· GPTQ `2210.17323`（**2,195**，ICLR 2023）；arXiv `id_list` 6 ID 一次 `200`+atom（15,717 B）+ OpenAlex 5/5 `200`（查询日 2026-11-13）；**首次系统补上 serving 侧（解码加速 + 后训练量化）**；必读清单仍 **10/10 组、37/37 条目**；④ **作者网 +4 → 73**：Azalia Mirhoseini `@Azaliamirh`（主页 href + X bio 双核；Wix 站点无 mailto ⇒ 邮箱未找到）· Jeffrey Quesnelle `@theemozilla`（核验链 `github.com/jquesnelle` 外链 + X bio「Nous Research CTO」）· Elias Frantar（`frantar.ai` `000`、组页已无其名、`@EliasFrantar` 无 bio ⇒ 未找到）· Dan Alistarh（`Dan.Alistarh@ist.ac.at` 取自 IST 课题组页 200/127,603 B；`@DanAlistarh` 404）；X 已核验 **42**；⑤ **发信 1 封 `SENT OK 03:05:47`**：Dan Alistarh（GPTQ，英文 **187** 词，`wc` 已核）；今日累计 **4 封**、累计 **25 封**；⑥ **`voice_ready` 2 条**：V17 Percy Liang 2026-11-11（本期首发）+ **V18 Jason Wei 2026-11-12 17:49 UTC**（推文页 200/169,476 B，`og:title`+`og:description` 与 profile `full_text` 一致；36% 更多基准提及）；`news_ready` **0 条**（5 篇均方法/系统/基准类，四问逐条写理由）；⑦ **交付**：`daily/2026-11-13.html` **43,441 B**（div 106/106、table 5/5、tr 36/36、td 163/163、th 25/25、details 2/2、ul 3/3、li 29/29、ol 5/5、**0 script**、**0 残留 `**`**、5 张卡片）+ `daily/index.html`（当日行改 5/5 + footer）；`PAPERS.md` **67** / `AUTHORS.md` **73**；`research/2026-11-13.md` 03:00 节；`ARXIV_API.md §9.161`；`发送记录.md` +1；`SEEN.md` 2 条候选→收录；`papers.jsonl` +2。
当前动作:     ✅ 本轮闭环：A 轨重扫（批未刷新 → 候补转正 2 篇收口 5/5）+ B 轨第十七轮（4 篇 + 4 人 + 1 封信 + V18）+ 日报/index/记忆 + 提交推送。
下一步:       ① 06:00 轮：A 轨重扫（若批刷新则按新批选 3 篇）；② B 轨继续「补充」：EDA 评测基座（OpenROAD/ORFS 一手核验）/ LongRoPE 等长上下文对照 / 存储方向（DRAM 模拟、近存计算）；③ 关注 25 封回信（若退信记「通道失效」不重发）；④ 用户手动 follow 35 个已核验 handle 后改「已follow」；⑤ Zephyr 的 dDPO 蒸馏可作下一轮候选（需先核与在研线的具体落点）。
本轮新增:     A 轨 **+2**（5/5 收口）· B 轨 **+4 经典**（67）· 作者网 **+4 人**（73）· 作者信 **1 封**（累计 25）· **0 follow** · `voice_ready` **2 条**（V17+V18）· `news_ready` 0 条
阻塞:         ① **X 写操作需登录态** ⇒ follow 无法自动执行；② **Sora 官方页仍 403**（本轮未再试）；③ arXiv PDF 未下载（如实记）；④ Azalia Mirhoseini 无公开邮箱、Elias Frantar 无当前主页、Jeffrey Quesnelle 无邮箱、Dan Alistarh 无 X ⇒ 均已如实记「未找到」，不猜；⑤ 搜索工具本轮未用（主页 + X 页自证已足够）。
ERROR_COUNT:  15（本轮 0 新增：arXiv 5/5 + id_list 1/1、OpenAlex 5/5、X profile 8/8 中 2 个「页面存在但无 bio」属预期负证据；`DanAlistarh` 404 / `ShunyuYao12` 单条页 307 均为预期负证据，不计错误）
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


## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
