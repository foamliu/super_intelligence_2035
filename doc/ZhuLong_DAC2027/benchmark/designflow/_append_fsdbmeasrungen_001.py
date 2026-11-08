#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-FsdbMeasRunGen-001 to D.jsonl + mark ledger."""
import json, hashlib
from pathlib import Path

BENCH = Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
CID = "EDA-Eval-DesignFlow-FsdbMeasRunGen-001"
JSONL = BENCH / "EDA-Eval-DesignFlow_D.jsonl"

check_src = (BENCH / "reference" / CID / "check.py").read_text()
test_rationale = (
    "16 条断言：①(a) submit.zip 合法且无泄漏(不含 check/reference/negative/hidden_manifest/jsonl)且 zip 根含 gen_meas_runner.py 且 py_compile 通过且无禁用 import/socket/urllib "
    "②(b) 候选在隐藏 B 上 exit 0 且产出 run_meas.sh/expected_pmt.json/meas_summary.log 三文件 "
    "③(c) run_meas.sh 为 bash 脚本(含 #!/usr/bin/env bash shebang)且含 bsub 命令 "
    "④(d) run_meas.sh 的 bsub 行数等于 B 中有效 .fsdb case 数(4) "
    "⑤(e) 缺 .fsdb 的 case 其 fsdb 路径不出现在 run_meas.sh(跳过逻辑生效) "
    "⑥(f) 每个有效 case 的 .fsdb 路径出现在 run_meas.sh "
    "⑦(g) 每条 bsub 行含 -o <case>/meas 输出目录 "
    "⑧(h) 每条 bsub 行调用 fscript meas 命令 "
    "⑨(i) expected_pmt.json 为非空 JSON dict "
    "⑩(j) manifest 条目数等于有效 case 数(4) "
    "⑪(k) .pmt 路径符合 <case>/meas/<measure_stem>.pmt 模式 "
    "⑫(l) manifest 键集合等于 B 的有效 case 名集合 "
    "⑬(m) meas_summary.log 含 submitted=4 与 skipped=2 "
    "⑭(n) summary 列出每个提交 job 的 case 名(JOB <case>) "
    "⑮(o) 反硬编码: A-specific token 不出现在源码 + A 运行 bsub 数(3)≠B(4) "
    "⑯(p) run_meas.sh 含 set -uo pipefail"
)

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["gen_meas_runner.py"],
    "prompt": (BENCH / "assets" / CID / "prompt.txt").read_text(),
    "attachments": [
        "assets/%s/prompt.txt" % CID,
        "assets/%s/task_brief.md" % CID,
        "assets/%s/fsdb_measure_A.sp" % CID,
        "assets/%s/case_tree_A" % CID,
    ],
    "test": check_src,
    "budget": {"max_turns": 25, "timeout_sec": 600},
    "metadata": {
        "trace_source": {
            "user": "johnl",
            "host": "hfeg0pkn001",
            "session_file": "1791423204544_pewjz.messages.json",
            "match_count": 188,
            "real_task_summary": (
                "DRAM Poststress007 per-bank DFT mBist FineSim MatrixRun 测量链路修复: johnl 的 04_margin_measure.py "
                "报 No simulation results (整个目录树 .pmt/.mt0=0), 根因是 03_measure_run.sh (bsub 提交 fscript meas "
                "对 .fsdb 波形跑测量产出 .pmt) 根本没跑 (meas/ 全空, meas_log/ 空, 46 个 .fsdb 波形存在但 0 个产 .pmt; "
                "license daemon down + Aging/step2 案例缺波形). 用户原话: 帮我看下测量margin脚本为什么不能用了 / 先生成.pmt / "
                "你要看我原来怎么跑的 照着改 别自己瞎写 / 要bsub的方式. 合成产物: gen_meas_runner.py 读 fsdb_measure.sp "
                "命令清单 + case 树, 跳过缺 .fsdb 的 case, 生成 bsub 提交的 run_meas.sh + expected_pmt.json 清单 + summary."
            ),
        },
        "domain": "waveform",
        "grade": "B",
        "track": "synthesized",
        "L_level": "L1",
        "test_rationale": test_rationale,
    },
}

# assert gate: k_rationale == k_check
k_check = 16  # conditions a-p
n_assertions = test_rationale.count("①") + sum(test_rationale.count(c) for c in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯")
# count circled markers present
import re
marks = re.findall(r"[①-⑯]", test_rationale)
k_rationale = len(set(marks))
assert k_rationale == k_check, "k_rationale=%d != k_check=%d" % (k_rationale, k_check)
assert k_check >= 8
assert test_rationale.startswith("16 条断言：")
print("GATE: k_rationale=k_check=%d >=8 OK" % k_check)

# byte-sync: test field must equal disk check.py
assert entry["test"] == (BENCH / "reference" / CID / "check.py").read_text(), "test!=disk check.py"
sha = hashlib.sha256(entry["test"].encode()).hexdigest()
print("byte-sync sha:", sha, "size:", len(entry["test"]))

# append (idempotency: skip if task_id already present)
existing = [json.loads(l) for l in JSONL.read_text().splitlines() if l.strip()]
if any(e.get("task_id") == CID for e in existing):
    print("ALREADY PRESENT, skipping append")
else:
    with open(JSONL, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("APPENDED to D.jsonl, total lines now:", sum(1 for l in JSONL.read_text().splitlines() if l.strip()))
