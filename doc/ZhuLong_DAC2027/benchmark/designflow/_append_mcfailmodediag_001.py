#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-McFailModeDiag-001 to EDA-Eval-DesignFlow_B.jsonl."""
import os, json, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-McFailModeDiag-001"
JSONL = f"{BENCH}/EDA-Eval-DesignFlow_B.jsonl"
CHECK = f"{BENCH}/reference/{CASE}/check.py"

with open(CHECK) as f:
    check_src = f.read()
check_sha = hashlib.sha256(check_src.encode()).hexdigest()[:8]

# verify k_check: count labeled (a)..(n) in assert messages
import re
labels = sorted(set(re.findall(r"\(([a-z])\)\s", check_src)))
k_check = len(labels)
print("k_check labels:", labels, "k=", k_check)
assert k_check >= 8 and labels == [chr(ord('a')+i) for i in range(k_check)], "label sequence broken"

prompt = (
"你是 EDA 设计流自动化 agent。请交付一个 **Monte Carlo / corner-sweep 仿真运行失败模式诊断器 + 状态/聚合一致性审计器**。\n\n"
"## 背景（真实场景，来自一条 FineSim/Solido Variation Designer 仿真 trace）\n"
"某用户在 Solido Variation Designer + FineSim 上跑了一组 Monte Carlo / corner 仿真，得到一批 run 结果"
"（每条 run 一个子目录：run.log / result.mt0 / status.json，外加顶层 summary.json 与 deck.sp）。"
"用户原话：「see variation_designer_7, find data bug, and how to debug」「check testbench」「how to fix each bug」。"
"真实诊断发现的关键 bug：**所有 run 在 engine.log 里都标记为 Failed，但 summary 的 yield 却报告为 +infinity / n_pass=全部**"
"——即 per-run 状态与聚合结果不一致。\n\n"
"## 任务\n"
"交付 Python 诊断器 `mc_faildiag.py`，CLI：`python3 mc_faildiag.py <runs_dir> <summary.json> <out_dir>`，功能：\n"
"1. 逐 run 读取 run.log + result.mt0 + status.json，把每条 run 分类到以下失败模式之一（按优先级，高优先级先判）：\n"
"   license_fail > port_mismatch_abort > env_error > non_convergence > measure_error > timeout > passed\n"
"   - license_fail: log 含 'no valid license' / 'License to run is temporarily unavailable'\n"
"   - port_mismatch_abort: log 含 'subckt ... and ... have different number of pins' / 'undefined subckt' / 'Simulation halted: port mismatch'\n"
"   - env_error: log 含 'Permission denied' / 'command not found' / 'module: command not found'\n"
"   - non_convergence: log 含 'DC not converged' / 'non-convergence'\n"
"   - measure_error: log 含 '.measure ... failed/aborted'，或 result.mt0 空/无数值\n"
"   - timeout: log 含 'SIGKILL/Killed/timed out' 且无 'job concluded'\n"
"   - passed: log 含 'Successfully Completed' + 'job concluded' 且 result.mt0 有数值行\n"
"   注意：某些 run 的 log 会同时含多个模式的标记，必须按上述优先级判定（例如同时含 license 报错与 non-convergence，应判 license_fail）。\n"
"2. 从 per-run verdicts 重新计算 computed_n_pass / 各模式计数，与 summary.json 里的 reported n_pass / n_fail / yield 做一致性审计：\n"
"   - 若 reported n_pass ≠ computed_n_pass，或 reported yield 为正/infinity 但 computed_n_pass=0，则 aggregate.consistent=False 并写明 inconsistency_detail。\n"
"3. 输出 `<out_dir>/mc_faildiag_report.json`，schema：\n"
"   {runs:[{name, verdict, root_cause, evidence:list}], summary:{n_total, n_pass, n_fail_by_mode:dict},\n"
"    aggregate:{reported_n_pass, reported_n_fail, reported_yield, computed_n_pass, consistent:bool, inconsistency_detail},\n"
"    root_cause_top, metrics_reported, corner, tool}\n\n"
"## 公开输入（assets/，A 档）\n"
"- `mc_runs_A/`：8 条 run 子目录（arun_01..arun_08，每条含 run.log / result.mt0 / status.json）\n"
"- `summary_A.json`：聚合结果（注意：本批 A 的 summary 与 per-run 状态**故意不一致**，正是要审计出的 bug）\n"
"- `deck_A.sp`：testbench 上下文（仅供参考，不需解析）\n"
"- `prompt.txt` / `task_brief.md`：任务说明与交付接口\n\n"
"## 交付\n"
"打包 `outputs/submit.zip`，内含 `mc_faildiag.py`（与可选的参考 report）。判分器会把你看不到的隐藏输入 B"
"（结构、run 名、失败模式组合、summary 是否一致都不同）放进 workdir，独立运行你的 `mc_faildiag.py` 并审计输出。\n"
"🚫 不许硬编码 A 的 run 名/verdict/yield；判分含跨输入重跑 A 与确定性重跑 B 的守卫。\n"
)

test_rationale = (
"14 条断言："
"①submit.zip 内含 mc_faildiag.py 且非空 "
"②mc_faildiag.py 可 py_compile "
"③候选经 subprocess 在隐藏 B 上运行（exit 0 且产出 mc_faildiag_report.json）"
"④B 的 10 条 run verdict 全部匹配 GT（passed/non_convergence/measure_error/port_mismatch_abort/license_fail/timeout/env_error）"
"⑤B non_convergence 计数==2 "
"⑥B measure_error 计数==1 "
"⑦B port_mismatch_abort 计数==1 "
"⑧B license_fail 计数==1 "
"⑨B env_error 计数==1 "
"⑩B 聚合一致性 verdict 正确（B 一致=True，computed_n_pass==3）"
"⑪每条 failed run 的 root_cause 与 evidence 非空 "
"⑫name-agnostic：B run 名出现于 B 报告、A run 名不泄漏进 B 报告 "
"⑬跨输入守卫：重跑 A 时 8 条 verdict 全对且 A 聚合**不一致**=False（computed_n_pass==0，复刻 trace 的 Bug #1 全 failed 但 yield=inf）"
"⑭确定性：重跑 B verdict 集合与首次完全一致"
)

case = {
  "task_id": CASE,
  "mode": "design_flow",
  "prompt": prompt,
  "attachments": [
    {"name":"mc_runs_A","source":"mc_runs_A","desc":"公开输入 A：8 条 MC/corner run 子目录（arun_01..arun_08），每条含 run.log / result.mt0 / status.json。本批 A 的 per-run 全 failed（多种模式），但 summary_A 报 yield=inf/n_pass=8——即 trace Bug #1。"},
    {"name":"summary_A.json","source":"summary_A.json","desc":"公开 A 聚合结果（与 per-run 状态故意不一致，需审计出）。"},
    {"name":"deck_A.sp","source":"deck_A.sp","desc":"A testbench 上下文（仅供参考）。"},
    {"name":"prompt.txt","source":"prompt.txt","desc":"任务说明（自然语言）。"},
    {"name":"task_brief.md","source":"task_brief.md","desc":"交付接口与文件位置说明（≤3 行）。"},
  ],
  "entry_point": "outputs/submit.zip",
  "expected_artifacts": ["mc_faildiag.py","mc_faildiag_report.json"],
  "test": check_src,
  "budget": {"max_turns": 20, "max_seconds": 1200},
  "metadata": {
    "trace_source": {
      "user":"e0024852","host":"hfeg0pkn004","session_file":"1793065824220_rigwz.messages.json",
      "match_count":72,"real_task_summary":"Solido Variation Designer + FineSim Monte Carlo 仿真结果诊断：用户要求 find data bug / check testbench / how to fix each bug；agent 读 engine.log/summary.json/project_setup.xml 发现 Bug #1（所有 run 标记 Failed 但 yield 报告 +infinity，状态/聚合不一致），全程 read_files 未真跑 FineSim。"
    },
    "domain":"spice_sim",
    "layer":"L1",
    "layer_rationale":"忠实于 trace：真实 agent 全程仅 read_files 读取既有 run logs/summary（从未真跑仿真器），属离线日志诊断；失败模式空间含 license/permission/timeout 等环境失败，无法用 .75 真跑复现，故 L1 静态解析最忠实且可覆盖完整失败空间。",
    "test_rationale": test_rationale,
    "track":"synthesized",
    "harness":"pi",
  }
}

# k gate
n_circ = test_rationale.count("①") + sum(1 for ch in test_rationale if ch in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭")
# count circled chars ①..⑭
import unicodedata
circ = [ch for ch in test_rationale if ch in "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭"]
k_rationale = len(circ)
print(f"k_rationale={k_rationale}  k_check={k_check}")
assert k_rationale == k_check >= 8, f"GATE FAIL: k_rationale={k_rationale} k_check={k_check}"
assert test_rationale.startswith("14 条断言："), "rationale prefix wrong"

# append (idempotency: remove prior same task_id)
lines=[]
if os.path.exists(JSONL):
    with open(JSONL) as f:
        for ln in f:
            try:
                if json.loads(ln).get("task_id")==CASE: continue
            except: pass
            lines.append(ln.rstrip("\n"))
lines.append(json.dumps(case, ensure_ascii=False))
with open(JSONL,"w") as f:
    f.write("\n".join(lines)+"\n")
print(f"appended. jsonl B now {len(lines)} lines. check_sha={check_sha} bytes={len(check_src)}")
