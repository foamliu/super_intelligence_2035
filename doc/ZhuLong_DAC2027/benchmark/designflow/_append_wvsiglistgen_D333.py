#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-WvSigListGen-001 to shard D jsonl."""
import json, os, base64

HERE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-WvSigListGen-001"
ASSETS = os.path.join(HERE, "assets", CASE)
REF = os.path.join(HERE, "reference", CASE)

# read check.py bytes for the test field
with open(os.path.join(REF, "check.py"), "r") as f:
    check_src = f.read()

prompt = open(os.path.join(ASSETS, "prompt.txt")).read().strip()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": ["assets/%s/spec_A.json" % CASE],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["gen_wv_sig.py"],
    "test": check_src,
    "budget": {"max_turns": 25, "timeout_sec": 1800},
    "metadata": {
        "domain": "waveform",
        "task_name": "WvSigListGen",
        "scenario": "DDR5 fullchip coretiming 仿真波形: 从网表提取的关键信号层次路径清单(按类别分组)生成 WaveView 可直接 load 的 .sig 信号列表文件,所有路径全小写(WaveView 硬约束),叶子信号 v() 包裹,总线位 <n> 保留,按类别分文件输出 + manifest.json",
        "direction": "signal spec JSON (groups of hierarchical paths) -> WaveView .sig signal-list files + manifest.json",
        "layer": "L1",
        "topic": "waveview .sig signal-list generator: lowercase normalization + v() leaf wrapping + bus-bit preservation + per-group file split",
        "difficulty": "medium",
        "design": "B-synthesized: trace 1793087996513_u78sz (hengbow DDR5 fullchip coretiming FSDB 波形, hengbow@hfeg0pgn045 mc407). shard A 已从同 trace 取 verification L2 意图(CoreTimingSig-001: coretiming 时序违例检查/分析); 本 case 取同 trace 不同意图=waveform L1 离线 .sig 信号列表生成(用户 U#2/U#4/U#5 提需求: 给出关键信号路径 list 让 waveview 直接 load, 弄成 sig_demo.sig 格式; U#8/U#13/U#24 用户硬约束 wv 只认小写; U#11 分文件; U#16/U#17 基于真实网表不猜测)。真实 /home/hengbow fsdb+netlist 不可附加(2GB/公共目录) -> B 档 synthesized 离线 generator(spec JSON 驱动)。不同意图+domain+L-level+check, 可辩护。",
        "track": "synthesized",
        "trace_source": {
            "user": "hengbow",
            "host": "hfeg0pgn045",
            "session_file": "1793087996513_u78sz.messages.json",
            "match_count": 407,
            "real_task_summary": "DDR5 fullchip coretiming FSDB 波形: 提取 WL/BL/地址/控制器关键信号 -> 生成 WaveView 可 load 的全小写 .sig 信号列表(分文件), 基于真实 netlist 层次不猜测; 用户反复强调 wv 只认小写"
        },
        "test_rationale": "16 条断言：① zip 含 gen_wv_sig.py 且不含 check/reference/negative/jsonl 等泄漏文件 ② gen_wv_sig.py 可 py_compile ③ B 真跑 subprocess exit 0 且产出非空 .sig 文件 ④ B 所有 signal= 行全小写(无大写字母, WaveView 硬约束) ⑤ B signal= 行格式为 v(leaf) 或 path.v(leaf)(总线位允许 <n> 在 v 内) ⑥ B 不使用 [n] 方括号作总线分隔符(必须 <>) ⑦ B 产出 .sig 文件数==spec_B 的 group 数 4 ⑧ B manifest.json 列全 N 文件名且各 n_signals 与实际行数一致 ⑨ B 每个 .sig 文件含其 spec group 的全部叶子信号(去重后) ⑩ B 层次路径用 . 分隔(无 / 或 ::) ⑪ B 单文件内 signal= 行无重复 ⑫ B .sig 文件含 # 注释行且注释行不被计为 signal ⑬ 反硬编码: 源码不含 A 专属信号名(ck_t/cm1_fc_rdlatencyto56/ra10gapin/ble_b<0>/xictop.xi_array8g_t)且 A-run 产出 v(ck_t)+v(ca<0>) ⑭ 跨输入 B2: B2-run 产出 B2 信号(serdes_top 层次)且 B2 group 数 3 != B 的 4 ⑮ 跨输入 B2: B2 所有 signal= 行无 < (B2 全标量模拟信号, 测无总线处理) ⑯ 确定性: B 跑 3 次全部输出文件 sha256 一致",
        "conditions_table": "a:zip-no-leak b:py_compile c:B-run-exit0-nonempty d:all-lowercase e:v(leaf)-format f:no-square-bracket-bus g:exactly-n_groups-sig-files h:manifest-files-and-counts i:per-file-leaf-coverage j:dot-hierarchy-separator k:no-dup-within-file l:comments-present-not-signals m:anti-hardcode-no-A-markers-and-A-run-produces-A n:cross-input-B2-serdes-and-different-group-count o:cross-input-B2-no-bus-bits p:deterministic-sha256"
    }
}

jsonl_path = os.path.join(HERE, "EDA-Eval-DesignFlow_D.jsonl")
# append
with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", jsonl_path)
# verify
import subprocess
n = int(subprocess.check_output(["wc", "-l", jsonl_path]).split()[0])
print("D.jsonl now", n, "lines")
# verify last line parses
with open(jsonl_path) as f:
    lines = f.readlines()
last = json.loads(lines[-1])
print("last task_id:", last["task_id"])
print("k_check labels:", len([c for c in "abcdefghijklmnop"]))
