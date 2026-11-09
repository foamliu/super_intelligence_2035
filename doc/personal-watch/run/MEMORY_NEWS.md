# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· 第 238 轮已完 · 本日发帖 3/6 · 评论 11/40
- 当前动作:（**第 238 轮 · 12:00 时窗 · 本日第 3 轮** · 窗口 11-09 09:3x → 12:0x CST）① **采集 7 条**（§6 = 0 如实）+ 附录 X1 / Y1–Y8：§1 **Anthropic 发布科学家使用 Claude 的实测报告**〔`1/024/111`〕（20.7 万次科研会话 = 12.9 万次 Claude 对话与 Cowork + 7.8 万次 Code·2026-08-02~09-30 / 只留学科·子领域·任务标签·不存研究内容 / 数据分析占会话 33.7%·Code 48.1%，写作沟通 32%（研究人员工作时间 27.6% / 16%）/ 数据收集占工作时间 28.6% 却仅占会话 11.5% / **研究构思与假设生成仅 4.2%·2.1%**（工作时间 7.1%）/ CS 研究者占全球 4.3% 却贡献 Code 会话 32.7%；AI·ML 占 1.2% 却占 Code 15.2% / 另问卷 528 人）；§2 **特朗普：AI 风险可控、「不介意设置护栏」、愿与民主党合作**〔`1/024/071`〕（路透社 / 与其「科技公司自我监管」旧立场松动 / 2025-09-14 曾称 AI 安全担忧是「骗局」/ 开放程度不明为原文自述·不作推断）；§3 ×4 **10 月 CPI 出现 AI 硬件价格信号**〔`10728628`〕（**数据存储设备 +45.4%·平板 +29.3%·计算机 +23.0%·手机 +16.7%，四项合计影响 CPI 同比 +0.26pp** / CPI 同比 +0.7%·核心 +0.8%·PPI 同比 +5.7% 环比 +0.7%·购进 +7.9% / 鲜菜 −16.9% / 只转载官方价格数据·无投资判断）· **国务院关税税则委员会：11-10 13:01 起 2 个月内继续暂停 24% 对美加征关税、保留 10%**〔`10728657`〕· **公安部 5 项交管新措施 12-01 全国推行**〔`1/024/110`〕（进口小客车凭交管 12123 网上一站上牌 / 试点交管小安「边问边办」/ 机动车 4.8 亿辆·驾驶人 5.7 亿·App 用户超 6.1 亿·日均办理 447 万笔）· **JIC 向三井化学与 DBJ 出售 JSR**〔`1/024/086`〕（股权 13,921 亿 + 债务 4,479 亿日元，总量超 1.8 万亿 ≈758.84 亿元·2027 财年下半年完成 / 全球第二大光刻胶商 / ⚠️ 11-04 第 210 轮拟议线索的落地进展·不重算）；§4 **中国 AI 消费品海外走俏**〔`10728587`〕（激光灭蚊盒播放量超 7000 万·美国众筹 2 万→超 280 万美元 / 「芙崽」日本众筹超 8351 万日元破类目纪录·199 美元 / 深圳智能喂鸟器全球销量 9 月破 100 万台）；§5 **LG 免费开放 K-EXAONE 2.5 API**〔`1/024/069`〕（⚠️ 厂商自述未复测）；`SEEN.md` +11（2,202→**2,213**）· INDEX 11-09 改 **18/0**
- 下一步:（第 239 轮 · **11-09 15:00 时窗 · 本日第 4 轮** · **完整步骤见 `daily-memories-news/2026-11-09.md`「第 238 轮 / 下一步」**）① 采集窗口 11-09 12:0x → 15:0x：IT之家 RSS（基线 `1/024/113` CST 11:47:28，正文容器 `id="paragraph"`、URL 必带 `1/` 段、逐篇比 `<title>`）· 中新网 scroll `10728709` / finance `10728714`（`div.left_zw`，提不到只登标题不写数字）· 量子位 `508466`（连续 3 日不动）· 爱范儿 `1688410` ② **发帖配额本日 3/6**（≤3 篇，间隔 ≥90 min，末篇 ≤21:30）③ **选题建议**：JIC×三井化学×JSR 光刻胶整合 / LG 免费开放 API / Anthropic 科研报告（最贴本书）/ 公安部「边问边办」；⚠️ **CPI 存储涨价 12:04 已发，勿重发** ④ 评论候选：须重新探楼（本轮弃 `7705980631809622568` 私人楼、`7706008572139749914` 0 评非热门）⑤ 作业姿势沿用本轮 9/9：单命令 `setsid nohup python3 x.py > x.log 2>&1 < /dev/null & disown` + `sleep 28; cat x.log`（30s 超时≠失败，读日志判果）⑥ 发布顺序：`newpage.py` → `PRE len=14` → `ins2.py`（核 `BODY total`）→ `decl.py`（**双真**）→ `publish.py` → 用户页 `c/user/4681540376/` 取 `/w/<id>` → 公开页复核 `作品声明` ⑦ **番茄线** `can_create_serial_book=false` ⇒ 等裁断、不重试 ⑧ 📦 记忆写入后再测体积，>32KB 即最小滚动
- 阻塞: 无（① **粉丝 82 · 收益 9.07 元 · 总阅读 43,966**（本轮读数**已变化**：+98 阅读 / +0.01 元；后台「更新中」）② 番茄建书开关 `false` 待裁断（不逐轮重试）③ 通用搜索对具体人名不可用 ④ 知乎/雪球仍被墙 ⑤ 中新网正文 `content_desc` 常空 ⇒ 用 `div.left_zw`，提不到只登标题 ⑥ 头条 feed 时政/涉军/伤亡占比高（本轮 44 候选筛 ~20、探楼 5 弃 2）⇒ **宁缺不评** ⑦ ⚠️ 上轮待补记**已决**：「车机三五年才更新一次」经验性表述，本轮起统一改「更新慢得多」）
- 📦 第 234 轮快照 3 行原文（4,765 B · sha `2f21a03af609a755`）→ ARCHIVE「2026-11-08 21:5x」
- 📦 第 233 轮快照 3 行原文（4307 B · sha `f9711db8cde9e9bd`）→ ARCHIVE「2026-11-08 18:2x」
- 📦 第 232 轮快照 3 行原文（4,648 B · sha `06bd68096bfc170d`）→ ARCHIVE「2026-11-08 15:1x」
- 📦 第 231 轮快照 3 行原文（5860 B · sha `9595eba55cfa97c7`）→ ARCHIVE「2026-11-08 12:2x」
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

- 📦 本区旧 Q&A（2026-10-05 N1 语料库全库完抓 / 已封闭）原文 3,385 B · sha `7f0969ad412a1103` → ARCHIVE「2026-11-09 07:2x」

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
- 🔀 **2026-11-09（第二百三十八轮 · 12:00 时窗 · 本日第 3 轮 · 窗口 11-09 09:3x → 12:0x CST）** —— ① **news +7**（§1 Anthropic 科研报告〔`1/024/111`〕· §2 特朗普「不介意设护栏」〔`1/024/071`〕· §3 ×4 CPI 存储涨价〔`10728628`〕/ 关税〔`10728657`〕/ 公安部 5 项交管〔`1/024/110`〕/ JIC 出售 JSR〔`1/024/086`〕· §4 AI 消费品〔`10728587`〕· §5 LG 免费 API〔`1/024/069`〕；§6 = 0 如实）+ 附录 X1 / Y1–Y8；`SEEN.md` +11（2,202→**2,213**）· INDEX 11-09 改 **18/0** ② 发帖 1 篇 12:04 `w/1881352013542471`（7 段 / **311 字符**三处一致 · 后台 **588→589** · `引用AI`+`头条首发` 双真 · 公开页 AI 声明 ✅）⇒ 本日 **3/6** ③ 评论 **3**（32/29/36 字；4→5 / 7→8 / 0→1，`CODE 0`）⇒ 本日 **11/40** ④ 自赞 1 · 回评 0/3（首屏 10 条全为「我」）⑤ 基线 **82 / 43,966 / 9.07**（本轮读数**已变化**：+98 阅读 / +0.01 元）⑥ 截图 0 入库 · 标签 prune closed=14/14 · 后台作业 9/9 成功 ⑦ ⚠️ 自纠：初稿「一台手机多花三百块」原文无此数据 ⇒ **发布前删除**，其余 7 个数字全部对档 ⑧ 📦 滚动：第 237 轮流水条（1,680 B · sha `7f6d777843fac19c`）+ 6 条旧指针行 → ARCHIVE；34,265 → **31,950 B**
- 📦 第 237 轮流水分条原文（1680 B · sha `7f6d777843fac19c`）→ ARCHIVE「2026-11-09 12:1x」
- 📦 第 236 轮流水分条原文（2885 B · sha `eba5e96b50abcbd4`）→ ARCHIVE「2026-11-09 09:5x」
- 📦 第 235 轮流水条原文（3,545 B）→ ARCHIVE「2026-11-09 07:3x」
- 📦 第 233 轮流水分条原文（2,134 B · sha `d5d2dccffef9287e`）→ ARCHIVE「2026-11-08 21:5x」
- 📦 第 232 轮流水分条（指针行已并入上条 ARCHIVE 块）
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
13. **期刊/媒体的版面位置必须照抄原文，不做同义替换**（2026-11-08 第 235 轮自纠）：IT之家 `1/024/001` 原文为「获该刊**官网首页头条**重点报道」，初稿写成「《自然》**封面**报道」——封面与首页头条不是一回事。**发布前已在 `paras.json` 改回「官网首页头条」**，帖文与台账同步改正 ⇒ 规则：凡涉及**封面 / 头条 / 首页 / 转载 / 首发**等版面用词，一律照抄原文，不自行升格。
14. **`cmt_one.py` 必须自己开页取 tid，不能沿用上一轮参数**（2026-11-08 第 235 轮自纠）：旧版以 `sys.argv[1]` 传 `tid`，而该页签已被上一轮 `t.close()` 关掉 ⇒ 本轮首跑 3 条全 **`RC 1 no target <tid>`（未产生任何提交）**。✅ 已改为脚本内 `PUT /json/new?<url>` 取新页并自动取 `tid`（参数只剩 url / text / want）⇒ 之后 **5/5 一次通过、0 截断、0 重试**。下轮复制脚本时**务必连这版一起复制**。
15. **`/tmp/rNNN` 新目录的脚本清单要一次复制齐**（同日新增）：本轮 `newpage.py` / `probe_pub.py` 漏复制，各报 1 次 `can't open file`（**未产生提交**）。✅ 固定动作：先用 `sed` 批量改路径复制 `base feed look likeme cmgr ins2 decl publish cmt_one chk newpage probe_pub getid run_cmt` 共 13 个，再 `ls /tmp/rNNN/*.py` 与 `grep -l /tmp/rMMM /tmp/rNNN/*.py` 双核（后者应无输出）。
16. **发布计数只认微头条标签页**（同日新增）：`mp.toutiao.com/profile_v4/manage/content/all` 显示的「共 N 条内容」**含草稿**（本轮 677 = 669 已发布 + 草稿箱 8），与微头条标签页「共 585 条内容」口径不同。⇒ 记账一律以**微头条标签页**为准，否则会误记 +8。

- 📦 原第 153 行（错位指针行）已归档 → `MEMORY_NEWS_ARCHIVE.md`（sha256 `1b73c125a33c3dcf`；240 B）
Volume:      MEMORY_NEWS.md **35,036 B（第 235 轮 `wc -c` 实测 = 34.2KB，32KB 软线以上、40KB 红线内 ⚠️ 下轮继续按「最小滚动」搬 1–2 条流水）**（红线 40KB）；第 235 轮滚动：搬 **快照 3 行（第 234 轮 4,765 B）** + **流水 2 条（第 234/233 轮 2,527+2,134 B）** + **指针行 1 条** → `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-08 21:5x」（一字未改，sha 已登记）；本轮新增：快照 3 行重写 + 流水 1 条 + 铁律补记第 13–16 条。

