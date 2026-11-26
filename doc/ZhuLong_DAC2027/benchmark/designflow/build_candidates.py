#!/usr/bin/env python3
"""build_candidates.py — 2026-11-12 用户令（换池 1105→1109, shard B 执行）步骤 5.

重建分类候选清单 candidates_mc10_classified.tsv：
  - 读 summary_1109.tsv（slug 已去重, 取最大 mc）
  - 四 shard keyword 分类（SHARD_DOMAINS 正则, 取命中数最多的 shard 为 domain；
    多个命中并列时按 A<B<C<D 顺序取首个，并标注 multi）
  - 4-shard ledger 排除（只保留未动过 = fresh）
  - mc>=10
  - 输出 schema: slug, match_count, domain, user, host  （即 任务书要求的 slug/mc/domain/user/host）

与 candidates_mc10.tsv 的关系：
  candidates_mc10.tsv = mc-matrix --emit-candidates 产出（ip user session_file match_count
    keywords, 含 touched, mcguard G4 兼容 p[3]=match_count），是各 shard `next` 选料的主清单。
  candidates_mc10_classified.tsv = 本脚本产出（slug mc domain user host, 仅 fresh, 带 domain
    分类），是换池交付的分类快照，便于人读与域分布统计，不进 mcguard。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# 2026-11-13: src 可由 argv[1] 指定（换池 1109->1113 后默认改 1113）；不传则回退 1109。
SRC = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "summary_1109.tsv")
OUT = os.path.join(HERE, "candidates_mc10_classified.tsv")
MIN_MC = 10

SHARD_DOMAINS = {
    "A": ("digital|verification|pnr_signoff|eda_other",
          "verdi|vcs|dc_shell|verilint|formality|innovus|primetime|design_compiler|rc|pt_shell"
          "|synthesis|synopsys|tcl|verilog|systemverilog|rtl|sdc|vivado|yosys|openroad"),
    "B": ("spice_sim|characterization",
          "hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim"),
    "C": ("physical_verify|layout_virtuoso|layout_aether|pg_layout",
          "calibre|virtuoso|aether|ipcustom|layout|lvs|drc|pexivirtuoso"),
    "D": ("schematic_netlist|waveform|analog_context",
          "waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic"),
}
SHARD_RE = {s: re.compile(p[1]) for s, p in SHARD_DOMAINS.items()}


def norm_sid(s):
    b = s.replace("\\", "/").rstrip("/").split("/")[-1]
    for suf in (".messages.archive.json", ".messages.archive", ".messages.json",
                ".archive.json", ".json"):
        if b.endswith(suf):
            return b[:-len(suf)]
    return b


def classify(kw):
    """返回 (domain, hits_dict). domain = 全部命中的 shard 并集（A<B<C<D 排序，
    用 "+" 连接）。与 mc-matrix 的 boolean membership 口径一致：一个 session 可同时
    归属多个 shard（如 "A+C"）。无任何命中返回 "?"。"""
    hits = {}
    for s in ("A", "B", "C", "D"):
        hits[s] = len(SHARD_RE[s].findall(kw or ""))
    matched = [s for s in ("A", "B", "C", "D") if hits[s] > 0]
    if not matched:
        return "?", hits
    return "+".join(matched), hits


def load_touched():
    """4 shard ledger + 老合并台账 → set of normalized sid (已动过).

    台账 schema (trace_ledger.py COLS): session_file user host match_count
    domain status case_id timestamp note  → session_file 在第 0 列。
    """
    touched = set()
    for s in ("A", "B", "C", "D"):
        p = os.path.join(HERE, "trace_ledger_%s.tsv" % s)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                p2 = line.rstrip("\n").split("\t")
                if p2 and p2[0] and p2[0] != "session_file":
                    touched.add(norm_sid(p2[0]))
    old = os.path.join(HERE, "trace_ledger.tsv")
    if os.path.exists(old):
        with open(old, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                p2 = line.rstrip("\n").split("\t")
                if p2 and p2[0] and p2[0] != "session_file":
                    touched.add(norm_sid(p2[0]))
    return touched


def main():
    if not os.path.exists(SRC):
        print("ERROR: %s 不存在" % SRC, file=sys.stderr)
        return 2
    touched = load_touched()
    # summary_1109.tsv 已 slug 去重, 这里再 dedup 防御
    best = {}
    with open(SRC, encoding="utf-8") as f:
        f.readline()
        for line in f:
            if not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            try:
                mc = int(float(p[4]))
            except (TypeError, ValueError):
                continue
            sid = norm_sid(p[3])
            if sid not in best or mc > best[sid]["mc"]:
                best[sid] = {"mc": mc, "user": p[2], "host": p[1], "kw": p[5]}
    rows = []
    n_fresh = 0
    n_touched = 0
    for sid, v in best.items():
        if v["mc"] < MIN_MC:
            continue
        if sid in touched:
            n_touched += 1
            continue
        n_fresh += 1
        dom, _ = classify(v["kw"])
        rows.append((sid, v["mc"], dom, v["user"], v["host"]))
    rows.sort(key=lambda r: -r[1])
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("slug\tmatch_count\tdomain\tuser\thost\n")
        for r in rows:
            f.write("%s\t%d\t%s\t%s\t%s\n" % r)
    # 域分布（boolean membership：一个 session 可计入多个 shard，与 mc-matrix 一致）
    from collections import Counter
    dom_cnt = Counter()
    for r in rows:
        for d in r[2].split("+"):
            if d != "?":
                dom_cnt[d] += 1
        if r[2] == "?":
            dom_cnt["?"] += 1
    print("wrote %s" % OUT)
    print("fresh mc>=%d rows = %d  (excluded touched = %d)" % (MIN_MC, n_fresh, n_touched))
    print("domain distribution (fresh, boolean membership): %s" % dict(sorted(dom_cnt.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
