#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-StackedMOSOpAnalysis-001 to B jsonl (r619 scratch)."""
import json, os

CASE = "EDA-Eval-DesignFlow-StackedMOSOpAnalysis-001"
BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
RD = os.path.join(BASE, "reference", CASE)

with open(os.path.join(RD, "check.py")) as f:
    check_src = f.read()

with open(os.path.join(os.path.dirname(__file__), "_stkop_prompt.txt")) as f:
    prompt = f.read()
with open(os.path.join(os.path.dirname(__file__), "_stkop_rationale.txt")) as f:
    test_rationale = f.read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "test": check_src,
    "attachments": [f"assets/{CASE}/op_data_A.json"],
    "expected_artifacts": None,
    "metadata": {
        "trace_source": {
            "user": "e0029308",
            "host": "hfeg0pkn002",
            "session_file": "1793089704959_am99r",
            "match_count": 339,
            "real_task_summary": "e0029308 在 hfeg0pkn002 上跑五管 OTA 静态工作点仿真(FineSim dcOpInfo, /proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/STD_PLDX_LVL_SIM/OP_DC_SIM)，输入对管用两只 MOS 串联(stack)等效长沟道。e0029308 连问三问：串联管子等效长 L 管时静态工作点怎么分析、能否只看某一根；接近 D 端 Vds 更大是否该分析靠近 D 端那根；五管 OTA 输入对管该看哪一侧(并纠正助手首答方向说反)。助手订正为：只有靠近漏端(D 端)那根进入饱和(pinch-off)、靠源端(S 端)管落在三极管区是正常预期非设计错、整串饱和看 D 端管 region==sat 且 Vds>=Vov、串内 KCL 电流相等。本 case 把「拿到 dcOpInfo 工作点数据判断堆叠管整串工作状态、定位该看哪根管」的概念 Q&A 泛化成「写可复用分析脚本 op_analyze.py」，拓扑推断 D 端管、判 properly_saturated/not_saturated/anomaly、报异常。"
        },
        "domain": "spice_sim",
        "shard": "B",
        "track": "synthesized",
        "level": "L1",
        "k_rationale": 11,
        "k_check": 11,
        "test_rationale": test_rationale,
        "asset_fidelity": "synth_data"
    }
}

jsonl_path = os.path.join(BASE, "EDA-Eval-DesignFlow_B.jsonl")
with open(jsonl_path) as f:
    lines = f.read().splitlines()
assert not any(json.loads(l).get("task_id") == CASE for l in lines if l.strip()), "case already in jsonl"
with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended; new line count:", len(lines) + 1)
print("k_check=", entry["metadata"]["k_check"], "k_rationale=", entry["metadata"]["k_rationale"])
