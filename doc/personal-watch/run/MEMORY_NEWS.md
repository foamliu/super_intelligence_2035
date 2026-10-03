# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 全部 ✅；自第四轮起进入常态采集）
已完成:       T1–T10 全部 ✅ · 首轮 smoke ✅ · 第二轮常态 ✅ · 第三轮·中文权威源 ✅ · 第四轮常态 ✅ · 第五轮常态 ✅
当前动作:     第五轮常态采集：`cn_news`（6 活源全 200，但命中多为国庆/时政/民生 → 未录）+ **IT之家 RSS**（中文主供给）+ 量子位 RSS（自第四轮起无新）+ HN(Algolia)（英文）→ 落盘 news/2026-10-03.md「五、第五轮」**news 5 条（中文 4 / 英文 1）**；SEEN +5；INDEX news 30→35
下一步:       常态采集（WAITING=1，睡 30min）：逐类搜索→去重→追加当日摘要；**每轮先用 `cn_news` + IT之家/量子位 RSS 补中文（中文≥英文）**，英文走 `search_news`(HN) / 官方 RSS；GDELT 限频退避
本轮新增:     news 5 条（**中文 4**：IT之家 4〔Airbnb AI 图片勒索 / 韩国银行 AI 黑客 / 华为 Mate 90 韬芯片 / 三星 HBM4 定价〕；**英文 1**：WSJ〔OpenAI 解雇研究人员，经 HN〕）
阻塞:         无
ERROR_COUNT:  1（历史：模型名 deepseek-v4-pro-fp4 不被网关支持 → 白睡一轮；已修。GDELT 429 属频控，已如实记录、未重试）
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

---

## 1. 状态头

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-03` 第四轮常态（06:45 UTC）~ `2026-10-03` 第五轮常态（07:17 UTC）
- **累计收录**：`57` 条（**news 35**〔第一轮 3 + 第二轮 6 + 第三轮 6 + 第四轮 15 + 第五轮 5〕+ 非新闻 22〔仅存 `SEEN.md`〕）

---

## 2. 流水（倒序，保留最近 ~20 条）

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
- **2026-10-03** —— ✅ **第二轮常态采集完成（15 条）**。PHASE→常态采集。
  - 工具：免 key MCP `web-search-free`（`search_news`=HN/GDELT、`rss_latest`、`web_search`=CN-Bing/360）。
  - 落盘：`news/2026-10-03.md` 追加「第二轮」段（15 条，均带 标题+来源+日期+链接）· `SEEN.md` +15 行 · `INDEX.md` 当日 16→31、累计 31。
  - 类目分布：①前沿模型 3 ②安全对齐 3 ③政策治理 4 ④AI与社会 2 ⑤公司人物 1 ⑥与本书相关 2。
  - 代表条目：Amazon 发布自家 "Jev" 决策模型克隆（TechCrunch）；Apple 收紧完全磁盘访问以遏制 AI agent 滥用（Ars）；特朗普呼吁 AI 公司"极大自我监管"（NBC）；比尔·盖茨称不受约束 AI 或"致十亿人死亡"（Guardian）；NVIDIA OpenShell 自主 agent 安全运行时（GitHub）。
  - 方法观察：**GDELT 本轮 429**（省额度未重试）→ 必须限频；**中文通用搜索仍无日期**（CN-Bing 返词典噪声、360 无 pubDate）→ 未从中录入；直连 **HEAD 抽检** TechCrunch/Anthropic/GitHub/arXiv=200、Ars=405（不支持 HEAD，条目经 RSS 取得）。
  - 判据核对：15/15 字段齐全；判断类已标"**我们的观察**"。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **首轮 smoke 完成（6 类 16 条落盘）**。
  - 工具：免 key MCP `web-search-free`（`search_news`=HN、`rss_latest`、`web_search`）。
  - 落盘：`news/2026-10-03.md`（16 条，均带 标题+来源+日期+链接）· `news/SEEN.md`（16 行）· `news/INDEX.md`（当日 16 / 累计 16）。
  - 类别覆盖：①前沿模型 3 ②安全对齐 3 ③政策治理 3 ④AI与社会 3 ⑤公司人物 2 ⑥与本书相关 2。
  - 关键发现（方法）：**`IT之家 RSS`（ithome.com/rss/）可用且带 pubDate**，补上中文 dated 源；**360 中文召回好但无日期**（本轮未正式录入）；**CN-Bing 多关键词中文长查询质量差**（返词典噪声）→ 中文改走 360/IT之家；**arXiv cs.AI RSS 当日空**；GDELT 本轮未调（省额度）。
  - 判据核对：16/16 条字段齐全；判断类内容已显式标"我们的观察"。**下一步常态采集（WAITING=1）。**
- **2026-10-03** —— ✅ **前期任务 T1–T4 完成**。
  - **T1 Web 搜索调研**：核实 12 个候选（Brave/CSE/SerpAPI/Tavily/Exa/ddgs/SearXNG/Mojeek/Bocha/Bing-Azure + CN-Bing/360）。
    决定性事实：本机（中国网络）Google/DDG/Brave/Yahoo/公共 SearXNG **全部不可达**；CN-Bing(200)、360(200)、Tavily/Exa/SerpAPI/Bocha **可达**。
  - **T2 MCP 配置+实测**：新建 `news/mcp_web_search_free.py`（`MCPServer`，兼容 1.x；3 工具 `web_search`/`search_news`/`rss_latest`），
    并 `news/cline_mcp_config.json`。**stdio 全链路实测通过**（initialize→tools/list→tools/call，exit 0）。
  - **T3 新闻 API 调研**：核实 17 个源（HN/HN-Algolia/GDELT/Guardian/NYT/NewsAPI/GNews/NewsData/Currents/Mediastack/TheNewsAPI + 官媒 RSS…）。
    **已实测取数**：HN 200、GDELT 200（含 429 频控样本）、中新/新华/人民 RSS 200、arXiv 200。
  - **T4 报告**：产出 `news/API_COMPARISON.md`（底稿）+ `news/API_COMPARISON.html`（自包含、内联 CSS、无外链、离线可开，2 大对比表 + 表下实测记录 + 风险）。
  - 详见报告 §4「实测记录」。**下一步：常态采集 smoke。**
- **2026-10-03** —— 建线。任务书 / loop / 记忆 / 产物目录就位。
- **2026-10-03** —— ⚠️ **首轮空转（已修）**：loop 拉起后 cline 报
  `The supported API model names are deepseek-flash, deepseek-v4-pro, but you passed deepseek-v4-pro-fp4`
  → 本轮什么都没干却 `exit 0`，且 `WAITING:1` 触发长睡。修复：① loop `MODEL` 改**规范 ID `deepseek-flash`**
  （2026-10-03 实测 `GET https://api.deepseek.com/models` → 官方仅 `deepseek-flash` / `deepseek-v4-pro`；`deepseek-v4-flash` 非官方 ID）；
  ② `WAITING` 置 `0`；③ loop 增加"抓 cline 致命错→强制短睡重试"兜底；④ 睡眠改为**对齐 BaiZe**（`SLEEP_SHORT=60` / `SLEEP_LONG=1800`）。
  **待 loop 重启后执行前期任务 T1–T4。**

---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-news/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
