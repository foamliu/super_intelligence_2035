# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）** + **任务书自滚归档（已把第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`；每次唤醒按 ≤32KB 自检）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~六十轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库 75,610 条 · N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + §4.4 措辞强度 tone 信号，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md）+ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）· **任务书自滚归档（第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`）** · **第六十轮常态采集（news +4：Mistral Large 4 · 英伟达市值新高 · Pinterest AI Beauty Guides · Flai A 轮）** · **第六十一轮常态采集（news +1：AMD 股价创历史新高·苏姿丰称 AI 芯片需求旺盛）** · **第六十二轮常态采集（news +2：德国交通部长盼特斯拉 FSD〔监督版〕获欧盟批准 · TechCrunch：LibreOffice 把「no AI」当特性）** · **第六十三轮常态采集（news +1：TechCrunch Anthropic 赠初创企业一年 Claude Team + 1,000 美元 API credits）** · **第六十四轮常态采集（news +1：Google 官方博客 EmbeddingGemma 2 开放轻量多模态嵌入模型〔基于 Gemma 4 · 端侧〕）** · **第六十五轮常态采集（news +1：TechCrunch Mirror Particle 构建「人类行为世界模型」基础模型〔将亮相 TechCrunch Disrupt Startup Battlefield 200〕）** · **第六十六轮常态采集（news +0：窗口 0.55h 无新 AI 事件 → 如实留空）** · **第六十七轮常态采集（news +0：窗口 0.53h 无新 AI 事件 → 如实留空）** · **第六十八轮常态采集（news +1：TechCrunch Hark 发布 AI 个人助理 Hark Pro〔computer-use 模型〕）** · **第六十九轮常态采集（news +0：窗口 0.55h 无新 AI 事件 → 如实留空）** · **第七十轮常态采集（news +1：TechCrunch Wajo〔前 DeepMind 工程师 Shivani Poddar 的 agent 创业·Khosla 押注〕· 第 62 轮窗口漏收 → 补收）** · **第七十一轮常态采集（news +1：TechCrunch Lambda 拟融资 $4B〔投前估值 $14.5B·2027 IPO 前最后一轮〕）** · **第七十二轮常态采集（news +1：TechCrunch Musubi 宣布实时内容审核「决策模型」`PolicyLM-1.7B`〔开放权重·<50ms〕）** · **第七十三轮常态采集（news +1：TechCrunch Underdog 端侧隐私 AI 助理〔Thiel Fellow Sigil Wen·Qwen3.8-27B 微调 27B 模型·自研 Husky 引擎·Stripe 支付抽成·第七十二轮窗口漏收 → 本轮补收〕）** · **第七十四轮常态采集（news +0：窗口 0.55h 无新 AI 事件 → 如实留空）** · **第七十五轮常态采集（news +1：TechCrunch Ex-Ramp 团队 AI 广告素材生成平台 `Melius` 融资 $25M〔$20M A 轮 CRV 领投 ＋ $5M 种子 GC 领投〕· 自称两月年化营收 >$1M〕** · **第七十六轮常态采集（news +1：IT之家〔据路透社〕Anthropic 正式公布新版「网络核验计划（CVP）」· 整合「玻璃翼计划（Project Glasswing）」与旧版 CVP；合作方 4–7 月至少找到 129,000 个已核实漏洞 · >33,000 评为严重/高危；三级均开放 Claude Opus 5.5 / Sonnet 5.5 / Mythos 5.1）** · **第七十七轮常态采集（news +3：OpenAI 发布又一批 AI 数学研究成果〔722 手稿·攻破数百难题〕· 美司法部要求员工改称 AI 为「超级智能」· SpaceX 拟募 $40B 采购英伟达芯片）** · **第七十八轮常态采集（news +1：AI 颠覆担忧消退·美国软件股创 2026 年阶段新高〔标普 500 软件与服务指数创 2025-11 以来新高〕）**
当前动作:     **本唤醒（2026-10-08 06:00 早报轮）：① P0 R2 交付（第 11 批硬指标）② 第七十九轮常态采集（news +6）** —— **①** `block_boot.py` **重写为 3 组设计**（修 R1 设计缺口：只按 top-|coef| 选样会**偏向 CI 不含 0**）→ `BOOTSTRAP.md`：**G1 = FDR `q<0.10` 全格**（本版为空）· **G2 = 每频 top-|coef|**（post-hoc·标 `exploratory`）· **G3 = 均匀随机 20 格**（seed `SEED_RAND=20351009`，**预先指定**）⇒ **G3 = 19/20（95%）的 95%CI 跨 0**，为「**未发现稳定滞后相关**」提供**关键稳健性证据**；`make_findings.py` → **`FINDINGS.md`**（全网格 23940 格·`q<0.10`=0·`stable`=0·机械 top-N + 如实 `refuted`）；**首份早报 `news/signal/daily/2026-10-08.md`**（口径块 + §1 信号简报〔近 24h 无新增〕+ z-table + 3 个 |z|≥1.5 偏离 + §2 昨日复核 + §3 结论 5 条 + §4 变更记录 AM→PM）。**`lag_corr.py` R2 确定性重跑**：与 R1 归档 `/tmp/lag_corr_R1.csv` **字节一致**（sha256 均 `83d3bf349be52251d409222a61f2466f0bf3ac8fe00f5e3d510f0494801783cc`）→ `LAG_CORR.md` 重发并带 **R2 复核头**。**② 第七十九轮**：窗口约 **21.9h**（第七十八轮 2026-10-07 08:10 → 本次 **2026-10-08 06:10 CST**，**节后首个工作日**）→ **news +6**（中文 4 / 英文 2）：IT之家 **MAI Code 1.1 Flash 拟整合 Win11**〔`010/308`·130B/256K/3-bit·性能数字为**原厂自述**·第 1 类〕· **英伟达 DGX Station for Windows**〔`010/313`·GB300·**748GB 统一内存**·≤20 PFLOPS·4Q26 上市·第 1 类〕· **传三星 12Hi HBM4E 通过英伟达等客户质量验证**〔`010/303`·据《韩国经济日报》·**三星称「无法确认」**⇒ 按传闻写·第 5 类〕· **CoreWeave 进军印度 240MW**〔`010/300`·AdaniConneX·Taloja·NVIDIA Vera Rubin·第 5 类〕· TechCrunch **Google SynthID 核验站全面开放**〔10-07 22:00 CST·第 2 类〕· **Nous Research $90M B 轮 @$1.5B**〔10-08 04:48 CST·Hermes for Businesses·第 5 类〕。**微软 Surface×英伟达发布会簇共 ~11 条，按「不追量」只取 2 条最可核验者，其余防重留档**。`SEEN.md` **+11 行**（6 news + 5 防重留档）。**G2′④**：同窗已单独启动 `cycle_run.py` **真实重跑**（`/tmp/cycle.log`：eda rc=0 / taxonomy rc=0 …）→ **本轮不再重复刷**；连续性**以 `STABILITY_LOG.md` 自报行**为准（⚠️ 未达标照写）。**体积**：TASK=**37.6KB**（>32KB 目标·<40KB 红线） / MEMORY=**28.9KB**（≤32KB 目标；本轮已把第七十三~六十三轮流水原文滚入 `daily-memories-news/2026-10-07.md`）→ 均 <40KB 红线，**本轮无需再搬**。**上一唤醒**：第七十八轮（+1）详见 §2 流水。
第11批(R2):    ✅ **P0 交付（R1+R2）**：`news/signal/` = prices/〔38 标的·6 类·2016–2026·2.56MB〕· SOURCE_TEST.md（ok=38/fail=0）· INDEX_FILES.md · `lag_corr.py`→ lag_corr.csv + LAG_CORR.md（**23940 格·FDR `q<0.10`=0/`stable`=0·如实负面**，非因果；**R2 重跑与 R1 字节一致 sha256 `83d3bf34…`**）｜`PREREG.md` **先于结果**｜`BOOTSTRAP.md`（**块自助 3 组：G1 FDR 全格 / G2 top-|coef| 每频（post-hoc·exploratory）/ G3 随机 20 格（seed 20351009）→ G3 = 19/20 CI 跨 0**）｜`FINDINGS.md`（台账：机械 top-N + 如实 `refuted`）｜**早报 `daily/2026-10-08.md`（首份 · AM）**｜⏭ R2 余项：**PM 晚报（18:00 收盘后 · 首次「早报 vs 实际」复核）**
下一步:       ① **PM 晚报（18:00，收盘后）**：填 `news/signal/daily/2026-10-08.md` **§4 PM 段**（**首次「早报 vs 实际」复核**；若台账有变则同步 `FINDINGS.md`）；② 常态采集续跑（**新节律：每天 2 次 06:00/18:00**；窗口内新 AI 事件照收、无则如实留空；**深扫 feed 头部以下若干位，防再漏收**）；③ **G2′④ 累积**：维持 ≥20h 真实重跑节奏（下一窗约 `2026-10-08 18:00` 及以后；**同天只计 1 天**），**如实自报连续天数/未达标**（`STABILITY_LOG.md`）；④ **第 10 批 B 线**：**仍待用户拍板 P1–P6/P7**（`news/dongfang/report.html` §8）→ **拍板前不实施日更**；⑤ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；⑥ L3（N5）**冻结**；⑦ **任务书/MEMORY 自滚归档**（>32KB 目标 / >40KB 红线前先搬 `WATCH_NEWS_TASK_ARCHIVE.md` / `daily-memories-news/`）
本轮新增:     **第七十九轮常态 news +6（中文 4 / 英文 2；当日 6 / 累计 179）**——IT之家 **MAI Code 1.1 Flash 拟整合 Win11**〔`010/308`·01:29 CST·130B 参数/256K 上下文/3-bit 量化已缩 80%·已集成 GitHub Copilot 与 VS Code·Terminal-Bench 2.1 +22%、.NET +15%、token 减 25%、新增「看图写代码」；**性能数字均原厂自述、未独立复现**；第 1 类〕· **英伟达 DGX Station for Windows**〔`010/313`·01:56 CST·GB300 Grace Blackwell Ultra·72 核 Grace＋Blackwell Ultra·748GB 统一内存〔252GB HBM3e＋496GB LPDDR5X〕·≤20 PFLOPS·≤1 万亿参数模型·1600W/20A·4Q26 上市；第 1 类〕· **传三星 12Hi HBM4E 已通过英伟达等主要客户质量验证**〔`010/303`·23:35 CST·据《韩国经济日报》·1c nm DRAM＋4nm Logic·48GB/堆栈·14~16Gbps·**三星官方答「无法确认」⇒ 按传闻保留**；第 5 类〕· **CoreWeave 落子印度 240MW**〔`010/300`·23:19 CST·AdaniConneX·Taloja 3×80MW·NVIDIA Vera Rubin·一期 2028 中·或翻倍至 +240MW；第 5 类〕· TechCrunch **Google SynthID 核验站向所有人开放**〔10-07 22:00 CST·图/视/音多格式·日 100 万次核验·原文自承「并非万无一失」；第 2 类〕· **Nous Research 确认 $1.5B 估值、$90M B 轮、推 Hermes for Businesses**〔10-08 04:48 CST·Robot Ventures 领投·Nvidia/Samsung 等参投·累计融资 $158M·Hermes 克隆 >2400 万次·自称占全球 AI token 2.5%·WSJ：9 月中 ARR ≈$36M；第 5 类〕。`SEEN.md` **+11 行**（6 news + 5 防重留档〔Surface 价格/RTX Spark/Meta Muse iPad/VS Code〕）。┃ 上一唤醒：第七十八轮（news +1）见 §2 流水
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）｜🆕 **第 10 批**：⚠️ **`mcp<2` 已成运行机全局 pin**（2.3.0 → **1.30.0**，否则 `mcp_ddgs`/离线自检不可用）→ 与需 **mcp 2.x** 的其它线**可能冲突**，**待 supervisor 确认**；⚠️ **ddgs 8/8 引擎被墙**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但结果端点被拦）→ 免费通用 web 搜索**本机不可用**，日常仍以 `cn_news` + 官方 RSS 为准；⚠️ **CN-Bing 抓取相关性降级**（查「人工智能 最新 政策」返回「人工」词条 → 200 ≠ 有料） ｜📦 **体积（实测字节）**：**TASK=38655B(37.6KB) / MEMORY=29692B(28.9KB)**（含 ARCHIVE≈48.3KB）；soft 32KB / 红线 40KB
ERROR_COUNT:  4（历史：模型名白睡一轮，已修；并发双抓重复，已修；watcher `pgrep -f` 自匹配死锁，已修；**relay rebase 删工作区分片 → 已恢复**）
```

**选定方案（prep_api 结论）**

- **Web 搜索**：**抓取 CN-Bing（`cn.bing.com`）主 + 360（`so.com`）备**（免 key、中文友好；本机唯一真跑通的通用搜索）。已封成 MCP `web-search-free`。
- **新闻取数**：**Hacker News API + GDELT Doc API + 官方 RSS**（新华/人民/中新/arXiv/Ars 等，免 key）。
- **付费/需 key 备选**（本机可连但需注册/信用卡，仅作升级路径）：Tavily、Exa、SerpAPI、Guardian、GNews、Currents、Mediastack、TheNewsAPI。
- **本机不可达（被墙）**：Google、DuckDuckGo、Brave、Yahoo、公共 SearXNG（8 实例全灭）、newsapi.org、BBC、Reuters、Google News RSS。
- **原 bocha key 额度已用尽**（`HTTP 403 not enough money or package quota`）→ 故改用免 key 自建后端。

**交付物**：`news/mcp_web_search_free.py`（MCP server，3 工具）· `news/cline_mcp_config.json`（MCP 配置片段）· `news/API_COMPARISON.md` + `news/API_COMPARISON.html`（自包含对比报告）。

---

## 🧰 取数用法（T10：`cn_news` 中文活源统一入口 —— **CLI 是一等公民**）

> ⚠️ **MCP 仍未装进 cline**（见下方运维问答）→ **一律用 CLI / Python 直调**。

```bash
# ① 中文权威源真新闻（中新网 + 联合国新闻·中文 + 央视网；内建 死源黑名单 + pubDate≤72h + Content-Type 校验）
cd /home/liuyang/super_intelligence_2035/doc/personal-watch/run
python3 news/mcp_web_search_free.py --cn-news --limit 30            # 人类可读（条目 + 各源新鲜度 + 丢弃原因）
python3 news/mcp_web_search_free.py --cn-news --limit 30 --json     # JSON（含 meta：per_source）

# ② 其它工具（Python 直调）
python3 -c "import sys; sys.path.insert(0,'news'); import mcp_web_search_free as m; print(m.search_news('AI regulation',5))"
python3 -c "import sys; sys.path.insert(0,'news'); import mcp_web_search_free as m; print(m.fetch_cn_news(30)['items'][:3])"

# ③ 中文 dated 补充源（T6 中文补强；均带 pubDate、实测活源 → 以 rss_latest 取）
python3 -c "import sys; sys.path.insert(0,'news'); import mcp_web_search_free as m; print(m.rss_latest('https://www.qbitai.com/feed',8))"    # 量子位（AI 纵深）
python3 -c "import sys; sys.path.insert(0,'news'); import mcp_web_search_free as m; print(m.rss_latest('https://www.ithome.com/rss/',20))"      # IT之家（科技产业）
python3 -c "import sys; sys.path.insert(0,'news'); import mcp_web_search_free as m; print(m.rss_latest('https://www.ifanr.com/feed',15))"       # 爱范儿（T6 新增；AI/数码）
# 备用活源（本轮实测 200 + 带 pubDate，未启用）：雷峰网 https://www.leiphone.com/feed · 钛媒体 https://www.tmtpost.com/rss
# ⚠️ 死源：新浪科技 http://rss.sina.com.cn/tech/rollnews.xml（接口 200 但内容停在 2018-09-23）；中新网 https://www.chinanews.com.cn/rss/it.xml（空 feed）
```

**返回样例（每条）**：
```json
{"title":"OpenAI披露澳大利亚又一政府机构遭入侵","source":"央视网","url":"https://news.cctv.com/2026/10/03/ARTI3jDXniV5jQDx59hwBf6y261003.shtml","published":"2026-10-03T01:14:00+00:00","lang":"zh","type":"news","snippet":"…"}
```
**实测（2026-10-03）**：6 活源全 `200` → 命中 30 条；丢弃 83 条（超龄 >72h）。**详见 `news/FETCH_CN_NEWS.md`**。

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（本线主动小结 · 2026-10-05 第6轮）：N1 全部抓完了吗？全链对齐了吗？体积红线（≥5MB 不入 git）落实了吗？**
  **A（本线 2026-10-05 实测）**：
  - **① N1 全库完抓 ✅**：第 7 轮（14:56→15:10）把游标 `2016-08-05 → 2016-01-01` 走完 → 语料 **2,267,862 → 2,492,230 条**（11 片 2016–2026；游标 `2015-12-31` = 已到终点，**倒序抓取收尾**）。`--stats` / `.progress.json` 一致（`done_days=3929`）。
  - **② 全链对齐 ✅**：`/tmp/n1_chain_r7.log` 尾 `[chain r7 done] 2026-10-05 15:10:58`；`STABILITY_LOG.md` **第 8 行** `2026-10-05 15:10 | 3914 | 2492429 | 75610 | 43 | 24 | ``9909e4cddcf525a8`` | ``90f357ff8a8be943`` | ok`（`EVENTS.csv` **75,610 条 / 18.11 MB**；`explore.csv` sha 不变属预期）。
  - **③ 体积红线落实 ✅（用户 §4-11 明令 ≥5MB 不入 git）**：ops RUN_ID 5（`d5d7dab`）已把 11 个分片 `git rm --cached`；本线补做 **`news/policy/.gitignore` + `git rm --cached EVENTS.csv`**（**18.11 MB ≥5MB**）；`fetch_archive.py --index` / `extract_events.py` 的体积口径**由「>20MB」改为「≥5MB」并新增「存放位置」列**；两处 `INDEX_FILES.md` 重生成。⚠️ 实测：`git check-ignore` **对已跟踪文件不命中** → 要命中**必须先 `git rm --cached`**（否则红线自检永远失败）。
  - **④ 🐞 善后（relay rebase 误删工作区分片）**：ops relay 的 `git pull --rebase` 把**被 untrack 的 11 个分片从工作区删掉**（`outbox` 末「工作区分片仍应为 11 → `0`」），而 RUN_ID 5 **本意是「保留工作区文件」** → 本线已 `cp ~/archive_data_backup/*.jsonl.gz news/archive/` **恢复**（11 片 / 105 MB，sha 与 `PROGRESS.md` 逐条一致）；`.gitignore` 生效（`git status` 无 `??`，提交绝不带 `.gz`）。
  - **⑤ 无 bypy** → 百度云盘**不可用** → 按红线「**宁可不传**」，≥5MB 一律 **本地保留 + 清单登记 + 如实标『未上云』**（两处 `INDEX_FILES.md` 均标 `本地/未上云(≥5MB)`；第二副本 `~/archive_data_backup/`）。
  - **⑥ 常态采集**：第十六轮 **+0**（国庆假期中文权威源 AI 类真新闻稀缺；`cn_news` 30 条均假期/民生/时政；量子位 `501700`、中新网 `10708128` 已在账 → 去重）→ 当日累计 **22**；累计 **news 91 / 非新闻 41**。

- **Q（本线主动小结 · 2026-10-05 第5轮）：N1 第 5 轮抓了吗？全链对齐全语料了吗？第 6 轮起了吗？**
  **A（本线 2026-10-05 14:30）**：
  - **第 5 轮抓取 ✅**：倒序 `2019-01-24 → 2017-10-30`，语料 **1,645,640 → 1,952,411 条（+306,771）**；片数 8 → **10**（新增 **2018 全年** + **2017-10~12**）。
  - **全链重跑 ✅**（14:07）：`EVENTS.csv` 54,485 → **63,398**（15.27 MB，sha `973a20f394987462`）；`EARLY_WARNING.md` 45 格 `q<0.05` 40→**44**、效果量门槛 18→**19**（同族同法，仅因语料增）。
  - **`STABILITY_LOG.md` 第 6 行 ✅**（14:07，可核验摘要）。
  - **第 6 轮已起 ✅**：倒序 `2017-10-30 → 2016-01-01`，后台抓取 + watcher（**按 `kill -0 <pid>` 等待**，抓完自动 `--index` + 链跑）。
  - **⚠️ 纪律**：停后台抓取须**杀 python 子进程**；等抓取**勿** `pgrep -f <脚本名>`（会自匹配 watcher 命令行 → 死锁）。

---

## 1. 状态头

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **N1 语料库**：`news/archive/chinanews-<年>.jsonl.gz`（只 5 字段；**仅取 标题+日期+来源+链接，不抓正文**）；现 **2,492,230 条 / 3929 天 / 11 片**（**2016-01-01 ~ 2026-10-03**；游标 `2015-12-31` = **倒序抓取已收尾**）；⚠️ **≥5MB → 不入 git**，清单见 `news/archive/INDEX_FILES.md`
- **L1 产物**：`news/policy/`（`EDA.md` / `TAXONOMY.md` / `SIGNALS.md` / `EVENTS.csv` / `EARLY_WARNING.md` / **`cycle_run.py` + `STABILITY_LOG.md`（G2′④ 运行台账）**）
- **L2 产物（探索性 · 非因果）**：`news/policy/`（`L2_PREREG.md` / **`EXPLORE.md` + `explore.csv`**）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：**每天 2 次定时唤醒（06:00 / 18:00，`SCHEDULE_HOURS=6,18`）**，时窗内零 token 分段睡（2026-10-07 用户令）；**`WAITING` 已不影响节律**（仅人读状态）；旧自适应 `WAITING=1`→睡 30min / `WAITING=0`→短睡 60s **降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）
- **上次采集窗口**：`2026-10-07 07:50 CST` 第七十七轮 ~ `2026-10-07 08:10 CST` 第七十八轮（**第七十八轮为本轮唤醒**）
- **累计收录**：`news` **179** 条（第一~七十九轮；当日 **6**）+ 非新闻（口径=逐行统计 `SEEN.md` 类型列）〔**仅存 `SEEN.md`**〕

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-08（第 11 批 · R2 · P0 · 06:00 早报轮）** —— ✅ **① P0 R2 交付**：**`BOOTSTRAP.md`**（`block_boot.py` **重写为 3 组**：**G1** = FDR `q<0.10` 全格〔本版为空〕· **G2** = 每频 top-|coef|〔**post-hoc ⇒ 标 `exploratory`**〕· **G3** = **均匀随机 20 格**〔seed `SEED_RAND=20351009`·**预先指定**〕⇒ **G3 = 19/20（95%）的 95%CI 跨 0**，为「未发现稳定滞后相关」提供**关键稳健性证据**；**修 R1 设计缺口**：只按 top-|coef| 选样会**偏向 CI 不含 0**，故不能作结论依据）· **`FINDINGS.md`**（`make_findings.py`：全网格 **23940** 格·`q<0.10`=**0**·`stable`=**0**·机械 top-N + 如实 `refuted`）· **首份早报 `news/signal/daily/2026-10-08.md`**（口径块〔as-of / 源 / 幸存者偏差〕+ §1 信号简报〔近 24h 无新增〕+ §1.2 z-table + §1.3 三个 |z|≥1.5 偏离〔A3_会议召开 −2.60 / A15_货币工具 −2.23 / T4_房地产 +2.22；最强格 `q=0.913/0.976/0.976`，样本外命中**不赢基线**〕+ §2 昨日复核〔38 标的 09-30 末日涨跌〕+ §3 结论 5 条 + §4 变更记录 AM→PM〔PM 待 18:00〕）· `LAG_CORR.md` 刷 **R2 复核头**（`lag_corr.py` **确定性重跑**，与 R1 归档 **字节一致** sha256 `83d3bf34…78 3cc`）。**② 第七十九轮常态采集 news +6**（中文 4 / 英文 2）——详见 `news/2026-10-08.md` 与 `daily-memories-news/2026-10-08.md` `[06:10]` 心跳。**③ G2′④**：同窗单独启动 `cycle_run.py` **真实重跑**（P0 链，`/tmp/cycle.log`）→ 本轮**不重复刷连续性**（如实自报）。**非因果 · 非投资建议 · L3 冻结** 口径不变。


- **2026-10-07（第 11 批 · R1 · P0）** —— ✅ **新闻信号→资产价格 R1 交付**：`news/signal/` = **PREREG.md（先于结果）+ SOURCE_TEST.md（源实测 ok=38/fail=0）+ fetch_prices.py + prices/〔38 标的/6 类/2016–2026·2.56MB〕+ INDEX_FILES.md + lag_corr.py → lag_corr.csv（23940 格）+ LAG_CORR.md**。**结论（如实·非因果·非投资建议）**：**FDR 后 `q<0.10`=0、`stable`=0**；未校正 `p<0.05`=1217/23940≈5.08%≈随机基线 ⇒ **未发现稳定滞后相关**（负面结果照写）。详见 `daily-memories-news/2026-10-07.md` `[18:00]` 心跳。

- **2026-10-07（本唤醒 ~08:10）** —— ✅ **第七十八轮常态采集：news +1（中文 1 / 英文 0；当日 14 / 累计 173）**：窗口约 **0.33h**（第七十七轮 07:50 → 本次 **2026-10-07 08:10 CST**，国庆假期最后一天上午；loop 于 08:08 按新节律「每天 2 次〔06:00/18:00〕」首启后立即唤起的紧凑补采）。**收录 1**：**IT之家《AI 颠覆担忧消退，美国软件股创 2026 年阶段新高》**〔`010/141`·**07:58:45 CST**〔在窗〕·本机 `HTTP 200` + 页面发布时刻核验；**标普 500 软件与服务指数创 2025 年 11 月以来新高**、**赛富时（Salesforce）/ ServiceNow 等财报亮眼**、**网络安全板块涨幅达三位数**〔报道所述〕、**多位分析师认为 AI 更多是「赋能」而非「颠覆」**〔原文/分析师表述〕；归第 5 类＋关联第 4 类；⚠️ 涉市场行情 → **仅相关性观察、非因果、非投资建议**〕。**未收/去重**：IT之家 `010/143` 前妻评马斯克〔人物·非 AI〕/`010/142` iOS 27.2 Beta 3〔非 AI〕/`010/140` 三维弹球〔非 AI〕/`010/139` IT早报 1007〔汇编·非具体事件〕/`010/138` XBOX GTA6〔07:48 CST·**早于窗口**〕→ 去重/不收；`cn_news`（限 40）均假期/民生/时政、**无 AI 条目**；**联合国中文源仍 404**；**量子位 `feed` 本轮取回空正文**〔如实记录〕；爱范儿/TechCrunch/The Verge/Ars 头部均已在账/同事件/非 AI/超窗 → 去重/不收。**台账**：`SEEN.md` **+1 行**（1 news）。**G2′④**：距上次真实重跑（**2026-10-07 07:59**，第七十七轮）约 **0.2h < 20h** → **不刷连续性**（自报仍 **连续 3 天 / 目标 7 天 · ⚠️ 未达标**；同天多次运行只计 1 天）。**体积**：MEMORY=**31.6KB**（已压至 ≤32KB）；TASK=**34.6KB**（>32KB 目标·<40KB 红线）；ARCHIVE≈47KB。

- 🔀 **第七十七轮**（2026-10-07 ~07:50，news +3：**IT之家《OpenAI 发布又一批 AI 数学研究成果，攻破数百个悬而未决难题》**〔`010/137`·722 手稿 / 372 结果家族 / 未发布前沿模型 / AGMAI 数学家咨询小组·与 OpenAI 官方《Sharing AI Progress in Mathematics》同事件·归第 1 类〕· **《落实特朗普行政令，美国司法部要求员工改称 AI 为「超级智能」》**〔`010/135`·据路透社·代理副总检察长 Trent McCotter 备忘录·归第 3 类〕· **《消息称 SpaceX 计划募资 400 亿美元，用于采购英伟达 AI 芯片》**〔`010/134`·据金融时报·阿波罗全球管理领投·归第 5 类〕）流水原文已滚入 `daily-memories-news/2026-10-07.md`（📦 滚动归档 · 第七十八轮 08:10 为 MEMORY≤32KB 归档；原文不改）。

- 🔀 **第七十六轮**（2026-10-07 ~07:15，news +1：**IT之家《已挖出十几万漏洞，Anthropic 向更多安全团队开放其最强 Claude 模型》**〔Anthropic 正式公布新版「网络核验计划（CVP）」·整合「玻璃翼计划（Project Glasswing）」；合作方 4–7 月至少 129,000 个已核实漏洞·>33,000 严重/高危；三级均开 Claude Opus 5.5 / Sonnet 5.5 / Mythos 5.1；归第 2 类＋关联第 5/1 类〕）流水原文已滚入 `daily-memories-news/2026-10-07.md`（📦 滚动归档 · 第七十七轮 07:50 为 MEMORY≤32KB 归档；原文不改）。

- 🔀 **第七十五轮**（2026-10-07 ~06:39，news +1：**TechCrunch《Ex-Ramp engineers raise $20M for platform Melius…》**〔Ramp 前员工 AI 广告素材生成平台 `Melius` 融资 $25M·$20M A 轮 CRV 领投 ＋ $5M 种子 GC 领投·自称两月年化营收 >$1M；归第 5 类〕）流水原文已滚入 `daily-memories-news/2026-10-07.md`（📦 滚动归档 · 第七十七轮 07:50 为 MEMORY≤32KB 归档；原文不改）。

- 🔀 **第七十四轮**（2026-10-07 ~06:06，news +0：窗口 0.55h 无新 AI 事件 → 如实留空）流水原文已滚入 `daily-memories-news/2026-10-07.md`（📦 滚动归档 · 第七十七轮 07:50 为 MEMORY≤32KB 归档；原文不改）。
- 🔀 **第七十三~六十三轮**（2026-10-07 00:02~05:33，共 **11** 轮；news +7：73 Underdog〔Qwen3.8-27B 端侧隐私助理〕· 72 Musubi `PolicyLM-1.7B`〔开放权重实时审核〕· 71 Lambda 拟融资 $4B〔投前 $14.5B〕· 70 Wajo〔前 DeepMind 工程师 agent 创业·Khosla〕· 67/66/69 窗口无新 AI 事件〔**news +0 如实留空**〕· 65 Mirror Particle「人类行为世界模型」· 64 Google `EmbeddingGemma 2` 〔端侧多模态嵌入〕· 63 Anthropic 赠初创一年 Claude Team + $1,000 credits）流水**原文已滚入** `daily-memories-news/2026-10-07.md`（📦 滚动归档 · **2026-10-08 06:10 为 MEMORY≤32KB 归档**；**原文不改·结论不变**）。

- 🔀 **第六十二轮**（2026-10-06 ~23:33，news +2：IT之家 德国交通部长盼特斯拉 FSD（监督版）获欧盟批准 · TechCrunch：LibreOffice 把「no AI」当特性）流水原文已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 2026-10-07 00:36 为 MEMORY≤32KB 归档；原文不改）。


- 🔀 **第六十一轮**（2026-10-06 ~22:54，news +1：**IT之家《AMD 股价创历史新高！CEO 苏姿丰称 AI 芯片需求非常旺盛，将持续大幅扩产》**〔10-06 22:30:54 CST `010/114`；归第 5 类〕）流水原文已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第六十一轮 22:54 心跳；原文不改）。

- 🔀 **第六十轮**（2026-10-06 ~22:19，news +4：IT之家 Mistral Large 4 公开预览版〔1 万亿总参 / 490 亿激活 · 月底开放权重〕· 英伟达市值 5.8 万亿美元创历史新高 · TechCrunch Pinterest AI Beauty Guides · TechCrunch Flai AI 经销软件〔2,700 万美元 A 轮〕；`SEEN.md` +6）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- 🔀 **第五十九轮及更早（第五十九~十九轮 + 第 10 批块）**：流水原文（第五十九轮 news+0 · 第五十八轮 CTV News Claude 救生 · 第五十七轮 SAP 收购 TechWolf · 第五十六轮 谷歌×Constellation 电力协议 / Mistral 预告 / Guardian 品牌风险 · 第五十五轮 404 Media Meta Muse 逃逸 / Osna.FM 德国 MAD / Guardian 抗议 · 第五十四~十九轮 + 第 10 批块）均已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第六十九轮 03:21 / 第七十八轮 08:10 归并；原文不改）。
