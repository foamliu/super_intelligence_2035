#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_sdc.py -- generic SDC (Synopsys Design Constraints) generator.

Reads every Verilog (*.v) file under <rtl_dir>, locates the module named
<top_module>, parses its port list (direction, width, and name), and emits an
SDC timing-constraints file.

Usage:
    python3 gen_sdc.py <rtl_dir> <top_module> [-o <out.sdc>]

Behaviour
---------
* A "main clock" constraint is always emitted.  If the top module exposes a
  clock input (a port whose name contains "clk" / "clock"), that port becomes a
  *real* clock; otherwise a *virtual* clock is created so that the IO delays
  still share a common timing reference.
* Every input port gets a ``set_input_delay`` and every output port gets a
  ``set_output_delay``, both referenced to the main clock.

Defaults
--------
    clock name   : clk
    clock period : 10.0 ns
    IO delay     : 2.0 ns
"""

from __future__ import print_function

import argparse
import glob
import os
import re
import sys

DEFAULT_CLOCK_NAME = "clk"
DEFAULT_CLOCK_PERIOD = 10.0   # ns
DEFAULT_IO_DELAY = 2.0        # ns


# --------------------------------------------------------------------------- #
# Verilog text helpers
# --------------------------------------------------------------------------- #
def read_verilog(rtl_dir):
    """Concatenate every .v file under rtl_dir (recursively) into one string."""
    paths = sorted(glob.glob(os.path.join(rtl_dir, "**", "*.v"), recursive=True))
    if not paths:
        # Fall back to a non-recursive glob for flat directories.
        paths = sorted(glob.glob(os.path.join(rtl_dir, "*.v")))
    if not paths:
        sys.exit("gen_sdc.py: no .v files found under %r" % rtl_dir)

    chunks = []
    for p in paths:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            chunks.append("\n// ---- file: %s ----\n" % os.path.basename(p))
            chunks.append(fh.read())
    return "\n".join(chunks)


def strip_comments(src):
    """Remove Verilog block (/* */) and line (//) comments."""
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", " ", src)
    return src


def extract_module_header(src, top_module):
    """Return the raw text between 'module <top_module>' and the closing ';'."""
    m = re.search(r"\bmodule\s+" + re.escape(top_module) + r"\b", src)
    if m is None:
        sys.exit("gen_sdc.py: module %r not found" % top_module)
    end = src.find(";", m.end())
    if end == -1:
        sys.exit("gen_sdc.py: could not find end of header for %r" % top_module)
    return src[m.end():end]


def extract_module_body(src, top_module):
    """Return the module body (header end .. endmodule), or '' if absent."""
    m = re.search(r"\bmodule\s+" + re.escape(top_module) + r"\b", src)
    if m is None:
        return ""
    semicolon = src.find(";", m.end())
    if semicolon == -1:
        return ""
    em = re.search(r"\bendmodule\b", src[semicolon:])
    if em is None:
        return src[semicolon:]
    return src[semicolon:semicolon + em.start()]


def gather_parameters(header, body):
    """Collect ``parameter NAME = value`` defaults (header #() + module body)."""
    params = {}

    def _scan(text):
        for m in re.finditer(
                r"\b(?:parameter|localparam)\s+(\w+)\s*=\s*([^,;)\s]+)", text):
            name, value = m.group(1), m.group(2)
            try:
                params[name] = int(safe_eval_int(value, params))
            except ValueError:
                params[name] = value

    _scan(header)
    _scan(body)
    return params


# --------------------------------------------------------------------------- #
# small, safe integer expression evaluator for bus bounds
# --------------------------------------------------------------------------- #
def safe_eval_int(expr, params=None):
    """Evaluate a (substituted) integer expression like 'WIDTH-1' safely."""
    expr = str(expr).strip()
    if params:
        for name, val in params.items():
            if isinstance(val, int):
                expr = re.sub(r"\b%s\b" % re.escape(name), str(val), expr)
    if re.fullmatch(r"[\d+\-*/()\s]+", expr) is None:
        raise ValueError("unsupported integer expression: %r" % expr)
    return int(eval(expr, {"__builtins__": {}}, {}))


# --------------------------------------------------------------------------- #
# port parsing
# --------------------------------------------------------------------------- #
def parse_ports(header, params):
    """Parse an ANSI / non-ANSI style module port list.

    Returns a list of dicts: [{'name', 'dir', 'range'}] in declaration order.
    'range' is None for scalar ports, otherwise the resolved "[msb:lsb]" string.
    """
    params = dict(params)

    # drop a leading parameter port list:  #(parameter WIDTH = 16)
    text = re.sub(r"^\s*#\s*\([^()]*\)", " ", header, count=1)

    # locate the (single) port-list parens
    i = text.find("(")
    j = text.rfind(")")
    if i == -1 or j == -1 or j <= i:
        return []
    body = text[i + 1:j]

    # normalise whitespace/newlines so each comma-separated token is on one line
    body = re.sub(r"\s+", " ", body)
    tokens = [t.strip() for t in body.split(",") if t.strip()]

    ports = []
    cur_dir = None
    cur_range = None

    for tok in tokens:
        dm = re.search(r"\b(input|output|inout)\b", tok)
        if dm:
            # new declaration begins
            cur_dir = dm.group(1)
            rest = re.sub(r"\b(input|output|inout)\b", " ", tok, count=1)
            rest = re.sub(r"\b(wire|reg|logic|signed|unsigned)\b", " ", rest)
            rest = rest.strip()
            cur_range = None
        else:
            rest = tok

        nm = re.match(r"^\s*(\[[^\[\]]*\])?\s*(\w+)\s*$", rest)
        if not nm:
            continue

        raw_range = nm.group(1)
        name = nm.group(2)

        if raw_range is not None:
            cur_range = resolve_range(raw_range, params)

        ports.append({
            "name": name,
            "dir": cur_dir,
            "range": cur_range,
        })

    return ports


def resolve_range(raw_range, params):
    """Resolve '[msb:lsb]' (after parameter substitution) to concrete bounds."""
    inner = raw_range.strip()[1:-1]          # strip '[' and ']'
    if ":" not in inner:
        msb = lsb = inner
    else:
        msb, lsb = inner.split(":", 1)
    msb = safe_eval_int(msb, params)
    lsb = safe_eval_int(lsb, params)
    return "[%d:%d]" % (msb, lsb)


def port_label(port):
    """Return the SDC 'get_ports' label for one port (bus-expanded)."""
    if port["range"]:
        return "%s%s" % (port["name"], port["range"])
    return port["name"]


# --------------------------------------------------------------------------- #
# SDC generation
# --------------------------------------------------------------------------- #
def generate_sdc(rtl_dir, top_module):
    src = read_verilog(rtl_dir)
    src = strip_comments(src)

    header = extract_module_header(src, top_module)
    body = extract_module_body(src, top_module)
    params = gather_parameters(header, body)
    ports = parse_ports(header, params)

    if not ports:
        sys.exit("gen_sdc.py: no ports parsed for module %r" % top_module)

    inputs = [p for p in ports if p["dir"] in ("input", "inout")]
    outputs = [p for p in ports if p["dir"] in ("output", "inout")]

    # clock detection (real clock input vs. combinational virtual clock)
    clock_ports = [p for p in inputs
                   if re.search(r"clk|clock", p["name"], re.IGNORECASE)]

    bar = "#" * 72
    lines = [bar,
             "# SDC for module: %s" % top_module,
             "# Generated by gen_sdc.py",
             bar,
             ""]

    if clock_ports:
        clk_port = port_label(clock_ports[0])
        lines.append("# Main clock (real clock input)")
        lines.append("create_clock -name %s -period %s [get_ports {%s}]"
                     % (DEFAULT_CLOCK_NAME, _fmt(DEFAULT_CLOCK_PERIOD), clk_port))
    else:
        lines.append("# Main clock")
        lines.append("# %s is purely combinational (no clock input port)," % top_module)
        lines.append("# so a virtual clock is used as the common timing reference.")
        lines.append("create_clock -name %s -period %s"
                     % (DEFAULT_CLOCK_NAME, _fmt(DEFAULT_CLOCK_PERIOD)))

    lines.append("")

    if inputs:
        lines.append("# Input delays")
        labels = " ".join(port_label(p) for p in inputs)
        lines.append("set_input_delay -clock %s %s [get_ports {%s}]"
                     % (DEFAULT_CLOCK_NAME, _fmt(DEFAULT_IO_DELAY), labels))
    if outputs:
        lines.append("# Output delays")
        labels = " ".join(port_label(p) for p in outputs)
        lines.append("set_output_delay -clock %s %s [get_ports {%s}]"
                     % (DEFAULT_CLOCK_NAME, _fmt(DEFAULT_IO_DELAY), labels))

    lines.append("")
    return "\n".join(lines)


def _fmt(value):
    """Format a float without a trailing '.0' when it is whole."""
    if isinstance(value, float) and value.is_integer():
        return "%d" % int(value)
    return str(value)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="gen_sdc.py",
        description="Generate an SDC file from a Verilog top-module port list.")
    ap.add_argument("rtl_dir", help="directory containing the .v RTL files")
    ap.add_argument("top_module", help="name of the top module to constrain")
    ap.add_argument("-o", "--output", dest="output", default=None,
                    help="output SDC file (default: <top_module>.sdc)")
    args = ap.parse_args(argv)

    sdc = generate_sdc(args.rtl_dir, args.top_module)

    out_path = args.output if args.output else args.top_module + ".sdc"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(sdc + "\n")

    # always echo the result so it can be inspected/piped
    sys.stdout.write(sdc + "\n")
    sys.stderr.write("gen_sdc.py: wrote %s\n" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())