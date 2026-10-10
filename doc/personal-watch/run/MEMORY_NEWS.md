# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）** + **任务书自滚归档（已把第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`；每次唤醒按 ≤32KB 自检）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~六十轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库 75,610 条 · N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + §4.4 措辞强度 tone 信号，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md）+ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）· **任务书自滚归档（第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`）** · **第六十~七十八轮常态采集 ✓（news +27：Mistral Large 4 / 英伟达市值 5.8 万亿新高 / Pinterest / Flai · AMD 苏姿丰 / FSD 欧盟 / LibreOffice / Anthropic Claude Team / EmbeddingGemma 2 / Mirror Particle / Hark / Wajo / Lambda $4B / Musubi PolicyLM-1.7B / Underdog / Melius / Anthropic CVP 129k 漏洞 / OpenAI 数学 722 手稿 / 美司法部「超级智能」/ SpaceX $40B / 软件股阶段新高；**明细见 §2 流水**）**· **第七十九~八十一轮常态采集（news +13：MAI Code 1.1 Flash · 英伟达 DGX Station for Windows · 传三星 12Hi HBM4E · CoreWeave 印度 240MW · Google SynthID · Nous Research $90M · 小马智行×Uber 伦敦 · 据报三星越南 2 厂 · 谷歌云 Gemini Agent · Waymo $5B · 格芯×台积电 $2B · Arena $200M · 被解雇 OpenAI 安全研究员公开信；**明细见 §2 流水**）** · **第 11 批 P0 · R3/R4/R5/R6（38 标的十年价格每次全量刷新 · `lag_corr.csv` **R1–R6 六次运行逐字节一致**〔`83d3bf34…`·**第 6 次可复现**〕· `AM_PM_CHECK.md` R5 复跑**未产生新表**〔🛡 0 格护栏生效〕· `INDEX_FILES.md` R5 重登记 + R3 勘误 · 日报 `2026-10-08` AM+PM / `2026-10-09` **AM+PM** / `2026-10-10` **PM**）** · **第八十二轮常态采集（news +8：TRAE 合并 Code/Work · 联想 TianxiCode 登顶 SWE-bench-Live · 字节 Seed「相位敏感性」· 星动纪元 VPP2 登顶 RoboDojo · openJiuwen 开源企业级 AgentOS · 豆包工作画布 · Claude Dashboards/Motion · 《柳叶刀》AMIE 真实急诊；**明细见 §2 流水**）**
当前动作:     **本唤醒（2026-10-10 18:00 · R6 晚报轮）：全链跑完 · 0 新结论（负面结果照写）**。**① 第 11 批 P0 · R6** —— `fetch_prices.py --refetch` **38 标的十年价格再全量刷新**（`ok=38 / fail=0`）⇒ **R6 相对 R5 唯一新数据 = 10 条汇率末日 2026-10-08 → 2026-10-09**（源侧补齐 ⇒ **只等源、不补造**）⇒ **末日一致性 38/38 = 2026-10-09**；`lag_corr.py` **R6 复核重跑**（23940 格）⇒ `lag_corr.csv` **与 R1–R5 逐字节一致**（sha256 `83d3bf349be52251…` / 4,018,511 B / 23,941 行；`q<0.10`=**0** / `stable`=**0** / 未校正 `p<0.05`=1217≈5.08%）——**原因可证**：分析窗口 = 价格 ∩ 语料，窗口＝价格∩语料，止于 2026-09-30 ⇒ 2026-10-01 起的价格行整体落在窗外 ⇒ **价格刷新无法改变任何统计量**（**第 6 次可复现性通过**）；配套：`LAG_CORR.md`（R6 头）· `FINDINGS.md`（`VERIFY_DATE`→2026-10-10 + §3 追加 R6 条）· `SOURCE_TEST.md`（18:06:11 重生成）· **`INDEX_FILES.md` R6 重登记**（§A 19 行当轮实测〔新增 `daily/2026-10-10.md`〕+ §B 38 个价格文件；指纹 `50d5ab4c3a40114c` / 合计 2,562,208 B）· **日报 `daily/2026-10-10.md` 新建（PM 单写版 · 150 行 / 19,388 B）**。**② 第 12 批 P0 复核 = 0 新增**（`REPORT.html` 234 行/30,150 B/`29a03cd0…`·`grep -c http`=0·与 HEAD 逐字节一致 ⇒ 已交付、不重跑）。**③ `cycle_run.py` 真实重跑**（`rc=0` · `days=3914 / recs=2492429 / events=75610`）⇒ `STABILITY_LOG.md` 追加 **2026-10-10 18:08** 行 ⇒ **G2′④ 连续 6 天 / 目标 7 天 —— ⚠️ 未达标（如实自报）**。**④ 第八十三轮常态采集（news +10 · 中 10 / 英 0）** ⇒ `news/2026-10-10.md`（87 行 / 13,424 B）＋ `INDEX.md` / `SEEN.md`（窗口 2026-10-09 18:20 → 10-10 17:55 CST ≈ 23.7h；因 **06:00 轮 cline 于 `exit 0` 中途结束 turn**，本窗由 18:00 轮**一次性覆盖** ⇒ **如实记为「一轮覆盖」**）。**本日无新增「早报→当日」机械复核对**（as-of 仍 2026-09-30 ⇒ `k=1` 目标日仍 2026-10-08，R3 已实核 63 格；且周六无交易时段）⇒ **如实写「无」**。🚫 非因果 · 非投资建议 · 无点位/仓位/择时（L3 冻结）。
第11批(R6):    ✅ **P0 交付（R1–R6 全部到位）**：`news/signal/` = prices/〔**38 标的·6 类·2016–2026·2,562,208 B·ok=38/fail=0·全量刷新至 2026-10-09〔**38/38 末日整齐**（R6 起 10 条汇率补齐到 10-09）〕**〕· SOURCE_TEST.md · **INDEX_FILES.md（R6 重登记：§A + §B 38 个价格文件逐文件；指纹 `50d5ab4c3a40114c`）** · `lag_corr.py` → lag_corr.csv + LAG_CORR.md（**23,940 格 · FDR `q<0.10`=0 / `stable`=0 · 如实负面**；**R1–R6 六次运行字节一致 sha256 `83d3bf349be52251…`**）· `BOOTSTRAP.md`（块自助 CI）· `FINDINGS.md`（台账 · 最后核验日 **2026-10-10**）· `LATEST_SIGNALS.md`（as-of **2026-09-30**·语料冻结）· `AM_PM_CHECK.md`（R3 实核 63 格 + R5 护栏说明）· `make_report_html.py` + **`REPORT.html`（第 12 批 P0 · 自包含 · 234 行 / 30,150 B · `29a03cd0cd41e7ec`）** · 日报 `daily/2026-10-08.md` / `2026-10-09.md` / **`2026-10-10.md`（R6 · PM 单写版）**。⚠️ **非因果 · 非投资建议**；🚫 无点位/仓位/择时。
下一步:       ① **G2′④ 累积**：维持「每日 ≥1 次真实重跑、相邻 ≥20h」节奏（**本日第 2 次真实重跑已入台账，同天只计 1 天**）→ **如实自报连续天数/未达标**（`news/policy/STABILITY_LOG.md`）；② **下一轮（2026-10-09 18:00 晚报轮）**：须**在本轮新建的 `daily/2026-10-09.md` 上补 PM 版**（AM 版已交付）；**⚠️ 本早报轮未做 `cycle_run.py` 真实重跑**（距 2026-10-08 18:24 仅 ~11.6h < 20h）⇒ **18:00 必须真跑**（届时 ~23.6h）；⚠️ **语料仍冻结（2026-09-30）** ⇒ 信号面 as-of 不变 ⇒ **如实写「近 24h 无新信号」**；**「早报→当日」机械复核对本日无新增**〔as-of 仍 2026-09-30 ⇒ `k=1` 目标日仍 2026-10-08，**R3 已核**〕⇒ 若当日早报含方向性表述届时才须复核；③ **常态采集续跑**（**每天 2 次 06:00/18:00**；窗口内新 AI 事件照收、无则如实留空；**深扫 feed 头部以下若干位，防再漏收**）；④ **价格增量**：每轮 `fetch_prices.py` 增量刷新 + **重跑 `lag_corr.py`**（**必须复报 sha**，若变化则查因）· ⚠️ **`USDCNY` 源仍停在 2026-09-30** ⇒ 若恢复更新则补跑重登记；⑤ **第 10 批 B 线**：**仍待用户拍板 P1–P6/P7**（`news/dongfang/report.html` §8）→ **拍板前不实施日更**；⑥ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；⑦ L3（N5）**冻结**；⑧ **任务书/MEMORY 自滚归档**（>32KB 目标 / >40KB 红线前先搬 `WATCH_NEWS_TASK_ARCHIVE.md` / `daily-memories-news/`）
本轮新增:     **第八十一轮常态 news +5（中文 3 / 英文 2；当日 5 / 累计 186）**——IT之家 **谷歌云发布 Gemini Agent，定位「通用工作智能体」**〔`010/706`·**页面标注 `2026/10/8 21:21` CST**·`HTTP 200`·「Gemini at Work 2026」·支持 Gemini Enterprise / Workspace / 第三方·**支持 Gemini 与 Claude 模型**·**私人预览阶段** ⇒「预计很快开放」按**厂商口径**保留；第 1 类〕· **Waymo 获 50 亿美元贷款**〔`010/734`·`23:01` CST·**黑石 / PIMCO / Sixth Street**·**首次债务融资**·用于 Robotaxi 扩张、**入欧日＝意向**；第 5 类〕· **格芯与台积电签署 20 亿美元协议**〔`010/716`·`22:15` CST·**美国首个硅中介层基地**·纽约州马耳他厂·服务 **AI/HPC 先进封装 CoWoS®**；第 5 类〕｜TechCrunch **Arena 估值 31 亿美元**〔`Posted 11:19 AM PDT 10-08` ＝ **10-09 02:19 CST**·$200M 由 Lightspeed / Khosla 领投·6 月已达 $100M run-rate·**公司自述**；第 5 类〕· **被解雇 OpenAI 安全研究员公开信**〔`Posted 1:04 PM PDT 10-08` ＝ **10-09 04:04 CST**·致 Safety and Security Committee / Safety Advisory Group / Mission Advisory Council·警告「**寒蝉效应**」·**单方陈述**；第 6 类〕。英源《Google brings agentic AI to Gemini》= 与 `010/706` **同事件 ⇒ 交叉印证·不另计**。`SEEN.md` **+13 行**（5 news + 1 同事件防重 + 2 feature 防重 + **6 留档**）。┃ **P0（第 11 批 · R4）**：38 标的价格**再全量刷新**（ok=38/fail=0·**末日 38/38 = 2026-10-08**）· `lag_corr.csv` **与 R1/R2/R3 逐字节一致**（**第 4 次**）· `INDEX_FILES.md` **R4 重登记 + R3 勘误** · `FINDINGS.md` §3 **R4 条目** · `daily/2026-10-09.md` **AM 版**。┃ 上一唤醒：第八十轮（news +2）见 §2 流水
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）｜🆕 **第 10 批**：⚠️ **`mcp<2` 已成运行机全局 pin**（2.3.0 → **1.30.0**，否则 `mcp_ddgs`/离线自检不可用）→ 与需 **mcp 2.x** 的其它线**可能冲突**，**待 supervisor 确认**；⚠️ **ddgs 8/8 引擎被墙**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但结果端点被拦）→ 免费通用 web 搜索**本机不可用**，日常仍以 `cn_news` + 官方 RSS 为准；⚠️ **CN-Bing 抓取相关性降级**（查「人工智能 最新 政策」返回「人工」词条 → 200 ≠ 有料） ｜📦 **体积（实测字节）**：**TASK=38565B(37.6KB) / MEMORY=31090B(30.4KB)**（含 ARCHIVE≈48.3KB）；soft 32KB / 红线 40KB（本轮已把 §2 的 **R3 / R2 两条 P0 长条目**压缩为 🔀 指针〔原文已在 `daily-memories-news/2026-10-08.md`〕，并把 §「已完成」的**第六十~七十八轮明细**收敛为一行〔明细见 §2 流水〕）
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
- **第 11 批产物（P0 · 新闻信号 → 资产价格）**：`news/signal/`（`PREREG.md` / `SOURCE_TEST.md` / `prices/`〔**38 标的 十年 2016–2026**〕/ `lag_corr.py` → `lag_corr.csv` + `LAG_CORR.md` / `BOOTSTRAP.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / **`AM_PM_CHECK.md`** / `daily/<date>.md` / **`INDEX_FILES.md`** / **`make_report_html.py` + `REPORT.html`**）；⚠️ ≥5MB 不入 git，`lag_corr.csv` ≈ **4.0MB < 5MB ⇒ 入 git**
- **上次采集窗口**：`2026-10-09 18:20 CST` ~ `2026-10-10 17:55 CST` ＝ **第八十三轮**（18:00 晚报轮；窗口 ≈ **23.7h**，因 06:00 轮 cline `exit 0` 中途结束 ⇒ **由 18:00 轮一次性覆盖**）
- **累计收录**：`news` **204** 条（第一~八十三轮；当日 **10**）+ 非新闻（口径=逐行统计 `SEEN.md` 类型列）〔**仅存 `SEEN.md`**〕

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-10（第 11 批 · R6 · P0 · 18:00 晚报轮）** —— ✅ **① P0 R6**：38 标的价格再全量刷新（ok=38/fail=0）⇒ **10 条汇率末日 10-08 → 10-09**（源侧补齐）⇒ **末日一致性 38/38 = 2026-10-09**；`lag_corr.py` R6 复核 ⇒ `lag_corr.csv` **与 R1–R5 逐字节一致〔第 6 次〕**（`83d3bf349be52251…` / 4,018,511 B / 23,941 行）；`INDEX_FILES.md` R6 重登记（`50d5ab4c3a40114c`）· `LAG_CORR.md` R6 头 · `FINDINGS.md` R6 条 · **日报 `daily/2026-10-10.md`（PM 单写版 · 150 行 / 19,388 B）**。**② `cycle_run.py` 真实重跑**（rc=0）⇒ `STABILITY_LOG.md` **2026-10-10 18:08** 行 ⇒ **连续 6/7 天 · ⚠️ 未达标（如实）**。**③ 第 12 批 P0 复核 = 0 新增**（`REPORT.html` 与 HEAD 逐字节一致 · 无外链）。**④ 第八十三轮常态采集（news +10 · 中 10 / 英 0）** ⇒ `news/2026-10-10.md` + `INDEX.md` + `SEEN.md`（窗口 ≈ 23.7h；06:00 轮 `exit 0` 中途结束 ⇒ 本窗由本轮一次性覆盖，**如实记**）。⚠️ **本日无新增复核对**（as-of 未推进 + 周六无交易时段）⇒ **如实写「无」**。

- **2026-10-09（18:30 · 重试唤醒 · 0 新增）** —— ⚠️ **本唤醒 = loop 对 18:00 时窗的【重试】**（18:00 轮 cline 于 **18:25:07 `exit 1`** ⇒ `/tmp/watch_news_loop.log` **18:25:07**「检测到 cline 失败/报错」/「重试 1/1（sleep 300s）」两行可核验 → **18:30 重试 ＝ 本唤醒**）。**18:00 轮实质产物已于 18:17–18:23 全部落盘**（`daily/2026-10-09.md` PM 版 · `INDEX_FILES.md`/`FINDINGS.md`/`LAG_CORR.md` R5 条 · 38 标的价格刷新 · `STABILITY_LOG.md` **2026-10-09 18:15** 行 · `news/2026-10-09.md` 第八十二轮），并由 **loop 兜底 auto-commit `b60b308c`（18:25:13）** 提交推送。**独立复核（本轮实测）**：`sha256(lag_corr.csv)`=`83d3bf34…`（**=R1–R5 五次一致**）· 23,941 行 · 末日分布 **{2026-10-09: 28, 2026-10-08: 10}**（A股21+大宗7=28→10-09；10 汇率→10-08，源侧未发布·**未补造**）· `HEAD`=`origin/main`·工作区干净 ⇒ **不重复跑任何 P0 动作 ⇒ 0 新增**（§4-3 / §4-9 / §4-10）。**下一正式轮 = 2026-10-10 06:00 早报轮**。

- **2026-10-09（第 11 批 · R5 · P0 · 18:00 晚报轮）** —— ✅ **18:00 晚报轮交付**（`fetch_prices.py --refetch` ok=38/fail=0；`lag_corr.py` R5 复核 ⇒ `lag_corr.csv` 与 R1–R4 逐字节一致〔**第 5 次**〕；🛡 `am_pm_check.py` 新增拒写护栏；`daily/2026-10-09.md` PM 版；`cycle_run.py` 真实重跑 ⇒ `STABILITY_LOG.md` **18:15** 行 ⇒ **连续 5/7 天·⚠️ 未达标**）。流水**摘要已上移**至本表首条 + `daily-memories-news/2026-10-09.md` `[18:00]` 心跳（**原文不改 · 结论不变**）。

- **2026-10-09（06:20 · 重试唤醒 · 0 新增）** —— ⚠️ **本唤醒 = loop 对 06:00 时窗的【重试】**（首次 cline 唤醒 **`exit 143` = SIGTERM** ⇒ loop 按 `rc≠0` 规则判失败 → `sleep 300s` → 重试 1/1；`/tmp/watch_news_loop.log` **06:15:37**「检测到 cline 失败/报错」/ **06:20:44**「wake up」两行可核验）。**06:00 轮全部工作已于 06:15 完成并推送**（`e0f89c79` R4 早报轮 + `32c5d251` 体积校正；**`HEAD` = `origin/main` = `32c5d251`**、news 线工作区干净；`sha256(lag_corr.csv)`=`83d3bf34…` 复核一致）⇒ **本轮不重复跑任何 P0 动作**（不重抓价格 / 不重跑 `lag_corr.py` / 不加 `cycle_run.py` 行）**⇒ 0 新增**（§4-3 防重复 / §4-10 如实）。已记心跳；**下一正式轮 = 18:00 晚报轮**。

- **2026-10-09（第 11 批 · R4 · P0 · 06:00 早报轮）** —— ✅ **① P0 R4 交付（早报版）**：`fetch_prices.py` **38 标的再全量刷新**（`ok=38 / fail=0`；**末日 38/38 全部 = 2026-10-08**）；相对 R3 **唯一实质变化 = 10 条汇率末日 2026-10-07 → 2026-10-08**（**`USDCNY` 2026-09-30 → 2026-10-08**，**源侧补齐·未补造**），**其余 28 个价格文件行数据逐字节相同**（文件字节差异**仅**来自 `fetched_at` 时间戳 ⇒ **已定因，非数据漂移**）。`lag_corr.py` **R4 复核重跑 → `lag_corr.csv` 与 R1/R2/R3 逐字节一致**（sha256 `83d3bf349be52251…` / 4,018,511 B / 23,941 行；全网格 23,940 格 · `q<0.10`=**0** · `stable`=**0**）——**原因可证：分析窗口 = 价格 ∩ 语料，窗口＝价格∩语料，止于 2026-09-30 ⇒ 新增 2026-10-08 行整体落在窗外** ⇒ **价格刷新不能改变任何统计量**（**第 4 次连续字节一致**）。三处生成器重跑：`LAG_CORR.md` 头 **R3 → R4 复核（2026-10-09 早）** · `signal_snapshot.py` → **`LATEST_SIGNALS.md` sha256 未变**（`99f284f701f23b94…`）· `make_findings.py`（`VERIFY_DATE` 2026-10-08 → 2026-10-09）+ `FINDINGS.md` §3 **追加 R4 条目**。**`INDEX_FILES.md` R4 重登记**（脚本生成：§A 代码/文档/生成物 **16 行**；§B **38 个价格文件逐文件** 名/类/行数/字节/sha16/存放/区间；**目录级指纹 `8699b2b2b16407cf`**；合计 **2,561,195 B**；最大 `prices/JPYCNY.json` **104,647 B** ⇒ **全部 < 5 MB ⇒ 入 git**；**末日一致性 38/38 ✅**）。**🔧 R4 登记勘误**：R3 §A 曾记 `daily/2026-10-08.md` = **130 行 / 11,565 B**（**登记时点早于 PM 定稿**），**实际定稿 171 行 / 17,567 B**（与 git HEAD 一致）⇒ **按实修正、不改文件内容**。**⚠️ R4 未新增「早报→当日」机械复核对（如实 · 不充数）**：信号面 as-of **仍 2026-09-30** ⇒ `daily k=1` 目标日**仍 2026-10-08**，**该格 R3 已核**（`AM_PM_CHECK.md`）。**`daily/2026-10-09.md` AM 版**（§0 口径块 · §1 盘前信号简报 · §2 昨日复核 · §3 结论 · §4 变更记录〔PM 段待 18:00〕）。**② 第八十一轮常态采集 news +5**（中文 3 / 英文 2）——详见 `news/2026-10-09.md` 与 `daily-memories-news/2026-10-09.md` `[06:00]` 心跳。**③ G2′④**：**本早报轮不做真实重跑**（距 2026-10-08 18:24 仅 **~11.6h < 20h**）⇒ **推迟至 18:00 晚报轮**（届时 ~23.6h）；**06:00 误起的后台 `cycle_run.py` 已终止**；**不刷行、不补记**（§4-9/§4-10 如实）。**非因果 · 非投资建议 · L3 冻结** 口径不变。

- 🔀 **2026-10-08（第 11 批 · R3 · P0 · 18:00 晚报轮 · 同日第二版）** —— ✅ **P0 R3 + 第八十轮 news +2 + `cycle_run.py` 真实重跑**（R3 = 38 标的价格全量刷新 ok=38/fail=0 · 三处窗口口径补丁「价格 ∩ 语料」截断 · `lag_corr.csv` **与 R2 逐字节一致** · 🆕 `am_pm_check.py` → `AM_PM_CHECK.md`〔63 格·未赢基线〕· `INDEX_FILES.md` R3 重登记 · `daily/2026-10-08.md` PM 版 · 台账追加 `18:24` 行〔指纹 `9909e4cddcf525a8`〕）。流水**原文已滚入** `daily-memories-news/2026-10-08.md`（`[18:25]` 心跳；**原文不改 · 结论不变**）。

- 🔀 **2026-10-08（第 11 批 · R2 · P0 · 06:00 早报轮）** —— ✅ **P0 R2（`block_boot.py` 3 组 G1/G2/G3〔G3 = 19/20 CI 跨 0〕+ `FINDINGS.md` + 首份早报 AM + `LAG_CORR.md` R2 头）+ 第七十九轮 news +6**。流水**原文已滚入** `daily-memories-news/2026-10-08.md`（`[06:10]` 心跳；**原文不改 · 结论不变**）。



- **2026-10-07（第 11 批 · R1 · P0）** —— ✅ **新闻信号→资产价格 R1 交付**：`news/signal/` = **PREREG.md（先于结果）+ SOURCE_TEST.md（源实测 ok=38/fail=0）+ fetch_prices.py + prices/〔38 标的/6 类/2016–2026·2.56MB〕+ INDEX_FILES.md + lag_corr.py → lag_corr.csv（23940 格）+ LAG_CORR.md**。**结论（如实·非因果·非投资建议）**：**FDR 后 `q<0.10`=0、`stable`=0**；未校正 `p<0.05`=1217/23940≈5.08%≈随机基线 ⇒ **未发现稳定滞后相关**（负面结果照写）。详见 `daily-memories-news/2026-10-07.md` `[18:00]` 心跳。

- 🔀 **第七十八~五十九轮及更早（2026-10-06~10-07，第 10 批块 + 第七十八~十九轮；news +25）**：流水原文均已滚入 `daily-memories-news/2026-10-06.md` / `2026-10-07.md`（📦 滚动归档 · **原文不改·结论不变**）。要点：**78** 软件股阶段新高 · **77** OpenAI 数学 722 手稿 / 美司法部「超级智能」/ SpaceX $40B · **76** Anthropic CVP 129k 漏洞 · **75** Melius $20M · **74** 留空 · **73~63** Underdog / Musubi PolicyLM-1.7B / Lambda $4B / Wajo / Mirror Particle / EmbeddingGemma 2 / Claude Team（+7）· **62** FSD 欧盟 / LibreOffice「no AI」· **61** AMD 苏姿丰 · **60** Mistral Large 4 等（+4）· **59 及更早**（含第 10 批块）见归档。
