#!/usr/bin/env python3
"""adaptive_concurrency.py — 评测并发「放量 / 回退」控制器（429 反馈 + 长鑫工作时段）

用户令（2026-11-15）原话：
  「harness：趁周末并发可以开的高一些。评测是否可以有些放量和回退机制。
    长鑫工作时间是 8:30-17:30，工作时间内如果遇到 429 就回退减少并发；
    工作时间之外如果一段时间没有 429 就增加并发。」

策略（环境变量可覆盖）：
  * 时段（Asia/Shanghai）：work = 周一~周五 08:30–17:30；off = 其余（含整个周末）
  * 上限：work 4 / off 10（周末与夜间更激进，白天保守）
  * 升：连续 CLEAN_MIN=20min 无 429 且距上次调整 ≥ DWELL_MIN=10min ⇒ +1（不超上限）
  * 降：任何 429 ⇒ 立即减半（向下取整，最低 1），并进入 COOLDOWN_MIN=20min 冷却
  * off→work 切换时若 current 超过工作日上限 ⇒ 直接压到上限

状态/事件落 `run/harness/manifests/`（根 .gitignore 已忽略，属机器运行时状态）。

用法：
  python3 adaptive_concurrency.py status [--json]
  python3 adaptive_concurrency.py next            # 只读：现在应该用几并发
  python3 adaptive_concurrency.py tick            # 按策略推进并落盘
  python3 adaptive_concurrency.py record --event 429 --count 3
  python3 adaptive_concurrency.py record --event ok
  python3 adaptive_concurrency.py scan-log traces/xxx.log [--record]
  python3 adaptive_concurrency.py reset --to 6
  N=$(python3 adaptive_concurrency.py next --quiet)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CST = timezone(timedelta(hours=8))          # 中国无夏令时，固定 +08:00
HERE = Path(__file__).resolve().parent      # run/harness
DEFAULT_STATE = HERE / "manifests" / "adaptive_concurrency_state.json"
DEFAULT_EVENTS = HERE / "manifests" / "adaptive_concurrency_events.jsonl"


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "").strip() or default)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, "").strip() or default)
    except ValueError:
        return default


# ---- 策略参数（环境变量可覆盖） -------------------------------------------
WORK_START = os.environ.get("HARNESS_WORK_START", "08:30").strip()   # HH:MM
WORK_END = os.environ.get("HARNESS_WORK_END", "17:30").strip()
MIN_N = _env_int("HARNESS_MIN_CONCURRENCY", 1)
WORK_CAP = _env_int("HARNESS_WORK_CAP", 4)           # 工作时间内上限
OFF_CAP = _env_int("HARNESS_OFF_CAP", 10)            # 工作时间外（含周末）上限
WORK_START_N = _env_int("HARNESS_WORK_START_N", 3)   # 工作日首次进入工作时段
OFF_START_N = _env_int("HARNESS_OFF_START_N", 6)     # 工作日夜间起步
WEEKEND_START_N = _env_int("HARNESS_WEEKEND_START_N", 8)  # 周末起步（用户：周末可开高）
CLEAN_MIN = _env_float("HARNESS_CLEAN_MIN", 20.0)    # 无 429 多久才允许 +1
COOLDOWN_MIN = _env_float("HARNESS_COOLDOWN_MIN", 20.0)  # 429 后多久内禁止加
DWELL_MIN = _env_float("HARNESS_DWELL_MIN", 10.0)    # 两次调整最小间隔

QUOTA_RE = re.compile(
    r"(\b429\b|too\s*many\s*requests|rate[\s_-]?limit|额度已用完|Token额度|quota[ _-]?exhausted)",
    re.IGNORECASE,
)

# ---- 时间工具 -------------------------------------------------------------

def now_cst() -> datetime:
    return datetime.now(CST)


def parse_dt(value: str | None) -> datetime:
    """解析 --now；无时区按 +08:00 解释；兼容 +0800 / +08:00 / Z。"""
    if not value:
        return now_cst()
    s = value.strip().replace("Z", "+00:00")
    # Python 3.10 的 fromisoformat 不接受 +0800（无冒号），统一补成 +08:00
    s = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", s)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CST)
    return dt.astimezone(CST)


def _hhmm_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def mode_of(dt: datetime) -> str:
    """work = 周一~周五 [WORK_START, WORK_END)；其余一律 off。"""
    if dt.weekday() >= 5:            # 5=Sat, 6=Sun
        return "off"
    mins = dt.hour * 60 + dt.minute
    if _hhmm_minutes(WORK_START) <= mins < _hhmm_minutes(WORK_END):
        return "work"
    return "off"


def cap_of(mode: str) -> int:
    return WORK_CAP if mode == "work" else OFF_CAP


def start_n_of(dt: datetime, mode: str) -> int:
    if mode == "work":
        return WORK_START_N
    return WEEKEND_START_N if dt.weekday() >= 5 else OFF_START_N


def _ts(dt: datetime | None) -> str | None:
    return dt.astimezone(CST).isoformat(timespec="seconds") if dt else None


def _from_ts(value) -> datetime | None:
    if not value:
        return None
    try:
        return parse_dt(str(value))
    except ValueError:
        return None


# ---- 状态读写 -------------------------------------------------------------

def new_state(dt: datetime, mode: str) -> dict:
    n = max(MIN_N, min(start_n_of(dt, mode), cap_of(mode)))
    return {
        "version": 1,
        "current": n,
        "mode": mode,
        "last_change": _ts(dt),
        "last_429": None,
        "last_ok": None,
        "429_total": 0,
        "updated": _ts(dt),
    }


def load_state(path: Path | str | None = None, dt: datetime | None = None) -> dict:
    p = Path(path) if path else DEFAULT_STATE
    dt = dt or now_cst()
    if p.exists():
        try:
            # utf-8-sig：兼容 Windows/记事本写入的 BOM
            st = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            st = None
            try:                       # 坏档留证，然后按新状态自愈
                p.replace(p.with_suffix(p.suffix + ".corrupt"))
            except Exception:
                pass
        if isinstance(st, dict) and isinstance(st.get("current"), int):
            st.setdefault("mode", mode_of(dt))
            st.setdefault("last_change", _ts(dt))
            st.setdefault("last_429", None)
            st.setdefault("last_ok", None)
            st.setdefault("429_total", 0)
            return st
        st = new_state(dt, mode_of(dt))
        save_state(st, p)
        return st
    return new_state(dt, mode_of(dt))


def ensure_state(path: Path | str | None = None, dt: datetime | None = None) -> dict:
    """载入状态；若状态文件不存在则先落盘一份基线（避免每次调用都重置 dwell）。"""
    st = load_state(path, dt)
    p = Path(path) if path else DEFAULT_STATE
    if not p.exists():
        save_state(st, p)
    return st


def save_state(st: dict, path: Path | str | None = None) -> None:
    p = Path(path) if path else DEFAULT_STATE
    p.parent.mkdir(parents=True, exist_ok=True)
    st["updated"] = _ts(now_cst())
    p.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_event(event: dict, path: Path | str | None = None) -> None:
    p = Path(path) if path else DEFAULT_EVENTS
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


# ---- 策略核心 -------------------------------------------------------------

def decide(st: dict, dt: datetime) -> tuple[int, str]:
    """返回 (目标并发, 原因)。不落盘。"""
    mode = mode_of(dt)
    cap = cap_of(mode)
    cur = int(st.get("current", MIN_N))
    last_429 = _from_ts(st.get("last_429"))
    last_change = _from_ts(st.get("last_change"))

    # 1) off→work 切换：压到工作时段上限
    if mode == "work" and cur > cap:
        return cap, f"clamp_to_work_cap({cur}->{cap})"

    # 2) 429 冷却期内只降不升
    if last_429 and (dt - last_429) < timedelta(minutes=COOLDOWN_MIN):
        left = COOLDOWN_MIN - (dt - last_429).total_seconds() / 60.0
        return max(MIN_N, min(cur, cap)), f"cooldown_after_429({left:.0f}m_left)"

    # 3) 两次调整最小间隔（防抖）
    if last_change and (dt - last_change) < timedelta(minutes=DWELL_MIN):
        left = DWELL_MIN - (dt - last_change).total_seconds() / 60.0
        return max(MIN_N, min(cur, cap)), f"dwell({left:.0f}m_left)"

    # 4) 连续 CLEAN_MIN 无 429 ⇒ 升一级
    ref = last_429 or last_change
    quiet_min = (dt - ref).total_seconds() / 60.0 if ref else 1e9
    if cur < cap and quiet_min >= CLEAN_MIN:
        return min(cap, cur + 1), f"clean_ramp(quiet={quiet_min:.0f}m)"

    return max(MIN_N, min(cur, cap)), f"hold(quiet={quiet_min:.0f}m,cap={cap})"


def tick(st: dict, dt: datetime | None = None, state_path=None, quiet: bool = False) -> dict:
    """按策略推进：必要时写入新 current；返回更新后的 state。"""
    dt = dt or now_cst()
    target, reason = decide(st, dt)
    st["mode"] = mode_of(dt)
    if target != int(st.get("current", MIN_N)):
        if not quiet:
            print(f"[adaptive] {st['current']} -> {target}  ({reason})", file=sys.stderr)
        st["current"] = target
        st["last_change"] = _ts(dt)
        save_state(st, state_path)
    return st


def record(event: str, dt: datetime | None = None, count: int = 1,
           state_path=None, events_path=None, note: str = "") -> dict:
    dt = dt or now_cst()
    st = ensure_state(state_path, dt)
    event = event.lower()
    if event in ("429", "quota", "rate_limit"):
        st["last_429"] = _ts(dt)
        st["429_total"] = int(st.get("429_total", 0)) + max(1, count)
        old = int(st.get("current", MIN_N))
        st["current"] = max(MIN_N, old // 2)
        st["last_change"] = _ts(dt)
        st["mode"] = mode_of(dt)
        save_state(st, state_path)
        append_event({"ts": _ts(dt), "event": "429", "count": count, "old": old,
                      "new": st["current"], "note": note}, events_path)
    else:
        st["last_ok"] = _ts(dt)
        save_state(st, state_path)
        append_event({"ts": _ts(dt), "event": "ok", "note": note}, events_path)
    return st


def scan_log(path: Path | str) -> dict:
    """统计 harbor 日志里的 429 / quota 命中行。"""
    p = Path(path)
    hits = 0
    samples: list[str] = []
    if p.exists():
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if QUOTA_RE.search(line):
                    hits += 1
                    if len(samples) < 5:
                        samples.append(line.rstrip()[:240])
    return {"file": str(p), "hits": hits, "samples": samples}


# ---- 给其他脚本调用的便捷接口 ---------------------------------------------

def auto_next(state_path=None, quiet: bool = False) -> int:
    """读状态 → 按策略 tick → 返回本轮应使用的并发数。"""
    st = tick(ensure_state(state_path), state_path=state_path, quiet=quiet)
    return int(st["current"])


def record_from_text(text: str, state_path=None, events_path=None,
                     note: str = "", quiet: bool = False) -> dict:
    """从一段日志文本判断有没有 429，并据此记录升/降。"""
    hits = sum(1 for line in text.splitlines() if QUOTA_RE.search(line))
    if hits:
        st = record("429", count=hits, state_path=state_path,
                    events_path=events_path, note=note)
        if not quiet:
            print(f"[adaptive] 429 x{hits} -> n_concurrent={st['current']}", file=sys.stderr)
        return st
    return record("ok", state_path=state_path, events_path=events_path, note=note)


# ---- CLI ------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="评测并发自适应升降（429 + 长鑫工作时段）")
    ap.add_argument("--state", default=str(DEFAULT_STATE), help="状态文件路径")
    ap.add_argument("--events", default=str(DEFAULT_EVENTS), help="事件 JSONL 路径")
    ap.add_argument("--now", default=None, help="注入当前时间（ISO8601，测试用）")
    sub = ap.add_subparsers(dest="cmd")

    p_status = sub.add_parser("status", help="打印状态")
    p_status.add_argument("--json", action="store_true")

    p_next = sub.add_parser("next", help="只读：现在应该用几并发")
    p_next.add_argument("--json", action="store_true")
    p_next.add_argument("--quiet", action="store_true")

    p_tick = sub.add_parser("tick", help="按策略推进并落盘")
    p_tick.add_argument("--quiet", action="store_true")

    p_rec = sub.add_parser("record", help="记录一次 429 / ok")
    p_rec.add_argument("--event", required=True,
                       choices=["429", "ok", "quota", "rate_limit"])
    p_rec.add_argument("--count", type=int, default=1)
    p_rec.add_argument("--note", default="")

    p_scan = sub.add_parser("scan-log", help="扫描 harbor 日志中的 429")
    p_scan.add_argument("log")
    p_scan.add_argument("--record", action="store_true", help="按扫描结果记录一次事件")

    p_reset = sub.add_parser("reset", help="强制设定当前并发")
    p_reset.add_argument("--to", type=int, required=True)

    args = ap.parse_args(argv)
    dt = parse_dt(args.now)
    cmd = args.cmd or "status"
    state_path = Path(args.state)
    events_path = Path(args.events)

    if cmd == "status":
        st = ensure_state(state_path, dt)
        mode = mode_of(dt)
        target, reason = decide(st, dt)
        payload = {
            "now": _ts(dt), "mode": mode, "current": st["current"],
            "cap": cap_of(mode), "next_target": target, "reason": reason,
            "last_429": st.get("last_429"), "429_total": st.get("429_total", 0),
            "work_window": f"{WORK_START}-{WORK_END} Mon-Fri",
            "caps": {"work": WORK_CAP, "off": OFF_CAP},
            "state_file": str(state_path),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"now={payload['now']}  mode={mode}  current={st['current']}/{cap_of(mode)}"
                  f"  next={target}  ({reason})")
            print(f"最后 429: {st.get('last_429') or '无'}   累计 429={payload['429_total']}")
            print(f"策略: work {WORK_CAP} / off {OFF_CAP}; clean={CLEAN_MIN:.0f}m; "
                  f"cooldown={COOLDOWN_MIN:.0f}m; dwell={DWELL_MIN:.0f}m")
        return 0

    if cmd == "next":
        st = ensure_state(state_path, dt)
        target, reason = decide(st, dt)
        if args.quiet:
            print(target)
        elif args.json:
            print(json.dumps({"n_concurrent": target, "reason": reason,
                              "mode": mode_of(dt), "current": st["current"]},
                             ensure_ascii=False))
        else:
            print(f"n_concurrent={target}  mode={mode_of(dt)}  ({reason})")
        return 0

    if cmd == "tick":
        st = tick(ensure_state(state_path, dt), dt, state_path=state_path, quiet=args.quiet)
        if not args.quiet:
            print(st["current"])
        return 0

    if cmd == "record":
        st = record(args.event, dt, args.count, state_path, events_path, args.note)
        print(json.dumps(st, ensure_ascii=False))
        return 0

    if cmd == "scan-log":
        res = scan_log(args.log)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        if args.record:
            text = Path(args.log).read_text(errors="replace") if Path(args.log).exists() else ""
            st = record_from_text(text, state_path, events_path, note=str(args.log))
            print(f"[adaptive] current={st['current']}")
        return 0

    if cmd == "reset":
        st = load_state(state_path, dt)
        st["current"] = max(MIN_N, min(args.to, cap_of(mode_of(dt))))
        st["last_change"] = _ts(dt)
        st["mode"] = mode_of(dt)
        save_state(st, state_path)
        print(json.dumps(st, ensure_ascii=False))
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())



