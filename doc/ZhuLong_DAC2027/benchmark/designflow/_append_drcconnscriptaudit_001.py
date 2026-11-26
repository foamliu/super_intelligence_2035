#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-DrcConnScriptAudit-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os, hashlib

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-DrcConnScriptAudit-001"
A = os.path.join(ROOT, "assets", CASE)
R = os.path.join(ROOT, "reference", CASE)
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_C.jsonl")

prompt = open(os.path.join(A, "prompt.md")).read().rstrip() + "\n"
check_py = open(os.path.join(R, "check.py")).read()

attachments = [
    "assets/%s/run.py" % CASE,
    "assets/%s/sameNet.rdb" % CASE,
    "assets/%s/diffNet.rdb" % CASE,
    "assets/%s/run_logic_notes.md" % CASE,
    "assets/%s/svrf_dfm_property.md" % CASE,
    "assets/%s/task_brief.md" % CASE,
]

test_rationale = (
    "14 条断言："
    "①(a) submit.zip 含 drc_conn_audit.py 且 py_compile 通过 "
    "②(b) --help/-h exit 0 打印 usage、无参 exit 非零 "
    "③(c) B1(同 3 缺陷,异名/异 netidnum) exit 0 且写出 report.json "
    "④(d) B1 report.json 含顶层键 mechanism/issues/plan/verdict/rdb_summary "
    "⑤(e) B1 mechanism 覆盖 dfm_property_opc011/netid_function/by_net/netidnum "
    "⑥(f) B1 issues 含三个 id(tcp_paths_missing/via_shield_unhandled/sconnect_not_configured)且 evidence 非空 "
    "⑦(g) B1 verdict==FAIL 且 issues>=3 "
    "⑧(h) B1 plan>=3 条 "
    "⑨(i) B2(clean: TCP/via-shield/SCONNECT 均已修) exit 0 且 0 个已知缺陷且 verdict==OK "
    "⑩(j) 跨输入守卫 B1 report 无 A 专属 token(find_all_paths/CONNECT_CFG/group_by_netid/load_rdb/101/102/107) "
    "⑪(k) B3(malformed run.py) exit 非零+stderr 非空+不写 report.json "
    "⑫(l) 确定性 B1 两跑 stdout 一致且 report.json md5 一致 "
    "⑬(m) 反 naive B1 issue evidence 必须引用 B1 实际代码名(tcp->trace_paths/via->check_via_chain/sconnect->LAYER_MAP) "
    "⑭(n) B1 rdb_summary 含 B1 实际 netidnum(sameNet 2001/diffNet 2002 与 2077,非 A 的 101/102/107)"
)

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "test": check_py,
    "metadata": {
        "domain": "physical_verify",
        "layer": "L1-boundary",
        "track": "faithful-seed-B-synthesized",
        "trace_source": {
            "user": "xxchen",
            "host": "hfeg0pkn005",
            "session_file": "1792985372628_41ki8.messages.json",
            "match_count": 146,
            "real_task_summary": (
                "xxchen 的 cline 会话(361 msgs/cwd /home/xxchen/connectivity 项目,"
                "tool_use 381 calibre + 2 pyAether)。U#0 要求解释 DFM PROPERTY OPC011 "
                "统计 netid 的机制(从 svrf_ur 文档追溯 property_definition/BY NET/NETID()/"
                "RDB netidnum 字段); U#1 把小 case 中间结果 sameNet.rdb/diffNet.rdb 整理进 "
                "markdown+html 说明文档; U#2(主交付)把 drc connection 脚本 run.py 的 3 个 "
                "缺陷(TCP 路径 find_all_paths 抓不到 / metal 上下层屏蔽 via 不支持 QA / "
                "SCONNECT 不在配置内)写成 markdown+html 并列改进 plan; 助手多轮 editor/"
                "run_approved_command 生成 run_issues.md+html(反复修 HTML 标签/重复), 用户接受。"
                "本 case 取正交子主题: 给含 3 已知缺陷的 DRC connectivity 脚本写 drc_conn_audit.py "
                "做审计+机制解析->JSON 报告(mechanism/issues/plan/verdict/rdb_summary)。"),
        },
        "test_rationale": test_rationale,
    },
}

# verify test==disk md5
disk_md5 = hashlib.md5(check_py.encode()).hexdigest()
entry_md5 = hashlib.md5(entry["test"].encode()).hexdigest()
assert disk_md5 == entry_md5, "test field != disk check.py (%s vs %s)" % (entry_md5, disk_md5)
# verify rationale prefix + k count
import re
assert test_rationale.startswith("14 条断言："), "rationale prefix"
marks = re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]", test_rationale)
assert len(marks) == 14, "expected 14 circled marks, got %d" % len(marks)
print("test==disk md5 OK:", disk_md5)
print("k_rationale=14, k_check=14, GATE PASS")

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", JSONL)

# verify line count + last id
with open(JSONL) as f:
    lines = f.readlines()
print("jsonl total lines:", len(lines))
last = json.loads(lines[-1])
print("last id:", last["id"], "domain:", last["metadata"]["domain"])
ids = {json.loads(l).get("id") for l in lines}
print("unique ids:", len(ids), "dups:", len(lines) - len(ids))
