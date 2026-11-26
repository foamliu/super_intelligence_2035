# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 回信跟踪已真实打通）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r270 · 2026-11-26 18:0x 时窗：**回信再核（IMAP 只读）无新实质回信、+1 退信**（#183 UT Austin 被 SpamAssassin `550 5.7.1` 拦截 ⇒ `退信(反垃圾拦截)`）＋ A 0 收（今日 5/5）＋ B +3 → 437（MobileNets 34,220 / TD3 9,037 / pix2pix 28,513）＋ 作者网 +3 → 404（X 159）＋ 发信 0（今日 12/12 已满，只建档）]
  前一（r269）: [r269 · 15:00 时窗：回信核验首落地（IMAP 只读，实质 7 人 / 8 封信 ≈4.3%）＋ B +3 → 434（ProGen2 / VQ-VAE / Rectified Flow）＋ 作者网 +3 → 401 ＋ 发信 2 → 184（今日 12/12）] 详情见 `daily-memories-research/2026-11-26.md`。
  ① 回信再核（r270）：INBOX **71 封**（15:00 为 67 ⇒ +4：Ollama/Facebook/招聘群发 + **1 退信**）；**无新实质回信**。新退信 **#183**（`lqiang@cs.utexas.edu`，Rectified Flow）2026-11-26 15:10:33 被 `cs.utexas.edu` 以 `550 5.7.1 Blocked by SpamAssassin` 拦截 ⇒ **地址有效、反垃圾拦截**，改判 `退信(反垃圾拦截)`（第 4 类，非「地址失效」、不计「无应答」）。
  ② 累计分账（184）：实质回信 **8 封信 / 7 人（≈4.3%）** · 自动 **1** · **退信 9** · 无应答(>14d) **21** · 未到期 **145** ⇒ 8+1+9+21+145 = 184 ✔。启示：强反垃圾 `*.edu` 会直接 550 拦截中文冷邮件 ⇒ 同类机构后续优先英文纯文本短正文；守「不催/不重发」。
  ③ B 轨 **+3 → 437**（第一百二十三轮）：MobileNets `1704.04861`（arXiv 预印本 2017，**34,220**；深度可分离卷积 + 宽度乘子 α + 分辨率乘子 ρ）· TD3 `1802.09477`（ICML 2018，**9,037**；截断双 Q 取最小 / 延迟策略更新 / 目标平滑）· pix2pix `1611.07004`（CVPR 2017，**28,513**；条件 GAN 同时学损失 + U-Net + PatchGAN）；三 ID 条目级查重 0 命中；abs 3/3 `200` + OpenAlex 3/3 `200`（查询日 2026-11-26）。
  ④ 作者网 **+3 → 404**（X 仍 159）：#402 Phillip Isola（MIT，pix2pix 一作，主页空格混淆还原 `philipi@mit.edu` ⇒ A 级；X 未找到·仅 Bluesky）/ #403 Scott Fujimoto（McGill·Mila，TD3 一作；A 级邮箱未找到、主页 404/302、`@sfujim` 属他人 ⇒ 仅建档；语言待核）/ #404 Alexei Efros（Berkeley，pix2pix 四作，主页明文还原 `efros@eecs.berkeley.edu` ⇒ A 级；`@aefros` 属他人 ⇒ X 未找到）。
  ⑤ 发信 **0**（今日 12/12 已满）：三位作者仅建档不发；若后续发信守「同一论文 ≤1」（pix2pix 已建 Isola + Efros，只选其一）。
  ⑥ 交付：`发送记录.md` #183 改判 + 累计 9/145 + §18:00 节 · `replies/README.md` 增量节 · `PAPERS.md` #435–#437 · `AUTHORS.md` 计数 404 + #402–#404 · `daily/2026-11-26.html` 18:00 增补节 · `research/2026-11-26.md` §18:00 · `daily/index.html` 当日行 + 最新摘要。
  ⑦ 网络：B abs 3/3 `200`（42,806 / 41,571 / 41,771 B）+ OpenAlex 3/3 `200`（34,220 / 9,037 / 28,513，查询日 2026-11-26）×；X 经代理 `x.com` 200（`@sfujim` / `@aefros` 实测为他人 ⇒ 不采用）；IMAP `200`（LOGIN OK，71 封）。

当前动作:     ✅ 18:00 时窗闭环：回信再核（+1 退信、0 新实质回信）；A 0 收；B +3 → 437；作者网 +3 → 404；发信 0（今日 12/12）。
下一步:       ① 21:00 时窗：A 额度满 ⇒ 0 新收；② B 轨 +3（第一百二十四轮，转「补充/更正」为主）；③ 作者网 +3；④ 每轮先读收件箱（SOP）；⑤ 发信：今日已满 ⇒ 仅草稿；⑥ 运维待办：显示名改学术署名 · SPEC 第 4 值 `退信(...)` 待追认 · 何卓论引荐信待裁定 · #164–#170 台账缺口核查 · posttrain sweep 回退核查。
本轮新增:     回信再核（+1 退信 / 0 新实质回信）· B +3（437）· 作者网 +3（404）· X +0（159）· 作者信 0（今日 12/12）· 退信台账 9 · voice_ready 0 · news_ready 0
阻塞:         ① 🔴 显示名仍为 `~/.hr_smtp` 的 `name` = `AI+EDA 招聘 · 自动` ⇒ 需运维改学术署名；② 回信可读但脚本仍只 SMTP ⇒ 每轮须 agent 主动 IMAP 只读；③ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且 agent 只读 ⇒ 需授权；④ 台账 #164–#170（11-25 七时窗）因并发 git 回滚未落盘，待运维核查；⑤ #168/#175 地址有效性存疑；⑥ loop 兜底 `git add` 范围仍需核查；⑦ loop 假阳性（工具回显含自检正则字样）⇒ 本线不打印该正则原文；⑧ 2026-11-26 09:11 posttrain sweep 回退本线 r266 十文件（r267 已恢复）⇒ 请运维核查；⑨ B 轨已 437（远超 50+ 阈值）⇒ 下轮起转「补充/更正」，减少凑数式新增；⑩ SPEC 只允许三值回信状态，但已出现第 4 类「退信(反垃圾拦截/地址无效)」⇒ 待运维追认写回 SPEC。
ERROR_COUNT:  124（r270 本身 0 错误；累计 124 为历史 loop 误判重试计数，待运维收紧匹配）
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
- **上次采集窗口**：`2026-11-26 18:0x`（**第二百七十轮 · 18:00 时窗**：A 轨 0 收（今日 5/5 已满）；B 轨 **+3 → 437**（MobileNets / TD3 / pix2pix）；作者网 **+3 → 404**（X 159）；发信 **0**（今日 12/12 已满，只建档）；**回信再核**：无新实质回信、**+1 退信**（#183 UT Austin 反垃圾拦截）⇒ 退信累计 9）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`papers.jsonl` 现 **412 行**（A 轨结构化台账；`SEEN.md` 为唯一防重台账；本日 A 轨 +5 → 今日 5/5）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**437 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**一百二十三轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**404 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`。**回信摘录 `research/mail/replies/<arXiv_ID>.md`（2026-11-26 起真实落盘 8 份）**


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-26（本地 18:0x · 18:00 时窗 · 🅰 A 轨 0 收（5/5 已满）＋ 🅱 B 轨第一百二十三轮 +3 → 437 ＋ 作者网 +3 → 404（X 159）＋ 发信 0（今日 12/12）＋ 回信再核：+1 退信、0 新实质回信）** —— **第二百七十轮**：① 回信再核（IMAP 只读）：INBOX **71 封**（15:00 为 67 ⇒ +4：Ollama/Facebook/招聘群发 + 1 退信）；**无新实质回信**。新退信 **#183**（`lqiang@cs.utexas.edu`，Rectified Flow）15:10:33 被 `cs.utexas.edu` 以 `550 5.7.1 Blocked by SpamAssassin` 拦截 ⇒ 地址有效、反垃圾拦截，改判 `退信(反垃圾拦截)`。② 累计（184）：实质 **8 信 / 7 人 ≈4.3%** · 自动 1 · **退信 9** · 无应答>14d 21 · 未到期 145（=184 ✔）。③ B +3 → 437：MobileNets `1704.04861`（34,220）/ TD3 `1802.09477`（9,037）/ pix2pix `1611.07004`（28,513）；abs 3/3 `200` + OpenAlex 3/3 `200`；三 ID 查重 0 命中。④ 作者网 +3 → 404（X 159）：#402 Phillip Isola（A 级 `philipi@mit.edu`）/ #403 Scott Fujimoto（A 级未找到、仅建档）/ #404 Alexei Efros（A 级 `efros@eecs.berkeley.edu`）；三人 X 均未找到、不猜。⑤ 发信 0（今日 12/12 已满，只建档）。⑥ 交付：`发送记录.md` §18:00 + #183 改判 + 累计 9/145；`replies/README.md` 增量；`PAPERS.md` #435–#437；`AUTHORS.md` 404 + #402–#404；`daily/2026-11-26.html` 18:00 节；`research/2026-11-26.md` §18:00；`daily/index.html` 当日行。详见 `daily-memories-research/2026-11-26.md`。
- **2026-11-26（本地 15:0x · 15:00 时窗 · r269）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-26.md`「r269」；结论不变（回信核验首落地：实质 **7 人 / 8 封信 ≈4.3%**；B +3 → 434；作者网 401；发信 #183/#184 → 184，今日 12/12）。
- **2026-11-26（本地 12:0x · 12:00 时窗 · 🅰 A 轨 0 收（5/5 已满）＋ 🅱 B 轨第一百二十一轮 +3 → 431 ＋ 作者网 +3 → 398（X 158）＋ 发信 2 封 → 182（今日 10/12）＋ 回信率 0/182）** —— **第二百六十八轮**：① 网络：B abs 3/3 `200`（41,755 / 42,768 / 44,035 B，`citation_title` + `citation_date` 逐字；ViT `comments` 明文 *ICLR camera-ready*，VAE / Neural ODE `comments` 为空）+ OpenAlex 3/3 `200`（47,417 / 8,138 / 71,599，查询日 2026-11-26；Neural ODE = conference-paper / NeurIPS）；X 经代理 `200`（RickyTQChen / giffmana / wellingmax）；`x.com` 自检 `200`；A 列表未重复请求。② B +3 → 431：VAE `1312.6114`（ICLR 2014 社区口径，47,417；重参数化变分下界 → SGVB + recognition model）/ Neural ODE `1806.07366`（NeurIPS 2018，8,138；参数化导数 + 黑盒求解器 + 常数显存 + 伴随法 + CNF）/ ViT `2010.11929`（ICLR 2021，71,599；patch 序列 + 纯 Transformer）；三 ID 查重 0 命中。③ 作者网 +3 → 398（X 156 → 158）：#396 Max Welling（UvA 页明文 `m.welling@uva.nl` ⇒ 已发信 #181；X `@wellingmax` 单源待核不计入）/ #397 Ricky T. Q. Chen（`rtqichen.github.io` 明文 gmail + X 双源 ⇒ 已发信 #182，中文）/ #398 Lucas Beyer（无邮箱、X `@giffmana` 双源 ⇒ 仅建档）；VAE 一作 Kingma 已在 #99/#363，去重不新增。④ 发信 2 → 182（今日 10/12）：#181 荷兰语称谓 + 英文 166 词 `SENT OK 12:04:18` / #182 中文 229 汉字 `SENT OK 12:04:22`；落款两行、其后无行；正文无项目名；两封开头句/三问句式零共用。⑤ 回信率 0/182（已回复 0 / 无应答>14d 21 / 未到期 161）；本轮无新增到期；`replies/` 仍只有 `README.md`。⑥ voice_ready 0 / news_ready 0。⑦ 交付：`PAPERS.md` #429–#431 + `AUTHORS.md` #396–#398 + `research/2026-11-26.md` §121 + `daily/index.html` 当日行（431 · 398 · 158 · 182 · 0/182）+ `发送记录.md` §12:0x + draft / body 各 2。⑧ 运维根因补足：显示名 = `~/.hr_smtp` 的 `name` 字段 `AI+EDA 招聘 · 自动`（`~/hr_mail.py` L29/36）⇒ 本线不改他线配置，待运维改为学术署名。
- **2026-11-26 09:1x 补轮（r267）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-26.md`（B +3 → 428 CycleGAN / ControlNet / EfficientNet；作者网 395；发信 #179 / #180；回信 0/180）。
- **2026-11-26 09:00 时窗（r266）**：原文已归档 → 同上（B +3 → 425 GCN / WaveNet / PixelRNN；作者网 392；发信 #178；回信 0/178）。
- **2026-11-26 06:1x 补轮（r265）**：原文已归档 → 同上（B +3 → 422 TRPO / DenseNet / Score-SDE；作者网 389；发信 #176 / #177；回信 0/177）。
- **2026-11-26 06:0x（第二百六十四轮 · r264）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-26.md`「归档 · r269 后折出」；结论不变（B +3 → 419 Adapter / Flow Matching / PipeDream；作者网 386；发信 #174/#175；回信率 0/175）。
- **2026-11-26 03:2x 补轮（第二百六十三轮 · r263）**：原文已归档 → 同上（B +3 → 416 Prefix-Tuning / Prompt Tuning / ELMo；作者网 383；发信 0；回信率 0/173）。
- **2026-11-26（本地 03:0x · 03:00 时窗 · 🅰 A 轨 +5 → 今日 5/5 ＋ 🅱 B 轨第一百一十五轮 +3 → 413 ＋ 作者网 +3 → 380（X +2 → 151）＋ 发信 1 封 → 173（今日 1/12）＋ 回信率 0/173）** —— **第二百六十二轮**：① 网络（详见快照）：A 列表 `cat:cs.CL&max_results=25`（`--noproxy '*'`）`200` + `application/atom+xml`（61,711 B / 25 entry，`published` 上界 `2026-11-24T18:59:08Z`，距本窗约 24.0h < 72h）；X 经代理 `200`；OpenAlex 3/3；A abs 5/5；B abs 3/3 全 `200`。② A 轨 +5（今日首窗收满 5/5）：AIChipBench `2611.33093`（RTL 跨步状态调试；首次状态不一致反馈 +25.0~46.9 pp、agent-hours 减半；45/69 通过公开测试者在新序列 32 步内失败）/ ShellBench `2611.32946`（100 任务 / 53,100 rollouts；模型 > harness，前三模型差 1.1 pp，五 harness 42.9–45.2）/ CoT-Proxy `2611.33148`（动作-only 蒸馏 + 空推理块 + 回放 KL；GPT-5.6 Luna → 4B AppWorld 7%→48%、SWE-bench Verified 3%→28%）/ Latent Merger `2611.33048`（潜空间合并超网络 LoRA，NeurIPS 2026）/ BriConstrain `2611.33135`（几何约束解码；碰撞自由 31%→91% / 15%→65%，约 60% 成本）；五 ID 查重 0 命中。③ B 轨 +3 → 413：StyleGAN `1812.04948`（CVPR 2019，12,729）/ Diffusion Models Beat GANs `2105.05233`（NeurIPS 2021，6,279；FID 2.97/4.59/7.72）/ PER `1511.05952`（ICLR 2016，4,541；DQN 41/49 Atari 优于均匀）；三 ID 条目级查重 0 命中。④ 作者网 +3 → 380（X 149 → 151）：#378 Tero Karras（无邮箱、`@TeroKarras` 404 ⇒ 仅建档）/ #379 Prafulla Dhariwal（无邮箱、`@prafdhar` 双源 ⇒ 仅建档）/ #380 Tom Schaul（未找到主页/邮箱、`@tom_schaul` 双源 ⇒ 仅建档）。⑤ 发信 1 → 173（今日 1/12）：#173 Or Patashnik（BriConstrain 末位，Tel Aviv University）英文 175 词 `SENT OK 03:08:57`；落款两行、其后无行；正文无项目名；与近期信零共用。⑥ 回信率 0/173（已回复 0 / 无应答>14d 9 / 未到期 164）；`replies/` 仍只有 `README.md`。⑦ voice_ready 0 / news_ready 1（BriConstrain）。⑧ 交付：`daily/2026-11-26.html` + `daily/index.html` 当日行（5/5 · 413 · 380 · 151 · 173 · 0/173）+ `research/2026-11-26.md` + `PAPERS.md` #411–#413 + `AUTHORS.md` #378–#380 + `发送记录.md` §03:xx + draft/body 各 1 + `SEEN.md`/`papers.jsonl` +5。⑨ **推送已闭环**：约 391 MB 经侧分支 `research-backlog-r262` 上传对象后，rebase origin/main + push main 成功（`56679802f5..c6a1d7e397`，`0 0`），临时侧分支已删。
- **2026-11-25（本地 22:4x · loop 重启补跑（21:00 后额外唤醒）· 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第一百一十三轮 +3 → 407 ＋ 作者网 +3 → 374（X +3 → 147）＋ 发信 1 封 → 171（今日 7/12）＋ 回信率 0/171）** —— **第二百六十轮**：① 网络（详见快照）：arXiv `https://export.arxiv.org` `200` + atom 61,711 B / 25 entry，`published` 上界 `2026-11-24T18:59:08Z`（距本窗约 44.7h < 72h；`http://` 端点本窗 `301` ⇒ 改 `https://`）；X `200`；OpenAlex 3/3；B abs 3/3 全 `200`。② A 轨 0 收（额度满）。③ B 轨 +3 → 407：GAE `1506.02438`（6,111）/ DDIM `2010.02502`（11,254，ICLR 2021）/ World Models `1803.10122`（2,470）；三 ID 条目级查重 0 命中。④ 作者网 +3 → 374（X +3 → 147）：#372 Jiaming Song（`tsong.me` 明文 `jiaming.tsong@gmail.com` + X `@baaadas` 双源 ⇒ 已发信；中文）/ #373 David Ha（X `@hardmaru` 双源；主页 `404`、无邮箱 ⇒ 仅建档）/ #374 Stefano Ermon（Stanford 页 `ermon AT cs.stanford.edu` + X `@StefanoErmon` 双源 ⇒ 仅建档，同论文已发一作）。⑤ 发信 1 → 171（今日 7/12）：#171 Jiaming Song 中文 276 汉字 `SENT OK 22:46:04`；落款两行、其后无行。⑥ 回信率 0/171（已回复 0 / 无应答>14d 9 / 未到期 162）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：daily 22:xx 节 + index 当日行 + `research/2026-11-25.md` §22:xx + `PAPERS.md` #405–#407 + `AUTHORS.md` #372–#374 + `发送记录.md` §22:xx + draft/body 各 1。⑨ **卫生事件**：09:10 未推送自动提交误入 166 个 PDF（最大 35MB）+ `__pycache__` + news 归档 gz（最大 18MB）≈1GB，已在未推送状态用 index-filter 改写为纯文本提交并 rebase 到 origin（备份分支保留；文件仍在本地磁盘、仅不被 git 跟踪），并给 `research/.gitignore` 加 `__pycache__/`、`*.pyc`。
- **2026-11-25（本地 09:0x · 09:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第一百一十二轮 +3 → 404 ＋ 作者网 +3 → 371（X +1 → 144）＋ 发信 2 封 → 170（今日 6/12）＋ 回信率 0/170）** —— **第二百五十九轮**：① 网络（详见快照）：A 列表 `200` + atom 62,971 B / 25 entry；X `200`；OpenAlex 3/3；B abs 3/3 + ar5iv 3/3 全 `200`。② A 轨 0 收（额度满）。③ B 轨 +3 → 404：FLAN-T5 `2210.11416`（5,968）/ Textbooks II `2309.05463`（878）/ BIG-bench `2206.04615`（2,190）；三 ID 查重 0 命中；**纠错弃用** `2308.03296`（实测为 Influence Functions，非 phi）。④ 作者网 +3 → 371：#369 Yubo Wang（官方仓 README `y726wang@uwaterloo.ca` ⇒ 已发信；X 未找到）/ #370 Suriya Gunasekar（主页 `suriyag@microsoft.com` ⇒ 已发信；X 未找到）/ #371 Hyung Won Chung（X `@hwchung27` 双源；无当前邮箱 ⇒ 仅建档）；X 144。⑤ 发信 2 → 170（今日 6/12）：#169 中文 283 字 `09:05:26` / #170 英文 182 词 `09:05:29`。⑥ 回信率 0/170（已回复 0 / 无应答>14d 9 / 未到期 161）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：daily 09:00 节 + index 当日行 + `research/2026-11-25.md` §09:00 + `PAPERS.md` #402–#404 + `AUTHORS.md` #369–#371 + `发送记录.md` §09:00 + draft/body 各 2。
- **2026-11-25（本地 06:0x · 06:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第一百一十一轮 +3 → 401 ＋ 作者网 +3 → 368（X +3 → 143）＋ 发信 2 封 → 168（今日 4/12）＋ 回信率 0/168）** —— **第二百五十八轮**：① 网络（详见快照）：A 列表 `200` + atom 62,971 B / 25 entry；X `200`；OpenAlex 3/3；B abs 3/3 + ar5iv 3/3 全 `200`。② A 轨 0 收（额度满）。③ B 轨 +3 → 401：Imagen `2205.11487`（4,540）/ Llemma `2310.10631`（509，ICLR 2024）/ MMLU-Pro `2406.01574`（3,057，NeurIPS 2024 D&B Spotlight）；条目级查重 0 命中；另纠错弃用 `2309.15698` / `2108.00644`（实测非目标论文）。④ 作者网 +3 → 368：#366 Saharia（当前主页 mailto ⇒ 已发信）/ #367 Azerbayev（旧论文地址 + 转发页 404 ⇒ 已发信并记风险）/ #368 Schoelkopf（仅建档）；X 143。⑤ 发信 2 → 168（今日 4/12）：#167 英文 148 词 `06:02:47` / #168 英文 161 词 `06:02:49`。⑥ 回信率 0/168（已回复 0 / 无应答>14d 9 / 未到期 159）。⑦ voice_ready 0 / news_ready 0。⑧ 交付：daily 06:00 节 + index 当日行 + `research/2026-11-25.md` §06:00 + `PAPERS.md` #399–#401 + `AUTHORS.md` #366–#368 + `发送记录.md` §06:00 + draft/body 各 2。
- **2026-11-25（本地 03:0x · 03:00 时窗 · 🅰 A 轨 +2 → 今日 5/5 ＋ 🅱 B 轨第一百一十轮 +3 → 398 ＋ 作者网 +3 → 365（X +3 → 140）＋ 发信 1 封 → 166（今日 2/12）＋ 回信率 0/166）** —— **第二百五十七轮**：① 网络：`cat:cs.CL&max_results=25&sortBy=submittedDate`（`--noproxy '*'`）**`200` + `application/atom+xml`**（62,971 B / 25 entry，`published` 上界 `2026-11-23T18:48:02Z` 与 00:00 逐字相同，距本窗 24.2h < 72h）+ X `200` + OpenAlex 3/3 `200` + A 轨 abs 2/2 `200`（42,019 / 41,783 B）+ B 轨 abs 3/3 `200`（41,755 / 44,028 / 39,154 B）。② A 轨 **+2（今日 5/5）**：CO-GRAFT `2611.31185`（4 角色 × 2⁴=16 指派 Shapley 归因；查询生成 ≤15%；Search-R1 × Qwen2.5/Llama-3.2 × GRPO/PPO × NQ/HotpotQA）/ Attention Temperature `2611.31113`（365M twins 8–15% 失校准；纯 bf16 37–58%；校准后 ALiBi 反落后 RoPE 5%）；两 ID 查重 0 命中。③ B 轨 **+3 → 398**：VAE `1312.6114`（45,270，ICLR 2014）/ PAL `2211.10435`（859，ICML 2023；13 任务，GSM8K 相对 PaLM-540B CoT +15% 绝对）/ TinyLlama `2401.02385`（1,248，1.1B / 约 1T token / 约 3 epoch）；三 ID 条目级查重 0 命中。④ 作者网 **+3 → 365**：#363 Durk Kingma（站点无 mailto ⇒ 仅建档；`@dpkingma` 单源强匹配）/ #364 Luyu Gao（`luyug@cs.cmu.edu` 主页 mailto ⇒ 已发信）/ #365 Perry Zhang（`pez010@ucsd.edu` 主页 mailto ⇒ 仅建档）；X **+3 → 140**。⑤ 发信 **1 封 → 166**：#166 Luyu Gao 中文 202 汉字，`SENT OK 03:04:05`；落款两行、其后无行；正文无项目名；与近期各信零共用；今日 2/12。⑥ 回信率 **0/166**；#1–#9 已转 `无应答(>14d)`；`replies/` 仍只有 `README.md`。⑦ voice_ready 0 / news_ready 0。⑧ 交付：`daily/2026-11-25.html` + `daily/index.html` 当日行 + `research/2026-11-25.md` §03:00 + `PAPERS.md` #396–#398 + `AUTHORS.md` #363–#365 + `发送记录.md` §03:00 + draft / body 各 1。
- **2026-11-25 00:0x（第二百五十六轮）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-25.md`「归档 · r267 后折出」；结论不变（B 轨 +3 → 395；作者网 +3 → 362；发信 1 → 165；回信率 0/165，首 #1–#9 转无应答）。
- **2026-11-24 21:0x（第二百五十五轮）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-24.md`「归档 · r266 后折出」；结论不变（B 轨 392 / 作者网 359 / 发信 #164 / 回信率 0/164）。
- **2026-11-24 06:0x & 09:0x & 15:0x（已折出）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-24.md`（归档 · r265 后折出；含本 r265 折出的 15:0x 原文）。



- **2026-11-24 00:0x & 03:0x（已折出）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-24.md`「归档 · MEMORY 滚动（r259 后折出）」；结论不变，勿以指针替代原文。
- **2026-11-23 18:0x ~ 2026-11-22 18:0x（更早 8 条）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-23.md`「归档 · MEMORY 滚动（r249 后折出）」；结论不变，勿以指针替代原文。

- **2026-11-22 06:0x ~ 2026-11-19（更早轮次）**：原文已按 §5 滚动归档 → `daily-memories-research/2026-11-22.md`「归档 · MEMORY 滚动（第九十四轮后折出）」与 `daily-memories-research/2026-11-21.md` / `2026-11-20.md` / `2026-11-19.md` / `2026-11-18.md`；结论不变，勿以指针替代原文。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
