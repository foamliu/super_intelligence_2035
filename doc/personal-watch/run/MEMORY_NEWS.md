# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~三十七轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序已收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库（75,610 条，对 15:10 全量快照）· N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + **§4.4 措辞强度 tone 信号**，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md，9 行）+ **G2′④ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）**
当前动作:     **本唤醒：第三十八轮常态采集（news **+0**：本轮**无新增**——⏱ 窗口 ~0.3h 紧接第三十七轮 + 国庆假期，中外权威源 AI 类**零命中**；`cn_news` 30 条均假期/民生/时政/体育/文旅、量子位/IT之家/爱范儿/雷峰网头部均已在账/非清单/超窗/非新闻，TechCrunch/Verge/Ars 头部均**已在账/同事件**（TechCrunch《OpenAI 欧盟文本水印》与在账 IT之家 `009/903` 同事件）/非 AI，HN 候选皆 tool/analysis/超窗或 BBC `HTTP 000` 不可达〔已在账 news(未核验)〕→ **如实留空、不凑数**〔§0.0.2〕**）。**上一唤醒：第三十七轮常态采集（news +2：TechCrunch Etched 融资要约 $40B+ · The Verge Nolla AI 自主处方试点）。**再上一唤醒：第 10 批 B 线 **P7（公开 RSS 核验）**——核验 Apple Podcasts / 蜻蜓FM / 喜马拉雅 / 小宇宙 → **未发现**《衍射+东方时事解读音频》的**公开 RSS/播客** → **P7 关闭**，B 线获取路径回到 **P2 待拍板**；产物 `news/dongfang/METHODS.md` + `report.html` 就地更新。**（更早唤醒·第 35/34/33 轮详见 §2 流水）**
下一步:       ① **第 10 批 B 线**：**P7 已核验 → 未发现公开 RSS/播客（P7 关闭）**；**仍待用户拍板 P1–P6**（`dongfang/report.html` §8：目标确认 P1 / 获取路径授权 P2〔**RSS 路线已排除 → 请在 P2(b) 用户登录态导出 / P2(c) 暂不实施 间选择**〕/ 仅个人使用 P3 / 音频存哪 P4 / 文字稿粒度 P5 / 更新时段 P6）→ **拍板前不实施日更**；② **G2′④ 累积**：**≥20h 后（约 2026-10-06 ≥11:10）**跑真实重跑（`cycle_run.py --with-l2`，**不带 `--record`**）追加台账（**台账自报：连续 1 天 / 目标 7 天，未达标**）；③ 常态采集续跑（**国庆假期中文权威源 AI 类稀薄 → 如实留空**）；④ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；⑤ L3（N5）**冻结**
本轮新增:     **第三十八轮常态 news **+0**（中文 0 / 英文 0；当日 **12** / 累计 **119**）**：本轮**无新增**（如实留空，不凑数）。**源盘点（如实）**：`cn_news`（限 30）均国庆假期/民生/时政/体育/文旅（`AI/人工智能/大模型/芯片/算力/机器人/智能` 标题零命中）→ 不收；**联合国中文源仍 404**；量子位头部《诺奖光遗传学》〔非 AI〕→ 不收，余（501705/501700/501605/501506/501451/501381/501368）均已在账 → 去重；IT之家 `009/901~908` 均已在账/非清单 → 去重；爱范儿头部 feature/opinion 或超窗（≤10-04）→ 不收；雷峰网头部 09-30~10-04 → 超 72h 窗；TechCrunch 头部《OpenAI 欧盟文本水印》〔20:36〕与在账 IT之家 `009/903` **同事件**→去重，余者均已在账/推介/feature/非 AI；The Verge/Ars 头部均**已在账/同事件/非 AI**（Verge《Wikipedia rogue bots》与在账 Wikimedia 官方同事件、Verge《Shield 涨价》与在账 Ars 同事件）→ 去重；`search_news`(HN `AI`/`Anthropic regulation`) 候选皆 Show/Ask HN·tool·analysis·**超窗**〔Anthropic regulation 全 08-16~09-30〕或 **BBC Pentagon×Anthropic `HTTP 000` 不可达**〔已在账 news(未核验)〕→ 拒收/去重。→ `SEEN.md` 追加 2 条 `news(同事件)`（TechCrunch 水印 · Verge Wikipedia）。 ┃ **（第 37 轮及更早见 §2 流水）**
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）｜🆕 **第 10 批**：⚠️ **`mcp<2` 已成运行机全局 pin**（2.3.0 → **1.30.0**，否则 `mcp_ddgs`/离线自检不可用）→ 与需 **mcp 2.x** 的其它线**可能冲突**，**待 supervisor 确认**；⚠️ **ddgs 8/8 引擎被墙**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但结果端点被拦）→ 免费通用 web 搜索**本机不可用**，日常仍以 `cn_news` + 官方 RSS 为准；⚠️ **CN-Bing 抓取相关性降级**（查「人工智能 最新 政策」返回「人工」词条 → 200 ≠ 有料）
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
- **上次采集窗口**：`2026-10-06 04:40 CST` 第三十七轮 ~ `2026-10-06 05:00 CST` 第三十八轮
- **累计收录**：`199` 条（**news 119**〔第一~三十七轮；当日 12〕+ 非新闻 82〔仅存 `SEEN.md`〕）

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-06（本唤醒 ~05:00）** —— 🆕 **第三十八轮常态采集：news +0（中文 0 / 英文 0；当日 12 / 累计 119，本类无新增）**。
  - **本轮无新增**（如实留空，不凑数；§0.0.2「负面结果可接受」）。⏱ 窗口 ~0.3 小时（紧接第三十七轮）+ 国庆假期 → 中外权威源 AI 类零命中。
  - **源盘点（如实）**：`cn_news`（限 30）均**假期/民生/时政/体育/文旅**（六张网、迪拜航空险情、国庆游客体验、云岭长征、国庆消费、青稞特写、超三联赛、WTT、村BA、东北超、国庆档票房破 8 亿、英国反移民抗议…）→ `AI/人工智能/大模型/芯片/算力/机器人/智能` 标题零命中 → 不收；**联合国中文源仍 `HTTP 404`**；量子位头部《诺奖颁给光遗传学》〔非 AI〕→ 不收、余均已在账；IT之家 `009/901~908` 均已在账/非清单；爱范儿头部 feature/opinion 或超窗；雷峰网头部 09-30~10-04 超窗；TechCrunch 头部《OpenAI will start watermarking ChatGPT's text in the EU》〔10-05 20:36〕与在账 IT之家 `009/903` **同事件** → 去重，余者均已在账/推介/feature/非 AI；The Verge/Ars 头部均**已在账/同事件/非 AI**（Verge《Wikipedia rogue bots》与在账 Wikimedia 官方同事件、Verge《Nvidia Shield $100 涨价》与在账 Ars 同事件）→ 去重；`search_news`(HN `AI`/`Anthropic regulation`) 候选皆 Show/Ask HN·tool·analysis·**超窗**〔Anthropic regulation 全 08-16~09-30〕或 **BBC Pentagon×Anthropic `HTTP 000` 不可达**〔已在账 news(未核验)〕→ 拒收/去重。
  - **台账**：`SEEN.md` 追加 2 条 `news(同事件)`（TechCrunch 水印 · The Verge Wikipedia）以防重复评估。
  - **G2′④**：距上次真实重跑（2026-10-05 15:10）约 **13.8h <20h** → **不做真实重跑、不刷台账连续性**；连续性自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（下一窗 ≥20h 真实重跑约在 **2026-10-06 ≥11:10**）。
  - **判据复核**：✅ 无新增即如实留空（不凑数）· ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。


- **2026-10-06（本唤醒 ~04:40）** —— 🆕 **第三十七轮常态采集：news +2（中文 0 / 英文 2；当日 12 / 累计 119）**。
  - **① TechCrunch《Etched fields funding offers at $40B+ valuation, sources say》**（10-05 20:24 UTC；本机实测 `HTTP 200` + `Content-Type: text/html` + `datePublished 2026-10-05T20:24:09+00:00`，在窗）：**AI 芯片初创 Etched** 在**仅两个月前**以 **210 亿美元估值融资 7 亿美元**后，**已收到翻倍乃至更高的投资要约** —— 据知情人士，正在评估的报价为**顶级投资方 400 亿美元** ~ **知名度较低投资方 500 亿美元**；**谈判仍早期**、条款或变；**Etched 拒绝置评**。→ 第 5 类「公司与人物动态（AI 芯片公司估值）」兼第 1 类「前沿模型与能力（算力硬件）」。
  - **② The Verge《Nolla Health will now use AI to review face scans and write acne prescriptions in Utah》**（10-05 20:14 UTC；本机实测 `HTTP 200` + `datePublished 2026-10-05T20:14:57+00:00`，在窗；援引 Bloomberg 更早报道）：医疗健康初创 **Nolla Health** 周一（10-05）宣布，**犹他州**居民可用其 App **扫描面部**，由 **AI 分析痤疮严重度并自主书写处方**；以**试点**推出、**医师监督逐步放松**（**前 100 名患者**的每一份 AI 处方须由**两名医师**在签发前批准，此后医师**仅抽查式复核**）。→ 第 4 类「AI 与社会（医疗/伦理）」兼第 3 类「政策与治理（自主处方监管边界）」。
  - **源盘点（如实）**：`cn_news`（限 30）均**假期/民生/时政/体育/文旅**（AI 标题零命中）→ 不收；**联合国中文源仍 404**；量子位/爱范儿/雷峰网/IT之家头部均**已在账/非清单/超窗/非新闻**，TechCrunch/The Verge 余者均**已在账/推介/feature/非 AI**，Ars 本轮未取 → 去重/不收；**`search_news`(HN `AI`/`Anthropic`) 新候选 = BBC《Pentagon stops using Anthropic AI tools after blacklisting company》〔10-05〕** —— ⚠️ **本机 `HTTP 000`（`bbc.co.uk` / `bbc.com` / `feeds.bbci.co.uk` 全不可达）且 HN 无任何可核验的替代同事件源** → 按铁律**未核验、不收录**（记 `SEEN.md` `类型：news(未核验)`）；余皆 Show/Ask HN·tool·opinion·analysis·同事件 → 拒收/去重。
  - **G2′④**：距上次真实重跑（2026-10-05 15:10）约 **13.5h <20h** → **不做真实重跑、不刷台账连续性**；连续性自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（下一窗 ≥20h 真实重跑约在 **2026-10-06 ≥11:10**）。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。


- **2026-10-06（本唤醒 ~03:52）** —— 🆕 **第三十六轮常态采集：news +2（中文 0 / 英文 2；当日 10 / 累计 117）**。
  - **① TechCrunch《Reflection debuts Beam, an open-weight AI model to rival Chinese models at lower compute cost》**（10-05 12:33；本机实测 `HTTP 200`，在窗）：**Reflection AI**（纽约布鲁克林，2024 年两名前 Google DeepMind 研究员创立）发布**首个前沿开放权重模型 Beam** —— **纯文本 MoE，501B 总参 / 23B 激活，23.8T token 预训练，1M 上下文**；**自称**高级推理基准与 **Z.ai GLM-5.2**（744B/40B）**相当**、**优于领先西方开源模型**且**推理算力省 3–4×**（⚠️未经独立验证）；**累计融资约 47 亿美元**（Nvidia/Sequoia/Lightspeed；上轮投前估值约 250 亿美元）、与 **SpaceX/Nebius** 签**逾 70 亿美元**算力协议（GB300 至 2029）；面向企业与**主权国家**推销「**AI 工厂**」（韩国 Shinsegae 试点）；**权重本月发布**。→ 第 1 类「前沿模型与能力」兼第 3 类「政策与治理（主权 AI）」。📎 官方博客（`reflection.ai/blog/introducing-beam`）· Semafor **同事件**不重复收录。
  - **② TechCrunch《After Factory's public spat with Khosla, Menlo proudly invests》**（10-05 12:38；本机实测 `HTTP 200`，在窗）：**Menlo Ventures** 宣布投资 **AI 编程初创 Factory**（属其上月按 **50 亿美元估值**宣布的融资轮，金额未披露、称「非象征性」）；背景为 Factory CEO **Matan Grinberg** 与投资人 **Chris Degnan**（后加入竞争对手 **Cognition** 任 CRO）的公开争执、**Vinod Khosla** 称 Factory 为「**苦苦挣扎的二线竞争者**」。→ 第 5 类「公司与人物动态」。
  - **源盘点（如实）**：`cn_news`（限 30）均**假期/民生/时政/体育/文旅**（AI 标题零命中）→ 不收；**联合国中文源仍 404**；量子位/爱范儿/雷峰网/IT之家/钛媒体头部均**已在账/非清单/超窗/非新闻**；TechCrunch 余者均已在账/推介/feature；The Verge《数学 drama》判 **feature 非新闻**、Ars 头部 tool/非 AI/同事件 → 去重/不收；`search_news`(HN `AI`) 新候选仅 Reflection 同事件，余皆 Show/Tell HN·analysis·opinion·超窗或弱相关（Semafor《AI nonprofit $10M journalism》、Nikkei《Toshiba HDD》）→ 拒收/去重；`web_search`(CN-Bing) 本轮超时。
  - **G2′④**：距上次真实重跑（2026-10-05 15:10）约 **12.7h <20h** → **不做真实重跑、不刷台账连续性**；连续性自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（下一窗 ≥20h 真实重跑约在 **2026-10-06 ≥11:10**）。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。


- **2026-10-05（本唤醒 ~23:40）** —— 🆕 **用户直派「第 10 批」A/B 双线（非常态采集，零 news 增量）**。
  - **A 线（免费 web-search MCP 装进 cline）**：依赖装齐（`ddgs 9.16.0` / `beautifulsoup4` / **`mcp<2` 关键 pin：2.3.0 → 1.30.0** / `faster-whisper 1.2.1` / `imageio-ffmpeg`，均 `--user --break-system-packages` + 清华镜像）；离线自检 `news/mcp_ddgs/web_search_selftest.py` **全 PASS**（**前提 mcp 1.x**）；**已注册进 cline 3.0.68**（`~/.cline/data/settings/cline_mcp_settings.json`，`transport.type=stdio`，**无 key**）→ `cline config mcp` 可见 `web-search`（6 工具）/ `web-search-free`（4 工具），**stdio 握手成功**。**逐引擎实测：ddgs 8/8 后端全 FAIL**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但**结果端点被拦**）→ **免费通用 web 搜索本机不可用（网络所限，非配置问题）**。产出 **`news/MCP_INSTALL.md`**（安装/实测/逐引擎表/根因/结论）。
  - **B 线（《衍射+东方时事解读音频》获取与转写 · 只调研不实施日更）**：确认目标 = 汇智 `dongfangtime.com/huizhi/yspd/`（**仅 HTTP**）音视频频道的**《衍射+东方时事解读音频》**（**每日 5 期 + 直播回放 1 期**；**年卡 398 / 月卡 46**；期号样本 **第 9657–9666 期**）；音频托管在**小鹅通 H5 `xet.pomoho.com`**，未登录态 **302 无限跳转**；微信服务号 = **衍射传媒**；`yanshe.org.cn` 有反下载（「未经协议授权禁止下载」/「10 分钟后自动关闭音频」）→ **官方无下载入口**。**ASR 可行性实测**：`faster-whisper` tiny / int8 / cpu on 2C4G → **RTF 0.024、峰值 258 MB**（模型经 `hf-mirror.com` 下载，须设 **`HF_HUB_DISABLE_XET=1`**；`base` 探针下载中停滞于 123 MB → **放弃，tiny 结论已足**）。产出 **`news/dongfang/report.html`**（自包含报告，覆 7 点）+ **`news/dongfang/METHODS.md`**（底稿）。
  - **同步**：`news/README.md`（新增 3 行文件表 + 红线第 6 条）· `news/FETCH_CN_NEWS.md`（头部加第 10 批状态注）· 本 MEMORY 顶部快照 + 阻塞。
  - **待拍板（7 项，见报告 §8）**：P1 目标确认 / P2 获取路径授权 / P3 仅个人使用 / P4 音频存哪（**本机无 bypy**）/ P5 文字稿粒度 / P6 更新时段 / P7 是否上 RSS 核验。→ **拍板前不实施日更**。
  - **判据复核**：✅ 区分「**已实测 / 据文档 / 待验证**」全篇标注 · ✅ 未编造任何接口/期号 · ✅ 未取得音频如实写「无内容」 · ✅ 不绕付费墙 · ✅ 音频不入 git · ✅ **第 10 批零 news 增量**（未污染 §0.1 计数）。

- （更早流水：**2026-10-06 ~01:24 第三十一轮**（The Verge《OpenAI PR 要求记者 move on》；已归档 `daily-memories-news/2026-10-06.md`）· **2026-10-06 ~00:13 / ~00:52 第二十九~三十轮**（已归档 `daily-memories-news/2026-10-06.md`）· **2026-10-05 22:13/22:49 第二十七~二十八轮**（The Verge StarCraft 破规作弊 · TechCrunch 中国 AI「agent fleet」；由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 21:05/21:37 第二十五~二十六轮**（常态采集；本轮第 10 批唤醒由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 18:45~20:26 第二十一~二十四轮**（常态采集；本轮 22:49 由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 17:25/17:55 第十九~二十轮**（TechCrunch 超级智能部队 · 钛媒体 SpaceXSI · TechCrunch 联邦法官裁定 Flock；已归档 `daily-memories-news/2026-10-05.md`）· **2026-10-05 16:12 第十六~十七轮**（L1 §4.3 固定召回率 precision 加固 + IT之家索尼×Meta 专利）→ 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-05 早期**（恢复 27h 停摆首轮 · N1 2021/2022 续抓）· **N1 第 3/4/5/6 轮抓取（2020→2019→2017/2018→2016）+ 第十一~十五轮常态采集 + 全链重跑** → 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-03 各轮 / 2026-10-04 各轮**（L1/N3 收口、N4/L2、L1 链重跑+轴对齐）→ `daily-memories-news/2026-10-03.md` · `daily-memories-news/2026-10-04.md`；第三~九轮 / 第二轮 / 首轮 smoke / 前期任务 T1–T4 / 建线 / 首轮空转 亦在其中）

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
