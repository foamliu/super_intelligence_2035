#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build & append EDA-Eval-DesignFlow-DummyMeas-001 jsonl entry (idempotent)."""
import json, os, sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
JSONL = os.path.join(BENCH, "benchmarks", "EDA-Eval-DesignFlow", "EDA-Eval-DesignFlow.jsonl")
REF = os.path.join(BENCH, "benchmarks", "EDA-Eval-DesignFlow", "reference",
                   "EDA-Eval-DesignFlow-DummyMeas-001")
CASE = "EDA-Eval-DesignFlow-DummyMeas-001"

check_py = open(os.path.join(REF, "check.py"), encoding="utf-8").read()

prompt = (
    "你是 EDA 团队的 PDK QA 工具开发者。用户 xinqiaoz 在做 DYT4E dummy pattern QA：给定一块"
    "\"跑完 dummy\"的 GDS（每层一个独立 dummy GDS），需要用 Empyrean Skipper 批处理模式"
    "（`skipper <tcl> <gds> -noterm`）量测这块 GDS 的几何与层信息（顶层 cell、Layer/Purpose 表、"
    "cell bbox、文件大小、精度、格式、层级深度），核对是否符合 dummy guideline。\n\n"
    "工具环境（.75 EDA 沙盒，已验证可用）：\n"
    "- Skipper 二进制在 PATH 中（`/apps/empyrean/tools/skipper/bin/skipper`），批处理 "
    "`skipper <your.tcl> <gds_abs_path> -noterm`，退出码 0 表示正常。\n"
    "- 可用 Tcl API：`dbImport <gds_abs_path>`（必须绝对路径，返回库句柄 $h）、"
    "`dbLibTopCell $h`（返回顶层 cell 名）、`dbLibSummary -lib $h`（返回完整摘要字符串，"
    "内含 File Size / Format / Precision / MaxLevel / CellNum / Lpp Statistics 层表 / "
    "ID Cells BBox without Text 行含 `(xl, yl, xh, yh)` 单位 um）。其它 dbLibBBox/dbLibCells/"
    "dbLayerCount 等 API 不存在。\n"
    "- argv 取参数：`set g [lindex $argv 0]`。Skipper 加载时还会自动往 stdout 打一段 SUMMARY"
    "（total rect/polygon/...），但那部分不在 dbLibSummary 返回值里，你的脚本只依赖 "
    "dbLibSummary 返回串。\n\n"
    "asset A（你能看到）：`LM1.gds`（真实 dummy GDS，138776 字节，topcell QA_chip_CMP_LM1，"
    "单层 352_8）+ `guideline_A.json`（A 的 dummy guideline）+ `task_brief.md`（详细任务说明与"
    "AUDIT 行 schema）。\n\n"
    "交付：`outputs/submit.zip`，内含**恰好一个** ASCII Tcl 文件 `dummy_audit.tcl`。脚本从 argv[0]"
    "读 GDS 绝对路径，dbImport→dbLibTopCell→dbLibSummary，解析摘要串，向 stdout 打印**恰好一行**"
    "（14 个字段，`|` 分隔）：\n"
    "`AUDIT|<topcell>|<cellnum>|<nlpp>|<lpp_csv>|<xl>|<yl>|<xh>|<yh>|<width>|<height>|"
    "<filesize>|<precision>|<format>|<maxlevel>`\n"
    "其中 width=xh-xl、height=yh-yl（um），lpp_csv 为所有 layer_purpose 逗号拼接。脚本末尾 exit。\n\n"
    "评分会换一块结构不同的隐藏 dummy GDS（B，你不可见）真跑你的脚本，逐字段比对真实值；同时把"
    "你的脚本跑在 A 的 GDS 上做交叉校验（同一脚本在不同 GDS 上必须报出不同的 topcell/层/尺寸，"
    "硬编码 B 的期望值会败）。脚本必须经 `skipper dummy_audit.tcl <gds> -noterm` 真跑（subprocess），"
    "不能只 print 期望串。"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        {"name": "LM1.gds", "source": "LM1.gds",
         "desc": "可见真实 dummy GDS A（DYT4E_WHCFP_LHCRP_DHCFP/v0d5_rev01/frame/QA/LM1.gds，138776 字节，topcell QA_chip_CMP_LM1，单层 352_8，bbox (2,1.75,1498.25,498.25)，xinqiaoz axjv8 Dummy Pattern QA trace）"},
        {"name": "guideline_A.json", "source": "guideline_A.json",
         "desc": "A 的 dummy guideline（expected_topcell=QA_chip_CMP_LM1，layer 352，bordSize 1500×500，precision 10000）"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "真实任务说明：xinqiaoz Dummy Pattern QA via Skipper dbImport/dbLibSummary，含 Skipper Tcl API 文档、AUDIT 行 14 字段 schema、隐藏 B 交叉校验规则"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["dummy_audit.tcl"],
    "test": check_py,
    "budget": {"max_turns": 20},
    "metadata": {
        "trace_source": {
            "user": "xinqiaoz",
            "host": "hfeg0pkn004",
            "session_file": "1792149907675_axjv8.messages.json",
            "match_count": 520,
            "real_task_summary": (
                "xinqiaoz 的 Dummy Pattern QA 会话（cwd /home/xinqiaoz/PDK_QA/pdkQaSystem，glm-5.3-flash，"
                "262 msgs/140 tool_use：68 editor+49 run_approved_command+16 read_files）。主线：用 Empyrean "
                "Skipper 批处理 `skipper <tcl> -noterm`（dbImport/dbLibTopCell/dbLibSummary -lpps）从 "
                "DYT4E_WHCFP_LHCRP_DHCFP/v0d5_rev01/frame/QA/ 下的 dummy GDS（LM1/LTM/HSP/...）量测层/bbox/"
                "polygon 统计核对 dummy guideline（config.ini layers/minSpace + calibreDummy.rule）。skipper "
                "GUI 因 libfontconfig 崩，改用 -noterm 批处理。关键字 pdk:2008/calibre:1080/skipper:806/.gds:777。"
                "真实 artifacts：frame/QA/LM1.gds(138KB,layer352_8)+LTM.gds(142KB,layer372_8)+config.ini+"
                "calibreDummy.rule。本 case 抽取其中 'Skipper dbImport+dbLibSummary 量测 dummy GDS 层/bbox/"
                "精度并按 guideline 自检' 这一可复用子流。"
            ),
        },
        "domain": "physical_verify",
        "layer": "L2",
        "layer_rationale": (
            "check() 在隐藏 dummy GDS B（LTM.gds，结构/层/尺寸全不同）上经 `skipper dummy_audit.tcl <gds> "
            "-noterm` 真跑 Empyrean Skipper subprocess，候选 Tcl 必须驱动 EDA 沙盒 dbImport+dbLibSummary "
            "解析真实 GDS 摘要（topcell/层表/bbox/文件大小/精度），不是离线文本或硬编码。"
        ),
        "test_rationale": (
            "13 条断言：① zip 含恰好一个名为 dummy_audit.tcl 的 tcl ② skipper 在隐藏 B 上 subprocess 退出 0 "
            "③ stdout 含 AUDIT 行且 14 字段齐全 ④ topcell == B 真实 QA_chip_CMP_LTM ⑤ cellnum==1 "
            "⑥ lpp_csv==372_8（B 层，非 A 的 352_8，跨输入判别）⑦ bbox xl,yl≈B(1.75,1.75) "
            "⑧ bbox xh,yh≈B(1498,498.25) ⑨ width=xh-xl≈1496.25 且 height=yh-yl≈496.5 "
            "⑩ filesize==142328（B，非 A 的 138776）⑪ precision==10000 且 format==GDSII 且 maxlevel==0 "
            "⑫ 3 次重跑 AUDIT 字段完全一致（随机化，击败硬编码）⑬ 跨输入 guard：在 A(LM1.gds) 上报出 "
            "QA_chip_CMP_LM1/352_8/138776 且与 B 不同（击败 print-expected/always-LTM stub）"
        ),
    },
}

# idempotent: replace if same task_id exists
lines = open(JSONL, encoding="utf-8").readlines() if os.path.exists(JSONL) else []
out = [l for l in lines if json.loads(l).get("task_id") != CASE]
out.append(json.dumps(entry, ensure_ascii=False))
open(JSONL, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("written", CASE, "->", JSONL, "lines=", len(out))
