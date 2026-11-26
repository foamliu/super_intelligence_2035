#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""robot 线 · L3 学情层：错题本 → 知识点画像 + 每日/每周摘要 + 可导出 HTML。

ROADMAP L3 判据：数据落本地、可导出 HTML。
数据来源 = 错题本（host/tools.py 的 wrong_book.json，本地，不上传）。

教育红线（11:10 令）：
  - 报告只统计**自造题**，不含真实学生隐私（姓名/学校/真人照片一律不出现）；
  - 不泄露原题最终答案（画像/摘要只展示「知识点 + 数量 + 时间」，不列答案）。
"""
import json
import os
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(HERE)

# 复用 tools.py 的错题本路径（`ROBOT_WRONG_BOOK` 可覆盖），保证 L2/L3 同一份数据。
import tools  # noqa: E402
LOGS_DIR = os.path.join(ROBOT_DIR, "logs")
# 正样本 = 会话/练习日志（作答次数 + 正确率），与错题本合并出更完整的掌握画像。
# `ROBOT_PRACTICE_LOG` 可覆盖（测试/多租户隔离用）。
PRACTICE_LOG_PATH = os.environ.get(
    "ROBOT_PRACTICE_LOG", os.path.join(LOGS_DIR, "practice_log.json"))

_TS_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d")


def load_wrong_book(path=None) -> list:
    """读取错题本（本地 JSON 列表）。文件缺失/损坏 → 空列表，绝不抛异常。"""
    path = path or tools.WRONG_BOOK_PATH
    return _load_list(path)


def load_practice_log(path=None) -> list:
    """读取练习日志（本地 JSON 列表）。文件缺失/损坏 → 空列表，绝不抛异常。"""
    path = path or PRACTICE_LOG_PATH
    return _load_list(path)


def _load_list(path) -> list:
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001
        return []


def log_practice(question, student_answer="", knowledge="", correct=False,
                 ts=None, path=None) -> dict:
    """记录一次作答（正样本：对/错），追加到本地练习日志并返回该条记录。

    红线：只落本地、不上传；`student_answer` 可留空（日志本身不含答案判据，
    只在掌握画像里聚合成「次数/正确率」，不泄露最终答案）。
    """
    entry = {
        "question": (question or "").strip(),
        "student_answer": (student_answer or "").strip(),
        "knowledge": (knowledge or "").strip() or "未分类",
        "correct": bool(correct),
        "ts": ts or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    path = path or PRACTICE_LOG_PATH
    items = load_practice_log(path)
    items.append(entry)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return entry


def mastery_label(wrong_count: int) -> str:
    """按错题次数给掌握等级（越少越好）。"""
    if wrong_count <= 0:
        return "待练习"
    if wrong_count == 1:
        return "待巩固"
    if wrong_count == 2:
        return "薄弱"
    return "重点突破"


def mastery_from_stats(wrong_count: int, attempt_count: int, correct_count: int) -> str:
    """正样本合并后的掌握等级：错题数 + 作答次数 + 答对数 综合判定。

    - 没练过也没错过 → 待练习
    - 无正样本（attempt_count==0）→ 退化为纯错题口径（mastery_label）
    - 有正样本：错得多 / 正确率低 → 重点突破 / 薄弱；错得少且正确率高 → 待巩固 / 已掌握
    """
    if wrong_count <= 0 and attempt_count <= 0:
        return "待练习"
    if attempt_count <= 0:
        return mastery_label(wrong_count)
    rate = correct_count / attempt_count
    if wrong_count == 0 and rate >= 0.8:
        return "已掌握"
    if wrong_count >= 3 or rate < 0.5:
        return "重点突破"
    if wrong_count >= 2 or rate < 0.6:
        return "薄弱"
    if wrong_count >= 1 or rate < 0.8:
        return "待巩固"
    return "已掌握"


def _day_of(ts) -> str:
    """把错题时间戳归一成 'YYYY-MM-DD'；无法解析返回 ''。"""
    ts = (ts or "").strip()
    for fmt in _TS_FORMATS:
        try:
            return datetime.strptime(ts, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def _week_of(ts) -> str:
    """把错题时间戳归一成 ISO 周 'YYYY-Www'；无法解析返回 ''。"""
    d = _day_of(ts)
    if not d:
        return ""
    y, w, _ = datetime.strptime(d, "%Y-%m-%d").isocalendar()
    return "%04d-W%02d" % (y, w)


def knowledge_profile(items=None) -> dict:
    """知识点画像：按知识点聚合错题，给错题数/首末次出错时间/掌握等级。

    返回 {"total_wrong", "knowledge_points":[...], "weak_points":[...]}。
    weak_points = 错题数 >= 2 的知识点（真正需要「重点突破/薄弱」的薄弱点）。
    """
    items = items if items is not None else load_wrong_book()
    agg = {}
    for it in items:
        k = (it.get("knowledge") or "").strip() or "未分类"
        ts = (it.get("ts") or "").strip()
        e = agg.setdefault(k, {"wrong_count": 0, "first_ts": ts, "last_ts": ts})
        e["wrong_count"] += 1
        if ts:
            if not e["first_ts"] or ts < e["first_ts"]:
                e["first_ts"] = ts
            if ts > e["last_ts"]:
                e["last_ts"] = ts
    points = [
        {
            "knowledge": k,
            "wrong_count": v["wrong_count"],
            "first_ts": v["first_ts"],
            "last_ts": v["last_ts"],
            "mastery": mastery_label(v["wrong_count"]),
        }
        for k, v in agg.items()
    ]
    points.sort(key=lambda p: (-p["wrong_count"], p["knowledge"]))
    weak = [p for p in points if p["wrong_count"] >= 2]
    return {"total_wrong": len(items), "knowledge_points": points, "weak_points": weak}


def practice_summary(items=None) -> dict:
    """练习（正样本）摘要：按知识点聚合作答次数 / 答对数 / 正确率。

    返回 {"total_practice", "total_correct", "overall_rate", "knowledge_points":[...]}。
    """
    items = items if items is not None else load_practice_log()
    agg = {}
    for it in items:
        k = (it.get("knowledge") or "").strip() or "未分类"
        e = agg.setdefault(k, {"attempt_count": 0, "correct_count": 0})
        e["attempt_count"] += 1
        if it.get("correct"):
            e["correct_count"] += 1
    points = [
        {
            "knowledge": k,
            "attempt_count": v["attempt_count"],
            "correct_count": v["correct_count"],
            "correct_rate": round(v["correct_count"] / v["attempt_count"], 3),
        }
        for k, v in agg.items()
    ]
    points.sort(key=lambda p: (-p["attempt_count"], p["knowledge"]))
    total = len(items)
    correct = sum(1 for it in items if it.get("correct"))
    return {
        "total_practice": total,
        "total_correct": correct,
        "overall_rate": round(correct / total, 3) if total else 0.0,
        "knowledge_points": points,
    }


def _touch_ts(e: dict, ts):
    """把时间戳并入首/末次字段（字符串字典序比较，口径与 knowledge_profile 一致）。"""
    ts = (ts or "").strip()
    if not ts:
        return
    if not e["first_ts"] or ts < e["first_ts"]:
        e["first_ts"] = ts
    if ts > e["last_ts"]:
        e["last_ts"] = ts


def merged_profile(wrong_items=None, practice_items=None) -> dict:
    """错题本（负样本）+ 练习日志（正样本）合并成完整掌握画像。

    返回 {"total_wrong", "total_practice", "knowledge_points":[...], "weak_points":[...]}。
    每个知识点含 wrong_count / attempt_count / correct_count / correct_rate / mastery。
    weak_points = 错题数 >= 2，或（练 >= 2 次且正确率 < 0.7）——真正需要突破的点。
    """
    wrong_items = wrong_items if wrong_items is not None else load_wrong_book()
    practice_items = practice_items if practice_items is not None else load_practice_log()
    agg = {}

    def _ensure(k):
        return agg.setdefault(k, {
            "wrong_count": 0, "attempt_count": 0, "correct_count": 0,
            "first_ts": "", "last_ts": "",
        })

    for it in wrong_items:
        k = (it.get("knowledge") or "").strip() or "未分类"
        e = _ensure(k)
        e["wrong_count"] += 1
        _touch_ts(e, it.get("ts"))
    for it in practice_items:
        k = (it.get("knowledge") or "").strip() or "未分类"
        e = _ensure(k)
        e["attempt_count"] += 1
        if it.get("correct"):
            e["correct_count"] += 1
        _touch_ts(e, it.get("ts"))

    points = []
    for k, v in agg.items():
        rate = round(v["correct_count"] / v["attempt_count"], 3) if v["attempt_count"] else 0.0
        points.append({
            "knowledge": k,
            "wrong_count": v["wrong_count"],
            "attempt_count": v["attempt_count"],
            "correct_count": v["correct_count"],
            "correct_rate": rate,
            "mastery": mastery_from_stats(v["wrong_count"], v["attempt_count"], v["correct_count"]),
            "first_ts": v["first_ts"],
            "last_ts": v["last_ts"],
        })
    points.sort(key=lambda p: (-p["wrong_count"], -p["attempt_count"], p["knowledge"]))
    weak = [p for p in points
            if p["wrong_count"] >= 2 or (p["attempt_count"] >= 2 and p["correct_rate"] < 0.7)]
    return {
        "total_wrong": len(wrong_items),
        "total_practice": len(practice_items),
        "knowledge_points": points,
        "weak_points": weak,
    }


def daily_summary(items=None) -> dict:
    """每日摘要：按日期聚合错题数。返回 {"total_days", "days":[{date, wrong_count}]}。"""
    items = items if items is not None else load_wrong_book()
    counter = Counter(d for d in (_day_of(it.get("ts")) for it in items) if d)
    days = [{"date": d, "wrong_count": c} for d, c in sorted(counter.items())]
    return {"total_days": len(days), "days": days}


def weekly_summary(items=None) -> dict:
    """每周摘要：按 ISO 周聚合错题数。返回 {"total_weeks", "weeks":[{week, wrong_count}]}。"""
    items = items if items is not None else load_wrong_book()
    counter = Counter(w for w in (_week_of(it.get("ts")) for it in items) if w)
    weeks = [{"week": w, "wrong_count": c} for w, c in sorted(counter.items())]
    return {"total_weeks": len(weeks), "weeks": weeks}


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_profile_html(items=None) -> str:
    """把学情画像渲染成**自包含**中文 HTML（内联 CSS，无外部依赖）。"""
    items = items if items is not None else load_wrong_book()
    prof = knowledge_profile(items)
    daily = daily_summary(items)
    weekly = weekly_summary(items)

    kp_rows = "".join(
        "<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (
            _esc(p["knowledge"]), p["wrong_count"], _esc(p["mastery"]),
            _esc(p["last_ts"] or "-"))
        for p in prof["knowledge_points"]
    ) or "<tr><td colspan='4'>暂无错题</td></tr>"

    weak_html = "".join(
        "<li>%s：错 %d 题（%s）</li>" % (_esc(p["knowledge"]), p["wrong_count"], _esc(p["mastery"]))
        for p in prof["weak_points"]
    ) or "<li>暂无薄弱点，继续加油！</li>"

    daily_html = "".join(
        "<tr><td>%s</td><td>%d</td></tr>" % (_esc(d["date"]), d["wrong_count"])
        for d in daily["days"]
    ) or "<tr><td colspan='2'>暂无记录</td></tr>"

    weekly_html = "".join(
        "<tr><td>%s</td><td>%d</td></tr>" % (_esc(w["week"]), w["wrong_count"])
        for w in weekly["weeks"]
    ) or "<tr><td colspan='2'>暂无记录</td></tr>"

    advice = []
    if prof["weak_points"]:
        names = "、".join(p["knowledge"] for p in prof["weak_points"][:3])
        advice.append("建议优先复习：<b>%s</b>（先看课本例题，再同类题巩固）。" % _esc(names))
    if daily["total_days"] >= 2 and daily["days"][-1]["wrong_count"] > daily["days"][0]["wrong_count"]:
        advice.append("最近错题有增加，注意是不是进度过快，可放慢节奏、多留复习时间。")
    if not advice:
        advice.append("目前错题不多，保持节奏即可。")

    advice_html = "".join("<li>%s</li>" % a for a in advice)

    html = (
        "<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>家教学习画像</title><style>"
        "body{font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#222}"
        "h1{font-size:22px}h2{font-size:17px;margin-top:28px;border-bottom:2px solid #eee;padding-bottom:6px}"
        "table{border-collapse:collapse;width:100%%;margin:8px 0}"
        "td,th{border:1px solid #ddd;padding:6px 8px;text-align:left;font-size:14px}"
        "th{background:#f2f2f2}.weak{color:#c0392b;font-weight:600}.ok{color:#27ae60;font-weight:600}"
        "ul{line-height:1.7}.meta{color:#666;font-size:13px}"
        "</style></head><body>"
        "<h1>家教学习画像（学情）</h1>"
        "<p class='meta'>错题总数：<b>%d</b> ｜ 涉及知识点：<b>%d</b> 个 ｜ 薄弱点：<b>%d</b> 个</p>"
        "<h2>知识点画像</h2><table><tr><th>知识点</th><th>错题数</th><th>掌握等级</th><th>最近出错</th></tr>%s</table>"
        "<h2>薄弱知识点</h2><ul>%s</ul>"
        "<h2>每日摘要</h2><table><tr><th>日期</th><th>错题数</th></tr>%s</table>"
        "<h2>每周摘要</h2><table><tr><th>周</th><th>错题数</th></tr>%s</table>"
        "<h2>学习建议</h2><ul>%s</ul>"
        "<p class='meta'>本报告由本地错题本自动生成，不含学生隐私，不上传。数据仅统计自造题。</p>"
        "</body></html>"
    ) % (prof["total_wrong"], len(prof["knowledge_points"]), len(prof["weak_points"]),
         kp_rows, weak_html, daily_html, weekly_html, advice_html)
    return html


def profile_report(out_path=None, wrong_path=None) -> dict:
    """生成学情画像 HTML（本地）并返回摘要 JSON。返回含 path / total_wrong / weak_points / daily / weekly。"""
    items = load_wrong_book(wrong_path)
    out_path = out_path or os.path.join(LOGS_DIR, "profile_report.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_profile_html(items))
    prof = knowledge_profile(items)
    return {
        "path": out_path,
        "total_wrong": prof["total_wrong"],
        "knowledge_count": len(prof["knowledge_points"]),
        "weak_points": prof["weak_points"],
        "daily": daily_summary(items),
        "weekly": weekly_summary(items),
    }


def build_profile_html_full(wrong_items=None, practice_items=None) -> str:
    """把「错题本 + 练习日志」合并渲染成**自包含**中文 HTML（含正样本：作答次数/正确率）。"""
    wrong_items = wrong_items if wrong_items is not None else load_wrong_book()
    practice_items = practice_items if practice_items is not None else load_practice_log()
    prof = merged_profile(wrong_items, practice_items)
    psum = practice_summary(practice_items)
    daily = daily_summary(wrong_items)
    weekly = weekly_summary(wrong_items)

    def pct(p):
        return ("%d%%" % round(p["correct_rate"] * 100)) if p["attempt_count"] else "-"

    kp_rows = "".join(
        "<tr><td>%s</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            _esc(p["knowledge"]), p["wrong_count"], p["attempt_count"], pct(p),
            _esc(p["mastery"]), _esc(p["last_ts"] or "-"))
        for p in prof["knowledge_points"]
    ) or "<tr><td colspan='6'>暂无记录</td></tr>"

    weak_html = "".join(
        "<li>%s：错 %d 题 · 练 %d 次 · 正确率 %s（%s）</li>" % (
            _esc(p["knowledge"]), p["wrong_count"], p["attempt_count"], pct(p), _esc(p["mastery"]))
        for p in prof["weak_points"]
    ) or "<li>暂无薄弱点，继续加油！</li>"

    practice_html = "".join(
        "<tr><td>%s</td><td>%d</td><td>%d</td><td>%d%%</td></tr>" % (
            _esc(p["knowledge"]), p["attempt_count"], p["correct_count"],
            round(p["correct_rate"] * 100))
        for p in psum["knowledge_points"]
    ) or "<tr><td colspan='4'>暂无练习记录</td></tr>"

    daily_html = "".join(
        "<tr><td>%s</td><td>%d</td></tr>" % (_esc(d["date"]), d["wrong_count"])
        for d in daily["days"]
    ) or "<tr><td colspan='2'>暂无记录</td></tr>"

    weekly_html = "".join(
        "<tr><td>%s</td><td>%d</td></tr>" % (_esc(w["week"]), w["wrong_count"])
        for w in weekly["weeks"]
    ) or "<tr><td colspan='2'>暂无记录</td></tr>"

    advice = []
    if prof["weak_points"]:
        names = "、".join(p["knowledge"] for p in prof["weak_points"][:3])
        advice.append("建议优先复习：<b>%s</b>（先看课本例题，再同类题巩固）。" % _esc(names))
    mastered = [p["knowledge"] for p in prof["knowledge_points"] if p["mastery"] == "已掌握"]
    if mastered:
        advice.append("已掌握：<b>%s</b>，可以适当加一点综合题。"
                      % _esc("、".join(mastered[:3])))
    if psum["total_practice"] and psum["overall_rate"] < 0.6:
        advice.append("最近练习正确率偏低，建议放慢节奏、把错题先复盘一遍。")
    if not advice:
        advice.append("目前记录不多，保持节奏即可。")
    advice_html = "".join("<li>%s</li>" % a for a in advice)

    html = (
        "<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>家教学习画像</title><style>"
        "body{font-family:system-ui,'Microsoft YaHei',sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#222}"
        "h1{font-size:22px}h2{font-size:17px;margin-top:28px;border-bottom:2px solid #eee;padding-bottom:6px}"
        "table{border-collapse:collapse;width:100%%;margin:8px 0}"
        "td,th{border:1px solid #ddd;padding:6px 8px;text-align:left;font-size:14px}"
        "th{background:#f2f2f2}.weak{color:#c0392b;font-weight:600}.ok{color:#27ae60;font-weight:600}"
        "ul{line-height:1.7}.meta{color:#666;font-size:13px}"
        "</style></head><body>"
        "<h1>家教学习画像（学情）</h1>"
        "<p class='meta'>错题总数：<b>%d</b> ｜ 练习次数：<b>%d</b> ｜ 涉及知识点：<b>%d</b> 个 ｜ 薄弱点：<b>%d</b> 个</p>"
        "<h2>知识点画像（错题 + 作答）</h2>"
        "<table><tr><th>知识点</th><th>错题数</th><th>作答次数</th><th>正确率</th><th>掌握等级</th><th>最近活动</th></tr>%s</table>"
        "<h2>薄弱知识点</h2><ul>%s</ul>"
        "<h2>练习摘要</h2><table><tr><th>知识点</th><th>作答次数</th><th>答对数</th><th>正确率</th></tr>%s</table>"
        "<h2>每日摘要（错题数）</h2><table><tr><th>日期</th><th>错题数</th></tr>%s</table>"
        "<h2>每周摘要（错题数）</h2><table><tr><th>周</th><th>错题数</th></tr>%s</table>"
        "<h2>学习建议</h2><ul>%s</ul>"
        "<p class='meta'>本报告由本地错题本 + 练习日志自动生成，不含学生隐私，不上传。数据仅统计自造题。</p>"
        "</body></html>"
    ) % (prof["total_wrong"], prof["total_practice"], len(prof["knowledge_points"]),
         len(prof["weak_points"]), kp_rows, weak_html, practice_html,
         daily_html, weekly_html, advice_html)
    return html


def profile_report_full(out_path=None, wrong_path=None, practice_path=None) -> dict:
    """生成「错题本 + 练习日志」合并画像 HTML（本地）并返回摘要 JSON。"""
    wrong_items = load_wrong_book(wrong_path)
    practice_items = load_practice_log(practice_path)
    out_path = out_path or os.path.join(LOGS_DIR, "profile_report.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_profile_html_full(wrong_items, practice_items))
    prof = merged_profile(wrong_items, practice_items)
    return {
        "path": out_path,
        "total_wrong": prof["total_wrong"],
        "total_practice": prof["total_practice"],
        "knowledge_count": len(prof["knowledge_points"]),
        "weak_points": prof["weak_points"],
        "knowledge_points": prof["knowledge_points"],
        "practice": practice_summary(practice_items),
        "daily": daily_summary(wrong_items),
        "weekly": weekly_summary(wrong_items),
    }


if __name__ == "__main__":
    # 自检：用临时错题本造 3 条样本，验证画像/摘要/HTML 全链路（不触发网络）。
    import tempfile
    demo = [
        {"question": "解方程：2x+3=11", "student_answer": "x=5",
         "knowledge": "一元一次方程", "ts": "2026-11-07 20:00:00"},
        {"question": "解方程：3x-5=10", "student_answer": "x=6",
         "knowledge": "一元一次方程", "ts": "2026-11-08 09:30:00"},
        {"question": "因式分解：x²-9", "student_answer": "x(x-3)",
         "knowledge": "因式分解", "ts": "2026-11-08 10:00:00"},
    ]
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(demo, f, ensure_ascii=False)

    prof = knowledge_profile(demo)
    print("知识点画像：", json.dumps(prof, ensure_ascii=False))
    print("每日摘要：", json.dumps(daily_summary(demo), ensure_ascii=False))
    print("每周摘要：", json.dumps(weekly_summary(demo), ensure_ascii=False))

    # 正样本：练习日志（作答次数 + 正确率）→ 合并画像
    demo_practice = [
        {"question": "解方程：2x+3=11", "student_answer": "x=4",
         "knowledge": "一元一次方程", "correct": True, "ts": "2026-11-08 20:00:00"},
        {"question": "解方程：5x-3=2", "student_answer": "x=1",
         "knowledge": "一元一次方程", "correct": True, "ts": "2026-11-08 20:05:00"},
        {"question": "因式分解：x²-4", "student_answer": "(x+2)(x-2)",
         "knowledge": "因式分解", "correct": True, "ts": "2026-11-08 20:10:00"},
    ]
    mp = merged_profile(demo, demo_practice)
    print("合并画像：", json.dumps(mp, ensure_ascii=False))
    print("练习摘要：", json.dumps(practice_summary(demo_practice), ensure_ascii=False))
    rep_full = profile_report_full(
        out_path=os.path.join(tempfile.gettempdir(), "profile_demo_full.html"),
        wrong_path=path,
        practice_path=None)
    # 上面的 practice_path=None 只读真实日志；为演示合并 HTML，直接传列表给 build_profile_html_full：
    html_full = build_profile_html_full(demo, demo_practice)
    with open(os.path.join(tempfile.gettempdir(), "profile_demo_full.html"), "w", encoding="utf-8") as f:
        f.write(html_full)
    print("合并报告：", json.dumps(
        {k: rep_full[k] for k in ("path", "total_wrong", "total_practice", "knowledge_count")},
        ensure_ascii=False))
    os.remove(path)


