#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第五十四轮落盘脚本：从 fetch-r54.json 生成 papers.jsonl 新增行 + SEEN.md 行。
收录集（RECORDED）为人工精选 34 篇（含中文摘要 SUMM）；其余 181 篇记为候选。
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(BASE)

FETCH = os.path.join(BASE, '2026-10-06-fetch-r54.json')
FIRST_SEEN = '2026-10-06'

SUMM = {
"2610.06750": "指出循环-注意力混合 LM 虽同时具备两条记忆通路，实际却明显更依赖注意力、循环状态利用不足，SFT 也只提整体性能而不改善两者协调；提出辅助损失——在循环状态传播全序列时限制注意力对早期上下文的访问——促使模型经循环通路保留/利用信息，在长上下文与聚合任务上增益最大，并泛化到多种混合 LM 与 agentic 任务。",
"2610.06387": "综述 LLM 规模理论从经验规模律到计算最优训练（Chinchilla 路线）的演进，聚焦参数效率、token 利用、数据效率与资源受限环境，梳理剪枝/高效架构/量化/LoRA/端侧优化；主张未来应以「性能-参数量-计算成本-token 分配-硬件约束」的关系而非单看性能衡量效率，并指出既有规模律是否适用于小模型与受限算力仍存空白。",
"2610.06647": "用低秩梯度草图保留有用学习信号以降低 RL 后训练显存，这些紧凑表示同时支持模型更新与高效策略同步；为防过大更新扰动，配合「预测-KL 步长控制」在应用更新前估计策略变化并调节幅度。推理任务上平均降训练显存最多 45.7% 而不损性能，并能在单 8 卡节点稳定训练 27B 模型 1100+ 步（dense Adam 会 OOM）。",
"2610.06479": "主张 KV 缓存压缩应以「保持全缓存模型的预测行为」为目标，而非依赖注意力质量等代理信号：按移除某条目后诱导的压缩缓存 logits 与全缓存 next-token 分布的 KL 给候选评分；利用逐出前的前向统计避免为每个候选单独跑掩码前向。在同保留预算下优于轻量注意力启发式，激进压缩增益最大，仍保持端到端加速。",
"2610.06286": "指出现有一站式 KV 压缩多在 prefill 后立即不可逆逐出、早于任何生成信号；定量分析显示真实生成阶段的首个查询给出的注意力信号与后续解码更一致，最大单步增益恰在 prefill-decode 边界。据此提出 DeferKV，把逐出决策从 prefill 末移到首个解码步并时间上融合 prompt 侧与 decode 侧观测，无需额外训练/draft 模型；LongBench/RULER/NIAH 稳定提升且保持低延迟。",
"2610.06031": "NTP 仅对即时下一 token 给显式监督，易诱使模型利用局部模式；现有 MTP 引入大量新参数而下游收益有限，latent MTP 又靠外部 helper 编码未来 token。提出 LightMTP：直接从模型自身隐状态 bootstrap 未来 token 表示，无需额外算力或外部监督，仅增加 ≤1% 参数即可把监督扩到更多未来 token，在通用语言建模与规划/编码/推理上取得相近收益。",
"2610.06026": "SVD 剪枝+量化通常两阶段解耦、各自优化，难以平衡、激进压缩下性能次优。提出统一框架「可微 bit-width」：让不重要分量被分配到 0-bit 精度，从而在单一框架内协同优化剪枝与量化，在极端压缩下取得更优性能。",
"2610.05977": "面向「一份权重流服务多精度」需求：主流量为 2-bit 分块仿射基，后接可配置数量的 1-bit 精化平面（二进步长），每个支持的精度都是可读前缀，由共享元数据派生的仿射映射解码、无逐权查表；稀疏 side record 存放网格最难拟合的少数权重。2/3/4-bit 下在 Llama-3.1-8B、Phi-4、OLMo-2-7B 多数领先多精度基线，A100 上 batch-1 matvec 内核多数情形更快。",
"2610.05966": "主张领域自适应可走「纯 RL」而非 SFT+RL（后者降低探索多样性、多阶段复杂）；指出纯 on-policy RL 存冷启动、混合策略 RL 又陷「梯度饥饿（有价值低概率教师 token 学得慢）」与「教师分布锚定（陈旧教师阻碍后期提升）」。提出 One-stage Policy Optimization (OnePO)：把教师输出当瞬时引导，用自适应目标演化强化有价值低概率教师 token 的学习、用教师退休在策略超过教师后丢弃其输出。医学适配仅 20K 样本得 HealthBench 67.2；27B 版 HuatuoGPT-3 达 HealthBench 70.1 / Professional 71.4。",
"2610.06804": "模型可给正确答案更高概率却仍常采样到错误答案（错误答案概率之和更大）。power distribution 把完整答案概率取幂再归一以「锐化」，采样可提推理但每查询需多次打分候选。提出 on-policy power distillation（OPPD）：用序贯蒙特卡洛采样器，由被训模型生成候选、冻结教师的 power distribution 加权，并把同样概率用于最大似然更新，使模型单次生成即产出这类答案；MATH500/GSM8K 上较未训模型单次生成大幅提升，与 GRPO 互补、可训练后再叠加。",
"2610.06817": "把 54 声的 Kokoro-82M 蒸馏为只说其中一声的 8.07M 参数模型 Paradee：保留教师架构但大幅收窄层，两半各自对冻结教师单独训练；先用教师合成语料并保留其时长/音高/能量/音素特征，再训小文本侧预测这些值、训小解码器把教师保存的值还原为教师音频（先谱损后对抗），最后连接两半并 int8 量化。int8 仅 8.5MB、单 CPU 线程 25× 实时、UTMOS 4.41（教师 4.52）；并将 2–8kHz 嗡嗡声定位为浊音相位问题，用后置相位锁定滤波消除。",
"2610.05126": "研究数据受限预训练中「重复次数」随模型规模变化：在固定目标语料占比、混入通用数据下，测量到的重复次数排名随模型规模改变，520M 的 Proof-Pile-2 实验证明把重复从 16 降到 8 既降 loss 又用更少训练 token。提出先用若干小模型的 loss 曲线保留一份「候选重复次数短名单」再在大规模上评估（PubMed/Caselaw 上 200M 与 520M 均保持最低 loss 项），并把该现象关联到一个含两项相反重复依赖 loss 的经验规模模型，其一阶展开即选择规则所用的线性形式。",
"2610.04950": "on-policy 蒸馏（OPD）用学生在自生成轨迹上的 token 级教师监督提升小模型推理；但独立擅解题的教师未必会有效引导——当学生前缀偏离教师路径或含错时，教师从这些前缀续写的准确性下降。提出 Prep-OPD：蒸馏前先用 RL 训练教师去适应学生已有推理状态并在出错时纠偏，训练以固定学生前缀、用最终答案正确性为奖励优化教师续写。",
"2610.06204": "用 GRPO 在程序化效用奖励上训练四个 Gemma 4 检查点（2.3B–31B 有效参数）做双边多议题议价，并在同一批 1152 场谈判、对两个训练未见的买方评估。相同学习率下 RL 相对基座的增益随规模由 +0.001(2.3B) 升至 +0.078(31B)；学习率翻三倍（训练步数相同或更少）在各规模都更好（+0.032~+0.081）；结论是应先调好学习率再断言小模型学不会议价，并用不止一个模型族的买方测试。",
}
SUMM.update({
"2610.06830": "指出多数 agent 记忆系统以 query-agnostic 方式构建记忆，既造成多余预处理开销又丢弃后续关键细节；提出 MemPilot 按「性能–成本–延迟」偏好编排按需记忆整理：用 RL 优化多步 LLM 策略，在「从 query-agnostic 记忆检索」与「把原始多模态历史委托给异构 LLM/VLM 做 query-specific 整理」之间迭代选择，联合控制证据量、整理指令、模型选择与视觉访问；用「目标分离的优势估计」与「前缀边际效用」做细粒度信用分配，在五个多模态 agent-memory 基准上取得更优权衡。",
"2610.06616": "探问能否用图像表示搭紧凑视频编码器：解耦「逐帧表示 / 跨帧 token 分配 / 时序交互」三操作——冻结图像编码器产逐帧候选，问题感知选择器按相关性/多样性/跨帧对应在帧间分配固定 token 预算，轻量 refiner 只对保留锚点写残差更新。13 基准 × 3 视觉语言骨干下以约 28–35% 视觉 token 匹配满图聚合性能（Qwen3-VL-8B 上 1,535 token 得 62.75 vs 满图 4,424 token 的 62.58），Qwen3-VL-32B 上还有 2.16× 端到端加速。",
"2610.05940": "通过探测实验指出现有流式视频 VLM 随输入增长逐步丢失长上下文信息；提出免训练适配技术 ReMem，从两视角利用记忆：流式上下文记忆（SCM）用 query 无关注意力持续压缩历史上下文，检索视觉记忆（RVM）再取最显著、query 相关的上下文增强 VLM 输入，从而处理任意长度流式视频并提升长上下文保留，在流式与通用长视频基准上达 SOTA。",
"2610.05861": "GUI agent 训练依赖大量高保真视觉-动作轨迹但极难获取；现有 GUI world model 靠文本描述或 HTML 渲染、丢弃图标与布局等像素级细节。提出 Infinite-Dreamer：把 GUI 状态转移当作「图像编辑」任务，用 VLM 把动作引起的 UI 变化描述为结构化 delta-text，再微调图像编辑骨干可控合成真实截图转移，生成单帧视觉鲁棒数据与多步想象轨迹。仅用合成数据微调 Qwen3-VL 得 Infinite-Actor，在 AndroidWorld/MobileWorld/AndroidControl-Curated 上跨规模稳定超越基线。",
"2610.06056": "LVLM 常出现目标幻觉；经验分析发现幻觉 token 并非单纯过度依赖语言先验，而是在中间层对文本与视觉上下文的相似度都异常偏低（上下文偏离）。提出 ROT：层特定、免训练框架，在中间层动态检测语义偏离并用保范旋转把隐状态旋回由上下文张成的局部多模态上下文平面，后续层再加表示平滑稳定校准轨迹；多基准/多架构一致降低幻觉。",
"2610.06672": "长视频理解需跨长时段检索分散信息、对记忆压力大；现有「query 驱动探索」对定位误差敏感、「记忆构建」又可能丢弃后续有用细节。提出 VideoTapestry：query-自适应记忆精炼的多 agent 框架，兼顾两类范式（详见原文）。",
"2610.06790": "指出现代 AI 依赖数十亿晶体管 SoC，而其验证流程仍高度手工；约 74.6% 的 EDA LLM 研究聚焦静态 RTL 代码生成，后仿真验证与交互式波形调试几乎空白。提出端到端 agentic 框架 Back-to-the-Future (BTTF)：把海量非结构化仿真 dump 蒸馏为规范化关系型 SQLite 数据库，配多 agent 协作编排引擎，把自然语言验证查询翻译为 schema-aware SQL，并把信号异常与带版本 RTL 仓库关联；150 查询基准上执行准确率 95.33%。",
"2610.06597": "agent harness 懂工作流依赖、上下文生命周期与执行目标，推理引擎则掌握请求队列、KV 缓存状态、资源压力与执行能力，但现有接口未系统连接两层信息、限制工作流感知执行。提出双向 Harness–Engine Pairing 协议 HEAR：标准化 harness 如何表达工作流意图与执行需求、引擎如何回传运行时状态/能力/结果，并把协议语义与优化策略分离。内存受限并发服务下 SCBench 批量 1.61× 加速、中位 TTFT 降 2.23×，BrowseComp-Plus/DeepResearchBench 端到端 1.23×/2.45× 且无质量下降。",
"2610.06563": "LLM agent 能在复杂工具环境中行动，却常在任务不可行、无解时仍不弃权。提出 harness-环境协同演化框架 HERA：(i) 用受控环境变异把可解任务变为需弃权的案例，自动构造可验证的可行/不可行任务对；(ii) 用既往失败驱动 harness 适配并生成针对弱项的新环境与任务。演化后的 harness 把弃权准确率 61.7%→83.3%、可行任务完成 68.3%→76.7%，并跨 19 个 LLM 迁移、平均提弃权准确率 15.3 点，使小模型以约 85% 更低成本匹配强模型。",
"2610.05039": "Agentic Harness 是构建任务上下文、控制执行流的运行时，决定 agent 整体表现。现有 meta-harness 多为 proposer-centric，随历史膨胀 proposer 负担加重。提出 Causal Improvement Graph (CIG)：图治理的 meta-harness，把演化中的改进状态外化到持久图中，用 Evidence/Hypothesis/Intervention/Outcome 四类节点及其结构关系保存「观察到什么/如何解释/如何检验/评估揭示什么」，让局部 proposer 直接在既有发现的关系上构建。跨多任务发现更强 harness，且对 task solver 与 proposer 选择稳健。",
"2610.04921": "指出 agent harness 的测试充分性不足；提出 HarnessTester 提升真实世界 agentic 系统的测试充分性，取得显著行/分支覆盖率与变异得分增益，并在 OpenClaw 等广泛使用的系统检出 122 个真实 harness bug（88 个此前未知、69 个已被开发者确认）。",
"2610.05481": "面向冻结骨干下的多语言代码生成（执行、跨语言覆盖、污染控制难题）：多 agent 数据锻造（Composer/Reviewer/Executor/Curator 四 agent 迭代精炼 instruction-code 对、用测试验证、过滤重复与基准泄漏）、执行验证的强化指令微调（masked SFT + 测试驱动 RL 目标）、语言条件 LoRA 专家混合（稀疏路由提升跨语言迁移，推理时骨干不变）；数据/目标/适配器联合设计在多编程语言上稳健增益。",
"2610.05367": "研究级证明自动形式化常依赖 Mathlib 缺失概念，编译成功也不保证语义保真，且缺对齐 NL-FL 数据、依赖昂贵前沿模型与手工 harness。提出 AIProver：联合后训练 119B 开源模型与用 HarnessEvolve 演化其工具调用 harness——验证器评估类型正确性/证明完整性/语义正确性并回传奖励与诊断证书，驱动微调与 RL，HarnessEvolve 对整套 harness 控制流做证书驱动的演化搜索并随模型更新重裁。并发布 LoCoBench（58.9k 实例）。pass@4 语义正确率 15.7%→36.7%，作为 Claude Code/Codex skill 提升到 79.8%/62.4%，且比 Numina-Lean-Agent 便宜 24%。",
"2610.04975": "长程工具 agent 会创建子目标、重规划、委托并组合兄弟结果；逐工具权限检查无法保证变化的目标图仍在主授权任务内。形式化该授权缺口（有限结构域、一个 principal 与一个授权根）：每个目标图变更携带版本绑定 witness，证明其延续追踪/资源/义务/不变量/闭合条件 refine 活跃根契约，每个受保护效果在原子提交边界复核；自由文本目标不提供授权。证明多项保持性并给出可执行模型（340 状态/419 转移）与 96 匹配案例实验（48 漂移案例零违禁提交）。",
"2610.05833": "长跑 agent 反复调用 LLM 并滚动更新文档窗口（逐出旧文档、追加新文档），破坏精确前缀缓存、催生非前缀 KV 复用+选择性重算。发现该类复用可能「历史依赖」：同一未变 prompt 会因之前处理的请求不同而给出不同答案。匹配 5% 重算预算下，文档对齐重算把跨请求顺序的答案变化从 CacheBlend 的 token top-k 的 69.0% 降到 26.1%，对全 prefill 的保真度提升 34.5–52.5 点，二者都约 5.7× TTFT 加速；消融显示「连续性」是稳健选择性重算的主因。",
"2610.05094": "系统评估 10 个推理模型在不同设计（prompt/评分量表/模型）下的判断：评分任务上多数判官相对人工真值平均绝对偏差仅 0.11（1–7 分），分类任务平均准确率 96.5%；但设计选择会造成偏移（仅改量表可移动测量到的偏差达 0.93 分；详细 prompt 使 leniency 降 28.9 点、换模型最多降 56.1 点）；反直觉的是更低推理努力不影响准确率与 leniency；模型身份是方差主源。作为更稳健可复现判官设计的方法学参考。",
"2610.05190": "生成式 LLM 从预训练继承人口偏差、有害生成等不良行为，常仅在小部分输入上于部署后显现。提出验证门控的行为修复（verification-gated behavioral repair）：在消除已识别缺陷的同时保持模型整体功能，并力求给出正确性保证（详见原文）。",
"2610.06064": "把「信任」定义为助手愿接受他方行为带来的脆弱性：构建 2000 段跨能力/善意/正直的对比对话（配对回复完成同一请求但信任与否不同），在冻结模型参数下学习 steering 矩阵，跨三族六个指令模型验证可双向单调改变信任决策；该效应延伸到有害请求/提示注入/内鬼威胁等安全相关 agent 场景，表明「对用户的信任」可沿激活的线性方向被因果控制。",
"2610.05982": "LLM 路由常被简化为分类任务，当多个候选都能正确回答同一 query 时暴露脆弱性——作者形式化这种能力重叠为 routing noise（任意正确候选误导路由，导致「路由崩溃」即对未见任务泛化骤降）。提出 Cluster-Aware Soft-Labeling Routing (CASLR)：把评估从单 query 成败转为宏观域共识，用 masked softmax 替代 one-hot——对答错专家目标概率置零、对剩余候选按全局聚类效用计算连续细粒度软标签来监督轻量 router。多基准上较 Llama-3.3-70B-Instruct 平均高 7.80%，路由延迟仅 1.13s。",
"2610.06096": "在九个图像-文本-表格数据集上发现「多模态饱和」：加入第三模态反而损害性能（VICReg 下三模态模型在 55.6% 配对运行中劣于自身最佳双模态子集，SimSiam 下 51.1%），并主张失败源于对齐几何。提出 R-VICReg：用可学习负曲率乘积因子上的测地距离平方对齐视图，曲率趋零时精确退化为 VICReg；把第三模态有益的概率从 44.4% 提到 64.4%，增益集中在 VICReg 饱和处。",
})


def main():
    data = json.load(open(FETCH, encoding='utf-8'))
    items = data['items']
    by_id = {it['arxiv_id']: it for it in items}
    recorded = list(SUMM.keys())
    missing = [a for a in recorded if a not in by_id]
    if missing:
        raise SystemExit('RECORDED not in fetch: %s' % missing)
    rec_set = set(recorded)

    # ---- papers.jsonl 新增行（按报告顺序）----
    plines = []
    for aid in recorded:
        it = by_id[aid]
        rec = {
            'arxiv_id': aid,
            'title': it['title'].strip(),
            'authors': it['authors'],
            'submitted': it['published'][:10],
            'updated': it['updated'][:10],
            'category': it['category'],
            'areas': it['areas'],
            'summary_zh': SUMM[aid],
            'abs_url': it['abs_url'],
            'pdf_url': it['pdf_url'],
            'first_seen': FIRST_SEEN,
        }
        plines.append(json.dumps(rec, ensure_ascii=False))
    with open(os.path.join(RES, 'papers.jsonl'), 'a', encoding='utf-8') as f:
        f.write('\n'.join(plines) + '\n')

    # ---- SEEN.md 未收录候选/收录行（按 arxiv_id 降序）----
    rows = []
    for it in sorted(items, key=lambda x: x['arxiv_id'], reverse=True):
        aid = it['arxiv_id']
        status = '收录' if aid in rec_set else '候选'
        title = it['title'].replace('|', '/').replace('\n', ' ').strip()
        rows.append('| %s | %s | %s | %s | %s |' % (FIRST_SEEN, aid, title, it['category'], status))

    seen_path = os.path.join(RES, 'SEEN.md')
    lines = open(seen_path, encoding='utf-8').read().split('\n')
    # 定位「最后一行表格行」后再插入
    last_row = max(i for i, ln in enumerate(lines) if ln.startswith('| 2'))
    new_lines = lines[:last_row + 1] + rows + lines[last_row + 1:]
    open(seen_path, 'w', encoding='utf-8').write('\n'.join(new_lines))

    n_rec = len(recorded)
    n_cand = len(items) - n_rec
    print('papers.jsonl +%d ; SEEN +%d (收录 %d / 候选 %d)' % (n_rec, len(rows), n_rec, n_cand))


if __name__ == '__main__':
    main()

