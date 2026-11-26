def check(deliverable, workdir):
    """PDK-QA DRC test-environment deliverable checker.

    deliverable: path to submit.zip (relative to workdir), e.g. "outputs/submit.zip"
    workdir:     session workdir (attachments placed here at session open).

    7 independent conditions (a)-(g). All-static Python (no Calibre run needed).
    TEETH: a naive "only CALIBRE_HOME" solution FAILS (c)+(d)+(g); the correct
    fake-MGC_HOME + stub-libXss + auto-rebuild solution PASSES.
    """
    import os, re, zipfile

    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    need = ["test_env.py", "smoke_report.md", "PHASE2_REPORT.md"]
    with zipfile.ZipFile(p) as z:
        bmap = {}
        for n in z.namelist():
            if n.endswith("/"):
                continue
            bmap[os.path.basename(n)] = n
        missing = [b for b in need if b not in bmap]
        if missing:
            raise AssertionError("submit.zip missing: " + ", ".join(missing))
        env_txt   = z.read(bmap["test_env.py"]).decode("utf-8", "ignore")
        smoke_txt = z.read(bmap["smoke_report.md"]).decode("utf-8", "ignore")
        rep_txt   = z.read(bmap["PHASE2_REPORT.md"]).decode("utf-8", "ignore")

    SUPPORT = [
        "ldr", "drcSyntax", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
        "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
        "uselessDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
        "emptyDeriveLayer", "drcWithPattern",
        "patternLayerVsDesignRuleLayerChange", "drcConsistencyWithChangedLdr",
        "drcCountWithinOption", "antMetalThk",
    ]
    TEXT = [
        "ldr", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
        "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
        "uselessDeriveLayer", "drcConsistencyWithChangedLdr",
        "drcCountWithinOption", "antMetalThk",
    ]
    PATTERN_CANSTART = [
        "emptyDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
        "patternLayerVsDesignRuleLayerChange", "drcWithPattern",
    ]

    # (a) zip contains the 3 deliverables
    assert len(missing) == 0, "(a) missing deliverables: " + str(missing)

    # (b) test_env.py fixes libpython3.7 by putting python-3.7.1 lib on LD_LIBRARY_PATH
    assert "python-3.7.1/x86_64/lib" in env_txt, \
        "(b) test_env.py does not add python-3.7.1/x86_64/lib to LD_LIBRARY_PATH"

    # (c) Calibre VCO bypass: fake MGC_HOME assigned + fake-home tmp path + stub libXss + calibre_vco stub
    #     TEETH: "only CALIBRE_HOME" has none of these -> FAIL.
    has_mgc_assign = re.search(r'MGC_HOME["\']?\]?\s*=\s*', env_txt) is not None
    has_fake_home  = ("calibre_fake_home" in env_txt) or (re.search(r'fake[_\s]*home', env_txt, re.I) is not None)
    has_libxss     = "libXss" in env_txt
    has_vco_stub   = "calibre_vco" in env_txt
    assert has_mgc_assign and has_fake_home and has_libxss and has_vco_stub, \
        "(c) no fake-MGC_HOME + stub-libXss + calibre_vco bypass (got mgc=%s fakehome=%s xss=%s vco=%s)" \
        % (has_mgc_assign, has_fake_home, has_libxss, has_vco_stub)

    # (d) auto-rebuild at import: existence check of BOTH stub paths + rebuild-if-missing
    #     + a module-level invocation of the setup.
    #     TEETH: bypass defined but only called lazily / always-recreate / no import call -> FAIL.
    has_fakehome_path = "/tmp/calibre_fake_home" in env_txt
    has_libxss_path   = "/tmp/libXss.so.1" in env_txt
    has_existence_check = re.search(
        r'not\s+os\.path\.(isdir|exists)\s*\(\s*_FAKE_HOME\s*\)|'
        r'not\s+os\.path\.(isdir|exists)\s*\(\s*_LIBXSS\s*\)|'
        r'need_rebuild|rebuild\s*=|if.*missing', env_txt) is not None
    has_import_call = re.search(r'^_setup_calibre_env\(\)\s*$',
                                env_txt, re.MULTILINE) is not None
    assert has_fakehome_path and has_libxss_path and has_existence_check and has_import_call, \
        "(d) no auto-rebuild-at-import (paths=%s/%s existence=%s importcall=%s)" \
        % (has_fakehome_path, has_libxss_path, has_existence_check, has_import_call)

    # (e) check_calibre_env() returns a (ok, msg) tuple
    m = re.search(r'def\s+check_calibre_env\s*\([^)]*\)\s*:.*?(?=\n(?:def\s|\Z))',
                  env_txt, re.DOTALL)
    assert m is not None, "(e) no check_calibre_env() definition"
    body = m.group(0)
    assert re.search(r'return\s*\(\s*\w+\s*,\s*[^)]*\s*\)|return\s+\w+\s*,\s*',
                      body) is not None, \
        "(e) check_calibre_env() does not return a (ok, msg) tuple"

    # (f) smoke_report lists all 17 supportFuncnames with correct verdicts:
    #     11 text -> PASS, drcSyntax -> PASS, 5 pattern -> CAN_START (not PASS, not SKIP/FAIL)
    for name in SUPPORT:
        assert name in smoke_txt, "(f) smoke_report missing checker: " + name
    for name in TEXT:
        line = re.search(r'^\s*[-*]\s*' + re.escape(name) + r'\s*:\s*(\w+)',
                         smoke_txt, re.MULTILINE)
        assert line and line.group(1).upper() == "PASS", \
            "(f) text checker %s not PASS (got %s)" % (name, line.group(1) if line else None)
    ds = re.search(r'^\s*[-*]\s*drcSyntax\s*:\s*(\w+)', smoke_txt, re.MULTILINE)
    assert ds and ds.group(1).upper() == "PASS", \
        "(f) drcSyntax not PASS (got %s)" % (ds.group(1) if ds else None)
    for name in PATTERN_CANSTART:
        line = re.search(r'^\s*[-*]\s*' + re.escape(name) + r'\s*:\s*(\w+)',
                         smoke_txt, re.MULTILINE)
        assert line and line.group(1).upper() == "CAN_START", \
            "(f) pattern checker %s not CAN_START (got %s) -- VCO was resolved, " \
            "pattern QA can start; marking PASS is wrong, SKIP/FAIL is wrong." \
            % (name, line.group(1) if line else None)

    # (g) PHASE2_REPORT pinpoints the calibre_env variable-name bug AND records
    #     that the CALIBRE_HOME-only regular approach was tried and failed AND
    #     the hacky workaround was restored.
    #     TEETH: a report that says "set CALIBRE_HOME, all pass" -> FAIL.
    has_varbug = (re.search(r'SW_WKSTN|MGC_VCO_', rep_txt) is not None and
                  re.search(r'(variable|var|underscore|\$SW|shell)', rep_txt, re.I) is not None)
    has_regular_fail = bool(re.search(
        r'CALIBRE_HOME.*?(fail|did not|does not|still|ineffective|unconditional|'
        r'unconditionnally|tried.{0,12}fail)', rep_txt, re.I | re.DOTALL))
    has_hacky_restore = bool(re.search(
        r'(restor|fake\s+MGC_HOME|stub\s+libXss|workaround)', rep_txt, re.I))
    assert has_varbug, "(g) PHASE2_REPORT does not pinpoint the calibre_env variable-name bug"
    assert has_regular_fail, \
        "(g) PHASE2_REPORT does not record that CALIBRE_HOME-only failed"
    assert has_hacky_restore, \
        "(g) PHASE2_REPORT does not describe the restored hacky workaround"

    return True
