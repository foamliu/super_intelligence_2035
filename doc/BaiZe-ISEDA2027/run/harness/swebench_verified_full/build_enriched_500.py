#!/usr/bin/env python3
"""Build enriched_500.json for SWE-bench Verified full-500 evaluation.

Loads two HF datasets (via proxy 172.19.92.25:13128):
  * princeton-nlp/SWE-bench_Verified  (500 instances — base data: F2P/P2P/test_patch/etc.)
  * SWE-bench/SWE-bench               (2297 instances — ALL infra fields: image/eval_script/log_parser/eval_type/version)

Joins on instance_id, overrides `image` from swebench_verified_image_list.txt
(the authoritative local mapping from the 500/500 docker pull), and writes
enriched_500.json — a local file usable as --dataset_name for the official
swebench v5.0.2 docker harness (make_test_spec needs: instance_id, image, repo,
version, FAIL_TO_PASS, PASS_TO_PASS, log_parser, eval_type, eval_script).

Also writes verified_500_ids.txt (one instance_id per line, in image_list order).
"""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
IMAGE_LIST = HARNESS_DIR / "swebench_verified_image_list.txt"
OUT_JSON = HERE / "enriched_500.json"
OUT_IDS = HERE / "verified_500_ids.txt"
PROXY = "http://172.19.92.25:13128"

# Ensure proxy is set for HF download
os.environ.setdefault("https_proxy", PROXY)
os.environ.setdefault("http_proxy", PROXY)
os.environ.setdefault("no_proxy", "127.0.0.1,localhost")

# Fields that make_test_spec requires (from swebench/harness/utils.py:251-272)
INFRA_FIELDS = ["image", "eval_script", "log_parser", "eval_type", "version"]
# Fields from Verified that we keep
VERIFIED_FIELDS = [
    "instance_id", "repo", "base_commit", "patch", "test_patch",
    "problem_statement", "hints_text", "FAIL_TO_PASS", "PASS_TO_PASS",
    "environment_setup_commit", "difficulty",
]


def log(msg: str):
    print(f"[build-enriched {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_image_list() -> dict[str, str]:
    """instance_id -> docker_image from the local 500/500 pull record."""
    mapping = {}
    for line in IMAGE_LIST.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            mapping[parts[0]] = parts[1]
    log(f"image_list: {len(mapping)} entries")
    return mapping


def main():
    from datasets import load_dataset

    image_map = load_image_list()

    # --- Load SWE-bench full (2297 instances, has ALL infra fields) ---
    log("loading SWE-bench/SWE-bench (full, 2297 instances) from HF ...")
    full_ds = load_dataset("SWE-bench/SWE-bench", split="test")
    full_lookup: dict[str, dict] = {}
    for row in full_ds:
        iid = row["instance_id"]
        full_lookup[iid] = {k: row.get(k) for k in INFRA_FIELDS}
    log(f"full dataset: {len(full_lookup)} instances with infra fields")

    # --- Load SWE-bench Verified (500 instances, base data) ---
    log("loading princeton-nlp/SWE-bench_Verified (500 instances) from HF ...")
    verified_ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    log(f"verified dataset: {len(verified_ds)} instances")

    # --- Join: for each Verified instance, merge infra fields from full ---
    enriched = []
    missing_infra = []
    image_overrides = 0
    for row in verified_ds:
        iid = row["instance_id"]
        inst = {k: row.get(k) for k in VERIFIED_FIELDS}
        # Ensure FAIL_TO_PASS / PASS_TO_PASS are lists (HF may store as strings)
        for key in ("FAIL_TO_PASS", "PASS_TO_PASS"):
            val = inst.get(key)
            if isinstance(val, str):
                try:
                    inst[key] = json.loads(val)
                except Exception:
                    inst[key] = [val]
        # Merge infra fields from full dataset
        infra = full_lookup.get(iid)
        if infra:
            for k in INFRA_FIELDS:
                inst[k] = infra[k]
        else:
            missing_infra.append(iid)
            # Fallback: derive version from instance_id (e.g. astropy__astropy-12907 -> astropy)
            inst.setdefault("version", iid.split("__")[0] if "__" in iid else "")
            inst.setdefault("eval_type", "EXECUTION")
            inst.setdefault("log_parser", "")
            inst.setdefault("eval_script", "")
        # Override image from local image_list (authoritative — matches pulled docker images)
        if iid in image_map:
            inst["image"] = image_map[iid]
            image_overrides += 1
        elif "image" not in inst or not inst["image"]:
            log(f"  WARNING: no image for {iid}")
        enriched.append(inst)

    log(f"joined: {len(enriched)} instances, {len(missing_infra)} missing infra, "
        f"{image_overrides} image overrides from image_list")
    if missing_infra:
        log(f"  missing-infra sample: {missing_infra[:5]}")

    # --- Write enriched_500.json ---
    OUT_JSON.write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
    log(f"wrote {OUT_JSON} ({OUT_JSON.stat().st_size} bytes)")

    # --- Write verified_500_ids.txt (in image_list order for reproducibility) ---
    ids_in_order = [iid for iid in image_map if any(e["instance_id"] == iid for e in enriched)]
    if len(ids_in_order) != len(enriched):
        # Fallback: use enriched order
        ids_in_order = [e["instance_id"] for e in enriched]
    OUT_IDS.write_text("\n".join(ids_in_order) + "\n")
    log(f"wrote {OUT_IDS} ({len(ids_in_order)} ids)")

    # --- Validation: check that make_test_spec can consume the first instance ---
    try:
        from swebench.harness.utils import make_test_spec
        ts = make_test_spec(enriched[0])
        log(f"make_test_spec validation OK: {enriched[0]['instance_id']} -> "
            f"eval_script_lines={len(ts.eval_script_list)}, image={ts.instance_image_key}")
    except Exception as e:
        log(f"make_test_spec validation FAILED: {e}")

    log("DONE")


if __name__ == "__main__":
    main()
