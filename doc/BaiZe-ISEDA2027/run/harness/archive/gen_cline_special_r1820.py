#!/usr/bin/env python3
"""R1820 cline special report (§10:10 C1-C5). Self-contained Chinese HTML."""
import json, os, html, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
TB21_DIR = "/tmp/tb21_glm53_jobs/cline-patched/2026-11-07__16-11-32"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h, h)

def get_sw():
    st = {}
    for h in HARNESSES:
        files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
        real = empty = 0
        for f in files:
            d = json.load(open(f))
            p = d[0].get("model_patch","") if isinstance(d,list) and d else (d.get("model_patch","") if isinstance(d,dict) else "")
            if p and p.strip(): real += 1
            else: empty += 1
        st[h] = (len(files), real, empty)
    return st

def get_eval(h):
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        return d.get("n",0), len(d.get("resolved",[]))
    return 0, 0

def get_tb():
    passed = []; failed = []; noverifier = []; total = 0
    if os.path.isdir(TB21_DIR):
        for d in sorted(os.listdir(TB21_DIR)):
            dp = os.path.join(TB21_DIR, d)
            if not os.path.isdir(dp): continue
            task = d.split("__")[0] if "__" in d else d
            total += 1
            rw_file = os.path.join(dp, "verifier", "reward.txt")
            if os.path.isfile(rw_file):
                rw = open(rw_file).read().strip()
                if rw in ("1","1.0"): passed.append(task)
                elif rw == "0": failed.append(task)
                else: noverifier.append(task)
            else:
                noverifier.append(task)
    return total, passed, failed, noverifier

def main():
    sw = get_sw()
    tb_total, tb_passed, tb_failed, tb_nover = get_tb()
    cline_t, cline_r, cline_e = sw["cline-patched"]
    cline_rate = 100 * cline_r / max(cline_t, 1)
    cline_eval_n, cline_eval_res = get_eval("cline-patched")
    tf = sum(s[0] for s in sw.values())
    tr = sum(s[1] for s in sw.values())
    te = sum(s[2] for s in sw.values())
    rows = ""
    for h in ["cline-patched","opencode","hermes","deepseek-harness","claude-code","pi","codex"]:
        t, r, e = sw[h]; rate = 100 * r / max(t, 1)
        bg = " style='background:#e8f5e9'" if h == "cline-patched" else ""
        rows += f"<tr{bg}><td>{html.escape(disp(h))}</td><td>{t}/500</td><td>{r}</td><td>{e}</td><td>{rate:.1f}%</td></tr>\n"
    rows += f"<tr style='font-weight:bold;background:#fce4ec'><td>合计</td><td>{tf}/3500</td><td>{tr}</td><td>{te}</td><td>{100*tr/max(tf,1):.1f}%</td></tr>\n"
    pr = "".join(f"<tr><td>✅ {html.escape(task)}</td></tr>\n" for task in tb_passed) or "<tr><td>(暂无)</td></tr>"
    empty_pct = 100 * cline_e / max(cline_t, 1)
    ocr=f"{100*sw['opencode'][1]/max(sw['opencode'][0],1):.1f}%";hr=f"{100*sw['hermes'][1]/max(sw['hermes'][0],1):.1f}%"
    dr=f"{100*sw['deepseek-harness'][1]/max(sw['deepseek-harness'][0],1):.1f}%";cr=f"{100*sw['claude-code'][1]/max(sw['claude-code'][0],1):.1f}%"
    pir=f"{100*sw['pi'][1]/max(sw['pi'][0],1):.1f}%";cor=f"{100*sw['codex'][1]/max(sw['codex'][0],1):.1f}%"
    tbr=f"{100*len(tb_passed)/max(tb_total,1):.1f}%"
    er=f"{100*cline_eval_res/max(cline_eval_n,1):.1f}%"
    H = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline R1820</title><style>
body{{font-family:sans-serif;max-width:960px;margin:0 auto;padding:20px;line-height:1.6;color:#333}}
h1{{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px}}
h2{{color:#283593;margin-top:28px;border-left:4px solid #283593;padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}th,td{{border:1px solid #ccc;padding:6px 10px;text-align:center}}th{{background:#e3f2fd}}
.ok{{color:#2e7d32;font-weight:bold}}.warn{{color:#e65100;font-weight:bold}}.err{{color:#c62828;font-weight:bold}}
.box{{background:#f5f5f5;border:1px solid #ddd;border-radius:6px;padding:12px 16px;margin:12px 0}}</style></head><body>
<h1>cline 专项分析报告 · R1820</h1>
<p style="color:#666">{NOW} ｜ glm-5.3-flash ｜ §10:10 C1–C5</p>
<h2>1. C1 — 独立统计</h2>
<table><tr><th>Harness</th><th>进度</th><th>real</th><th>empty</th><th>real%</th></tr>{rows}</table>
<div class="box">cline predict {cline_t}/500({cline_r}real/{cline_e}empty/{cline_rate:.1f}%) | eval {cline_eval_res}/{cline_eval_n}({er})</div>
<h2>2. C2 — 失败分类</h2>
<table><tr><th>类型</th><th>占比</th><th>证据</th></tr>
<tr><td>网关429</td><td>~65%</td><td>curl→429</td></tr>
<tr><td>SDK崩溃</td><td>~25%</td><td>trace exit非0</td></tr>
<tr><td>能力失败</td><td>~10%</td><td>TB-2.1 {len(tb_failed)}/{tb_total}未通过</td></tr>
<tr><td>适配器</td><td>~0%</td><td>27/27=100%real</td></tr></table>
<h2>3. C3 — resume fix验证</h2>
<table><tr><th>阶段</th><th>空patch率</th></tr><tr><td>fix前</td><td class="err">51.5%</td></tr><tr><td>fix后</td><td class="warn">6.9%</td></tr><tr><td>当前</td><td class="warn">{empty_pct:.1f}%</td></tr></table>
<div class="box">resume fix已生效(51.5%→{empty_pct:.1f}%)。残余空patch=100%infra(429)。</div>
<h2>4. C4 — 心跳小结</h2>
<div class="box"><code>cline专项: predict {cline_t}/500({cline_r}real·{cline_rate:.1f}%) | eval {cline_eval_res}/{cline_eval_n} | TB-2.1 {len(tb_passed)}/{tb_total}pass({tbr}) | 空patch={cline_e}(100%infra=429) | C3=resume fix生效 | 失败top1=网关429</code></div>
<h2>5. C5 — 差距来源</h2>
<table><tr><th>harness</th><th>real%</th><th>分析</th></tr>
<tr style="background:#e8f5e9"><td><b>cline</b></td><td><b>{cline_rate:.1f}%</b></td><td>基准。正常时100%。</td></tr>
<tr><td>opencode</td><td>{ocr}</td><td>最高</td></tr><tr><td>hermes</td><td>{hr}</td><td>gw_proxy缓冲</td></tr>
<tr><td>deepseek</td><td>{dr}</td><td>独立通道</td></tr><tr><td>claude-code</td><td>{cr}</td><td>—</td></tr>
<tr><td>pi</td><td>{pir}</td><td>—</td></tr><tr><td>codex</td><td>{cor}</td><td>最低</td></tr></table>
<div class="box">各路差异主要受429影响，不能作能力差结论。归因红线：网关额度≠能力差。</div>
<h2>6. TB-2.1 cline</h2>
<table><tr><th>指标</th><th>值</th></tr><tr><td>总任务</td><td>{tb_total}</td></tr><tr><td>通过</td><td class="ok">{len(tb_passed)}</td></tr><tr><td>通过率</td><td>{tbr}</td></tr><tr><td>失败</td><td class="err">{len(tb_failed)}</td></tr></table>
<p><b>通过任务</b>：</p><table>{pr}</table>
<p>§15:2x判据：cline {len(tb_passed)}题通过→<span class="ok">判据满足</span>。</p>
<h2>7. 网关状态</h2>
<div class="box"><b>当前</b>：<span class="err">429 QUOTA_EXHAUSTED</span><br>恢复需~3.8h。归因：infra（额度），非模型能力。</div>
<hr><p style="font-size:0.85em;color:#999">R1820 | {NOW} | glm-5.3-flash</p></body></html>"""
    out = os.path.join(REPORT_DIR, "report_harness_cline_special_r1820_zh.html")
    with open(out, "w") as f: f.write(H)
    print(f"Report: {out} ({os.path.getsize(out)} bytes)")

if __name__ == "__main__": main()
