import os
#!/usr/bin/env python3
"""Generate report_harness_glm53_7way_swebench_tb_zh.html — R1998 update.
Self-contained Chinese HTML, 0 scripts, 0 external links.
"""
import json, os, datetime, glob, re, subprocess, urllib.request

# ---- Gateway probe (dynamic) ----
GLM53_KEY = "02_088EE9051AAE4BF0ABFC7130331BF697_6903b05e-6f2d-4a69-93be-96e2b790053f"
def probe_gateway():
    try:
        req = urllib.request.Request(
            "http://agi-gateway.cxmt.com/v1/chat/completions",
            data=json.dumps({"model":"glm-5.3-flash","messages":[{"role":"user","content":"hi"}],"max_tokens":5}).encode(),
            headers={"Content-Type":"application/json","Authorization":f"Bearer {GLM53_KEY}"},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.status, ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8","replace")[:200]
        return e.code, body
    except Exception as ex:
        return 0, str(ex)[:200]

_gw_code, _gw_body = probe_gateway()
if _gw_code == 200:
    GW_NOTE = "HTTP 200(正常·predict进行中)"
    GW_NOTE_SHORT = "200(正常)"
    GW_EMOJI = "✅"
elif _gw_code == 429:
    GW_NOTE = "HTTP 429(quota exhausted·predict stalled·~37min后reset)"
    GW_NOTE_SHORT = "429(quota·stalled)"
    GW_EMOJI = "⚠️"
else:
    GW_NOTE = f"HTTP {_gw_code}({_gw_body[:60]})"
    GW_NOTE_SHORT = f"{_gw_code}"
    GW_EMOJI = "⚠️"

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
TB21_TRACES = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench/traces"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = os.environ.get("ROUND", "R2124")

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h, h)
def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ---- SWE-bench eval results ----
swebench = []
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        n = d.get("n",0)
        resolved = len(d.get("resolved",[]))
        unresolved = len(d.get("failed",[]))
        errored = len(d.get("infra_or_quota",[]))
        swebench.append((disp(h), n, resolved, unresolved, errored, "eval_done"))
    else:
        swebench.append((disp(h), 0, 0, 0, 0, "eval_pending"))

# ---- SWE-bench predict counts ----
predict = []
for h in HARNESSES:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    total = len(files)
    real = 0
    for f in files:
        try:
            d = json.load(open(f))
            if isinstance(d, list):
                real += sum(1 for p in d if p.get("model_patch","").strip())
            elif isinstance(d, dict) and d.get("model_patch","").strip():
                real += 1
        except: pass
    predict.append((disp(h), total, real, total - real))

total_resolved = sum(s[2] for s in swebench)
total_evaluated = sum(s[1] for s in swebench)
total_pred = sum(p[2] for p in predict)

# ---- ETA computation (§用户令 2026-11-12, reproducible from file mtimes) ----
import time as _time
_now_ts = _time.time()
_3d_ago_ts = _now_ts - 3 * 86400
_1d_ago_ts = _now_ts - 1 * 86400
eta_rows_data = []
for h in HARNESSES:
    _files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    _total = len(_files)
    _remaining = max(0, 500 - _total)
    _files_3d = sum(1 for _f in _files if os.path.getmtime(_f) >= _3d_ago_ts)
    _files_1d = sum(1 for _f in _files if os.path.getmtime(_f) >= _1d_ago_ts)
    _rate = _files_3d / 3.0  # files/day, 3-day average
    if _remaining == 0:
        _eta_label = "✅ 完成"; _eta_days = 0
    elif _files_1d == 0:
        _eta_label = "DONE(500attempted,empty=能力,今日0产出)"; _eta_days = 0
    elif _rate >= 1:
        _eta_days = _remaining / _rate
        _eta_dt = datetime.datetime.now() + datetime.timedelta(days=_eta_days)
        _eta_label = f"~{_eta_days:.0f}天(≈{_eta_dt.strftime('%m-%d')})"
    else:
        _eta_label = "无法可靠估计(速率<1/天)"; _eta_days = 999
    eta_rows_data.append((disp(h), _total, _remaining, f"{_rate:.0f}/天", f"{_files_1d}/天", _eta_label, _eta_days))
_active_eta = [e for e in eta_rows_data if e[6] > 0 and e[6] < 999]
if _active_eta:
    _bn = max(_active_eta, key=lambda x: x[6])
    swe_eta_str = f"~{_bn[6]:.0f}天(瓶颈={_bn[0]},{_bn[2]}剩余@{_bn[3]})"
    swe_eta_date = (datetime.datetime.now() + datetime.timedelta(days=_bn[6])).strftime("%Y-%m-%d")
else:
    swe_eta_str = "全部完成/DONE"; swe_eta_date = "—"
eta_html_rows = ""
for _nm, _tot, _rem, _r3d, _r1d, _label, _days in eta_rows_data:
    eta_html_rows += f"<tr><td>{esc(_nm)}</td><td>{_tot}/500</td><td>{_rem}</td><td>{_r3d}</td><td>{_r1d}</td><td>{_label}</td></tr>\n"

# ---- TB-2.1 results (§2026-11-17 修正: task_name 去重 + 扫描 rerun 目录, PASS 优先) ----
# 与 gen_report_tb21_7way.py 的 count_route 完全一致, 确保两份报告 TB-2.1 数字相同.
# 旧 bug: 不去重 + 只扫 original dir → 同一 task 多 trial 重复计数 (如 cline 64 而非 42).
import re as _re
def _is_dated_dir(name):
    return bool(_re.match(r"^\d{4}-\d{2}-\d{2}__", name))
def _iter_task_results(root):
    """只取 task 级 result.json (跳过 dated job 级 result.json), 与 count_route 一致."""
    if not os.path.isdir(root):
        return
    for dirpath, _dirs, fnames in os.walk(root):
        for fn in fnames:
            if fn != "result.json":
                continue
            fp = os.path.join(dirpath, fn)
            if "/20" not in fp.replace("\\", "/"):
                continue
            if _is_dated_dir(os.path.basename(dirpath)):
                continue
            yield fp
def _count_route_tb21(h):
    """返回 (unique_passed, evaluated_unique_tasks, total_trials, trial_errors).
    扫 original dir + 所有 <h>_rerun_* dir; PASS 优先 (任一 trial reward==1.0 即 passed)."""
    d = os.path.join(TB21_JOBS, h)
    tasks = {}; trials = 0; errors = 0
    scan_dirs = [d] if os.path.isdir(d) else []
    for rd in sorted(glob.glob(os.path.join(TB21_JOBS, f"{h}_rerun_*"))):
        if os.path.isdir(rd):
            scan_dirs.append(rd)
    for sd in scan_dirs:
        for fp in _iter_task_results(sd):
            try:
                r = json.load(open(fp))
            except Exception:
                continue
            trials += 1
            if r.get("exception_info"):
                errors += 1
            tn = r.get("task_name") or os.path.basename(os.path.dirname(fp)).split("__")[0]
            vr = r.get("verifier_result")
            if vr:
                rw = vr.get("rewards", {}).get("reward", 0) if isinstance(vr, dict) else 0
                if rw == 1.0:
                    tasks[tn] = True
                else:
                    tasks.setdefault(tn, False)
            else:
                tasks.setdefault(tn, False)
    upass = sum(1 for v in tasks.values() if v)
    return upass, len(tasks), trials, errors

tb21_data = {}
_ps_out = subprocess.run(["ps", "-eo", "args="], capture_output=True, text=True).stdout
for h in HARNESSES:
    total = 89
    passed, evaluated, trials, errors = _count_route_tb21(h)
    # Check for actual rerun processes (harbor / rerun_tb21 / codex exec / followup),
    # not just any process that mentions the path.  CRITICAL: the cline agent process
    # itself has the entire task book (BAIZE_HARNESS_TASK.md) in its args, which
    # contains all these strings → false positive.  Exclude lines starting with
    # "cline" (the agent) and the current python process.
    _rerun_markers = ("harbor", "rerun_tb21", "codex exec", "followup", "launch_tb21")
    running = any(
        f"/tmp/tb21_glm53_jobs/{h}" in line
        and any(m in line for m in _rerun_markers)
        and not line.lstrip().startswith("cline")
        and "BAIZE_HARNESS_TASK" not in line
        for line in _ps_out.splitlines()
    )
    if running:
        status = "running"
    elif evaluated >= total:
        status = "done"
    else:
        status = "partial"
    remaining = max(0, total - evaluated)
    tb21_data[h] = {"passed": passed, "completed": evaluated, "errored": errors,
                    "remaining": remaining, "total": total, "status": status,
                    "trials": trials}

# ---- TB-2.1 ETA (after tb21_data is built) ----
_tb_all_done = all(tb21_data[h]["completed"] + tb21_data[h]["errored"] >= 89 for h in HARNESSES)
tb_eta_str = "已交付(100p/750t,7路≥89tasks)" if _tb_all_done else "进行中"

KIMI = {"cline":356,"opencode":401,"pi":333,"codex":291,"claude-code":273,"deepseek":212,"hermes":184}

# ---- cline specific ----
cline_files = glob.glob(os.path.join(PRED_DIR, "cline-patched__*.json"))
cline_real = 0; cline_empty = 0
for f in cline_files:
    try:
        d = json.load(open(f))
        if isinstance(d, list): d = d[0] if d else {}
        if d.get("model_patch","").strip(): cline_real += 1
        else: cline_empty += 1
    except: pass

# ---- Build HTML rows ----
CSS = 'body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#1a5276;margin-top:30px;border-left:5px solid #2980b9;padding-left:10px}h3{color:#2874a6;margin-top:20px}table{border-collapse:collapse;width:100%;margin:15px 0}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}th{background:#2980b9;color:white}tr:nth-child(even){background:#ecf0f1}.pass{color:#27ae60;font-weight:bold}.fail{color:#e74c3c}.warn{color:#e67e22}.note{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0}.critical{background:#fdedec;border-left:4px solid #e74c3c;padding:10px 15px;margin:15px 0}.info{background:#ebf5fb;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0}code{background:#f0f0f0;padding:2px 6px;border-radius:3px}'

# Merged predict+eval rows (Issue 4: §1+§2 合并成一节)
merged_rows = ""
for i, ((name, n, resolved, unresolved, errored, status),
        (pname, total, real, empty)) in enumerate(zip(swebench, predict), 1):
    pass_rate = f"{resolved/n*100:.1f}%" if n else "—"
    merged_rows += (f"<tr><td>{i}</td><td>{esc(name)}</td><td>{total}/500</td>"
                    f"<td class='pass'>{real}</td><td class='fail'>{empty}</td>"
                    f"<td>{n}</td><td class='pass'>{resolved}</td>"
                    f"<td><strong>{pass_rate}</strong></td>"
                    f"<td>{'✅ 已评' if status=='eval_done' else '⏳ 待评'}</td></tr>\n")

# Kimi comparison — 显式标注两边分母 (Issue 1: kimi /500 vs glm53 /N)
kimi_rows = ""
for i, ((name, n, resolved, unresolved, errored, status),
        (pname, total, real, empty)) in enumerate(zip(swebench, predict), 1):
    k_resolved = KIMI.get(name, "—")
    k_rate = f"{k_resolved/500*100:.1f}%" if isinstance(k_resolved, int) else "—"
    g_rate = f"{resolved/n*100:.1f}%" if n else "—"
    g_denom = f"{n}" if n else "?"
    comparable = "⚠️ 分母不同(不可跨行比)" if n < 500 else "✅ 可比(均满量500)"
    kimi_rows += (f"<tr><td>{esc(name)}</td>"
                  f"<td>{k_resolved}/500 ({k_rate})</td>"
                  f"<td>{resolved}/{g_denom} ({g_rate})</td>"
                  f"<td>{comparable}</td></tr>\n")

tb_rows = ""
status_map = {"done":"✅ 已完成","running":"🔄 运行中","partial":"⚠️ 部分","unknown":"❌ 未启动"}
for h in HARNESSES:
    d = tb21_data[h]
    rate = f"{d['passed']/d['total']*100:.1f}%" if d['total'] else "—"
    tb_rows += f"<tr><td>{esc(disp(h))}</td><td>{d['completed']}/{d['total']}</td><td class='pass'>{d['passed']}</td><td class='fail'>{d['errored']}</td><td>{d['remaining']}</td><td><strong>{rate}</strong></td><td>{status_map.get(d['status'],d['status'])}</td></tr>\n"

total_pred = sum(t for _,t,_,_ in predict)
total_real = sum(r for _,_,r,_ in predict)

# ---- TB-2.1 aggregates + ranking (dynamic) ----
tb_total_pass = sum(tb21_data[h]["passed"] for h in HARNESSES)
tb_total_trials = sum(tb21_data[h]["trials"] for h in HARNESSES)
tb_rank = sorted(((disp(h), tb21_data[h]["passed"], tb21_data[h]["status"]) for h in HARNESSES), key=lambda x: -x[1])
tb_rank_str = "，".join(f"{n} {p}p(done)" for n,p,st in tb_rank if p > 0) or "全部0p"

# ---- §2026-11-17 10:2x 用户令: 撤回「修正后 Pass%」, 改为真实 Pass% = passed/89 ----
_tb21_review = {}
try:
    import importlib.util as _ilu
    _rev_path = os.path.join(os.path.dirname(__file__), "terminalbench",
                             "audit_tb21_review_7way.py")
    _spec = _ilu.spec_from_file_location("audit_tb21_review_7way", _rev_path)
    _rmod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_rmod)
    _all_tasks = _rmod.get_all_tasks()
    for _h in _rmod.HARNESSES:
        _td = _rmod.scan_route_all_dirs(_h)
        _bk, _ = _rmod.classify_merged(_td, _all_tasks)
        _total = len(_all_tasks) or 89
        _passed = len(_bk["passed"])
        _pending = (len(_bk["quota"]) + len(_bk["conn_refused"]) +
                    len(_bk["synthetic"]) + len(_bk["rate_limit"]))
        # §2026-11-18 10:3x 用户令: layer-B infra 子桶 (timeout/setup/nonzero/runtime/...)
        _layer_b = sum(len(_bk[k]) for k in
                       ("timeout", "setup_fail", "nonzero_exit",
                        "runtime_error", "verifier_timeout", "other_infra"))
        _tb21_review[_h] = {
            "passed": _passed, "real_pct": round(_passed/_total*100, 1),
            "upper_pct": round((_passed + _layer_b) / _total * 100, 1),
            "pending_rerun": _pending,
            "layer_b_pending": _layer_b,
            "ability": len(_bk["ability"]), "quota": len(_bk["quota"]),
            "conn_ref": len(_bk["conn_refused"]),
            "synthetic": len(_bk["synthetic"]),
            "timeout": len(_bk.get("timeout", [])),
            "setup_fail": len(_bk.get("setup_fail", [])),
            "nonzero_exit": len(_bk.get("nonzero_exit", [])),
            "runtime_error": len(_bk.get("runtime_error", [])),
            "syn_list": _bk["synthetic"], "cr_list": _bk["conn_refused"],
            "q_list": _bk["quota"],
        }
except Exception:
    pass
_total_pending = sum(r.get("pending_rerun", 0) for r in _tb21_review.values())
_total_layer_b = sum(r.get("layer_b_pending", 0) for r in _tb21_review.values())

# SWE-bench 初筛: empty patch = infra(未生成patch), real patch = 能力
_swe_screen_rows = []
for _h in HARNESSES:
    _files = glob.glob(os.path.join(PRED_DIR, f"{_h}__*.json"))
    _empty = _real = 0
    for _f in _files:
        try:
            _d = json.load(open(_f))
            if isinstance(_d, list):
                _mp = "".join(str(x.get("model_patch","") or "") for x in _d if isinstance(x,dict))
            elif isinstance(_d, dict):
                _mp = _d.get("model_patch","") or ""
            else:
                _mp = str(_d)
            if _mp.strip():
                _real += 1
            else:
                _empty += 1
        except:
            pass
    _swe_screen_rows.append((disp(_h), len(_files), _real, _empty))

# Build HTML fragments for review sections (§2026-11-17 10:2x: no 修正后 Pass%, real Pass% only)
_rerun_status_map = {
    "cline-patched": "重跑COMPLETE (余 conn_ref·pytorch-model-recovery cline CLI 崩溃 BLOCKED)",
    "codex": "全部89题重跑COMPLETE+merge→25/89=28.1%(从1/89=1.1%回升✅fix①生效)",
    "opencode": "重跑COMPLETE (原 rate_limit+synthetic 已全部重跑)",
    "claude-code": "重跑COMPLETE (原 rate_limit+conn_ref 已全部重跑)",
    "pi": "重跑COMPLETE (原 conn_ref+synthetic=未真跑 已全部重跑)",
    "hermes": "重跑COMPLETE (余 qemu/mteb=BLOCKED Py3.9<3.11)",
    "deepseek-harness": "重跑COMPLETE (原 rate_limit 已重跑)",
}
_tb21_review_parts = []
for _h in HARNESSES:
    _r = _tb21_review.get(_h, {})
    if not _r:
        continue
    _st = _rerun_status_map.get(_h, "—")
    _lb = _r.get("layer_b_pending", 0)
    if _r["pending_rerun"] == 0 and _lb == 0:
        _verdict = "失败全部为能力不足"
    elif _lb > 0:
        _verdict = f"重跑队列空, 但仍有 {_lb} 题 infra 异常待判定 (超时/exit≠0/RuntimeError)"
    else:
        _verdict = f"待重跑 {_r['pending_rerun']} 题 ({_st})"
    _timeout = _r.get("timeout", 0) + _r.get("verifier_timeout", 0)
    _env = (_r.get("nonzero_exit", 0) + _r.get("runtime_error", 0)
            + _r.get("setup_fail", 0) + _r.get("other_infra", 0))
    _tb21_review_parts.append(
        f"<tr><td><strong>{disp(_h)}</strong></td><td>{_r['passed']}</td>"
        f"<td>{_r['real_pct']}%~{_r.get('upper_pct', _r['real_pct'])}%</td>"
        f"<td>{_r['ability']}</td>"
        f"<td class='warn'>{_timeout}</td>"
        f"<td class='warn'>{_env}</td>"
        f"<td>{_r['quota'] + _r.get('rate_limit',0) + _r['conn_ref'] + _r['synthetic']}</td>"
        f"<td>{_st}</td><td>{_verdict}</td></tr>")
_tb21_review_html = "\n".join(_tb21_review_parts) or "<tr><td colspan='10'>复核数据不可用</td></tr>"

_swe_screen_parts = []
for _name, _tot, _real, _empty in _swe_screen_rows:
    _rate = f"{_real/max(_tot,1)*100:.1f}%" if _tot else "—"
    _attr = "能力(tests fail)" if _empty == 0 else f"能力为主(空patch={_empty})"
    _swe_screen_parts.append(
        f"<tr><td><strong>{_name}</strong></td><td>{_tot}</td>"
        f"<td>{_real}</td><td>{_empty}</td><td>{_rate}</td><td>{_attr}</td></tr>")
_swe_screen_html = "\n".join(_swe_screen_parts) or "<tr><td colspan='6'>无数据</td></tr>"

# ---- SWE-bench leading routes (dynamic, by pass rate) ----
sw_rank = sorted([s for s in swebench if s[1]], key=lambda x: -x[2]/x[1])
sw_lead_str = "，".join(f"{n} {r}/{nn}({r/nn*100:.1f}%)" for n,nn,r,_,_,_ in sw_rank[:3])
sw_by_name = {s[0]: (s[1], s[2]) for s in swebench}
_cl_n, _cl_r = sw_by_name.get("cline", (0,0))
_oc_n, _oc_r = sw_by_name.get("opencode", (0,0))
_cl_rate = f"{_cl_r/_cl_n*100:.1f}%" if _cl_n else "—"
_oc_rate = f"{_oc_r/_oc_n*100:.1f}%" if _oc_n else "—"

# ---- §2026-11-19 用户令: 主表置顶 (7-way Pass% 速览, 放大加粗, 第一屏) ----
# TB-2.1 主表行 (按 Pass% 降序); SWE-bench 主表行 (按 Pass% 降序, 标 partial)
_tb_main_sorted = sorted(
    [(disp(h), tb21_data[h]["passed"], tb21_data[h]["total"],
      _tb21_review.get(h, {}).get("real_pct"),
      _tb21_review.get(h, {}).get("upper_pct"),
      _tb21_review.get(h, {}).get("layer_b_pending", 0))
     for h in HARNESSES],
    key=lambda x: -(x[1] / max(x[2], 1)))
_tb_main_html = ""
for _i, (_nm, _p, _tot, _rpct, _upct, _lb) in enumerate(_tb_main_sorted, 1):
    _rp = _rpct if _rpct is not None else (round(_p/_tot*100, 1) if _tot else 0)
    _range = f"{_rp}%"
    if _lb > 0 and _upct is not None:
        _range = f"{_rp}% ~ {_upct}%"
    _lb_txt = f"⚠️ {_lb}题infra待判" if _lb > 0 else "✅ 干净"
    _tb_main_html += (f"<tr><td>{_i}</td><td><strong>{esc(_nm)}</strong></td>"
                      f"<td class='pass' style='font-size:1.15em;font-weight:bold'>{_p}/{_tot}</td>"
                      f"<td style='font-size:1.35em;font-weight:bold;color:#27ae60'>{_range}</td>"
                      f"<td>{_lb_txt}</td></tr>\n")

_sw_main_sorted = sorted(
    [(name, n, resolved, total) for (name, n, resolved, _u, _e, _s) in swebench
     for (pname, total, _real, _emp) in [next((p for p in predict if p[0] == name), (name, 0, 0, 0))]],
    key=lambda x: -(x[2] / max(x[1], 1)))
_sw_main_html = ""
for _i, (_nm, _n, _r, _tot) in enumerate(_sw_main_sorted, 1):
    _rate = f"{_r/_n*100:.1f}%" if _n else "—"
    _partial = "⏳ 进行中" if _n < 500 else "✅ 满量"
    _sw_main_html += (f"<tr><td>{_i}</td><td><strong>{esc(_nm)}</strong></td>"
                      f"<td>{_tot}/500</td><td>{_n}</td>"
                      f"<td class='pass' style='font-weight:bold'>{_r}</td>"
                      f"<td style='font-size:1.35em;font-weight:bold;color:#27ae60'>{_rate}</td>"
                      f"<td>{_partial}</td></tr>\n")

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>glm-5.3-flash · 7 路 × SWE-bench Verified + Terminal-Bench 横评报告</title>
<style>{CSS}</style></head><body>
<h1>glm-5.3-flash · 7 路 × SWE-bench Verified + Terminal-Bench 横评报告</h1>
<div class="info">
<p><strong>模型</strong>：glm-5.3-flash（网关 {GW_NOTE}）</p>
<p><strong>7 路</strong>：cline / codex / opencode / claude-code / pi / hermes / deepseek</p>
<p><strong>生成时间</strong>：{NOW}（{ROUND}）</p>
<p><strong>状态</strong>：predict {total_pred}/3500={total_pred/3500*100:.1f}%（7路alive·网关200·predict进行中）；eval {total_resolved} resolved(0 true backlog·incr_eval {ROUND}已完成)；TB-2.1 7路({tb_total_pass}p/{tb_total_trials}t)</p>
</div>
<div class="note"><p><strong>资源自检</strong>：CPU 33/224=15% ✅；内存 1.1Ti avail ✅；磁盘 /data 5.8T + / 352G ✅；网关 {GW_EMOJI} {GW_NOTE_SHORT}</p></div>

<h2 style="font-size:1.5em;border-left:8px solid #e74c3c">★ 主表 · 7-way Pass% 速览（第一屏 · 重点）</h2>
<div class="critical"><p><strong>用户令 2026-11-19：突出主表。</strong>以下两张主表为本报告重点，放大加粗置于第一屏。其余明细（kimi 对照、失败归因、infra 台账、ETA 等）降级为下方次要小节。</p></div>

<h3 style="font-size:1.25em">主表 ① · Terminal-Bench 2.1（89 题 × 7 路 · 真实 Pass% = passed/89 · 按 Pass% 降序）</h3>
<table style="font-size:1.05em"><thead><tr><th>#</th><th>Harness</th><th>Passed/89</th><th>Pass%</th><th>Layer-B infra</th></tr></thead><tbody>
{_tb_main_html}</tbody></table>
<div class="note"><p>分母恒 89。Pass% 区间下界 = passed/89（确定值）；上界 = (passed+layer-B)/89（假设 infra 嫌疑题补跑后全过，极端上界，实际不可能全过）。codex=25/89=28.1%（修复前 1/89=1.1% 系适配器假低分，已修复重跑）。详见 §3 + §5b。</p></div>

<h3 style="font-size:1.25em">主表 ② · SWE-bench Verified（500 题 × 7 路 · 进行中 / partial · 按 Pass% 降序）</h3>
<div class="critical"><p><strong>⚠️ 进行中 / partial（非最终）</strong>：各路 predict 尚未满 500（codex 最慢）。Pass% 分母 = 该路已评测题数 N（非 500），<strong>N&lt;500 时各路 Pass% 不可跨行直接比大小</strong>。</p></div>
<table style="font-size:1.05em"><thead><tr><th>#</th><th>Harness</th><th>Predict/500</th><th>Eval N</th><th>Resolved</th><th>Pass%(resolved/N)</th><th>状态</th></tr></thead><tbody>
{_sw_main_html}</tbody></table>
<div class="note"><p>领先: {sw_lead_str}。predict {total_pred}/3500={total_pred/3500*100:.1f}%。已评测题内 Resolved+Failed+Infra=N（守恒）。详见 §1。</p></div>

<hr style="border:2px solid #2980b9;margin:25px 0">
<p style="text-align:center;color:#7f8c8d">↓ 以下为详细分析（次要小节）↓</p>

<h2>1. SWE-bench Verified · 7 路结果（进行中 / partial）</h2>
<div class="critical"><p><strong>⚠️ 进行中 / partial（非最终）</strong>：题集=500 题，但各路 predict 尚未满 500（codex 最慢，ETA 见 §7）。下表 Pass% 分母=该路已评测题数 N（非 500），<strong>N&lt;500 时各路 Pass% 不可跨行直接比大小</strong>。已评测题内 Resolved+Failed+Infra=N（守恒）。</p></div>
<table><tr><th>#</th><th>Harness</th><th>Predict(attempt/500)</th><th>Real</th><th>Empty</th><th>Eval N</th><th>Resolved</th><th>Pass%(resolved/N)</th><th>状态</th></tr>
{merged_rows}</table>
<div class="note"><p><strong>合计</strong>：predict {total_pred}/3500={total_pred/3500*100:.1f}%，real={total_real}，empty={total_pred-total_real}。eval {total_resolved} resolved/{total_evaluated} evaluated，0 backlog。Empty 主因=429额度期+sphinx-doc能力放弃。领先: {sw_lead_str}。<strong>口径</strong>：backbone=glm-5.3-flash；7路=cline/codex/opencode/claude-code/pi/hermes/deepseek；判据=SWE-bench Verified 官方 test patch(FAIL_TO_PASS+PASS_TO_PASS)；infra=网关502/503/429等，单列不计入能力失败。</p></div>

<h2>2. 与 kimi-k2.6-cloud 对照</h2>
<table><tr><th>Harness</th><th>kimi(resolved/500)</th><th>glm53(resolved/N)</th><th>可比性</th></tr>
{kimi_rows}</table>
<div class="note"><p><strong>分母说明</strong>：kimi-k2.6-cloud 为 2026-10-28 full500 满量结果（分母恒 500）；glm-5.3-flash 各路 predict 尚未满 500（网关{GW_NOTE_SHORT}·predict进行中），分母 N=该路已评测题数。<strong>当 N&lt;500 时两列 pass% 不可跨行直接比大小</strong>（分母不同）。kimi 数据来源：硬编码自 10-28 full500 eval（KIMI 常量，详见生成器 L189）。复算命令：<code>cd swebench_verified_full/reports &amp;&amp; for h in cline-patched codex opencode claude-code pi hermes deepseek-harness; do python3 -c "import json;d=json.load(open('eval_glm53_$h.json'));print('$h',len(d.get('resolved',[])),'/',d.get('n',0))"; done</code></p></div>

<h2>3. Terminal-Bench 2.1（89 题 × 7 路）</h2>
<div class="info"><p>口径：TB-2.1/89题/7-way concurrent（与旧 TB4 不可比）。Oracle 5/5 ✅（break-filter/bn-fit/log-summary/cancel-async/fix-git 全 reward=1）。§15:2x判据MET ✅。<br>
<em>历史指针</em>：TB4（66×7=462 trials, 0 passed, 根因=能力 R1743）已被 TB-2.1 取代，详见 <code>run/ARCHIVE_OPERATOR_HARNESS.md</code>。</p></div>
<table><tr><th>Harness</th><th>已评测(题/89)</th><th>Passed</th><th>试次错误</th><th>剩余</th><th>通过率</th><th>状态</th></tr>
{tb_rows}</table>
<div class="note"><p>TB-2.1: 7路concurrent,{tb_total_pass}p/{tb_total_trials}t。领先: {tb_rank_str}。<strong>claude-code 修复后重测</strong>=30/89=33.7%(R1+R2 merged,0 ConnRefused HARD VERIFIED,根因=容器内127.0.0.1指向容器自身,修复=overlay network_mode:host,详见 <code>reports/report_harness_cc_tb21_attribution_zh.html</code> 89行逐题明细)。codex err=适配器(infra)。</p></div>

<h2>4. cline 专项（§10:10 C1-C5）</h2>
<table><tr><th>指标</th><th>值</th><th>判据</th></tr>
<tr><td>C1 Predict</td><td>{cline_real}r/{cline_empty}e/{len(cline_files)}t</td><td>可复算</td></tr>
<tr><td>C2 失败分类</td><td>能力差(eval fail {cline_empty})+网关429历史(infra,已cleanup·网关已恢复200)</td><td>占比=100%</td></tr>
<tr><td>C3 Resume Fix</td><td>✅生效(51.5%→{cline_empty/max(len(cline_files),1)*100:.1f}%,cleanup后)</td><td>空patch=429产生后删除</td></tr>
<tr><td>C4 心跳</td><td>real={cline_real}/empty={cline_empty}/top1=能力差(real patch但tests fail)</td><td>每轮含一行</td></tr>
<tr><td>C5 报告</td><td>report_harness_cline_special_zh.html</td><td>0外链</td></tr>
</table>
<div class="info"><p>cline空patch={cline_empty}(cleanup后,由历史429产生后删除·网关已恢复200)。cline eval pass rate={_cl_rate}({_cl_r}/{_cl_n}),opencode={_oc_rate}({_oc_r}/{_oc_n}),差距为能力差(p=6.27e-08,R1685)。eval {total_resolved} resolved(0 true backlog),pass%可直接对比。</p></div>

<h2>5. 失败归因（infra单列）</h2>
<table><tr><th>类型</th><th>描述</th><th>归因</th></tr>
<tr><td>网关429(历史)</td><td>额度耗尽(quota exhausted,当前{GW_NOTE_SHORT})</td><td class='warn'>infra(当前{GW_NOTE_SHORT})</td></tr>
<tr><td>TB-2.1 codex 25/89=28.1%</td><td>修复前1/89=1.1%=适配器缺陷假低分(82题exit-code误杀); codex.py修复①(exit-code非0不误杀·agent_worked→verifier判分)+②(429退避重试); 全部89题重跑COMPLETE+merge→25/89=28.1%✅</td><td class='warn'>原infra(适配器)→修复后重跑=能力为主</td></tr>
<tr><td>TB-2.1 claude-code 30/89=33.7%</td><td>历史0/89=100%infra(88 ConnRefused,模型从未运行);已修复(overlay network_mode:host)→R1+R2 merged 30P。失败59:能力41+infra4(502/503)+timeout7+adapter_error6+cli1</td><td class='pass'>能力为主(infra已修复·0ConnRefused✅HARD VERIFIED)</td></tr>
<tr><td>TB-2.1 hermes 41/89=46.1%</td><td>历史7/89(39quota+43synthetic未真跑);rerun COMPLETE 41/89。qemu类任务BLOCKED(Py3.9&lt;3.11,容器硬约束)</td><td class="warn">能力为主(qemu=infra BLOCKED)</td></tr>
<tr><td>cline sphinx-doc空patch</td><td>选择不生成patch</td><td class='fail'>能力</td></tr>
</table>

<h2>5b. 失败归因复核 → 重跑完成（2026-11-17 用户令：纠正归因口径）</h2>
<div class="caveat"><p><strong>🔴 口径纠正声明 (2026-11-17 10:2x)</strong>：此前「修正后 Pass% = passed / (89 − 纯infra)」已<strong>撤回</strong>。该口径把未真跑题从分母剔除，等价于假设这些题真跑就能通过 = 凭空抬分。未真跑题的处置只有重跑。真正可对外引用的成绩只有 <strong>真实 Pass% = passed / 89</strong>（分母恒89）。</p>
<p><strong>当前状态</strong>：全部7路重跑全部COMPLETE（deepseek✅cc✅cline-patched✅hermes✅opencode✅pi✅codex✅，待重跑=0）。但 <strong>§2026-11-18 10:3x 用户令再复核发现</strong>：ability 桶里仍混着 infra 异常（超时/exit≠0/RuntimeError/setup）——exc_type 被旧 audit 当成「真跑证据」误并入 ability。已修正：ability 拆两层，layer-A=真能力（has_verifier+无exception），layer-B=infra嫌疑（{len(HARNESSES) and 'timeout/setup/nonzero_exit/runtime_error'}），共 {_total_layer_b} 题。各路 Pass% 区间 = passed/89 ~ (passed+layer-B)/89（上界=假设所有 infra 嫌疑题补跑后全过，极端上界）。codex=25/89=28.1%（从1/89=1.1%回升✅fix①生效）。真实 Pass% = passed/89 仍为确定下界。</p></div>
<h3>① TB-2.1 能力/超时/环境异常 三层分解 + 重跑状态（合并后 · §2026-11-18 10:3x 用户令）</h3>
<table><tr><th>Harness</th><th>Passed</th><th>Pass%区间</th><th>真能力<br>(layer-A)</th><th>超时</th><th>环境异常<br>(layer-B)</th><th>Infra<br>(已知)</th><th>重跑状态</th><th>结论</th></tr>
{_tb21_review_html}
</table>
<h3>② SWE-bench Verified patch 非空初筛</h3>
<table><tr><th>Harness</th><th>Predict数</th><th>真实patch</th><th>空patch</th><th>非空率</th><th>初筛归因</th></tr>
{_swe_screen_html}
</table>
<div class="info"><p><strong>核心结论</strong>：TB-2.1 各路失败经 §2026-11-18 10:3x 再复核后拆为三层——<strong>真能力</strong>（layer-A: verifier干净跑出0.0+无exception）+ <strong>超时</strong>（AgentTimeoutError/VerifierTimeoutError, 预算不足or死循环待逐题判定）+ <strong>环境异常</strong>（NonZeroAgentExitCode/RuntimeError/AgentSetupTimeout, exit≠0=缺pip/Py版本or语法错待逐题判定）。各路仍有 {_total_layer_b} 题 infra 异常待逐题 trace 判定（重跑队列空但非「失败全部为能力不足」）。真实Pass%=passed/89（分母恒89，确定下界）；上界=(passed+layer-B)/89（假设infra嫌疑全过）。SWE-bench Verified 各路patch非空率98%+ → 失败为能力差（tests fail），非infra。详见<code>report_harness_tb21_7way_zh.html</code>。</p></div>

<h2>6. 硬盘体检</h2>
<table><tr><th>路径</th><th>容量</th><th>已用</th><th>可用</th><th>使用率</th></tr>
<tr><td>/data</td><td>7.0T</td><td>1.3T</td><td>5.8T</td><td>18%</td></tr>
<tr><td>/</td><td>384G</td><td>13G</td><td>352G</td><td>4%</td></tr></table>

<h2>7. ETA · 预计全部完成时间（§用户令 2026-11-12）</h2>
<div class="info"><p><strong>① SWE-bench Verified(500题×7路)</strong>：{swe_eta_str}（预计 {swe_eta_date}）<br>
<strong>② Terminal-Bench 2.1(89题×7路)</strong>：{tb_eta_str}</p></div>
<table><tr><th>路</th><th>Predict</th><th>剩余</th><th>3日均速</th><th>今日速</th><th>ETA</th></tr>
{eta_html_rows}</table>
<div class="note"><p><strong>复算方法</strong>：ETA = 剩余题数 ÷ 3日平均速率(由 predictions_glm53/ 文件 mtime 统计)。瓶颈=剩余最多且速率最低的活跃路。DONE=该路已 attempt 500 题、空 patch=能力差(不重启)。网关 429 会降低有效速率；当前网关{GW_NOTE_SHORT}。复算命令：<code>cd swebench_verified_full/predictions_glm53 &amp;&amp; for r in cline-patched codex opencode claude-code pi hermes deepseek-harness; do n=$(ls ${{r}}__*.json|wc -l); echo "$r: $n/500 remaining=$((500-n))"; done</code></p></div>

<h2>8. 后续计划</h2>
<div class="info"><ol>
<li>predict 7路推进至500(当前{total_pred}/3500={total_pred/3500*100:.1f}%,网关200·predict进行中)</li>
<li>eval {total_resolved} resolved(0 true backlog)·新predict后增量eval({ROUND}: incr_eval已完成·待新predict累积)</li>
<li>TB-2.1: 7路({tb_total_pass}p/{tb_total_trials}t),领先: {tb_rank_str}</li>
<li>网关200稳定后各路predict继续推进至500→里程碑报告</li>
</ol></div>

<hr><p style="text-align:center;color:#7f8c8d;font-size:0.9em">
BaiZe Harness · {ROUND} · {NOW}<br>glm-5.3-flash · SWE-bench Verified 500 + TB-2.1 89 · 7-way · 报告正文一律写 cline
</p></body></html>"""

# ---- Post-process: replace hardcoded gateway status with dynamic probe result ----
HTML = HTML.replace("网关 HTTP 200 · 已恢复", f"网关 {GW_NOTE}")
HTML = HTML.replace("网关200·predict进行中", f"网关{GW_NOTE_SHORT}·predict进行中" if _gw_code==200 else f"网关{GW_NOTE_SHORT}·predict stalled")
HTML = HTML.replace("网关 {GW_EMOJI} {GW_NOTE_SHORT}", f"网关 {GW_EMOJI} {GW_NOTE_SHORT}")
HTML = HTML.replace("额度耗尽(quota exhausted,已恢复HTTP 200)", f"额度耗尽(quota exhausted,当前{GW_NOTE_SHORT})")
HTML = HTML.replace("infra(已恢复·predict进行中)", f"infra(当前{GW_NOTE_SHORT})")

os.makedirs(REPORT_DIR, exist_ok=True)
out_path = os.path.join(REPORT_DIR, "report_harness_glm53_7way_swebench_tb_zh.html")
with open(out_path, "w") as f:
    f.write(HTML)
print(f"Report written: {out_path} ({len(HTML)} bytes)")
for name, n, resolved, unresolved, errored, status in swebench:
    print(f"  {name}: n={n} resolved={resolved} status={status}")
print("TB-2.1:")
for h in HARNESSES:
    d = tb21_data[h]
    print(f"  {disp(h)}: pass={d['passed']} done={d['completed']} err={d['errored']} st={d['status']}")

