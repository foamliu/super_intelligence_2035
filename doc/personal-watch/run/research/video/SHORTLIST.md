# 《两分钟论文》选题表 · SHORTLIST

> research 线 · 运维指令 2026-10-03 **第 3 批 B 节（V1）**。**目的 2** = 做**两分钟中文科普视频**发 **B站 / 抖音**（与「目的 1 借鉴」**口径分开**）。
> **筛选口径**：① **大众能懂**（有直观画面 / 反直觉结论）② **有传播力**（震撼结果 / 热门话题）③ **可讲清**（不必搬全篇）④ **有真实来源**（arXiv ID + 链接）。
> **候选池**：`research/SEEN.md` / `raw/2026-10-03-topk-fetch.json` 里 **≤30d** 的论文。**🚫 不为话题性曲解论文**；**🚫 不盗用论文原图**（画面自绘/自生成）。

**建议栏目名**：《两分钟论文》是**已有知名频道**，本线**须起自己的栏目名**（避免品牌混淆）——候选：《论文两分钟》/《两分钟读论文》/《Foam 读论文》（待用户拍板）。

## 候选（17 条，按「上手难度 × 传播潜力」粗排）

| # | 论文（arXiv） | 一句话看点 | 为什么大众会看 | 难度 | 建议平台 | 备注 |
|--:|:--|:--|:--|:--|:--|:--|
| 1 | **Faynt: Scaling and Optimizing Policies for Competitive Melee**（[2610.02144](https://arxiv.org/abs/2610.02144)） | 一个 **10M 参数小模型**用强化学习在《任天堂明星大乱斗 Melee》里 **244 局赢 240 局（98.4%）**，打遍 14 个专业 AI | 游戏 + 「小模型打败大专家」反直觉；对战画面直观 | **易** | 都 | ✅ 口播稿 `scripts/2610.02144.md` |
| 2 | **Codoku: Renewable Program-Reasoning Challenges for Frontier Coding Agents**（[2609.34661](https://arxiv.org/abs/2609.34661)） | 把「代码推理」做成**数独**：AI 要填一段**残缺程序**，而残缺程序**不能运行**，没法靠执行作弊 | 数独类比秒懂；「连大模型也只解一半」有话题 | **易** | 都 | ✅ 口播稿 `scripts/2609.34661.md` |
| 3 | **Moore, Escher, Penrose: A Conformal Golden Braid**（[2610.02210](https://arxiv.org/abs/2610.02210)） | 用扩散模型生成**埃舍尔式「画中画 / 无限循环」**自指画面 | 视觉震撼 + 艺术/数学名人（埃舍尔《画廊》）；画面极适合短视频 | **中** | 都 | ✅ 口播稿 `scripts/2610.02210.md` |
| 4 | **Tactile Curiosity Drives Robot Interaction**（[2609.40134](https://arxiv.org/abs/2609.40134)） | 给机器人「**触觉好奇心**」，让它主动去摸、去接触，而不是随机乱动 | 机器人「摸来摸去」画面萌、传播力强 | **易** | 都 | 待核全文（现基于摘要） |
| 5 | **AIR-LLM: Broadcasting AI Weights over Radio for Memory-Free Edge LLM Inference**（[2610.00465](https://arxiv.org/abs/2610.00465)） | 把大模型权重用 **5G 广播「发到空气里」**，边缘设备**边收边用、不存不加载** | 极反直觉（「模型在天上飞」），画面感强 | **中** | 都 | 概念性强，**须严格不改写结论** |
| 6 | **FIGS: Evaluating Multi-Turn Sycophancy Without Penalizing Empathy**（[2609.39863](https://arxiv.org/abs/2609.39863)） | 多轮聊天里 AI 会「**越聊越顺着你**」；新基准测谄媚，但**不把共情当认输** | 「AI 拍马屁」人人有感 | **易** | 都 | 可做互动式演示 |
| 7 | **LLM Persona Unlearning**（[2609.39882](https://arxiv.org/abs/2609.39882)） | 从**权重层面**「删掉」模型里某个人格角色，让它再难被提示词唤起 | 「给 AI 做记忆/人格删除」反直觉、隐私话题 | **中** | B站 | 涉及安全，措辞需谨慎 |
| 8 | **Anti-Persona: Disrupting Unauthorized Identity Binding**（[2610.01944](https://arxiv.org/abs/2610.01944)） | 给照片加一层「**反人脸绑定**」扰动，阻止别人用几张照片把你的脸「绑」进个性化模型再识别 | 人脸隐私，人人相关 | **中** | 都 | 需正确区分「防御」与「攻击」 |
| 9 | **RSIGame: Autonomous Agentic Game Development with Recursive Self-improvement**（[2609.39045](https://arxiv.org/abs/2609.39045)） | 让 AI agent **自己循环**「探索-诊断-改进」地做游戏、自我进化 | 「AI 自己做游戏」话题性强 | **中** | B站 | 可展示小游戏 demo 画面 |
| 10 | **DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression**（[2609.19969](https://arxiv.org/abs/2609.19969)） | 把大模型「记忆缓存」压到约 **1/4**、每 token 仅 **890 字节**，长文本更省显存 | **DeepSeek** 热度高；「给 AI 记忆瘦身」可类比 | **中偏难** | B站 | 工程细节多，需翻译成「人话」 |
| 11 | **Sharpening Tax in Post-Training**（[2610.01509](https://arxiv.org/abs/2610.01509)） | 反直觉：后训练让单题更强，却让「**解题覆盖面**」变窄；没后训练的模型**多试几次反而更强** | 颠覆「后训练 = 变强」的常识 | **中** | B站 | 结论硬核，适合科普向受众 |
| 12 | **LongEmo: Towards Emotion Understanding and Reasoning in Long Videos**（[2609.40079](https://arxiv.org/abs/2609.40079)） | 让 AI 看懂**长视频里情绪的累积与转折**（不只是单帧表情） | 影视解说 / 影迷受众广 | **中** | B站 | 可用经典电影片段示意（自绘/授权素材） |
| 13 | **Mem++: Non-Destructive Memory for Long-Term Organizational LLM Agents**（[2610.02002](https://arxiv.org/abs/2610.02002)） | 给 AI 装「**不破坏原文、按需检索**」的长期记忆，能答「某年某月哪个决定有效」 | 「AI 记忆」热门；可类比「公司档案」 | **中** | B站 | — |
| 14 | **Sphere Encoder 2**（[2610.02208](https://arxiv.org/abs/2610.02208)） | 从高维「**球面**」上随机取点解码成图，修掉原版「赤道聚集」与「模糊」两处缺陷 | 视觉生成话题，画面直观 | **中** | B站 | 数学感偏强 |
| 15 | **PainterBench: A Figural Divergent-Thinking Benchmark for Tool-Using Language Models**（[2609.34195](https://arxiv.org/abs/2609.34195)） | 给 AI 一个**不能擦的残缺图形**，让它用工具一笔笔画完，考「发散创造」 | AI 画画 + 「创造力」话题 | **易** | 都 | — |
| 16 | **One Basis to Animate Them All: Gaussian Blendshape Distillation for Real-Time Avatars**（[2610.02207](https://arxiv.org/abs/2610.02207)） | 把 3D 高斯**虚拟人**的实时动画蒸馏成线性「表情基底」，更省算力 | 数字人 / 虚拟主播热门 | **中** | 都 | — |
| 17 | **Qwen-Audio-3.1-Realtime: Towards Reliable Agentic Voice Interaction**（[2609.25176](https://arxiv.org/abs/2609.25176)） | 实时语音助手「**会思考、会调工具、还知道何时该闭嘴**」，嘈杂背景误应答大降 | 语音助手人人用；「该不该接话」有意思 | **中** | B站 | — |

## 本批 TOP-3 选题（→ 已写 V2 口播稿）

1. **#1 Faynt（2610.02144）** — 游戏 + 小模型反直觉，**传播力最强 + 最易讲**。
2. **#2 Codoku（2609.34661）** — 「代码数独」类比天然，**反直觉（不能靠运行作弊）**。
3. **#3 Moore, Escher, Penrose（2610.02210）** — **视觉最震撼**（埃舍尔式循环画面），B站美学/科普受众广。

> 口播稿见 `scripts/2610.02144.md` · `scripts/2609.34661.md` · `scripts/2610.02210.md`。
> **V3（视频生成）**：**待用户/supervisor 确认运行机工具链（TTS / 文生图 / 剪辑）后再动**，本批不做。

## 红线复核（每条脚本都须过）

1. 🚫 **不盗用论文原图** —— 画面自绘/自生成；引用观点标出处。
2. 🚫 **不夸大** —— 「SOTA / 颠覆 / 突破」**须有出处**；**不编造数据**。
3. ✅ 必须标明「**论文解读**」；必须给 **arXiv 链接**（口播说「链接放简介」）。
4. 🚫 **不为话题性曲解论文**（宁可不做，不可失真）。
5. 📦 **大文件不入 git**（成片/音频/图片 >20MB 走外部目录并记清单）。