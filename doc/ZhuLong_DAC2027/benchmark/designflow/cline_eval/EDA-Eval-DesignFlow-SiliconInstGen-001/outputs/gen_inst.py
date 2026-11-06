#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_inst.py -- SiliconSmart ".inst" generator from an SPF / CDL netlist.

Usage
-----
    python3 gen_inst.py <spf_file> <output_inst_file>

Behaviour
---------
  1. Read the SPF / CDL netlist text.
  2. Extract the ordered port list from the ``.SUBCKT`` line.
  3. Read the ``.GLOBAL`` line(s) and split the nets into power / ground
     supplies (body-bias rails such as ``vbp`` / ``vbn`` are grouped with the
     matching supply domain: ``vbp`` -> power, ``vbn`` -> ground).
  4. Parse primitive instance lines (``X<i> <in> <out> <subckt> ...``) to
     detect which subckt ports are *output* ports (driven from the ``out``
     terminal of a gate and never used as an ``in`` terminal) and which are
     ordinary inputs.
  5. Detect complementary / differential port pairs (e.g. ``Clk<0>`` /
     ``ClkN<0>``), recognise clock pins and an async-reset pin.
  6. Write a SiliconSmart ".inst" file with the ``add_pin`` /
     ``set_subckt_ports`` / ``add_switching_set`` / ``add_latch`` /
     ``add_function`` / ``config`` sections.

Only the Python standard library is used.
"""

import re
import sys

# ---------------------------------------------------------------------------
# Heuristics / configuration
# ---------------------------------------------------------------------------
POWER_KEYWORDS = ("vcc", "vdd", "vpp", "vbp", "vp", "vdda", "power", "pwr")
GROUND_KEYWORDS = ("vss", "gnd", "vnn", "vbn", "vn", "vssa", "ground", "grnd")

CLOCK_RE = re.compile(r"^(clk|ck|clock|cph)", re.IGNORECASE)
RESET_RE = re.compile(r"^(rn|rstn|rst|resetn|reset|clr|clrn|prn|pre|setn)($|b?)",
                      re.IGNORECASE)


def classify_supply(name):
    """Return 'power', 'ground' or None for a given net name."""
    low = name.lower()
    for kw in POWER_KEYWORDS:
        if kw in low:
            return "power"
    for kw in GROUND_KEYWORDS:
        if kw in low:
            return "ground"
    return None


def strip_inline_comment(line):
    """Drop an inline '$' comment (SPICE/SPF style) and surrounding blanks."""
    if "$" in line:
        line = line.split("$", 1)[0]
    return line.strip()


def parse_netlist(text):
    """Parse an SPF/CDL netlist.

    Returns ``(subckt_name, ports, global_nets, instances)`` where:

    * ``ports``       -- ordered list of ``.SUBCKT`` port tokens
    * ``global_nets`` -- ordered list of ``.GLOBAL`` net tokens
    * ``instances``   -- list of dicts ``{name, in, out, subckt, rest}``
    """
    subckt_name = None
    ports = []
    global_nets = []
    instances = []
    in_subckt = False

    for raw in text.splitlines():
        line = strip_inline_comment(raw)
        if not line:
            continue
        if line.startswith("*"):
            continue
        upper = line.upper()

        if upper.startswith(".SUBCKT"):
            toks = line.split()
            if len(toks) >= 2:
                subckt_name = toks[1]
                ports = toks[2:]
            in_subckt = True
            continue

        if upper.startswith(".GLOBAL"):
            global_nets.extend(line.split()[1:])
            continue

        if upper.startswith(".ENDS"):
            in_subckt = False
            continue

        if line.startswith("."):
            # Other control statements (.TEMP, .OPTION, .MODEL, ...) - ignore.
            continue

        # Primitive / subckt instance lines start with 'X'.  Netlist header
        # convention is:  X<name> <in> <out> <subckt> [control ...] [vdd] [vss]
        if in_subckt and line[0].upper() == "X":
            toks = line.split()
            if len(toks) >= 4:
                instances.append({
                    "name": toks[0],
                    "in": toks[1],
                    "out": toks[2],
                    "subckt": toks[3],
                    "rest": toks[4:],
                })
            continue

    return subckt_name, ports, global_nets, instances


def sort_naturally(items):
    """Sort strings with embedded numbers in natural order."""
    def key(s):
        return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)]
    return sorted(items, key=key)


def insert_N(name):
    """Return the complementary/negative name of a differential signal.

    ``Clk<3>`` -> ``ClkN<3>``, ``CK`` -> ``CKN``, ``A`` -> ``AN``.
    """
    bus = re.search(r"<[^>]*>|\[[^\]]*\]", name)
    if bus:
        return name[:bus.start()] + "N" + name[bus.start():]
    return name + "N"


def find_differential_pairs(ports):
    """Return a list of ``(pos, neg)`` complementary port pairs."""
    pset = set(ports)
    pairs = []
    used = set()
    for p in ports:
        if p in used:
            continue
        n = insert_N(p)
        if n in pset and n != p:
            pairs.append((p, n))
            used.add(p)
            used.add(n)
    return pairs


def analyse(subckt_name, ports, global_nets, instances):
    """Classify the ports of a cell.

    Returns a dict with keys: ``power``, ``ground``, ``output``, ``pairs``,
    ``pos``, ``neg``, ``clock_pins``, ``reset_pins``, ``data_pins``.
    """
    power = []
    ground = []
    for net in global_nets:
        kind = classify_supply(net)
        if kind == "power" and net not in power:
            power.append(net)
        elif kind == "ground" and net not in ground:
            ground.append(net)

    supply_nets = set(power) | set(ground)

    # Output ports: driven by an instance ("out" terminal) and never used as
    # an "in" terminal of any instance.
    in_nodes = set(inst["in"] for inst in instances)
    out_nodes = set(inst["out"] for inst in instances)
    output = [p for p in ports if p in out_nodes and p not in in_nodes]

    pairs = sort_naturally(find_differential_pairs(ports))
    pos = [p for p, _ in pairs]
    neg = [n for _, n in pairs]
    pair_names = set(pos) | set(neg)

    # Clock pins: complementary pair members plus any single-ended clock
    # (e.g. a clock pre-driver input such as CkPre).
    clock_pins = []
    for p in ports:
        if p in supply_nets:
            continue
        if p in pair_names or CLOCK_RE.match(p):
            if p not in clock_pins:
                clock_pins.append(p)

    reset_pins = [p for p in ports
                  if p not in supply_nets and p not in output
                  and p not in pair_names and RESET_RE.match(p)]

    data_pins = [p for p in ports
                 if p not in supply_nets and p not in output
                 and p not in clock_pins and p not in reset_pins]
    data_pins = sort_naturally(data_pins)

    return {
        "power": power,
        "ground": ground,
        "output": output,
        "pairs": pairs,
        "pos": pos,
        "neg": neg,
        "clock_pins": clock_pins,
        "reset_pins": reset_pins,
        "data_pins": data_pins,
    }


def render(subckt_name, ports, global_nets, a):
    """Render the SiliconSmart .inst file body."""
    L = []
    rule = "# " + "-" * 70

    L.append("## " + "=" * 69)
    L.append("##  SiliconSmart .inst  :  %s" % (subckt_name if subckt_name else "?"))
    L.append("##  generated by gen_inst.py  (pure Python standard library)")
    L.append("## " + "-" * 69)
    if subckt_name:
        L.append("##  .SUBCKT %s %s" % (subckt_name, " ".join(ports)))
    if global_nets:
        L.append("##  .GLOBAL %s" % " ".join(global_nets))
    L.append("## " + "=" * 69)
    L.append("")

    all_names = a["power"] + a["ground"] + list(ports)
    w = max((len(n) for n in all_names), default=0)

    L.append(rule)
    L.append("#  power / ground supplies (from .GLOBAL)")
    L.append(rule)
    for n in a["power"]:
        L.append("add_pin %-*s power" % (w, n))
    for n in a["ground"]:
        L.append("add_pin %-*s ground" % (w, n))
    L.append("")

    L.append(rule)
    L.append("#  signal pins")
    L.append(rule)
    for p in ports:
        typ = "output" if p in a["output"] else "input"
        L.append("add_pin %-*s %s" % (w, p, typ))
    L.append("")

    L.append(rule)
    L.append("#  subckt port list (must match .SUBCKT order)")
    L.append(rule)
    L.append("set_subckt_ports {%s}" % " ".join(ports))
    L.append("")

    L.append(rule)
    L.append("#  complementary / differential switching sets")
    L.append(rule)
    for p, n in a["pairs"]:
        L.append("add_switching_set {%s %s}" % (p, n))
    L.append("")

    L.append(rule)
    L.append("#  sequential element (latch)")
    L.append(rule)
    L.append("add_latch {")
    if a["data_pins"]:
        L.append("    data    {%s}" % " ".join(a["data_pins"]))
    if a["pos"]:
        L.append("    clock   {%s}" % " ".join(a["pos"]))
    if a["neg"]:
        L.append("    clockn  {%s}" % " ".join(a["neg"]))
    if a["output"]:
        L.append("    output  %s" % " ".join(a["output"]))
    if a["reset_pins"]:
        L.append("    reset   %s" % " ".join(a["reset_pins"]))
    L.append("}")
    L.append("")

    L.append(rule)
    L.append("#  logic function")
    L.append(rule)
    L.append("add_function {")
    terms = []
    for i, d in enumerate(a["data_pins"]):
        if i < len(a["pos"]):
            terms.append("(%s & %s)" % (d, a["pos"][i]))
        else:
            terms.append(d)
    if a["output"] and terms:
        L.append("    %s = %s" % (a["output"][0], " | ".join(terms)))
    elif a["output"]:
        L.append("    %s" % a["output"][0])
    L.append("}")
    L.append("")

    L.append(rule)
    L.append("#  config")
    L.append(rule)
    L.append("config {")
    if subckt_name:
        L.append("    cell    %s" % subckt_name)
        L.append("    subckt  %s" % subckt_name)
    L.append("}")
    L.append("")

    return "\n".join(L)


def generate(text):
    """Generate .inst content from raw netlist text."""
    subckt_name, ports, global_nets, instances = parse_netlist(text)
    a = analyse(subckt_name, ports, global_nets, instances)
    return render(subckt_name, ports, global_nets, a)


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: python3 gen_inst.py <spf_file> <output_inst_file>\n")
        return 2

    spf_file, out_file = argv[1], argv[2]
    with open(spf_file, "r") as fh:
        text = fh.read()

    result = generate(text)
    with open(out_file, "w") as fh:
        fh.write(result)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))