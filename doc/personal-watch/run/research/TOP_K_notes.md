> 说明：以下是**人工**对 TOP-5 的「为什么与我们在研工作相关」，3–5 句/条；
> 全部基于**标题 + 摘要 + arXiv comment**（未整篇精读），判断类语句标「**我们判断**」。
> 生成器每次重跑都会**自动嵌入本文件**（`--notes-md`），因此可与 `TOP_K.md` 保持一致。

- **#1 ExecCritic（2609.09133）**：它把**测试构造**与**代码修复**拆成两个角色，用 `test→verify→revise` 脚手架 + 角色化 RL 训练，正对口 ZhuLong 的 **generate–execute–refine 执行闭环** 与 **code agent** 方向；
  摘要明确 point out「patch 与 test 由同一轨迹生成会**同错而同信**（false confidence）」，这恰是我们在 EDA 代码任务里做**执行反馈可信度**时最该防的失效模式。**我们判断**：其「fail-closed harness 冻结测试」的设计可直接借鉴为 ZhuLong 的评测/判分护栏；
  有官方代码（`github.com/msr-orchard/execcritic`）与 35 页 tech report，属**可复现**的高价值条目。

- **#2 Rethinking Multi-Image Re-Representation（2609.39363）**：它把**多图理解**统一为「重表征」，并把 **prompted CoT** 与 **agentic 视觉工具调用**当作同一枚硬币的两面——这与 BaiZe 的 **多模态对齐** 与 ZhuLong 的 **工具/MCP** 两条线同时相交；
  其 **Mosaic** 用 10 个**可组合图像算子**主动构造视觉中间产物，本质上是「视觉侧的 harness」。**我们判断**：其新基准 **MosaicBench** 的「细粒度 grounding」评测口径，对 BaiZe 多模态对齐的验收有参考价值；代码在 `github.com/gengyuanmax/mosaic`。

- **#3 PainterBench（2609.34195）**：把人类**未完成图形发散思维**任务搬到 agent 场景：agent 经**工具调用**作画、每轮观察结果、自行决定何时收笔——是**工具使用 + 增量视觉规划**的干净基准；
  对 ZhuLong 的 **评测基准（SWE-bench 类）** 与 **工具/MCP** 很有启发：它展示了「开放式、无 golden answer、过程可观测」的任务如何被**可评测化**。**我们判断**：其「agent 自我终止」机制对长程 EDA 任务的**停止准则**设计有借鉴意义（25 页 / 7 图 / 11 表，规格扎实）。

- **#4 One to More, More to One（2609.23377）**：针对仓库级 SWE 的**类别跷跷板**（RL 后部分类别涨、部分类别退）提出**类别感知的专家训练 + 策略融合**，直击 ZhuLong **SWE 类 agent** 与 BaiZe **后训练（SFT/RL）** 的共同痛点；
  其「Executable task construction + SWE Labeler 多轴标注」把训练池**证据化组织**，方法与我们的**数据配比/可执行任务构造**诉求高度一致。**我们判断**：这是本轮**最贴近 ZhuLong 主线**的候选之一，且放出了 `Logics-SWE-Qwen3.6-27B` 权重与 44 页附录，**可复现性最强**。

- **#5 Faynt（2610.02144）⚠️**：它用 **10M/75M 参数的 Transformer 策略**+RL 在《任天堂明星大乱斗 Melee》上做到 98.4% 胜率，**代码/方法/机构(NVIDIA)/54 页**四项代理全中，故 `q=4.0`。
  **但须诚实标注**：这是**游戏 RL 的策略缩放**，与 LLM/SLM 主线的相关性**仅停留在「规模律 / RL 后训练 / 高效推理」这类泛词命中**——**我们判断**它很可能是**词表过配（over-match）**，建议人工降权。
  → **复核提示**：若按「与两条线的真实相关度」手排，**#18 Sharpening Tax in Post-Training（2610.01509）** 的优先级应更高：它发现**预训练 LLM + 轻量 inference harness 即可是能干 agent，且 pass@K（解空间覆盖）常胜过 post-trained 版本**——对 ZhuLong 的 **agent harness** 与 BaiZe 的 **后训练** 都是**反直觉且高信息量**的结论，只因缺 `code/org/comment` 代理而 `q` 偏低。