# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r190 · 本地 2026-11-16 21:0x · 21:00 时窗：A 轨 0 新收（今日 5/5 已满）+ B 轨第四十六轮 +4 → 182 + 作者网 +3 → 170（X 已核验 96）+ 0 封信（今日 12 封硬上限）+ voice_ready 1（V30）] ① A 轨 `cat:cs.CL` 20-entry **`200` + atom（50,794 B / 20 entry）**，`published` 上界仍 **`2026-11-13T18:45:49Z`**（与 18:00 一致，周末不公告）；今日配额 5/5 ⇒ 0 新收。② B 轨 **+4 → 182（第四十六轮）**：LIMA `2305.11206`（**904**，NeurIPS 2023，会场取 OpenAlex pp. 55006–55021）/ The False Promise `2305.15717`（**304**，ICLR 2024 spotlight，OpenReview `venue`；&lt;500 按「方法论常青」收）/ Muon is Scalable `2502.16982`（**622**，预印本）/ FlashAttention-3 `2407.08608`（**418**，NeurIPS 2024，OpenAlex；&lt;500 按「开创范式 + 方法论常青」收）。证据：atom `id_list` **`200`（11,916 B / 4 entry）+ abs 4/4 `200`（43,595 / 42,562 / 45,291 / 43,000 B）+ OpenAlex 4/4 `200` + OpenReview 1/1 `200`（9,494 B）+ PDF 4/4 `200` + `application/pdf`（499,719 / 1,051,380 / 2,077,505 / 1,096,663 B，均 <5MB）**；`pdftotext` 核到 `1,000 carefully curated` / `750,000 tokens` / `43%` / `88% meet the prompt requirements`；`∼70%` / `mimicking ChatGPT’s style but not its factuality` / `model imitation is a false promise`；`adding weight decay` / `per-parameter update scale` / `∼ 2× computational efficiency` / `5.7T tokens` / `ZeRO-1`；`740 TFLOPs/s (75% utilization)` / `1.2 PFLOPs/s` / `2.6× lower numerical error` / `35% utilization on the H100`。③ 落选如实记：Zero Bubble `2401.10241` 实测仅 **90** 被引 ⇒ 不收（不凑数）。④ 作者网 **+3 → 170（编号 166–168）**：Xuezhe Ma（USC ISI；`xuezhema@usc.edu` USC Viterbi 目录页明文；X `@MaxMa1987` 双源核）/ Pengfei Liu 刘鹏飞（SJTU / GAIR；`pengfei@sjtu.edu.cn` 教师页明文；X 未找到）/ Eric Wallace（OpenAI；仅 CV 内 `ericwallace@berkeley.edu` 旧域 ⇒ 不建议直发；X `@Eric_Wallace_` 双源核）；X 已核验 **94 → 96**。⑤ 发信 **0**：今日 12 封（#56–#67）= 每日硬上限；已备下轮草稿 `mail/drafts/2305.11206-ma.md` / `-liu.md`（均标「未发送」），按「同论文 ≤1」下轮只发其一。⑥ **回信率 0 / 67**，0 封到期（最早 2026-11-25）。⑦ `voice_ready` **1（V30）** = Eric Wallace 2026-11-04 原推（前沿算力投入开源漏洞发现与修补 / Linux 内核案例；单推页 `og:title`+`og:description` 双源，**正文在摘要处截断 ⇒ 引用须标节选**）；`news_ready` **0**。⑧ 交付：`daily/2026-11-16.html` **102,580 B / 100.2 KB** + `index.html` 行与 footer；`PAPERS.md` 182 / `AUTHORS.md` 170；`research/2026-11-16.md` §13；`发送记录.md` 21:0x 回信率段；6 线建议 6 条（vision / designflow 明写「无」）。⑨ ⚠️ **同名站点假阳性 2 个**：`chunting.me`（他人博客 `葉峻榳醫師`）/ `jayshah.dev`（6sense 工程师）⇒ 均丢弃、未建档（「站点可达 ≠ 人正确」）。
当前动作:     ✅ 本轮闭环：A 轨守配额 + B 轨 182 + 作者网 170 + 0 封信（额度满，守纪律）+ voice_ready 1 + 日报 / index / 记忆 + 提交推送。
下一步:       ① 00:00 时窗（11-17）A 轨重新开配额，按 ≤72h 评估候选（公告批 `2026-11-13T18:45:49Z` 起）；② B 轨候选：HBM / JEDEC 一手（连续多轮未命中）/ 训练 spike 侧（QK-clip）/ 长上下文调度（Zero Bubble `2401.10241` 已实测 90 被引 ⇒ 暂留候选）；③ 发信：**#167 Pengfei Liu（中文，教师页明文）优先**，#166 Xuezhe Ma 备选（同论文只发一封）· #165 Guangxuan Xiao · #161 Ze Liu；#164 Yang You 域名复核前不发；④ 复抓 `@Guangxuan_Xiao` 补 X 核验；⑤ 待用户手动 follow 已核验 96 条 handle；⑥ 11-25 起若仍 0 回，按六层归因并报运维。
本轮新增:     A 轨 0（今日 5/5 配额满）· B 轨 +4（182）· 作者网 +3（170）· 作者信 0（累计 67）· voice_ready 1 · news_ready 0 · 回信率 0/67
阻塞:         ① X 写操作需登录态 ⇒ follow 无法自动执行；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到（最需运维介入）；③ `WATCH_RESEARCH_TASK.md` 已 **44,052 B > 40 KB 红线**，但该文件标注「agent 只读」⇒ 需 supervisor 决定是否授权滚动归档；④ `x.com/Guangxuan_Xiao` 上次连续 2 次 `000`，待复抓。
ERROR_COUNT:  96（本轮 +0：所有端点均 `200`；仅 Muon PDF `pdftotext` 1 条 `Invalid blend mode` 警告，非网络错误）
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
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**178 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**四十五轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**167 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V29）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`（与日报草稿同目录，用文件名区分；无 arXiv 的用 `<会议>-<年份>.md`）。 ｜ 现状（2026-11-16 18:0x）：PAPERS **178** / AUTHORS **167**（X 已核验 **94**）/ 作者信 **67**（回信率 **0/67**）。




---



## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-16（本地 21:0x · 21:00 时窗 · A 轨 0 新收（配额满，公告批未前进）+ 🅱 B 轨第四十六轮 +4 → 182 + 作者网 +3 → 170 + 0 封信（今日 12 封硬上限）+ voice_ready 1（V30））** —— **第一百九十轮**：① A 轨 `cat:cs.CL` 20-entry **`200` + atom（50,794 B / 20 entry）**，`published` 上界仍 **`2026-11-13T18:45:49Z`**（与 18:00 一致，周末不公告）；今日 5/5 ⇒ 0 新收。② B 轨 +4 → 182：LIMA `2305.11206`（**904**，NeurIPS 2023）/ False Promise `2305.15717`（**304**，ICLR 2024 spotlight，**&lt;500 按方法论常青**）/ Muon is Scalable `2502.16982`（**622**，预印本）/ FlashAttention-3 `2407.08608`（**418**，NeurIPS 2024，**&lt;500 按开创范式**）；atom `id_list` `200`（11,916 B / 4 entry）+ abs 4/4 `200` + OpenAlex 4/4 `200` + OpenReview 1/1 `200` + PDF 4/4 `200`（均 <5MB）；`pdftotext` 核到 `1,000 carefully curated` / `750,000 tokens` / `43%` / `88% meet the prompt requirements`、`∼70%` / `mimicking ChatGPT’s style but not its factuality`、`adding weight decay` / `per-parameter update scale` / `∼ 2× computational efficiency` / `5.7T tokens`、`740 TFLOPs/s (75% utilization)` / `1.2 PFLOPs/s` / `2.6× lower numerical error`。③ 落选如实记：Zero Bubble `2401.10241` 仅 **90** 被引 ⇒ 不收（不凑数）。④ 作者网 +3 → 170：Xuezhe Ma（USC ISI；`xuezhema@usc.edu` 目录页明文；X `@MaxMa1987` 双源）/ Pengfei Liu（SJTU；`pengfei@sjtu.edu.cn` 教师页明文；X 未找到）/ Eric Wallace（OpenAI；CV 内仅旧域 ⇒ 不建议直发；X `@Eric_Wallace_` 双源）；X 已核验 96。⑤ 发信 0：今日 12 封 = 硬上限；草稿 `drafts/2305.11206-{ma,liu}.md` 已入仓并标「未发送」，下轮按「同论文 ≤1」只发其一。⑥ 回信率 **0/67**，0 封到期（最早 2026-11-25）。⑦ `voice_ready` **1（V30）** = Eric Wallace 2026-11-04 原推（前沿算力投入开源漏洞发现与修补；单推页双源，**正文摘要处截断 ⇒ 引用须标节选**）；`news_ready` 0。⑧ 交付：`daily/2026-11-16.html` **102,580 B** + `index.html`；PAPERS 182 / AUTHORS 170；`research/2026-11-16.md` §13；`发送记录.md` 21:0x 回信率段；6 线建议 6 条（vision / designflow 明写「无」）。⑨ ⚠️ 同名站点假阳性 2 个（`chunting.me` 他人博客 / `jayshah.dev` 6sense 工程师）⇒ 均丢弃未建档。

- **2026-11-16（本地 18:0x · 18:00 时窗 · A 轨 0 新收（配额满，公告批未前进）+ 🅱 B 轨第四十五轮 +4 → 178 + 作者网 +2 → 167 + 0 封信（今日 12 封硬上限）+ voice_ready 1）** —— **第一百八十九轮**：① A 轨 `cat:cs.CL` 20-entry `200` + atom（50,794 B / 20 entry），`published` 上界仍 `2026-11-13T18:45:49Z`（周末不公告）；今日 5/5 ⇒ 0 新收。⚠️ `http://export.arxiv.org/api/query` 本轮返回 **`301` / 0 B** ⇒ 改 `https://` 后 `200` + atom，后续固定 https。② B 轨 +4 → 178：LAMB `1904.00962`（932，ICLR 2020）/ LayerNorm `1607.06450`（12,853，预印本，无 comment）/ StreamingLLM `2309.17453`（1,248，ICLR 2024）/ Nucleus Sampling `1904.09751`（2,832，ICLR 2020）；abs 4/4 + atom 4/4 + OpenAlex 4/4 + PDF 4/4 全 `200`，`pdftotext` 核 `76 minutes` / `batch size of 32768` / `91.460` / `100.2% efficiency` / `single training case` / `adaptive bias and gain` / `up to 4 million tokens` / `22.2× speedup` / `Beam Search (size 32) leads to degenerate repetition`。StreamingLLM PDF **16.95MB ≥5MB** ⇒ 只在 `/tmp` 核、不入 git。③ 作者网 +2 → 167（编号 164–165）：Yang You（NUS；主页 `yangyou (at) nus (dot) edu` 域名待复核；X `@YangYou1991` 双源核 ⇒ 待跟踪）/ Guangxuan Xiao（MIT HAN Lab；`xiaoguangxuan@gmail.com` 主页 mailto；X `@Guangxuan_Xiao` 仅主页 href 单源 + `x.com` 两次 `000` ⇒ 未核验不计数）；X 已核验 94。④ 发信 0：今日 12 封（#56–#67）= 每日硬上限；待发 #164（域名复核后）/ #165 / #161 / #162。⑤ 回信率 **0/67**，0 封到期（最早 2026-11-25）；新增可审计变量 = 邮箱域名与机构属地不一致（`nus (dot) edu` vs 常见 `nus.edu.sg`）⇒ 复核前不发。⑥ `voice_ready` **1**（V29 = Yang You 2026-11-04 原推：The Trinity / harness 能力驱动演化 / `+26 points across 18 unseen benchmarks`；单推页 `og:title`+`og:description` 双源一致）；`news_ready` 0。⑦ 交付：`daily/2026-11-16.html` **90,002 B / 87.9 KB**（div 126/126、table 24/24、tr 148/148、td 453/453、th 101/101、details 4/4、h2 22/22、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html` 行与 footer；PAPERS 178 / AUTHORS 167；`research/2026-11-16.md` §12；`发送记录.md` 18:0x 回信率段；6 线建议 6 条（data / designflow 明写「无」）。

- **2026-11-16（本地 15:0x · 15:00 时窗 · A 轨 0 新收（配额满，公告批继续前进）+ 🅱 B 轨第四十四轮 +4 → 174 + 作者网 +3 → 165 + 0 封信（今日 12 封硬上限））** —— **第一百八十八轮**：① A 轨 `cat:cs.CL` 20-entry `200`+atom（**50,794 B / 20 entry**），`published` 上界 **`2026-11-13T18:45:49Z`**（较 12:00 的 `08:40:07Z` 继续前进）；今日 5/5 ⇒ 0 新收。② B 轨 +4 → 174：Swin `2103.14030`（38,712，ICCV 2021）/ SpeechT5 `2110.07205`（141，ACL 2022，<500 按「开创统一模态范式」收）/ GPipe `1811.06965`（1,280，NeurIPS 2019）/ Scaling Data-Constrained `2305.16264`（254，NeurIPS 2023，<500 按「方法论常青」收）；abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200`，`pdftotext` 核数字。⚠️ 先验 ID `2010.00718` 实为 `When to Impute?` ⇒ SpeechT5 真 ID 已纠正为 `2110.07205`。③ 作者网 +3 → 165（Ze Liu 刘泽 / Junyi Ao / Long Zhou；X 已核验 93）。④ 发信 0：今日 12 封（#56–#67）= 每日硬上限 ⇒ 只做收录与建档；待发 #161 / #162（中文）。⑤ 回信率 0/67，0 封到期（最早 2026-11-25）。⑥ voice/news 均 0。⑦ 交付：`daily/2026-11-16.html` 78,849 B / 77.0 KB + `index.html`；PAPERS 174 / AUTHORS 165；`research/2026-11-16.md` §11；`发送记录.md` 15:0x 回信率段；`replies/README.md`。⑧ 发现 `WATCH_RESEARCH_TASK.md` 44,052 B 超 40 KB 红线，但标注 agent 只读 ⇒ 已记入阻塞，待 supervisor 决定。
- **2026-11-16（本地 12:0x · 12:00 时窗 · A 轨 0 新收（配额满，公告批首次前进）+ 🅱 B 轨第四十三轮 +4 → 170 + 第 66/67 封信（中文 RTLLM / 英文 Gemini 1.5））** —— **第一百八十七轮**：① A 轨 `cat:cs.CL` 20-entry `200`+atom（47,638 B / 20 entry），`published` 上界 `2026-11-13T08:40:07Z` ⇒ 连续 16 个时窗未前进后**首次前进**；今日 5/5 ⇒ 0 新收。② B 轨 +4 → 170：Gemini 1.5 `2403.05530`（4,633）/ RTLLM `2308.05345`（301，ASP-DAC 2024）/ VerilogEval `2309.07544`（359，ICCAD 2023 Invited）/ PIM Benchmarking `2105.03814`（285，IEEE Access 2022）；abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200`，`pdftotext` 核数字。⚠️ 先验 ID `2309.00867`/`2309.04781` 命中无关论文 ⇒ 已纠正。③ 作者网 +4 → 162（谢知遥 / Machel Reid / Juan Gómez-Luna / Onur Mutlu；X 已核验 92）。④ 发信 2 封：`SENT OK 12:05:36`（#66 中文 186 汉字）· `12:05:43`（#67 英文 187 词），落款两行、查重 0 命中，今日 12 封 = 硬上限。⑤ 回信率 0/67，0 封到期。⑥ voice/news 均 0。
- **2026-11-16（本地 09:0x · 09:00 时窗 · A 轨复核「批仍未前进」+ 🅱 B 轨第四十二轮 +5 + 第 63/64/65 封信（日文 / 中文 / 中文））** —— **第一百八十六轮**：① A 轨 `cat:cs.CL` 20-entry `200`+atom（**50,083 B / 20 entry**，四轮逐值一致），`published` 上界 `2026-11-12T18:59:52Z` ⇒ **连续第 16 个时窗未前进**；今日 5/5 ⇒ 0 新收。② B 轨 **+5 → 166**：GShard `2006.16668`（1,633，2020 预印本）· Mixtral `2401.04088`（4,372）· Self-RAG `2310.11511`（1,091，**会场未核不写 ICLR**）· LongBench `2308.14508`（1,169，ACL 2024）· Cambrian-1 `2406.16860`（514，NeurIPS 2024 Oral）；`id_list` 连续 `429`×3 ⇒ 改走 abs 页 5/5 `200`（43,816 / 46,189 / 42,906 / 45,172 / 45,385 B；作者数 9/26/5/13/14）；OpenAlex 5/5 `200`；PDF 5/5 `200`（1,747,868 / 2,475,990 / 1,405,127 / 11,630,690 / 6,427,380 B；35/13/30/19/51 页）`pdftotext` 全通过，核到 `600 billion`/`2048 TPU v3`、`47B`/`13B active`、`ISREL`/`ISSUP`/`ISUSE`、`4,750 test instances`/`13,386 characters`、`Spatial Vision Aggregator`/`576`/`36 tokens`/`OCR (27.6%)`。⚠️ LongBench 11.6 MB、Cambrian-1 6.4 MB >5 MB ⇒ 仅本地 gitignore。③ 作者网 **+3 → 158**（#154 Asai：`aasai@andrew.cmu.edu` 为主页 `mailto:` **百分号编码**解码所得 + `@AkariAsai` 双源；#155 白雨石：`bys22@mails.tsinghua.edu.cn` 主页明文 + `@realYushiBai` 双源；#156 童晟邦：`tsb@berkeley.edu` 主页明文 + `@TongPetersb` 双源）；X 已核验 **89**。④ 发信 **3 封**：`SENT OK 09:04:43`（#63 日文 **300 字非空白**）· `09:04:50`（#64 中文 **215 汉字 / 343 非空白**）· `09:04:55`（#65 中文 **207 汉字 / 347 非空白**）；落款严格两行、其后无任何行；正文不含项目名；查重三 ID 与三地址 **0 命中**；与同轮另两封开头句 / 问题句式 / 技术细节零共用；本时窗 3 封 = 上限，今日 10 封 ≤12；**母语判定按姓名族属优先（#63 日文、#64/#65 中文），未因海外机构 / berkeley.edu / gmail 判英文**。⑤ **回信率 0 / 65**，**0 封到期**（最早 2026-11-25）；新增分层变量 = 日文母语收件人 · 海外 vs 国内华人。⑥ `voice_ready` 0（只核 handle、未抓 timeline）；`news_ready` 0（五篇均经典方法 / 技术报告，无事件点）。⑦ 交付：`daily/2026-11-16.html` **58,075 B / 56.7 KB**（table 10/10、h2 9/9、h3 5/5、ol 5/5、li 20/20、details 2/2、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html`（当日行 5/5，追加 03:00/06:00/09:00 段；footer 166 / 158 / 65 / 0/65）；`PAPERS.md` **166**（#162–#166）/ `AUTHORS.md` **158**（#154–#156）；`research/2026-11-16.md` §9；`发送记录.md` +3 行 + 跟踪表 +3 + 09:0x 回信率段；6 线建议 **6 条增量**。
- **2026-11-16（本地 06:0x · 06:00 时窗，r188-b）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-16.md`「[06:00] wake」；含 B 轨第四十一轮 +4（Gorilla / Let's Verify / Qwen2.5-VL / DeepSeek-V2）与 #60–#62 三封信，勿以本指针替代结论。
- **2026-11-16（本地 03:0x · 03:00 时窗，r188-a）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-16.md`「[03:00] wake」；含 A 轨补满 5/5（NOPO / Parsed-Plausible-Wrong）与 B 轨第四十轮 +4，勿以本指针替代结论。
- **2026-11-16（本地 00:0x · 00:00 时窗 · A 轨 3/5 ＋ 🅱 B 轨第三十九轮 +4 ＋ 第 56–57 封信（英文 / 法文问候+英文）＋ voice_ready 0）** —— **第一百八十三轮**：① A 轨 `cat:cs.CL` **`200` + atom**（259,108 B / 100 entry；20-entry 复核 50,083 B），`published` 上界 `2026-11-12T18:59:52Z`；`cat:cs.LG` `200` + atom（上界 `18:59:54Z`）⇒ **第 13 个时窗未前进**（周末不公告）⇒ 按例外取 3 篇未消费候选：**MAPE `2611.17068`**（+12% 绝对准确率 / 35% 服务成本 / 原文可回查 + 意图组合；代码 github.com/ash-ding/MAPE）· **Pretraining Data Statistics `2611.16882`**（163M 三阶段 词频→位置→正确 / Zipf→均匀加速 / OLMo-2 32B 复现；≈73.2h 略超 72h 已标注）· **LazyWeights `2611.17108`**（DRAM 按需解码 / 体积 −5.7–31.4% / Orin −36% 延迟 −38% 能耗 / 3.89 bit 6.6×）；`id_list` `200` + atom（8,148 B / 3 entry）、abs 3/3 `200`、PDF 3/3 `200` + `pdftotext`。② B 轨 **+4 → 153**：Longformer `2004.05150`（6,470）· Flamingo `2204.14198`（2,333，NeurIPS 2022）· RoBERTa `1907.11692`（33,672）· DINO `2104.14294`（7,104，ICCV 2021 源取 OpenAlex）；`id_list` `200` + atom（10,643 B / 4 entry，作者 3/27/10/7）、OpenAlex 4/4 `200`、PDF 4/4 `200`（后两篇 >5MB 仅本地），核到 512 窗口 / dilation×14 / 位置编码复制 4,096、80B / 43M / 0-init tanh gating −4.2%、160GB / 8K / 500K、78.3% k-NN。③ 作者网 **+3 → 149**：Iz Beltagy（主页明文 mailto + `@i_beltagy` 双源 ⇒ 已发信）· Jean-Baptiste Alayrac（主页明文 mailto ⇒ 已发信；X 未找到）· Mathilde Caron（仅 2021 年 PDF 旧域地址 ⇒ 只建档）；X 已核验 **83**。④ 发信 **2 封**：`SENT OK 00:03:22`（英文 194 词）· `00:03:28`（法文问候 + 英文 179 词），落款两行 `Best regards,` / `Yang Liu`；发送前查重 0 命中；今日 2 / 累计 **57**。⑤ 回信率 **0/57**，0 封到期；新增分层变量 = 是否仍在原作者团队。⑥ `voice_ready` **0**（三条候选经单推页 `og:title` 核为 `@lmsysorg` / `@simran_s_arora` / `@mercor` 转推 ⇒ 丢弃；TerminalBench 已用于 11-15；其余 >30 天）；`news_ready` **0**。⑦ 交付：`daily/2026-11-16.html` **24,343 B**（div 71/71、table 2/2、tr 15/15、td 33/33、th 5/5、h2 4/4、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html` 新行 + footer；`PAPERS.md` 153 / `AUTHORS.md` 149；`research/2026-11-16.md` §0–§7；`SEEN.md` +3；`papers.jsonl` +3；`发送记录.md` +2 + 跟踪表 +2 + 00:0x 回信率段；6 线建议 **6 条**（designflow 明写「无」）。


- **2026-11-15（本地 21:0x 时窗，r182）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-15.md`「归档 · MEMORY 滚动（2026-11-16 r186）」；含 B 轨第三十七轮 +4（wav2vec 2.0 / MQA / BitNet b1.58 / RM Overoptimization）与 #54–#55 两封信，勿以本指针替代结论。
- **2026-11-15（本地 18:0x 时窗，r181）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-15.md`「归档 · MEMORY 滚动（2026-11-16 r186）」；含 B 轨第三十六轮 +4（Whisper / Gato / SGLang / Self-Consistency）与 #54 一封信，勿以本指针替代结论。
- **2026-11-15（本地 15:0x 时窗，r180）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-15.md`「归档 · MEMORY 滚动（2026-11-16 r186）」；含 B 轨第三十六轮前段与 #52–#53 两封信（Cloudflare XOR 还原 / 主页明文），勿以本指针替代结论。
- **2026-11-15（本地 12:0x 时窗，r179）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-15.md`「归档 · MEMORY 滚动（2026-11-16 r186）」；含 B 轨第三十五轮 +4（Qwen / PaLM / RETRO / AWQ）与 #50–#51 两封信，勿以本指针替代结论。
- **2026-11-15（本地 09:0x 时窗，r178）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-15.md`「归档 · MEMORY 滚动（2026-11-16 r186）」；含 B 轨第三十四轮 +4（MemGPT / Generative Agents / Self-Refine / Mamba）与 #48–#49 两封信，勿以本指针替代结论。
- **2026-11-15（本地 06:0x · 06:00 时窗，r177）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-15.md`「归档 · MEMORY 滚动（2026-11-16 r183 唤醒时执行）」；含 B 轨第三十三轮 +3、作者网 +3、第 47 封中文信（ToolLLM）。
- **2026-11-15（本地 03:0x · 03:00 时窗，r176）** 原文已按 §5 滚动归档 → 同上「归档 · MEMORY 滚动（r183）」；含 A 轨补满 5/5、B 轨第三十二轮 +3、第 46 封日文信、voice_ready 1。

- **2026-11-15（本地 00:0x · 00:00 时窗，r175）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-15.md`「归档 · MEMORY 滚动（2026-11-16 r183 唤醒时执行）」；含 A 轨 3/5、B 轨第三十一轮 +4、作者网 +4、第 44–45 封信，勿以本指针替代结论。
- **2026-11-12（18:00 / 21:00 两轮，r158–r159）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-14 r170 唤醒时执行）」；含 B 轨第十四 / 十五轮、作者网与发信增量，勿以本指针替代结论。
- **2026-11-13（00:00 / 03:00 两轮，r160–r161）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-13.md`「归档 · MEMORY 滚动（2026-11-14 r171 唤醒时执行）」；含 B 轨第十六 / 十七轮与发信增量，勿以本指针替代结论。
- **2026-11-12（本地 03:0x–15:2x · 03/06/09/12/15 五轮，r152–r157 及更早）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-12.md`「归档 · MEMORY 滚动（2026-11-13 r161 唤醒时执行）」；含 B 轨第九至十三轮、A 轨补齐 5/5 与各轮发信/作者网增量，勿以本指针替代结论。






- **2026-11-13（本地 12:0x · 12:00 时窗）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-14.md`「归档 · MEMORY 滚动（2026-11-14 r174 唤醒时执行）」。



- **2026-11-13（本地 15:0x · 15:00 时窗）** 原文已按 §5 滚动归档 → 同上「归档 · MEMORY 滚动（r174）」。



- **2026-11-13（本地 18:0x · 18:00 时窗）** 原文已按 §5 滚动归档 → 同上「归档 · MEMORY 滚动（r174）」。
- **2026-11-13（本地 21:0x · 21:00 时窗）** 原文已按 §5 滚动归档 → 同上「归档 · MEMORY 滚动（r174）」。








- **2026-11-13（06:00 / 09:00 两轮，r162–r163）** 原文已按 §5 滚动归档 → `daily-memories-research/2026-11-13.md`「归档 · MEMORY 滚动（2026-11-14 r172 唤醒时执行）」。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
