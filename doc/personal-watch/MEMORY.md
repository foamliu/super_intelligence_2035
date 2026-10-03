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
  - `WAITING: 1` = **无近期待办（常态）** → 长睡（默认 6 小时）省 token。
- ⚠️ **正则只认行首** `^WAITING:[[:space:]]*1`；**绝不要在正文/快照/流水里再出现以 `WAITING:` 开头的行**。

---

## 3. 在途任务（截至 2026-10-03 建哨）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **news** | **前期任务 T1–T4**（2026-10-03 下发）：① 找免费 web search API ② 配 web search MCP（+实测） ③ 找免费·权威新闻 API ④ 自包含对比报告 | `run/news/API_COMPARISON.html`（自包含）+ `run/news/API_COMPARISON.md`（底稿）；选定方案写回 `run/MEMORY_NEWS.md`（`PHASE=prep_api`） | 🆕 已下发，待 worker 执行 |

> 说明：news 线为**新线**。**前期任务 T1–T4 完成前暂缓常态采集**；完成后回到 §1 关注清单做日常采集，产出落 `run/news/`。supervisor 只需 `git pull` 读 `run/MEMORY_NEWS.md` 顶部快照 + `run/news/` 即可巡检。
> **前期任务口径（2026-10-03 用户）**：重点是**免费**（web search API / 新闻 API）+ **可实测** + **对比成表**；强调"权威"新闻源。

---

## 4. 待拍板 / 我欠的答复

- [x] ✅ **worker 运行主机已确认（2026-10-03 用户）**：**可连外网且速度不慢** → news 线具备运行前提。待 loop 拉起后即可派活。
- [ ] **搜索/新闻 API 选型**：待 news 线交付 `API_COMPARISON.html` 后，由 supervisor/用户拍板**最终方案**（免费额度、中文覆盖、权威性、稳定性）。
- [ ] **MCP 配置归属**：T2 配置的是否为**运行机**上的 cline MCP 配置（路径/生效方式需在报告里写清）。
- [ ] **采集节律**：默认长睡 6 小时（每日 4 轮）是否合适？还是每日 1 轮晨报？
- [ ] **输出形态**：日报够不够，是否要**周报合订** / **主题归档**（按关注清单分类长期累积）。
- [ ] **关注清单**是否要收敛（现在 6 大类，见 `WATCH_NEWS_TASK.md` §1），避免噪声。
- [ ] 是否增设 **paper 线**（arXiv 等）。

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
- **搜索能力**：本机（含 Windows 侧 cline 会话）已挂 `web-search` MCP（bocha，中文友好）；通用工具为 `web_search` / `search_news` / `fetch_page` / `wiki_lookup`。
- 🔑 **news worker 运行主机（2026-10-03 实测）**：`liuyang@iZuf65t80q2n4qgbjqbcp0Z`（阿里云），**可出外网**。
  - **网关支持的模型名只有 `deepseek-flash` / `deepseek-v4-pro`**（🚫 不是 `deepseek-v4-pro-fp4`）。
  - 日志：`/tmp/watch_news_loop.log`；本轮 cline 原始输出：`/tmp/watch_news_cline_last.log`。
- **仓库**：`origin = git@github.com:foamliu/super_intelligence_2035.git`，分支 `main`。

---

## 7. 已知坑（会复发）

- 🔴 **cline 报错仍返回 `exit 0`（本线已踩，2026-10-03）**：模型名写错 / 额度耗尽时，cline 打印 `error: ...` 却 `exit 0` → loop 分辨不出失败、按 `WAITING` 白睡。
  - **本线修法**：loop 把 cline 输出 tee 到 `/tmp/watch_news_cline_last.log`，命中致命特征（`supported API model names` / `额度已用完` / `hook dispatch failed` / `unauthoriz`）或 `exit!=0` 时**强制短睡重试**。
  - ⚠️ 别用裸 `error:` 做特征：agent 干活时会把 API 报错当**证据**贴出来，会误判。
- 🔴 **模型名必须与本机网关匹配**：本机只支持 **`deepseek-flash` / `deepseek-v4-pro`**。抄别的机器的脚本（如 BaiZe 用的 `deepseek-v4-pro-fp4`）会直接失败 → **新线/换机时先核对模型名**。
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
