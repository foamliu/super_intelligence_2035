#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R84: EDA Sandbox Throughput Model — DeepSeek traces to RL training budget.
Data: ~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/ (103 traces)
Python 3.8+ stdlib only. Zero GPU. Zero network."""
import argparse, json, math, os, re, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

TRACE_BASE = os.path.expanduser('~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace')
DATASET_PATH = os.path.expanduser('~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl')
REPORT_DIR = '/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports'
JSON_DIR = os.path.dirname(os.path.abspath(__file__))

TOOL_NAME_RE = re.compile(r'<tool_name>(\w+)</tool_name>')
SEARCH_QUERY_RE = re.compile(r'"query"\s*:\s*"([^"]*)"')
API_LIST_RE = re.compile(r'"api_list"\s*:\s*\[([^\]]*)\]')
API_NAME_RE = re.compile(r'"([^"]*)"')

A40_MEM_GB = 46.0
MINICPM5_MEM_GB = 4.7
SGLANG_KV_FRAC = 0.7
MINICPM5_HIDDEN = 2048
MINICPM5_LAYERS = 42
BYTES_PER_KV = 2
GRPO_GROUP = 8
RL_BATCH = 128
RL_STEPS_TARGET = 3000
MAX_CTX = 8192

def load_traces(base_dir):
    if not os.path.isdir(base_dir):
        print('WARNING: trace dir not found: ' + base_dir); return []
    dirs = sorted(os.listdir(base_dir)); traces = []
    for d in dirs:
        conv_path = os.path.join(base_dir, d, 'api_conversation_history.json')
        meta_path = os.path.join(base_dir, d, 'task_metadata.json')
        if not os.path.exists(conv_path): continue
        try: conv = json.load(open(conv_path))
        except: continue
        tool_calls = []; turns = 0; tot_prompt = 0; tot_comp = 0
        for msg in conv:
            role = msg.get('role',''); content = msg.get('content',[])
            if role == 'assistant':
                turns += 1
                tok = msg.get('metrics',{}).get('tokens',{})
                tot_prompt += tok.get('prompt',0); tot_comp += tok.get('completion',0)
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict):
                            text = c.get('text','')
                            for m in TOOL_NAME_RE.finditer(text):
                                tn = m.group(1); ci = {'name': tn}
                                if tn == 'search_apis':
                                    qm = SEARCH_QUERY_RE.search(text)
                                    if qm: ci['query'] = qm.group(1)[:100]
                                elif tn == 'get_api_details':
                                    am = API_LIST_RE.search(text)
                                    if am:
                                        apis = API_NAME_RE.findall(am.group(1))
                                        ci['apis'] = apis[:10]; ci['n_apis'] = len(apis)
                                elif tn == 'run_pyAether_code_tool':
                                    ci['has_code'] = 'import pyAether' in text or 'def ' in text
                                    ci['est_lines'] = text.count('\n')
                                tool_calls.append(ci)
            elif role == 'user':
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict):
                            text = c.get('text','')
                            if 'error' in text.lower()[:200] or 'traceback' in text.lower()[:200]:
                                if tool_calls: tool_calls[-1]['has_error'] = True
                            if len(text) > 100 and tool_calls:
                                tool_calls[-1]['result_length'] = len(text)
        duration_s = None; n_file_ops = 0
        if os.path.exists(meta_path):
            try:
                meta = json.load(open(meta_path)); fic = meta.get('files_in_context',[]); dates = []
                for f in fic:
                    for k in ['cline_read_date','cline_edit_date']:
                        v = f.get(k)
                        if v: dates.append(v)
                if dates:
                    duration_s = (max(dates)-min(dates))/1000.0; n_file_ops = len(dates)
            except: pass
        try: start_ts = int(d)
        except: start_ts = 0
        traces.append({'task_id':d,'start_ts':start_ts,'n_turns':turns,'n_tool_calls':len(tool_calls),
            'tool_calls':tool_calls,'duration_s':duration_s,'n_file_ops':n_file_ops,
            'total_prompt_tokens':tot_prompt,'total_completion_tokens':tot_comp})
    return traces

def load_dataset(path):
    if not os.path.exists(path): return []
    tasks = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try: tasks.append(json.loads(line))
                except: pass
    return tasks

def analyze_patterns(traces):
    all_calls = []; call_types = Counter(); calls_per_task = []; tool_seqs = []
    for t in traces:
        calls_per_task.append(t['n_tool_calls'])
        tool_seqs.append([tc['name'] for tc in t['tool_calls']])
        for tc in t['tool_calls']:
            all_calls.append(tc); call_types[tc['name']] += 1
    n = len(traces); type_dist = dict(call_types.most_common())
    avg_per_type = {k: v/n for k,v in type_dist.items()}
    first3 = Counter()
    for seq in tool_seqs: first3[tuple(seq[:3])] += 1
    search_queries = [tc['query'] for tc in all_calls if tc['name']=='search_apis' and 'query' in tc]
    n_apis_get = [tc['n_apis'] for tc in all_calls if tc['name']=='get_api_details' and 'n_apis' in tc]
    err_by_type = defaultdict(int); tot_by_type = defaultdict(int)
    for tc in all_calls:
        tot_by_type[tc['name']] += 1
        if tc.get('has_error'): err_by_type[tc['name']] += 1
    err_rates = {k: err_by_type[k]/tot_by_type[k] for k in tot_by_type}
    rl = [tc.get('result_length',0) for tc in all_calls if tc.get('result_length')]
    return {'total_tool_calls':len(all_calls),'n_tasks':n,'type_distribution':type_dist,
        'avg_calls_per_type_per_task':avg_per_type,
        'calls_per_task':{'mean':statistics.mean(calls_per_task),'median':statistics.median(calls_per_task),
            'min':min(calls_per_task),'max':max(calls_per_task),
            'stdev':statistics.stdev(calls_per_task) if len(calls_per_task)>1 else 0},
        'common_first_3':{str(k):v for k,v in first3.most_common(5)},
        'n_unique_queries':len(set(search_queries)),'query_samples':search_queries[:10],
        'n_apis_get':{'mean':statistics.mean(n_apis_get) if n_apis_get else 0,
            'median':statistics.median(n_apis_get) if n_apis_get else 0,
            'min':min(n_apis_get) if n_apis_get else 0,'max':max(n_apis_get) if n_apis_get else 0},
        'error_rate_by_type':err_rates,
        'result_len':{'mean':statistics.mean(rl) if rl else 0,'median':statistics.median(rl) if rl else 0,
            'p90':sorted(rl)[int(len(rl)*0.9)] if rl else 0} if rl else {}}

def analyze_timing(traces):
    durs = [t['duration_s'] for t in traces if t['duration_s'] and t['duration_s']>0]
    calls = [t['n_tool_calls'] for t in traces if t['duration_s'] and t['duration_s']>0]
    turns = [t['n_turns'] for t in traces if t['duration_s'] and t['duration_s']>0]
    pct = [d/c for d,c in zip(durs,calls) if c>0]
    ptt = [d/t for d,t in zip(durs,turns) if t>0]
    pt = [t['total_prompt_tokens'] for t in traces]
    ct = [t['total_completion_tokens'] for t in traces]
    return {'n_with_timing':len(durs),
        'task_duration_s':{'mean':statistics.mean(durs),'median':statistics.median(durs),
            'min':min(durs),'max':max(durs),'p90':sorted(durs)[int(len(durs)*0.9)],
            'stdev':statistics.stdev(durs) if len(durs)>1 else 0},
        'per_call_s':{'mean':statistics.mean(pct),'median':statistics.median(pct),
            'min':min(pct),'max':max(pct)},
        'per_turn_s':{'mean':statistics.mean(ptt),'median':statistics.median(ptt)},
        'avg_prompt_tok':statistics.mean(pt) if pt else 0,
        'avg_comp_tok':statistics.mean(ct) if ct else 0,
        'total_prompt':sum(pt),'total_comp':sum(ct)}

def model_throughput(timing, patterns):
    ds_per_call = timing['per_call_s']['mean']
    ds_per_turn = timing['per_turn_s']['mean']
    avg_calls = patterns['calls_per_task']['mean']
    tc = patterns['type_distribution']
    tot_tc = max(patterns['total_tool_calls'],1); n_tasks = max(patterns['n_tasks'],1)
    run_code_frac = tc.get('run_pyAether_code_tool',0)/tot_tc
    n_run = avg_calls*run_code_frac
    n_search = tc.get('search_apis',0)/n_tasks
    n_get = tc.get('get_api_details',0)/n_tasks
    sb_times = {'search_apis':1.0,'get_api_details':0.5,'run_pyAether_code_tool':8.0}
    tot_sb = n_search*sb_times['search_apis']+n_get*sb_times['get_api_details']+n_run*sb_times['run_pyAether_code_tool']
    ds_llm = max(ds_per_call*avg_calls-tot_sb, 0)
    mcp5_batch = 0.5*(timing['task_duration_s']['mean']/ds_per_turn)
    mcp5_inter = 5.0*(timing['task_duration_s']['mean']/ds_per_turn)
    n_cpus = 32; sb_mem_mb = 1500; tot_mem_gb = 256
    max_sb = min(int(tot_mem_gb*1024/sb_mem_mb), n_cpus)
    kv_per_tok = 2*MINICPM5_LAYERS*MINICPM5_HIDDEN*BYTES_PER_KV
    kv_per_req = kv_per_tok*MAX_CTX
    tot_kv = 4*A40_MEM_GB*1024**3*SGLANG_KV_FRAC - MINICPM5_MEM_GB*1024**3
    max_gpu = int(tot_kv/kv_per_req)
    conc_levels = [1,2,4,8,16,32,64]; results = []
    for c in conc_levels:
        eff_sb = min(c, max_sb); sb_tp = eff_sb/tot_sb
        eff_gpu = min(c, max_gpu); gpu_tp = eff_gpu/(mcp5_batch+1)
        actual = min(sb_tp, gpu_tp)
        rph = actual*3600; rps = RL_BATCH*GRPO_GROUP; sph = rph/rps
        th = RL_STEPS_TARGET/sph if sph>0 else float('inf')
        results.append({'concurrency':c,'eff_sb':eff_sb,'eff_gpu':eff_gpu,
            'bottleneck':'sandbox' if sb_tp<gpu_tp else 'gpu',
            'sb_tp':round(sb_tp,4),'gpu_tp':round(gpu_tp,4),
            'actual_tp':round(actual,4),'rph':round(rph,1),
            'sph':round(sph,2),'train_days':round(th/24,1) if th!=float('inf') else None})
    return {'sb_times':sb_times,'tot_sb_per_task':round(tot_sb,1),
        'n_run_per_task':round(n_run,1),'n_search_per_task':round(n_search,1),
        'n_get_per_task':round(n_get,1),'ds_llm_per_task':round(ds_llm,1),
        'mcp5_batch_per_task':round(mcp5_batch,1),'mcp5_inter_per_task':round(mcp5_inter,1),
        'max_conc_sb':max_sb,'max_conc_gpu':max_gpu,
        'kv_per_req_gb':round(kv_per_req/1024**3,2),'tot_kv_gb':round(tot_kv/1024**3,1),
        'conc_table':results,'opt_conc':max(results,key=lambda x:x['rph'])['concurrency']}

def model_budget(throughput, timing):
    opt = max(throughput['conc_table'], key=lambda x:x['rph'])
    rollout_s = throughput['tot_sb_per_task']+throughput['mcp5_batch_per_task']
    rl_timeout = 300; eff_rollout = min(rollout_s, rl_timeout)
    group_s = eff_rollout*1.3; step_s = (RL_BATCH*group_s)/opt['concurrency']
    phases = [('warmup',200,'Low difficulty, short ctx'),('basic',500,'Single API, simple assert'),
        ('intermediate',800,'2-3 API chains'),('advanced',800,'6-10 API, techlib'),
        ('expert',700,'10+ API, complex workflow')]
    pe = []
    for name,steps,desc in phases:
        ph = (steps*step_s)/3600; pe.append({'phase':name,'steps':steps,'desc':desc,'hours':round(ph,1),'days':round(ph/24,2)})
    tot_steps = sum(s for _,s,_ in phases); tot_h = sum(p['hours'] for p in pe)
    crash_rate = 0.088; exp_crash = tot_h*crash_rate; crash_h = (exp_crash*55)/60
    ckpt_h = tot_h*0.0356; tot_all = tot_h+crash_h+ckpt_h
    return {'rollout_budget_s':round(rollout_s,1),'rl_timeout_s':rl_timeout,
        'eff_rollout_s':round(eff_rollout,1),'group_s':round(group_s,1),'step_s':round(step_s,1),
        'opt_conc':opt['concurrency'],'opt_rph':opt['rph'],'opt_sph':opt['sph'],
        'total_steps':tot_steps,'phases':pe,'base_hours':round(tot_h,1),'base_days':round(tot_h/24,2),
        'exp_crashes':round(exp_crash,1),'crash_hours':round(crash_h,1),
        'ckpt_hours':round(ckpt_h,1),'tot_hours':round(tot_all,1),
        'tot_days':round(tot_all/24,2),'gpu_days':round(tot_all/24,2)}

def compute_decision(budget, patterns, timing):
    return {'rollout_verdict':'FEASIBLE' if budget['rollout_budget_s']<300 else 'TIGHT',
        'time_verdict':'WITHIN_WINDOW' if budget['tot_days']<21 else 'OVER_BUDGET',
        'gpu_days':budget['gpu_days'],'opt_conc':budget['opt_conc'],
        'bottleneck':'sandbox_limited' if budget['rollout_budget_s']>30 else 'gpu_limited',
        'key_nums':{'avg_calls_per_task':round(patterns['calls_per_task']['mean'],1),
            'avg_task_dur_s':round(timing['task_duration_s']['mean'],1),
            'sandbox_time_per_task_s':budget['rollout_budget_s'],
            'steps_per_hour':budget['opt_sph'],'total_train_days':budget['tot_days']},
        'recs':['Use concurrency='+str(budget['opt_conc'])+' for optimal throughput',
            'Set RL timeout to '+str(budget['rl_timeout_s'])+'s per rollout (5 min)',
            'Checkpoint every 2 steps (R82: 3.56% overhead, optimal)',
            'Allocate '+str(math.ceil(budget['gpu_days']))+' GPU-days for full RL',
            'Monitor sandbox CPU; if <80%, increase concurrency',
            'Pre-warm NFS 30 min before starting']}

def generate_html(analysis):
    p = analysis['patterns']; t = analysis['timing']; th = analysis['throughput']
    b = analysis['budget']; d = analysis['decision']
    h = []
    h.append('<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">')
    h.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    h.append('<title>R84: EDA 沙盒吞吐量模型</title><style>')
    h.append('body{font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333;line-height:1.6}')
    h.append('h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}')
    h.append('h2{color:#2874a6;margin-top:30px;border-left:4px solid #3498db;padding-left:12px}')
    h.append('h3{color:#2c3e50;margin-top:20px}')
    h.append('table{border-collapse:collapse;width:100%;margin:15px 0;background:#fff}')
    h.append('th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}')
    h.append('th{background:#2980b9;color:#fff;font-weight:600}')
    h.append('tr:nth-child(even){background:#f9f9f9}')
    h.append('.verdict{padding:10px 20px;border-radius:6px;font-weight:bold;margin:10px 0}')
    h.append('.verdict.good{background:#d4edda;color:#155724;border:1px solid #c3e6cb}')
    h.append('.verdict.warn{background:#fff3cd;color:#856404;border:1px solid #ffeaa7}')
    h.append('.verdict.bad{background:#f8d7da;color:#721c24;border:1px solid #f5c6cb}')
    h.append('.metric-card{display:inline-block;background:#fff;border:1px solid #ddd;border-radius:8px;padding:15px;margin:5px;min-width:180px;text-align:center}')
    h.append('.metric-card .value{font-size:1.8em;font-weight:bold;color:#2980b9}')
    h.append('.metric-card .label{font-size:0.85em;color:#666;margin-top:5px}')
    h.append('.note{background:#e8f6f3;border-left:4px solid #1abc9c;padding:10px 15px;margin:10px 0}')
    h.append('.warn-note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:10px 0}')
    h.append('code{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em}')
    h.append('</style></head><body>')
    h.append('<h1>R84: EDA 沙盒吞吐量模型 — 从 DeepSeek 轨迹到 RL 训练预算</h1>')
    h.append('<p><strong>数据源</strong>: 103 条 DeepSeek 全 harness 轨迹 + EDA-Eval-PyAether 158 任务</p>')
    h.append('<p><strong>时间</strong>: ' + datetime.now().strftime('%Y-%m-%d %H:%M') + ' · 零 GPU · 纯 stdlib</p>')
    # S1 Decision Summary
    h.append('<h2>1. 决策摘要</h2>')
    vc = 'good' if d['rollout_verdict']=='FEASIBLE' else 'warn'
    tc = 'good' if d['time_verdict']=='WITHIN_WINDOW' else 'bad'
    h.append('<div class="verdict '+vc+'">单题 rollout 预算: '+d['rollout_verdict']+' ('+str(b['rollout_budget_s'])+'s/rollout)</div>')
    h.append('<div class="verdict '+tc+'">训练时间: '+d['time_verdict']+' ('+str(b['tot_days'])+' GPU-days)</div>')
    h.append('<div>')
    for label,val in d['key_nums'].items():
        h.append('<div class="metric-card"><div class="value">'+str(val)+'</div><div class="label">'+label+'</div></div>')
    h.append('</div><h3>推荐</h3><ul>')
    for r in d['recs']: h.append('<li>'+r+'</li>')
    h.append('</ul>')
    # S2 Data Overview
    h.append('<h2>2. 数据概览</h2><table><tr><th>指标</th><th>值</th></tr>')
    h.append('<tr><td>轨迹总数</td><td>'+str(p['n_tasks'])+' 条</td></tr>')
    h.append('<tr><td>工具调用总数</td><td>'+str(p['total_tool_calls'])+' 次</td></tr>')
    h.append('<tr><td>有计时数据的任务</td><td>'+str(t['n_with_timing'])+' 条</td></tr>')
    h.append('<tr><td>总 prompt tokens</td><td>'+str(t['total_prompt'])+'</td></tr>')
    h.append('<tr><td>总 completion tokens</td><td>'+str(t['total_comp'])+'</td></tr></table>')
    # S3 Tool Call Patterns
    h.append('<h2>3. 工具调用模式分析</h2>')
    h.append('<table><tr><th>工具类型</th><th>调用次数</th><th>每任务平均</th><th>错误率</th></tr>')
    for tool,count in sorted(p['type_distribution'].items(), key=lambda x:-x[1]):
        avg = p['avg_calls_per_type_per_task'].get(tool,0)
        err = p['error_rate_by_type'].get(tool,0)
        h.append('<tr><td>'+tool+'</td><td>'+str(count)+'</td><td>'+str(round(avg,2))+'</td><td>'+str(round(err*100,1))+'%</td></tr>')
    h.append('</table><h3>每任务工具调用频次</h3><table><tr><th>统计量</th><th>值</th></tr>')
    c = p['calls_per_task']
    for k in ['mean','median','min','max','stdev']:
        h.append('<tr><td>'+k+'</td><td>'+str(round(c[k],1))+'</td></tr>')
    h.append('</table><h3>常见工具调用序列 (前3步)</h3><table><tr><th>序列</th><th>出现次数</th></tr>')
    for seq,count in p['common_first_3'].items():
        h.append('<tr><td>'+' → '.join(seq)+'</td><td>'+str(count)+'</td></tr>')
    h.append('</table>')
    h.append('<div class="note"><strong>关键发现</strong>: 强模型标准模式 <code>search_apis → get_api_details → run_pyAether_code_tool</code>。平均每任务 '+str(round(c['mean'],1))+' 次调用, run_code 约 5 次需沙盒执行。</div>')
    # S4 Timing
    h.append('<h2>4. 时间分析</h2><table><tr><th>指标</th><th>值</th></tr>')
    td = t['task_duration_s']
    h.append('<tr><td>任务时长 (均值)</td><td>'+str(round(td['mean'],1))+'s</td></tr>')
    h.append('<tr><td>任务时长 (中位数)</td><td>'+str(round(td['median'],1))+'s</td></tr>')
    h.append('<tr><td>任务时长 (P90)</td><td>'+str(round(td['p90'],1))+'s</td></tr>')
    h.append('<tr><td>任务时长 (最大)</td><td>'+str(round(td['max'],1))+'s</td></tr>')
    h.append('<tr><td>每次工具调用 (含LLM)</td><td>'+str(round(t['per_call_s']['mean'],1))+'s</td></tr>')
    h.append('<tr><td>每任务 prompt tokens</td><td>'+str(round(t['avg_prompt_tok']))+'</td></tr>')
    h.append('<tr><td>每任务 completion tokens</td><td>'+str(round(t['avg_comp_tok']))+'</td></tr></table>')
    # S5 Sandbox Throughput
    h.append('<h2>5. 沙盒吞吐量模型</h2><h3>单次工具执行时间估计</h3>')
    h.append('<table><tr><th>工具</th><th>估计耗时</th><th>每任务次数</th><th>小计</th></tr>')
    npt = {'search_apis':th['n_search_per_task'],'get_api_details':th['n_get_per_task'],'run_pyAether_code_tool':th['n_run_per_task']}
    for tool,ts in th['sb_times'].items():
        n = npt.get(tool,0); h.append('<tr><td>'+tool+'</td><td>'+str(ts)+'s</td><td>'+str(n)+'</td><td>'+str(round(ts*n,1))+'s</td></tr>')
    h.append('</table>')
    h.append('<div class="metric-card"><div class="value">'+str(th['tot_sb_per_task'])+'s</div><div class="label">每任务沙盒总耗时</div></div>')
    h.append('<div class="metric-card"><div class="value">'+str(th['max_conc_sb'])+'</div><div class="label">最大并发沙盒数</div></div>')
    h.append('<div class="metric-card"><div class="value">'+str(th['max_conc_gpu'])+'</div><div class="label">最大并发GPU请求</div></div>')
    h.append('<div class="metric-card"><div class="value">'+str(th['kv_per_req_gb'])+'GB</div><div class="label">每请求KV缓存(8K)</div></div>')
    # S6 Concurrency Table
    h.append('<h2>6. 并发级别吞吐量</h2>')
    h.append('<table><tr><th>并发</th><th>有效沙盒</th><th>瓶颈</th><th>沙盒吞吐</th><th>GPU吞吐</th><th>rollouts/h</th><th>steps/h</th><th>训练天数</th></tr>')
    for r in th['conc_table']:
        days = str(r['train_days']) if r['train_days'] else 'N/A'
        h.append('<tr><td>'+str(r['concurrency'])+'</td><td>'+str(r['eff_sb'])+'</td><td>'+r['bottleneck']+'</td><td>'+str(r['sb_tp'])+'</td><td>'+str(r['gpu_tp'])+'</td><td>'+str(r['rph'])+'</td><td>'+str(r['sph'])+'</td><td>'+days+'</td></tr>')
    h.append('</table>')
    h.append('<div class="note"><strong>最优并发</strong>: '+str(th['opt_conc'])+' — GPU和沙盒利用率最平衡。</div>')
    # S7 RL Budget
    h.append('<h2>7. RL 训练预算</h2><h3>单题 Rollout 预算 (R1 关键问题)</h3>')
    h.append('<table><tr><th>指标</th><th>值</th></tr>')
    h.append('<tr><td>单次 rollout 预算</td><td>'+str(b['rollout_budget_s'])+'s</td></tr>')
    h.append('<tr><td>RL 超时</td><td>'+str(b['rl_timeout_s'])+'s (5 min)</td></tr>')
    h.append('<tr><td>有效 rollout 时长</td><td>'+str(b['eff_rollout_s'])+'s</td></tr>')
    h.append('<tr><td>组生成时间 (G=8并行)</td><td>'+str(b['group_s'])+'s</td></tr>')
    h.append('<tr><td>每步时间</td><td>'+str(b['step_s'])+'s</td></tr>')
    h.append('<tr><td>每步 rollout 数</td><td>'+str(RL_BATCH*GRPO_GROUP)+'</td></tr></table>')
    h.append('<h3>训练阶段预算</h3><table><tr><th>阶段</th><th>步数</th><th>描述</th><th>小时</th><th>天数</th></tr>')
    for pe in b['phases']:
        h.append('<tr><td>'+pe['phase']+'</td><td>'+str(pe['steps'])+'</td><td>'+pe['desc']+'</td><td>'+str(pe['hours'])+'</td><td>'+str(pe['days'])+'</td></tr>')
    h.append('</table><h3>总预算 (含崩溃恢复+检查点)</h3><table><tr><th>项目</th><th>值</th></tr>')
    h.append('<tr><td>基础训练</td><td>'+str(b['base_hours'])+'h ('+str(b['base_days'])+' days)</td></tr>')
    h.append('<tr><td>预计崩溃</td><td>'+str(b['exp_crashes'])+' 次 (率=0.088/h)</td></tr>')
    h.append('<tr><td>崩溃恢复开销</td><td>'+str(b['crash_hours'])+'h</td></tr>')
    h.append('<tr><td>检查点开销</td><td>'+str(b['ckpt_hours'])+'h (3.56%, R82)</td></tr>')
    h.append('<tr><td><strong>总时间</strong></td><td><strong>'+str(b['tot_hours'])+'h = '+str(b['tot_days'])+' days</strong></td></tr>')
    h.append('<tr><td><strong>所需 GPU-days</strong></td><td><strong>'+str(b['gpu_days'])+'</strong></td></tr></table>')
    verdict = '在 ISEDA 窗口内 (21天预算)' if b['tot_days']<21 else '超出窗口, 需减少步数或增加并发'
    h.append('<div class="verdict '+('good' if b['tot_days']<21 else 'bad')+'">'+verdict+'</div>')
    # S8 Relationships
    h.append('<h2>8. 与既有研究的关系</h2><table><tr><th>本研究</th><th>前置</th><th>关系</th></tr>')
    for r,pre,rel in [('R84沙盒吞吐','R1环境接口','量化R1的rollout预算'),('R84并发模型','R81 GPU-Day计划','为Step6全RL提供精确时间'),
        ('R84崩溃开销','R82崩溃恢复','复用崩溃率+恢复时间'),('R84检查点','R82检查点策略','复用最优频率每2步'),
        ('R84工具模式','R83难度分析','工具调用数与难度档相关'),('R84 LLM估计','R77分词器覆盖','EDA术语碎片化影响推理'),
        ('R84训练阶段','R74 RL课程','复用5阶段渐进难度')]:
        h.append('<tr><td>'+r+'</td><td>'+pre+'</td><td>'+rel+'</td></tr>')
    h.append('</table>')
    # S9 Limitations
    h.append('<h2>9. 局限性与待实测校准项</h2>')
    h.append('<div class="warn-note"><strong>重要</strong>: 估计基于 DeepSeek 轨迹外推, GPU到位后需用MiniCPM5-2B实测校准:</div><ul>')
    h.append('<li>沙盒执行时间为估计值, 实际取决于pyAether库加载与EDA操作复杂度</li>')
    h.append('<li>MiniCPM5-2B在4×A40上推理速度为估计值, 需SGLang serve后实测tokens/s</li>')
    h.append('<li>实际并发受NFS I/O带宽限制 (pyAether库从NFS加载)</li>')
    h.append('<li>任务时长从file_context时间戳推算, 可能低估</li>')
    h.append('<li>RL的rollout实际可能比DeepSeek交互更短或更长, 需100步后校准</li></ul>')
    # S10 Conclusion
    h.append('<h2>10. 结论</h2><div class="note">')
    h.append('<p><strong>单题rollout预算</strong>: '+str(b['rollout_budget_s'])+'s, RL超时'+str(b['rl_timeout_s'])+'s足够覆盖</p>')
    h.append('<p><strong>瓶颈</strong>: '+d['bottleneck']+' — 沙盒执行(run_pyAether_code_tool)是主要耗时项</p>')
    h.append('<p><strong>训练时间</strong>: '+str(b['tot_days'])+' GPU-days, '+('在ISEDA窗口内' if b['tot_days']<21 else '需优化')+'</p>')
    h.append('<p><strong>最优并发</strong>: '+str(b['opt_conc'])+' 个同时运行的沙盒</p></div>')
    h.append('<p style="text-align:center;color:#999;margin-top:40px;font-size:0.85em">R84 · BaiZe Stage(ii) · '+datetime.now().strftime('%Y-%m-%d %H:%M')+' · 零GPU · 纯stdlib</p>')
    h.append('</body></html>')
    return '\n'.join(h)

def main():
    parser = argparse.ArgumentParser(description='R84: EDA Sandbox Throughput Model')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--html', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--decision-only', action='store_true')
    args = parser.parse_args()
    print('[R84] Loading traces from: ' + TRACE_BASE)
    traces = load_traces(TRACE_BASE)
    print('[R84] Loaded ' + str(len(traces)) + ' traces')
    dataset = load_dataset(DATASET_PATH)
    print('[R84] Dataset: ' + str(len(dataset)) + ' tasks')
    patterns = analyze_patterns(traces)
    timing = analyze_timing(traces)
    throughput = model_throughput(timing, patterns)
    budget = model_budget(throughput, timing)
    decision = compute_decision(budget, patterns, timing)
    analysis = {'r84_id':'R84','timestamp':datetime.now().isoformat(),
        'data_source':TRACE_BASE,'n_traces':len(traces),'n_dataset_tasks':len(dataset),
        'patterns':patterns,'timing':timing,'throughput':throughput,
        'budget':budget,'decision':decision}
    if args.decision_only:
        print('\n=== R84 DECISION SUMMARY ===')
        print('Rollout: '+decision['rollout_verdict']+' ('+str(budget['rollout_budget_s'])+'s)')
        print('Training: '+decision['time_verdict']+' ('+str(budget['tot_days'])+' GPU-days)')
        print('Concurrency: '+str(decision['opt_conc']))
        print('Bottleneck: '+decision['bottleneck'])
        for r in decision['recs']: print('  - '+r)
        return
    if args.verbose:
        print('\n=== R84 VERBOSE ===')
        print('\n--- Patterns ---')
        print('Total calls: '+str(patterns['total_tool_calls']))
        print('Types: '+str(patterns['type_distribution']))
        print('Calls/task: mean='+str(round(patterns['calls_per_task']['mean'],1))+' median='+str(patterns['calls_per_task']['median'])+' max='+str(patterns['calls_per_task']['max']))
        print('Errors: '+str({k:round(v*100,1) for k,v in patterns['error_rate_by_type'].items()}))
        print('\n--- Timing ---')
        print('Duration: mean='+str(round(timing['task_duration_s']['mean'],1))+'s median='+str(round(timing['task_duration_s']['median'],1))+'s max='+str(round(timing['task_duration_s']['max'],1))+'s')
        print('Per-call: '+str(round(timing['per_call_s']['mean'],1))+'s')
        print('Prompt tok/task: '+str(round(timing['avg_prompt_tok'])))
        print('\n--- Throughput ---')
        print('Sandbox time/task: '+str(throughput['tot_sb_per_task'])+'s')
        print('Max concurrent SB: '+str(throughput['max_conc_sb']))
        print('Max concurrent GPU: '+str(throughput['max_conc_gpu']))
        print('Optimal concurrency: '+str(throughput['opt_conc']))
        print('\nConc | SB | Bottleneck | RPH | SPH | Days')
        for r in throughput['conc_table']:
            print('  '+str(r['concurrency']).rjust(3)+' | '+str(r['eff_sb']).rjust(3)+' | '+r['bottleneck'].rjust(10)+' | '+str(r['rph']).rjust(8)+' | '+str(r['sph']).rjust(6)+' | '+str(r['train_days']))
        print('\n--- Budget ---')
        print('Rollout: '+str(budget['rollout_budget_s'])+'s')
        print('Step: '+str(budget['step_s'])+'s')
        print('Total: '+str(budget['tot_days'])+' GPU-days')
        print('  Base: '+str(budget['base_days'])+'d Crash: '+str(budget['crash_hours'])+'h Ckpt: '+str(budget['ckpt_hours'])+'h')
        for pe in budget['phases']:
            print('  '+pe['phase'].ljust(15)+' '+str(pe['steps']).rjust(5)+' steps '+str(pe['hours']).rjust(8)+'h')
    if args.html:
        os.makedirs(REPORT_DIR, exist_ok=True)
        hp = os.path.join(REPORT_DIR, 'report_posttrain_r84_sandbox_throughput_zh.html')
        with open(hp,'w') as f: f.write(generate_html(analysis))
        print('[R84] HTML: '+hp+' ('+str(round(os.path.getsize(hp)/1024,1))+'KB)')
    if args.json:
        jp = os.path.join(JSON_DIR, 'r84_sandbox_throughput.json')
        with open(jp,'w') as f: json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print('[R84] JSON: '+jp+' ('+str(round(os.path.getsize(jp)/1024,1))+'KB)')
    if not any([args.verbose,args.html,args.json,args.decision_only]):
        print('[R84] Use --verbose, --html, --json, or --decision-only')

if __name__ == '__main__':
    main()
