#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCell TCL Flow Generator (generic).

Reads a JSON process specification (``spec.json``) and the eight skeleton ``.tcl``
templates, then writes a complete, internally-consistent AutoCell standard-cell
TCL flow into the target output directory:

    run.tcl  layers.tcl  layer_functions.tcl  viadefs.tcl
    globals.tcl  rules.tcl  place.tcl  route.tcl

The generated flow follows the documented pipeline contract:

  * sourcing order : layers, layer_functions, viadefs, globals, rules, place, route
  * ``tech -process`` lives in ``layers.tcl`` (never in ``run.tcl``)
  * via *definitions* live in ``viadefs.tcl``; via *instances* (``via .. -viadef ..``)
    live in ``route.tcl``
  * exactly one placement mode (auto => ``set_placer``, replay => ``read_placement``)
  * predictable GDS output path via ``[file join $case_dir ...]``
  * explicit router contract (``grid_map``, ``pin_template``, ``pin_grid``,
    ``vdd_connector``, ``vss_connector``)

Usage:
    python3 generate_autocell_flow.py --spec <spec.json> --skeleton <dir> --out <dir>
"""

import argparse
import json
import os
import re
import sys

SOURCE_ORDER = [
    "layers.tcl",
    "layer_functions.tcl",
    "viadefs.tcl",
    "globals.tcl",
    "rules.tcl",
    "place.tcl",
    "route.tcl",
]

EIGHT_FILES = ["run.tcl"] + SOURCE_ORDER

PLACEHOLDER_RE = re.compile(
    r"\{\{\s*(?P<k>[A-Za-z0-9_.\-]+)\s*\}\}"
    r"|@(?P<a>[A-Za-z0-9_.\-]+)@"
    r"|<<\s*(?P<l>[A-Za-z0-9_.\-]+)\s*>>"
    r"|%%(?P<p>[A-Za-z0-9_.\-]+)%%"
    r"|\$\{(?P<d>[A-Za-z0-9_.\-]+)\}"
    r"|###(?P<h>[A-Za-z0-9_.\-]+)###"
)

RESIDUE_RE = re.compile(
    r"TODO|TBD|FIXME|PLACEHOLDER"
    r"|\{\{\s*[A-Za-z0-9_.\-]+\s*\}\}"
    r"|@[A-Za-z0-9_.\-]+@"
    r"|<<\s*[A-Za-z0-9_.\-]+\s*>>"
    r"|%%[A-Za-z0-9_.\-]+%%"
    r"|\$\{[A-Za-z0-9_.\-]+\}"
    r"|###[A-Za-z0-9_.\-]+###"
)


class FlowError(Exception):
    pass
# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _num(v):
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return repr(v)
    if isinstance(v, str):
        return v.strip()
    return str(v)


def _q(s):
    s = str(s).replace("\\", "\\\\").replace('"', '\\"')
    return '"%s"' % s


def _numlist(values):
    return "{ %s }" % " ".join(_num(v) for v in values)


def _wordlist(values):
    return "{ %s }" % " ".join(str(v) for v in values)


def _qlist(values):
    return "{ %s }" % " ".join(_q(v) for v in values)


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _as_str_list(value):
    out = []
    for it in _as_list(value):
        if isinstance(it, str):
            out.extend([t for t in it.split() if t])
        else:
            out.append(str(it))
    return out
# ---------------------------------------------------------------------------
# JSON / IO
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_text(path, content):
    content = content.replace("\r\n", "\n").rstrip() + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _pick(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return d[k]
    return default
# ---------------------------------------------------------------------------
# Spec normalisation (tolerant to several JSON shapes for each field)
# ---------------------------------------------------------------------------

def _normalize_gds_mapping(raw):
    out = {}
    if isinstance(raw, dict):
        for name, pair in raw.items():
            if isinstance(pair, dict):
                pair = [_pick(pair, "layer", "gds_layer", default=0),
                        _pick(pair, "datatype", "data_type", "gds_datatype", default=0)]
            out[str(name)] = [_num(pair[0]), _num(pair[1])]
    elif isinstance(raw, list):
        for rec in raw:
            if not isinstance(rec, dict):
                continue
            name = _pick(rec, "name", "layer", default=None)
            if name is None:
                continue
            gds = _pick(rec, "gds", default=None)
            if isinstance(gds, (list, tuple)) and len(gds) >= 2:
                pair = [gds[0], gds[1]]
            else:
                pair = [_pick(rec, "layer_num", "gds_layer", default=0),
                        _pick(rec, "datatype", "data_type", "gds_datatype", default=0)]
            out[str(name)] = [_num(pair[0]), _num(pair[1])]
    return out


def _normalize_layer_functions(raw):
    out = {}
    if isinstance(raw, dict):
        for layer, fns in raw.items():
            out[str(layer)] = _as_str_list(fns)
    elif isinstance(raw, list):
        for rec in raw:
            if not isinstance(rec, dict):
                continue
            layer = _pick(rec, "layer", "name", default=None)
            if layer is None:
                continue
            out[str(layer)] = _as_str_list(_pick(rec, "functions", "roles", default=[]))
    return out
def _normalize_vias(raw):
    out = []
    if isinstance(raw, dict):
        for name, rec in raw.items():
            rec = dict(rec) if isinstance(rec, dict) else {}
            rec.setdefault("name", name)
            out.append(rec)
    elif isinstance(raw, list):
        out = [dict(r) for r in raw if isinstance(r, dict)]
    for v in out:
        v["name"] = str(_pick(v, "name", default="VIA"))
        v["cut_layer"] = str(_pick(v, "cut_layer", "cut", default="CONT"))
        v["layer1"] = str(_pick(v, "layer1", "bottom", "lower", default=""))
        v["layer2"] = str(_pick(v, "layer2", "top", "upper", default=""))
        v["cut_rowcol"] = _as_list(_pick(v, "cut_rowcol", default=[1, 1]))
        v["cut_size"] = _as_list(_pick(v, "cut_size", default=[0.1, 0.1]))
        v["cut_space"] = _as_list(_pick(v, "cut_space", default=[0.1, 0.1]))
        v["layer1_enc"] = _as_list(_pick(v, "layer1_enc", default=[0.05, 0.05]))
        v["layer2_enc"] = _as_list(_pick(v, "layer2_enc", default=[0.05, 0.05]))
    return out


def _normalize_global_nets(raw):
    nets = raw if isinstance(raw, dict) else {}
    return {
        "vdd": _as_str_list(_pick(nets, "vdd", "power", default=["VDD"])),
        "vss": _as_str_list(_pick(nets, "vss", "ground", default=["VSS"])),
        "vpw": _as_str_list(_pick(nets, "vpw", "pwell", default=[])),
        "vnw": _as_str_list(_pick(nets, "vnw", "nwell", default=[])),
    }


def _normalize_rules(raw):
    out = []
    for rec in _as_list(raw):
        if not isinstance(rec, dict):
            continue
        rec = dict(rec)
        rule = {
            "type": str(_pick(rec, "type", "rule", default="min_width")),
            "value": _num(_pick(rec, "value", "space", default="")),
        }
        layers = _pick(rec, "layers", default=None)
        layer = _pick(rec, "layer", default=None)
        if layers is not None:
            rule["layers"] = _as_str_list(layers)
        elif layer is not None:
            rule["layer"] = str(layer)
        extra = {}
        for ek, ev in rec.items():
            if ek in ("type", "rule", "value", "space", "layer", "layers"):
                continue
            extra[ek] = ev
        if extra:
            rule["extra"] = extra
        out.append(rule)
    return out
def _normalize_device_classes(raw, netlist, process):
    classes = [dict(r) for r in _as_list(raw) if isinstance(r, dict)]
    if classes:
        return classes
    pmos = _as_str_list(_pick(netlist, "pmos_set", "pmos_classes", default=["pch"]))
    nmos = _as_str_list(_pick(netlist, "nmos_set", "nmos_classes", default=["nch"]))
    for name in nmos:
        if process == "finfet":
            classes.append({"name": name, "type": "nmos", "model": name,
                            "channel_length": 0.011, "poly_extension": 0.032,
                            "active_extension": 0.057, "fin_width": 0.0065, "nfin": 2})
        else:
            classes.append({"name": name, "type": "nmos", "model": name,
                            "channel_length": 0.135, "channel_width": 1.875,
                            "poly_extension_bottom": 0.35, "poly_extension_top": 0.35,
                            "active_extension": 0.33})
    for name in pmos:
        if process == "finfet":
            classes.append({"name": name, "type": "pmos", "model": name,
                            "channel_length": 0.011, "poly_extension": 0.032,
                            "active_extension": 0.057, "fin_width": 0.0065, "nfin": 2})
        else:
            classes.append({"name": name, "type": "pmos", "model": name,
                            "channel_length": 0.135, "channel_width": 1.875,
                            "poly_extension_bottom": 0.35, "poly_extension_top": 0.35,
                            "active_extension": 0.33})
    return classes
def normalize_spec(raw):
    """Return a canonical spec dictionary with every field resolved."""
    if not isinstance(raw, dict):
        raise FlowError("spec JSON must be an object")

    process = str(_pick(raw, "process", "process_type", default="planar")).strip().lower()
    if process not in ("planar", "finfet"):
        raise FlowError("unknown process %r (expected planar or finfet)" % (process,))

    design_name = str(_pick(raw, "design_name", "name", "design", default="autocell"))

    placement_raw = _pick(raw, "placement", "place", default={}) or {}
    routing_raw = _pick(raw, "routing", "route", default={}) or {}
    netlist_raw = _pick(raw, "netlist", default={}) or {}
    output_raw = _pick(raw, "output", "outputs", default={}) or {}

    netlist = {
        "mode": str(_pick(netlist_raw, "mode", "input", default="schematic")).lower(),
        "file": _pick(netlist_raw, "file", "netlist", "path", default="netlist.cdl"),
        "pmos_set": _as_str_list(_pick(netlist_raw, "pmos_set", "pmos_classes", default=["pch"])),
        "nmos_set": _as_str_list(_pick(netlist_raw, "nmos_set", "nmos_classes", default=["nch"])),
    }

    device_classes = _normalize_device_classes(
        _pick(placement_raw, "device_classes", "devices", default=[]),
        netlist, process)

    # Router contract: fully derived from the spec with consistent defaults.
    grid_map = _pick(routing_raw, "grid_map", "gridmap", default={})
    if isinstance(grid_map, dict):
        grid_map = {str(k): str(v) for k, v in grid_map.items()}
    else:
        grid_map = {}

    grids = _as_list(_pick(routing_raw, "grids", default=[]))
    pin_template = str(_pick(routing_raw, "pin_template", default="pin_template"))
    pin_layer = str(_pick(routing_raw, "pin_layer", default="M0"))
    pin_grid = str(_pick(routing_raw, "pin_grid", default="pin"))
    vdd_connector = str(_pick(routing_raw, "vdd_connector", default="vdd_pgc"))
    vss_connector = str(_pick(routing_raw, "vss_connector", default="vss_pgc"))

    cell_list = []
    for rec in _as_list(_pick(raw, "cell_list", "cells", default=[])):
        if not isinstance(rec, dict):
            continue
        cell_list.append({
            "name": str(_pick(rec, "name", "cell", default="cell")),
            "netlist": _pick(rec, "netlist", "schematic", default=None),
            "rows": _pick(rec, "rows", "row", default=1),
            "placement": _pick(rec, "placement", default=None),
        })

    spec = {
        "process": process,
        "design_name": design_name,
        "gds_mapping": _normalize_gds_mapping(_pick(raw, "gds_mapping", "layers", default={})),
        "layer_functions": _normalize_layer_functions(
            _pick(raw, "layer_functions", "layer_roles", default={})),
        "via_definitions": _normalize_vias(_pick(raw, "via_definitions", "vias", "viadefs", default=[])),
        "global_nets": _normalize_global_nets(_pick(raw, "global_nets", "pg_nets", default={})),
        "design_rules": _normalize_rules(_pick(raw, "design_rules", "rules", "drc", default=[])),
        "placement": {
            "mode": str(_pick(placement_raw, "mode", "placement_mode", default="auto")).lower(),
            "device_classes": device_classes,
            "boundary": _pick(placement_raw, "boundary", default={}) or {},
            "connections": _as_list(_pick(placement_raw, "connections", "connectors", default=[])),
            "templates": _as_list(_pick(placement_raw, "templates", default=[])),
            "options": _pick(placement_raw, "options", default={}) or {},
        },
        "routing": {
            "pin_template": pin_template,
            "pin_layer": pin_layer,
            "pin_grid": pin_grid,
            "vdd_connector": vdd_connector,
            "vss_connector": vss_connector,
            "grid_map": grid_map,
            "grids": grids,
            "options": _pick(routing_raw, "options", default={}) or {},
        },
        "netlist": netlist,
        "cell_list": cell_list,
        "output": {
            "gds_path": _pick(output_raw, "gds_path", "gds", "path",
                              default="%s.gds" % design_name),
        },
        "options": _pick(raw, "options", "flow_options", default={}) or {},
    }

    if spec["netlist"]["mode"] not in ("schematic", "read_netlist", "readnetlist"):
        spec["netlist"]["mode"] = "schematic"
    if not spec["cell_list"]:
        spec["cell_list"] = [{"name": "cell0", "netlist": None, "rows": 1, "placement": None}]
    return spec
# ---------------------------------------------------------------------------
# Technology-file generators
# ---------------------------------------------------------------------------

def _header(title):
    return "\n".join([
        "# " + "-" * 75,
        "#   %s" % title,
        "#   Auto-generated by generate_autocell_flow.py",
        "# " + "-" * 75,
    ]) + "\n\n"


def gen_layers(spec):
    lines = [_header("layers.tcl - technology object + CAD layer definitions")]
    lines.append("tech -process %s\n" % spec["process"])
    for name in sorted(spec["gds_mapping"]):
        layer_no, datatype = spec["gds_mapping"][name]
        lines.append("tech add_layer -name %s -gds %s" % (_q(name), _numlist([layer_no, datatype])))
    return "\n".join(lines)


def gen_layer_functions(spec):
    lines = [_header("layer_functions.tcl - layer role documentation")]
    for name in sorted(spec["layer_functions"]):
        fns = spec["layer_functions"][name]
        if not fns:
            continue
        lines.append("tech set_layer_function -layer %s -functions %s" % (_q(name), _qlist(fns)))
    return "\n".join(lines)


def gen_viadefs(spec):
    lines = [_header("viadefs.tcl - via / contact stack definitions (add_viadef)")]
    for v in spec["via_definitions"]:
        parts = ["tech add_viadef",
                 "-name %s" % _q(v["name"]),
                 "-cut_layer %s" % _q(v["cut_layer"]),
                 "-layer1 %s" % _q(v["layer1"]),
                 "-layer2 %s" % _q(v["layer2"]),
                 "-cut_rowcol %s" % _numlist(v["cut_rowcol"]),
                 "-cut_size %s" % _numlist(v["cut_size"]),
                 "-cut_space %s" % _numlist(v["cut_space"]),
                 "-layer1_enc %s" % _numlist(v["layer1_enc"]),
                 "-layer2_enc %s" % _numlist(v["layer2_enc"])]
        lines.append(" ".join(parts))
    return "\n".join(lines)


def gen_globals(spec):
    lines = [_header("globals.tcl - global power / ground / body net naming")]
    nets = spec["global_nets"]
    for key in ("vdd", "vss", "vpw", "vnw"):
        if nets.get(key):
            lines.append("tech set_global_net -%s %s" % (key, _wordlist(nets[key])))
    return "\n".join(lines)


def gen_rules(spec):
    lines = [_header("rules.tcl - design rules (add_rule)")]
    for r in spec["design_rules"]:
        parts = ["tech add_rule", "-type %s" % r["type"]]
        if "layers" in r:
            parts.append("-layer %s" % _qlist(r["layers"]))
        elif "layer" in r:
            parts.append("-layer %s" % _q(r["layer"]))
        parts.append("-value %s" % _num(r["value"]))
        for ek, ev in r.get("extra", {}).items():
            if isinstance(ev, bool):
                parts.append("-%s %s" % (ek, "1" if ev else "0"))
            elif isinstance(ev, (list, tuple)):
                parts.append("-%s %s" % (ek, _numlist(ev)))
            elif isinstance(ev, (int, float)):
                parts.append("-%s %s" % (ek, _num(ev)))
            else:
                parts.append("-%s %s" % (ek, _q(ev)))
        lines.append(" ".join(parts))
    return "\n".join(lines)
def _device_class_names(spec, dtype):
    return [str(dc.get("name")) for dc in spec["placement"]["device_classes"]
            if str(dc.get("type", "")).lower() == dtype]


def _boundary_name(spec):
    b = spec["placement"]["boundary"]
    return str(_pick(b, "name", "boundary_name", default="boundary"))


def _dummy_name(spec):
    b = spec["placement"]["boundary"]
    return str(_pick(b, "dummy", "dummy_template", default="dummy_template"))


def _row_height(spec):
    b = spec["placement"]["boundary"]
    h = _pick(b, "height", "row_height", default=None)
    if h is not None:
        return float(h)
    return 0.24 if spec["process"] == "finfet" else 12.5


def gen_place(spec):
    p = spec["placement"]
    process = spec["process"]
    height = _row_height(spec)
    lines = [_header("place.tcl - PG connectors, boundary, device classes, placer templates")]

    for dc in p["device_classes"]:
        name = str(_pick(dc, "name", default="dev"))
        dtype = str(_pick(dc, "type", "polarity", default="nmos"))
        model = str(_pick(dc, "model", "model_name", default=name))
        if process == "finfet":
            parts = ["device_class", name, "-type", dtype, "-model", model]
            for k in ("channel_length", "poly_extension", "active_extension",
                      "fin_width", "nfin"):
                if k in dc:
                    parts += ["-%s" % k, _num(dc[k])]
            lines.append(" ".join(parts))
            for fd in _as_list(_pick(dc, "fin_definitions", "fin_definition", default=[])):
                if isinstance(fd, dict):
                    lines.append("device_class %s add_fin_definition -nfin %s -active_width %s"
                                 % (name, _num(fd.get("nfin", 2)),
                                    _num(fd.get("active_width", 0.038))))
        else:
            parts = ["device_class", name, "-type", dtype]
            for k in ("channel_length", "channel_width", "poly_extension_bottom",
                      "poly_extension_top", "active_extension"):
                if k in dc:
                    parts += ["-%s" % k, _num(dc[k])]
            parts += ["-model", model]
            lines.append(" ".join(parts))

    # PG connectors (referenced by run.tcl as vdd_connector / vss_connector).
    conns = [c for c in p["connections"] if isinstance(c, dict)]
    have = {str(c.get("name")) for c in conns}
    vss = spec["routing"]["vss_connector"]
    vdd = spec["routing"]["vdd_connector"]
    if vss and vss not in have:
        conns = [{"name": vss, "type": "ground"}] + conns
    if vdd and vdd not in have:
        conns = conns + [{"name": vdd, "type": "power"}]
    for c in conns:
        name = str(_pick(c, "name", default="pgc"))
        ctype = str(_pick(c, "type", "net_type", default="power"))
        extra = ""
        if "height" in c:
            extra += " -height %s" % _num(c["height"])
        lines.append("connection %s -type %s%s" % (name, ctype, extra))

    # Matched / dummy placement templates (referenced by set_placer in run.tcl).
    nmos = _device_class_names(spec, "nmos")
    pmos = _device_class_names(spec, "pmos")
    if not nmos and not pmos:
        nmos, pmos = ["nch"], ["pch"]
    lines.append("")
    lines.append("template matched_template -type normal -height %s -unit_width 0.5 -priority 0"
                 % _num(height))
    for n in nmos:
        lines.append("template matched_template append_device -name %s "
                     "-point [dict create offset_x 0 offset_y 0 mag_x 1 mag_y 0] "
                     "-reference_point [dict create offset_x 0 offset_y 0 mag_x 1 mag_y 1]" % n)
    for n in pmos:
        lines.append("template matched_template append_device -name %s "
                     "-point [dict create offset_x 0 offset_y %s mag_x 1 mag_y 0] "
                     "-reference_point [dict create offset_x 0 offset_y 0 mag_x 1 mag_y 0]"
                     % (n, _num(height / 2)))
    lines.append("template %s -type dummy -height %s -unit_width 0.65"
                 % (_dummy_name(spec), _num(height)))

    # Cell boundary.
    b = p["boundary"]
    spacing = _pick(b, "spacing", default=0.5)
    left = _pick(b, "left_ext", "left_extension", default=0.5)
    right = _pick(b, "right_ext", "right_extension", default=0.5)
    lines.append("")
    lines.append("boundary %s -height %s -spacing %s -left_ext %s -right_ext %s"
                 % (_boundary_name(spec), _num(height), _num(spacing),
                    _num(left), _num(right)))
    return "\n".join(lines)
def gen_route(spec):
    r = spec["routing"]
    lines = [_header("route.tcl - via instances, signal-pin template, routing grids")]

    # Via instances (references to the viadefs declared in viadefs.tcl).
    for v in spec["via_definitions"]:
        lines.append("via %s -viadef %s -tech default_tech"
                     % (_q(v["name"]), _q(v["name"])))

    # Signal-pin template (referenced by run.tcl as -pin_template).
    lines.append("pin %s -layer %s" % (r["pin_template"], _q(r["pin_layer"])))

    # Routing grids: every value in grid_map plus the pin grid must be defined.
    grid_objs = {}
    for g in r["grids"]:
        if isinstance(g, dict):
            grid_objs[str(_pick(g, "name", default="grid"))] = g
        elif isinstance(g, str):
            grid_objs[g] = {}
    ordered = []
    for n in list(r["grid_map"].values()) + [r["pin_grid"]]:
        if n and n not in ordered:
            ordered.append(n)
    for n in ordered:
        g = grid_objs.get(n, {})
        cost = _pick(g, "cost", default=None)
        suffix = " -cost %s" % _num(cost) if cost is not None else ""
        lines.append("grid %s%s" % (n, suffix))
    return "\n".join(lines)


def gen_run(spec):
    n = spec["netlist"]
    r = spec["routing"]
    pl = spec["placement"]
    lines = [_header("run.tcl - top-level flow entry")]

    lines.append("# Case directory - location of this flow (all paths are relative to it).")
    lines.append("set case_dir [file dirname [file nativename $tcl_script_path]]")
    lines.append("set tech_home ${case_dir}")
    lines.append("")

    for k, v in spec["options"].items():
        if isinstance(v, bool):
            v = 1 if v else 0
        lines.append("option %s %s" % (k, _num(v)))

    lines.append("")
    lines.append("# ---- source the split technology files (fixed order) ----")
    for f in SOURCE_ORDER:
        lines.append('source [file join $case_dir "%s"]' % f)

    cells = [c["name"] for c in spec["cell_list"]]
    lines.append("")
    lines.append("set simple_cells [list %s]" % " ".join(cells))

    pmos_set = _wordlist(n["pmos_set"])
    nmos_set = _wordlist(n["nmos_set"])

    lines.append("")
    if n["mode"] in ("read_netlist", "readnetlist"):
        lines.append("read_netlist -cells $simple_cells \\")
        lines.append("    -pmos_set %s \\" % pmos_set)
        lines.append("    -nmos_set %s \\" % nmos_set)
        lines.append('    -file "${tech_home}/%s"' % n["file"])
        per_cell_schematic = False
    else:
        per_cell_schematic = True

    lines.append("")
    lines.append("foreach cell_name $simple_cells {")
    if per_cell_schematic:
        lines.append("    schematic $cell_name \\")
        lines.append('        -spice_path "${tech_home}/cells/${cell_name}/schematic/sch.cdl" \\')
        lines.append("        -pmos_classes %s \\" % pmos_set)
        lines.append("        -nmos_classes %s" % nmos_set)
        lines.append("")

    # Device classes bound to the cell.
    dc_names = _wordlist([str(dc.get("name")) for dc in pl["device_classes"]])

    lines.append("    cell $cell_name -tech default_tech \\")
    lines.append("        -schematic $cell_name \\")
    lines.append("        -boundary %s \\" % _boundary_name(spec))
    lines.append("        -dummy %s \\" % _dummy_name(spec))
    lines.append("        -device_classes %s" % dc_names)
    lines.append("")

    # Exactly one placement mode.
    if pl["mode"] == "replay":
        lines.append("    cell $cell_name read_placement \\")
        lines.append('        -file "${tech_home}/cells/${cell_name}/layout/placement.json" \\')
        lines.append("        -type json -top_cell $cell_name")
    else:
        lines.append("    cell $cell_name set_placer -templates { matched_template %s }"
                     % _dummy_name(spec))
    lines.append("")

    # Router contract: grid_map, pin_template, pin_grid, vdd/vss connectors.
    gm = " ".join("%s %s" % (k, v) for k, v in r["grid_map"].items())
    lines.append("    cell $cell_name set_router \\")
    lines.append("        -grid_map [dict create %s] \\" % gm)
    lines.append("        -pin_template %s \\" % r["pin_template"])
    lines.append("        -pin_grid %s \\" % r["pin_grid"])
    lines.append("        -vss_connector %s \\" % r["vss_connector"])
    lines.append("        -vdd_connector %s" % r["vdd_connector"])
    lines.append("")
    lines.append("    cell $cell_name generate_layout")
    lines.append("}")
    lines.append("")

    gds = spec["output"]["gds_path"]
    if gds.startswith("$") or gds.startswith("[") or gds.startswith("/"):
        file_expr = gds
    else:
        file_expr = "[file join $case_dir %s]" % _q(gds)
    lines.append("set FileName %s" % file_expr)
    lines.append("write_layout -cells $simple_cells -type gds -file $FileName")
    return "\n".join(lines)
# ---------------------------------------------------------------------------
# Skeleton template rendering (optional baseline with placeholders)
# ---------------------------------------------------------------------------

def build_context(spec):
    ctx = {
        "process": spec["process"],
        "design_name": spec["design_name"],
        "pin_template": spec["routing"]["pin_template"],
        "pin_layer": spec["routing"]["pin_layer"],
        "pin_grid": spec["routing"]["pin_grid"],
        "vdd_connector": spec["routing"]["vdd_connector"],
        "vss_connector": spec["routing"]["vss_connector"],
        "boundary": _boundary_name(spec),
        "dummy_template": _dummy_name(spec),
        "netlist_mode": spec["netlist"]["mode"],
        "netlist_file": spec["netlist"]["file"],
        "output_gds": spec["output"]["gds_path"],
    }
    for name, pair in spec["gds_mapping"].items():
        ctx["layer." + name.lower() + ".gds"] = _numlist([pair[0], pair[1]])
        ctx["layer." + name.lower() + ".name"] = _q(name)
    return ctx


def has_placeholders(text):
    return PLACEHOLDER_RE.search(text) is not None


def render_template(text, ctx):
    def repl(m):
        for grp in ("k", "a", "l", "p", "d", "h"):
            key = m.group(grp)
            if key is not None:
                return str(ctx.get(key, m.group(0)))
        return m.group(0)
    return PLACEHOLDER_RE.sub(repl, text)


def has_residue(text):
    return RESIDUE_RE.search(text) is not None


# ---------------------------------------------------------------------------
# Report / manifest + main entry points
# ---------------------------------------------------------------------------

def gen_report(spec):
    return {
        "process": spec["process"],
        "design_name": spec["design_name"],
        "file_count": len(EIGHT_FILES),
        "files": EIGHT_FILES,
        "sourcing_order": SOURCE_ORDER,
        "placement_mode": spec["placement"]["mode"],
        "netlist_mode": spec["netlist"]["mode"],
        "layer_count": len(spec["gds_mapping"]),
        "via_count": len(spec["via_definitions"]),
        "device_class_count": len(spec["placement"]["device_classes"]),
        "cell_count": len(spec["cell_list"]),
        "generator": "generate_autocell_flow.py",
    }


_GENERATORS = {
    "run.tcl": gen_run,
    "layers.tcl": gen_layers,
    "layer_functions.tcl": gen_layer_functions,
    "viadefs.tcl": gen_viadefs,
    "globals.tcl": gen_globals,
    "rules.tcl": gen_rules,
    "place.tcl": gen_place,
    "route.tcl": gen_route,
}


def generate_flow(spec_path, skeleton_dir, out_dir):
    """Read the spec + skeleton and write the eight TCL files + report.json.

    Returns the report dict.
    """
    spec = normalize_spec(load_json(spec_path))
    os.makedirs(out_dir, exist_ok=True)
    ctx = build_context(spec)

    for name in EIGHT_FILES:
        skel_path = os.path.join(skeleton_dir, name) if skeleton_dir else None
        skel = read_text(skel_path)
        content = None
        if skel is not None and has_placeholders(skel):
            content = render_template(skel, ctx)
        if content is None or has_residue(content):
            # Fall back to fully spec-driven generation, guaranteeing a valid,
            # internally-consistent and placeholder-free flow.
            content = _GENERATORS[name](spec)
        write_text(os.path.join(out_dir, name), content)

    report = gen_report(spec)
    write_text(os.path.join(out_dir, "report.json"),
               json.dumps(report, indent=2) + "\n")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="AutoCell TCL flow generator")
    ap.add_argument("--spec", required=True, help="path to spec JSON")
    ap.add_argument("--skeleton", default=None, help="path to skeleton template dir")
    ap.add_argument("--out", required=True, help="output directory")
    args = ap.parse_args(argv)

    report = generate_flow(args.spec, args.skeleton, args.out)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())