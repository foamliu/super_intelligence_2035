# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

- 📦 第 343 轮快照四行原文（2834 B · sha `b0c8952cedba2f82`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 09:5x（第 344 轮压红线 · 第 343 轮快照四行原文）」（原文一字未改）
PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· **第 355 轮已完**（11-26 09:3x · 09:30 定时窗 · 本日第 2 轮）· 本轮采集 **11 条**（§1 3 / §2 1 / §3 3 / §4 1 / §5 2 / §6 1 · 🖼 有图 6 / 无图 5 · `SEEN.md` 3,947 → **3,959**，+12）· **图文文章 1 篇（带 1 图）已发**（后台 105 → 106 · 四硬标准 4/4）· 主通道 = 图文文章（带 1 图，不变）· 自赞 1/1 · 引流评论 1 条落地 · CDP 9222 正常
- 已完成: 第 351 轮 9 条 + 1 篇（101→102）；**第 352 轮 12 条 + 1 篇（`article/7712120224836747819` · 102→103）**；**第 353 轮 12 条 + 1 篇（`article/7712127896428479017` · 103→104）**；**第 354 轮 8 条 + 1 篇（`article/7712248867193963050` · 104→105）**；**第 355 轮 11 条 + 1 篇（`article/7712287311320384041` · 105→106 · 4/4 · 自赞 1 · 引流评论 1）**；`SEEN/INDEX/news/` 已同步
- 当前动作: 第 355 轮已收尾（采集 11 条 + 发布 `article/7712287311320384041` + 自赞 1 + 引流评论 1 条 + 记账 + 提交）
- 下一步:（第 356 轮 / 12:00 时窗）① 发布一篇图文文章（带 1 图）—— 从新入账里挑（优先 §1 模型发布或 §3 治理）② 开工三件（`hb` / `git log -- run/news` / 后台 `共 N 条`+首行）+ `pgrep` 查并发 ③ 每轮必须 `grep '^IMG' /tmp/rNNN/common.py` 核对配图路径（`STYLE §A.49` 第 1 条）；取图复核带完整 UA + Referer，IT之家正文图在 `data-original` ④ **配图水印**：量子位全篇图右下角带「公众号·量子位」、IT之家部分图带站标、`x-bce-process=image/watermark` 参数 = 真水印 ⇒ 发布前逐张 `read` 目视，弃用带水印图（`STYLE §A.50/A.51`）⑤ 自赞判 `like` 用 `classList.contains('like')` ⑥ **引流评论**：逐字 `Input.dispatchKeyEvent` 在他人帖可落地（计数 +1 判成功），选平和 AI 楼、≤40 字 ⑦ 发布红线：涉美政坛/军事/伤亡/司法条目**只记不发**（禁令 9）
- 本轮新增: 11 条（来源数：IT之家 8 / 量子位 2 / 中新网 1）
- 阻塞: **无硬阻塞**。**仍需人工裁断/观察**：① 番茄建书 `can_create_serial_book=false` ② 回评 0/3（本轮未对既有用户评论做定向回复，机制待建）③ 长期限制不变（通用搜索对具体人名/论文标题不可用 · 知乎/雪球被墙 · 本机无 PIL/tesseract · 央视网正文前端渲染抓不到 ⇒ 走 CDP · 新发文常先「审核中」· 同一时窗可能有并发 news 进程）。
- ERROR_COUNT:  0
- ⚠️ **git pull --rebase 在本共享工作副本里有坑（第 346 轮实录）**：`git pull --rebase --autostash` 中断后 `.git/rebase-merge` 残留、worktree 会被拨到 `origin/main`（本线未提交改动「看起来消失」）⇒ 处理顺序：① 先查 `.git/rebase-merge`（orig-head / autostash）② 解决冲突只取自己那几行、其它线文件一律 `git checkout HEAD -- <file>`（🚫 不替别人提交）③ 完成后再 `git stash pop` 取回 autostash；**未提交前不要跑第二次 pull**。
- ⚠️ **`SEEN.md` 记数口径（第 346 轮更正）**：以后一律报 `wc -l` 行数（本轮 3,854 → 3,859）；12:38 对 `open(p,'w')` 回写过的 `SEEN.md` 出现「git 不显示 modified + 读到旧内容 + stat 不更新」，12:39 改 `open(...,'a')` + `fsync` 后正常（`git diff` +5 行）⇒ 大表回写后**必须 `git diff --stat` 复核**，看不到改动就追加重写一次，别当成功。

- 📦 第 340 轮快照四行原文（4,448 B · sha `7dab89c8aa18e352`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-23 18:5x（第 341 轮滚动 · 第 340 轮快照四行原文）」（原文一字未改）

- 📦 第 316b/316/315/313/311/308/293/292/291 轮快照与流水条指针 → 原文均在 `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 ~ 11-20」各块内（sha 见各块标题，一字未改）


- 📦 第 287 轮快照五行原文（5893 B · sha `a8f56b205982bdde`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 18:3x」（原文一字未改）
- 📦 第 286 轮快照三行原文（3576 B · sha `0d6222d0871b9078`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 15:4x」（原文一字未改）
- 📦 第 285 轮快照三行原文（4695 B · sha `7934b0595dc9f0d9`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 12:4x」（原文一字未改）
- 📦 第 283 轮快照三行原文（4728 B · sha `c1f2f2f3b6e3d5dd`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 07:4x」（原文一字未改）
- 📦 第 276 轮快照三行原文（3462 B · sha `5e1aa1d2bfd23bc0`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 10:3x」（原文一字未改）
- 📦 第 288 轮流水条原文（2042 B · sha `eab93f41f2fef785`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 09:55（第 313 轮压红线 · 第 288 轮流水条）」（原文一字未改）
- 📦 第 286 轮快照三行原文（1391 B · sha `cc5661db52fe964a`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 22:1x（第 289 轮滚动 · 第 286 轮快照原文）」（原文一字未改）

- 📦 第 273 轮快照三行原文（4,687 B · sha `a697bee9c9e5b96f`）→ ARCHIVE「📦 归档块 · 2026-11-14 12:0x」（原文一字未改）

- 📦 已归档指针（第 262/260/255/251/248/247/244/241/239/237/236/235/233/232/212 轮快照三行与流水条）→ 原文均在 `MEMORY_NEWS_ARCHIVE.md` 对应归档块内（最新块「2026-11-12 22:0x」sha `969c518f90e0a8db`/`85817918b3524f0f`/`8e1e392539ebff24`）；此处压缩为一行，未改动任何原文与结论

- 📦 第 264/255/251 轮快照指针行原文（合计 346 B · sha `d4450803fde82a7d`）→ ARCHIVE「📦 同块补录 · 2026-11-13 15:4x」（原文一字未改）

  5. ⚠️ **重复发布坑（第 251 轮实证）**：同一 `targetId` 上**再点一次** `预览并发布` + `确认发布` 会生成**新文章**（新 ID），与 10-25「同 targetId 残留 state」不同 ⇒ **每篇发布动作只跑一轮**；点完 `确认发布` 后**只读** `/profile_v4/graphic/articles`，🚫 不重复点发布按钮；要复核就 reload 该列表页。
  6. 🖼 **配图落地**：下载前先看图（`view.py`：base64 注入 `<img>` + 截图 + 多模态读），确认无二维码/微信号/外链短址/第三方水印再用；文件名 `imgs/<YYYY-MM-DD-HHMM>-<slug>.<ext>`，扩展名须与 Content-Type 一致；🚫 不入 git。
  7. 🎯 **图片尺寸坑**：IT之家官图常为**竖长图**（本篇 1017×1431、另一篇 1080×6659）⇒ 正文里渲染宽 676px、高度会被拉得很长；发长图前先看图，过长就换第二张候选。
  8. 📊 **后台读数**：`/profile_v4/graphic/articles` 文首「共 N 条内容」+ 每行 `时间 / 状态 / 展现 / 阅读`，刷新（`location.reload`）才更新状态（12:07 首读「审核中」→ 刷新后「已发布」）。
  9. 收尾：写 `news/<date>.md`（条目 + 通道认定）→ `SEEN.md` / `INDEX.md` → MEMORY 快照 + 流水 + `daily-memories-news/<date>.md` → `git pull --rebase --autostash` → `git add -- run/MEMORY_NEWS.md run/MEMORY_NEWS_ARCHIVE.md run/daily-memories-news run/news` → commit → push → `git status -sb` 无 ahead/behind；提交前 `git status --porcelain | grep -Ei '\.(png|jpe?g|webp)$'` 必须为空。

- 📦 第 243 轮快照 3 行原文（4,400 B · sha `39ab4a59c4f7f6cc`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-10 12:1x」

- 📦 第 231/232/233/234/238 轮快照指针行原文（合计 543 B · sha `3e15984234607c93`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-13 12:3x · 同块补录」（原文一字未改）
（原「prep_api 选定方案」段 18 行原文 1,237 B · sha `0a8a5601fc781f9b` → `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 16:1x」；要点：Web 搜索走 CN-Bing 主 + 360 备（MCP `web-search-free`）；新闻取数 HN + GDELT + 官方 RSS；Google/DDG/Brave 等被墙；bocha key 额度用尽）
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

- 📦 第 243 轮流水条原文 → `MEMORY_NEWS_ARCHIVE.md`「📦 第 243 轮流水条原文」
- 📦 旧流水条原文 → `MEMORY_NEWS_ARCHIVE.md`「📦 旧流水条原文」
- 📦 2026-11-07 第 224 轮唤醒行原文（825 B · sha `e1b32f04f74a1aae`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-12 07:3x（状态头旧行）」（原文一字未改）

- 📦 旧流水条原文 → `MEMORY_NEWS_ARCHIVE.md`「📦 旧流水条原文」

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
- 🔀 **2026-11-26（第三百五十五轮 · 09:30 定时窗 · 本日第 2 轮 · 窗口 11-26 07:20 → 09:45 CST）** —— ① **开工三件**：`hb` 1795656600（09:30）· `git log -- run/news` 最新 = 第 354 轮 `8fe4019445` · 后台 `共 105 条`、首行「FSD 进欧洲…」已发布（展现 49/阅读 0/点赞 1/评论 0）；`pgrep` 无并发 news ② **采集 11 条**（§1 3 / §2 1 / §3 3 / §4 1 / §5 2 / §6 1）：IT之家 `1/032/535` DeepMind Mass Spec Skills（质谱识别不足4%→约97%）· `543` OpenAI 开测私有推理「零窥探AI」· `540` 纽约州暂停联网AI聊天玩具销售5年、每日最高罚1.5万美元 · `562` 三部委《新一代通信网建设实施方案》大小模型协同运维 · `542` 韩国 Detect AI 考场反作弊识别AI眼镜、12-09首秀 · `551` Neuralink 获美国首个植入式脑机关键性临床批文（30+参与者）· `548` ElevenLabs 目标估值330亿美元 · `546` FCC 批准 SpaceX 最多100万颗数据中心卫星；量子位 `512565` Loop 架构 9400万参数 vs 50亿、显存21.34GB→0.31GB · `512819` 黎曼 Lean 证明 1740万行→7.6万行（降99.56%，是否成立仍待核验）；中新网 `10737869` 哈萨克斯坦首次用 AI 起草法案 ③ 🖼 **有图 6 / 无图 5**（`535/543/542/551/548/546` 六张 IT之家图只存 URL 未下载；`540` 图带 watermark 参数、量子位两图带公众号水印、`562` 无正文图、中新网模板图 ⇒ 如实「无」）· `SEEN.md` 3,947 → **3,959**（+12）· `INDEX` 当日 8 → 19 · `ith_dedup 60/hit4/new56` · 量子位 10 条 · research `news_ready` 0 新增 ④ ✅ **图文文章（带 1 图）** `article/7712287311320384041`「把机房搬上天：100 万颗卫星的批文，下来了」**09:34** · 12 段 / `共 570 字` · 1 图 PNG 1440×810（1,452,426 B）· 图注「图：IT之家（SpaceX Starmind 太空数据中心示意图，非本号拍摄）」· 后台 **105 → 106** · **四硬标准 4/4**（① `/article/` canonical 一致 `artH 1326` ② 图 676×380 `nw1440 nh810 complete:true broken:0` + 图注可见 ③ `<article>` 内 `NOTICE hits:[]`（全文「版权」来自推荐流他人文章，已排除）④ `DECL found:true`）· 声明 `on:["头条首发","发布得更多收益","引用AI"]` ⑤ **自赞 1/1**（`detail-like` → `detail-like like`）⑥ **引流评论 1 条落地**：他号「黎曼代码」文 `7712272916877558312` 评论「代码瘦身是工程活，证明能不能成立，还得等同行把每一步复核完。」（31 字）· `评论 6→7` · `mine:true` ⇒ 日计 2/40 · 回评 0/3（如实）⑦ 位图 0 入库 ⑧ **新坑（§A.51）**：四硬标准③须以 `<article>` 内为准；`VAR=$(...) cmd` 前置赋值里 `$VAR` 为空 ⇒ 用 `env VAR="$(cat f)"`
- 🔀 **2026-11-26（第三百五十四轮 · 06:00 定时窗 · 本日第 1 轮 · 窗口 11-25 23:25 → 11-26 07:20 CST）** —— ① **开工三件**：`hb` `1795647600`（07:00 CST）· `git log -- run/news` 最新 = 第 353 轮 `e1e6aa6eb4` · 后台文章 `共 104 条内容`、首行「AI 帮你下单，平台先算广告账 · 11-25 23:16 · 已发布 · 首发」；`pgrep` 仅本会话、无并发 news ② **采集 8 条**（§1 3 / §2 0 / §3 1 / §4 1 / §5 2 / §6 1）：量子位 `512727` 秘塔 AI「全民开机」输入故事直出 15 分钟短片（12 种预设 / 16:9·9:16·1:1）· `512715` 智元 AIMA 生态 + 元苼计划五年投入不低于 20 亿元、灵心平台一年 2 万+ 用户 / 3 万+ 智能体 / 7 万+ 内容 · `512582` 九章云极 Physical AI Factory、易观报告 2026 物理 AI 基础设施约 335 亿元、2030 预计超 800 亿元（58% / 178 EFLOPS / CAGR 39%）；IT之家 `1/032/466` 特斯拉 FSD 欧盟审批推迟至 12-15（27 国至少 15 国赞成 + 人口 65% / 原定 12-1、后称 12-7、最终 12-15 / 荷兰 4 月初批 / 十余国跟进 / 意大利已落地）· `1/032/499` 华为陈海波鸿蒙「全栈熵减」；中新网 `10737724` 智源 REAL 物理 AI 评测体系与首批结果（60 余家 / 16 家场景方 / 顺丰·吉利·海尔·TCL 奥赛题 / HumanCOIN 数据集 / 人感安全白皮书）；央视网 AI 数学喜忧参半（OpenAI 722 篇手稿 / 17 分支 / 次日撤回 3 修订 14 / 霍奇猜想正负号错误 / 丘成桐联盟 / 20 岁学生证伪阿诺德猜想）；research `daily/2026-11-26.html` `news_ready 1` = arXiv 2611.33135 BriConstrain LEGO 约束解码（BrickNet 31%→91% / ICLF 15%→65% / ~60% 解码成本）③ 🖼 **有图 5 / 无图 3**：量子位 3 张 + IT之家 466 图 `img_check` 全 `OK 200 image/*`（只存 URL 未下载）；央视/中新正文图为前端渲染/主办方供图 ⇒ 如实「无」；附录 2 条（`512683` 商汤厂商稿 / `512748` 商汤 U1.6 重复主题）；`SEEN.md` 3,937 → **3,947**（+10 含附录 2）· `INDEX` 当日 8 ④ ✅ **图文文章（带 1 图）** `article/7712248867193963050`「FSD 进欧洲，卡在 15 张赞成票上」**07:05** · 7 段 / `共 454 字` · 1 图 JPEG 1348×697（180,845 B）· 图注「图：IT之家」· 后台 **104 → 105** · **四硬标准 4/4**（① `/article/` canonical 一致 `artH 1016` ② 图 676×350 `nw1348 nh697 complete:true broken:0` + 图注可见 ③ `NOTICE hits:[]` ④ `DECL found:true`）· 声明 `on:["头条首发","发布得更多收益","引用AI"]` ⑤ **自赞 1/1**（`classList.contains('like')` → `detail-like like`）⑥ **引流评论 1 条落地**：他号「人人都是产品经理」文 `7711214004168852008` 评论「本体贵在把隐性业务规则写死，Agent越自动，越需要它兜底可解释。」· `评论 11→12` · `mine:true` ⇒ 日计 1/40（破前几轮他人帖不落字）· 回评 0/3 ⑦ 位图 0 入库（新图 `git check-ignore` 命中 `run/**/*.jpg`）⑧ **新坑**：量子位全篇图右下角带「公众号·量子位」水印、IT之家 `499` 图带站标 ⇒ 均弃用，改选无站标的 IT之家 `466`（`STYLE §A.50`）
- 📦 第 351 轮流水条原文（2498 B）→ `daily-memories-news/2026-11-25.md`（原文一字未改）
- 📦 第 350 轮流水条原文（2422 B · sha `c7d8e0ada82fa1c2`）→ `daily-memories-news/2026-11-24.md`「📦 第 350 轮流水条原文」（原文一字未改）
- 🔀 **2026-11-24（第三百四十九轮 · 21:30 唤醒 · 本日第 7 轮 · 窗口 11-24 18:0x → 21:4x CST）** —— ① **开工三件**：`hb` `1795527000`（21:30:00 CST）· `git log -- run/news` 最新 = 第 348 轮 `3ecf16dbac` · 后台 `共 100 条`、首行「一封诈骗邮件… · 11-24 15:06 · 已发布 · 展现 148」；`pgrep` 无并发 news 进程；`/tmp/r349` 为本轮唯一目录（`common.py` 复制后已 `grep '^IMG'` 改成本轮图）② **采集 13 条**（§1 2 / §2 2 / §3 3 / §4 3 / §5 3 · §6 0）：IT之家 `867` Codex 窃听案新细节（100 万美元保释 / 10-09 逮捕）· `811` OpenAI/Anthropic 员工警告内部模型「无法安全发布」（Axios / 二十多名消息人士）· `838` 我国牵头全球首个生成式 AI 治理国际标准提案（29 项 / 49 项 / 近 400 名专家）· `801` 三星/SK 海力士 2030 缺 26 万工人（建筑业 62.9% 为五六十岁）· `818` 小鹏 IRON 预热（11-25 14:00 科技日）· `823` Anthropic 盘前跌破 83 美元发行价（-6.5% 报 82 / 募资 935 亿美元）· `863` Chrome 关后仍占 300–700MB（Gemini 托盘设置）· `704` 罗永浩锤子 713.95 万股权冻结；中新网 `10737216` 香港 OPC BUILD 一人公司 · `10737165` 生成式 AI 治理标准提案（与 `838` 同一发布会，双源互证）· `10737195` BCG 亚太职场 AI（8 国 6349 人 / 中国 87%→88%）· `10737201` 亚洲数学联盟落户港中大（丘成桐任主席）· `10737079` 山东国企 AI（盘古矿山模型 120 余家单位）· `ith_dedup` `60/3/57` · `--cn-news --limit 200` 182 条入 5 · 量子位 `rss_latest` 返回字符串结构异常未取 · research `news_ready 0` ③ 🖼 **有图 10 / 无图 3**（`867`/`838`/`704` 正文页无图 ⇒ 如实「无」；其余 10 张 `img_check` 带**完整 UA + Referer** 全 `200 image/*`；⚠️ IT之家正文图在 `data-original`，`src` 恒为占位图 ⇒ 按 `data-original` 取图；只存 URL 未在采集层下载）④ ✅ **图文文章（带 1 图）** `article/7711730347863507519`「最强的模型，可能正被锁在柜子里」**21:35** · 28 段 / `共 1273 字` · 1 图 PNG 1440×810（850,958 B · sha256 前 16 `432b2f1075781002` · 发布前 `viewimg` 目视无二维码/微信号/外链/水印）· 图注「图：IT之家（AI 主题示意图，非本号拍摄）」· 后台 **100 → 101** · **四硬标准 4/4**（① `/article/` canonical 一致 `artH 2368` ② 图 676×380 `broken:0` + 图注可见（`pub349.jpg`）③ `NOTICE hits:[]` ④ `DECL found:true`）⑤ 自赞 **1/1** ⑥ 评论 0 / 回评 0（如实：本篇 `评论 0`、未做重复打卡评论）⑦ 声明 `on:["头条首发","发布得更多收益","引用AI"]`（按可见文本点 `span`，一次到位，§A.49 第 4 条未复发）⑧ 位图 0 入库 ⑨ 新坑：`s3b` 按「本地上传」文本找入口失败（`FILEINPUTS 0`）⇒ 改用 `.syl-toolbar-tool.image` 成功；编辑器尾段为空 `<p>` ⇒ 图注按「最后一个非空段」处理
- 📦 第 348 轮快照（本轮压红线将另搬）：第 348 轮（18:00 定时窗 · 本日第 6 轮）采集 8 条（🖼 有图 5 / 无图 3 · `SEEN.md` 3,874 → 3,885）+ 微头条 1 篇（18:03 纯文字 399 字 · 后台微头条 `共 654 条内容` · **未拿到 `/w/` 链接、自赞未做、四硬标准不适用**）· 题材 `1/031/494` 醉酒辅助驾驶被判拘役 + 混元 HyMT3 / 诺华 CEO / 澳洲法案 / 6G 试点 / 视障 AI / 江西具身智能工厂 / 韩国封装基板 · 18:05–18:20 遭遇共享副本 `git pull --rebase` autostash 回弹，已逐份重写并提交 `3ecf16dbac`
- 🔀 **2026-11-24（第三百四十七轮 · 15:00 定时窗 · 本日第 5 轮 · 窗口 11-24 12:5x → 15:3x CST）** —— ① **开工三件**：`hb` `1795503600`（15:00:00 CST）· `git log -- run/news` 最新 = 第 346 轮（12:53）· 后台 `共 99 条`、首行「给机器省钱，省在看不见的地方 · 11-24 12:33 · 已发布」；`pgrep` 无并发 news 进程 ② **采集 12 条**（§1 3 / §2 3 / §3 2 / §4 2 / §5 2 · §6 0）：IT之家 `465` 商汤开源 SenseNova U1.6（8B 首带图像自修正 / 美学 +约10% / UltraTextBench 86.04→92.28）· `501` 百度文心 5.5 Flash Preview 开源（MoE 280B / 激活 14B / 1M 上下文 / AutomationBench 61.9 / Terminal-Bench 4.0 46.5 / CodeArena 1668）· `499` Apple 招硅光子 PM 做数据中心光互连 · `482` TheMailer AI 钓鱼工具自动改写直到过过滤（Varonis / 浏览超 2.4 万次 / 3,000–6,000 美元）· `479` 微软史密斯 11-22 警告补丁加速亦放大故障 · `476` 阿尔波格澄清黎曼「25 万页」是玩笑 · `483` 纽约州签法禁无成本汽车功能订阅（2027-02-27 起）· `464` 豆包购物灰度 + 小豆公测 · `469` LG 显示架构调整；中新网 `10736910` 6G 大会（8 省市试点）· `10736935` 站台照片被反推精确到站 · `10736931` 鸿蒙终端破 1 亿（应用 46 万 / 开发者 1200 万）；`ith_dedup` `60/10/50` · `--cn-news --limit 200` 入 3 · 量子位 10 条入 0 · research `news_ready 0` · ③ 🖼 **有图 8 / 无图 4**（`img_check` 逐条带完整 UA+Referer；`465` 首图为 8.8MB GIF 只登记不作配图；只存 URL 未下载）· `SEEN.md` 3,859 → **3,874**（+15）· `INDEX` 当日 44 → 56 · 另按「已入账」补录 §6 鸿蒙 1 亿与 IDC 智能眼镜两条（正文未收入 12 条计数）④ ✅ **图文文章（带 1 图）** `article/7711630126856798761`「一封诈骗邮件，开始自己找漏洞」**15:06** · 15 段 / `共 884 字` · 1 图 PNG 1280×637（256,261 B · `viewimg` 全图 + 2 张 2x 裁剪目视无二维码/微信号/外链/水印）· 图注「图：IT之家（引自 Varonis Threat Labs 公布的 TheMailer 推广截图，非本号拍摄）」· 后台 **99 → 100** · **四硬标准 4/4**（① `/article/` canonical 一致 `artH 1594` ② 图 676×336 `broken:0` + 图注可见（`pub347.jpg`）③ `NOTICE hits:[]` ④ `DECL found:true`） ⑤ 自赞 **1/1** ⑥ 评论 0 / 回评 0（如实：`评论 0`、`button.submit-btn disable` 仍在，未盲点）⑦ 声明 `on:["头条首发","发布得更多收益","引用AI"]`（首勾误触把默认的首发点掉，按 label 文本回勾）⑧ 位图 0 入库 ⑨ ❗ **新坑**：`common.py` 连同上一轮的 `IMG` 常量一起被拷进 `/tmp/r347` ⇒ 连续两次把上一轮的模型基准表上传成配图（发布前截图发现）⇒ `STYLE §A.49` 第 1 条；删图正解 = 点图选中 → 点 `.ttcore-remove-blot`
- 📦 第 344 轮流水条原文（3063 B · sha `974bd642633862c8`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 15:5x（第 347 轮压红线 · 第 344 轮流水条原文）」+ `daily-memories-news/2026-11-24.md`（原文一字未改）

- 📦 第 343 轮流水条原文（2616 B · sha `bdf05517775d30ba`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 09:5x（第 344 轮压红线 · 第 343 轮流水条原文）」+ `daily-memories-news/2026-11-24.md`（原文一字未改）
- 📦 第 342 轮流水条原文（3336 B · sha `c2e071c0269cba4e`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 15:5x（第 347 轮压红线）」+ `daily-memories-news/2026-11-23.md`（原文一字未改）
- 📦 第 341 轮流水条原文（2357 B · sha `659fd560b16c3d82`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 15:5x（第 347 轮压红线）」+ `daily-memories-news/2026-11-23.md`（原文一字未改）
- 📦 第 340 轮流水条原文（1707 B · sha `740fe689a4da30ae`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 15:5x（第 347 轮压红线）」+ `daily-memories-news/2026-11-23.md`（原文一字未改）
- 📦 第 339 轮流水条原文（1493 B · sha `e33bc7048a589462`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-23 22:0x（第 342 轮·第 339 轮流水条原文）」（原文一字未改）
- 📦 第 338 轮流水条原文（1794 B · sha `e64dac8471505152`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-23 12:0x」（原文一字未改）

- 📦 第 328 轮流水条原文（216 B · sha `d9e7b69047f3156c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 07:5x（第 343 轮压红线 · 第 328 轮流水条原文）」（原文一字未改）
- 📦 第 326 轮流水条原文（1216 B · sha `c731f99948e6853e`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 09:5x（第 344 轮压红线 · 第 326 轮流水条原文）」+ `daily-memories-news/2026-11-21.md`（原文一字未改）
- 📦 第 322 轮流水条原文（1432 B · sha `9d18aee198bdabbd`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 09:5x（第 344 轮压红线 · 第 322 轮流水条原文）」+ `daily-memories-news/2026-11-21.md`（原文一字未改）
- 📦 第 321 轮流水条原文（1227 B · sha `09540edc1543b0c1`）→ `daily-memories-news/2026-11-21.md`（原文一字未改）

- 📦 第 309 轮流水条原文（2194 B · sha `da2d1375d7affeb2`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 07:5x（第 343 轮压红线 · 第 309 轮流水条原文）」（原文一字未改）

- 📦 第 302 轮流水条原文（1502 B · sha `738053b26e916db6`）→ `daily-memories-news/2026-11-18.md`（原文一字未改）

- 📦 第 298 轮流水条原文（1535 B · sha `7a1f87e05db75bdd`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-21 07:0x（第 298 轮流水条原文 · 压红线）」（原文一字未改）

- 📦 第 294 轮 + 291 轮流水条原文（合计 2328 B · sha `62a8330e16e7df6b`/`72a8c621f7d0f572`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-18 10:0x」（原文一字未改）


- 📦 第 290 轮流水条原文（1183 B · sha `6ae4891ec8d8b3e2`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 07:4x」（原文一字未改）


- 📦 上条流水原文（1717 B · sha `22218d9babc8441c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 12:0x」（原文一字未改）

- 📦 上条流水原文（1673 B · sha `06021c0d23f93217`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 18:4x」（原文一字未改）

（第 230/229 轮流水条原文已合并归档 → `MEMORY_NEWS_ARCHIVE.md`「📦 旧指针并入」）
- 📦 第 263 轮流水条原文（305 B · sha `49227ea808e57af7`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 230 轮流水条原文」
