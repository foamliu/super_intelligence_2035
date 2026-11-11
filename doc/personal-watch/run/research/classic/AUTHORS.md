# 作者关系网（B 轨 · 滚动维护）

> 依据：`WATCH_RESEARCH_TASK.md` 用户令 2026-11-11（「找到这些作者的 X 账号并 follow，把这些顶级研究者的最新言论也作为给 news 投料的一部分」）。
> 字段：`姓名 · 机构 · 代表论文(1–2) · 邮箱(如公开) · 主页 · X 账号(@handle) · 状态(待跟踪/已follow/已发信/已回复) · 备注`
>
> 🔴 **找 X 的铁律（不猜）**：只登记**能从可访问页面读到**的 handle（本轮唯一可用手段 = 作者本人主页 `href` 实测）；**读不到 = 写「未找到 X」**。
> 🚫 不许猜 handle（猜错会 follow 到无关账号，比不 follow 更糟）。X.com 本身本轮不可达（见文末探测证据），因此**无法在本轮做任何 follow 动作**。

**本轮快照**：累计 **8** 人｜已发信 **1**（Tri Dao）｜X 已核验 **2**（`@tri_dao` / `@_albertgu`）｜X 未找到 **6**｜已 follow **0（BLOCKED）**

---

## 一、关系网主表

### 1. Tri Dao

| 字段 | 内容 |
|:--|:--|
| 姓名 | Tri Dao（越南裔美国人 ⇒ 信按英文写） |
| 机构 | Princeton University（Computer Science，助理教授）· 兼 Together AI |
| 代表论文 | FlashAttention（arXiv `2205.14135`，一作）· Mamba（arXiv `2312.00752`，二作） |
| 邮箱 | **tri@tridao.me**（来源：`https://tridao.me/assets/pdf/cv.pdf` 实测 `HTTP 200` / 212,820 B / `pdftotext` 提取；**非 PDF 里的旧地址**） |
| 主页 | <https://tridao.me>（实测 `HTTP 200` / 23,797 B） |
| X 账号 | **@tri_dao**（核验方式：主页 `contact-icons` 区块 `href="https://twitter.com/tri_dao"`，title 标注 `X username`） |
| 状态 | **已发信**（2026-11-11 11:5x CST，经典论文请教信第 1 封）· X 待 follow（BLOCKED） |
| 备注 | 同时是一作/二作的 Mamba 与 FlashAttention 都进了本轮经典清单 ⇒ **一份关系覆盖两条线**（pretrain 吞吐 + zhulong 架构消融）。回复若涉及 kernel 细节，可直接回填 pretrain 的 attention 排障与 harness 的成本口径。 |

### 2. Albert Gu

| 字段 | 内容 |
|:--|:--|
| 姓名 | Albert Gu（中文名 顾世翔；按英文写） |
| 机构 | Carnegie Mellon University（Machine Learning Department / CSD） |
| 代表论文 | Mamba（arXiv `2312.00752`，一作）· S4 / 结构化状态空间系列 |
| 邮箱 | **未找到**（`goombalab.github.io` 主页与 `/blog/` 均实测 `HTTP 200` 但**无 `mailto:`**；CMU 个人页 `www.cs.cmu.edu/~albertgu/` 与 `ml.cmu.edu` 教职页均不可用/404 ⇒ 按纪律**不写猜测邮箱**） |
| 主页 | <https://goombalab.github.io>（实测 `HTTP 200` / 16,373 B） |
| X 账号 | **@_albertgu**（核验方式：主页 `href="https://x.com/_albertgu"`） |
| 状态 | **待跟踪**（X 待 follow · 邮箱待公开后再发信） |
| 备注 | 与 Tri Dao 是同一实验室合作链，**同轮不重复发信**（避免「同一合作圈两封信」的打扰感）；下轮若其 CMU 页面恢复或论文新投出现新邮箱再评估。 |

### 3. Ashish Vaswani

| 字段 | 内容 |
|:--|:--|
| 姓名 | Ashish Vaswani |
| 机构 | Essential AI（联合创始人；OpenAlex 记为 Google，为论文发表时机构） |
| 代表论文 | Attention Is All You Need（arXiv `1706.03762`，一作） |
| 邮箱 | **未找到**（个人主页 `ashishvaswani.com` 本轮实测 `HTTP 000`，不可达；无其它公开页可核） |
| 主页 | 未核验（同上，不可达） |
| X 账号 | **未找到 X**（不可达 ⇒ 不查不猜） |
| 状态 | 待跟踪 |
| 备注 | 2017 年论文，PDF 上的邮箱已过 9 年，按令**必须**用当前机构主页邮箱；本轮拿不到 ⇒ 不发信。 |

### 4. Noam Shazeer

| 字段 | 内容 |
|:--|:--|
| 姓名 | Noam Shazeer |
| 机构 | Google DeepMind（OpenAlex 记为 Google，为论文发表时机构） |
| 代表论文 | Attention Is All You Need（二作）· 后续 MoE / 稀疏专家系列 |
| 邮箱 | **未找到**（无个人主页可取） |
| 主页 | 未找到 |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | 顶级工程型研究者，X 上极其活跃（据公开报道），**但本轮无法核验 handle ⇒ 不登记**；拿到可访问来源后再补。 |

### 5. Niki Parmar

| 字段 | 内容 |
|:--|:--|
| 姓名 | Niki Parmar |
| 机构 | Essential AI（联合创始人；OpenAlex 记为 Google/USC） |
| 代表论文 | Attention Is All You Need（三作） |
| 邮箱 | **未找到** |
| 主页 | 未找到（本轮未命中可访问主页） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | — |

### 6. Jordan Hoffmann

| 字段 | 内容 |
|:--|:--|
| 姓名 | Jordan Hoffmann |
| 机构 | **未核实**（OpenAlex authorship 的 `institutions` 为空；论文发表时为 DeepMind） |
| 代表论文 | Training Compute-Optimal LLMs / Chinchilla（一作） |
| 邮箱 | **未找到** |
| 主页 | 未找到 |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | Chinchilla 的「20 token/参数」是 data 线直接依据，优先补其当前机构与邮箱。 |

### 7. Sebastian Borgeaud

| 字段 | 内容 |
|:--|:--|
| 姓名 | Sebastian Borgeaud |
| 机构 | **未核实**（OpenAlex 未给；论文发表时为 DeepMind） |
| 代表论文 | Chinchilla（二作） |
| 邮箱 | **未找到** |
| 主页 | 未找到 |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | — |

### 8. Arthur Mensch

| 字段 | 内容 |
|:--|:--|
| 姓名 | Arthur Mensch |
| 机构 | Mistral AI（联合创始人 & CEO，据公开报道；OpenAlex 未给机构） |
| 代表论文 | Chinchilla（三作） |
| 邮箱 | **未找到**（Mistral 官网团队页本轮未取到可用邮箱；按纪律不猜） |
| 主页 | 未找到（本轮未取到可访问个人页） |
| X 账号 | **未找到 X**（不猜） |
| 状态 | 待跟踪 |
| 备注 | 工业界 CEO，回信概率低但**公开言论对 news 有价值**（属 `voice_ready` 的候选来源，须拿到原文 + 链接才可用）。 |

---

## 二、🔴 X 能力探测（只读 · 2026-11-11 11:3x–11:4x CST）

> 令要求「先验证能力再动手」。**结论：BLOCKED(x_access)** —— 本机对 X 的出网被阻断，且无浏览器 / MCP 通道、无授权凭据。

| 探针 | 命令（原样） | 结果 |
|:--|:--|:--|
| 1 | `curl -sI -m 20 https://x.com/karpathy` | **无任何响应头返回**（空输出，exit 0 = curl 走到超时分支） |
| 2 | `curl -o /dev/null -m 8 -w '%{http_code} %{time_total}' https://x.com/` | **`000` / 8.00s**（连接阶段即失败） |
| 3 | `curl -o /dev/null -m 8 https://google.com/` | **`000` / 8.00s** |
| 4 | `curl -o /dev/null -m 8 https://huggingface.co/` | **`000` / 8.00s** |
| 5 | `curl -o /dev/null -m 8 https://tridao.me/` | **`200` / 2.57s** |
| 6 | `curl -o /dev/null -m 8 https://kexue.fm/` | `403` / 0.12s（站点自身拦截） |

**判读**：③④ 与 ② 同时 `000` ⇒ **不是 x.com 单点故障，而是本机出网白名单**（github.io / tridao.me / api.openalex.org / export.arxiv.org 可通）。因此：
- ❌ **不能自动 follow**；🚫 不许注册新账号、不许用未授权凭据登录；
- ✅ 可做的替代：**从作者本人主页核验 handle**（本轮已核验 2 个），并把清单交给用户手动 follow。

### 待 follow 清单（请用户手动执行 · 均已从作者主页核验）

| # | 人物 | handle | 主页链接 | 为什么值得跟 |
|:--|:--|:--|:--|:--|
| 1 | Tri Dao | `@tri_dao` | <https://x.com/tri_dao> | FlashAttention / Mamba 作者，kernel 与长上下文进展的第一手来源 |
| 2 | Albert Gu | `@_albertgu` | <https://x.com/_albertgu> | SSM / Mamba 路线主推者，架构选择的判断值得跟踪 |

> 两个链接的 handle 均来自其**本人主页**的 `href`（`twitter.com/tri_dao` / `x.com/_albertgu`），非搜索猜测。用户 follow 后请在本表把状态改为 `已follow` 并写日期，后续 `voice_ready` 才能标「已核验账号」。

---

## 三、发信记录（本线经典轨）

| 日期 | 对象 | 论文 | 邮箱来源 | 结果 |
|:--|:--|:--|:--|:--|
| 2026-11-11 11:5x | Tri Dao | `2205.14135` FlashAttention | 个人 CV PDF（2026 版） | 见 `research/mail/发送记录.md` |

---

## 四、维护纪律

1. **一次一作者**：同一作者 / 同一论文 ≤1 封；同一机构 ≤2 封/天（`RESEARCH_MAIL_SPEC §3`）。
2. **邮箱取当前机构主页 / 本人 CV 的最新地址**，🚫 不用 5 年前 PDF 首页的旧邮箱（可能已失效或转他人）。
3. **X handle 只登记可访问页面读到的**；X 不可达期间，`voice_ready` 只能用「转引自 <媒体>，未见原推」，且**不得**标 `voice_ready`。
4. 状态四态：`待跟踪` → `已follow` → `已发信` → `已回复`；每次只前进，不跳级、不回退（回信内容另存 `research/mail/replies/`）。
