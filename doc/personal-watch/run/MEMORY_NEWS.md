# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 0

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~十一轮常态 ✅ · **N1 抓取器 + 语料（2358 天 / 1,288,020 条 / 7 片 2020–2026，游标 `2020-04-19`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库（44,782 条）· N3-4 预警方案 · L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md，4 行）**
当前动作:     **N1 续抓 900s**（`2021-07-14 → 2020-04-19`：新建 `chinanews-2020` 片，183,772 条）→ 全链重跑对齐全语料（EDA→TAXONOMY→SIGNALS→**EVENTS 44,782**→EARLY_WARNING 45 格 `q<0.05`=**39**、门槛=**14**）；🐞 **修复 watcher `pgrep -f` 自匹配死锁**（等待条件命中自身命令行 → 永不退出）；**并补做第十一轮常态采集（news 8 条）**
下一步:       ① **N1 续抓**（`fetch_archive.py --max-seconds …`，倒序 `2020-04-19 → 2016-01-01`）→ 抓够再重跑链并记台账；② **G2′④ 累积**：按周期 `python3 news/policy/cycle_run.py --with-l2` 追加 `STABILITY_LOG.md`；③ L1 稳定性 / 组合规则 + 纳入 SIGNALS 措辞信号；④ L3（N5）**冻结**
本轮新增:     **N1 语料 984,298 → 1,288,020 条（+303,722；7 片，新增 2020 片）**；全链重算：`EVENTS.csv` 34,569 → **44,782**（10.90 MB，sha `afdc41346dd1bae7`）；`EARLY_WARNING.md` 45 格 `q<0.05` 34→**39**、效果量门槛 15→**14**；**`STABILITY_LOG.md` 新增第 4 行（13:19）**；**news 日报 8 条（中文 6 / 英文 2）**；🐞 修 2 个 bug（见运维问答）
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **`pgrep -f <脚本名>` 会自匹配 wrapper 命令行** → 勿用该写法做等待条件）
ERROR_COUNT:  3（历史：模型名白睡一轮，已修；并发双抓重复，已修；**本轮：watcher `pgrep -f` 自匹配死锁 → 已 kill 并改人工跑链**）
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

- **Q（supervisor 记忆 §4 挂起项 · 2026-10-03）：MCP 是否真装进运行机 cline？**
  **A（本线 2026-10-03 实测）：未装。** 运行机上 `~/.cline/data/settings/` 只有 `cli-notices.json` + `providers.json`，**无 `cline_mcp_settings.json`**；`find ~/.cline -iname '*mcp*'` 无结果 → cline 会话**没有** `web_search`/`search_news`/`rss_latest` 这三个 MCP 工具（`web-search-free` 字样只出现在会话消息日志里，不在任何配置）。
  **对本线影响：无。** 本线取数改为**直接调用交付的 Python 模块**：`cd run/news && python3 -c "import mcp_web_search_free as m; print(m.search_news('AI regulation',5))"`（本轮 15 条即如此取得，链路实测可用）。
  **若要装 MCP（供 cline 工具化调用）**：把 `run/news/cline_mcp_config.json` 的 `mcpServers['web-search-free']` 并入运行机 cline 的 `cline_mcp_settings.json`（`command`=`python3`，`args`=`["/home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/mcp_web_search_free.py"]`）；⚠️ 需 loop 重启 / cline 重载 MCP 才生效（是否重载由 supervisor 定）。

- **Q（第 6 批 T10 · 2026-10-03）：`fetch_cn_news()`（中文活源统一入口）是否落地？确切怎么用？**
  **A（本线 2026-10-03 实测）：已落地并实跑。** 实现于 `news/mcp_web_search_free.py`：`fetch_cn_news()` / `cn_news_report()` + **MCP 工具 `cn_news`** + **CLI `--cn-news`**（两种调用方式齐备）。
  - **确切命令**：`cd run && python3 news/mcp_web_search_free.py --cn-news --limit 30`（人类可读）／ `… --cn-news --limit 30 --json`（JSON）。
  - **实测结果**：**6 个活源全部 200** → **命中 30 条**（`lang=zh type=news`，按 `published` 倒序）；**丢弃 83 条**（超龄 >72h）。各源新鲜度：中新网×3 kept=30/30/30 · 联合国·中文 kept=18(drop 12) · 央视网 news_1 kept=80 · 央视网 tech_1 kept=9(drop 71)。
  - **用法 + 返回结构 + 自测原始输出**：见 `news/FETCH_CN_NEWS.md`。

- **Q（第 9 批 N4 · 2026-10-03）：G2「准备项」做到哪一步？价格源在运行机通吗？**
  **A（本线 2026-10-03 实测）**：
  - **① 价格源运行机复测 ✅**：腾讯实时 `qt.gtimg.cn` **200** · **腾讯日K `web.ifzq.gtimg.cn/appstock/app/fqkline/get` 200（JSON）** · 新浪 `hq.sinajs.cn`（需 `Referer`）**200**；**东财日K `push2his.eastmoney.com` ❌ 运行机 TLS 被重置**（`TLS alert, decode error (562)`，HTTP 000）→ **历史日线改走腾讯**。
  - **② 方法预注册 ✅** → `news/policy/L2_PREREG.md`（事件窗 `[-1,+1]/[-5,+5]/[+1,+20]`；基准=**指数调整 + 市场模型**；`t` 检验 + bootstrap CI；**FDR 校正**；四坑逐条）。
  - **③ 事件源 `EVENTS.csv`（N3-3）尚未就绪 → 未过 G2 → L2 不产出任何结论**（N4 目前**只做"准备"，不跑 CAR**）。〔**2026-10-04 更新**：事件库已就绪，见下条〕

- **Q（第 9 批 N4 · 追问 2026-10-04）：N4 产出了吗？G2 过没过？**
  **A（本线 2026-10-04）**：
  - **G2 全过**：① 价格源运行机复测 ✅ ② 方法预注册 `L2_PREREG.md`（§2.2–§2.9 跑前写死，含板块清单/对齐聚合）✅ ③ 产出**默认只做描述性统计**（分布 / 均值·中位数 / **自助法 95% CI** / **N**），显著性**必 FDR 校正** ✅。
  - **N4 产出 ✅**：`news/policy/EXPLORE.md` + `news/policy/explore.csv`（1170 格）—— **动作类型(15)×板块(13)×窗口(3)** 的描述性 **CAR** + **FDR(BH) 按基准分族校正** + **四坑逐条**（预期 `flag_expected` / 反向因果关键词 / 同期拥挤日 `frac_crowded_days` / 多重比较）+ **能力边界**。
  - **如实负面/局限**：FDR(q<0.05) 显著格 指数调整 176 / 市场模型 16（族内 ~585）；**两种基准符号相反 133 格** → 结论**对基准选择敏感**；`EVENTS.csv` 抽检 precision≈80% 噪声会**稀释**关联（偏保守）。
  - **复现**：`python3 news/policy/explore_l2.py` → `explore.csv` **重跑字节一致** `cc6058305bbe8d61`（种子 `SEED=20351004`，自助法 5000 次）。
  - **红线复核**：全文**无因果措辞**（`影响/导致/利好/利空/冲击` 仅出现在**免责声明/禁用说明**中）；**🚫 不声称因果**；✅「没找到稳定关联」如实保留；**非投资建议**。
  - **N1 同步续抓**：语料 904 → **1194 天 / 557,197 条**（新增 2023 片，取到 `2023-06-27`）。

---

## 1. 状态头

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **N1 语料库**：`news/archive/chinanews-<年>.jsonl.gz`（只 5 字段；**仅取 标题+日期+来源+链接，不抓正文**）；现 **2358 天 / 1,288,020 条 / 7 片**（**2020-04-19 ~ 2026-10-03**；游标 `2020-04-19` → `2016-01-01`）
- **L1 产物**：`news/policy/`（`EDA.md` / `TAXONOMY.md` / `SIGNALS.md` / `EVENTS.csv` / `EARLY_WARNING.md` / **`cycle_run.py` + `STABILITY_LOG.md`（G2′④ 运行台账）**）
- **L2 产物（探索性 · 非因果）**：`news/policy/`（`L2_PREREG.md` / **`EXPLORE.md` + `explore.csv`**）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-04 06:50 CST` 第十轮 ~ `2026-10-05 13:15 CST` 第十一轮
- **累计收录**：`108` 条（**news 77**〔第一~九轮 61 + 第十轮 8 + 第十一轮 8〕+ 非新闻 31〔仅存 `SEEN.md`〕）

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-05** —— 🆕 **N1 续抓进 2020（+303,722 条 / 7 片）+ 全链重算 + 修复 watcher `pgrep -f` 死锁 + 第十一轮常态 news 8 条**。
  - **后台 N1 抓取（第 3 轮）**：`fetch_archive.py --max-seconds 900`（12:59 起、13:14 止）→ 游标 `2021-07-14 → 2020-04-19`，**新建 `chinanews-2020.jsonl.gz`（183,772 条）**；累计 **1,288,020 条 / 2358 天 / 7 片（2020–2026）**，`--index` 重生成 `archive/INDEX_FILES.md`（各片均 <20 MB）。
  - **🐞 修复 watcher `pgrep -f` 自匹配死锁**：等待条件 `while pgrep -f "python3 .../fetch_archive.py"` **命中自身 bash cmdline** → 永不退出 / 链不启动；`kill -TERM 124251 124250` 后**改为人工跑链**（详见运维问答第 3 轮）。
  - **全链重跑对齐全语料**：`cycle_run.py --with-l2`（13:15→13:19）→ `eda.py`(n=1,288,023, days=2358) → `taxonomy.py` → `signals.py` → `extract_events.py`（**44,782 事件**，`EVENTS.csv` **10.90 MB**，sha `afdc41346dd1bae7`）→ `early_warning.py`（45 格 `q<0.05` **39**、效果量门槛 **14**）→ `explore_l2.py`（ok；`explore.csv` sha **不变**属预期）。
  - **G2′④ 台账**：`STABILITY_LOG.md` 追加**第 4 行（13:19）**；「连续 N 周」仍靠**逐周累积**。
  - **常态采集（第十一轮）**：`news/2026-10-05.md` **news 8 条（中文 6 / 英文 2）**；`SEEN.md` +8 news / +5 非新闻；`INDEX.md` 累计 **news 77 / 非新闻 31**。⚠️ **联合国新闻·中文源本轮 404**（如实记录）；GDELT 限频未用。
  - **文档同步**：`MEMORY_NEWS.md` 快照/运维问答/流水；`news/policy/README.md` §4。
  - **未做**：L3 冻结。判据复核：无因果措辞、低频单列、非投资建议。

- **2026-10-05** —— 🆕 **N1 续抓（新增 2021 片 + 补全 2022）+ 全链重跑 + 修复并发双抓重复**。
  - **N1 续抓**：`fetch_archive.py --max-seconds 300`（≥2s/req）→ 游标 `2022-04-20 → 2021-11-12`；**新建 `chinanews-2021.jsonl.gz`**（28,886 条）+ **补全 2022 全年**（161,166 → 238,861 条）；语料 **806,509 → 913,074 条 / 6 片**（2021–2026）。
  - **🐞 并发双抓 bug（本线操作失误）**：停上一轮抓取时 `kill -INT <wrapper-pid>` **只命中 bash wrapper、未命中 python 子进程** → 旧抓未停，我又起新抓 → **两进程同写同一 shard**，产生 **74,527 行重复**。
    - **修复**：跑既有 **`fetch_archive.py --repair`**（按 `url` 去重 + 修 URL，幂等，18s）→ 去重后六片**唯一 url = 913,074**，`gzip -t` 全通过、0 坏行；`--stats`/`--index` 重生成（`INDEX_FILES.md` 6 片，均 <20 MB）。
    - **教训**：**停后台抓取要杀 python 子进程**（`pkill -f 'python3 news/archive/fetch_archive.py'`）；**同一 shard 严禁并发写**。
  - **全链重跑对齐全语料**：`cycle_run.py`（纯 L1 链）→ `eda.py`(n=913074, days=1788) → `taxonomy.py` → `signals.py` → `extract_events.py`（**34,569 事件**，`EVENTS.csv` **8.39 MB**，sha `11b168a45e7e48bc`）→ `early_warning.py`（45 格 `q<0.05` **34**、效果量门槛 **15**）。
  - **本轮末再抓 240s**（**单进程**，`fetch_archive.py --max-seconds 240`，启动后核对 **pid 唯一**）→ 游标 `2021-11-12 → 2021-07-14`，**+71,224 条 → 984,298 条**（`--stats` 唯一计 **984,295**）；`--index` 已重生成。
    - ⚠️ 注：本轮的 L1 产物（**EVENTS 34,569**）对齐的是 **913,074 快照**；抓够后需**再重跑链**对齐。
  - **G2′④ 台账**：`STABILITY_LOG.md` 追加第 3 行 `2026-10-05 12:49 | 1788 | 913074 | 34569 | 34 | 15 | 11b168a45e7e48bc | … | not-requested`。
  - **L2/N4**：`explore_l2.py` 重生成 `EXPLORE.md`（事件数 → 34,569；`explore.csv` 预期**字节不变**——价格窗自 2023-06 起，2021-22 事件不入 L2）。
  - **文档同步**：`news/policy/README.md` §4/§4.1 更新（语料/事件数/门槛数）。
  - **未做**：**常态采集**（news 日报 0 条，专注 N1 + 修 bug）；L3 冻结。判据复核：无因果措辞、低频单列、非投资建议。
- **2026-10-05** —— 🆕 **恢复 27h 停摆后首轮：L1 链对齐全语料 + 建 G2′④ 运行台账 + 修复 numpy 缺失**。
  - **核对（发现产物 stale）**：`news/archive` 已 **1627 天 / 806,509 条 / 5 片**（2022–2026，游标 `2022-04-20`），而 L1 产物停在 605,311 条那版 → 全链重跑。
  - **L1 链全量重跑**：`eda.py`(n=806509,days=1627) → `taxonomy.py`(15 类) → `signals.py`(128 行) → `extract_events.py`（**31,398 事件**，CN 22,904；`EVENTS.csv` 7.26 MB，sha `9fd3a9670f0a1dde`）→ `early_warning.py`（283 行）。
    - `EARLY_WARNING.md` §4.2：**45 格** → `q<0.05` **32**；过**效果量门槛** **10**；反向格（AUC<0.5）如实列出。口径**未改**（θ=1.0 / BH-FDR / walk-forward），差异纯由语料变长引起。
  - **🆕 交付（G2′④ 证据）**：`news/policy/cycle_run.py`（纯 stdlib，按序重跑 L1 链；`--with-l2` 带 L2；`--record` 只记当前态）+ `news/policy/STABILITY_LOG.md`（每次运行自动追加一行可核验摘要）。**首行**：2026-10-05 12:35 ｜ 1627 天 / 806,509 条 ｜ 事件 31,398 ｜ q<0.05=32 ｜ 门槛=10 ｜ L2=ok。（自检修复：`--record` 回退解析 `EDA.md` 的中文格式 → 复测记 `days=1627 recs=806509`）
  - **🐞 环境修复**：运行机缺 **numpy/scipy**（且无 pip/sudo）→ `explore_l2.py` 报 `ModuleNotFoundError`；用 `get-pip.py --break-system-packages` + **Tuna 镜像**装 **numpy 2.5.3 / scipy 1.18.1**（用户级 `~/.local`）→ **L2 复跑成功**。
  - **L2/N4 重生成**：`EXPLORE.md` 事件数 → **31,398**（可对齐 23,105）；`explore.csv` **sha 不变**（价格窗 2023-06 起，2022 事件不入 L2，**属预期**）。
  - **文档同步**：`news/policy/README.md` §4/§4.1 更新；`INDEX_FILES.md` EVENTS.csv 行更新。
  - **未做**：**N1 续抓**（下一轮 `fetch_archive.py --max-seconds …`）、**常态采集**（news 日报 0 条）、L3 冻结。判据复核：无因果措辞、低频单列、非投资建议。
- **2026-10-04** —— 🆕 **N4（L2 探索性关联分析）交付 + N1 续抓进 2023 年（G2 全过）**。
  - **N4 两产物**：`news/policy/EXPLORE.md` + `news/policy/explore.csv`（生成器 **`news/policy/explore_l2.py`**，新脚本）。
    - **方法**（**预注册** `L2_PREREG.md` §2.2–§2.9，跑前写死）：事件源 `EVENTS.csv`（18,232 条）；价格源 **腾讯 `web.ifzq.gtimg.cn`（qfq 日K）**（东财运行机 TLS 复位→弃）；**板块 13 × 动作类型 15 × 窗口 3**；基准 = **指数调整 + 市场模型**两种；**按事件日聚合**（同日多事件取均值，防重复计数）→ 日级 CAR → `t` 检验 + **自助法 5000 次 95% CI**；**N = 事件日数**；**FDR（BH）按基准分族**校正。
    - **四坑逐条**：① 预期窗 `[-10,-1]` p<0.1 的格 **79**（标 `疑似已预期`）② 反向因果：稳市场类关键词占比（按类型，最高 A3 1.2%）→ 标注**不得当外生事件** ③ 同期拥挤日（单日事件中位数 **27**、90 分位 **48**）→ `frac_crowded_days` 列 ④ 多重比较：585 格/基准 → FDR。
    - **如实结果**：FDR(q<0.05) 显著格 指数调整 **176** / 市场模型 **16**；两基准符号一致 **452** / 相反 **133**（后者多 |CAR|≈0，**对基准敏感**）。措辞**只用 相关/同期/滞后/共现**。
    - **可复现**：`sha256(explore.csv)` 前16 = **`cc6058305bbe8d61`**，**重跑字节一致**（种子固定、无网络依赖）。
  - **N1 续抓**：`fetch_archive.py --max-seconds 900`（≥2s/req）→ 语料 **904 → 1194 天 / 420,828 → 557,197 条**；**新增 2023 片** `chinanews-2023.jsonl.gz`（86,699 行 / 3.87 MB）；游标 `2026-10-03 ← 2023-06-27 → 2016-01-01`（0 失败 / 0 空页）。⚠️ **停抓用 PID 精确 `kill -INT`**；`--stats`/`--index` **不与抓取并发**。
  - **阶段门**：**G1 全过**；**G2（L2 自身门槛）①+②+③ 全过 → N4 放行**；**G2′ ④「连续 N 周稳定运行」⬜**（= 下一步）；**G3（L3 解冻）❄️ 未过**。
  - **未做**：常态采集（专注 L2/N1）；L3（N5）冻结。**判据复核**：N4 全文无因果措辞（仅免责声明列禁用词）、给 CI + N、多重比较已校正；N1 语料 5 字段齐全、可回溯 `url`。
- **2026-10-04** —— 🆕 **L1/N3 收口：③ 信号 + ④ 事件库 + ⑤ 预警方案（G1 全过）**。
  - **③ `SIGNALS.md`**（生成器 `news/policy/signals.py`）：先行信号清单（**① 措辞强度词表 · ② 词频/新词首次出现 · ③ 主题通稿密度 · ④ 版面（`channel` 代理） · ⑤ 评论体标记 · ⑥ 口径变化月度趋势**），每条给**可操作提取方法 + `as-of`（=发布日，无滞后）**。
  - **④ `EVENTS.csv`（18,232 条）+ `EVENTS.md` + `EVENTS_AUDIT.csv`**（生成器 `extract_events.py`，**纯词典/正则规则**；⚠️ 本环境**无 LLM key** → ② LLM 分类**未接入**，由 ③ 抽样校验顶替）。**抽样人工校验 100 条 → precision 80%**（见 `EVENTS.md` §5）。字段：`日期·主体·动作类型·领域·力度·依据标题·url`。
  - **⑤ `EARLY_WARNING.md`（新产物）**（生成器 **`early_warning.py`（新脚本）**）：`信号 → P(活跃度高于常态) + 时间窗`（Δ=7/30/90）；**预注册固定规则**（θ=1.0，**无拟合参数→无前视**）+ **样本外** + **4 类基线**（随机/气候多数类/恒正/恒负）+ precision/recall/F1/**AUC**/**提前期** + 自助法 95% CI。
    - **关键设计（如实）**：标签用「未来 Δ 天活跃度 **> 气候期望**」（**非退化**）；若用「**是否发生**」→ 高频类基准率 **≈1.00 退化**（见其 §2.1）。
    - **如实负面结果**：若把 θ 交给「训练段 F1 最优」，**84% 训练段退化选到 θ=0（恒正）** → 故改用**预注册固定 θ**（见其 §4.0）；**部分类型 AUC≈0.5 未胜出基线**，同样列出。
    - **最好**：`A8 讲话 Δ=7` AUC **0.669**；`A2 出访 Δ=30` ΔP **+0.24**（探索性）；**高频可建模、中频部分可用、低频仅参考**。
  - **重跑对齐**：`eda.py`/`taxonomy.py`/`signals.py`/`extract_events.py`/`early_warning.py` **全部重跑** → 统一 **904 天 / 420,828 条**（`EVENTS.csv` sha 不变 `f1444c915d545238`，确定性可复现）。核对：独立复算 `A8 Δ=7`/`A2 Δ=30` 等格与产物**一致**。
  - **阶段门**：**G1 ①②③④ 全过**；**G2′ ①②③ ✅、④「连续 N 周稳定运行」⬜**（= 下一步）。
  - **未做**：常态采集（专注 L1/N3）；**L2（N4）不产出结论**（受 **G2 门**约束）；**L3（N5）冻结**。判据复核：语料 5 字段齐全、可回溯 `url`；预警**只给概率+时间窗**、措辞用**迹象/倾向**、**无因果措辞**、**非投资建议**。
- **2026-10-03** —— 🆕 **N1 语料扩至 880 天 · N3-1 ③④ 产出 `TAXONOMY.md`（L1 主线推进）**。
  - **N1 续抓**：后台 `fetch_archive.py --max-seconds 900`（≥2s/req），倒序 `2024-06-08` → **`2024-05-07`**；语料 **847 天/393,059 → 880 天/408,956 条**（2024/2025/2026 三片；0 失败 / 0 空页）。⚠️ 停抓用 **PID 精确 `kill`**；`--stats`/`--index` **不与抓取并发**（实测并发会写坏 index 的 sha，顺序跑即正常）。
  - **`TAXONOMY.md`（新产物）**：新建生成器 **`news/policy/taxonomy.py`**（读语料 → 按类别聚合**真实计数** → 复现写盘）。**由 EDA 归纳**的 **15 类动作体系 A1–A15**，每类给 **定义/触发词 · 原始计数 + 政经口径计数 · 占比 · 2–3 真实示例（日期+链接） · 边界规则**；**频率分层由实测计数得出**（阈值一次写死：高频≥1000 / 中频200–999 / 低频<200，近3年政经口径）：
    - **高频** = A1 会见会谈(3444) · A8 领导人讲话活动(2388) · A5 发布印发(1869) · A13 回应反制(1312) · A4 举行(1256) · A6 部署实施(1040)；
    - **中频** = A15 货币工具(747) · A3 召开(517) · A2 出访访问(323) · A7 通报处罚(233) · A10 签署(202)；
    - **低频** = A14 试点推广(141) · A11 上市并购(132) · A9 开通投产(63) · A12 演习试射(51)。
  - **阶段性结论**：**政治动作整体样本充足**（高频/中频具备统计建模条件），与 §0.0.1「动作 ≠ 稀有事件」的判断一致；真正稀疏的是**战略级事件**。
  - **局限（如实写明）**：子串计数含噪声（A4 举行 / A11 上市 / A13 回应 尤甚）· **政经口径偏中国**（`GOV_MARKERS` 以中国机构为主 → **美/欧/日/韩 动作被低估**，是中国一侧的下界）· **A15 混入例行操作**（逆回购/MLF 与降准降息不同量级）· **代理源 ≠ 新华社**。
  - **未做**：常态采集（专注 L1）；L2 不产出结论（`EVENTS.csv` 未就绪 → 未过 G2）；L3 冻结。**下一步**：**N3-3 事件库** → N3-2 信号 → N3-4 预警；续抓 N1。
- **2026-10-03** —— 🆕 **转 L1/N1 主线：N1 语料抓取 + N3-1 EDA + L2 预注册 + 价格源复测**。
  - **新华网主源复测（结论）**：`www.xinhuanet.com/politics/2016-01/01/` → **HTTP 403**；`so.news.cn/getNews` → **HTTP 405**（WAF 页）→ **如实记录、🚫 不绕**（不代理/不伪造 UA）；按任务书**改用兜底源**。
  - **新建 `news/archive/fetch_archive.py`**（中新网逐日枚举 `scroll-news/{YYYY}/{MMDD}/news.shtml`，实测 2016/2023/2024 全 200；**GBK/UTF-8 自动探测**；**≥2s 限速**；断点续抓；子模式 `--stats/--index/--repair/--check`）。
  - **本轮语料**：倒序抓 **2026-06-30 ~ 2026-10-03 ＝ 96 天 / 46,883 条**（`chinanews-2026.jsonl.gz` 2.07 MB；0 失败 / 0 空页）；`--repair` 修 **2653** 条协议相对 URL（修后抽检 `HTTP 200`）。⚠️ 抓取中 `pkill -f fetch_archive.py` **误杀自身 shell**（模式匹配到命令行）→ 记一笔，改用 PID 精确 kill。
  - **N3-1 EDA**（`news/policy/EDA.md`，**真实计数**）：频道 top = 社会 10,383 / **时政 8,648** / 财经 8,567 / 国际 3,899；动作词 top = 发布 1,373 · 举行 1,320 · 启动 963 · 回应 393 · 调研 391 · **会见 282** · 出席 246；主体词 = 习近平（示例）/ 政治局 13 / 国务院常务会议 8；标题模式 = 「X 会见 Y」281 · 「X 决定/批准…」148 · 「签署协议」48 · 「就…作出重要指示」3。
  - **L2 预注册**（`news/policy/L2_PREREG.md`，窗口/口径/检验/多重比较**先写死**）+ **价格源运行机复测**：腾讯实时 `qt.gtimg.cn` **200** · 腾讯日K `web.ifzq.gtimg.cn` **200 JSON** · 新浪 `hq.sinajs.cn`（需 `Referer`）**200**；**东财 `push2his.eastmoney.com` ❌（TLS reset：`decode error 562`）** → 历史日线改用腾讯。
  - **下一步**：继续续抓 N1（近 3 年 → 10 年）→ 由 EDA 归纳 `TAXONOMY.md` → N3-2/3/4。本轮**未做常态采集**（专注 N1/N3）。
  - 判据复核：语料 5 字段齐全、**可回溯 url**；EDA 数字**均来自真实语料**；L2 全文**无因果措辞**（只 相关/同期/滞后/共现）。
- **2026-10-04** —— 🐞 **L1 链在扩展语料上重跑 + 语料/事件轴对齐修复（本轮主线）**。
  - **🐞 关键缺陷（已修）**：`news/policy/early_warning.py` 评估轴原取**语料全程**，而 `EVENTS.csv` 只从 **2024-04-13** 起 → 前 ~380 天「**信号列有、标签恒 0**」→ **伪造全零负样本、虚高 AUC**（旧版部分格 AUC≈0.9 是假的）。**修复**：加**轴对齐护栏**（评估窗口 = 语料 ∩ 事件日期范围）；修复后 §4 `测试N` 由 ~1260 降到 ~1100–1200，AUC 回落到可信区间（最好 ≈ **0.65**）。
  - **§4.2 改为数据驱动 + 效果量门槛**：删掉原**写死结论**（曾与实测自相矛盾）；现全部由当次实测生成。**45 格**：`p<0.05` **34** ｜ BH 后 `q<0.05` **34** ｜ 过**效果量门槛**（`q<0.05` 且 `AUC≥0.60` 且非低频）**8**；另 **9 格 AUC<0.5 反向**如实列出。产物内明写：**`q<0.05` 只证明「非随机」≠「可预警」**；本信号本质是**活动聚簇/持续性**弱信息。
  - **§5 频率分层（由实测得出）**：**高频可建模**（A8 讲话 Δ=7 AUC **0.626**、A4 举行 Δ=7 0.587）｜ **中频部分可用**（A15 货币 Δ=30 **0.648**、A2 出访 Δ=7 **0.639**、A6 部署 Δ=90 **0.638**）｜ **低频仅案例**（A9/A12 样本 <5 或 AUC<0.5）。
  - **链全量一致重跑**：`eda.py`→`taxonomy.py`→`signals.py`→`extract_events.py`（**25,032 事件**，CN=18,581；`EVENTS.csv` 5.76 MB，sha `ac6ac48e4f57975f`）→`early_warning.py`（`EARLY_WARNING.md` 283 行）；`explore_l2.py` 随新 `EVENTS.csv` 重生成（`explore.csv` 1170 格，sha `90f357ff8a8be943`；事件 **25,032**、可对齐交易日 **23,105 = 92.3%**）。
  - **N1 状态**：`--stats` 确认 **1296 天 / 605,311 条**、0 失败 / 0 空页；`--index` 重生成 `INDEX_FILES.md`（4 片 2023–2026，均 <20 MB → 入 git）。
  - **记忆维护**：`MEMORY_NEWS.md` 上轮 **~36 KB 超限** → 将**第三~九轮**常态采集流水**滚动归档**到 `daily-memories-news/2026-10-03.md`（原文不改），MEMORY 降到 **~23 KB**。
  - **未做**：常态采集（专注 L1/L2 重算）；**L3（N5）冻结**。判据复核：§4.2 **无写死结论**、`p`/`q` 与表一致、低频类已单列；**无因果措辞**、**非投资建议**。
- （更早流水：第三~九轮 / 第二轮 / 首轮 smoke / 前期任务 T1–T4 / 建线 / 首轮空转 → 已归档 `daily-memories-news/2026-10-03.md`）

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
