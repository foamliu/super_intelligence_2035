#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-verify for StarRCFlow-001: §4.9 three-fake FAIL + assertion gate + disk roundtrip + append jsonl."""
import os, sys, io, json, zipfile, tempfile, shutil, importlib.util, subprocess, csv

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-StarRCFlow-001"
R_DIR = os.path.join(ROOT, "reference", CASE)
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_A.jsonl")
H_DIR = os.path.join(ROOT, "hidden", CASE)

sys.path.insert(0, R_DIR)
spec = importlib.util.spec_from_file_location("chk", os.path.join(R_DIR, "check.py"))
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)

REF_FILES = ["setup_and_run.sh", "run_gxtr_MULTI_CORNER.csh", "autorun_gxtr_v0d1.csh",
             "extract_rc.py", "extract_net_info.py"]

def make_submit_with(overrides):
    tmp = tempfile.mkdtemp()
    for fn in REF_FILES:
        shutil.copy(os.path.join(R_DIR, fn), os.path.join(tmp, fn))
    for fn, content in overrides.items():
        with open(os.path.join(tmp, fn), "w") as f: f.write(content)
        os.chmod(os.path.join(tmp, fn), 0o755)
    z = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(z, "w") as zf:
        for fn in REF_FILES:
            zf.write(os.path.join(tmp, fn), fn)
    return z

# §4.9 three degenerate submissions (distinct from the 5 negatives)
print("=== §4.9 three-fake regression ===")
fakes = {
    "empty_shell": {"setup_and_run.sh": "#!/bin/bash\n# empty shell\n"},
    "print_expected": {"setup_and_run.sh": "#!/bin/bash\necho 'module: ds/star/2020.09-SP5-4'\necho 'StarXtract: /fake/StarXtract'\necho 'first 5'\n"},
    "core_deleted": {"autorun_gxtr_v0d1.csh": "#!/bin/csh -f\n# core StarXtract call deleted\necho running $1\n"},
}
fake_results = {}
for name, ov in fakes.items():
    z = make_submit_with(ov)
    try:
        chk.check(z, ".")
        fake_results[name] = "PASS-MUST-FAIL !!"
    except AssertionError as e:
        fake_results[name] = "FAIL-OK: %s" % str(e)[:90]
    except Exception as e:
        fake_results[name] = "FAIL-OK(exc): %s" % str(e)[:90]
for k,v in fake_results.items(): print("  ", k, "->", v)
sec49_ok = all(v.startswith("FAIL-OK") for v in fake_results.values())
print("  §4.9 PASS" if sec49_ok else "  §4.9 BROKEN")

# Assertion gate: count independent conditions in check.py
print("=== assertion gate ===")
src = open(os.path.join(R_DIR, "check.py")).read()
cond_labels = re.findall(r'_cond\("([a-z]+)"', src) if 're' in dir() else []
import re
cond_labels = re.findall(r'_cond\("([a-z]+)"', src)
k_check = len(cond_labels)
RATIONALE = ("16 条断言：① zip 含 5 交付脚本 ② setup_and_run.sh 语法 OK 且可执行 "
             "③ --show-version 报 StarXtract 路径+module ④ --cell-list first 5 恰 5 行且源自 B CCI_data "
             "⑤ --cell-list random 3 恰 3 行且随机 ⑥ run_gxtr/autorun 以真实命令调 StarXtract 且有循环 "
             "⑦ run_gxtr 产 done.list ⑧ run_gxtr 时间戳目录名匹配 yymmddHHMMSS "
             "⑨ extract_rc.py 产合法 CSV 且行数==B *|NET 总数 ⑩ extract_net_info.py per-cell cap 汇总与 SPF 一致 "
             "⑪ --clean 保留旧 rundata ⑫ --version 切换后报新 module ⑬ 跨输入护卫 B token 不在 A feint "
             "⑭ 3 种子重跑结构一致 ⑮ SPF RC 量纲合理 ⑯ 三假提交（空壳/print-stub/core-deleted）均 FAIL")
k_rationale = RATIONALE.count("①") + RATIONALE.count("②") + RATIONALE.count("③") + RATIONALE.count("④") + \
              RATIONALE.count("⑤") + RATIONALE.count("⑥") + RATIONALE.count("⑦") + RATIONALE.count("⑧") + \
              RATIONALE.count("⑨") + RATIONALE.count("⑩") + RATIONALE.count("⑪") + RATIONALE.count("⑫") + \
              RATIONALE.count("⑬") + RATIONALE.count("⑭") + RATIONALE.count("⑮") + RATIONALE.count("⑯")
# count circled numbers properly
import unicodedata
circ = [c for c in RATIONALE if ord(c) >= 0x2460 and ord(c) <= 0x2473]
k_rationale = len(circ)
print("  k_rationale=%d  k_check=%d  labels=%s" % (k_rationale, k_check, cond_labels))
gate_ok = (k_rationale == k_check) and (k_check >= 8)
print("  gate PASS" if gate_ok else "  gate FAIL")

# disk roundtrip: re-open reference_submit.zip, re-run check
print("=== disk roundtrip ===")
z = os.path.join(R_DIR, "reference_submit.zip")
roundtrip_ok = False
try:
    chk.check(z, ".")
    roundtrip_ok = True
    print("  roundtrip PASS")
except Exception as e:
    print("  roundtrip FAIL:", e)

# Final verdict
all_ok = sec49_ok and gate_ok and roundtrip_ok
print("=== FINAL ===", "ALL_OK" if all_ok else "NOT_OK")
sys.exit(0 if all_ok else 1)
