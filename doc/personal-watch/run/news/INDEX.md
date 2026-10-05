# INDEX — 新闻摘要索引

> 由 **news agent** 维护：每轮落盘后更新当日计数与累计。
> 摘要文件：包内 `news/<YYYY-MM-DD>.md`；去重台账：`news/SEEN.md`。
> **计数口径（T8.3）**：`news 条数` **只计 §0.1 定义的「新闻」**；非新闻**单列计数**（依 T8 修订版**不入摘要**，仅存 `SEEN.md` 防重复评估）。

| 日期 | news 条数 | 非新闻 条数 | 文件 | 备注 |
|:--|--:|--:|:--|:--|
| 2026-10-03 | 61 | 26 | [2026-10-03.md](2026-10-03.md) | 第一轮 smoke（原 16 → **news 3**）+ 第二轮（原 15 → **news 6**）+ **第三轮 · 中文权威源（T9）news 6（中文 4 / 英文 2）** + **第四轮 · 常态采集 news 15（中文 11 / 英文 4）** + **第五轮 · 常态采集 news 5（中文 4 / 英文 1）** + **第六轮 · 常态采集 news 9（中文 7 / 英文 2）** + **第七轮 · 常态采集 news 6（中文 3 / 英文 3）** + **第八轮 · 常态采集 news 4（中文 2 / 英文 2）** + **第九轮 · 常态采集 news 7（中文 5 / 英文 2；含 IT之家首页补漏 10-02 漏收 5 条）**。非新闻 26 条（feature / opinion / analysis / paper / tool / discussion）仅存 `SEEN.md`。来源：IT之家 · 量子位 · 爱范儿 · 中新网 · 央视网 · 联合国新闻 · The Register · WSJ · NYT · Guardian · NBC · Fortune · TechCrunch · Ars Technica · Anthropic · NVIDIA · Aleph Alpha · CBS News · WIRED · Tom's Hardware · HN(Algolia) |
| 2026-10-04 | 8 | 0 | [2026-10-04.md](2026-10-04.md) | **第十轮 · 常态采集 news 8（中文 4 / 英文 4）**；国庆假期中文权威源 AI 类增量稀薄（多为时政/体育/民生）→ 按 §0.1 只收真新闻。来源：The Guardian · The Register · The New Stack · The Telegraph · 量子位 · IT之家 · 雷峰网 |
| 2026-10-05 | 25 | 19 | [2026-10-05.md](2026-10-05.md) | **第十一轮 · 常态采集 news 8（中文 6 / 英文 2）** + **第十二轮 · 补漏 +1（量子位《Hinton 首篇 RSI 论文》）** + **第十三轮 · +1（IT之家《JEDEC 硅光子可靠性标准 JESD264》）** + **第十四轮 · +8（中文 3 / 英文 5）** + **第十五轮 · +4（中文 4，IT之家 ×2〔华为×高通专利许可协议 · 台达×英伟达 Hyperion 自动驾驶〕/ 中新网 ×2〔机器人在北京上"幼儿园" · AI 催生浙江文旅新场景〕）= news 22（中文 15 / 英文 7）（与 N1 第 3~7 轮语料抓取并行）。来源：IT之家 · 量子位 · 中新网 · The Guardian · The New York Times · TechCrunch · WIRED。⚠️ **联合国新闻·中文源 404**；The Register atom 本轮 ParseError；Guardian/theguardian 判源失败（如实记录）；GDELT 未用。非新闻 15 条（opinion/analysis/feature/tool）仅存 `SEEN.md` 防重 + **第十六轮 · +0**（与 N1 第 7 轮收尾并行；`cn_news` 30 条均假期/民生/时政 → 不收；量子位 `501700`、中新网 `10708128` 已在账 → 去重；**第十七轮 · +1（IT之家《索尼向 Meta 转让 419 项 XR 专利》）**——`cn_news` 40 条均假期/民生/时政 → 不收，联合国中文源仍 404，量子位头部均已在账，HN 命中多 opinion/超窗） + **第十八轮 · +0**（与 L1 §4.4 措辞信号加固并行；`cn_news` 40 条均假期/民生/时政 → 不收，联合国中文源仍 404，IT之家新增候选「鸿海 9 月营收创新高」判非清单 → 不收，**新试「爱范儿 feed」无当日新增**〔feature/超龄〕，`web_search`(CN-Bing) 8 条均 SEO 聚合 → 不收） + **第十九轮 · +2（英文 1 / 中文 1）**——**TechCrunch《Trump unveils his new Super Intelligence Force》**（10-04，美国「超级智能部队」组建）· **钛媒体《马斯克为 AI 改名：SpaceXAI 将更名 SpaceXSI》**（10-05，马斯克 X 表态）；`cn_news` 40 条均假期/民生/时政 → 不收，**新试「钛媒体 feed」为活源**（4 条 analysis 仅存 `SEEN.md`），The Register/机器之心 atom 仍 ParseError，雷峰网头部软文/文体/法律 → 不收）|

**累计收录：news 94 条**（另非新闻 45 条，仅存 `SEEN.md` 防重）

> 🧭 **工具**：免 key MCP `web-search-free` —— `web_search`（CN-Bing/360）· `search_news`（HN/GDELT）· `rss_latest`（**含新增中文 dated 源：量子位 `qbitai.com/feed`、IT之家 `ithome.com/rss/`**）· **`cn_news`（T10 中文活源统一入口）**。
> 📄 中文入口用法与自测：`news/FETCH_CN_NEWS.md`。