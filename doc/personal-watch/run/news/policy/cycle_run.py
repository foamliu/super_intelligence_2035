#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/policy/cycle_run.py — L1 链「按周期运行」编排 + 稳定运行台账（G2′ ④）
==========================================================================
任务书 §0.0.2 **G2′ ④ = 「连续 N 周稳定运行」（按周期跑预警并与基线对比）**。
本脚本把 L1 链的**固定顺序**（EDA → TAXONOMY → SIGNALS → EVENTS → EARLY_WARNING）封成
**一条命令**，每次运行把**可核验的摘要**（语料规模 / 事件数 / FDR 显著格 / 效果量门槛格 / 产物 sha）
**追加**到 `STABILITY_LOG.md` —— 由此形成**可 git 追溯的运行台账**（"连续运行"的证据）。

⚠️ 纪律（与任务书一致）：
  * **只重跑本线脚本**（写 `news/policy/` 下产物）；🚫 不改任何结论、不改预注册；
  * **顺序固定**（下游依赖上游；`early_warning.py` 需 `EVENTS.csv` 先就绪）；
  * 数字**全部由当次实测解析**得来（🚫 不手填）；解析不到就写 `?`，**不猜**；
  * **可选**：`explore_l2.py`（L2/N4 探索性）**仅当 numpy/scipy 可用**才跑；缺失则跳过并如实记 `skip(no numpy)`。

用法：
  python3 news/policy/cycle_run.py            # 重跑 L1 链 + 记一行台账
  python3 news/policy/cycle_run.py --record   # 不重跑，只把「当前产物状态」记一行（补记/自检）
  python3 news/policy/cycle_run.py --with-l2  # 额外重跑 explore_l2.py（需 numpy/scipy）
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_MD = os.path.join(HERE, "STABILITY_LOG.md")
EVENTS_CSV = os.path.join(HERE, "EVENTS.csv")
EXPLORE_CSV = os.path.join(HERE, "explore.csv")
EDA_MD = os.path.join(HERE, "EDA.md")
EW_MD = os.path.join(HERE, "EARLY_WARNING.md")

# L1 链固定顺序（下游依赖上游）
L1_STEPS = ["eda.py", "taxonomy.py", "signals.py", "extract_events.py", "early_warning.py"]


def sha16(path: str) -> str:
    if not os.path.exists(path):
        return "-"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def run_step(name: str) -> tuple[int, str]:
    """跑一个链步骤，返回 (exit_code, stdout+stderr)。"""
    p = os.path.join(HERE, name)
    try:
        r = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=1800)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:  # noqa: BLE001
        return 1, f"[cycle_run] ERROR running {name}: {e}"


def parse_corpus(eda_text: str) -> tuple[str, str]:
    """从 eda 输出 / EDA.md 取 (条数, 天数)。兼容两种格式：
       * `eda.py` stdout：`n=806509, days=1627, ...`
       * `EDA.md` §0   ：`条目总数：**806509** ｜ 覆盖天数：**1627** ｜ ...`
    """
    m = re.search(r"n=(\d+),\s*days=(\d+)", eda_text)
    if m:
        return (m.group(1), m.group(2))
    m = re.search(r"条目总数：\*\*(\d+)\*\*.*?覆盖天数：\*\*(\d+)\*\*", eda_text)
    return (m.group(1), m.group(2)) if m else ("?", "?")


def parse_events(ev_text: str) -> str:
    m = re.search(r"events=(\d+)", ev_text)
    return m.group(1) if m else "?"


def parse_ew(path: str) -> tuple[str, str]:
    """从 EARLY_WARNING.md 取 (q<0.05 格数, 效果量门槛格数)。"""
    if not os.path.exists(path):
        return ("?", "?")
    txt = open(path, encoding="utf-8").read()
    q = re.search(r"BH 校正后\s*`q<0\.05`\*\*：\*\*(\d+)\*\*", txt)
    gate = re.search(r"→\s*\*\*(\d+)\*\*\s*/\s*45\s*格判为", txt)
    return (q.group(1) if q else "?", gate.group(1) if gate else "?")


def record_row(note: str, corpus: tuple[str, str], events: str, ew: tuple[str, str],
               l2_state: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    days, recs = corpus[1], corpus[0]
    row = (f"| {now} | {days} | {recs} | {events} | {ew[0]} | {ew[1]} | "
           f"`{sha16(EVENTS_CSV)}` | `{sha16(EXPLORE_CSV)}` | {l2_state} | {note} |\n")
    header = ("# STABILITY_LOG — L1 链「按周期运行」台账（G2′ ④）\n\n"
              "> 由 `news/policy/cycle_run.py` **自动追加**。**每次运行 = 一行**；"
              "**连续多行 = 「连续 N 周稳定运行」的证据**（可 git 追溯）。\n"
              "> 🚫 不改任何结论；数字**由当次实测解析**（解析不到写 `?`，不猜）。\n"
              "> **列**：语料天/条 = 事件库所用语料；事件数 = `EVENTS.csv` 行数；"
              "**q<0.05 格 / 效果量门槛格** = `EARLY_WARNING.md` §4.2（分母恒 45）；"
              "sha = 产物前 16 位（复现核对）；L2 = `explore_l2.py` 状态。\n\n"
              "| 时间 | 语料天 | 语料条 | 事件数 | q<0.05 格 | 效果量门槛格 | EVENTS.sha16 | explore.sha16 | L2 | 备注 |\n"
              "|:--|--:|--:|--:|--:|--:|:--|:--|:--|:--|\n")
    if not os.path.exists(LOG_MD):
        with open(LOG_MD, "w", encoding="utf-8") as f:
            f.write(header)
    with open(LOG_MD, "a", encoding="utf-8") as f:
        f.write(row)
    print(f"[cycle] logged: days={days} recs={recs} events={events} "
          f"q<0.05={ew[0]} gate={ew[1]} l2={l2_state}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true", help="不重跑，只记当前产物状态")
    ap.add_argument("--with-l2", action="store_true", help="额外重跑 explore_l2.py（需 numpy/scipy）")
    args = ap.parse_args()

    eda_text = ev_text = ""
    note = ""

    if args.record:
        note = "record-only(补记/自检)"
    else:
        for step in L1_STEPS:
            rc, out = run_step(step)
            print(f"[cycle] {step} rc={rc}")
            if step == "eda.py":
                eda_text = out
            elif step == "extract_events.py":
                ev_text = out
            if rc != 0:
                note += f"⚠️{step}:rc{rc} "
        note = note or "L1 链按序重跑 OK"

    # 语料规模：优先用 eda 输出；否则回退解析 EDA.md 文本
    corpus = parse_corpus(eda_text)
    if corpus[0] == "?":
        corpus = parse_corpus(open(EDA_MD, encoding="utf-8").read()) if os.path.exists(EDA_MD) else ("?", "?")
    events = parse_events(ev_text)
    if events == "?":
        txt = open(os.path.join(HERE, "EVENTS.md"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "EVENTS.md")) else ""
        m = re.search(r"事件总数：\*\*(\d+)\*\*", txt)
        events = m.group(1) if m else "?"
    ew = parse_ew(EW_MD)

    # L2（可选）
    l2_state = "not-requested"
    if args.with_l2:
        try:
            import numpy  # noqa: F401
            import scipy  # noqa: F401
            rc, _ = run_step("explore_l2.py")
            l2_state = "ok" if rc == 0 else f"rc{rc}"
        except Exception:  # noqa: BLE001
            l2_state = "skip(no numpy)"

    record_row(note, corpus, events, ew, l2_state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
