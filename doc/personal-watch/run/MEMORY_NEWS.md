# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~四十七轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序已收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库（75,610 条，对 15:10 全量快照）· N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + **§4.4 措辞强度 tone 信号**，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md，9 行）+ **G2′④ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）** · **第四十三~四十七轮常态采集（news +2 / +1 / +0 / +1 / +2）**
当前动作:     **本唤醒：第四十七轮常态采集（news **+2**）**——窗口 ~0.55h 紧接第四十六轮 + **国庆假期末段**；中文权威源 AI 类**零命中**（`cn_news` 限 60 → 标题正则仅「智驾提醒」「六网含算力网」两条命中且均**非事件**）→ **如实留空、不凑数**〔§0.0.2〕；**IT之家新增 2 条收录**：`009/946`《GLM-5.3 上架亚马逊 AWS 大模型平台，智谱打开海外收入分成通道》（据《科创板日报》，**Amazon Bedrock 当日接入智谱 GLM-5.3**、**AWS 按调用量与智谱收入分成**；本机实测原文 `HTTP 200` + `Content-Type: text/html`，在窗；归第 1 类）· `009/949`《LG 电子将为北美超 5GW 人工智能数据中心供应冷水机组》（LG 北美分支与 **AIR Control Concepts** 达成**超 5GW AIDC 先进冷水机组长期供应协议**；与在账 `009/505`〔10-03 建厂计划〕为**同题材不同事件**，单列；本机实测 `HTTP 200`，在窗；归第 1 类）。IT之家余者（`009/953` 黄仁勋「世界巡演」AI 二创视频〔**文化现象·从严不收**〕· `009/947` 维基媒体×OpenAI 失控智能体〔**同事件·在账 Wikimedia 官方**〕· `009/945` 挪威 AI 眼镜〔同事件〕· `009/941` 空芯光纤〔已在账〕· `009/936` opinion · `009/937` 券商评级 · `009/939` 非 AI · 余非清单）→ 去重/不收；量子位头部（诺奖光遗传学〔非 AI〕+ 余已在账）；TechCrunch AI/The Verge/Ars 头部均**已在账/同事件/超窗/非新闻**；HN 候选皆 Show/Ask HN·tool·discussion → 拒收/去重。**上一唤醒：第四十六轮（news +1：IT之家 空芯光纤 AI 算力商用）· 第四十五轮（+0）· 第四十四轮（+1：麦当劳 AI 定价集体诉讼）· 第四十三轮（+2）**；第 10 批 B 线 P7（公开 RSS 核验 → 未发现，P7 关闭）等详见 §2 流水
下一步:       ① **第 10 批 B 线**：**P7 已核验 → 未发现公开 RSS/播客（P7 关闭）**；**仍待用户拍板 P1–P6**（`dongfang/report.html` §8：目标确认 P1 / 获取路径授权 P2〔**RSS 路线已排除 → 请在 P2(b) 用户登录态导出 / P2(c) 暂不实施 间选择**〕/ 仅个人使用 P3 / 音频存哪 P4 / 文字稿粒度 P5 / 更新时段 P6）→ **拍板前不实施日更**；② **G2′④ 累积**：**≥20h 后（约 2026-10-06 ≥11:10）**跑真实重跑（`cycle_run.py --with-l2`，**不带 `--record`**）追加台账（**台账自报：连续 1 天 / 目标 7 天，未达标**）；③ 常态采集续跑（**国庆假期中文权威源 AI 类稀薄 → 如实留空**）；④ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；⑤ L3（N5）**冻结**
本轮新增:     **第四十七轮常态 news **+2**（中文 2 / 英文 0；当日 **19** / 累计 **126**）**——① **IT之家《GLM-5.3 上架亚马逊 AWS 大模型平台，智谱打开海外收入分成通道》**（10-06；据《科创板日报》，**Amazon Bedrock 当日接入智谱 GLM-5.3**、**AWS 按模型调用量与智谱收入分成**，智谱近期与多家海外云厂商落地同类分成、国内已与阿里云百炼等签约；本机实测原文 `HTTP 200` + `Content-Type: text/html`，在窗；归第 1 类）；② **IT之家《LG 电子将为北美超 5GW 人工智能数据中心供应冷水机组》**（10-06；LG 电子北美分支与暖通企业 **AIR Control Concepts** 达成**超 5GW 规模 AIDC 先进冷水机组长期供应协议**，AIR 客户为全球领先数据中心运营商；与在账 `009/505`〔10-03 建厂计划〕为**同题材不同事件**，单列；本机实测 `HTTP 200`，在窗；归第 1 类）。`cn_news`（限 60）均国庆假期/民生/时政/天气/体育/文旅（`AI/…` 标题正则**仅「智驾提醒」「六网含算力网」两条命中且均非事件**）→ 不收；**联合国中文源仍 `HTTP 404`**；IT之家余者（`009/953` 黄仁勋「世界巡演」AI 二创视频〔**文化现象·从严不收**〕· `009/947` 维基媒体×OpenAI 失控智能体〔**同事件·在账 Wikimedia 官方**〕· `009/945` 挪威 AI 眼镜〔同事件〕· `009/941` 空芯光纤〔已在账〕· `009/936` opinion · `009/937` 券商评级 · `009/939` 非 AI）→ 去重/不收；TechCrunch AI/The Verge/Ars 头部均**已在账/同事件/超窗/非新闻**；HN 候选皆 Show/Ask HN·tool·discussion → 拒收/去重；→ `SEEN.md` **+2 行**（均 `news`）。┃ **第四十六轮及更早见 §2 流水**
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）｜🆕 **第 10 批**：⚠️ **`mcp<2` 已成运行机全局 pin**（2.3.0 → **1.30.0**，否则 `mcp_ddgs`/离线自检不可用）→ 与需 **mcp 2.x** 的其它线**可能冲突**，**待 supervisor 确认**；⚠️ **ddgs 8/8 引擎被墙**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但结果端点被拦）→ 免费通用 web 搜索**本机不可用**，日常仍以 `cn_news` + 官方 RSS 为准；⚠️ **CN-Bing 抓取相关性降级**（查「人工智能 最新 政策」返回「人工」词条 → 200 ≠ 有料）
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
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-06 08:55 CST` 第四十五轮 ~ `2026-10-06 09:32 CST` 第四十六轮
- **累计收录**：`news` **124** 条（第一~四十六轮；当日 **17**）+ 非新闻约 **122** 条（含第四十五轮 +9 / 第四十六轮 +7 防重行；口径=逐行统计 `SEEN.md` 类型列；+ `news(同事件) 3 / news(未核验) 1`）〔**仅存 `SEEN.md`**〕

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-06（本唤醒 ~10:05）** —— 🆕 **第四十七轮常态采集：news +2（中文 2 / 英文 0；当日 19 / 累计 126）**：① **IT之家《GLM-5.3 上架亚马逊 AWS 大模型平台，智谱打开海外收入分成通道》**（10-06；据《科创板日报》，**Amazon Bedrock 当日接入智谱 GLM-5.3**、**AWS 按模型调用量与智谱收入分成**，智谱近期与多家海外云厂商落地同类分成、国内已与阿里云百炼等签约；本机实测原文 `HTTP 200` + `Content-Type: text/html`，在窗；**归第 1 类〔大模型商业化 / 云分成〕**）；② **IT之家《LG 电子将为北美超 5GW 人工智能数据中心供应冷水机组》**（10-06；LG 电子北美分支与暖通企业 **AIR Control Concepts** 达成**超 5GW 规模 AIDC 先进冷水机组长期供应协议**，AIR 客户为全球领先数据中心运营商；与在账 `009/505`〔10-03 建厂计划〕为**同题材不同事件**，**单列不合并**；本机实测 `HTTP 200`，在窗；**归第 1 类〔AI 算力基础设施 / 液冷〕**）。源盘点：`cn_news`（限 60）均国庆假期/民生/时政/天气/体育/文旅（`AI/…` 标题正则**仅「智驾提醒」「六网含算力网」两条命中且均非事件**）→ 不收；**联合国中文源仍 404**；IT之家（`009/953` 黄仁勋「世界巡演」AI 二创视频〔**文化现象·从严不收**〕· `009/947` 维基媒体×OpenAI 失控智能体〔**同事件·在账 Wikimedia 官方**〕· `009/945` 挪威 AI 眼镜〔同事件〕· `009/941` 空芯光纤〔已在账〕· `009/936` opinion · `009/937` 券商评级 · `009/939` 非 AI · 余非清单）、量子位（诺奖光遗传学〔非 AI〕+ 余已在账）→ 去重/不收；TechCrunch AI/The Verge/Ars 头部均**已在账/同事件/超窗/非新闻**；HN 候选皆 Show/Ask HN·tool·discussion → 拒收/去重。**台账**：`SEEN.md` 追加 **2 行**（均 `news` 收录）。**G2′④**：距上次真实重跑（2026-10-05 15:10）约 **18.9h <20h** → **不做真实重跑、不刷台账连续性**（自报仍 **连续 1 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 真实重跑约在 **2026-10-06 ≥11:10**）。**判据复核**：✅ 无新增即如实留空 · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。


- **2026-10-06（本唤醒 ~09:32）** —— 🆕 **第四十六轮常态采集：news +1（中文 1 / 英文 0；当日 17 / 累计 124）**：**IT之家《我国应用下一代通信关键技术空心光纤，AI 算力时代给光信号造出"磁悬浮"高速轨道》**（10-06 01:16；援引**央视新闻 10-05 微博**，我国下一代通信关键技术**空芯光纤（hollow-core fiber）已率先在宁夏中卫的智算中心间投入商用**，**传输时延与损耗直降 30% 以上**；纤径不足 0.4mm、内嵌 20 根微型玻璃圆柱；本机实测原文 `HTTP 200` + `Content-Type: text/html` + `pubDate 2026-10-06 01:16:52`，在窗；**归第 1 类〔AI 算力/通信基础设施〕**）。源盘点：`cn_news`（限 45）均国庆假期/民生/时政/天气/体育/文旅（`AI/人工智能/大模型/芯片/算力/机器人/智能/算法/数据/量子` 标题正则**零命中**）→ 不收；**联合国中文源仍 404**；IT之家（`009/945` 挪威 AI 眼镜〔同事件·在账 Reuters/Ars〕· `009/932` Reflection Beam〔同事件·在账 TechCrunch〕· `009/936` 奥尔特曼评马斯克〔opinion〕· `009/937` 高盛台积电〔券商评级〕· `009/939` 欧盟数字主权 Element Pro〔非 AI〕· 余非清单）、量子位（诺奖光遗传学〔非 AI〕）、爱范儿（feature/超窗）→ 去重/不收；TechCrunch AI/The Verge/Ars 头部均**已在账/同事件/超窗/非新闻**；HN 候选皆 tool·analysis·discussion·opinion·feature → 拒收/去重。**台账**：`SEEN.md` 追加 **8 行**（1 `news` + 7 非新闻防重）。**G2′④**：距上次真实重跑（2026-10-05 15:10）约 **18.4h <20h** → **不做真实重跑、不刷台账连续性**（自报仍 **连续 1 天 / 目标 7 天 · ⚠️ 未达标**；下一窗具备 ≥20h 间隔约在 **2026-10-06 ≥11:10**）。**判据复核**：✅ 无新增即如实留空 · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。
- **2026-10-06（本唤醒 ~08:55）** —— 🆕 **第四十五轮常态采集：news +0（中文 0 / 英文 0；当日 16 / 累计 123，本类无新增）**。本轮**无新增**（如实留空，不凑数；§0.0.2）。窗口 ~0.5h 紧接第四十四轮 + 国庆假期末段 → 中外权威源 AI 类**零命中**。**源盘点（如实）**：`cn_news`（限 45）均假期/民生/时政/天气/体育/文旅（诺奖光遗传学〔非 AI〕、跳城游、援莱索托医疗队、无障碍决议、戴高乐号火灾、东北超、红色旅游、盗矿溺亡、天气、长征展、预约系统…）→ `AI/人工智能/大模型/芯片/算力/机器人/智能/算法/数据/量子/OpenAI/英伟达/神经网络` 标题正则**仅两条命中且均非事件**：「智驾提醒」（公众安全提醒、非事件）、「六张网（含算力网）」（"十五五"基础设施综述、**非事件性报道**）→ **不收**；⚠️ **联合国新闻·中文源仍 `HTTP 404`**。**英文 feed**：**TechCrunch AI**（`HTTP 200`，22 条）头部 = 水印〔**同事件**，在账 IT之家 `009/903`〕· Reflection Beam·Instinct·TikTok·Hot Girl·HackerRank·visual ads·agent fleet〔**均已在账**〕· 余 Disrupt 推介/超窗 → 去重；**Ars technology-lab**（`HTTP 200`，20 条）头部 = MCP〔**已在账（第四十一轮）**〕，余**非 AI/超窗**（Apple 全盘访问〔`10-02`>72h + tool〕· 联邦被黑 · RAM 短缺 · Zimbra · Cloudflare 量子证书 · RSA〔≤10-01〕）→ 去重/不收；**Ars `/ai/feed` 仍 `404`**（改用 technology-lab）。**`search_news`(HN `AI`)**：候选皆 **tool（schema-guard·Nova Sprint·Rashomon·Ototo·Skins·XCOR·Headline Arena·FlyHedwig·delphi.ai·It's a Plan）/ analysis（proton「What Is Proactive AI?」·AI Buildout Doom Loop〔Mastodon 镜像〕·Luke W）/ discussion（Fireship PewDiePie 视频·personal AI computer 推文·Ask HN 音效模型）/ paper（Khanmigo）/ opinion（NYT Ada Lovelace）/ 已在 `SEEN.md`** → 拒收/去重，其中 **9 条此前未在账者追加进 `SEEN.md` 防重复评估**。**A 线回归自检**：`news/mcp_ddgs/web_search_selftest.py` **离线自检全 PASS**（含 `search_status` 默认值暴露 / ddgs 版本可见 / 错误路径 `ok:false`）→ `web-search` MCP **仍可装载**（ddgs 8 引擎本机仍不可达，历轮一致；见 `news/MCP_INSTALL.md`）。**源健康度**：`cn_news`（中新网/央视网）`200` · **联合国中文 `404`** · TechCrunch AI / Ars technology-lab `200` · Ars `/ai/feed` `404` · The Register/BBC/CN-Bing/DDGS 同第四十四轮。**台账**：`SEEN.md` 追加 **9 行**（非新闻防重）。**G2′④**：距上次真实重跑（2026-10-05 15:10）约 **17.75h <20h** → **不做真实重跑、不刷台账连续性**（自报仍 **连续 1 天 / 目标 7 天 · ⚠️ 未达标**；如实写，**不为凑数刷行**；下一窗具备 ≥20h 间隔的真实重跑约在 **2026-10-06 ≥11:10**）。**判据复核**：✅ 无新增即如实留空 · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。

- **2026-10-06（本唤醒 ~08:22）** —— 🆕 **第四十四轮常态采集：news +1（中文 1 / 英文 0；当日 16 / 累计 123）**：**IT之家《麦当劳在美遭集体诉讼，被指用 AI 系统非法操纵菜单价格》**（10-06；据**路透社**，**麦当劳**在**芝加哥联邦法院**被提起**拟议的全国性集体诉讼**，原告指控其**借助 AI 定价系统非法协调特许经营店与直营餐厅的菜单价格**、**违反美国反垄断法**；诉讼于**当地时间上周五**提交；路透社此前报道其**定价引擎运用机器学习**持续分析近 **1.4 万家门店**每日数百万笔交易；麦当劳**周一发声明**称指控**主观揣测、缺乏事实依据**，「巨无霸以及其他任何餐品的价格都并非由人工智能设定」，各加盟商拥有定价决策权；原告代理律师 **Lark Turner** 称其「利用海量数据与特许加盟体系榨取消费者」，原告拟代表**数百万**伊利诺伊州消费者；本机实测原文 `HTTP 200` + `Content-Type: text/html`，在窗。→ 归**第 4 类 AI 与社会（算法定价 / 消费者权益）**兼第 3 类（反垄断 / 算法监管），**如实区分「原告指控 / 麦当劳回应」**，不把指控写成事实。源盘点：`cn_news`（限 40）均假期/民生/时政/体育/文旅（`AI/人工智能/大模型/芯片/算力/机器人/智能/算法/数据/量子` 标题正则**仅「假日提醒：莫把智驾当代驾」命中且为公众安全提醒、非事件**）→ 不收；**联合国中文源仍 404**；IT之家（育碧《看门狗》· MagSafe 3 固件 · Safari 追踪谷歌 · iCloud 别名 · IT早报 · 折叠 iPhone Duo · 铃木 e‑Sky **非清单**）、量子位（诺奖光遗传学〔非 AI〕+ 余已在账）、爱范儿（feature/opinion/超窗）、雷峰网（feature/超窗）→ 去重/不收；TechCrunch 头部（Lucid〔非 AI〕/水印〔同事件〕/Etched·Factory·Reflection·Instinct·TikTok·Ghost·Hot Girl·PearX〔已在账/推介〕）、The Verge（Call for Me〔同事件〕/Nolla〔已在账〕/Wikipedia〔同事件〕/水印〔同事件〕/OpenAI PR・Altman〔已在账〕/AI 数学 drama〔feature〕/Matic・Hyundai〔非 AI〕）、Ars（MCP〔已在账〕/余非 AI·tool·超窗）→ 去重/不收；`search_news`(HN `AI`/`AI regulation`/`OpenAI`/`Anthropic`/`AI safety`/`superintelligence`) 候选皆 **tool（XCOR 厂商稿·Nova Sprint·Rashomon·Ototo·Skins·Headline Arena·Vespper）/ analysis（AI Buildout Doom Loop〔Mastodon 镜像〕·Luke W 设计系统·semianalysis·nymag〔feature〕·lesswrong）/ paper（Khanmigo 两年实验）/ discussion（Ask HN）/ 已在 SEEN / 同事件 / 超窗（NBC `10-01`·NYT `09-30`）→ 拒收/去重**。**源健康度**：**联合国中文源仍 404** · **Ars `/ai/feed` 仍 404**（改用 technology-lab）· **The Register `headlines.atom` PoW 墙** · **BBC 空响应** · **`web-search`(DDGS) `live_probe` 8/8 引擎被墙** · **`web_search`(CN-Bing) 相关性降级**。**台账**：`SEEN.md` 追加 **8 行**（1 news 收录 + 7 非新闻防重：XCOR·Rashomon·Ototo·Skins·Doom Loop·Luke W·Khanmigo）。**G2′④**：距上次真实重跑（2026-10-05 15:10）约 **17.2h <20h** → **不做真实重跑、不刷台账连续性**（自报仍 **连续 1 天 / 目标 7 天 · ⚠️ 未达标**；下一窗 ≥20h 真实重跑约在 **2026-10-06 ≥11:10**）。**判据复核**：✅ 每条带 `标题+来源+发布日期+链接` · ✅ 指控类**区分指控/回应** · ✅ 非新闻单列（仅存 `SEEN.md`）· ✅「我们的观察」标注 · ✅ 无因果措辞 · ✅ 非投资建议 · ✅ **L3（N5）冻结**。

- 🔀 **第四十三轮**（2026-10-06 ~07:48，news +2：Gemini Call-for-Me 爆料 · tvOS 27.2 Apple TV 4K Siri AI 爆料）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- 🔀 **第四十一~四十二轮**（2026-10-06 ~06:41〔+1 Ars MCP〕/ ~07:14〔+0〕）已由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。
- 🗂 **第三十八~四十轮（10-06 ~05:00 / ~05:33 / ~06:06，均 news +0）** —— 由滚动机制归档至 `daily-memories-news/2026-10-06.md`（原文不改）。

- **2026-10-05（本唤醒 ~23:40）** —— 🗂 **用户直派「第 10 批」A/B 双线**（A：免费 web-search MCP 装进 cline〔**依赖装齐 + cline 注册成功，但 ddgs 8/8 引擎被墙 → 本机不可用**〕；B：《衍射+东方时事解读音频》获取与转写调研〔**只调研不实施日更**〕）→ **明细已由滚动机制归档至 `daily-memories-news/2026-10-05.md`**（原文不改）；产物：`news/MCP_INSTALL.md` · `news/dongfang/report.html` · `news/dongfang/METHODS.md`；**待用户拍板 P1–P6/P7**。

- （更早流水：**2026-10-06 ~03:52 / ~04:40 第三十六~三十七轮**（Reflection Beam · Menlo×Factory · Etched 融资要约 · Nolla 处方；本轮由滚动机制平滑归档至 `daily-memories-news/2026-10-06.md`）· **2026-10-06 ~01:24 第三十一轮**（The Verge《OpenAI PR 要求记者 move on》；已归档 `daily-memories-news/2026-10-06.md`）· **2026-10-06 ~00:13 / ~00:52 第二十九~三十轮**（已归档 `daily-memories-news/2026-10-06.md`）· **2026-10-05 22:13/22:49 第二十七~二十八轮**（The Verge StarCraft 破规作弊 · TechCrunch 中国 AI「agent fleet」；由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 21:05/21:37 第二十五~二十六轮**（常态采集；本轮第 10 批唤醒由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 18:45~20:26 第二十一~二十四轮**（常态采集；本轮 22:49 由滚动机制平滑归档至 `daily-memories-news/2026-10-05.md`）· **2026-10-05 17:25/17:55 第十九~二十轮**（TechCrunch 超级智能部队 · 钛媒体 SpaceXSI · TechCrunch 联邦法官裁定 Flock；已归档 `daily-memories-news/2026-10-05.md`）· **2026-10-05 16:12 第十六~十七轮**（L1 §4.3 固定召回率 precision 加固 + IT之家索尼×Meta 专利）→ 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-05 早期**（恢复 27h 停摆首轮 · N1 2021/2022 续抓）· **N1 第 3/4/5/6 轮抓取（2020→2019→2017/2018→2016）+ 第十一~十五轮常态采集 + 全链重跑** → 已归档 `daily-memories-news/2026-10-05.md`；**2026-10-03 各轮 / 2026-10-04 各轮**（L1/N3 收口、N4/L2、L1 链重跑+轴对齐）→ `daily-memories-news/2026-10-03.md` · `daily-memories-news/2026-10-04.md`；第三~九轮 / 第二轮 / 首轮 smoke / 前期任务 T1–T4 / 建线 / 首轮空转 亦在其中）

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
