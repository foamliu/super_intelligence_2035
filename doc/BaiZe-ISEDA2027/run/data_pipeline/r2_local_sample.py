#!/usr/bin/env python3
"""R2 本地采样（Code/Math/L3）+ base /first-rows 单次取样的 token 与 overlap 实测。"""
import json, random, glob, time, urllib.request
import pyarrow.parquet as pq
from transformers import AutoTokenizer

TOK_DIR = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod"
L3_BASE = "/nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data"
CODE_BASE = "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data"
MATH_BASE = "/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data"

tok = AutoTokenizer.from_pretrained(TOK_DIR)
def tk(t): return len(tok(t, add_special_tokens=False)["input_ids"])
def stats(name, s, n, rows):
    if not s: print(f"{name}: no samples"); return 0
    avg = sum(s)/len(s); tot = avg*rows
    print(f"{name:26s} n={n:5d} avg={avg:7.1f} tok/doc total~{tot/1e9:7.2f} B")
    return tot

print("=== 1) Local Code/Math/L3 ===")
for tier, rows in [("L2",266_878_376),("L3",81_205_105)]:
    fs = sorted(glob.glob(f"{CODE_BASE}/UltraData-Code-{tier}/**/*.parquet", recursive=True))
    s=[]; random.seed(1)
    for f in random.sample(fs, min(8,len(fs))):
        t=pq.read_table(f); s += [tk(c) for c in t.column("content").to_pylist()[::1500][:400]]
    stats(f"Code({tier})", s, len(s), rows)
for tier, rows in [("L1",86_032_552),("L2-preview",13_835_635),("L3",81_318_266)]:
    fs = sorted(glob.glob(f"{MATH_BASE}/UltraData-Math-{tier}/**/*.parquet", recursive=True))
    s=[]; random.seed(2)
    for f in random.sample(fs, min(8,len(fs))):
        t=pq.read_table(f); s += [tk(c) for c in t.column("content").to_pylist()[::800][:400]]
    stats(f"Math({tier})", s, len(s), rows)
for label, sub, rows in [("en/qa","ultrafineweb_en_l3/qa",320_112_563),("en/multi","ultrafineweb_en_l3/multi_style",378_071_951),("zh/qa","ultrafineweb_zh_l3/qa",156_629_979),("zh/multi","ultrafineweb_zh_l3/multi_style",203_720_633)]:
    fs = sorted(glob.glob(f"{L3_BASE}/{sub}/*.parquet"))
    s=[]; random.seed(3)
    for f in random.sample(fs, min(6,len(fs))):
        t=pq.read_table(f); s += [tk(c) for c in t.column("content").to_pylist()[::2000][:400]]
    stats(f"L3({label})", s, len(s), rows)

print("\n=== 2) base /first-rows 取样（en 前 100 行）===")
def first_rows(repo, config, split, tries=3):
    url = f"https://datasets-server.huggingface.co/first-rows?dataset=openbmb/{repo}&config={config}&split={split}"
    for a in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)["rows"]
        except Exception as e:
            print(f"  retry {a} err {e}"); time.sleep(5)
    return None
rows = first_rows("Ultra-FineWeb", "default", "en")
if rows:
    base_texts = [" ".join(r["row"]["content"].split()) for r in rows]
    base_toks = [tk(c) for c in base_texts]
    print(f"base en 样本 {len(base_toks)}  avg={sum(base_toks)/len(base_toks):.1f} tok/doc  (~1T/1.159B rows={1000/1.159:.0f} 期望)")
    # overlap with L3
    l3_files = sorted(glob.glob(f"{L3_BASE}/ultrafineweb_en_l3/qa/*.parquet"))
    l3_texts=[]
    random.seed(7)
    for f in random.sample(l3_files, min(4,len(l3_files))):
        t=pq.read_table(f); l3_texts += [" ".join(c.split()) for c in t.column("content").to_pylist()[::3000][:200]]
    def sh(s,k=5):
        w=s.split(); return {" ".join(w[i:i+k]) for i in range(len(w)-k+1)}
    bsh=[sh(x) for x in base_texts]; lsh=[sh(x) for x in l3_texts]
    js=0.0; n=0; exact=len(set(base_texts)&set(l3_texts[:len(base_texts)]))
    for i in range(len(bsh)):
        for j in range(len(lsh)):
            js += len(bsh[i]&lsh[j])/max(1,len(bsh[i]|lsh[j])); n+=1
    print(f"base 100 vs L3 {len(l3_texts)}: exact全文匹配={exact} ({exact/min(len(base_texts),len(l3_texts))*100:.2f}%), 5-gram Jaccard 均值={js/n:.4f}")
else:
    print("first-rows 不可用（可能限流），base token 用 README 权威值 1T en")
print("\nDONE")