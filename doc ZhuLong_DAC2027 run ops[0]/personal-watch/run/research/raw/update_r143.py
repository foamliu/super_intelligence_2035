#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十三轮落盘（2026-11-10 PM：晚报 2 篇「科普」）。

数据源：`raw/2026-11-10-pm-candidates-r143.json`（arXiv 官方 API 单分类 100 条合并去重，
`published >= 2026-11-09`）。断言：仅追加、每个 arXiv ID 恰好 1 行、published 前缀 2026-11-09。
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
CAND = BASE / 'raw' / '2026-11-10-pm-candidates-r143.json'

FIRST = {'2611.12820': '2026-11-10', '2611.12832': '2026-11-10'}

AREAS = {
    '2611.12820': ['AI 审稿', '埋错误基准', '漏检', '省略型错误', '系统集成', '误报', '评测方法'],
    '2611.12832': ['低精度预训练', 'NVFP4', '罕见事实', '曝光次数', '梯度噪声', 'Adam 二阶矩', 'loss 指标盲区'],
}

SUMMARY = {
    '2611.12820': (
        '把 100 个已知错误埋进 10 篇开放获取的心理学论文（先按 INSPECT-SR 等清单整理出 62 类错误，'
        '每篇 10 个；埋法既包括改写关键句，也包括直接删掉关键信息，例如删掉元分析必需的统计变换、'
        '删掉关键因变量的计算说明），再让当时的 Claude / GPT / Gemini 各版本与两个付费 AI 审稿工具'
        '（Reviewer3、Refine.ink）去读，用 LLM-as-judge 核对每条意见是否精确对应埋下的错误。'
        '最佳单系统 GPT-5.5（high reasoning）抓到 71/100（512 条意见，$0.30/篇、$0.042/错误），'
        '最差 Reviewer3 仅 30/100；把全部基础模型并起来 91/100、并上所有系统 93/100。'
        'Refine.ink 57/100 但最贵（约 $50/篇、$8.77/错误），在方法学设计、统计错误、内部一致性上最强，'
        '在因果推断、报告完整性、可推广性上最弱。所有系统都栽在同一类：7 个谁都没抓到的错误全是'
        '「省略型」（删掉了本该有的信息）。同一模型重跑 3 次几乎不增加命中（作者未扫温度）。'
        '⚠️ 只做实验心理学、只测召回不测误报（false positive 未测）、埋入错误的分布与真实论文错误分布'
        '是否一致未知；错误判定经抽查而非 100 条逐条人工复核；作者自报、本线未复现。'
    ),
    '2611.12832': (
        '问一个被 loss 掩盖的问题：低精度预训练在 loss 打平时，学「罕见事实」是否一样快。'
        '作者用模拟 4-bit 矩阵乘（操作数按格式量化、FP32 累加）从零训练 transformer，'
        '在曝光次数可控的合成传记（人物出现 1–256 次）上、以及把它们混进 FineWeb-Edu（1B token 中 7.2% 为传记 token）'
        '两种设置下比较。结果：NVFP4 要达到与 BF16 相同的召回，在 token 对齐下需要 1.32×（合成）/1.52×（自然文本）'
        '的曝光次数，而验证 loss 只差 0.5% / 2%；若两边都用 BF16 矩阵乘评测，降为 1.26× / 1.30×；'
        '按 loss 对齐则约 1.2×。越罕见越吃亏：见到 64 次的事实 0.97×，只见到 2 次的事实 1.30×。'
        '机制拆解：零均值梯度噪声就能复现「只量化反向」的代价（几乎不动 loss）；'
        '噪声只进 Adam 二阶矩时等效于降低学习率、代价会消退，而噪声进更新会压低信噪比、'
        '约 2/3 的代价一直带到训练结束；调大学习率补不回来。'
        '用 BF16 checkpoint 的梯度统计即可给各低精度格式/部分量化/噪声控制排序（Spearman 0.96，95% CI [0.84, 0.99]，'
        '17 个配置中 15 个落在观测 95% 区间内），且只需一段「插桩」语料切片。'
        '补救：适配 NVIDIA NVFP4 配方把 loss 差距补上 60%，但曝光代价只补 42%（自然文本约 1/8），'
        'BF16 cooldown 与「分块形梯度噪声」可减轻但都消不掉。'
        '⚠️ 模型仅 10.6M/25.7M/92.0M（非嵌入参数）、单张 RTX 4090、模拟量化而非原生 FP4 kernel、'
        '不验证与 Blackwell 内核逐位一致、也不测原生 FP4 吞吐；作者自报、本线未复现。'
    ),
}


def main():
    cand = {x['arxiv_id']: x for x in json.loads(CAND.read_text(encoding='utf-8'))['fresh']}
    seen_lines = SEEN.read_text(encoding='utf-8').splitlines()
    for aid in FIRST:
        assert aid in cand, 'missing candidate %s' % aid
        assert not [ln for ln in seen_lines if ('| %s |' % aid) in ln], 'dup %s' % aid
        assert cand[aid]['published'].startswith('2026-11-09'), (aid, cand[aid]['published'])

    seen_rows, paper_rows = [], []
    for aid in FIRST:
        m = cand[aid]
        seen_rows.append('| %s | %s | %s | %s | 收录 |' % (FIRST[aid], aid, m['title'], m['category']))
        paper_rows.append(json.dumps({
            'arxiv_id': aid, 'title': m['title'], 'authors': m['authors'],
            'submitted': m['published'][:10], 'updated': m['updated'][:10],
            'category': m['category'], 'areas': AREAS[aid], 'summary_zh': SUMMARY[aid],
            'abs_url': 'https://arxiv.org/abs/%s' % aid,
            'pdf_url': 'https://arxiv.org/pdf/%s' % aid,
            'first_seen': FIRST[aid],
        }, ensure_ascii=False))

    while seen_lines and not seen_lines[-1].strip():
        seen_lines.pop()
    SEEN.write_text('\n'.join(seen_lines + seen_rows) + '\n', encoding='utf-8')

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
    sys.exit(main())
