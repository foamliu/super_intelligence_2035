#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-CalibreOpen1Fix-001 to shard A jsonl."""
import json, os

CASE = "EDA-Eval-DesignFlow-CalibreOpen1Fix-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
A_DIR = f"{BENCH}/assets/{CASE}"
REF_DIR = f"{BENCH}/reference/{CASE}"
JSONL = f"{BENCH}/EDA-Eval-DesignFlow_A.jsonl"

PROMPT = open(f"{A_DIR}/prompt.txt").read().rstrip("\n")
CHECK = open(f"{REF_DIR}/check.py").read()

ATTACHMENTS = [
    f"assets/{CASE}/prompt.txt",
    f"assets/{CASE}/task_brief.md",
    f"assets/{CASE}/gen_preAA_G5_CIP_final_A.py",
    f"assets/{CASE}/calibreSTIcmp_A.rule",
    f"assets/{CASE}/config_A.txt",
]

ENTRY = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": ATTACHMENTS,
    "test": CHECK,
    "metadata": {
        "trace_source": {
            "user": "ellawu",
            "host": "hfeg0pkn005",
            "session_file": "1789545344007_xchvr.messages.json",
            "match_count": 122,
            "real_task_summary": (
                "Calibre DRC OPEN1 错误诊断：用户报告 'ERROR: Error OPEN1 - problem with access, "
                "file type, or file open of file: calibreSTIcmp.rule.'；助手深查 gen_preAA_G5_CIP_final.py "
                "脚本与 calibreSTIcmp.rule，定位根因 = rule 文件缺 LAYOUT PRECISION 语句（脚本计算了 "
                "precision=10000 却从未注入），Calibre 默认 PRECISION 1000 与 GDS 实际 10000 不匹配报 OPEN1；"
                "次要问题：rsync 返回值未检查、calibre 前未校验文件存在、sed 仅改 PATH/PRIMARY。"
                "修复 = 注入 LAYOUT PRECISION <precision>（从 config 读，replace/insert）+ rsync 返回检查 + 文件校验。"
            ),
        },
        "domain": "pnr_signoff",
        "track": "faithful",
        "level": "L2",
        "test_rationale": (
            "14 条断言：①submit.zip 恰含 fix.py 与 diagnose.json 两文件 ②fix.py py_compile 通过 "
            "③A 运行 exit0 且输出 rule 含 LAYOUT PRECISION 10000（从 config_A 的 precision=10000 注入） "
            "④A 输出保留 LAYOUT path LP4TOP.gds / system gdsii / primary LP4TOP 三语句 "
            "⑤跨输入 B 运行 exit0 且输出 rule 含 LAYOUT PRECISION 1000（从 config_B 的 precision=1000 注入，验泛化） "
            "⑥B 输出保留 B 的 LAYOUT path M2CORE.gds / system gdsii / primary M2CORE "
            "⑦A 输出恰一条 PRECISION 行（无重复插入） ⑧B 输出恰一条 PRECISION 行 "
            "⑨diagnose.json 合法 JSON 且含 root_cause/issues/fix_summary 三键 "
            "⑩root_cause 提及 PRECISION（真实根因） ⑪issues 为 list 且长度≥2 "
            "⑫fix_summary 提及 PRECISION 注入语义 "
            "⑬防硬编码：fix.py 源码不含 A 专属字面量(cxmtG5_CIP/decqa/LP4TOP/ella_train/AF_FsMrgNEnCount)且不含 B 专属字面量(cxmt10G7/iejoad/M2CORE/vex_qa/DRAMCoreTop) "
            "⑭防硬编码：fix.py 源码不含精度字面量 10000/1000（precision 必须从 config 读取不得硬编码，否则 B 侧 1000 会错）"
        ),
    },
}

# verify test==disk roundtrip
disk_check = open(f"{REF_DIR}/check.py").read()
if ENTRY["test"] != disk_check:
    raise SystemExit("ERROR: test field != disk check.py")
print("[append] test==disk roundtrip OK")

# append (do not duplicate)
existing = []
if os.path.isfile(JSONL):
    with open(JSONL) as f:
        for line in f:
            d = json.loads(line)
            if d.get("task_id") == CASE:
                raise SystemExit(f"ERROR: {CASE} already in jsonl")
            existing.append(d)

with open(JSONL, "a") as f:
    f.write(json.dumps(ENTRY, ensure_ascii=False) + "\n")

n = sum(1 for _ in open(JSONL))
print(f"[append] {CASE} appended. A jsonl now {n} entries.")
