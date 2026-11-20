#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-HierarchyTrace-001 to shard B jsonl."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CASE_ID = "EDA-Eval-DesignFlow-HierarchyTrace-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, 'assets', CASE_ID)
REF = os.path.join(BENCH, 'reference', CASE_ID)
JSONL = os.path.join(BENCH, 'EDA-Eval-DesignFlow_B.jsonl')

with open(os.path.join(ASSETS, 'prompt.txt'), 'r', encoding='utf-8') as f:
    prompt = f.read().strip()
with open(os.path.join(REF, 'check.py'), 'r', encoding='utf-8') as f:
    test_src = f.read()

test_rationale = (
    "14 条断言：①submit.zip 含恰好 1 个 .py 脚本 ②脚本 py_compile 通过 ③B 合法路径 exit 0 "
    "④B 合法路径 stdout 含 CHAIN: 行 ⑤B CHAIN==期望链(WOWTOPB->LP5TOPB->Array16GTopB->Array8GWB->"
    "Array1GTopX->M1GTopB->M256MEGU->MSAQ12B 8名) ⑥B 断路径(末层伪实例)exit 1 ⑦B 断路径 stdout 含 BREAK "
    "标志 ⑧A 合法路径 exit 0(交叉输入守卫) ⑨A CHAIN==期望链(WOWTOP->LP5TOP->Array16GTop->Array8G_E->"
    "Array1G_Top_W->M1G_Top->M512MEG_U->MSAQ_28) ⑩A CHAIN≠B CHAIN(泛化非硬编码) ⑪B 伪顶层路径 exit 1"
    "(顶层定位正确) ⑫B CHAIN 恰好 8 名(top+7层结构完整) ⑬3 次运行 sha256 一致(幂等) ⑭B CHAIN[0]==WOWTOPB"
    "(标准单元 inv/nor2/nand3/buf 被跳过，非顶层)"
)

entry = {
    "id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        {"name": "prompt.txt", "source": "prompt.txt",
         "desc": "真实用户原话（A-faithful，xinweif @ hfeg0pkn005，trace 1792204349915_1g0xs U#70 逐字）：写 python 脚本检查 hierarchy xi_c_top.xi_array16gtop...xi_msaq_28 在网表中是否存在"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "交付接口：check_hierarchy.py <网表> <点分隔路径>，exit 0/1 + CHAIN:/RESULT: 行；判分只跑隐藏 B"},
        {"name": "netlist", "source": "netlist",
         "desc": "可见真实 A 网表（合成 SPICE fullchip，含 7 层 hierarchy WOWTOP→LP5TOP→Array16GTop→Array8G_E→Array1G_Top_W→M1G_Top→M512MEG_U→MSAQ_28，含 +续行实例与 inv/nor2 标准单元噪声）"},
    ],
    "test": test_src,
    "metadata": {
        "trace_source": {
            "user": "xinweif",
            "host": "hfeg0pkn005",
            "session_file": "1792204349915_1g0xs.messages.archive.json",
            "match_count": 28,
            "real_task_summary": "xinweif 在 hfeg0pkn005 上用 FineSim 仿真 LP5X DDR fullchip 网表(112MB WOWTOP)，分析两路仿真(激励同、网表异)导致 rdqst fail vs pass 的差异。用户 U#70「帮我写一个python脚本，检查这个hierarchy：xi_c_top.xi_array16gtop.xi_array8g_e.xi_array1gbk3.xi_m1g_top.xi_m512meg_u.xi_msaq_28 在这个网表是否存在」。agent 迭代 ~15 版 check_hierarchy.py Hierarchy Tracer：扫描 .SUBCKT 定义、按.分割层级路径、逐层在父 SUBCKT 中匹配 X-实例名→提取子 subckt 名(实例行末 token)、处理 +续行、跳过标准单元(inv/nor2/nand2/buf)。终版确认 7 层 SUBCKT 全部存在(xi_c_top→LP5TOP→Array16GTop→Array8G_E→Array1G_Top_W→M1G_Top→M512MEG_U→MSAQ_28)。本 case 抽取「SPICE 网表 hierarchy 路径追踪」可复用子流，关键 trap 为续行处理与标准单元顶层跳过。关键字 finesim/spice/hierarchy 高密。"
        },
        "domain": "spice_sim",
        "layer": "L1",
        "layer_rationale": "check() 在隐藏 B 网表(与 A 同 SPICE hierarchy 结构但 subckt 名/叶子/续行位置不同)上跑候选脚本，离线解析 SPICE 网表追踪 hierarchy 路径，subprocess 调候选 CLI，无需 EDA 工具。L1 离线 Python 复刻。",
        "track": "faithful",
        "test_rationale": test_rationale,
    },
}

# verify roundtrip: test field == disk check.py
assert test_src == open(os.path.join(REF, 'check.py'), 'r', encoding='utf-8').read(), "test field != disk check.py"

# count existing lines + unique ids
with open(JSONL, 'r', encoding='utf-8') as f:
    lines = f.readlines()
ids = set()
for ln in lines:
    try:
        ids.add(json.loads(ln)['id'])
    except Exception:
        pass
assert CASE_ID not in ids, "case id already in jsonl"
print("before: %d lines, %d unique ids" % (len(lines), len(ids)))

with open(JSONL, 'a', encoding='utf-8') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

with open(JSONL, 'r', encoding='utf-8') as f:
    after = f.readlines()
print("after: %d lines" % len(after))
# re-verify last entry parses + assertion gate
last = json.loads(after[-1])
import re as _re
k_rat = len(_re.findall(r'[①-⑯⑰⑱⑲⑳]', last['metadata']['test_rationale']))
# count labeled conditions in test (a-n)
k_chk = len(_re.findall(r'raise AssertionError\("([a-n]):', last['test']))
print("k_rationale=%d  k_check=%d  GATE=%s" % (k_rat, k_chk, "PASS" if k_rat == k_chk and k_chk >= 8 else "FAIL"))
print("appended:", last['id'])
