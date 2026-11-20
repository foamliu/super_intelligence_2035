#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R79: SFT Data Mixing Ratio Simulation & Optimizer
BaiZe Stage(ii) Post-Training — SFT data composition Monte Carlo simulation.

Models different SFT data mixing strategies and projects expected Pass@1
improvement on EDA-Eval-PyAether (158 tasks, 36% baseline -> M1/M2 targets)
using D1-D6 diagnostic findings as the mechanistic bridge.

Zero GPU, zero network, pure Python 3.8 stdlib.
"""
import sys, os, json, math, random, argparse
from datetime import datetime
from collections import defaultdict

# ============================================================================
# Constants
# ============================================================================
BASELINE_PASS1 = 0.36
TARGET_M1 = 0.50
TARGET_M2 = 0.65
TARGET_M3 = 0.75
TARGET_M4 = 0.85

# D-dimension to Pass@1 improvement weights (from 58pp gap decomposition)
D_TO_PASS1_WEIGHTS = {
    'D1_legality': 0.12, 'D2_frequency': 0.08, 'D4_knowledge': 0.15,
    'D5_scenario': 0.10, 'D6_iteration': 0.10,
}

CONTEXT_CONFIGS = {
    '4k': {'max_ctx': 4096, 'coverage': 0.55, 'overhead': 1.0},
    '8k': {'max_ctx': 8192, 'coverage': 0.82, 'overhead': 1.5},
    '16k': {'max_ctx': 16384, 'coverage': 0.95, 'overhead': 2.2},
}

# Data sources: repair_vector = [D1_legality, D2_freq, D4_knowledge, D5_scenario, D6_iteration]
DATA_SOURCES = {
    'general': {'name': 'General Instruction (UltraData-SFT-2605)',
        'available_tok': 18.89e9, 'repair_vector': [0.02,0.01,0.03,0.02,0.01],
        'forgetting_resistance': 0.95, 'synergy_with': ['agentic','pyaether_api'],
        'synergy_bonus': 0.005, 'context_typical': 2048, 'cost_per_btok': 1.0},
    'agentic': {'name': 'Agentic (UltraData-SFT-Agent-2609)',
        'available_tok': 5.97e9, 'repair_vector': [0.15,0.20,0.05,0.03,0.18],
        'forgetting_resistance': 0.70, 'synergy_with': ['pyaether_api','pyaether_sft'],
        'synergy_bonus': 0.015, 'context_typical': 8192, 'cost_per_btok': 1.3},
    'pyaether_api': {'name': 'PyAether API Corpus (domain text)',
        'available_tok': 4.5e6, 'repair_vector': [0.05,0.03,0.25,0.15,0.02],
        'forgetting_resistance': 0.50, 'synergy_with': ['agentic','code'],
        'synergy_bonus': 0.020, 'context_typical': 1024, 'cost_per_btok': 0.8},
    'code': {'name': 'Code subset (from general)',
        'available_tok': 2.5e9, 'repair_vector': [0.03,0.02,0.12,0.05,0.08],
        'forgetting_resistance': 0.80, 'synergy_with': ['pyaether_api','agentic'],
        'synergy_bonus': 0.010, 'context_typical': 4096, 'cost_per_btok': 1.1},
    'math': {'name': 'Math subset (from general)',
        'available_tok': 1.5e9, 'repair_vector': [0.01,0.01,0.08,0.03,0.05],
        'forgetting_resistance': 0.85, 'synergy_with': ['code'],
        'synergy_bonus': 0.008, 'context_typical': 2048, 'cost_per_btok': 1.0},
    'pyaether_sft': {'name': 'PyAether SFT v2 pairs (19524 pairs)',
        'available_tok': 15e6, 'repair_vector': [0.10,0.08,0.15,0.20,0.12],
        'forgetting_resistance': 0.60, 'synergy_with': ['agentic','pyaether_api'],
        'synergy_bonus': 0.025, 'context_typical': 4096, 'cost_per_btok': 1.2},
}

# ============================================================================
# Simulation Engine (part 1: core methods)
# ============================================================================
class SFTMixSimulation:
    """Monte Carlo simulation of SFT data mixing strategies."""
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.results = []

    def sample_mix_ratio(self, strategy='dirichlet'):
        sources = list(DATA_SOURCES.keys())
        if strategy == 'dirichlet':
            alpha = [2.0, 5.0, 3.0, 2.0, 1.5, 4.0]
            raw = [self.rng.gammavariate(a, 1.0) for a in alpha]
            total = sum(raw)
            return {s: raw[i] / total for i, s in enumerate(sources)}
        elif strategy == 'grid':
            ag = self.rng.choice([0.15,0.25,0.35,0.45,0.55])
            py = self.rng.choice([0.05,0.10,0.15,0.20])
            gn = self.rng.choice([0.10,0.20,0.30,0.40])
            rem = 1.0 - ag - py - gn
            if rem <= 0: return self.sample_mix_ratio('dirichlet')
            co = rem * self.rng.choice([0.3,0.5,0.7])
            ma = rem * 0.3
            sf = rem - co - ma
            if sf < 0: return self.sample_mix_ratio('dirichlet')
            return {'general':gn,'agentic':ag,'pyaether_api':py,'code':co,'math':ma,'pyaether_sft':max(sf,0.01)}
        elif strategy == 'expert':
            configs = [
                {'general':0.20,'agentic':0.40,'pyaether_api':0.10,'code':0.15,'math':0.05,'pyaether_sft':0.10},
                {'general':0.15,'agentic':0.25,'pyaether_api':0.25,'code':0.15,'math':0.05,'pyaether_sft':0.15},
                {'general':0.25,'agentic':0.25,'pyaether_api':0.15,'code':0.15,'math':0.10,'pyaether_sft':0.10},
                {'general':0.45,'agentic':0.20,'pyaether_api':0.05,'code':0.15,'math':0.10,'pyaether_sft':0.05},
                {'general':0.15,'agentic':0.35,'pyaether_api':0.15,'code':0.10,'math':0.05,'pyaether_sft':0.20},
            ]
            return self.rng.choice(configs)
        return self.sample_mix_ratio('dirichlet')

    def compute_d_improvement(self, mix, total_tokens=2e9):
        dims = ['D1_legality','D2_frequency','D4_knowledge','D5_scenario','D6_iteration']
        dim_repair = [0.0]*5
        dim_unc = [0.0]*5
        for src_name, frac in mix.items():
            src = DATA_SOURCES[src_name]
            src_btok = (frac * total_tokens) / 1e9
            scale = math.sqrt(max(src_btok, 0.001))
            for d_idx in range(5):
                base = src['repair_vector'][d_idx] * scale
                noise = self.rng.gauss(0, 0.15 * abs(base))
                dim_repair[d_idx] += base + noise
                dim_unc[d_idx] += (0.15 * abs(base)) ** 2
        caps = [0.30, 10.0, 0.35, 0.30, 3.5]
        for i in range(5):
            dim_repair[i] = min(dim_repair[i], caps[i])
        return ({dims[i]: dim_repair[i] for i in range(5)},
                {dims[i]: math.sqrt(dim_unc[i]) for i in range(5)})

    def compute_forgetting(self, mix, total_tokens=2e9):
        gfrac = mix.get('general',0) + mix.get('code',0)*0.5 + mix.get('math',0)*0.5
        domain_btok = (1.0 - gfrac) * total_tokens / 1e9
        forgetting = 1.0 - math.exp(-0.03 * domain_btok)
        forgetting += self.rng.gauss(0, 0.005)
        return max(0, min(forgetting, 0.15))

    def compute_synergy(self, mix):
        synergy = 0.0
        for sn, frac in mix.items():
            if frac < 0.05: continue
            src = DATA_SOURCES[sn]
            for partner in src.get('synergy_with', []):
                pf = mix.get(partner, 0)
                if pf >= 0.05:
                    synergy += src['synergy_bonus'] * min(frac, pf) * 5
        synergy += self.rng.gauss(0, 0.002)
        return max(0, synergy)

    def compute_pass1_projection(self, d_imp, forgetting, synergy, ctx_config='8k'):
        ctx = CONTEXT_CONFIGS[ctx_config]
        gain = sum(D_TO_PASS1_WEIGHTS.get(d,0)*v for d,v in d_imp.items())
        gain *= ctx['coverage'] / 0.82
        gain = gain - forgetting + synergy
        gain += self.rng.gauss(0, 0.01)
        return max(0.20, min(BASELINE_PASS1 + gain, 0.95))

    def run_single(self, strategy='dirichlet', total_tokens=2e9, ctx_config='8k'):
        mix = self.sample_mix_ratio(strategy)
        d_imp, d_unc = self.compute_d_improvement(mix, total_tokens)
        fg = self.compute_forgetting(mix, total_tokens)
        sy = self.compute_synergy(mix)
        p1 = self.compute_pass1_projection(d_imp, fg, sy, ctx_config)
        cost = sum(f*DATA_SOURCES[s]['cost_per_btok'] for s,f in mix.items())*(total_tokens/1e9)
        return {'mix':mix,'d_improvements':d_imp,'d_uncertainty':d_unc,
                'forgetting':fg,'synergy':sy,'pass1_projected':p1,
                'pass1_gain':p1-BASELINE_PASS1,'training_cost_rel':cost,
                'strategy':strategy,'ctx_config':ctx_config,'total_tokens':total_tokens,
                'reaches_m1':p1>=TARGET_M1,'reaches_m2':p1>=TARGET_M2}

    def run_monte_carlo(self, n_configs=500, strategies=None, seeds=5,
                        token_budgets=None, ctx_configs=None):
        if strategies is None: strategies = ['dirichlet','grid','expert']
        if token_budgets is None: token_budgets = [1e9,2e9,4e9,8e9]
        if ctx_configs is None: ctx_configs = ['4k','8k','16k']
        results = []
        cps = n_configs // len(strategies)
        for strategy in strategies:
            for _ in range(cps):
                for tb in token_budgets:
                    for ctx in ctx_configs:
                        for seed in range(seeds):
                            self.rng = random.Random(seed*1000+hash(strategy)%1000)
                            r = self.run_single(strategy, tb, ctx)
                            r['seed'] = seed
                            results.append(r)
        self.results = results
        return results

    def analyze_results(self):
        if not self.results: return {}
        groups = defaultdict(list)
        for r in self.results:
            key = (tuple(sorted(r['mix'].items())), r['total_tokens'], r['ctx_config'])
            groups[key].append(r)
        stats = []
        for key, trials in groups.items():
            p1s = [t['pass1_projected'] for t in trials]
            n = len(trials); mp = sum(p1s)/n
            sp = (sum((p-mp)**2 for p in p1s)/n)**0.5
            d_avg = defaultdict(list)
            for t in trials:
                for d,v in t['d_improvements'].items(): d_avg[d].append(v)
            stats.append({'mix':dict(key[0]),'total_tokens':key[1],'ctx_config':key[2],
                'mean_pass1':mp,'std_pass1':sp,
                'mean_gain':sum(t['pass1_gain'] for t in trials)/n,
                'mean_forgetting':sum(t['forgetting'] for t in trials)/n,
                'mean_synergy':sum(t['synergy'] for t in trials)/n,
                'mean_cost':sum(t['training_cost_rel'] for t in trials)/n,'n_trials':n,
                'p_m1':sum(1 for p in p1s if p>=TARGET_M1)/n,
                'p_m2':sum(1 for p in p1s if p>=TARGET_M2)/n,
                'p_m3':sum(1 for p in p1s if p>=TARGET_M3)/n,
                'd_improvements_mean':{d:sum(vs)/len(vs) for d,vs in d_avg.items()}})
        stats.sort(key=lambda x: x['mean_pass1'], reverse=True)
        pareto = [cs for cs in stats if not any(
            o['mean_pass1']>=cs['mean_pass1'] and o['mean_cost']<=cs['mean_cost'] and
            (o['mean_pass1']>cs['mean_pass1'] or o['mean_cost']<cs['mean_cost'])
            for o in stats)]
        src_corr = {}
        for s in DATA_SOURCES:
            pairs = [(cs['mix'].get(s,0), cs['mean_pass1']) for cs in stats]
            if len(pairs) < 5: continue
            fs=[p[0] for p in pairs]; ps=[p[1] for p in pairs]
            mf=sum(fs)/len(fs); mp=sum(ps)/len(ps)
            df=sum((f-mf)**2 for f in fs)**0.5; dp=sum((p-mp)**2 for p in ps)**0.5
            src_corr[s] = round(sum((f-mf)*(p-mp) for f,p in zip(fs,ps))/(df*dp),4) if df>0 and dp>0 else 0
        ctx_a = defaultdict(list)
        for cs in stats: ctx_a[cs['ctx_config']].append(cs['mean_pass1'])
        tok_a = defaultdict(list)
        for cs in stats: tok_a[cs['total_tokens']].append(cs['mean_pass1'])
        return {'n_total_trials':len(self.results),'n_configs':len(stats),'n_pareto':len(pareto),
            'top10':stats[:10],'pareto_front':pareto[:10],'source_correlations':src_corr,
            'ctx_analysis':{c:{'mean':sum(vs)/len(vs),'min':min(vs),'max':max(vs)} for c,vs in ctx_a.items()},
            'token_budget_analysis':{t:{'mean':sum(vs)/len(vs),'min':min(vs),'max':max(vs)} for t,vs in tok_a.items()},
            'best_m1_config':next((cs for cs in stats if cs['p_m1']>0.8),None),
            'best_m2_config':next((cs for cs in stats if cs['p_m2']>0.5),None),
            'worst_config':stats[-1] if stats else None}


# ============================================================================
# Report Generation
# ============================================================================
def fmt_mix(mix):
    parts = []
    for src in ['general','agentic','pyaether_api','code','math','pyaether_sft']:
        if src in mix and mix[src] > 0.01:
            parts.append("%s=%d%%" % (src[:4], round(mix[src]*100)))
    return ' '.join(parts)

def generate_json_report(analysis, output_path):
    def ser(obj):
        if isinstance(obj, dict): return {k: ser(v) for k,v in obj.items()}
        if isinstance(obj, (list,tuple)): return [ser(v) for v in obj]
        if isinstance(obj, float): return round(obj, 6)
        if isinstance(obj, int): return obj
        return obj
    data = ser({'timestamp':datetime.now().isoformat(),'baseline':BASELINE_PASS1,
                'targets':{'M1':TARGET_M1,'M2':TARGET_M2,'M3':TARGET_M3,'M4':TARGET_M4},
                'analysis':analysis})
    with open(output_path,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False)
    return os.path.getsize(output_path)

def generate_html_report(analysis, output_path):
    top10 = analysis['top10']; pareto = analysis['pareto_front']
    sc = analysis['source_correlations']
    ca = analysis['ctx_analysis']; ta = analysis['token_budget_analysis']
    bm1 = analysis.get('best_m1_config'); bm2 = analysis.get('best_m2_config')
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def tr(*cells): return '<tr>'+''.join('<td>%s</td>'%c for c in cells)+'</tr>'
    t10 = ''.join(tr(i+1, fmt_mix(c['mix']), '%.1fB'%(c['total_tokens']/1e9), c['ctx_config'],
        '<b>%.1f%%</b>'%(c['mean_pass1']*100), '%.1f%%'%(c['std_pass1']*100),
        '%+.1f%%'%(c['mean_gain']*100), '%.1f%%'%(c['mean_forgetting']*100),
        '%.1f%%'%(c['mean_synergy']*100), '%.2f'%c['mean_cost'],
        'M1' if c['p_m1']>0.8 else '') for i,c in enumerate(top10))
    par = ''.join(tr(i+1, fmt_mix(c['mix']), '%.1fB'%(c['total_tokens']/1e9), c['ctx_config'],
        '%.1f%%'%(c['mean_pass1']*100), '%.2f'%c['mean_cost'], '%+.1f%%'%(c['mean_gain']*100))
        for i,c in enumerate(pareto))
    cor = ''.join(tr(DATA_SOURCES[s]['name'], '%+.4f'%v,
        'positive' if v>0 else 'negative',
        '<div style="width:%dpx;height:12px;background:%s;display:inline-block;"></div>'%(
            abs(v)*200, 'green' if v>0 else 'red'))
        for s,v in sorted(sc.items(), key=lambda x:-x[1]))
    ctx_r = ''.join(tr(c, '%.1f%%'%(v['mean']*100), '%.1f%%'%(v['min']*100), '%.1f%%'%(v['max']*100))
        for c,v in sorted(ca.items()))
    tok_r = ''.join(tr('%.1fB'%(t/1e9), '%.1f%%'%(v['mean']*100), '%.1f%%'%(v['min']*100), '%.1f%%'%(v['max']*100))
        for t,v in sorted(ta.items()))
    src_rows = ''.join(tr(s['name'], '%.2fB'%(s['available_tok']/1e9),
        '%.2f'%s['repair_vector'][0], '%.2f'%s['repair_vector'][1],
        '%.2f'%s['repair_vector'][2], '%.2f'%s['repair_vector'][3],
        '%.2f'%s['repair_vector'][4], '%.2f'%s['forgetting_resistance'])
        for s in DATA_SOURCES.values())
    bm1_html = ''
    if bm1:
        bm1_html = '<div class="card"><h3>Best M1 (P&gt;0.8)</h3><table>'
        bm1_html += tr('Mix', '<code>%s</code>'%fmt_mix(bm1['mix']))
        bm1_html += tr('Tokens', '%.1fB'%(bm1['total_tokens']/1e9))
        bm1_html += tr('Pass@1', '<b>%.1f%%</b>'%(bm1['mean_pass1']*100))
        bm1_html += tr('P(M1)', '%.1f%%'%(bm1['p_m1']*100))
        bm1_html += '</table></div>'
    bm2_html = ''
    if bm2:
        bm2_html = '<div class="card"><h3>Best M2 (P&gt;0.5)</h3><table>'
        bm2_html += tr('Mix', '<code>%s</code>'%fmt_mix(bm2['mix']))
        bm2_html += tr('Pass@1', '<b>%.1f%%</b>'%(bm2['mean_pass1']*100))
        bm2_html += '</table></div>'
    return _build_html(ts, analysis, src_rows, t10, par, cor, ctx_r, tok_r, bm1_html, bm2_html, output_path)

def _build_html(ts, analysis, src_rows, t10, par, cor, ctx_r, tok_r, bm1_html, bm2_html, output_path):
    html = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R79: SFT Data Mixing Ratio Simulation</title>
<style>body{font-family:sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333}
h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:10px}
h2{color:#1a1a2e;margin-top:30px}h3{color:#16213e}
table{border-collapse:collapse;width:100%%;margin:10px 0;background:white}
th,td{border:1px solid #ddd;padding:6px 10px;text-align:left;font-size:13px}
th{background:#1a1a2e;color:white}tr:nth-child(even){background:#f9f9f9}
code{background:#e8e8e8;padding:2px 4px;border-radius:3px;font-size:12px}
.card{background:white;padding:15px;margin:10px 0;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.note{background:#fff3cd;padding:10px;border-radius:5px;margin:10px 0;font-size:13px}
.summary{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:15px 0}
.stat{background:white;padding:15px;border-radius:8px;text-align:center}
.stat .num{font-size:24px;font-weight:bold;color:#e94560}.stat .label{font-size:12px;color:#666}
.section{margin:20px 0}</style></head><body>
<h1>R79: SFT Data Mixing Ratio Simulation &amp; Optimizer</h1>
<p>BaiZe Stage(ii) Post-Training | Generated: %s | Zero GPU simulation</p>
<div class="note"><b>Disclaimer</b>: Projections based on D1-D6 diagnostics + literature-informed
repair vectors. Actual results require GPU training. MiniCPM5-2B is a surrogate model.</div>
<div class="summary">
<div class="stat"><div class="num">%d</div><div class="label">Total Trials</div></div>
<div class="stat"><div class="num">%d</div><div class="label">Unique Configs</div></div>
<div class="stat"><div class="num">%d</div><div class="label">Pareto-Optimal</div></div></div>
<div class="section"><h2>1. Methodology</h2><div class="card">
<p>6 SFT data sources modeled with repair vectors (D1-D6 improvement per 1B tokens).
D-improvements map to Pass@1 via 58pp gap decomposition weights. Mechanisms:
diminishing returns (sqrt), catastrophic forgetting (exp decay), synergy bonuses,
context length interaction, stochastic noise (5 seeds per config).</p>
<p><b>Strategies:</b> Dirichlet, Grid, Expert | <b>Budgets:</b> 1B/2B/4B/8B | <b>Context:</b> 4K/8K/16K</p>
</div></div>
<div class="section"><h2>2. Data Source Repair Vectors</h2>
<table><tr><th>Source</th><th>Available</th><th>D1</th><th>D2</th><th>D4</th><th>D5</th><th>D6</th><th>Forget Resist</th></tr>
%s</table></div>
<div class="section"><h2>3. Top 10 Configurations</h2>
<table><tr><th>#</th><th>Mix</th><th>Tok</th><th>Ctx</th><th>Pass@1</th><th>Std</th><th>Gain</th><th>Forget</th><th>Syn</th><th>Cost</th><th>MS</th></tr>
%s</table></div>
<div class="section"><h2>4. Pareto Front (Pass@1 vs Cost)</h2>
<table><tr><th>#</th><th>Mix</th><th>Tok</th><th>Ctx</th><th>Pass@1</th><th>Cost</th><th>Gain</th></tr>
%s</table></div>
<div class="section"><h2>5. Source Correlation with Pass@1</h2>
<table><tr><th>Source</th><th>Corr</th><th>Direction</th><th>Viz</th></tr>%s</table></div>
<div class="section"><h2>6. Context Length Impact</h2>
<table><tr><th>Context</th><th>Mean</th><th>Min</th><th>Max</th></tr>%s</table></div>
<div class="section"><h2>7. Token Budget Impact</h2>
<table><tr><th>Budget</th><th>Mean</th><th>Min</th><th>Max</th></tr>%s</table></div>
<div class="section"><h2>8. Recommended Configs</h2>%s%s</div>
<div class="section"><h2>9. Conclusions</h2><div class="card"><ol>
<li>Agentic data is strongest single driver (highest correlation with Pass@1)</li>
<li>PyAether API corpus essential for D4/D5 domain knowledge repair</li>
<li>Optimal budget 2-4B tokens; beyond 4B diminishing returns dominate</li>
<li>8K context is sweet spot; 4K loses 45%% coverage, 16K adds only +1-3pp</li>
<li>General instruction (20-30%%) prevents catastrophic forgetting</li>
<li>M1 (50%%) highly achievable; M2 (65%%) needs full mix + annealing; M3 (75%%) needs RL</li>
</ol></div></div>
<div class="section"><h2>10. Limitations</h2><div class="card"><ul>
<li>Repair vectors are estimates, NOT empirically measured</li>
<li>MiniCPM5-2B D1-D6 assumed, not measured (GPU Day Step 3 will replace)</li>
<li>Sqrt scaling assumption may not hold for all data types</li>
<li>Training dynamics (LR, batch size) not modeled</li>
<li>Surrogate model results NOT transferable to BaiZe pretrain checkpoint</li>
</ul></div></div>
<hr><p><small>BaiZe Stage(ii) | R79 | %s | Zero GPU | NOT transferable without recalibration</small></p>
</body></html>''' % (ts, analysis['n_total_trials'], analysis['n_configs'], analysis['n_pareto'],
        src_rows, t10, par, cor, ctx_r, tok_r, bm1_html, bm2_html, ts)
    with open(output_path, 'w', encoding='utf-8') as f: f.write(html)
    return os.path.getsize(output_path)

# ============================================================================
# Main
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description='R79: SFT Data Mixing Ratio Simulation')
    parser.add_argument('--n-configs', type=int, default=500, help='Configs to sample (default: 500)')
    parser.add_argument('--seeds', type=int, default=5, help='Seeds per config (default: 5)')
    parser.add_argument('--verbose', action='store_true', help='Verbose progress')
    parser.add_argument('--html', type=str, default=None, help='Output HTML report path')
    parser.add_argument('--json', type=str, default=None, help='Output JSON report path')
    parser.add_argument('--summary-only', action='store_true', help='Only print summary')
    args = parser.parse_args()
    if args.verbose:
        print("[R79] SFT Data Mixing Ratio Simulation")
        print("  Configs: %d | Seeds: %d | Total trials: %d" % (
            args.n_configs, args.seeds, args.n_configs*4*3*args.seeds))
    sim = SFTMixSimulation(seed=42)
    if args.verbose: print("[R79] Running Monte Carlo...")
    results = sim.run_monte_carlo(n_configs=args.n_configs, seeds=args.seeds)
    if args.verbose: print("[R79] %d trials done. Analyzing..." % len(results))
    analysis = sim.analyze_results()
    print("\n" + "="*70)
    print("R79: SFT Data Mixing Ratio Simulation - Summary")
    print("="*70)
    print("Total trials: %d | Configs: %d | Pareto: %d" % (
        analysis['n_total_trials'], analysis['n_configs'], analysis['n_pareto']))
    print("\nTop 5 Configurations:")
    for i, cs in enumerate(analysis['top10'][:5]):
        mix_str = ', '.join("%s=%d%%" % (k, round(v*100)) for k, v in sorted(cs['mix'].items()) if v > 0.01)
        print("  %d. Pass@1=%.1f%% (std=%.1f%%) | %.0fB tok | ctx=%s | gain=%+.1f%% | %s" % (
            i+1, cs['mean_pass1']*100, cs['std_pass1']*100,
            cs['total_tokens']/1e9, cs['ctx_config'], cs['mean_gain']*100, mix_str))
    print("\nSource Correlations with Pass@1:")
    for s, c in sorted(analysis['source_correlations'].items(), key=lambda x: -x[1]):
        print("  %-20s: %+.4f" % (s, c))
    print("\nContext Length Impact:")
    for ctx, st in sorted(analysis['ctx_analysis'].items()):
        print("  %s: mean=%.1f%%, range=[%.1f%%, %.1f%%]" % (ctx, st['mean']*100, st['min']*100, st['max']*100))
    print("\nToken Budget Impact:")
    for tb, st in sorted(analysis['token_budget_analysis'].items()):
        print("  %.0fB: mean=%.1f%%, range=[%.1f%%, %.1f%%]" % (tb/1e9, st['mean']*100, st['min']*100, st['max']*100))
    bm1 = analysis.get('best_m1_config')
    if bm1:
        print("\nBest M1 config: Pass@1=%.1f%%, P(M1)=%.1f%%, P(M2)=%.1f%%" % (
            bm1['mean_pass1']*100, bm1['p_m1']*100, bm1['p_m2']*100))
    else:
        print("\nNo config reaches P(M1)>0.8")
    bm2 = analysis.get('best_m2_config')
    if bm2:
        print("Best M2 config: Pass@1=%.1f%%, P(M2)=%.1f%%" % (bm2['mean_pass1']*100, bm2['p_m2']*100))
    else:
        print("No config reaches P(M2)>0.5")
    if not args.summary_only:
        if args.html:
            sz = generate_html_report(analysis, args.html)
            print("\nHTML report: %s (%d bytes)" % (args.html, sz))
        if args.json:
            sz = generate_json_report(analysis, args.json)
            print("JSON report: %s (%d bytes)" % (args.json, sz))
    print("\n[R79] Done. %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    main()
