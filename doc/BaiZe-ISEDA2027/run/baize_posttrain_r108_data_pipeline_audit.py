#!/usr/bin/env python3
"""R108: Comprehensive SFT/RL Data Pipeline End-to-End Audit (Zero GPU)"""
import argparse, json, os, sys, statistics, re
from pathlib import Path
from collections import Counter

RUN_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run")
REPORTS_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
EVAL_DATASET = Path("/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
SFT_FILES = [
    RUN_DIR / "sft_pyaether_corpus.parquet",
    RUN_DIR / "sft_pyaether_corpus_v2.parquet",
    RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.parquet",
]
RL_FILE = RUN_DIR / "rl_pyaether_synth_v2.parquet"
YAML_FILES = [
    RUN_DIR / "baize_posttrain_rl_verl_config_v2.yaml",
    RUN_DIR / "baize_posttrain_tool_config.yaml",
    RUN_DIR / "baize_posttrain_eda_tools.yaml",
]
MODEL_PATH = Path("/nas_data/app.e0031982/models/MiniCPM5-2B")

def load_parquet(path):
    try:
        import pandas as pd
        return pd.read_parquet(str(path)), None
    except Exception as e:
        return None, str(e)

def load_jsonl(path):
    items = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
    except Exception as e:
        return [], str(e)
    return items, None

def messages_to_text(messages):
    if isinstance(messages, str):
        return messages
    if isinstance(messages, list):
        parts = []
        for msg in messages:
            if isinstance(msg, dict):
                parts.append(msg.get('content', ''))
            elif isinstance(msg, str):
                parts.append(msg)
        return '\n'.join(str(p) for p in parts)
    return str(messages)

def estimate_tokens(text):
    if text is None:
        return 0
    return max(1, len(str(text)) // 4)

def extract_apis_from_text(text):
    return set(f"pyAether.{a}" for a in re.findall(r'pyAether\.(\w+)', str(text)))

def run_audit(smoke=False):
    import pandas as pd
    results = {'title': 'R108: SFT/RL Data Pipeline Audit', 'timestamp': '2026-11-09',
               'sections': [], 'verdict': None, 'issues': [], 'stats': {}}

    # 1. Parquet inventory
    sec1 = {'title': '1. Parquet File Inventory', 'items': []}
    for pq in SFT_FILES + [RL_FILE]:
        info = {'path': pq.name, 'exists': pq.exists()}
        if pq.exists():
            info['size_mb'] = round(pq.stat().st_size / 1048576, 2)
            df, err = load_parquet(pq)
            if err:
                info['error'] = err
                results['issues'].append(f"Load failed: {pq.name}")
            else:
                info['rows'] = len(df)
                info['columns'] = df.columns.tolist()
                nulls = df.isnull().sum()
                info['null_counts'] = {k: int(v) for k, v in nulls.to_dict().items() if v > 0}
        else:
            info['error'] = 'NOT FOUND'
            results['issues'].append(f"Missing: {pq.name}")
        sec1['items'].append(info)
    results['sections'].append(sec1)

    # 2. RL format validation
    sec2 = {'title': '2. RL Data Format Validation', 'items': []}
    rl_df, rl_err = load_parquet(RL_FILE)
    if rl_err:
        sec2['items'].append({'error': rl_err})
        results['issues'].append(f'RL load: {rl_err}')
    else:
        for col in ['prompt', 'data_source']:
            ok = col in rl_df.columns
            sec2['items'].append({'check': f'Column "{col}"', 'pass': ok})
            if not ok:
                results['issues'].append(f'RL missing: {col}')
        if 'prompt' in rl_df.columns:
            s0 = rl_df['prompt'].iloc[0]
            sec2['items'].append({'check': 'prompt is list', 'pass': isinstance(s0, list)})
        if 'data_source' in rl_df.columns:
            ds = rl_df['data_source'].value_counts().to_dict()
            sec2['items'].append({'check': 'data_source', 'pass': len(ds) > 0,
                                  'detail': {str(k): int(v) for k, v in ds.items()}})
        texts = [messages_to_text(m) for m in rl_df['prompt'].dropna()]
        toks = [estimate_tokens(t) for t in texts]
        sec2['items'].append({'check': 'Prompt token stats', 'pass': True, 'detail': {
            'count': len(toks), 'mean': round(statistics.mean(toks), 1) if toks else 0,
            'median': int(statistics.median(toks)) if toks else 0,
            'max': max(toks) if toks else 0,
            'over_8192': sum(1 for t in toks if t > 8192)}})
        diffs = []
        for m in rl_df.get('metadata', pd.Series(dtype=object)).dropna():
            if isinstance(m, str):
                try:
                    m = json.loads(m)
                except Exception:
                    continue
            if isinstance(m, dict):
                diffs.append(m.get('difficulty', 'unknown'))
        sec2['items'].append({'check': 'Difficulty dist', 'pass': True, 'detail': dict(Counter(diffs))})
    results['sections'].append(sec2)

    # 3. SFT format validation
    sec3 = {'title': '3. SFT Data Format Validation', 'items': []}
    sft_total = 0
    for sft_file in SFT_FILES:
        if not sft_file.exists():
            continue
        df, err = load_parquet(sft_file)
        if err:
            sec3['items'].append({'file': sft_file.name, 'error': err})
            continue
        sft_total += len(df)
        item = {'file': sft_file.name, 'rows': len(df), 'columns': df.columns.tolist()}
        msg_cols = [c for c in df.columns if c in ('messages', 'conversation', 'prompt', 'text')]
        item['msg_cols'] = msg_cols
        if msg_cols:
            s0 = df[msg_cols[0]].iloc[0]
            if isinstance(s0, list):
                item['format'] = 'chat_messages'
                if s0 and isinstance(s0[0], dict):
                    item['roles'] = list(set(m.get('role', '?') for m in s0 if isinstance(m, dict)))
            else:
                item['format'] = str(type(s0).__name__)
        sec3['items'].append(item)
    results['sections'].append(sec3)

    # 4. Contamination check
    sec4 = {'title': '4. Contamination Isolation Check (RED LINE)', 'items': []}
    eval_tasks, eval_err = load_jsonl(EVAL_DATASET)
    if eval_err or not eval_tasks:
        sec4['items'].append({'error': f'Eval dataset: {eval_err or "empty"}'})
        results['issues'].append('Contamination check: eval dataset not loadable')
    else:
        sec4['items'].append({'eval_tasks': len(eval_tasks)})
        eval_apis = set()
        eval_prompts = set()
        for t in eval_tasks:
            for field in ['prompt', 'test_code', 'assertion']:
                text = t.get(field, '') or ''
                if isinstance(text, str):
                    eval_apis.update(extract_apis_from_text(text))
            p = t.get('prompt', '')
            if isinstance(p, str) and len(p) > 50:
                eval_prompts.add(p[:200].strip().lower())
        sec4['items'].append({'eval_api_names': len(eval_apis), 'sample': sorted(list(eval_apis))[:15]})
        if rl_df is not None:
            rl_apis = set()
            for col in rl_df.columns:
                if rl_df[col].dtype == 'object':
                    for val in rl_df[col].dropna():
                        rl_apis.update(extract_apis_from_text(val))
            overlap = eval_apis & rl_apis
            sec4['items'].append({'rl_apis': len(rl_apis), 'api_overlap': len(overlap),
                                  'note': 'API overlap expected (same library)'})
        contam_hits = 0
        if rl_df is not None and 'prompt' in rl_df.columns:
            for msg in rl_df['prompt'].dropna():
                text = messages_to_text(msg).lower()
                for ep in eval_prompts:
                    if ep in text:
                        contam_hits += 1
                        break
        sec4['items'].append({'eval_fingerprints': len(eval_prompts),
                              'verbatim_contamination': contam_hits,
                              'verdict': 'PASS' if contam_hits == 0 else 'FAIL'})
        if contam_hits > 0:
            results['issues'].append(f'CONTAMINATION: {contam_hits} rows')
    results['sections'].append(sec4)

    # 5. YAML config validation
    sec5 = {'title': '5. YAML Config Path Validation', 'items': []}
    for yf in YAML_FILES:
        item = {'file': yf.name, 'exists': yf.exists()}
        if yf.exists():
            content = yf.read_text()
            paths = re.findall(r'(?:path|train_files|val_files|tokenizer|api_database):\s*([^\n]+)', content)
            item['referenced_paths'] = len(paths)
            path_checks = []
            for p in paths[:10]:
                p = p.strip().strip('"').strip("'")
                full = os.path.expanduser(p)
                exists = os.path.exists(full) or p.startswith('baize_posttrain_')
                path_checks.append({'path': p, 'exists': exists})
                if not exists and '/' in p:
                    results['issues'].append(f'YAML path missing: {p}')
            item['path_checks'] = path_checks
        sec5['items'].append(item)
    results['sections'].append(sec5)

    # 6. Model path check
    sec6 = {'title': '6. Model & Tokenizer Check', 'items': []}
    item = {'path': str(MODEL_PATH), 'exists': MODEL_PATH.exists()}
    if MODEL_PATH.exists():
        files = list(MODEL_PATH.iterdir())
        item['files'] = [f.name for f in files]
        item['has_safetensors'] = any(f.suffix == '.safetensors' for f in files)
        item['has_config'] = (MODEL_PATH / 'config.json').exists()
        item['has_tokenizer'] = (MODEL_PATH / 'tokenizer.json').exists() or (MODEL_PATH / 'tokenizer_config.json').exists()
    sec6['items'].append(item)
    results['sections'].append(sec6)

    # 7. Summary stats
    sec7 = {'title': '7. Summary Statistics', 'items': []}
    stats = {'rl_total_tasks': len(rl_df) if rl_df is not None else 0,
             'sft_total_all_versions': sft_total,
             'eval_total_tasks': len(eval_tasks) if eval_tasks else 0}
    sec7['items'].append(stats)
    results['stats'] = stats
    results['sections'].append(sec7)

    # 8. Verdict
    sec8 = {'title': '8. Launch Readiness Verdict', 'items': []}
    ic = len(results['issues'])
    verdict = 'READY' if ic == 0 else (f'CONDITIONAL ({ic} issues)' if ic <= 2 else f'NOT READY ({ic} issues)')
    sec8['items'].append({'verdict': verdict, 'issues': results['issues']})
    results['verdict'] = verdict
    results['sections'].append(sec8)
    return results

def generate_html(results):
    s = results.get('stats', {})
    vclass = 'verdict-ready' if results['verdict'] == 'READY' else 'verdict-conditional'
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R108: SFT/RL 数据管线审计</title>
<style>
body {{ font-family: sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
h2 {{ color: #16213e; margin-top: 30px; border-left: 4px solid #e94560; padding-left: 10px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #16213e; color: white; }}
tr:nth-child(even) {{ background: #f2f2f2; }}
.pass {{ color: #27ae60; font-weight: bold; }}
.fail {{ color: #e74c3c; font-weight: bold; }}
.warn {{ color: #f39c12; }}
pre {{ background: #1e1e2e; color: #cdd6f4; padding: 15px; border-radius: 8px; overflow-x: auto; }}
.verdict-box {{ padding: 20px; border-radius: 10px; margin: 20px 0; font-size: 1.2em; }}
.verdict-ready {{ background: #d4edda; border: 2px solid #27ae60; }}
.verdict-conditional {{ background: #fff3cd; border: 2px solid #f39c12; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }}
.stat-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
.stat-value {{ font-size: 2em; font-weight: bold; color: #e94560; }}
.stat-label {{ color: #666; font-size: 0.9em; }}
</style></head><body>
<h1>R108: SFT/RL 数据管线端到端审计</h1>
<p><strong>日期</strong>: {results['timestamp']} | <strong>类型</strong>: 零 GPU 数据验证</p>
<div class="verdict-box {vclass}"><strong>判定: {results['verdict']}</strong></div>
<div class="stats-grid">
<div class="stat-card"><div class="stat-value">{s.get('rl_total_tasks',0)}</div><div class="stat-label">RL 任务</div></div>
<div class="stat-card"><div class="stat-value">{s.get('sft_total_all_versions',0)}</div><div class="stat-label">SFT 行(全版本)</div></div>
<div class="stat-card"><div class="stat-value">{s.get('eval_total_tasks',0)}</div><div class="stat-label">评测任务</div></div>
</div>
"""
    for sec in results['sections']:
        html += f'<h2>{sec["title"]}</h2>\n'
        for item in sec['items']:
            if 'error' in item:
                html += f'<p class="fail">❌ {item["error"]}</p>\n'
                continue
            html += '<table>\n'
            for k, v in item.items():
                if isinstance(v, (dict, list)):
                    v_str = json.dumps(v, ensure_ascii=False, indent=2, default=str)
                    html += f'<tr><td><strong>{k}</strong></td><td><pre>{v_str}</pre></td></tr>\n'
                else:
                    vd = str(v)
                    if v in (True, 'True', 'PASS'):
                        vd = f'<span class="pass">✅ {v}</span>'
                    elif v in (False, 'False', 'FAIL'):
                        vd = f'<span class="fail">❌ {v}</span>'
                    html += f'<tr><td><strong>{k}</strong></td><td>{vd}</td></tr>\n'
            html += '</table>\n'
    if results['issues']:
        html += '<h2>⚠️ 问题清单</h2><ul>\n'
        for issue in results['issues']:
            html += f'<li class="warn">{issue}</li>\n'
        html += '</ul>\n'
    html += '<h2>结论</h2><p>R108 完成数据管线端到端审计。⚠️ 替身模型 RL 结果不可迁移到 BaiZe。</p></body></html>'
    return html

def main():
    parser = argparse.ArgumentParser(description='R108 Data Pipeline Audit')
    parser.add_argument('--html', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    print('[R108] Starting data pipeline audit...')
    results = run_audit(smoke=args.smoke)
    print(f'\n[R108] Verdict: {results["verdict"]}')
    print(f'[R108] Issues: {len(results["issues"])}')
    for issue in results['issues']:
        print(f'  ⚠️ {issue}')
    print(f'\n[R108] Stats: {json.dumps(results["stats"], ensure_ascii=False)}')
    if args.json:
        jp = RUN_DIR / 'r108_data_pipeline_audit.json'
        with open(jp, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f'[R108] JSON: {jp}')
    if args.html:
        html = generate_html(results)
        hp = REPORTS_DIR / 'report_posttrain_r108_data_pipeline_audit_zh.html'
        hp.parent.mkdir(parents=True, exist_ok=True)
        with open(hp, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'[R108] HTML: {hp} ({len(html)} bytes)')
    print('\n[R108] Done.')

if __name__ == '__main__':
    main()
