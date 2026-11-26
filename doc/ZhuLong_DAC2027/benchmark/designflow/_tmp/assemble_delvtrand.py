#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble DelvtrandAnomalyScan-001 case entry and append to
EDA-Eval-DesignFlow_D.jsonl. Idempotent: skips if task_id already present."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")
REF = os.path.join(BENCH, "reference", "DelvtrandAnomalyScan-001")
CHK = os.path.join(REF, "check.py")

TASK_ID = "EDA-Eval-DesignFlow-DelvtrandAnomalyScan-001"

# ---- idempotency guard ----
existing = [json.loads(l) for l in open(JSONL, encoding="utf-8") if l.strip()]
if any((e.get("task_id") or e.get("id")) == TASK_ID for e in existing):
    print("SKIP: %s already in D.jsonl (%d lines)" % (TASK_ID, len(existing)))
    sys.exit(0)

# ---- read check.py source as the test field ----
check_src = open(CHK, encoding="utf-8").read()

PROMPT = r"""我手头有一份 SPICE 网表（`.cdl` 格式），里面是若干 subckt 定义，每个 subckt 内有一堆晶体管行。晶体管行长这样：

```
XNM0 O I VSS nsvt_dbc w=119e-9 l=6e-9 delvtrand=delvtrand_nsvt dtemp=dtemp_nsvt
XPM4 OUT ENE VDD psvt_dbc w=119e-9 l=54e-9 delvtrand=100e-3 dtemp=0
XM2 OUT N2 VDD psvt_dbc w=300e-9 l=6e-9 delvtrand=100e-3 dtemp=0
```

解析规则：
- 以 `X` 开头的行是晶体管实例行：`X<inst> <n1> <n2> <n3> <model>_dbc w=.. l=.. delvtrand=<v> dtemp=..`。`<inst>` 是实例名（去掉行首的 `X`），`<model>_dbc` 是模型名（取 `_dbc` 前的部分），`delvtrand=<v>` 是该管子的 delvtrand 参数值。
- `.subckt <name> ...` 行声明当前所在的 subckt 名，对它之后、`.ends` 之前的所有晶体管行生效（行号是文件里 1-based 的行号）。

我要找的是 **delvtrand 参数被写死成常数** 的管子。正常的管子应该用工艺变量名：
- `delvtrand=delvtrand_nsvt`（nsvt 管）
- `delvtrand=delvtrand_psvt`（psvt 管）
- `delvtrand=delvtrand_pulvt`（pulvt 管）
- `delvtrand=delvtrand_nulvt`（nulvt 管）

只要 `delvtrand=<v>` 的 `<v>` 不是上面四个工艺变量名之一，就判为异常（anomaly）。常见的写死值有 `0`、`100e-3`、`50e-3` 等——这些都是异常。

对每个异常管子，我要知道：
- `instance`：实例名（行首 `X` 后面的部分，如 `NM1`、`PM4`、`M2`）
- `subcircuit`：它所在的 subckt 名
- `line`：它在文件中的 1-based 行号
- `model`：模型名（含 `_dbc` 后缀，如 `nsvt_dbc`、`psvt_dbc`）
- `delvtrand`：写死的 delvtrand 值原样字符串（如 `0`、`100e-3`）

另外还要统计 **delvtrand 分布**：对所有管子按 delvtrand 值计数。四个工艺变量名各占一档；所有非工艺变量的值合并成一档叫 `hardcoded`（即写死值的总数）。

输出一个 JSON 报告，结构固定如下（键按字典序，便于确定性比对）：

```json
{
  "anomalies": [
    {"instance": "<实例名>", "subcircuit": "<subckt 名>", "line": <行号>,
     "model": "<模型>_dbc", "delvtrand": "<写死值>"},
    ...
  ],
  "anomaly_count": <异常管子数>,
  "delvtrand_distribution": {
    "delvtrand_nsvt": <数>, "delvtrand_nsvt": <数>,
    "delvtrand_pulvt": <数>, "delvtrand_nulvt": <数>,
    "hardcoded": <写死值总数>
  },
  "netlist_file": "<输入文件 basename>",
  "total_transistors": <全部管子数>
}
```

`anomalies` 数组按行号升序排。`delvtrand_distribution` 里只出现实际存在的工艺变量档 + `hardcoded` 档（不存在的工艺变量档不要写进去）。

我给你一份样例网表 `inputs_A/netlist_A.cdl`（含 4 个 subckt：`INV_1X_A`/`NAND_2X_A`/`TS_comp_A`/`TS_analog_A`，共 20 个管子，其中 3 个 delvtrand 写死），以及对应的正确输出 `example_output/report_A.json`，供你对照解析逻辑。

帮我写个 `analyze_delvtrand.py`，CLI 是：
```
python3 analyze_delvtrand.py <netlist.cdl> --out <report.json>
```
`--out` 默认 `report.json`。只准用 Python 标准库；**不准** import `numpy`/`scipy`/`pandas`/`subprocess`/`socket`/`urllib`/`requests`/`http.client`/`calibre`/`pyaether`，不准用 `eval`/`exec`/`os.system`，也不准硬编码去读 reference/hidden 目录或任何只属于隐藏测试输入的字面量（例如隐藏网表里才会出现的 `*_B` 后缀 subckt 名、`netlist_B` 文件名等）。最后把 `analyze_delvtrand.py` 打包成 `outputs/submit.zip` 给我。

我之后会用一份**结构相同但 subckt/实例名不同**的隐藏网表来测你的脚本，所以请确保你的解析逻辑是通用的，不要针对样例 A 的具体名字写死。"""

TEST_RATIONALE = (
    "12 条断言："
    "①submit.zip 含 analyze_delvtrand.py 且无禁止 import"
    "(numpy/scipy/pandas/subprocess/socket/urllib/requests/calibre/pyaether 等)"
    "/eval/exec/os.system 调用、无 reference/hidden/inputs_B/netlist_B/"
    "DelvtrandAnomaly 路径或字面量泄漏、无 INV_2X_B/NAND_3X_B/TS_comp_B/"
    "TS_analog_B/net60/net14/NETX/NETY/net9 等 B 专属字面量 "
    "②py_compile 通过 "
    "③隐藏 B 运行退出 0 且产出合法 JSON 且 total_transistors==独立 oracle"
    "(regex-finditer 重解析，按位置回溯当前 .subckt 上下文) 的管子总数(23) "
    "④anomaly_count==oracle(6) "
    "⑤异常实例名集合==oracle{NM1,PM2,PM4,PM5,M4,M5} "
    "⑥异常 subckt 名集合==oracle{NAND_3X_B,TS_comp_B,TS_analog_B} "
    "⑦每条异常的(instance,subcircuit,delvtrand)三元组集合==oracle(6 条全匹配) "
    "⑧每条异常的(instance,line)映射==oracle(行号精确匹配) "
    "⑨每条异常的(instance,model)映射==oracle(模型名含_dbc后缀精确匹配) "
    "⑩delvtrand_distribution 字典==oracle(按 delvtrand 值计数，"
    "非工艺变量合并入 hardcoded 档) "
    "⑪反硬编码跨输入 A:SUT 跑 A 产合法 JSON、A/B 的 .subckt 名集合不相交、"
    "A total_transistors==20、B 输出与源码均无 A 专属字面量"
    "(INV_1X_A/NAND_2X_A/TS_comp_A/TS_analog_A/net58/net12/net7) "
    "⑫3-seed sha256(B 报告字节级)稳定；"
    "另 §4.9 三假提交回归(非 zip/空 zip/错名 zip)均被 check 早返回 REJECTED"
)

case = {
    "task_id": TASK_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": [
        {
            "name": "inputs_A/netlist_A.cdl",
            "source": "inputs_A/netlist_A.cdl",
            "desc": "样例 A 的 SPICE 网表（synth_lib，4 个 subckt：INV_1X_A/NAND_2X_A/"
                    "TS_comp_A/TS_analog_A，共 20 个晶体管，其中 3 个 delvtrand 写死，"
                    "供你对照解析与异常判定逻辑）",
        },
        {
            "name": "example_output/report_A.json",
            "source": "example_output/report_A.json",
            "desc": "样例 A 在正确实现下的期望 JSON 报告（total_transistors=20，"
                    "anomaly_count=3，delvtrand_distribution 含 4 个工艺变量档 + "
                    "hardcoded=3）",
        },
    ],
    "test": check_src,
    "budget": {"max_turns": 24},
    "expected_artifacts": ["outputs/submit.zip"],
    "metadata": {
        "domain": "schematic_netlist",
        "trace_source": {
            "user": "zhililu",
            "host": "10.129.32.93",
            "session_file": "1793841644587_o9nm6.messages.json",
            "match_count": 28,
            "real_task_summary": (
                "analyze_delvtrand.py: scan SPICE netlist TS_core for transistors "
                "whose delvtrand= parameter is a hardcoded constant (0/100e-3/50e-3) "
                "rather than a process-variable token (delvtrand_nsvt/psvt/pulvt/"
                "nulvt); per-anomaly table (instance/subcircuit/line/model/"
                "delvtrand) + delvtrand distribution; 3-turn evolution (initial "
                "scan / re-check after fix / Spectre SFE-23 error diagnosis)"),
        },
        "test_rationale": TEST_RATIONALE,
        "layer": "L2",
        "difficulty": "B",
        "design": "schematic_netlist",
        "direction": "synthesized",
        "heavy": "spice_netlist_parse+delvtrand_anomaly_scan",
        "scenario": "SPICE .cdl 网表 delvtrand 参数异常扫描（工艺变量 vs 写死常数）",
        "task_name": "DelvtrandAnomalyScan",
        "topic": "SPICE .subckt/X-instance transistor-line parse + delvtrand "
                 "process-variable vs hardcoded-constant anomaly detection + "
                 "per-anomaly (instance,subcircuit,line,model,delvtrand) table + "
                 "delvtrand distribution histogram",
        "tcr_refs": [],
        "wall_time_sec": 2400,
    },
}

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")

# verify
after = [json.loads(l) for l in open(JSONL, encoding="utf-8") if l.strip()]
print("appended %s -> D.jsonl now %d lines" % (TASK_ID, len(after)))
assert after[-1]["task_id"] == TASK_ID
assert after[-1]["metadata"]["test_rationale"].count("①") >= 1
# count assertions (①..⑫)
import re
n_assert = len(re.findall(r"[①-⑿⓪]", after[-1]["metadata"]["test_rationale"]))
print("test_rationale assertion count:", n_assert)
assert n_assert >= 8, "k_rationale must be >= 8"
print("OK")
