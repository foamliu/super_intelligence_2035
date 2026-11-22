#!/usr/bin/env python3
# negative: hardcode_b -- hardcodes B's exact JSON answer. Fails anti-hardcode
# (cond o): running on A (disjoint cell set) does NOT yield A's 14-missing
# oracle (it still emits B's answer).
import json, sys
B_ANSWER = {
  "missing_instances": [
    {"line": 11, "cell": "bufLV_drv", "instance": "I1",
     "ports": {"Y": "net1", "A": "clk_in", "vcc": "vcc", "vss": "vss"}},
    {"line": 12, "cell": "invLVSx2", "instance": "I2",
     "ports": {"Y": "net2", "A": "clk_in", "vcc": "vcc", "vss": "vss"}},
    {"line": 23, "cell": "nor2LVx2", "instance": "I0",
     "ports": {"Y": "Y", "A": "A", "B": "B", "vcc": "vcc", "vss": "vss"}},
    {"line": 24, "cell": "nor2LVx2", "instance": "I1",
     "ports": {"Y": "net10", "A": "Y", "B": "B", "vcc": "vcc", "vss": "vss"}},
    {"line": 25, "cell": "ntn_io", "instance": "MN0",
     "ports": {"D": "net10", "G": "A", "S": "vss", "B": "vss"}},
    {"line": 26, "cell": "ptn_io", "instance": "MP0",
     "ports": {"D": "net10", "G": "A", "S": "vcc", "B": "vcc"}},
    {"line": 37, "cell": "invenIOLV", "instance": "I0",
     "ports": {"Y": "Q", "A": "D", "En": "en", "EnN": "enN", "vcc": "vcc", "vss": "vss"}},
    {"line": 38, "cell": "keeperRC", "instance": "I1",
     "ports": {"Q": "Q", "vcc": "vcc", "vss": "vss"}},
    {"line": 40, "cell": "tg_lv", "instance": "I3",
     "ports": {"P0": "D", "P1": "Q", "S": "en", "SN": "enN"}},
    {"line": 51, "cell": "mux4IOLV", "instance": "I0",
     "ports": {"Y": "Y", "A": "A", "B": "B", "C": "C", "D": "D",
               "S0": "S0", "S1": "S1", "vcc": "vcc", "vss": "vss"}},
    {"line": 65, "cell": "delayRC3", "instance": "I0",
     "ports": {"OUT": "out", "IN": "in", "vcc": "vcc", "vss": "vss"}},
    {"line": 82, "cell": "invLVSx2", "instance": "I5",
     "ports": {"Y": "net40", "A": "sin", "vcc": "vpwr", "vss": "vgnd"}}
  ],
  "summary": {
    "total_instances": 28, "missing_count": 12, "available_count": 16,
    "missing_cells": ["bufLV_drv","delayRC3","invLVSx2","invenIOLV","keeperRC",
                      "mux4IOLV","nor2LVx2","ntn_io","ptn_io","tg_lv"],
    "available_cells_used": ["andbase_clk","bufLV","clkbufLV","dff_base","invLV",
                             "keeper_base","mux2LV","nmos_b","pgmon_b","pmos_b",
                             "tie_base"]
  }
}
print(json.dumps(B_ANSWER, indent=2))
