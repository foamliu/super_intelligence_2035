#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bpt_attribution_t6_report.py — 36.15 run1 T6 工具格式归因表 + 中文 HTML 报告生成器
数据源 (可复算): attribution_3615_run1/ (final_report.json + codegen_rejection_stats.json
                 + execution_results.jsonl) 与 attribution_3615_run1_perquest_profile.json
输出: attribution_t6_table.json (归因表, 机器可读)
      reports/report_posttrain_attribution_t6_zh.html (中文报告, 单文件自包含, 内联 SVG)
纪律: 只读 run1 落盘数据; 不改 benchmark/check.py/题面; 取不到标 TODO; 不引用未跑完的 run.
"""
import json, os, datetime, html, math

RUN = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.join(RUN, "attribution_3615_run1")
PROFILE = os.path.join(RUN, "attribution_3615_run1_perquest_profile.json")
REPORTS = os.path.join(os.path.dirname(RUN), "reports")
os.makedirs(REPORTS, exist_ok=True)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


fr = load(os.path.join(R1, "final_report.json"))
rej_stats = load(os.path.join(R1, "codegen_rejection_stats.json"))
prof = load(PROFILE)

summ = fr["summary"]
gs = summ["generation_statistics"]
N = summ["total_problems_evaluated"]
gen_success, gen_fail, gen_timeout = gs["success"], gs["fail"], gs["timeout"]
passed = summ["total_correct_completions"]
post_gen = passed / gen_success if gen_success else 0.0
overall = passed / N

reject_reasons = prof["aggregate_reject_reasons"]
reject_tools = prof["aggregate_reject_tools"]
sixtype = prof["classification_RCA_v2_sixtype"]
gdd = prof["genfail_deep_dive"]
rejected_total = rej_stats["rejected_total"]
rc_str_not_arr = rej_stats.get("run_commands_string_not_array", 0)

p0_eliminable = {
    "missing-required-field": 0.70,
    "other-type-error": 0.40,
    "string-not-array": 0.90,
    "unavailable-tool": 0.50,
    "wrong-type-boolean": 0.80,
}
MECH = {
    "missing-required-field": "run_commands 缺 commands / read_files 缺 path 对象 / submit 缺 summary|verified; P0 给结构化正例",
    "other-type-error": "把 submit_and_exit 的 summary/verified 传给 eda_flow 工具等双 MCP 混淆; P0 区分两 server 参数不互通 (余为 parser 乱码, 非 prompt 可解)",
    "string-not-array": "run_commands 把多条命令拼成一个字符串; P0 直接给数组正反例 (262/321=81.7% 属 run_commands)",
    "unavailable-tool": "调用不存在工具名 / parser 产出乱码工具名; P0 列出两 server 真实工具 (余为 vLLM minicpm5 parser 乱码, infra 层)",
    "wrong-type-boolean": "submit_and_exit 的 verified 传成字符串/数字; P0 明示为布尔",
}
reason_rows = []
total_elim = 0
for reason, cnt in sorted(reject_reasons.items(), key=lambda x: -x[1]):
    er = p0_eliminable.get(reason, 0.0)
    ec = round(cnt * er)
    total_elim += ec
    reason_rows.append({"reason": reason, "count": cnt, "pct_of_total": round(cnt / rejected_total * 100, 1),
                        "p0_eliminable_rate": er, "p0_eliminable_count": ec, "mechanism": MECH.get(reason, "")})

n_genfail = gdd["n_gen_fail"]
zero_rej = gdd["zero_rejections"]
rej_death = n_genfail - zero_rej
dist = gdd["rejection_count_distribution"]
opt_rescue = rej_death * 0.5
cons_rescue = rej_death * (1.0 / 3.0)
opt_pp = opt_rescue * post_gen / N * 100
cons_pp = cons_rescue * post_gen / N * 100

table = {
    "meta": {"generator": "bpt_attribution_t6_report.py",
             "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
             "data_source": "attribution_3615_run1 (36.15 run1, minicpm5-2b-sft-v39-final / global_step_105)"},
    "funnel": {"total_tasks": N, "gen_success": gen_success, "gen_fail": gen_fail, "gen_timeout": gen_timeout,
               "passed": passed, "overall_pass_rate_pct": round(overall * 100, 2),
               "post_gen_pass_rate_pct": round(post_gen * 100, 2)},
    "rejection_total": rejected_total,
    "rejection_by_reason": reason_rows,
    "p0_eliminable_total": total_elim,
    "p0_eliminable_pct": round(total_elim / rejected_total * 100, 1),
    "rejection_by_tool_top": dict(sorted(reject_tools.items(), key=lambda x: -x[1])[:8]),
    "run_commands_share_pct": round(reject_tools.get("run_commands", 0) / rejected_total * 100, 1),
    "run_commands_string_not_array": rc_str_not_arr,
    "six_type_classification": sixtype,
    "t6_genfail_decomposition": {"n_genfail": n_genfail, "silent_no_rejection": zero_rej,
                                 "rejection_death": rej_death, "rejection_count_distribution": dist,
                                 "genfail_used_search_apis": gdd["used_search_apis"],
                                 "genfail_used_run_code": gdd["used_run_code"]},
    "p0_expected_recovery": {"optimistic_delta_pp": round(opt_pp, 1), "conservative_delta_pp": round(cons_pp, 1),
                             "target": "76 个拒绝致死任务 (run_commands 占 80.6% 拒绝)"},
    "blocker": {"item": "A1/A3 单变量消融 (40题) + P0 dev 前后对比 (79题) 须在 36.15 跑",
                "status": "HARD BLOCKED",
                "cause": "36.15 隧道 DOWN: dual-nix-tunnel 需 Windows 中继 172.19.195.133 运行 tunnel.ps1; .17 端口 3333 未监听; 直连 36.15:22 被防火墙阻. run1 21:15 完成时隧道尚通, 约 1.5h 前中继掉线.",
                "who_stuck": "运维/infra (须在 Windows 中继重启 tunnel.ps1); 无法从 .17 单侧修复",
                "eta": "未知 (取决于运维); 隧道恢复后 A1+A3 约 4-5h, P0 dev eval 约 2-3h",
                "model_serve_state": ".17 GPU6:8096 step105-final 健康 (urllib 实测); GPU7:8095 R2-step200 监听中; 唯缺到 36.15 反向隧道 18096"},
}
with open(os.path.join(RUN, "attribution_t6_table.json"), "w", encoding="utf-8") as f:
    json.dump(table, f, ensure_ascii=False, indent=1)
print("wrote attribution_t6_table.json  overall=%.4f elim=%d/%d=%.1f%%" % (overall, total_elim, rejected_total, total_elim / rejected_total * 100))

# ---------- HTML helpers ----------
def esc(s):
    return html.escape(str(s))


def svg_pie(segments, w=240, h=240, r=90, cx=120, cy=120):
    total = sum(v for _, v, _ in segments)
    parts = []
    ang = -math.pi / 2
    for label, v, col in segments:
        if v <= 0:
            continue
        frac = v / total
        a2 = ang + frac * 2 * math.pi
        x1, y1 = cx + r * math.cos(ang), cy + r * math.sin(ang)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        large = 1 if frac > 0.5 else 0
        parts.append('<path d="M%d,%d L%d,%d A%d,%d 0 %d 1 %d,%d Z" fill="%s" stroke="#fff" stroke-width="1.5"/>' % (cx, cy, x1, y1, r, r, large, x2, y2, col))
        ang = a2
    return '<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">%s</svg>' % (w, h, w, h, "".join(parts))


COL = ["#c0392b", "#e67e22", "#2980b9", "#27ae60", "#8e44ad", "#16a085", "#f39c12", "#7f8c8d"]
seg_reason = [(r["reason"], r["count"], COL[i % len(COL)]) for i, r in enumerate(reason_rows)]
seg_six = [(k, v, COL[i % len(COL)]) for i, (k, v) in enumerate(sorted(sixtype.items(), key=lambda x: -x[1]))]
seg_genfail = [("rej-death(76)", rej_death, "#c0392b"), ("silent(45)", zero_rej, "#e67e22")]

reason_table = ""
for r in reason_rows:
    reason_table += ("<tr><td>%s</td><td>%d</td><td>%.1f%%</td><td>%.0f%%</td><td>%d</td><td>%s</td></tr>"
                     % (esc(r["reason"]), r["count"], r["pct_of_total"], r["p0_eliminable_rate"] * 100, r["p0_eliminable_count"], esc(r["mechanism"])))
tool_rows = "".join("<tr><td>%s</td><td>%d</td><td>%.1f%%</td></tr>" % (esc(t), c, c / rejected_total * 100) for t, c in sorted(reject_tools.items(), key=lambda x: -x[1])[:8])
six_rows = "".join("<tr><td>%s</td><td>%d</td><td>%.1f%%</td></tr>" % (esc(k), v, v / N * 100) for k, v in sorted(sixtype.items(), key=lambda x: -x[1]))
rc_share = round(reject_tools.get("run_commands", 0) / rejected_total * 100, 1)
elim_pct = round(total_elim / rejected_total * 100, 1)

CSS = 'body{font-family:"PingFang SC","Microsoft YaHei",Arial,sans-serif;max-width:1100px;margin:0 auto;padding:24px;color:#222;line-height:1.6;background:#fafafa}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:8px}h2{color:#1a5276;margin-top:34px;border-left:5px solid #2980b9;padding-left:10px}table{border-collapse:collapse;width:100%%;margin:12px 0;background:#fff}th,td{border:1px solid #ccc;padding:7px 9px;text-align:left;font-size:13px}th{background:#2980b9;color:#fff}tr:nth-child(even){background:#f2f6fa}.box{background:#fff;border:1px solid #ddd;border-radius:6px;padding:14px 18px;margin:14px 0}.kpi{display:inline-block;background:#2980b9;color:#fff;border-radius:6px;padding:10px 16px;margin:6px 8px 6px 0;font-size:14px}.kpi b{font-size:20px;display:block}.warn{background:#fef5e7;border-left:5px solid #e67e22}.block{background:#fdedec;border-left:5px solid #c0392b}.ok{background:#eafaf1;border-left:5px solid #27ae60}.pie-wrap{display:flex;flex-wrap:wrap;gap:24px;align-items:center;margin:10px 0}.small{font-size:12px;color:#666}code{background:#eee;padding:1px 5px;border-radius:3px}'

doc = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>BaiZe Post-Train T6 归因 (36.15 run1)</title><style>%s</style></head><body>
<h1>BaiZe Stage(ii) Post-Train · T6 工具格式归因报告</h1>
<p class="small">环境: 36.15 run1 · 模型 <code>minicpm5-2b-sft-v39-final</code> (global_step_105) · EDA-Eval-PyAether 158 题 · Pass@1 · 2500s · <code>-p 8 -n</code><br>生成: bpt_attribution_t6_report.py · 数据源 attribution_3615_run1/ · %s</p>
<div class="box ok"><b>一句话结论</b>: 当前最大损失不在「会不会写 EDA 代码」(写出来后通过率 83.3%%), 而在「会不会按 MCP 协议调工具并提交」—— 158 题中 <b>121 题(76.6%%)</b> 卡在 T6 工具格式导致代码生成失败; 全程 <b>1304 次工具调用被拒</b>, 其中 <b>80.6%% 是 <code>run_commands</code></b>。一条 P0 提示补丁预计可消掉约 <b>65.9%%</b> 的拒绝, 乐观 +20pp / 保守 +13pp Pass@1。</div>
<h2>1. 基线漏斗 (已对账 final_report.json)</h2>
<div class="box"><span class="kpi"><b>158</b>总题数</span><span class="kpi"><b>36</b>生成成功</span><span class="kpi"><b>121</b>生成失败</span><span class="kpi"><b>1</b>超时</span><span class="kpi"><b>30</b>通过</span><span class="kpi"><b>18.99%%</b>整体 Pass@1</span><span class="kpi"><b>83.3%%</b>生成后通过率</span><p style="margin-top:12px">漏斗: 158 → 生成成功 36 (22.8%%) → 通过 30 (83.3%%) → 整体 18.99%%。<b>瓶颈在「代码生成完成率」而非「判分能力」</b>。提分主战场 = 让模型把代码写出来并按协议调工具。</p></div>
<h2>2. T6 失败分型 (RCA v2 六类, 按本 run 重算)</h2>
<div class="pie-wrap"><div>%s<br><span class="small">六类分布 (题数)</span></div><div class="box" style="flex:1;min-width:300px"><table><tr><th>类别</th><th>题数</th><th>占比</th></tr>%s</table></div></div>
<p>T6_tool_format_genfail (121) 一类独占 76.6%%, 头号损失项; 其余 T4 断言不足(5)/T5 超时(1)/T3 API 误用(1) 合计仅 7 题。</p>
<h2>3. T6 归因表 · 1304 次拒绝 → 原因分布 → P0 可消比例</h2>
<div class="pie-wrap"><div>%s<br><span class="small">拒绝原因分布 (次数)</span></div></div>
<div class="box"><table><tr><th>拒绝原因</th><th>次数</th><th>占总拒绝</th><th>P0 可消比例</th><th>预计可消</th><th>机制 / P0 对应</th></tr>%s<tr style="background:#eafaf1;font-weight:bold"><td>合计 P0 可消</td><td>—</td><td>—</td><td>—</td><td>%d / 1304</td><td>%.1f%% of 拒绝</td></tr></table></div>
<p class="small">P0 补丁 = <code>attribution_prompt_p0_toolfmt.md</code>: 工具清单段加硬约束(run_commands commands=数组、read_files files=对象数组、submit_and_exit summary/verified 类型、区分两 MCP server 参数不互通)。</p>
<h2>4. 拒绝按工具分布 (Top 8)</h2>
<div class="box"><table><tr><th>工具</th><th>拒绝次数</th><th>占比</th></tr>%s</table><p><code>run_commands</code> 占 <b>%.1f%%</b> 拒绝, 单一最大损失项。其中 <code>string-not-array</code> 262/321=81.7%% 属 run_commands。</p><p class="warn box" style="padding:10px"><b>深层发现</b>: aggregate_tool_calls 里出现大量<b>乱码工具名</b>(如 <code>submitdata/app.e_and003_exit1982</code>), 说明 vLLM <code>minicpm5</code> tool-call parser 把模型输出解析成垃圾工具名 —— 这一层<b>非 prompt 可解</b>, 是 infra/parser 层, P0 只能回收「格式可指导」部分。</p></div>
<h2>5. T6 生成失败分解 · 静默未生成 vs 拒绝致死</h2>
<div class="pie-wrap"><div>%s<br><span class="small">121 个 gen-fail 分解</span></div><div class="box" style="flex:1;min-width:320px"><b>拒绝致死 (76, 62.8%%)</b>: 工具调用被反复拒, 耗尽 turn 预算 → 没产出 .py。P0 直接目标。<br><b>静默未生成 (45, 37.2%%)</b>: 零拒绝, 模型产出文本/乱码工具名但从未成功调工具。P0 不直接覆盖。<br><br><b>关键洞察</b>: 121 个 gen-fail 任务 <code>used_search_apis=0</code> 且 <code>used_run_code=0</code> —— <b>从未进入「检索→执行」回路</b>, 全部 turn 烧在错误工具调用或纯文本上 (与 .17 旧 v2 RCA「仅 9.88%% 题进入检索→执行→修错」一致)。</div></div>
<table><tr><th>每题拒绝次数桶</th><th>0</th><th>1-2</th><th>3-5</th><th>6-10</th><th>11+</th></tr><tr><td>gen-fail 题数</td><td>45</td><td>38</td><td>19</td><td>7</td><td>12</td></tr></table>
<h2>6. P0 预期回收估算 (预注册, 先定后测, 仅排序依据非定论)</h2>
<div class="box"><p>目标: 76 个拒绝致死任务 (run_commands 占 80.6%% 拒绝)。P0 砍 run_commands 拒绝约 60%% → 部分拒绝致死任务完成生成 → 经 83.3%% 生成后通过率转为通过。</p><span class="kpi"><b>+%.1fpp</b>乐观 (救回 1/2=38 题→+32 pass)</span><span class="kpi"><b>+%.1fpp</b>保守 (救回 1/3=25 题→+21 pass)</span><p class="small" style="margin-top:10px"><b>上限警告</b>: 受 vLLM minicpm5 tool-call parser 乱码工具名限制, 该层非 prompt 可解。45 个静默未生成任务 P0 不直接覆盖。最终数字须在 36.15 用 A1/A3 + P0 dev eval 单变量实测 + McNemar 检验。</p></div>
<h2>7. 今夜执行状态与阻塞 (诚实记录)</h2>
<div class="block box"><p><b>已完成 (CPU, 本轮交付)</b>: ✅ T6 归因表(本报告 + attribution_t6_table.json) · ✅ POSTTRAIN_PLAN_NEXT.md 计划填妥 · ✅ EXPERIMENTS_POSTTRAIN.md 新节 · ✅ P0/P1/P2/P3 补丁模板 + dev-eval runner run-ready (wake503) · ✅ 40 题分层子集 + 79/79 train/dev 拆分。</p><p><b>HARD BLOCKED</b>: ❌ A1/A3 两臂 40 题结果 · ❌ P0 dev 前后对比 —— 两者<b>必须在 36.15 跑</b> (15:4x 用户令)。<br><b>卡在哪</b>: 36.15 隧道 DOWN。dual-nix-tunnel 需 Windows 中继 <code>172.19.195.133</code> 运行 <code>tunnel.ps1</code>; .17 端口 3333 未监听、无 ssh -p3333 进程; 直连 36.15:22 被防火墙阻。run1 21:15 完成时隧道尚通, 约 1.5h 前中继掉线。<br><b>谁在卡</b>: 运维/infra —— 须在 Windows 中继重启 <code>tunnel.ps1</code>; <b>无法从 .17 单侧修复</b>。<br><b>ETA</b>: 未知(取决于运维)。隧道恢复后 A1+A3 约 4-5h、P0 dev eval 约 2-3h。<br><b>已就绪等待</b>: .17 GPU6:8096 step105-final 服务健康(urllib 实测); GPU7:8095 R2-step200 监听中; 补丁模板/split/runner 全 <code>--dry-run</code> 验证通过。隧道一恢复即可 <code>ssh -p3333 -fN -R 18096:localhost:8096 ...</code> 起跑。</p></div>
<h2>8. 可复算命令</h2>
<div class="box"><pre style="font-size:12px;white-space:pre-wrap">python3 bpt_attribution_t6_report.py   # 复算 T6 归因表 + 本报告\nls attribution_3615_run1/               # final_report.json codegen_rejection_stats.json execution_results.jsonl\nbash bpt_attribution_ablation.sh --arm A1 --dry-run   # 隧道恢复后在 36.15\nbash bpt_attribution_ablation.sh --arm A3 --dry-run\nbash bpt_attribution_prompt_dev_eval.sh --patch p0 --split dev --dry-run</pre></div>
<p class="small" style="margin-top:30px;color:#999">BaiZe Stage(ii) Post-Train · 归因线 · commit 前缀 <code>posttrain attribution:</code> · 不改 benchmark/check.py/题面, 单变量预注册, 先 dev 后 test, 反作弊常开。</p></body></html>""" % (CSS, esc(table["meta"]["generated_at"]), svg_pie(seg_six), six_rows, svg_pie(seg_reason), reason_table, total_elim, elim_pct, tool_rows, rc_share, svg_pie(seg_genfail), opt_pp, cons_pp)
with open(os.path.join(REPORTS, "report_posttrain_attribution_t6_zh.html"), "w", encoding="utf-8") as f:
    f.write(doc)
print("wrote reports/report_posttrain_attribution_t6_zh.html")
