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

# ---- shard 支持：按 domain 分片，每个 shard 独立 ledger + keywords 过滤候选 ----
# summary.tsv 列: ip host user session_file match_count keywords tools
# keywords 列（$6，格式 "tool:count;tool:count"）做 domain 代理过滤。
# 注意：$7(tools) 对部分 session 为空（如 verilog:4237 但 tools=""），r309 修前
# 过滤 $7 会漏掉 ~346 个 mc>=15 的 verilog/rtl/sdc session（dedup 294→2381，8x）。
# 故 r309 起过滤改用 $6（authoritative），$7 仅作冗余参考。
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
# per-shard mc 阈值
# 2026-11-11 用户令：全面下调到 mc>=10（原 A=15 / B,C,D=30）。
# 依据：2026-11-05 全量扫描 summary_1105.tsv 实测（5822 数据行 -> 2560 去重 session）：
#   未动过(可做)  mc>=30 → mc>=10：119 → 381（+262，3.2x）；分 shard A 109→318, B 5→39,
#   C 102→332, D 70→252。复算：trace_ledger.py mc-matrix --src designflow/summary_1105.tsv
# 可被 summary_stats.json 的 shard_mc 字段覆盖。
SHARD_MC = {"A": 10, "B": 10, "C": 10, "D": 10}
# 全局默认阈值（无 --shard 时用；也是 refresh 时写 mc<N> 的键）
DEFAULT_MC = 10

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
    """分母 = 候选池规模。严格按 target_mc 取对应 key。

    2026-11-11 修复：旧实现把候选 key 列表写死成 ("mc30","mc100",...)，导致
    target_mc 形同虚设 —— 设 target_mc=10 时仍会 fallback 到 mc30，分母永远是
    mc>=30 的口径（这正是日报 34.4% 与"池枯竭"互相打架的根因）。
    现在：显式接受 mc<N> / mcN / mc100 / mc300 / sessions 按顺序精确回退，
    但会打印实际命中的 key，绝不静默换成别档口径。
    返回 (target, mc, key_hit)。
    """
    mc = int(stats.get("target_mc", DEFAULT_MC))
    # 只接受与 target_mc 同档或更宽松的显式快照 key，按"同档优先"顺序
    cand_keys = ["mc%d" % mc, "mc_%d" % mc, "mc%03d" % mc,
                 "mc100", "mc300", "sessions"]
    seen = set()
    for k in cand_keys:
        if k in seen:
            continue
        seen.add(k)
        if stats.get(k):
            return int(stats[k]), mc, k
    return int(stats.get("sessions", 0) or 0), mc, "sessions"


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

def _pool_members(st):
    """返回池内 session slug 集合（来自 mc_matrix.src / scan_snapshot），用于把
    覆盖率分子限制在同一底池内 —— 否则会把快照之外的旧 session 算进分子，
    导致"池 1929 - 已动过 2347"这类自相矛盾的数字。"""
    src = st.get("mc_matrix", {}).get("src") if isinstance(st.get("mc_matrix"), dict) else None
    src = src or st.get("scan_snapshot")
    if not src:
        return None
    p = src if os.path.isabs(src) else os.path.join(HERE, src)
    if not os.path.exists(p):
        p = os.path.join(os.path.dirname(HERE), src) if not os.path.isabs(src) else p
    if not os.path.exists(p):
        return None
    best, _, _ = _dedup_scan(p)
    return set(best)


def cmd_stats(args):
    rows = load()
    st = load_stats()
    target, mc, key_hit = target_of(st)
    pool = _pool_members(st)

    def _in_pool(r):
        return pool is None or _norm_sid(r["session_file"]) in pool

    covered = [r for r in rows if r["status"] in COVERED and _in_pool(r)]
    touched = [r for r in rows if r["status"] in TOUCHED and _in_pool(r)]
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    pct = (100.0 * len(covered) / target) if target else 0.0
    if target:
        print("trace 覆盖率 %s %5.1f%%   covered=%d / target=%d (mc>=%d, key=%s%s)"
              % (bar(pct), pct, len(covered), target, mc, key_hit,
                 "，已限定池内" if pool else ""))
    else:
        print("trace 覆盖率：候选池未知（先 refresh：sessions/mc10/mc30/mc100）；covered=%d"
              % len(covered))
    print("  已动过 %d：case %d · deepread %d · parked %d · claimed %d（全台账）"
          % (len(touched), by.get("case", 0), by.get("deepread", 0),
             by.get("parked", 0), by.get("claimed", 0)))
    if target:
        # 2026-11-11：旧实现用 len(touched) 直接减，但 4 个 shard ledger 有重复行
        # （同一 session 被多个 shard park 过），会把"剩余可做"算成 0，误导成"池已枯竭"。
        # 现在按去重后的 session slug 计数。
        touched_sids = {_norm_sid(r["session_file"]) for r in touched if r["session_file"]}
        print("  剩余可做 ≈ %d（池 %d - 池内去重已动过 %d）"
              % (max(0, target - len(touched_sids)), target, len(touched_sids)))
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
    target, mc, key_hit = target_of(st)
    pool = _pool_members(st)

    def _in_pool(r):
        return pool is None or _norm_sid(r["session_file"]) in pool

    covered = [r for r in rows if r["status"] in COVERED and _in_pool(r)]
    touched = [r for r in rows if r["status"] in TOUCHED and _in_pool(r)]
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
    # 2026-11-11：把分母实际命中的快照 key 显式写进页面，杜绝"分母悄悄换档"。
    src_txt = ("分母口径 = <code>summary_stats.json:%s</code>（target_mc=%d）" % (key_hit, mc)
               if target else "分母口径 = 未知")
    return (
        '<h3>trace 覆盖率进度条（候选池 mc&ge;%d，合并 4 shard ledger）</h3>\n'
        '<p style="color:#666;font-size:.78rem">%s</p>\n'
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
        % (mc, src_txt, pct_txt, mc, len(covered), pool_txt, len(touched), width, delta,
           by.get("case", 0), by.get("seeded", 0), by.get("deepread", 0),
           by.get("parked", 0), by.get("claimed", 0), dom_html or "<li>—</li>"))
def cmd_next(args):
    # 规范化：台账存 bare 形式或带 .messages.json 后缀混存，summary.tsv 统一带后缀。
    # strip 后缀再做 anchor 匹配，避免 $-anchor 漏放行已用 session。
    used = [r["session_file"].replace(".messages.json", "")
            for r in load() if r["session_file"]]
    st = load_stats()
    # per-shard mc 阈值: summary_stats.json.shard_mc → SHARD_MC → target_mc → DEFAULT_MC
    shard_mc_cfg = st.get("shard_mc", {}) if isinstance(st.get("shard_mc"), dict) else {}
    if _shard and _shard in SHARD_MC:
        mc = int(shard_mc_cfg.get(_shard, SHARD_MC[_shard]))
    else:
        mc = int(st.get("target_mc", DEFAULT_MC))
    # 扫描路径: 优先 summary_stats.json.scan_path, 否则用 .75 上最新扫描目录
    scan_tsv = st.get("scan_path", "")
    if not scan_tsv:
        scan_tsv = "/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv"
    pat = "|".join(used) if used else "__none__"
    # shard tools 过滤（$7 = tools 列）
    tool_filter = ""
    if _shard and _shard in SHARD_DOMAINS:
        tools_re = SHARD_DOMAINS[_shard][1]
        tool_filter = " && $6 ~ /%s/" % tools_re
    print("# 1) 在 .75 上跑（经 eda_flow run_commands）取候选，已排除台账里的 session%s：" % ("，按 shard %s keywords($6) 过滤" % _shard if _shard else ""))
    print("# (sub(/\\.messages\\.json$/,\"\",$4) 规范化后做 anchor 匹配)")
    print("# 候选池 mc>=%d%s (11/06: shard A 放宽过滤词+降阈值; **2026-11-11 用户令: 全线降到 mc>=10**)" % (mc, " [shard %s 专属阈值]" % _shard if _shard and _shard in SHARD_MC and mc != DEFAULT_MC else ""))
    print("# 扫描源: %s" % scan_tsv)
    print("# r309: 过滤改用 $6(keywords) 而非 $7(tools)；$7 对 ~346 verilog session 为空，旧 $7 过滤漏候选 8x (dedup 294->2381)")
    print("awk -F'\\t' 'NR>1 && $5+0>=%d {sub(/\\.messages\\.json$/,\"\",$4); $4 !~ /^(%s)$/%s {print $5\"\\t\"$4\"\\t\"$3\"\\t\"$2\"\\t\"$6}' "
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
    # 2026-11-11 用户令：全线下调到 mc>=10，故各档都要统计，供 refresh 写 mc10/mc15/mc20/mc30
    for m in (10, 15, 20, 30):
        if m == 30:
            continue
        print("echo \"mc%d: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=%d {print $4}' | sort -u | wc -l)\""
              % (m, m))
        print("echo \"users_mc%d: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=%d {print $3}' | sort -u | wc -l)\""
              % (m, m))
    print("echo \"users_mc30: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=30 {print $3}' | sort -u | wc -l)\"")
    print("# 3) 各 shard 候选池规模 (用当前过滤词 + mc 阈值):")
    for sid in sorted(SHARD_DOMAINS):
        tools_re = SHARD_DOMAINS[sid][1]
        mc = SHARD_MC.get(sid, 30)
        print("echo \"shard_%s_pool_mc%d: $(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=%d && $6 ~ /%s/ {print $4}' | sort -u | wc -l)\""
              % (sid, mc, mc, tools_re))
    print("# 4) 新增 session (旧扫描没有的, 按 target_mc=%d 口径):" % DEFAULT_MC)
    print("echo \"new_sessions: $(comm -13 <(tail -n +2 %s | awk -F'\\t' '$5+0>=%d{print $4}' | sort -u) <(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=%d{print $4}' | sort -u) | wc -l)\""
          % (old_scan, DEFAULT_MC, DEFAULT_MC))
    print("# 5) 各 shard 的新增候选 (旧扫描没有的):")
    for sid in sorted(SHARD_DOMAINS):
        tools_re = SHARD_DOMAINS[sid][1]
        mc = SHARD_MC.get(sid, 30)
        print("echo \"shard_%s_new: $(comm -13 <(tail -n +2 %s | awk -F'\\t' '$5+0>=%d && $6 ~ /%s/{print $4}' | sort -u) <(tail -n +2 $SUMMARY | awk -F'\\t' '$5+0>=%d && $6 ~ /%s/{print $4}' | sort -u) | wc -l)\""
              % (sid, old_scan, mc, tools_re, mc, tools_re))
    print("# 6) 更新 summary_stats.json (把上面的数字填进去):")
    print("#    python3 designflow/trace_ledger.py refresh --json '{\"scan_path\":\"$SCAN_DIR/summary.tsv\",\"mc30\":NNN,...}'")
    print("# 7) daily scan log 增量 (今日新增 trace):")
    print("TODAY=$(date +%%Y%%m%%d)")
    print("echo \"today_log: /home/t0002965/log/eda_trace_$TODAY.log\"")
    print("echo \"today_sessions: $(grep -c '^10\\.' /home/t0002965/log/eda_trace_$TODAY.log 2>/dev/null)\"")
    print("# 旧扫描: %s" % old_scan)
    return 0


def _norm_sid(s):
    """规范化 session 标识 → **纯 slug**（如 1792044811256_a7ied）。

    同一 slug 会在多个 user 目录 / 多台机器上重复出现（实测 2700 个 slug 里有 2 个
    被两个不同 user 使用），所以必须用 slug 而不是 user+slug 做去重键，否则会多算。
    """
    base = s.replace("\\", "/").rstrip("/").split("/")[-1]
    for suf in (".messages.archive.json", ".messages.archive",
                ".messages.json", ".archive.json", ".json"):
        if base.endswith(suf):
            return base[: -len(suf)]
    return base


def _is_header(p):
    """判断 summary.tsv 的一行是否为表头（列名，而非数据）。"""
    return bool(p) and p[0] in ("ip", "session_file", "match_count", "#")


def _dedup_scan(src):
    """读 summary.tsv → {sid: {mc, user, host, kw, ip}}，同 session 取最大 mc。

    注意：summary.tsv 里同一 session 会在**很多台机器**上各出现一行（同一个 cline
    session 目录被多 host 挂载/同步），所以必须先按 session 去重再统计，否则数字会
    虚高（实测 5822 数据行 → 2701 个去重 session）。表头行必须跳过，否则
    "session_file" 会被当成一个 session 混进统计。
    """
    best = {}
    n_rows = 0
    n_hdr = 0
    with open(src, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            if _is_header(p):
                n_hdr += 1
                continue
            if len(p) < 6:
                continue
            n_rows += 1
            host, user, sf, mcs, kws = p[1], p[2], p[3], p[4], p[5]
            sid = _norm_sid(sf)
            try:
                mc = int(float(mcs))
            except (TypeError, ValueError):
                continue
            if sid not in best or mc > best[sid]["mc"]:
                best[sid] = {"mc": mc, "user": user, "host": host,
                             "kw": kws, "ip": p[0]}
    return best, n_rows, n_hdr


def cmd_mcmartix(args):
    """2026-11-11 用户令：mc 阈值全线下调到 mc>=10 的评估工具（纯本机，可复算）。

    读一份 summary.tsv（列: ip host user session_file match_count keywords tools），
    按 session 去重（同一 session 可能在多台机重复出现，取最大 match_count），
    然后对每个阈值 m 统计：池总量 / 已动过(4 shard ledger) / 未动过(=真正可做)。
    可选 --shard X 再按该 shard 的 keywords 过滤词切分。

    用途：
      1) 复核"降到 mc>=10 到底能多出多少可做候选"；
      2) 生成可直接喂给 `trace_ledger.py refresh --json` 的 mc10/mc15/mc20/mc30 数字；
      3) 生成 candidates_mc<N>.tsv 候选清单（--emit-candidates）。
    """
    import re
    src = args.src
    if not os.path.exists(src):
        print("ERROR: 扫描快照不存在: %s" % src)
        return 2

    # 台账：把已动过的 session 全部收进来（4 shard + 老合并台账）
    touched = {}
    for s in ("A", "B", "C", "D"):
        p = os.path.join(HERE, "trace_ledger_%s.tsv" % s)
        for r in _load_file(p):
            if r["session_file"]:
                touched[_norm_sid(r["session_file"])] = r["status"]
    for r in _load_file(os.path.join(HERE, "trace_ledger.tsv")):
        if r["session_file"]:
            touched.setdefault(_norm_sid(r["session_file"]), r["status"])

    # 扫描快照：session 去重，取最大 mc（和 keywords 一起保留）
    best, n_rows, n_hdr = _dedup_scan(src)

    # 可选：按 shard 的 keywords 过滤词切分
    kw_pat = None
    if args.shard:
        if args.shard not in SHARD_DOMAINS:
            print("ERROR: 未知 shard %s" % args.shard)
            return 2
        kw_pat = re.compile(SHARD_DOMAINS[args.shard][1])

    rows = [dict(sid=k, **v) for k, v in best.items()
            if (kw_pat is None or kw_pat.search(v["kw"] or ""))]

    thresholds = [int(x) for x in args.thresholds.split(",") if x.strip()]
    print("# 扫描快照: %s" % src)
    print("# 数据行 = %d（跳过表头 %d 行）→ 去重 session = %d%s"
          % (n_rows, n_hdr, len(rows),
             ("（shard %s keywords 过滤后）" % args.shard) if args.shard else ""))
    print("# 台账已动过 session = %d（case/seeded=%d, parked=%d）"
          % (len(touched),
             sum(1 for v in touched.values() if v in COVERED),
             sum(1 for v in touched.values() if v == "parked")))
    print("")
    print("%-10s %10s %10s %10s" % ("阈值", "池总量", "已动过", "未动过(可做)"))
    print("-" * 44)
    table = {}
    for m in thresholds:
        sel = [r for r in rows if r["mc"] >= m]
        t = sum(1 for r in sel if r["sid"] in touched)
        table[m] = {"pool": len(sel), "touched": t, "fresh": len(sel) - t}
        print("mc>=%-6d %10d %10d %10d" % (m, len(sel), t, len(sel) - t))

    if args.json:
        print("")
        print("# 可直接喂 refresh 的 JSON 片段：")
        obj = {"target_mc": args.target_mc,
               "shard_mc": {s: args.target_mc for s in sorted(SHARD_DOMAINS)},
               "mc_matrix": {("mc%d" % m): table[m] for m in thresholds}}
        for m in thresholds:
            obj["mc%d" % m] = table[m]["pool"]
        print(json.dumps(obj, ensure_ascii=False))

    if args.emit_candidates:
        m = args.emit_candidates_mc
        sel = sorted([r for r in rows if r["mc"] >= m],
                     key=lambda r: -r["mc"])
        out = os.path.join(HERE, "candidates_mc%d.tsv" % m)
        with open(out, "w", encoding="utf-8") as f:
            f.write("ip\tuser\tsession_file\tmatch_count\tkeywords\n")
            for r in sel:
                f.write("%s\t%s\t%s\t%d\t%s\n"
                        % (r["ip"], r["user"], r["sid"], r["mc"], r["kw"]))
        unledgered = sum(1 for r in sel if r["sid"] not in touched)
        print("")
        print("已写出候选清单: %s（%d 行，其中未动过 %d）" % (out, len(sel), unledgered))
    return 0


def cmd_mcguard(args):
    """2026-11-11 用户令守门员：检查 mc>=10 规则是否被破坏（可进 pre-commit / 每轮自检）。

    检查项：
      G1 summary_stats.json: target_mc == 10
      G2 summary_stats.json: shard_mc 全 == 10（A/B/C/D）
      G3 trace_ledger.py: SHARD_MC 全 == 10、DEFAULT_MC == 10
      G4 候选清单 candidates_mc10.tsv 存在，且 min(match_count) >= 10
      G5 任务书 *_TASK*.md 的「选料阈值」不得残留 target_mc=30 / shard_mc 15/30 模板
      G6 覆盖率分母 key 必须是 mc10
    退出码：0 全过；1 有 FAIL。
    """
    import re
    fails = []
    warns = []

    # ---- G1/G2 ----
    st = load_stats()
    if int(st.get("target_mc", -1)) != 10:
        fails.append("G1 summary_stats.target_mc = %r（必须 10）" % st.get("target_mc"))
    shard_mc = st.get("shard_mc", {})
    for s in ("A", "B", "C", "D"):
        v = shard_mc.get(s)
        if v != 10:
            fails.append("G2 summary_stats.shard_mc[%s] = %r（必须 10）" % (s, v))

    # ---- G3 ----
    src = os.path.join(HERE, "trace_ledger.py")
    with open(src, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"^SHARD_MC\s*=\s*(\{[^}]*\})", txt, re.M)
    if not m:
        fails.append("G3 找不到 SHARD_MC 定义")
    else:
        try:
            cfg = json.loads(m.group(1).replace("'", '"'))
        except Exception:
            cfg = {}
        for s in ("A", "B", "C", "D"):
            if cfg.get(s) != 10:
                fails.append("G3 trace_ledger.SHARD_MC[%s] = %r（必须 10）" % (s, cfg.get(s)))
    if not re.search(r"^DEFAULT_MC\s*=\s*10\b", txt, re.M):
        fails.append("G3 trace_ledger.DEFAULT_MC 不是 10")

    # ---- G4 ----
    cand = os.path.join(HERE, "candidates_mc10.tsv")
    if not os.path.exists(cand):
        fails.append("G4 缺 candidates_mc10.tsv")
    else:
        mn = None
        with open(cand, encoding="utf-8") as f:
            f.readline()
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) < 4:
                    continue
                try:
                    v = int(float(p[3]))
                except ValueError:
                    continue
                mn = v if mn is None else min(mn, v)
        if mn is None:
            fails.append("G4 candidates_mc10.tsv 无数据行")
        elif mn < 10:
            fails.append("G4 candidates_mc10.tsv 最小 mc = %d（<10，混入低档候选）" % mn)

    # ---- G5 ----
    bench = os.path.dirname(HERE)
    import glob
    tasks = sorted(glob.glob(os.path.join(bench, "BAIZE_DESIGNFLOW_BENCH_TASK*.md")))
    for t in tasks:
        with open(t, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                # 只抓"可复制执行"的模板行，放过已标注作废/禁止的行
                if '"target_mc":30' in line.replace(" ", "") and "禁止" not in line \
                        and "作废" not in line and "已作废" not in line:
                    fails.append("G5 %s:L%d 残留可执行的 target_mc=30 模板"
                                 % (os.path.basename(t), i))
                if re.search(r'"shard_mc"\s*:\s*\{\s*"A"\s*:\s*15', line) and "作废" not in line:
                    fails.append("G5 %s:L%d 残留 shard_mc A:15 模板"
                                 % (os.path.basename(t), i))

    # ---- G6 ----
    target, mc, key = target_of(st)
    if key != "mc10":
        warns.append("G6 覆盖率分母 key = %s（期望 mc10；可能是 11/09 换池未完成或 key 缺失）" % key)

    print("=== mc>=10 守门员 ===")
    print("target_mc=%s shard_mc=%s 分母key=%s 分母=%s"
          % (st.get("target_mc"), json.dumps(shard_mc, ensure_ascii=False), key, target))
    if fails:
        print("\nFAIL (%d):" % len(fails))
        for x in fails:
            print("  ✗ " + x)
    else:
        print("  ✓ G1-G5 全过")
    for w in warns:
        print("  ! " + w)
    print("\n结果：%s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


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
    p.add_argument("--min-mc", type=int, default=DEFAULT_MC)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--apply", action="store_true", help="写回台账 (默认 dry-run)")
    p = sub.add_parser("mc-matrix",
                       help="2026-11-11 用户令: 按 mc 阈值矩阵统计 池/已动过/未动过 "
                            "(纯本机可复算), 并生成 candidates_mc<N>.tsv")
    p.add_argument("--src", required=True, help="扫描快照 summary.tsv 路径")
    p.add_argument("--thresholds", default="5,10,15,20,30")
    p.add_argument("--target-mc", dest="target_mc", type=int, default=DEFAULT_MC,
                   help="建议 adopt 的阈值 (写进 refresh JSON 的 target_mc/shard_mc)")
    p.add_argument("--json", action="store_true", help="输出可喂 refresh --json 的片段")
    p.add_argument("--emit-candidates", dest="emit_candidates", action="store_true",
                   help="写出 candidates_mc<N>.tsv")
    p.add_argument("--emit-candidates-mc", dest="emit_candidates_mc", type=int,
                   default=DEFAULT_MC)
    p = sub.add_parser("mcguard",
                       help="2026-11-11 守门员: 校验 mc>=10 规则未被破坏 (退出码 0=PASS/1=FAIL)")
    a = ap.parse_args()
    if a.shard:
        _set_shard(a.shard)
    return {"stats": cmd_stats, "next": cmd_next, "claim": cmd_claim,
            "mark": cmd_mark, "refresh": cmd_refresh, "seed": cmd_seed,
            "scansync": cmd_scansync, "prefilter": cmd_prefilter,
            "mc-matrix": cmd_mcmartix, "mcguard": cmd_mcguard}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())

