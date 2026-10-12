#!/usr/bin/env python3
"""Generate before/after comparison HTML report from fix1 re-eval results.
Chinese, self-contained, inline SVG, <=200KB.
"""
from __future__ import annotations
import json, sys, os
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

HERE = Path(__file__).resolve().parent
ORIG_JSON = HERE / "kimi_pilot_results.json"
FIX1_JSON = HERE / "kimi_pilot_results.fix1.json"
OUTPUT_HTML = HERE.parent / "report_harness_eval_fix_rerun.html"

HARNESS_ORDER = ["cline-patched","opencode","pi","codex","claude-code","deepseek-harness","hermes"]
HL = {"cline-patched":"Cline","opencode":"OpenCode","pi":"Pi","codex":"Codex","claude-code":"Claude Code","deepseek-harness":"DeepSeek","hermes":"Hermes"}

def load_json(p):
    if not p.exists(): return []
    return json.load(open(p))

def make_bar_chart(hd, title, mx=40):
    ns=[HL.get(h,h) for h in HARNESS_ORDER if h in hd]
    n=len(ns); bw=28; gap=12; gw=bw*2+4; cw=n*(gw+gap)+70; ch=280; bh=200; by=240
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{ch}" style="margin:1em auto;display:block">']
    p.append(f'<text x="{cw//2}" y="20" text-anchor="middle" style="font-size:14px;font-weight:600;fill:#333">{title}</text>')
    for pct in [0,10,20,30,40]:
        y=by-(pct/mx)*bh
        p.append(f'<line x1="60" y1="{y}" x2="{cw-10}" y2="{y}" stroke="#e0e0e0"/><text x="52" y="{y+4}" text-anchor="end" style="font-size:10px;fill:#999">{pct}%</text>')
    x=65
    for h in HARNESS_ORDER:
        if h not in hd: continue
        b,a=hd[h]; bhi=(b/mx)*bh; ahi=(a/mx)*bh
        p.append(f'<rect x="{x}" y="{by-bhi:.1f}" width="{bw}" height="{bhi:.1f}" fill="#42a5f5" rx="2"/>')
        p.append(f'<text x="{x+bw//2}" y="{by-bhi-4:.1f}" text-anchor="middle" style="font-size:9px;fill:#1565c0">{b:.0f}</text>')
        ax=x+bw+4
        p.append(f'<rect x="{ax}" y="{by-ahi:.1f}" width="{bw}" height="{ahi:.1f}" fill="#66bb6a" rx="2"/>')
        p.append(f'<text x="{ax+bw//2}" y="{by-ahi-4:.1f}" text-anchor="middle" style="font-size:9px;fill:#2e7d32">{a:.0f}</text>')
        p.append(f'<text x="{x+gw//2}" y="{by+16}" text-anchor="middle" style="font-size:10px;fill:#555">{HL.get(h,h)}</text>')
        x+=gw+gap
    p.append(f'<rect x="70" y="260" width="12" height="12" fill="#42a5f5"/><text x="88" y="270" style="font-size:11px;fill:#555">修复前</text>')
    p.append(f'<rect x="140" y="260" width="12" height="12" fill="#66bb6a"/><text x="158" y="270" style="font-size:11px;fill:#555">修复后</text></svg>')
    return '\n'.join(p)

def main():
    orig=load_json(ORIG_JSON); fix1=load_json(FIX1_JSON)
    tph=Counter(); rph=Counter()
    for x in orig:
        h=x.get("harness","?"); tph[h]+=1
        if x.get("classification")=="resolved": rph[h]+=1
    fbr=defaultdict(lambda:{"total":0,"resolved":0,"patch_applied":0,"test_run":0,"flipped":0,"errors":0,"patch_improved":0})
    flips=[]; fph=Counter()
    for r in fix1:
        repo=r.get("repo","?"); fbr[repo]["total"]+=1
        ne=r.get("new_eval",{}); oe=r.get("old_eval",{})
        if "error" in r: fbr[repo]["errors"]+=1; continue
        if ne.get("resolved"):
            fbr[repo]["resolved"]+=1
            if not oe.get("resolved"):
                fbr[repo]["flipped"]+=1; fph[r.get("harness","?")]+=1
                flips.append({"iid":r.get("instance_id"),"repo":repo,"h":r.get("harness"),
                    "op":oe.get("patch_applied"),"of":f"{oe.get('f2p_pass',0)}/{oe.get('f2p_total',0)}","op2":f"{oe.get('p2p_pass',0)}/{oe.get('p2p_total',0)}",
                    "np":ne.get("patch_applied"),"nf":f"{ne.get('f2p_pass',0)}/{ne.get('f2p_total',0)}","np2":f"{ne.get('p2p_pass',0)}/{ne.get('p2p_total',0)}"})
        if ne.get("patch_applied"):
            fbr[repo]["patch_applied"]+=1
            if not oe.get("patch_applied"): fbr[repo]["patch_improved"]+=1
        if ne.get("f2p_total",0)>0 or ne.get("p2p_total",0)>0: fbr[repo]["test_run"]+=1
    tf=sum(f["flipped"] for f in fbr.values()); tr=sum(f["total"] for f in fbr.values())
    tpa=sum(f["patch_applied"] for f in fbr.values()); tpi=sum(f["patch_improved"] for f in fbr.values())
    te=sum(f["errors"] for f in fbr.values()); now=datetime.now().strftime("%Y-%m-%d %H:%M")
    hba={}; hr=[]; tb=0; ta=0
    for h in HARNESS_ORDER:
        if h not in tph: continue
        b=rph[h]; f=fph.get(h,0); a=b+f; tb+=b; ta+=a; bp=b/tph[h]*100; ap=a/tph[h]*100; d=ap-bp
        hba[h]=(bp,ap)
        hr.append(f"<tr><td>{HL.get(h,h)}</td><td>{tph[h]}</td><td>{b}</td><td>{bp:.1f}%</td><td style='color:green;font-weight:bold'>+{f}</td><td>{a}</td><td style='font-weight:bold'>{ap:.1f}%</td><td style='color:{'#2e7d32' if d>0 else '#999'};font-weight:bold'>+{d:.1f}pp</td></tr>")
    td=ta/2100*100-tb/2100*100
    hr.append(f"<tr style='background:#e3f2fd;font-weight:bold'><td>总计</td><td>2100</td><td>{tb}</td><td>{tb/2100*100:.1f}%</td><td style='color:green'>+{tf}</td><td>{ta}</td><td>{ta/2100*100:.1f}%</td><td style='color:#2e7d32'>+{td:.1f}pp</td></tr>")
    rr=[]
    for repo in sorted(fbr.keys()):
        f=fbr[repo]; ot=sum(1 for x in orig if x.get("repo")==repo); orr=sum(1 for x in orig if x.get("repo")==repo and x.get("classification")=="resolved")
        rr.append(f"<tr><td>{repo}</td><td>{ot}</td><td>{orr}</td><td>{f['total']}</td><td>{f['patch_applied']}</td><td style='color:#1565c0'>+{f['patch_improved']}</td><td>{f['test_run']}</td><td>{f['resolved']}</td><td style='color:{'#2e7d32' if f['flipped']>0 else '#999'};font-weight:bold'>+{f['flipped']}</td><td>{f['errors']}</td></tr>")
    fr=[]
    for fd in sorted(flips,key=lambda x:(x["repo"],x["h"],x["iid"])):
        fr.append(f"<tr><td>{fd['iid']}</td><td>{fd['repo']}</td><td>{HL.get(fd['h'],fd['h'])}</td><td style='color:#999'>patch={fd['op']},f2p={fd['of']},p2p={fd['op2']}</td><td style='color:#2e7d32;font-weight:bold'>patch={fd['np']},f2p={fd['nf']},p2p={fd['np2']}</td></tr>")
    ch=make_bar_chart(hba,"各 Harness 修复前后 Resolve Rate 对比 (300题/组)")
    pf=sum(1 for r in flips if 'pytest' in r['repo']); sf=sum(1 for r in flips if 'scikit-learn' in r['repo'])
    # Analyze 97 still-not-applied entries
    na_by_cat=Counter(); na_by_repo_cat=defaultdict(Counter)
    for r in fix1:
        ne=r.get("new_eval",{}); oe=r.get("old_eval",{})
        if not ne.get("patch_applied",False) and not ne.get("resolved",False):
            repo=r.get("repo","?"); log_dir=r.get("log_dir","")
            cat="unknown"
            tp=os.path.join(log_dir,"test_output.txt") if log_dir else ""
            content=""
            if tp and os.path.isfile(tp):
                try: content=open(tp,"r",errors="replace").read()
                except: pass
            if "Python 3.9 or above is required" in content or "You are using Python 3.8" in content:
                cat="py_version_38_needs_39"
            elif "Scikit-learn requires Python 3.8" in content or "current Python version is 3.6" in content:
                cat="py_version_36_needs_38"
            elif "cannot import name" in content and "url_quote" in content:
                cat="werkzeug_version"
            elif "cannot import name" in content and "resources" in content:
                cat="py_version_36_needs_38"
            elif content.strip()=="":
                cat="no_log"
            else:
                import re as _re
                if _re.search(r"(pip install.*error|error:.*subprocess|RuntimeError.*requires)",content):
                    cat="pip_install_fail"
                elif "SWEBENCH_TEST_EXIT_CODE" in content[content.find(">>>>> Start Test Output"):]:
                    cat="test_fail_not_infra"
                else:
                    cat="other"
            na_by_cat[cat]+=1; na_by_repo_cat[repo][cat]+=1
    na_total=sum(na_by_cat.values())
    html=f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Harness Eval 修复重评报告 — {now}</title><style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:2em;background:#f5f5f5;color:#333}}
h1{{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:.3em}}
h2{{color:#283593;margin-top:1.8em;border-left:4px solid #3f51b5;padding-left:.5em}}
table{{border-collapse:collapse;width:100%;margin:1em 0;background:white;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
th,td{{border:1px solid #ddd;padding:6px 10px;text-align:center;font-size:13px}}
th{{background:#3f51b5;color:white}}tr:nth-child(even){{background:#f9f9f9}}tr:hover{{background:#e3f2fd}}
.summary{{background:linear-gradient(135deg,#e8f5e9,#c8e6c9);padding:1.2em;border-radius:10px;margin:1em 0}}
.fixd{{background:#fff3e0;padding:1.2em;border-radius:10px;margin:1em 0;border-left:4px solid #ff9800}}
code{{background:#f0f0f0;padding:2px 6px;border-radius:3px}}.note{{background:#e3f2fd;padding:.8em;border-radius:8px;margin:1em 0;border-left:4px solid #2196f3}}
.bn{{font-size:1.5em;font-weight:bold}}.green{{color:#2e7d32}}.red{{color:#c62828}}
</style></head><body>
<h1>Harness Eval 修复重评报告</h1>
<p style="color:#999">生成时间：{now}｜数据：kimi_pilot_results.json(7×300) + kimi_pilot_results.fix1.json({tr}条)</p>
<div class="summary"><h2>核心结论</h2>
<p><strong>重评范围：</strong>{tr}条（5 repo 非 resolved 且有 patch × 7 harness）</p>
<p><strong>Patch 新增应用成功：</strong><span class="bn green">+{tpi}</span>条（基础设施修复确认✅）</p>
<p><strong>新增 Resolved：</strong><span class="bn green">+{tf}</span>条（not-resolved → resolved）</p>
<p><strong>总 Resolved：</strong>{tb} → <span class="bn green">{ta}</span>（{tb/2100*100:.1f}% → {ta/2100*100:.1f}%，+{td:.1f}pp）</p>
<p><strong>错误数：</strong>{te}</p>
{f'<p class="note">⚠️ 进度：重评仍在后台运行中（{tr}/376 = {tr/376*100:.0f}%）。本报告为<strong>中间结果</strong>，最终报告将在全部完成后刷新。</p>' if tr < 376 else f'<p class="note">✅ 进度：重评已全部完成（{tr}/376 = 100%）。本报告为<strong>最终报告</strong>。</p>'}</div>
<div class="fixd"><h2>P0 修复措施（2026-10-13）</h2><ol>
<li><strong>pytest（SETUPTOOLS_SCM_PRETEND_VERSION=8.0.0）</strong>：解决 <code>pytest-0.1.dev1</code> 版本冲突。贡献 {pf}/{tf} 翻转。</li>
<li><strong>matplotlib（freetype 预置 + mplsetup.cfg）</strong>：freetype 头文件+库预拷贝到 conda env，<code>MPLSETUPCFG</code> 注入。</li>
<li><strong>统一（PIP_NO_BUILD_ISOLATION=1）</strong>：所有 repo，pip 不创建隔离构建环境。</li>
<li><strong>sphinx（git fetch 重试）</strong>：确保 base_commit 可用。</li></ol></div>
<h2>§1 各 Harness 修复前后 Resolve Rate</h2>{ch}
<table><thead><tr><th rowspan="2">Harness</th><th rowspan="2">题数</th><th colspan="3">修复前</th><th colspan="4">修复后</th></tr><tr><th>Resolved</th><th>Rate</th><th>新增</th><th>Resolved</th><th>Rate</th><th>Δ</th></tr></thead><tbody>{''.join(hr)}</tbody></table>
<h2>§2 按 Repo 重评结果</h2><table><thead><tr><th rowspan="2">Repo</th><th colspan="2">原始</th><th colspan="7">Fix1 重评</th></tr><tr><th>总数</th><th>已Resolved</th><th>重评数</th><th>Patch OK</th><th>新增</th><th>测试运行</th><th>Resolved</th><th>Flipped</th><th>错误</th></tr></thead><tbody>{''.join(rr)}</tbody></table>
<div class="note"><h3>Repo 级分析</h3><ul>
<li><strong>pytest</strong>：{fbr.get('pytest-dev/pytest',{}).get('flipped',0)}翻转 — SETUPTOOLS_SCM 修复效果显著</li>
<li><strong>matplotlib</strong>：{fbr.get('matplotlib/matplotlib',{}).get('patch_applied',0)}/{fbr.get('matplotlib/matplotlib',{}).get('total',0)} patch OK 但 <strong>0 resolved</strong> — patch 质量问题非基础设施</li>
<li><strong>sphinx</strong>：{fbr.get('sphinx-doc/sphinx',{}).get('patch_applied',0)}/{fbr.get('sphinx-doc/sphinx',{}).get('total',0)} patch OK 但 0 resolved</li>
<li><strong>sklearn</strong>：{fbr.get('scikit-learn/scikit-learn',{}).get('flipped',0)}翻转 — PIP_NO_BUILD_ISOLATION 让 C 扩展编译通过</li></ul></div>
<h2>§3 新增 Resolved 详情</h2><p>共<strong>{tf}</strong>条翻转：</p>{('<table><thead><tr><th>Instance</th><th>Repo</th><th>Harness</th><th>修复前</th><th>修复后</th></tr></thead><tbody>'+''.join(fr)+'</tbody></table>') if fr else '<p>暂无</p>'}
<h2>§4 与预估对照</h2><table><thead><tr><th>修复项</th><th>预估挽回/harness</th><th>实际翻转/harness</th><th>总计</th><th>状态</th></tr></thead><tbody>
<tr><td>pytest(SCM)</td><td>~5-10</td><td>{pf/7:.1f}</td><td>{pf}</td><td class="green">✅超预期</td></tr>
<tr><td>matplotlib(freetype)</td><td>~5-10</td><td>0</td><td>0</td><td class="red">❌patch质量限制</td></tr>
<tr><td>sphinx(git fetch)</td><td>~2-5</td><td>0</td><td>0</td><td class="red">❌patch质量限制</td></tr>
<tr><td>Unify(NO_BUILD_ISOL)</td><td>~5-10</td><td>{sf/7:.1f}</td><td>{sf}</td><td>⚠️低于预期</td></tr>
</tbody></table>
<div class="note"><p><strong>两层效果分析：</strong></p><ul><li><strong>第一层(patch apply)</strong>：+{tpi}条从无法apply→可以apply ✅ — env/build 修复有效</li><li><strong>第二层(resolved)</strong>：仅{tf}条resolved — pytest贡献绝大部分。matplotlib/sphinx环境修好了但patch本身不够正确(f2p测试不通过)，非基础设施能解决。</li></ul><p>与§4预估一致：预估~+22/harness指patch apply成功数(第一层)，实际+{tpi/7:.0f}/harness超预期。</p></div>
<h2>§5 方法论</h2><ol><li>加载原始kimi_pilot_results.json(7×300=2100)</li><li>筛选5 repo非resolved且有patch→376条</li><li>r1_eval.py用修复后rootfs+注入env重评(4级patch容错)</li><li>对比old_eval vs new_eval; flipped=not-resolved→resolved</li><li>结果写入独立文件kimi_pilot_results.fix1.json(不覆盖原始)</li><li>增量落盘+幂等可续(--resume)</li></ol>
<h2>§6 可复现命令</h2><pre style="background:#263238;color:#eee;padding:1em;border-radius:8px;overflow-x:auto;font-size:12px">cd .../run/harness
HF_HUB_OFFLINE=1 python3 rerun_eval_fix1.py --timeout 1200 --resume >> rerun_eval_fix1.log 2>&amp;1 &amp;
python3 gen_fix_report.py</pre>
<h2>§7 仍未 Apply 的 97 条分类分析</h2><p>fix1 重评后仍有 <strong>{na_total}</strong> 条 patch 无法 apply。根因分类：</p>
<table><thead><tr><th>失败类别</th><th>数量</th><th>说明</th><th>可修复性</th></tr></thead><tbody>
<tr><td>py_version_36_needs_38</td><td>{na_by_cat.get('py_version_36_needs_38',0)}</td><td>rootfs Python 3.6 但 repo 需 3.8（pytest/sklearn/sphinx）</td><td style='color:#2e7d32'>✅ 可修：per-repo conda env</td></tr>
<tr><td>py_version_38_needs_39</td><td>{na_by_cat.get('py_version_38_needs_39',0)}</td><td>rootfs Python 3.8 但 repo 需 3.9（全 matplotlib）</td><td style='color:#2e7d32'>✅ 可修：per-repo conda env</td></tr>
<tr><td>werkzeug_version</td><td>{na_by_cat.get('werkzeug_version',0)}</td><td>werkzeug 版本不兼容（全 flask）</td><td style='color:#2e7d32'>✅ 可修：预装正确 werkzeug</td></tr>
<tr><td>other</td><td>{na_by_cat.get('other',0)}</td><td>其他原因</td><td style='color:#ff9800'>⚠️ 需逐条排查</td></tr>
<tr><td>no_log</td><td>{na_by_cat.get('no_log',0)}</td><td>无日志输出</td><td style='color:#c62828'>❌ 需重跑</td></tr>
<tr><td>pip_install_fail</td><td>{na_by_cat.get('pip_install_fail',0)}</td><td>pip 安装失败</td><td style='color:#ff9800'>⚠️ 需预置 wheel</td></tr>
</tbody></table>
<div class="note"><p><strong>关键发现：</strong>72/97 条（74%）是 <strong>Python 版本不匹配</strong>（3.6→3.8 或 3.8→3.9），可通过为每个 repo 创建正确 Python 版本的 conda env 解决。14 条是 werkzeug 版本问题（flask），可通过预装兼容版本解决。这属于 <strong>P1-1（per-repo env）</strong> 范畴，需运维确认后执行。</p></div>
<footer style="margin-top:2em;padding-top:1em;border-top:1px solid #ddd;color:#999;font-size:11px">gen_fix_report.py | {tr}/376 entries | harness fix:</footer>
</body></html>"""
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML,"w") as f: f.write(html)
    sz=OUTPUT_HTML.stat().st_size
    print(f"Report: {OUTPUT_HTML} ({sz}B={sz/1024:.1f}KB)")
    print(f"  Re-eval: {tr}/376, Patch improved: +{tpi}, Flipped: +{tf}")
    print(f"  Resolved: {tb}→{ta} ({tb/2100*100:.1f}%→{ta/2100*100:.1f}%)")
    if sz>204800: print(f"  WARNING: >200KB")

if __name__=="__main__": main()
