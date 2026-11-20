#!/usr/bin/env python3
# build_netlist_gate2verilog_001.py
# EDA-Eval-DesignFlow-NetlistGate2Verilog-001 (schematic_netlist, A-faithful, B-grade synthesized, L1)
# trace: 1792046093287_3yv6w (qi3wang@10.129.32.83) U#0 verbatim
# Task: gate-level SPICE subckt -> Verilog module (assign-based)
import os, zipfile, io, json, hashlib, shutil, subprocess, sys

CASE = "EDA-Eval-DesignFlow-NetlistGate2Verilog-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)
os.makedirs(ASSETS, exist_ok=True)
os.makedirs(os.path.join(ASSETS, "hidden"), exist_ok=True)
os.makedirs(REF, exist_ok=True)
os.makedirs(os.path.join(REF, "negative"), exist_ok=True)

# ---------- cell library ----------
# pin order: inputs (in listed order), then output 'z'
CELLS = {
    'inv':   {'ins': ['a'],            'tmpl': '~{a}'},
    'buf':   {'ins': ['a'],            'tmpl': '{a}'},
    'nand2': {'ins': ['a', 'b'],       'tmpl': '~({a} & {b})'},
    'nor2':  {'ins': ['a', 'b'],       'tmpl': '~({a} | {b})'},
    'and2':  {'ins': ['a', 'b'],       'tmpl': '({a} & {b})'},
    'or2':   {'ins': ['a', 'b'],       'tmpl': '({a} | {b})'},
    'nand3': {'ins': ['a', 'b', 'c'],  'tmpl': '~({a} & {b} & {c})'},
    'nor3':  {'ins': ['a', 'b', 'c'],  'tmpl': '~({a} | {b} | {c})'},
    'oai21': {'ins': ['a', 'b', 'c'],  'tmpl': '~({a} | ({b} & {c}))'},
    'oai22': {'ins': ['a', 'b', 'c', 'd'], 'tmpl': '~(({a} & {b}) | ({c} & {d}))'},
    'aoi21': {'ins': ['a', 'b', 'c'],  'tmpl': '~(({a} & {b}) | {c})'},
    'mux2':  {'ins': ['a', 'b', 'sel'], 'tmpl': '{sel} ? {b} : {a}'},
    'xor2':  {'ins': ['a', 'b'],       'tmpl': '({a} ^ {b})'},
    'xnor2': {'ins': ['a', 'b'],       'tmpl': '~({a} ^ {b})'},
}

# ---------- module definitions (hand-crafted valid DAGs) ----------
# each: name, inputs, outputs, supplies, insts=[(cell, [in_nets], out_net)]
MODULE_A = {
    'name': 'OdtPdMuxA',
    'inputs': ['OdtWr', 'DmiInEn', 'Reset', 'MdNtEn', 'NtOdtRdDQ', 'RdqstInEn', 'FsRocEn', 'RocEn'],
    'outputs': ['AnyOdt', 'NtFlag', 'PdSel', 'DmiPd0', 'DmiPd1'],
    'supplies': ['inh_vcc', 'inh_vss'],
    'insts': [
        ('inv',   ['OdtWr'],                          'w0'),
        ('nand2', ['OdtWr', 'DmiInEn'],               'w1'),
        ('and2',  ['OdtWr', 'DmiInEn'],               'w2'),
        ('oai21', ['w0', 'FsRocEn', 'NtOdtRdDQ'],     'w3'),
        ('nor2',  ['Reset', 'MdNtEn'],                'w4'),
        ('and2',  ['w3', 'w4'],                       'NtFlag'),
        ('oai22', ['w0', 'DmiInEn', 'w1', 'RdqstInEn'], 'w5'),
        ('nand3', ['OdtWr', 'DmiInEn', 'RdqstInEn'],  'w6'),
        ('nor3',  ['Reset', 'RocEn', 'FsRocEn'],      'w7'),
        ('aoi21', ['RocEn', 'FsRocEn', 'w0'],         'w8'),
        ('mux2',  ['w5', 'w2', 'FsRocEn'],            'PdSel'),
        ('or2',   ['w2', 'w6'],                       'AnyOdt'),
        ('xor2',  ['w6', 'w7'],                       'DmiPd0'),
        ('xnor2', ['w3', 'w8'],                       'DmiPd1'),
    ],
}
MODULE_B = {
    'name': 'OdtPdMuxB',
    'inputs': ['WrEn', 'InEn', 'RstN', 'NtEn', 'RdDQ', 'InEn2', 'RocF', 'ClkEn'],
    'outputs': ['FlagA', 'FlagB', 'Sel', 'Code0', 'Code1'],
    'supplies': ['vdda', 'gnda'],
    'insts': [
        ('inv',   ['WrEn'],                  'b0'),
        ('nand2', ['WrEn', 'InEn'],          'b1'),
        ('nor2',  ['RstN', 'NtEn'],          'b2'),
        ('and2',  ['b1', 'b2'],              'FlagA'),
        ('oai21', ['b0', 'RocF', 'RdDQ'],    'b3'),
        ('nor3',  ['RstN', 'ClkEn', 'RocF'], 'b4'),
        ('mux2',  ['b3', 'b1', 'RocF'],      'FlagB'),
        ('nand3', ['WrEn', 'InEn', 'InEn2'], 'b5'),
        ('or2',   ['b5', 'b4'],              'Sel'),
        ('xor2',  ['b3', 'b4'],              'Code0'),
        ('aoi21', ['ClkEn', 'RocF', 'b0'],   'b6'),
        ('xnor2', ['b6', 'b5'],              'Code1'),
        ('and2',  ['b6', 'b2'],              'b7'),
        ('or2',   ['b7', 'b4'],              'b8'),
        ('buf',   ['b8'],                    'b9'),
        ('nand2', ['b9', 'b3'],              'b10'),
        ('mux2',  ['b10', 'b7', 'InEn2'],    'b11'),
        ('xnor2', ['b11', 'b1'],             'b12'),
    ],
}
# b0..b12: ensure all consumed. b0: oai21(5), aoi21(11). b1: FlagA(4), mux(7), xnor(18). b2: and(4), and(13).
# b3: mux(7), xor(10), nand2(16). b4: or(9), xor(10), or(14). b5: or(9), xnor(12). b6: xnor(12), and(13).
# b7: or(14), mux(17). b8: buf(15). b9: nand2(16). b10: mux(17). b11: xnor(18). b12: ??? DANGLING.
# fix: make Code1 = xnor2([b11, b1]) and drop b12; but then b11 consumed. Let b12 feed nothing -> remove.
MODULE_B['insts'] = [i for i in MODULE_B['insts'] if i[2] != 'b12']
# now b11 consumed by? b11 is output of mux(17), not consumed -> dangling. Make Code1 = xnor2([b11,b1]) (inst18) consumes b11,b1. keep.
# re-add the xnor consuming b11:
MODULE_B['insts'].append(('xnor2', ['b11', 'b1'], 'Code1'))
# but Code1 was already inst12 (xnor2 b6,b5). Remove that one; reassign.
MODULE_B['insts'] = [i for i in MODULE_B['insts'] if not (i[0]=='xnor2' and i[2]=='Code1' and i[1]==['b6','b5'])]
# now b6 consumed by aoi21? no, b6 produced by aoi21(11), consumed by? xnor(b6,b5) was removed. b6 dangling.
# fix: add an output consumer for b6. Make Code0 = and2([b6, b3])? but Code0 already xor(b3,b4). 
# Simpler: add internal b13 = and2([b6,b3]) and feed Sel? no Sel=or(b5,b4). 
# Let me just make b6 feed a new wire used by an existing output.
# Redo B cleanly below.

MODULE_B = {
    'name': 'OdtPdMuxB',
    'inputs': ['WrEn', 'InEn', 'RstN', 'NtEn', 'RdDQ', 'InEn2', 'RocF', 'ClkEn'],
    'outputs': ['FlagA', 'FlagB', 'Sel', 'Code0', 'Code1'],
    'supplies': ['vdda', 'gnda'],
    'insts': [
        ('inv',   ['WrEn'],                  'b0'),
        ('nand2', ['WrEn', 'InEn'],          'b1'),
        ('nor2',  ['RstN', 'NtEn'],          'b2'),
        ('and2',  ['b1', 'b2'],              'FlagA'),
        ('oai21', ['b0', 'RocF', 'RdDQ'],    'b3'),
        ('nor3',  ['RstN', 'ClkEn', 'RocF'], 'b4'),
        ('nand3', ['WrEn', 'InEn', 'InEn2'], 'b5'),
        ('aoi21', ['ClkEn', 'RocF', 'b0'],   'b6'),
        ('mux2',  ['b3', 'b6', 'RocF'],      'FlagB'),
        ('or2',   ['b5', 'b4'],              'Sel'),
        ('xor2',  ['b3', 'b4'],              'Code0'),
        ('xnor2', ['b6', 'b5'],              'Code1'),
        ('and2',  ['b6', 'b2'],              'b7'),
        ('buf',   ['b7'],                    'b8'),
        ('nand2', ['b8', 'b3'],              'b9'),
    ],
}
# consumption check B: b0->oai21(5),aoi21(8). b1->and(4)FlagA. b2->and(4),and(13). b3->mux(9)FlagB,xor(11)Code0,nand2(15).
# b4->or(10)Sel,xor(11)Code0. b5->or(10)Sel,xnor(12)Code1. b6->mux(9)FlagB,xnor(12)Code1,and(13).
# b7->buf(14). b8->nand2(15). b9-> ??? DANGLING (b9 not consumed, not output).
# fix: b9 must be consumed. Make Code1 = xnor2([b9, b5])? but then b6 dangling (b6 was consumed by xnor(12) which we'd change).
# Simplest fix: remove insts 13,14,15 (and b7,buf b8,nand2 b9) — they're a dangling tail. Keep b6 consumed by FlagB(mux) + Code1(xnor).
MODULE_B['insts'] = [
    ('inv',   ['WrEn'],                  'b0'),
    ('nand2', ['WrEn', 'InEn'],          'b1'),
    ('nor2',  ['RstN', 'NtEn'],          'b2'),
    ('and2',  ['b1', 'b2'],              'FlagA'),
    ('oai21', ['b0', 'RocF', 'RdDQ'],    'b3'),
    ('nor3',  ['RstN', 'ClkEn', 'RocF'], 'b4'),
    ('nand3', ['WrEn', 'InEn', 'InEn2'], 'b5'),
    ('aoi21', ['ClkEn', 'RocF', 'b0'],   'b6'),
    ('mux2',  ['b3', 'b6', 'RocF'],      'FlagB'),
    ('or2',   ['b5', 'b4'],              'Sel'),
    ('xor2',  ['b3', 'b4'],              'Code0'),
    ('xnor2', ['b6', 'b5'],              'Code1'),
]
# b0: oai21(5),aoi21(8) [2x]. b1: and(4)FlagA [1x]. b2: and(4)FlagA [1x]. b3: mux(9)FlagB,xor(11)Code0 [2x].
# b4: or(10)Sel,xor(11)Code0 [2x]. b5: or(10)Sel,xnor(12)Code1 [2x]. b6: mux(9)FlagB,xnor(12)Code1 [2x]. all consumed. 12 insts.
# cells B: inv,nand2,nor2,and2,oai21,nor3,nand3,aoi21,mux2,or2,xor2,xnor2 = 12 distinct.

MODULE_B2 = {
    'name': 'OdtPdMuxC',
    'inputs': ['A', 'B', 'C', 'D', 'E', 'F'],
    'outputs': ['Y0', 'Y1', 'Y2'],
    'supplies': ['avdd', 'agnd'],
    'insts': [
        ('inv',  ['A'],          'c0'),
        ('nand2',['A', 'B'],     'c1'),
        ('nor2', ['C', 'D'],     'c2'),
        ('and2', ['c1', 'c2'],   'Y0'),
        ('oai21',['c0', 'E', 'F'],'c3'),
        ('mux2', ['c3', 'c1', 'E'], 'Y1'),
        ('xor2', ['c2', 'c3'],   'Y2'),
    ],
}
# c0: oai21(5). c1: and(4)Y0,mux(6)Y1. c2: and(4)Y0,xor(7)Y2. c3: mux(6)Y1,xor(7)Y2. all consumed. 7 insts.
# cells B2: inv,nand2,nor2,and2,oai21,mux2,xor2 = 7 distinct (subset, fewer cells -> cross-input).

def validate(mod):
    ports = set(mod['inputs']) | set(mod['outputs']) | set(mod['supplies'])
    driven = {}
    for cell, ins, out in mod['insts']:
        assert out not in driven, "double-drive %s" % out
        driven[out] = cell
        assert cell in CELLS, "unknown cell %s" % cell
        assert len(ins) == len(CELLS[cell]['ins']), "arity %s" % cell
    # every internal net consumed
    internal = set(driven) - ports
    all_consumed = set()
    for cell, ins, out in mod['insts']:
        for n in ins:
            all_consumed.add(n)
    for n in internal:
        assert n in all_consumed, "dangling internal %s" % n
    for o in mod['outputs']:
        assert o in driven, "output %s not driven" % o
    # DAG check
    import collections
    graph = {n: [] for n in driven}
    indeg = {n: 0 for n in driven}
    for cell, ins, out in mod['insts']:
        for n in ins:
            if n in driven:
                graph[n].append(out)
                indeg[out] = indeg.get(out, 0) + 1
    # kahn
    q = collections.deque([n for n in driven if indeg.get(n,0)==0])
    seen = 0
    while q:
        n = q.popleft(); seen += 1
        for m in graph[n]:
            indeg[m] -= 1
            if indeg[m]==0: q.append(m)
    assert seen == len(driven), "cycle detected"
    return True

for m in (MODULE_A, MODULE_B, MODULE_B2):
    validate(m)
print("circuits valid")

# ---------- netlist emitter ----------
def emit_netlist(mod):
    lines = []
    lines.append("* Gate-level netlist: %s" % mod['name'])
    ports = mod['inputs'] + mod['outputs'] + mod['supplies']
    lines.append(".SUBCKT %s %s" % (mod['name'], ' '.join(ports)))
    pininfo = ' '.join("%s:I" % p for p in mod['inputs']) + ' ' + \
              ' '.join("%s:O" % p for p in mod['outputs']) + ' ' + \
              ' '.join("%s:B" % p for p in mod['supplies'])
    lines.append("*. PININFO %s" % pininfo)
    for i, (cell, ins, out) in enumerate(mod['insts']):
        lines.append("X%d %s %s" % (i, ' '.join(ins + [out]), cell))
    lines.append(".ENDS %s" % mod['name'])
    return '\n'.join(lines) + '\n'

# ---------- gold converter ----------
GOLD = r'''#!/usr/bin/env python3
"""netlist2verilog_ref.py -- gate-level SPICE subckt -> Verilog module (assign-based).
CLI: netlist2verilog.py <netlist.sp> <module> -o <out.v>
Parses .SUBCKT <module> ... .ENDS, reads *. PININFO for port directions,
maps standard-cell instances (inv/buf/nand2/nor2/and2/or2/nand3/nor3/oai21/oai22/aoi21/mux2/xor2/xnor2)
to boolean assign statements, emits a clean Verilog module named <module>.
"""
import sys, re, argparse

CELLS = {
    'inv':   (['a'], '~{a}'),
    'buf':   (['a'], '{a}'),
    'nand2': (['a', 'b'], '~({a} & {b})'),
    'nor2':  (['a', 'b'], '~({a} | {b})'),
    'and2':  (['a', 'b'], '({a} & {b})'),
    'or2':   (['a', 'b'], '({a} | {b})'),
    'nand3': (['a', 'b', 'c'], '~({a} & {b} & {c})'),
    'nor3':  (['a', 'b', 'c'], '~({a} | {b} | {c})'),
    'oai21': (['a', 'b', 'c'], '~({a} | ({b} & {c}))'),
    'oai22': (['a', 'b', 'c', 'd'], '~(({a} & {b}) | ({c} & {d}))'),
    'aoi21': (['a', 'b', 'c'], '~(({a} & {b}) | {c})'),
    'mux2':  (['a', 'b', 'sel'], '{sel} ? {b} : {a}'),
    'xor2':  (['a', 'b'], '({a} ^ {b})'),
    'xnor2': (['a', 'b'], '~({a} ^ {b})'),
}

def parse_netlist(text, module):
    lines = text.splitlines()
    in_sub = False
    ports = []
    pininfo = {}
    insts = []
    for line in lines:
        s = line.strip()
        if s.startswith(".SUBCKT") or s.startswith(".subckt"):
            toks = s.split()
            if len(toks) >= 2 and toks[1] == module:
                in_sub = True
                ports = toks[2:]
                continue
        if not in_sub:
            continue
        if s.startswith("*. PININFO") or s.startswith("*.PININFO"):
            for tok in s.replace("*. PININFO", "").replace("*.PININFO", "").split():
                if ':' in tok:
                    nm, d = tok.rsplit(':', 1)
                    pininfo[nm] = d.upper()
            continue
        if s.startswith(".ENDS") or s.startswith(".ends"):
            break
        if s.startswith("*") or s.startswith("."):
            continue
        if s.startswith("X") and len(s.split()) >= 2:
            toks = s.split()
            cell = toks[-1]
            nets = toks[1:-1]
            insts.append((toks[0], cell, nets))
    return ports, pininfo, insts

def convert(text, module):
    ports, pininfo, insts = parse_netlist(text, module)
    port_set = set(ports)
    out_lines = []
    out_lines.append("// Gate-level Verilog generated from SPICE netlist")
    out_lines.append("// Module: %s" % module)
    out_lines.append("`timescale 10ps/10ps")
    out_lines.append("module %s (" % module)
    pdir = {}
    for p in ports:
        d = pininfo.get(p, 'I')
        pdir[p] = d
    port_decls = []
    for p in ports:
        d = pdir[p]
        if d == 'O':
            port_decls.append("    output  %s" % p)
        elif d == 'B':
            port_decls.append("    inout   %s" % p)
        else:
            port_decls.append("    input   %s" % p)
    out_lines.append(',\n'.join(port_decls))
    out_lines.append(");")
    # internal wires
    driven = {}
    for inst, cell, nets in insts:
        if cell not in CELLS:
            continue
        ins_names, _ = CELLS[cell]
        out_net = nets[len(ins_names)] if len(nets) > len(ins_names) else nets[-1]
        driven[out_net] = (cell, nets)
    internal = [n for n in driven if n not in port_set]
    if internal:
        out_lines.append("")
        for n in internal:
            out_lines.append("    wire %s;" % n)
    out_lines.append("")
    for inst, cell, nets in insts:
        if cell not in CELLS:
            continue
        ins_names, tmpl = CELLS[cell]
        in_nets = nets[:len(ins_names)]
        out_net = nets[len(ins_names)]
        mapping = {ins_names[i]: in_nets[i] for i in range(len(ins_names))}
        expr = tmpl
        for k, v in mapping.items():
            expr = expr.replace('{' + k + '}', v)
        out_lines.append("    assign %s = %s;" % (out_net, expr))
    out_lines.append("endmodule")
    return '\n'.join(out_lines) + '\n'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('netlist')
    ap.add_argument('module')
    ap.add_argument('-o', '--out', default=None)
    args = ap.parse_args()
    with open(args.netlist) as f:
        text = f.read()
    v = convert(text, args.module)
    outpath = args.out if args.out else (args.module + '.v')
    with open(outpath, 'w') as f:
        f.write(v)
    print("wrote %s" % outpath)

if __name__ == '__main__':
    main()
'''

# ---------- write assets ----------
with open(os.path.join(ASSETS, "netlist_A.sp"), 'w') as f:
    f.write(emit_netlist(MODULE_A))
with open(os.path.join(ASSETS, "hidden", "netlist_B.sp"), 'w') as f:
    f.write(emit_netlist(MODULE_B))
with open(os.path.join(ASSETS, "hidden", "netlist_B2.sp"), 'w') as f:
    f.write(emit_netlist(MODULE_B2))
with open(os.path.join(ASSETS, "hidden", "hidden_manifest.json"), 'w') as f:
    json.dump({"B": "netlist_B.sp", "B2": "netlist_B2.sp",
               "B_module": MODULE_B['name'], "B2_module": MODULE_B2['name']}, f, indent=2)

PROMPT = "这是我的网表路径 netlist_A.sp，帮我把其中的 OdtPdMuxA 模块使用verilog进行实现，要求简介清晰，写好后另存在统一个目录下的不同文件，文件以模块名命名"
with open(os.path.join(ASSETS, "prompt.txt"), 'w') as f:
    f.write(PROMPT + "\n")
TASK_BRIEF = "交付接口：写一个可复用 Python 脚本 netlist2verilog.py <netlist.sp> <module> -o <out.v>，解析 gate-level SPICE subckt 并输出 Verilog module（assign 组合逻辑，端口方向由 *. PININFO 决定）。打包 outputs/submit.zip（含 netlist2verilog.py）。"
with open(os.path.join(ASSETS, "task_brief.md"), 'w') as f:
    f.write(TASK_BRIEF + "\n")

# ---------- write gold ----------
GOLD_PATH = os.path.join(REF, "netlist2verilog_ref.py")
with open(GOLD_PATH, 'w') as f:
    f.write(GOLD)
os.chmod(GOLD_PATH, 0o755)

print("assets + gold written")
print("ASSETS:", ASSETS)
