# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```

PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r217 · 本地 2026-11-20 03:0x · 03:00 时窗：A 轨补齐 5/5（+2，从同一 40-entry 公告批、72h 内未收录条目选）+ B 轨 +4 → 272 + 作者网 +4 → 251 + 发信 3 → 109 + 回信率 0/109]
  ① 网络：`cat:cs.CL`（`https` + `--noproxy '*'`）`200` / **94,399 B / 40 entry** / `application/atom+xml`；最新 `published` 仍 **`2026-11-18T18:56:12Z`** ⇒ **连续第 6 窗未前进**；`id_list=2611.24809,2611.24540` ⇒ `200` / 4,464 B / 2 entry；abs 页 2/2 `200`；arXiv 原生 HTML 2/2 `200`（966,440 / 122,470 B）；`x.com` 经代理 `200`（较前几窗 `000` 有变化），但未做推文双源核验 ⇒ voice 仍 0。
  ② A 轨 **5/5**（03:00 补 2）：FlashMorph2 `2611.24809`（cs.CL；复旦 / ByteDance Seed / NTU；指出 FlashMorph 两个 off-policy 失配；端到端评估离散架构 + 联合优化层选择与权重；Qwen3-0.6B/1.7B/8B + Qwen3-30B-A3B + Lightning/GLA/GDN；RULER +2.42 / LongBench +1.08 / recall +0.76；层选择 0.72–3.57 GPU 小时，8.4–20.8× vs HALO、560–854× vs KL-LS）/ Ingredients `2611.24540`（cs.CL；JPMorgan Chase LLM Suite，单作者；8 层 51,455,488 参数 / 词表 50,304 / 1,024 token / FineWeb / 名义 300M token；五开关 32 次核心训练两种子；MoE+Muon+GDN 增益最大且多数可叠加，额外归一化有效，匹配参数的注意力门 ≈0；全开 3.6792/3.6750 nats；95% 参考边界 ±0.0043 nats；MoE 臂 161.3M 总参/51.6M 激活；另记一次未来 token 泄漏被奇偶置换测试发现）。
  ③ B 轨 **+4 → 272**：C4 文档化 `2104.08758`（**990**，EMNLP 2021 pp. 1286–1305；365M 文档 / 156B token / 305 GB；无 blocklist 395M/198B/380 GB；无清洗 1.1B/1.4T/2.3 TB；blocklist 不成比例删少数群体文本）/ ConvNeXt `2201.03545`（**13,910**，CVPR 2022 pp. 11966–11976；300 epoch / AdamW 4e-3 / batch 4096 / wd 0.05 / LayerScale 1e-6 / EMA；T 版 4.5 GFLOPs 82.1% vs Swin-T 81.3%；XL 384² 87.8%）/ Grokking `2201.02177`（**967**；mod 97、50% 数据、10³ 步训练 vs 10⁶ 步验证；25–30% 数据附近 −1% 数据 → 泛化中位时间 +40–50%；weight decay 最有效）/ Mirage `2304.15004`（**1,116**，NeurIPS 2023 pp. 55565–55581；BIG-Bench 约 92% 的涌现只在 multiple-choice grade / exact match 下出现；per-token CE 幂律平滑）。abs 4/4 `200` + OpenAlex 4/4 `200` + ar5iv 4/4 `200`（207,799 / 476,499 / 106,203 / 151,070 B）。
  ④ 作者网 **+4 → 251**（#248 Zhuang Liu 刘壮 **A 级** `zhuangl@princeton.edu`（`liuzhuang13.github.io` 页内明文，200 / 42,671 B）+ X `@liuzhuang1234` 仅登记未核验 / #249 Sanmi Koyejo **A 级** `sanmi@cs.stanford.edu`（主页明文，200 / 7,785 B）/ #250 Biswa Sengupta **B 级** `biswa.sengupta@jpmorgan.com`（arXiv HTML 正文，200 / 122,470 B）/ #251 Alethea Power **C 级** `alethea@openai.com`（2022 年 comment，不发））；Rylan Schaeffer 主页无可读邮箱、Jesse Dodge 两个主页均 404 ⇒ 只登记不猜地址；X 已核验保持 **106**。
  ⑤ 发信 **3 封 → 109**（今日 5/12）：#107 刘壮（`2201.03545` ConvNeXt，中文 **194** 字，`SENT OK 03:03:13`，A 级）/ #108 Koyejo（`2304.15004` Mirage，英文 **171** 词，`03:03:18`，A 级）/ #109 Sengupta（`2611.24540` Ingredients，英文 **161** 词，`03:03:18`，B 级）；落款两行其后无行、正文无项目名 / 雇主、同轮三封开头与问题句式零共用。
  ⑥ 回信率 **0 / 109**，**0 封到期**（最早 2026-11-25，#1–#7）；`replies/` 仍无摘录；通道只发不收。
  ⑦ voice_ready **0**（X 可达但未双源核验）/ news_ready **0**（五篇无事件点；经典侧为 2021–2023 旧作）。
  ⑧ 交付：`daily/2026-11-20.html`（5 篇 A 轨卡片 + B #269–#272 + 作者 #248–#251 + 发信表 + 两轮六线建议 + voice/news 0 + 附录）+ `daily/index.html` 当日行 + `research/2026-11-20.md`（§4–§8）+ `SEEN.md` / `papers.jsonl` +2 + `PAPERS.md` #269–#272（快照 272）+ `AUTHORS.md` #248–#251（计数 251）+ `发送记录.md` §03:0x + 三份 draft 状态改「已发送」。
  ⑨ 查重与纠错：A 轨两 ID 在 `SEEN.md` / `papers.jsonl` **0 命中**；B 轨四 ID 在 `PAPERS.md` 全量正则 **0 命中**；⚠️ ar5iv 对新论文返回 **307 空体** ⇒ 改用 arXiv 原生 HTML（已记 ERROR_COUNT）。

当前动作:     ✅ 03:00 闭环：A 轨补齐 5/5（混合注意力层选择 / 小模型重复因子实验），B 轨 +4（语料审计 / ConvNeXt / Grokking / 指标幻象），作者网 +4，发出 3 封（中 1 / 英 2）。
下一步:       ① 06:00：今日 5/5 已满，A 轨不再收；只核对公告批是否前进并记台账；② B 轨下轮候选：HBM/JEDEC 一手、训练 spike 侧、合成数据自举、EDA 可执行判分第二篇、AIMv2/DFN 与 ConvNeXt 对照；③ 发信下轮可再发 ≤3（今日 5/12），优先 A 级且未触达的机构；④ 11-25 首批到期 → #1–#7 转 `无应答(>14d)`；⑤ 运维：SMTP 只发不收 / PDF 传输截断仍在。
本轮新增:     A 轨 +2（5/5）· B 轨 +4（272）· 作者网 +4（251）· 作者信 +3（109）· voice_ready 0 · news_ready 0 · 回信率 0/109 · X 已核验 106
阻塞:         ① 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到，最需运维介入；② PDF 下载截断未复测（本轮走 arXiv 原生 HTML）；③ A 轨公告批连续 6 窗未前进（最新仍 2026-11-18T18:56:12Z）⇒ 若 06:00 仍不动，今日 5/5 即为该批上限；④ `WATCH_RESEARCH_TASK.md` 体积超红线且 agent 只读 ⇒ 需授权。
ERROR_COUNT:  114（本轮 +1：ar5iv 对新论文 `2611.24809` / `2611.24540` 返回 `307` / 0 B ⇒ 改用 arXiv 原生 HTML `200`，已记入附录；另 `x.com` 代理由 `000` 变 `200`，但未据此放宽 voice 核验口径）


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
- **上次采集窗口**：`2026-11-20 03:0x`（**第二百一十七轮 · 03:00 时窗**：`cat:cs.CL` `200` / 94,399 B / 40 entry；最新 `published` **`2026-11-18T18:56:12Z`**（**连续 6 窗未前进**）；A 轨补齐 **5/5**（新增 `2611.24809` / `2611.24540`）；B 轨 **第七十一轮 +4 → 272**；作者网 **251**；X 已核验 **106**；发信 **109**（今日 5/12）；回信率 **0/109**；voice_ready 0；news_ready 0）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`363` 篇（11-20 A 轨 +5：`2611.24849` / `2611.24844` / `2611.24071` / `2611.24809` / `2611.24540`；`SEEN.md` 为唯一防重台账）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**264 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**六十九轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**245 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-20（本地 03:0x · 03:00 时窗 · 🅰 A 轨补齐 5/5（+2）＋ 🅱 B 轨第七十一轮 +4 → 272 ＋ 作者网 +4 → 251 ＋ 3 封信（累计 109）＋ 回信率 0/109）** —— **第二百一十七轮**：① 网络：`cat:cs.CL` `200` / 94,399 B / 40 entry，最新 `published` 仍 `2026-11-18T18:56:12Z`（连续第 6 窗未前进）；`id_list=2611.24809,2611.24540` `200` / 4,464 B / 2 entry；abs 2/2 + arXiv 原生 HTML 2/2 `200`（966,440 / 122,470 B）；`x.com` 代理 `200`（前几窗为 `000`），未做推文双源核验 ⇒ voice 0。② A 轨补 2 篇：FlashMorph2 `2611.24809`（RULER +2.42 / LongBench +1.08 / recall +0.76；层选择 0.72–3.57 GPU 小时；8.4–20.8× vs HALO、560–854× vs KL-LS）/ Ingredients `2611.24540`（51,455,488 参数 / 1,024 token / 300M token 预算；32 次核心训练两种子；MoE+Muon+GDN 多数可叠加；全开 3.6792/3.6750 nats，参考边界 ±0.0043 nats；MoE 臂 161.3M 总参/51.6M 激活）。③ B 轨 +4 → 272：C4 文档化 `2104.08758`（**990**，EMNLP 2021 pp. 1286–1305）/ ConvNeXt `2201.03545`（**13,910**，CVPR 2022 pp. 11966–11976）/ Grokking `2201.02177`（**967**）/ Mirage `2304.15004`（**1,116**，NeurIPS 2023 pp. 55565–55581）；abs + OpenAlex + ar5iv 各 4/4。④ 作者网 +4 → 251（#248 刘壮 **A** `zhuangl@princeton.edu` + X `@liuzhuang1234` 登记未核验 / #249 Koyejo **A** `sanmi@cs.stanford.edu` / #250 Sengupta **B** `biswa.sengupta@jpmorgan.com` / #251 Alethea Power **C**）。⑤ 发信 3 封：#107 中文 194 字 `SENT OK 03:03:13` / #108 英文 171 词 `03:03:18` / #109 英文 161 词 `03:03:18`；今日 5/12。⑥ 回信率 **0/109**，0 封到期（最早 11-25）。⑦ voice 0 / news 0。⑧ 交付：daily + index + §4–§8 + SEEN/papers.jsonl +2 + PAPERS #269–#272 + AUTHORS #248–#251 + 台账 §03:0x + drafts/bodies 各 3。

- **2026-11-20（本地 00:1x · 00:00 时窗 · 🅰 A 轨 3/5 ＋ 🅱 B 轨第七十轮 +4 → 268 ＋ 作者网 +2 → 247 ＋ 2 封中文信（累计 106）＋ 回信率 0/106）** —— **第二百一十六轮**：① 网络：`cat:cs.CL`（`https` + `--noproxy '*'`）`200` / **94,399 B / 40 entry** / `application/atom+xml`，最新 `published` 仍 **`2026-11-18T18:56:12Z`**（连续第 5 窗未前进）；`http` 端点 `301` ⇒ 改 `https`。② A 轨 **3/5（额度重置）**：ExecJudges `2611.24849`（7 个 TREC 集合；可读程序替代逐文档 LLM 判分；TREC DL 2019–2021 达 Claude Sonnet 5.5 级一致度；ExecJudges-L 7/7 优于同标签预算分类器）/ General progress substitutes `2611.24844`（逐技能抽除；延迟可从小模型预测；补数据只需一小部分；7B 抽掉一门编程语言同样找回）/ Retained Context Charging `2611.24071`（相关性压过位置；65,536 token 热缓存降 >2 个数量级；P99 −31~42% 但中位上升）。`id_list` 3/3 `200`（7,615 B）+ abs 页 `citation_*` 3/3。③ B 轨 **+4 → 268**：Transformer-XL `1901.02860`（**1,881**；80% / 450% / 1,874×；0.99 / 1.08 / 18.3 / 21.8 / 54.5；384/1600）/ Emu3 `2409.18869`（**1,022**；8B / 32 层 / 4096 / 14336 / 32（8 KV）/ 184,622 / 1e6 / 131,072；512 / 720；top-k 16,384）/ Medusa `2401.10774`（**1,028**；>2.2× / 2.3–2.8× / 3.62×）/ Janus `2410.13848`（**633**；CVPR 2025 pp. 12966–12977；1.3B；GenEval 61%；FID 8.53）；`id_list` 批量 **`429`** ⇒ abs 页 4/4 + OpenAlex 4/4；PDF 全截断 ⇒ ar5iv 4/4 `200`（312,920 / 267,946 / 319,495 / 317,703 B）。④ 作者网 **+2 → 247**：#246 蔡天乐 **B 级** `tianle.cai@princeton.edu`（ar5iv 作者块 + `tianle.website` 200/6,114 B 核身份，无 `mailto:`）/ #247 Quoc V. Le **C 级** `qvl@google.com`（2019 论文）；Xinlong Wang 两域名 404、`xiaokang2022.github.io` 实为同名他人博客 ⇒ 拒用；X 106 不变。⑤ 发信 **2 封 → 106**：#105 张令明 中文 **227** 字 `SENT OK 00:05:38`（A 级当场复核）/ #106 郭达雅 中文 **241** 字 `SENT OK 00:05:45`（A 级）；落款两行其后无行、正文无项目名、同轮零共用；今日 2/12。⑥ 回信率 **0/106**，0 封到期（最早 11-25）；通道只发不收。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-20.html` + `daily/index.html` + `research/2026-11-20.md` + `PAPERS.md` #265–#268 + `AUTHORS.md` #246–#247 + `发送记录.md` §00:0x + 两份 draft 状态改「已发送」。⑨ 查重：A 轨三 ID 在 SEEN / papers.jsonl 0 命中；B 轨四 ID 在 PAPERS.md 0 命中（另核 4 个已在表内的 ID）。

- **2026-11-19（本地 21:0x · 21:00 时窗 · 🅰 A 轨 0 新收（今日 5/5）＋ 🅱 B 轨第六十九轮 +4 → 264 ＋ 作者网 +3 → 245 ＋ 0 封信（备 11-20 草稿 2））** —— **第二百一十五轮**：① 网络：`export.arxiv.org` 直连 `200` / **94,399 B / 40 entry** / `application/atom+xml`，最新 `published` **`2026-11-18T18:56:12Z`**（与 15:00 / 15:30 / 18:00 逐字一致 ⇒ 连续 4 窗未前进）；`x.com` 直连与经 `127.0.0.1:7897` 均 **`200`**，但未做单条推文双源核验 ⇒ voice_ready 0。② A 轨 **0 新收**（今日 5/5 已满，不拿旧批凑第 6 篇）。③ B 轨 **+4 → 264**：Transfusion `2408.11039`（**588**；文本因果 / 图像双向注意力 + 双损失；**7B / 2T token**；同 FLOPs **FID 低约 2×**；图文生文以 **21.8% FLOPs** 追平 Chameleon；每图 16 patch）/ Agentless `2407.01489`（**1,053**，PACM SE 2(FSE) pp. 801–824, 2025；三段固定流水线；SWE-bench Lite **32.00% / 96 修复 / $0.70 / 78,166 avg tokens**，v1 曾报 27.33% / $0.34）/ Massive Activations `2402.17762`（**444**，<500 按「方法论常青」；少数激活大 **10^5**、与输入无关 ⇒ 隐式 bias；CLIP ViT-L layer 13 置零 **75.5%→59.8%**、置均值仍 75.5%）/ EDA Corpus `2405.06676`（**38**，<500 按「本领域权威」；IEEE LAD 2024 pp. 1–5，DOI `10.1109/lad62341.2024.10691774`；**>1000** 条、QA **198** 唯一（增强后近 600）+ 指令–脚本对；脚本类**必须在 OpenROAD 真跑判对错**）。arXiv `id_list` 4/4 `200`（10,058 B 一次批量，含 `primary_category` / `updated`）+ OpenAlex 4/4 `200`；PDF **2/4 完整**（1,384,716 / 453,822 B，`%PDF-` + `pdftotext` 通过）、2/4 `content-length` 14,087,563 / 7,636,655 B **>5 MB 未落盘** ⇒ 数字用 **ar5iv 2/2 `200`**（300,229 / 271,351 B）核对并标「未做 PDF 逐页复核」。④ 作者网 **+3 → 245**：#243 Lingming Zhang 张令明 **A 级** `lingming@illinois.edu`（`lingming.cs.illinois.edu` 页内 `mailto:`，`200`/22,815 B；`llingming.github.io` 已 `404`）/ #244 Chunqiu Steven Xia **B 级** `chunqiu2@illinois.edu`（PDF 首页分组明文 `{chunqiu2, yinlind2, sorend2, lingming}@illinois.edu`）/ #245 Vidya A. Chhabria **A 级** `vidyachhabria@asu.edu`（ASU 官方 profile `200`/124,745 B 页内明文）；Transfusion 作者（Meta FAIR，无个人主页）与 Mingjie Sun（`mingjiesun.com` `000`、`cs.cmu.edu/~mingjies/` `404`）⇒ 只计入覆盖、不猜地址；X 保持 **106**。⑤ 发信 **0 封**（今日 12/12 硬上限，台账不新增行）；新备 **11-20 第二封中文草稿** `drafts/2407.01489.md` + `bodies/2026-11-20-2407.01489.txt`（Lingming Zhang；CJK **247** 字 ≤300；落款两行其后无行；两问均二选一；专属细节 = 32.00% / 96 / $0.70 / 78,166 / 三段流水线）。⑥ 回信率 **0 / 104**，0 封到期（最早 11-25）；`replies/` 无摘录；通道只发不收。⑦ voice_ready **0** / news_ready **0**。⑧ 交付：`daily/2026-11-19.html`（+21:00 节 + 附录 21:00 检索式 + 头部页脚时间）+ `daily/index.html` 当日行（264 / 245）+ `research/2026-11-19.md` §41–§44 + `PAPERS.md` #261–#264 + `AUTHORS.md` #243–#245 + `发送记录.md` §21:0x + draft/body 各 1。⑨ 纠错：拦下「EDA Corpus `2405.07288`」——实测为 *Erasing Concepts from Text-to-Image Diffusion Models with Few-shot Unlearning*（OpenAlex 34，无关）⇒ 按 `ti:"EDA Corpus"` 检索得真 ID **`2405.06676`** 后才收录；旧记在候选池作废。

- **2026-11-19（本地 18:1x · 18:00 时窗 · 🅰 A 轨 0 新收（今日 5/5）＋ 🅱 B 轨第六十八轮 +4 → 260 ＋ 作者网 +3 → 242 ＋ 0 封信（备 11-20 草稿 1））** —— **第二百一十四轮**：① 网络：`export.arxiv.org` **https 直连** `200` / **94,399 B / 40 entry**（http 端点返回 `301` / 0 B，已改 https），最新 `published` **`2026-11-18T18:56:12Z`**（与 15:00 / 15:30 逐字相同）；`x.com` 直连 **`200`**、经 `http://127.0.0.1:7897` 亦 **`200`**（前几轮均 `000`），但**未做单条推文双源核验** ⇒ voice_ready 0。② A 轨 **0 新收**（今日 5/5 已满，不凑第 6 篇）。③ B 轨 **+4 → 260**：DiT `2212.09748`（**9,393**，ICCV 2023 pp. 4172–4182，DOI `10.1109/iccv51070.2023.00387`；118.6 Gflops / FID 2.27 / 512² 3.04）/ DeepSeek-Coder `2401.14196`（**2,479**；1.3B–33B / 2T token / **87%-10%-3%** / 87 语言 / repository-level 进预训练 / 16K FIM）/ Math-Shepherd `2312.08935`（**1,535**，ACL 2024 pp. 9426–9439；GSM8K **77.9→84.1**、MATH **28.6→33.0**、验证 **89.1/43.5**）/ MetaGPT `2308.00352`（**2,831**；SOP 编码 + 角色流水线；HumanEval/MBPP **85.9/87.7**，503 s，126.5/124.3 token/line）；arXiv `id_list` 4/4 `200` + OpenAlex 4/4 `200`；PDF 2 篇 <5 MB 但**截断**（1,911,399 / 827,225 B，仅 4/5 页、`pdftotext` xref 错）、2 篇 >5 MB（43,824,062 / 16,753,634 B）⇒ 数字全部改用 **ar5iv 4/4 `200`**（288,428 / 324,866 / 156,622 / 502,095 B）+ arXiv 摘要核对并标「未做 PDF 逐页复核」。④ 作者网 **+3 → 242**（#240 Daya Guo 郭达雅 **A 级** `guody5@mail2.sysu.edu.cn`（主页 `mailto:`，`200`/74,157 B）/ #241 Peiyi Wang 王培懿 无地址（GitHub API `email=null`、主页 404）/ #242 Sirui Hong 洪思睿 无地址（论文首页地址属另一作者，不挪用））；DiT 两作者 Bill Peebles（#52）/ Saining Xie（X 表 V-48）早已建档 ⇒ 不重复计数；X 保持 **106**。⑤ 发信 **0 封**：今日 **12/12** 达每日硬上限 ⇒ 台账不新增行；已备 **11-20 中文草稿** `drafts/2401.14196.md` + `bodies/2026-11-20-2401.14196.txt`（CJK **255** 字 ≤300；落款两行 `祝好，`/`Yang Liu` 其后无行；两问均二选一；专属细节 = 87/10/3 · 2T · 16K FIM · repository-level）。⑥ 回信率 **0 / 104**，**0 封到期**（最早 11-25）；`replies/` 无摘录；通道只发不收。⑦ voice_ready **0** / news_ready **0**（X 可达但未双源核验；四篇无事件点）。⑧ 交付：`daily/2026-11-19.html`（+18:00 节：B #257–#260 / 作者 #240–#242 / 六线建议 / 晚报变更 / 附录检索式；头部与页脚时间同步）+ `index.html` 当日行（B 260 / 作者 242）+ `research/2026-11-19.md` §36–§39 + `PAPERS.md` #257–#260 + `AUTHORS.md` #240–#242 + draft/body 各 1。


- **2026-11-19（本地 15:3x · 15:30 补跑时窗 · 🅰 A 轨 0 新收（今日 5/5，最新批仍 11-18 18:56Z）＋ 🅱 B 轨第六十七轮 +4 → 256 ＋ 作者网 +4 → 239 ＋ 发信 0（今日 12/12 满）＋ 回信率 0/104）** —— **第二百一十三轮**：① 网络：shell 已注入代理 `7897`，但代理到 `export.arxiv.org` 返回 `000`（SSL 35）⇒ 用 `env -u HTTP_PROXY -u HTTPS_PROXY` **直连** `200` / `application/atom+xml` / **71,226 B / 30 entry**；最新 `published` **`2026-11-18T18:56:12Z`**（与 15:00 时窗相同，未再前进）；`x.com` 直连与代理均 `000`（`mihomo` systemd `active`，但出口不通）。② A 轨 0 新收（今日 5/5 已满，不塞当天；新批 7 ID 沿用 15:00 查重结论，登记 11-20）。③ B 轨 +4 → 256：s1 `2501.19393`（**1,939**，EMNLP 2025 pp. 20286–20332；`s1K` = 1,000 题、budget forcing `a_max`/`a_min` + `"Wait"`、比 o1-preview 最高 +27%、AIME24 50%→57%）/ Gemma 2 `2408.00118`（**3,891**；局部滑窗 4096 与全局 8192 逐层交替、GQA + RoPE、2B/9B 蒸馏替代 NTP、logit soft_cap 50.0/30.0）/ BLT `2412.09871`（**144**，<500 按「开创范式」收；next-byte 熵切 patch、8B/4T bytes）/ TheAgentCompany `2412.14161`（**465**，<500 按「本领域权威 / 方法论常青」收；模拟软件公司长程任务、最强 agent 自主 30%）；arXiv `id_list` 4 批均 `200`（7,313 / 6,208 / 21,496 / 5,840 B）+ OpenAlex 4/4 `200`；PDF 仅 **1/4 可解析**（Gemma 2 `610,320` B、`%PDF-` + `%%EOF` 完整），另 3 篇下载截断（1,368,920 / 839,117 / 1,183,809 B，无 `%%EOF`、`pdftotext` 失败）⇒ 数字改用 arXiv 官方摘要（s1 另用 ar5iv HTML `200` / 731,343 B 交叉核对）并逐条标注「未做 PDF 逐页复核」。④ 作者网 +4 → 239（#236 Niklas Muennighoff **A 级** `n.muennighoff@gmail.com`（`muennighoff.com` `200` / 47,863 B 的 `mailto:`；主页自述 Cursor / Stanford、北大本科）/ #237 Morgane Riviere 无地址 / #238 Artidoro Pagnoni 无地址（`apagnoni.github.io` `000`）/ #239 Frank F. Xu 徐方政 **B 级** `fangzhengxu@microsoft.com`（`frankxfz.me` `200` / 1,256 B 的 `[at]` 写法））；X 保持 **106**（`@Muennighoff` 仅主页 href 候选，未二次核验 ⇒ 不计数）。⑤ 发信 **0 封**：今日已 **12/12** 达每日硬上限 ⇒ 本轮只建档（`发送记录.md` 不新增行）。⑥ 回信率 **0 / 104**、0 封到期（最早 2026-11-25）；`mail/replies/` 无摘录；通道只发不收。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-19.html`（+B 轨 4 条 + 作者网 4 条 + 15:3x 六线建议 + 15:30 检索式；div 19/19、table 11/11、tr 101/101、td 420/420、th 57/57、p 8/8、0 script、0 残留 `**`，77,244 B）+ `index.html` 当日行（B 256 / 作者 239）+ `research/2026-11-19.md` §32–§35 + `PAPERS.md` #253–#256 + `AUTHORS.md` #236–#239。⑨ 纠错：拦下 4 个错误 ID —— `2309.15698` 实为 *Deep Model Fusion: A Survey*（非 VerilogEval；真 ID `2309.07544` 已收）、`2305.09673` 实为 *Vulnerability Detection…*（非 LoRA 遗忘）、`2205.10593` 实为 *Few-Shot NLI Generation with PDD*（与 CircuitNet 无关）、`2209.14389` 实为 *Downstream Datasets Make Surprisingly Good Pretraining Corpora*（原拟 Small-scale proxies 是 `2309.14322`，已收 #226）。






- **2026-11-18（本地 12:1x · 12:00 时窗）** —— **第二百零三轮**：B 轨 +3 → 222 / 作者网 203 / 信 90 / H4 启动；细节已 fold 至 `daily-memories-research/2026-11-18.md`。

- **更早轮次（2026-11-12 ~ 2026-11-16，r152–r183）**：原文已按 §5 滚动归档 → `daily-memories-research/` 各日文件的「归档 · MEMORY 滚动」段（2026-11-13 / 14 / 15 / 16 等），此处只留指针，勿以指针替代结论。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
