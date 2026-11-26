#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SchNetPrefixHilightGen-001 to EDA-Eval-DesignFlow_C.jsonl.
test field is the exact bytes of the on-disk check.py (byte-equal guarantee)."""
import json
import os

CASE = "EDA-Eval-DesignFlow-SchNetPrefixHilightGen-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = os.path.join(BENCH, "reference", CASE)
ASSETS = os.path.join(BENCH, "assets", CASE)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")

with open(os.path.join(REF, "check.py"), "r", encoding="utf-8") as f:
    test_src = f.read()
with open(os.path.join(ASSETS, "prompt.txt"), "r", encoding="utf-8") as f:
    prompt = f.read()

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/%s/net_inventory_A.json" % CASE,
        "assets/%s/hilight_config_A.json" % CASE,
    ],
    "test": test_src,
    "metadata": {
        "domain": "layout_virtuoso",
        "level": "L2",
        "track": "B-synthesized",
        "trace_source": {
            "user": "steveny",
            "host": "hfeg0pnd001",
            "ip": "10.129.32.189",
            "session_file": "1791783189298_t2hnp",
            "match_count": 336,
            "real_task_summary": "用 Virtuoso SKILL 高亮当前 schematic cellview 中所有以 'net' 打头的 net（不区分大小写，黄色 y3）；走 probe 路线（geGetEditCellView + cv~>nets + rexMatchp 前缀 + geDeleteAllProbe + geMakeProbeWithColor），schHiHiliteLabel 不能按名过滤。真实结果在 auto_steveny_case1/BCenterL/schematic 高亮 80 个 net。",
        },
        "test_rationale": (
            "15 条断言：①(a) submit.zip 合法且仅含 gen_sch_net_hilight.py 一个文件(无 reference/check/jsonl/hidden 泄漏) "
            "②(b) 候选脚本 py_compile 通过(语法合法) "
            "③(c) 仅 Python 标准库(禁 virtuoso/aether/calibre/pyaether/numpy/pandas/sklearn/scipy/matplotlib/lxml/bs4/requests) "
            "④(d) 隐藏输入 B 运行 exit 0 "
            "⑤(e) hilight.il 输出非空 "
            "⑥(f) hilight.il 含 geGetEditCellView() 取 cv + unless(cv ...) 守卫 "
            "⑦(g) hilight.il 含 geDeleteAllProbe 清旧 probe "
            "⑧(h) hilight.il 含 geMakeProbeWithColor 且用配置的 color "
            "⑨(i) hilight.il 含名模式匹配(rexMatchp 或 setof + 名过滤) "
            "⑩(j) matched_nets.json 的 match_count == B 实际匹配数(9) "
            "⑪(k) matched_nets.json 的 matched 集合 == B 实际匹配名集合(精确,无假阳假阴) "
            "⑫(l) matched_nets.json 不含非匹配 net(spin/begin_err/main/offin/anet/VDD 等被排除) "
            "⑬(m) matched_nets.json 的 color == B 配置色(g2) "
            "⑭(n) matched_nets.json 的 cellview == B 的 cellview(非 A 硬编码) "
            "⑮(o) hilight.il 引用 B 的 pattern(in),非硬编码 A 的 net"
        ),
    },
}

# append (dedup guard: skip if id already present)
existing = set()
if os.path.exists(JSONL):
    with open(JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                existing.add(e.get("id") or e.get("case_id") or e.get("name"))
            except Exception:
                pass
if CASE in existing:
    print("SKIP: %s already in jsonl" % CASE)
else:
    with open(JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("APPENDED: %s" % CASE)
print("jsonl_C lines now:", sum(1 for _ in open(JSONL)))
