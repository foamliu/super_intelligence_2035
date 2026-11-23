# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· **第 343 轮已完**（11-24 07:00 定时窗 · 本日第 1 轮）· 本轮采集 **13 条**（§1 1 / §2 1 / §3 3 / §4 4 / §5 4 / §6 1 · 🖼 有图 9 / 无图 4 · `SEEN.md` 3,810 → **3,825**）· 本日发文 **1 篇**（**07:03 `7711506337942782483`「AI替数学家想出来的法子，得先过一道数学的关」**）· 后台 **95 → 96** · 主通道 = 图文文章（带 1 图，不变）· 引流评论 0/40 · 回评 0/3（如实：`评论` 键仍 `submit-btn disable`，textarea 空）· 自赞 **1/1**（`detail-like like | 1`）· 新篇四硬标准 **4/4**（①✅ `/article/7711506337942782483/` ②✅ 图 1200×630 渲染 676×355 `broken:0` + 图注可见 ③✅ `NOTICE []` ④✅ `DECL found:true`「作品声明：内容由AI生成」）· 上轮 342 轮无障碍 · CDP 9222 正常
- 下一步:（第 344 轮 · 下一唤醒）① 开工三件（`hb` / `git log -- run/news` / 后台 `共 N 条` + 首行）+ `pgrep` 查并发；先复核 07:03 那篇公开页 `DECL` / 图 / `NOTICE` 是否仍在（若变 ⇒ 按 `STYLE §A.43` 第 2 条用「修改」补勾，**只改一次**）② 采集按常规（`ith_dedup --json` · `--cn-news --limit 200` · 量子位 · research `news_ready`），⚠️ 取图复核必须带**完整 UA + Referer**（仅 `Mozilla/5.0` 会 403，`STYLE §A.45` 第 1 条）③ 只按 RSS 摘要入账的条目一律写 `🖼 图片：无`，别补抓 ④ 发布仍走图文文章（带 1 图）：`s0_nav` 必读 `共 0 字` → 填 → 图 → 注 → 「引用AI」按可见文本点 + `chkdecl` 回读 → 预览 → 确认**只点一次** → **id 从列表 `.article-card` 的 18/19 位数字取**（`getid.py` 的 `a[href*=item]` 对新稿不可靠，`STYLE §A.45` 第 2 条）→ 自赞前显式 `Page.navigate` ⑤ 优先选题（已入账、可扩写）：`1/031/204` 三上真司 vs 金亨泰（AI 与手艺，话题度高）· `1/031/228` 星芒「手机只是开始」· `10736712` 智能体 AI 手机出海（Counterpoint 281% CAGR）
- 阻塞: **无硬阻塞**。**仍需人工裁断（非本轮新增）**：① 头条 Web 端评论提交键对该账号恒 `disable`（本轮复测 `CMT {btn:"submit-btn disable"}`、`div.comment-textarea` placeholder「说点什么吧...」为空）⇒ 引流评论 / 回评全部暂停（本轮如实 0/40、0/3）② 番茄建书 `can_create_serial_book=false`。其余长期限制不变（通用搜索对具体人名/论文标题不可用 · 知乎/雪球被墙 · 本机无 PIL/tesseract · `SEEN.md` 双口径记数 · 央视网正文前端渲染抓不到 · 新发文常先「审核中」· 新稿 id 需等转「已发布」才出现在列表 DOM · 同一时窗可能有并发 news 进程）。

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
- 🔀 **2026-11-24（第三百四十三轮 · 07:00 定时窗 · 本日第 1 轮 · 窗口 11-23 21:45 → 11-24 07:4x CST）** —— ① **开工三件**：`hb` `1795474800`（07:00:00 CST）· `git log -- run/news` 最新 = 第 342 轮 · 后台 `共 95 条`、首行「一个会说话的毛绒兔子… · 11-23 21:34 · 已发布」；无并发 news 进程 ② **采集 13 条**（§1 1 / §2 1 / §3 3 / §4 4 / §5 4 / §6 1）：IT之家 `232` 谷歌 DeepMind×Quantum AI 用 Gemini 4 多智能体+Lean 形式化验证优化量子算法（聚变算力成本 -11.8 倍 · 纠错量子比特 5,650→4,338 · 光敏分子 -8 倍 · P450 2.5 倍 481→333 · Grover 2.57 倍 · arcsin 最高 290 倍）· 联合国 `1143248` 独立科学小组《人工智能能力建设》简报（Latam-GPT 55 万美元 · 1000+ 语言 · 坦桑尼亚糖网筛查复诊近两倍 · 布里奇敦峰会）· `231` 三星首款 1100Hz 显示器 · `205` 丹麦 2027 校园手机禁令 · 央视网 `ARTIN3bq…` 高标准数字园区 91 家 · `204` 三上真司「希望 AI 彻底消失」vs 金亨泰 · 中新网 `10736712` 智能体 AI 手机出海（Counterpoint CAGR 281%）· `094` 岚图泰山 896 线激光雷达 · `088` 阿维塔四轮爆胎直播 · `218` 英伟达恢复黄仁勋 CEO · `228` 星芒「手机只是开始」· `182` 鸿蒙壹亿纪念章 · `165` 摩尔线程回购 5–10 亿元 · `243` NASA 月表核裂变电源 LR-1；`ith_dedup` `60/13/47` · `--cn-news --limit 200` 164 条入 1 · 量子位 10 条均已在册 ⇒ 0 · research `news_ready 0` · 🖼 **有图 9 / 无图 4**（9 张 `206 image/*` 带**完整 UA + Referer** 复核；只存 URL 未下载）· `SEEN.md` 3,810 → **3,825**（+15）· `INDEX` 新建当日行 13 ③ ✅ **图文文章（带 1 图）** `article/7711506337942782483`「AI替数学家想出来的法子，得先过一道数学的关」**07:03** · 15 段 / `共 795 字` · 1 图 PNG 1200×630（495,023 B · 发布前 `viewimg` 目视干净）· 图注「图：IT之家（谷歌 DeepMind 研究博客题图，非本号拍摄）」· 后台 **95 → 96** · **四硬标准 4/4**（① `/article/` URL ② 图 676×355 broken:0 + 图注可见 ③ `NOTICE []` ④ `DECL found:true`）④ 自赞 **1/1** ⑤ 评论 0 / 回评 0（如实：`button.submit-btn disable`、`div.comment-textarea` 为空）⑥ 新坑 → `STYLE §A.45`：仅 `-A Mozilla/5.0` 取图 403（需完整 UA+Referer）/ 新稿 id 在 `getid.py` 的 `a[href*=item]` 里取不到，需从 `.article-card` 的 18–19 位数字取 ⑦ 位图 0 入库（`git check-ignore` 命中 `run/**/*.png`）

- 🔀 **2026-11-23（第三百四十二轮 · 21:30 定时窗 · 本日第 7 轮 · 窗口 11-23 18:50 → 21:45 CST）** —— ① **开工三件**：`hb` `1795440600`（21:30:00 CST）· `git log -- run/news` 最新 = 第 341 轮 · 后台 `共 94 条内容`、首行「936个AI科学家… 11-23 18:08 已发布 首发」；无并发 news 进程 ② ✅ **上轮阻塞解除**：公开页 `article/7711306186800251446/` → `DECL {found:true}`「作品声明：内容由AI生成」+ `IMGS {broken:0, 2228×394→676×120}` + `NOTICE []` + `P1 {artH:1326}` ⇒ **AI-DECL-341 解除、4/4**（18:1x 的「修改」补勾约 3 小时后公开页生效） ③ **采集 15 条**（§1 1 / §2 2 / §4 4 / §5 7 / §6 1 · §3 0）：IT之家 `203` 155 家组织要求亚马逊/eBay 停售 AI 玩具（PIRG：AI 兔子教孩子找漂白剂 · 仅亚马逊美国站超 50 款在售）· `188` CrowdStrike 439 亿美元全股票收购 Zscaler · `164` Meta 路易斯安那最大 AI 数据中心（92.9 万平方米 · 居民「日落没了」）· `196` 华为×澳门电讯 Wi-Fi 感知·识别家庭成员活动 · `160` 联想外骨骼 6999 元 · `190` 马斯克「咖啡师也能建数据中心」· `194` Docker 新徽标「为智能体而造」· `942` 荣耀 YOYO·豆包助手曝光 · `972` 德国车企劳资（奔驰 1.9% / 宝马 3.5%）· `200` Arm CEO 续约至 2033 · `201` 无翼飞车首飞 · `189`+`092` 荣耀李健谈子品牌与星芒 · `985` Omdia 非洲手机 2026Q3 -40%；量子位 `512195` 无界方舟 Edge0-145B（1450 亿参数 · 12GB 显存 · 80+ token/s · T-Bench 2.1 86.5 · 客户超 11 万家）；中新网 `10736644` 香港具身智能峰会 · `ith_dedup` `60/3/57` · `--cn-news` 175 条入 1 · 量子位 10 条入 1 · research `news_ready 0` · 🖼 **有图 12 / 无图 3** · `SEEN.md` 3,790 → **3,810**（+20）· `INDEX` 当日累计 **44** ④ ✅ **图文文章（带 1 图）** `article/7711359550640652843`「一个会说话的毛绒兔子，教孩子去找漂白剂」**21:34** · 21 段 / `共 1194 字`（正文汉字 1,060）· 1 图 JPEG 1444×962（188,799 B · 发布前 `viewimg` 目视无二维码/微信号/水印）· 图注「图：IT之家（AI 儿童玩具示意图；报道提及的 Alilo Smart AI Bunny 等产品，非本号拍摄）」· 后台 **94 → 95** · **四硬标准 4/4**（`/article/` URL · 图 676×450 broken:0 · `NOTICE []` · `DECL found:true`） ⑤ 🔑 **声明勾选正判据**（`STYLE §A.44` 第 4 条）：读每个 checkbox 的 `closest(label).innerText` → `on:[头条首发, 发布得更多收益, 引用AI]`，「三图」不在列 ⇒ §A.43 的假勾坑未复发 ⑥ 新坑 3 条（`STYLE §A.44` 第 1–3 条）：`fetch.py` 对 IT之家 `985` 漏正文（`chars=489`、`text` 空）⇒ `id="paragraph"` 兜底取到 901 字 / `s6` 的 `PUBID` 恒 `NONE`（id 从列表 `a[href*=item]` 取）/ 自赞前媒体页签已被导航过 ⇒ 必须显式 `Page.navigate`（首次 `RE1 NO` 点空） ⑦ 自赞 **1/1**（`detail-like like | 1`）· 评论 0 / 回评 0（如实：`CMT {submit-btn disable, op 0.3}`）· 位图 0 入库 · 📦 压红线：第 341 轮快照 + 「当前动作」两行 2,208 B → ARCHIVE「22:0x」，再把第 339 轮流水条 1,493 B 与旧阻塞行 615 B 搬出 ⇒ MEMORY 31,555 → **28.5KB** 线内
- 🔀 **2026-11-23（第三百四十一轮 · 18:00 定时窗 · 本日第 6 轮 · 窗口 11-23 15:00 → 18:50 CST）** —— ① **开工三件**：`hb` `1795428000`（18:00:00 CST）· `git log` 最新 15:3x（第 340 轮）· 后台 `93`、首行 15:04「审核中」② ✅ **上轮阻塞自愈**：`s0_nav` 读到 15:04 那篇转「已发布」⇒ 公开页 `DECL found:true`「作品声明：内容由AI生成」+ 图 864×596 `broken:0` + `NOTICE {hits:[]}` ⇒ **AI-DECL-340 解除、4/4**（印证「预览页不渲染声明」）③ **采集 6 条**（§1 1 / §3 2 / §4 3）· `ith_dedup` `60/2/58`，实抓正文 3 篇入 3（`091`/`090`/`049`）；`921`/`917`/`935`/`954`/`912` **实返 404**（首页最新 `092`）⇒ 条目不存在；`--cn-news` 188 条入 2（`10736564` AI 仿冒名人带货 · `10736567` AI 创作者计税；央视网稿仍只剩「正在加载」）；量子位 8 条入 1（`512004`）；research `news_ready 0` · 🖼 **有图 4 / 无图 2** · `SEEN.md` 3,781 → **3,790** ④ **发布** `article/7711306186800251446`「936个AI科学家，办了一本自己的期刊」**18:08** · 13 段 `共 825 字` · 1 图 PNG 2228×654（176,635 B，**无 x-bce/watermark 参数**，`viewimg` 目视干净）· 后台 **93 → 94** ⑤ 🔑 **新坑（`STYLE §A.43`）**：发布页 `input[value="3"]` 有两个（封面「三图」+ 声明「引用AI」）⇒ `setai.py` 点下去「ck:true」实际勾的**是「三图」**，公开页 `DECL found:false` 才发现；正解 = 按可见文本「引用AI」（`span.byte-checkbox-inner-text`）真实点击 + 回读 `checked` + 截图见红勾 ⑥ **补改一次**：台账「修改」是普通 `span`，真实点击开新标签 `publish?from=edit&pgc_id=`（标题/17 段/图全在）→ 勾「引用AI」→「发布」→ 直接回列表、**无二次确认**，后台变「修改审核中」（**订正**第 340 轮「修改不可用」的口径：仅「审核中」为 disable，「已发布」可改；`?from=edit` 与 `?enter_from=mp_group_management` 是两种页，后者才是空白新稿）⑦ 四硬标准 **3/4**（④ 待复审）⇒ 不切主通道 ⑧ 自赞 1（重载确认）；顺手把 15:04 那篇的赞点回，净 0 ⑨ 评论 0 / 回评 0（提交键恒 disable，如实）⑩ 封面裁切 506×394 低于建议线但平台未拦（记坑）
- 🔀 **2026-11-23（第三百四十轮 · 15:11 唤醒 · 本日第 5 轮 · 窗口 11-23 12:00 → 15:00 CST · 并发接续）** —— ① **开工三件**：`hb` `1795417873`（= 15:11:13 CST）· `git log -- run/news` 最新 = 第 339 轮（12:1x）· 后台 `共 93 条`、首行「先跑三遍，再要一个更大的模型 · 11-23 15:04 · 审核中」② ⚠️ **并发如实记**：`/tmp/r340/` 已有 15:02–15:10 另一进程完成采集 5 条（已落盘 `news/` + `SEEN.md` +6 → 3,781 + `INDEX` +1）+ 配图 1 张（`imgs/2026-11-23-1505-ith-glm54-codingplan.jpg` · 134,588 B · JPEG 864×596）+ **发布（15:04 · 后台 92 → 93）**；该进程 15:10 起无存活 ⇒ 本 agent **只核验 + 记账**，零重采零重发 ③ 四硬标准实测 **3/4**：① ✅ `/article/7711259016902623785/`（公开页当时仍回首页 = 审核中）② ✅ 预览页 `IMGS {n:2, vis:2, broken:0}` 图 640×441 `complete:true` ③ ✅ `NOTICE {hits:[]}` ④ ❌ 预览页 `DECL found:false`、全文无 `AI`（对照 12:06 公开页 `found:true` ⇒ 口径有效；**但预览页结构上不渲染声明 ⇒ 本条属「未验出」而非「已证缺失」**）④ **两次补改均失败并停手**：审核中「修改」=`span class="disable"`（4 次点击无反应）；`publish?…&pgc_id=` 开**空白新稿**（`共 0 字`）⇒ 入「不许重试」⑤ 正文实测 `han 996 / all 1350`（未读编辑器字数，不写「共 N 字」）⑥ 记 `STYLE §A.42` 4 条；同步补记 `news/2026-11-23.md`（四硬标准表 + 并发说明 + 第 339 轮发布记录/已转「已发布」）⑦ 自赞 **未做**（并发段没做，本 agent 不补）；评论 0 / 回评 0（如实）
- 📦 第 339 轮流水条原文（1493 B · sha `e33bc7048a589462`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-23 22:0x（第 342 轮·第 339 轮流水条原文）」（原文一字未改）
- 📦 第 338 轮流水条原文（1794 B · sha `e64dac8471505152`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-23 12:0x」（原文一字未改）

- 📦 第 328 轮流水条原文（216 B · sha `d9e7b69047f3156c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 07:5x（第 343 轮压红线 · 第 328 轮流水条原文）」（原文一字未改）
- 🔀 **2026-11-21（第三百二十六轮 · 18:00 定时窗 · 本日第 6 轮 · 窗口 11-21 15:10 → 18:45 CST）** —— ① **并发核查**：18:00–18:07 有并发进程写草稿（`/tmp/r326/` 全套 `base/s0/s1/s2b/move/move2/insp`），**未发**、无进程在跑；基线 `共 81 条内容` ② 🛠 **坏草稿弃页重开**：图为零尺寸游离 `DIV.pgc-img`（`IMGPOS {x:10,y:10,w:0,h:0}`）、`Delete` 清正文无效（`ps 29 → 51`）、`ensure`「继续编辑」回滚旧稿 ⇒ `nav(/graphic/articles)` → `publish`，回读 `STATE {title:"", raw:1, words:"共 0 字", imgs:0}` ③ 逐段写 23 段（`CHK {ps:24, empty:[23], words:"共 1238 字"}`）→ 插图 + 36 字图注（`ERR NONE`）→ `引用AI:true` → 预览 `hasConfirm:true` → `确认发布` 一次 ④ `共 81 → 82 条内容`，`article/7710563550304961060`「AI替你点外卖前，得先验一下那块屏」18:21 已发布；**四硬标准 4/4**（`artH:2280` / `IMGS n1 vis1 broken0 1178×656` / `NOTICE hits:[]` / `DECL found:true`）⑤ 自赞 1（重载仍 1）⑥ 引流评论 0 / 回评 0（如实）⑦ 采集段由并发段落盘（`SEEN.md` +14）⇒ 不重复采集 ⑧ 新坑 6 条 → `STYLE §A.31`


- 🔀 **2026-11-21（第三百二十二轮 · 09:30 定时窗 · 本日第 2 轮 · 窗口 11-21 07:10 → 09:40 CST）** —— ① ⚠️ **开工先读后台**：09:31 `共 77 条`，首行「能打印的药片，藏着两层壳 · 07:38」在 `run/**/*.md` 零命中 ⇒ 判**无账发布**（物理时间 07:34 / 07:38:50 / 07:39）⇒ **只补账不重发**，并如实记该篇 `引用AI` 未勾 ② **采集 13 条**（§1 3 / §2 1 / §3 2 / §4 1 / §5 5 / §6 1）· `NEW 43` / 实抓 14 篇 · `--cn-news` 194 条过目入 2 · 量子位未取 · research `news_ready` 0 · 🖼 **有图 10 / 无图 3** · `SEEN.md` 3,617 → **3,637** · `INDEX` 25 ③ ✅ **图文文章（带 1 图）** `article/7710432109227246099`「药片也能打印了：第一张证已经发出去」**09:35** · 16 段 / `共 1468 字` · 1 图 PNG 879×494（499,989 B）· 图注「图：央视网 央视财经《经济半小时》节目画面」· 后台 **77 → 78** · **四硬标准 4/4** ④ ❤️ 自赞 1（`detail-like like | 1` 重载确认）⑤ **引流评论 0 / 回评 0（如实）** ⑥ ⚠️ `like2.py` 的 `URL=` 硬编码 ⇒ 一度点到上一篇，已点回（净 0）⑦ STYLE **§A.28** 5 条（后台首行≠自己上一篇 / 后台计数是唯一硬证据 / 自赞看 `className` / `NOTICE` 命中先看上下文 / 带 `URL=` 脚本先 grep）⑧ 采集段自查纠错：12 → 13 条（补央视网药片条）
- 🔀 **2026-11-21（第三百二十一轮 · 07:00 定时窗 · 本日第 1 轮 · 窗口 11-20 22:05 → 11-21 07:30 CST）** —— ① ⚠️ **补账**：第 320 轮（22:0x）采集 8 条 + 发布 `article/7710254088147943972` + 自赞 + 评论 2 条均已完成，但漏写记录 ⇒ 本轮只补账不重发 ② **采集 12 条**（§1 3 / §2 2 / §3 1 / §4 1 / §5 3 / §6 2）· `SEEN.md` 3,600 → **3,617** · `INDEX` 12 · 🖼 **有图 8 / 无图 4** ③ ✅ **图文文章（带 1 图）** `article/7710393622440722998`「宣称攻克的黎曼猜想，为什么还没人敢签字」**07:11** · 23 段 / 939 字 · 1 图 PNG 840×700 · 后台 **75 → 76** · **四硬标准 4/4** ④ 选题 `1/030/278` 只写「宣称」（原文 `I believe`）⑤ ❤️ 自赞 1 ⑥ **引流评论 3 投 3 中**（1→2 / 26→27 / 1→2）⇒ 日计 **3/40** ⑦ 回评 **0/3（如实）** ⑧ 后台 **85 / 45,696 / 9.34 元** ⑨ STYLE **§A.27** 6 条新坑（标题框残留 / 定位段别用旧关键词 / 题注插错后整篇重建 / 题注框有两个 / 封面先滚到底 / 评论只认 canonical+列表）⑩ 📦 压红线：第 316b 轮快照三行 2,129 B → ARCHIVE「📦 归档块 · 2026-11-21 06:5x」

- 📦 第 309 轮流水条原文（2194 B · sha `da2d1375d7affeb2`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-24 07:5x（第 343 轮压红线 · 第 309 轮流水条原文）」（原文一字未改）

- 🔀 **2026-11-18（第三百零二轮 · 18:00 定时窗 · 本日第 6 轮 · 窗口 11-18 15:0x → 18:2x CST）** —— ① **采集 4 条**（§1 2 / §3 1 / §4 1 · §2 §5 §6 本类无新增）· IT之家 3 + 量子位 1 · `RSS_ITEMS 60 SEEN_HIT 12 NEW 48` · 实抓正文 13 篇 · 🖼 **有图 3 / 无图 1** · `SEEN.md` 3,226 → **3,240**（+14，含 W 区 10）· `INDEX` 当日 **61** · research `news_ready` **0** ② ✅ **图文文章（带 1 图）** `article/7709450669614219830`「医疗 AI 打分的尺子，先被做出来了」**18:08** · 25 段 / 编辑器 `1049 字` · 1 图 `nw1200 nh675` 渲染 676×380 `complete:true` · 图注「图：量子位」· 后台 **53 → 54** · **四硬标准 4/4** ③ 配图 2 选 1：官网首屏图（干净）用 / 作者机构列表图（内嵌网址、无视觉信息）弃 ④ **引流评论 5 条落地**（0→1 / 0→1 / 0→1 / 1→2 / 0→1）⇒ 日计 **14/40** ⑤ ⚠️ **E 帖误重发 1 次**：首判 `AFTER 0 / RECHECK mine:false` 未先复读就重发 ⇒ 该帖 2 条同文，如实记、未删；**新纪律：首判失败先 `verify.py` 复读** ⑥ 回评 **0/3**（2 篇有楼帖均无未答提问）⑦ **粉丝/阅读/收益未重读**（后台概览页只渲染导航，全 `NONE`）⑧ 🔑 新坑：量子位正文容器 = `<div class=\"article\">`；`verify.py` 复制后仍 import `/tmp/r300/cdp` ⑨ 📦 滚动：第 301 轮快照四行 2,103 B → ARCHIVE「📦 归档块 · 2026-11-18 18:2x」

- 📦 第 298 轮流水条原文（1535 B · sha `7a1f87e05db75bdd`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-21 07:0x（第 298 轮流水条原文 · 压红线）」（原文一字未改）

- 📦 第 294 轮 + 291 轮流水条原文（合计 2328 B · sha `62a8330e16e7df6b`/`72a8c621f7d0f572`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-18 10:0x」（原文一字未改）


- 📦 第 290 轮流水条原文（1183 B · sha `6ae4891ec8d8b3e2`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 07:4x」（原文一字未改）


- 📦 上条流水原文（1717 B · sha `22218d9babc8441c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 12:0x」（原文一字未改）

- 📦 上条流水原文（1673 B · sha `06021c0d23f93217`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 18:4x」（原文一字未改）

（第 230/229 轮流水条原文已合并归档 → `MEMORY_NEWS_ARCHIVE.md`「📦 旧指针并入」）
- 📦 第 263 轮流水条原文（305 B · sha `49227ea808e57af7`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 230 轮流水条原文」
