#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-FmFreqVsTAnalyze-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, hashlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-FmFreqVsTAnalyze-001"
CHECK_PATH = os.path.join(BENCH, "reference", CASE, "check.py")

with open(CHECK_PATH, "r") as f:
    check_src = f.read()
test_sha8 = hashlib.sha256(check_src.encode()).hexdigest()[:8]

prompt = (
    "你是 IC 设计工程师，使用 Synopsys WaveView ACE（Tcl）分析一个 FM（调频）信号的瞬时频率。"
    "请编写一个 Tcl ACE 脚本，计算一个 FM（调频）信号的瞬时频率随时间变化曲线，并在新的 WaveView 窗口中显示。要求：\n\n"
    "1. 定义过程 f_vs_t，接收信号对象 sig 和电压阈值 v_thr\n"
    "2. 创建一个新的波形数据对象（名为 \"frequency\"，analog 类型）\n"
    "3. 对输入信号创建 RISE 扫描并设置电压阈值\n"
    "4. 遍历所有上升沿数据点，计算相邻两个上升沿之间的频率 f = 1/(t2 - t1)\n"
    "5. 将每个频率值及其对应时间 (t2, freq) 追加到新波形中\n"
    "6. 主程序打开 ./wave.dat 波形文件，获取信号 \"wave\"，调用 f_vs_t\n"
    "7. 结果文件单独保存在一个顶层项目中\n\n"
    "你可以使用 search_api、get_api_details 和 run_code 工具完成任务，入参类型均是 tcl。\n\n"
    "（真实 trace: user=e0023936 @ hfhds201, session 1793095651315_qb1ua, mc=104；"
    "脚本须可配置，从 config.json 读取 wave_file/signal/threshold/out_file/carrier_freq_hz 字段以参数化。）"
)

rationale = (
    "19 条断言："
    "① submit.zip 合法 zip 且含 fm_freq_vs_t.tcl "
    "② 候选 Tcl 经嵌入 sx_stub.tcl 用 tclsh 在独立临时目录真跑无 source/语法错误(§4.2) "
    "③ 定义 proc f_vs_t {sig v_thr} "
    "④ f_vs_t 调 sx_create_signal \"frequency\" analog "
    "⑤ f_vs_t 调 sx_create_scan RISE "
    "⑥ f_vs_t 调 sx_set_threshold 用 v_thr 参数 "
    "⑦ f_vs_t 用 sx_scan_first + sx_scan_next 构成上升沿遍历循环 "
    "⑧ f_vs_t 调 sx_fetch_x 取上升沿时刻 "
    "⑨ f_vs_t 计算 1.0/(t2-t1)（相邻上升沿倒数） "
    "⑩ f_vs_t 调 sx_append_data 追加 (t2, freq) "
    "⑪ f_vs_t 调 sx_free_scan 释放扫描 "
    "⑫ subprocess 隐藏 B: sx_open_sim_file_read 用 B 的 wave_file(./fm_input.wdf) "
    "⑬ subprocess B: sx_find_wave_in_file 用 B 的 signal(fm_carrier) "
    "⑭ subprocess B: sx_set_threshold 用 B 的 threshold(0.5) "
    "⑮ subprocess B: sx_write_open 用 B 的 out_file(inst_freq_out.wdf) 且 sx_write_close "
    "⑯ subprocess B: 调 sx_display_wave + sx_update_wv 显示 "
    "⑰ subprocess B: 追加频率值 ≈ B carrier_freq(2.5MHz, 容差 1%) 且 ≥2 个点 "
    "⑱ subprocess 隐藏 B2(随机化): find_wave_in_file/set_threshold/write_open 用 B2 值(fm_mod/0.8/ifreq_curve.wdf) 反硬编码 A "
    "⑲ subprocess B2: 追加频率 ≈ B2 carrier_freq(500kHz, 容差 1%)"
)

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        f"assets/{CASE}/prompt.txt",
        f"assets/{CASE}/task_brief.md",
        f"assets/{CASE}/config_A.json",
    ],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "e0023936",
            "host": "hfhds201",
            "session_file": "1793095651315_qb1ua.messages.json",
            "match_count": 104,
            "real_task_summary": (
                "USER#1/#3 (逐字原文): '编写一个 Tcl ACE 脚本，计算一个 FM（调频）信号的瞬时频率随时间变化曲线，"
                "并在新的 WaveView 窗口中显示' + 7 条算法规格(定义 f_vs_t(sig,v_thr)/创建 frequency analog/RISE 扫描设阈值/"
                "遍历上升沿算 f=1/(t2-t1)/追加(t2,freq)/主程序打开 ./wave.dat 取 wave 调 f_vs_t/结果存独立顶层项目)。"
                "纯提需求未给根因修复 → A档任务说明。trace 123 msgs/8 user turns, WaveView ACE Tcl; assistant 经 RAG search_apis + "
                "SandBox run_code(tcl,32次) + editor(5) 实测 API 序列, 产出 /home/e0023936/fm_freq_vs_t.tcl "
                "(f_vs_t: sx_create_signal/sx_create_scan RISE/sx_set_threshold/sx_scan_first+next/sx_fetch_x/1.0/(t2-t1)/"
                "sx_append_data/sx_free_scan; main: sx_new_wv/sx_open_sim_file_read/sx_find_wave_in_file/sx_write_open+add+close/"
                "sx_display_wave+sx_update_wv)。本案 config-driven 化(load_config/cfg_get 读 config.json) 以支持隐藏 B 反硬编码。"
            ),
        },
        "domain": "eda_other",
        "track": "faithful",
        "layer": "L1-static",
        "harness": "cline",
        "test_sha8": test_sha8,
        "test_rationale": rationale,
        "self_verify": (
            "REF PASS 19/19 (a-s) on /tmp/judge_fmfmt 独立目录; "
            "5 negatives 全 FAIL distinct first_fail {c,d,g,i,l} "
            "(naive_empty->c / naive_hardcode_a->l / naive_print_expected->d / naive_core_deleted->i / naive_no_loop->g); "
            "§4.9 三假(empty->c / print_expected->d / core_deleted->i) 全 FAIL; "
            "negative_selftest PASS (REF_PASS=True ALL_FAIL=True DISTINCT_CONDS=5). "
            "subprocess 经 tclsh+嵌入 sx_stub.tcl 真跑候选 on B+B2 (§4.2); B/B2 随机化(§4.5)."
        ),
        "hidden_B": (
            "config_B.json: wave_file=./fm_input.wdf, signal=fm_carrier, threshold=0.5, out_file=inst_freq_out.wdf, carrier_freq_hz=2500000 "
            "(结构对立于 A 的 ./wave.dat/wave/1.65/frequency_result.wdf/1MHz); "
            "config_B2.json: ./fm_mod_signal.wdf/fm_mod/0.8/ifreq_curve.wdf/500000 (随机化). "
            "check.py 嵌入 sx_stub.tcl 按 carrier 生成上升沿 t_k=k/carrier, 验候选 f=1/(t2-t1)≈carrier."
        ),
        "A_assets_note": (
            "A assets: prompt.txt(U#3 逐字 7 要求) + task_brief.md(交付接口≤3行: submit.zip 含 fm_freq_vs_t.tcl, "
            "读 config.json 的 wave_file/signal/threshold/out_file/carrier_freq_hz) + config_A.json(真实 A 配置). "
            "不含 check.py/reference/hidden/negative/jsonl (§4.8 泄漏隔离)."
        ),
    },
}

jsonl_path = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify roundtrip: test field == disk check.py
with open(jsonl_path) as f:
    last = json.loads(f.readlines()[-1])
assert last["test"] == check_src, "test field != disk check.py"
assert last["id"] == CASE
print(f"appended {CASE} to {jsonl_path}")
print(f"test_sha8={test_sha8} test_len={len(check_src)} k_check=19(a-s) k_rationale=19")
print("roundtrip OK: test field == disk check.py")
