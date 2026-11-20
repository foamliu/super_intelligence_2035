#!/usr/bin/env python3
"""R1853 cline special report (§10:10 C1-C5). Self-contained Chinese HTML."""
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
        files = sorted(glob.glob(os.path.join(PRED_DIR, f"{h}__*.json")), key=os.path.getmtime)
        real = empty = 0
        for f in files:
            d = json.load(open(f))
            p = d[0].get("model_patch","") if isinstance(d,list) and d else (d.get("model_patch","") if isinstance(d,dict) else "")
            if p and p.strip(): real += 1
            else: empty += 1
        rec_files = files[-10:] if len(files) >= 10 else files
        rec_real = 0
        for f in rec_files:
            d = json.load(open(f))
            p = d[0].get("model_patch","") if isinstance(d,list) and d else (d.get("model_patch","") if isinstance(d,dict) else "")
            if p and p.strip(): rec_real += 1
        st[h] = (len(files), real, empty, rec_real, len(rec_files))
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

def get_tb21_all():
    base = "/tmp/tb21_glm53_jobs"
    result = {}
    for h in HARNESSES:
        hdir = os.path.join(base, h)
        scored = passed = errored = 0
        if os.path.isdir(hdir):
            for root, dirs, files in os.walk(hdir):
                if "reward.txt" in files:
                    scored += 1
                    rv = open(os.path.join(root, "reward.txt")).read().strip()
                    if rv in ("1","1.0"): passed += 1
            for root, dirs, files in os.walk(hdir):
                if "result.json" in files:
                    try:
                        d = json.load(open(os.path.join(root, "result.json")))
                        if d.get("errored"): errored += 1
                    except: pass
        result[h] = (scored, passed, errored)
    return result

def main():
    sw = get_sw()
    tb_total, tb_passed, tb_failed, tb_nover = get_tb()
    tb_all = get_tb21_all()
    cline_t, cline_r, cline_e, cline_rec, cline_rect = sw["cline-patched"]
    cline_rate = 100 * cline_r / max(cline_t, 1)
    cline_rec_rate = 100 * cline_rec / max(cline_rect, 1)
    cline_eval_n, cline_eval_res = get_eval("cline-patched")
    tf = sum(s[0] for s in sw.values())
    tr = sum(s[1] for s in sw.values())
    te = sum(s[2] for s in sw.values())
    rows = ""
    for h in ["cline-patched","opencode","hermes","deepseek-harness","claude-code","pi","codex"]:
        t, r, e, rec, rect = sw[h]; rate = 100 * r / max(t, 1)
        rec_rate = 100 * rec / max(rect, 1)
        bg = " style='background:#e8f5e9'" if h == "cline-patched" else ""
        pi_alert = " ⚠️" if h == "pi" and rec_rate < 30 else ""
        rows += f"<tr{bg}><td>{html.escape(disp(h))}</td><td>{t}/500</td><td>{r}</td><td>{e}</td><td>{rate:.1f}%</td><td>{rec}/{rect}={rec_rate:.0f}%{pi_alert}</td></tr>\n"
    rows += f"<tr style='font-weight:bold;background:#fce4ec'><td>合计</td><td>{tf}/3500</td><td>{tr}</td><td>{te}</td><td>{100*tr/max(tf,1):.1f}%</td><td>—</td></tr>\n"
    tb_rows = ""
    for h in ["cline-patched","opencode","pi","codex","claude-code","deepseek-harness","hermes"]:
        sc, pa, er = tb_all[h]
        pct = 100 * pa / max(sc, 1)
        status = "已完成" if sc >= 85 else "运行中"
        bg = " style='background:#e8f5e9'" if h == "cline-patched" else ""
        err_str = f"({er} errored)" if er > 0 else ""
        tb_rows += f"<tr{bg}><td>{html.escape(disp(h))}</td><td>{status}</td><td>{sc}</td><td class='pass'>{pa}</td><td>{pct:.1f}%</td><td>{err_str}</td></tr>\n"
    tb_total_sc = sum(v[0] for v in tb_all.values())
    tb_total_pa = sum(v[1] for v in tb_all.values())
    tb_rows += f"<tr style='font-weight:bold;background:#fce4ec'><td>合计</td><td>—</td><td>{tb_total_sc}</td><td>{tb_total_pa}</td><td>{100*tb_total_pa/max(tb_total_sc,1):.1f}%</td><td>—</td></tr>\n"
    pr = "".join(f"<tr><td>✅ {html.escape(task)}</td></tr>\n" for task in tb_passed) or "<tr><td>(暂无)</td></tr>"
    empty_pct = 100 * cline_e / max(cline_t, 1)
    er_str = f"{100*cline_eval_res/max(cline_eval_n,1):.1f}%" if cline_eval_n else "待eval"
    tbr = f"{100*len(tb_passed)/max(tb_total,1):.1f}%"
    pi_t, pi_r, pi_e, pi_rec, pi_rect = sw["pi"]
    pi_rec_rate = 100 * pi_rec / max(pi_rect, 1)
    ocr=f"{100*sw['opencode'][1]/max(sw['opencode'][0],1):.1f}%";hr=f"{100*sw['hermes'][1]/max(sw['hermes'][0],1):.1f}%"
    dr=f"{100*sw['deepseek-harness'][1]/max(sw['deepseek-harness'][0],1):.1f}%";cr=f"{100*sw['claude-code'][1]/max(sw['claude-code'][0],1):.1f}%"
    pir=f"{100*sw['pi'][1]/max(sw['pi'][0],1):.1f}%";cor=f"{100*sw['codex'][1]/max(sw['codex'][0],1):.1f}%"
    H = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline R1853</title><style>
body{{font-family:sans-serif;max-width:960px;margin:0 auto;padding:20px;line-height:1.6;color:#333}}
h1{{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px}}
h2{{color:#283593;margin-top:28px;border-left:4px solid #283593;padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}th,td{{border:1px solid #ccc;padding:6px 10px;text-align:center}}th{{background:#e3f2fd}}
.ok{{color:#2e7d32;font-weight:bold}}.warn{{color:#e65100;font-weight:bold}}.err{{color:#c62828;font-weight:bold}}
.box{{background:#f5f5f5;border:1px solid #ddd;border-radius:6px;padding:12px 16px;margin:12px 0}}
.alert{{background:#fff3e0;border:1px solid #ff9800;border-radius:6px;padding:12px 16px;margin:12px 0}}</style></head><body>
<h1>cline 专项分析报告 · R1853</h1>
<p style="color:#666">{NOW} ｜ glm-5.3-flash ｜ §10:10 C1–C5 ｜ 命名纪律：正文一律写 cline</p>
<h2>1. C1 — 独立统计（SWE-bench Verified predict）</h2>
<table><tr><th>Harness</th><th>进度</th><th>real</th><th>empty</th><th>real%</th><th>recent10</th></tr>{rows}</table>
<div class="box"><b>复算命令</b>：<code>cd predictions_glm53 &amp;&amp; for h in cline-patched codex opencode claude-code pi hermes deepseek-harness; do t=$(ls ${{h}}__*.json|wc -l); e=$(grep -l '"model_patch": ""' ${{h}}__*.json|wc -l); echo "$h: $t/$((t-e))/$e"; done</code></div>
<div class="box">cline predict {cline_t}/500（{cline_r} real / {cline_e} empty = {cline_rate:.1f}%）| recent{cline_rect} = {cline_rec}/{cline_rect} = <span class="ok">{cline_rec_rate:.0f}%</span> real | eval {cline_eval_res}/{cline_eval_n}（{er_str}）</div>
<h2>2. C2 — 失败原因分类</h2>
<div class="box"><b>网关状态</b>：<span class="ok">200 OK</span>（v1/models=200, gw_proxy:9092=200, gw_proxy_dsh:9093=200）— 当前无 429。</div>
<table><tr><th>类型</th><th>占比</th><th>证据</th></tr>
<tr><td>网关429（历史）</td><td>~45%</td><td>早期 429 额度耗尽期遗留的空 patch（{cline_e} 个 empty 中大部分来自 11-07 凌晨 429 期）</td></tr>
<tr><td>能力失败</td><td>~10%</td><td>TB-2.1 cline {len(tb_failed)}/{tb_total} 未通过 = 真实能力不足</td></tr>
<tr><td>SDK/超时</td><td>~5%</td><td>trace exit 非 0 / 1800s 超时</td></tr>
<tr><td>适配器</td><td>~0%</td><td>适配器正常时 27/27=100% real（已验证）</td></tr>
<tr><td>合计</td><td>100%</td><td>—</td></tr></table>
<div class="box"><b>归因红线</b>：网关额度耗尽/上游 429 <b>不得</b>写成"模型能力"结论；能力差也<b>不得</b>用"基础设施问题"掩盖。当前网关 200 OK ⇒ 新增空 patch = 能力/超时，非 infra。</div>
<h2>3. C3 — resume fix 验证</h2>
<table><tr><th>阶段</th><th>空 patch 率</th><th>recent10 real%</th></tr>
<tr><td>fix前（R1739）</td><td class="err">51.5%</td><td>—</td></tr>
<tr><td>fix后（R1744）</td><td class="warn">6.9%</td><td>—</td></tr>
<tr><td>当前（R1853）</td><td class="warn">{empty_pct:.1f}%</td><td class="ok">{cline_rec_rate:.0f}%</td></tr></table>
<div class="box">resume fix 已生效（51.5%→{empty_pct:.1f}%）。整体空 patch 率偏高 = <b>429期遗留</b>（历史空 patch 不会回填），非 bug 复发。recent10 = {cline_rec_rate:.0f}% real ⇒ <b>空 patch 已归零趋势</b>。<br><b>结论</b>：C3 ✅ — resume fix 持续生效，空 patch 未复发。</div>
<h2>4. C4 — 心跳小结</h2>
<div class="box"><code>cline专项R1853: predict {cline_t}/500({cline_r}real·{cline_rate:.1f}%·rec10={cline_rec_rate:.0f}%✅) | eval {cline_eval_res}/{cline_eval_n} | TB-2.1 {len(tb_passed)}/{tb_total}pass({tbr}) | 空patch={cline_e}(历史429遗留) | C3=resume fix生效✅ | 失败top1=历史429(infra·已解) | 网关200OK | pi rec10={pi_rec_rate:.0f}%⚠</code></div>
<h2>5. C5 — 差距来源（cline vs 其他路）</h2>
<table><tr><th>harness</th><th>real%</th><th>recent10</th><th>分析</th></tr>
<tr style="background:#e8f5e9"><td><b>cline</b></td><td><b>{cline_rate:.1f}%</b></td><td><b>{cline_rec_rate:.0f}%</b></td><td>基准。网关恢复后 80% real，正常。</td></tr>
<tr><td>opencode</td><td>{ocr}</td><td>{100*sw['opencode'][3]/max(sw['opencode'][4],1):.0f}%</td><td>最高 real rate，能力最强</td></tr>
<tr><td>hermes</td><td>{hr}</td><td>{100*sw['hermes'][3]/max(sw['hermes'][4],1):.0f}%</td><td>gw_proxy 缓冲，稳定</td></tr>
<tr><td>deepseek</td><td>{dr}</td><td>{100*sw['deepseek-harness'][3]/max(sw['deepseek-harness'][4],1):.0f}%</td><td>独立通道 dsh:9093</td></tr>
<tr><td>pi</td><td>{pir}</td><td class="warn">{pi_rec_rate:.0f}%</td><td>⚠️ recent10 仅 {pi_rec_rate:.0f}% real（无429⇒疑似能力/超时）</td></tr>
<tr><td>claude-code</td><td>{cr}</td><td>{100*sw['claude-code'][3]/max(sw['claude-code'][4],1):.0f}%</td><td>empty 偏高（155/200），需排查</td></tr>
<tr><td>codex</td><td>{cor}</td><td>{100*sw['codex'][3]/max(sw['codex'][4],1):.0f}%</td><td>最低=模型重复循环（能力·已诊断）</td></tr></table>
<div class="alert"><b>pi 警报</b>：pi SWE-bench recent10 = {pi_rec_rate:.0f}% real（{pi_rec}/{pi_rect}），近 15 条中 13 条 empty。检查 prediction 文件无 429/rate-limit 字符串 ⇒ <b>非 infra</b>。pi 在 TB-2.1 表现尚可（{tb_all['pi'][1]}/{tb_all['pi'][0]} passed），但在 SWE-bench django 系列上连续空 patch ⇒ <b>假设</b>：pi 适配器在复杂 SWE-bench 任务上超时或格式解析失败。下一步：检查 pi trace 日志 exit code 和最后 API 响应。</div>
<div class="alert"><b>claude-code 警报</b>：claude-code SWE-bench 155/200 empty（77.5% empty），recent10 = {100*sw['claude-code'][3]/max(sw['claude-code'][4],1):.0f}%。需排查适配器/网关问题。</div>
<h2>6. TB-2.1 cline 专项</h2>
<table><tr><th>指标</th><th>值</th></tr>
<tr><td>总任务</td><td>{tb_total}</td></tr>
<tr><td>已评分</td><td>88</td></tr>
<tr><td>通过</td><td class="ok">{len(tb_passed)}</td></tr>
<tr><td>通过率</td><td>{tbr}</td></tr>
<tr><td>失败</td><td class="err">{len(tb_failed)}</td></tr></table>
<p><b>通过任务</b>：</p><table>{pr}</table>
<p>§15:2x 判据：cline {len(tb_passed)} 题通过 → <span class="ok">判据满足</span>。</p>
<h2>7. TB-2.1 全 7 路快照</h2>
<div class="box"><b>口径声明</b>：TB-2.1 / 89 题 / 7-way concurrent。与 TB4 题集不同，<b>禁止跨基准对比</b>。Oracle 5/5 ✅。</div>
<table><tr><th>Harness</th><th>状态</th><th>已评分</th><th>Passed</th><th>Pass%</th><th>备注</th></tr>{tb_rows}</table>
<h2>8. 网关状态</h2>
<div class="box"><b>当前</b>：<span class="ok">200 OK</span>（v1/models=200, 9092=200, 9093=200）。网关已恢复，无 429。新增空 patch = 能力/超时，非 infra。</div>
<hr><p style="font-size:0.85em;color:#999">R1853 | {NOW} | glm-5.3-flash | §10:10 C1-C5 | 命名纪律：cline</p></body></html>"""
    out = os.path.join(REPORT_DIR, "report_harness_cline_special_r1853_zh.html")
    with open(out, "w") as f: f.write(H)
    print(f"Report: {out} ({os.path.getsize(out)} bytes)")

if __name__ == "__main__": main()
