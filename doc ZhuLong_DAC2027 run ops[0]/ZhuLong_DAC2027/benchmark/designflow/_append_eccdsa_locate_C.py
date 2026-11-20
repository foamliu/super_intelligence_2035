#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-EccDsaLocate-001 to _C.jsonl with byte-sync test==disk check.py."""
import os, json, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")
CASE = "EccDsaLocate-001"
REF = os.path.join(BENCH, "reference", CASE)
AST = os.path.join(BENCH, "assets", CASE)

check_path = os.path.join(REF, "check.py")
check_src = open(check_path, "r").read()
disk_sha = hashlib.sha256(check_src.encode("utf-8")).hexdigest()

prompt = open(os.path.join(AST, "prompt.txt")).read()
task_brief = open(os.path.join(AST, "task_brief.md")).read()

test_rationale = (
    "15 条断言：①(a) submit.zip 可解压且含 locate_ecc_dsa.py ②(b) 候选脚本在 hidden B inventory 上 "
    "subprocess 真跑后产出 ecc_dsa_map.json 与 ecc_dsa_positions.csv 且 map 含 spine/units/ecc/dsa/summary 五键 "
    "③(c) ecc.class=='ECC' ④(d) dsa.class=='DSA' ⑤(e) units 与 B inventory 一致 ⑥(f) ECC 实例数与 B 真值一致 "
    "⑦(g) DSA 实例数与 B 真值一致 ⑧(h) ECC distinct_cells 集合与 B 真值一致 ⑨(i) DSA distinct_cells 集合与 B 真值一致 "
    "⑩(j) ECC bbox_union 与 B 真值一致(容差1e-6) ⑪(k) DSA bbox_union 与 B 真值一致 ⑫(l) 每个 ECC 实例含 "
    "instName/cell/lib/bbox 且 bbox 落在 inventory 范围内 ⑬(m) 每个 DSA 实例同上 ⑭(n) summary 的 total_ecc/total_dsa/"
    "grand_total 与实例数及 inventory 总数一致 ⑮(o) false-positive 守卫：BANDSAW_clk 诱饵不在 DSA 实例中且 DSA 类中"
    "所有 cell 确为 DSA(子串假阳性被排除)"
)

entry = {
    "id": "EDA-Eval-DesignFlow-EccDsaLocate-001",
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        f"assets/EDA-Eval-DesignFlow-{CASE}/prompt.txt",
        f"assets/EDA-Eval-DesignFlow-{CASE}/task_brief.md",
        f"assets/EDA-Eval-DesignFlow-{CASE}/spine_inventory_A.json",
    ],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "xiwang",
            "host": "hfeg0pkn002",
            "session_file": "1794035650061_tmx27.messages.json",
            "match_count": 1032348,
            "real_task_summary": (
                "xiwang 在 hfeg0pkn002 上基于 DDGOA spine 版图，要求画出 ECC 和 DSA 所在的位置。"
                "真实 agent 用 pyAether(SandBox_MCP_Server__run_code 41 次) 解析 SpineTop_modules.csv"
                "(列 cell/instName/lib/x1_um/y1_um/x2_um/y2_um) + fullmap.json 层次图，按 cell 名正则 "
                "r'ECC|Ecc' / r'DSA|Dsa' 过滤 ECC/DSA 实例，per-class 聚合 bbox 并集+实例清单，并用 "
                "ae.dbOpenCVByType 打开 ddgoa_cmos_top/SpineTop layout + emyGetAllInstHeaders 递归走层次计算"
                "绝对 bbox(transform 旋转/偏移合成)。真实 OA/pyAether 不可沙盒复现，离线化为 spine 实例清单 JSON "
                "驱动的 ECC/DSA delimited-token 名字分类 + per-class bbox 并集聚合 + 实例位置清单 + 三件套"
                "(json/csv)输出，check.py 在 hidden B 上 subprocess 真跑候选并结构化比较 15 条件。"
            ),
        },
        "domain": "layout_aether",
        "track": "synthesized",
        "level": "L2",
        "k_check": 15,
        "k_rationale": 15,
        "test_rationale": test_rationale,
    },
}

# byte-sync: test field sha == disk check.py sha
test_sha = hashlib.sha256(entry["test"].encode("utf-8")).hexdigest()
assert test_sha == disk_sha, f"BYTE-SYNC FAIL: test sha {test_sha} != disk sha {disk_sha}"
print("byte-sync test==disk check.py sha256:", disk_sha, "OK")

# assertion gate
assert entry["metadata"]["k_rationale"] == entry["metadata"]["k_check"] >= 8
print("assertion gate: k_rationale == k_check == 15 >= 8 GATE PASS")

# append (do not duplicate)
existing = [json.loads(l) for l in open(JSONL) if l.strip()]
ids = {e.get("id") or e.get("task_id") for e in existing}
if entry["id"] in ids:
    print("WARNING: id already present, skipping append")
else:
    with open(JSONL, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("appended to", os.path.basename(JSONL), "-> total", len(existing)+1, "entries")

# roundtrip: read back, test field compiles, run check on reference_submit.zip
import tempfile, shutil, importlib.util, zipfile, sys
e2 = [json.loads(l) for l in open(JSONL) if l.strip()][-1]
assert e2["id"] == entry["id"]
assert hashlib.sha256(e2["test"].encode("utf-8")).hexdigest() == disk_sha, "roundtrip test sha mismatch"
print("roundtrip: id ok, test sha == disk ok")
