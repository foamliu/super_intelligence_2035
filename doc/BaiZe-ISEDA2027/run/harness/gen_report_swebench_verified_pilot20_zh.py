#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 SWE-bench Verified 20 条试点横评报告（中文 HTML，自包含）。

按 BAIZE_HARNESS_TASK.md 运维令 2026-10-27 08:3x part②：
  「先 cline + hermes 各 smoke 1 条验通 → 再各跑 20 条试点 → 报初步 resolve 结果
   （三列 resolved/failed/infra-or-quota + 结论），供运维放大决策。」

数据来源（全部可溯源，不编造）：
  - reports/eval_{harness}.json          —— eval 阶段汇总（resolved/failed/infra_or_quota）
  - reports/predict_{harness}.json       —— predict 阶段逐题分类
  - predictions/{harness}__{iid}.json    —— 逐题 patch（model_patch 长度）
  - verified_20_ids.txt                  —— 20 条 instance_id 清单
  - enriched_20.json                     —— 每题 repo / base_commit / difficulty

命名规程：报告正文一律写 `cline`（不写 cline-patched）；代码标识符不改。
"""
from __future__ import annotations
import html
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PILOT = HERE / "swebench_verified_pilot"
REPORT_DIR = PILOT / "reports"
PRED_DIR = PILOT / "predictions"
IDS_FILE = PILOT / "verified_20_ids.txt"
ENRICHED = PILOT / "enriched_20.json"
OUT = HERE / "report_harness_swebench_verified_pilot20_zh.html"

DISPLAY = {"cline-patched": "cline", "hermes": "hermes"}
HARNESS_ORDER = ["cline-patched", "hermes"]


def esc(s):
    return html.escape(str(s))


def load_ids():
    return [l.strip() for l in IDS_FILE.read_text().splitlines() if l.strip()]


def load_enriched():
    rows = json.loads(ENRICHED.read_text())
    return {r["instance_id"]: r for r in rows}


def load_predict(harness):
    f = REPORT_DIR / f"predict_{harness}.json"
    if not f.exists():
        return []
    try:
        d = json.loads(f.read_text())
        return d if isinstance(d, list) else []
    except Exception:
        return []


def load_eval(harness):
    f = REPORT_DIR / f"eval_{harness}.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text())
    except Exception:
        return {}


def patch_len(harness, iid):
    f = PRED_DIR / f"{harness}__{iid}.json"
    if not f.exists() or f.stat().st_size < 30:
        return 0
    try:
        preds = json.loads(f.read_text())
        if preds:
            return len(preds[0].get("model_patch", ""))
    except Exception:
        return 0
    return 0


def is_smoke_eval(ev):
    return "_smoke" in ev.get("run_id", "")


def classify_instance(harness, iid, ev, pred_map, eval_done=True):
    pr = pred_map.get(iid, {})
    cls = pr.get("classification", "")
    # infra / no-patch are determinable from predict alone (no eval needed)
    if cls in ("infra", "blocked", "git-fetch-timeout", "timeout", "quota-blocked"):
        return "infra-or-quota"
    if cls == "no-patch":
        return "no-patch"
    if not eval_done:
        # eval not yet run for this harness: a produced patch cannot be
        # classified resolved/failed -> mark eval-pending (NOT failed/resolved)
        if pr or patch_len(harness, iid) > 0:
            return "eval-pending"
        return "not-run"
    resolved = set(ev.get("resolved", []))
    failed = set(ev.get("failed", []))
    infra = set(ev.get("infra_or_quota", []))
    if iid in resolved:
        return "resolved"
    if iid in infra:
        return "infra-or-quota"
    if iid in failed:
        return "failed"
    # has a patch but absent from eval lists (eval skipped it) -> failed
    if pr or patch_len(harness, iid) > 0:
        return "failed"
    return "not-run"


def fmt_pct(a, b):
    return f"{a/b*100:.1f}%" if b else "—"
def parts_from(per_harness, n_total, now, banner, eval_real, predict_done,
               cr, cf, ci, cnp, hr, hf, hi, hnp):
    c_evald = cr + cf
    h_evald = hr + hf
    cep = per_harness["cline-patched"]["counts"].get("eval-pending", 0)
    hep = per_harness["hermes"]["counts"].get("eval-pending", 0)
    c_ep_s = f" · <b>eval-pending {cep}</b>" if cep else ""
    h_ep_s = f" · <b>eval-pending {hep}</b>" if hep else ""
    parts = [f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SWE-bench Verified 20 条试点横评报告</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6f8;color:#222;margin:0;padding:24px;max-width:1200px;margin:0 auto;line-height:1.6}}
h1{{font-size:1.5rem;border-bottom:3px solid #2b6cb0;padding-bottom:8px}}
h2{{font-size:1.2rem;color:#2b6cb0;margin-top:32px;border-left:5px solid #2b6cb0;padding-left:10px}}
h3{{font-size:1.05rem;margin-top:22px}}
.meta{{color:#666;font-size:.85rem;margin-bottom:18px}}
.card{{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin:14px 0}}
.tldr{{background:#ebf8ff;border:1px solid #bee3f8;border-radius:8px;padding:16px 20px;margin:16px 0}}
.warn{{background:#fffbeb;border:1px solid #fbd38d;border-radius:8px;padding:12px 18px;margin:14px 0;color:#744210}}
table{{border-collapse:collapse;width:100%;font-size:.85rem;background:#fff;margin:10px 0}}
th,td{{border:1px solid #e2e8f0;padding:6px 8px;text-align:center}}
th{{background:#edf2f7;font-weight:600}} tr:nth-child(even){{background:#f7fafc}}
td.l{{text-align:left}}
td.pass{{background:#c6f6d5;font-weight:700;color:#22543d}} td.fail{{background:#fed7d7;color:#822727}}
td.infra{{background:#feebc8;color:#7b341e}} td.nopatch{{background:#e2e8f0;color:#718096}} td.notrun{{background:#f7fafc;color:#a0aec0}} td.evalpend{{background:#e9d8fd;color:#553c9a}}
code{{background:#edf2f7;padding:1px 5px;border-radius:3px;font-size:.82rem}}
.ev{{font-family:ui-monospace,Consolas,monospace;font-size:.78rem;color:#555}}
.foot{{color:#999;font-size:.78rem;margin-top:40px;border-top:1px solid #e2e8f0;padding-top:12px}}
</style></head><body>
<h1>SWE-bench Verified · 20 条试点横评报告</h1>
<div class="meta">生成时间：{now} · 任务令：2026-10-27 08:3x part②（用户直令：SWE-bench Verified 20 条试点启动）<br>
模型：kimi-k2.6-cloud（cline 经 secrets.json / hermes 经 gw_proxy 9090）· 评测集：SWE-bench Verified 500 题中抽取 20 条（5 repo × 4 题）<br>
评测脚本：官方 swebench v5.0.2 docker harness（<code>sg docker</code>，max_workers 4，timeout 1800s）· 命名规程：正文一律写 <code>cline</code>。</div>
{banner}"""]
    parts.append(f"""<div class="tldr"><h3 style="margin-top:0">TL;DR</h3>
<p>两路 harness 各跑 20 条 SWE-bench Verified 试点（同一 20 题集 / 同一模型 kimi-k2.6-cloud / 同一 timeout 1800s / 同一官方 docker 评测）：</p>
<ul>
<li><b>cline</b>：resolve <b>{cr}/{n_total}</b>（{fmt_pct(cr, n_total)}）；resolved {cr} · failed {cf} · infra-or-quota {ci} · 未产出 patch {cnp}（eval 覆盖 {c_evald} 条）{c_ep_s}。</li>
<li><b>hermes</b>：resolve <b>{hr}/{n_total}</b>（{fmt_pct(hr, n_total)}）；resolved {hr} · failed {hf} · infra-or-quota {hi} · 未产出 patch {hnp}（eval 覆盖 {h_evald} 条）{h_ep_s}。</li>
<li>⚠️ 严格遵守任务令「停在 20 条试点」，<b>未跑全量 500</b>。本结果供运维放大决策。</li>
</ul></div>""")
    parts.append("""<h2>一、评测口径</h2><div class="card"><table>
<tr><th class="l">维度</th><th class="l">取值</th></tr>
<tr><td class="l">评测集</td><td class="l">SWE-bench Verified 500 题中抽取 20 条（astropy 4 / django 4 / sympy 4 / matplotlib 4 / scikit-learn 4）</td></tr>
<tr><td class="l">模型</td><td class="l">kimi-k2.6-cloud（统一骨干，与 2100 Lite 同口径可比）</td></tr>
<tr><td class="l">harness</td><td class="l">cline（<code>cline-patched</code> 适配器）+ hermes（两路适配器均已 smoke 验通）</td></tr>
<tr><td class="l">predict</td><td class="l">每题 git clone@base_commit → 跑 harness CLI agent（problem_statement）→ git diff 作 model_patch；timeout 1800s/题</td></tr>
<tr><td class="l">eval</td><td class="l">官方 swebench v5.0.2 docker harness（enriched_20.json 补全 infra 字段）；<code>sg docker</code>，max_workers 4，timeout 1800s/题</td></tr>
<tr><td class="l">代理</td><td class="l">git fetch 经 172.19.92.25:13128（外网）；agent CLI 经本地 gw_proxy（剥外网代理，R529）</td></tr>
<tr><td class="l">规模控制</td><td class="l">严格 20 条（任务令：🚫 不得跑全量）</td></tr>
</table></div>""")
    return finalize(parts, per_harness, n_total, now, eval_real, cr, hr)


def finalize(parts, per_harness, n_total, now, eval_real, cr, hr):
    hep = per_harness["hermes"]["counts"].get("eval-pending", 0)
    cc = per_harness["cline-patched"]["counts"]
    cf, ci = cc["failed"], cc["infra-or-quota"]
    parts.append("""<h2>二、三列汇总（resolved / failed / infra-or-quota）</h2>
<div class="card"><table>
<tr><th>harness</th><th>predict 产出 patch</th><th>eval 覆盖</th>
<th class="pass">resolved</th><th class="fail">failed</th><th class="infra">infra-or-quota</th><th class="evalpend">eval-pending</th><th>resolve 率（/20）</th></tr>""")
    for h in HARNESS_ORDER:
        d = per_harness[h]; c = d["counts"]
        pred_patch = sum(1 for r in d["rows"] if r["patch"] > 0)
        evald = c["resolved"] + c["failed"]
        parts.append(f'<tr><td class="l">{DISPLAY[h]}</td><td>{pred_patch}/{n_total}</td><td>{evald}</td>'
                     f'<td class="pass">{c["resolved"]}</td><td class="fail">{c["failed"]}</td>'
                     f'<td class="infra">{c["infra-or-quota"]}</td><td class="evalpend">{c["eval-pending"]}</td>'
                     f'<td>{fmt_pct(c["resolved"], n_total)}</td></tr>')
    parts.append('</table><p class="ev">数据溯源：<code>swebench_verified_pilot/reports/eval_cline-patched.json</code> · <code>reports/eval_hermes.json</code> · <code>reports/predict_*.json</code> · <code>predictions/{harness}__{iid}.json</code>。</p></div>')
    cls_css = {"resolved": "pass", "failed": "fail", "infra-or-quota": "infra", "no-patch": "nopatch", "eval-pending": "evalpend", "not-run": "notrun"}
    for idx, h in enumerate(HARNESS_ORDER):
        d = per_harness[h]
        parts.append(f'<h2>三-{idx+1}、{DISPLAY[h]} 逐题明细</h2><div class="card"><table>'
                     f'<tr><th>instance_id</th><th>repo</th><th>分类</th><th>patch(B)</th><th>wall(s)</th><th>难度</th></tr>')
        for r in d["rows"]:
            parts.append(f'<tr><td class="l">{esc(r["iid"])}</td><td>{esc(r["repo"])}</td>'
                         f'<td class="{cls_css.get(r["cls"], "")}">{esc(r["cls"])}</td><td>{r["patch"]}</td>'
                         f'<td>{r["wall"] if r["wall"] is not None else "—"}</td><td>{esc(r["diff"]) or "—"}</td></tr>')
        parts.append("</table></div>")
    if not eval_real:
        # one or both evals still pending -- report per-harness honestly
        c_done = (cr + cf + ci) > 0
        cpart = (f"cline eval 已完成：resolve {cr}/{n_total}（{fmt_pct(cr, n_total)}），"
                 f"resolved {cr} · failed {cf} · infra-or-quota {ci}。") if c_done else "cline eval 尚未完成。"
        hpatch = sum(1 for r in per_harness["hermes"]["rows"] if r["patch"] > 0)
        hpart = (f"hermes eval 仍在进行（predict 已产出 {hpatch}/20 patch，{hep} 条待 eval），"
                 f"编排器自动 eval 完成后重新运行本生成器获得最终三列结果。") if hep else "hermes eval 尚未完成。"
        concl = cpart + hpart
    elif cr == 0 and hr == 0:
        concl = "两路 resolve 均为 0。需排查是否为 infra（git-fetch-timeout / docker eval）或模型能力问题。建议运维先看 <code>logs/eval_*.log</code> 再决定是否放大。"
    else:
        concl = (f"初步结果：cline resolve {cr}/{n_total}（{fmt_pct(cr, n_total)}），hermes resolve {hr}/{n_total}（{fmt_pct(hr, n_total)}）。"
                 "两路均产出有效 patch 且 eval 通过率非零 → pipeline 可用。建议运维据此决定是否放大到 50/100 条或扩到 7 路。"
                 "⚠️ matplotlib 13989/14623 等大仓 fetch 易超时（900s），放大时建议加大 fetch timeout 或用 partial-clone。")
    parts.append(f"""<h2>四、结论与放大建议</h2><div class="card"><p>{concl}</p>
<p><b>已知 infra 注意点</b>：</p><ul>
<li>matplotlib / 大型仓 <code>git fetch</code> 全量拉取可能 &gt;900s 超时 → 该题判 infra-or-quota（非模型能力）。</li>
<li>agent CLI（cline/hermes）必须剥外网代理（否则本地 gw_proxy 请求被 Squid 拒绝，R529）。</li>
<li>eval 经 <code>sg docker</code> 切组运行；docker 镜像 500/500 已预拉。</li>
<li>严格遵守任务令：停在 20 条试点，🚫 不得跑全量 500。</li>
</ul></div>""")
    parts.append(f"""<div class="foot">报告生成器：harness/gen_report_swebench_verified_pilot20_zh.py · 数据目录：harness/swebench_verified_pilot/ · 生成时间：{now}<br>
溯源文件：verified_20_ids.txt（20 题清单）· enriched_20.json（infra 字段补全）· reports/eval_*.json · reports/predict_*.json · predictions/ · logs/</div>
</body></html>""")
    OUT.write_text("\n".join(parts))
    print(f"written {OUT} ({OUT.stat().st_size}B)")
    cline = per_harness["cline-patched"]; hermes = per_harness["hermes"]
    print(f"  cline: resolved={cline['counts']['resolved']} failed={cline['counts']['failed']} infra={cline['counts']['infra-or-quota']} (eval_real={eval_real})")
    print(f"  hermes: resolved={hermes['counts']['resolved']} failed={hermes['counts']['failed']} infra={hermes['counts']['infra-or-quota']}")

def build():
    ids = load_ids()
    enriched = load_enriched()
    n_total = len(ids)
    per_harness = {}
    predict_done = True
    eval_real = True
    for h in HARNESS_ORDER:
        preds = load_predict(h)
        ev = load_eval(h)
        if len(preds) < n_total:
            predict_done = False
        ev_done = bool(ev) and not is_smoke_eval(ev)
        if not ev_done:
            eval_real = False
        pred_map = {p["instance_id"]: p for p in preds}
        rows = []
        counts = {"resolved": 0, "failed": 0, "infra-or-quota": 0,
                  "no-patch": 0, "eval-pending": 0, "not-run": 0}
        for iid in ids:
            cls = classify_instance(h, iid, ev, pred_map, eval_done=ev_done)
            counts[cls] = counts.get(cls, 0) + 1
            pl = patch_len(h, iid)
            pr = pred_map.get(iid, {})
            rows.append({"iid": iid, "repo": enriched.get(iid, {}).get("repo", ""),
                         "cls": cls, "patch": pl, "wall": pr.get("wall_s"),
                         "diff": enriched.get(iid, {}).get("difficulty", "")})
        per_harness[h] = {"rows": rows, "counts": counts, "ev": ev,
                          "pred_n": len(preds)}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    banner = ""
    if not eval_real:
        banner = ('<div class="warn">⚠️ eval 阶段尚未完成（eval_*.json 仍为 smoke 旧产物或缺失）。'
                  'predict/eval 全部完成后请重新运行本生成器以获得最终三列结果。</div>')
    elif not predict_done:
        banner = ('<div class="warn">⚠️ predict 阶段仍在进行（predict_*.json 尚未写全 20 条）。'
                  '下方部分行为「not-run」。predict 完成后重新运行本生成器。</div>')
    cline = per_harness["cline-patched"]
    hermes = per_harness["hermes"]
    cr, cf, ci = cline["counts"]["resolved"], cline["counts"]["failed"], cline["counts"]["infra-or-quota"]
    cnp = cline["counts"]["no-patch"] + cline["counts"]["not-run"]
    hr, hf, hi = hermes["counts"]["resolved"], hermes["counts"]["failed"], hermes["counts"]["infra-or-quota"]
    hnp = hermes["counts"]["no-patch"] + hermes["counts"]["not-run"]
    return parts_from(per_harness, n_total, now, banner, eval_real, predict_done,
                      cr, cf, ci, cnp, hr, hf, hi, hnp)


if __name__ == "__main__":
    build()

