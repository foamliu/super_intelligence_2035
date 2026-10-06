#!/usr/bin/env python3
"""Query BO search sqlite DB for trial results."""
import sqlite3, json, sys

DB = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

# Status distribution
c.execute("SELECT status, count(*) FROM trials GROUP BY status")
print("STATUS DIST:", c.fetchall())

c.execute("SELECT count(*) FROM trials")
total = c.fetchone()[0]
print(f"TOTAL: {total}")

# Top 10 by loss (complete only)
print("\nTOP 10 by loss (status=complete):")
for r in c.execute("SELECT id, params, loss, status FROM trials WHERE status='complete' ORDER BY loss ASC LIMIT 10"):
    p = json.loads(r[1]) if r[1] else {}
    w = p.get("web", 0)
    co = p.get("code", 0)
    m = p.get("math", 0)
    print(f"  #{r[0]:3d} web={w:.4f} code={co:.4f} math={m:.4f} loss={r[2]:.4f}")

# Last 10 by id
print("\nLAST 10 by id:")
for r in c.execute("SELECT id, params, loss, status FROM trials ORDER BY id DESC LIMIT 10"):
    p = json.loads(r[1]) if r[1] else {}
    w = p.get("web", 0)
    co = p.get("code", 0)
    m = p.get("math", 0)
    print(f"  #{r[0]:3d} web={w:.4f} code={co:.4f} math={m:.4f} loss={r[2]} status={r[3]}")

# Prior (88:8:4) nearest
print("\nPRIOR (88:8:4) nearest complete trials:")
rows = []
for r in c.execute("SELECT id, params, loss, status FROM trials WHERE status='complete'"):
    p = json.loads(r[1]) if r[1] else {}
    w = p.get("web", 0)
    co = p.get("code", 0)
    m = p.get("math", 0)
    dist = abs(w - 0.88) + abs(co - 0.08)
    rows.append((dist, r[0], w, co, m, r[2]))
rows.sort()
for dist, tid, w, co, m, loss in rows[:5]:
    print(f"  #{tid:3d} web={w:.4f} code={co:.4f} math={m:.4f} loss={loss:.4f} dist={dist:.4f}")

# All complete trials sorted by loss (for best-so-far curve)
print("\nALL COMPLETE trials sorted by loss:")
all_rows = []
for r in c.execute("SELECT id, params, loss FROM trials WHERE status='complete' ORDER BY loss ASC"):
    p = json.loads(r[1]) if r[1] else {}
    all_rows.append((r[0], p.get("web", 0), p.get("code", 0), p.get("math", 0), r[2]))
print(f"  Count: {len(all_rows)}")
if all_rows:
    best = all_rows[0]
    print(f"  BEST: #{best[0]} web={best[1]:.4f} code={best[2]:.4f} math={best[3]:.4f} loss={best[4]:.4f}")
    # Rank of prior
    for i, (tid, w, co, m, loss) in enumerate(all_rows):
        if abs(w - 0.88) + abs(co - 0.08) < 0.05:
            print(f"  PRIOR nearest #{tid} rank={i+1}/{len(all_rows)} loss={loss:.4f}")
            break

conn.close()
