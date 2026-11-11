# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

PHASE:        常态采集（第 11 批 P0 已完成 · 第 13 批头条涨粉常态化 · 番茄线待裁断）· **第 257 轮已完** · 本日发帖 **1/6**（图文文章 1）· 评论 **5/40** · 自赞 1 · 回评 0/3 · ✅ **主通道 = 图文文章（带 1 图），微头条为辅助** —— 依据 = 第 257 轮新发 `article/7707053987975774762` **四条硬标准再次全过**（非 `/w/` URL · 首图 1200×630 complete · `WARN []` · `作品声明：内容由AI生成`）
- 当前动作:（**第 257 轮 · 07:00 时窗 · 11-12 新自然日第 1 轮** · 窗口 11-11 21:3x → 11-12 07:3x CST · **分两段执行，如实记**）① **采集 16 条**（§1 ×4 **AlphaGenome 2 单细胞条件式架构**〔`822`·68 类组织 / 1.07 亿单细胞 / 因果变异 30% vs 16% / 方向 43% vs 23%〕· **CarPlay 接入 Gemini**〔`831`〕· **Adobe 四项 Sneaks**〔`815`〕· **DeepL Aure（8 语 · 无中文）**〔`810`〕· **RTX Spark 进 Win11**〔`766`〕；§2 ×2 **Grok 生成儿童色情图像集体诉讼**〔`809`〕· **存储 Q4 官方价**〔`786`〕；§3 ×2 **宁夏 10 个重大科技专项**〔中新网 `10730500`〕· **创新创业大赛 158 项目**〔`10730483`〕；§4 ×2 **速卖通 AI 托管日均成交 +近 70%**〔`10730521`〕· **来宾糖业 160 亿元**〔`10730491`〕；§5 ×4 **GTA6 预购 10 亿美元**〔`830`〕· **网传罢免黄仁勋（无官方公告）**〔`829`〕· **魏牌二代蓝山 13,086 台**〔`785`〕· **HarmonyOS 7 5.55GB**〔`782`〕；§6 ×2 **量子位「卖 Token→卖结果」**〔`509088`〕· **CMF 微专业**〔`10730475`〕）+ 附录 4 组；`SEEN.md` +18（2,458→**2,476**）· INDEX 11-12 = **16**；🖼 **本轮 16 条 · 有图 12 条 · 无图 4 条**（`810`/`786`/`509088`/`10730475` 正文 0 图）② **发帖 1 篇（主通道）**：图文文章 **「AI读DNA，这次读到了单个细胞」**（**16/30** 字 · 后台 **674 字** · 14 段 + 1 图 + 图注）· 图 `imgs/2026-11-12-0710-alphagenome2.png`（688,045 B · 1200×630 · 看图合规）· 双声明 `头条首发`+`引用AI` ⇒ **`article/7707053987975774762` · 07:10 已发布 · 首发**；**四条硬标准 4/4 全过 ⇒ 主通道维持** ③ **评论 5/5**（全 CODE 0 · 计数均 +1 · 0 截断）：花呗诉讼 35→36 · OpenAI 游戏机 4→5 · AMD Zen 6 0→1 · AI 短剧 8→9 · STEM 停办 0→1 ⇒ **日计 5/40** ④ **自赞 1/1**（`detail-like` → `detail-like like`，真鼠标）⑤ **回评 0/3 如实记**（`comment/all` 首屏 14 行全为本人；文章页「回复」按钮 `REPLYBTN NF`，两次探评论区均 `评论 0` 懒加载未渲染）⑥ 基线：粉丝 **82** · 总阅读 **44,201** · 收益 **9.1 元**（三点「昨日计算中」⇒ 未刷新）⑦ ⚠️ **查明并登记第 256 轮遗留：同一篇重复发布**（`7706914774336143915` 22:13 / `7706918729116664374` 22:23 · 两 URL 均 200、md5 一致）—— **未删未隐，待用户裁断**；本轮起加三条防复发 ⑧ 标签治理 26→1（closed 25/25）
- 下一步:（第 258 轮 · **11-12 09:30 时窗 · 本日第 2 轮**）① **主通道 = 图文文章**：≤1 篇、标题 ≤30 字、正文 ≥300 字、1 张已看过的图、双声明；**发布只跑一轮**（发布前记 `content/all` COUNT；点完 `确认发布` 只读列表；改稿另开新 page）② **采集**窗口 11-12 07:3x → 09:3x：IT之家基线 `1/025/831` · 中新网基线 `10730521` · 量子位 `509088` · 爱范儿（补跑已完成，恢复正常节奏）③ **评论** 日计 5/40，可评 ≤5；**勿重复** `7706871644786917898`/`7706841508355392034`/`7706817415958577699`/`7706404278100886035`/`7706820177299505706` 及之前全部楼层 ④ **回评** 改走 `comment/all` 逐行判 who（**不再**用文章页找「回复」按钮）⑤ **重复两篇不删**，继续待裁断 ⑥ 脚本：`cp /tmp/r257_news/*.py` 到新目录后 `sed` 改路径 + `grep -l '/tmp/r257'` 双核 ⑦ 记忆写入后再测体积（>32KB 即最小滚动）
- 阻塞: 老阻塞不变：粉丝 **82 · 收益 9.1 元 · 总阅读 44,201** · 番茄建书 `can_create_serial_book=false` 待裁断（不逐轮重试）· 通用搜索对具体人名/论文标题不可用 · 知乎/雪球被墙 · 央视网正文容器常为空 ⇒ 只登标题 · IT之家正文取 `id="paragraph"` 段内去标签 · 头条 feed 涉时政/涉军占比高 ⇒ **宁缺不评** · 量子位 RSS 默认 UA 403 须浏览器 UA · 中新网正文 URL 日期段必须当日 · `run_commands` 30s 硬超时 ⇒ **两段式**（启动后台 → 另次读日志）· `/w/` 帖不能用 `cmt_one.py` 评论 · 本机**无 PIL / 无 tesseract** ⇒ 看图走 CDP base64 + 截图 + 多模态 · IT之家 `src` 是 73B `t.png` 占位 ⇒ 取 `data-original` · **⚠️ `DOM.setFileInputFiles` 打隐藏 file input 会让该标签页 CDP 整体 wedged ⇒ 用 `curl /json/close/<tid>` 只关该页重开，🚫 不 pkill 9222** · **⚠️ 同稿重复发布累计 4 篇待裁断**：11-11 两篇 `7706759795105088054`/`7706729234433917482` + 11-11 22:13/22:23 两篇 `7706914774336143915`/`7706918729116664374`（后者为第 256 轮遗留，本轮查明）；「AI 标识推荐流他见」仍无法自验（非硬阻塞）

- 📦 第 255 轮快照三行（当前动作 / 下一步 / 阻塞）原文（4,917 B · sha `c618fdeed1247be4`/`1cd697f909a424c0`/`e9642d7be56788c6`）→ `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-12 07:3x」（原文一字未改）

- 📦 第 251 轮快照三行（当前动作/下一步/阻塞）原文 → `MEMORY_NEWS_ARCHIVE.md`「2026-11-11 21:5x」（3 行 · 原文一字未改）
  5. ⚠️ **重复发布坑（第 251 轮实证）**：同一 `targetId` 上**再点一次** `预览并发布` + `确认发布` 会生成**新文章**（新 ID），与 10-25「同 targetId 残留 state」不同 ⇒ **每篇发布动作只跑一轮**；点完 `确认发布` 后**只读** `/profile_v4/graphic/articles`，🚫 不重复点发布按钮；要复核就 reload 该列表页。
  6. 🖼 **配图落地**：下载前先看图（`view.py`：base64 注入 `<img>` + 截图 + 多模态读），确认无二维码/微信号/外链短址/第三方水印再用；文件名 `imgs/<YYYY-MM-DD-HHMM>-<slug>.<ext>`，扩展名须与 Content-Type 一致；🚫 不入 git。
  7. 🎯 **图片尺寸坑**：IT之家官图常为**竖长图**（本篇 1017×1431、另一篇 1080×6659）⇒ 正文里渲染宽 676px、高度会被拉得很长；发长图前先看图，过长就换第二张候选。
  8. 📊 **后台读数**：`/profile_v4/graphic/articles` 文首「共 N 条内容」+ 每行 `时间 / 状态 / 展现 / 阅读`，刷新（`location.reload`）才更新状态（12:07 首读「审核中」→ 刷新后「已发布」）。
  9. 收尾：写 `news/<date>.md`（条目 + 通道认定）→ `SEEN.md` / `INDEX.md` → MEMORY 快照 + 流水 + `daily-memories-news/<date>.md` → `git pull --rebase --autostash` → `git add -- run/MEMORY_NEWS.md run/MEMORY_NEWS_ARCHIVE.md run/daily-memories-news run/news` → commit → push → `git status -sb` 无 ahead/behind；提交前 `git status --porcelain | grep -Ei '\.(png|jpe?g|webp)$'` 必须为空。

- 📦 第 243 轮快照 3 行原文（4,400 B · sha `39ab4a59c4f7f6cc`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-10 12:1x」

- 📦 第 238 轮快照 3 行原文（4,512 B · sha `3946423ddec919b6`）→ ARCHIVE「2026-11-09 15:1x」
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

- **[09:3x] wake (2026-11-10 第 243 轮)** | PHASE=常态采集 | news +8 独立事件（§6 = 0 如实；IT之家 RSS 60/60 全读 · 本窗新增 16 条 `1/024/572`–`612` · 正文 7/7 `<title>` 一致，`604` 无 `<p>` 改按 `id="paragraph"` 段内去标签提取 · 中新网 `--cn-news` 30/30（主类 2）· 央视网正文 2/2 · 爱范儿 20/20（0 入主类）· 量子位 10/10（0 新增））· 发帖 1（`w/1881433097720844` · 后台 **593→594** · 6 段 **219** 字符 · `头条首发`+`引用AI` 双真 `ALL_OK` 才发 · 公开页「作品声明：内容由AI生成」+ 2026-11-10 09:33）· 评论 5（`0→1`/`0→1`/`0→1`/`0→1`/`2→3`，全 `CODE 0`、0 ASCII）· 点赞 1 · 回评 0/3（首屏 10 条全为「我」）· 基线 **82 / 43,966 / 9.07**（连续第 5 时窗未刷新）· prune 开场 matched=1 kept=1 · 收尾 matched=**21** kept=1 **closed=20/20** · 记忆滚动（第 242 轮快照 3 行 2,161 B → ARCHIVE「2026-11-10 09:3x」）30,386 → **32,052 B（回线内）**
- **[07:0x] wake (2026-11-10 第 242 轮)** | PHASE=常态采集 | news +9 独立事件（§6 = 0 如实；IT之家 RSS 60/60 全读 · 本窗新增 20 条 `1/024/549`–`568`+`570` · 正文 6/6 `<title>` 一致，`564`/`561` 无 `<p>` 改抓 `post_content` · 中新网 `--cn-news` 30/30 + finance 30/30 主类 0 · 量子位 10/10（新增 1 条）· 爱范儿 20/20（1 条入 §1））· 发帖 1（`w/1881423852191756` · 后台 **592→593** · 6 段 **259** 字符 · `头条首发`+`引用AI` 双真 `ALL_OK` 才发 · 公开页「作品声明：内容由AI生成」+ 2026-11-10 07:06）· 评论 5（`15→16` / `1→2` / `2→3` / `3→4` / `7→8`，全 `CODE 0`、0 ASCII）· 点赞 1 · 回评 0/3（首屏 10 条全为「我」）· 基线 **82 / 43,966 / 9.07**（连续第 4 时窗未刷新）· 🐞 30s 超时连同 `sleep 45` 会把 heredoc 写入一起吞掉 ⇒ 写脚本 / 启动 / 读日志分三次调用 · 记忆滚动 30,299 → **30,371 B**（回线内）
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
- 🔀 **2026-11-12（第二百五十七轮 · 07:00 时窗 · 本日第 1 轮 · 窗口 11-11 21:3x → 11-12 07:3x CST）** —— ① **采集 +16**（§1 AlphaGenome 2〔`822`〕/ CarPlay 接 Gemini〔`831`〕/ Adobe 四项 Sneaks〔`815`〕/ DeepL Aure〔`810`〕/ RTX Spark〔`766`〕· §2 Grok 儿童色情图诉讼〔`809`〕/ 存储 Q4 价〔`786`〕· §3 宁夏 10 个重大专项〔`10730500`〕/ 创新创业大赛〔`10730483`〕· §4 速卖通 AI 托管 +近 70%〔`10730521`〕/ 来宾糖业 160 亿〔`10730491`〕· §5 GTA6 预购 10 亿美元〔`830`〕/ 网传罢免黄仁勋〔`829`〕/ 魏牌蓝山 13,086 台〔`785`〕/ HarmonyOS 7〔`782`〕· §6 量子位 509088 / CMF 微专业〔`10730475`〕）`SEEN.md` +18（→**2,476**）· INDEX **16** · 🖼 有图 **12** / 无图 **4** ② **发帖 1 篇** 图文文章「AI读DNA，这次读到了单个细胞」`article/7707053987975774762`（07:10 已发布 · 16/30 字 · 674 字 · 14 段 + 1 图 · 双声明）**四条硬标准 4/4 全过 ⇒ 主通道维持** ③ **评论 5/5**（全 CODE 0 · 计数均 +1 · 0 截断）⇒ 日计 **5/40** ④ **自赞 1/1**（`detail-like like`）⑤ **回评 0/3 如实记**（`comment/all` 全为本人；文章页 `REPLYBTN NF`；评论区懒加载 `评论 0`）⑥ **查明第 256 轮遗留**：同稿重复发布 `7706914774336143915`(22:13)/`7706918729116664374`(22:23)，两 URL 均 200、md5 一致 ⇒ **未删未隐，待裁断**；加三条防复发 ⑦ 基线 82 / 44,201 / 9.1 ⑧ 标签治理 26→1（closed 25/25）⑨ 本轮**分两段**（采集段 07:04 由 auto-commit `e65654c3f` 提交，MEMORY/台账由 07:30 段补写）
- 🔀 **2026-11-11（第二百五十五轮 · 21:30 时窗 · 本日第 7 轮 · 窗口 11-11 18:0x → 21:3x CST）** —— ① **采集 +16**（§1 IBM Nighthawk r3〔`787`〕/ 字节智能体·张一鸣 2029-2030〔`726`〕/ Claude 3 天适配 MI355X〔`736`〕/ 民航大×宁德〔`794`〕/ 宁夏 500 个 AI+制造场景〔`10730455`〕/ ENISA 冰箱被黑〔`784`〕· §2 Grok Build GhostShares〔`790`〕/ 企业 AI 限权〔`734`〕· §3 欧盟数字公平法案〔`735`〕· §4 彭博英国 AI 1/4 增长〔`729`〕/ 下架外卖剧本〔`10730480`〕· §5 宜得利 3,762 万〔`780`〕/ 花呗诉讼〔`781`〕/ 日产 -67.14%〔`791`〕/ 奔驰〔`773`〕/ 电子秤合规〔`797`〕；§6=0 如实）`SEEN.md` +17（→**2,394**）· INDEX **109** · 🖼 有图 **13** / 无图 **3** ② **发帖 1 篇** 图文文章「量子计算机开始拼积木了」`article/7706908695103406628`（21:45 已发布 · 11/30 字 · 528 字 · 12 段 + 1 图 · 双声明）**四条硬标准 4/4 全过 ⇒ 主通道维持** ③ **评论 5/5**（全 CODE 0 · 计数均 +1 · 0 截断）⇒ 日计 **10/40** ④ 回评/自赞未做 ⑤ **踩坑 6 条**：`setFileInputFiles` 打隐藏 input → 单标签页 CDP wedged（其他正常，用 `/json/close` 只关该页）· 本地上传/扫码上传上下排列易误触出关不掉的二维码弹窗 · 发布两处坐标（预览 1123,933 / 确认 1130,933）· tid 文件名对齐等 ⑥ 📦 滚动：第 251 轮快照 3 行（6,260 B · sha `642f73313aacfee0`/`a83a746f5b1f078e`/`b4c87673acb186e3`）→ ARCHIVE「2026-11-11 21:5x」
- 📦 第 251 轮流水分条原文（1463 B · sha `62c93e132b154dfe`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-11 21:5x」
- 📦 第 248 轮流水分条原文（1345 B · sha `1e2e0a72bf28a4bb`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-11 12:2x」
- 📦 第 247 轮流水分条原文（1,491 B · sha `cab25963c943921d`）→ MEMORY_NEWS_ARCHIVE.md「2026-11-11 07:4x」
- 📦 第 244 轮流水分条原文（1,516 B · sha `1be5101a5a097189`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-10 15:2x」
- 📦 第 241 轮流水分条原文（1,755 B · sha `7182e22fda8c6106`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-10 15:2x」

- 📦 第 239 轮流水分条原文（1352 B · sha `2fc0b61be1bb7018`）→ ARCHIVE「2026-11-10 12:2x」

- 📦 第 237 轮流水分条原文（1680 B · sha `7f6d777843fac19c`）→ ARCHIVE「2026-11-09 12:1x」
- 📦 第 236 轮流水分条原文（2885 B · sha `eba5e96b50abcbd4`）→ ARCHIVE「2026-11-09 09:5x」
- 📦 第 235 轮流水条原文（3,545 B）→ ARCHIVE「2026-11-09 07:3x」
- 📦 第 235 / 233 / 232 轮三行指针原文（290 B · sha `10caacf3ede6b4ae`）→ `MEMORY_NEWS_ARCHIVE.md`「2026-11-11 12:2x」
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
Volume:      MEMORY_NEWS.md **32,233 B（第 257 轮收尾 `wc -c` 实测 · 32KB 软线内）**（红线 40KB）；第 257 轮滚动（最小滚动）：① 第 255 轮快照「当前动作 / 下一步 / 阻塞」三行（4,917 B · sha `c618fdeed1247be4`/`1cd697f909a424c0`/`e9642d7be56788c6`）② 2026-11-07 第 224 轮唤醒行（825 B · sha `e1b32f04f74a1aae`）→ 均搬入 `MEMORY_NEWS_ARCHIVE.md`「📦 归档块 · 2026-11-12 07:3x」（原文一字未改，原位各留 1 行指针）。本轮同步：快照 3 行重写 + 流水 1 条 + `daily-memories-news/2026-11-12.md`（新建，第 257 轮段）+ `news/2026-11-12.md`（+16 条，采集段已由 auto-commit `e65654c3f` 提交）+ `SEEN.md` 2,476 + `INDEX.md` 16 + `台账.md` 第 257 轮。

