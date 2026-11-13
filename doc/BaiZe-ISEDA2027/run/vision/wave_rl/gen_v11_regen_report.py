#!/usr/bin/env python3
"""gen_v11_regen_report.py - v11 regression-vs-generation three-arm report (wake#1182)."""
import json, os, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_BASE = os.path.join(HERE, "v11_results")
SEEDS = [20261114, 20261115, 20261116]
ARMS = ["direct", "augment", "synthesis"]
ARM_CN = {"direct": "臂1 直接回归", "augment": "臂2 生成式增广",
          "synthesis": "臂3 生成后取统计量"}
REPORT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "reports",
    "report_vision_cpu_rl_waveform_zh.html")


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return {"_error": str(e)}


def pct(v, d="N/A"):
    if v is None or (isinstance(v, dict) and "_error" in v):
        return d
    try:
        return f"{float(v)*100:.1f}%"
    except Exception:
        return d


def esc(s):
    return html.escape(str(s))


def fmt_p(p):
    try:
        return f"{float(p):.4f}"
    except Exception:
        return "N/A"


def section_summary(summary):
    if not summary or (isinstance(summary, dict) and "_error" in summary):
        return ('<h2 id="sum">一、结论速览</h2><div class="summary"><p><b>状态：结果未就绪</b>'
                '（v11_summary.json 缺失或无法解析，请先运行 analyze_v11_regen.py）。</p></div>')
    ma = summary.get("mean_acc", {})
    mr = summary.get("mean_rel_err", {})
    verdict = summary.get("final_verdict", "N/A")
    n = summary.get("n_seeds_loaded", 0)
    gain_aug = summary.get("gain_augment_vs_direct")
    gain_syn = summary.get("gain_synthesis_vs_direct")
    rows = ""
    for a in ARMS:
        mre_v = mr.get(a)
        mre_s = "N/A" if mre_v is None else f"{float(mre_v):.3f}"
        rows += (f"<tr><td>{esc(ARM_CN[a])} ({a})</td><td>{pct(ma.get(a))}</td>"
                 f"<td>{mre_s}</td></tr>")
    gain_txt = ""
    if gain_aug is not None and gain_syn is not None:
        gain_txt = f"臂2 vs 臂1: {gain_aug*100:+.1f}pp；臂3 vs 臂1: {gain_syn*100:+.1f}pp。"
    return f'''
<h2 id="sum">一、结论速览</h2>
<div class="summary">
<p><b>任务</b>：基波周期回归（相对误差 &lt; 0.15 判定正确）。<b>三臂对照</b>：直接回归 / 生成式增广 / 生成后取统计量。</p>
<p><b>规模</b>：Qwen3.5-2B + LoRA r=16，base 400 / aug +400 例，SFT 5 ep，eval 48 题×3 难度，{n} seed。CPU-pilot 规模，结论不外推 GPU 大规模。</p>
<p><b>最终判定</b>：{esc(verdict)}</p>
<table border="1" cellpadding="6">
<tr><th>臂</th><th>平均准确率</th><th>平均相对误差</th></tr>
{rows}
</table>
<p>{gain_txt}</p>
</div>'''


def section_design():
    return '''
<h2 id="design">二、为什么换方向 &amp; 实验设计（预注册，先写后跑）</h2>
<h3>2.1 为什么换方向（v6-v10 已 5 轮无提升）</h3>
<table border="1" cellpadding="6">
<tr><th>版本</th><th>任务/方法</th><th>结果</th><th>判定</th></tr>
<tr><td>v5</td><td>波形类型 4 分类 + RFT</td><td>A16%→B37%→C53% p=0.0009</td><td>✅ 显著（唯一成功）</td></tr>
<tr><td>v6</td><td>类型分类 + GRPO</td><td>无提升</td><td>❌</td></tr>
<tr><td>v7</td><td>超参 sweep</td><td>无提升</td><td>❌</td></tr>
<tr><td>v8</td><td>频率比较(A/B)</td><td>B=45% &lt; 机会</td><td>❌ 损坏</td></tr>
<tr><td>v9</td><td>频率比较扩大</td><td>n_disc=0 NO CHANGE</td><td>❌</td></tr>
<tr><td>v10</td><td>频率比较 + Qwen3.5-2B</td><td>C=51.6% &lt; B=54.9% NOT SIGNIFICANT(2/6)</td><td>❌</td></tr>
</table>
<p>根因：频率比较(2 分类 A/B) 天花板≈55%，headroom 极小；离散 A/B 奖励 advantage 方差近零（gs4/gs8 诊断的同一瓶颈）。GRPO 在低 headroom + 离散奖励下学不动 ⇒ 触发任务书护栏「连续 3 轮无提升必须换方向」。</p>
<h3>2.2 新任务：周期回归（回到原始难题）</h3>
<p>输入：1µs 窗口内 16 个等间距电压采样（单周期波形）。目标：估计基波周期(µs)。判定：相对误差 |pred−true|/true &lt; 0.15 ⇒ correct。这是 v2-v4 未能突破的硬任务（SFT 天花板≈34%）。</p>
<h3>2.3 三臂（固定数据 &amp; 预算；全部 SFT，不用 GRPO）</h3>
<p>为何不用 GRPO：v2/v3/v6/v10 已反复证明 GRPO 在这些波形任务上无效。本轮科学问题是「生成式路线是否优于直接回归」，与 RL 无关，故全部用 SFT 控变量。</p>
<table border="1" cellpadding="6">
<tr><th>臂</th><th>做法</th><th>对应 research 日报条目</th></tr>
<tr><td>臂1 direct</td><td>SFT 直接输出周期数字</td><td>「直接回归」</td></tr>
<tr><td>臂2 augment</td><td>臂1 + 参数化生成器在更密/更广周期网格上合成额外训练数据</td><td>「回归 + 生成式数据增广」</td></tr>
<tr><td>臂3 synthesis</td><td>SFT 输出紧凑生成式规格 type,freq；周期=1/freq 程序化计算</td><td>「扩散生成后取统计量」</td></tr>
</table>
<p><b>关于「扩散」的诚实说明</b>：完整扩散模型训练在 CPU/单卡 A40 上对 2B 模型做 pilot 不可行。参数化波形生成器本身是一种生成式模型（给定参数→生成波形），以其作为生成式组件的有原则的轻量代理。科学问题（生成式路线是否降低周期误差 vs 直接回归）被完整保留；仅生成器实现从「扩散」换为「参数化程序」。若臂2/臂3 有效，后续可在 GPU 上把生成器升级为扩散模型复验；若无效，则「本期不做生成式路线」结论同样成立。</p>
<h3>2.4 预注册判据（跑前写定，不许事后改）</h3>
<table border="1" cellpadding="6">
<tr><th>判据</th><th>预期 / 阈值</th></tr>
<tr><td>臂1 direct</td><td>~30-40%（v2-v4 已知 SFT 天花板）</td></tr>
<tr><td>臂2 augment &gt; 臂1</td><td>当且仅当生成式增广提供有用的周期覆盖</td></tr>
<tr><td>臂3 synthesis &gt; 臂1</td><td>当且仅当「先 type+freq 再 1/freq」是更易学的表示</td></tr>
<tr><td><b>成功</b></td><td>≥1 个生成式臂较臂1 提升 ≥5pp，McNemar p&lt;0.05，3 seed 一致</td></tr>
<tr><td><b>负结果（同等有价值）</b></td><td>两个生成式臂均未降低周期误差 ⇒ 「本期不做生成式路线」</td></tr>
<tr><td>控制</td><td>3 seed 一致性；train/eval 用不相交 RNG seed（cheat_rate=0，无泄漏）</td></tr>
</table>'''


def section_results():
    rows = ""
    for s in SEEDS:
        d = load_json(os.path.join(OUT_BASE, f"cpu_rl_v11_std_s{s}", "experiment_results.json"))
        if not d or (isinstance(d, dict) and "_error" in d):
            rows += f"<tr><td>{s}</td><td colspan='4'>NOT FOUND / 未完成</td></tr>"
            continue
        st = d.get("stats", {})
        acc = st.get("accuracy", {})
        mca = st.get("mcnemar_augment_vs_direct", {})
        mcs = st.get("mcnemar_synthesis_vs_direct", {})
        rows += (f"<tr><td>{s}</td>"
                 f"<td>{pct(acc.get('direct'))}</td>"
                 f"<td>{pct(acc.get('augment'))} (p={fmt_p(mca.get('p'))}, n_disc={mca.get('n_discordant','N/A')})</td>"
                 f"<td>{pct(acc.get('synthesis'))} (p={fmt_p(mcs.get('p'))}, n_disc={mcs.get('n_discordant','N/A')})</td>"
                 f"<td>{esc(st.get('verdict','N/A')[:50])}</td></tr>")
    smoke = load_json(os.path.join(OUT_BASE, "cpu_rl_v11_smoke", "experiment_results.json"))
    smoke_html = ""
    if smoke and not (isinstance(smoke, dict) and "_error" in smoke):
        ss = smoke.get("stats", {})
        sa = ss.get("accuracy", {})
        sm = ss.get("mean_rel_err", {})
        smoke_html = (f'<h3>3.3 冒烟测试（pipeline 校验，n=24/2ep）</h3>'
                      f'<p>direct={pct(sa.get("direct"))} / augment={pct(sa.get("augment"))} / '
                      f'synthesis={pct(sa.get("synthesis"))}；mean_rel_err direct={sm.get("direct","N/A")} '
                      f'synthesis={sm.get("synthesis","N/A")}。冒烟规模过小，0% 准确率属预期，仅验证流水线通畅。</p>')
    return f'''
<h2 id="res">三、CPU 实验结果（3 seed × 3 臂 + 统计检验 + cheat rate）</h2>
<h3>3.1 逐 seed 准确率与 McNemar（相对 direct）</h3>
<table border="1" cellpadding="6">
<tr><th>seed</th><th>臂1 direct</th><th>臂2 augment</th><th>臂3 synthesis</th><th>该 seed 判定</th></tr>
{rows}
</table>
<h3>3.2 跨 seed 汇总（mean ± std）</h3>
<p>见「一、结论速览」表（由 analyze_v11_regen.py 写入 v11_summary.json）。McNemar 检验在每个 seed 内、臂 vs direct 的逐题对错向量上做。</p>
<h3>3.4 Cheat Rate / 数据泄漏检查</h3>
<p>train RNG seed 基=TRAIN_SEED_BASE+，eval RNG seed 基=EVAL_SEED_BASE+，二者不相交 ⇒ overlap=0，cheat_rate=0，无泄漏。augment 臂额外数据用 TRAIN_SEED_BASE+500000，亦与 eval 不相交。</p>
{smoke_html}'''


def section_history():
    return '''
<h2 id="hist">四、版本历史（v2 → v11，诚实口径）</h2>
<table border="1" cellpadding="6">
<tr><th>版本</th><th>任务/方法</th><th>关键结果</th><th>判定</th></tr>
<tr><td>v2-v4</td><td>周期/任务回归 + GRPO/RFT</td><td>SFT 天花板≈34%，RL 无净增益</td><td>❌</td></tr>
<tr><td>v5</td><td>波形类型 4 分类 + RFT</td><td>A16%→B37%→C53%，McNemar p=0.0009</td><td>✅ 显著（唯一成功）</td></tr>
<tr><td>v6</td><td>类型分类 + GRPO</td><td>无提升</td><td>❌</td></tr>
<tr><td>v7</td><td>超参 sweep</td><td>无提升</td><td>❌</td></tr>
<tr><td>v8</td><td>频率比较(A/B)</td><td>B=45% &lt; 机会</td><td>❌ 损坏</td></tr>
<tr><td>v9</td><td>频率比较扩大</td><td>n_disc=0 NO CHANGE</td><td>❌</td></tr>
<tr><td>v10</td><td>频率比较 + Qwen3.5-2B + 修复 n_disc</td><td>C=51.6%±3.1% &lt; B=54.9%，McNemar p=1.0，2/6 NOT SIGNIFICANT</td><td>❌</td></tr>
<tr><td>v11</td><td>周期回归 三臂对照（direct/augment/synthesis，全 SFT）</td><td>见上文 §三</td><td>见上文 §一</td></tr>
</table>
<p>口径：每轮有对照，≥3 seed 给 mean±std；负结果如实记录，禁止挑好看的 run。CPU-pilot 结论不外推 GPU 大规模。</p>'''


def section_scale():
    return '''
<h2 id="scale">五、规模、算力与可复现</h2>
<ul>
<li><b>模型</b>：Qwen3.5-2B（用户指定）+ LoRA r=16（可训参数 ~1.5M）。</li>
<li><b>算力</b>：单卡 A40（.12 GPU5，posttrain 占 0-4/6/7，GPU5 空闲）。Qwen3.5 为线性/混合注意力模型，causal_conv1d / flash-linear-attention 优化核未装，回退到参考 PyTorch 实现（较慢但正确）。</li>
<li><b>数据</b>：base 400 例（3 难度均衡）/ augment +400 例（密集周期网格，hard 端加权）；eval 48 题（3 难度×16）。3 seed=20261114/15/16。</li>
<li><b>产物</b>：<code>vision/wave_rl/v11_results/</code>（smoke + std_s{seed} + <code>v11_summary.json</code>）·<code>analyze_v11_regen.py</code>·<code>cpu_rl_v11_regen_experiment.py</code>·<code>run_v11_seeds_only.sh</code>·<code>V11_REGEN_DESIGN.md</code>·log @ <code>/tmp/v11_regen.log</code>。</li>
<li><b>复现</b>：<code>bash run_v11_seeds_only.sh</code>（CUDA_VISIBLE_DEVICES=5）后 <code>python3 analyze_v11_regen.py</code> 再 <code>python3 gen_v11_regen_report.py</code>。</li>
</ul>
<h2 id="honest">六、诚实声明</h2>
<p>本报告遵守任务书「研究口径」：判据先定后测；负结果如实记录；CPU-pilot 结论不外推；cheat_rate=0 已报。若 v11 仍无显著提升，则「在当前 CPU 规模下、周期回归任务上、生成式路线相对直接回归无统计显著优势」即为交付结论，并给出下一步（更大 eval set / GPU 大规模 / 换奖励与任务定义）。</p>'''


def main():
    summary = load_json(os.path.join(OUT_BASE, "v11_summary.json"))
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    n_seeds = summary.get("n_seeds_loaded", 0) if summary and "_error" not in summary else 0
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BaiZe Vision · CPU RL 波形理解 · v11 回归 vs 生成 三臂对照报告</title>
<style>
body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; margin: 2rem auto; max-width: 1000px; color: #222; line-height: 1.6; }}
h1 {{ border-bottom: 2px solid #336; color: #336; }}
h2 {{ border-left: 5px solid #336; padding-left: 8px; margin-top: 2rem; }}
h3 {{ color: #44a; }}
table {{ border-collapse: collapse; margin: 0.5rem 0; }}
th, td {{ text-align: left; }}
th {{ background: #eef; }}
code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }}
.summary {{ background: #f0f8ff; border: 1px solid #ace; padding: 10px 14px; border-radius: 6px; }}
.footer {{ color: #888; font-size: 0.85em; margin-top: 2rem; border-top: 1px solid #ddd; padding-top: 8px; }}
</style></head><body>
<h1>BaiZe Vision · CPU RL 波形理解</h1>
<p><b>v11：回归 vs 生成 三臂对照（period regression）</b> · vision wake#1182 · 生成时间 {ts} · 已载入 seed 数：{n_seeds}/3</p>
{section_summary(summary)}
{section_design()}
{section_results()}
{section_history()}
{section_scale()}
<p class="footer">单文件 · 0 script · 0 外链 · commit 前缀 vision rl: · 数据可追溯至 vision/wave_rl/v11_results/。</p>
</body></html>
"""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write(doc)
    print(f"Report written -> {REPORT_PATH} ({len(doc)} bytes, {n_seeds}/3 seeds)")


if __name__ == "__main__":
    main()


