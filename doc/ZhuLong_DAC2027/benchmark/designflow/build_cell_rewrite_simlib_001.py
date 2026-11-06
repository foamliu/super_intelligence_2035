#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-CellRewriteSimlib-001 (shard D, schematic_netlist).
A-faithful prompt = trace 2w4ol U#2 verbatim (netlist rewrite with simlib_base.sv
physical cells + & / | logic merge, preserve power/bulk pins + specify timing).
B-grade synthesized assets (real /proj netlist unattachable).
Deliverable = rewrite_netlist.py (CLI <netlist.sv> <simlib_base.sv> -o <out.sv>).
check.py runs candidate on hidden B (and re-runs on A for anti-hardcode).
16 independent conditions a-p.
"""
import os, json, hashlib, shutil, subprocess, sys, zipfile, io

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "cell_rewrite_simlib_001"
CASE_ID = "EDA-Eval-DesignFlow-CellRewriteSimlib-001"
AST = os.path.join(REPO, "assets", CASE)
REF = os.path.join(REPO, "reference", CASE)
HID = os.path.join(AST, "hidden")
NEG = os.path.join(REF, "negative")
for d in (AST, REF, HID, NEG):
    os.makedirs(d, exist_ok=True)

# ---------- simlib_base.sv (shared by A, B, B2) ----------
SIMLIB_BASE = """`celldefine
module inv_base ( Y, A, vcc_, vss_, vbulkn_, vbulkp_ );
  output Y; input A; inout vcc_, vss_, vbulkn_, vbulkp_;
  parameter string strength1 = "strong1";
  parameter string strength0 = "strong0";
  assign Y = ~A;
endmodule
module buf_base ( Y, A, vcc_, vss_, vbulkn_, vbulkp_ );
  output Y; input A; inout vcc_, vss_, vbulkn_, vbulkp_;
  parameter string strength1 = "strong1";
  parameter string strength0 = "strong0";
  assign Y = A;
endmodule
module fgc_pwrstate_monitor ( celltype, sin, sout, vpwr, vgnd, vblkn, vblkp );
  input [4095:0] celltype; input sin; output sout; inout vpwr, vgnd, vblkn, vblkp;
  assign sout = sin;
endmodule
`endcelldefine
"""

# input names per arity
def _inputs(n):
    return ["A", "B", "C", "D", "E", "F"][:n]

def _assign_expr(typ, n):
    ins = _inputs(n)
    if typ == "nand":
        return "~(" + " & ".join(ins) + ")"
    if typ == "and":
        return "(" + " & ".join(ins) + ")"
    if typ == "nor":
        return "~(" + " | ".join(ins) + ")"
    if typ == "or":
        return "(" + " | ".join(ins) + ")"
    if typ == "inv":
        return "~" + ins[0]
    raise ValueError(typ)

def gen_cell_module(name, typ, n, tRise="15", tFall="15"):
    ins = _inputs(n)
    ports = ["Y"] + ins + ["inh_vcc", "inh_vss", "inh_vbn", "inh_vbp"]
    hdr = "module %s ( %s );" % (name, ", ".join(ports))
    decls = ["  output Y;"] + ["  input %s;" % i for i in ins] + \
            ["  inout inh_vcc, inh_vss, inh_vbn, inh_vbp;"]
    params = ['  parameter string strength1 = "strong1";',
              '  parameter string strength0 = "strong0";']
    assign = "  assign Y = %s;" % _assign_expr(typ, n)
    arcs = "\n".join("    (%s => Y) = (tRise, tFall);" % i for i in ins)
    spec = """  specify
    specparam tRise = %s*`CDLYW:25*`CDLYW:40*`CDLYW, tFall = %s*`CDLYW:25*`CDLYW:40*`CDLYW;
%s
  endspecify""" % (tRise, tFall, arcs)
    return "`celldefine\n" + hdr + "\n" + "\n".join(decls) + "\n" + "\n".join(params) + "\n" + assign + "\n" + spec + "\nendmodule\n`endcelldefine\n"

def gen_netlist(cells, label):
    out = ["// Auto-generated netlist for %s — cells not in simlib_base.sv need rewrite." % label, ""]
    for (name, typ, n, *rest) in cells:
        tr = rest[0] if rest else "15"
        out.append(gen_cell_module(name, typ, n, tr))
    return "\n".join(out)

# A: 6 cells (the visible input)
A_CELLS = [
    ("nand2IOLVx2", "nand", 2),
    ("nand3IOLVx2", "nand", 3),
    ("nor2IOLVx2",  "nor",  2),
    ("and2IOLVx2",  "and",  2),
    ("or2IOLVx2",   "or",   2),
    ("inv1DSx1",    "inv",  1),
]
# B: structurally different names + arities overlap but distinct strings
B_CELLS = [
    ("nand2LVx4",  "nand", 2),
    ("nand3IOLVx1", "nand", 3),
    ("nor2LVx2",   "nor",  2),
    ("and2LVx4",   "and",  2),
    ("or2LVx1",    "or",   2),
    ("inv1DSx2",   "inv",  1),
]
# B2: fewer cells, different names (cross-input guard)
B2_CELLS = [
    ("nand2DGx2",  "nand", 2),
    ("nor2DGx1",   "nor",  2),
    ("and2DGx1",   "and",  2),
    ("inv1DGx4",   "inv",  1),
]

NETLIST_A = gen_netlist(A_CELLS, "A")
NETLIST_B = gen_netlist(B_CELLS, "B (hidden)")
NETLIST_B2 = gen_netlist(B2_CELLS, "B2 (hidden cross-input)")

# ---------- prompt (A-faithful, U#2 verbatim from trace 2w4ol) ----------
PROMPT = """请修改 netlist 文件。其中有些模块用到的 cell 在 simlib_base.sv 中不存在，无法直接读取，请结合 simlib_base.sv 把它们替换掉。 约束如下（务必严格遵守）： 优先复用 simlib_base.sv 中【自带电源/衬底引脚】的物理单元积木 分工规则（这是重点）： 凡是有“延时/时序/驱动强度”等物理效应的部分，必须用库内物理单元实现， 并把 vcc_/vss_/vbulkp_/vbulkn_ 等电源与衬底脚真实接进这些物理单元； 凡是对输出没有延时、没有物理影响的纯逻辑输入合并，一律直接用 位与 &（或 |、^ 等）逻辑表达式在这个物理单元的前端拼接完成， 不要再把它们拆成单独的晶体管堆或单独的门级模块。 不要下面这两种做法： 不要用纯行为/无电源脚的 UDP 原语来形成单纯的逻辑电路， 因为它无法承接 vcc/vss/bulk，电源腿会变成悬空摆设； 尽量不要把原始cell都做成独立的 pp/nn 晶体管串并联堆，除非没有模块可以实现对应功能 那既啰嗦又违背第2条“无延时输入用 &”的规则。 每个被替换的 cell，先用真值表和器件原理分析，再用 simlib_base.sv 里的 物理单元 + & 组合式地复原出逻辑功能，并保持时序/保持行为一致。 改写时保留原 cell 的所有参数与连接关系（电源脚、衬底脚、端口名都要保留）。 输出要求： 在对话窗口打印每处被替换的原始行和替换后的行； 无须实际改写 netlist 文件； 最后用真值表穷举（含保持态/上一值）验证替换前后等价。"""

TASK_BRIEF = """交付接口：submit.zip 内含 rewrite_netlist.py，CLI 用法 `python3 rewrite_netlist.py <input_netlist.sv> <simlib_base.sv> -o <out.sv>`。
输入文件位置：assets/ 下 input_netlist_A.sv 与 simlib_base.sv（A 为可见样例）。
判分用隐藏输入 B（结构不同）调用同一脚本，校验改写规则与布尔等价。"""

HIDDEN_MANIFEST = {
    "case_id": CASE_ID,
    "hidden_inputs": [
        {"name": "input_netlist_B.sv", "purpose": "primary hidden check input"},
        {"name": "input_netlist_B2.sv", "purpose": "cross-input guard"},
    ],
    "simlib_base": "simlib_base.sv (shared, identical to visible A)",
    "note": "B/B2 netlists are NOT placed in the SUT sandbox; check.py embeds them.",
}

# ---------- gold rewriter ----------
GOLD = r'''#!/usr/bin/env python3
"""Reference netlist rewriter: replace non-simlib_base cells with inv_base/buf_base
+ & / | logic merge, preserving ports, params (strength1/strength0), power/bulk
pins (vcc_/vss_/vbulkn_/vbulkp_), and specify timing blocks.
CLI: python3 rewrite_netlist.py <input_netlist.sv> <simlib_base.sv> -o <out.sv>
"""
import sys, re, argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("netlist")
    ap.add_argument("simlib")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    with open(a.simlib, "r", errors="replace") as f:
        simlib_txt = f.read()
    with open(a.netlist, "r", errors="replace") as f:
        net_txt = f.read()
    base_names = set(re.findall(r"^\s*module\s+(\w+)\s*\(", simlib_txt, re.M))
    out_modules = []
    # split netlist into modules (top-level `celldefine ... endmodule blocks)
    blocks = re.split(r"(`celldefine)", net_txt)
    # reassemble: pairs of `celldefine + body
    chunks = []
    for i in range(1, len(blocks), 2):
        body = (blocks[i] + (blocks[i+1] if i+1 < len(blocks) else ""))
        chunks.append(body)
    if not chunks:
        # fallback: split by module keyword
        chunks = re.split(r"(?m)^(?=\s*module\s)", net_txt)
        chunks = [c for c in chunks if c.strip()]
    for ch in chunks:
        m = re.search(r"module\s+(\w+)\s*\(([^)]*)\)", ch)
        if not m:
            continue
        name = m.group(1)
        if name in base_names:
            out_modules.append(ch.rstrip())
            continue
        # parse port list
        port_list = [p.strip() for p in m.group(2).split(",") if p.strip()]
        # parse directions
        out_decls = re.findall(r"^\s*(output|input|inout)\s+([^;]+);", ch, re.M)
        inputs = []
        power = {}
        for d, names in out_decls:
            for nm in [x.strip() for x in names.split(",") if x.strip()]:
                if d == "input":
                    inputs.append(nm)
                elif d == "inout":
                    power[nm] = nm
        # classify by name prefix
        low = name.lower()
        if low.startswith("nand"):
            base, op = "inv_base", "&"
        elif low.startswith("nor"):
            base, op = "inv_base", "|"
        elif low.startswith("and"):
            base, op = "buf_base", "&"
        elif low.startswith("or"):
            base, op = "buf_base", "|"
        elif low.startswith("inv"):
            base, op = "inv_base", None
        else:
            # unknown: leave unchanged
            out_modules.append(ch.rstrip())
            continue
        # build .A expression
        if op is None:
            a_expr = inputs[0] if inputs else "1'b0"
        else:
            a_expr = (" %s " % op).join(inputs)
            a_expr = "(" + a_expr + ")"
        # map power inouts to base pins
        vcc  = power.get("inh_vcc",  "inh_vcc")
        vss  = power.get("inh_vss",  "inh_vss")
        vbn  = power.get("inh_vbn",  "inh_vbn")
        vbp  = power.get("inh_vbp",  "inh_vbp")
        inst = ("  %s #(strength1, strength0) I_rw0 (.A(%s), .Y(Y), "
                ".vcc_(%s), .vss_(%s), .vbulkn_(%s), .vbulkp_(%s));") % (
                base, a_expr, vcc, vss, vbn, vbp)
        # rebuild module: header + decls + params + inst + specify
        # extract specify block
        sp = re.search(r"(\s*specify\b.*?endspecify\s*)", ch, re.S)
        specify_block = sp.group(1) if sp else ""
        # header line
        hdr = re.search(r"(`celldefine\s*module\s+\w+\s*\([^)]*\)\s*;)", ch).group(1)
        # decls + params (lines before assign)
        pre_assign = re.split(r"^\s*assign\b", ch, flags=re.M)[0]
        # keep lines: decls + params (drop `celldefine/module line already in hdr)
        decl_param_lines = [ln for ln in pre_assign.splitlines()
                            if ln.strip() and not ln.strip().startswith("`celldefine")
                            and not re.match(r"\s*module\s", ln)]
        body_lines = [hdr] + decl_param_lines + [inst]
        if specify_block:
            body_lines.append(specify_block.rstrip())
        body_lines.append("endmodule")
        body_lines.append("`endcelldefine")
        out_modules.append("\n".join(body_lines))
    with open(a.out, "w") as f:
        f.write("// rewritten netlist\n")
        for m in out_modules:
            f.write(m + "\n\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

# ---------- check.py (16 conditions a-p) ----------
CHECK = r'''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-CellRewriteSimlib-001.
16 independent conditions a-p. Returns "PASS" or raises AssertionError.
"""
import os, sys, re, json, subprocess, tempfile, hashlib, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(HERE, "..", "..", "assets", "cell_rewrite_simlib_001")
def _rd(rel):
    p = os.path.join(AST, rel)
    with open(p, "r", errors="replace") as f:
        return f.read()
SIMLIB_BASE = _rd("simlib_base.sv")
NETLIST_A = _rd("input_netlist_A.sv")
NETLIST_B = _rd(os.path.join("hidden", "input_netlist_B.sv"))
NETLIST_B2 = _rd(os.path.join("hidden", "input_netlist_B2.sv"))

FORBIDDEN_IMPORTS = ("ref", "reference", "check", "gold", "answer", "_reference_check")
LEAK_PAT = re.compile(r"/proj/|/rundata/|/home/[a-zA-Z0-9]+/\.|/home/[a-zA-Z0-9]+/Documents")
A_NAMES = ["nand2IOLVx2", "nand3IOLVx2", "nor2IOLVx2", "and2IOLVx2", "or2IOLVx2", "inv1DSx1"]
B_NAMES = ["nand2LVx4", "nand3IOLVx1", "nor2LVx2", "and2LVx4", "or2LVx1", "inv1DSx2"]

def _eval_expr(expr, input_names):
    """Eval a Verilog boolean expr (~ & | ()) over all input combos."""
    e = re.sub(r"~", " not ", expr)
    e = re.sub(r"&", " and ", e)
    e = e.replace("|", " or ")
    # sanitize
    if not re.match(r"^[\w\s()\.\']+$", e.replace("not", "").replace("and", "").replace("or", "")):
        # has 1'b0 etc -> handle
        e = re.sub(r"1'b0", "False", e)
        e = re.sub(r"1'b1", "True", e)
    results = []
    n = len(input_names)
    for bits in range(1 << n):
        env = {input_names[i]: bool((bits >> i) & 1) for i in range(n)}
        try:
            results.append(bool(eval(e, {"__builtins__": {}}, env)))
        except Exception:
            return None
    return results

def _base_names():
    return set(re.findall(r"^\s*module\s+(\w+)\s*\(", SIMLIB_BASE, re.M))

def _extract_a_expr(mbody):
    """Extract balanced-paren content of .A(...) from a module body."""
    i = mbody.find(".A")
    if i < 0:
        return None
    j = mbody.find("(", i)
    if j < 0:
        return None
    depth = 0
    k = j
    while k < len(mbody):
        c = mbody[k]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return mbody[j+1:k]
        k += 1
    return None

def _run_cand(src, netlist_text, workdir):
    simlib_path = os.path.join(workdir, "simlib_base.sv")
    net_path = os.path.join(workdir, "in_net.sv")
    out_path = os.path.join(workdir, "out.sv")
    with open(simlib_path, "w") as f:
        f.write(SIMLIB_BASE)
    with open(net_path, "w") as f:
        f.write(netlist_text)
    r = subprocess.run([sys.executable, src, net_path, simlib_path, "-o", out_path],
                       capture_output=True, text=True, timeout=60)
    out_txt = ""
    if os.path.exists(out_path):
        with open(out_path, "r", errors="replace") as f:
            out_txt = f.read()
    return r.returncode, r.stdout, r.stderr, out_txt

def _parse_modules(txt):
    mods = {}
    for m in re.finditer(r"module\s+(\w+)\s*\(([^)]*)\)\s*;(.*?)endmodule", txt, re.S):
        name = m.group(1)
        mods[name] = m.group(0)
    return mods

def check(deliverable, workdir):
    # extract submit.zip
    tmp = tempfile.mkdtemp(prefix="_chk_", dir=tempfile.gettempdir())
    try:
        zpath = deliverable
        if not os.path.exists(zpath):
            zpath = os.path.join(workdir, deliverable)
        if not os.path.exists(zpath):
            raise AssertionError("(a) submit.zip not found")
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        src = None
        for fn in os.listdir(tmp):
            if fn == "rewrite_netlist.py" or (fn.endswith(".py") and src is None):
                src = os.path.join(tmp, fn)
        if not src:
            raise AssertionError("(a) no .py script in submit.zip")
        with open(src, "r", errors="replace") as f:
            src_txt = f.read()

        # (a) zip structure + no forbidden imports + no leak + no import ref
        names = [n for n in zipfile.ZipFile(zpath).namelist()]
        if not any(n.endswith(".py") for n in names):
            raise AssertionError("(a) no python file in zip")
        for imp in FORBIDDEN_IMPORTS:
            if re.search(r"\bimport\s+%s\b|\bfrom\s+%s\b" % (imp, imp), src_txt):
                raise AssertionError("(a) forbidden import: %s" % imp)
        if LEAK_PAT.search(src_txt):
            raise AssertionError("(a) leak path in source")

        # (b) py_compile
        rc = subprocess.run([sys.executable, "-m", "py_compile", src],
                            capture_output=True, text=True)
        if rc.returncode != 0:
            raise AssertionError("(b) py_compile failed: %s" % rc.stderr[:200])

        # run on B
        rcB, outB, errB, svB = _run_cand(src, NETLIST_B, tmp)
        # (c) B run exit0 + non-empty
        if rcB != 0:
            raise AssertionError("(c) B run exit=%d err=%s" % (rcB, errB[:200]))
        if not svB.strip():
            raise AssertionError("(c) B output empty")

        base = _base_names()
        modsB = _parse_modules(svB)

        # (d) output instances use only base names; no leftover primitive gates
        for mname, mbody in modsB.items():
            if mname in base:
                continue
            # find instantiated module names
            insts = re.findall(r"\b(inv_base|buf_base|fgc_pwrstate_monitor|nand\d|nor\d|and\d|or\d|inv\d|nand[0-9]IOLV|pmos|nmos|cmos|tran)\b", mbody)
            bad = [x for x in insts if x not in base]
            if bad:
                raise AssertionError("(d) module %s uses non-base cells: %s" % (mname, bad))
            # no assign-based primitive gates left as the function driver
            if re.search(r"\bassign\s+Y\s*=", mbody) and "inv_base" not in mbody and "buf_base" not in mbody:
                raise AssertionError("(d) module %s keeps primitive assign, no base instance" % mname)

        # (e) power pins connected in each inv_base/buf_base instance
        for mname, mbody in modsB.items():
            if mname in base:
                continue
            for inst in re.finditer(r"(inv_base|buf_base)\s*#\([^)]*\)\s+\w+\s*\(([^;]*\))\s*;", mbody, re.S):
                pinblock = inst.group(2)
                for pin, val in [(".vcc_", "inh_vcc"), (".vss_", "inh_vss"),
                                 (".vbulkn_", "inh_vbn"), (".vbulkp_", "inh_vbp")]:
                    if not re.search(r"%s\s*\(\s*%s\s*\)" % (re.escape(pin), val), pinblock):
                        raise AssertionError("(e) %s pin %s not connected to %s in %s"
                                             % (mname, pin, val, pinblock[:120]))

        # (f) inverting -> inv_base ; non-inverting -> buf_base
        for mname, mbody in modsB.items():
            if mname in base:
                continue
            low = mname.lower()
            want_inv = low.startswith("nand") or low.startswith("nor") or low.startswith("inv")
            has_inv = "inv_base" in mbody
            has_buf = "buf_base" in mbody
            if want_inv and not has_inv:
                raise AssertionError("(f) %s should use inv_base" % mname)
            if (not want_inv) and not has_buf:
                raise AssertionError("(f) %s should use buf_base" % mname)
            if want_inv and has_buf:
                raise AssertionError("(f) %s inverting but uses buf_base" % mname)

        # (g) .A expr uses & for and/nand, | for or/nor
        for mname, mbody in modsB.items():
            if mname in base:
                continue
            low = mname.lower()
            am = _extract_a_expr(mbody)
            if not am:
                raise AssertionError("(g) %s no .A expr" % mname)
            aexpr = am
            if low.startswith("nand") or low.startswith("and"):
                if "&" not in aexpr and len([x for x in re.findall(r"\b[A-E]\b", aexpr)]) > 1:
                    raise AssertionError("(g) %s and/nand should use & got: %s" % (mname, aexpr))
            if low.startswith("nor") or low.startswith("or"):
                if "|" not in aexpr and len([x for x in re.findall(r"\b[A-E]\b", aexpr)]) > 1:
                    raise AssertionError("(g) %s or/nor should use | got: %s" % (mname, aexpr))

        # (h) no UDP primitives
        if re.search(r"\bprimitive\b|\bendprimitive\b|\btable\b|\bendtable\b", svB):
            raise AssertionError("(h) UDP primitive found in output")

        # (i) no transistor instances
        if re.search(r"\b(pmos|nmos|cmos|rcmos|rpmos|rnmos|tran|tranif[01]|rtran|rbp|bxn)\b", svB):
            raise AssertionError("(i) transistor instance found in output")

        # (j) module ports preserved
        origBmods = _parse_modules(NETLIST_B)
        for mname, mbody in modsB.items():
            if mname in base or mname not in origBmods:
                continue
            oph = re.search(r"module\s+%s\s*\(([^)]*)\)\s*;" % re.escape(mname), origBmods[mname])
            nph = re.search(r"module\s+%s\s*\(([^)]*)\)\s*;" % re.escape(mname), mbody)
            if not (oph and nph):
                raise AssertionError("(j) %s header missing" % mname)
            oports = [p.strip() for p in oph.group(1).split(",") if p.strip()]
            nports = [p.strip() for p in nph.group(1).split(",") if p.strip()]
            if oports != nports:
                raise AssertionError("(j) %s ports differ: %s vs %s" % (mname, oports, nports))

        # (k) params preserved (strength1/strength0)
        for mname, mbody in modsB.items():
            if mname in base:
                continue
            if "strength1" not in mbody or "strength0" not in mbody:
                raise AssertionError("(k) %s missing strength params" % mname)

        # (l) specify block preserved
        for mname, mbody in modsB.items():
            if mname in base:
                continue
            if mname in origBmods and "specify" in origBmods[mname]:
                if "specify" not in mbody or "endspecify" not in mbody:
                    raise AssertionError("(l) %s specify block dropped" % mname)

        # (m) boolean equivalence original vs rewritten (all input combos)
        for mname, mbody in modsB.items():
            if mname in base or mname not in origBmods:
                continue
            low = mname.lower()
            # original assign
            oam = re.search(r"assign\s+Y\s*=\s*([^;]+);", origBmods[mname])
            if not oam:
                continue
            orig_expr = oam.group(1).strip()
            # rewritten: .A expr + cell type
            am = _extract_a_expr(mbody)
            if not am:
                raise AssertionError("(m) %s no .A for equivalence" % mname)
            aexpr = am.strip()
            if "inv_base" in mbody:
                rw_expr = "~(" + aexpr + ")"
            else:
                rw_expr = "(" + aexpr + ")"
            # input names from port decls
            decls = re.findall(r"^\s*input\s+([^;]+);", origBmods[mname], re.M)
            ins = []
            for d in decls:
                ins.extend([x.strip() for x in d.split(",") if x.strip()])
            orig_vals = _eval_expr(orig_expr, ins)
            rw_vals = _eval_expr(rw_expr, ins)
            if orig_vals is None:
                raise AssertionError("(m) %s orig expr eval failed: %s" % (mname, orig_expr))
            if rw_vals is None:
                raise AssertionError("(m) %s rewritten expr eval failed: %s" % (mname, rw_expr))
            if orig_vals != rw_vals:
                raise AssertionError("(m) %s not equivalent: %s vs %s" % (mname, orig_expr, rw_expr))

        # (n) cross-input B: B module names present, A-specific names absent
        for bn in B_NAMES:
            if bn not in svB:
                raise AssertionError("(n) B name %s absent from B output" % bn)
        for an in A_NAMES:
            if an in svB:
                raise AssertionError("(n) A name %s leaked into B output (hardcoded-A)" % an)

        # (o) anti-hardcode: source has no A-specific literals; re-run on A works
        for an in A_NAMES:
            if an in src_txt:
                raise AssertionError("(o) A-specific name %s hardcoded in source" % an)
        rcA, outA, errA, svA = _run_cand(src, NETLIST_A, tmp)
        if rcA != 0 or not svA.strip():
            raise AssertionError("(o) A re-run failed exit=%d" % rcA)
        for an in A_NAMES:
            if an not in svA:
                raise AssertionError("(o) A name %s missing from A output" % an)

        # (p) determinism + CLI
        rcB2, _, _, svB2 = _run_cand(src, NETLIST_B, tmp)
        rcB3, _, _, svB3 = _run_cand(src, NETLIST_B, tmp)
        h1 = hashlib.sha256(svB.encode()).hexdigest()
        h2 = hashlib.sha256(svB2.encode()).hexdigest()
        h3 = hashlib.sha256(svB3.encode()).hexdigest()
        if not (h1 == h2 == h3):
            raise AssertionError("(p) non-deterministic: %s %s %s" % (h1[:8], h2[:8], h3[:8]))
        if "argparse" not in src_txt and "sys.argv" not in src_txt:
            raise AssertionError("(p) no CLI (argparse/sys.argv) in source")
        # B2 cross-input guard (bonus distinctness from B)
        rcB2x, _, _, svB2x = _run_cand(src, NETLIST_B2, tmp)
        if rcB2x != 0 or not svB2x.strip():
            raise AssertionError("(p) B2 cross-input run failed")

        return "PASS (16/16 conditions a-p)"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    try:
        res = check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ".")
        print(res)
    except AssertionError as e:
        print("FAIL:", e)
        sys.exit(1)
'''

# ---------- negatives ----------
NEG_EMPTY = "# empty stub\n"
NEG_PRINT_B = '''#!/usr/bin/env python3
import sys
# hardcoded B output (print the expected B rewritten netlist)
OUT = """// rewritten netlist
`celldefine
module nand2LVx4 ( Y, A, B, inh_vcc, inh_vss, inh_vbn, inh_vbp );
  output Y; input A; input B; inout inh_vcc, inh_vss, inh_vbn, inh_vbp;
  parameter string strength1 = "strong1";
  parameter string strength0 = "strong0";
  inv_base #(strength1, strength0) I_rw0 (.A((A & B)), .Y(Y), .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
  specify
    specparam tRise = 15*`CDLYW:25*`CDLYW:40*`CDLYW, tFall = 15*`CDLYW:25*`CDLYW:40*`CDLYW;
    (A => Y) = (tRise, tFall); (B => Y) = (tRise, tFall);
  endspecify
endmodule
`endcelldefine
"""
with open(sys.argv[sys.argv.index("-o")+1], "w") as f:
    f.write(OUT)
'''
NEG_HARDCODE_A = '''#!/usr/bin/env python3
import sys
# hardcodes A-specific cell names -> fails (n) A-name-leak-into-B and (o)
OUT = """// rewritten
module nand2IOLVx2 ... endmodule
module nand3IOLVx2 ... endmodule
"""
with open(sys.argv[sys.argv.index("-o")+1], "w") as f:
    f.write(OUT)
'''
NEG_SYNTAX = '''#!/usr/bin/env python3
def broken(
'''
NEG_NO_OUTPUT = '''#!/usr/bin/env python3
import sys
# does nothing
pass
'''
NEG_WRONG_BASE = '''#!/usr/bin/env python3
# uses buf_base for inverting nand (fails f) and wrong op (g)
import sys, re
simlib = open(sys.argv[2]).read()
net = open(sys.argv[1]).read()
out = open(sys.argv[sys.argv.index("-o")+1], "w")
out.write("// rewritten\n")
for m in re.finditer(r"module\s+(\w+)\s*\(([^)]*)\)\s*;(.*?)endmodule", net, re.S):
    name = m.group(1)
    if name in set(re.findall(r"module\s+(\w+)", simlib)):
        out.write(m.group(0)+"\n\n"); continue
    out.write("module %s (...); buf_base I (.A(A), .Y(Y), .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp)); endmodule\n\n" % name)
out.close()
'''
NEG_NO_POWER = '''#!/usr/bin/env python3
# inv_base but no power pins connected (fails e)
import sys, re
simlib = open(sys.argv[2]).read()
net = open(sys.argv[1]).read()
out = open(sys.argv[sys.argv.index("-o")+1], "w")
out.write("// rewritten\n")
for m in re.finditer(r"module\s+(\w+)\s*\(([^)]*)\)\s*;(.*?)endmodule", net, re.S):
    name = m.group(1)
    if name in set(re.findall(r"module\s+(\w+)", simlib)):
        out.write(m.group(0)+"\n\n"); continue
    low = name.lower()
    base = "inv_base" if (low.startswith("nand") or low.startswith("nor") or low.startswith("inv")) else "buf_base"
    out.write("module %s ( Y, A, B, inh_vcc, inh_vss, inh_vbn, inh_vbp ); output Y; input A; input B; inout inh_vcc, inh_vss, inh_vbn, inh_vbp; parameter string strength1 = \\"strong1\\"; parameter string strength0 = \\"strong0\\"; %s I_rw0 (.A((A & B)), .Y(Y)); specify specparam tRise = 15*`CDLYW:25*`CDLYW:40*`CDLYW, tFall = 15*`CDLYW:25*`CDLYW:40*`CDLYW; (A => Y) = (tRise, tFall); (B => Y) = (tRise, tFall); endspecify endmodule\n\n" % (name, base))
out.close()
'''

NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest: all negatives must FAIL check()."""
import os, sys, tempfile, zipfile, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check.py")
NEG = os.path.join(HERE, "negative")
def run(negname):
    src = os.path.join(NEG, negname)
    tmp = tempfile.mkdtemp(prefix="_neg_", dir=tempfile.gettempdir())
    try:
        zp = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.write(src, "rewrite_netlist.py")
        r = subprocess.run([sys.executable, CHECK, zp, tmp], capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout[:200] + r.stderr[:200]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
results = {}
for n in sorted(os.listdir(NEG)):
    if not n.endswith(".py"):
        continue
    rc, out = run(n)
    results[n] = (rc, out)
    print("%s -> rc=%d %s" % (n, rc, "FAIL-OK" if rc != 0 else "PASS-BAD"))
bad = [n for n, (rc, _) in results.items() if rc == 0]
if bad:
    print("NEG_SELFTEST FAIL: these negatives passed (should fail):", bad)
    sys.exit(1)
print("NEG_SELFTEST PASS: all %d negatives FAIL check()" % len(results))
'''

def write(p, content):
    with open(p, "w") as f:
        f.write(content)
    return p

# write assets
write(os.path.join(AST, "simlib_base.sv"), SIMLIB_BASE)
write(os.path.join(AST, "input_netlist_A.sv"), NETLIST_A)
write(os.path.join(AST, "prompt.txt"), PROMPT)
write(os.path.join(AST, "task_brief.md"), TASK_BRIEF)
write(os.path.join(HID, "input_netlist_B.sv"), NETLIST_B)
write(os.path.join(HID, "input_netlist_B2.sv"), NETLIST_B2)
write(os.path.join(HID, "hidden_manifest.json"), json.dumps(HIDDEN_MANIFEST, indent=2, ensure_ascii=False))

# write reference
gold_path = write(os.path.join(REF, "rewrite_netlist_ref.py"), GOLD)
check_path = write(os.path.join(REF, "check.py"), CHECK)
write(os.path.join(REF, "negative_selftest.py"), NEG_SELFTEST)
write(os.path.join(NEG, "empty_shell.py"), NEG_EMPTY)
write(os.path.join(NEG, "print_expected_B.py"), NEG_PRINT_B)
write(os.path.join(NEG, "hardcode_a.py"), NEG_HARDCODE_A)
write(os.path.join(NEG, "syntax_err.py"), NEG_SYNTAX)
write(os.path.join(NEG, "no_output.py"), NEG_NO_OUTPUT)
write(os.path.join(NEG, "wrong_base.py"), NEG_WRONG_BASE)
write(os.path.join(NEG, "no_power.py"), NEG_NO_POWER)

# build reference_submit.zip (gold script)
refsubmit = os.path.join(REF, "reference_submit.zip")
if os.path.exists(refsubmit):
    os.remove(refsubmit)
with zipfile.ZipFile(refsubmit, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(gold_path, "rewrite_netlist.py")

print("built", CASE_ID)
print("assets:", AST)
print("reference:", REF)
print("gold sha256:", hashlib.sha256(open(gold_path, 'rb').read()).hexdigest()[:12])
print("check sha256:", hashlib.sha256(open(check_path, 'rb').read()).hexdigest()[:12])
print("A cells:", [c[0] for c in A_CELLS])
print("B cells:", [c[0] for c in B_CELLS])
print("B2 cells:", [c[0] for c in B2_CELLS])
