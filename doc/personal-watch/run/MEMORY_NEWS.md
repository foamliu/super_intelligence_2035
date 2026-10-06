# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）** + **任务书自滚归档（已把第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`；每次唤醒按 ≤32KB 自检）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~六十轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库 75,610 条 · N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + §4.4 措辞强度 tone 信号，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md）+ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）· **任务书自滚归档（第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`）** · **第六十轮常态采集（news +4：Mistral Large 4 · 英伟达市值新高 · Pinterest AI Beauty Guides · Flai A 轮）** · **第六十一轮常态采集（news +1：AMD 股价创历史新高·苏姿丰称 AI 芯片需求旺盛）** · **第六十二轮常态采集（news +2：德国交通部长盼特斯拉 FSD〔监督版〕获欧盟批准 · TechCrunch：LibreOffice 把「no AI」当特性）**
当前动作:     **本唤醒：第六十二轮常态采集（news +2：中文 1 / 英文 1）** —— 窗口约 **0.65h**（第六十一轮 22:54 → 本次 23:33）。**两条实际发布时刻均落在本轮窗口内**：**① IT之家《德国交通部长：希望特斯拉 FSD（监督版）辅助驾驶系统能在欧盟获批》**（`010/124`，**23:06:34 CST**，本机 `HTTP 200`，据 Golem 当日报道；归第 3 类）· **② TechCrunch《LibreOffice says 'no AI' is now a software feature》**（**23:25 CST**，本机 `HTTP 200`；The Document Foundation 称可预见未来不为软件加入 AI、把「no AI」当设计立场/特性；归第 4 类）。盘：`cn_news`(限 80，活源 6) 均假期返程/民生/时政/文旅/财经，`AI/…` **零命中**；**联合国中文源仍 404**；IT之家 `010/123` 明日方舟游戏〔非 AI〕· `010/107` 杨利伟空间站 · `010/103` 任天堂 · `010/102` 宝马 · `010/098` 显卡驱动〔均非 AI〕、余已在账/同事件/非 AI；量子位头部 非 AI/analysis；TechCrunch 头部 `Mistral 1T model`〔**同事件·在账 `010/108`**〕· `Pinterest AI Beauty Guides`〔在账〕、余非 AI/已在账；The Verge/Ars/404 Media 头部均已在账/同事件/非 AI/非新闻；`search_news`(HN `AI`) 命中多 tool/analysis/同事件 → 拒收/去重，**本轮未超时**。**体积**：TASK=**31.6KB** / MEMORY≈**31KB** 均 ≤32KB → **无需归档**。**上一唤醒**：第六十一轮（+1：AMD 市值新高）详见 §2 流水。
下一步:       ① 常态采集续跑（窗口内新 AI 事件照收、无则如实留空）；② **G2′④ 累积**：维持 ≥20h 真实重跑节奏（下一窗约 `2026-10-07 ≥07:24`），**如实自报连续天数/未达标**（`STABILITY_LOG.md`）；③ **第 10 批 B 线**：**仍待用户拍板 P1–P6/P7**（`news/dongfang/report.html` §8）→ **拍板前不实施日更**；④ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；⑤ L3（N5）**冻结**；⑥ **任务书/MEMORY 自滚归档**（>32KB 目标 / >40KB 红线前先搬 `WATCH_NEWS_TASK_ARCHIVE.md` / `daily-memories-news/`）
本轮新增:     **第六十二轮常态 news +2（中文 1 / 英文 1；当日 **52** / 累计 **159**）**——德国交通部长盼特斯拉 FSD〔监督版〕获欧盟批准（第 3 类）· TechCrunch：LibreOffice 把「no AI」当特性（第 4 类）。→ `SEEN.md` **+3 行**（2 news 收录 + 1 防重：IT之家 `010/123` 明日方舟游戏·非 AI）。┃ 第六十一轮（news +1）见 §2 流水
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）｜🆕 **第 10 批**：⚠️ **`mcp<2` 已成运行机全局 pin**（2.3.0 → **1.30.0**，否则 `mcp_ddgs`/离线自检不可用）→ 与需 **mcp 2.x** 的其它线**可能冲突**，**待 supervisor 确认**；⚠️ **ddgs 8/8 引擎被墙**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但结果端点被拦）→ 免费通用 web 搜索**本机不可用**，日常仍以 `cn_news` + 官方 RSS 为准；⚠️ **CN-Bing 抓取相关性降级**（查「人工智能 最新 政策」返回「人工」词条 → 200 ≠ 有料） ｜📦 **体积：TASK=31.6KB / MEMORY≈30KB（ARCHIVE≈47KB）**（均已 ≤32KB 目标；soft 32KB / 红线 40KB）
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
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-06 22:54 CST` 第六十一轮 ~ `2026-10-06 23:33 CST` 第六十二轮（**第六十二轮为本轮唤醒**）
- **累计收录**：`news` **159** 条（第一~六十二轮；当日 **52**）+ 非新闻（口径=逐行统计 `SEEN.md` 类型列）〔**仅存 `SEEN.md`**〕

---

## 2. 流水（倒序，保留最近 ~20 条）


- **2026-10-06（本唤醒 ~23:33）** —— 🆕 **第六十二轮常态采集：news +2（中文 1 / 英文 1；当日 52 / 累计 159）**：**① IT之家《德国交通部长：希望特斯拉 FSD（监督版）辅助驾驶系统能在欧盟获批》**（10-06 **23:06:34 CST** `010/124`，本机实测 `HTTP 200`，据外媒 Golem 当日报道；作者潞源）：**德国联邦交通部长施特芬·比尔格表示，希望特斯拉 FSD（监督版）辅助驾驶系统能在欧盟范围内获批**，认为欧盟统一审批类似系统具积极意义；他称审批**涉及很多待解决的技术问题、且需划分好责任认定**，对其而言**推动创新落地最重要**，并称该监督版**有望提升德国道路交通安全、望其尽快在欧洲投入使用**；另注：**特斯拉今年 4 月称 FSD（监督版）将于数月内在全欧盟获批**，但**该系统实为 L2 级辅助驾驶、驾驶员须始终准备接管方向盘**。归第 3 类〔自动驾驶/辅助驾驶的监管审批〕；**如实归属为部长「表示/希望」、非既成决定**。**② TechCrunch《LibreOffice says 'no AI' is now a software feature》**（**23:25 CST**，署名 Zack Whittaker，本机实测 `HTTP 200`）：**The Document Foundation（TDF）本周在博客表示**，虽不完全排斥 AI，但**在可预见未来「不会向软件中加入」AI** → 报道标题化为「no AI」本身成特性；回顾 TDF **8 月底发布新版本时即重申「不含生成式 AI 功能」**、称这是**「深思熟虑的设计立场」**，以确保**用户文档不上传服务器处理、软件任何部分均无需联网运行**；TDF 称其有**数千万用户**、用户应**保有对自身数据的控制权**，并引其原话「**唯一经得起审计的保证，就是数据不离开本机**」；另注用户仍可**装扩展/接本地模型**用 AI，TDF 称当前**无 AI 集成满足其全部要求**、其标准**非断然拒绝、而是对当下技术的评估**，「**在那之前默认安装中不会有任何形式的 AI**」。归第 4 类〔软件生态对 AI 渗透的态度 / 数据主权〕。**源盘点**：`cn_news`（限 80，活源 6）均假期返程/民生/时政/文旅/财经/气象（IMF 对冲基金风险、以色列旅行警告、商务部涉欧答问、香港自由度评级、拉脱维亚组阁、法国凡尔赛宫停电、诺奖物理、俄莫无人机袭…），`AI/…` **正则零命中** → 不收；**联合国中文源仍 404**；IT之家 `010/124` 已收、`010/123` 明日方舟·RTX Spark 笔记本〔非 AI·游戏〕· `010/107` 杨利伟空间站 · `010/104` 亚马逊艾美奖 · `010/103` 任天堂 · `010/102` 宝马 · `010/098` 显卡驱动〔均非 AI〕→ 不收/去重；量子位头部 诺奖物理/陶哲轩/OpenAI 28 天/Hinton RSI〔非 AI/analysis〕→ 不收；**TechCrunch** 头部 `Mistral's new 1T model…`〔**同事件·在账 `010/108`**〕· `Pinterest AI Beauty Guides`〔在账〕、余 `Disrupt 议程/Battlefield 评委`〔推介〕· `OpenAI 欧盟水印/Reflection Beam/Instinct/TikTok 购物助手/Hot Girl/HackerRank/OpenAI 视觉广告/Chinese AI agent fleet`〔已在账/feature〕→ 去重/不收；**The Verge `ai`**（10 条）头部 `Google 撤免费 Gemini`〔**同事件·在账 IT之家 10-03**〕· `Alexa lalala`〔非清单〕· 余已在账/feature/podcast → 去重；**Ars `ai`**（15 条）头部 `OpenAI agents hack Wikipedia`〔**同事件·已在账 Wikimedia**〕· `MCP agent-to-agent/Apple Intelligence 移除工具/AI glasses Norway/Chegg 诉讼`〔在账/非清单/超窗〕→ 去重；**404 Media `rss`**（15 条）头部 `404@3`〔newsletter〕· `Flock 立法`〔**同事件·在账 10-02**〕· 余已在账/非 AI → 去重；**`search_news`(HN `AI`)**（20 条）多 `Show HN`〔tool〕· 博客/Substack〔analysis/opinion〕· `openai.com《Building advertising…》`〔**同事件·在账**〕· Nobel 物理/GTA 浏览器版/revenue tax〔非 AI〕→ 拒收/去重，**本轮未超时**。**源健康度**：IT之家 / TechCrunch / The Verge / Ars / 404 Media / 量子位 / 中新网 / 央视网 均 `200`；**联合国中文源 `HTTP 404`**；**DDGS `web_search` 仍 8/8 引擎被墙**。**台账**：`SEEN.md` **+3 行**（2 news 收录 + 1 防重〔`010/123` 明日方舟·游戏非 AI〕）。**G2′④**：距上次真实重跑（2026-10-06 11:24）约 **12.2h < 20h** → **不做真实重跑、不刷连续性**（自报仍 **连续 2 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 约在 **2026-10-07 ≥07:24**）。**体积**：TASK=**31.6KB** / MEMORY≈**31KB**（ARCHIVE≈47KB）均 ≤32KB → 无需归档。**判据复核**：✅ 标题+来源+发布日期+链接 · ✅ 两条均本机实测原文 `HTTP 200` 并核验发布时刻 · ✅ 自动驾驶项与在账「台达×英伟达 Hyperion」（10-05）同域不同主体·单列不合并 · ✅ 部长表态如实归属为「表示/希望」 · ✅ 非 AI（游戏/消费外设/整车销量/显卡驱动）与 promo/newsletter/discussion/feature 从严不收 · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。


- **2026-10-06（本唤醒 ~22:54）** —— 🆕 **第六十一轮常态采集：news +1（中文 1 / 英文 0；当日 50 / 累计 157）**：**① IT之家《AMD 股价创历史新高！CEO 苏姿丰称 AI 芯片需求非常旺盛，将持续大幅扩产》**（10-06 **22:30:54 CST** `010/114`，本机实测 `HTTP 200`，在窗；作者沁沧）：**AMD 盘初涨近 3%，报 649.88 美元创历史新高，市值达 1.06 万亿美元**；开盘后回落、涨超 2% 报 646.48 美元；**CEO 苏姿丰当日受访：2026 年整体运算市场需求极为强劲，AMD 虽已同步扩产但需求仍远高于供给，预计 2027 年将大幅扩增产能**；另注：**上月（9 月）AMD 股价累计涨约 30%、总市值首次突破 1 万亿美元**；**9 月 28 日 AMD 宣布将以 82 亿美元收购 AI 初创公司 World Labs**。归第 5 类〔头部芯片公司市值 / 关键人物言论 / 资本动向〕，与在账《英伟达市值 5.82 万亿美元创历史新高》**同一主线**。**源盘点**：`cn_news`（限 80，活源 6）均假期返程/民生/时政/文旅/财经（商务部涉欧答问、香港自由度评级、法国凡尔赛宫停电、冯德莱恩涉黑海、国庆档票房…），`AI/…` **正则零命中**（唯一「华为…AI 时代计算架构」已在账·`analysis` → 不收）；**联合国中文源仍 404**；IT之家 `010/114` 已收、`010/111` 特斯拉印度〔非 AI〕· `010/110` Gigaphoton 氖气回收〔半导体供应链·非清单〕· `010/098` 显卡驱动〔非 AI〕、`010/106` 电商促销、`010/112`/`010/113` 为 404、余 `010/109`~`010/101` 已在账/同事件/非 AI → 不收；量子位头部 诺奖/陶哲轩/OpenAI 28 天〔非 AI/analysis〕→ 不收；**TechCrunch** 头部 `Mistral's new 1T model…`〔**同事件·已在账 `010/108`**，原文实测 200〕、余 `Bluesky/Emmys/Uber/Paramount/Type One/Lucid/Facebook`〔非 AI〕· `Pinterest/Flai/Etched/Reflection/Instinct/OpenAI 水印/TikTok/Menlo×Factory`〔已在账〕→ 去重/不收；**The Verge `ai`**（10 条）/ **404 Media `rss`**（15 条）/ **Ars**（12 条）头部**均已在账 / 同事件 / 非 AI / 非新闻** → 去重；**`search_news`(HN)**：`AI`（10，未超时）/`AI safety`（8）/`ChatGPT ads`（6）命中多 `Show/Tell HN`〔tool〕· 博客〔analysis〕· `openai.com《Building advertising…》`〔**同事件·在账 OpenAI 视觉广告**〕→ 拒收/去重，`Gemini` 查询 **`ReadTimeout`**、`Gemini 4 Argon` = 在账量子位 10-03 同模型。⚠️ **`search`(HN) 间歇超时**；**DDGS `web-search` 仍 8/8 引擎被墙**。**台账**：`SEEN.md` **+4 行**（1 news 收录 + 3 防重）。**G2′④**：距上次真实重跑（2026-10-06 11:24）约 **11.5h < 20h** → **不做真实重跑、不刷连续性**（自报仍 **连续 2 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 约在 **2026-10-07 ≥07:24**）。**体积**：TASK=**31.6KB** / MEMORY≈**31KB**（ARCHIVE≈47KB）均 ≤32KB → 无需归档。**判据复核**：✅ 标题+来源+发布日期+链接 · ✅ 本机实测 `HTTP 200` 核验发布时刻 · ✅ 融资/收购/市值标注口径 · ✅ 非 AI 从严不收 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。

- 🔀 **第六十轮**（2026-10-06 ~22:19，news +4：IT之家 Mistral Large 4 公开预览版〔1 万亿总参 / 490 亿激活 · 月底开放权重〕· 英伟达市值 5.8 万亿美元创历史新高 · TechCrunch Pinterest AI Beauty Guides · TechCrunch Flai AI 经销软件〔2,700 万美元 A 轮〕；`SEEN.md` +6）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- **2026-10-06（本唤醒 ~21:45）** —— 🆕 **第五十九轮常态采集：news +0（中文 0 / 英文 0；当日 45 / 累计 152）**：**本轮无新增**（窗口约 **0.65h**，紧接第五十八轮 + 国庆假日晚间 → 中外权威源 AI 类**零新事件**，如实留空、不凑数）。源盘点：`cn_news`（限 60，活源 6）中新网/央视网 60 条均**假期返程/民生/时政/文旅/体育/气象**（外交部涉台/涉菲/涉欧答问 · 国庆档票房破 10 亿 · 诺奖物理 · 莫斯科无人机袭 · 台风「小熊」…），`AI/…` 标题正则**仅 1 处命中且已超龄 82.2h>72h 丢弃**（央视《AI 眼镜给稻田精准…》）→ 不收；**联合国中文源仍 404**；IT之家新头部 `010/105` 红魔手机 · `010/104` 亚马逊 Prime Video 艾美奖 · `010/103` 任天堂 Switch 儿童游戏 · `010/102` 宝马标准化零部件 · `010/101`《战争机器》Xbox 性能〔**均非 AI**〕；余者（`010/097`/`010/096`/`010/094`/`010/093`/`010/091`/`010/090`/`010/074`/`010/063`/`010/048`/`010/043`/`010/038`/`010/037`/`010/036`/`010/035`/`010/033`）**均非 AI / 已在账 / 同事件** → 去重/不收；量子位 `501746`《诺奖物理一人独揽》· `501720`《诺奖光遗传学》〔非 AI〕· `501736` 陶哲轩 · `501726` OpenAI 28 天〔analysis〕→ 不收/去重；TechCrunch AI（15 条，最新 10-05 20:36）/ The Verge `ai`（10 条）/ Ars `technology-lab`（15 条）/ 404 Media `rss`（15 条）头部**均已在账 / 同事件 / 非 AI / 超窗** → 去重（**The Verge《Google is about to remove free access to Gemini Flash and Pro》**＝在账 IT之家 10-03《10 月 9 日起未订阅用户仅能用 Gemini Flash-Lite》**同事件**；**404 Media《Lawmakers Introduce Multiple Laws to Curb Flock…》**＝在账 Sanders「Ban Flock Act」10-02 **同事件** + **非 AI**〔ALPR 而非 AI〕）；⚠️ **`search_news`(HN) 本轮 `Network is unreachable`（startpage/duckduckgo）超时 → 零候选**；**curl HN Algolia API 本机空返回**；**The Register `ai-and-ml` atom `ParseError`（not well-formed）**；**CN-Bing `web_search`（2 次）返回泛化词条（「人工」词条 / AI 工具导航站）→ 相关性降级**。**台账**：`SEEN.md` **+2 行**（均同事件/非 AI 防重）。**G2′④**：距上次真实重跑（2026-10-06 11:24）约 **10.4h < 20h** → **不做真实重跑、不刷连续性**（自报仍 **连续 2 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 约在 **2026-10-07 ≥07:24**）。**体积**：TASK=**31.6KB** / MEMORY=**~28KB** 均 ≤32KB → **无需归档**。**判据复核**：✅ 无新料如实写「不给新增」不凑数 · ✅ 同事件不同媒体**单列防重不合并** · ✅ feature/discussion/tool/analysis/促销**从严不收** · ✅ 非 AI（汽车/外设/游戏/媒体/消费产品）**不收** · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。

- 🔀 **第五十八轮**（2026-10-06 ~21:06，news +1：CTV News：少年依 Claude 指引受困 B.C.「Widowmaker」后获救）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- 🔀 **第五十七轮**（2026-10-06 ~20:31，news +1：SAP 拟收购 AI 工作智能平台 TechWolf〔SAP 官方公告〕）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- 🔀 **第五十五轮**（2026-10-06 ~19:13，news +3：404 Media Meta Muse「VM 逃逸（KVM escape）」/ Osna.FM〔转述 Der Spiegel〕德国 MAD 用 AI 筛查国防军申请人 / Guardian「Pull the plug」抗议者对 AI 公司直接行动）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- 🔀 **第五十六轮**（2026-10-06 ~19:55，news +3：IT之家 谷歌×Constellation 3.59GW 长期电力协议 / Mistral AI 新模型预告〔网安等方面优于中国竞品〕/ Guardian AI 滥用为品牌最大声誉威胁）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- **2026-10-06（本唤醒 ~18:41）第五十四轮常态采集（news +5：韩国 4.7 万亿韩元专项 / AGCM 调查 Suno / 索尼音乐下架 26 万首 AI 伪造歌曲 / Anthropic CEO 薪酬 / DeepSeek 800 亿元融资）** —— 🗂 明细已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- 🔀 **第五十二~五十三轮流水原文已滚入** `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第五十二~五十三轮，2026-10-06）。


- 🔀 **第五十一轮**（2026-10-06 ~11:56，news +1：IT之家 月之暗面 pre-IPO〔估值约 500 亿美元·明年一季度赴港 IPO〕）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- 🔀 **第五十轮**（2026-10-06 ~11:16，news +2：快手可灵 AI 赴港 IPO 筹备〔募资至少 10 亿美元〕· 中新网 AI 短片<合龙>海外获奖；含 G2′④ 真实重跑 + 任务书自滚归档）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。
- 🔀 **第四十九轮流水原文已滚入** `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第四十九轮，2026-10-06）。

- 🔀 **第四十八轮流水原文已滚入** `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第四十八轮，2026-10-06）。


- 🔀 **第四十七轮**（2026-10-06 ~10:05，news +2：IT之家 GLM-5.3 上架 AWS Bedrock〔智谱海外云分成〕· LG 电子北美超 5GW AIDC 冷水机组）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- 🔀 **第四十六轮**（2026-10-06 ~09:32，news +1：IT之家 空芯光纤〔hollow-core fiber·宁夏中卫智算中心间商用〕）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。
- 🔀 **第四十五轮**（2026-10-06 ~08:55，news +0）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- 🔀 **第四十四轮**（2026-10-06 ~08:22，news +1：IT之家《麦当劳在美遭集体诉讼，被指用 AI 系统非法操纵菜单价格》）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- 🔀 **第四十三轮**（2026-10-06 ~07:48，news +2：Gemini Call-for-Me 爆料 · tvOS 27.2 Apple TV 4K Siri AI 爆料）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- 🔀 **第四十一~四十二轮**（2026-10-06 ~06:41〔+1 Ars MCP〕/ ~07:14〔+0〕）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。
- 🗂 **第三十八~四十轮（10-06 ~05:00 / ~05:33 / ~06:06，均 news +0）** —— 由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- **2026-10-05（本唤醒 ~23:40）** —— 🗂 **用户直派「第 10 批」A/B 双线**（A：免费 web-search MCP 装进 cline〔**依赖装齐 + cline 注册成功，但 ddgs 8/8 引擎被墙 → 本机不可用**〕；B：《衍射+东方时事解读音频》获取与转写调研〔**只调研不实施日更**〕）→ **明细已由滚动机制归档至 `daily-memories-news/2026-10-05.md`**（原文不改）；产物：`news/MCP_INSTALL.md` · `news/dongfang/report.html` · `news/dongfang/METHODS.md`；**待用户拍板 P1–P6/P7**。

- （更早流水：**2026-10-06 ~03:52 / ~04:40 第三十六~三十七轮**（Reflection Beam · Menlo×Factory · Etched 融资要约 · Nolla 处方；本轮由滚动机制平滑归档至 `daily-memories-news/2026-10-06.md`）· **2026-10-06 ~01:24 第三十一轮**（The Verge《OpenAI PR 要求记者 move on》；已归档 `daily-memories-news/2026-10-06.md`）· **2026-10-06 ~00:13 / ~00:52 第二十九~三十轮**（已归档 `daily-memories-news/2026-10-06.md`）· **2026-10-05 22:13/22:49 第二十七~二十八轮**（The Verge StarCraft 破规作弊 · TechCrunch 中国 AI「agent fleet」；由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 21:05/21:37 第二十五~二十六轮**（常态采集；本轮第 10 批唤醒由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 18:45~20:26 第二十一~二十四轮**（常态采集；本轮 22:49 由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 17:25/17:55 第十九~二十轮**（TechCrunch 超级智能部队 · 钛媒体 SpaceXSI · TechCrunch 联邦法官裁定 Flock；已归档 `daily-memori