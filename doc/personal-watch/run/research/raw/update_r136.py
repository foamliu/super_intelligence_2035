#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十六轮落盘（2026-11-06 PM 晚 2 篇「科普」）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-06-pm-idlist-r136a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.08294': '2026-11-06', '2611.08314': '2026-11-06'}
SUMMARY = {
    '2611.08294': 'Manim 这类程序化动画工具能精确渲染教学视频，但「渲染成功」不等于「画面对」：仍可能有布局重叠、讲解缺失或内容错误，而渲染结果本身不会告诉你该改哪行代码。作者构建 ManimData —— 用「生成—执行—渲染—审阅—修改」闭环加上检索到的 API 文档，产出 24,034 条经渲染验证与质量过滤的轨迹，保留中间程序、执行报错、视觉批评与修正动作；再用角色条件监督微调训练一个 4B 模型（ManimCode）分别扮演写、审、改三种角色，随后用渲染结果与无参考质量反馈做强化学习，专门训练 Reviser 处理训练轨迹里没见过的错误。场景级测试上，ManimCode 在 ManimData-test / ManimBench 的渲染成功率 96.6% / 97.0%，同一推理设置下未训练的 4B 基座为 52.6% / 82.0%；视频质量分从 2.48 升到 2.94、从 3.00 升到 3.44。把它接进两个长视频教学系统（Code2Video 的 117 个讲座主题、TheoremExplainAgent 的 239 个定理）后，完整产出视频从 19/117 升到 107/117、从 53/239 升到 239/239，教学效果与视觉质量指标同步上升。⚠️ 质量评分主要由一个多模态裁判给出，人工盲评 98 对视频时只在质量差距 ≥0.5 分时与裁判一致率 79%（差距 <0.25 分时仅 29%）；ManimBench 中 85/100 条参考程序与知识库中的文档示例近乎重复（已排除检索）；作者自报、本线未复现。',
    '2611.08314': '鸟群、鱼群、兽群的集体运动通常被建模成「两两之间的吸引力/排斥力/对齐力」之和，但实验证据显示真实群体存在多体作用。作者把材料科学里拟合原子间势的原子团簇展开（ACE）改造成面向自驱动个体的 dACE：它把每个个体的加速度做严格等变的展开，并唯一地拆成 1 体、2 体、3 体及更高阶项，另加一个「自身过去运动」项（分阶段拟合，避免把交互吞进自项）。在已知交互规则的 2D/3D 模拟群体上，dACE 用很少的数据就能逐阶恢复规则；对比的神经网络 SocialNet 需要更多数据，在多体或手性规则上误差大得多，且只支持 2D。在斑马鱼（8 段公开追踪视频、每组 60–100 条）与黄金闪鳞鱼（10 次试验、每组 10–151 条）的真实追踪数据上，dACE 学到的规则在数据的两半之间一致性更高；闪鳞鱼的 3 体项在邻居变密时与 2 体响应方向相反，使总响应停止增长，与既有实验相符。论文还给出一条方法学警告：下一帧预测准确率主要衡量的是自推进与观测噪声，而不是个体间交互，因此不能用来给交互模型排名，应改用「无共享帧的预测协议 + 加入交互相对自模型的增益 + 两半数据学到的规则一致性」三项组合。⚠️ 真实数据无法与「真规则」对照，一致性只是必要条件；模拟实验的规则族有限；单作者工作，作者自报、本线未复现。',
}
AREAS = {
    '2611.08294': ['多模态', '教育动画', '代码生成', '视觉自纠错', '强化学习', 'Manim'],
    '2611.08314': ['集体运动', '多体交互', '可解释模型', '原子团簇展开', '鱼群追踪'],
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
    # XML 里含 4 个备选（2611.08177 / 2611.08226 / 2611.08478 / 2611.08486，未选）⇒ 只取 2 篇入选
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
