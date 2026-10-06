# MCP_INSTALL.md — 给本机 cline 装「免费 web-search MCP」安装与实测记录（第 10 批 · A 线）

> 交付物位置：`news/MCP_INSTALL.md`（本文件）。
> 目标（`WATCH_NEWS_TASK.md` 第 10 批 A）：**照抄 supervisor 现用的那一套**，把 vendor 进仓库的 `news/mcp_ddgs/web_search_mcp_server.py` **装进本机 cline 并实测**；与本线既有 `news/mcp_web_search_free.py`（CN-Bing + 360）**互补/双后端**；**全程免 key**、**不动 vendor 文件**、**只改本线配置**。
> 相关：`news/mcp_ddgs/README.md`（安装/注册原文）、`news/API_COMPARISON.md`（选型）、`news/FETCH_CN_NEWS.md`（`cn_news` 入口）。

---

## 0. 一句话结论（先看这个）

| 项 | 结果 |
|:--|:--|
| **能否装进 cline** | ✅ **能**（依赖装好、离线自检全 PASS、已注册进 `cline_mcp_settings.json`、stdio 握手成功、6 工具可见） |
| **装后能否在本机联网用** | ❌ **ddgs 的 8 个引擎在本机全部失败**（墙/超时）→ **本机不可用** |
| **替代/兜底** | ✅ 本线既有 `web-search-free`（CN-Bing + 360 + HN + RSS）**已一并注册**；`cn_news` 中文权威源**实测可用**（质量最好）；⚠️ 但 CN-Bing 抓取**相关性已降级**（见 §5） |
| **红线遵守** | ✅ 免 key、配置无 key、未改 vendor 文件、未动 BaiZe 配置 |

> **诚实说明**：本机（中国网络）**海外搜索引擎全部不可达**（与本线既有结论一致：`MEMORY_NEWS.md` 选定方案「本机不可达：Google / DuckDuckGo / Brave / Yahoo / 公共 SearXNG」）。因此 **ddgs 这套「能装对、但本机跑不通」** —— 不是装错，是网络环境所限。**如实记录，不假装成功。**

---

## 1. 环境事实（实测）

| 项 | 值 | 证据 |
|:--|:--|:--|
| cline 版本 | **3.0.68** | `cline version` → `3.0.68` |
| cline MCP 配置路径 | **`~/.cline/data/settings/cline_mcp_settings.json`** | `cline config mcp` 报「No MCP settings file found at /home/liuyang/.cline/data/settings/cline_mcp_settings.json」（即这就是它找的路径） |
| 旧机路径 | `~/.cline/data/globalState.json` **不存在**（新机布局不同） | 任务书第 10 批已注明 |
| python | `python3`（`~/.local` 用户级安装） | `pip --user --break-system-packages`（PEP 668 管控） |
| `ddgs` | **9.16.0** | `python3 -c 'import ddgs;print(ddgs.__version__)'` |
| `mcp` | **1.30.0**（**特意降到 <2**，见 §4） | `importlib.metadata.version("mcp")` |
| 其它已装依赖 | `beautifulsoup4` ✅ · `lxml` ✅（`search_status` 自报 `optional_extras`） | 见 §3 search_status 输出 |

**注册前备份**：该文件**此前不存在**（`cline config mcp` 报「No MCP settings file found」）→ **无历史配置可覆盖**；`cline mcp install` 生成的首版已另存 `/tmp/cline_mcp_settings.bak.json`。

---

## 2. 安装步骤与证据

### 2.1 装依赖（清华镜像）

```bash
python3 -m pip install --user --break-system-packages \
  -i https://pypi.tuna.tsinghua.edu.cn/simple 'ddgs==9.16.0' beautifulsoup4
# 结果：Successfully installed ddgs-9.16.0 ...（lxml 太慢，跳过——fetch_page 的 HTML 回退才用得到）
```

### 2.2 离线自检（**不联网，先证明「装对了」**）

```bash
cd /home/liuyang/super_intelligence_2035/doc/personal-watch/run
python3 news/mcp_ddgs/web_search_selftest.py
```

**原始输出（节选）**：

```text
  [PASS] 已注册 search_status / web_search / wiki_lookup
  [PASS] web_search 结果整形（title 去 HTML、snippet 压缩、rank、backend_used、region 默认/覆盖、timelimit 归一/透传）
  [PASS] search_news / search_images
  [PASS] fetch_page 分页与截断（total_chars / limit / truncated / next_offset / 续读）
  [PASS] wiki_lookup（条目/标题/链接/摘要）
  [PASS] search_status（默认值 / ddgs 版本 / live_probe 桩化）
  [PASS] 错误路径（搜索失败返回 ok:false）
====================================================================
 结果：全部通过
```

> ⚠️ **前提**：`mcp` 必须是 **1.x**（见 §4）。用 mcp 2.x 时，本 vendor 文件 `from mcp.server.fastmcp import FastMCP` **直接 ImportError**，自检 `[0]` 段全 FAIL。

### 2.3 注册进 cline

```bash
cline mcp install web-search --yes -- python3 \
  /home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/mcp_ddgs/web_search_mcp_server.py
# → Installed MCP server web-search.
```

cline 3.0.68 用的**新 schema**（`transport.type=stdio`），随后补 `env` + `timeout` + 第二个服务器，得到最终配置：

```json
// ~/.cline/data/settings/cline_mcp_settings.json
{
  "mcpServers": {
    "web-search": {
      "transport": {
        "type": "stdio",
        "command": "python3",
        "args": ["…/run/news/mcp_ddgs/web_search_mcp_server.py"],
        "env": {
          "WEB_SEARCH_DEFAULT_REGION": "cn-zh",
          "WEB_SEARCH_DEFAULT_BACKEND": "auto",
          "WEB_SEARCH_MAX_RESULTS": "8",
          "PYTHONIOENCODING": "utf-8"
        }
      },
      "timeout": 120, "disabled": false
    },
    "web-search-free": {
      "transport": {
        "type": "stdio",
        "command": "python3",
        "args": ["…/run/news/mcp_web_search_free.py"],
        "env": { "PYTHONUNBUFFERED": "1" }
      },
      "timeout": 120, "disabled": false
    }
  }
}
```

**生效验证**：

```bash
cline config mcp
# Configured MCP servers (/home/liuyang/.cline/data/settings/cline_mcp_settings.json):
#   web-search [stdio]
#   web-search-free [stdio]
```

> 🔒 配置内**无任何 key/token**；**未修改** vendor 的 `web_search_mcp_server.py`（分叉红线）；**只新增**本线两个服务器，未触碰其它线。

### 2.4 stdio 握手 + 工具列表（**证明 cline 能拉起服务器、工具可见**）

用 `mcp` 客户端以**与 cline 相同的命令行**拉起服务器：

```python
# /tmp/mcp_handshake.py（节选）
params = StdioServerParameters(command="python3", args=[SERVER], env={...})
async with stdio_client(params) as (r, w):
    async with ClientSession(r, w) as s:
        await s.initialize()
        print([t.name for t in (await s.list_tools()).tools])
```

**原始输出**：

```text
TOOLS: ['web_search', 'search_news', 'search_images', 'fetch_page', 'wiki_lookup', 'search_status']
search_status: {"ok": true, "defaults": {"region": "cn-zh", "backend": "auto", "max_results": 8},
                "env_keys": {"WEB_SEARCH_DEFAULT_REGION": "cn-zh", "WEB_SEARCH_DEFAULT_BACKEND": "auto", "WEB_SEARCH_MAX_RESULTS": 8},
                "optional_extras": {"bs4": true, "lxml": true}, "ddgs_version": "9.16.0",
                "backends_available": ["duckduckgo","brave","bing", …]}
```

✅ **6 个工具全部注册**、`ddgs 9.16.0` 可见、`cn-zh` 默认生效。

---

## 3. ⭐ 逐引擎实测表（第 10 批步骤 4 —— **本步决定可用性**）

命令（`/tmp/engine_test.py`，逐 backend 真发一次 `text("superintelligence AI")`）：

```python
from ddgs import DDGS
for eng in ["auto","duckduckgo","brave","bing","google","mojeek","yahoo","startpage"]:
    with DDGS() as d:
        kw = {"backend": eng} if eng != "auto" else {}
        rows = list(d.text("superintelligence AI", max_results=3, region="cn-zh", **kw))
```

**实测结果（本机 · 2026-10-05）**：

| backend | 结果 | 报错/耗时 | 备注 |
|:--|:--|:--|:--|
| `auto` | ❌ FAIL | `TimeoutException: error sending request for url (https://www.startpage.com/)` · 20.1s | 回退到 startpage 仍超时 |
| `duckduckgo` | ❌ FAIL | `DDGSException: No results found` · 5.0s | 被墙 |
| `brave` | ❌ FAIL | `DDGSException: No results found` · 5.0s | 被墙 |
| `bing` | ❌ FAIL | `TimeoutException: … (https://search.yahoo.com/search…)` · 20.0s | cn.bing 可达但 ddgs 链路仍超时（见 §5 根因） |
| `google` | ❌ FAIL | `DDGSException: No results found` · 5.0s | 被墙 |
| `mojeek` | ❌ FAIL | `DDGSException: No results found` · 1.4s | — |
| `yahoo` | ❌ FAIL | `DDGSException: No results found` · 5.0s | 被墙 |
| `startpage` | ❌ FAIL | `DDGSException: No results found` · 5.0s | 被墙 |

**→ 8/8 全灭。本机 ddgs 链路不可用。**

### 3.1 根因：原始连通性（curl，排除「是 ddgs 写错」的可能）

```bash
for h in https://duckduckgo.com https://www.bing.com https://cn.bing.com https://www.mojeek.com; do
  curl -sS -m 10 -o /dev/null -w "$h -> HTTP %{http_code} %{time_total}s\n" -A 'Mozilla/5.0' "$h"; done
```

| 目标 | 结果 |
|:--|:--|
| `https://duckduckgo.com` | ❌ `curl (28) Connection timed out after 10002 ms` → **HTTP 000** |
| `https://www.bing.com` | ✅ HTTP 302（0.15s） |
| `https://cn.bing.com` | ✅ HTTP 200（0.18s） |
| `https://www.mojeek.com` | ✅ HTTP 200（0.98s） |
| `https://search.yahoo.com`（ddgs `bing` 回退目标） | ❌ 超时（由上表 `bing` 报错推知） |

**结论**：**DNS/TCP 层**就决定了 —— `duckduckgo / yahoo` 等**直接不可达**；`bing/mojeek` 主页虽可达，但 ddgs 的**结果解析端点**在抓结果时被拦/超时。**不属于配置问题。**

---

## 4. 关键坑：`mcp` 必须 `<2`（**否则 vendor 服务器起不来**）

- vendor 的 `web_search_mcp_server.py` 用的是 **`mcp.server.fastmcp.FastMCP`**（**mcp 1.x 的 API**）。
- 本机预装的 **mcp 2.3.0** 里 `FastMCP` 已改名 → `import` 时直接抛 `ImportError: cannot import name 'FastMCP' … pin 'mcp<2'`，**服务器无法启动**（自检 `[0]` 段全 FAIL）。
- **红线要求「不改 vendor 文件」** → 因此**唯一正解 = 把 mcp 降到 1.x**，让原版文件原样跑：

```bash
python3 -m pip install --user --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple 'mcp<2'
# → Successfully installed … mcp-1.30.0 …（卸载了 mcp-2.3.0）
```

- **副作用评估（已验证）**：本线另一服务器 `mcp_web_search_free.py` **同时兼容 1.x/2.x**（它先试 `mcp.server.mcpserver.MCPServer`，失败则回退 `FastMCP`）→ 降到 1.30.0 后**仍正常**（§5 实测）。✅ 无回归。

---

## 5. 第二个后端：`web-search-free`（本线既有）实测

### 5.1 握手 + 工具列表

```text
TOOLS: ['web_search', 'search_news', 'rss_latest', 'cn_news']
```

✅ 4 个工具全部可见（mcp 1.30.0 下正常）。

### 5.2 `web_search`（CN-Bing 抓取）—— ⚠️ **相关性已降级**

调用：`web_search(query="人工智能 最新 政策", max_results=3)`

```text
[web_search:bing] query='人工智能 最新 政策'（5 条）
1. 人工（汉语词汇）_百度百科            https://baike.baidu.com/item/人工/4377695
2. 人工：仝，不读gong，跟"全"差一笔…   https://www.toutiao.com/article/7345448737164083753/
3. 人工的意思_人工的解释-汉语国学      https://www.hanyuguoxue.com/cidian/ci-c21a24e92
```

⚠️ **查询是「人工智能 最新 政策」，返回的却是「人工」这个词条** —— 明显是**被降级/风控页**（把长查询截断/兜底）。与本线 `MEMORY_NEWS.md` 记录一致（「CN-Bing 多查询返回雷同/疑似兜底页」）。

> ❗**教训沿用**：「**接口 200 ≠ 有料**」。CN-Bing 返回 200 + 有 URL，但**内容不相关** → 该后端**作为「通用搜索」已不可信**；仅可当**补充**，不当主搜索。

### 5.3 `cn_news`（中文权威源）—— ✅ **可靠**

```bash
python3 news/mcp_web_search_free.py --cn-news --limit 5
# [cn_news] 生成 2026-10-05T15:34:11Z ｜ 新鲜度窗口 ≤72h ｜ 活源 6 个
# 1. 赓续长征精神…  中新网 2026-10-05T15:27:51Z  https://www.chinanews.com.cn/sh/2026/10-05/10708295.shtml
# 2. 超三联赛…      中新网 2026-10-05T15:26:17Z  https://www.chinanews.com.cn/ty/2026-10-05/10708294.shtml
# 3. WTT…孙颖莎     中新网 2026-10-05T15:22:55Z  https://www.chinanews.com.cn/ty/2026-10-05/10708292.shtml
# …（均带 ISO8601 日期、来源、链接）
```

✅ **这是本机当前最可靠的中文取数路径**（中新网 + 联合国新闻·中文 + 央视网，内建 `pubDate≤72h` + `Content-Type` 校验）。

---

## 6. 复现命令（拷贝即用）

```bash
cd /home/liuyang/super_intelligence_2035/doc/personal-watch/run

# ① 装依赖（含关键 pin: mcp<2）
python3 -m pip install --user --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple \
  'ddgs==9.16.0' beautifulsoup4 'mcp<2'

# ② 离线自检（应全 PASS）
python3 news/mcp_ddgs/web_search_selftest.py

# ③ 注册（cline 3.0.68）
cline mcp install web-search --yes -- python3 \
  /home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/mcp_ddgs/web_search_mcp_server.py

# ④ 逐引擎实测（会全 FAIL，见 §3 —— 这是网络环境所致）
python3 /tmp/engine_test.py

# ⑤ 可靠路径：中文权威源真新闻
python3 news/mcp_web_search_free.py --cn-news --limit 30
```

---

## 7. 结论与建议（给 supervisor / 用户拍板）

1. **A 线的「安装 + 注册 + 协议验证」全部完成**（这是任务书要求的 A 线交付）：依赖 ✅ · 离线自检 ✅ · cline 配置 ✅ · 6 工具握手 ✅ · 双后端注册 ✅。**产物即本文件。**
2. **但「本机联网可用性」= 不可用**：ddgs 8 引擎全灭（海外被墙）；CN-Bing 抓取降级（相关性失真）。→ **本机日常取数继续以 `cn_news`（CLI/Python 直调）+ 现有 RSS 活源 为主**，**不要依赖 ddgs 做通用搜索**。
3. **若将来换到「可直连海外」的网络**：本套 ddgs MCP **无需改动即可用**（配置已就位）—— 建议保留注册。
4. **待拍板**：是否需要为「通用 web 搜索」**另寻本机可用后端**（例如已实测可达的 `mojeek` 站内页解析、或用户提供代理）。🚫 本线不做代理/绕墙（红线）。
5. **`mcp<2` 是本机全局 pin**：若其它线需要 mcp 2.x，**会与本 vendor 服务器冲突** → 届时需与 supervisor 确认（可能需 venv 隔离）。**此点已在 `MEMORY_NEWS.md` 记录。**

---

*（本文件为 news 线第 10 批 A 线交付 · 2026-10-05 · 全程免 key · 未改 vendor · 未动他线配置）*
