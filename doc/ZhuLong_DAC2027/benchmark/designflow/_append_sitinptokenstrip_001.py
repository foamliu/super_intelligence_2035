#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SiInpTokenStrip-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json, os

CID = "EDA-Eval-DesignFlow-SiInpTokenStrip-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF_DIR = os.path.join(BENCH, "reference", CID)
CHECK_SRC = open(os.path.join(REF_DIR, "check.py"), "r", encoding="utf-8").read()

prompt = open(os.path.join(BENCH, "assets", CID, "prompt.txt"), "r", encoding="utf-8").read().rstrip("\n")

attachments = [
    "assets/%s/meta_A" % CID,
    "assets/%s/prompt.txt" % CID,
    "assets/%s/task_brief.md" % CID,
]

test_rationale = (
    "14 条断言：①submit.zip 合法且含 remove_token.py，源码无禁用 import(socket/urllib/requests/pty/http)且不引金标模块 "
    "②remove_token.py py_compile 通过 ③在隐藏 B(token=R_SrefOsc)上运行 exit 0 且产出非空 JSON 报告 "
    "④报告含 keys root/token/si_inp_found/files_modified/total_occurrences_removed/files "
    "⑤报告 token==R_SrefOsc 且 si_inp_found/files_modified/total_occurrences_removed==金标(B) "
    "⑥files[] 长度==si_inp_found 且每条含 path/modified/occurrences_removed/line_preview "
    "⑦逐文件 (modified, occurrences_removed)==金标按路径对齐 ⑧B 中任一 si.inp 不再含整词 token(\\b 残留检查) "
    "⑨每个 si.inp 行数不变(未增删行) ⑩非 target 文件(si.inp.bak/run.sh/notes.txt)sha256 不变 "
    "⑪decoy 子串 R_SrefOscTrim 在 corner_B6 仍存在 + 每个 ignore 行双引号仍成对(2 个) "
    "⑫反硬编码:在可见 A(token=T_mBistOsc)上重跑 report.token==T_mBistOsc 且 files_modified>0 且 A 报告≠B 报告;源码不含 B-only token 字面量 R_SrefOsc "
    "⑬源码无 /rundata /proj /home/mike MatrixRun dscqa finesim DDR6TOP 硬编码路径且不引金标 "
    "⑭确定性:3 次重跑(root 规范化后)报告 sha256 一致"
)

case = {
    "task_id": CID,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": attachments,
    "entry_point": "outputs/submit.zip",
    "test": CHECK_SRC,
    "metadata": {
        "domain": "schematic_netlist",
        "track": "faithful",
        "layer": "L1",
        "k_check": 14,
        "k_rationale": 14,
        "trace_source": {
            "user": "mike",
            "host": "10.129.32.80",
            "session_file": "1789611712575_5tdum.messages.json",
            "match_count": 80,
            "real_task_summary": (
                "用户(mike@10.129.32.80)逐字 U#0(pinyin)「这个路径下有很多目录，每个目录下有个 si.inp 文件，"
                "帮我写个命令，我要删掉 si.inp 中 T_mBistOsc 字符串」——纯提需求未给根因/修复，符合 A 档前提。"
                "trace 演化(51 msg):agent list_allowed_files 枚举 Meta 根 25 corner 子目录(primesim.Meta001_..._FF/SS/TT.X2P6/X1P12)"
                "+read_files 抽样 si.inp 定位 T_mBistOsc 在第 55 行 .option finesim_ignore=\"...\" +find/grep/search_codebase 确认所有 corner 同构"
                "+editor 逐文件替换 line 55(去 T_mBistOsc 含尾空格) 但 policy 限 /rundata 不可写。"
                "真实 /rundata Meta 树不可附加→B-grade synthesized(meta_A 树 6 corner 各含 si.inp,token T_mBistOsc 在 ignore 行)。"
                "金标 remove_token_ref.py: <root> <token> [--out] os.walk 找 si.inp 按 \\b 整词移除 token(处理引号边界+拒绝子串) 原地改写+JSON 报告。"
                "hidden B=meta_B 树 8 corner token R_SrefOsc 含边例(首/尾/唯一/跨两行/decoy 子串 R_SrefOscTrim/无 token)反硬编码。"
            ),
        },
        "test_rationale": test_rationale,
    },
}

# gate: k_rationale == k_check >= 8
assert case["metadata"]["k_rationale"] == case["metadata"]["k_check"] >= 8, "assertion gate failed"

jsonl = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")
# guard: no duplicate task_id
with open(jsonl, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        if json.loads(line).get("task_id") == CID:
            raise SystemExit("ERROR: %s already in D.jsonl" % CID)
with open(jsonl, "a", encoding="utf-8") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")

# verify test==disk sha
import hashlib
disk = hashlib.sha256(open(os.path.join(REF_DIR, "check.py"), "rb").read()).hexdigest()[:12]
embedded = hashlib.sha256(CHECK_SRC.encode("utf-8")).hexdigest()[:12]
print("appended %s (k=14, test==disk sha %s, attachments=%d)" % (CID, disk == embedded, len(attachments)))
print("D.jsonl now:", sum(1 for _ in open(jsonl)), "lines")
