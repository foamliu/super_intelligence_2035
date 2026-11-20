#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SpecNotifClassify-001 to the shard A jsonl."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "SpecNotifClassify-001"
DOMAIN = "verification"
LEVEL = "L1-static"
TRACK = "B"   # B-synthesized (reconstructed Verilog snippet faithful to trace structure)
K = 14

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = "assets/" + CASE
REF = "reference/" + CASE

prompt = open(os.path.join(BENCH, ASSETS, "prompt.txt")).read()
check_py = open(os.path.join(BENCH, REF, "check.py")).read()

entry = {
    "id": "EDA-Eval-DesignFlow-" + CASE,
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "test": check_py,
    "attachments": [
        {"name": "prompt.txt",      "source": ASSETS + "/prompt.txt"},
        {"name": "task_brief.md",   "source": ASSETS + "/task_brief.md"},
        {"name": "sp_sram_A.v",     "source": ASSETS + "/sp_sram_A.v"},
        {"name": "hidden/hidden_manifest.json", "source": ASSETS + "/hidden/hidden_manifest.json"},
    ],
    "metadata": {
        "domain": DOMAIN,
        "level": LEVEL,
        "track": TRACK,
        "k_check": K,
        "k_rationale": K,
        "test_rationale": (
            "14 条断言：①(a) submit.zip 恰含 notif_classify.py 与 notif_report.json 两件齐全 "
            "②(b) notif_classify.py 可 py_compile 通过无语法错误 "
            "③(c) [A] tviol_A 记录 is_vector=true 且 used_in_specify=true 且 used_per_bit_behavioral=true 且 fix_strategy=split_spec_notif 且 vcs_pass2_safe=false "
            "④(d) [A] tviol_CEB is_vector=false 且 fix_strategy=no_fix_needed 且 vcs_pass2_safe=true "
            "⑤(e) [A] tviol_WT is_vector=true 且 used_in_specify=true 且 used_per_bit_behavioral=false 且 fix_strategy=scalarize_decl 且 vcs_pass2_safe=false "
            "⑥(f) [A] tviol_CRSLA is_vector=true 但 used_in_specify=false → fix_strategy=no_fix_needed 且 vcs_pass2_safe=true（向量但未进 specify 不会触发 Pass2 崩溃）"
            "⑦(g) [A] summary.total==17 且 split_spec_notif==3 且 scalarize_decl==5 且 no_fix_needed==9 "
            "⑧(h) [A] summary.vcs_pass2_unsafe==8 "
            "⑨(i) [A] 全部 17 个 tviol_* notifier 被枚举且不含任何 prev_tviol_* "
            "⑩(j) [B 隐藏交叉输入] tviol_ADDR=split_spec_notif 且 tviol_DQS=scalarize_decl 且 tviol_CS=no_fix_needed "
            "⑪(k) [B] summary.total==9 且 split==3 且 scalarize==2 且 no_fix==4 "
            "⑫(l) [B] 反硬编：B 报告枚举的是 B 自身的 9 个 notifier 名（ADDR/BWE/COLSEL/CS/DATA/DM/DQS/OE/WPS），不是 A 的名字 "
            "⑬(m) 候选自报 notif_report.json 为合法 JSON 且含 notifiers[] 与 summary{} 顶层键 "
            "⑭(n) [B] summary.vcs_pass2_unsafe==5"
        ),
        "trace_source": {
            "session_id": "1789367633495_9uwcw",
            "host": "hfeg0pkn001",
            "user": "lorikx",
            "mc": "mc250",
            "keywords": "rtl:371;synopsys:207;verilog:117;aether:54;skipper:15;calibre:14;vhdl:10;hspice:9",
            "user_turn_verbatim": "我是用Makefile里的make cfg_128x80_cm1_cd的命令运行，然后出现了错误，请帮我检查是什么原因，后续都用中文回答我",
            "turn_index": 0,
            "turn_kind": "提出需求",
            "real_task_summary": (
                "SRAM 模型 sp_sram.v 用 make cfg_128x80_cm1_cd 编译时 VCS Pass2 崩溃 "
                "（Timing check notifier must be scalar register）。真实 trace 中 assistant 诊断出 "
                "specify 块的 $setuphold/$width/$period notifier 实参为向量 reg，其中 tviol_A/D/BWEB 既进 "
                "specify 又被行为级逐位用（需拆 spec_notif 标量），tviol_WT/RT/WAT/WAV/RA 仅进 specify "
                "（改标量声明即可），tviol_CEB/WEB/CRSLA/CRSRA 等本就安全。本 case 把诊断核心抽成 "
                "notifier 分类工具，候选须对可见 A 与结构对立的隐藏 B 都正确分类。"
            ),
        },
    },
}

jsonl_path = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify roundtrip: last line test field == disk check.py bytes
lines = open(jsonl_path).read().splitlines()
last = json.loads(lines[-1])
assert last["id"] == "EDA-Eval-DesignFlow-" + CASE, last["id"]
assert last["test"] == check_py, "test field bytes != disk check.py"
assert last["metadata"]["k_check"] == last["metadata"]["k_rationale"] == K
print("appended", CASE, "→", os.path.basename(jsonl_path), "now", len(lines), "entries")
print("k_check=k_rationale=%d (>=8 GATE PASS)" % K)
print("test field bytes:", len(last["test"]), "== disk check.py bytes:", len(check_py))
