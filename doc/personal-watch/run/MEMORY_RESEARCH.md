# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；06:00 / 18:00 主轮（loop 实际按 0,3,6,9,12,15,18,21 八时窗唤）
已完成:       [r158 · 本地 2026-11-12 18:0x · 18:00 时窗：A 轨重扫 + **B 轨第十四轮**] ① A 轨单分类 5 查询 **5/5 `200` + `atom+xml`**（cs.CL 125,187 / cs.CV 213,062 / cs.LG 298,685 / cs.AI 212,409 / cs.SE 30,986，与 06/09/12/15 点**逐字节同值** ⇒ 批仍 `2026-11-10`）；merged 410 / seen 13 / fresh 397；当日 5/5 满 ⇒ **0 新收**（`raw/2026-11-12-18h-candidates-r158.json`）。② **B 轨 +4 → 55**：SimPO `2405.14734`（**560**，NeurIPS 2024，DOI `10.52202/079017-3946`，pp.124198–124235）· Zephyr `2310.16944`（**867**，预印本）· CircuitNet `2208.01040`（**44**⚠️<500，Sci China Inf Sci **65(12)**，DOI `10.1007/s11432-022-3571-8`，按判据④「领域标志性」收录）· Sutton《The Bitter Lesson》（**博客**，2019-03-13，无 arXiv/DOI/被引，单列）；arXiv `id_list` 1 次 `200`+atom、OpenAlex 4/4 `200`（查询日 2026-11-12）。③ **作者网 +4 → 61**：Danqi Chen `@danqi_chen`（`danqic@cs.princeton.edu`）/ Yibo Lin（**未找到 X**，`yibolin@pku.edu.cn`）/ Nathan Lambert `@natolambert`（`mail@interconnects.ai`）/ Lewis Tunstall `@_lewtun`（无公开邮箱）；X 已核验 **35**、待 follow **34**。④ **发信 3 封 `SENT OK 18:06:04 / :07 / :13`**：Danqi Chen（中文 **296** 字）+ Yibo Lin（中文 **262** 字）+ Nathan Lambert（英文 **178** 词），**发送前字数已核**；今日累计 **10 封**（七轮，每轮 ≤3；机构 Stanford/ETH/Princeton/PKU/Interconnects 各 1、PI 2 到上限）。⑤ `voice_ready` 维持 **2 条**（2 条拟引用推文经单条页 `og:title` 核为**他人**：`@esonghori2` / `@deanwball` ⇒ V15/V16 作废）；`news_ready` **0 条**。⑥ 交付：`daily/2026-11-12.html` **120,019 B**（div 112/112、table 19/19、tr 171/171、td 588/588、details 2/2、**0 script**）+ `daily/index.html`；`PAPERS.md` **55** / `AUTHORS.md` **61**；`research/2026-11-12.md` 18:00 节；`ARXIV_API.md §9.158`；`发送记录.md` +3。⑦ **上一轮 r157（15:0x）要点原文已存 `daily-memories-research/2026-11-12.md`（§5 滚动，结论不变）**。
当前动作:     ✅ 本轮闭环：A 轨重扫（0 新收）+ B 轨第十四轮（4 篇经典 + 4 人 + 3 封信）+ 日报/index + 记忆 + 提交推送。
下一步:       ① 21:00 轮 A 轨重扫（批刷新则按「新证据优先」替换并写变更说明）；② B 轨继续「补充」：IPO/KTO/ORPO 类偏好优化 / EDA 方向 LLM 评测基座 / 长上下文·KV cache 压缩；③ 用户手动 follow 34 个 handle 后改「已follow」；④ 再试 Sora 官方页（当前 403）；⑤ 发信前**先核字数**（英文 `wc -w` ≤200 / 中文 ≤300 非空白字符）。
本轮新增:     A 轨 **0 篇** · B 轨 **+4 经典**（55）· 作者网 **+4 人**（61）· 作者信 **3 封** · **0 follow** · `voice_ready` **2 条（不变）** · `news_ready` 0 条
阻塞:         ① **X 写操作需登录态** ⇒ follow 无法自动执行；② **Sora 官方页 403**；③ arXiv PDF 仍慢 ⇒ 本轮未下载；④ **搜索工具本轮全引擎失败** ⇒ Yibo Lin 的 X 未能二次检索（记「未找到」，不猜）。
ERROR_COUNT:  14（本轮 +1：`@_lewtun` / `@natolambert` profile JSON 混入**他人推文**，2 条拟引用经单条页 `og:title` 核验后**拦截未采用**，记为 V15/V16 作废）
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
- **2026-11-12（本地 15:0x–15:2x · 15:00 时窗 · A 轨重扫 + 🅱 B 轨第十三轮）** —— **第一百五十七轮**：① **A 轨 0 新收**：单分类 5 查询 **5/5 `200` + `atom+xml`**（cs.CL 125,187 / cs.CV 213,062 / cs.LG 298,685 / cs.AI 212,409 / cs.SE 30,986，与 06/09/12 点**逐字节同值** ⇒ 批仍 `2026-11-10`）；merged 410 / seen 13 / fresh 397；当日额度 5/5 ⇒ 不超额（`raw/2026-11-12-15h-candidates-r157.json`）。② **B 轨 +4 → 51**：DPO `2305.18290`（**3,123**，NeurIPS 2023 pp.53728–53741，DOI `10.52202/075280-2338`）· Mamba-2 `2405.21060`（**1,003**，`comment`=`ICML 2024`）· FlashAttention-2 `2307.08691`（**1,844**，预印本）· Ramulator 2.0 `2308.11030`（**185**⚠️<500，本领域标志性；IEEE CAL 23(1):112–116）；arXiv `id_list` 3 次 `200`+atom（9,704/5,938/9,862 B）、OpenAlex 4/4 `200`。③ **⚠️ 更正**：`2310.16944` 实测 = **Zephyr**（Tunstall et al.），非 DPO；DPO 真实 ID = `2305.18290` ⇒ 已按实测收录、不沿用错误 ID。④ **作者网 +3 → 57**：Rafael Rafailov `@rm_rafailov`（bio `RL at @thinkymachines`；主页 `000`/`403` ⇒ 邮箱未找到）· Archit Sharma `@archit_sharma97`（bio 自证 `co-created: ... DPO`；`architsh@stanford.edu` ← 主页 `mailto:` 200/3,936 B）· Onur Mutlu `@_onurmutlu_`（bio 自证 ETH+CMU/SAFARI；`omutlu@gmail.com` ← `people.inf.ethz.ch/omutlu/` 200/19,850 B）；X 已核验 32、待 follow 33。⑤ **发信 2 封均 `SENT OK 15:03:05`**：Archit Sharma（`2305.18290`，英文 **197 词**）+ Onur Mutlu（`2308.11030`，英文 **177 词**），**发送前均 `wc -w` 已核**；草稿 `mail/drafts/{2305.18290,2308.11030}.md`、正文 `mail/2026-11-12-classic-*.txt`、日志 `/tmp/r157/mail_r157_{dpo,ramulator}.log`；今日累计 7 封。⑥ **`voice_ready` 2 条（不变）**：3 profile `200`，但 2 条拟引用推文经单条页 `og:title` 核为 `@koraykv` / `@Shalev_lif` ⇒ **V13/V14 作废**，不冒充原文；`news_ready` 0 条（四问不过）。⑦ **建议 6 线齐全**（pretrain MFU/Mamba-2 等 loss；vision 显式「无」；harness MFU+长度偏置；data DPO 三元组 schema + DRAM 规格语料；zhulong 奖励三臂 + 模拟器吞吐标定；designflow 保真度三轴）。⑧ 交付：`daily/2026-11-12.html` → **113,453 B**（div 111/111、table 17/17、tr 156/156、td 556/556、details 2/2、**0 script**）+ `daily/index.html`；`PAPERS.md` 51 / `AUTHORS.md` 57；`research/2026-11-12.md` 15:00 节；`ARXIV_API.md §9.157`；`发送记录.md` +2。⑨ 🚫 未发日报邮件、未 follow（0，未假装）、未下载 PDF（如实记）。
- **2026-11-12（本地 12:00–12:1x · 12:00 加轮 · A 轨重扫（cs.SE 恢复）+ 🅱 B 轨第十二轮）** —— **第一百五十六轮**：① **A 轨 0 新收**：5 查询 **5/5 `200` + `atom+xml`**（cs.CL 125,187 / cs.CV 213,062 / cs.LG 298,685 / cs.AI 212,409 / **cs.SE 30,986（上轮 429，本轮恢复）**，与 06:00/09:00 逐字节同值 ⇒ 批仍 2026-11-10）；merged 303 / seen 9 / fresh 294；额度 5/5 ⇒ 不超额（`raw/2026-11-12-pm-candidates-r156.json`）。② **B 轨 +4 → 47**：τ-bench `2406.12045`（1,198）· TD-Gammon（CACM 38(3):58–68，1,680；1994 版 823，OpenAlex 取到完整摘要）· Sora 技术报告（官方页 403 全拒 ⇒ 只写标题级，被引未查）· Kimi K2 `2507.20534`（1,410，v2）；arXiv 3/3、Crossref 1/1、OpenAlex 4/4 全 `200`（查询日 2026-11-12）；**必读清单 37/37 全覆盖**。③ **⚠️ 更正**：`2401.14185` 实测 = TDFNet（cs.SD，被引 3），**非 Kimi** ⇒ 不伪造，改用 `2507.20534`。④ **作者网 +3 → 54**：Bill Peebles `@billpeeb` · Tim Brooks `@_tim_brooks` · Gerald Tesauro（IBM 旧页 308→通用页无 mailto ⇒ 未找到邮箱/X）；X 已核验 29、待 follow 30。⑤ **发信 1 封 SENT OK 12:04:55**：Nisan Stiennon（`2009.01325`，英文）；**⚠️ wc -w 实测 212 词，超 ≤200 规格 12 词（先发后核）⇒ 如实记账 + 纪律新增「发送前必查词数」**；今日累计 5 封。⑥ `voice_ready` 2 条不变（无「两处一致 + 正文完整」新推文）；`news_ready` 0 条（四问不过）。⑦ follow 仍 0（需登录态）；X：直连 000 / 显式代理 200 ⇒ **非 proxy_down**。⑧ 交付：`daily/2026-11-12.html` 97,297 B（div/table/tr/td/details 全配平、0 script）+ `daily/index.html`；`PAPERS.md` 47 / `AUTHORS.md` 54；`SEEN.md`/`papers.jsonl` +0；`research/2026-11-12.md` 12:00 节；`ARXIV_API.md §9.156`。
- **2026-11-12（本地 09:00–09:2x · 09:00 加轮 · A 轨重扫 + 🅱 B 轨第十一轮）** —— **第一百五十五轮**：① **A 轨 0 新增**（当日 5/5 已满，🚫 不超额）：单分类 4/5 `200` + `atom+xml`（125,187 / 213,062 / 298,685 / 212,409，**与 06:00 逐字节同值**），**`cs.SE` 三次 `429`** ⇒ 脚本退出、候选 json **未生成**（本线并发请求自伤，已写 `ARXIV_API §9.155`）。② **B 轨 +4 → 43**：Llama 3 `2407.21783`（23,796 / 预印本 / 405B dense + 128K）· RT-1 `2212.06817`（2,747 / RSS 2023 `10.15607/rss.2023.xix.025`）· Christiano `1706.03741`（1,643 / NeurIPS 2017 `papers.nips.cc/paper/7017`）· Stiennon `2009.01325`（945 / NeurIPS 2020，arXiv `comments`）；arXiv `id_list` **4/4 `200`**（73,338 B）、OpenAlex **4/4 `200`**（查询日 2026-11-12）；必读清单 **34/37**。③ **作者网 +3 → 51**：Jan Leike `@janleike`（`jan@anthropic.com`，主页 mailto + `twitter.com/janleike` 双证）· Paul Christiano `@paulfchristiano`（X 页 bio 自证，无邮箱）· Nisan Stiennon（`nisan+web@stiennon.com`；`x.com/nisanstiennon` **404** ⇒ 未找到 X）；X 已核验 27、待 follow 28。④ **发信 1 封**：Jan Leike **`SENT OK 09:04:13`**，英文 **199 词**；今日累计 4 封；PI 2 封达上限、Anthropic 1 封。⑤ **`voice_ready` 维持 2 条**：Jason Wei 11-11 长贴在 profile `full_text` 与推文页 `og:description` **两处截断** ⇒ V12 未采用（不冒充完整原文）。⑥ **X 可达**（`x.com` `200` / 0.86s、`ShunyuYao12` `200` / 0.76s、出口 `178.249.213.185`），3 个 profile `200`；**0 follow**（未假装）。⑦ **交付**：`daily/2026-11-12.html` **79.6 KB**（div 109/109、table 13/13、tr 111/111、td 400/400、details 2/2、0 script）+ `daily/index.html`；`PAPERS.md` 43 / `AUTHORS.md` 51 / `research/2026-11-12.md` 09:00 节 / `ARXIV_API.md §9.155` / `发送记录.md` +1。


- **2026-11-12（本地 06:00–06:2x · 06:00 时窗 · A 轨扫描 + 🅱 B 轨第十轮）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-12 r158）」；要点：A 轨重扫 5/5（0 新收）、B 轨 +4 → 39（SWE-agent / Tree of Thoughts / Llama 2 / LLaVA-1.5）、作者网 +1 → 48（Kilian Lieret）、发信 1 封（Karl Pertsch，PI 当日 2 封到上限）、首现「profile timeline 混入他人推文」问题。以归档原文为准。

- **2026-11-12（本地 03:0x–03:1x · 03:00 时窗 · A 轨补齐 5/5 + 🅱 B 轨第九轮）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-12 r158）」；要点：A 轨 2 篇（`2611.14459` 文本编码 / `2611.13560` GRPO 稠密奖励）、B 轨 +4 → 35（GLM-4 / MiniMax-01 / RT-2 / Octo）、作者网 +4 → 47、发信 1 封（Pete Florence）。以归档原文为准，勿以本指针替代结论。
- **2026-11-11（本地 21:00–21:1x · 21:00 时窗 · 🅱 B 轨第七轮）** —— **第一百五十一轮**：① **B 轨 +4 → 27 篇**：AlphaGo（Nature 529(7587):484–489，Crossref 200；OpenAlex **16,697**）· AlphaGo Zero（Nature 550(7676):354–359；**9,661**）· Gemini `2312.11805` v5（arXiv API 200 + atom+xml；**10,518**）· OpenVLA `2406.09246` v3（arXiv API 200；**2,913**）；Nature 摘要 `dc.description` 2/2 200。② **必读清单 10/10 组全覆盖**（第 3/8/10 组一次补齐；剩余子项 AlphaFold / AlphaStar / Kimi / GLM-4 / MiniMax-01 / RT-2·π0·Octo / SORA）。③ 作者网 **+5 → 39**（David Silver / Oriol Vinyals `@OriolVinyalsML` / Sergey Levine `@svlevine` / Chelsea Finn `@chelseabfinn` / Moo Jin Kim `@moo_jin_kim`）；X 核验 13→17。④ **1 封 SENT OK 21:04:26**（Moo Jin Kim，英文 195 词，`moojink@cs.stanford.edu` 主页防爬还原；问双塔融合 vs 数据多样性、逐维分桶 vs 文本序列化）；今日累计 **9 封**。⑤ follow 仍 **0**（需登录态）；待 follow 13→17。⑥ voice_ready 仍 **2 条**（V6 Chelsea 10-24 完整 ⇒ 下期候选；V7 Sergey 11-09 截断 ⇒ 未采用；V8 Oriol 08-05 ⇒ 降级）。⑦ **21:00 建议 6 线齐全**（pretrain 显式「无新增」+ 理由；vision 2×2 双塔；harness 3 列 + 双基线；data 多样性三臂；zhulong search_budget + 自举先测 checker；designflow 自对弈 30–50 题）。⑧ 交付：`daily/2026-11-11.html` 137,988 → **155,562 B**（div 114/114、table 18/18、tr 183/183、td 815/815、details 3/3、**0 script**）+ `daily/index.html` + `PAPERS.md` 27 + `AUTHORS.md` 39 + `x/*.json` 18 文件 / 58,529 B。⑨ 🚫 未发日报邮件。
- **2026-11-12（本地 00:0x–00:2x · 临时唤醒 · A 轨早报 + 🅱 B 轨第八轮）** —— **第一百五十二轮**：① **A 轨 3 篇（3/5）**：SLIC `2611.13452`（4B 本地模型强化微调做模拟电路闭环优化；41 拓扑开源基准；摘要称 8 轮分布内 Pass@1 87.1%、比 763B DeepSeek-V4.1-Flash Think 高 48.5pp、留出拓扑 72.6%、TSMC 65nm PDK 49.9%、32 轮 83.2%）· Plumbline `2611.13393`（训练正确性验证；3 框架 5 模型 61 问题 / 32 静默 / 42 已修或上报 / 8 首提 / 7 类模式）· ACF adherence `2611.13709`（把 AGENTS.md 指令操作化成脚本、逐条测合规；结论「多数遵循但两极分化」，摘要无具体数字 ⇒ 不编）。② **取数**：6 检索式 6/6 `200`+`application/atom+xml`（106,222 / 102,462 / 104,967 / 106,719 / 102,495 / 103,019 B；串行 ≥3.2s）；公告批最新 `2026-11-10`；3 篇 published 距唤醒 38.2h / 39.9h / 32.1h。③ **B 轨 +4 → 31**：AlphaFold（Nature 596:583–589，OpenAlex 45,663）· AlphaStar（Nature 575:350–354，3,799）· Kimi k1.5（arXiv 2501.12599，1,436）· π0（arXiv 2410.24164 / RSS 2025，3,214）；Nature `dc.description` 2/2 200、arXiv id_list 200+atom、OpenAlex 4/4 200（查询日 2026-11-12）。④ **作者网 +4 → 43**：John Jumper（无公开邮箱；`@JohnJumper` 19 followers 无 bio ⇒ 身份不可证，拒绝登记）· Igor Babuschkin `@ibab`（bio CEO River AI / 前 xAI）· Danny Driess `@DannyDriess`（主页防爬 `danny.driess@gmail.com`；X bio Research Scientist @physical_int）· Kimi Team `@Kimi_Moonshot`（官方）；X 17→20。⑤ **发信 1 封 SENT OK 00:07:41**：Danny Driess（π0；英文 191 词；问低数据下 flow matching vs 离散动作、异构 tool call 的 chunk 边界、冻结主干 vs 全参）；草稿 `mail/drafts/2410.24164.md`、正文 `mail/2026-11-12-classic-2410.24164.txt`、日志 `/tmp/mail_send_r152_classic_2410.log`、台账已写。⑥ **voice_ready 2 条**：Sutton V4（2026-11-07「Brute force computation is not enough for intelligence…IMHO」）· Chelsea Finn V6（2026-10-24 生成式价值分类器）；V3/V5/V7 仍因正文截断不采用。⑦ **news_ready 0 条**（3 篇均借鉴、四问不过；已写理由）。⑧ **交付**：`daily/2026-11-12.html` 36,739 B（div/table/tr/td/details 全配平、0 script）+ `daily/index.html` 当日行 + footer；`PAPERS.md` 31 / `AUTHORS.md` 43；`SEEN.md`+3、`papers.jsonl`+3、`research/2026-11-12.md`。⑨ ⚠️ PDF 3 篇未下载完成（arXiv 慢；仅 `2611.13452` 见 `%PDF-`）⇒ 日报如实记「未完成」。




- **2026-11-11（本地 15:00–15:2x · 15:00 时窗 · 🅱 B 轨第五轮）** —— **第一百四十九轮**：① **B 轨 +4 → 19 篇**，补第四轮显式留空的 **vision 空档** 与必读清单缺口：ResNet `1512.03385`（OpenAlex **CVPR 版 243,173** / arXiv 版 12,953；CVPR 2016 pp.770–778）· seq2seq `1409.3215`（**18,379**；NIPS 2014 索引命中、页码留空）· Dyna 1991（**871**，SIGART 2(4)160–163）/ 前身 1990（**1,383**，pp.216–224）· LLaVA `2304.08485`（**3,189** NeurIPS 版 / 2,820 arXiv 版；`comments`=NeurIPS 2023 Oral；pp.34892–34916）。证据：arXiv abs **3/3 200**（42,963 / 43,176 / 42,352 B）、Crossref **5/5 200**、OpenAlex **5/5 200**。② **作者网 +5 → 28 人**：Kaiming He（`kaiming@mit.edu` 主页 200；未找到 X）· Ilya Sutskever（`@ilyasut` 200，name/bio 双核；无公开邮箱）· Richard S. Sutton（`@RichardSSutton` 200，bio 含 UAlberta/amii/Turing；主页仅 amii 行政信箱 ⇒ 不发）· Haotian Liu（`@imhaotian`；`liuhaotian.cn@gmail.com`）· Chunyuan Li（`@ChunyuanLi`；`lichunyuan24@gmail.com`，同合作圈本轮不发）。③ **发信 2 封 `SENT OK`**：Kaiming He **15:05:38**（中文 **196** 字）/ Haotian Liu **15:05:43**（中文 **215** 字）；草稿 `drafts/1512.03385.md` / `drafts/2304.08485.md` 先入仓，台账已追加。④ **follow 仍 0**（需登录态，未假装），待 follow 清单 **6 → 10**。⑤ **`voice_ready` 仍 2 条**；Sutton 11-07 原文本轮已核验（`2119142310894334262`）但受「每期 ≤2」⇒ 台账 V4、下期用。⑥ **交付**：`daily/2026-11-11.html` → **120,421 B**（+15:00 增量建议 6 线表、补充变更说明 6 行、附录 A-2 第 10–12 行；**0 `<script>`**）；`daily/index.html` 同步。











- **2026-11-11（本地 11:3x–13:2x · 首轮 / 第二轮 / 午间 / 晚报四轮）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-12 r152 唤醒时执行）」；要点（B 轨首轮 4 篇经典与 8 人作者网、第二轮 4 篇与 Haoxing Ren 信、午间 A 轨 5/5、晚报 B 轨第四轮与 X 解封）保持原记录，勿以本指针替代结论。

- **2026-11-12（本地 18:0x · 18:00 时窗 · 🅱 B 轨第十四轮）** —— **第一百五十八轮**：① **A 轨重扫 5/5 `200`+atom**（6.78/3.34/2.02/3.38/2.65s，串行 ≥3.2s），`totalResults` 与 06/09/12/15 点逐字节同值 ⇒ 批仍 **2026-11-10**；merged 410 / seen 13 / fresh 397；当日 5/5 已满 ⇒ **0 新收**（`raw/2026-11-12-18h-candidates-r158.json`）。② **B 轨 +4 → 55**：SimPO `2405.14734`（**560**，NeurIPS 2024，pp.124198–124235）· Zephyr `2310.16944`（**867**，预印本）· CircuitNet `2208.01040`（**44**⚠️，Sci China Inf Sci 65(12)）· Sutton《The Bitter Lesson》（博客 2019-03-13，无 arXiv/DOI，单列）；③ **作者网 +4 → 61**：Danqi Chen / Yibo Lin（未找到 X）/ Nathan Lambert / Lewis Tunstall；X 已核验 **35**。④ **发信 3 封 `SENT OK 18:06:04 / :07 / :13`**（中文 296 字 / 中文 262 字 / 英文 178 词，发送前已核）；今日累计 **10 封**。⑤ `voice_ready` 维持 2（V15/V16 作者不符作废）；`news_ready` 0。⑥ 交付：日报 **120,019 B**（0 script、标签全配平）+ `daily/index.html`；`PAPERS.md` 55 / `AUTHORS.md` 61；`ARXIV_API.md §9.158`；台账 +3。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
