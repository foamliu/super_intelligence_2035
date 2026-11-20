#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-HilightCsvGroupGen-001 to EDA-Eval-DesignFlow_C.jsonl.
test field is the exact bytes of the on-disk check.py (byte-equal guarantee)."""
import json, os

CASE = "EDA-Eval-DesignFlow-HilightCsvGroupGen-001"
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
        "assets/%s/config_A.csv" % CASE,
        "assets/%s/rules_A.txt" % CASE,
    ],
    "test": test_src,
    "metadata": {
        "domain": "layout_virtuoso",
        "level": "L1",
        "track": "B-synthesized",
        "trace_source": {
            "user": "e0045488",
            "host": "hfeg0pkn004",
            "session_file": "1793688752516_jd1wq",
            "match_count": 64,
            "real_task_summary": (
                "Virtuoso layout bbox highlight generator: parse a resistor-segment CSV "
                "(auto-detect comma vs whitespace format), group bboxes by a layer-rules file "
                "('Label: pattern' with trailing '*' prefix-wildcard), emit a SKILL .il that "
                "highlights each group on its own y<N>/drawing layer with a cycled palette/halo "
                "and a label at the first bbox centre, plus clear-previous-highlights logic."
            ),
        },
        "test_rationale": (
            "17 条断言：①(a) submit.zip 合法且仅含 gen_hilight.py 一个文件(无 reference/check/jsonl 泄漏) "
            "②(b) 候选脚本 py_compile 通过(语法合法) "
            "③(c) 仅 Python 标准库(禁 gdspy/calibre/numpy/pandas/sklearn/scipy/matplotlib/aether/pyAether/lxml/bs4/requests) "
            "④(d) 隐藏输入 B(逗号格式 CSV,layer/rules vocab 与 A 不同)运行 exit0 "
            "⑤(e) 输出 .il 非空 "
            "⑥(f) .il 含 geGetEditCellView() + unless(cv ...) 守卫 "
            "⑦(g) .il 含清高亮逻辑(boundp('hilightSets) + foreach(hiSet hilightSets) + geDeleteHilightSet + hilightSets=nil) "
            "⑧(h) geCreateHilightSet(cv 调用数 == B 有 bbox 的组数(3 组 M1/ND/PD/M2) "
            "⑨(i) geAddHilightRectangle 调用数 == B 有效 bbox 总数(7,跳过 '-' 坐标行 R9p 与 unmatched 行 unknown_lay) "
            "⑩(j) geAddHilightLabel 调用数 == 3 且标签字符串含 M1/ND/PD/M2(精确无截断) "
            "⑪(k) geSetHilightSetHaloParameters 调用数 == 3(每组一个) "
            "⑫(l) .il 末行含 printf(\"Grouped bbox highlights applied.\") "
            "⑬(m) 反硬编码: B 输出含 B 标签(M1/ND/PD/M2)且不含 A 专属标签(M0/BM1/nsd/psd) "
            "⑭(n) 确定性: 同 --out 路径连跑 3 次 sha256 完全一致 "
            "⑮(o) B 组 M1 bbox 计数 == 3(metal1A/metal1B/metal1C 经 metal1* 前缀通配归入) "
            "⑯(p) B 组 ND/PD bbox 计数 == 2(ndiff/pdiff 经精确 base_layer 匹配归入) "
            "⑰(q) B 组 M2 bbox 计数 == 2(m2_sig/m2_vdd 经 m2* 前缀通配归入)"
        ),
    },
}

line = json.dumps(entry, ensure_ascii=False)
# validate round-trip + test==disk
parsed = json.loads(line)
assert parsed["test"] == test_src, "test field != disk check.py"
# dedup guard: don't append if id already present (old entries use task_id)
with open(JSONL, "r", encoding="utf-8") as f:
    ids = []
    for l in f:
        if not l.strip(): continue
        o = json.loads(l)
        ids.append(o.get("id") or o.get("task_id"))
assert entry["id"] not in ids, "id already in jsonl_C: %s" % entry["id"]
with open(JSONL, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("appended %s to %s (jsonl_C now %d lines)" % (CASE, os.path.basename(JSONL), len(ids) + 1))
print("test bytes:", len(test_src), "rationale k=", entry["metadata"]["test_rationale"].count("条断言") or 17)
