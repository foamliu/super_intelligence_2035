#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十轮落盘（2026-11-08 PM 晚报 2 篇「科普」：2611.07920 / 2611.08469）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致（2026-11-05，周末例外批次）。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-08-pm-idlist-r140a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.07920': '2026-11-08', '2611.08469': '2026-11-08'}
SUMMARY = {
    '2611.07920': '问的是「有限经验如何支撑无界的泛化」：只学过小数加法的孩子会加任意长度，而在 ≤40 符号短串上训练的 LSTM/Transformer 到 41-500 长度即崩。作者把差别归到「决策时读什么」——位置/计数/时间随输入变长不断取新值，是「坐标」，读坐标的学习器在长输入中必然遇到训练未覆盖的取值；而「两者是否相同」在每个长度上答案不变，是「巧合」，只读巧合的学习器在长输入里找不到短输入没有的东西，因此有限经验即可固定其规则。推论：记忆须携带输入长度而规则保持有限 ⇒ 这段记忆从每个位置看必须一样，只能由「环」组成（对应网格细胞），检测回到原位的细胞是位置细胞，记录是海马索引，前额叶控制器只移动环、从不读环。只读巧合不损失算力：被有限经验固定下来的正是图灵机随输入步进计算的部分。实验：≤40 符号训练后，15 个基准中 9 个在长度 41-500 上平均 ≥99% 正确（其中 5 个任务 LSTM/Transformer 全解不出）；训练后给新环可零错反转 15,015 个符号，更长处的失败点与理论曲线一致。⚠️ 作者自报、本线未复现；全为离散符号任务的小规模训练（12,000 步/批量 32/长度 1-40），45 次基准运行中 23 次首次成功、7 次重试成功、15 次全败；与网格细胞/位置细胞/海马索引的对应为作者的解释性映射、非实测。',
    '2611.08469': '两个网络可以算出完全相同的函数，却在「怎么算」上不同；可解释性、AI 审计与「机器是否有意识」的判断依赖的都是这类机制层的量。作者针对最苛刻的例子——整合信息论（IIT）的 φ——在 4/5 单元、真值已知的随机网络中精确求解「有限、残缺、有噪声的干预实验能否识别它」。三条结论：① 行为可能完全沉默——循环网络与前馈网络在响应延迟上的输入-输出规律完全相同，φ 分别为 0.28 与 0 bit，而内部记录 4-53 次试验即可区分；② 部分访问同样盲——一步记录中漏掉的单元造成 0.30-1.02 bit 的精度地板，样本量再大也无法降低；all-but-self 奇偶网络里任意长度记录只能通过若干隐藏单元保真度的乘积看到它们（一次干预可打破该对称）；③ 度量有「悬崖」——φ 用一个准则选划分却报另一个，跨边界的极小机制变化令 φ 跳 25-100%（所找到的边中 99% 如此），约 1% 几乎完美拟合干预数据的替代模型会把 φ 误报 >20%。单侧结论仍可保：同一批数据能给出边两侧的下界，作者证明某 64 维机制区域内恒有 φ>1.004 bit，并用约 10^7 次受控转移给出误证明概率 ≤α 的证书。作者结论：可测性是设计问题而非数据量问题。⚠️ 作者自报、本线未复现；仅 4-5 单元已知接线的小网络，φ 精确计算随规模超指数增长（割数 4 单元 150→5 单元 1,061），真实规模是否保持同样障碍作者明说未定；证书成本高（750 万/2,800 万次转移）；作者不判断任何系统是否真有意识。',
}
AREAS = {
    '2611.07920': ['系统性泛化', '长度外推', '网格细胞', '海马索引', '图灵完备', '网格记忆', '认知计算神经科学'],
    '2611.08469': ['整合信息论', '机器意识', '可识别性', '机制vs行为', '干预实验', '单侧证书', 'AI审计'],
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
