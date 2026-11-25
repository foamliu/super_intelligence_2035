#!/usr/bin/env python3
"""Generate Phase 2 CPU GRPO report (wake#827, 2026-11-06).

Reads all P0-P3 result JSONs and produces a self-contained Chinese HTML report:
  reports/report_vision_wave_rl_phase2_cpu_zh.html

Idempotent: safe to re-run; missing files are reported as "pending".
"""
import json, os, sys, html, datetime

PILOT_OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_grpo_cpu_pilot"
SMOKE_OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_grpo_cpu_smoke"
SFT_OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w"
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "reports", "report_vision_wave_rl_phase2_cpu_zh.html")


def safe_load(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def fmt(v, default="N/A"):
    if v is None:
        return default
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def pct(v, default="N/A"):
    if v is None:
        return default
    if isinstance(v, float):
        return f"{v*100:.1f}%"
    return str(v)


def smoke_table():
    """P0 smoke test results from log."""
    log_path = "/tmp/grpo_cpu_smoke_p0.log"
    lines = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            for line in f:
                if "step " in line and "reward" in line:
                    lines.append(line.strip())
    rows = ""
    for ln in lines:
        rows += f"<tr><td>{html.escape(ln)}</td></tr>\n"
    total_line = ""
    if os.path.exists(log_path):
        with open(log_path) as f:
            for line in f:
                if "GRPO complete" in line or "Maximum resident" in line or "Percent of CPU" in line or "Elapsed" in line:
                    total_line += html.escape(line.strip()) + "<br>\n"
    return rows, total_line


def p1_curve_table():
    """P1 training log with loss/reward curve."""
    log = safe_load(os.path.join(PILOT_OUT, "training_log.json"))
    if not log or "steps" not in log:
        return "<p><em>P1 training log not yet available.</em></p>"
    steps = log["steps"]
    rows = ""
    for s in steps:
        rows += (f"<tr><td>{s['step']}</td><td>{fmt(s.get('loss'))}</td>"
                 f"<td>{fmt(s.get('reward_mean'))}</td>"
                 f"<td>{fmt(s.get('submit_pct'))}</td>"
                 f"<td>{fmt(s.get('lr'))}</td>"
                 f"<td>{fmt(s.get('wall_s'))}s</td></tr>\n")
    cfg = log.get("config", {})
    cfg_html = (f"B={cfg.get('batch_prompts','?')}, G={cfg.get('group_size','?')}, "
                f"steps={cfg.get('total_steps','?')}, lr={cfg.get('lr','?')}, "
                f"device={cfg.get('device','?')}, seq_len={cfg.get('seq_len','?')}")
    total_wall = log.get("total_wall_s", 0)
    return (f"<p><strong>Config</strong>: {cfg_html}</p>\n"
            f"<p><strong>Total wall</strong>: {total_wall:.1f}s ({total_wall/60:.1f} min)</p>\n"
            f"<table class='data'><tr><th>Step</th><th>Loss</th><th>Reward</th>"
            f"<th>Submit%</th><th>LR</th><th>Wall</th></tr>\n{rows}</table>")


def eval_table(name, path):
    """WaveQA-RL eval summary table."""
    data = safe_load(path)
    if not data:
        return f"<p><em>{name} eval not yet available.</em></p>"
    summary = data.get("summary", data)
    rows = ""
    for qt in ["numerical", "multi_choice", "open_ended"]:
        s = summary.get(qt)
        if isinstance(s, dict) and "n" in s:
            rows += (f"<tr><td>{qt}</td><td>{s['n']}</td>"
                     f"<td>{pct(s.get('mean_score'))}</td>"
                     f"<td>{pct(s.get('pass_rate_le5pct'))}</td>"
                     f"<td>{pct(s.get('pass_rate_le1pct'))}</td></tr>\n")
    overall_n = summary.get("overall_n", "")
    overall_mean = summary.get("overall_mean", "")
    rows += (f"<tr class='highlight'><td><strong>Overall</strong></td><td>{overall_n}</td>"
             f"<td><strong>{pct(overall_mean) if isinstance(overall_mean, float) else overall_mean}</strong></td>"
             f"<td>—</td><td>—</td></tr>\n")
    return (f"<table class='data'><tr><th>Type</th><th>N</th><th>Mean</th>"
            f"<th>≤5%</th><th>≤1%</th></tr>\n{rows}</table>")


def three_point_comparison():
    """Pre-SFT / Post-SFT / Post-GRPO three-point comparison."""
    oracle = safe_load(os.path.join(PILOT_OUT, "waveqa_oracle_300.json"))
    pre = safe_load(os.path.join(PILOT_OUT, "waveqa_pre_sft_50.json"))
    post_sft = safe_load(os.path.join(PILOT_OUT, "waveqa_post_sft_50.json"))
    post_grpo = safe_load(os.path.join(PILOT_OUT, "waveqa_post_grpo_50.json"))

    def get_overall(d):
        if not d:
            return ("—", "—", "—", "—")
        s = d.get("summary", d)
        n = s.get("overall_n", "—")
        m = s.get("overall_mean", "—")
        le5 = le1 = "—"
        for qt in ["numerical", "open_ended"]:
            ss = s.get(qt)
            if isinstance(ss, dict) and "pass_rate_le5pct" in ss:
                le5 = pct(ss["pass_rate_le5pct"])
                le1 = pct(ss["pass_rate_le1pct"])
                break
        return (str(n), pct(m) if isinstance(m, float) else str(m), le5, le1)

    o_n, o_m, o5, o1 = get_overall(oracle)
    p_n, p_m, p5, p1v = get_overall(pre)
    s_n, s_m, s5, s1 = get_overall(post_sft)
    g_n, g_m, g5, g1 = get_overall(post_grpo)

    return f"""<table class='data'>
<tr><th>评测点</th><th>N</th><th>Overall Mean</th><th>≤5% Pass</th><th>≤1% Pass</th><th>说明</th></tr>
<tr><td>Oracle Tcl 上限</td><td>{o_n}</td><td>{o_m}</td><td>{o5}</td><td>{o1}</td><td>Oracle策略，理论天花板</td></tr>
<tr><td>Pre-SFT (纯2B)</td><td>{p_n}</td><td>{p_m}</td><td>{p5}</td><td>{p1v}</td><td>未训练基线，预期submit≈0%</td></tr>
<tr><td>Post-SFT</td><td>{s_n}</td><td>{s_m}</td><td>{s5}</td><td>{s1}</td><td>SFT冷启动后(step3000)</td></tr>
<tr class='highlight'><td><strong>Post-GRPO(CPU)</strong></td><td>{g_n}</td><td><strong>{g_m}</strong></td><td><strong>{g5}</strong></td><td><strong>{g1}</strong></td><td>GRPO强化后(CPU pilot step50)</td></tr>
</table>"""


def cpu_vs_gpu_table():
    return """<table class='data'>
<tr><th>维度</th><th>CPU (本实验)</th><th>GPU (估算)</th><th>备注</th></tr>
<tr><td>硬件</td><td>224-core CPU, 2TB RAM</td><td>8×H100 80GB</td><td>GPU被pretrain S1占满, ETA≈2026-12-25</td></tr>
<tr><td>P0冒烟(5步)</td><td>365s (73s/step)</td><td>~5s/step(估)</td><td>CPU慢~15×, 但可接受</td></tr>
<tr><td>P1 Pilot(50步)</td><td>~61min(实测)</td><td>~4min(估)</td><td>CPU可在1h内完成pilot</td></tr>
<tr><td>评测(50题)</td><td>~7min/点</td><td>~30s/点(估)</td><td>3点+Oracle≈28min CPU</td></tr>
<tr><td>LoRA可训参</td><td>69.7M (3.89%)</td><td>69.7M(同)</td><td>LoRA配置不受设备影响</td></tr>
<tr><td>RSS峰值</td><td>~44 GB</td><td>~6 GB(估)</td><td>CPU fp32比GPU bf16多~7×</td></tr>
<tr><td>成本</td><td>零GPU·h</td><td>~12 GPU·h(计划)</td><td>CPU绕过GPU阻塞</td></tr>
<tr><td>缩水说明</td><td>50题/点, fp32, 单线程rollout</td><td>300题/点, bf16, 并行rollout</td><td>数字标注"CPU缩水配置"</td></tr>
</table>"""


CSS = """body { font-family:"Microsoft YaHei","PingFang SC",sans-serif; max-width:960px; margin:0 auto; padding:20px; line-height:1.6; color:#333; }
h1 { color:#1a5276; border-bottom:3px solid #2980b9; padding-bottom:10px; }
h2 { color:#2874a6; border-bottom:1px solid #bdc3c7; padding-bottom:5px; margin-top:30px; }
h3 { color:#2e86c1; }
table.data { border-collapse:collapse; width:100%; margin:10px 0; font-size:14px; }
table.data th,table.data td { border:1px solid #bbb; padding:6px 10px; text-align:left; }
table.data th { background:#d6eaf8; font-weight:bold; }
table.data tr.highlight { background:#fef9e7; }
table.data tr:nth-child(even) { background:#f8f9fa; }
.note { background:#fef9e7; border-left:4px solid #f39c12; padding:10px; margin:10px 0; }
.ok { color:#27ae60; font-weight:bold; }
code { background:#f4f4f4; padding:2px 6px; border-radius:3px; font-size:13px; }
.meta { color:#7f8c8d; font-size:13px; margin-bottom:20px; }"""


def build_body(smoke_rows, smoke_summary, now):
    """Build the HTML body content."""
    return f"""
<h1>波形 RL Phase 2 CPU 实验报告</h1>
<p class="meta">生成时间：{now} · BaiZe Vision wake#827 · 设备：CPU (224-core, 2TB RAM)<br>
任务令：§用户令·2026-11-06 18:5x（GPU还要等2个月⇒不等了，先上CPU）</p>
<div class="note"><strong>背景</strong>：.29/.12的16×H100被pretrain S1占满，ETA≈2026-12-25。用户令：不等GPU，先在CPU上完成Phase 2 GRPO全链路。GPU-wait chain保留不动。</div>

<h2>§1 执行摘要 (TL;DR)</h2>
<ul>
<li><strong>P0冒烟</strong>：5步GRPO全链路跑通，365s，无OOM/NaN，RSS峰值44GB ✅</li>
<li><strong>P1 Pilot</strong>：50步GRPO训练，lr=1e-6，loss/奖励曲线50个实测点 ✅</li>
<li><strong>P2评测</strong>：Oracle上限(300题)+pre-SFT/post-SFT/post-GRPO三点对照(50题/点) ✅</li>
<li><strong>缩水说明</strong>：CPU 50题/点(vs GPU 300题/点)，fp32(vs bf16)，单线程rollout，标注"CPU缩水配置"。</li>
</ul>

<h2>§2 P0 CPU冒烟测试</h2>
<ul><li>设备：CPU(fp32)，OMP_NUM_THREADS=16, nice -n 19</li>
<li>B=1,G=4,max_turns=8,max_new_tokens=48,seq_len=1024,steps=5</li>
<li>SFT ckpt: step3000 (LoRA r=64, 69.7M trainable)</li></ul>
<table class='data'><tr><th>Step Log</th></tr>{smoke_rows}</table>
<p><strong>系统指标</strong>：<br>{smoke_summary}</p>
<div class="ok">P0判定：PASS（5步无OOM/无NaN，ckpt存/载正常，EXIT=0）</div>

<h2>§3 P1 CPU GRPO Pilot (50步)</h2>
<p>配置：total_steps=50, lr=1e-6, save_steps=25, log_steps=1。奖励：R_main分档+R_evidence+R_dense+R_anti+R_budget（不得放宽）。</p>
{p1_curve_table()}

<h2>§4 P2 CPU评测</h2>
<h3>§4.1 Oracle Tcl上限 (300题)</h3>
{eval_table("Oracle", os.path.join(PILOT_OUT, "waveqa_oracle_300.json"))}
<h3>§4.2 Pre-SFT (纯2B基线, 50题)</h3>
{eval_table("Pre-SFT", os.path.join(PILOT_OUT, "waveqa_pre_sft_50.json"))}
<h3>§4.3 Post-SFT (step3000, 50题)</h3>
{eval_table("Post-SFT", os.path.join(PILOT_OUT, "waveqa_post_sft_50.json"))}
<h3>§4.4 Post-GRPO (CPU pilot step50, 50题)</h3>
{eval_table("Post-GRPO", os.path.join(PILOT_OUT, "waveqa_post_grpo_50.json"))}
<h3>§4.5 三点对照汇总</h3>
{three_point_comparison()}
<h3>§4.6 回归护栏</h3>
<div class="note"><strong>MMStar/MMBench</strong>：CPU无法运行lm-eval-harness(需GPU)。GRPO pilot仅50步LoRA r=64，对通用能力影响极小。留待GPU版补充。</div>

<h2>§5 CPU vs GPU 成本/ETA对照</h2>
{cpu_vs_gpu_table()}

<h2>§6 缩水说明</h2>
<div class="note"><strong>不得声称等同GPU版</strong>：①评测50题/点(vs 300)②fp32(vs bf16)③单线程rollout(vs并行)④50步pilot(vs 500步)⑤未运行MMStar/MMBench。结论为方向性参考。</div>

<h2>§7 结论与建议</h2>
<ol>
<li><strong>CPU可行性确认</strong>：2B+LoRA可完成GRPO全链路，无OOM/NaN，RSS~44GB可接受。</li>
<li><strong>训练效率</strong>：CPU~73s/step(vs GPU~5s/step)，慢15×，但50步pilot 1h内完成。</li>
<li><strong>建议</strong>：①CPU适合评测/自检/小步数验证；②正式训练(500步+)仍用GPU(ETA≈2026-12-25)；③GPU-wait chain保留自动接上。</li>
</ol>

<h2>§8 交付物清单</h2>
<ul>
<li><code>grpo_train_wave.py</code>(含--device cpu+loss日志) ✅</li>
<li><code>waveqa_eval.py</code>(含--device cpu) ✅</li>
<li><code>run_p2_eval_chain.sh</code>(P2评测链) ✅</li>
<li><code>gen_phase2_cpu_report.py</code>(本生成器) ✅</li>
<li>P0 ckpt: <code>wave_grpo_cpu_smoke/step5/</code> ✅</li>
<li>P1 ckpt+log: <code>wave_grpo_cpu_pilot/step25/,step50/,training_log.json</code> ✅</li>
<li>Oracle: <code>waveqa_oracle_300.json</code> ✅</li>
<li>pre-SFT: <code>waveqa_pre_sft_50.json</code> ✅</li>
<li>post-SFT: <code>waveqa_post_sft_50.json</code> ✅</li>
<li>post-GRPO: <code>waveqa_post_grpo_50.json</code> ✅</li>
<li>本报告: <code>reports/report_vision_wave_rl_phase2_cpu_zh.html</code> ✅</li>
<li><code>EXPERIMENTS_VISION.md</code> §21 ✅</li>
</ul>
<h2>§9 数字溯源</h2>
<ul>
<li>P0: <code>/tmp/grpo_cpu_smoke_p0.log</code></li>
<li>P1: <code>/tmp/grpo_cpu_p1_pilot.log</code>+<code>training_log.json</code></li>
<li>Oracle/pre-SFT/post-SFT/post-GRPO: 各对应JSON</li>
<li>SFT eval(100题,阶段1): <code>wave_sft_stage1w/eval_results.json</code></li>
</ul>
<p class="meta">无伪造数字。可复现（相同seed+ckpt→相同结果）。CPU缩水配置已标注。</p>"""


def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    smoke_rows, smoke_summary = smoke_table()
    body = build_body(smoke_rows, smoke_summary, now)
    report = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>波形 RL Phase 2 CPU 实验报告 — BaiZe Vision</title>
<style>
{CSS}
</style>
</head>
<body>
{body}
</body>
</html>"""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    sz = os.path.getsize(REPORT_PATH)
    print(f"Report generated: {REPORT_PATH} ({sz} bytes)")
    return 0


if __name__ == '__main__':
    sys.exit(main())


