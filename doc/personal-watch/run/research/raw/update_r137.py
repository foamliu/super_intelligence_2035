#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十七轮落盘（2026-11-07 AM 早 3 篇「借鉴」）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-07-am-idlist-r137a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.07707': '2026-11-07', '2611.08363': '2026-11-07', '2611.08133': '2026-11-07'}
SUMMARY = {
    '2611.07707': '大模型推理受限于把大权重矩阵和 KV cache 反复搬进内存的开销。模拟内存计算（AIMC）把计算直接放在静态权重所在的存储阵列上，能大幅降能耗与延迟；3D-IMC 再把存储阵列垂直叠成多层以提升容量，但引出新问题：权重怎么摆进存储层，决定了哪些矩阵-向量乘（MVM）能并行执行，进而影响延迟与吞吐，而 3D-IMC 的权重映射「并发性」此前研究不足、算力利用率偏低。作者提出 CAMP（上下文感知映射与放置）：用一张冲突矩阵把架构、目标网络与运行时上下文造成的资源争用刻画出来，据此做吞吐最优的权重映射，再用基于 profiling 的反馈环剪枝搜索空间、在可用时间内返回优化映射。CAMP 是离线、纯软件方案、不需改硬件；把 3D-IMC 算力利用率从 42.4% 提到 60.3%，相对 SOTA 映射最高 2.0× 的 IMC 吞吐、1.74× 的端到端吞吐。⚠️ 作者自报、本线未复现；收益依赖特定 3D-IMC 模拟器/架构。',
    '2611.08363': '量化能降低 LLM 推理的显存与带宽需求，但会掉精度；而把高精度数据放到外部、需要时再取回，又会让生成卡顿。StrataFlux 挑战这个权衡：在保留量化省显存/加速优点的同时，把低比特权重与 KV cache 量化损失掉的精度补回来——它把「细化精度」的表示、选择与投递三者协同设计，让主机内存（RAM）与固态硬盘（SSD）成为额外精度的可用来源；选择性精度流式加载减少传输量、把加载与计算重叠、并在多个解码步之间复用已取回的精度，使生成不必等每次传输。评测覆盖 2–4 bit 权重、2–3 bit KV（独立 GPU 与统一内存平台）：2-bit Llama-3.1-8B-Instruct 把 WikiText-2 困惑度从 9.46 降到 8.40，同时在 RTX 5090 上保持量化版 95.4% 的吞吐；2-bit 权重 + KV 让 Qwen3-8B 的 AIME 2024/2025 从 11.0% 提到 47.1%，GPU 显存占用不变；128K 上下文下，3-bit 权重 + 2-bit KV 的 Llama-3.1-8B-Instruct 在 RTX 5090 上困惑度与速度接近 vLLM 的 4-bit AWQ + 8-bit KV，而显存约用一半。结论：GPU 常驻精度不必决定精度上限，外存层延迟也不必决定解码速度。⚠️ 作者自报、本线未复现；依赖特定加速库/平台适配。',
    '2611.08133': '生产部署常用不同模型来平衡成本与质量（级联、路由、长对话中切换模型），上下文跨轮累积，每次切换都要让目标模型对这段上下文重跑 prefill。已有方法只迁移全注意力（FA）的 K/V cache；而混合线性注意力模型还保留循环状态（REC）与卷积历史（Conv），Conv 与 REC 的交互使跨模型状态转移变复杂：Conv 扰动量会改变循环层里的 key/value 并影响 REC 更新；conv 历史可被覆盖，但 REC 的变化仍会影响后续输出，而且更精确地重建 REC 不一定带来更好的续写。作者提出 HST（Hybrid State Transfer）处理 FA/REC/Conv 三类状态：用结构化 REC 映射、Conv 对齐时保留历史顺序、以冻结目标模型的输出校准适配器、离线合入 FA cache 映射。在 5 个基准上，Qwen3.5 4B→27B、9B→27B 的平均任务保留率分别 89.88%、94.11%；在源 cache 已就绪时，16K 合成输入上「交接主体」加速 21.66×、21.91×。⚠️ 作者自报、本线未复现；收益以「源模型 cache 已就绪」为前提。',
}
AREAS = {
    '2611.07707': ['存储计算', '3D-IMC', '模拟内存计算', '权重映射', 'LLM推理加速', '调度/编译'],
    '2611.08363': ['低比特推理', '量化', '内存层级', 'KV cache', '外存 offload', '存储'],
    '2611.08133': ['混合线性注意力', '状态迁移', '模型级联/路由', 'KV cache', '推理效率', '架构'],
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
    # XML 里含 5 个备选（2611.07263 / 2611.07552 / 2611.07605 / 2611.08082 / 2611.08216，未选）⇒ 只取 3 篇入选
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
        assert m['published'].startswith('2026-11-05'), (aid, m['published'])
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
