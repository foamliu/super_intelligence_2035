#!/usr/bin/env python3
"""flatten_verilog.py --- flatten a hierarchical CDL/Verilog netlist.

Usage:
    python3 flatten_verilog.py <input.v> [-o <output.v>]

This tool turns a hierarchical netlist (top module instantiating ICV_*
wrappers, which instantiate further ICV_* wrappers or LEAF_* leaf cells)
into a single flat Verilog netlist.  Three hard rules are enforced:

  1. NO backslash escapes -- every identifier is rewritten into a legal
     Verilog simple identifier [A-Za-z_][A-Za-z0-9_]*.  Backslashes are
     removed, ``[`` ``]`` ``:`` become ``_``, a leading digit gets an
     ``n`` prefix, and bus bit-selects (e.g. ``DIN[0]``) become scalar
     net names (``DIN_0_``).

  2. NO ICV_* wrappers -- every wrapper module is DFS-inlined into the
     top module; only LEAF_* cell instances remain.  Each leaf instance
     name carries the wrapper-instance path as a prefix
     (e.g. X1 -> X8 -> leaf X9 becomes X1_X8_X9).  LEAF_* module
     definitions are kept (with cleaned identifiers and stripped PG).

  3. NO VDD/VSS -- any VDD/VSS port, wire, or pin connection is dropped.

The accepted input grammar is intentionally small (one construct per
line, ``;`` terminated)::

    module NAME ( port list ) ;
    input           NAME ;
    input [W:0]     NAME ;
    output          NAME ;
    output [W:0]    NAME ;
    wire  [W:0]     NAME ;
    MODULE INST ( .PIN(NET) , ... ) ;
    not/buf/nand/nor/and/or ( Z , A , ... ) ;
    endmodule
"""

import sys
import re
import argparse


def clean_ident(name):
    """Rewrite an identifier/net string into a legal simple identifier."""
    if name is None:
        return ""
    s = name.replace("\\", "")                 # remove escape backslash
    s = s.replace("[", "_").replace("]", "_").replace(":", "_")
    if s and s[0].isdigit():
        s = "n" + s
    return s


def is_pg(name):
    """Return True if a name denotes VDD/VSS (power/ground net)."""
    if name is None:
        return False
    s = name.replace("\\", "").strip()
    while s.endswith("!"):
        s = s[:-1]
    return s in ("VDD", "VSS")


def bit_indices(msb, lsb):
    if msb is None or lsb is None:
        return None
    if msb >= lsb:
        return list(range(msb, lsb - 1, -1))
    return list(range(msb, lsb + 1, 1))


def scalar_names(base, msb, lsb):
    """Expand a (possibly bus) declaration name into scalar net names."""
    idxs = bit_indices(msb, lsb)
    if idxs is None:
        return [clean_ident(base)]
    cbase = clean_ident(base)
    return ["{}_{}_".format(cbase, i) for i in idxs]


def parse_netlist(text):
    """Parse the restricted netlist grammar into a list of modules."""
    modules = []
    module_names = {}
    cur = None
    for raw in text.splitlines():
        line = raw
        if "//" in line:
            line = line.split("//", 1)[0]
        line = line.strip()
        if not line:
            continue

        if line.startswith("module"):
            m = re.match(r"^module\s+([^\s(]+)\s*\((.*)\)\s*;?\s*$", line)
            if not m:
                continue
            name = m.group(1)
            ports = [p.strip() for p in m.group(2).split(",") if p.strip()]
            mod = {"name": name, "ports": ports,
                   "port_dir": {}, "wires": [], "body": []}
            modules.append(mod)
            module_names[name] = mod
            cur = mod
            continue

        if line.startswith("endmodule"):
            cur = None
            continue

        if cur is None:
            continue

        # port direction
        m = re.match(r"^(input|output|inout)\b", line)
        if m:
            m2 = re.match(
                r"^(input|output|inout)\s*(?:\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*)?([^\s;]+)\s*;?\s*$",
                line)
            if m2:
                msb = int(m2.group(2)) if m2.group(2) is not None else None
                lsb = int(m2.group(3)) if m2.group(3) is not None else None
                cur["port_dir"][m2.group(4)] = (m2.group(1), msb, lsb)
            continue

        # wire declaration
        m = re.match(r"^wire\b", line)
        if m:
            m2 = re.match(
                r"^wire\s*(?:\[\s*(\d+)\s*:\s*(\d+)\s*\]\s*)?([^\s;]+)\s*;?\s*$",
                line)
            if m2:
                msb = int(m2.group(1)) if m2.group(1) is not None else None
                lsb = int(m2.group(2)) if m2.group(2) is not None else None
                cur["wires"].append((m2.group(3), msb, lsb))
            continue

        # primitive gate (inside leaf cells)
        m = re.match(
            r"^(notif0|notif1|bufif0|bufif1|nand|nor|and|or|xor|xnor|not|buf)\s*\(",
            line)
        if m:
            g = re.match(
                r"^(notif0|notif1|bufif0|bufif1|nand|nor|and|or|xor|xnor|not|buf)\s*\((.*)\)\s*;?\s*$",
                line)
            if g:
                args = [a.strip() for a in g.group(2).split(",") if a.strip()]
                cur["body"].append(("gate", g.group(1), args))
            continue

        # module instance (single line:  TYPE INST ( .PIN(NET) , ... ) ;)
        m = re.match(r"^([^\s(]+)\s+([^\s(]+)\s*\((.*)\)\s*;?\s*$", line)
        if m:
            mtype = m.group(1)
            iname = m.group(2)
            pins_raw = m.group(3)
            pins = []
            for pm in re.finditer(r"\.\s*([^\s()]+)\s*\(\s*([^()]*?)\s*\)", pins_raw):
                pins.append((pm.group(1), pm.group(2).strip()))
            cur["body"].append(("inst", mtype, iname, pins))
            continue

    return modules, module_names


def resolve(ref, netmap):
    """Map a net reference through the current port-to-net binding."""
    if ref in netmap:
        return netmap[ref]
    m = re.match(r"^([^\[\]]+)\[(\d+)\]$", ref)
    if m:
        base, idx = m.group(1), m.group(2)
        if base in netmap:
            return "{}[{}]".format(netmap[base], idx)
    return ref


def get_top(modules):
    instantiated = set()
    for mod in modules:
        for item in mod["body"]:
            if item[0] == "inst":
                instantiated.add(item[1])
    tops = [m["name"] for m in modules if m["name"] not in instantiated]
    if tops:
        return tops[0]
    return modules[0]["name"] if modules else None


def flatten(top_name, modules, module_names):
    """DFS-inline wrappers; return the top module and its leaf instances."""
    top = module_names[top_name]
    leaf_instances = []  # (clean_mtype, clean_name, [(clean_pin, clean_net)])

    top_netmap = {}
    for p in top["ports"]:
        top_netmap[p] = p
    for (wname, _msb, _lsb) in top["wires"]:
        top_netmap[wname] = wname

    def expand(mod, prefix, netmap):
        for item in mod["body"]:
            if item[0] != "inst":
                continue
            _kind, mtype, iname, pins = item
            inst_key = (prefix + "_" if prefix else "") + iname

            if mtype.startswith("LEAF_"):
                cpins = []
                for pin, net in pins:
                    if is_pg(pin):
                        continue
                    rnet = resolve(net, netmap)
                    if is_pg(rnet):
                        continue
                    cpins.append((clean_ident(pin), clean_ident(rnet)))
                leaf_instances.append((clean_ident(mtype), clean_ident(inst_key), cpins))
                continue

            child = module_names.get(mtype)
            if child is None:
                # Unknown (non-leaf, non-wrapper) module: keep as a terminal instance.
                cpins = []
                for pin, net in pins:
                    if is_pg(pin):
                        continue
                    rnet = resolve(net, netmap)
                    if is_pg(rnet):
                        continue
                    cpins.append((clean_ident(pin), clean_ident(rnet)))
                leaf_instances.append((clean_ident(mtype), clean_ident(inst_key), cpins))
                continue

            child_netmap = {}
            for pin, net in pins:
                if is_pg(pin):
                    continue
                rnet = resolve(net, netmap)
                if is_pg(rnet):
                    continue
                child_netmap[pin] = rnet
            for p in child["ports"]:
                if p not in child_netmap and not is_pg(p):
                    child_netmap[p] = p
            expand(child, inst_key, child_netmap)

    expand(top, "", top_netmap)
    return top, leaf_instances


def build_ports_and_wires(mod):
    port_names = []
    decl_lines = []
    for p in mod["ports"]:
        if is_pg(p):
            continue
        direction, msb, lsb = mod["port_dir"].get(p, ("input", None, None))
        for nm in scalar_names(p, msb, lsb):
            port_names.append(nm)
            decl_lines.append("  {} {} ;".format(direction, nm))

    wire_names = []
    wire_lines = []
    seen = set()
    for (wname, msb, lsb) in mod["wires"]:
        if is_pg(wname):
            continue
        for nm in scalar_names(wname, msb, lsb):
            if nm in seen:
                continue
            seen.add(nm)
            wire_names.append(nm)
            wire_lines.append("  wire {} ;".format(nm))

    return port_names, decl_lines, wire_names, wire_lines


def emit_leaf_module(mod):
    port_names, decl_lines, wire_names, wire_lines = build_ports_and_wires(mod)
    header = "module {} ( {} ) ;".format(clean_ident(mod["name"]), " , ".join(port_names))
    lines = [header]
    lines.extend(decl_lines)
    lines.extend(wire_lines)
    for item in mod["body"]:
        if item[0] == "gate":
            gtype, args = item[1], item[2]
            clean_args = [clean_ident(a) for a in args if not is_pg(a)]
            lines.append("  {} ( {} ) ;".format(gtype, " , ".join(clean_args)))
        elif item[0] == "inst":
            mtype, iname, pins = item[1], item[2], item[3]
            cpins = []
            for pin, net in pins:
                if is_pg(pin) or is_pg(net):
                    continue
                cpins.append(".{}({})".format(clean_ident(pin), clean_ident(net)))
            lines.append("  {} {} ( {} ) ;".format(
                clean_ident(mtype), clean_ident(iname), " , ".join(cpins)))
    lines.append("endmodule")
    return "\n".join(lines)


def emit_flat(top, leaf_instances, modules):
    port_names, decl_lines, wire_names, wire_lines = build_ports_and_wires(top)

    port_set = set(port_names)
    wire_set = set(wire_names)
    extra_wires = []
    for (_mt, _nm, cpins) in leaf_instances:
        for (_pin, net) in cpins:
            if net not in port_set and net not in wire_set:
                wire_set.add(net)
                extra_wires.append("  wire {} ;".format(net))

    header = "module {} ( {} ) ;".format(clean_ident(top["name"]), " , ".join(port_names))
    lines = [header]
    lines.extend(decl_lines)
    lines.extend(wire_lines)
    lines.extend(extra_wires)
    for (mtype, nm, cpins) in leaf_instances:
        pinstr = " , ".join(".{}({})".format(p, n) for (p, n) in cpins)
        lines.append("  {} {} ( {} ) ;".format(mtype, nm, pinstr))
    lines.append("endmodule")

    leaf_mods = [m for m in modules if m["name"].startswith("LEAF_")]
    chunks = ["\n".join(lines)]
    for lm in leaf_mods:
        chunks.append(emit_leaf_module(lm))
    return "\n\n".join(chunks) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Flatten a hierarchical CDL/Verilog netlist.")
    ap.add_argument("input", help="input netlist (.v)")
    ap.add_argument("-o", "--output", default=None,
                    help="output netlist (.v); default: stdout")
    args = ap.parse_args(argv)

    with open(args.input, "r") as f:
        text = f.read()

    modules, module_names = parse_netlist(text)
    top_name = get_top(modules)
    top, leaf_instances = flatten(top_name, modules, module_names)
    out = emit_flat(top, leaf_instances, modules)

    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()