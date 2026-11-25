#!/usr/bin/env python3
"""R2000 cline special report - HTML generator (reads data from pickle)."""
import pickle, os

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
with open("/tmp/cline_r2000_data.pkl", "rb") as pf:
    D = pickle.load(pf)

HARNESSES = D["HARNESSES"]; eval_data = D["eval_data"]; pred_data = D["pred_data"]
tb21_all = D["tb21_all"]; ROUND = D["ROUND"]; NOW = D["NOW"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}

sw_rows = ""
for h in HARNESSES:
    dn = DISPLAY.get(h, h)
    r, n = eval_data.get(dn, (0, 0))
    t, rp = pred_data.get(dn, (0, 0))
    sw_rows += f"<tr><td>{dn}</td><td>{r}</td><td>{n}</td><td>{100*r/max(n,1):.1f}%</td><td>{t}</td><td>{100*rp/max(t,1):.1f}%</td></tr>\n"

tb21_rows = ""
for dn in ["cline","codex","hermes","opencode","claude-code","deepseek","pi"]:
    d, p = tb21_all.get(dn, (0, 0))
    tb21_rows += f"<tr><td>{dn}</td><td>{p}</td><td>{d}</td><td>{100*p/max(d,1):.1f}%</td></tr>\n"

ct, cr, ce = D["cline_total"], D["cline_real"], D["cline_empty"]
cr_eval, cn_eval = D["cr"], D["cn"]
tcd, tcp = D["tb21_cline_done"], D["tb21_cline_pass"]
ttd, ttp = D["tb21_total_d"], D["tb21_total_p"]
empty_str = D["empty_str"]
op_r, op_n = eval_data.get("opencode", (0, 0))

with open("/tmp/cline_r2000_rows.pkl", "wb") as pf:
    pickle.dump(dict(sw_rows=sw_rows, tb21_rows=tb21_rows, ct=ct, cr=cr, ce=ce,
                     cr_eval=cr_eval, cn_eval=cn_eval, tcd=tcd, tcp=tcp,
                     ttd=ttd, ttp=ttp, empty_str=empty_str, op_r=op_r, op_n=op_n,
                     NOW=NOW, ROUND=ROUND), pf)
print("Rows prepared. Ready for HTML generation.")
