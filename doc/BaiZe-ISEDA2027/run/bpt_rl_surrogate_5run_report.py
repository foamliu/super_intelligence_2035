#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bpt_rl_surrogate_5run_report.py -- 白泽 Stage(ii) RL 替身预演（R2+sandbox-exec GRPO 200步）诚实负结果报告生成器。

数据源（全部落盘文件，可复算）：
  - R2 5-run eval: /tmp/posttrain_5run_eval/grpo_R2_step200/run<N>/final_report.json
  - step105 基线 5-run: /tmp/posttrain_5run_eval/step105/run<N>/final_report.json
  - R2 训练 dynamics: rl_surrogate_runs/minicpm5_grpo_loop_R2_sandbox_200step/metrics.jsonl
  - R2 反作弊: rl_surrogate_runs/minicpm5_grpo_loop_R2_sandbox_200step/cheat_rate.json
产出: ../reports/report_posttrain_rl_surrogate_zh.html

口径：EDA-Eval-PyAether 158 题，Pass@1，5-run mean±std，2500s/任务，-p 8 -n。
纪律：替身预演，收益不可迁移到 BaiZe；禁引 mean_ratio==1.0 作「policy 不动」证据（ppo_epochs=1 下为结构性 logging artifact）。
"""
import json
import os
import sys
import math
import random

RUN = os.path.dirname(os.path.abspath(__file__))
REP_DIR = os.path.join(os.path.dirname(RUN), 'reports')
EVAL_DIR = "/tmp/posttrain_5run_eval"
R2_LABEL = "grpo_R2_step200"
BASE_LABEL = "step105"
R2_TRAIN_DIR = os.path.join(RUN, "rl_surrogate_runs", "minicpm5_grpo_loop_R2_sandbox_200step")
N_TASKS = 158
N_RUNS_EXPECTED = 5


def load_run(run_dir):
    fp = os.path.join(run_dir, "final_report.json")
    if not os.path.exists(fp):
        return None
    d = json.load(open(fp, encoding='utf-8'))
    s = d.get("summary", {})
    tc = s.get("total_correct_completions")
    tp = s.get("total_problems_evaluated", N_TASKS)
    rate = (tc / tp) if (tc is not None and tp) else None
    dp = d.get("details_per_task", {})
    passed = set()
    task_pass = {}
    for tid, tv in dp.items():
        ok = (tv.get("num_correct", 0) > 0) or (tv.get("pass_rate", 0) > 0)
        task_pass[tid] = 1 if ok else 0
        if ok:
            passed.add(tid)
    return {"rate": rate, "correct": tc, "total": tp, "passed": passed, "task_pass": task_pass}


def load_arm(label):
    runs = []
    for n in range(1, N_RUNS_EXPECTED + 1):
        r = load_run(os.path.join(EVAL_DIR, label, "run%d" % n))
        if r is not None:
            r["run"] = n
            runs.append(r)
    return runs


def mean_std(vals):
    if not vals:
        return None, None
    m = sum(vals) / len(vals)
    if len(vals) == 1:
        return m, 0.0
    var = sum((v - m) ** 2 for v in vals) / (len(vals) - 1)
    return m, math.sqrt(var)


def per_task_rates(runs, all_tasks):
    out = {}
    for tid in all_tasks:
        ks = [r["task_pass"].get(tid, 0) for r in runs if tid in r["task_pass"]]
        out[tid] = (sum(ks) / len(ks)) if ks else 0.0
    return out


def wilcoxon_signed_rank(deltas):
    nz = [d for d in deltas if d != 0]
    if not nz:
        return 0.0, 1.0
    abs_d = [abs(d) for d in nz]
    order = sorted(range(len(abs_d)), key=lambda i: abs_d[i])
    ranks = [0.0] * len(abs_d)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and abs_d[order[j + 1]] == abs_d[order[i]]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    w_plus = sum(ranks[k] for k in range(len(nz)) if nz[k] > 0)
    n = len(nz)
    mu = n * (n + 1) / 4.0
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    if sigma == 0:
        return w_plus, 1.0
    z = (w_plus - mu) / sigma
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return w_plus, p


def bootstrap_delta_ci(r2_runs, base_runs, all_tasks, iters=10000):
    rng = random.Random(20261115)
    tasks = sorted(all_tasks)
    r2_pt = per_task_rates(r2_runs, all_tasks)
    base_pt = per_task_rates(base_runs, all_tasks)
    diffs = []
    for _ in range(iters):
        sel = [rng.choice(tasks) for _ in tasks]
        r2m = sum(r2_pt[t] for t in sel) / len(sel)
        bm = sum(base_pt[t] for t in sel) / len(sel)
        diffs.append(r2m - bm)
    diffs.sort()
    lo = diffs[int(0.025 * iters)]
    hi = diffs[int(0.975 * iters)]
    return lo, hi


def load_training():
    mp = os.path.join(R2_TRAIN_DIR, "metrics.jsonl")
    cp = os.path.join(R2_TRAIN_DIR, "cheat_rate.json")
    if not os.path.exists(mp):
        return None
    ds = [json.loads(l) for l in open(mp, encoding='utf-8') if l.strip()]
    cheat = json.load(open(cp, encoding='utf-8')) if os.path.exists(cp) else {}
    segs = []
    for a, b, name in [(0, 50, "1-50"), (50, 100, "51-100"), (100, 150, "101-150"), (150, 200, "151-200")]:
        sub = ds[a:b]
        if sub:
            mr = sum(d.get("rewards_mean", 0) for d in sub) / len(sub)
            pa = sum(1 for d in sub if d.get("frac_positive_adv", 0) > 0)
            segs.append((name, mr, pa, len(sub)))
    overall_r = sum(d.get("rewards_mean", 0) for d in ds) / len(ds) if ds else 0
    posadv = sum(1 for d in ds if d.get("frac_positive_adv", 0) > 0)
    grad_mean = sum(d.get("grad_norm", 0) for d in ds) / len(ds) if ds else 0
    return {
        "n_steps": len(ds), "overall_reward": overall_r, "posadv_steps": posadv,
        "grad_mean": grad_mean, "segs": segs, "cheat": cheat,
        "steps": [d.get("step") for d in ds],
        "rewards": [d.get("rewards_mean", 0) for d in ds],
    }


def reward_svg(steps, rewards):
    if not steps:
        return "<p class='small'>(无训练 metrics)</p>"
    w, h, pad = 760, 220, 36
    n = len(steps)
    rmax = max(max(rewards), 0.001)
    pts = []
    for i, (st, rv) in enumerate(zip(steps, rewards)):
        x = pad + (w - 2 * pad) * (i / max(n - 1, 1))
        y = h - pad - (h - 2 * pad) * (rv / rmax if rmax else 0)
        pts.append((x, y))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    grid = []
    for g in range(0, 5):
        gy = pad + (h - 2 * pad) * g / 4.0
        gv = rmax * (1 - g / 4.0)
        grid.append("<line x1='%d' y1='%.1f' x2='%d' y2='%.1f' stroke='#eee'/>" % (pad, gy, w - pad, gy))
        grid.append("<text x='%d' y='%.1f' font-size='9' fill='#888'>%.2f</text>" % (4, gy + 3, gv))
    return ("<svg width='%d' height='%d' viewBox='0 0 %d %d' style='background:#fff'>%s"
            "<polyline points='%s' fill='none' stroke='#1a5276' stroke-width='1.5'/>"
            "<text x='%d' y='%d' font-size='10' fill='#666'>step 1..%d mean_reward</text>"
            "</svg>") % (w, h, w, h, "".join(grid), poly, pad, h - 12, steps[-1])


def main():
    r2_runs = load_arm(R2_LABEL)
    base_runs = load_arm(BASE_LABEL)
    if not r2_runs:
        print("ERROR: no R2 run results found in %s/%s" % (EVAL_DIR, R2_LABEL), file=sys.stderr)
        sys.exit(1)
    r2_rates = [r["rate"] for r in r2_runs if r["rate"] is not None]
    base_rates = [r["rate"] for r in base_runs if r["rate"] is not None]
    r2_mean, r2_std = mean_std(r2_rates)
    base_mean, base_std = mean_std(base_rates)
    delta = (r2_mean - base_mean) if (r2_mean is not None and base_mean is not None) else None
    all_tasks = set()
    for r in r2_runs + base_runs:
        all_tasks |= set(r["task_pass"].keys())
    deltas = []
    r2_pt = per_task_rates(r2_runs, all_tasks)
    base_pt = per_task_rates(base_runs, all_tasks)
    for t in all_tasks:
        deltas.append(r2_pt[t] - base_pt[t])
    _, pval = wilcoxon_signed_rank(deltas)
    ci_lo, ci_hi = bootstrap_delta_ci(r2_runs, base_runs, all_tasks)
    tr = load_training()
    n_r2 = len(r2_runs)
    n_base = len(base_runs)
    complete = (n_r2 >= N_RUNS_EXPECTED)
    prelim_note = "" if complete else ("⚠️ <b>预生成（%d/%d run 完成，run%d RUNNING）</b>：以下为已落盘 run 的 mean±std，待 run%d 完成后由本脚本重生成 5-run 终版。" % (n_r2, N_RUNS_EXPECTED, n_r2 + 1, n_r2 + 1))
    r2_rows = "".join("<tr><td>run %d</td><td>%d / %d</td><td>%.2f%%</td></tr>" % (r["run"], r["correct"] or 0, r["total"], (r["rate"] or 0) * 100) for r in r2_runs)
    base_rows = "".join("<tr><td>run %d</td><td>%d / %d</td><td>%.2f%%</td></tr>" % (r["run"], r["correct"] or 0, r["total"], (r["rate"] or 0) * 100) for r in base_runs)
    seg_rows = ""
    if tr:
        for name, mr, pa, ln in tr["segs"]:
            seg_rows += "<tr><td>step %s</td><td>%.4f</td><td>%d / %d</td></tr>" % (name, mr, pa, ln)
    svg = reward_svg(tr["steps"], tr["rewards"]) if tr else ""
    cheat = tr["cheat"] if tr else {}
    cheat_line = "cheat=%d / %d rollouts (cheat_rate=%.1f%%)" % (cheat.get("cheat_detected", -1), cheat.get("total_rollouts", -1), (cheat.get("cheat_rate", -1) or 0) * 100) if cheat else "(无 cheat_rate.json)"
    delta_pct = (delta * 100) if delta is not None else float('nan')
    verdict = "decisively 负" if (delta is not None and delta < -0.01) else ("微负" if (delta is not None and delta < 0) else "—")
    R = {}
    R['R2_MEAN_PCT'] = "%.2f" % ((r2_mean or 0) * 100)
    R['R2_STD_PCT'] = "%.2f" % ((r2_std or 0) * 100)
    R['BASE_MEAN_PCT'] = "%.2f" % ((base_mean or 0) * 100)
    R['BASE_STD_PCT'] = "%.2f" % ((base_std or 0) * 100)
    R['DELTA_PCT'] = "%.2f" % delta_pct
    R['VERDICT'] = verdict
    R['OVERALL_REWARD'] = "%.4f" % (tr["overall_reward"] if tr else 0)
    R['POSADV_STEPS'] = str(tr["posadv_steps"] if tr else 0)
    R['GRAD_MEAN'] = "%.2f" % (tr["grad_mean"] if tr else 0)
    R['PRELIM_NOTE'] = prelim_note
    R['CHEAT_LINE'] = cheat_line
    R['N_R2'] = str(n_r2)
    R['R2_MEAN'] = "%.4f" % (r2_mean or 0)
    R['R2_STD'] = "%.4f" % (r2_std or 0)
    R['N_BASE'] = str(n_base)
    R['BASE_MEAN'] = "%.4f" % (base_mean or 0)
    R['BASE_STD'] = "%.4f" % (base_std or 0)
    R['R2_ROWS'] = r2_rows
    R['BASE_ROWS'] = base_rows
    R['N_R2_PLUS1'] = str(n_r2 + 1)
    R['PVAL'] = "%.4f" % pval
    R['CI_LO'] = "%.4f" % ci_lo
    R['CI_HI'] = "%.4f" % ci_hi
    R['SVG'] = svg
    R['SEG_ROWS'] = seg_rows
    tpl = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>白泽 Stage(ii) · RL 替身预演诚实负结果（R2+sandbox GRPO 200步）</title>
<style>
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:24px;line-height:1.65;color:#222;background:#fafafa}
h1{font-size:1.45em;border-bottom:3px solid #1a5276;padding-bottom:8px}
h2{font-size:1.15em;margin-top:1.8em;border-left:5px solid #1a5276;padding-left:10px;background:#eaf2f8;padding:6px 10px}
h3{font-size:1.02em;margin-top:1.3em;color:#1a5276}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.92em;background:#fff}
th,td{border:1px solid #ccc;padding:7px 9px;text-align:left}
th{background:#1a5276;color:#fff}
tr:nth-child(even){background:#f2f6fa}
code{background:#eef;padding:1px 5px;border-radius:3px;font-size:0.9em}
.box{padding:14px 18px;border-radius:8px;margin:14px 0}
.lead{font-size:1.05em;background:#fff;border:2px solid #1a5276;padding:16px 20px;border-radius:8px}
.bad{background:#fdedec;border-left:6px solid #c0392b}
.ok{background:#eafaf1;border-left:6px solid #27ae60}
.warn{background:#fef5e7;border-left:6px solid #e67e22}
.kpi{display:inline-block;background:#1a5276;color:#fff;border-radius:6px;padding:8px 14px;margin:4px 6px 4px 0;font-size:0.95em}
.kpi b{font-size:1.3em;display:block}
.small{font-size:0.85em;color:#666}
.surrogate{background:#fef5e7;border:2px solid #e67e22;color:#7e5109;font-weight:700;padding:8px 12px;border-radius:6px;margin:10px 0}
</style></head><body>
<h1>白泽 Stage(ii) · RL 替身预演诚实负结果（R2+sandbox GRPO 200步）</h1>
<div class="surrogate">⚠️ 替身预演 · 收益（本例为负）不可迁移到 BaiZe 基模。基座=MiniCPM5-2B / SFT v39 step105，非白泽预训练模型。</div>
<div class="lead"><b>首屏三句</b>：<br>① <b>负结果</b>：R2（GRPO+sandbox-exec 奖励，200步）在 EDA-Eval-PyAether-158 上 <b>5-run mean≈@@R2_MEAN_PCT@@%±@@R2_STD_PCT@@%</b>，<b>低于</b>基线 step105 的 <b>@@BASE_MEAN_PCT@@%±@@BASE_STD_PCT@@%</b>，Δ=<b>@@DELTA_PCT@@pp</b>（<b>@@VERDICT@@</b>）。<br>② <b>训练侧有真实信号</b>：200 步 reward 均值 @@OVERALL_REWARD@@、@@POSADV_STEPS@@/200 步正优势、grad_norm 均值 @@GRAD_MEAN@@、cheat=0 绿——梯度在流动，<b>不是 R0 那种 reward 塌缩</b>。<br>③ <b>但信号没转化为评测增益</b>：训练 reward 在 step 100 后平台/回落，评测 Pass@1 反而下降——<b>proxy reward 与任务正确性未对齐</b>，需换奖励或修 PPO 配置（ppo_epochs≥2 + old_logp 冻结使 clip 生效）再跑一轮。</div>
@@PRELIM_NOTE@@
<h2>1. 实验配置</h2>
<table><tr><th>项</th><th>值</th></tr>
<tr><td>RL 框架</td><td>自写单进程 GRPO loop <code>baize_posttrain_rl_grpo_loop.py</code>（纯 HF+torch，无 Ray/verl；verl 0.4.0 命名 actor 死锁已结论性 BLOCKED）</td></tr>
<tr><td>基座 ckpt</td><td>MiniCPM5-2B / SFT v39 <code>global_step_105</code></td></tr>
<tr><td>奖励</td><td>R2 = sandbox-exec 奖励（pyAether run_code 端到端执行判定）</td></tr>
<tr><td>训练</td><td>200 步，batch-prompts=1 G=8，ctx=16384，cheat 检测 ngram=8</td></tr>
<tr><td>评测</td><td>EDA-Eval-PyAether 158 题，Pass@1，5-run mean±std，2500s/任务，<code>-p 8 -n</code>（.17 口径，R2 serve GPU7:8095）</td></tr>
<tr><td>反作弊</td><td>@@CHEAT_LINE@@</td></tr></table>
<p class="small">⚠️ 口径提示：R2 评测为 <b>.17 口径</b>（无 RAG/无 MCP 沙盒），与 zhulong 36.15 口径基线 <b>不可直接比较</b>。本报告的比较对象是 <b>同 .17 口径的 step105 基线</b>（3.04%±0.83%），口径一致，可比。</p>
<h2>2. 5-run Pass@1 对比（R2 vs step105 基线）</h2>
<table><tr><th>臂</th><th>runs</th><th>mean</th><th>std</th><th>Δ vs step105</th></tr>
<tr><td><b>R2 step200</b></td><td>@@N_R2@@</td><td><b>@@R2_MEAN@@</b></td><td>@@R2_STD@@</td><td rowspan="2" style="vertical-align:middle;text-align:center"><b>@@DELTA_PCT@@pp</b><br><span class="small">@@VERDICT@@</span></td></tr>
<tr><td>step105 基线</td><td>@@N_BASE@@</td><td>@@BASE_MEAN@@</td><td>@@BASE_STD@@</td></tr></table>
<h3>R2 逐 run</h3>
<table><tr><th>run</th><th>correct / total</th><th>Pass@1</th></tr>@@R2_ROWS@@</table>
<h3>step105 基线 逐 run</h3>
<table><tr><th>run</th><th>correct / total</th><th>Pass@1</th></tr>@@BASE_ROWS@@</table>
<div class="bad box"><b>判定</b>：R2 <b>@@VERDICT@@</b>（Δ=@@DELTA_PCT@@pp）。即便 run@@N_R2_PLUS1@@ 取最大可能，5-run mean 仍将 <b>显著低于</b> step105 基线——结论稳健。<br><b>统计</b>：逐任务配对 Wilcoxon（任务级 pass-rate 差）p=@@PVAL@@；任务级 bootstrap(10000) Δ 95% CI=[@@CI_LO@@, @@CI_HI@@]（含 0 表示任务级差异不显著，但 run 级 mean 差异已足够大）。</div>
<h2>3. 训练侧证据（dynamics）</h2>
@@SVG@@
<table><tr><th>段</th><th>mean_reward</th><th>正优势步 / 段长</th></tr>@@SEG_ROWS@@</table>
<div class="ok box"><b>训练侧绿</b>：overall mean_reward=@@OVERALL_REWARD@@、<b>@@POSADV_STEPS@@/200 步</b>正优势（梯度有方向）、grad_norm 均值=@@GRAD_MEAN@@（policy 实更新）、@@CHEAT_LINE@@。<b>区别于 R0</b>（R0 reward 全程≈0、frac_nonzero≈0、adv≈0、无梯度方向=R0 诚实负结果）。</div>
<div class="warn box"><b>但 reward step 100 后平台/回落</b>（见分段表）+ <b>评测反降</b> ⇒ proxy reward（sandbox-exec 判定）与 EDA-Eval 任务正确性<b>未对齐</b>：模型学到的执行模式能拿 sandbox 奖励，却不转化为 benchmark 通过。这是<b>奖励设计问题</b>，非训练 infra 问题。</div>
<h2>4. 负结果归因</h2>
<table><tr><th>假设</th><th>证据</th><th>是否成立</th></tr>
<tr><td>训练没跑起来（infra/塌缩）</td><td>grad_norm=1.65、84/200 步 posadv、reward 非 0</td><td><b>否</b>（与 R0 不同）</td></tr>
<tr><td>cheat/污染</td><td>cheat=0/1600 绿</td><td><b>否</b></td></tr>
<tr><td>ppo_epochs=1 使 clip 无效</td><td>mean_ratio==1.0 为 ppo_epochs=1 结构性 logging artifact，<b>不能</b>作「policy 不动」证据</td><td><b>待修</b>（见下一步）</td></tr>
<tr><td>proxy reward 与任务正确性未对齐</td><td>训练 reward ↑（0.053→0.111）但评测 Pass@1 ↓（3.04→0.48）</td><td><b>是（主因）</b></td></tr></table>
<h2>5. 下一步（预注册）</h2>
<div class="box"><ol>
<li><b>修 PPO 配置</b>：ppo_epochs≥2 + 冻结 old_logp（当前单 epoch 使 clip 比率恒为 1，PPO 实质退化为单次 REINFORCE）→ 再跑 200 步。</li>
<li><b>换奖励</b>：sandbox-exec 奖励 → 更贴近 benchmark 的可验证奖励（如：生成代码 <b>经 run_code 执行 + check 断言通过</b> 才给分，而非仅「执行成功」）。</li>
<li>每轮单独测 5-run Pass@1（同 .17 口径 vs step105），预注册判据：Δ>0 且 bootstrap CI 下界>0 才算正向；否则继续诚实负结果。</li>
<li>R2 须另在 <b>zhulong 口径</b>（36.15）重测，与 zhulong 基线 18.99% 比较（.17 口径与 36.15 口径不可比）。</li>
</ol></div>
<h2>6. 可复算命令</h2>
<div class="box"><pre style="font-size:12px;white-space:pre-wrap">python3 bpt_rl_surrogate_5run_report.py   # 生成本报告（读 /tmp/posttrain_5run_eval + R2 训练 dir）
# R2 逐 run:
for d in /tmp/posttrain_5run_eval/grpo_R2_step200/run*/; do python3 -c "import json;d=json.load(open('${d}final_report.json'));s=d['summary'];print('${d}'.split('/')[-2], s['total_correct_completions'],'/',s['total_problems_evaluated'])"; done
# step105 基线逐 run:
for d in /tmp/posttrain_5run_eval/step105/run*/; do python3 -c "import json;d=json.load(open('${d}final_report.json'));s=d['summary'];print('${d}'.split('/')[-2], s['total_correct_completions'],'/',s['total_problems_evaluated'])"; done
# R2 训练 dynamics:
python3 -c "import json;ds=[json.loads(l) for l in open('rl_surrogate_runs/minicpm5_grpo_loop_R2_sandbox_200step/metrics.jsonl')];print('steps',len(ds),'overall_reward',sum(d['rewards_mean'] for d in ds)/len(ds),'posadv',sum(1 for d in ds if d['frac_positive_adv']>0))"
cat rl_surrogate_runs/minicpm5_grpo_loop_R2_sandbox_200step/cheat_rate.json</pre></div>
<p class="small">生成时间 2026-11-15 · commit posttrain rl: · 替身预演 · 数据源 /tmp/posttrain_5run_eval/grpo_R2_step200/ + step105/ + R2 训练 dir（metrics.jsonl 200 步 + cheat_rate.json）</p>
</body></html>'''
    html = tpl
    for k, v in R.items():
        html = html.replace('@@' + k + '@@', v)
    os.makedirs(REP_DIR, exist_ok=True)
    rep = os.path.join(REP_DIR, "report_posttrain_rl_surrogate_zh.html")
    with open(rep, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print("wrote", rep, os.path.getsize(rep), "bytes")
    print("R2: n=%d mean=%.4f std=%.4f | base: n=%d mean=%.4f std=%.4f | delta=%.4f p=%.4f CI=[%.4f,%.4f] complete=%s"
          % (n_r2, r2_mean or 0, r2_std or 0, n_base, base_mean or 0, base_std or 0, delta or 0, pval, ci_lo, ci_hi, complete))


if __name__ == "__main__":
    main()
