# 搜索 / 新闻 API 调研与选型报告（news 线 · T1–T4）

> 生成时间：2026-10-03 ｜ 采集/测试主机：`liuyang@iZuf65t80q2n4qgbjqbcp0Z`（阿里云，中国网络）
> 口径：**能真跑就真跑**；额度/限制**必标来源**（`已实测` = 本机真跑；`据官方文档` = 官方页面；`待验证` = 官方页面本机不可达/未取到数字）。
> 铁律：**不编造**、**不把"据说"当结论**、失败**贴原始报错**、控制频率**省额度**。

---

## 0. 一句话结论 + 推荐方案

**本机（中国网络）在没有付费 key 的前提下**，可稳定使用的免 key 组合是：

| 用途 | 选定方案 | 说明 |
|:--|:--|:--|
| **Web 搜索** | **抓取 CN-Bing（`cn.bing.com`）主 + 360（`so.com`）备** | 免 key、中文友好；已封装为 MCP `web-search-free`（见 §3） |
| **新闻/信号取数** | **Hacker News API + GDELT Doc API + 官方 RSS** | 免 key；RSS 覆盖新华/人民/中新/Arn/arXiv 等 |
| **付费/需 key 备选** | Tavily / Exa / Guardian / GNews / Currents … | 本机多数**可连**，但需注册 key（部分需信用卡） |

**关键判据（本机网络事实）**：Google、DuckDuckGo、Brave、Yahoo、公共 SearXNG、newsapi.org、BBC、Reuters、Google News RSS **全部不可达**（timeout/被墙）；而 CN-Bing、360、Bocha、Hacker News、GDELT、Tavily、Exa、SerpAPI 及多家国内 RSS **可达**。→ 选型必须**以本机可达性为准**，不能只抄文档。

**已交付**：
- MCP server：`news/mcp_web_search_free.py`（已封 3 个工具：`web_search` / `search_news` / `rss_latest`）
- MCP 配置：`news/cline_mcp_config.json`（配置路径/命令/参数见 §3）
- 本报告 HTML：`news/API_COMPARISON.html`（自包含）

---

## 1. Web Search API 对比（T1）

| # | 名称 | 官网 / 文档 | 免费额度 | 速率限制 | 需 key / 信用卡 / 审核 | 中文 | 数据来源 | 条款 / 限制 | 本机实测 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| 1 | **CN-Bing 网页抓取** | https://cn.bing.com/ | 免费（HTML 网页） | 非官方，反爬，勿高频 | 🚫 无需 key | ✅ 强 | Bing 索引 | 非官方 API；仅个人低频；可能被限流/改版 | ✅ **已实测**：200，解析出标题+链接 |
| 2 | **360 搜索（so.com）** | https://www.so.com/ | 免费（HTML 网页） | 非官方，反爬 | 🚫 无需 key | ✅ 强 | 360 索引 | 非官方；结果链接为 302 跳转 | ✅ **已实测**：200，解析成功 |
| 3 | Bocha 博查 | https://open.bochaai.com/ | 无永久免费，按量付费 | 按套餐 | ✅ key；充值/实名 | ✅ 强 | 自建（近千亿网页/生态） | 商用需授权 | ⚠️ **已实测**：API 可达，但**现有 key 403「not enough money or package quota」** |
| 4 | Brave Search API | https://brave.com/search/api/ | 免费 2,000 queries/月（1 QPS） **待验证** | 1 req/s | ✅ key + **信用卡** | 弱 | 自建**独立索引** | 免费层非商用 | ❌ 本机**不可达**（timeout）→ 额度**待验证** |
| 5 | Google Programmable Search (CSE) | https://developers.google.com/custom-search/v1/overview | 100 query/天；超量 $5/1000；≤10k/天 **待验证** | — | ✅ key + 信用卡 | ✅ | Google 索引 | 需展示 Google 署名 | ❌ 本机 **google 被墙** |
| 6 | Tavily | https://tavily.com/ | 免费额度（官网未列明数字）**待验证** | 按套餐 | ✅ key | 中英 | 自建爬取+索引（面向 agent） | 商用需付费 | ✅ **已实测**：本机可达（HTTP 200） |
| 7 | Exa | https://docs.exa.ai/reference/pricing | 免费 **$10/月**（≈2,500 instant 检索），每月 1 日重置，**无需付款方式** | 见文档 | ✅ key（免费注册） | 弱 | 神经/语义索引 | 按量计费 | ✅ 本机可达 ｜ **据官方文档** |
| 8 | SerpAPI | https://serpapi.com/ | 免费 100 search/月 | — | ✅ key | ✅ | **转售** Google/Bing/百度等 | 明确为转售 | ✅ **已实测**：本机可达（HTTP 200） |
| 9 | DuckDuckGo（`ddgs`） | https://pypi.org/project/ddgs/ | 免费、无 key | 反爬 | 🚫 无需 key | 弱 | 转售 Bing/DDG/Yahoo 等 | 非官方 | ❌ **已实测**：失败（`search.yahoo.com ... operation timed out`）→ DDG/Yahoo 被墙 |
| 10 | SearXNG（自建/公共） | https://docs.searxng.org/ | 免费（**自建**） | 自定 | 🚫 无需 key | ✅（可配引擎） | 聚合 **261** 个引擎 | AGPL；须尊重上游 robots | ❌ **已实测**：8 个公共实例**全部不可达** → 需自建（本机资源） |
| 11 | Mojeek | https://www.mojeek.com/support/api/search/ | 付费（未见免费层）**待验证** | 按套餐 | ✅ key | 弱 | 自建**独立索引** | 付费 | ❌ **已实测**：本机搜索 HTTP 403 |
| 12 | Bing Web Search (Azure) | https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/overview | F1 免费层（额度**待验证**） | 见文档 | ✅ key + **Azure 订阅 + 信用卡** | ✅ | Bing 索引 | 明确为「搜索式」用途 | ⚠️ 未实测（需 key）；但 `cn.bing.com` 已实测可达 |

---

## 2. News API / 订阅源对比（T3）

| # | 名称 | 官网 / 文档 | 免费额度 | 速率限制 | 需 key | 语种 / 地域 | 权威性评估 | 授权 / 署名 | 本机实测 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| 1 | **Hacker News API** | https://github.com/HackerNews/API | 免费 | **官方称「无速率限制」** | 🚫 无需 | 英文为主 | 极客社区**一手讨论** | MIT | ✅ **已实测**：`topstories` 200；Algolia 检索 200 |
| 2 | **Hacker News (Algolia)** | https://hn.algolia.com/api | 免费 | 未标明（勿高频） | 🚫 无需 | 英文为主 | 一手讨论检索 | — | ✅ **已实测**：按时间检索，返回标题/时间/URL |
| 3 | **GDELT Doc 2.0 API** | https://www.gdeltproject.org/ | 免费 | **有频控**（连续查询→429） | 🚫 无需 | **100+ 语种** | 全球新闻**事件聚合**（转售/聚合） | 开放 | ⚠️ **已实测**：可达 200（单次约 13s），**高频即 429**；query 关键词需 ≥3 字符 |
| 4 | Guardian Open Platform | https://open-platform.theguardian.com/ | 免费 dev key（额度 **待验证**） | 见文档 | ✅ key | 英文 | 一手媒体（卫报） | 需署名 | ⚠️ **已实测**：API host 可达（401 未授权）；**文档站本机被墙** |
| 5 | NYT API | https://developer.nytimes.com/ | 免费 500 req/天 **待验证** | 5 req/min **待验证** | ✅ key | 英文 | 一手媒体（纽时） | 需署名 | ⏳ 未实测（待验） |
| 6 | NewsAPI.org | https://newsapi.org/ | 免费 dev 100 req/天、24h 延迟、**非商用** | — | ✅ key | 多语 | **聚合**（多源） | 免费层非商用 | ❌ **已实测**：本机**不可达**（timeout） |
| 7 | GNews | https://gnews.io/ | 免费 **100 req/天**、**非商用**、仅近 30 天 | 每日重置 | ✅ key（**无需信用卡**） | 41 语 / 71 国 | 聚合（80,000+ 源） | 免费层非商用 | ✅ 本机可达 ｜ **据官方文档** |
| 8 | NewsData.io | https://newsdata.io/ | 免费额度（页面为 JS 渲染，**待验证**） | — | ✅ key | 多语多国 | 聚合 | 商用需付费 | ⚠️ **已实测**：host 可达（401 未授权）；额度**待验证** |
| 9 | Currents API | https://currentsapi.services/ | 免费 **250 req/天**（≤20 结果/次，30 天历史） | 每日 00:00 UTC 重置 | ✅ key | 20+ 语 / 168 国 | 聚合 | 不可再分发 | ✅ 本机可达 ｜ **据官方文档** |
| 10 | Mediastack | https://mediastack.com/ | 免费 **100 calls/月**、**非商用**、延迟数据 | — | ✅ key | 13 语 / 50+ 国 | 聚合（7,500+ 源） | 免费层非商用 | ✅ 本机可达 ｜ **据官方文档** |
| 11 | TheNewsAPI | https://www.thenewsapi.com/ | 免费 **100 req/天**、3 篇/次 | — | ✅ key | 全语种访问 | 聚合 | — | ✅ 本机可达 ｜ **据官方文档** |
| 12 | **官方 RSS · 中文** | 新华 http://www.xinhuanet.com/politics/news_politics.xml ｜ 人民 http://www.people.com.cn/rss/politics.xml ｜ 中新 https://www.chinanews.com.cn/rss/scroll-news.xml | 免费 | 勿高频 | 🚫 无需 | 中文 | **一手官媒** | 按源署名 | ✅ **已实测**：3 源均 200 且解析出条目 |
| 13 | **官方 RSS · 英文/学术** | arXiv https://export.arxiv.org/api/query ｜ Ars Technica https://arstechnica.com/feed/ | 免费 | 勿高频 | 🚫 无需 | 英文 | **一手**（论文/媒体） | 按源署名 | ✅ **已实测**：arXiv API 200；Ars 200 |
| 14 | Anthropic / DeepMind News | https://www.anthropic.com/news ｜ https://deepmind.google/ | 免费（网页） | 勿高频 | 🚫 无需 | 英文 | **一手**（实验室官网） | 按源署名 | ✅ **已实测**：2 站 200（HTML，需解析） |
| 15 | Google News RSS | https://news.google.com/rss | 免费 | — | 🚫 无需 | 多语 | 聚合 | — | ❌ **已实测**：本机**不可达** |
| 16 | BBC / Reuters RSS | https://feeds.bbci.co.uk/news/rss.xml | 免费 | — | 🚫 无需 | 英文 | 一手媒体 | 按源署名 | ❌ **已实测**：BBC timeout、Reuters timeout、AP 403 |
| 17 | 机器之心 / 36氪 feed | https://www.jiqizhixin.com/rss ｜ https://36kr.com/feed | — | — | 🚫 无需 | 中文 | 科技媒体 | — | ⚠️ **已实测**：机器之心 RSS 已下线（302→data-service）；36氪 `/feed` 返回 SPA HTML 非 RSS |

---

## 3. 选定方案与 MCP 配置（T2）

### 3.1 选定
- **web_search** → **CN-Bing（主）+ 360（备）**：本机**唯一**既免 key、又中文友好、又真跑通的通用网页搜索。
- **news** → **Hacker News + GDELT + 官方 RSS**：免 key、可溯源、覆盖中英。

### 3.2 MCP server（已封装）
文件：`news/mcp_web_search_free.py`（工具：`web_search` / `search_news` / `rss_latest`）
依赖：`requests`（已装）、`mcp`（已装 2.3.0）。用 mcp 2.x 的 `MCPServer`（`FastMCP` 在新版改名），并兼容 1.x。

### 3.3 cline MCP 配置片段
配置路径：`news/cline_mcp_config.json`（并入目标机 cline 的 MCP 配置文件：`{"mcpServers": {...}}`）

```json
{
  "mcpServers": {
    "web-search-free": {
      "command": "python3",
      "args": [
        "/home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/mcp_web_search_free.py"
      ],
      "description": "免 key 网页搜索/新闻取数（CN-Bing + 360 + HackerNews + RSS）",
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

> 参考现成件：仓库根 `mcp_web_search.py`（bocha 版）+ `cline_mcp_config.json`。**因原 bocha key 额度用尽（§4 实测 403），故改用免 key 自建后端。**

### 3.4 MCP 实测证据（stdio 全链路）

```bash
$ python3 /tmp/mcp_stdio_test.py
[1] initialize -> {"name": "web-search-free", "version": ""}
[2] tools/list -> ['web_search', 'search_news', 'rss_latest']
[3] tools/call web_search ->
[web_search:bing] query='EU AI Act regulation'（2 条）
1. Your gateway to the EU, News, Highlights | European Union
   🔗 https://european-union.europa.eu/index_en
2. European Commission, official website - European Commission
   🔗 https://commission.europa.eu/index_en
server exit code: 0
```

---

## 4. 实测记录（命令 + 原始输出/报错）

### 4.1 网络可达性探针（`curl --max-time`，2026-10-03）

```
duckduckgo.com                         => 超时(被墙)
html.duckduckgo.com                    => 超时(被墙)
www.google.com                         => 超时(被墙)
api.search.brave.com                   => 超时(被墙)
searx.be / priv.au / baresearch.org …  => 超时(全部公共实例被墙)
newsapi.org                            => 超时(被墙)
feeds.bbci.co.uk/news/rss.xml          => 超时(被墙)
www.reuters.com                        => 超时(被墙)
news.google.com/rss                    => 超时(被墙)
www.theguardian.com / open-platform    => 超时(被墙); 但 content.guardianapis.com => 401(可达)
--------------------------------------------------------------------------------
cn.bing.com                            => 200(可用)   www.bing.com => 302
www.so.com                             => 200(可用)
api.bocha.cn                           => 404(host 可达)
hacker-news.firebaseio / hn.algolia    => 301 / 200(可用)
www.gdeltproject.org / api.gdeltproject=> 301 / 200(可用，慢)
api.tavily.com / api.exa.ai / serpapi.com => 200 / 404 / 200(可达, 需key)
gnews.io / newsdata.io / mediastack.com / thenewsapi.com / currentsapi => 200~401(可达, 需key)
xinhuanet / people.com.cn / chinanews   => 200(RSS 可用)
arxiv.org / export.arxiv.org / arstechnica.com/feed => 200(可用)
anthropic.com / deepmind.google         => 200(可用)
huggingface.co / openai.com             => 超时 / 403
```

### 4.2 `ddgs`（DuckDuckGo）失败原文（配合 §1#9）

```bash
$ python3 -c "from ddgs import DDGS; print(DDGS().text('OpenAI GPT', max_results=3))"
DDGS ERROR: TimeoutException error sending request for url
(https://search.yahoo.com/search;...?p=OpenAI+GPT) > operation timed out
```

### 4.3 原 bocha key 额度用尽原文（配合 §1#3）

```bash
$ curl -s -X POST https://api.bocha.cn/v1/web-search -H 'Authorization: Bearer sk-****' \
    -H 'Content-Type: application/json' -d '{"query":"人工智能 监管 立法","count":3}'
HTTP 403
{"message": "You do not have enough money or package quota", "log_id": "6c4e234a2c5df120", "code": "403"}
```

### 4.4 CN-Bing 抓取（免 key，解析标题+链接）

```
$ GET https://cn.bing.com/search?q=AI+regulation+EU
HTTP 200  b_algo count: 10
- AI工具集官网 | 1000+ AI工具集合 …        | https://ai-bot.cn/
- AI 工具完全指南（2026）…                 | https://tanqingbo.cn/ai-tools-guide/
- AI能力体验中心_Demo中心                   | https://ai.baidu.com/experience
```

### 4.5 360 搜索抓取（免 key，备用后端）

```
$ GET https://www.so.com/s?q=AI+%E7%9B%91%E7%AE%A1
HTTP 200  parsed: 8
- 欧盟批准简化 AI 监管规则,明令禁止 AI 用于生成色情内容_ZAKER新闻 | https://www.so.com/link?m=...
- 金安区: 互联网+AI监管 …_六安市人民政府                  | https://www.so.com/link?m=...
```

### 4.6 Hacker News（Algolia，免 key）

```
$ GET https://hn.algolia.com/api/v1/search_by_date?query=AI&tags=story&hitsPerPage=3
- People will be AI's app layer | 2026-10-03T04:46:25Z | https://twitter.com/...
- Where AI learns to do real work | 2026-10-03T04:40:10Z | https://labelbox.com/
```

### 4.7 GDELT Doc API（免 key，含 429 频控原文）

```
$ GET https://api.gdeltproject.org/api/v2/doc/doc?query="artificial intelligence" regulation
HTTP 200  (≈13s)
{"articles":[{"title":"Россия будет играть важную роль в регулировании ИИ ...",
  "seendate":"20260717T101500Z","domain":"ria.ru","language":"Russian"}, ...]}

# 连续快速查询时：
HTTP 429  (频控)   ← 高频会触发；需间隔请求
# query 关键词过短时：
Your search contained a keyword that was too short.
```

### 4.8 官方 RSS（免 key，中文/英文）

```
$ GET https://www.chinanews.com.cn/rss/scroll-news.xml
HTTP 200
<title>亚运会开幕后第十三个比赛日：亮点纷呈 中国代表团再获七金</title>
<link>https://www.chinanews.com.cn/ty/2026/10-03/10707434.shtml</link>
<pubDate>Sat, 3 Oct 2026 12:53:46</pubDate>

$ 新华网/人民网 RSS => 200；arXiv API => 200（<title>TACO: Ternary …Optimizer for LLM Fine-Tuning</title>）
```

---

## 5. 风险与限制

1. **非官方抓取的稳定性**：CN-Bing / 360 为 HTML 抓取，**页面改版即可能失效**，且属灰色地带 → 仅**个人低频**使用，已内置自动回退（Bing→360），并保留升级到付费 API 的口子。
2. **GDELT 频控**：连续请求快速触发 **429** 且单次约 13s → 采集时**必须限频**（建议间隔 ≥10s，并做 429 退避）。
3. **额度/限制「待验证」项**：Brave、Google CSE、Guardian、NewsData、Bing(Azure)、NYT 的免费额度/速率因**官方页面本机不可达**或**未取到数字**，本次**未证实**；正式采用前需在其官网复核。
4. **付费/需 key 方案本机可达但非零成本**：Tavily/Exa/SerpAPI 等虽可达，但需注册（部分需信用卡），免费额度有限 → 仅作**备选/升级路径**。
5. **中文覆盖**：免 key 方案里，中文权威面主要依赖**国内官媒 RSS**（新华/人民/中新）；通用中文搜索依赖 **CN-Bing/360 抓取**。Boacha 是质量最好的中文 API，但**需付费**。
6. **合规**：所有方案均**只取标题/摘要 + 链接**，不采付费墙正文、不整篇转载；尊重 robots 与频率。
7. **本机环境绑定**：以上「可用/不可用」结论**强依赖本机网络**（中国节点）。换机（如境外节点）结论可能反转——换机第一步须重跑 §4.1 探针。

---

## 附录 A · 复现命令

```bash
git -C /home/liuyang/super_intelligence_2035 pull --rebase --autostash
cd /home/liuyang/super_intelligence_2035/doc/personal-watch/run/news
# 1) 直接跑函数（真查询）
python3 -c "import mcp_web_search_free as m; print(m.web_search('AI regulation',3)); print(m.search_news('LLM',3,'hn'))"
# 2) 跑 MCP（stdio）——可接任意 MCP 客户端；本报告用 /tmp/mcp_stdio_test.py 验证
python3 mcp_web_search_free.py
```

## 附录 B · 关键文件
- MCP server：`news/mcp_web_search_free.py`
- MCP 配置：`news/cline_mcp_config.json`
- 本报告 HTML：`news/API_COMPARISON.html`
