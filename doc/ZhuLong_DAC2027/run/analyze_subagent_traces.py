#!/usr/bin/env python3
"""analyze_subagent_traces.py — A0/A1/A2 trace analysis for report.

Extracts per-task: spawn count, verdict (PASS/FAIL), adoption (code edit after verdict),
wall_sec, n_msgs, finishReason, peak context tokens, compaction triggers.
Outputs JSON summary for the HTML report.
"""
import json, os, glob, re, sys
from collections import Counter, defaultdict
from pathlib import Path

RUN_DIR = Path("/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run")
TRACE_BASE = Path("/tmp/zhulong_subagent_trace")

def load_msgs(filepath):
    try:
        d = json.load(open(filepath))
        return d.get('messages', []) if isinstance(d, dict) else d
    except Exception:
        return []

def extract_tool_calls(msgs):
    """Extract tool_use calls from assistant messages."""
    calls = []
    for m in msgs:
        if m.get('role') != 'assistant':
            continue
        for c in m.get('content', []):
            if isinstance(c, dict) and c.get('type') == 'tool_use':
                calls.append({
                    'name': c.get('name', '?'),
                    'input': c.get('input', {}),
                })
    return calls

def extract_tool_results(msgs):
    """Extract tool_result contents from user messages."""
    results = []
    for m in msgs:
        if m.get('role') != 'user':
            continue
        for c in m.get('content', []):
            if isinstance(c, dict) and c.get('type') == 'tool_result':
                results.append(c.get('content', ''))
    return results

def extract_finish_and_usage(msgs):
    """Extract finishReason and token usage from last assistant message metrics."""
    last_metrics = {}
    last_model = ''
    for m in msgs:
        if m.get('role') == 'assistant':
            if 'metrics' in m:
                last_metrics = m['metrics']
            if 'modelInfo' in m:
                last_model = m['modelInfo'].get('id', '')
    return last_metrics, last_model

def get_peak_context(msgs):
    """Estimate peak context from cumulative inputTokens."""
    peak = 0
    for m in msgs:
        if m.get('role') == 'assistant' and 'metrics' in m:
            it = m['metrics'].get('inputTokens', 0)
            if it > peak:
                peak = it
    return peak

def count_compaction_triggers(msgs):
    """Count compaction-related messages (look for compaction indicators)."""
    n = 0
    for m in msgs:
        s = json.dumps(m, ensure_ascii=False).lower()
        if 'compact' in s and ('history' in s or 'summar' in s or 'truncat' in s):
            n += 1
    return n

def analyze_task_trace(task_dir):
    """Analyze a single task's trace directory."""
    ws = task_dir / 'ws'
    if not ws.exists():
        return None
    sessions_dir = ws / 'sessions'
    if not sessions_dir.exists():
        return None
    sess_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
    if not sess_dirs:
        return None

    # Main session = the non-agent_ directory
    main_sess = None
    sub_sessions = []
    for sd in sess_dirs:
        name = sd.name
        if name.startswith('agent_'):
            sub_sessions.append(sd)
        else:
            main_sess = sd

    result = {
        'task': task_dir.name,
        'has_main': main_sess is not None,
        'n_sub_sessions': len(sub_sessions),
    }

    if main_sess:
        main_msgs_file = None
        for f in main_sess.iterdir():
            if f.name.endswith('.messages.json') and not f.name.startswith('agent_'):
                main_msgs_file = f
                break
        if main_msgs_file:
            msgs = load_msgs(main_msgs_file)
            result['main_n_msgs'] = len(msgs)
            result['main_peak_ctx'] = get_peak_context(msgs)
            result['main_compaction_triggers'] = count_compaction_triggers(msgs)
            metrics, model = extract_finish_and_usage(msgs)
            result['main_last_inputTokens'] = metrics.get('inputTokens', 0)
            result['main_last_outputTokens'] = metrics.get('outputTokens', 0)
            result['main_model'] = model

            # Extract tool calls
            calls = extract_tool_calls(msgs)
            tool_names = [c['name'] for c in calls]
            result['main_tool_hist'] = dict(Counter(tool_names))
            result['main_n_spawn'] = sum(1 for n in tool_names if 'spawn' in n.lower())
            result['main_n_editor'] = sum(1 for n in tool_names if n == 'editor')
            result['main_n_run_code'] = sum(1 for n in tool_names if 'run_code' in n or 'run_pyAether' in n)

            # Find spawn_agent calls and their results (verdicts)
            spawn_results = []
            calls_with_idx = []
            for i, m in enumerate(msgs):
                if m.get('role') == 'assistant':
                    for c in m.get('content', []):
                        if isinstance(c, dict) and c.get('type') == 'tool_use' and 'spawn' in c.get('name', '').lower():
                            calls_with_idx.append((i, c.get('input', {})))
            result['main_spawn_call_count'] = len(calls_with_idx)

            # Find the tool_results that follow spawn calls (verdicts)
            results_list = extract_tool_results(msgs)
            for r in results_list:
                r_str = str(r)
                if 'VERDICT' in r_str or 'verdict' in r_str.lower()[:500]:
                    # Extract PASS/FAIL
                    verdict = 'UNKNOWN'
                    if re.search(r'VERDICT\s*:\s*FAIL', r_str, re.I) or re.search(r'\bFAIL\b', r_str[:200]):
                        verdict = 'FAIL'
                    elif re.search(r'VERDICT\s*:\s*PASS', r_str, re.I) or re.search(r'\bPASS\b', r_str[:200]):
                        verdict = 'PASS'
                    spawn_results.append({
                        'verdict': verdict,
                        'snippet': r_str[:500],
                    })
            result['verdicts'] = spawn_results

            # Adoption analysis: did the main agent edit code AFTER the first spawn_result?
            # Find index of first tool_result containing verdict
            first_verdict_idx = None
            for i, m in enumerate(msgs):
                if m.get('role') == 'user':
                    for c in m.get('content', []):
                        if isinstance(c, dict) and c.get('type') == 'tool_result':
                            r_str = str(c.get('content', ''))
                            if 'VERDICT' in r_str or 'verdict' in r_str.lower()[:500]:
                                first_verdict_idx = i
                                break
                    if first_verdict_idx is not None:
                        break
            # Count editor/run_code calls AFTER first_verdict_idx
            edits_after = 0
            runs_after = 0
            if first_verdict_idx is not None:
                for m in msgs[first_verdict_idx + 1:]:
                    if m.get('role') == 'assistant':
                        for c in m.get('content', []):
                            if isinstance(c, dict) and c.get('type') == 'tool_use':
                                nm = c.get('name', '')
                                if nm == 'editor':
                                    edits_after += 1
                                if 'run_code' in nm or 'run_pyAether' in nm:
                                    runs_after += 1
            result['edits_after_verdict'] = edits_after
            result['runs_after_verdict'] = runs_after
            result['adopted'] = (edits_after > 0 or runs_after > 0)

    # Sub-agent sessions: token + tool analysis
    sub_tok_in = 0
    sub_tok_out = 0
    sub_n_msgs_total = 0
    sub_tools = Counter()
    sub_finish_reasons = Counter()
    for sd in sub_sessions:
        for f in sd.iterdir():
            if f.name.endswith('.messages.json'):
                sm = load_msgs(f)
                sub_n_msgs_total += len(sm)
                for m in sm:
                    if m.get('role') == 'assistant' and 'metrics' in m:
                        sub_tok_in += m['metrics'].get('inputTokens', 0)
                        sub_tok_out += m['metrics'].get('outputTokens', 0)
                calls = extract_tool_calls(sm)
                for c in calls:
                    sub_tools[c['name']] += 1
    result['sub_n_msgs_total'] = sub_n_msgs_total
    result['sub_tok_in'] = sub_tok_in
    result['sub_tok_out'] = sub_tok_out
    result['sub_tool_hist'] = dict(sub_tools)

    return result


def analyze_arm(arm, batch_dirs):
    """Analyze all tasks across batch dirs for an arm."""
    all_tasks = {}
    for bd in batch_dirs:
        if not bd.exists():
            continue
        for task_dir in sorted(bd.iterdir()):
            if task_dir.is_dir() and task_dir.name.startswith('EDA-Eval-PyAether-'):
                r = analyze_task_trace(task_dir)
                if r:
                    all_tasks[f"{bd.name}/{task_dir.name}"] = r
    return all_tasks


def main():
    output = {
        'analysis': 'ZhuLong subagent A0/A1/A2 trace analysis',
        'date': '2026-11-15',
    }

    # A1 batches (3 rounds)
    a1_batches = [
        TRACE_BASE / 'A1' / '2026_1114_130945',
        TRACE_BASE / 'A1' / '2026_1114_152932',
        TRACE_BASE / 'A1' / '2026_1114_180019',
    ]
    # A2 batches (3 rounds) — skip the smoke 2026_1114_202023
    a2_batches = [
        TRACE_BASE / 'A2' / '2026_1114_210739',
        TRACE_BASE / 'A2' / '2026_1114_234310',
        TRACE_BASE / 'A2' / '2026_1115_021900',
    ]

    print("Analyzing A1 traces...", file=sys.stderr)
    a1_tasks = analyze_arm('A1', a1_batches)
    print(f"  A1: {len(a1_tasks)} task-traces", file=sys.stderr)

    print("Analyzing A2 traces...", file=sys.stderr)
    a2_tasks = analyze_arm('A2', a2_batches)
    print(f"  A2: {len(a2_tasks)} task-traces", file=sys.stderr)

    # Aggregate A2 adoption analysis
    a2_verdict_tasks = defaultdict(list)  # task -> list of (round, verdict, adopted)
    for key, r in a2_tasks.items():
        batch, task = key.split('/', 1)
        verdicts = r.get('verdicts', [])
        verdict = verdicts[0]['verdict'] if verdicts else 'NO_SPAWN'
        a2_verdict_tasks[task].append({
            'batch': batch,
            'verdict': verdict,
            'adopted': r.get('adopted', False),
            'edits_after': r.get('edits_after_verdict', 0),
            'runs_after': r.get('runs_after_verdict', 0),
            'n_spawn': r.get('main_spawn_call_count', 0),
            'main_n_msgs': r.get('main_n_msgs', 0),
            'main_peak_ctx': r.get('main_peak_ctx', 0),
        })

    # Summarize verdict distribution
    verdict_counts = Counter()
    adopted_counts = Counter()
    for task, rounds in a2_verdict_tasks.items():
        for rd in rounds:
            verdict_counts[rd['verdict']] += 1
            adopted_counts[(rd['verdict'], rd['adopted'])] += 1

    # Aggregate per-round stats
    a2_per_round = defaultdict(lambda: {
        'n_tasks': 0, 'n_spawn': 0, 'n_verdicts': 0,
        'verdicts': Counter(), 'adopted': 0, 'total_edits_after': 0,
        'peak_ctxs': [], 'n_msgs': [],
    })
    for key, r in a2_tasks.items():
        batch, task = key.split('/', 1)
        rd = a2_per_round[batch]
        rd['n_tasks'] += 1
        rd['n_spawn'] += r.get('main_spawn_call_count', 0)
        verdicts = r.get('verdicts', [])
        rd['n_verdicts'] += len(verdicts)
        for v in verdicts:
            rd['verdicts'][v['verdict']] += 1
        if r.get('adopted', False):
            rd['adopted'] += 1
        rd['total_edits_after'] += r.get('edits_after_verdict', 0)
        rd['peak_ctxs'].append(r.get('main_peak_ctx', 0))
        rd['n_msgs'].append(r.get('main_n_msgs', 0))

    a1_per_round = defaultdict(lambda: {
        'n_tasks': 0, 'n_spawn': 0, 'peak_ctxs': [], 'n_msgs': [],
        'sub_tok_in': 0, 'sub_tok_out': 0, 'sub_n_msgs': 0,
        'main_tok_in': 0,
    })
    for key, r in a1_tasks.items():
        batch, task = key.split('/', 1)
        rd = a1_per_round[batch]
        rd['n_tasks'] += 1
        rd['n_spawn'] += r.get('main_spawn_call_count', 0)
        rd['peak_ctxs'].append(r.get('main_peak_ctx', 0))
        rd['n_msgs'].append(r.get('main_n_msgs', 0))
        rd['sub_tok_in'] += r.get('sub_tok_in', 0)
        rd['sub_tok_out'] += r.get('sub_tok_out', 0)
        rd['sub_n_msgs'] += r.get('sub_n_msgs_total', 0)
        rd['main_tok_in'] += r.get('main_last_inputTokens', 0)

    # A0 from compaction results (per-task pass + context)
    a0_data = {}
    try:
        comp = json.load(open(RUN_DIR / 'ablation_compaction_results.json'))
        for rnd in comp['rounds']:
            tag = rnd['summary']['tag']
            if 'basic' in tag:
                for t in rnd.get('tasks', []):
                    key = f"{tag}/{t['task']}"
                    a0_data[key] = {
                        'pass': t.get('pass', 0),
                        'wall_sec': t.get('wall_sec', 0),
                        'n_msgs': t.get('n_assistant_msgs', 0),
                        'prompt_tokens': t.get('prompt_tokens', 0),
                        'total_tokens': t.get('total_tokens', 0),
                    }
    except Exception as e:
        print(f"  A0 load error: {e}", file=sys.stderr)

    # Compute summary stats
    def mean(lst):
        lst = [x for x in lst if x is not None and x > 0]
        return sum(lst) / len(lst) if lst else 0

    output['A0'] = {
        'n_task_traces': len(a0_data),
        'per_round': {},
    }
    for tag in ['C_basic_r1', 'C_basic_r2', 'C_basic_r3']:
        tasks = {k: v for k, v in a0_data.items() if k.startswith(tag)}
        if tasks:
            output['A0']['per_round'][tag] = {
                'n_tasks': len(tasks),
                'pass_rate': sum(v['pass'] for v in tasks.values()) / len(tasks),
                'mean_wall_sec': mean([v['wall_sec'] for v in tasks.values()]),
                'mean_n_msgs': mean([v['n_msgs'] for v in tasks.values()]),
                'mean_prompt_tokens': mean([v['prompt_tokens'] for v in tasks.values()]),
                'mean_total_tokens': mean([v['total_tokens'] for v in tasks.values()]),
            }

    output['A1'] = {
        'n_task_traces': len(a1_tasks),
        'per_round': {},
    }
    for batch, rd in a1_per_round.items():
        output['A1']['per_round'][batch] = {
            'n_tasks': rd['n_tasks'],
            'total_spawn': rd['n_spawn'],
            'mean_spawn_per_task': rd['n_spawn'] / rd['n_tasks'] if rd['n_tasks'] else 0,
            'mean_peak_ctx': mean(rd['peak_ctxs']),
            'mean_n_msgs': mean(rd['n_msgs']),
            'sub_tok_in_total': rd['sub_tok_in'],
            'sub_tok_out_total': rd['sub_tok_out'],
            'sub_n_msgs_total': rd['sub_n_msgs'],
            'main_tok_in_total': rd['main_tok_in'],
        }

    output['A2'] = {
        'n_task_traces': len(a2_tasks),
        'per_round': {},
        'verdict_counts': dict(verdict_counts),
        'adopted_counts': {f"{k[0]}_adopted={k[1]}": v for k, v in adopted_counts.items()},
    }
    for batch, rd in a2_per_round.items():
        output['A2']['per_round'][batch] = {
            'n_tasks': rd['n_tasks'],
            'total_spawn': rd['n_spawn'],
            'mean_spawn_per_task': rd['n_spawn'] / rd['n_tasks'] if rd['n_tasks'] else 0,
            'n_verdicts': rd['n_verdicts'],
            'verdicts': dict(rd['verdicts']),
            'n_adopted': rd['adopted'],
            'adopt_rate': rd['adopted'] / rd['n_tasks'] if rd['n_tasks'] else 0,
            'total_edits_after': rd['total_edits_after'],
            'mean_peak_ctx': mean(rd['peak_ctxs']),
            'mean_n_msgs': mean(rd['n_msgs']),
        }

    # A2 per-task detail (for adoption vs pass correlation)
    output['A2_per_task'] = {}
    for task, rounds in sorted(a2_verdict_tasks.items()):
        output['A2_per_task'][task] = rounds

    # Save
    out_file = RUN_DIR / 'subagent_trace_analysis.json'
    json.dump(output, open(out_file, 'w'), ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_file}", file=sys.stderr)

    # Print summary
    print("\n=== SUMMARY ===", file=sys.stderr)
    print(f"A0 task-traces: {output['A0']['n_task_traces']}", file=sys.stderr)
    print(f"A1 task-traces: {output['A1']['n_task_traces']}", file=sys.stderr)
    print(f"A2 task-traces: {output['A2']['n_task_traces']}", file=sys.stderr)
    print(f"\nA2 verdict distribution: {output['A2']['verdict_counts']}", file=sys.stderr)
    print(f"A2 adopted counts: {output['A2']['adopted_counts']}", file=sys.stderr)
    for batch, rd in output['A2']['per_round'].items():
        print(f"  {batch}: verdicts={rd['verdicts']} adopted={rd['n_adopted']}/{rd['n_tasks']} mean_peak_ctx={rd['mean_peak_ctx']:.0f} mean_n_msgs={rd['mean_n_msgs']:.0f}", file=sys.stderr)


if __name__ == '__main__':
    main()
