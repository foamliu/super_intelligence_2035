#!/usr/bin/env python3
# _build_negs_gate2v.py -- build negatives for NetlistGate2Verilog-001
import os, zipfile, shutil, textwrap, subprocess, sys, tempfile

CASE = "EDA-Eval-DesignFlow-NetlistGate2Verilog-001"
NEG = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/%s/negative" % CASE
os.makedirs(NEG, exist_ok=True)

# the correct gold (copy) for derivatives
GOLD = open("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/%s/netlist2verilog_ref.py" % CASE).read()

# correct B verilog output (precomputed by gold) for print_expected_B
B_V = """// Gate-level Verilog generated from SPICE netlist
// Module: OdtPdMuxB
`timescale 10ps/10ps
module OdtPdMuxB (
    input   WrEn,
    input   InEn,
    input   RstN,
    input   NtEn,
    input   RdDQ,
    input   InEn2,
    input   RocF,
    input   ClkEn,
    output  FlagA,
    output  FlagB,
    output  Sel,
    output  Code0,
    output  Code1,
    inout   vdda,
    inout   gnda
);

    wire b0;
    wire b1;
    wire b2;
    wire b3;
    wire b4;
    wire b5;
    wire b6;

    assign b0 = ~WrEn;
    assign b1 = ~(WrEn & InEn);
    assign b2 = ~(RstN | NtEn);
    assign FlagA = (b1 & b2);
    assign b3 = ~(b0 | (RocF & RdDQ));
    assign b4 = ~(RstN | ClkEn | RocF);
    assign b5 = ~(WrEn & InEn & InEn2);
    assign b6 = ~((ClkEn & RocF) | b0);
    assign FlagB = RocF ? b6 : b3;
    assign Sel = (b5 | b4);
    assign Code0 = (b3 ^ b4);
    assign Code1 = ~(b6 ^ b5);
endmodule
"""

negs = {}

# 1. empty_shell -> FAIL (c) no output
negs['empty_shell'] = "#!/usr/bin/env python3\nimport sys\n# does nothing\nsys.exit(0)\n"

# 2. syntax_err -> FAIL (b) py_compile
negs['syntax_err'] = "#!/usr/bin/env python3\ndef broken(\n  print('hi'\nimport sys\nsys.exit(1)\n"

# 3. no_output -> runs but writes nothing -> FAIL (c)
negs['no_output'] = "#!/usr/bin/env python3\nimport sys, argparse\nap=argparse.ArgumentParser(); ap.add_argument('netlist'); ap.add_argument('module'); ap.add_argument('-o')\nargs=ap.parse_args()\n# parse but don't write\nsys.exit(0)\n"

# 4. print_expected_B -> hardcodes B verilog, ignores args -> FAIL (k) B2 mismatch
negs['print_expected_B'] = "#!/usr/bin/env python3\nimport sys, argparse\nB_V = '''%s'''\nap=argparse.ArgumentParser(); ap.add_argument('netlist'); ap.add_argument('module'); ap.add_argument('-o')\nargs=ap.parse_args()\nout = args.o if args.o else (args.module+'.v')\nwith open(out,'w') as f: f.write(B_V)\nprint('wrote',out)\n" % B_V

# 5. ref_core_deleted -> convert returns empty -> FAIL (f)/(h)
negs['ref_core_deleted'] = GOLD.replace("    return '\\n'.join(out_lines) + '\\n'",
                                        "    return ''  # core deleted")

# 6. hardcode_a -> embeds A literals, branches on name -> FAIL (j) + (c)/(h) for B
negs['hardcode_a'] = "#!/usr/bin/env python3\nimport sys, argparse\nA='OdtPdMuxA'\nap=argparse.ArgumentParser(); ap.add_argument('netlist'); ap.add_argument('module'); ap.add_argument('-o')\nargs=ap.parse_args()\nout = args.o if args.o else (args.module+'.v')\nif args.module==A:\n    with open(out,'w') as f: f.write('module OdtPdMuxA(input OdtWr, output AnyOdt); assign AnyOdt=OdtWr; endmodule\\n')\nelse:\n    with open(out,'w') as f: f.write('module %s; endmodule\\n' % args.module)\nprint('wrote',out)\n"

# 7. wrong_logic -> maps nand2 to and2 -> FAIL (h) truth mismatch
wrong = GOLD.replace("'nand2': (['a', 'b'], '~({a} & {b})'),",
                     "'nand2': (['a', 'b'], '({a} & {b})'),")
negs['wrong_logic'] = wrong

# 8. no_pininfo_dir -> all ports input -> FAIL (e)
no_pin = GOLD.replace("        d = pininfo.get(p, 'I')",
                      "        d = 'I'  # ignore pininfo")
negs['no_pininfo_dir'] = no_pin

# 9. spice_leftover -> emits .SUBCKT in .v -> FAIL (g)
spice_left = GOLD.replace("    out_lines.append('endmodule')",
                          "    out_lines.append('.SUBCKT leftover'); out_lines.append('endmodule')")
negs['spice_leftover'] = spice_left

# 10. no_endmodule -> omit endmodule -> FAIL (d)
no_end = GOLD.replace("    out_lines.append(\"endmodule\")",
                      "    # endmodule omitted")
negs['no_endmodule'] = no_end

# 11. drive_supply -> assign vdda=0 -> FAIL (p)
drive_sup = GOLD.replace("    out_lines.append(\"endmodule\")",
                         '    out_lines.append("    assign vdda = 1\'b0;"); out_lines.append("endmodule")')
negs['drive_supply'] = drive_sup

# 12. nondeterministic -> timestamp comment -> FAIL (n)
nondet = GOLD.replace("    out_lines.append(\"// Gate-level Verilog generated from SPICE netlist\")",
                      "    import time; out_lines.append(\"// generated %s\" % time.time()); out_lines.append(\"// Gate-level Verilog generated from SPICE netlist\")")
negs['nondeterministic'] = nondet

for name, src in negs.items():
    d = os.path.join(NEG, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "netlist2verilog.py"), 'w') as f:
        f.write(src)
    with zipfile.ZipFile(os.path.join(d, "submit.zip"), 'w') as z:
        z.write(os.path.join(d, "netlist2verilog.py"), "netlist2verilog.py")

# negative_selftest.py
selftest = '''#!/usr/bin/env python3
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check
NEG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "negative")
names = sorted(os.listdir(NEG))
results = {}
for name in names:
    zpath = os.path.join(NEG, name, "submit.zip")
    if not os.path.isfile(zpath):
        continue
    w = tempfile.mkdtemp()
    try:
        labels = check._conds(zpath, w)
        failed = [l for l, ok, m in labels if not ok]
        results[name] = failed
    except Exception as e:
        results[name] = ["EXC:%s" % str(e)[:80]]
allfail = all(v for v in results.values())
print("NEG_SELFTEST results:")
for k, v in sorted(results.items()):
    print("  %s -> %s %s" % (k, "FAIL(OK)" if v else "PASS(BAD)", v))
print("NEG_RC=%d distinct=%s" % (len(results), len(set(tuple(v) for v in results.values()))))
print("ALL_FAIL=%s" % allfail)
sys.exit(0 if allfail else 1)
'''
with open(os.path.join(NEG, "..", "negative_selftest.py"), 'w') as f:
    f.write(selftest)
print("built %d negatives" % len(negs))
