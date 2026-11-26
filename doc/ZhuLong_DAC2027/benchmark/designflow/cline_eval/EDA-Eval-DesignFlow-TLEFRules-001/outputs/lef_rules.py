#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lef_rules.py -- Parse a LEF technology (techlef) file and emit a JSON summary of
the routing (wiring) layer rules and the via/cut layer rules.

Usage:
    python3 lef_rules.py <techlef_path>

The summary is written to stdout as a single JSON object with these keys:

    "routing_layers" : every TYPE ROUTING layer
    "cut_layers"     : every TYPE CUT (via/cut) layer
    "vias"           : every VIA definition
    "viarules"       : every VIARULE ... GENERATE rule

Field conventions:
 * width / max_width / area / spacing / resistance are numbers; integer tokens
   (e.g. "12") stay integers, decimal tokens (e.g. "8.88") stay floats.
 * pitch and offset are lists of numbers (LEF permits one or two values).
 * spacing_table is a dict {"parallel_run_length", "width", "spacing"} for
   layers that declare a SPACINGTABLE, and null otherwise.
 * vias: "cuts" is the number of RECTs drawn on the via's CUT layer,
   "layers" preserves the LAYER order inside the VIA.
 * viarules: "enclosures" maps layer name -> [overhang1, overhang2];
   "width_range" maps layer name -> "min TO max" (a flat string dict).
"""

import json
import sys


def _num(s):
    """Convert a numeric LEF token, preserving integer-vs-float spelling."""
    s = s.strip()
    if not s:
        return None
    try:
        if '.' in s or 'e' in s or 'E' in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def _tokenize(text):
    """Split LEF text into tokens.

    Handles '#' line comments, double-quoted strings (kept as single tokens,
    including their quotes), and ';' as a standalone statement terminator.
    """
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c == '#':
            while i < n and text[i] != '\n':
                i += 1
            continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 1
            tokens.append(text[i:j + 1])
            i = j + 1
            continue
        if c == ';':
            tokens.append(';')
            i += 1
            continue
        j = i
        while j < n and not text[j].isspace() and text[j] not in ';#"':
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def _parse_spacing_table(stmt):
    """Parse a SPACINGTABLE statement (token list, first element 'SPACINGTABLE').

    Returns:
        {"parallel_run_length": [..], "width": [..], "spacing": [[..], ...]}
    """
    i = 1  # skip 'SPACINGTABLE'
    prl = None
    widths = []
    rows = []
    while i < len(stmt):
        tok = stmt[i]
        if tok == 'PARALLELRUNLENGTH':
            i += 1
            prl = []
            while i < len(stmt) and stmt[i] != 'WIDTH':
                prl.append(_num(stmt[i]))
                i += 1
        elif tok == 'WIDTH':
            i += 1
            if i >= len(stmt):
                break
            w = _num(stmt[i])
            i += 1
            row = []
            while (i < len(stmt) and stmt[i] != 'WIDTH'
                   and stmt[i] != 'PARALLELRUNLENGTH'):
                row.append(_num(stmt[i]))
                i += 1
            widths.append(w)
            rows.append(row)
        else:
            i += 1
    return {
        'parallel_run_length': prl,
        'width': widths,
        'spacing': rows,
    }


class LefRules(object):
    """Minimal LEF technology-file parser for routing/via rule summary."""

    def __init__(self, text):
        self.tokens = _tokenize(text)
        self.i = 0
        self.layers = {}    # ordered name -> layer info dict
        self.vias = []      # list of via dicts
        self.viarules = []  # list of viarule dicts

    # ------------------------------------------------------------------ #
    # low-level helpers
    # ------------------------------------------------------------------ #
    def _read_statement(self):
        """Collect tokens until (and consuming) the next ';'."""
        stmt = []
        while self.i < len(self.tokens):
            t = self.tokens[self.i]
            self.i += 1
            if t == ';':
                return stmt
            stmt.append(t)
        return stmt

    def _skip_block(self, end_name):
        while self.i < len(self.tokens):
            if (self.tokens[self.i] == 'END'
                    and self.i + 1 < len(self.tokens)
                    and self.tokens[self.i + 1] == end_name):
                self.i += 2
                return
            self.i += 1

    def _skip_statement(self):
        while self.i < len(self.tokens):
            if self.tokens[self.i] == ';':
                self.i += 1
                return
            self.i += 1

    # ------------------------------------------------------------------ #
    # top level
    # ------------------------------------------------------------------ #
    def parse(self):
        while self.i < len(self.tokens):
            t = self.tokens[self.i]
            if t == 'LAYER':
                self._parse_layer()
            elif t == 'VIA':
                self._parse_via()
            elif t == 'VIARULE':
                self._parse_viarule()
            elif t == 'SITE':
                if self.i + 1 < len(self.tokens):
                    self._skip_block(self.tokens[self.i + 1])
                else:
                    self.i += 1
            elif t == 'PROPERTYDEFINITIONS':
                self._skip_block('PROPERTYDEFINITIONS')
            elif t == 'UNITS':
                self._skip_block('UNITS')
            else:
                self._skip_statement()
        self._finalize_vias()
        return self

    # ------------------------------------------------------------------ #
    # LAYER
    # ------------------------------------------------------------------ #
    def _parse_layer(self):
        self.i += 1  # skip 'LAYER'
        if self.i >= len(self.tokens):
            return
        name = self.tokens[self.i]
        self.i += 1
        info = {
            'name': name,
            'type': None,
            'direction': None,
            'width': None,
            'pitch': [],
            'offset': [],
            'area': None,
            'max_width': None,
            'spacing': None,
            'adjacent_cuts_spacing': None,
            'spacing_table': None,
        }
        while self.i < len(self.tokens):
            if self.tokens[self.i] == 'END':
                self.i += 2
                break
            stmt = self._read_statement()
            if not stmt:
                continue
            key = stmt[0]
            args = stmt[1:]
            if key == 'TYPE':
                info['type'] = args[0] if args else None
            elif key == 'DIRECTION':
                info['direction'] = args[0] if args else None
            elif key == 'PITCH':
                info['pitch'] = [_num(a) for a in args]
            elif key == 'WIDTH':
                if args:
                    info['width'] = _num(args[0])
            elif key == 'OFFSET':
                info['offset'] = [_num(a) for a in args]
            elif key == 'AREA':
                if args:
                    info['area'] = _num(args[0])
            elif key == 'MAXWIDTH':
                if args:
                    info['max_width'] = _num(args[0])
            elif key == 'SPACINGTABLE':
                info['spacing_table'] = _parse_spacing_table(stmt)
            elif key == 'SPACING':
                if 'ADJACENTCUTS' in args:
                    info['adjacent_cuts_spacing'] = _num(args[0])
                elif info['spacing'] is None:
                    info['spacing'] = _num(args[0])
        self.layers[name] = info

# ------------------------------------------------------------------ #
    # VIA
    # ------------------------------------------------------------------ #
    def _parse_via(self):
        self.i += 1  # skip 'VIA'
        if self.i >= len(self.tokens):
            return
        name = self.tokens[self.i]
        self.i += 1
        via = {
            'name': name,
            'resistance': None,
            'layers': [],
            'rect_counts': {},
            'cuts': 0,
        }
        current = None
        while self.i < len(self.tokens):
            if self.tokens[self.i] == 'END':
                self.i += 2
                break
            if self.tokens[self.i] in ('DEFAULT', 'GENERATE'):
                self.i += 1
                continue
            stmt = self._read_statement()
            if not stmt:
                continue
            key = stmt[0]
            if key == 'RESISTANCE':
                if len(stmt) > 1:
                    via['resistance'] = _num(stmt[-1])
            elif key == 'LAYER':
                if len(stmt) > 1:
                    current = stmt[1]
                    via['layers'].append(current)
            elif key == 'RECT':
                if current is not None:
                    via['rect_counts'][current] = via['rect_counts'].get(current, 0) + 1
        self.vias.append(via)

    def _finalize_vias(self):
        """Count cuts = RECTs drawn on each via's CUT layer."""
        for via in self.vias:
            cuts = 0
            for lname in via['layers']:
                linfo = self.layers.get(lname)
                if linfo is not None and linfo.get('type') == 'CUT':
                    cuts += via['rect_counts'].get(lname, 0)
            via['cuts'] = cuts

    # ------------------------------------------------------------------ #
    # VIARULE
    # ------------------------------------------------------------------ #
    def _parse_viarule(self):
        self.i += 1  # skip 'VIARULE'
        if self.i >= len(self.tokens):
            return
        name = self.tokens[self.i]
        self.i += 1
        rule = {
            'name': name,
            'layers': [],
            'has_spacing': False,
            'enclosures': {},
            'width_range': {},
        }
        current = None
        while self.i < len(self.tokens):
            if self.tokens[self.i] == 'END':
                self.i += 2
                break
            if self.tokens[self.i] == 'GENERATE':
                self.i += 1
                continue
            stmt = self._read_statement()
            if not stmt:
                continue
            key = stmt[0]
            if key == 'LAYER':
                if len(stmt) > 1:
                    current = stmt[1]
                    rule['layers'].append(current)
            elif key == 'ENCLOSURE':
                if current is not None and len(stmt) >= 3:
                    rule['enclosures'][current] = [_num(stmt[1]), _num(stmt[2])]
            elif key == 'WIDTH':
                if current is not None and len(stmt) >= 4 and stmt[2] == 'TO':
                    rule['width_range'][current] = '{} TO {}'.format(stmt[1], stmt[3])
            elif key == 'SPACING':
                rule['has_spacing'] = True
        self.viarules.append(rule)

# ------------------------------------------------------------------ #
    # JSON assembly
    # ------------------------------------------------------------------ #
    def build(self):
        routing_layers = []
        cut_layers = []
        for info in self.layers.values():
            ltype = info.get('type')
            if ltype == 'ROUTING':
                routing_layers.append({
                    'name': info['name'],
                    'direction': info.get('direction'),
                    'width': info.get('width'),
                    'pitch': info.get('pitch') or [],
                    'max_width': info.get('max_width'),
                    'area': info.get('area'),
                    'offset': info.get('offset') or None,
                    'spacing_table': info.get('spacing_table'),
                })
            elif ltype == 'CUT':
                cut_layers.append({
                    'name': info['name'],
                    'spacing': info.get('spacing'),
                    'adjacent_cuts_spacing': info.get('adjacent_cuts_spacing'),
                })

        vias = [
            {
                'name': v['name'],
                'cuts': v['cuts'],
                'resistance': v['resistance'],
                'layers': v['layers'],
            }
            for v in self.vias
        ]

        viarules = [
            {
                'name': r['name'],
                'layers': r['layers'],
                'has_spacing': r['has_spacing'],
                'enclosures': r['enclosures'],
                'width_range': r['width_range'],
            }
            for r in self.viarules
        ]

        return {
            'routing_layers': routing_layers,
            'cut_layers': cut_layers,
            'vias': vias,
            'viarules': viarules,
        }


def main(argv):
    if len(argv) < 2:
        sys.stderr.write('Usage: lef_rules.py <techlef_path>\n')
        return 2
    path = argv[1]
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    summary = LefRules(text).parse().build()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))