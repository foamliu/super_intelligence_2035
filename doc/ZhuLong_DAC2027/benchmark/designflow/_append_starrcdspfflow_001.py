#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-StarRCDspfFlow-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os, sys, re

CASE = "EDA-Eval-DesignFlow-StarRCDspfFlow-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
BENCH = os.path.join(REPO, "benchmarks", "EDA-Eval-DesignFlow")
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
REF = os.path.join(BENCH, "reference", CASE)
ASSETS = os.path.join(BENCH, "assets", CASE)

check_src = open(os.path.join(REF, "check.py")).read()

# ---- count independent conditions in check.py (k_check) ----
cond_labels = sorted(set(re.findall(r'_cond\("([a-z])"', check_src)))
k_check = len(cond_labels)
assert k_check >= 8, "k_check < 8: %d" % k_check
print("k_check =", k_check, "labels =", "".join(cond_labels))

rationale = (
    "14 条断言："
    "① submit.zip 含 5 个交付文件齐全(starrc_dspf.cmd/spf_layers.py/run_starrc_dspf.sh/run_analysis.sh/filelist.f) "
    "② run_starrc_dspf.sh 与 run_analysis.sh 通过 bash -n 语法检查且可执行 "
    "③ spf_layers.py 在可见 A.spf 上 L2 真跑 exit 0(subprocess 真exec 候选脚本) "
    "④ A 报告含全部 6 个电阻 + 正确层名(M1/M2/M3/PO/NW) + PASS + TOTAL_RESISTORS=6 "
    "⑤ 注入变异 A.spf(RRA1 的 $lvl 由 1 改 3)后解析层应为 M3 而非 M1(击穿只打印期望串/硬编码的假提交，L2 真跑) "
    "⑥ 隐藏 B.spf 交叉输入(L2 真跑)报告 7 个电阻 + 正确层名(M4/M5/M6/CO/PO) + PASS + TOTAL_RESISTORS=7(击穿硬编码 A 层集) "
    "⑦ starrc_dspf.cmd 含完整 DSPF 关键字集(NETLIST_FORMAT:SPF/GDS_FILE/TCAD_GRD_FILE/MAPPING_FILE/NETLIST_FILE/NETLIST_MINRES_THRESHOLD/NETLIST_MINRES_HANDLING/COUPLING_)且 NETLIST_FORMAT:SPF 为活动行 "
    "⑧ cmd 用 @PLACEHOLDER@/$env 参数化且活动行无 /home/ 硬编码绝对路径 "
    "⑨ run_starrc_dspf.sh 含 module load + STARRC_MODULE 参数化且活动行无 /home/ 硬编码 "
    "⑩ run_analysis.sh 用 SPF_FILE/argv 参数化且活动行无 /home/ 硬编码 "
    "⑪ spf_layers.py 用 argv[1]/SPF_FILE 参数化且活动行无 /home/ 硬编码 "
    "⑫ filelist.f 列出 .spf + spf_layers.py + starrc_dspf.cmd 且无 /home/ 硬编码 "
    "⑬ run_starrc_dspf.sh --check-cmd 在 fake StarXtract fixture 下 L2 真跑，输出含 FAKE_STARRC_SHELL + STARRC_INVOKED + STARRC_MODULE=(击穿不调用 StarXtract 的 stub) "
    "⑭ spf_layers.py 在 A 上 3 次重跑 stdout 完全一致(确定性)"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": open(os.path.join(ASSETS, "prompt.txt")).read(),
    "attachments": [
        {"name": "prompt.txt", "source": "prompt.txt", "desc": "StarRC DSPF 抽取 flow + .spf 电阻层分析任务说明(寄生抽取后端场景)"},
        {"name": "task_brief.md", "source": "task_brief.md", "desc": "交付接口与文件位置(<=3 行)"},
        {"name": "dspf_A/dspf_A.spf", "source": "dspf_A/dspf_A.spf", "desc": "示例 DSPF(.spf)文件 A(含 *LAYER_MAP + R*$lvl 电阻，M1/M2/M3/PO/NW 多层)"},
        {"name": "feint/starrc_dspf_partial.cmd", "source": "feint/starrc_dspf_partial.cmd", "desc": "StarRC 命令文件残缺模板(全注释 + TODO + 硬编码 /home 路径，待修复)"},
        {"name": "feint/spf_layers_partial.py", "source": "feint/spf_layers_partial.py", "desc": "SPF 解析器残缺模板(硬编码路径，仅读 header，待补全 layer map + R 行解析)"},
        {"name": "hidden/hidden_manifest.json", "source": "hidden/hidden_manifest.json", "desc": "隐藏输入 B 清单(不进 SUT 沙箱)"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["scripts/starrc_dspf.cmd", "scripts/spf_layers.py", "run/run_starrc_dspf.sh", "run/run_analysis.sh", "filelist.f"],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "e0045488",
            "host": "hfeg0pkn002",
            "session_file": "1792386615426_npf2k.messages.json",
            "match_count": 103,
            "real_task_summary": "StarRC DSPF flow 探索 + .spf 电阻层分析: 用户先问 StarRC DSPF 抽取选项(man 页只有消息目录，助手从二进制/消息库 ground-truth 出真实 NETLIST_FORMAT:SPF 等关键字)，再问 .spf 中 $lvl 含义(= *LAYER_MAP 层索引)，最后要求逐电阻报告所在层(助手写 spf_layers.py 解析 *LAYER_MAP + R*$lvl 映射层名 + 按层汇总)"
        },
        "domain": "pnr_signoff",
        "verb": "starrc-dspf-flow-and-spf-resistor-layer-map",
        "level": "L2",
        "track": "B",
        "test_rationale": rationale,
        "hidden_input": {
            "b_path": "hidden/dspf_B/",
            "b_files": ["dspf_B.spf"],
            "diff_dims": ["layer_set(M4/M5/M6/CO/PO vs A 的 M1/M2/M3/PO/NW)", "net_names(netB_* vs netA_*)", "resistor_names(RBT* vs RRA*)", "resistor_count(7 vs 6)", "rc_values(全异)"]
        },
        "l2_real_run": "check.py L2 真跑 = subprocess 真exec 候选脚本(非文本相似): (c) spf_layers.py 在可见 A.spf 真跑 exit0; (e) 注入变异 A.spf(RRA1 $lvl 1->3) 真跑验层 M3 非 M1(击穿假打印/硬编码); (f) 隐藏 B.spf 交叉输入真跑验 7 电阻+正确层(击穿硬编码 A 层集); (m) run_starrc_dspf.sh --check-cmd 在 fake StarXtract fixture 下真exec 验输出含 FAKE_STARRC_SHELL+STARRC_INVOKED+STARRC_MODULE=(击穿不调用 StarXtract 的 stub); (n) A 上 3 次重跑 stdout 一致(确定性). 静态条件 (a)(b)(g)(h)(i)(j)(k)(l) 纯字符串/正则断言. .75 L2 自验(infra-honest): 候选 spf_layers.py 在 .75 Python 3.7.1 上真跑 dspf_A.spf -> TOTAL_RESISTORS=6 + 全部层名正确 + PASS(可移植性确认，比 3.9 更老); .75 真实 StarXtract 可调用(module load ds/star/2020.09-SP5-4 -> StarXtract -V -> R-2020.09-SP5-4-VAL-20220823). 真跑完整 StarXtract 抽取需完整 PDK DEF/LEF/TF/CCI_cmd/mapping(40min 预算内造不出可跑 B) -> 不假装能跑，--check-cmd 仅验调用链可达.",
        "harness": "cline",
        "notes": "B 档 synthesized. 真实 trace npf2k (e0045488@hfeg0pkn002, mc=103) 用户原话 'I want to work on dspf flow' + 'please tell me what layer each Resistor is on in this file' -> 助手 ground-truth StarRC 选项(无 NETLIST_FORMAT:DSPF, DSPF 输出 = NETLIST_FORMAT:SPF) + 写 spf_layers.py(*LAYER_MAP 解析 + R*$lvl 层映射 + 按层汇总). 真实 /proj/drexp/.../invBx2.spf 对 e0031982 不可读(权限 denied) + SPF 内容不在 trace read_files 结果中 -> B 档合成 dspf_A.spf/dspf_B.spf(同 DSPF 1.2 格式，5维全异). 本 case 重构为 design_flow: 给定 dspf_A + feint 残缺模板，SUT 交付参数化 StarRC DSPF flow(5 文件: cmd + spf_layers.py 解析器 + run 脚本 + filelist). 关键字集从 starrc_shell+DEF+LAYER_MAP_FILE 迁移到 StarXtract+GDS_FILE+MAPPING_FILE(更贴合 StarRC 经典命令文件引擎 R-2020.09-SP5-4，.75 已验证)."
    }
}

# ---- byte-sync guard: test field must equal disk check.py ----
assert entry["test"] == check_src, "test field != disk check.py"
# ---- assertion gate: k_rationale == k_check >= 8 ----
assert entry["metadata"]["test_rationale"].startswith("14 条断言："), "rationale prefix"
marks = re.findall(r"[①-⑮]", entry["metadata"]["test_rationale"])
k_rationale = len(set(marks))
assert k_rationale == k_check, "k_rationale(%d) != k_check(%d)" % (k_rationale, k_check)
assert k_check >= 8, "k_check < 8"
print("GATE: k_rationale=%d == k_check=%d >= 8  PASS" % (k_rationale, k_check))
print("test bytes:", len(entry["test"]))

# ---- idempotency: do not append if CASE already in jsonl ----
existing = open(JSONL).read()
if CASE in existing:
    print("SKIP: %s already in %s" % (CASE, JSONL))
    sys.exit(0)

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", JSONL)

# ---- disk roundtrip: re-read last line, test field == disk check.py ----
last = open(JSONL).read().strip().splitlines()[-1]
d = json.loads(last)
assert d["task_id"] == CASE, "last line task_id mismatch: %s" % d.get("task_id")
assert d["test"] == check_src, "disk roundtrip: test field != disk check.py"
assert d["metadata"]["test_rationale"].startswith("14 条断言：")
print("DISK ROUNDTRIP: PASS (test == disk check.py, %d bytes)" % len(d["test"]))
print("A.jsonl lines:", len(open(JSONL).read().splitlines()))
