#!/usr/bin/env python3
"""trace_ledger.py — trace 处理台账 + 覆盖率进度（纯标准库）

解决两件事：
  1) 去重：开工前 `next` 取候选（自动排除已动过的 session），`claim` 落台账；
  2) 进度：`stats --bar` 打印覆盖率百分比，`refresh` 记录候选池并显示新增 trace。

文件（本目录）：
  trace_ledger.tsv     逐 session 台账（只有"动过的"，很小，可入库）
  summary_stats.json   候选池规模快照（每轮刷一次）

台账列：session_file user host match_count domain status case_id updated_at note
status：claimed / deepread / case / parked
"""
import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATS = os.path.join(HERE, "summary_stats.json")

# ---- shard 支持：按 domain 分片，每个 shard 独立 ledger + tools 过滤候选 ----
# summary.tsv 列: ip host user session_file match_count keywords tools
# tools 列（$7）做 domain 代理过滤（不完美，agent 可 peek-and-skip）
SHARD_DOMAINS = {
    # shard A 11/06 放宽: 加 synthesis/synopsys/tcl/verilog/systemverilog/rtl/synthesis/sdc
    # (数字前端工程师少用 cline, 旧过滤词只命中 53 session, 放宽后 11/05 新扫描命中 187)
    "A": ("digital|verification|pnr_signoff|eda_other",
          "verdi|vcs|dc_shell|verilint|formality|innovus|primetime|design_compiler|rc|pt_shell"
          "|synthesis|synopsys|tcl|verilog|systemverilog|rtl|sdc|vivado|yosys|openroad"),
    "B": ("spice_sim|characterization",
          "hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim"),
    "C": ("physical_verify|layout_virtuoso|layout_aether|pg_layout",
          "calibre|virtuoso|aether|ipcustom|layout|lvs|drc|pexivirtuoso"),
    "D": ("schematic_netlist|waveform|analog_context",
          "waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic"),
}
# per-shard mc 阈值 (shard A 候选稀缺, 降到 15; 其他保持 30)
# 可被 summary_stats.json 的 shard_mc 字段覆盖
SHARD_MC = {"A": 15, "B": 30, "C": 30, "D": 30}

# 运行时由 --shard 设定
_shard = None
LEDGER = os.path.join(HERE, "trace_ledger.tsv")

def _set_shard(s):
    global _shard, LEDGER
    _shard = s
    if s:
        LEDGER = os.path.join(HERE, "trace_ledger_%s.tsv" % s)

COLS = ["session_file", "user", "host", "match_count", "domain", "status",
        "case_id", "updated_at", "note"]
VALID_STATUS = ("claimed", "deepread", "case", "parked", "seeded")
# 'seeded' = shard agent 已把 trace 种入 jsonl (出完 case)，等同 'case' 计入覆盖
COVERED = ("case", "seeded")                   # 计入"已覆盖"
TOUCHED = ("claimed", "deepread", "case", "parked", "seeded")   # 计入"已动过"


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _load_file(path):
    """从单个台账文件读行（不设全局 LEDGER）。"""
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            parts += [""] * (len(COLS) - len(parts))
            if parts[0] == COLS[0]:      # 容忍误写入的表头行
                continue
            rows.append(dict(zip(COLS, parts[:len(COLS)])))
    return rows


def load():
    # 无 --shard 时：聚合 4 个 per-shard 台账（真实数据源），而非过时的合并台账
    if _shard is None:
        shard_files = [os.path.join(HERE, "trace_ledger_%s.tsv" % s)
                       for s in ("A", "B", "C", "D")]
        if any(os.path.exists(p) for p in shard_files):
            rows = []
            for p in shard_files:
                rows.extend(_load_file(p))
            return rows
    return _load_file(LEDGER)


def save(rows):
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in COLS) + "\n")
    os.replace(tmp, LEDGER)


def load_stats():
    if not os.path.exists(STATS):
        return {}
    with open(STATS, encoding="utf-8") as f:
        return json.load(f)


def target_of(stats):
    """分母 = 候选池规模（默认 match_count>=30，可用 stats.target_mc 覆盖）"""
    mc = int(stats.get("target_mc", 30))
    for k in ("mc%d" % mc, "mc30", "mc100", "mc300", "sessions"):
        if stats.get(k):
            return int(stats[k]), mc
    return int(stats.get("sessions", 0) or 0), mc


def bar(pct, width=28):
    pct = max(0.0, min(100.0, pct))
    filled = int(round(width * pct / 100.0))
    return "[" + "#" * filled + "." * (width - filled) + "]"


def _upsert(session, **kw):
    rows = load()
    for r in rows:
        if r["session_file"] == session:
            for k, v in kw.items():
                if v not in (None, ""):
                    r[k] = str(v)
            r["updated_at"] = _now()
            save(rows)
            return r
    r = {c: "" for c in COLS}
    r["session_file"] = session
    r["status"] = kw.pop("status", "claimed")
    for k, v in kw.items():
        if v not in (None, ""):
            r[k] = str(v)
    r["updated_at"] = _now()
    rows.append(r)
    save(rows)
    return r

def cmd_stats(args):
    rows = load()
    st = load_stats()
    target, mc = target_of(st)
    covered = [r for r in rows if r["status"] in COVERED]
    touched = [r for r in rows if r["status"] in TOUCHED]
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    pct = (100.0 * len(covered) / target) if target else 0.0
    if target:
        print("trace 覆盖率 %s %5.1f%%   covered=%d / target=%d (mc>=%d)"
              % (bar(pct), pct, len(covered), target, mc))
    else:
        print("trace 覆盖率：候选池未知（先 refresh：sessions/mc300/mc500/mc1000）；covered=%d"
              % len(covered))
    print("  已动过 %d：case %d · deepread %d · parked %d · claimed %d"
          % (len(touched), by.get("case", 0), by.get("deepread", 0),
             by.get("parked", 0), by.get("claimed", 0)))
    if target:
        print("  剩余可做 ≈ %d（已动过的不再计入）" % max(0, target - len(touched)))
    if st.get("updated_at"):
        print("  快照 %s：sessions=%s mc300=%s mc500=%s mc1000=%s"
              % (st.get("updated_at"), st.get("sessions"), st.get("mc300"),
                 st.get("mc500"), st.get("mc1000")))
    if st.get("prev_sessions"):
        print("  新增 traces（自上次刷新）：%+d"
              % (int(st.get("sessions", 0)) - int(st["prev_sessions"])))
    dom = {}
    for r in covered:
        if r.get("domain"):
            dom[r["domain"]] = dom.get(r["domain"], 0) + 1
    if dom:
        print("  已覆盖 domain：" + " · ".join("%s:%d" % (k, v) for k, v in sorted(dom.items())))
    if args.html:
        print(html_block(rows, st))


def html_block(rows=None, st=None):
    """日报用的 HTML 片段（内联样式，无外链）"""
    rows = load() if rows is None else rows
    st = load_stats() if st is None else st
    target, mc = target_of(st)
    covered = [r for r in rows if r["status"] in COVERED]
    touched = [r for r in rows if r["status"] in TOUCHED]
    pct = (100.0 * len(covered) / target) if target else 0.0
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    dom = {}
    for r in covered:
        if r.get("domain"):
            dom[r["domain"]] = dom.get(r["domain"], 0) + 1
    delta = "—"
    if st.get("prev_sessions"):
        delta = "新增 traces（自上次刷新）：%+d" % (
            int(st.get("sessions", 0)) - int(st["prev_sessions"]))
    dom_html = "".join("<li>%s：<b>%d</b></li>" % (k, v) for k, v in sorted(dom.items()))
    pct_txt = ("%.1f%%" % pct) if target else "—"
    width = pct if target else 0.0
    pool_txt = str(target) if target else "未知（待 refresh）"
    return (
        '<h3>trace 覆盖率进度条（候选池 mc&ge;%d，合并 4 shard ledger）</h3>\n'
        '<div class="kpis">\n'
        '<div class="kpi"><div class="n">%s</div><div class="l">已用 / 候选池（mc&ge;%d）</div></div>\n'
        '<div class="kpi"><div class="n">%d</div><div class="l">已用去重 session</div></div>\n'
        '<div class="kpi"><div class="n">%s</div><div class="l">候选池总量</div></div>\n'
        '<div class="kpi"><div class="n">%d</div><div class="l">已动过（含暂缓）</div></div>\n'
        '</div>\n'
        '<div style="background:#e3e8ef;border-radius:6px;height:18px;overflow:hidden">'
        '<div style="width:%.1f%%;height:18px;background:#2c7be5"></div></div>\n'
        '<p style="color:#666;font-size:.8rem">%s · 台账 case %d / seeded %d / deepread %d / parked %d / claimed %d</p>\n'
        '<ul>%s</ul>\n'
        % (mc, pct_txt, mc, len(covered), pool_txt, len(touched), width, delta,
           by.get("case", 0), by.get("seeded", 0), by.get("deepread", 0),
           by.get("parked", 0), by.get("claimed", 0), dom_html or "<li>—</li>"))
def cmd_next(args):
    # 规范化：台账存 bare 形式或带 .messages.json 后缀混存，summary.tsv 统一带后缀。
    # strip 后缀再做 anchor 匹配，避免 $-anchor 漏放行已用 session。
    used = [r["session_file"].replace(".messages.json", "")
            for r in load() if r["session_file"]]
    st = load_stats()
    # per-shard mc 阈值: SHARD_MC → summary_stats.json.shard_mc → target_mc → 30
    shard_mc_cfg = st.get("shard_mc", {}) if isinstance(st.get("shard_mc"), dict) else {}
    if _shard and _shard in SHARD_MC:
        mc = int(shard_mc_cfg.get(_shard, SHARD_MC[_shard]))
    else:
        mc = int(st.get("target_mc", 30))
    # 扫描路径: 优先 summary_stats.json.scan_path, 否则用 .75 上最新扫描目录
    scan_tsv = st.get("scan_path", "")
    if not scan_tsv:
        scan_tsv = "/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv"
    pat = "|".join(used) if used else "__none__"
    # shard tools 过滤（$7 = tools 列）
    tool_filter = ""
    if _shard and _shard in SHARD_DOMAINS:
        tools_re = SHARD_DOMAINS[_shard][1]
        tool_filter = " && $7 ~ /%s/" % tools_re
    print("# 1) 在 .75 上跑（经 eda_flow run_commands）取候选，已排除台账里的 session%s：" % ("，按 shard %s tools 过滤" % _shard if _shard else ""))
    print("# (sub(/\\.messages\\.json$/,\"\",$4) 规范化后做 anchor 匹配)")
    print("# 候选池 mc>=%d%s (11/06: shard A 放宽过滤词+降到 mc>=15; 其他 shard 保持 mc>=30)" % (mc, " [shard %s 专属阈值]" % _shard if _shard and _shard in SHARD_MC and mc != 30 else ""))
    print("# 扫描源: %s" % scan_tsv)
    print("awk -F'\\t' 'NR>1 && $5+0>=%d {sub(/\\.messages\\.json$/,\"\",$4); $4 !~ /^(%s)$/%s {print $5\"\\t\"$4\"\\t\"$3\"\\t\"$2\"\\t\"$7}' "
          "%s | sort -rn | head -%d"
          % (mc, pat, tool_filter, scan_tsv, args.n))
    # 预筛提示
    pre = load_prefilter() if args.prefiltered else {}
    if args.prefiltered:
        rejects = [sf for sf, r in pre.items() if r.get("verdict") == "reject"]
        print("# 1.5) --prefiltered: 已排除 %d 个 prefilter reject" % len(rejects))
        if rejects:
            print("#   rejects: %s" % " ".join(s[:20] for s in rejects[:5]))
    else:
        print("# 1.5) 可选: 对候选跑 0.8B 预筛 (trace_prefilter.py), 过滤非 EDA session")
        print("#   python3 designflow/trace_prefilter.py batch --summary <candidates.tsv> --min-mc %d --limit %d" % (mc, args.n))
        print("#   python3 designflow/trace_ledger.py%s prefilter --apply" % (" --shard %s" % _shard if _shard else ""))
    print("# 2) 选第一条，落台账：")
    print("python3 designflow/trace_ledger.py%s claim --session <session_file> --user <user> "
          "--host <host> --match <match_count> [--domain <domain>]"
          % (" --shard %s" % _shard if _shard else ""))
    print("# 3) 出完 case 后结算（这是覆盖率的唯一分子来源）：")
    print("python3 designflow/trace_ledger.py%s mark --session <session_file> --status case "
          "--case-id <EDA-Eval-DesignFlow-XXX>"
          % (" --shard %s" % _shard if _shard else ""))
    print("# 台账已有 %d 条，均已从候选中排除。" % len(used))


def cmd_claim(args):
    for r in load():
        if r["session_file"] == args.session and r["status"] in TOUCHED:
            print("REFUSED: 该 session 已在台账（status=%s, case_id=%s, %s）"
                  % (r["status"], r["case_id"] or "-", r["updated_at"]))
            return 1
    _upsert(args.session, user=args.user, host=args.host, match_count=args.match,
            domain=args.domain, status="claimed", note=args.note)
    print("claimed: %s (%s/%s, mc=%s)" % (args.session, args.user, args.host, args.match))
    return 0


def cmd_mark(args):
    if args.status not in VALID_STATUS:
        print("bad status: %s (allowed: %s)" % (args.status, "/".join(VALID_STATUS)))
        return 2
    _upsert(args.session, status=args.status, case_id=args.case_id, note=args.note)
    print("marked: %s -> %s%s" % (args.session, args.status,
                                  (" (%s)" % args.case_id) if args.case_id else ""))
    return 0


def cmd_seed(args):
    """把 jsonl 里已有的 case 灌进台账（一次性 bootstrap）"""
    rows = load()
    have = {r["session_file"] for r in rows if r["session_file"]}
    added = 0
    with open(args.jsonl, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            md = r.get("metadata") or {}
            ts = md.get("trace_source") or {}
            s = ts.get("session_file")
            if not s or s in have:
                continue
            rows.append({
                "session_file": s, "user": ts.get("user", ""), "host": ts.get("host", ""),
                "match_count": str(ts.get("match_count", "")),
                "domain": md.get("domain", ""), "status": "case",
                "case_id": r.get("task_id", ""), "updated_at": _now(), "note": "seeded",
            })
            have.add(s)
            added += 1
    save(rows)
    print("seeded %d case(s) from %s; ledger total=%d" % (added, args.jsonl, len(rows)))
    return 0


PREFILTER_RESULTS = os.path.join(HERE, "prefilter_results.jsonl")


def load_prefilter():
    """读 prefilter_results.jsonl, 返回 {session_file: verdict_dict}"""
    out = {}
    if not os.path.exists(PREFILTER_RESULTS):
        return out
    with open(PREFILTER_RESULTS, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            sf = r.get("session") or r.get("session_file")
            if sf:
                out[sf] = r
    return out


def cmd_prefilter(args):
    """批量跑 0.8B 预筛 + 把 verdict 写回台账 note 列

    用法:
      # 用已有 prefilter_results.jsonl 更新台账 (不重跑 0.8B)
      python3 trace_ledger.py prefilter --apply

      # 对 candidates.tsv 跑预筛 + 写台账
      python3 trace_ledger.py prefilter --candidates candidates_mc30.tsv --apply
    """
    import subprocess
    if args.candidates:
        # 跑 trace_prefilter.py
        cmd = ["python3", os.path.join(HERE, "trace_prefilter.py"), "batch",
               "--summary", args.candidates,
               "--min-mc", str(args.min_mc),
               "--output", PREFILTER_RESULTS]
        if args.limit:
            cmd += ["--limit", str(args.limit)]
        print("running: %s" % " ".join(cmd))
        rc = subprocess.call(cmd)
        if rc != 0:
            print("prefilter failed (rc=%d)" % rc)
            return rc
    if not os.path.exists(PREFILTER_RESULTS):
        print("no prefilter_results.jsonl; run with --candidates first")
        return 1
    results = load_prefilter()
    print("prefilter results: %d sessions" % len(results))
    # 统计
    from collections import Counter
    verdicts = Counter(r.get("verdict") for r in results.values())
    print("  verdicts: %s" % dict(verdicts))
    if not args.apply:
        print("(dry-run; --apply 写入台账)")
        return 0
    # 写回台账: reject → status=parked, note=prefilter_reject
    #          accept/uncertain → note=prefilter_<verdict> (不改变 status)
    n_reject = n_label = 0
    rows = load()
    have = {r["session_file"]: r for r in rows}
    for sf, r in results.items():
        v = r.get("verdict", "uncertain")
        # 规范化 session_file 形式 (台账可能存 bare 或带后缀)
        keys = [sf, sf + ".messages.json"]
        # 也试 strip 后缀
        if sf.endswith(".messages.json"):
            keys.append(sf.replace(".messages.json", ""))
        matched = None
        for k in keys:
            if k in have:
                matched = k
                break
        if matched:
            row = have[matched]
        else:
            # 新建一行 (不 claim, 只记 prefilter 结果)
            row = {c: "" for c in COLS}
            row["session_file"] = sf
            row["status"] = "parked" if v == "reject" else ""
            row["match_count"] = str(r.get("mc", ""))
            row["user"] = r.get("user", "")
            rows.append(row)
            have[sf] = row
        note = "prefilter_%s conf=%.2f" % (v, float(r.get("confidence", 0)))
        if v == "reject":
            row["status"] = "parked"
            row["note"] = note + " | " + str(r.get("reason", ""))[:80]
            n_reject += 1
        else:
            # 不覆盖已有 case/seeded 的 note
            if row["status"] not in COVERED:
                row["note"] = note
            n_label += 1
        row["updated_at"] = _now()
    save(rows)
    print("applied: %d reject→parked, %d labeled (accept/uncertain); ledger total=%d"
          % (n_reject, n_label, len(rows)))
    return 0


def cmd_refresh(args):
    try:
        new = json.loads(args.json)
    except Exception as e:
        print("bad json: %s" % e)
        return 2
    st = load_stats()
    if st.get("sessions"):
        st["prev_sessions"] = st["sessions"]
    st.update(new)
    st["updated_at"] = _now()
    with open(STATS, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("stats refreshed: %s" % json.dumps({k: st[k] for k in sorted(st)}, ensure_ascii=False))
    return 0


def cmd_scansync(args):
    """管理任务: 在 .75 上找最新扫描目录, 统计各口径, 输出 ready-to-run 命令块.
    shard A 用这个做每日巡检: 更新 summary_stats.json + 报告各 shard 候选池规模 + 新增 trace."""
    st = load_stats()
    old_scan = st.get("scan_path", "/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv")
    print("# === scansync: 在 .75 上跑 (经 eda_flow run_commands) ===")
    print("# 1) 找最新扫描目录 (按时间排序)")
    print("ls -dt /home/t0002965/log/ssh_eda_search_*/ 2>/dev/null | head -1")
    print("# 2) 用最新扫描统计各口径 (假设最新目录是 $SCAN_DIR):")
    print("#    SCAN_DIR=$(ls -dt /home/t0002965/log/ssh_eda_search_*/ | head -1)")
    print("#    SUMMARY=$SCAN_DIR/summary.tsv")
    print("echo \"scan_dir: $SCAN_DIR\"")
    print("echo \"total_rows: $(tail -n +2 $SUMMARY | wc -l)\"")
    print("echo \"dedup_sessions: $(tail -n +2 $SUMMARY | awk -F'\\t' '{print $4}' | sort -u | wc -l)\"")
    print("echo \"dedup_users: $(tail -n +2 $SUMMARY | awk -F'\\t' '{print $3}' | sort -u | wc -l)\"")
    print("echo \"dedup_hosts: $(tail -n +2 $SUMMARY | awk -F'\\t' '{print $2}' | sort -u | wc -l)\"")
    print("echo \"mc30: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=30 {print $4}' | sort -u | wc -l)\"")
    print("echo \"mc100: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=100 {print $4}' | sort -u | wc -l)\"")
    print("echo \"users_mc30: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=30 {print $3}' | sort -u | wc -l)\"")
    print("# 3) 各 shard 候选池规模 (用当前过滤词 + mc 阈值):")
    for sid in sorted(SHARD_DOMAINS):
        tools_re = SHARD_DOMAINS[sid][1]
        mc = SHARD_MC.get(sid, 30)
        print("echo \"shard_%s_pool_mc%d: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=%d && $7 ~ /%s/ {print $4}' | sort -u | wc -l)\""
              % (sid, mc, mc, tools_re))
    print("# 4) 新增 session (旧扫描没有的):")
    print("echo \"new_sessions: $(comm -13 <(tail -n +2 %s | awk -F'\\t' '$5+0>=30{print $4}' | sort -u) <(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=30{print $4}' | sort -u) | wc -l)\""
          % old_scan)
    print("# 5) 各 shard 的新增候选 (旧扫描没有的):")
    for sid in sorted(SHARD_DOMAINS):
        tools_re = SHARD_DOMAINS[sid][1]
        mc = SHARD_MC.get(sid, 30)
        print("echo \"shard_%s_new: $(comm -13 <(tail -n +2 %s | awk -F'\\t' '$5+0>=%d && $7 ~ /%s/{print $4}' | sort -u) <(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=%d && $7 ~ /%s/{print $4}' | sort -u) | wc -l)\""
              % (sid, old_scan, mc, tools_re, mc, tools_re))
    print("# 6) 更新 summary_stats.json (把上面的数字填进去):")
    print("#    python3 designflow/trace_ledger.py refresh --json '{\"scan_path\":\"$SCAN_DIR/summary.tsv\",\"mc30\":NNN,...}'")
    print("# 7) daily scan log 增量 (今日新增 trace):")
    print("TODAY=$(date +%%Y%%m%%d)")
    print("echo \"today_log: /home/t0002965/log/eda_trace_$TODAY.log\"")
    print("echo \"today_sessions: $(grep -c '^10\\.' /home/t0002965/log/eda_trace_$TODAY.log 2>/dev/null)\"")
    print("# 旧扫描: %s" % old_scan)
    return 0


def main():
    ap = argparse.ArgumentParser(description="trace ledger + coverage progress")
    ap.add_argument("--shard", default=None, choices=sorted(SHARD_DOMAINS.keys()),
                    help="shard ID (A/B/C/D): uses trace_ledger_<X>.tsv + tools filter in next")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stats")
    p.add_argument("--bar", action="store_true")
    p.add_argument("--html", action="store_true")
    p = sub.add_parser("next")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--prefiltered", action="store_true",
                   help="读 prefilter_results.jsonl, 提示排除 reject 的 session")
    p = sub.add_parser("claim")
    p.add_argument("--session", required=True)
    p.add_argument("--user", default="")
    p.add_argument("--host", default="")
    p.add_argument("--match", default="")
    p.add_argument("--domain", default="")
    p.add_argument("--note", default="")
    p = sub.add_parser("mark")
    p.add_argument("--session", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--case-id", dest="case_id", default="")
    p.add_argument("--note", default="")
    p = sub.add_parser("refresh")
    p.add_argument("--json", required=True)
    p = sub.add_parser("seed")
    p.add_argument("--jsonl", required=True)
    p = sub.add_parser("scansync",
                       help="管理任务: 输出 .75 上最新扫描的统计命令块 (shard A 每日巡检用)")
    p = sub.add_parser("prefilter")
    p.add_argument("--candidates", help="candidates TSV (跑 trace_prefilter.py)")
    p.add_argument("--min-mc", type=int, default=30)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--apply", action="store_true", help="写回台账 (默认 dry-run)")
    a = ap.parse_args()
    if a.shard:
        _set_shard(a.shard)
    return {"stats": cmd_stats, "next": cmd_next, "claim": cmd_claim,
            "mark": cmd_mark, "refresh": cmd_refresh, "seed": cmd_seed,
            "scansync": cmd_scansync, "prefilter": cmd_prefilter}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())

