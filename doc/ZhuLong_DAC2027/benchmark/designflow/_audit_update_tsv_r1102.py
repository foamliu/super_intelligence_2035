#!/usr/bin/env python3
"""Update anti_hardcode_audit_all.tsv for the 79 D k=12 cases based on the
runtime §4.9 re-test (d_s49.tsv). Preserves all other rows unchanged.

Verdict mapping:
  SOUND    -> 判定 PASS, 有anti_hardcode=y(runtime), print_only/core_deleted/hardcode_a=FAIL(runtime)
  WEAK_NEG -> keep GAP, append note "r1102 runtime: ref PASS but existing negatives only fail shallowly (mis-named/structural); §4.9 not yet substantively tested"
  REF_FAIL -> keep GAP, append note "r1102 runtime: ref FAIL offline (harness-dependent, check reads hidden/ from assets); unverifiable without harness context"
  NO_REF   -> keep GAP, append note "r1102 runtime: no reference_submit.zip; unverifiable offline"
  NO_NEG   -> keep GAP, append note "r1102 runtime: no negative samples"
  NO_DIR/NO_CHECK -> keep GAP, append note "r1102 runtime: no reference/ dir found (naming mismatch)"
"""
import csv, io

AUDIT = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/anti_hardcode_audit_all.tsv"
S49 = "/tmp/d_s49.tsv"

# load s49 verdicts
s49 = {}
with open(S49) as f:
    next(f)
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        c = line.split("\t")
        s49[c[0]] = {"ref":c[1],"sut":c[2],"neg":c[3],"sub":c[4],"shal":c[5],"pass":c[6],"verdict":c[7],"note":c[8] if len(c)>8 else ""}

# read audit
with open(AUDIT) as f:
    header = f.readline()
    rows = [h.rstrip("\n") for h in f]

updated = 0
out_rows = []
for row in rows:
    cols = row.split("\t")
    cid = cols[1] if len(cols)>1 else ""
    if cols[0]=="D" and cid in s49:
        v = s49[cid]
        verdict = v["verdict"]
        if verdict == "SOUND":
            cols[3] = "y(runtime)"
            cols[4] = cols[4]  # 只在B跑 keep
            cols[5] = "FAIL(runtime)"
            cols[6] = "FAIL(runtime)"
            cols[7] = "FAIL(runtime)"
            cols[8] = "PASS"
            cols[9] = ("r1102 runtime §4.9 re-test (renamed negatives to SUT name '"
                       + v["sut"] + "'): ref PASS + all " + v["neg"] +
                       " negatives FAIL (n_pass=0, " + v["sub"] +
                       " substantive catches). Static GAP was false positive (static audit only looked for file-based A-gold cross-check pattern; this case uses embedded-oracle / runtime-subprocess / anti-hardcode-token-guard instead).")
        elif verdict == "WEAK_NEG":
            cols[9] = (cols[9] + " | r1102 runtime: ref PASS(" + v["ref"] +
                       ") but existing negatives only fail shallowly/structurally (n_sub="
                       + v["sub"] + ", n_shal=" + v["shal"] + ", n_pass=0) after rename to '"
                       + v["sut"] + "'; §4.9 not yet substantively tested by current negatives — needs stronger print_only/core_deleted negatives.")
        elif verdict == "REF_FAIL":
            cols[9] = (cols[9] + " | r1102 runtime: ref FAIL offline (ref=" + v["ref"] +
                       ", harness-dependent: check reads hidden/ fixtures from assets dir into workdir); unverifiable without harness context. "
                       + v["neg"] + " negatives, n_pass=0, n_sub=" + v["sub"] + ".")
        elif verdict == "NO_REF":
            cols[9] = (cols[9] + " | r1102 runtime: no reference_submit.zip; cannot confirm ref PASS offline. "
                       + v["neg"] + " negatives, n_pass=0, n_sub=" + v["sub"] + ".")
        elif verdict == "NO_NEG":
            cols[9] = cols[9] + " | r1102 runtime: no negative samples to test."
        else:
            cols[9] = cols[9] + " | r1102 runtime: " + verdict + " (" + v["note"] + ")."
        out_rows.append("\t".join(cols))
        updated += 1
    else:
        out_rows.append(row)

with open(AUDIT, "w") as f:
    f.write(header)
    f.write("\n".join(out_rows) + "\n")

print("updated %d D k=12 rows" % updated)
# recount
import subprocess
print("=== new D verdict counts ===")
