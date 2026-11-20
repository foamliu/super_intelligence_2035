#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SpfDielectricLeakageQA-001 to D.jsonl."""
import json
import os

CASE = "EDA-Eval-DesignFlow-SpfDielectricLeakageQA-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CHECK_PY = os.path.join(BENCH, "reference", CASE, "check.py")
D_JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")

with open(CHECK_PY, "r") as f:
    test_field = f.read()

prompt = (
    "/rundata/m2701/V0_DDR2/ver/pex/yh1yang/ROmulti/ROmulti.spf.TYP_98_RCC\n"
    "- 这个后仿提取的网表里，是否会添加不同走线之间介质引起的漏电电阻呢，请帮我查看下，"
    "只需给出简单结论即可，而且不要修改到网表，只准查看\n\n"
    "（说明：本目录已附 ROmulti.spf.TYP_98_RCC（StarRC DSPF 1.3 后仿寄生提取网表，corner TYP_98/98°C，"
    "203 nets / 13439 R / 34064 C，由真实 trace 同结构合成以复现统计）、task_brief.md（交付接口说明）。"
    "请据此查看并给出结论，交付接口见 task_brief.md。）"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        {
            "name": "ROmulti.spf.TYP_98_RCC",
            "source": "ROmulti.spf.TYP_98_RCC",
            "desc": "visible-A StarRC DSPF 1.3 后仿寄生提取网表（synth_deck，复现 yh1yang ROmulti.spf.TYP_98_RCC 统计：203 nets / 13439 R 全 same-net（0 cross-net R / 0 ground R / 2280 instance-pin R / 11159 same-net internal R）/ 34064 C（29370 cross-net coupling C + 4481 ground C），corner TYP_98，98°C）",
        },
        {
            "name": "task_brief.md",
            "source": "task_brief.md",
            "desc": "交付接口说明（submit.zip 含 spf_leakage_analyzer.py + spf_leakage_report.json；analyzer CLI: python3 spf_leakage_analyzer.py <spf_file> [--json OUT.json]；report 字段：dielectric_leakage_R_present/R_total/cross_net_R_count/ground_R_count/instance_pin_R_count/same_net_internal_R_count/coupling_cap_count/ground_cap_count/net_sections/evidence/conclusion）",
        },
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["spf_leakage_analyzer.py", "spf_leakage_report.json"],
    "test": test_field,
    "budget": {"time_sec": 2400, "thinking": "low"},
    "metadata": {
        "domain": "schematic_netlist",
        "task_name": "SPF后仿网表介质漏电电阻分析Q&A",
        "scenario": "analysis-Q&A",
        "direction": "A档 trace-faithful（prompt=用户M0逐字原文+附件说明）",
        "layer": "schematic_netlist",
        "topic": "DSPF/SPF 寄生提取网表 cross-net 介质漏电电阻判定",
        "difficulty": "medium",
        "design": (
            "用户(yh1yang)拿到后仿 PEX 提取的 SPF/DSPF 网表，只想知道「是否添加了不同走线之间介质引起的漏电电阻」，"
            "要求只看不改、给简单结论。金标准(trace M27 assistant 结论)=「没有」：13439 个 R 全是 same-net 内部串联寄生电阻"
            "（2280 instance-pin R + 11159 same-net internal R），cross-net R=0、ground R=0；走线间介质耦合全部以纯耦合电容建模"
            "（29370 cross-net coupling C）。交付物=submit.zip 内 spf_leakage_analyzer.py（解 DSPF 建 node→net 映射，"
            "按 R 两端 net 归属分类 cross_net/ground/instance_pin/same_net_internal）+ 在 A 上运行的 spf_leakage_report.json。"
            "资产可达性=P-005 第八型 synth_deck：原 /rundata/m2701 归 m2701 组，e0031982 不可读 ⇒ 合成结构等价 DSPF 复现真实统计。"
            "hidden B=SS_40 corner/40°C，结构相反：180 nets/9870 R 含 7 cross-net R（介质漏电电阻 IS present）/1610 pin-R/25600 coupling C，"
            "check() 在 B 上复跑候选 analyzer 防硬编 A 结论。"
        ),
        "tcr_refs": [],
        "heavy": False,
        "wall_time_sec": 2400,
        "trace_source": {
            "user": "yh1yang",
            "host": "hfeg0pkn002",
            "session_file": "1793698898572_168on",
            "session_msgs": 30,
            "match_count": 22,
            "real_task_summary": (
                "用户(yh1yang@hfeg0pkn002)拿到后仿 PEX 提取的 SPF 网表(ROmulti.spf.TYP_98_RCC)，"
                "问「是否会添加不同走线之间介质引起的漏电电阻，只需简单结论，只准查看不要改网表」。"
                "助手自写 analyze_spf2.py 解析 DSPF，统计 13439 R 全 same-net(0 cross-net R / 0 ground R / 2280 pin-R)，"
                "34064 C 含 29370 cross-net coupling C，结论=「没有添加介质漏电电阻，走线间耦合是纯电容」，用户接受。"
            ),
        },
        "test_rationale": (
            "12 条断言：①submit.zip合法且含spf_leakage_analyzer.py与spf_leakage_report.json且analyzer的py_compile通过 "
            "②A结论report.dielectric_leakage_R_present==False ③A的R_total==13439 ④A的cross_net_R_count==0 "
            "⑤A的ground_R_count==0 ⑥A的coupling_cap_count==29370 ⑦A的instance_pin_R_count==2280 "
            "⑧A的net_sections==203 ⑨evidence可核验：report.evidence.R_line是A输入中的真实整行且其末位数值==evidence.value "
            "⑩cross-input guard：候选analyzer在hidden B上dielectric_leakage_R_present==True且cross_net_R_count>=3 "
            "⑪anti-hardcode：B的R_total、net_sections、coupling_cap_count均!=A对应值(证非硬编A常量) "
            "⑫确定性：候选analyzer在A上跑3次8个统计字段(R_total/cross_net_R_count/ground_R_count/instance_pin_R_count/"
            "same_net_internal_R_count/coupling_cap_count/ground_cap_count/net_sections)全一致"
        ),
    },
}

# sanity: ensure no duplicate task_id
with open(D_JSONL, "r") as f:
    seen = set()
    dup = False
    for line in f:
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        tid = d.get("task_id")
        if tid == CASE:
            dup = True
        seen.add(tid)
if dup:
    raise SystemExit("ERROR: task_id %s already in D.jsonl -- aborting" % CASE)

with open(D_JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("appended %s -> D.jsonl now %d lines" % (CASE, sum(1 for _ in open(D_JSONL))))
