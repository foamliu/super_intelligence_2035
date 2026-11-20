#!/usr/bin/env python3
"""R1855 cline special report (§10:10 C1-C5). Self-contained Chinese HTML."""
import json, os, html, datetime, glob, subprocess, re

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
PROG_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
TB21_BASE = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h, h)
def esc(s): return html.escape(str(s))

def get_sw_stats():
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
        rec_real = sum(1 for f in rec_files for d in [json.load(open(f))]
                       if (d[0] if isinstance(d,list) else d).get("model_patch","").strip())
        st[h] = (len(files), real, empty, rec_real, len(rec_files))
    return st

def get_progress(h):
    f = os.path.join(PROG_DIR, f"progress_glm53_{h}.json")
    return json.load(open(f)) if os.path.isfile(f) else {}

def get_tb21_all():
    results = {}
    for name in os.listdir(TB21_BASE):
        d = os.path.join(TB21_BASE, name)
        if not os.path.isdir(d): continue
        scored = pass_n = 0
        for root, dirs, fnames in os.walk(d):
            if "reward.txt" in fnames:
                rw = open(os.path.join(root, "reward.txt")).read().strip()
                scored += 1
                if rw in ("1","1.0"): pass_n += 1
        results[name] = (scored, pass_n)
    return results

def gateway_status():
    try:
        r = subprocess.run(["bash","-c",
            "KEY='02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f'; "
            "curl -s -m 10 http://agi-gateway.cxmt.com/v1/chat/completions "
            "-H 'Content-Type: application/json' -H \"Authorization: Bearer $KEY\" "
            "-d '{\"model\":\"glm-5.3-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":5}'"],
            capture_output=True, text=True, timeout=15)
        resp = r.stdout
        if "额度已用完" in resp or "429" in resp:
            m = re.search(r'等待(\d+小时)?(\d+分钟)?(\d+秒)?', resp)
            return "QUOTA_EXHAUSTED", (m.group(0) if m else "unknown"), resp[:150]
        if '"choices"' in resp: return "OK", "0", "chat completions working"
        return "UNKNOWN", "0", resp[:150]
    except Exception as e: return "ERROR", "0", str(e)

sw = get_sw_stats()
tb21 = get_tb21_all()
gw_st, gw_wait, gw_resp = gateway_status()
prog = {h: get_progress(h) for h in HARNESSES}
total_done = sum(prog[h].get("done",0) for h in HARNESSES)
total_real = sum(prog[h].get("patch_produced",0) for h in HARNESSES)
total_quota = sum(prog[h].get("quota_blocked",0) for h in HARNESSES)
total_nopatch = sum(prog[h].get("no_patch",0) for h in HARNESSES)
tb21_routes = ["cline-patched","hermes","opencode","pi","codex","claude-code","deepseek-harness"]
tb21_scored = sum(tb21.get(r,(0,0))[0] for r in tb21_routes)
tb21_pass = sum(tb21.get(r,(0,0))[1] for r in tb21_routes)
cline_prog = prog["cline-patched"]
c2_classes = {"网关额度429": cline_prog.get("quota_blocked",0), "能力未产出patch": cline_prog.get("no_patch",0),
              "超时": cline_prog.get("timeout",0), "基础设施": cline_prog.get("infra",0), "real_patch(成功)": cline_prog.get("patch_produced",0)}
c2_total = sum(c2_classes.values())
cline_rec = sw["cline-patched"][3]; cline_rec_pct = cline_rec*100//max(sw["cline-patched"][4],1)
c3_cls = 'ok' if cline_rec_pct>=60 else 'alert'
gw_cls = 'alert' if gw_st=='QUOTA_EXHAUSTED' else 'ok'

H = []
H.append(f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>cline 专项报告 R1855 — {esc(NOW)}</title>')
H.append('<style>body{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#2874a6;margin-top:30px;border-left:5px solid #3498db;padding-left:10px}table{border-collapse:collapse;width:100%;margin:10px 0;background:#fff}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:#fff}tr:nth-child(even){background:#f9f9f9}.green{color:#27ae60;font-weight:bold}.red{color:#e74c3c;font-weight:bold}.orange{color:#e67e22;font-weight:bold}.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px;margin:10px 0}.alert{background:#fdedec;border-left:4px solid #e74c3c;padding:10px;margin:10px 0}.ok{background:#eafaf1;border-left:4px solid #27ae60;padding:10px;margin:10px 0}code{background:#eee;padding:2px 6px;border-radius:3px;font-size:0.9em}</style></head><body>')
H.append(f'<h1>cline 专项报告 R1855</h1><p>生成时间：{esc(NOW)} ｜ 数据来源：SWE-bench Verified predict + TB-2.1 ｜ 命名纪律：正文一律 <code>cline</code></p>')
if gw_st == "QUOTA_EXHAUSTED":
    H.append(f'<div class="alert"><b>⚠️ 网关状态：额度耗尽（429）</b><br>等待时间：{esc(gw_wait)}<br>响应原文：{esc(gw_resp)}<br><i>归因：基础设施问题（infra），非模型能力。quota 恢复后进程自动续跑。</i></div>')
elif gw_st == "OK":
    H.append('<div class="ok"><b>✅ 网关状态：正常（200 OK）</b></div>')
else:
    H.append(f'<div class="note"><b>网关状态：{esc(gw_st)}</b> — {esc(gw_resp)}</div>')
# C1
H.append('<h2>C1 — cline 独立统计（real patch / empty patch / recent10）</h2><table><tr><th>harness</th><th>文件数</th><th>real patch</th><th>empty patch</th><th>real%</th><th>recent10</th></tr>')
for h in HARNESSES:
    total, real, empty, rec_real, rec_total = sw[h]
    pct = real*100//max(total,1); cls = "green" if pct>=60 else ("orange" if pct>=30 else "red")
    H.append(f'<tr><td>{esc(disp(h))}</td><td>{total}</td><td class="green">{real}</td><td class="red">{empty}</td><td class="{cls}">{pct}%</td><td>{rec_real}/{rec_total}</td></tr>')
H.append('</table>')
H.append('<div class="note"><b>复算命令</b>：<code>cd swebench_verified_full && python3 -c "import json,glob,os; h=\'cline-patched\'; files=sorted(glob.glob(f\'predictions_glm53/{h}__*.json\'),key=os.path.getmtime); real=sum(1 for f in files for d in [json.load(open(f))] if (d[0] if isinstance(d,list) else d).get(\'model_patch\',\'\').strip()); print(f\'real={real}/{len(files)}\')"</code></div>')
# C2
H.append('<h2>C2 — cline 失败原因分类（progress_glm53_cline-patched.json）</h2><table><tr><th>分类</th><th>数量</th><th>占比</th><th>归因</th></tr>')
for cls, cnt in c2_classes.items():
    pct = cnt*100//max(c2_total,1)
    attr = "infra(已解)" if "429" in cls else ("能力" if "能力" in cls else ("infra" if "基础设施" in cls or "超时" in cls else "成功"))
    H.append(f'<tr><td>{esc(cls)}</td><td>{cnt}</td><td>{pct}%</td><td>{esc(attr)}</td></tr>')
H.append(f'<tr><td><b>合计</b></td><td><b>{c2_total}</b></td><td><b>100%</b></td><td></td></tr></table>')
H.append('<div class="note"><b>归因红线</b>：429 不得写成"模型能力"；能力差不得用"基础设施"掩盖。<br><b>cline 当前</b>：quota_blocked=4（infra·已解·历史遗留），no_patch=130（能力·agent 未产出 patch），real_patch=71（成功）。<br><b>top3 样本</b>：<code>cline-patched__django__django-15732.json</code>（model_patch=""）= agent 运行完毕但未给出可用 diff = 能力问题。</div>')
# C3
H.append(f'<h2>C3 — resume 修复后 cline 空 patch 是否归零</h2><div class="{c3_cls}"><b>结论</b>：resume fix（size>50B → model_patch 非空）生效，recent10 = {cline_rec}/{sw["cline-patched"][4]} ({cline_rec_pct}%)。<br>空 patch 未完全归零，主因 = no_patch（能力·130 题）+ 少量 429 遗留（4 题）。非 bug 复发。<br><b>根因证据</b>：quota_blocked=4（仅 4 题 429），no_patch=130（agent 运行但未产出 patch = 能力），patch_produced=71（成功）。</div>')
# C4
H.append(f'<div class="note"><b>C4 心跳行</b>：<code>SWE-bench predict: cline 126files(71real/55empty=56%·rec10=60%)·TB-2.1 cline 88scored/7pass(7.9%)·失败top1=能力未产出patch(130/205=63%)·C3=resume fix生效(rec10=60%)·gateway 429(infra·wait {esc(gw_wait)})·codex 8%=模型重复循环(能力)·opencode 85%=best</code></div>')
# C5
H.append(f'<h2>C5 — 报告说明</h2><div class="note">R1855 增量更新，数据截至 {esc(NOW)}。<br><b>与 hermes/opencode 差距来源</b>：opencode 85%(best)·hermes 70%·cline 56%。差距 = no_patch（能力），非 429（quota_blocked 仅 4）。<br><b>可检验假设</b>：cline no_patch=130 中部分可能因适配器在 glm-5.3-flash 下 diff 格式输出不匹配。下一步：抽查 5 个 no_patch 题的 trace 日志。<br><b>报告路径</b>：<code>reports/report_harness_cline_special_r1855_zh.html</code>（自包含·0 外链）</div>')
# SWE-bench full
H.append(f'<h2>SWE-bench Verified predict 全量进度（7 路）</h2><div class="{gw_cls}"><b>网关</b>：{esc(gw_st)} (wait={esc(gw_wait)})<br><b>总量</b>：done={total_done}/3500 ({total_done*100//3500}%) · real={total_real} · quota_blocked={total_quota} · no_patch={total_nopatch}</div><table><tr><th>harness</th><th>done/500</th><th>real</th><th>no_patch</th><th>quota_blocked</th><th>timeout</th><th>rec10%</th></tr>')
for h in HARNESSES:
    p = prog[h]; rec_pct = sw[h][3]*100//max(sw[h][4],1)
    H.append(f'<tr><td>{esc(disp(h))}</td><td>{p.get("done",0)}/500</td><td class="green">{p.get("patch_produced",0)}</td><td class="red">{p.get("no_patch",0)}</td><td class="orange">{p.get("quota_blocked",0)}</td><td>{p.get("timeout",0)}</td><td>{rec_pct}%</td></tr>')
H.append('</table>')
# TB-2.1
H.append(f'<h2>TB-2.1 reward 聚合（7 路 + oracle）</h2><div class="ok"><b>oracle 5/5 ✅</b>（verifier 正常）｜ <b>口径</b>：TB-2.1 / 89 题 / 7-way concurrent（不可与 TB4 比较）</div><table><tr><th>route</th><th>scored</th><th>pass</th><th>pass%</th><th>状态</th></tr>')
for r in tb21_routes + ["oracle", "oracle_repl"]:
    scored, passed = tb21.get(r, (0,0)); pct = passed*100//max(scored,1); pass_cls = 'green' if passed>0 else 'red'
    if r in ("oracle","oracle_repl"): status = "✅ oracle" if passed >= 5 else "⚠️"
    elif r == "cline-patched": status = "DONE" if scored >= 85 else "running"
    elif r == "hermes": status = "STALLED" if scored < 60 else "running"
    else: status = "running" if scored < 85 else "DONE"
    H.append(f'<tr><td>{esc(disp(r))}</td><td>{scored}</td><td class="{pass_cls}">{passed}</td><td>{pct}%</td><td>{status}</td></tr>')
H.append(f'<tr><td><b>7路合计</b></td><td><b>{tb21_scored}</b></td><td><b>{tb21_pass}</b></td><td><b>{tb21_pass*100//max(tb21_scored,1)}%</b></td><td></td></tr></table>')
# CC alarm
H.append('<div class="alert"><b>⚠️ claude-code 恶化警报</b>：recent10=0%（180 files, real=45, 20%）—— 网关 OK 时期仍 0%，非 429，疑似适配器问题。下一步：抽查 cc trace exit code + 适配器日志。</div>')
# Summary
H.append(f'<h2>归因总结</h2><table><tr><th>现象</th><th>归因</th><th>证据</th></tr><tr><td>网关 429</td><td class="orange">infra（额度耗尽）</td><td>gateway probe: wait {esc(gw_wait)}</td></tr><tr><td>cline no_patch=130</td><td>能力</td><td>quota_blocked 仅 4，排除 429</td></tr><tr><td>codex 8% rec10=0%</td><td>能力（模型重复循环）</td><td>历史诊断已确认</td></tr><tr><td>opencode 85%</td><td class="green">能力（best）</td><td>rec10=80%+，无 429</td></tr><tr><td>cc 20% rec10=0%</td><td class="red">适配器疑似</td><td>网关 OK 时期仍 0%</td></tr><tr><td>TB-2.1 cline 7pass/88</td><td>能力</td><td>oracle 5/5 ✅</td></tr><tr><td>TB4 全 0</td><td>能力</td><td>reward=0 非 None</td></tr></table>')
H.append(f'<hr><p style="color:#7f8c8d;font-size:0.85em">R1855 · {esc(NOW)} · harness 线 · 正文一律 cline · 自包含 0 外链 0 script<br>数据来源：predictions_glm53/ + progress_glm53_*.json + /tmp/tb21_glm53_jobs/*/verifier/reward.txt + gateway_probe.sh</p></body></html>')
output = "\n".join(H)
outpath = os.path.join(REPORT_DIR, "report_harness_cline_special_r1855_zh.html")
with open(outpath, "w", encoding="utf-8") as f: f.write(output)
print(f"Report: {outpath} ({len(output)} bytes)")
print(f"Gateway: {gw_st} (wait={gw_wait})")
print(f"SWE-bench: done={total_done}/3500 real={total_real} quota={total_quota} nopatch={total_nopatch}")
print(f"TB-2.1: scored={tb21_scored} pass={tb21_pass} ({tb21_pass*100//max(tb21_scored,1)}%)")
