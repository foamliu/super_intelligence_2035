# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~二十二轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序已收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库（75,610 条，对 15:10 全量快照）· N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + **§4.4 措辞强度 tone 信号**，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md，9 行）+ **G2′④ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）**
当前动作:     **本唤醒：第二十二轮常态采集（news **+2**：Reuters 挪威拟**临时禁止**公共场所 AI 智能眼镜 · 中新网 藏语大模型 **DeepZang** 迭代推进会）；**上轮**：第二十一轮 +0（国庆源薄）+ 补 G2′④ 台账「连续性自报」行
下一步:       ① 提交本线产物（**不含任何 ≥5MB 文件**）；② **G2′④ 累积**：**隔日（≥20h）**跑真实重跑（`cycle_run.py --with-l2`，**不带 `--record`**）追加台账（**台账自报：连续 1 天 / 目标 7 天，未达标**）；③ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；④ L3（N5）**冻结**
本轮新增:     **第二十二轮常态 news **+2**（中文 1 / 英文 1；当日 26→**28**）**：**Reuters《Norway to propose temporary ban on AI glasses in some public places》**（10-05，挪威拟**临时禁止**部分公共场所 AI 智能眼镜；本机 Reuters 原文不可达，仅凭**标题+链接+HN 日期**核验）· **中新网《中国首个藏语大语言模型 DeepZang 迭代推进会在呼和浩特召开》**（10-05）。`cn_news` 40 条多为假期/民生/时政（唯一 AI 新增=DeepZang）；**央视网 tech 13 条真条目被 `pubDate≤72h` 丢弃**；钛媒体/TechCrunch 新增候选均 feature/同事件 → 去重或不收。累计 **news 97 / 非新闻 50**
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）
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

- **Q（本线主动小结 · 2026-10-05 第4轮）：N1 抓到 2019 了吗？全链对齐全语料了吗？watcher 死锁真修好了吗？**
  **A（本线 2026-10-05 实测）**：
  - **① N1 语料进 2019 ✅**：第 4 轮 `fetch_archive.py --max-seconds 900`（13:26→13:43）→ 游标 `2020-04-19 → 2019-01-24`，**新建 `chinanews-2019.jsonl.gz`（11.46 MB / 259,019 行）**；累计 **1,645,640 条 / 2809 天 / 8 片（2019–2026）**（倒序续抓，终点 `2016-01-01`）。
  - **② 全链重跑对齐全语料 ✅**：`EVENTS.csv` 44,782 → **54,485**（**13.19 MB < 20 MB → 入 git**；sha `6deffc1918f167ef`）；`EARLY_WARNING.md` 45 格 → `q<0.05` **40**、过效果量门槛（`q<0.05` 且 `AUC≥0.60` 且非低频）**18**，样本外 AUC 最高 `A15 货币 Δ=90` **0.791**。口径**未改**（θ=1.0 / BH-FDR / walk-forward），数字变化纯由**语料变长**引起。`explore.csv` sha **不变**属预期（价格窗自 2023-06 起 → 2019–2022 新增事件不入 L2）。
  - **③ watcher 死锁修复 ✅（改判据）**：上轮教训是 `pgrep -f` 自匹配 → 本轮等待条件改为**按 pid 判定** `while kill -0 <pid>; do sleep 10; done`（**永不匹配自身**），抓完才触发 `fetch_archive.py --index` + `cycle_run.py --with-l2`。已实测：第 4 轮抓取结束后 watcher 正常启动并跑完链（`/tmp/n1_chain_r4.log` 尾 `[watcher] ALL DONE`）。
  - **④ G2′④ 台账**：`STABILITY_LOG.md` 第 **5** 行 `2026-10-05 13:45 | 2809 | 1645643 | 54485 | 40 | 18 | `6deffc1918f167ef` | `90f357ff8a8be943` | ok`。「连续 N 周」仍靠**逐周累积**。
  - **⑤ 常态采集**：本轮 **+2**（第十二轮 Hinton RSI + 第十三轮 JEDEC 硅光子）→ 当日累计 **10 条**；`INDEX.md` 累计 **news 79 / 非新闻 35**。


- **Q（本线主动小结 · 2026-10-05）：停摆 27h 恢复后，`news/archive` 语料已到 806,509 条，但 L1 产物还是旧的 —— 处理了吗？G2′④ 有起色吗？**
  **A（本线 2026-10-05 实测）**：
  - **已处理（产物对齐全语料）**：`news/archive` **1627 天 / 806,509 条 / 5 片（2022–2026）**，而 L1 产物尚停在 605,311 条那版 → **全链重跑**：`EDA`(n=806509,days=1627) → `TAXONOMY`(15 类) → `SIGNALS` → **`EVENTS.csv` 31,398 条**（CN 22,904；7.26 MB；sha `9fd3a9670f0a1dde`） → `EARLY_WARNING.md`（45 格）。
  - **`EARLY_WARNING.md` §4.2（全语料）**：`q<0.05` **32/45**；过**效果量门槛**（`q<0.05` 且 `AUC≥0.60` 且非低频）**10/45**；反向（AUC<0.5）如实列出。**口径未变**（预注册 θ=1.0、BH-FDR、walk-forward）—— 数字变化纯由**语料变长**引起。
  - **G2′④ 起色（本轮交付）**：新增 **`news/policy/cycle_run.py`**（一键按序重跑 L1 链并于 `--with-l2` 时带 L2）+ **`news/policy/STABILITY_LOG.md`**（**每次运行自动追加一行**可核验摘要）→ 这就是"**连续 N 周稳定运行**"的**证据台账**。首行：**2026-10-05 12:35 ｜ 1627 天 / 806,509 条 ｜ 事件 31,398 ｜ q<0.05=32 ｜ 门槛=10 ｜ L2=ok**。**后续按周期跑并累积即可过 G2′④。**
  - **🐞 环境修复（新机遗留）**：运行机**无 numpy/scipy、无 pip、无 sudo** → `explore_l2.py` 直接 `ModuleNotFoundError`。已用 `get-pip.py`（`--break-system-packages`）+ **Tuna 镜像**用户级装 **numpy 2.5.3 / scipy 1.18.1** → `explore_l2.py` 复跑成功。⚠️ **建议**：新机 bring-up 清单补一条「python 科学栈（numpy/scipy）」。
  - **口径提示**：`explore.csv` 在扩语料后 **sha 仍为 `90f357ff8a8be943`（字节不变）** —— **属预期**（价格窗自 2023-06 起，**2022 新增事件不入 L2**），已在 `EXPLORE.md`/`README §4` 写明。

- **Q（本线主动小结 · 2026-10-05 第2轮）：语料为何从 806,509 跳到 913,074？有没有被"注水"？G2′④ 台账动了吗？**
  **A（本线 2026-10-05 实测）**：**三件事** ——
  - **① 真实续抓（有效增量）**：`fetch_archive.py` 倒序爬到 **2021-11-12** → **新建 `chinanews-2021.jsonl.gz`** + **补全 2022 全年**（原 2022 只到 `04-21`，现 `01-01~12-31`）。属**真实新增**（✅ 代理源，非新华社）。
  - **② 🐞 本线操作失误：并发双抓 → 重复条目**。上一轮收尾用 `kill -INT <wrapper-pid>` 停抓，**只杀了 bash wrapper、没杀到 python 子进程** → 旧抓仍在跑；我又起新抓 → **两进程同时写同一 shard**，产生 **74,527 行重复**（2021 片 ~49% 重复、2022 片 ~16%）。
  - **③ 处置（未新增脚本）**：用既有 **`fetch_archive.py --repair`**（本就 **按 `url` 去重 + 修 URL**，幂等）→ 六片**去重后唯一 url = 913,074**，全片 `gzip -t` 通过、**0 坏行**。清洗后行数 = `--stats` 计数，二者一致。
  - **G2′④ 台账**：`cycle_run.py`（本轮未带 `--with-l2`）追加第 3 行 **`2026-10-05 12:49 | 1788 | 913074 | 34569 | 34 | 15 | 11b168a45e7e48bc`**（L2 记 `not-requested`，因 `explore.csv` 不受 2021-22 事件影响 → 无需重跑）。**「连续 N 周」仍需逐周累积。**
  - **教训（已写进本节与流水）**：**停后台抓取要杀 python 子进程**（`pkill -f 'python3 news/archive/fetch_archive.py'`，或 `kill $(pgrep -f 'python3 news/archive/fetch_archive.py')`），**别只杀 wrapper**；**同一 shard 严禁并发写**。

- **Q（本线主动小结 · 2026-10-05 第3轮）：为何后台 watcher 挂了 10 分钟没动静？G2′④ 台账与全链是多少？**
  **A（本线 2026-10-05 实测）：**
  - **① 🐞 watcher `pgrep -f` 自匹配死锁（本线操作失误）**：上一轮把「等 fetch 结束再跑链」写成 detached `bash -c 'while pgrep -f "python3 news/archive/fetch_archive.py" >/dev/null; do sleep 5; done; …'`。`pgrep -f` 匹配**整条命令行**，而**该 bash 自身 cmdline 就含这个字符串** → **永远匹配到自己** → 循环**永不退出**、链**永不启动**（fetch 12:59 起跑、13:14 `[done] total=1288020` 已结束，watcher 仍在睡）。
  - **② 处置**：`kill -TERM 124251 124250` 停掉死锁 watcher → 手动 `fetch_archive.py --index` → `nohup python3 news/policy/cycle_run.py --with-l2`（13:15 起、13:19 完）。
  - **③ 全链实测**：`days=2358 recs=1288023 → EVENTS 44782 → q<0.05=39 gate=14 l2=ok`；`STABILITY_LOG.md` 第 4 行 `2026-10-05 13:19 | 2358 | 1288023 | 44782 | 39 | 14 | `afdc41346dd1bae7` | `90f357ff8a8be943` | ok`。`EVENTS.csv` **10.90 MB（<20 MB → 入 git）**；`explore.csv` sha **不变**（价格窗 2023-06 起 → 2020/21 事件不入 L2，属预期）。
  - **教训（已进快照/阻塞行）**：**勿用 `pgrep -f <脚本名>` 做「等某进程结束」的条件**（会自匹配 wrapper cmdline）；**按 pid 判定**（`kill -0 <pid>` / `wait <pid>`），或 `pgrep -f` 时**排除自身**（加 `-a` 过滤 PID / 用 `-x`）。

- **Q（本线主动小结 · 2026-10-04）：为何 `EARLY_WARNING.md` §4.2 的预警结论比上一版「收敛」了很多？是不是调低了标准？**
  **A（本线 2026-10-04 实测）：不是调标准，是修掉一个真 bug —— 上一版结论本身是错的。** 两件事：
  **① 语料/事件**轴**不对齐（主因）**：N1 语料已扩到 **1296 天（2023-03-18~2026-10-03）**，但 `EVENTS.csv` 只覆盖 **2024-04-13 起**；旧脚本评估轴取**语料全程** → 前 ~380 天「有信号列、但**标签恒为 0**」→ 伪造海量全零负样本 → **AUC 被系统性抬高**（旧版好几个格 AUC 冲到 0.9+，是假的）。已加**轴对齐护栏**：评估窗口 = 语料范围 ∩ 事件日期范围。
  **② §4.2 结论原来是写死的**：旧文案硬编码「只有少数稳」，与实测（BH 后 **34/45** 已显著）**自相矛盾**。现改为**数据驱动**（全部由当次实测生成）+ **效果量门槛**（**q<0.05 且 AUC≥0.60 且非低频类**）。
  **修复后实测**：45 格中 **34** 原始 `p<0.05`、**34** 过 BH（`q<0.05`）；但**只 8 格**通过效果量门槛 → 才是真正的「可预警候选」（最好约 **A15 货币 Δ=30 AUC 0.648 / A2 出访 Δ=7 0.639 / A6 部署 Δ=90 0.638**）。另有 **9 格 AUC<0.5（反向）**，如实列出。
  **关键提醒（已写进产物）**：`q<0.05` **只证明「非随机」，≠「可预警」**；本设置 N 大 + 政治动作**成簇自相关** → **多数格天然显著**；信号本质是**「活动聚簇/持续性」弱信息**，🚫 **不是「预测新起点」**。**低频类**（样本 <5）只作案例、不入显著结论。**（若后续要「分族」校正，须事先登记，不得事后换族凑显著。）**

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
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-05 13:15 CST` 第十一轮 ~ `2026-10-05 19:16 CST` 第二十二轮
- **累计收录**：`147` 条（**news 97**〔第一~二十二轮；当日 28〕+ 非新闻 50〔仅存 `SEEN.md`〕）

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-05（本唤醒 ~19:16）** —— 🆕 **第二十二轮常态采集：news +2（中文 1 / 英文 1）**。
  - **① Reuters《Norway to propose temporary ban on AI glasses in some public places》**（2026-10-05）：据路透社报道（经 Hacker News 索引，HN story id `49963007`，发布 `2026-10-05T10:25:29Z`），挪威政府拟提出**临时禁令**，禁止在部分公共场所使用 **AI 智能眼镜**。⚠️ **本机无法抓取 Reuters 原文**（`fetch` 超时，历史一致）→ 仅凭**标题 + 链接 + HN 日期**核验（正文细节未取得，如实标注，不臆测）。→ 关注清单第 3 类「政策与治理」。
  - **② 中新网《中国首个藏语大语言模型 DeepZang 迭代推进会在呼和浩特召开》**（2026-10-05）：中国首个藏语大语言模型 **DeepZang** 的「升级迭代及同声传译研发推进会」近日在内蒙古呼和浩特举行（中新网拉萨 10-05 19:10 电，作者万纪玮）；报道称藏语因结构特殊/方言差异/语料稀缺属 NPL 低资源难题，DeepZang 在多方言适配、语义精准识别、离线场景应用持续优化，将融入公共服务、教育医疗、文旅、基层治理；DeepZang 创始人旦增罗布出席。→ 关注清单第 1 类「模型与能力」。
  - **源盘点（如实）**：`cn_news` 40 条多为**国庆假期/民生/时政**（高速拥堵、AG600、中网、诺奖、南部战区正告菲方、横店入境游…；唯一 AI 新增 = DeepZang）；**央视网 tech 13 条真条目被 `pubDate≤72h` 丢弃**（锂电正极 82.2h、新恐龙 104.0h、人造太阳 109.0h…）；**联合国中文源仍 `HTTP 404`**（判源失败）；量子位头部均已在账；IT之家头部为游戏/汽车/消费电子（华为×高通 `009/852` 同事件 → 去重）；钛媒体新增 feature/opinion/analysis 仅存 `SEEN.md`；TechCrunch 新增候选（Amazon 数据中心、OpenAI 安全员工离职）均同事件/feature → 去重或不收；`search_news`(HN) 唯一新 §0.1 = 挪威禁 AI 眼镜；`web_search`(CN-Bing) 无有效召回归。
  - **G2′④**：本轮距上次真实重跑（15:10）约 **4.1h <20h** → **不刷台账连续性**；自报维持 **已连续 1 天 / 目标 7 天 · ⚠️ 未达标**（如实写）。
  - **文档同步**：`news/2026-10-05.md`（第二十二轮段）· `news/SEEN.md`（+2 news）· `news/INDEX.md`（当日 26→**28** / 累计 news 95→**97**）· `MEMORY_NEWS.md`（快照 + 本流水）· 日流水心跳行 `[19:16]`。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**（未产出任何策略/仓位/择时）。

- **2026-10-05（本唤醒 ~18:45）** —— 🎯 **补 G2′④ 台账缺口（`cycle_run.py` 新增「连续性自报」行）+ 第二十一轮常态采集（news +0，如实）**。
  - **动机**：任务书 §0.0.2 **G2′④ 2026-10-05 修订口径**要求台账**必须自报「已连续 X 天 / 目标 7 天」**，而原 `STABILITY_LOG.md` 无此字段（只有逐行记录）。
  - **实现（`news/policy/cycle_run.py`）**：新增 `_iter_rows / _is_real / compute_streak / update_streak_line` —— 按**修订口径**（连续 7 **自然日**、每日 ≥1 次**真实重跑**、相邻 **≥20h**、**同天多次只计 1 天**、`record-only` **不计入**）**由台账真实行自动推算**；每次运行**重写文末**「G2′④ 连续性自报」行（🚫 不补造、不手填）。`--record` 跑通：`strk=1/7`（现全部真实行同为 2026-10-05 → 计 1 天）。表头口径同步更新（「连续 N 周」→「连续 7 自然日」）。
  - **第二十一轮常态采集（news +0）**：`cn_news`（中新网×3 + 央视网 news/tech）命中均假期/民生/时政 → 不收；**央视网 tech 13 条真条目被 `pubDate≤72h` 丢弃**（含《生成式AI用户规模突破7亿人》超龄 142h）；**联合国中文源仍 `HTTP 404`**；量子位头部均已在账；IT之家《高通×华为逻辑折叠芯片专利授权》与在账 `009/806` **同事件** → 去重；钛媒体新增 1 feature + 2 analysis 仅存 `SEEN.md`；TechCrunch《Google 冻结漏洞赏金》已在账；The Register atom 仍 ParseError。当日维持 **26**（累计 news 95 / 非新闻 50）。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。
  - **未做**：真实重跑（距上次 15:10 **<20h** → **不刷连续性**）。


- **2026-10-05（本唤醒 ~17:55）** —— 🆕 **第二十轮常态采集：news +1（英文 1 / 中文 0）**。
  - **① TechCrunch《Federal judge calls Flock 'indiscriminate mass surveillance'》**（2026-10-03）：TechCrunch 报道，一名联邦法官裁定，某县治安官副手在**未取得搜查令**的情况下使用 AI 车牌识别/监控系统 **Flock** 搜索一名女性的车牌，**侵犯其第四修正案权利**；法官将 Flock 定性为「**无差别的大规模监控**」。→ 关注清单第 4 类「AI 与社会（伦理 / 公民权利 / 公众态度）」。
  - **源盘点（如实）**：`cn_news` 30 条均**国庆假期 / 民生 / 时政**（横店入境游、悉尼持刀、缅北电诈、四川高铁、2026 诺贝尔生理学奖、南部战区正告菲方……）→ 非关注清单 → **不收**；量子位头部 8 条**均已在账**；IT之家《高通与华为逻辑折叠芯片专利授权》（`009/852`）与在账《华为×高通广泛专利许可协议》（`009/806`）**疑同事件** → 去重跳过；《阿里千问 AI 耳夹式耳机》（`009/846`）判**消费电子** → 不收；**钛媒体新增 2 条 analysis**（纳指/A股硬科技 `8159517`、快手视频 Agent `8159522`）仅存 `SEEN.md`；爱范儿《OpenAI 元老离职信》**同 Guardian 在账事件** → 去重；`search_news`(HN) 8 条均 **opinion / blog / 超窗** → 不收。
  - **源健康度（如实记录）**：The Register `headlines.atom` → **ParseError**；**Guardian `technology/rss` → 本机构网络不可达**（`Errno 101`，**判源失败，未静默当「无新增」**）；Ars / WIRED feed `200` 但当日头条**非 AI** → 不收；中新网 / 央视网 / 量子位 / IT之家 / 爱范儿 / 雷峰网 / 钛媒体 / TechCrunch feed 均 **200**。GDELT 未用（省额度）。
  - **G2′④**：本轮距上次真实重跑（15:10）**仅 ~2.8h（<20h）** → **不刷台账**；连续天数仍 = **1 天**（目标 7 天，**未达标**，如实写）。
  - **文档同步**：`news/2026-10-05.md`（第二十轮段）· `news/SEEN.md`（+1 news / +2 非新闻）· `news/INDEX.md`（当日 26 / 累计 news 95 · 非新闻 47）· `MEMORY_NEWS.md`（快照 + 本流水 + 滚动归档）· 日流水心跳行 `[17:55]`。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**（未产出任何策略/仓位/择时）。


- **2026-10-05（本唤醒 ~17:25）** —— 🆕 **第十九轮常态采集：news +2（英文 1 / 中文 1）**。
  - **① TechCrunch《Trump unveils his new Super Intelligence Force》**（2026-10-04）：特朗普 10-04 在 Truth Social 宣布组建「**超级智能部队**」（Super Intelligence Force），据 WSJ 由国家情报总监 **Jay Clayton** 任主席（FTC 主席 Ferguson、国防部 Emil Michael、OPM Kupor 任副主席），负责协调联邦政府确保美国在「超级智能」领先，章程要求 **120 天**内提交风险/机遇报告（承接 9 月「AI→SI」行政令叙事）。
  - **② 钛媒体《马斯克为 AI 改名：SpaceXAI 将更名 SpaceXSI》**（2026-10-05）：马斯克 **10-04** 在 X 上确认将 **SpaceXAI → SpaceXSI**（「AI」换「SI」），称「SpaceX 是一家超级智能公司」；⚠️ 文中为「钛度号」作者专栏（含分析），**核心新闻点 = 马斯克 X 表态**；截至报道官方**未公布生效时间**。
  - **源盘点（如实）**：**新试 `tmtpost.com/rss` = 活源**（带 pubDate、当日更新）；`cn_news` 40 条均假期/民生/时政 → 不收；量子位头部 10 条**均已在账**；IT之家头部为消费电子/汽车/游戏 → 不收（鸿海营收仍判非清单）；雷峰网头部软文/文体/法律 → 不收；The Register `headlines.atom` 与机器之心 `jiqizhixin.com/rss` 均 **ParseError**；HN 8 条均 opinion/超窗 → 不收；联合国中文源仍 **404**。非新闻 4 条（钛媒体 analysis）**仅存 `SEEN.md`**。
  - **文档同步**：`news/2026-10-05.md`（第十九轮段）· `news/SEEN.md`（+2 news / +4 非新闻）· `news/INDEX.md`（当日 25 / 累计 news 94 · 非新闻 45）· `MEMORY_NEWS.md`（快照 3 行 + 累计 + 本流水）· 日流水心跳行 `[17:25]`。
  - **判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 非新闻单列（仅存 `SEEN.md`，不入摘要）· ✅ 「我们的观察」措辞明确标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**（未产出任何策略/仓位/择时）。
  - **未做**：G2′④ 连续天数累积（需**隔日 ≥20h** 的真实重跑；本轮与上轮间隔不足 → **不刷台账**，连续天数仍 = **1**，如实标 **未达标**）。

- （更早流水：**2026-10-05 16:12 第十六~十七轮**（L1 §4.3 固定召回率 precision 加固 + IT之家索尼×Meta 专利）→ 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-05 早期**（恢复 27h 停摆首轮 · N1 2021/2022 续抓）· **N1 第 3/4/5/6 轮抓取（2020→2019→2017/2018→2016）+ 第十一~十五轮常态采集 + 全链重跑** → 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-03 各轮 / 2026-10-04 各轮**（L1/N3 收口、N4/L2、L1 链重跑+轴对齐）→ `daily-memories-news/2026-10-03.md` · `daily-memories-news/2026-10-04.md`；第三~九轮 / 第二轮 / 首轮 smoke / 前期任务 T1–T4 / 建线 / 首轮空转 亦在其中）

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
