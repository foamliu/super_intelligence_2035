#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十九轮落盘（2026-11-08 AM 早报 3 篇「借鉴」：2611.08285 / 2611.08417 / 2611.07812）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致（2026-11-05，周末例外批次）。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-08-am-idlist-r139a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.08285': '2026-11-08', '2611.08417': '2026-11-08', '2611.07812': '2026-11-08'}
SUMMARY = {
    '2611.08285': '质疑「轨迹型失败预测器」到底学到了什么：在公开 SWE-bench Verified 轨迹上（每模型每题只跑一次）分解后，一个完全不看轨迹、只用「该题对其他模型有多难」的参考分达到 0.92 AUROC，而轨迹预测器只有 0.62-0.63；同一题内只用「是哪个模型跑的」就有 0.82，预测器基本在复现模型的整体能力排名；扣除难度与能力后轨迹增益在统计上等价于 0（-0.001，18 个配置一致）。「最佳单模型 vs any-model oracle」的差距不比随机波动大，逐题模型切换在留出跑上无收益；重复跑 pilot 显示同一模型常「有的跑解出、有的跑解不出」，重跑只能救「坏跑」、救不了超能力的题，而现有预测器分不清。作者呼吁失败预测要解释「为什么这次跑失败」，并在重复跑 + 闭环等预算下评估。⚠️ 作者自报、本线未复现；证据主要来自单一基准 + 单一 scaffold，重复跑 pilot 为小规模公开语料。',
    '2611.08417': '提出「基准维护债（benchmark maintenance debt）」：即使发布时经过严格校验的基准也会腐坏——模型变强后给出合法却被 verifier 判错的解法，评测基建改动也会让题目的隐含假设失效。作者给出持续校验工作流（社区报告 + 任务工件 + agent 轨迹 + 自动 oracle 检查 + 人工闸门修复），用于 Terminal-Bench 2.0（89 题）：审计发现约 30% 有缺陷，修复后发布 Terminal-Bench 2.1（28 题修订 = 89 处环境修复 + 11 处指令修复），准确率整体 +10pp 以上、排行榜名次最多动 3 位（Spearman ρ=0.958）。第二层结论：资源预算是测量规格的一部分——固定 wall-clock / 输出 token 预算会实质改变表现，放宽时间上限可抹平 GPT 5.4 上约 20pp 的 harness 差距、把 GPT 5.4 mini 的 30pp 差距缩到 5pp（预算最多扫到 32×）。⚠️ 作者自报、本线未复现；结论绑定 TB2.0 的任务/verifier，修复令分数跨版本不可直接比较。',
    '2611.07812': '在紧密的数据预算下比较两套反差极大的预训练语料（1911 年《大英百科全书》vs BabyLM 2026 严格子集），预算对齐在 1,000 万词与 3,700 万词，每套都训教师模型、蒸馏出的 5,800 万参数 Baby-Llama 学生、以及无蒸馏学生消融，模型族/配方/评测协议完全相同。横跨 BLiMP、BLiMP Supplement、EWoK、Entity Tracking、COMPS 的结果是「技能画像差异」而非单一质量排序：BabyLM 2026 在语言可接受性上稳定更强，Britannica 在 Entity Tracking（合成状态跟踪）上常更强；反差在教师与学生、两个预算下都出现，蒸馏学生对照的跨种子复现最干净；匹配训练曝光量、拉长诊断上下文后反差仍存，而教师直接集成复现不出 10M Britannica 学生的 Entity Tracking 行为（该任务幅度对训练动力学敏感）。结论：小规模比较预训练数据必须做多基准评测。⚠️ 作者自报、本线未复现；仅两份语料、58M 级小模型，不可外推到 2B 级预训练。',
}
AREAS = {
    '2611.08285': ['coding agent', '失败预测', '轨迹监控', '模型路由', 'SWE-bench', '重复跑评测'],
    '2611.08417': ['agent 基准', 'Terminal-Bench', '基准维护债', '持续校验', '自动 oracle', '资源预算'],
    '2611.07812': ['小模型', '预训练语料', '配对实验', '蒸馏', '技能画像', '多基准评测'],
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
