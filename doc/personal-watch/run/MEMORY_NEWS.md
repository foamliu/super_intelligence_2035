# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ 🆕 L2/N4 探索性（G2 全过）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~九轮常态 ✅ · **N1 抓取器 + 语料（1194 天 / 557,197 条）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库（18,232 条）· N3-4 预警方案 · L2 预注册 · 价格源复测 · 🆕 N4 探索性关联（EXPLORE.md + explore.csv）**
当前动作:     **N4（L2 探索性）交付 + N1 续抓**：`news/policy/EXPLORE.md` + `explore.csv`（生成器 `explore_l2.py`）→ **动作类型×板块×窗口** 描述性 CAR + **FDR(BH) 校正显著性** + 四坑逐条 + 能力边界；**🚫 非因果**。**G2（①价格源复测 ②方法预注册 ③描述性统计）全过** → N4 放行。`explore.csv` **重跑字节一致**（`cc6058305bbe8d61`）= 可复现
下一步:       ① **G2′ ④：连续 N 周稳定运行**（按周期跑预警并与基线对比）→ ② 加 **FDR 校正** + 纳入 SIGNALS 措辞/新词信号 + 系统评估组合规则 → ③ 继续 N1 续抓（**2023-06-27 → 2016-01-01**）；④ L3（N5）**冻结**
本轮新增:     **N4 两产物（`EXPLORE.md` + `explore.csv` 新）**；N1 语料 904 → **1194 天**（420,828 → **557,197 条**，新增 2023 片）；**news 日报 0 条**（本轮专注 L2/N1，未做常态采集）
阻塞:         无（新华网长期 403/405 → 用兜底源 `chinanews`；⚠️ **东财日K 运行机 TLS 被重置不可用** → 历史日线改腾讯 `ifzq` 日K；⚠️ **`--stats`/`--index` 不可与抓取/`--repair` 并发**——实测并发会写坏 index 行 sha，顺序跑即正常）
ERROR_COUNT:  1（历史：模型名 `deepseek-v4-pro-fp4` 白睡一轮，已修；本轮 0）
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
- **N1 语料库**：`news/archive/chinanews-<年>.jsonl.gz`（只 5 字段；**仅取 标题+日期+来源+链接，不抓正文**）；现 **1194 天 / 557,197 条**（2023-06-27 ~ 2026-10-03）
- **L1 产物**：`news/policy/`（`EDA.md` / `TAXONOMY.md` / `SIGNALS.md` / `EVENTS.csv` / `EARLY_WARNING.md`）
- **L2 产物（探索性 · 非因果）**：`news/policy/`（`L2_PREREG.md` / **`EXPLORE.md` + `explore.csv`**）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-03` 第八轮常态（11:10 UTC）~ `2026-10-03` 第九轮常态（11:55 UTC）
- **累计收录**：`87` 条（**news 61**〔第一轮 3 + 第二轮 6 + 第三轮 6 + 第四轮 15 + 第五轮 5 + 第六轮 9 + 第七轮 6 + 第八轮 4 + 第九轮 7〕+ 非新闻 26〔仅存 `SEEN.md`〕）

---

## 2. 流水（倒序，保留最近 ~20 条）

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
- **2026-10-03** —— ✅ **第九轮常态采集完成（news 7 条：中文 5 / 英文 2）**。PHASE=常态采集。
  - **`cn_news`（T10）实跑**：`--cn-news --limit 40 --json` → `exit=0`、**6 活源全 200**（`limit=200` 复核命中 188 条）；中新网×3 kept=30/30/30（drop 0）· 联合国 kept=18(drop 12，超龄) · 央视 news_1 kept=80 / tech_1 kept=11(drop 69，超龄)。⚠️ 命中**几乎全为国庆/时政/民生/亚运（非 AI）** → **未从中录条目**（宁缺勿滥）。
  - **关键补漏（方法改进，建议固化）**：实测 **IT之家 RSS 窗口仅 ~5h**（`count=60`、`pubDate` 06:23~11:45 GMT、`id` 445→533）→ **10-02 的 `1/009/237`–`270` 段整体漏收**；改用 **IT之家首页 `www.ithome.com/` 枚举**（覆盖更深）**补齐 5 条 10-02 中文 AI 新闻** → **建议后续每轮固定加抓首页**。
  - **落盘**：`news/2026-10-03.md` 追加「九、第九轮」7 条 · `SEEN.md` +9 行（7 news + 2 非新闻）· `INDEX.md` news 54→**61**（另非新闻 24→**26**）。
  - **代表条目**：IT之家《Cloudflare 推出基于 Qwen 的开源多模态决策模型 Clef》(§1.1) · Tom's Hardware《Anthropic 称智谱 GLM-5.3 具 Mythos 级漏洞利用能力》(§1.2) · IT之家《AI 伦理研究：DeepSeek 对男女一视同仁…》(§1.2) · TechCrunch《特朗普与 AI 领袖签署的承诺拼错美国国名》(§1.3) · IT之家《OpenAI 融资再落袋 200 亿美元·估值 8,520 亿》/《博通筹 600 亿美元》/《Anthropic 最早 11 月中旬上市》(§1.5)。
  - **方法观察**：**新发现不可达**：Reuters `www.reuters.com`、NY Post `nypost.com`（`Network is unreachable`）→ Bull 超算/FTC 立案两条**无法核验 → 未收录**；**CN-Bing 新闻垂直 `cn.bing.com/news/search`** 为 **JS 渲染**（HTML 无正文）；**360 `web_search`** 中英混合长查询**返 0**；**cnBeta `backend.php` / 钛媒体 `tmtpost.com/rss` / 36氪 `feed-newsflash`** 经 stdlib **解析失败**；**新浪科技 RSS** 仍停 2018-09-23；**虎嗅 `rss/0.xml`** 超时；**英文 = Tom's Hardware 正文直取** + **TechCrunch** + HN(Algolia)；**GDELT 未调**（退避）。
  - **拒收例（§0.1）**：雷峰网《连败 6 场…寒武纪前高管…》(特稿) · 量子位《Jev 估值 100 亿美元…回答一切》(AMA/访谈，与第四轮同题) · IT之家《苹果 homeOS 前瞻…》(前瞻/传闻) · IT之家《迈富时 GEO…》三连(`1/009/523–525`，软文) · IT之家《贝恩：…2031 年 6 万亿美元…》(报告解读/预测) · IT之家《纳德拉重申 Copilot 定位》(表态、无新事件) · IT之家《OpenAI 澳洲机构遭入侵》/《`.si` 域名激增》/《苹果收紧 macOS 27》/《DGX Spark 64GB》/《Anthropic 1 亿美元培训》/《arXiv 限投 2 篇》(**均已在 SEEN，同题去重**) → **存疑即不收**。
  - 判据复核：7/7 字段齐全（标题 + 来源 + 发布日期 + 🔗链接 + 🏷 类型：news）；**中文 5 ≥ 英文 2**。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **第八轮常态采集完成（news 4 条：中文 2 / 英文 2）**。PHASE=常态采集。
  - **`cn_news`（T10）实跑**：`--cn-news --limit 90` → **6 活源全 200**；新鲜度：中新网×3 kept=30/30/30（drop 0）· 联合国 kept=18(drop 12，超龄) · 央视 news_1 kept=80 / tech_1 kept=11(drop 69，超龄)；**丢弃合计 ≈81**。⚠️ 命中仍多为**国庆/时政/民生（非 AI）** → **仅从中录 1 条**（央视网 AI 眼镜稻飞虱），其余**未凑数**。
  - **落盘**：`news/2026-10-03.md` 追加「八、第八轮」4 条 · `SEEN.md` +6 行（4 news + 2 拒收 feature）· `INDEX.md` news 50→54（另非新闻 24）。
  - **代表条目**：TechCrunch《斯洛文尼亚 `.si` 域名在特朗普"超级智能"行政令后注册激增》（§1.3）· WIRED《这些 AI 专家想把高风险研究放到公开场合做》（Trillium Labs，§1.2）· IT之家《AI 自动识别后厨违规行为，浙江 19.5 万家外卖商家接入系统》（§1.4）· 央视网《体长仅 1 毫米的稻飞虱怎么防？AI 眼镜给稻田精准"把脉"》（§1.4）。
  - **方法观察**：**中文主供给仍是 IT之家 RSS**；**量子位 RSS** 最新仍为 10-03 04:41「OpenAI 安全团队」（**与第四轮同题 → 去重**）；**爱范儿 RSS** 最新 10-03 07:00《AI 视频榜…》(feature→拒收)；**钛媒体 `tmtpost.com/feed`** 可用但本轮无 AI 新闻；**36氪 `feed`/`feed-newsflash`、cnBeta `backend.php`、机器之心 `rss`、观察者 `rss`** 经 stdlib **解析失败**；界面 404 / 澎湃空 / C114 解析失败 / **Guardian 本机不可达**；**GDELT 未调**（退避）；**science.org**（HN 收录的《An AI agent emailed researchers…》）**正文 403** → 未收录。
  - **拒收例（§0.1）**：量子位《OpenAI 安全团队持续地震…》(与第四轮同题**去重**) · 爱范儿《AI 视频榜全球第二…》/ The Verge《OpenAI's Dot agent…hands-on》(feature；Dots 发布 09-29 >72h) · 钛媒体《AI 正在造 AI》《国庆出游用 AI…》(analysis/专栏) · TechCrunch《Sanders…Flock》(车牌监控，非 AI 主线) /《Pope Leo XIV…AI art》(离题) · WIRED《ICE…Palantir database》(非 AI) · 央视网《机器人巡检…特色养殖》(农业科技) · 极客公园《英伟达股价创新高…》(日汇总) → **存疑即不收**。
  - 判据复核：4/4 字段齐全（标题 + 来源 + 发布日期 + 🔗链接 + 🏷 类型：news）；**中文 2 ≥ 英文 2**。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **第七轮常态采集完成（news 6 条：中文 3 / 英文 3）**。PHASE=常态采集。
  - **`cn_news`（T10）实跑**：`--cn-news --limit 300 --json` → `exit=0`、**6 活源全 200**；新鲜度：中新网×3 kept=30/30/30（drop 0）· 联合国 kept=18(drop 12，超龄) · 央视 news_1 kept=80 / tech_1 kept=11(drop 69，超龄)；**丢弃合计 81**。⚠️ 命中仍多为**国庆/时政/民生（非 AI）** → **未从中录条目**（宁缺勿滥）。
  - **落盘**：`news/2026-10-03.md` 追加「七、第七轮」6 条 · `SEEN.md` +6 行 · `INDEX.md` news 44→50（另非新闻 22）。
  - **代表条目**：Meta《Muse 开源、进消费设备》(TechCrunch) · Sean Parker《围绕音乐重建 Stability AI》(TechCrunch) · Circuit Breaker Labs《让 AI 对孩子更安全》(TechCrunch) · 爱范儿《MiniMax M3.1 Flash Preview 实测》 · IT之家《AI 面试官"恐怖谷"上热搜》 · IT之家《大众 CARIAD 裁员 1000 人》。
  - **方法观察**：**新增中文 dated 活源：爱范儿 RSS**（`ifanr.com/feed`，200 + 带 pubDate）；本轮另实测 **雷峰网 `leiphone.com/feed`**、**钛媒体 `tmtpost.com/rss`** 亦为活源（记备用）；**新发现死源**：**新浪科技 `rss.sina.com.cn/tech/rollnews.xml`** = 接口 200 但**内容停在 2018-09-23**（又一「200 ≠ 有新闻」例）；**中新网 `/rss/it.xml`** 空 feed；**机器之心/澎湃 302、智东西 500、虎嗅超时、pingwest 返 HTML**；**GDELT 未调**（退避）。
  - **拒收例（§0.1）**：钛媒体《AI 正在造 AI》《AI 杀不死咨询公司》《大模型一体机缩水》《Muse 狂飙，龙虾退潮》(analysis/专栏) · 钛媒体《苏姿丰抬头，李飞飞低头》(报道 AMD 9/28 收购 World Labs，**事件 >72h** 且为特稿) · 雷峰网《DeepSeek 开源算子工具…》(09-30 18:58 北京，**≈72h 边界**) · 爱范儿《AI 视频榜全球第二…》(feature) /《Gemini 4 正式发布…》(与量子位**同题去重**) · 路透《AI 竞相在资金耗尽前改变世界》(feature) · HN `Show/Ask HN`(tool/discussion) · qz/Ars(Shield TV/Apple FDA)（**均已 SEEN**） → **存疑即不收**。
  - 判据复核：6/6 字段齐全（标题 + 来源 + 发布日期 + 🔗链接 + 🏷 类型：news）；**中文 3 ≥ 英文 3**。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **第六轮常态采集完成（news 9 条：中文 7 / 英文 2）**。PHASE=常态采集。
  - **`cn_news`（T10）实跑**：`--cn-news --limit 40 --json` → `exit=0`、**6 活源全 200**；新鲜度：中新网×3 kept=30/30/30（drop 0）· 联合国 kept=18(drop 12，超龄) · 央视 news_1 kept=80 / tech_1 kept=11(drop 69，超龄)；**丢弃合计 81**。⚠️ 命中仍多为**国庆/时政/民生（非 AI）** → **未从中录条目**（宁缺勿滥）。
  - **落盘**：`news/2026-10-03.md` 追加「六、第六轮」9 条 · `SEEN.md` +9 行 · `INDEX.md` news 35→44（另非新闻 22）。
  - **代表条目**：Amazon《Strands Decider 2B 开源决策模型》(IT之家) · Aleph Alpha《Kolibri 主权开源权重模型》(官博，经 HN) · CBS《Qwen 政治偏向研究》(英文) · AMD《Versal 航天级 AI SoC 出样》· 华为《小艺帮帮忙智能体调整》· YouTube《Shorts 算法调整》· LG《美国 AI 数据中心冷水机组工厂》· 量子位《DeepSeek 扩招》· Neurable《EEG 脑电耳机》。
  - **方法观察**：中文 AI 新料主来自 **IT之家 RSS**；英文来自 **CBS News / Aleph Alpha 官博（经 HN）**；**Ars RSS** 仍停 10-02（无新）；**The Register** `headlines.atom` 经 stdlib **仍报 `not well-formed ... line 7, column 22`**（待修，改经 HN）；**GDELT 未调**（退避）。
  - **拒收例（§0.1）**：NPR《AI 数据中心：居民电价谁埋单》(explainer/泛论) · Guardian《OpenAI 称大规模黑客调查昂贵》(与第四轮 IT之家同题**去重**) · qz/Reuters/Tom's Hardware/Ars(Shield TV)（**均已 SEEN**）· Reddit《Gemini 取消免费》(论坛帖) · EFF deeplink(倡导/分析) · HN `Show/Ask HN`(tool/discussion) → **存疑即不收**。
  - 判据复核：9/9 字段齐全（标题 + 来源 + 发布日期 + 🔗链接 + 🏷 类型：news）；**中文 7 ≥ 英文 2**。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **第五轮常态采集完成（news 5 条：中文 4 / 英文 1）**。PHASE=常态采集。
  - **`cn_news`（T10）实跑**：`--cn-news --limit 60` → **6 活源全 200**；新鲜度：中新网×3 kept=30/30/30 · 联合国 kept=18(drop 12) · 央视 news_1 kept=80 / tech_1 kept=11(drop 69)；**丢弃合计 81**（均超龄 >72h）。⚠️ 命中多为**国庆/时政/民生（非 AI）** → **未从中录条目**（宁缺勿滥）。
  - **落盘**：`news/2026-10-03.md` 追加「五、第五轮」5 条（中文 4：IT之家；英文 1：WSJ 经 HN）· `SEEN.md` +5 行 · `INDEX.md` news 30→35（另非新闻 22）。
  - **代表条目**：《爱彼迎房东用 AI 生成「漏水」照勒索房客》(IT之家) · 《韩国五大银行首次同时遭（疑似 AI 驱动）黑客攻击、三家信息泄露》(IT之家/韩联社) · 《OpenAI 解雇被指共享机密的研究人员》(WSJ) · 《三星为 2027 HBM4 寻求超 HBM3E 三倍定价》(IT之家)。
  - **方法观察**：本窗口仅 ~30min → 新料有限，**未凑数**；**量子位 RSS 自第四轮无新**；**The Register** 的 `headlines.atom`/`.rss` 经 stdlib 解析**均报 `not well-formed ... line 7, column 22`** → 该源 RSS 改由 **HN** 取（记一笔待修）；**Ars RSS** 最新停在 10-02（无新）；**GDELT 未调**（退避）。
  - **拒收例（§0.1）**：路透《AI 竞相在资金耗尽前改变世界》(feature) · OpenAI《GPT-6 使用指南》(tutorial) · Yahoo Finance《Google 员工对新 Gemini 存疑》(非具体事件) · `Codex Originals`(产品页) · 各类 `Show HN`/`Ask HN` → **存疑即不收**。
  - 判据复核：5/5 字段齐全（标题 + 来源 + 发布日期 + 🔗链接 + 🏷 类型：news）；**中文 4 ≥ 英文 1**。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **第四轮常态采集完成（news 15 条：中文 11 / 英文 4）**。PHASE=常态采集。
  - **新增中文 dated 活源：量子位 RSS**（`https://www.qbitai.com/feed`，实测 `200` + 带 `pubDate`）→ 补齐中文 AI 纵深报道（Gemini 4 / 何恺明 NAT-ARC / OpenAI 安全团队 / arXiv 新规 / 丘成桐论文）。依 **T10** 规定**未并入** `CN_LIVE_SOURCES`（只准三类活源），以 `rss_latest` 单独取数。
  - **落盘**：`news/2026-10-03.md` 追加「四、第四轮」15 条（中文 11：量子位 5 + IT之家 5 + 中新网 1；英文 4：NVIDIA 官方 / The Register / Ars Technica / Fortune）· `SEEN.md` +15 行 · `INDEX.md` news 15→30（另非新闻 22）。
  - **代表条目**：谷歌 Gemini 4 发布（量子位）· arXiv 最严投稿新规（量子位）· OpenAI 智能体闯祸「每天烧 50 万美元」调查（IT之家）· OpenAI 收加州传票（The Register）· 美国陆军组建自主系统司令部（IT之家，🏷 关联「自主系统」）。
  - **拒收例（§0.1）**：路透《AI 正竞相在资金耗尽之前改变世界》(feature / 泛论) · OpenAI GPT-6 使用指南 (tutorial) · 量子位《Jev 估值…回答一切》(AMA/访谈) · 量子位《openJiuwen X-Router…》(疑似软文) → **存疑即不收**。
  - 判据复核：15/15 字段齐全（标题 + 来源 + 发布日期 + 链接 + 🏷 类型：news）。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **第三轮：T10「中文活源统一入口」+ T9「中文权威源真新闻」+ T8「§0.1 收口」全部完成**。PHASE→常态采集。
  - **T10 落地**：`news/mcp_web_search_free.py` 新增 `fetch_cn_news()` / `cn_news_report()` + **MCP 工具 `cn_news`** + **CLI `--cn-news`**；**实跑** `--cn-news --limit 30` → **6 活源全 200、命中 30 条、丢弃 83 条**（超龄 >72h）；文档 `news/FETCH_CN_NEWS.md`。
  - **T9 产出**：`news/2026-10-03.md` 追加「三、第三轮 · 中文权威源」**真新闻 6 条（中文 4：央视网 2 + 中新网 2；英文 2：Ars Technica）** → **中文 ≥ 英文**（彻底纠正此前「中文权威新闻 = 0」）。
  - **T8 收口**：原 31 条逐条打 `🏷 类型` → **保留 news 9**、移出非新闻 22（feature / opinion / analysis / paper / tool / discussion；依修订版**不设「非新闻附录」**）；`SEEN.md` **增「类型」列**（37 行）；`INDEX.md` 计数改 **news-only**（news 15 / 非新闻 22）。
  - **关键方法**：**央视网 → 站内 JSONP 接口**（`news.cctv.com/2019/07/gaiban/cmsdatainterface/page/{news,tech}_1.jsonp`，自带 `focus_date`；页面为 JS 渲染，直抓 HTML 拿不到条目链接）；死源黑名单（新华 / 人民 / 央视 RSS）**永不请求**。
  - 判据复核：本文件所有条目均带 标题 + 来源 + 发布日期 + 链接。**下一步常态采集（WAITING=1）。**
- （更早流水：第二轮 / 首轮 smoke / 前期任务 T1–T4 / 建线 / 首轮空转 → 已归档 `daily-memories-news/2026-10-03.md`）

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
