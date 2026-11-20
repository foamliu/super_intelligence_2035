#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十三轮落盘（2026-11-05 AM 早 3 篇「借鉴」）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-05-am-idlist-r133a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.05234': '2026-11-05', '2611.05304': '2026-11-05', '2611.05266': '2026-11-05'}
SUMMARY = {
    '2611.05234': '把标准 transformer 的 attention residuals 搬到「循环深度」上：looped transformer 反复复用同一组层来用参数换计算，但标准残差把各次循环压成单条信息流、无法选择该复用哪一层的表示。ARLoop 让每层的输入通过「在模型深度方向做注意力」选择性聚合，并发现 looped 模型不需要完整残差历史——滑动窗口深度注意力在较大循环深度下即匹配或优于全历史。140M / 370M 受控实验（R=1..5）一致优于 PreNorm 与既有残差设计（如 140M R=3 验证 PPL 16.59→16.03、370M R=3 12.28→12.17，收益随循环深度增大：R=1 约 −0.11 PPL、R=3 约 −0.53）。真实预训练配方：PreNormLoop-0.6B（18 层 / R=3 / 180B token）对 ARLoop-0.6B 同预算，另训 ARLoop-1.2B（24 层 / R=3 / 500B token）；1.2B 只用 0.5T token 即在全部 8 个评测（ARC-C、HellaSwag、WinoGrande、OpenBookQA、GSM8K、MATH、MBPP、HumanEval）超过唯一全开放的 looped LLM Huginn-3.5B，数学与代码提升最大，并与同量级非 looped 的 Qwen3.5-2B 有竞争力（在多数任务上仍低于 Ouro，作者归因于对方数据预算与数据质量）。全开放：模型三个 + 代码。⚠️ 作者自报、未复现；规模上限 1.2B / 0.5T token；评测为常规 zero-shot/few-shot，未覆盖长上下文与 agent 任务。',
    '2611.05304': 'looped 模型每循环一次都要各存一份 K/V，KV cache 随循环数线性膨胀，成为比参数内存更硬的瓶颈。作者观察到两类结构：looped 模型的 KV 沿 loop 轴高度冗余；不同循环步对量化的敏感度差异很大。据此提出 LoopVQ：把多个循环步的通道联合编码进同一个向量量化码字（一个 index 跨 Tc 个循环步共享），并用全精度模型输出微调码本，使量化输出逼近全精度输出。评测覆盖通用（GSM8K / MATH500 / HumanEval / MBPP）、长链式思考（AIME24/25、GPQA-Diamond、HumanEval+ 等）与长上下文检索（NIAH、LongBench），对象为 Ouro-1.4B / Ouro-2.6B / Huginn-3.5B。0.5 bit/元素时优于面向标准 LLM 的 KV 量化基线 CQ / TaSQ（例：Ouro-1.4B GSM8K BF16 78.77 → CQ 46.78 / TaSQ 57.32 / LoopVQ 75.82 / TaSQ+LoopVQ 77.56；MATH500 77.20 → 17.80 / 38.80 / 69.40 / 75.20）；与 TaSQ 正交叠加后 0.25 bit 仍保留大部分 BF16 精度，0.25 bit 时 KV 压缩比达 64×。系统侧在 SGLang 中实现（8 token/page；sink 与最近窗口留 bf16；量化页按 Tc 循环步共享 index），32K 上下文 decode 延迟近乎减半，峰值服务吞吐相对 BF16 最高 4.3×（Ouro-1.4B）与 6.1×（Ouro-2.6B）；校准成本低（Ouro-1.4B k-means 6.1 min + 码本微调 2.3 min，单张 RTX 6000 Ada）。⚠️ 作者自报、未复现；只在 looped 族验证、需逐模型校准；服务实验为 RTX 6000 Ada + SGLang（A100 在附录）；小模型上精度损失仍可见（Huginn-3.5B GSM8K 34.04 → 32.37）。',
    '2611.05266': '朴素 on-policy RL 常被基座能力卡住：某些行为一次都采不到，就永远学不会；而现代后训练的奖励越来越多来自「带评分细则的文本反馈」。作者把这类反馈用成方向性监督：仅在策略失败的轮次注入反馈串，把「带反馈前缀的同一策略」当专家，做 on-policy 自蒸馏（OPSD），再与逐准则 RL 奖励叠加（targeted guidance），从而在不改主奖励的前提下教会辅助准则。实验为多轮 agentic 软件工程环境：基座 Qwen3-Coder-30B + 自家 agentic coding SFT，GRPO 优化 pass-rate 并正则化输出长度，200 步、batch 32 groups × 32 rollouts、lr 3e-6、异步 RL（推理策略可落后于训练策略）、全词表 KL（含 thinking 与 tool-call token）。Table 1（最后 32 步均值）：7 项风格准则从基线 Markdown 0.00 / Sol.Desc 0.70 / Req.Order 0.04 / Approval 0.00 / Cmd Ran 0.43 / Suggest 0.00 / Work 0.03 提到 0.85 / 0.95 / 0.77 / 0.55 / 0.99 / 0.64 / 0.85，而 coding pass-rate 0.33±.05 与基线持平；对照 GRPO 的 Markdown 仍 0.00、OPSD pass-rate 掉到 0.30、Online SFT / LaTRO / Verifree 多数准则 <0.05。稳定性归因两条：崩溃前兆是策略熵尖峰（蒸馏权重过大导致风格与 pass-rate 双崩），静态小权重即可留在稳定区；把 KL 施加到 thinking token 上可消除准则间振荡，thinking 轨迹中会出现自提醒。⚠️ 作者自报、未复现；单基座单 harness、单数据集单 epoch；准则由外部 judge 二值判定 + 固定反馈串；不提升 pass-rate（论文明确目标不是提主指标）。',
}
AREAS = {
    '2611.05234': ['LLM', '预训练架构', 'looped transformer', '参数高效', 'attention residuals', '深度方向注意力'],
    '2611.05304': ['SLM', 'KV cache 量化', '亚 1 bit', '向量量化', '推理服务', 'SGLang 吞吐'],
    '2611.05266': ['agent harness', 'agentic RL', 'on-policy 自蒸馏', '文本反馈', '多准则', '训练稳定性'],
}


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
        assert m['published'].startswith('2026-11-03'), (aid, m['published'])
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
