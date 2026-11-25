#!/usr/bin/env python3
"""Convert SWE-bench Multimodal test.parquet → per-instance JSON + swebench dataset JSON.

Output:
  instances/<instance_id>.json  — per-instance JSON for the predict phase
  mm_test.json                  — swebench-readable list (for run_evaluation --dataset_name)

Each per-instance JSON preserves ALL parquet fields (including image_assets with
image URLs) so the predict runner can download and embed images.

Usage:
  python3 mm_parquet_to_json.py [--parquet test.parquet] [--out-dir .]
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path

import pandas as pd


def parquet_row_to_dict(row) -> dict:
    """Convert a pandas Series (parquet row) to a JSON-serialisable dict.

    Handles numpy arrays (image_assets fields) by converting to lists.
    """
    out = {}
    for k in row.index:
        v = row[k]
        if isinstance(v, dict):
            # image_assets: convert numpy arrays to lists
            out[k] = {ik: (iv.tolist() if hasattr(iv, "tolist") else iv)
                       for ik, iv in v.items()}
        elif hasattr(v, "tolist"):
            out[k] = v.tolist()
        else:
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser(description="Convert MM parquet → instance JSONs")
    ap.add_argument("--parquet", default=str(Path(__file__).parent / "test.parquet"))
    ap.add_argument("--out-dir", default=str(Path(__file__).parent))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    inst_dir = out_dir / "instances"
    inst_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(args.parquet)
    print(f"[mm_parquet] loaded {len(df)} rows from {args.parquet}")

    all_instances = []
    n_with_img = 0
    n_total_img = 0

    for i in range(len(df)):
        row = df.iloc[i]
        inst = parquet_row_to_dict(row)
        iid = inst["instance_id"]

        # Write per-instance JSON (includes image_assets for predict phase)
        (inst_dir / f"{iid}.json").write_text(
            json.dumps(inst, ensure_ascii=False, indent=2))

        # Count images
        ia = inst.get("image_assets", {})
        ps_imgs = ia.get("problem_statement", [])
        if ps_imgs:
            n_with_img += 1
            n_total_img += len(ps_imgs)

        # For swebench dataset JSON, keep all fields (swebench reads what it needs)
        all_instances.append(inst)

    # Write swebench-readable dataset JSON
    dataset_path = out_dir / "mm_test.json"
    dataset_path.write_text(json.dumps(all_instances, ensure_ascii=False))
    print(f"[mm_parquet] wrote {len(all_instances)} instances → {dataset_path}")
    print(f"[mm_parquet] wrote per-instance JSONs → {inst_dir}/")
    print(f"[mm_parquet] rows with problem_statement images: {n_with_img}/{len(df)}")
    print(f"[mm_parquet] total problem_statement images: {n_total_img} "
          f"(avg {n_total_img / max(n_with_img, 1):.1f} per row with images)")

    # Write instance ID list (for convenience)
    ids_path = out_dir / "mm_test_ids.txt"
    ids_path.write_text("\n".join(inst["instance_id"]
                                   for inst in all_instances) + "\n")
    print(f"[mm_parquet] wrote ID list → {ids_path}")


if __name__ == "__main__":
    main()
