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

# three-mouth numbers (from .75 实时重扫 2026-11-03, eda_flow run_commands)
# 旧值错误：users=2850 未去重（scan.tsv users_with_cline 求和，同用户多 host 重复计）；
# session_files=52698 是 files_scanned 求和（所有扫描到的 session, 非命中的）。
# 修正：用每日扫描日志 eda_trace_YYYYMMDD.log（只记 EDA-trace-worthy 命中 session）。
# 10/28 原扫描 summary.tsv：384 去重用户 / 3899 去重命中 session / 24085 命中条目。
# 11/03 最新每日扫描：365 去重用户 / 14444 去重命中 session / 698 hosts。
# 趋势（qualifying sessions）：10/29=14370, 10/30=2641(异常低,可能扫描中断),
# 10/31=13994, 11/01=14047, 11/02=13890, 11/03=14448。
THREE_MOUTH = {
    "hosts": 698,
    "users": 365,          # 去重（从 session 路径 /home/<user>/ 提取, 跨 host 去重）
    "session_files": 14444,  # 去重命中 session（EDA-trace-worthy, 非全部 session）
    "ic_eda_hits": 24085,  # summary.tsv 命中条目数（10/28 原扫描, 含同 session 多 keyword）
    "pool_mc100": 696,     # 候选池 mc>=100 去重 session（11/03 改, 旧 mc>=300=172）
    "pool_users_mc100": 182,  # 候选池去重用户
}

# (trace provenance for every proper case lives in metadata.trace_source — 即时令 XI)


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
    # 即时令 XII: trace 来源列显示用户名（溯源到具体是谁的工作）。
    # 格式: <user>/<session_file> @ <host> (<real_task_summary>)
    # 读 metadata.trace_source.user（新字段名）；旧字段 user_hash 作兼容回退；无则 "—"。
    md = c.get("metadata", {}) or {}
    src = md.get("trace_source")
    if src:
        if isinstance(src, dict):
            host = src.get("host", "?")
            sf = src.get("session_file", "")
            summ = src.get("real_task_summary", "")
            user = src.get("user") or src.get("user_hash") or "—"
            base = f"{sf} @ {host}"
            if summ:
                base = f"{base} ({summ})"
            return f"{user}/{base}"
        return src
    return "—"


def trace_user(c):
    # 即时令 XII: 独立的「用户」列，直接显示原用户名（不 hash），便于一眼溯源。
    md = c.get("metadata", {}) or {}
    src = md.get("trace_source")
    if isinstance(src, dict):
        return src.get("user") or src.get("user_hash") or "—"
    return "—"


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
    # 即时令 XI: test 思路列读 metadata.test_rationale（每条 case 自己的真实验证思路）；
    # 无该字段则 "—"（不再显示写死的废话）。
    md = c.get("metadata", {}) or {}
    tr = md.get("test_rationale")
    if tr:
        return tr
    return "—"


# 21:5x 运维令规则 4：日报 case 表新增三列 k(断言)/k(check)/一致
_CIRCLED = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
            "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳",
            "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚"]


def _k_rationale(c):
    """Count enumerated assertion marks (①..⑳) in test_rationale.
    Returns int (0 if none / no rationale)."""
    md = c.get("metadata", {}) or {}
    tr = md.get("test_rationale") or ""
    return sum(1 for m in _CIRCLED if m in tr)


def _k_check(c):
    """Count independent condition labels in check.py source.
    Handles common labeling conventions across the benchmark:
      - comment labels:  `# ---------- (a) ...` / `# (a) ...`
      - string labels:   `"(a) zip has ..."` ( DummyDeck-style _cond msg)
      - bare labels:     `_cond(results, "a", False, ...)` (CTLESpec-style)
    Returns the count of distinct single-letter labels forming the
    condition set (0 if no labels found)."""
    import re
    src = c.get("test", "") or ""
    labels = set()
    # pattern 1: comment labels  "# ... (x) ..."
    for m in re.finditer(r"^\s*#[^\n]*?\(([a-z])\)", src, re.M):
        labels.add(m.group(1))
    # pattern 2: string labels  '"(x) ...'
    for m in re.finditer(r"\"\(([a-z])\)", src):
        labels.add(m.group(1))
    # pattern 3: bare labels  _cond(results, "x", ...
    for m in re.finditer(r"_cond\([^,]*,\s*\"([a-z])\"", src):
        labels.add(m.group(1))
    if not labels:
        return 0
    # Count the contiguous alphabetic run of condition labels.
    # Some check.py leave the first (a) condition unlabeled (e.g. the
    # zip-existence guard) but label (b)..(n); in that case assume an
    # implicit (a) and add 1 to the run starting at 'b'.
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    n = 0
    if "a" in labels:
        for ch in alphabet:
            if ch in labels:
                n += 1
            else:
                break
    else:
        for ch in alphabet[1:]:
            if ch in labels:
                n += 1
            else:
                break
        if n > 0:
            n += 1  # implicit unlabeled (a)
    return n


def gate_triple(c):
    """Return (k_rationale_str, k_check_str, consistent_str) per 21:5x rule 4."""
    kr = _k_rationale(c)
    kc = _k_check(c)
    krs = str(kr) if kr > 0 else "—"
    kcs = str(kc) if kc > 0 else "—"
    consistent = "✓" if (kr == kc and kc >= 8) else "✗"
    return krs, kcs, consistent


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
        krs, kcs, gcons = gate_triple(c)
        gclass = "pass" if gcons == "✓" else "fail"
        rows_html.append(
            "<tr><td>{tid}</td><td>{usr}</td><td>{ts}</td><td>{sp}</td><td>{ps}</td><td>{dr}</td><td>{ta}</td><td>{tl}</td><td>{krs}</td><td>{kcs}</td><td><span class='tag {gc}'>{gcons}</span></td><td><span class='tag {pc}'>{pst}</span></td></tr>".format(
                tid=esc(tid),
                usr=esc(trace_user(c)),
                ts=esc(trace_source(c)),
                sp=esc(solve_problem(c)),
                ps=esc(prompt_summary(c)),
                dr=esc(deliverable_req(c)),
                ta=esc(test_approach(c)),
                tl=esc(detect_test_lang(c.get("test", ""))),
                krs=esc(krs), kcs=esc(kcs), gcons=esc(gcons), gc=gclass,
                pc=pclass, pst=esc(pi_st),
            )
        )
    table_rows = "\n".join(rows_html) or '<tr><td colspan="12">(无用例)</td></tr>'

    domain_dist = " · ".join(f"{esc(k)}: {v}" for k, v in sorted(by_domain.items())) or "(无)"

    # trace 覆盖率（进度条）：读 designflow/trace_ledger.tsv + summary_stats.json
    cov_html = ""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import trace_ledger
        cov_html = trace_ledger.html_block()
    except Exception as e:
        cov_html = "<p style='color:#999'>trace 台账未就绪（%s）</p>" % esc(e)

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

<h2>一、三口径数字（.75 实时重扫 2026-11-03，eda_flow run_commands 实测）</h2>
<div class="kpis">
<div class="kpi"><div class="n">{THREE_MOUTH['hosts']}</div><div class="l">目标机数（全部有 EDA 命中）</div></div>
<div class="kpi"><div class="n">{THREE_MOUTH['users']}</div><div class="l">去重用户数（跨 host 去重）</div></div>
<div class="kpi"><div class="n">{THREE_MOUTH['session_files']:,}</div><div class="l">去重命中 session（EDA-trace-worthy）</div></div>
<div class="kpi"><div class="n">{THREE_MOUTH['ic_eda_hits']:,}</div><div class="l">命中条目数（10/28 原扫描, 含同 session 多 keyword）</div></div>
</div>
<div class="note">
<b>数据来源</b>：沈佳成 698 机 SSH 扫描（.75 <code>/home/t0002965/log/ssh_eda_search_20261028_174426/</code>）+ 每日扫描日志（<code>eda_trace_YYYYMMDD.log</code>）。<br>
<b>11/03 重算修正</b>（旧值有误）：
<table style="margin-top:6px;font-size:.75rem">
<tr><th>口径</th><th>旧值（错）</th><th>实际值（修正）</th><th>错误原因</th></tr>
<tr><td>用户数</td><td>2850</td><td><b>365</b>（11/03）/ 384（10/28）</td><td>旧值未去重：scan.tsv 各 host users_with_cline 求和，同一用户多 host 登录重复计</td></tr>
<tr><td>session 文件数</td><td>52698</td><td><b>14444</b>（11/03 去重命中）/ 3899（10/28 去重命中）</td><td>旧值是 files_scanned 求和（所有扫描到的 session，非 EDA 命中的）</td></tr>
<tr><td>IC/EDA 命中</td><td>24085</td><td>24085 ✅</td><td>= summary.tsv 行数（命中条目，含同 session 多 keyword）</td></tr>
<tr><td>目标机数</td><td>698</td><td>698 ✅</td><td>698 台全部有 EDA 命中</td></tr>
</table>
<b>每日趋势</b>（qualifying sessions，去重命中 session 数）：10/29=14370 · 10/30=2641（异常低，疑似扫描中断）· 10/31=13994 · 11/01=14047 · 11/02=13890 · <b>11/03=14448</b>。会话数在增长（6 天 +78）。
</div>
<h3>候选池与覆盖率（候选池 = match_count≥100 的去重 session，11/03 调整）</h3>
<div class="kpis">
<div class="kpi"><div class="n">{THREE_MOUTH.get('pool_mc100',696)}</div><div class="l">候选池（mc≥100 去重 session）</div></div>
<div class="kpi"><div class="n">172</div><div class="l">旧候选池（mc≥300, 已弃）</div></div>
<div class="kpi"><div class="n">{THREE_MOUTH.get('pool_users_mc100',182)}</div><div class="l">候选池去重用户</div></div>
<div class="kpi"><div class="n">80/365</div><div class="l">已覆盖用户（21.9%）</div></div>
</div>
<div class="note">
<b>mc = match_count</b> = session 文件里命中 EDA 关键词的<b>行数</b>（grep -icE RE1，一行命中任一关键词计 1）。RE1 含 60+ EDA 关键词：virtuoso/innovus/calibre/spectre/hspice/aether/skipper/waveview/pyAether/dbGet/dbCreate*/schematic/netlist/synthesis/PDK/analog/cmos/... 11/03 已加 <code>rtl</code>。<br>
<b>候选池阈值 mc≥300 → mc≥100</b>（11/03 用户直令）：旧阈值 300 太严（只筛出 172 个"重度 EDA 会话"），把 mc 100-299 的 524 个中等丰富 session 排除了。新阈值 mc≥100 候选池 = <b>696</b> 个去重 session / 182 个去重用户。benchmark 已用 266 个 session，覆盖率 266/696 = <b>38.2%</b>（旧口径 88.4% 是因候选池太小虚高）。<br>
<b>mc 分布</b>（去重 session）：1-9: 1912(49%) · 10-49: 883 · 50-99: 408 · <b>100-299: 524(新纳入)</b> · 300-499: 123 · 500-999: 47 · 1000+: 2
</div>

<h2>二、评测用例盘点（benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl）</h2>
<div class="kpis">
<div class="kpi"><div class="n">{len(cases)}</div><div class="l">累计用例数</div></div>
<div class="kpi"><div class="n">{proper_n}</div><div class="l">设计流口径（proper design_flow）</div></div>
<div class="kpi"><div class="n">{legacy_n}</div><div class="l">legacy scripting（已标记 legacy:true）</div></div>
<div class="kpi"><div class="n">1</div><div class="l">jsonl 文件数（已合并）</div></div>
</div>
<p><b>按 domain 分布：</b>{domain_dist}</p>
<div class="note">即时令 VIII 已将原 15 个按工具分文件合并为单一 <code>EDA-Eval-DesignFlow.jsonl</code>；scripting 口径用例标记 <code>legacy:true</code> 保留存量，不再追加。新建用例只往此文件追加，按设计流契约（mode=design_flow / entry_point=outputs/submit.zip / 双参 check(deliverable, workdir) / 无 lang·host）。</div>

{cov_html}

<h2>三、用例清单（每行一个 Case · 真实 trace 在上，legacy 在下）</h2>
<table><tr><th>task_id</th><th>用户</th><th>trace 来源</th><th>解决的问题</th><th>任务说明(prompt)</th><th>交付件要求</th><th>test 思路</th><th>test 语言</th><th>k(断言)</th><th>k(check)</th><th>一致</th><th>pi 结果</th></tr>
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
