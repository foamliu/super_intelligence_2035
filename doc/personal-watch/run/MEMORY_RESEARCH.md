# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```

PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r236 · 本地 2026-11-22 09:0x · 09:00 时窗：A 轨今日 5/5 已满（0 新收）＋ B 轨 +3 → 335 ＋ 作者网 +2 → 306 ＋ 发信 3 封 → 137（今日 9/12）＋ 回信率 0/137]
  ① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）**`200` / 109,971 B / 40 entry / atom**；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 15 窗未前进**，仍在 72h 窗内）⇒ A 轨 5/5 不凑第 6 篇。
  ② B 轨 **+3 → 335**（文生图三件套）：unCLIP / DALL·E 2 `2204.06125`（**10,659**，preprint；CLIP 嵌入先验 + diffusion 解码，AR vs diffusion prior）/ Parti `2206.10789`（**1,827**，OpenAlex article = TMLR；ViT-VQGAN 离散 token 纯自回归，20B，零样本 FID 7.23 / 微调 3.22，P2 1600+）/ CFG `2207.12598`（**7,405**，preprint，`comment` = NeurIPS 2021 Workshop 短版；条件/无条件联合训练 + score 线性组合）；arXiv `id_list` `200` + atom（7,556 B / 3 entry；一次 `429` 限速重试成功）+ abs 3/3 `200`（40,571 / 45,080 / 41,707 B）+ OpenAlex 3/3 `200`；三 ID 三处查重 0 命中（Switch Transformer / QLoRA / PagedAttention / RoPE / AdamW / GPT-4 / Toolformer / WebArena / GAIA / DeepSeek-V3 / Qwen2.5 已在表内 ⇒ 剔除）。
  ③ 作者网 **+2 → 306**：#305 Jiahui Yu（`jiahuiyu@google.com`，ar5iv 613,481 B 首页邮箱块；X `@jiahuiyu` 双源；主页 `jiahuiyu.com` `200` / 23,467 B 无邮箱）/ #306 Aditya Ramesh（`aramesh@openai.com`，ar5iv 274,460 B；X 未找到——`@adityaramesh` 实为他人）。X 已核验 **117**。
  ④ 发信 **3 封（#135 / #136 / #137，累计 137，今日 9/12）**：#135 Ramesh 英文 **197** 词 `SENT OK 09:05:25`；#136 Jiahui Yu 汉字 **252** `09:05:27`；#137 Salimans 荷兰语问候 + 英文 **189** 词 `09:05:29`；发前 ar5iv 3/3 `200` 且页内邮箱逐字复核；落款两行；开头句 / 问句零共用；三地址均为 2022 年论文内地址 ⇒ 已标注送达率不可验证。
  ⑤ 回信率 **0 / 137**，**0 封到期**（最早 2026-11-25，#1–#7 ⇒ 距今 3 天）；`replies/` 仍只有 `README.md`；通道只发不收。
  ⑥ voice_ready **0** / news_ready **0**（B 轨三条均 2022 年奠基论文，非本窗事件点）。
  ⑦ 交付：`daily/2026-11-22.html`（09:00 节：why + B 轨 3 行 #333–#335 + 作者 / 信件段 + 建议 4 条 + 附录 7 行 + footer）+ `daily/index.html` 当日行（335 · 306 · 117 · 137 · 0/137）+ `research/2026-11-22.md` 09:00 节 + `PAPERS.md` #333–#335 + `AUTHORS.md` #305–#306 + `发送记录.md` §09:0x + drafts / bodies 各 3。

当前动作:     ✅ 09:00 时窗闭环：A 轨保持 5/5（不凑数），B 轨 +3（unCLIP / Parti / CFG），作者网 +2（Jiahui Yu / Aditya Ramesh），3 封信发出（累计 137），回信率 0/137。
下一步:       ① 12:00 时窗：A 轨今日 5/5 已满 ⇒ 继续 B 轨 / 作者网 / 回信诊断；② B 轨候选：HBM / JEDEC 一手、QK-clip 实现报告、视频时序建模（Latte `2401.12168` 先核 ID 与被引）、生成评测人评一致性（HPSv2 / ImageReward）；③ 视需要从新作者补邮箱建草稿（待发队列空）；④ 11-25 首批到期 → #1–#7 转 `无应答(>14d)`；⑤ 运维：发件显示名 / SMTP 只发不收 / 任务书 44 KB 超红线。
补推记录:     2026-11-22 09:1x · 本轮 commit 前 `git pull --rebase --autostash`；若 push 被拒按 `fetch + rebase origin/main` 重试（最多 5 次），不 `add -A`。
本轮新增:     A 轨 0（今日 5/5）· B 轨 +3（335）· 作者网 +2（306）· 作者信 +3（137）· voice_ready 0 · news_ready 0 · 回信率 0/137 · X 已核验 117
阻塞:         ① 🔴 发件显示名 `AI+EDA 招聘 · 自动`（最可能的 0 回信原因），需运维改配置；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到；③ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且 agent 只读 ⇒ 需授权；④ 本轮三封信地址均为 2022 年论文内地址（OpenAI / Google 不公开个人邮箱）⇒ 送达率不可验证；⑤ 无新增其他阻塞。
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
- **上次采集窗口**：`2026-11-22 09:0x`（**第二百三十六轮 · 09:00 时窗**：A 轨今日 5/5 已满（0 新收）；`cat:cs.CL` `200` / 109,971 B / 40 entry；最新 `published` **`2026-11-19T18:57:25Z`**（连续第 15 窗未前进）；B 轨第八十九轮 +3 → 335）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`363` 篇（11-20 A 轨 +5：`2611.24849` / `2611.24844` / `2611.24071` / `2611.24809` / `2611.24540`；`SEEN.md` 为唯一防重台账）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**335 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**七十四轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**306 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-22（本地 09:0x · 09:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十九轮 +3 → 335 ＋ 作者网 +2 → 306 ＋ 信 3 封（累计 137，今日 9/12）＋ 回信率 0/137）** —— **第二百三十六轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 15 窗未前进**，仍在 72h 窗内）⇒ A 轨不凑第 6 篇。② B 轨 **+3 → 335**（文生图三件套）：unCLIP / DALL·E 2 `2204.06125`（**10,659**，preprint；CLIP 嵌入先验 + diffusion 解码，AR vs diffusion prior，零样本语言引导编辑）/ Parti `2206.10789`（**1,827**，OpenAlex `type=article` = TMLR；ViT-VQGAN 离散 token 纯自回归，编码器-解码器 20B，零样本 FID **7.23** / 微调 **3.22**，PartiPrompts **1600+**）/ CFG `2207.12598`（**7,405**，preprint，`comment` = NeurIPS 2021 Workshop 短版；条件 + 无条件联合训练，score 线性组合，无需分类器）；arXiv `id_list` `200` + atom（7,556 B / 3 entry，一次 `429` 后按 ≥3 s 限速重试成功）+ abs 3/3 `200`（40,571 / 45,080 / 41,707 B，`citation_title` 逐字）+ OpenAlex 3/3 `200`；三 ID 三处查重 0 命中（Switch Transformer / QLoRA / PagedAttention / RoPE / AdamW / GPT-4 / Toolformer / WebArena / GAIA / DeepSeek-V3 / Qwen2.5 已在表内 ⇒ 剔除）。③ 作者网 **+2 → 306**：#305 Jiahui Yu（邮箱 `jiahuiyu@google.com` 取自 ar5iv 613,481 B 首页邮箱块；X `@jiahuiyu` 双源 `200` / 191,153 B + bio 自述 Startup / 前 OpenAI / 前 DeepMind；主页 `jiahuiyu.com` `200` / 23,467 B 无邮箱）/ #306 Aditya Ramesh（邮箱 `aramesh@openai.com` 取自 ar5iv 274,460 B；X 未找到——`@adityaramesh` bio 为 `A+ : Indic : …` 系他人，`@tim_salimans` `404`、`@jonathanho` 为 Chicago 另一账号 ⇒ 均不记）；X 已核验 **117**。④ 发信 **3 封**（#135 Ramesh 英文 **197** 词 `SENT OK 09:05:25` / #136 Jiahui Yu 汉字 **252** `09:05:27` / #137 Salimans 荷兰语问候 + 英文 **189** 词 `09:05:29`；发前 ar5iv 全文页 3/3 `200` 且页内邮箱逐字；落款两行；开头句 / 问句零共用；三地址均 2022 年论文内地址 ⇒ 标注送达率不可验证），累计 **137**、今日 9/12、待发队列空。⑤ 回信率 **0/137**，0 封到期（最早 11-25）。⑥ voice_ready 0 / news_ready 0（2022 年奠基论文，非本窗事件点）。⑦ 交付：`daily/2026-11-22.html` 09:00 节（why + 3 行 + 作者 / 信件段 + 建议 4 条 + 附录 7 行 + footer）+ `index.html` 当日行（335 · 306 · 117 · 137）+ `research/2026-11-22.md` 09:00 节 + `PAPERS.md` #333–#335 + `AUTHORS.md` #305–#306 + `发送记录.md` §09:0x + drafts/bodies 各 3。

- **2026-11-22（本地 06:0x · 06:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十八轮 +3 → 332 ＋ 作者网 +2 → 304 ＋ 信 2 封（累计 134，今日 6/12）＋ 回信率 0/134）** —— **第二百三十五轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 14 窗未前进**，仍在 72h 窗内）⇒ A 轨不凑第 6 篇。② B 轨 **+3 → 332**：CogVideoX `2408.06072`（**2,181**，ICLR 2025；3D 因果 VAE + expert adaptive LayerNorm，10 秒 / 16 fps / 768×1360，2B/5B）/ Open-Sora Plan `2412.00131`（**359**，预印本；Wavelet-Flow VAE + Joint Image-Video Skiparse Denoiser + 多维数据治理）/ Spike No More `2312.16903`（**72**，<500 按「方法论常青」收；sub-layer 小 + shortcut 大两条件，PDF 首页 1.7B 约 13,000 步发散）；`id_list` `200` + atom（7,780 B / 3 entry）+ OpenAlex 3/3 `200`；三 ID 三处查重 0 命中（FineWeb / Phi-3 / AgentBench 已在表内 ⇒ 剔除）。③ 作者网 **+2 → 304**：#303 Sho Takase 邮箱 `sho.takase@lycorp.co.jp`（PDF v2 通讯行）、主页 `200` / 22,054 B 无邮箱、X 未找到 / #304 唐杰 邮箱 `jietang@tsinghua.edu.cn`（主页 `200` / 217,822 B 明文）、X `@jietang` 双源 `200` / 180,469 B + bio；X **116**。④ 发信 **2 封**（#133 日文 281 字 `SENT OK 06:03:43` / #134 汉字 185 `06:03:48`；发前地址 2/2 复核；落款两行；问句零共用），累计 **134**、今日 6/12、待发队列空。⑤ 回信率 **0/134**，0 封到期（最早 11-25）。⑥ voice_ready 0 / news_ready 0。⑦ 交付：`daily/2026-11-22.html` 06:00 节 + `index.html` 当日行（332 · 304 · 116 · 134）+ `research/2026-11-22.md` 06:00 节 + `PAPERS.md` #330–#332 + `AUTHORS.md` #303–#304 + `发送记录.md` §06:0x + drafts/bodies 各 2。

- **2026-11-22（本地 03:0x · 03:00 时窗 · 🅰 A 轨 +2（今日 5/5）＋ 🅱 B 轨第八十七轮 +3 → 329 ＋ 作者网 +2 → 302 ＋ 信 1 封（累计 132，今日 4/12）＋ 回信率 0/132）** —— **第二百三十四轮**：① 网络：`cat:cs.CV&max_results=40`（`--noproxy '*'`）`200` / **107,965 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:59:57Z`**（公告批仍未前进；与 00:00 的 cs.CL 上界 `18:57:25Z` 同批，仍在 72h 窗内）。② A 轨 **+2（今日 5/5）**：WeMM-Video `2611.26409`（cs.CV；2B/4B/9B/35B-A3B omni-modal，约 1.2T token 渐进预训练 + 多教师 OPD / MrDPO / 专家 RL，120+ 基准，9B 超过 Qwen3-Omni-30B-A3B-Instruct）/ TRQ `2611.26334`（cs.CV；视频 DiT KV cache 2-bit 量化，2×2 平面旋转树每颗 2 bit + 共享 Hadamard，在线无梯度，VBench 主体一致性 90.38→92.02 / 86.33→87.61）；五 ID 三处查重 0 命中；abs 2/2 `200`（43,294 / 41,727 B）且 `citation_title` 逐字一致。③ B 轨 **+3 → 329**：EVA-02 `2303.11331`（**683**，Image and Vision Computing）/ Sequence Parallelism `2105.13120`（**258**，ACL 2023；未达 500 按「开创范式 / 常青」入选）/ ViT registers `2309.16588`（**821**，ICLR 2024）；`id_list` `200` + atom（7,486 B / 3 entry）+ abs 3/3 `200`（43,667 / 44,844 / 40,626 B）+ OpenAlex 3/3 `200`；同批排除已收 Transfusion / Janus / Ring Attention。④ 作者网 **+2 → 302**：#301 Timothée Darcet **无邮箱**（`timdarcet.github.io` `200` / 2,363 B）但 X `@timdarcet` `200` / 181,126 B（`og:title` + `og:description` 双源）/ #302 Changli Tang（清华大学电子系博士生；WeMM-Video 一作）无邮箱（`github.com/TCL606` `200` / 196,169 B）、X `@TCL606` `404` ⇒ 只建档；反例 `@xgwang` 实为 Montréal 的 3 followers 账号 ⇒ 不记；X 已核验 **115**。⑤ 发信 **1 封**（#132 Show-o / Mike Zheng Shou，汉字 203，`SENT OK 03:02:36`；发前 `sites.google.com/view/showlab` `200` / 162,233 B 且页内邮箱逐字；落款两行），累计 **132**、今日 4/12、待发队列清空。⑥ 回信率 **0/132**，0 封到期（最早 11-25）。⑦ voice_ready 0（未抓到可双源核验的单条推文）/ news_ready 0（五篇均方法 / 框架类，无事件点，不硬凑）。⑧ 交付：`daily/2026-11-22.html`（5/5；补 2 卡 + B 轨 3 行 + 作者 / 信件段 + 晚报变更说明 + 03:00 建议 + 附录）+ `index.html` 当日行（5/5 · 329 · 302 · 115 · 132）+ `research/2026-11-22.md` + `PAPERS.md` #327–#329 + `AUTHORS.md` #301–#302 + `发送记录.md` §03:0x + `SEEN.md`/`papers.jsonl` 2 条 + draft Show-o 回填「已发送」。

- **2026-11-22（本地 00:0x · 00:00 时窗 · 🅰 A 轨 +3（今日 3/5）＋ 🅱 B 轨第八十六轮 +3 → 326 ＋ 作者网 +2 → 300 ＋ 信 3 封（累计 131，今日 3/12）＋ 回信率 0/131）** —— **第二百三十三轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 13 窗未前进**，仍在 72h 窗内）。② A 轨 **+3**：SheetAlign `2611.26069`（cs.CL，表格 agent 三段式；Qwen3-4B 仅换接口 13.5%→29.2%，加训练 32.8%，Domain-Spreadsheet 30.1%）/ RL Can Only Reinforce `2611.26084`（cs.LG；约 35 组成功尝试为胜负各半阈值，4–256 次尝试、1.3M–85M 参数成立）/ dLoop `2611.26275`（cs.CL；Prelude–Loop–Coda 循环潜变量，TPF 折算下优于 Fast-dLLM 四项）；六 ID 三处查重 0 命中；abs 3/3 `200`（41,201 / 40,874 / 43,057 B）且 `citation_title` 逐字一致。③ B 轨 **+3 → 326**：EVA-CLIP `2303.15389`（**1,204**）/ RefinedWeb `2306.01116`（**1,221**）/ SD3 `2403.03206`（**5,735**），均 preprint；`id_list` `200` + atom（7,923 B / 3 entry）+ abs 3/3 `200`（40,797 / 41,829 / 43,894 B）+ OpenAlex 3/3 `200`；同批排除已收 Muon / Qwen2-VL / RoPE 外推 / The Pile / HumanEval / DataComp / DINOv2 / SAM / Chameleon / Emu3。④ 作者网 **+2 → 300**：#299 Robin Rombach **无邮箱**（`rombach.me` / `www.robrombach.com` 均 `000`）但 X `@robrombach` `200` / 188,334 B 且 `og:title` 逐字 / #300 Patrick Esser 邮箱·主页·X 均未找到 ⇒ 只建档；⚠️ 三处同名反例拦下：`@guipenedo`（巴西灯光从业者）、`@PatrickEsser`（= patrick goncalves）、`@EsserPatrick`（= Patrick Esser JR）⇒ 不记。⑤ 发信 **3 封**（#129 Grounding DINO 汉字 187 `00:02:06` / #130 EAGLE 汉字 200 `00:02:08` / #131 Depth Anything 汉字 241 `00:02:09`；发前地址页 3/3 `200` 且页内邮箱逐字；落款两行），累计 **131**、今日 3/12、待发余 1 封（Show-o）。⑥ 回信率 **0/131**，0 封到期（最早 11-25）。⑦ voice_ready 0（未抓到可双源核验的单条推文）/ news_ready 0（无事件点，不硬凑）。⑧ 交付：`daily/2026-11-22.html`（新建，div 11/11 · table 5/5 · tr 28/28 · td 46/46 · th 22/22 · 0 script · 0 残留 `**`）+ `index.html` 当日行（3/5 · 326 · 300 · 114 · 131）+ `research/2026-11-22.md` + `PAPERS.md` #324–#326 + `AUTHORS.md` #299–#300 + `发送记录.md` §00:0x + `SEEN.md`/`papers.jsonl` 3 条。

- **2026-11-21（本地 21:0x · 21:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十五轮 +3 → 323 ＋ 作者网 +2 → 298 ＋ 信 0 封（当日 12/12，备稿新增 1 → 待发 4）＋ 回信率 0/128）** —— **第二百三十二轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 12 窗未前进**）。② A 轨 **0 新收**（今日 5/5 已满）。③ B 轨 **+3 → 323**：Cosmos WFM `2501.03575`（**1,115**，预印本 NVIDIA）/ Show-o `2408.12528`（**739**，ICLR 2025）/ FP8-LM `2310.18313`（**171**，**&lt;500 按「方法论常青」收**）；`id_list` 单批 `200` + atom（12,215 B / 3 entry）+ abs 3/3 `200`（53,618 / 41,613 / 45,703 B）+ OpenAlex 3/3 `200`；先查重 0 命中；**写入前拦截两处候选池 ID 误记**（`2312.16873` 实测为杆状聚合物论文、`2408.12528` 实测为 Show-o ⇒ 改收 Show-o）。④ 作者网 **+2 → 298**：#297 Mike Zheng Shou **A** `mike.zheng.shou AT gmail.com`（`sites.google.com/view/showlab` 经代理 `200` / 161,838 B 页内明文）+ X `@MikeShou1` 双源 / #298 Ming-Yu Liu（劉洺堉）**无明文邮箱**（`mingyuliu.net` 7,878 B / NVIDIA 人员页 70,084 B）+ X `@liu_mingyu`；X 已核验 **113**；`@mikeshou` 为他人 ⇒ 不记。⑤ 发信 **0 封**（累计 128，当日 12/12）：新增草稿 `drafts/2408.12528.md`（中文 **217** 汉字，落款两行；专属细节 1.3B / K=8,192 / 16×16 token / 35M 图文对 500K steps / GenEval 0.68），待发共 4 封。⑥ 回信率 **0/128**，0 封到期（最早 11-25）。⑦ voice_ready 0 新增（达上限）/ news_ready 0（无本窗事件点）。⑧ 交付：`daily/2026-11-21.html` +21:00 节、`index.html` 当日行（323 / 298 / 113 / 128 / 备稿 4）、`research/2026-11-21.md` 21:00 节、`PAPERS.md` #321–#323、`AUTHORS.md` #297–#298、`发送记录.md` §21:0x、draft 1。

- **2026-11-21（本地 18:0x · 18:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十四轮 +3 → 320 ＋ 作者网 +2 → 296 ＋ 信 0 封（当日 12/12，备稿新增 1）＋ 回信率 0/128）** —— **第二百三十一轮**：① 网络：`cat:cs.CL&max_results=40`（`--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 11 窗未前进**）。② A 轨 **0 新收**（今日 5/5 已满）。③ B 轨 **+3 → 320**：Depth Anything `2401.10891`（**2,769**，CVPR 2024）/ HunyuanVideo `2412.03603`（**2,092**，预印本）/ V-JEPA `2404.08471`（**846**，TMLR）；`id_list` 单批 `200` + atom（15,089 B / 3 entry）+ abs 3/3 `200` + OpenAlex 3/3 `200`；先查重剔除已在表内的 DeepSeek-R1 / Mixtral / Self-Consistency / Ring Attention / s1 / DCLM。④ 作者网 **+2 → 296**：#295 Lihe Yang **A** `lihe.yang.cs@gmail.com`（`liheyoung.github.io` `200` / 17,151 B 页内 `mailto:`）/ #296 Hengshuang Zhao **A** `hszhao[at]cs.hku.hk`（HKU 页 `200` / 36,107 B 明文）；X 保持 **111**（`@LiheYoung` / `@hszhao` 均 `404` ⇒ 不记）。⑤ 发信 **0 封**（累计 128，当日 12/12）：新增草稿 `drafts/2401.10891.md`（中文 **241** 汉字），待发共 3 封。⑥ 回信率 **0/128**，0 封到期（最早 11-25）。⑦ voice_ready 0 新增（达上限）/ news_ready 0。⑧ 交付：`daily/2026-11-21.html` +18:00 节、`index.html` 当日行（320 / 296 / 111 / 128 / 备稿 3）、`research/2026-11-21.md` 18:00 节、`PAPERS.md` #318–#320、`AUTHORS.md` #295–#296、`发送记录.md` §18:0x、draft 1。

- **2026-11-21（本地 15:0x · 15:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十三轮 +3 → 317（Grounding DINO 2,415 / AndroidWorld 525 / EAGLE 499）＋ 作者网 +2 → 294（Shilong Liu A 级 / Hongyang Zhang A 级，X 已核验 111）＋ 信 0 封（当日 12/12 硬上限，备 2 封中文草稿 198 / 209 汉字）＋ 回信率 0/128，0 封到期；两处 ID 误记写入前拦截（2303.19588⇒2303.05499、2502.05907 实为 EvolvingAgent）** —— 核验：arXiv `id_list` `200` + atom、abs 3/3 `200`、OpenAlex 3/3 `200`；`x.com` 经代理 `200`，`@atasteoff` `404` 不记；交付 `daily/2026-11-21.html` +15:00 节、`index.html` 当日行、`PAPERS.md` #315–#317、`AUTHORS.md` #293–#294、`发送记录.md` §15:0x、draft 2 个。

- **2026-11-21（本地 12:0x · 12:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十二轮 +3 → 314 ＋ 作者网 +2 → 292 ＋ 1 封信（累计 128，今日 12/12 满）＋ 回信率 0/128）** —— **第二百二十九轮**：① 网络：`cat:cs.CL`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（**连续第 9 窗逐字相同**）。② A 轨 **0 新收**（今日 5/5 已满，不凑第 6 篇）。③ B 轨 **+3 → 314**：Grounding DINO 1.5 `2405.10300`（**237**，按「本领域权威」，预印本）/ CodeAct `2402.01030`（**470**，按「方法论常青」，arXiv `comment` = ICML 2024、OpenAlex 仍记 preprint）/ Native Sparse Attention `2502.11089`（**674**，≥500 直接满足，OpenAlex source = ACL 2025）；arXiv `id_list` 单批 **`200` + atom**（10,529 B / 3 entry）+ abs 页 **3/3 `200`**（44,192 / 44,230 / 44,015 B）+ OpenAlex **3/3 `200`**。⚠️ **写入前拦截 ID 误记**：原计划「Small-scale proxies」按记忆写作 `2209.14375`，`id_list` 实测为 *Improving alignment of dialogue agents via targeted human judgements* ⇒ 真 ID `2309.14322` **已在表内 #226** ⇒ 整条剔除、换收 NSA。④ 作者网 **+2 → 292**：#291 Xingyao Wang（UIUC / OpenHands；**无明文邮箱** —— GitHub `email=null`、`xwang.dev` 邮箱为 Cloudflare 编码，不反解）/ #292 Peter J. Liu（无现行页；据 X 简介曾在 Google Brain / DeepMind）；X 已核验 **110**（`@xingyaow_` `200` / 170,026 B、`@peterjliu` `200` / 162,821 B，均 `og:title`+`og:description` 双源）；`@xingyaoww` / `@m_wortsman` **`404`**、`@Wortsman` 为另一人 ⇒ 未收。⑤ 发信 **1 封**（累计 **128**，今日 **12/12** 达每日硬上限）：#128 **Vidya A. Chhabria** `vidyachhabria@asu.edu`（ASU profile 当场复核 `200` / 124,745 B，页内明文 ⇒ **A 级**）/ `2405.06676` EDA Corpus（B 轨 #264，末位 / 通讯）/ 英文 **200** 词（`wc -w` 实测）/ `SENT OK 12:03:31`；**已到日上限 ⇒ 后续时窗不借额度**。三问各指一处决策：Table II 的 **28 条失败脚本**「崩 vs 跑通改错对象」占比（executor vs state-diff）／增强改写是否与原文**同侧**划分（否则 22/50 只当下界）／**258 database vs 138 flow** 的小语料配比。专属细节：Table I `198+392=590`、`395+545=943`、Table II `22 true / 28 false`、`95/5`。⑥ 回信率 **0 / 128**，**0 封到期**（最早 11-25）；`replies/` 仍只有 `README.md`。⑦ voice_ready **0 新增**（今日已 2 条，达上限）/ news_ready **0**。⑧ 交付：`daily/2026-11-21.html`（+12:00 节；69,742 B，div 18/18、table 18/18、tr 108/108、td 253/253、th 74/74、0 script、0 残留 `**`）+ `index.html` 当日行（314 / 292 / 110 / 128）+ `research/2026-11-21.md` 12:00 节 + `PAPERS.md` #312–#314 + `AUTHORS.md` #291–#292（#245 → 已发信）+ `发送记录.md` §12:0x + 回信表 #123–#128。
- **2026-11-21（本地 09:00 · 09:00 时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`「归档 · MEMORY 滚动（第八十七轮后折出）」；结论不变，勿以指针替代原文。

- **2026-11-21（本地 09:00 · 09:00 时窗）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-21.md`「归档 · MEMORY 滚动（第八十七轮后折出）」；结论不变，勿以指针替代原文。




- **2026-11-21（本地 00:0x · 00:00 时窗 · 🅰 A 轨 +3（今日 3/5）＋ 🅱 B 轨第七十八轮 +3 → 299 ＋ 作者网 +4 → 280 ＋ 3 封（累计 119）＋ 回信率 0/119）** —— **第二百二十四轮**：① 网络：`cat:cs.CL`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**，与 11-20 的 15:00 / 18:00 / 21:00 逐字相同 ⇒ 公告批本窗未前进；`x.com` 经 `127.0.0.1:7897` **`000`**，Mihomo `systemctl is-active`=active 但出口不通 ⇒ voice_ready 0。② A 轨 **+3（今日 3/5）**：AutoMaster `2611.26510`（Skill-FT 用自然语言技能抑制教师轨迹坏习惯，AutoMaster 闭环；4B/9B × Terminal/Search/SWE 比 vanilla SFT 平均 **+1.42–8.99 pp**，且 SFT 保留 skill 前缀在六个设置全部更好）/ MemFolder `2611.26427`（RecordFolder 实体锚点折叠 + ContextFolder 紧凑编码；Mem0 上 **50% 记录保留 99.0%** 平均性能、比最强基线 +1.9 pp）/ HiSA `2611.26363`（按 token 位置静态无参规则做 RoPE 隐藏维稀疏，只算约 **1/3 q·k**，训练不降反升，FA3 kernel + 代码开源）；三 ID 在 `SEEN.md` / `papers.jsonl` / 近 7 天 `daily/` **0 命中**。③ B 轨 **+3 → 299**：Horovod `1802.05799`（**1,619**，预印本；ring-allreduce + TF 最少改写）/ Deformable DETR `2010.04159`（**8,952**，`comment`=ICLR 2021 Oral；参考点稀疏采样、少 10× epoch、小目标更好）/ SigLIP 2 `2502.14786`（**1,832**，预印本；caption + 自监督 + 在线治理、原生宽高比/多分辨率）；arXiv `id_list` 单篇 3/3 `200` + atom + OpenAlex 3/3 `200`（查询日 2026-11-21）；PDF 30 s 内未下完 ⇒ 数字用 arXiv 摘要并标「未做 PDF 逐页复核」。④ 作者网 **+4 → 280**：#277 Xizhou Zhu **B** `zhuwalter@sensetime.com`（ar5iv HTML `200` / 267,916 B 脚注；2020 年地址疑失效 ⇒ 只建档不发）/ #278 Michael Tschannen **未找到**（`tschannen.github.io` `404`）/ #279 Xiaohua Zhai **未找到**（`xiaohuazhai.com` `000`）/ #280 Alexander Sergeev **未找到**（论文无邮箱）；**X 保持 107**（代理 000，不猜 handle）。⑤ 发信 **3 封**（累计 **119**）：#117 NeRF（`me@bmild.com`，英文 **181** 词，`SENT OK 00:04:19`）/ #118 Faster R-CNN（`ross.girshick@gmail.com`，**178** 词，`00:04:21`）/ #119 Quiet-STaR（`eric@humansand.ai`，**182** 词，`00:04:24`）；三地址发前当场复核（`bmild.github.io` 12,088 B / `~rbg/` 7,882 B / `ezelikman.github.io` 19,986 B，均 `200` + `mailto:` 明文）；落款均两行其后无行、正文无项目名、开头句与问句句式互不相同。⑥ 回信率 **0 / 119**，**0 封到期**（最早 2026-11-25，#1–#7）；`replies/` 只有 `README.md` 与诊断文档；通道只发不收。⑦ voice_ready **0** / news_ready **0**（X 000；三篇 A 轨均方法类、无大众事件点）。⑧ 交付：`daily/2026-11-21.html`（3 篇 + B 轨表 + 作者表 + 信件表 + 6 线建议 + 附录；div 11/11、table 7/7、tr 34/34、td 75/75、th 32/32、0 script、**19,289 B**）+ `daily/index.html` 当日行（tr +1 / td +5，平衡实测）+ `research/2026-11-21.md` + `SEEN.md` +3 + `papers.jsonl` +3 + `PAPERS.md` #297–#299 + `AUTHORS.md` #277–#280 + `发送记录.md` §00:0x + #117–#119 行。⑨ 记忆维护：把 11-20 15:00 的长流水原文 fold 至 `daily-memories-research/2026-11-20.md`（原文不改），MEMORY 保持 **28.6 KB**（<32 KB）。

- **更早轮次 2026-11-20（12:0x / 18:0x）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-20.md`「归档 · MEMORY 滚动（第八十二轮折出）」。

- **2026-11-19（本地 21:0x · 21:00 时窗）** —— 第二百一十五轮（B 轨 +4 → 264 / 作者网 245 / 信 0）；原文已 fold 至 `daily-memories-research/2026-11-19.md`「归档 · MEMORY 滚动（第七十九轮折出）」。



- **2026-11-18（本地 12:1x · 12:00 时窗）** —— **第二百零三轮**：B 轨 +3 → 222 / 作者网 203 / 信 90 / H4 启动；细节已 fold 至 `daily-memories-research/2026-11-18.md`。

- **更早轮次（2026-11-12 ~ 2026-11-16，r152–r183）**：原文已按 §5 滚动归档 → `daily-memories-research/` 各日文件的「归档 · MEMORY 滚动」段（2026-11-13 / 14 / 15 / 16 等），此处只留指针，勿以指针替代结论。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
