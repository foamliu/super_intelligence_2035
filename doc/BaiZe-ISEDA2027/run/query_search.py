#!/usr/bin/env python3
"""Query BO search results from SQLite."""
import sqlite3, json, sys, os

DB = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search.db"
if not os.path.exists(DB):
    print(f"DB not found: {DB}")
    sys.exit(1)

conn = sqlite3.connect(DB)
c = conn.cursor()

print("=== SCHEMA ===")
for r in c.execute("SELECT sql FROM sqlite_master WHERE type='table'"):
    print(r[0])

print("\n=== STATUS COUNTS ===")
for r in c.execute("SELECT status, COUNT(*) FROM trials GROUP BY status"):
    print(f"  {r[0]}: {r[1]}")

print("\n=== COMPLETED TRIALS (sorted by loss ASC) ===")
rows = list(c.execute(
    "SELECT id, status, loss, params, gpu FROM trials WHERE status='complete' ORDER BY loss ASC"))
for r in rows:
    p = json.loads(r[3])
    web = p.get("web", 0)
    code = p.get("code", 0)
    math = 1 - web - code
    print(f"  id={r[0]:4d} loss={r[2]:.4f} web={web:.4f} code={code:.4f} math={math:.4f} gpu={r[4]}")

print(f"\n  Total complete: {len(rows)}")

print("\n=== ALL TRIALS (by id) ===")
for r in c.execute("SELECT id, status, ROUND(loss,4) FROM trials ORDER BY id"):
    print(f"  {r[0]:4d} {r[1]:10s} loss={r[2]}")

# Prior point comparison
print("\n=== PRIOR POINT CHECK (88:8:4 => web=0.88, code=0.08) ===")
prior_rows = list(c.execute(
    "SELECT id, loss, params FROM trials WHERE status='complete' ORDER BY loss ASC"))
if prior_rows:
    best = prior_rows[0]
    best_p = json.loads(best[2])
    best_web = best_p.get("web", 0)
    best_code = best_p.get("code", 0)
    # Find closest to prior
    closest = None
    closest_dist = 999
    for row in prior_rows:
        p = json.loads(row[2])
        d = abs(p.get("web", 0) - 0.88) + abs(p.get("code", 0) - 0.08)
        if d < closest_dist:
            closest_dist = d
            closest = row
    if closest:
        cp = json.loads(closest[2])
        print(f"  Best trial: id={best[0]} loss={best[1]:.4f} web={best_web:.4f} code={best_code:.4f}")
        print(f"  Prior-like trial: id={closest[0]} loss={closest[1]:.4f} "
              f"web={cp.get('web',0):.4f} code={cp.get('code',0):.4f} (dist={closest_dist:.4f})")
        if best[1] is not None and closest[1] is not None:
            delta = closest[1] - best[1]
            print(f"  Delta (prior - best) = {delta:.4f}")

conn.close()
