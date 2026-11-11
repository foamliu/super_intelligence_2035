# 作者关系网（B 轨 · 滚动维护）

> 依据：`WATCH_RESEARCH_TASK.md` 用户令 2026-11-11（「找到这些作者的 X 账号并 follow，把这些顶级研究者的最新言论也作为给 news 投料的一部分」）。
> 字段：`姓名 · 机构 · 代表论文(1–2) · 邮箱(如公开) · 主页 · X 账号(@handle) · 状态(待跟踪/已follow/已发信/已回复) · 备注`
>
> 🔴 **找 X 的铁律（不猜）**：只登记**能从可访问页面读到**的 handle（作者本人主页 `href`，并用 X 页 `og:description` 二次核对身份）；**读不到 = 写「未找到 X」**。
> 🚫 不许猜 handle（猜错会 follow 到无关账号，比不 follow 更糟）。X.com 自 **2026-11-11 12:4x** 起经本机 Mihomo 代理**只读可达**；**follow 仍需登录态 ⇒ 未自动执行**（0 follow，未假装）。

**本轮快照**：累计 **28** 人（第五轮 +5：Kaiming He / Ilya Sutskever / Richard S. Sutton / Haotian Liu / Chunyuan Li）｜已发信 **7**（Tri Dao · Shunyu Yao · Haoxing Ren · Jason Wei · Noah Shinn · **Kaiming He · Haotian Liu**）｜X 已核验 **10**（`@tri_dao` / `@_albertgu` / `@ShunyuYao12` / `@edwardjhu` / `@jyangballin` / `@_jasonwei` / **`@ilyasut` / `@RichardSSutton` / `@imhaotian` / `@ChunyuanLi`**）｜X 未找到 **18**｜**X 已恢复可达（2026-11-11 12:4x 起，经本机 Mihomo 7897，`x.com` `200` / 出口 `178.249.213.185`）**｜已 follow **0**（follow 需登录态 ⇒ 仍靠用户手动，见第二节）｜已核验言论 **4 条**（V1–V4；本轮新增 V4 Sutton）


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

### 14. Jason Wei

| 字段 | 内容 |
|:--|:--|
| 姓名 | Jason Wei（美籍 ⇒ 信按英文写） |
| 机构 | **Meta Superintelligence Labs**（本人主页实测「I currently work at Meta Superintelligence Labs. From 2023 to 2025, I was at OpenAI…」；CoT 发表时为 Google Brain） |
| 代表论文 | Chain-of-Thought（`2201.11903`，一作）· 指令微调 / 涌现能力系列 |
| 邮箱 | **jason.weng.wei@gmail.com**（来源：`https://jasonwei.net/` 页内 `mailto:` 实测；**非 2022 年论文 PDF 旧地址**） |
| 主页 | <https://jasonwei.net>（实测 `HTTP 200` / 116,550 B） |
| X 账号 | **@_jasonwei**（核验方式：主页 `href="https://twitter.com/_jasonwei"`） |
| 状态 | **已发信**（2026-11-11 12:10 CST，经典论文请教信第 4 封）· X 待 follow（BLOCKED） |
| 备注 | 其主页自述「My work helped popularize chain-of-thought, instruction tuning, and emergence」⇒ **一篇经典覆盖 zhulong 的 thinking 轴与 pretrain 的 SFT 数据口径**。⚠️ 邮箱是 gmail 个人信箱（本人主页公开挂出），非机构信箱。 |

### 15. Noah Shinn

| 字段 | 内容 |
|:--|:--|
| 姓名 | Noah Shinn |
| 机构 | 独立研究者 · **前 Sierra**（本人主页实测「Previously, I was a researcher at Sierra, where I joined as one of the first employees.」；Reflexion 发表时为 Northeastern University 编程语言组） |
| 代表论文 | Reflexion（`2303.11366`，一作）· τ-bench（与 Shunyu Yao 合作） |
| 邮箱 | **noahrshinn@gmail.com**（来源：`https://noahshinn.com/` 页内明写 `Email: noahrshinn[at]gmail[dot]com`，去混淆后使用） |
| 主页 | <https://noahshinn.com>（实测 `HTTP 200` / 4,689 B） |
| X 账号 | **未找到 X**（该主页只列 Github / Google Scholar，无 twitter / x.com 链接 ⇒ 按令不猜） |
| 状态 | **已发信**（2026-11-11 12:11 CST，经典论文请教信第 5 封） |
| 备注 | τ-bench 与 Shunyu Yao 合作 ⇒ 与已发信的 Shunyu Yao 属同一合作圈；本轮只写给 Noah（未重复打扰 Shunyu）。 |

### 16. Xuezhi Wang

| 字段 | 内容 |
|:--|:--|
| 姓名 | Xuezhi Wang |
| 机构 | **未核实**（CoT 发表时在 Google；本轮无可访问的本人主页） |
| 代表论文 | Chain-of-Thought（`2201.11903`，二作） |
| 邮箱 | **未找到** |
| 主页 | **未找到**（`xuezhiwang.com` 实测 `HTTP 200` 但页面标题为「w66.com 中国区」赌博站 ⇒ **非本人站点**，不予采用） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | 同论文已发给一作 Jason Wei ⇒ 按「同一合作圈不重复打扰」本轮不发。 |

### 17. Denny Zhou

| 字段 | 内容 |
|:--|:--|
| 姓名 | Denny Zhou |
| 机构 | **未核实**（CoT 发表时在 Google；本轮未核到机构字段） |
| 代表论文 | Chain-of-Thought（`2201.11903`，末位作者）· 推理 / 思维链系列 |
| 邮箱 | **未找到**（`dennyzhou.github.io` 实测 `HTTP 200` / 50,918 B，但页面为多年前的论文列表，**无 `mailto:` / 社交链接**） |
| 主页 | <https://dennyzhou.github.io>（无联系方式） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | 末位作者、CoT 方向长期主导者；拿到可访问的新主页后再补。 |

### 18. Carlos E. Jimenez

| 字段 | 内容 |
|:--|:--|
| 姓名 | Carlos E. Jimenez |
| 机构 | Princeton University（Princeton Language and Intelligence；OpenAlex `institutions` 实测） |
| 代表论文 | SWE-bench（`2310.06770`，一作） |
| 邮箱 | **未找到** |
| 主页 | **未找到**（`carlosej.github.io` DNS 不解析；`www.cs.princeton.edu/~carlosej/` 返回「This person has moved」占位页） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | SWE-bench 一作；论文已由二作 John Yang 的 handle 覆盖（X 侧）。 |

### 19. John Yang

| 字段 | 内容 |
|:--|:--|
| 姓名 | John Yang（主页自称「John Y」） |
| 机构 | Stanford University（CS PhD；本人主页实测「2nd year Computer Science PhD student @ Stanford University」） |
| 代表论文 | SWE-bench（`2310.06770`，二作）· SWE-agent 系列 |
| 邮箱 | **未找到**（主页无 `mailto:`） |
| 主页 | <https://john-b-yang.github.io>（实测 `HTTP 200` / 6,840 B） |
| X 账号 | **@jyangballin**（核验方式：主页 `href="https://x.com/jyangballin"`，同页多条推文链接指向同一 handle） |
| 状态 | 待跟踪 · X 待 follow（BLOCKED） |
| 备注 | SWE-agent / SWE-bench 的主要工程实现者，harness 侧言论密度高；**关注度优先级高**。 |

### 20. Jianlin Su（苏剑林）

| 字段 | 内容 |
|:--|:--|
| 姓名 | Jianlin Su（苏剑林；中文作者 ⇒ 若发信按中文） |
| 机构 | **Zhuiyi Technology（追一科技，深圳）**（OpenAlex `raw_affiliation_strings` 实测：`Zhuiyi Technology Co., Ltd. Shenzhen, China`） |
| 代表论文 | RoFormer / RoPE（`2104.09864`，一作） |
| 邮箱 | **未找到**（`kexue.fm` 站点本轮实测 `HTTP 403`（站点自身拦截），无法读取联系方式） |
| 主页 | <https://kexue.fm>（403，不可读） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | RoPE 是 BaiZe 位置编码的直接来源，**如果只能补一个人的联系方式，优先补他**；但机构邮箱不公开、博客反爬 ⇒ 本轮不发信（不猜邮箱）。 |

### 21. Hugo Touvron

| 字段 | 内容 |
|:--|:--|
| 姓名 | Hugo Touvron（法国人 ⇒ 信按英文写） |
| 机构 | Meta AI（FAIR；LLaMA 一作） |
| 代表论文 | LLaMA（`2302.13971`，一作） |
| 邮箱 | **未找到**（`hugotouvron.github.io` 实测 `HTTP 404`；未找到其它可访问个人页） |
| 主页 | **未找到** |
| X 账号 | **未找到 X**（无可核验来源 ⇒ 不猜） |
| 状态 | 待跟踪 |
| 备注 | LLaMA 的 token 预算口径（1.0–1.4T）是 data 线「小模型多训」一侧的直接依据；**但本文是否公开邮箱未核实 ⇒ 不发信**。⚠️ 今日 Meta 机构已发 1 封（Jason Wei），按「同机构 ≤2 封/天」仍有额度，缺的是**可核验邮箱**。 |

### 22. Long Ouyang

| 字段 | 内容 |
|:--|:--|
| 姓名 | Long Ouyang（中文姓名 ⇒ 若发信按中文） |
| 机构 | OpenAI（InstructGPT 一作；**当前机构未核验**） |
| 代表论文 | InstructGPT（`2203.02155`，一作） |
| 邮箱 | **未找到**（`longouyang.github.io` 实测 `HTTP 404`；无其它公开页） |
| 主页 | **未找到** |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | InstructGPT 的 RLHF 三步与「1.3B 胜过 175B」是 zhulong 对齐轴的基线；**作者已不在论文通讯地址可及的公开页** ⇒ 不发信。 |

### 23. Tom B. Brown

| 字段 | 内容 |
|:--|:--|
| 姓名 | Tom B. Brown（GPT-3 一作；署名 `Tom B. Brown`，常被检索为 `Tom Brown`） |
| 机构 | **未核实**（发表时 OpenAI；OpenAlex 的机构映射把 30/31 位作者记为 Johns Hopkins University —— **明显错误，不采用**） |
| 代表论文 | GPT-3 / Language Models are Few-Shot Learners（`2005.14165`，一作） |
| 邮箱 | **未找到** |
| 主页 | **未找到**（未命中可访问个人页） |
| X 账号 | **未找到 X** |
| 状态 | 待跟踪 |
| 备注 | ⚠️ 同名者极多（`Tom Brown` 在 X 上有多个高仿/同名账号）⇒ 本线**明确不登记任何 handle**，避免 follow 到无关账号。 |

### 24. Kaiming He（何恺明）

| 字段 | 内容 |
|:--|:--|
| 姓名 | Kaiming He（何恺明；中文作者 ⇒ 信按**中文**写） |
| 机构 | **MIT**（EECS，Associate Professor；ResNet 发表时 Microsoft Research） |
| 代表论文 | ResNet（arXiv `1512.03385`，一作）· Mask R-CNN / Focal Loss 等检测线 |
| 邮箱 | **kaiming@mit.edu**（来源：`https://people.csail.mit.edu/kaiming/` 页内明文，2026-11-11 实测 `HTTP 200` / 55,458 B） |
| 主页 | <https://people.csail.mit.edu/kaiming/>（实测 `200`） |
| X 账号 | **未找到 X**（主页面无 twitter / x.com 链接 ⇒ 按令不猜） |
| 状态 | **已发信**（2026-11-11 15:2x CST，B 轨第五轮；中文，≤300 字）· 无 X |
| 备注 | 顶级作者 ⇒ 按令**优先覆盖**。信只问两点：小数据 + 冻结视觉塔下 depth vs width 的取舍、shortcut 恒等映射是否仍关键；以及接进 LN 预训练栈时 BN 该换 GN 还是保留并冻结。 |

### 25. Ilya Sutskever

| 字段 | 内容 |
|:--|:--|
| 姓名 | Ilya Sutskever（按英文写） |
| 机构 | **SSI**（Safe Superintelligence Inc.，联合创始人；seq2seq 发表时 Google） |
| 代表论文 | seq2seq（arXiv `1409.3215`，一作）· AlexNet（2012，二作）· GPT 系列早期工作 |
| 邮箱 | **未找到**（无公开个人主页 / 未见 `mailto:` ⇒ 按纪律不猜、不发信） |
| 主页 | 未找到（无公开个人站；机构站无个人页） |
| X 账号 | **@ilyasut**（核验：`x.com/ilyasut` 实测 `200`，`name` = `Ilya Sutskever (@ilyasut) / X`，`bio` = `SSI @SSI`） |
| 状态 | 待跟踪（X 待 follow；无公开邮箱 ⇒ 不发信） |
| 备注 | 其言论多为长周期观点（scaling / superintelligence），**低频但权重高**；引用需整段上下文，历史推文多超 30 天 ⇒ 按令降级处理。 |

### 26. Richard S. Sutton

| 字段 | 内容 |
|:--|:--|
| 姓名 | Richard S. Sutton（按英文写） |
| 机构 | University of Alberta（教授荣休）· **Keen Technologies**（联合创始人）· amii |
| 代表论文 | Dyna（1991，单作者）· 《Reinforcement Learning: An Introduction》（教材）· TD 学习系列 |
| 邮箱 | **未找到**（`http://incompleteideas.net/` 实测 `200`，页内仅有 amii 行政信箱 `lynda.vang@amii.ca`，**非本人** ⇒ 不写、不发） |
| 主页 | <http://incompleteideas.net/>（实测 `200` / 16,719 B） |
| X 账号 | **@RichardSSutton**（核验：`x.com/RichardSSutton` 实测 `200`，`bio` 含 `UAlberta, amii, The Royal Society, Turing Award`） |
| 状态 | 待跟踪（X 待 follow；无本人公开邮箱 ⇒ 不发信） |
| 备注 | Dyna 作者 ⇒ 「规划/想象」这条线的源头人物；2026-11 仍在高频发言（见言论台账 V4），是 `voice_ready` 的**高价值稳定源**。 |

### 27. Haotian Liu

| 字段 | 内容 |
|:--|:--|
| 姓名 | Haotian Liu（中文作者 ⇒ 信按**中文**写） |
| 机构 | **Meta Superintelligence Lab**（X bio 实测；LLaVA 发表时 UC San Diego） |
| 代表论文 | LLaVA / Visual Instruction Tuning（arXiv `2304.08485`，一作）· LLaVA-1.5（`2310.03744`，一作） |
| 邮箱 | **liuhaotian.cn@gmail.com**（来源：`https://haotian-liu.github.io/` 页内 `mailto:`（percent-encoded），2026-11-11 实测 `200` / 25,018 B） |
| 主页 | <https://haotian-liu.github.io/>（实测 `200`） |
| X 账号 | **@imhaotian**（核验：主页 `href="https://twitter.com/imhaotian"`；`x.com/imhaotian` 实测 `200`，`bio` = `@Meta Superintelligence Lab, prev. @xAI @grok imagine/omni/v`） |
| 状态 | **已发信**（2026-11-11 15:2x CST，B 轨第五轮；中文，≤300 字）· X 待 follow |
| 备注 | 信问两点：①「先冻结 LLM 只训 projection」的收益来源（防遗忘 vs 对齐输入分布），只能保一阶段时保哪个；② 595K 过滤 CC 对齐数据有多关键、专业领域真实图文对稀少时强模型合成描述能否替代。 |

### 28. Chunyuan Li

| 字段 | 内容 |
|:--|:--|
| 姓名 | Chunyuan Li（李春元；中文作者） |
| 机构 | **Google DeepMind**（X bio：`Agentic Vision @Google DeepMind`；此前 xAI / Microsoft Research；LLaVA 发表时 MSR） |
| 代表论文 | LLaVA（arXiv `2304.08485`，二作 / 通讯级）· LLaVA-Med · 多模态指令数据系列 |
| 邮箱 | **lichunyuan24@gmail.com**（来源：`https://chunyuanli.github.io/` 页内 `mailto:`（percent-encoded），实测 `200` / 24,034 B） |
| 主页 | <https://chunyuanli.github.io/>（实测 `200`） |
| X 账号 | **@ChunyuanLi**（核验：主页 `href="https://twitter.com/ChunyuanLi"`；`x.com/ChunyuanLi` 实测 `200`，`bio` = `Agentic Vision @Google DeepMind | Previous: @xAI, @MSFTResearch`） |
| 状态 | 待跟踪（**本轮不与一作同轮发信**，避免同一合作圈两封信） |
| 备注 | 其 bio 已转向「Agentic Vision」⇒ 后续 `voice_ready` 与 VLM-agent 选题的优先跟踪对象。 |

---

## 二、🟢 X 能力探测（只读 · 2026-11-11 **第四轮 12:4x 起已恢复可达**）


> 令要求「先验证能力再动手」。**结论：`OPEN(x_readonly)`（第四轮 12:4x CST 实测）** —— 经运维部署的本机 Mihomo 代理（`http://127.0.0.1:7897`），`x.com` 已可达；**只读可做，写操作（follow/like/发帖）仍需登录态 ⇒ 不做**。

| # | 探针（原样） | 结果 |
|:--|:--|:--|
| 1（前三轮 11:3x / 11:4x / 12:0x） | `curl -o /dev/null -m 8/10 https://x.com/` | **`000` / 8.0–10.0s ×3 次** ⇒ 历史结论 `BLOCKED(x_access)` |
| 2（**第四轮**，显式带代理） | `curl -x http://127.0.0.1:7897 -w '%{http_code} %{time_total}' https://x.com` | **`200` / 0.79s** |
| 3（**第四轮**） | 同上，`https://x.com/karpathy` | **`200` / 0.77s** |
| 4（**第四轮**） | 同上，`https://x.com/_jasonwei` | **`200` / 0.66s**；页内 `<meta property="og:description">` = `ai researcher @meta, past: openai, google` |
| 5（**第四轮**） | `curl -x http://127.0.0.1:7897 https://api.ipify.org` | **`178.249.213.185`**（与运维给的出口一致） |
| 6（**第四轮**） | 未带代理的同一台机器 | **`000`** ⇒ 必须显式走代理；本线 shell 未继承 `~/.profile` 的变量（`env` 实测为空），脚本内已内置默认代理 |

**能力矩阵（实测边界）**

| 能力 | 是否可做 | 证据 |
|:--|:--|:--|
| 读作者主页（bio / 粉丝数 / 置顶） | ✅ | `x.com/<handle>` `200`，`og:description` 与页内 JSON 可读 |
| 读近期推文原文（登录前 timeline） | ✅（有限） | profile 页内嵌 timeline JSON 含 `full_text` / `created_at_ms`；单页约 8–9 条**热门/近期**推文，**不是全量时间线** |
| 单条推文页取全文 | ⚠️ 部分 | 推文页 `200` 且 `og:title` 可核验作者，但正文由 JS 渲染，**长推文正文可能不在 HTML**（Jason Wei 的 benchmark 那条即如此） |
| follow / like / 发帖 | ❌ | 需登录态；🚫 令明确不许注册新账号、不许用未授权凭据 ⇒ **本轮 0 follow（未假装已 follow）** |
| 抓取节奏 | ⏱ 受限 | 本轮 6 个 handle + 4 条推文页，串行、相邻请求 ≥3s；脚本 `research/classic/x_fetch.py`（只读，仅标准库） |

**落地**：脚本 `research/classic/x_fetch.py`，原始结果落 `research/classic/x/<handle>.json`（6 个文件，共 15.3 KB，可入 git）。

### 待 follow 清单（请用户手动执行 · 6 个 handle 已在 X 侧二次核验）

| # | 人物 | handle | 主页链接 | X 侧核验（第四轮实测） | 为什么值得跟 |
|:--|:--|:--|:--|:--|:--|
| 1 | Tri Dao | `@tri_dao` | <https://x.com/tri_dao> | `200`，bio = `Asst. Prof @PrincetonCS, Chief Scientist @togethercompute…` | FlashAttention / Mamba 作者，kernel 与长上下文进展的第一手来源 |
| 2 | Albert Gu | `@_albertgu` | <https://x.com/_albertgu> | `200`，bio = `assistant prof @mldcmu. chief scientist @cartesia…` | SSM / Mamba 路线主推者，架构选择的判断值得跟踪 |
| 3 | Shunyu Yao | `@ShunyuYao12` | <https://x.com/ShunyuYao12> | `200`，bio = `Language agents` | ReAct / ToT 一作，现于 OpenAI 做 agent 产品，agent 方向言论密度高 |
| 4 | Edward J. Hu | `@edwardjhu` | <https://x.com/edwardjhu> | `200`，bio = `Head of AI Modeling @ Mercor / Ph.D. with Yoshua Bengio` | LoRA 一作，PEFT 与训练实践的第一手来源 |
| 5 | John Yang | `@jyangballin` | <https://x.com/jyangballin> | `200`，bio = `CS PhD @Stanford. Creator of @SWEbench…` | SWE-bench 二作 / SWE-agent 工程主力，harness 与 SWE 评测一手信息 |
| 6 | Jason Wei | `@_jasonwei` | <https://x.com/_jasonwei> | `200`，bio = `ai researcher @meta, past: openai, google` | CoT / 指令微调 / 涌现能力关键作者，reasoning 与训练配方判断密度高 |
| 7（**第五轮新增**） | Ilya Sutskever | `@ilyasut` | <https://x.com/ilyasut> | `200`，`name` = `Ilya Sutskever (@ilyasut) / X`，bio = `SSI @SSI` | seq2seq 一作 / GPT 系早期核心，长周期判断（scaling、superintelligence）权重极高 |
| 8（**第五轮新增**） | Richard S. Sutton | `@RichardSSutton` | <https://x.com/RichardSSutton> | `200`，bio 含 `UAlberta, amii, The Royal Society, Turing Award` | Dyna / TD 学习作者，「规划 vs 暴力算力」争论的源头人物，仍在高频发言 |
| 9（**第五轮新增**） | Haotian Liu | `@imhaotian` | <https://x.com/imhaotian> | `200`，bio = `@Meta Superintelligence Lab, prev. @xAI @grok imagine/omni/v` | LLaVA 一作，多模态指令数据与 VLM 训练一手信息 |
| 10（**第五轮新增**） | Chunyuan Li | `@ChunyuanLi` | <https://x.com/ChunyuanLi> | `200`，bio = `Agentic Vision @Google DeepMind | Previous: @xAI, @MSFTResearch` | LLaVA 二作，现做 agentic vision ⇒ VLM-agent 选题优先源 |


> 六个 handle 均来自其**本人主页**的 `href`（非搜索猜测），并在第四轮用 X 主页 `og:description` **二次核对 bio 与身份一致**。用户 follow 后请把状态改为 `已follow` 并写日期。

### 已核验言论台账（第四轮首获 · 原文 + 时间 + 链接）

| # | 人物 | 时间（UTC） | 原文（照抄） | 链接 | 用途 |
|:--|:--|:--|:--|:--|:--|
| V1 | Albert Gu `@_albertgu` | 2026-11-07 | "it's hilarious how many have taken the bitter lesson to mean just scaling up transformers. it's about scaling, but innovations in algorithmic primitives can lead to much more efficient scaling" | <https://x.com/_albertgu/status/2119206160410800219> | ✅ 已进日报 `voice_ready`（架构消融口径） |
| V2 | Tri Dao `@tri_dao` | 2026-10-28 | "Super interesting result: H-Net learns to dynamically tokenize variable names in coding data as separate tokens, and it scales much better on code compared to BPE" | <https://x.com/tri_dao/status/2115531348161028374> | ✅ 已进日报 `voice_ready`（代码语料 tokenizer） |
| V3 | Jason Wei `@_jasonwei` | 2026-11-10 22:31 | 起句 "Created a \"benchmark benchmark\": a frequency distribution of which benchmarks were reported by the frontier labs in 2026…"（**正文含转义引号，HTML 内嵌串被截断；推文页正文未渲染**） | <https://x.com/_jasonwei/status/2120283338640621826> | ❌ **未采用**：不满足「原文完整 + 可核验」，不冒充完整原文；仅在此登记，待下轮用其它入口取全文后再评估 |
| V4 | Richard S. Sutton `@RichardSSutton` | 2026-11-07 18:57 | "Brute force computation is not enough for intelligence. Clever new methods are needed. The science of AI is far from finished. IMHO" | <https://x.com/RichardSSutton/status/2119142310894334262> | 🕓 **本期未用（受「每期 ≤2 条」上限）**，原文已核验 ⇒ **下期 `voice_ready` 首选候选**；话题点 = 「暴力算力 vs 更聪明的方法」；风险 = 是**观点**且带 `IMHO`，🚫 不得写成结论 |


> ⚠️ 引用纪律：只有 **V1 / V2** 两条的原文在「profile 页内嵌 JSON」与「单条推文页 `og:title` 作者核对」两处一致，才进日报 `voice_ready`；**每条都附原链接与时间**，中文仅作翻译、不作转述。

**每个 handle 的原始快照**：`research/classic/x/<handle>.json`（字段 `bio` / `name` / `tweets[]`（`id` / `created_at` / `text` / `url`）/ `fetched_at`）。

**⚠️ 已知局限（如实记）**：① 登录前 profile 页只给 8–9 条热门/近期推文，**不能当完整时间线**用；② 正文含转义引号时可能被截断 ⇒ 只采用「两处一致」的条目；③ `syndication.twitter.com` 时间线接口本轮返回 **`429`**（未用，不绕过）；④ 不抓回复串（成本高、噪声大）。

---

## 三、发信记录（本线经典轨）

| 日期 | 对象 | 论文 | 邮箱来源 | 结果 |
|:--|:--|:--|:--|:--|
| 2026-11-11 11:36 | Tri Dao | `2205.14135` FlashAttention | 个人 CV PDF（2026 版） | `SENT OK`（见 `research/mail/发送记录.md`） |
| 2026-11-11 11:43 | Shunyu Yao | `2210.03629` ReAct | 本人主页 `mailto:` | `SENT OK`（`shunyuy@princeton.edu`） |
| 2026-11-11 11:43 | Haoxing Ren | `2311.00176` ChipNeMo · `2309.07544` VerilogEval | 公司站 `mailto:`（`info@agentrys.ai`，请转交） | `SENT OK`（公司公开信箱） |
| 2026-11-11 12:10 | Jason Wei | `2201.11903` Chain-of-Thought | 本人主页 `mailto:`（`jasonwei.net`） | `SENT OK`（`jason.weng.wei@gmail.com`，英文 165 词） |
| 2026-11-11 12:11 | Noah Shinn | `2303.11366` Reflexion | 本人主页明写邮箱（`noahshinn.com`） | `SENT OK`（`noahrshinn@gmail.com`，英文 153 词） |
| 2026-11-11 15:05（**第五轮**） | Kaiming He（何恺明） | `1512.03385` ResNet | 本人当前机构主页明文（`people.csail.mit.edu/kaiming/`，`200`） | `SENT OK`（`kaiming@mit.edu`，**中文 196 字**） |
| 2026-11-11 15:05（**第五轮**） | Haotian Liu | `2304.08485` LLaVA | 本人当前主页 `mailto:`（`haotian-liu.github.io`，`200`） | `SENT OK`（`liuhaotian.cn@gmail.com`，**中文 215 字**） |

| 2026-11-11 12:4x–13:0x（**第四轮**） | （本轮 **0 封**） | 新增经典 `2005.14165` / `2203.02155` / `2302.13971` | 逐个实测：`hugotouvron.github.io` `404` · `longouyang.github.io` `404` · `ashishvaswani.com` `000` · 未命中任何 `mailto:` | **不发信**（按令不猜邮箱）。今日累计 **5 封**（分属三轮，每轮 ≤3）；第四轮把额度留给「有可核验邮箱」的候选 —— 本轮没有合格的 ⇒ **宁缺勿凑** |

---

## 四、维护纪律

1. **一次一作者**：同一作者 / 同一论文 ≤1 封；同一机构 ≤2 封/天（`RESEARCH_MAIL_SPEC §3`）。
2. **邮箱取当前机构主页 / 本人 CV 的最新地址**，🚫 不用 5 年前 PDF 首页的旧邮箱（可能已失效或转他人）。
3. **X handle 只登记可访问页面读到的**，并在 X 可达时用 `og:description` 二次核对身份；`voice_ready` **必须有原文 + 原链接 + 时间**，两处不一致或正文不完整的一律不采用（如 V3）。
4. 状态四态：`待跟踪` → `已follow` → `已发信` → `已回复`；每次只前进，不跳级、不回退（回信内容另存 `research/mail/replies/`）。
5. 抓 X 一律走 `research/classic/x_fetch.py`（只读、串行、≥3s、单轮 ≤6 个 handle），原始结果落 `research/classic/x/`，**不做任何写操作**。
