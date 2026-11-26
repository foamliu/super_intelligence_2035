#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SimlibIndex-001 to the shard D jsonl.
The test field is the byte-exact content of check.py on disk (so the
assertion-gate k_check == disk label count stays consistent).
"""
import json, os

CASE = "EDA-Eval-DesignFlow-SimlibIndex-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CHECK_PY = os.path.join(BENCH, "reference", CASE, "check.py")
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")

with open(CHECK_PY) as f:
    test_src = f.read()

rationale = (
    "14 条断言："
    "①submit.zip 内含 3 件交付物(simlib_ref_db.py/ref_index.json/ref_table.txt)齐全 "
    "②simlib_ref_db.py 通过 py_compile 语法校验 "
    "③候选工具在隐藏 simlib B 上以 --simlib/--json/--table CLI 运行退出码 0 "
    "④B 索引含全部 13 个 B 专属 module 名且无 A 名(反硬编码 A 索引) "
    "⑤B 索引排除 decoy task monitorTask/function f_count(只索引 module) "
    "⑥B ref_table.txt 列出全部 13 个 B module 名 "
    "⑦B 精确查询 inv_base_simple 返回该 module 完整原文(module/endmodule/pp m1 齐全,非邻居块) "
    "⑧B 精确查询 inv_base_simple 的 snippet 含 `celldefine 包裹(celldefine=True 条目) "
    "⑨B 子串查询 LbusDrvB 匹配 CK_LbusDrvB 或 CMD_LbusDrvB 且 score>=0.85 "
    "⑩B 无匹配查询 zzz_nonexistent_cell 返回无 reference(无 matched 头) "
    "⑪B 家族后缀查询 dlyrc_baseX 匹配 dlyrc_base 且 score>=0.85 "
    "⑫B snippet(max_chars=80) 长度<=80 且以 '...' 结尾(截断生效) "
    "⑬B 两次运行索引 JSON 字节一致(确定性) "
    "⑭隐藏 B2(不同名/结构)运行退出码 0 且索引含 12 个 B2 专属名含 mux4_base/ck_bufB2(反硬编码 A/B)"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": (
        "你是 EDA 工程师 e0039602，在 hfeg0plg17 上维护 netlist_cell_convert 工具链（把 schematic 导出的抽象 cell Verilog 网表转成 simlib 物理单元）。"
        "为了提高转换时 LLM 推理的准确性，现在要新增一个**参考示例库**模块：把黄金结果库 simlib_drcoa_digital.sv 里所有 model 的名字解析出来建成可索引表格，"
        "每次要转换一个新 model 时，用它的名字在该表里做精确/相似匹配，命中后把对应 model 的整段原文取出来拼进 prompt 作为参考示例，让模型照着模仿。\n\n"
        "真实场景里的相似匹配要处理：同名精确命中、同家族加后缀变体（如 _gut / _gut2 / _youmingz，靠子串包含 + difflib.SequenceMatcher + 同后缀加宽打分）、"
        "完全无匹配（返回空）、以及把命中的 model 原文（含 `celldefine 包裹）按 max_chars 截断拼成参考示例文本。索引只收 module，不能把 task/function 也收进来。\n\n"
        "交付：outputs/submit.zip，内含 simlib_ref_db.py（实现，纯 Python 标准库，确定性，对任意 simlib SV 通用）、ref_index.json（对附件 simlib_sample.sv 建好的索引）、ref_table.txt（可读名字表）。"
        "详细解析/匹配/检索/导出/CLI 规则见 convert_rules.md。隐藏测试输入 B/B2 与附件 A 的 module 名/数量/家族完全不同，工具必须泛化规则而非记忆 A 的具体名字。"
    ),
    "attachments": [
        {"name": "simlib_sample.sv", "source": "simlib_sample.sv",
         "desc": "黄金结果库样本（13 个 module，含 `celldefine 包裹与未包裹、家族后缀变体 _gut/_gut2、CK_LbusDrv/CMD_LbusDrv 同族）"},
        {"name": "query_cells.json", "source": "query_cells.json",
         "desc": "查询示例（exact / substring_family / substring / no_match），展示期望匹配行为"},
        {"name": "convert_rules.md", "source": "convert_rules.md",
         "desc": "解析/四档打分/检索/导出/CLI 规则（必须复刻：exact 1.0、子串 0.85-0.9、SequenceMatcher、同后缀 +0.06 封顶；--query 时 stdout 只输出 snippet）"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "交付接口与文件位置 + 约束（纯标准库、确定性、对隐藏 B 通用）"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["simlib_ref_db.py", "ref_index.json", "ref_table.txt"],
    "test": test_src,
    "budget": {"max_turns": 25, "wall_time_sec": 1800},
    "metadata": {
        "domain": "schematic_netlist",
        "task_name": "simlib model-name index + similarity-matching reference-example retriever",
        "scenario": "解析 simlib SV 全部 module 建可索引表，按名字精确/相似匹配，取命中 model 原文拼参考示例进 prompt",
        "direction": "simlib model-name index + fuzzy-match reference retrieval",
        "layer": "schematic_netlist",
        "topic": "simlib_ref_db (model-name index + similarity match)",
        "difficulty": "L1",
        "design": "offline-Python deterministic simlib indexer; hidden B/B2 test generalization (different names/count/families, decoy task/function)",
        "tcr_refs": "enbl7 deepread (SimlibRefDB: _score 4-tier, find_reference, reference_snippet, to_json/to_table, CLI)",
        "heavy": "python",
        "wall_time_sec": 1800,
        "trace_source": {
            "host": "hfeg0plg17",
            "user": "e0039602",
            "session_file": "1792573537545_enbl7",
            "session_msgs": 344,
            "match_count": 515,
            "real_task_summary": "netlist_cell_convert 增量: simlib_drcoa_digital.sv 全 model 名解析建可索引表 + 精确/相似匹配 + 命中 model 原文拼参考示例进 prompt + prompt 监视器 + 3 进程并行 + 无限重试",
        },
        "test_rationale": rationale,
    },
}

# verify no duplicate task_id in D jsonl
existing = []
with open(JSONL) as f:
    for ln in f:
        ln = ln.strip()
        if not ln:
            continue
        existing.append(json.loads(ln)["task_id"])
if CASE in existing:
    print("ERROR: %s already in D.jsonl — not appending (would duplicate)" % CASE)
    raise SystemExit(1)

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify write + test field == disk check.py roundtrip
with open(JSONL) as f:
    last = None
    for ln in f:
        ln = ln.strip()
        if ln:
            last = ln
c = json.loads(last)
assert c["task_id"] == CASE, "last entry not the new case"
assert c["test"] == test_src, "test field != disk check.py (roundtrip mismatch)"
# assertion gate: k_rationale == k_check
import re
# count ACTUAL condition labels: those appearing as "(x) " inside assert
# message strings (e.g. assert ..., "(a) ..."). Ignore incidental (p)/(x) in
# prose like os.path.isfile(p) or "for x in ...".
cond_labels = sorted(set(re.findall(r'"\(([a-z])\)\s', test_src)))
n_check = len(cond_labels)
n_rationale = sum(1 for ch in rationale if ch in "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮")
print("appended %s" % CASE)
print("k_check (labels in test) = %d  labels=%s" % (n_check, cond_labels))
print("k_rationale (①-⑮ marks) = %d" % n_rationale)
print("GATE: k_rationale == k_check >= 8 ->", n_rationale == n_check and n_check >= 8)
print("D.jsonl now has %d entries" % (len(existing) + 1))
