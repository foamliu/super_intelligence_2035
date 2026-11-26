#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-LibToParm-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-LibToParm-001"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
CHECK = os.path.join(BENCH, "reference", CID, "check.py")
PROMPT = os.path.join(BENCH, "assets", CID, "prompt.txt")

with open(CHECK, encoding="utf-8") as f:
    test_field = f.read()
with open(PROMPT, encoding="utf-8") as f:
    prompt = f.read()

attachments = [
    "assets/EDA-Eval-DesignFlow-LibToParm-001/sram_demo_A.lib",
    "assets/EDA-Eval-DesignFlow-LibToParm-001/lib_timing_map.txt",
    "assets/EDA-Eval-DesignFlow-LibToParm-001/prompt.txt",
    "assets/EDA-Eval-DesignFlow-LibToParm-001/task_brief.md",
]

test_rationale = (
    "15 条断言：① submit.zip 含 lib_to_parm.py + timing_stress_A.parm 两件齐全 "
    "② lib_to_parm.py 可 py_compile "
    "③ 候选 lib→parm 转换器对可见 A bundle 运行 exit 0 并产出 parm "
    "④ A parm 恰好 25 行且每行 `.param name = value` 格式 "
    "⑤ A parm 25 行顺序与 PARM_ORDER(clkh…tcyc) 完全一致 "
    "⑥ A parm 各值与独立 oracle(不同代码路径解析 .lib)在 1e-15 内一致 "
    "⑦ A clkh 单位换算 ns→s 正确(130.03e-9) "
    "⑧ A tasr/tasf placeholder 0.1 → 输出 1e-10 "
    "⑨ A tdsr 总线 bit=max 聚合正确(取 bit1=30.06e-9 而非 bit0) "
    "⑩ A tchr hold 负值原样保留(-7.94e-9，不取绝对值) "
    "⑪ 候选对隐藏 B bundle 运行 exit 0 且 B parm 顺序正确 "
    "⑫ B parm 各值与独立 oracle 在 1e-15 内一致 "
    "⑬ 跨输入守卫 B parm 与 A 差异≥15 条(击破硬编 A) "
    "⑭ B placeholder 位置不同于 A(B tdsr=1e-10，A tdsr=30.06e-9 非占位) "
    "⑮ 反硬编 B clkh=170.03e-9 ≠ A clkh=130.03e-9"
)

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_field,
    "prompt": prompt,
    "attachments": attachments,
    "metadata": {
        "trace_source": {
            "user": "e0046686",
            "host": "hfeg0plg80",
            "session_file": "1792376325408_9eh38.messages.json",
            "match_count": 874,
            "real_task_summary": (
                "Liberty(.lib) timing extraction -> back-annotation parm for "
                "timing_stress.sp post-sim (verification) on hfeg0plg80 "
                "(e0046686); user turn #68 verbatim: 「当前接到一个任务："
                "【从lib提取timing给反标跑仿真】，需要在zk或者np的哪个工程的"
                "什么地方，如何进行修改？先给出任务梳理对任务进行拆解分析，"
                "给出修改目标内容给我，由我确认后再决定是否开始修改」 -- "
                "clean task request (received a new task: extract timing from "
                "lib for back-annotation sim), no root cause / fix given => "
                "A-grade rule 2 OK => A-grade faithful. 338-msg session; "
                "assistant delivered extract_lib_timing.py (lib->parm, 772L "
                "pure stdlib) under np/autosim_script/lib_timing_tools/, user "
                "accepted (turn #181-183 'finish remaining steps 7-9'). This "
                "case scopes a generic lib->parm converter (verb: lib-to-parm), "
                "distinct from all existing shard-A verbs (synth-upf-diagnose "
                "/ apr-stamp-fix / flat-net / apr-setup-audit / apr-log-audit "
                "/ vcs-equiv / itf-compare / calibre-pdf2md / flow-guide / "
                "tlef-rules / innovus-launch-diag / deadloop-scan / "
                "ostrich-spef-rc / impsr1253-vddpm-fix / redhawk-gen-inputs / "
                "pwr-globals / dc-synth / simlib-idx / power-fill / etc.)."
            ),
        },
        "domain": "verification",
        "track": "faithful",
        "test_rationale": test_rationale,
    },
}

# idempotency: remove any prior entry with same task_id
kept = []
with open(JSONL, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            kept.append(line)
            continue
        if d.get("task_id") != CID:
            kept.append(line)
with open(JSONL, "w", encoding="utf-8") as f:
    for line in kept:
        f.write(line.rstrip("\n") + "\n")
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify roundtrip
ids = []
with open(JSONL, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            d = json.loads(line)
            ids.append(d.get("task_id", "?"))
print("appended %s; A.jsonl now %d lines / %d unique ids" % (CID, len(ids), len(set(ids))))
# verify test field bytes match disk check.py
with open(CHECK, encoding="utf-8") as f:
    disk = f.read()
ok = (disk == entry["test"])
print("test==disk check.py roundtrip:", ok)
print("k_rationale count (①-⑮):", test_rationale.count("①") + sum(1 for ch in test_rationale if ch in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"))
