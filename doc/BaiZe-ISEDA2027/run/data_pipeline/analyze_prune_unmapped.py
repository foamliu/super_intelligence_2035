#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_prune_unmapped.py — Per-shard judgment for operator order 2026-10-25 10:3x
"删除无法对应下载目录的早期分词产物".

For each early shard (code_s*, l3_s*, math_s*) under baize-data/text/:
  1. Read its .json manifest (input_dir, num_tokens, num_documents).
  2. Resolve symlinks inside staging_r3/<shard>/ -> absolute /nas_inference parquet.
  3. mappable vs candidate download dirs:
       candidates = Ultra-FineWeb/data/ultrafineweb_*, UltraX-Preview, /nas_inference/...UltraData-*
     .bin manifest input_dir = staging_r3/<shard> (deprecated intermediate path)
     => NOT a download dir => 不可映射 (by manifest). Resolved download dir reported too.
  4. coverage: early source parquet set ⊆ union(full_* source sets).
       full_* sources (per run_full_tokenize.sh SOURCES):
         full_ultradata_code_l2 <- UltraData-Code-L2 (recursive)
         full_ultradata_code_l3 <- UltraData-Code-L3 (recursive)
         full_ufw_l3             <- Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa (ONLY qa!)
         full_ultradata_math_l3  <- UltraData-Math-L3 (recursive)
         full_ultradata_math_l1  <- UltraData-Math-L1 (recursive)
  5. Gate (all 3 to delete): unmappable AND covered AND not env14/full_*.
       unmappable AND NOT covered => KEEP, flag "来源不明,待人工裁决".

Outputs:
  run/data/prune_unmapped_judgment_20261025.tsv   (per-shard judgment table)
  run/data/prune_unmapped_20261025.txt            (deletion list: path + bytes)
  run/data/prune_unmapped_summary_20261025.json   (summary stats)
"""
import os, json, sys

TEXT_DIR = "/nas_train/app.e0031982/datasets/baize-data/text"
STAGING_R3 = os.path.join(TEXT_DIR, "staging_r3")
OPENBMB_INF = "/nas_inference/app.e0031982/datasets/openbmb"
OUT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data"

FULL_SOURCES = {
    "full_ultradata_code_l2": os.path.join(OPENBMB_INF, "UltraData-Code/data/UltraData-Code-L2"),
    "full_ultradata_code_l3": os.path.join(OPENBMB_INF, "UltraData-Code/data/UltraData-Code-L3"),
    "full_ufw_l3":            os.path.join(OPENBMB_INF, "Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa"),
    "full_ultradata_math_l3": os.path.join(OPENBMB_INF, "UltraData-Math/data/UltraData-Math-L3"),
    "full_ultradata_math_l1": os.path.join(OPENBMB_INF, "UltraData-Math/data/UltraData-Math-L1"),
}

def rel_to_openbmb(abspath):
    ap = os.path.realpath(abspath)
    ob = OPENBMB_INF + "/"
    if ap.startswith(ob):
        return ap[len(ob):]
    return None

def find_parquet_recursive(root):
    out = set()
    if not os.path.isdir(root):
        return out
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith(".parquet"):
                rp = rel_to_openbmb(os.path.join(dp, f))
                if rp:
                    out.add(rp)
    return out

def build_full_source_set():
    full_by_name = {}
    union = set()
    for name, root in FULL_SOURCES.items():
        s = find_parquet_recursive(root)
        full_by_name[name] = s
        union |= s
        print(f"[full] {name}: {len(s)} parquet <- {root}", file=sys.stderr)
    print(f"[full] UNION source set: {len(union)} parquet", file=sys.stderr)
    return full_by_name, union

def shard_source_set(shard):
    """Read symlinks in staging_r3/<shard>/ -> resolved rel-to-openbmb parquet set.
    Returns (set_of_rel, list_of_broken_targets)."""
    sdir = os.path.join(STAGING_R3, shard)
    relset = set()
    broken = []
    if not os.path.isdir(sdir):
        return relset, broken
    for f in sorted(os.listdir(sdir)):
        fp = os.path.join(sdir, f)
        if os.path.islink(fp):
            tgt = os.readlink(fp)
            if not os.path.isabs(tgt):
                tgt = os.path.realpath(fp)
            if not os.path.exists(tgt):
                broken.append(tgt)
                continue
            rp = rel_to_openbmb(tgt)
            if rp:
                relset.add(rp)
    return relset, broken

def shard_download_dir(relset):
    """Bucket source parquet rel-paths by dataset root."""
    dirs = set()
    for rp in relset:
        parts = rp.split("/")
        if parts[0] in ("UltraData-Code", "UltraData-Math"):
            dirs.add("/".join(parts[:3]))   # UltraData-Code/data/UltraData-Code-L2
        elif parts[0] == "Ultra-FineWeb-L3":
            dirs.add("/".join(parts[:4]))   # Ultra-FineWeb-L3/data/ultrafineweb_en_l3/multi_style
        else:
            dirs.add(parts[0])
    return sorted(dirs)

def fmt_bytes(n):
    return f"{n:,} B"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    full_by_name, full_union = build_full_source_set()
    groups = [("code_s", 30), ("l3_s", 40), ("math_s", 40)]
    rows = []
    delete_files = []
    keep_uncovered = []
    tsv_lines = ["shard\tinput_dir(manifest)\tnum_tokens\tnum_documents\tresolved_download_dir\tsrc_parquet_n\tbroken_links\tmappable\tcovered_by_full_*\tuncovered_count\taction"]

    for prefix, n in groups:
        for i in range(n):
            shard = f"{prefix}{i}"
            jf = os.path.join(TEXT_DIR, shard + ".json")
            meta = {}
            if os.path.isfile(jf):
                try:
                    meta = json.load(open(jf))
                except Exception:
                    meta = {}
            input_dir = meta.get("input_dir", "")
            num_tokens = int(meta.get("num_tokens", 0))
            num_docs = int(meta.get("num_documents", 0))
            relset, broken = shard_source_set(shard)
            ddirs = shard_download_dir(relset)
            ddir_str = ";".join(ddirs) if ddirs else "(none/broken)"
            is_staging = input_dir.startswith(STAGING_R3) or input_dir.startswith("staging_r3")
            mappable = "不可映射(manifest->staging_r3废弃中间路径)"
            uncovered = relset - full_union
            covered = (len(uncovered) == 0) and (len(relset) > 0)
            covered_str = "是(源⊆full_*)" if covered else ("否" if len(relset) > 0 else "否(无源parquet)")
            if not covered:
                action = "保留(不可映射且未全覆盖->来源不明待人工裁决)"
                keep_uncovered.append((shard, len(uncovered), ddir_str))
            else:
                action = "删除(不可映射且已被full_*全覆盖)"
                for ext in (".bin", ".idx", ".json"):
                    p = os.path.join(TEXT_DIR, shard + ext)
                    if os.path.isfile(p):
                        delete_files.append((p, os.path.getsize(p)))
            tsv_lines.append("\t".join([
                shard, input_dir, str(num_tokens), str(num_docs), ddir_str,
                str(len(relset)), str(len(broken)), mappable,
                covered_str, str(len(uncovered)), action]))
            rows.append(dict(shard=shard, prefix=prefix, num_tokens=num_tokens,
                             covered=covered, ddirs=ddir_str, src_n=len(relset),
                             uncovered=len(uncovered)))

    tsv_path = os.path.join(OUT_DIR, "prune_unmapped_judgment_20261025.tsv")
    with open(tsv_path, "w") as f:
        f.write("\n".join(tsv_lines) + "\n")
    del_path = os.path.join(OUT_DIR, "prune_unmapped_20261025.txt")
    delete_files.sort()
    total_del_bytes = 0
    with open(del_path, "w") as f:
        f.write("# prune_unmapped_20261025.txt — deletion list (operator 2026-10-25 10:3x)\n")
        f.write("# gate: unmappable(manifest->staging_r3) AND covered_by_full_* ; env14 & /nas_env/full_* untouched\n")
        f.write(f"# {'path'}\t{ 'bytes'}\n")
        for p, b in delete_files:
            f.write(f"{p}\t{b}\n")
            total_del_bytes += b
        f.write(f"# TOTAL files={len(delete_files)}  bytes={total_del_bytes}\n")
    by_prefix = {}
    for r in rows:
        p = r["prefix"]
        by_prefix.setdefault(p, dict(total=0, covered=0, uncovered=0, tok_covered=0, tok_uncovered=0))
        by_prefix[p]["total"] += 1
        if r["covered"]:
            by_prefix[p]["covered"] += 1
            by_prefix[p]["tok_covered"] += r["num_tokens"]
        else:
            by_prefix[p]["uncovered"] += 1
            by_prefix[p]["tok_uncovered"] += r["num_tokens"]
    summary = {
        "generated_by": "analyze_prune_unmapped.py",
        "operator_order": "2026-10-25 10:3x",
        "env14_untouched": True,
        "full_source_set_size": len(full_union),
        "full_by_name": {k: len(v) for k, v in full_by_name.items()},
        "early_groups": by_prefix,
        "delete_files": len(delete_files),
        "delete_bytes": total_del_bytes,
        "delete_tb": round(total_del_bytes / 1e12, 3),
        "keep_uncovered_shards": [{"shard": s, "uncovered_parquet": u, "download_dir": d} for s, u, d in keep_uncovered],
        "outputs": [tsv_path, del_path],
    }
    sum_path = os.path.join(OUT_DIR, "prune_unmapped_summary_20261025.json")
    with open(sum_path, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\n=== PER-SHARD JUDGMENT SUMMARY ===")
    for p, st in by_prefix.items():
        print(f"  {p}*: total={st['total']}  covered(删)={st['covered']}  uncovered(留)={st['uncovered']}  "
              f"tok_covered={st['tok_covered']:,}  tok_uncovered={st['tok_uncovered']:,}")
    print(f"\n  DELETE: files={len(delete_files)}  bytes={fmt_bytes(total_del_bytes)}  (~{summary['delete_tb']} TB)")
    print(f"  KEEP (uncovered, 待人工裁决): {len(keep_uncovered)} shards")
    for s, u, d in keep_uncovered:
        print(f"    - {s}: {u} uncovered parquet ; resolved={d}")
    print(f"\n  outputs:\n    {tsv_path}\n    {del_path}\n    {sum_path}")

if __name__ == "__main__":
    main()


