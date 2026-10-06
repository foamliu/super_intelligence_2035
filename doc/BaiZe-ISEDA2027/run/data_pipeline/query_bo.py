#!/usr/bin/env python3
"""Query BO search SQLite DB for trial stats and top results."""
import sqlite3, json, sys

DB = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Stats
cur.execute("SELECT status, count(*) FROM trials GROUP BY status")
print("STATUS COUNTS:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")
cur.execute("SELECT count(*) FROM trials")
total = cur.fetchone()[0]
complete = 0
pruned = 0
running = 0
fail = 0
cur.execute("SELECT status, count(*) FROM trials GROUP BY status")
for r in cur.fetchall():
    s = r[0].lower()
    if s == "complete":
        complete = r[1]
    elif s == "pruned":
        pruned = r[1]
    elif s == "running":
        running = r[1]
    elif s == "fail":
        fail = r[1]
print(f"TOTAL={total} COMPLETE={complete} PRUNED={pruned} RUNNING={running} FAIL={fail}")

# Top 10 by loss (COMPLETE only)
cur.execute("""
SELECT id, params, loss, status FROM trials
WHERE status='complete' AND loss IS NOT NULL ORDER BY loss ASC LIMIT 10""")
print("\n--- TOP 10 (complete, loss ASC) ---")
for r in cur.fetchall():
    params = json.loads(r[1]) if r[1] else {}
    web = params.get("web", 0)
    code = params.get("code", 0)
    math_r = round(1.0 - web - code, 4) if isinstance(web, (int, float)) and isinstance(code, (int, float)) else "?"
    print(f"  #{r[0]:3d} loss={r[2]:.4f} web={web:.4f} code={code:.4f} math={math_r}")

# All complete trials sorted by loss, with prior point check
cur.execute("""
SELECT id, params, loss, status FROM trials
WHERE status='complete' AND loss IS NOT NULL ORDER BY loss ASC""")
all_trials = cur.fetchall()
print(f"\n--- ALL COMPLETE TRIALS (sorted by loss): {len(all_trials)} ---")
prior_rank = None
prior_loss = None
for i, r in enumerate(all_trials):
    params = json.loads(r[1]) if r[1] else {}
    web = params.get("web", 0)
    code = params.get("code", 0)
    dist = abs(web - 0.88) + abs(code - 0.08)
    mark = " <<<< PRIOR(88:8:4)?" if dist < 0.01 else ""
    if dist < 0.01 and prior_rank is None:
        prior_rank = i + 1
        prior_loss = r[2]
    print(f"  rank{i+1:3d} #{r[0]:3d} loss={r[2]:.4f} web={web:.4f} code={code:.4f}{mark}")

if prior_rank:
    best_loss = all_trials[0][2]
    delta = prior_loss - best_loss
    print(f"\n--- PRIOR POINT (88:8:4) ---")
    print(f"  rank={prior_rank}/{len(all_trials)} loss={prior_loss:.4f}")
    print(f"  best={best_loss:.4f} (trial #{all_trials[0][0]})")
    print(f"  delta={delta:.4f} ({delta/best_loss*100:.1f}% worse than best)")

conn.close()
