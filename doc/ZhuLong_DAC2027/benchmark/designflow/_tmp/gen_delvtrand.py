#!/usr/bin/env python3
"""Generator for DelvtrandAnomalyScan-001 case assets."""
import json, os, re

CASE = "DelvtrandAnomalyScan-001"
BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
AST = BASE + "/assets/" + CASE
REF = BASE + "/reference/" + CASE
TMP = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_tmp"

PV = ["delvtrand_nsvt", "delvtrand_psvt", "delvtrand_pulvt", "delvtrand_nulvt"]
MODELS = {"nsvt": "nsvt_dbc", "psvt": "psvt_dbc", "pulvt": "pulvt_dbc", "nulvt": "nulvt_dbc"}

def mos(inst, n1, n2, n3, vt, w, l, dv):
    model = MODELS[vt]
    dtv = "dtemp_" + vt if dv in PV else "0"
    return "X%s %s %s %s %s w=%s l=%s delvtrand=%s dtemp=%s" % (inst, n1, n2, n3, model, w, l, dv, dtv)

def subckt(name, ports, lns):
    out = ["** Library name: synth_lib", "** Cell name: " + name, "** View name: schematic",
           ".subckt " + name + " " + " ".join(ports)]
    out.extend(lns)
    out.append(".ends " + name)
    out.append("** End of subcircuit definition.")
    out.append("")
    return out

# NETLIST A (visible)
lines_A = []
lines_A += subckt("INV_1X_A", ["I", "O", "VDD", "VSS"], [
    mos("NM0", "O", "I", "VSS", "nsvt", "119e-9", "6e-9", "delvtrand_nsvt"),
    mos("PM0", "O", "I", "VDD", "psvt", "119e-9", "6e-9", "delvtrand_psvt"),
])
lines_A += subckt("NAND_2X_A", ["A", "B", "O", "VDD", "VSS"], [
    mos("NM0", "net7", "B", "VSS", "nsvt", "119e-9", "6e-9", "delvtrand_nsvt"),
    mos("NM1", "net7", "A", "VSS", "nsvt", "119e-9", "6e-9", "delvtrand_nsvt"),
    mos("PM0", "O", "B", "VDD", "psvt", "119e-9", "6e-9", "delvtrand_psvt"),
    mos("PM1", "O", "A", "VDD", "psvt", "119e-9", "6e-9", "delvtrand_psvt"),
])
lines_A += subckt("TS_comp_A", ["EN", "NEG", "OUT", "POS", "VDD", "VSS"], [
    mos("NM0", "OUT", "ENB", "VSS", "nsvt", "200e-9", "20e-9", "delvtrand_nsvt"),
    mos("NM1", "INBIAS", "ENB", "VSS", "nsvt", "200e-9", "20e-9", "0"),
    mos("NM2", "VNB", "ENB", "VSS", "nsvt", "200e-9", "20e-9", "delvtrand_nsvt"),
    mos("PM0", "net58", "NEG", "VCM", "pulvt", "623e-9", "20e-9", "delvtrand_pulvt"),
    mos("PM1", "net12", "POS", "VCM", "pulvt", "623e-9", "20e-9", "delvtrand_pulvt"),
    mos("PM2", "VCM", "VPB", "VDD", "pulvt", "119e-9", "54e-9", "delvtrand_pulvt"),
    mos("PM3", "VPB", "ENE", "VDD", "psvt", "119e-9", "54e-9", "delvtrand_psvt"),
    mos("PM4", "OUT", "ENE", "VDD", "psvt", "119e-9", "54e-9", "100e-3"),
])
lines_A += subckt("TS_analog_A", ["CLK", "OUT", "VDD", "VSS"], [
    mos("M0", "OUT", "N2", "VSS", "nsvt", "300e-9", "6e-9", "delvtrand_nsvt"),
    mos("M1", "OUT", "N2", "VDD", "psvt", "300e-9", "6e-9", "delvtrand_psvt"),
    mos("M2", "OUT", "N2", "VDD", "psvt", "300e-9", "6e-9", "100e-3"),
    mos("M3", "N2", "N3", "VSS", "nulvt", "200e-9", "20e-9", "delvtrand_nulvt"),
    mos("M4", "N3", "N4", "VDD", "pulvt", "200e-9", "20e-9", "delvtrand_pulvt"),
    mos("M5", "N4", "CLK", "VSS", "nsvt", "200e-9", "20e-9", "delvtrand_nsvt"),
])
netlist_A = "\n".join(lines_A) + "\n"

# NETLIST B (hidden)
lines_B = []
lines_B += subckt("INV_2X_B", ["I", "O", "VDD", "VSS"], [
    mos("NM0", "O", "I", "VSS", "nsvt", "238e-9", "6e-9", "delvtrand_nsvt"),
    mos("PM0", "O", "I", "VDD", "psvt", "238e-9", "6e-9", "delvtrand_psvt"),
])
lines_B += subckt("NAND_3X_B", ["A", "B", "O", "VDD", "VSS"], [
    mos("NM0", "net9", "B", "VSS", "nsvt", "357e-9", "6e-9", "delvtrand_nsvt"),
    mos("NM1", "net9", "A", "VSS", "nsvt", "357e-9", "6e-9", "0"),
    mos("PM0", "O", "B", "VDD", "psvt", "357e-9", "6e-9", "delvtrand_psvt"),
    mos("PM1", "O", "A", "VDD", "psvt", "357e-9", "6e-9", "delvtrand_psvt"),
])
lines_B += subckt("TS_comp_B", ["EN", "NEG", "OUT", "POS", "VDD", "VSS"], [
    mos("NM0", "OUT", "ENB", "VSS", "nsvt", "200e-9", "20e-9", "delvtrand_nsvt"),
    mos("NM1", "INBIAS", "ENB", "VSS", "nsvt", "200e-9", "20e-9", "delvtrand_nsvt"),
    mos("NM2", "VNB", "ENB", "VSS", "nsvt", "200e-9", "20e-9", "delvtrand_nsvt"),
    mos("PM0", "net60", "NEG", "VCM", "pulvt", "623e-9", "20e-9", "delvtrand_pulvt"),
    mos("PM1", "net14", "POS", "VCM", "pulvt", "623e-9", "20e-9", "delvtrand_pulvt"),
    mos("PM2", "VCM", "VPB", "VDD", "pulvt", "119e-9", "54e-9", "100e-3"),
    mos("PM3", "VPB", "ENE", "VDD", "psvt", "119e-9", "54e-9", "delvtrand_psvt"),
    mos("PM4", "OUT", "ENE", "VDD", "psvt", "119e-9", "54e-9", "100e-3"),
    mos("PM5", "NETX", "ENE", "VDD", "psvt", "119e-9", "54e-9", "50e-3"),
    mos("PM6", "NETY", "ENB", "VDD", "pulvt", "119e-9", "54e-9", "delvtrand_pulvt"),
])
lines_B += subckt("TS_analog_B", ["CLK", "OUT", "VDD", "VSS"], [
    mos("M0", "OUT", "N2", "VSS", "nsvt", "300e-9", "6e-9", "delvtrand_nsvt"),
    mos("M1", "OUT", "N2", "VDD", "psvt", "300e-9", "6e-9", "delvtrand_psvt"),
    mos("M2", "OUT", "N2", "VDD", "psvt", "300e-9", "6e-9", "delvtrand_psvt"),
    mos("M3", "N2", "N3", "VSS", "nulvt", "200e-9", "20e-9", "delvtrand_nulvt"),
    mos("M4", "N3", "N4", "VDD", "pulvt", "200e-9", "20e-9", "100e-3"),
    mos("M5", "N4", "CLK", "VSS", "nsvt", "200e-9", "20e-9", "0"),
    mos("M6", "N5", "CLK", "VDD", "psvt", "200e-9", "20e-9", "delvtrand_psvt"),
])
netlist_B = "\n".join(lines_B) + "\n"

def compute_oracle(netlist_text, filename):
    lines = netlist_text.split("\n")
    total = 0
    anomalies = []
    dist = {}
    current_sub = None
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith(".subckt"):
            current_sub = s.split()[1]
        elif s.startswith(".ends"):
            current_sub = None
        m = re.search(r'delvtrand=(\S+)', line)
        if m:
            total += 1
            val = m.group(1)
            inst_match = re.match(r'X(\S+)', s)
            inst = inst_match.group(1) if inst_match else "?"
            model_match = re.search(r'(\w+_dbc)', line)
            model = model_match.group(1) if model_match else "?"
            dist[val] = dist.get(val, 0) + 1
            if val not in PV:
                anomalies.append({"instance": inst, "subcircuit": current_sub, "line": i, "model": model, "delvtrand": val})
    pv_dist = {v: dist.get(v, 0) for v in PV}
    hc_count = sum(c for v, c in dist.items() if v not in PV)
    return {"netlist_file": filename, "total_transistors": total, "anomaly_count": len(anomalies), "anomalies": sorted(anomalies, key=lambda a: a["line"]), "delvtrand_distribution": dict(pv_dist, hardcoded=hc_count)}

oracle_A = compute_oracle(netlist_A, "netlist_A.cdl")
oracle_B = compute_oracle(netlist_B, "netlist_B.cdl")

print("=== ORACLE A ===")
print(json.dumps(oracle_A, indent=2))
print("=== ORACLE B ===")
print(json.dumps(oracle_B, indent=2))

os.makedirs(AST + "/inputs_A", exist_ok=True)
os.makedirs(AST + "/example_output", exist_ok=True)
os.makedirs(REF + "/hidden/inputs_B", exist_ok=True)
os.makedirs(REF + "/negative", exist_ok=True)

with open(AST + "/inputs_A/netlist_A.cdl", "w") as f:
    f.write(netlist_A)
with open(AST + "/example_output/report_A.json", "w") as f:
    json.dump(oracle_A, f, indent=2, ensure_ascii=False)
with open(REF + "/hidden/inputs_B/netlist_B.cdl", "w") as f:
    f.write(netlist_B)

with open(TMP + "/oracle_B.json", "w") as f:
    json.dump(oracle_B, f)
with open(TMP + "/oracle_A.json", "w") as f:
    json.dump(oracle_A, f)
with open(TMP + "/netlist_A.txt", "w") as f:
    f.write(netlist_A)
with open(TMP + "/netlist_B.txt", "w") as f:
    f.write(netlist_B)

print("Files written.")
print("netlist_A:", len(netlist_A), "bytes,", len(netlist_A.splitlines()), "lines")
print("netlist_B:", len(netlist_B), "bytes,", len(netlist_B.splitlines()), "lines")
