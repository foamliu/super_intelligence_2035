#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十八轮落盘（2026-11-07 PM 晚 2 篇「科普」：2611.08478 / 2611.08412）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致（2026-11-05）。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-07-pm-idlist-r138a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.08478': '2026-11-07', '2611.08412': '2026-11-07'}
SUMMARY = {
    '2611.08478': 'AI 科学家已经出现，但没有一个「能跑起来」的世界供它们成长：人类科学家有几百年的开放问题与共享思路（论文对人是「可读也可做」），而论文对 AI 只是「可读、不可运行」。作者把每篇论文变成一个可执行环境——自动抽取论文的开放式研究问题、复现其方法作为基线，AI-Scientist 进入环境后被拿来与人类作者的成果对比。首批发布 1,000 个已核验环境；以此当评测，发现前沿 AI-Scientist 已在 74% 的情况下超过人类研究者；同时留下 6,400 小时研究轨迹（每个想法、实验、失败、成功都有记录）；作为训练场，可把小模型的研究构思能力提升 158% 以比肩前沿模型。⚠️ 作者自报、本线未复现；「74%」是在其自建的 1,000 个环境中对比、非全部科研、存在选择性。',
    '2611.08412': 'AI 在数学里用得越来越多，问题来了：能不能把「AI 参与证明」检测出来，并和「只是帮忙润色文字」区分开？作者用历史 arXiv 论文 + 近期披露实质使用 AI 的论文 + OpenAI 放出的人工稿，构造 5 个 cohort、共 8,281 篇（含针对同一研究问题的人工/AI 配对）。提出 ProofTrace：把每篇论文表示为「即时证明支撑图」(GIPS) 并抽取可解释的数学组织特征。三大发现：① 特征的主成分投影呈现「AI 参与度梯度」；② 找到 AI 生成证明的反复出现的特征（更少引用外部结果、更依赖中间结论、图连通性改变，且在控制领域/篇幅/图规模后仍稳健）；③ 独立检测实验中，ProofTrace 能区分人类论文与「披露实质用 AI」的论文，且在 AI 改写后仍稳，而 SOTA 文本检测器性能急剧下降。⚠️ 作者自报、本线未复现；检测针对「披露」实质用 AI 的论文，主要是数学证明域，迁移到代码/自然语言未验证。',
}
AREAS = {
    '2611.08478': ['AI-Scientist', '可执行环境', '自动复现基线', '研究轨迹', '科学自动化', '科普'],
    '2611.08412': ['AI4Math', 'AI生成内容检测', 'ProofTrace', 'GIPS图', 'cohort/配对', '科普'],
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
