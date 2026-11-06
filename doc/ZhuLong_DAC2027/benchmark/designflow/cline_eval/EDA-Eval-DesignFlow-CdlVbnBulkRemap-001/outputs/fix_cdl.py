#!/usr/bin/env python3
"""fix_cdl.py -- generic CDL body-bias (bulk) remapper for the bufLx* buffer family.

StarRCXT RCC extraction fails when a bufLx* buffer instance still ties its
body-bias bulk terminals to the top-level floating nets vbn!/vbp! instead of
the real power/ground nets vss!/vcc!.  This script locates those instances
structurally (subcircuit name matches the glob `bufLx*` AND the bulk terminals
are still connected to vbn!/vbp!) and remaps only those two terminals:

    vbn! -> vss!     (the net feeding the subcircuit's vss! port)
    vbp! -> vcc!     (the net feeding the subcircuit's vcc! port)

The signal terminals (A/Y) and the power terminals (vcc!/vss!) are left
untouched, and every other line in the CDL is copied verbatim.  Nothing about
this script is specific to instance name XI37 or cell name bufLx4; it works on
any netlist whose buffer subcircuits are named `bufLx*` and carry body-bias
ports named vbn!/vbp!.

Usage:
    fix_cdl.py <in.cdl> <out.cdl> <out.diff>

Exit codes:
    0  success (fix applied, or nothing to change / already fixed)
    2  no `bufLx*` instance is present in the input CDL
"""

import sys
import re
import difflib


def core_net(net):
    """Strip the CDL global-net '!' suffix (e.g. 'vbn!' -> 'vbn')."""
    return net.rstrip('!')


def split_line(line):
    """Split a raw line into (content, line_ending)."""
    if line.endswith('\r\n'):
        return line[:-2], '\r\n'
    if line.endswith('\n'):
        return line[:-1], '\n'
    if line.endswith('\r'):
        return line[:-1], '\r'
    return line, ''


def is_buf_cell(cell_name):
    """True if the cell name matches the bufLx* buffer-family glob."""
    return cell_name is not None and cell_name.startswith('bufLx')


def parse_subckt(content):
    """Return (name, [ports]) for a .SUBCKT statement, else None."""
    m = re.match(r'^\.SUBCKT\s+(\S+)\s*(.*)$', content, re.IGNORECASE)
    if not m:
        return None
    name = m.group(1)
    ports = m.group(2).split()
    return name, ports


def remap_bulk(conns, ports):
    """Retarget the body-bias bulk terminals of one bufLx* instance.

    `conns` is the ordered list of net names appearing between the instance
    name and the '/'; `ports` is the subcircuit's ordered port list.  Returns
    (new_conns, num_changed).
    """
    if not ports:
        # Fall back to the documented bufLx* signature if unknown.
        ports = ['A', 'Y', 'vbn!', 'vbp!', 'vcc!', 'vss!']

    vbn_idx = vbp_idx = vcc_idx = vss_idx = None
    for i, p in enumerate(ports):
        c = core_net(p)
        if c == 'vbn' and vbn_idx is None:
            vbn_idx = i
        elif c == 'vbp' and vbp_idx is None:
            vbp_idx = i
        elif c == 'vcc' and vcc_idx is None:
            vcc_idx = i
        elif c == 'vss' and vss_idx is None:
            vss_idx = i

    new_conns = list(conns)
    changed = 0

    if vbn_idx is not None and vbn_idx < len(new_conns):
        if core_net(new_conns[vbn_idx]) == 'vbn':
            new_conns[vbn_idx] = (
                new_conns[vss_idx]
                if vss_idx is not None and vss_idx < len(new_conns)
                else 'vss!'
            )
            changed += 1

    if vbp_idx is not None and vbp_idx < len(new_conns):
        if core_net(new_conns[vbp_idx]) == 'vbp':
            new_conns[vbp_idx] = (
                new_conns[vcc_idx]
                if vcc_idx is not None and vcc_idx < len(new_conns)
                else 'vcc!'
            )
            changed += 1

    return new_conns, changed


def main(argv):
    if len(argv) != 3:
        sys.stderr.write('usage: fix_cdl.py <in.cdl> <out.cdl> <out.diff>\n')
        return 1

    in_cdl, out_cdl, out_diff = argv[0], argv[1], argv[2]

    with open(in_cdl, 'r', newline='') as f:
        raw = f.read()
    lines = raw.splitlines(keepends=True)

    # Pass 1: collect every subcircuit's ordered port list.
    subckts = {}
    for line in lines:
        content, _ = split_line(line)
        result = parse_subckt(content.strip())
        if result is not None:
            subckts[result[0]] = result[1]

    # Pass 2: rewrite bufLx* instances whose bulk terminals float on
    # vbn!/vbp!; copy every other line verbatim.
    out_lines = []
    has_buf_instance = False
    changed_terminals = 0

    for line in lines:
        content, ending = split_line(line)
        stripped = content.strip()
        lead = content[:len(content) - len(content.lstrip())]
        new_line = None

        if stripped[:1] in ('X', 'x'):
            toks = stripped.split()
            if '/' in toks:
                slash = toks.index('/')
                cell = toks[slash + 1] if slash + 1 < len(toks) else None
                if is_buf_cell(cell):
                    has_buf_instance = True
                    conns = toks[1:slash]
                    ports = subckts.get(cell)
                    new_conns, n = remap_bulk(conns, ports)
                    if n:
                        changed_terminals += n
                        rebuilt = [toks[0]] + new_conns + toks[slash:]
                        new_line = lead + ' '.join(rebuilt) + ending

        out_lines.append(new_line if new_line is not None else line)

    # Write the fixed CDL (byte-for-byte copy of the input when unchanged).
    with open(out_cdl, 'w', newline='') as f:
        f.writelines(out_lines)

    # Write the unified diff.  Pass lines that still carry their trailing
    # newlines so difflib emits a proper line terminator on every line.
    diff = difflib.unified_diff(
        lines,
        out_lines,
        fromfile=in_cdl,
        tofile=out_cdl,
        lineterm='\n',
    )
    with open(out_diff, 'w', newline='') as f:
        f.write(''.join(diff))

    if not has_buf_instance:
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))