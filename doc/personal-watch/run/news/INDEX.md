# INDEX — 新闻摘要索引

> 由 **news agent** 维护：每轮落盘后更新当日计数与累计。
> 摘要文件：包内 `news/<YYYY-MM-DD>.md`；去重台账：`news/SEEN.md`。
> **计数口径（T8.3）**：`news 条数` **只计 §0.1 定义的「新闻」**；非新闻**单列计数**（依 T8 修订版**不入摘要**，仅存 `SEEN.md` 防重复评估）。

| 日期 | news 条数 | 非新闻 条数 | 文件 | 备注 |
|:--|--:|--:|:--|:--|
| 2026-10-03 | 44 | 22 | [2026-10-03.md](2026-10-03.md) | 第一轮 smoke（原 16 → **news 3**）+ 第二轮（原 15 → **news 6**）+ **第三轮 · 中文权威源（T9）news 6（中文 4 / 英文 2）** + **第四轮 · 常态采集 news 15（中文 11 / 英文 4）** + **第五轮 · 常态采集 news 5（中文 4 / 英文 1）** + **第六轮 · 常态采集 news 9（中文 7 / 英文 2）**。非新闻 22 条（feature / opinion / analysis / paper / tool / discussion）仅存 `SEEN.md`。来源：IT之家 · 量子位 · 中新网 · 央视网 · 联合国新闻 · The Register · WSJ · NYT · Guardian · NBC · Fortune · TechCrunch · Ars Technica · Anthropic · NVIDIA · Aleph Alpha · CBS News · HN(Algolia) |

**累计收录：news 44 条**（另非新闻 22 条，仅存 `SEEN.md` 防重）

> 🧭 **工具**：免 key MCP `web-search-free` —— `web_search`（CN-Bing/360）· `search_news`（HN/GDELT）· `rss_latest`（**含新增中文 dated 源：量子位 `qbitai.com/feed`、IT之家 `ithome.com/rss/`**）· **`cn_news`（T10 中文活源统一入口）**。
> 📄 中文入口用法与自测：`news/FETCH_CN_NEWS.md`。