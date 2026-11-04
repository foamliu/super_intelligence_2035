#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build + self-verify + append EDA-Eval-DesignFlow-HierDcSynth-001 (shard A).

Case: combinational design + PrimeLib stdcells spec -> hierarchy-preserving
DC synthesis synth.tcl generator (avoid the set_dont_touch-on-submodules
GTECH-unmapped bug; no ungroup/flatten).
Verb: hier-preserving-dc-synth-flow (digital, B-grade synthesized, A-grade
faithful task statement verbatim from trace uh82d USER turn).
Real assets (johnl addr_to_rowcol_region DC synth flow) readable but span
multiple v6/v7 iterations + a continuation session -> synthesized faithful
spec bundles A + hidden B capturing the real synth.tcl structure
(LVS-only cell filter, combinational guard, virtual clock + IO delays,
hierarchy preservation, reports, write netlist/sdc).
"""
import os, sys, json, re, zipfile, shutil, subprocess, tempfile, py_compile

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-HierDcSynth-001"
A_DIR = os.path.join(BENCH, "assets", CID)
HID = os.path.join(A_DIR, "hidden")
REF = os.path.join(BENCH, "reference", CID)
NEG = os.path.join(REF, "negative")
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
for d in (A_DIR, HID, REF, NEG):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- specs
SPEC_A = {
    "top": "addr_dec_A", "rtl": "rtl_A.v", "lib": "stdcells_A.db",
    "submodules": ["reg0_calc_A", "reg1_calc_A", "decode_A", "mux_A"],
    "clock": {"name": "vclk", "period_ns": 1.0},
    "max_delay_ns": 0.5, "max_transition_ns": 0.1, "load_pf": 0.005,
    "input_transition_ns": 0.02, "lvs_only": True,
    "combinational_only": True,
    "reports": ["timing", "area", "qor", "references", "check_design", "constraints"],
}
SPEC_B = {
    "top": "addr_map_B", "rtl": "rtl_B.v", "lib": "stdcells_B.db",
    "submodules": ["sel_b", "encode_b", "arb_b"],
    "clock": {"name": "ick", "period_ns": 1.6},
    "max_delay_ns": 0.8, "max_transition_ns": 0.12, "load_pf": 0.004,
    "input_transition_ns": 0.025, "lvs_only": True,
    "combinational_only": True,
    "reports": ["timing", "area", "qor", "references", "check_design"],
}

RTL_A = """// Combinational address decoder with hierarchical submodules.
// top: addr_dec_A ; submodules: reg0_calc_A, reg1_calc_A, decode_A, mux_A
module addr_dec_A (
    input  [7:0] addr,
    input        sel,
    output [4:0] row,
    output [4:0] col,
    output       valid
);
    wire [4:0] reg0_q, reg1_q, dec_out, mux_out;
    reg0_calc_A u_reg0 (.addr(addr), .sel(sel), .q(reg0_q));
    reg1_calc_A u_reg1 (.addr(addr), .sel(sel), .q(reg1_q));
    decode_A    u_dec  (.in({reg0_q, reg1_q}), .out(dec_out));
    mux_A       u_mux  (.a(dec_out), .b(reg1_q), .s(sel), .y(mux_out));
    assign row   = mux_out;
    assign col   = reg0_q ^ reg1_q;
    assign valid = |addr;
endmodule

module reg0_calc_A (input [7:0] addr, input sel, output reg [4:0] q);
  always @* q = addr[4:0] ^ {4'b0, sel};
endmodule
module reg1_calc_A (input [7:0] addr, input sel, output reg [4:0] q);
  always @* q = addr[7:5] + addr[4:0];
endmodule
module decode_A (input [9:0] in, output reg [4:0] out);
  always @* out = in[4:0] | in[9:5];
endmodule
module mux_A (input [4:0] a, input [4:0] b, input s, output reg [4:0] y);
  always @* y = s ? a : b;
endmodule
"""

RTL_B = """// Combinational address mapper with hierarchical submodules.
// top: addr_map_B ; submodules: sel_b, encode_b, arb_b
module addr_map_B (
    input  [6:0] a,
    input        en,
    output [3:0] code,
    output       v
);
    wire [3:0] s, e, ar;
    sel_b    u_sel (.a(a), .en(en), .y(s));
    encode_b u_enc (.a(a), .y(e));
    arb_b    u_arb (.req(s), .gnt(ar));
    assign code = e | ar;
    assign v    = |a & en;
endmodule

module sel_b (input [6:0] a, input en, output reg [3:0] y);
  always @* y = a[3:0] & {4{en}};
endmodule
module encode_b (input [6:0] a, output reg [3:0] y);
  always @* y = a[6:3] ^ a[2:0];
endmodule
module arb_b (input [3:0] req, output reg [3:0] gnt);
  always @* gnt = req & ~(req - 4'd1);
endmodule
"""

# ---------------------------------------------------------------- generator (reference)
GEN_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_synth_tcl.py - Hierarchy-preserving DC synthesis script generator.

Reads a JSON spec describing a combinational design (top, rtl path, library,
submodules, clock, delays, LVS-only cell filter, combinational-only guard,
report list) and emits a Synopsys Design Compiler synth.tcl that PRESERVES
hierarchy (no ungroup / no set_flatten) and does NOT set_dont_touch on
submodules (avoids the unmapped-GTECH bug), while restricting mapping to
*LVS* library cells, applying a virtual clock + IO delays, guarding that the
RTL is purely combinational, and writing reports + netlist + sdc.

CLI:  python3 gen_synth_tcl.py --spec <spec.json> -o <out.tcl>
"""
import sys, json, argparse


def emit(spec):
    top = spec["top"]
    rtl = spec["rtl"]
    lib = spec["lib"]
    clk = spec.get("clock", {}) or {}
    clk_name = clk.get("name", "virtual_clock")
    clk_period = float(clk.get("period_ns", 1.0))
    max_delay = float(spec.get("max_delay_ns", 0.5))
    max_tran = float(spec.get("max_transition_ns", 0.1))
    load = float(spec.get("load_pf", 0.005))
    in_tran = float(spec.get("input_transition_ns", 0.02))
    lvs_only = bool(spec.get("lvs_only", True))
    comb_only = bool(spec.get("combinational_only", True))
    reports = spec.get("reports", ["timing", "area", "qor", "references"])
    L = []
    L.append("# Hierarchy-preserving DC synthesis script (generated).")
    L.append("# Top-level hierarchy is kept; submodules mapped to target library.")
    L.append("# Submodules are mapped to library cells (no preserve-as-is).")
    L.append("set TOP %s" % top)
    L.append("set RTL %s" % rtl)
    L.append("set LIB %s" % lib)
    L.append("set_app_var sh_continue_on_error false")
    L.append("set_app_var target_library [list $LIB]")
    L.append("set_app_var link_library [concat * $target_library]")
    L.append("file mkdir out")
    L.append("file mkdir out/work")
    L.append("define_design_lib WORK -path out/work")
    L.append("analyze -format verilog %s" % rtl)
    L.append("elaborate %s" % top)
    L.append("current_design %s" % top)
    L.append("link")
    if comb_only:
        L.append("if {[sizeof_collection [all_registers]] != 0} {")
        L.append('    error "Sequential element found; this flow accepts combinational RTL only"')
        L.append("}")
    if lvs_only:
        L.append("set LVS_CELLS [get_lib_cells -quiet */*LVS*]")
        L.append("if {[sizeof_collection $LVS_CELLS] == 0} {")
        L.append('    error "The target library contains no *LVS* cells"')
        L.append("}")
        L.append("set LVS_LIB_NAMES [list]")
        L.append("foreach_in_collection cell $LVS_CELLS {")
        L.append("    lappend LVS_LIB_NAMES [lindex [split [get_object_name $cell] /] 0]")
        L.append("}")
        L.append("set LVS_LIB_NAMES [lsort -unique $LVS_LIB_NAMES]")
        L.append("set NON_LVS_NAMES [list]")
        L.append("foreach lib_name $LVS_LIB_NAMES {")
        L.append("    foreach_in_collection cell [get_lib_cells -quiet ${lib_name}/*] {")
        L.append("        set full_name [get_object_name $cell]")
        L.append("        set cell_name [lindex [split $full_name /] end]")
        L.append("        if {![string match *LVS* $cell_name]} {")
        L.append("            lappend NON_LVS_NAMES $full_name")
        L.append("        }")
        L.append("    }")
        L.append("}")
        L.append("set_attribute $LVS_CELLS dont_use false")
        L.append("if {[llength $NON_LVS_NAMES] != 0} {")
        L.append("    set_dont_use [get_lib_cells $NON_LVS_NAMES]")
        L.append("}")
    L.append("set_units -time ns -resistance kOhm -capacitance pF -voltage V -current mA")
    L.append("set_max_transition %.4f [current_design]" % max_tran)
    L.append("set_max_area 0")
    L.append("set_load -pin_load %.4f [all_outputs]" % load)
    L.append("set_input_transition -max %.4f [all_inputs]" % in_tran)
    L.append("set_input_transition -min %.4f [all_inputs]" % in_tran)
    L.append("create_clock -name %s -period %.4f" % (clk_name, clk_period))
    L.append("set_input_delay 0.0 -clock %s [all_inputs]" % clk_name)
    L.append("set_output_delay 0.0 -clock %s [all_outputs]" % clk_name)
    L.append("set_max_delay %.4f -from [all_inputs] -to [all_outputs]" % max_delay)
    L.append("compile_ultra")
    L.append('set unmapped [get_cells -hierarchical -quiet -filter "is_unmapped == true"]')
    L.append("if {[sizeof_collection $unmapped] != 0} {")
    L.append('    error "Mapping left unmapped cells"')
    L.append("}")
    if lvs_only:
        L.append("set NON_LVS_REFS [list]")
        L.append('foreach_in_collection cell [get_cells -hierarchical -quiet -filter "is_hierarchical == false"] {')
        L.append("    set ref_name [get_attribute $cell ref_name]")
        L.append('    if {$ref_name ne "**logic_0**" && $ref_name ne "**logic_1**" && ![string match *LVS* $ref_name]} {')
        L.append("        lappend NON_LVS_REFS $ref_name")
        L.append("    }")
        L.append("}")
        L.append("if {[llength $NON_LVS_REFS] != 0} {")
        L.append('    error "Final netlist contains non-LVS cells"')
        L.append("}")
    repmap = {
        "timing": "report_timing -delay_type max -from [all_inputs] -to [all_outputs] -max_paths 20",
        "area": "report_area",
        "qor": "report_qor",
        "references": "report_reference",
        "check_design": "check_design",
        "constraints": "report_constraint -all_violators",
    }
    for r in reports:
        if r in repmap:
            L.append("redirect out/%s.rpt { %s }" % (r, repmap[r]))
    L.append("change_names -rules verilog -hierarchy")
    L.append("write -format verilog -hierarchy -output out/mapped.v")
    L.append("write -format ddc -hierarchy -output out/mapped.ddc")
    L.append("write_sdc out/mapped.sdc")
    L.append("quit")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()
    with open(args.spec) as f:
        spec = json.load(f)
    tcl = emit(spec)
    with open(args.output, "w") as f:
        f.write(tcl)


if __name__ == "__main__":
    main()
'''

# ---------------------------------------------------------------- check.py
CHECK_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py - grader for EDA-Eval-DesignFlow-HierDcSynth-001.

Deliverable: submit.zip containing gen_synth_tcl.py (generic hierarchy-
preserving DC synth.tcl generator, CLI `--spec <spec.json> -o <out.tcl>`,
pure stdlib) and synth_A.tcl (precomputed tcl for A bundle).

Judgment: runs candidate's gen_synth_tcl.py on visible A and hidden B
(subprocess, real python3), parses the emitted synth.tcl, and asserts 19
independent structural conditions (a)-(s) covering: zip contents, py_compile,
real run on A, tclsh info complete, analyze/elaborate/current_design/link,
hierarchy preservation (no ungroup/set_flatten), no set_dont_touch on
submodules (anti GTECH bug), compile_ultra, LVS-only cell filter,
combinational guard, virtual clock + IO delays, reports, write netlist/sdc,
real run on B, cross-input guard (B top != A, no A submodule names, B clock
differs), anti-hardcode (generator source free of A/B literals), and
determinism (3 runs byte-identical).
"""
import os, re, sys, json, zipfile, subprocess, tempfile, py_compile, shutil

CID = "EDA-Eval-DesignFlow-HierDcSynth-001"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CID))
A_SPEC = os.path.join(ASSETS, "spec_A.json")
B_SPEC = os.path.join(ASSETS, "hidden", "spec_B.json")

A_TOP = "addr_dec_A"
B_TOP = "addr_map_B"
A_SUBS = ["reg0_calc_A", "reg1_calc_A", "decode_A", "mux_A"]
A_CLK = ("vclk", "1.0000")
B_CLK = ("ick", "1.6000")
FORBIDDEN_LITERALS = ["addr_dec_A", "addr_map_B", "reg0_calc_A", "reg1_calc_A",
                      "decode_A", "mux_A", "sel_b", "encode_b", "arb_b",
                      "stdcells_A.db", "stdcells_B.db", "vclk", "ick"]


def _run(cmd, cwd, timeout=120):
    try:
        r = subprocess.run(["bash", "-lc", cmd], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def _tclsh_info_complete(tcl_path, tmpdir):
    """Return 1 if tclsh says the file is a complete script, 0 if not,
    -1 if tclsh is unavailable (caller falls back to brace balance)."""
    probe = os.path.join(tmpdir, "_probe.tcl")
    with open(probe, "w") as f:
        f.write('set f [open "%s"]; set c [read $f]; close $f; '
                'puts "IC=[info complete $c]"; exit\n' % tcl_path)
    rc, out, _ = _run("tclsh %s" % probe, tmpdir, timeout=30)
    if rc != 0:
        return -1
    m = re.search(r"IC=(\d)", out)
    return int(m.group(1)) if m else -1


def _brace_balance(text):
    depth = 0
    for ch in text:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def check(deliverable, workdir):
    """Return True on PASS, raise AssertionError with the failing label on FAIL."""
    if not os.path.isfile(deliverable):
        raise AssertionError("a: deliverable not a file")
    tmp = tempfile.mkdtemp(prefix="chk_hierdcsynth_")
    try:
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            z.extractall(tmp)
        base_names = set(os.path.basename(n) for n in names if not n.endswith("/"))
        assert ("gen_synth_tcl.py" in base_names and
                "synth_A.tcl" in base_names and len(base_names) == 2), \
            "a: submit.zip must contain exactly gen_synth_tcl.py + synth_A.tcl"
        gen_path = os.path.join(tmp, "gen_synth_tcl.py")

        # b) py_compile
        try:
            py_compile.compile(gen_path, doraise=True)
        except Exception as e:
            raise AssertionError("b: gen_synth_tcl.py py_compile failed: %s" % e)

        def run_gen(spec_path, out_name):
            out_path = os.path.join(tmp, out_name)
            rc, out, err = _run("python3 gen_synth_tcl.py --spec %s -o %s" % (spec_path, out_name), tmp, timeout=60)
            return rc, out, err, out_path

        # c) run candidate on A
        rc, out, err, sA = run_gen(A_SPEC, "sA.tcl")
        assert rc == 0 and os.path.isfile(sA) and os.path.getsize(sA) > 0, \
            "c: candidate run on A failed (rc=%d err=%s)" % (rc, err[:200])
        tA = open(sA, encoding="utf-8", errors="replace").read()

        # d) tclsh info complete (real tclsh; fallback brace balance)
        ic = _tclsh_info_complete(sA, tmp)
        if ic == 0:
            raise AssertionError("d: A synth.tcl tclsh info complete == 0")
        if ic == -1:
            assert _brace_balance(tA), "d: tclsh unavailable and brace balance failed"

        # e) analyze -format verilog + rtl path
        assert "analyze -format verilog" in tA and "rtl_A.v" in tA, \
            "e: A synth.tcl missing analyze -format verilog / rtl path"

        # f) elaborate + current_design + link
        assert ("elaborate %s" % A_TOP) in tA and ("current_design %s" % A_TOP) in tA and "link" in tA, \
            "f: A synth.tcl missing elaborate/current_design/link for %s" % A_TOP

        # g) hierarchy preserved: no ungroup -all, no set_flatten
        assert "ungroup -all" not in tA and "set_flatten" not in tA, \
            "g: A synth.tcl flattens hierarchy (ungroup -all / set_flatten present)"

        # h) no set_dont_touch on submodules (anti GTECH-unmapped bug)
        assert "set_dont_touch" not in tA, \
            "h: A synth.tcl contains set_dont_touch (causes unmapped GTECH submodules)"

        # i) compile_ultra present
        assert "compile_ultra" in tA, "i: A synth.tcl missing compile_ultra"

        # j) LVS-only cell filter
        assert "get_lib_cells -quiet */*LVS*" in tA and "set_dont_use" in tA, \
            "j: A synth.tcl missing LVS-only cell filter (get_lib_cells *LVS* / set_dont_use)"

        # k) combinational guard
        assert "all_registers" in tA and "error" in tA, \
            "k: A synth.tcl missing combinational-only guard (all_registers/error)"

        # l) virtual clock + IO delays + max_delay
        assert ("create_clock -name %s -period %s" % A_CLK) in tA and \
               "set_input_transition" in tA and "set_load" in tA and \
               "set_max_delay" in tA, \
            "l: A synth.tcl missing clock/IO-delay constraints"

        # m) reports: timing + area + qor + references
        assert "report_timing" in tA and "report_area" in tA and \
               "report_qor" in tA and "report_reference" in tA, \
            "m: A synth.tcl missing report_timing/area/qor/references"

        # n) write netlist + sdc
        assert "write -format verilog" in tA and "write_sdc" in tA, \
            "n: A synth.tcl missing write -format verilog / write_sdc"

        # o) run candidate on B (real B run)
        rc, out, err, sB = run_gen(B_SPEC, "sB.tcl")
        assert rc == 0 and os.path.isfile(sB) and os.path.getsize(sB) > 0, \
            "o: candidate run on B failed (rc=%d err=%s)" % (rc, err[:200])
        tB = open(sB, encoding="utf-8", errors="replace").read()

        # p) cross-input guard: B top == addr_map_B, no A submodule names
        assert ("elaborate %s" % B_TOP) in tB and ("current_design %s" % B_TOP) in tB, \
            "p: B synth.tcl missing elaborate/current_design for %s" % B_TOP
        assert not any(sub in tB for sub in A_SUBS), \
            "p: B synth.tcl leaked A submodule names (cross-input guard)"

        # q) cross-input guard: B clock differs from A
        assert ("create_clock -name %s -period %s" % B_CLK) in tB, \
            "q: B synth.tcl clock != ick/1.6 (cross-input guard)"

        # r) anti-hardcode: generator source free of A/B literals
        src = open(gen_path, encoding="utf-8", errors="replace").read()
        leaked = [lit for lit in FORBIDDEN_LITERALS if lit in src]
        assert not leaked, \
            "r: gen_synth_tcl.py source leaks A/B literals: %s" % leaked

        # s) determinism: 3 runs on A byte-identical
        outs = []
        for i in range(3):
            rc, _, _, sp = run_gen(A_SPEC, "sA_%d.tcl" % i)
            assert rc == 0 and os.path.isfile(sp), "s: run %d failed" % i
            outs.append(open(sp, encoding="utf-8", errors="replace").read())
        assert outs[0] == outs[1] == outs[2], "s: 3 runs on A not byte-identical"

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        try:
            ok = check(sys.argv[1], sys.argv[2])
            print("PASS" if ok else "FAIL")
            sys.exit(0 if ok else 1)
        except AssertionError as e:
            print("FAIL:", e)
            sys.exit(1)
    else:
        print("usage: check.py <submit.zip> <workdir>")
        sys.exit(2)
'''

# ---------------------------------------------------------------- write assets
def w(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

w(os.path.join(A_DIR, "spec_A.json"), json.dumps(SPEC_A, indent=2))
w(os.path.join(A_DIR, "rtl_A.v"), RTL_A)
w(os.path.join(HID, "spec_B.json"), json.dumps(SPEC_B, indent=2))
w(os.path.join(HID, "rtl_B.v"), RTL_B)
w(os.path.join(REF, "gen_synth_tcl.py"), GEN_PY)
w(os.path.join(REF, "check.py"), CHECK_PY)

PROMPT = """为一块组合地址解码芯片（顶层 `addr_dec_A`，含 4 个层次化子模块 reg0_calc_A / reg1_calc_A / decode_A / mux_A，使用 PrimeLib 表征的 stdcells 库 stdcells_A.db，仅允许使用名字含 "LVS" 的库单元）生成一份**层次保留**的 Synopsys Design Compiler 综合脚本 synth.tcl（digital, DC 综合流程）。

要求（忠实复刻真实 DC 综合流程的约束与守卫）：
- 保留顶层层次结构：**不要** `ungroup`、**不要** `set_flatten`；让 `compile_ultra` 把子模块映射到目标库。
- **不要**对子模块设 `set_dont_touch`（否则子模块保持 unmapped 的 GTECH/层次单元，无法映射到 LVS 单元）。
- 仅允许使用名字含 `LVS` 的库单元：用 `get_lib_cells -quiet */*LVS*` 收集 LVS 单元，对非 LVS 单元 `set_dont_use`。
- 组合电路守卫：若 `all_registers` 非空则 `error` 退出（本流程只接受组合 RTL）。
- 虚拟时钟 `vclk` 周期 1.0 ns + `set_input_delay`/`set_output_delay` 绑 vclk + `set_max_delay 0.5 -from [all_inputs] -to [all_outputs]` + `set_max_transition 0.1` + `set_load -pin_load 0.005 [all_outputs]` + `set_input_transition 0.020 [all_inputs]`。
- `analyze -format verilog rtl_A.v` → `elaborate addr_dec_A` → `current_design addr_dec_A` → `link`。
- 综合后守卫：`get_cells -hierarchical -filter "is_unmapped == true"` 为空，否则 error；非 LVS 引用检查。
- 重定向报告：timing / area / qor / references / check_design / constraints。
- `change_names -rules verilog -hierarchy` + `write -format verilog -hierarchy -output out/mapped.v` + `write_sdc out/mapped.sdc`。

交付：一个通用的生成器 `gen_synth_tcl.py`（CLI `--spec <spec.json> -o <out.tcl>`，纯标准库，从 spec 读 top/rtl/lib/子模块/时钟/约束，生成上述 synth.tcl；**不要**硬编码任何设计专有字面量），以及用它对附件 `spec_A.json` 生成的 `synth_A.tcl`。把两者打包成 `outputs/submit.zip`。

用户原话（逐字，A 档 faithful，trace 1790219837415_uh82d / johnl @ hfeg0pfn119，用户轮，粘入先前 glm-5.2 对话转录后）：
「注意要保留层次进行综合」
「你看下生存到报考我没看到时序报告」
「继续」
（真实资产：/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/ 下 synth.tcl/run_dc.sh/rtl/addr_to_rowcol_region.v/out/reports/*；真实设计 addr_to_rowcol_region 含 6 个层次子模块，先前脚本因对子模块 set_dont_touch 导致 references_post 中 6 个子模块以 `h` 属性未映射，修复 = 移除子模块 dont_touch 但仍保留层次。）
"""

TASK_BRIEF = """# 交付接口
- 交付物：`outputs/submit.zip`，内含 `gen_synth_tcl.py`（生成器）+ `synth_A.tcl`（对 spec_A.json 的产物）。
- 生成器 CLI：`python3 gen_synth_tcl.py --spec <spec.json> -o <out.tcl>`，纯标准库。
- 可见输入：`assets/EDA-Eval-DesignFlow-HierDcSynth-001/spec_A.json` + `rtl_A.v`。
"""
w(os.path.join(A_DIR, "prompt.txt"), PROMPT)
w(os.path.join(A_DIR, "task_brief.md"), TASK_BRIEF)

# ---------------------------------------------------------------- negatives
NEG_FAKES = {
    "fake_empty.py": "# empty generator\n",
    "fake_print_expected.py": (
        "import sys\n"
        "TCL='# hardcoded A synth.tcl\\nset TOP addr_dec_A\\nset RTL rtl_A.v\\n"
        "set LIB stdcells_A.db\\nelaborate addr_dec_A\\ncurrent_design addr_dec_A\\n"
        "compile_ultra\\ncreate_clock -name vclk -period 1.0000\\n"
        "write -format verilog -output out/mapped.v\\nwrite_sdc out/mapped.sdc\\nquit\\n'\n"
        "import argparse\n"
        "ap=argparse.ArgumentParser();ap.add_argument('--spec');ap.add_argument('-o',dest='output');a=ap.parse_args()\n"
        "open(a.output,'w').write(TCL)\n"
    ),
    "fake_core_deleted.py": (
        "import sys,json,argparse\n"
        "def emit(s):\n"
        "    L=['# no compile_ultra, no LVS filter','set TOP '+s['top'],'set RTL '+s['rtl'],\n"
        "       'set LIB '+s['lib'],'analyze -format verilog $RTL','elaborate $TOP',\n"
        "       'current_design $TOP','link','create_clock -name '+s['clock']['name'],\n"
        "       'set_max_delay 0.5 -from [all_inputs] -to [all_outputs]',\n"
        "       'write -format verilog -output out/mapped.v','write_sdc out/mapped.sdc','quit']\n"
        "    return '\\n'.join(L)+'\\n'\n"
        "ap=argparse.ArgumentParser();ap.add_argument('--spec');ap.add_argument('-o',dest='output');a=ap.parse_args()\n"
        "open(a.output,'w').write(emit(json.load(open(a.spec))))\n"
    ),
    "naive_hardcode_a.py": (
        "import sys,argparse\n"
        "# hardcodes A top/submodules (ignores spec top)\n"
        "TCL='# naive hardcode addr_dec_A\\nset TOP addr_dec_A\\nset RTL rtl_A.v\\n"
        "set LIB stdcells_A.db\\nanalyze -format verilog $RTL\\nelaborate addr_dec_A\\n"
        "current_design addr_dec_A\\nlink\\ncompile_ultra\\n"
        "create_clock -name vclk -period 1.0000\\nset_max_delay 0.5 -from [all_inputs] -to [all_outputs]\\n"
        "report_timing\\nreport_area\\nreport_qor\\nreport_reference\\n"
        "write -format verilog -output out/mapped.v\\nwrite_sdc out/mapped.sdc\\nquit\\n'\n"
        "ap=argparse.ArgumentParser();ap.add_argument('--spec');ap.add_argument('-o',dest='output');a=ap.parse_args()\n"
        "open(a.output,'w').write(TCL)\n"
    ),
    "naive_flatten.py": (
        "import sys,json,argparse\n"
        "def emit(s):\n"
        "    L=['# naive flatten (the bug)','set TOP '+s['top'],'set RTL '+s['rtl'],\n"
        "       'set LIB '+s['lib'],'analyze -format verilog $RTL','elaborate $TOP',\n"
        "       'current_design $TOP','link','set_flatten true','ungroup -all -flatten',\n"
        "       'compile_ultra -area_high_effort_script',\n"
        "       'create_clock -name '+s['clock']['name']+' -period %.4f'%float(s['clock']['period_ns']),\n"
        "       'set_max_delay 0.5 -from [all_inputs] -to [all_outputs]',\n"
        "       'report_timing\\nreport_area\\nreport_qor\\nreport_reference',\n"
        "       'write -format verilog -output out/mapped.v','write_sdc out/mapped.sdc','quit']\n"
        "    return '\\n'.join(L)+'\\n'\n"
        "ap=argparse.ArgumentParser();ap.add_argument('--spec');ap.add_argument('-o',dest='output');a=ap.parse_args()\n"
        "open(a.output,'w').write(emit(json.load(open(a.spec))))\n"
    ),
}
for name, body in NEG_FAKES.items():
    w(os.path.join(NEG, name), body)

# negative_selftest.py
NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run check.py against the reference (must PASS) and all negatives (must FAIL)."""
import os, sys, zipfile, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(HERE)
CHECK = os.path.join(REF, "check.py")
GEN = os.path.join(REF, "gen_synth_tcl.py")
CID = "EDA-Eval-DesignFlow-HierDcSynth-001"
ASSETS = os.path.normpath(os.path.join(REF, "..", "..", "assets", CID))
A_SPEC = os.path.join(ASSETS, "spec_A.json")


def make_zip(gen_py_path, tcl_name, tcl_content, zpath):
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(gen_py_path, "gen_synth_tcl.py")
        z.writestr(tcl_name, tcl_content)


def run_check(zpath):
    r = subprocess.run(["python3", CHECK, zpath, REF], capture_output=True, text=True, timeout=180)
    return r.returncode, r.stdout.strip() + r.stderr.strip()


def main():
    # reference: precompute synth_A.tcl
    tmp = tempfile.mkdtemp()
    try:
        sa = os.path.join(tmp, "synth_A.tcl")
        subprocess.run(["python3", GEN, "--spec", A_SPEC, "-o", sa], check=True)
        tcl = open(sa).read()
        ref_zip = os.path.join(tmp, "ref.zip")
        make_zip(GEN, "synth_A.tcl", tcl, ref_zip)
        rc, out = run_check(ref_zip)
        assert rc == 0, "REF must PASS but: %s" % out
        print("REF PASS")
        # negatives
        neg_dir = os.path.join(REF, "negative")
        for name in ["fake_empty.py", "fake_print_expected.py", "fake_core_deleted.py",
                     "naive_hardcode_a.py", "naive_flatten.py"]:
            gz = os.path.join(tmp, name + ".zip")
            make_zip(os.path.join(neg_dir, name), "synth_A.tcl", tcl, gz)
            rc, out = run_check(gz)
            assert rc != 0, "NEG %s must FAIL but PASSED" % name
            print("NEG", name, "FAIL ok")
        print("ALL NEG FAIL; REF PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
'''
w(os.path.join(NEG, "negative_selftest.py"), NEG_SELFTEST)

# ---------------------------------------------------------------- self-verify
def build_submit_zip(gen_py, tcl_name, tcl_content, zpath):
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(gen_py, "gen_synth_tcl.py")
        z.writestr(tcl_name, tcl_content)

print("=== self-verify: ref PASS + 5 neg FAIL + 3-fake FAIL ===")
tmp = tempfile.mkdtemp(prefix="hierdcsynth_build_")
try:
    gen_ref = os.path.join(REF, "gen_synth_tcl.py")
    sa = os.path.join(tmp, "synth_A.tcl")
    r = subprocess.run(["python3", gen_ref, "--spec", A_SPEC if False else os.path.join(A_DIR, "spec_A.json"), "-o", sa],
                       capture_output=True, text=True)
    assert r.returncode == 0, "ref gen failed: %s" % r.stderr
    tcl_A = open(sa).read()
    ref_zip = os.path.join(tmp, "ref.zip")
    build_submit_zip(gen_ref, "synth_A.tcl", tcl_A, ref_zip)
    rc = subprocess.run(["python3", os.path.join(REF, "check.py"), ref_zip, REF],
                        capture_output=True, text=True, timeout=180)
    print("REF:", rc.stdout.strip(), rc.stderr.strip()[:300])
    assert rc.returncode == 0, "REF must PASS"
    print("REF PASS ✓")

    # negatives
    for name in ["fake_empty.py", "fake_print_expected.py", "fake_core_deleted.py",
                 "naive_hardcode_a.py", "naive_flatten.py"]:
        gz = os.path.join(tmp, "neg_" + name + ".zip")
        build_submit_zip(os.path.join(NEG, name), "synth_A.tcl", tcl_A, gz)
        rc = subprocess.run(["python3", os.path.join(REF, "check.py"), gz, REF],
                            capture_output=True, text=True, timeout=180)
        ok = rc.returncode != 0
        print("NEG", name, "->", "FAIL ✓" if ok else "PASS ✗", rc.stdout.strip()[:120])
        assert ok, "NEG %s must FAIL" % name
    print("5 negatives all FAIL ✓")

    # §4.9 three fakes = fake_empty / fake_print_expected / fake_core_deleted (already above)
    print("§4.9 (a)空壳=fake_empty (b)只print=fake_print_expected (c)删核心=fake_core_deleted -> all FAIL ✓")
    print("NEG_RC=0")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ---------------------------------------------------------------- assertions gate
K_CHECK = 19  # a-s
RATIONALE = (
    "19 条断言：① submit.zip 恰含 gen_synth_tcl.py + synth_A.tcl ② gen_synth_tcl.py py_compile 通过 "
    "③ 候选生成器对可见 A 的 spec_A.json 运行 exit 0 且产出非空 synth.tcl ④ A 的 synth.tcl 通过 tclsh info complete（无 tclsh 时退化为括号配平）"
    "⑤ A synth.tcl 含 analyze -format verilog 与 rtl_A.v 路径 ⑥ A synth.tcl 含 elaborate addr_dec_A + current_design addr_dec_A + link "
    "⑦ A synth.tcl 保留层次：不含 ungroup -all 且不含 set_flatten ⑧ A synth.tcl 不含 set_dont_touch（避免子模块保持 unmapped GTECH 的 bug）"
    "⑨ A synth.tcl 含 compile_ultra ⑩ A synth.tcl 含 LVS-only 过滤 get_lib_cells -quiet */*LVS* + set_dont_use "
    "⑪ A synth.tcl 含组合电路守卫 all_registers + error ⑫ A synth.tcl 含虚拟时钟 create_clock -name vclk -period 1.0000 + set_input_transition + set_load + set_max_delay "
    "⑬ A synth.tcl 含 report_timing + report_area + report_qor + report_reference ⑭ A synth.tcl 含 write -format verilog + write_sdc "
    "⑮ 候选生成器对隐藏 B 的 spec_B.json 运行 exit 0 且产出非空 synth.tcl ⑯ 跨输入守卫 B synth.tcl 含 elaborate addr_map_B 且不含任何 A 子模块名（reg0_calc_A 等）"
    "⑰ 跨输入守卫 B synth.tcl 时钟为 create_clock -name ick -period 1.6000（与 A 的 vclk/1.0 不同）⑱ 反硬编 gen_synth_tcl.py 源码不含 A/B 专有字面量（设计名/子模块名/库名/时钟名）"
    "⑲ 随机化：对 A 连跑 3 次产出的 synth.tcl 字节一致"
)
# count ①..⑲
import re as _re
k_rationale = len(_re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲]', RATIONALE))
print("GATE: k_rationale=%d k_check=%d -> %s" % (k_rationale, K_CHECK, "PASS" if k_rationale == K_CHECK and K_CHECK >= 8 else "FAIL"))
assert k_rationale == K_CHECK and K_CHECK >= 8, "assertion gate failed"

# ---------------------------------------------------------------- append jsonl
ENTRY = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": CHECK_PY,
    "prompt": PROMPT,
    "attachments": [
        "assets/%s/spec_A.json" % CID,
        "assets/%s/rtl_A.v" % CID,
        "assets/%s/prompt.txt" % CID,
        "assets/%s/task_brief.md" % CID,
    ],
    "metadata": {
        "trace_source": {
            "user": "johnl",
            "host": "hfeg0pfn119",
            "session_file": "1790219837415_uh82d.messages.json",
            "match_count": 41,
            "real_task_summary": "hierarchy-preserving DC synthesis flow for combinational addr_to_rowcol_region (digital domain) on hfeg0pfn119 (johnl); user turn (continuation, pasted prior glm-5.2 transcript + 「注意要保留层次进行综合」+ 「你看下生存到报考我没看到时序报告」+ 「继续」); real assets at /home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/ (synth.tcl, run_dc.sh, rtl/, out/reports/*); prior script set_dont_touch on submodules -> references_post showed 6 hierarchical submodules unmapped (GTECH h); fix = remove submodule dont_touch but keep hierarchy (no ungroup/flatten); B-grade synthesized (real assets span v6/v7 iterations + continuation session).",
        },
        "domain": "digital",
        "track": "faithful",
        "test_rationale": RATIONALE,
    },
}
with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(ENTRY, ensure_ascii=False) + "\n")
print("APPENDED to %s (now %d lines)" % (JSONL,
      sum(1 for _ in open(JSONL))))
print("DONE:", CID)
