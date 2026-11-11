#!/usr/bin/env python3
"""Filter cand400.tsv to find fresh (not in any shard ledger) + fresh-USER candidates.
Output sorted by D-domain-dominant + mc preference."""
import os, json, re

BASE = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow"
CAND = os.path.join(BASE, "_r528_cand400.tsv")
LEDGERS = [os.path.join(BASE, f"trace_ledger_{s}.tsv") for s in "ABCD"]
DJSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl"

def norm_sid(s):
    s = os.path.basename(s.strip())
    for suf in (".messages.json", ".json", ".messages"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    return s

# Build ledger sid set + ledger users
ledger_sids = set()
ledger_users = set()
for p in LEDGERS:
    if not os.path.exists(p):
        continue
    with open(p) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            sid = norm_sid(parts[0])
            ledger_sids.add(sid)
            ledger_users.add(parts[1].strip())

# Build D.jsonl users
d_users = set()
with open(DJSONL) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        ts = obj.get("trace_source") or {}
        u = ts.get("user") or obj.get("user") or ""
        if u:
            d_users.add(u)

print(f"# ledger_sids={len(ledger_sids)} ledger_users={len(ledger_users)} d_users={len(d_users)}", flush=True)

# D-domain keywords (dominant analog_context/schematic_netlist/waveform)
D_KW = re.compile(r"(?i)(schematic|netlist|waveform|analog|hspice|spice|spectre|pex|lvs|mosfet|transistor|cmos|cellview|virtuoso|aether|waveview|pyaether|mixed.signal|cadence|opamp|current.mirror|diffpair|bias|gm|ac.analysis|dc.analysis|tran|noise|stb|phase.margin|gain.margin|bode)")

def parse_cand(line):
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 5:
        return None
    mc = int(parts[0])
    sid = norm_sid(parts[1])
    user = parts[2].strip()
    host = parts[3].strip()
    kw = parts[4].strip() if len(parts) > 4 else ""
    return mc, sid, user, host, kw

fresh_rows = []
fresh_user_rows = []
with open(CAND) as f:
    for line in f:
        c = parse_cand(line)
        if not c:
            continue
        mc, sid, user, host, kw = c
        if sid in ledger_sids:
            continue  # already ledgered
        fresh = True
        # D-domain dominant check
        d_match = D_KW.search(kw)
        is_d_dom = bool(d_match)
        row = (mc, sid, user, host, kw, is_d_dom)
        fresh_rows.append(row)
        if user not in ledger_users and user not in d_users:
            fresh_user_rows.append(row)

print(f"# fresh (not ledgered)={len(fresh_rows)} fresh-USER={len(fresh_user_rows)}", flush=True)

# Sort: fresh-USER first, by D-domain dominant desc, then mc 10-29 first (smaller mc), then mc desc
def sort_key(r):
    mc, sid, user, host, kw, is_d_dom = r
    # prefer D-domain dominant, prefer mc 10-29 (low), then higher mc
    mc_bucket = 0 if (10 <= mc <= 29) else (1 if mc < 10 else 2)
    return (0 if is_d_dom else 1, mc_bucket, -mc)

fresh_user_rows.sort(key=sort_key)
fresh_rows.sort(key=sort_key)

out_fu = os.path.join(BASE, "_r528_fresh_user.tsv")
out_f = os.path.join(BASE, "_r528_fresh.tsv")
with open(out_fu, "w") as f:
    f.write("# mc\tsid\tuser\thost\tkeywords\td_dominant\n")
    for r in fresh_user_rows:
        mc, sid, user, host, kw, is_d_dom = r
        f.write(f"{mc}\t{sid}\t{user}\t{host}\t{kw}\t{int(is_d_dom)}\n")
with open(out_f, "w") as f:
    f.write("# mc\tsid\tuser\thost\tkeywords\td_dominant\n")
    for r in fresh_rows:
        mc, sid, user, host, kw, is_d_dom = r
        f.write(f"{mc}\t{sid}\t{user}\t{host}\t{kw}\t{int(is_d_dom)}\n")

print(f"# wrote {out_fu} ({len(fresh_user_rows)} rows)")
print(f"# wrote {out_f} ({len(fresh_rows)} rows)")
print("# top 25 fresh-USER:")
for r in fresh_user_rows[:25]:
    mc, sid, user, host, kw, is_d_dom = r
    print(f"{mc}\t{sid}\t{user}\t{host}\t{kw}\tD={is_d_dom}")
