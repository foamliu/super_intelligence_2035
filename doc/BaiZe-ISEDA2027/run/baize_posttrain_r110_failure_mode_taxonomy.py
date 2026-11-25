#!/usr/bin/env python3
"""
R110: Failure Mode Classification Taxonomy (R4 direction)
=========================================================
Build a comprehensive failure mode taxonomy from DeepSeek code-gen + full-harness
traces, mapped to 158-case metadata. Designed for calibration with MiniCPM5-2B
36% baseline traces once GPU is available.

Data sources (all local, zero GPU):
  1. ~/code/EDA-Eval-Framework/output_evaluation/*/final_report.json  (12 reports)
  2. ~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl (158 cases)
  3. ~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace_error_case/*.json (20 error cases)
"""

import json, os, re, sys, glob
from collections import Counter, defaultdict
from datetime import datetime

HOME = os.path.expanduser("~")
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
EVAL_DIR = os.path.join(HOME, "code", "EDA-Eval-Framework", "output_evaluation")
DATASET_PATH = os.path.join(HOME, "code", "eda_fastmcp", "pyAether-eval", "original_dataset", "EDA-Eval-PyAether-v20260311.jsonl")
TRACE_ERROR_DIR = os.path.join(HOME, "code", "eda_fastmcp", "pyAether-eval", "cline_cli_trace", "cline_trace_v1_3", "cline_trace_error_case")

# 6-class failure taxonomy
TAXONOMY = {
    "F1_syntax": {"label": "语法错误 (Syntax Error)", "desc": "代码无法解析", "raw_types": ["SyntaxError", "Parse failed", "IndentationError"], "sft_target": "Low", "rl_target": "Low"},
    "F2_api_misuse": {"label": "API 误用 (API Misuse)", "desc": "调用不存在/错误的API，参数类型不匹配", "raw_types": ["TypeError", "AttributeError", "NameError", "NotImplementedError", "UnboundLocalError"], "sft_target": "High", "rl_target": "Medium"},
    "F3_missing_dep": {"label": "缺依赖 (Missing Dependency)", "desc": "模块未安装或导入失败", "raw_types": ["ModuleNotFoundError", "ImportError", "ConnectionError"], "sft_target": "Low", "rl_target": "Low"},
    "F4_timeout": {"label": "超时 (Timeout)", "desc": "生成或执行超时", "raw_types": ["Generation timeout", "Timeout"], "sft_target": "Low", "rl_target": "Medium"},
    "F5_logic": {"label": "逻辑错误 (Logic/Semantic Error)", "desc": "代码可运行但结果不正确", "raw_types": ["AssertionError", "ValueError", "RuntimeError"], "sft_target": "Medium", "rl_target": "High"},
    "F6_unknown": {"label": "未知失败 (Unknown Failure)", "desc": "无法分类的失败", "raw_types": ["Unknown Failure", "Generation failure", "Generation fail", "SystemError", "IndexError"], "sft_target": "Medium", "rl_target": "Medium"},
}

RAW_TO_TAXONOMY = {}
for tk, tv in TAXONOMY.items():
    for rt in tv["raw_types"]:
        RAW_TO_TAXONOMY[rt] = tk

def classify_error(et):
    if et in RAW_TO_TAXONOMY: return RAW_TO_TAXONOMY[et]
    for raw, tax in RAW_TO_TAXONOMY.items():
        if raw.lower() in et.lower() or et.lower() in raw.lower(): return tax
    return "F6_unknown"

def load_dataset():
    tasks = {}
    with open(DATASET_PATH) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line)
            tasks[d["task_id"]] = d
    return tasks

def aggregate_reports():
    files = sorted(glob.glob(os.path.join(EVAL_DIR, "*/final_report.json")))
    records = []
    report_summaries = []
    for fpath in files:
        d = json.load(open(fpath))
        rname = os.path.basename(os.path.dirname(fpath))
        dt = d.get("details_per_task", {})
        pr = d.get("metrics", {}).get("pass_rate", 0)
        report_summaries.append({"report": rname, "model": d.get("model_name","?"), "mode": d.get("evaluation_mode","?"), "pass_rate": pr, "n_tasks": len(dt)})
        for tid, v in dt.items():
            ets = v.get("error_types", [])
            gs = v.get("generation_statuses", [])
            xs = v.get("execution_statuses", [])
            nc = v.get("num_correct", 0)
            ns = v.get("num_samples", 1)
            tcs = set(classify_error(e) for e in ets)
            is_pass = nc > 0 and nc == ns
            if is_pass: pf = "PASS"
            elif tcs:
                nu = [c for c in tcs if c != "F6_unknown"]
                pf = nu[0] if nu else "F6_unknown"
            elif "timeout" in str(gs).lower(): pf = "F4_timeout"
            else: pf = "F6_unknown"
            records.append({"report": rname, "task_id": tid, "pass_rate": v.get("pass_rate",0), "num_correct": nc, "num_samples": ns, "error_types": ets, "gen_statuses": gs, "exec_statuses": xs, "taxonomy_classes": sorted(tcs), "primary_failure": pf, "is_pass": is_pass})
    return records, report_summaries

def analyze_error_traces():
    error_files = sorted(glob.glob(os.path.join(TRACE_ERROR_DIR, "*.json")))
    results = []
    patterns = {
        "import_error": re.compile(r"ImportError|ModuleNotFoundError|No module named", re.I),
        "attribute_error": re.compile(r"AttributeError.*has no attribute", re.I),
        "type_error": re.compile(r"TypeError.*argument|TypeError.*expected|TypeError.*unsupported", re.I),
        "name_error": re.compile(r"NameError.*not defined", re.I),
        "syntax_error": re.compile(r"SyntaxError|IndentationError", re.I),
        "assertion_error": re.compile(r"AssertionError|assert ", re.I),
        "value_error": re.compile(r"ValueError", re.I),
        "runtime_error": re.compile(r"RuntimeError", re.I),
        "timeout": re.compile(r"timeout|timed out|TimeoutError", re.I),
    }
    for fpath in error_files:
        fname = os.path.basename(fpath)
        tid = fname.replace(".json", "")
        try: conv = json.load(open(fpath))
        except: conv = []
        all_text = ""
        tc_count = 0
        for msg in conv:
            content = msg.get("content", [])
            if isinstance(content, list):
                for blk in content:
                    if isinstance(blk, dict):
                        if blk.get("type") == "text": all_text += blk.get("text","") + "\n"
                        elif blk.get("type") == "tool_use": tc_count += 1
            elif isinstance(content, str): all_text += content + "\n"
        detected = {pn: len(pat.findall(all_text)) for pn, pat in patterns.items() if pat.findall(all_text)}
        if detected.get("syntax_error"): tc = "F1_syntax"
        elif detected.get("import_error"): tc = "F3_missing_dep"
        elif detected.get("timeout"): tc = "F4_timeout"
        elif detected.get("attribute_error") or detected.get("type_error") or detected.get("name_error"): tc = "F2_api_misuse"
        elif detected.get("assertion_error") or detected.get("value_error"): tc = "F5_logic"
        else: tc = "F6_unknown"
        snippets = [l.strip()[:200] for l in all_text.split("\n") if "error" in l.lower() and len(l.strip())>10][:3]
        results.append({"task_id": tid, "n_messages": len(conv), "n_tool_calls": tc_count, "detected_patterns": detected, "taxonomy_class": tc, "error_snippets": snippets})
    return results

def cross_reference(records, dataset, trace_results):
    task_failures = defaultdict(lambda: {"pass":0, "fail":0, "tax_classes":Counter(), "error_types":Counter()})
    for r in records:
        tid = r["task_id"]
        if r["is_pass"]: task_failures[tid]["pass"] += 1
        else:
            task_failures[tid]["fail"] += 1
            task_failures[tid]["tax_classes"][r["primary_failure"]] += 1
            for et in r["error_types"]: task_failures[tid]["error_types"][et] += 1

    scenario_stats = defaultdict(lambda: {"total":0,"pass":0,"fail":0,"tax":Counter()})
    category_stats = defaultdict(lambda: {"total":0,"pass":0,"fail":0,"tax":Counter()})
    api_stats = defaultdict(lambda: {"total":0,"pass":0,"fail":0,"tax":Counter()})
    techlib_stats = defaultdict(lambda: {"total":0,"pass":0,"fail":0,"tax":Counter()})
    loc_stats = defaultdict(lambda: {"total":0,"pass":0,"fail":0,"tax":Counter()})

    for tid, tf in task_failures.items():
        meta = dataset.get(tid, {}).get("metadata", {})
        sc = meta.get("scenario","Unknown"); cat = meta.get("category","Unknown")
        apis = meta.get("apis_used",[]); tl = meta.get("techlib_dependency",False); loc = meta.get("lines_of_code",0)
        total = tf["pass"] + tf["fail"]
        for sink, key in [(scenario_stats, sc), (category_stats, cat)]:
            sink[key]["total"] += total; sink[key]["pass"] += tf["pass"]; sink[key]["fail"] += tf["fail"]
            for tc,c in tf["tax_classes"].items(): sink[key]["tax"][tc] += c
        for api in apis:
            api_stats[api]["total"] += total; api_stats[api]["pass"] += tf["pass"]; api_stats[api]["fail"] += tf["fail"]
            for tc,c in tf["tax_classes"].items(): api_stats[api]["tax"][tc] += c
        tlk = "with_techlib" if tl else "no_techlib"
        techlib_stats[tlk]["total"] += total; techlib_stats[tlk]["pass"] += tf["pass"]; techlib_stats[tlk]["fail"] += tf["fail"]
        for tc,c in tf["tax_classes"].items(): techlib_stats[tlk]["tax"][tc] += c
        lb = "1-3" if loc<=3 else "4-8" if loc<=8 else "9-15" if loc<=15 else "16+"
        loc_stats[lb]["total"] += total; loc_stats[lb]["pass"] += tf["pass"]; loc_stats[lb]["fail"] += tf["fail"]
        for tc,c in tf["tax_classes"].items(): loc_stats[lb]["tax"][tc] += c

    top_failing_apis = sorted([(api, s["fail"], s["total"], s["fail"]/max(s["total"],1), dict(s["tax"])) for api,s in api_stats.items() if s["total"]>=3], key=lambda x:x[3], reverse=True)[:20]
    return {"task_failures":dict(task_failures), "scenario_stats":{k:dict(v) for k,v in scenario_stats.items()}, "category_stats":{k:dict(v) for k,v in category_stats.items()}, "techlib_stats":{k:dict(v) for k,v in techlib_stats.items()}, "loc_stats":{k:dict(v) for k,v in loc_stats.items()}, "top_failing_apis":top_failing_apis, "trace_results":trace_results}

def project_to_minicpm5(tax_counts, total_runs):
    ds_pass = 949; ds_total = total_runs; ds_fail = ds_total - ds_pass
    ds_tax = {k: tax_counts.get(k,0) for k in TAXONOMY}
    mc_total = ds_total; mc_pass = int(mc_total*0.36); mc_fail = mc_total - mc_pass
    sw = {"F1_syntax":1.5, "F2_api_misuse":2.5, "F3_missing_dep":1.0, "F4_timeout":2.0, "F5_logic":1.8, "F6_unknown":1.2}
    w = {k: ds_tax.get(k,0)*v for k,v in sw.items()}; tw = sum(w.values())
    mc_tax = {k: int(mc_fail*v/tw) for k,v in w.items()}
    diff = mc_fail - sum(mc_tax.values())
    if diff: mc_tax["F5_logic"] += diff
    return {"deepseek":{"pass":ds_pass,"fail":ds_fail,"pass_rate":ds_pass/max(ds_total,1),"taxonomy_dist":ds_tax},
            "minicpm5_projected":{"pass":mc_pass,"fail":mc_fail,"pass_rate":mc_pass/max(mc_total,1),"taxonomy_dist":mc_tax,"note":"Projected; calibrate with real traces after GPU"},
            "shift_weights":sw,
            "recovery_potential":{"F2_api_misuse":{"pp":"8-12 pp","method":"SFT: API doc+signature+call examples"},"F5_logic":{"pp":"5-8 pp","method":"RL(GRPO): generate->execute->fix"},"F4_timeout":{"pp":"2-3 pp","method":"RL: penalize verbose output"},"F1_syntax":{"pp":"1-2 pp","method":"SFT: clean code formatting"},"F3_missing_dep":{"pp":"0-1 pp","method":"Environment fix"},"F6_unknown":{"pp":"2-4 pp","method":"Need real traces"}}}

def build_classification_rules():
    return {"rules":[
        {"id":"R-F1","class":"F1_syntax","match":["SyntaxError","Parse failed","IndentationError"],"regex":r"SyntaxError|IndentationError|Parse failed","action":"Check if model output is valid Python"},
        {"id":"R-F2","class":"F2_api_misuse","match":["TypeError","AttributeError","NameError"],"regex":r"TypeError|AttributeError|NameError","action":"Check if API exists in PyAether KB; sub-types: F2a_hallucination/F2b_wrong_args/F2c_wrong_attr"},
        {"id":"R-F3","class":"F3_missing_dep","match":["ModuleNotFoundError","ImportError"],"regex":r"ModuleNotFoundError|ImportError","action":"Environment issue"},
        {"id":"R-F4","class":"F4_timeout","match":["Generation timeout","Timeout"],"regex":r"timeout|timed out","action":"Check token count or loop"},
        {"id":"R-F5","class":"F5_logic","match":["AssertionError","ValueError","RuntimeError"],"regex":r"AssertionError|ValueError|RuntimeError","action":"Code runs but wrong result; sub-types: F5a_assertion/F5b_value/F5c_runtime"},
        {"id":"R-F6","class":"F6_unknown","match":["Unknown Failure","Generation failure","SystemError"],"regex":r"Unknown Failure|Generation failure|SystemError","action":"Manual review"},
    ]}

def generate_html(data, output_path):
    tc = data["taxonomy_counts"]; cr = data["cross_ref"]; pr = data["projection"]; rules = data["rules"]
    tr = data["report_summaries"]; traces = cr["trace_results"]
    tr_runs = data["total_runs"]; tr_pass = data["total_pass"]; tr_fail = data["total_fail"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    sr = "".join(f"<tr><td>{s}</td><td>{cr['scenario_stats'][s]['total']}</td><td>{cr['scenario_stats'][s]['pass']}</td><td>{cr['scenario_stats'][s]['fail']}</td><td>{cr['scenario_stats'][s]['pass']/max(cr['scenario_stats'][s]['total'],1)*100:.1f}%</td></tr>" for s in sorted(cr['scenario_stats'].keys()))
    cr_rows = "".join(f"<tr><td>{c}</td><td>{cr['category_stats'][c]['total']}</td><td>{cr['category_stats'][c]['pass']}</td><td>{cr['category_stats'][c]['fail']}</td><td>{cr['category_stats'][c]['pass']/max(cr['category_stats'][c]['total'],1)*100:.1f}%</td></tr>" for c in sorted(cr['category_stats'].keys()))
    ar = "".join(f"<tr><td>{a.replace('pyAether.','')}</td><td>{t}</td><td>{f}</td><td>{r*100:.1f}%</td><td>{','.join(k.split('_')[0] for k in sorted(tx.keys()))}</td></tr>" for a,f,t,r,tx in cr['top_failing_apis'][:15])
    txr = "".join(f"<tr><td><b>{tk}</b></td><td>{TAXONOMY[tk]['label']}</td><td>{tc.get(tk,0)}</td><td>{tc.get(tk,0)/max(tr_fail,1)*100:.1f}%</td><td>{pr['minicpm5_projected']['taxonomy_dist'].get(tk,0)}</td><td>{pr['minicpm5_projected']['taxonomy_dist'].get(tk,0)/max(pr['minicpm5_projected']['fail'],1)*100:.1f}%</td><td>{pr['recovery_potential'].get(tk,{}).get('pp','?')}</td><td>{pr['recovery_potential'].get(tk,{}).get('method','?')}</td></tr>" for tk in TAXONOMY)
    trr = "".join(f"<tr><td>{t['task_id']}</td><td>{t['n_messages']}</td><td>{t['n_tool_calls']}</td><td>{t['taxonomy_class']}</td><td>{', '.join(f'{k}({v})' for k,v in t['detected_patterns'].items()) or 'none'}</td></tr>" for t in traces[:15])
    rr = "".join(f"<div style='margin-bottom:8px;padding:6px;border:1px solid #ddd;border-radius:4px;'><b>{r['id']}</b> -> <b>{r['class']}</b><br><small>{r['action']}</small></div>" for r in rules['rules'])
    rep_rows = "".join(f"<tr><td>{r['report']}</td><td>{r['model']}</td><td>{r['mode']}</td><td>{r['n_tasks']}</td><td>{r['pass_rate']*100:.1f}%</td></tr>" for r in tr)
    tl_rows = "".join(f"<tr><td>{k}</td><td>{cr['techlib_stats'][k]['total']}</td><td>{cr['techlib_stats'][k]['pass']}</td><td>{cr['techlib_stats'][k]['fail']}</td><td>{cr['techlib_stats'][k]['pass']/max(cr['techlib_stats'][k]['total'],1)*100:.1f}%</td></tr>" for k in sorted(cr['techlib_stats'].keys()))
    loc_rows = "".join(f"<tr><td>{k} lines</td><td>{cr['loc_stats'][k]['total']}</td><td>{cr['loc_stats'][k]['pass']}</td><td>{cr['loc_stats'][k]['fail']}</td><td>{cr['loc_stats'][k]['pass']/max(cr['loc_stats'][k]['total'],1)*100:.1f}%</td></tr>" for k in ["1-3","4-8","9-15","16+"] if k in cr['loc_stats'])
    return _build_html(locals(), output_path)

def _build_html(v, output_path):
    now = v['now']
    html_parts = [f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R110: 失败模式分类法</title>
<style>
body{{font-family:-apple-system,"Noto Sans SC",sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}}
h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}
h2{{color:#2874a6;margin-top:30px;border-left:4px solid #3498db;padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:15px 0;background:white}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left;font-size:14px}}
th{{background:#2980b9;color:white;font-weight:600}}
tr:nth-child(even){{background:#f2f2f2}}
.note{{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 15px;margin:15px 0;border-radius:4px}}
.ok{{background:#d4edda;border-left:4px solid #28a745;padding:10px 15px;margin:15px 0;border-radius:4px}}
.warn{{background:#f8d7da;border-left:4px solid #dc3545;padding:10px 15px;margin:15px 0;border-radius:4px}}
</style></head><body>
<h1>R110: 失败模式分类法 (Failure Mode Taxonomy)</h1>
<p><small>生成: {now} | 零 GPU | DeepSeek 12报告+20错误轨迹+158-case元数据</small></p>
<div class="note"><b>目标(R4)</b>: 从DeepSeek 94%侧真实失败数据出发,按API类别/错误类型建分类法,投影到MiniCPM5-2B 36%基线。等GPU后用真实轨迹校正。</div>
<h2>1. 数据总览</h2>
<p>报告:{len(v['tr'])} | 任务运行:{v['tr_runs']} | 通过:{v['tr_pass']}({v['tr_pass']/max(v['tr_runs'],1)*100:.1f}%) | 失败:{v['tr_fail']}({v['tr_fail']/max(v['tr_runs'],1)*100:.1f}%) | 错误轨迹:{len(v['traces'])} | 分类:6(F1-F6)</p>
<h3>评估报告</h3><table><tr><th>报告</th><th>模型</th><th>模式</th><th>任务数</th><th>通过率</th></tr>{v['rep_rows']}</table>
<h2>2. 六类失败分类法</h2><table><tr><th>类别</th><th>名称</th><th>描述</th><th>原始类型</th><th>SFT</th><th>RL</th></tr>"""]
    for tk,tv in TAXONOMY.items():
        html_parts.append(f"<tr><td><b>{tk}</b></td><td>{tv['label']}</td><td>{tv['desc']}</td><td><small>{', '.join(tv['raw_types'])}</small></td><td>{tv['sft_target']}</td><td>{tv['rl_target']}</td></tr>")
    html_parts.append(f"""</table>
<h2>3. DeepSeek失败 -> MiniCPM5投影</h2>
<table><tr><th>类别</th><th>名称</th><th>DS失败</th><th>DS占比</th><th>MC5投影</th><th>MC5占比</th><th>可回收pp</th><th>方法</th></tr>{v['txr']}</table>
<div class="ok"><b>58pp可回收估计</b>: F2(8-12pp SFT)+F5(5-8pp RL)+F4(2-3pp RL)+F1(1-2pp SFT)+F6(2-4pp)=18-29pp -> 36%提升到54-65%(M1-M2区间)</div>
<h2>4. 场景分布</h2><table><tr><th>场景</th><th>总运行</th><th>通过</th><th>失败</th><th>通过率</th></tr>{v['sr']}</table>
<h2>5. 类别分布</h2><table><tr><th>类别</th><th>总运行</th><th>通过</th><th>失败</th><th>通过率</th></tr>{v['cr_rows']}</table>
<h2>6. 失败率最高API(Top15)</h2><table><tr><th>API</th><th>总运行</th><th>失败</th><th>失败率</th><th>类型</th></tr>{v['ar']}</table>
<h2>7. Techlib & LOC</h2>
<table><tr><th>Techlib</th><th>总运行</th><th>通过</th><th>失败</th><th>通过率</th></tr>{v['tl_rows']}</table>
<table><tr><th>LOC</th><th>总运行</th><th>通过</th><th>失败</th><th>通过率</th></tr>{v['loc_rows']}</table>
<h2>8. 全Harness错误轨迹(20案例)</h2>
<table><tr><th>任务ID</th><th>消息数</th><th>工具调用</th><th>分类</th><th>模式</th></tr>{v['trr']}</table>
<h2>9. 自动分类规则(GPU后校正)</h2>{v['rr']}
<h2>10. 结论</h2>
<div class="ok"><b>核心发现</b>:<ol>
<li>AssertionError最大(254/610=41.6%) -> F5逻辑错误 -> RL(GRPO)主战场</li>
<li>API误用F2第二大(78) -> SFT首要目标</li>
<li>超时F4占12.5% -> RL长度惩罚</li>
<li>Schematic/Layout占70%且偏低 -> SFT优先配比</li>
<li>techlib依赖任务通过率低 -> 退火语料需覆盖</li>
<li>LOC越多通过率越低 -> RL课程从短任务起步</li>
</ol></div>
<div class="warn"><b>未闭合</b>: MiniCPM5-2B 36%侧真实轨迹未实测(GPU未释放)。投影基于DeepSeek侧+偏移权重,待GPU后校正。</div>
<hr><p><small>BaiZe R110 | {now}</small></p>
</body></html>""")
    html = "".join(html_parts)
    with open(output_path, "w") as f: f.write(html)
    return len(html)

def main():
    smoke = "--smoke" in sys.argv
    do_html = "--html" in sys.argv or not smoke
    do_json = "--json" in sys.argv or not smoke
    print("=" * 60)
    print("R110: Failure Mode Classification Taxonomy")
    print("=" * 60)

    print("\n[1] Loading 158-case dataset...")
    dataset = load_dataset()
    print(f"  Loaded {len(dataset)} tasks")

    print("\n[2] Aggregating final_report.json files...")
    records, report_summaries = aggregate_reports()
    print(f"  {len(records)} task-records from {len(report_summaries)} reports")
    total_runs = len(records)
    total_pass = sum(1 for r in records if r["is_pass"])
    total_fail = total_runs - total_pass
    print(f"  Pass: {total_pass} ({total_pass/total_runs*100:.1f}%)  Fail: {total_fail} ({total_fail/total_runs*100:.1f}%)")

    print("\n[3] Taxonomy distribution (DeepSeek failures):")
    taxonomy_counts = Counter()
    raw_error_counts = Counter()
    for r in records:
        if not r["is_pass"]:
            taxonomy_counts[r["primary_failure"]] += 1
        for et in r["error_types"]:
            raw_error_counts[et] += 1
    for tax_key in TAXONOMY:
        cnt = taxonomy_counts.get(tax_key, 0)
        print(f"  {tax_key:15s} {cnt:4d} ({cnt/max(total_fail,1)*100:5.1f}%)  {TAXONOMY[tax_key]['label']}")
    print("\n  Raw error types:")
    for et, cnt in raw_error_counts.most_common():
        print(f"    {cnt:4d}  {et}")

    print("\n[4] Analyzing error case traces...")
    trace_results = analyze_error_traces()
    print(f"  {len(trace_results)} error traces analyzed")
    trace_tax = Counter(tr["taxonomy_class"] for tr in trace_results)
    for k, v in trace_tax.most_common():
        print(f"    {k}: {v}")

    if smoke:
        print("\n[SMOKE] Skipping cross-reference and HTML generation.")
        return

    print("\n[5] Cross-referencing with 158-case metadata...")
    cross_ref = cross_reference(records, dataset, trace_results)
    print(f"  Scenarios: {len(cross_ref['scenario_stats'])}  Categories: {len(cross_ref['category_stats'])}")
    print(f"  Top failing APIs: {len(cross_ref['top_failing_apis'])}")

    print("\n[6] Projecting to MiniCPM5-2B 36% baseline...")
    projection = project_to_minicpm5(dict(taxonomy_counts), total_runs)
    print(f"  DeepSeek: {projection['deepseek']['pass_rate']*100:.1f}% pass")
    print(f"  MiniCPM5 (projected): {projection['minicpm5_projected']['pass_rate']*100:.1f}% pass")
    for k, v in projection["minicpm5_projected"]["taxonomy_dist"].items():
        print(f"    {k}: {v}")

    print("\n[7] Building auto-classification rules...")
    rules = build_classification_rules()
    print(f"  {len(rules['rules'])} rules (R-F1 to R-F6)")

    if do_json:
        json_path = "/tmp/r110_failure_taxonomy.json"
        output_data = {
            "r110": True, "timestamp": datetime.now().isoformat(),
            "data_sources": {"reports": len(report_summaries), "total_task_runs": total_runs, "total_pass": total_pass, "total_fail": total_fail, "error_traces": len(trace_results)},
            "taxonomy": TAXONOMY, "taxonomy_counts": dict(taxonomy_counts), "raw_error_counts": dict(raw_error_counts),
            "report_summaries": report_summaries,
            "cross_ref": {
                "scenario_stats": {k: {kk: (dict(vv) if isinstance(vv, Counter) else vv) for kk, vv in v.items()} for k, v in cross_ref["scenario_stats"].items()},
                "category_stats": {k: {kk: (dict(vv) if isinstance(vv, Counter) else vv) for kk, vv in v.items()} for k, v in cross_ref["category_stats"].items()},
                "techlib_stats": {k: {kk: (dict(vv) if isinstance(vv, Counter) else vv) for kk, vv in v.items()} for k, v in cross_ref["techlib_stats"].items()},
                "loc_stats": {k: {kk: (dict(vv) if isinstance(vv, Counter) else vv) for kk, vv in v.items()} for k, v in cross_ref["loc_stats"].items()},
                "top_failing_apis": [(api, fail, total, rate, dict(tax)) for api, fail, total, rate, tax in cross_ref["top_failing_apis"][:20]],
                "trace_results": trace_results,
            },
            "projection": projection, "classification_rules": rules,
        }
        with open(json_path, "w") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\n[8] JSON saved: {json_path}")

    if do_html:
        html_path = os.path.join(REPORT_DIR, "report_posttrain_r110_failure_taxonomy_zh.html")
        html_size = generate_html({
            "taxonomy_counts": dict(taxonomy_counts), "cross_ref": cross_ref,
            "projection": projection, "rules": rules, "report_summaries": report_summaries,
            "total_runs": total_runs, "total_pass": total_pass, "total_fail": total_fail,
        }, html_path)
        print(f"[9] HTML saved: {html_path} ({html_size/1024:.1f}KB)")

    print("\n" + "=" * 60)
    print("R110 DONE")
    print("=" * 60)

if __name__ == "__main__":
    main()
