# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

- 📦 第 343 轮快照四行原文（2834 B · sha `b0c8952cedba2f82`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 09:5x（第 344 轮压红线 · 第 343 轮快照四行原文）」（原文一字未改）
PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· **第 363 轮已完成**（11-28 09:30 时窗 · 本日第 2 轮 · 采 9 条 + 图文文章 `7713029952563593791` · 112→113 · 4/4 · 自赞 1 · 引流 1 · 回评 0）· 今日引流 2/40 · 回评 0/3 · CDP 9222 正常
- 已完成: 第 361 轮 14 条 + 1 篇（110→111）；第 362 轮 9 条 + 1 篇（111→112）；**第 363 轮 9 条 + 1 篇（`7713029952563593791` · 112→113 · 4/4 · 自赞 1 · 引流 1 · 回评 0）**；`SEEN/INDEX/news/` 已同步
- 当前动作: **第 363 轮**（本日第 2 轮 · 09:30 时窗 · 采集 9 条 + 图文文章 BrainBot + 自赞/引流；回评无新提问）
- 下一步:（第 364 轮 / 12:00 时窗）① 开工三件（`hb` / `git log -- run/news` / 后台 `共 N 条`+首行）+ `pgrep` 查并发；先试 `git pull --rebase --autostash`（当前 0/0）② 发一篇图文文章（带 1 图），优先 §1 模型发布 / §3 治理 / §5 公司 ③ 每轮先 `grep '^IMG' /tmp/rNNN/common.py` 核对配图路径（`§A.49`）；取图复核带完整 UA + Referer ④ 配图水印：量子位「公众号·量子位」、IT之家站标、央视/TIEE 标识、`x-bce-process=…watermark`、图内域名文本均弃用 ⇒ 发布前逐张 `read`（`§A.50/A.51/A.55`）⑤ 自赞判 `like` 用 `classList.contains('like')` ⑥ 引流/回评逐字 `Input.dispatchKeyEvent`，选平和 AI 楼、**含标点 ≤40 字**、单帖只评一次；🚫 **先确认目标文不是本号旧文**（查 `news/toutiao/台账.md` 的文章 id），误评立即删除并如实记；回评走公开页 `.reply-btn` → `.children-input`（`§A.55`）⑦ 发布红线：涉美政坛/军事/伤亡/司法条目**只记不发**（禁令 9）⑧ 四硬标准③的 `NOTICE` 命中可能是正文自述词（如「搬运」「版权」），按 `§A.53` 回溯；视频类优先无 UI 技术示意图 ⑨ **loop 自指雷**：会话里禁止 echo/grep/sed 出循环脚本含触发词的源码行（`§A.54`）⑩ 头条搜索结果链接是 `so.toutiao.com/search/jump?...` 跳转链，不能直接当文章 URL，改用真实 `/article/<id>/`；相关推荐里混有本号旧文，评论前必查台账
- 本轮新增: 9 条（§1 2 / §2 1 / §3 0 / §4 1 / §5 3 / §6 2；`SEEN` 4,028→4,037；有图 7 / 无图 2）
- 阻塞: 无（本轮 loop / CDP / 发布链路正常）。番茄建书 `can_create_serial_book=false` 仍待人工裁断。长期限制不变（通用搜索对具体人名/论文标题不可用 · 知乎/雪球被墙 · 本机无 PIL/tesseract · 央视网正文前端渲染抓不到 ⇒ 走 CDP · 新发文常先「审核中」）。
- ERROR_COUNT:  0
- 🔀 **2026-11-26（第三百五十九轮 · 18:00 定时窗 · 本日第 5 轮 · 窗口 11-26 15:00 → 18:05 CST）** —— ① **开工三件**：`hb` `1795687200`（18:00）· `git log -- run/news` 最新 = 第 358 轮 `6d29db887f` · 后台 `共 108 条`、首行「同一个行业…」15:06 已发布；`pgrep` 无并发 news ② **采集 13 条**（§1 4 / §2 2 / §3 2 / §4 2 / §5 2 / §6 1）：混元 DFly2（Hy4 flash 单项最高 4.2×，`929`）· 商汤 SenseNova-RoboRSI-27B（RoboDojo 34.7 / Preview 10.0 的 3.47 倍，`887`）· Sand.ai MAGI-2（480B/28B 激活 / 1080p 0.5 元每秒 / 30s 约 15 元 / I2V 超 Seedance 2.5 / Elo 998.5→1150.3 / 计划开源；`512916`+爱范儿 `1691445`）· 三星 ISSCC 2027 5XX 层 NAND（`832`）· 微软史密斯警告 AI 加速漏洞发现（`798`）· 黑客借微软商店分发恶意应用（`932`）· 广东词元经济与词元出海（`927`）· 德国消费者中心起诉 OpenAI 退订（`888`）· Anthropic 职场报告 58 家 66 访（爱范儿 `1691748`）· 苹果下架 MiniMax Talkie（`835`）· 纳德拉「量大管饱」（`805`）· Epic 斯威尼称 Claude 误判蒸馏（`822`）· 沃尔沃人形机器人进工厂（`939`）③ 🖼 **有图 12 / 无图 1**（`832` 无正文图；`927`/`512916` 带水印 ⇒ 不作发布配图；只存 URL 未下载）· `SEEN` 3,979→**3,993** · `INDEX` 当日 39→52 · `ith_dedup 60/hit0/new60`（抽查 769/752 在册，去重正常）④ ✅ **图文文章** `article/7712418888985641526`「AI 视频开始按秒卖了：一秒五毛，30 秒一杯奶茶钱」**18:05** · 12 段 / 816 字 · 1 图 1600×1552（197,907 B，Sand.ai 技术报告 MoE 示意图）· **四硬标准 4/4**（canonical `artH 1812` / 图 676×656 broken:0 / `<article>` 内 NOTICE hits:[]、后台无警告 / DECL found:true）· 声明三勾 ⑤ **自赞 1/1** ⑥ **引流 1 条（32 字）**：他号同题文 `7712031290748420659`「一秒五毛是入场券，能不能只重做改坏的那两秒，才是真正省钱的地方。」23→24 mine:true ⇒ 日计 **5/40** · 回评 **0/3**（无新提问，如实记）⑦ 位图 0 入库 ⑧ **新坑**：视频类配图优先无 UI 技术示意图，编辑器整屏截图既杂又可能带敏感画面（弃用含一战画面帧）
- 📦 第 358 轮流水条原文 → `daily-memories-news/2026-11-26.md`「📦 压红线搬出 · 2026-11-28 09:4x」（原文一字未改）
- 📦 第 354/355 轮流水条原文（合计 5996 B）→ `daily-memories-news/2026-11-26.md`「📦 压红线搬出 · 2026-11-26 15:0x」（原文一字未改）
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
- 📦 第 360 轮两条流水条原文（「同窗重试」+ 21:30 定时窗，合计 1,574 B）→ `daily-memories-news/2026-11-26.md`「📦 压红线搬出 · 2026-11-28 07:1x（第 362 轮滚动）」（原文一字未改）
- 🔀 **2026-11-28（第三百六十三轮 · 09:30 时窗 · 本日第 2 轮 · 窗口 11-27 22:36 → 11-28 09:30 CST，补录上轮未入账条目）** —— ① 开工三件：`hb` 1795829400（09:30）· `git log -- run/news` 最新 = 第 362 轮 `71a4d26535` · 后台 `共 112 条`、首行「车里说句话…」07:06 已发布；`pgrep` 无并发 news ② 采集 9 条（§1 2 / §2 1 / §3 0 / §4 1 / §5 3 / §6 2）：陶哲轩哈佛表态「AI 批量证明像核废料」+ 黎曼猜想公开协作（`qbit 513075`）· DLSS 5 神经渲染 RDR2（单次 -31% / 双次 -41%，`775`）· 微软 Copilot 可未经确认改 OneDrive/SharePoint（`790`）· Caltech BrainBot 250 纳米纳米机器人（小鼠递药量约 5 倍，`798`）· 商汤 Token 工厂信通院最高评级（`513346`，厂商稿）· OpenAI 反诉苹果窃密（`780`，司法只记不发）· 联想预装 ChatGPT（`777`）· 一目科技 YIMU xEco（`513101`）· 千里科技印奇智驾聚焦 2–3 家（`753`）③ 🖼 有图 7 / 无图 2（量子位 3 张带水印、`790` 带 IT之家站标、`775` 带 `x-bce-process` ⇒ 只登记不作配图）· `SEEN` 4,028→**4,037** · `INDEX` 当日 9→18 · `ith_dedup 60/hit7/new53`（已核对重覆 3 条：Siri 额度 / 小米澎程 / 和平饭店）④ ✅ 图文文章 `article/7713029952563593791`「250纳米的机器人，试着把药送进大脑」**09:37** · 13 段 / 842 字 · 1 图 1440×1580（1,543,302 B，Caltech 示意图，目视无 watermark）· 四硬标准 4/4（canonical `artH 1918` / 图 676×742 broken:0 complete:true / `articleHits:[]` / DECL found）· 声明三勾 ⑤ 自赞 1/1 ⑥ 引流 1 条（25 字）他号 AI 芯片文 `7712633758188454426`「芯片是地基，模型是楼；地基拼的是产能、软件栈和电。」30→31 mine:true ⇒ 日计 **2/40**；⚠️ 首次误评本号旧文 `7712120224836747819`（评论 0→1）已删除（1→0），未计配额 ⑦ 回评 0/3（粉丝视图最新仍 11-24 白帝燃，无新增）⑧ 位图 0 入库 ⑨ 新坑：相关推荐里混有本号旧文，评论前必查 `台账.md` 文章 id
- 🔀 **2026-11-28（第三百六十二轮 · 07:00 时窗 · 本日首轮 · 窗口 11-27 21:36 → 11-28 07:10 CST）** —— ① 开工三件：`hb` 1795820400（07:00）· `git log -- run/news` 最新 = 第 361 轮 `60e39198e9` · 后台 `共 111 条`、首行「微信把电商大模型开源了…」11-27 21:34 已发布；`pgrep` 无并发 news ② 采集 9 条（§1 4 / §2 0 / §3 0 / §4 1 / §5 1 / §6 3）：research `news_ready` 1（Solve Vision with Code，VBVR-Pro-Bench 500 实例 / 三 Agent 0.923·0.894·0.893 / 高最强视频模型 >0.22，arXiv `2611.34813`）· 众擎开放大小脑 + 5 年 10 亿元生态（Awaken-HI 56.7%→90% / BFM 35kg / 6000 卡 / 万台级，`qbit 513352`）· DeepSeek 网页/App 上线 Token 账单、聊天仍免费（`qbit 513305`）· 未发布 Claude Opus 5.6 生成可交互 PPT（42 分钟 / 约 90 美元，爱范儿 `1695831`）· 韩国学校抢购金属探测器防 AI 作弊（咨询量 +100 倍 / 474 起 +69.9%，`1/033/763`）· 美团王兴称明年 AI 资本开支低于今年（`1/033/748`）· 支付宝车载助手 3.0 接入 80 多家车企、覆盖 1,800 万辆（`1/033/625` + 爱范儿 `1695888`）· 智源物理 AI 圆桌：具身研发优先转向 S0/S1（`qbit 513125`）· 我国 Z 箍缩聚变供热示范堆规划 2031–2035 建设（`1/033/770`）③ 🖼 **有图 7 / 无图 2**（Solve Vision / 美团无图；量子位 3 张带「公众号·量子位」、聚变图带央视/TIEE 标识 ⇒ 只登记不作发布配图；只存 URL 未下载）· `SEEN` 4,019→**4,028** · `INDEX` 当日 +9 ④ ✅ **图文文章** `7712991169810055721`「车里说句话就能交停车费，80多家车企接入了」**07:06** · 11 段 / 890 字 · 1 图 1080×720 PNG（860,837 B，IT之家 `1/033/625` 声纹支付界面）· 后台 **111→112** · **四硬标准 4/4**（canonical 一致 `artH 1557` / 图 676×451 broken:0 complete:true / `<article>` 内 NOTICE hits:[]、后台无警告 / DECL found:true）· 声明三勾 ⑤ **自赞 1/1** ⑥ **引流 1 条（23 字）**：大河财立方同题文 `7712844127817187876` 评论「车能替你交停车费，拼的不是模型，是停车场接口。」· 评论 0→1 · `mine:true` ⇒ 日计 **1/40** · 回评 **0/3**（评论管理首屏无新增提问，如实记）⑦ 位图 0 入库 ⑧ **新坑**：头条搜索结果是 `so.toutiao.com/search/jump?...` 跳转链，不能直接当文章 URL，需用真实 `/article/<id>/`
- 🔀 **2026-11-27（第三百六十一轮 · 21:30 时窗 · 本日首轮）** —— ① 开工三件：`hb` 21:30 · `git log -- run/news` 最新 = 第 360 轮 `5b6abde2d8` · 后台 `共 110 条`、首行「能钻1000℃火场…」11-26 21:36 已发布（展现 407/阅读 0/点赞 1/评论 0）；`pgrep` 无并发 news ② 采集 14 条（§1 6 / §2 1 / §3 2 / §4 1 / §5 2 / §6 2）：谷歌第 10 代 TPU 512GB HBM5（2029 量产，`1/033/624`）· 微信开源 WeMM-Ecom（35B-A3B 电商榜 74.35，`1/033/649`）· 混元 Hy3D 3.6（`qbit 513155`）· 蚂蚁灵波 LingBot-Map 2.0/Navi（ATE 31.12→4.72 米，`qbit 513227`）· 20 AI Agents 优化 Quickwit（约 350 次实验 / 热查询 40.5→27.9 秒，`qbit 513163`）· coding agent over-edit（arXiv 2611.34875，research `news_ready 1`）· 三井购物公园 App 311.9 万会员信息外泄（`568`）· 十一部门分布式数字身份规定（`733`）· 数字素养 64.69% / AI 素养 47.46%（`732`）· 李小龙 AI 复活讨论（`612`）· 豆包八成头部电视厂商（`718`）· 韩国要三星做 Jetson Thor 竞品（`619`）· 智元 G2 承担喇叭 BOX 并线（`744`）· 小米汽车世界模型 2.0（`614`）③ 🖼 有图 13 / 无图 1（research 论文图无稳定直链）· `SEEN` 4,005→4,019 · `INDEX` 当日 14 · `ith_dedup 60/hit0/new60` ④ ✅ 图文文章 `7712843774648484371`「微信把电商大模型开源了：28 项电商基准平均 74.35 分」21:34 · 9 段 / 838 字 · 1 图 1418×818（258,158 B，IT之家榜单图）· 四硬标准 4/4（artH 1456 / 图 676×390 broken:0 / articleHits:[] / DECL found）· 声明三勾 ⑤ 自赞 1/1 ⑥ 引流 1 条（31 字）：他号《AI 重构〈史记〉》文 `7711624540161360419` 评论「地铁图把矛盾摆出来了，哪些是笔误、哪些是故意留白，还得人来判。」98→99 mine:true ⇒ 日计 1/40 · 回评 0/3（无新提问）⑦ 位图 0 入库 ⑧ **今日 5 次定时唤醒均 `opencode returned (exit 1)`**（4~5 秒即退）⇒ 仅本轮成功；loop 多次报 pull 失败但当前仓库同步正常 ⇒ 记 infra，待查根因 ⑨ 新坑：量子位图几乎全量带公众号水印 ⇒ 配图转用 IT之家正文技术图
- 📦 第 356 轮流水条原文（2980 B）→ `daily-memories-news/2026-11-26.md`「📦 压红线搬出 · 2026-11-26 21:5x（第 360 轮同窗重试）」（原文一字未改）
- 📦 第 355 轮流水条原文（1521 B · sha `28ee19664a86f08e`）→ `daily-memories-news/2026-11-26.md`「📦 压红线搬出 · 2026-11-27 21:5x」（原文一字未改）
- 📦 第 351 轮流水条原文（2498 B）→ `daily-memories-news/2026-11-25.md`（原文一字未改）
- 📦 第 350 轮流水条原文（2422 B · sha `c7d8e0ada82fa1c2`）→ `daily-memories-news/2026-11-24.md`「📦 第 350 轮流水条原文」（原文一字未改）
- 📦 第 349 轮流水条原文（3,038 B · sha `c12cd1b5ce6268a1`）→ `daily-memories-news/2026-11-24.md`「📦 压红线搬出 · 2026-11-26 09:5x」（原文一字未改）
- 📦 第 348 轮快照（本轮压红线将另搬）：第 348 轮（18:00 定时窗 · 本日第 6 轮）采集 8 条（🖼 有图 5 / 无图 3 · `SEEN.md` 3,874 → 3,885）+ 微头条 1 篇（18:03 纯文字 399 字 · 后台微头条 `共 654 条内容` · **未拿到 `/w/` 链接、自赞未做、四硬标准不适用**）· 题材 `1/031/494` 醉酒辅助驾驶被判拘役 + 混元 HyMT3 / 诺华 CEO / 澳洲法案 / 6G 试点 / 视障 AI / 江西具身智能工厂 / 韩国封装基板 · 18:05–18:20 遭遇共享副本 `git pull --rebase` autostash 回弹，已逐份重写并提交 `3ecf16dbac`
- 📦 第 347 轮流水条原文（2,917 B · sha `92bbc5f7b74078cf`）→ `daily-memories-news/2026-11-24.md`「📦 压红线搬出 · 2026-11-26 09:5x」（原文一字未改）
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
