#!/usr/bin/env python3
# judge_vcc2sc_var_ref.py — reference solver for EDA-Eval-DesignFlow-Vcc2scVarJudge-001
# Usage: python3 judge_vcc2sc_var_ref.py <measure_file> <spec_file> <out.json>
#
# Parses a FineSimPro .mt0 measure file (header lines '$DATA1' / '.TITLE' then a
# column header `<metric...> temper alter#` then numeric rows), reads the SPEC
# file (`<metric> Variation<limit><m|u|n>V` per line), computes per-metric
# variation (max-min) across all corners, judges PASS/FAIL case-insensitively,
# produces a per-temperature breakdown, root-cause hints and optimization
# suggestions, and writes a structured JSON report.
import json, re, sys, os
from collections import defaultdict

META_COLS = {"temper", "alter#", "alter", "mc_index"}


def parse_spec(path):
    spec = {}
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            m = re.search(r"(\w+)\s+Variation\s*[<<=]\s*([\d.]+)\s*(m|u|n)?\s*V", line, re.I)
            if m:
                metric, num, unit = m.group(1), float(m.group(2)), (m.group(3) or "").lower()
                scale = {"m": 1e-3, "u": 1e-6, "n": 1e-9, "": 1.0}.get(unit, 1.0)
                spec[metric] = num * scale
    return spec


def _floats(text):
    out = []
    for t in text.split():
        if re.fullmatch(r"[+-]?[\d.eE+*\-]+", t):
            try:
                out.append(float(t))
            except ValueError:
                pass
    return out


def parse_measure_file(path):
    """Return (header_cols, rows) where rows is list of dict{col: value}."""
    with open(path, "r", errors="replace") as fh:
        lines = fh.readlines()
    hdr_idx, header = None, None
    for i, ln in enumerate(lines):
        if ln.startswith(("$DATA", "$OPTION", ".TITLE", "*", "#")):
            continue
        if not ln.strip():
            continue
        toks = ln.split()
        if toks and all(re.fullmatch(r"[A-Za-z_#][\w#]*", t) for t in toks):
            hdr_idx, header = i, toks
            break
    if hdr_idx is None or header is None:
        return [], []
    rows = []
    for ln in lines[hdr_idx + 1:]:
        if not ln.strip():
            continue
        vals = _floats(ln)
        if len(vals) < len(header):
            continue
        rows.append({header[j]: vals[j] for j in range(len(header))})
    return header, rows


def main():
    if len(sys.argv) != 4:
        print("usage: judge_vcc2sc_var_ref.py <measure_file> <spec_file> <out.json>")
        sys.exit(2)
    mt0_path, spec_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    spec = parse_spec(spec_path)
    if not spec:
        result = {"error": "no spec metric parsed", "spec_file": spec_path}
        json.dump(result, open(out_path, "w"), indent=2)
        sys.exit(2)
    header, rows = parse_measure_file(mt0_path)
    if not rows:
        result = {"error": "no measure rows parsed", "measure_file": mt0_path}
        json.dump(result, open(out_path, "w"), indent=2)
        sys.exit(1)

    # map spec metrics -> measure column (case-insensitive)
    metric_cols = {}
    for spec_metric in spec:
        ml = spec_metric.lower()
        col = next((h for h in header if h.lower() == ml), None)
        metric_cols[spec_metric] = col

    temper_col = next((h for h in header if h.lower() == "temper"), None)
    alter_col  = next((h for h in header if h.lower() in ("alter#", "alter")), None)

    n_corners = len(rows)
    metrics_report = {}
    overall_pass = True
    for spec_metric, limit in spec.items():
        col = metric_cols.get(spec_metric)
        entry = {
            "spec_metric": spec_metric,
            "limit_V": limit,
            "limit_mV": limit * 1e3,
            "measure_column": col,
            "present": col is not None,
        }
        if col is None:
            entry["judgement"] = "FAIL"
            entry["reason"] = "metric not present in measure file (case-insensitive match failed)"
            overall_pass = False
            metrics_report[spec_metric] = entry
            continue
        vals = [r[col] for r in rows]
        vmin, vmax = min(vals), max(vals)
        var = vmax - vmin
        mean = sum(vals) / len(vals)
        ok = var < limit
        overall_pass = overall_pass and ok
        # locate min/max corner (alter + temper)
        def corner_of(value):
            for r in rows:
                if r[col] == value:
                    return {"alter": (int(r[alter_col]) if alter_col and alter_col in r else None),
                            "temper": (r[temper_col] if temper_col and temper_col in r else None)}
            return None
        entry.update({
            "n_corners": len(vals),
            "min_V": vmin, "max_V": vmax, "mean_V": mean,
            "variation_V": var, "variation_mV": var * 1e3,
            "judgement": "PASS" if ok else "FAIL",
            "min_corner": corner_of(vmin),
            "max_corner": corner_of(vmax),
        })
        metrics_report[spec_metric] = entry

    # per-temperature breakdown
    per_temp = {}
    if temper_col:
        groups = defaultdict(list)
        for r in rows:
            groups[r[temper_col]].append(r)
        for t, rs in sorted(groups.items()):
            blk = {"n_corners": len(rs), "temper": t}
            for spec_metric, limit in spec.items():
                col = metric_cols.get(spec_metric)
                if col is None:
                    continue
                vs = [r[col] for r in rs]
                blk[spec_metric] = {
                    "variation_mV": (max(vs) - min(vs)) * 1e3 if len(vs) > 1 else 0.0,
                    "min_V": min(vs), "max_V": max(vs), "mean_V": sum(vs)/len(vs),
                }
            per_temp[str(t)] = blk

    # root-cause hints + optimization
    root_causes = []
    optimizations = []
    for spec_metric, entry in metrics_report.items():
        if entry.get("judgement") != "FAIL":
            continue
        col = entry.get("measure_column")
        if col is None or "min_corner" not in entry:
            continue
        # identify worst temperature block
        worst_t, worst_var = None, -1.0
        for t, blk in per_temp.items():
            v = blk.get(spec_metric, {}).get("variation_mV", 0.0)
            if v > worst_var:
                worst_var, worst_t = v, t
        root_causes.append({
            "metric": spec_metric,
            "variation_mV": entry["variation_mV"],
            "worst_temperature": worst_t,
            "worst_block_variation_mV": worst_var,
            "min_corner": entry["min_corner"],
            "max_corner": entry["max_corner"],
        })
        optimizations.append({
            "metric": spec_metric,
            "suggestions": [
                "increase loop/error-amplifier DC gain to reduce load regulation PVT sensitivity",
                "strengthen output-stage drive / lower output resistance for the worst load",
                "add temperature compensation / trim on the reference and input offset",
                "verify stability (no ringing) inside the measurement window",
            ],
            "worst_temperature": worst_t,
        })

    result = {
        "measure_file": os.path.basename(mt0_path),
        "spec_file": os.path.basename(spec_path),
        "n_corners_total": n_corners,
        "n_metrics": len(spec),
        "metrics": metrics_report,
        "per_temperature": per_temp,
        "overall_judgement": "PASS" if overall_pass else "FAIL",
        "root_causes": root_causes,
        "optimization_suggestions": optimizations,
        "method": "measure_file_parse_and_spec_judge",
    }
    json.dump(result, open(out_path, "w"), indent=2)
    print("overall:", result["overall_judgement"])
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
