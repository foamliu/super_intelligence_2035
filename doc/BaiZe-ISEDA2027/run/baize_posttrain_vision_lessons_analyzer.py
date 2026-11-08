#!/usr/bin/env python3
"""baize_posttrain_vision_lessons_analyzer.py
R57: Vision Line GRPO Failure Lessons -> BaiZe RL Risk Mitigation Playbook.

Cross-references the vision line CPU GRPO failure experience (v1-v4,
EXPERIMENTS_VISION.md Section 21-22) with BaiZe planned RL reward arms (R0-R4).

Usage:
  python3 baize_posttrain_vision_lessons_analyzer.py              # Full: JSON + HTML
  python3 baize_posttrain_vision_lessons_analyzer.py --json-only  # JSON only
  python3 baize_posttrain_vision_lessons_analyzer.py --html-only  # HTML only
  python3 baize_posttrain_vision_lessons_analyzer.py --dry-run    # Print to stdout

Pure Python 3.8+, zero third-party dependencies.
"""
import json, os, sys
from datetime import datetime

VISION_GRPO_TIMELINE = [
    {"version":"v1","method":"GRPO discrete 5-tier","baseline":"post-SFT 9.2%","treatment":"post-GRPO 6.2%","delta":-3.0,"verdict":"WORSE","loss":"~0","G":4},
    {"version":"v2","method":"GRPO continuous (flip)","baseline":"B=6.7%","treatment":"C=11.1%","delta":4.4,"verdict":"NOT SIGNIFICANT (p=0.625)","loss":"~0","G":4},
    {"version":"v3","method":"GRPO continuous (40 steps)","baseline":"B=34.0%","treatment":"C=25.0%","delta":-9.0,"verdict":"WORSE (3rd negative)","loss":"~0.000038","G":8},
    {"version":"v4","method":"RFT/STaR","baseline":"B=34.0%","treatment":"C=34.0%","delta":0.0,"verdict":"NO CHANGE","loss":"CE stable","G":4},
]

VISION_DIAG = {
    "gs4_std0_pct": 78.7, "gs4_total": 94, "gs4_all0_pct": 0.0,
    "gs4_allpos_pct": 20.2, "gs4_stdpos_pct": 21.3, "gs4_judgment": "PARTIAL",
    "gs8_std0_pct": 73.0, "gs8_total": 100, "gs8_stdpos_pct": 27.0,
    "gs8_judgment": "PARTIAL", "gs4_to_gs8_delta": -5.7,
    "key_finding": "all-zero impossible (fail=-0.5). Real problem: all-same-tier=78.7% -> advantage=0 -> zero gradient",
    "per_target": {
        "rise_time": {"n":26,"std0":100.0,"mean":-0.5,"dx":"CAPABILITY GAP (needs SFT)"},
        "duty_cycle": {"n":22,"std0":90.9,"mean":-0.405,"dx":"NEAR NO-SIGNAL"},
        "amplitude": {"n":24,"std0":87.5,"mean":0.429,"dx":"NEAR SATURATION"},
        "period": {"n":22,"std0":31.8,"mean":0.457,"dx":"GRPO-LEARNABLE (68% signal)"},
    },
}

BAIZE_ARMS = {
    "R0": {"name":"Skeleton","risk":"LOW","score":2,"analog":"N/A","type":"binary",
           "factors":["No sandbox -> not a training arm"],"mit":["Smoke only"]},
    "R1": {"name":"Binary pass/fail","risk":"CRITICAL","score":9,"analog":"v1 (EXACT match)","type":"binary",
           "factors":["std=0 collapse expected","36% base G=8: P(mixed)=97.2% (vs vision 27.6%)","No partial credit"],
           "mit":["DO NOT start with R1","Monitor std=0>50%->switch R2","Use Dr.GRPO","Filter 10-90% tasks"]},
    "R2": {"name":"Partial scores","risk":"HIGH","score":6,"analog":"v3 continuous (partial match)","type":"partial",
           "factors":["v3 continuous STILL failed (loss~0)","Partial reduces but doesn't eliminate all-same-tier",
                      "Assertion ratio still discretized","ImportError=0.0"],
           "mit":["START with R2","Monitor std=0>60%->add noise","Use float ratio","Consider Dr.GRPO"]},
    "R3": {"name":"R2+tool penalty","risk":"MEDIUM","score":5,"analog":"v3+cost (no direct)","type":"partial+penalty",
           "factors":["Penalty adds variance but may cause tool avoidance"],
           "mit":["Small penalty 0.01/call","Monitor tool freq"]},
    "R4": {"name":"R3+API legality","risk":"MEDIUM","score":5,"analog":"v3+API (no direct)","type":"partial+penalty+legal",
           "factors":["API penalty may penalize exploration","Risk: only safe APIs -> reduced capability"],
           "mit":["Soft penalty","Monitor API diversity"]},
}

RISK_MAPPINGS = [
    {"vf":"std=0=78.7% -> zero gradient","ve":"74/94 groups all-same-tier",
     "br":"R1 binary high risk; R2 partial lower but significant","sev":"CRITICAL",
     "thr":"std=0>60% for 3 steps -> switch arm or increase G"},
    {"vf":"Continuous reward (v3) did NOT fix std=0","ve":"v3 C=25%<B=34%, loss~0",
     "br":"R2 partial may not provide enough variance","sev":"HIGH",
     "thr":"loss<1e-4 for 5 steps -> switch to Dr.GRPO"},
    {"vf":"Capability gap (rise_time 100% all wrong)","ve":"26/26 groups all -0.5",
     "br":"Some EDA tasks 100% failure -> wasted RL budget","sev":"HIGH",
     "thr":"Exclude scenarios <5% or >95% pass after baseline"},
    {"vf":"G 4->8 only -5.7pp std=0 (marginal)","ve":"78.7%->73.0%",
     "br":"G=8 may not be enough; G=16 diminishing","sev":"MEDIUM",
     "thr":"std=0>70% at G=8 -> try G=12"},
    {"vf":"RFT (v4) = no improvement","ve":"C=34%=B=34%, 67% collect -> no new info",
     "br":"Fallback to RFT may also fail","sev":"LOW",
     "thr":"Do NOT auto-fallback to RFT; report and wait"},
    {"vf":"avgR high variance but loss~0","ve":"-0.5->0.398->0.033",
     "br":"Reward variance without gradient = not updating","sev":"HIGH",
     "thr":"avgR std>0.3 AND loss<1e-4 -> diagnose std=0"},
    {"vf":"15 steps insufficient","ve":"v2 p=0.50 at 15 steps",
     "br":"Smoke 10 iters shows nothing; need 200+","sev":"MEDIUM",
     "thr":"Evaluate at step 200; if no improvement by 500 -> diagnose"},
    {"vf":"Per-target heterogeneity","ve":"period 68% signal vs rise_time 0%",
     "br":"Some EDA scenarios learnable, others not","sev":"HIGH",
     "thr":"Weight sampling: 2x learnable, 0.5x gap scenarios"},
]

MONITORING = [
    {"metric":"std=0 rate","vr":"78.7%","red":">70% for 3 steps","act":"Switch arm or increase G","r36":"R36 P2"},
    {"metric":"Loss value","vr":"~0.000038","red":"<1e-4 for 5 steps","act":"Dr.GRPO or reward noise","r36":"NEW"},
    {"metric":"avgR variance","vr":"-0.5->0.398->0.033","red":"High var+no trend","act":"Reduce LR or increase KL","r36":"NEW"},
    {"metric":"Per-scenario pass","vr":"rise_time 0%, period 68%","red":"0%/100% for 200 steps","act":"Exclude scenario","r36":"NEW"},
    {"metric":"Cheat rate","vr":"N/A","red":">5%","act":"STOP; investigate hacking","r36":"R36 P7"},
    {"metric":"API diversity","vr":"N/A","red":"Decreasing for 200 steps","act":"Reduce tool/API penalty","r36":"NEW"},
]

COMPARISON = [
    {"a":"Base model","v":"Qwen3-VL-2B LoRA","b":"MiniCPM5-2B full"},
    {"a":"Base success","v":"9.2% (post-SFT)","b":"36% (zero-shot)"},
    {"a":"Task","v":"Waveform regression","b":"EDA code gen + tool-use"},
    {"a":"Reward","v":"5-tier->continuous (both failed)","b":"Binary R1->Partial R2->Penalty R3/R4"},
    {"a":"Group size","v":"4->8 (marginal)","b":"8 (config)->12-16 (fallback)"},
    {"a":"Steps","v":"50->40->120","b":"2000 (planned), 10 (smoke)"},
    {"a":"std=0 root","v":"Discrete+9.2%->all-same-tier","b":"Risk: R1+36%->all-0/all-1; R2 mitigates"},
    {"a":"Fallback","v":"GRPO->RFT (also failed)","b":"R2->R3->R4->SFT aug (no RFT)"},
    {"a":"Anti-cheat","v":"None","b":"PreToolUse+cheat rate (red line)"},
    {"a":"Key advantage","v":"--","b":"36%>>9.2% + DAPO + Dr.GRPO option"},
]

def compute_signal(base=0.36, G=8):
    """Estimate P(std>0) for BaiZe vs vision."""
    p0 = (1-base)**G; p1 = base**G; mixed = 1-p0-p1
    vp = 0.092; vG = 4; vm = 1-(1-vp)**vG-vp**vG
    return {"baize_r1_p_mixed": round(mixed,6), "baize_p_all0": round(p0,6),
            "baize_p_all1": round(p1,6), "vision_p_mixed": round(vm,6),
            "ratio": round(mixed/max(vm,1e-10),2)}

def generate_summary():
    sig = compute_signal()
    return {"title":"R57: Vision GRPO Failure -> BaiZe RL Risk",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vision_all_failed": True,
            "vision_root_cause": "std=0=78.7% (discretized reward + low base -> all-same-tier -> zero gradient)",
            "signal": sig,
            "recommendation": ("START with R2 (partial scores), NOT R1. "
                "Monitor std=0 per step. >60% for 3 steps -> Dr.GRPO. "
                ">70% -> increase G to 12. No signal by step 500 -> per-scenario analysis. "
                "DO NOT fallback to RFT. Fall back to SFT augmentation.")}

def generate_html(output_path):
    s = generate_summary(); sig = s["signal"]
    def tr(cells, h=False):
        t = "th" if h else "td"
        return "<tr>"+"".join(f"<{t}>{c}</{t}>" for c in cells)+"</tr>"
    vtl = "".join(tr([v["version"],v["method"],v["baseline"],v["treatment"],
        f'{v["delta"]:+.1f}pp',v["verdict"]]) for v in VISION_GRPO_TIMELINE)
    arms = "".join(tr([k,v["name"],v["risk"],str(v["score"]),v["analog"]])
        for k,v in BAIZE_ARMS.items())
    rm = "".join(tr([r["vf"][:55]+"...",r["br"][:55]+"...",r["sev"],r["thr"]])
        for r in RISK_MAPPINGS)
    mc = "".join(tr([m["metric"],m["vr"],m["red"],m["act"]]) for m in MONITORING)
    cmp = "".join(tr([c["a"],c["v"],c["b"]]) for c in COMPARISON)
    pt = VISION_DIAG["per_target"]
    ptr = "".join(tr([k,str(v["n"]),f'{v["std0"]}%',f'{v["mean"]:.3f}',v["dx"]])
        for k,v in pt.items())
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R57: Vision GRPO 失败教训 -> BaiZe RL 风险缓解手册</title>
<style>
body{{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#1a1a2e;line-height:1.6}}
h1{{color:#c0392b;border-bottom:3px solid #c0392b;padding-bottom:10px}}
h2{{color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:5px;margin-top:30px}}
h3{{color:#34495e;margin-top:20px}}
table{{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px}}
th{{background:#2c3e50;color:white;padding:8px;text-align:left}}
td{{border:1px solid #ddd;padding:6px 8px}}tr:nth-child(even){{background:#f2f2f2}}
.box{{background:white;border-left:4px solid #3498db;padding:15px;margin:15px 0;border-radius:0 5px 5px 0}}
.danger{{background:#f8d7da;border-left:4px solid #dc3545;padding:15px;margin:15px 0;border-radius:0 5px 5px 0}}
.warn{{background:#fff3cd;border-left:4px solid #ffc107;padding:15px;margin:15px 0;border-radius:0 5px 5px 0}}
.rec{{background:#e8f5e9;border:2px solid #4caf50;padding:20px;margin:20px 0;border-radius:8px}}
</style></head><body>
<h1>R57: Vision 线 GRPO 失败教训 -> BaiZe RL 风险缓解手册</h1>
<p><strong>日期</strong>: {s["timestamp"]} | <strong>来源</strong>: EXPERIMENTS_VISION.md Section 21-22 | <strong>零 GPU</strong></p>
<div class="danger"><h3>核心结论</h3>
<p>Vision 线 GRPO <strong>全部 4 轮失败</strong>。根因: <strong>std=0=78.7%</strong>（离散奖励+低base->全同档->零梯度）。
<strong>连续化未解决</strong>（v3 仍 loss~0）。</p>
<p><strong>BaiZe 优势</strong>: 36% base >> 9.2% -> R1 P(signal)={sig["baize_r1_p_mixed"]*100:.1f}% vs vision {sig["vision_p_mixed"]*100:.1f}% = <strong>{sig["ratio"]}x 更多信号</strong>。但 R1 仍有风险，<strong>必须从 R2 起步</strong>。</p></div>
<h2>一、Vision GRPO 失败时间线</h2>
<table><tr><th>版本</th><th>方法</th><th>基线</th><th>实验</th><th>Delta</th><th>结论</th></tr>{vtl}</table>
<h2>二、Advantage 方差诊断</h2>
<table><tr><th>目标</th><th>n</th><th>std=0%</th><th>mean</th><th>诊断</th></tr>{ptr}</table>
<div class="box"><p><strong>关键发现</strong>: {VISION_DIAG["key_finding"]}</p></div>
<h2>三、BaiZe 奖励臂风险评估</h2>
<table><tr><th>臂</th><th>名称</th><th>风险</th><th>分</th><th>Vision对标</th></tr>{arms}</table>
<div class="danger"><p><strong>R1 (Binary) = CRITICAL</strong>: 与 vision v1 完全相同失败模式。P(mixed)={sig["baize_r1_p_mixed"]*100:.1f}%, P(all-0)={sig["baize_p_all0"]*100:.2f}%。不从 R1 起步。</p></div>
<div class="warn"><p><strong>R2 (Partial) = HIGH but recommended start</strong>: vision v3 连续仍失败，但 36% base 提供更多信号。监控 std=0 > 60% -> Dr.GRPO。</p></div>
<h2>四、Vision 失败 -> BaiZe 风险映射</h2>
<table><tr><th>Vision 失败</th><th>BaiZe 风险</th><th>严重度</th><th>预注册阈值</th></tr>{rm}</table>
<h2>五、预注册 RL 监控仪表盘</h2>
<table><tr><th>指标</th><th>Vision 参考</th><th>RED 阈值</th><th>RED 动作</th></tr>{mc}</table>
<h2>六、BaiZe vs Vision 全面对比</h2>
<table><tr><th>维度</th><th>Vision</th><th>BaiZe</th></tr>{cmp}</table>
<h2>七、最终建议</h2>
<div class="rec"><ol>
<li><strong>从 R2 起步</strong>，不从 R1</li>
<li><strong>监控 std=0</strong>: >60%x3步->Dr.GRPO; >70%->G=12</li>
<li><strong>Step 500</strong>: 无改善->per-scenario分析->排除0%/100%场景</li>
<li><strong>不回退 RFT</strong>（vision v4 证明无效）->回退 SFT 增强</li>
<li><strong>诚实报告</strong>: RL 无效=支持「规模非瓶颈」论</li>
</ol></div>
<div class="box"><p><strong>交付物</strong>: baize_posttrain_vision_lessons_analyzer.py + EXPERIMENTS Section R57 + 本HTML（自包含,0script,0外链）</p>
<p><strong>数据溯源</strong>: EXPERIMENTS_VISION.md Section 21-22。vision 诊断数据在 .12（本节点 .17 不可达），使用已记录数值。无伪造。</p></div>
<footer><p style="text-align:center;color:#999;margin-top:30px">R57 BaiZe Stage(ii) {s["timestamp"]} 零 GPU</p></footer>
</body></html>"""
    with open(output_path,"w",encoding="utf-8") as f: f.write(html)
    return len(html)

def main():
    args = sys.argv[1:]
    json_only = "--json-only" in args
    html_only = "--html-only" in args
    dry_run = "--dry-run" in args
    sd = os.path.dirname(os.path.abspath(__file__))
    rd = os.path.join(sd, "..", "reports")
    os.makedirs(rd, exist_ok=True)
    s = generate_summary()
    if dry_run:
        print("="*70)
        print("R57: Vision GRPO Failure -> BaiZe RL Risk Assessment")
        print("="*70)
        for v in VISION_GRPO_TIMELINE:
            print(f"  {v['version']}: {v['treatment']} vs {v['baseline']} -> {v['verdict']}")
        sig = s["signal"]
        print(f"\nBaiZe R1 P(mixed)={sig['baize_r1_p_mixed']*100:.1f}% vs vision {sig['vision_p_mixed']*100:.1f}% = {sig['ratio']}x")
        print(f"\nRecommendation: {s['recommendation'][:100]}...")
        return
    jp = os.path.join(sd, "baize_posttrain_r57_vision_lessons.json")
    hp = os.path.join(rd, "report_posttrain_r57_vision_lessons_rl_risk_zh.html")
    if not html_only:
        out = {"summary": s, "timeline": VISION_GRPO_TIMELINE,
               "diagnosis": VISION_DIAG, "arms": BAIZE_ARMS,
               "risk_mappings": RISK_MAPPINGS, "monitoring": MONITORING,
               "comparison": COMPARISON}
        with open(jp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"[R57] JSON: {jp} ({os.path.getsize(jp)} bytes)")
    if not json_only:
        hs = generate_html(hp)
        print(f"[R57] HTML: {hp} ({hs} bytes)")
    if not json_only and not html_only:
        print("[R57] Done.")

if __name__ == "__main__":
    main()

