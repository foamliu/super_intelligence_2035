#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-HcellPairGen-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-HcellPairGen-001"
JSONL = os.path.join(BASE, "EDA-Eval-DesignFlow_C.jsonl")
A = os.path.join(BASE, "assets", CASE)
R = os.path.join(BASE, "reference", CASE)

with open(os.path.join(R, "check.py")) as f:
    test_field = f.read()
with open(os.path.join(A, "prompt.txt")) as f:
    prompt_field = f.read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_field,
    "prompt": prompt_field,
    "attachments": [
        f"assets/{CASE}/layout_cells_A",
        f"assets/{CASE}/source_cells_A",
        f"assets/{CASE}/existing_hcell_A",
        f"assets/{CASE}/cci_lvs_log_A",
        f"assets/{CASE}/task_brief.md",
        f"assets/{CASE}/prompt.txt",
    ],
    "metadata": {
        "trace_source": {
            "user": "kaixuanx",
            "host": "hfeg0pkn002",
            "session_file": "1793707420467_xqeql.messages.json",
            "match_count": 181,
            "real_task_summary": (
                "用户跑 Calibre LVS 抽 PEX，hcell 文件不全，calibre 报 "
                "'Terminate LPE running due to CCI-LVS run failed'，日志含 "
                "'WARNING: hcell missing: layout \"<L>\" source \"<S>\"' / "
                "'source ?' 两类报错。trace 中 agent 写 find_hcell.py (hcell "
                "文件 stat/recon) 与 find_hcell2.py (后仿验证器，hcell 生成逻辑"
                "被覆盖丢失)。本案 B 档重定义为离线 hcell 配对生成器：依据 layout "
                "/source 层级 + 已有 hcell + CCI-LVS 缺失 hcell 日志，生成完整 "
                "hcells 文件（已有优先、Type-1 显式配对校验层级、Type-2 按名称"
                "大小写+去结尾 _<数字> 匹配解析 source）。"
            ),
        },
        "domain": "physical_verify",
        "shard": "C",
        "track": "B-synthesized",
        "level": "L1",
        "harness": "cline",
        "test_rationale": (
            "18 条断言：① zip 含 gen_hcell.py 且 >=200B UTF-8 无 NUL "
            "② py_compile 通过且仅用标准库(禁 calibre/numpy/pandas/gdspy 等) "
            "③ B 输入下脚本 exit 0 且输出非空且 stdout 无 Traceback "
            "④ B 输出首行恰为 header 注释行 "
            "⑤ B 输出每个非注释/非空行恰含 2 个空白分隔 token(合法 hcells 配对格式) "
            "⑥ B 已有 hcell 配对按原序保留且排在所有日志派生配对之前 "
            "⑦ B 已有优先：pfd_core 与已有 'pfd_core' 配对而非日志 'pfd_core_dup' "
            "⑧ B Type-1 显式配对(vco_lc_tank/div2_sync/div4_async/reg_vdd_bandgap/esd_diode)全在且 L->S 正确 "
            "⑨ B 被过滤的 Type-1 'ghost_cell'(不在层级文件)不出现在输出 "
            "⑩ B Type-2 大小写不敏感精确匹配解析到 source 原始名(cp_curr_mirror->CP_Curr_Mirror/bg_core->BG_Core/ptat_gen->PTAT_Gen) "
            "⑪ B Type-2 去结尾 _<数字> 后匹配 'loop_filter'->'loop_filter_3' "
            "⑫ B Type-2 精确匹配 'bg_trim_net'->'bg_trim_net' 在输出 "
            "⑬ B 输出无重复 layout cell(每个 layout cell 至多出现一次) "
            "⑭ B2 退化输入 exit 0 且输出 header+恰 4 对 L==S(无已有/无规范化/无过滤) "
            "⑮ B3 空输入(LVS 通过无 missing-hcell) exit 0 且输出仅 header 行无配对行 "
            "⑯ A(可见)输出与 golden_A.hcells 字节相等 "
            "⑰ 反硬编码：B 输出与 golden_B.hcells 字节相等(B 用不同 cell 集) "
            "⑱ 缺失输入文件时非零退出且 stdout 无未捕获 Traceback"
        ),
    },
}

# guard: test field must equal disk check.py bytes
with open(os.path.join(R, "check.py")) as f:
    disk = f.read()
assert test_field == disk, "test field != disk check.py"

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", CASE, "to", JSONL)
# count lines
with open(JSONL) as f:
    n = sum(1 for _ in f)
print("jsonl_C lines now:", n)
