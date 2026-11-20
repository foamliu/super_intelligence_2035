#!/usr/bin/env python3
"""Query the BO study DB and dump summary for report generation."""
import sqlite3, json, sys

DB = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search_eval.db"

conn = sqlite3.connect(DB)

# Count by status
c = conn.execute(
    "SELECT COUNT(*), SUM(CASE WHEN status='complete' THEN 1 ELSE 0 END), "
    "SUM(CASE WHEN status!='complete' THEN 1 ELSE 0 END) FROM trials"
).fetchone()
print(f"Total={c[0]} complete={c[1]} other={c[2]}")

# Top 15
rows = conn.execute(
    "SELECT id, loss, params FROM trials WHERE status='complete' ORDER BY loss ASC LIMIT 15"
).fetchall()
print("\nTop-15 by loss:")
for r in rows:
    p = json.loads(r[2]) if r[2] else {}
    w = p.get("web", 0)
    co = p.get("code", 0)
    ma = 1.0 - w - co
    print(f"  #{r[0]:3d} loss={r[1]:.6f} web={w:.4f} code={co:.4f} math={ma:.4f}")

# Bottom 5
rows = conn.execute(
    "SELECT id, loss, params FROM trials WHERE status='complete' ORDER BY loss DESC LIMIT 5"
).fetchall()
print("\nBottom-5 by loss:")
for r in rows:
    p = json.loads(r[2]) if r[2] else {}
    w = p.get("web", 0)
    co = p.get("code", 0)
    ma = 1.0 - w - co
    print(f"  #{r[0]:3d} loss={r[1]:.6f} web={w:.4f} code={co:.4f} math={ma:.4f}")

# Prior 88:8:4
rows = conn.execute(
    "SELECT id, loss FROM trials WHERE status='complete' AND "
    "abs(json_extract(params,'$.web')-0.88)<0.002 AND "
    "abs(json_extract(params,'$.code')-0.08)<0.002 ORDER BY id"
).fetchall()
print("\nPrior ~88:8:4 trials:")
for r in rows:
    print(f"  #{r[0]:3d} loss={r[1]:.6f}")

# Stats
rows = conn.execute(
    "SELECT MIN(loss), MAX(loss), AVG(loss), COUNT(*) FROM trials WHERE status='complete'"
).fetchone()
print(f"\nStats: min={rows[0]:.6f} max={rows[1]:.6f} avg={rows[2]:.6f} n={rows[3]}")

# Distribution of web/code/math
rows = conn.execute(
    "SELECT json_extract(params,'$.web'), json_extract(params,'$.code') "
    "FROM trials WHERE status='complete'"
).fetchall()
import numpy as np
webs = [r[0] for r in rows]
codes = [r[1] for r in rows]
maths = [1.0 - r[0] - r[1] for r in rows]
print(f"\nweb:  min={min(webs):.4f} max={max(webs):.4f} mean={np.mean(webs):.4f} std={np.std(webs):.4f}")
print(f"code: min={min(codes):.4f} max={max(codes):.4f} mean={np.mean(codes):.4f} std={np.std(codes):.4f}")
print(f"math: min={min(maths):.4f} max={max(maths):.4f} mean={np.mean(maths):.4f} std={np.std(maths):.4f}")

# Best config
best = conn.execute(
    "SELECT id, loss, params FROM trials WHERE status='complete' ORDER BY loss ASC LIMIT 1"
).fetchone()
bp = json.loads(best[2])
bw = bp.get("web", 0)
bc = bp.get("code", 0)
bm = 1.0 - bw - bc
print(f"\nBest: #{best[0]} loss={best[1]:.6f} web={bw:.4f} code={bc:.4f} math={bm:.4f}")

conn.close()
