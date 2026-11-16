# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r192 · 本地 2026-11-17 03:0x · 03:00 时窗：A 轨补满 5/5 晚报 + B 轨第四十八轮 +4 → 190 + 作者网 +3 → 174（X 已核验 99）+ 3 封信（累计 73）+ voice_ready 2 + news_ready 1] ① A 轨复核 `cat:cs.CL` 列表 **`200` + atom（260,090 B / 100 entry）**，`published` 上界仍 **`2026-11-13T18:45:49Z`**（连续第 15 时窗未前进）⇒ 按「最近一次公告批」例外再收 2 篇：OMA `2611.16816`（Qwen2.5-1.5B/3B；ALFWorld 0.734→0.828 / 0.742→0.812；WebShop-SOL nAUC 0.399→0.511；失败轨迹常打满 50 轮；普通 WebShop「mixed or reversed」）/ Verification Transport `2611.18471`（4 benchmarks × 7 judge 主干 × 4 协议 × 3 边界；31.0% / 30.9% / 20.3%；补溯源救回 85.5%）；`id_list` `200` + atom（17,991 B）+ PDF 2/2 `200` + `%PDF-`（3,031,805 / 848,210 B）；当日 5/5 收口。② B 轨 **+4 → 190**：MT-Bench/LLM-as-a-Judge `2306.05685`（**5,326**，NeurIPS 2023 D&B）/ Self-Rewarding LMs `2401.10020`（**664**，ICML 2024）/ TinyStories `2305.07759`（**589**，MSR 预印本）/ Mind2Web `2306.06070`（**503**，NeurIPS 2023 Spotlight）；arXiv atom `200`（11,227 B / 4 entry）+ OpenAlex 4/4 `200` + PDF 4/4 `200`（末篇 7,635,816 B >5MB 仅 /tmp）；**Magpie 300 / WebShop 358 <500 ⇒ 落选如实记，不凑数**。③ 作者网 **+3 → 174（编号 172–174）**：Yu Su 苏禹（OSU；`su.809@osu.edu` 主页 `mailto:` 明文；`@ysu_nlp` og:title + bio 双源）/ Ming He（天津大学；`heming01@foxmail.com` PDF 首页；X 未找到）/ Disha Sheshanarayana（MUJ；PDF 首页邮箱；X 未找到）；X 已核验 **98 → 99**。④ 发信 **3 封**（今日 6/12、累计 **73**）：#71 苏禹（Mind2Web，中文 CJK 251 字，`SENT OK 03:05:14`）/ #72 Ming He（OMA，中文 260 字，`03:05:17`）/ #73 Disha（Transport，英文 193 词，`03:05:21`）；落款两行其后无任何行；同轮抗模板（开头句 / 问题句式 / 技术细节零共用）。⑤ **回信率 0 / 73**，0 封到期（最早 2026-11-25）；按待诊断信号处理，不记为成功；通道只发不收仍是最大阻塞。⑥ `voice_ready` **2**：V31 Lianmin Zheng `@lm_zheng`（SGLang 在 Meta 生产服务、数十亿用户；2026-11-11；单推页双源，尾部链接截断标节选）/ V32 Yu Su `@ysu_nlp`（ICLR'27 SAC 批次最高均分 3；2026-11-06；双源，个人观察）；两条高热推（ARLoop `@yuekun_yao` / SGLang v1.0 `@sgl_project`）判为转推丢弃。`news_ready` 沿用早报 1 条（Gamer）。⑦ 交付：`daily/2026-11-17.html` **34,852 B**（div 20/20、table 8/8、tr 49/49、td 62/62、th 36/36、h2 6/6、h3 5/5、details 1/1、ul 7/7、li 30/30、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html` 当日行改 5/5 + footer；`research/2026-11-17.md` §8–§14；`SEEN.md` +2（5,690 行）；`papers.jsonl` +2（366 行，JSON 全通过）；`PAPERS.md` 190（#187–#190 + 快照/候选池）；`AUTHORS.md` 174（#172–#174）；`发送记录.md` 新时窗段 + 跟踪表 #71–#73 + 03:0x 回信率段；6 线 PM 增量建议 6 条（pretrain 明写「无」）。
当前动作:     ✅ 本轮闭环：晚报 5/5 + B 轨 190 + 作者网 174 + 3 封信 + voice_ready 2 + 日报 / index / 记忆 + 提交推送。
下一步:       ① 09:00 时窗复核 `cat:cs.CL` 上界（周一 20:00 ET 公告批应在 09:00 CST 后出现）⇒ 前进则按 72h 正常口径另起新条目；② B 轨候选：HBM / JEDEC 一手（连续多轮未命中）/ 训练 spike 侧（QK-clip）/ Magpie `2406.08464`（300）与 WebShop `2207.01206`（358）暂留；③ 发信：#164 Yang You（邮箱域名待复核）/ #169–#171 无公开邮箱只能 X follow；④ 复抓 `@Guangxuan_Xiao` 补 X 核验；⑤ 待用户手动 follow 已核验 99 条 handle；⑥ 11-25 起若仍 0 回，按六层归因并报运维。
本轮新增:     A 轨 +2（当日 5/5）· B 轨 +4（190）· 作者网 +3（174）· 作者信 +3（累计 73）· voice_ready 2 · news_ready 1（沿用）· 回信率 0/73
阻塞:         ① X 写操作需登录态 ⇒ follow 无法自动执行；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到（最需运维介入）；③ `WATCH_RESEARCH_TASK.md` 仍 **44,052 B > 40 KB 红线**，但文件标注「agent 只读」⇒ 需 supervisor 决定是否授权滚动归档；④ `x.com/Guangxuan_Xiao` 上次连续 2 次 `000`，待复抓。
ERROR_COUNT:  96（本轮 +0：所有端点均 `200`；仅 `pdftotext` 少量字体警告，非网络错误）
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
- **累计收录**：`343` 篇（另候选 **4,558** 篇 + **候选（RSS补充）507** 篇 ⇒ 状态行合计 **5,406**；`SEEN.md` 文件 **5,690 行**；仅存 `SEEN.md` 防重；**本轮 +2 收录**（`2611.16816` / `2611.18471`，2026-11-12 / 11-13 提交、最近公告批；当日累计 +5）；`papers.jsonl` **341** 行）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**190 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**四十八轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**174 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V32）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`（与日报草稿同目录，用文件名区分；无 arXiv 的用 `<会议>-<年份>.md`）。 ｜ 现状（2026-11-17 03:0x）：PAPERS **190** / AUTHORS **174**（X 已核验 **99**）/ 作者信 **73**（回信率 **0/73**）。




---



## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-17（本地 03:0x · 03:00 时窗 · A 轨补满 5/5 晚报 ＋ 🅱 B 轨第四十八轮 +4 → 190 ＋ 3 封信（累计 73）＋ 作者网 +3 → 174 ＋ voice_ready 2）** —— **第一百九十二轮**：① A 轨复核 `cat:cs.CL` 列表 `200` + atom（260,090 B / 100 entry），`published` 上界仍 `2026-11-13T18:45:49Z`（连续第 15 时窗未前进）⇒ 按「最近一次公告批」例外补 2 篇未消费候选：**OMA `2611.16816`**（Dawei Zhang 等 8 位，通讯 Ming He；Qwen2.5-1.5B/3B；ALFWorld 端点 0.734→0.828 / 0.742→0.812；WebShop-SOL nAUC 0.399→0.511；普通 WebShop「mixed or reversed」；失败轨迹常打满 50 轮）/ **Verification Transport `2611.18471`**（Disha Sheshanarayana / Sai Linisha Reddy Goli，MUJ；4 benchmarks × 7 judge 主干 × 4 协议 × 3 抽象边界；31.0% / 30.9% / 20.3% 翻转；补溯源救回 85.5%）；`id_list` `200` + atom（17,991 B）+ PDF 2/2 `200` + `%PDF-`（3,031,805 / 848,210 B）；当日 5/5 收口。② B 轨 **+4 → 190**：MT-Bench/LLM-as-a-Judge `2306.05685`（**5,326**，NeurIPS 2023 D&B）/ Self-Rewarding LMs `2401.10020`（**664**，ICML 2024）/ TinyStories `2305.07759`（**589**，MSR）/ Mind2Web `2306.06070`（**503**，NeurIPS 2023 Spotlight）；atom `200`（11,227 B / 4 entry）+ OpenAlex 4/4 `200` + PDF 4/4 `200`（末篇 7,635,816 B >5MB 仅 /tmp）；**Magpie 300 / WebShop 358 <500 ⇒ 如实落选留候选，不凑数**。③ 作者网 **+3 → 174（#172–#174）**：Yu Su 苏禹（OSU；`su.809@osu.edu` 主页 `mailto:` 明文；`@ysu_nlp` og:title + bio 双源）/ Ming He（天津大学；`heming01@foxmail.com` PDF 首页；X 未找到）/ Disha Sheshanarayana（MUJ；PDF 首页邮箱；X 未找到）；X 已核验 **98 → 99**。④ 发信 **3 封**（今日 6/12、累计 **73**）：#71 苏禹（Mind2Web，中文 CJK 251 字，`SENT OK 03:05:14`）/ #72 Ming He（OMA，中文 260 字，`03:05:17`）/ #73 Disha（Transport，英文 193 词，`03:05:21`）；落款两行其后无任何行；同轮开头句 / 问题句式 / 技术细节零共用。⑤ **回信率 0 / 73**，0 封到期（最早 2026-11-25）⇒ 按待诊断信号处理，不记为成功；通道只发不收仍是最大阻塞。⑥ `voice_ready` **2**：V31 Lianmin Zheng `@lm_zheng`（SGLang 在 Meta 生产服务、数十亿用户；2026-11-11；双源，尾部链接截断标节选）/ V32 Yu Su `@ysu_nlp`（ICLR'27 SAC 批次最高均分 3；2026-11-06；双源，个人观察非统计结论）；两条高热推（ARLoop `@yuekun_yao` / SGLang v1.0 `@sgl_project`）判为转推丢弃。⑦ 交付：`daily/2026-11-17.html` **34,852 B**（div 20/20、table 8/8、tr 49/49、td 62/62、th 36/36、h2 6/6、h3 5/5、details 1/1、ul 7/7、li 30/30、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html` 当日行改 5/5 + footer；`research/2026-11-17.md` §8–§14；`SEEN.md` +2（5,690 行）；`papers.jsonl` +2（366 行，JSON 全通过）；`PAPERS.md` 190 / `AUTHORS.md` 174；`发送记录.md` 新时窗段 + 跟踪表 #71–#73 + 03:0x 回信率段；6 线 PM 增量建议 6 条（pretrain 明写「无」）。


- **2026-11-17（本地 00:0x · 00:00 时窗 · A 轨 3/5 早报 ＋ 🅱 B 轨第四十七轮 +4 → 186 ＋ 3 封中文信 ＋ 作者网 +3 → 171 ＋ voice_ready 0 ＋ news_ready 1）** —— **第一百九十一轮**：① A 轨 `cat:cs.CL` 列表 `200` + atom（260,090 B / 100 entry），`published` 上界仍 `2026-11-13T18:45:49Z`（公告批连续第 14 时窗未前进）⇒ 按「最近一次公告批」例外取 3 篇未消费候选：**ModHarness-RL `2611.18533`**（State=typed blocks / Compression+Steering / CodeSearch 14–24%、对最强基线 +5–12% / 1.5B–8B；Penn State+LinkedIn）· **Muon 临时 weight decay `2611.17876`**（162M/405M/1.4B/3.4B；撤除时差 0.26 nats、73% 才反超、终点 0.0275 nats；λ=0.15 / 前 44% / 28,000 updates；Meta+Mila+UdeM+Samsung SAIL）· **Gamer `2611.18397`**（数万小时键鼠轨迹 / 一千小时+指令数据 / speculative decoding+BF16 验证 / Qwen3-VL 2B–32B 与 30B-A3B / A800+H200；miHoYo Honkai AI R&D）；`id_list` `200` + atom（10,065 B / 3 entry）+ PDF 3/3 `200` + `%PDF-`（841,073 / 879,284 / 24,627,777 B，末篇 >5MB 仅 /tmp）。② B 轨 **+4 → 186**：AlphaCode `2203.07814`（**1,787**，Science 2022，DOI `10.1126/science.abq1158`）· BLOOM `2211.05100`（**2,860**，394 作者）· StarCoder `2305.06161`（**1,518**，67 作者）· HH-RLHF `2204.05862`（**5,138**，31 作者）；atom `id_list` `200`（39,958 B / 4 entry）+ OpenAlex 4/4 `200` + PDF 4/4 `200`（<5MB）；`pdftotext` 核到 `top 54.3%` / `more than 5,000 participants` / `10 simulated Codeforces contests`、`46 natural and 13 programming languages (59 in total)` / `ROOTS corpus`、`1 trillion tokens` / `opt-out process` / `multi-query attention`、`iterated online mode` / `Online HH RLHF (52B)`。③ 作者网 **+3 → 171（编号 169–171）**：Thomas Wolf（HF 个人页 href → X + `x.com/Thom_wolf` `200` / og:title 双源 ⇒ 已核；无公开邮箱）· Loubna Ben Allal（同上双源，og:description = `Research @huggingface`；无公开邮箱）· Oriol Vinyals（`@OriolVinyalsML` **仅 og:title 单源 ⇒ 不计入已核验**；⚠️ `oriolvinyals.com` 实为同名西班牙治疗师站 ⇒ 丢弃不建档）；X 已核验 **96 → 98**。④ 发信 **3 封中文**（今日 3/12、累计 **70**）：#68 刘鹏飞 `pengfei@sjtu.edu.cn`（LIMA，229 字，`SENT OK 00:03:01`）· #69 Guangxuan Xiao `xiaoguangxuan@gmail.com`（StreamingLLM，287 字，`00:03:07`）· #70 刘泽 `liuzeeeee@gmail.com`（Swin，262 字，`00:03:14`）；落款两行 `祝好，`/`Yang Liu`，同轮开头句与问题落点无共用；同论文 Xuezhe Ma 按「同论文 ≤1」未发。⑤ 回信率 **0/70**，0 封到期（最早 2026-11-25）；发件通道仍只发不收。⑥ `voice_ready` **0（本期无）**：`x.com`=200；抓 `@LoubnaBenAllal1` 8 条 / `@Thom_Wolf` 9 条；两条候选经单推页 og:title 核为转推（`@Nouamanetazi` / `@andonlabs`）⇒ 丢弃；两条作者核对通过者页面无 og:description、时间线正文截断 ⇒ 按「正文不完整不采用」弃用。`news_ready` **1**（Gamer，明标「无量化胜率」只作候选）。⑦ 交付：`daily/2026-11-17.html` **22,812 B**（div 14/14、table 5/5、tr 30/30、td 38/38、th 22/22、h2 4/4、details 1/1、0 `<script>`、0 残留 `**`）+ `index.html` 新行与 footer；`PAPERS.md` **186**（#183–#186）/ `AUTHORS.md` **171**（#169–#171，3 条状态更新为已发信）；`research/2026-11-17.md` §0–§7；`SEEN.md` +3（5,685 行）；`papers.jsonl` +3（364 行，JSON 全通过）；`发送记录.md` +3 行 + 跟踪表 #68–#70 + 00:1x 回信率段；6 线建议 **6 条**（designflow 明写「无」）。
- **2026-11-16（本地 21:0x · 21:00 时窗 · A 轨 0 新收（配额满，公告批未前进）+ 🅱 B 轨第四十六轮 +4 → 182 + 作者网 +3 → 170 + 0 封信（今日 12 封硬上限）+ voice_ready 1（V30））** —— **第一百九十轮**：① A 轨 `cat:cs.CL` 20-entry **`200` + atom（50,794 B / 20 entry）**，`published` 上界仍 **`2026-11-13T18:45:49Z`**（与 18:00 一致，周末不公告）；今日 5/5 ⇒ 0 新收。② B 轨 +4 → 182：LIMA `2305.11206`（**904**，NeurIPS 2023）/ False Promise `2305.15717`（**304**，ICLR 2024 spotlight，**&lt;500 按方法论常青**）/ Muon is Scalable `2502.16982`（**622**，预印本）/ FlashAttention-3 `2407.08608`（**418**，NeurIPS 2024，**&lt;500 按开创范式**）；atom `id_list` `200`（11,916 B / 4 entry）+ abs 4/4 `200` + OpenAlex 4/4 `200` + OpenReview 1/1 `200` + PDF 4/4 `200`（均 <5MB）；`pdftotext` 核到 `1,000 carefully curated` / `750,000 tokens` / `43%` / `88% meet the prompt requirements`、`∼70%` / `mimicking ChatGPT’s style but not its factuality`、`adding weight decay` / `per-parameter update scale` / `∼ 2× computational efficiency` / `5.7T tokens`、`740 TFLOPs/s (75% utilization)` / `1.2 PFLOPs/s` / `2.6× lower numerical error`。③ 落选如实记：Zero Bubble `2401.10241` 仅 **90** 被引 ⇒ 不收（不凑数）。④ 作者网 +3 → 170：Xuezhe Ma（USC ISI；`xuezhema@usc.edu` 目录页明文；X `@MaxMa1987` 双源）/ Pengfei Liu（SJTU；`pengfei@sjtu.edu.cn` 教师页明文；X 未找到）/ Eric Wallace（OpenAI；CV 内仅旧域 ⇒ 不建议直发；X `@Eric_Wallace_` 双源）；X 已核验 96。⑤ 发信 0：今日 12 封 = 硬上限；草稿 `drafts/2305.11206-{ma,liu}.md` 已入仓并标「未发送」，下轮按「同论文 ≤1」只发其一。⑥ 回信率 **0/67**，0 封到期（最早 2026-11-25）。⑦ `voice_ready` **1（V30）** = Eric Wallace 2026-11-04 原推（前沿算力投入开源漏洞发现与修补；单推页双源，**正文摘要处截断 ⇒ 引用须标节选**）；`news_ready` 0。⑧ 交付：`daily/2026-11-16.html` **102,580 B** + `index.html`；PAPERS 182 / AUTHORS 170；`research/2026-11-16.md` §13；`发送记录.md` 21:0x 回信率段；6 线建议 6 条（vision / designflow 明写「无」）。⑨ ⚠️ 同名站点假阳性 2 个（`chunting.me` 他人博客 / `jayshah.dev` 6sense 工程师）⇒ 均丢弃未建档。

- **2026-11-16（本地 18:0x · 18:00 时窗 · A 轨 0 新收（配额满，公告批未前进）+ 🅱 B 轨第四十五轮 +4 → 178 + 作者网 +2 → 167 + 0 封信（今日 12 封硬上限）+ voice_ready 1）** —— **第一百八十九轮**：① A 轨 `cat:cs.CL` 20-entry `200` + atom（50,794 B / 20 entry），`published` 上界仍 `2026-11-13T18:45:49Z`（周末不公告）；今日 5/5 ⇒ 0 新收。⚠️ `http://export.arxiv.org/api/query` 本轮返回 **`301` / 0 B** ⇒ 改 `https://` 后 `200` + atom，后续固定 https。② B 轨 +4 → 178：LAMB `1904.00962`（932，ICLR 2020）/ LayerNorm `1607.06450`（12,853，预印本，无 comment）/ StreamingLLM `2309.17453`（1,248，ICLR 2024）/ Nucleus Sampling `1904.09751`（2,832，ICLR 2020）；abs 4/4 + atom 4/4 + OpenAlex 4/4 + PDF 4/4 全 `200`，`pdftotext` 核 `76 minutes` / `batch size of 32768` / `91.460` / `100.2% efficiency` / `single training case` / `adaptive bias and gain` / `up to 4 million tokens` / `22.2× speedup` / `Beam Search (size 32) leads to degenerate repetition`。StreamingLLM PDF **16.95MB ≥5MB** ⇒ 只在 `/tmp` 核、不入 git。③ 作者网 +2 → 167（编号 164–165）：Yang You（NUS；主页 `yangyou (at) nus (dot) edu` 域名待复核；X `@YangYou1991` 双源核 ⇒ 待跟踪）/ Guangxuan Xiao（MIT HAN Lab；`xiaoguangxuan@gmail.com` 主页 mailto；X `@Guangxuan_Xiao` 仅主页 href 单源 + `x.com` 两次 `000` ⇒ 未核验不计数）；X 已核验 94。④ 发信 0：今日 12 封（#56–#67）= 每日硬上限；待发 #164（域名复核后）/ #165 / #161 / #162。⑤ 回信率 **0/67**，0 封到期（最早 2026-11-25）；新增可审计变量 = 邮箱域名与机构属地不一致（`nus (dot) edu` vs 常见 `nus.edu.sg`）⇒ 复核前不发。⑥ `voice_ready` **1**（V29 = Yang You 2026-11-04 原推：The Trinity / harness 能力驱动演化 / `+26 points across 18 unseen benchmarks`；单推页 `og:title`+`og:description` 双源一致）；`news_ready` 0。⑦ 交付：`daily/2026-11-16.html` **90,002 B / 87.9 KB**（div 126/126、table 24/24、tr 148/148、td 453/453、th 101/101、details 4/4、h2 22/22、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html` 行与 footer；PAPERS 178 / AUTHORS 167；`research/2026-11-16.md` §12；`发送记录.md` 18:0x 回信率段；6 线建议 6 条（data / designflow 明写「无」）。

- **2026-11-16（本地 15:0x · 15:00 时窗 · A 轨 0 新收（配额满，公告批继续前进）+ 🅱 B 轨第四十四轮 +4 → 174 + 作者网 +3 → 165 + 0 封信（今日 12 封硬上限））** —— **第一百八十八轮**：① A 轨 `cat:cs.CL` 20-entry `200`+atom（**50,794 B / 20 entry**），`published` 上界 **`2026-11-13T18:45:49Z`**（较 12:00 的 `08:40:07Z` 继续前进）；今日 5/5 ⇒ 0 新收。② B 轨 +4 → 174：Swin `2103.14030`（38,712，ICCV 2021）/ SpeechT5 `2110.07205`（141，ACL 2022，<500 按「开创统一模态范式」收）/ GPipe `1811.06965`（1,280，NeurIPS 2019）/ Scaling Data-Constrained `2305.16264`（254，NeurIPS 2023，<500 按「方法论常青」收）；abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200`，`pdftotext` 核数字。⚠️ 先验 ID `2010.00718` 实为 `When to Impute?` ⇒ SpeechT5 真 ID 已纠正为 `2110.07205`。③ 作者网 +3 → 165（Ze Liu 刘泽 / Junyi Ao / Long Zhou；X 已核验 93）。④ 发信 0：今日 12 封（#56–#67）= 每日硬上限 ⇒ 只做收录与建档；待发 #161 / #162（中文）。⑤ 回信率 0/67，0 封到期（最早 2026-11-25）。⑥ voice/news 均 0。⑦ 交付：`daily/2026-11-16.html` 78,849 B / 77.0 KB + `index.html`；PAPERS 174 / AUTHORS 165；`research/2026-11-16.md` §11；`发送记录.md` 15:0x 回信率段；`replies/README.md`。⑧ 发现 `WATCH_RESEARCH_TASK.md` 44,052 B 超 40 KB 红线，但标注 agent 只读 ⇒ 已记入阻塞，待 supervisor 决定。
- **2026-11-16（本地 12:0x · 12:00 时窗 · A 轨 0 新收（配额满，公告批首次前进）+ 🅱 B 轨第四十三轮 +4 → 170 + 第 66/67 封信（中文 RTLLM / 英文 Gemini 1.5））** —— **第一百八十七轮**：① A 轨 `cat:cs.CL` 20-entry `200`+atom（47,638 B / 20 entry），`published` 上界 `2026-11-13T08:40:07Z` ⇒ 连续 16 个时窗未前进后**首次前进**；今日 5/5 ⇒ 0 新收。② B 轨 +4 → 170：Gemini 1.5 `2403.05530`（4,633）/ RTLLM `2308.05345`（301，ASP-DAC 2024）/ VerilogEval `2309.07544`（359，ICCAD 2023 Invited）/ PIM Benchmarking `2105.03814`（285，IEEE Access 2022）；abs 4/4 `200` + OpenAlex 4/4 `200` + PDF 4/4 `200`，`pdftotext` 核数字。⚠️ 先验 ID `2309.00867`/`2309.04781` 命中无关论文 ⇒ 已纠正。③ 作者网 +4 → 162（谢知遥 / Machel Reid / Juan Gómez-Luna / Onur Mutlu；X 已核验 92）。④ 发信 2 封：`SENT OK 12:05:36`（#66 中文 186 汉字）· `12:05:43`（#67 英文 187 词），落款两行、查重 0 命中，今日 12 封 = 硬上限。⑤ 回信率 0/67，0 封到期。⑥ voice/news 均 0。
- **2026-11-16（本地 09:0x · 09:00 时窗 · A 轨复核「批仍未前进」+ 🅱 B 轨第四十二轮 +5 + 第 63/64/65 封信（日文 / 中文 / 中文））** —— **第一百八十六轮**：① A 轨 `cat:cs.CL` 20-entry `200`+atom（**50,083 B / 20 entry**，四轮逐值一致），`published` 上界 `2026-11-12T18:59:52Z` ⇒ **连续第 16 个时窗未前进**；今日 5/5 ⇒ 0 新收。② B 轨 **+5 → 166**：GShard `2006.16668`（1,633，2020 预印本）· Mixtral `2401.04088`（4,372）· Self-RAG `2310.11511`（1,091，**会场未核不写 ICLR**）· LongBench `2308.14508`（1,169，ACL 2024）· Cambrian-1 `2406.16860`（514，NeurIPS 2024 Oral）；`id_list` 连续 `429`×3 ⇒ 改走 abs 页 5/5 `200`（43,816 / 46,189 / 42,906 / 45,172 / 45,385 B；作者数 9/26/5/13/14）；OpenAlex 5/5 `200`；PDF 5/5 `200`（1,747,868 / 2,475,990 / 1,405,127 / 11,630,690 / 6,427,380 B；35/13/30/19/51 页）`pdftotext` 全通过，核到 `600 billion`/`2048 TPU v3`、`47B`/`13B active`、`ISREL`/`ISSUP`/`ISUSE`、`4,750 test instances`/`13,386 characters`、`Spatial Vision Aggregator`/`576`/`36 tokens`/`OCR (27.6%)`。⚠️ LongBench 11.6 MB、Cambrian-1 6.4 MB >5 MB ⇒ 仅本地 gitignore。③ 作者网 **+3 → 158**（#154 Asai：`aasai@andrew.cmu.edu` 为主页 `mailto:` **百分号编码**解码所得 + `@AkariAsai` 双源；#155 白雨石：`bys22@mails.tsinghua.edu.cn` 主页明文 + `@realYushiBai` 双源；#156 童晟邦：`tsb@berkeley.edu` 主页明文 + `@TongPetersb` 双源）；X 已核验 **89**。④ 发信 **3 封**：`SENT OK 09:04:43`（#63 日文 **300 字非空白**）· `09:04:50`（#64 中文 **215 汉字 / 343 非空白**）· `09:04:55`（#65 中文 **207 汉字 / 347 非空白**）；落款严格两行、其后无任何行；正文不含项目名；查重三 ID 与三地址 **0 命中**；与同轮另两封开头句 / 问题句式 / 技术细节零共用；本时窗 3 封 = 上限，今日 10 封 ≤12；**母语判定按姓名族属优先（#63 日文、#64/#65 中文），未因海外机构 / berkeley.edu / gmail 判英文**。⑤ **回信率 0 / 65**，**0 封到期**（最早 2026-11-25）；新增分层变量 = 日文母语收件人 · 海外 vs 国内华人。⑥ `voice_ready` 0（只核 handle、未抓 timeline）；`news_ready` 0（五篇均经典方法 / 技术报告，无事件点）。⑦ 交付：`daily/2026-11-16.html` **58,075 B / 56.7 KB**（table 10/10、h2 9/9、h3 5/5、ol 5/5、li 20/20、details 2/2、footer 1/1、0 `<script>`、0 残留 `**`）+ `index.html`（当日行 5/5，追加 03:00/06:00/09:00 段；footer 166 / 158 / 65 / 0/65）；`PAPERS.md` **166**（#162–#166）/ `AUTHORS.md` **158**（#154–#156）；`research/2026-11-16.md` §9；`发送记录.md` +3 行 + 跟踪表 +3 + 09:0x 回信率段；6 线建议 **6 条增量**。
























- **更早轮次（2026-11-12 ~ 2026-11-16，r152–r183）**：原文已按 §5 滚动归档 → `daily-memories-research/` 各日文件的「归档 · MEMORY 滚动」段（2026-11-13 / 14 / 15 / 16 等），此处只留指针，勿以指针替代结论。
## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
