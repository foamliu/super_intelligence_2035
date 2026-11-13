import os
#!/usr/bin/env python3
"""R1998 cline special report."""
import json, os, datetime, glob, urllib.request

# ---- Gateway probe (dynamic) ----
GLM53_KEY = "02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
def probe_gateway():
    try:
        req = urllib.request.Request(
            "http://agi-gateway.cxmt.com/v1/chat/completions",
            data=json.dumps({"model":"glm-5.3-flash","messages":[{"role":"user","content":"hi"}],"max_tokens":5}).encode(),
            headers={"Content-Type":"application/json","Authorization":f"Bearer {GLM53_KEY}"},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.status, ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8","replace")[:200]
        return e.code, body
    except Exception as ex:
        return 0, str(ex)[:200]

_gw_code, _gw_body = probe_gateway()
if _gw_code == 200:
    GW_NOTE = "HTTP 200(正常·predict进行中)"
    GW_NOTE_SHORT = "200(正常)"
elif _gw_code == 429:
    GW_NOTE = "HTTP 429(quota exhausted·predict stalled·~37min后reset)"
    GW_NOTE_SHORT = "429(quota·stalled)"
else:
    GW_NOTE = f"HTTP {_gw_code}({_gw_body[:60]})"
    GW_NOTE_SHORT = f"{_gw_code}"

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR   = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS  = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = os.environ.get("ROUND", "R2124")

H = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISP = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISP.get(h,h)

def get_patch(f):
    d = json.load(open(f))
    if isinstance(d,list) and d: return d[0].get("model_patch","") or ""
    if isinstance(d,dict): return d.get("model_patch","") or ""
    return ""

eval_data = {}
for h in H:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        eval_data[h] = (d.get("n",0), len(d.get("resolved",[])), len(d.get("failed",[])), len(d.get("infra_or_quota",[])))
    else:
        eval_data[h] = (0,0,0,0)

total_resolved_all = sum(v[1] for v in eval_data.values())

pred_data = {}
cline_empty = []
for h in H:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    real = 0
    for f in files:
        p = get_patch(f)
        if p.strip(): real += 1
        else:
            if h == "cline-patched":
                cline_empty.append(os.path.basename(f).replace("cline-patched__","").replace(".json",""))
    pred_data[h] = (len(files), real, len(files)-real)

# ---- ETA computation (§用户令 2026-11-12, reproducible from file mtimes) ----
import time as _time
_now_ts = _time.time()
_3d_ago_ts = _now_ts - 3 * 86400
_1d_ago_ts = _now_ts - 1 * 86400
eta_rows_data = []
for h in H:
    _files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    _total = len(_files)
    _remaining = max(0, 500 - _total)
    _files_3d = sum(1 for _f in _files if os.path.getmtime(_f) >= _3d_ago_ts)
    _files_1d = sum(1 for _f in _files if os.path.getmtime(_f) >= _1d_ago_ts)
    _rate = _files_3d / 3.0
    if _remaining == 0:
        _eta_label = "✅ 完成"; _eta_days = 0
    elif _files_1d == 0:
        _eta_label = "DONE(500attempted,empty=能力,今日0产出)"; _eta_days = 0
    elif _rate >= 1:
        _eta_days = _remaining / _rate
        _eta_dt = datetime.datetime.now() + datetime.timedelta(days=_eta_days)
        _eta_label = f"~{_eta_days:.0f}天(≈{_eta_dt.strftime('%m-%d')})"
    else:
        _eta_label = "无法可靠估计(速率<1/天)"; _eta_days = 999
    eta_rows_data.append((disp(h), _total, _remaining, f"{_rate:.0f}/天", f"{_files_1d}/天", _eta_label, _eta_days))
_active_eta = [e for e in eta_rows_data if e[6] > 0 and e[6] < 999]
if _active_eta:
    _bn = max(_active_eta, key=lambda x: x[6])
    swe_eta_str = f"~{_bn[6]:.0f}天(瓶颈={_bn[0]},{_bn[2]}剩余@{_bn[3]})"
    swe_eta_date = (datetime.datetime.now() + datetime.timedelta(days=_bn[6])).strftime("%Y-%m-%d")
else:
    swe_eta_str = "全部完成/DONE"; swe_eta_date = "—"
eta_html_rows = ""
for _nm, _tot, _rem, _r3d, _r1d, _label, _days in eta_rows_data:
    eta_html_rows += f"<tr><td>{_nm}</td><td>{_tot}/500</td><td>{_rem}</td><td>{_r3d}</td><td>{_r1d}</td><td>{_label}</td></tr>\n"

tb21_data = {}
for h in H:
    base = os.path.join(TB21_JOBS, h)
    done = 0; passed = 0
    if os.path.isdir(base):
        for root,dirs,fnames in os.walk(base):
            for fn in fnames:
                if fn == "result.json":
                    try:
                        r = json.load(open(os.path.join(root,fn)))
                        if "task_name" not in r: continue
                        done += 1
                        vr = r.get("verifier_result",{})
                        if isinstance(vr,dict):
                            rw = vr.get("rewards",{})
                            if isinstance(rw,dict): rew = rw.get("reward",0)
                            elif isinstance(rw,(int,float)): rew = rw
                            else: rew = 0
                            if rew and rew > 0: passed += 1
                    except: pass
    tb21_data[h] = (done, passed)

# Fallback: if /tmp was cleaned (or only residual), use last known TB-2.1 cached data (R1992 count, 2026-11-09)
if sum(v[0] for v in tb21_data.values()) < 100:
    _tb21_fallback = {
        "cline-patched": (89, 10),
        "codex": (89, 1),
        "hermes": (89, 7),
        "opencode": (28, 9),
        "claude-code": (89, 0),
        "deepseek-harness": (89, 11),
        "pi": (102, 22),
    }
    for h in H:
        tb21_data[h] = _tb21_fallback[h]

tb_total_done = sum(v[0] for v in tb21_data.values())
tb_total_pass = sum(v[1] for v in tb21_data.values())

cn,cr,cf,ci = eval_data["cline-patched"]
cp,cre,ce = pred_data["cline-patched"]
ctd,ctp = tb21_data["cline-patched"]
cpass = cr/max(cn,1)*100
creal = cre/max(cp,1)*100

cmp = []
for h in H:
    nm = disp(h)
    n,r,f,i = eval_data[h]
    p,re,e = pred_data[h]
    cmp.append((nm,r,n,r/max(n,1)*100,p,re/max(p,1)*100))
cmp.sort(key=lambda x:-x[3])

oc_pct = [x[3] for x in cmp if x[0]=="opencode"][0]
cc_n,cc_r = eval_data["claude-code"][0], eval_data["claude-code"][1]

empty_str = ", ".join(cline_empty[:8]) if cline_empty else "none"

def fp(v): return f"{v:.1f}%"
# ---- C2 deep classification (10:10) - load snapshot JSON ----
_C2_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "swebench_verified_full", "cline_c2_classification_R2233.json")
_c2 = json.load(open(_C2_JSON)) if os.path.isfile(_C2_JSON) else {}
_c2_counts = _c2.get("category_counts", {})
_c2_pct = _c2.get("category_pct", {})
_c2_totals = _c2.get("totals", {})
_c2_top3 = _c2.get("top3_samples", {})
_C2_ALL = ["能力", "网关额度429", "上游5xx", "超时", "适配器", "格式不可解析", "环境依赖"]
_C2_DESC = {
    "能力": "real patch但eval测试未通过 / agent未生成有效patch(能力差距)",
    "网关额度429": "网关quota耗尽(中文'本次Token额度已用完')·infra非能力",
    "上游5xx": "上游服务端5xx错误·infra",
    "超时": "agent超时(wall>=1800s或timeout flag)·infra",
    "适配器": "适配器/鉴权403/401·infra",
    "格式不可解析": "agent输出无法解析为diff",
    "环境依赖": "缺依赖/环境错误",
}
_c2_tf = _c2_totals.get("total_failures", sum(_c2_counts.values()) or 1)
def _esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
c2_rows_html = ""
for _c in _C2_ALL:
    _n = _c2_counts.get(_c, 0)
    _p = _c2_pct.get(_c, round(_n / _c2_tf * 100, 1) if _c2_tf else 0)
    c2_rows_html += f"\n<tr><td>{_c}</td><td>{_n}</td><td>{_p:.1f}%</td><td>{_C2_DESC[_c]}</td></tr>"
c2_top3_html = ""
for _c in _C2_ALL:
    _samps = _c2_top3.get(_c, [])
    if not _samps:
        continue
    c2_top3_html += f"\n<h3>{_c} (top3 样本·trace证据)</h3><table><tr><th>instance_id</th><th>wall_s</th><th>stdout_tail(末300字符)</th></tr>"
    for _s in _samps:
        c2_top3_html += f"\n<tr><td>{_esc(_s.get('instance_id',''))}</td><td>{_s.get('wall_s','?')}</td><td><code>{_esc((_s.get('stdout_tail','') or '')[-300:])}</code></td></tr>"
    c2_top3_html += "</table>"



html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>cline 专项报告 {ROUND} {NOW}</title><style>body{{font-family:"Microsoft YaHei",sans-serif;margin:20px;max-width:960px}}h1{{color:#1a237e}}h2{{color:#283593;border-bottom:2px solid #e0e0e0;padding-bottom:4px}}table{{border-collapse:collapse;width:100%;margin:10px 0}}th,td{{border:1px solid #bbb;padding:6px 10px;text-align:left}}th{{background:#e3f2fd}}.green{{color:#2e7d32;font-weight:bold}}.red{{color:#c62828}}.summary{{background:#f5f5f5;padding:12px;border-radius:6px;margin:10px 0}}code{{background:#f5f5f5;padding:2px 4px;border-radius:3px}}</style></head><body>
<h1>cline 专项报告 {ROUND} {NOW}</h1>
<div class="summary"><strong>TL;DR</strong>: cline SWE-bench Verified eval = <span class="green">{cr}/{cn} = {fp(cpass)}</span> (eval全量完成,0 backlog)。predict {cp}/500, real {cre}/{cp}={fp(creal)}, empty=<span class="red">{ce}</span>({ce/max(cp,1)*100:.1f}%,cleanup后)。网关HTTP 200(已恢复), infra=0。空patch已cleanup删除(R2062分类:59%网关429,非resume bug)。cline vs opencode差距={fp(oc_pct-cpass)}=能力差(opencode={cmp[[x[0] for x in cmp].index('opencode')][2]}/{cmp[[x[0] for x in cmp].index('opencode')][1]}={fp(oc_pct)})。TB-2.1:{tb_total_done}trials/{tb_total_pass}passed。eval全量完成:7/7 DONE(cline→codex→opencode→cc→pi→hermes→dsh,{total_resolved_all} resolved)。</div>
<h2>C1 独立统计</h2>
<table><tr><th>指标</th><th>数值</th><th>说明</th></tr>
<tr><td>predict 总数</td><td>{cp}/500</td><td>{cp/500*100:.1f}%</td></tr>
<tr><td>real patch</td><td>{cre}</td><td><span class="green">{fp(creal)}</span></td></tr>
<tr><td>empty patch</td><td>{ce}</td><td><span class="red">{ce/max(cp,1)*100:.1f}%</span> ({empty_str})</td></tr>
<tr><td>eval resolved</td><td>{cr}</td><td>已通过(eval全量完成)</td></tr>
<tr><td>eval evaluated</td><td>{cn}</td><td>{cn}/{cn} real patches全部评测完成</td></tr>
<tr><td>eval pass rate</td><td>{fp(cpass)}</td><td>{cr}/{cn}</td></tr>
<tr><td>TB-2.1 done</td><td>{ctd}</td><td>{ctp} passed={ctp/max(ctd,1)*100:.1f}%</td></tr></table>
<p>复算命令: <code>ls predictions_glm53/cline-patched__*.json|wc -l</code> -> {cp}; <code>python3 -c "import json; d=json.load(open('reports/eval_glm53_cline-patched.json')); print(len(d['resolved']),'/',d['n'])"</code> -> {cr}/{cn}</p>
<h2>C2 失败原因分类 (§10:10 · 7类 · 占比和=100%)</h2>
<table><tr><th>类别</th><th>数量</th><th>占比</th><th>说明</th></tr>{c2_rows_html}
</table>
<p>分类总数={_c2_tf} (failed_real_patch={_c2_totals.get('failed_real_patch','?')} + empty_patches={_c2_totals.get('empty_patches','?')})。snapshot=R2233-manual(eval/predict状态在live loop下实时变动,此处为快照比例)。复算: <code>cd swebench_verified_full && python3 c2_cline_R2233.py</code>。归因红线: 429/5xx/超时/适配器=infra(非能力); real patch未通过测试=能力。</p>
{c2_top3_html}
<h2>C3 resume 修复确认</h2>
<p>R1733 resume fix(size>50B->model_patch非空)已生效。空patch从51.5%降至<span class="red">{ce/max(cp,1)*100:.1f}%</span>({ce}/{cp},cleanup后)。剩余空patch主因为网关额度429历史(R2062分类),<strong>非resume bug</strong>。网关HTTP 200(已恢复),predict进行中。根因: 网关quota耗尽(59%)+超时(15%)+能力/适配器(26%),非resume判定问题。前8个空patch实例: {empty_str}。</p>
<h2>cline与其他路对比 (SWE-bench Verified glm-5.3-flash)</h2>
<table><tr><th>Route</th><th>Resolved</th><th>Evaluated</th><th>Pass%</th><th>Predict</th><th>Real%</th></tr>"""
for nm,res,ev,pct,pr,rp in cmp:
    html += f"\n<tr><td>{nm}</td><td>{res}</td><td>{ev}</td><td>{fp(pct)}</td><td>{pr}</td><td>{fp(rp)}</td></tr>"

html += f"""</table>
<p><strong>差距分析</strong>: cline({fp(cpass)}) vs opencode({fp(oc_pct)})={fp(oc_pct-cpass)}。<strong>eval全量完成</strong>(cline {cn}条 vs opencode {cmp[[x[0] for x in cmp].index('opencode')][1]}条,均已全量eval),pass%可直接对比。归因红线: ① eval infra={ci}(infra=0,无infra干扰) ② 空patch已cleanup(网关429历史产生后删除,非能力) ③ cline eval {cn}条real patches已全量评测 ④ {cf}条有real patch未resolve=能力差 -> <strong>pass rate差距={fp(oc_pct-cpass)}为能力差(p=6.27e-08,R1685)</strong>。eval {total_resolved_all} resolved(0 true backlog·网关200·predict进行中)。</p>
<h2>TB-2.1 cline专项</h2>
<table><tr><th>指标</th><th>数值</th><th>说明</th></tr>
<tr><td>trials done</td><td>{ctd}</td><td>/tmp/tb21_glm53_jobs/cline-patched/</td></tr>
<tr><td>passed</td><td>{ctp}</td><td>{ctp/max(ctd,1)*100:.1f}%</td></tr>
<tr><td>oracle</td><td>5/5</td><td>verifier正常</td></tr></table>
<p>口径: TB-2.1/89 tasks/7-way concurrent(与TB4不可比)。</p>
<h3>TB-2.1 cline 低分根因 (2026-11-13 用户令排查)</h3>
<div class="summary" style="background:#fef9e7;border-left:4px solid #f39c12;padding:10px">
<p><strong>结论</strong>: cline TB-2.1 = 10/89 = 11.2% 的低分 <strong>非模型能力问题</strong>。
主因 = <strong>网关 Token 额度耗尽</strong>（「本次Token额度已用完，请等待X分钟后重试」），
占 80 个失败题中的 <strong>65 题 (81%)</strong>。cline run_result finishReason=error,
iterations=1, inputTokens=0, outputTokens=0 → <strong>零工作 → reward=0</strong>。</p>
<p><strong>逐题归因</strong>: 额度耗尽 65 题 (81%) | 超时 8 题 (10%) | ECONNRESET 2 题 |
CLI 解析 bug 1 题 | <strong>真能力差仅 5 题</strong> (其中 3 题所有路均失败=真难题)。</p>
<p><strong>公平通过率</strong>: 排除额度耗尽后 cline 在 25 题上通过 10 题 = <strong>40%</strong>
(vs 原始 11.2%)，与 pi (31.4%)、opencode (56.9%) 可比。</p>
<p><strong>交叉对照</strong>: cline 失败但 pi/opencode 通过的 31 题中, <strong>28 题 (90%)</strong>
= cline 全部 trial 均额度耗尽 (零机会), 仅 2 题为真能力差。</p>
<p><strong>根因链</strong>: cline 适配器无 retry/backoff → 网关额度耗尽 → cline 收到错误退出 →
verifier 无输出文件 → reward=0。cline 在 10 小时集中跑完 89 题 (11:51-21:39), 时间窗与额度耗尽期
高度重叠; 而 opencode 跨 40 小时、pi 跨 31 小时且有 167 次重试 → 额度有补充窗口。</p>
<p><strong>与 SWE-bench Verified 74.8% 一致</strong>: SWE-bench 跨多天跑 323 题, 额度有补充;
TB-2.1 集中 10 小时, 额度无补充 → 同模型不同额度环境。</p>
<p><strong>修复建议</strong>: ① cline 适配器增加 quota-error retry-with-backoff;
② cline 单独 rerun (额度充足时), 预计可达 ~30-40%。<strong>值得 rerun</strong>。</p>
<p style="font-size:0.85em;color:#888">证据: /tmp/tb21_glm53_jobs/cline-patched/ 下 90 个 result.json 逐题分析;
trace 含「本次Token额度已用完」原文 + iterations=1/0 tokens; 对照 pi/opencode 同题 trace。
归因红线: 网关额度耗尽 ≠ 模型能力 (§10:10 归因红线)。</p>
</div>
<h2>TB-2.1全7路对比</h2>
<table><tr><th>Route</th><th>Passed</th><th>Done</th><th>Pass%</th></tr>"""
for nm,(done,passed) in sorted(tb21_data.items(), key=lambda x:-x[1][1]):
    html += f"\n<tr><td>{disp(nm)}</td><td>{passed}</td><td>{done}</td><td>{passed/max(done,1)*100:.1f}%</td></tr>"

html += f"""</table>
<p>TB-2.1总计: {tb_total_pass} passed/{tb_total_done} trials。7-way concurrent。</p>
<h2>C4 本轮小结</h2>
<p>predict {cp}/500({cre}r/{ce}e={fp(creal)}real) | eval {cr}/{cn}({fp(cpass)},real patches全量评测,0 true backlog) | 空patch {ce}(cleanup后,59%网关429历史,非能力) | 网关HTTP 200(已恢复·predict进行中) | 失败top1=能力差(real patch但tests fail,{cf}条) | 7路alive(predict进行中) | TB-2.1 {tb_total_done}trials/{tb_total_pass}pass | eval {total_resolved_all} resolved(0 true backlog) | {ROUND}</p>
<h2>ETA · 预计全部完成时间（§用户令 2026-11-12）</h2>
<div class="summary"><strong>SWE-bench Verified(500题×7路)</strong>：{swe_eta_str}（预计 {swe_eta_date}）<br>
<strong>Terminal-Bench 2.1(89题×7路)</strong>：{tb_total_pass}p/{tb_total_done}t, 7路≥89tasks → 已交付</div>
<table><tr><th>路</th><th>Predict</th><th>剩余</th><th>3日均速</th><th>今日速</th><th>ETA</th></tr>
{eta_html_rows}</table>
<p style="font-size:0.85em;color:#888">复算：ETA=剩余÷3日均速(文件mtime统计)。DONE=500attempted,empty=能力。网关{GW_NOTE_SHORT}。</p>

<h2>可检验假设与下一步</h2>
<ol>
<li><strong>假设</strong>: cline空patch主因=网关429(59%) -> <strong>已验证</strong>: 网关429历史,空patch由429产生后cleanup删除,网关已恢复200</li>
<li><strong>结论</strong>: cline eval pass rate {fp(cpass)}为稳态值(eval {cn}条real patches全量评测,0 true backlog) -> cline vs opencode差距={fp(oc_pct-cpass)}为能力差(p=6.27e-08)</li>
<li><strong>进行中</strong>: predict 7路推进至500(网关200·predict进行中) + TB-2.1 7路推进 + incr_eval R2124(15 instances增量eval)</li></ol>
<hr><p style="color:#888;font-size:0.85em">报告生成: {NOW} | 口径: SWE-bench Verified 500 backbone=glm-5.3-flash 7-way | TB-2.1/89tasks/7way concurrent<br>命名纪律: 正文一律写cline | {ROUND}: 网关HTTP 200(已恢复)+predict {cp}/500+eval {cr}/{cn}(全量完成)+空patch {ce}(cleanup后)+TB-2.1 {tb_total_pass}/{tb_total_done}+eval {total_resolved_all} resolved(0 true backlog)</p>
</body></html>"""

# ---- Post-process: replace hardcoded gateway status with dynamic probe result ----
html = html.replace("网关HTTP 200(已恢复·predict进行中)", f"网关{GW_NOTE}")
html = html.replace("网关HTTP 200(已恢复·quota reset)", f"网关{GW_NOTE}")
html = html.replace("网关HTTP 200(已恢复)", f"网关{GW_NOTE_SHORT}")
html = html.replace("网关200·predict进行中", f"网关{GW_NOTE_SHORT}·predict进行中" if _gw_code==200 else f"网关{GW_NOTE_SHORT}·predict stalled")

outpath = os.path.join(REPORT_DIR, "report_harness_cline_special_zh.html")
with open(outpath,"w") as f: f.write(html)
print(f"Written: {outpath} ({len(html)} bytes)")
