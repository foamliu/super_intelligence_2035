#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-DcUpfDiag-001 to EDA-Eval-DesignFlow_A.jsonl."""
import os, json

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID  = "EDA-Eval-DesignFlow-DcUpfDiag-001"
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_A.jsonl")
REF_DIR = os.path.join(ROOT, "reference", CID)
A_DIR   = os.path.join(ROOT, "assets", CID)

# check.py source -> test field
with open(os.path.join(REF_DIR, "check.py"), encoding="utf-8") as f:
    check_src = f.read()

PROMPT = """DC synthesis UPF / save_upf 诊断 (HL22 porting, test_chip workspace)。

用户原话（逐字，A 档 faithful）：
「检查synth/scripts中的dc.tcl和upf/test_chip_power.upf定义，推测dc结果save_upf输出的upf文件为空的问题，而且dc产生的netlist无VDD/VSS」

附件 bundle 是该 DC synthesis 运行的真实产物（dc.tcl 驱动 + test_chip_power.upf 电源意图 + dc_setup_filenames.tcl + sim.upf + dc.log 运行日志 + snps_upf.log UPF 加载回显 + dc.upf save_upf 输出 + postsyn_head.v 网表头 + rtl_top.v 顶层端口段）。

交付接口（仅说明交付形态与文件位置，不补充任务意图）：
- mode: design_flow
- entry_point: outputs/submit.zip
- test: check(deliverable, workdir)

请实现一个**通用 DC UPF / save_upf 诊断器** `diagnose_upf.py`，CLI `diagnose_upf.py <bundle_root> [-o out.json]`，纯 stdlib 解析 bundle 内的 dc.tcl + UPF + dc.log + dc.upf + postsyn_head.v + rtl_top.v，对两个症状（save_upf 输出为空、netlist 无 VDD/VSS）推断根因，输出结构化 `diagnosis.json`（schema：`save_upf_empty{root_cause, mechanism, evidence, fix, is_defect}` + `netlist_no_pg{root_cause, mechanism, evidence, is_defect}` + `latent_issues[{id, severity, desc, fix}]`）。

诊断器必须**通用自适应**：从 bundle 文件动态推断根因，不硬编任何 design 名或特定答案；同一诊断器能对结构不同的 bundle 给出不同根因。

交付：把 `diagnose_upf.py` + `diagnosis_A.json`（用该诊断器对可见 A bundle 跑出的结果）打包为 `outputs/submit.zip`。
"""

ATTACHMENTS = [os.path.join("assets", CID, fn) for fn in sorted(os.listdir(A_DIR))
               if fn != "hidden"]

METADATA = {
    "trace_source": {
        "user": "alan3zh",
        "host": "hfeg0pkn001",
        "session_file": "1793362556805_gytxt.messages.json",
        "match_count": 440,
        "real_task_summary": (
            "DC synthesis UPF/save_upf empty-output diagnosis for test_chip_v1 "
            "(HL22) on hfeg0pkn001 (alan3zh); user turn 0 verbatim: 「检查"
            "synth/scripts中的dc.tcl和upf/test_chip_power.upf定义，推测dc结果"
            "save_upf输出的upf文件为空的问题，而且dc产生的netlist无VDD/VSS」 -- "
            "user gives SYMPTOMS only (empty save_upf + netlist no PG), no root "
            "cause / fix => A-grade rule 2 OK => A-grade faithful. 48-msg session; "
            "assistant msg#47 delivered full diagnosis verified against real files: "
            "(1) save_upf empty == -supplemental expected (golden UPF + 0 isolation/"
            "level-shifter/retention => 0 delta => only 2-line comment header, NOT "
            "a defect; fix = drop -supplemental or load original UPF downstream; "
            "(2) netlist no VDD/VSS == DC write -format verilog never emits PG pins, "
            "PG intent travels via UPF+DDC, RTL top has no VDD port, NOT a defect; "
            "(3) latent: load_upf after link (warn), comma in set_port_attributes "
            "port list (dormant bug), -include_scope -elements {.} redundant (info). "
            "This case scoping a reusable generic DC-UPF diagnostic (verb: "
            "synth-upf-diagnose), distinct from AprSetupAudit / AprLogAudit / "
            "AprStampFix / VcsEquiv / FlatNet.")
    },
    "domain": "digital",
    "track": "faithful",
    "test_rationale": (
        "14 条断言：① submit.zip 含 diagnose_upf.py + diagnosis_A.json 两件齐全 "
        "② diagnose_upf.py 可 py_compile ③ 候选诊断器对 A bundle 运行 exit 0 并产 "
        "diagnosis_A.json ④ dA.save_upf_empty.root_cause == \"supplemental_zero_delta"
        "\"（与独立 oracle 重算一致） ⑤ dA.save_upf_empty.is_defect == false（非缺陷）"
        " ⑥ dA.save_upf_empty.evidence 含 UPF-214(0 isolation) + enable_golden_upf "
        "⑦ dA.netlist_no_pg.root_cause == \"dc_write_verilog_no_pg\" 且 is_defect == "
        "false ⑧ dA.latent_issues 含 load_upf_order + comma_in_set_port_attributes "
        "+ redundant_include_scope 三条 ⑨ dA.save_upf_empty.fix 含 \"去 -supplemental"
        "\" 语义 ⑩ 候选诊断器对隐藏 B bundle 运行 exit 0 ⑪ 跨输入守卫：dB."
        "save_upf_empty.root_cause == \"upf_not_loaded\"（≠ A 的 "
        "supplemental_zero_delta，B 的 load_upf 被注释） ⑫ 跨输入守卫：dB."
        "latent_issues 不含 comma_in_set_port_attributes（B 用空格分隔） ⑬ 反硬编："
        "候选脚本不含 A 的 design 名 hl22_porting_test_chip_v1 字面量 ⑭ dA 与 dB 的 "
        "save_upf_empty.root_cause 不同（防同答）")
}

rec = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": PROMPT,
    "attachments": ATTACHMENTS,
    "metadata": METADATA,
}

# idempotent: drop existing record with same task_id
kept = []
if os.path.isfile(JSONL):
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                kept.append(line)
                continue
            if o.get("task_id") != CID:
                kept.append(line)

with open(JSONL, "w", encoding="utf-8") as f:
    for line in kept:
        f.write(line + "\n")
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print("appended:", CID)
print("A.jsonl lines now:", len(kept) + 1)
print("attachments:", len(ATTACHMENTS))
