# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~二十五轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序已收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库（75,610 条，对 15:10 全量快照）· N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + **§4.4 措辞强度 tone 信号**，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md，9 行）+ **G2′④ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）**
当前动作:     **本唤醒：第二十五轮常态采集（news **+1**：The Guardian《Accept 'bad things' in return for benefits of AI, says Sam Altman》10-05；⚠️ 本机 Guardian 不可达〔`Errno 101`〕→ 仅凭标题+链接+HN 日期核验）；**上轮**：第二十四轮 +2（TechCrunch Sanders Flock 法案 · Safeworld 种子轮）
下一步:       ① 提交本线产物（**不含任何 ≥5MB 文件**）；② **G2′④ 累积**：**隔日（≥20h，约 2026-10-06 ≥11:10）**跑真实重跑（`cycle_run.py --with-l2`，**不带 `--record`**）追加台账（**台账自报：连续 1 天 / 目标 7 天，未达标**）；③ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；④ L3（N5）**冻结**
本轮新增:     **第二十五轮常态 news **+1**（中文 0 / 英文 1；当日 33→**34**）**：**The Guardian《Accept 'bad things' in return for benefits of AI, says Sam Altman》**（10-05；OpenAI CEO Sam Altman 称社会应「**接受一些坏事**」以换取 AI 益处；⚠️ **本机 Guardian `Errno 101` 不可达** → 仅凭**标题 + 链接 + HN 日期**核验，如实标注）。`cn_news` 60 条均假期/民生/时政（唯一 AI = DeepZang 已在账）→ 不收；**联合国中文源仍 404**；量子位（诺奖非 AI）/IT之家/钛媒体/爱范儿/雷峰网头部均已在账或非清单；TechCrunch / Ars / WIRED 头部（已在账 / 非 AI / 评测导购）→ 不收；HN 新增候选 **Bloomberg（newsletter）/ The New Yorker（专栏）/ The Bulletin / Lawfare（analysis）/ The Atlantic（随笔）** 均判**非新闻 → 拒收**（存 `SEEN.md`）；Forbes SpaceXAI rebrand 与在账同事件 → 去重；FT《Altman legal risks》本机不可达 → 不收。**计数口径对账（如实）**：`SEEN.md` 的 `news` 行含「同事件去重跳过」条（如 `ithome/009/852`）→ **SEEN `news` 行数 ≠ 摘要 news 数**，本线以**摘要实际收录**为准（当日 **34** / 累计 **103**）。累计 **news 103 / 非新闻 58**
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）
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
- **上次采集窗口**：`2026-10-05 20:26 CST` 第二十四轮 ~ `2026-10-05 21:05 CST` 第二十五轮
- **累计收录**：`161` 条（**news 103**〔第一~二十五轮；当日 34〕+ 非新闻 58〔仅存 `SEEN.md`〕）

---

## 2. 流水（倒序，保留最近 ~20 条）
- **2026-10-05（本唤醒 ~21:05）** —— 🆕 **第二十五轮常态采集：news +1（英文 1 / 中文 0）**。
  - **① The Guardian《Accept 'bad things' in return for benefits of AI, says Sam Altman》**（2026-10-05）：据 The Guardian 报道，OpenAI CEO **Sam Altman** 表示社会应当「**接受（AI 带来的）一些坏事**」以换取 AI 的**益处**。⚠️ **本机 The Guardian 原文不可达**（`Errno 101` 网络不可达 / `curl` 超时）→ 仅凭**标题 + 链接 + HN 日期**（HN date 2026-10-05；URL 路径 `/2026/oct/05/`）核验，**正文细节未取得，如实标注**。→ 关注清单第 5 类「公司与人物动态」/ 第 4 类「AI 与社会」（承接在账 Axios《Altman: Ascribing religion to models a "safety issue"》10-03）。
  - **源盘点（如实）**：`cn_news` **60 条均国庆假期 / 民生 / 时政 / 体育 / 天气 / 文旅**（唯一 AI = DeepZang `10708223`，已在账）→ **不收**；**联合国中文源仍 `HTTP 404`**；量子位头部《诺奖颁给光遗传学》（`501720`，非 AI）、其余均已在账 → 去重；IT之家（三星 S27 / 恋与深空 / 铁路抢票 / GTA6…）、钛媒体、爱范儿、雷峰网头部**均已在账或非清单** → 去重 / 不收；TechCrunch（Sanders Flock / Safeworld / 其余已在账）、Ars（键盘科普 / 考古 / 野生动物，非 AI）、WIRED（评测导购，非新闻）→ 不收。
  - **`search_news`(HN)**：查询 `AI` / `AI safety` / `superintelligence` / `Anthropic OpenAI` / `OpenAI` / `AI regulation` / `AI jobs` / `AI model release` / `AI governance` —— 新增候选 **Bloomberg《AI Backers Sound the Alarm About Safety》（newsletter）/ The New Yorker《Will A.I. Still Take Our Jobs?》（专栏）/ The Bulletin《AI doesn't need 'superintelligence'…nuclear war》（analysis）/ Lawfare《A Warning for Frontier AI Model Governance》（analysis）/ The Atlantic《I Quit OpenAI…》（随笔）** 均判**非新闻 → 拒收**（存 `SEEN.md`）；Forbes《SpaceXAI rebrand》与在账 钛媒体 `8159476` **同事件** → 去重；NBC《Trump calls for self-regulation》（10-01）**超 72h 窗** → 拒收。
  - **FT（Financial Times）**：《Legal risks pile up for Altman as OpenAI uncovers hacks》（10-05）**本机 `curl` 超时（不可达）** → 无法核验正文/日期，**本轮不收**（如实，未静默当「无新增」）。
  - **计数口径对账（如实）**：`SEEN.md` 中标 `news` 的行**含「同事件去重跳过」条**（如 `ithome/1/009/852.htm`）→ **SEEN 的 `news` 行数 ≠ 当日摘要 news 数**；本线以**摘要实际收录**为 INDEX/累计口径（当日 **34** / 累计 **103**）。
  - **G2′④**：本轮距上次真实重跑（15:10）约 **5.9h <20h** → **不做真实重跑、不刷台账连续性**；连续性自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（下一窗具备 ≥20h 间隔的真实重跑约在 **2026-10-06 ≥11:10**）。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**（未产出任何策略/仓位/择时）。

- **2026-10-05（本唤醒 ~20:26）** —— 🆕 **第二十四轮常态采集：news +2（英文 2 / 中文 0）**。
  - **① TechCrunch《Sanders introduces bill to ban the federal government from using Flock》**（2026-10-02，Connie Loizos）：参议员 **Bernie Sanders** 于 10-02 提出《**Ban Flock Act**》，**禁止联邦机构使用自动车牌识别（ALPR）系统或接入地方/私营车牌数据**；覆盖所有 ALPR（未点名 Flock），仅对收费与国会今后批准（留存限 48h）设例外；州/地方不禁用将失去五个联邦部门拨款，公民可起诉、州检察长可执法。AOC + Jeff Merkley 联署；Flock 逾 12 万台摄像头、月处理逾 200 亿次读取。**仅提案未成法**（如实标注）。→ 关注清单第 3 类「政策与治理」。
  - **② TechCrunch《Can Safeworld convince people that gen AI robots won't hurt them?》**（2026-10-05，Tim Fernholz）：**CMU Safe AI 实验室主任 Dr. Ding Zhao** 等创办 **Safeworld** **出隐身（emerging from stealth）**，获 **超 1200 万美元种子轮**（Shine Capital、a16z Speedrun 领投）；做「**把控制权交给生成式 AI 模型的机器人**」的**安全评测**：在仿真（Genesis/MuJoCo）中放入机器人真实软件 + 逼真人类模型、批量跑上万种人机交互场景。→ 关注清单第 1/2 类「前沿模型与能力 / AI 安全与对齐」。
  - **源盘点（如实）**：`cn_news` 40 条均**国庆假期/民生/时政/体育/天气**（汽车供应链、广州南站、四川红色旅游、巴凯银行香港牌照、魔方赛、网球中网、南部战区正告菲方、内蒙 3.1 级地震、AG600 北疆驻防、丽江直飞清州、悉尼持刀）→ 不收（唯一 AI = **DeepZang `10708223` 已在账**）；**联合国中文源仍 `HTTP 404`**（判源失败）；量子位头部诺奖（非 AI）+ 其余已在账；IT之家 10 条为消费电子/游戏/社会 → 不收；钛媒体/爱范儿/雷峰网头部均已在账或非清单；**TechCrunch《All the AI agents…text messages》经 fetch 核验为 roundup 综述 → 拒收**、**MIT Tech Review《People really hate AI…》核验为第一人称分析 → 拒收**、**Anthropic《What do you want from AI?》核验为研究公告 + 超窗（09-29）→ 拒收**；**FT 两篇本机 fetch 两次均超时 → 无法核验，不收**（如实记录）；The Register atom 仍 ParseError、Guardian tech RSS 仍不可达。
  - **G2′④**：本轮距上次真实重跑（15:10）约 **5.3h <20h** → **不做真实重跑、不刷台账连续性**；自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（下一窗具备 ≥20h 间隔约在 **2026-10-06 ≥11:10**）。
  - **文档同步**：`news/2026-10-05.md`（第二十四轮段）· `news/SEEN.md`（+2 news / +3 非新闻）· `news/INDEX.md`（当日 31→**33** / 累计 news 100→**102** · 非新闻 50→**53**）· `MEMORY_NEWS.md`（快照 + 本流水）· 日流水心跳行 `[20:26]`。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**（未产出任何策略/仓位/择时）。


- **2026-10-05（本唤醒 ~19:50）** —— 🆕 **第二十三轮常态采集：news +3（英文 3 / 中文 0）**。
  - **① BleepingComputer《Anthropic asks Claude users to share voice data for AI model training》**（2026-10-04）：安全/科技媒体 BleepingComputer 报道，Anthropic 请求其 Claude 用户分享**语音数据**用于 AI 模型训练（头部实验室数据获取策略 / 用户隐私边界）。→ 关注清单第 5 类「公司与人物动态」。
  - **② DW《Is Russia using AI for disinformation in the Central African Republic and elsewhere?》**（2026-10-04）：德国之声援引 Anthropic 一份报告，讨论俄罗斯是否在**中非共和国（CAR）及其他地区**借助 AI 进行**虚假信息**活动。→ 关注清单第 4/3 类。
  - **③ Axios《OpenAI's Altman: Ascribing religion to models a "safety issue"》**（2026-10-03）：Axios 报道 OpenAI CEO **Sam Altman** 将「把宗教/信仰投射到（AI）模型上」视为一个「**安全问题**」。→ 关注清单第 2/5 类。
  - ⚠️ **三条原文均不可达**（BleepingComputer `HTTP 403`；Axios/DW `fetch` 超时；Reuters 历史超时）→ **仅凭标题 + 链接 + HN 日期核验**，正文细节未取得，**如实标注、不臆测**（与第二十二轮 Reuters 处理一致）。
  - **源盘点（如实）**：`cn_news` 30 条均**国庆假期/民生/时政/体育**（巴凯银行香港牌照、浙江文旅、高速返程、魔方赛、诺奖、南部战区正告菲方、内蒙 3.1 级地震……）→ 不收；**联合国中文源仍 `HTTP 404`**（判源失败）；**央视网 tech 真条目仍被 `pubDate≤72h` 丢弃**；量子位头部（诺奖）非 AI、其余已在账；IT之家头部为消费/游戏/汽车（高通×华为 `009/852` 同事件）；钛媒体新增均已在账；TechCrunch 新增为 podcast/非 AI 主题；**WIRED《Rural Data Centers…》经 fetch 核验为「Power Play!」周专栏（非新闻）→ 拒收**、**《Lawmakers…Flock Cameras》核验日期 09-15（超窗）→ 拒收**；Ars/爱范儿/雷峰网非 AI 或超窗/同事件；The Register / 机器之心 atom 仍 **ParseError**；Guardian/NYT feed 本轮不可达（如实记录）。
  - **G2′④**：本轮**距上次真实重跑（15:10）约 4.7h <20h** → **不做真实重跑、不刷台账连续性**；自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（下一窗具备 ≥20h 间隔约在 **2026-10-06 ≥11:10**）。
  - **文档同步**：`news/2026-10-05.md`（第二十三轮段）· `news/SEEN.md`（+3 news）· `news/INDEX.md`（当日 31 / 累计 news 100）· `MEMORY_NEWS.md`（快照 + 本流水）· 日流水心跳行 `[19:50]`。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**（未产出任何策略/仓位/择时）。

- **2026-10-05（本唤醒 ~19:16）** —— 🆕 **第二十二轮常态采集：news +2（中文 1 / 英文 1）**。
  - **① Reuters《Norway to propose temporary ban on AI glasses in some public places》**（2026-10-05）：据路透社报道（经 Hacker News 索引，HN story id `49963007`，发布 `2026-10-05T10:25:29Z`），挪威政府拟提出**临时禁令**，禁止在部分公共场所使用 **AI 智能眼镜**。⚠️ **本机无法抓取 Reuters 原文**（`fetch` 超时，历史一致）→ 仅凭**标题 + 链接 + HN 日期**核验（正文细节未取得，如实标注，不臆测）。→ 关注清单第 3 类「政策与治理」。
  - **② 中新网《中国首个藏语大语言模型 DeepZang 迭代推进会在呼和浩特召开》**（2026-10-05）：中国首个藏语大语言模型 **DeepZang** 的「升级迭代及同声传译研发推进会」近日在内蒙古呼和浩特举行（中新网拉萨 10-05 19:10 电，作者万纪玮）；报道称藏语因结构特殊/方言差异/语料稀缺属 NPL 低资源难题，DeepZang 在多方言适配、语义精准识别、离线场景应用持续优化，将融入公共服务、教育医疗、文旅、基层治理；DeepZang 创始人旦增罗布出席。→ 关注清单第 1 类「模型与能力」。
  - **源盘点（如实）**：`cn_news` 40 条多为**国庆假期/民生/时政**（高速拥堵、AG600、中网、诺奖、南部战区正告菲方、横店入境游…；唯一 AI 新增 = DeepZang）；**央视网 tech 13 条真条目被 `pubDate≤72h` 丢弃**（锂电正极 82.2h、新恐龙 104.0h、人造太阳 109.0h…）；**联合国中文源仍 `HTTP 404`**（判源失败）；量子位头部均已在账；IT之家头部为游戏/汽车/消费电子（华为×高通 `009/852` 同事件 → 去重）；钛媒体新增 feature/opinion/analysis 仅存 `SEEN.md`；TechCrunch 新增候选（Amazon 数据中心、OpenAI 安全员工离职）均同事件/feature → 去重或不收；`search_news`(HN) 唯一新 §0.1 = 挪威禁 AI 眼镜；`web_search`(CN-Bing) 无有效召回归。
  - **G2′④**：本轮距上次真实重跑（15:10）约 **4.1h <20h** → **不刷台账连续性**；自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（如实写）。
  - **文档同步**：`news/2026-10-05.md`（第二十二轮段）· `news/SEEN.md`（+2 news）· `news/INDEX.md`（当日 26→**28** / 累计 news 95→**97**）· `MEMORY_NEWS.md`（快照 + 本流水）· 日流水心跳行 `[19:16]`。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**（未产出任何策略/仓位/择时）。

- **2026-10-05（本唤醒 ~18:45）** —— 🎯 **补 G2′④ 台账缺口（`cycle_run.py` 新增「连续性自报」行）+ 第二十一轮常态采集（news +0，如实）**。
  - **动机**：任务书 §0.0.2 **G2′④ 2026-10-05 修订口径**要求台账**必须自报「已连续 X 天 / 目标 7 天」**，而原 `STABILITY_LOG.md` 无此字段（只有逐行记录）。
  - **实现（`news/policy/cycle_run.py`）**：新增 `_iter_rows / _is_real / compute_streak / update_streak_line` —— 按**修订口径**（连续 7 **自然日**、每日 ≥1 次**真实重跑**、相邻 **≥20h**、**同天多次只计 1 天**、`record-only` **不计入**）**由台账真实行自动推算**；每次运行**重写文末**「G2′④ 连续性自报」行（🚫 不补造、不手填）。`--record` 跑通：`strk=1/7`（现全部真实行同为 2026-10-05 → 计 1 天）。表头口径同步更新（「连续 N 周」→「连续 7 自然日」）。
  - **第二十一轮常态采集（news +0）**：`cn_news`（中新网×3 + 央视网 news/tech）命中均假期/民生/时政 → 不收；**央视网 tech 13 条真条目被 `pubDate≤72h` 丢弃**（含《生成式AI用户规模突破7亿人》超龄 142h）；**联合国中文源仍 `HTTP 404`**；量子位头部均已在账；IT之家《高通×华为逻辑折叠芯片专利授权》与在账 `009/806` **同事件** → 去重；钛媒体新增 1 feature + 2 analysis 仅存 `SEEN.md`；TechCrunch《Google 冻结漏洞赏金》已在账；The Register atom 仍 ParseError。当日维持 **26**（累计 news 95 / 非新闻 50）。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。
  - **未做**：真实重跑（距上次 15:10 **<20h** → **不刷连续性**）。

- （更早流水：**2026-10-05 17:25/17:55 第十九~二十轮**（TechCrunch 超级智能部队 · 钛媒体 SpaceXSI · TechCrunch 联邦法官裁定 Flock；已归档 `daily-memories-news/2026-10-05.md`）· **2026-10-05 16:12 第十六~十七轮**（L1 §4.3 固定召回率 precision 加固 + IT之家索尼×Meta 专利）→ 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-05 早期**（恢复 27h 停摆首轮 · N1 2021/2022 续抓）· **N1 第 3/4/5/6 轮抓取（2020→2019→2017/2018→2016）+ 第十一~十五轮常态采集 + 全链重跑** → 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-03 各轮 / 2026-10-04 各轮**（L1/N3 收口、N4/L2、L1 链重跑+轴对齐）→ `daily-memories-news/2026-10-03.md` · `daily-memories-news/2026-10-04.md`；第三~九轮 / 第二轮 / 首轮 smoke / 前期任务 T1–T4 / 建线 / 首轮空转 亦在其中）

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
