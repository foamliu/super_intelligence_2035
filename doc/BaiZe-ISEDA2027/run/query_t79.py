#!/usr/bin/env python3
import sqlite3, json
c = sqlite3.connect("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search_eval.db")
r = c.execute("SELECT id,loss,params FROM trials WHERE id=79").fetchone()
p = json.loads(r[2])
w = p["web"]
co = p["code"]
ma = 1.0 - w - co
print("#{} loss={:.6f} web={:.4f} code={:.4f} math={:.4f}".format(r[0], r[1], w, co, ma))

# Also get #59 and #125 for completeness
for tid in [55, 59, 125]:
    r2 = c.execute("SELECT id,loss,params FROM trials WHERE id={}".format(tid)).fetchone()
    if r2:
        p2 = json.loads(r2[2])
        w2 = p2["web"]
        co2 = p2["code"]
        ma2 = 1.0 - w2 - co2
        print("#{} loss={:.6f} web={:.4f} code={:.4f} math={:.4f}".format(r2[0], r2[1], w2, co2, ma2))
c.close()
