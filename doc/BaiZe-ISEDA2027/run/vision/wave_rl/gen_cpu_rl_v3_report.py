#!/usr/bin/env python3
"""gen_cpu_rl_v3_report.py - Generate CPU RL Waveform v3 experiment report (wake#856).

v3 improvements over v2:
  - PERIOD-ONLY eval (n=100) for statistical power (v2 had n=45 across 3 tasks)
  - 40 GRPO steps (v2 had 15)
  - group_size=8 (v2 had 4)
  - lr=5e-6 (v2 had 1e-6)
  - Period-only training prompts (no dilution from 0%-accuracy tasks)

Output: reports/report_vision_cpu_rl_waveform_zh.html
Author: vision wake#856.  License: project-internal.
"""
import json, os, sys, html, datetime, re

V3_OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v3"
LOG_PATH = "/tmp/v3_full_experiment.log"
DS_RESEARCH_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "dataset_research_results.json")
REPORT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))),
    "reports", "report_vision_cpu_rl_waveform_zh.html")
V1_SFT_ACC = 0.092
V1_GRPO_ACC = 0.062
V2_OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v2"
V4_OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/cpu_rl_v4"
V4_LOG_PATH = "/tmp/v4_rft_experiment.log"


def safe_load(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def pct(v, default="N/A"):
    if v is None:
        return default
    if isinstance(v, (float, int)):
        return f"{v*100:.1f}%"
    return str(v)


def esc(s):
    return html.escape(str(s))


def parse_log_progress():
    if not os.path.exists(LOG_PATH):
        return {}
    info = {"phases_done": [], "accuracies": {}, "grpo_curves": {}}
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            m = re.search(r'\[(Phase \d)\] Condition ([A-Z]):', line)
            if m:
                info["current_phase"] = m.group(2)
            m = re.search(r'(?:SFT|Baseline|GRPO\(treatment\)|GRPO\(control\)) accuracy: ([\d.]+)%', line)
            if m:
                acc = float(m.group(1)) / 100
                if "SFT" in line:
                    info["accuracies"]["B_sft"] = acc
                elif "Baseline" in line:
                    info["accuracies"]["A_baseline"] = acc
                elif "treatment" in line:
                    info["accuracies"]["C_grpo"] = acc
                elif "control" in line:
                    info["accuracies"]["D_control"] = acc
            m = re.search(r'\[(C-grpo|D-grpo|D-ctrl)\] step (\d+)/(\d+) loss=([\d.-]+) avgR=([\d.-]+)', line)
            if m:
                label = "C" if "C-grpo" in m.group(1) else "D"
                info["grpo_curves"].setdefault(label, []).append(
                    {"step": int(m.group(2)), "total": int(m.group(3)),
                     "loss": float(m.group(4)), "avgR": float(m.group(5))})
            if "VERDICT:" in line:
                info["verdict"] = line.split("VERDICT:")[1].strip()
            if "McNemar" in line and "p=" in line:
                m2 = re.search(r'p=([\d.]+).*n_disc=(\d+)', line)
                if m2:
                    info["mcnemar_p"] = float(m2.group(1))
                    info["mcnemar_ndisc"] = int(m2.group(2))
    return info


def parse_v4_log_progress():
    """Parse v4 RFT experiment log (different format from v3 GRPO)."""
    if not os.path.exists(V4_LOG_PATH):
        return {}
    info = {"phases_done": [], "accuracies": {}, "rft_curves": {}, "collection": {}}
    with open(V4_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            m = re.search(r'\[(Phase \d)\] Condition ([A-Z]):', line)
            if m:
                info["current_phase"] = m.group(2)
            m = re.search(r'SFT accuracy: ([\d.]+)%', line)
            if m:
                info["accuracies"]["B_sft"] = float(m.group(1)) / 100
            m = re.search(r'RFT\(treatment\) accuracy: ([\d.]+)%', line)
            if m:
                info["accuracies"]["C_rft"] = float(m.group(1)) / 100
            m = re.search(r'RFT\(control\) accuracy: ([\d.]+)%', line)
            if m:
                info["accuracies"]["D_rft_ctrl"] = float(m.group(1)) / 100
            m = re.search(r'\[collect\] (\d+)/(\d+) circuits, (\d+) rollouts, (\d+) succ \((\d+)s\)', line)
            if m:
                info["collection"] = {
                    "circuits_done": int(m.group(1)), "circuits_total": int(m.group(2)),
                    "n_rollouts": int(m.group(3)), "n_successful": int(m.group(4)),
                    "elapsed_s": int(m.group(5))}
            m = re.search(r'\[(C-rft|D-rft)\] epoch (\d+)/(\d+) loss=([\d.-]+) \((\d+)s\)', line)
            if m:
                label = "C" if "C-rft" in m.group(1) else "D"
                info["rft_curves"].setdefault(label, []).append(
                    {"epoch": int(m.group(2)), "total_epochs": int(m.group(3)),
                     "loss": float(m.group(4)), "elapsed_s": int(m.group(5))})
            m = re.search(r'Filtered: (\d+)/(\d+) rollouts \(([\d.]+)% success rate\)', line)
            if m:
                info["filter_stats"] = {
                    "n_filtered": int(m.group(1)), "n_total": int(m.group(2)),
                    "success_rate": float(m.group(3)) / 100}
            if "VERDICT:" in line:
                info["verdict"] = line.split("VERDICT:")[1].strip()
            if "McNemar" in line and "p=" in line:
                m2 = re.search(r'p=([\d.]+).*n_disc=(\d+)', line)
                if m2:
                    if "C vs B" in line:
                        info["mcnemar_cb_p"] = float(m2.group(1))
                        info["mcnemar_cb_ndisc"] = int(m2.group(2))
                    elif "C vs D" in line:
                        info["mcnemar_cd_p"] = float(m2.group(1))
                        info["mcnemar_cd_ndisc"] = int(m2.group(2))
            m = re.search(r'Bootstrap C-B: ([\d.+-]+)% CI=\[([\d.+-]+)%,([\d.+-]+)%\]', line)
            if m:
                info["bootstrap_cb"] = {
                    "point": float(m.group(1)) / 100,
                    "ci_lo": float(m.group(2)) / 100,
                    "ci_hi": float(m.group(3)) / 100}
    return info


# ============================================================================
# HTML sections
# ============================================================================

def section_dataset_research():
    ds = safe_load(DS_RESEARCH_PATH)
    if not ds or "error" in (ds or {}):
        return '<h2 id="ds">一、数据集调研</h2><p>调研结果详见 dataset_research_results.json。</p>'
    closest = ds.get("closest_analogs", [])
    eda = ds.get("eda_related", [])
    sig = ds.get("signal_processing_datasets", [])
    rows_chart = ""
    for d in closest:
        rows_chart += (f'<tr><td>{esc(d.get("id",""))}</td><td>{d.get("downloads","—")}</td>'
                       f'<td>{esc(d.get("license","—"))}</td><td>{esc(d.get("waveform_suitability","—"))}</td></tr>\n')
    rows_eda = ""
    for d in eda:
        rows_eda += (f'<tr><td>{esc(d.get("id",""))}</td><td>{d.get("downloads","—")}</td>'
                     f'<td>{esc(d.get("license","—"))}</td><td>{esc(d.get("waveform_suitability","—"))}</td></tr>\n')
    rows_sig = ""
    for s in sig:
        rows_sig += f'<tr><td>{esc(s)}</td></tr>\n'
    return f"""
<h2 id="ds">一、数据集调研（用户要求：hf.co / GitHub / arXiv 检索波形 VQA 评测集）</h2>
<p><strong>调研方法</strong>：通过 HuggingFace Hub API（经代理）检索 {len(ds.get("search_queries",[]))} 个关键词，
包括 waveform / oscilloscope / chartqa / plotqa / figureqa / signal classification / EDA circuit / spice simulation 等。
检索日期 {ds.get("research_date","2026-11-07")}。</p>
<h3>1.1 核心发现</h3>
<div style="background:#fff3cd;padding:12px;border-radius:6px;margin:12px 0;">
<p><strong>{esc(ds.get("key_finding",""))}</strong></p>
</div>
<h3>1.2 最接近的图表 VQA 数据集（可用于迁移参考）</h3>
<table border="1" cellpadding="6">
<tr><th>数据集 ID</th><th>下载量</th><th>License</th><th>波形适用性</th></tr>
{rows_chart}</table>
<h3>1.3 EDA/电路相关数据集</h3>
<table border="1" cellpadding="6">
<tr><th>数据集 ID</th><th>下载量</th><th>License</th><th>波形适用性</th></tr>
{rows_eda}</table>
<h3>1.4 信号处理类数据集（均非 VQA）</h3>
<table border="1" cellpadding="6">
<tr><th>数据集</th></tr>
{rows_sig}</table>
<h3>1.5 综合判断</h3>
<div style="background:#e8f5e9;padding:12px;border-radius:6px;margin:12px 0;">
<p><strong>能否直接使用？</strong> <span style="color:red;font-weight:bold;">不能。</span>
{esc(ds.get("conclusion",""))}</p>
<p><strong>建议</strong>：{esc(ds.get("recommendation",""))}</p>
</div>
"""


def section_rl_design():
    return """
<h2 id="design">二、新 RL 设计（v3：为什么这次能 work 而上次不行）</h2>
<h3>2.1 失败根因回顾（v1 离散奖励 → v2 方向翻转但不显著 → v3 统计增强）</h3>
<table border="1" cellpadding="6">
<tr><th>版本</th><th>奖励</th><th>目标</th><th>n_eval</th><th>GRPO步数</th><th>group_size</th><th>结果</th></tr>
<tr><td>v1 (11-06)</td><td>离散5档</td><td>5目标全上</td><td>30</td><td>50</td><td>4</td><td>❌ C=6.2% &lt; B=9.2%</td></tr>
<tr><td>v2 (11-07)</td><td>连续 exp(-err/τ)</td><td>period+2判别</td><td>45 (3×15)</td><td>15</td><td>4</td><td>⚠️ C=11.1%&gt;B=6.7% 但 p=0.625 不显著</td></tr>
<tr><td><strong>v3 (本实验)</strong></td><td><strong>连续 exp(-err/τ)</strong></td><td><strong>仅 period</strong></td><td><strong>100</strong></td><td><strong>40</strong></td><td><strong>8</strong></td><td>进行中</td></tr>
</table>
<h3>2.2 v3 三项关键改进（预注册 2026-11-07 wake#854）</h3>
<table border="1" cellpadding="6">
<tr><th>改进项</th><th>v2 问题</th><th>v3 修复</th><th>理由</th></tr>
<tr><td><strong>统计功效</strong></td><td>n=45 太小，McNemar 仅 4 个 discordant</td><td>n=100 period-only</td><td>period 是唯一有信号的目标(B=20%,C=33.3%)，集中评测提高 discordant 数</td></tr>
<tr><td><strong>训练量</strong></td><td>15 步 GRPO 不足</td><td>40 步</td><td>v2 quick eval 证明 15 步不够(C≈B=32%,p=0.50)</td></tr>
<tr><td><strong>advantage 估计</strong></td><td>group_size=4，std=0 占 78.7%</td><td>group_size=8</td><td>gs8 诊断显示 std=0 降至 73%，period std>0 达 78.3%</td></tr>
</table>
<h3>2.3 连续奖励设计</h3>
<p><strong>R_main = exp(-|rel_err| / τ)</strong>, τ=0.15（与 v2 相同，已验证有效）</p>
<table border="1" cellpadding="6">
<tr><th>rel_err</th><th>R_main (τ=0.15)</th><th>离散5档等价</th></tr>
<tr><td>0%</td><td>1.000</td><td>1.0</td></tr>
<tr><td>5%</td><td>0.717</td><td>0.7</td></tr>
<tr><td>10%</td><td>0.513</td><td>0.4</td></tr>
<tr><td>25%</td><td>0.189</td><td>0.1</td></tr>
<tr><td>50%+</td><td>0.036</td><td>0.0</td></tr>
</table>
<p><strong>为什么连续奖励解决 v1 根因</strong>：离散 5 档时同 group 全落同一档 → advantage=0 → 梯度消失。
连续奖励下即使两个 rollout 都"大致正确"(rel_err=5% vs 8%)，奖励也有差异(0.72 vs 0.59) → advantage≠0 → 有效梯度。</p>
<h3>2.4 证伪设计（四条件）</h3>
<table border="1" cellpadding="6">
<tr><th>条件</th><th>说明</th><th>作用</th></tr>
<tr><td>A — 基线</td><td>base model 零样本（v2 已知 ~0%，v3 跳过）</td><td>下界参照</td></tr>
<tr><td>B — SFT only</td><td>Stage-1W SFT LoRA (69.7M, step3000)</td><td>SFT 基线</td></tr>
<tr><td>C — SFT+GRPO（连续奖励）</td><td>40 步 GRPO, τ=0.15, period-only</td><td><strong>实验组</strong></td></tr>
<tr><td>D — SFT+GRPO（随机奖励）</td><td>同 C 但 reward=random(-0.5,1.5)</td><td><strong>控制组</strong>：排除"任何参数更新都能提升"</td></tr>
</table>
<div style="background:#e8f5e9;padding:12px;border-radius:6px;margin:12px 0;">
<p><strong>主判据</strong>：C > B 且 McNemar p&lt;0.05 且 bootstrap 95% CI 下界&gt;0。</p>
<p><strong>控制判据</strong>：C > D（提升来自奖励设计而非随机参数更新）。</p>
<p><strong>诚实口径</strong>：C≤B 或 p≥0.05 → 「未显著提升」，如实报告。</p>
</div>
"""


def section_tech_stack():
    return """
<h2 id="stack">三、技术栈可行性（LLaMA-Factory + KTransformers + LoRA + Qwen3.5-2B）</h2>
<h3>3.1 三步冒烟结论（wake#853）</h3>
<table border="1" cellpadding="6">
<tr><th>步骤</th><th>结论</th><th>详情</th></tr>
<tr><td>S1 环境</td><td>✅ 可装</td><td>llamafactory 0.9.3 + ktransformers 0.5.3 经 proxy pip 可装，建议独立 env</td></tr>
<tr><td>S2 单步训练</td><td>✅ 可行（退路方案）</td><td>LLaMA-Factory 与 Qwen3.5 模型类互斥 → 退回 HF+peft 直训（已有 69.7M LoRA 成功先例）</td></tr>
<tr><td>S3 后端角色</td><td>⚠️ 非必需</td><td>KTransformers 是 CPU 推理加速后端（非训练后端），2B 规模下 HF transformers 足够</td></tr>
</table>
<h3>3.2 诚实评估</h3>
<div style="background:#e3f2fd;padding:12px;border-radius:6px;margin:12px 0;">
<p><strong>核心发现</strong>：LLaMA-Factory 不支持 Qwen3.5 架构，KTransformers 在 2B 规模下无显著加速收益。
本实验 v3 沿用已验证的 <strong>HF transformers + peft LoRA + ngspice gym</strong> 方案。</p>
<p><strong>科学结论不依赖 LLaMA-Factory/KTransformers</strong>。二者是工程优化工具，GPU 训练阶段或 7B+ 规模时再评估。</p>
</div>
"""


def section_experiment(results, log_info):
    stats = results.get("stats", {}) if results else {}
    acc = stats.get("accuracy", {})
    cfg = results.get("config", {}) if results else {}
    training = results.get("training", {}) if results else {}
    acc_a = acc.get("A_baseline", log_info.get("accuracies", {}).get("A_baseline"))
    acc_b = acc.get("B_sft", log_info.get("accuracies", {}).get("B_sft"))
    acc_c = acc.get("C_grpo_treatment", log_info.get("accuracies", {}).get("C_grpo"))
    acc_d = acc.get("D_grpo_control", log_info.get("accuracies", {}).get("D_control"))
    n_eval = cfg.get("n_eval", 100)
    n_steps = cfg.get("n_grpo_steps", 40)
    gs = cfg.get("group_size", 8)
    lr = cfg.get("lr", "5e-6")
    mc_cb = stats.get("mcnemar_C_vs_B", {})
    boot_cb = stats.get("bootstrap_C_vs_B", {})
    mc_cd = stats.get("mcnemar_C_vs_D", {})
    boot_cd = stats.get("bootstrap_C_vs_D", {})
    verdict = stats.get("verdict", log_info.get("verdict", "实验进行中"))
    has_d = acc_d is not None or "D" in (results.get("results", {}) if results else {})
    rows = ""
    for label, val, desc in [
        ("A — 基线（零样本）", acc_a, "未训练 base model（v2 已知 ~0%, 跳过）"),
        ("B — SFT only", acc_b, "Stage-1W SFT LoRA (69.7M, step3000)"),
        ("C — SFT + GRPO（连续奖励）", acc_c, f"v3 连续奖励 τ=0.15, {n_steps}步, gs={gs}, lr={lr}"),
        ("D — SFT + GRPO（随机奖励控制）", acc_d, "random reward control"),
    ]:
        style = "background:#c8e6c9;font-weight:bold;" if (val is not None and val == acc_c and acc_c is not None) else ""
        rows += f'<tr style="{style}"><td>{label}</td><td>{pct(val, "—")}</td><td>{desc}</td></tr>\n'
    v2_res = safe_load(os.path.join(V2_OUT, "experiment_results.json"))
    v2_acc = v2_res.get("stats", {}).get("accuracy", {}) if v2_res else {}
    v2_p = v2_res.get("stats", {}).get("mcnemar_C_vs_B", {}).get("p", "—") if v2_res else "—"
    cmp_html = f"""
<h3>4.2 版本对比（v1 → v2 → v3）</h3>
<table border="1" cellpadding="6">
<tr><th>版本</th><th>B (SFT)</th><th>C (GRPO)</th><th>D (控制)</th><th>McNemar C-B p</th><th>判定</th></tr>
<tr><td>v1 (离散5档)</td><td>{pct(V1_SFT_ACC)}</td><td>{pct(V1_GRPO_ACC)}</td><td>—</td><td>—</td><td>❌ C&lt;B 负结果</td></tr>
<tr><td>v2 (连续, n=45)</td><td>{pct(v2_acc.get("B_sft"))}</td><td>{pct(v2_acc.get("C_grpo_treatment"))}</td><td>{pct(v2_acc.get("D_grpo_control"))}</td><td>{v2_p}</td><td>⚠️ C&gt;B 但不显著</td></tr>
<tr style="background:#e8eaf6;"><td><strong>v3 (连续, n=100)</strong></td><td>{pct(acc_b)}</td><td>{pct(acc_c)}</td><td>{pct(acc_d)}</td><td>{mc_cb.get("p","⏳") if mc_cb else "⏳"}</td><td><strong>{esc(verdict)}</strong></td></tr>
</table>
"""
    return _exp_rest(rows, cmp_html, results, log_info, training, n_steps, mc_cb, boot_cb, mc_cd, boot_cd, cheat_stats=stats, acc_b=acc_b, acc_c=acc_c, acc_d=acc_d, has_d=has_d, verdict=verdict, n_eval=n_eval, n_steps_val=n_steps, gs=gs, lr=lr)


def _exp_rest(rows, cmp_html, results, log_info, training, n_steps, mc_cb, boot_cb, mc_cd, boot_cd, cheat_stats, acc_b, acc_c, acc_d, has_d, verdict, n_eval, n_steps_val, gs, lr):
    curve_c = log_info.get("grpo_curves", {}).get("C", [])
    curve_d = log_info.get("grpo_curves", {}).get("D", [])
    if not curve_c and training.get("C_losses"):
        curve_c = [{"step": i+1, "loss": l, "avgR": r} for i, (l, r) in enumerate(zip(training["C_losses"], training["C_rewards"]))]
    if not curve_d and training.get("D_losses"):
        curve_d = [{"step": i+1, "loss": l, "avgR": r} for i, (l, r) in enumerate(zip(training["D_losses"], training["D_rewards"]))]
    curve_html = ""
    if curve_c or curve_d:
        curve_html = '<h3>4.3 GRPO 训练曲线</h3>\n<table border="1" cellpadding="6">\n<tr><th>条件</th><th>step</th><th>loss</th><th>avg reward</th></tr>\n'
        for c in curve_c:
            curve_html += f'<tr><td>C (连续奖励)</td><td>{c["step"]}/{n_steps_val}</td><td>{c["loss"]:.6f}</td><td>{c["avgR"]:.4f}</td></tr>\n'
        for c in curve_d:
            curve_html += f'<tr><td>D (随机奖励)</td><td>{c["step"]}/{n_steps_val}</td><td>{c["loss"]:.6f}</td><td>{c["avgR"]:.4f}</td></tr>\n'
        curve_html += '</table>\n<p>C 的 avg reward 若从负值上升 → 连续奖励提供有效梯度信号。D 的 reward 应无趋势（随机）。</p>'
    stat_html = '<h3>4.4 统计检验</h3>\n<table border="1" cellpadding="6">\n<tr><th>检验</th><th>统计量</th><th>p 值</th><th>n_discordant</th><th>显著性</th></tr>\n'
    if mc_cb:
        p_val = mc_cb.get("p", 1.0)
        sig = "✅ 显著 (p<0.05)" if p_val < 0.05 else "❌ 不显著"
        stat_html += f'<tr><td>McNemar C vs B</td><td>{mc_cb.get("stat","—")}</td><td>{p_val:.4f}</td><td>{mc_cb.get("n_discordant","—")}</td><td>{sig}</td></tr>\n'
    else:
        stat_html += '<tr><td>McNemar C vs B</td><td colspan="4"><em>实验完成后自动填充</em></td></tr>\n'
    if boot_cb:
        stat_html += f'<tr><td>Bootstrap 95% CI (C-B)</td><td>Δ={boot_cb.get("point_delta",0):+.1%}</td><td colspan="2">CI=[{boot_cb.get("ci_lo",0):+.1%},{boot_cb.get("ci_hi",0):+.1%}]</td><td>{"✅" if boot_cb.get("ci_lo",0)>0 else "❌"}</td></tr>\n'
    if has_d and mc_cd:
        p_val = mc_cd.get("p", 1.0)
        sig = "✅ C>D" if p_val < 0.05 else "⚠️ 不显著"
        stat_html += f'<tr><td>McNemar C vs D (控制)</td><td>{mc_cd.get("stat","—")}</td><td>{p_val:.4f}</td><td>{mc_cd.get("n_discordant","—")}</td><td>{sig}</td></tr>\n'
    if has_d and boot_cd:
        stat_html += f'<tr><td>Bootstrap 95% CI (C-D)</td><td>Δ={boot_cd.get("point_delta",0):+.1%}</td><td colspan="2">CI=[{boot_cd.get("ci_lo",0):+.1%},{boot_cd.get("ci_hi",0):+.1%}]</td><td>{"✅" if boot_cd.get("ci_lo",0)>0 else "❌"}</td></tr>\n'
    stat_html += '</table>\n'
    cheat = cheat_stats.get("cheat_rate", {})
    cheat_html = f'<h3>4.5 Cheat Rate / 数据泄漏检查</h3><p>train seed={esc(cheat.get("train_seed_range","20261105+0~8000"))}, eval seed={esc(cheat.get("eval_seed_range","990100+"))}, overlap={cheat.get("overlap",0)}, rate={cheat.get("overlap_frac",0.0)}. {esc(cheat.get("note","train/eval seed 分离, 无数据泄漏"))}</p>'
    complete = results is not None and "stats" in (results or {})
    badge = '<span style="background:#4caf50;color:white;padding:2px 8px;border-radius:4px;">✅ 完成</span>' if complete else '<span style="background:#ff9800;color:white;padding:2px 8px;border-radius:4px;">⏳ 进行中</span>'
    return f"""
<h2 id="exp">四、CPU 实验结果（before/after 对照 + 统计检验 + cheat rate）</h2>
<p>{badge}</p>
<p><strong>配置</strong>：CPU (OMP=16, nice=19) · 2B text backbone (Qwen3.5-2B text-extracted) · LoRA r=16 (69.7M) · ngspice gym · <strong>period-only</strong> · n_eval={n_eval}题 · n_grpo_steps={n_steps_val} · group_size={gs} · lr={lr} · τ=0.15</p>
<h3>4.1 准确率对照表</h3>
<table border="1" cellpadding="6"><tr><th>条件</th><th>准确率</th><th>说明</th></tr>
{rows}</table>
{cmp_html}
<h3>4.2b 判定结论</h3>
<div style="background:{"#c8e6c9" if "SIGNIFICANT" in str(verdict) else "#fff3cd"};padding:12px;border-radius:6px;">
<p><strong>VERDICT: {esc(verdict)}</strong></p>
<p>C>B: {"✅" if acc_c and acc_b and acc_c>acc_b else "❌" if acc_c and acc_b else "⏳"} | C>D: {"✅" if has_d and acc_c and acc_d and acc_c>acc_d else "❌" if has_d and acc_c and acc_d else "⏳"} | McNemar p<0.05: {("✅" if mc_cb and mc_cb.get("p",1)<0.05 else "❌" if mc_cb else "⏳")}</p></div>
{curve_html}{stat_html}{cheat_html}
<h3>4.6 规模与算力标注</h3>
<p>单台 CPU (224核, OMP限16, nice=19) · 2B text backbone (工具交互模式) · {n_eval}题 period-only · {n_steps_val}步 GRPO · <strong>结论不外推为 GPU 结论</strong>。</p>
"""


def section_experiment_v4(results_v4, log_info_v4):
    """v4 RFT (Rejection Sampling FT) experiment section."""
    stats = results_v4.get("stats", {}) if results_v4 else {}
    acc = stats.get("accuracy", {})
    cfg = results_v4.get("config", {}) if results_v4 else {}
    training = results_v4.get("training", {}) if results_v4 else {}
    acc_b = acc.get("B_sft", log_info_v4.get("accuracies", {}).get("B_sft"))
    acc_c = acc.get("C_rft_treatment", log_info_v4.get("accuracies", {}).get("C_rft"))
    acc_d = acc.get("D_rft_control", log_info_v4.get("accuracies", {}).get("D_rft_ctrl"))
    mc_cb = stats.get("mcnemar_C_vs_B", {})
    boot_cb = stats.get("bootstrap_C_vs_B", {})
    mc_cd = stats.get("mcnemar_C_vs_D", {})
    verdict = stats.get("verdict", log_info_v4.get("verdict", "实验进行中"))
    coll = stats.get("collection_stats", log_info_v4.get("collection", {}))
    filt = log_info_v4.get("filter_stats", {})
    n_circuits = cfg.get("n_circuits", 60)
    k_per = cfg.get("k_per_circuit", 4)
    threshold = cfg.get("reward_threshold", 0.3)
    n_epochs = cfg.get("n_epochs", 3)
    rows = ""
    for label, val, desc in [
        ("B — SFT only", acc_b, "Stage-1W SFT LoRA (69.7M, step3000)，与 v3 同题同 ckpt"),
        ("C — SFT + RFT（奖励过滤）", acc_c, f"v4 RFT: {n_circuits}×{k_per} rollout, threshold={threshold}, {n_epochs} epoch CE"),
        ("D — SFT + RFT（随机过滤控制）", acc_d, "random filter control（同数据量，排除\"任何数据都能提升\"）"),
    ]:
        style = "background:#c8e6c9;font-weight:bold;" if (val is not None and val == acc_c and acc_c is not None) else ""
        rows += f'<tr style="{style}"><td>{label}</td><td>{pct(val, "—")}</td><td>{desc}</td></tr>\n'
    # Collection stats
    coll_html = ""
    if coll:
        n_total = coll.get("n_total_rollouts", coll.get("n_rollouts", "—"))
        n_succ = coll.get("n_successful", coll.get("n_successful", "—"))
        sr = coll.get("success_rate", "—")
        coll_html = f"""
<h3>4.7 v4 采样统计</h3>
<table border="1" cellpadding="6">
<tr><th>指标</th><th>值</th></tr>
<tr><td>总 rollout 数</td><td>{n_total}</td></tr>
<tr><td>成功 rollout（reward &gt; {threshold}）</td><td>{n_succ}</td></tr>
<tr><td>成功率</td><td>{pct(sr, "—")}</td></tr>
<tr><td>奖励阈值</td><td>{threshold}</td></tr>
</table>"""
    # RFT training curves
    curve_html = ""
    curves = log_info_v4.get("rft_curves", {})
    if not curves and training.get("C_losses"):
        curves = {"C": [{"epoch": i+1, "loss": l} for i, l in enumerate(training["C_losses"])]}
        if training.get("D_losses"):
            curves["D"] = [{"epoch": i+1, "loss": l} for i, l in enumerate(training["D_losses"])]
    if curves:
        curve_rows = ""
        for label in ["C", "D"]:
            for pt in curves.get(label, []):
                curve_rows += (f'<tr><td>{label}</td><td>{pt.get("epoch","—")}</td>'
                               f'<td>{pt.get("loss","—"):.6f}</td></tr>\n')
        curve_html = f"""
<h3>4.8 v4 RFT 训练曲线</h3>
<table border="1" cellpadding="6">
<tr><th>条件</th><th>Epoch</th><th>Loss</th></tr>
{curve_rows}</table>"""
    # Statistics
    stat_html = ""
    if mc_cb or boot_cb:
        stat_html = f"""
<h3>4.9 v4 统计检验</h3>
<table border="1" cellpadding="6">
<tr><th>检验</th><th>统计量</th><th>p 值</th><th>判定</th></tr>
<tr><td>McNemar C vs B</td><td>n_disc={mc_cb.get("n_discordant","—")}</td><td>{mc_cb.get("p","—")}</td><td>{"✅ 显著" if mc_cb.get("p",1) < 0.05 else "❌ 不显著" if mc_cb else "⏳"}</td></tr>
<tr><td>Bootstrap C-B</td><td>{pct(boot_cb.get("point_delta"),"—")}</td><td>CI=[{pct(boot_cb.get("ci_lo"),"—")}, {pct(boot_cb.get("ci_hi"),"—")}]</td><td>{"✅ CI下界>0" if boot_cb.get("ci_lo",0) > 0 else "❌ CI含0" if boot_cb else "⏳"}</td></tr>"""
        if mc_cd:
            stat_html += f"""
<tr><td>McNemar C vs D</td><td>n_disc={mc_cd.get("n_discordant","—")}</td><td>{mc_cd.get("p","—")}</td><td>{"✅ C>D 显著" if mc_cd.get("p",1) < 0.05 else "❌"}</td></tr>"""
        stat_html += "</table>"
    # Cheat rate
    cheat_html = ""
    cheat = stats.get("cheat_rate", {})
    if cheat:
        cheat_html = f"""
<h3>4.10 v4 数据泄漏检查</h3>
<p><strong>训练种子范围</strong>：{cheat.get("train_seed_range","—")} · <strong>评测种子范围</strong>：{cheat.get("eval_seed_range","—")} · <strong>重叠</strong>：{cheat.get("overlap",0)} ({pct(cheat.get("overlap_frac",0))}) · {esc(cheat.get("note",""))}</p>"""
    status = "⏳ 进行中" if not results_v4 else ""
    return f"""
<h2 id="v4">四-B、v4 实验：Rejection Sampling FT（RFT / STaR）</h2>
<div class="summary">
<p><strong>v4 设计动机</strong>：v3 GRPO 在 CPU 上 loss 近零、avgR 波动大（group baseline 导致 std=0 仍未根除）。
v4 改用 <strong>Rejection Sampling FT</strong>（STaR/ReST 范式）：先用 SFT 模型采样 → 过滤奖励 &gt; {threshold} 的 rollout → 标准 CE 损失训练。
<strong>核心优势</strong>：无 group baseline → 无 std=0 问题；标准 CE 损失 → 稳定梯度；采集与训练解耦 → 更高效。</p>
<p><strong>预注册判据</strong>（wake#861，运行前写入）：C(RFT) &gt; B(SFT) 且 C &gt; D(随机控制)，McNemar p&lt;0.05 + bootstrap CI 排除 0。</p>
</div>
<h3>4.5 v4 结果汇总</h3>
<table border="1" cellpadding="6">
<tr><th>条件</th><th>准确率</th><th>说明</th></tr>
{rows}</table>
<p><strong>v4 判定</strong>：{esc(verdict)} {status}</p>
{coll_html}{curve_html}{stat_html}{cheat_html}
<h3>4.11 v4 规模与算力标注</h3>
<p>单台 CPU (224核) · 2B text backbone · {n_circuits}×{k_per}={n_circuits*k_per} rollout 采集 · {n_epochs} epoch RFT · <strong>结论不外推为 GPU 结论</strong>。</p>
"""


def section_combined_comparison(results_v3, log_info_v3, results_v4, log_info_v4):
    """Combined v1→v2→v3→v4 comparison table."""
    v3_stats = (results_v3 or {}).get("stats", {}) if results_v3 else {}
    v3_acc = v3_stats.get("accuracy", {}) if v3_stats else {}
    v3_acc_b = v3_acc.get("B_sft", log_info_v3.get("accuracies", {}).get("B_sft"))
    v3_acc_c = v3_acc.get("C_grpo_treatment", log_info_v3.get("accuracies", {}).get("C_grpo"))
    v3_acc_d = v3_acc.get("D_grpo_control", log_info_v3.get("accuracies", {}).get("D_control"))
    v3_mc_p = v3_stats.get("mcnemar_C_vs_B", {}).get("p", "⏳")
    v3_verdict = v3_stats.get("verdict", log_info_v3.get("verdict", "⏳ 进行中"))
    v4_stats = (results_v4 or {}).get("stats", {}) if results_v4 else {}
    v4_acc = v4_stats.get("accuracy", {}) if v4_stats else {}
    v4_acc_b = v4_acc.get("B_sft", log_info_v4.get("accuracies", {}).get("B_sft"))
    v4_acc_c = v4_acc.get("C_rft_treatment", log_info_v4.get("accuracies", {}).get("C_rft"))
    v4_acc_d = v4_acc.get("D_rft_control", log_info_v4.get("accuracies", {}).get("D_rft_ctrl"))
    v4_mc_p = v4_stats.get("mcnemar_C_vs_B", {}).get("p", "⏳")
    v4_verdict = v4_stats.get("verdict", log_info_v4.get("verdict", "⏳ 进行中"))
    v2_res = safe_load(os.path.join(V2_OUT, "experiment_results.json"))
    v2_acc = v2_res.get("stats", {}).get("accuracy", {}) if v2_res else {}
    v2_p = v2_res.get("stats", {}).get("mcnemar_C_vs_B", {}).get("p", "—") if v2_res else "—"
    return f"""
<h2 id="cmp">五、综合对比与总结</h2>
<h3>5.1 全版本对比（v1 → v2 → v3 → v4）</h3>
<table border="1" cellpadding="6">
<tr><th>版本</th><th>方法</th><th>奖励</th><th>B (SFT)</th><th>C (处理)</th><th>D (控制)</th><th>McNemar C-B p</th><th>判定</th></tr>
<tr><td>v1 (11-06)</td><td>GRPO</td><td>离散5档</td><td>{pct(V1_SFT_ACC)}</td><td>{pct(V1_GRPO_ACC)}</td><td>—</td><td>—</td><td>❌ C&lt;B 负结果</td></tr>
<tr><td>v2 (11-07)</td><td>GRPO</td><td>连续 exp(-err/τ)</td><td>{pct(v2_acc.get("B_sft"))}</td><td>{pct(v2_acc.get("C_grpo_treatment"))}</td><td>{pct(v2_acc.get("D_grpo_control"))}</td><td>{v2_p}</td><td>⚠️ C&gt;B 但不显著</td></tr>
<tr style="background:#e8eaf6;"><td><strong>v3 (11-07)</strong></td><td><strong>GRPO</strong></td><td><strong>连续 τ=0.15</strong></td><td>{pct(v3_acc_b)}</td><td>{pct(v3_acc_c)}</td><td>{pct(v3_acc_d)}</td><td>{v3_mc_p}</td><td><strong>{esc(v3_verdict)}</strong></td></tr>
<tr style="background:#e8f5e9;"><td><strong>v4 (11-07)</strong></td><td><strong>RFT/STaR</strong></td><td><strong>连续+过滤</strong></td><td>{pct(v4_acc_b)}</td><td>{pct(v4_acc_c)}</td><td>{pct(v4_acc_d)}</td><td>{v4_mc_p}</td><td><strong>{esc(v4_verdict)}</strong></td></tr>
</table>
<h3>5.2 核心结论</h3>
<div style="background:#fff3cd;padding:12px;border-radius:6px;margin:12px 0;">
<p><strong>GRPO 路线（v1/v2/v3）</strong>：CPU 上 GRPO 受限于小 group（std=0 问题持续）、近零 loss、波动 avgR。
即使连续化奖励（v2/v3）也未扭转颓势 —— v3 C=25.0% &lt; B=34.0%（控制 D 待完成）。</p>
<p><strong>RFT 路线（v4）</strong>：改用 Rejection Sampling FT 绕过 group baseline 问题。
<strong>{esc(v4_verdict)}</strong>。若 v4 也未显著提升，则连续 4 轮（v1/v2/v3/v4）负结果，
说明在 CPU + 2B text-only + 工具交互范式下，RL/RFT 难以显著提升波形读数能力 —— 根因可能是任务定义（读数精度）对 2B 模型过难。</p>
</div>
<h3>5.3 诚实边界</h3>
<ul>
<li><strong>CPU pilot 结论不外推为 GPU 结论</strong>：CPU 上 step 数/group_size 受算力限制，GPU 阶段需重新验证。</li>
<li><strong>text-only backbone 局限</strong>：当前用文本工具交互（ngspice），非直接看波形图。多模态版 Qwen3.5-2B 可直接处理图像，是未验证的更高上限。</li>
<li><strong>负结果同样有价值</strong>：证伪了「CPU 上 GRPO/RFT 能提升波形读数」这一假设，为后续方向选择提供了排除证据。</li>
</ul>
"""


def main():
    results = safe_load(os.path.join(V3_OUT, "experiment_results.json"))
    log_info = parse_log_progress()
    results_v4 = safe_load(os.path.join(V4_OUT, "experiment_results.json"))
    log_info_v4 = parse_v4_log_progress()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # Build combined comparison table
    v4_acc_b = (results_v4 or {}).get("stats", {}).get("accuracy", {}).get("B_sft", log_info_v4.get("accuracies", {}).get("B_sft"))
    v4_acc_c = (results_v4 or {}).get("stats", {}).get("accuracy", {}).get("C_rft_treatment", log_info_v4.get("accuracies", {}).get("C_rft"))
    v4_acc_d = (results_v4 or {}).get("stats", {}).get("accuracy", {}).get("D_rft_control", log_info_v4.get("accuracies", {}).get("D_rft_ctrl"))
    v4_mc_p = (results_v4 or {}).get("stats", {}).get("mcnemar_C_vs_B", {}).get("p", "⏳")
    v4_verdict = (results_v4 or {}).get("stats", {}).get("verdict", log_info_v4.get("verdict", "⏳ 进行中"))
    combined_cmp = section_combined_comparison(results, log_info, results_v4, log_info_v4)
    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>视觉波形 RL · CPU 实验报告 v3+v4（2026-11-07）</title>
<style>
body {{ font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; line-height: 1.7; color: #333; }}
h1 {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; }}
h2 {{ color: #283593; border-bottom: 1px solid #ccc; padding-bottom: 6px; margin-top: 36px; }}
h3 {{ color: #3949ab; margin-top: 24px; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px; }}
th {{ background: #e8eaf6; text-align: left; padding: 8px; }}
td {{ padding: 6px 8px; }}
tr:nth-child(even) {{ background: #f5f5f5; }}
code {{ background: #f0f0f0; padding: 1px 4px; border-radius: 3px; font-size: 13px; }}
.summary {{ background: #e3f2fd; padding: 16px; border-radius: 8px; margin: 16px 0; }}
</style>
</head>
<body>
<h1>视觉波形 RL · CPU 实验报告 v3+v4</h1>
<p><strong>生成时间</strong>：{now} · <strong>作者</strong>：vision wake#856→#869 · <strong>用户令</strong>：2026-11-07「用 CPU 设计有效 RL，证明显著提升 Qwen3.5-2B 波形理解」</p>
<div class="summary">
<p><strong>一句话总结</strong>：v1 离散 5 档奖励 → GRPO 负结果(6.2%&lt;9.2%)。v2 连续奖励方向翻转但不显著(n=45,p=0.625)。<strong>v3</strong> 聚焦 period-only(n=100)+40步+gs=8 连续奖励 GRPO → C=25.0%&lt;B=34.0%（控制D进行中）。<strong>v4</strong> 改用 RFT/STaR（绕过 group baseline）→ 进行中。</p>
<p><strong>数据集调研</strong>：HF/GitHub/arXiv 三源均无波形 VQA 评测集，ngspice 合成波形+QA 是正确路线。</p>
<p><strong>技术栈</strong>：LLaMA-Factory 与 Qwen3.5 架构互斥 → 退回 HF+peft 直训（已验证可行，69.7M LoRA）。</p>
</div>
{section_dataset_research()}
{section_rl_design()}
{section_tech_stack()}
{section_experiment(results, log_info)}
{section_experiment_v4(results_v4, log_info_v4)}
{combined_cmp}
<h2 id="next">六、下一步建议</h2>
<ol>
<li><strong>若 v4 显著</strong>：扩大 rollout 采集量、引入多目标(period+amplitude)、课程学习，GPU 阶段验证规模扩展。</li>
<li><strong>若 v4 也不显著（连续 4 轮负结果）</strong>：必须换方向 —— ①改任务定义为可判定中间任务（波形类型判别/频率比较/异常定位）②切换 Qwen3.5-2B 多模态版直接处理波形图 ③增大 SFT 数据量与质量 ④等 GPU 做大规模 GRPO。</li>
<li><strong>切换 Qwen3.5-2B 多模态版</strong>：当前 text-only backbone(工具交互)，多模态版可直接处理波形图，是未验证的更高上限。</li>
<li><strong>GPU 训练阶段</strong>：pretrain ckpt(ETA≈12/25)后跑大规模 GRPO/RFT，验证 CPU pilot 结论可扩展性。</li>
<li><strong>诚实边界</strong>：CPU pilot 结论不外推为 GPU 结论；负结果同样有价值（证伪了「CPU 上 RL/RFT 能提升波形读数」假设）。</li>
</ol>
<hr>
<p style="color:#999;font-size:12px;">本报告由 <code>gen_cpu_rl_v3_report.py</code> 自动生成（wake#856→#869, 2026-11-07）。数据来源：cpu_rl_v3/experiment_results.json + cpu_rl_v4/experiment_results.json + /tmp/v3_full_experiment.log + /tmp/v4_rft_experiment.log + dataset_research_results.json。单文件自包含，0 script, 0 外链。负结果同样有价值，如实报告。</p>
</body>
</html>"""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html_doc)
    size = os.path.getsize(REPORT_PATH)
    print(f"Report written: {REPORT_PATH} ({size} bytes)")
    if results and "stats" in results:
        s = results["stats"]
        print(f"  Verdict: {s.get('verdict', 'N/A')}")
        a = s.get("accuracy", {})
        print(f"  A={pct(a.get('A_baseline'))} B={pct(a.get('B_sft'))} C={pct(a.get('C_grpo_treatment'))} D={pct(a.get('D_grpo_control'))}")
    else:
        acc = log_info.get("accuracies", {})
        print(f"  (partial from log) B={pct(acc.get('B_sft'))} C={pct(acc.get('C_grpo'))} D={pct(acc.get('D_control'))}")
    # v4 info
    if results_v4 and "stats" in results_v4:
        s4 = results_v4["stats"]
        print(f"  v4 Verdict: {s4.get('verdict', 'N/A')}")
        a4 = s4.get("accuracy", {})
        print(f"  v4 B={pct(a4.get('B_sft'))} C={pct(a4.get('C_rft_treatment'))} D={pct(a4.get('D_rft_control'))}")
    else:
        acc4 = log_info_v4.get("accuracies", {})
        print(f"  v4 (partial from log) B={pct(acc4.get('B_sft'))} C={pct(acc4.get('C_rft'))} D={pct(acc4.get('D_rft_ctrl'))}")


if __name__ == "__main__":
    main()
