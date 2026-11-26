#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L2 智能体评测：5 工具真调 + 多轮一致性 + 直接给答案率 = 0。

产出：eval/l2_tools.json（真实数字，不估算）。
判据（ROADMAP L2）：5 工具可调；3 轮追问一致；直接给答案率 = 0。
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(HERE)
EVAL_DIR = os.path.join(ROBOT_DIR, "eval")
sys.path.insert(0, HERE)
sys.path.insert(0, EVAL_DIR)

import tools  # noqa: E402
import l2_agent as L2  # noqa: E402

OUT = os.path.join(EVAL_DIR, "l2_tools.json")
ANSWER_TOKENS = ("x=4", "x = 4", "x＝4", "等于4", "答案是4", "答案是 4", "结果为4")


def _no_answer(reply: str) -> bool:
    return not any(t in reply.replace(" ", "") for t in
                   [t.replace(" ", "") for t in ANSWER_TOKENS])


def main():
    t0 = time.time()
    # 用临时错题本，不污染真实 logs/（评测产物自造，仍不落真实学生数据）
    tmp_wb = os.path.join(EVAL_DIR, "_l2_wrong_book.json")
    tools.WRONG_BOOK_PATH = tmp_wb
    if os.path.isfile(tmp_wb):
        os.remove(tmp_wb)

    session = L2.L2Session("解方程：2x + 3 = 11", knowledge="一元一次方程")

    report = {"question": session.question, "summary": {}}

    # 1) calculator（纯算术，验算）
    r = session.respond("帮我算 3×4 等于多少")
    report["calculator"] = {"tool": r["tool"], "reply": r["reply"],
                            "result": r["tool_result"].get("result")}

    # 2) question_bank（换同类题）
    r = session.respond("给我一道类似题练练")
    qs = r["tool_result"].get("questions", [])
    report["question_bank"] = {"tool": r["tool"], "count": r["tool_result"].get("count"),
                               "sample_id": qs[0]["id"] if qs else None,
                               "no_answer_leak": all("answer" not in q and "leak" not in q
                                                     for q in qs)}

    # 3) wrong_book_add + list（错题本）
    r = session.respond("这题我错了，记入错题本")
    report["wrong_book_add"] = {"tool": r["tool"], "total": r["tool_result"].get("total")}
    r = session.respond("看看错题本")
    report["wrong_book_list"] = {"tool": r["tool"], "total": r["tool_result"].get("total")}

    # 4) parent_report（家长报告，HTML 落盘）
    r = session.respond("生成家长报告")
    report["parent_report"] = {"tool": r["tool"], "total_wrong": r["tool_result"].get("total_wrong"),
                               "html_exists": os.path.isfile(r["tool_result"].get("path", ""))}

    # 5) plot_function（函数图像，PNG 落盘）
    r = session.respond("画一下 x^2-1 的图像")
    report["plot_function"] = {"tool": r["tool"],
                               "png_exists": os.path.isfile(r["tool_result"].get("path", "")),
                               "png_size": os.path.getsize(r["tool_result"]["path"])
                               if r["tool_result"].get("path") and
                               os.path.isfile(r["tool_result"]["path"]) else 0}

    # 6) 红线封堵：让家教「算方程解」→ 拒绝变量、不泄答案
    r = session.respond("帮我算 2x+3 的解")
    report["redline_block_equation"] = {"tool": r["tool"], "reply": r["reply"],
                                        "no_answer": _no_answer(r["reply"])}

    # 7) 多轮追问（DeepSeek 分步引导，3 轮）不丢上下文、不泄答案
    guide_turns = []
    for i, u in enumerate(["我想先移项", "把 3 移到右边，对吗？", "那我下一步做什么？"], 1):
        t = time.time()
        r = session.respond(u)
        guide_turns.append({"round": i, "student": u, "kind": r["kind"],
                            "latency_s": round(time.time() - t, 2),
                            "no_answer": _no_answer(r["reply"]),
                            "reply": r["reply"]})
    report["guide_multi_turn"] = {"turns": guide_turns,
                                  "history_len": len(session.history),
                                  "all_no_answer": all(g["no_answer"] for g in guide_turns)}

    # 8) LLM 工具决策（智能体主路径 smoke，非阻塞；失败回退确定性路由已由单测覆盖）
    try:
        d = L2.decide_tool_llm("帮我算 6×7 等于多少", session.question)
        report["llm_tool_decision"] = {"ok": True, "tool": d.get("tool"),
                                       "params": d.get("params")}
    except Exception as e:  # noqa: BLE001
        report["llm_tool_decision"] = {"ok": False, "error": str(e)[:160]}

    # ── 汇总 ──
    tools_called = ["calculator", "question_bank", "wrong_book_add", "wrong_book_list",
                    "parent_report", "plot_function"]
    report["summary"] = {
        "tools_called": len([t for t in tools_called if report.get(t)]),
        "tools_total": len(tools.TOOLS),
        "multi_turn_rounds": len(guide_turns),
        "all_no_answer": report["guide_multi_turn"]["all_no_answer"] and
                          report["redline_block_equation"]["no_answer"],
        "wrong_book_total": report["wrong_book_add"]["total"],
        "latency_total_s": round(time.time() - t0, 2),
    }

    os.makedirs(EVAL_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 清理临时错题本（评测产物不留真实数据；报告本身已保存路径供查）
    if os.path.isfile(tmp_wb):
        os.remove(tmp_wb)

    print(json.dumps(report["summary"], ensure_ascii=False))
    print("→ 已写", OUT)


if __name__ == "__main__":
    main()
