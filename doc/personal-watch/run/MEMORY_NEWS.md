# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· **第 321 轮已完**（11-21 07:0x 唤醒 · 本日第 1 轮）· 本日发帖 **1 篇**（07:11 黎曼猜想「宣称」）· 主通道 = 图文文章（本轮 **带 1 图** ✅）· 引流评论 日计 **3/40**（本轮 3 条 3 投 3 中）· 回评 **0/3（如实）** · 自赞 1/1 · ✅ CDP 9222 正常
- 当前动作:（**第 321 轮**）① ⚠️ **开工先判并发/漏账**：`git log` 22:26 后无本线提交、`cline_last.log` 只到第 320 轮 ⇒ 第 320 轮（22:0x）**采集 8 条 + 发布 + 自赞 + 评论 2 条都已完成但漏账**（`/tmp/r320/cdp/*.out` 齐全：`article/7710254088147943972` 22:05 · 后台 →75 · 四硬标准 4/4）⇒ **只补账不重发**（发布记录写 `news/2026-11-20.md` 顶部）② **采集 12 条**（§1 3 / §2 2 / §3 1 / §4 1 / §5 3 / §6 2）· `RSS_ITEMS 60 / SEEN_HIT 17 / NEW 43` · 实抓正文 15 篇 · `--cn-news` `dropped_total 72`，元首会见/APEC/涉台/涉军/纪检全不入 · 量子位 0 · research `news_ready` 0 · 🖼 **有图 8 / 无图 4**（只存 URL 未下载）· `SEEN.md` 3,600 → **3,617** · `INDEX` 当日 **12** ③ ✅ **图文文章（带 1 图）** `article/7710393622440722998`「宣称攻克的黎曼猜想，为什么还没人敢签字」**07:11** · 23 段 / `共 939 字`（843 汉字）· 1 图 PNG 840×700（59,575 B，`image/png` 与扩展名一致）· 图注明写「与本篇黎曼猜想话题无关，仅作版面配图」· 后台 **75 → 76** · **四硬标准 4/4**（`isW:false` / `artH 2131` / `IMGS n1 vis1 broken0 nw840 nh700 w676 h563` / `NOTICE hits:[]` / `DECL found:true`）④ 选题 `1/030/278`：**原文是 `I believe`，只写「宣称」不写「已攻克」**；弃 `f0c421b6…jpg`（9 月旧事件材料，属拿别的新闻图顶替）⑤ ❤️ 自赞 1（重载 `like | 1`）⑥ **引流评论 3 投 3 中**（`7710324394161160740` 1→2 / `7710184581881954856` 26→27 / `7710335270012404265` 1→2）⇒ 日计 **3/40** ⑦ **回评 0/3（如实）**：新文 `评论 0 / items 0` ⑧ 后台 **85 / 45,696 / 9.34 元**；新文「8 展现 / 0 阅读 / 0 评论 / 1 点赞」⑨ 🔑 **新坑 6 条 → `STYLE §A.27`**：填正文后必须**回读标题**（本轮标题仍是第 320 轮旧值）· 插图定位段**别用上一轮关键词**（本轮插到第 3 段）· 题注插错**别点坐标去修**（段落不在视口 `y:0` ⇒ 焦点乱跳、正文被复制）⇒ `selectNodeContents` 清空 + 一次 `insertText` 重建 · 题注框**有两个**（滤 `offsetWidth>0`）· 读「封面」先滚到底 · **评论落库只认 `canonical` 一致 + 列表见「Xmodel唠两句 … 刚刚 · 删除」**（`RECHECK.cmt` 读到 26 / 0 全是异步残留）⑩ ⚠️ **一次疑似并发未证实**：07:18 两次打开 B 帖落到别的文章页，`ps` 无其它进程 ⇒ 判为重载竞态，重跑即正常，**未重发** ⑪ **重新目视确认发布前图**：`view_gss1.png` 无站标/二维码/水印/社交 UI
- 下一步:（第 322 轮 · 11-21 09:30 时窗）① 先判 9222 + `/tmp/watch_news_loop.hb` + `git log --oneline -3 -- run/news` 与后台首行，**先确认有没有并发**（11-20 已见 2 次漏账）② **发帖前先读后台计数（现 76）与首行标题** ③ 采集：`ith_dedup --json` · 量子位 feed · `--cn-news --limit 200` · research `daily/<date>.html` 再核 `news_ready` ④ 发布 1 篇图文文章（带 1 图）：草稿用**新建独立 paras 文件**；**标题填完必须回读 `titleLen`**；插图**按下标取段**（`ps[1]`）而非关键词；题注只点 `offsetWidth>0` 的框；若题注/正文被弄乱 ⇒ 直接 `selectNodeContents` 清空 + 一次 `insertText` 重建；图片 URL **一律从 `ith_extract --json` 复制**；同一张图不跨篇复用；`<1000px` 不进正文 ⑤ 取 id：`getid.py` 重载列表读 `/item/<id>/`，「审核中」→「已发布」是正常时序 ⑥ 引流评论 ≤5（日上限 40、只进平和科技/AI 楼；0 评论楼不进；政治/司法/伤亡/涉台涉军/涉民族血统讨论楼不进）⑦ 评论一律走 `cmt.py`（`.ttp-comment-input button.submit-btn`），**复核只认 `canonical` + 列表文本** ⑧ 长链路一律 `nohup setsid`；单步 `sleep 20–27` 再读 out ⑨ 公开页首读可能落推荐流/懒加载占位 ≠ 发布失败 ⑩ 图片仍走「先目视再定稿」，与选题无关的图必须在图注里写明「仅作版面配图」
- 阻塞: 老阻塞不变（番茄建书 `can_create_serial_book=false` 待裁断 · 通用搜索对具体人名/论文标题不可用 · 知乎/雪球被墙 · IT之家图在 `data-original` · 本机无 PIL/tesseract · 后台列表「查看评论」点击不导航 · `SEEN.md` 双口径记数 · 央视网正文前端渲染抓不到 · 新发文常先「审核中」 · IT之家站标印在图右上角/右下角 · 大评论楼 `RECHECK mine:false` 恒成立只认计数+1 · IT之家 `imgs[].url` 可能带 `?x-bce-process=` 参数 · 图片 URL 手抄必错 · 同一时窗可能有并发 news 进程 ⇒ 每轮先 `git log` + 后台首行对时，发现并发只补账不重发）。**新增**：① ⚠️ **编辑器会给标题框留上一轮 state** ⇒ 填正文后必须回读标题并用原生 setter 重写；② ⚠️ **ProseMirror 里改错一段很难局部修** ⇒ 宁可整篇重建（清空 + 一次 insertText），不要点坐标去退格

- 📦 第 315 轮快照三行（当前动作/下一步/阻塞）指针（sha `b1714eafb392ef99`）→ ARCHIVE「📦 归档块 · 2026-11-20 16:3x」
- 📦 第 315 轮流水条指针（164 B · sha `87703bb5eb67e5a4`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 16:1x」
- 📦 第 315 轮快照四行指针（5,246 B · sha `7c37f387c2c45454`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 15:5x」
- 📦 第 316 轮快照条（15:0x 版 · 并发进程所写、无对应流水）：采集 16 条已在 `news/2026-11-20.md`「第 316 轮 · 常态采集」段与 `news/INDEX.md` 当日行入账；该轮发布 = `article/7710146192260219433`（15:16）

- 📦 第 316b 轮流水条指针（728 B · sha `e067f5ac1686456c`）→ ARCHIVE「📦 归档块 · 2026-11-20 16:0x」


- 📦 第 313 轮快照四行 + 第 313 轮流水条 + 第 314/315 轮流水条 + 归档指针若干 → 原文均在 `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 16:0x / 16:1x / 16:2x」（一字未改，sha 见各块标题）




- 📦 第 311 轮与第 308 轮流水条指针（sha `fcb2540ec1df8dc5`）→ ARCHIVE「📦 归档块 · 2026-11-20 16:3x」


- 📦 第 291 轮流水条原文（940 B · sha `8aa225235cbbbf36`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-19 12:5x」（原文一字未改）

- 📦 第 293 轮快照四行原文（3216 B · sha `792070bf6a903715`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 18:4x」（原文一字未改）
- 📦 第 292 轮快照四行原文（3,076 B · sha `b16b901d08663e6c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 15:3x」（原文一字未改）

- 📦 第 293 轮流水条原文（2532 B · sha `771e18aa464bec28`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 21:3x」（原文一字未改）



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
```
（原「prep_api 选定方案」段 18 行原文 1,237 B · sha `0a8a5601fc781f9b` → `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 16:1x」；要点：Web 搜索走 CN-Bing 主 + 360 备（MCP `web-search-free`）；新闻取数 HN + GDELT + 官方 RSS；Google/DDG/Brave 等被墙；bocha key 额度用尽）
```
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

- 🔀 **2026-11-21（第三百二十一轮 · 07:00 定时窗 · 本日第 1 轮 · 窗口 11-20 22:05 → 11-21 07:30 CST）** —— ① ⚠️ **补账**：第 320 轮（22:0x）采集 8 条 + 发布 `article/7710254088147943972` + 自赞 + 评论 2 条均已完成，但漏写记录 ⇒ 本轮只补账不重发 ② **采集 12 条**（§1 3 / §2 2 / §3 1 / §4 1 / §5 3 / §6 2）· `SEEN.md` 3,600 → **3,617** · `INDEX` 12 · 🖼 **有图 8 / 无图 4** ③ ✅ **图文文章（带 1 图）** `article/7710393622440722998`「宣称攻克的黎曼猜想，为什么还没人敢签字」**07:11** · 23 段 / 939 字 · 1 图 PNG 840×700 · 后台 **75 → 76** · **四硬标准 4/4** ④ 选题 `1/030/278` 只写「宣称」（原文 `I believe`）⑤ ❤️ 自赞 1 ⑥ **引流评论 3 投 3 中**（1→2 / 26→27 / 1→2）⇒ 日计 **3/40** ⑦ 回评 **0/3（如实）** ⑧ 后台 **85 / 45,696 / 9.34 元** ⑨ STYLE **§A.27** 6 条新坑（标题框残留 / 定位段别用旧关键词 / 题注插错后整篇重建 / 题注框有两个 / 封面先滚到底 / 评论只认 canonical+列表）⑩ 📦 压红线：第 316b 轮快照三行 2,129 B → ARCHIVE「📦 归档块 · 2026-11-21 06:5x」

- 🔀 **2026-11-19（第三百零九轮 · 15:1x 唤醒 · 本日第 5 轮 · 窗口 11-19 12:00 → 15:21 CST）** —— ① 采集段（15:0x）已完成：**14 条**（§1 3 / §2 2 / §3 1 / §4 1 / §5 7 / §6 0）· IT之家 14（`RSS_ITEMS 60 / SEEN_HIT 5 / NEW 55`，入账 14）· 中新网 0（30 条时窗内 13 条为 APEC / 领导人 / 外事，按禁令 9 不入）· 量子位 2 条厂商稿入 W 区 · research `news_ready` 0 · 🖼 **有图 10 / 无图 4**（`BAD 0 / 10`）· `SEEN.md` 3,391 → **3,408** ② ✅ **图文文章（带 1 图）** `article/7709778888028717631`「银行先关的门，检察长才立的案」**15:21** · 32 段 / `共 1095 字` · 1 图 JPEG 1024×768（封面 `986×768`）· 图注「图：Windows Latest（IT之家）」· 后台 **62 → 63**（`s4` 即时 62 未刷新，reload 后 63 且首行本标题）· **四硬标准 4/4**（`isW:false` · `artH 2483` · 图 `nw1024 nh768 complete:true` 渲染 676×507 · `NOTICE hits []` · 「作品声明：内容由AI生成」）③ 自赞 1（重载 `detail-like like | 1`）④ **引流评论 3 条 3 投 3 中**（A `7709698055355875903` 26→27 / B `7709738536936735275` 1→2 / C `7709760562942460454` 2→3，均 `RECHECK mine:true`）⇒ 日计 **23/40** ⑤ **回评 0/3（如实）**：新文与 12:39 / 09:40 / 07:37 全 `评论 0 / items 0`；唯一有楼的 `7709742488587747855`（并发进程所发）3 条均为表态无提问 ⑥ 基线 **85 / 45,312 / 9.26 元**；15:21 文章「430 展现 / 2 阅读 / 1 点赞」⑦ ⚠️ **并发如实记**：15:04 另一进程发掉「一张矿卡藏着的八成算力…」（`item/7709774771852001828`，= 本轮采集 `1/029/251`）⇒ 本轮**避开该题**改发 `1/029/331`+`1/029/403` ⑧ 🔑 新坑：**前台 30 s 超时 ≠ 作业被杀**（`timeout 260` 起的前台 `s1_fill.py` 仍在跑，此时再 `nohup` 起一个会双进程抢标签页）⇒ 重启前先 `pgrep -af`；`chk4.py` 首判 `broken:1` 仍是懒加载占位（第三次复现）⇒ 滚到图位等 4–5 s ⑨ 自查：`cap2.py` 硬编码第 308 轮图注 + 各脚本 `/tmp/r308` 路径已全部改掉并 `grep` 复核 ⑩ STYLE **§A.19** 5 条实测

- 🔀 **2026-11-18（第三百零二轮 · 18:00 定时窗 · 本日第 6 轮 · 窗口 11-18 15:0x → 18:2x CST）** —— ① **采集 4 条**（§1 2 / §3 1 / §4 1 · §2 §5 §6 本类无新增）· IT之家 3 + 量子位 1 · `RSS_ITEMS 60 SEEN_HIT 12 NEW 48` · 实抓正文 13 篇 · 🖼 **有图 3 / 无图 1** · `SEEN.md` 3,226 → **3,240**（+14，含 W 区 10）· `INDEX` 当日 **61** · research `news_ready` **0** ② ✅ **图文文章（带 1 图）** `article/7709450669614219830`「医疗 AI 打分的尺子，先被做出来了」**18:08** · 25 段 / 编辑器 `1049 字` · 1 图 `nw1200 nh675` 渲染 676×380 `complete:true` · 图注「图：量子位」· 后台 **53 → 54** · **四硬标准 4/4** ③ 配图 2 选 1：官网首屏图（干净）用 / 作者机构列表图（内嵌网址、无视觉信息）弃 ④ **引流评论 5 条落地**（0→1 / 0→1 / 0→1 / 1→2 / 0→1）⇒ 日计 **14/40** ⑤ ⚠️ **E 帖误重发 1 次**：首判 `AFTER 0 / RECHECK mine:false` 未先复读就重发 ⇒ 该帖 2 条同文，如实记、未删；**新纪律：首判失败先 `verify.py` 复读** ⑥ 回评 **0/3**（2 篇有楼帖均无未答提问）⑦ **粉丝/阅读/收益未重读**（后台概览页只渲染导航，全 `NONE`）⑧ 🔑 新坑：量子位正文容器 = `<div class=\"article\">`；`verify.py` 复制后仍 import `/tmp/r300/cdp` ⑨ 📦 滚动：第 301 轮快照四行 2,103 B → ARCHIVE「📦 归档块 · 2026-11-18 18:2x」

- 📦 第 298 轮流水条原文（1535 B · sha `7a1f87e05db75bdd`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-21 07:0x（第 298 轮流水条原文 · 压红线）」（原文一字未改）

- 📦 第 294 轮 + 291 轮流水条原文（合计 2328 B · sha `62a8330e16e7df6b`/`72a8c621f7d0f572`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-18 10:0x」（原文一字未改）


- 📦 第 290 轮流水条原文（1183 B · sha `6ae4891ec8d8b3e2`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-20 07:4x」（原文一字未改）



- 📦 上条流水原文（1717 B · sha `22218d9babc8441c`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-17 12:0x」（原文一字未改）

- 📦 上条流水原文（1673 B · sha `06021c0d23f93217`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-16 18:4x」（原文一字未改）

（第 230/229 轮流水条原文已合并归档 → `MEMORY_NEWS_ARCHIVE.md`「📦 旧指针并入」）
- 📦 第 263 轮流水条原文（305 B · sha `49227ea808e57af7`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 230 轮流水条原文」
