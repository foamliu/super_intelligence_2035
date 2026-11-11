# 作者关系网（B 轨 · 滚动维护）

> 依据：`WATCH_RESEARCH_TASK.md` 用户令 2026-11-11（「找到这些作者的 X 账号并 follow，把这些顶级研究者的最新言论也作为给 news 投料的一部分」）。
> 字段：`姓名 · 机构 · 代表论文(1–2) · 邮箱(如公开) · 主页 · X 账号(@handle) · 状态(待跟踪/已follow/已发信/已回复) · 备注`
>
> 🔴 **找 X 的铁律（不猜）**：只登记**能从可访问页面读到**的 handle（本轮唯一可用手段 = 作者本人主页 `href` 实测）；**读不到 = 写「未找到 X」**。
> 🚫 不许猜 handle（猜错会 follow 到无关账号，比不 follow 更糟）。X.com 本身本轮不可达（见文末探测证据），因此**无法在本轮做任何 follow 动作**。

**本轮快照**：累计 **13** 人｜已发信 **3**（Tri Dao · Shunyu Yao · Haoxing Ren）｜X 已核验 **4**（`@tri_dao` / `@_albertgu` / `@ShunyuYao12` / `@edwardjhu`）｜X 未找到 **9**｜已 follow **0（BLOCKED，见第二节）**

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

### 9. Shunyu Yao

| 字段 | 内容 |
|:--|:--|
| 姓名 | Shunyu Yao（拼音名；中文汉字写法**未核实 ⇒ 不写**；信按中文写，判据 = 中文姓名 + 中文主页/中文媒体链接） |
| 机构 | **OpenAI**（个人主页 2026-11-11 实测自述「I am a researcher at OpenAI. I study agents.」；ReAct 发表时为 Princeton） |
| 代表论文 | ReAct（arXiv `2210.03629`，一作）· Tree of Thoughts（`2305.10601`，一作）· Computer-Using Agent（OpenAI 产品线） |
| 邮箱 | **shunyuy@princeton.edu**（来源：`https://ysymyth.github.io/` 页内 `mailto:` 实测 `HTTP 200` / 17,240 B；⚠️ 仍是 Princeton 域名，但为**本人当前主页仍在挂的地址**，非论文 PDF 旧邮箱） |
| 主页 | <https://ysymyth.github.io>（实测 `HTTP 200` / 17,240 B） |
| X 账号 | **@ShunyuYao12**（核验方式：主页 header 社交图标 `href="https://www.twitter.com/ShunyuYao12"`；同页多篇论文的 "tweet" 链接均指向该 handle） |
| 状态 | **已发信**（2026-11-11 11:43 CST，中文，230 字）· X 待 follow（BLOCKED） |
| 备注 | ReAct 是 harness 线「think→act→observe」骨架来源；现做 CUA / Deep Research 一类 agent 产品，**其一手言论对 news 的 `voice_ready` 价值高**（须拿到原文 + 链接才可用）。 |

### 10. Edward J. Hu

| 字段 | 内容 |
|:--|:--|
| 姓名 | Edward J. Hu（中文名**未核实 ⇒ 不写**） |
| 机构 | Mercor（个人主页 2026-11-11 实测自述「leading model training and research at Mercor」；LoRA 发表时为 Microsoft） |
| 代表论文 | LoRA（arXiv `2106.09685`，一作） |
| 邮箱 | **未找到**（`edwardjhu.com` 与 `/about` 均实测无 `mailto:` / 无可提取邮箱；`/about` 仅 162 B，疑为跳转页 ⇒ 按纪律不猜） |
| 主页 | <https://edwardjhu.com>（实测 `HTTP 200` / 39,953 B） |
| X 账号 | **@edwardjhu**（核验方式：主页社交链接 `data-title="twitter.com/edwardjhu"` + `href="https://twitter.com/edwardjhu"`） |
| 状态 | **待跟踪**（X 可跟；邮箱缺失 ⇒ 本轮不发信） |
| 备注 | LoRA 是 vision 线 CPU 小样本微调与 pretrain PEFT 对照的默认基线；等其公开邮箱后再发信。 |

### 11. Haoxing Ren（Mark Ren）

| 字段 | 内容 |
|:--|:--|
| 姓名 | Haoxing Ren（主页自称 **Mark Ren**；中文汉字写法**未核实 ⇒ 不写**） |
| 机构 | **Agentrys**（创始人，做 Agentic Design Automation）· 此前 NVIDIA Research（26 年 IBM Research + NVIDIA Research，主页自述） |
| 代表论文 | ChipNeMo（`2311.00176`，末位作者 / 项目负责人）· VerilogEval（`2309.07544`，末位作者） |
| 邮箱 | **info@agentrys.ai**（来源：`https://agentrys.ai` 页内 `mailto:`，实测 `HTTP 200` / 14,610 B；**公司公开信箱，非个人邮箱**，信首已请转交） |
| 主页 | <https://haoxingren.github.io/>（实测 `HTTP 200` / 16,340 B，内容自证 NVIDIA / ChipNeMo / VerilogEval） |
| X 账号 | **未找到 X**（主页仅 Google Scholar + LinkedIn 链接，无 `x.com` / `twitter.com` href） |
| 状态 | **已发信**（2026-11-11 11:43 CST，中文，246 字，发至公司信箱） |
| 备注 | 2× DAC Best Paper、IEEE Fellow；其「Agentic Design Automation」方向与 designflow 线高度重合，是最值得长期跟踪的工业界人物。 |

### 12. Mingjie Liu

| 字段 | 内容 |
|:--|:--|
| 姓名 | Mingjie Liu（中文名写法未核实 ⇒ 不写） |
| 机构 | NVIDIA（OpenAlex 作者记录 `A5100681148` 的 `last_known_institutions` = Nvidia (United States)；ChipNeMo / VerilogEval 一作） |
| 代表论文 | ChipNeMo（`2311.00176`，一作）· VerilogEval（`2309.07544`，一作） |
| 邮箱 | **未找到**（未找到可访问的本人主页；NVIDIA 企业邮箱不公开 ⇒ 不猜） |
| 主页 | **未找到**（试 `mingjieliu.github.io` / `mingjiel.github.io` 均 `404`、`mingjieliu.com` DNS 不解析） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | 两篇 EDA 经典的一作；若后续找到其主页/邮箱，优先补信（与 Haoxing Ren 同一合作圈，**同轮不重复打扰**）。 |

### 13. Nathaniel Pinckney

| 字段 | 内容 |
|:--|:--|
| 姓名 | Nathaniel Pinckney |
| 机构 | NVIDIA（ChipNeMo 与 VerilogEval 作者，机构按论文署名） |
| 代表论文 | VerilogEval（`2309.07544`，二作）· ChipNeMo（`2311.00176`，中间作者） |
| 邮箱 | **未找到** |
| 主页 | **未找到**（本轮未命中可访问主页） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | — |

---

## 二、🔴 X 能力探测（只读 · 2026-11-11 11:3x–11:4x CST 两轮）

> 令要求「先验证能力再动手」。**结论：BLOCKED(x_access)** —— 本机对 X 的出网被阻断，且无浏览器 / MCP 通道、无授权凭据。

| 探针 | 命令（原样） | 结果 |
|:--|:--|:--|
| 1 | `curl -sI -m 20 https://x.com/karpathy` | **无任何响应头返回**（空输出，exit 0 = curl 走到超时分支） |
| 2 | `curl -o /dev/null -m 8 -w '%{http_code} %{time_total}' https://x.com/` | **`000` / 8.00s**（连接阶段即失败） |
| 3 | `curl -o /dev/null -m 8 https://google.com/` | **`000` / 8.00s** |
| 4 | `curl -o /dev/null -m 8 https://huggingface.co/` | **`000` / 8.00s** |
| 5 | `curl -o /dev/null -m 8 https://tridao.me/` | **`200` / 2.57s** |
| 6 | `curl -o /dev/null -m 8 https://kexue.fm/` | `403` / 0.12s（站点自身拦截） |
| 7（第二轮复测） | `curl -o /dev/null -m 10 https://x.com/` | **`000` / 10.002s** |
| 8（第二轮复测） | `curl -o /dev/null -m 10 https://x.com/ShunyuYao12` | **`000` / 10.003s** |
| 9（同轮对照） | `curl -o /dev/null -m 10 https://export.arxiv.org/` | **`200` / 1.16s** |

**判读**：③④⑦⑧ 同时 `000`，而 ⑨ 与 `github.io` / `tridao.me` / `api.openalex.org` 可通 ⇒ **不是 x.com 单点故障，而是本机出网白名单**。因此：
- ❌ **不能自动 follow**；🚫 不许注册新账号、不许用未授权凭据登录；
- ✅ 可做的替代：**从作者本人主页核验 handle**（两轮累计已核验 4 个），并把清单交给用户手动 follow。

### 待 follow 清单（请用户手动执行 · 均已从作者本人主页核验）

| # | 人物 | handle | 主页链接 | 为什么值得跟 |
|:--|:--|:--|:--|:--|
| 1 | Tri Dao | `@tri_dao` | <https://x.com/tri_dao> | FlashAttention / Mamba 作者，kernel 与长上下文进展的第一手来源 |
| 2 | Albert Gu | `@_albertgu` | <https://x.com/_albertgu> | SSM / Mamba 路线主推者，架构选择的判断值得跟踪 |
| 3 | Shunyu Yao | `@ShunyuYao12` | <https://x.com/ShunyuYao12> | ReAct / ToT 一作，现于 OpenAI 做 agent 产品（CUA / Deep Research），agent 方向言论密度高 |
| 4 | Edward J. Hu | `@edwardjhu` | <https://x.com/edwardjhu> | LoRA 一作，PEFT 与训练实践的第一手来源 |

> 四个 handle 均来自其**本人主页**的 `href`（`twitter.com/tri_dao` / `x.com/_albertgu` / `www.twitter.com/ShunyuYao12` / `twitter.com/edwardjhu`），非搜索猜测。用户 follow 后请在本表把状态改为 `已follow` 并写日期，后续 `voice_ready` 才能标「已核验账号」。

---

## 三、发信记录（本线经典轨）

| 日期 | 对象 | 论文 | 邮箱来源 | 结果 |
|:--|:--|:--|:--|:--|
| 2026-11-11 11:36 | Tri Dao | `2205.14135` FlashAttention | 个人 CV PDF（2026 版） | `SENT OK`（见 `research/mail/发送记录.md`） |
| 2026-11-11 11:43 | Shunyu Yao | `2210.03629` ReAct | 本人主页 `mailto:` | `SENT OK`（`shunyuy@princeton.edu`） |
| 2026-11-11 11:43 | Haoxing Ren | `2311.00176` ChipNeMo · `2309.07544` VerilogEval | 公司站 `mailto:`（`info@agentrys.ai`，请转交） | `SENT OK`（公司公开信箱） |

---

## 四、维护纪律

1. **一次一作者**：同一作者 / 同一论文 ≤1 封；同一机构 ≤2 封/天（`RESEARCH_MAIL_SPEC §3`）。
2. **邮箱取当前机构主页 / 本人 CV 的最新地址**，🚫 不用 5 年前 PDF 首页的旧邮箱（可能已失效或转他人）。
3. **X handle 只登记可访问页面读到的**；X 不可达期间，`voice_ready` 只能用「转引自 <媒体>，未见原推」，且**不得**标 `voice_ready`。
4. 状态四态：`待跟踪` → `已follow` → `已发信` → `已回复`；每次只前进，不跳级、不回退（回信内容另存 `research/mail/replies/`）。
