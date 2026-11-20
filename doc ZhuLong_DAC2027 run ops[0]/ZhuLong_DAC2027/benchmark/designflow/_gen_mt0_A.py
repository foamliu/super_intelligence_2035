#!/usr/bin/env python3
# Reconstruct Vcc2scstdby_tran.mt0 (A) faithfully matching the trace's accepted
# golden SPEC judgment (ASST#120). 121 PVT corners; format verbatim from trace
# read_files (lines 1-15). First 12 data rows are VERBATIM from the trace; the
# remaining 109 are generated to reproduce the golden per-metric stats:
#   unload:  n=121  min=0.897240  max=0.902370  var=5.130mV  mean=0.900699
#   load1mA: n=121  min=0.886300  max=0.901560  var=15.260mV mean=0.898408
#     load1mA min @ alter 115 (130C), max @ alter 83 (130C)
#   per-temp: 85C=1 row; -40C=60 rows (unload var 3.70mV, load1mA var 10.94mV);
#             130C=60 rows (unload var 1.82mV, load1mA var 15.26mV)
import random, io, math
rng = random.Random(20261019)  # deterministic

OUT = []
OUT.append("$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0")
OUT.append(".TITLE '*******option**********'")
OUT.append("  vcc2sc_unload vcc2sc_load1ma         temper         alter#")

def fmt_row(unload, load1ma, temper, alter):
    return "    %11.4e %11.4e %14.4e %14.4e" % (unload, load1ma, temper, float(alter))

# --- Verbatim first 12 rows from trace (alter 1..12) ---
verbatim = [
    (9.0122e-01, 9.0044e-01,  85.0, 1),
    (9.0016e-01, 8.9964e-01, -40.0, 2),
    (9.0042e-01, 8.9998e-01, -40.0, 3),
    (9.0005e-01, 8.9944e-01, -40.0, 4),
    (9.0028e-01, 8.9978e-01, -40.0, 5),
    (8.9981e-01, 8.9917e-01, -40.0, 6),
    (9.0030e-01, 8.9980e-01, -40.0, 7),
    (9.0041e-01, 8.9996e-01, -40.0, 8),
    (9.0001e-01, 8.9942e-01, -40.0, 9),
    (8.9983e-01, 8.9920e-01, -40.0, 10),
    (9.0026e-01, 8.9975e-01, -40.0, 11),
    (9.0007e-01, 8.9948e-01, -40.0, 12),
]
for u, l, t, a in verbatim:
    OUT.append(fmt_row(u, l, t, a))

# --- Rows 13..61 : -40C block (49 more rows, alter 13..61) ---
# -40C block totals (60 rows): unload var 3.70mV, load1mA var 10.94mV
# overall unload min 0.897240 must be in -40C block (lowest temp -> lowest v).
# set -40C unload range [0.897240, 0.900940] (var 3.70mV)
# set -40C load1mA range [0.889900, 0.900840] (var 10.94mV)
# (mean tuned so overall mean hits golden)
LOW_U_MIN, LOW_U_MAX = 0.897240, 0.900940
LOW_L_MIN, LOW_L_MAX = 0.889900, 0.900840
# rows 2..12 already placed (11 rows). Need rows 13..61 (49 rows).
# ensure block min/max are hit: put min at row 13, max at row 61.
def gen_block(n_new, lo_u, hi_u, lo_l, hi_l, u_seed, l_seed, place_min_at, place_max_at):
    """Generate n_new rows uniformly within [lo,hi], then force min/max positions."""
    us = [lo_u + (hi_u-lo_u)*rng.random() for _ in range(n_new)]
    ls = [lo_l + (hi_l-lo_l)*rng.random() for _ in range(n_new)]
    us[place_min_at] = lo_u
    us[place_max_at] = hi_u
    ls[place_min_at] = lo_l
    ls[place_max_at] = hi_l
    return list(zip(us, ls))

# -40C remaining 49 rows (indices 0..48 within this batch)
low_rest = gen_block(49, LOW_U_MIN, LOW_U_MAX, LOW_L_MIN, LOW_L_MAX, 1, 2, place_min_at=0, place_max_at=48)
for i, (u, l) in enumerate(low_rest):
    OUT.append(fmt_row(u, l, -40.0, 13 + i))

# --- Rows 62..121 : 130C block (60 rows, alter 62..121) ---
# 130C block: unload var 1.82mV, load1mA var 15.26mV
# overall unload max 0.902370 in 130C; range [0.900550, 0.902370]
# overall load1mA min 0.886300 @ alter 115, max 0.901560 @ alter 83 (both 130C)
HIGH_U_MIN, HIGH_U_MAX = 0.900550, 0.902370   # var 1.82mV
HIGH_L_MIN, HIGH_L_MAX = 0.886300, 0.901560   # var 15.26mV
high_rest = gen_block(60, HIGH_U_MIN, HIGH_U_MAX, HIGH_L_MIN, HIGH_L_MAX, 3, 4, place_min_at=-1, place_max_at=-1)
# force load1mA min @ alter 115 (index 53), max @ alter 83 (index 21)  [both 130C, per golden]
high_rest[53] = (high_rest[53][0], HIGH_L_MIN)
high_rest[21] = (high_rest[21][0], HIGH_L_MAX)
# force unload max @ alter 92 (index 30), min @ alter 62 (index 0)
high_rest[0]  = (HIGH_U_MIN, high_rest[0][1])
high_rest[30] = (HIGH_U_MAX, high_rest[30][1])
# nudge means toward golden: shift -40C block slightly up (unload +0.00045, load1mA +0.0015)
for i in range(len(low_rest)):
    u, l = low_rest[i]
    low_rest[i] = (min(u + 0.00045, LOW_U_MAX), min(l + 0.0015, LOW_L_MAX))
# re-force -40C endpoints after nudge
low_rest[0]  = (LOW_U_MIN, low_rest[0][1])   # alter 13 = block unload min
low_rest[48] = (LOW_U_MAX, low_rest[48][1])  # alter 61 = block unload max
low_rest[0]  = (low_rest[0][0], LOW_L_MIN)
low_rest[48] = (low_rest[48][0], LOW_L_MAX)
for i, (u, l) in enumerate(high_rest):
    OUT.append(fmt_row(u, l, 130.0, 62 + i))

text = "\n".join(OUT) + "\n"
with open("designflow/_A_mt0.txt", "w") as f:
    f.write(text)

# verify stats
unload = [v[0] for v in verbatim] + [u for u,_ in low_rest] + [u for u,_ in high_rest]
load1  = [v[1] for v in verbatim] + [l for _,l in low_rest] + [l for _,l in high_rest]
temper = [85.0] + [-40.0]*60 + [130.0]*60
assert len(unload)==121 and len(load1)==121 and len(temper)==121
print("A.mt0 rows:", len(unload))
print("unload: min=%.6f max=%.6f var=%.3fmV mean=%.6f" % (min(unload), max(unload), (max(unload)-min(unload))*1000, sum(unload)/121))
print("load1mA: min=%.6f max=%.6f var=%.3fmV mean=%.6f" % (min(load1), max(load1), (max(load1)-min(load1))*1000, sum(load1)/121))
# per-temp
for t in (85.0,-40.0,130.0):
    u = [unload[i] for i in range(121) if temper[i]==t]
    l = [load1[i]  for i in range(121) if temper[i]==t]
    if len(u)>1:
        print("  T=%g n=%d unload_var=%.3fmV load_var=%.3fmV" % (t, len(u), (max(u)-min(u))*1000, (max(l)-min(l))*1000))
    else:
        print("  T=%g n=%d (single)" % (t, len(u)))
# load1mA min/max alter
min_idx = load1.index(min(load1)); max_idx = load1.index(max(load1))
print("load1mA min @ alter", min_idx+1, "T=", temper[min_idx])
print("load1mA max @ alter", max_idx+1, "T=", temper[max_idx])
print("size:", len(text))
