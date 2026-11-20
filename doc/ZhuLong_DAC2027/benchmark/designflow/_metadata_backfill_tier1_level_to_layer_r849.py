#!/usr/bin/env python3
"""档1 level→layer normalize — r849 batch1 (5 cases).

承 B r772 档1 spec + D r848 全量转 normal-apply 声明。
对 cases/D/*.json 中 metadata.level 存在且 metadata.layer 不存在的 case，
将键名 level 改为 layer（保留键序位置与值），其余字段 verbatim 不动。
both-skip：level+layer 同时存在的 case 本批不处理（需单独判定）。

用法：
    python3 _metadata_backfill_tier1_level_to_layer_r849.py           # 默认前 5 条
    python3 _metadata_backfill_tier1_level_to_layer_r849.py --all     # 全量 147 条
"""
import json, os, argparse, sys
from collections import OrderedDict

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASES_D = os.path.join(BENCH, "cases", "D")

BATCH_N = 5


def rename_level_to_layer(meta):
    """重建 metadata OrderedDict，把 'level' 键名改为 'layer'，保留位置与值。
    返回 (new_meta, changed)。若 level 不存在或 layer 已存在，原样返回 changed=False。"""
    if "level" not in meta or "layer" in meta:
        return meta, False
    new = OrderedDict()
    for k, v in meta.items():
        if k == "level":
            new["layer"] = v
        else:
            new[k] = v
    return new, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="处理全部 147 条（默认前 5）")
    args = ap.parse_args()

    # 收集 level-only 候选，按文件名排序
    candidates = []
    for fname in sorted(os.listdir(CASES_D)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(CASES_D, fname)
        with open(fpath) as f:
            d = json.load(f)
        md = d.get("metadata", {})
        if "level" in md and "layer" not in md:
            candidates.append((fname, fpath, d))

    target = candidates if args.all else candidates[:BATCH_N]
    print(f"level-only 候选总数: {len(candidates)}")
    print(f"本批处理: {len(target)} 条 ({'all' if args.all else 'first %d' % BATCH_N})")
    print("=" * 70)

    changed = 0
    for fname, fpath, d in target:
        md = d.get("metadata", {})
        old_val = md.get("level")
        new_md, ok = rename_level_to_layer(md)
        if not ok:
            print(f"SKIP  {fname} (both 或无 level)")
            continue
        d["metadata"] = new_md
        with open(fpath, "w") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        changed += 1
        # 验证：重读确认
        with open(fpath) as f:
            chk = json.load(f)
        chk_md = chk.get("metadata", {})
        assert "level" not in chk_md, f"{fname}: level 仍存在!"
        assert chk_md.get("layer") == old_val, f"{fname}: layer 值不对!"
        # 确认键序位置保持
        old_keys = list(md.keys())
        new_keys = list(chk_md.keys())
        old_pos = old_keys.index("level")
        new_pos = new_keys.index("layer")
        assert new_pos == old_pos, f"{fname}: 键序位置变了 {old_pos}->{new_pos}"
        # 其余键不变
        assert new_keys[:old_pos] == old_keys[:old_pos], f"{fname}: 前段键序变"
        assert new_keys[old_pos + 1:] == old_keys[old_pos + 1:], f"{fname}: 后段键序变"
        print(f"OK    {fname}: level={old_val} -> layer={old_val} (pos={old_pos})")

    print("=" * 70)
    print(f"完成: {changed} 条 level->layer normalize")


if __name__ == "__main__":
    main()
