#!/usr/bin/env python3
"""Regenerate negatives for AnalogGroupCfgMergeDummy-001 with 6 distinct first_fail conditions.
Negatives: empty_shell(c), print_expected(c), ref_core_deleted(d), hardcode_a(o),
drop_o_labels(i), drop_layout_only(k), wrong_axis(m).
"""
import os, json

CASE = "EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF_DIR = f"{ROOT}/reference/{CASE}"
NEG_DIR = f"{REF_DIR}/negative"
os.makedirs(NEG_DIR, exist_ok=True)

with open(f"{REF_DIR}/gg_cfg_merge_verify_ref.py") as f:
    ref_src = f.read()

# 1. empty_shell -> c (no files)
with open(f"{NEG_DIR}/empty_shell.py", "w") as f:
    f.write('''#!/usr/bin/env python3
import argparse, sys
ap = argparse.ArgumentParser()
for a in ("--base","--patch","--labels","--layout-inst","--sch-inst","--outdir"):
    ap.add_argument(a)
args = ap.parse_args()
sys.exit(0)
''')

# 2. print_expected -> c (prints, no files)
with open(f"{NEG_DIR}/print_expected.py", "w") as f:
    f.write('''#!/usr/bin/env python3
import argparse, sys
ap = argparse.ArgumentParser()
for a in ("--base","--patch","--labels","--layout-inst","--sch-inst","--outdir"):
    ap.add_argument(a)
args = ap.parse_args()
print("merged_cfg.json merge_report.md dummy_audit.json instance_diff.json verdict.json")
print("overall PASS")
sys.exit(0)
''')

# 3. ref_core_deleted -> d (deep_merge returns patch, discards base)
rcd = ref_src.replace(
    "def deep_merge(base, patch):\n    \"\"\"Leaf-override deep merge: patch overrides base at leaf keys; dict nodes merged recursively.\"\"\"\n    if isinstance(base, dict) and isinstance(patch, dict):\n        out = dict(base)\n        for k, v in patch.items():\n            if k in out:\n                out[k] = deep_merge(out[k], v)\n            else:\n                out[k] = v\n        return out\n    return patch",
    "def deep_merge(base, patch):\n    \"\"\"BROKEN - returns patch entirely, discarding base.\"\"\"\n    return patch  # BUG: discards base, loses all non-patched keys"
)
with open(f"{NEG_DIR}/ref_core_deleted.py", "w") as f: f.write(rcd)

# 4. hardcode_a -> o (correct logic but source contains A-specific literal 'VwlpRefAmpIP')
ha = ref_src.replace(
    'if __name__ == "__main__":\n    main()',
    '_PROJECT_CELL_REFERENCE = "VwlpRefAmpIP"  # dead ref: A-specific literal -> fails anti-hardcode\n\nif __name__ == "__main__":\n    main()'
)
with open(f"{NEG_DIR}/hardcode_a.py", "w") as f: f.write(ha)

# 5. drop_o_labels -> i (always returns empty o_labels)
dol = ref_src.replace(
    '    o_labels = [r for r in labels if r["text"] == "O"]',
    '    o_labels = []  # BUG: drops all O labels'
)
with open(f"{NEG_DIR}/drop_o_labels.py", "w") as f: f.write(dol)

# 6. drop_layout_only -> k (always returns empty layout_only)
dli = ref_src.replace(
    '    layout_only = sorted(r["name"] for r in lay if r["name"] not in sch_names)',
    '    layout_only = []  # BUG: drops all layout-only instances'
)
with open(f"{NEG_DIR}/drop_layout_only.py", "w") as f: f.write(dli)

# 7. wrong_axis -> m (always checks left/right axis, ignores TopBottom -> verdict FAIL on B)
wa = ref_src.replace(
    '    if str(dp_dummy.get("LeftRight")) == "1":\n        axis_ok = dist["left"] > 0 and dist["right"] > 0\n    if str(dp_dummy.get("TopBottom")) == "1":\n        axis_ok = axis_ok and dist["top"] > 0 and dist["bottom"] > 0\n    if str(cm_dummy.get("LeftRight")) == "1" and str(dp_dummy.get("LeftRight")) != "1":\n        axis_ok = dist["left"] > 0 and dist["right"] > 0',
    '    # BUG: always checks left/right, ignores TopBottom patch axis\n    axis_ok = dist["left"] > 0 and dist["right"] > 0\n    if str(cm_dummy.get("LeftRight")) == "1" and str(dp_dummy.get("LeftRight")) != "1":\n        axis_ok = dist["left"] > 0 and dist["right"] > 0'
)
with open(f"{NEG_DIR}/wrong_axis.py", "w") as f: f.write(wa)

print("negatives:", sorted(os.listdir(NEG_DIR)))
