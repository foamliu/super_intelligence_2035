#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-DrcWaiveDeckGen-001 to shard C jsonl."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-DrcWaiveDeckGen-001"
ASSET_DIR = os.path.join(REPO, "assets", CID)
REF_DIR = os.path.join(REPO, "reference", CID)

with open(os.path.join(ASSET_DIR, "prompt.txt"), "r", encoding="utf-8") as f:
    prompt = f.read()
with open(os.path.join(REF_DIR, "check.py"), "r", encoding="utf-8") as f:
    check_src = f.read()

attachments = [
    "assets/%s/prompt.txt" % CID,
    "assets/%s/task_brief.md" % CID,
    "assets/%s/config_A.json" % CID,
    "assets/%s/waive_check_reference_A.drc" % CID,
]

test_rationale = (
    "14 条断言："
    "①(a) submit.zip 含 drc_waive_deck_gen.py(>=400B,UTF-8 无 NUL)且 py_compile 通过 "
    "②(b) 在隐藏 B 上 subprocess exit0 无 Traceback 且写出 TSV_S_03_waive_check.drc + "
    "waive_deck_manifest.json(合法 JSON,含 deck_path/rule_id/target_cell/layout/layer_maps/"
    "checks/parameterized/fixed/audit 顶层键) "
    "③(c) manifest.layout == {path:B_rule_dir/TSV_S_03_expand.oas, primary:TSV_S_03, "
    "system:OASIS, resolution:1, precision:null} "
    "④(d) deck 文本含 REFERENCE 层映射用 B 的 opc1 层+datatype(LAYER MAP 5101 DATATYPE 61 8002 + "
    "LAYER REFERENCE 8002) "
    "⑤(e) deck 文本含 DRCW_mark1 层映射用 B 的 opc2 datatype(LAYER MAP 5101 DATATYPE 62 8003 + "
    "LAYER DRCW_mark1 8003) "
    "⑥(f) deck 文本含 ERROR_OUTPUT 层映射固定为 100/0 -> 8001(未被 opc1/opc2 参数化) "
    "⑦(g) manifest.layer_maps 恰 3 条,roles=={error_output,reference,drcw_mark1},"
    "dest_layers=={8001,8002,8003},parameterized: error_output=False/reference=True/drcw_mark1=True "
    "⑧(h) manifest.audit.reference_and_drcw_share_opc1_layer==True 且 reference.source_layer=="
    "drcw.source_layer==5101 "
    "⑨(i) manifest.audit.error_layer_fixed==True 且 manifest.fixed=={error_layer:100,error_datatype:0} "
    "⑩(j) deck 文本含 CHECK1 块且 DRCW_mark1_vaild1 INTERACT ERROR_OUTPUT==1 / "
    "DRCW_mark1_vaild2 INTERACT REFERENCE==1 / DRCW_mark1 NOT DRCW_mark1_vaild 三行齐全 "
    "⑪(k) deck 文本含 CHECK2 块且 (REFERENCE OUTSIDE ERROR_OUTPUT) NOT ((REFERENCE OUTSIDE "
    "ERROR_OUTPUT) INTERACT DRCW_mark1 == 1) "
    "⑫(l) deck 文本含 waiveMarkExists 块且 CHIP NOT INTERACT DRCW_mark1 "
    "⑬(m) precision-omit 分支:B precision=null -> deck 无 ^PRECISION 行 且 "
    "manifest.audit.precision_emitted_only_if_set==True "
    "⑭(n) 跨输入守卫:在可见 A(precision=1000,opc1_layer=4001,opc1_dt=51,opc2_dt=52)上重跑 exit0 + "
    "A deck 用 4001/51->8002 与 4001/52->8003 + A deck 含 PRECISION 1000 + A deck 文本 != B deck "
    "文本(证配置驱动,杀硬编码 B / 静态 deck / 忽略 precision 的候选)"
)

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": attachments,
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["outputs/submit.zip"],
    "test": check_src,
    "budget": {"max_turns": 20},
    "metadata": {
        "domain": "physical_verify",
        "task_name": "DrcWaiveDeckGen",
        "scenario": "Calibre DRC waiver check SVRF deck generator (parameterized opc1/opc2 layer numbers)",
        "direction": "physical_layout",
        "layer": "L1-boundary",
        "topic": "drc_waive_deck_parameterized_svrf_gen",
        "difficulty": "L1-boundary",
        "design": "B-synthesized",
        "tcr_refs": [],
        "heavy": False,
        "wall_time_sec": 600,
        "trace_source": {
            "user": "xinqiaoz",
            "host": "hfeg0pkn004",
            "session_file": "1789892820566_17cgk.messages.json",
            "session_msgs": 207,
            "match_count": 321,
            "real_task_summary": (
                "xinqiaoz/hfeg0pkn004, mc=321, keywords pdk:714/calibre:414/.gds:113/virtuoso:9 "
                "(PDK_QA DrcPatternCheck 维护 session). 207 msgs/1.09MB, agent cline(lead) glm-5.2. "
                "USER#1(逐字真实意图轮) 'writeWaiveDrcFile 中只需要参数化 opc1,opc2 的层号，其他的任然不变' "
                "— 用户要求把 writeWaiveDrcFile 里的 OPC1/OPC2 层号参数化(error 层 100/0、dest 层 8001/8002/8003、"
                "CHECK1/CHECK2/waiveMarkExists 语义不变)。read_files 取得真实 writeWaiveDrcFile 源码"
                "(LAYER MAP 100/0->8001 ERROR_OUTPUT; 4001/51->8002 REFERENCE; 4001/52->8003 DRCW_mark1; "
                "CHECK1 DRCW_mark1 INTERACT ERROR_OUTPUT/REFERENCE; CHECK2 REFERENCE OUTSIDE ERROR_OUTPUT; "
                "waiveMarkExists CHIP NOT INTERACT DRCW_mark1)。session 是多轮迭代(legacy fallback/prefix "
                "fallback/patternNotFound 显示/report doc 更新),本 case 只取 USER#1 的 waiver-deck 参数化子任务。"
                "A-档不可行(gold=对 writeWaiveDrcFile 的代码 diff,依赖 pdkQaSystem 1116 行生产代码+calibre 运行环境,"
                "且 working dir 已被清理) -> B-档 synthesized L1-boundary,seed=USER#1 逐字意图(参数化 opc1/opc2 层号 "
                "-> 独立 stdlib CLI 生成参数化 SVRF waive deck + 语义自审 manifest)。fresh-user xinqiaoz, "
                "physical_verify domain anchor(PDK QA Calibre DRC waiver)。已有 xinqiaoz 同主题 case: DrcPatCheckAudit-001"
                "(bad/good cell 配对审计)、DrcLegacyFallback-001(legacy cell 兜底匹配)、DrcPatternHandover-001(交接文档),"
                "本 case 角度=waiver SVRF deck 生成+层号参数化语义,与前三者不重叠。"
            ),
        },
        "test_rationale": test_rationale,
    },
}

out_path = os.path.join(REPO, "EDA-Eval-DesignFlow_C.jsonl")
# guard: do not double-append
existing_ids = set()
with open(out_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            existing_ids.add(json.loads(line)["task_id"])
        except Exception:
            pass
if CID in existing_ids:
    print("ALREADY PRESENT, skipping append:", CID)
else:
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("APPENDED:", CID)
    print("test field bytes:", len(check_src))

# gate check: k_rationale == k_check == 14
import re
k_rat = test_rationale.count("①") + test_rationale.count("②") + test_rationale.count("③") + \
        test_rationale.count("④") + test_rationale.count("⑤") + test_rationale.count("⑥") + \
        test_rationale.count("⑦") + test_rationale.count("⑧") + test_rationale.count("⑨") + \
        test_rationale.count("⑩") + test_rationale.count("⑪") + test_rationale.count("⑫") + \
        test_rationale.count("⑬") + test_rationale.count("⑭")
# count check.py labeled conditions (a)-(n) via _cond("x", ...)
cond_labels = set(re.findall(r'_cond\("([a-z])"', check_src))
k_check = len(cond_labels)
print("k_rationale =", k_rat, "| k_check =", k_check, "| labels =", sorted(cond_labels))
assert test_rationale.startswith("14 条断言："), "rationale prefix wrong"
assert k_rat == 14 and k_check == 14, "GATE FAIL: k mismatch"
print("GATE PASS: k_rationale=k_check=14 >= 8")
