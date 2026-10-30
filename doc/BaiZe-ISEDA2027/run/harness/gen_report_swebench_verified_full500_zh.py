#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 SWE-bench Verified 全量 500 题横评报告（中文 HTML，自包含）。

按 BAIZE_HARNESS_TASK.md 运维令 2026-10-28 07:1x（用户直令：跑完整的
SWE-bench Verified）。

数据字典（全部可溯源，不编造）：
  数据来源                                       字段用途
  ---------------------------------------------------------------------------
  swebench_verified_full/reports/progress_{h}.json   predict 阶段逐题分类
        顶层: done/total/patch_produced/infra/timeout/quota_blocked/
              no_patch/last_update；results[]: instance_id,wall_s,
              model_patch_len,classification,quota_blocked,timeout
  swebench_verified_full/reports/eval_{h}.json       eval 阶段汇总
        resolved:[iid...] / failed:[iid...] / infra_or_quota:[iid...] / n
  swebench_verified_full/predictions/{h}__{iid}.json 逐题 model_patch
  swebench_verified_full/full_500_ids_{h}.txt        每路 500 题清单
  swebench_verified_pilot/reports/eval_*.json        20 题试点对照

口径（铁律）：
  - 评测集固定 500（princeton-nlp/SWE-bench_Verified，非 Lite/非子集）
  - 模型固定 kimi-k2.6-cloud（统一骨干）
  - 打分 = 官方 swebench v5.0.2 docker harness
  - infra-or-fetch-timeout 单列，不计入模型失败/成功（铁律 3）
  - 闸门不过的 harness 不进全量，如实列「未参与 + 原因」（铁律 4）

命名规程：报告正文一律写 `cline`（不写 cline-patched）；代码标识符不改。
报告目录纪律：HTML 产出在 doc/BaiZe-ISEDA2027/reports/（不在 run/reports）。

鲁棒性：eval 尚未完成时也能运行（仅 predict 阶段 → 显示 banner + predict
统计 + eval-pending）；eval 完成后重新运行即得完整三列 + Wilson CI + McNemar。
"""
from __future__ import annotations
import html
import json
import math
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = HERE / "swebench_verified_full"
REPORT_DIR = FULL / "reports"
PRED_DIR = FULL / "predictions"
# 报告输出到项目级 reports/（目录纪律 2026-10-28）
PROJECT_REPORTS = HERE.parent.parent / "reports"
OUT = PROJECT_REPORTS / "report_harness_swebench_verified_full500_zh.html"

# 7 路（5 原 gate-PASS + 2 adapter-fixed R988: hermes/deepseek 适配器修复后恢复全量）
HARNESS_ORDER = ["cline-patched", "opencode", "pi", "claude-code", "codex",
                 "hermes", "deepseek-harness"]
DISPLAY = {"cline-patched": "cline", "opencode": "opencode", "pi": "pi",
           "claude-code": "claude-code", "codex": "codex",
           "hermes": "hermes", "deepseek-harness": "deepseek-harness"}
# 闸门 FAIL → 未参与全量（如实列）— R988 修复后 hermes/deepseek 已恢复，GATE_FAILED 为空
GATE_FAILED = {}
N_TOTAL = 500
# 20 题试点对照（pilot20 报告实测，commit 33782ab93 系列）
PILOT20 = {"cline-patched": (13, 20), "hermes": (11, 20)}


def esc(s):
    return html.escape(str(s))


def fmt_pct(a, b):
    return f"{a/b*100:.1f}%" if b else "—"


def wilson_ci(x, n, z=1.96):
    """Wilson score 95% CI for x successes in n trials. Returns (lo, hi) as proportions."""
    if n <= 0:
        return (0.0, 0.0)
    phat = x / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def mcnemar_exact(resolved_a, resolved_b, common):
    """Exact McNemar on common evaluated instance set.
    n01 = A resolved & B not; n10 = B resolved & A not.
    Two-sided p via exact binomial (k ~ Binomial(discordant, 0.5))."""
    ra = set(resolved_a) & common
    rb = set(resolved_b) & common
    n01 = len(ra - rb)
    n10 = len(rb - ra)
    disc = n01 + n10
    if disc == 0:
        return {"n01": 0, "n10": 0, "discordant": 0, "p": 1.0,
                "chi2_cc": 0.0, "note": "无 discordant 对"}
    k = min(n01, n10)
    # exact two-sided p = 2 * P(X<=k) (symmetric), cap at 1.0
    p_one = sum(math.comb(disc, i) for i in range(0, k + 1)) / (2 ** disc)
    p = min(1.0, 2 * p_one)
    # continuity-corrected chi-square (for reference when disc large)
    chi2 = (abs(n01 - n10) - 1) ** 2 / disc if disc > 0 else 0.0
    return {"n01": n01, "n10": n10, "discordant": disc, "p": p,
            "chi2_cc": chi2, "note": ""}


def load_progress(harness):
    f = REPORT_DIR / f"progress_{harness}.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text())
    except Exception:
        return {}


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


def is_real_eval(ev):
    """eval_*.json is a real full eval (not a stale gate/smoke subset)."""
    if not ev:
        return False
    # gate evals had small n (<=10); full eval n should be hundreds
    return ev.get("n", 0) > 10


def aggregate(harness):
    """Build per-harness predict + eval aggregates."""
    prog = load_progress(harness)
    ev = load_eval(harness)
    results = prog.get("results", []) if prog else []
    # predict stats
    done = prog.get("done", len(results))
    patch = prog.get("patch_produced", sum(1 for r in results if r.get("model_patch_len", 0) > 0))
    infra = prog.get("infra", 0)
    timeout = prog.get("timeout", 0)
    quota = prog.get("quota_blocked", 0)
    no_patch = prog.get("no_patch", 0)
    last_update = prog.get("last_update", "")
    # wall time
    walls = [r.get("wall_s", 0) for r in results if r.get("wall_s")]
    total_wall = sum(walls)
    avg_wall = total_wall / len(walls) if walls else 0
    # eval stats
    resolved = ev.get("resolved", []) if is_real_eval(ev) else []
    failed = ev.get("failed", []) if is_real_eval(ev) else []
    infra_ev = ev.get("infra_or_quota", []) if is_real_eval(ev) else []
    eval_done = is_real_eval(ev)
    return {
        "harness": harness, "display": DISPLAY.get(harness, harness),
        "done": done, "patch": patch, "infra": infra, "timeout": timeout,
        "quota": quota, "no_patch": no_patch, "last_update": last_update,
        "total_wall": total_wall, "avg_wall": avg_wall,
        "resolved": resolved, "failed": failed, "infra_ev": infra_ev,
        "eval_done": eval_done, "n_eval": ev.get("n", 0),
    }


CSS_STYLE = """
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f6f8;color:#222;margin:0;padding:24px;max-width:1280px;margin:0 auto;line-height:1.6}
h1{font-size:1.5rem;border-bottom:3px solid #2b6cb0;padding-bottom:8px}
h2{font-size:1.2rem;color:#2b6cb0;margin-top:32px;border-left:5px solid #2b6cb0;padding-left:10px}
h3{font-size:1.05rem;margin-top:22px}
.meta{color:#666;font-size:.85rem;margin-bottom:18px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin:14px 0}
.tldr{background:#ebf8ff;border:1px solid #bee3f8;border-radius:8px;padding:16px 20px;margin:16px 0}
.warn{background:#fffbeb;border:1px solid #fbd38d;border-radius:8px;padding:12px 18px;margin:14px 0;color:#744210}
table{border-collapse:collapse;width:100%;font-size:.83rem;background:#fff;margin:10px 0}
th,td{border:1px solid #e2e8f0;padding:6px 8px;text-align:center}
th{background:#edf2f7;font-weight:600} tr:nth-child(even){background:#f7fafc}
td.l{text-align:left}
td.pass{background:#c6f6d5;font-weight:700;color:#22543d} td.fail{background:#fed7d7;color:#822727}
td.infra{background:#feebc8;color:#7b341e} td.nopatch{background:#e2e8f0;color:#718096} td.evalpend{background:#e9d8fd;color:#553c9a}
td.sig{background:#fed7d7;font-weight:700} td.nosig{background:#f7fafc;color:#718096}
code{background:#edf2f7;padding:1px 5px;border-radius:3px;font-size:.82rem}
.ev{font-family:ui-monospace,Consolas,monospace;font-size:.78rem;color:#555}
.foot{color:#999;font-size:.78rem;margin-top:40px;border-top:1px solid #e2e8f0;padding-top:12px}
"""


def head(now, any_eval, all_predict):
    banner = ""
    if not any_eval:
        banner = ('<div class="warn">⚠️ eval 阶段尚未完成（eval_*.json 仍为 gate 旧产物或缺失）。'
                  '本报告当前仅含 <b>predict 阶段</b>统计（产出 patch 率 / 未产出 patch / infra / 配额）。'
                  'predict+eval 全部完成后请重新运行本生成器以获得 resolved/failed 三列、Wilson 95% CI 与 McNemar 配对检验。</div>')
    elif not all_predict:
        banner = ('<div class="warn">⚠️ predict 阶段仍在进行（部分路未达 500）。下方 resolved 统计基于'
                  '已完成题集；predict 完成后重新运行本生成器。</div>')
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SWE-bench Verified 全量 500 题横评报告</title>
<style>{CSS_STYLE}</style></head><body>
<h1>SWE-bench Verified · 全量 500 题横评报告</h1>
<div class="meta">生成时间：{now} · 任务令：2026-10-28 07:1x（用户直令：跑完整的 SWE-bench Verified）<br>
模型：kimi-k2.6-cloud（统一骨干）· 评测集：princeton-nlp/SWE-bench_Verified 全量 500 题<br>
评测脚本：官方 swebench v5.0.2 docker harness（<code>sg docker</code>，max_workers 8–12，timeout 1800s/题）<br>
命名规程：正文一律写 <code>cline</code>（不写 cline-patched）· 报告目录：doc/BaiZe-ISEDA2027/reports/</div>
{banner}"""


def tldr(per, any_eval, all_predict):
    rows = []
    for h in HARNESS_ORDER:
        d = per[h]
        if any_eval and d["eval_done"]:
            r = len(d["resolved"])
            lo, hi = wilson_ci(r, d["n_eval"] or N_TOTAL)
            ci = f"（95% CI {lo*100:.1f}%–{hi*100:.1f}%）" if d["n_eval"] else ""
            rows.append(f'<li><b>{d["display"]}</b>：resolve <b>{r}/{d["n_eval"] or N_TOTAL}</b>'
                        f'（{fmt_pct(r, d["n_eval"] or N_TOTAL)}）{ci}；'
                        f'产出 patch {d["patch"]} · 未产出 patch {d["no_patch"]} · infra {d["infra"]}。</li>')
        else:
            rows.append(f'<li><b>{d["display"]}</b>：predict done <b>{d["done"]}/500</b>；'
                        f'产出 patch {d["patch"]}（{fmt_pct(d["patch"], d["done"])}）· '
                        f'未产出 patch {d["no_patch"]} · infra {d["infra"]} · eval 待完成。</li>')
    status = "（predict+eval 已完成）" if (any_eval and all_predict) else "（predict 进行中 / eval 待完成）"
    return f"""<div class="tldr"><h3 style="margin-top:0">TL;DR</h3>
<p>5 路 gate-PASS harness 各跑 SWE-bench Verified <b>全量 500 题</b>（同一 500 题 / 同一模型 kimi-k2.6-cloud /
同一 timeout 1800s / 同一官方 docker 评测）{status}：</p>
<ul>{"".join(rows)}</ul>
<p>闸门未过的 <b>hermes</b> / <b>deepseek-harness</b> 不进全量（如实列「未参与 + 原因」，铁律 4）。
infra-or-fetch-timeout 单列、不计入模型失败/成功（铁律 3）。</p></div>"""


def scope_section():
    return """<h2>一、评测口径</h2><div class="card"><table>
<tr><th class="l">维度</th><th class="l">取值</th></tr>
<tr><td class="l">评测集</td><td class="l">SWE-bench Verified 全量 500 题（princeton-nlp/SWE-bench_Verified，非 Lite、非子集）</td></tr>
<tr><td class="l">模型</td><td class="l">kimi-k2.6-cloud（统一骨干，与 20 题试点、2100 Lite 同口径可比）</td></tr>
<tr><td class="l">harness</td><td class="l">5 路 gate-PASS：cline / opencode / pi / claude-code / codex（闸门：10 题 resolve≥1 且未产出 patch≤2）</td></tr>
<tr><td class="l">predict</td><td class="l">每题 git clone@base_commit → 跑 harness CLI agent（problem_statement）→ git diff 作 model_patch；timeout 1800s/题；断点续跑（已有 prediction 跳过）</td></tr>
<tr><td class="l">fetch 优化</td><td class="l">git fetch timeout 300→1800s；各路 ids 轮转避免同仓并发 fetch 拥塞；fetch 超时题判 infra 单列</td></tr>
<tr><td class="l">eval</td><td class="l">官方 swebench v5.0.2 docker harness；<code>sg docker</code>，max_workers 8–12，timeout 1800s/题</td></tr>
<tr><td class="l">代理</td><td class="l">git fetch 经 172.19.92.25:13128（外网）；agent CLI 经本地 gw_proxy（剥外网代理，R529）</td></tr>
<tr><td class="l">铁律</td><td class="l">①不许改评测口径 ②不许放宽测试 ③infra 单列 ④闸门不过不硬跑 ⑤资源不足先报 blocker</td></tr>
</table></div>"""


def predict_summary(per):
    rows = []
    tot_done = tot_patch = tot_np = tot_infra = 0
    for h in HARNESS_ORDER:
        d = per[h]
        tot_done += d["done"]; tot_patch += d["patch"]; tot_np += d["no_patch"]; tot_infra += d["infra"]
        rows.append(f'<tr><td class="l">{d["display"]}</td><td>{d["done"]}/500</td>'
                    f'<td>{d["patch"]} ({fmt_pct(d["patch"], d["done"])})</td>'
                    f'<td class="nopatch">{d["no_patch"]} ({fmt_pct(d["no_patch"], d["done"])})</td>'
                    f'<td class="infra">{d["infra"]}</td><td>{d["quota"]}</td>'
                    f'<td>{d["total_wall"]/3600:.1f}h</td><td>{d["avg_wall"]:.0f}s</td>'
                    f'<td>{d["last_update"]}</td></tr>')
    rows.append(f'<tr style="font-weight:700"><td class="l">合计</td><td>{tot_done}/2500</td>'
                f'<td>{tot_patch}</td><td class="nopatch">{tot_np}</td><td class="infra">{tot_infra}</td>'
                f'<td>—</td><td>—</td><td>—</td><td>—</td></tr>')
    return f"""<h2>二、predict 阶段汇总（适配器健康度）</h2>
<div class="card"><p>「未产出 patch」= 适配器健康度指标（agent 跑完但没产出 diff）；「infra」= git-fetch 超时等基础设施失败（单列，不计模型能力）。</p>
<table>
<tr><th>harness</th><th>done</th><th>产出 patch</th><th class="nopatch">未产出 patch</th>
<th class="infra">infra</th><th>quota</th><th>总耗时</th><th>平均/题</th><th>last_update</th></tr>
{"".join(rows)}</table></div>"""


def eval_summary(per):
    rows = []
    for h in HARNESS_ORDER:
        d = per[h]
        if d["eval_done"]:
            r, f, ie = len(d["resolved"]), len(d["failed"]), len(d["infra_ev"])
            rows.append(f'<tr><td class="l">{d["display"]}</td><td>{d["n_eval"]}</td>'
                        f'<td class="pass">{r}</td><td class="fail">{f}</td><td class="infra">{ie}</td>'
                        f'<td>{fmt_pct(r, d["n_eval"])}</td></tr>')
        else:
            rows.append(f'<tr><td class="l">{d["display"]}</td><td colspan="5" class="evalpend">eval 待完成</td></tr>')
    return f"""<h2>三、eval 阶段三列汇总（resolved / failed / infra-or-quota）</h2>
<div class="card"><p>resolved = 通过官方测试；failed = 产出 patch 但未通过测试（模型能力）；infra-or-quota = 基础设施/配额失败（单列，不计模型能力）。</p>
<table>
<tr><th>harness</th><th>eval 覆盖</th><th class="pass">resolved</th><th class="fail">failed</th>
<th class="infra">infra-or-quota</th><th>resolve 率</th></tr>
{"".join(rows)}</table></div>"""


def wilson_section(per):
    rows = []
    for h in HARNESS_ORDER:
        d = per[h]
        if d["eval_done"] and d["n_eval"]:
            r = len(d["resolved"]); lo, hi = wilson_ci(r, d["n_eval"])
            rows.append(f'<tr><td class="l">{d["display"]}</td><td>{r}</td><td>{d["n_eval"]}</td>'
                        f'<td>{fmt_pct(r, d["n_eval"])}</td>'
                        f'<td>{lo*100:.1f}% – {hi*100:.1f}%</td></tr>')
    return f"""<h2>四、Wilson 95% 置信区间</h2>
<div class="card"><p>500 题样本必须给置信区间（任务令④）。Wilson score 区间，z=1.96。</p>
<table>
<tr><th>harness</th><th>resolved</th><th>n</th><th>点估计</th><th>95% CI</th></tr>
{"".join(rows)}</table></div>"""


def eval_pending_section(per):
    return """<h2>三、eval 阶段（待完成）</h2>
<div class="card"><p class="warn">eval 阶段尚未启动（predict 进行中）。predict 全部完成后将启动官方 swebench v5.0.2 docker harness
（<code>sg docker</code>，max_workers 8–12）对每路 predictions 打分，产出 <code>eval_{harness}.json</code>
（resolved / failed / infra_or_quota），随后重新运行本生成器以补全：三列汇总 · Wilson 95% CI · McNemar 7×7 配对检验。</p>
<p>当前 eval_*.json 为 gate 阶段（≤10 题）旧产物，不计入全量统计（本生成器以 n&gt;10 判定真实全量 eval）。</p></div>"""


def mcnemar_section(per):
    # McNemar needs pairs of harnesses both with real eval; use common evaluated set
    done = [h for h in HARNESS_ORDER if per[h]["eval_done"]]
    if len(done) < 2:
        return '<h2>五、McNemar 配对检验（待 eval）</h2><div class="card"><p class="warn">至少两路 eval 完成后才可做配对检验。</p></div>'
    # common set = instances evaluated by both (resolved+failed, i.e. not infra)
    def evset(h):
        d = per[h]
        return set(d["resolved"]) | set(d["failed"])
    hdr = "".join(f"<th>{per[h]['display']}</th>" for h in done)
    rows = []
    for a in done:
        cells = [f'<td class="l">{per[a]["display"]}</td>']
        ca = evset(a)
        for b in done:
            if a == b:
                cells.append('<td>—</td>')
            else:
                cb = evset(b)
                common = ca & cb
                m = mcnemar_exact(per[a]["resolved"], per[b]["resolved"], common)
                sig = "sig" if m["p"] < 0.05 else "nosig"
                cells.append(f'<td class="{sig}">n01={m["n01"]} n10={m["n10"]}<br>p={m["p"]:.3f}<br>(共{len(common)}题)</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"""<h2>五、McNemar 配对检验（同题集配对）</h2>
<div class="card"><p>同题集 500 题配对样本充足（任务令④）。n01 = 行 resolved & 列 failed；n10 = 行 failed & 列 resolved。
exact binomial two-sided p；<span class="sig">p&lt;0.05 显著</span>，<span class="nosig">不显著</span>。</p>
<table><tr><th></th>{hdr}</tr>{"".join(rows)}</table></div>"""


def gate_failed_section():
    if not GATE_FAILED:
        return """<h2>六、闸门状态</h2>
<div class="card"><p>用户令要求 7 路，全部 7 路已通过闸门或经适配器修复（R988）后恢复全量评测。
hermes / deepseek-harness 原闸门 fail（适配器不健康），R988 修复后 verify5b 分别达 80% / 60%，已纳入全量。</p></div>"""
    rows = "".join(
        f'<tr><td class="l">{esc(k)}</td><td class="nopatch">{esc(v)}</td></tr>'
        for k, v in GATE_FAILED.items())
    return f"""<h2>六、未参与全量的 harness（闸门未过，如实列）</h2>
<div class="card"><p>用户令要求 7 路；其中部分闸门 10 题不达标（铁律 4：闸门不过不硬跑全量）。
已如实列「未参与 + 原因」，不为凑 7 路而硬跑。</p>
<table><tr><th>harness</th><th>未参与原因</th></tr>{rows}</table></div>"""


def pilot_compare(per, any_eval):
    rows = ""
    for h, (pr, pn) in PILOT20.items():
        disp = DISPLAY.get(h, h)
        if h in per and per[h]["eval_done"] and per[h]["n_eval"]:
            r = len(per[h]["resolved"]); n = per[h]["n_eval"]
            rows += (f'<tr><td class="l">{disp}</td><td>{pr}/{pn} ({fmt_pct(pr, pn)})</td>'
                     f'<td>{r}/{n} ({fmt_pct(r, n)})</td>'
                     f'<td>{"落在 CI 内 ✓" if wilson_ci(pr, pn)[0] <= r/n <= wilson_ci(pr, pn)[1] else "偏离试点 CI，需解释"}</td></tr>')
        else:
            rows += f'<tr><td class="l">{disp}</td><td>{pr}/{pn} ({fmt_pct(pr, pn)})</td><td class="evalpend">eval 待完成</td><td>—</td></tr>'
    return f"""<h2>七、与 20 题试点一致性对照</h2>
<div class="card"><p>试点为抽样，全量应落在试点 CI 内；偏离要解释（任务令④）。</p>
<table><tr><th>harness</th><th>20 题试点</th><th>全量 500</th><th>一致性</th></tr>{rows}</table>
<p>试点口径：report_harness_swebench_verified_pilot20_zh.html（cline 13/20=65.0%，hermes 11/20=55.0%）。</p></div>"""


def repro_section():
    return """<h2>八、复现命令</h2>
<div class="card"><p class="ev"># predict（断点续跑，已有 prediction 跳过）<br>
cd doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full<br>
setsid bash launch_full_predict_5.sh &gt; logs/full_predict_launcher.log 2&gt;&amp;1 &amp;<br><br>
# 监控（progress JSON 为权威）<br>
python3 -c "import json,glob,os; [print(os.path.basename(f), json.load(open(f))['done'],'/500') for f in sorted(glob.glob('reports/progress_*.json'))]"<br><br>
# eval（predict 全部完成后；sg docker，max_workers 8–12）<br>
python3 run_verified_full.py eval --harness &lt;h&gt; --ids-file full_500_ids_&lt;h&gt;.txt<br><br>
# 生成报告（predict-only 也可运行；eval 完成后重运行得完整报告）<br>
python3 gen_report_swebench_verified_full500_zh.py</p></div>"""


def footer(now):
    return f"""<div class="foot">报告生成器：harness/gen_report_swebench_verified_full500_zh.py · 数据目录：harness/swebench_verified_full/ · 生成时间：{now}<br>
溯源：reports/progress_*.json（predict 逐题）· reports/eval_*.json（eval 汇总）· predictions/（逐题 patch）· full_500_ids_*.txt（500 题清单）<br>
铁律遵守：评测口径不变 · infra 单列 · 闸门不过不硬跑 · 结果 JSON 不入仓库（永久硬约束）</div>
</body></html>"""


def build():
    per = {h: aggregate(h) for h in HARNESS_ORDER}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    any_eval = any(per[h]["eval_done"] for h in HARNESS_ORDER)
    all_predict = all(per[h]["done"] >= N_TOTAL for h in HARNESS_ORDER)
    parts = [head(now, any_eval, all_predict)]
    parts.append(tldr(per, any_eval, all_predict))
    parts.append(scope_section())
    parts.append(predict_summary(per))
    if any_eval:
        parts.append(eval_summary(per))
        parts.append(wilson_section(per))
        parts.append(mcnemar_section(per))
    else:
        parts.append(eval_pending_section(per))
    parts.append(gate_failed_section())
    parts.append(pilot_compare(per, any_eval))
    parts.append(repro_section())
    parts.append(footer(now))
    PROJECT_REPORTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts))
    print(f"written {OUT} ({OUT.stat().st_size}B)")
    for h in HARNESS_ORDER:
        d = per[h]
        r = len(d["resolved"])
        print(f"  {d['display']:12s} done={d['done']}/500 patch={d['patch']} "
              f"no_patch={d['no_patch']} infra={d['infra']} eval={'Y' if d['eval_done'] else 'N'} "
              f"resolved={r}")


if __name__ == "__main__":
    build()
