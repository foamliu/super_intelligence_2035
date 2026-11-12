# 作者关系网（B 轨 · 滚动维护）

> 依据：`WATCH_RESEARCH_TASK.md` 用户令 2026-11-11（「找到这些作者的 X 账号并 follow，把这些顶级研究者的最新言论也作为给 news 投料的一部分」）。
> 字段：`姓名 · 机构 · 代表论文(1–2) · 邮箱(如公开) · 主页 · X 账号(@handle) · 状态(待跟踪/已follow/已发信/已回复) · 备注`
>
> 🔴 **找 X 的铁律（不猜）**：只登记**能从可访问页面读到**的 handle（作者本人主页 `href`，并用 X 页 `og:description` 二次核对身份）；**读不到 = 写「未找到 X」**。
> 🚫 不许猜 handle（猜错会 follow 到无关账号，比不 follow 更糟）。X.com 自 **2026-11-11 12:4x** 起经本机 Mihomo 代理**只读可达**；**follow 仍需登录态 ⇒ 未自动执行**（0 follow，未假装）。

**本轮快照**：累计 **54** 人（第八轮 +4：John Jumper / Igor Babuschkin / Danny Driess / Kimi Team；第九轮 +4：Team GLM / MiniMax / Karl Pertsch / Pete Florence；第十轮 +1：Kilian Lieret；第十一轮 +3：Jan Leike / Paul Christiano / Nisan Stiennon；**第十二轮 +3：Bill Peebles `@billpeeb` / Tim Brooks `@_tim_brooks` / Gerald Tesauro（未找到 X）**）｜已发信 **14**（Tri Dao · Shunyu Yao · Haoxing Ren · Jason Wei · Noah Shinn · Kaiming He · Haotian Liu · Karthik Narasimhan · Moo Jin Kim · Danny Driess · Pete Florence · Karl Pertsch · Jan Leike · **Nisan Stiennon**）｜X 已核验 **29**（`@tri_dao` / `@_albertgu` / `@ShunyuYao12` / `@edwardjhu` / `@jyangballin` / `@_jasonwei` / `@ilyasut` / `@RichardSSutton` / `@imhaotian` / `@ChunyuanLi` / `@karthik_r_n` / `@demishassabis` / `@koraykv` / `@OriolVinyalsML` / `@svlevine` / `@chelseabfinn` / `@moo_jin_kim` / `@ibab` / `@DannyDriess` / `@Kimi_Moonshot` / `@ZhipuAI` / `@MiniMax_AI` / `@KarlPertsch` / `@peteflorence` / `@KLieret` / `@janleike` / `@paulfchristiano` / **`@billpeeb`** / **`@_tim_brooks`**）｜X 未找到 **25**｜**X 可达（本机 Mihomo 7897；2026-11-12 12:0x 实测：需显式 `--proxy http://127.0.0.1:7897` —— 本 shell 环境未继承 `HTTPS_PROXY`，直连 `x.com` 返回 `000`、带代理返回 `200`；`x_fetch.py` 内部已默认走代理，2/2 `200`）**｜已 follow **0**（follow 需登录态 ⇒ 仍靠用户手动，见第二节）｜言论台账 **12 条**（V1–V12；本期 `voice_ready` 仍为 V2 / V4 两条，未新增可采用的完整原文）


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

### 29. Karthik Narasimhan

| 字段 | 内容 |
|:--|:--|
| 姓名 | Karthik Narasimhan（印度裔 ⇒ 信按英文写） |
| 机构 | Princeton University（Computer Science，助理教授）；此前 OpenAI · MIT CSAIL · Sierra |
| 代表论文 | GPT-1（arXiv 无；官方 PDF `language_understanding_paper.pdf`，**二作**）· ReAct（arXiv `2210.03629`，共同作者） |
| 邮箱 | **karthikn@princeton.edu**（来源：本人主页 `https://karthiknarasimhan.com/` 页内 `mailto:`，**percent-encoded**；`HTTP 200` / 14,706 B 实测 2026-11-11） |
| 主页 | <https://karthiknarasimhan.com/>（`200`；`www.` 同源同内容） |
| X 账号 | **@karthik_r_n**（核验：主页 `href="https://twitter.com/karthik_r_n"` + X 页 `og:description` = `Professor@Princeton, ex @OpenAI, @SierraPlatform, @MIT_CSAIL, @iitmadras.` **两处一致**；`HTTP 200`） |
| 状态 | **已发信**（2026-11-11 18:1x CST，第六轮 · 英文）· X 待 follow |
| 备注 | X bio 自列 `GPT, ReAct, Tree-of-Thoughts, SWE-Bench/Agent, TAU-bench, GEO` ⇒ **一个人横跨我们 harness 线的三条主线**（ReAct 式循环 / SWE 式判分 / τ-bench 式对话任务），是作者网里「覆盖面最宽」的节点；信里避开「复述摘要」，只问 harness 记账与失败模式。同合作圈注意：Shunyu Yao 今日 11:43 已发 1 封（同为 Princeton 圈）⇒ 按「同机构 ≤2 封/天」本日 Princeton 恰为 2 封，**不再追加**。 |

### 30. Demis Hassabis

| 字段 | 内容 |
|:--|:--|
| 姓名 | Demis Hassabis |
| 机构 | **Google DeepMind**（联合创始人 & CEO；Alphabet 首席科学家；2024 诺贝尔化学奖） |
| 代表论文 | DQN（Nature 2015，**末位作者**）· AlphaGo（Nature 2016）/ AlphaFold（Nature 2021，通讯） |
| 邮箱 | **未找到**（无公开个人邮箱；DeepMind 站点只有公司级联系表单 ⇒ 按纪律不发信） |
| 主页 | 未找到（无个人主页） |
| X 账号 | **@demishassabis**（核验：X 页 `og:description` = `Nobel Laureate. Co-Founder & Chair @GoogleDeepMind; Chief...`，与作者身份一致；`HTTP 200`） |
| 状态 | 待跟踪 · X 待 follow |
| 备注 | 言论密度极高（模型发布 / 世界模型 / 科学发现），是 `voice_ready` 的**高价值源**，但同时**商业宣传属性强** ⇒ 采用时必须区分「事实性发布」与「营销表述」，后者不标 `voice_ready`。 |

### 31. Koray Kavukcuoglu

| 字段 | 内容 |
|:--|:--|
| 姓名 | Koray Kavukcuoglu |
| 机构 | **Google DeepMind**（SVP）· Google 首席 AI 架构师 |
| 代表论文 | DQN（Nature 2015，**二作**）· 早期 CNN 特征学习（NIPS 2013） |
| 邮箱 | **未找到**（无公开个人邮箱） |
| 主页 | 未找到 |
| X 账号 | **@koraykv**（核验：X 页 `og:description` = `SVP, Google DeepMind / Chief AI Architect, Google.`；`HTTP 200`） |
| 状态 | 待跟踪 · X 待 follow |
| 备注 | DQN 的两个人（Hassabis / Kavukcuoglu）都在 X 上活跃，但**一作 Mnih 无公开账号/邮箱** ⇒ 深度 RL 这条线**无法从作者侧直接问到超参**，只能靠论文 + 社区复现。 |

### 32. Volodymyr Mnih

| 字段 | 内容 |
|:--|:--|
| 姓名 | Volodymyr Mnih |
| 机构 | Google DeepMind（DQN / A3C 一作） |
| 代表论文 | DQN（Nature 2015，**一作**）· Asynchronous Methods for Deep RL（A3C，arXiv `1602.01783`） |
| 邮箱 | **未找到**（无个人主页、无 `mailto:` 命中） |
| 主页 | 未找到 |
| X 账号 | **未找到 X**（未核验到本人账号 ⇒ 不登记） |
| 状态 | 待跟踪（缺可联系方式 ⇒ 本轮不发信） |
| 备注 | 这是「顶级作者但渠道缺失」的典型：🚫 不猜 `@volodymyrmnih` 之类 handle（X 上同名账号无法用 bio 核验身份）。 |

### 33. Alec Radford

| 字段 | 内容 |
|:--|:--|
| 姓名 | Alec Radford |
| 机构 | OpenAI（研究科学家；GPT-1 / GPT-2 / CLIP 一作） |
| 代表论文 | GPT-1（一作，无 arXiv）· GPT-2（一作，无 arXiv）· CLIP（arXiv `2103.00020`） |
| 邮箱 | **未找到**（无公开个人主页可核） |
| 主页 | **未找到**（`https://radford.ai/` 实测 `HTTP 200` 但仅 **114 B** ⇒ 占位/跳转页，**不采信为个人主页**） |
| X 账号 | **未找到 X**（`x.com/AlecRadford` 实测 `200`，但 `og:description` = `8 followers · 1 following. Joined Feb 2011.` —— **无任何身份信息、粉丝数异常** ⇒ 判定为同名占位 / 非本人，**不登记**） |
| 状态 | 待跟踪（本轮**不发信**） |
| 备注 | ⚠️ **本轮最好的「不猜」样本**：handle 拼写完全正确、页面也 `200`，但 bio 无法验证身份 ⇒ 按令**宁可不登记**（猜错 = follow 到无关账号，比不 follow 更糟）。原始快照 `research/classic/x/AlecRadford.json`。 |

### 34. Jared Kaplan

| 字段 | 内容 |
|:--|:--|
| 姓名 | Jared Kaplan |
| 机构 | **Anthropic**（联合创始人 & 首席科学官）；Scaling Laws 发表时 Johns Hopkins University 物理系 |
| 代表论文 | Scaling Laws for Neural Language Models（arXiv `2001.08361`，**一作**）· 后续 Anthropic 系列（多为机构署名） |
| 邮箱 | **未找到**（`https://jaredkaplan.net/` 实测 `200` 但仅 **114 B** ⇒ 占位页；Anthropic 无个人公开邮箱 ⇒ 不发信） |
| 主页 | 未找到 |
| X 账号 | **未找到 X**（本轮未核验到本人账号；🚫 不猜） |
| 状态 | 待跟踪 |
| 备注 | 他这条线的「可问价值」很高（2B 的 token 预算到底该按哪条幂律选点），但**渠道缺失** ⇒ 改为在日报里把「Kaplan vs Chinchilla 口径差异」写成给 pretrain 的可执行实验设计（见当日 18:00 增量建议）。 |

---

### 35. David Silver

| 字段 | 内容 |
|:--|:--|
| 姓名 | David Silver |
| 机构 | **Google DeepMind**（AlphaGo / AlphaGo Zero 一作；DQN 三作） |
| 代表论文 | AlphaGo（Nature 2016）· AlphaGo Zero（Nature 2017） |
| 邮箱 | **未找到**（个人站 `https://www.davidsilver.uk/` 实测 `HTTP 200` / 96,600 B，页内无 `mailto:`；无当前机构个人页可核） |
| 主页 | <https://www.davidsilver.uk/>（实测 `200`；只有博客/文章，无联系方式区块） |
| X 账号 | **未找到 X**（个人站无 x/twitter 链接；🚫 未猜 `@davidsilver` 之类常见 handle） |
| 状态 | 待跟踪（渠道缺失 ⇒ 不发信） |
| 备注 | AlphaGo 系两篇的**共同一作**，是「搜索预算 + 自我对弈」这条线最直接的作者；但其公开表达主要在论文与访谈，X 不可核 ⇒ 只作为**经典论文作者**建档，不作为言论源。 |

### 36. Oriol Vinyals

| 字段 | 内容 |
|:--|:--|
| 姓名 | Oriol Vinyals |
| 机构 | **Discovery Loop**（联合创始人 & CTO，X bio 自述）· **224 Ventures** 合伙人；发表时 Google DeepMind VP、Gemini TL（1.0–4.0） |
| 代表论文 | Sequence to Sequence Learning（arXiv `1409.3215`，二作）· Gemini（arXiv `2312.11805`，Gemini TL）· AlphaStar（X bio 自述参与） |
| 邮箱 | **未找到**（`research.google/people/oriolvinyals/` 实测 `404`；无个人主页可核 ⇒ 不发信） |
| 主页 | 未找到（同上） |
| X 账号 | **@OriolVinyalsML**（`200`；bio = `Co-founder & CTO of Discovery Loop; Partner, 224 Ventures / Past: Google DeepMind VP, Gemini TL (1.0 to 4.0), Alpha{Fold,Star,Code}, seq2seq, distillation` ⇒ 与 seq2seq / Gemini 作者身份一致） |
| 状态 | 待跟踪 · X 待 follow |
| 备注 | 一人同时覆盖必读清单第 2 组（seq2seq）与第 8 组（Gemini/AlphaStar）⇒ **优先级最高的言论源之一**；但已离开 Google，近期推文多为创业相关，引用时须区分「个人观点」与「Gemini 官方口径」。 |

### 37. Sergey Levine

| 字段 | 内容 |
|:--|:--|
| 姓名 | Sergey Levine |
| 机构 | **UC Berkeley**（EECS 副教授）· **Physical Intelligence** 联合创始人 |
| 代表论文 | OpenVLA（arXiv `2406.09246`，作者列表第 16 位，arXiv API 18 人全量核对）· RT 系列 / 机器人学习 |
| 邮箱 | **未找到**（个人页 `people.eecs.berkeley.edu/~svlevine/` 实测 `200` / 12,481 B，`Email:` 后是 `toggle_vis('email')` 的**招生说明**，无实际地址；页面不公开邮箱） |
| 主页 | <https://people.eecs.berkeley.edu/~svlevine/>（实测 `200`） |
| X 账号 | **@svlevine**（`200`；bio = `Associate Professor at UC Berkeley / Co-founder, Physical Intelligence`，与身份一致） |
| 状态 | 待跟踪 · X 待 follow（无邮箱 ⇒ 不发信） |
| 备注 | OpenVLA 的资深作者之一，言论集中在 VLA / 机器人策略；对我们「动作接口 + 评测协议」有参考价值，但**不套用机器人结论到 EDA**。 |

### 38. Chelsea Finn

| 字段 | 内容 |
|:--|:--|
| 姓名 | Chelsea Finn |
| 机构 | **Stanford University**（CS & EE 助理教授）· **Physical Intelligence** 联合创始人 |
| 代表论文 | OpenVLA（arXiv `2406.09246`，作者列表第 18 位）· 元学习 / 机器人学习系列 |
| 邮箱 | **未找到**（`https://cbfinn.github.io/` 实测 `200` / 31,521 B，仅有课程助教邮箱 `cs330-staff-aut2324@cs.stanford.edu`，**非本人**；`profiles.stanford.edu/chelsea-finn` 无公开邮箱 ⇒ 不猜） |
| 主页 | <https://cbfinn.github.io/>（实测 `200`） |
| X 账号 | **@chelseabfinn**（`200`；bio = `Asst Prof of CS & EE @Stanford / Co-founder of Physical Intelligence @physical_int / PhD from @Berkeley_EECS…`） |
| 状态 | 待跟踪 · X 待 follow（无邮箱 ⇒ 不发信） |
| 备注 | 言论密度高且偏方法论（VLA、long-context agent、value classifier）；已核验 V6（2026-10-24，generative value classifiers）⇒ **下期 `voice_ready` 候选**。 |

### 39. Moo Jin Kim

| 字段 | 内容 |
|:--|:--|
| 姓名 | Moo Jin Kim（韩裔，英文名 ⇒ 信按英文写） |
| 机构 | **OpenAI**（research scientist，主页自述）· Stanford CS PhD（导师 Chelsea Finn / Percy Liang） |
| 代表论文 | OpenVLA（arXiv `2406.09246`，**一作**）· OpenVLA-OFT / Cosmos Policy（主页自述） |
| 邮箱 | **moojink@cs.stanford.edu**（来源：本人主页 `https://moojink.github.io/` 页内防爬写法 `moojink at cs dot stanford dot edu`，`HTTP 200` / 33,139 B 实测，按原样还原） |
| 主页 | <https://moojink.github.io/>（实测 `200`） |
| X 账号 | **@moo_jin_kim**（`200`；bio = `Research @OpenAI | CS PhD @StanfordAILab`，与身份一致） |
| 状态 | **已发信**（2026-11-11 21:04 CST，B 轨第七轮；英文 195 词）· X 待 follow |
| 备注 | ⚠️ 主页自述已入职 OpenAI，Stanford 邮箱可能停用 ⇒ 若退信记「通道失效」，**不猜其他地址**。信的内容是「双塔融合 vs 数据多样性」「逐维分桶 vs 文本序列化」两个取舍，直接回填 vision / harness 的预注册。 |

---

### 40. John Jumper

| 字段 | 内容 |
|:--|:--|
| 姓名 | John Jumper（美国人 ⇒ 信按英文写） |
| 机构 | **Google DeepMind**（AlphaFold 一作 / 通讯；2024 诺贝尔化学奖共同得主） |
| 代表论文 | AlphaFold（Nature 2021，DOI `10.1038/s41586-021-03819-2`，一作） |
| 邮箱 | **未找到**（DeepMind 不公开个人邮箱；无本人主页可核） |
| 主页 | **未找到本人页**（机构页 <https://deepmind.google/technologies/alphafold/> 为项目页） |
| X 账号 | **未找到 X**（`x.com/JohnJumper` 实测 `200` 但 `og:description` = `19 followers · 7 following. Joined Dec 2008`、无 bio ⇒ **身份不可证，拒绝登记**，🚫 不猜） |
| 状态 | 待跟踪（无邮箱、无可证 X ⇒ 本轮不发信、不 follow） |
| 备注 | AlphaFold 的「把领域先验编码进结构」是 vision 线几何通道的参照；但**公开联系通道缺失** ⇒ 只作经典条目作者，不作本线沟通对象。 |

### 41. Igor Babuschkin

| 字段 | 内容 |
|:--|:--|
| 姓名 | Igor Babuschkin（德国出生 ⇒ 信按英文写） |
| 机构 | **River AI（CEO & 联合创始人）**· 曾任 xAI（Research & Engineering）· AlphaStar 发表时在 DeepMind |
| 代表论文 | AlphaStar（Nature 2019，DOI `10.1038/s41586-019-1724-z`，二作） |
| 邮箱 | **未找到**（无公开个人页/邮箱） |
| 主页 | **未找到** |
| X 账号 | **@ibab**（`x.com/ibab` `200`；bio = `CEO & Co-Founder @river_ai_inc. Previously @xAI, Research & Engineering`，与 AlphaStar 二作身份一致） |
| 状态 | 待跟踪 · X 待 follow（无邮箱 ⇒ 不发信） |
| 备注 | AlphaStar 联盟式 RL 的工程负责人之一；其言论对「多智能体训练/大规模 RL 工程」有参考价值，但**当前创业方向与本线偏离** ⇒ 只跟踪、不发信。 |

### 42. Danny Driess

| 字段 | 内容 |
|:--|:--|
| 姓名 | Danny Driess（德国人 ⇒ 信按英文写） |
| 机构 | **Physical Intelligence**（Research Scientist）· 曾任 Google DeepMind（Gemini × robotics） |
| 代表论文 | π0（arXiv `2410.24164`，第三作）· PaLM-E（ICML 2023，一作） |
| 邮箱 | **danny.driess@gmail.com**（来源：本人主页 `https://dannydriess.github.io/` 页内防爬写法 `danny dot driess at gmail dot com`，`HTTP 200` / 29,043 B 实测，按原样还原） |
| 主页 | <https://dannydriess.github.io/>（实测 `200`） |
| X 账号 | **@DannyDriess**（来源：本人主页 `href="https://twitter.com/DannyDriess"`；`x.com/DannyDriess` `200`，`<title>Danny Driess (@DannyDriess) / X</title>`） |
| 状态 | **已发信**（2026-11-12 00:07 CST，B 轨第八轮；英文 191 词）· X 待 follow |
| 备注 | 信问两个取舍：① 低数据域内（数万张图）flow matching 动作头 vs 离散 token 化，哪个更稳；② 动作块（action chunk）长度与异构动作空间（不同 arity 的 tool call）如何兼容。答复直接回填 zhulong 的动作接口消融。 |

### 43. Kimi Team（Moonshot AI）

| 字段 | 内容 |
|:--|:--|
| 姓名 | **Kimi Team / Moonshot AI（团队署名，无单一作者）**；作者列表中含 **Jianlin Su**（见主表 #20） |
| 机构 | Moonshot AI（月之暗面，北京） |
| 代表论文 | Kimi k1.5（arXiv `2501.12599`，团队署名） |
| 邮箱 | **未找到**（官方站未给研究联系邮箱；🚫 不用客服/商务邮箱冒充作者） |
| 主页 | <https://www.kimi.com>（产品站；<https://www.moonshot.cn> 机构站） |
| X 账号 | **@Kimi_Moonshot**（`200`；`<title>Kimi.ai (@Kimi_Moonshot) / X</title>`，官方账号，非个人） |
| 状态 | 待跟踪 · X 待 follow（团队账号只作发布源，不发信） |
| 备注 | long2short 与「RL 作为新 scaling 轴」是 zhulong 的直接参照；**团队账号的言论只作公司口径**，引用须标「Moonshot 官方账号」。 |

### 44. Team GLM（智谱 AI · 团队署名）

| 字段 | 内容 |
|:--|:--|
| 姓名 | Team GLM（GLM-4 论文的团队署名，共 **59** 位；一作 Aohan Zeng，含 Jie Tang / Juanzi Li / Minlie Huang / Yuxiao Dong） |
| 机构 | 智谱 AI（Zhipu AI / 北京）· 部分作者挂清华大学 |
| 代表论文 | ChatGLM / GLM-4（arXiv `2406.12793`，团队署名）· GLM-130B |
| 邮箱 | **未找到**（官网只有商务/客服入口；🚫 不用客服邮箱冒充研究作者） |
| 主页 | <https://github.com/THUDM>（GLM 系列代码与模型卡；`200` 未逐页核验） |
| X 账号 | **@ZhipuAI**（**官方机构账号**，非个人；核验：<https://x.com/ZhipuAI> `200`，`<title>` = `ZhipuAI by BigModel (@ZhipuAI) / X`，`og:description` = `全部自研GLM模型架构`） |
| 状态 | 待跟踪 · X 待 follow（机构号） |
| 备注 | 机构号主要发产品与发布信息，**言论价值低于个人号**；若要请教 GLM-4 的中文配比细节，需先找到一作 Aohan Zeng 的当前主页/邮箱（本轮未找到公开研究邮箱 ⇒ **不发信**）。 |

### 45. MiniMax（团队署名）

| 字段 | 内容 |
|:--|:--|
| 姓名 | MiniMax（团队署名，**按字母序**：Aonian Li · Bangwei Gong · Bo Yang …，共 **90** 位） |
| 机构 | MiniMax（上海） |
| 代表论文 | MiniMax-01（arXiv `2501.08313`，团队署名）· MiniMax-VL-01（同报告） |
| 邮箱 | **未找到**（🚫 不用客服/商务邮箱） |
| 主页 | <https://github.com/MiniMax-AI>（代码与模型开源入口） |
| X 账号 | **@MiniMax_AI**（**官方机构账号**；核验：<https://x.com/MiniMax_AI> `200`，`<title>` = `MiniMax (official) (@MiniMax_AI) / X`，bio 指向 `Code: @MiniMax_Code`） |
| 状态 | 待跟踪 · X 待 follow（机构号） |
| 备注 | 关注点：线性注意力 + MoE 的长上下文工程口径；个人作者未逐一建档（90 人字母序，无声明的通讯作者）。 |

### 46. Karl Pertsch

| 字段 | 内容 |
|:--|:--|
| 姓名 | Karl Pertsch（德国人 ⇒ 信按英文写） |
| 机构 | **Physical Intelligence**（member of technical staff，主页自述「training robot foundation models」）；前 UC Berkeley / Stanford 博后 |
| 代表论文 | Octo（arXiv `2405.12213`，三作 / 共同负责人，RSS 2024）· RT-2（arXiv `2307.15818`，作者之一） |
| 邮箱 | **karl.pertsch@gmail.com**（来源：本人主页 `<a href="mailto:karl.pertsch@gmail.com">`，`HTTP 200` / 64,903 B 实测） |
| 主页 | <https://kpertsch.github.io>（`200` / 64,903 B） |
| X 账号 | **@KarlPertsch**（核验：主页 `href="https://twitter.com/KarlPertsch"`；<https://x.com/karlpertsch> `200`，`<title>` = `Karl Pertsch (@KarlPertsch) / X`，bio = `Robot Foundation Models @physical_int`） |
| 状态 | **已发信**（2026-11-12 06:05 CST，英文 191 词，经典论文口径；见 `research/mail/发送记录.md`）· X 待 follow |
| 备注 | **一份关系覆盖两条必读清单条目**（Octo + RT-2）；⚠️ 与 Danny Driess 同属 Physical Intelligence ⇒ 2026-11-12 该公司**当日 2 封**（00:07 Danny + 06:05 本封）**已达「同机构 ≤2 封/天」上限**，今日不再向 PI 发信。 |

### 47. Pete Florence

| 字段 | 内容 |
|:--|:--|
| 姓名 | Pete Florence（美国人 ⇒ 信按英文写） |
| 机构 | **Generalist AI**（联合创始人 & CEO）；前 Google DeepMind（Senior Research Scientist）；MIT CS PhD（导师 Russ Tedrake） |
| 代表论文 | RT-2（arXiv `2307.15818`，54 位作者中第 13 位，核心作者之一）· RT-1 系列 · kPAM |
| 邮箱 | **pete.florence@gmail.com**（来源：本人主页 `Email: <code>pete dot florence at gmail dot com</code>` 的防爬写法还原；`HTTP 200` / 47,238 B 实测） |
| 主页 | <https://www.peteflorence.com>（`200` / 47,238 B） |
| X 账号 | **@peteflorence**（核验：主页 `href="https://x.com/peteflorence"`；<https://x.com/peteflorence> `200`，`<title>` = `Pete Florence (@peteflorence) / X`，bio = `Co-Founder &amp; CEO @GeneralistAI`） |
| 状态 | **已发信**（2026-11-12 03:1x CST，英文，经典论文口径；见 `research/mail/发送记录.md`） |
| 备注 | RT-2 的「**动作 = 文本 token**」正是我们「agent 用文本 tool call 调 EDA 工具」的机器人版先例 ⇒ 问题集中在「离散分桶的精度损失」与「网页数据 vs 域内轨迹的混比」。 |

### 48. Kilian Lieret

| 字段 | 内容 |
|:--|:--|
| 姓名 | Kilian Lieret（德国人 ⇒ 信按英文写） |
| 机构 | **Meta Superintelligence**（X bio 自述「Meta Superintelligence, prev. Princeton」）；SWE-bench / SWE-agent 团队核心工程维护者 |
| 代表论文 | SWE-agent（arXiv `2405.15793`，第 4 作者）· SWE-bench 多语/多模态版（维护者，见其 bio） |
| 邮箱 | **未找到**（`klieret.github.io` 实测 `HTTP 404`；X bio 未挂邮箱 ⇒ 按纪律不写猜测地址） |
| 主页 | 未找到（`klieret.github.io` 404，2026-11-12 实测） |
| X 账号 | **@KLieret**（核验：① 来源 = John Yang 推文原文「Follow @KLieret for leaderboard updates」（`https://x.com/jyangballin/status/2115494796064403620`）；② <https://x.com/KLieret> 实测 `200`，`og:title` = `Kilian Lieret (@KLieret) on X`，`og:description` = `Meta Superintelligence, prev. Princeton. SWE-bench multilingual/multimodal, (mini-)SWE-agent, SWE-smith, CodeClash, ProgramBench, SWE-sweep` ⇒ 身份自证） |
| 状态 | **待跟踪**（X 待 follow；无公开邮箱 ⇒ 不发信） |
| 备注 | **harness 线的「榜单更新频率」信号源**：他负责 SWE-bench 系榜单维护，推文里常带「新模型进榜/新变体」的即时信息 ⇒ 这是「评测基准本身在变」的一手消息，比论文更早。⚠️ 已离开 Princeton 去 Meta，院校邮箱不可靠 ⇒ 只跟踪不写信。 |

### 49. Jan Leike

| 字段 | 内容 |
|:--|:--|
| 姓名 | Jan Leike（德国人 ⇒ 信按英文写） |
| 机构 | **Anthropic**（alignment / superalignment 方向；主页自述与主页 `publications.html` 可核）· 论文发表时为 OpenAI |
| 代表论文 | Deep RL from human preferences（arXiv `1706.03741`，二作）· Learning to summarize from human feedback（arXiv `2009.01325`，作者）· InstructGPT 系工作（OpenAI 期间） |
| 邮箱 | **jan@anthropic.com**（来源：本人主页 <https://jan.leike.name/> 的 `<a href="mailto:Jan%20Leike%20%3Cjan%40anthropic.com%3E">`，2026-11-12 09:0x 实测 `HTTP 200` / 6,411 B；**非 2017 年论文 PDF 旧地址**） |
| 主页 | <https://jan.leike.name/>（`200` / 6,411 B）· 博客 <https://aligned.substack.com> |
| X 账号 | **@janleike**（双证：① 主页 `href="https://twitter.com/janleike"` 且链接文字 `@janleike`；② <https://x.com/janleike> `200`，`og:title` = `Jan Leike (@janleike) on X`。⚠️ 该页 `og:description` 本轮未渲染 ⇒ bio 未取到，只登记 handle，不写 bio） |
| 状态 | **已发信**（2026-11-12 09:04 CST，经典论文请教信第十三封；英文 199 词）· X 待 follow |
| 备注 | **RLHF 这条线的「前史」作者**：2017 年偏好奖励 → 2020 年摘要偏好 → InstructGPT。信问三件可回填的事：① 工具调用短 episode（10–30 步）下，学到的奖励要多少标注密度才能胜过手写可验证奖励；② 小规模下 RM 瓶颈是容量还是标签噪声、最先出现的 reward hacking 形态；③ tie / 标注分歧如何聚合。⚠️ 与 Paul Christiano 同一篇论文 ⇒ **同篇论文本轮只发一封**（发给可核验邮箱的 Leike）。 |

### 50. Paul Christiano

| 字段 | 内容 |
|:--|:--|
| 姓名 | Paul Christiano |
| 机构 | **Alignment Research Center（ARC）**（Founder & Director；X bio 自述「Former Head of Safety @ CAISI. Previously led alignment at OpenAI.」） |
| 代表论文 | Deep RL from human preferences（arXiv `1706.03741`，一作）· Learning to summarize from human feedback（arXiv `2009.01325`，末位） |
| 邮箱 | **未找到**（个人站 <https://paulfchristiano.com/> 实测 `HTTP 200` / 57,044 B，但页内**无 `mailto:`**；只有 Google Scholar 链接 ⇒ 按纪律不写猜测地址） |
| 主页 | <https://paulfchristiano.com/>（`200` / 57,044 B） |
| X 账号 | **@paulfchristiano**（核验：<https://x.com/paulfchristiano> `200`，`og:title` = `Paul Christiano (@paulfchristiano) on X`，`og:description` = `Founder & Director of the Alignment Research Center. Former Head of Safety @ CAISI. Previously led alignment at OpenAI. Views my own.` ⇒ 身份自证。⚠️ 其个人站未挂 X 链接，来源为 X 页自证，非主页 `href`） |
| 状态 | **待跟踪**（X 待 follow；无公开邮箱 ⇒ 不发信） |
| 备注 | RLHF 思路的源头作者，但其公开表达偏 alignment 理论；对我们更直接的价值是**「奖励从哪来」的判断**，适合长期跟踪而非立刻请教（同篇论文已向 Leike 发信，🚫 不重复打扰）。 |

### 51. Nisan Stiennon

| 字段 | 内容 |
|:--|:--|
| 姓名 | Nisan Stiennon |
| 机构 | 未核验（个人站未写当前机构） |
| 代表论文 | Learning to summarize from human feedback（arXiv `2009.01325`，一作） |
| 邮箱 | **nisan+web@stiennon.com**（来源：本人站 <https://nisanstiennon.com/> 的 `<a href="mailto:nisan+web@stiennon.com">`，`HTTP 200` / 5,575 B 实测；**非 2020 年论文 PDF 旧地址**） |
| 主页 | <https://nisanstiennon.com/>（`200` / 5,575 B；`www.` 同页同尺寸） |
| X 账号 | **未找到 X**（`x.com/nisanstiennon` 实测 **`404`**，`og:title` = `User Profile Not Found - X｜404 Error` ⇒ 按令**不猜替代 handle、不登记**） |
| 状态 | **已发信**（2026-11-12 12:04 CST，B 轨第十二轮；英文；⚠️ 实测 212 词，超 ≤200 规格 12 词，已如实记账） |
| 备注 | 若 18:00 轮要发「偏好数据质量」方向的信，他是首选（RLHF 摘要范式的直接作者）；问题应聚焦**偏好数据集的构建与一致率**，而不是摘要任务本身。 |

---

### 52. Bill Peebles（William Peebles）

| 字段 | 内容 |
|:--|:--|
| 姓名 | Bill Peebles（William Peebles） |
| 机构 | OpenAI（X bio 自述 `head of sora @openai`） |
| 代表论文 | Video generation models as world simulators（Sora 技术报告，2024，**无 arXiv**）· Scalable Diffusion Models with Transformers（DiT，2022） |
| 邮箱 | **未找到**（本轮未核个人主页；🚫 不猜） |
| 主页 | 未核验 |
| X 账号 | **@billpeeb**（核验：`x_fetch.py` 实测 `200`，`<title>` = `Bill Peebles (@billpeeb) / X`，bio = `head of sora @openai 🇺🇸🇺🇸🇺🇸`） |
| 状态 | **待跟踪**（X 待 follow；无公开邮箱 ⇒ 不发信） |
| 备注 | Sora 负责人 ⇒ 视频生成 / 世界模型路线的**一手判断源**；⚠️ 官方页本机 403，其论文细节**只能等新发布或访谈**，🚫 不据传闻写。 |

### 53. Tim Brooks

| 字段 | 内容 |
|:--|:--|
| 姓名 | Tim Brooks |
| 机构 | Meta（X bio 自述 `superintelligence @ Meta`）· 前 OpenAI（Sora 共同负责人） |
| 代表论文 | Video generation models as world simulators（Sora 技术报告，2024，**无 arXiv**）· InstructPix2Pix（2022） |
| 邮箱 | **未找到**（本轮未核个人主页；🚫 不猜） |
| 主页 | 未核验 |
| X 账号 | **@_tim_brooks**（核验：`200`，`<title>` = `Tim Brooks (@_tim_brooks) / X`，bio = `superintelligence @ Meta`） |
| 状态 | **待跟踪**（X 待 follow；无公开邮箱 ⇒ 不发信） |
| 备注 | **已离开 OpenAI 转 Meta** ⇒ 任何涉 Sora 的发言均为「前负责人」视角，引用须标时间与身份变化，🚫 不可当成 OpenAI 现行口径。 |

### 54. Gerald Tesauro

| 字段 | 内容 |
|:--|:--|
| 姓名 | Gerald Tesauro |
| 机构 | IBM（论文发表时为 IBM Thomas J. Watson Research Center；**当前职位未核验**） |
| 代表论文 | Temporal Difference Learning and TD-Gammon（CACM 1995，**独著**）· TD-Gammon, a Self-Teaching Backgammon Program（Neural Computation 1994） |
| 邮箱 | **未找到**（旧主页 `research.ibm.com/people/t/tesauro/` 实测 **`308`** → 重定向到通用 `research.ibm.com/people`，页面无 `mailto:`） |
| 主页 | 未核验（同上，已重定向到通用页） |
| X 账号 | **未找到 X**（无可核个人页读到 handle ⇒ 按令不猜、不登记） |
| 状态 | **待跟踪**（不发信） |
| 备注 | 1995 年论文，PDF 上的邮箱已过 30 年 ⇒ 按令**必须**用当前机构主页邮箱，本轮拿不到 ⇒ 不发信；其方法论价值已通过 #45 条目落库。 |

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
| 7（**第十一轮 09:0x**） | 显式带代理：`https://x.com` / `https://x.com/ShunyuYao12` / `https://api.ipify.org` | **`200` / 0.86s** · **`200` / 0.76s** · 出口 **`178.249.213.185`** ⇒ 代理仍在线（`x.com` 可达，follow 仍需登录态） |

**能力矩阵（实测边界）**

| 能力 | 是否可做 | 证据 |
|:--|:--|:--|
| 读作者主页（bio / 粉丝数 / 置顶） | ✅ | `x.com/<handle>` `200`，`og:description` 与页内 JSON 可读 |
| 读近期推文原文（登录前 timeline） | ✅（有限） | profile 页内嵌 timeline JSON 含 `full_text` / `created_at_ms`；单页约 8–9 条**热门/近期**推文，**不是全量时间线** |
| 单条推文页取全文 | ⚠️ 部分 | 推文页 `200` 且 `og:title` 可核验作者，但正文由 JS 渲染，**长推文正文可能不在 HTML**（Jason Wei 的 benchmark 那条即如此） |
| follow / like / 发帖 | ❌ | 需登录态；🚫 令明确不许注册新账号、不许用未授权凭据 ⇒ **本轮 0 follow（未假装已 follow）** |
| 抓取节奏 | ⏱ 受限 | 本轮 6 个 handle + 4 条推文页，串行、相邻请求 ≥3s；脚本 `research/classic/x_fetch.py`（只读，仅标准库） |

**落地**：脚本 `research/classic/x_fetch.py`，原始结果落 `research/classic/x/<handle>.json`（6 个文件，共 15.3 KB，可入 git）。

### 待 follow 清单（请用户手动执行 · 30 个 handle 已在 X 侧二次核验）

| # | 人物 | handle | 主页链接 | X 侧核验（2026-11-12 实测） | 为什么值得跟 |
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
| 11（**第六轮新增**） | Karthik Narasimhan | `@karthik_r_n` | <https://x.com/karthik_r_n> | `200`，bio = `Professor@Princeton, ex @OpenAI, @SierraPlatform, @MIT_CSAIL, @iitmadras. GPT, ReAct, Tree-of-Thoughts, SWE-Bench/Agent, TAU-bench, GEO` | GPT-1 二作 / ReAct 共同作者 ⇒ **harness 三条主线（循环 / 判分 / 对话任务）汇于一人**，言论价值最高 |
| 12（**第六轮新增**） | Demis Hassabis | `@demishassabis` | <https://x.com/demishassabis> | `200`，bio = `Nobel Laureate. Co-Founder & Chair @GoogleDeepMind; Chief Scientist of Alphabet. Founder & CEO @IsomorphicLabs` | DQN 末位 / AlphaGo / AlphaFold 通讯 ⇒ DeepMind 家族一手发布源（**须区分事实与营销**） |
| 13（**第六轮新增**） | Koray Kavukcuoglu | `@koraykv` | <https://x.com/koraykv> | `200`，bio = `SVP, Google DeepMind / Chief AI Architect, Google.` | DQN 二作 ⇒ 深度 RL 与 Gemini 系架构的一手来源 |
| 14（**第七轮新增**） | Oriol Vinyals | `@OriolVinyalsML` | <https://x.com/OriolVinyalsML> | `200`，bio = `Co-founder & CTO of Discovery Loop… Past: Google DeepMind VP, Gemini TL (1.0 to 4.0), Alpha{Fold,Star,Code}, seq2seq…` | seq2seq 二作 + Gemini TL ⇒ 必读清单第 2 / 8 组交叉点 |
| 15（**第七轮新增**） | Sergey Levine | `@svlevine` | <https://x.com/svlevine> | `200`，bio = `Associate Professor at UC Berkeley / Co-founder, Physical Intelligence` | OpenVLA 资深作者 ⇒ VLA / 动作接口的一手来源 |
| 16（**第七轮新增**） | Chelsea Finn | `@chelseabfinn` | <https://x.com/chelseabfinn> | `200`，bio = `Asst Prof of CS & EE @Stanford / Co-founder of Physical Intelligence…` | OpenVLA 末位 + 元学习 ⇒ VLA 与 long-context agent 方法言论 |
| 17（**第七轮新增**） | Moo Jin Kim | `@moo_jin_kim` | <https://x.com/moo_jin_kim> | `200`，bio = `Research @OpenAI | CS PhD @StanfordAILab` | OpenVLA 一作 ⇒ 该配方细节的最直接作者（今日已发信） |
| 18（**第八轮新增**） | Igor Babuschkin | `@ibab` | <https://x.com/ibab> | `200`，bio = `CEO & Co-Founder @river_ai_inc. Previously @xAI, Research & Engineering` | AlphaStar 二作 ⇒ 大规模多智能体 RL 的工程一手经验 |
| 19（**第八轮新增**） | Danny Driess | `@DannyDriess` | <https://x.com/DannyDriess> | `200`，`<title>Danny Driess (@DannyDriess) / X</title>`；handle 源自主页 `href` | π0 三作 / PaLM-E 一作 ⇒ VLA 与 flow matching 动作接口一手信息 |
| 20（**第八轮新增**） | Kimi Team（Moonshot AI） | `@Kimi_Moonshot` | <https://x.com/Kimi_Moonshot> | `200`，`<title>Kimi.ai (@Kimi_Moonshot) / X</title>`（官方账号） | Kimi k1.5 团队 ⇒ long2short / RL scaling 的官方发布源 |
| 21（**第八轮新增**） | Physical Intelligence | `@physical_int` | <https://x.com/physical_int> | `200`，bio = `Physical Intelligence (Pi), bringing AI into the physical world.` | π0 / OpenVLA 系团队账号 ⇒ VLA 模型与数据发布的一手源 |
| 22（**第九轮新增**） | Zhipu AI（智谱） | `@ZhipuAI` | <https://x.com/ZhipuAI> | `200`，`<title>ZhipuAI by BigModel (@ZhipuAI) / X</title>`，bio = `全部自研GLM模型架构`（**官方机构号**） | GLM-4 团队 ⇒ 中文系开源模型发布与配比口径的官方源（机构号，营销多，须筛） |
| 23（**第九轮新增**） | MiniMax | `@MiniMax_AI` | <https://x.com/MiniMax_AI> | `200`，`<title>MiniMax (official) (@MiniMax_AI) / X</title>`，bio 含 `Code: @MiniMax_Code`（**官方机构号**） | MiniMax-01 团队 ⇒ 线性注意力 / 长上下文工程口径的官方源 |
| 24（**第九轮新增**） | Karl Pertsch | `@KarlPertsch` | <https://x.com/KarlPertsch> | `200`，`<title>Karl Pertsch (@KarlPertsch) / X</title>`，bio = `Robot Foundation Models @physical_int`；handle 源自主页 `href` | Octo 三作 + RT-2 作者 ⇒ 通用机器人策略与「新动作空间低成本适配」一手信息 |
| 25（**第十轮新增**） | Kilian Lieret | `@KLieret` | <https://x.com/KLieret> | `200`，`og:title` = `Kilian Lieret (@KLieret) on X`，`og:description` = `Meta Superintelligence, prev. Princeton. SWE-bench multilingual/multimodal, (mini-)SWE-agent, SWE-smith, CodeClash, ProgramBench, SWE-sweep` | SWE-agent 第 4 作者 + SWE-bench 系榜单维护者 ⇒ 「基准本身在变」的最早信号源 |
| 25（**第九轮新增**） | Pete Florence | `@peteflorence` | <https://x.com/peteflorence> | `200`，`<title>Pete Florence (@peteflorence) / X</title>`，bio = `Co-Founder &amp; CEO @GeneralistAI`；handle 源自主页 `href` | RT-2 核心作者 ⇒ 「动作＝文本 token」与 VLA 泛化的第一手判断 |
| 27（**第十一轮新增**） | Jan Leike | `@janleike` | <https://x.com/janleike> | `200`，`og:title` = `Jan Leike (@janleike) on X`；handle 源自主页 `href="https://twitter.com/janleike"`（⚠️ `og:description` 本轮未渲染，bio 空缺如实记） | RLHF 前史（2017 偏好奖励 / 2020 摘要偏好）作者 ⇒ 「奖励从哪来 + 标注预算」的一手判断 |
| 28（**第十一轮新增**） | Paul Christiano | `@paulfchristiano` | <https://x.com/paulfchristiano> | `200`，`og:title` = `Paul Christiano (@paulfchristiano) on X`，bio = `Founder &amp; Director of the Alignment Research Center. Former Head of Safety @ CAISI. Previously led alignment at OpenAI. Views my own.`（X 页自证；个人站未挂 X 链接） | 偏好奖励一作 ⇒ RLHF 思路源头，但发言偏 alignment 理论，**跟踪为主** |
| 29（**第十二轮新增**） | Bill Peebles | `@billpeeb` | <https://x.com/billpeeb> | `200`，`<title>` = `Bill Peebles (@billpeeb) / X`，bio = `head of sora @openai 🇺🇸🇺🇸🇺🇸` | Sora 负责人 ⇒ 视频生成 / 世界模型路线的一手判断源（⚠️ 官方报告本机 403，细节勿据传闻写） |
| 30（**第十二轮新增**） | Tim Brooks | `@_tim_brooks` | <https://x.com/_tim_brooks> | `200`，`<title>` = `Tim Brooks (@_tim_brooks) / X`，bio = `superintelligence @ Meta` | Sora 共同负责人（**已转 Meta**）⇒ 涉 Sora 发言均属「前负责人」视角，引用须标身份与时间 |


> **30 个 handle** 均来自其**本人主页的 `href`**、**X 页 `<title>`/`og:title` 自证** 或**论文作者身份可核对**的路径（前 6 个第四轮、7–10 第五轮、11–13 第六轮、14–17 第七轮、18–21 第八轮、22–25 第九轮、26 第十轮 `@KLieret`、27–28 第十一轮 `@janleike` / `@paulfchristiano`、**29–30 第十二轮 `@billpeeb` / `@_tim_brooks`**），并用 X 主页 `og:description` / `<title>` **二次核对身份一致**；`x.com/AlecRadford` 虽 `200` 但 bio 无身份信息、`x.com/JohnJumper` 虽 `200` 但仅 19 followers 且无 bio ⇒ **均拒绝登记**（见主表 #33 / #40）。⚠️ 序号在第十轮出现重复「25」（`@KLieret` 与 `@peteflorence` 同号）—— 属历史编号瑕疵，**handle 与核验证据不受影响**；本轮起按 27/28 续编，不再改动旧行（不删旧条目）。用户 follow 后请把状态改为 `已follow` 并写日期。

### 已核验言论台账（第四轮首获 · 原文 + 时间 + 链接）

| # | 人物 | 时间（UTC） | 原文（照抄） | 链接 | 用途 |
|:--|:--|:--|:--|:--|:--|
| V1 | Albert Gu `@_albertgu` | 2026-11-07 | "it's hilarious how many have taken the bitter lesson to mean just scaling up transformers. it's about scaling, but innovations in algorithmic primitives can lead to much more efficient scaling" | <https://x.com/_albertgu/status/2119206160410800219> | ✅ 已进日报 `voice_ready`（架构消融口径） |
| V2 | Tri Dao `@tri_dao` | 2026-10-28 | "Super interesting result: H-Net learns to dynamically tokenize variable names in coding data as separate tokens, and it scales much better on code compared to BPE" | <https://x.com/tri_dao/status/2115531348161028374> | ✅ 已进日报 `voice_ready`（代码语料 tokenizer） |
| V3 | Jason Wei `@_jasonwei` | 2026-11-10 22:31 | 起句 "Created a \"benchmark benchmark\": a frequency distribution of which benchmarks were reported by the frontier labs in 2026…"（**正文含转义引号，HTML 内嵌串被截断；推文页正文未渲染**） | <https://x.com/_jasonwei/status/2120283338640621826> | ❌ **未采用**：不满足「原文完整 + 可核验」，不冒充完整原文；仅在此登记，待下轮用其它入口取全文后再评估 |
| V4 | Richard S. Sutton `@RichardSSutton` | 2026-11-07 18:57 | "Brute force computation is not enough for intelligence. Clever new methods are needed. The science of AI is far from finished. IMHO" | <https://x.com/RichardSSutton/status/2119142310894334262> | ✅ **已进日报 `voice_ready`（2026-11-12 期）**；话题点 = 「暴力算力 vs 更聪明的方法」；风险 = 是**观点**且带 `IMHO`，🚫 不得写成结论 |
| V5 | Karthik Narasimhan `@karthik_r_n` | 2026-11-05 21:38 | 起句 `Just like everything else in the global economy, the future will have lots of AI agents for specialized tasks,  essentially creating multi-developer agentic systems that can benefit greatly from working together. @awhanjie 's latest paper`（**抓到的 `full_text` 在此处截断**；推文页正文未渲染） | <https://x.com/karthik_r_n/status/2118457961727275111> | ❌ **未采用（正文不完整）**：推文页 `200`、`og:title` = `Karthik Narasimhan (@karthik_r_n) on X` 作者可核，但正文不完整 ⇒ 按令**不冒充完整原文**；下轮换入口（thread 首条 / 转载全文）再评估 |
| V6（**第七轮新增**） | Chelsea Finn `@chelseabfinn` | 2026-10-24 22:09 UTC | "Generative value classifiers are a new parametrization of Q-functions that don't require action conditioning. We think these may combine gracefully with large, pre-trained policies and learn/generalize better from a richer output signal. Paper: https://t.co/pNphW8m0uf"（原文两处换行，此处以空格连接；**起止完整**） | <https://x.com/chelseabfinn/status/2114117117813706782> | ✅ **已进日报 `voice_ready`（2026-11-12 期）**，推文页 `200` + `og:title` 双核验；话题点 = 「不依赖动作条件的价值函数」；风险 = 是**作者观点 + 自家论文**，须标「作者自述」 |
| V7（**第七轮新增**） | Sergey Levine `@svlevine` | 2026-11-09 06:02 UTC | 起句 `A VLM can figure out semantics: which object to grasp, where to put it. But how do we turn this knowledge into fluent and dexterous actions? At CoRL on Tuesday, Andy and Will will talk about Flow Reversal Steering: a method for passing VLM …"（**抓到的 `full_text` 在引号处截断**） | <https://x.com/svlevine/status/2119672075589726281> | ❌ **未采用（正文不完整）**：推文页 `200` + `og:title` = `Sergey Levine (@svlevine) on X` 作者可核，但正文不完整 ⇒ 按令**不冒充完整原文** |
| V8（**第七轮新增**） | Oriol Vinyals `@OriolVinyalsML` | 2026-08-05 16:05 UTC | "Thirteen years ago, a quick email exchange with @JeffDean brought me to @Google. After an unforgettable journey from Brain, to DeepMind, and to @GoogleDeepMind, working on seq2seq or distillation, and co-leading huge projects such as AlphaStar, and Gemini, I'm saying goodbye to https://t.co/v2zK39buQ1"（起止完整） | <https://x.com/OriolVinyalsML/status/2085034508777304440> | 🕓 **>30 天 ⇒ 降级**（2026-08-05，98 天），**不进 `voice_ready`**；只作作者动向记录（已离开 Google，创办 Discovery Loop） |
| V9（**第十轮新增**） | Tri Dao `@tri_dao` | 2026-11-05 19:01 UTC | "Distilling most of our expertise in kernel and inference engine optimization into an agent loop that powers our production. A 2-year project that we're finally able to share" | <https://x.com/tri_dao/status/2118418321456660572> | ✅ **已进日报 `voice_ready`（2026-11-12 06:00 期）**：推文页 `200` + `og:title` = `Tri Dao (@tri_dao) on X` + `og:description` **逐字等于** profile 抓到的 `full_text`（双源一致）⇒ 可用；话题点 = 「把 kernel/推理优化经验蒸馏进 agent loop」；风险 = 属**自家产品**宣传，🚫 不得写成第三方评测 |
| V10（**第十轮新增**） | （拟 John Yang `@jyangballin`） | 2026-10-28 13:44 UTC | 拟用文 "New paper: Frontier Coding Agents Find Different Bugs Than Maintainers Fix…" | <https://x.com/jyangballin/status/2115439606443528405> | ❌ **未采用（作者不符）**：推文页 `200` 但 `og:title` = **`Mark Müller (@mnmueller) on X`** ≠ John Yang ⇒ profile 抓取的 timeline JSON **混入了他人推文**；按令**不采用**。这条是本轮发现的重要口径漏洞（见下方维护纪律 3） |
| V11（**第十轮新增**） | （拟 Shunyu Yao `@ShunyuYao12`） | 2026-11-05 19:07 UTC | 拟用文 "Hy4 from @TencentHunyuan is the new #1 open-weights model on APEX-Agents…" | <https://x.com/ShunyuYao12/status/2118420063242039721> | ❌ **未采用（作者不符）**：推文页 `og:title` = **`Mercor (@mercor) on X`** ⇒ 同上，非本人推文；**不采用**（同轮另两条 `@ShunyuYao12` 的推文作者核对通过，但正文为「Try it out!」等无信息量短句 ⇒ 也不用） |
| V12（**第十一轮新增**） | Jason Wei `@_jasonwei` | 2026-11-11 21:31 UTC | 起句 `The fall of “what you can do” and the rise of “who you know”… Traditionally, many of us believe in a world where how hard you work is more important than who you know. I used to subscribe to this idea as both a scientist, who believed that facts about our world are agnostic to who says them, and as…`（**`og:description` 以省略号截断**） | <https://x.com/_jasonwei/status/2120630417158250953> | ❌ **未采用（正文不完整）**：推文页 `200` 且 `og:title` = `Jason Wei (@_jasonwei) on X` 作者可核，但 `og:description` 与 profile `full_text` **两处都被截断**，无法给出完整原文 ⇒ 按令不采用；`voice_ready` 本期**仍为 V2 / V4 两条** |



> ⚠️ 引用纪律：`voice_ready` 只采用**原文完整 + 作者可核**的条目（V1 / V2 / V4 / V6 / V8；V3 / V5 / V7 / **V12** 正文截断不采用；V10 / V11 作者不符不采用），**每条附原链接与时间**，中文仅作翻译、不作转述；V8 >30 天已降级。

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
| 2026-11-11 18:06（**第六轮**） | Karthik Narasimhan | GPT-1（无 arXiv） | 本人主页 `karthiknarasimhan.com` 的 `mailto:`（percent-encoded，`200` / 14,706 B 实测） | `SENT OK`（`karthikn@princeton.edu`，**英文 164 词**） |
| 2026-11-11 21:04（**第七轮**） | Moo Jin Kim | `2406.09246` OpenVLA | 本人主页 `moojink.github.io` 防爬写法 `moojink at cs dot stanford dot edu`（`200` / 33,139 B 实测） | `SENT OK`（`moojink@cs.stanford.edu`，**英文 195 词**；⚠️ 已入职 OpenAI，若退信记「通道失效」） |
| 2026-11-12 00:1x（**第八轮**） | Danny Driess | `2410.24164` π0 | 本人主页 `dannydriess.github.io` 防爬写法 `danny dot driess at gmail dot com`（`200` / 29,043 B 实测） | `SENT OK`（`danny.driess@gmail.com`，**英文 178 词**） |
| 2026-11-12 03:03（**第九轮**） | Pete Florence | `2307.15818` RT-2 | 本人主页 `www.peteflorence.com` 明写 `pete dot florence at gmail dot com`（`200` / 47,238 B 实测） | `SENT OK`（`pete.florence@gmail.com`，**英文 189 词**） |
| 2026-11-12 06:05（**第十轮**） | Karl Pertsch | `2405.12213` Octo | 本人主页 `kpertsch.github.io` 的 `mailto:karl.pertsch@gmail.com`（`200` / 64,903 B 复测，2026-11-12 06:0x） | `SENT OK`（`karl.pertsch@gmail.com`，**英文 191 词**；同机构 PI 当日第 2 封 = 达上限） |
| 2026-11-12 09:04（**第十一轮**） | Jan Leike | `1706.03741` Deep RL from human preferences | 本人主页 `jan.leike.name` 的 `mailto:Jan Leike <jan@anthropic.com>`（`200` / 6,411 B，2026-11-12 09:0x） | `SENT OK`（`jan@anthropic.com`，**英文 199 词**；Anthropic 当日第 1 封） |

| 2026-11-12 12:04（**第十二轮**） | Nisan Stiennon | `2009.01325` Learning to summarize from human feedback | 本人站 `nisanstiennon.com` 的 `mailto:nisan+web@stiennon.com`（`200` / 5,575 B，直连与代理 **md5 一致**） | `SENT OK`（`nisan+web@stiennon.com`，英文；⚠️ **`wc -w` 实测 212 词，超 ≤200 规格 12 词，已如实记入台账**） |
| 2026-11-11 12:4x–13:0x（**第四轮**） | （本轮 **0 封**） | 新增经典 `2005.14165` / `2203.02155` / `2302.13971` | 逐个实测：`hugotouvron.github.io` `404` · `longouyang.github.io` `404` · `ashishvaswani.com` `000` · 未命中任何 `mailto:` | **不发信**（按令不猜邮箱）。该轮结束时累计 **5 封**（分属三轮，每轮 ≤3）；第四轮把额度留给「有可核验邮箱」的候选 —— 本轮没有合格的 ⇒ **宁缺勿凑**（当日最终累计 = **9 封**，见上方各行） |

---

## 四、维护纪律

1. **一次一作者**：同一作者 / 同一论文 ≤1 封；同一机构 ≤2 封/天（`RESEARCH_MAIL_SPEC §3`）。
2. **邮箱取当前机构主页 / 本人 CV 的最新地址**，🚫 不用 5 年前 PDF 首页的旧邮箱（可能已失效或转他人）。
3. **X handle 只登记可访问页面读到的**，并在 X 可达时用 `og:description` 二次核对身份；`voice_ready` **必须有原文 + 原链接 + 时间**，两处不一致或正文不完整的一律不采用（如 V3）。<br>⚠️ **2026-11-12 第十轮新增教训**：`x_fetch.py` 从 profile 页内嵌 timeline JSON 解析出的条目**会混入他人推文**（本轮 V10/V11 两条经单条推文页 `og:title` 核对分别是 `@mnmueller` 与 `@mercor`）⇒ 今后**每条拟引用推文都必须先打开 `x.com/<handle>/status/<id>` 核 `og:title` 的作者名**，作者不符直接丢弃；**正文也要用 `og:description` 与 profile `full_text` 相互校验**，二者一致才算「双源一致」。
4. 状态四态：`待跟踪` → `已follow` → `已发信` → `已回复`；每次只前进，不跳级、不回退（回信内容另存 `research/mail/replies/`）。
5. 抓 X 一律走 `research/classic/x_fetch.py`（只读、串行、≥3s、单轮 ≤6 个 handle），原始结果落 `research/classic/x/`，**不做任何写操作**。
6. **发送前必查词数（2026-11-12 新增，血的教训）**：英文信发送**之前**先 `wc -w <body.txt>` 确认 ≤200（中文 ≤300 字），**不达标先删改再发**。第十二轮因「先发后核」实测 **212 词**、超 12 词 ⇒ 已如实记入 `research/mail/发送记录.md`；此后本项为**发送前置检查**，不是事后记录。
7. **X 抓取需显式代理**：本机 shell 默认**不继承** `HTTP(S)_PROXY`，直连 `x.com` 会返回 `000`；`x_fetch.py` 内部默认走 `http://127.0.0.1:7897`，手工 `curl` 时**必须加 `--proxy`**。`000` **不等于**代理挂了（本轮实测：直连 000 / 带代理 200）⇒ 先分清「无代理」与「代理挂」，再决定是否报运维。
