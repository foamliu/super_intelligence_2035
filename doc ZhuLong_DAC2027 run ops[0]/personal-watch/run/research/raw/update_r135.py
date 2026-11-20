#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十五轮落盘（2026-11-06 AM 早 3 篇「借鉴」）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-06-am-idlist-r135a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.06133': '2026-11-06', '2611.06147': '2026-11-06', '2611.06828': '2026-11-06'}
SUMMARY = {
    '2611.06133': '混合注意力大模型（多数层已换成线性/滑窗注意力）在长上下文解码时，剩下的少数全注意力层仍决定单 token 成本。作者不改权重、不重训，只把每个全注意力层的注意力限制成三部分：固定前缀 256 token、最近 W 个 token 的滑窗、以及按 Quest 做页级检索挑出的 Q 个最相关 token，再用 NSGA-II 多目标搜索为每一层单独挑 (W,Q)（A100 上 8.6–34.2 GPU-hours；122B/397B 在 4 卡 GB200 上 31.3–58.4 GPU-hours），并对比 6 种配置（基线、两种统一配置、Best Accuracy / Best Speed / Balanced）。在 6 个混合模型、3 个家族（Qwen3.5 4B/27B/122B-A10B、Ornith-1.0-397B、Gemma-4-31B、gpt-oss-120b）与 21 个长上下文基准上，每个模型都至少有一种配置逐项保住基线精度、平均差距在 0.5 个百分点以内；batch 4 下 64k/256k 解码最多快 1.26×/2.22×（Qwen3.5-4B）、1.20×/2.23×（Qwen3.5-122B-A10B）、1.16×/2.06×（Ornith-397B），稠密 Qwen3.5-27B 与 Gemma-4-31B 只到 1.11×/1.09×，gpt-oss-120b 接近其上下文上限时收益很小。⚠️ 短上下文反而比基线慢，要到 32k–64k 之后才转为更快；Quest 保留完整 KV cache ⇒ 只省计算不省显存；配置须逐模型逐层搜索，且未在国产加速器上验证；作者自报、本线未复现。',
    '2611.06147': 'MoE 推理里常见的加速手段是「每 token 少跑几个专家」，过去只按精度基准验收。作者在 vLLM 上审计 9 个 MoE 模型，发现这种削减会削弱拒答：在 RTX A6000 上保留约三分之二的已选专家，离线解码（batch 8）快 15%–28%，MMLU 掉不到 2 分，但在「要求不要拒答」的越狱模板下，有害请求的回答率在 Qwen1.5-MoE 上升 18.4 个百分点、OLMoE 上升 9.5、DeepSeek-V2-Lite 上升 6.6（9 个模型中这 3 个显著）；改用 top-p 路由（每 token 专家数可变）在更大精度代价下最多升 30.1 个百分点。作者把升高的来源定位到「处理 prompt 与生成最初几个 token」这一段，于是提出 SafeStart：prompt 与最初 8 个生成 token 全专家运行，之后才切到削减后的专家集，并在 vLLM 里用一个融合 kernel 实现。不削专家时该 kernel 只给在线服务的每输出 token 中位时间加最多 2.4%；削专家时保住至少 85% 的离线解码加速，把上述越狱下的变化压到 −2.1 ~ +1.3 个百分点。另有 889 条预留请求的预注册分析：直接截断使有害服从上升 5.8–21.4 个百分点，SafeStart 只留 0.6–2.6 个百分点，三个模型中两个非劣于原模型；保留约一半专家时，batch 8 解码快 38%–44%，并仍消掉至少 86% 的上升。⚠️ 单卡 RTX A6000 + vLLM，未覆盖多卡/国产加速器；越狱模板与裁判（Llama Guard 3 8B 为主、HarmBench 为副）本身有误差；主要结论针对该确认性设置，泛化需再验；作者自报、本线未复现。',
    '2611.06828': '门控 delta 线性注意力（GDN、Kimi Delta Attention、GDN-2）是按 GPU 的小 tensor-core 分块与快速向量寄存器设计的；直接搬到 TPU（256×256 脉动矩阵单元 + 较慢的向量单元）会有一半矩阵块空着，并卡在向量操作上。作者提出 Systolic Linear Attention（SLA）：把 key 宽度加宽到 256 并做 value head 分组共享、把衰减门分成 4 个 64 通道的 tile、把 chunk 求解（含反向）全部改成块矩阵乘并融进一个 kernel。TPU v7x 上单层 SLA-R4 比开源 Tokamax KDA kernel 快 1.6×–2.5×（精确 chunk 求逆时 1.4×–2.4×），临时 HBM 少 52%–61%；在最多 512 卡、6.5B–63.1B 稀疏 MoE 的预训练研究里，同等困惑度下训练比 MaxText KDA 快 8%–24%，且任何规模都不需要给线性注意力门做 clamp（RoPE 骨干 8K→64K 零样本，63.1B NoPE 上 32K 8-Needle 83.2%–84.4%）。⚠️ 收益主要来自 head 共享 + kernel 融合，方法针对「宽矩阵块 + 大矩阵/向量差距」的加速器，GPU 上未必成立；匹配种子下仍比宽 key KDA 差约 0.1 困惑度（1 步 Neumann 逆时 0.3），63.1B 为单种子、64K QA 集偏小；作者自报（Google）、本线未复现。',
}
AREAS = {
    '2611.06133': ['LLM', '长上下文', '推理加速', '稀疏注意力', 'KV cache', 'vLLM'],
    '2611.06147': ['MoE', '推理服务', '专家削减', '安全对齐', '拒答', 'vLLM'],
    '2611.06828': ['线性注意力', 'TPU', 'kernel 协同设计', 'MoE 预训练', '训练效率'],
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
    # XML 里含 2 个备选（2611.06513 / 2611.06841，未选）⇒ 只取 3 篇入选
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
