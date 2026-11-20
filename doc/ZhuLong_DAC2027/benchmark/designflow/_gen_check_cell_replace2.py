#!/usr/bin/env python3
"""Generate check.py for NetlistCellReplace-001 with embedded B/B2 assets."""
import os
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
AST = BENCH + "/assets/EDA-Eval-DesignFlow-NetlistCellReplace-001"
REF = BENCH + "/reference/EDA-Eval-DesignFlow-NetlistCellReplace-001"

netB = open(AST+"/hidden/hidden_netlist_B.v").read()
simB = open(AST+"/hidden/hidden_simlib_B.sv").read()
netB2 = open(AST+"/hidden/hidden_netlist_B2.v").read()
simB2 = open(AST+"/hidden/hidden_simlib_B2.sv").read()

TEMPLATE = r'''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-NetlistCellReplace-001.
16 conditions a-p. Runs candidate on hidden B/B2 netlists + simlibs.
"""
import sys, os, re, io, zipfile, subprocess, hashlib, tempfile, shutil, py_compile

NET_B = __NET_B__
SIM_B = __SIM_B__
NET_B2 = __NET_B2__
SIM_B2 = __SIM_B2__

A_NAMES = ["LatchTopA","my_nand2A","my_nand3A","vdda","gnda","vbpa","vbna",
           "nand2pA","nand3pA","invpA","nandrslatchA","vcc_","vss_","vbulkp_","vbulkn_"]
B_UNKNOWN = ["NA2_B","NA3_B"]
B_SIMLIB = ["ND2P_B","ND3P_B","IVP_B","rslatch_B","nor2p","oai21p"]
B_POWER = ["pvdd","pgnd","psub","nsub"]
B_PORTS = ["Y","S","R0","R1","pvdd","nsub","psub","pgnd"]
B2_UNKNOWN = ["XN2_C","XN3_C"]
FORBIDDEN_IMPORTS = ["ref_check","reference","_reference","check_py","gold","answer",
    "_gold","_ref","socket","urllib","requests","pty","http.client","ftplib",
    "telnetlib","smtplib"]
FORBIDDEN_PATHS = ["/proj/","/rundata/","/home/"]

def parse_modules(text):
    mods = {}
    for m in re.finditer(r'module\s+(\w+)\s*\(([^)]*)\)\s*;(.*?)endmodule', text, re.S):
        name = m.group(1)
        ports = [p.strip() for p in m.group(2).split(',') if p.strip()]
        mods[name] = {'ports': ports, 'body': m.group(3), 'kind': 'module'}
    for m in re.finditer(r'primitive\s+(\w+)\s*\(([^)]*)\)\s*;(.*?)endprimitive', text, re.S):
        name = m.group(1)
        ports = [p.strip() for p in m.group(2).split(',') if p.strip()]
        mods[name] = {'ports': ports, 'body': m.group(3), 'kind': 'primitive'}
    return mods

def parse_assigns(body):
    out = {}
    for m in re.finditer(r'assign\s+(\w+)\s*=\s*([^;]+);', body):
        out[m.group(1)] = m.group(2).strip()
    return out

def parse_instantiations(body):
    insts = []
    for m in re.finditer(r'\b(\w+)\s+(\w+)\s*\((.*?)\)\s*;', body, re.S):
        cell, inst, ports_str = m.group(1), m.group(2), m.group(3)
        if cell in ('assign','module','endmodule','endprimitive','primitive','generate',
                     'endgenerate','if','else','begin','end','parameter','localparam',
                     'wire','reg','input','output','inout','timescale','celldefine',
                     'endcelldefine'):
            continue
        pmap = {}
        for pm in re.finditer(r'\.(\w+)\s*\(([^)]*)\)', ports_str):
            pmap[pm.group(1)] = pm.group(2).strip()
        if pmap:
            insts.append((cell, inst, pmap))
    return insts

def eval_expr(expr, env):
    e = expr.replace('&&','&').replace('||','|').replace('!','~')
    tokens = re.findall(r'[~&|^()]|\w+', e)
    pos = [0]
    def peek(): return tokens[pos[0]] if pos[0] < len(tokens) else None
    def consume():
        t = tokens[pos[0]]; pos[0]+=1; return t
    def pexpr(): return por()
    def por():
        v = pxor()
        while peek()=='|': consume(); v = v | pxor()
        return v
    def pxor():
        v = pand()
        while peek()=='^': consume(); v = v ^ pand()
        return v
    def pand():
        v = punary()
        while peek()=='&': consume(); v = v & punary()
        return v
    def punary():
        if peek()=='~': consume(); return ~punary() & 1
        return patom()
    def patom():
        t = consume()
        if t=='(':
            v = pexpr()
            if peek()==')': consume()
            return v
        if t in ('0','1'): return int(t)
        val = env.get(t, 0)
        return int(val) & 1 if isinstance(val,(int,float)) else 0
    return pexpr() & 1

def eval_latch_orig(S, R0, R1, Y_prev):
    nr = (~(R0 & R1 & Y_prev)) & 1
    nq = (~(S & nr)) & 1
    return nq

def eval_modified_net(modified_text, sim_mods, S, R0, R1, Y_prev):
    mods = parse_modules(modified_text)
    all_mods = dict(sim_mods)
    all_mods.update(mods)
    top = None
    for name, md in mods.items():
        if 'inout' in md['body'] or parse_instantiations(md['body']):
            top = (name, md); break
    if top is None:
        for name, md in mods.items():
            top = (name, md); break
    if top is None:
        return None
    topname, topdef = top
    insts = parse_instantiations(topdef['body'])
    assigns = parse_assigns(topdef['body'])
    fb_wire = None
    for tgt, expr in assigns.items():
        if tgt == 'Y' and re.match(r'^\w+$', expr):
            fb_wire = expr
    if fb_wire is None:
        fb_wire = 'nq'
    env = {'S': S, 'R0': R0, 'R1': R1, fb_wire: Y_prev, 'Y': Y_prev}
    fb_driver = None
    for tgt, expr in assigns.items():
        if tgt == 'Y': continue
        if re.match(r'^\w+$', expr) and expr in env:
            env[tgt] = env[expr]
        else:
            env[tgt] = eval_expr(expr, env)
    for cell, inst, pmap in insts:
        if cell not in all_mods: continue
        cmd = all_mods[cell]
        if cmd['kind'] == 'primitive':
            a_val = int(env.get(pmap.get('a',''), 0)) & 1
            b_val = int(env.get(pmap.get('b',''), 0)) & 1
            q_prev = int(env.get(pmap.get('q',''), Y_prev)) & 1
            if a_val == 0: q_next = 1
            elif a_val == 1 and b_val == 0: q_next = 0
            elif a_val == 1 and b_val == 1: q_next = q_prev
            else: q_next = q_prev
            env[pmap['q']] = q_next
        else:
            cell_assigns = parse_assigns(cmd['body'])
            drives_fb = any(pmap.get(t) == fb_wire for t, _ in cell_assigns.items())
            if drives_fb:
                fb_driver = (cell, inst, pmap, cmd); continue
            local_env = {p: env.get(net, 0) for p, net in pmap.items()}
            for tgt, expr in cell_assigns.items():
                val = eval_expr(expr, local_env)
                out_net = pmap.get(tgt)
                if out_net:
                    env[out_net] = val; local_env[tgt] = val
    if fb_driver:
        cell, inst, pmap, cmd = fb_driver
        cell_assigns = parse_assigns(cmd['body'])
        local_env = {p: env.get(net, 0) for p, net in pmap.items()}
        for tgt, expr in cell_assigns.items():
            val = eval_expr(expr, local_env)
            out_net = pmap.get(tgt)
            if out_net:
                env[out_net] = val; local_env[tgt] = val
    env['Y'] = env.get(fb_wire, Y_prev)
    return env.get('Y', 0) & 1

def extract_modified_net(stdout):
    m = re.search(r'// BEGIN_NET(.*?)// END_NET', stdout, re.S)
    return m.group(1).strip() if m else ""

def run_candidate(candidate_py, net_text, sim_text, tmpdir):
    net_path = os.path.join(tmpdir, "netlist.v")
    sim_path = os.path.join(tmpdir, "simlib.sv")
    with open(net_path, 'w') as f: f.write(net_text)
    with open(sim_path, 'w') as f: f.write(sim_text)
    try:
        r = subprocess.run([sys.executable, candidate_py, net_path, sim_path],
            capture_output=True, text=True, timeout=30, cwd=tmpdir)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)

def check(deliverable, workdir):
    conditions = {}
    tmpdir = tempfile.mkdtemp(prefix="chk_cellreplace_")
    try:
        if not os.path.isfile(deliverable):
            raise Exception("deliverable not found: " + str(deliverable))
        with zipfile.ZipFile(deliverable) as z:
            z.extractall(tmpdir)
        py_files = [f for f in os.listdir(tmpdir) if f.endswith('.py')]
        if not py_files:
            raise Exception("no .py in zip")
        candidate_py = os.path.join(tmpdir, sorted(py_files)[0])
        src = open(candidate_py).read()

        conditions['a'] = True
        for imp in FORBIDDEN_IMPORTS:
            if re.search(r'\b' + re.escape(imp) + r'\b', src):
                conditions['a'] = False; break
        if conditions.get('a', True):
            for p in FORBIDDEN_PATHS:
                if p in src:
                    conditions['a'] = False; break

        try:
            py_compile.compile(candidate_py, doraise=True)
            conditions['b'] = True
        except Exception as e:
            conditions['b'] = False

        rc, out_b, err_b = run_candidate(candidate_py, NET_B, SIM_B, tmpdir)
        mod_net_b = extract_modified_net(out_b)
        conditions['c'] = (rc == 0 and len(mod_net_b) > 20)
        conditions['d'] = not any(u in mod_net_b for u in B_UNKNOWN)
        conditions['e'] = any(s in mod_net_b for s in B_SIMLIB)
        conditions['f'] = all(p in mod_net_b for p in B_PORTS)
        conditions['g'] = all(p in mod_net_b for p in B_POWER)

        b_pwr_pins = ["vpwr","vgnd","vpsub","vnsub"]
        insts_b = parse_instantiations(mod_net_b)
        pwr_connected = True
        pwr_check_done = False
        for cell, inst, pmap in insts_b:
            if cell in ("ND2P_B","ND3P_B","IVP_B","nor2p","oai21p"):
                pwr_check_done = True
                for pp in b_pwr_pins:
                    if pp not in pmap or pmap[pp] not in B_POWER:
                        pwr_connected = False; break
        conditions['h'] = pwr_connected and pwr_check_done

        sim_b_mods = parse_modules(SIM_B)
        all_match = True
        for S in (0,1):
            for R0 in (0,1):
                for R1 in (0,1):
                    for yp in (0,1):
                        y_orig = eval_latch_orig(S, R0, R1, yp)
                        y_repl = eval_modified_net(mod_net_b, sim_b_mods, S, R0, R1, yp)
                        if y_repl is None or y_orig != y_repl:
                            all_match = False
        conditions['i'] = all_match

        tt_pat = re.search(r'(TRUTH_TABLE|truth|MATCH|HOLD|VERIFICATION)', out_b, re.I)
        has_tt_rows = len(re.findall(r'\b[01]\s+[01]\s+[01]\s+[01]', out_b)) >= 8
        conditions['j'] = bool(tt_pat) and has_tt_rows

        non_net_out = re.sub(r'// BEGIN_NET.*?// END_NET', '', out_b, flags=re.S)
        conditions['k'] = any(u in non_net_out for u in B_UNKNOWN)
        conditions['l'] = not any(a in mod_net_b for a in A_NAMES)

        rc2, out_b2, err_b2 = run_candidate(candidate_py, NET_B2, SIM_B2, tmpdir)
        mod_net_b2 = extract_modified_net(out_b2)
        sim_b2_mods = parse_modules(SIM_B2)
        b2_match = True
        if rc2 != 0 or not mod_net_b2:
            b2_match = False
        else:
            for S in (0,1):
                for R0 in (0,1):
                    for R1 in (0,1):
                        for yp in (0,1):
                            y_orig = eval_latch_orig(S, R0, R1, yp)
                            y_repl = eval_modified_net(mod_net_b2, sim_b2_mods, S, R0, R1, yp)
                            if y_repl is None or y_orig != y_repl:
                                b2_match = False
            if any(u in mod_net_b2 for u in B2_UNKNOWN):
                b2_match = False
            if any(a in mod_net_b2 for a in A_NAMES):
                b2_match = False
        conditions['m'] = b2_match

        conditions['n'] = ('sys.argv' in src or 'argparse' in src)

        rc3, out3, _ = run_candidate(candidate_py, NET_B, SIM_B, tmpdir)
        rc4, out4, _ = run_candidate(candidate_py, NET_B, SIM_B, tmpdir)
        h1 = hashlib.sha256(out_b.encode()).hexdigest()
        h2 = hashlib.sha256(out3.encode()).hexdigest()
        h3 = hashlib.sha256(out4.encode()).hexdigest()
        conditions['o'] = (h1 == h2 == h3)
        conditions['p'] = not any(p in src for p in FORBIDDEN_PATHS)

        passed = sum(1 for v in conditions.values() if v is True)
        total = len(conditions)
        detail = []
        for k in sorted(conditions.keys()):
            v = conditions[k]
            detail.append(k + ":" + ("PASS" if v is True else "FAIL"))
        print("CONDITIONS: %d/%d PASS" % (passed, total))
        print("DETAIL: " + " ".join(detail))
        if passed == total:
            return True
        raise Exception("check FAILED: %d/%d. %s" % (passed, total, " ".join(detail)))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: check.py <submit.zip> [workdir]")
        sys.exit(1)
    deliverable = sys.argv[1]
    workdir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(deliverable)
    try:
        result = check(deliverable, workdir)
        print("RESULT: PASS")
    except Exception as e:
        print("RESULT: FAIL")
        print(str(e))
        sys.exit(1)
'''

# Replace placeholders with repr() of the asset strings
result = TEMPLATE.replace("__NET_B__", repr(netB))
result = result.replace("__SIM_B__", repr(simB))
result = result.replace("__NET_B2__", repr(netB2))
result = result.replace("__SIM_B2__", repr(simB2))

with open(REF+"/check.py", 'w') as f:
    f.write(result)
print("check.py written:", REF+"/check.py", "size:", os.path.getsize(REF+"/check.py"))
