#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十二轮落盘（2026-11-10 AM：11-09 晚报补跑 2 篇科普 + 11-10 早报 3 篇借鉴）。"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-10-am-idlist-r142a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.09204': '2026-11-10', '2611.09807': '2026-11-10', '2611.09412': '2026-11-10',
         '2611.09729': '2026-11-10', '2611.09802': '2026-11-10'}
AREAS = {
    '2611.09204': ['表征漂移', '载体神经元', '预注册', '消融对照', '可解释性', '剪枝', '训练动态'],
    '2611.09807': ['对话记忆', '压缩 vs 检索', 'RAG', '配对检验', 'McNemar', '上下文成本', '负结果与功效', '延迟分位数'],
    '2611.09412': ['线性时间架构', 'SSM', 'IIR', '极点几何', 'lattice-ladder', '长上下文外推', '吞吐'],
    '2611.09729': ['评测可靠性', 'Monte Carlo', '重复运行方差', '分层指标', '成本与啰嗦度'],
    '2611.09802': ['AGENTS.md', 'CLAUDE.md', '文档债', '指令过期', '轨迹级评测', '静默失败', 'tool call 成本'],
}
SUMMARY = {}
SUMMARY.update({
    '2611.09204': '在 OpenCoder-1.5B 的 2.03 万亿 token 预训练记录上（恒定学习率、每 1,000 step 一个 checkpoint），追踪 169 个 Python 语言构造的「载体神经元」（每层 MLP 中对该构造区分度最高的 5%）。对 16 个「语法决定下一 token」的构造，强制位置上的 loss 在训练前 4%（84B token）即到地板，之后 96% 训练几乎不动（24 条序列 20 平 / 4 升 / 0 降）；但载体集合 169/169 到最后 checkpoint 仍在变（注入「突然安顿」检出 99.1–99.4%，逐步安顿在 500B 前检出 99.4–100%，未注入序列零误报）。把 84B 时的旧载体在终点挖掉，抬升 loss 与随机同尺寸集合不可分（0.14 nats，95% CI [−0.01, 0.42]，14 个里 10 个占优，p=0.09）；挖当前载体为 0.40 nats（16 个里 14 个显著）。退出某集合的神经元回归率是同条件神经元的 3 倍，但没有集合会原样重组。作者预注册的「载体会安顿」假设被自己的数据否掉。⚠️ 单一模型/单语料/恒定学习率，作者明确不可外推到其他模型或训练配方；本线未复现。',
    '2611.09807': '比较两种对话记忆：RAG（保留原始对话轮次、检索原话）与两层压缩记忆（每轮抽成原子事实、按轮数指数衰减、检索即强化、并把命中的事实回填其来源轮次）。两臂在同一窗口、同一存储、同一生成器与同一 judge 下回答 LoCoMo 全部 1,985 题（841 open-domain / 446 adversarial / 321 temporal / 281 single-hop / 96 multi-hop），两臂预测写在同一行 ⇒ 在 512 个分歧题上做 McNemar 精确检验（两臂在 1,473 题上一致）。四个可比类别：压缩 71.4% vs 64.6%（+6.8pp，p=5.5e-08），prompt token 少 34%；五类全算则仅 +2.0pp 不显著（对抗类 −14.6pp）。梯度：参考答案只需 1–2 个原词时压缩 +9.6pp，超过 8 个词时 −3.1pp，token 重叠同向 ⇒ 非 judge 所致。作者还撤回早先「慢数倍」的延迟结论：非配对比较的均值差全在尾部（p50 1,741 vs 1,769 ms；p99 28,348 vs 12,149 ms；两侧最大值都约 93.8s 为供应商重试）。另报四个带功效计算的负结果。⚠️ LoCoMo 为合成长对话、judge 为模型判分、事实抽取质量依赖抽取器；本线未复现。',
})
SUMMARY.update({
    '2611.09412': '把 Mamba（选择性 SSM）、RWKV、RetNet 等线性时间循环架构统一刻画为 IIR（无限脉冲响应）系统：其零极点几何决定可表示的时间模式；但为并行度，这些参数化常把极点约束在实轴，丢掉复共轭极点对应的振荡模式，构成架构偏置。作者借一般 IIR 的 lattice–ladder 实现提出 MIRA：每个 block 实现高阶 IIR，同时表示实极点与复共轭极点，并保持线性时间与分块并行。预训练 MIRA-S（12 层、宽 768、0.14B、训练上下文仅 512 token）在 FineWeb-Edu 上全程 PPL 低于 Mamba-1(S6)/Mamba-2(SSD)/RWKV-6/RWKV-7 且 next-token 准确率更高；评测上下文拉到 32,768（64×）仍最低 PPL，并与 RoPE 版 MHA（含 YaRN）持平或更好。专用 CUDA kernel（RTX A6000）32K 前向 11.37 ms（对 MHA+FlashAttention/Mamba S6/RWKV-6/RWKV-7 为 4.13×/1.32×/2.15×/2.85×），吞吐 8.36M tok/s（6.41×/2.20×/1.02×/1.28×）。消融：lattice 阶 K=2 优于 K=1（纯实极点）；写入门控瓶颈 d_r=d/8 最低 PPL。⚠️ 0.14B / 单语料 / 训练上下文 512 / 专用 kernel，不能直接外推到 2B 与本机硬件；本线未复现。',
    '2611.09729': '指出「一次跑多少分」的评测无法区分能力不足与抽样波动。构造 DS-QA：100 道大学课程级数据科学题，覆盖 16 个数据集、9 个维度、3 个难度；三层指标（通用：运行时长/啰嗦度/文本相似度；粗粒度：准确率/代码可执行性/完整度；任务特定共 35 项）。采用 Monte Carlo 协议：同一题在相同条件下重复 100 次（评测子集 41 题，GPT-4o 等 OpenAI 模型，temperature=1），用分数标准差（不稳定度）度量可靠性。结果：不稳定度随难度上升；GPT-4o 在 Data Pre-processing 上 easy 0%、medium 66%、hard 81%；Data Visualisation 的 medium 达 0.99、Supervised Learning 的 hard 达 1.00 ⇒ 重复跑近乎抛硬币。指标间相关普遍 ≤0.30（不冗余）；啰嗦度呈幂律：词啰嗦比 +0.1 ⇒ token 啰嗦比 +0.013（斜率 1.01，95% CI [0.95,1.07]，Spearman 0.953）；GPT-4.1-mini 温度 >1 更易漂移。⚠️ 主实验只用 41 题子集与 OpenAI 模型、数据科学任务，协议可移植但数值不可直接搬到 EDA 评测；本线未复现。',
    '2611.09802': '研究仓库指令文件（AGENTS.md / CLAUDE.md 等，每个 agent session 都会读）随代码演进「过期」后产生的文档债。取 3 个活跃开源仓库各 1 条真实过期指令（测试命令 / 代码位置 / 添加组件的流程），固定代码与任务，只改该指令为三个版本（保持过期 / 更正到当前路径 / 删除）；2 个模型（Claude Haiku 5.5、Sonnet 5.5，Claude Code 2.1.316）× 22 个维护任务 × 5–7 次重复 = 732 条轨迹，逐 tool call 分析。是否走旧路径取决于任务是否把 agent 引到该行：测试命令 80 次过期跑里 78 次走了旧路，流程类约 2/3，代码位置类 0 次。Sonnet 在过期测试命令上每次多约 2 次 tool call：过期 6 次/120k token vs 更正 4 次/78k vs 删除 5 次/100k。隐蔽失效：旧命令找不到测试但输出经 tail 管道仍报成功，Sonnet 40 次过期跑里 19 次「修完后的首次检查」未真正跑测试。任务成功率几乎不变，且没有任何一次修复该指令文件。⚠️ 只有 3 条指令、22 个任务、2 个同族模型与单一 harness；不含「从来就错」的指令；本线未复现。',
})
def official():
    out = {}
    for e in ET.parse(XML).getroot().findall('a:entry', NS):
        aid = e.find('a:id', NS).text.split('/abs/')[-1].split('v')[0]
        out[aid] = {
            'title': ' '.join(e.find('a:title', NS).text.split()),
            'authors': [a.find('a:name', NS).text for a in e.findall('a:author', NS)],
            'published': e.find('a:published', NS).text,
            'updated': e.find('a:updated', NS).text,
            'category': e.find('x:primary_category', NS).attrib['term'],
        }
    out = {k: v for k, v in out.items() if k in FIRST}
    assert sorted(out) == sorted(FIRST), sorted(out)
    return out


def main():
    meta = official()
    lines = SEEN.read_text(encoding='utf-8').splitlines()
    for aid in FIRST:
        assert not [ln for ln in lines if ('| %s |' % aid) in ln], aid
    seen_rows = []
    paper_rows = []
    for aid in FIRST:
        m = meta[aid]
        assert m['published'].startswith('2026-11-06'), (aid, m['published'])
        seen_rows.append('| %s | %s | %s | %s | 收录 |' % (FIRST[aid], aid, m['title'], m['category']))
        paper_rows.append(json.dumps({
            'arxiv_id': aid, 'title': m['title'], 'authors': m['authors'],
            'submitted': m['published'][:10], 'updated': m['updated'][:10],
            'category': m['category'], 'areas': AREAS[aid], 'summary_zh': SUMMARY[aid],
            'abs_url': 'https://arxiv.org/abs/%s' % aid,
            'pdf_url': 'https://arxiv.org/pdf/%s' % aid,
            'first_seen': FIRST[aid],
        }, ensure_ascii=False))
    while lines and not lines[-1].strip():
        lines.pop()
    SEEN.write_text('\n'.join(lines + seen_rows) + '\n', encoding='utf-8')
    old = [ln for ln in PAPERS.read_text(encoding='utf-8').splitlines() if ln.strip()]
    have = {json.loads(ln)['arxiv_id'] for ln in old}
    added = [r for r in paper_rows if json.loads(r)['arxiv_id'] not in have]
    PAPERS.write_text('\n'.join(old + added) + '\n', encoding='utf-8')
    l2 = SEEN.read_text(encoding='utf-8').splitlines()
    for aid in FIRST:
        assert sum(1 for ln in l2 if ('| %s |' % aid) in ln) == 1, aid
    print('SEEN lines=%d 收录=%d 候选=%d papers=%d (+%d)' % (
        len(l2),
        sum(1 for ln in l2 if ln.endswith('| 收录 |')),
        sum(1 for ln in l2 if ln.endswith('| 候选 |')),
        len([ln for ln in PAPERS.read_text(encoding='utf-8').splitlines() if ln.strip()]),
        len(added)))


if __name__ == '__main__':
    main()
