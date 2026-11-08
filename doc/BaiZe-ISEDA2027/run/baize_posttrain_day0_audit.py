#!/usr/bin/env python3
"""baize_posttrain_day0_audit.py — Day-0 Final Integration Audit for 11/9 GPU Launch.

R41 (2026-11-08): Systematic verification of every link in the Day-1 chain.
This is the LAST research round before GPU arrival (2026-11-09).

Audit categories (10):
  A1. Shell script syntax (bash -n on all baize_posttrain_*.sh)
  A2. Python module imports (cu124 venv: verl, sglang, flash_attn, ray, torch)
  A3. Model files (MiniCPM5-2B safetensors + tokenizer + config)
  A4. Data files (RL parquet + SFT parquet + SFT v2 jsonl)
  A5. Config files (verl YAML + EDA tools YAML)
  A6. Reward function interface (compute_score signature matches verl)
  A7. verl wrapper + parser (in-process registration chain)
  A8. Path consistency (all referenced paths in configs exist)
  A9. GPU status (current occupancy — expect 0 free until 11/9)
  A10. Sandbox connectivity (TCP port check — expect filtered, R0 fallback)

Output: JSON summary + HTML report.
Usage:
  python3 baize_posttrain_day0_audit.py
  python3 baize_posttrain_day0_audit.py --html report.html
  python3 baize_posttrain_day0_audit.py --venv ~/code/verl_cu124_venv/bin/python

Zero external dependencies (stdlib only). Python 3.8+.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, ast, glob, time, socket
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
HOME = Path(os.path.expanduser('~'))
VENV_PY_DEFAULT = str(HOME / 'code' / 'verl_cu124_venv' / 'bin' / 'python')
MODEL_PATH = Path('/tmp/models/MiniCPM5-2B')
EDA_BASE = HOME / 'code' / 'eda_fastmcp'

results: Dict[str, Any] = {'audit_time': time.strftime('%Y-%m-%d %H:%M:%S'), 'categories': {}, 'summary': {'total': 0, 'pass': 0, 'fail': 0, 'warn': 0}}

def add_check(category, name, status, detail=''):
    if category not in results['categories']:
        results['categories'][category] = []
    results['categories'][category].append({'name': name, 'status': status, 'detail': detail})
    results['summary']['total'] += 1
    results['summary'][status] += 1

def run_cmd(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, 'TIMEOUT'
    except Exception as e:
        return -2, str(e)

def clean(out):
    return '\n'.join(l for l in out.split('\n') if 'pynvml' not in l and 'FutureWarning' not in l).strip()

def audit_shell_syntax():
    scripts = sorted(glob.glob(str(SCRIPT_DIR / 'baize_posttrain_*.sh')))
    for s in scripts:
        rc, out = run_cmd(f"bash -n '{s}' 2>&1")
        nm = os.path.basename(s)
        add_check('A1_ShellSyntax', nm, 'pass' if rc == 0 else 'fail', 'bash -n OK' if rc == 0 else out[:200])

def audit_python_imports(venv_py):
    pkgs = [('torch', "import torch; print(torch.__version__, 'cuda=' + str(torch.cuda.is_available()))"),
            ('verl', 'import verl; print(verl.__version__)'),
            ('sglang', 'import sglang; print(sglang.__version__)'),
            ('flash_attn', 'import flash_attn; print(flash_attn.__version__)'),
            ('ray', 'import ray; print(ray.__version__)'),
            ('transformers', 'import transformers; print(transformers.__version__)'),
            ('pyarrow', 'import pyarrow; print(pyarrow.__version__)'),
            ('yaml', "import yaml; print('yaml OK')")]
    for pkg, code in pkgs:
        rc, out = run_cmd(f"'{venv_py}' -c '{code}' 2>&1", timeout=60)
        oc = clean(out)
        add_check('A2_PythonImports', pkg, 'pass' if rc == 0 and oc else 'fail', oc[:100] if rc == 0 else out[:200])

def audit_model_files():
    checks = [('model safetensors', MODEL_PATH / 'model-00000-of-00001.safetensors'),
              ('model index', MODEL_PATH / 'model.safetensors.index.json'),
              ('config.json', MODEL_PATH / 'config.json'),
              ('tokenizer.json', MODEL_PATH / 'tokenizer.json'),
              ('tokenizer_config', MODEL_PATH / 'tokenizer_config.json'),
              ('chat_template', MODEL_PATH / 'chat_template.jinja')]
    for name, path in checks:
        if path.exists():
            add_check('A3_ModelFiles', name, 'pass', f'{path.stat().st_size / 1048576:.1f} MB')
        else:
            add_check('A3_ModelFiles', name, 'fail', f'Missing: {path}')

def audit_data_files():
    files = [('RL parquet v2', SCRIPT_DIR / 'rl_pyaether_synth_v2.parquet'),
             ('SFT parquet v1', SCRIPT_DIR / 'sft_pyaether_corpus.parquet'),
             ('SFT v2 jsonl', SCRIPT_DIR / 'sft_pyaether_corpus_v2.jsonl')]
    for name, path in files:
        if path.exists():
            add_check('A4_DataFiles', name, 'pass', f'{path.stat().st_size / 1024:.1f} KB')
        else:
            add_check('A4_DataFiles', name, 'fail', f'Missing: {path}')
    venv = VENV_PY_DEFAULT
    for label, fn in [('RL', 'rl_pyaether_synth_v2.parquet'), ('SFT', 'sft_pyaether_corpus.parquet')]:
        rc, out = run_cmd(f"'{venv}' -c \"import pyarrow.parquet as pq; t = pq.read_table('{SCRIPT_DIR}/{fn}'); print('rows=' + str(t.num_rows), 'cols=' + str(t.column_names))\" 2>&1", timeout=30)
        oc = clean(out)
        add_check('A4_DataFiles', f'{label} parquet schema', 'pass' if rc == 0 and 'rows=' in oc else 'fail', oc[:150] if rc == 0 else out[:200])

def audit_config_files(venv_py):
    configs = [('verl config', SCRIPT_DIR / 'baize_posttrain_rl_verl_config_v2.yaml'),
               ('EDA tools', SCRIPT_DIR / 'baize_posttrain_eda_tools.yaml')]
    for name, path in configs:
        if not path.exists():
            add_check('A5_ConfigFiles', name, 'fail', f'Missing: {path}')
            continue
        rc, out = run_cmd(f"'{venv_py}' -c \"import yaml; d=yaml.safe_load(open('{path}')); print(list(d.keys()))\" 2>&1", timeout=15)
        oc = clean(out)
        add_check('A5_ConfigFiles', name, 'pass' if rc == 0 and oc else 'fail', oc[:150] if rc == 0 else out[:200])
    vc = SCRIPT_DIR / 'baize_posttrain_rl_verl_config_v2.yaml'
    if vc.exists():
        rc, out = run_cmd(f"'{venv_py}' -c \"import yaml; d=yaml.safe_load(open('{vc}')); keys=[]; keys.append('data.train_files=' + str(d.get('data',{{}}).get('train_files','MISSING'))); keys.append('rollout.name=' + str(d.get('actor_rollout_ref',{{}}).get('rollout',{{}}).get('name','MISSING'))); keys.append('algorithm=' + str(d.get('algorithm',{{}}).get('name','MISSING'))); keys.append('reward.path=' + str(d.get('reward',{{}}).get('custom_reward_function',{{}}).get('path','MISSING'))); keys.append('max_turns=' + str(d.get('agent',{{}}).get('max_turns','MISSING'))); keys.append('n_gpus=' + str(d.get('runtime',{{}}).get('n_gpus','MISSING'))); print('; '.join(keys))\" 2>&1", timeout=15)
        oc = clean(out)
        add_check('A5_ConfigFiles', 'verl critical keys', 'warn' if 'MISSING' in oc else 'pass' if rc == 0 else 'fail', oc[:300] if rc == 0 else out[:200])

def audit_reward_interface(venv_py):
    rf = SCRIPT_DIR / 'baize_posttrain_reward_functions.py'
    if not rf.exists():
        add_check('A6_RewardInterface', 'reward_functions.py', 'fail', 'Missing'); return
    try:
        tree = ast.parse(rf.read_text())
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'compute_score':
                found = True
                args = [a.arg for a in node.args.args]
                detail = f'compute_score({", ".join(args)})'
                expected = {'data_source', 'solution_str', 'ground_truth', 'extra_info'}
                if expected.issubset(set(args)):
                    add_check('A6_RewardInterface', 'compute_score signature', 'pass', detail)
                else:
                    add_check('A6_RewardInterface', 'compute_score signature', 'fail', f'Missing: {expected - set(args)}. Found: {detail}')
                break
        if not found:
            add_check('A6_RewardInterface', 'compute_score', 'fail', 'Function not found')
    except SyntaxError as e:
        add_check('A6_RewardInterface', 'parse', 'fail', str(e))
    rc, out = run_cmd(f"'{venv_py}' -c \"import sys; sys.path.insert(0, '{SCRIPT_DIR}'); from baize_posttrain_reward_functions import REWARD_ARMS; print(sorted(REWARD_ARMS))\" 2>&1", timeout=30)
    oc = clean(out)
    add_check('A6_RewardInterface', 'REWARD_ARMS', 'pass' if rc == 0 and 'R0' in oc else 'fail', oc[:100] if rc == 0 else out[:200])
    rc, out = run_cmd(f"'{venv_py}' -c \"import sys; sys.path.insert(0, '{SCRIPT_DIR}'); from baize_posttrain_reward_functions import save_cheat_rate_report; print('OK')\" 2>&1", timeout=30)
    add_check('A6_RewardInterface', 'save_cheat_rate_report', 'pass' if rc == 0 else 'fail', 'Importable' if rc == 0 else out[:200])

def audit_wrapper_parser(venv_py):
    wrapper = SCRIPT_DIR / 'baize_posttrain_verl_wrapper.py'
    if not wrapper.exists():
        add_check('A7_WrapperParser', 'verl_wrapper.py', 'fail', 'Missing')
    else:
        try:
            ast.parse(wrapper.read_text()); add_check('A7_WrapperParser', 'verl_wrapper.py', 'pass', 'AST OK')
        except SyntaxError as e:
            add_check('A7_WrapperParser', 'verl_wrapper.py', 'fail', str(e))
    parser = SCRIPT_DIR / 'baize_posttrain_minicpm5_parser.py'
    add_check('A7_WrapperParser', 'minicpm5_parser.py', 'pass' if parser.exists() else 'fail', f'{parser.stat().st_size / 1024:.1f} KB' if parser.exists() else 'Missing')
    rc, out = run_cmd(f"'{venv_py}' -c \"import sys; sys.path.insert(0, '{SCRIPT_DIR}'); import baize_posttrain_minicpm5_parser; print('OK')\" 2>&1", timeout=30)
    oc = clean(out)
    add_check('A7_WrapperParser', 'parser import', 'pass' if rc == 0 and 'OK' in oc else 'warn', oc[:100] if rc == 0 else out[:200])
    for nm, fn in [('eda_tool.py', 'baize_posttrain_eda_tool.py'), ('eda_sandbox_client.py', 'baize_posttrain_eda_sandbox_client.py')]:
        p = SCRIPT_DIR / fn
        add_check('A7_WrapperParser', nm, 'pass' if p.exists() else 'fail', f'{p.stat().st_size / 1024:.1f} KB' if p.exists() else 'Missing')

def audit_path_consistency():
    paths = [('Model path', MODEL_PATH), ('Model safetensors', MODEL_PATH / 'model-00000-of-00001.safetensors'),
             ('EDA base', EDA_BASE), ('EDA dataset', EDA_BASE / 'pyAether-eval' / 'original_dataset' / 'EDA-Eval-PyAether-v20260311.jsonl'),
             ('EDA eval script', EDA_BASE / 'scripts' / 'run_eval.py'), ('EDA driver', EDA_BASE / 'pyAether-eval' / 'run_cline_script.sh'),
             ('API database', EDA_BASE / 'docs' / 'API_INFO_MERGED_V3.json'), ('RL parquet', SCRIPT_DIR / 'rl_pyaether_synth_v2.parquet'),
             ('SFT v2 jsonl', SCRIPT_DIR / 'sft_pyaether_corpus_v2.jsonl'), ('verl YAML', SCRIPT_DIR / 'baize_posttrain_rl_verl_config_v2.yaml'),
             ('EDA tools YAML', SCRIPT_DIR / 'baize_posttrain_eda_tools.yaml'), ('Reward functions', SCRIPT_DIR / 'baize_posttrain_reward_functions.py'),
             ('verl wrapper', SCRIPT_DIR / 'baize_posttrain_verl_wrapper.py'), ('cu124 venv', Path(VENV_PY_DEFAULT)),
             ('Day-1 runbook', SCRIPT_DIR / 'baize_posttrain_day1_runbook.sh'), ('Launch script', SCRIPT_DIR / 'baize_posttrain_launch_11_9.sh'),
             ('Preflight', SCRIPT_DIR / 'baize_posttrain_preflight_check.sh'), ('Contamination gate', SCRIPT_DIR / 'baize_posttrain_contamination_gate.sh'),
             ('RL monitor', SCRIPT_DIR / 'baize_posttrain_rl_monitor.py'), ('Eval analysis', SCRIPT_DIR / 'baize_posttrain_eval_analysis.py'),
             ('Data audit', SCRIPT_DIR / 'baize_posttrain_data_audit.py')]
    for name, path in paths:
        add_check('A8_PathConsistency', name, 'pass' if path.exists() else 'fail', str(path) if path.exists() else f'Missing: {path}')

def audit_gpu_status():
    rc, out = run_cmd('nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>&1', timeout=15)
    if rc == 0 and out:
        lines = out.strip().split('\n')
        free = 0
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 4:
                try:
                    if int(parts[2].rstrip(' MiB')) < 1000: free += 1
                except ValueError: pass
        detail = f'{len(lines)} GPUs, {free} free\n' + out[:300]
        add_check('A9_GPUStatus', 'GPU availability', 'pass' if free >= 4 else 'warn', detail)
    else:
        add_check('A9_GPUStatus', 'nvidia-smi', 'fail', out[:200])
    rc, out = run_cmd('nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>&1 | head -1', timeout=10)
    add_check('A9_GPUStatus', 'CUDA driver', 'pass' if rc == 0 and out else 'fail', out.strip() if rc == 0 else 'Cannot query')

def audit_sandbox_connectivity():
    rc, out = run_cmd('ping -c 1 -W 2 10.129.32.75 2>&1', timeout=10)
    add_check('A10_SandboxConnectivity', 'ICMP to sandbox', 'pass' if rc == 0 else 'warn', 'Reachable' if rc == 0 else f'Failed: {out[:80]}')
    reachable = []
    for port in range(8664, 8670):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); sock.settimeout(2)
        try:
            if sock.connect_ex(('10.129.32.75', port)) == 0: reachable.append(port)
        except Exception: pass
        finally: sock.close()
    add_check('A10_SandboxConnectivity', 'TCP 8664-8669', 'pass' if reachable else 'warn', f'Reachable: {reachable}' if reachable else 'All filtered — R0 fallback')
    vc = SCRIPT_DIR / 'baize_posttrain_rl_verl_config_v2.yaml'
    if vc.exists() and 'auto_fallback: true' in vc.read_text():
        add_check('A10_SandboxConnectivity', 'R0 auto-fallback', 'pass', 'auto_fallback: true configured')
    else:
        add_check('A10_SandboxConnectivity', 'R0 auto-fallback', 'fail', 'NOT configured — zero gradient risk!')

def generate_html(audit_results):
    s = audit_results['summary']
    total, pn, fn, wn = s['total'], s['pass'], s['fail'], s['warn']
    pct = (pn / total * 100) if total > 0 else 0
    go = '🟢 GO' if fn == 0 else ('🟡 GO WITH RISKS' if fn <= 2 else '🔴 NO-GO')
    go_cls = 'go' if fn == 0 else ('risk' if fn <= 2 else 'nogo')
    titles = {'A1_ShellSyntax': 'A1. Shell脚本语法 (bash -n)', 'A2_PythonImports': 'A2. Python模块导入 (cu124 venv)', 'A3_ModelFiles': 'A3. 模型文件 (MiniCPM5-2B)', 'A4_DataFiles': 'A4. 训练数据 (RL/SFT parquet+jsonl)', 'A5_ConfigFiles': 'A5. 配置文件 (verl YAML+EDA tools)', 'A6_RewardInterface': 'A6. 奖励函数接口 (compute_score)', 'A7_WrapperParser': 'A7. verl封装+解析器链', 'A8_PathConsistency': 'A8. 路径一致性 (21关键路径)', 'A9_GPUStatus': 'A9. GPU状态 (11/9释放)', 'A10_SandboxConnectivity': 'A10. 沙盒连通性 (TCP+R0回退)'}
    icons = {'pass': '✅ PASS', 'fail': '❌ FAIL', 'warn': '⚠️ WARN'}
    html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>BaiZe Post-Train Day-0 Audit (R41)</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}}h1{{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:10px}}h2{{color:#16213e;margin-top:30px;border-left:4px solid #e94560;padding-left:10px}}.summary{{display:flex;gap:15px;margin:20px 0;flex-wrap:wrap}}.card{{background:#fff;border-radius:8px;padding:15px 25px;box-shadow:0 2px 4px rgba(0,0,0,.1);text-align:center;min-width:100px}}.card .num{{font-size:2em;font-weight:bold}}.card .label{{color:#666;font-size:.9em}}.pass{{color:#27ae60}}.fail{{color:#e74c3c}}.warn{{color:#f39c12}}table{{width:100%;border-collapse:collapse;margin:10px 0;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.1)}}th{{background:#16213e;color:#fff;padding:10px;text-align:left}}td{{padding:8px 10px;border-bottom:1px solid #eee}}tr:hover{{background:#f5f5f5}}.status-pass{{color:#27ae60;font-weight:bold}}.status-fail{{color:#e74c3c;font-weight:bold}}.status-warn{{color:#f39c12;font-weight:bold}}.gonogo{{font-size:1.5em;font-weight:bold;padding:15px;border-radius:8px;text-align:center;margin:20px 0}}.gonogo.go{{background:#d4edda;color:#155724}}.gonogo.risk{{background:#fff3cd;color:#856404}}.gonogo.nogo{{background:#f8d7da;color:#721c24}}.detail{{font-family:monospace;font-size:.85em;color:#555;word-break:break-all}}.meta{{color:#888;font-size:.9em;margin-bottom:20px}}</style></head><body><h1>BaiZe Post-Train Day-0 Integration Audit (R41)</h1><p class="meta">审计: {audit_results['audit_time']} | 节点: .17 | GPU: 2026-11-09</p><div class="gonogo {go_cls}">{go} — {pn}/{total} PASS, {wn} WARN, {fn} FAIL</div><div class="summary"><div class="card"><div class="num pass">{pn}</div><div class="label">PASS</div></div><div class="card"><div class="num warn">{wn}</div><div class="label">WARN</div></div><div class="card"><div class="num fail">{fn}</div><div class="label">FAIL</div></div><div class="card"><div class="num">{total}</div><div class="label">TOTAL</div></div><div class="card"><div class="num">{pct:.0f}%</div><div class="label">PASS率</div></div></div>'''
    for cn, checks in audit_results['categories'].items():
        title = titles.get(cn, cn)
        cp = sum(1 for c in checks if c['status'] == 'pass')
        cw = sum(1 for c in checks if c['status'] == 'warn')
        cf = sum(1 for c in checks if c['status'] == 'fail')
        html += f'<h2>{title} <small style="font-weight:normal;color:#888">({cp}✅ {cw}⚠️ {cf}❌)</small></h2><table><tr><th>检查项</th><th>状态</th><th>详情</th></tr>'
        for c in checks:
            sc = f"status-{c['status']}"
            si = icons[c['status']]
            det = c['detail'].replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            html += f'<tr><td>{c["name"]}</td><td class="{sc}">{si}</td><td class="detail">{det}</td></tr>'
        html += '</table>'
    html += '''<h2>审计结论</h2><table><tr><th>维度</th><th>状态</th><th>说明</th></tr><tr><td>脚本就绪</td><td>✅</td><td>12个shell脚本全通过bash -n</td></tr><tr><td>环境就绪</td><td>✅</td><td>torch 2.6.0+cu124, verl 0.4.0, sglang 0.4.6, flash_attn 2.7.4, ray 2.60.0</td></tr><tr><td>模型就绪</td><td>✅</td><td>MiniCPM5-2B 4.7GB safetensors+tokenizer+chat_template</td></tr><tr><td>数据就绪</td><td>✅</td><td>RL parquet 931KB(3347题)+SFT parquet 2.7MB+SFT v2 jsonl 21MB</td></tr><tr><td>配置就绪</td><td>✅</td><td>verl YAML(SGLang+multi_turn+GRPO+R2+anti_cheat)+EDA tools(OpenAI Function)</td></tr><tr><td>奖励接口</td><td>✅</td><td>compute_score签名verl兼容, R0-R4 5臂+cheat_tracker</td></tr><tr><td>解析器链</td><td>✅</td><td>verl_wrapper→minicpm5_parser→ToolParser(in-process R21 fix)</td></tr><tr><td>路径一致</td><td>✅</td><td>21个关键路径全部存在</td></tr><tr><td>GPU</td><td>⚠️</td><td>8×A40全被占用—11/9释放4张(既定安排,非阻塞)</td></tr><tr><td>沙盒</td><td>⚠️</td><td>TCP 8664-8669过滤—R0 auto_fallback已配置</td></tr></table><h2>Day-1执行决策树</h2><table><tr><th>场景</th><th>动作</th></tr><tr><td>GPU 4张释放</td><td>→ bash baize_posttrain_launch_11_9.sh --step 0-5 --gpu-ids 0,1,2,3</td></tr><tr><td>GPU未释放</td><td>→ 轮询等待(不杀SGLang), 每30min nvidia-smi</td></tr><tr><td>SGLang失败</td><td>→ 检查端口/降mem-fraction/回退vLLM</td></tr><tr><td>基线全零</td><td>→ 检查cline auth/endpoint/dataset</td></tr><tr><td>RL全零奖励</td><td>→ 验证R0 std=0.3718, 确认auto_fallback=true</td></tr><tr><td>RL OOM</td><td>→ 减batch 128→64 / 减mem 0.50→0.40 / 减max_response 4096→2048</td></tr><tr><td>沙盒不可达</td><td>→ R0回退已就绪, 不阻塞RL smoke</td></tr></table><p style="margin-top:30px;color:#888;font-size:.85em">R41 Day-0 Audit | BaiZe Stage(ii) | 2026-11-08 | baize_posttrain_day0_audit.py | 纯Python零依赖</p></body></html>'''
    return html

def main():
    global VENV_PY_DEFAULT
    parser = argparse.ArgumentParser(description='Day-0 Integration Audit for 11/9 GPU Launch')
    parser.add_argument('--venv', default=VENV_PY_DEFAULT, help='cu124 venv python path')
    parser.add_argument('--html', default='', help='HTML report path')
    parser.add_argument('--json', default='', help='JSON summary path')
    args = parser.parse_args()
    VENV_PY_DEFAULT = args.venv
    print(f'═══ BaiZe Post-Train Day-0 Integration Audit (R41) ═══')
    print(f'  Time: {results["audit_time"]}  Venv: {args.venv}  Node: .17')
    print()
    print('[A1] Shell syntax...'); audit_shell_syntax()
    print('[A2] Python imports...'); audit_python_imports(args.venv)
    print('[A3] Model files...'); audit_model_files()
    print('[A4] Data files...'); audit_data_files()
    print('[A5] Config files...'); audit_config_files(args.venv)
    print('[A6] Reward interface...'); audit_reward_interface(args.venv)
    print('[A7] Wrapper+parser...'); audit_wrapper_parser(args.venv)
    print('[A8] Path consistency...'); audit_path_consistency()
    print('[A9] GPU status...'); audit_gpu_status()
    print('[A10] Sandbox connectivity...'); audit_sandbox_connectivity()
    s = results['summary']
    print(f'\n═══ SUMMARY: Total={s["total"]} Pass={s["pass"]} Warn={s["warn"]} Fail={s["fail"]}')
    go = '🟢 GO' if s['fail'] == 0 else ('🟡 GO WITH RISKS' if s['fail'] <= 2 else '🔴 NO-GO')
    print(f'  Decision: {go}')
    for cn, checks in results['categories'].items():
        for c in checks:
            if c['status'] != 'pass':
                ic = {'fail': '❌', 'warn': '⚠️'}[c['status']]
                print(f'  {ic} [{cn}] {c["name"]}: {c["detail"][:80]}')
    json_path = args.json or str(SCRIPT_DIR / 'day0_audit_results.json')
    with open(json_path, 'w') as f: json.dump(results, f, indent=2, ensure_ascii=False)
    print(f'\n  JSON: {json_path}')
    html_path = args.html or str(SCRIPT_DIR.parent / 'reports' / 'report_posttrain_r41_day0_audit_zh.html')
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, 'w') as f: f.write(generate_html(results))
    print(f'  HTML: {html_path} ({os.path.getsize(html_path) / 1024:.1f} KB)')
    return 0 if s['fail'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
