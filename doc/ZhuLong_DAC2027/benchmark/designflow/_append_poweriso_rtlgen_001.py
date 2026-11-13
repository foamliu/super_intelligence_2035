#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-PowerIsoCellRtlGen-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os, sys

CASE = "EDA-Eval-DesignFlow-PowerIsoCellRtlGen-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF_DIR = os.path.join(BENCH, "reference", CASE)
ASSET_DIR = os.path.join(BENCH, "assets", CASE)

prompt = """[design_flow] Power Isolation Cell 行为级 RTL 模型 (power isolation cell behavioral RTL model)

背景
e0045144 在 `/home/e0045144/jtag/ACC/run/` 下做 JTAG/ACC 相关的低功耗设计验证，需要一个
**power isolation cell（电源隔离单元）的行为级 RTL 模型**——用于在仿真里抽象掉断电域
（power-off domain）过来的信号：当 isolation enable 有效时把输出隔离掉，防止浮动/不确定值
传导进常开域（always-on domain）；isolation 无效时数据透明直通。

e0045144 原话（核心 produce-task）：「帮我写一个 power iso 的 design」，并明确要的是
**一个隔离单元（ISO cell）的行为级 RTL 模型，含 enable 保持/取值逻辑**（即隔离生效时要么
把输出钳到固定值，要么保持生效前一刻的数据）。真实芯片里这类单元应例化标准单元库里的
`ISO_CLAMPxx`/`ISO_LATCHxx`/`ISO_LEVELxx`，本任务只做行为级仿真模型，不需例化真实库单元。

任务
交付两个文件，打包进 `outputs/submit.zip`：

1. `power_iso.v` — Verilog 行为级 RTL 模型，**参数化**，必须对任意配置成立（不能写死某一组取值）。
   定义三个模块：
   - `power_iso_clamp`（钳位型）：参数 `WIDTH`(默认1)/`CLAMP_VAL`(默认1'b0)/`ISO_EN_ACTIVE`(默认1'b1)；
     端口 `iso_en`/`din`/`dout`；极性 `wire iso_act = (ISO_EN_ACTIVE==1'b1) ? iso_en : ~iso_en;`
     逻辑 `assign dout = iso_act ? {WIDTH{CLAMP_VAL}} : din;`（隔离生效→输出钳到 WIDTH 位全 CLAMP_VAL，否则透明）。
   - `power_iso_keep`（保持型）：参数 `WIDTH`(默认1)/`INIT_VAL`(默认1'b0)/`ISO_EN_ACTIVE`(默认1'b1)；
     端口 `iso_en`/`clk`/`rstn`/`din`/`dout`(reg)；同样的极性 wire；
     时序 always（异步低有效复位）：`if (~rstn) dout <= {WIDTH{INIT_VAL}}; else if (iso_act) dout <= dout; else dout <= din;`
     （复位→INIT_VAL，隔离生效→保持，否则→跟随 din）。
   - `power_iso`（顶层选择）：参数 `WIDTH`/`ISO_TYPE`(默认"CLAMP")/`CLAMP_VAL`/`INIT_VAL`/`ISO_EN_ACTIVE`；
     端口 `iso_en`/`clk`/`rstn`/`din`/`dout`；用 `generate` 块按 `ISO_TYPE=="KEEP"` 切换：KEEP 例化
     `power_iso_keep`，否则（含 CLAMP）例化 `power_iso_clamp`；两分支各带 generate label（如 `g_keep`/`g_clamp`）。

2. `verify_model.py` — Python 行为级自校验器（仅用标准库），镜像 RTL 逻辑。必须定义以下两个
   **签名固定**的行为函数（判分器会按此签名 import 调用）：
   - `clamp_iso(iso_en, din, clamp_val, active, width)`：隔离生效（active=1 时 iso_en=1，或
     active=0 时 iso_en=0）→ 返回 width 位全 clamp_val（clamp_val=1 返回 (1<<width)-1，=0 返回 0）；
     否则 → 透明返回 din。
   - `keep_iso(iso_en, din, cur, active)`：隔离生效 → 返回 cur（保持）；否则 → 返回 din（跟随）。
   - 直接 `python3 verify_model.py`（不带参数）运行时，对**可见配置 A**（width=8, clamp_val=0,
     init_val=1, active=1，CLAMP 与 KEEP 两种模式都覆盖）跑一组自检，全过则在 stdout 打印
     `ALL TESTS PASSED` 且退出码 0；任一失败打印 `FAIL:` 行并退出码非 0。自检用例至少覆盖：
     透明直通、隔离钳位（clamp_val=0/1）、隔离保持、双极性（高有效/低有效）、复位默认值 INIT_VAL。

可见样本 A（随附件 `spec_A.md` 提供）展示了完整规格与 A 的具体配置
（WIDTH=8, ISO_TYPE="CLAMP", CLAMP_VAL=1'b0, INIT_VAL=1'b1, ISO_EN_ACTIVE=1'b1 高有效），
可据此离线开发与自测。判分将在一份**位宽/钳位值/极性/模式均不同且对你不可见**的隐藏配置 B
上检验你交付的 `verify_model.py` 的行为函数是否仍然正确——所以实现必须真正参数化，不能把 A
的取值（clamp_val=0、active=1、width=8 等）硬编码进行为函数。

约束
- `verify_model.py` 仅用 Python 标准库，无第三方依赖。
- `power_iso.v` 必须三个模块齐全、generate 切换正确、极性 wire 在两个子模块都存在。
- 最终交付：把 `power_iso.v` 和 `verify_model.py` 打包进 `outputs/submit.zip`。"""

attachments = [
    {
        "name": "spec_A.md",
        "source": "benchmarks/EDA-Eval-DesignFlow/assets/%s/spec_A.md" % CASE,
        "desc": "可见样本A的完整规格书：power isolation cell 行为级 RTL 模型三模块结构、参数、极性处理、generate 切换，以及 verify_model.py 的函数签名与自检要求；含 A 的具体配置(WIDTH=8/CLAMP/CLAMP_VAL=0/INIT_VAL=1/高有效)。SUT 用以理解需求并离线开发/自测。"
    }
]

with open(os.path.join(REF_DIR, "check.py"), encoding='utf-8') as f:
    test_src = f.read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "test": test_src,
    "expected_artifacts": ["power_iso.v", "verify_model.py", "submit.zip"],
    "budget": {"max_turns": 30, "timeout_sec": 2400},
    "metadata": {
        "domain": "digital",
        "level": "L1-B",
        "difficulty": "medium",
        "track": "design_flow",
        "task_name": "power isolation cell behavioral RTL model (clamp/keep semantics + configurable enable polarity) with python behavioral self-check",
        "scenario": "B档合成 (deliverable=写私有 /home/e0045144/jtag/ACC/run/power_iso.v+verify_model.py → .75 Permission denied → INFEASIBLE → 自包含参数化重构)",
        "trace_source": {
            "user": "e0045144",
            "host": "hfeg0pkn005",
            "ip": "10.129.2.14",
            "session_file": "1794394698715_yx1e1.messages.json",
            "match_count": 39,
            "scan": "ssh_eda_search_20261113_131349",
            "real_task_summary": "U#0(RTL 语法检查 Q&A): xorTstCHaIn 例化带 `ifndef FPGA 条件编译端口, 问语法是否有问题(agent 答: 前置逗号风格合法)。U#1(核心 produce-task, 本 case 选用): 「帮我写一个 power iso 的 design」+ask_question 澄清为「隔离单元(ISO cell)的行为级 RTL 模型, 含 enable 保持/取值逻辑」→agent 产 power_iso.v 三模块(power_iso_clamp 钳位 assign dout=iso_act?{WIDTH{CLAMP_VAL}}:din / power_iso_keep 时序 always 复位{WIDTH{INIT_VAL}}+保持+跟随 / power_iso 顶层 generate 按 ISO_TYPE 切换) + tb_power_iso.v + verify_model.py(Python 行为自检 11 check, 镜像 RTL {WIDTH{CLAMP_VAL}} 复制修 bug 后全 PASS); 参数 WIDTH/CLAMP_VAL/INIT_VAL/ISO_EN_ACTIVE(极性)/ISO_TYPE。U#2(后续 Q&A): 查 .lib 内有无 iso cell(scan_lib_iso.py)。deliverable=写私有 /home/e0045144/jtag/ACC/run/ → .75 Permission denied → INFEASIBLE → B档合成。"
        },
        "test_rationale": "16 条断言：① submit.zip 解压后含 power_iso.v 与 verify_model.py 两个文件 ② verify_model.py 仅用 Python 标准库无外部 import ③ power_iso.v 定义 module power_iso_clamp(钳位型) ④ power_iso.v 定义 module power_iso_keep(保持型) ⑤ power_iso.v 定义 module power_iso 顶层且含 ISO_TYPE 参数 ⑥ power_iso_clamp 含参数 WIDTH/CLAMP_VAL/ISO_EN_ACTIVE 且 assign dout = iso_act ? {WIDTH{CLAMP_VAL}} : din ⑦ power_iso_keep 含参数 WIDTH/INIT_VAL/ISO_EN_ACTIVE 且 always 块复位到 {WIDTH{INIT_VAL}} + 隔离保持 + 否则跟随 din ⑧ 两个子模块均含极性 wire iso_act = (ISO_EN_ACTIVE==1'b1) ? iso_en : ~iso_en ⑨ 顶层 power_iso 用 generate 块按 ISO_TYPE==\"KEEP\" 切换例化 keep / 否则 clamp ⑩ verify_model.py 定义 clamp_iso(iso_en,din,clamp_val,active,width) 且 B 配置(width=16,clamp_val=1,active=0)行为正确(en=0→65535, en=1→din) ⑪ verify_model.py 定义 keep_iso(iso_en,din,cur,active) 且 B 配置(active=0)行为正确(en=1→din, en=0→cur) ⑫ subprocess 跑 verify_model.py 退出码 0 且 stdout 含 'ALL TESTS PASSED' ⑬ 跨输入守卫: clamp_iso 在 B(width=16,clamp_val=1,active=0)下 en=0 返回 65535 与 A(width=8,clamp_val=0,active=1)行为不同(击败 hardcoded_A) ⑭ 3-seed 随机化: clamp_iso/keep_iso 与 check.py 独立 oracle 在随机输入上一致(3 seed 全过) ⑮ power_iso.v 结构平衡: module/endmodule 配对 + generate/endgenerate 配对 + begin/end 配对 ⑯ 双极性守卫: clamp_iso active=1 时 en=1 隔离/en=0 透明, active=0 时 en=0 隔离/en=1 透明(两种极性都正确)"
    }
}

# append
out = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
n = 0
with open(out, encoding='utf-8') as f:
    for line in f:
        if line.strip():
            n += 1
print("A.jsonl before:", n, "cases")

# idempotency: skip if CASE already present
exists = False
with open(out, encoding='utf-8') as f:
    for line in f:
        if CASE in line:
            exists = True; break
if exists:
    print("CASE already in A.jsonl, NOT appending."); sys.exit(0)

with open(out, 'a', encoding='utf-8') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

n2 = 0
with open(out, encoding='utf-8') as f:
    for line in f:
        if line.strip():
            n2 += 1
print("A.jsonl after:", n2, "cases")
print("appended:", CASE)

# verify k_rationale == k_check
import re
k_check = test_src.count('("', )  # crude
# better: count CONDITIONS entries
k_check_real = len(re.findall(r'^\s*\("[a-z]",', test_src, re.M))
k_rat = entry["metadata"]["test_rationale"].count("①") + entry["metadata"]["test_rationale"].count("⑩") - 1  # placeholder
# count unicode circled numbers properly
import unicodedata
circ = [c for c in entry["metadata"]["test_rationale"] if 0x2460 <= ord(c) <= 0x2473]
print("k_check (CONDITIONS) =", k_check_real, " k_rationale (circled) =", len(circ))
assert k_check_real == len(circ) >= 8, "ASSERTION GATE FAILED"
print("ASSERTION GATE: k_rationale == k_check =", k_check_real, ">= 8  OK")
