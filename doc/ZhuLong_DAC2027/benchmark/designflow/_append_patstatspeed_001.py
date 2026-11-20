#!/usr/bin/env python3
"""Builder for EDA-Eval-DesignFlow-PatStatSpeed-001 (verification, B-track synth, L1-static).

Trace: jascperc @ hfeg0pkn001, session 1793172758983_0kv56.messages.json (mc=160, verilog:3287).
User verbatim (#0): analyze two LPDDR5 dvprog dirs, count valid .avc patterns by speed
(2nd-to-last '_' field of filename) and by MCU week (ISO week from file mtime); valid folder
must contain more than just irun.log (A_Compare.txt + ncsim.shm); output html + md with chart.
Real /rundata dirs are jascperc-host-owned and not extractable into the sandbox, so assets are
synthesized (B-track). check.py re-runs the candidate pattern_analysis.py on a HIDDEN B tree
(different speeds/weeks/counts) and validates a machine-readable stats.json + html/md presence.
"""
import os, json, zipfile, subprocess, sys, shutil, struct, tempfile

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-PatStatSpeed-001"
AST = os.path.join(REPO, "assets", CID)
REF = os.path.join(REPO, "reference", CID)

import datetime

def iso_week_label(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    y, w, _ = dt.isocalendar()
    return "W%d-%d" % (w, y)

def fmt_ts(ts):
    if ts is None: return "N/A"
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

# ---------- avc / folder tree generator ----------
def make_avc(root, name, mtime_ts, kind):
    """kind: 'valid' | 'only_irun' | 'no_folder' | 'no_speed'"""
    if kind == "no_speed":
        # single-field name -> no speed parseable
        fname = name if name.endswith(".avc") else name + ".avc"
        p = os.path.join(root, fname)
        with open(p, "w") as f:
            f.write("# avc stub\n")
        os.utime(p, (mtime_ts, mtime_ts))
        return
    fname = name if name.endswith(".avc") else name + ".avc"
    p = os.path.join(root, fname)
    with open(p, "w") as f:
        f.write("# avc stub %s\n" % name)
    os.utime(p, (mtime_ts, mtime_ts))
    fld = os.path.join(root, fname[:-4])
    if kind == "no_folder":
        return  # intentionally no folder
    os.makedirs(fld, exist_ok=True)
    if kind == "valid":
        with open(os.path.join(fld, "A_Compare.txt"), "w") as f:
            f.write("PASS\n")
        os.makedirs(os.path.join(fld, "ncsim.shm"), exist_ok=True)
        with open(os.path.join(fld, "irun.log"), "w") as f:
            f.write("irun log\n")
    elif kind == "only_irun":
        with open(os.path.join(fld, "irun.log"), "w") as f:
            f.write("irun only\n")
    # set folder mtime too (not used by analyzer but tidy)
    os.utime(fld, (mtime_ts, mtime_ts))

# Date timestamps (2026). ISO weeks computed by isocalendar.
D = {}
for mmdd, ts_str in [
    ("0915", "2026-09-15 10:00:00"), ("0916", "2026-09-16 11:00:00"),
    ("0922", "2026-09-22 09:30:00"), ("0923", "2026-09-23 14:00:00"),
    ("0929", "2026-09-29 08:00:00"), ("0930", "2026-09-30 12:00:00"),
    ("1006", "2026-10-06 10:00:00"), ("1007", "2026-10-07 15:00:00"),
    ("1013", "2026-10-13 09:00:00"), ("1014", "2026-10-14 16:00:00"),
    ("1020", "2026-10-20 10:00:00"), ("1027", "2026-10-27 11:00:00"),
    ("1103", "2026-11-03 09:00:00"),
]:
    D[mmdd] = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").timestamp()

def build_A():
    root = os.path.join(AST, "dvprog_A")
    if os.path.isdir(root): shutil.rmtree(root)
    d1 = os.path.join(root, "PTE_A1"); os.makedirs(d1, exist_ok=True)
    d2 = os.path.join(root, "PTE_A2"); os.makedirs(d2, exist_ok=True)
    # A dir1: speed 10667 across W42-W44; only-irun 20; no_folder 2; no_speed 1
    idx = 0
    for wk, n in [("1020", 10), ("1027", 8), ("1103", 5)]:
        for _ in range(n):
            idx += 1
            make_avc(d1, "pattern_simulation_16Gb_LP6_Fix_10667_%03d" % idx, D[wk], "valid")
    for i in range(20):
        make_avc(d1, "pattern_simulation_16Gb_LP6_Fix_9600_inv%03d" % i, D["1020"], "only_irun")
    for i in range(2):
        make_avc(d1, "pattern_simulation_16Gb_LP6_Fix_8000_orph%03d" % i, D["1021" if "1021" in D else "1020"], "no_folder")
    make_avc(d1, "lonely", D["1020"], "no_speed")
    # A dir2: speed 10667 W43-44; only-irun 10; no_folder 1
    idx = 0
    for wk, n in [("1027", 4), ("1103", 6)]:
        for _ in range(n):
            idx += 1
            make_avc(d2, "pattern_simulation_16Gb_LP6_Fix_10667_%03d" % idx, D[wk], "valid")
    for i in range(10):
        make_avc(d2, "pattern_simulation_16Gb_LP6_Fix_9600_inv%03d" % i, D["1027"], "only_irun")
    make_avc(d2, "pattern_simulation_16Gb_LP6_Fix_8000_orph0", D["1027"], "no_folder")

def build_B():
    root = os.path.join(REF, "hidden_B")
    if os.path.isdir(root): shutil.rmtree(root)
    d1 = os.path.join(root, "PTE_B1"); os.makedirs(d1, exist_ok=True)
    d2 = os.path.join(root, "PTE_B2"); os.makedirs(d2, exist_ok=True)
    # B dir1: speeds 9600/10667/8000 across W38-W41; skips
    idx = 0
    for spd, wk, n in [("9600","0915",6),("9600","0922",5),("9600","0929",4),
                       ("10667","0922",3),("10667","0929",7),("10667","1006",2),
                       ("8000","0929",4),("8000","1006",1)]:
        for _ in range(n):
            idx += 1
            make_avc(d1, "pattern_simulation_16Gb_LP6_Fix_%s_%03d" % (spd, idx), D[wk], "valid")
    for i in range(8):
        make_avc(d1, "pattern_simulation_16Gb_LP6_Fix_9600_bad%03d" % i, D["0915"], "only_irun")
    for i in range(3):
        make_avc(d1, "pattern_simulation_16Gb_LP6_Fix_7000_nf%03d" % i, D["0922"], "no_folder")
    make_avc(d1, "orphan", D["0915"], "no_speed")
    # B dir2: speeds 9600/10700 W41-W42; skips
    idx = 0
    for spd, wk, n in [("9600","1006",2),("9600","1013",3),("10700","1006",5),("10700","1013",6)]:
        for _ in range(n):
            idx += 1
            make_avc(d2, "pattern_simulation_16Gb_LP6_Fix_%s_%03d" % (spd, idx), D[wk], "valid")
    for i in range(5):
        make_avc(d2, "pattern_simulation_16Gb_LP6_Fix_9600_bad%03d" % i, D["1006"], "only_irun")
    for i in range(2):
        make_avc(d2, "pattern_simulation_16Gb_LP6_Fix_7000_nf%03d" % i, D["1013"], "no_folder")

# ---------- gold analyzer (independent oracle, used by check.py) ----------
GOLD_SRC = '''
import os, datetime, json
from collections import defaultdict

def _iso_week_label(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    y, w, _ = dt.isocalendar()
    return "W%d-%d" % (w, y)

def gold_analyze(dirs):
    results = []
    skipped = {"no_folder": [], "only_irunlog": [], "no_speed": []}
    per_dir = []
    total_avc = 0
    for basedir, label in dirs:
        avc = valid = nf = oi = ns = 0
        try:
            entries = os.listdir(basedir)
        except Exception:
            entries = []
        for e in sorted(entries):
            fp = os.path.join(basedir, e)
            if not e.endswith(".avc") or not os.path.isfile(fp):
                continue
            avc += 1
            base = e[:-4]
            parts = base.split("_")
            speed = parts[-2] if len(parts) >= 2 else None
            if speed is None:
                skipped["no_speed"].append(e); ns += 1; continue
            fldp = os.path.join(basedir, base)
            if not os.path.isdir(fldp):
                skipped["no_folder"].append(e); nf += 1; continue
            try:
                contents = os.listdir(fldp)
            except Exception:
                contents = []
            non_irun = [x for x in contents if x != "irun.log" and not x.startswith(".")]
            if len(non_irun) == 0:
                skipped["only_irunlog"].append(e); oi += 1; continue
            ts = os.stat(fp).st_mtime
            results.append({"filename": e, "speed": speed, "timestamp": ts})
            valid += 1
        per_dir.append({"label": label, "avc": avc, "valid": valid,
                        "no_folder": nf, "only_irunlog": oi, "no_speed": ns})
    total_avc = sum(pd["avc"] for pd in per_dir)
    total_valid = len(results)
    speeds = sorted(set(r["speed"] for r in results))
    weeks = sorted(set(_iso_week_label(r["timestamp"]) for r in results),
                   key=lambda s: (int(s.split("-")[1]), int(s.split("-")[0][1:])))
    weekly_total = defaultdict(int)
    per_speed_weekly = defaultdict(lambda: defaultdict(int))
    tss = [r["timestamp"] for r in results if r["timestamp"]]
    for r in results:
        wl = _iso_week_label(r["timestamp"])
        weekly_total[wl] += 1
        per_speed_weekly[r["speed"]][wl] += 1
    time_range = [datetime.datetime.fromtimestamp(min(tss)).strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.datetime.fromtimestamp(max(tss)).strftime("%Y-%m-%d %H:%M:%S")] if tss else [None, None]
    return {
        "total_valid": total_valid,
        "total_avc": total_avc,
        "unique_speeds": len(speeds),
        "speeds": speeds,
        "time_range": time_range,
        "week_span": len(weeks),
        "weeks": weeks,
        "weekly_total": dict(weekly_total),
        "per_speed_weekly": {s: dict(v) for s, v in per_speed_weekly.items()},
        "skipped": skipped,
        "per_dir": per_dir,
    }
'''

# ---------- reference solution pattern_analysis.py ----------
REF_SCRIPT = '''#!/usr/bin/env python3
"""Pattern .avc speed/week analyzer -> HTML + MD + stats.json reports.

Usage: pattern_analysis.py <dir1> <dir2> <output_dir> [--label1 L1] [--label2 L2]

Rules (per verification trace):
  - speed = second-to-last underscore-delimited field of .avc filename
  - a valid pattern has a matching folder (basename without .avc) that contains
    more than just irun.log (i.e. at least one non-irun.log, non-hidden file)
  - group valid patterns by speed and by MCU ISO week (from file mtime)
"""
import os, sys, datetime, json, argparse
from collections import defaultdict

SPEED_COLORS = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd',
                '#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']

def get_speed(fname):
    base = fname[:-4] if fname.endswith(".avc") else fname
    parts = base.split("_")
    return parts[-2] if len(parts) >= 2 else None

def folder_valid(fp):
    if not os.path.isdir(fp):
        return False
    try:
        non_irun = [e for e in os.listdir(fp) if e != "irun.log" and not e.startswith(".")]
        return len(non_irun) > 0
    except Exception:
        return False

def get_ts(path):
    try:
        st = os.stat(path)
        return st.st_mtime or st.st_ctime
    except Exception:
        return None

def mcu_week(ts):
    if ts is None:
        return (None, None)
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.isocalendar()[:2]

def week_label(wk):
    return "W%d-%d" % (wk[1], wk[0]) if wk[0] else "Unknown"

def fmt_ts(ts):
    if ts is None:
        return "N/A"
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def analyze_dir(basedir, label):
    results, skip_nof, skip_log, skip_spd = [], [], [], []
    avc = 0
    try:
        entries = os.listdir(basedir)
    except Exception as e:
        print("ERROR: cannot list %s: %s" % (basedir, e))
        return [], [], [], [], 0
    avcs = sorted(e for e in entries if e.endswith(".avc") and os.path.isfile(os.path.join(basedir, e)))
    for f in avcs:
        avc += 1
        spd = get_speed(f)
        if spd is None:
            skip_spd.append(f); continue
        fld = f[:-4]
        fldp = os.path.join(basedir, fld)
        if not os.path.isdir(fldp):
            skip_nof.append(f); continue
        if not folder_valid(fldp):
            skip_log.append(f); continue
        ts = get_ts(os.path.join(basedir, f))
        results.append({"filename": f, "speed": spd, "folder": fld,
                        "timestamp": ts, "source": label})
    print("Dir[%s] %s: AVC=%d Valid=%d NoFolder=%d OnlyIrun=%d NoSpeed=%d" %
          (label, basedir, avc, len(results), len(skip_nof), len(skip_log), len(skip_spd)))
    return results, skip_nof, skip_log, skip_spd, avc

def compute_stats(results, per_dir_info, all_skip):
    speeds = sorted(set(r["speed"] for r in results))
    weeks = sorted(set(week_label(mcu_week(r["timestamp"])) for r in results),
                   key=lambda s: (int(s.split("-")[1]), int(s.split("-")[0][1:])))
    weekly_total = defaultdict(int)
    per_speed_weekly = defaultdict(lambda: defaultdict(int))
    tss = [r["timestamp"] for r in results if r["timestamp"]]
    for r in results:
        wl = week_label(mcu_week(r["timestamp"]))
        weekly_total[wl] += 1
        per_speed_weekly[r["speed"]][wl] += 1
    time_range = [fmt_ts(min(tss)), fmt_ts(max(tss))] if tss else ["N/A", "N/A"]
    return {
        "total_valid": len(results),
        "total_avc": sum(pd["avc"] for pd in per_dir_info),
        "unique_speeds": len(speeds),
        "speeds": speeds,
        "time_range": time_range,
        "week_span": len(weeks),
        "weeks": weeks,
        "weekly_total": dict(weekly_total),
        "per_speed_weekly": {s: dict(v) for s, v in per_speed_weekly.items()},
        "skipped": all_skip,
        "per_dir": per_dir_info,
    }

def gen_md(stats, dirs_meta):
    L = []
    L.append("# Pattern Speed Analysis Report")
    L.append("")
    L.append("*Generated on %s*" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    L.append("")
    L.append("## Overview")
    L.append("")
    L.append("- **Total Valid Patterns:** %d" % stats["total_valid"])
    L.append("- **Total AVC Scanned:** %d" % stats["total_avc"])
    L.append("- **Time Range:** %s ~ %s" % (stats["time_range"][0], stats["time_range"][1]))
    L.append("- **Unique Speeds:** %d" % stats["unique_speeds"])
    L.append("- **Week Span:** %d weeks" % stats["week_span"])
    L.append("")
    L.append("### Source Directories")
    L.append("")
    L.append("| Label | Path | Valid |")
    L.append("|-------|------|-------|")
    for pd in stats["per_dir"]:
        L.append("| %s | `%s` | %d |" % (pd["label"], dirs_meta.get(pd["label"], ""), pd["valid"]))
    L.append("")
    L.append("## Speed Overview")
    L.append("")
    L.append("| Speed | Total |")
    L.append("|-------|-------|")
    for s in stats["speeds"]:
        tot = sum(stats["per_speed_weekly"][s].values())
        L.append("| %s MHz | %d |" % (s, tot))
    L.append("")
    L.append("## Weekly Summary")
    L.append("")
    L.append("| Week | Total | Speed Breakdown |")
    L.append("|------|-------|----------------|")
    for w in stats["weeks"]:
        tot = stats["weekly_total"].get(w, 0)
        brk = " ".join("%sMHz:%d" % (s, stats["per_speed_weekly"][s].get(w, 0)) for s in stats["speeds"])
        L.append("| %s | %d | %s |" % (w, tot, brk))
    L.append("")
    L.append("## Per-Speed Weekly Breakdown")
    L.append("")
    hdr = "| Speed |" + "".join("%s|" % w for w in stats["weeks"]) + " Total |"
    sep = "|-------|" + "".join("---|" for _ in stats["weeks"]) + "-------|"
    L.append(hdr); L.append(sep)
    for s in stats["speeds"]:
        row = "| %s MHz |" % s
        for w in stats["weeks"]:
            row += " %d |" % stats["per_speed_weekly"][s].get(w, 0)
        row += " **%d** |" % sum(stats["per_speed_weekly"][s].values())
        L.append(row)
    L.append("")
    L.append("## Skipped / Invalid Patterns")
    L.append("")
    for cat in ("no_folder", "only_irunlog", "no_speed"):
        items = stats["skipped"].get(cat, [])
        L.append("### %s (%d items)" % (cat, len(items)))
        L.append("")
        for it in items[:10]:
            L.append("- `%s`" % it)
        if len(items) > 10:
            L.append("- *... and %d more*" % (len(items) - 10))
        L.append("")
    L.append("---")
    L.append("*Report generated automatically*")
    return "\\n".join(L)

def gen_html(stats, dirs_meta):
    L = []
    L.append("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Pattern Speed Report</title>")
    L.append("<style>body{font-family:sans-serif;margin:20px}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px 8px}</style>")
    L.append("</head><body>")
    L.append("<h1>Pattern Speed Analysis Report</h1>")
    L.append("<p>Generated on %s</p>" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    L.append("<h2>Overview</h2><ul>")
    L.append("<li><b>Total Valid Patterns:</b> %d</li>" % stats["total_valid"])
    L.append("<li><b>Total AVC Scanned:</b> %d</li>" % stats["total_avc"])
    L.append("<li><b>Time Range:</b> %s ~ %s</li>" % (stats["time_range"][0], stats["time_range"][1]))
    L.append("<li><b>Unique Speeds:</b> %d</li>" % stats["unique_speeds"])
    L.append("<li><b>Week Span:</b> %d weeks</li>" % stats["week_span"])
    L.append("</ul>")
    # chart: stacked bar via inline SVG
    L.append("<h2>Weekly Speed Chart</h2>")
    L.append("<div id='chart' class='chart-container'>")
    weeks = stats["weeks"]; speeds = stats["speeds"]
    maxv = max([stats["weekly_total"].get(w, 0) for w in weeks] + [1])
    bw = 60; h = 200
    L.append("<svg width='%d' height='%d'>" % (max(1, len(weeks)) * bw + 80, h + 60))
    for i, w in enumerate(weeks):
        x = i * bw + 40
        y0 = h
        for si, s in enumerate(speeds):
            v = stats["per_speed_weekly"][s].get(w, 0)
            bh = int(v / maxv * h)
            col = SPEED_COLORS[si % len(SPEED_COLORS)]
            L.append("<rect x='%d' y='%d' width='%d' height='%d' fill='%s'><title>%s %s: %d</title></rect>" % (x, y0 - bh, bw - 10, bh, col, s, w, v))
            y0 -= bh
        L.append("<text x='%d' y='%d' font-size='10' text-anchor='middle'>%s</text>" % (x + (bw - 10) / 2, h + 15, w))
    # legend
    for si, s in enumerate(speeds):
        L.append("<rect x='10' y='%d' width='12' height='12' fill='%s'></rect><text x='28' y='%d' font-size='10'>%s MHz</text>" % (h + 40 + si * 16, SPEED_COLORS[si % len(SPEED_COLORS)], h + 50 + si * 16, s))
    L.append("</svg></div>")
    L.append("<h2>Per-Speed Weekly Breakdown</h2><table><tr><th>Speed</th>" + "".join("<th>%s</th>" % w for w in weeks) + "<th>Total</th></tr>")
    for s in speeds:
        row = "<tr><td>%s MHz</td>" % s
        for w in weeks:
            row += "<td>%d</td>" % stats["per_speed_weekly"][s].get(w, 0)
        row += "<td><b>%d</b></td></tr>" % sum(stats["per_speed_weekly"][s].values())
        L.append(row)
    L.append("</table>")
    L.append("</body></html>")
    return "\\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir1"); ap.add_argument("dir2"); ap.add_argument("output_dir")
    ap.add_argument("--label1", default="dir1"); ap.add_argument("--label2", default="dir2")
    args = ap.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    dirs = [(args.dir1, args.label1), (args.dir2, args.label2)]
    all_results = []; all_skip = {"no_folder": [], "only_irunlog": [], "no_speed": []}
    per_dir_info = []; dirs_meta = {}
    for basedir, label in dirs:
        res, nf, oi, ns, avc = analyze_dir(basedir, label)
        all_results.extend(res)
        all_skip["no_folder"].extend(nf); all_skip["only_irunlog"].extend(oi); all_skip["no_speed"].extend(ns)
        per_dir_info.append({"label": label, "avc": avc, "valid": len(res),
                             "no_folder": len(nf), "only_irunlog": len(oi), "no_speed": len(ns)})
        dirs_meta[label] = basedir
    stats = compute_stats(all_results, per_dir_info, all_skip)
    with open(os.path.join(args.output_dir, "pattern_speed_report.md"), "w") as f:
        f.write(gen_md(stats, dirs_meta))
    with open(os.path.join(args.output_dir, "pattern_speed_report.html"), "w") as f:
        f.write(gen_html(stats, dirs_meta))
    with open(os.path.join(args.output_dir, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print("Wrote report to %s (valid=%d avc=%d speeds=%d weeks=%d)" %
          (args.output_dir, stats["total_valid"], stats["total_avc"], stats["unique_speeds"], stats["week_span"]))

if __name__ == "__main__":
    main()
'''

# ---------- check.py ----------
CHECK_PY = '''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-PatStatSpeed-001 (verification, B-track synth, L1-static).

Trace: jascperc @ hfeg0pkn001, session 1793172758983_0kv56.messages.json (mc=160).
User verbatim (#0): analyze two LPDDR5 dvprog dirs; count valid .avc patterns by speed
(2nd-to-last '_' field) and by MCU ISO week (file mtime); valid folder must contain more than
just irun.log (A_Compare.txt + ncsim.shm); output html + md with chart.

Deliverable: outputs/submit.zip{pattern_analysis.py}. check() re-runs the candidate script on a
HIDDEN B dvprog tree (different speeds/weeks/counts) and validates stats.json + html/md presence,
defeating hardcoded answers.
"""
import os, re, sys, json, zipfile, tempfile, shutil, subprocess, py_compile, datetime
from collections import defaultdict

CID = "EDA-Eval-DesignFlow-PatStatSpeed-001"
HERE = os.path.dirname(os.path.abspath(__file__))
B_ROOT = os.path.join(HERE, "hidden_B")

def _iso_week_label(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    y, w, _ = dt.isocalendar()
    return "W%d-%d" % (w, y)

def gold_analyze(dirs):
    results = []; skipped = {"no_folder": [], "only_irunlog": [], "no_speed": []}
    per_dir = []
    for basedir, label in dirs:
        avc = valid = nf = oi = ns = 0
        try:
            entries = os.listdir(basedir)
        except Exception:
            entries = []
        for e in sorted(entries):
            fp = os.path.join(basedir, e)
            if not e.endswith(".avc") or not os.path.isfile(fp):
                continue
            avc += 1
            base = e[:-4]
            parts = base.split("_")
            speed = parts[-2] if len(parts) >= 2 else None
            if speed is None:
                skipped["no_speed"].append(e); ns += 1; continue
            fldp = os.path.join(basedir, base)
            if not os.path.isdir(fldp):
                skipped["no_folder"].append(e); nf += 1; continue
            try:
                contents = os.listdir(fldp)
            except Exception:
                contents = []
            non_irun = [x for x in contents if x != "irun.log" and not x.startswith(".")]
            if len(non_irun) == 0:
                skipped["only_irunlog"].append(e); oi += 1; continue
            ts = os.stat(fp).st_mtime
            results.append({"filename": e, "speed": speed, "timestamp": ts})
            valid += 1
        per_dir.append({"label": label, "avc": avc, "valid": valid,
                        "no_folder": nf, "only_irunlog": oi, "no_speed": ns})
    speeds = sorted(set(r["speed"] for r in results))
    weeks = sorted(set(_iso_week_label(r["timestamp"]) for r in results),
                   key=lambda s: (int(s.split("-")[1]), int(s.split("-")[0][1:])))
    weekly_total = defaultdict(int)
    per_speed_weekly = defaultdict(lambda: defaultdict(int))
    tss = [r["timestamp"] for r in results if r["timestamp"]]
    for r in results:
        wl = _iso_week_label(r["timestamp"])
        weekly_total[wl] += 1
        per_speed_weekly[r["speed"]][wl] += 1
    time_range = [datetime.datetime.fromtimestamp(min(tss)).strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.datetime.fromtimestamp(max(tss)).strftime("%Y-%m-%d %H:%M:%S")] if tss else [None, None]
    return {
        "total_valid": len(results),
        "total_avc": sum(pd["avc"] for pd in per_dir),
        "unique_speeds": len(speeds),
        "speeds": speeds,
        "time_range": time_range,
        "week_span": len(weeks),
        "weeks": weeks,
        "weekly_total": dict(weekly_total),
        "per_speed_weekly": {s: dict(v) for s, v in per_speed_weekly.items()},
        "skipped": skipped,
        "per_dir": per_dir,
    }

def _read_zip(zpath):
    if not os.path.isfile(zpath):
        raise AssertionError("cond(a): submit.zip not found at %s" % zpath)
    out = {}
    with zipfile.ZipFile(zpath) as z:
        for n in z.namelist():
            if n.endswith("/"):
                continue
            base = os.path.basename(n)
            if base:
                try:
                    out[base] = z.read(n).decode("utf-8")
                except UnicodeDecodeError:
                    out[base] = z.read(n).decode("latin-1")
    return out

def _run_candidate(script_text, d1, d2, tmp):
    sp = os.path.join(tmp, "cand_pattern_analysis.py")
    with open(sp, "w") as f:
        f.write(script_text)
    outdir = os.path.join(tmp, "cand_out")
    os.makedirs(outdir, exist_ok=True)
    try:
        r = subprocess.run([sys.executable, sp, d1, d2, outdir],
                           capture_output=True, text=True, timeout=180)
    except Exception as e:
        return None, None, "script crashed: %s" % e
    stats_path = os.path.join(outdir, "stats.json")
    stats = None
    if os.path.isfile(stats_path):
        try:
            with open(stats_path) as fh:
                stats = json.load(fh)
        except Exception:
            stats = None
    return stats, r, outdir

def check(deliverable, workdir):
    if not os.path.isabs(deliverable):
        deliverable = os.path.join(workdir, deliverable)
    files = _read_zip(deliverable)

    # (a) zip contains pattern_analysis.py
    assert "pattern_analysis.py" in files, "cond(a): missing pattern_analysis.py (have %s)" % sorted(files.keys())
    src = files["pattern_analysis.py"]

    # (b) py_compile OK
    cdir = tempfile.mkdtemp(prefix="patstat_compile_")
    try:
        tf_path = os.path.join(cdir, "cand.py")
        with open(tf_path, "w") as f:
            f.write(src)
        cfile = os.path.join(cdir, "cand.pyc")
        try:
            py_compile.compile(tf_path, cfile=cfile, doraise=True)
        except Exception as e:
            raise AssertionError("cond(b): pattern_analysis.py py_compile failed: %s" % e)
    finally:
        shutil.rmtree(cdir, ignore_errors=True)

    # gold from hidden B
    b1 = os.path.join(B_ROOT, "PTE_B1"); b2 = os.path.join(B_ROOT, "PTE_B2")
    assert os.path.isdir(b1) and os.path.isdir(b2), "hidden B missing"
    gold = gold_analyze([(b1, "PTE_B1"), (b2, "PTE_B2")])

    tmp = tempfile.mkdtemp(prefix="patstat_check_")
    try:
        stats, r, outdir = _run_candidate(src, b1, b2, tmp)

        # (c) CLI runs with 3 positional args, exits 0
        assert r is not None and r.returncode == 0, "cond(c): script must accept <dir1> <dir2> <output_dir> and exit 0 (rc=%s, stderr=%s)" % (
            r.returncode if r else "n/a", (r.stderr[:200] if r else ""))

        # (d) html exists + non-empty
        hp = os.path.join(outdir, "pattern_speed_report.html")
        assert os.path.isfile(hp) and os.path.getsize(hp) > 0, "cond(d): pattern_speed_report.html missing/empty"

        # (e) md exists + non-empty
        mp = os.path.join(outdir, "pattern_speed_report.md")
        assert os.path.isfile(mp) and os.path.getsize(mp) > 0, "cond(e): pattern_speed_report.md missing/empty"

        # (f) stats.json exists + valid JSON
        assert stats is not None, "cond(f): stats.json missing or not valid JSON"

        # (g) total_valid == gold
        assert int(stats.get("total_valid", -1)) == gold["total_valid"], "cond(g): total_valid %r != gold %r" % (stats.get("total_valid"), gold["total_valid"])

        # (h) total_avc == gold
        assert int(stats.get("total_avc", -1)) == gold["total_avc"], "cond(h): total_avc %r != gold %r" % (stats.get("total_avc"), gold["total_avc"])

        # (i) unique_speeds + speeds set
        assert int(stats.get("unique_speeds", -1)) == gold["unique_speeds"], "cond(i): unique_speeds %r != gold %r" % (stats.get("unique_speeds"), gold["unique_speeds"])
        cand_speeds = sorted(str(s) for s in stats.get("speeds", []))
        assert cand_speeds == gold["speeds"], "cond(i): speeds %r != gold %r" % (cand_speeds, gold["speeds"])

        # (j) speed parsed as 2nd-to-last field: gold has multi-field names; verify a known gold speed that is NOT first/last
        # (covered by speeds equality vs gold which uses parts[-2]; if candidate used last/first field, speeds mismatch -> (i) already fails.
        #  explicit: ensure gold speed set is non-trivial (>1 speed) so the field-position is exercised
        assert gold["unique_speeds"] >= 2, "cond(j): gold must exercise multi-speed (sanity)"

        # (k) weeks + week_span
        cand_weeks = sorted(str(w) for w in stats.get("weeks", []))
        assert cand_weeks == gold["weeks"], "cond(k): weeks %r != gold %r" % (cand_weeks, gold["weeks"])
        assert int(stats.get("week_span", -1)) == gold["week_span"], "cond(k): week_span %r != gold %r" % (stats.get("week_span"), gold["week_span"])

        # (l) weekly_total (normalize over gold weeks, missing=0)
        cand_wt = {str(k): int(v) for k, v in stats.get("weekly_total", {}).items()}
        gold_wt = {w: int(gold["weekly_total"].get(w, 0)) for w in gold["weeks"]}
        cand_wt = {w: int(cand_wt.get(w, 0)) for w in gold["weeks"]}
        assert cand_wt == gold_wt, "cond(l): weekly_total %r != gold %r" % (cand_wt, gold_wt)

        # (m) per_speed_weekly matrix (normalize: full matrix over gold speeds x gold weeks, missing=0)
        cand_psw = stats.get("per_speed_weekly", {})
        def _full(psw, speeds, weeks):
            return {s: {w: int(psw.get(s, {}).get(w, 0)) for w in weeks} for s in speeds}
        cand_m = _full(cand_psw, gold["speeds"], gold["weeks"])
        gold_m = _full(gold["per_speed_weekly"], gold["speeds"], gold["weeks"])
        assert cand_m == gold_m, "cond(m): per_speed_weekly %r != gold %r" % (cand_m, gold_m)

        # (n) validity filter: only_irunlog + no_folder skip counts
        skip = stats.get("skipped", {})
        cand_oi = len(skip.get("only_irunlog", []))
        cand_nf = len(skip.get("no_folder", []))
        assert cand_oi == len(gold["skipped"]["only_irunlog"]), "cond(n): only_irunlog skip %r != gold %r" % (cand_oi, len(gold["skipped"]["only_irunlog"]))
        assert cand_nf == len(gold["skipped"]["no_folder"]), "cond(n): no_folder skip %r != gold %r" % (cand_nf, len(gold["skipped"]["no_folder"]))

        # (o) html contains a chart/figure (svg/canvas/plotly/chart div) - user required legend/chart
        html_txt = open(hp).read()
        assert re.search(r"<svg|<canvas|plotly|chart-container|class=.chart|<rect", html_txt, re.I), "cond(o): html lacks chart/figure (svg/canvas/plotly)"

        # (p) anti-stub: source contains directory traversal + speed parse + file write
        assert re.search(r"os\\.listdir|os\\.walk", src), "cond(p): no directory traversal (os.listdir/os.walk)"
        assert re.search(r"\\.split\\(['\\\"]_['\\\"]\\)", src), "cond(p): no speed parsing (split('_'))"
        assert re.search(r"open\\(|\\.write\\(", src), "cond(p): no file write (open/write)"

        # (q) anti-hardcode cross-input: B gold differs from A gold (sanity that B is a real cross-input)
        a1 = os.path.join(os.path.join(HERE, "..", "..", "assets", CID, "dvprog_A", "PTE_A1"))
        a2 = os.path.join(os.path.join(HERE, "..", "..", "assets", CID, "dvprog_A", "PTE_A2"))
        if os.path.isdir(a1) and os.path.isdir(a2):
            ag = gold_analyze([(a1, "PTE_A1"), (a2, "PTE_A2")])
            assert ag["total_valid"] != gold["total_valid"] or ag["speeds"] != gold["speeds"], "cond(q): B must differ from A (anti-hardcode sanity)"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return True
'''

# ---------- prompt / brief / manifest ----------
PROMPT = '''分别对/rundata/iejoad/V0/simdir/verilog/e0033105/verilog.pim.iejoad.PTE_20260624_1/dvprog/和/rundata/iejoad/V0/simdir/verilog/e0033105/verilog.pim.iejoad.PTE_20260624/dvprog/两个路径下的
pattern统计下验证了哪些speed，每个speed 多少支。 pattern的speed是avc文件的倒数第二个字段，比如pattern_simulation_16Gb_LP6_Fix_10667_011.avc的频率是10667频率。
pattern 的统计可以按照文件新建的时间统计，给出一个统计时间跨度出来，再给出一个总览，总共哪些speed，每个speed 多少支。输出html和md两种格式。

不需要把每个pattern 都列出来，需要根据pattern的生成时间，按照周进行统计，每周测试了多少只。给个图例展示（折线图、柱状图都行），周序号按照实际的MCU周进行标记
输出的文件里都是乱码，可以把中文暂时按照英文翻译。

要对avc文件匹配的文件夹也要做检索，比如pattern_simulation_16Gb_LP6_Fix_9600_0928_9600_996.avc文件首先要检索下是否存在pattern_simulation_16Gb_LP6_Fix_9600_0928_9600_996文件夹，
然后pattern_simulation_16Gb_LP6_Fix_9600_0928_9600_996文件夹里只有irun.log的都要排除掉，这种不能算是合法的pattern。
/rundata/iejoad/V0/simdir/verilog/e0033105/verilog.pim.iejoad.PTE_20260624/dvprog/pattern_simulation_16Gb_LP6_Fix_9600_0928_9600_996/

包含A_Compare.txt、ncsim.shm的是有效的pattern文件。把有效的pattern文件按照不同的频率进行统计
不需要把每个pattern 都列出来，需要根据pattern的生成时间，按照周进行统计，每周测试了多少只。给个图例展示（折线图、柱状图都行），周序号按照实际的MCU周进行标记
'''

TASK_BRIEF = '''交付接口：outputs/submit.zip 含 pattern_analysis.py（Python3）。
用法：pattern_analysis.py <dir1> <dir2> <output_dir>，扫描两 dvprog 目录下的 .avc 与同名文件夹，在 output_dir 输出 pattern_speed_report.html、pattern_speed_report.md 与 stats.json（机器可读，字段：total_valid/total_avc/unique_speeds/speeds/time_range/week_span/weeks/weekly_total/per_speed_weekly/skipped{no_folder,only_irunlog,no_speed}/per_dir）。
判定规则：speed=avc 文件名倒数第二个 '_' 字段；合法 pattern=同名文件夹存在且含 irun.log 以外的文件；按文件 mtime 的 ISO 周(MCU 周)分组。
开发样例输入在 assets/dvprog_A/PTE_A1 与 PTE_A2（仅供调试，判分用不同输入）。
'''

def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)

def main():
    os.makedirs(AST, exist_ok=True)
    os.makedirs(REF, exist_ok=True)
    # A tree
    build_A()
    # B tree (judge side)
    build_B()
    # prompt / brief / manifest
    write_text(os.path.join(AST, "prompt.txt"), PROMPT)
    write_text(os.path.join(AST, "task_brief.md"), TASK_BRIEF)
    manifest = {"case_id": CID, "hidden_input": "B", "hidden_path": "reference/%s/hidden_B" % CID,
                "note": "B dvprog tree with different speeds/weeks/counts; check.py runs candidate on B only.",
                "b_dirs": ["PTE_B1", "PTE_B2"]}
    write_text(os.path.join(AST, "hidden", "hidden_manifest.json"), json.dumps(manifest, ensure_ascii=False, indent=2))
    # reference solution + check.py
    write_text(os.path.join(REF, "pattern_analysis.py"), REF_SCRIPT)
    write_text(os.path.join(REF, "check.py"), CHECK_PY)
    # reference_submit.zip
    zpath = os.path.join(REF, "reference_submit.zip")
    if os.path.isfile(zpath): os.unlink(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(REF, "pattern_analysis.py"), "pattern_analysis.py")
    # negatives
    neg_dir = os.path.join(REF, "negative")
    if os.path.isdir(neg_dir): shutil.rmtree(neg_dir)
    os.makedirs(os.path.join(neg_dir, "naive_noop"), exist_ok=True)
    os.makedirs(os.path.join(neg_dir, "print_only"), exist_ok=True)
    os.makedirs(os.path.join(neg_dir, "ref_delete_core"), exist_ok=True)
    # naive_noop: writes a stats.json with hardcoded A-ish numbers (wrong for B)
    noop = '''#!/usr/bin/env python3
import os, sys, json
d = sys.argv[3] if len(sys.argv) > 3 else "."
os.makedirs(d, exist_ok=True)
open(os.path.join(d, "pattern_speed_report.html"), "w").write("<html></html>")
open(os.path.join(d, "pattern_speed_report.md"), "w").write("# stub\\n")
stats = {"total_valid": 23, "total_avc": 60, "unique_speeds": 1, "speeds": ["10667"],
         "time_range": ["x","y"], "week_span": 3, "weeks": ["W42-2026","W43-2026","W44-2026"],
         "weekly_total": {"W42-2026": 10, "W43-2026": 12, "W44-2026": 1},
         "per_speed_weekly": {"10667": {"W42-2026": 10, "W43-2026": 12, "W44-2026": 1}},
         "skipped": {"no_folder": [], "only_irunlog": [], "no_speed": []},
         "per_dir": []}
json.dump(stats, open(os.path.join(d, "stats.json"), "w"))
print("noop")
'''
    write_text(os.path.join(neg_dir, "naive_noop", "pattern_analysis.py"), noop)
    print_only = '''#!/usr/bin/env python3
import sys
print("Pattern Speed Analysis Report")
print("total valid: 146")
print("(no files written)")
'''
    write_text(os.path.join(neg_dir, "print_only", "pattern_analysis.py"), print_only)
    # ref_delete_core: ref script with directory traversal removed (replace os.listdir with empty)
    del_core = REF_SCRIPT.replace("entries = os.listdir(basedir)", "entries = []  # CORE DELETED")
    write_text(os.path.join(neg_dir, "ref_delete_core", "pattern_analysis.py"), del_core)
    # negative_selftest.py
    selftest = '''#!/usr/bin/env python3
"""negative_selftest: all 3 negatives must FAIL check(). Run: python3 negative_selftest.py"""
import os, sys, json, zipfile, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check
def make_zip(py_text, tmp):
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("pattern_analysis.py", py_text)
    return zp
results = {}
for name in ["naive_noop", "print_only", "ref_delete_core"]:
    py = open(os.path.join(HERE, "negative", name, "pattern_analysis.py")).read()
    tmp = tempfile.mkdtemp()
    zp = make_zip(py, tmp)
    try:
        check.check(zp, tmp)
        results[name] = "PASS (BAD - negative should FAIL)"
    except AssertionError as e:
        results[name] = "FAIL (good): %s" % str(e)[:120]
    except Exception as e:
        results[name] = "FAIL (good): %s: %s" % (type(e).__name__, str(e)[:120])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(results, indent=2))
bad = [k for k, v in results.items() if v.startswith("PASS")]
sys.exit(1 if bad else 0)
'''
    write_text(os.path.join(REF, "negative_selftest.py"), selftest)
    print("BUILT assets + reference for", CID)
    # ---- self-verify ----
    def make_zip(py_text, tmp):
        zp = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr("pattern_analysis.py", py_text)
        return zp
    # ref PASS
    tmp = tempfile.mkdtemp()
    zp = make_zip(open(os.path.join(REF, "pattern_analysis.py")).read(), tmp)
    sys.path.insert(0, REF)
    import importlib
    if "check" in sys.modules: del sys.modules["check"]
    import check as chk
    try:
        ok = chk.check(zp, tmp)
        print("REF self-check:", "PASS" if ok else "FAIL", ok)
    except AssertionError as e:
        print("REF self-check: FAIL -", str(e)[:300])
        raise
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # negatives FAIL
    r = subprocess.run([sys.executable, os.path.join(REF, "negative_selftest.py")], capture_output=True, text=True)
    print("NEG selftest stdout:", r.stdout)
    print("NEG selftest rc:", r.returncode)
    if r.returncode != 0:
        print("NEG stderr:", r.stderr[:500])
        raise SystemExit("negative_selftest did not all FAIL")
    print("ALL SELF-VERIFY GREEN")

if __name__ == "__main__":
    main()
