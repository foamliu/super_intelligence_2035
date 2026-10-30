#!/usr/bin/env python3
"""Generate the daily Chinese HTML report for the Design-Flow Benchmark.

Usage: python3 gen_daily_report.py [--date MM_DD]
Default date = today (local). Writes to <repo>/docs/reports/report_MM_DD.html.

Per 即时令 VII: main case table is per-case rows with columns
  task_id | trace 来源 | 解决问题 | 任务说明(prompt) | 交付件要求 | test 思路 | test 语言 | pi 结果
Aggregate KPI summary kept above the per-case table.
"""
import json, os, sys, glob, datetime, html

REPO = os.environ.get("EDA_FLOW_BENCH_ROOT") or "/nasdata/app.e0031982/code/EDA-Flow-Bench"
REPO = os.path.abspath(REPO)
BENCH_DIR = os.path.join(REPO, "benchmarks", "EDA-Eval-DesignFlow")
BENCH_FILE = os.path.join(BENCH_DIR, "EDA-Eval-DesignFlow.jsonl")  # single merged file (即时令 VIII)
# 日报输出到 super_intelligence_2035/doc/ZhuLong_DAC2027/reports/（与 zhulong 报告统一管理）
WS_REPO_ROOT = os.environ.get("SUPER_INTELLIGENCE_2035_ROOT") or "/nasdata/app.e0031982/code/super_intelligence_2035"
REPORT_DIR = os.path.join(WS_REPO_ROOT, "doc", "ZhuLong_DAC2027", "reports")
PI_STATUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pi_debug_status.jsonl")

# three-mouth numbers (from .75 落盘实测值, 运维增补II)
THREE_MOUTH = {"hosts": 698, "users": 2850, "session_files": 52698, "ic_eda_hits": 24085}

# trace provenance for the known proper design_flow cases (from rtl_design_flow_case_design.md)
TRACE_SRC = {
    "EDA-Eval-DesignFlow-Digital-010": "t0002948/1789900011859_zpx23 (std_intmac 乘加树+饱和)",
    "EDA-Eval-DesignFlow-Digital-021": "klhu/1792224347250_fww0m (PrimeTime 负 slack 提取)",
    "EDA-Eval-DesignFlow-Digital-022": "t0002948/1792133892937_i2dlp + 1791602575997_53vw2 (DC DFT 失败诊断)",
    "EDA-Eval-DesignFlow-Digital-023": "t0002948/1792400029503_0na23 (VCS makefile 参数化)",
    "EDA-Eval-DesignFlow-Verification-001": "ukkn7/8adf72139dee @ hfeg0plg91 (ERC_AI_CHECK pipeline 子section 过滤 + virtuoso→aether flow 改写)",
    "EDA-Eval-DesignFlow-Characterization-001": "9knot/vincelu @ hfeg0plg49 (SiliconSmart drgqx 5 库表征 .tcl/.inst 多类 error 修复)",
    "EDA-Eval-DesignFlow-PDKQA-001": "x4b0p/xinqiaoz @ hfeg0pkn004 (PDK QA DRC 框架 Windows→Linux 迁移, Calibre VCO aok/aoi autoswitch bug 假 MGC_HOME 绕过)",
    "EDA-Eval-DesignFlow-Backannot-001": "82ybr/haoyut @ hfeg0plg49 (PrimeTime read_parasitics 寄生反标失败诊断·DRAM STA signoff, 跨 EDA 厂家 hierarchy 策略差异 StarRC merge vs Cadence SI)",
}


def today_mmdd():
    return datetime.date.today().strftime("%m_%d")


def detect_test_lang(t):
    if not t:
        return "—"
    if "procedure(check" in t or t.lstrip().startswith("procedure("):
        return "SKILL"
    if "proc check {" in t or t.lstrip().startswith("proc "):
        return "Tcl"
    if "def check" in t:
        return "Python"
    return "—"


def is_two_param(t):
    return ("def check(deliverable" in t or "procedure(check(deliverable" in t
            or "proc check {deliverable" in t)


def load_cases():
    cases = []
    if not os.path.exists(BENCH_FILE):
        return cases
    for line in open(BENCH_FILE):
        line = line.strip()
        if not line:
            continue
        try:
            cases.append(json.loads(line))
        except Exception:
            pass
    return cases


def load_pi_status():
    last = {}
    if os.path.exists(PI_STATUS):
        for line in open(PI_STATUS):
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    tid = r.get("task_id", "")
                    if tid:
                        last[tid] = r
                except Exception:
                    pass
    return last


def esc(s):
    return html.escape(str(s))


def trace_source(c):
    tid = c.get("task_id", "")
    if tid in TRACE_SRC:
        return TRACE_SRC[tid]
    if c.get("legacy"):
        return "synthesized (legacy scripting 口径)"
    md = c.get("metadata", {}) or {}
    src = md.get("trace_source") or md.get("legacy_source_file")
    if src:
        if isinstance(src, dict):
            host = src.get("host", "?")
            sf = src.get("session_file", "")
            summ = src.get("real_task_summary", "")
            return f"{sf} @ {host} ({summ})" if summ else f"{sf} @ {host}"
        return src
    return "synthesized"


def solve_problem(c):
    md = c.get("metadata", {}) or {}
    return md.get("task_name") or md.get("scenario") or md.get("direction") or "—"


def prompt_summary(c):
    p = c.get("prompt", "") or ""
    p = " ".join(p.split())
    return (p[:90] + "…") if len(p) > 90 else p


def deliverable_req(c):
    ep = c.get("entry_point", "") or "—"
    md = c.get("metadata", {}) or {}
    arts = md.get("artifacts") or md.get("expected_artifacts") or []
    if arts:
        return f"{ep} 内含 {', '.join(map(str, arts))}"
    return ep


def test_approach(c):
    t = c.get("test", "") or ""
    if c.get("legacy"):
        return "校验函数返回值 (scripting 单参 check(candidate))"
    if is_two_param(t):
        return "校验交付件 (双参 check(deliverable, workdir): 解 zip + 断言内含文件 + 内容达标)"
    return "—"


def main():
    mmdd = sys.argv[1] if len(sys.argv) > 1 else today_mmdd()
    cases = load_cases()
    pi_by_tid = load_pi_status()

    legacy_n = sum(1 for c in cases if c.get("legacy"))
    proper_n = len(cases) - legacy_n

    # domain distribution
    by_domain = {}
    for c in cases:
        dom = (c.get("metadata", {}) or {}).get("domain", "未分类")
        by_domain[dom] = by_domain.get(dom, 0) + 1

    # pi debug tallies (dedup by task_id, last row)
    pi_tally = {"PASS": 0, "FAIL": 0, "draft": 0, "未跑": 0}
    for c in cases:
        tid = c.get("task_id", "")
        st = pi_by_tid.get(tid, {}).get("status", "未跑")
        pi_tally[st] = pi_tally.get(st, 0) + 1

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # per-case rows: real-trace (proper) first, legacy after
    cases_sorted = sorted(cases, key=lambda c: (1 if c.get("legacy") else 0, c.get("task_id", "")))

    rows_html = []
    for c in cases_sorted:
        tid = c.get("task_id", "")
        pi_st = pi_by_tid.get(tid, {}).get("status", "未跑")
        pclass = {"PASS": "pass", "FAIL": "fail"}.get(pi_st, "draft")
        rows_html.append(
            "<tr><td>{tid}</td><td>{ts}</td><td>{sp}</td><td>{ps}</td><td>{dr}</td><td>{ta}</td><td>{tl}</td><td><span class='tag {pc}'>{pst}</span></td></tr>".format(
                tid=esc(tid),
                ts=esc(trace_source(c)),
                sp=esc(solve_problem(c)),
                ps=esc(prompt_summary(c)),
                dr=esc(deliverable_req(c)),
                ta=esc(test_approach(c)),
                tl=esc(detect_test_lang(c.get("test", ""))),
                pc=pclass, pst=esc(pi_st),
            )
        )
    table_rows = "\n".join(rows_html) or '<tr><td colspan="8">(无用例)</td></tr>'

    domain_dist = " · ".join(f"{esc(k)}: {v}" for k, v in sorted(by_domain.items())) or "(无)"

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>设计流 Benchmark 日报 report_{mmdd}</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:0;background:#f5f7fa;color:#222;line-height:1.6}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px}}
h1{{font-size:1.5rem;border-bottom:3px solid #2c7be5;padding-bottom:8px}}
h2{{font-size:1.15rem;margin-top:28px;color:#2c7be5;border-left:4px solid #2c7be5;padding-left:10px}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}
.kpi{{flex:1;min-width:140px;background:#fff;border:1px solid #e3e8ef;border-radius:8px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
.kpi .n{{font-size:1.6rem;font-weight:700;color:#2c7be5}}
.kpi .l{{font-size:.8rem;color:#666}}
table{{border-collapse:collapse;width:100%;background:#fff;margin:8px 0;font-size:.8rem}}
th,td{{border:1px solid #e3e8ef;padding:6px 8px;text-align:left;vertical-align:top}}
th{{background:#f0f4f8;white-space:nowrap}}
td{{word-break:break-word}}
.tag{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.75rem}}
.pass{{background:#d4edda;color:#155724}}
.fail{{background:#f8d7da;color:#721c24}}
.draft{{background:#fff3cd;color:#856404}}
.legacy{{background:#eef2f7;color:#555}}
.note{{background:#fffbe6;border-left:3px solid #f0ad4e;padding:10px 14px;margin:12px 0;border-radius:4px}}
footer{{margin-top:30px;color:#999;font-size:.75rem;text-align:center}}
</style></head><body><div class="wrap">
<h1>设计流 Benchmark 日报 · {mmdd}</h1>
<p><span class="tag pass">多机扩样层 v0.50 已交付</span> <span class="tag legacy">即时令 VII/VIII 整改：单一 jsonl + 设计流契约</span> <span style="color:#999">生成时间 {now}</span></p>

<h2>一、三口径数字（多机版，.75 落盘实测值）</h2>
<div class="kpis">
<div class="kpi"><div class="n">{THREE_MOUTH['hosts']}</div><div class="l">目标机数</div></div>
<div class="kpi"><div class="n">{THREE_MOUTH['users']}</div><div class="l">用户数（home 有 .cline/data/sessions）</div></div>
<div class="kpi"><div class="n">{THREE_MOUTH['session_files']:,}</div><div class="l">会话文件数 (*.json)</div></div>
<div class="kpi"><div class="n">{THREE_MOUTH['ic_eda_hits']:,}</div><div class="l">IC/EDA 命中会话</div></div>
</div>
<div class="note">数据来源：沈佳成 698 机 SSH 扫描结果（落盘 .75 <code>/home/t0002965/log/ssh_eda_search_20261028_174426/</code>）。11 类分布：layout_aether 14534 · layout_virtuoso 2496 · schematic_netlist 2362 · physical_verify 1295 · analog_context 1167 · spice_sim 1027 · pnr_signoff 503 · waveform 368 · logic_synth 167 · eda_other 159 · skipper 7。</div>

<h2>二、评测用例盘点（benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl）</h2>
<div class="kpis">
<div class="kpi"><div class="n">{len(cases)}</div><div class="l">累计用例数</div></div>
<div class="kpi"><div class="n">{proper_n}</div><div class="l">设计流口径（proper design_flow）</div></div>
<div class="kpi"><div class="n">{legacy_n}</div><div class="l">legacy scripting（已标记 legacy:true）</div></div>
<div class="kpi"><div class="n">1</div><div class="l">jsonl 文件数（已合并）</div></div>
</div>
<p><b>按 domain 分布：</b>{domain_dist}</p>
<div class="note">即时令 VIII 已将原 15 个按工具分文件合并为单一 <code>EDA-Eval-DesignFlow.jsonl</code>；scripting 口径用例标记 <code>legacy:true</code> 保留存量，不再追加。新建用例只往此文件追加，按设计流契约（mode=design_flow / entry_point=outputs/submit.zip / 双参 check(deliverable, workdir) / 无 lang·host）。</div>

<h2>三、用例清单（每行一个 Case · 真实 trace 在上，legacy 在下）</h2>
<table><tr><th>task_id</th><th>trace 来源</th><th>解决的问题</th><th>任务说明(prompt)</th><th>交付件要求</th><th>test 思路</th><th>test 语言</th><th>pi 结果</th></tr>
{table_rows}
</table>

<h2>四、pi 被测调试结果</h2>
<div class="kpis">
<div class="kpi"><div class="n" style="color:#155724">{pi_tally['PASS']}</div><div class="l">PASS</div></div>
<div class="kpi"><div class="n" style="color:#721c24">{pi_tally['FAIL']}</div><div class="l">FAIL</div></div>
<div class="kpi"><div class="n" style="color:#856404">{pi_tally['draft']}</div><div class="l">draft</div></div>
<div class="kpi"><div class="n" style="color:#888">{pi_tally['未跑']}</div><div class="l">未跑</div></div>
</div>
<div class="note">被测 agent = <code>pi</code> 1.4.0（provider cxmt / deepseek-v4-pro-cloud），已配 <code>eda_flow</code> MCP（127.0.0.1:18891）。pi 调用链 open_session→run_code→close_session 已验证连通。</div>

<h2>五、阻塞 / 下一步</h2>
<ul>
<li>即时令 VII/VIII 整改完成：合并为单一 jsonl + 日报改 per-case 表格。</li>
<li>下一步：从 698 机真实 session（增补 IV SSH 免密已通）抓真实 trace，按设计流契约建新用例（追加到 EDA-Eval-DesignFlow.jsonl）。</li>
<li>pyAether (aether host) run_code 初始化超时，layout_aether 类真实建图用例待 aether 沙盒稳定。</li>
<li>每新建用例用 pi 实跑验证 → 更新 pi_debug_status.jsonl。</li>
</ul>

<footer>Design-Flow Benchmark · 自动生成 by gen_daily_report.py · 三口径数字引用 .75 落盘实测值</footer>
</div></body></html>"""

    os.makedirs(REPORT_DIR, exist_ok=True)
    out = os.path.join(REPORT_DIR, f"report_benchmark_{mmdd}.html")
    with open(out, "w") as f:
        f.write(doc)
    print("wrote", out, f"({len(cases)} cases, {proper_n} proper, {legacy_n} legacy)")


if __name__ == "__main__":
    main()
