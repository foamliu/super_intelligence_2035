# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```

PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r231 · 本地 2026-11-21 18:0x · 18:00 时窗：A 轨 0 新收（今日 5/5 已满）＋ B 轨 +3 → 320 ＋ 作者网 +2 → 296 ＋ 发信 0（当日 12/12，备稿共 3）＋ 回信率 0/128]
  ① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）**`200` / 109,971 B / 40 entry / atom**；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 11 窗未前进**，仍在 72h 内，截止 11-22 18:57Z）。
  ② A 轨 **0 新收**（今日 5/5 已满，不凑第 6 篇、不替换已发条目）。
  ③ B 轨 **+3 → 320**：Depth Anything `2401.10891`（**2,769**，CVPR 2024）/ HunyuanVideo `2412.03603`（**2,092**，预印本）/ V-JEPA `2404.08471`（**846**，TMLR）；arXiv `id_list` 单批 `200` + atom（15,089 B / 3 entry）+ abs 3/3 `200`（42,879 / 50,895 / 41,768 B）+ OpenAlex 3/3 `200`；先查重：三 ID 在 `PAPERS.md` / `SEEN.md` / `papers.jsonl` 0 命中，同批候选 DeepSeek-R1 / Mixtral / Self-Consistency / Ring Attention / s1 / DCLM 已在表内 ⇒ 剔除。
  ④ 作者网 **+2 → 296**：#295 Lihe Yang **A** `lihe.yang.cs@gmail.com`（`liheyoung.github.io` `200` / 17,151 B 页内 `mailto:`）/ #296 Hengshuang Zhao **A** `hszhao[at]cs.hku.hk`（HKU 个人页 `200` / 36,107 B 明文）；X 已核验保持 **111**（`@LiheYoung` / `@hszhao` 均 `404` ⇒ 不记）。
  ⑤ 发信 **0 封**（累计 128）：当日 **12/12** 硬上限 ⇒ 不跨日借额度；新增 1 封中文草稿 `drafts/2401.10891.md`（**241** 汉字，落款两行），待发共 3 封（2303.05499 198 / 2401.15077 209 / 2401.10891 241），计划 11-22 00:00 起发。
  ⑥ 回信率 **0 / 128**，**0 封到期**（最早 2026-11-25，#1–#7）；`replies/` 仍只有 `README.md`；通道只发不收。
  ⑦ voice_ready **本窗 0 新增**（今日已 2 条，达上限）/ news_ready **0**（3 条方法·技术报告类，无本窗事件点）。
  ⑧ 交付：`daily/2026-11-21.html`（+18:00 节：B 轨表 + 作者/信件段 + news_ready 0 + 6 线建议 + 附录）+ `daily/index.html` 当日行（320 / 296 / 111 / 128 / 备稿 3）+ `research/2026-11-21.md` 18:00 节 + `PAPERS.md` #318–#320 + `AUTHORS.md` #295–#296 + `发送记录.md` §18:0x + draft 1 个。

当前动作:     ✅ 18:00 时窗闭环：A 轨 0 新收（额度已满），B 轨 +3（Depth Anything / HunyuanVideo / V-JEPA，均 ≥500），作者网 +2（均 A 级邮箱），信 0 封（日上限）但新增 1 封草稿，voice_ready 0 新增（达上限）。
下一步:       ① 21:00 时窗：继续 B 轨候选（HBM/JEDEC 一手 / QK-clip 实现 / InternViT 一手 / 视频世界模型一手）+ 作者网 +2；② 11-22 00:00 额度重置后发已备 3 封（发送前复核地址页）；③ 11-25 首批到期 → #1–#7 转 `无应答(>14d)`；④ 运维：发件显示名 / SMTP 只发不收 / 任务书 44 KB 超红线；⑤ 推送：先 `pull --rebase` 再 push。
本轮新增:     A 轨 0（今日 5/5）· B 轨 +3（320）· 作者网 +2（296）· 作者信 0（128，备稿共 3）· voice_ready 0 新增 · news_ready 0 · 回信率 0/128 · X 已核验 111
阻塞:         ① 🔴 发件显示名 `AI+EDA 招聘 · 自动`（最可能的 0 回信原因），需运维改配置；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到；③ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且 agent 只读 ⇒ 需授权；④ 无新增其他阻塞。
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
- **上次采集窗口**：`2026-11-20 18:0x`（**第二百二十二轮 · 18:00 时窗**：`cat:cs.CL` `200` / 109,971 B / 40 entry；最新 `published` **`2026-11-19T18:57:25Z`**（与 15:00 相同）；B 轨第七十六轮 +4 → 292）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`363` 篇（11-20 A 轨 +5：`2611.24849` / `2611.24844` / `2611.24071` / `2611.24809` / `2611.24540`；`SEEN.md` 为唯一防重台账）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**320 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**七十三轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**296 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-21（本地 18:0x · 18:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十四轮 +3 → 320 ＋ 作者网 +2 → 296 ＋ 信 0 封（当日 12/12，备稿新增 1）＋ 回信率 0/128）** —— **第二百三十一轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 11 窗未前进**）。② A 轨 **0 新收**（今日 5/5 已满）。③ B 轨 **+3 → 320**：Depth Anything `2401.10891`（**2,769**，CVPR 2024）/ HunyuanVideo `2412.03603`（**2,092**，预印本）/ V-JEPA `2404.08471`（**846**，TMLR）；`id_list` 单批 `200` + atom（15,089 B / 3 entry）+ abs 3/3 `200` + OpenAlex 3/3 `200`；先查重剔除已在表内的 DeepSeek-R1 / Mixtral / Self-Consistency / Ring Attention / s1 / DCLM。④ 作者网 **+2 → 296**：#295 Lihe Yang **A** `lihe.yang.cs@gmail.com`（`liheyoung.github.io` `200` / 17,151 B 页内 `mailto:`）/ #296 Hengshuang Zhao **A** `hszhao[at]cs.hku.hk`（HKU 页 `200` / 36,107 B 明文）；X 保持 **111**（`@LiheYoung` / `@hszhao` 均 `404` ⇒ 不记）。⑤ 发信 **0 封**（累计 128，当日 12/12）：新增草稿 `drafts/2401.10891.md`（中文 **241** 汉字），待发共 3 封。⑥ 回信率 **0/128**，0 封到期（最早 11-25）。⑦ voice_ready 0 新增（达上限）/ news_ready 0。⑧ 交付：`daily/2026-11-21.html` +18:00 节、`index.html` 当日行（320 / 296 / 111 / 128 / 备稿 3）、`research/2026-11-21.md` 18:00 节、`PAPERS.md` #318–#320、`AUTHORS.md` #295–#296、`发送记录.md` §18:0x、draft 1。

- **2026-11-21（本地 15:0x · 15:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十三轮 +3 → 317（Grounding DINO 2,415 / AndroidWorld 525 / EAGLE 499）＋ 作者网 +2 → 294（Shilong Liu A 级 / Hongyang Zhang A 级，X 已核验 111）＋ 信 0 封（当日 12/12 硬上限，备 2 封中文草稿 198 / 209 汉字）＋ 回信率 0/128，0 封到期；两处 ID 误记写入前拦截（2303.19588⇒2303.05499、2502.05907 实为 EvolvingAgent）** —— 核验：arXiv `id_list` `200` + atom、abs 3/3 `200`、OpenAlex 3/3 `200`；`x.com` 经代理 `200`，`@atasteoff` `404` 不记；交付 `daily/2026-11-21.html` +15:00 节、`index.html` 当日行、`PAPERS.md` #315–#317、`AUTHORS.md` #293–#294、`发送记录.md` §15:0x、draft 2 个。

- **2026-11-21（本地 12:0x · 12:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十二轮 +3 → 314 ＋ 作者网 +2 → 292 ＋ 1 封信（累计 128，今日 12/12 满）＋ 回信率 0/128）** —— **第二百二十九轮**：① 网络：`cat:cs.CL`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 9 窗逐字相同**）。② A 轨 **0 新收**（今日 5/5 已满，不凑第 6 篇）。③ B 轨 **+3 → 314**：Grounding DINO 1.5 `2405.10300`（**237**，按「本领域权威」，预印本）/ CodeAct `2402.01030`（**470**，按「方法论常青」，arXiv `comment` = ICML 2024、OpenAlex 仍记 preprint）/ Native Sparse Attention `2502.11089`（**674**，≥500 直接满足，OpenAlex source = ACL 2025）；arXiv `id_list` 单批 **`200` + atom**（10,529 B / 3 entry）+ abs 页 **3/3 `200`**（44,192 / 44,230 / 44,015 B）+ OpenAlex **3/3 `200`**。⚠️ **写入前拦截 ID 误记**：原计划「Small-scale proxies」按记忆写作 `2209.14375`，`id_list` 实测为 *Improving alignment of dialogue agents via targeted human judgements* ⇒ 真 ID `2309.14322` **已在表内 #226** ⇒ 整条剔除、换收 NSA。④ 作者网 **+2 → 292**：#291 Xingyao Wang（UIUC / OpenHands；**无明文邮箱** —— GitHub `email=null`、`xwang.dev` 邮箱为 Cloudflare 编码，不反解）/ #292 Peter J. Liu（无现行页；据 X 简介曾在 Google Brain / DeepMind）；X 已核验 **110**（`@xingyaow_` `200` / 170,026 B、`@peterjliu` `200` / 162,821 B，均 `og:title`+`og:description` 双源）；`@xingyaoww` / `@m_wortsman` **`404`**、`@Wortsman` 为另一人 ⇒ 未收。⑤ 发信 **1 封**（累计 **128**，今日 **12/12** 达每日硬上限）：#128 **Vidya A. Chhabria** `vidyachhabria@asu.edu`（ASU profile 当场复核 `200` / 124,745 B，页内明文 ⇒ **A 级**）/ `2405.06676` EDA Corpus（B 轨 #264，末位 / 通讯）/ 英文 **200** 词（`wc -w` 实测）/ `SENT OK 12:03:31`；**已到日上限 ⇒ 后续时窗不借额度**。三问各指一处决策：Table II 的 **28 条失败脚本**「崩 vs 跑通改错对象」占比（executor vs state-diff）／增强改写是否与原文**同侧**划分（否则 22/50 只当下界）／**258 database vs 138 flow** 的小语料配比。专属细节：Table I `198+392=590`、`395+545=943`、Table II `22 true / 28 false`、`95/5`。⑥ 回信率 **0 / 128**，**0 封到期**（最早 11-25）；`replies/` 仍只有 `README.md`。⑦ voice_ready **0 新增**（今日已 2 条，达上限）/ news_ready **0**。⑧ 交付：`daily/2026-11-21.html`（+12:00 节；69,742 B，div 18/18、table 18/18、tr 108/108、td 253/253、th 74/74、0 script、0 残留 `**`）+ `index.html` 当日行（314 / 292 / 110 / 128）+ `research/2026-11-21.md` 12:00 节 + `PAPERS.md` #312–#314 + `AUTHORS.md` #291–#292（#245 → 已发信）+ `发送记录.md` §12:0x + 回信表 #123–#128。
- **2026-11-21（本地 09:0x · 09:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十一轮 +4 → 311 ＋ 作者网 +3 → 290 ＋ 2 封中文信（累计 127）＋ 回信率 0/127 ＋ voice_ready 0 新增）** —— **第二百二十八轮**：① 网络：`cat:cs.CL&max_results=40`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**（连续第 8 窗未前进）；`x.com` 直连 `000`、代理 `127.0.0.1:7897` **`200`**（`x.com/liuziwei7` `200` / 217,370 B）。② A 轨 **0 新收**（今日 5/5 已满，不凑第 6 篇）。③ B 轨 **+4 → 311**：LLaVA-OneVision `2408.03326`（**3,423**，TMLR；单模型覆盖单图/多图/视频 + 任务迁移）/ VideoMAE `2203.12602`（**2,690**，NeurIPS 2022，pp. 10078–10093；管状掩码 90–95%、3k–4k 视频、K400 87.4%）/ DINO-X `2411.14347`（**173**，<500 按「本领域权威」；Grounding-100M、Pro 零样本 COCO 56.0 AP）/ RoPE 外推 `2310.05209`（**107**，<500 按「方法论常青」；ICLR 2024，critical dimension，16K→1M）；⚠️ **`id_list` 前两次 `429`**，加 `User-Agent` + 退避后第三次 `200` + atom（**10,844 B / 4 entry**）—— 未把 429 当「无数据」；abs 4/4 `200`（42,147 / 42,543 / 45,378 / 41,298 B）+ OpenAlex 4/4 `200`；**先查重剔除** EVA-02 `2303.15343` / Moonlight `2502.16982` / YaRN `2309.00071` / SAM2 `2408.00714`（已在表内）。④ 作者网 **+3 → 290**：#288 Limin Wang 王利民 **A** `lmwang.nju@gmail.com`（`wanglimin.github.io` 明文 `lmwang.nju [at] gmail.com`，55,527 B）/ #289 Xipeng Qiu 邱锡鹏 **A** `xpqiu@fudan.edu.cn`（主页 `mailto:`，33,632 B）/ #290 Ziwei Liu 刘子纬 **无邮箱**（`liuziwei7.github.io` 39,458 B 无 `mailto:`）；X 已核验 **108**（+1 `@liuziwei7`，`og:title` × `og:description` 双源）；DINO-X 20 位作者原生 HTML **无公开邮箱** ⇒ 只计不建、不猜；⚠️ 顶部计数行上轮（06:0x）漏更新，本轮以 287 为基线续记并写明。⑤ 发信 **2 封**（累计 **127**，今日 **11/12**）：#126 邱锡鹏 中文 **228** 字 `SENT OK 09:07:13` / #127 王利民 中文 **257** 字 `09:07:14`；地址发前当场复核 2/2 `200`；两封开头句不同、问句句式零共用；专属细节 = `critical dimension` + 16K→1M / 管状掩码 90–95% + 3k–4k 视频；落款严格两行其后无行。**主动少发一封**（DINO-X / LLaVA-OneVision 无公开邮箱 ⇒ 宁缺不猜）。⑥ 回信率 **0 / 127**，**0 封到期**（最早 2026-11-25，#1–#7 ⇒ 距今 4 天）；`replies/` 仍只有 `README.md`；通道只发不收。⑦ voice_ready **0 新增**（今日已 2 条 Karpathy / Sutton，达「每期 ≤2 条」上限）/ news_ready **0**（4 条经典均方法类、无事件点）。⑧ 交付：`daily/2026-11-21.html`（+09:00 节：B 轨表 + voice/作者/信件段 + news_ready 0 + 6 线建议 + 附录；表头标题/时间同步改）+ `daily/index.html` 当日行改写（311 / 290 / 108 / 127 / voice 2）+ `research/2026-11-21.md` 09:00 节 + `PAPERS.md` #308–#311 + `AUTHORS.md` #288–#290 + `发送记录.md` §09:0x + #126–#127 行 + drafts/bodies 各 2。⑨ 记忆维护：MEMORY 27.3 → 27.8 KB（<32 KB），未 fold（近 8 条流水均在本周）。

- **2026-11-21（本地 06:0x · 06:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十轮 +3 → 307 ＋ 作者网 +2 → 287 ＋ 3 封中文信（累计 125）＋ 回信率 0/125 ＋ voice_ready 1）** —— **第二百二十七轮**：① 网络：`cat:cs.CL&max_results=40` 直连 `200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（连续第 7 窗未前进）；`x.com` 直连 `000`、代理 `127.0.0.1:7897` **`200`**（推文页 125,980 B）。② A 轨 **0 新收**（5/5 已满，不凑第 6 篇）。③ B 轨 **+3 → 307**：Mask DINO `2206.02777`（**911**，CVPR 2023，DOI `10.1109/cvpr52729.2023.00297`；query embedding × 高分辨率像素图点积出掩码）/ ViT-22B `2302.05442`（**965**，QK-norm 压注意力 logit 过大）/ PaLM 2 `2305.10403`（**2,439**，配比 > 规模、深窄）；`id_list` 单批 `200` + atom（9,772 B / 3 entry）+ abs 3/3 `200`（42,570 / 47,645 / 64,215 B）+ OpenAlex 3/3 `200`；**先查重剔除** Position Interpolation `2306.15595` / InternVL `2312.14238`（已在表内）。④ 作者网 **+2 → 287**：#286 Ryan Hanrui Wang **B** `wang@nebius.com`（arXiv native HTML 脚注 `Correspondence to:`，420,247 B）/ #287 Feng Li **A** `fliay@connect.ust.hk`（本人主页 `mailto:`，24,341 B）；**#274 Weisen Jiang 待跟踪 → 已发信**（MetaMath 一作学生邮箱判失效 ⇒ 该论文唯一一封）；X 保持 **107**（补抓 `_onurmutlu_` / `RichardSSutton`；无登录态 ⇒ 不 follow、不假称已 follow）。⑤ 发信 **3 封**（累计 **125**，今日 9/12）：#123 VR-SparseQuant 中文 **153** 字 `SENT OK 06:04:11` / #124 Mask DINO 中文 **225** 字 `06:04:15` / #125 MetaMath 中文 **163** 字 `06:04:18`；地址发前当场复核 3/3 `200`；开头三样、问句句式互不相同；专属细节分别为「两条 2:4 稀疏流共享同一 FP4 预算 + 离线 scale-ratio 校准」「query embedding × 像素图点积、54.5 AP / 59.4 PQ」「多视角改写不改答案、GSM8K 66.4% / MATH 19.4%」。⑥ 回信率 **0 / 125**，**0 封到期**（最早 11-25，#1–#7）；通道只发不收。⑦ voice_ready **1**：Sutton 2026-11-07「Brute force computation is not enough for intelligence…」（主页内嵌 JSON × `og:description` 双源逐字一致；风险 3 条已标）；news_ready **0**（三条经典均无事件点）。⑧ 交付：`daily/2026-11-21.html`（06:00 节；div 17/17、table 14/14、tr 81/81、td 183/183、th 59/59、0 script、49,437 B）+ `daily/index.html` 当日行（307 / 287 / 125 / voice 2）+ `research/2026-11-21.md` + `PAPERS.md` #305–#307 + `AUTHORS.md` #286–#287 + `发送记录.md` §06:0x + #123–#125 行 + drafts/bodies 各 3。⑨ 记忆维护：把 11-20 的 09:0x / 06:0x / 03:0x 三条长流水 fold 至 `daily-memories-research/2026-11-20.md`（原文不改）。




- **2026-11-21（本地 00:0x · 00:00 时窗 · 🅰 A 轨 +3（今日 3/5）＋ 🅱 B 轨第七十八轮 +3 → 299 ＋ 作者网 +4 → 280 ＋ 3 封（累计 119）＋ 回信率 0/119）** —— **第二百二十四轮**：① 网络：`cat:cs.CL`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**，与 11-20 的 15:00 / 18:00 / 21:00 逐字相同 ⇒ 公告批本窗未前进；`x.com` 经 `127.0.0.1:7897` **`000`**，Mihomo `systemctl is-active`=active 但出口不通 ⇒ voice_ready 0。② A 轨 **+3（今日 3/5）**：AutoMaster `2611.26510`（Skill-FT 用自然语言技能抑制教师轨迹坏习惯，AutoMaster 闭环；4B/9B × Terminal/Search/SWE 比 vanilla SFT 平均 **+1.42–8.99 pp**，且 SFT 保留 skill 前缀在六个设置全部更好）/ MemFolder `2611.26427`（RecordFolder 实体锚点折叠 + ContextFolder 紧凑编码；Mem0 上 **50% 记录保留 99.0%** 平均性能、比最强基线 +1.9 pp）/ HiSA `2611.26363`（按 token 位置静态无参规则做 RoPE 隐藏维稀疏，只算约 **1/3 q·k**，训练不降反升，FA3 kernel + 代码开源）；三 ID 在 `SEEN.md` / `papers.jsonl` / 近 7 天 `daily/` **0 命中**。③ B 轨 **+3 → 299**：Horovod `1802.05799`（**1,619**，预印本；ring-allreduce + TF 最少改写）/ Deformable DETR `2010.04159`（**8,952**，`comment`=ICLR 2021 Oral；参考点稀疏采样、少 10× epoch、小目标更好）/ SigLIP 2 `2502.14786`（**1,832**，预印本；caption + 自监督 + 在线治理、原生宽高比/多分辨率）；arXiv `id_list` 单篇 3/3 `200` + atom + OpenAlex 3/3 `200`（查询日 2026-11-21）；PDF 30 s 内未下完 ⇒ 数字用 arXiv 摘要并标「未做 PDF 逐页复核」。④ 作者网 **+4 → 280**：#277 Xizhou Zhu **B** `zhuwalter@sensetime.com`（ar5iv HTML `200` / 267,916 B 脚注；2020 年地址疑失效 ⇒ 只建档不发）/ #278 Michael Tschannen **未找到**（`tschannen.github.io` `404`）/ #279 Xiaohua Zhai **未找到**（`xiaohuazhai.com` `000`）/ #280 Alexander Sergeev **未找到**（论文无邮箱）；**X 保持 107**（代理 000，不猜 handle）。⑤ 发信 **3 封**（累计 **119**）：#117 NeRF（`me@bmild.com`，英文 **181** 词，`SENT OK 00:04:19`）/ #118 Faster R-CNN（`ross.girshick@gmail.com`，**178** 词，`00:04:21`）/ #119 Quiet-STaR（`eric@humansand.ai`，**182** 词，`00:04:24`）；三地址发前当场复核（`bmild.github.io` 12,088 B / `~rbg/` 7,882 B / `ezelikman.github.io` 19,986 B，均 `200` + `mailto:` 明文）；落款均两行其后无行、正文无项目名、开头句与问句句式互不相同。⑥ 回信率 **0 / 119**，**0 封到期**（最早 2026-11-25，#1–#7）；`replies/` 只有 `README.md` 与诊断文档；通道只发不收。⑦ voice_ready **0** / news_ready **0**（X 000；三篇 A 轨均方法类、无大众事件点）。⑧ 交付：`daily/2026-11-21.html`（3 篇 + B 轨表 + 作者表 + 信件表 + 6 线建议 + 附录；div 11/11、table 7/7、tr 34/34、td 75/75、th 32/32、0 script、**19,289 B**）+ `daily/index.html` 当日行（tr +1 / td +5，平衡实测）+ `research/2026-11-21.md` + `SEEN.md` +3 + `papers.jsonl` +3 + `PAPERS.md` #297–#299 + `AUTHORS.md` #277–#280 + `发送记录.md` §00:0x + #117–#119 行。⑨ 记忆维护：把 11-20 15:00 的长流水原文 fold 至 `daily-memories-research/2026-11-20.md`（原文不改），MEMORY 保持 **28.6 KB**（<32 KB）。

- **更早轮次 2026-11-20（12:0x / 18:0x）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-20.md`「归档 · MEMORY 滚动（第八十二轮折出）」。

- **2026-11-19（本地 21:0x · 21:00 时窗）** —— 第二百一十五轮（B 轨 +4 → 264 / 作者网 245 / 信 0）；原文已 fold 至 `daily-memories-research/2026-11-19.md`「归档 · MEMORY 滚动（第七十九轮折出）」。



- **2026-11-18（本地 12:1x · 12:00 时窗）** —— **第二百零三轮**：B 轨 +3 → 222 / 作者网 203 / 信 90 / H4 启动；细节已 fold 至 `daily-memories-research/2026-11-18.md`。

- **更早轮次（2026-11-12 ~ 2026-11-16，r152–r183）**：原文已按 §5 滚动归档 → `daily-memories-research/` 各日文件的「归档 · MEMORY 滚动」段（2026-11-13 / 14 / 15 / 16 等），此处只留指针，勿以指针替代结论。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
