#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-StaFlowScaffold-001 (shard A, round 50).

A-grade faithful (trace q11i6, e0046913@hfeg0pkn003, mc=874, digital).
verb = sta-flow-scaffold (construct STA flow dir tree mirroring a lint flow,
referencing feint PrimeTime scripts) -- unique vs all existing shard-A verbs.

Creates:
  assets/EDA-Eval-DesignFlow-StaFlowScaffold-001/
      prompt.txt, task_brief.md
      lint_flow_A/{config,run,data,script,all_out/...}
      feint_ref_A/{setup,scripts,Makefile}
      hidden/lint_flow_B/..., feint_ref_B/..., hidden_manifest.json
  reference/EDA-Eval-DesignFlow-StaFlowScaffold-001/
      build_sta_flow.py (reference solution)
      check.py (20 conditions a-t)
      report_A.json, reference_submit.zip
      negative/{fake_empty,fake_print_expected,fake_core_deleted,
                naive_hardcode_a,fake_structure_only}.py
      negative_selftest.py
Then self-verifies (ref PASS 20/20, 5 negatives + 3 fake all FAIL).
"""
import os, sys, json, zipfile, subprocess, tempfile, shutil, py_compile, stat, re

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-StaFlowScaffold-001"
AST = os.path.join(REPO, "assets", CASE)
REF = os.path.join(REPO, "reference", CASE)
NEG = os.path.join(REF, "negative")
A_LINT = os.path.join(AST, "lint_flow_A")
A_FEINT = os.path.join(AST, "feint_ref_A")
B_LINT = os.path.join(AST, "hidden", "lint_flow_B")
B_FEINT = os.path.join(AST, "hidden", "feint_ref_B")

# ---------- helpers ----------
def _w(path, content, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    if mode is not None:
        os.chmod(path, mode)

def _ln(src, dst):
    if os.path.lexists(dst):
        os.remove(dst)
    os.symlink(src, dst)

# ============================================================
# 1. A bundle (lint_flow_A + feint_ref_A) -- minimal faithful
# ============================================================
def build_A_bundle():
    L = os.path.join(AST, "lint_flow_A")
    # config
    _w(os.path.join(L, "config", "CXDP_DESIGN_CFG"),
       "# CXMP design config\nCXDP_DESIGN_NAME=cla_top\nCXDP_PROJ_TAG=v1.0_Latest\nCXDP_LINT_CORNER=typical\n")
    _w(os.path.join(L, "config", "CXDP_PROJ_CFG"),
       "# project config\nCXDP_PROJ=lacaa\nCXDP_PROJ_ROOT=/proj/lacaa/TV1_digital\n")
    # run
    _w(os.path.join(L, "run", "CXDP_LINT_CFG"),
       "# CXMP lint config\nCXDP_DESIGN_NAME=cla_top\nCXDP_LINT_TAG=v1.0_Latest\nCXDP_LINT_TOOL=spyglass\n")
    _w(os.path.join(L, "run", "lint.tcl"),
       "# lint.tcl - spyglass lint flow\nsource lint_setup.tcl\nread_verilog -container r ../data/cla_top.awl\nrun_lint -category all > ../all_out/v1.0_Latest/report/lint.rpt\nexit\n")
    _w(os.path.join(L, "run", "Makefile"),
       "# Makefile - lint flow\ninclude CXDP_LINT_CFG\nDESIGN ?= $(CXDP_DESIGN_NAME)\n.PHONY: help lint clean\nhelp:\n\t@echo \"lint flow (design=$(DESIGN))\"\nlint:\n\tspyglass -f lint.tcl\nclean:\n\trm -rf ../all_out/v1.0_Latest/log/*\n")
    # run symlinks (structural example, not read by builder)
    _ln("../../config/CXDP_DESIGN_CFG", os.path.join(L, "run", "CXDP_DESIGN_CFG"))
    _ln("../../config/CXDP_PROJ_CFG", os.path.join(L, "run", "CXDP_PROJ_CFG"))
    # data
    _w(os.path.join(L, "data", "cla_top.awl"), "// cla_top lint awl filelist\nrtl/cla_top.v\nrtl/cla_sub.v\n")
    # script
    _w(os.path.join(L, "script", "lint_qa_chk.pl"),
       "#!/usr/bin/perl\nuse strict; use warnings;\nmy $d=$ENV{CXDP_DESIGN_NAME}||\"design\";\nprint \"LINT QA: $d\\n\";\nexit 0;\n")
    # all_out
    for sub in ("filelist", "log", "out_src", "QA", "report"):
        os.makedirs(os.path.join(L, "all_out", "v1.0_Latest", sub), exist_ok=True)
    # feint_ref_A
    F = os.path.join(AST, "feint_ref_A")
    _w(os.path.join(F, "setup", "common_setup.tcl"),
       "# feint common setup\nset PBA gbv\nset corner typical\nset DESIGN cla_top\n")
    _w(os.path.join(F, "scripts", "pt.tcl"),
       "# pt.tcl - PrimeTime reference\nsource ../setup/common_setup.tcl\nread_verilog \$DESIGN.netlist.f\nread_sdc \$DESIGN.sdc\nupdate_timing\nreport_timing -npaths 50\nexit\n")
    _w(os.path.join(F, "Makefile"),
       "# feint Makefile\nPT = pt_shell\n.PHONY: sta\nsta:\n\t$(PT) -f scripts/pt.tcl\n")

# ============================================================
# 2. B hidden bundle (heterogeneous cross-input guard)
# ============================================================
def build_B_bundle():
    L = os.path.join(AST, "hidden", "lint_flow_B")
    _w(os.path.join(L, "config", "CXDP_DESIGN_CFG"),
       "# CXMP design config (B)\nCXDP_DESIGN_NAME=uart_top\nCXDP_PROJ_TAG=v2.1_Latest\nCXDP_LINT_CORNER=ss0p72vm40c\n")
    _w(os.path.join(L, "config", "CXDP_PROJ_CFG"),
       "# project config (B)\nCXDP_PROJ=lacaa\nCXDP_PROJ_ROOT=/proj/lacaa/TV2_digital\n")
    _w(os.path.join(L, "run", "CXDP_LINT_CFG"),
       "# CXDP lint config (B)\nCXDP_DESIGN_NAME=uart_top\nCXDP_LINT_TAG=v2.1_Latest\nCXDP_LINT_TOOL=spyglass\n")
    _w(os.path.join(L, "run", "lint.tcl"),
       "# lint.tcl - spyglass lint flow (B)\nsource lint_setup.tcl\nread_verilog -container r ../data/uart_top.awl\nrun_lint -category all > ../all_out/v2.1_Latest/report/lint.rpt\nexit\n")
    _w(os.path.join(L, "run", "Makefile"),
       "# Makefile - lint flow (B)\ninclude CXDP_LINT_CFG\nDESIGN ?= $(CXDP_DESIGN_NAME)\n.PHONY: help lint clean\nhelp:\n\t@echo \"lint flow (design=$(DESIGN))\"\nlint:\n\tspyglass -f lint.tcl\nclean:\n\trm -rf ../all_out/v2.1_Latest/log/*\n")
    _ln("../../config/CXDP_DESIGN_CFG", os.path.join(L, "run", "CXDP_DESIGN_CFG"))
    _ln("../../config/CXDP_PROJ_CFG", os.path.join(L, "run", "CXDP_PROJ_CFG"))
    _w(os.path.join(L, "data", "uart_top.awl"), "// uart_top lint awl filelist\nrtl/uart_top.v\nrtl/uart_baud.v\n")
    _w(os.path.join(L, "script", "lint_qa_chk.pl"),
       "#!/usr/bin/perl\nuse strict; use warnings;\nmy $d=$ENV{CXDP_DESIGN_NAME}||\"design\";\nprint \"LINT QA: $d\\n\";\nexit 0;\n")
    for sub in ("filelist", "log", "out_src", "QA", "report"):
        os.makedirs(os.path.join(L, "all_out", "v2.1_Latest", sub), exist_ok=True)
    # extra mcmm subdir (B only)
    _w(os.path.join(L, "mcmm", "mcmm.tcl"), "# mcmm multi-corner multi-mode config (B)\nset modes {func scan}\nset corners {ss0p72vm40c tt_25c ff_0p99vm125c}\n")
    # feint_ref_B (PBA=exhaustive)
    F = os.path.join(AST, "hidden", "feint_ref_B")
    _w(os.path.join(F, "setup", "common_setup.tcl"),
       "# feint common setup (B)\nset PBA exhaustive\nset corner ss0p72vm40c\nset DESIGN uart_top\n")
    _w(os.path.join(F, "scripts", "pt.tcl"),
       "# pt.tcl - PrimeTime reference (B)\nsource ../setup/common_setup.tcl\nread_verilog \$DESIGN.netlist.f\nread_sdc \$DESIGN.sdc\nupdate_timing\nreport_timing -npaths 50\nexit\n")
    _w(os.path.join(F, "Makefile"),
       "# feint Makefile (B)\nPT = pt_shell\n.PHONY: sta\nsta:\n\t$(PT) -f scripts/pt.tcl\n")
    _w(os.path.join(AST, "hidden", "hidden_manifest.json"),
       json.dumps({"lint_dir": "lint_flow_B", "feint_dir": "feint_ref_B",
                   "design": "uart_top", "tag": "v2.1_Latest",
                   "pba": "exhaustive", "corner": "ss0p72vm40c",
                   "mcmm": True, "note": "heterogeneous vs A"}, indent=2))

# ============================================================
# 3. prompt + task_brief
# ============================================================
def build_prompt():
    _w(os.path.join(AST, "prompt.txt"),
       "/proj/lacaa/TV1_digital/simdir/yutingq/CXDP/cla_top/lint 仔细阅读该目录下的文件层次和结构，"
       "以cla_top的lint flow为参考，为我构建一个相同文件层次结构的sta flow。"
       "（sta flow的脚本参考来源为/proj/lacaa/TV1_digital/simdir/yutingq/feint）\n\n"
       "【交付要求】请编写一个通用的 STA flow 构建器 build_sta_flow.py，"
       "命令行接口：\n"
       "    python3 build_sta_flow.py --lint <lint_flow_dir> --feint <feint_ref_dir> --out <out_dir>\n"
       "该构建器读取参考 lint flow 的目录层次 + feint 的 PrimeTime 脚本，"
       "在 <out_dir> 下镜像生成一套完整的 STA flow 目录树（含 run/、data/、script/、all_out/、config/ 等子目录，"
       "以及 sta.tcl、sta_setup.tcl、Makefile、CXDP_STA_CFG、sta_qa_chk.pl、README.md、install.sh 等文件，"
       "脚本需能通过 perl -c / tclsh info complete / make -n help / bash -n 的语法校验）。\n"
       "构建器需自适应：从输入 bundle 读取 design name / tag / corner / PBA 模式等参数并传播到产物中，"
       "使得同一构建器对结构不同的 bundle 也能正确生成 STA flow。\n\n"
       "可见输入 bundle 位于本工作目录的 lint_flow_A/ 与 feint_ref_A/ 下。\n"
       "请把 build_sta_flow.py 以及对可见 A bundle 运行构建器后输出的结构化清单 report_A.json（JSON manifest，"
       "至少含 design/tag/pba/corner/mcmm 字段）一起打包成 outputs/submit.zip 提交。\n")
    _w(os.path.join(AST, "task_brief.md"),
       "# 交付接口\n\n- 交付件：`outputs/submit.zip`，内含 `build_sta_flow.py` + `report_A.json` 两件。\n"
       "- 构建器 CLI：`build_sta_flow.py --lint <dir> --feint <dir> --out <dir>`。\n"
       "- 可见输入：`lint_flow_A/`、`feint_ref_A/`（本工作目录下）。\n")

# ============================================================
# 4. reference solution: build_sta_flow.py
# ============================================================
BUILDER_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_sta_flow.py - Generic STA flow scaffolding builder.

Reads an existing lint flow directory tree + a feint PrimeTime reference,
and emits a mirrored STA flow directory tree with PT-based scripts.

CLI: build_sta_flow.py --lint <lint_dir> --feint <feint_dir> --out <out_dir>
Prints a JSON manifest to stdout (design/tag/pba/corner/mcmm/...).
"""
import os, sys, re, json

def _parse_kv(path):
    d = {}
    if not os.path.isfile(path):
        return d
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d

def _parse_tcl_vars(path, names):
    d = {}
    if not os.path.isfile(path):
        return d
    txt = open(path).read()
    for n in names:
        m = re.search(r'^\s*set\s+%s\s+(\S+)' % re.escape(n), txt, re.M)
        if m:
            d[n] = m.group(1).strip('"')
    return d

def _w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def _symlink(src, dst):
    if os.path.lexists(dst):
        os.remove(dst)
    os.symlink(src, dst)

def build(lint_dir, feint_dir, out_dir):
    cfg = _parse_kv(os.path.join(lint_dir, "config", "CXDP_DESIGN_CFG"))
    design = cfg.get("CXDP_DESIGN_NAME", "design")
    tag = cfg.get("CXDP_PROJ_TAG", "v1.0_Latest")
    corner = cfg.get("CXDP_LINT_CORNER", "typical")
    cs = _parse_tcl_vars(os.path.join(feint_dir, "setup", "common_setup.tcl"),
                         ["PBA", "corner"])
    pba = cs.get("PBA", "gba")
    fcorner = cs.get("corner", corner)
    mcmm = os.path.isdir(os.path.join(lint_dir, "mcmm"))

    # config (copy from lint so output is self-contained)
    cfg_dir = os.path.join(out_dir, "config")
    os.makedirs(cfg_dir, exist_ok=True)
    for fn in ("CXDP_DESIGN_CFG", "CXDP_PROJ_CFG"):
        src = os.path.join(lint_dir, "config", fn)
        if os.path.isfile(src):
            _w(os.path.join(cfg_dir, fn), open(src).read())

    # run dir
    run_dir = os.path.join(out_dir, "run")
    os.makedirs(run_dir, exist_ok=True)
    sta_cfg = ("# CXDP STA config (derived from lint)\n"
               "CXDP_DESIGN_NAME=%s\nCXDP_PROJ_TAG=%s\n"
               "STA_CORNER=%s\nSTA_PBA=%s\nSTA_TOOL=pt_shell\n"
               % (design, tag, fcorner, pba))
    _w(os.path.join(run_dir, "CXDP_STA_CFG"), sta_cfg)
    feint_cs = os.path.join(feint_dir, "setup", "common_setup.tcl")
    cs_txt = open(feint_cs).read() if os.path.isfile(feint_cs) else ""
    sta_setup = ("# sta_setup.tcl - STA setup (derived from feint common_setup)\n"
                 + cs_txt + "\nset DESIGN_NAME %s\n" % design)
    _w(os.path.join(run_dir, "sta_setup.tcl"), sta_setup)
    sta_tcl = ("# sta.tcl - PrimeTime STA flow\n"
               "source sta_setup.tcl\n"
               "read_verilog -container r -libname L ../data/%s.netlist.f\n"
               "read_sdc ../data/%s.sdc\n"
               "set_operating_conditions -analysis_type on_chip_variation %s\n"
               "update_timing\n"
               "report_timing -delay_type max -npaths 50 -significant_digits 4 > ../all_out/%s/report/sta_max.rpt\n"
               "report_timing -delay_type min -npaths 50 > ../all_out/%s/report/sta_min.rpt\n"
               "report_constraint -all_violators > ../all_out/%s/report/constraint.rpt\n"
               "exit\n"
               % (design, design, fcorner, tag, tag, tag))
    _w(os.path.join(run_dir, "sta.tcl"), sta_tcl)
    makefile = ("# Makefile - STA flow (PrimeTime via LSF)\n"
                "include CXDP_STA_CFG\n"
                "DESIGN ?= $(CXDP_DESIGN_NAME)\n"
                "TAG ?= $(CXDP_PROJ_TAG)\n"
                "PT = pt_shell\n"
                "LSF = bsub -q lnx64 -P STA\n"
                ".PHONY: help sta_run report clean\n"
                "help:\n"
                "\t@echo \"STA flow targets: sta_run report clean (design=$(DESIGN) tag=$(TAG))\"\n"
                "sta_run:\n"
                "\t$(LSF) $(PT) -f sta.tcl -x \"set DESIGN $(DESIGN)\" 2>&1 | tee ../all_out/$(TAG)/log/sta.log\n"
                "report:\n"
                "\t$(PT) -f sta.tcl 2>&1 | tee ../all_out/$(TAG)/log/sta_rpt.log\n"
                "clean:\n"
                "\trm -rf ../all_out/$(TAG)/log/* ../all_out/$(TAG)/report/*\n")
    _w(os.path.join(run_dir, "Makefile"), makefile)
    _symlink("../config/CXDP_DESIGN_CFG",
             os.path.join(run_dir, "CXDP_DESIGN_CFG"))
    _symlink("../config/CXDP_PROJ_CFG",
             os.path.join(run_dir, "CXDP_PROJ_CFG"))

    # data dir
    data_dir = os.path.join(out_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    _w(os.path.join(data_dir, "%s.netlist.f" % design),
       "# netlist filelist for %s\nrtl/%s_netlist.v\n" % (design, design))
    _w(os.path.join(data_dir, "%s.sdc" % design),
       "# SDC for %s\ncreate_clock -name clk -period 2.0 [get_ports clk]\n" % design)
    _w(os.path.join(data_dir, "sta_override.tcl"),
       "# sta override (from feint)\nset_propagated_clock [all_clocks]\n")

    # script dir
    script_dir = os.path.join(out_dir, "script")
    os.makedirs(script_dir, exist_ok=True)
    qa = ("#!/usr/bin/perl\n# sta_qa_chk.pl - STA QA check\n"
          "use strict; use warnings;\n"
          "my $design = $ENV{CXDP_DESIGN_NAME} || \"design\";\n"
          "print \"STA QA: design=$design\\n\";\n"
          "exit 0;\n")
    _w(os.path.join(script_dir, "sta_qa_chk.pl"), qa)

    # all_out
    for sub in ("filelist", "log", "out_src", "QA", "report"):
        os.makedirs(os.path.join(out_dir, "all_out", tag, sub), exist_ok=True)

    # mcmm (mirror lint)
    if mcmm:
        os.makedirs(os.path.join(out_dir, "mcmm"), exist_ok=True)
        src_mcmm = os.path.join(lint_dir, "mcmm", "mcmm.tcl")
        body = open(src_mcmm).read() if os.path.isfile(src_mcmm) else "# mcmm config\n"
        _w(os.path.join(out_dir, "mcmm", "mcmm.tcl"), body)

    # README + install.sh
    _w(os.path.join(out_dir, "README.md"),
       "# STA flow for %s\n\nTag: %s | Corner: %s | PBA: %s | MCMM: %s\n"
       % (design, tag, fcorner, pba, mcmm))
    _w(os.path.join(out_dir, "install.sh"),
       "#!/bin/bash\n# install STA flow\nset -e\ncd \"$(dirname \"$0\")\"\n"
       "echo \"installing STA flow for %s\"\nexit 0\n" % design)
    os.chmod(os.path.join(out_dir, "install.sh"), 0o755)

    manifest = {
        "design": design, "tag": tag, "pba": pba,
        "corner": fcorner, "mcmm": mcmm,
        "run_files": sorted(os.listdir(run_dir)),
        "data_files": sorted(os.listdir(data_dir)),
        "dirs": sorted([d for d in os.listdir(out_dir)
                        if os.path.isdir(os.path.join(out_dir, d))]),
    }
    print(json.dumps(manifest, indent=2))

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--lint", required=True)
    ap.add_argument("--feint", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.lint, a.feint, a.out)

if __name__ == "__main__":
    main()
'''

def write_builder():
    _w(os.path.join(REF, "build_sta_flow.py"), BUILDER_SRC)

# ============================================================
# 5. check.py (20 conditions a-t)
# ============================================================
CHECK_SRC = r'''#!/usr/bin/env python3
"""check.py - grader for EDA-Eval-DesignFlow-StaFlowScaffold-001.

Deliverable: submit.zip containing build_sta_flow.py (generic STA flow
scaffolding builder, CLI `build_sta_flow.py --lint <d> --feint <d> --out <d>`)
and report_A.json (JSON manifest of running the builder on visible A).

Judgment: runs the candidate's build_sta_flow.py on visible A and hidden B
(subprocess, real interpreter), then validates the emitted STA flow tree with
real `perl -c` / `tclsh info complete` / `make -n help` / `bash -n`. 20
independent conditions (a)-(t). Cross-input guard (q)-(t) defeats hardcoded-A
solutions: the builder must be adaptive (read design/tag/corner/PBA/mcmm from
the bundle and propagate them).

verb: sta-flow-scaffold (construct STA flow dir tree) -- distinct from all
existing shard-A verbs.
"""
import os, re, sys, json, shlex, zipfile, subprocess, tempfile, py_compile

CID = "EDA-Eval-DesignFlow-StaFlowScaffold-001"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CID))
A_LINT = os.path.join(ASSETS, "lint_flow_A")
A_FEINT = os.path.join(ASSETS, "feint_ref_A")
B_LINT = os.path.join(ASSETS, "hidden", "lint_flow_B")
B_FEINT = os.path.join(ASSETS, "hidden", "feint_ref_B")


def _run(cmd, cwd, timeout=120):
    try:
        r = subprocess.run(["bash", "-lc", cmd], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def _extract(zip_path, dest):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)


def _tcl_complete(tcl_path):
    q = shlex.quote('set fd [open %s r]; set s [read $fd]; close $fd; '
                    'puts [info complete $s]' % tcl_path)
    rc, out, err = _run("echo %s | tclsh" % q, os.path.dirname(tcl_path))
    return rc == 0 and "1" in out, out.strip() + err.strip()


def check(deliverable, workdir):
    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    tmp = tempfile.mkdtemp(prefix="chk_stascaffold_")
    try:
        _extract(p, tmp)
        names = sorted(zipfile.ZipFile(p).namelist())

        # (a) submit.zip contains exactly build_sta_flow.py + report_A.json
        assert names == ["build_sta_flow.py", "report_A.json"], \
            "(a) submit.zip must contain exactly [build_sta_flow.py, report_A.json]; got %s" % names

        builder = os.path.join(tmp, "build_sta_flow.py")

        # (b) build_sta_flow.py compiles
        py_compile.compile(builder, doraise=True)

        # (c) builder run on A: exit0 + outA/ exists with core subdirs
        outA = tempfile.mkdtemp(prefix="outA_")
        rc, out, err = _run("python3 %s --lint %s --feint %s --out %s"
                            % (builder, A_LINT, A_FEINT, outA), tmp)
        assert rc == 0, "(c) builder on A failed rc=%d err=%s" % (rc, err[:300])
        for d in ("run", "data", "script", "all_out", "config"):
            assert os.path.isdir(os.path.join(outA, d)), \
                "(c) outA missing core subdir: %s" % d

        # (d) outA/all_out/v1.0_Latest/ has 5 subdirs
        tagA_dirs = os.path.join(outA, "all_out", "v1.0_Latest")
        assert os.path.isdir(tagA_dirs), "(d) outA all_out/v1.0_Latest missing"
        sub5 = {"filelist", "log", "out_src", "QA", "report"}
        got = set(os.listdir(tagA_dirs)) if os.path.isdir(tagA_dirs) else set()
        assert sub5 <= got, "(d) outA all_out/v1.0_Latest missing subdirs: %s" % (sub5 - got)

        # (e) outA/run/ has 6 entries: CXDP_STA_CFG, sta.tcl, sta_setup.tcl,
        #     Makefile + symlinks CXDP_DESIGN_CFG, CXDP_PROJ_CFG
        runA = os.path.join(outA, "run")
        run_entries = set(os.listdir(runA)) if os.path.isdir(runA) else set()
        need_files = {"CXDP_STA_CFG", "sta.tcl", "sta_setup.tcl", "Makefile"}
        need_links = {"CXDP_DESIGN_CFG", "CXDP_PROJ_CFG"}
        assert need_files <= run_entries, "(e) outA/run missing files: %s" % (need_files - run_entries)
        for lk in need_links:
            lp = os.path.join(runA, lk)
            assert os.path.islink(lp), "(e) outA/run/%s must be a symlink" % lk

        # (f) outA/data/ has 3 files: cla_top.netlist.f, cla_top.sdc, sta_override.tcl
        dataA = os.path.join(outA, "data")
        data_entries = set(os.listdir(dataA)) if os.path.isdir(dataA) else set()
        need_data = {"cla_top.netlist.f", "cla_top.sdc", "sta_override.tcl"}
        assert need_data <= data_entries, "(f) outA/data missing: %s" % (need_data - data_entries)

        # (g) outA/script/sta_qa_chk.pl: perl -c OK
        plA = os.path.join(outA, "script", "sta_qa_chk.pl")
        assert os.path.isfile(plA), "(g) outA/script/sta_qa_chk.pl missing"
        rc, out, err = _run("perl -c %s" % plA, os.path.dirname(plA))
        assert rc == 0, "(g) perl -c on sta_qa_chk.pl failed: %s" % (err[:200])

        # (h) outA/run/sta.tcl: tclsh info complete == 1
        ok, dbg = _tcl_complete(os.path.join(runA, "sta.tcl"))
        assert ok, "(h) tclsh info complete on sta.tcl failed: %s" % dbg[:200]

        # (i) outA/run/sta_setup.tcl: tclsh info complete == 1
        ok, dbg = _tcl_complete(os.path.join(runA, "sta_setup.tcl"))
        assert ok, "(i) tclsh info complete on sta_setup.tcl failed: %s" % dbg[:200]

        # (j) outA/run/Makefile: make -n help exit 0
        rc, out, err = _run("make -n help", runA)
        assert rc == 0, "(j) make -n help on A Makefile failed: %s" % (err[:200])

        # (k) outA/run/sta.tcl contains PT command set
        statcl = open(os.path.join(runA, "sta.tcl")).read()
        for kw in ("read_sdc", "update_timing", "report_timing"):
            assert kw in statcl, "(k) sta.tcl missing PT command: %s" % kw

        # (l) outA/run/Makefile contains pt_shell + bsub (LSF)
        mkA = open(os.path.join(runA, "Makefile")).read()
        assert "pt_shell" in mkA, "(l) A Makefile missing pt_shell"
        assert "bsub" in mkA, "(l) A Makefile missing bsub (LSF)"

        # (m) outA/run/CXDP_STA_CFG contains key STA variables
        cfgA = open(os.path.join(runA, "CXDP_STA_CFG")).read()
        for pat in ("CXDP_DESIGN_NAME=cla_top", "STA_PBA=gbv",
                    "STA_CORNER=", "CXDP_PROJ_TAG=v1.0_Latest"):
            assert pat in cfgA, "(m) A CXDP_STA_CFG missing: %s" % pat

        # (n) outA has README.md + install.sh; bash -n install.sh OK
        assert os.path.isfile(os.path.join(outA, "README.md")), "(n) outA missing README.md"
        instA = os.path.join(outA, "install.sh")
        assert os.path.isfile(instA), "(n) outA missing install.sh"
        rc, out, err = _run("bash -n %s" % instA, outA)
        assert rc == 0, "(n) bash -n on install.sh failed: %s" % (err[:200])

        # (o) report_A.json (in zip) parses JSON with correct A fields
        rpt = json.load(open(os.path.join(tmp, "report_A.json")))
        assert rpt.get("design") == "cla_top", "(o) report_A.json design != cla_top"
        assert rpt.get("tag") == "v1.0_Latest", "(o) report_A.json tag != v1.0_Latest"
        assert rpt.get("pba") == "gbv", "(o) report_A.json pba != gbv"
        assert rpt.get("mcmm") is False, "(o) report_A.json mcmm != false"

        # (p) builder run on B: exit0 + outB/ exists with core subdirs
        outB = tempfile.mkdtemp(prefix="outB_")
        rc, out, err = _run("python3 %s --lint %s --feint %s --out %s"
                            % (builder, B_LINT, B_FEINT, outB), tmp)
        assert rc == 0, "(p) builder on B failed rc=%d err=%s" % (rc, err[:300])
        for d in ("run", "data", "script", "all_out", "config"):
            assert os.path.isdir(os.path.join(outB, d)), \
                "(p) outB missing core subdir: %s" % d

        # (q) cross-input guard: outB design == uart_top (CXDP_STA_CFG)
        cfgB = open(os.path.join(outB, "run", "CXDP_STA_CFG")).read()
        assert "CXDP_DESIGN_NAME=uart_top" in cfgB, \
            "(q) B design != uart_top (not adaptive)"
        assert "CXDP_DESIGN_NAME=cla_top" not in cfgB, \
            "(q) B leaked A design name cla_top"

        # (r) cross-input guard: outB has mcmm/, outA does NOT
        assert os.path.isdir(os.path.join(outB, "mcmm")), \
            "(r) B missing mcmm/ subdir (not adaptive)"
        assert not os.path.isdir(os.path.join(outA, "mcmm")), \
            "(r) A should NOT have mcmm/ but does"

        # (s) cross-input guard: outB PBA == exhaustive, outA PBA == gbv
        stsetupB = open(os.path.join(outB, "run", "sta_setup.tcl")).read()
        assert re.search(r'set\s+PBA\s+exhaustive', stsetupB), \
            "(s) B sta_setup.tcl PBA != exhaustive"
        stsetupA = open(os.path.join(runA, "sta_setup.tcl")).read()
        assert re.search(r'set\s+PBA\s+gbv', stsetupA), \
            "(s) A sta_setup.tcl PBA != gbv"

        # (t) cross-input guard: outB tag == v2.1_Latest, outA tag == v1.0_Latest
        assert os.path.isdir(os.path.join(outB, "all_out", "v2.1_Latest")), \
            "(t) B all_out/v2.1_Latest missing (tag not propagated)"
        assert not os.path.isdir(os.path.join(outB, "all_out", "v1.0_Latest")), \
            "(t) B leaked A tag v1.0_Latest"

        return True
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
'''

def write_check():
    _w(os.path.join(REF, "check.py"), CHECK_SRC)

# ============================================================
# 6. negatives
# ============================================================
NEG_EMPTY = "#!/usr/bin/env python3\n# fake_empty (§4.9a): does nothing\n"
NEG_PRINT = r'''#!/usr/bin/env python3
# fake_print_expected (§4.9b): prints expected A manifest, builds nothing
import sys, json
print(json.dumps({"design":"cla_top","tag":"v1.0_Latest","pba":"gbv",
                  "corner":"typical","mcmm":False,
                  "run_files":[],"data_files":[],"dirs":[]}, indent=2))
'''
NEG_CORE = r'''#!/usr/bin/env python3
# fake_core_deleted (§4.9c): CLI/argparse scaffolding present, build() body deleted
import os, sys, json, argparse

def build(lint_dir, feint_dir, out_dir):
    pass  # core deleted

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lint", required=True)
    ap.add_argument("--feint", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.lint, a.feint, a.out)
    print(json.dumps({"design":"cla_top","tag":"v1.0_Latest","pba":"gbv",
                      "corner":"typical","mcmm":False}, indent=2))

if __name__ == "__main__":
    main()
'''
NEG_HARD = r'''#!/usr/bin/env python3
# naive_hardcode_a: hardcodes cla_top/v1.0_Latest, ignores bundle -> fails B guard
import os, sys, json, argparse

def build(lint_dir, feint_dir, out_dir):
    design, tag, pba, corner = "cla_top", "v1.0_Latest", "gbv", "typical"
    os.makedirs(os.path.join(out_dir, "config"), exist_ok=True)
    _w = lambda p, c: (os.makedirs(os.path.dirname(p), exist_ok=True),
                       open(p, "w").write(c))
    _w(os.path.join(out_dir, "config", "CXDP_DESIGN_CFG"),
       "CXDP_DESIGN_NAME=cla_top\n")
    run = os.path.join(out_dir, "run"); os.makedirs(run, exist_ok=True)
    _w(os.path.join(run, "CXDP_STA_CFG"),
       "CXDP_DESIGN_NAME=cla_top\nCXDP_PROJ_TAG=v1.0_Latest\nSTA_CORNER=typical\nSTA_PBA=gbv\n")
    _w(os.path.join(run, "sta_setup.tcl"), "set PBA gbv\nset corner typical\n")
    _w(os.path.join(run, "sta.tcl"),
       "source sta_setup.tcl\nread_sdc x.sdc\nupdate_timing\nreport_timing\nexit\n")
    _w(os.path.join(run, "Makefile"),
       "PT=pt_shell\nLSF=bsub\nhelp:\n\t@echo hi\nsta_run:\n\t$(LSF) $(PT) -f sta.tcl\n")
    # symlinks so A structural checks pass; B guard still fails (hardcoded design)
    for lk in ("CXDP_DESIGN_CFG", "CXDP_PROJ_CFG"):
        lp = os.path.join(run, lk)
        if os.path.lexists(lp):
            os.remove(lp)
        os.symlink("../config/" + lk, lp)
    data = os.path.join(out_dir, "data"); os.makedirs(data, exist_ok=True)
    _w(os.path.join(data, "cla_top.netlist.f"), "rtl/cla_top.v\n")
    _w(os.path.join(data, "cla_top.sdc"), "create_clock -period 2\n")
    _w(os.path.join(data, "sta_override.tcl"), "set_propagated_clock [all_clocks]\n")
    sc = os.path.join(out_dir, "script"); os.makedirs(sc, exist_ok=True)
    _w(os.path.join(sc, "sta_qa_chk.pl"),
       "#!/usr/bin/perl\nuse strict;use warnings;print 1;exit 0;\n")
    for s in ("filelist","log","out_src","QA","report"):
        os.makedirs(os.path.join(out_dir, "all_out", tag, s), exist_ok=True)
    _w(os.path.join(out_dir, "README.md"), "# STA flow\n")
    _w(os.path.join(out_dir, "install.sh"), "#!/bin/bash\necho hi\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lint", required=True)
    ap.add_argument("--feint", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.lint, a.feint, a.out)
    print(json.dumps({"design":"cla_top","tag":"v1.0_Latest","pba":"gbv",
                      "corner":"typical","mcmm":False}, indent=2))

if __name__ == "__main__":
    main()
'''
NEG_STRUCT = r'''#!/usr/bin/env python3
# fake_structure_only: makes dirs + empty/invalid scripts -> fails perl/tclsh/make
import os, sys, json, argparse

def build(lint_dir, feint_dir, out_dir):
    for d in ("config","run","data","script","all_out/v1.0_Latest/filelist",
              "all_out/v1.0_Latest/log","all_out/v1.0_Latest/out_src",
              "all_out/v1.0_Latest/QA","all_out/v1.0_Latest/report"):
        os.makedirs(os.path.join(out_dir, d), exist_ok=True)
    _w = lambda p, c: (os.makedirs(os.path.dirname(p), exist_ok=True),
                       open(p, "w").write(c))
    # empty scripts (no valid syntax)
    _w(os.path.join(out_dir, "script", "sta_qa_chk.pl"), "")
    _w(os.path.join(out_dir, "run", "sta.tcl"), "if {1} {\n")  # unbalanced
    _w(os.path.join(out_dir, "run", "sta_setup.tcl"), "if {1} {\n")  # unbalanced
    _w(os.path.join(out_dir, "run", "Makefile"), "help:\n\tbroken$(\n")
    _w(os.path.join(out_dir, "run", "CXDP_STA_CFG"),
       "CXDP_DESIGN_NAME=cla_top\nSTA_PBA=gbv\nCXDP_PROJ_TAG=v1.0_Latest\n")
    _w(os.path.join(out_dir, "data", "cla_top.netlist.f"), "rtl/x.v\n")
    _w(os.path.join(out_dir, "data", "cla_top.sdc"), "create_clock\n")
    _w(os.path.join(out_dir, "data", "sta_override.tcl"), "set x 1\n")
    _w(os.path.join(out_dir, "install.sh"), "#!/bin/bash\necho hi\n")
    _w(os.path.join(out_dir, "README.md"), "# x\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lint", required=True)
    ap.add_argument("--feint", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.lint, a.feint, a.out)
    print(json.dumps({"design":"cla_top","tag":"v1.0_Latest","pba":"gbv",
                      "corner":"typical","mcmm":False}, indent=2))

if __name__ == "__main__":
    main()
'''

def write_negatives():
    _w(os.path.join(NEG, "fake_empty.py"), NEG_EMPTY)
    _w(os.path.join(NEG, "fake_print_expected.py"), NEG_PRINT)
    _w(os.path.join(NEG, "fake_core_deleted.py"), NEG_CORE)
    _w(os.path.join(NEG, "naive_hardcode_a.py"), NEG_HARD)
    _w(os.path.join(NEG, "fake_structure_only.py"), NEG_STRUCT)

# negative_selftest.py
NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py - all 5 negatives + §4.9 fakes must FAIL check().
Each negative is packaged as submit.zip (with a stub report_A.json) and run
through check.py; expected: every one raises (FAIL). Exit 0 iff all FAIL.
"""
import os, sys, json, zipfile, tempfile, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REF = HERE
NEG = os.path.join(REF, "negative")

def _make_submit(builder_src, tmp):
    bp = os.path.join(tmp, "build_sta_flow.py")
    open(bp, "w").write(builder_src)
    # produce a stub report_A.json (for (a)/(o))
    rpt = {"design":"cla_top","tag":"v1.0_Latest","pba":"gbv",
           "corner":"typical","mcmm":False,
           "run_files":[],"data_files":[],"dirs":[]}
    rp = os.path.join(tmp, "report_A.json")
    open(rp, "w").write(json.dumps(rpt))
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.write(bp, "build_sta_flow.py")
        z.write(rp, "report_A.json")
    return zp

def _run_check(zp):
    wd = tempfile.mkdtemp(prefix="neg_wd_")
    try:
        r = subprocess.run([sys.executable, os.path.join(REF, "check.py")],
                           cwd=wd, capture_output=True, text=True, timeout=180,
                           input="")
        # check.py is imported; use it directly
        sys.path.insert(0, REF)
        import importlib
        if "check" in sys.modules:
            del sys.modules["check"]
        import check as ck
        try:
            # place submit.zip in wd
            shutil.copy(zp, os.path.join(wd, "outputs", "submit.zip") if False
                        else os.path.join(wd, "submit.zip"))
            os.makedirs(os.path.join(wd, "outputs"), exist_ok=True)
            shutil.copy(zp, os.path.join(wd, "outputs", "submit.zip"))
            res = ck.check("outputs/submit.zip", wd)
            return res, ""
        except Exception as e:
            return None, str(e)
        finally:
            sys.path.pop(0)
            if "check" in sys.modules:
                del sys.modules["check"]
    finally:
        shutil.rmtree(wd, ignore_errors=True)

def main():
    negs = ["fake_empty.py", "fake_print_expected.py", "fake_core_deleted.py",
            "naive_hardcode_a.py", "fake_structure_only.py"]
    results = {}
    for n in negs:
        src = open(os.path.join(NEG, n)).read()
        tmp = tempfile.mkdtemp(prefix="neg_build_")
        try:
            zp = _make_submit(src, tmp)
            res, err = _run_check(zp)
            results[n] = (res, err)
            status = "FAIL-OK" if res is None else "!!! PASS (BAD) !!!"
            first_cond = err.splitlines()[0][:120] if err else ""
            print("%-28s -> %s  [%s]" % (n, status, first_cond))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    bad = [n for n, (r, _) in results.items() if r is True]
    if bad:
        print("\nNEG_RC=1 -- negatives that PASSED (should FAIL):", bad)
        sys.exit(1)
    print("\nNEG_RC=0 -- all %d negatives FAIL as expected" % len(negs))

if __name__ == "__main__":
    main()
'''

def write_selftest():
    _w(os.path.join(REF, "negative_selftest.py"), NEG_SELFTEST)

# ============================================================
# 7. build reference_submit.zip + report_A.json, self-verify
# ============================================================
def make_reference_and_verify():
    builder = os.path.join(REF, "build_sta_flow.py")
    # run builder on A -> capture stdout as report_A.json
    outA = tempfile.mkdtemp(prefix="ref_outA_")
    try:
        r = subprocess.run([sys.executable, builder, "--lint", A_LINT,
                            "--feint", A_FEINT, "--out", outA],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, "ref builder on A failed: %s" % r.stderr
        report_A = r.stdout
        _w(os.path.join(REF, "report_A.json"), report_A)
        # build reference_submit.zip
        zp = os.path.join(REF, "reference_submit.zip")
        if os.path.exists(zp):
            os.remove(zp)
        with zipfile.ZipFile(zp, "w") as z:
            z.write(builder, "build_sta_flow.py")
            z.write(os.path.join(REF, "report_A.json"), "report_A.json")
        print("[ref] reference_submit.zip built (%d bytes)" % os.path.getsize(zp))
        return zp
    finally:
        shutil.rmtree(outA, ignore_errors=True)

def run_check_on(zip_path, label):
    """Run check() in-process on a submit.zip placed in a temp workdir."""
    wd = tempfile.mkdtemp(prefix="chk_wd_")
    try:
        os.makedirs(os.path.join(wd, "outputs"), exist_ok=True)
        shutil.copy(zip_path, os.path.join(wd, "outputs", "submit.zip"))
        sys.path.insert(0, REF)
        if "check" in sys.modules:
            del sys.modules["check"]
        import check as ck
        try:
            res = ck.check("outputs/submit.zip", wd)
            print("[%-12s] check() -> PASS (returned %s)" % (label, res))
            return True, ""
        except AssertionError as e:
            print("[%-12s] check() -> FAIL: %s" % (label, str(e)[:200]))
            return False, str(e)
        except Exception as e:
            print("[%-12s] check() -> ERROR: %s" % (label, str(e)[:200]))
            return False, str(e)
        finally:
            sys.path.pop(0)
            if "check" in sys.modules:
                del sys.modules["check"]
    finally:
        shutil.rmtree(wd, ignore_errors=True)

# ============================================================
# main
# ============================================================
def main():
    print("=== build A bundle ===")
    build_A_bundle()
    print("=== build B hidden bundle ===")
    build_B_bundle()
    print("=== write prompt + task_brief ===")
    build_prompt()
    print("=== write reference build_sta_flow.py ===")
    write_builder()
    print("=== write check.py ===")
    write_check()
    print("=== write negatives + selftest ===")
    write_negatives()
    write_selftest()

    print("=== build reference_submit.zip + report_A.json ===")
    zp = make_reference_and_verify()

    print("\n=== self-verify: reference must PASS ===")
    ok, err = run_check_on(zp, "reference")
    if not ok:
        print("!!! REFERENCE FAILED -- aborting"); sys.exit(1)

    print("\n=== self-verify: §4.9 + negatives must FAIL ===")
    negs = ["fake_empty.py", "fake_print_expected.py", "fake_core_deleted.py",
            "naive_hardcode_a.py", "fake_structure_only.py"]
    all_fail = True
    for n in negs:
        src = open(os.path.join(NEG, n)).read()
        tmp = tempfile.mkdtemp(prefix="negzip_")
        try:
            bp = os.path.join(tmp, "build_sta_flow.py"); open(bp, "w").write(src)
            rpt = {"design":"cla_top","tag":"v1.0_Latest","pba":"gbv",
                   "corner":"typical","mcmm":False}
            rp = os.path.join(tmp, "report_A.json")
            open(rp, "w").write(json.dumps(rpt))
            nzp = os.path.join(tmp, "submit.zip")
            with zipfile.ZipFile(nzp, "w") as z:
                z.write(bp, "build_sta_flow.py"); z.write(rp, "report_A.json")
            ok, err = run_check_on(nzp, n)
            if ok:
                all_fail = False
                print("  !!! %s PASSED (should FAIL)" % n)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if not all_fail:
        print("!!! SOME NEGATIVES PASSED -- aborting"); sys.exit(1)
    print("  all 5 negatives FAIL as expected (NEG_RC=0)")

    print("\n=== count assertions ===")
    # count check.py labeled conditions (a)-(t)
    check_src = open(os.path.join(REF, "check.py")).read()
    labels = re.findall(r'# \(([a-z])\)', check_src)
    k_check = len(labels)
    print("check.py labels:", labels)
    print("k_check =", k_check)

    print("\n=== BUILD COMPLETE ===")
    print("A.jsonl NOT yet appended -- run _append_staflow_001.py next")

if __name__ == "__main__":
    main()
