def check(deliverable, workdir):
    """SiliconSmart library-characterization config-debug deliverable checker.

    deliverable: path to submit.zip (relative to workdir), e.g. "outputs/submit.zip"
    workdir:     session workdir (attachments are placed here at session open)

    7 independent conditions (a)-(g); each has teeth so the buggy originals FAIL
    and a correct patch PASSES. All-static Python (no SiliconSmart run needed).
    """
    import os, re, zipfile

    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    need = [
        "drgqx_cmos_analog.tcl",
        "drgqx_cmos_digital.tcl",
        "drgqx_cmos_io.tcl",
        "drgqx_cmos_stdcells.tcl",
        "stdcells_ac.tcl",
        "configure.tcl",
        "ffrqIOLVx2_pc60_odt.inst",
        "nor3IOLVIOx1_DQS.inst",
        "invYx2_CoM.inst",
        "IO_TX_LOCAL_DCA_DQS.inst",
        "T_CompXor.inst",
        "fix_summary.md",
    ]

    with zipfile.ZipFile(p) as z:
        # map basename -> zip entry (so subdir layouts also work)
        bmap = {}
        for n in z.namelist():
            if n.endswith("/"):
                continue
            bmap[os.path.basename(n)] = n
        missing = [b for b in need if b not in bmap]
        if missing:
            raise AssertionError("submit.zip 缺少交付件: " + ", ".join(missing))

        tcl_texts = {b: z.read(bmap[b]).decode("utf-8", "ignore") for b in need if b.endswith(".tcl")}
        inst_texts = {b: z.read(bmap[b]).decode("utf-8", "ignore") for b in need if b.endswith(".inst")}
        summary_text = z.read(bmap["fix_summary.md"]).decode("utf-8", "ignore")

    # --- helpers: Tcl '#' is a comment only where a command is expected (line
    #     start, after optional leading whitespace). A trailing "# disabled" is
    #     NOT a comment -- the command still runs (the real-world trap). ---
    def active_lines(txt):
        out = []
        for ln in txt.splitlines():
            s = ln.lstrip()
            if s.startswith("#"):
                continue
            if s.strip() == "":
                continue
            out.append(ln)
        return out

    tcl_buggy = [
        "drgqx_cmos_analog.tcl", "drgqx_cmos_digital.tcl", "drgqx_cmos_io.tcl",
        "drgqx_cmos_stdcells.tcl", "stdcells_ac.tcl",
    ]

    # --- (a) 5 export *.tcl: qualify_library/qualification_lc_shell commented
    #         at line START; model uses -timing not -verilog all ---
    for b in tcl_buggy:
        al = active_lines(tcl_texts[b])
        for ln in al:
            if re.search(r"\bqualify_library\b", ln) or re.search(r"qualification_lc_shell", ln):
                raise AssertionError(
                    b + ": qualify_library/qualification_lc_shell 仍有未在行首 '#' 注释的活跃行 -> " + ln.strip())
        for ln in al:
            if "-verilog all" in ln:
                raise AssertionError(b + ": model 仍用 -verilog all -> " + ln.strip())
        has_timing_model = any(re.search(r"\bmodel\b", ln) and "-timing" in ln for ln in al)
        if not has_timing_model:
            raise AssertionError(b + ": 未找到 model ... -timing 行 (建模必须只建模有表征数据的 cell)")

    # --- (b) ffrqIOLVx2_pc60_odt.inst: add_latch no empty {} register name;
    #         AND no '^' in any add_forbidden_state / add_function line (all .inst) ---
    f = "ffrqIOLVx2_pc60_odt.inst"
    for ln in active_lines(inst_texts[f]):
        if re.search(r"add_latch\s+\S+\s+\{\s*\}", ln):
            raise AssertionError(f + ": add_latch 仍含空 '{}' 寄存器名 -> " + ln.strip())
    for b, txt in inst_texts.items():
        for ln in active_lines(txt):
            if (re.search(r"\badd_forbidden_state\b", ln) or re.search(r"\badd_function\b", ln)) and "^" in ln:
                raise AssertionError(b + ": add_forbidden_state/add_function 仍含非法 '^' (XOR) -> " + ln.strip())

    # --- (c) nor3IOLVIOx1_DQS.inst: set_netlist_file / cut_netlist point to
    #         nor3IOLVIOx1_DQS.spf_RC; old name nor3IOLVIO_1p6.spf_RC gone ---
    f = "nor3IOLVIOx1_DQS.inst"
    ntxt = inst_texts[f]
    if "nor3IOLVIO_1p6.spf_RC" in ntxt:
        raise AssertionError(f + ": 仍引用旧网表名 nor3IOLVIO_1p6.spf_RC")
    net_ok = False
    for ln in active_lines(ntxt):
        if (re.search(r"\bset_netlist_file\b", ln) or re.search(r"\bcut_netlist\b", ln)):
            if "nor3IOLVIOx1_DQS.spf_RC" in ln:
                net_ok = True
            else:
                raise AssertionError(f + ": set_netlist_file/cut_netlist 未指向 nor3IOLVIOx1_DQS.spf_RC -> " + ln.strip())
    if not net_ok:
        raise AssertionError(f + ": 未找到指向 nor3IOLVIOx1_DQS.spf_RC 的 set_netlist_file/cut_netlist 行")

    # --- (d) invYx2_CoM.inst: A/Y pin use vwlp_type (not bare 'default') ---
    f = "invYx2_CoM.inst"
    ial = active_lines(inst_texts[f])
    for ln in ial:
        if re.search(r"add_pin\s+(A|Y)\s+default\b", ln):
            raise AssertionError(f + ": A/Y pin 仍用 default pintype -> " + ln.strip())
    if not any(re.search(r"add_pin\s+A\s+vwlp_type\b", ln) for ln in ial):
        raise AssertionError(f + ": 未找到 add_pin A vwlp_type")
    if not any(re.search(r"add_pin\s+Y\s+vwlp_type\b", ln) for ln in ial):
        raise AssertionError(f + ": 未找到 add_pin Y vwlp_type")

    # --- (e) IO_TX_LOCAL_DCA_DQS.inst: default_input_state defined (active);
    #         no '||'; no '<' in add_function/add_forbidden_state lines ---
    f = "IO_TX_LOCAL_DCA_DQS.inst"
    eal = active_lines(inst_texts[f])
    if not any("default_input_state" in ln for ln in eal):
        raise AssertionError(f + ": 未在活跃行定义 default_input_state (PARA-7 未修)")
    for ln in eal:
        if "||" in ln:
            raise AssertionError(f + ": 仍含非法 '||' -> " + ln.strip())
        if (re.search(r"\badd_function\b", ln) or re.search(r"\badd_forbidden_state\b", ln)) and "<" in ln:
            raise AssertionError(f + ": add_function/add_forbidden_state 仍含非法 '<' -> " + ln.strip())

    # --- (f) configure.tcl: vssFoot not duplicate (<=1 active -param vssFoot def) ---
    f = "configure.tcl"
    cnt = 0
    for ln in active_lines(tcl_texts[f]):
        if re.search(r"set_config_opt\s+-param\s+vssFoot\b", ln):
            cnt += 1
    if cnt > 1:
        raise AssertionError("configure.tcl: vssFoot 仍重复定义 (活跃定义数=%d, 应 <=1)" % cnt)

    # --- (g) fix_summary.md: non-empty + covers each error category ---
    s = summary_text.strip().lower()
    if not s:
        raise AssertionError("fix_summary.md 为空")
    required = [
        ("qualify", "lc_shell/qualify_library"),
        (("verilog", "timing"), "model SMSC-99"),
        ("add_latch", "latch 语法"),
        (("xor", "forbidden"), "forbidden_state XOR"),
        ("netlist", "网表名漂移"),
        ("default_input_state", "PARA-7"),
        ("vssfoot", "vssFoot 重复"),
        ("vwlp", "vwlp pintype"),
    ]
    for tok, desc in required:
        if isinstance(tok, tuple):
            ok = any(t in s for t in tok)
        else:
            ok = tok in s
        if not ok:
            raise AssertionError("fix_summary.md 未覆盖问题类别: " + desc + " (关键字 " + str(tok) + " 缺失)")

    return True
