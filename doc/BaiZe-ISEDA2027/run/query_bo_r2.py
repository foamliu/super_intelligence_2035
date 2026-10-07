#!/usr/bin/env python3
"""Query BO Round 2 DB (mix_search_eval_r2.db).

CORRECT direction: score = lm_eval 8-task avg accuracy, HIGHER = BETTER.
Use ORDER BY score DESC for best/top-K.

Usage:
  python query_bo_r2.py                          # query on .29 (default DB path)
  python query_bo_r2.py /path/to/mix_search_eval_r2.db
  python query_bo_r2.py --topk 10                # show top-10 instead of top-5
"""
import sqlite3, sys, json, argparse

DEFAULT_DB = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search_eval_r2.db"


def main():
    p = argparse.ArgumentParser(description="Query BO R2 DB (score DESC = correct)")
    p.add_argument("db", nargs="?", default=DEFAULT_DB, help="Path to mix_search_eval_r2.db")
    p.add_argument("--topk", type=int, default=5, help="Number of top/bottom trials to show")
    args = p.parse_args()

    conn = sqlite3.connect(args.db)
    c = conn.cursor()

    # Schema check
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='trials'")
    schema = c.fetchone()
    if not schema:
        print(f"ERROR: table 'trials' not found in {args.db}")
        sys.exit(1)

    # Counts
    c.execute("SELECT COUNT(*) FROM trials WHERE status='complete'")
    n_complete = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trials")
    n_total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trials WHERE status='failed'")
    n_failed = c.fetchone()[0]

    print(f"DB: {args.db}")
    print(f"Trials: {n_complete} complete / {n_failed} failed / {n_total} total")
    print()

    # Score statistics
    c.execute("SELECT MIN(score), MAX(score), AVG(score) FROM trials WHERE status='complete'")
    smin, smax, savg = c.fetchone()
    print(f"Score stats (higher=better): MIN={smin:.4f}  MAX={smax:.4f}  AVG={savg:.4f}")
    print()

    # Top-K (CORRECT: score DESC = highest = best)
    print(f"=== Top-{args.topk} (ORDER BY score DESC — CORRECT, higher=better) ===")
    c.execute(
        "SELECT id, score, params, lm_eval_detail FROM trials "
        "WHERE status='complete' ORDER BY score DESC LIMIT ?",
        (args.topk,),
    )
    for r in c.fetchall():
        tid, score, params_json, detail = r
        params = json.loads(params_json)
        web = params.get("web", 0)
        code = params.get("code", 0)
        math_r = max(1.0 - web - code, 0.01)
        print(f"  t{tid}: score={score:.4f}  web={web:.4f} code={code:.4f} math={math_r:.4f}")

    print()
    # Bottom-K (for reference: score ASC = lowest = worst)
    print(f"=== Bottom-{args.topk} (ORDER BY score ASC — worst, for reference) ===")
    c.execute(
        "SELECT id, score, params FROM trials "
        "WHERE status='complete' ORDER BY score ASC LIMIT ?",
        (args.topk,),
    )
    for r in c.fetchall():
        tid, score, params_json = r
        params = json.loads(params_json)
        web = params.get("web", 0)
        code = params.get("code", 0)
        math_r = max(1.0 - web - code, 0.01)
        print(f"  t{tid}: score={score:.4f}  web={web:.4f} code={code:.4f} math={math_r:.4f}")

    conn.close()


if __name__ == "__main__":
    main()
