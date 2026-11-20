#!/usr/bin/env python3
"""Append AnalogGroupCfgMergeDummy-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json, os

CASE = "EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
A_DIR = f"{ROOT}/assets/{CASE}"
REF_DIR = f"{ROOT}/reference/{CASE}"
JSONL = f"{ROOT}/EDA-Eval-DesignFlow_D.jsonl"

with open(f"{REF_DIR}/check.py") as f:
    check_src = f.read()
with open(f"{A_DIR}/prompt.txt") as f:
    prompt = f.read()

attachments = [
    f"assets/{CASE}/prompt.txt",
    f"assets/{CASE}/task_brief.md",
    f"assets/{CASE}/base_cfg_A.json",
    f"assets/{CASE}/patch_A.json",
    f"assets/{CASE}/labels_A.txt",
    f"assets/{CASE}/layout_inst_A.txt",
    f"assets/{CASE}/sch_inst_A.txt",
]

test_rationale = (
    "16 条断言：①submit.zip 顶层仅含 gg_cfg_merge_verify.py(及 B 输出 5 文件)且无 check/reference/negative/.jsonl/hidden 泄漏 "
    "②gg_cfg_merge_verify.py 经 py_compile 通过(语法合法) "
    "③B-run exit0 且产出 5 个文件(merged_cfg.json/merge_report.md/dummy_audit.json/instance_diff.json/verdict.json)均存在 "
    "④merged_cfg_B.json 为合法 JSON 且与 deep_merge(base_B, patch_B) 逐键相等(深合并正确,非覆盖键保留 base 原值) "
    "⑤merged_cfg_B 中 patch 指定叶子(DifferentPair.Matching.Dummy.TopBottom)被覆盖为 patch 值 \"1\" "
    "⑥merged_cfg_B 中被改段的兄弟键(DP.Dummy.LeftRight、DP.Matching.Style/Mode/Rows)与 base 相等(未受波及) "
    "⑦merged_cfg_B 中其它 PatternCfg 段(CurrentMirror/Cascode)与 base 完全相等(未改动) "
    "⑧merge_report.md 含 \"Changed keys\" 段、被改键路径(TopBottom)及其旧值→新值,且含 \"unchanged\" 段声明未改段 "
    "⑨dummy_audit.json 的 n_labels>0 且每个 O label 的 xy 为 [x,y] 二元数值列表 "
    "⑩dummy_audit.json 的 distribution 中 top>0 且 bottom>0(B patch 为 TopBottom=1,方位分布须两侧均有) "
    "⑪instance_diff.json 的 layout_only 非空且至少一个名字含 \"Dum\" 或以 \"GG_DUM\" 开头(GG 生成 dummy) "
    "⑫instance_diff.json 中所有 schematic instance 名都出现在 shared(即在 layout 中存在) "
    "⑬verdict.json 的 overall==\"PASS\" 且 checks 列表每条 pass==True "
    "⑭B2 跨输入:B2-run exit0、merged_cfg_B2==deep_merge(base_B2,patch_B2)、CurrentMirror.Dummy.LeftRight 被覆盖为 \"1\" 而 DifferentPair.Dummy.LeftRight 保持 base 值(未改)、B2 verdict==PASS "
    "⑮反硬编码:候选源码不含 A 专有字面量(VwlpRefAmpIP/AnaWeave_demo/A 坐标 100,400 等),且 B 的 merge_report.md 不含 A 单元名 VwlpRefAmpIP(B 输出须来自 B 输入) "
    "⑯确定性:对 B 输入连跑 3 次,5 个输出文件的 sha256 拼接值三次完全一致"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": prompt,
    "attachments": attachments,
    "expected_artifacts": ["gg_cfg_merge_verify.py"],
    "budget": {"max_turns": 30, "timeout_sec": 1800},
    "metadata": {
        "trace_source": {
            "user": "ziyuny",
            "host": "10.129.32.190",
            "session_file": "1791532940009_ca92c.messages.json",
            "match_count": 108,
            "real_task_summary": (
                "AnaWeave Group Generator (Empyrean 模拟版图自动放置) 配置合并 + dummy 审计。"
                "用户 ziyuny 在 Aether 中对模拟单元 VwlpRefAmpIP 走 Group Generator 流程生成版图,"
                "要求对差分对(DifferentPair)左右两端加 dummy(U#2/U#3),后又要求不加 dummy 重新生成(U#4/U#5)。"
                "cline 产出: train_ddgoa_test_VwlpRefAmpIP_patch.json(部分覆盖 cfg,如 {PatternCfg.DifferentPair.Matching.Dummy.LeftRight:1}) + "
                "verify_merged_cfg_VwlpRefAmpIP_dpDummyLR_20261009.py(读 merged+base cfg,验 DP.Dummy.LeftRight==1 而 TopBottom/Style/Mode 与 CurrentMirror 段不变) + "
                "verify_gg_generated_dummies_VwlpRefAmpIP.py(pyAether 打开 schematic+layout cellview,找 layout-only instance=GG 生成 dummy,报 xy) + "
                "scan_layout_labels_VwlpRefAmpIP.py(扫 layout label,GG 约定 dummy label 改写为 'O',报 O label 位置) + "
                "dump_cfg_dummy_sections.py(dump DeviceCfg/DummyCfg/LibCfg/TapCfg/PatternCfg.DifferentPair)。"
                "A-faithful 不可移植(live Aether Group Generator + cellview 锁 + project lib),故 B 级合成: "
                "读 base cfg JSON + patch JSON(深合并)+ layout label 扫描 txt + layout/schematic instance txt -> "
                "产出 merged_cfg.json + merge_report.md + dummy_audit.json + instance_diff.json + verdict.json,"
                "check 验结构(深合并/patch 生效/兄弟键不变/其它段不变/O label 方位分布/layout-only dummy/sch 全在 layout/verdict PASS/跨输入 B2/反硬编码/确定性),L1 离线可验。"
            ),
        },
        "domain": "analog_context",
        "grade": "B",
        "L_level": "L1",
        "track": "synthesized",
        "test_rationale": test_rationale,
    },
}

# verify k_rationale == k_check == 16
import re
k_rat = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯]", test_rationale))
print(f"k_rationale = {k_rat}")
# count conditions in check.py CONDITIONS list
conds = re.findall(r'^\s*\("([a-z])",', check_src, re.M)
print(f"k_check = {len(conds)} (conds={conds})")
assert k_rat == 16 and len(conds) == 16, f"assertion gate: k_rationale={k_rat} k_check={len(conds)}"

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", JSONL)
# verify
n = sum(1 for _ in open(JSONL))
print("D.jsonl lines now:", n)
