#!/usr/bin/env python3
# Hidden B measure file: DIFFERENT structure from A to force generalization.
# - 81 corners (not 121); 3 temp blocks: 25C (1 typ), -40C (40), 125C (40)
# - different metric names: vcc2sc_vout_light / vcc2sc_vout_full
# - SPEC_B limits <4mV (not 5mV)
# - outcome: light PASS (var 3.20mV < 4mV), full FAIL (var 8.50mV > 4mV)
# - light min @ alter 40 (-40C), max @ alter 81 (125C)
# - full  min @ alter 75 (125C), max @ alter 5  (-40C)
import random
rng = random.Random(20261106)

OUT = []
OUT.append("$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0")
OUT.append(".TITLE 'vcc2sc_stdby_pvt_tran'")
OUT.append("  vcc2sc_vout_light vcc2sc_vout_full         temper         alter#")

def fmt_row(light, full, temper, alter):
    return "    %11.4e %11.4e %14.4e %14.4e" % (light, full, temper, float(alter))

# row 1: 25C typ
OUT.append(fmt_row(1.10230e+00, 1.09700e+00, 25.0, 1))

# -40C block (40 rows, alter 2..41): light var 2.40mV, full var 5.30mV
LOW_L_MIN, LOW_L_MAX = 1.09980, 1.10220   # light var 2.40mV
LOW_F_MIN, LOW_F_MAX = 1.09320, 1.09850   # full var 5.30mV  (full max @ alter 5 here)
low = [(LOW_L_MIN + (LOW_L_MAX-LOW_L_MIN)*rng.random(),
        LOW_F_MIN + (LOW_F_MAX-LOW_F_MIN)*rng.random()) for _ in range(40)]
low[0]  = (LOW_L_MIN, low[0][1])   # alter 2 = light block min
low[39] = (LOW_L_MAX, low[39][1])  # alter 41 = light block max
low[3]  = (low[3][0], LOW_F_MAX)   # alter 5 = full block max (overall full max)
low[10] = (low[10][0], LOW_F_MIN)  # alter 12 = full block min
for i,(l,f) in enumerate(low):
    OUT.append(fmt_row(l, f, -40.0, 2+i))

# 125C block (40 rows, alter 42..81): light var 1.10mV, full var 3.20mV
HIGH_L_MIN, HIGH_L_MAX = 1.10130, 1.10240   # light var 1.10mV  (overall light max @ alter 81)
HIGH_F_MIN, HIGH_F_MAX = 1.08990, 1.09310   # full var 3.20mV  (overall full min @ alter 75)
high = [(HIGH_L_MIN + (HIGH_L_MAX-HIGH_L_MIN)*rng.random(),
         HIGH_F_MIN + (HIGH_F_MAX-HIGH_F_MIN)*rng.random()) for _ in range(40)]
high[0]  = (HIGH_L_MIN, high[0][1])   # alter 42 = light block min
high[39] = (HIGH_L_MAX, high[39][1])  # alter 81 = light block max (overall light max)
high[33] = (high[33][0], HIGH_F_MIN)  # alter 75 = full block min (overall full min)
high[20] = (high[20][0], HIGH_F_MAX)  # alter 62 = full block max
for i,(l,f) in enumerate(high):
    OUT.append(fmt_row(l, f, 125.0, 42+i))

text = "\n".join(OUT) + "\n"
with open("designflow/_B_mt0.txt","w") as f:
    f.write(text)

# verify
light = [1.10230] + [l for l,_ in low] + [l for l,_ in high]
full  = [1.09700] + [f for _,f in low] + [f for _,f in high]
temper = [25.0] + [-40.0]*40 + [125.0]*40
assert len(light)==81 and len(full)==81
print("B.mt0 rows:", len(light))
print("light: min=%.6f max=%.6f var=%.3fmV" % (min(light), max(light), (max(light)-min(light))*1000))
print("full : min=%.6f max=%.6f var=%.3fmV" % (min(full),  max(full),  (max(full)-min(full))*1000))
print("light min @ alter", light.index(min(light))+1, "T=", temper[light.index(min(light))])
print("light max @ alter", light.index(max(light))+1, "T=", temper[light.index(max(light))])
print("full  min @ alter", full.index(min(full))+1,  "T=", temper[full.index(min(full))])
print("full  max @ alter", full.index(max(full))+1,  "T=", temper[full.index(max(full))])
for t in (25.0,-40.0,125.0):
    L=[light[i] for i in range(81) if temper[i]==t]; F=[full[i] for i in range(81) if temper[i]==t]
    if len(L)>1: print("  T=%g n=%d light_var=%.3fmV full_var=%.3fmV" % (t,len(L),(max(L)-min(L))*1000,(max(F)-min(F))*1000))
print("size:", len(text))
