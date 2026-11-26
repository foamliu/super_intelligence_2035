#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001 to EDA-Eval-DesignFlow_A.jsonl"""
import os, json

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001"
REF = os.path.join(BENCH, "reference", CASE)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")

with open(os.path.join(REF, "check.py"), "r", encoding="utf-8") as f:
    check_src = f.read()

# trace_source
trace_source = {
    "user": "alan3zh",
    "host": "hfeg0plg49",
    "session_file": "1793621923074_i9chj/1793621923074_i9chj.messages.json",
    "match_count": 401,
    "real_task_summary": (
        "Innovus fp 阶段 IMPSR-1253 告警诊断 + innovus_fp.tcl 分代网表感知修复会话：用户 alan3zh "
        "在 hfeg0plg49 上要求「进入./apr/logs查看inv_fp.log，其中有告警：(IMPSR-1253) Unable to "
        "find any standard cell pin connected to the VDD_PM net. 查询问题原因」。轮[U#1] 给告警症状"
        "问根因（未给根因/修复方案）→规则②不命中→A 档（faithful）。金标 = trace 助手 A#2–A#65 真实"
        "诊断+修复链：根因 = 新 DC 网表 dc_2026-11-02-20.29.45 已自带电源意图，PM 子树 "
        "PMArrayPart(TOPPMBLK)→PMVDDIMatrixPart(PM_VDDI_Inst)→21×PMVDDIRowPart→21×INVD8(PMRowBLK_*) "
        "= 441 leaf，leaf .VDD 接模块局部 VDD_PM 网，经层次端口 .VDD_PM(VDD_PM)（非 .VDD）链到顶层 "
        "VDD_PM；GNC 找名为 VDD 的 pin → 0 leaf std-cell pin → VERIFY 1 instTerm, 0 leaf → sroute "
        "报 IMPSR-1253，fp 阶段属预期（netlist-level pd_pm isolation，leaf hookup 在后续 power "
        "routing 段）。修复 innovus_fp.tcl：_pm_nl dbGet 分代探测 → 新网表跳过无效 GNC + VERIFY 区分 "
        "leaf pin 与 hierarchy port + 旧网表走 manual addNet+GNC -instanceBasename -netlistOverride + "
        "UPF-aware + *VDDI_Inst* 保留；_apr_setup_validate.py ALL PASSED。"
    )
}

TEST_RATIONALE = (
    "16 条断言：①submit.zip 恰含 2 个文件 innovus_fp.tcl 与 diagnose.json "
    "②innovus_fp.tcl 通过 Tcl `info complete` 语法完整性检查 "
    "③diagnose.json 含全部 7 个必需键（net_name/impsr1253_verdict/root_cause/pm_subtree/dc_revision/leaf_pin_count/hierarchy_port） "
    "④diagnose.json 的 impsr1253_verdict 标记 EXPECTED at floorplan（fp 阶段预期，非错误） "
    "⑤diagnose.json 的 root_cause 描述隔离机制（含 hierarchy/local/leaf/netlist/port 中 ≥3 个关键词） "
    "⑥diagnose.json 的 leaf_pin_count == 0（VERIFY 报 0 leaf std-cell pin） "
    "⑦diagnose.json 的 hierarchy_port 非空（描述 .VDD_PM(VDD_PM) 式层次端口） "
    "⑧diagnose.json 的 pm_subtree 含叶单元计数值（441 等数字） "
    "⑨diagnose.json 的 dc_revision 非空（记录 DC 网表版本） "
    "⑩diagnose.json 的 net_name 非空（诊断锁定 IMPSR-1253 告警的目标 net） "
    "⑪innovus_fp.tcl 含分代探测 dbGet top.nets.name $<变量>（非硬编码字面量） "
    "⑫innovus_fp.tcl 含 globalNetConnect 手动回退路径并带 -instanceBasename 与 -netlistOverride "
    "⑬innovus_fp.tcl 含 VERIFY 逻辑区分 leaf std-cell pin 与 hierarchy port pin "
    "⑭anti-hardcode：innovus_fp.tcl 不得用 `set <var> VDD_PM` 裸赋值硬编码 A 的 net 名 "
    "⑮stub 在隐藏 B（VDD_SENS / SENS_VDDI_Inst / 216 leaf / 不同 revision）上跑候选 tcl：exit 0 + dbGet 命中 VDD_SENS + 未 addNet VDD_PM + 未 globalNetConnect PMRowBLK_* "
    "⑯innovus_fp.tcl 头部注释提及 IMPSR-1253 与 floorplan"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": "进入./apr/logs查看inv_fp.log，其中有告警：Begin power routing ... **WARN: (IMPSR-1253): Unable to find any standard cell pin connected to the VDD_PM net. 查询问题原因",
    "attachments": [
        "assets/EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001/inv_fp.log",
        "assets/EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001/innovus_fp.tcl",
        "assets/EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001/dc_netlist_A.v",
        "assets/EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001/power.globals",
        "assets/EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001/task_brief.md",
    ],
    "test": check_src,
    "metadata": {
        "trace_source": trace_source,
        "domain": "pnr_signoff",
        "track": "faithful",
        "level": "L2",
        "harness": "cline",
        "test_rationale": TEST_RATIONALE,
    }
}

# dedup guard
existing_ids = set()
with open(JSONL, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                existing_ids.add(json.loads(line)["task_id"])
            except Exception:
                pass
if CASE in existing_ids:
    print("SKIP: %s already in jsonl" % CASE)
    raise SystemExit(0)

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify roundtrip: test field == disk check.py
with open(JSONL, "r", encoding="utf-8") as f:
    last = None
    for line in f:
        if line.strip():
            last = json.loads(line)
assert last["task_id"] == CASE
assert last["test"] == check_src, "test field != disk check.py"
# count assertions vs check conditions
import re
k_rationale = TEST_RATIONALE.count("①") + sum(1 for i in range(2,17) if chr(0x245f+i) in TEST_RATIONALE)
# check.py condition labels a-p = 16
k_check = len(re.findall(r'_cond\("([a-z])"', check_src))
print("k_rationale =", k_rationale, " k_check =", k_check)
print("test==disk roundtrip OK, bytes =", len(check_src))
print("A jsonl lines now =", sum(1 for l in open(JSONL) if l.strip()))
