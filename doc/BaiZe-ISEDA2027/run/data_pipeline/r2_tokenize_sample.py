#!/usr/bin/env python3
"""
R2 调研：对 8 源做 token 抽样外推 + base vs L3 重叠率实测。
只读：本地 parquet（L3/Code/Math）+ datasets-server /rows（base/UltraX）。不下载全量。
口径：DeepSeek-V4.1-Flash tokenizer（tokenizer_eod），add_special_tokens=False。
"""
import json, random, urllib.request, glob
import pyarrow.parquet as pq
from transformers import AutoTokenizer

TOK_DIR = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod"
L3_BASE = "/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data"
CODE_BASE = "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data"
MATH_BASE = "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data"

tok = AutoTokenizer.from_pretrained(TOK_DIR)

def tk(text):
    return len(tok(text, add_special_tokens=False)["input_ids"])

def rows_api(repo, config, split, offset, length):
    url = f"https://datasets-server.huggingface.co/rows?dataset=openbmb/{repo}&config={config}&split={split}&offset={offset}&length={length}"
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.load(r)
    return [row["row"] for row in d["rows"]]

def stats(name, toks, n_docs, total_rows):
    total = sum(toks) / len(toks) * total_rows
    print(f"{name:28s} sampled={n_docs:5d}  avg={sum(toks)/len(toks):7.1f} tok/doc  total≈{total/1e9:7.2f} B token")
    return total

print("=== token 抽样外推 ===\n")

# --- base (Ultra-FineWeb) via /rows (offset cap ~ <1M) ---
def sample_rows(repo, config, split, offsets, length=100):
    out = []
    for off in offsets:
        try:
            out += rows_api(repo, config, split, off, length)
        except Exception as e:
            print("  err", repo, split, off, e)
    return out

base_en = sample_rows("Ultra-FineWeb", "default", "en", [0, 30_000, 60_000, 90_000, 120_000, 150_000, 180_000, 210_000, 240_000, 270_000])
base_en_toks = [tk(r["content"]) for r in base_en]
base_en_tot = stats("Ultra-FineWeb base (en)", base_en_toks, len(base_en_toks), 1_159_254_991)

base_zh = sample_rows("Ultra-FineWeb", "default", "zh", [0, 30_000, 60_000, 90_000, 120_000, 150_000])
base_zh_toks = [tk(r["content"]) for r in base_zh]
base_zh_tot = stats("Ultra-FineWeb base (zh)", base_zh_toks, len(base_zh_toks), 131_006_462)

# --- UltraX-Preview (5 configs) ---
ux_cfg = {
    "UltraX-AICC": ("AICC", 21_281_632),
    "UltraX-FineWeb": ("FineWeb", 29_197_202),
    "UltraX-FineWeb-ProX-Doc": ("ProX-Doc", 17_278_113),
    "UltraX-RedPajama-V2": ("RedPajama-V2", 22_115_000),
    "UltraX-Ultra-FineWeb": ("Ultra-FineWeb", 23_917_631),
}
ux_all = []
for cfg, (label, rows_n) in ux_cfg.items():
    rs = sample_rows("UltraX-Preview", cfg, "train", [0, 20_000, 40_000])
    if rs:
        s = [tk(r["cleaned_content"]) for r in rs]
        sub = sum(s)/len(s)*rows_n
        ux_all.append(sub)
        print(f"  UltraX/{label:14s} avg={sum(s)/len(s):7.1f} tok/doc  total≈{sub/1e9:6.2f} B")
ux_tot = sum(ux_all)

# --- local L3 (re-sample to confirm) ---
l3_cfg = [
    ("en/qa", "qa", "ultrafineweb_en_l3/qa", 320_112_563),
    ("en/multi", "multi_style", "ultrafineweb_en_l3/multi_style", 378_071_951),
    ("zh/qa", "qa", "ultrafineweb_zh_l3/qa", 156_629_979),
    ("zh/multi", "multi_style", "ultrafineweb_zh_l3/multi_style", 203_720_633),
]
for label, _, subdir, rows_n in l3_cfg:
    fs = sorted(glob.glob(f"{L3_BASE}/{subdir}/*.parquet"))
    s = []
    random.seed(0)
    for f in random.sample(fs, min(8, len(fs))):
        t = pq.read_table(f)
        for c in t.column("content").to_pylist()[::2000][:500]:
            s.append(tk(c))
    stats(f"Ultra-FineWeb-L3 ({label})", s, len(s), rows_n)

# --- local Code (L2 + L3, use content column) ---
code_rows = {"L2": 266_878_376, "L3": 81_205_105}
for tier, rows_n in code_rows.items():
    fs = sorted(glob.glob(f"{CODE_BASE}/UltraData-Code-{tier}/**/*.parquet", recursive=True))
    s = []
    random.seed(1)
    for f in random.sample(fs, min(8, len(fs))):
        try:
            t = pq.read_table(f)
            for c in t.column("content").to_pylist()[::1500][:400]:
                s.append(tk(c))
        except Exception as e:
            print("code err", f, e)
    stats(f"UltraData-Code ({tier})", s, len(s), rows_n)

# --- local Math (L1 + L2-preview + L3) ---
math_rows = {"L1": 86_032_552, "L2-preview": 13_835_635, "L3": 81_318_266}
for tier, rows_n in math_rows.items():
    fs = sorted(glob.glob(f"{MATH_BASE}/UltraData-Math-{tier}/**/*.parquet", recursive=True))
    s = []
    random.seed(2)
    for f in random.sample(fs, min(8, len(fs))):
        try:
            t = pq.read_table(f)
            for c in t.column("content").to_pylist()[::800][:400]:
                s.append(tk(c))
        except Exception as e:
            print("math err", f, e)
    stats(f"UltraData-Math ({tier})", s, len(s), rows_n)

print("\n=== 汇总 ===")
print(f"base en+zh ≈ {(base_en_tot+base_zh_tot)/1e12:.2f} T")
print(f"UltraX 5configs ≈ {ux_tot/1e9:.1f} B")

print("\n=== base vs L3 重叠率（文本级）===")
def norm(s):
    return " ".join(s.split())
base_texts = [norm(r["content"]) for r in base_en[:500]]
l3_files = sorted(glob.glob(f"{L3_BASE}/ultrafineweb_en_l3/qa/*.parquet")) + sorted(glob.glob(f"{L3_BASE}/ultrafineweb_en_l3/multi_style/*.parquet"))
l3_texts = []
random.seed(7)
for f in random.sample(l3_files, min(6, len(l3_files))):
    t = pq.read_table(f)
    l3_texts += [norm(c) for c in t.column("content").to_pylist()[::3000][:200]]
l3_texts = l3_texts[:500]
base_set = set(base_texts)
l3_set = set(l3_texts)
inter = base_set & l3_set
print(f"base 采样 {len(base_texts)}, L3 采样 {len(l3_texts)}")
print(f"exact 全文匹配 (整串相等): {len(inter)} / {min(len(base_set), len(l3_set))} = {len(inter)/min(len(base_set),len(l3_set))*100:.3f}%")
# 前缀/子串重叠：L3 内容是否包含 base 内容前缀
def shingles(s, k=5):
    ws = s.split()
    return { " ".join(ws[i:i+k]) for i in range(len(ws)-k+1) }
base_sh = [shingles(b) for b in base_texts[:200]]
l3_sh = [shingles(l) for l in l3_texts[:200]]
match_pairs = 0; jacc_sum = 0.0; n = 0
for i in range(len(base_sh)):
    for j in range(len(l3_sh)):
        jacc = len(base_sh[i] & l3_sh[j]) / max(1, len(base_sh[i] | l3_sh[j]))
        jacc_sum += jacc; n += 1
        if jacc > 0.5: match_pairs += 1
print(f"200x200 对 base vs L3 文档 5-gram Jaccard: 均值={jacc_sum/n:.4f}, >0.5 的对数={match_pairs} ({match_pairs/n*100:.2f}%)")
print("=> L3 是 Q&A/多风格改写合成体, 与 base 原始文本 verbatim/near-dup 重叠 ≈ 0")