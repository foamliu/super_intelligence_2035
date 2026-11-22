#!/usr/bin/env python3
"""Reference solution for EDA-Eval-DesignFlow-NetMissingCellExtract-001.

Deterministic parser that, given a Verilog netlist and a simlib library file,
emits a structured JSON report of all "missing cell" instances (cells
instantiated in the netlist but NOT defined in simlib).

Usage:
    python netlist_missing_cell_extract.py <netlist> <simlib>
Output:
    JSON report on stdout (and ONLY JSON).
"""
import re
import json
import sys

# Verilog keywords whose line is never a cell instantiation.
KEYWORDS = {
    'module', 'endmodule', 'input', 'output', 'inout', 'wire', 'reg',
    'parameter', 'localparam', 'assign', 'always', 'initial', 'begin', 'end',
    'if', 'else', 'case', 'endcase', 'for', 'while', 'generate',
    'endgenerate', 'integer', 'real', 'time', 'genvar', 'function',
    'endfunction', 'task', 'endtask', 'defparam', 'tri', 'wand', 'wor',
    'supply0', 'supply1', 'specify', 'endspecify', 'specparam',
    # gate primitives (no instance name) -- excluded explicitly
    'not', 'buf', 'and', 'or', 'nand', 'nor', 'xor', 'xnor',
    'bufif0', 'bufif1', 'notif0', 'notif1', 'tranif1', 'tranif0',
    'tran', 'rtran', 'cmos', 'rcmos', 'pmos', 'nmos', 'rpmos', 'rnmos',
}


def strip_comments(text):
    """Replace // line comments and /* */ block comments with spaces,
    preserving newlines so line numbers stay intact."""
    def repl_block(m):
        return re.sub(r'[^\n]', ' ', m.group(0))
    text = re.sub(r'/\*.*?\*/', repl_block, text, flags=re.DOTALL)
    text = re.sub(r'//[^\n]*', lambda m: ' ' * len(m.group(0)), text)
    return text


def strip_specify(text):
    """Blank out specify/endspecify blocks (content), preserving newlines."""
    def repl(m):
        return re.sub(r'[^\n]', ' ', m.group(0))
    return re.sub(r'\bspecify\b.*?\bendspecify\b', repl, text, flags=re.DOTALL)


def extract_module_names(simlib_text):
    """Collect all defined module names in the simlib file."""
    names = set(re.findall(r'\bmodule\s+(\w+)\s*[#(;]', simlib_text))
    return names


def _skip_param(rest):
    """If rest starts with a parameter override #(...), consume it (balanced
    parens) and return the remainder; otherwise return rest unchanged. Return
    None on malformed input."""
    rest = rest.lstrip()
    if rest.startswith('#'):
        rest = rest[1:].lstrip()
        if not rest.startswith('('):
            return None
        depth = 0
        j = 0
        for j, ch in enumerate(rest):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
        else:
            return None
        rest = rest[j + 1:].lstrip()
    return rest


def _parse_ports(port_text):
    """Parse `.port(expr), .port(expr), ...` into an ordered dict."""
    ports = {}
    i = 0
    n = len(port_text)
    while i < n:
        if port_text[i] != '.':
            i += 1
            continue
        m = re.match(r'\.(\w+)\s*\(', port_text[i:])
        if not m:
            i += 1
            continue
        pname = m.group(1)
        start = i + m.end()
        depth = 1
        j = start
        while j < n and depth > 0:
            if port_text[j] == '(':
                depth += 1
            elif port_text[j] == ')':
                depth -= 1
            j += 1
        pexpr = port_text[start:j - 1].strip()
        ports[pname] = pexpr
        i = j
    return ports


def _parse_instance(stmt):
    """Try to parse a statement chunk as a cell instantiation.
    Returns (cell, inst, ports) or None."""
    stmt = stmt.strip()
    m = re.match(r'([A-Za-z_]\w*)\s*', stmt)
    if not m:
        return None
    cell = m.group(1)
    if cell in KEYWORDS:
        return None
    rest = stmt[m.end():]
    # optional parameter override BEFORE instance name
    rest = _skip_param(rest)
    if rest is None:
        return None
    m2 = re.match(r'([A-Za-z_]\w*)\s*', rest)
    if not m2:
        return None
    inst = m2.group(1)
    rest = rest[m2.end():]
    # optional parameter override AFTER instance name (non-standard but seen)
    rest = _skip_param(rest)
    if rest is None:
        return None
    if not rest.startswith('('):
        return None
    depth = 0
    j = 0
    for j, ch in enumerate(rest):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                break
    else:
        return None
    port_text = rest[1:j]
    ports = _parse_ports(port_text)
    return cell, inst, ports


def extract_instances(text):
    """Walk the (comment-stripped) netlist line by line, accumulating
    multi-line instance statements, and return a list of
    (start_line_1based, cell, inst, ports)."""
    lines = text.split('\n')
    instances = []
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()
        if not stripped or stripped.startswith('`'):
            i += 1
            continue
        fw = re.match(r'([A-Za-z_]\w*)', stripped)
        if not fw or fw.group(1) in KEYWORDS:
            i += 1
            continue
        # pre-check: must look like IDENT ( #(| IDENT  to be an instance start
        tail = stripped[fw.end():].lstrip()
        if not (tail.startswith('#(') or re.match(r'[A-Za-z_]\w*', tail)):
            i += 1
            continue
        buf = stripped
        start_line = i + 1
        j = i
        depth = buf.count('(') - buf.count(')')
        while (';' not in buf) or depth > 0:
            j += 1
            if j >= n:
                break
            nxt = lines[j].strip()
            buf += ' ' + nxt
            depth += nxt.count('(') - nxt.count(')')
            if depth < 0:
                depth = 0
        result = _parse_instance(buf)
        if result is not None:
            cell, inst, ports = result
            instances.append((start_line, cell, inst, ports))
            i = j + 1
            continue
        i += 1
    return instances


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("usage: netlist_missing_cell_extract.py <netlist> <simlib>\n")
        sys.exit(2)
    netlist_path = sys.argv[1]
    simlib_path = sys.argv[2]
    with open(simlib_path, 'r') as f:
        simlib_raw = f.read()
    simlib_text = strip_comments(simlib_raw)
    known_cells = extract_module_names(simlib_text)

    with open(netlist_path, 'r') as f:
        net_raw = f.read()
    net_text = strip_comments(net_raw)
    net_text = strip_specify(net_text)

    all_instances = extract_instances(net_text)

    missing_instances = []
    missing_cells = set()
    available_cells_used = set()
    available_count = 0
    for (line, cell, inst, ports) in all_instances:
        if cell in known_cells:
            available_count += 1
            available_cells_used.add(cell)
        else:
            missing_instances.append({
                "line": line,
                "cell": cell,
                "instance": inst,
                "ports": ports,
            })
            missing_cells.add(cell)

    report = {
        "missing_instances": missing_instances,
        "summary": {
            "total_instances": len(all_instances),
            "missing_count": len(missing_instances),
            "available_count": available_count,
            "missing_cells": sorted(missing_cells),
            "available_cells_used": sorted(available_cells_used),
        },
    }
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
