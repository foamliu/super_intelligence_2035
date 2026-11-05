#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SchFixFloating-001 to D.jsonl."""
import json, os

CASE = "EDA-Eval-DesignFlow-SchFixFloating-001"
BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = os.path.join(BASE, "reference", CASE)
AST = os.path.join(BASE, "assets", CASE)

with open(os.path.join(REF, "check.py"), "r") as f:
    check_src = f.read()

with open(os.path.join(AST, "prompt.txt"), "r") as f:
    prompt = f.read().strip()

attachments = [
    f"assets/{CASE}/prompt.txt",
    f"assets/{CASE}/task_brief.md",
    f"assets/{CASE}/config_A.json",
    f"assets/{CASE}/CDS.log",
]

test_rationale = (
    "14 条断言：①submit.zip 含 gen_fix_sch.py 且无 check/reference/hidden_manifest/"
    "config_B/gen_fix_sch_ref/negative_selftest 等泄题文件与禁用 import "
    "②gen_fix_sch.py py_compile 通过(语法合法) "
    "③在隐藏 config_B 上运行 `python3 gen_fix_sch.py _config.json` exit0 且写出 "
    "fix_schematic.il + fix_plan.json "
    "④fix_schematic.il 用 dbOpenCellViewByType 且 mode 为 \"a\"(编辑打开 cellview) "
    "⑤fix_schematic.il 含 let 且每个 setq 为单赋值(刚好 3 个顶层 token：setq+符号+值)，"
    "禁用 trace 中的多赋值 setq bug `(setq a x b y)` "
    "⑥Fix1 全局 net 误接修复：含 dbSetInstTermNet 且 B 的 wrong_net(\"0\") 与 correct_net"
    "(\"VSS\") 引号串均在 il 中 "
    "⑦Fix2 删浮空 net 上的 dangling wires：含 dbDeleteObject 且 B 的每个浮空 net 名"
    "(net12/net99)引号串均在 il 中 "
    "⑧Fix3 连浮空 instTerm↔pin：含 dbSetInstTermNet 且 B 的 instance 名(I_amp_2)与 "
    "ipin/opin 名(INP/OUTP)引号串均在 il 中 "
    "⑨fix_schematic.il 含 dbSave "
    "⑩Fix4 清 orphaned 空 net：il 含 cv~>nets 且 dbDeleteObject 且 null 空检查 "
    "⑪fix_plan.json 可解析且 errors_count==6、floating_nets==[net12,net99]、"
    "lib/cell 匹配 B "
    "⑫B-must+反泄题：B 的 lib/cell/inst 引号串在 il 中且 A 的 lib(lvs)/cell(pre_sim)/"
    "inst(I_pre_0)/wrong_net(gnd!) 引号串均不在 il 中 "
    "⑬确定性：B 上 3 次运行 fix_schematic.il 的 sha256 一致；跨输入：A 上运行的 il "
    "sha256 与 B 不同(数据驱动而非硬编) "
    "⑭gen_fix_sch.py 源无 /home/、/rundata、/proj/ 硬编主机路径且用 sys.argv 读 config"
    "(非硬编配置路径)。§4.9 三假(empty/print_only/hardcoded_stub)经 negative_selftest "
    "均 FAIL 且首失败标签互异{c,d,f}=3 独立；named 负样本 multi_setq→e、no_global_fix→f、"
    "no_orphan→j 各命中目标条件。"
)

metadata = {
    "domain": "schematic_netlist",
    "track": "faithful",
    "layer": "L1",
    "k_check": 14,
    "k_rationale": 14,
    "trace_source": {
        "user": "willashi",
        "host": "hfeg0plg15",
        "session_file": "1792380407268_opm9y.messages.json",
        "match_count": 279,
        "real_task_summary": (
            "用户窗口中 lvs/pre_sim schematic testbench 做 lvs pre_sim Check&Save 报 "
            "7 errors+8 warnings(SCH-1172)：I_pre_0.IN 浮空输入、PIN0(ipin)浮空、net5 "
            "浮空、I_pre_0.VSS 接 global gnd!(应改 VSS net)、I_pre_0.OUT short warning。"
            "用户 U0=「目前窗口的schemetic报错，帮我修一下，指名报错原因」(clean 提需求，"
            "未指出根因→A 档可用)。trace 中 agent 读 CDS.log 诊断错误清单，沙盒 pyAether/"
            "SKILL 不可用→降级写 SKILL 修复脚本 fix_pre_sim_v3.il：dbOpenCellViewByType "
            "mode \"a\" 打开 + let 局部绑定 + Fix1 替换 VSS 上 global gnd!→VSS net"
            "(dbSetInstTermNet) + Fix2 删 net5 dangling wires(dbDeleteObject) + Fix3 连 "
            "I_pre_0.IN↔PIN0、OUT↔PIN1 + 清 orphaned nets + dbSave；并踩 bug：setq 不可多"
            "赋值、return 须在 prog 内。B-grade synthesized：真实 Virtuoso GUI 执行非确定"
            "性+沙盒不可用，降级为 config-driven 生成器 gen_fix_sch.py(读 config JSON→"
            "出 fix_schematic.il+fix_plan.json)，check 用隐藏 config_B(不同 lib/cell/inst/"
            "pin 名、不同 global net 名\"0\"、两个浮空 net)验证数据驱动与结构。"
        ),
    },
    "test_rationale": test_rationale,
}

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": attachments,
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "metadata": metadata,
}

# idempotency: remove any prior entry with same task_id
jsonl = os.path.join(BASE, "EDA-Eval-DesignFlow_D.jsonl")
lines = []
if os.path.exists(jsonl):
    with open(jsonl, "r") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                o = json.loads(ln)
            except Exception:
                lines.append(ln)
                continue
            if o.get("task_id") == CASE:
                continue  # drop prior
            lines.append(ln)
lines.append(json.dumps(entry, ensure_ascii=False))
with open(jsonl, "w") as f:
    for ln in lines:
        f.write(ln + "\n")
print("appended", CASE, "-> total lines:", len(lines))

# verify gate: count circled numbers in rationale
import re
n = len(re.findall(r'[①-⑯]', test_rationale))
print("circled-count =", n, "k_check =", metadata["k_check"],
      "startswith_ok =", test_rationale.startswith("14 条断言："))
