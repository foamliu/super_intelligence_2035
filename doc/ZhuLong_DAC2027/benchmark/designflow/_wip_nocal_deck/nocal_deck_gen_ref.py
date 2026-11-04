#!/usr/bin/env python3
"""
nocal_deck_gen.py -- Comparator offset testbench: calibration -> no-calibration
control-run deck generator.

Sub-skill (faithful to trace xq6n1, yanghao): given a calibration offset-measurement
testbench (cal_only.sp) where init/switch/DFF-clock control signals drive a successive-
approximation calibration sequence, emit a CONTROL (no-calibration) testbench
(nocal_only.sp) that measures the RAW comparator offset:
  * init  -> constant vdd  (reset never released -> calibration never starts)
  * clk   -> constant 0    (DFF never clocked)
  * en    -> constant 0    (cal cap switch always open -> cap disconnected)
The comparator netlist, input ramp, supplies, .measure offset statement and analysis
are preserved verbatim from the input deck.

CLI:  nocal_deck_gen.py <cal_only.sp> <spec.json> <out_dir>
spec.json maps the control-signal vsource/net names + const values (name-agnostic).
"""
import sys, os, re, json

def _parse_vsource(line):
    # "Vxxx  net  0  pulse(...)"  or  "Vxxx  net  0  pwl(...)"  or "Vxxx net 0 1.2"
    m = re.match(r'^(\S+)\s+(\S+)\s+(\S+)\s+(.+)$', line.strip())
    if not m:
        return None
    return {"vname": m.group(1), "net": m.group(2), "ref": m.group(3), "rest": m.group(4)}

def rewrite_deck(cal_text, spec):
    cs = spec["control_signals"]
    # build net -> (vsource, const_value) map; const_value may be a param name
    targets = {}
    for key in ("init", "clk", "en"):
        c = cs[key]
        val = c.get("const_value", 0)
        # if const_value_param given, prefer the param token (keeps deck parametric)
        if c.get("const_value_param"):
            val = c["const_value_param"]
        targets[c["net"]] = (c["vsource"], val)
    out_lines = []
    rewritten = set()
    for raw in cal_text.splitlines():
        line = raw
        # only rewrite independent voltage sources (lines starting with V)
        st = raw.strip()
        if st.startswith("V"):
            vs = _parse_vsource(raw)
            if vs and vs["net"] in targets and vs["ref"] == "0":
                want_vname, val = targets[vs["net"]]
                # name-agnostic: match by NET, not by vsource literal; keep original vname
                new_line = "%-6s %-10s 0  %s" % (vs["vname"], vs["net"], val)
                line = new_line
                rewritten.add(vs["net"])
        out_lines.append(line)
    # guard: all three control nets must have been rewritten
    missing = set(targets.keys()) - rewritten
    if missing:
        raise RuntimeError("control signal net(s) not found in deck: %s" % ",".join(sorted(missing)))
    return "\n".join(out_lines) + "\n"

def main():
    if len(sys.argv) != 4:
        print("usage: nocal_deck_gen.py <cal_only.sp> <spec.json> <out_dir>", file=sys.stderr)
        return 2
    cal_path, spec_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(cal_path) as f:
        cal_text = f.read()
    with open(spec_path) as f:
        spec = json.load(f)
    nocal_text = rewrite_deck(cal_text, spec)
    os.makedirs(out_dir, exist_ok=True)
    out_deck = os.path.join(out_dir, "nocal_only.sp")
    with open(out_deck, "w") as f:
        f.write(nocal_text)
    # manifest for downstream/judge
    manifest = {
        "deck_path": out_deck,
        "rewrote_control_signals": sorted(spec["control_signals"].keys()),
        "dut_subckt": spec.get("dut_subckt"),
        "measure_names": spec.get("measure_names", []),
    }
    with open(os.path.join(out_dir, "nocal_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("wrote %s" % out_deck)
    return 0

if __name__ == "__main__":
    sys.exit(main())
