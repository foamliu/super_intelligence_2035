# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（第二轮已完成）
已完成:       T1–T4 前期任务 ✅ · 首轮 smoke ✅（16 条）· 第二轮常态采集 ✅（15 条）
当前动作:     第二轮常态采集落盘（追加 news/2026-10-03.md 15 条）+ 更新 SEEN/INDEX + 本轮直连可达性抽检
下一步:       常态采集（WAITING=1，睡 30min）：逐类搜索→去重→追加当日摘要；GDELT 需限频（本轮 429，省额度未重试）
本轮新增:     15 条（来源数：HN · TechCrunch · Anthropic · Ars Technica · Guardian · NYT · NBC · arXiv · MIT Tech Review · GitHub · Medium）
阻塞:         无
ERROR_COUNT:  1（历史：模型名 deepseek-v4-pro-fp4 不被网关支持 → 白睡一轮；已修。本轮 GDELT 429 属频控，已如实记录、未重试）
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
- **上次采集窗口**：`2026-10-03` 首轮 smoke ~ `2026-10-03` 第二轮常态
- **累计收录**：`31` 条（首轮 16 + 第二轮 15）

---

## 2. 流水（倒序，保留最近 ~20 条）

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
