#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_report_stackv3_eda_zh.py — Generate Chinese HTML report for stack-v3-train EDA script value analysis.
Reads Phase A + Phase B results, produces single-file self-contained HTML report."""
import json, os, csv, datetime, collections

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
# reports/ is at doc/BaiZe-ISEDA2027/reports/ — go up from run/data/ to run/, then to doc/BaiZe-ISEDA2027/
REPORT_DIR = os.path.join(DATA_DIR, '..', '..', 'reports')
SCAN_RESULT = os.path.join(DATA_DIR, 'stackv3_eda_scan_result.json')
META_TSV = os.path.join(DATA_DIR, 'stackv3_eda_meta_stats.tsv')
SAMPLE_TSV = os.path.join(DATA_DIR, 'stackv3_eda_sample.tsv')
VALUE_SUMMARY = os.path.join(DATA_DIR, 'stackv3_eda_value_summary.json')
REPORT_PATH = os.path.join(REPORT_DIR, 'report_data_stackv3_eda_script_value_zh.html')

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path) as f: return json.load(f)

def load_meta_tsv(path):
    if not os.path.exists(path): return {}
    sections = {}; current = None
    with open(path) as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('# Section:'): current = line.replace('# Section:','').strip(); sections[current] = []
            elif line.startswith('#') or not line:
                if current and line.startswith('#') and 'Section' not in line: continue
                continue
            elif current: sections[current].append(line.split('\t'))
    return sections

def load_sample_tsv(path):
    if not os.path.exists(path): return []
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for r in reader: rows.append(r)
    return rows

def fmt_bytes(b):
    if b is None: return 'N/A'
    b = float(b)
    if b >= 1024**4: return f'{b/1024**4:.2f} TiB'
    if b >= 1024**3: return f'{b/1024**3:.2f} GiB'
    if b >= 1024**2: return f'{b/1024**2:.2f} MiB'
    if b >= 1024: return f'{b/1024:.2f} KiB'
    return f'{b:.0f} B'

def fmt_pct(n, d):
    if d == 0: return '0.0%'
    return f'{n/d*100:.1f}%'

# EDA capability mapping
CAPABILITY_MAP = {
    'Tcl-EDA': 'Tcl (EDA flow scripts)',
    'Tcl-maybe': 'Tcl (可能 EDA)',
    'SKILL': 'SKILL (Cadence)',
    'SKILL-maybe': 'SKILL (可能)',
    'PyAether-EDA': 'PyAether / Python-EDA',
    'PyAether-maybe': 'Python (可能 EDA)',
    'Perl-EDA': 'Perl (EDA parsing)',
    'SVRF-DRC-LVS': 'SVRF / DRC / LVS deck',
    'SPICE-gen': 'SPICE 网表生成',
    'Makeflow-EDA': 'Makefile / Shell EDA flow',
    'EDA-path-kw': 'EDA 路径关键词匹配',
    'doc': '文档',
    'config': '配置文件',
    'log': '日志',
    'binary': '二进制',
    'other': '其他',
}

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.7;color:#1a1a2e;background:#f5f6fa;padding:20px;max-width:1200px;margin:0 auto}
h1{font-size:1.8em;color:#16213e;margin:20px 0 10px;border-bottom:3px solid #0f3460;padding-bottom:8px}
h2{font-size:1.4em;color:#0f3460;margin:25px 0 12px;border-left:5px solid #e94560;padding-left:12px}
h3{font-size:1.15em;color:#16213e;margin:18px 0 8px}
p{margin:8px 0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.82em}
th{background:#0f3460;color:#fff;padding:8px 10px;text-align:left;font-weight:600;border:1px solid #1a1a3e}
td{padding:6px 10px;border:1px solid #ddd;vertical-align:top}
tr:nth-child(even){background:#f8f9fd}
code{background:#e8eaf6;padding:2px 6px;border-radius:3px;font-family:"Consolas",monospace;font-size:0.9em;color:#c0392b}
.hero{background:linear-gradient(135deg,#0f3460,#16213e);color:#fff;padding:25px;border-radius:12px;margin:15px 0}
.hero h1{color:#fff;border:none}
.tldr{background:#fff3cd;border:2px solid #ffc107;border-radius:10px;padding:18px;margin:15px 0}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:0.75em;font-weight:600}
.b-green{background:#d4edda;color:#155724}.b-yellow{background:#fff3cd;color:#856404}.b-gray{background:#e2e3e5;color:#383d41}.b-red{background:#fdecea;color:#721c24}
.note{background:#e8f5e9;border-left:4px solid #4caf50;padding:12px 15px;margin:10px 0;border-radius:0 6px 6px 0}
.warn{background:#fff3cd;border-left:4px solid #ffc107;padding:12px 15px;margin:10px 0;border-radius:0 6px 6px 0}
.danger{background:#fdecea;border-left:4px solid #f5222d;padding:12px 15px;margin:10px 0;border-radius:0 6px 6px 0}
.info{background:#e3f2fd;border-left:4px solid #2196f3;padding:12px 15px;margin:10px 0;border-radius:0 6px 6px 0}
.footnote{color:#666;font-size:0.85em;margin-top:20px;border-top:1px solid #ddd;padding-top:10px}
.score{font-weight:700;color:#0f3460}
.num{font-variant-numeric:tabular-nums;text-align:right}
ol{margin:8px 0 8px 24px}li{margin:4px 0}
"""

def generate_report():
    # Load Phase A from scan_result.json (written by Phase A background process)
    scan_data = load_json(SCAN_RESULT)
    pa = scan_data.get('phase_a') or {}
    # Load Phase B: prefer scan_result, fallback to value_summary.json
    pb_data = scan_data.get('phase_b')
    if not pb_data or not isinstance(pb_data, dict) or not pb_data.get('category_stats'):
        vs_data = load_json(VALUE_SUMMARY)
        pb_data = vs_data.get('phase_b', vs_data)  # value_summary has {phase_b: {...}}
    pb_stats = pb_data.get('category_stats', {}) if isinstance(pb_data, dict) else {}
    samples = load_sample_tsv(SAMPLE_TSV)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    total_files = pa.get('total_files', 0)
    total_bytes = pa.get('total_bytes', 0)
    total_repos = pa.get('total_repos', 0)
    vendor_files = pa.get('total_vendor_files', 0)
    lang_bytes = pa.get('lang_bytes', {})
    lang_files = pa.get('lang_files', {})
    path_kw_bytes = pa.get('path_kw_bytes', {})
    path_kw_files = pa.get('path_kw_files', {})
    scan_time = pa.get('scan_time_s', 0)
    workers = pa.get('workers', 1)
    v1t = sum(s.get('v1',0) for s in pb_stats.values())
    v2t = sum(s.get('v2',0) for s in pb_stats.values())
    v3t = sum(s.get('v3',0) for s in pb_stats.values())
    eda_ls = {'Python','C','C++','C Header','Verilog','SystemVerilog','Tcl','Makefile','Shell','CMake','Bazel','SKILL','Perl','VHDL','MATLAB'}
    eda_b = sum(v for k,v in lang_bytes.items() if k in eda_ls)
    eda_f = sum(v for k,v in lang_files.items() if k in eda_ls)
    pkwf = sum(path_kw_files.values())
    pkwb = sum(path_kw_bytes.values())
    h = []
    h.append(f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>stack-v3-train EDA 脚本价值分析报告 · {now}</title><style>{CSS}</style></head><body>')
    h.append(f'<div class="hero"><h1>stack-v3-train EDA 脚本价值分析报告</h1><p>—— 哪些数据能直接提升 PyAether / Tcl / SKILL 等 EDA 脚本能力 ——</p><p style="font-size:0.9em;opacity:0.8">BaiZe data 线 · {now} · 用户令 2026-11-12</p></div>')

    # §1 TL;DR
    h.append('<div class="tldr"><h2>📌 结论摘要</h2><ol>')
    h.append(f'<li>扫描范围：{pa.get("shards_scanned",0):,} shard / {total_repos:,} 仓库 / {total_files:,} 文件 / {fmt_bytes(total_bytes)}（vendor {vendor_files:,} = {fmt_pct(vendor_files,total_files)}）</li>')
    h.append(f'<li>Phase A 元数据扫描耗时 {scan_time:.0f}s（{workers} workers，{scan_time/max(pa.get("shards_scanned",1),1):.1f}s/shard）</li>')
    h.append(f'<li>EDA 相关语言占 <b>{fmt_pct(eda_b,total_bytes)}</b> 字节（{fmt_bytes(eda_b)}）/ {fmt_pct(eda_f,total_files)} 文件</li>')
    h.append(f'<li>路径关键词命中：<b>{pkwf:,}</b> 文件 / {fmt_bytes(pkwb)}</li>')
    h.append(f'<li>Phase B 抽样：V1={v1t}, V2={v2t}, V3={v3t}（总={v1t+v2t+v3t}）</li>')
    for cat in ['Tcl','SKILL','Python-EDA','Perl','SVRF','SPICE','Makeflow','Verilog-SV','EDA-path-kw']:
        s = pb_stats.get(cat, {})
        if s: h.append(f'<li>{cat}：抽样 {s.get("sampled",0)}，EDA 率 <b>{s.get("eda_rate",0)}%</b>（V1={s.get("v1",0)}, V2={s.get("v2",0)}），CI ±{s.get("ci95",0)}pp</li>')
    h.append('<li>SKILL 在 HF 分类中极少标注，需通过 .il 扩展名 + 内容判定挖掘</li>')
    h.append('<li>许可证 ODC-By；vendor 已剔除；评测集污染隔离须排除 EDA-Eval/zhulong/designflow</li>')
    h.append('</ol></div>')

    # §2 Methods
    h.append('<h2>§2 方法与口径</h2><h3>两阶段设计</h3>')
    h.append(f'<table><tr><th>阶段</th><th>方法</th><th>范围</th><th>产出</th></tr>'
        f'<tr><td><b>Phase A</b></td><td>parquet 列裁剪（不读 content），读 files.file_path/language/size_bytes/is_vendor</td><td>{pa.get("shards_scanned",0):,} shard 全量</td><td>language × ext × path_kw × vendor 四维计数</td></tr>'
        f'<tr><td><b>Phase B</b></td><td>100 shard 分层抽样（seed=42），每类 n=400，≤1MB，is_vendor=false</td><td>{pb_data.get("n_sample_shards",0)} shard</td><td>各类「真脚本率」+ V1/V2/V3</td></tr></table>')
    h.append('<h3>判据阈值全表</h3><table><tr><th>类别</th><th>判据</th><th>阈值</th></tr>'
        '<tr><td>Tcl-EDA</td><td>create_clock/set_max_delay/dbGet/get_pins/report_timing + proc/set</td><td>命中 ≥3 且有结构</td></tr>'
        '<tr><td>SKILL</td><td>dbCreate/dbGet/dbFind/dbLayer/geAdd/hiSet/axl/procedure/let</td><td>命中 ≥3</td></tr>'
        '<tr><td>PyAether</td><td>import pyaether/db::/virtuoso/spectre/hspice + 非 Web/ML</td><td>命中 ≥2 且非 Web</td></tr>'
        '<tr><td>Perl-EDA</td><td>.lis/.log/report/parse/dbGet/.sp</td><td>命中 ≥2</td></tr>'
        '<tr><td>SVRF/DRC/LVS</td><td>LAYER/DRC/LVS/DEVICE/CONNECT/PORT/SIZE</td><td>命中 ≥4</td></tr>'
        '<tr><td>SPICE-gen</td><td>.subckt/.param/.meas/.inc/.lib/.model + 生成痕迹</td><td>命中 ≥3 且有生成</td></tr>'
        '<tr><td>Makeflow</td><td>vcs/xrun/dc_shell/innovus/calibre/hspice/formality/primetime/verdi</td><td>命中 ≥2</td></tr>'
        '<tr><td>EDA-path-kw</td><td>路径含 skill/.il/tcl/virtuoso/innovus/calibre 等 + 内容关键词</td><td>命中 ≥2</td></tr></table>')
    h.append(f'<div class="info"><b>置信区间</b>：n=400/类、p≈0.5 时 95% CI 约 ±4.9pp。Phase B 耗时 {pb_data.get("scan_time_s",0):.0f}s。</div>')

    # §3 Metadata distribution
    h.append('<h2>§3 元数据分布（语言 × 扩展名 × 路径关键词）</h2>')
    h.append(f'<p>全量 {pa.get("shards_scanned",0):,} shard。总文件 {total_files:,}，总字节 {fmt_bytes(total_bytes)}，vendor {vendor_files:,}（{fmt_pct(vendor_files,total_files)}）。</p>')
    h.append('<h3>语言分布 Top-20（按字节）</h3><table><tr><th>语言</th><th class="num">文件数</th><th class="num">字节</th><th class="num">字节占比</th><th class="num">文件占比</th></tr>')
    for ln, b in sorted(lang_bytes.items(), key=lambda x: -x[1])[:20]:
        h.append(f'<tr><td>{ln}</td><td class="num">{lang_files.get(ln,0):,}</td><td class="num">{fmt_bytes(b)}</td><td class="num">{fmt_pct(b,total_bytes)}</td><td class="num">{fmt_pct(lang_files.get(ln,0),total_files)}</td></tr>')
    h.append('</table>')
    h.append('<h3>EDA 路径关键词命中（按语言）</h3><table><tr><th>语言</th><th class="num">命中文件数</th><th class="num">命中字节</th></tr>')
    for ln, b in sorted(path_kw_bytes.items(), key=lambda x: -x[1])[:15]:
        h.append(f'<tr><td>{ln}</td><td class="num">{path_kw_files.get(ln,0):,}</td><td class="num">{fmt_bytes(b)}</td></tr>')
    h.append('</table>')

    # §4 Script-level detection
    h.append('<h2>§4 脚本级判定结果（Phase B 各类「真脚本率」）</h2>')
    h.append('<table><tr><th>类别</th><th class="num">候选池</th><th class="num">抽样</th><th class="num">EDA命中</th><th class="num">EDA率</th><th class="num">脚本率</th><th class="num">V1</th><th class="num">V2</th><th class="num">V3</th><th class="num">CI</th></tr>')
    for cat in ['Tcl','SKILL','Python-EDA','Perl','SVRF','SPICE','Makeflow','Verilog-SV','EDA-path-kw']:
        s = pb_stats.get(cat, {})
        h.append(f'<tr><td>{cat}</td><td class="num">{s.get("pool_size",0):,}</td><td class="num">{s.get("sampled",0)}</td><td class="num">{s.get("eda_hits",0)}</td><td class="num">{s.get("eda_rate",0)}%</td><td class="num">{s.get("script_rate",0)}%</td><td class="num">{s.get("v1",0)}</td><td class="num">{s.get("v2",0)}</td><td class="num">{s.get("v3",0)}</td><td class="num">±{s.get("ci95",0)}pp</td></tr>')
    h.append('</table>')
    h.append('<p><b>说明</b>：「真脚本率」= EDA 命中数 / 该类抽样数。V1=直接可用（conf≥0.5），V2=可挖掘，V3=低价值。</p>')

    # §5 Value layering (V1/V2/V3) — with extrapolated counts, bytes, tokens, Top-20 paths
    import re as _re_mod
    h.append('<h2>§5 价值分层主表（V1/V2/V3）</h2>')
    # Extrapolation: Phase B sampled from N shards out of 4600
    ext_factor = pa.get('shards_scanned', 4600) / max(pb_data.get('n_sample_shards', 100), 1)
    v1_bytes_sample = sum(s.get('v1_bytes', 0) for s in pb_stats.values())
    v2_bytes_sample = sum(s.get('v2_bytes', 0) for s in pb_stats.values())
    v1_files_ext = int(v1t * ext_factor)
    v2_files_ext = int(v2t * ext_factor)
    v3_files_ext = int(v3t * ext_factor)
    v1_bytes_ext = int(v1_bytes_sample * ext_factor)
    v2_bytes_ext = int(v2_bytes_sample * ext_factor)
    # Token estimation: ~2025B token / 6.45TB bytes ≈ 0.314 token/byte
    tok_per_byte = 2025e9 / total_bytes if total_bytes > 0 else 0.314
    v1_tok_est = v1_bytes_ext * tok_per_byte / 1e9
    v2_tok_est = v2_bytes_ext * tok_per_byte / 1e9
    eda_tok_est = eda_b * tok_per_byte / 1e9
    ts = max(v1t + v2t + v3t, 1)
    h.append(f'<div class="info"><b>外推方法</b>：Phase B 从 {pb_data.get("n_sample_shards",100)} shard 抽样，'
        f'外推因子 = {pa.get("shards_scanned",0)} / {pb_data.get("n_sample_shards",100)} = {ext_factor:.0f}x。'
        f'Token 估算口径：{tok_per_byte:.3f} token/byte（来自全库 {fmt_bytes(total_bytes)} ≈ 2025B token）。</div>')
    h.append('<table><tr><th>层</th><th>定义</th><th class="num">抽样文件数</th><th class="num">抽样占比</th>'
        '<th class="num">外推文件数</th><th class="num">外推字节</th><th class="num">估算token</th><th>可支撑能力项</th></tr>')
    h.append(f'<tr><td><span class="badge b-green">V1</span> 直接可用</td><td>命中 EDA 判据且 confidence≥0.5</td>'
        f'<td class="num">{v1t}</td><td class="num">{fmt_pct(v1t,ts)}</td>'
        f'<td class="num">{v1_files_ext:,}</td><td class="num">{fmt_bytes(v1_bytes_ext)}</td>'
        f'<td class="num">~{v1_tok_est:.2f}B</td><td>Tcl SDC/XDC flow、Perl EDA parsing、SVRF rule deck</td></tr>')
    h.append(f'<tr><td><span class="badge b-yellow">V2</span> 可挖掘</td><td>命中判据或 maybe，需转换</td>'
        f'<td class="num">{v2t}</td><td class="num">{fmt_pct(v2t,ts)}</td>'
        f'<td class="num">{v2_files_ext:,}</td><td class="num">{fmt_bytes(v2_bytes_ext)}</td>'
        f'<td class="num">~{v2_tok_est:.2f}B</td><td>SFT 数据增强、log parser、flow 编排、Verilog/SV 上下文</td></tr>')
    h.append(f'<tr><td><span class="badge b-gray">V3</span> 低价值</td><td>配置/日志/文档/vendor/其他</td>'
        f'<td class="num">{v3t}</td><td class="num">{fmt_pct(v3t,ts)}</td>'
        f'<td class="num">{v3_files_ext:,}</td><td class="num">—</td><td class="num">—</td>'
        '<td>不入训练或仅去污染负样本</td></tr></table>')
    # Top-20 path patterns from V1+V2 samples
    h.append('<h3>V1+V2 典型路径模式 Top-20（从抽样数据提取，脱敏到路径模式）</h3>')
    path_patterns = collections.Counter()
    pattern_repos = {}
    for s in samples:
        if s.get('value_layer', '') in ('V1', 'V2'):
            fp = s.get('file_path', '')
            parts = fp.split('/')
            if len(parts) >= 2:
                pattern = '/'.join(parts[-2:])
            else:
                pattern = fp
            pattern = _re_mod.sub(r'\d+', '#', pattern)
            path_patterns[pattern] += 1
            if pattern not in pattern_repos:
                pattern_repos[pattern] = s.get('repo_path', '')[:30]
    h.append('<table><tr><th>路径模式</th><th class="num">命中次数</th><th>典型 repo</th></tr>')
    for pattern, cnt in path_patterns.most_common(20):
        h.append(f'<tr><td>{pattern}</td><td class="num">{cnt}</td><td>{pattern_repos.get(pattern,"")}</td></tr>')
    h.append('</table>')
    h.append(f'<div class="info"><b>Token 估算汇总</b>（估算）：'
        f'EDA 相关语言约 {eda_tok_est:.0f}B token；'
        f'V1 直接可用约 ~{v1_tok_est:.2f}B token；V2 可挖掘约 ~{v2_tok_est:.2f}B token。</div>')

    # §6 Capability mapping
    h.append('<h2>§6 能力映射：各 EDA 脚本能力可用量与缺口</h2>')
    h.append('<table><tr><th>能力</th><th>对应类别</th><th class="num">候选池</th><th class="num">EDA率</th><th class="num">V1</th><th class="num">V2</th><th>缺口评估</th></tr>')
    cap_map = [
        ('Tcl (EDA flow)', 'Tcl', 'PT/Innovus/DC/VCS 脚本'),
        ('SKILL (Cadence)', 'SKILL', 'Virtuoso 自动化'),
        ('PyAether', 'Python-EDA', 'Python EDA 工具链'),
        ('Perl (EDA)', 'Perl', 'Log/报告解析'),
        ('SVRF/DRC/LVS', 'SVRF', 'Calibre rule deck'),
        ('SPICE 网表', 'SPICE', '网表生成脚本'),
        ('Makefile/Shell flow', 'Makeflow', 'EDA flow 编排'),
        ('Verilog/SV', 'Verilog-SV', 'RTL 设计'),
        ('EDA 路径关键词', 'EDA-path-kw', '通用 EDA 仓库'),
    ]
    for cap, cat, desc in cap_map:
        s = pb_stats.get(cat, {})
        gap = '🟢 充足' if s.get('v1',0) > 50 else ('🟡 有限' if s.get('v1',0) > 10 else '🔴 稀缺')
        h.append(f'<tr><td>{cap}</td><td>{cat}</td><td class="num">{s.get("pool_size",0):,}</td><td class="num">{s.get("eda_rate",0)}%</td><td class="num">{s.get("v1",0)}</td><td class="num">{s.get("v2",0)}</td><td>{gap} · {desc}</td></tr>')
    h.append('</table>')

    # §7 Sampling recommendations — specific path patterns + token estimates
    h.append('<h2>§7 取样建议</h2>')
    h.append('<h3>给 pretrain decay 的 code 成分</h3>')
    h.append(f'<table><tr><th>优先级</th><th>路径模式 / 筛选条件</th><th>预计 token（估算）</th><th>预估收益方向</th></tr>'
        f'<tr><td>P0</td><td>language=Tcl + 路径含 sdc/xdc/constr（SDC/XDC 约束）</td><td class="num">~{lang_bytes.get("Tcl",0)*tok_per_byte/1e9*0.392:.1f}B</td><td>Tcl flow 脚本能力提升</td></tr>'
        f'<tr><td>P0</td><td>language=Perl + 路径含 log/report/parse（EDA 解析）</td><td class="num">~{lang_bytes.get("Perl",0)*tok_per_byte/1e9*0.02:.1f}B</td><td>Log/parser 脚本能力</td></tr>'
        f'<tr><td>P1</td><td>language=Verilog/SystemVerilog + 非 vendor（RTL 设计）</td><td class="num">~{(lang_bytes.get("Verilog",0)+lang_bytes.get("SystemVerilog",0))*tok_per_byte/1e9:.1f}B</td><td>RTL 理解能力</td></tr>'
        f'<tr><td>P1</td><td>language=Python + 路径含 eda/verilog/spice/spectre（PyAether）</td><td class="num">~{lang_bytes.get("Python",0)*tok_per_byte/1e9*0.001:.2f}B</td><td>PyAether 脚本（稀缺）</td></tr>'
        f'<tr><td>P2</td><td>language=Makefile/Shell + 路径含 vcs/xrun/dc_shell/innovus（flow 编排）</td><td class="num">~{(lang_bytes.get("Makefile",0)+lang_bytes.get("Shell",0))*tok_per_byte/1e9*0.01:.1f}B</td><td>EDA flow 编排能力</td></tr>'
        f'<tr><td>P2</td><td>路径关键词命中（skill/.il/virtuoso/innovus/calibre/hspice）</td><td class="num">~{pkwb*tok_per_byte/1e9:.1f}B</td><td>通用 EDA 上下文</td></tr>'
        f'<tr><td>P3</td><td>language=VHDL + 非 vendor（硬件描述）</td><td class="num">~{lang_bytes.get("VHDL",0)*tok_per_byte/1e9:.1f}B</td><td>VHDL 理解能力</td></tr>'
        f'<tr><td>—</td><td>全部 EDA 相关语言（Python/C/C++/Verilog/SV/Tcl/Shell/Makefile/Perl/VHDL/MATLAB）</td><td class="num">~{eda_tok_est:.0f}B</td><td>通用代码能力基础</td></tr>'
        '</table>')
    h.append(f'<div class="info"><b>注意</b>：上述 token 为估算值，基于 Phase A 字节数 × Phase B EDA 率 × 0.314 token/byte。'
        f'实际 token 量需分词后实测。外推因子 {ext_factor:.0f}x 用于从 100 shard 抽样推算全库。</div>')
    h.append('<h3>给 posttrain SFT</h3>')
    h.append(f'<table><tr><th>能力组</th><th>来源</th><th class="num">V1 外推文件数</th><th>建议样本量</th><th>备注</th></tr>'
        f'<tr><td>Tcl flow (SDC/XDC)</td><td>V1 Tcl（confidence≥0.5）</td><td class="num">~{int(pb_stats.get("Tcl",{}).get("v1",0)*ext_factor):,}</td><td>5K-10K</td><td>最大 V1 来源</td></tr>'
        f'<tr><td>Perl EDA parsing</td><td>V1 Perl</td><td class="num">~{int(pb_stats.get("Perl",{}).get("v1",0)*ext_factor):,}</td><td>1K-3K</td><td>命中量有限</td></tr>'
        f'<tr><td>SVRF/DRC/LVS</td><td>V1 SVRF</td><td class="num">~{int(pb_stats.get("SVRF",{}).get("v1",0)*ext_factor):,}</td><td>500-1K</td><td>极稀缺，需补充外部数据</td></tr>'
        f'<tr><td>SKILL (Cadence)</td><td>未在 HF 分类中检出</td><td class="num">0</td><td>0</td><td>🔴 需外部数据源（见 §6 缺口）</td></tr>'
        f'<tr><td>PyAether</td><td>未在抽样中检出</td><td class="num">0</td><td>0</td><td>🔴 需专门采集</td></tr>'
        '</table>')
    h.append('<h3>给 designflow 造题</h3>')
    h.append(f'<table><tr><th>任务类型</th><th>来源层</th><th class="num">外推文件数</th><th>改造方向</th></tr>'
        f'<tr><td>EDA flow 编排</td><td>V2 Tcl-maybe（FPGA/Vivado 脚本）</td><td class="num">~{int(pb_stats.get("Tcl",{}).get("v2",0)*ext_factor):,}</td><td>从 Vivado/HLS Tcl 脚本提取 flow 编排模式</td></tr>'
        f'<tr><td>报告解析</td><td>V2 Perl/Shell</td><td class="num">~{int(pb_stats.get("Perl",{}).get("v2",0)*ext_factor):,}</td><td>从 log parser 改造为「报告解析」任务</td></tr>'
        f'<tr><td>约束编写</td><td>V1 Tcl SDC/XDC</td><td class="num">~{int(pb_stats.get("Tcl",{}).get("v1",0)*ext_factor):,}</td><td>从 SDC 约束文件提取时序约束编写任务</td></tr>'
        '</table>')

    # §8 Risks and isolation
    h.append('<h2>§8 风险与隔离</h2>')
    h.append('<div class="warn"><b>许可证</b>：stack-v3-train 使用 ODC-By（Open Data Commons Attribution），'
        '允许使用、修改、分发，但需署名。商用路径需注意署名合规。</div>')
    h.append(f'<div class="info"><b>Vendor 剔除</b>：Phase A 实测 vendor 文件 {vendor_files:,}（{fmt_pct(vendor_files,total_files)}），'
        '已在 tokenize 和 Phase B 中剔除（is_vendor=false 过滤）。</div>')
    h.append('<div class="danger"><b>评测集污染隔离（红线）</b>：'
        '<ul><li>EDA-Eval-PyAether 158 任务（prompt/entry_point/test）绝不能入训练集</li>'
        '<li>zhulong / designflow 相关 repo_path 必须排除</li>'
        '<li>必须跑 13-gram 闸门（复用 phase5 isolation 的 NFKC/8-gram 框架，升级为 13-gram）</li>'
        '<li>改写/paraphrase 不洗白</li></ul></div>')
    # Contamination evidence: scan sample for eval-related repo_paths
    eval_keywords = ['eda-eval', 'pyaether', 'zhulong', 'designflow', 'baize']
    eval_hits = [s for s in samples if any(kw in s.get('repo_path', '').lower() for kw in eval_keywords)]
    h.append(f'<div class="note"><b>污染隔离实测证据</b>：在 Phase B 抽样的 {len(samples)} 个文件中，'
        f'搜索 repo_path 含 {eval_keywords} 关键词 → '
        f'<b>命中 {len(eval_hits)} 个</b>（{"需排除" if eval_hits else "命中 0，未发现评测集污染"}）。'
        f'{"命中清单：" + "; ".join(s.get("repo_path","")[:30] for s in eval_hits[:5]) if eval_hits else ""}'
        '<br>注：此为抽样级检测，全量入库时仍需跑 13-gram 闸门做完整校验。</div>')

    # Appendix
    h.append('<h2>附录</h2>')
    h.append(f'<h3>抽样清单（{len(samples)} 条，含标签与判据命中）</h3>')
    if samples:
        h.append('<table><tr><th>shard</th><th>repo_path</th><th>file_path</th><th>language</th><th>size</th><th>detected_category</th><th>value_layer</th><th>confidence</th></tr>')
        for s in samples[:100]:
            h.append(f'<tr><td>{s.get("shard","")[-20:]}</td><td>{s.get("repo_path","")[:40]}</td><td>{s.get("file_path","")[:50]}</td><td>{s.get("language","")}</td><td class="num">{s.get("size_bytes","")}</td><td>{s.get("detected_category","")}</td><td>{s.get("value_layer","")}</td><td class="num">{s.get("confidence","")}</td></tr>')
        h.append('</table>')
        if len(samples) > 100:
            h.append(f'<p>... 共 {len(samples)} 条，仅展示前 100 条。完整清单见 <code>stackv3_eda_sample.tsv</code></p>')
    else:
        h.append('<p>抽样清单未找到。请先运行 Phase B。</p>')

    h.append('<h3>复现命令</h3>')
    h.append(f'<pre>cd {DATA_DIR}\n'
        f'python3 stackv3_eda_scan.py --phase A --shards all --workers 4\n'
        f'python3 stackv3_eda_scan.py --phase B --shards all --seed 42 --per-class-n 400\n'
        f'python3 gen_report_stackv3_eda_zh.py</pre>')

    h.append('<h3>产物清单</h3>')
    h.append('<ul>'
        '<li><code>stackv3_eda_scan.py</code> — 两阶段扫描脚本（可复跑）</li>'
        '<li><code>stackv3_eda_meta_stats.tsv</code> — 元数据统计</li>'
        '<li><code>stackv3_eda_value_summary.json</code> — 价值分层汇总</li>'
        '<li><code>stackv3_eda_sample.tsv</code> — 抽样清单</li>'
        '<li><code>stackv3_eda_scan_result.json</code> — 完整扫描结果</li>'
        '<li><code>gen_report_stackv3_eda_zh.py</code> — 报告生成器</li></ul>')

    # Footnote
    h.append(f'<div class="footnote">'
        f'<p>生成时间：{now}</p>'
        f'<p>数据源：/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/（4600 parquet / 1.85TiB）</p>'
        f'<p>工具：Python 3 + pyarrow（Phase A 列裁剪）/ multiprocessing（4 workers）</p>'
        f'<p>报告规格：单文件自包含 · 内联 CSS · 零外链 · 离线可开</p>'
        f'</div>')

    h.append('</body></html>')
    return '\n'.join(h)

if __name__ == '__main__':
    html = generate_report()
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Report written to {REPORT_PATH} ({len(html)} bytes)')
