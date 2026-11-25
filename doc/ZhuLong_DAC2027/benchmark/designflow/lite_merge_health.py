#!/usr/bin/env python3
"""Lite-500 health merge (coordinator = shard A).

Rebuilds designflow/lite_health_all.tsv from the 4 per-shard lite_health_<X>.tsv
files + the authoritative owner map (cases/<shard>/<case_id>.json directory).

For each Lite case_id, the LATEST row (by ts) across ALL per-shard tsvs is taken
(cross-shard entries are common: a shard may record a row for a case owned by
another shard). Owner is assigned by the cases/<shard>/ directory, NOT by which
tsv the row came from.

Also regenerates designflow/reports/lite500_health_<date>.md.

Usage:
    python3 designflow/lite_merge_health.py [--date YYYY-MM-DD] [--dry]
"""
import argparse, os, sys, datetime, glob, subprocess
from collections import defaultdict

BENCH_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
HERE = os.path.dirname(os.path.abspath(__file__))
DFLOW = HERE                       # .../benchmark/designflow
BMARK = os.path.dirname(DFLOW)     # .../benchmark
REPO_ROOT = "/nasdata/app.e0031982/code/super_intelligence_2035"
LITE_TXT = os.path.join(BENCH_DIR, "eval", "cases_lite.txt")
CASES_DIR = os.path.join(BENCH_DIR, "benchmarks", "EDA-Eval-DesignFlow", "cases")
PREFIX = "EDA-Eval-DesignFlow-"
SHARDS = ["A", "B", "C", "D"]

# status -> category bucket for the report
def bucket(st):
    if st == "green":
        return "strict_green"
    if st in ("green_verified", "green_pending_runtime"):
        return "runtime_pending"
    if st.endswith("_fixed"):
        return "fixed"
    if st.endswith("_pending"):
        return "pending"
    if st == "retired_broken":
        return "retired"
    if st == "cross_shard":
        return "cross_shard"
    return "other"


def norm(cid):
    return cid[len(PREFIX):] if cid.startswith(PREFIX) else cid


def read_lite():
    out = []
    with open(LITE_TXT) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                out.append(ln)
    return out


STATUS_RANK = {
    # higher = more verified (case is "done")
    "green": 100,
    "green_verified": 80,
    "green_pending_runtime": 70,
    "p0_fixed": 60, "p1_fixed": 60, "p2_fixed": 60, "p3_fixed": 60,
    "p0_pending": 40, "p1_pending": 40, "p2_pending": 40, "p3_pending": 40,
    "cross_shard": 20,
    "missing": 10,
}


def status_rank(st):
    return STATUS_RANK.get(st, 0)


def build_owner_map(lite_raw, latest_per_owner):
    """Map normalized case_id -> owner shard (by cases/<s>/<raw>.json).

    For non-dup cases: the single shard holding the file.
    For dup cases (file in >1 shard dir): owner = the shard whose latest tsv
    row has the BEST (most-verified) status. Rationale: Lite-fix goal is
    500/500 green; a case verified green by a shard is de-facto owned by that
    shard, and counting it as pending under another shard misrepresents the
    bottleneck. (e.g. NetlistCmp exists in B/+D/: D has green, B has
    green_verified -> D owns it, status green.)
    """
    shard_files = {}
    for s in SHARDS:
        d = os.path.join(CASES_DIR, s)
        names = set()
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".json"):
                    names.add(fn[:-5])
        shard_files[s] = names
    owner = {}
    dup_notes = []
    missing = []
    for raw in lite_raw:
        cid = norm(raw)
        holders = [s for s in SHARDS if raw in shard_files[s]]
        if not holders:
            missing.append(raw)
            owner[cid] = "?"
            continue
        if len(holders) == 1:
            owner[cid] = holders[0]
            continue
        # dup: pick shard with best-status latest row
        best_sh = None
        best_rank = -1
        best_st = ""
        for s in holders:
            r = latest_per_owner.get(cid, {}).get(s)
            st = r["status"] if r else "missing"
            rk = status_rank(st)
            if rk > best_rank:
                best_rank = rk
                best_sh = s
                best_st = st
        owner[cid] = best_sh
        dup_notes.append((raw, holders, best_sh, best_st))
    return owner, missing, dup_notes


def read_tsv(path):
    """Yield dict rows. cols: ts case_id shard L0 L1 L2 L3 L4 L5 status fix_note wall_s

    Reads from COMMITTED HEAD (git show HEAD:<relpath>) to avoid picking up
    other shards' in-flight uncommitted working-tree changes. Falls back to
    working-tree file if not under git or git show fails.
    """
    text = None
    # Try committed HEAD version
    try:
        rel = os.path.relpath(path, REPO_ROOT)
        r = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            text = r.stdout
    except Exception:
        pass
    if text is None:
        if not os.path.exists(path):
            return
        with open(path) as f:
            text = f.read()
    lines = text.split("\n")
    if not lines:
        return
    header = lines[0].split("\t")
    seq = 0
    for ln in lines[1:]:
        ln = ln.rstrip("\r")
        if not ln:
            continue
        parts = ln.split("\t")
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        row = dict(zip(header, parts))
        # _seq = monotonic append-order within this file (ground truth of "last
        # action"). Agents sometimes append a row with a ts earlier than a
        # preceding row (e.g. a green_verified back-dated after a stale
        # p0_pending); picking "latest by ts" then keeps the stale row. File
        # order is the reliable signal; ts is only a tiebreaker.
        row["_seq"] = seq
        seq += 1
        cid = row.get("case_id", "")
        if not cid or cid.startswith("L1-BATCH") or cid.startswith("P0-REVERIFY"):
            continue
        yield row


def latest_rows():
    """normalized case_id -> latest row across all per-shard tsvs.

    "Latest" = greatest (_seq, ts): within a single shard file, the last-
    appended row wins even if its ts is mis-ordered (agents back-date rows);
    across shards, ts breaks ties. Returns dict cid -> (row, src_shard). The
    caller (owner-aware merge) decides whether to use the owner's row or fall
    back.
    """
    latest = {}
    for s in SHARDS:
        for row in read_tsv(os.path.join(DFLOW, f"lite_health_{s}.tsv")):
            cid = norm(row["case_id"])
            ts = row.get("ts", "")
            seq = row.get("_seq", 0)
            if cid not in latest or (seq, ts) >= latest[cid][0]["_key"]:
                row["_key"] = (seq, ts)
                latest[cid] = (row, s)
    return latest


def owner_latest_rows(owner_map, latest):
    """For each cid, prefer the OWNER shard's latest row; fall back to global latest.

    Rationale: a cross_shard report from another shard is informational; the
    owner's own assessment (green/pending/...) is authoritative for status.
    This prevents a stale cross_shard label from another shard overriding the
    owner's resolved green (e.g. FmRtl2RtlDemo: D cross_shard@02:22 note says
    'now green' but label stuck, overriding A green@02:15).
    """
    # per-shard latest row for each cid (only from that shard's tsv)
    per_owner = {}  # cid -> {shard -> row}  (latest row each shard has for cid)
    for s in SHARDS:
        for row in read_tsv(os.path.join(DFLOW, f"lite_health_{s}.tsv")):
            cid = norm(row["case_id"])
            ts = row.get("ts", "")
            seq = row.get("_seq", 0)
            d = per_owner.setdefault(cid, {})
            # last-appended row wins (file order), ts as tiebreaker (see
            # latest_rows docstring for the back-dated-row rationale)
            if s not in d or (seq, ts) >= d[s].get("_key", (-1, "")):
                row["_key"] = (seq, ts)
                d[s] = row
    result = {}
    for cid, ow in owner_map.items():
        if ow in per_owner.get(cid, {}):
            r = per_owner[cid][ow]
            result[cid] = (r, ow)
        elif cid in latest:
            result[cid] = latest[cid]
        # else: no row at all (caller handles missing)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    lite_raw = read_lite()
    # per-shard latest row for each cid (working from committed HEAD inside read_tsv)
    per_owner = {}  # cid -> {shard -> row}
    for s in SHARDS:
        for row in read_tsv(os.path.join(DFLOW, f"lite_health_{s}.tsv")):
            cid = norm(row["case_id"])
            ts = row.get("ts", "")
            seq = row.get("_seq", 0)
            d = per_owner.setdefault(cid, {})
            # last-appended row wins (file order), ts as tiebreaker (see
            # latest_rows docstring for the back-dated-row rationale)
            if s not in d or (seq, ts) >= d[s].get("_key", (-1, "")):
                row["_key"] = (seq, ts)
                d[s] = row
    # global latest (cid -> (row, src_shard)) for fallback
    latest = {}
    for cid, sd in per_owner.items():
        best = None
        for s, r in sd.items():
            if best is None or r.get("_key", (-1, "")) >= best[0].get("_key", (-1, "")):
                best = (r, s)
        if best:
            latest[cid] = best
    owner, missing, dup_notes = build_owner_map(lite_raw, per_owner)
    own_latest = owner_latest_rows(owner, latest)

    # Build all.tsv rows
    all_rows = []
    missing_row = []
    for raw in lite_raw:
        cid = norm(raw)
        ow = owner.get(cid, "?")
        r = None
        src = "-"
        if cid in own_latest:
            r, src = own_latest[cid]
        elif cid in latest:
            r, src = latest[cid]
        if r is not None:
            all_rows.append({
                "case_id": raw,
                "owner_shard": ow,
                "status": r.get("status", "?"),
                "L0": r.get("L0", "?"),
                "L1": r.get("L1", "?"),
                "L2": r.get("L2", "?"),
                "L3": r.get("L3", "?"),
                "L4": r.get("L4", "?"),
                "L5": r.get("L5", "?"),
                "src_shard": src,
                "fix_note": r.get("fix_note", ""),
            })
        else:
            missing_row.append(raw)
            all_rows.append({
                "case_id": raw, "owner_shard": ow, "status": "missing",
                "L0": "?", "L1": "?", "L2": "?", "L3": "?", "L4": "?", "L5": "?",
                "src_shard": "-", "fix_note": "no row in any per-shard tsv",
            })

    # Write all.tsv
    cols = ["case_id", "owner_shard", "status", "L0", "L1", "L2", "L3", "L4", "L5", "src_shard", "fix_note"]
    out_tsv = os.path.join(DFLOW, "lite_health_all.tsv")
    lines = ["\t".join(cols)]
    for r in all_rows:
        lines.append("\t".join(str(r.get(c, "")) for c in cols))
    tsv_text = "\n".join(lines) + "\n"

    # Stats
    total = len(all_rows)
    by_owner_status = defaultdict(lambda: defaultdict(int))
    by_bucket = defaultdict(int)
    by_owner_bucket = defaultdict(lambda: defaultdict(int))
    for r in all_rows:
        ow = r["owner_shard"]; st = r["status"]; b = bucket(st)
        by_owner_status[ow][st] += 1
        by_bucket[b] += 1
        by_owner_bucket[ow][b] += 1

    # Report markdown
    rep_lines = []
    rep_lines.append(f"# Lite-500 Health Report — {args.date}")
    rep_lines.append("")
    rep_lines.append(f"- **Total Lite cases**: {total}")
    rep_lines.append(f"- **Owner missing** (not in any cases/<shard>/): {len(missing)}")
    rep_lines.append(f"- **No health row** (missing from all per-shard tsvs): {len(missing_row)}")
    rep_lines.append("")
    rep_lines.append("## Overall buckets")
    rep_lines.append("")
    rep_lines.append("| bucket | count |")
    rep_lines.append("|:--|--:|")
    for b in ["strict_green", "runtime_pending", "fixed", "pending", "retired", "cross_shard", "other"]:
        rep_lines.append(f"| {b} | {by_bucket[b]} |")
    rep_lines.append(f"| **TOTAL** | **{total}** |")
    rep_lines.append("")
    rep_lines.append("## Per-shard x status")
    rep_lines.append("")
    rep_lines.append("| owner | status | count |")
    rep_lines.append("|:--|:--|--:|")
    for ow in SHARDS:
        for st in sorted(by_owner_status[ow]):
            rep_lines.append(f"| {ow} | {st} | {by_owner_status[ow][st]} |")
    rep_lines.append("")
    rep_lines.append("## Per-shard buckets")
    rep_lines.append("")
    rep_lines.append("| owner | strict_green | runtime_pending | fixed | pending | retired |")
    rep_lines.append("|:--|--:|--:|--:|--:|--:|")
    for ow in SHARDS:
        bb = by_owner_bucket[ow]
        rep_lines.append(f"| {ow} | {bb['strict_green']} | {bb['runtime_pending']} | {bb['fixed']} | {bb['pending']} | {bb['retired']} |")
    rep_lines.append("")
    # dup-owner resolution log
    if dup_notes:
        rep_lines.append("## Dup-owner cases (file in >1 shard dir) — resolved by best-status rule")
        rep_lines.append("")
        rep_lines.append("| case_id | holders | resolved_owner | status |")
        rep_lines.append("|:--|:--|:--|:--|")
        for raw, holders, ow, st in dup_notes:
            rep_lines.append(f"| {raw} | {','.join(holders)} | {ow} | {st} |")
        rep_lines.append("")
    # bottleneck list
    rep_lines.append("## Non-green cases (pending/fixed/retired/other) — fix backlog")
    rep_lines.append("")
    rep_lines.append("| case_id | owner | status | src | fix_note |")
    rep_lines.append("|:--|:--|:--|:--|:--|")
    for r in all_rows:
        if bucket(r["status"]) not in ("strict_green",):
            note = r["fix_note"][:120].replace("|", "\\|")
            rep_lines.append(f"| {r['case_id']} | {r['owner_shard']} | {r['status']} | {r['src_shard']} | {note} |")
    rep_lines.append("")
    rep_text = "\n".join(rep_lines) + "\n"

    # Print summary to stdout
    print(f"=== Lite-500 merge ({args.date}) ===")
    print(f"total={total}  owner_missing={len(missing)}  no_row={len(missing_row)}")
    print("buckets:", dict(by_bucket))
    print("per-owner x status:")
    for ow in SHARDS:
        print(f"  {ow}: {dict(by_owner_status[ow])}")
    if missing:
        print("OWNER MISSING:", missing[:10])
    if missing_row:
        print("NO ROW:", missing_row[:10])
    if dup_notes:
        print(f"\ndup-owner cases resolved ({len(dup_notes)}):")
        for raw, holders, ow, st in dup_notes:
            print(f"  {raw}: holders={holders} -> owner={ow} (status={st})")

    if args.dry:
        print("\n(--dry: not writing)")
        return

    with open(out_tsv, "w") as f:
        f.write(tsv_text)
    print(f"wrote {out_tsv} ({len(all_rows)} rows)")

    rep_dir = os.path.join(DFLOW, "reports")
    os.makedirs(rep_dir, exist_ok=True)
    rep_path = os.path.join(rep_dir, f"lite500_health_{args.date}.md")
    with open(rep_path, "w") as f:
        f.write(rep_text)
    print(f"wrote {rep_path}")


if __name__ == "__main__":
    main()
