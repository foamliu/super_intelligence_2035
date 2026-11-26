#!/usr/bin/env python3
"""_build_spf_coupling_parser_001.py -- builds all artifacts for
EDA-Eval-DesignFlow-SpfCouplingParser-001 (bhcla SPF coupling -> SABL CSV parser,
spec-driven-generator + static-verification pattern).

Produces:
  EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/EDA-Eval-DesignFlow-SpfCouplingParser-001/
      prompt.txt, task_brief.md, spec_a.json, sample_a.spf_CC, hidden_manifest.json
  EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-SpfCouplingParser-001/
      check.py, gen_spf_coupling_parser.py (gold), spec_a.json, spec_b.json,
      hidden/sample_b.spf_CC, negative/*.py, negative_selftest.py
Then self-verifies: gold PASS (>=8 conds), negatives + section 4.9 fakes all FAIL.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-SpfCouplingParser-001"
AST = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)

# ---------- shared spec schema ----------
COLUMN_SET = ["rownum", "CP", "SA_index", "Sa_BLa", "PreEq", "bl", "IO", "ION",
              "Cslin", "PCS", "NCS", "PCHa", "PCHb", "BLen", "power", "total"]
CATEGORY_ORDER = ["ION", "IO", "PreEq", "PCS", "NCS", "PCHa", "PCHb", "Cslin", "BLen", "bl"]
CATEGORY_PATTERNS = {
    "ION": r"^ION",
    "IO": r"^IO",
    "PreEq": r"^PreEq",
    "PCS": r"^PCS",
    "NCS": r"^NCS",
    "PCHa": r"^PCHa",
    "PCHb": r"^PCHb",
    "Cslin": r"Cslin",
    "BLen": r"BLen",
    "bl": r"^cn\d+bl[ab]<\d+>$",
}
POWER_TARGET = "0"
HIER_PATTERN = r"XI_msax(\d+)_cp(\d+)\.XI_CXSA_1x4_0<(\d+)>\.Sa_BLa<(\d+)>"


def emit_block(signal, total_pf, couplings):
    """couplings: list of (kind, tgt, val) where kind in {'C','Cg'}; for Cg tgt='0'."""
    lines = ["*|NET %s %.9gPF" % (signal, total_pf)]
    idx = 1
    for kind, tgt, val in couplings:
        lines.append("%s%d %s %s %.6e" % (kind, idx, signal, tgt, val))
        idx += 1
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------- sample A (assets, faithful) ----------
# 4 Sa_BLa signals across 2 CPs; realistic PF magnitudes (e-18..e-16)
SAMPLE_A_SIGNALS = [
    ("XI_msax256_cp10.XI_CXSA_1x4_0<39>.Sa_BLa<0>", 0.000852709, [
        ("C", "cn09bla<24>", 1.0195e-18),
        ("C", "cn09blb<24>", 3.32513e-18),
        ("C", "PreEq0<3>", 4.73601e-17),
        ("C", "IO_read<1>", 2.1e-17),
        ("C", "ION_write<2>", 8.5e-18),
        ("C", "Cslin_top<5>", 1.2e-17),
        ("C", "PCS0<1>", 3.4e-18),
        ("C", "NCS0<1>", 2.8e-18),
        ("C", "PCHa0<1>", 5.1e-18),
        ("C", "PCHb0<1>", 4.2e-18),
        ("C", "BLen0<1>", 6.7e-18),
        ("Cg", "0", 4.73601e-16),
    ]),
    ("XI_msax256_cp10.XI_CXSA_1x4_0<40>.Sa_BLa<0>", 0.000791204, [
        ("C", "cn09bla<25>", 1.1e-18),
        ("C", "PreEq0<4>", 3.9e-17),
        ("C", "IO_read<2>", 1.9e-17),
        ("C", "ION_write<3>", 7.6e-18),
        ("C", "Cslin_top<6>", 1.05e-17),
        ("C", "PCS0<2>", 3.1e-18),
        ("C", "NCS0<2>", 2.5e-18),
        ("C", "PCHa0<2>", 4.8e-18),
        ("C", "PCHb0<2>", 4.0e-18),
        ("C", "BLen0<2>", 6.3e-18),
        ("Cg", "0", 4.1e-16),
    ]),
    ("XI_msax196_cp07.XI_CXSA_1x4_0<12>.Sa_BLa<0>", 0.000643118, [
        ("C", "cn07bla<12>", 8.9e-19),
        ("C", "PreEq0<1>", 3.2e-17),
        ("C", "IO_read<1>", 1.7e-17),
        ("C", "ION_write<1>", 7.1e-18),
        ("C", "Cslin_top<2>", 9.8e-18),
        ("C", "PCS0<1>", 2.9e-18),
        ("C", "NCS0<1>", 2.4e-18),
        ("C", "PCHa0<1>", 4.5e-18),
        ("C", "PCHb0<1>", 3.8e-18),
        ("C", "BLen0<1>", 5.9e-18),
        ("Cg", "0", 3.6e-16),
    ]),
    ("XI_msax196_cp07.XI_CXSA_1x4_0<12>.Sa_BLa<1>", 0.000658802, [
        ("C", "cn07bla<13>", 9.2e-19),
        ("C", "PreEq0<2>", 3.4e-17),
        ("C", "IO_read<2>", 1.8e-17),
        ("C", "ION_write<2>", 7.3e-18),
        ("C", "Cslin_top<3>", 1.01e-17),
        ("C", "PCS0<2>", 3.0e-18),
        ("C", "NCS0<2>", 2.6e-18),
        ("C", "PCHa0<2>", 4.6e-18),
        ("C", "PCHb0<2>", 3.9e-18),
        ("C", "BLen0<2>", 6.1e-18),
        ("Cg", "0", 3.7e-16),
    ]),
]


def render_spf(header_lines, signals):
    out = list(header_lines)
    for sig, tot, cou in signals:
        out.append(emit_block(sig, tot, cou))
    return "\n".join(out)


SAMPLE_A_TEXT = render_spf(
    ["# SPF Standard Parasitic Format - coupling data",
     "# extracted: 1027 lpe msaq_E (ray1lei)",
     "# file: /proj/drgqx/V0/ver/pex/ray1lei/msaq_E/1027/lpe/msaq/msaq_E.spf_CC",
     ""],
    SAMPLE_A_SIGNALS,
)

# ---------- sample B (hidden, isomorphic, 6 signals / 2 CPs, different values) ----------
SAMPLE_B_SIGNALS = [
    ("XI_msax128_cp03.XI_CXSA_1x4_0<7>.Sa_BLa<0>", 0.000512884, [
        ("C", "cn05bla<07>", 7.7e-19),
        ("C", "PreEq1<2>", 2.8e-17),
        ("C", "IO_addr<4>", 1.5e-17),
        ("C", "ION_ctrl<5>", 6.4e-18),
        ("C", "Cslin_bot<1>", 8.6e-18),
        ("C", "PCS1<3>", 2.7e-18),
        ("C", "NCS1<3>", 2.2e-18),
        ("C", "PCHa1<3>", 4.1e-18),
        ("C", "PCHb1<3>", 3.5e-18),
        ("C", "BLen1<3>", 5.4e-18),
        ("Cg", "0", 3.2e-16),
    ]),
    ("XI_msax128_cp03.XI_CXSA_1x4_0<7>.Sa_BLa<1>", 0.000521107, [
        ("C", "cn05bla<08>", 7.9e-19),
        ("C", "PreEq1<3>", 2.9e-17),
        ("C", "IO_addr<5>", 1.55e-17),
        ("C", "ION_ctrl<6>", 6.5e-18),
        ("C", "Cslin_bot<2>", 8.8e-18),
        ("C", "PCS1<4>", 2.8e-18),
        ("C", "NCS1<4>", 2.3e-18),
        ("C", "PCHa1<4>", 4.2e-18),
        ("C", "PCHb1<4>", 3.6e-18),
        ("C", "BLen1<4>", 5.5e-18),
        ("Cg", "0", 3.3e-16),
    ]),
    ("XI_msax128_cp03.XI_CXSA_1x4_0<8>.Sa_BLa<0>", 0.000498221, [
        ("C", "cn05blb<07>", 7.5e-19),
        ("C", "PreEq1<1>", 2.7e-17),
        ("C", "IO_addr<3>", 1.45e-17),
        ("C", "ION_ctrl<4>", 6.3e-18),
        ("C", "Cslin_bot<0>", 8.4e-18),
        ("C", "PCS1<2>", 2.6e-18),
        ("C", "NCS1<2>", 2.1e-18),
        ("C", "PCHa1<2>", 4.0e-18),
        ("C", "PCHb1<2>", 3.4e-18),
        ("C", "BLen1<2>", 5.3e-18),
        ("Cg", "0", 3.1e-16),
    ]),
    ("XI_msax512_cp11.XI_CXSA_1x4_0<21>.Sa_BLa<0>", 0.000977640, [
        ("C", "cn12bla<21>", 1.21e-18),
        ("C", "PreEq2<5>", 5.6e-17),
        ("C", "IO_dq<9>", 2.6e-17),
        ("C", "ION_dqs<9>", 1.04e-17),
        ("C", "Cslin_mid<8>", 1.46e-17),
        ("C", "PCS2<5>", 4.1e-18),
        ("C", "NCS2<5>", 3.4e-18),
        ("C", "PCHa2<5>", 6.2e-18),
        ("C", "PCHb2<5>", 5.1e-18),
        ("C", "BLen2<5>", 8.1e-18),
        ("Cg", "0", 5.6e-16),
    ]),
    ("XI_msax512_cp11.XI_CXSA_1x4_0<21>.Sa_BLa<2>", 0.000961418, [
        ("C", "cn12bla<22>", 1.18e-18),
        ("C", "PreEq2<6>", 5.4e-17),
        ("C", "IO_dq<10>", 2.55e-17),
        ("C", "ION_dqs<10>", 1.02e-17),
        ("C", "Cslin_mid<9>", 1.43e-17),
        ("C", "PCS2<6>", 4.0e-18),
        ("C", "NCS2<6>", 3.3e-18),
        ("C", "PCHa2<6>", 6.0e-18),
        ("C", "PCHb2<6>", 5.0e-18),
        ("C", "BLen2<6>", 7.9e-18),
        ("Cg", "0", 5.5e-16),
    ]),
    ("XI_msax512_cp11.XI_CXSA_1x4_0<22>.Sa_BLa<0>", 0.001003825, [
        ("C", "cn12blb<21>", 1.24e-18),
        ("C", "PreEq2<7>", 5.8e-17),
        ("C", "IO_dq<11>", 2.65e-17),
        ("C", "ION_dqs<11>", 1.06e-17),
        ("C", "Cslin_mid<10>", 1.49e-17),
        ("C", "PCS2<7>", 4.2e-18),
        ("C", "NCS2<7>", 3.5e-18),
        ("C", "PCHa2<7>", 6.4e-18),
        ("C", "PCHb2<7>", 5.2e-18),
        ("C", "BLen2<7>", 8.3e-18),
        ("Cg", "0", 5.7e-16),
    ]),
]
SAMPLE_B_TEXT = render_spf(
    ["# SPF Standard Parasitic Format - coupling data",
     "# extracted: 1105 lpe msaq_E v2 (ray1lei)",
     "# file: /proj/drgqx/V1/ver/pex/ray1lei/msaq_E/1105/lpe/msaq/msaq_E_v2.spf_CC",
     ""],
    SAMPLE_B_SIGNALS,
)


def make_spec(output_csv, spf_file, marker_a_only):
    return {
        "column_set": list(COLUMN_SET),
        "category_order": list(CATEGORY_ORDER),
        "category_patterns": dict(CATEGORY_PATTERNS),
        "power_target": POWER_TARGET,
        "hierarchy_pattern": HIER_PATTERN,
        "spf_file": spf_file,
        "output_csv": output_csv,
        "sort_key": ["CP", "SA_index", "Sa_BLa"],
        "marker_a_only": marker_a_only,  # a token unique to A (for anti-hardcode-A)
    }


SPEC_A = make_spec("sabl_summary_a.csv", "sample_a.spf_CC", "msax256_cp10")
SPEC_B = make_spec("sabl_summary_b.csv", "sample_b.spf_CC", "msax128_cp03")

# marker_b_only for anti-hardcode (B-specific token that MUST appear)
SPEC_B["marker_b_only"] = "msax512_cp11"


# ---------------- gold generator (emits parse_spf_cc.py parameterized by spec) ----------------
GOLD_GEN = '''#!/usr/bin/env python3
"""gen_spf_coupling_parser.py -- spec-driven generator for SPF coupling -> SABL CSV parser.

Reads a spec.json (column set, category classification rules, signal hierarchy
pattern, output csv name) and emits a self-contained parser parse_spf_cc.py that
reproduces the SPF coupling-summary skill from the trace.

Usage: python gen_spf_coupling_parser.py <spec.json> <outdir>
Emits: <outdir>/parse_spf_cc.py
"""
import json
import os
import sys


def _py_list(items):
    return "[" + ", ".join(_py_str(i) for i in items) + "]"


def _py_str(s):
    return '"' + str(s).replace("\\\\", "\\\\\\\\").replace('"', '\\\\"') + '"'


def _py_dict_str(d):
    return "{" + ", ".join(_py_str(k) + ": " + _py_str(v) for k, v in d.items()) + "}"


def emit_parser(spec):
    column_set = spec["column_set"]
    category_order = spec["category_order"]
    category_patterns = spec["category_patterns"]
    power_target = spec["power_target"]
    hier_pattern = spec["hierarchy_pattern"]
    output_csv = spec["output_csv"]
    sort_key = spec["sort_key"]
    L = []
    A = L.append
    A("#!/usr/bin/env python3")
    A('"""parse_spf_cc.py -- emitted by gen_spf_coupling_parser.py.')
    A("Parses an SPF coupling file into a SABL summary CSV.")
    A('Usage: python parse_spf_cc.py <spf_file> <outdir>"""')
    A("import csv")
    A("import os")
    A("import re")
    A("import sys")
    A("")
    A("COLUMN_SET = " + _py_list(column_set))
    A("CATEGORY_ORDER = " + _py_list(category_order))
    A("CATEGORY_PATTERNS = " + _py_dict_str(category_patterns))
    A("POWER_TARGET = " + _py_str(power_target))
    A("HIER_RE = re.compile(" + _py_str(hier_pattern) + ")")
    A("OUTPUT_CSV = " + _py_str(output_csv))
    A("SORT_KEY = " + _py_list(sort_key))
    A("")
    A("")
    A("def classify(tgt):")
    A("    for cat in CATEGORY_ORDER:")
    A("        if re.search(CATEGORY_PATTERNS[cat], tgt):")
    A("            return cat")
    A("    return None")
    A("")
    A("")
    A("def parse_spf(text):")
    A("    lines = text.splitlines()")
    A("    start = 0")
    A("    for i, ln in enumerate(lines):")
    A("        if ln.startswith('*|NET'):")
    A("            start = i")
    A("            break")
    A("    blocks = []")
    A("    cur = None")
    A("    for ln in lines[start:]:")
    A("        if ln.startswith('*|NET'):")
    A("            if cur is not None:")
    A("                blocks.append(cur)")
    A("            parts = ln.split()")
    A("            sig = parts[1]")
    A("            tot = float(parts[2].replace('PF', ''))")
    A('            cur = {"signal": sig, "total": tot, "cats": {}}')
    A("        elif (ln.startswith('C') or ln.startswith('Cg')) and cur is not None:")
    A("            parts = ln.split()")
    A("            if len(parts) < 4:")
    A("                continue")
    A("            tgt = parts[2]")
    A("            try:")
    A("                val = float(parts[3])")
    A("            except ValueError:")
    A("                continue")
    A("            if tgt == POWER_TARGET:")
    A("                cat = 'power'")
    A("            else:")
    A("                cat = classify(tgt)")
    A("            if cat is not None:")
    A('                cur["cats"][cat] = cur["cats"].get(cat, 0.0) + val')
    A("        elif ln.strip() == '' and cur is not None:")
    A("            blocks.append(cur)")
    A("            cur = None")
    A("    if cur is not None:")
    A("        blocks.append(cur)")
    A("    return blocks")
    A("")
    A("")
    A("def summarize(blocks):")
    A("    rows = []")
    A("    for b in blocks:")
    A("        m = HIER_RE.match(b['signal'])")
    A("        if not m:")
    A("            continue")
    A("        n, mm, k, j = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))")
    A('        cp = "msax%s_cp%s" % (n, mm)')
    A('        row = {"CP": cp, "SA_index": k, "Sa_BLa": j, "total": b["total"]}')
    A("        for cat in CATEGORY_ORDER:")
    A('            row[cat] = b["cats"].get(cat, 0.0)')
    A('        row["power"] = b["cats"].get("power", 0.0)')
    A("        rows.append(row)")
    A("    rows.sort(key=lambda r: tuple(r[c] for c in SORT_KEY))")
    A("    for i, r in enumerate(rows, 1):")
    A('        r["rownum"] = i')
    A("    return rows")
    A("")
    A("")
    A("def main():")
    A("    if len(sys.argv) < 3:")
    A('        print("usage: parse_spf_cc.py <spf_file> <outdir>", file=sys.stderr)')
    A("        sys.exit(2)")
    A("    spf_path = sys.argv[1]")
    A("    outdir = sys.argv[2]")
    A("    with open(spf_path) as f:")
    A("        text = f.read()")
    A("    blocks = parse_spf(text)")
    A("    rows = summarize(blocks)")
    A("    os.makedirs(outdir, exist_ok=True)")
    A("    out = os.path.join(outdir, OUTPUT_CSV)")
    A('    with open(out, "w", newline="") as f:')
    A("        w = csv.writer(f)")
    A("        w.writerow(COLUMN_SET)")
    A("        for r in rows:")
    A("            w.writerow([r[c] for c in COLUMN_SET])")
    A("")
    A("")
    A('if __name__ == "__main__":')
    A("    main()")
    A("")
    return "\\n".join(L)


def main():
    if len(sys.argv) < 3:
        print("usage: gen_spf_coupling_parser.py <spec.json> <outdir>", file=sys.stderr)
        sys.exit(2)
    spec_path = sys.argv[1]
    outdir = sys.argv[2]
    with open(spec_path) as f:
        spec = json.load(f)
    os.makedirs(outdir, exist_ok=True)
    parser_path = os.path.join(outdir, "parse_spf_cc.py")
    with open(parser_path, "w") as f:
        f.write(emit_parser(spec))


if __name__ == "__main__":
    main()
'''


# ---------------- check.py (independent recompute) ----------------
CHECK = '''#!/usr/bin/env python3
"""check(deliverable, workdir) for EDA-Eval-DesignFlow-SpfCouplingParser-001.

Runs the SUT generator (gen_spf_coupling_parser.py from submit.zip) on the HIDDEN
spec_b.json (not spec_a), then runs the emitted parser on the hidden SPF sample B,
and independently recomputes the expected SABL summary CSV from sample_b to verify
structure + values. 16 independent conditions a-p; any FAIL -> raise AssertionError.
"""
import csv
import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import OrderedDict


def _cond(idx, ok, msg):
    if not ok:
        raise AssertionError("cond %s FAIL: %s" % (idx, msg))


# ---- independent recompute (does NOT use the SUT generator/parser) ----
def recompute(spec, spf_text):
    col_set = spec["column_set"]
    cat_order = spec["category_order"]
    cat_pat = spec["category_patterns"]
    power_target = spec["power_target"]
    hier_re = re.compile(spec["hierarchy_pattern"])
    sort_key = spec["sort_key"]

    def classify(tgt):
        for cat in cat_order:
            if re.search(cat_pat[cat], tgt):
                return cat
        return None

    lines = spf_text.splitlines()
    start = 0
    for i, ln in enumerate(lines):
        if ln.startswith("*|NET"):
            start = i
            break
    blocks = []
    cur = None
    for ln in lines[start:]:
        if ln.startswith("*|NET"):
            if cur is not None:
                blocks.append(cur)
            parts = ln.split()
            sig = parts[1]
            tot = float(parts[2].replace("PF", ""))
            cur = {"signal": sig, "total": tot, "cats": {}}
        elif (ln.startswith("C") or ln.startswith("Cg")) and cur is not None:
            parts = ln.split()
            if len(parts) < 4:
                continue
            tgt = parts[2]
            try:
                val = float(parts[3])
            except ValueError:
                continue
            cat = "power" if tgt == power_target else classify(tgt)
            if cat is not None:
                cur["cats"][cat] = cur["cats"].get(cat, 0.0) + val
        elif ln.strip() == "" and cur is not None:
            blocks.append(cur)
            cur = None
    if cur is not None:
        blocks.append(cur)

    rows = []
    for b in blocks:
        m = hier_re.match(b["signal"])
        if not m:
            continue
        n, mm, k, j = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        cp = "msax%s_cp%s" % (n, mm)
        row = OrderedDict()
        row["CP"] = cp
        row["SA_index"] = k
        row["Sa_BLa"] = j
        row["total"] = b["total"]
        for cat in cat_order:
            row[cat] = b["cats"].get(cat, 0.0)
        row["power"] = b["cats"].get("power", 0.0)
        rows.append(row)
    rows.sort(key=lambda r: tuple(r[c] for c in sort_key))
    for i, r in enumerate(rows, 1):
        r["rownum"] = i
    # rebuild in column_set order
    out = []
    for r in rows:
        out.append({c: r[c] for c in col_set})
    return out


def _read_csv(path):
    with open(path, newline="") as f:
        rdr = csv.reader(f)
        rows = list(rdr)
    return rows


def _fval(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def check(deliverable, workdir):
    ref_dir = os.path.dirname(os.path.abspath(__file__))
    spec_b_path = os.path.join(ref_dir, "spec_b.json")
    spec_a_path = os.path.join(ref_dir, "spec_a.json")
    with open(spec_b_path) as f:
        spec_b = json.load(f)
    spec_a = json.load(open(spec_a_path)) if os.path.exists(spec_a_path) else {}
    sample_b_path = os.path.join(ref_dir, "hidden", spec_b["spf_file"])
    with open(sample_b_path) as f:
        spf_b_text = f.read()

    expected = recompute(spec_b, spf_b_text)

    tmp = tempfile.mkdtemp(prefix="chk_spf_")
    try:
        if not os.path.exists(deliverable):
            raise AssertionError("deliverable not found: %s" % deliverable)
        with zipfile.ZipFile(deliverable) as z:
            z.extractall(tmp)
        # a. zip valid + contains gen_spf_coupling_parser.py + spec_a.json
        gen_path = os.path.join(tmp, "gen_spf_coupling_parser.py")
        spec_a_in_zip = os.path.join(tmp, "spec_a.json")
        _cond("a", os.path.isfile(gen_path) and os.path.isfile(spec_a_in_zip),
              "zip must contain gen_spf_coupling_parser.py and spec_a.json")

        # b. gen py_compile passes
        try:
            py_compile.compile(gen_path, doraise=True)
            b_ok = True
        except py_compile.PyCompileError:
            b_ok = False
        _cond("b", b_ok, "gen_spf_coupling_parser.py must py_compile without syntax error")

        # c. run gen on hidden spec_b -> emits parse_spf_cc.py
        outdir = os.path.join(tmp, "gen_out")
        os.makedirs(outdir, exist_ok=True)
        proc = subprocess.run([sys.executable, gen_path, spec_b_path, outdir],
                              capture_output=True, text=True, timeout=60)
        parser_path = os.path.join(outdir, "parse_spf_cc.py")
        _cond("c", proc.returncode == 0 and os.path.isfile(parser_path),
              "gen run on spec_b must emit parse_spf_cc.py (rc=%d, stderr=%s)"
              % (proc.returncode, proc.stderr[:200]))

        # d. emitted parser py_compile passes
        try:
            py_compile.compile(parser_path, doraise=True)
            d_ok = True
        except py_compile.PyCompileError:
            d_ok = False
        _cond("d", d_ok, "emitted parse_spf_cc.py must py_compile without syntax error")

        # e. run emitted parser on hidden sample_b -> produces output_csv
        poutdir = os.path.join(tmp, "parse_out")
        os.makedirs(poutdir, exist_ok=True)
        pproc = subprocess.run([sys.executable, parser_path, sample_b_path, poutdir],
                               capture_output=True, text=True, timeout=60)
        csv_path = os.path.join(poutdir, spec_b["output_csv"])
        _cond("e", pproc.returncode == 0 and os.path.isfile(csv_path),
              "parser run on sample_b must produce %s (rc=%d, stderr=%s)"
              % (spec_b["output_csv"], pproc.returncode, pproc.stderr[:200]))

        rows = _read_csv(csv_path)
        # f. CSV header == spec_b.column_set (ordered)
        _cond("f", len(rows) >= 1 and rows[0] == spec_b["column_set"],
              "CSV header must equal spec_b.column_set in order, got %s"
              % (rows[0] if rows else "EMPTY"))

        data_rows = rows[1:]
        # g. row count == expected (BLa signals)
        _cond("g", len(data_rows) == len(expected),
              "CSV data row count must be %d (BLa signals in sample_b), got %d"
              % (len(expected), len(data_rows)))

        # h. rownum 1..N sequential
        rn = [_fval(r[0]) for r in data_rows]
        _cond("h", len(rn) == len(expected) and all(rn[i] == i + 1 for i in range(len(rn))),
              "rownum must be 1..%d sequential, got %s" % (len(expected), rn))

        # build dict by rownum for value compare
        got = {int(_fval(r[0])): r for r in data_rows}
        col_index = {c: i for i, c in enumerate(spec_b["column_set"])}

        # i. CP matches recompute
        cp_ok = all(got[i + 1][col_index["CP"]] == expected[i]["CP"] for i in range(len(expected)))
        _cond("i", cp_ok, "CP column must match recompute (hierarchy parse) for all rows")

        # j. SA_index matches recompute (int)
        sa_ok = all(_fval(got[i + 1][col_index["SA_index"]]) == expected[i]["SA_index"]
                    for i in range(len(expected)))
        _cond("j", sa_ok, "SA_index column must match recompute (int) for all rows")

        # k. Sa_BLa matches recompute (int)
        bla_ok = all(_fval(got[i + 1][col_index["Sa_BLa"]]) == expected[i]["Sa_BLa"]
                     for i in range(len(expected)))
        _cond("k", bla_ok, "Sa_BLa column must match recompute (int) for all rows")

        # l. total matches recompute (*|NET total) within tolerance
        tol = 1e-12
        tot_ok = all(abs(_fval(got[i + 1][col_index["total"]]) - expected[i]["total"]) <= tol
                     for i in range(len(expected)))
        _cond("l", tot_ok, "total column must match *|NET total within tol for all rows")

        # m. each category column matches recompute sum within tolerance
        cat_cols = ["PreEq", "bl", "IO", "ION", "Cslin", "PCS", "NCS", "PCHa", "PCHb", "BLen", "power"]
        bad = []
        for i in range(len(expected)):
            for c in cat_cols:
                gv = _fval(got[i + 1][col_index[c]])
                ev = expected[i][c]
                if gv is None or abs(gv - ev) > tol:
                    bad.append((i + 1, c, gv, ev))
        _cond("m", len(bad) == 0,
              "category columns must match recompute sums within tol, first mismatches: %s"
              % str(bad[:5]))

        # n. anti-hardcode-A: B marker present, A marker absent in CSV text
        csv_txt = "\\n".join(",".join(r) for r in rows)
        _cond("n", spec_b.get("marker_b_only", "") in csv_txt
              and spec_a.get("marker_a_only", "ZNONE_A") not in csv_txt
              and spec_a.get("output_csv", "ZNONE_A") not in csv_txt,
              "CSV must contain B-specific marker %s and NOT contain A-specific marker/%s"
              % (spec_b.get("marker_b_only"), spec_a.get("output_csv")))

        # o. 3-seed determinism: run gen 3x -> identical md5 of emitted parser
        hashes = []
        for i in range(3):
            od = os.path.join(tmp, "det_%d" % i)
            os.makedirs(od, exist_ok=True)
            subprocess.run([sys.executable, gen_path, spec_b_path, od],
                           capture_output=True, text=True, timeout=60)
            pp = os.path.join(od, "parse_spf_cc.py")
            h = hashlib.md5(open(pp, "rb").read()).hexdigest() if os.path.isfile(pp) else ""
            hashes.append(h)
        _cond("o", len(set(hashes)) == 1 and hashes[0],
              "generator must be deterministic across 3 runs, got %s" % hashes)

        # p. anti-trivial: emitted parser defines parse_spf + summarize + classify
        ptxt = open(parser_path).read()
        _cond("p", "def parse_spf(" in ptxt and "def summarize(" in ptxt
              and "def classify(" in ptxt and "csv.writer" in ptxt,
              "emitted parser must define parse_spf/summarize/classify and write CSV (anti-trivial)")

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    ref_dir = os.path.dirname(os.path.abspath(__file__))
    deliv = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ref_dir, "_gold_submit.zip")
    wd = sys.argv[2] if len(sys.argv) > 2 else ref_dir
    print(check(deliv, wd))
'''


# ---------------- negatives ----------------
NEG_NOOP = '''#!/usr/bin/env python3
# negative: noop -- produces nothing
import sys
if len(sys.argv) < 3:
    sys.exit(2)
'''

NEG_HARDCODE_A = '''#!/usr/bin/env python3
# negative: hardcode_a -- emits a parser baked with spec_A column/output (fails anti-hardcode-A on B)
import os, sys
if len(sys.argv) < 3:
    sys.exit(2)
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
p = os.path.join(outdir, "parse_spf_cc.py")
with open(p, "w") as f:
    f.write("#!/usr/bin/env python3\\n")
    f.write("import csv, os, sys\\n")
    f.write('COLUMN_SET = ["rownum","CP","SA_index","Sa_BLa","PreEq","bl","IO","ION","Cslin","PCS","NCS","PCHa","PCHb","BLen","power","total"]\\n')
    f.write('OUTPUT_CSV = "sabl_summary_a.csv"\\n')  # WRONG: A name, not B
    f.write("def parse_spf(t): return []\\n")
    f.write("def summarize(b): return []\\n")
    f.write("def classify(t): return None\\n")
    f.write("def main():\\n")
    f.write("    outdir = sys.argv[2]\\n")
    f.write("    os.makedirs(outdir, exist_ok=True)\\n")
    f.write('    with open(os.path.join(outdir, OUTPUT_CSV), ' + chr(34) + 'w' + chr(34) + ', newline=' + chr(34) + chr(34) + ') as f:\\n')
    f.write("        w = csv.writer(f); w.writerow(COLUMN_SET)\\n")
    f.write('if __name__ == "__main__": main()\\n')
'''

NEG_STUB = '''#!/usr/bin/env python3
# negative: stub -- writes a TODO placeholder parser
import os, sys
if len(sys.argv) < 3:
    sys.exit(2)
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "parse_spf_cc.py"), "w") as f:
    f.write("# TODO: implement SPF parser\\n")
'''

NEG_FAKE_PRINT = '''#!/usr/bin/env python3
# negative: fake_print -- prints expected header but writes no real CSV rows
import os, sys
if len(sys.argv) < 3:
    sys.exit(2)
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
p = os.path.join(outdir, "parse_spf_cc.py")
with open(p, "w") as f:
    f.write("#!/usr/bin/env python3\\n")
    f.write("import os, sys\\n")
    f.write('print(' + chr(34) + 'rownum,CP,SA_index,Sa_BLa' + chr(34) + ')\\n')  # print only, no file
    f.write("def parse_spf(t): return []\\n")
    f.write("def summarize(b): return []\\n")
    f.write("def classify(t): return None\\n")
'''

NEG_FAKE_EMPTY = '''#!/usr/bin/env python3
# negative: section 4.9(a) empty shell -- parses args, emits empty parser file
import os, sys
if len(sys.argv) < 3:
    sys.exit(2)
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
open(os.path.join(outdir, "parse_spf_cc.py"), "w").close()  # empty file
'''

NEG_FAKE_PRINT_ONLY = '''#!/usr/bin/env python3
# negative: section 4.9(b) print-only -- parser only prints, never writes CSV
import os, sys
if len(sys.argv) < 3:
    sys.exit(2)
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
p = os.path.join(outdir, "parse_spf_cc.py")
with open(p, "w") as f:
    f.write("#!/usr/bin/env python3\\n")
    f.write("import sys\\n")
    f.write('print(' + chr(34) + 'sabl_summary_b.csv' + chr(34) + ')\\n')
    f.write("def parse_spf(t): return []\\n")
    f.write("def summarize(b): return []\\n")
    f.write("def classify(t): return None\\n")
'''

NEG_FAKE_CORE_DELETED = '''#!/usr/bin/env python3
# negative: section 4.9(c) core-deleted -- gold-like generator but summarize() returns [] (core logic deleted)
import json, os, sys
if len(sys.argv) < 3:
    sys.exit(2)
with open(sys.argv[1]) as f:
    spec = json.load(f)
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
p = os.path.join(outdir, "parse_spf_cc.py")
with open(p, "w") as f:
    f.write("#!/usr/bin/env python3\\n")
    f.write("import csv, os, re, sys\\n")
    f.write("COLUMN_SET = " + str(spec['column_set']) + "\\n")
    f.write("OUTPUT_CSV = " + repr(spec['output_csv']) + "\\n")
    f.write("def parse_spf(t): return []\\n")  # core deleted
    f.write("def summarize(b): return []\\n")  # core deleted
    f.write("def classify(t): return None\\n")
    f.write("def main():\\n")
    f.write("    outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)\\n")
    f.write('    with open(os.path.join(outdir, OUTPUT_CSV), ' + chr(34) + 'w' + chr(34) + ', newline=' + chr(34) + chr(34) + ') as f:\\n')
    f.write("        w = csv.writer(f); w.writerow(COLUMN_SET)\\n")
    f.write('if __name__ == "__main__": main()\\n')
'''

NEG_SELFTEST = '''#!/usr/bin/env python3
"""negative_selftest.py -- run check() against each negative; all must FAIL (raise)."""
import os
import shutil
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check import check

NEGATIVES = ["noop.py", "hardcode_a.py", "stub.py", "fake_print.py"]
F_4_9 = ["fake_empty.py", "fake_print_only.py", "fake_core_deleted.py"]
SPEC_A = os.path.join(HERE, "spec_a.json")


def build_zip(gen_src, tmp):
    zfp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zfp, "w") as z:
        z.write(gen_src, "gen_spf_coupling_parser.py")
        z.write(SPEC_A, "spec_a.json")
    return zfp


def run_one(gen_src, label):
    tmp = tempfile.mkdtemp(prefix="neg_")
    try:
        zfp = build_zip(gen_src, tmp)
        try:
            res = check(zfp, tmp)
            print("  [FAIL expected but PASS] %s -> %s" % (label, res))
            return False
        except AssertionError as e:
            print("  [OK fail] %s -> %s" % (label, str(e)[:120]))
            return True
        except Exception as e:
            print("  [OK fail(non-asssert)] %s -> %s: %s" % (label, type(e).__name__, str(e)[:120]))
            return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    all_fail = True
    print("=== negatives (must all FAIL) ===")
    for neg in NEGATIVES:
        p = os.path.join(HERE, "negative", neg)
        if not os.path.exists(p):
            print("  [SKIP] %s not found" % neg); continue
        if not run_one(p, neg):
            all_fail = False
    print("=== section 4.9 fakes (must all FAIL) ===")
    for fk in F_4_9:
        p = os.path.join(HERE, "negative", fk)
        if not os.path.exists(p):
            print("  [SKIP] %s not found" % fk); continue
        if not run_one(p, fk):
            all_fail = False
    print("=== ALL NEGATIVES FAIL:", all_fail, "===")
    sys.exit(0 if all_fail else 1)


if __name__ == "__main__":
    main()
'''


# ---------------- write assets ----------------
def write_assets():
    os.makedirs(AST, exist_ok=True)
    with open(os.path.join(AST, "prompt.txt"), "w") as f:
        f.write(PROMPT)
    with open(os.path.join(AST, "task_brief.md"), "w") as f:
        f.write(TASK_BRIEF)
    with open(os.path.join(AST, "spec_a.json"), "w") as f:
        json.dump(SPEC_A, f, ensure_ascii=False, indent=2)
    with open(os.path.join(AST, "sample_a.spf_CC"), "w") as f:
        f.write(SAMPLE_A_TEXT)
    with open(os.path.join(AST, "hidden_manifest.json"), "w") as f:
        json.dump({
            "hidden_dir": "hidden",
            "spec_b": "spec_b.json",
            "sample_b": "sample_b.spf_CC",
            "note": ("Hidden input B (spec_b.json + sample_b.spf_CC) is isomorphic to A but with "
                     "different scale/values: 6 Sa_BLa signals across 2 CPs (msax128_cp03, msax512_cp11) "
                     "vs A's 4 signals (msax256_cp10, msax196_cp07); different SA indices, coupling "
                     "values, output_csv name. check.py runs the SUT generator on spec_b only and the "
                     "emitted parser on sample_b only."),
        }, f, ensure_ascii=False, indent=2)


# ---------------- write reference ----------------
def write_reference():
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "check.py"), "w") as f:
        f.write(CHECK)
    with open(os.path.join(REF, "gen_spf_coupling_parser.py"), "w") as f:
        f.write(GOLD_GEN)
    with open(os.path.join(REF, "spec_a.json"), "w") as f:
        json.dump(SPEC_A, f, ensure_ascii=False, indent=2)
    with open(os.path.join(REF, "spec_b.json"), "w") as f:
        json.dump(SPEC_B, f, ensure_ascii=False, indent=2)
    os.makedirs(os.path.join(REF, "hidden"), exist_ok=True)
    with open(os.path.join(REF, "hidden", "sample_b.spf_CC"), "w") as f:
        f.write(SAMPLE_B_TEXT)
    negdir = os.path.join(REF, "negative")
    os.makedirs(negdir, exist_ok=True)
    for name, src in [
        ("noop.py", NEG_NOOP),
        ("hardcode_a.py", NEG_HARDCODE_A),
        ("stub.py", NEG_STUB),
        ("fake_print.py", NEG_FAKE_PRINT),
        ("fake_empty.py", NEG_FAKE_EMPTY),
        ("fake_print_only.py", NEG_FAKE_PRINT_ONLY),
        ("fake_core_deleted.py", NEG_FAKE_CORE_DELETED),
    ]:
        with open(os.path.join(negdir, name), "w") as f:
            f.write(src)
    with open(os.path.join(REF, "negative_selftest.py"), "w") as f:
        f.write(NEG_SELFTEST)


PROMPT = ("帮助我去处理一部分数据，转化为排版规律的csv文件或excel文件，这部分是通过SPF工具抽出来的signal之间的"
          "coupling数据，每个空白行后的第一行都是这个信号的总coupling,之后是该signal和其他signal之间的coupling,"
          "最后一行则是该信号和power之间的coupling…除了上述表述外，还有什么是你想在正式处理数据之前想了解的？")

TASK_BRIEF = (
    "# 交付接口\n"
    "交付: outputs/submit.zip，内含 gen_spf_coupling_parser.py（标准库生成器）与 spec_a.json。\n"
    "生成器读 spec.json（参数化配置：列集合/分类规则/信号层级/输出csv名）后在指定输出目录产出 parse_spf_cc.py（自包含 SPF 解析器）。\n"
    "参考: assets/sample_a.spf_CC 为真实 SPF coupling 抽取样本，spec_a.json 已将其处理参数预解析。"
)


def gold_zip(tmp):
    zfp = os.path.join(tmp, "_gold_submit.zip")
    with zipfile.ZipFile(zfp, "w") as z:
        z.write(os.path.join(REF, "gen_spf_coupling_parser.py"), "gen_spf_coupling_parser.py")
        z.write(os.path.join(REF, "spec_a.json"), "spec_a.json")
    return zfp


def self_verify():
    sys.path.insert(0, REF)
    import importlib
    if "check" in sys.modules:
        del sys.modules["check"]
    import check as chk
    tmp = tempfile.mkdtemp(prefix="gold_self_")
    try:
        zfp = gold_zip(tmp)
        res = chk.check(zfp, tmp)
        print("GOLD check() -> %s (PASS expected)" % res)
        if res is not True:
            print("FAIL: gold did not pass"); return False
    except Exception as e:
        print("GOLD check() RAISED: %s: %s" % (type(e).__name__, str(e)[:300]))
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # negatives
    neg = subprocess.run([sys.executable, os.path.join(REF, "negative_selftest.py")],
                         capture_output=True, text=True)
    print(neg.stdout)
    print(neg.stderr)
    if neg.returncode != 0:
        print("FAIL: negative_selftest did not all FAIL"); return False
    # section 4.9 fakes via direct call
    print("section 4.9 fakes already covered in negative_selftest (fake_empty/fake_print_only/fake_core_deleted)")
    return True


def main():
    write_assets()
    write_reference()
    print("artifacts written to:")
    print("  assets:", AST)
    print("  reference:", REF)
    ok = self_verify()
    if not ok:
        print("SELF-VERIFY FAILED"); sys.exit(1)
    print("SELF-VERIFY OK: gold PASS + all negatives FAIL")
    # also run the emitted parser on sample A to show a real CSV (sanity)
    tmp = tempfile.mkdtemp(prefix="demo_")
    try:
        subprocess.run([sys.executable, os.path.join(REF, "gen_spf_coupling_parser.py"),
                        os.path.join(REF, "spec_a.json"), tmp], check=True)
        subprocess.run([sys.executable, os.path.join(tmp, "parse_spf_cc.py"),
                        os.path.join(AST, "sample_a.spf_CC"), tmp], check=True)
        print("--- demo sabl_summary_a.csv (sample A) ---")
        print(open(os.path.join(tmp, "sabl_summary_a.csv")).read())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
