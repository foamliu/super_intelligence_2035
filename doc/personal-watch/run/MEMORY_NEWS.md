# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）** + **任务书自滚归档（已把第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`；每次唤醒按 ≤32KB 自检）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~六十轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库 75,610 条 · N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + §4.4 措辞强度 tone 信号，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md）+ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）· **任务书自滚归档（第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`）** · **第六十~七十八轮常态采集 ✓（news +27：Mistral Large 4 / 英伟达市值 5.8 万亿新高 / Pinterest / Flai · AMD 苏姿丰 / FSD 欧盟 / LibreOffice / Anthropic Claude Team / EmbeddingGemma 2 / Mirror Particle / Hark / Wajo / Lambda $4B / Musubi PolicyLM-1.7B / Underdog / Melius / Anthropic CVP 129k 漏洞 / OpenAI 数学 722 手稿 / 美司法部「超级智能」/ SpaceX $40B / 软件股阶段新高；**明细见 §2 流水**）**· **第七十九轮常态采集（news +6：MAI Code 1.1 Flash 拟整合 Win11 · 英伟达 DGX Station for Windows · 传三星 12Hi HBM4E 通过英伟达等客户质量验证 · CoreWeave 落子印度 240MW · Google SynthID 核验站开放 · Nous Research $90M B 轮 @ $1.5B）** · **第八十轮常态采集（news +2：小马智行 × Uber 伦敦 Robotaxi 测试计划 · 据报三星拟投超 100 万亿越南盾在越建 2 座半导体后端测试厂）** · **第 11 批 P0 · R3（38 标的十年价格全量刷新 · `lag_corr.py` R3 窗口截断后重跑字节一致 · 🆕 `AM_PM_CHECK.md` 首次早报→晚报复核 · `INDEX_FILES.md` 逐文件重登记 · 日报 AM+PM 两版）** · **第八十一轮常态采集（news +5：谷歌云 Gemini Agent · Waymo $5B 贷款 · 格芯×台积电 $2B 硅中介层 · Arena $200M @ $3.1B · 被解雇 OpenAI 安全研究员公开信）** · **第 11 批 P0 · R4（38 标的十年价格全量刷新至 2026-10-08〔ok=38/fail=0·10 条汇率末日补齐〕· `lag_corr.py` R4 复核重跑**与 R1/R2/R3 逐字节一致**〔**第 4 次可复现**〕· `INDEX_FILES.md` R4 重登记 + **R3 登记勘误**· `daily/2026-10-09.md` **AM 版**）**
当前动作:     **本唤醒（2026-10-09 06:00 早报轮 · 第 81 轮）：① 第 11 批 P0 · R4 交付（早报版）② 第八十一轮常态采集（news +5）** —— **①** `fetch_prices.py` **38 标的再全量刷新**（`ok=38 / fail=0`；**末日 38/38 全部 = 2026-10-08**；相对 R3 的**唯一实质变化** = **10 条汇率末日 2026-10-07 → 2026-10-08**〔**`USDCNY` 2026-09-30 → 2026-10-08**，**源侧补齐·未补造**〕，**其余 28 个价格文件行数据逐字节相同**，文件字节差异**仅**来自每次抓取必写的 `fetched_at` 时间戳〔**已定因**〕）；**R4 复核重跑 → `lag_corr.csv` 与 R1/R2/R3 逐字节一致**（sha256 `83d3bf349be52251…` / 4,018,511 B / 23,941 行；全网格 `q<0.10`=**0** / `stable`=**0**）——**原因可证：分析窗口 = 价格 ∩ 语料，语料冻结于 2026-09-30 ⇒ 新增的 2026-10-08 行整体落在窗外** ⇒ **价格刷新无法改变任何统计量**；三处生成器重跑（`LAG_CORR.md` 头 **R3 → R4**、`LATEST_SIGNALS.md` **sha256 不变** `99f284f701f23b94…`、`FINDINGS.md` §3 **追加 R4 条目**）；**`INDEX_FILES.md` R4 重登记**（§A 16 行 + §B **38 个价格文件逐文件** + 目录级指纹 `8699b2b2b16407cf` / 合计 2,561,195 B / 最大 `prices/JPYCNY.json` 104,647 B ⇒ **全部入 git**）+ **🔧 R3 登记勘误**（R3 曾记 `daily/2026-10-08.md` = 130 行 / 11,565 B，**实为 171 行 / 17,567 B**〔登记时点早于 PM 定稿〕⇒ **按实修正、不改内容**）；**⚠️ R4 未新增「早报→当日」机械复核对**（信号面 as-of 仍 2026-09-30 ⇒ `k=1` 目标日仍 2026-10-08，**R3 已核**）⇒ **如实声明、不重复充数**；**② 第八十一轮常态采集（news +5 · 中文 3 / 英文 2，窗口 10-08 18:25 → 10-09 06:00 ≈ 11.6h 隔夜窗）**：IT之家 `010/706` **谷歌云 Gemini Agent**〔`2026/10/8 21:21` CST·「Gemini at Work 2026」·**通用工作智能体**·私人预览 ⇒「预计很快开放」按厂商口径〕· `010/734` **Waymo $5B 贷款**〔`23:01` CST·黑石/PIMCO/Sixth Street·**首次债务融资**·入欧日＝意向〕· `010/716` **格芯×台积电 $2B 硅中介层**〔`22:15` CST·纽约州马耳他·CoWoS® 生态〕· TC **Arena 估值 $3.1B**〔PDT 11:19 → **10-09 02:19 CST**·$200M Lightspeed/Khosla 领投〕· TC **被解雇 OpenAI 安全研究员公开信**〔PDT 13:04 → **10-09 04:04 CST**·**单方陈述**〕；TC《Google brings agentic AI to Gemini》= **同事件交叉印证·不另计**；`cn_news` 30 条无 AI 具体事件 → 不收；**6 条 AI 相关留档**（`010/715` Alexa Tablet / `010/743` 苹果 10-13 发布会预告 / `010/737` 余承东 / `010/718` 乾崑 / `010/697` Counterpoint 代工数据 / TC OpenAI 营收「据报道」）；🔧 **时区勘误：IT之家 / TechCrunch `pubDate` = GMT（TC 页面 PDT）**，此前标「〔CST〕」系笔误（不影响窗口归属），**本轮起以文章页标注时间〔CST〕为准**；`SEEN.md` **+13 行**（5 news + 3 防重 + 6 留档）· `INDEX.md` 新增 **2026-10-09 行** + 计数器 **181 → 186**。**非因果 · 非投资建议 · L3（N5）冻结** 口径不变。
第11批(R4):    ✅ **P0 交付（R1+R2+R3+R4 全部到位）**：`news/signal/` = prices/〔**38 标的·6 类·2016–2026·2.56MB·ok=38/fail=0·全量刷新至 2026-10-08**〕· SOURCE_TEST.md · **INDEX_FILES.md（R4 重登记：§A 代码/文档 15 行 + §B **38 个价格文件逐文件** 行数/字节/sha256/区间）** · `lag_corr.py`→ lag_corr.csv + LAG_CORR.md（**23940 格·FDR `q<0.10`=0/`stable`=0·如实负面**，非因果；**R1/R2/R3/R4 四次运行字节一致 sha256 `83d3bf34…`**；R3 = 数据全量刷新 + 窗口截断「价格 ∩ 语料」后重跑；**R4 = 早报轮再全量刷新〔38/38 末日 = 2026-10-08〕⇒ CSV 仍逐字节不变**）｜`PREREG.md` **先于结果**｜`BOOTSTRAP.md`（**3 组：G1 FDR 全格 / G2 top-|coef| 每频（post-hoc·exploratory）/ G3 随机 20 格（seed 20351009）→ G3 = 19/20 CI 跨 0**）｜`FINDINGS.md`（台账 §3 已含 **R3 条目**）｜**日报 `daily/2026-10-08.md`（AM 06:00 生成 + PM 18:00 优化）**｜🆕 **`AM_PM_CHECK.md`（`am_pm_check.py`）= 首次「早报 → 今日实际」机械复核**（3 个 `|z|≥1.5` 信号 × daily `k=1` × 21 只个股 = 63 格；命中 **0.4762 / 0.0476 / 0.4762** vs 当日多数向基线 **0.9524** ⇒ **未赢基线 · 单日不构成结论**） ⇒ **第 11 批 P0 无余项**
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
- **第 11 批产物（P0 · 新闻信号 → 资产价格）**：`news/signal/`（`PREREG.md` / `SOURCE_TEST.md` / `prices/`〔**38 标的 十年 2016–2026**〕/ `lag_corr.py` → `lag_corr.csv` + `LAG_CORR.md` / `BOOTSTRAP.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / **`AM_PM_CHECK.md`** / `daily/<date>.md` / **`INDEX_FILES.md`**）；⚠️ ≥5MB 不入 git，`lag_corr.csv` ≈ **4.0MB < 5MB ⇒ 入 git**
- **上次采集窗口**：`2026-10-08 18:25 CST` 第八十轮 ~ `2026-10-09 06:00 CST` 第八十一轮（**第八十一轮为本轮唤醒 · 早报轮**；窗口 ≈ 11.6h）
- **累计收录**：`news` **186** 条（第一~八十一轮；当日 **5**）+ 非新闻（口径=逐行统计 `SEEN.md` 类型列）〔**仅存 `SEEN.md`**〕

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-09（第 11 批 · R4 · P0 · 06:00 早报轮）** —— ✅ **① P0 R4 交付（早报版）**：`fetch_prices.py` **38 标的再全量刷新**（`ok=38 / fail=0`；**末日 38/38 全部 = 2026-10-08**）；相对 R3 **唯一实质变化 = 10 条汇率末日 2026-10-07 → 2026-10-08**（**`USDCNY` 2026-09-30 → 2026-10-08**，**源侧补齐·未补造**），**其余 28 个价格文件行数据逐字节相同**（文件字节差异**仅**来自 `fetched_at` 时间戳 ⇒ **已定因，非数据漂移**）。`lag_corr.py` **R4 复核重跑 → `lag_corr.csv` 与 R1/R2/R3 逐字节一致**（sha256 `83d3bf349be52251…` / 4,018,511 B / 23,941 行；全网格 23,940 格 · `q<0.10`=**0** · `stable`=**0**）——**原因可证：分析窗口 = 价格 ∩ 语料，语料冻结于 2026-09-30 ⇒ 新增 2026-10-08 行整体落在窗外** ⇒ **价格刷新不能改变任何统计量**（**第 4 次连续字节一致**）。三处生成器重跑：`LAG_CORR.md` 头 **R3 → R4 复核（2026-10-09 早）** · `signal_snapshot.py` → **`LATEST_SIGNALS.md` sha256 未变**（`99f284f701f23b94…`）· `make_findings.py`（`VERIFY_DATE` 2026-10-08 → 2026-10-09）+ `FINDINGS.md` §3 **追加 R4 条目**。**`INDEX_FILES.md` R4 重登记**（脚本生成：§A 代码/文档/生成物 **16 行**；§B **38 个价格文件逐文件** 名/类/行数/字节/sha16/存放/区间；**目录级指纹 `8699b2b2b16407cf`**；合计 **2,561,195 B**；最大 `prices/JPYCNY.json` **104,647 B** ⇒ **全部 < 5 MB ⇒ 入 git**；**末日一致性 38/38 ✅**）。**🔧 R4 登记勘误**：R3 §A 曾记 `daily/2026-10-08.md` = **130 行 / 11,565 B**（**登记时点早于 PM 定稿**），**实际定稿 171 行 / 17,567 B**（与 git HEAD 一致）⇒ **按实修正、不改文件内容**。**⚠️ R4 未新增「早报→当日」机械复核对（如实 · 不充数）**：信号面 as-of **仍 2026-09-30** ⇒ `daily k=1` 目标日**仍 2026-10-08**，**该格 R3 已核**（`AM_PM_CHECK.md`）。**`daily/2026-10-09.md` AM 版**（§0 口径块 · §1 盘前信号简报 · §2 昨日复核 · §3 结论 · §4 变更记录〔PM 段待 18:00〕）。**② 第八十一轮常态采集 news +5**（中文 3 / 英文 2）——详见 `news/2026-10-09.md` 与 `daily-memories-news/2026-10-09.md` `[06:00]` 心跳。**③ G2′④**：**本早报轮不做真实重跑**（距 2026-10-08 18:24 仅 **~11.6h < 20h**）⇒ **推迟至 18:00 晚报轮**（届时 ~23.6h）；**06:00 误起的后台 `cycle_run.py` 已终止**；**不刷行、不补记**（§4-9/§4-10 如实）。**非因果 · 非投资建议 · L3 冻结** 口径不变。

- 🔀 **2026-10-08（第 11 批 · R3 · P0 · 18:00 晚报轮 · 同日第二版）** —— ✅ **P0 R3 + 第八十轮 news +2 + `cycle_run.py` 真实重跑**（R3 = 38 标的价格全量刷新 ok=38/fail=0 · 三处窗口口径补丁「价格 ∩ 语料」截断 · `lag_corr.csv` **与 R2 逐字节一致** · 🆕 `am_pm_check.py` → `AM_PM_CHECK.md`〔63 格·未赢基线〕· `INDEX_FILES.md` R3 重登记 · `daily/2026-10-08.md` PM 版 · 台账追加 `18:24` 行〔指纹 `9909e4cddcf525a8`〕）。流水**原文已滚入** `daily-memories-news/2026-10-08.md`（`[18:25]` 心跳；**原文不改 · 结论不变**）。

- 🔀 **2026-10-08（第 11 批 · R2 · P0 · 06:00 早报轮）** —— ✅ **P0 R2（`block_boot.py` 3 组 G1/G2/G3〔G3 = 19/20 CI 跨 0〕+ `FINDINGS.md` + 首份早报 AM + `LAG_CORR.md` R2 头）+ 第七十九轮 news +6**。流水**原文已滚入** `daily-memories-news/2026-10-08.md`（`[06:10]` 心跳；**原文不改 · 结论不变**）。



- **2026-10-07（第 11 批 · R1 · P0）** —— ✅ **新闻信号→资产价格 R1 交付**：`news/signal/` = **PREREG.md（先于结果）+ SOURCE_TEST.md（源实测 ok=38/fail=0）+ fetch_prices.py + prices/〔38 标的/6 类/2016–2026·2.56MB〕+ INDEX_FILES.md + lag_corr.py → lag_corr.csv（23940 格）+ LAG_CORR.md**。**结论（如实·非因果·非投资建议）**：**FDR 后 `q<0.10`=0、`stable`=0**；未校正 `p<0.05`=1217/23940≈5.08%≈随机基线 ⇒ **未发现稳定滞后相关**（负面结果照写）。详见 `daily-memories-news/2026-10-07.md` `[18:00]` 心跳。

- 🔀 **第七十八轮**（2026-10-07 ~08:10，news +1：**IT之家《AI 颠覆担忧消退，美国软件股创 2026 年阶段新高》**〔`010/141`·标普 500 软件与服务指数创 2025-11 以来新高·归第 5 类〕）流水**原文已滚入** `daily-memories-news/2026-10-07.md`（📦 滚动归档 · **2026-10-08 18:40 为 MEMORY ≤ 32KB 归档**；**原文不改·结论不变**）。

- 🔀 **第七十七轮**（2026-10-07 ~07:50，news +3：**IT之家《OpenAI 发布又一批 AI 数学研究成果》**〔`010/137`·722 手稿·归第 1 类〕· **《美国司法部要求员工改称 AI 为「超级智能」》**〔`010/135`·据路透社·归第 3 类〕· **《消息称 SpaceX 计划募资 400 亿美元采购英伟达 AI 芯片》**〔`010/134`·据金融时报·归第 5 类〕）流水**原文已滚入** `daily-memories-news/2026-10-07.md`（📦 滚动归档 · **2026-10-08 18:40 为 MEMORY ≤ 32KB 归档**；**原文不改·结论不变**）。

- 🔀 **第七十六轮**（2026-10-07 ~07:15，news +1：**IT之家《已挖出十几万漏洞，Anthropic 向更多安全团队开放其最强 Claude 模型》**〔Anthropic 正式公布新版「网络核验计划（CVP）」·整合「玻璃翼计划（Project Glasswing）」；合作方 4–7 月至少 129,000 个已核实漏洞·>33,000 严重/高危；三级均开 Claude Opus 5.5 / Sonnet 5.5 / Mythos 5.1；归第 2 类＋关联第 5/1 类〕）流水原文已滚入 `daily-memories-news/2026-10-07.md`（📦 滚动归档 · 第七十七轮 07:50 为 MEMORY≤32KB 归档；原文不改）。

- 🔀 **第七十五轮**（2026-10-07 ~06:39，news +1：**TechCrunch《Ex-Ramp engineers raise $20M for platform Melius…》**〔Ramp 前员工 AI 广告素材生成平台 `Melius` 融资 $25M·$20M A 轮 CRV 领投 ＋ $5M 种子 GC 领投·自称两月年化营收 >$1M；归第 5 类〕）流水原文已滚入 `daily-memories-news/2026-10-07.md`（📦 滚动归档 · 第七十七轮 07:50 为 MEMORY≤32KB 归档；原文不改）。

- 🔀 **第七十四轮**（2026-10-07 ~06:06，news +0：窗口 0.55h 无新 AI 事件 → 如实留空）流水原文已滚入 `daily-memories-news/2026-10-07.md`（📦 滚动归档 · 第七十七轮 07:50 为 MEMORY≤32KB 归档；原文不改）。
- 🔀 **第七十三~六十三轮**（2026-10-07 00:02~05:33，共 **11** 轮；news +7：73 Underdog〔Qwen3.8-27B 端侧隐私助理〕· 72 Musubi `PolicyLM-1.7B`〔开放权重实时审核〕· 71 Lambda 拟融资 $4B〔投前 $14.5B〕· 70 Wajo〔前 DeepMind 工程师 agent 创业·Khosla〕· 67/66/69 窗口无新 AI 事件〔**news +0 如实留空**〕· 65 Mirror Particle「人类行为世界模型」· 64 Google `EmbeddingGemma 2` 〔端侧多模态嵌入〕· 63 Anthropic 赠初创一年 Claude Team + $1,000 credits）流水**原文已滚入** `daily-memories-news/2026-10-07.md`（📦 滚动归档 · **2026-10-08 06:10 为 MEMORY≤32KB 归档**；**原文不改·结论不变**）。

- 🔀 **第六十二轮**（2026-10-06 ~23:33，news +2：IT之家 德国交通部长盼特斯拉 FSD（监督版）获欧盟批准 · TechCrunch：LibreOffice 把「no AI」当特性）流水原文已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 2026-10-07 00:36 为 MEMORY≤32KB 归档；原文不改）。


- 🔀 **第六十一轮**（2026-10-06 ~22:54，news +1：**IT之家《AMD 股价创历史新高！CEO 苏姿丰称 AI 芯片需求非常旺盛，将持续大幅扩产》**〔10-06 22:30:54 CST `010/114`；归第 5 类〕）流水原文已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第六十一轮 22:54 心跳；原文不改）。

- 🔀 **第六十轮**（2026-10-06 ~22:19，news +4：IT之家 Mistral Large 4 公开预览版〔1 万亿总参 / 490 亿激活 · 月底开放权重〕· 英伟达市值 5.8 万亿美元创历史新高 · TechCrunch Pinterest AI Beauty Guides · TechCrunch Flai AI 经销软件〔2,700 万美元 A 轮〕；`SEEN.md` +6）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。


- 🔀 **第五十九轮及更早（第五十九~十九轮 + 第 10 批块）**：流水原文（第五十九轮 news+0 · 第五十八轮 CTV News Claude 救生 · 第五十七轮 SAP 收购 TechWolf · 第五十六轮 谷歌×Constellation 电力协议 / Mistral 预告 / Guardian 品牌风险 · 第五十五轮 404 Media Meta Muse 逃逸 / Osna.FM 德国 MAD / Guardian 抗议 · 第五十四~十九轮 + 第 10 批块）均已滚入 `daily-memories-news/2026-10-06.md`（📦 滚动归档 · 第六十九轮 03:21 / 第七十八轮 08:10 归并；原文不改）。
