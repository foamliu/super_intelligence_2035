# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· **第 267 轮已完**（本日第 4 轮 · 12:00 时窗）· 本日发帖 **3/3**（图文文章 3 · `article/7707433091148694058` + `7707463571722895891` + **`7707501720577770038`**）· 评论 **11/40** · 自赞 **2/2** · 回评 **0/3**（如实，无真实提问）· ✅ **主通道维持 = 图文文章（带 1 图）** —— 12:07 新稿四条硬标准 4/4 全过（`/article/` URL · 图 1392×770 complete 渲染 676×374 · `WARN []` · 作品声明：内容由AI生成）
- 当前动作:（**第 267 轮 · 12:00 时窗 · 本日第 4 轮** · 窗口 11-13 09:4x → 12:1x CST）① **采集 10 条**（`news/2026-11-13.md` 第 267 轮段：§1 1 / §2 1 / §3 1 / §4 3 / §5 2 / §6 2）· 🖼 **有图 9 / 无图 1**；IT之家 RSS 60/60 · 正文 14 篇 `<title>` 14/14 一致；✅ **上轮覆盖缺口关闭**：中新网 30/30（0 入主类）· 量子位 10/10（0 入主类）· 爱范儿 15/15（1 入 §1）；`SEEN.md` +11 行（含不收汇总行）· `INDEX.md` 当日 **42**（264 轮 17 + 265 轮 15 + 267 轮 10）② **发布 1 篇（主通道）**：12:07 `article/7707501720577770038`「两千亿美元的算力，账单谁来付」**431 字 / 11 段 / 1 图**（`imgs/2026-11-13-1205-openai-15b.png` 31,891 B · 696×385 · 图注「图：IT之家」）· 后台 `graphic/articles` **17 → 18** · 列表「审核中」→ 重载「已发布」· **四条硬标准 4/4 全过**；⚠️ **配图换过一次**：IT之家首图是 **CNBC 台标直播截图**（禁令 11）⇒ 改取同文第 2 张（OpenAI 标志白底图），看图确认无二维码/外链/台标 ③ **评论 4 条全计数 +1**（岗位收敛 0→1 · TIOBE 0→1 · 癌症疫苗 13→14 · 学习本质 0→1）⇒ 日计 **11/40**；⚠️ **B 条实测 41 字符（超上限 1 字）已落地，如实记，下轮起先 `len()` 校验**；英伟达/黄仁勋系列 · Anthropic 招股书 · 马化腾司庆 · 省委书记调研 宁缺不评 ④ **自赞 1/1**（`detail-like like | 1`）· **回评 0/3 如实**（评论管理首屏 10 行 = DCF9000 观点长评 + 我方历史 9 条）⑤ 基线 12:1x：粉丝 **82** · 总阅读 **44,500（昨日 +252）** · 累计收益 **9.15 元** · 文章后台 **18 条**（草稿 22）⑥ 📦 滚动：第 266 轮快照三行（3,573 B · sha `653f3e5277abe8b2`/`85bb2d0c00a8de00`/`a9d6911fb33a1822`）→ ARCHIVE「2026-11-13 12:2x」⑦ `hr_tabs prune toutiao.com` ⇒ matched=5 kept=1 closed=4/4 · AFTER matched=1 OK
- 下一步:（第 268 轮 · **11-13 15:00 时窗 · 本日第 5 轮**）① **起手先查并发**：`ls -lt /tmp | head`；本稿 `7707501720577770038` 若仍非「已发布」超 2 小时 ⇒ 记焦虑点但**不重发** ② **主通道 = 图文文章**：≤1 篇 · 标题 ≤30 字 · 正文 ≥300 字 · 1 图 + 图注署名 · 双声明；发布前记 `graphic/articles` 计数（现 **18**）；发布后**三重核对**（计数 +1 / 列表首条 / 公开页图 complete + 作品声明）③ **采集**窗口 11-13 12:1x → 15:0x：IT之家从 `1/026/651` 之后；中新网 / 量子位 / 爱范儿照常全跑；每条必填 `🖼 图片` ④ **评论** 日计 11/40，可再评 ≤5；**勿重复**本日 11 楼（`7707267479009034767`/`7707234484353090063`/`7707262762359849512`/`7707210793091170851`/`7707436392657191434`/`7707424412719252003`/`7707455768789877286`/`7707100050426233394`/`7707211353336922665`/`7707390616887443968`/`7707322179695804937`）；**投前逐条 `len(text)<=40` 断言** ⑤ 自赞用精确类名集合 ⑥ 回评走 `comment/all` 逐行判 who ⑦ ⚠️ **待裁断**：本轮 `1/026/484`（白矮星双星）与第 265 轮**同条目重复入账**（已如实标注、未删未改）——请 supervisor 定口径 ⑧ `MEMORY_NEWS.md` 现 ≈31.6KB，本轮已滚 1 次，暂不必再滚
- 📦 第 266 轮快照三行（当前动作 / 下一步 / 阻塞）原文（3,573 B · sha `653f3e5277abe8b2`/`85bb2d0c00a8de00`/`a9d6911fb33a1822`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-13 12:2x」（原文一字未改）
- 阻塞: 老阻塞不变：粉丝 **82** · 收益 9.1 元 · 总阅读 **44,500** · 番茄建书 `can_create_serial_book=false` 待裁断（不逐轮重试）· 通用搜索对具体人名/论文标题不可用 · 知乎/雪球被墙 · 央视网正文容器常为空 ⇒ 正文在 `var contentdate` 脚本内（正则取段落串再剥标签）+ 图片须补 `https:` · IT之家正文取 `id="paragraph"` 段内去标签（⚠️ `1/026/479` 该类段落为 0 ⇒ 只能登记标题级事实）· 头条 feed 涉时政/涉军/涉党史占比高 ⇒ **宁缺不评** · 量子位 RSS 默认 UA 403 须浏览器 UA（图片站带 **Referer 防盗链 403**；**IT之家图片无 Referer 一律 403**）· 中新网正文 URL 日期段必须当日 · `run_commands` 30s 硬超时 ⇒ **两段式 `nohup setsid` + 读日志**（`sleep 40+` 必须放后台）· `/w/` 帖不能用 `cmt_one.py` 评论 · 本机无 PIL / 无 tesseract ⇒ 看图走 CDP base64 + 截图 + 多模态 · IT之家 `src` 是 73B `t.png` 占位 ⇒ 取 `data-original` · 图片面板 `setFileInputFiles` 后须再点面板「确定」· 图注框是图片下方 `textarea[placeholder=请输入图片描述(最多50字)]` · `DOM.setFileInputFiles` 打隐藏 file input 会让该标签页 CDP wedged ⇒ `curl /json/close/<tid>` 只关该页重开，🚫 不 pkill 9222 · **⚠️ 自赞判据必须精确类名集合** · `http://127.0.0.1:9222/json/new` 必须 **PUT**（GET 返回空 body ⇒ JSONDecodeError）
- 📦 第 264 轮快照三行（当前动作 / 下一步 / 阻塞）原文（5090 B · sha `d89dfc6c8e4e1588`/`03b8d62cfc13cac1`/`cf1205c8a8dd0435`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-13 10:0x」（原文一字未改）
- 📦 已归档指针（第 262/260/255/251/248/247/244/241/239/237/236/235/233/232/212 轮快照三行与流水条）→ 原文均在 `MEMORY_NEWS_ARCHIVE.md` 对应归档块内（最新块「2026-11-12 22:0x」sha `969c518f90e0a8db`/`85817918b3524f0f`/`8e1e392539ebff24`）；此处压缩为一行，未改动任何原文与结论

- 📦 第 255 轮快照三行（当前动作 / 下一步 / 阻塞）原文（4,917 B · sha `c618fdeed1247be4`/`1cd697f909a424c0`/`e9642d7be56788c6`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-12 07:3x」（原文一字未改）

- 📦 第 251 轮快照三行（当前动作/下一步/阻塞）原文 → `MEMORY_NEWS_ARCHIVE.md`「2026-11-11 21:5x」（3 行 · 原文一字未改）
  5. ⚠️ **重复发布坑（第 251 轮实证）**：同一 `targetId` 上**再点一次** `预览并发布` + `确认发布` 会生成**新文章**（新 ID），与 10-25「同 targetId 残留 state」不同 ⇒ **每篇发布动作只跑一轮**；点完 `确认发布` 后**只读** `/profile_v4/graphic/articles`，🚫 不重复点发布按钮；要复核就 reload 该列表页。
  6. 🖼 **配图落地**：下载前先看图（`view.py`：base64 注入 `<img>` + 截图 + 多模态读），确认无二维码/微信号/外链短址/第三方水印再用；文件名 `imgs/<YYYY-MM-DD-HHMM>-<slug>.<ext>`，扩展名须与 Content-Type 一致；🚫 不入 git。
  7. 🎯 **图片尺寸坑**：IT之家官图常为**竖长图**（本篇 1017×1431、另一篇 1080×6659）⇒ 正文里渲染宽 676px、高度会被拉得很长；发长图前先看图，过长就换第二张候选。
  8. 📊 **后台读数**：`/profile_v4/graphic/articles` 文首「共 N 条内容」+ 每行 `时间 / 状态 / 展现 / 阅读`，刷新（`location.reload`）才更新状态（12:07 首读「审核中」→ 刷新后「已发布」）。
  9. 收尾：写 `news/<date>.md`（条目 + 通道认定）→ `SEEN.md` / `INDEX.md` → MEMORY 快照 + 流水 + `daily-memories-news/<date>.md` → `git pull --rebase --autostash` → `git add -- run/MEMORY_NEWS.md run/MEMORY_NEWS_ARCHIVE.md run/daily-memories-news run/news` → commit → push → `git status -sb` 无 ahead/behind；提交前 `git status --porcelain | grep -Ei '\.(png|jpe?g|webp)$'` 必须为空。

- 📦 第 243 轮快照 3 行原文（4,400 B · sha `39ab4a59c4f7f6cc`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-10 12:1x」

- 📦 第 231/232/233/234/238 轮快照指针行原文（合计 543 B · sha `3e15984234607c93`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-13 12:3x · 同块补录」（原文一字未改）
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

- 📦 2026-11-10 第 243 轮唤醒流水条原文（1,025 B · sha `82e94b51b6aef7f2`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-13 12:3x」（原文一字未改）
- 📦 2026-11-10 第 242 轮唤醒流水条原文（985 B · sha `b75f3fc1c93db156`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-13 12:3x · 同块补录」（原文一字未改）
- 📦 2026-11-07 第 224 轮唤醒行原文（825 B · sha `e1b32f04f74a1aae`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-12 07:3x（状态头旧行）」（原文一字未改）

- 📦 旧唤醒流水三行原文（2026-11-05 第 214 轮 / 11-06 第 221 轮 / 11-06 第 222 轮 · 1567 B · sha `9cae5577486e10fc`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-11 12:2x」

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **N1 语料库**：`news/archive/chinanews-<年>.jsonl.gz`（只 5 字段；**仅取 标题+日期+来源+链接，不抓正文**）；现 **2,492,230 条 / 3929 天 / 11 片**（**2016-01-01 ~ 2026-10-03**；游标 `2015-12-31` = **倒序抓取已收尾**）；⚠️ **≥5MB → 不入 git**，清单见 `news/archive/INDEX_FILES.md`
- **L1 产物**：`news/policy/`（`EDA.md` / `TAXONOMY.md` / `SIGNALS.md` / `EVENTS.csv` / `EARLY_WARNING.md` / **`cycle_run.py` + `STABILITY_LOG.md`（G2′④ 运行台账）**）
- **L2 产物（探索性 · 非因果）**：`news/policy/`（`L2_PREREG.md` / **`EXPLORE.md` + `explore.csv`**）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：**每天 2 次定时唤醒（06:00 / 18:00，`SCHEDULE_HOURS=6,18`）**，时窗内零 token 分段睡（2026-10-07 用户令）；**`WAITING` 已不影响节律**（仅人读状态）；旧自适应 `WAITING=1`→睡 30min / `WAITING=0`→短睡 60s **降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）
- **第 11 批产物（P0 · 新闻信号 → 资产价格）**：见 `news/signal/`〔`PREREG.md` / `SOURCE_TEST.md` / `prices/`（38 标的十年 2016–2026）/ `lag_corr.py` → `lag_corr.csv` + `LAG_CORR.md` / `BOOTSTRAP.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `INDEX_FILES.md` / `REPORT.html` / `daily/<date>.md`〕；⚠️ ≥5MB 不入 git（`lag_corr.csv` ≈ **4.0MB ⇒ 入 git**）
- 📦 状态头旧行 + 「累计收录」说明两行原文（284 B · sha `48934d0f3305f368`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-11 12:2x」（原指向「2026-11-05 21:5x」「2026-11-06 15:4x/15:5x」）
- ⚠️ **去重 grep 口径（2026-10-25 定论）**：查 `SEEN.md` 必须**英文专名 + 中文译名双查**（本轮只查译名险些让 PerturbAI 事件重复入账）；**未读到正文的条目一律不写数字**（IT之家 `1/017/274` 实为 PerturbAI 一文，抓取摘要里的 GPU 解锁比例不可用）。
- ⚠️ **头条评论焦点坑（2026-10-20 定论）**：`www.toutiao.com` 评论框要 **user-activation**，`cdp.py` 每次新建 WS 会丢激活 ⇒ 点击无效、`ABORT_NO_FOCUS`。**点击前必须 `Emulation.setFocusEmulationEnabled {enabled:true}` + `window.focus()`**（参考 `/tmp/ng/cmt_lib.py: unlock()`）。
- ⚠️ **两个计数勿混（2026-10-23 定论；计数随发帖增长，10-24 18:5x 实读 = 493）**：**微头条列表 = 484 条（历史口径）**（`profile_v4/weitoutiao`）；「**作品管理 / 全部内容 = 575**」含草稿与其他体裁 ⇒ 台账/记忆**一律记 484**，不得与 575 互推。
- ⚠️ **「头条首发」有 100 字门槛（2026-10-25 21:5x 定论，读 React 源码得出）**：发布页 `onChange` = `E<100 ? toast('声明首发需不少于100字') & setChecked(false) : setClaimExclusive(1)` ⇒ **正文 <100 字的短帖永远勾不上首发，属平台规则而非工具故障**（本轮为此白折腾 ~35 min）。短线稿子要么写足 100 字，要么放弃首发声明。
- ⚠️ **发布页残留 state（2026-10-25 21:46 实证）**：同一 `targetId` 若「填过 A 稿未发」再填 B 稿，页面 state 会混入 A 稿内容并发出（本轮导致 18:02 虚拟电厂稿被重发一次，后台计数 499→500）。**铁律：每稿用 `/json/new` 开新 page 再 `fill_pm.py`。**
- ⚠️ **评论落地判据改版（2026-10-25 21:5x）**：`tt_cmt.py` 的 `RECHECK mine=false` **不可作失败判据**（新评论常落进「查看全部 N 条评论」折叠区）⇒ 判据 = 「评论计数 +1 **且** 页面向下滚 ≥1200px 后正文中出现 `Xmodel唠两句`」。

---

## 2. 流水（倒序，保留最近 ~20 条）
- 🔀 **2026-11-13（第二百六十七轮 · 12:00 时窗 · 本日第 4 轮 · 窗口 11-13 09:4x → 12:1x CST）** —— ① **采集 10 条**（§1 1 / §2 1 / §3 1 / §4 3 / §5 2 / §6 2）· 🖼 **有图 9 / 无图 1** · IT之家 60/60 · 正文 14 篇 `<title>` 14/14 · 中新网 30/30 · 量子位 10/10 · 爱范儿 15/15 ⇒ **265 轮覆盖缺口关闭** · `SEEN.md` +11 · `INDEX` 当日 **42** ② **发布 1 篇**：12:07 `article/7707501720577770038`「两千亿美元的算力，账单谁来付」431 字 / 11 段 / 1 图（31,891 B · 696×385 · 图注「图：IT之家」）· 后台 **17 → 18** · **四条硬标准 4/4 全过** ⇒ 主通道维持；⚠️ **配图换图一次**：IT之家首图为 **CNBC 台标直播截图**（禁令 11）⇒ 改用同文第 2 张（OpenAI 标志白底图） ③ **评论 4 条全 +1**（0→1 / 0→1 / 13→14 / 0→1）⇒ 日计 **11/40**；⚠️ **B 条 41 字符超 1 字已落地（如实）**，下轮起投前 `len()<=40` 断言 ④ **自赞 1/1**（`detail-like like | 1`）· 回评 **0/3** 如实 ⑤ 基线 **82 / 44,500（+252）/ 9.15 元** · 文章后台 **18 条** ⑥ ⚠️ **重复入账一处**：`1/026/484`（白矮星双星）与 265 轮同条目，已如实标注未删改，列待裁断 ⑦ 📦 滚动第 266 轮快照三行（3,573 B）→ ARCHIVE「2026-11-13 12:2x」· 体积 32,430 → 33,033 B；`hr_tabs prune` matched=5 kept=1 closed=4/4
- 🔀 **2026-11-13（第二百六十六轮 · 09:30 时窗 · 本日第 3 轮 · 窗口 11-13 07:5x → 09:4x CST）** —— ① **采集 15 条**（§1 4 / §2 2 / §3 1 / §4 2 / §5 4 / §6 2）· 🖼 **有图 11 / 无图 4** · IT之家 RSS 60/60 · 正文 16 篇 `<title>` 16/16 一致 · ⚠️ **量子位 / 爱范儿 / 中新网未跑（覆盖缺口已如实写进摘要与小结）** · `SEEN.md` +16 · `INDEX.md` 当日 **32**（264 轮 17 + 265 轮 15）② **发布 1 篇**：09:38 `article/7707463571722895891`「同一场业绩会，走出了两个数」367 字 / 10 段 / 1 图（558,084 B · 1440×1525）· 后台 **16 → 17** · **四条硬标准 4/4 全过** ⇒ 主通道维持；⚠️ 列表仍「审核中」（发布后 10 分钟内如实记）③ **评论 3 条全 +1**（短剧 0→1 / Grok 0→1 / MCN 1→2）⇒ 日计 **7/40**；黄仁勋·党史·印度·中日·情报类帖宁缺不评 ④ **自赞 1/1**（`detail-like like | 1`）· 回评 **0/3** 如实 ⑤ 基线 **82 / 44,500（+252）/ 9.1 元** · 文章后台 **17 条** ⑥ **两处自纠**：`INDEX` 与摘要初写 13 条（§2 1 / §5 3），复核正文实存 **14** 条 ⇒ 已改并留更正痕迹；第 264 轮「新增 17 条 / 小结表 16」口径差已在 INDEX 并列写明 ⑦ 📦 滚动第 264 轮快照三行（5,090 B）→ ARCHIVE「2026-11-13 10:0x」· 体积 32,724 → 27,878 → 现值 ≈32.4KB（下轮起再滚 1 行）
- 📦 第 264 轮流水分条原文（1515 B · sha `d78785aea4e15e18`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-13 10:1x」（原文一字未改）
- 🔀 **2026-11-12（第二百六十三轮 · 21:0x 时窗 · 本日第 7 轮 · 窗口 11-12 18:0x → 23:3x CST）** —— 采集段与发布段由并发进程完成（21:30–21:48），本次唤醒接手收尾：① **采集核对 12 条**（§1 = 3 / §2 = 2 / §3 = 1 / §4 = 3 / §5 = 2 / §6 = 1）· 🖼 **有图 8 / 无图 4**（顶部「9/3」误算已在小结内如实更正并保留痕迹）· `SEEN.md` +14（含附录 2 条央视网） ② **发布（未重复）** 21:47 `article/7707278451081789994`「三十七个漏洞挖出来，只修了二百多个」983 字 / 15 段 / 1 图（`imgs/2026-11-12-2100-glasswing-funnel.webp` 11,112 B · 1280×720）· 后台 **14 → 15** · **四条硬标准 4/4 全过** ⇒ 主通道维持 ③ **评论 5 投 5 成**（0→1 / 0→1 / 3→4 / 1→2 / 4→5）⇒ 日计 **24/40** ④ **自赞含一次误取消（如实记）**：并发进程 `like3.py` 读到已赞仍盲点 ⇒ 取消点赞；本次用精确类名集合判定补回 `detail-like like | 1`；新增铁律：`'detail-like'.endswith('like')` 恒真 ⇒ 🚫 子串判定 ⑤ **回评 0/3 如实**（DCF9000 观点长评非提问、已回过） ⑥ 基线 **82 / 44,248（昨日 +47）/ 9.1 元** · 文章后台 **15 条**；「未通过」命中经查为筛选 tab 文案非警告 ⑦ 📦 滚动：第 262 轮快照三行（5,753 B · sha `969c518f90e0a8db`/`85817918b3524f0f`/`8e1e392539ebff24`）+ 第 261 轮流水分条（1,367 B · sha `a0d966d31d13efe5`）→ ARCHIVE「2026-11-12 22:0x / 22:1x」；体积 31,705 → **30,906 B**（<32KB）
- 🔀 **2026-11-12（第二百六十二轮 · 18:0x 时窗 · 本日第 6 轮 · 窗口 11-12 15:0x → 18:0x CST）** —— 采集段与发布段由前置进程完成（18:0x–18:25），本次唤醒接手收尾：① **采集核对 12 条**（有图 9 / 无图 3）· `SEEN.md` 本日 85 行 · **INDEX 74 → 86**（补计并注明口径） ② **发布（未重复）** 18:13 `article/7707224580758995475`「一千三百零二辆车，不说明谁在载客」768 字 / 10 段 / 1 图 · `graphic/articles` **13 → 14** · **四条硬标准 4/4 全过** ⇒ **主通道 = 图文文章维持** ③ **评论 5 投 5 成**（0→1 / 2→3 / 0→1 / 0→1 / 1→2）⇒ 日计 **19/40**；1 次草稿含 ASCII `K` 被断言拦下，换全中文重投成功 ④ **自赞 1/1**（先读 className 再点）⑤ **回评 0/3 如实**（DCF9000 为观点长评非提问、6 小时前已回） ⑥ 基线 **82 / 44,248（昨日 +47）/ 9.1 元** · 文章后台 **14 条** ⑦ 台账补第 262 轮整段 · 日流水补收尾段 · 体积 31,839 B（<32KB）
- 📦 第 257 轮流水分条（1,945 B · sha `691f5dd969215565`）→ ARCHIVE「2026-11-12 18:0x」
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
Volume:      MEMORY_NEWS.md **32,233 B（第 257 轮收尾 `wc -c` 实测 · 32KB 软线内）**（红线 40KB）；第 257 轮滚动（最小滚动）：① 第 255 轮快照「当前动作 / 下一步 / 阻塞」三行（4,917 B · sha `c618fdeed1247be4`/`1cd697f909a424c0`/`e9642d7be56788c6`）② 2026-11-07 第 224 轮唤醒行（825 B · sha `e1b32f04f74a1aae`）→ 均搬入 `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-12 07:3x」（原文一字未改，原位各留 1 行指针）。本轮同步：快照 3 行重写 + 流水 1 条 + `daily-memories-news/2026-11-12.md`（新建，第 257 轮段）+ `news/2026-11-12.md`（+16 条，采集段已由 auto-commit `e65654c3f` 提交）+ `SEEN.md` 2,476 + `INDEX.md` 16 + `台账.md` 第 257 轮。

