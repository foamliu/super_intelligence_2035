#!/usr/bin/env python3
"""One-off inspection: GPIC tar key naming + corpus/mathtext probes."""
import tarfile, json, os

tar = "/nas_train/app.e0031982/datasets/baize-vision/smoke/shard-00000.tar"
print("=== GPIC tar members (first 10) ===")
tf = tarfile.open(tar)
seen = {}
for m in list(tf.getmembers())[:20]:
    base = m.name.split(".")[0]
    seen.setdefault(base, []).append(m.name)
for k, v in list(seen.items())[:4]:
    print(k, "->", v)
for m in tf.getmembers():
    if m.name.endswith(".json"):
        print("JSON sample:", json.loads(tf.extractfile(m).read()))
        break

print("=== /usr/share/dict/words ===", os.path.exists("/usr/share/dict/words"))
if os.path.exists("/usr/share/dict/words"):
    with open("/usr/share/dict/words") as f:
        wl = [w.strip() for w in f]
    print("word count:", len(wl), "sample:", wl[:5])

print("=== matplotlib mathtext probe ===")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(2, 1))
try:
    fig.text(0.5, 0.5, r"$\int_0^{\infty} e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}$", fontsize=12)
    fig.savefig("/tmp/_mt_probe.png", dpi=80)
    print("mathtext OK, size:", os.path.getsize("/tmp/_mt_probe.png"))
except Exception as e:
    print("mathtext FAIL:", e)

print("=== local text corpora candidates ===")
for p in ["/nas_train/app.e0031982/datasets", "/usr/share/dict"]:
    if os.path.isdir(p):
        print(p, "->", os.listdir(p)[:15])
