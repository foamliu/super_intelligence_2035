#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SramTailorPlanClassify-001 to shard B jsonl."""
import json, os

CASE = "EDA-Eval-DesignFlow-SramTailorPlanClassify-001"
EDA_BENCH_ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CHECK_PY = os.path.join(EDA_BENCH_ROOT, "reference", CASE, "check.py")

with open(CHECK_PY) as f:
    test_src = f.read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "budget": {"max_turns": 20},
    "expected_artifacts": ["sram_tailor_plan_classify.py", "summary_a.json"],
    "prompt": (
        "你是 CXMT 的 SPICE 仿真工程师，正在为一块 1M-word × 72-bit SRAM "
        "（顶层名 CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS，8T bitcell 阵列）做 "
        "FineSim 仿真前的 DSPF 裁剪（tailor）。裁剪工具 dspf-tool 的 "
        "tailor/plan_iface.py 会把每个 cell 按 row_action 分成 prune / conly / "
        "full_rc 三类：row_action=prune 的 cell 默认裁掉，但如果它的 cell_map "
        "或 device_map 里 status 不是 verified 就会被「rescue」回 full_rc（保留"
        "完整 RC 网络），导致本来该裁的 73408 个 cell 一个都没裁掉。\n\n"
        "已知 8T bitcell 的 source/bulk 网在层次 split 视图（全局 supply/内部"
        " net）和 flat conly 视图（instance 前缀的 terminal）之间天然不同，因此 "
        "device_map 里出现的 pin_mismatch:S 和 pin_mismatch:B 是**预期内**的，"
        "不应阻止裁剪；其余非 verified 状态（model_mismatch、arity_mismatch、"
        "occurrence_conflict、missing_split）仍然要 rescue。\n\n"
        "请写一个独立的 Python 脚本 sram_tailor_plan_classify.py（仅用标准库），"
        "读三份输入并产出一份 JSON 摘要，用于核对裁剪分类是否正确：\n"
        "  sram_tailor_plan_classify.py <cell_map.tsv> <device_map.tsv> "
        "<rules.json> <out_summary.json>\n\n"
        "输入：\n"
        "- cell_map.tsv：表头 cell_id\\trow_action\\tstatus，每行一个 cell；"
        "row_action ∈ {prune, conly, full_rc}。\n"
        "- device_map.tsv：表头 cell_id\\tstatus，同套 status 词汇。\n"
        "- rules.json：{ \"acceptable_mismatches\": [\"pin_mismatch:S\", "
        "\"pin_mismatch:B\"] } —— 列出哪些 device-map mismatch 是可接受、不"
        "阻止裁剪的（不同数据集这个列表会变，必须从 rules.json 读，不能硬编码）"
        "。\n\n"
        "分类规则：\n"
        "- 一个 cell 是 unverified_blocking 当且仅当：cell_map 的 status ≠ "
        "verified 且 ∉ acceptable_mismatches，**或** device_map 的 status ≠ "
        "verified 且 ∉ acceptable_mismatches。\n"
        "- 最终 action：row_action==\"prune\" 且 unverified_blocking → full_rc"
        "（被 rescue）；否则保持 row_action（conly / full_rc 的 row action 不会"
        "被 rescue）。\n\n"
        "输出 out_summary.json：\n"
        "{ \"total_cells\": <int>, \"final_counts\": {\"prune\":<int>,"
        "\"conly\":<int>,\"full_rc\":<int>}, \"rescued_from_prune\":[<cell_id>,"
        "...]（排序）, \"unverified_blocking\":[<cell_id>,...]（排序）, "
        "\"prunable_cells\":[<cell_id>,...]（排序，最终 action==prune 的）}。\n\n"
        "交付：把 sram_tailor_plan_classify.py 打包成 outputs/submit.zip。可见"
        "资产 A（cell_map.tsv / device_map.tsv / rules.json / task_brief.md）"
        "用于理解 schema 和自测；隐藏评估集 B1/B2 的 cell 数、status 分布和 "
        "acceptable_mismatches 都和 A 不同，硬编码 A 的答案会判失败。"
    ),
    "attachments": [
        {"name": "cell_map.tsv",
         "source": "A/cell_map.tsv",
         "desc": "可见 SRAM tailor cell map（asset A，50 cells）：cell_id / "
                 "row_action(prune|conly|full_rc) / status(verified|pin_mismatch:S"
                 "|pin_mismatch:B|model_mismatch|arity_mismatch|"
                 "occurrence_conflict|missing_split)。用于理解 schema 与自测。"
                 "隐藏 B1/B2 结构相同但 cell 数与分布不同。"},
        {"name": "device_map.tsv",
         "source": "A/device_map.tsv",
         "desc": "可见 SRAM tailor device map（asset A，50 cells）：cell_id / "
                 "status，与 cell_map 同套 status 词汇。device_map 的 status "
                 "分布与 cell_map 独立，分类时必须同时查两份 map。"},
        {"name": "rules.json",
         "source": "A/rules.json",
         "desc": "可见分类规则（asset A）：acceptable_mismatches="
                 "[\"pin_mismatch:S\",\"pin_mismatch:B\"]，列出不阻止裁剪的 "
                 "device-map mismatch。隐藏 B2 的 acceptable_mismatches 只含 "
                 "pin_mismatch:S（反硬编码），必须从 rules.json 读。"},
        {"name": "task_brief.md",
         "source": "task_brief.md",
         "desc": "交付接口说明：sram_tailor_plan_classify.py 四参 CLI、"
                 "unverified_blocking 判定、prune→full_rc rescue 规则、"
                 "输出 JSON schema、反硬编码要求。"},
    ],
    "test": test_src,
    "metadata": {
        "domain": "spice_sim",
        "layer": "L1",
        "layer_rationale": (
            "纯离线 Python：读 TSV/JSON、按 rules.json 的 acceptable_mismatches "
            "做 cell 分类、写 JSON 摘要。不调任何 EDA 沙盒工具、不跑仿真，"
            "属于「读附件写脚本」的 L1 复刻。金标准=plan_iface.py Option A 修复"
            "（pin_mismatch:S/B 不阻止裁剪）后的分类逻辑。"
        ),
        "test_rationale": (
            "14 条断言：① zip 含 sram_tailor_plan_classify.py ② 脚本 py_compile "
            "通过 ③ B1 运行 exit 0 且产出非空 summary ④ B1 total_cells=80 "
            "⑤ B1 final_counts 三项(prune/conly/full_rc)与金标准一致 ⑥ B1 "
            "rescued_from_prune 数=15 ⑦ B1 unverified_blocking 数=24 ⑧ B1 "
            "prunable_cells 数=35 ⑨ B2 运行 exit 0 且产出 summary ⑩ B2 "
            "total_cells=60 ⑪ B2 final_counts(prune/full_rc)与金标准一致 "
            "⑫ B2 rescued_from_prune 数=20（反硬编码：B2 只接受 pin_mismatch:S，"
            "若硬编码 B1 规则会得 15 而非 20）⑬ B2 unverified_blocking 数=29 "
            "（pin_mismatch:B 在 B2 里阻止裁剪）⑭ B1 与 B2 final_counts 不同"
            "（证明脚本数据驱动、非返回常量）。"
        ),
        "trace_source": {
            "user": "e0044979",
            "host": "hfeg0pkn001",
            "session_file": "1793771550244_nlf6u.messages.json",
            "match_count": 146,
            "real_task_summary": (
                "e0044979@hfeg0pkn001 对 1M×72 SRAM（顶层 "
                "CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS，8T bitcell）做 FineSim "
                "仿真前的 DSPF 裁剪调试（236 msgs，1.9MB session；11-08 "
                "parked note「FineSim detect_prep log debug, archive 待查」）。"
                "U#1「我跑脚本裁剪电路，碰到错误 ERROR: detect: testbench "
                "needs exactly one direct .include defining the conly top」= "
                "debug-paste；U#2「Check the tailor plan ... check whether "
                "cell still keep full_rc」= CLEAN 分析需求（提目标，未给根因）；"
                "U#6「Fix the code with Option A, I've backup the code」给出"
                "修复方向→按 §A-② 排除 A 档，走 B-synthesized。assistant 读 "
                "plan.log（row actions: full_rc 10/conly 38/prune 976 rows；"
                "cell actions: conly 2072/full_rc 73704/prune 0；interface "
                "mapping_not_verified=73408）+ plan_iface.py + xa.toggle（272229 "
                "nodes），定位根因=73408 cell 全因 mapping_not_verified 被 rescue"
                "回 full_rc；产 sed_fix.sed/apply_patch.sh/fix_plan_iface.py 把 "
                "plan_iface.py 的 unverified_devices 查询加 AND status NOT IN "
                "('pin_mismatch:S','pin_mismatch:B')。本 case 取其 cell-action "
                "分类逻辑（pin_mismatch:S/B 可接受、其余 mismatch 仍 rescue）"
                "做离线分类器。re-peel 依据：原 park note 标「archive 待查」但"
                "本 session 即全量（1.9MB .messages.json，无独立 archive），"
                "深 peek 证实 U#2 = CLEAN produce-task + U#6 给修复方向→"
                "B-synthesized viable。"
            ),
        },
    },
}

jsonl_path = os.path.join(EDA_BENCH_ROOT, "EDA-Eval-DesignFlow_B.jsonl")
with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", CASE, "to", jsonl_path)
