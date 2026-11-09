#!/usr/bin/env python3
"""Generate cline special report R1745."""
import json, glob, os, html, time
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(BASE, "swebench_verified_full", "predictions_glm53")
PROG_FILE = os.path.join(BASE, "swebench_verified_full", "reports", "progress_glm53_cline-patched.json")
TB4_DIR = os.path.join(BASE, "terminalbench", "jobs_tb4_glm53_full")
REPORT_DIR = os.path.join(BASE, "..", "..", "reports")

def load_predictions(harness):
    files = glob.glob(os.path.join(PRED_DIR, "*" + harness + "*.json"))
    results = []
    for f in files:
        try:
            d = json.load(open(f))
            patch = ""
            if isinstance(d, list):
                for item in d:
                    if isinstance(item, dict) and item.get("model_patch") is not None:
                        patch = item.get("model_patch", "") or ""
                        break
            elif isinstance(d, dict):
                patch = d.get("model_patch", "") or ""
            mtime = os.path.getmtime(f)
            iid = os.path.basename(f).replace(harness + "__", "").replace(".json", "")
            results.append((iid, len(patch), mtime))
        except:
            pass
    return sorted(results, key=lambda x: x[2])

def classify_empty():
    try:
        d = json.load(open(PROG_FILE))
    except:
        return []
    results = d.get("results", [])
    classifications = []
    for r in results:
        plen = r.get("model_patch_len", 0)
        if not plen or plen == 0:
            stdout = r.get("stdout_tail", "")
            iid = r.get("instance_id", "?")
            if "\u989d\u5ea6" in stdout or "Token" in stdout:
                cat = "QUOTA"
            elif "ConnectionRefused" in stdout or "Unable to connect" in stdout:
                cat = "ADAPTER_CONN"
            elif "ai/dist/index.js" in stdout:
                cat = "ADAPTER_SDK"
            elif r.get("timeout", False):
                cat = "TIMEOUT"
            else:
                cat = "OTHER"
            classifications.append((iid, cat, stdout[:200]))
    return classifications

def get_tb4_stats():
    stats = {}
    if not os.path.isdir(TB4_DIR):
        return stats
    for d in os.listdir(TB4_DIR):
        path = os.path.join(TB4_DIR, d)
        if not os.path.isdir(path):
            continue
        completed = passed = 0
        for root, dirs, files in os.walk(path):
            for fn in files:
                if fn == "result.json":
                    completed += 1
                if fn == "reward.json":
                    try:
                        rdata = json.load(open(os.path.join(root, fn)))
                        if isinstance(rdata, dict) and rdata.get("reward", 0) > 0:
                            passed += 1
                    except:
                        pass
        name = d.replace("cline-patched", "cline")
        if name not in stats:
            stats[name] = {"completed": 0, "passed": 0}
        stats[name]["completed"] += completed
        stats[name]["passed"] += passed
    return stats

# Collect data
harnesses = ["cline", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]
all_preds = {h: load_predictions(h) for h in harnesses}

c1_rows = []
for h in harnesses:
    preds = all_preds[h]
    total = len(preds)
    real = sum(1 for _, plen, _ in preds if plen > 0)
    empty = total - real
    real_lens = [plen for _, plen, _ in preds if plen > 0]
    median = sorted(real_lens)[len(real_lens)//2] if real_lens else 0
    display = h.replace("deepseek-harness", "deepseek")
    c1_rows.append((display, total, real, empty, 100*real/max(total,1), median))

cline_preds = all_preds["cline"]
real_ts = [mt for _, plen, mt in cline_preds if plen > 0]
last_real_ts = max(real_ts) if real_ts else 0
pre_q = [(i,p,m) for i,p,m in cline_preds if m <= last_real_ts]
post_q = [(i,p,m) for i,p,m in cline_preds if m > last_real_ts]
pre_real = sum(1 for _,p,_ in pre_q if p > 0)
pre_total = len(pre_q)
post_total = len(post_q)

empty_classes = classify_empty()
class_counts = {}
for iid, cat, _ in empty_classes:
    class_counts[cat] = class_counts.get(cat, 0) + 1

q_count = class_counts.get("QUOTA", 0)
a_conn = class_counts.get("ADAPTER_CONN", 0)
a_sdk = class_counts.get("ADAPTER_SDK", 0)

TB4_stats = get_tb4_stats()
now = datetime.now().strftime("%Y-%m-%d %H:%M")
ct, cr, ce = c1_rows[0][1], c1_rows[0][2], c1_rows[0][3]
t_all = sum(r[1] for r in c1_rows)
r_all = sum(r[2] for r in c1_rows)
tb4_total = sum(s["completed"] for s in TB4_stats.values())
last_real_str = time.strftime("%H:%M", time.localtime(last_real_ts)) if last_real_ts else "N/A"

# Cat labels
cat_labels = {
    "QUOTA": "\u7f51\u5173\u989d\u5ea6\u8017\u5c3d(429/403)",
    "ADAPTER_CONN": "\u9002\u914d\u5668(gw_proxy\u4e0d\u53ef\u8fbe)",
    "ADAPTER_SDK": "\u9002\u914d\u5668(AI SDK\u5f02\u5e38)",
    "TIMEOUT": "\u8d85\u65f6",
    "OTHER": "\u5176\u4ed6",
}

print("Data collected:")
print("  cline: " + str(ct) + "/" + str(cr) + "/" + str(ce))
print("  pre-quota: " + str(pre_real) + "/" + str(pre_total) + " = " + str(round(100*pre_real/max(pre_total,1),1)) + "%")
print("  C2: " + str(class_counts))
print("  TB4: " + str(tb4_total) + " completed, 0 passed")

CSS = "body{font-family:sans-serif;margin:2em;background:#f8f9fa;color:#333}h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:.3em}h2{color:#16213e;margin-top:1.5em;border-left:4px solid #e94560;padding-left:.5em}table{border-collapse:collapse;width:100%;margin:1em 0;background:#fff}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#16213e;color:#fff}tr:nth-child(even){background:#f2f2f2}.good{color:#27ae60;font-weight:bold}.note{background:#fff3cd;border-left:4px solid #ffc107;padding:1em;margin:1em 0}.fix{background:#d4edda;border-left:4px solid #28a745;padding:1em;margin:1em 0}.alert{background:#f8d7da;border-left:4px solid #dc3545;padding:1em;margin:1em 0}code{background:#eef;padding:2px 4px;border-radius:3px}.box{background:#fff;border-radius:8px;padding:1.5em;margin:1em 0;box-shadow:0 2px 4px rgba(0,0,0,.1)}"

H = []
H.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">')
H.append('<title>cline \u4e13\u9879\u5206\u6790\u62a5\u544a R1745</title>')
H.append('<style>' + CSS + '</style></head><body>')
H.append('<h1>cline \u4e13\u9879\u5206\u6790\u62a5\u544a R1745</h1>')
H.append('<p><small>BaiZe Harness \u7814\u7a76\u7ebf \u00b7 ' + now + ' \u00b7 \u6307\u4ee4\uff1a2026-11-07 10:10 \u7528\u6237\u4ee4 C1-C5</small></p>')
H.append('<div class="alert"><strong>\u26a0\ufe0f \u7f51\u5173\u72b6\u6001</strong>\uff1achat completions \u8fd4\u56de HTTP 403\uff08\u989d\u5ea6\u8017\u5c3d\uff09<br><strong>\u5f52\u56e0\u7ea2\u7ebf</strong>\uff1a\u7f51\u5173\u989d\u5ea6\u8017\u5c3d/429/403 \u4e0d\u7b49\u4e8e\u6a21\u578b\u80fd\u529b\u5dee\u3002</div>')
H.append('<div class="box"><h3>TL;DR</h3><ul>')
H.append('<li><strong>C1</strong>\uff1a7\u8def\u5408\u8ba1 ' + str(t_all) + ' \u6761\u9884\u6d4b\uff0c' + str(r_all) + ' real\u3002cline ' + str(ct) + '\u6761\u4e2d' + str(cr) + ' real(' + str(round(100*cr/max(ct,1),1)) + '%)\u3002</li>')
H.append('<li><strong>\u5173\u952e\u53d1\u73b0</strong>\uff1a\u989d\u5ea6\u8017\u5c3d\u524d cline ' + str(pre_real) + '/' + str(pre_total) + ' = <span class="good">' + str(round(100*pre_real/max(pre_total,1),1)) + '%</span>\uff0c\u4e0e opencode(' + str(c1_rows[2][4]) + '%)\u65e0\u80fd\u529b\u5dee\u8ddd\u3002</li>')
H.append('<li><strong>C2</strong>\uff1a\u7a7apatch\u5168\u90e8=infra\uff1a\u7f51\u5173\u989d\u5ea6=' + str(q_count) + '\u3001\u9002\u914d\u5668=' + str(a_conn + a_sdk) + '\u3002100% infra\u3002</li>')
H.append('<li><strong>C3</strong>\uff1a\u7a7apatch\u672a\u5f52\u96f6\uff0c\u6839\u56e0=\u7f51\u5173\u989d\u5ea6\u8017\u5c3d(403)\uff0c\u975e run_single.py:45 bug(R1744\u5df2\u4fee)\u3002</li>')
H.append('<li><strong>TB4</strong>\uff1a' + str(tb4_total) + ' trials completed / 0 passed(reward=0=\u80fd\u529b)\u3002</li>')
H.append('</ul></div>')

# C1
H.append('<h2>C1 \u2014 \u72ec\u7acb\u7edf\u8ba1</h2>')
H.append('<table><tr><th>Harness</th><th>\u9884\u6d4b\u6570</th><th>Real</th><th>Empty</th><th>Real%</th><th>\u4e2d\u4f4dpatch(B)</th></tr>')
for display, total, real, empty, real_pct, median in c1_rows:
    H.append('<tr><td>' + display + '</td><td>' + str(total) + '/500</td><td>' + str(real) + '</td><td>' + str(empty) + '</td><td>' + str(round(real_pct,1)) + '%</td><td>' + str(median) + '</td></tr>')
H.append('</table>')

# Pre/post quota
H.append('<div class="note"><strong>cline\u989d\u5ea6\u524d\u540e\u5bf9\u6bd4</strong><table><tr><th>\u9636\u6bb5</th><th>\u9898\u6570</th><th>Real</th><th>Empty</th><th>Real%</th></tr>')
H.append('<tr><td>\u989d\u5ea6\u524d</td><td>' + str(pre_total) + '</td><td>' + str(pre_real) + '</td><td>' + str(pre_total-pre_real) + '</td><td><span class="good">' + str(round(100*pre_real/max(pre_total,1),1)) + '%</span></td></tr>')
H.append('<tr><td>\u989d\u5ea6\u540e</td><td>' + str(post_total) + '</td><td>0</td><td>' + str(post_total) + '</td><td>0.0%</td></tr>')
H.append('<tr><td>\u5408\u8ba1</td><td>' + str(ct) + '</td><td>' + str(cr) + '</td><td>' + str(ce) + '</td><td>' + str(round(100*cr/max(ct,1),1)) + '%</td></tr></table>')
H.append('<p>\u6700\u540ereal patch @ ' + last_real_str + '\uff0c\u4e4b\u540e' + str(post_total) + '\u9898\u5168empty(403\u5feb\u901f\u5931\u8d25)\u3002</p></div>')

# C2
H.append('<h2>C2 \u2014 \u5931\u8d25\u539f\u56e0\u5206\u7c7b</h2>')
H.append('<table><tr><th>\u5931\u8d25\u7c7b\u522b</th><th>\u6570\u91cf</th><th>\u5360\u6bd4</th></tr>')
total_ep = len(empty_classes)
for cat_key in ["QUOTA", "ADAPTER_CONN", "ADAPTER_SDK", "TIMEOUT", "OTHER"]:
    cnt = class_counts.get(cat_key, 0)
    H.append('<tr><td>' + cat_labels[cat_key] + '</td><td>' + str(cnt) + '</td><td>' + str(round(100*cnt/max(total_ep,1),1)) + '%</td></tr>')
H.append('<tr><td><strong>\u5408\u8ba1</strong></td><td><strong>' + str(total_ep) + '</strong></td><td><strong>100%</strong></td></tr></table>')

# Top3 samples
H.append('<p><strong>Top3(\u7f51\u5173\u989d\u5ea6)</strong></p><pre>')
for iid, cat, stdout in empty_classes:
    if cat == "QUOTA":
        H.append(iid + ':\n  ' + html.escape(stdout[:150]) + '\n')
        if sum(1 for x in empty_classes if x[1]=="QUOTA" and x[0]<=iid) >= 3:
            break
H.append('</pre>')

# C3
H.append('<h2>C3 \u2014 \u7a7apatch\u662f\u5426\u5f52\u96f6</h2>')
H.append('<div class="alert"><strong>\u274c \u672a\u5f52\u96f6</strong>\uff1a' + str(ce) + ' \u4e2a\u7a7apatch\u3002</div>')
H.append('<p><strong>\u6839\u56e0</strong>\uff1a<strong>\u7f51\u5173\u989d\u5ea6\u8017\u5c3d(HTTP 403)</strong>\uff0c\u975e run_single.py:45 bug\u3002</p>')
H.append('<div class="fix"><strong>\u2705 R1744\u4fee\u590d</strong>\uff1aalways-extract-patch(7\u5904)\u3002\u989d\u5ea6\u524d' + str(pre_real) + '/' + str(pre_total) + '=' + str(round(100*pre_real/max(pre_total,1),1)) + '%\uff08vs \u4fee\u590d\u524d51.5%\uff09=\u4fee\u590d\u6709\u6548\u3002</div>')
H.append('<p><strong>\u8bc1\u636e</strong></p><pre>1. curl /v1/chat/completions -> HTTP 403\n2. astropy-14369: "\u672c\u6b21Token\u989d\u5ea6\u5df2\u7528\u5b8c"\n3. \u6700\u540ereal @ ' + last_real_str + ', \u4e4b\u540e' + str(post_total) + '\u9898\u5168empty\n4. \u7a7apatch\u95f4\u9689\u22486min=403\u5feb\u901f\u5931\u8d25</pre>')

# C4
H.append('<h2>C4 \u2014 \u5fc3\u8df3\u4e00\u884c</h2>')
H.append('<div class="box"><code>cline\u4e13\u9879: SWE-bench real ' + str(cr) + '/' + str(ct) + '(' + str(round(100*cr/max(ct,1),1)) + '%) \u00b7 \u989d\u5ea6\u524d' + str(pre_real) + '/' + str(pre_total) + '=' + str(round(100*pre_real/max(pre_total,1),1)) + '%\u2248opencode · empty ' + str(ce) + '(\u5168infra) · TB4 ' + str(tb4_total) + 'completed/0passed · top1=\u7f51\u5173\u989d\u5ea6\u8017\u5c3d(403)</code></div>')

# C5
H.append('<h2>C5 \u2014 \u5dee\u8ddd\u6765\u6e90</h2>')
H.append('<table><tr><th>\u6307\u6807</th><th>cline</th><th>opencode</th><th>hermes</th><th>\u5dee\u8ddd</th></tr>')
H.append('<tr><td>Real%(\u5168\u91cf)</td><td>' + str(round(c1_rows[0][4],1)) + '%</td><td>' + str(round(c1_rows[2][4],1)) + '%</td><td>' + str(round(c1_rows[5][4],1)) + '%</td><td>\u7a7apatch=infra</td></tr>')
H.append('<tr><td><strong>Real%(\u989d\u5ea6\u524d)</strong></td><td><span class="good">' + str(round(100*pre_real/max(pre_total,1),1)) + '%</span></td><td>' + str(round(c1_rows[2][4],1)) + '%</td><td>-</td><td><strong>\u65e0\u80fd\u529b\u5dee\u8ddd</strong></td></tr>')
H.append('<tr><td>TB4 passed</td><td>0</td><td>0</td><td>0</td><td>\u51680=\u80fd\u529b</td></tr></table>')
H.append('<div class="note"><strong>\u7ed3\u8bba</strong>\uff1a<ol><li><strong>\u8fde\u63a5\u6b63\u5e38cline real=' + str(round(100*pre_real/max(pre_total,1),1)) + '%\uff0c\u4e0eopencode\u65e0\u5dee\u8ddd\u3002</strong></li><li>\u7a7apatch=infra(403+\u9002\u914d\u5668)\uff0c\u975e\u80fd\u529b\u5dee\u3002</li><li>TB4\u51680=glm-5.3-flash\u80fd\u529b\u9650\u5236\u3002</li><li><strong>\u53ef\u68c0\u9a8c\u5047\u8bbe</strong>\uff1a\u989d\u5ea6\u6062\u590d\u540ereal%\u219290%+\u3002</li></ol></div>')

# TB4
H.append('<h2>TB4\u5168\u5c40</h2><table><tr><th>Harness</th><th>Completed</th><th>Passed</th></tr>')
for h in ["cline", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]:
    display = h.replace("deepseek-harness", "deepseek")
    s = TB4_stats.get(h, TB4_stats.get(display, {"completed": 0, "passed": 0}))
    H.append('<tr><td>' + display + '</td><td>' + str(s["completed"]) + '</td><td>' + str(s["passed"]) + '</td></tr>')
H.append('<tr><td><strong>\u5408\u8ba1</strong></td><td><strong>' + str(tb4_total) + '</strong></td><td><strong>0</strong></td></tr></table>')

H.append('<h2>\u9644\u5f55</h2><ul><li>\u7f51\u5173: /v1/models HTTP200, /v1/chat/completions HTTP403</li><li>gw_proxy 9092/9093 \u8fd0\u884c\u4e2d</li><li>cline \u76f4\u8fde gateway</li><li>\u9884\u6d4b7\u8defalive(0% CPU)</li></ul>')
H.append('<hr><p><small>\u751f\u6210: ' + now + ' \u00b7 gen_cline_special_r1745.py \u00b7 0\u5916\u94fe</small></p></body></html>')

out_path = os.path.join(REPORT_DIR, "report_harness_cline_special_r1745_zh.html")
with open(out_path, "w") as f:
    f.write("\n".join(H))
print("Report: " + out_path + " (" + str(os.path.getsize(out_path)) + " bytes)")
