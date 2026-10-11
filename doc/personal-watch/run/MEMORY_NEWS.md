# MEMORY_NEWS.md — 观察哨 · **新闻 agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_news_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起：`WAITING` 不再决定唤醒节律**）：loop 定时模式 `SCHEDULE_HOURS=6,18` **每天 2 次（06:00 / 18:00）**唤醒，时窗内零 token 分段睡；字段仅为人读状态。旧自适应（`0`→短睡 60s 续跑 / `1`→睡 30min 省 token）**已降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
PHASE:        常态采集（T1–T10 ✅）+ **L1/N3 收口（G1 全过）+ L2/N4 探索性（G2 全过）** + **任务书自滚归档（已把第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`；每次唤醒按 ≤32KB 自检）**（L1 焦点 · L2 探索性 · L3 冻结）
已完成:       T1–T10 ✅ · 首~六十轮常态 ✅ · **N1 抓取器 + 语料〔全库完抓〕2,492,230 条 / 11 片 2016–2026（游标 `2015-12-31`，倒序收尾至 `2016-01-01`）· N3-1 EDA · TAXONOMY · N3-2 信号 · N3-3 事件库 75,610 条 · N3-4 预警方案 · L1 预警准则加固（`early_warning.py` §4.3 固定召回率 precision + §4.4 措辞强度 tone 信号，`EARLY_WARNING.md` 424 行）· L2 预注册 · 价格源复测 · N4 探索性关联（EXPLORE.md + explore.csv）· G2′④ 运行台账（cycle_run.py + STABILITY_LOG.md）+ 连续性自报（`compute_streak`：连续 7 自然日 · ≥20h · 同天计 1 · record-only 不计入）· **任务书自滚归档（第2–10批 + §0.0.0/§0.0.1 背景块 → `WATCH_NEWS_TASK_ARCHIVE.md`）** · **第六十~七十八轮常态采集 ✓（news +27 · **明细见 `daily-memories-news/` 当日心跳**）** · **第七十九~八十一轮常态采集（news +13 · **明细见 `daily-memories-news/` 当日心跳**）** · **第 11 批 P0 · R3/R4/R5/R6（38 标的十年价格每次全量刷新 · `lag_corr.csv` **R1–R6 六次运行逐字节一致**〔`83d3bf34…`·**第 6 次可复现**〕· `AM_PM_CHECK.md` R5 复跑**未产生新表**〔🛡 0 格护栏生效〕· `INDEX_FILES.md` R5 重登记 + R3 勘误 · 日报 `2026-10-08` AM+PM / `2026-10-09` **AM+PM** / `2026-10-10` **PM**）** · **第八十二轮常态采集（news +8：TRAE 合并 Code/Work · 联想 TianxiCode 登顶 SWE-bench-Live · 字节 Seed「相位敏感性」· 星动纪元 VPP2 登顶 RoboDojo · openJiuwen 开源企业级 AgentOS · 豆包工作画布 · Claude Dashboards/Motion · 《柳叶刀》AMIE 真实急诊；**明细见 §2 流水**）** · **第八十三轮常态采集（news +10 · 中 10 / 英 0 · 18:00 晚报轮）** · **第 11 批 P0 · R7（38 标的十年价格每轮全量刷新 · `lag_corr.csv` **R1–R7 七次运行逐字节一致**〔`83d3bf349be52251…`·**第 7 次可复现**〕· **`REPORT.html` §⑤ 10 条汇率行显示层修复**〔`29a03cd0…` → `ff695f4f0cf79060…`〕· `LATEST_SIGNALS.md` R7 · `INDEX_FILES.md` R7 重登记 · 日报 `2026-10-11` **AM 版**）** · **第八十四轮常态采集（news +6：Anthropic 非预期模型行为披露〔含虚假凶案线索·**补收**〕· 《食品安全法》修订草案涉 AI 监管 · 尼康撤销清华徐宁冠军资格 · 腾讯元器停服 · 英伟达洽谈收购 Reflection AI · 凯奇拒绝 AI 授权条款；**明细见 §2 流水**）** · **第八十五轮常态采集（news +7：消息称字节/腾讯加速个人 AI 智能体〔对标 Meta Muse〕· 微软纳德拉「默认假设 AI 模型失控 + 强制中断」· Anthropic 禁「辱骂 Claude」政策 · 报告称 Claude 半年封杀 1140 万账号 · 欧盟称其 AI 规则可阻止失控 AI · 国安部 AI 声纹克隆防诈提示 · 蚂蚁「灵光」内测；**明细见 §2 流水**）** · **第 13 批 18:00 轮（P0 交付：微头条 1 篇〔18:05 已发布/首发〕+ 引流评论 4 条〔全成功/前排〕+ 第八十六轮 news +7 · 当日 20 / 累计 224）** · **G2′④ 连续性：连续 7 天 / 7 天 ✅ 达标**（`2026-10-11 15:16` 真实重跑 · 距上次 21.0h；⚠️ **18:00 轮同天不重跑**）
当前动作:     **本唤醒（2026-10-11 18:00 · 第 13 批 18:00 时窗）**：**① 发文 1 篇** = 微头条 **18:05**「国家安全部：接陌生电话先『沉默三秒』× AI 声纹克隆」（**4 段 / 200 字（实测） · 纯文字**）⇒ 后台 **已发布 / 首发** · 作品页 `toutiao.com/w/1878747404777480/`（距 15:01 首篇 **≈3h04min ≥ 90min ✅** · 本日 **2 篇 / 上限 6**）。**② 声明口径（§9）** = 作品声明**单选**且「**引用 AI**」与「个人观点，仅供参考」**互斥** ⇒ 取 **「引用 AI」** + 头条首发。**③ ⚠️ 配图（§8）** = 发布页「图片」面板**仅上传 · 未见免费图库入口** ⇒ **纯文字发** · 台账 `无图` ⚠️ 待修（已写入 `SPEC §8.1`）。**④ 引流评论 4 条（全成功 · 全前排）** = 玄奘《大唐西域记》（康宁汉姆照书找鹿野苑/菩提伽耶）· WorkBuddy×Office（「AI 进办公第一步是先能『看见』文件夹」）· 新疆佛塔《三国志》（吐鲁番干燥保住纸本）· 200 个 AI 虚拟文明（「秩序是涌现的」）；**频道页 + 热榜实测争议/民族/标题党偏重 ⇒ 弃用 · 4 条全部取自「推荐」流**（§5 口径）。**⑤ 回评 = 0（如实）**：`评论管理` 仍为「豆包」机器人 + 旧帖 ⇒ 无「真实提问 / 理性讨论」可回。**⑥ 评论框机制（实测 · 已归档 `SPEC §5.1`）** = `.comment-textarea` 必须**派发** `beforeinput`/`input`/`keyup`/`change` 才激活 `button.submit-btn`（**仅 `Input.insertText` 不生效**）。**⑦ 第八十六轮常态采集（news +7 · 中 7 / 英 0）** = 15:06→18:20 ≈ **3.2h** ⇒ `news/2026-10-11.md` + `INDEX.md`/`SEEN.md`（+11 行）· **累计 224**；**量子位 feed 恢复**（4 条落上轮窗 ⇒ **补收 3**）。**⑧ 基线（实测）** = 粉丝 **70**（昨日无变化）/ 累计收益 **6.38 元** / 微头条 **420 条**（+1）· 主页「**Xmodel唠两句**」**1.7 万获赞 / 70 粉丝 / 134 关注**。**⑨ G2′④（如实）** = 同天只计 1 天（15:16 已跑）⇒ **18:00 轮不重跑**（连续 **7/7 天 ✅**）。**⑩ CDP 卫生** = 自建 **3 tab** 按 id 关闭 + `hr_tabs.py prune toutiao.com`（留 1）· 未触 `zhipin.com` · 凭据未落盘。｜ ⤴️ **上一唤醒（15:06 维护轮 · 摘要）**：**0 篇（合规）**（距 15:01 首篇 ~5min < 90min）· 选题储备 `drafts/2026-10-11-ai-voice-clone-sms.md`（275 字 · 已于本 18:05 用掉）· 发布复验 `toutiao.com/w/1878735833613380/`（含「作品声明：个人观点、仅供参考」）· 第八十五轮 news +7 · G2′④ `2026-10-11 15:16` 真实重跑（连续 **7/7 天 ✅ 达标**）—— **详情见 §2 流水 + `daily-memories-news/2026-10-11.md` `[15:06]`**。
第11批(R7):    ✅ **P0 交付（R1–R7 全部到位）**：`news/signal/`（prices/〔**38 标的 · 6 类 · 2016–2026 · 2,562,208 B · ok=38/fail=0 · 末日 38/38 = 2026-10-09**〕· `INDEX_FILES.md`〔R7 重登记 · 目录指纹 `acc18b5fb54f8ce4`〕· `lag_corr.csv` + `LAG_CORR.md`〔**23,940 格 · FDR `q<0.10`=0 / `stable`=0 · 如实负面**；**R1–R7 字节一致 `83d3bf349be52251…`**〕· `FINDINGS.md`（最后核验日 **2026-10-11**）· `LATEST_SIGNALS.md`（as-of **2026-09-30** · 语料冻结）· `REPORT.html`〔`ff695f4f0cf79060…`〕· 日报 `daily/2026-10-08.md` ~ **`2026-10-11.md`（R7 · AM 版；PM 待补）**）。⚠️ **非因果 · 非投资建议**；**明细见 `news/signal/`。**
下一步:       **⓪ 【第 13 批 P0 · 当前最高】今日头条涨粉**：**每天 6 轮（07:00/09:30/12:00/15:00/18:00/21:30）** → 每轮 ① 从当日 `news/<date>.md` 挑 1 条最有话题度 → 写微头条草稿；② **频控 ≤6 篇/天 · 间隔 ≥90min**（⇒ **每轮最多 1 篇**），未满足 ⇒ 只做「选题储备 + 回评论」、不发新帖；③ 发布前用 `~/news_cdp.js` **复测选择器**（不确定 ⇒ 只存草稿、不发布）；④ 回评论只回「真实提问/理性讨论」（≤3/轮 · 30–90s 随机间隔）；⑤ 记账 `news/toutiao/台账.md` + 心跳 + `daily-memories-news/`。⚠️ **本日已发 2 篇（15:01 / 18:05）**；下一节律轮 = **21:30**（距 18:05 ≥ 90min ⇒ 最早 19:35 可发）；草稿 `drafts/2026-10-11-ai-voice-clone-sms.md` **已于 18:05 用掉** ⇒ **21:30 需从 `news/2026-10-11.md` 新挑 1 条**。① **G2′④**：**连续 7/7 天 ✅ 已达标**（2026-10-11 15:16 已跑）⇒ **18:00 轮无需再跑**（⚠️ 同天多次只计 1 天），自 10-12 起维持「每日 ≥1 次真实重跑、相邻 ≥20h」；② ⚠️ **第 11 批已归档**（`WATCH_NEWS_TASK.md` L55「📦 [已归档] · ✅ R1–R7 已全部交付」）⇒ **不再要求**「18:00 晚报轮补 `signal/daily/2026-10-11.md` PM 版 / 价格增量 R8」（**旧指令作废 · 如实记录**）；**下一轮（2026-10-11 21:30）**：① **第 13 批（最高优先）**：从 `news/2026-10-11.md` 新挑 1 条写第 **3** 篇微头条（距 18:05 ≥ 90min ⇒ **最早 19:35**）· 引流评论 ≤10 条 · 回评只回「真实提问 / 理性讨论」；② **常态采集续跑**（窗口内新 AI 事件照收、无则如实留空；**深扫 feed 头部以下若干位，防再漏收**）；③ **第 10 批 B 线**：**仍待用户拍板 P1–P6/P7**（`news/dongfang/report.html` §8）→ **拍板前不实施日更**；⑥ L1 稳定性 / 下一个候选文本信号 = **新词首发 / 版面**（§4.4 措辞组合**未胜出**，如实保留）；⑦ L3（N5）**冻结**；⑧ **任务书/MEMORY 自滚归档**（>32KB 目标 / >40KB 红线前先搬 `WATCH_NEWS_TASK_ARCHIVE.md` / `daily-memories-news/`）
本轮新增:     **第八十六轮常态 news +7（中文 7 / 英文 0；当日 20 / 累计 224）**——**华为 × 华东师大「昇腾原生时序预训练模型」登顶 `TIME-leaderboard` / `GIFT-Eval`**〔IT之家 `011/631`·**厂商自述口径 · 不作第三方定论**；第 1 类〕· **Qwen-Image-2.1 Pro / Turbo API 上线千问 AI 平台**〔IT之家 `011/622`；第 1 类〕· **努比亚 NaviX Ultra（「第二代豆包手机」）开放「内测实验室」**〔IT之家 `011/617`；第 4 类〕· **马斯克：给信用卡拍照即可用 Grok Bot 搜优惠下单（争议性表态 · 双方公开回应 · 未实测）**〔IT之家 `011/616`；第 5 类〕· **量子位《硅谷 AI 现状》**〔`502585`·13:22 CST·**补收**〕· **量子位《GPT-4o 的拯救行动》**〔`502550`·13:18 CST·**补收**〕· **量子位《DeepSeek Bot 民间版》**〔`502544`·11:27 CST·**补收 · 非官方**〕。`cn_news` 30 条 **AI 具体事件 0 条** → 不收。`SEEN.md` **+11 行**（**7 news / 7 条事件** + **4 防重/留档**〔含量子位 `502584` 留档不重收〕；明细见 `SEEN.md` 与 `news/2026-10-11.md` §方法观察）。┃ **P0（第 13 批 · 18:00 时窗）**：微头条 **1 篇**（18:05 已发布 / 首发 · 国安部「沉默三秒」× AI 声纹克隆 · **纯文字** ⚠️）· 引流评论 **4 条**（全成功 / 全前排）· 回评 **0**（如实）· 台账 + 基线（粉丝 70 / 收益 6.38 元 / 微头条 420 条）。┃ **G2′④**：同天只计 1 天（`2026-10-11 15:16` 已跑）⇒ **18:00 不重跑**（连续 **7/7 天 ✅ 达标**）。┃ 上一唤醒：第八十五轮（news +7 · 15:06 时窗）明细见 `daily-memories-news/2026-10-11.md`
阻塞:         无（新华网长期 403/405 → 兜底源 `chinanews`；⚠️ **无 bypy → 网盘不可用** → ≥5MB 一律「本地保留 + 清单登记 + 如实标『未上云』」；⚠️ **东财日K 运行机 TLS 被重置** → 历史日线走腾讯 `ifzq`；⚠️ **停后台抓取须杀 python 子进程**；⚠️ **等抓取勿用 `pgrep -f <脚本名>`** → 用 `kill -0 <pid>`；⚠️ **ops relay 的 `git pull --rebase` 会删掉被 untrack 的工作区分片** → 须从 `~/archive_data_backup/` 恢复）｜🆕 **第 10 批**：⚠️ **`mcp<2` 已成运行机全局 pin**（2.3.0 → **1.30.0**，否则 `mcp_ddgs`/离线自检不可用）→ 与需 **mcp 2.x** 的其它线**可能冲突**，**待 supervisor 确认**；⚠️ **ddgs 8/8 引擎被墙**（duckduckgo/yahoo 超时；cn.bing/mojeek 可达但结果端点被拦）→ 免费通用 web 搜索**本机不可用**，日常仍以 `cn_news` + 官方 RSS 为准；⚠️ **CN-Bing 抓取相关性降级**（查「人工智能 最新 政策」返回「人工」词条 → 200 ≠ 有料） ｜📦 **体积（实测字节 · 本唤醒 2026-10-11 15:1x 实测 · 提交后复测）**：**TASK=38171B(37.3KB) / MEMORY=32616B(31.9KB) / ARCHIVE=60015B(58.6KB)**；soft 32KB / 红线 40KB ⇒ ✅ **均在红线下**（本唤醒新增长文触发 soft 上限 ⇒ 依「最小滚动」把 §2 R6 长条目 + 第 60~78 / 79~81 轮明细**指针化**〔全文在 `daily-memories-news/`〕）。历史压缩：§2 的 **R3 / R2 两条 P0 长条目** → 🔀 指针〔原文在 `daily-memories-news/2026-10-08.md`〕；§「已完成」的**第六十~七十八轮明细** → 一行〔明细见 `daily-memories-news/` 当日心跳〕）
ERROR_COUNT:  4（历史：模型名白睡一轮，已修；并发双抓重复，已修；watcher `pgrep -f` 自匹配死锁，已修；**relay rebase 删工作区分片 → 已恢复**）
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
python3 -c "import sys; sys.path.insert(0,'news'); import mcp_web_search_free as m; print(m.rss_latest('https://www.ifanr.com/feed',15))"       # 爱范儿（T6 新增；AI/数码）
# 备用活源（本轮实测 200 + 带 pubDate，未启用）：雷峰网 https://www.leiphone.com/feed · 钛媒体 https://www.tmtpost.com/rss
# ⚠️ 死源：新浪科技 http://rss.sina.com.cn/tech/rollnews.xml（接口 200 但内容停在 2018-09-23）；中新网 https://www.chinanews.com.cn/rss/it.xml（空 feed）
```

**返回样例（每条）**：
```json
{"title":"OpenAI披露澳大利亚又一政府机构遭入侵","source":"央视网","url":"https://news.cctv.com/2026/10/03/ARTI3jDXniV5jQDx59hwBf6y261003.shtml","published":"2026-10-03T01:14:00+00:00","lang":"zh","type":"news","snippet":"…"}
```
**实测（2026-10-03）**：6 活源全 `200` → 命中 30 条；丢弃 83 条（超龄 >72h）。**详见 `news/FETCH_CN_NEWS.md`**。

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（本线主动小结 · 2026-10-05 第6轮）：N1 全部抓完了吗？全链对齐了吗？体积红线（≥5MB 不入 git）落实了吗？**
  **A（本线 2026-10-05 实测）**：
  - **① N1 全库完抓 ✅**：第 7 轮（14:56→15:10）把游标 `2016-08-05 → 2016-01-01` 走完 → 语料 **2,267,862 → 2,492,230 条**（11 片 2016–2026；游标 `2015-12-31` = 已到终点，**倒序抓取收尾**）。`--stats` / `.progress.json` 一致（`done_days=3929`）。
  - **② 全链对齐 ✅**：`/tmp/n1_chain_r7.log` 尾 `[chain r7 done] 2026-10-05 15:10:58`；`STABILITY_LOG.md` **第 8 行** `2026-10-05 15:10 | 3914 | 2492429 | 75610 | 43 | 24 | ``9909e4cddcf525a8`` | ``90f357ff8a8be943`` | ok`（`EVENTS.csv` **75,610 条 / 18.11 MB**；`explore.csv` sha 不变属预期）。
  - **③ 体积红线落实 ✅（用户 §4-11 明令 ≥5MB 不入 git）**：ops RUN_ID 5（`d5d7dab`）已把 11 个分片 `git rm --cached`；本线补做 **`news/policy/.gitignore` + `git rm --cached EVENTS.csv`**（**18.11 MB ≥5MB**）；`fetch_archive.py --index` / `extract_events.py` 的体积口径**由「>20MB」改为「≥5MB」并新增「存放位置」列**；两处 `INDEX_FILES.md` 重生成。⚠️ 实测：`git check-ignore` **对已跟踪文件不命中** → 要命中**必须先 `git rm --cached`**（否则红线自检永远失败）。
  - **④ 🐞 善后（relay rebase 误删工作区分片）**：ops relay 的 `git pull --rebase` 把**被 untrack 的 11 个分片从工作区删掉**（`outbox` 末「工作区分片仍应为 11 → `0`」），而 RUN_ID 5 **本意是「保留工作区文件」** → 本线已 `cp ~/archive_data_backup/*.jsonl.gz news/archive/` **恢复**（11 片 / 105 MB，sha 与 `PROGRESS.md` 逐条一致）；`.gitignore` 生效（`git status` 无 `??`，提交绝不带 `.gz`）。
  - **⑤ 无 bypy** → 百度云盘**不可用** → 按红线「**宁可不传**」，≥5MB 一律 **本地保留 + 清单登记 + 如实标『未上云』**（两处 `INDEX_FILES.md` 均标 `本地/未上云(≥5MB)`；第二副本 `~/archive_data_backup/`）。
  - **⑥ 常态采集**：第十六轮 **+0**（国庆假期中文权威源 AI 类真新闻稀缺；`cn_news` 30 条均假期/民生/时政；量子位 `501700`、中新网 `10708128` 已在账 → 去重）→ 当日累计 **22**；累计 **news 91 / 非新闻 41**。

- **Q（本线主动小结 · 2026-10-05 第5轮）：N1 第 5 轮抓了吗？全链对齐全语料了吗？第 6 轮起了吗？**
  **A（本线 2026-10-05 14:30）**：
  - **第 5 轮抓取 ✅**：倒序 `2019-01-24 → 2017-10-30`，语料 **1,645,640 → 1,952,411 条（+306,771）**；片数 8 → **10**（新增 **2018 全年** + **2017-10~12**）。
  - **全链重跑 ✅**（14:07）：`EVENTS.csv` 54,485 → **63,398**（15.27 MB，sha `973a20f394987462`）；`EARLY_WARNING.md` 45 格 `q<0.05` 40→**44**、效果量门槛 18→**19**（同族同法，仅因语料增）。
  - **`STABILITY_LOG.md` 第 6 行 ✅**（14:07，可核验摘要）。
  - **第 6 轮已起 ✅**：倒序 `2017-10-30 → 2016-01-01`，后台抓取 + watcher（**按 `kill -0 <pid>` 等待**，抓完自动 `--index` + 链跑）。
  - **⚠️ 纪律**：停后台抓取须**杀 python 子进程**；等抓取**勿** `pgrep -f <脚本名>`（会自匹配 watcher 命令行 → 死锁）。

---

## 1. 状态头

- **线**：news（新闻采集）
- **任务书**：`WATCH_NEWS_TASK.md`（只读）
- **产物**：`news/<YYYY-MM-DD>.md`（当日摘要）· `news/SEEN.md`（去重台账）· `news/INDEX.md`（索引）
- **N1 语料库**：`news/archive/chinanews-<年>.jsonl.gz`（只 5 字段；**仅取 标题+日期+来源+链接，不抓正文**）；现 **2,492,230 条 / 3929 天 / 11 片**（**2016-01-01 ~ 2026-10-03**；游标 `2015-12-31` = **倒序抓取已收尾**）；⚠️ **≥5MB → 不入 git**，清单见 `news/archive/INDEX_FILES.md`
- **L1 产物**：`news/policy/`（`EDA.md` / `TAXONOMY.md` / `SIGNALS.md` / `EVENTS.csv` / `EARLY_WARNING.md` / **`cycle_run.py` + `STABILITY_LOG.md`（G2′④ 运行台账）**）
- **L2 产物（探索性 · 非因果）**：`news/policy/`（`L2_PREREG.md` / **`EXPLORE.md` + `explore.csv`**）
- **日流水**：`daily-memories-news/<YYYY-MM-DD>.md`
- **采集节律**：**每天 2 次定时唤醒（06:00 / 18:00，`SCHEDULE_HOURS=6,18`）**，时窗内零 token 分段睡（2026-10-07 用户令）；**`WAITING` 已不影响节律**（仅人读状态）；旧自适应 `WAITING=1`→睡 30min / `WAITING=0`→短睡 60s **降级为「仅回退模式」**（`WATCH_SCHEDULE_HOURS=` 置空时启用）
- **第 11 批产物（P0 · 新闻信号 → 资产价格）**：见 `news/signal/`〔`PREREG.md` / `SOURCE_TEST.md` / `prices/`（38 标的十年 2016–2026）/ `lag_corr.py` → `lag_corr.csv` + `LAG_CORR.md` / `BOOTSTRAP.md` / `FINDINGS.md` / `LATEST_SIGNALS.md` / `AM_PM_CHECK.md` / `INDEX_FILES.md` / `REPORT.html` / `daily/<date>.md`〕；⚠️ ≥5MB 不入 git（`lag_corr.csv` ≈ **4.0MB ⇒ 入 git**）
- **上次采集窗口**：`2026-10-11 15:06 CST` ~ `2026-10-11 18:20 CST` ＝ **第八十六轮**（18:00 时窗轮 ⇒ 本窗 ≈ **3.2h**；同一自然日的早报/午间轮已单记）
- **累计收录**：`news` **224** 条（第一~八十六轮；当日 **20**）+ 非新闻（口径=逐行统计 `SEEN.md` 类型列）〔**仅存 `SEEN.md`**〕

---

## 2. 流水（倒序，保留最近 ~20 条）

- **2026-10-11（第 13 批 · P0 · 18:00 时窗）** —— ✅ **本轮交付（微头条 1 篇 + 引流评论 4 条 + 第八十六轮采集）**。**① 发文**：微头条 **18:05**「国家安全部提醒：接陌生电话可先「沉默三秒」再开口——数秒语音样本就可能被克隆声音」（**4 段 / 200 字（实测）** · **纯文字**）⇒ 后台 **已发布 / 首发** · 作品页 **`toutiao.com/w/1878747404777480/`**；**距 15:01 首篇 ≈3h04min ≥ 90min ✅**（本日 **2 篇 / 上限 6**）。**② 声明（§9）**：作品声明**单选**、「引用 AI」与「个人观点，仅供参考」**互斥** ⇒ 取 **「引用 AI」** + 头条首发。**③ ⚠️ 配图（§8）**：发布页「图片」面板**仅见上传 · 未见免费图库入口** ⇒ **纯文字发** · 台账记 `无图` ⚠️（写入 `SPEC §8.1`，待用户确认是入口问题还是本号未开通）。**④ 引流评论 4 条（全成功 · 均列前排）**：玄奘/《大唐西域记》· WorkBuddy×Office 三件套 · 新疆佛塔《三国志》· 200 个 AI 虚拟文明；**频道页 + 热榜实测争议/民族/标题党偏重 ⇒ 弃用**，4 条**全部取自「推荐」流**（§5 · 均 ≤40 字）。**⑤ 回评 0（如实）**：`评论管理` 仍为「豆包」机器人 + 旧帖，无「真实提问 / 理性讨论」可回。**⑥ 评论框机制（实测 · 归档 `SPEC §5.1`）**：`.comment-textarea` 必须派发 `beforeinput`/`input`/`keyup`/`change` 才激活 `button.submit-btn`（仅 `Input.insertText` 不生效）。**⑦ 第八十六轮采集（news +7 · 中 7 / 英 0 · 15:06→18:20 ≈ 3.2h）** ⇒ `news/2026-10-11.md` + `INDEX.md`/`SEEN.md`（+11 行 · 累计 **224**）；**量子位 feed 恢复**（补收 3：`502585`/`502550`/`502544`；`502584` 留档不重收）；`reuters.com`/`bbc.co.uk`/`ft.com` 仍不可达（如实）。**⑧ 台账/基线**：粉丝 **70**（无变化）· 收益 **6.38 元** · 微头条 **420 条**（+1）· 主页「**Xmodel唠两句**」1.7 万获赞 / 134 关注。**⑨ G2′④**：同天只计 1 天（15:16 已跑）⇒ **18:00 不重跑**（连续 **7/7 ✅**）。**⑩ CDP 卫生**：3 tab 按 id 关闭 + `prune toutiao.com`（留 1）· 未触 zhipin · 凭据未落盘。
- **2026-10-11（第 13 批 · P0 · 15:00 时窗：首轮 15:00 + 复唤醒维护轮 15:06）** —— ✅ **首轮交付：微头条 1 篇（15:01 已发布 / 首发 · 尼康撤奖 × AI 诚信）+ 复唤醒维护轮 0 篇（合规）**：新建 **news 线专用 CDP 助手 `~/news_cdp.js`**（`list/newtab/eval/type/click` · 不带 Origin 头 · **未入 git**）· 作品页 `toutiao.com/w/1878735833613380/` · 台账 `news/toutiao/台账.md` 首版（基线粉丝 70 / 总阅读 33,574）· 选题储备 `drafts/2026-10-11-ai-voice-clone-sms.md`（275 字 · 供 18:00 轮）· 第八十五轮常态采集 news +7（当日 13 / 累计 217）· G2′④ `2026-10-11 15:16` 真实重跑（连续 7/7 天 ✅）。流水**原文已滚入** `daily-memories-news/2026-10-11.md`（`[15:00]` / `[15:06]` 心跳；**原文不改 · 结论不变**）。**→ 18:00 轮明细见本表首条。**
- **2026-10-10（第 11 批 · R6 · P0 · 18:00 晚报轮）** —— ✅ **R6 交付**（38 标的价格再全量刷新 `ok=38/fail=0` ⇒ 末日 **38/38 = 2026-10-09** · `lag_corr.csv` 与 R1–R5 **逐字节一致**〔第 6 次〕· `INDEX_FILES.md`/`LAG_CORR.md`/`FINDINGS.md` R6 重登记 · 日报 `daily/2026-10-10.md` **PM 单写版** · `cycle_run.py` 真实重跑 ⇒ `STABILITY_LOG.md` **`2026-10-10 18:08`** 行 ⇒ 连续 **6/7 天 · ⚠️ 未达标（如实）** · 第八十三轮 news **+10**）。**全文见 `daily-memories-news/2026-10-10.md` `[18:00]` 心跳（不改 · 结论不变）**。

- **2026-10-09（18:30 · 重试唤醒 · 0 新增）** —— ⚠️ loop 对 18:00 时窗的**重试**（18:00 轮 cline 18:25:07 `exit 1`；产物已落盘并由 loop 兜底 auto-commit `b60b308c` 推送）。独立复核 `sha256(lag_corr.csv)`=`83d3bf34…`（=R1–R5 一致）· 23,941 行 · 末日 {2026-10-09:28, 2026-10-08:10}（汇率源未发布 · **未补造**）· `HEAD`=`origin/main` · 工作区干净 ⇒ **不重复跑 P0 ⇒ 0 新增**（§4-3 / §4-9 / §4-10）。

- **2026-10-09（第 11 批 · R5 · P0 · 18:00 晚报轮）** —— ✅ 交付（`fetch_prices.py --refetch` ok=38/fail=0 · `lag_corr.csv` 与 R1–R4 逐字节一致〔第 5 次〕· 🛡 `am_pm_check.py` 新增拒写护栏 · `daily/2026-10-09.md` PM 版 · `cycle_run.py` 真实重跑 ⇒ `STABILITY_LOG.md` **18:15** 行 ⇒ 连续 5/7 天）。**流水摘要已上移本表首条；原文/全文见 `daily-memories-news/2026-10-09.md` `[18:00]` 心跳（不改 · 结论不变）**。

- **2026-10-09（06:20 · 重试唤醒 · 0 新增）** —— ⚠️ loop 对 06:00 时窗的**重试**（首次 cline `exit 143` = SIGTERM ⇒ `sleep 300s` → 重试 1/1；`/tmp/watch_news_loop.log` **06:15:37 / 06:20:44** 两行可核验）。**06:00 轮工作已于 06:15 完成并推送**（`e0f89c79` + `32c5d251`；`HEAD`=`origin/main`、news 线工作区干净；`sha256(lag_corr.csv)` 复核一致）⇒ **本轮不重复跑任何 P0 动作 ⇒ 0 新增**（§4-3 / §4-10）。全文见 `daily-memories-news/2026-10-09.md`。

- **2026-10-09（第 11 批 · R4 · P0 · 06:00 早报轮）** —— ✅ **R4 交付**（38 标的**再全量刷新** `ok=38/fail=0` · 相对 R3 **唯一实质变化 = 10 条汇率末日 2026-10-07 → 2026-10-08**〔**源侧补齐 · 未补造**〕，其余 28 个价格文件行数据**逐字节相同**〔差异仅 `fetched_at`〕· `lag_corr.py` **R4 复核重跑 ⇒ `lag_corr.csv` 与 R1–R3 逐字节一致**〔sha256 `83d3bf349be52251…` · 4,018,511 B · 23,941 行 · `q<0.10`=0 · `stable`=0；**原因可证：分析窗口止于 2026-09-30 ⇒ 新增 10-08 行整体落窗外**〕· 三处生成器重跑〔`LAG_CORR.md` R4 头 / `LATEST_SIGNALS.md` sha 未变 / `FINDINGS.md` §3 追加〕· **`INDEX_FILES.md` R4 重登记**〔目录级指纹 `8699b2b2b16407cf` · 合计 2,561,195 B · 末日一致性 38/38 ✅〕· ⚠️ **R4 未新增「早报→当日」机械复核对（如实 · 不充数）** · 日报 `daily/2026-10-09.md` **AM 版** · 第八十一轮常态采集 news +5）。流水**原文已滚入** `daily-memories-news/2026-10-09.md`（`[06:00]` 心跳；**原文不改 · 结论不变**）。

- 🔀 **2026-10-08（第 11 批 · R3 · P0 · 18:00 晚报轮 · 同日第二版）** —— ✅ **P0 R3 + 第八十轮 news +2 + `cycle_run.py` 真实重跑**（R3 = 38 标的价格全量刷新 ok=38/fail=0 · 三处窗口口径补丁「价格 ∩ 语料」截断 · `lag_corr.csv` **与 R2 逐字节一致** · 🆕 `am_pm_check.py` → `AM_PM_CHECK.md`〔63 格·未赢基线〕· `INDEX_FILES.md` R3 重登记 · `daily/2026-10-08.md` PM 版 · 台账追加 `18:24` 行〔指纹 `9909e4cddcf525a8`〕）。流水**原文已滚入** `daily-memories-news/2026-10-08.md`（`[18:25]` 心跳；**原文不改 · 结论不变**）。

- 🔀 **2026-10-08（第 11 批 · R2 · P0 · 06:00 早报轮）** —— ✅ **P0 R2（`block_boot.py` 3 组 G1/G2/G3〔G3 = 19/20 CI 跨 0〕+ `FINDINGS.md` + 首份早报 AM + `LAG_CORR.md` R2 头）+ 第七十九轮 news +6**。流水**原文已滚入** `daily-memories-news/2026-10-08.md`（`[06:10]` 心跳；**原文不改 · 结论不变**）。



- **2026-10-07（第 11 批 · R1 · P0）** —— ✅ **新闻信号→资产价格 R1 交付**：`news/signal/` = **PREREG.md（先于结果）+ SOURCE_TEST.md（源实测 ok=38/fail=0）+ fetch_prices.py + prices/〔38 标的/6 类/2016–2026·2.56MB〕+ INDEX_FILES.md + lag_corr.py → lag_corr.csv（23940 格）+ LAG_CORR.md**。**结论（如实·非因果·非投资建议）**：**FDR 后 `q<0.10`=0、`stable`=0**；未校正 `p<0.05`=1217/23940≈5.08%≈随机基线 ⇒ **未发现稳定滞后相关**（负面结果照写）。详见 `daily-memories-news/2026-10-07.md` `[18:00]` 心跳。

- 🔀 **第七十八~五十九轮及更早（2026-10-06~10-07，第 10 批块 + 第七十八~十九轮；news +25）**：流水原文均已滚入 `daily-memories-news/2026-10-06.md` / `2026-10-07.md`（📦 滚动归档 · **原文不改·结论不变**）。要点：**78** 软件股阶段新高 · **77** OpenAI 数学 722 手稿 / 美司法部「超级智能」/ SpaceX $40B · **76** Anthropic CVP 129k 漏洞 · **75** Melius $20M · **74** 留空 · **73~63** Underdog / Musubi PolicyLM-1.7B / Lambda $4B / Wajo / Mirror Particle / EmbeddingGemma 2 / Claude Team（+7）· **62** FSD 欧盟 / LibreOffice「no AI」· **61** AMD 苏姿丰 · **60** Mistral Large 4 等（+4）· **59 及更早**（含第 10 批块）见归档。
