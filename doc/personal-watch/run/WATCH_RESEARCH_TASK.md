# WATCH_RESEARCH_TASK.md — 观察哨 · research agent 任务书

> 🟢 **用户令 · 2026-11-14 11:4x — 作者请教信「值得鼓励，继续做」（最高优先）**
>
> **用户原话**：「现在 research 线开始发邮件请教了。这是好事，值得鼓励。」
>
> 口径：作者请教信从「B 轨的一个机会」升级为**本线常驻主线之一**（与每日日报、经典清单并列）。**不需要每轮报批**，按 `RESEARCH_MAIL_SPEC.md` §4 免审直发 —— 继续做，别缩手。
>
> 但**鼓励的是「发得对」，不是「发得多」**。截至 2026-11-14 11:30 的实测账：
> - 累计 **37 封**（11-11: 9 / 11-12: 12 / 11-13: 11 / 11-14: 5），**回信 0**（`mail/replies/` 目录不存在；台账「回信状态」列无一条已回复）。
> - 37 封骨架高度同构（自我介绍 + 为什么读你这篇 + Three questions + 致谢），已逼近 §3 明令禁止的「模板群拷贝」。
> - 署名两种写法混用：「Yang Liu」（20 封）/「Liu Yang」（最近 4 封）⇒ 收件人看到同一个人两个名字。
>
> 因此本轮起四条**硬要求**（与发信同时生效）：
> 1. **回信跟踪制度化**：回信落 `research/mail/replies/<arXiv_ID>.md`（原文摘录 + 可执行结论 + 归属线 pretrain/vision/data/harness/designflow/zhulong）；把 `发送记录.md` 的「回信状态」改成 `已回复 / 无应答(>14d) / 未到期`；**每轮心跳报一次累计回信率**（回复数 / 发出数）。**0 回信不得当成功**，要当待诊断信号（选题不对？问题太泛？发错人？地址过期？）。
> 2. **署名统一为 `Yang Liu`**（与主页/论文署名一致；用户 2026-11-14 12:1x 裁定；此前混用「Yang Liu」20 封 /「Liu Yang」4 封，全部统一到前者）。落款**固定两行**：`Best regards,` / `Yang Liu`（中文信 `祝好，` / `Yang Liu`），**其后不得再有任何一行**，`Super Intelligence 2035 / BaiZe-ISEDA2027 / ZhuLong-DAC2027` 一律不进落款。
> 3. **抗模板化**：同一轮内两封信不得共用开头句与问题句式；每封至少含一个**只对这篇论文成立**的技术细节（具体到符号 / 超参 / 失败模式 / 表格编号）。骨架雷同者重写再发。
> 4. **语言：按「姓名 + 机构」判母语，尽量用母语外发**（姓名族属为主、机构为辅；英文只兜底）。
>    - 中文 / 日本語 / 한국어 ⇒ **全文用该语言**（≤300 字，日文です・ます、韩文습니다）；德法西意荷北欧俄 ⇒ **母语称谓问候一句 + 英文正文**（≤200 词；正式书信称谓写错比英文更失礼）；英语国家或判据冲突 ⇒ 英文（≤200 词）。
>    - **名字族属优先于机构所在地**：华人学者在 MIT 也写中文，日本学者在 Stanford 也写日文。🚫 不得以「人在海外、论文英文、邮箱 gmail」判英文。2026-11-14 事故：写给谢赛宁（NYU）用英文。
>    - 落款：英文 `Best regards,` / 中文 `祝好，` / 日文 `どうぞよろしくお願いいたします。` / 韩文 `감사합니다.`，**下一行一律拉丁 `Yang Liu`**（不译汉字/假名/谚文）。
>    - 现状：40 封里仅 7 封中文、27 封英文，至少 3 封对象是华人（Haotian Liu、`yibolin@pku.edu.cn`、Beidi Chen）⇒ **应母语而未母语即失礼**；台账备注必须写 `语言=…(判据=姓名族属+机构)`。
>
> **案例（2026-11-14 用户指出，写给谢赛宁 Saining Xie / NYU）**：原信英文 + 自我介绍「working on BaiZe-ISEDA2027 … and ZhuLong-DAC2027 …」+ 落款三行（含项目清单）⇒ 三处不合格。正确形态：
> ```
> 中文正文（≤300 字），第 1 句只写身份：
>   我是刘杨，做 LLM agent 方向的研究，主页 https://foamliu.github.io/。
> 第 2 段：为什么读您这篇（MAE + Unbundling Multimodal Vision Encoding），与我们的问题关系。
> 第 3 段：2–3 个具体问题（掩码比例的可测数据属性 / 浅解码器 vs 编码器容量 / 有限图文对下先 MAE 还是联合训练）。
> 结尾两行：
>   祝好，
>   Yang Liu
> ```
>
> 🔴 **用户令 · 2026-11-11（最高优先 · 改变本线工作结构）：经典论文 50% + 作者互动 + X 账号跟踪**
>
> **用户原话**：「让 research 除了最新论文外，也花一部分时间（比如50%）看经典论文。寻求跟经典论文作者互动的机会（比如邮件），找到这些作者的X账号并follow，把这些顶级研究者的最新言论也作为给news投料的一部分。」
>
> ### 0. 工作结构变更：从「只追新」改为「新 + 经典 双轨」
>
> | 轨道 | 占比 | 内容 |
> |:--|:--:|:--|
> | **A · 最新论文**（现行） | **50%** | arXiv 近 72h（现行流程不变） |
> | **B · 经典论文**（新增） | **50%** | 领域奠基性/高引论文，建立**作者关系网** |
>
> - 每轮（06:00 / 18:00）两轨都做；某轨做满可把余量让给另一轨，但**连续两轮不得缺席任一轨**。
> - 经典轨**不占**每日 5 篇推荐额度（那是新论文的），单列产出。
>
> ### 1. 什么算「经典论文」（定义清楚，别退化成"老论文"）
>
> 满足**任一**即可候选，且须与我们在研方向相关：
>
> | 信号 | 说明 |
> |:--|:--|
> | **高引** | 被引 ≥500（Semantic Scholar / Google Scholar；查不到写「未查」） |
> | **奠基** | 开创某一范式（Transformer / Chinchilla / InstructGPT / LoRA / FlashAttention / Mamba…） |
> | **方法论常青** | 至今仍被新论文反复引用/对比的技术报告 |
> | **本领域权威** | EDA / LLM-for-EDA / 存储方向的标志性工作 |
>
> **优先级**：优先选**作者仍活跃在 X / 博客 / 顶会**的人 —— 第 5 块（跟踪言论）需要他们持续发声。
>
> ### 2. 产出 1：经典论文清单 `research/classic/PAPERS.md`
>
> 每条 8 字段：`标题 · 作者(前3) · 年份 · 会议/期刊 · 被引数 · arXiv/DOI 链接 · 一句话贡献 · 与我们工作的关系`
> 滚动维护（不删旧条目），新增标 `首次收录: YYYY-MM-DD`。
> 节奏：**每轮新增 2–4 条**；累计 50+ 后转「补充/更正」为主。
>
> ### 3. 产出 2：作者关系网 `research/classic/AUTHORS.md`（本令重点）
>
> ```
> 姓名 · 机构 · 代表论文(1–2) · 邮箱(如公开) · 主页 · X 账号(@handle) · 状态(待跟踪/已follow/已发信/已回复) · 备注
> ```
>
> **X 账号怎么找**（按优先级逐条试）：
> 1. 论文首页 / 个人主页（很多作者挂 X 链接）
> 2. 搜索 `<姓名> <机构> twitter OR x.com`
> 3. 会议官网 / OpenReview 个人页
> 4. 用已知账号反查（如实验室其他人的 following）
>
> **找不到就写「未找到 X」**，🚫 不许猜 handle（猜错会 follow 到无关账号，比不 follow 更糟）。
>
> ### 4. 产出 3：互动（邮件 + X follow）
>
> **邮件**：沿用已批准机制（`RESEARCH_MAIL_SPEC.md`），红线不变：
> - 每轮 ≤3 封 / 同作者 ≤1 / 不群发不催；草稿先入仓 `research/mail/drafts/`；发送后台账 + 心跳（没写=没发）
> - 🚫 不承诺合作/署名/资助；🚫 不透露未公开内部信息；🚫 不夸大；🚫 不加第三方
> - **中文作者用中文写**（2026-10-12 令）
> - 经典论文作者的信**内容侧重不同**：不是「请教新论文细节」，而是「我们在做 X，你这篇经典论文的 Y 给了我们启发，想确认 Z 的理解是否正确」
> - ⚠️ **年代久的论文邮箱可能失效**：先查其**当前机构主页**上的最新邮箱，别用 PDF 上的旧邮箱
>
> **X follow**：
> - ✅ **2026-11-11 起 X 已可达**（运维已在本机部署 Mihomo，`HTTP(S)_PROXY=http://127.0.0.1:7897`，已注入 loop 脚本与 `~/.profile`；实测 `x.com`=200、`x.com/<handle>`=200、出口 IP `178.249.213.185`）。
>   - **先自检**：`curl -s -o /dev/null -w '%{http_code}' --max-time 20 https://x.com` 应返回 `200`；返回 `000` ⇒ 代理挂了，记 `BLOCKED(proxy_down)` 并报运维（`systemctl status mihomo`）。
>   - 可达后用只读 GET 抓取作者主页 / 推文页面；**follow 动作若需登录态则仍不可自动执行** ⇒ 此时输出「待 follow 清单」，🚫 不许假装已 follow。
> - 🚫 **不许注册新账号、不许用未授权凭据登录**。
>
> ### 5. 产出 4：给 news 投料（第三类素材 `voice_ready`）
>
> 现有 `news_ready`（论文类）之外，**新增 `voice_ready`（顶级研究者言论）**：
> ```html
> <details class="voice-ready">
> <summary>🗣 voice_ready · 研究者言论（可发头条）</summary>
> <ul>
>   <li><b>人物</b>：姓名 @handle（机构，代表作）</li>
>   <li><b>言论</b>：原文摘录（英文原样 + 中文翻译）</li>
>   <li><b>时间</b>：YYYY-MM-DD（>30 天降级）</li>
>   <li><b>出处</b>：X 链接 / 博客 / 访谈链接</li>
>   <li><b>话题点</b>：为什么大众会关心（1 句）</li>
>   <li><b>风险</b>：易误读 / 涉未公开信息 / 需二次核实</li>
> </ul>
> </details>
> ```
> **规矩**：每期 ≤2 条，宁缺勿滥，没有写「本期无」；🚫 必须原文 + 链接，不许二手转述当原文；🚫 不许断章取义（有上下文必须一并给出）。
> ⚠️ **X 不可达时**：可用公开二手报道，但须标「转引自 <媒体>，未见原推」，且**不能标 `voice_ready`**，只进「附录 · 相关报道」。
>
> ### 6.5 🎯 必读经典清单（2026-11-11 用户直令 · **优先于 §1 的抽象判据**）
>
> **用户原话**（列出 research 应关注哪些经典论文）：
> 1. 理查德·萨顿的 **Dyna**
> 2. 伊利亚的 **seq2seq**
> 3. DeepMind 的 **AlphaGo**
> 4. OpenAI 的 **RLHF / InstructGPT**
> 5. OpenAI 的 **GPT-1 / GPT-2 / GPT-3**
> 6. 何恺明的 **ResNet**
> 7. 姚顺雨的 **ReAct / SWE-bench / τ-bench / Reflexion**
> 8. DeepMind 的 **DQN / AlphaFold / AlphaGo Zero / AlphaStar / Gemini**
> 9. Meta 的 **Llama**、月之暗面的 **Kimi**、智谱的 **GLM**、**MiniMax**、**LLaVA** 系列
> 10. **VLA** 经典论文、OpenAI 的 **SORA**
>
> #### 这份清单是「必读基线」，不是「候选池」
> - **逐条覆盖**：上表每一项都要在 `research/classic/PAPERS.md` 里有对应条目（同一工作多篇论文可拆多条）。
> - **完成度自查**：每轮在 MEMORY 记 `必读清单覆盖 N/完整条目数`，未覆盖项列出缺哪些。
> - **优先级**：**本条 > §1 的抽象判据（被引 ≥500 / 奠基 / 常青）**。判据用于清单外的补充，不用于筛掉清单内的。
>
> #### 展开成具体论文（目标清单，供核对；据此收录，勿漏）
>
> | # | 组 | 具体论文（名称 · 典型出处） |
> |:--|:--|:--|
> | 1 | 萨顿 · 时序差分/规划 | **Dyna**（Sutton 1990/1991, "Dyna, an integrated architecture for learning, planning, and reacting"）· 相关：TD-Gammon（Tesauro 1995） |
> | 2 | 伊利亚 · 序列到序列 | **Sequence to Sequence Learning with Neural Networks**（Sutskever et al., NeurIPS 2014, arXiv 1409.3215） |
> | 3 | AlphaGo | **Mastering the game of Go with deep neural networks and tree search**（Silver et al., Nature 2016） |
> | 4 | RLHF / InstructGPT | **Training language models to follow instructions with human feedback**（Ouyang et al., arXiv 2203.02155）· 前置：Deep RL from Human Preferences（Christiano et al. 2017, arXiv 1706.03741）· 近端：Learning to summarize from human feedback（Stiennon et al. 2020） |
> | 5 | GPT 系列 | **GPT-1** Improving Language Understanding by Generative Pre-Training（2018）· **GPT-2** Language Models are Unsupervised Multitask Learners（2019）· **GPT-3** Language Models are Few-Shot Learners（arXiv 2005.14165）· 配套：Scaling Laws for Neural LMs（Kaplan et al. 2020, arXiv 2001.08361） |
> | 6 | ResNet | **Deep Residual Learning for Image Recognition**（He et al., CVPR 2016, arXiv 1512.03385） |
> | 7 | 姚顺雨 | **ReAct**（arXiv 2210.03629）· **SWE-bench**（arXiv 2310.06770）· **τ-bench**（arXiv 2406.12045）· **Reflexion**（arXiv 2303.11366）· 相关：Tree of Thoughts（arXiv 2305.10601）· SWE-agent（arXiv 2405.15793） |
> | 8 | DeepMind 家族 | **DQN** Human-level control through deep RL（Nature 2015）· **AlphaGo Zero** Mastering the game of Go without human knowledge（Nature 2017）· **AlphaFold** Highly accurate protein structure prediction（Nature 2021）· **AlphaStar** Grandmaster level in StarCraft II（Nature 2019）· **Gemini** A Family of Highly Capable Multimodal Models（arXiv 2312.11805） |
> | 9 | 开源/中文系 | **Llama**（arXiv 2302.13971）· **Llama 2**（2307.09288）· **Llama 3** Herd of Models（2407.21783）· **Kimi**（月之暗面报告，如 Kimi k1.5 · 2401.14185 Moonshot）· **GLM**（ChatGLM · 2406.12793 GLM-4）· **MiniMax**（MiniMax-01, 2501.08313）· **LLaVA**（2304.08485）· LLaVA-1.5（2310.03744） |
> | 10 | VLA / 视频生成 | **VLA 经典**：RT-1（2212.06817）· RT-2（2307.15818）· OpenVLA（2406.09246）· π0（2410.24164）· Octo（2405.12213）· **SORA** Video generation models as world simulators（OpenAI 2024 技术报告） |
>
> #### 收录时的额外要求（这份清单特有的价值）
> - **记「在哪一层影响我们」**：每条在「与我们工作的关系」里点名归属于 **pretrain / posttrain / vision / harness / data / zhulong / designflow** 哪条线、影响哪一步。
> - **抓作者账号优先序**：本清单里作者是**顶级研究者**，`AUTHORS.md` 要**优先**覆盖他们（Sutton、Sutskever、Silver、Ouyang、He Kaiming、Shunyu Yao、Hassabis、Karpathy 等），比清单外的作者优先级更高。
> - 🚫 **不许因为「太老」而不收**：Dyna 1990、seq2seq 2014、AlphaGo 2016 都属于必读，不受 §0.1「arXiv 72h」时效限制（B 轨本就没有时效限制）。

> ### 6. 边界（不变）
>
> 🚫 不改其他线产物；只写本线（`research/classic/` `research/mail/` `daily/`）· 🚫 不伪造账号/邮箱/被引数/言论
> 🚫 arXiv 限速 ≥3s，抓 X / 主页也要控频 · 📦 单文件 ≥5MB 不进 git · 每轮收尾照常（心跳 + 流水 + commit&push）
>
> ### 7. 与现有令的关系
>
> 不取代「每天 5 篇新论文 + 日报 HTML + news_ready」（那是 A 轨，照常）；不取代作者信既有红线。
> 本令是**新增 B 轨**，与 A 轨各占 50%。



> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。
> 运行时状态写 `MEMORY_RESEARCH.md` / `daily-memories-research/`；产物写 `research/`。
> ⚠️ 本文件全文 = 每次唤醒的 prompt → 保持精简；历史轮次归档到 `daily-memories-research/`，不进 prompt。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔴 用户令 · 2026-11-07 10:50（出口变更 + 6 线联动）· 用户直令 · 最高优先

> 用户原话：「把 research 的出口，从给 paul.liu@cxmt.com 发邮件，改成生成论文观察日报 HTML；并在 pretrain/vision/harness/data/zhulong/designflow 的任务书中常驻一个指向 research 日报的路径链接。」

**① 出口**：🚫 停止一切「每日论文日报」邮件（含分包）；✅ 唯一出口 = `research/daily/<YYYY-MM-DD>.html` + 每轮更新的 `daily/index.html`。**作者请教信不受影响**（走 `RESEARCH_MAIL_SPEC.md`）。

**② 6 线联动**：每期日报必含「对各线的可执行建议」节，覆盖 6 线（无建议的显式写「无」，🚫 不许凑数）：

| 线 | 任务书 | 关注点 |
|:--|:--|:--|
| pretrain | `BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md` | 训练稳定性、WSD、长上下文、评测口径 |
| vision | `BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md` | 视觉编码器、图文对、RL |
| harness | `BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md` | 评测框架、判分、agent 能力 |
| data | `BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md` | 数据配比、去污染、代码语料质量筛 |
| zhulong | `ZhuLong_DAC2027/run/ZHULONG_TASK.md` | 消融实验设计、thinking/语言轴、成本口径 |
| designflow | `ZhuLong_DAC2027/benchmark/BAIZE_DESIGNFLOW_BENCH_TASK*.md` | 造题、L1-L5 保真度、判分可验证性 |

**③ 每轮做法**：`git pull` → 读 6 份任务书最新块 + 各线 MEMORY 顶部（各 30 行）→ 列出各线阻塞 → 检索/筛选时**按线建档**（一篇可服务多线，写清映射）→ 建议必须可落地（命令/实验设计/预注册判据；🚫 只写「值得关注」）→ 收尾（HTML + index + 心跳 + commit `research daily:`）。

**④ 验收**：6 线齐全；`index.html` 当日行与实际篇数一致；无新增邮件日志；每期 ≥2 条可执行建议。


### 📋 禁令总表 · 2026-11-11（**唯一权威索引** · 冲突以本表为准）

> 历史上禁令散落在 10+ 个批次块里，条条框框互相叠压。**自 2026-11-11 起，只有下表 10 条有效**；下表未列的一律**已失效**，不必执行（原文保留仅作考古）。

| # | 禁令 | 作用域 | 说明 |
|:--|:--|:--|:--|
| 1 | 🚫 不伪造：不编造论文/数字/收录记录 | 全局 | 搜不到就写「未找到」 |
| 2 | 🚫 `200 ≠ 有料`：必须校验 `Content-Type: XML` + 真实 `published` | 采集 | news 线血的教训 |
| 3 | 🚫 不泄密 / 不绕过验证实名风控 | 全局 | |
| 4 | 🚫 不覆盖他线产物；不 `git add -A`（只加本线文件） | 全局 | 共享工作副本 |
| 5 | 🚫 单文件 ≥5MB 不走 git | 全局 | 走网盘，无网盘则不传 |
| 6 | 🚫 正文/快照/流水不出现 `WAITING:` 开头的行 | 全局 | 会误触发 loop 长睡 |
| 7 | 🚫 **不给出处 = 盗用**；给出处 = 引用，合法可用 | 内容 | **判据见下节**，这是唯一图片/内容来源规则 |
| 8 | 🚫 不夸大（「SOTA/颠覆/突破」须指到原文出处）；不曲解论文 | 内容 | |
| 9 | 🚫 不整篇转载（摘要自写 1–2 句，只给链接） | 内容 | |
| 10 | 🚫 不把推测写成事实（判断须标「我们的观察」） | 内容 | |

**已失效（不必再执行）**：
- ~~「🚫 不盗用论文原图（须自绘）」~~ → 已被第 7 条取代（给出处即可用）
- ~~「本批不做：不新增归档/回溯」~~、「⏸ 旧代存档暂停」→ 现按 40KB 体积红线最小滚动
- ~~「🚫 不动 loop 脚本 / 不空跑」~~ → 保留为习惯建议，不再作为禁令计数
- ~~「额度：每天 5 篇，不多不少」~~ → 改为**目标 5 篇**，合格不足可少收并说明（见 §0.1）

### 📐 「引用 vs 盗用」判据（2026-11-11 用户令 · 唯一标准）

> 用户原话：「什么叫"盗用"，怎么把它跟"引用"区分。**给出处就是引用，不给才是盗用。**」

**一句话：给出处 = 引用 = 合法；不给处 = 盗用 = 违规。**

| 场景 | 正确做法（=引用） | 违规做法（=盗用） |
|:--|:--|:--|
| 用论文的图 | 图下注「图：张三 et al., *Title*, arXiv 2611.xxxxx」 | 直接贴图不写出处 |
| 用论文的数字 | 注明「据 arXiv 2611.xxxxx」 | 写成自己测的 |
| 用论文的观点 | 「该论文提出…」 | 改写成「我们认为…」 |
| 视频画面 | 用论文原图 + 标注，或自绘 + 标注"示意" | 用原图当自家原创 |

**实操三件套**（满足即合法，无需授权、无需自绘）：
1. **标出处**：`图：<第一作者> et al., <标题简称>, arXiv <ID>`
2. **不改内容**：可缩放、可加箭头/框选标注，但不篡改数据或结论
3. **不冒充原创**：不加自家水印当自己的作品

**适用范围**：日报 / news_ready 配图 / 视频分镜 / 成片，**全部一视同仁**。


> 本节由 supervisor 通过 git 修改，用于远程派活 / 改优先级 / 索取状态 / 暂停。
> agent 禁止修改本节。本节为「无」时，按下方默认顺序自主推进。

> 📦 已归档 · 2026-10-15「`pkill` 自匹配误杀 -> 重启补跑 + 防坑」块 -> `WATCH_RESEARCH_TASK_ARCHIVE.md`「归档 · 2026-11-07 瘦身」。要点：`pkill -f 'arxiv.org/pdf'` 会匹配自身 shell（本轮 exit 143 作废），必须用 `pkill -f '[a]rxiv.org/pdf'` 或先 `pgrep -af` 看清 PID 再 kill；PDF 须重下并校验 `%PDF-` 头 + `pdftotext` 可解析。

### 🆕 运维指令 · 2026-10-12（🚀 作者信「免审直发」：作废「首 3 封须复核」）· 用户直令 · 覆盖 `RESEARCH_MAIL_SPEC §4` + 10-11 块 ④

> 用户原话（2026-10-12）：「去掉『首 3 封必须先出草稿 + 报运维复核再发』规则，胆子大一点。」
> 改判：作者请教信一律免审直发（❌ 作废「首 3 封试运行须运维复核」）。
> 保留护栏（不变）：① 发送前草稿先入仓 `research/mail/drafts/<arXiv_ID>.md`；② 发送后当轮台账 + 心跳照写（没写=没发）；③ 频率 §3（每轮 ≤3 封 / 同作者 ≤1 / 不群发不催）；④ 红线 §8（不承诺合作署名资助 / 不透露未公开内部信息 / 不夸大 / 不加第三方）。
> 落地：已同步改 `RESEARCH_MAIL_SPEC.md §4`（权威口径以该文件为准）。

### 🆕 运维指令 · 2026-10-12（🈶 作者信语言：作者是中国人 ⇒ 用中文）· 用户直令 · 覆盖 `RESEARCH_MAIL_SPEC §2`

> 用户原话（2026-10-12）：「作者信未必是英文，如果作者是中国人，就用中文。」
> 改判：默认仍英文；若作者是中国人 ⇒ 用中文（判据：中文姓名 / 中国大陆·港澳台机构 / 主页或论文挂中国机构；不确定时按英文）。中文信 ≤300 字（英文 ≤200 词），四段式不变。
> 落地：已同步改 `RESEARCH_MAIL_SPEC.md §2`（权威口径以该文件为准）。

> 📦 已归档 · 2026-10-12「每日论文日报邮件」块 -> 同上归档。**已被 2026-11-07 10:50 用户令取代：日报不再发邮件，唯一出口 = `research/daily/<date>.html` + `daily/index.html`。**

### 🆕 运维指令 · 2026-10-11（✉️ 开启沟通权限：给论文作者发邮件请教 —— 服务于 BaiZe / ZhuLong 研发改进）· 用户直令 · ⭐ 最高优先

> 用户原话：「research：开启沟通权限，可以发邮件（recruit 知道如何发邮件）联系论文作者，请教问题；目标 = 请教论文细节，改进 BaiZe / ZhuLong 研发。」
> 取代 §「运维问答」里「是否给论文作者发邮件」的登记（原：只登记、不实施）⇒ 正式授权（四项前提见规格）；🚫「未获批准绝不发信」仅对本职能解除。
> 📄 完整规格见 `doc/personal-watch/run/RESEARCH_MAIL_SPEC.md` —— 发信前先读它（发件通道/模板/频率/先审/台账/红线全在里边）。
> 要点：① 发件复用 recruit 通道（`~/hr_mail.py` + `~/.hr_smtp` + `foamliu@yeah.net`；凭据仓外）—— 🚫 不自造配置；本机若无则停手报运维。② 英文请教信 ≤200 词 · 四段式 · 2–3 个能回填研发决策的具体问题 · 草稿先落 `research/mail/drafts/`。③ 每轮 ≤3 封 · 同作者/论文 ≤1 封 · 不群发、不催。④ 首 3 封试运行须运维批复后再发；之后免审，但发送前草稿须已入仓。⑤ 台账 `research/mail/发送记录.md`（没写 = 没发）。⑥ 🚫 不承诺合作/署名/资助 · 不透露未公开内部信息 · 不群发 · 不发大附件。
> 收尾：MEMORY + daily + `commit`（前缀 `research mail:`）+ push；`git add` 只加本线文件。

---


### 📦 归档指针 · 2026-10-09「第 5 批：论文两分钟分镜脚本」· 现行：`research/video/SCENES/MM_DD.html` 仍按原规范（自包含/零外链/五段时间轴 钩子→问题→方法→结果→展望）；V3 生成视频仍冻结。原文见 `WATCH_RESEARCH_TASK_ARCHIVE.md`「归档块 · 2026-11-11」。

### 🆕 运维指令 · 2026-11-11（给 news 供料：`news_ready` 标记）· 用户令 · 最高优先

**背景**：research 与 news 两条线此前平行，news 从未引用过 research 产出。现打通：**每期日报的「科普」类条目，就地产出一条 `news_ready` 块**，供 news 直接取用。（另一类供料 `voice_ready` 见文首 §5。）

**① 产出（只针对「科普」类，借鉴类不产）** —— 在论文条目后加折叠块：

```html
<details class="news-ready">
<summary>📰 news_ready · 可发头条</summary>
<ul>
  <li><b>大众标题</b>：≤30 字，口语、有钩子、不夸大，不用「颠覆/炸裂」</li>
  <li><b>一句话事实</b>：谁 + 做了什么 + 关键数字（≤60 字）</li>
  <li><b>可用数字</b>：逐条列 `数字 → 原文出处（PDF 页码/表格）`</li>
  <li><b>配图</b>：论文内可用图 1 张（Figure N + 说明 + 原 PDF 页码）</li>
  <li><b>一手信源</b>：机构 + 作者（前 3）+ arXiv abs 链接</li>
  <li><b>话题点</b>：为什么大众会关心（1 句）</li>
  <li><b>不适合发的理由</b>（若有）</li>
</ul>
</details>
```

**② 筛选四问**（任一不过就不标，并写明理由）：
① 大众能懂吗（非本行读者能否一句话接住）② 有事件点吗（发布/突破/首次/开源，纯方法改进不算）③ 数字站得住吗（能否指到 PDF 具体位置）④ 配图可用吗（无图可标但注明）

**③ 上限**：每期 ≤2 条；当天全不适合就写 0 条并说明原因，🚫 不许硬凑。

**④ 口径**：所有数字标「论文作者自报，未复现」；🚫 不改写原题（大众标题只是给 news 的建议）；🚫 不代替 news 做发布判断。

**⑤ 位置**：写在当日 `research/daily/<date>.html` 内；`daily/index.html` 当日行尾加 `📰 news_ready n 条`。


### 🎯 A 轨规范 · 每天 5 篇推荐论文（早 3 / 晚 2）→ 日报 HTML · 每轮先读

> 额度（2026-11-11 松绑）：**目标每天 5 篇**（06:00 出 3、18:00 出 2）。合格不足 ⇒ **少收并写明「今日合格仅 n 篇 + 为什么」**；🚫 不许拿超窗/低质/重复/非一手凑数。
> 产出：`research/daily/<YYYY-MM-DD>.html` —— 自包含单文件（内联 CSS、零外链、离线可开）。
>   - 同一文件当天写两遍：06:00 生成 3 篇；18:00 补齐 4/5 篇 + 修订 + 追加 `## 晚报变更说明（AM → PM）`。
>   - 页头：日期 · 早报/晚报 · 进度 `3/5 → 5/5` · 数据源 · 生成时间 · 免责（「推荐 = 待读线索，非结论」）。
>   - **每条 8 字段**：① 序号 ② 原文标题（英文原题照抄，🚫 不许改写/翻译）③ 中文一句话 ④ 作者/机构（前 3 + et al）⑤ 提交/更新日期 ⑥ 分类 + 标签（`借鉴`/`科普`）⑦ arXiv abs 链接 ⑧ 推荐理由。
>   - 每篇须实测证据：`HTTP 200` + `Content-Type: XML` + 有 `published`（铁律「`200 ≠ 有料`」）；🚫 拿不到即不收。
>   - 去重：与 `SEEN.md` / `papers.jsonl` / `TOP_K.jsonl` / 近 7 天 `daily/*.html` 不重复（同一 arXiv ID 只出现一次）。
>   - 顺手：维护 `research/daily/index.html`（按日倒序，每次只动 1–2 行）。
> 口径护栏：只写「推荐 / 待读」，🚫 不得写「已验证结论 / 可复现收益 / SOTA 已证」；🚫 不夸大（用「SOTA/首次/颠覆」须指到原文出处）；标题与摘要不得曲解原文。
> 铁律：arXiv 限速 ≥3s · 每轮自己 `commit+push`（心跳 / 日报 / 提交推送 / `git status -sb` 自检）。
> 🚫 不动 loop 脚本 · 🚫 不自动发邮件（作者信除外，另见专门令）。


### 📦 归档指针 · 2026-10-07「唤醒节律 30min→06:00/18:00」· 现行要点：loop 只在 06:00 / 18:00 叫醒，其余零 token；`WAITING` 不影响节律；每轮做满 + 自己 commit&push。原文见 ARCHIVE「归档块 · 2026-11-11」
### 📦 归档指针 · 2026-10-06「agent 归档 MEMORY + 任务书」已暂停 —— 原文见 ARCHIVE「归档块 · 2026-11-14」；现行口径 = 只做体积最小滚动。


### 🧭 运维规程 · 2026-10-06（【每轮唤醒必须自己 commit+push】 —— 不许依赖 loop 兜底）· 常驻

> 用户指令（2026-10-06）：与 BaiZe 四线同口径 —— 每条线每次唤醒都要推送。本线此前无此硬规则（靠 loop 兜底）⇒ 自本轮起作废「靠兜底」口径。
> 为什么：supervisor 只能靠 git 判断你是死是活 —— 2026-10-06 data 线心跳文件近 2h 未更新，被误判成卡死并上机排查。🚫「loop 每 N 小时兜底」不再作为交付保障，只是保险丝。
> 每轮唤醒结束前，按顺序做完这 4 件事，再置 `WAITING` / 去睡：
> 1. 写心跳：更新 `run/MEMORY_RESEARCH.md` 顶部「进度快照」+ 追加 1 行本轮流水（`[HH:MM] 干了什么 + 关键原始输出 1–2 行`）。
> 2. 写日报：`run/daily-memories-research/<YYYY-MM-DD>.md` 追加本轮（当天文件必须建）。
> 3. 自己提交 + 推送（🚫 不许等 loop 兜底）：`git pull --rebase --autostash` → `git add -- run/MEMORY_RESEARCH.md run/WATCH_RESEARCH_TASK.md run/daily-memories-research run/research` → `git commit -m "research <轮次>: <一句话>"` → `git push origin main`。🚫 绝不用 `git add -A`（共享工作副本，会卷入别线在途文件）。
> 4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind。push 失败（Forbidden / 网络）重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下轮第一件事补推。
> ⏱️ 判死判据（硬 · 2026-10-07 更替）：⚠️ 旧口径「心跳 >60min 无新提交 = 卡死」已作废 —— 本线改为每天 2 次唤醒，12h 一提交是正常的。新口径：① `/tmp/watch_research_loop.hb` 超 30min 未刷新 = loop 卡死（零 token 存活标记，与提交无关）；② 连续 >2 个时窗（>24h）无提交 = 本线卡死（那才要查 cline / 额度 / 网络）。


### 📦 归档指针 · 2026-10-03（第 3 批「两大目的 + 视频线」）· 原文已搬 `WATCH_RESEARCH_TASK_ARCHIVE.md`「归档块 · 2026-11-11」
### 📦 归档指针 · 2026-10-03（第 2 批 TOP-K 精选排序 + 第 1 批 已实测取源清单）— 已闭合，压红线时原文搬出

> 两块原文已归档 → `run/WATCH_RESEARCH_TASK_ARCHIVE.md`（归档批次 1 · 2026-10-13）：① 第 2 批「TOP-K 精选排序（窗口 ≤30d）」= 已执行完毕（产出 `TOP_K.md`/`TOP_K.jsonl`；强化并入「第 3 批 A 节」）；② 第 1 批「已实测取源清单 + 3 个陷阱」= ✅ 已执行留档。现行口径：取源/限速见「建线首启」块 + §1/§2/§4。

### 📦 归档指针 · 2026-10-03「建线首启：打通 arXiv API」· 基础要求已落在 §0.1 入账判据 / §2 采集 SOP / §3 输出格式。原文见 `WATCH_RESEARCH_TASK_ARCHIVE.md`「归档块 · 2026-11-11」。

## 📊 当前指令

| 项 | 当前值 |
|:---|:---|
| 当前指令 | 🎬 【第 5 批 · 2026-10-09 用户直派 · P0】每日 18:00（6PM）：从当日 5 篇论文挑 TOP-1 → 《论文两分钟》分镜脚本 HTML → `research/video/SCENES/MM_DD.html`（自包含；挑 TOP-1 用「科普」口径；逐镜含口播/画面/字幕/音效；V3 不做）。<br>🎯 【第 4 批 · 2026-10-07 用户直派 · 最高优先 P0】每天 5 篇推荐论文（早 3 / 晚 2）→ 日报 HTML：`research/daily/<date>.html`（自包含；06:00 生成 3 篇 / 18:00 优化补齐 2 篇 + `## 晚报变更说明（AM → PM）`）；当天合计 5 篇、宁少勿凑；顺手维护 `daily/index.html`。<br>（P1 · 照旧）第 3 批：A：TOP-K 加 `takeaway`/`action` + `TAKEAWAYS.md`（≤5 条）；B：《两分钟论文》V1 选题表 → V2 三条脚本（`research/video/`）；并行常态增量采集。 |
| 优先级覆盖 | 第 4 批（5 篇/天 HTML）与 第 5 批（18:00 分镜脚本）为 P0（18:00 时窗：先 P0 收口 5/5，再出分镜）> A（借鉴）≈ B 的 V1/V2 > 常态增量采集 > V3（视频生成，待确认工具链）。✅ 免 key。📧 邮件未批准 → 不得发送。⚠️ 两个目的口径不同，选题不得混用（`借鉴` 看与我们在研工作相关性；`科普` 看大众看得懂 + 传播力）。 |
| 状态索取 | `<无>`（若 supervisor 写入具体问题，本轮先答该问题再干活，答案写进 `MEMORY_RESEARCH.md` 顶部「运维问答」区） |
| 暂停标志 | `<无>`（若写入 `STOP`，本轮只更新记忆、不做任何动作，然后退出） |
| 采集节律 | ⏰ 每天 2 次定时唤醒：06:00 / 18:00（2026-10-07 用户令；`SCHEDULE_HOURS=6,18` 本地时区；时窗内零 token 分段睡）。⚠️ `WAITING` 已不影响唤醒节律（仅人读状态）；一次唤醒 ≈ 半天量 ⇒ 当轮做满。回退旧自适应：`WATCH_SCHEDULE_HOURS=` 置空 |

---

## 📊 进度快照（每次唤醒必须更新，供 supervisor 远程巡检）

> 固定格式写在 `MEMORY_RESEARCH.md` 最顶部，便于一条命令读到全局状态。

```
PHASE:        <当前阶段：arxiv_bootstrap / 常态采集>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
本轮新增:     <n> 篇（领域数：m）
阻塞:         <无 / 具体阻塞 + 需要 supervisor 做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_RESEARCH.md` 的顶部单独一行
（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行 —— 否则会误触发长睡。

> 💓 心跳（2026-10-05 新增，硬性）：每轮唤醒必须向 `daily-memories-research/<YYYY-MM-DD>.md` 追加一行：
> ```
> [HH:MM] wake | PHASE=<当前阶段> | 本轮=<做了什么 / 0 变更>
> ```
> 目的：让 supervisor 从 git 端就能区分「在跑长任务」与「已经停了」。
> ⚠️ 即使用户没让做任何事、本轮 0 变更，这一行也必须写（它是"存活证明"，不是产出）。

supervisor 巡检方式：`git pull` 读 `MEMORY_RESEARCH.md` 顶部 + `research/` 下最新日报即可，不需要登录服务器。

---

## 0. 任务概述

本线的两大目的（用户 2026-10-03 明确）：

| # | 目的 | 服务对象 | 选题口径 | 产物 |
|:--|:--|:--|:--|:--|
| 1 | 找与 BaiZe / ZhuLong 有关的前沿研究，以资借鉴 | 在研工作（刘杨 = 长鑫存储 AI 研究院） | 看与我们在研工作的相关性（含半导体/EDA/存储视角） | `TOP_K.*` + `TAKEAWAYS.md` |
| 2 | 找有潜力的论文 → 做《两分钟论文》科普视频 → 发 B站/抖音 → 涨粉变现 | 公众/粉丝 | 看大众能不能懂 + 有没有传播力（可以与我们无关） | `video/SHORTLIST.md` + `video/scripts/*.md`（+ 后续视频） |

> ⚠️ 两个目的口径不同，选题必须分开（勿混，参照 news 线"口径分开"的教训）。

通用目的：为《超级智能2035》（作者刘杨/Foam）提供一手论文与科普素材；只搬运事实 + 忠实摘要，不生产观点。

产出（按用途分目录）：
- 日报/台账（原有）：`research/<YYYY-MM-DD>.md` · `SEEN.md`（主键 arXiv ID）· `INDEX.md` · `papers.jsonl` · `ARXIV_API.md`；
- 借鉴（目的 1）：`research/TOP_K.md` · `TOP_K.jsonl` · `TAKEAWAYS.md`；
- 科普视频（目的 2）：`research/video/SHORTLIST.md` · `research/video/scripts/<arXiv_ID>.md`（+ 后续成片，大文件不入 git）。

---

## 0.1 什么是「可收录的论文」（入账判据 · 硬性）

> ⚠️ 本线只收"一手论文"。不满足下面 4 条的一律不算（可另单列为"相关报道"，不进论文台账）。

可收录论文 = 「arXiv 上的、与关注领域相关的、可核验的一手论文」。4 条必须同时成立：

| # | 判据 | 说明 |
|:--|:--|:--|
| 1 | 来源 | arXiv（一手预印本）；必须给 `arXiv ID` + `abs` 链接（有 pdf 也给）。其它一手源（OpenReview / ACL Anthology）须显式标注。 |
| 2 | 时效 | `published`（首次提交）≤ 72 小时（日报口径）。陈年经典不算（除非 supervisor 点名）。<br>⚠️ 例外：arXiv 周末不公告（见运维指令 R2′）→ 落在周末/周一早时，可放宽到「最近一次公告批次」并如实标注实际日期区间。 |
| 3 | 可核验 | 齐备：`arXiv ID` + `标题` + `作者` + `提交/更新日期` + `主分类` + `链接`。 |
| 4 | 领域相关 | 命中 §1 关注领域。 |

典型反例（不进论文台账）：博客解读 / 媒体转述 / 二手综述 / 知乎推文 / 公众号文章
（若要留，放日报文末「附录 · 相关报道」并标 `🏷 类型：report`，不计入论文数）。

---

## 1. 关注领域（Watch List）

> 每轮由上到下逐领域检索；没有就如实写"本领域无新增"，不要凑数。查询清单应固化进脚本/配置（R2）。

| # | 领域 | arXiv 主分类 | 收什么 | 建议查询词 |
|:--|:--|:--|:--|:--|
| 1 | LLM | cs.CL · cs.LG | 预训练/规模律/指令微调/RLHF/推理/长上下文 | `large language model`、`scaling law`、`reasoning` |
| 2 | SLM（小模型） | cs.CL · cs.LG | 小模型/端侧/蒸馏/量化/高效推理 | `small language model`、`on-device`、`distillation` |
| 3 | 多模态 | cs.CV · cs.MM · cs.CL | VLM / MLLM / 图文视频理解 / 生成 | `vision-language model`、`multimodal`、`MLLM` |
| 4 | agent harness | cs.SE · cs.AI · cs.MA | code agent / tool use / harness / 评测基准 | `agent`、`tool use`、`SWE-bench`、`terminal-bench`、`multi-agent` |
| 5 | 邻域（可选） | cs.AI · cs.LG | RAG / 评测 / 对齐安全（仅当与 1–4 强相关） | `retrieval augmented`、`benchmark`、`alignment` |

> ✅ 关注领域可被 supervisor 修改（改本表即可）。

---

## 2. 每轮采集 SOP（每次唤醒照此执行）

1. 读现状：`MEMORY_RESEARCH.md` 顶部快照 + `research/SEEN.md`（已收录，避免重复）+ 当日日报（已写部分）。
2. 定窗口：确认上次采集时间（见流水）→ 本轮优先覆盖上次之后的新提交。
3. 逐领域检索：对 §1 每领域跑查询（`sortBy=submittedDate&sortOrder=descending`）；
   ⏱ arXiv 礼貌限速：请求间隔 ≥ 3 秒；单轮查询总数受控（建议 ≤ 12 次）。
4. 筛与去重：与 `SEEN.md` 比对 arXiv ID（主键）→ 命中即跳过；只留命中 §1 且满足 §0.1 的条目。
5. 落盘：新条目追加到 `research/<YYYY-MM-DD>.md`（§3 格式）+ 写入 `research/papers.jsonl` + `SEEN.md`。
6. 更新：`research/INDEX.md` 计数；`MEMORY_RESEARCH.md` 快照 + `WAITING`；当日流水。
7. 提交：`git add` 只加本线文件（`MEMORY_RESEARCH.md` `research/` `daily-memories-research/`）→ `commit -m "research <date> <n> 篇"` → `push`。

> ⏱ 不要 sleep / 不要等待：一轮做完就更新记忆并退出（loop 按 `WAITING` 决定何时唤醒下一轮）。

---

## 3. 输出格式

### `research/<YYYY-MM-DD>.md`（当日日报）

```markdown
# 论文日报 · <YYYY-MM-DD>

> 采集窗口：<上次时间> ~ <本次时间> ｜ 本轮新增：<n> 篇 ｜ 查询数：<m>

## 1. LLM
- **[标题]**（arXiv:<ID>，<提交/更新日期>）
  作者：<前 3 + et al>
  分类：<primary_category> ｜ 🏷 领域标签：<LLM/推理/长上下文…>
  一句话摘要：<中文，1~2 句，忠实原文，不抄整段>
  🔗 abs: <...> ｜ pdf: <...>
  （可选）💻 代码：<...>

## 2. SLM（小模型）
- ...（无新增则写：_本领域无新增_）
```

字段硬要求：`arXiv ID` + `标题` + `作者` + `日期` + `分类` + `🔗 abs` 缺一不可。

### `research/daily/<YYYY-MM-DD>.html`（⭐ P0 · 每天 5 篇推荐 · 早 3 晚 2 · 见本区顶部「第 4 批」块）

> 这是本线当前 P0 交付物；`research/<YYYY-MM-DD>.md`（下方）降为配套台账，两者可内容不同口径（md = 采集流水；HTML = 精选推荐）。

```text
结构（自包含单文件，内联 CSS，零外链，离线可开）：
┌ 页头：日期 · 早报/晚报 · 今日进度 3/5 → 5/5 · 数据源(arXiv) · 生成时间 · 免责「推荐 = 待读线索，非结论」
├ 5 条推荐（每条 8 字段：序号 / 原题 / 中文一句话 / 作者机构 / 日期 / 分类+标签(借鉴|科普) / arXiv abs 链接 / 推荐理由）
├ 附录：本轮检索式与命中数（可核验）· 去重剔除条数
└ 18:00 轮追加：## 晚报变更说明（AM → PM）—— 逐条写「改了什么 / 为什么」
```

硬性：① 当天合计 5 篇（3 + 2），宁少勿凑并写明原因；② 每篇必须有实测证据（`HTTP 200` + `XML` + 有 `published`）；③ 与 `SEEN.md` / `papers.jsonl` / `TOP_K.jsonl` / 近 7 天 `daily/` 不重复；④ 每轮必须提交 `research/daily/`（HTML 是交付物 ⇒ 必须入 git）；⑤ 顺手维护 `research/daily/index.html`。

### `research/SEEN.md`（去重台账）

```markdown
# SEEN — 已收录论文去重台账

| 首次收录 | arXiv ID | 标题 | 主分类 |
|:--|:--|:--|:--|
| 2026-10-03 | 2609.xxxxx | <标题> | cs.CL |
```

### `research/papers.jsonl`（结构化台账，一行一篇）

```json
{"arxiv_id":"2609.xxxxx","title":"...","authors":["..."],"submitted":"2026-10-02","updated":"2026-10-03","category":"cs.CL","areas":["LLM"],"summary_zh":"...","abs_url":"...","pdf_url":"...","first_seen":"2026-10-03"}
```

---

## 4. 操作要点（禁令见文首「📋 禁令总表」，本节只讲**怎么做**，不复述禁令）

1. **限速**：arXiv 请求间隔 ≥ 3 秒；单轮查询数受控；不并发打爆。
2. **校验**：`Content-Type: XML` + 真实 `published`；拿到 HTML/404/空 feed 判失败并记录，**不算「无新增」**。
3. **PDF 下载**：先验 `Content-Type: application/pdf` + 文件头 `%PDF`；单轮 ≤10 篇。
4. **大文件（≥5MB）走网盘**：首选 `bypy`，备选 `BaiduPCS-Go`；把 路径/提取码/文件名 登记进 `research/INDEX.md`。
   - `research/pdf/`、`research/raw/`、`research/video/` 须有 `.gitignore` 规则；`git add` 前用 `git check-ignore -v <file>` 自查。
   - **元数据仍要入 git**：清单里记 路径 / 字节数 / sha256 / 存放位置 —— 数据本体不进 git，但「账」必须在 git。
   - 网盘也不可用 ⇒ 宁可不传（本地保留 + 清单登记 + `MEMORY_RESEARCH.md` 写「未上云」）。
   - 📌 现状：`research/raw/topk-fetch.json` ≈2.7MB 可留 git；PDF 一律只存链接 + 网盘路径。

---

## 5. 记忆维护（硬性）

> 理由：`MEMORY_RESEARCH.md` 每次唤醒都被 agent 全文读取 → 越大越烧 token。

- 上限（两者相同）：`MEMORY_RESEARCH.md` 与本线任务书 `WATCH_RESEARCH_TASK.md`（全文=prompt） 均 ≤ 32KB（红线 40KB）；一旦超限即执行滚动。
- 任务书自己滚（2026-10-06 用户裁定）：任务书的归档由本线 agent 自己做（与 MEMORY 同机制），不再依赖 supervisor —— 只把「已闭合」的历史轮次 / 已执行完的运维块【原文】搬入 `run/WATCH_RESEARCH_TASK_ARCHIVE.md`（留 1 行指针；不新增/不改写任何指令，本区作者仍是 supervisor）。
- 滚动：把较早的流水条目（保留最近 ~20 条）追加到 `daily-memories-research/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 /「进度快照」③ 「运维问答」④ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---

## 6. 附录 · 相关文件

- 本项目总纲：`../README.md`；supervisor 记忆：`../MEMORY.md`；agent 总表：`../AGENTS.md`。
- 姊妹线（范式与铁律来源）：`WATCH_NEWS_TASK.md`（news 线）+ `watch_news_loop.sh`。
- arXiv API：文档 https://info.arxiv.org/help/api/user-manual.html ｜ 端点 `http://export.arxiv.org/api/query`


