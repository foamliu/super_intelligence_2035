#!/usr/bin/env python3
"""_metadata_backfill_tier1_batch2_r860.py — 档1 batch2: 型2 描述串 layer → topic + layer 回填 L*

承 r855 refine spec: "型2 描述串移至 topic 字段 + layer 回填 L*"
承 r849 batch1 (level→layer key rename) 后续: 处理 layer 值为描述性长字符串的 case

规则:
  1. 若 layer 是描述性字符串(非 L1/L2/L3): 移至 topic 字段
     - topic 为空: topic = old_layer
     - topic 非空: topic = old_layer + " | " + old_topic (描述串作前缀 tag)
  2. layer 回填为正确 L1/L2/L3 值 (基于 case 实际难度评估)
  3. 其余字段 verbatim 不动, 保持键序

本批 5 条 (batch2):
  | case | old_layer | new_layer | reason |
  |---|---|---|---|
  | Analog-001 | netlist_connectivity_trace | L1 | offline Verilog netlist parsing |
  | DDR5CmdSeqFind-001 | schematic_netlist | L1 | offline verilog pattern file search |
  | DevUsageExtract-001 | L1-boundary | L1 | offline CDL netlist device extraction |
  | AplmmxDanglingIncDiagQA-001 | aplmmx_dangling_inc_diagnose | L1 | offline log+netlist file analysis |
  | FMFreqVsT-001 | fm_instantaneous_frequency_waveview_ace | L2 | requires WaveView ACE Tcl (real tool) |
"""
import json, os, sys
from collections import OrderedDict

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASES_D = os.path.join(BENCH, "cases", "D")

# batch2 targets: (task_id, new_layer)
BATCH = [
    ("EDA-Eval-DesignFlow-Analog-001", "L1"),
    ("EDA-Eval-DesignFlow-DDR5CmdSeqFind-001", "L1"),
    ("EDA-Eval-DesignFlow-DevUsageExtract-001", "L1"),
    ("EDA-Eval-DesignFlow-AplmmxDanglingIncDiagQA-001", "L1"),
    ("EDA-Eval-DesignFlow-FMFreqVsT-001", "L2"),
]

def normalize_case(tid, new_layer):
    fpath = os.path.join(CASES_D, tid + ".json")
    if not os.path.exists(fpath):
        return (tid, "FILE_NOT_FOUND", None)
    with open(fpath) as f:
        c = json.load(f, object_pairs_hook=OrderedDict)
    meta = c.get("metadata", OrderedDict())
    old_layer = meta.get("layer")
    old_topic = meta.get("topic", "")

    # Skip if already proper L*
    if isinstance(old_layer, str) and old_layer.strip() in ("L1", "L2", "L3"):
        return (tid, "ALREADY_L_STAR", old_layer)

    # Move old_layer to topic
    if old_topic:
        new_topic = old_layer + " | " + old_topic
    else:
        new_topic = old_layer

    # Rebuild metadata preserving key order: replace layer value, set topic
    new_meta = OrderedDict()
    for k, v in meta.items():
        if k == "layer":
            new_meta[k] = new_layer
        elif k == "topic":
            new_meta[k] = new_topic
        else:
            new_meta[k] = v
    # If topic key didn't exist, add it after layer
    if "topic" not in meta:
        # insert topic after layer
        new_meta2 = OrderedDict()
        for k, v in new_meta.items():
            new_meta2[k] = v
            if k == "layer":
                new_meta2["topic"] = new_topic
        new_meta = new_meta2

    c["metadata"] = new_meta

    # Write back
    with open(fpath, "w") as f:
        json.dump(c, f, indent=2, ensure_ascii=False)

    # Verify
    with open(fpath) as f:
        c2 = json.load(f, object_pairs_hook=OrderedDict)
    meta2 = c2.get("metadata", {})
    assert meta2.get("layer") == new_layer, f"layer mismatch: {meta2.get('layer')} != {new_layer}"
    assert old_layer in meta2.get("topic", ""), f"old_layer not in topic: {meta2.get('topic')}"
    return (tid, "OK", f"layer={old_layer}→{new_layer}, topic←{old_layer}")

def main():
    print(f"=== batch2 r860: 型2 layer→topic + layer 回填 L* ({len(BATCH)} cases) ===")
    results = []
    for tid, new_layer in BATCH:
        tid_res, status, detail = normalize_case(tid, new_layer)
        results.append((tid_res, status, detail))
        print(f"  {tid_res}: {status} ({detail})")
    ok = sum(1 for _, s, _ in results if s == "OK")
    print(f"\n{ok}/{len(BATCH)} normalized OK")
    if ok != len(BATCH):
        print("WARNING: not all cases normalized!")
        sys.exit(1)

if __name__ == "__main__":
    main()
