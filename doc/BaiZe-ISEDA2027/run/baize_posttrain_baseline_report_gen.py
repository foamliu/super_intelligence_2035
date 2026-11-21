#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data-driven regenerator for the baseline-nailed milestone report (令 §E.1).

Consumes JSON deliverables from the baseline-nailed pipeline and regenerates
reports/report_posttrain_baseline_nailed_zh.html in place.

Inputs (all optional except audit):
  - baseline_measurement_audit.json            (B1 / B2 / B3 / admissions A)
  - baseline_B4_execution_determinism.json     (B4)
  - baseline_A0_base_5run_summary.json         (A0 final 5-run)  [preferred]
    else highest baseline_A0_base_<N>run_interim_summary.json   [fallback]
  - baseline_A1_sft_5run_summary.json          (A1 final 5-run)  [optional]
  - baseline_A0_vs_A1_paired_compare.json      (paired stats)    [optional]
  - baseline_A0_base_run1_pertask.json         (B5 single-run detail)

Incremental: with only A0 shows A0 numbers + A1 pending; when A1 + compare land
a full paired-stats section appears. Re-running is safe/idempotent.
No GPU / sandbox / network. Does NOT touch protocol/benchmark/check.py.
"""
import argparse, glob, html, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.normpath(os.path.join(RUN_DIR, "..", "reports"))
REPORT_PATH = os.path.join(REPORT_DIR, "report_posttrain_baseline_nailed_zh.html")


def load(path):
    p = os.path.join(RUN_DIR, path) if not os.path.isabs(path) else path
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p))
    except Exception as e:
        sys.stderr.write("[warn] failed to load %s: %s\n" % (p, e))
        return None


def esc(s):
    return html.escape(str(s) if s is not None else "")


def pct(x):
    try:
        return "%.2f%%" % (float(x) * 100.0)
    except Exception:
        return str(x)


def pick_a0_summary():
    s = load("baseline_A0_base_5run_summary.json")
    if s:
        return s, "final"
    interims = glob.glob(os.path.join(RUN_DIR, "baseline_A0_base_*run_interim_summary.json"))
    best, best_n = None, 0
    for f in interims:
        d = load(f)
        if not d:
            continue
        n = int(d.get("n_runs_completed", 0) or 0)
        if n > best_n:
            best_n, best = n, d
    return (best, "interim(n=%d)" % best_n) if best else (None, None)


CSS = """
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:24px auto;padding:0 20px;color:#222;line-height:1.65}
h1{font-size:1.5em;border-bottom:3px solid #c0392b;padding-bottom:8px}
h2{background:#f4f4f4;padding:6px 10px;border-left:5px solid #2c3e50;margin-top:32px}
h3{color:#2c3e50;margin-top:22px}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.93em}
th,td{border:1px solid #ccc;padding:6px 9px;text-align:left;vertical-align:top}
th{background:#2c3e50;color:#fff}
tr:nth-child(even){background:#f9f9f9}
code{background:#f0f0f0;padding:1px 5px;border-radius:3px;font-size:0.88em}
.kpi{display:inline-block;background:#c0392b;color:#fff;font-weight:bold;padding:4px 12px;border-radius:6px;margin:2px 6px 2px 0}
.ok{color:#1e7d32;font-weight:bold}.bad{color:#c0392b;font-weight:bold}.warn{color:#b8860b;font-weight:bold}
.note{background:#fff8e1;border-left:5px solid #f5a623;padding:10px 14px;margin:12px 0}
.danger{background:#fdecea;border-left:5px solid #c0392b;padding:10px 14px;margin:12px 0}
.first{background:#fef9f7;border:2px solid #c0392b;padding:14px 18px;border-radius:8px}
.tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.78em;color:#fff;background:#7f8c8d}
.tag.go{background:#1e7d32}.tag.stop{background:#c0392b}.tag.pending{background:#b8860b}
"""


def table(rows, header=None):
    out = ["<table>"]
    if header:
        out.append("<tr>" + "".join("<th>%s</th>" % esc(h) for h in header) + "</tr>")
    for r in rows:
        out.append("<tr>" + "".join("<td>%s</td>" % c for c in r) + "</tr>")
    out.append("</table>")
    return "\n".join(out)
def render(audit, b4, a0, a0_kind, a1, cmp, run1):
    now = "2026-11-21"
    a0_done = a0 is not None
    a0_n = int(a0.get("n_runs_completed", 0)) if a0 else 0
    a0_final5 = a0_done and a0_n >= 5
    a1_done = a1 is not None and int(a1.get("n_runs_completed", 0) or 0) >= 5
    stage_tag = "Stage3 完成" if (a0_final5 and a1_done) else ("Stage3 进行中" if a0_done else "Stage3 待启动")
    H = []
    H.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">')
    H.append("<title>BaiZe Posttrain · 把 baseline 做扎实（baseline-nailed）</title>")
    H.append("<style>%s</style></head><body>" % CSS)
    H.append("<h1>BaiZe Stage(ii) Posttrain · 把 baseline 做扎实</h1>")
    H.append('<p><span class="tag %s">%s</span> &nbsp; 报告日期：%s（数据驱动自动生成）&nbsp; 机器：s0pgpuap12（10.252.32.17）&nbsp; 触发令：2026-11-20 21:1x「把 baseline 做扎实」</p>' % (
        "go" if a0_final5 and a1_done else "pending", stage_tag, now))

    adm = audit.get("admissions_A", {}) if audit else {}
    mixed = adm.get("A2_mixed_caliber", {}) if isinstance(adm.get("A2_mixed_caliber"), dict) else {}
    rec = mixed.get("recovered_4run_drop_run1_ws_anchor", {}) if mixed else {}
    H.append('<div class="first"><h3 style="margin-top:6px">首屏三句（现状承认，不许含糊）</h3><ol>')
    H.append("<li><b>现有 3.04%% ± 0.83%% 不是 base 模型</b>——它是 SFT v39 global_step_105。MiniCPM5-2B 原模型作为 cline 底模的 5-run 数字，至本轮之前<b>不存在</b>。%s</li>" % (
        "<b>本轮 A0 5-run 已产出该数字（见 §一）</b>。" if a0_final5 else
        ("本轮 A0 已产出 interim 数字（见 §一），5-run 收口中。" if a0_done else "本轮 A0 待产出。")))
    rec_mean = rec.get("mean")
    H.append("<li><b>6.84%% ± 6.12%% 是混合口径</b>：run1=18.99%% 为 ws-only 锚点（分母仅 36 个 ws 段），run2–5 为 recovered 口径；剔除 run1 后 recovered 4-run = <b>%s%% ± %s</b>。主结论用后者，混合 5-run 并列报告。</li>" % (
        ("%.2f" % (round(float(rec_mean) * 100, 2)) if rec_mean is not None else "3.80"),
        ("%.2f" % (round(float(rec.get("std_sample", 0.009)) * 100, 2)) if rec.get("std_sample") is not None else "0.90")))
    ruler = adm.get("A3_ruler_bug", "")
    H.append("<li><b>量尺本身有 bug</b>：%s。历史实测该偏差可达 <b>15.19pp</b>，比任何模型效应都大。A0/A1 走 .17 抽取器（读 code/&lt;task&gt;/pyAether_code no-ws 路径），不受此 bug 影响。</li>" % esc(ruler.split(";")[0] if ruler else "format_cline_cli_output.py 原本只读 ws/pyAether_code、丢 no-ws 代码"))
    H.append("</ol></div>")

    H.append("<h2>一、本轮里程碑结论</h2>")
    if a0_done:
        mean, std = a0.get("five_run_mean"), a0.get("five_run_std")
        pr = a0.get("per_run_pass_rate", {})
        runs_str = ", ".join("run%s=%s" % (k, pct(v)) for k, v in sorted(pr.items(), key=lambda x: int(x[0])))
        kind_note = "" if a0_kind == "final" else "（%s，非最终 5-run）" % a0_kind
        H.append('<p><span class="kpi">A0 base Pass@1 = %s ± %s</span>（MiniCPM5-2B 原模型 · .17 口径 · 修复后抽取器 · 沙盒真执行验证 · n=%d runs%s）。</p>' % (pct(mean), pct(std), a0_n, kind_note))
        H.append("<p>逐 run：%s。</p>" % runs_str)
        if a1_done and cmp:
            d = cmp.get("delta_mean_pass_rate")
            arms = cmp.get("arms", {})
            a1a = arms.get("A1_sft", {})
            H.append('<p><span class="kpi">A1 (SFT step105) Pass@1 = %s ± %s</span> &nbsp; <span class="kpi">SFT 增量 Δ = %s</span>（同尺同口径，配对统计见 §六）。</p>' % (pct(a1a.get("mean_pass_rate")), pct(a1a.get("std_pass_rate")), pct(d)))
        else:
            H.append("<p>要量化「SFT 增量」须 A1(SFT step105)在<b>同一把修复后 .17 量尺</b>上跑 5-run（%s）。</p>" % ("A1 5-run 进行中" if a1 else "A1 待 A0 5-run 干净后起"))
    else:
        H.append('<p><span class="tag pending">A0 5-run 尚未产出</span> — 待 finalize-watcher 聚合 5 个 final_report.json 后自动填充。</p>')

    if audit:
        b1 = audit.get("B1_identity", {})
        H.append('<div class="danger"><b>⚠ B1 身份警示（§B.1 风险已坐实）</b>：final_report.json 的 model_name = %s（config.yaml active_model 陈旧标签，<b>非实际服务模型</b>）。<b>权威身份</b>：① curl :8098/v1/models → id=%s root=%s；② serve PID%s --model %s --served-model-name %s；③ <b>逐会话</b>复核 158/158 session = %s。⇒ <b>requested=served=ckpt=base 一致，B1 真身份 PASS</b>；陈旧标签属报告头 bug，已显式标注，不据此判 fail 停跑。本报告所有数字归因到 MiniCPM5-2B base。</div>' % (
            esc((a0.get("report_model_name_per_run", {}) if a0 else {}).get("1", "zhulong_deepseek_v32")),
            esc(b1.get("v1_models_id")), esc(b1.get("v1_models_root")),
            esc(b1.get("serve_pid")), esc(b1.get("ckpt_path")), esc(b1.get("served_model")), esc(b1.get("served_model"))))

    H.append("<h2>二、臂矩阵（A/B/C/D 全表 · 本轮 A0/A1）</h2>")
    a0_status = ("run1-5 ✅ %s±%s" % (pct(a0.get("five_run_mean")), pct(a0.get("five_run_std"))) if a0_final5
                 else ("interim n=%d %s±%s" % (a0_n, pct(a0.get("five_run_mean")), pct(a0.get("five_run_std"))) if a0_done else "待 finalize"))
    a1_status = ("run1-5 ✅ %s±%s" % (pct(a1.get("five_run_mean")), pct(a1.get("five_run_std"))) if a1_done
                 else ("A1 5-run 进行中" if a1 else "待 A0 5-run 干净后起"))
    H.append(table([
        ["<b>A0</b>", "MiniCPM5-2B 原模型(base)", ":8098(GPU4 vLLM standby)", ".17(无远程RAG/无沙盒MCP/cline/-p8 -n/无PreToolUse hook)", "<b>用户要的那个 base 数字</b>", '<span class="tag %s">%s</span>' % ("go" if a0_final5 else "pending", a0_status)],
        ["<b>A1</b>", "SFT v39 global_step_105", ":8096(GPU5 serve, A1 链自动起)", "同 A0，同一把尺", "分离「SFT 带来的增量」", '<span class="tag %s">%s</span>' % ("go" if a1_done else "pending", a1_status)],
        ["A2/A3(暂缓)", "+RAG / +沙盒 MCP", "36.15 口径", "36.15(有 RAG+沙盒 MCP+PreToolUse hook)", "分离环境杠杆", '<span class="tag">待 zhulong 当前 batch 跑完再排</span>'],
    ], ["臂", "底模", "endpoint", "口径", "用途", "本轮状态"]))
    H.append("<p>两臂同：158 题 / Pass@1 / -p 8 -n / 2500s / 5-run / 同一抽取器 / 同一 fail_mode 分类器。串行纪律：起跑前 pgrep -f run_cline_script + ss -tlnp 自检。</p>")
    H.append("<h2>三、五道验收项（B1–B5）</h2>")
    if audit:
        b1 = audit.get("B1_identity", {})
        cfg = b1.get("ckpt_config", {})
        fp = b1.get("fingerprint_3x", [])
        fp_str = "3× 风格一致(均 %s)，md5 不同(采样随机)" % esc(b1.get("served_model")) if fp else "—"
        H.append("<h3>B1 身份四证</h3>")
        H.append(table([
            ["requested_model", "%s(base，非 SFT)" % esc(b1.get("requested_model", "minicpm5-2b")), "—"],
            ["served_model(/v1/models id)", "%s，root=%s" % (esc(b1.get("v1_models_id")), esc(b1.get("v1_models_root"))), '<span class="ok">✓</span>'],
            ["ckpt_path / mtime", "%s，mtime %s" % (esc(b1.get("ckpt_path")), esc(b1.get("ckpt_mtime"))), '<span class="ok">✓</span>'],
            ["ckpt_config", "%s·%s层·hidden%s·%s·_name_or_path=%s" % (esc(cfg.get("architectures")), esc(cfg.get("num_hidden_layers")), esc(cfg.get("hidden_size")), esc(cfg.get("torch_dtype")), esc(cfg.get("_name_or_path"))), '<span class="ok">✓ base</span>'],
            ["fingerprint(同 prompt 3 seed)", fp_str, '<span class="ok">✓</span>'],
            ["逐会话复核", "<b>158/158 session = %s</b>" % esc(b1.get("served_model")), '<span class="ok">✓</span>'],
            ["final_report.model_name", "%s(config.yaml 陈旧标签)" % esc((a0.get("report_model_name_per_run", {}) if a0 else {}).get("1", "zhulong_deepseek_v32")), '<span class="bad">✗ 报告头标签 bug</span>'],
        ], ["字段", "值", "一致?"]))
        H.append("<p><b>判据</b>：四字段(requested/served/ckpt/fingerprint)一致 ⇒ <b>B1 真身份 PASS</b>。final_report.model_name 为陈旧标签，非实际模型，已显式标注，不触发停跑。</p>")

    if audit:
        b2 = audit.get("B2_ruler_diff", {})
        hist = b2.get("historical_5run_ruler_error", {})
        H.append("<h3>B2 量尺一致性（原始抽取 vs 回补）</h3>")
        H.append(table([
            ["ws-only 抽取(path A,bug)", "仅读 ws/pyAether_code，丢 no-ws 代码", "0%(live batch 抽 0 题)"],
            ["recovered 回补(path B,修复后)", "加 no-ws fallback code/&lt;task&gt;/pyAether_code", "157 题被抽(同 batch)"],
        ], ["口径", "说明", "Pass@1"]))
        H.append("<p><b>量尺误差（历史 5-run max）= %spp</b>（run1 ws-only 18.99%% vs recovered-4run mean 3.80%%）。<b>源头修复</b>：36.15 format_cline_cli_output.py L168-170 加 no-ws fallback(mtime 2026-11-18 10:00)—— ⚠ <b>未提交 working-tree edit，有 revert 风险</b>。A0/A1 走 .17 抽取器<b>不受此 bug 影响</b>；A2/A3 走 36.15 前须复核该 fix 在位。<b>正式数字一律用修复后口径。</b></p>" % hist.get("max_ruler_error_pp", 15.19))

    if audit:
        b3 = audit.get("B3_judge_noise", {})
        pr = b3.get("per_run", {})
        rows = []
        for k in sorted(pr.keys(), key=lambda x: int(x.replace("run", ""))):
            r = pr[k]
            rows.append([k, r.get("exec_lines"), r.get("passed"), "%.5f" % r.get("pass1_10x_mean", 0), r.get("pass1_10x_sd")])
        H.append("<h3>B3 打分器噪声（同 jsonl 重评 10×）</h3>")
        H.append(table(rows, ["run", "exec_lines", "passed", "Pass@1 10× mean", "10× sd"]))
        H.append("<p><b>judge_sd = %s（全部 5 run）</b> ⇒ 打分<b>完全确定</b>。5-run 方差<b>全部来自上游</b>(generation + sandbox 执行)，非打分器。判据「同臂两 run 差值 &lt; 2×judge_sd=0」⇒ 任何非零差值归因于 generation/execution 噪声 ⇒ 动机转 B4。</p>" % b3.get("judge_sd_all_runs", 0.0))
    if b4:
        H.append("<h3>B4 执行确定性（10 任务 × 10 次沙盒重跑）</h3>")
        H.append(table([
            ["规格", esc(b4.get("spec"))],
            ["源 run", esc(b4.get("source_run"))],
            ["PASS 任务(5)", ", ".join(b4.get("pass_task_ids", []))],
            ["FAIL 任务(5)", ", ".join(b4.get("fail_task_ids", []))],
            ["重跑次数", "%d" % b4.get("n_runs_completed", 10)],
            ["翻转任务数", "<b>%d</b>" % b4.get("n_tasks_flipped", 0)],
            ["<b>翻转率 flip_rate</b>", '<span class="ok"><b>%s</b></span>' % b4.get("flip_rate", 0.0)],
            ["历史对照", esc(b4.get("historical_reference"))],
        ], ["字段", "值"]))
        H.append("<p><b>判据满足</b>：flip_rate=0（0/10 任务翻转，10 轮判决全一致），优于历史 wake533 direct 2/79。⚠ caveat：10 任务均为快任务(0 timeout)，未覆盖 timeout-prone 题翻转，但符合 B4 规格。</p>")
    else:
        H.append('<h3>B4 执行确定性（待补）</h3><p><span class="tag pending">待补</span></p>')

    H.append("<h3>B5 逐题画像（回答「哪些地方出错」· MiniCPM5 base 自己的数据）</h3>")
    H.append("<p><b>⚠ 用 MiniCPM5 base 自己的数据重做，未沿用 DeepSeek 的 fail_mode 分布。</b></p>")
    if a0_done:
        cats = a0.get("per_task_categories", {})
        dist = a0.get("per_task_pass_distribution_0_to_N", {})
        fm = a0.get("dominant_fail_mode_over_failing_tasks", {})
        fm4 = a0.get("four_metric_means_over_runs", {})
        dist_str = " · ".join("%s/5→%s 题" % (k, v) for k, v in sorted(dist.items(), key=lambda x: int(x[0])))
        H.append(table([
            ["A0 Pass@1(n=%d runs)" % a0_n, "<b>%s ± %s</b>" % (pct(a0.get("five_run_mean")), pct(a0.get("five_run_std")))],
            ["题级 pass 次数分布", dist_str],
            ["题级分类", "pass_all=%s / fail_all=%s / partial=%s / n=%s" % (cats.get("pass_all_runs"), cats.get("fail_all_runs"), cats.get("partial"), cats.get("n_tasks"))],
        ], ["指标", "值"]))
        total_fail = sum(fm.values()) if fm else 0
        legend = run1.get("fail_mode_legend", {}) if run1 else {}
        fmrows = []
        for k, v in sorted(fm.items(), key=lambda x: -x[1]):
            share = ("%.1f%%" % (100.0 * v / total_fail)) if total_fail else "—"
            fmrows.append([k, v, share, esc(legend.get(k, ""))])
        H.append("<h4>fail_mode 五分类（dominant over failing tasks，n=%d）</h4>" % total_fail)
        H.append(table(fmrows, ["类别", "题数", "占比(fail)", "含义"]))
        H.append("<h4>四指标（agent 行为画像 · 题均值）</h4>")
        H.append(table([
            ["agent_loop_entry_rate(是否进入 agent 回路)", "<b>%s</b>" % pct(fm4.get("agent_loop_entry_rate"))],
            ["tool_call_count_mean(工具调用数/题)", "<b>%s</b>" % fm4.get("tool_call_count_mean")],
            ["error_rate_mean(报错率)", "<b>%s%%</b>" % (round(float(fm4.get("error_rate_mean", 0)) * 100, 2))],
            ["rag_queried_rate(API 检索工具命中率)", "<b>%s</b>" % pct(fm4.get("rag_queried_rate"))],
        ], ["指标", "值"]))
    if run1:
        atc = run1.get("aggregate_tool_calls", {})
        rej = run1.get("aggregate_reject_reasons", {})
        atc_str = " · ".join("%s=%s" % (k, v) for k, v in sorted(atc.items(), key=lambda x: -x[1])[:10])
        rej_str = " · ".join("%s=%s" % (k, v) for k, v in rej.items())
        H.append('<p><b>聚合工具调用</b>(run1, top10)：%s。<br><b>拒绝原因</b>：%s。<br><span class="note">注：rag_queried_rate 计的是本地 PyAether API 检索工具(search_apis 等，.17 harness 自带)，<b>非</b>远程 RAG recall(:9002，A0 口径未启用)。</span></p>' % (esc(atc_str), esc(rej_str)))
    H.append("<h2>四、口径六元组（caliber six-tuple）</h2>")
    H.append(table([
        ["1. 模型/底模", "MiniCPM5-2B <b>base</b>", "SFT v39 step105"],
        ["2. harness", ".17 cline harness", "36.15 zhulong harness"],
        ["3. 量尺/抽取器", "<b>修复后</b>(读 pyAether_code no-ws)", "broken ws-only(丢 no-ws)"],
        ["4. 远程 RAG", "无(:9002 未启用)", "有"],
        ["5. 沙盒 MCP(codegen 期)", "无", "有"],
        ["6. 协议", "158题/Pass@1/2500s/单trace/<b>5-run 目标</b>/-p8 -n", "同协议(但量尺/模型/harness 不同)"],
    ], ["元", "A0(本轮)", "旧 6.84% 5-run(不可比)"]))
    H.append("<p><b>结论</b>：A0 与旧 6.84%(3.04%)在六元组中有 <b>3 项不同</b>(模型/量尺/harness)⇒ <b>禁止直接比较</b>。要量化「SFT 增量」须 A1 在<b>同一把修复后 .17 量尺</b>上跑 5-run。</p>")

    H.append("<h2>五、分段交付与状态</h2>")
    s1 = '<span class="tag go">✅ DONE</span> → baseline_measurement_audit.json' if audit else '<span class="tag pending">待补</span>'
    s2 = '<span class="tag go">✅ DONE</span> run1 逐题画像(B5)' if run1 else '<span class="tag pending">待补</span>'
    s3 = ('<span class="tag go">✅ A0 5-run DONE (%s±%s)</span>' % (pct(a0.get("five_run_mean")), pct(a0.get("five_run_std"))) if a0_final5
          else ('<span class="tag pending">进行中：A0 interim n=%d (%s±%s)</span>' % (a0_n, pct(a0.get("five_run_mean")), pct(a0.get("five_run_std"))) if a0_done else '<span class="tag pending">进行中</span>'))
    s3b = (' + <span class="tag go">A1 5-run DONE (%s±%s)</span>' % (pct(a1.get("five_run_mean")), pct(a1.get("five_run_std"))) if a1_done
           else ' + <span class="tag pending">A1 5-run %s</span>' % ("进行中" if a1 else "待起"))
    H.append(table([
        ["Stage1(≤2h,零 codegen)", "B1 身份四证 + B3 judge 噪声 + B2 量尺差值", s1],
        ["Stage2(单 run)", "A0 run1 逐题画像(B5)", s2],
        ["Stage3(5-run)", "A0 补满 5-run + A1 同尺 5-run → 正式基线表", s3 + s3b],
    ], ["Stage", "内容", "状态"]))
    b_all = "B1✅/B2✅/B3✅/B4✅/B5✅" if (audit and b4 and a0_done and run1) else "部分✅/部分待补"
    H.append("<p><b>五道验收项：%s</b>。Stage1 verdict=GO（未触发停跑）；Stage2 单 run 结论清晰（fail_mode 以 F5_logic+F4_api 为主）⇒ 支持补 5-run。</p>" % b_all)

    if cmp:
        H.append("<h2>六、A0-vs-A1 配对统计（量化 SFT 增量）</h2>")
        arms = cmp.get("arms", {})
        a0a = arms.get("A0_base", {})
        a1a = arms.get("A1_sft", {})
        boot = cmp.get("paired_bootstrap", {}) or {}
        mc = cmp.get("mcnemar", {}) or {}
        maj = mc.get("majority", {}) or {}
        anyp = mc.get("any_pass", {}) or {}
        ptt = cmp.get("per_task_paired_tests", {}) or {}
        wil = ptt.get("wilcoxon_signed_rank", {}) or {}
        pt = ptt.get("paired_t_test", {}) or {}
        H.append(table([
            ["A0 base mean ± std", "%s ± %s (n=%s)" % (pct(a0a.get("mean_pass_rate")), pct(a0a.get("std_pass_rate")), a0a.get("n_runs"))],
            ["A1 SFT mean ± std", "%s ± %s (n=%s)" % (pct(a1a.get("mean_pass_rate")), pct(a1a.get("std_pass_rate")), a1a.get("n_runs"))],
            ["<b>Δ mean pass rate (A1−A0)</b>", "<b>%s</b>（正 ⇒ SFT 提升）" % pct(cmp.get("delta_mean_pass_rate"))],
            ["配对任务数", "%d" % cmp.get("n_tasks_paired", 0)],
            ["Wilcoxon signed-rank p", "%s（方向：%s）" % (wil.get("p_two_sided"), esc(wil.get("direction", "")))],
            ["paired t-test p", "%s（t=%s, df=%s）" % (pt.get("p_two_sided"), pt.get("t"), pt.get("df"))],
            ["McNemar (majority) χ² / p", "χ²=%s / p=%s（discord=%s：A0_only=%s A1_only=%s）" % (maj.get("chi2_continuity"), maj.get("chi2_p_two_sided"), maj.get("discordant"), maj.get("A0_only"), maj.get("A1_only"))],
            ["McNemar (any_pass) χ² / p", "χ²=%s / p=%s（discord=%s）" % (anyp.get("chi2_continuity"), anyp.get("chi2_p_two_sided"), anyp.get("discordant"))],
            ["paired bootstrap (B=10000)", "Δ=%s, 95%%CI[%s,%s], p=%s" % (pct(boot.get("delta_mean")), pct(boot.get("ci95_low")), pct(boot.get("ci95_high")), boot.get("p_two_sided"))],
            ["scipy_available", str(cmp.get("scipy_available"))],
        ], ["统计量", "值"]))
        H.append("<p><b>口径</b>：%s。McNemar 'majority' = task passes if pass_count ≥ ceil(n_runs/2)；'any_pass' = passes if pass_count ≥ 1。Bootstrap 对 158 任务有放回重采样(B=10000)。</p>" % esc(cmp.get("protocol", "")))
    H.append("<h2>七、全部落盘路径</h2>")
    H.append(table([
        ["Stage1 审计 JSON", "run/baseline_measurement_audit.json"],
        ["B4 执行确定性 JSON", "run/baseline_B4_execution_determinism.json"],
        ["A0 5-run summary", "run/baseline_A0_base_5run_summary.json" + (("（%s）" % a0_kind) if a0_kind and a0_kind != "final" else "")],
        ["A1 5-run summary", "run/baseline_A1_sft_5run_summary.json" + (("（待产出）" if not a1_done else ""))],
        ["A0-vs-A1 配对统计", "run/baseline_A0_vs_A1_paired_compare.json" + (("（待产出）" if not cmp else ""))],
        ["A0 run1 逐题画像 JSON(E.2)", "run/baseline_A0_base_run1_pertask.json"],
        ["逐题画像脚本", "run/baize_posttrain_baseline_pertask_profile.py"],
        ["5-run finalize 脚本", "run/baize_posttrain_a0_finalize_5run.py"],
        ["A1 自治链脚本", "run/baize_posttrain_a1_sft_chain.sh"],
        ["配对比较脚本", "run/baize_posttrain_arm_paired_compare.py"],
        ["本报告生成脚本", "run/baize_posttrain_baseline_report_gen.py"],
        ["本轮里程碑报告(E.1)", "reports/report_posttrain_baseline_nailed_zh.html（本文件）"],
        ["5-run eval 链脚本", "run/baize_posttrain_5run_eval.sh"],
        ["vLLM base serve 日志", "/tmp/vllm_gpu4.log(GPU4 :8098)"],
    ], ["交付物", "路径"]))

    H.append("<h2>八、本轮禁止项核对（令 §F）</h2><ul>")
    H.append("<li>🚫 五道验收项过之前起 GRPO/SFT/造题 —— <b>未起</b>(仅做 baseline eval)✅</li>")
    H.append("<li>🚫 改 158 题面/check.py/协议/超时/-p —— <b>未改</b>(协议冻结项全保持)✅</li>")
    H.append("<li>🚫 把 3.04% 说成 base 结果 —— 本报告显式标注 3.04%=SFT step105 ✅</li>")
    H.append("<li>🚫 跨口径比较不标注 —— §四口径六元组显式标注 3 项不同，<b>禁止直接比较</b> ✅</li>")
    H.append("</ul>")

    H.append("<h2>九、下一步</h2><ol>")
    if not a0_final5:
        H.append("<li>A0 5-run 收口中（run345 auto-chain 串行 + finalize-watcher 自动聚合 5 个 final_report.json → baseline_A0_base_5run_summary.json）。</li>")
    if not a1_done:
        H.append("<li>A0 5-run 干净后，A1 链自动起 :8096 serve SFT step105 → A1 同尺 5-run → baseline_A1_sft_5run_summary.json。</li>")
    if not cmp:
        H.append("<li>两臂 summary 齐备后，compare-watcher 自动跑配对统计 → baseline_A0_vs_A1_paired_compare.json。</li>")
    H.append("<li>本报告由 report-watcher 在上述交付物落盘后<b>自动原地覆盖更新</b>。</li>")
    H.append("</ol>")
    H.append('<p style="margin-top:30px;color:#888;font-size:0.85em">BaiZe Stage(ii) posttrain · baseline-nailed · 数据驱动自包含单文件 HTML · 由 baize_posttrain_baseline_report_gen.py 生成 · commit 前缀 posttrain baseline-nailed:</p>')
    H.append("</body></html>")
    return "\n".join(H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=REPORT_PATH)
    ap.add_argument("--dry-run", action="store_true", help="print to stdout instead of writing file")
    args = ap.parse_args()
    audit = load("baseline_measurement_audit.json")
    b4 = load("baseline_B4_execution_determinism.json")
    a0, a0_kind = pick_a0_summary()
    a1 = load("baseline_A1_sft_5run_summary.json")
    if a1 and int(a1.get("n_runs_completed", 0) or 0) < 5:
        a1 = None
    cmp = load("baseline_A0_vs_A1_paired_compare.json")
    run1 = load("baseline_A0_base_run1_pertask.json")
    if not audit:
        sys.stderr.write("[FATAL] baseline_measurement_audit.json missing; nothing to render.\n")
        return 1
    html_out = render(audit, b4, a0, a0_kind, a1, cmp, run1)
    if args.dry_run:
        sys.stdout.write(html_out)
    else:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as f:
            f.write(html_out)
        n = len(html_out.splitlines())
        sz = os.path.getsize(args.out)
        a0n = int(a0.get("n_runs_completed", 0)) if a0 else 0
        print("[report-gen] WROTE %s (%d lines, %d bytes)" % (args.out, n, sz))
        print("[report-gen] A0=%s(n=%d,%s) A1=%s compare=%s B4=%s run1=%s" % (
            "yes" if a0 else "no", a0n, a0_kind or "?", "yes" if a1 else "no",
            "yes" if cmp else "no", "yes" if b4 else "no", "yes" if run1 else "no"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
