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
LEDGER = os.path.join(HERE, "trace_ledger.tsv")
STATS = os.path.join(HERE, "summary_stats.json")

COLS = ["session_file", "user", "host", "match_count", "domain", "status",
        "case_id", "updated_at", "note"]
VALID_STATUS = ("claimed", "deepread", "case", "parked")
COVERED = ("case",)                          # 计入"已覆盖"
TOUCHED = ("claimed", "deepread", "case", "parked")   # 计入"已动过"


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def load():
    rows = []
    if not os.path.exists(LEDGER):
        return rows
    with open(LEDGER, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            parts += [""] * (len(COLS) - len(parts))
            if parts[0] == COLS[0]:      # 容忍误写入的表头行
                continue
            rows.append(dict(zip(COLS, parts[:len(COLS)])))
    return rows


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
    """分母 = 候选池规模（默认 match_count>=300，可用 stats.target_mc 覆盖）"""
    mc = int(stats.get("target_mc", 300))
    for k in ("mc%d" % mc, "mc300", "sessions"):
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
    print("trace 覆盖率 %s %5.1f%%   covered=%d / target=%d (mc>=%d)"
          % (bar(pct), pct, len(covered), target, mc))
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
    return (
        '<h2>二、trace 覆盖率（进度条）</h2>\n'
        '<div class="kpis">\n'
        '<div class="kpi"><div class="n">%.1f%%</div><div class="l">已交付 / 候选池（mc&ge;%d）</div></div>\n'
        '<div class="kpi"><div class="n">%d</div><div class="l">已交付 case</div></div>\n'
        '<div class="kpi"><div class="n">%d</div><div class="l">候选池总量</div></div>\n'
        '<div class="kpi"><div class="n">%d</div><div class="l">已动过（含暂缓）</div></div>\n'
        '</div>\n'
        '<div style="background:#e3e8ef;border-radius:6px;height:18px;overflow:hidden">'
        '<div style="width:%.1f%%;height:18px;background:#2c7be5"></div></div>\n'
        '<p style="color:#666;font-size:.8rem">%s · 台账 case %d / deepread %d / parked %d / claimed %d</p>\n'
        '<ul>%s</ul>\n'
        % (pct, mc, len(covered), target, len(touched), pct, delta,
           by.get("case", 0), by.get("deepread", 0), by.get("parked", 0),
           by.get("claimed", 0), dom_html or "<li>—</li>"))
def cmd_next(args):
    used = [r["session_file"] for r in load() if r["session_file"]]
    st = load_stats()
    mc = int(st.get("target_mc", 300))
    pat = "|".join(used) if used else "__none__"
    print("# 1) 在 .75 上跑（经 eda_flow run_commands）取候选，已排除台账里的 session：")
    print("awk -F'\\t' 'NR>1 && $5+0>=%d && $4 !~ /^(%s)$/ {print $5\"\\t\"$4\"\\t\"$3\"\\t\"$2}' "
          "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv | sort -rn | head -%d"
          % (mc, pat, args.n))
    print("# 2) 选第一条，落台账：")
    print("python3 designflow/trace_ledger.py claim --session <session_file> --user <user> "
          "--host <host> --match <match_count> [--domain <domain>]")
    print("# 3) 出完 case 后结算（这是覆盖率的唯一分子来源）：")
    print("python3 designflow/trace_ledger.py mark --session <session_file> --status case "
          "--case-id <EDA-Eval-DesignFlow-XXX>")
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


def main():
    ap = argparse.ArgumentParser(description="trace ledger + coverage progress")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stats")
    p.add_argument("--bar", action="store_true")
    p.add_argument("--html", action="store_true")
    p = sub.add_parser("next")
    p.add_argument("--n", type=int, default=5)
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
    a = ap.parse_args()
    return {"stats": cmd_stats, "next": cmd_next, "claim": cmd_claim,
            "mark": cmd_mark, "refresh": cmd_refresh, "seed": cmd_seed}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())

