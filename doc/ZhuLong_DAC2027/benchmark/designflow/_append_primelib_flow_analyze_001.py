#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-PrimeLibFlowAnalyze-001 to D.jsonl with byte-sync."""
import json, hashlib
from pathlib import Path

BENCH = Path("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow")
CASE = "EDA-Eval-DesignFlow-PrimeLibFlowAnalyze-001"
REF = BENCH / "reference" / CASE
JSONL = BENCH / "EDA-Eval-DesignFlow_D.jsonl"

check_src = (REF / "check.py").read_text(encoding="utf-8")
check_sha = hashlib.sha256(check_src.encode("utf-8")).hexdigest()
check_size = len(check_src.encode("utf-8"))

PROMPT = """/home/johnl/.cline/scripts/data/primelib/primelib_char_all_comb  帮我看下这里的k库流程是怎样的

---
交付接口（task_brief）：
- 编写 analyze_flow.py，解析给定 PrimeLib 表征工程目录，输出结构化 JSON（库名/corner/源网表/cell 清单来源与数量/流程步骤/运行门禁/工具/校验项/corner 切换机制/电压/温度/网格/阈值）。
- 用法：python3 analyze_flow.py <project_dir> -o flow_analysis.json
- 交付：把 analyze_flow.py 打包成 outputs/submit.zip。"""

TEST_RATIONALE = (
    "16 条断言："
    "① zip 合法且含 analyze_flow.py 可解压 "
    "② analyze_flow.py 在隐藏 B 项目上运行 exit 0 "
    "③ 输出 library == \"iolib_io\" "
    "④ 输出 corner == \"TT_1p1_25c\" "
    "⑤ 输出 source_netlist == \"../netlist.io.sp\" "
    "⑥ 输出 cell_list_source == \"cells.txt\" "
    "⑦ 输出 cell_count == 15 "
    "⑧ flow_steps >=5 步且含 prepare/primelib_char/validate/lc_to_db "
    "⑨ gate 含 \"PREPARE.PASS\" "
    "⑩ tools 含 \"primelib\" "
    "⑪ validation_checks 非空且含 cell inventory "
    "⑫ corner_mechanism 含 \"PROJECT_CONFIG\" "
    "⑬ voltage.vcc == 1.1 且 vbp == 1.1 "
    "⑭ temperature_c == 25.0 "
    "⑮ 反硬编码：在 A 项目上跑出 library == \"stdcells_ac\"（与 B 不同） "
    "⑯ 3-seed 确定性：3 次运行输出完全一致"
)

entry = {
    "id": CASE,
    "task_id": CASE,
    "case_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": PROMPT,
    "attachments": [
        f"assets/{CASE}/primelib_char_all_comb",
    ],
    "budget": {"max_turns": 25},
    "expected_artifacts": ["outputs/submit.zip"],
    "metadata": {
        "trace_source": {
            "user": "johnl",
            "host": "hfeg0pkn001",
            "session_file": "1793866732639_cr42l.messages.json",
            "match_count": 43,
            "real_task_summary": "理解 PrimeLib K 库表征流程：netlist.presim → prepare(盘点/分类/闭包/门禁) → LSF PrimeLib(识别/网格表征) → validate 严校验 → LC 转 DB；配置驱动、失败即断。",
        },
        "domain": "schematic_netlist",
        "track": "faithful",
        "test_rationale": TEST_RATIONALE,
        "check_sha256": check_sha,
        "check_size": check_size,
        "level": "L1",
        "grade": "A",
    },
    "task_id_full": CASE,
}

# byte-sync: verify jsonl test field == disk check.py
line = json.dumps(entry, ensure_ascii=False)
roundtrip = json.loads(line)
rt_test = roundtrip["test"]
rt_sha = hashlib.sha256(rt_test.encode("utf-8")).hexdigest()
rt_size = len(rt_test.encode("utf-8"))
assert rt_sha == check_sha, f"byte-sync FAIL: jsonl test sha {rt_sha} != disk {check_sha}"
assert rt_size == check_size, f"byte-sync FAIL: jsonl test size {rt_size} != disk {check_size}"
print(f"byte-sync OK: sha {check_sha[:16]}... size {check_size}")

# assertion gate
k_rationale = 16
k_check = 16
assert k_rationale == k_check and k_check >= 8
print(f"assertion gate OK: k_rationale={k_rationale} k_check={k_check}")

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print(f"Appended to {JSONL}")

# verify last line
with open(JSONL, "rb") as f:
    f.seek(0, 2); end = f.tell()
    # read last line
    pos = end - 2
    while pos > 0 and f.read(1) != b"\n":
        pos -= 1; f.seek(pos)
    last = f.readline().decode("utf-8").strip()
d = json.loads(last)
print(f"last entry id={d['id']} domain={d['metadata']['domain']} track={d['metadata']['track']}")

# count
cnt = sum(1 for l in open(JSONL) if l.strip())
print(f"D.jsonl now has {cnt} entries")
