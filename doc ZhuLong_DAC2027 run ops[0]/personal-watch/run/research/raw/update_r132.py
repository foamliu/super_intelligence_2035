#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百三十二轮落盘（2026-11-04 PM 晚 2 篇「科普」）。

幂等：已存在的 ID 不重复追加；断言 published 前缀与官方 XML 一致。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
SEEN=BASE/'SEEN.md'; PAPERS=BASE/'papers.jsonl'
XML=BASE/'raw'/'2026-11-04-pm-idlist-r132a.xml'
NS={'a':'http://www.w3.org/2005/Atom','x':'http://arxiv.org/schemas/atom'}
FIRST={'2611.05290':'2026-11-04','2611.05148':'2026-11-04'}
SUMMARY={
'2611.05290':'把「假安慰」定义为一个可测的失败模式：官方已发布严重天气警报、而 LLM 助手看不到警报数据时，它可能告诉用户「目前平静」。作者把 2026-10-19~10-23 采集的真实 NWS 警报冻结为 117 个可重放案例（69 个警报案例 / 32 个无警报对照 / 16 个非美国地点），用同一 Claude 管线的 5 种条件重放（温度 0、500 token 上限）：完整生产管线假安慰 0.0%（0/66）、只给警报数据配中性提示 0.0%（0/69）、「失明」中性提示 37.7%（26/69）、失明且被要求披露盲区 44.9%（31/69）。所有案例均为隐式（无一条明确否认警报存在）。配对 McNemar：真实警报显著消除假安慰（p<0.0001），「要求披露盲区」无显著作用（p=0.40）。自动正则指标方向相反、漏掉 57 个真案例中的 53 个，故弃用。只有警报数据也不够：中性提示下 87.5% 的无警报对照被拉响警报，生产提示为 0%。另报告两个常见失效：把 NWS 测试产品当作真实警报、复杂案例撞 token 预算。⚠️ 作者自报、未复现；单评审者手标、单模型家族（Claude Sonnet 4.6）、单季节试点；采集机 77% 时间休眠 ⇒ 偏向长时警报；最终集合无 Extreme 级别。',
'2611.05148':'把「查询路由」当成数据中心的电网调节手段：不推迟请求，而是把「对模型不敏感」的查询在大小模型实例之间动态分配，从而改变 LLM 推理功率。作者由查询到达率与序列长度分布推出平均 token 迭代时间、请求驻留时间、服务容量与功率的解析模型（H100 上 R²>0.99），据此刻画可行路由分配与对应功率灵活性（预测误差约 2.8% MAPE）。在 10,000 张 H100 的模拟数据中心（大/小实例 3:1 = Llama-3.1-70B 四卡张量并行 + Mistral-24B 单卡）上跑一周 Azure 真实聊天 trace：基线设施功率 6–9.1 MW（均值 7.3 MW）；50% 查询可路由时削减 0.6 MW，100% 可路由时 1.19 MW = 均值功率的 16%；四小时削减事件中降功率 2.4 / 4.8 MWh，约 10 s 达到目标降幅的 90%。⚠️ 作者自报、未复现；以模拟为主（trace 驱动 + 实测功率模型），不是真实电网联动；设施功耗用「每 GPU 额外 300 W + PUE 1.2」近似；可路由查询占比为假设扫描，真实业务可用比例未验证。',
}
AREAS={
'2611.05290':['LLM 安全','严重天气','假安慰','安全关键建议','可重放评测','智能体工具访问'],
'2611.05148':['数据中心','功率灵活性','查询路由','LLM 服务','电网互动','能效'],
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
        m=meta[aid]; assert m['published'].startswith('2026-11-03'), (aid,m['published'])
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
