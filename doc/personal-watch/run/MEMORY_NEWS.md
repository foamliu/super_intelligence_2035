# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· 第 232 轮已完
已完成:      建哨 · 免费搜索/NEWS 取数 · 第 11 批 R1–R7 · 第 12 批报告 · 第 13–16 批头条（发文 + 引流评论 + 回评 + 自赞 + STYLE/PERSONA）· 第 189–232 轮采集 + 发帖 + 评论
- 当前动作:（**第 232 轮 · 12:00 准点唤醒 · 11-08 第 3 轮** · 窗口 11-08 09:3x → 12:0x CST）① **采集 7 条独立事件**：§1 ×1 **特斯拉 AI 加速器路线图更新**〔`023/876`〕（SI6 算力达 HW4 的 80 倍 = 17.28～46.08 POPS、内存 9 倍、预计 2029–2030；Dojo D3 弃晶圆级 SRAM 改多芯粒 + 堆叠 HBM、面向太空部署；命名改用「超级智能 SI」、SpaceXAI 将更名 SpaceXSI）；§2 ×1 **美国 NHTSA 召回机制改革：OTA 成提升修复率核心路径**〔`023/866`〕（2025 年召回近 900 起 / 超 2,900 万辆；约四成车主因不便未修；150 万美元补助州 DMV 通知；特斯拉 2024 年 OTA 修复约 70 万辆 TPMS；意见截至 12-05）；§3 ×2 **索尼全球首发「车载乘客眩晕检测」**〔`023/860`〕（双路视频 + AI 预测眩晕、提示少急刹急转、与北京交通大学合作、复用原 ADAS 前视摄像头）· **微软 Outlook/Hotmail 邮件被报无故丢失**〔`023/838`〕（SPF 验证失败退信 550 5.7.23、已正确配置亦被拒、11-05 起、微软未回应）；§4 ×2 **毕马威《2026 全球财务智能化调研报告》**〔`10728290`〕（20 国 13 行业 1,013 位财务主管；超四分之三企业已用 AI；具备验证能力企业见效快 3–6 倍；33% 人机协同监督）· **香港城市大学（东莞）研讨会：AI 时代人才画像**〔`10728284`〕；§5 ×1 **特斯拉 Cybertruck 再涨价最高 9%、入门双电机版暂停接单**〔`023/863`〕（84,990→92,490；Cyberbeast 首破 10 万美元；2027 年年中停产让产能给 Cybercab）；§6 = 0（如实）；附录 Z1–Z5；`SEEN.md` +9（2,087→**2,096**）· `INDEX.md` 11-08 行 14→**21**；IT之家 RSS 60/60 · 正文 7 篇 `<title>` **7/7** 一致 · 中新网 30/30（正文 2/2）· 量子位 10/10（0 新增）② **发帖 1 篇 12:04 `w/1881261380548615`**（6 段 / **213 字符** · 后台作品数 **582→583** · `引用AI=true`+`头条首发=true` 读回后发布 · 公开页「作品声明：内容由AI生成」`hasAI=true` ✅）⇒ 本日 **3/6** ③ **评论 5**（35/37/33/36/34 字，**0 截断**；第 4/5 条首次 `TITLE_MISMATCH` RC 8 **未提交** ⇒ 改关键字重跑通过）⇒ 本日 **15/40**④ **自赞 1** · **回评 0/3**⑤ 基线 **82（+1）/ 43,868（昨 337）/ 8.99 元** ⑥ 🐞 新坑：新目录脚本未改路径 ⇒ `ins2.py` 曾把上一轮旧稿填进输入框（**未发布**，覆盖重填并核对 `total` 才发）⑦ 截图 **0 入库**
- 下一步:（第 233 轮 · 本日 15:00 时窗 · 本日第 4 轮）① 采集：窗口 11-08 12:0x → 15:0x；IT之家 RSS（时点基线 = `1/023/878`，GMT 11-08 03:54:12 = CST 11:54:12）+ 正文 `https://www.ithome.com/1/<栏目>/<id>.htm`（**必带 `1/` 段**、逐篇比 `<title>`）；中新网 `scroll-news.xml`（基线最新 `10728299`）；量子位 `qbitai.com/feed`（基线 `508264`）② 发帖配额 **3/6**（下篇须距 12:04 ≥90 min）评论日计数 **15/40** ③ 评论前固定姿势：`open` 新 page（**PUT**）→ `Page.navigate` → 核 `location.href`+`document.title` → `cmt_lib.run`（复用 `/tmp/r232/cmt_one.py`）+ `assert`（`len<=40` 且无 ASCII 字母）+ **`want` 关键字必须直接取自站点标题实际片段** ④ 发布固定顺序：**先 `sed` 改脚本内 `/tmp/rNNN` 路径** → `ins2.py`（核 `total` 与 `paras.json` 一致）→ `decl.py`（读回 `引用AI=true`）→ `publish.py` → 公开页复核 → 主页取 `w/<id>` ⑤ 一律 `nohup setsid` + 读日志判结果 ⑥ 主文件已回 **≈21.6KB**（线内） ⑦ **番茄线**：`can_create_serial_book=false` ⇒ **等裁断，不重试**
- 阻塞: 无（⚠️ 观察项：① 粉丝 82（昨日 +1）· 收益 8.99 元 · 总阅读 43,868（昨日 337）；② 番茄建书开关 `can_create_serial_book=false` 待裁断（**不逐轮重试**）；③ 通用搜索对具体人名仍不可用；④ 知乎 / 雪球等仍被墙，采集只靠 RSS + 正文；⑤ 第 230 轮第 2 条引流评论被截断（19/35 字）已如实记账、**未删未重发**；⑥ 量子位 `508244` 仍按 §0.1 判据 3/4 归附录；⑦ `023/870`（台积电否认 3D DRAM）与 `023/858` 内存题材重叠，**已归附录不重复计数**）
- 📦 第 231 轮快照 3 行原文（5860 B · sha `9595eba55cfa97c7`）→ ARCHIVE「2026-11-08 12:2x」
- 📦 第 230 轮快照 3 行原文（4821 B · sha `2b51801a377b75bf`）→ ARCHIVE「2026-11-08 12:2x」
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

- **[07:0x] wake (2026-11-07 第 224 轮)** | PHASE=常态采集 | news +11 独立事件（§4 = 0 如实；IT之家 60/60 标题全读 · 正文 10/10 `<title>` 一致 · 量子位 10/10（正文 2/2）· 爱范儿 20/20（0 入主类）· 中新网 30/30（正文 1/1））· 发帖 1（`w/1881151899051011` · 后台 **574→575** · 5 段 271 字符 · `引用AI`+`头条首发` 双读回 true 才发 · 公开页「作品声明：内容由AI生成」）· 评论 4（引流 3：`12→13`/`30→31`/`0→1` + 自帖 1：`0→1`，均 `mine=true`）· 点赞 0 · 回评 0/3（评论管理首屏 10 条全为「我」）· 基线 **80 / 43,215 / 8.93**（三项未变）· 🐞 `declchk` 写死旧帖 id + 会把标签带离发布页（草稿未丢）· 发布页复选框 **9 个** · 记忆滚动 30,104 → **30,626 B**

- **[18:0x] wake (2026-11-06 第 222 轮)** | PHASE=常态采集 | news +10 独立事件（六类全覆盖；IT之家 60/60 标题全读 · 正文 14 篇 `<title>` 14/14 · 量子位 2/2 · 中新网 3/3）· 发帖 1（`w/1881102908820483` · 后台 **572→573** · `引用AI`+`头条首发` 双读回 true 才发 · 公开页「作品声明：内容由AI生成」）· 评论 4（引流 3：`1→2`/`0→1`/`2→3` + 自帖 1：`0→1`，均 `mine=true`）· 点赞 0 · 回评 0/3（评论管理 10 条全为「我」）· 基线 **80 / 43,215 / 8.93**（均未变）· 🐞 IT之家 URL 误加 `1/`→404 假页（须比 `<title>` + `--compressed`）· 🐞 前台 30s 超时 ⇒ `nohup setsid`
- **[15:0x] wake (2026-11-06 第 221 轮)** | PHASE=常态采集 | news +10 独立事件（六类全覆盖；IT之家 60/60 · 正文 40 篇 title 40/40 · 中新网 30/30 · 正文 28/28）· 发帖 1（`w/1881091724984328` · 后台 **571→572** · 引用AI 读回 true · 公开页 hasAI=true）· 引流评论 3 落地 + 自评 1 · 点赞 0 · 回评 0/3（无新提问）· 基线 **80 / 43,215 / 8.93**
- **[12:00] wake (2026-11-05 第 214 轮)** | PHASE=常态采集 | news +10（IT之家 60/60 · 正文 11 篇 `<title>` 11/11 · 量子位 10/10 · 爱范儿 15/15 与 cn_news 30 条均 0 入主类）· 发帖 1（`w/1880989577460748` · 后台 **564→565** · 「内容由AI生成」✅ 两次复核 · **已发布+首发**）· 评论 2 确认 + 1 存疑（4 条因页面级输入失效放弃）· 自赞 0 · 回评 0/3 · 基线 **79 / 42,981 / 8.89**

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **N1 语料库**：`news/archive/chinanews-<年>.jsonl.gz`（只 5 字段；**仅取 标题+日期+来源+链接，不抓正文**）；现 **2,492,230 条 / 3929 天 / 11 片**（**2016-01-01 ~ 2026-10-03**；游标 `2015-12-31` = **倒序抓取已收尾**）；⚠️ **≥5MB → 不入 git**，清单见 `news/archive/INDEX_FILES.md`
- **L1 产物**：`news/policy/`（`EDA.md` / `TAXONOMY.md` / `SIGNALS.md` / `EVENTS.csv` / `EARLY_WARNING.md` / **`cycle_run.py` + `STABILITY_LOG.md`（G2′④ 运行台账）**）
- **L2 产物（探索性 · 非因果）**：`news/policy/`（`L2_PREREG.md` / **`EXPLORE.md` + `explore.csv`**）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：**每天 2 次定时唤醒（06:00 / 18:00，`SCHEDULE_HOURS=6,18`）**，时窗内零 token 分段睡（2026-10-07 用户令）；**`WAITING` 已不影响节律**（仅人读状态）；旧自适应 `WAITING=1`→睡 30min / `WAITING=0`→短睡 60s **降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）
- **第 11 批产物（P0 · 新闻信号 → 资产价格）**：见 `news/signal/`〔`PREREG.md` / `SOURCE_TEST.md` / `prices/`（38 标的十年 2016–2026）/ `lag_corr.py` → `lag_corr.csv` + `LAG_CORR.md` / `BOOTSTRAP.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `INDEX_FILES.md` / `REPORT.html` / `daily/<date>.md`〕；⚠️ ≥5MB 不入 git（`lag_corr.csv` ≈ **4.0MB ⇒ 入 git**）
- 📦 状态头旧行（208/175/171 三轮采集窗口 + 累计收录旧行）→ ARCHIVE「2026-11-05 21:5x」「2026-11-06 15:4x/15:5x」
- ⚠️ **去重 grep 口径（2026-10-25 定论）**：查 `SEEN.md` 必须**英文专名 + 中文译名双查**（本轮只查译名险些让 PerturbAI 事件重复入账）；**未读到正文的条目一律不写数字**（IT之家 `1/017/274` 实为 PerturbAI 一文，抓取摘要里的 GPU 解锁比例不可用）。
- ⚠️ **头条评论焦点坑（2026-10-20 定论）**：`www.toutiao.com` 评论框要 **user-activation**，`cdp.py` 每次新建 WS 会丢激活 ⇒ 点击无效、`ABORT_NO_FOCUS`。**点击前必须 `Emulation.setFocusEmulationEnabled {enabled:true}` + `window.focus()`**（参考 `/tmp/ng/cmt_lib.py: unlock()`）。
- ⚠️ **两个计数勿混（2026-10-23 定论；计数随发帖增长，10-24 18:5x 实读 = 493）**：**微头条列表 = 484 条（历史口径）**（`profile_v4/weitoutiao`）；「**作品管理 / 全部内容 = 575**」含草稿与其他体裁 ⇒ 台账/记忆**一律记 484**，不得与 575 互推。
- ⚠️ **「头条首发」有 100 字门槛（2026-10-25 21:5x 定论，读 React 源码得出）**：发布页 `onChange` = `E<100 ? toast('声明首发需不少于100字') & setChecked(false) : setClaimExclusive(1)` ⇒ **正文 <100 字的短帖永远勾不上首发，属平台规则而非工具故障**（本轮为此白折腾 ~35 min）。短线稿子要么写足 100 字，要么放弃首发声明。
- ⚠️ **发布页残留 state（2026-10-25 21:46 实证）**：同一 `targetId` 若「填过 A 稿未发」再填 B 稿，页面 state 会混入 A 稿内容并发出（本轮导致 18:02 虚拟电厂稿被重发一次，后台计数 499→500）。**铁律：每稿用 `/json/new` 开新 page 再 `fill_pm.py`。**
- ⚠️ **评论落地判据改版（2026-10-25 21:5x）**：`tt_cmt.py` 的 `RECHECK mine=false` **不可作失败判据**（新评论常落进「查看全部 N 条评论」折叠区）⇒ 判据 = 「评论计数 +1 **且** 页面向下滚 ≥1200px 后正文中出现 `Xmodel唠两句`」。
- **累计收录**：见 `news/INDEX.md` 逐日行（旧说明已归档 → `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-06 15:5x」）

---



## 2. 流水（倒序，保留最近 ~20 条）
- 🔀 **2026-11-08（第二百三十二轮 · 12:00 准点唤醒 · 本日第 3 轮 · 窗口 11-08 09:3x → 12:0x CST）** —— ① **news +7**（§6 = 0，如实）+ 附录 Z1–Z5：§1 **特斯拉 AI 加速器路线图（SI6 算力达 HW4 的 80 倍 = 17.28～46.08 POPS、内存 9 倍、2029–2030 推出；Dojo D3 弃晶圆级 SRAM 改多芯粒 + 堆叠 HBM、面向太空部署；命名改用「超级智能 SI」）**〔`023/876`〕；§2 **美国 NHTSA 召回机制改革：OTA 成提升修复率核心路径（2025 年召回近 900 起 / 超 2,900 万辆；约四成因不便未修；150 万美元补助州 DMV 通知；特斯拉 2024 年 OTA 修复约 70 万辆 TPMS）**〔`023/866`〕；§3 **索尼首发「车载乘客眩晕检测」（双路视频 + AI、与北京交通大学合作、复用原 ADAS 前视摄像头）**〔`023/860`〕· **微软 Outlook/Hotmail 邮件无故丢失（SPF 退信 550 5.7.23、已正确配置亦被拒、11-05 起）**〔`023/838`〕；§4 **毕马威《2026 全球财务智能化调研报告》（20 国 13 行业 1,013 位财务主管；超四分之三已用 AI；验证能力企业快 3–6 倍）**〔`10728290`〕· **港城大（东莞）研讨会：AI 时代人才画像**〔`10728284`〕；§5 **Cybertruck 再涨价最高 9%、入门双电机版暂停接单**〔`023/863`〕；`SEEN.md` +9（2,087→**2,096**）· `INDEX.md` 14→**21**；IT之家 60/60 · 正文 7/7 一致 · 中新网 30/30（正文 2/2）· 量子位 10/10（0 新增）② **发帖 1 篇 12:04 `w/1881261380548615`**（6 段 / **213 字符** · 后台 **582→583** · `引用AI=true`+`头条首发=true` 后发布 · 公开页「作品声明：内容由AI生成」✅）⇒ 本日 **3/6** ③ **评论 5**（35/37/33/36/34 字，**0 截断**；第 4/5 条首次 `TITLE_MISMATCH` RC 8 **未提交**，改关键字重跑通过）⇒ 本日 **15/40** ④ **自赞 1**（`detail-like like`，`赞`→`1`）· **回评 0/3** ⑤ 基线 **82（+1）/ 43,868（昨 337）/ 8.99 元（无变化·更新中）** ⑥ 🐞 坑：新目录脚本未改路径 ⇒ `ins2.py` 曾把上一轮旧稿填进输入框（**未发布**，重填并核对 `total` 才发）⑦ 截图 **0 入库**
- 📦 第 231 轮流水分条原文（2512 B · sha `2e0c5aa90d23fbe4`）→ ARCHIVE「2026-11-08 12:1x」
- 📦 第 229 轮流水分条原文（1737 B · sha `908a057b44ee6966`）→ ARCHIVE「2026-11-08 10:0x」
- 📦 第 228 轮流水分条原文（1769 B · sha `912cdaa0942264a3`）→ ARCHIVE「2026-11-08 10:0x」

- 📦 第 226 轮流水分条原文（1715 B · sha `5879a1efe6dd41ca`）→ ARCHIVE「2026-11-08 10:0x」
- 📦 第 230 轮流水分条原文（1879 B · sha `2665832333ef7d26`）→ ARCHIVE「2026-11-08 10:0x」
- 📦 第 224 轮快照 6 行原文（4,981 B · sha `17fa848d9a326882`）→ ARCHIVE「2026-11-07 09:5x」
- 📦 第 217 轮流水分条原文（1,825 B · sha `98190bacf22303df`）→ ARCHIVE「2026-11-06 15:3x」
- 📦 第 212 轮流水分条原文（1,416 B · sha `f18f5feb821079e1`）→ ARCHIVE「2026-11-06 15:2x」








> 📦 **体积纪律**：主文件超 32KB 时，最旧条目**原文**搬入 `MEMORY_NEWS_ARCHIVE.md`（**一字未改**，按时间倒序）。2026-10-23 09:5x 搬迁 1 条（10-19 21:30，1,267 B 逐字一致），主文件 34,487 → **33,219 B** 后又插入本轮条目 ⇒ 现 **≈35.2KB**（仍略超 32KB，下次唤醒再搬 1–2 条，**本轮已守诚**）。

## 🧷 铁律补记（2026-10-26 21:5x · 第 154 轮自纠后）

1. **IT之家正文只认 RSS 原链**：`https://www.ithome.com/<栏目>/<YYYY>/<MM>/<DD>/<id>.htm`。省略日期的短链（如 `1/018/121.htm`）会**回落到同 ID 旧文**（本轮实测返回 2026-03 一篇「深度链接侵权」稿）。**取正文前必须比对返回页 `<title>` 与 RSS 标题；不一致 ⇒ 不得标「正文全文已读」，更不得入账。**
2. **发布/评论作业一律 `nohup setsid … &` + 读日志判结果**：`run_commands` 前台 30s 硬超时会把命令杀掉，但后台作业照跑（第 154 轮发布即此情形，结果以 `/tmp/r154/pub.log` 为准，勿重复发布）。
3. **IT之家 RSS 链可能 404 ⇒ 先探再取**（2026-10-30 第 178 轮新增）：`1/020/985.htm` 实测 **404**，真实路径为 `1/019/985.htm`（栏目号**不随日期机械递增**）。取正文前：① 先看 HTTP 状态；② 再比 `<title>` 与 RSS 标题；③ 都对才入账。
4. **正文容器双模板**（同日新增）：`id="post_content"` 与 `id="paragraph"` 混用；只用前者正则会**取到页脚脚本 / 无关广告稿**（`1/020/039` 实测）。统一按 `id="paragraph"` 段落容器取，并**逐篇比对 `<title>`**。
5. **头条页滚动/点赞必须用「真滚动 + 真鼠标」**（同日新增）：`window.scrollBy` 在该站常**不生效**（元素 `y` 恒定）⇒ 滚到目标用 **`el.scrollIntoView({block:'center'})`**；点赞/自赞必须 **`Input.dispatchMouseEvent` 真实鼠标点击**（`element.click()` 即使元素已在视口内也不触发）。判据 = `div.ttp-comment-like > .inner` 的 `liked` 类 + 计数文本（「赞」→「1」）。
7. **发布脚本不含勾选动作 ⇒ 必须先勾后发**（2026-11-06 第 219 轮自纠）：`/tmp/ng/pub1210.py` 只「读勾选态 → 点发布」，**不会设置声明** ⇒ 本轮以 `引用AI:false` 发出。**固定顺序：`sel_decl2.py`（打印 `引用AI=true`）→ 发布脚本**。「修改」补正可行但代价高（见第 8 条）。
8. **后台「修改」编辑页：`正文字数=0` 时点发布无效**（同日实测）：`publish?edit_id=<id>` 页面把正文渲染出来，但计数器为 **0**，此时点「发布」**不跳转、无 toast、剩余修改次数不减**（连试 2 次仍是 `REMAIN 5`）。**解法 = 编辑页全选清空 → 逐段重新输入**（段间 `Shift+Enter` 软换行）⇒ `counter` 变为真实字数后再点发布即成功。⚠️ 另：**页面对同一帖反复点「修改」会累积多个 `publish?edit_id=` 标签** ⇒ 用完即 `json/close`。
6. **发评论前必须逐字核对目标帖标题**（2026-10-30 第 180 轮自纠后新增）：探楼（`cmtbox`）拿到的 ID 若与候选行写错一位，脚本会**发到另一篇帖子上**（本轮 5 条里 1 条发到《谷歌的新AI世界模型…》）。⇒ 规则：**发评脚本必须先打印 `document.title`，与候选标题逐字比对一致后再输入正文**；发错即如实记账、🚫 不删评掩饰。
9. **评论脚本必须先「导航」再发评**（2026-11-07 第 229 轮踩坑后新增）：`news/fanqie/cdp.py open <url>`（走 `/json/new`）返回的 page **停在 `about:blank`**，而 `cmt_lib.run()` **自己不做 `Page.navigate`** ⇒ 直接跑会 `TypeError: 'NoneType' object is not subscriptable`（本轮连挂 2 次，**均未产生任何提交**）。✅ 固定姿势（已封 `/tmp/r229/cmt_one.py`，下轮直接复用）：`open` 新 page → `Page.navigate` → 等 10 s → 核 `location.href` 以 `https://www.toutiao.com/article/` 开头、`document.title` **含候选关键字** → `cmt_lib.unlock` → `cmt_lib.run`。🎯 附带收益：每帖单开 page **同时解决第 228 轮「评论组件 SPA 复用 / `AFTER` 列表是上一篇的」**；落地判据升级为「首屏第 1 条 = `Xmodel唠两句 … 刚刚 删除`」。
10. **评论正文不要夹 ASCII / 拉丁字母**（2026-11-08 第 230 轮自纠后新增）：`ttx.T.type()` 逐字输入时遇到 ASCII 片段（本轮 `vibe coding`）会**中途停止**，但脚本仍会点「提交」⇒ 落库评论**被截断为半句**（本轮第 2 条：原稿 35 字 → 实际 19 字）。✅ 规则：① 评论一律**纯中文 + 中文标点**；② 若必须夹 ASCII，`type` 后先回读 `div.comment-textarea` 的**实际长度**（`TYPED.len` 是当时值、不可当成功判据），不足则补齐再提交；③ 发错/截断**如实记账，🚫 不删评掩饰、🚫 不重复补发同帖**。
11. **`/json/new` 只接受 PUT**（2026-11-08 第 231 轮实测）：`urllib.request.urlopen('http://127.0.0.1:9222/json/new?<url>')` 直接 GET 会报 **`HTTP Error 405: Method Not Allowed`**（Chrome/155.0.8059.39）。✅ 新开标签一律用 **`news/fanqie/cdp.py open <url>`**（内部已 `method="PUT"`），或自建 `Request(url, method='PUT')`。✅ **落地效果**：本轮草稿期加 `assert len<=40 and 无 ASCII 字母`，5 条评论 **39/35/37/36/37 字全部完整落库、0 截断**（第 230 轮同类坑未再复发）。
12. **评论脚本的 `want` 关键字必须直接取自站点标题实际片段**（2026-11-08 第 232 轮新增）：本轮第 4/5 条因我自拟的简称（「陈建斌回应AI陈建斌」「男子考驾照时利用AI眼镜作弊」）与站点标题文字不一致，被铁律 6 的 `TITLE_MISMATCH` **拦下（`RC 8`，未输入正文、未产生提交）**；改取标题内确实存在的连续片段（`AI陈建斌` / `正确率比他自己做还低`）重跑即通过。✅ 规则：`want` 一律**从 `document.title` 实测结果里复制**，不要凭候选行简写。另：**`/tmp/rNNN` 新目录的脚本必须先 `sed` 改掉写死的 `/tmp/rMMM` 路径**——第 232 轮 `ins2.py` 未改路径，读的是上一轮的 `paras.json`，**把旧稿填进了发布框**（`total=241`），发现后覆盖重填（`total=213`）核对一致才发布；⇒ **填完稿先比对 `total` 与 `paras.json` 累加值**。

- 📦 原第 153 行（错位指针行）已归档 → `MEMORY_NEWS_ARCHIVE.md`（sha256 `1b73c125a33c3dcf`；240 B）
Volume:      MEMORY_NEWS.md **~28.9KB（第 232 轮实测）**（红线 40KB 内 ✅）；第 232 轮滚动：搬 **4 段**原文 → `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-08 12:1x / 12:2x」（第 231 轮流水分条 2,512 B · 第 231 轮快照 3 行 5,860 B · 第 230 轮快照 3 行 4,821 B · 均一字未改，sha 已登记）；本轮新增：快照 3 行重写 + 流水 1 条 + 铁律补记第 12 条。

