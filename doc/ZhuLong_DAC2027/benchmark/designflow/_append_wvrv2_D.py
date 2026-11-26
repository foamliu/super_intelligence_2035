#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-WvFsdbReaderV2Gen-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json
import os

CASE = "EDA-Eval-DesignFlow-WvFsdbReaderV2Gen-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = os.path.join(ROOT, "reference", CASE)

with open(os.path.join(REF, "check.py"), "r", encoding="utf-8") as f:
    check_src = f.read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": (
        "请你阅读skill目录，找到这两个阅读波形的skill，请你修改waveview-fsdb-reader"
        "再写一个waveview-fsdb-readerV2.py，让他可以像finesim-fsdb-reader一样"
        "对读出的信号生成一个简单的分析报告"
    ),
    "attachments": [
        "assets/%s/prompt.txt" % CASE,
        "assets/%s/task_brief.md" % CASE,
        "assets/%s/waveview_fsdb_reader.py" % CASE,
        "assets/%s/fsdb_reader.py" % CASE,
        "assets/%s/SKILL_wv.md" % CASE,
        "assets/%s/SKILL_fs.md" % CASE,
    ],
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "metadata": {
        "domain": "waveform",
        "track": "faithful",
        "layer": "L1",
        "k_check": 14,
        "k_rationale": 14,
        "trace_source": {
            "user": "e0039602",
            "host": "10.129.8.136",
            "session_file": "1789895350779_hoh52.messages.json",
            "match_count": 64,
            "real_task_summary": (
                "用户要求阅读 skill 目录，找到 waveview-fsdb-reader 与 finesim-fsdb-reader "
                "两个读波形 skill，修改前者并新写 waveview-fsdb-readerV2.py，使其能像 "
                "finesim-fsdb-reader 一样对读出的信号生成简单分析报告。trace 中 agent 用 "
                "list_allowed_files/read_files 读两个 skill 的 waveview_fsdb_reader.py"
                "(wv -ace_no_gui 后端，返回 {sig:[(t,v)...]}) 与 fsdb_reader.py(fscript + "
                "analyze_signal: 数字边沿/脉冲计数、模拟统计+过零点)，合并出 V2：复用 "
                "WaveViewReader 读信号 + detect_signal_type 自动分类 + 数字(detect_edges/"
                "detect_pulses)/模拟(analog_stats/zero_crossings) 分析 + format_report + "
                "argparse CLI(fsdb_path/signals/step/t_start/t_end/--direct/--thresh)。"
                "B-grade synthesized: 真实 .fsdb/test.fsdb 在 .75 permission-denied 不可附加，"
                "check 用合成波形数据(数字时钟 0<->1 + 模拟电流基线+高斯负尖峰)直接测 V2 的"
                "分析函数，stub waveview_fsdb_reader 使导入无需真实 wv 二进制。"
            ),
        },
        "test_rationale": (
            "14 条断言：①submit.zip 含 *reader*V2*.py 且无 check/reference/hidden/"
            "extract_ref/金标/negative_selftest 等泄题条目与禁用 import "
            "②V2 脚本 py_compile 通过(语法合法) "
            "③V2 复用 waveview_fsdb_reader 后端(源码含 waveview_fsdb_reader 且引用 "
            "WaveViewReader/read_signals) "
            "④analyze_signal 对隐藏 B 数字信号判 digital、模拟信号判 analog(双电平驻留 vs "
            "单电平+尖峰) "
            "⑤数字报告 n_rising/n_falling/n_edges/n_pulses 计数与独立金标在 B 上一致 "
            "⑥数字 edges 列表(时间, 方向)与金标越过 thresh=0.25 边沿逐条匹配(时间容差 1e-15) "
            "⑦数字 pulses 列表(start, end, width)与金标高脉冲逐条匹配 "
            "⑧模拟 analog_stats 的 v_min/v_max/v_mean/n_points/t_start/t_end 与金标一致"
            "(数值容差 1e-9) "
            "⑨模拟 zero_crossings 计数及每条(线性插值时间, rising/falling 方向)与金标匹配 "
            "⑩format_report 经子进程执行候选脚本产出可读报告含 === Signal:/Type/Data points/"
            "Time range/Total edges/Total pulses 结构标签 "
            "⑪CLI --help 经子进程执行暴露 fsdb_path/signals/step/--direct/--thresh 五参数 "
            "⑫read_and_analyze 与 analyze_signals 两个捆绑函数存在且可调用(读信号+分析一体化) "
            "⑬反硬编码:B 与 B2(不同 toggle 周期/尖峰中心/深度/信号名)运行结果不同(数字 "
            "n_edges/n_pulses 异 或 模拟 v_min/v_max 异)，证明数据驱动 "
            "⑭确定性:3 次重跑 analyze_signal(B) 报告 sha256 一致；V2 源码无 "
            "/rundata|/proj|/home 硬编码主机路径"
        ),
    },
}

jsonl = os.path.join(ROOT, "EDA-Eval-DesignFlow_D.jsonl")
line = json.dumps(entry, ensure_ascii=False)
# idempotency guard: remove any prior line with same task_id
if os.path.exists(jsonl):
    with open(jsonl, "r", encoding="utf-8") as f:
        kept = [ln for ln in f if ln.strip()
                and json.loads(ln).get("task_id") != CASE]
else:
    kept = []
kept.append(line)
with open(jsonl, "w", encoding="utf-8") as f:
    for ln in kept:
        f.write(ln.rstrip("\n") + "\n")
print("appended %s -> D.jsonl (now %d lines)" % (CASE, len(kept)))
