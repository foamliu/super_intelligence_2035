#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""metadata-debt backfill · tier 1 · level -> layer normalize (r772)

背景 (r771 spec):
  B.jsonl 395 实测: 160 条用 legacy `metadata.level` 键, 143 条用标准 `metadata.layer` 键,
  92 条两者皆无。audit 工作 (r747 layer 校验法 / r764 最新 case) 已确立 `layer` 为标准键名
  (TASK §5 难度表 L1/L2/L3)。本脚本把 160 条 legacy `level` 重命名为 `layer`, 保留值与位置。

双存储 (r767 实测同步):
  1. EDA-Eval-DesignFlow_B.jsonl  (compact, ensure_ascii=False, 每行一 JSON, 末尾换行)
  2. cases/B/<task_id>.json        (indent=2, ensure_ascii=False)
  两处都改, 保持同步。

纪律:
  - 仅改 metadata 里 `level` -> `layer` (位置保留), 不动其他字段。
  - 若某 case 同时有 level 和 layer (实测 0 条), 跳过并记 manifest, 不覆盖。
  - 无 level 的 case 原样保留 (jsonl 整行 verbatim, cases/B 文件不重写)。
  - 产出 manifest: designflow/metadata_backfill_tier1_r772_manifest.tsv
"""
import json
import os
import glob

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
CASES_DIR = os.path.join(BENCH, "cases", "B")
MANIFEST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "metadata_backfill_tier1_r772_manifest.tsv",
)


def rename_key_preserve_order(d, old, new):
    """Return a new dict with `old` renamed to `new`, position preserved."""
    new_d = {}
    for k, v in d.items():
        if k == old:
            new_d[new] = v
        else:
            new_d[k] = v
    return new_d


def process_jsonl():
    rows = []
    out_lines = []
    n_renamed = 0
    n_skip_both = 0
    n_unchanged = 0
    raw = open(JSONL, encoding="utf-8").read()
    # preserve trailing newline
    ends_nl = raw.endswith("\n")
    lines = raw.splitlines()
    for line in lines:
        if not line.strip():
            out_lines.append(line)
            continue
        o = json.loads(line)
        md = o.get("metadata", {})
        has_level = "level" in md
        has_layer = "layer" in md
        if has_level and has_layer:
            n_skip_both += 1
            rows.append((o.get("task_id", ""), md.get("level"), md.get("layer"), "skip_both"))
            out_lines.append(line)  # verbatim
            continue
        if has_level and not has_layer:
            old_val = md.get("level")
            o["metadata"] = rename_key_preserve_order(md, "level", "layer")
            n_renamed += 1
            rows.append((o.get("task_id", ""), old_val, "", "renamed"))
            out_lines.append(json.dumps(o, ensure_ascii=False))
            continue
        # no level: keep verbatim to avoid any formatting drift
        n_unchanged += 1
        out_lines.append(line)
    out = "\n".join(out_lines)
    if ends_nl:
        out += "\n"
    with open(JSONL, "w", encoding="utf-8") as f:
        f.write(out)
    return n_renamed, n_skip_both, n_unchanged, rows


def process_cases():
    n_renamed = 0
    n_skip_both = 0
    n_unchanged = 0
    for path in sorted(glob.glob(os.path.join(CASES_DIR, "*.json"))):
        o = json.load(open(path, encoding="utf-8"))
        md = o.get("metadata", {})
        has_level = "level" in md
        has_layer = "layer" in md
        if has_level and has_layer:
            n_skip_both += 1
            continue
        if has_level and not has_layer:
            o["metadata"] = rename_key_preserve_order(md, "level", "layer")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(o, f, ensure_ascii=False, indent=2)
                f.write("\n")
            n_renamed += 1
            continue
        n_unchanged += 1
    return n_renamed, n_skip_both, n_unchanged


def main():
    j_renamed, j_skip, j_unch, rows = process_jsonl()
    c_renamed, c_skip, c_unch = process_cases()
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("task_id\told_level\told_layer\taction\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print(f"jsonl: renamed={j_renamed} skip_both={j_skip} unchanged={j_unch}")
    print(f"cases/B: renamed={c_renamed} skip_both={c_skip} unchanged={c_unch}")
    print(f"manifest -> {MANIFEST}")
    # post-verify
    lvl = 0
    lyr = 0
    for line in open(JSONL, encoding="utf-8").read().splitlines():
        if not line.strip():
            continue
        md = json.loads(line).get("metadata", {})
        if "level" in md:
            lvl += 1
        if "layer" in md:
            lyr += 1
    print(f"post-verify jsonl: has_level={lvl} has_layer={lyr} (expect 0 / 303)")


if __name__ == "__main__":
    main()
