#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SimSavedCornerComplete-001 to B jsonl."""
import json, os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SimSavedCornerComplete-001"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")

with open(os.path.join(BENCH, "assets", CID, "prompt.txt")) as f:
    prompt = f.read()
with open(os.path.join(BENCH, "reference", CID, "check.py")) as f:
    test = f.read()

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        {
            "name": "sim.saved.total",
            "source": "assets/" + CID + "/sim.saved.total",
            "desc": "示例仿真输入文件 A(可见):每个 case 一行 <base_path>_<FF|TT|SS>.X4 <PVT_TAG> X4,5 个 PVT corner(FF1.3v110C/FF1.3v-40C/TT0.94v25C/SS0.94v110C/SS0.94v-40C),部分 case 缺 corner;来自 ynbai 的 cline trace,需识别缺失 corner 并补全",
        },
        {
            "name": "task_brief.md",
            "source": "assets/" + CID + "/task_brief.md",
            "desc": "交付接口说明(<=3 行):脚本打进 outputs/submit.zip,运行 python3 sim_saved_corner_complete.py <input> <output>,输出缺失 corner 的补充行",
        },
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": None,
    "test": test,
    "budget": None,
    "metadata": {
        "domain": "characterization",
        "track": "faithful",
        "harness": "cline",
        "level": "L1",
        "trace_source": {
            "user": "ynbai",
            "host": "hfhds201",
            "session_file": "1794018867939_1qlnn.messages.json",
            "match_count": 2736,
            "real_task_summary": "ynbai @ hfhds201(=.75 local) 为 DDR5 DRVQA 仿真向量补全 PVT corner。USER#0 原话「识别...sim.saved.total 文件,文件为仿真输入文件,内容例如[5 行 case+corner 路径]...为仿真 case Golden005_..._3600 的 5 个 corner 的输入,每一个 case 应该都有 5 个,但是文件不全,部分不是五个,帮忙补全,补全文件生成为 sim.saved.total.zl,相同 corner 不同电压温度下前方相同」+ USER#1「多出来的 case 行输出到 sim.saved.total.zl.more 中」——纯需求轮给目标(5 corner 补全)+方法(同 corner 不同 V/T 前方相同)+输出位置,未给根因/修复。trace 39 msgs/328KB,fresh(11-07 10:56 写入),read_files/run_approved_command/editor。assistant 写 extract_more.py 解析 case 分组(去 _FF/_TT/_SS.Xn 后缀)+缺 corner 补全+输出 .zl.more(244 行=122 case×2 缺)。",
        },
        "test_rationale": "17 条断言:①submit.zip 含一个 .py 脚本 ②该 .py 脚本 py_compile 通过 ③无参数/参数数错时非零退出 ④在隐藏 B 上运行 exit 0 且生成 output 文件 ⑤每行格式 <path> <PVT> X<4|8> 且 PVT ∈ 5 expected(FF1.3v110C/FF1.3v-40C/TT0.94v25C/SS0.94v110C/SS0.94v-40C) ⑥output 行数 == 7 且无空行 ⑦output 无行与 B 已有行重复(补充行是新缺失 corner,非已有行) ⑧ProbeB_2700 的 TT0.94v25C 补充行存在 ⑨ProbeB_2700 的 SS0.94v-40C 补充行存在 ⑩ProbeC_4800 的 FF1.3v-40C 补充行存在 ⑪ProbeD_3600 的 SS0.94v110C 补充行存在 ⑫ProbeD_3600 的 SS0.94v-40C 补充行存在 ⑬ProbeE_2400 的 FF1.3v110C 补充行存在 ⑭ProbeE_2400 的 TT0.94v25C 补充行存在 ⑮完整 case ProbeA_3200/ProbeF_4000 在 output 中无任何行 ⑯路径后缀正确(缺失 FF 用 _FF.Xn / SS 用 _SS.Xn / TT 用 _TT.Xn) ⑰跨输入 A!=B(在可见 A 上运行得 3 行 Golden 与 B 的 7 行 Probe 不同,防硬编码)",
    },
}

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify
with open(JSONL) as f:
    n = sum(1 for _ in f)
print("appended", CID, "-> jsonl now", n, "lines")

# verify last line parses + assertion gate
last = None
with open(JSONL) as f:
    for last in f: pass
d = json.loads(last)
tr = d["metadata"]["test_rationale"]
# count assertions ①..⑰
import re
k_rat = len(re.findall(r"[①-⑰]", tr))
# count conditions in test
k_check = d["test"].count("raise AssertionError(")
# map labels a..q
labels = re.findall(r'raise AssertionError\("([a-q]):', d["test"])
print("k_rationale =", k_rat, "| k_check(raise) =", k_check, "| labels =", "".join(labels))
print("gate:", "PASS ✓" if (k_rat == k_check and k_check >= 8) else "FAIL ✗")
print("trace_source:", json.dumps(d["metadata"]["trace_source"], ensure_ascii=False)[:160])
