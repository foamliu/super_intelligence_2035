# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）** + **任务书自滚归档（已把第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`；每次唤醒按 ≤32KB 自检）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~六十轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库 75,610 条 · N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + §4.4 措辞强度 tone 信号，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md）+ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）· **任务书自滚归档（第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`）** · **第六十轮常态采集（news +4：Mistral Large 4 · 英伟达市值新高 · Pinterest AI Beauty Guides · Flai A 轮）** · **第六十一轮常态采集（news +1：AMD 股价创历史新高·苏姿丰称 AI 芯片需求旺盛）** · **第六十二轮常态采集（news +2：德国交通部长盼特斯拉 FSD〔监督版〕获欧盟批准 · TechCrunch：LibreOffice 把「no AI」当特性）** · **第六十三轮常态采集（news +1：TechCrunch Anthropic 赠初创企业一年 Claude Team + 1,000 美元 API credits）** · **第六十四轮常态采集（news +1：Google 官方博客 EmbeddingGemma 2 开放轻量多模态嵌入模型〔基于 Gemma 4 · 端侧〕）** · **第六十五轮常态采集（news +1：TechCrunch Mirror Particle 构建「人类行为世界模型」基础模型〔将亮相 TechCrunch Disrupt Startup Battlefield 200〕）**
当前动作:     **本唤醒：第六十五轮常态采集（news +1：中文 0 / 英文 1）** —— 窗口约 **0.57h**（第六十四轮 00:36 → 本次 **2026-10-07 01:10 CST**；深夜 + 国庆假期末段）。**新增 1 条**：**TechCrunch《Mirror Particle is building a 'world model' of human behavior》**（记者 Rebecca Bellan，原文 `9:35 AM PDT · October 6, 2026` ＝ **2026-10-07 00:35 CST**，本机实测原文可解析；**上一轮 feed 轮询未及 → 本轮补收**；旧金山初创 **Mirror Particle**〔成立两年〕构建**「人类行为世界模型」基础模型**，为品牌预测消费者行为及其原因，主张主流 LLM「角色扮演」路线有根本缺陷〔人类＝视觉感知 / 空间推理 / 社会智能〕，将亮相 **TechCrunch Disrupt Startup Battlefield 200**；背景：同类行为预测创企密集融资〔Simile 2 亿 · Aaru 8,800 万 · Humans& 4.8 亿种子〕；归第 1 类）。盘：`cn_news`（限 50，活源 6）均假期返程/民生/时政/文旅/财经/体育（布里斯班奥运会徽 · 澜湄合作洪水预警 · 中国足球队收官 · IMF 对冲基金风险 · 以色列旅行警告 · 商务部涉欧答问 · 《只此青绿》千场 · 拉脱维亚组阁 · 法国凡尔赛宫停电 · 攀岩安全提示…），**无 AI 条目** → 不收；**联合国中文源仍 404**；**IT之家** feed 头部仍 `010/124`〔第六十二轮已账〕、`010/123` 游戏非 AI、`010/098` 显卡驱动非 AI、`010/110` 半导体设备非 AI → 无新 AI 条目；量子位（诺奖物理/陶哲轩减速派/OpenAI 28 天/Hinton RSI/GPT-6 3D）非 AI/analysis/已在账；爱范儿（Mate 90 feature/OpenAI 元老离职信 opinion）非新闻/超窗；TechCrunch 余（`Anthropic…` 第六十三轮 / `LibreOffice` 第六十二轮 / `Mistral 1T` 同事件 / `Pinterest` 第六十轮 / `Disrupt 议程` promo）；The Verge（`We can't just…recording` column、`Wikipedia rogue bots` 同事件）；Ars（`OpenAI hack Wikipedia` 同事件、`VMware` 非 AI、`MCP agent-to-agent` 分析）→ 去重/不收；`search_news`(HN) 候选多 discussion/tool、WSJ Mistral〔同事件·在账〕、Liquid D1/GPT-6.1 Sol〔超窗〕→ 拒收/去重，**本轮未超时**。**体积**：TASK=**31.6KB** / MEMORY≈**30.6KB**（ARCHIVE≈47KB）→ 均 ≤32KB → **无需额外归档**。**上一唤醒**：第六十四轮（+1：Google 官方博客 EmbeddingGemma 2）详见 §2 流水。
下一步:       ① 常态采集续跑（窗口内新 AI 事件照收、无则如实留空）；② **G2′④ 累积**：维持 ≥20h 真实重跑节奏（下一窗约 `2026-10-07 ≥07:24`），**如实自报连续天数/未达标**（`STABILITY_LOG.md`）；③ **第 10 批 B 线**：**仍待用户拍板 P1–P6/P7**（`news/dongfang/report.html` §8）→ **拍板前不实施日更**；④ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；⑤ L3（N5）**冻结**；⑥ **任务书/MEMORY 自滚归档**（>32KB 目标 / >40KB 红线前先搬 `WATCH_NEWS_TASK_ARCHIVE.md` / `daily-memories-news/`）
本轮新增:     **第六十五轮常态 news +1（中文 0 / 英文 1；当日 **3** / 累计 **162**）**——TechCrunch《Mirror Particle is building a 'world model' of human behavior》（第 1 类）。→ `SEEN.md` **+3 行**（1 news 收录 + 2 防重）。┃ 第六十四轮（news +1）见 §2 流水
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）｜🆕 **第 10 批**：⚠️ **`mcp<2` 已成运行机全局 pin**（2.3.0 → **1.30.0**，否则 `mcp_ddgs`/离线自检不可用）→ 与需 **mcp 2.x** 的其它线**可能冲突**，**待 supervisor 确认**；⚠️ **ddgs 8/8 引擎被墙**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但结果端点被拦）→ 免费通用 web 搜索**本机不可用**，日常仍以 `cn_news` + 官方 RSS 为准；⚠️ **CN-Bing 抓取相关性降级**（查「人工智能 最新 政策」返回「人工」词条 → 200 ≠ 有料） ｜📦 **体积：TASK=31.6KB / MEMORY≈30.6KB（ARCHIVE≈47KB）**（均已 ≤32KB 目标；soft 32KB / 红线 40KB）
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
- **上次采集窗口**：`2026-10-07 00:36 CST` 第六十四轮 ~ `2026-10-07 01:10 CST` 第六十五轮（**第六十五轮为本轮唤醒**）
- **累计收录**：`news` **162** 条（第一~六十五轮；当日 **3**）+ 非新闻（口径=逐行统计 `SEEN.md` 类型列）〔**仅存 `SEEN.md`**〕

---

## 2. 流水（倒序，保留最近 ~20 条）


- **2026-10-07（本唤醒 ~01:10）** —— 🆕 **第六十五轮常态采集：news +1（中文 0 / 英文 1；当日 3 / 累计 162）**：**TechCrunch《Mirror Particle is building a 'world model' of human behavior》**（记者 Rebecca Bellan，原文 `9:35 AM PDT · October 6, 2026` ＝ **2026-10-07 00:35 CST**，本机实测 TechCrunch 原文可解析；**上一轮 feed 轮询未及 → 本轮补收**；旧金山初创 **Mirror Particle**〔成立两年〕构建**「人类行为世界模型」基础模型**、为品牌预测消费者行为及其原因，主张 LLM「角色扮演」路线有根本缺陷〔人类＝视觉感知/空间推理/社会智能〕，将亮相 **TechCrunch Disrupt Startup Battlefield 200**；背景：同类行为预测创企密集融资〔Simile 2 亿 · Aaru 8,800 万 · Humans& 4.8 亿种子〕；归第 1 类）。`cn_news`（限 50，活源 6）均假期返程/民生/时政/文旅/财经/体育，**无 AI 条目** → 不收；**联合国中文源仍 404**；IT之家 feed 头部仍 `010/124`〔第六十二轮已账〕、`010/123` 游戏、`010/098` 驱动、`010/110` 半导体设备均非 AI → 无新 AI 条目；量子位/爱范儿头部非 AI/analysis/feature/超窗；TechCrunch（`Anthropic…` 六十三 / `LibreOffice` 六十二 / `Mistral 1T` 同事件 / `Pinterest` 六十 / `Disrupt 议程` promo）、The Verge（`We can't just…recording` column、`Wikipedia rogue bots` 同事件）、Ars（`OpenAI hack Wikipedia` 同事件 / `VMware` 非 AI / `MCP agent-to-agent` 分析）→ 去重/不收；`search_news`(HN) 候选多 discussion/tool、WSJ Mistral〔同事件·在账〕、Liquid D1/GPT-6.1 Sol〔超窗〕→ 拒收/去重，**本轮未超时**；`SEEN.md` +3 行（1 news + 2 防重）。**G2′④**：距 2026-10-06 11:24 真实重跑约 **13.8h <20h** → 不刷连续性（自报仍 **连续 2 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 约 `2026-10-07 ≥07:24`）。**体积**：TASK=**31.6KB** / MEMORY≈**30.6KB**（ARCHIVE≈47KB）均 ≤32KB → 无需额外归档。**判据复核**：✅ 标题+来源+发布日期+链接 · ✅ 本机实测原文可解析并核验 `9:35 AM PDT Oct 6`＝00:35 CST 在窗 · ✅ 公司/事件如实归属（非转述/软文）· ✅ 非 AI/feature/opinion/discussion 从严不收 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。


- **2026-10-07（本唤醒 ~00:36）** —— 🆕 **第六十四轮常态采集：news +1（中文 0 / 英文 1；当日 2 / 累计 161）**：**Google 官方博客《EmbeddingGemma 2: an open, lightweight multimodal embedding model》**（`blog.google` developers-tools feed `date: Tue, 06 Oct 2026 16:00:00` ＝ **2026-10-07 00:00 CST**，本机 `HTTP 200` 实测博文可解析；旁证 HN 同日提交）：Google **发布 EmbeddingGemma 2**——**开放的轻量级多模态嵌入（embedding）模型**，主打**隐私优先 / 端侧（on-device）**；**基于 Gemma 4 构建**并**共享其文本 tokenizer 与音频编码器**，可与 Gemma 4 在**同一端侧 RAG 管线**中共存、降低合计内存占用；官方称其在 **sub-1B 参数**规模下取得新「**每参数质量（quality-per-parameter）**」水准、**MTEB Code 由 68.76 → 78.68**，并称可**优于部分体积两倍以上的专用模型**；权重已在 **Hugging Face / Kaggle** 发布〔`Gemini Enterprise Agent Platform Model Garden` 称即将上线〕，端侧走 **LiteRT / MediaPipe**，演示见 **Google AI Edge Gallery**（Instant Media Search / Video Moments Finder）。归第 1 类〔前沿模型发布 / 基准突破〕。**源盘点**：`cn_news`（限 80，活源 6）均假期末段民生/时政/文旅/财经/体育（澜湄合作洪水预警 · 中国足球队收官战 · IMF 对冲基金风险 · 以色列旅行警告 · WTT · 《只此青绿》千场 · 安徽矾都文旅 · 拉脱维亚组阁 · 商务部涉欧答问 · 攀岩安全提示…），**无 AI 条目** → 不收；**联合国中文源仍 404**；**IT之家** `list` 页与 `rss` **交叉核对**头部仍 `010/124`〔第六十二轮已账〕· `010/123` 游戏非 AI · `010/098` 显卡驱动非 AI → **无晚于 `010/124` 的 AI 条目**；量子位头部 诺奖物理/陶哲轩/OpenAI 28 天/Hinton RSI〔非 AI/analysis/已在账〕；**TechCrunch AI feed** 新头部 `Anthropic…`〔第六十三轮已账〕· `LibreOffice`〔已账〕· `Mistral 1T`〔同事件·在账 `010/108`〕；**The Verge `ai`** 头部 `We can't just change the definition of 'recording'`〔**column/opinion**〕· `Google 撤免费 Gemini`〔**同事件·在账 IT之家 10-03**〕· `Alexa lalala`〔已账〕；**Ars** 头部 `OpenAI agents hack Wikipedia`〔同事件·已账 Wikimedia〕· `VMware 调查`〔非 AI〕· `MCP agent-to-agent`〔分析〕→ 去重/不收；**`search_news`(HN `AI`)** 多 `Show HN`〔tool〕/博客〔analysis〕/video〔opinion〕· `NYT《In race with U.S., China struggles to recruit foreign AI researchers》`〔**feature/付费墙** → 不收〕· `EmbeddingGemma 2`〔**收录**〕→ 拒收/去重，**本轮未超时**。**台账**：`SEEN.md` **+3 行**（1 news + 2 防重）。**G2′④**：距上次真实重跑（2026-10-06 11:24）约 **13.2h < 20h** → **不做真实重跑、不刷连续性**（自报仍 **连续 2 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 约在 **2026-10-07 ≥07:24**）。**体积**：TASK=**31.6KB** / MEMORY≈**30.6KB**（ARCHIVE≈47KB）均 ≤32KB → 无需额外归档。**判据复核**：✅ 标题+来源+发布日期+链接 · ✅ 官方博文发布事件（非转述/非软文） · ✅ 非 AI/feature/opinion/tool/付费墙 从严不收 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。


- **2026-10-07（本唤醒 ~00:02）** —— 🆕 **第六十三轮常态采集：news +1（中文 0 / 英文 1；当日 1 / 累计 160）**：**TechCrunch《Anthropic is giving startups a free year of Claude Team and $1,000 in credits》**（**10-06 16:00 UTC ＝ 2026-10-07 00:00 CST** `techcrunch.com/2026/10/06/anthropic-gives-startups-a-free-year-…`，本机实测原文 `HTTP 200` + `datePublished 2026-10-06T16:00:00+00:00`，在窗）：**Anthropic 于周二（10-06）宣布扩展其「Claude for Startups」计划**，向**符合条件的公司**提供补贴式模型访问及附加权益；新版作为 **Anthropic 的 SF Tech Week 活动**一部分推出 —— **免费赠送一年 Claude Team**（团队付费版，含**最多 5 个 premium 席位**）＋ **1,000 美元 API credits**（用于基于 Claude 开发）；另可获 **Claude Marketplace** 权限（构建插件）与**预约 Anthropic 应用 AI 团队线上 office hours**；报道引其原话「**我们相信 AI 的益处将主要通过『在模型之上做构建的公司』触达大多数人，而非仅通过模型本身**」。归第 5 类〔头部 AI 实验室战略 / 生态与开发者争夺〕。**源盘点**：`cn_news`（限 60，活源 6）均假期返程/民生/时政/文旅/财经（中国足球队收官战、IMF 对冲基金风险、以色列旅行警告、商务部涉欧答问、香港自由度评级、拉脱维亚组阁、法国凡尔赛宫停电、国庆返程提示…），`AI/…` **正则零命中** → 不收；**联合国中文源仍 404**；IT之家 feed 头部 `010/124` 已在账〔第六十二轮〕· `010/123` 明日方舟·RTX Spark〔游戏非 AI〕· `010/098` 显卡驱动〔非 AI〕· `010/114` AMD〔第六十一轮已账〕· `010/108` Mistral Large 4〔第六十轮已账〕→ **无晚于 `010/124` 的新 AI 条目**；量子位（诺奖物理/陶哲轩/OpenAI 28 天/Hinton RSI/GPT-6 3D/DeepSeek 扩招）非 AI/analysis/已在账；爱范儿（Mate 90 硬哲学 feature / OpenAI 元老离职信 opinion / AI 视频榜 feature）非新闻/超窗 → 不收；**TechCrunch AI feed** 新头部即 `Anthropic…`（收录）、余 `LibreOffice`〔第六十二轮已账〕/`Mistral 1T`〔同事件·在账 `010/108`〕；**The Verge `ai`** 头部 `Google 撤免费 Gemini Flash/Pro`〔**同事件·在账 IT之家 10-03**〕· `Alexa lalala`〔非清单〕、余已账/feature/podcast；**Ars `technology-lab`** 头部 `OpenAI agents hack Wikipedia`〔**同事件·已账 Wikimedia 官方**〕· `VMware 调查`〔非 AI〕· `MCP agent-to-agent`〔分析〕→ 去重；**`search_news`(HN `AI`)** 多 `Show HN`〔tool〕· 博客〔analysis〕/WSJ opinion〔非新闻〕/`Ghost/Core`〔**已在账**〕→ 拒收/去重，**本轮未超时**。**台账**：`SEEN.md` **+1 行**。**G2′④**：距上次真实重跑（2026-10-06 11:24）约 **12.6h < 20h** → **不做真实重跑、不刷连续性**（自报仍 **连续 2 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 约在 **2026-10-07 ≥07:24**）。**体积**：TASK=**31.6KB** / MEMORY≈**30KB**（本轮自滚归档第六十一 / 五十九轮流水；ARCHIVE≈47KB）均 ≤32KB → 无需额外归档。**判据复核**：✅ 标题+来源+发布日期+链接 · ✅ 本机实测 `HTTP 200` 核验 `datePublished` 在窗 · ✅ 补贴/免费额度如实归属为「宣布/提供」 · ✅ 非 AI（游戏/显卡驱动/整车/外设）与 feature/podcast/opinion 从严不收 · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。

- 🔀 **第六十二轮**（2026-10-06 ~23:33，news +2：IT之家 德国交通部长盼特斯拉 FSD（监督版）获欧盟批准 · TechCrunch：LibreOffice 把「no AI」当特性）流水原文已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 2026-10-07 00:36 为 MEMORY≤32KB 归档；原文不改）。


- 🔀 **第六十一轮**（2026-10-06 ~22:54，news +1：**IT之家《AMD 股价创历史新高！CEO 苏姿丰称 AI 芯片需求非常旺盛，将持续大幅扩产》**〔10-06 22:30:54 CST `010/114`；归第 5 类〕）流水原文已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第六十一轮 22:54 心跳；原文不改）。

- 🔀 **第六十轮**（2026-10-06 ~22:19，news +4：IT之家 Mistral Large 4 公开预览版〔1 万亿总参 / 490 亿激活 · 月底开放权重〕· 英伟达市值 5.8 万亿美元创历史新高 · TechCrunch Pinterest AI Beauty Guides · TechCrunch Flai AI 经销软件〔2,700 万美元 A 轮〕；`SEEN.md` +6）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- 🔀 **第五十九轮**（2026-10-06 ~21:45，**news +0**：窗口约 0.65h 无新 AI 事件 → 如实留空、不凑数；含同事件/非 AI 防重 2 行）流水原文已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第五十九轮 21:45 心跳；原文不改）。

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