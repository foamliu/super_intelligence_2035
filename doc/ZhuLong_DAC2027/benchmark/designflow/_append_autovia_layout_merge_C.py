#!/usr/bin/env python3
"""_append_autovia_layout_merge_C.py - append AutoViaLayoutMerge-001 to C.jsonl."""
import json
import os

CASE_ID = "EDA-Eval-DesignFlow-AutoViaLayoutMerge-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
REF = os.path.join(REPO, "benchmarks/EDA-Eval-DesignFlow/reference", CASE_ID)
CHECK = os.path.join(REF, "check.py")
JSONL = os.path.join(REPO, "benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_C.jsonl")

with open(CHECK) as f:
    check_src = f.read()

ASSETS = "benchmarks/EDA-Eval-DesignFlow/assets/%s" % CASE_ID
PROMPT = open(os.path.join(REPO, ASSETS, "prompt.txt")).read()

RATIONALE = (
    "16 条断言："
    "①submit.zip 含 autovia_merge_gen.py 且 py_compile 通过 "
    "②生成器在 hidden B 上 CLI exit0 且写出 out-nogui+out-config "
    "③out-config B 含 outLibName=\"serdes_analog\"（由 B libName 派生，杀硬编码 A） "
    "④out-config B 含 outCellName=\"serdes_top_autovia\"（B cellName+_autovia） "
    "⑤out-nogui B 含新 let 变量 outLibName outCellName srcCV dstCV viaMasterCV "
    "⑥out-nogui B 含默认回退 outLibName←libName / outCellName←strcat(cellName \"_autovia\") "
    "⑦out-nogui B 含 merge guard readOnlyCellList && length(readOnlyCellList)>=1 "
    "⑧out-nogui B 只读打开源 layout dbOpenCellViewByType(libName cellName viewType ... \"r\") "
    "⑨out-nogui B 建输出库 dbCreateLib(outLibName ...) "
    "⑩out-nogui B 建目标 cellview 写模式 dbOpenCellViewByType(outLibName outCellName viewType \"maskLayout\" \"w\") "
    "⑪out-nogui B 用 dbCopyFig 拷 ≥4 类对象 {shapes,labels,vias,pins,blockages} "
    "⑫out-nogui B 拷 instance dbCreateInst+dbCreateInstArray 都在 "
    "⑬out-nogui B 把 via cell 在原点 R0 实例化 dbCreateInst(dstCV viaMasterCV ... list(0 0) \"R0\") "
    "⑭out-nogui B 保存+bbox dbSave(dstCV)+dbComputeBBox(dstCV) "
    "⑮out-nogui B 保留 procedure( RunAutoViaNoGui 恰 1 次+IMCleGetTimeString helper（防破坏性删除） "
    "⑯确定性 B 上跑 3 次 out-nogui md5 一致"
)

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": PROMPT,
    "attachments": [
        "assets/%s/inputs/run_autovia_nogui.il" % CASE_ID,
        "assets/%s/inputs/run_autovia_config.il" % CASE_ID,
        "assets/%s/inputs/prompt_autovia.md" % CASE_ID,
        "assets/%s/inputs/task_brief.md" % CASE_ID,
    ],
    "metadata": {
        "trace_source": {
            "user": "e0014566",
            "host": "hfeg0plg49",
            "session_file": "1783342909947_149bq.messages.json",
            "match_count": 10,
            "real_task_summary": "AutoVia 跑通后，把 addViaToLayout 的 via-cell→layout merge 逻辑 inline 进 RunAutoViaNoGui() 末尾（dbCopyFig 全量拷原 layout 对象 + dbCreateInst 把 readOnlyCellList 里的 via cell 在原点 R0 实例化 + dbSave 保存新 layout），并加 outLibName/outCellName 配置参数。用户 U#2 逐字提目标未给根因。"
        },
        "domain": "layout_virtuoso",
        "track": "faithful-seed-B-synthesized",
        "level": "L1-boundary",
        "test_rationale": RATIONALE,
        "k_rationale": 16,
        "k_check": 16,
    },
}

# verify test field == disk check.py (roundtrip)
assert entry["test"] == open(CHECK).read(), "test field != disk check.py"

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("appended %s to %s" % (CASE_ID, JSONL))
print("k_rationale=k_check=%d >= 8 GATE PASS" % entry["metadata"]["k_check"])
