commit 2fe14fd74ede6ca61c9025dfc383ef06f6e89ecd
Author: paul.liu <paul.liu@cxmt.com>
Date:   Mon Oct 5 21:02:35 2026 +0800

    auto-commit 2026-10-05 21:02:35

diff --git a/doc/BaiZe-ISEDA2027/run/compile_p911_results.py b/doc/BaiZe-ISEDA2027/run/compile_p911_results.py
new file mode 100644
index 00000000..cc211110
--- /dev/null
+++ b/doc/BaiZe-ISEDA2027/run/compile_p911_results.py
@@ -0,0 +1,57 @@
+#!/usr/bin/env python3
+"""P-9.11: Compile hybrid vs dense results, compute ratios, output table."""
+import json, sys, os
+
+def load(path):
+    with open(path) as f: return json.load(f)
+
+def main():
+    hybrid_path = sys.argv[1] if len(sys.argv)>1 else 'p911_results_hybrid.json'
+    dense_path  = sys.argv[2] if len(sys.argv)>2 else 'p911_results_dense.json'
+    out_path    = sys.argv[3] if len(sys.argv)>3 else 'p911_compiled.json'
+    h = load(hybrid_path); d = load(dense_path)
+    hr = { (r['ctx'], r['batch']): r for r in h['results'] }
+    dr = { (r['ctx'], r['batch']): r for r in d['results'] }
+    cells = sorted(set(list(hr.keys())+list(dr.keys())))
+    table = []
+    for ctx, bs in cells:
+        hc = hr.get((ctx,bs),{}); dc = dr.get((ctx,bs),{})
+        herr = hc.get('error'); derr = dc.get('error')
+        row = {'ctx':ctx,'batch':bs}
+        for m, c, pfx in [('hybrid',hc,'h'), ('dense',dc,'d')]:
+            row[f'{pfx}_ttft'] = c.get('ttft_s')
+            row[f'{pfx}_prefill'] = c.get('prefill_tok_s')
+            row[f'{pfx}_decode'] = c.get('decode_tok_s')
+            row[f'{pfx}_e2e'] = c.get('e2e_latency_s')
+            row[f'{pfx}_vram'] = c.get('peak_vram_gb')
+            row[f'{pfx}_error'] = c.get('error')
+        # ratios: hybrid / dense (>1 = hybrid better)
+        if row['d_prefill'] and row['h_prefill'] and row['d_prefill']>0:
+            row['prefill_ratio'] = round(row['h_prefill']/row['d_prefill'], 2)
+        else: row['prefill_ratio'] = None
+        if row['d_decode'] and row['h_decode'] and row['d_decode']>0:
+            row['decode_ratio'] = round(row['h_decode']/row['d_decode'], 2)
+        else: row['decode_ratio'] = None
+        if row['d_vram'] and row['h_vram'] and row['d_vram']>0:
+            row['vram_ratio'] = round(row['h_vram']/row['d_vram'], 2)
+        else: row['vram_ratio'] = None
+        if row['d_e2e'] and row['h_e2e'] and row['d_e2e']>0:
+            row['e2e_ratio'] = round(row['h_e2e']/row['d_e2e'], 2)
+        else: row['e2e_ratio'] = None
+        if row['d_ttft'] and row['h_ttft'] and row['d_ttft']>0:
+            row['ttft_ratio'] = round(row['h_ttft']/row['d_ttft'], 2)
+        else: row['ttft_ratio'] = None
+        table.append(row)
+    # Print table
+    print(f"\n{'ctx':>7} {'bs':>3} {'h_TTFT':>8} {'d_TTFT':>8} {'ratio':>6} | {'h_pre':>8} {'d_pre':>8} {'ratio':>6} | {'h_dec':>8} {'d_dec':>8} {'ratio':>6} | {'h_VRAM':>7} {'d_VRAM':>7} {'ratio':>6} | {'h_e2e':>8} {'d_e2e':>8} {'ratio':>6}")
+    print('-'*155)
+    for r in table:
+        def fmt(v): return f'{v:>8}' if v is not None else f"{'OOM':>8}"
+        def fmtr(v): return f'{v:>6}' if v is not None else f"{'-':>6}"
+        def fmtg(v): return f'{v:>7}' if v is not None else f"{'OOM':>7}"
+        print(f"{r['ctx']:>7} {r['batch']:>3} {fmt(r['h_ttft'])} {fmt(r['d_ttft'])} {fmtr(r['ttft_ratio'])} | {fmt(r['h_prefill'])} {fmt(r['d_prefill'])} {fmtr(r['prefill_ratio'])} | {fmt(r['h_decode'])} {fmt(r['d_decode'])} {fmtr(r['decode_ratio'])} | {fmtg(r['h_vram'])} {fmtg(r['d_vram'])} {fmtr(r['vram_ratio'])} | {fmt(r['h_e2e'])} {fmt(r['d_e2e'])} {fmtr(r['e2e_ratio'])}")
+    output = {'experiment':'P-9.11','stack':'sglang','hybrid_model':'BaiZe Mamba2-hybrid 2.22B (nemotron_h)','dense_model':'MiniCPM5-2B dense GPT 2.51B (Llama)','table':table}
+    with open(out_path,'w') as f: json.dump(output,f,indent=2)
+    print(f"\n[done] compiled table saved to {out_path}")
+
+if __name__=='__main__': main()
