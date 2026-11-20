#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-CstViewPrecheck-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json, os, sys

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-CstViewPrecheck-001"
REF = os.path.join(REPO, "reference", CID)

check_py = os.path.join(REF, "check.py")
test_src = open(check_py).read()

PROMPT = open(os.path.join(REPO, "assets", CID, "prompt.txt")).read()

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": [
        "assets/%s/prompt.txt" % CID,
        "assets/%s/task_brief.md" % CID,
        "assets/%s/spec_A.json" % CID,
        "assets/%s/pyAether_sample.py" % CID,
    ],
    "test": test_src,
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 20},
    "metadata": {
        "trace_source": {
            "user": "ziyuny",
            "host": "10.129.32.190",
            "session_file": "1789961467130_nibwl.messages.json",
            "match_count": 154,
            "real_task_summary": "Aether Group Generator skill 维护：用户 ziyuny 想在重跑 group generate 前预清理残留的 cstconfig view——先 ae.dbCVExist 检查 view 是否存在，存在则 ae.dbDelCV 删除（U#0 提需求、U#16 要求加到脚本 120/121 行之间、U#51 明确指定用 dbCVExist+dbDelCV 而非 emyDMIsCellViewExist/emyScalarName 那套）。助手先用 emyDMIsCellViewExist+emyCdbaNS+emyScalarName 实现，遇 TypeError 后改用 dbCVExist+dbDelCV（直接传字符串），插入 '3.1 预清理' 块到 group_generate.py，同步到 v1.1 两份副本，py_compile 校验，并在 train/ddgoa_test 项目 zyTest/VwlpRefAmpIP 上实跑（dbCVExist->True->dbDelCV->True 成功；下次 dbCVExist->False 跳过）。本 case 取同 trace 不同意图=预清理工具本身（与已交付 AnalogGroupCfgMergeDummy-001 的 config patch 意图不重叠）。"
        },
        "domain": "analog_context",
        "grade": "B",
        "track": "synthesized",
        "L_level": "L1",
        "test_rationale": (
            "16 条断言："
            "①submit.zip 可解压且无泄漏(不含 check.py/reference/jsonl/negative)且含 cstconfig_precheck.py 且 py_compile 通过 "
            "②A(可见输入,zyTest/VwlpRefAmpIP/cstconfig,mock dbCVExist=True/dbDelCV=True)运行 exit0 且产出 report.json "
            "③report.json 含全部 8 键(lib/cell/view/existed/deleted/delete_ret/status/timestamp) "
            "④A 的 dbCVExist 被调用恰好 1 次且参数 lib=zyTest/cell=VwlpRefAmpIP/view=cstconfig(从 mock 调用日志验) "
            "⑤A 的 existed==True(mock 返回 True) "
            "⑥A 的 dbDelCV 被调用恰好 1 次且参数与 dbCVExist 一致 "
            "⑦A 的 deleted==True 且 delete_ret==True "
            "⑧A 的 status==\"deleted\"(存在+删除成功) "
            "⑨B(隐藏输入,analogLib/BandgapTop/cstconfig,mock dbCVExist=False)运行 dbCVExist 被调用但 dbDelCV 不被调用(view 不存在则跳过删除) "
            "⑩B 的 existed==False 且 deleted==False 且 status==\"skipped\" "
            "⑪B2(隐藏输入,phyLib/DDR5Clk/cstcfg_v2,mock dbCVExist=True/dbDelCV=False)的 dbDelCV 被调用且返回 False(删除失败) "
            "⑫B2 退出码非 0 且 status==\"delete_failed\"(删除失败必须报错退出) "
            "⑬跨输入守卫:B 的 report.lib/cell/view==B 规格(analogLib/BandgapTop/cstconfig)而非 A 的 zyTest/VwlpRefAmpIP "
            "⑭反硬编码:候选源码不含 A 专属字面量 zyTest 或 VwlpRefAmpIP(从 --lib/--cell 读而非写死) "
            "⑮确定性:A 的 mock 调用日志跑 3 次 sha256 完全一致(行为可重复) "
            "⑯B2 的 report.view==\"cstcfg_v2\"(view 从 --view 读而非硬编码 \"cstconfig\")"
        ),
    },
}

jsonl_path = os.path.join(REPO, "EDA-Eval-DesignFlow_D.jsonl")
existing = open(jsonl_path).read().splitlines()
for line in existing:
    if line.strip():
        d = json.loads(line)
        if d.get("task_id") == CID:
            print("!!! CID already in jsonl — aborting"); sys.exit(1)

with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

n = sum(1 for l in open(jsonl_path) if l.strip())
print("appended %s to %s (now %d lines)" % (CID, jsonl_path, n))

# roundtrip: last line parses + test field == disk check.py
last = [l for l in open(jsonl_path) if l.strip()][-1]
d = json.loads(last)
assert d["task_id"] == CID
assert d["test"] == test_src, "test field bytes != disk check.py"
print("roundtrip OK: test field (%d bytes) == disk check.py (%d bytes)" % (len(d["test"]), len(test_src)))

# assertion gate: count ①…⑯ in test_rationale == 16 == k_check
import re
rationale = d["metadata"]["test_rationale"]
circled = re.findall(r"[\u2460-\u2473]", rationale)  # ①..⑳
k_rationale = len(circled)
# count _cond("a.".."p.") labels in check.py
labels = re.findall(r'_cond\("([a-p])\.', test_src)
k_check = len(set(labels))
print("GATE: k_rationale=%d k_check=%d" % (k_rationale, k_check))
assert k_rationale == 16 and k_check == 16 and k_rationale == k_check and k_check >= 8, "ASSERTION GATE FAIL"
print("ASSERTION GATE PASS: k_rationale=k_check=16 >= 8")
