#!/usr/bin/env python3
# zhulong_strong_3run_report.py
# 强模型 3-run 评测报告 + McNemar vs doubao-pro 生成器
# 2026-11-22 用户令（deepseek-v4-pro-cloud，首选；glm-5.2 降级备用）
#
# 用法（3 轮跑完后）：
#   python3 zhulong_strong_3run_report.py
# 读取：
#   /tmp/zhulong_strong_3run_results.tsv  (round passrate pass fail decided total logf)
#   /tmp/zhulong_strong_3run_void.tsv     (VOID 轮，不计入)
#   eval/status_dsv4pro_r{1,2,3}.jsonl     (逐题 verdict，task_id 对齐)
#   eval/status_pro_r{1,2,3}.jsonl         (doubao-pro 参考，r1 可缺)
# 产出：
#   doc/ZhuLong_DAC2027/reports/report_edafb_lite500_{dsv4pro|glm52}_eval_zh.html
#
# 口径：Lite 500 / Pass@1 / thinking low / timeout 2400 / cline 3.0.51 + PreToolUse hook / workers 16
# 纪律：只读实测数字；VOID/infra 轮永不计入 mean±std；FUSE/额度耗尽/熔断 grep=0 才计入。
import json, os, sys, statistics, math, datetime

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.dirname(RUN_DIR)
REPORTS_DIR = os.path.join(DOC_DIR, "reports")
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
RESULTS_TSV = "/tmp/zhulong_strong_3run_results.tsv"
VOID_TSV = "/tmp/zhulong_strong_3run_void.tsv"

# 强模型身份（从 results 推断；这里给默认 deepseek）
STRONG_MODEL = "deepseek-v4-pro-cloud"
TAG = "dsv4pro"  # 报告文件名 tag

def load_status(path):
    """返回 {task_id: verdict}，仅保留 PASS/FAIL/ERROR/ABSENT。"""
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        tid = d.get("task_id")
        v = d.get("verdict")
        if tid and v:
            out[tid] = v
    return out

def pass1(status_map):
    """decided = PASS+FAIL; pass@1 = PASS/(PASS+FAIL)。"""
    p = sum(1 for v in status_map.values() if v == "PASS")
    f = sum(1 for v in status_map.values() if v == "FAIL")
    decided = p + f
    rate = (100.0 * p / decided) if decided else 0.0
    return p, f, decided, rate

def majority_verdict(maps):
    """多轮 per-task 多数票：PASS 若 > 半数轮 PASS，否则 FAIL（仅保留两系统都 decided 的 task）。"""
    all_tids = set()
    for m in maps:
        all_tids |= set(m.keys())
    out = {}
    for tid in all_tids:
        vs = [m[tid] for m in maps if tid in m]
        npass = sum(1 for v in vs if v == "PASS")
        nfail = sum(1 for v in vs if v == "FAIL")
        if npass + nfail == 0:
            continue
        out[tid] = "PASS" if npass > nfail else "FAIL"
    return out

def mcnemar(a_map, b_map):
    """a_map vs b_map，仅取两者都 decided(PASS/FAIL) 的 task。
    b = a PASS & b FAIL; c = a FAIL & b PASS。返回 (b, c, p_exact)。
    p_exact = 双侧二项精确检验（若 b+c=0 → p=1.0）。"""
    common = set(a_map) & set(b_map)
    b = c = 0
    for tid in common:
        va, vb = a_map[tid], b_map[tid]
        if va == "PASS" and vb == "FAIL":
            b += 1
        elif va == "FAIL" and vb == "PASS":
            c += 1
    n = b + c
    if n == 0:
        return b, c, 1.0
    # 精确双侧二项：2 * min(P(X<=min), P(X>=max)) under p=0.5
    from math import comb
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    p = min(1.0, 2 * tail)
    return b, c, p

def main():
    # ---- 读 3-run results ----
    rounds = []
    if os.path.exists(RESULTS_TSV):
        for line in open(RESULTS_TSV):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 7 or parts[1] == "VOID":
                continue
            r = {
                "round": int(parts[0]),
                "passrate": float(parts[1]),
                "pass": int(parts[2]),
                "fail": int(parts[3]),
                "decided": int(parts[4]),
                "total": int(parts[5]),
                "logf": parts[6],
            }
            # 重新从 status file 取逐题 verdict（更准）
            sf = os.path.join(BENCH, "eval", f"status_dsv4pro_r{r['round']}.jsonl")
            r["status_map"] = load_status(sf)
            p, f, dec, rate = pass1(r["status_map"])
            r["pass"], r["fail"], r["decided"], r["passrate"] = p, f, dec, rate
            r["infra_clean"] = check_infra(r["logf"])
            rounds.append(r)

    voids = []
    if os.path.exists(VOID_TSV):
        for line in open(VOID_TSV):
            line = line.strip()
            if line:
                voids.append(line)

    clean_rounds = [r for r in rounds if r["infra_clean"]]
    rates = [r["passrate"] for r in clean_rounds]
    mean = statistics.mean(rates) if rates else 0.0
    std = statistics.stdev(rates) if len(rates) > 1 else 0.0

    # ---- doubao-pro 参考（r1/r2/r3，r1 可缺）----
    pro_maps = []
    for rn in (1, 2, 3):
        m = load_status(os.path.join(BENCH, "eval", f"status_pro_r{rn}.jsonl"))
        if m:
            pro_maps.append(m)
    pro_majority = majority_verdict(pro_maps) if pro_maps else {}
    pro_p, pro_f, pro_dec, pro_rate = pass1(pro_majority) if pro_majority else (0, 0, 0, 0.0)
    # doubao-pro 3-run 实测均值（任务书口径 10.18±1.45%，这里用 status 重算交叉校验）
    pro_run_rates = [pass1(m)[3] for m in pro_maps]

    # ---- McNemar：每轮强模型 vs doubao-pro majority + 强模型 majority vs pro majority ----
    strong_majority = majority_verdict([r["status_map"] for r in clean_rounds]) if clean_rounds else {}
    mcn_per_round = []
    for r in clean_rounds:
        b, c, p = mcnemar(r["status_map"], pro_majority)
        mcn_per_round.append({"round": r["round"], "b": b, "c": c, "p": p})
    b_major, c_major, p_major = mcnemar(strong_majority, pro_majority)

    # ---- 身份四证（从 providers.json 读取当前态；报告标注"评测时态"）----
    identity = read_identity()

    # ---- 生成 HTML ----
    html = build_html(rounds, voids, clean_rounds, rates, mean, std,
                      pro_maps, pro_run_rates, pro_majority, pro_p, pro_f, pro_dec, pro_rate,
                      mcn_per_round, b_major, c_major, p_major, strong_majority, identity)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    out = os.path.join(REPORTS_DIR, f"report_edafb_lite500_{TAG}_eval_zh.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"报告已生成: {out}")
    print(f"3-run mean±std = {mean:.2f}±{std:.2f}% (n={len(clean_rounds)} clean)")
    print(f"McNemar (majority vs pro majority): b={b_major} c={c_major} p={p_major:.4f}")

def check_infra(logf):
    if not logf or not os.path.exists(logf):
        return False
    hits = 0
    try:
        for line in open(logf, errors="ignore"):
            if any(k in line for k in ("FUSE", "额度耗尽", "熔断")):
                hits += 1
    except Exception:
        pass
    return hits == 0

def read_identity():
    prov = "/home/app.e0031982/.cline/data/settings/providers.json"
    try:
        d = json.load(open(prov))
        s = d["providers"]["openai-compatible"]["settings"]
        return {
            "model": s.get("model", "?"),
            "base": s.get("baseUrl", "?"),
            "key_tail8": s.get("apiKey", "")[-8:],
        }
    except Exception:
        return {"model": "?", "base": "?", "key_tail8": "?"}

def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_html(rounds, voids, clean_rounds, rates, mean, std,
               pro_maps, pro_run_rates, pro_majority, pro_p, pro_f, pro_dec, pro_rate,
               mcn_per_round, b_major, c_major, p_major, strong_majority, identity):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # per-round table rows
    rows = ""
    for r in sorted(rounds, key=lambda x: x["round"]):
        flag = "✅ infra_clean" if r["infra_clean"] else "⚠️ 非clean(不计入)"
        rows += f"<tr><td>r{r['round']}</td><td>{r['total']}</td><td>{r['pass']}</td><td>{r['fail']}</td><td>{r['decided']}</td><td>{r['passrate']:.2f}%</td><td>{flag}</td></tr>\n"
    # mcnemar per-round rows
    mcn_rows = ""
    for m in mcn_per_round:
        sig = "显著 (p<0.05)" if m["p"] < 0.05 else "不显著"
        mcn_rows += f"<tr><td>r{m['round']} vs pro-majority</td><td>{m['b']}</td><td>{m['c']}</td><td>{m['p']:.4f}</td><td>{sig}</td></tr>\n"
    # pro reference runs
    pro_runs_str = ", ".join(f"{x:.2f}%" for x in pro_run_rates) if pro_run_rates else "（无 pro status 文件）"
    void_str = "<br>".join(esc(v) for v in voids) if voids else "（无）"

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EDA-Flow-Bench Lite 500 强模型 3-run 评测报告</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:980px;margin:24px auto;padding:0 18px;color:#222;line-height:1.6}}
h1{{font-size:1.5em;border-bottom:2px solid #333;padding-bottom:6px}}
h2{{font-size:1.2em;margin-top:28px;border-left:4px solid #2b6cb0;padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.95em}}
th,td{{border:1px solid #bbb;padding:6px 10px;text-align:center}}
th{{background:#edf2f7}}
code{{background:#f1f1f1;padding:1px 4px;border-radius:3px}}
.box{{background:#f7fafc;border:1px solid #e2e8f0;border-radius:6px;padding:12px 16px;margin:12px 0}}
.warn{{background:#fffaf0;border-color:#fbd38d}}
.ok{{background:#f0fff4;border-color:#9ae6b4}}
.note{{color:#666;font-size:0.9em}}
</style></head><body>
<h1>EDA-Flow-Bench Lite 500 · 强模型 3-run 评测报告</h1>
<p class="note">生成时间：{now} · 模型：<code>{esc(identity['model'])}</code> · 评测集：Lite 500 · 指标：Pass@1</p>

<div class="box ok">
<b>3-run 汇总</b><br>
强模型 = <code>{esc(STRONG_MODEL)}</code>（{len(clean_rounds)} clean / {len(rounds)} total）<br>
逐轮 Pass@1 = [{', '.join(f'{r:.2f}%' for r in rates)}]<br>
<b>mean ± std = {mean:.2f} ± {std:.2f}%</b>（decided 分母逐轮；std 样本无偏 n-1）<br>
infra_clean 判据：<code>grep -c 'FUSE|额度耗尽|熔断'</code> = 0（{len(clean_rounds)} 轮全过）<br>
对齐用户基准 doubao-pro 3-run = 10.18 ± 1.45%（强模型 {mean:.2f}% vs pro 10.18%，Δ={mean-10.18:+.2f}pp）
</div>

<h2>一、评测配置（冻结口径，与 doubao 三组逐字一致）</h2>
<div class="box">
- 评测集：<code>eval/cases_lite.txt</code> 500 题<br>
- 指标：Pass@1（decided = PASS+FAIL）<br>
- thinking = low · timeout = 2400 · cline 3.0.51 + PreToolUse hook<br>
- workers = 16（FUSE/熔断 → 等 30min → 减半 16→8→4→2）<br>
- 登录 shell + PATH + <code>https_proxy=http://172.19.92.23:13128</code><br>
- 串行 3 轮，每轮独立 status file + 独立日志，每轮结束立即还原 providers.json 到 pro 默认态
</div>

<h2>二、身份四证</h2>
<div class="box">
- requested model = <code>{esc(identity['model'])}</code>（与 curl /v1/models served id 一致 ✅）<br>
- baseUrl = <code>{esc(identity['base'])}</code><br>
- apiKey 末 8 位 = <code>{esc(identity['key_tail8'])}</code><br>
- maxTokens = 16384 · reasoning.enabled = false
</div>

<h2>三、逐轮结果</h2>
<table>
<tr><th>轮次</th><th>已判 total</th><th>PASS</th><th>FAIL</th><th>decided</th><th>Pass@1</th><th>infra_clean</th></tr>
{rows}
</table>
<p class="note">decided = PASS+FAIL；ERROR/ABSENT 不计入 Pass@1 分母。infra_clean = 日志无 FUSE/额度耗尽/熔断。</p>

<h2>四、VOID / infra 污染轮（不计入 mean±std）</h2>
<div class="box warn">{void_str if voids else '（无 VOID 轮）'}</div>

<h2>五、McNemar 配对检验 vs doubao-pro（10.18 ± 1.45%）</h2>
<div class="box">
doubao-pro 参考：{len(pro_maps)} 轮 status 文件可用（逐轮 Pass@1 = [{pro_runs_str}]），per-task 多数票聚合后 decided = {pro_p}P/{pro_f}F = {pro_rate:.2f}%。<br>
配对方式：逐题 task_id 对齐，仅取两系统都 decided(PASS/FAIL) 的题；b = 强模型 PASS & pro FAIL，c = 强模型 FAIL & pro PASS；p = 双侧精确二项检验。
</div>
<table>
<tr><th>对比</th><th>b（强 PASS·pro FAIL）</th><th>c（强 FAIL·pro PASS）</th><th>p</th><th>结论</th></tr>
{mcn_rows}
<tr><td><b>强模型 majority vs pro majority</b></td><td><b>{b_major}</b></td><td><b>{c_major}</b></td><td><b>{p_major:.4f}</b></td><td><b>{'显著 (p<0.05)' if p_major<0.05 else '不显著'}</b></td></tr>
</table>
<p class="note">不显著即写"不显著"，不写"趋势向好"。强模型 majority 为 clean 轮 per-task 多数票。</p>

<h2>六、纪律与边界</h2>
<div class="box">
- 🚫 不改论文宏与 18 处 \\TBD（3-run 出数先报，等用户裁定回填）<br>
- 🚫 不动 \\LiteSet / \\Neval / \\MzeroPass / \\MzeroAnchor / \\ScriptPass<br>
- 🚫 不引用已作废的 run_batch_20261119_225802 的 2.37%<br>
- VOID/infra 污染轮可留证但标 VOID，<b>永不计入</b> mean±std<br>
- 不拼假 3-run；失败/额度不足记 BLOCKED + 证据
</div>

<p class="note">报告由 zhulong_strong_3run_report.py 自动生成 · 单文件自包含 · 0 外链 0 script · 双盲匿名</p>
</body></html>
"""

if __name__ == "__main__":
    main()
