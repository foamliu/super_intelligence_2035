#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-XProbeHierGen-001 to D.jsonl."""
import json, hashlib, os

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-XProbeHierGen-001"
REF_DIR = os.path.join(BASE, "reference", CASE)

check_data = open(os.path.join(REF_DIR, "check.py"), "rb").read()
check_sha = hashlib.sha256(check_data).hexdigest()
check_size = len(check_data)

entry = {
    "case_id": CASE,
    "task_id": "XProbeHierGen-001",
    "task_id_full": CASE,
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": (
        "这是一个 DRAM 原理图层级 CrossProbe CSV 生成任务（真实 trace 来源：xiwang @ hfeg0pkn002，"
        "调用 FindCir4CrossProbe_wx skill，从芯片物理顶层 ddgoa_top/WOWTOP 递归下降整个 schematic 层级，"
        "找出所有例化目标器件（如 ptn_lvio/ptn_lv）的电路，并按 CrossProbe 标准 10 列 CSV 输出每一行的层级路径）。"
        "\n\n用户在已采集的层级映射基础上提出两件事：\n"
        "(1) 总结某个器件（ptn_lvio / ptn_lv）都用在哪些模块的电路；\n"
        "(2) 重新生成 CrossProbe CSV 时，hierPath 列不需要器件本身的 instance 段——"
        "即把 /XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_Array1GBK1.XI_m1G_TOP.XI_VblhXdecTopE.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2.XMP0<0>"
        " 截成 /XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_Array1GBK1.XI_m1G_TOP.XI_VblhXdecTopE.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2"
        "（截止到直接例化该器件的父电路实例，去掉末尾器件段），同一父实例内多个器件合并为一行。\n\n"
        "附件是合成件（依据 trace 真实结构合成的 fullmap_A.json 层级映射，格式 "
        "{\"lib|parentcell\": {\"childcell\": [\"instname|childlib\", ...]}}）。"
        "请写一个通用脚本 xprobe_hier_gen.py，CLI 接受 --fullmap <json> --seed <cell> --mode <leaf|parent> --out <csv>，"
        "读取层级映射，自动识别根（不被任何 cell 例化的 cell），构建目标器件的祖先闭包做剪枝 DFS，"
        "leaf 模式按器件实例逐位展开总线输出（hierPath 含器件段、cellName=器件名），"
        "parent 模式按父电路实例去重输出（hierPath 截止父电路实例、cellName=父电路名），"
        "每段实例名加 X 前缀，输出标准 10 列 CSV。隐藏输入 B 结构与 A 不同（不同 root/seed/层级/总线），判分只跑 B。"
        "完成后把脚本打包进 outputs/submit.zip。"
    ),
    "attachments": [
        "assets/EDA-Eval-DesignFlow-XProbeHierGen-001/fullmap_A.json",
        "assets/EDA-Eval-DesignFlow-XProbeHierGen-001/task_brief.md",
    ],
    "test": check_data.decode("utf-8"),
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 20},
    "metadata": {
        "trace_source": {
            "user": "xiwang",
            "host": "hfeg0pkn002",
            "session_file": "1794018796078_ftu9v.messages.json",
            "match_count": 497,
            "real_task_summary": (
                "用户(xiwang@hfeg0pkn002)调用 FindCir4CrossProbe_wx skill,从 ddgoa_top/WOWTOP 递归下降整个 schematic 层级,"
                "agent 写 collector.py 在 pyAether 沙箱内做实例级 BFS 采集 fullmap.json(8985 cell 闭包,265 个直接例化 ptn_lvio 的父 cell),"
                "写 builder.py 做实例级遍历(按 ptn_lvio 祖先剪枝+总线逐位展开+X 前缀)输出 CrossProbe 10 列 CSV(141725 行 ptn_lvio 器件实例)。"
                "用户后续:(U1)总结 ptn_lvio 都用在哪些模块电路->agent 按 6 库 265 父 cell 归纳功能模块;"
                "(U2)同样总结 ptn_lv(394 父 cell,185619 行 CSV);"
                "(U3)重新生成 ptn_lvio CSV,hierPath 不需要器件本身 instance 段,举例 /XI_C_Top...XI_VblhDigDrvCmpIP_2.XMP0<0> 换成 /XI_C_Top...XI_VblhDigDrvCmpIP_2,"
                "agent 改 builder 加 parent 模式:父电路实例级去重(45161 器件->49524 父电路实例),hierPath 截止父电路,instName/libName/cellName 同步改父电路。"
                "会话 129 msgs 497 D-domain 命中(schematic:154 netlist:340 hspice:3),模型 GLM-5.2。"
                "真实资产 /proj/ddgoa/V0/libs 与 /ai_sandbox/ddgoa/V0/agentdir/xiwang/ 经 NFS 可读但属 xiwang 私有,fullmap.json/builder.py 实物不可直接复用 -> B-grade synthesized:"
                "合成 fullmap_A.json(同结构迷你层级:ddgoa_top|WOWTOP->LP5TOP/LP5TOP_ArrayDie 双分支,ptn_lvio 在 commonIP 分支 6 父 cell,VblhDigDrvIPTop 二次例化测多路径,总线 MP0<3:0>/MP0<1:0> 测逐位展开),"
                "隐藏 B=ddgoa_cmos_top|CHIP_TOP/ptn_lv/CoreTop+IoTop 双分支/12 直接父 cell/WckOscCore 16 位总线(每维度反硬编码)。"
                "候选写通用 xprobe_hier_gen.py(自动找根+祖先闭包剪枝 DFS+leaf/parent 双模式+总线展开+X 前缀+10 列 CSV),离线 L1 验证生成器的层级遍历+双模式语义+反硬编码+确定性。"
            ),
        },
        "domain": "schematic_netlist",
        "grade": "B synthesized",
        "track": "synthesized",
        "level": "L1",
        "test_rationale": (
            "15 条断言：①submit.zip 是合法 zip 且含至少 1 个 .py 脚本 ②脚本经 py_compile 通过 "
            "③在隐藏 B(fullmap_B.json)上以 leaf 模式 subprocess 跑通且生成 csv 文件(exit 0) "
            "④leaf B CSV 表头恰为 10 列 item,hierPath,dbType,instName,libName,cellName,viewName,propertyName,propertyValue,findByProperty "
            "⑤leaf B CSV 行数等于期望(总线逐位展开后 51 行,反硬编码) "
            "⑥leaf B 每个 hierPath 以 / 开头且每段以 X 开头 ⑦leaf B 每行 instName 等于 hierPath 末段 "
            "⑧leaf B 每行 libName=TECHLIB 且 cellName=seed_B(ptn_lv) ⑨leaf B 含 ≥8 个不同总线位展开(如 XMP0<0>..<7>,<0>..<15> 等,反退化) "
            "⑩在隐藏 B 上以 parent 模式 subprocess 跑通且生成 csv 文件(exit 0) ⑪parent B 行数 < leaf B 行数(同父实例多器件去重)且等于期望(13 行) "
            "⑫parent B 每个 hierPath 末段为电路实例(XI_...)而非器件段(XMP...) ⑬parent B 每行 instName 等于 hierPath 末段 "
            "⑭parent B 每行 cellName ≠ seed_B(应为父电路 cell 名) ⑮在 A(fullmap_A.json)+seed_A 上 leaf 跑出行数=18(≠B 的 51,反硬编码 B)且 B leaf 3 次重跑 md5 一致(确定性)"
        ),
        "check_sha256": check_sha,
        "check_size": check_size,
    },
}

out_path = os.path.join(BASE, "EDA-Eval-DesignFlow_D.jsonl")
with open(out_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("Appended to", out_path)
print("check_sha256:", check_sha)
print("check_size:", check_size)

# verify roundtrip: last line test field bytes == disk check.py bytes
with open(out_path) as f:
    lines = f.readlines()
last = json.loads(lines[-1])
assert last["test"].encode("utf-8") == check_data, "test field byte mismatch"
assert last["metadata"]["check_sha256"] == check_sha
assert last["metadata"]["check_size"] == check_size
print("byte-sync OK: test==disk check.py, sha+size match")
print("D.jsonl lines:", len(lines))
