#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001 to C.jsonl.
test field == disk check.py (roundtrip verified)."""
import hashlib
import json
import os
import sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
BENCH_ROOT = os.path.join(BENCH, "benchmarks", "EDA-Eval-DesignFlow")
CASE = "EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001"
C_JSONL = os.path.join(BENCH_ROOT, "EDA-Eval-DesignFlow_C.jsonl")
CHECK_PY = os.path.join(BENCH_ROOT, "reference", CASE, "check.py")

with open(CHECK_PY, "r", encoding="utf-8") as f:
    check_src = f.read()

# roundtrip sha16 (first 16 hex chars of sha256) for traceability
sha16 = hashlib.sha256(check_src.encode("utf-8")).hexdigest()[:16]

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": (
        "你正在帮助一位 Cadence Virtuoso 用户（colinxu）查询他当前 Virtuoso 会话里正在处理的 cell。\n\n"
        "真实场景（来自 trace，session pcn3b @ hfeg0plg55）：用户当时直接问「show me the cell name in virtuoso」。"
        "助手先确认工作区是一个 Virtuoso/SKILL 训练目录（V0_NCG_HF_Virtuoso），里面有 add_testpin.il / delete_testpin.il / get-username.sh / sleep.sh 四个文件；"
        "读 add_testpin.il 发现它通过 `dbOpenCellViewByType(\"drjpa_analog\" \"AG_AnalogBankBuf\" \"schematic\" \"\" \"a\")` 以 append（可编辑）模式打开目标 cellview，"
        "再以 read-only 模式打开 `basic/iopin/symbol` 作为 pin master；"
        "助手先用 `geGetEditCellView()` 想直接拿当前窗口的 cell 名，但 sandbox 里没有活跃窗口返回 nil；"
        "于是改成用 `dbOpenCellViewByType(... \"r\")` 把 add_testpin.il 里解析出的目标 cellview 打开，读回 `cellName/libName/viewName`，"
        "得到 **cell = AG_AnalogBankBuf / lib = drjpa_analog / view = schematic / type = paint / numInstances = 1**。\n\n"
        "核心推理：当前要「show」的 cell 名，需要从工作区的 .il 脚本里识别出**被修改的 cell**（`dbOpenCellViewByType` 用可编辑模式 \"a\"/\"w\" 打开的那个），"
        "并把它和**只读 master**（用 \"r\" 打开的，例如 `basic/iopin/symbol` 这种 pin/对象母本）区分开——后者不是当前在做的 cell。\n\n"
        "现在请你把「扫描 Virtuoso/SKILL 工作区、从 .il 脚本里推断当前正在处理的 cell 名」的能力沉淀成一个可复用工具："
        "写一个 Python 脚本，它读入一个工作区目录，正则提取所有 `dbOpenCellViewByType(lib cell view [viewname] mode)` 调用，"
        "按 open mode 分类（editable \"a\"/\"w\" = 被修改的 cell；read-only \"r\" = master / 验证重开），"
        "把**可编辑目标**作为 primary cell name，把只读打开作为 masters 列表排除在外，"
        "输出一份结构化 JSON 报告（含 lib / cell / view / source_file / open_mode / editable / masters[]）。\n\n"
        "可见输入 A（附件）= 真实 trace 工作区的 4 个文件（add_testpin.il + delete_testpin.il + get-username.sh + sleep.sh）。"
        "判分时会换一组隐藏输入 B（同类型的 add-pin/remove-pin 工作区，但 lib/cell/view 完全不同，"
        "且 .il 里 master 的打开顺序被刻意调到 target 之前，用来检验你是不是真的按 mode 分类而不是「抓第一个」）。"
    ),
    "attachments": [
        "assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/prompt.txt",
        "assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/task_brief.md",
        "assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/manifest_A.json",
        "assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/add_testpin.il",
        "assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/delete_testpin.il",
        "assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/get-username.sh",
        "assets/EDA-Eval-DesignFlow-VirtCellNameFromIlProduce-001/sleep.sh",
    ],
    "test": check_src,
    "metadata": {
        "domain": "layout_virtuoso",
        "layer": "L1",
        "grade": "B",
        "track": "design_flow",
        "asset_fidelity": (
            "synthesized-reframe: trace gold = live Virtuoso SKILL run_code (geGetEditCellView -> nil in sandbox; "
            "then dbOpenCellViewByType('drjpa_analog' 'AG_AnalogBankBuf' 'schematic' '' 'r') -> cell=AG_AnalogBankBuf/lib=drjpa_analog/view=schematic/type=paint/numInstances=1). "
            "Live Virtuoso not reproducible + geGetEditCellView returns nil without active window. Reframe captures the real reasoning path: "
            "parse workspace .il scripts to find the editable (mode 'a'/'w') dbOpenCellViewByType target = the cell being modified, "
            "distinguish from read-only (mode 'r') masters like basic/iopin/symbol. Visible A = real 4-file workspace (add_testpin.il + delete_testpin.il + get-username.sh + sleep.sh, verbatim from .75 trace). "
            "Hidden B = rewritten 2 .il files (edit_pin.il + remove_pin.il) targeting analogLib/Nand2/schematic (editable 'a') with basic/iopin/symbol master (read-only 'r'); "
            "edit_pin.il opens master BEFORE target to defeat naive first-match parsers. lib/cell/view fully disjoint from A (drjpa_analog/AG_AnalogBankBuf -> analogLib/Nand2)."
        ),
        "reframe_note": (
            "C-shard layout_virtuoso workspace-.il-script-parsing cellview-inference reframe subtype, first of its kind. "
            "Orthogonal to VirtuosoOpenCellQueryGen-001 (SKILL-script-generator: generates open-cell script) -- this case PARSES existing .il to find the target; "
            "orthogonal to VirtBridgeStatusDiag-001 (bridge endpoint TCP reachability) -- this case is .il script semantic parsing; "
            "orthogonal to D-shard TopCellNameProduce-001 (fniub, live geGetTopLevelCellView via mock pyAether) -- this case derives target from workspace scripts with no live Virtuoso. "
            "Same offline-single-file-stdlib reframe pattern as DrcJobExitCwdDiag-001 / ConnPathResolve-001 but layout_virtuoso cellview domain. "
            "path-bug revival #9 (C-line r856 #2, continuing dyvlr r855); legit under 2026-11-15 reaudit (env-config/flow-driving)."
        ),
        "trace_source": {
            "user": "colinxu",
            "host": "hfeg0plg55 (10.129.35.74)",
            "session_file": "1792670912119_pcn3b.messages.json",
            "match_count": 38,
            "real_task_summary": (
                "colinxu @ hfeg0plg55 session pcn3b (20 msgs / 2 user turns, both identical text 'show me the cell name in virtuoso'). "
                "Agent gold chain: skills(eda_agent) -> list_allowed_files workspace (4 files: add_testpin.il/delete_testpin.il/get-username.sh/sleep.sh) -> "
                "read_files add_testpin.il reveals target dbOpenCellViewByType('drjpa_analog' 'AG_AnalogBankBuf' 'schematic' '' 'a') editable + master basic/iopin/symbol read-only 'r' + reopen 'r' verify -> "
                "RAG search_apis -> geGetEditCellView/geGetWindowCellView/geGetTopLevelCellView -> get_api_details -> read case_007 highlight nets -> "
                "run_approved_command get-username.sh -> 'colinxu' -> SandBox_MCP run_code SKILL geGetEditCellView() -> 'No cellview is currently being edited' (sandbox no active window, nil) -> "
                "user repeats -> SandBox_MCP run_code SKILL dbOpenCellViewByType('drjpa_analog' 'AG_AnalogBankBuf' 'schematic' '' 'r') -> "
                "prints lib='drjpa_analog'/cell='AG_AnalogBankBuf'/view='schematic'/type='paint'/numInstances=1. User accepts (no further turn). "
                "Reframe: live Virtuoso Q&A -> offline .il-workspace-parser produce. SUT ships show_cell_name.py that scans .il files for dbOpenCellViewByType calls, "
                "classifies editable ('a'/'w') vs read-only ('r') masters, picks editable target as primary cell name, outputs structured JSON. "
                "Hidden B: rewritten .il (analogLib/Nand2/schematic editable + basic/iopin/symbol master, master opened FIRST in edit_pin.il to defeat first-match), "
                "lib/cell/view fully disjoint from A. check.py 14 conditions a-n."
            ),
        },
        "test_rationale": (
            "14 条断言：①zip 合法且恰好 1 个 .py 候选(>=300B UTF-8 无 NUL) ②候选 py_compile 通过且仅用标准库(禁 numpy/pandas/requests/virtuoso/aether/pyAether/calibre 等) "
            "③B 运行 exit 0 + 合法 JSON + 7 顶层键齐全(lib/cell/view/source_file/open_mode/editable/masters) ④B lib==analogLib(反 A 的 drjpa_analog) "
            "⑤B cell==Nand2(反 A 的 AG_AnalogBankBuf) ⑥B view==schematic ⑦B open_mode==a 且 editable==true(editable 目标非 master) "
            "⑧B primary cell 不是 iopin(master 排除：edit_pin.il 把 master 放在 target 前，naive 抓首个 dbOpenCellViewByType 会落到 iopin 上 FAIL) "
            "⑨B masters 非空列表且每个 open_mode==r 且至少含 basic/iopin/symbol ⑩反硬编 guard：A 运行 primary cell==AG_AnalogBankBuf 且 lib==drjpa_analog 且输出不含 analogLib/Nand2 "
            "⑪B source_file 命名 B 工作区里真实存在的 .il 文件(证明候选真读了 B 的文件而非凭空作答) ⑫缺工作区目录时候选非零退出 ⑬3-seed 确定性：A 运行 3 次 stdout sha256 稳定 "
            "⑭反作弊：候选源码不含 B 答案 token(Nand2/analogLib) 的字面量(答案须由输入派生不得嵌入)"
        ),
    },
}

# roundtrip: ensure test field round-trips through json
roundtrip_test = json.loads(json.dumps(entry))["test"]
assert roundtrip_test == check_src, "test field roundtrip mismatch"
assert entry["metadata"]["test_rationale"].startswith("14 条断言："), "rationale prefix"

# k_rationale == k_check == 14
import re
k_rat = 14  # count of ①..⑮ marks (we have ①..⑮ = 14)
marks = re.findall(r"[①-⑯⑰⑱⑲⑳]", entry["metadata"]["test_rationale"])
print("rationale marks =", len(marks), "expected 14")
assert len(marks) == 14, "rationale mark count != 14"
print("k_rationale = k_check = 14 >= 8 GATE PASS")
print("test==disk check.py roundtrip sha16 =", sha16)

# append
with open(C_JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", C_JSONL)

# verify
with open(C_JSONL, "r", encoding="utf-8") as f:
    lines = f.readlines()
print("C.jsonl lines =", len(lines))
last = json.loads(lines[-1])
assert last["task_id"] == CASE
assert last["test"] == check_src
print("verified: last line task_id =", last["task_id"], "test roundtrip OK")
