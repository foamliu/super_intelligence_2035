#!/usr/bin/env python3
"""Generate reference solution for NetlistCellReplace-001."""
import os
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = BENCH + "/reference/EDA-Eval-DesignFlow-NetlistCellReplace-001"

REF_CODE = r'''#!/usr/bin/env python3
"""replace_cells_ref.py -- Reference: replace unknown cells in a Verilog netlist
with simlib physical cells (power pins connected), merge pure-logic inputs with &,
print replaced lines, verify truth table with hold state.

CLI: replace_cells_ref.py <netlist> <simlib>
"""
import sys, re, itertools

def parse_modules(text):
    """Parse Verilog module/primitive definitions -> {name: {ports:[...], body:text, kind:'module'/'primitive'}}"""
    mods = {}
    for m in re.finditer(r'(`celldefine\s*)?module\s+(\w+)\s*\(([^)]*)\)(.*?)(`endcelldefine\s*)?endmodule', text, re.S):
        name = m.group(2)
        ports = [p.strip() for p in m.group(3).split(',') if p.strip()]
        mods[name] = {'ports': ports, 'body': m.group(4), 'kind': 'module'}
    for m in re.finditer(r'(`celldefine\s*)?primitive\s+(\w+)\s*\(([^)]*)\)(.*?)endprimitive', text, re.S):
        name = m.group(2)
        ports = [p.strip() for p in m.group(3).split(',') if p.strip()]
        mods[name] = {'ports': ports, 'body': m.group(4), 'kind': 'primitive'}
    return mods

def parse_assigns(body):
    """Parse 'assign Y = expr;' -> {Y: expr_str}"""
    out = {}
    for m in re.finditer(r'assign\s+(\w+)\s*=\s*([^;]+);', body):
        out[m.group(1)] = m.group(2).strip()
    return out

def eval_expr(expr, env):
    """Evaluate a Verilog Boolean expression (1-bit) given env dict.
    Supports: ~ ! & && | || ^ ~& ~| ( ) and identifiers."""
    e = expr.replace('&&','&').replace('||','|').replace('!','~')
    # tokenize
    tokens = re.findall(r'[~&|^()]|\w+', e)
    pos = [0]
    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None
    def consume():
        t = tokens[pos[0]]; pos[0]+=1; return t
    def parse_expr():
        return parse_or()
    def parse_or():
        v = parse_xor()
        while peek()=='|':
            consume(); r = parse_xor(); v = v | r
        return v
    def parse_xor():
        v = parse_and()
        while peek()=='^':
            consume(); r = parse_and(); v = v ^ r
        return v
    def parse_and():
        v = parse_unary()
        while peek()=='&':
            consume(); r = parse_unary(); v = v & r
        return v
    def parse_unary():
        if peek()=='~':
            consume(); return ~parse_unary() & 1
        return parse_atom()
    def parse_atom():
        t = consume()
        if t=='(':
            v = parse_expr()
            if peek()==')': consume()
            return v
        if t in ('0','1'):
            return int(t)
        # identifier
        val = env.get(t, 0)
        return int(val) & 1 if isinstance(val,(int,float)) else 0
    return parse_expr() & 1

def get_cell_logic(moddef, simmods):
    """Determine a cell's output logic: returns dict {out_port: expr_str} from assign, or None for primitive."""
    if moddef['kind'] == 'primitive':
        return None  # sequential, handle specially
    assigns = parse_assigns(moddef['body'])
    return assigns

def parse_instantiations(body):
    """Parse cell instantiations: 'cell_name inst_name (.port(net), ...);' -> [(cell_name, inst_name, {port:net})]"""
    insts = []
    # match: word word ( ... ) ;  but not 'assign'/'module'/'endmodule'
    for m in re.finditer(r'\b(\w+)\s+(\w+)\s*\(([^)]*)\)\s*;', body):
        cell, inst, ports_str = m.group(1), m.group(2), m.group(3)
        if cell in ('assign','module','endmodule','endprimitive','primitive','generate','endgenerate',
                     'if','else','begin','end','parameter','localparam','wire','reg','input','output','inout',
                     'timescale','celldefine','endcelldefine'):
            continue
        pmap = {}
        for pm in re.finditer(r'\.(\w+)\s*\(([^)]*)\)', ports_str):
            pmap[pm.group(1)] = pm.group(2).strip()
        if pmap:
            insts.append((cell, inst, pmap))
    return insts

def eval_circuit(netlist_text, simlib_text, inputs_dict, y_prev, output_port="Y"):
    """Evaluate a netlist given input values + Y_prev (for feedback).
    Returns dict of all wire values."""
    all_mods = parse_modules(netlist_text)
    sim_mods = parse_modules(simlib_text)
    all_mods.update(sim_mods)

    # find the top module (first module with instantiations of other cells, or the largest)
    top = None
    for name, md in all_mods.items():
        if md['kind']=='module':
            insts = parse_instantiations(md['body'])
            assigns = parse_assigns(md['body'])
            if insts or assigns:
                if top is None or len(md['body'])>len(top[1]['body']):
                    top = (name, md)
    if top is None:
        return {}
    topname, topdef = top
    insts = parse_instantiations(topdef['body'])
    assigns = parse_assigns(topdef['body'])

    env = dict(inputs_dict)
    # find the output port name
    out_port = output_port
    # set feedback: find the wire driven by the output assign (Y = nq) -> nq gets Y_prev
    # Look for assign Y = <wire>; set <wire> = Y_prev initially
    for tgt, expr in assigns.items():
        # if Y is assigned from a single wire, that wire is the feedback
        pass
    # Set Y_prev for the feedback wire. The feedback wire is the one assigned to Y.
    y_assign_expr = assigns.get(out_port, None)
    if y_assign_expr:
        fb_wire = y_assign_expr.strip()
        if re.match(r'^\w+$', fb_wire):
            env[fb_wire] = y_prev
    env[out_port] = y_prev

    # evaluate instantiations iteratively (2 passes for cross-coupled)
    for _pass in range(3):
        for cell, inst, pmap in insts:
            if cell not in all_mods:
                continue
            cmd = all_mods[cell]
            if cmd['kind'] == 'primitive':
                # sequential: q_next = f(a, b, q_prev)
                a_val = env.get(pmap.get('a',''), 0)
                b_val = env.get(pmap.get('b',''), 0)
                q_prev = env.get(pmap.get('q',''), y_prev)
                a_val = int(a_val)&1 if isinstance(a_val,(int,float)) else 0
                b_val = int(b_val)&1 if isinstance(b_val,(int,float)) else 0
                q_prev = int(q_prev)&1 if isinstance(q_prev,(int,float)) else 0
                if a_val == 0:
                    q_next = 1
                elif a_val == 1 and b_val == 0:
                    q_next = 0
                elif a_val == 1 and b_val == 1:
                    q_next = q_prev  # hold
                else:
                    q_next = q_prev
                env[pmap['q']] = q_next
            else:
                cell_assigns = parse_assigns(cmd['body'])
                for tgt, expr in cell_assigns.items():
                    # map cell ports to instance nets
                    local_env = {}
                    for p, net in pmap.items():
                        local_env[p] = env.get(net, 0)
                    val = eval_expr(expr, local_env)
                    # find which port is the output
                    # assume tgt is the output port
                    out_net = pmap.get(tgt, None)
                    if out_net:
                        env[out_net] = val
        # evaluate assigns
        for tgt, expr in assigns.items():
            if re.match(r'^\w+$', expr) and expr in env:
                env[tgt] = env[expr]
            else:
                env[tgt] = eval_expr(expr, env)
    return env

def main():
    if len(sys.argv) < 3:
        print("Usage: replace_cells_ref.py <netlist> <simlib>", file=sys.stderr)
        sys.exit(1)
    net_path, sim_path = sys.argv[1], sys.argv[2]
    with open(net_path) as f: net_text = f.read()
    with open(sim_path) as f: sim_text = f.read()

    net_mods = parse_modules(net_text)
    sim_mods = parse_modules(sim_text)
    sim_names = set(sim_mods.keys())

    # find top module (one with instantiations, not defined as simple behavioral)
    top = None
    for name, md in net_mods.items():
        insts = parse_instantiations(md['body'])
        if insts:
            top = (name, md)
            break

    replaced_lines = []
    new_body_lines = []

    if top:
        topname, topdef = top
        insts = parse_instantiations(topdef['body'])
        assigns = parse_assigns(topdef['body'])
        # find simlib cells matching unknown cells by logic
        # build logic map for simlib cells
        sim_logic = {}
        for sn, smd in sim_mods.items():
            if smd['kind']=='module':
                sa = parse_assigns(smd['body'])
                sim_logic[sn] = sa

        # find physical nand2p and nand3p in simlib
        nand2p = None; nand3p = None; latch = None
        for sn, sa in sim_logic.items():
            for tgt, expr in sa.items():
                if re.match(r'~\(A\s*&\s*B\)', expr.replace(' ','')):
                    if nand2p is None: nand2p = sn
                if re.match(r'~\(A\s*&\s*B\s*&\s*C\)', expr.replace(' ','')):
                    if nand3p is None: nand3p = sn
        for sn, smd in sim_mods.items():
            if smd['kind']=='primitive':
                latch = sn; break

        # detect power pin names from simlib cells
        pwr_pins = {}
        if nand2p and nand2p in sim_mods:
            for p in sim_mods[nand2p]['ports']:
                if p not in ('Y','A','B'):
                    pwr_pins[p] = p  # map simlib pin -> local
        # find power inouts in top module
        top_ports = topdef['ports']
        pwr_inouts = [p for p in top_ports if p not in ('Y',)]
        # heuristics: match by role
        # power pin mapping: vcc->first pwr inout, vss->second, etc.
        pwr_map = {}
        pin_roles = {}
        if nand2p and nand2p in sim_mods:
            sp = sim_mods[nand2p]['ports']
            for p in sp:
                if p not in ('Y','A','B'):
                    pin_roles[p] = p
        # map simlib power pins to top module inouts by role hints
        for sp_pin in pin_roles:
            for ti in pwr_inouts:
                tl = ti.lower()
                spl = sp_pin.lower().replace('_','')
                if ('vcc' in tl or 'vdd' in tl or 'pwr' in tl) and ('vcc' in spl or 'vdd' in spl or 'pwr' in spl):
                    pwr_map[sp_pin] = ti; break
                if ('vss' in tl or 'gnd' in tl) and ('vss' in spl or 'gnd' in spl):
                    pwr_map[sp_pin] = ti; break
                if ('vbp' in tl or 'psub' in tl or 'vpwr' in tl) and ('vbp' in spl or 'psub' in spl):
                    pwr_map[sp_pin] = ti; break
                if ('vbn' in tl or 'nsub' in tl) and ('vbn' in spl or 'nsub' in spl):
                    pwr_map[sp_pin] = ti; break

        # collect original instantiation lines for printing
        orig_lines = []
        for cell, inst, pmap in insts:
            if cell not in sim_names:
                # find original line in net_text
                for ln in net_text.splitlines():
                    if re.search(r'\b'+re.escape(cell)+r'\s+'+re.escape(inst)+r'\b', ln):
                        orig_lines.append(ln.strip())
                        break

        # build replacement
        # Strategy: replace unknown NAND2 -> nand2p (physical), unknown NAND3 -> assign rstbar + nand2p
        new_insts = []
        rstbar_created = False
        for cell, inst, pmap in insts:
            if cell in sim_names:
                new_insts.append((cell, inst, pmap))
                continue
            # determine logic of unknown cell
            cmd = net_mods.get(cell)
            if cmd is None: continue
            ca = parse_assigns(cmd['body'])
            expr_str = ""
            for tgt, e in ca.items():
                expr_str = e.strip()
            # NAND2: ~(A & B)
            if nand2p and re.match(r'~\(A\s*&\s*B\)$', expr_str.replace(' ','')):
                npmap = dict(pmap)
                for sp in pin_roles:
                    if sp in pwr_map:
                        npmap[sp] = pwr_map[sp]
                new_insts.append((nand2p, inst, npmap))
                replaced_lines.append((orig_lines[0] if orig_lines else "",
                    "%s %s (.Y(%s), .A(%s), .B(%s), %s);" % (
                    nand2p, inst, pmap.get('Y',''), pmap.get('A',''), pmap.get('B',''),
                    ', '.join('.%s(%s)'%(sp, pwr_map[sp]) for sp in pin_roles if sp in pwr_map))))
            # NAND3: ~(A & B & C) -> assign rstbar = A & B; nand2p(.Y, .A(rstbar), .B(C))
            elif nand2p and re.match(r'~\(A\s*&\s*B\s*&\s*C\)$', expr_str.replace(' ','')):
                rstbar = "rstbar_%s" % inst
                rstbar_created = True
                a_net = pmap.get('A',''); b_net = pmap.get('B',''); c_net = pmap.get('C',''); y_net = pmap.get('Y','')
                npmap = {'Y': y_net, 'A': rstbar, 'B': c_net}
                for sp in pin_roles:
                    if sp in pwr_map:
                        npmap[sp] = pwr_map[sp]
                new_insts.append((nand2p, inst, npmap))
                replaced_lines.append((orig_lines[0] if orig_lines else "",
                    "assign %s = %s & %s; %s %s (.Y(%s), .A(%s), .B(%s), %s);" % (
                    rstbar, a_net, b_net, nand2p, inst, y_net, rstbar, c_net,
                    ', '.join('.%s(%s)'%(sp, pwr_map[sp]) for sp in pin_roles if sp in pwr_map))))
            else:
                new_insts.append((cell, inst, pmap))

        # emit modified netlist
        out_lines = ["// BEGIN_NET"]
        out_lines.append("module %s (%s);" % (topname, ', '.join(topdef['ports'])))
        # port declarations
        for p in topdef['ports']:
            if p == 'Y':
                out_lines.append("    output %s;" % p)
            else:
                out_lines.append("    inout %s;" % p)
        # wires
        for cell, inst, pmap in new_insts:
            for p, net in pmap.items():
                if net and net not in topdef['ports'] and not net.startswith('rstbar'):
                    pass
        # emit rstbar assigns
        for cell, inst, pmap in new_insts:
            if pmap.get('A','').startswith('rstbar_'):
                rb = pmap['A']
                # find the original A, B for this rstbar from replaced_lines
                pass
        # emit instantiations
        for cell, inst, pmap in new_insts:
            pl = ', '.join('.%s(%s)'%(p,v) for p,v in pmap.items())
            out_lines.append("    %s %s (%s);" % (cell, inst, pl))
        out_lines.append("    assign Y = nq;")
        out_lines.append("endmodule")
        out_lines.append("// END_NET")
        modified_net = '\n'.join(out_lines)
    else:
        modified_net = "// BEGIN_NET\n// END_NET"

    # print modified netlist
    print(modified_net)
    print()

    # print replacements
    print("// REPLACEMENT")
    for orig, repl in replaced_lines:
        print("ORIG: %s" % orig)
        print("NEW:  %s" % repl)
    print()

    # truth table verification (with hold state)
    print("// TRUTH_TABLE")
    print("S R0 R1 Y_prev | Y_next | orig | repl | MATCH")
    all_match = True
    for S in (0,1):
        for R0 in (0,1):
            for R1 in (0,1):
                for yp in (0,1):
                    # evaluate original
                    env_o = eval_circuit(net_text, sim_text, {'S':S,'R0':R0,'R1':R1}, yp, 'Y')
                    y_orig = env_o.get('Y', 0) & 1
                    # evaluate modified (write to temp, eval)
                    env_r = eval_circuit(modified_net, sim_text, {'S':S,'R0':R0,'R1':R1}, yp, 'Y')
                    y_repl = env_r.get('Y', 0) & 1
                    m = "OK" if y_orig==y_repl else "FAIL"
                    if y_orig != y_repl: all_match = False
                    print("%d  %d  %d   %d    |   %d    |  %d   |  %d   | %s" % (
                        S,R0,R1,yp,y_repl,y_orig,y_repl,m))
    hold_ok = True
    # check hold: S=1,R0=1,R1=1 -> Y_next==Y_prev
    for yp in (0,1):
        env_o = eval_circuit(net_text, sim_text, {'S':1,'R0':1,'R1':1}, yp, 'Y')
        if env_o.get('Y',0)&1 != yp: hold_ok = False
    print("HOLD_OK=%s ALL_MATCH=%s" % (hold_ok, all_match))
    if all_match and hold_ok:
        print("VERIFICATION: PASS")
    else:
        print("VERIFICATION: FAIL")

if __name__ == '__main__':
    main()
'''

with open(REF+"/netlist_cell_replace_ref.py","w") as f:
    f.write(REF_CODE)
print("Reference solution written:", REF+"/netlist_cell_replace_ref.py")
