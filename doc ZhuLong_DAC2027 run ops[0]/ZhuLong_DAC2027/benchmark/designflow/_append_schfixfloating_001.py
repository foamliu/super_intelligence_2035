#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SchFixFloating-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json
import os

CASE_ID = "EDA-Eval-DesignFlow-SchFixFloating-001"
REF_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/" + CASE_ID

with open(os.path.join(REF_DIR, "check.py")) as f:
    test_src = f.read()

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_src,
    "prompt": (
        "目前窗口的schemetic报错，帮我修一下，指名报错原因。"
    ),
    "attachments": [
        "assets/%s/config_A.json" % CASE_ID,
        "assets/%s/prompt.txt" % CASE_ID,
        "assets/%s/task_brief.md" % CASE_ID,
    ],
    "metadata": {
        "domain": "schematic_netlist",
        "level": "L1-boundary",
        "track": "faithful",
        "test_rationale": (
            "15 条断言："
            "①submit.zip 含 gen_fix_sch.py（对象=压缩包成员，判定=存在）"
            "②gen_fix_sch.py 可 py_compile（对象=脚本，判定=语法合法）"
            "③在隐藏 B 上 python3 gen_fix_sch.py 退 0 并写出 fix_schematic.il + fix_plan.json"
            "（对象=生成器运行，判定=成功产出两文件）"
            "④fix_schematic.il 调 dbOpenCellViewByType 且 mode=\"a\"（对象=打开方式，判定=编辑模式）"
            "⑤let((<vars>)) 独立绑定且无多赋值 setq `(setq a x b y)`（对象=局部绑定，判定=合法单赋值）"
            "⑥Fix1 dbSetInstTermNet 把错连 global net 换成正确 net，且 B 的 wrong_net 串（0!）出现在 .il"
            "（对象=global net 替换，判定=实例端子改连正确 net）"
            "⑦Fix2 dbDeleteObject 删浮空 net 的 dangling wires（oldNet~>shapes）（对象=悬空连线，判定=删除）"
            "⑧Fix3 dbSetInstTermNet 连浮空 instTerm↔ipin，B 的 ipin 名 PINP/PINN 出现（对象=浮空端子，判定=连到对应 ipin）"
            "⑨fix_schematic.il 调 dbSave(cv)（对象=保存，判定=落盘）"
            "⑩Cleanup foreach nets 当 connections==nil && shapes==nil 时 dbDeleteObject（对象=孤儿 net，判定=清理）"
            "⑪fix_plan.json errors_count == B 期望 6（对象=错误计数，判定=等于 B）"
            "⑫fix_plan.json floating_inst_terms==[INP,INN] 且 floating_nets==[net9]（对象=浮空清单，判定=等于 B）"
            "⑬fix_plan.json cellview==AmpTB_B 且 cell==amp_top 且 lib==analog_bb（对象=标识，判定=匹配 B）"
            "⑭跨输入护栏：A-only 串（pre_sim/I_pre_0/gnd!/PIN0/net5/VSS 等）不出现，B-must 串（AmpTB_B/I_drv/0!/GND/INP/INN/PINP/PINN/net9 等）齐全"
            "（对象=输出内容，判定=不泄 A 且含 B）"
            "⑮非退化 + 3 跑 sha256 一致 + §4.9 三假（empty/print_fixed_A/multi_setq）全 FAIL 且命中≥3 个独立条件"
            "（对象=健壮性，判定=确定性+抗假提交）"
        ),
        "trace_source": {
            "user": "willashi",
            "host": "hfeg0plg15",
            "session_file": "1792380407268_opm9y.messages.json",
            "match_count": 279,
            "real_task_summary": (
                "用户[willashi]提需求：「目前窗口的schemetic报错，帮我修一下，指名报错原因」。"
                "agent 读 CDS.log 诊断 lvs pre_sim schematic Check&Save 报 7 errors+8 warnings(SCH-1172)："
                "I_pre_0.IN 浮空输入 / PIN0(ipin) 浮空 / net5 浮空输入 / I_pre_0.VSS 接 global gnd!(应改 VSS net)。"
                "SandBox pyAether/SKILL 多次不可用 → 降级 editor 写 SKILL 修复脚本 fix_pre_sim_v3.il："
                "procedure fixPreSimSchematic @key lib/cell/view + let 独立绑定 cv/insts/nets/terms/instPre/pin0/pin1... + "
                "(setq cv (dbOpenCellViewByType lib cell view \"a\")) + Fix1 dbSetInstTermNet 替换 gnd!→VSS net + "
                "Fix2 删 net5 dangling wires(foreach cv~>shapes dbDeleteObject) + Fix3 连 I_pre_0.IN↔PIN0 + "
                "Fix4 连 OUT↔PIN1 + 清 orphaned nets(foreach oldNetsToFix dbDeleteObject) + dbSave cv；CIW load 执行。"
                "后续 U5 要求补全 IN/OUT/VDD/GND 4 pin；U6/U7 反馈 SKILL bug：setq 不可多赋值、return 须在 prog 内。"
                "金标=v3 SKILL 修复脚本逻辑结构，降级为 config-driven 生成器（真实 Virtuoso GUI 非确定性+沙盒不可用→生成脚本+fix_plan）。"
            ),
        },
    },
}

JSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl"

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify
with open(JSONL) as f:
    lines = f.readlines()
print("D.jsonl now %d lines" % len(lines))
last = json.loads(lines[-1])
print("last task_id:", last["task_id"])
print("last domain:", last["metadata"]["domain"])
print("test_rationale head:", last["metadata"]["test_rationale"][:40])
print("test src len:", len(last["test"]))
# assertion gate
import re
m = re.match(r"(\d+)\s*条断言", last["metadata"]["test_rationale"])
k_rat = int(m.group(1))
# count CONDITIONS in test
k_chk = last["test"].count('("', 0, last["test"].find("]")) // 1
# better: count entries in CONDITIONS list
conds = re.findall(r'\("([a-z])",', last["test"])
print("k_rationale=%d  k_check=%d  match=%s  >=8=%s" %
      (k_rat, len(conds), k_rat == len(conds), len(conds) >= 8))
