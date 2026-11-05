#!/usr/bin/env python3
# _append_spice_deck_pair_diff_001.py -- append SpiceDeckPairDiff-001 to EDA-Eval-DesignFlow_B.jsonl
import os, json, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
CASE = "EDA-Eval-DesignFlow-SpiceDeckPairDiff-001"
REF = os.path.join(BENCH, "reference", CASE)
ASSETS = os.path.join(BENCH, "assets", CASE)

prompt = open(os.path.join(ASSETS, "prompt.txt")).read().rstrip("\n")
test_src = open(os.path.join(REF, "check.py")).read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/" + CASE + "/deck_ref_A.sp",
        "assets/" + CASE + "/deck_cmp_A.sp",
    ],
    "test": test_src,
    "metadata": {
        "trace_source": {
            "user": "e0024852",
            "host": "hfeg0pkn004",
            "session_file": "1791981291929_4oo3i.messages.json",
            "match_count": 134,
            "real_task_summary": (
                "FineSim deck 对比（A-faithful U#7 逐字「I want to know the difference of "
                "_finesim.sp and _finesim_pre.sp」；trace 实为 sim_log_compare.py 解释 + _finesim.sp "
                "vs _finesim_pre.sp 差异讲解，便携子技能=spice deck 配对结构化 diff 报告）"
            ),
        },
        "domain": "spice_sim",
        "track": "faithful",
        "test_rationale": (
            "15 条断言："
            "①(a) zip 含 spice_deck_diff.py 且 py_compile 通过 "
            "②(b) B 运行 exit 0 且产出 deck_diff.json "
            "③(c) 报告 schema 完整（10 顶层键 options/measures/params/tran/stimulus/alter/includes/nodeset_probe/instances/summary + 20 summary 键齐全） "
            "④(d) B options added=={cshunt} 且 removed=={abstol} "
            "⑤(e) B options changed=={post(1→2),reltol(1e-6→1e-9)} 含 ref→cmp 逐条 "
            "⑥(f) B measures added=={v_oh,i_leak} 且 removed=={v_ol} "
            "⑦(g) B measures changed=={t_hold}（同名不同签名） "
            "⑧(h) B params added=={temp} 且 changed=={load,vdd} "
            "⑨(i) B stimulus added=={Vtestb} 且 removed=={} 且 changed=={Vclkb,Vdatab} "
            "⑩(j) B alter ref_count==2 cmp_count==4 delta==2（仅计数 .alter 块，不并入基线字典） "
            "⑪(k) B includes added=={model_ss.inc} 且 removed=={model_ff.inc} "
            "⑫(l) B instances added=={Xn4,Xn5} 且 removed=={Xn3} "
            "⑬(m) B nodeset_delta==2 且 probe_delta==-1 且 tran.changed==True "
            "⑭(n) 跨输入护栏：A 重跑 summary==A GT 且 A measure 名==A GT 且无 B measure 名泄漏 且 A≠B（击败 hardcode-B/print-expected） "
            "⑮(o) 确定性：B 重跑两次 deck_diff.json sha256 一致"
        ),
    },
}

# byte-sync check: test field must equal disk check.py bytes
disk = open(os.path.join(REF, "check.py")).read()
assert entry["test"] == disk, "test field not byte-synced with disk check.py"
print("test field byte-synced OK (md5 %s, %d B)" % (
    hashlib.md5(disk.encode()).hexdigest(), len(disk)))

# count k_rationale circled-number marks vs k_check labels in check.py
import re
circled = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]", entry["metadata"]["test_rationale"]))
labels = set(re.findall(r"_cond\(\"([a-z]+)\"", disk))
print("k_rationale(circled)=%d  k_check(labels)=%d  labels=%s" % (
    circled, len(labels), sorted(labels)))
assert circled == len(labels), "k_rationale != k_check"
assert circled >= 8, "k < 8"
print("GATE PASS: k_rationale=k_check=%d >= 8" % circled)

# append (one line)
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify count + unique ids
lines = open(JSONL).read().splitlines()
ids = []
for ln in lines:
    if not ln.strip():
        continue
    d = json.loads(ln)
    ids.append(d.get("task_id"))
print("jsonl_B lines=%d  unique_ids=%d  last=%s" % (len(lines), len(set(ids)), ids[-1]))
assert len(ids) == len(set(ids)) or ids.count(CASE) == 1
print("appended", CASE)
