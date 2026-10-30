def check(deliverable, workdir):
    """LayoutVirtuoso-001 deliverable checker — offline-Python RTEXT/RNODE
    label audit + cleanup advisor (layout_virtuoso domain).

    deliverable: path to submit.zip (relative to workdir), e.g. "outputs/submit.zip"
    workdir:     session workdir (attachments placed here at session open).

    7 independent conditions (a)-(g). All-static Python (no EDA tool run
    needed — this is an offline label-inventory audit task). The checker RUNS
    the candidate's own rtext_rnode_audit.py on the two attachments (unclean
    + clean inventories) to verify it actually does per-net audit + garbage
    detection + dedup and is not a naive total-counter or always-ALIGNED stub.

    TEETH:
      - naive total-counter (only counts RTEXT/RNODE totals, no per-net) ->
        FAIL (c) (cannot name garbage nets test2/edit_test)
      - naive always-ALIGNED tool -> FAIL (c) (unclean must be MISALIGNED)
      - tool that ignores the RNODE==0 rule -> garbage mis-reported ALIGNED ->
        FAIL (e)
      - tool that does not dedup by (layer,purpose,net,xy) -> dup count wrong
        -> FAIL (d)
      - tool that counts drawing-purpose labels as RTEXT/RNODE -> counts off
        -> FAIL (c)/(d)
      - tool that does not enumerate per-net in cleanup_report -> FAIL (g)
    """
    import os, re, subprocess, zipfile

    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    need = ["rtext_rnode_audit.py", "sample_output_unclean.txt",
            "sample_output_clean.txt", "cleanup_report.txt"]
    with zipfile.ZipFile(p) as z:
        bmap = {}
        for n in z.namelist():
            if n.endswith("/"):
                continue
            bmap[os.path.basename(n)] = n
        missing = [b for b in need if b not in bmap]
        assert not missing, "(a) submit.zip missing: " + ", ".join(missing)

        tool_src = z.read(bmap["rtext_rnode_audit.py"]).decode("utf-8", "ignore")
        sample_unclean = z.read(bmap["sample_output_unclean.txt"]).decode("utf-8", "ignore")
        sample_clean = z.read(bmap["sample_output_clean.txt"]).decode("utf-8", "ignore")
        report_txt = z.read(bmap["cleanup_report.txt"]).decode("utf-8", "ignore")

    # (a) zip contains all 4 deliverables
    assert len(missing) == 0, "(a) missing deliverables: " + str(missing)

    # locate the inventory attachments inside workdir
    def find(name):
        for cand in (name, "assets/" + name):
            cp = os.path.join(workdir, cand)
            if os.path.isfile(cp):
                return cp
        for root, _, files in os.walk(workdir):
            if name in files:
                return os.path.join(root, name)
        return None

    inv_unclean = find("label_inventory_unclean.txt")
    inv_clean = find("label_inventory_clean.txt")
    assert inv_unclean is not None, "(setup) label_inventory_unclean.txt attachment not found"
    assert inv_clean is not None, "(setup) label_inventory_clean.txt attachment not found"

    # (b) rtext_rnode_audit.py is syntactically valid Python (compiles)
    import py_compile
    tmp_py = os.path.join(workdir, "_candidate_rtext_rnode_audit.py")
    with open(tmp_py, "w") as f:
        f.write(tool_src)
    try:
        py_compile.compile(tmp_py, doraise=True)
    except py_compile.PyCompileError as e:
        raise AssertionError("(b) rtext_rnode_audit.py has syntax error: " + str(e))

    def run(inv):
        cmd = ["python3", tmp_py, "--inventory", inv]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=60, cwd=workdir)
            return r.returncode, r.stdout, r.stderr
        except Exception as e:
            return -1, "", str(e)

    # (c) unclean inventory -> MISALIGNED + names garbage nets test2+edit_test +
    #     names the 3 real nets vcc/vss/viso. A naive total-counter (no per-net
    #     grouping) cannot name the garbage nets -> FAIL. An always-ALIGNED stub
    #     -> FAIL (unclean must be MISALIGNED).
    rc, out_u, err_u = run(inv_unclean)
    assert rc == 0, "(c) rtext_rnode_audit.py exit=%d on unclean stderr=%s" % (rc, err_u[:300])
    assert re.search(r'\bMISALIGNED\b', out_u), \
        "(c) unclean inventory must yield MISALIGNED (got %r); a naive " \
        "always-ALIGNED tool fails here" % out_u[:200]
    assert re.search(r'\btest2\b', out_u) and re.search(r'\bedit_test\b', out_u), \
        "(c) unclean output must name garbage nets test2 + edit_test: %r" % out_u[:300]
    assert re.search(r'\bvcc\b', out_u) and re.search(r'\bvss\b', out_u) and \
        re.search(r'\bviso\b', out_u), \
        "(c) unclean output must name the 3 real power nets vcc/vss/viso: %r" % out_u[:300]

    # (d) unclean duplicate label count = 9 (3 RTEXT dups + 6 RNODE dups).
    #     A tool that does not dedup by (layer,purpose,net,xy) reports wrong
    #     count. Also drawing-purpose (24 vblh!) MUST NOT be counted as dups
    #     or as RTEXT/RNODE (a tool that fails to filter drawing inflates counts).
    dm = re.search(r'duplicate_labels:\s*(\d+)', out_u)
    assert dm and int(dm.group(1)) == 9, \
        "(d) unclean duplicate_labels must be 9 (3 RTEXT + 6 RNODE dups), " \
        "got: %r" % out_u[:300]
    # drawing-purpose must be ignored: total RTEXT+RNODE parsed = 12+37 = 49
    # (not 49+24). Check the report does not count vblh as a net.
    assert "vblh" not in out_u, \
        "(d) drawing-purpose net 'vblh' must be ignored, not audited: %r" % out_u[:300]

    # (e) per-net verdict: test2/edit_test = GARBAGE (RTEXT>0 AND RNODE==0).
    #     A tool that only checks RTEXT>0 (ignores RNODE==0) would mark garbage
    #     nets ALIGNED -> FAIL. Look for a GARBAGE verdict line for each.
    assert re.search(r'net=test2\b.*verdict=GARBAGE', out_u) or \
           re.search(r'GARBAGE.*test2', out_u), \
        "(e) test2 must be flagged GARBAGE (RTEXT>0 but RNODE==0): %r" % out_u[:300]
    assert re.search(r'net=edit_test\b.*verdict=GARBAGE', out_u) or \
           re.search(r'GARBAGE.*edit_test', out_u), \
        "(e) edit_test must be flagged GARBAGE (RTEXT>0 but RNODE==0): %r" % out_u[:300]
    # real nets must be ALIGNED
    assert re.search(r'net=vcc\b.*verdict=ALIGNED', out_u) or \
           re.search(r'ALIGNED.*vcc', out_u), \
        "(e) vcc must be ALIGNED: %r" % out_u[:300]

    # (f) clean inventory -> ALIGNED + 0 garbage + 0 duplicates + 3 nets all
    #     ALIGNED (vcc RTEXT=2 RNODE=11, vss RTEXT=2 RNODE=11, viso RTEXT=2 RNODE=9).
    rc, out_c, err_c = run(inv_clean)
    assert rc == 0, "(f) rtext_rnode_audit.py exit=%d on clean stderr=%s" % (rc, err_c[:300])
    assert re.search(r'\bALIGNED\b', out_c), \
        "(f) clean inventory must yield ALIGNED: %r" % out_c[:200]
    dmc = re.search(r'duplicate_labels:\s*(\d+)', out_c)
    assert dmc and int(dmc.group(1)) == 0, \
        "(f) clean duplicate_labels must be 0, got: %r" % out_c[:200]
    gmc = re.search(r'garbage_nets:\s*(\d+)', out_c)
    assert gmc and int(gmc.group(1)) == 0, \
        "(f) clean garbage_nets must be 0, got: %r" % out_c[:200]
    # clean has exactly 3 nets, all ALIGNED
    assert re.search(r'net=vcc\b.*RTEXT=2.*RNODE=11.*verdict=ALIGNED', out_c), \
        "(f) clean vcc must be RTEXT=2 RNODE=11 ALIGNED: %r" % out_c[:300]
    assert re.search(r'net=vss\b.*RTEXT=2.*RNODE=11.*verdict=ALIGNED', out_c), \
        "(f) clean vss must be RTEXT=2 RNODE=11 ALIGNED: %r" % out_c[:300]
    assert re.search(r'net=viso\b.*RTEXT=2.*RNODE=9.*verdict=ALIGNED', out_c), \
        "(f) clean viso must be RTEXT=2 RNODE=9 ALIGNED: %r" % out_c[:300]

    # (g) cleanup_report.txt enumerates per-net (net + RTEXT + RNODE + verdict)
    #     for all 3 real nets AND the 2 garbage nets, plus a delete list with
    #     xy. A tool that only reports totals (no per-net block) -> FAIL.
    for net in ("vcc", "vss", "viso", "test2", "edit_test"):
        assert net in report_txt, \
            "(g) cleanup_report.txt missing net: %s" % net
    assert "DELETE" in report_txt, \
        "(g) cleanup_report.txt missing DELETE suggested-delete list"
    # delete list must include xy coordinates (proves real dedup, not just a count)
    assert re.search(r'xy=\(', report_txt), \
        "(g) cleanup_report.txt delete list must include xy= coordinates: %r" % report_txt[:200]
    # report must reference both BEFORE (MISALIGNED) and AFTER (ALIGNED) states
    assert "MISALIGNED" in report_txt and "ALIGNED" in report_txt, \
        "(g) cleanup_report.txt must contrast BEFORE (MISALIGNED) vs AFTER (ALIGNED)"

    # cleanup the temp candidate file
    try:
        os.remove(tmp_py)
    except OSError:
        pass

    return True
