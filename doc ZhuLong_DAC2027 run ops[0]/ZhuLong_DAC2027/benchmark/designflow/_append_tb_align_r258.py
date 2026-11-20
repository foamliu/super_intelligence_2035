#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-TbAlignReport-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json
import os

ROOT = '/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow'
CASE = 'EDA-Eval-DesignFlow-TbAlignReport-001'
ASSETS_DIR = os.path.join(ROOT, 'assets', CASE)
REF_DIR = os.path.join(ROOT, 'reference', CASE)

prompt = (
    "请阅读rtl/文件夹内的修改记录markdown文件，以及最新的.v文件，调整一下testbench，符合最新的修改要求\n\n"
    "请写一个 Python3 脚本 `analyze_tb_alignment.py`（无第三方依赖），读取同目录 `manifest.json`"
    "（含 `modification_note`、`new_rtl`、`baseline_tb` 三个键，分别指向修改记录 markdown、"
    "新 RTL Verilog、基线 testbench Verilog），分析新 RTL 是否相对基线 TB 改变了 CR-edge 语义"
    "（列冗余 repair-store 边沿是否仍清空存储阵列 / 是否改为 Q=X 输出扰动脉冲），"
    "并在 stdout 输出结构化 JSON 报告（exit 0）。\n\n"
    "JSON 报告必须包含以下 11 个顶层字段：\n"
    "- `design_name`：RTL 模块名（字符串）\n"
    "- `tb_name`：testbench 模块名（字符串）\n"
    "- `version_old`：基线 TB 的旧版本号（从 TB 文件 `Version:` 注释解析，字符串）\n"
    "- `note_rule`：修改记录中的黄金规则标签（形如 `G[0-9]+`，字符串）\n"
    "- `cr_signals`：RTL 端口中 CR 使能类信号名列表（排除 CR 地址类信号，字符串列表）\n"
    "- `old_check_count`：基线 TB 中依赖旧 CR-edge 清空行为的检查数量（整数）\n"
    "- `old_check_labels`：上述检查的标签列表（从 $display 字符串派生，字符串列表）\n"
    "- `rtl_clears_mem_on_cr_edge`：新 RTL 在 CR 边沿是否仍清空存储阵列（布尔）\n"
    "- `rtl_qx_pulse_on_cr_edge`：新 RTL 在 CR 边沿是否改为输出 Q=X 扰动脉冲（布尔）\n"
    "- `needs_alignment`：TB 是否需要迁移（不再清空阵列且存在旧检查时为 True，布尔）\n"
    "- `summary`：一句话结论（字符串）\n\n"
    "交付：把 `analyze_tb_alignment.py` 打包成 `outputs/submit.zip`（zip 内顶层就是该 .py 文件）。\n"
)

attachments = [
    'assets/' + CASE + '/modification_note.md',
    'assets/' + CASE + '/new_rtl.v',
    'assets/' + CASE + '/baseline_tb.v',
    'assets/' + CASE + '/config_a.json',
    'assets/' + CASE + '/prompt.txt',
    'assets/' + CASE + '/task_brief.md',
]

check_src = open(os.path.join(REF_DIR, 'check.py'), encoding='utf-8').read()

rationale = (
    "14 条断言："
    "① submit.zip 内含 analyze_tb_alignment.py "
    "② analyze_tb_alignment.py 通过 py_compile 无语法错 "
    "③ 候选在隐藏 B（重标签变体 CRSENL/CRSENR/G3/版本 8.5）上 exit 0 且输出含全部 11 个必需键的合法 JSON "
    "④ design_name == B 期望(sram_sp) "
    "⑤ tb_name == B 期望(tb_sram_sp) "
    "⑥ version_old == B 期望(8.5，非 A 的 9.5) "
    "⑦ note_rule == B 期望(G3，非 A 的 G1) "
    "⑧ cr_signals == B 期望([CRSENL,CRSENR]，非 A 的 CRSLE/CRSRE，排除 CRANL/CRANR 地址信号) "
    "⑨ old_check_count == B 期望(5) "
    "⑩ old_check_labels 为重标签集（含 CRSENL/CRSENR，不含 A 的 CRSLE/CRSRE） "
    "⑪ rtl_clears_mem_on_cr_edge == B 期望(False，新 RTL 不再清空阵列) "
    "⑫ rtl_qx_pulse_on_cr_edge == B 期望(True，新 RTL 改为 Q=X 脉冲) "
    "⑬ needs_alignment == B 期望(True) "
    "⑭ B' 跨输入守卫：候选在结构异构 B'（CRSLE/CRSRE/G7/版本 7.2，RTL 仍清空阵列）上派生值须匹配 B' 期望(clears=True/needs=False/count=0/rule=G7，且与 B 不同)"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "lorikx",
            "host": "hfeg0pkn001",
            "session_file": "1793069875156_c6xow.messages.json",
            "match_count": 149,
            "real_task_summary": (
                "lorikx 在 sim/tb_sp_sram.v 上向 cline 请求按 rtl/ 修改记录 markdown 与最新 .v "
                "调整 testbench 符合最新修改要求；cline 阅读修改记录(G1 黄金规则：CRSxE 边沿不再清空"
                "存储阵列，仅产生 Q=X 输出扰动脉冲)与新版 sram_sp.v，将 tb_sp_sram.v 由 v9.5 迁移到 v9.6"
                "：移除 5 处 'mem=X / mem not X after CRSxE' 旧检查，新增 snap_mem_cr_edge / "
                "check_qx_after_cr_edge / check_mem_cr_edge_unchanged 三类检查任务（各 8 次调用），"
                "更新 changelog 与版本号"
            ),
        },
        "domain": "digital",
        "test_rationale": rationale,
        "track": "faithful",
        "shard": "A",
        "test_sha8": "6d7d4dd4",
    },
}

out_path = os.path.join(ROOT, 'EDA-Eval-DesignFlow_A.jsonl')
line = json.dumps(entry, ensure_ascii=False)
# idempotency guard: remove any prior entry with same task_id
kept = []
removed = 0
with open(out_path, encoding='utf-8') as f:
    for ln in f:
        try:
            d = json.loads(ln)
            if d.get('task_id') == CASE:
                removed += 1
                continue
        except Exception:
            pass
        kept.append(ln if ln.endswith('\n') else ln + '\n')
with open(out_path, 'w', encoding='utf-8') as f:
    f.writelines(kept)
    f.write(line + '\n')
print('removed prior:', removed)
print('appended. total lines now:', len(kept) + 1)
print('k_rationale == k_check:', rationale.count('①') > 0, 'assertions=', sum(1 for c in '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭' if c in rationale))
