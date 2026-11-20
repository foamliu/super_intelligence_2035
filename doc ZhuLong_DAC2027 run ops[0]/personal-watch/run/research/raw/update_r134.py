#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十四轮落盘（2026-11-05 PM 晚报 2 篇「科普」）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-05-pm-idlist-r134a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.06840': '2026-11-05', '2611.06704': '2026-11-05'}
SUMMARY = {
    '2611.06840': '文生图模型「数不清十以上的数」这件事，被作者做成了一个受控实验：固定物体与起始噪声、一次只改一个变量，看提示词里的数量词到底还起不起作用。5 个开源模型（SDXL、SD3.5-Medium、FLUX.1-dev、FLUX.2 [klein] base 4B、Qwen-Image 20B）各用自己的采样设置；3,088 张生成图由没见过提示词的人来数（零先验），并用 SAM 3 等三种检测器交叉核对。结论：每个模型对少量物体都跟随数字，但都有「有效范围」（reach）——SD3.5-M 与 FLUX.1-dev 在十几之后就不再跟随（SD3.5-M 的中位数量不管要求多少都停在 4.5–8.5；FLUX.1-dev 到「三十」反而缩到 1–2 个），FLUX.2 [klein] 与 Qwen-Image 能松散跟到 25，SDXL 居中。超出范围后，起始噪声的粗尺度部分固定了画面构图但不固定数量：只重画比图像八分之一更细的噪声，就能保住布局、又把数量挪动「换新数字」的 0.69 倍（2/3）。数量词确实仍进入去噪器、并在最初若干步起作用，但没有找到明确方向。把数量以噪点网格直接画进起始 latent 时，人眼在 59% 的图里数出所求数量（只写在提示词里只有 4%）；植入的数量能压过冲突的数字词，但换物体词会重画。评测层面：超过十个后精确匹配率几乎分不开「松散跟随」与「完全忽略」（SD3.5-M 4% vs 松散模型 5–7%），相对误差甚至偏爱固定猜 16，须用同噪声对照才能分辨。⚠️ 作者自报、未复现；只测开源模型、未测闭源；计数依赖人工 + 检测器；43 页含大量附录。',
    '2611.06704': '在「只会上下左右」的吃豆人上训练一个基于 Qwen3.5-9B 的 agent，然后回答一个被高分掩盖的问题：表现差，到底该改「读屏」还是改「选动作」。作者用三族证据分开查：截图审计（RGB 截图 + 结构化盘面/实体判读，24 张不同截图含 4 段 episode 的 6 个时序采样）、历史 ASCII 原始动作策略的运行记录（文本棋盘，去掉图像转录）、以及独立的策略对比。主结果：8 个固定留出迷宫、每格 96 局的常起局面板上，策略优化前 checkpoint 0 通关 0/96，选定 checkpoint 270 通关 77/96（论文摘要的另一表述是「0% → 80.2%」，三条命）；但完整保留的轨迹并不单调——最高 78/96（@335），最后一次完整校验（@425）回落到 60/96，说明「反复使用同一面板上的成绩」不等于稳定保持或对新迷宫泛化。感知侧发现：静态截图读得很准的 reader，在实际交互的不同观测上仍会出错；另一条 ASCII 策略线在继续优化后校验通关数反而下降，回放中出现「明明有出口却选了立即致命动作」的案例。作者据此要求后训练做三类检查：在用中评测感知、区分训练成功与整局验证、看决策与后续表现而不是只看一个选定分数。⚠️ 作者自报、未复现；单模型家族、单游戏、留出仅 8 个固定迷宫；主实验用文本棋盘，作者明确该结果不代表图像策略效果；不给出 RL 失败的单一原因；PDF 未标注机构。',
}
AREAS = {
    '2611.06840': ['多模态', '文生图', '计数失败', '起始噪声', '数量词', '评测指标'],
    '2611.06704': ['agent harness', 'VLM agent', '后训练诊断', '感知-决策分解', '评测陷阱', '长程控制'],
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
        assert m['published'].startswith('2026-11-04'), (aid, m['published'])
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
