#!/usr/bin/env python3
"""
lef_rules.py - Summarize routing / cut / via / viarule rules from a technology LEF.

Accepts a technology LEF file path as a command-line argument and prints a
structured JSON summary to stdout.

Usage:
    python3 lef_rules.py <techlef>

Top-level JSON schema:
    routing_layers : [ { name, direction, width, pitch[], max_width, area,
                         offset, spacing_table } ]
    cut_layers     : [ { name, spacing, adjacent_cuts_spacing } ]
    vias           : [ { name, cuts, resistance, layers[] } ]
    viarules       : [ { name, layers[], has_spacing, enclosures{}, width_range{} } ]
"""

import json
import re
import sys


def tokenize(text):
    """Strip '#' comments and split into whitespace tokens; keep ';' as a token."""
    text = re.sub(r"#.*", "", text)
    text = text.replace(";", " ; ")
    return text.split()


def read_floats(tokens, i):
    """Read a run of float tokens until (but not including) ';'."""
    vals = []
    while i < len(tokens) and tokens[i] != ";":
        vals.append(float(tokens[i]))
        i += 1
    return vals, i


def parse_spacing(tokens, i):
    """Parse a SPACING statement; ``i`` points at the first token after SPACING."""
    n = len(tokens)
    sp = {"value": float(tokens[i])}
    i += 1
    while i < n and tokens[i] != ";":
        kw = tokens[i]
        if kw == "LAYER":
            sp["layer"] = tokens[i + 1]
            i += 2
        elif kw == "ADJACENTCUTS":
            sp["adjacent_cuts"] = int(tokens[i + 1])
            i += 2
        elif kw == "WITHIN":
            sp["within"] = float(tokens[i + 1])
            i += 2
        elif kw == "RANGE":
            sp["range"] = [float(tokens[i + 1]), float(tokens[i + 2])]
            i += 3
        else:
            i += 1
    return sp, i


def parse_spacing_table(tokens, i):
    """Parse a SPACINGTABLE statement; ``i`` points at the first token after it."""
    n = len(tokens)
    table = {"parallel_run_length": [], "rows": []}
    while i < n and tokens[i] != ";":
        kw = tokens[i]
        if kw == "PARALLELRUNLENGTH":
            i += 1
            while i < n and tokens[i] != "WIDTH" and tokens[i] != ";":
                table["parallel_run_length"].append(float(tokens[i]))
                i += 1
        elif kw == "WIDTH":
            i += 1
            w = float(tokens[i])
            i += 1
            spacing = []
            while i < n and tokens[i] != "WIDTH" and tokens[i] != ";":
                spacing.append(float(tokens[i]))
                i += 1
            table["rows"].append({"width": w, "spacing": spacing})
        else:
            i += 1
    return table, i


def parse_layer(tokens, i):
    """Parse a LAYER block; ``i`` points at the layer name token."""
    n = len(tokens)
    name = tokens[i]
    i += 1
    layer = {"name": name}
    while i < n and tokens[i] != "END":
        tok = tokens[i]
        i += 1
        if tok == ";":
            continue
        if tok == "TYPE":
            layer["type"] = tokens[i]
            i += 1
        elif tok == "DIRECTION":
            layer["direction"] = tokens[i]
            i += 1
        elif tok == "WIDTH":
            layer["width"] = float(tokens[i])
            i += 1
        elif tok == "PITCH":
            layer["pitch"], i = read_floats(tokens, i)
        elif tok == "OFFSET":
            layer["offset"], i = read_floats(tokens, i)
        elif tok == "AREA":
            layer["area"] = float(tokens[i])
            i += 1
        elif tok == "MAXWIDTH":
            layer["max_width"] = float(tokens[i])
            i += 1
        elif tok == "SPACINGTABLE":
            layer["spacing_table"], i = parse_spacing_table(tokens, i)
        elif tok == "SPACING":
            sp, i = parse_spacing(tokens, i)
            layer.setdefault("spacings", []).append(sp)
        else:
            while i < n and tokens[i] != ";":
                i += 1
    if i < n and tokens[i] == "END":
        i += 1
    if i < n and tokens[i] == name:
        i += 1
    return layer, i


def parse_via(tokens, i):
    """Parse a VIA block; ``i`` points at the via name token."""
    n = len(tokens)
    name = tokens[i]
    i += 1
    via = {"name": name, "layers": [], "resistance": None}
    rects_by_layer = {}
    while i < n and tokens[i] != "END":
        tok = tokens[i]
        i += 1
        if tok in (";", "DEFAULT"):
            continue
        if tok == "RESISTANCE":
            via["resistance"] = float(tokens[i])
            i += 1
        elif tok == "LAYER":
            lname = tokens[i]
            i += 1
            via["layers"].append(lname)
            rects = []
            while i < n and tokens[i] != "LAYER" and tokens[i] != "END":
                t = tokens[i]
                if t == "RECT":
                    i += 1
                    rects.append([float(tokens[i]), float(tokens[i + 1]),
                                  float(tokens[i + 2]), float(tokens[i + 3])])
                    i += 4
                else:
                    i += 1
            rects_by_layer[lname] = rects
    if i < n and tokens[i] == "END":
        i += 1
    if i < n and tokens[i] == name:
        i += 1
    via["_rects"] = rects_by_layer
    return via, i
def parse_viarule(tokens, i):
    """Parse a VIARULE block; ``i`` points at the viarule name token."""
    n = len(tokens)
    name = tokens[i]
    i += 1
    vr = {"name": name, "layers": [], "has_spacing": False,
          "enclosures": {}, "width_range": {}}
    while i < n and tokens[i] != "END":
        tok = tokens[i]
        i += 1
        if tok in (";", "GENERATE"):
            continue
        if tok == "LAYER":
            lname = tokens[i]
            i += 1
            vr["layers"].append(lname)
            while i < n and tokens[i] != "LAYER" and tokens[i] != "END":
                t = tokens[i]
                if t == ";":
                    i += 1
                elif t == "ENCLOSURE":
                    i += 1
                    vr["enclosures"][lname] = [float(tokens[i]), float(tokens[i + 1])]
                    i += 2
                elif t == "WIDTH":
                    i += 1
                    wmin = float(tokens[i])
                    i += 1
                    if i < n and tokens[i] == "TO":
                        i += 1
                        wmax = float(tokens[i])
                        i += 1
                    else:
                        wmax = wmin
                    vr["width_range"][lname] = {"min": wmin, "max": wmax}
                elif t == "RECT":
                    i += 1
                    i += 4
                elif t == "SPACING":
                    i += 1
                    sx = float(tokens[i])
                    i += 1
                    if i < n and tokens[i] == "BY":
                        i += 1
                        sy = float(tokens[i])
                        i += 1
                    else:
                        sy = sx
                    vr["has_spacing"] = True
                else:
                    i += 1
    if i < n and tokens[i] == "END":
        i += 1
    if i < n and tokens[i] == name:
        i += 1
    return vr, i


def build_spacing_table(layer):
    """Return a normalized spacing_table value for a routing layer."""
    if "spacing_table" in layer:
        return layer["spacing_table"]
    spacings = layer.get("spacings", [])
    if spacings:
        return {"spacing": spacings[0]["value"]}
    return None
def parse_lef(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    tokens = tokenize(text)
    n = len(tokens)
    i = 0

    layers = {}
    vias = []
    viarules = []

    while i < n:
        tok = tokens[i]
        if tok == "LAYER":
            layer, i = parse_layer(tokens, i + 1)
            layers[layer["name"]] = layer
        elif tok == "VIA":
            via, i = parse_via(tokens, i + 1)
            vias.append(via)
        elif tok == "VIARULE":
            vr, i = parse_viarule(tokens, i + 1)
            viarules.append(vr)
        elif tok == "PROPERTYDEFINITIONS":
            while i < n and not (tokens[i] == "END"
                                 and i + 1 < n
                                 and tokens[i + 1] == "PROPERTYDEFINITIONS"):
                i += 1
            i += 2
        else:
            i += 1

    cut_layer_names = {name for name, l in layers.items() if l.get("type") == "CUT"}

    routing_layers = []
    for name, l in layers.items():
        if l.get("type") != "ROUTING":
            continue
        routing_layers.append({
            "name": name,
            "direction": l.get("direction"),
            "width": l.get("width"),
            "pitch": l.get("pitch"),
            "max_width": l.get("max_width"),
            "area": l.get("area"),
            "offset": l.get("offset"),
            "spacing_table": build_spacing_table(l),
        })

    cut_entries = []
    for name, l in layers.items():
        if l.get("type") != "CUT":
            continue
        spacing = None
        adjacent = None
        for sp in l.get("spacings", []):
            if "adjacent_cuts" in sp:
                adjacent = {
                    "spacing": sp["value"],
                    "adjacent_cuts": sp["adjacent_cuts"],
                    "within": sp.get("within"),
                }
            elif spacing is None:
                spacing = sp["value"]
        cut_entries.append({
            "name": name,
            "spacing": spacing,
            "adjacent_cuts_spacing": adjacent,
        })

    via_entries = []
    for v in vias:
        cuts = 0
        for lname, rects in v.get("_rects", {}).items():
            if lname in cut_layer_names:
                cuts += len(rects)
        via_entries.append({
            "name": v["name"],
            "cuts": cuts,
            "resistance": v["resistance"],
            "layers": v["layers"],
        })

    return {
        "routing_layers": routing_layers,
        "cut_layers": cut_entries,
        "vias": via_entries,
        "viarules": viarules,
    }


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 lef_rules.py <techlef>", file=sys.stderr)
        return 2
    result = parse_lef(argv[1])
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))