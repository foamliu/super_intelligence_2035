#!/usr/bin/env python3
"""
R98: Training-Eval API Coverage Gap Analysis
=============================================
R97 showed 0% API full-coverage even with 27B model -> API knowledge is the
core bottleneck. This script checks: do the APIs required by the 158 eval
tasks actually appear in our SFT corpus and API knowledge base?

Zero GPU. Pure analysis. Python 3.8+ stdlib only.
"""
import argparse, json, os, re, sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent
REPORTS_DIR = RUN_DIR.parent / "reports"  # doc/BaiZe-ISEDA2027/reports/
EVAL_DATASET = Path.home() / "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
API_KB = Path.home() / "code/eda_fastmcp/docs/API_INFO_MERGED_V3.json"
SFT_V1 = RUN_DIR / "sft_pyaether_corpus.jsonl"
SFT_V2 = RUN_DIR / "sft_pyaether_corpus_v2.jsonl"

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try: records.append(json.loads(line))
                except json.JSONDecodeError: pass
    return records

def norm_api(api):
    api = api.strip()
    if not api: return None
    if not api.startswith("pyAether."): api = "pyAether." + api
    return api

def load_eval_tasks(path):
    tasks = load_jsonl(path)
    result = []
    for t in tasks:
        meta = t.get("metadata", {})
        apis = set()
        for a in meta.get("apis_used", []):
            na = norm_api(a)
            if na: apis.add(na)
        result.append({
            "task_id": t.get("task_id", ""),
            "scenario": meta.get("scenario", "Unknown"),
            "category": meta.get("category", "Unknown"),
            "apis_used": sorted(apis),
            "num_apis": len(apis),
        })
    return result

def load_sft_apis(path, max_records=None):
    apis = set()
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                rec = json.loads(line)
                for a in rec.get("api_used", []):
                    na = norm_api(a)
                    if na: apis.add(na)
                count += 1
                if max_records and count >= max_records: break
            except json.JSONDecodeError: pass
    return apis, count

def load_api_kb_names(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    names = set()
    if isinstance(data, dict):
        for key, val in data.items():
            # Keys are short API names (e.g., "aeAddDesignMapping")
            if key:
                na = norm_api(key)
                if na: names.add(na)
            # Also check api_name field inside value (may have pyAether. prefix)
            if isinstance(val, dict):
                an = val.get("api_name", "")
                if an:
                    na = norm_api(an)
                    if na: names.add(na)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                an = item.get("api_name", "")
                if an:
                    na = norm_api(an)
                    if na: names.add(na)
    return names

def extract_apis_from_text(text):
    if not text: return set()
    return set("pyAether." + m for m in re.findall(r'pyAether\.(\w+)', text))

def load_sft_apis_from_text(path, max_records=None):
    apis = set()
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                rec = json.loads(line)
                found = extract_apis_from_text(rec.get("prompt","")) | extract_apis_from_text(rec.get("completion",""))
                apis.update(found)
                count += 1
                if max_records and count >= max_records: break
            except json.JSONDecodeError: pass
    return apis, count

def analyze_coverage(eval_tasks, sft_v1_apis, sft_v2_apis, api_kb_names):
    eval_all_apis = set()
    for t in eval_tasks:
        eval_all_apis.update(t["apis_used"])
    sft_union = sft_v1_apis | sft_v2_apis
    sft_v1_cov = eval_all_apis & sft_v1_apis
    sft_v2_cov = eval_all_apis & sft_v2_apis
    sft_union_cov = eval_all_apis & sft_union
    kb_cov = eval_all_apis & api_kb_names
    missing_sft = eval_all_apis - sft_union
    missing_kb = eval_all_apis - api_kb_names
    missing_both = eval_all_apis - (sft_union | api_kb_names)
    per_task = []
    for t in eval_tasks:
        ta = set(t["apis_used"])
        uc = ta & sft_union; kc = ta & api_kb_names; ac = ta & (sft_union | api_kb_names)
        per_task.append({
            "task_id": t["task_id"], "scenario": t["scenario"], "category": t["category"],
            "num_apis": t["num_apis"],
            "sft_union_cov": len(uc), "kb_cov": len(kc), "all_cov": len(ac),
            "sft_pct": round(100*len(uc)/max(t["num_apis"],1),1),
            "kb_pct": round(100*len(kc)/max(t["num_apis"],1),1),
            "all_pct": round(100*len(ac)/max(t["num_apis"],1),1),
            "missing_sft": sorted(ta - sft_union),
            "missing_kb": sorted(ta - api_kb_names),
            "missing_all": sorted(ta - (sft_union | api_kb_names)),
        })
    sc_stats = defaultdict(lambda: {"n":0,"apis":0,"sft":0,"kb":0,"all":0,"fs":0,"fk":0,"fa":0})
    for pt in per_task:
        d = sc_stats[pt["scenario"]]
        d["n"] += 1; d["apis"] += pt["num_apis"]
        d["sft"] += pt["sft_union_cov"]; d["kb"] += pt["kb_cov"]; d["all"] += pt["all_cov"]
        if pt["sft_pct"]==100: d["fs"] += 1
        if pt["kb_pct"]==100: d["fk"] += 1
        if pt["all_pct"]==100: d["fa"] += 1
    cat_stats = defaultdict(lambda: {"n":0,"apis":0,"sft":0,"kb":0,"all":0,"fs":0,"fk":0,"fa":0})
    for pt in per_task:
        d = cat_stats[pt["category"]]
        d["n"] += 1; d["apis"] += pt["num_apis"]
        d["sft"] += pt["sft_union_cov"]; d["kb"] += pt["kb_cov"]; d["all"] += pt["all_cov"]
        if pt["sft_pct"]==100: d["fs"] += 1
        if pt["kb_pct"]==100: d["fk"] += 1
        if pt["all_pct"]==100: d["fa"] += 1
    eval_api_cnt = Counter()
    for t in eval_tasks:
        for api in t["apis_used"]: eval_api_cnt[api] += 1
    ms_ranked = sorted([(a,c) for a,c in eval_api_cnt.items() if a in missing_sft], key=lambda x:-x[1])
    mk_ranked = sorted([(a,c) for a,c in eval_api_cnt.items() if a in missing_kb], key=lambda x:-x[1])
    return {
        "eval_total_apis": len(eval_all_apis),
        "sft_v1_total": len(sft_v1_apis), "sft_v2_total": len(sft_v2_apis),
        "kb_total": len(api_kb_names),
        "sft_v1_covered": len(sft_v1_cov), "sft_v2_covered": len(sft_v2_cov),
        "sft_union_covered": len(sft_union_cov), "kb_covered": len(kb_cov),
        "missing_sft": sorted(missing_sft), "missing_kb": sorted(missing_kb),
        "missing_both": sorted(missing_both),
        "missing_sft_count": len(missing_sft), "missing_kb_count": len(missing_kb),
        "missing_both_count": len(missing_both),
        "per_task": per_task,
        "scenario_stats": dict(sc_stats), "category_stats": dict(cat_stats),
        "missing_sft_ranked": ms_ranked, "missing_kb_ranked": mk_ranked,
    }

def generate_html(results, n_tasks, v1c, v2c, smoke=False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    n = results["eval_total_apis"]; sc = results["sft_union_covered"]; kc = results["kb_covered"]
    ms = results["missing_sft_count"]; mk = results["missing_kb_count"]; mb = results["missing_both_count"]
    sp = round(100*sc/max(n,1),1); kp = round(100*kc/max(n,1),1)
    tfs = sum(1 for pt in results["per_task"] if pt["sft_pct"]==100)
    tfk = sum(1 for pt in results["per_task"] if pt["kb_pct"]==100)
    tfa = sum(1 for pt in results["per_task"] if pt["all_pct"]==100)
    def cl(v): return "good" if v>=80 else ("warn" if v>=50 else "bad")
    sr = ""
    for s, d in sorted(results["scenario_stats"].items()):
        sr += f"<tr><td>{s}</td><td>{d['n']}</td><td>{d['apis']}</td><td>{d['sft']}({round(100*d['sft']/max(d['apis'],1),1)}%)</td><td>{d['kb']}({round(100*d['kb']/max(d['apis'],1),1)}%)</td><td>{d['all']}({round(100*d['all']/max(d['apis'],1),1)}%)</td><td>{d['fs']}</td><td>{d['fk']}</td><td>{d['fa']}</td></tr>"
    cr = ""
    for c, d in sorted(results["category_stats"].items()):
        cr += f"<tr><td>{c}</td><td>{d['n']}</td><td>{d['apis']}</td><td>{d['sft']}({round(100*d['sft']/max(d['apis'],1),1)}%)</td><td>{d['kb']}({round(100*d['kb']/max(d['apis'],1),1)}%)</td><td>{d['all']}({round(100*d['all']/max(d['apis'],1),1)}%)</td><td>{d['fs']}</td><td>{d['fk']}</td><td>{d['fa']}</td></tr>"
    msr = "".join(f"<tr><td><code>{a}</code></td><td>{c}</td></tr>" for a,c in results["missing_sft_ranked"][:30]) or "<tr><td colspan=2>All covered</td></tr>"
    mkr = "".join(f"<tr><td><code>{a}</code></td><td>{c}</td></tr>" for a,c in results["missing_kb_ranked"][:30]) or "<tr><td colspan=2>All covered</td></tr>"
    worst = sorted(results["per_task"], key=lambda x:x["all_pct"])[:20]
    wr = ""
    for pt in worst:
        m = ", ".join(pt["missing_all"][:5])
        if len(pt["missing_all"])>5: m += f"(+{len(pt['missing_all'])-5})"
        wr += f"<tr><td>{pt['task_id']}</td><td>{pt['scenario']}</td><td>{pt['num_apis']}</td><td>{pt['sft_pct']}%</td><td>{pt['kb_pct']}%</td><td>{pt['all_pct']}%</td><td><code>{m}</code></td></tr>"
    return _html_template(now, n, sc, kc, sp, kp, ms, mk, mb, tfs, tfk, tfa, n_tasks, v1c, v2c, sr, cr, msr, mkr, wr, cl, smoke)

def _html_template(now, n, sc, kc, sp, kp, ms, mk, mb, tfs, tfk, tfa, nt, v1c, v2c, sr, cr, msr, mkr, wr, cl, smoke):
    sn = " <span style='color:red'>(SMOKE)</span>" if smoke else ""
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>R98 API Coverage Gap</title>
<style>body{{font-family:-apple-system,sans-serif;max-width:1200px;margin:0 auto;padding:20px;line-height:1.6;color:#333}}
h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}h2{{color:#2874a6;margin-top:30px}}
table{{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}th{{background:#ebf5fb;font-weight:600}}
tr:nth-child(even){{background:#f9f9f9}}.c{{display:inline-block;background:#f0f3f4;border-radius:8px;padding:15px 20px;margin:5px;min-width:200px}}
.c h3{{margin:0 0 5px;font-size:14px;color:#7f8c8d}}.c .v{{font-size:28px;font-weight:bold;color:#2c3e50}}.c .s{{font-size:12px;color:#95a5a6}}
.good{{color:#27ae60}}.warn{{color:#e67e22}}.bad{{color:#e74c3c}}code{{background:#f4f4f4;padding:2px 6px;border-radius:3px;font-size:13px}}
.note{{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:10px 0}}.wb{{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:10px 0}}</style></head>
<body><h1>R98: Training-Eval API Coverage Gap Analysis</h1><p><small>{now}{sn}</small></p>
<div class="note"><b>Motivation</b>: R97 showed 0% API coverage even with 27B. Do the 158 eval APIs appear in training data?</div>
<h2>1. Summary</h2>
<div class="c"><h3>Eval Tasks</h3><div class="v">{nt}</div></div>
<div class="c"><h3>Eval APIs</h3><div class="v">{n}</div></div>
<div class="c"><h3>SFT Coverage</h3><div class="v {cl(sp)}">{sc}/{n} ({sp}%)</div><div class="s">v1:{v1c} v2:{v2c}</div></div>
<div class="c"><h3>KB Coverage</h3><div class="v {cl(kp)}">{kc}/{n} ({kp}%)</div><div class="s">API_INFO_MERGED_V3</div></div>
<div class="c"><h3>Missing Both</h3><div class="v {mb==0 and 'good' or 'bad'}">{mb}</div></div>
<h2>2. Per-Task Full Coverage</h2>
<div class="c"><h3>SFT Full</h3><div class="v {cl(tfs/nt*100)}">{tfs}/{nt}</div></div>
<div class="c"><h3>KB Full</h3><div class="v {cl(tfk/nt*100)}">{tfk}/{nt}</div></div>
<div class="c"><h3>Union Full</h3><div class="v {cl(tfa/nt*100)}">{tfa}/{nt}</div></div>
<h2>3. By Scenario</h2><table><tr><th>Scenario</th><th>Tasks</th><th>APIs</th><th>SFT</th><th>KB</th><th>Union</th><th>SF</th><th>KF</th><th>UF</th></tr>{sr}</table>
<h2>4. By Category</h2><table><tr><th>Category</th><th>Tasks</th><th>APIs</th><th>SFT</th><th>KB</th><th>Union</th><th>SF</th><th>KF</th><th>UF</th></tr>{cr}</table>
<h2>5. Missing from SFT (Top 30)</h2><div class="wb">APIs needed by eval but absent from SFT corpus.</div><table><tr><th>API</th><th>In N tasks</th></tr>{msr}</table>
<h2>6. Missing from KB (Top 30)</h2><div class="wb">APIs needed by eval but absent from API knowledge base.</div><table><tr><th>API</th><th>In N tasks</th></tr>{mkr}</table>
<h2>7. Worst 20 Tasks</h2><table><tr><th>Task</th><th>Scenario</th><th>APIs</th><th>SFT%</th><th>KB%</th><th>Union%</th><th>Missing</th></tr>{wr}</table>
<h2>8. Conclusions</h2><div class="note"><ol>
<li><b>SFT: {sp}%</b> ({sc}/{n}) — {ms} missing</li>
<li><b>KB: {kp}%</b> ({kc}/{n}) — {mk} missing</li>
<li><b>Both missing: {mb}</b> — cannot be injected</li>
<li><b>Full coverage: SFT {tfs}, KB {tfk}, Union {tfa}</b> of {nt}</li>
<li><b>Implications:</b><ul>
<li>High SFT → annealing+SFT boost API knowledge → M1(50%) feasible</li>
<li>High KB, low SFT → add KB API docs to SFT synthesis</li>
<li>Missing both → source from eda_fastmcp codebase</li></ul></li></ol></div>
<h2>9. Limitations</h2><ul><li>API coverage != Pass@1</li><li>api_used may be incomplete</li><li>Exact match may miss variants</li><li>No contamination (API names only)</li></ul>
<h2>10. Related</h2><ul><li><b>R97</b>: 0% API coverage → R98 checks training data gap</li><li><b>R89</b>: DS success patterns → R98 verifies training presence</li><li><b>P0 D2</b>: Tool frequency → training-side evidence</li><li><b>P1-d</b>: PyAether corpus → KB coverage validation</li></ul>
<p><small>Zero-GPU analysis. API coverage is necessary but not sufficient.</small></p></body></html>"""

def main():
    ap = argparse.ArgumentParser(description="R98: Training-Eval API Coverage Gap Analysis")
    ap.add_argument("--html", action="store_true", help="Generate HTML report")
    ap.add_argument("--json", action="store_true", help="Output JSON results")
    ap.add_argument("--verbose", action="store_true", help="Verbose output")
    ap.add_argument("--smoke", action="store_true", help="Smoke test (5 tasks, 100 SFT records)")
    ap.add_argument("--text-scan", action="store_true", help="Also scan full text of SFT for API mentions")
    args = ap.parse_args()
    print("R98: Training-Eval API Coverage Gap Analysis")
    print("=" * 60)
    print(f"\n[1] Loading eval tasks from {EVAL_DATASET}...")
    if not EVAL_DATASET.exists():
        print(f"ERROR: {EVAL_DATASET} not found"); sys.exit(1)
    eval_tasks = load_eval_tasks(EVAL_DATASET)
    if args.smoke: eval_tasks = eval_tasks[:5]; print("   SMOKE: first 5 tasks")
    print(f"   Loaded {len(eval_tasks)} tasks")
    eval_apis = set()
    for t in eval_tasks: eval_apis.update(t["apis_used"])
    print(f"   Unique eval APIs: {len(eval_apis)}")
    print(f"\n[2] Loading SFT corpus APIs...")
    v1a, v1c, v2a, v2c = set(), 0, set(), 0
    mr = 100 if args.smoke else None
    if SFT_V1.exists():
        v1a, v1c = load_sft_apis(SFT_V1, max_records=mr)
        print(f"   SFT v1: {v1c} records, {len(v1a)} APIs")
    else: print(f"   SFT v1 not found: {SFT_V1}")
    if SFT_V2.exists():
        v2a, v2c = load_sft_apis(SFT_V2, max_records=mr)
        print(f"   SFT v2: {v2c} records, {len(v2a)} APIs")
    else: print(f"   SFT v2 not found: {SFT_V2}")
    if args.text_scan and not args.smoke:
        print(f"\n[2b] Text-scanning SFT corpus...")
        if SFT_V1.exists():
            t1, _ = load_sft_apis_from_text(SFT_V1, max_records=mr)
            extra = t1 - v1a
            if extra: print(f"   Text scan: {len(extra)} extra APIs in v1"); v1a.update(t1)
        if SFT_V2.exists():
            t2, _ = load_sft_apis_from_text(SFT_V2, max_records=mr); v2a.update(t2)
    print(f"\n[3] Loading API KB from {API_KB}...")
    if not API_KB.exists():
        print(f"ERROR: {API_KB} not found"); sys.exit(1)
    kb = load_api_kb_names(API_KB)
    print(f"   KB: {len(kb)} APIs")
    print(f"\n[4] Computing coverage...")
    res = analyze_coverage(eval_tasks, v1a, v2a, kb)
    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    print(f"  Eval tasks:          {len(eval_tasks)}")
    print(f"  Eval unique APIs:    {res['eval_total_apis']}")
    print(f"  SFT v1 APIs:         {res['sft_v1_total']}")
    print(f"  SFT v2 APIs:         {res['sft_v2_total']}")
    print(f"  KB APIs:             {res['kb_total']}")
    print(f"  SFT union covered:   {res['sft_union_covered']}/{res['eval_total_apis']} ({round(100*res['sft_union_covered']/max(res['eval_total_apis'],1),1)}%)")
    print(f"  KB covered:          {res['kb_covered']}/{res['eval_total_apis']} ({round(100*res['kb_covered']/max(res['eval_total_apis'],1),1)}%)")
    print(f"  Missing from SFT:    {res['missing_sft_count']}")
    print(f"  Missing from KB:     {res['missing_kb_count']}")
    print(f"  Missing from both:   {res['missing_both_count']}")
    tfs = sum(1 for pt in res["per_task"] if pt["sft_pct"]==100)
    tfk = sum(1 for pt in res["per_task"] if pt["kb_pct"]==100)
    tfa = sum(1 for pt in res["per_task"] if pt["all_pct"]==100)
    print(f"  Tasks full SFT:      {tfs}/{len(eval_tasks)}")
    print(f"  Tasks full KB:       {tfk}/{len(eval_tasks)}")
    print(f"  Tasks full union:    {tfa}/{len(eval_tasks)}")
    if args.verbose:
        print(f"\n  Missing from SFT (top 10):")
        for a, c in res["missing_sft_ranked"][:10]: print(f"    {a} (in {c} tasks)")
        print(f"\n  Missing from KB (top 10):")
        for a, c in res["missing_kb_ranked"][:10]: print(f"    {a} (in {c} tasks)")
        print(f"\n  Per-scenario:")
        for s, d in sorted(res["scenario_stats"].items()):
            print(f"    {s}: {d['n']} tasks, SFT {d['sft']}/{d['apis']}, KB {d['kb']}/{d['apis']}")
    if args.json:
        jp = RUN_DIR / "r98_api_coverage_gap.json"
        out = {"analysis": "R98 API Coverage Gap", "timestamp": datetime.now().isoformat(),
               "smoke": args.smoke, "eval_tasks": len(eval_tasks), "sft_v1_count": v1c,
               "sft_v2_count": v2c, "results": res}
        with open(jp, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\n  JSON: {jp} ({jp.stat().st_size/1024:.1f} KB)")
    if args.html:
        hp = REPORTS_DIR / "report_posttrain_r98_api_coverage_gap_zh.html"
        with open(hp, "w", encoding="utf-8") as f: f.write(generate_html(res, len(eval_tasks), v1c, v2c, smoke=args.smoke))
        print(f"\n  HTML: {hp} ({hp.stat().st_size/1024:.1f} KB)")
    print(f"\nDone.")

if __name__ == "__main__":
    main()
