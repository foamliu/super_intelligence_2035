#!/usr/bin/env python3
"""
R90: SFT课程学习配比优化设计
基于R88/R89结论设计四阶段SFT课程配比
"""
import os
import json
from collections import defaultdict

SFT_CORPUS = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/sft_pyaether_corpus_v2.jsonl"
REPORT = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_posttrain_sft_curriculum_zh.html"
CONFIG = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/sft_curriculum_config.json"

def main():
    # 分析语料
    corpus = []
    with open(SFT_CORPUS, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                corpus.append(json.loads(line))
    
    stats = {"total": len(corpus), "has_args": sum(1 for x in corpus if x.get("has_args", False)), "diff_dist": defaultdict(int)}
    for item in corpus:
        tc = item.get("tool_calls", 0)
        turns = item.get("turns", 1)
        if tc == 0 or turns == 1:
            stats["diff_dist"]["L1"] += 1
        elif tc <=3:
            stats["diff_dist"]["L2"] +=1
        elif tc <=10:
            stats["diff_dist"]["L3"] +=1
        else:
            stats["diff_dist"]["L4"] +=1
    
    # 课程设计
    curriculum = {
        "phases": [
            {"name": "基础认知", "ratio": 0.15, "mix": {"L1":0.7, "L2":0.3}, "objective": "掌握工具格式与search_apis"},
            {"name": "单工具使用", "ratio":0.25, "mix":{"L1":0.2, "L2":0.6, "L3":0.2}, "objective":"单API调用"},
            {"name": "多工具协同", "ratio":0.35, "mix":{"L2":0.2, "L3":0.6, "L4":0.2}, "objective":"多API协同+错误修复"},
            {"name": "复杂任务", "ratio":0.25, "mix":{"L3":0.3, "L4":0.7}, "objective":"复杂场景处理"}
        ],
        "data_mix": {"通用SFT":0.3, "通用Agent":0.2, "PyAether":0.5},
        "expected_improvement": "工具合法率>98%，search_apis使用率>95%，Pass@1>50%"
    }
    
    # 保存配置
    with open(CONFIG, 'w', encoding='utf-8') as f:
        json.dump(curriculum, f, ensure_ascii=False, indent=2)
    
    # 生成HTML
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>R90 SFT课程设计</title></head>
<body><h1>R90 SFT课程学习配比优化设计</h1>
<h2>语料统计</h2><p>总样本：{stats['total']:,}，含参数：{stats['has_args']/stats['total']:.1%}</p>
<h3>难度分布：</h3><ul>
{"".join(f"<li>{k}: {v:,} ({v/stats['total']:.1%})</li>" for k,v in stats['diff_dist'].items())}
</ul>
<h2>四阶段课程</h2>
{"".join(f"<h3>Phase {i+1}: {p['name']}（占比{p['ratio']:.0%}）</h3><p>目标：{p['objective']}</p><p>难度配比：{p['mix']}</p>" for i,p in enumerate(curriculum['phases']))}
<h2>数据混合</h2><p>通用SFT 30% + 通用Agent 20% + PyAether领域 50%</p>
<h2>预期效果</h2><p>{curriculum['expected_improvement']}</p>
</body></html>"""
    
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"完成：配置保存在{CONFIG}，报告保存在{REPORT}")

if __name__ == "__main__":
    main()
