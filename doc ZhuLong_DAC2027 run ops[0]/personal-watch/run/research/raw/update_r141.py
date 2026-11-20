#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十一轮落盘（2026-11-09 AM 早报 3 篇「借鉴」：2611.07595 / 2611.08452 / 2611.07634）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致（2026-11-05，公告批次例外）。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
SEEN = BASE / 'SEEN.md'
PAPERS = BASE / 'papers.jsonl'
XML = BASE / 'raw' / '2026-11-09-am-idlist-r141a.xml'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
FIRST = {'2611.07595': '2026-11-09', '2611.08452': '2026-11-09', '2611.07634': '2026-11-09'}
SUMMARY = {
    '2611.07595': 'agent 探索得到的流程知识通常随轨迹丢弃、下次重新摸索。作者把它做成不改模型参数的可复用资产：结构化 Gene（策略＋适用条件）、绑定执行案例的 Capsule、记录反例的 AntiGene，执行时在会话起点按任务检索注入（注入预算 12,000 字节）。用 Baseline–Extraction–Gene 配对协议（同题同 harness 同基座，B 原生 / G 注入，新会话重跑，token 全记录），在 Claude Code 与 Codex × 2 基座 × 4 基准（Terminal-Bench 2.1、SWE-bench Multilingual、SWE-rebench、GAIA）的 16 配置 320 对配对上，成功率 83.13%→87.50%（+4.38pp）、任务执行 token −24.24%（按全部配对求和口径）；两边都成功的 265 对 token 仍 −17.57%。分基准：TB-2.1 64/80→71/80（+8.75pp）、SWE-rebench +5.00pp、GAIA +3.75pp、SWE-bench Multilingual 96.25% 持平；16 配置中 9 个提升、7 个不变。⚠️ 作者自报、本线未复现；评估集自述为「diagnostic rather than random sample」（每配置 20 题并额外按观察到提升与 token 用量挑题），不可当无偏基准分；排除超时/触限跑，token 不含经验抽取开销。',
    '2611.08452': '复现 ML 实验的成功取决于能否把散落在论文/代码/工件里的「做法与决定」补齐。作者标准化「精修可复现工件」（精修代码库＋环境配置＋实验启动器＋复现指南），由 agent 构建、人定标准，另有独立 Auditor 核验执行证据（因为数字吻合也可能是替换测量）。基准 ReproBridge-Bench：742 篇 ICML 2026 Spotlight→241 篇有代码→随机 50 篇→排除工件/算力/闭源 14 篇 ⇒ 36 篇论文、502 实验、1,463 任务，其中 1,029 个（70.3%）数值兼容进入评测（387 实验）；每任务 5 位独立人工复现者的参考分数，参考变异 ≤ 绝对分数 10% 才判 stable；采用双侧兼容规则（分数高于公布值同样判不兼容）。结果：4 个 coding agent 复现成功率 76.4%→92.6%、下游 API 花费 −19.7%（−16.8%～−23.7%）、跨模型成功率极差 21.6pp→3.9pp；消融中移除任一组件都掉，代码与环境缺失损失最大；1,029 任务含 299 个 CPU-only（730 个 GPU）。⚠️ 作者自报、未复现；仅覆盖有官方实现且算力可承受的 Spotlight 论文（36/50），成功=数值兼容＋审计通过，不等于复现同一科学结论；5 个参考观测仍是小样本，10% 为人为阈值。',
    '2611.07634': '把「局部改动合并回整文件且不破坏无关内容」定义为独立的 Apply 任务并训练专用小模型。数据流水线：CommitPack 57.7M 真实 commit→规则抽样（单文件、限制文件长度/改动大小/行变更比、message 质量、按语言均衡）24,460 条→LLM 生成显式改动描述与 update_snippet/完整 final_code→一致性校验（diff 必须完全且只能由 snippet 解释，删 2,960=12.1%）→可解性过滤（3 个强模型各 2 次共 6 attempts，5 或 6 次全败样本丢弃，删 516=2.4%）⇒ 20,984 条（19,347 训练/1,637 测试，按 commit 切分，20 种语言）。训练 Qwen3-4B（64k）：SFT 整文件交叉熵；GRPO 用语言/格式感知的等价奖励（代码 Pygments token 级、JSON/YAML/XML 先规范化、MD/SQL 格式规范化）＋按错误类型加权的密集奖励 r=max(0,1−0.25·patch_errors−0.35·side_effects)，区间外副作用罚更重。SFT 版 94.4%（该等价口径）超 DeepSeek-V3.2 91.6%；RL 版 1.45s 下 0.938（Qwen3.5-397B 0.948）；无草稿模型投机解码（n-gram+suffix）单 A100 约 2,700 tok/s、端到端延迟约 75× 低于 API 版；IDE 部署把 Apply 平均延迟 50s→1.89s，按时间容量规划替换 5 个上游实例中的 1 个可省 20% 上游机器成本；100 条真实开发任务 91 条首次输出可接受。⚠️ 作者自报（含厂商实测）、本线未复现；语言感知等价会放宽判分（94.4% 为该口径，严格字符串比较更低）；可解性过滤依赖具体模型、对困难样本有偏。',
}
AREAS = {
    '2611.07595': ['agent 经验复用', 'Gene 资产', '不改参数', '配对实验', 'Terminal-Bench 2.1', 'SWE-rebench', 'token 成本', 'harness'],
    '2611.08452': ['可复现性', '工件标准化', '执行证据审计', '参考变异', '多参考面板', 'CPU-only 任务', '测量口径'],
    '2611.07634': ['代码 Apply', '数据漏斗', '一致性校验', '可解性过滤', '语言感知等价判分', '密集奖励', 'GRPO', '投机解码', '小模型专精'],
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
