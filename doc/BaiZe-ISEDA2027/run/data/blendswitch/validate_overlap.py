#!/usr/bin/env python3
"""
validate_overlap.py — 离线零重叠验证器（Plan F 交付物之一）

读取 S1 消费记录 + S2 生成的 index 序列，按 document id 求交，
输出 overlap_docs / total_docs，必须 = 0。

用法:
  python3 validate_overlap.py --s1-log <path> --s2-index <path> \
    --shuffle-dirs <dir1>,<dir2>,... --output result.json

输入格式:
  --s1-log:    JSON 文件，含 consumed_per_source 数组
  --s2-index:  .npy 或 JSON 文件，含 S2 的 dataset_index + dataset_sample_index
  --shuffle-dirs: 逗号分隔的目录列表，每个目录含 shuffle_index.npy
  --output:    输出 JSON 路径

输出 JSON:
{
  "overlap_docs": int,
  "total_docs": int,
  "overlap_rate": float,
  "per_source": {...},
  "pass": bool,
  "epoch_wrap_warnings": [...]
}
"""

import argparse, json, os, sys
import numpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blend_switcher import BlendSwitcher


def load_shuffle_indices(shuffle_dirs):
    """Load shuffle_index arrays from directories."""
    indices = []
    for d in shuffle_dirs:
        npy = os.path.join(d, "shuffle_index.npy")
        if os.path.exists(npy):
            indices.append(numpy.load(npy, allow_pickle=True))
        else:
            print(f"WARNING: {npy} not found, using empty")
            indices.append(numpy.array([], dtype=numpy.int64))
    return indices


def main():
    parser = argparse.ArgumentParser(description="Offline zero-overlap validator")
    parser.add_argument("--s1-log", required=True, help="S1 consumption JSON")
    parser.add_argument("--s2-index", required=True, help="S2 indices (.npy or .json)")
    parser.add_argument("--shuffle-dirs", required=True,
                        help="Comma-separated dirs with shuffle_index.npy")
    parser.add_argument("--source-keys", default="", help="Comma-separated source keys")
    parser.add_argument("--output", default="overlap_result.json", help="Output JSON path")
    args = parser.parse_args()

    # Load S1 consumption
    with open(args.s1_log) as f:
        s1_data = json.load(f)
    consumed = numpy.array(s1_data["consumed_per_source"], dtype=numpy.int64)
    num_sources = len(consumed)
    source_keys = args.source_keys.split(",") if args.source_keys else [f"src_{i}" for i in range(num_sources)]

    # Load shuffle indices
    shuffle_dirs = [d.strip() for d in args.shuffle_dirs.split(",")]
    shuffle_indices = load_shuffle_indices(shuffle_dirs)

    # Load S2 indices
    if args.s2_index.endswith(".npy"):
        s2_data = numpy.load(args.s2_index, allow_pickle=True).item()
        s2_di = s2_data["dataset_index"]
        s2_dsi = s2_data["dataset_sample_index"]
    else:
        with open(args.s2_index) as f:
            s2_data = json.load(f)
        s2_di = numpy.array(s2_data["dataset_index"], dtype=numpy.int16)
        s2_dsi = numpy.array(s2_data["dataset_sample_index"], dtype=numpy.int64)

    # Build switcher with S1 consumption
    switcher = BlendSwitcher(num_sources, source_keys)
    switcher.consumed_per_source = consumed
    switcher.total_consumed = int(consumed.sum())
    switcher.switched = True
    switcher.new_dataset_index = s2_di
    switcher.new_dataset_sample_index = s2_dsi
    switcher.new_weights = [0.0] * num_sources  # not needed for overlap
    switcher.new_size = len(s2_di)
    switcher.shared_source_mask = s1_data.get("shared_source_mask", [True] * num_sources)
    switcher.cursor_offsets = {i: int(consumed[i]) for i in range(num_sources)}

    # Compute overlap
    result = switcher.compute_overlap(shuffle_indices)

    # Output
    output = {
        "overlap_docs": result["total_overlap_docs"],
        "total_docs": result["total_s1_docs"],
        "overlap_rate": result["overlap_rate"],
        "per_source": result["per_source"],
        "pass": result["total_overlap_docs"] == 0,
        "epoch_wrap_warnings": result["epoch_wrap_warnings"],
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*60}")
    print(f"Overlap docs:  {output['overlap_docs']}")
    print(f"Total S1 docs: {output['total_docs']}")
    print(f"Overlap rate:  {output['overlap_rate']:.6f}")
    print(f"PASS (overlap=0): {output['pass']}")
    print(f"Output: {args.output}")
    print(f"{'='*60}")
    sys.exit(0 if output["pass"] else 1)


if __name__ == "__main__":
    main()
