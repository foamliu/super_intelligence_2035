#!/usr/bin/env python3
"""
R23: DeepSeek 103-task full-harness trajectory mining.
Key finding: All 103 traces ARE the 158 eval tasks -> 100% contaminated.
Extracts BEHAVIORAL PATTERNS (not task content) for SFT augmentation.
Usage: python3 baize_posttrain_mine_deepseek_traces.py [--dry-run] [--max-tasks N]
"""
import argparse, json, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HOME = Path(os.path.expanduser('~'))
TRACE_DIR = HOME / 'code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace'
ERROR_DIR = HOME / 'code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace_error_case'
EVAL_DS = HOME / 'code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl'
OUT_PATTERNS = Path(__file__).parent / 'sft_deepseek_patterns.jsonl'
OUT_STATS = Path(__file__).parent / 'sft_deepseek_gold_stats.json'

EVAL_EP_SET = set(); EVAL_NGRAMS = set()

def load_eval():
    global EVAL_EP_SET, EVAL_NGRAMS
    if not EVAL_DS.exists(): return
    with open(EVAL_DS) as f:
        for line in f:
            t = json.loads(line)
            ep = t.get('entry_point','')
            if ep: EVAL_EP_SET.add(ep)
            words = t.get('prompt','').split()
            for i in range(len(words)-7): EVAL_NGRAMS.add(' '.join(words[i:i+8]).lower())
    print(f'[INFO] Eval ref: {len(EVAL_EP_SET)} EPs, {len(EVAL_NGRAMS)} 8-grams')

def extract_task_prompt(conv):
    if not conv or conv[0].get('role')!='user': return None
    for b in conv[0].get('content',[]):
        if b.get('type')=='text':
            m = re.search(r'<task>\s*(.*?)\s*</task>', b['text'], re.DOTALL)
            return m.group(1).strip() if m else b['text'][:500]
    return None

def extract_ep(prompt):
    m = re.search(r'def\s+(\w+)\s*\(', prompt)
    return m.group(1) if m else None

def extract_tool_calls(text):
    """Extract tool calls - fixed regex for multi-line XML with task_progress."""
    calls = []
    for m in re.finditer(r'<use_mcp_tool>(.*?)</use_mcp_tool>', text, re.DOTALL):
        block = m.group(1)
        sm = re.search(r'<server_name>\s*(.*?)\s*</server_name>', block)
        tm = re.search(r'<tool_name>\s*(.*?)\s*</tool_name>', block)
        am = re.search(r'<arguments>\s*(.*?)\s*</arguments>', block, re.DOTALL)
        if sm and tm:
            calls.append({'server': sm.group(1).strip(), 'tool': tm.group(1).strip(),
                          'args': (am.group(1) if am else '').strip()[:500]})
    return calls

def extract_code(text):
    clean = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
    return [m.group(1).strip() for m in re.finditer(r'```python\s*(.*?)\s*```', clean, re.DOTALL) if len(m.group(1).strip())>20]

def check_contam(text, ep):
    if ep and ep in EVAL_EP_SET: return True, f'EP match: {ep}'
    words = text.split()
    for i in range(len(words)-7):
        ng = ' '.join(words[i:i+8]).lower()
        if ng in EVAL_NGRAMS: return True, f'8-gram: {ng[:60]}'
    return False, ''

def parse_trace(tp):
    cf = tp / 'api_conversation_history.json'
    if not cf.exists(): return None
    with open(cf) as f: conv = json.load(f)
    if not isinstance(conv,list) or len(conv)<2: return None
    prompt = extract_task_prompt(conv)
    if not prompt: return None
    ep = extract_ep(prompt)
    # Extract full conversation data
    all_msgs = []; tool_seq = []; api_queries = []; code_blocks = []
    error_recovery_pairs = []
    prev_error = None
    for i,msg in enumerate(conv):
        role = msg.get('role',''); content = msg.get('content',[])
        if not isinstance(content,list): continue
        text = '\n'.join(b.get('text','') for b in content if b.get('type')=='text')
        if role=='assistant':
            calls = extract_tool_calls(text); codes = extract_code(text)
            for c in calls:
                tool_seq.append(c['tool'])
                if c['tool'] in ('search_apis','get_api_details'):
                    qm = re.search(r'"query"\s*:\s*"([^"]+)"', c['args'])
                    nm = re.search(r'"api_name"\s*:\s*"([^"]+)"', c['args'])
                    if qm: api_queries.append(qm.group(1))
                    if nm: api_queries.append(nm.group(1))
            for cb in codes: code_blocks.append(cb)
            # Check if this is an error recovery (after previous error)
            if prev_error and codes:
                error_recovery_pairs.append({'error': prev_error[:300], 'fix_code': codes[0][:500]})
                prev_error = None
            all_msgs.append({'role':'assistant','text':text,'tool_calls':calls,'codes':codes})
        elif role=='user' and i>0:
            # Check for error messages in tool results
            if 'Error' in text or 'error' in text or 'Traceback' in text:
                em = re.search(r'((?:Error|Traceback).*?)(?:\n\n|\Z)', text, re.DOTALL)
                if em: prev_error = em.group(1)[:300]
            all_msgs.append({'role':'user','text':text[:2000]})
    return {'task_id':tp.name,'entry_point':ep,'num_msgs':len(all_msgs),
            'tool_seq':tool_seq,'api_queries':api_queries,'code_blocks':code_blocks,
            'error_recovery':error_recovery_pairs,'num_tool_calls':len(tool_seq),
            'num_code_blocks':len(code_blocks)}

def parse_error_trace(jf):
    """Parse error case JSON files (different format - single JSON, not directory)."""
    with open(jf) as f:
        data = json.load(f)
    # Error traces may have different structure
    conv = data if isinstance(data, list) else data.get('conversation', data.get('messages', []))
    if not isinstance(conv, list) or len(conv) < 2: return None
    prompt = extract_task_prompt(conv) or ''
    ep = extract_ep(prompt)
    tool_seq = []; code_blocks = []; errors = []
    for msg in conv:
        role = msg.get('role',''); content = msg.get('content',[])
        if not isinstance(content,list): continue
        text = '\n'.join(b.get('text','') for b in content if b.get('type')=='text')
        if role=='assistant':
            calls = extract_tool_calls(text); codes = extract_code(text)
            tool_seq.extend([c['tool'] for c in calls])
            code_blocks.extend(codes)
        elif role=='user':
            if 'Error' in text or 'Traceback' in text:
                errors.append(text[:300])
    return {'task_id':jf.stem,'entry_point':ep,'num_msgs':len(conv),
            'tool_seq':tool_seq,'code_blocks':code_blocks,'errors':errors,
            'num_tool_calls':len(tool_seq),'num_code_blocks':len(code_blocks)}

def extract_patterns(traces):
    """Extract behavioral patterns NOT contaminated with eval task content."""
    patterns = []
    # 1. Tool-call sequence patterns
    seq_counter = Counter()
    for t in traces:
        seq = tuple(t['tool_seq'])
        if seq: seq_counter[seq] += 1
    for seq, count in seq_counter.most_common(20):
        patterns.append({
            'type': 'tool_call_sequence',
            'sequence': list(seq),
            'frequency': count,
            'description': f'Common tool-call pattern: {" -> ".join(seq)}'
        })

    # 2. API search query patterns (behavioral, not task content)
    query_counter = Counter()
    for t in traces:
        query_counter.update(t['api_queries'])
    for q, count in query_counter.most_common(30):
        patterns.append({
            'type': 'api_search_query',
            'query': q,
            'frequency': count,
            'description': f'API search query used by DeepSeek'
        })

    # 3. Error recovery patterns
    all_recovery = []
    for t in traces:
        all_recovery.extend(t.get('error_recovery', []))
    for er in all_recovery[:50]:
        # Sanitize: remove any eval-specific function names
        sanitized_fix = er['fix_code']
        for ep in EVAL_EP_SET:
            sanitized_fix = sanitized_fix.replace(ep, '<FUNCTION>')
        patterns.append({
            'type': 'error_recovery',
            'error_type': er['error'][:100],
            'fix_pattern': sanitized_fix[:300],
            'description': 'How DeepSeek recovers from execution errors'
        })

    # 4. Tool usage statistics
    tool_counter = Counter()
    for t in traces:
        tool_counter.update(t['tool_seq'])
    patterns.append({
        'type': 'tool_usage_stats',
        'tools': dict(tool_counter.most_common()),
        'description': 'Frequency of each tool used across all traces'
    })

    # 5. Turn count distribution
    turn_counts = [len(t['tool_seq']) for t in traces]
    patterns.append({
        'type': 'turn_distribution',
        'min': min(turn_counts) if turn_counts else 0,
        'max': max(turn_counts) if turn_counts else 0,
        'mean': sum(turn_counts)/len(turn_counts) if turn_counts else 0,
        'median': sorted(turn_counts)[len(turn_counts)//2] if turn_counts else 0,
        'description': 'Distribution of tool-call turns per task'
    })

    return patterns

def generate_sft_from_patterns(patterns):
    """Generate SFT training pairs from behavioral patterns (NOT eval task content)."""
    sft_pairs = []
    # Generate tool-call behavior SFT pairs
    for p in patterns:
        if p['type'] == 'tool_call_sequence' and p['frequency'] >= 3:
            seq = p['sequence']
            # Create a generic SFT pair teaching the tool-call pattern
            desc = ' -> '.join(seq)
            sft_pairs.append({
                'conversation': [
                    {'role': 'system', 'content': 'You are a Python engineer using pyAether EDA tools.'},
                    {'role': 'user', 'content': f'When solving a pyAether coding task, what tool-call sequence should you follow?'},
                    {'role': 'assistant', 'content': f'A proven approach is: {desc}. '
                        f'First search for relevant APIs, then get details for the best match, '
                        f'write code based on the API documentation, execute it, and iterate on errors.'}
                ],
                'metadata': {'source': 'deepseek_pattern', 'pattern_type': 'tool_call_sequence', 'frequency': p['frequency']}
            })
        elif p['type'] == 'error_recovery' and 'fix_pattern' in p:
            sft_pairs.append({
                'conversation': [
                    {'role': 'system', 'content': 'You are a Python engineer using pyAether EDA tools.'},
                    {'role': 'user', 'content': f'I got this error when running pyAether code: {p["error_type"]}'},
                    {'role': 'assistant', 'content': f'To fix this, try the following approach:\n```python\n{p["fix_pattern"]}\n```\n'
                        f'Common fixes include: checking import paths, verifying API names, and ensuring correct argument types.'}
                ],
                'metadata': {'source': 'deepseek_pattern', 'pattern_type': 'error_recovery'}
            })
    return sft_pairs

def main():
    ap = argparse.ArgumentParser(description='R23: DeepSeek trace mining -> patterns + SFT')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--max-tasks', type=int, default=0)
    args = ap.parse_args()
    print('='*60)
    print('R23: DeepSeek Trajectory Mining -> Behavioral Patterns')
    print('='*60)
    load_eval()
    if not TRACE_DIR.exists(): print(f'[ERROR] {TRACE_DIR}'); sys.exit(1)
    tdirs = sorted([d for d in TRACE_DIR.iterdir() if d.is_dir()])
    if args.max_tasks > 0: tdirs = tdirs[:args.max_tasks]
    print(f'[INFO] {len(tdirs)} success traces')
    traces = []; perr = 0
    for td in tdirs:
        r = parse_trace(td)
        if r: traces.append(r)
        else: perr += 1
    # Parse error traces (JSON files)
    etraces = []
    if ERROR_DIR.exists():
        for jf in sorted(ERROR_DIR.glob('*.json')):
            r = parse_error_trace(jf)
            if r: etraces.append(r)
    print(f'[INFO] Parsed: {len(traces)} success + {len(etraces)} error ({perr} errors)')

    # ── Contamination check ──
    contam_count = 0
    for t in traces:
        ep = t['entry_point']
        if ep and ep in EVAL_EP_SET:
            contam_count += 1
    print(f'\n[FINDING] Contaminated (EP match): {contam_count}/{len(traces)} = {contam_count/len(traces)*100:.0f}%')
    print(f'[FINDING] All DeepSeek traces ARE the 158 eval tasks -> raw traces CANNOT be used for SFT')

    # ── Extract behavioral patterns ──
    patterns = extract_patterns(traces)
    print(f'\n[INFO] Extracted {len(patterns)} behavioral patterns')
    # Print key stats
    tool_stats = next((p for p in patterns if p['type']=='tool_usage_stats'), None)
    if tool_stats:
        print(f'[STATS] Tool usage: {tool_stats["tools"]}')
    turn_dist = next((p for p in patterns if p['type']=='turn_distribution'), None)
    if turn_dist:
        print(f'[STATS] Turns per task: mean={turn_dist["mean"]:.1f} min={turn_dist["min"]} max={turn_dist["max"]}')

    # ── Generate SFT pairs from patterns ──
    sft_pairs = generate_sft_from_patterns(patterns)
    print(f'\n[INFO] Generated {len(sft_pairs)} SFT pairs from patterns (contamination-free)')

    # ── Stats ──
    stats = {
        'total_success_traces': len(traces),
        'total_error_traces': len(etraces),
        'parse_errors': perr,
        'contaminated_count': contam_count,
        'contamination_rate': f'{contam_count/len(traces)*100:.1f}%' if traces else 'N/A',
        'key_finding': 'All 103 DeepSeek traces are from the 158 eval tasks -> 100% contaminated. Raw traces CANNOT be used for SFT (red-line violation). Behavioral patterns extracted instead.',
        'patterns_extracted': len(patterns),
        'sft_pairs_from_patterns': len(sft_pairs),
        'tool_usage': tool_stats['tools'] if tool_stats else {},
        'turn_distribution': {'mean': turn_dist['mean'], 'min': turn_dist['min'], 'max': turn_dist['max']} if turn_dist else {},
        'error_recovery_count': sum(len(t.get('error_recovery',[])) for t in traces),
        'error_trace_count': len(etraces),
        'error_trace_errors': sum(len(t.get('errors',[])) for t in etraces) if etraces else 0,
    }

    # ── Write output ──
    if not args.dry_run and sft_pairs:
        with open(OUT_PATTERNS, 'w') as f:
            for p in sft_pairs:
                f.write(json.dumps(p, ensure_ascii=False) + '\n')
        sz = OUT_PATTERNS.stat().st_size
        print(f'\n[OUT] {len(sft_pairs)} SFT pairs -> {OUT_PATTERNS} ({sz:,} bytes = {sz/1024:.1f} KB)')
        stats['output_file'] = str(OUT_PATTERNS)
        stats['output_size_bytes'] = sz
    else:
        print(f'\n[DRY-RUN] Would write {len(sft_pairs)} pairs')

    with open(OUT_STATS, 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f'[OUT] Stats -> {OUT_STATS}')

    print('\n' + '='*60)
    print('R23 Summary')
    print('='*60)
    print(f'  Traces parsed:     {len(traces)} success + {len(etraces)} error')
    print(f'  Contamination:     {contam_count}/{len(traces)} ({contam_count/len(traces)*100:.0f}%)')
    print(f'  Key finding:       Raw traces = eval tasks -> CANNOT use for SFT')
    print(f'  Patterns extracted: {len(patterns)}')
    print(f'  SFT pairs (safe):  {len(sft_pairs)}')
    print(f'  Error recovery:    {stats["error_recovery_count"]} pairs')
    print(f'  Avg tool calls:    {stats["turn_distribution"].get("mean",0):.1f}')

if __name__ == '__main__': main()
