# MEMORY.md — personal-watch（观察哨）**supervisor** 长期记忆 · **醒来先读本文件**

WAITING: 0

> ⚠️ **本文件在项目根**（`doc/personal-watch/`），是 **supervisor（观察哨长）** 的状态文件。
> **不属于任何 worker 线** —— worker 的记忆在 `run/` 下：`run/MEMORY_NEWS.md`（以后每条线一个）。
> 日流水在根目录 `daily-memories/`（**不要**与 `run/daily-memories-news/` 等 worker 流水混）。
> 纪律：**`WAITING:` 只在顶部出现一次**；**≤32KB**，超限滚动到 `daily-memories/`。

---

## 0. 我是谁 / 我的角色

- 我是 `doc/personal-watch` 的 **supervisor（观察哨长）**：**不亲自采集**，只**派活、巡检、汇总、拍板**。
- **下达通道** = 各任务书的 `## 🔧 运维指令区（OPERATOR NOTES）`（**改文件 + git commit/push**）。
- **查看通道** = 读各线的 `run/MEMORY_*.md` 顶部「进度快照」+ `run/` 产物（`git pull` 即可，**不登录服务器**）。
- 我当前指挥的线：**news**（新闻采集，任务书 `run/WATCH_NEWS_TASK.md`）。
- 上级 = 用户（作者刘杨/Foam）；本哨位的**服务对象是《超级智能2035》的写作与修订**。

---

## 1. 每次「醒来」的固定动作（SOP）

1. **先同步**：`git fetch origin` → `git pull --rebase --autostash origin main`
   （worker 每次唤醒都可能 push；**不 pull 直接改会冲突**）。
2. **读本文件**：尤其 §3 在途任务 / §4 待拍板 / §5 铁律。
3. **读 worker 状态**：`run/MEMORY_NEWS.md` 顶部 + `run/news/` 最新摘要 + `git log --oneline -20`。
4. **处理回写**：worker 有产物/答复 → 读、核、必要时答复（写进对应任务书运维指令区或该线「运维问答」）。
5. **下发新任务**：在对应任务书运维指令区加 **带日期的 block**（**越靠前越优先**；老块不改，留作历史）。
6. **提交**：`git add` **只加自己动的文件** → `commit` → `push`。**不要 `git add -A`**。
7. **回写本文件 + 当日 `daily-memories/<date>.md`**。

---

## 2. 通讯协议 / 接口（关键认知）

- **接口 = 任务书的「运维指令区」**，当前有：
  - `run/WATCH_NEWS_TASK.md`（news 线）
- **下发格式**：`### 🆕 运维指令 · <日期>（摘要）` + 正文；**新块放前面**，写清 **优先级 / 顺序 / 判据 / 铁律**。
- **各线回写位置**：`run/MEMORY_NEWS.md`（状态头 + 进度快照 + 运维问答 + 流水）、`run/daily-memories-news/`、`run/news/`。
- **`WAITING` 机制**：`run/MEMORY_NEWS.md` **顶部**的 `WAITING:` 行驱动 loop 睡眠：
  - `WAITING: 0` = **有近期待办**（要追后续）→ 短睡（默认 30 分钟）续跑；
  - `WAITING: 1` = **无近期待办（常态）** → 睡 30 分钟（`SLEEP_LONG=1800`，**与 BaiZe `SLEEP_WAIT` 一致**）省 token。
- ⚠️ **正则只认行首** `^WAITING:[[:space:]]*1`；**绝不要在正文/快照/流水里再出现以 `WAITING:` 开头的行**。

---

## 3. 在途任务（截至 2026-10-03）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **news** | 🧭 **三层链（用户定调）**：**L1 预测政治信号（新华社→政经举措）→ L2 历史学习"信号→股价"（事件研究）→ L3 算法交易**；**第 9 批 = N4 传导 + N5 草案**（第 8 批 = N3 L1；第 7 批 = N1 语料库 + N2 价格）；T1–T10 全 ✅ | `news/policy/`（`TAXONOMY.md` `SIGNALS.md` `EVENTS.csv` `IMPACT.*` `STRATEGY_DRAFT.md`）· `news/archive/` · `news/analysis/` | ✅ 运行中（54 条真新闻；N1/N3/N4/N5 待做） |
| **research** | **第 3 批：两大目的定案** —— ① **借鉴**（与 BaiZe/ZhuLong 相关，含**半导体/EDA/存储**视角）→ `TOP_K.*`(加 `takeaway`/`action`) + **`TAKEAWAYS.md`≤5 条**；② **科普视频《两分钟论文》**（B站/抖音涨粉）→ `video/SHORTLIST.md` + `video/scripts/*.md`；并行常态增量 | `research/TOP_K.*` · `TAKEAWAYS.md` · `video/SHORTLIST.md` · `video/scripts/<arXiv ID>.md` | ✅ 运行中（61 篇；第 3 批刚派） |

> ✅ **T1–T4 已完成并交付（2026-10-03，commit `c326ba8`）**：
> - **T1** 核实 12 个 web-search 候选；**T2** 新建**免 key MCP** `run/news/mcp_web_search_free.py`（3 工具 `web_search`/`search_news`/`rss_latest`）+ `run/news/cline_mcp_config.json`，**stdio 全链路实测通过**；
> - **T3** 核实 17 个新闻源；**T4** 产出 `run/news/API_COMPARISON.html`（自包含）+ `.md` 底稿。
> - **选定方案**：Web 搜索 = **CN-Bing 主 + 360 备**（免 key）；新闻 = **Hacker News + GDELT + 官方 RSS**。
> - **决定性事实（本机=中国网络）**：Google / DuckDuckGo / Brave / Yahoo / 公共 SearXNG / newsapi.org / BBC / Reuters **全部不可达**；原 **bocha key 额度已耗尽**（`403 not enough money`）→ 故走免 key 自建。
>
> ✅ **首轮 smoke 已完成（commit `3fcd854`）**：`run/news/2026-10-03.md` **16 条**（6 类，均带 标题+来源+日期+链接）。
> supervisor 巡检 = `git pull` 读 `run/MEMORY_NEWS.md` 顶部快照 + `run/news/`。

---

## 4. 待拍板 / 我欠的答复

**已定（无需再议）**
- [x] ✅ **运行主机可连外网**。
- [x] ✅ **全程免 key**（不用付费 API）；搜索能力**以本机自建 MCP 为准**。
- [x] ✅ **非新闻"直接不收"**（用户拍板 → T8 修订版）。
- [x] ✅ **暂不新增智能体** → 原 **archive 线并入 news**（`news/archive/` + `news/analysis/`），脚手架已删。
- [x] ✅ **research 窗口放宽到 ≤30d**（仅限 TOP-K 任务；日报口径不变）。

**在飞（等交付）**
- [ ] ⭐ **news N1**：新华社 2016–2026 十年回溯（标题+日期+链接）+ 分析/饼图 → `news/archive/` `news/analysis/`。
      ⚠️ **前置**：新华网 `/politics/…` **403**、`so.news.cn/getNews` **405+WAF**（**须在运行机复测**）；走不通则用**中新网兜底并标注"非新华社"**（🚫 不许冒充）。
- [ ] ⭐ **news N2**：新闻 ×**资产价格**相关性（**先做 N1**；价格源需先做**免 key + 可达性**实测）。
- [ ] ⭐ **research TOP-K**：`TOP_K.md`/`TOP_K.jsonl`（**质量 × BaiZe/ZhuLong 相关性**，≤30d）＋ **A 节强化**（加 `takeaway`/`action` + `TAKEAWAYS.md`≤5 条）。
- [ ] ⭐ **research 视频线 V1/V2**：《两分钟论文》**选题表** + **3 条两分钟口播稿**（`research/video/`）。
- [ ] ⚠️ **V3 视频生成工具链待确认**：运行机是否有 **TTS / 文生图 / 剪辑**？（我这边有 ComfyUI 系工具，**但不确定运行机可用**）→ **确认后再派**。
- [ ] **news T5**：自建 MCP 装进运行机 cline（**非阻塞** —— CLI 直调已可用）；**T7** GDELT 退避。

**待你拍板 / 未来职能**
- [x] 🎯 **news 北极星已定（用户 2026-10-03）**：**低频「先行指标 → 资产价格」观察与准备**；**A股**；**日/周/月频**（⇒ **算法交易**，非高频量化）；**暂不投真金**；**延迟不要紧**。
      立项四项**已答**：市场=A股 · 频率=日/周/月 · 数据源="随便即可"（东财日K 已实测 ✅）· 资金=暂不投入。
      用户**情景假设**：2028 前后格局变化 → A股转慢牛（⚠️ **仅假设**，本线**只做数据观察、不做政治预测/表态**）。
      🚨 **新增方法学红线**：**必须去趋势**（用收益率/差分，防伪相关）· **低频样本小须给置信区间** · **标注 as-of 防前视** · 见 `WATCH_NEWS_TASK.md` §0.0。
- [x] 🧭 **news 三层链已定（用户 2026-10-03）** = **① 预测政治信号 → ② 历史学习"政治信号→股价" → ③ 算法交易**（任务书 **§0.0.0**）。
      **L1 = N3**（第 8 批）动作分类体系/信号特征/事件库(近3年)/预警(walk-forward+基线) → `news/policy/`；
      **L2 = N4**（第 9 批）**事件研究**（AR/CAR + 板块 + 时滞）→ `IMPACT.*`；**必处理** 预期内/反向因果/同期混杂/多重比较，**N<5 不给结论**；
      **L3 = N5**（第 9 批）交易规则**草案**（计费用+基准，**禁实盘**）→ `STRATEGY_DRAFT.md`。
      🔑 **N1 新华社十年索引 = 语料库**（优先级最高）；**S1 价格（东财日K）** 是 N4 前置。
- [ ] 📧 **research 邮件交流**：**已登记、未批准**。启用前须先定：**发件邮箱/身份/署名 · 模板 · 频率上限 · 是否逐封审核**。🚫 **未批准不得发送**。
- [ ] 🎬 **research V3 视频生成**：**待确认运行机有无 TTS/文生图/剪辑**（我这边有 ComfyUI 系工具链，可补位）。
- [ ] **采集节律**：现为 `WAITING=1` 睡 30min（≈每日 48 轮）。对"新闻"是否偏密？是否改 1~2h？
- [ ] **输出形态**：是否需要**周报合订**（把日报并成一份）。
- [ ] **news 关注清单**是否收敛（现 6 大类）；research 视频栏目**起名**（避免与已有《两分钟论文》混淆）。

---

## 5. 铁律（红线）

- 🚫 **不许编造**：新闻条目必带**链接 + 发布日期 + 来源**；无来源不收录。
- 🚫 **不许把推测写成事实**：区分「原文」与「我们的判断（需显式标注）」。
- 🚫 **不采集需登录/付费墙的正文**：只引用公开标题/摘要 + 链接。
- 🚫 **不整篇转载**：只做摘要 + 链接（版权）。
- 🚫 **不在正文/流水写以 `WAITING:` 开头的行**（会误触发 loop 长睡）。
- 🚫 **不 `git add -A`**（共享工作副本，会卷入别的线在途文件）。
- ⚠️ **控制抓取频率**：避免对同一站点高频请求。

---

## 6. 关键路径与事实速查

- **关键路径**：`启动 news loop → 首轮采集打通（能拿到带链接的条目）→ 稳定每日产出 → supervisor 汇总`。
- **建哨范式**（照抄 `doc/BaiZe-ISEDA2027/`）：
  - supervisor = 项目根 `README.md` + `MEMORY.md` + `AGENTS.md` + `daily-memories/`；
  - worker = `run/<线>_TASK.md`（只读任务书）+ `run/<线>_loop.sh`（含 fetch+pull-rebase / 行首 WAITING 正则 / 只 add 本线文件 三处防坑）+ `run/MEMORY_<线>.md` + `run/daily-memories-<线>/`。
- **loop 三处防坑**（务必沿用，见 `run/watch_news_loop.sh` 头部注释）：
  1. push 前先 `fetch + pull --rebase --autostash`（只 push 不 pull 会永久卡死）；
  2. `WAITING` 正则收紧为**行首**匹配（旧版 `WAITING:[* ]*1` 会误匹配散文）；
  3. 兜底提交**只 add 本线文件**（避免 `git add -A` 卷入他人在途文件）。
- 🧠 **降低思考量（2026-10-03，实测）**：cline CLI 有 **`--thinking none|low|medium|high|xhigh`**（省略 = 用 provider 默认；**`deepseek-flash` 默认 `high`** → 想得久/费 token）。
  - news loop 已加变量 **`THINKING="low"`** 并透传给 `cline ... --thinking "$THINKING"`；要更省改成 `none`。
  - 校验实测：`cline --thinking bogus` → `error: invalid thinking level "bogus" (expected "none", "low", "medium", "high", or "xhigh")`（枚举即这 5 档）。
  - ⚠️ **改 `loop.sh` 需重启 loop 才生效**（bash 已解析的运行中脚本不重读）。
- **搜索能力**：本机（含 Windows 侧 cline 会话）已挂 `web-search` MCP（bocha，中文友好）；通用工具为 `web_search` / `search_news` / `fetch_page` / `wiki_lookup`。
- 🔑 **news worker 运行主机（2026-10-03 实测）**：`liuyang@iZuf65t80q2n4qgbjqbcp0Z`（阿里云），**可出外网**。
  - **网关 = DeepSeek 官方 API**（`https://api.deepseek.com`）。**规范模型 ID 只有两个**（2026-10-03 实测 `GET /models` → 200）：
    **`deepseek-flash`**（显示名 DeepSeek-V4.1-Flash，1M ctx，text+image）/ **`deepseek-v4-pro`**（DeepSeek-V4-Pro，1M ctx）。
  - 🚫 `deepseek-v4-pro-fp4`（BaiZe 那台 `agi-gateway.cxmt.com` 的名字）本机不认；🚫 `deepseek-v4-flash` **不是官方 ID**（会被别名成 `deepseek-flash`，但换机可能直接报错）。
  - 日志：`/tmp/watch_news_loop.log`；本轮 cline 原始输出：`/tmp/watch_news_cline_last.log`。
- **仓库**：`origin = git@github.com:foamliu/super_intelligence_2035.git`，分支 `main`。
- 📰 **中文权威源「活/死」实测（2026-10-03，重要 —— 接源前必测 pubDate）**：
  - 🚫 **死源（返 200 但内容不更新，禁用）**：
    新华网 `www.xinhuanet.com/{tech,politics,world}/news_*.xml`（各 300 条，**停在 2022**）·
    人民网 `www.people.com.cn/rss/*.xml`（**2021/2024**）·
    **央视 `www.cctv.com/program/rss/**/index.xml`（**2006/2007**）** ·
    `xinhuanet english/rss/*`（**2017/2018**）。
  - ✅ **活源（必须接）**：
    **中新网** `www.chinanews.com.cn/rss/{scroll-news,world,finance}.xml`（pubDate = 当天）·
    **联合国新闻·中文** `news.un.org/feed/subscribe/zh/news/all/rss.xml`（2026-10-02）·
    **央视网·新闻/科技网页** `news.cctv.com/`（**RSS 是死的，但网页活**：含当天日期，**须 HTML 抓取**）。
  - 🔑 **铁律**：**"接口 200" ≠ "有新闻"** —— **必须校验 `pubDate` 新鲜度（≤72h）**；**连 LLM 给的源清单也要先测**（DeepSeek 推荐的央视 RSS 实测是 2006 死源）。

---

## 7. 已知坑（会复发）

- 🔴 **cline 报错仍返回 `exit 0`（本线已踩，2026-10-03）**：模型名写错 / 额度耗尽时，cline 打印 `error: ...` 却 `exit 0` → loop 分辨不出失败、按 `WAITING` 白睡。
  - **本线修法**：loop 把 cline 输出 tee 到 `/tmp/watch_news_cline_last.log`，命中致命特征（`supported API model names` / `额度已用完` / `hook dispatch failed` / `unauthoriz`）或 `exit!=0` 时**强制短睡重试**。
  - ⚠️ 别用裸 `error:` 做特征：agent 干活时会把 API 报错当**证据**贴出来，会误判。
- 🔴 **模型名必须与本机网关匹配，且用规范 ID**：本机 = DeepSeek 官方 API，规范 ID 只有 **`deepseek-flash` / `deepseek-v4-pro`**（`GET https://api.deepseek.com/models` 可查）。
  - 抄别的机器的脚本（BaiZe 的 `deepseek-v4-pro-fp4` 属于 `agi-gateway.cxmt.com`）会直接失败。
  - ⚠️ **别名陷阱**：`deepseek-v4-flash` 在官方兼容层会被别名成 `deepseek-flash`（本机实测 200），**但它不是官方 ID**，别写它。
  - ✅ **新线/换机第一步**：`curl -s https://api.deepseek.com/models -H "Authorization: Bearer <key>"` 看规范 ID。
- ⚠️ **`.29` 与 `.12` 的 `/tmp` 不共享**；若 worker 跨机，诊断日志必须**指明机器**。
- ⚠️ **`MEMORY_*.md` 每次唤醒被全文读进上下文** → 越大越烧 token；超 32KB 必须滚动归档。
- ⚠️ **任务书全文 = 每次唤醒的 prompt**（loop 里 `prompt="$(< TASK_MD)"`）→ 任务书要**精简**，历史移入归档文件、不进 prompt。
- ⚠️ 本机 PowerShell 读 UTF-8 中文可能显示乱码——**只影响显示**；校验用 `read_files`。
- ⚠️ 若 worker 机器**外网时通时断**（如 VPN 影响）→ 搜索失败**重试即可**，不是仓库/权限问题。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → worker 回报**。
- ⚠️ **本文件在项目根**；worker 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **2026-10-03** —— **建哨**：新建 `doc/personal-watch/`（观察哨）。落地 supervisor（`README.md` / `MEMORY.md` / `AGENTS.md` / `daily-memories/`）+ 首条 worker 线 **news**（`run/WATCH_NEWS_TASK.md` / `run/watch_news_loop.sh` / `run/MEMORY_NEWS.md` / `run/news/` / `run/daily-memories-news/`），范式照抄 `doc/BaiZe-ISEDA2027/`。
  - **已 push**：commit **`8a0a3ca`** 到 `origin/main`（`run/watch_news_loop.sh` 入库为 `i/lf`）。
  - **用户已确认**：运行主机可连外网且速度不慢 → 具备运行前提，**待拉起 loop** 后即可派活。
- **2026-10-03（纠错）** —— ① **模型名**：loop 曾用 BaiZe 的 `deepseek-v4-pro-fp4`，本机（DeepSeek 官方 API）不认 → 实测 `GET api.deepseek.com/models` 得规范 ID 仅 **`deepseek-flash` / `deepseek-v4-pro`**，已改 **`deepseek-flash`**（`deepseek-v4-flash` 非官方 ID）。
  ② **睡眠**：我曾自创 `SLEEP_LONG=21600`（6h）→ 用户质问后核查 **BaiZe 全部 loop 实为 `SLEEP_BUSY=60` / `SLEEP_WAIT=1800`**，从无小时级睡眠 → 已**完全对齐 BaiZe**（60 / 1800 / PUSH 18000 / TIMEOUT 1500）。
  → 教训：**不自创数值，先照抄已验证模板；引用"XX 那边是多少"必须真去读源码**。
- **2026-10-03（"新闻"定义收口）** —— 用户抽查指出《注意力经济…儿童电视》（Guardian **09-17 特稿**）**不是新闻**。
  复核：**31 条里真·新闻仅约 9~10 条**（余为特稿/观点/博客/论文/论坛帖/Show HN）。
  **根因 = 任务书从未定义"新闻"**（我只写了"抓什么（信号）"）→ 补 **任务书 §0.1「什么是新闻」4 条判据**（时效≤72h / 事件性 / 报道体 / 可核验）+ 类型标签 + 非新闻单列；下发 **T8**。
  → **教训：关键术语（新闻/信号/权威…）必须在任务书里给出可操作定义，否则 agent 会按最宽口径填充。**
- **2026-10-03（用户点名批评 + 我的实测纠偏）** —— 用户："**新华社没有 RSS 吗？真正的新闻你一个都没拉，净做些没用的。**"
  - **复核结论**：**用户对** —— 31 条里**中文权威新闻 = 0**；agent 把"RSS 返回 200"当成了"可用"，**从未真正产出中文条目**。
  - **我的实测补正**：新华网 RSS **确有**，但是**死源**（URL 返 200/300 条，**内容停在 2022**）；人民网停在 2021/2024；**唯一实测"活"的官媒 RSS = 中新网**（pubDate 当天）。
  - **下发 T9**：只认**条目**不认"接口 200"、**校验 pubDate ≤72h**、**活源白名单（中新网）固化进 MCP**、**死源禁用**、新华/人民要走网页列表页或放弃换活源、**中文条目数 ≥ 英文**；并重申**主线是采集真新闻**，报告是副产品。
  - **T8 修订**：按用户拍板 —— 非新闻**直接不收**（取消附录方案）。
  - → **教训：验收标准要钉在"产出物"上（条目/证据），不能停在"接口通不通"；并要教 agent"200≠有料，必须验新鲜度"。**
- **2026-10-03（DeepSeek 建议 → 我的实测复核）** —— 用户转来 DeepSeek 建议：**央视 RSS 为首选**（给了 6 个 `cctv.com/program/rss/...` 地址）+ 联合国新闻中文。
  - **实测**：**央视 RSS = 死源（2006/2007）**，建议**不成立**；**联合国新闻·中文 RSS = 活源（2026-10-02）**，**成立**；
    另测出 **央视网网页是活的**（`news.cctv.com/tech/` 含当天日期）→ 央视要用须**走 HTML 抓取，不是老 RSS**。
  - **更新 T9 活/死源清单**（活：中新网 RSS + 联合国 RSS + 央视网页；死：新华/人民/央视 RSS + xinhuanet english）。
  - → **再证**：**"源"必须自己测过才用，连 LLM 的推荐也一样**。
- **2026-10-03（"UA 被拦"诊断复核 → 证伪）** —— 对方补充"联合国源 `unable to parse` 是 feedparser 的 UA 被拦"。
  - **实测**：4 种 UA（`feedparser/6.0.11` / 浏览器 / `curl/8.0` / 无）**全部 200 `application/rss+xml`** → **联合国不拦 UA**。
  - **真正原因**：**URL 写错** —— `https://news.un.org/zh/rss` → **404 `text/html`**（57KB HTML 页）→ feedparser 收到 HTML 自然 `unable to parse`；
    正确地址是 `https://news.un.org/feed/subscribe/zh/news/all/rss.xml`。
  - **处置（T9 新增第 7 条）**：URL 写死正确值 · **校验 `Content-Type`（rss/xml）+ `pubDate`，拿到 HTML/404 判失败** · 设可识别 UA 作**通用防御**（非本因）。
  - → **教训再升级：连"病因诊断"也要能实测证伪——两轮下来，"想当然"已两次出错（央视 RSS 活着 / UA 被拦）。**
- **2026-10-03（派活 T10）** —— 用户同意把三个**已实测活源**（中新网 RSS / 联合国中文 RSS / 央视网 HTML）**固化成 `fetch_cn_news()`**，
  并**指定由 news agent 自己实现**（熟环境、调试方便）。
  - 规格已下发（第 6 批）：**MCP 工具 `cn_news` + CLI 直调 双形态**；**内建 死源黑名单 / `pubDate≤72h` / `Content-Type` 校验 / UA / 限速降级**；返回 `{title,source,url,published,lang,type}`；**自测必交证据**。
  - ⚠️ 强调：**MCP 未装进 cline 时，CLI 直调是一等公民**。
- **2026-10-03（建第 2 条线：research）** —— 用户要求"**类似 news，建个 research agent：打通 arXiv 下载 API，收集&整理论文（AI，特别是 LLM/SLM/多模态/agent harness）**"。
  - **落地**（范式照抄 news）：`run/WATCH_RESEARCH_TASK.md`（只读任务书，含 §0.1 论文入账判据 + §1 关注领域 + R1–R5）·
    `run/watch_research_loop.sh`（同款加固 loop）· `run/MEMORY_RESEARCH.md` · `run/research/`（+`pdf/`）· `run/daily-memories-research/`。
  - **继承的铁律**：不许编造 · 字段缺一不可 · **`200 ≠ 有料`（验 `Content-Type` + `published`）** · **礼貌限速（arXiv ≥3s）** · 不整篇转载 · 只加本线文件。
  - **R1 先跑**：打通 arXiv API 并**给实测证据**（真查询 + 条目 + 日期）；**R1 未打通不做常态采集**。
  - **待办**：用户需在运行机上 `setsid bash watch_research_loop.sh ...` **拉起 loop**（见 `run/README.md`）。
- **2026-10-03（research 取源实测 + 派活第 1 批）** —— 用户：research 线**已启动**；问"从哪里获取最新 AI 前沿信息"（附 DeepSeek 建议）。
  - **supervisor 实测候选源**：`rss.arxiv.org/rss/cs.{LG,AI,CL}` → **200 rss+xml 但 items=0**（feed 含 `<skipDays>Saturday/Sunday</skipDays>` → **周末不发**）→ **不作主力**；
    **`https://export.arxiv.org/api/query`** → **200 atom+xml，真条目 + `published`** → ✅ **主力**（⚠️ http→**301**，须 https + 跟随重定向）；
    **`https://huggingface.co/api/daily_papers`** → **200 JSON**，但 `publishedAt` **滞后 3~8 天** → ✅ 仅作**社区精选加权**，**不作新鲜源**。
  - **产出/下发**：research 任务书新增「第 1 批：已实测取源清单 + 3 个陷阱」= **R1′**（主力 arXiv API + 副源 HF；RSS 周末空不得写"无新增"）+ **R2′**：
    **`≤72h` 对 arXiv 会误杀**（工作日 20:00 ET 公告、周末不发）→ 改为"日报 ≤72h；周末/周一放宽到**最近一次公告批次**并标注实际区间"。同步修正 §0.1 时效判据。
  - **纠正**：DeepSeek 那套是 **AI+EDA**（cs.AR），本线类别改为 **cs.CL/cs.CV/cs.MM/cs.SE/cs.AI/cs.MA/cs.LG**。
- **2026-10-03（research 首轮交付 + 我的抽验）** —— research agent 交 `4360401`：**首轮 34 篇**（R1–R4）。
  - **R1** arXiv API **已打通**（**HTTPS**/Atom，实测 `HTTP/2 200`，`Content-Type: application/atom+xml`）→ `research/ARXIV_API.md`（含可复现命令）；
    ⚠️ **它自己也发现"http→301、必须 https"** —— 与我的实测一致（独立复现）。
  - **R2** 查询固化 → `research/queries.json`（12 查询 / 5 领域）。
  - **R3/R4** 抓 **214 篇**（≤72h + arXiv ID 去重）→ **精选收录 34 篇**（含中文摘要/作者/分类/abs+pdf）+ **180 篇记入 SEEN 候选**（候选≠不存在，仅未逐条摘要）；
    产物：日报 + `SEEN.md` + `INDEX.md` + **`papers.jsonl`** + `arxiv_fetch.py`（限速≥3s + 校验 + 去重 + 窗口）+ `test_arxiv_fetch.py`。
  - ✅ **我抽验 3 个 arXiv ID**（`id_list=` 反查）：**全部真实**，标题与 `published` 逐字吻合（2026-09-30，落在声明的 ≤72h 窗口内）。
  - **诚实项**：1 次查询 `Read timeout` **如实记录并重试成功**（非静默丢弃）。
  - **待办**：R1′/R2′（HF Daily Papers 副源 + 周末时效放宽）将于**下一轮唤醒**生效。
- **2026-10-03（news 交付 T8–T10 + 我的独立验证）** —— news agent 交 `fd32d67`：
  - **T10** `fetch_cn_news()` 落地（MCP `cn_news` + CLI `--cn-news --limit N [--json] [--max-age-hours]` + Python 直调）；
  - **T9** 中文权威真新闻 **6 条（中文 4 ≥ 英文 2）**：央视网 2 + 中新网 2 + Ars 2；
  - **T8** 原 31 条按 §0.1 收口 → **留 news 9 / 移出非新闻 22**（仅存 SEEN）。
  - ✅ **我亲自复跑其 CLI**（`PYTHONIOENCODING=utf-8 python news/mcp_web_search_free.py --cn-news --limit 5`，exit=0）：
    输出条目**均带当天 `published`**（2026-10-03）· 各源 status/Content-Type 透明 · **超龄丢弃有理由**（90.2h/76.5h>72h）· **死源黑名单确实永不请求**。
  - ⚠️ **两点观察**（已记录，非缺陷）：
    ① `cn_news` 是**通用中文新闻管道**（返回"最新"而非"AI 相关"）→ **调用方仍须按 §1/§0.1 过滤**（agent 写日报时确实过滤了）；
    ② **央视走 `cctv-jsonp`（ct=text/html）**，是对"央视无活 RSS"的合理例外；与"非 rss/xml 判失败"规则不冲突（该规则针对 RSS 源）。
  - **仍待办**：T5（自建 MCP 装进 cline / 等效 CLI 已具备）· T6 · T7。
- **2026-10-03（对外汇报）** —— 按用户要求，参照 `doc/BaiZe-ISEDA2027/report_10_03.html` 生成 **`report_10_03.html`**（本目录根，自包含）：
  8 节 = 两条线状态一览 · 组织方式 · news 全过程（含两次用户纠错闭环）· research 新建 · **8 条关键教训/铁律** · 系统组件 · 需决策项 · 下一步排期。
  校验：标签全平衡（div 27/27 · table 8/8 · tr 41/41 · td 108/108 · code 128/128…）· 无 markdown 残留。
- **2026-10-03（报告刷新 ~17:00）** —— 按用户要求刷新 `report_10_03.html`（39.3 KB，自包含）：
  - 数字更新：提交 22→**29**；news 15→**35** 条（**后三轮中文 19:英文 7，T6 意图达成**）；research **已启动 + 首轮 34 篇**；
  - 新增：**刷新增量框** · §3.5（第 4/5 轮 + 中文逆转）· §4.1（**取源实测表**）· §5 追加 3 条教训（**arXiv RSS 周末空**=第 3 次"200≠有料"；**HF 滞后 3~8 天**；**`≤72h` 换场景会误杀**）· **§9 历史回溯（2016–2026）可行性** · §7/§8 更新；
  - ⚠️ 报告内**如实标注**：两条线自 ~15:15 后**无新提交**（同期 BaiZe 线仍在提交）→ 疑似 loop 停摆/额度，需运行机确认。
  - 校验：标签平衡 · markdown 残留 = 0。
- **2026-10-03（用户问历史回溯）** —— 实测：**现行 feed 不支持** 2016–2026 回溯（RSS=滚动窗口）；
  **HN Algolia ✅**（2016 区间实测 200/nbHits=91）· **GDELT ✅（2017 起，但 1 req/5s，我连试 3 次 429）** · Guardian 需免费 key（401）· Wayback 超时未验。
  → 建议**单开 archive 线**（`type: archive`，不污染 news 口径）；**待用户定主题/窗口**。
- **2026-10-03（用户定 archive 范围 → 建第 3 条线）** —— 用户：**回溯 = 新华社 2016–2026，先估每年条数**；🚫 **不用 Guardian 类 key**；**锁国内权威源**。
  - **supervisor 实测（决定性）**：
    - ✅ **中新网可按天枚举**：`/scroll-news/{YYYY}/{MMDD}/news.shtml` → 200/173–378KB；条目 `/{频道}/{YYYY}/{MM-DD}/{id}.shtml`；
    - ⚠️ **新华网归档未打通**：`/politics/2016-01/01/` → **403**；`so.news.cn/getNews` → **405 + WAF 页**（需**在国内运行机重试**）；
    - ⚠️ 央视网日期路径 → **403**。
  - **抽样（中新网 · 同日 06-15 跨年）**＝ 2016:1237 · 2019:400 · 2022:803 · 2025:327 · 2026:490 → **≈0.3k–1.2k 条/日** → **年量级 ≈12–45 万条**（**抽样，非精确**）。
  - ⚠️ **规模警示**：若新华社 20 万条/年 → 10 年 **≈200 万条**；限速 ≥2s 下**仅枚举就 >45 天** → **全量不可行**，须缩窗/抽样/只取标题+链接。
  - **建 archive 线**（第 3 条）：`WATCH_ARCHIVE_TASK.md`（A1 端点勘察 + A2 抽样计数 + §0.1 口径「archive ≠ news」）· `watch_archive_loop.sh`（同款加固）· `MEMORY_ARCHIVE.md` · `archive/`（`ENDPOINTS.md` / `COUNT_STUDY.md`）· `daily-memories-archive/`。
  - 已同步 `README.md`（3 条线）· `AGENTS.md` · `run/README.md`（§2.2 启动）。
- **2026-10-03（用户拍板 archive 方案 C）** —— 用户选 **C：只取「标题+日期+链接」，不抓正文**。
  - **我纠正了自己的错误估算**：先前 ">45 天" 是**按条**算的（200 万条 × 2s）；**方案 C 按"天"枚举**（一天 1 个列表页）→ 10 年 ≈ **3650 请求 ≈ 2–3 小时**（4 源 ≈ 10 小时级）。→ **C 可行**。
  - **下发 archive 第 2 批**：C 规格 = 5 字段（`date/source/channel/title/url`）· 主键 `url` · **按年分片压缩** `index/<源>-<年>.jsonl.gz` · `PROGRESS.md` 断点续抓 · `INDEX_FILES.md` 清单 · **单年 >20MB 不入 git**（本体放 `~/archive_data/`）· 限速 ≥2s · **A1 未通前 C 仅对中新网先行**。
- **2026-10-03（用户 5 条指令 → 组织调整）** ——
  1. **research**：按**质量 + 与 BaiZe/ZhuLong 相关性**排序出 **TOP-K**，窗口放宽 **≤30d** → 下发 **R-T1~T3**（双维度 0–5 打分 / HN 热度替代 HF / `TOP_K.md`+`.jsonl` / 必须附方法与局限）。
  2. **archive 并入 news**（**不新增智能体**）→ **删除 archive 线脚手架**（`WATCH_ARCHIVE_TASK.md`/loop/MEMORY/产物目录），职能改为 **news 第 7 批 N1**（新华社十年回溯 标题+日期+链接 + **分析/饼图**）。
  3. **news N2**：新闻 ×**资产价格**相关性分析（先做 N1；价格源先做免 key 可达性实测；须写"相关≠因果"）。
  4. **暂不新增智能体**（写入 README §2/§3、AGENTS §1、任务书）。
  5. **research 未来职能**：给作者**发邮件**做学术交流 → **只登记、不实施**；启用前置（邮箱/署名/模板/频次/逐封审核）已写进任务书，🚫 **未批准不得发送**。
  - 同步：`README.md`（**回退为 2 条线** + 三类产出口径）· `AGENTS.md`（删 archive 行 + 不新增声明）· `run/README.md`（删 §2.2）· 创建 `news/archive/` `news/analysis/`。
- **2026-10-03（报告再刷新 ~19:50）** —— `report_10_03.html` → **44,966 B / 477 行**：数字 29→**39** 提交、news 35→**54**、research 34→**61**；
  新增 **§3.6（N1/N2 + archive 并入）**、**§4.2（TOP-K 规格）**、**§5 追加 3 条教训**（HF 不可达不伪造 / R2′ 周末生效 / **我的">45 天"估算按"条"算错，作废**）；
  **§9 重写为"已定案"**（方案 C + 国内源实测表 + 已排除 GDELT/HN/Guardian/Wayback + 落地形态）；§7/§8 更新为 N1/N2/TOP-K。
  - 校验：标签平衡 · **`**` = 0 · 反引号 = 0**。
- **2026-10-03（用户明确 research 两大目的 → 派第 3 批）** ——
  - **目的 1 · 借鉴**：找与 **BaiZe/ZhuLong** 相关的前沿研究**以资借鉴**（**刘杨 = 长鑫存储 AI 研究院**）→ TOP-K 加 `takeaway`/`action` + **`TAKEAWAYS.md`（≤5 条）**；**相关面含半导体/EDA/存储**。
  - **目的 2 · 科普**：做 **《两分钟论文》** 视频**发 B站/抖音涨粉变现** → 新 `research/video/` 线：**V1 选题表 → V2 三条两分钟口播稿（350–450 字，固定结构，🚫 不盗用原图）→ V3 视频（待确认工具链）**。
  - ⚠️ **两目的口径不同，选题必须分开**（已写进任务书与 README）。
  - **待确认**：运行机是否有 **TTS/文生图/剪辑** 工具链（**V3 前置**）。
- **2026-10-03（用户明确 news 长期目的：量化交易 agent）** ——
  - news 线**北极星 = 构建量化交易 agent（副业）**；新闻/回溯/相关性 = **数据与信号基建**。
  - 任务书新增 **§0.0**：**路线图 S0–S5**（数据地基 → 行情 → 因子 → 回测 → 纸上交易 → 小资金实盘）· **6 条红线**（不许编造价格/回测 · 查前视/幸存者/数据窥探 · 回测≠实盘 · 相关≠因果 · **未授权禁接交易接口** · 合规如实提示）· **立项四项待拍板**。
  - **supervisor 实测免 key 行情源**：**腾讯 `qt.gtimg.cn` ✅ / 新浪 `hq.sinajs.cn` ✅（需 Referer）/ 东财 `push2his…kline` ✅（历史日线）**；Yahoo ⚠️（运行机可能墙）；**stooq ❌（返回 HTML 非 CSV）**。→ 已写入 N2 数据源表。
- **2026-10-03（用户细化北极星 → 改定位为"低频观察"）** —— 用户答：**A股** · **日频甚至更慢（周/月）** · **数据"随便即可"（延迟不要紧）** · **暂不投真金** · 重点是**把握"资产价格 ↔ 先行指标（新闻 + 长期时政经济趋势）"的相关关系**（提前准备）；并给出**情景假设**：2028 前后格局变化 → A股转慢牛。
  - **据此重写 §0.0**：定位改为 **低频「先行指标 → 资产价格」观察与准备**；路线图 S1→**低频价格**、S2→**先行指标体系**、S3→**lead-lag 相关性**、S4→**观察仪表盘（周/月报）**、S5→**低频规则化算法交易**。
  - **新增方法学红线 4 条**：**必须去趋势**（防伪相关）· **低频样本小须给置信区间**（周≈520/月≈120）· **标注 `as-of` 防前视** · **周/月聚合口径固定并写明**。
  - **新增第 11 条红线**：⚖️ **政治话题中立**（涉台海/格局只做描述性统计，**不预测、不表态**）。
  - **N2 规格重写**：价格侧 A股指数（东财日K）· 先行指标=新闻类 + **长期时政经济类（PMI/社融/CPI/汇率/利率/成交量/北向…，须先实测免 key 可达+有历史）** · 分析=去趋势 + lead-lag（0–4 周）+ 显著性 + as-of。
  - 立项四项**全部已回答**（市场 A股 / 频率 日周月 / 数据源 随便 / 资金 暂不投）。
- **2026-10-03（news worker 首交付）** —— agent 完成 **T1–T4**（`c326ba8`）+ **首轮 smoke 16 条**（`3fcd854`）+ 记忆回写（`bdc20db`），已转**常态采集**（`WAITING=1`）。
  亮点：**真跑实测**（给报错原文）、**建了免 key MCP**、报告**自包含**、**360 无日期就拒收**（守"字段缺一不可"）。
  待用户拍板：**是否补正规 API key**（免 key 抓取脆弱/合规灰区）。待核：**MCP 是否已装进运行机 cline**。
