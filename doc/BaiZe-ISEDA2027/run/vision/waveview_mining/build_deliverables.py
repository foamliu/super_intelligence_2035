#!/usr/bin/env python3
import json, os
from collections import Counter

RUN = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
RAW = RUN + "/vision/waveview_mining/waveview_mined_raw.json"
IDX = RUN + "/vision/real_waveview_index.json"
DF = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/waveview_real_cases.jsonl"
OUT_JSONL = RUN + "/vision/waveview_cases_mined.jsonl"
OUT_HTML = RUN + "/reports/report_vision_waveview_mining_zh.html"

raw = json.load(open(RAW))
cands = raw["candidates"]
idx = json.load(open(IDX))
idx_by_id = {c["case_id"]: c for c in idx["cases"]}
df = [json.loads(l) for l in open(DF) if l.strip()]
df_by_id = {r["case_id"]: r for r in df}

# ---- three-way reconciliation by case_id (+ sha256 where available) ----
idx_ids = set(idx_by_id)
df_ids = set(df_by_id)
mined_runnable = [c for c in cands if not c["image_missing"] and c["vision_run_type"] == "A"]
mined_run_ids = set(c["case_id"] for c in mined_runnable)
# sha256 cross-check between mined and idx
sha_match = 0
for c in mined_runnable:
    ic = idx_by_id.get(c["case_id"])
    if ic and c["sha256_check"] and c["sha256_check"] == ic["check_py"]["sha256"]:
        sha_match += 1
three_way = idx_ids & df_ids & mined_run_ids
only_mined = mined_run_ids - idx_ids - df_ids
missing_in_mined = (idx_ids | df_ids) - mined_run_ids

# ---- build mined jsonl (designflow口径 + extras) ----
lines = []
for c in cands:
    dfc = df_by_id.get(c["case_id"])
    ic = idx_by_id.get(c["case_id"])
    rec = {
        "case_id": c["case_id"],
        "case_name": (dfc or {}).get("case_name", c["task_name"]),
        "source_shard": c["source_pool"],
        "source_pool": c["source_pool"],
        "pool_line": c["pool_line"],
        "shard_jsonl": c["shard_jsonl"],
        "domain": c["domain"],
        "requires_image": (dfc or {}).get("requires_image", not c["image_missing"]),
        "image_paths": c["image_paths"],
        "image_sha256": [im["sha256"] for im in c["image_inventory"]],
        "image_kind": (dfc or {}).get("image_kind", ""),
        "image_count": c["image_count"],
        "image_missing": c["image_missing"],
        "check_path": "reference/%s/check.py" % c["case_id"],
        "check_path_3615": c["check_path_3615"],
        "check_exists": c["check_exists"],
        "sha256_check": c["sha256_check"],
        "k_conditions": c["k_conditions"],
        "baseline_pass": (dfc or {}).get("baseline_pass", None),
        "baseline_source": (dfc or {}).get("baseline_source", ""),
        "failure_mode_tier": (dfc or {}).get("failure_mode_tier", ""),
        "asset_fidelity": (dfc or {}).get("asset_fidelity", c["asset_fidelity"]),
        "vision_run_type": c["vision_run_type"],
        "vab_reason": c["vab_reason"],
        "keyword_hits": c["keyword_hits"],
        "restoration_notes": c["restoration_notes"],
        "expected_artifacts": c["expected_artifacts"],
        "grade": (dfc or {}).get("grade", ""),
        "notes": (dfc or {}).get("notes", ""),
    }
    lines.append(rec)
with open(OUT_JSONL, "w") as f:
    for r in lines:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ---- funnel stats ----
stats = raw["stats"]
total = stats["total"]
wave = len(cands)
judgeable = sum(1 for c in cands if c["check_exists"])
with_img = sum(1 for c in cands if not c["image_missing"])
runnable = len(mined_runnable)
rt_all = Counter(c["vision_run_type"] for c in cands)
rt_img = Counter(c["vision_run_type"] for c in cands if not c["image_missing"])
print("funnel: total=%d wave=%d judgeable=%d with_img=%d runnable=%d" % (total, wave, judgeable, with_img, runnable))
print("run_type_all=", dict(rt_all), "run_type_img=", dict(rt_img))
print("three-way: intersect=%d only_mined=%d missing_in_mined=%d sha_match=%d" % (len(three_way), len(only_mined), len(missing_in_mined), sha_match))
print("jsonl lines=", len(lines))
