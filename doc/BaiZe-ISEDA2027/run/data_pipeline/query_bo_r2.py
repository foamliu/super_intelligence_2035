#!/usr/bin/env python3
"""Query Round2 BO DB (mix_search_eval_r2.db).

⚠️ DIRECTION: R2 objective = lm_eval 8-task avg ACCURACY → HIGHER = BETTER.
   (R1 used val-loss → lower=better; do NOT copy R1's ORDER BY ... ASC here!)
   Correct sort: ORDER BY score DESC.
"""
import sqlite3, json, sys

DB = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search_eval_r2.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

# Stats
c.execute("SELECT status, count(*) FROM trials GROUP BY status")
print("STATUS COUNTS:", c.fetchall())
c.execute("SELECT count(*) FROM trials")
total = c.fetchone()[0]
print(f"TOTAL: {total}")

# Top 10 by score DESC (HIGHER = BETTER for accuracy)
print("\n--- TOP 10 (complete, score DESC = TRUE best) ---")
for r in c.execute("""
    SELECT id, params, score, lm_eval_detail FROM trials
    WHERE status='complete' AND score IS NOT NULL ORDER BY score DESC LIMIT 10"""):
    p = json.loads(r[1]) if r[1] else {}
    web = p.get("web", 0)
    code = p.get("code", 0)
    math_r = round(1.0 - web - code, 4) if isinstance(web, (int, float)) and isinstance(code, (int, float)) else "?"
    detail = json.loads(r[3]) if r[3] else {}
    print(f"  #{r[0]:3d} score={r[2]:.6f} web={web:.4f} code={code:.4f} math={math_r}")
    if detail:
        print(f"         detail: {detail}")

# Bottom 5 (for reference — these are the WORST)
print("\n--- BOTTOM 5 (complete, score ASC = worst) ---")
for r in c.execute("""
    SELECT id, params, score FROM trials
    WHERE status='complete' AND score IS NOT NULL ORDER BY score ASC LIMIT 5"""):
    p = json.loads(r[1]) if r[1] else {}
    web = p.get("web", 0)
    code = p.get("code", 0)
    math_r = round(1.0 - web - code, 4)
    print(f"  #{r[0]:3d} score={r[2]:.6f} web={web:.4f} code={code:.4f} math={math_r}")

# Score distribution
c.execute("SELECT MIN(score), MAX(score), AVG(score) FROM trials WHERE status='complete' AND score IS NOT NULL")
mn, mx, avg = c.fetchone()
print(f"\nScore range: {mn:.4f} - {mx:.4f} (avg={avg:.4f}, spread={mx-mn:.4f})")

# Prior (88:8:4) nearest
print("\nPRIOR (88:8:4) nearest complete trials:")
rows = []
for r in c.execute("SELECT id, params, score FROM trials WHERE status='complete'"):
    p = json.loads(r[1]) if r[1] else {}
    w = p.get("web", 0)
    co = p.get("code", 0)
    dist = abs(w - 0.88) + abs(co - 0.08)
    rows.append((dist, r[0], w, co, r[2]))
rows.sort()
for dist, tid, w, co, score in rows[:5]:
    print(f"  #{tid:3d} score={score:.4f} web={w:.4f} code={co:.4f} dist={dist:.4f}")

conn.close()
