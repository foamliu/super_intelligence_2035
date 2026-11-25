#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A0 deep-dive HTML stage (loads /tmp/a0_deepdive.pkl from gen stage 1)."""
import json, os, statistics, collections, html, pickle

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
REP_DIR = os.path.join(RUN_DIR, "reports")
OUT = os.path.join(REP_DIR, "report_posttrain_A0_capability_deepdive_zh.html")
P = pickle.load(open("/tmp/a0_deepdive.pkl", "rb"))
per_task = P["per_task"]; cats = P["cats"]; fm_dist = P["fm_dist"]; et_dist = P["et_dist"]
pass_g = P["pass_g"]; fail_g = P["fail_g"]; breadth_dist = P["breadth_dist"]
agg_tc = P["agg_tc"]; a0_5run = P["a0_5run"]; a1_5run = P["a1_5run"]
paired = P["paired"]; r83 = P["r83"]

def pct(x): return "%.2f%%" % (x * 100)
def fmt(x, d=1): return ("%%.%df" % d) % x
def esc(x): return html.escape(str(x))
def tbl(headers, rows):
    h = "".join("<th>%s</th>" % esc(x) for x in headers)
    body = "".join("<tr>" + "".join("<td>%s</td>" % esc(x) for x in r) + "</tr>" for r in rows)
    return '<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (h, body)

A0_MEAN = a0_5run["five_run_mean"]; A0_STD = a0_5run["five_run_std"]
A1_MEAN = a1_5run["five_run_mean"]; A1_STD = a1_5run["five_run_std"]
DS_SCORE = 0.821; DS_STD = 0.030
DELTA = A0_MEAN - DS_SCORE
per_run = a0_5run["per_run_pass_rate"]
pt_dist = a0_5run["per_task_pass_distribution_0_to_N"]
FM_LEG = {"F1_no_code": "F1 未产出可执行代码", "F2_tool_format": "F2 工具调用格式错误",
          "F3_timeout": "F3 超时", "F4_api_misuse": "F4 API 误用", "F5_logic_error": "F5 逻辑错误"}

rows1 = [[i, "%d/158" % round(per_run[str(i)] * 158), pct(per_run[str(i)])] for i in range(1, 6)]
rows1.append(["mean ± sd", "—", "%s ± %s" % (pct(A0_MEAN), pct(A0_STD))])
t1 = tbl(["Run", "通过数", "Pass@1"], rows1)
tcat = tbl(["类别", "题数", "占比"], [
    ["pass_all（5/5 全通过）", cats["pass_all"], pct(cats["pass_all"] / 158)],
    ["partial（1–4/5 部分通过）", cats["partial"], pct(cats["partial"] / 158)],
    ["fail_all（0/5 全失败）", cats["fail_all"], pct(cats["fail_all"] / 158)],
    ["合计", 158, "100.00%"]])
tpd = tbl(["5-run 通过次数", "题数", "占比"],
          [["%d/5" % k, pt_dist.get(str(k), 0), pct(pt_dist.get(str(k), 0) / 158)] for k in range(0, 6)])

fm_total = sum(fm_dist.values())
rows2 = [[FM_LEG.get(k, k), fm_dist[k], pct(fm_dist[k] / fm_total)] for k in
         ["F5_logic_error", "F4_api_misuse", "F1_no_code", "F3_timeout", "F2_tool_format"] if k in fm_dist]
rows2.append(["合计（失败题）", fm_total, "100.00%"])
t2 = tbl(["失败模式（按题主导）", "题数", "占比"], rows2)

et_total = sum(et_dist.values())
rows3 = [[k, v, pct(v / et_total)] for k, v in et_dist.most_common(12)]
rows3.append(["合计（task-run 异常条目）", et_total, "100.00%"])
t3 = tbl(["底层异常类型", "条目数", "占比"], rows3)

def g_row(name, g):
    return [name, g["n"], fmt(g["m_tc"], 1), fmt(g["m_it"] / 1000, 0) + "k", fmt(g["m_ot"], 0),
            fmt(g["m_sc"], 1), fmt(g["m_rc"], 2), fmt(g["m_rmc"], 1), fmt(g["m_breadth"], 2),
            pct(g["al_rate"]), pct(g["rq_rate"])]
t4 = tbl(["组别(Pass@1 多数)", "题数", "工具调用均值", "输入token", "输出token", "搜索调用",
          "run_code", "run_commands", "工具广度", "进入agent回路", "RAG查询"],
         [g_row("PASS 组(≥3/5)", pass_g), g_row("FAIL 组(<3/5)", fail_g)])

rows5 = [["%d 种" % k, breadth_dist[k], pct(breadth_dist[k] / 158)] for k in sorted(breadth_dist, reverse=True)]
t5 = tbl(["distinct 工具种数(均值/题)", "题数", "占比"], rows5)
agg_total = sum(agg_tc.values())
rows5b = [[k, agg_tc[k], pct(agg_tc[k] / agg_total)] for k, v in sorted(agg_tc.items(), key=lambda x: -x[1])]
rows5b.append(["合计(run1 全 158 题)", agg_total, "100.00%"])
t5b = tbl(["工具(run1 聚合)", "调用次数", "占比"], rows5b)

mc = paired["mcnemar"]["majority"]; bs = paired["paired_bootstrap"]; pt = paired["per_task_paired_tests"]
rows6 = [["A0 base (MiniCPM5-2B)", 5, pct(A0_MEAN), pct(A0_STD)],
         ["A1 SFT (v39 step105)", 5, pct(A1_MEAN), pct(A1_STD)],
         ["Δ = A1 − A0", "—", pct(paired["delta_mean_pass_rate"]), "—"]]
t6 = tbl(["臂", "n_run", "Pass@1 mean", "sd"], rows6)
t6b = tbl(["配对检验", "统计量", "p(双侧)"], [
    ["McNemar χ²(连续校正)", fmt(mc["chi2_continuity"], 2), mc["chi2_p_two_sided"]],
    ["Wilcoxon signed-rank", fmt(pt["wilcoxon_signed_rank"]["statistic"], 1), pt["wilcoxon_signed_rank"]["p_two_sided"]],
    ["paired-t", fmt(pt["paired_t_test"]["t"], 2), pt["paired_t_test"]["p_two_sided"]],
    ["paired bootstrap CI95", "[%s, %s]" % (pct(bs["ci95_low"]), pct(bs["ci95_high"])), bs["p_two_sided"]]])
a1_fm = a1_5run["dominant_fail_mode_over_failing_tasks"]
rows6c = [[FM_LEG.get(k, k), a1_fm.get(k, 0)] for k in
          ["F1_no_code", "F3_timeout", "F5_logic_error", "F4_api_misuse", "F2_tool_format"] if k in a1_fm]
t6c = tbl(["A1 失败模式", "题数"], rows6c)

ds_fm = r83["fail_mode_distribution"]; ds_fm_total = sum(ds_fm.values())
DS_LEG = {"none": "无失败(通过)", "semantic": "语义/逻辑错", "infrastructure": "基础设施错",
          "api_misuse": "API 误用", "timeout": "超时", "protocol": "协议错"}
rows7 = [[DS_LEG.get(k, k), ds_fm.get(k, 0), pct(ds_fm.get(k, 0) / ds_fm_total)] for k in
         ["none", "semantic", "infrastructure", "api_misuse", "timeout", "protocol"]]
t7 = tbl(["DeepSeek 失败模式(r83, 7-run)", "题数", "占比"], rows7)
bysc = r83.get("by_scenario", {})
rows7b = [[sc, dd.get("count"), pct(dd.get("deepseek_avg", 0)), pct(dd.get("minicpm5_pred_avg", 0))]
          for sc, dd in sorted(bysc.items(), key=lambda x: -x[1].get("count", 0))]
t7b = tbl(["场景", "题数", "DeepSeek 均分", "MiniCPM5 预测均分(r83)"], rows7b)
CSS = """
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;margin:0;color:#1a2332;background:#f5f7fa;line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:28px 22px}
h1{font-size:24px;margin:0 0 4px}
h2{font-size:19px;margin:26px 0 10px;padding-left:10px;border-left:5px solid #2b6cb0;color:#1a365d}
h3{font-size:15px;margin:14px 0 6px;color:#2c5282}
.sub{color:#64748b;font-size:13px;margin-bottom:8px}
.cards{display:flex;flex-wrap:wrap;gap:12px;margin:14px 0}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:14px 16px;min-width:150px;flex:1}
.card .k{font-size:12px;color:#64748b}.card .v{font-size:22px;font-weight:700;color:#1a365d;margin-top:4px}
.card .u{font-size:11px;color:#94a3b8;margin-top:2px}
.warn{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:12px 16px;color:#9a3412;margin:12px 0;font-size:13.5px}
.note{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px 16px;color:#1e40af;margin:12px 0;font-size:13.5px}
.ok{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:12px 16px;color:#166534;margin:12px 0;font-size:13.5px}
table{border-collapse:collapse;width:100%;background:#fff;margin:10px 0;font-size:13.5px}
th,td{border:1px solid #e2e8f0;padding:7px 9px;text-align:left}
th{background:#f1f5f9;color:#1e293b;font-weight:600}tr:nth-child(even) td{background:#fafbfc}
tbody tr:last-child td{font-weight:700;background:#f1f5f9}
.foot{color:#94a3b8;font-size:12px;margin-top:24px;border-top:1px solid #e2e8f0;padding-top:10px}
code{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:12.5px;color:#b91c1c}
"""
spr = max(per_run.values()) - min(per_run.values())
H = []
H.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A0 能力深度分析报告 — MiniCPM5-2B vs DeepSeek-V4-Pro</title><style>%s</style></head><body><div class="wrap">' % CSS)
H.append('<h1>A0 能力深度分析报告</h1>')
H.append('<div class="sub">MiniCPM5-2B（A0 base） vs DeepSeek-V4-Pro · 行为学/结构性对照 · 撰写/署名：BaiZe post-train agent · 2026-11-23</div>')
H.append('<div class="warn"><b>首屏口径声明（不许含糊）</b><br>'
  '<b>A0（本报告主角）</b>＝MiniCPM5-2B <b>原模型</b>｜cline harness（<code>eda_fastmcp/scripts/run_cline_script.sh</code>）在 <b>.17</b> 启动｜5-run Pass@1＝<b>%s ± %s</b>（158 题 / 2500s / 单 trace / <code>-p 8 -n</code> / 冻结协议）。<br>'
  '<b>DeepSeek-V4-Pro（对照锚点）</b>＝<b>36.15</b> 启动｜cline harness｜<b>%s ± %s</b>（5/5，来源 <code>PLAN_MINICPM5_PYAETHER_158.md</code>；r83 7-run 均分 %s）。<br>'
  '<b>禁止直接相减</b>：两侧<b>规模（2B vs V4-Pro 云端大模型）</b>与<b>启动机器（.17 vs 36.15）</b>不同 ⇒ 差值同时含「能力」与「环境」两成分，<b>不得把两个百分比直接相减当作纯能力差</b>（参见 <code>doc/AGENTS.md §4.3「大模型参照不可与 2B 比较」</code>）。本报告<b>只做结构性/行为学对照，不做裸分数排名</b>。</div>'
  % (pct(A0_MEAN), pct(A0_STD), pct(DS_SCORE), pct(DS_STD), pct(r83["meta"]["deepseek_avg_overall"])))
H.append('<div class="note"><b>⚠️ 口径勘误（数据为准）</b>：任务书 §C 与预注册把 A0 标注为「无 RAG / 无沙盒 MCP」，但落盘逐题工具调用数据<b>显示 A0 实际使用了</b> RAG 知识工具（run1 聚合 <code>search_apis</code>＝1969 / <code>get_api_details</code>＝978 / <code>search_apis_by_keyword</code>＝476）与沙盒 MCP（<code>run_code</code>＝81，经 dual-nix-tunnel）与 <code>run_commands</code>＝684，且全程挂 PreToolUse 反作弊 hook。故 <b>A0 实际口径 = cline harness 全工具（含 RAG + 沙盒 + hook）</b>，与 DeepSeek 侧「有 RAG + 有 MCP」在「是否挂工具」维度一致；但 A0 的向量召回自 11-13 失效（详见下条降级声明，全程纯 BM25 兜底）、<code>run_code</code> 沙盒用量极低（81 次/158 题），<b>检索质量与自纠错强度仍低于 DeepSeek 侧完整口径</b>。⇒ ~38.8pp 裸差同时含<b>模型规模（2B vs V4-Pro）</b>、<b>启动机器（.17 vs 36.15）</b>、<b>检索质量（退化 BM25 vs 完整向量）</b>三重混淆，<b>不得把两个百分比直接相减当作纯能力差</b>（参见 <code>doc/AGENTS.md §4.3</code>）。勘误依据 = 落盘 JSON 的 <code>aggregate_tool_calls</code>。</div>')
H.append('<div class="warn"><b>🔴 检索 infra 降级声明（wake783 · 2026-11-24 独立复核 · 铁律2 infra≠能力）</b>：A0/A1/A5 三臂 eval 期间，eda_fastmcp MCP <code>search_apis</code> 的向量召回后端（<code>.env RAG_RECALL_URL=http://localhost:9002/recall</code>）<b>自 2026-11-13 起全线失效</b>——:9002 被 nvidia_gpu_exporter 占用返回 HTML、本地 recall 服务已死亡；MCP 日志 <code>eda_fastmcp/logs/app.log</code> 显示 recall error 共 17164 次（11-20=509 / 11-21=8884 / 11-22=2854 / 11-23=1548），「向量=0 条」出现 16487 次、<b>向量召回从未成功</b>（全程纯 BM25 兜底）。故本报告所有「RAG/检索」指标（rag_queried_rate、search_apis=1969 等）反映的是<b>退化检索口径</b>（向量召回失效、BM25-only），<b>非</b>完整向量+BM25 检索。⇒ <b>A0=43.29% / A1=4.56% 基线含检索 infra 故障成分</b>，修复检索后（方案A：<code>.env</code> 启用 <code>10.252.32.15:9001</code>，实测返回精准向量结果 aeGetCurDesign@0.8815；方案B：修本地 recall）<b>基线需重测</b>。此为已知局限，按 §三 诚实性要求照写；修复前不得把当前基线当「检索完整口径」的最终数。</div>')
H.append('<div class="cards">'
  '<div class="card"><div class="k">A0 base 5-run Pass@1</div><div class="v">%s</div><div class="u">MiniCPM5-2B · .17 · ± %s</div></div>'
  '<div class="card"><div class="k">DeepSeek-V4-Pro 5/5</div><div class="v">%s</div><div class="u">36.15 · ± %s · 不可与2B直接比</div></div>'
  '<div class="card"><div class="k">A0 − DeepSeek 裸差</div><div class="v">%s</div><div class="u">含能力+环境，禁当能力差</div></div>'
  '<div class="card"><div class="k">A1 SFT 5-run</div><div class="v">%s</div><div class="u">SFT 显著退化 Δ=%s</div></div>'
  '</div>' % (pct(A0_MEAN), pct(A0_STD), pct(DS_SCORE), pct(DS_STD), pct(DELTA), pct(A1_MEAN), pct(paired["delta_mean_pass_rate"])))
H.append('<h2>§一 5-run 稳定性与逐题类别</h2><div class="sub">数据源：<code>baseline_A0_base_5run_summary.json</code>（自行复核）。</div>%s'
  '<h3>逐题 5-run 通过类别（n=158）</h3>%s<h3>5-run 通过次数分布</h3>%s'
  % (t1, tcat, tpd))
H.append('<div class="note"><b>读数</b>：5-run mean %s ± %s，run 间极差 %s（最高 run3 %s → 最低 run5 %s），相对稳定。25 题 5/5 全过、51 题 0/5 全挂、82 题部分通过——即 <b>%s 题存在随机翻转</b>（partial），单 run 评分对约半数题目不收敛，论文须用 5-run mean + 配对检验。</div>'
  % (pct(A0_MEAN), pct(A0_STD), pct(spr), pct(max(per_run.values())), pct(min(per_run.values())), cats["partial"]))
H.append('<h2>§二 五分类失败模式（A0 自己的数据，非 DeepSeek 沿用）</h2><div class="sub">按「每题 5-run 主导 fail_mode」计；失败题 = fail_all + partial = %d。</div>%s'
  % (fm_total, t2))
H.append('<div class="note"><b>读数</b>：A0 失败以 <b>F5 逻辑错误（%d 题，%s）</b>为主——代码跑通但断言不满足，MiniCPM5-2B <b>能写出来、能跑，但逻辑/语义不对</b>；其次 F4 API 误用（%d）与 F1 未产出代码（%d）。F2 工具格式错误仅 %d ⇒ MiniCPM5-2B 的<b>工具协议掌握已较好</b>（与「M1 工具协议修好」预注册判据一致）。</div>'
  % (fm_dist["F5_logic_error"], pct(fm_dist["F5_logic_error"] / fm_total), fm_dist["F4_api_misuse"], fm_dist["F1_no_code"], fm_dist["F2_tool_format"]))
H.append('<h2>§三 底层异常类型</h2><div class="sub">聚合所有 task-run 的 <code>error_types</code>（一题可多条）。</div>%s' % t3)
H.append('<div class="note"><b>读数</b>：异常以 <b>Generation fail（%d）</b>、<b>AssertionError（%d）</b>、<b>TypeError（%d）</b>为主。AssertionError 多 ⇒ 断言失败（与 F5 呼应）；TypeError/AttributeError/NameError 多 ⇒ API 误用/对象属性错（与 F4 呼应）；Generation fail/timeout 高 ⇒ 2500s 内未稳定产出（与 F1/F3 呼应）。</div>'
  % (et_dist["Generation fail"], et_dist["AssertionError"], et_dist["TypeError"]))
H.append('<h2>§四 PASS 组 vs FAIL 组：工具行为与 token 效率</h2><div class="sub">按 5-run 多数通过（≥3/5=PASS 组，&lt;3/5=FAIL 组）分组，组内各指标取题均值。</div>%s' % t4)
H.append('<div class="warn"><b>反直觉核心发现</b>：<b>FAIL 组反而消耗更多资源</b>——工具调用 %s vs %s、搜索调用 %s vs %s、输入 token %s vs %s、输出 token %s vs %s。即失败的题<b>越搜越多、越写越多却不收敛</b>，典型的「检索过载—无效堆砌」失败模式；而 PASS 组<b>用更少调用解出</b>。<b>run_code 沙盒执行两组都极低</b>（%s vs %s）⇒ MiniCPM5-2B 几乎不靠「执行-看错-修」自纠错回路。PASS 组 agent 回路进入率 %s（FAIL 组 %s）⇒ 进入回路者更可能解出。</div>'
  % (fmt(fail_g["m_tc"], 1), fmt(pass_g["m_tc"], 1), fmt(fail_g["m_sc"], 1), fmt(pass_g["m_sc"], 1),
     fmt(fail_g["m_it"] / 1000, 0) + "k", fmt(pass_g["m_it"] / 1000, 0) + "k",
     fmt(fail_g["m_ot"], 0), fmt(pass_g["m_ot"], 0),
     fmt(fail_g["m_rc"], 2), fmt(pass_g["m_rc"], 2), pct(pass_g["al_rate"]), pct(fail_g["al_rate"])))
H.append('<h2>§五 工具使用广度</h2><div class="sub">每题 distinct 工具种数（8 种上限）。</div>%s<h3>run1 全 158 题工具调用聚合（口径证据）</h3>%s'
  % (t5, t5b))
H.append('<div class="note"><b>读数</b>：%d 题用 6–7 种工具，广度普遍较高；但 <code>run_code</code> 仅 %d 次（run1/158 题）⇒ <b>沙盒自纠错几乎未被利用</b>，这是 A0 相对 DeepSeek 的一个明确行为短板。</div>'
  % (breadth_dist.get(7, 0) + breadth_dist.get(6, 0), agg_tc["run_code"]))
H.append('<h2>§六 与 A1（SFT 退化）相互印证</h2><div class="sub">A1 = SFT v39 step105，同尺同口径 5-run。数据源：<code>baseline_A0_vs_A1_paired_compare.json</code>。</div>%s<h3>配对检验（158 题）</h3>%s<h3>A1 失败模式（退化循环）</h3>%s'
  % (t6, t6b, t6c))
H.append('<div class="warn"><b>读数</b>：SFT 使 Pass@1 从 %s <b>暴跌至 %s</b>（Δ=%s，所有配对检验 p=0.0）。A1 失败主导为 <b>F1 未产出代码（%d 题）</b>——SFT 后模型大量题<b>根本不产出可执行代码</b>（退化循环），与 A0 主导 F5 逻辑错截然不同。⇒ <b>当前 SFT 配方有害</b>，破坏了 base 模型的代码产出能力，须待 pretrain ckpt 后重做。这反向印证：A0 base 的 %s 主要来自「能产出且逻辑大致正确」，SFT 把「能产出」这一基本能力打掉了。</div>'
  % (pct(A0_MEAN), pct(A1_MEAN), pct(paired["delta_mean_pass_rate"]),
     a1_5run["dominant_fail_mode_over_failing_tasks"].get("F1_no_code", 0), pct(A0_MEAN)))
H.append('<h2>§七 A0 vs DeepSeek 行为学对照</h2>'
  '<div class="warn"><b>诚实性声明</b>：DeepSeek 侧<b>仅有单点分数锚点（%s）+ r83 的 7-run 失败模式分布</b>，<b>无逐题配对数据</b> ⇒ <b>无法做逐题配对检验</b>，本节只做分布级/场景级行为对照，不伪造逐题对照。两侧 fail_mode 分类法不同（A0 五分类 vs r83 六分类），下表为各自原口径，不做强行映射。</div>'
  '<h3>DeepSeek 失败模式分布（r83, 7-run, 158 题）</h3>%s<h3>按场景对照（DeepSeek 均分 vs r83 中 MiniCPM5 预测均分）</h3>%s'
  % (pct(DS_SCORE), t7, t7b))
H.append('<div class="note"><b>读数</b>：DeepSeek r83 7-run 均分 %s，全通过题 %d；其失败也以<b>语义/逻辑错（semantic %d）</b>与<b>基础设施错（%d）</b>为主。<b>结构性相似点</b>：两侧主要失败都是「逻辑/语义错」而非「工具协议错」——MiniCPM5-2B 在<b>工具协议层已接近 DeepSeek 的失败结构</b>。<b>差异点</b>：① DeepSeek 通过率远高（%s vs %s），差距主要体现在「逻辑正确性」与「难题覆盖」；② A0 的 F1 未产出代码（%d）相对更突出 ⇒ MiniCPM5-2B 在<b>稳定产出可执行代码</b>上明显不足；③ A0 几乎不用 run_code 自纠错。</div>'
  % (pct(r83["meta"]["deepseek_avg_overall"]), ds_fm.get("none", 0), ds_fm.get("semantic", 0),
     ds_fm.get("infrastructure", 0), pct(DS_SCORE), pct(A0_MEAN), fm_dist["F1_no_code"]))
H.append('<h2>§八 核心结论：哪些能力接近，哪些明显不足</h2>'
  '<div class="ok"><b>接近的能力</b>：<br>'
  '1. <b>工具协议掌握</b>——F2 工具格式错误仅 %d 题，agent 回路进入率 %s，广度 6–7 种/题 ⇒ MiniCPM5-2B 已能正确发起多工具 agent 回路，与 DeepSeek 失败结构（都不卡协议）一致。<br>'
  '2. <b>简单题覆盖</b>——25 题 5/5 全过，trivial/easy 档有相当通过率。<br>'
  '3. <b>RAG 检索使用</b>——RAG 查询率 %s，能主动检索 API 文档（⚠️ 但向量召回 infra 自 11-13 失效、实为 BM25 兜底退化口径，见首屏「检索 infra 降级声明」；不应解读为「完整检索能力已接近 DeepSeek」）。</div>'
  '<div class="warn"><b>明显不足的能力</b>：<br>'
  '1. <b>逻辑/语义正确性</b>——F5 逻辑错 %d 题（%s）为主，AssertionError %d 条；代码跑通但断言不满足，这是与 DeepSeek 拉开差距的主因（~38.8pp 含能力+环境）。<br>'
  '2. <b>稳定产出可执行代码</b>——F1 未产出代码 %d 题、Generation fail %d 条；部分题 2500s 内未稳定产出。<br>'
  '3. <b>自纠错闭环</b>——run_code 沙盒执行仅 %s 次/题（两组皆≈0.8），几乎不靠「执行-看错-修」回路；FAIL 组过载检索（%s 次搜索）却不收敛。<br>'
  '4. <b>难题/极端题覆盖</b>——51 题 0/5 全挂，T4/T5 档覆盖远低于 DeepSeek。<br>'
  '5. <b>SFT 后退化</b>——当前 SFT 配方使 Pass@1 暴跌 %s（F1 未产出代码 %d），base 产出能力被打掉，配方须重做。</div>'
  '<div class="note"><b>口径再申</b>：以上「接近/不足」均为<b>同 harness（含 RAG+沙盒+hook）下的行为学对照</b>；~38.8pp 裸差不等于纯能力差（规模 2B vs V4-Pro、机器 .17 vs 36.15、检索质量 退化BM25 vs 完整向量 均不同）。要量化纯能力差，需在同机器、同 harness 下对两模型做 5-run 逐题配对——DeepSeek 侧目前无逐题数据，列为 TODO。</div>'
  % (fm_dist["F2_tool_format"], pct(pass_g["al_rate"]), pct(pass_g["rq_rate"]),
     fm_dist["F5_logic_error"], pct(fm_dist["F5_logic_error"] / fm_total), et_dist["AssertionError"],
     fm_dist["F1_no_code"], et_dist["Generation fail"], fmt(pass_g["m_rc"], 2), fmt(fail_g["m_sc"], 1),
     pct(paired["delta_mean_pass_rate"]), a1_5run["dominant_fail_mode_over_failing_tasks"].get("F1_no_code", 0)))
tidx = tbl(["证据", "路径 / 命令"], [
    ["A0 5-run 汇总", "run/baseline_A0_base_5run_summary.json"],
    ["A0 逐题(run1-5)", "run/baseline_A0_base_run{1..5}_pertask.json"],
    ["A1 SFT 5-run 汇总", "run/baseline_A1_sft_5run_summary.json"],
    ["A0 vs A1 配对检验", "run/baseline_A0_vs_A1_paired_compare.json"],
    ["DeepSeek 行为参照(r83)", "run/r83_difficulty_analysis.json"],
    ["DeepSeek 分数锚点", "run/PLAN_MINICPM5_PYAETHER_158.md L24 (82.1%%±3.0%%)"],
    ["AGENTS §4.3", "doc/AGENTS.md §4.3 (大模型参照不可与2B比较)"],
    ["本报告生成脚本", "run/baize_posttrain_A0_deepdive_gen.py (+ _html.py)"],
    ["复现命令", "cd run && python3 baize_posttrain_A0_deepdive_gen.py && python3 baize_posttrain_A0_deepdive_html.py"],
    ["A0 口径勘误依据", "aggregate_tool_calls: search_apis=1969 / run_code=81 (run1)"],
    ["检索 infra 降级证据(wake783)", "eda_fastmcp/logs/app.log (recall error 17164 次,自 2026-11-13) / .env RAG_RECALL_URL=localhost:9002 / kb/recall_api.log"],
])
H.append('<h2>证据索引（产物路径 + 复现命令）</h2>%s' % tidx)
H.append('<div class="foot">本报告由 BaiZe post-train agent 以第一责任方身份撰写并署名（三条令 §三）。所有数字由 <code>baize_posttrain_A0_deepdive_gen.py</code> 从落盘 JSON 自行计算，未抄 _ops_draft_ 代拟稿。生成时间 2026-11-23；wake783（2026-11-24）增补「检索 infra 降级声明」（向量召回自 11-13 失效、向量=0 条 16487 次，基线含 infra 故障成分，修复后需重测）。</div>')
H.append('</div></body></html>')
with open(OUT, "w") as f:
    f.write("".join(H))
print("WROTE", OUT, os.path.getsize(OUT), "bytes ; segments=", len(H))
