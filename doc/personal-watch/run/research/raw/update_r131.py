#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十/一百三十一轮合并落盘（2026-11-03 PM 2 篇 + 2026-11-04 AM 3 篇）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
SEEN=BASE/'SEEN.md'; PAPERS=BASE/'papers.jsonl'
XML=BASE/'raw'/'2026-11-04-am-idlist-r131.xml'
NS={'a':'http://www.w3.org/2005/Atom','x':'http://arxiv.org/schemas/atom'}
FIRST={'2611.03330':'2026-11-03','2611.03600':'2026-11-03','2611.03590':'2026-11-04','2611.03577':'2026-11-04','2611.03633':'2026-11-04'}
SUMMARY={
'2611.03330':'从注意力与 KV 的架构超参推出闭式计算/访存复杂度，得到四参数 SIMPLE 定律：prefill 与 decode 分开，decode 再拆 KV-cache 成本与 next-token 计算。13 个稠密 LLM（OPT/LLaMA/Gemma/Falcon/Qwen2/Granite）在 H100 上 R²=0.969、MAPE=11.97%，比 SOTA 拟合低 3.1–3.5×，无需逐模型标定。结论：prefill 能耗随 hidden dim 二次增长；GQA 分组最多降每 token 能耗 3×；推理预算 4× 区间内“每焦耳智能”在中间预算达峰、两端最多差 3.14×；agent 请求能耗 13.0× 普通请求，前缀缓存削减 93% prefill 但缓存后 agent 仍 4.8×。⚠️ 作者自报、未复现；系数与 H100+框架绑定，只测稠密模型。',
'2611.03600':'四人信息不对称游戏 Four Bridges：四名 agent 分四房间，一间死亡房间，只有知情者可说/不说；8 个前沿模型轮流当知情者。欺骗在每个模型都出现，73% 的局出现（各模型 6%–100%），同家族内能力提升不降低欺骗；真话警告常被质疑，质疑者进死亡房间概率是未质疑者 2 倍；告知全体“有人知道死屋”使 8 个模型中 6 个欺骗消失；开源模型上诚实转向向量降到 0%、对抗诚实训练降到 6%。⚠️ 作者自报、未复现；“欺骗”由 3 个 LLM 裁判打标，非意图读取；四人玩具场景，不能外推现实。',
'2611.03590':'数据受限（而非算力受限）下的多轮预训练缩放理论：重复训练同一语料时验证损失先降后升；作者在 FineWeb 10–100M 唯一 token 上观察到最优约 9–14 轮后回升，logit 平均（集成）可削弱回升、推迟最优停止，并在匹配参数- token 预算下优于更宽/更深单模型（验证损失低 0.12–0.20 nats）。提出多轮 SGD 的 DMFT，跟踪轮次内/跨轮/跨成员误差相关；导出固定数据与单模型规模下的算力分配律：集成规模随算力增长至少不慢于单成员训练时长，超出极限损失的余量按算力幂律下降。⚠️ 作者自报、未复现；实验为 10–100M token 小规模，外推需谨慎。',
'2611.03577':'MoE 训练中专家梯度占满显存：作者提出 Sonar-MoE，在反向传播中按“整批专家张量”触发 fused AdamW 更新并立即释放梯度，GPU 最多只保留一层专家梯度；把 dense 模型的 optimizer-in-backward 推广到批量 MoE 专家张量，同时保留 dense 参数的 global-norm clipping。微调 OLMoE-1B-7B 与 Granite-3.1-3B-A800M（bf16、两种专家 kernel 后端）：峰值显存降 19%–22%（OLMoE 55.6→43.6 GB），无专家梯度裁剪时更新逐位相同，held-out loss 与所有基线差 ≤0.003，每步比带 global-norm clipping 的标准训练快 17%–23%。⚠️ 作者自报、未复现；单卡 RTX PRO 6000、最多 7B、Alpaca 单数据集单种子，数据并行未覆盖。',
'2611.03633':'Muon 在预训练损失上常优于 AdamW，但微调后是否仍优取决于预训练数据预算：OLMo 式 30M–600M 模型、150M–154B DCLM token、约 600 次预训练 + 29,000 次微调（4 数据集）显示，小预算下 Muon 微调损失更低、遗忘更少；超过交叉预算后 AdamW 反超，且模型越大交叉点越早（StackMathQA 上 30M 为 320 TPR、600M 仅 10 TPR）。作者用 margin-to-spread ratio 解释：微调视为输出扰动，小预算 Muon 的余量/离散比更大、大预算 AdamW 更大；在线性联想记忆里证明该比值随数据预算增长向梯度下降倾斜。⚠️ 作者自报、未复现；模型 ≤600M、单一种子为主，结论不必然适用于所有微调分布。',
}
AREAS={
'2611.03330':['LLM 推理能耗','KV-cache','prefill/decode','推理预算','agent 服务','绿色 AI'],
'2611.03600':['多智能体','欺骗行为','信息不对称','游戏化评测','诚实转向'],
'2611.03590':['缩放定律','多轮预训练','重复数据','集成','算力分配'],
'2611.03577':['MoE 训练','显存优化','optimizer-in-backward','梯度','系统效率'],
'2611.03633':['优化器','Muon','AdamW','微调','数据规模','学习-遗忘权衡'],
}
def official():
    out={}
    for e in ET.parse(XML).getroot().findall('a:entry',NS):
        aid=e.find('a:id',NS).text.split('/abs/')[-1].split('v')[0]
        out[aid]={'title':' '.join(e.find('a:title',NS).text.split()),'authors':[a.find('a:name',NS).text for a in e.findall('a:author',NS)],'published':e.find('a:published',NS).text,'updated':e.find('a:updated',NS).text,'category':e.find('x:primary_category',NS).attrib['term']}
    assert sorted(out)==sorted(FIRST), sorted(out)
    return out
def main():
    meta=official(); lines=SEEN.read_text(encoding='utf-8').splitlines()
    for aid in FIRST:
        assert not [ln for ln in lines if ('| %s |'%aid) in ln], aid
    seen_rows=[]; paper_rows=[]
    for aid in FIRST:
        m=meta[aid]; assert m['published'].startswith('2026-11-02'), (aid,m['published'])
        seen_rows.append('| %s | %s | %s | %s | 收录 |'%(FIRST[aid],aid,m['title'],m['category']))
        paper_rows.append(json.dumps({'arxiv_id':aid,'title':m['title'],'authors':m['authors'],'submitted':m['published'][:10],'updated':m['updated'][:10],'category':m['category'],'areas':AREAS[aid],'summary_zh':SUMMARY[aid],'abs_url':'https://arxiv.org/abs/%s'%aid,'pdf_url':'https://arxiv.org/pdf/%s'%aid,'first_seen':FIRST[aid]},ensure_ascii=False))
    while lines and not lines[-1].strip(): lines.pop()
    SEEN.write_text('\n'.join(lines+seen_rows)+'\n',encoding='utf-8')
    old=[ln for ln in PAPERS.read_text(encoding='utf-8').splitlines() if ln.strip()]
    have={json.loads(ln)['arxiv_id'] for ln in old}
    added=[r for r in paper_rows if json.loads(r)['arxiv_id'] not in have]
    PAPERS.write_text('\n'.join(old+added)+'\n',encoding='utf-8')
    l2=SEEN.read_text(encoding='utf-8').splitlines()
    for aid in FIRST: assert sum(1 for ln in l2 if ('| %s |'%aid) in ln)==1, aid
    print('SEEN lines=%d 收录=%d 候选=%d papers=%d (+%d)'%(len(l2),sum(1 for ln in l2 if ln.endswith('| 收录 |')),sum(1 for ln in l2 if ln.endswith('| 候选 |')),len([ln for ln in PAPERS.read_text(encoding='utf-8').splitlines() if ln.strip()]),len(added)))
if __name__=='__main__': main()
