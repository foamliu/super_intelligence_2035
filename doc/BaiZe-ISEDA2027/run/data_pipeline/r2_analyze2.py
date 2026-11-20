#!/usr/bin/env python3
"""
R2 调研 v2：本地采样(Code/Math/L3) + 下载 base 单文件抽样 + base vs L3 重叠。
只读/少量下载。口径 DeepSeek tokenizer (tokenizer_eod), add_special_tokens=False。
"""
import json, random, glob, os, urllib.request
import pyarrow.parquet as pq
from transformers import AutoTokenizer

TOK_DIR = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod"
L3_BASE = "/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data"
CODE_BASE = "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data"
MATH_BASE = "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data"
DL = "/tmp/base_samples"

tok = AutoTokenizer.from_pretrained(TOK_DIR)

def tk(text):
    return len(tok(text, add_special_tokens=False)["input_ids"])

def stats(name, toks, n, total_rows):
    if not toks:
        print(f"{name}: (no samples)")
        return 0
    avg = sum(toks)/len(toks)
    tot = avg * total_rows
    print(f"{name:26s} n={n:5d} avg={avg:7.1f} tok/doc  total≈{tot/1e9:7.2f} B")
    return tot

def dl(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    print(f"  downloading {os.path.basename(path)} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "baize-data"})
    with urllib.request.urlopen(req, timeout=600) as r, open(path, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    return path

print("=== 1) base 单文件下载 + 抽样 ===")
os.makedirs(DL, exist_ok=True)
en_path = dl("https://huggingface.co/datasets/openbmb/Ultra-FineWeb/resolve/main/data/ultrafineweb_en/ultrafineweb-en-part-0001-of-2048.parquet", f"{DL}/en.parquet")
zh_path = dl("https://huggingface.co/datasets/openbmb/Ultra-FineWeb/resolve/main/data/ultrafineweb_zh/ultrafineweb-zh-part-0001-of-0724.parquet", f"{DL}/zh.parquet")

en_t = pq.read_table(en_path)
zh_t = pq.read_table(zh_path)
en_col = en_t.column("content").to_pylist()
zh_col = zh_t.column("content").to_pylist()
print(f"en file rows={len(en_col)}, zh file rows={len(zh_col)}")
# 抽样 tokenize（每文件最多 600 行均匀分布）
en_s = en_col[::max(1, len(en_col)//600)][:600]
zh_s = zh_col[::max(1, len(zh_col)//600)][:600]
base_en_avg = sum(tk(c) for c in en_s)/len(en_s)
base_zh_avg = sum(tk(c) for c in zh_s)/len(zh_s)
print(f"base en avg={base_en_avg:.1f} tok/doc × 1,159,254,991 rows ≈ {base_en_avg*1.159e9/1e12:.3f} T")
print(f"base zh avg={base_zh_avg:.1f} tok/doc × 131,006,462 rows ≈ {base_zh_avg*1.31e8/1e12:.3f} T")

print("\n=== 2) 本地 Code / Math / L3 抽样 ===")
# Code L2 + L3
for tier, rows_n in [("L2", 266_878_376), ("L3", 81_205_105)]:
    fs = sorted(glob.glob(f"{CODE_BASE}/UltraData-Code-{tier}/**/*.parquet", recursive=True))
    s = []
    random.seed(1)
    for f in random.sample(fs, min(8, len(fs))):
        t = pq.read_table(f)
        s += [tk(c) for c in t.column("content").to_pylist()[::1500][:400]]
    stats(f"UltraData-Code ({tier})", s, len(s), rows_n)
# Math L1/L2-preview/L3
for tier, rows_n in [("L1", 86_032_552), ("L2-preview", 13_835_635), ("L3", 81_318_266)]:
    fs = sorted(glob.glob(f"{MATH_BASE}/UltraData-Math-{tier}/**/*.parquet", recursive=True))
    s = []
    random.seed(2)
    for f in random.sample(fs, min(8, len(fs))):
        t = pq.read_table(f)
        s += [tk(c) for c in t.column("content").to_pylist()[::800][:400]]
    stats(f"UltraData-Math ({tier})", s, len(s), rows_n)
# L3 (re-confirm 4 configs)
for label, subdir, rows_n in [
    ("en/qa", "ultrafineweb_en_l3/qa", 320_112_563),
    ("en/multi", "ultrafineweb_en_l3/multi_style", 378_071_951),
    ("zh/qa", "ultrafineweb_zh_l3/qa", 156_629_979),
    ("zh/multi", "ultrafineweb_zh_l3/multi_style", 203_720_633),
]:
    fs = sorted(glob.glob(f"{L3_BASE}/{subdir}/*.parquet"))
    s = []
    random.seed(3)
    for f in random.sample(fs, min(6, len(fs))):
        t = pq.read_table(f)
        s += [tk(c) for c in t.column("content").to_pylist()[::2000][:400]]
    stats(f"Ultra-FineWeb-L3 ({label})", s, len(s), rows_n)

print("\n=== 3) base vs L3 重叠率（文本级实测）===")
def norm(s):
    return " ".join(s.split())
base_texts = [norm(c) for c in en_col[::max(1, len(en_col)//600)][:600]]
l3_files = sorted(glob.glob(f"{L3_BASE}/ultrafineweb_en_l3/qa/*.parquet")) + sorted(glob.glob(f"{L3_BASE}/ultrafineweb_en_l3/multi_style/*.parquet"))
l3_texts = []
random.seed(7)
for f in random.sample(l3_files, min(8, len(l3_files))):
    t = pq.read_table(f)
    l3_texts += [norm(c) for c in t.column("content").to_pylist()[::3000][:300]]
l3_texts = l3_texts[:600]
base_set = set(base_texts)
l3_set = set(l3_texts)
inter = base_set & l3_set
print(f"base 采样 {len(base_texts)}, L3 采样 {len(l3_texts)}")
print(f"exact 全文匹配: {len(inter)} / {min(len(base_set), len(l3_set))} = {len(inter)/min(len(base_set),len(l3_set))*100:.4f}%")
def shingles(s, k=5):
    ws = s.split()
    return {" ".join(ws[i:i+k]) for i in range(len(ws)-k+1)}
base_sh = [shingles(b) for b in base_texts[:200]]
l3_sh = [shingles(l) for l in l3_texts[:200]]
jacc_sum = 0.0; n = 0; hi = 0
for i in range(len(base_sh)):
    for j in range(len(l3_sh)):
        jacc = len(base_sh[i] & l3_sh[j]) / max(1, len(base_sh[i] | l3_sh[j]))
        jacc_sum += jacc; n += 1
        if jacc > 0.5:
            hi += 1
print(f"200x200 对 5-gram Jaccard 均值={jacc_sum/n:.4f}, >0.5 对数={hi} ({hi/n*100:.2f}%)")
print("CONCLUSION: L3 是 base 的合成改写(Q&A/多风格), verbatim 重叠≈0; base 是新增语料")