# web-search MCP（免 key）— news agent 版

> **来源**：**supervisor 现用**的 `web-search` MCP **原样副本**（用户 2026-10-05 指定「按你现有的工具配置」）。
> 上游路径（Windows）：`E:\code\stem_fest\mcp_server\web_search_mcp_server.py`。
> 🚫 **不要改这里的 `web_search_mcp_server.py`** —— 改了就会与 supervisor 现用版**分叉**；要改请先问 supervisor。

## 1. 是什么

- **FastMCP stdio 服务器**，**全程免 API Key**；6 个工具：

| 工具 | 作用 |
|:--|:--|
| `web_search` | 通用网页搜索（ddgs 多引擎轮换，`backend=auto` 并发去重合并） |
| `search_news` | 新闻搜索（返回日期 / 来源） |
| `search_images` | 图片搜索（原图 / 缩略图直链） |
| `wiki_lookup` | 维基百科检索 + 首段摘要（MediaWiki API） |
| `fetch_page` | 抓取网页正文（优先 `ddgs.extract` → markdown/纯文本，支持分页续读） |
| `search_status` | 自检：依赖版本、可用引擎、默认参数；`live_probe=True` 会真发一次搜索 |

- **依赖**：`mcp`（FastMCP）+ `ddgs`（supervisor 机实测 **9.16.0**）；可选 `beautifulsoup4` + `lxml`（仅 `fetch_page` 的 HTML 回退路径）。
- **环境变量（均可选）**：`WEB_SEARCH_DEFAULT_REGION`（默认 `cn-zh`）· `WEB_SEARCH_DEFAULT_BACKEND`（默认 `auto`）· `WEB_SEARCH_MAX_RESULTS`（默认 `8`）。

## 2. 安装

```bash
cd ~/super_intelligence_2035/doc/personal-watch/run
python3 -m pip install -r news/mcp_ddgs/requirements.txt
# 国内慢：python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r news/mcp_ddgs/requirements.txt

# ① 离线自检（不联网，先证明"装对了"）
python3 news/mcp_ddgs/web_search_selftest.py        # 应全 PASS

# ② 联网自检（真发一次搜索；这一步才反映本机网络能否用）
python3 news/mcp_ddgs/web_search_mcp_server.py --help 2>/dev/null || true
#   ↑ 该服务器是 stdio 协议，直接跑会"等输入"；联网验证请按 §4 用 search_status(live_probe=True)
```

## 3. 注册进 cline

⚠️ 新运行机（腾讯 `VM-0-6-ubuntu`）的 cline 配置**布局与旧机不同**（`~/.cline/data/globalState.json` **不存在**）→ 先探明：

```bash
ls -la ~/.cline/ 2>/dev/null
find ~ -maxdepth 6 -iname '*mcp*' 2>/dev/null
cline --help
```

在找到的 MCP 配置文件（旧机对应 `~/.cline/data/settings/cline_mcp_settings.json`）里加：

```json
"web-search": {
  "command": "python3",
  "args": ["/home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/mcp_ddgs/web_search_mcp_server.py"],
  "env": {
    "WEB_SEARCH_DEFAULT_REGION": "cn-zh",
    "WEB_SEARCH_DEFAULT_BACKEND": "auto",
    "PYTHONIOENCODING": "utf-8"
  },
  "disabled": false,
  "timeout": 120
}
```
> 🚫 配置里**不得出现任何 key/token**（本服务器本来就不需要）。改配置前**先备份**。

## 4. 实测（⭐ 关键：本机在中国网络，海外引擎可能不可达）

1. **逐引擎实测**（把每个引擎的成功/失败/报错记下来）：
   `ddgs` 的回退顺序是 `auto → duckduckgo → brave → bing → google → mojeek → yahoo → startpage`。
   用 `search_status(live_probe=True)` 先探一次；再写个 3 行脚本逐个 `backend=` 试，做成**实测表**。
2. **配置生效后真跑一次**：工具列表出现 6 个工具 → 各跑一次 `web_search` / `fetch_page`，拿回**带 URL 的结果**。
3. **与本线既有 `mcp_web_search_free.py`（CN-Bing + 360）互补**：哪套通就用哪套；**两套都注册也行** → 双后端。

## 5. 已知限制 / 排错

- 直接抓 DuckDuckGo HTML 约 15 次请求后会被风控 → 本服务器**统一交给 `ddgs`** 处理 cookie/指纹并跨引擎轮换，**不要自己写裸抓**。
- 缺依赖时报 `缺少依赖 ddgs。请先安装：pip install ddgs`。
- `fetch_page` 在 `ddgs.extract` 失败时会回退到 `bs4`；未装 `beautifulsoup4` 时会报错 → 装依赖即可。
- 若**所有**引擎在本机都不通：**如实记录**，并回退到本线 CN-Bing/360 那套（`mcp_web_search_free.py`）+ CLI 直调。
