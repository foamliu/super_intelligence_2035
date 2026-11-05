#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-PortTextPlan-001 to shard C jsonl."""
import json
import os

CASE_ID = "EDA-Eval-DesignFlow-PortTextPlan-001"
REF_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/" + CASE_ID
ASSETS_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/" + CASE_ID
JSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_C.jsonl"

check_src = open(os.path.join(REF_DIR, "check.py")).read()

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "prompt": open(os.path.join(ASSETS_DIR, "prompt.txt")).read(),
    "attachments": [
        {"name": "prompt.txt", "source": "prompt.txt",
         "desc": "ellawu 真实场景（cline 分析 Cadence SKILL cxmt_autoPR_generatePortText.il 版图端口文本生成脚本）+ 沙盒注（离线可计算核心：transform/去重/project 字体/方向）+ 规则表 + 交付接口"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "交付接口 ≤3 行：outputs/submit.zip → port_text_plan.py；argv <spec.json> <out.json>；check 双参只跑 hidden B"},
        {"name": "port_text_spec_A.json", "source": "port_text_spec_A.json",
         "desc": "A 样例 spec（cellName=TopPR, project=degpa, 4 instances, R90/R0 transform, bBoxMap/pinCenter 去重场景，供理解格式与本地试跑）"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["port_text_plan.py"],
    "test": check_src,
    "budget": {"max_turns": 25, "wall_time_sec": 1200},
    "metadata": {
        "domain": "layout_virtuoso",
        "task_name": "PortTextPlan",
        "scenario": "Cadence SKILL cxmt_autoPR_generatePortText.il 版图端口文本生成：底层子单元 pin-label/pin-shape 经 instance transform 浮到顶层，以顶层端口名创建 dbCreateLabel/leCreatePin/dbCreateTextDisplay；按 PROJ_NAME 选字体、ADIE_PERI 特殊处理、三重去重",
        "direction": "parse JSON spec of top cellview + instances(transform) + sub-cell pin labels/shapes + pin_terminal_map + existing labels/pin-centers + project/cellName; emit ordered port-text creation ops with faithful dbTransformPoint/dbTransformBBox (8 orientations), 3-decimal rounding, bBoxMapLabel/createdTextList/pinCenterBox dedup, project font+orient case, pin direction lookup",
        "layer": "L1-boundary",
        "topic": "skill-porttext-plan-transform-dedup",
        "difficulty": "L1-medium",
        "design": "B-faithful-seed-B-synthesized",
        "tcr_refs": ["cxmt_autoPR_generatePortText.il", "cxmt_generatePortTextCell", "dbCreateLabel",
                     "leCreatePin", "dbCreateTextDisplay", "dbTransformPoint", "dbTransformBBox",
                     "schTraceNetToConn", "pinTerminal_table", "bBoxMapLabel_table", "pinCenterBox",
                     "ADIE_PERI", "degpa", "dqpoa", "dqrmb", "drgpa", "decoa", "lhiou", "R90MX",
                     "centerCenter", "roman", "purpose==pin", "port text", "AutoPR"],
        "heavy": False,
        "wall_time_sec": 1200,
        "trace_source": {
            "host": "hfeg0pkn001",
            "user": "ellawu",
            "session_file": "1791615357921_izmw3",
            "session_msgs": 247,
            "match_count": 206,
            "real_task_summary": "ellawu 在 /home/ellawu/ 下用 cline 分析 Cadence SKILL 脚本 cxmt_autoPR_generatePortText.il（CXMT AutoPR 流程版图端口文本生成）。USER#1 逐字「分析一下这个脚本」+ 上传 cxmt_autoPR_generatePortText.il；USER#2-3 问「能实现从底层浮 pin 到顶层吗」「instance 重新摆放 location 变化吗」；USER#4 上传 cxmt_autoPR_generatePortText_allNet.py 再分析；USER#7「给我一个完整的可运行的 python脚本」。agent 主要做 prose 分析（schTraceNetToConn 建 instance#terminal->topSignalName 映射、dbTransformPoint 坐标变换、dbCreateLabel/leCreatePin/dbCreateTextDisplay 创建、bBoxMapLabel 去重、pinCenterBox 重叠去重、PROJ_NAME case 选字体、ADIE_PERI 特殊分支），并 heredoc 产出一版 Python 后删除。真实 gold 依赖 live Virtuoso OA 不可离线静默判分，故取其「离线可计算核心」做 B 档 synthesized：给定 spec JSON 离线计算端口文本创建操作序列。",
        },
        "test_rationale": "13 条断言：①(a) zip 含 port_text_plan.py 非空且 py_compile 通过 ②(b) 候选脚本在 hidden B 上 subprocess 运行 exit 0 无 Traceback 且产出有效 JSON operations 列表 ③(c) X0 label:P dbCreateLabel xy==[198,197] text PVDD layer[MT,pin] orient R90 height 0.2（R180 transform + ADIE_PERI 用 label 自身 orient）④(d) X0 label:N dbCreateLabel xy==[194,193] text PVSS orient R0（ADIE_PERI 用 label 自身 orient，与 P 的 R90 不同，证 orient 取自 label 而非硬编码）⑤(e) X0 pin:P leCreatePin bBox==[[180,180],[190,190]] name PVDD direction inputOutput layer[MT,pin] access[left,right]（dbTransformBBox R180 + 方向查表）⑥(f) X0 pin:P dbCreateLabel xy==[185,185] PVDD orient R0 height 0.2（dqpoa 项目 pin 路径产 dbCreateLabel 而非 dbCreateTextDisplay，且 X0 无 dbCreateTextDisplay）⑦(g) X2 pin:IN 无 leCreatePin（pinCenterBox 与已有 [400,400] 重叠去重）但仍产 dbCreateLabel xy==[400,400] text SIGIN（dqpoa 即使重叠也产 label）⑧(h) X1 无任何操作（bBoxMapLabel 在已有 PVDD label [50,50] 去重，label+pin 两路径皆跳过）⑨(i) X3 无任何操作（bBoxMapLabel 在已有 TIEHI label [220,330] 去重）⑩(j) X4 label:A dbCreateLabel xy==[500,103] text BUS_A orient R0 height 0.2（R90MX orient 矩阵 + scale[2,1] transform）⑪(k) X5 pin:T2 leCreatePin direction inputOutput（topsig UNK 非顶层 terminal -> 默认方向 inputOutput）且 dbCreateLabel text UNK ⑫(l) cross-input guard：候选源码不得硬编码 A 专属 token（TopPR/VDD/CLK/RSTN/GND/I0#A/I1#A/I2#A/I3#A/98.0/96.0/305.0），且 B 专属信号 PVDD/PVSS/SIGIN/BUS_A/UNK 必须出现在输出（防 fake_print_expected 硬编码 A 输出）⑬(m) 3 次 subprocess 运行 out.json 字节级 md5 一致（确定性）",
    },
}

# roundtrip check: test field bytes must equal disk check.py
import hashlib
disk_md5 = hashlib.md5(open(os.path.join(REF_DIR, "check.py"), "rb").read()).hexdigest()
test_md5 = hashlib.md5(check_src.encode("utf-8")).hexdigest()
assert disk_md5 == test_md5, "test field != disk check.py (md5 %s vs %s)" % (test_md5, disk_md5)
print("test==disk check.py roundtrip md5 OK:", disk_md5)

# k gate
import re
k_rat = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬]", entry["metadata"]["test_rationale"]))
labels = re.findall(r'AssertionError\("\(([a-z])\)', open(os.path.join(REF_DIR, "check.py")).read())
k_check = len(set(labels))
assert entry["metadata"]["test_rationale"].startswith("13 条断言："), "rationale prefix missing"
assert k_rat == 13 and k_check == 13 and k_rat == k_check, "k gate: k_rat=%d k_check=%d" % (k_rat, k_check)
print("assertion GATE: k_rationale=%d k_check=%d (>=8) PASS" % (k_rat, k_check))

# append (no dup)
existing = open(JSONL).read().splitlines()
for line in existing:
    if line.strip():
        e = json.loads(line)
        if e["task_id"] == CASE_ID:
            print("ALREADY PRESENT, skipping append"); raise SystemExit(0)

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", CASE_ID, "to", os.path.basename(JSONL))
print("jsonl lines now:", sum(1 for l in open(JSONL) if l.strip()))
