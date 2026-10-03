# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 0

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        prep_api（前期任务 T1–T4 ✅ 已完成）
已完成:       T1 Web搜索API调研 · T2 MCP配置+stdio实测 · T3 新闻API调研 · T4 对比报告（.md+.html）
当前动作:     T1–T4 交付完成；转常态采集，下一步做 1 轮 smoke
下一步:       常态采集 smoke：用 MCP `web-search-free` 每类取 1~2 条 → 落盘 news/2026-10-03.md + SEEN + INDEX
本轮新增:     0 条
阻塞:         无
ERROR_COUNT:  1（首轮：模型名 deepseek-v4-pro-fp4 不被网关支持 → cline 报错退出、白睡一轮；已修）
```

**选定方案（prep_api 结论）**

- **Web 搜索**：**抓取 CN-Bing（`cn.bing.com`）主 + 360（`so.com`）备**（免 key、中文友好；本机唯一真跑通的通用搜索）。已封成 MCP `web-search-free`。
- **新闻取数**：**Hacker News API + GDELT Doc API + 官方 RSS**（新华/人民/中新/arXiv/Ars 等，免 key）。
- **付费/需 key 备选**（本机可连但需注册/信用卡，仅作升级路径）：Tavily、Exa、SerpAPI、Guardian、GNews、Currents、Mediastack、TheNewsAPI。
- **本机不可达（被墙）**：Google、DuckDuckGo、Brave、Yahoo、公共 SearXNG（8 实例全灭）、newsapi.org、BBC、Reuters、Google News RSS。
- **原 bocha key 额度已用尽**（`HTTP 403 not enough money or package quota`）→ 故改用免 key 自建后端。

**交付物**：`news/mcp_web_search_free.py`（MCP server，3 工具）· `news/cline_mcp_config.json`（MCP 配置片段）· `news/API_COMPARISON.md` + `news/API_COMPARISON.html`（自包含对比报告）。

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- （暂无）

---

## 1. 状态头

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`<尚未开始>`
- **累计收录**：`0` 条

---

## 2. 流水（倒序，保留最近 ~20 条）

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
