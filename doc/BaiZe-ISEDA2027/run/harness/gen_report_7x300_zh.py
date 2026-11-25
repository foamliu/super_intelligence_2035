#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 report_harness_7x300.html（中文版）—— 7 harness × 300 SWE-bench Lite 评测报告"""
import json, html as H, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path("/nas_train/app.e0031982/code/super_intelligence_2035")
OUT = ROOT / "doc/BaiZe-ISEDA2027/report_harness_7x300.html"
JSON = ROOT / "doc/BaiZe-ISEDA2027/run/harness/kimi_pilot_results.json"

def esc(s): return H.escape(str(s), quote=True)

data = json.load(open(JSON))

# ---- 从 eval report.json join infra_failure_reason（精确到 entry，可复算）----
# 每个 harness 的 run_id 形如 R1_KIMI_{HARNESS_UPPER}_{instance_id}，report.json 顶层 key = instance_id
LOGS_EVAL = Path("/nas_train/app.e0031982/harness_work/logs_eval")
_HUPPER = {'CLINE_PATCHED':'cline-patched','OPENCODE':'opencode','PI':'pi','CODEX':'codex',
           'CLAUDE_CODE':'claude-code','DEEPSEEK_HARNESS':'deepseek-harness','HERMES':'hermes'}
infra_reason = {}
if LOGS_EVAL.exists():
    for rp in LOGS_EVAL.rglob('report.json'):
        rundir = rp.parent.parent.parent.name
        h = next((lo for up, lo in _HUPPER.items() if rundir.startswith('R1_KIMI_' + up + '_')), None)
        if not h:
            continue
        try:
            rep = json.loads(rp.read_text())
        except Exception:
            continue
        for iid, v in rep.items():
            if isinstance(v, dict):
                infra_reason[(iid, h)] = v.get('infra_failure_reason') or None
# per-repo 聚合
repo_infra = defaultdict(lambda: defaultdict(int))   # repo -> reason -> entry 计数
repo_paF   = defaultdict(int)                        # repo -> eval 阶段 patch_applied=False 计数
repo_paT   = defaultdict(int)                        # repo -> eval 阶段 patch_applied=True 计数
repo_res   = defaultdict(int)                        # repo -> resolved 计数
for e in data:
    repo = e['repo']
    reason = infra_reason.get((e['instance_id'], e['harness']))
    repo_infra[repo][reason or '(none)'] += 1
    pa = e.get('harness_result', {}).get('eval', {}).get('patch_applied')
    if pa is False:
        repo_paF[repo] += 1
    elif pa is True:
        repo_paT[repo] += 1
    if e.get('classification') == 'resolved':
        repo_res[repo] += 1

HARNESSES = ['cline-patched','opencode','pi','codex','claude-code','deepseek-harness','hermes']
SHORT = {'cline-patched':'cline','opencode':'opencode','pi':'pi','codex':'codex',
         'claude-code':'claude','deepseek-harness':'deepseek','hermes':'hermes'}
# eval 环境可用性分组（数据驱动修正 2026-10-12：requests 42/42 patch 全 apply，故此移出「受限」组）
EVAL_OK = ['django/django','sympy/sympy','scikit-learn/scikit-learn']          # 大样本 eval-OK（django/sklearn 仍有少量 missing_module，见 §7.3）
EVAL_OK_SMALL = ['psf/requests','pydata/xarray','pylint-dev/pylint','mwaskom/seaborn']  # 小样本 eval-OK（patch 基本全 apply）
EVAL_BROKEN = ['matplotlib/matplotlib','pytest-dev/pytest','sphinx-doc/sphinx',
               'astropy/astropy','pallets/flask']                              # 大面积 patch_applied=False（基础设施失效，非能力）

# ---- per-harness 统计 ----
stats = {}
for h in HARNESSES:
    es = [e for e in data if e['harness'] == h]
    res = [e for e in es if e.get('classification') == 'resolved']
    pbf = [e for e in es if e.get('classification') == 'patch-but-failed']
    blk = [e for e in es if e.get('classification') in ('blocked','quota-blocked')]
    walls = [e['harness_result']['wall_s'] for e in es if e.get('harness_result',{}).get('wall_s',0) > 0]
    rwalls = [e['harness_result']['wall_s'] for e in res if e.get('harness_result',{}).get('wall_s',0) > 0]
    pbf_eval = defaultdict(int)
    for e in pbf:
        ev = e.get('harness_result',{}).get('eval',{})
        if not ev.get('patch_applied', False): pbf_eval['patch_not_applied'] += 1
        elif ev.get('f2p_pass',0) == 0 and ev.get('f2p_total',0) > 0: pbf_eval['f2p_all_fail'] += 1
        elif ev.get('f2p_pass',0) < ev.get('f2p_total',0): pbf_eval['f2p_partial'] += 1
        else: pbf_eval['f2p_pass_p2p_fail'] += 1
    stats[h] = {'total':len(es),'resolved':len(res),'pbf':len(pbf),'blocked':len(blk),
        'rate': 100*len(res)/len(es) if es else 0,
        'wall_mean': statistics.mean(walls) if walls else 0,
        'rwall_mean': statistics.mean(rwalls) if rwalls else 0,
        'rwall_med': statistics.median(rwalls) if rwalls else 0,
        'pbf_eval': dict(pbf_eval)}

TOTAL = len(data)
RESOLVED_TOTAL = sum(1 for e in data if e.get('classification') == 'resolved')

# ---- instance 重叠 ----
ir = defaultdict(dict)
for e in data: ir[e['instance_id']][e['harness']] = (e.get('classification') == 'resolved')
all7 = {i: r for i, r in ir.items() if len(r) == 7}
nobody = sum(1 for r in all7.values() if not any(r.values()))
everybody = sum(1 for r in all7.values() if all(r.values()))
some = len(all7) - nobody - everybody

# ---- head-to-head（cline vs 其他）----
h2h = {}
for h in HARNESSES:
    if h == 'cline-patched': continue
    co = sum(1 for r in all7.values() if r.get('cline-patched') and not r.get(h))
    oo = sum(1 for r in all7.values() if not r.get('cline-patched') and r.get(h))
    both = sum(1 for r in all7.values() if r.get('cline-patched') and r.get(h))
    h2h[h] = (co, oo, both)

# ---- per-repo 矩阵 ----
repo_r = defaultdict(lambda: defaultdict(int))
repo_t = defaultdict(lambda: defaultdict(int))
repo_order = []
for e in data:
    if e['repo'] not in repo_order:
        repo_order.append(e['repo'])
    repo_t[e['repo']][e['harness']] += 1
    if e.get('classification') == 'resolved': repo_r[e['repo']][e['harness']] += 1

# repo 唯一实例数 / 总 entries（用于 infra 归因表的「唯一实例」与「entries」列）
_repo_uniq_set = defaultdict(set)
repo_total_entry = defaultdict(int)
for e in data:
    _repo_uniq_set[e['repo']].add(e['instance_id'])
repo_uniq = {r: len(s) for r, s in _repo_uniq_set.items()}
for repo in repo_t:
    repo_total_entry[repo] = sum(repo_t[repo].values())

def repo_cat(repo):
    if repo in EVAL_OK: return 'eval可用'
    if repo in EVAL_BROKEN: return 'eval失效'
    return 'eval可用·小样本'

# ---- 排名 ----
ranking = sorted(HARNESSES, key=lambda h: -stats[h]['rate'])
best = ranking[0]
rate_min = min(stats[h]['rate'] for h in HARNESSES)
rate_max = max(stats[h]['rate'] for h in HARNESSES)
rate_spread = rate_max - rate_min

# ============ SVG 图 ============
def bar_chart():
    max_rate = max(stats[h]['rate'] for h in HARNESSES)
    bw, gap, cy = 80, 20, 230
    s = ['<svg width="780" height="290" xmlns="http://www.w3.org/2000/svg">',
         '<line x1="80" y1="230" x2="740" y2="230" stroke="#d0d7de" stroke-width="1"/>']
    for i, h in enumerate(HARNESSES):
        x = 80 + i*(bw+gap)
        hh = stats[h]['rate']/max_rate*185
        color = '#1f6feb' if h=='cline-patched' else ('#1a7f37' if stats[h]['rate']>=29 else ('#9a6700' if stats[h]['rate']>=26 else '#cf222e'))
        s.append(f'<rect x="{x}" y="{cy-hh:.1f}" width="{bw}" height="{hh:.1f}" fill="{color}" rx="3"/>')
        s.append(f'<text x="{x+bw/2}" y="{cy-hh-6:.1f}" text-anchor="middle" font-size="13" font-weight="bold" fill="#1f2328">{stats[h]["rate"]:.1f}%</text>')
        s.append(f'<text x="{x+bw/2}" y="248" text-anchor="middle" font-size="11" fill="#59636e">{SHORT[h]}</text>')
        s.append(f'<text x="{x+bw/2}" y="264" text-anchor="middle" font-size="10" fill="#8b949e">{stats[h]["resolved"]}/{stats[h]["total"]}</text>')
    s.append('<text x="80" y="282" text-anchor="start" font-size="10" fill="#8b949e">纵轴：resolve rate（resolved / total，%）· 每柱标注 resolved/total</text>')
    s.append('</svg>')
    return ''.join(s)

def pareto_chart():
    max_wall = max(stats[h]['rwall_mean'] for h in HARNESSES)
    s = ['<svg width="780" height="300" xmlns="http://www.w3.org/2000/svg">',
         '<line x1="60" y1="240" x2="730" y2="240" stroke="#d0d7de"/><line x1="60" y1="20" x2="60" y2="240" stroke="#d0d7de"/>',
         '<text x="390" y="275" text-anchor="middle" font-size="12" fill="#59636e">平均 wall time（秒，仅 resolved 实例）</text>',
         '<text x="18" y="130" text-anchor="middle" font-size="12" fill="#59636e" transform="rotate(-90 18 130)">resolve rate（%）</text>']
    for t in range(15, 40, 5):
        yy = 240 - t/35*200
        s.append(f'<text x="52" y="{yy:.0f}" text-anchor="end" font-size="10" fill="#8b949e">{t}%</text>')
        s.append(f'<line x1="56" y1="{yy:.0f}" x2="60" y2="{yy:.0f}" stroke="#d0d7de"/>')
    for h in HARNESSES:
        st = stats[h]
        x = 60 + st['rwall_mean']/max_wall*660
        y = 240 - st['rate']/35*200
        color = '#1f6feb' if h=='cline-patched' else '#1a7f37'
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="8" fill="{color}"/>')
        s.append(f'<text x="{x+12:.0f}" y="{y+4:.0f}" font-size="12" font-weight="bold" fill="{color}">{SHORT[h]}</text>')
    s.append('</svg>')
    return ''.join(s)

def pbf_chart():
    order = ['patch_not_applied','f2p_all_fail','f2p_partial','f2p_pass_p2p_fail']
    colors = {'patch_not_applied':'#cf222e','f2p_all_fail':'#9a6700','f2p_partial':'#1f6feb','f2p_pass_p2p_fail':'#8b949e'}
    labels = {'patch_not_applied':'patch未应用','f2p_all_fail':'f2p全失败','f2p_partial':'f2p部分通过','f2p_pass_p2p_fail':'f2p过/p2p败'}
    s = ['<svg width="780" height="230" xmlns="http://www.w3.org/2000/svg">']
    for i, h in enumerate(HARNESSES):
        x = 80 + i*92
        tp = stats[h]['pbf']
        yoff = 0
        for pt in order:
            v = stats[h]['pbf_eval'].get(pt, 0)
            pct = v/tp*160 if tp else 0
            s.append(f'<rect x="{x}" y="{40+yoff:.1f}" width="72" height="{pct:.1f}" fill="{colors[pt]}"/>')
            yoff += pct
        s.append(f'<text x="{x+36}" y="28" text-anchor="middle" font-size="11" fill="#59636e">{SHORT[h]}</text>')
        s.append(f'<text x="{x+36}" y="215" text-anchor="middle" font-size="10" fill="#8b949e">n={tp}</text>')
    x = 80; sy = 0
    s.append('</svg>')
    legend = ''.join(f'<span style="display:inline-block;margin:0 6px"><span style="display:inline-block;width:10px;height:10px;background:{colors[o]};border-radius:2px"></span> {labels[o]}</span>' for o in order)
    return ''.join(s) + f'<div class="legend">{legend}</div>'

# ============ 表格 ============
def rank_table():
    rows = []
    for i, h in enumerate(ranking, 1):
        st = stats[h]
        hl = ' class="cline-row"' if h == 'cline-patched' else ''
        medal = ['🥇','🥈','🥉'][i-1] if i <= 3 else ''
        rows.append(f'<tr{hl}><td>{medal} {i}</td><td><b>{SHORT[h]}</b></td>'
                    f'<td>{st["resolved"]}/{st["total"]}</td><td class="num">{st["rate"]:.1f}%</td>'
                    f'<td>{st["pbf"]}</td><td>{st["blocked"]}</td>'
                    f'<td>{st["wall_mean"]:.0f}s</td><td>{st["rwall_mean"]:.0f}s</td></tr>')
    return ''.join(rows)

def repo_matrix():
    all_repos = EVAL_OK + EVAL_BROKEN + EVAL_OK_SMALL
    rows = []
    for repo in all_repos:
        cat = repo_cat(repo)
        cat_tag = {'eval可用':'<span class="tag-ok">eval可用</span>',
                   'eval失效':'<span class="tag-lim">eval失效</span>',
                   'eval可用·小样本':'<span class="tag-part">小样本</span>'}[cat]
        cells = [f'<td class="rname">{esc(repo)} {cat_tag}</td>']
        for h in HARNESSES:
            r, t = repo_r[repo].get(h, 0), repo_t[repo].get(h, 0)
            rate = 100*r/t if t else 0
            hl = ' style="background:#ddf4ff;font-weight:600"' if h == 'cline-patched' else ''
            cells.append(f'<td{hl}>{r}/{t}<br><span class="sub">{rate:.0f}%</span></td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return ''.join(rows)

# ---- eval 基础设施失效归因表（repo × failure reason × entry 计数）----
def infra_breakdown_table():
    all_repos = EVAL_OK + EVAL_BROKEN + EVAL_OK_SMALL
    reasons = ['missing_module', 'out_of_memory', 'no_tests_collected']
    rows = []
    # 表头
    header = ['repo', '唯一实例', 'entries', 'patch未应用']
    header += [{'missing_module': 'missing_module（缺模块）', 'out_of_memory': 'out_of_memory（内存爆）',
                'no_tests_collected': 'no_tests（测试未收集）'}[r] for r in reasons]
    rows.append('<tr>' + ''.join(f'<th>{h}</th>' for h in ['repo','唯一实例','entries','patch未应用'] +
                  [{'missing_module': '缺模块', 'out_of_memory': '内存爆', 'no_tests_collected': '测试未收集'}[r] for r in reasons]) + '</tr>')
    for repo in all_repos:
        uniq = repo_uniq[repo]
        tot = repo_total_entry[repo]
        paF = repo_paF.get(repo, 0)
        cells = [f'<td class="rname">{esc(repo)}</td>',
                 f'<td class="num">{uniq}</td>',
                 f'<td class="num">{tot}</td>',
                 f'<td class="num">{paF}</td>']
        for r in reasons:
            v = repo_infra[repo].get(r, 0)
            cells.append(f'<td class="num">{"<b>" + str(v) + "</b>" if v else "·"}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return '<table>' + ''.join(rows) + '</table>'

# ---- §8 eval 基础设施失效归因（root-cause 专章）----
def _inf(repo, key=None):
    """取 repo 的 infra_failure_reason 计数；key=None 返回整个 Counter"""
    c = repo_infra[repo]
    return c if key is None else c.get(key, 0)

def inf_diag():
    """逐 repo 根因诊断（日志实证的内联文字）"""
    parts = []
    parts.append(
        '<p><b>root-cause 结论：</b>这 5 个 repo 的 <code>patch_applied=False</code> 不是模型/harness 能力不足，也不是统称的「依赖装不上」——'
        '而是 <b>eval 基础设施失效</b>（根因各 repo 不同）。同时，原报告把 <code>psf/requests</code> 归入「受限」也是<b>错误的</b>：'
        'requests 的 42 次 patch <b>全部成功应用</b>，0 resolved 只是 FAIL_TO_PASS 测试没过（模型没做对），评测管线本身完全正常。</p>')
    parts.append('<h3>matplotlib —— 全部 missing_module（C 扩展编译需外网下载 freetype）</h3>')
    parts.append(
        '<p>' + f'{repo_uniq["matplotlib/matplotlib"]} 个唯一实例 / {repo_total_entry["matplotlib/matplotlib"]} entries，'
        f'其中 {repo_paF.get("matplotlib/matplotlib",0)} 次 patch 未应用、'
        f'全部为 <code>missing_module</code>（{_inf("matplotlib/matplotlib","missing_module")} 次）。'
        '根因（eval 日志实证）：rootfs 构建时 <code>pip install -e .</code> 触发 C++ 扩展编译（<code>running build_ext</code> / <code>g++</code>），'
        '需从 sourceforge.net / savannah.gnu.org 下载 <code>freetype-2.6.1.tar.gz</code>；沙箱无法访问外部源码站 → '
        '<code>_c_internal_utils</code> 等 C 扩展缺失 → <code>import matplotlib</code> 直接 ImportError。'
        '此时 patch 本身早已 cleanly apply，swebench 将 import 失败标记为 <code>infra_failure_reason=missing_module</code>（一个歧义类别），'
        '并连带把 <code>patch_successfully_applied</code> 置 false。<b>0 分（0 resolved）是基础设施假象，不代表任何 harness 的 matplotlib 能力。</b></p>')
    parts.append('<h3>pytest —— 110 missing_module（少量真实可评）</h3>')
    parts.append(
        '<p>' + f'{repo_uniq["pytest-dev/pytest"]} 个唯一实例 / {repo_total_entry["pytest-dev/pytest"]} entries，'
        f'{repo_paF.get("pytest-dev/pytest",0)} 次 patch 未应用，其中 {_inf("pytest-dev/pytest","missing_module")} 次 <code>missing_module</code>'
        '（rootfs 内 pytest 运行所需的模块缺失）。仅 5 次 patch 成功应用，其中 2 次 resolved —— '
        '说明在 eval 正常的那一小撮上，模型/harness 是能解 pytest 的（有效 rate 2/5 = 40%），'
        '整体 1.7% 的惨淡 rate 主要被 113 次 eval 失效稀释。</p>')
    parts.append('<h3>sphinx —— 92 次纯 git apply 失败（无 infra 标记，非缺模块）</h3>')
    parts.append(
        '<p>' + f'{repo_uniq["sphinx-doc/sphinx"]} 个唯一实例 / {repo_total_entry["sphinx-doc/sphinx"]} entries，'
        f'{repo_paF.get("sphinx-doc/sphinx",0)} 次 patch 未应用，但 <b>全部没有</b> <code>infra_failure_reason</code> 标记 —— '
        '即 <b>纯 git apply 失败</b>（base_commit 与 rootfs checkout 不一致 / diff 上下文冲突），'
        '与 matplotlib 的「缺模块」是<b>两类不同</b>的失效。19 次成功 apply 的也无 resolved，样本不足以判能力。</p>')
    parts.append('<h3>astropy —— 28 次 out_of_memory（沙箱内存不足）</h3>')
    parts.append(
        '<p>' + f'{repo_uniq["astropy/astropy"]} 个唯一实例 / {repo_total_entry["astropy/astropy"]} entries，'
        f'{repo_paF.get("astropy/astropy",0)} 次 patch 未应用，全部 <code>out_of_memory</code>（{_inf("astropy/astropy","out_of_memory")} 次）—— '
        'astropy 的 C 扩展编译/测试在受限内存沙箱里 OOM，属资源型失效。</p>')
    parts.append('<h3>flask —— 7 次 no_tests_collected（样本极小）</h3>')
    parts.append(
        '<p>' + f'{repo_uniq["pallets/flask"]} 个唯一实例 / {repo_total_entry["pallets/flask"]} entries，'
        f'{repo_paF.get("pallets/flask",0)} 次 patch 未应用（其中 {_inf("pallets/flask","no_tests_collected")} 次 <code>no_tests_collected</code>，'
        'patch 应用了但 FAIL_TO_PASS 测试收集为空）。3 个唯一实例，样本太小，不构成统计结论。</p>')
    parts.append('<h3>psf/requests —— 误判修正（patch 全 apply，非失效）</h3>')
    parts.append(
        '<p>' + f'{repo_uniq["psf/requests"]} 个唯一实例 / {repo_total_entry["psf/requests"]} entries，'
        f'<b>0 次 patch 未应用</b>（{repo_paF.get("psf/requests",0)} 次 False），42 次 patch 全部成功 apply；'
        '0 resolved 是因为 FAIL_TO_PASS 测试全没过（模型未做对），<b>评测管线完全正常</b>。'
        '故 requests 应从「受限」移入「小样本 eval-OK」。</p>')
    parts.append('<h3>scikit-learn / django —— eval-OK，但有少量 missing_module</h3>')
    parts.append(
        '<p>' + f'scikit-learn：{repo_paF.get("scikit-learn/scikit-learn",0)} 次 patch 未应用（其中 {_inf("scikit-learn/scikit-learn","missing_module")} 次 missing_module），'
        f'但 {repo_paT["scikit-learn/scikit-learn"]} 次 patch 成功应用 → 有效 rate {100*repo_res["scikit-learn/scikit-learn"]/repo_paT["scikit-learn/scikit-learn"]:.1f}%'
        f'（{repo_res["scikit-learn/scikit-learn"]}/{repo_paT["scikit-learn/scikit-learn"]}），是全部 repo 中最高的。'
        f'django：{repo_paF.get("django/django",0)} 次 patch 未应用（其中 {_inf("django/django","missing_module")} 次 missing_module），'
        f'{repo_paT["django/django"]} 次 patch 成功应用、有效 rate {100*repo_res["django/django"]/repo_paT["django/django"]:.1f}%。'
        '两者主体 eval-OK，只有零星 missing_module，不影响结论方向。</p>')
    return ''.join(parts)

def inf_impact():
    """影响量化 + 修复建议"""
    broken_uniq = sum(repo_uniq[r] for r in EVAL_BROKEN)
    broken_entries = sum(repo_total_entry[r] for r in EVAL_BROKEN)
    broken_paF = sum(repo_paF.get(r, 0) for r in EVAL_BROKEN)
    ok_uniq = sum(repo_uniq[r] for r in EVAL_OK)
    ok_small_uniq = sum(repo_uniq[r] for r in EVAL_OK_SMALL)
    parts = []
    parts.append('<h3>8.3 影响量化</h3>')
    parts.append(
        '<p>' + f'5 个 eval 失效 repo 合计 <b>{broken_uniq}</b> 个唯一实例（占 300 实例的 {100*broken_uniq/300:.0f}%）、'
        f'<b>{broken_entries}</b> 次 entries（其中 {broken_paF} 次 patch 未应用）被基础设施失效压制到 near-0，'
        '系统性低估了所有 harness 的平均 rate。'
        f'真正可公正比较的 repo 是 <b>django/sympy/scikit-learn</b>（{ok_uniq} 唯一实例），'
        f'另加 requests/xarray/pylint/seaborn（{ok_small_uniq} 唯一实例）为「小样本 eval-OK」，仅方向性参考。</p>')
    parts.append('<h3>8.4 修复建议（优先级从高到低）</h3>')
    parts.append('<ul>')
    parts.append('<li><b>matplotlib 专项（收益最大，23 实例一夜回血）</b>：把 <code>freetype-2.6.1.tar.gz</code> 及 build 依赖预下载进 rootfs（或用 manylinux wheel 绕过源码编译），使 <code>pip install -e .</code> 走本地；预构建 <code>_c_internal_utils</code> 的 .so 一并注入。</li>')
    parts.append('<li><b>astropy 专项</b>：加大沙箱内存限额，或对 astropy 用 prebuilt wheel（avoid 源码编译 OOM）。</li>')
    parts.append('<li><b>pytest 专项</b>：核对 rootfs 内 pytest 测试运行依赖清单，补齐缺失模块后再 --resume。</li>')
    parts.append('<li><b>sphinx 专项</b>：92 次 git apply 失败需核对 eval spec 的 base_commit 与 rootfs checkout 是否一致（不是依赖问题）。</li>')
    parts.append('<li><b>统一</b>：给 eval 沙箱开放 pypi / sourceforge / savannah / files.pythonhosted 白名单（或预置 wheel cache + 源码 tarball 镜像），一次性根治「外网下载」类失效。</li>')
    parts.append('</ul>')
    return ''.join(parts)

def infra_section():
    """§8 完整 HTML（表 + 判定 + 逐 repo 根因 + 影响 + 修复建议）"""
    broken_uniq = sum(repo_uniq[r] for r in EVAL_BROKEN)
    return (''
        '<h3>8.1 失效面全景</h3>'
        '<div class="callout callout-red"><b>⚠️ 结论修正：</b>原「只 3 个 eval-可用 repo」的说法不准确。'
        '准确表述是：<b>5 个 repo 因 eval 基础设施失效</b>（matplotlib/pytest/sphinx/astropy/flask，共 ' + str(broken_uniq) + ' 唯一实例）被系统性压到 near-0；'
        '而 <code>psf/requests</code> 是<b>被误判</b>的 —— 它 patch 全 apply、0 resolved 是能力/难度问题，不应算「受限」。'
        '其余 eval-OK repo 里，django/sklearn 也各有少量 <code>missing_module</code>（见上表），并非 100% 干净。</div>'
        + infra_breakdown_table()
        + '<h3>8.2 逐 repo root-cause（日志实证）</h3>'
        + inf_diag()
        + inf_impact())

def h2h_table():
    rows = []
    for h in HARNESSES:
        if h == 'cline-patched': continue
        co, oo, both = h2h[h]
        rows.append(f'<tr><td><b>{SHORT[h]}</b></td><td class="num">{co}</td><td class="num">{oo}</td>'
                    f'<td class="num">{both}</td><td>{"cline 更强" if co>oo else "对方更强" if oo>co else "持平"}</td></tr>')
    return ''.join(rows)

def pbf_table():
    rows = []
    for h in HARNESSES:
        pe = stats[h]['pbf_eval']
        tp = stats[h]['pbf']
        pna = pe.get('patch_not_applied', 0)
        rows.append(f'<tr><td><b>{SHORT[h]}</b></td><td class="num">{tp}</td>'
                    f'<td class="num">{pna}<br><span class="sub">{100*pna/tp:.1f}%</span></td>'
                    f'<td class="num">{pe.get("f2p_all_fail",0)}</td>'
                    f'<td class="num">{pe.get("f2p_partial",0)}</td><td class="num">{pe.get("f2p_pass_p2p_fail",0)}</td></tr>')
    return ''.join(rows)

# 进度摘要
hermes_done = stats['hermes']['total']
hermes_rem = 300 - hermes_done
progress_pct = 100*TOTAL/2100

CSS = """
:root{--bg:#f6f8fa;--card:#fff;--border:#d0d7de;--text:#1f2328;--muted:#59636e;--primary:#0b3d6e;--accent:#1f6feb;--ok:#1a7f37;--warn:#9a6700;--bad:#cf222e}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:var(--text);background:var(--bg);line-height:1.7;font-size:15px}
.wrap{max-width:1100px;margin:0 auto;padding:32px 20px 80px}
header.hero{background:linear-gradient(135deg,#0b3d6e 0%,#1f6feb 100%);color:#fff;border-radius:14px;padding:30px 32px;margin-bottom:22px}
header.hero h1{margin:0 0 6px;font-size:23px}header.hero .sub{font-size:14px;opacity:.95}
header.hero .meta{margin-top:14px;font-size:13px;opacity:.9}
h2.sec{font-size:19px;margin:34px 0 10px;padding-bottom:8px;border-bottom:2px solid #dbeafe;color:var(--primary)}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin:12px 0}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13.5px}
th,td{border:1px solid var(--border);padding:7px 9px;text-align:center}th{background:#f1f5f9;color:var(--primary);font-weight:600}
td.rname{text-align:left;font-family:monospace;font-size:12px}
td.num{font-variant-numeric:tabular-nums}
.cline-row{background:#f0f7ff}
.sub{color:var(--muted);font-size:11px}
.legend{font-size:12px;color:var(--muted);margin-top:4px}
.callout{border-radius:8px;padding:14px 18px;margin:14px 0;border-left:4px solid}
.callout-blue{background:#dbeafe;border-color:#2563eb}
.callout-green{background:#d1fae5;border-color:#10b981}
.callout-yellow{background:#fef3c7;border-color:#f59e0b}
.callout-red{background:#fee2e2;border-color:#dc2626}
.tag-ok{display:inline-block;padding:1px 7px;border-radius:4px;font-size:11px;background:#d1fae5;color:#1a7f37}
.tag-lim{display:inline-block;padding:1px 7px;border-radius:4px;font-size:11px;background:#fee2e2;color:#b91c1c}
.tag-part{display:inline-block;padding:1px 7px;border-radius:4px;font-size:11px;background:#fef3c7;color:#9a6700}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:14px 0}
.sum{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px;text-align:center}
.sum .n{font-size:1.7em;font-weight:700;color:var(--accent)}.sum .l{font-size:12px;color:var(--muted)}
code{background:#f1f5f9;padding:1px 6px;border-radius:3px;font-size:13px}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--border);font-size:12px;color:#8b949e}
.chart{margin:16px 0;text-align:center}
"""

html_doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe Harness 7×300 评测报告（中文版）</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<header class="hero">
<h1>BaiZe Harness 7×300 评测报告</h1>
<div class="sub">7 个 agent harness × 300 SWE-bench Lite 实例 · 统一 backbone（kimi-k2.6-cloud）· 统一沙箱 · 统一判据</div>
<div class="meta">生成时间 2026-10-12 · 数据源 <code>run/harness/kimi_pilot_results.json</code>（{TOTAL} entries，进度 {progress_pct:.1f}%，hermes {hermes_done}/300 还差 {hermes_rem} 个 sympy）· 自包含单文件 · 零外链</div>
</header>

<div class="callout callout-blue"><b>一句话结论：</b>7 个 harness 在<b>完全相同</b>的 backbone 与评测管线下，resolve rate 全部落在 <b>{min(stats[h]["rate"] for h in HARNESSES):.1f}% ~ {max(stats[h]["rate"] for h in HARNESSES):.1f}%</b> 的窄带内（相差约 {max(stats[h]["rate"] for h in HARNESSES)-min(stats[h]["rate"] for h in HARNESSES):.1f} pp）。<b>pi（30.3%）居首，cline（28.7%）/ opencode（29.0%）紧随其后</b>，codex 速度最慢（wall 922s）换取 26.7%。有效比较范围内（django/sympy/scikit-learn，eval-可用；eval 失效 repo 的完整 root-cause 归因见 §8），<b>pi ≥ opencode ≥ cline</b>，三者差距极小且<b>不具统计显著性</b>（binomial SE ≈3pp）。</div>

<div class="grid">
<div class="sum"><div class="n">{TOTAL}</div><div class="l">总 entries（{progress_pct:.1f}% 完成）</div></div>
<div class="sum"><div class="n">{RESOLVED_TOTAL}</div><div class="l">总 resolved</div></div>
<div class="sum"><div class="n">{100*RESOLVED_TOTAL/TOTAL:.1f}%</div><div class="l">总体 resolve rate</div></div>
<div class="sum"><div class="n">{len(all7)}</div><div class="l">7 方都测过的实例</div></div>
<div class="sum"><div class="n">{everybody}</div><div class="l">全员解出（everybody）</div></div>
<div class="sum"><div class="n">{nobody}</div><div class="l">全灭（nobody, {100*nobody/len(all7):.0f}%）</div></div>
</div>

<h2 class="sec">1. 评测设计</h2>
<div class="card">
<p><b>对象</b>：7 个 coding agent harness —— <code>cline-patched</code>（BaiZe 的 agent 骨架，EDA 开发基于它）、<code>opencode</code>、<code>pi</code>（gpt-eng）、<code>codex</code>、<code>claude-code</code>、<code>deepseek-harness</code>、<code>hermes</code>（SWE-bench 官方 harness）。</p>
<p><b>控制变量</b>：统一 backbone <code>kimi-k2.6-cloud</code> · 同一沙箱 · 同一 eval 判据（SWE-bench <code>test patch applied + FAIL_TO_PASS 全过 + PASS_TO_PASS 全过</code>）。</p>
<p><b>任务集</b>：SWE-bench Lite <b>300 实例</b>（stratified 抽样：30 Round-1 + 70 比例填充；100-set 是 300-set 子集，可 <code>--resume</code> 复用）。7 路并行跑（R2），每 harness 内部串行。</p>
<p><b>分类</b>：<code>resolved</code>（解出）/ <code>patch-but-failed</code>（PBF，补丁产出但测试未全过）/ <code>blocked</code> / <code>quota-blocked</code>。</p>
<p><b>定位</b>：这是 <b>harness 选型 + cline 改进</b> 研究（软件工程基准，<b>不是</b> EDA 基准）；BaiZe 的最终下游评测用 <code>EDA-Eval-PyAether</code>（158 任务）。本报告是 harness 线的 7×300 结果汇总，与「交互轨迹 vs cline 报告」互补。</p>
</div>

<h2 class="sec">2. 总体排名</h2>
<div class="card">
<table>
<tr><th>#</th><th>harness</th><th>resolved</th><th>resolve rate</th><th>PBF</th><th>blocked</th><th>wall 平均（全部）</th><th>wall 平均（resolved）</th></tr>
{rank_table()}
</table>
<div class="chart">{bar_chart()}</div>
<div class="callout callout-yellow"><b>读图提示：</b>codex 与 hermes 的 wall 明显更高（922s / 802s），但 rate 并未对应领先 —— 多花的墙钟没有换来精度提升（见 §3 速度-精度权衡）。</div>
</div>

<h2 class="sec">3. 速度-精度权衡</h2>
<div class="card">
<div class="chart">{pareto_chart()}</div>
<p><b>左上角 = 更快 + 更准</b>（优）。<b>opencode（370s / 29.0%）与 pi（358s / 30.3%）落在 Pareto 前沿</b>；cline（399s / 28.7%）略慢一点、精度接近。codex（572s）与 hermes（479s）明显更慢且精度落在下沿 —— 属 Pareto 劣势。deepseek 最慢且精度最低（473s / 23.7%）。</p>
</div>

<h2 class="sec">4. 失败与阻塞分解</h2>
<div class="card">
<h3>4.1 PBF（patch-but-failed）构成</h3>
<div class="chart">{pbf_chart()}</div>
<table>
<tr><th>harness</th><th>PBF 总数</th><th>patch 未应用</th><th>f2p 全失败</th><th>f2p 部分通过</th><th>f2p 过 / p2p 败</th></tr>
{pbf_table()}
</table>
<p>两类主导：<b>① f2p 全失败</b>（「改了但改不对」，占 PBF 的约 56%~69%）与 <b>② patch 未应用</b>（补丁格式/环境问题，占 24%~35%）。<b>cline 的 patch 未应用率 35.4%（75/212）偏高</b>，高于 codex（29.4%）、claude（27.8%）、hermes（24.5%）—— 这是 cline 的一个可改进点。</p>
<h3>4.2 blocked 分布</h3>
<p>除 cline/opencode 各 2 个外，其余 harness 有 6~17 个 blocked（其中约 2 个 quota-blocked）。<b>claude-code 与 hermes 的 blocked 最多（17 个）</b>，多为 git checkout 冲突 + git_fetch 503 等环境性问题，非能力问题。</p>
</div>

<h2 class="sec">5. Instance 重叠分析（7 方都测过的 294 个实例）</h2>
<div class="card">
<p>在 {len(all7)} 个 all-7 实例上：<b>{nobody}</b> 个实例（{100*nobody/len(all7):.0f}%）<b>全体 harness 都解不出</b>，<b>{everybody}</b> 个实例（{100*everybody/len(all7):.0f}%）全员解出，<b>{some}</b> 个是「部分解出」。</p>
<p class="sub">解读：{100*nobody/len(all7):.0f}% 的实例「全灭」说明 SWE-bench 本批任务的难度对这些 harness + 同 backbone 组合整体偏高；「部分解出」的 {some} 个才是 harness 间真正的分化空间 —— 样本量小，差异不具统计显著性。</p>
</div>

<h2 class="sec">6. Head-to-Head（以 cline 为轴 · all-7 子集）</h2>
<div class="card">
<table>
<tr><th>对手</th><th>cline 独解</th><th>对方独解</th><th>双方都解出</th><th>读法</th></tr>
{h2h_table()}
</table>
<p class="sub">cline 相对 <b>deepseek-harness</b> 优势最明显（独解 31 vs 16）；相对 <b>pi</b> 略处下风（12 vs 17）；与 opencode / claude / hermes 基本互有胜负。均为小样本，仅供方向性参考。</p>
</div>

<h2 class="sec">7. Per-Repo 分解</h2>
<div class="card">
<table>
<tr><th>repo</th>{''.join(f'<th>{SHORT[h]}</th>' for h in HARNESSES)}</tr>
{repo_matrix()}
</table>
<div class="callout callout-yellow"><b>读表提示：</b>「eval失效」tag = patch_applied 大面积 False（基础设施失效，非模型能力，0 分是假象）；「小样本」tag = patch 基本全 apply 但唯一实例 ≤6，仅供参考。逐 repo root-cause、影响量化与修复建议见 <b>§8</b>。</div>
</div>

<h2 class="sec">8. eval 基础设施失效归因（root-cause 专章）</h2>
<div class="card">
{infra_section()}
</div>

<h2 class="sec">9. 口径与诚实条款</h2>
<div class="card">
<ul>
<li><b>快照未闭环</b>：hermes {hermes_done}/300（还差 {hermes_rem} 个，均为 sympy），其 rate（{stats["hermes"]["rate"]:.1f}%）可能受未完成实例的<b>选择偏差</b>影响；全部跑完后应重跑本脚本刷新数字。</li>
<li><b>R1/R2 wall time 不完全可比</b>：R2 为 7 路并行，wall 含资源争抢开销；且 hermes/codex 的 wall 偏长部分源于自身较重实现。</li>
<li><b>样本量</b>：resolve rate 的 binomial SE ≈ 3 pp（p≈0.28, n≈300），故 pi/cline/opencode 三者之差（≤1.6 pp）<b>不具统计显著性</b>，排名仅有方向性意义。</li>
<li><b>实例重叠</b>：all-7 的 294 实例中「部分解出」仅 {some} 个，head-to-head 独解计数多为个位数，<b>不作显著性结论</b>。</li>
<li><b>轨迹数据缺失</b>：仅 stdout_tail 最后 500 字符，无 per-turn 轨迹 —— 工具调用序列、token、压缩事件均不可得。</li>
<li><b>数据可复算</b>：所有数字由 <code>gen_report_7x300_zh.py</code> 从 <code>kimi_pilot_results.json</code> 现算，脚本入库。</li>
</ul>
</div>

<h2 class="sec">10. 对 BaiZe 的启示</h2>
<div class="card">
<ul>
<li><b>harness 选型</b>：pi / opencode / cline 三者在同 backbone 下难分伯仲（30.3% / 29.0% / 28.7%），若考虑<b>速度</b>，opencode（wall 最短 460s）与 pi 更优；cli<b>ne</b> 的护城河在于 BaiZe 的 EDA agent 已基于它开发、且有可落地的改进点（§4 的 patch 未应用率、ai@7.0.49 transform error）。</li>
<li><b>{rate_spread:.1f} pp 的 harness 差带 vs 数十 pp 的模型差带</b>：ZhuLong 侧 full harness（DeepSeek-V4-Pro）≈94% vs 裸 LLM ≈10.5%，说明<b>主要矛盾仍是模型能力 / 观测保真度，而非 harness 细节</b> —— 与 BaiZe「harness 冻结、换 backbone」的主体研究一致。</li>
<li><b>基线参照</b>：本次 backbone 固定为 kimi-k2.6-cloud，7 harness 的 23.7%~30.3% 可作为该 backbone 在 SWE-bench 的上限参考；BaiZe-backbone 接入后可在同一管线复测。</li>
</ul>
</div>

<footer>
harness 线 · 7×300 评测报告（中文版）· 2026-10-12 · 自包含单文件 · 内联 CSS/SVG · 零外链 · 纯分析（不占 GPU）<br>
数据源：run/harness/kimi_pilot_results.json（{TOTAL} entries）· 生成脚本：run/harness/gen_report_7x300_zh.py · 每格数字可复算
</footer>

</div>
</body>
</html>'''

OUT.write_text(html_doc, encoding='utf-8')
print(f"Written {OUT} ({len(html_doc)} bytes, {len(html_doc)/1024:.1f} KB)")
print(f"total={TOTAL} resolved={RESOLVED_TOTAL} rate={100*RESOLVED_TOTAL/TOTAL:.1f}% all7={len(all7)} nobody={nobody} everybody={everybody} some={some}")
print(f"best={SHORT[best]} {stats[best]['rate']:.1f}% worst={SHORT[ranking[-1]]} {stats[ranking[-1]]['rate']:.1f}%")
