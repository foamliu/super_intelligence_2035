#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
port_catch.py -- generic CDL/SPICE netlist instance port-connectivity grabber.

Pure standard-library implementation (no cck / EDA-tool license required).

Usage:
    python3 port_catch.py <netlist> <inst_fullpath> [-o out.json]

For a hierarchical instance path such as `top.I1.I2` it locates the target
subcircuit instantiation and, for every port of its master subcircuit, reports:

    name       : master port name
    direction  : direction declared by .PININFO (I->input / O->output / B->bidir)
    net        : the net this port is wired to in the parent hierarchy
    neighbors  : other instances in the *same* parent hierarchy that are wired
                 to that same net (the target itself is excluded).
                 Each neighbor is {inst, terminal, master} where:
                   - a subcircuit instance (X*) uses its master port name as
                     `terminal` and its master subcircuit name as `master`;
                   - a MOS instance (M*) uses D/G/S/B as `terminal` and its
                     model name as `master`;
                   - a two-terminal device (R/C/V/I/...) uses P/N as `terminal`
                     and has an empty `master`.
"""

import argparse
import json
import sys

PININFO_DIR = {
    'I': 'input',
    'O': 'output',
    'B': 'bidir',
}

MOS_TERMINALS = ['D', 'G', 'S', 'B']
TWOTERM_TERMINALS = ['P', 'N']


class Subckt(object):
    """A .SUBCKT definition."""

    def __init__(self, name):
        self.name = name
        self.ports = []          # ordered port names
        self.pininfo = {}        # port -> direction letter ('I'/'O'/'B')
        self.instances = []      # list of Instance, in source order

    def find_instance(self, name):
        for inst in self.instances:
            if inst.name == name:
                return inst
        return None


class Instance(object):
    """A single device instantiation line."""

    def __init__(self, letter, name):
        self.letter = letter    # 'X', 'M', 'R', ...
        self.name = name        # full instance name (incl. leading device letter)
        self.nets = []          # ordered net terminals
        self.master = ''        # master subckt (X) or model (M)

    def is_subckt(self):
        return self.letter == 'X'


def read_merged_lines(text):
    """Split into logical lines, merging SPICE '+' continuation lines."""
    logical = []
    for raw in text.split('\n'):
        s = raw.rstrip('\r')
        stripped = s.strip()
        if stripped == '':
            continue
        if stripped.startswith('+'):
            cont = stripped[1:].strip()
            if logical:
                logical[-1] = logical[-1] + ' ' + cont
            else:
                logical.append(cont)
        else:
            logical.append(stripped)
    return logical


def directive_upper(stripped):
    """Return the uppercase directive keyword if `stripped` is a dot directive.

    CDL conventionally writes some dot directives with a star prefix, e.g.
    ``*.PININFO``; we recognise both ``.PININFO`` and ``*.PININFO``.
    """
    if stripped.startswith('*.'):
        return stripped[1:].split()[0].upper()
    if stripped.startswith('.'):
        return stripped.split()[0].upper()
    return None


def parse_netlist(text):
    """Parse netlist text into subcircuit definitions.

    Returns (subckts, exact_index, ci_index): `subckts` is the list of Subckt
    objects in definition order, the two dicts map subckt name to a Subckt
    (exact match and case-insensitive match respectively).
    """
    lines = read_merged_lines(text)
    subckts = []
    exact_index = {}
    ci_index = {}

    # ---- pass 1: collect .SUBCKT names / ports / .PININFO ----
    current = None
    for line in lines:
        direc = directive_upper(line)
        if direc is None:
            continue
        toks = line.split()
        if direc == '.SUBCKT':
            if len(toks) < 2:
                continue
            sc = Subckt(toks[1])
            sc.ports = toks[2:]
            subckts.append(sc)
            exact_index[sc.name] = sc
            ci_index[sc.name.lower()] = sc
            current = sc
        elif direc == '.ENDS':
            current = None
        elif direc == '.PININFO' and current is not None:
            for item in toks[1:]:
                port, sep, d = item.partition(':')
                if sep:
                    current.pininfo[port] = d.strip().upper()

    # ---- pass 2: parse device instances into their subckt ----
    current = None
    for line in lines:
        direc = directive_upper(line)
        if direc is not None:
            toks = line.split()
            if direc == '.SUBCKT' and len(toks) >= 2:
                current = ci_index.get(toks[1].lower())
            elif direc == '.ENDS':
                current = None
            continue

        toks = line.split()
        if not toks or current is None:
            continue
        first = toks[0]
        letter = first[0].upper()
        if not letter.isalpha():
            continue

        inst = Instance(letter, first)
        rest = toks[1:]

        if letter == 'X':
            if '/' in rest:
                i = rest.index('/')
                inst.nets = rest[:i]
                after = rest[i + 1:]
                inst.master = after[0] if after else ''
            else:
                inst.nets, inst.master = split_x_no_slash(rest, ci_index)
        elif letter == 'M':
            # drain gate source bulk model [params...]
            inst.nets = rest[:4]
            if len(rest) > 4:
                inst.master = rest[4]
        else:
            # two-terminal device (R/C/V/I/L/D/B ...): n1 n2 ...
            inst.nets = rest[:2]

        current.instances.append(inst)

    return subckts, exact_index, ci_index


def split_x_no_slash(rest, ci_index):
    """Best-effort split of an X instance line without a '/' separator.

    Tries to find, among the tokens, a master subcircuit name whose port count
    equals the number of net tokens preceding it.  Falls back to treating the
    last token as the master name.
    """
    n = len(rest)
    for i in range(1, n):
        cand = rest[i]
        sc = ci_index.get(cand.lower())
        if sc is not None and len(sc.ports) == i:
            return rest[:i], cand
    if n >= 1:
        return rest[:-1], rest[-1]
    return [], ''


def lookup_subckt(exact_index, ci_index, name):
    if name in exact_index:
        return exact_index[name]
    return ci_index.get(name.lower())


def instance_connections(inst, exact_index, ci_index):
    """Return aligned (net, terminal, master) tuples for an instance."""
    conns = []
    if inst.letter == 'X':
        sc = lookup_subckt(exact_index, ci_index, inst.master)
        ports = sc.ports if sc else []
        for i, net in enumerate(inst.nets):
            terminal = ports[i] if i < len(ports) else ''
            conns.append((net, terminal, inst.master))
    elif inst.letter == 'M':
        for i, net in enumerate(inst.nets):
            terminal = MOS_TERMINALS[i] if i < len(MOS_TERMINALS) else ''
            conns.append((net, terminal, inst.master))
    else:
        for i, net in enumerate(inst.nets):
            terminal = TWOTERM_TERMINALS[i] if i < len(TWOTERM_TERMINALS) else ''
            conns.append((net, terminal, ''))
    return conns


def map_direction(letter):
    return PININFO_DIR.get(letter, '')


def port_catch(netlist_text, fullpath):
    subckts, exact_index, ci_index = parse_netlist(netlist_text)

    parts = fullpath.split('.')
    if len(parts) < 2:
        raise ValueError(
            'instance full path must have at least two levels: <top>.<inst>')

    top = lookup_subckt(exact_index, ci_index, parts[0])
    if top is None:
        raise ValueError('top subcircuit not found: %s' % parts[0])

    scope = top
    target = None
    target_parent = None
    for name in parts[1:]:
        inst = scope.find_instance(name)
        if inst is None or not inst.is_subckt():
            raise ValueError(
                'instance %r is not a subcircuit instance in %r'
                % (name, scope.name))
        target = inst
        target_parent = scope
        nxt = lookup_subckt(exact_index, ci_index, inst.master)
        if nxt is None:
            raise ValueError('master subcircuit %r not defined' % inst.master)
        scope = nxt

    master_sc = lookup_subckt(exact_index, ci_index, target.master)
    if master_sc is None:
        raise ValueError('master subcircuit %r not defined' % target.master)

    result = {
        'instance': fullpath,
        'master': target.master,
        'ports': [],
    }

    for i, pname in enumerate(master_sc.ports):
        net = target.nets[i] if i < len(target.nets) else ''
        neighbors = []
        for other in target_parent.instances:
            if other.name == target.name:
                continue
            for net_other, terminal, master in instance_connections(
                    other, exact_index, ci_index):
                if net_other == net:
                    neighbors.append({
                        'inst': other.name,
                        'terminal': terminal,
                        'master': master,
                    })
        result['ports'].append({
            'name': pname,
            'direction': map_direction(master_sc.pininfo.get(pname, '')),
            'net': net,
            'neighbors': neighbors,
        })

    return result


def main(argv):
    parser = argparse.ArgumentParser(
        description='Grab a subcircuit instance ports, nets and neighbors.')
    parser.add_argument('netlist', help='path to CDL/SPICE netlist')
    parser.add_argument('inst_fullpath',
                        help='hierarchical instance path, e.g. top.I1.I2')
    parser.add_argument('-o', '--output', default=None,
                        help='output JSON file (default: stdout)')
    args = parser.parse_args(argv)

    with open(args.netlist, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    result = port_catch(text, args.inst_fullpath)
    out = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(out + '\n')
    else:
        print(out)


if __name__ == '__main__':
    main(sys.argv[1:])