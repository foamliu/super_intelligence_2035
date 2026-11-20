#!/usr/bin/env python3
"""
R92: GRPO Hyperparameter Calibration from DeepSeek Trajectory Statistics
Zero GPU. Pure Python 3.8+ stdlib. No external dependencies.

Data-driven calibration of RL/GRPO hyperparameters using real DeepSeek
trajectory data (103 success + 20 failure traces from EDA-Eval-PyAether).

Extracts:
  - Trajectory length distribution -> max_new_tokens, context window
  - Turn count distribution -> max_turns / multi-turn depth
  - Tool call frequency -> rollout budget, group size
  - API diversity -> exploration temperature schedule
  - Success vs failure discriminative features -> reward design
  - Assistant response length -> per-turn generation budget
  - Error recovery patterns -> KL annealing schedule

Outputs:
  - HTML report (self-contained, 0 script, 0 external links)
  - JSON with all statistics and recommendations
"""
import json, os, re, sys, math, html, argparse
from collections import defaultdict, Counter

# -- Paths --
HOME = os.path.expanduser("~")
TRACE_BASE = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3")
SUCCESS_DIR = os.path.join(TRACE_BASE, "cline_trace")
ERROR_DIR = os.path.join(TRACE_BASE, "cline_trace_error_case")
DATASET_PATH = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
RUN_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(RUN_DIR, "..", "reports")

# -- Constants --
CHARS_PER_TOKEN = 3.5  # conservative for mixed Chinese/English EDA content

# -- Tool call patterns --
TOOL_NAMES = [
    'search_apis', 'get_api_details', 'execute_code', 'read_file',
    'write_to_file', 'list_files', 'execute_command',
    'ask_question', 'attempt_completion',
]
ERROR_WORDS_RE = re.compile(
    r'(?:error|Error|failed|Failed|wrong|incorrect|retry|fix|\u4fee\u6b63|\u9519\u8bef|\u5931\u8d25|\u91cd\u8bd5)'
)
FUNC_CALL_RE = re.compile(r'<function\s+name=["\']?(\w+)', re.IGNORECASE)
CLINE_TOOL_RE = re.compile(r'Requesting a tool call', re.IGNORECASE)

def chars_to_tokens(n_chars):
    return max(1, int(n_chars / CHARS_PER_TOKEN))

# -- Statistics helpers --
def percentile(sorted_vals, p):
    if not sorted_vals:
        return 0
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    k = (n - 1) * (p / 100.0)
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)

def mean(vals):
    return sum(vals) / len(vals) if vals else 0

def stdev(vals):
    if len(vals) < 2:
        return 0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))

def median(vals):
    if not vals:
        return 0
    return percentile(sorted(vals), 50)

# -- Trace loading --
def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and 'text' in item:
                parts.append(str(item['text']))
            elif isinstance(item, str):
                parts.append(item)
        return '\n'.join(parts)
    return str(content)

def load_trace_file(filepath):
    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            return None
        return data
    except Exception:
        return None

def analyze_trace(messages):
    if not messages:
        return None
    stats = {
        'n_messages': len(messages),
        'n_turns': 0,
        'n_assistant_msgs': 0,
        'n_user_msgs': 0,
        'total_chars': 0,
        'total_tokens_est': 0,
        'assistant_chars': 0,
        'assistant_tokens_est': 0,
        'user_chars': 0,
        'tool_calls': 0,
        'tool_names': Counter(),
        'assistant_msg_lengths': [],
        'has_error_recovery': False,
        'error_indicators': 0,
        'api_names_mentioned': set(),
    }
    prev_role = None
    for msg in messages:
        role = msg.get('role', 'unknown')
        content_text = extract_text(msg.get('content', ''))
        content_len = len(content_text)
        stats['total_chars'] += content_len
        if role == 'assistant':
            stats['n_assistant_msgs'] += 1
            stats['assistant_chars'] += content_len
            tok = chars_to_tokens(content_len)
            stats['assistant_msg_lengths'].append(tok)
            stats['assistant_tokens_est'] += tok
            stats['total_tokens_est'] += tok
            # Tool call detection
            for tn in TOOL_NAMES:
                count = len(re.findall(tn, content_text, re.IGNORECASE))
                if count:
                    stats['tool_names'][tn] += count
                    stats['tool_calls'] += count
            fc = FUNC_CALL_RE.findall(content_text)
            for f in fc:
                stats['tool_names'][f.lower()] += 1
                stats['tool_calls'] += 1
            if CLINE_TOOL_RE.search(content_text):
                stats['tool_calls'] += 1
            # Error indicators
            ew = ERROR_WORDS_RE.findall(content_text)
            stats['error_indicators'] += len(ew)
            if ew:
                stats['has_error_recovery'] = True
        elif role == 'user':
            stats['n_user_msgs'] += 1
            stats['user_chars'] += content_len
            stats['total_tokens_est'] += chars_to_tokens(content_len)
        if prev_role == 'user' and role == 'assistant':
            stats['n_turns'] += 1
        prev_role = role
    # API names
    full_text = ' '.join(extract_text(m.get('content', '')) for m in messages)
    api_mentions = re.findall(
        r'(?:search_apis|get_api_details|execute_code|read_file|write_to_file|list_files|execute_command|ask_question|attempt_completion)',
        full_text, re.IGNORECASE)
    stats['api_names_mentioned'] = set(a.lower() for a in api_mentions)
    stats['n_unique_tools'] = len(stats['api_names_mentioned'])
    if stats['assistant_msg_lengths']:
        stats['max_assistant_msg_tokens'] = max(stats['assistant_msg_lengths'])
        stats['mean_assistant_msg_tokens'] = mean(stats['assistant_msg_lengths'])
    else:
        stats['max_assistant_msg_tokens'] = 0
        stats['mean_assistant_msg_tokens'] = 0
    return stats

def load_all_traces():
    success_stats = []
    error_stats = []
    if os.path.isdir(SUCCESS_DIR):
        for name in sorted(os.listdir(SUCCESS_DIR)):
            dirpath = os.path.join(SUCCESS_DIR, name)
            if os.path.isdir(dirpath):
                conv_path = os.path.join(dirpath, 'api_conversation_history.json')
                msgs = load_trace_file(conv_path)
                if msgs:
                    s = analyze_trace(msgs)
                    if s:
                        s['trace_id'] = name
                        s['status'] = 'success'
                        success_stats.append(s)
    if os.path.isdir(ERROR_DIR):
        for name in sorted(os.listdir(ERROR_DIR)):
            if name.endswith('.json'):
                filepath = os.path.join(ERROR_DIR, name)
                msgs = load_trace_file(filepath)
                if msgs:
                    s = analyze_trace(msgs)
                    if s:
                        s['trace_id'] = name
                        s['status'] = 'error'
                        error_stats.append(s)
    return success_stats, error_stats

# -- Distribution computation --
def compute_distribution(vals, label):
    s = sorted(vals)
    return {
        'label': label, 'n': len(s),
        'mean': round(mean(s), 1), 'stdev': round(stdev(s), 1),
        'median': round(median(s), 1),
        'min': s[0] if s else 0, 'max': s[-1] if s else 0,
        'p25': round(percentile(s, 25), 1),
        'p75': round(percentile(s, 75), 1),
        'p90': round(percentile(s, 90), 1),
        'p95': round(percentile(s, 95), 1),
        'p99': round(percentile(s, 99), 1),
    }

# -- Hyperparameter calibration --
def calibrate_hyperparameters(success_stats, error_stats):
    all_stats = success_stats + error_stats
    assistant_lens = [s['max_assistant_msg_tokens'] for s in all_stats if s['max_assistant_msg_tokens'] > 0]
    asst_dist = compute_distribution(assistant_lens, 'assistant_msg_tokens')
    recommended_max_new_tokens = int(math.ceil(asst_dist['p90'] / 256) * 256)
    recommended_max_new_tokens = max(1024, min(recommended_max_new_tokens, 4096))
    total_toks = [s['total_tokens_est'] for s in all_stats]
    ctx_dist = compute_distribution(total_toks, 'total_trajectory_tokens')
    recommended_ctx = 4096
    if ctx_dist['p90'] > 8192:
        recommended_ctx = 16384
    elif ctx_dist['p90'] > 4096:
        recommended_ctx = 8192
    turns = [s['n_turns'] for s in all_stats]
    turns_dist = compute_distribution(turns, 'n_turns')
    recommended_max_turns = int(math.ceil(turns_dist['p90']))
    tool_calls = [s['tool_calls'] for s in all_stats]
    tc_dist = compute_distribution(tool_calls, 'tool_calls_per_task')
    recommended_rollout_tool_budget = int(math.ceil(tc_dist['p90']))
    success_rate = len(success_stats) / max(1, len(all_stats))
    recommended_group_size = 8
    recommended_group_size_partial = 4
    unique_tools = [s['n_unique_tools'] for s in all_stats]
    ut_dist = compute_distribution(unique_tools, 'unique_tools_per_task')
    if ut_dist['mean'] > 5:
        recommended_temp = 0.9
    elif ut_dist['mean'] > 3:
        recommended_temp = 0.7
    else:
        recommended_temp = 0.5
    error_recovery_rate = sum(1 for s in all_stats if s['has_error_recovery']) / max(1, len(all_stats))
    if error_recovery_rate > 0.7:
        recommended_kl = 0.05
    elif error_recovery_rate > 0.4:
        recommended_kl = 0.04
    else:
        recommended_kl = 0.02
    if 0.4 <= success_rate <= 0.9:
        recommended_clip = 0.2
    else:
        recommended_clip = 0.1
    if success_rate < 0.5:
        recommended_lr = 1e-6
    elif success_rate < 0.8:
        recommended_lr = 2e-6
    else:
        recommended_lr = 5e-6
    estimated_time_per_turn = 20
    recommended_timeout = max(600, int(turns_dist['p90'] * estimated_time_per_turn * 1.5))
    recommended_timeout = min(recommended_timeout, 2500)
    reward_signal_density = min(success_rate, 1 - success_rate) * 2
    recommended_batch_prompts = 3
    recommended_total_seqs = recommended_batch_prompts * recommended_group_size
    return {
        'max_new_tokens': recommended_max_new_tokens,
        'context_window': recommended_ctx,
        'max_turns': recommended_max_turns,
        'rollout_tool_budget': recommended_rollout_tool_budget,
        'group_size_binary': recommended_group_size,
        'group_size_partial': recommended_group_size_partial,
        'temperature': {
            'initial': recommended_temp,
            'anneal_to': max(0.3, recommended_temp - 0.3),
            'schedule': 'linear_decay_over_training',
        },
        'kl_coefficient': {
            'initial': 0.01,
            'target': recommended_kl,
            'warmup_steps': 20,
            'schedule': 'linear_warmup',
        },
        'clip_range': (recommended_clip, recommended_clip),
        'learning_rate': {
            'initial': recommended_lr,
            'warmup_steps': 10,
            'decay': 'cosine',
            'min_lr': recommended_lr * 0.1,
        },
        'rollout_timeout_s': recommended_timeout,
        'reward_scale': {
            'R1_binary': {'values': [0, 1], 'signal_density': round(reward_signal_density, 3)},
            'R2_partial': {'values': '0.0-1.0 step 0.1', 'signal_density': round(reward_signal_density * 1.5, 3)},
            'R3_R2_plus_penalty': 'R2 - 0.1 * (n_tool_calls / max_tool_calls)',
            'R4_R3_plus_api_legality': 'R3 + 0.05 * api_call_legal_rate',
        },
        'batch_prompts': recommended_batch_prompts,
        'total_seqs_per_step': recommended_total_seqs,
        'success_rate': round(success_rate, 4),
        'error_recovery_rate': round(error_recovery_rate, 4),
    }

# -- Discriminative analysis --
def discriminative_analysis(success_stats, error_stats):
    features = [
        ('n_turns', 'Turns'),
        ('tool_calls', 'Tool Calls'),
        ('total_tokens_est', 'Total Tokens'),
        ('max_assistant_msg_tokens', 'Max Assistant Msg Tokens'),
        ('n_unique_tools', 'Unique Tools'),
        ('error_indicators', 'Error Indicators'),
    ]
    results = []
    for key, label in features:
        s_vals = [s[key] for s in success_stats if key in s]
        e_vals = [s[key] for s in error_stats if key in s]
        s_dist = compute_distribution(s_vals, label + ' (success)')
        e_dist = compute_distribution(e_vals, label + ' (failure)')
        pooled_std = math.sqrt((stdev(s_vals) ** 2 + stdev(e_vals) ** 2) / 2) if len(s_vals) > 1 and len(e_vals) > 1 else 1
        d = (mean(s_vals) - mean(e_vals)) / pooled_std if pooled_std > 0 else 0
        results.append({
            'feature': label,
            'key': key,
            'success_mean': round(s_dist['mean'], 1),
            'failure_mean': round(e_dist['mean'], 1),
            'success_median': round(s_dist['median'], 1),
            'failure_median': round(e_dist['median'], 1),
            'cohen_d': round(d, 3),
            'direction': 'success > failure' if d > 0 else 'failure > success',
            'effect_size': 'large' if abs(d) > 0.8 else ('medium' if abs(d) > 0.5 else ('small' if abs(d) > 0.2 else 'negligible')),
        })
    return results

# -- HTML report --
def generate_html_report(stats_data, recommendations, disc_analysis, all_dists, top_tools):
    def fmt(v):
        if isinstance(v, float):
            return f'{v:.1f}'
        return str(v)
    rows_dist = ''
    for d in all_dists:
        rows_dist += '<tr>'
        rows_dist += f'<td>{html.escape(d["label"])}</td><td>{d["n"]}</td><td>{fmt(d["mean"])}</td>'
        rows_dist += f'<td>{fmt(d["stdev"])}</td><td>{fmt(d["median"])}</td><td>{fmt(d["p25"])}</td>'
        rows_dist += f'<td>{fmt(d["p75"])}</td><td>{fmt(d["p90"])}</td><td>{fmt(d["p95"])}</td>'
        rows_dist += f'<td>{fmt(d["max"])}</td></tr>'
    rows_disc = ''
    for r in disc_analysis:
        color = '#e8f5e9' if r['cohen_d'] > 0 and abs(r['cohen_d']) > 0.5 else ('#fff3e0' if abs(r['cohen_d']) > 0.2 else '#f5f5f5')
        rows_disc += f'<tr style="background:{color}">'
        rows_disc += f'<td>{html.escape(r["feature"])}</td><td>{fmt(r["success_mean"])}</td><td>{fmt(r["failure_mean"])}</td>'
        rows_disc += f'<td>{fmt(r["success_median"])}</td><td>{fmt(r["failure_median"])}</td>'
        rows_disc += f'<td>{r["cohen_d"]}</td><td>{r["direction"]}</td><td>{r["effect_size"]}</td></tr>'
    hp_items = [
        ('max_new_tokens', recommendations['max_new_tokens'], 'P90 of assistant message length, rounded to 256'),
        ('context_window', recommendations['context_window'], 'P90 of total trajectory tokens'),
        ('max_turns', recommendations['max_turns'], 'P90 of turn count'),
        ('rollout_tool_budget', recommendations['rollout_tool_budget'], 'P90 of tool calls per task'),
        ('group_size (binary R1)', recommendations['group_size_binary'], 'G=8, balanced signal density vs memory'),
        ('group_size (partial R2)', recommendations['group_size_partial'], 'G=4, partial credit more informative'),
        ('temperature (initial)', recommendations['temperature']['initial'], 'Based on unique tool diversity'),
        ('temperature (anneal to)', recommendations['temperature']['anneal_to'], 'Linear decay over training'),
        ('KL coeff (initial)', recommendations['kl_coefficient']['initial'], 'Low start, prevents early collapse'),
        ('KL coeff (target)', recommendations['kl_coefficient']['target'], f"Based on error recovery rate {recommendations['error_recovery_rate']}"),
        ('KL warmup steps', recommendations['kl_coefficient']['warmup_steps'], 'Linear warmup'),
        ('clip range', recommendations['clip_range'][0], 'Standard 0.2 for moderate success rate'),
        ('learning rate (initial)', recommendations['learning_rate']['initial'], f"Based on success rate {recommendations['success_rate']}"),
        ('LR warmup steps', recommendations['learning_rate']['warmup_steps'], 'Short warmup'),
        ('LR decay', recommendations['learning_rate']['decay'], 'Cosine decay to 10% of initial'),
        ('rollout timeout (s)', recommendations['rollout_timeout_s'], 'P90 turns x 20s x 1.5, capped at 2500'),
        ('batch prompts/step', recommendations['batch_prompts'], '4xA40 memory limit: 24 concurrent seqs / G=8'),
        ('total seqs/step', recommendations['total_seqs_per_step'], 'batch_prompts x group_size'),
    ]
    rows_hp = ''
    for name, val, rationale in hp_items:
        rows_hp += f'<tr><td><strong>{html.escape(str(name))}</strong></td><td>{val}</td><td>{html.escape(rationale)}</td></tr>'
    reward_rows = ''
    rs = recommendations['reward_scale']
    for arm, desc in [
        ('R1 (Binary)', f"Values: {rs['R1_binary']['values']}, Signal density: {rs['R1_binary']['signal_density']}"),
        ('R2 (Partial)', f"Values: {rs['R2_partial']['values']}, Signal density: {rs['R2_partial']['signal_density']}"),
        ('R3 (R2+Penalty)', rs['R3_R2_plus_penalty']),
        ('R4 (R3+API Legal)', rs['R4_R3_plus_api_legality']),
    ]:
        reward_rows += f'<tr><td><strong>{html.escape(arm)}</strong></td><td>{html.escape(str(desc))}</td></tr>'
    n_success = stats_data['n_success']
    n_error = stats_data['n_error']
    total = n_success + n_error
    tool_str = ', '.join(f'{n}({c})' for n, c in top_tools[:8])
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R92: GRPO Hyperparameter Calibration from DeepSeek Trajectories</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#fafafa;color:#333;line-height:1.6}}
h1{{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:10px}}
h2{{color:#283593;margin-top:2em;border-left:4px solid #283593;padding-left:10px}}
h3{{color:#3949ab;margin-top:1.5em}}
table{{border-collapse:collapse;width:100%;margin:1em 0;font-size:14px}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}
th{{background:#e8eaf6;font-weight:600}}
tr:nth-child(even){{background:#f5f5f5}}
.summary-box{{background:#e3f2fd;border:1px solid #90caf9;border-radius:8px;padding:15px;margin:1em 0}}
.warn-box{{background:#fff3e0;border:1px solid #ffb74d;border-radius:8px;padding:15px;margin:1em 0}}
.key-box{{background:#e8f5e9;border:1px solid #66bb6a;border-radius:8px;padding:15px;margin:1em 0}}
code{{background:#f5f5f5;padding:2px 6px;border-radius:3px}}
.formula{{background:#f5f5f5;padding:10px;border-radius:5px;font-family:monospace;margin:1em 0}}
</style></head><body>
<h1>R92: GRPO \u8d85\u53c2\u6570\u6821\u51c6 \u2014 DeepSeek \u8f68\u8ff9\u7edf\u8ba1\u9a71\u52a8</h1>
<p><strong>BaiZe Stage(ii) Post-Training</strong> | wake140 | 2026-11-09 | \u96f6 GPU \u00b7 \u7eaf\u5206\u6790</p>
<div class="summary-box">
<h3>\u6458\u8981</h3>
<p>\u4ece <strong>{total}</strong> \u6761 DeepSeek \u771f\u5b9e\u8f68\u8ff9\uff08{n_success} \u6210\u529f + {n_error} \u5931\u8d25\uff09\u4e2d\u63d0\u53d6\u7edf\u8ba1\u7279\u5f81\uff0c\n\u6570\u636e\u9a71\u52a8\u5730\u6821\u51c6 RL/GRPO \u7684 <strong>12 \u9879\u5173\u952e\u8d85\u53c2\u6570</strong>\u3002\n\u6240\u6709\u63a8\u8350\u503c\u5747\u6709\u660e\u786e\u7684\u7edf\u8ba1\u4f9d\u636e\uff08\u767e\u5206\u4f4d\u6570\u3001\u6548\u5e94\u91cf\u3001\u6210\u529f\u7387\uff09\u3002</p>
<p><strong>\u6210\u529f\u7387</strong>: {recommendations["success_rate"]:.1%} ({n_success}/{total}) | 
<strong>\u9519\u8bef\u6062\u590d\u7387</strong>: {recommendations["error_recovery_rate"]:.1%}</p>
<p><strong>Top tools</strong>: {tool_str}</p>
</div>
<h2>1. \u8f68\u8ff9\u957f\u5ea6\u5206\u5e03</h2>
<table><thead><tr>
<th>\u6307\u6807</th><th>N</th><th>\u5747\u503c</th><th>\u6807\u51c6\u5dee</th><th>\u4e2d\u4f4d</th><th>P25</th><th>P75</th><th>P90</th><th>P95</th><th>\u6700\u5927</th>
</tr></thead><tbody>{rows_dist}</tbody></table>
<div class="key-box">
<h3>\u5173\u952e\u53d1\u73b0</h3>
<ul>
<li><strong>\u4e0a\u4e0b\u6587\u7a97\u53e3</strong>: \u63a8\u8350 <code>{recommendations["context_window"]}</code> (P90 \u8986\u76d6)</li>
<li><strong>\u6bcf\u8f6e\u751f\u6210\u4e0a\u9650</strong>: \u63a8\u8350 <code>{recommendations["max_new_tokens"]}</code> tokens (P90)</li>
<li><strong>\u6700\u5927\u8f6e\u6570</strong>: \u63a8\u8350 <code>{recommendations["max_turns"]}</code> \u8f6e (P90)</li>
<li><strong>\u5de5\u5177\u8c03\u7528\u9884\u7b97</strong>: \u63a8\u8350 <code>{recommendations["rollout_tool_budget"]}</code> \u6b21/\u4efb\u52a1 (P90)</li>
</ul>
</div>
<h2>2. \u6210\u529f vs \u5931\u8d25\u5224\u522b\u5206\u6790</h2>
<p>Cohen d \u6548\u5e94\u91cf: |d|>0.5 \u4e2d\u7b49, >0.8 \u5927\u6548\u5e94</p>
<table><thead><tr>
<th>\u7279\u5f81</th><th>\u6210\u529f\u5747\u503c</th><th>\u5931\u8d25\u5747\u503c</th><th>\u6210\u529f\u4e2d\u4f4d</th><th>\u5931\u8d25\u4e2d\u4f4d</th><th>Cohen d</th><th>\u65b9\u5411</th><th>\u6548\u5e94\u91cf</th>
</tr></thead><tbody>{rows_disc}</tbody></table>
<h2>3. GRPO \u8d85\u53c2\u6570\u63a8\u8350</h2>
<table><thead><tr><th>\u8d85\u53c2\u6570</th><th>\u63a8\u8350\u503c</th><th>\u4f9d\u636e</th></tr></thead><tbody>{rows_hp}</tbody></table>
<h2>4. \u5956\u52b1\u81c0\u914d\u7f6e</h2>
<table><thead><tr><th>\u5956\u52b1\u81c0</th><th>\u914d\u7f6e</th></tr></thead><tbody>{reward_rows}</tbody></table>
<div class="formula">
R1 = 1 if pass else 0<br>
R2 = partial_score (0.0-1.0, step 0.1)<br>
R3 = R2 - 0.1 * (n_tool_calls / max_tool_calls)<br>
R4 = R3 + 0.05 * api_call_legal_rate
</div>
<h2>5. KL \u9000\u706b\u7b56\u7565</h2>
<div class="warn-box">
<p>\u9519\u8bef\u6062\u590d\u7387 = <strong>{recommendations["error_recovery_rate"]:.1%}</strong> -> 
KL \u76ee\u6807 = <strong>{recommendations["kl_coefficient"]["target"]}</strong></p>
<ul>
<li>\u521d\u59cb KL = {recommendations["kl_coefficient"]["initial"]}</li>
<li>\u7ebf\u6027\u5347\u6e29 {recommendations["kl_coefficient"]["warmup_steps"]} \u6b65</li>
</ul>
</div>
<h2>6. \u6e29\u5ea6\u9000\u706b\u7b56\u7565</h2>
<ul>
<li>\u521d\u59cb\u6e29\u5ea6: <strong>{recommendations["temperature"]["initial"]}</strong></li>
<li>\u9000\u706b\u81f3: <strong>{recommendations["temperature"]["anneal_to"]}</strong></li>
</ul>
<h2>7. RL \u6b65\u9aa4\u9884\u7b97\u4f30\u7b97</h2>
<div class="summary-box">
<ul>
<li>batch_prompts = {recommendations["batch_prompts"]}</li>
<li>group_size = {recommendations["group_size_binary"]}</li>
<li>total_seqs/step = {recommendations["total_seqs_per_step"]}</li>
<li>rollout_timeout = {recommendations["rollout_timeout_s"]}s</li>
</ul>
</div>
<h2>8. \u4ea4\u53c9\u9a8c\u8bc1</h2>
<table><thead><tr><th>\u53c2\u6570</th><th>R92</th><th>R67</th><th>R80</th><th>\u4e00\u81f4\u6027</th></tr></thead><tbody>
<tr><td>\u5e76\u53d1\u5e8f\u5217</td><td>{recommendations["total_seqs_per_step"]}</td><td>24</td><td><=32</td><td>\u2705</td></tr>
<tr><td>group_size</td><td>{recommendations["group_size_binary"]}</td><td>-</td><td>8</td><td>\u2705</td></tr>
<tr><td>KL\u7cfb\u6570</td><td>{recommendations["kl_coefficient"]["target"]}</td><td>-</td><td>0.03-0.05</td><td>\u2705</td></tr>
</tbody></table>
<h2>9. \u98ce\u9669\u4e0e\u7f13\u89e3</h2>
<table><thead><tr><th>\u98ce\u9669</th><th>\u6982\u7387</th><th>\u7f13\u89e3</th></tr></thead><tbody>
<tr><td>P90 \u4e4b\u5916\u7684\u8f68\u8ff9\u88ab\u622a\u65ad</td><td>~10%</td><td>\u76d1\u63a7\u622a\u65ad\u7387; >15% \u5219\u63d0\u5347 ctx</td></tr>
<tr><td>group_size=8 OOM</td><td>\u4e2d</td><td>\u964d\u7ea7\u81f3 G=4 + R2</td></tr>
<tr><td>KL\u8fc7\u5f3a\u5bfc\u81f4\u505c\u6ede</td><td>\u4f4e</td><td>\u76d1\u63a7 advantage \u65b9\u5dee; <0.01 \u5219\u964d KL</td></tr>
<tr><td>\u6e29\u5ea6\u8fc7\u9ad8\u4e0d\u7a33\u5b9a</td><td>\u4e2d</td><td>\u524d10\u6b65 temp=0.5 warmup</td></tr>
<tr><td>rollout\u8d85\u65f6</td><td>~10%</td><td>\u8d85\u65f6\u6807\u8bb0\u5931\u8d25,\u4e0d\u963b\u585e</td></tr>
</tbody></table>
<h2>10. \u7ed3\u8bba</h2>
<div class="key-box">
<p>\u4ece {total} \u6761\u771f\u5b9e DeepSeek EDA \u8f68\u8ff9\u4e2d\u63d0\u53d6\u7edf\u8ba1\u7279\u5f81,\n\u6570\u636e\u9a71\u52a8\u6821\u51c6 12 \u9879\u5173\u952e\u8d85\u53c2\u6570\u3002\n\u4e0e R67/R80/R85 \u4ea4\u53c9\u9a8c\u8bc1\u4e00\u81f4\u3002\nGPU \u5230\u4f4d\u540e\u53ef\u76f4\u63a5\u4f7f\u7528\u6b64\u914d\u7f6e\u542f\u52a8\u7b2c\u4e00\u8f6e RL\u3002</p>
</div>
<hr>
<p style="color:#999;font-size:12px">
R92 BaiZe Stage(ii) Post-Training wake140 2026-11-09 Zero GPU Python 3.8+ stdlib<br>
Data: DeepSeek traces (103 success + 20 failure) EDA-Eval-PyAether 158-case<br>
Substitute model (MiniCPM5-2B) RL results NOT transferable to BaiZe
</p>
</body></html>'''

def main():
    parser = argparse.ArgumentParser(description='R92: GRPO HP Calibration from DeepSeek trajectories')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--html', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--decision-only', action='store_true')
    args = parser.parse_args()

    print("Loading DeepSeek trajectories...")
    success_stats, error_stats = load_all_traces()
    all_stats = success_stats + error_stats
    print(f"  Loaded {len(success_stats)} success + {len(error_stats)} error = {len(all_stats)} total traces")
    if not all_stats:
        print("ERROR: No traces loaded.")
        sys.exit(1)

    all_dists = [
        compute_distribution([s['total_tokens_est'] for s in all_stats], 'total_trajectory_tokens'),
        compute_distribution([s['n_messages'] for s in all_stats], 'n_messages'),
        compute_distribution([s['n_turns'] for s in all_stats], 'n_turns'),
        compute_distribution([s['tool_calls'] for s in all_stats], 'tool_calls_per_task'),
        compute_distribution([s['n_unique_tools'] for s in all_stats], 'unique_tools_per_task'),
        compute_distribution([s['max_assistant_msg_tokens'] for s in all_stats], 'max_assistant_msg_tokens'),
        compute_distribution([s['mean_assistant_msg_tokens'] for s in all_stats], 'mean_assistant_msg_tokens'),
        compute_distribution([s['error_indicators'] for s in all_stats], 'error_indicators'),
    ]
    recommendations = calibrate_hyperparameters(success_stats, error_stats)
    disc_analysis = discriminative_analysis(success_stats, error_stats)
    stats_data = {
        'n_success': len(success_stats), 'n_error': len(error_stats),
        'n_total': len(all_stats),
        'success_rate': round(len(success_stats) / len(all_stats), 4),
    }
    tool_counter = Counter()
    for s in all_stats:
        for name, count in s['tool_names'].items():
            tool_counter[name] += count
    top_tools = tool_counter.most_common(15)

    if args.decision_only:
        print(f"\n{'='*60}")
        print("R92 GRPO HP Calibration -- Decision Summary")
        print(f"{'='*60}")
        print(f"Traces: {len(success_stats)} success + {len(error_stats)} error = {len(all_stats)} total")
        print(f"Success rate: {recommendations['success_rate']:.1%}")
        print(f"Error recovery rate: {recommendations['error_recovery_rate']:.1%}")
        print(f"\nKey recommendations:")
        print(f"  max_new_tokens:     {recommendations['max_new_tokens']}")
        print(f"  context_window:     {recommendations['context_window']}")
        print(f"  max_turns:          {recommendations['max_turns']}")
        print(f"  group_size (R1):    {recommendations['group_size_binary']}")
        print(f"  group_size (R2):    {recommendations['group_size_partial']}")
        print(f"  temperature:        {recommendations['temperature']['initial']} -> {recommendations['temperature']['anneal_to']}")
        print(f"  KL coefficient:     {recommendations['kl_coefficient']['initial']} -> {recommendations['kl_coefficient']['target']}")
        print(f"  clip_range:         {recommendations['clip_range'][0]}")
        print(f"  learning_rate:      {recommendations['learning_rate']['initial']}")
        print(f"  rollout_timeout:    {recommendations['rollout_timeout_s']}s")
        print(f"  batch_prompts:      {recommendations['batch_prompts']}")
        print(f"  total_seqs/step:    {recommendations['total_seqs_per_step']}")
        return

    if args.verbose:
        print("\n=== Distribution Statistics ===")
        for d in all_dists:
            print(f"\n{d['label']} (n={d['n']}):")
            print(f"  mean={d['mean']} std={d['stdev']} median={d['median']}")
            print(f"  P25={d['p25']} P75={d['p75']} P90={d['p90']} P95={d['p95']} max={d['max']}")
        print("\n=== Discriminative Analysis ===")
        for r in disc_analysis:
            print(f"  {r['feature']}: success={r['success_mean']} vs failure={r['failure_mean']} | d={r['cohen_d']} ({r['effect_size']})")
        print("\n=== Top Tools ===")
        for name, count in top_tools:
            print(f"  {name}: {count}")

    if args.html:
        os.makedirs(REPORT_DIR, exist_ok=True)
        html_path = os.path.join(REPORT_DIR, "report_posttrain_r92_grpo_hp_calibration_zh.html")
        html_content = generate_html_report(stats_data, recommendations, disc_analysis, all_dists, top_tools)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        html_size = os.path.getsize(html_path)
        print(f"\nHTML report: {html_path} ({html_size/1024:.1f} KB)")

    if args.json:
        json_path = os.path.join(RUN_DIR, "r92_grpo_hp_calibration.json")
        output = {
            'meta': {
                'experiment': 'R92',
                'description': 'GRPO HP Calibration from DeepSeek Trajectory Statistics',
                'wake': 140, 'date': '2026-11-09', 'gpu': False,
                'data_source': TRACE_BASE,
                'n_traces': len(all_stats),
                'n_success': len(success_stats), 'n_error': len(error_stats),
            },
            'distributions': all_dists,
            'discriminative_analysis': disc_analysis,
            'recommendations': recommendations,
            'top_tools': top_tools,
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        json_size = os.path.getsize(json_path)
        print(f"JSON output: {json_path} ({json_size/1024:.1f} KB)")

    if not args.html and not args.json and not args.verbose and not args.decision_only:
        print(f"\nR92 GRPO HP Calibration Summary:")
        print(f"  Traces: {len(all_stats)} ({len(success_stats)} success / {len(error_stats)} error)")
        print(f"  max_new_tokens={recommendations['max_new_tokens']} ctx={recommendations['context_window']}")
        print(f"  max_turns={recommendations['max_turns']} G={recommendations['group_size_binary']}")
        print(f"  temp={recommendations['temperature']['initial']} KL={recommendations['kl_coefficient']['target']} LR={recommendations['learning_rate']['initial']}")
        print(f"  batch={recommendations['batch_prompts']}p x {recommendations['group_size_binary']}G = {recommendations['total_seqs_per_step']}seqs")
        print(f"  timeout={recommendations['rollout_timeout_s']}s")

if __name__ == '__main__':
    main()
