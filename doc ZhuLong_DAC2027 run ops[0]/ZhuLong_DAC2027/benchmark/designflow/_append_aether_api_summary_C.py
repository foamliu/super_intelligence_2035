#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-AetherApiSummary-001 to shard C jsonl."""
import os, json

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "AetherApiSummary-001"
JSONL = os.path.join(REPO, "EDA-Eval-DesignFlow_C.jsonl")

# visible A attachments
atts = []
for root, dirs, files in os.walk(os.path.join(REPO, "assets", CASE, "inputs")):
    for f in sorted(files):
        full = os.path.join(root, f)
        rel = os.path.relpath(full, REPO)
        atts.append(rel)
atts = sorted(atts)

# read check.py source for test field
check_src = open(os.path.join(REPO, "reference", CASE, "check.py"), encoding="utf-8").read()

prompt = open(os.path.join(REPO, "assets", CASE, "inputs", "prompt_aether_api_summary.md"), encoding="utf-8").read()

test_rationale = (
    "16 条断言："
    "①submit.zip含aether_api_summary.py(>=800B,UTF-8无NUL,纯标准库无第三方import,py_compile通过) "
    "②候选CLI在隐藏B上exit0并写出非空report.md+合法summary.json "
    "③summary.json顶层6键(categories/db_patterns/object_attributes/design_patterns/best_practices/total_files)齐全 "
    "④summary.total_files==对B fixture独立重推的.py文件数 "
    "⑤summary.categories子目录集合==B fixture独立重推的子目录集合(覆盖全部B且不含A独有子目录,杀硬编码A) "
    "⑥每类别file_count==对该子目录独立重推的.py数 "
    "⑦每类别top_apis名均在B该子目录独立重推的API集合内且排第1的API==独立重推的最频API(数据派生非子串) "
    "⑧db_patterns.dbOpenCV_count==对B fixture独立重推的dbOpenCV出现次数(数值) "
    "⑨db_patterns.dbGet_count==对B独立重推的dbGet*出现次数(数值) "
    "⑩object_attributes每个类的属性集合==对B fixture @attrs注解独立重推的属性集合(且类集合相等) "
    "⑪design_patterns.try_except_count==对B独立重推的try:块数(数值) "
    "⑫design_patterns.config_class_used==对B独立重推的布尔(Config(或class Config出现与否) "
    "⑬design_patterns.lisp_helpers_used==对B独立重推的布尔(car/cadr/mapcar等出现与否) "
    "⑭best_practices含dbCloseCV资源释放条目当且仅当B有dbOpenCV(数据派生) "
    "⑮确定性:对B连续3次运行summary.json的md5完全一致 "
    "⑯交叉纯净:report.md与summary.json均引用B独有子目录(mentor)与B独有API(calibreDrc/calibreLvs,不出现在A fixture),杀硬编码A与naive全量dump"
)

trace_source = {
    "user": "taodu",
    "host": "hfeg0plg55",
    "session_file": "1791862539977_nwwkg.messages.json",
    "match_count": 271,
    "real_task_summary": (
        "taodu/hfeg0plg55(10.129.35.74), mc=271, keywords schematic:288/dbGet:260/pyAether:163/"
        "netlist:35/hspice:20/cellview:16/calibre:13/virtuoso:4, tools list_allowed_files:18/"
        "read_files:23/editor:38/run_commands:4/SandBox_MCP_Server__run_code:4/RAG_MCP_Server__search_apis:4, "
        "177 msgs/1.22MB, model deepseek-v4-flash, cwd /home/taodu/sos/settings_cdns. "
        "USER#1 逐字(A-档 seed 提出目标未给根因)「分析下面到目录，总结出aether常用到API和常用到DB处理方式，"
        "输出一个PDF文件 /apps/imctf/cad/init/settings_aether/python_ae」; 单轮闭环(其余97条user均为tool_result). "
        "agent: list_allowed_files探python_ae 16子目录(le/db/hi/se/layout/tc/ut/veri/wave/genabs/image/IAPR/mentor/"
        "PG_DUMMY/py_cck_code/AUTO_PC) -> read_files读各子目录.py源码 -> editor写generate_aether_api_pdf.py->gen_report.py"
        "(analyze_codebase()+gen_pdf(),reportlab不可用回退.txt) -> SandBox run_code探reportlab(不可用) -> 最终交付"
        "Aether_pyAether_API_and_DB_Guide.txt(结构化手册:四设计模式[异常处理/Config类/Lisp辅助/GOA API/AI APR流程]+"
        "五最佳实践[资源释放/异常安全/只读/SDL/层次遍历/事务]+附录速查[文件分类/对象属性]). "
        "gold依赖live /apps/.../python_ae源码树+live reportlab -> .75沙盒不可达 -> A-档disqualified(tooling) -> "
        "B-档synthesized L1-boundary(离线fixture python_ae代码库->结构化报告生成器,stdlib-only,确定性). "
        "与现有layout_aether case(GdsRectGen/ABMatchPlacementCheck/CTLEAether/ScmosStructId/AddCellPin/ListInstCV/"
        "PinFloatAether等具体版图操作)正交——本案=代码库静态分析->API参考手册生成,首次覆盖该子主题,taodu首个nwwkg trace."
    ),
}

case = {
    "task_id": "EDA-Eval-DesignFlow-AetherApiSummary-001",
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": atts,
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["outputs/report.md", "outputs/report_summary.json"],
    "test": check_src,
    "budget": {"max_turns": 20},
    "metadata": {
        "domain": "layout_aether",
        "task_name": "AetherApiSummary",
        "scenario": "aether pyAether codebase static analysis -> API & DB-processing reference manual",
        "direction": "layout_aether",
        "layer": "pyAether-API",
        "topic": "codebase-analysis-to-doc",
        "difficulty": "L1-boundary",
        "design": "B-faithful-seed-synthesized",
        "tcr_refs": ["1791862539977_nwwkg"],
        "heavy": "offline-stdlib",
        "wall_time_sec": 600,
        "trace_source": trace_source,
        "test_rationale": test_rationale,
    },
}

# verify id not already present
existing = set()
with open(JSONL, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            existing.add(json.loads(line).get("task_id"))
        except Exception:
            pass
assert case["task_id"] not in existing, "DUPLICATE id already in jsonl: %s" % case["task_id"]

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")

print("appended %s (test=%dB, attachments=%d)" % (case["task_id"], len(check_src), len(atts)))
print("attachment list:")
for a in atts:
    print("  " + a)
