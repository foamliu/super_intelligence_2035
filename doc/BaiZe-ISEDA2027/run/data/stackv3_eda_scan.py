#!/usr/bin/env python3
"""stack-v3-train EDA Script Value Analysis — Two-Phase Scan.

Phase A: Metadata full scan (no content read) — language x ext x path_kw x vendor
Phase B: Content stratified sampling — EDA script detection per category
"""
import pyarrow.parquet as pq
import os, sys, glob, json, csv, time, random, re, collections, argparse

DATA_DIR = '/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data'
OUT_DIR = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data'

EDA_PATH_KW = re.compile(
    r'skill|\.il$|tcl|\.sdc$|pyaether|virtuoso|innovus|icc2|dc_shell|pt_shell|'
    r'primetime|calibre|svrf|lvs|drc|hspice|spectre|finesim|verdi|formality|'
    r'tessent|vcs|xrun|questa|modelsim|spice|spectre|cdl|lef|def|gds|oasis|'
    r'liberty|\.lib$', re.IGNORECASE)

TCL_PATTERNS = ['create_clock','set_max_delay','set_input_delay','dbGet','get_db',
    'get_pins','get_cells','report_timing','link_design','read_verilog',
    'read_def','foreach_in_collection','redirect','set_max_fanout',
    'compile_ultra','current_design','source ']
TCL_STRUCT = re.compile(r'\bproc\b|\bset\s+\w+', re.IGNORECASE)

SKILL_PATTERNS = ['dbCreate','dbGet','dbFind','dbLayer','geAdd','geGet',
    'hiSet','hiGet','axl','sdb','rod','procedure(','let(','defun','axlDM']

PYAETHER_PATTERNS = ['import pyaether','from pyaether','db::','dbCreate',
    'virtuoso','spectre','hspice','pyaether']
PY_NON_EDA = re.compile(r'django|flask|torch|numpy|pandas|tensorflow|keras|sklearn|requests|http|sqlalchemy', re.IGNORECASE)

PERL_EDA_PATTERNS = ['.lis','.log','report','parse','dbGet','.sp','open_file','read_file']
SVRF_PATTERNS = ['LAYER','DRC','LVS','DEVICE','CONNECT','PORT','SIZE']
SPICE_PATTERNS = ['.subckt','.param','.meas','.inc','.lib','.model']
SPICE_GEN = re.compile(r"f['\"].*?['\"]|template|write\(|open\(|\.write\(", re.IGNORECASE)
MAKEFLOW_PATTERNS = ['vcs','xrun','dc_shell','innovus','calibre','hspice','formality','primetime','verdi']

EDA_LANGS = {'Python','C','C++','C++ Header','C Header','Verilog',
    'SystemVerilog','Tcl','Makefile','CMake','Shell','Bazel','MATLAB','VHDL'}

def get_all_parquets():
    return sorted(glob.glob(os.path.join(DATA_DIR, '*.parquet')))

def detect_eda_script(content, language, file_path):
    """Detect if a file is an EDA script. Returns (category, confidence, hits)."""
    if not content or len(content) > 1048576:
        return ('skip', 0, [])
    ext = os.path.splitext(file_path)[1].lower()
    hits = []; cat = None; conf = 0

    if language == 'Tcl' or ext in ('.tcl','.sdc','.xdc'):
        tcl_hits = sum(1 for p in TCL_PATTERNS if p in content)
        has_struct = bool(TCL_STRUCT.search(content))
        if tcl_hits >= 3 and has_struct:
            cat = 'Tcl-EDA'; conf = min(tcl_hits/5, 1.0)
            hits = [p for p in TCL_PATTERNS if p in content][:5]
        elif tcl_hits >= 1:
            cat = 'Tcl-maybe'; conf = tcl_hits/5
            hits = [p for p in TCL_PATTERNS if p in content][:3]

    if cat is None and (language in ('SKILL','Other') or ext == '.il'):
        skill_hits = sum(1 for p in SKILL_PATTERNS if p in content)
        if skill_hits >= 3:
            cat = 'SKILL'; conf = min(skill_hits/5, 1.0)
            hits = [p for p in SKILL_PATTERNS if p in content][:5]
        elif ext == '.il' and skill_hits >= 1:
            cat = 'SKILL-maybe'; conf = skill_hits/5
            hits = [p for p in SKILL_PATTERNS if p in content][:3]

    if cat is None and (language == 'Python' or ext == '.py'):
        pya_hits = sum(1 for p in PYAETHER_PATTERNS if p in content.lower())
        has_non_eda = bool(PY_NON_EDA.search(content[:2000]))
        if pya_hits >= 2 and not has_non_eda:
            cat = 'PyAether-EDA'; conf = min(pya_hits/4, 1.0)
            hits = [p for p in PYAETHER_PATTERNS if p in content.lower()][:5]
        elif pya_hits >= 1 and not has_non_eda:
            cat = 'Python-EDA-maybe'; conf = pya_hits/4
            hits = [p for p in PYAETHER_PATTERNS if p in content.lower()][:3]

    if cat is None and (language == 'Perl' or ext in ('.pl','.pls')):
        perl_hits = sum(1 for p in PERL_EDA_PATTERNS if p in content)
        if perl_hits >= 2:
            cat = 'Perl-EDA'; conf = min(perl_hits/3, 1.0)
            hits = [p for p in PERL_EDA_PATTERNS if p in content][:5]

    if cat is None and (ext == '.svrf' or any(k in file_path.lower() for k in ['svrf','drc','lvs'])):
        svrf_hits = sum(1 for p in SVRF_PATTERNS if p in content)
        if svrf_hits >= 4:
            cat = 'SVRF-DRC-LVS'; conf = min(svrf_hits/6, 1.0)
            hits = [p for p in SVRF_PATTERNS if p in content][:5]

    if cat is None and (ext in ('.sp','.spc','.cir') or any(k in file_path.lower() for k in ['spice','netlist'])):
        spice_hits = sum(1 for p in SPICE_PATTERNS if p in content)
        has_gen = bool(SPICE_GEN.search(content))
        if spice_hits >= 3 and has_gen:
            cat = 'SPICE-gen'; conf = min(spice_hits/5, 1.0)
            hits = [p for p in SPICE_PATTERNS if p in content][:5]

    if cat is None and (language in ('Makefile','Shell') or ext in ('.mk','.sh','.bash')):
        flow_hits = sum(1 for p in MAKEFLOW_PATTERNS if p in content.lower())
        if flow_hits >= 2:
            cat = 'Makeflow-EDA'; conf = min(flow_hits/4, 1.0)
            hits = [p for p in MAKEFLOW_PATTERNS if p in content.lower()][:5]

    if cat is None and EDA_PATH_KW.search(file_path):
        eda_kw_hits = sum(1 for p in MAKEFLOW_PATTERNS + TCL_PATTERNS[:5] if p in content.lower())
        if eda_kw_hits >= 2:
            cat = 'EDA-path-kw'; conf = eda_kw_hits/5
            hits = [p for p in MAKEFLOW_PATTERNS + TCL_PATTERNS[:5] if p in content.lower()][:5]

    if cat is None:
        if ext in ('.md','.rst','.txt','.doc','.pdf'): cat = 'doc'
        elif ext in ('.json','.yaml','.yml','.xml','.csv','.tsv','.toml','.ini','.cfg'): cat = 'config'
        elif ext in ('.log','.lis','.out'): cat = 'log'
        elif ext in ('.png','.jpg','.jpeg','.gif','.svg','.pdf'): cat = 'binary'
        else: cat = 'other'

    return (cat, conf, hits)

def classify_type(file_path, language):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.md','.rst','.txt','.doc'): return 'doc'
    if ext in ('.json','.yaml','.yml','.xml','.csv','.tsv','.toml','.ini','.cfg','.conf'): return 'config'
    if ext in ('.log','.lis','.out','.rpt'): return 'log'
    if ext in ('.png','.jpg','.jpeg','.gif','.svg','.pdf','.bin','.dat'): return 'binary'
    if language in ('Python','Tcl','Perl','Shell','Makefile','CMake','C','C++',
                    'Verilog','SystemVerilog','VHDL','MATLAB','SKILL'): return 'script'
    if any(kw in file_path.lower() for kw in ['readme','golden','expected','regression']): return 'doc'
    return 'other'

def phase_a_meta_scan(shard_files, out_prefix=''):
    """Phase A: scan metadata columns only (no content)."""
    t_start = time.time()
    lang_bytes = collections.Counter(); lang_files = collections.Counter()
    ext_bytes = collections.Counter(); ext_files = collections.Counter()
    path_kw_bytes = collections.Counter(); path_kw_files = collections.Counter()
    vendor_bytes = collections.Counter(); vendor_files = collections.Counter()
    lang_ext_bytes = collections.Counter()
    total_files = 0; total_bytes = 0; total_repos = 0
    total_vendor_files = 0; total_vendor_bytes = 0; shards_scanned = 0

    for sf in shard_files:
        t0 = time.time()
        try:
            pf = pq.ParquetFile(sf)
            tbl = pf.read(columns=["repo_path","num_files",
                "files.list.element.size_bytes","files.list.element.file_path",
                "files.list.element.language","files.list.element.is_vendor"])
            n_repos = tbl.num_rows; total_repos += n_repos
            files_col = tbl.column('files').to_pylist()
            num_files_col = tbl.column('num_files').to_pylist()
            for i, fl in enumerate(files_col):
                if num_files_col[i] == 0 or not fl: continue
                for f in fl:
                    fb = f.get('size_bytes',0) or 0
                    ln = f.get('language','Unknown') or 'Unknown'
                    fp = f.get('file_path','') or ''
                    is_v = f.get('is_vendor',False)
                    total_files += 1; total_bytes += fb
                    lang_bytes[ln] += fb; lang_files[ln] += 1
                    _, ext = os.path.splitext(fp); ext_low = ext.lower()
                    ext_bytes[ext_low] += fb; ext_files[ext_low] += 1
                    lang_ext_bytes[(ln, ext_low)] += fb
                    if EDA_PATH_KW.search(fp):
                        path_kw_bytes[ln] += fb; path_kw_files[ln] += 1
                    if is_v:
                        total_vendor_files += 1; total_vendor_bytes += fb
                        vendor_bytes[ln] += fb; vendor_files[ln] += 1
            dt = time.time() - t0; shards_scanned += 1
            if shards_scanned % 50 == 0 or shards_scanned <= 3:
                elapsed = time.time() - t_start
                eta = elapsed / shards_scanned * (len(shard_files) - shards_scanned)
                print(f'  [{shards_scanned}/{len(shard_files)}] {os.path.basename(sf)[:30]}... '
                      f'repos={n_repos} time={dt:.1f}s elapsed={elapsed:.0f}s ETA={eta:.0f}s', flush=True)
        except Exception as e:
            print(f'  ERROR on {os.path.basename(sf)}: {e}', flush=True)

    total_time = time.time() - t_start
    _write_meta_tsv(t_start, total_time, shards_scanned, total_repos, total_files, total_bytes,
                    total_vendor_files, total_vendor_bytes, lang_bytes, lang_files,
                    ext_bytes, ext_files, path_kw_bytes, path_kw_files,
                    vendor_bytes, vendor_files, lang_ext_bytes, out_prefix)
    print(f'\n{"="*60}')
    print(f'Phase A Complete: {shards_scanned} shards in {total_time:.0f}s')
    print(f'  Repos: {total_repos:,}  Files: {total_files:,}  Bytes: {total_bytes:,} ({total_bytes/1024**4:.2f} TiB)')
    print(f'  Vendor: {total_vendor_files:,} ({total_vendor_files/max(total_files,1)*100:.1f}%)')
    print(f'  Speed: {total_time/max(shards_scanned,1):.1f}s/shard')
    return {
        'shards_scanned': shards_scanned, 'total_repos': total_repos,
        'total_files': total_files, 'total_bytes': total_bytes,
        'total_vendor_files': total_vendor_files, 'total_vendor_bytes': total_vendor_bytes,
        'scan_time_s': round(total_time, 1),
        'speed_s_per_shard': round(total_time/max(shards_scanned,1), 1),
        'lang_bytes': dict(lang_bytes.most_common()),
        'lang_files': dict(lang_files.most_common()),
        'ext_bytes': dict(ext_bytes.most_common(50)),
        'path_kw_bytes': dict(path_kw_bytes.most_common()),
        'path_kw_files': dict(path_kw_files.most_common()),
        'vendor_bytes': dict(vendor_bytes.most_common(20)),
    }

def _write_meta_tsv(t_start, total_time, shards_scanned, total_repos, total_files, total_bytes,
                    total_vendor_files, total_vendor_bytes, lang_bytes, lang_files,
                    ext_bytes, ext_files, path_kw_bytes, path_kw_files,
                    vendor_bytes, vendor_files, lang_ext_bytes, out_prefix):
    tsv_path = os.path.join(OUT_DIR, f'{out_prefix}stackv3_eda_meta_stats.tsv')
    with open(tsv_path, 'w', newline='') as fout:
        w = csv.writer(fout, delimiter='\t')
        w.writerow(['# Phase A: Metadata Full Scan'])
        w.writerow(['# shards_scanned', shards_scanned])
        w.writerow(['# total_repos', total_repos])
        w.writerow(['# total_files', total_files])
        w.writerow(['# total_bytes', total_bytes])
        w.writerow(['# total_vendor_files', total_vendor_files])
        w.writerow(['# total_vendor_bytes', total_vendor_bytes])
        w.writerow(['# scan_time_s', round(total_time, 1)])
        w.writerow([])
        w.writerow(['# Section: Language Distribution'])
        w.writerow(['language','files','bytes','pct_files','pct_bytes'])
        for ln, b in lang_bytes.most_common():
            w.writerow([ln, lang_files[ln], b,
                f'{lang_files[ln]/max(total_files,1)*100:.2f}',
                f'{b/max(total_bytes,1)*100:.2f}'])
        w.writerow([])
        w.writerow(['# Section: Extension Distribution (top 50)'])
        w.writerow(['extension','files','bytes','pct_files','pct_bytes'])
        for ext, b in ext_bytes.most_common(50):
            w.writerow([ext, ext_files[ext], b,
                f'{ext_files[ext]/max(total_files,1)*100:.2f}',
                f'{b/max(total_bytes,1)*100:.2f}'])
        w.writerow([])
        w.writerow(['# Section: EDA Path Keyword Matches by Language'])
        w.writerow(['language','kw_files','kw_bytes','pct_of_lang_files','pct_of_lang_bytes'])
        for ln, b in path_kw_bytes.most_common():
            w.writerow([ln, path_kw_files[ln], b,
                f'{path_kw_files[ln]/max(lang_files.get(ln,1),1)*100:.2f}',
                f'{b/max(lang_bytes.get(ln,1),1)*100:.2f}'])
        w.writerow([])
        w.writerow(['# Section: Vendor by Language (top 20)'])
        w.writerow(['language','vendor_files','vendor_bytes'])
        for ln, b in vendor_bytes.most_common(20):
            w.writerow([ln, vendor_files[ln], b])
        w.writerow([])
        w.writerow(['# Section: Language x Extension (EDA-relevant, top 30)'])
        w.writerow(['language','extension','bytes'])
        eda_le = [(k,v) for k,v in lang_ext_bytes.items()
                  if k[0] in EDA_LANGS or k[1] in {'.tcl','.sdc','.il','.v','.sv','.sp','.svrf','.lib','.lef','.def'}]
        for (ln, ext), b in sorted(eda_le, key=lambda x: -x[1])[:30]:
            w.writerow([ln, ext, b])
    print(f'  Output: {tsv_path}')

def phase_b_detection(shard_files, seed=42, per_class_n=400, out_prefix=''):
    """Phase B: stratified content sampling with EDA script detection."""
    random.seed(seed)
    t_start = time.time()
    CATS = [
        ('Tcl', lambda ln, fp: ln == 'Tcl' or os.path.splitext(fp)[1].lower() in ('.tcl','.sdc','.xdc')),
        ('SKILL', lambda ln, fp: ln in ('SKILL','Other') or os.path.splitext(fp)[1].lower() == '.il'),
        ('Python-EDA', lambda ln, fp: ln == 'Python'),
        ('Perl', lambda ln, fp: ln == 'Perl' or os.path.splitext(fp)[1].lower() in ('.pl','.pls')),
        ('SVRF', lambda ln, fp: os.path.splitext(fp)[1].lower() == '.svrf' or any(k in fp.lower() for k in ['svrf','drc','lvs','.drc','.lvs'])),
        ('SPICE', lambda ln, fp: os.path.splitext(fp)[1].lower() in ('.sp','.spc','.cir') or any(k in fp.lower() for k in ['spice','netlist'])),
        ('Makeflow', lambda ln, fp: ln in ('Makefile','Shell') or os.path.splitext(fp)[1].lower() in ('.mk','.sh','.bash')),
        ('Verilog-SV', lambda ln, fp: ln in ('Verilog','SystemVerilog') or os.path.splitext(fp)[1].lower() in ('.v','.sv','.vh','.svh')),
        ('EDA-path-kw', lambda ln, fp: bool(EDA_PATH_KW.search(fp))),
    ]
    total_shards = len(shard_files)
    n_sample_shards = min(100, total_shards)
    shard_indices = sorted(set([int(i * total_shards / n_sample_shards) for i in range(n_sample_shards)]))
    sample_shards = [shard_files[i] for i in shard_indices if i < total_shards]
    print(f'Phase B: Scanning {len(sample_shards)} shards, n={per_class_n}, seed={seed}', flush=True)

    candidates = {cat: [] for cat, _ in CATS}
    max_pool = per_class_n * 5
    for si, sf in enumerate(sample_shards):
        t0 = time.time()
        try:
            pf = pq.ParquetFile(sf)
            tbl = pf.read(columns=['repo_path','files'])
            files_col = tbl.column('files').to_pylist()
            repo_col = tbl.column('repo_path').to_pylist()
            for i, fl in enumerate(files_col):
                if not fl: continue
                repo_p = repo_col[i] or ''
                for f in fl:
                    fb = f.get('size_bytes',0) or 0
                    if fb > 1048576 or fb == 0: continue
                    if f.get('is_vendor', False): continue
                    fp = f.get('file_path','') or ''
                    ln = f.get('language','Unknown') or 'Unknown'
                    content = f.get('content','') or ''
                    for cat, matcher in CATS:
                        if all(len(candidates[c]) >= max_pool for c, _ in CATS): break
                        if matcher(ln, fp) and len(candidates[cat]) < max_pool:
                            candidates[cat].append({'shard':os.path.basename(sf),'repo_path':repo_p,
                                'file_path':fp,'language':ln,'size_bytes':fb,'content':content})
                            break
        except Exception as e:
            print(f'  ERROR on {os.path.basename(sf)}: {e}', flush=True)
        dt = time.time() - t0
        if (si+1) % 10 == 0 or si == 0:
            counts = {k: len(v) for k, v in candidates.items()}
            print(f'  [{si+1}/{len(sample_shards)}] {os.path.basename(sf)[:30]}... time={dt:.1f}s {counts}', flush=True)
        if all(len(candidates[c]) >= max_pool for c, _ in CATS):
            print(f'  All at max_pool={max_pool}, stop early', flush=True); break

    print(f'\nPhase B: Detecting EDA scripts...', flush=True)
    all_samples = []; category_stats = {}
    for cat, _ in CATS:
        pool = candidates[cat]
        if not pool:
            category_stats[cat] = {'pool_size':0,'sampled':0,'eda_hits':0,'v1':0,'v2':0,'v3':0,
                'v1_bytes':0,'v2_bytes':0,'script_rate':0,'ci95':0}
            print(f'  {cat}: pool=0', flush=True); continue
        sample = random.sample(pool, per_class_n) if len(pool) > per_class_n else pool[:]
        eda_hits=0; v1c=0; v2c=0; v3c=0; v1b=0; v2b=0; sc=0
        for item in sample:
            cat_det, conf, hits = detect_eda_script(item['content'], item['language'], item['file_path'])
            dtype = classify_type(item['file_path'], item['language'])
            if dtype == 'script': sc += 1
            is_eda = cat_det not in ('other','doc','config','log','binary','skip')
            if is_eda: eda_hits += 1
            if is_eda and conf >= 0.5: v1c += 1; v1b += item['size_bytes']
            elif is_eda or (cat_det and 'maybe' in cat_det): v2c += 1; v2b += item['size_bytes']
            else: v3c += 1
            all_samples.append({'category':cat,'shard':item['shard'],'repo_path':item['repo_path'],
                'file_path':item['file_path'],'language':item['language'],'size_bytes':item['size_bytes'],
                'detected_category':cat_det,'confidence':round(conf,2),'hits':'|'.join(hits),
                'data_type':dtype,'value_layer':'V1' if (is_eda and conf>=0.5) else ('V2' if (is_eda or (cat_det and 'maybe' in cat_det)) else 'V3')})
        n = len(sample)
        category_stats[cat] = {'pool_size':len(pool),'sampled':n,'eda_hits':eda_hits,
            'eda_rate':round(eda_hits/max(n,1)*100,1),'v1':v1c,'v2':v2c,'v3':v3c,
            'v1_bytes':v1b,'v2_bytes':v2b,'script_rate':round(sc/max(n,1)*100,1),
            'ci95':round(1.96*(0.5*0.5/max(n,1))**0.5*100,1)}
        print(f'  {cat}: pool={len(pool)} n={n} eda={eda_hits}({eda_hits/max(n,1)*100:.1f}%) V1={v1c} V2={v2c} V3={v3c}', flush=True)

    total_time = time.time() - t_start
    sample_tsv = os.path.join(OUT_DIR, f'{out_prefix}stackv3_eda_sample.tsv')
    with open(sample_tsv, 'w', newline='') as fout:
        w = csv.writer(fout, delimiter='\t')
        w.writerow(['category','shard','repo_path','file_path','language','size_bytes',
            'detected_category','confidence','hits','data_type','value_layer'])
        for s in all_samples:
            w.writerow([s['category'],s['shard'],s['repo_path'],s['file_path'],s['language'],
                s['size_bytes'],s['detected_category'],s['confidence'],s['hits'],s['data_type'],s['value_layer']])
    summary_path = os.path.join(OUT_DIR, f'{out_prefix}stackv3_eda_value_summary.json')
    summary = {'phase_b': {'n_sample_shards':len(sample_shards),'seed':seed,
        'per_class_n':per_class_n,'scan_time_s':round(total_time,1),
        'category_stats':category_stats}, 'sample_tsv':sample_tsv}
    with open(summary_path, 'w') as fout:
        json.dump(summary, fout, indent=2, ensure_ascii=False, default=str)
    print(f'\nPhase B Complete: {total_time:.0f}s  TSV: {sample_tsv} ({len(all_samples)} rows)')
    return summary

def main():
    ap = argparse.ArgumentParser(description='stack-v3-train EDA Script Value Analysis')
    ap.add_argument('--phase', default='both', choices=['A','B','both','test'])
    ap.add_argument('--shards', default='all', help='all | N (number of shards)')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--per-class-n', type=int, default=400)
    ap.add_argument('--out-prefix', default='')
    args = ap.parse_args()
    all_parquets = get_all_parquets()
    print(f'Total parquet files: {len(all_parquets)}')
    if args.shards == 'all': shard_files = all_parquets
    elif args.shards.isdigit(): shard_files = all_parquets[:int(args.shards)]
    else: shard_files = all_parquets[:1]
    print(f'Using {len(shard_files)} shards')
    phase_a_result = None; phase_b_result = None
    if args.phase in ('A','both','test'):
        print(f'\n{"="*60}\nPhase A: Metadata Scan\n{"="*60}')
        phase_a_result = phase_a_meta_scan(shard_files, args.out_prefix)
    if args.phase in ('B','both') and args.phase != 'test':
        print(f'\n{"="*60}\nPhase B: Content Sampling & Detection\n{"="*60}')
        phase_b_result = phase_b_detection(shard_files, args.seed, args.per_class_n, args.out_prefix)
    if phase_a_result or phase_b_result:
        combined_path = os.path.join(OUT_DIR, f'{args.out_prefix}stackv3_eda_scan_result.json')
        with open(combined_path, 'w') as fout:
            json.dump({'phase_a': phase_a_result, 'phase_b': phase_b_result},
                      fout, indent=2, ensure_ascii=False, default=str)
        print(f'\nCombined results: {combined_path}')

if __name__ == '__main__':
    main()
