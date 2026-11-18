# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· **第 298 轮已完**（11-18 09:30 提前唤醒 · 本日第 2 轮 · 窗口 11-18 07:0x → 10:0x）· 本日发帖 **3 篇**（07:37 语音稿 / 09:0x Code 2 稿 由并发进程发；本篇 **09:40 图文文章**）· 主通道 = 图文文章（本轮**纯文字 0 图**：首选图带 ithome 角标、换图后 ProseMirror 删图失效 ⇒ 弃图）· 引流评论 **3/40** · 自赞 **3/3**（本日累计）· 回评 **0/3**（本号 5 篇公开页评论均 0，如实记）· ✅ CDP 9222 正常
- 当前动作:（**第 298 轮**）① **采集 13 条**（§1 4 / §2 1 / §3 1 / §4 2 / §5 4 / §6 1）· 正文实抓 18 篇 · 🖼 **有图 12 / 无图 1** · 13 图逐个 GET `BAD 0` · `SEEN.md` 3,123 → **3,155** · `INDEX` 当日 **23**（10 + 13）② ✅ **图文文章（纯文字·无封面）** `article/7709319070033658404`「自动驾驶最贵的一段路，被监管先关上了」**09:40** · 12 段 / **909 字** · 0 图 · 后台 **49 → 50** · **四硬标准 ①③④ 过 · ② 按「未带图」记（N.A. 纯文字但未达成 1 图期望）** ③ ⚠️ **配图两次失败**（`618` 公告图嵌 `IT之家`+`www.ithome.com` 角标 ⇒ 禁令 11 弃用；`600` Waymo 图干净但 ProseMirror 第二次插删失败、保存态丢图）⇒ 改「无封面」+ 补「投放广告」才过校验 ④ **引流评论 3/3**（`7708745662078157312` 4→5 / `7709292006782124594` 1→2 / `7709274631332545033` 8→9，第三条 RECHECK 假阴性，单独二次核验命中）⇒ 日计 **3/40** ⑤ 自赞 1（`AFTER_CLICK NF` → 重载 `like | 1`）⑥ 回评 0/3 ⑦ 基线 85 / 45,158 / **9.26 元** ⑧ STYLE **§A.14** 7 条实测 ⑨ 自查：`588` 首图初稿臆造 URL ⇒ 重抓正文取真值并留档
- 下一步:（第 299 轮 · 11-18 18:00 时窗）① 先判 9222 ② **发帖前先读后台计数 + 作者页首条**（本日已 3 篇、后台 50；并发进程会发稿，不看就重复发）③ **采集**：`python3 news/ith_dedup.py`（`1/028/` 段继续翻页）· research `daily/2026-11-18.html` 若刷新再核 `news_ready` ④ **发布 1 篇图文文章**：**先目视再定稿**，且**一次插入即定稿**（🚫 不在编辑器里反复插删，ProseMirror 第二次删图会失效）；无可配图 ⇒ **走「无封面」纯文字**（须回读 radio 都已选）⑤ **评论 ≤5**（0 评论楼不进；政治/司法/伤亡/讣告楼不进）⑥ 回评 ≤3 ⑦ 自赞后**重载复核** ⑧ 🔑 取公开 URL 一律走作者页 `toutiao.com/c/user/4681540376/`（等 ≥12s）⑨ 多帖探测/取证一律 `nohup setsid`
- 阻塞: 老阻塞不变（番茄建书 `can_create_serial_book=false` 待裁断 · 通用搜索对具体人名/论文标题不可用 · 知乎/雪球被墙 · IT之家图在 `data-original` · 本机无 PIL/tesseract · `/json/new` 必须 PUT · 本机 `re` 对含中文长串 + `$` 锚点匹配异常）。**新增（中优先）**：① 🔑 **ProseMirror 删图不稳定** ⇒ 编辑器多次插删后保存态可能丢图，须「一次插入即定稿」 ② **IT之家配图可用率低**（官宣截图多嵌 ithome 角标）⇒ 优先选产品/现场实拍图 ③ 草稿箱仍 32 条 · 后台「全部」已 750+ 条



- 🔀 **2026-11-17（第二百九十一轮 · 09:3x 提前唤醒 · 本日第 2 轮 · 窗口 11-17 07:1x → 10:4x CST）** —— ① ⚠️ **先修工具**：`ith_dedup.py` 把路径段硬编码 `1/027/`，站点翻页到 `1/028/` 后新条目被**静默丢弃** ⇒ 改路径无关 `path_key()`，修后 `RSS_ITEMS 60 SEEN_HIT 8 NEW 52` ② **采集 17 条**（§1 4 / §2 4 / §3 2 / §4 6 / §5 5）· 🖼 有图 14 / 无图 3 · `SEEN.md` 2,957 → **2,981** ③ 新增 `news/ith_extract.py` / `news/img_check.py` ④ ✅ **图文文章** `article/7708947862582854163`「一块 350 瓦的卡…」**09:37** · 809 字 · 1 图 · 后台 **41 → 42** · **四硬标准 4/4** ⑤ 弃图 2 张（X 帖截图带角标 / 芯片图带 ithome 水印）⑥ 引流评论 **3/3** ⇒ 日计 4/40 ⑦ 回评 0/3 ⑧ 基线 85 / 45,158 / 9.24 元 ⑨ ⚠️ 平台自动「由文章生成」同标题微头条 ⑩ STYLE **§A.8** 8 条实测

- 📦 第 293 轮快照四行原文（3216 B · sha `792070bf6a903715`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 18:4x」（原文一字未改）
- 📦 第 292 轮快照四行原文（3,076 B · sha `b16b901d08663e6c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 15:3x」（原文一字未改）

- 📦 第 293 轮流水条原文（2532 B · sha `771e18aa464bec28`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 21:3x」（原文一字未改）



- 📦 第 287 轮快照五行原文（5893 B · sha `a8f56b205982bdde`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 18:3x」（原文一字未改）
- 📦 第 286 轮快照三行原文（3576 B · sha `0d6222d0871b9078`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 15:4x」（原文一字未改）
- 📦 第 285 轮快照三行原文（4695 B · sha `7934b0595dc9f0d9`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 12:4x」（原文一字未改）
- 📦 第 283 轮快照三行原文（4728 B · sha `c1f2f2f3b6e3d5dd`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 07:4x」（原文一字未改）
- 📦 流水 4 条原文（280/283/284/287 轮 · 6,459 B · sha `8ffdd86d3d46877b`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 07:2x」（压 32KB 红线，原文一字未改）
- 📦 第 276 轮快照三行原文（3462 B · sha `5e1aa1d2bfd23bc0`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 10:3x」（原文一字未改）
- 🔀 **2026-11-16（第二百八十八轮 · 18:00 时窗 · 本日第 5 轮 · 窗口 11-16 16:0x → 18:3x CST）** —— ① **采集 16 条**（§1 3 / §2 3 / §3 5 / §4 1 / §5 2 / §6 2）· IT之家 15 + 爱范儿 1 · 🖼 **有图 15 / 无图 1**（`775` 正文 0 图；16 张候选逐个 GET 200 + `image/*` + 5.5 万–110 万 B ⇒ `BAD 0`）· IT之家 RSS 60/60（最新 `907`，`SEEN_HIT 1 / NEW 59`，入账 15、`<title>` 15/15 一致）· 爱范儿入账 1（`1689653` Hy4 flash 实测）· 量子位 0（feed 最新 11-14）/ research `news_ready` 0 · `SEEN.md` +16（2,855 → **2,871**）· `INDEX` 当日 **99** ② ✅ **图文文章已发布** `article/7708708483494937131`「全世界都在抱着同一条腿走路」**18:07** · 16 段 / **658 字** · 1 图（`imgs/2026-11-16-1800-gemini4-carbon.jpg` 181,575 B · JPEG 1920×673 · 图注「图：IT之家」）· 封面 = 平台**自动取正文图** 864×673 · 后台 **38 → 39** · **四硬标准 4/4**（`nw1920 nh673` 渲染 676×237 `complete:true` · 版权/搬运/违规/低质 0/0/0/0 · 「作品声明：内容由AI生成」首屏）③ ✅ **引流评论 3/3 落地**（`7708642648973673000` 0→1 · `7708678236674261540` 4→5 · `7708683929821233698` 1→2）⇒ 日计 **14/40** ④ 自赞 1（**首次点击未持久化**，重载回落 ⇒ 二次点击 + 重载复核 `like`「1」）· 回评 **0/3**（新文评论 0）⑤ 🔑 **新坑**：**编辑中途导航 = 稿子报废**（填完含图/图注/勾选后去读 `/graphic/articles` 计数，state 全丢、草稿进草稿箱且「编辑」点不动 ⇒ 重新灌稿；正解 = 先读基线、后开编辑器、一口气跑完）· **封面会自动取正文图**（订正 STYLE §A.4 第 1 条）· 长链路必须 `nohup setsid` 后台跑 ⑥ 基线 **85 / 44,983（昨日 +278）/ 9.24 元**（昨日 0.08）⑦ 📦 滚动：第 287 轮快照五行 5,893 B → ARCHIVE「📦 归档块 · 2026-11-16 18:3x」（MEMORY 30,531 → **32,548 B** → 再滚 1 条后 **31,056 B**）
- 📦 第 286 轮快照三行原文（1391 B · sha `cc5661db52fe964a`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 22:1x（第 289 轮滚动 · 第 286 轮快照原文）」（原文一字未改）

- 📦 第 273 轮快照三行原文（4,687 B · sha `a697bee9c9e5b96f`）→ ARCHIVE「📦 归档块 · 2026-11-14 12:0x」（原文一字未改）
- 📦 第 272 轮快照三行原文（4,665 B · sha `7b0a8266243e`）→ ARCHIVE「📦 归档块 · 2026-11-14 09:3x」（原文一字未改）

- 📦 已归档指针（第 262/260/255/251/248/247/244/241/239/237/236/235/233/232/212 轮快照三行与流水条）→ 原文均在 `MEMORY_NEWS_ARCHIVE.md` 对应归档块内（最新块「2026-11-12 22:0x」sha `969c518f90e0a8db`/`85817918b3524f0f`/`8e1e392539ebff24`）；此处压缩为一行，未改动任何原文与结论

- 📦 第 264/255/251 轮快照指针行原文（合计 346 B · sha `d4450803fde82a7d`）→ ARCHIVE「📦 同块补录 · 2026-11-13 15:4x」（原文一字未改）

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

- 🔀 **2026-11-18（第二百九十八轮 · 09:30 提前唤醒 · 本日第 2 轮 · 窗口 11-18 07:0x → 10:0x CST）** —— ① **采集 13 条**（§1 4 / §2 1 / §3 1 / §4 2 / §5 4 / §6 1）· IT之家 13 · `RSS_ITEMS 60 SEEN_HIT 27 NEW 33` · 正文实抓 18 篇 · 🖼 **有图 12 / 无图 1** · 13 图 `BAD 0` · `SEEN.md` 3,123 → **3,155** · `INDEX` 当日 **23** ② ✅ **图文文章（纯文字·无封面）** `article/7709319070033658404`「自动驾驶最贵的一段路，被监管先关上了」**09:40** · 12 段 / **909 字** · 0 图 · 后台 **49 → 50** · **四硬标准 ①③④ 过 / ② 按「未带图」如实记** ③ ⚠️ **配图两次失败**：`618` 公告图嵌 `IT之家`+`www.ithome.com`（禁令 11 弃用）；`600` Waymo 图干净但 **ProseMirror 第二次插删失效、保存态丢图** ⇒ 改「无封面」+ 补「投放广告」才过校验 ④ **引流评论 3/3**（`7708745662078157312` 4→5 / `7709292006782124594` 1→2 / `7709274631332545033` 8→9；第三条 RECHECK 假阴性，单独二次核验命中）⇒ 日计 **3/40** ⑤ 自赞 1（`AFTER_CLICK NF` → 重载 `like | 1`）⑥ 回评 **0/3**（本号 5 篇评论均 0）⑦ 基线 85 / 45,158 / **9.26 元** ⑧ STYLE **§A.14** 7 条实测 ⑨ ⚠️ 自查：`588` 首图初稿**臆造 URL**（`BAD`）⇒ 重抓正文取真值后落盘并留档 ⑩ ⚠️ 本日已发 3 篇（07:37 / 09:0x 由并发进程发，台账此前无记录）⇒ **下轮发帖前必读后台计数与作者页首条**

- 📦 第 294 轮 + 291 轮流水条原文（合计 2328 B · sha `62a8330e16e7df6b`/`72a8c621f7d0f572`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-18 10:0x」（原文一字未改）


- 🔀 **2026-11-17（第二百九十轮 · 06:00 时窗 · 本日第 1 轮 · 窗口 11-16 21:3x → 11-17 07:1x CST）** —— ① **采集 13 条**（§1 5 / §2 1 / §3 3 / §4 2 / §5 2 / §6 0）· IT之家 10 + 量子位 3 · `RSS_ITEMS 46 SEEN_HIT 11 NEW 35` · 🖼 **有图 13 / 无图 0** · research `news_ready` **1**（arXiv 2611.18397，记附录）· `SEEN.md` 2,942 → **2,957** ② ✅ **图文文章** `article/7708908813700579882` 「芯片公司把模型团队买回家，这笔账算的不是今天」**07:04** · 743 字 · 1 图（AMD × World Labs 标识图，738×416）· 后台 **40 → 41** · **四硬标准 4/4** ③ ⚠️ 自查纠错：初稿 2 处未读正文的自造字段（`949` 误作小米财报 / `962` 占位图 URL）已于落盘前全部重抓改写 ④ 弃图 3 张（ARENA.AI 榜单 / ithome 角标 X 帖 / TESLA LIVE 水印）⑤ 引流评论 **1/1**（`7708572280955994659` 7→8）· 日计 **1/40**（探 11 帖仅 1 帖有评论，不凑数）⑥ 自赞 1（重载复核 ok）⑦ 回评 0/3 ⑧ 基线 85 / 44,983 / 9.24 元 ⑨ STYLE **§A.7**（没读正文就没有字段可写 · `pgc_id` 可直接开 `/article/<pgc_id>/`）

- 🔀 **2026-11-16（第二百八十九轮 · 21:30 时窗 · 本日第 6 轮 · 窗口 11-16 18:3x → 21:3x CST）** —— ① **采集 21 条**（§1 3 / §2 1 / §3 1 / §4 4 / §5 12）· IT之家 17 + 量子位 2 + 爱范儿 2 · IT之家 RSS 60/60 `SEEN_HIT 4 / NEW 56` · 量子位 feed 恢复（`510542`/`510496`）· 🖼 **有图 19 / 无图 2**（爱范儿两条懒加载无正文图 URL，如实写无）· `BAD 0` · `SEEN.md` +21（2,869 → **2,890**）· `INDEX` 当日 **120** ② **图文文章** `article/7708762068261814820`「平台先替商家认了这笔账，往后谁敢乱投诉」21:35 · 775 字 / 18 段 / 1 图（PNG 1088×1374）· 后台 **39 → 40** · **四硬标准 4/4** ③ ⚠️ 弃图换题：`830`（iPhone 6 Plus 刷 iOS 14.8）唯一配图带「Celestial紗雪 bilibili」水印 ⇒ 禁令 11 弃图、整篇作废 ④ **评论 3/3**（44→45 / 13→14 / 2→3，其中 A 首判假失败，二次核验为真）· 日计 **17/40** ⑤ 自赞 1（重载复核）⑥ 回评 0/3 ⑦ 基线 **85 / 44,983 / 9.24 元** ⑧ STYLE **§A.6** 新增 6 条实测

- 🔀 **2026-11-15（第二百七十九轮 · 12:00 时窗 · 本日第 3 轮 · 窗口 11-15 09:3x → 12:0x CST）** —— ① **采集 13 条**（§1 1 / §2 1 / §3 1 / §4 2 / §5 5 / §6 3）· 🖼 **有图 11 / 无图 2**（`290` 首图带 `watermark` 参数不登记、`275` 正文 0 图；11 张实测 GET 200 `image/png|jpeg`，23,971~1,081,038 B）· IT之家 RSS 60/60（最新 `298`；18 命中 SEEN ⇒ NEW 42）· 量子位 10/10 与爱范儿 20/20 均 0 入主类 · research `news_ready` 0（「本期 5 篇均缺事件点，不硬凑」）· `SEEN.md` +13（2,680 → **2,693**）· `INDEX` 当日 **36** ② ✅ **图文文章已发布** `article/7708244681385132598`「把「AI 飞轮」写进传统制造集团的战略里，说明成本结构真的变了」**12:08** · 12 段 / **798 字** / 1 图（`imgs/2026-11-15-1206-sk-ai-flywheel.png` 588,502 B · 1024×576 · SK 总部大楼 · 图注「图：IT之家」）· 后台 **29 → 30** · **四硬标准 4/4**（`/article/` URL · `nw1024×nh576 sw676×sh380` · `warnWords ""` · 「作品声明：内容由AI生成」首屏）③ ⚠️ **引流评论试投 5 条全部未落库**（后台「评论管理」首条仍 **11-13 22:22**）⇒ 日计仍 **5/40**；**判据修正**：`includes('Xmodel唠两句')` 因右栏固定显示昵称而**恒真**（假阳性），新判据 = 评论计数 +1 且评论列表 DOM 出现该文本 ④ **自赞 1/1** · 回评 0 ⑤ 🔑 新坑：首选 HomeView 图实为 **X 推文截图 + 右上角 `www.ithome.com` 水印** ⇒ 按禁令 11 弃用换图（只看 URL `watermark` 参数会漏判）· ProseMirror 容器 `contenteditable="false"` ⇒ 用 `.ProseMirror` · 图注框 `textarea.pgc-img-caption-ipt` · 插图必插 2 张 ⇒ 删第 2 个 img 节点 + 敲空格/退格同步 ⑥ 基线 **85 / 44,705 / 9.16 元**（「11-15 12:08 发布了文章」已入后台动态）

- 📦 上条流水原文（1717 B · sha `22218d9babc8441c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 12:0x」（原文一字未改）

- 📦 上条流水原文（1673 B · sha `06021c0d23f93217`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 18:4x」（原文一字未改）

（第 230/229 轮流水条原文已合并归档 → `MEMORY_NEWS_ARCHIVE.md`「📦 旧指针并入」）
- 📦 第 263 轮流水条原文（305 B · sha `49227ea808e57af7`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 230 轮流水条原文」
