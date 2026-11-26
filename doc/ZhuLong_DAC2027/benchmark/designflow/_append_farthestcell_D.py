#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_append_farthestcell_D.py - append EDA-Eval-DesignFlow-FarthestCellPick-001
to EDA-Eval-DesignFlow_D.jsonl."""
import os, json, hashlib

CASE = "EDA-Eval-DesignFlow-FarthestCellPick-001"
REF_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/" + CASE
ASSET_DIR = "assets/" + CASE
JSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl"

# full check.py source as test string
with open(os.path.join(REF_DIR, "check.py"), "r", errors="replace") as f:
    test_src = f.read()
test_sha = hashlib.sha256(test_src.encode()).hexdigest()

# prompt
with open("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/" + ASSET_DIR + "/prompt.txt") as f:
    prompt = f.read()

test_rationale = (
    "14 条断言："
    "①zip 含 gen_farthest_cell_report.py 且无禁用 import(socket/urllib/requests/subprocess 等)/引用(_ref/check/reference)/路径(/proj//rundata//home/) "
    "②源码 py_compile(compile)通过 "
    "③隐藏 netlist_B 上候选 exit0 且报告非空 "
    "④B 报告含正确最远 cell 实例名 Xnear_M "
    "⑤B 报告含正确 cumulative BL R=46(±0.5) "
    "⑥B 报告含正确 subckt 类型 kcellx1mdl_M "
    "⑦B 报告含正确 measurement node CC_near_M "
    "⑧B 报告含正确 WL trigger net WL_near_M "
    "⑨B 报告含正确 column=near "
    "⑩B 报告未把 RC-load decoy(Xload0/Xload1)命名为最远 cell "
    "⑪反硬编码 A：A 上重跑含最远实例 Xfar_B 且≠B、源码无 A 专属字面量(Xfar_B/CC_far_B/WL_far_B) "
    "⑫跨输入 B2：B2 上重跑含最远实例 Xfar_T 且≠A≠B、源码无 B2 专属字面量、B2 结论正确 "
    "⑬CLI 用 sys.argv/argparse 且未硬编码输入文件名 "
    "⑭确定性：B 上 3 次重跑报告 sha256 一致"
)

case = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        ASSET_DIR + "/prompt.txt",
        ASSET_DIR + "/task_brief.md",
        ASSET_DIR + "/netlist.sp",
    ],
    "entry_point": "outputs/submit.zip",
    "test": test_src,
    "metadata": {
        "domain": "schematic_netlist",
        "trace_source": {
            "user": "t0002616",
            "host": "10.129.2.13",
            "session_file": "1793062149793_u8ovn.messages.json",
            "match_count": 126,
            "real_task_summary": (
                "t0002616 在 10.129.2.13 上用 cline 要求分析 SRAM 目标列测试台网表(Mat_Testbench_revised, "
                "12504 行)计算 tCS(WL on→VSN 90%, D0)与 WR_Time(BLa/b cross→VSN 95%)应选哪个 cell。trace agent "
                "grep+解析网表层次(Mat→submat→CBL→kcellx32mdl_{T,M,B}_Tar→kcellx1mdl)，结论：真实 VSN=位单元存储"
                "节点 CC(非节点名 VSN)；只有 kcellx32mdl_*_Tar 里的 kcellx1mdl_* 才有真实 CC。U#1 用户要求'选最远 cell'。"
                "agent 按位线/字线 R·C 累积电阻定最远：SA 从顶段 LBL1 进→(CTCon)→LBL0 半→T→M→B，最远=B 底段 LBL0 半"
                "远列(LWL0_R)单元 xi_kcellx32mdl_b_4.cc02 / WL lwl0_r_bottar<2>。U#2 给激励 All0.sp，agent 核对发现"
                "激励选错层(测 M 中段 _m_4，应改 B 底段 _b_4)并给出修正 .meas。"
            ),
        },
        "test_rationale": test_rationale,
        "track": "faithful",
        "grade": "B-synthesized",
        "layer": "L1",
    },
}

# k-check gate
k_rat = test_rationale.count("①") + sum(1 for ch in test_rationale if ch in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭")
# count assertions ①-⑭
import re
assertions = re.findall(r"[①-⑭]", test_rationale)
k_rat = len(assertions)
print("k_rationale =", k_rat, "(expect 14)")
assert k_rat == 14, "k_rationale != 14"

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended", CASE, "to D.jsonl")
print("test sha256 =", test_sha)
# verify line count
with open(JSONL) as f:
    n = sum(1 for _ in f)
print("D.jsonl lines =", n)
