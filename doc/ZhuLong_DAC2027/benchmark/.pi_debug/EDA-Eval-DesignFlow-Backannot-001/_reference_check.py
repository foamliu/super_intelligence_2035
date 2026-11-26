def check(deliverable, workdir):
    """Backannot-001 deliverable checker — PrimeTime parasitics backannotation
    failure diagnosis (DRAM STA signoff).

    deliverable: path to submit.zip (relative to workdir), e.g. "outputs/submit.zip"
    workdir:     session workdir (attachments placed here at session open).

    7 independent conditions (a)-(g). All-static Python (no PrimeTime/StarRC
    run needed — this is an offline log-diagnosis task).
    TEETH: a naive report that only counts error numbers, does NO hierarchy
    comparison, does NOT split critical vs noncritical, and dumps all 9660
    into the ignore list -> FAILS (e)+(f)+(g).
    """
    import os, re, zipfile

    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    need = ["annot_diag_report.md", "hierarchy_compare.tsv",
            "noncritical_ignore_list.txt", "critical_fails.tsv"]
    with zipfile.ZipFile(p) as z:
        bmap = {}
        for n in z.namelist():
            if n.endswith("/"):
                continue
            bmap[os.path.basename(n)] = n
        missing = [b for b in need if b not in bmap]
        if missing:
            raise AssertionError("submit.zip missing: " + ", ".join(missing))
        rep_txt   = z.read(bmap["annot_diag_report.md"]).decode("utf-8", "ignore")
        cmp_txt   = z.read(bmap["hierarchy_compare.tsv"]).decode("utf-8", "ignore")
        ign_txt   = z.read(bmap["noncritical_ignore_list.txt"]).decode("utf-8", "ignore")
        crit_txt  = z.read(bmap["critical_fails.tsv"]).decode("utf-8", "ignore")

    # (a) zip contains all 4 deliverables
    assert len(missing) == 0, "(a) missing deliverables: " + str(missing)

    # (b) report mentions all three PARA error types: 043, 044, 124
    has_043 = re.search(r'PARA[- ]?043', rep_txt) is not None
    has_044 = re.search(r'PARA[- ]?044', rep_txt) is not None
    has_124 = re.search(r'PARA[- ]?124', rep_txt) is not None
    assert has_043 and has_044 and has_124, \
        "(b) report must classify by all three types (043=%s 044=%s 124=%s)" \
        % (has_043, has_044, has_124)

    # (c) report contains the backannotation summary numbers
    #     Total 1,041,009 / Not annotated 9,660 / 0.93%
    has_total   = re.search(r'1[,.]?041[,.]?009', rep_txt) is not None
    has_unannot = re.search(r'9[,.]?660', rep_txt) is not None
    has_pct     = re.search(r'0\.93\s*%', rep_txt) is not None
    assert has_total and has_unannot and has_pct, \
        "(c) report missing summary numbers (total=%s unannot=%s pct=%s)" \
        % (has_total, has_unannot, has_pct)

    # (d) report identifies root cause as cross-vendor hierarchy strategy
    #     difference (StarRC merges trivial nodes vs Cadence SI keeps full
    #     hierarchy). Must name BOTH vendors AND the merge/keep contrast.
    has_starrc   = re.search(r'StarRC', rep_txt, re.I) is not None
    has_cadence  = re.search(r'Cadence', rep_txt, re.I) is not None
    has_merge    = re.search(r'merg', rep_txt, re.I) is not None       # merge
    has_hierarchy= re.search(r'hierarchy|层级|层次', rep_txt, re.I) is not None
    assert has_starrc and has_cadence and has_merge and has_hierarchy, \
        "(d) root cause not cross-vendor hierarchy (starrc=%s cadence=%s " \
        "merge=%s hierarchy=%s)" % (has_starrc, has_cadence, has_merge, has_hierarchy)

    # (e) hierarchy_compare.tsv: header + >= 5 data rows, each row must carry
    #     BOTH a netlist hierarchy path AND a spef hierarchy path.
    #     TEETH: a naive report that only lists error counts has no compare
    #     rows -> FAIL.
    lines = [ln for ln in cmp_txt.splitlines() if ln.strip()]
    assert len(lines) >= 6, "(e) hierarchy_compare.tsv has too few rows (%d)" % len(lines)
    hdr = lines[0].lower()
    assert "netlist" in hdr and ("spef" in hdr or "parasitic" in hdr), \
        "(e) hierarchy_compare.tsv header must have netlist + spef columns: " + lines[0]
    data_rows = lines[1:]
    assert len(data_rows) >= 5, "(e) need >=5 compare rows, got %d" % len(data_rows)
    both_path_rows = 0
    for ln in data_rows:
        cols = ln.split("\t")
        # at least 4 cols (error_type, net, netlist_path, spef_path); the two
        # path columns must each contain a hierarchy separator '.' or '/'
        if len(cols) >= 4 and (re.search(r'[./]', cols[2]) and re.search(r'[./]', cols[3])):
            both_path_rows += 1
    assert both_path_rows >= 5, \
        "(e) need >=5 rows with BOTH netlist & spef hierarchy paths, got %d" \
        % both_path_rows

    # (f) noncritical_ignore_list.txt: entries must match
    #     CellName#OldNetName#NewNetName  (# separates 3 segments, 2 '#').
    #     TEETH: a flat list of net names / error ids -> FAIL.
    ign_lines = [ln for ln in ign_txt.splitlines() if ln.strip()
                 and not ln.lstrip().startswith("#") and not ln.lstrip().startswith(".IGNORE")]
    assert len(ign_lines) >= 5, "(f) ignore list has too few entries (%d)" % len(ign_lines)
    good = 0
    for ln in ign_lines:
        s = ln.strip()
        # accept an optional leading .IGNORE_NET token, then CellName#Old#New
        m = re.match(r'(?:\.IGNORE_NET\s+)?([^\s#]+)#([^\s#]+)#([^\s#]+)$', s)
        if m:
            good += 1
    assert good >= 5, "(f) need >=5 entries of CellName#Old#New, got %d" % good

    # (g) critical_fails.tsv non-empty AND distinct from noncritical ignore list.
    #     TEETH: dumping all 9660 into ignore and leaving critical empty, OR
    #     putting the same nets in both -> FAIL.
    crit_lines = [ln for ln in crit_txt.splitlines() if ln.strip()]
    assert len(crit_lines) >= 2, "(g) critical_fails.tsv empty (need header + >=1 row)"
    # collect net tokens from ignore list (the NewNetName segment)
    ign_nets = set()
    for ln in ign_lines:
        m = re.match(r'(?:\.IGNORE_NET\s+)?([^\s#]+)#([^\s#]+)#([^\s#]+)$', ln.strip())
        if m:
            ign_nets.add(m.group(2).strip('[]'))
            ign_nets.add(m.group(3).strip('[]'))
    # collect net tokens from critical_fails (any column containing 'net' or
    # the 2nd column which is typically the net)
    crit_nets = set()
    for ln in crit_lines[1:]:
        cols = ln.split("\t")
        for c in cols:
            cm = re.search(r'([A-Za-z_][\w\[\]]*)', c)
            if cm:
                crit_nets.add(cm.group(1).strip('[]'))
    overlap = ign_nets & crit_nets
    assert len(crit_nets) >= 1, "(g) critical_fails.tsv has no net tokens"
    # allow at most a tiny accidental overlap, but NOT full overlap
    assert len(overlap) < min(len(ign_nets), len(crit_nets)) or len(ign_nets) == 0, \
        "(g) critical nets fully overlap noncritical ignore list -> " \
        "did not split critical vs noncritical: overlap=%s" % str(sorted(overlap)[:8])

    return True
