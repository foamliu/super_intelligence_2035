#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build & append EDA-Eval-DesignFlow-PowerFill-001 jsonl entry (idempotent)."""
import json, os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
JSONL = os.path.join(BENCH, "benchmarks", "EDA-Eval-DesignFlow", "EDA-Eval-DesignFlow.jsonl")
REF = os.path.join(BENCH, "benchmarks", "EDA-Eval-DesignFlow", "reference",
                   "EDA-Eval-DesignFlow-PowerFill-001")
CASE = "EDA-Eval-DesignFlow-PowerFill-001"

check_py = open(os.path.join(REF, "check.py"), encoding="utf-8").read()

prompt = (
    "你是 EDA 团队的后端流程工具开发者。用户 e0014566 在做一块 DRAM test chip 的 PowerFill"
    "（电源填充）后端流程：Virtuoso SKILL 驱动 RSCALC → AutoVia → PowerFill 三段迭代降低关键字网"
    "电阻。PowerFill 跑完会导出一块带 power-fill 金属的 GDS，流程下一步要审计这块 GDS：确认顶层 cell、"
    "cell 树（特别是 PowerFill 自动生成的 `*_auto_pgfill` marker cell 是否落进去了）、层表、bbox、"
    "精度/格式，以及最关键的——**自动发现 power net**（PowerFill 的 powernet 配置可留空，工具自己去"
    "GDS 的 text label 里找）。\n\n"
    "工具环境（.75 EDA 沙盒，已验证可用）：\n"
    "- `calibredrv` 在 PATH（`/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/calibredrv`，"
    "Calibre DESIGNrev v2020.1_36.18，headless 无需 X11）。\n"
    "- 子命令 `calibredrv -a layout peek <gds> <flag...>`，可组合：`-topcell`/`-cellcount`/`-cells`/"
    "`-layers`/`-bbox`/`-precision`/`-format`/`-units`/`-celltext <cellname>`。组合例 "
    "`-topcell -cellcount -precision -format -units -bbox` 输出形如 "
    "`units 0.00025 precision 4000.0 format GDS topcell testa_opt1 cellcount 31 bbox {testa_opt1 {3530 -21410 1196470 57410}}`。"
    "`-celltext <cell>` 输出 `{<cell> {label x y layer dtype} ...}`。⚠️ `-all` 在 v2020.1 不存在。\n"
    "- calibredrv 会在 cwd 建一个 `.calibredrv_workspace` 目录（正常，别写进报告）。\n\n"
    "asset A（你能看到）：`gds_A.gds`（真实 PowerFill 流程中间产物 GDS，221184 字节，topcell testa_via1，"
    "cellcount 29，cell 树里**没有** `*_auto_pgfill` cell）+ `task_brief.md`（详细任务说明、JSON schema、"
    "pwrnet 自动发现规则、交叉校验规则）。\n\n"
    "交付：`outputs/submit.zip`，内含**恰好一个**纯标准库 ASCII Python 文件 `pf_audit.py`。脚本从 `argv[1]`"
    "读 GDS 绝对路径，用 `calibredrv -a layout peek` 真跑（subprocess）解析 GDS，向 stdout 打印**恰好一个**"
    "JSON 对象，字段：topcell、cellcount、cells、has_auto_pgfill、auto_pgfill_cells、layers、bbox、"
    "precision、format、units、filesize、text_labels、pwrnets。\n\n"
    "**pwrnet 自动发现规则**（PowerFill 关键逻辑）：从 topcell celltext 取 text label unique 集合，"
    "①排除层名 token（`^[A-Z]\\d+$` 如 M1/V1/CT）；②折叠 Cadence 全局 bang（`vdd!` 与 `vdd` 归并为 vdd）；"
    "③剩余按字典序输出。**has_auto_pgfill** = cells 里存在以 `_auto_pgfill` 结尾的 cell（PowerFill 真跑过的 marker）。\n\n"
    "评分会换一块结构不同的隐藏 PowerFill GDS（B，你不可见）真跑你的脚本，逐字段比对真实值；同时把你的脚本"
    "跑在 A 上做交叉校验（同一脚本在 A 上必须报 testa_via1/29/无 auto_pgfill/221184，与 B 的 "
    "testa_opt1/31/有 auto_pgfill/243712 不同，硬编码 B 期望值会在 A 上露馅）。脚本必须经 calibredrv 真跑"
    "解析真实 GDS，不能只 print 期望串，不能靠文件名猜 topcell。≥8 个独立条件，3 次重跑关键字段稳定。"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        {"name": "gds_A.gds", "source": "gds_A.gds",
         "desc": "可见真实 PowerFill 流程中间产物 GDS A（e0014566 RSCALC/AutoVia/PowerFill flow 的 testa_via1 段，221184 字节，topcell testa_via1，cellcount 29，cell 树无 *_auto_pgfill marker，bbox {3530 -21410 1196470 57410}，precision 4000.0，format GDS，text_labels {M1,vbb,vdd,vdd!,vss}）"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "真实任务说明：e0014566 PowerFill GDS 审计 via calibredrv，含 calibredrv peek API 文档、JSON report schema、pwrnet 自动发现规则（排除层名+折叠 vdd!）、has_auto_pgfill marker 判定、隐藏 B 交叉校验规则"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["pf_audit.py"],
    "test": check_py,
    "budget": {"max_turns": 20},
    "metadata": {
        "trace_source": {
            "user": "e0014566",
            "host": "hfeg0plg58",
            "session_file": "1785846039627_itvhk.messages.json",
            "match_count": 689,
            "real_task_summary": (
                "e0014566 的 PowerFill 后端流程会话（cwd /home/e0014566/test_layout_rscalc_flow_4，356 msgs/178 user+178 asst，"
                "tool_use：run_commands 111 + read_files 24 + search_codebase 13 + SandBox_MCP_Server__run_code 10 + editor 10）。"
                "用户首条 '请完整跑一下 prompt_flow.md 整个的过程' 驱动 RSCALC → AutoVia → PowerFill 三段迭代降阻 flow on testa cell。"
                "主线：①RSCALC（Virtuoso SKILL run_rscalc_nogui.il）跑电阻 → 解析 *.rvn baseline_rpoints.csv；"
                "②AutoVia（run_autovia_nogui.il）插入 via 生成 testa_via1 cell；③PowerFill（genPowerFill.py + run_powerfill_nogui.il）"
                "电源填充，pwrnet 留空自动从 GDS text label 发现（vdd/vss/vbb），跑完在 cell 树加 *_auto_pgfill marker cell；"
                "④calibredrv -a layout peek 审计 GDS topcell/layers/text labels；⑤calibre DRC short-check（10G4plus_Short_Check.rule → "
                "short.results/short.summary，TOTAL RESULTS GENERATED=0 即 clean）。用户两次关键 catch：A) PowerFill 未生成填充（powernet 空→"
                "自动发现失败）；B) GDS 传递 bug——检测到已有 GDS 应该用新生成的覆盖而非复用旧。真实 artifacts：testa_via1.gds(221KB,"
                "topcell testa_via1,cellcount 29,无 auto_pgfill)+testa_opt1.gds(243KB,topcell testa_opt1,cellcount 31,含 testa_via1_auto_pgfill)"
                "+test.svrf/10G4plus_Short_Check.rule+short.results。关键字 virtuoso:672/calibre:187/cellview:29。本 case 抽取其中 "
                "'calibredrv GDS 结构审计 + PowerFill pwrnet 从 text label 自动发现 + *_auto_pgfill marker 判定' 这一可复用 L2 子流。"
            ),
        },
        "domain": "physical_verify",
        "layer": "L2",
        "layer_rationale": (
            "check() 在隐藏 PowerFill 输出 GDS B（testa_opt1.gds，结构/cellcount/has_auto_pgfill/filesize 全不同）上经 "
            "`calibredrv -a layout peek` 真跑 Mentor Calibre DESIGNrev subprocess，候选 pf_audit.py 必须驱动 EDA 沙盒 "
            "calibredrv 解析真实 GDS（topcell/cell 树/层/bbox/text label），不是离线文本或硬编码；并交叉跑在 A 上做跨输入 guard。"
        ),
        "test_rationale": (
            "13 条断言：① zip 含恰好一个名为 pf_audit.py 的文件 ② pf_audit.py 经 py_compile 通过 "
            "③ 候选在隐藏 B 上 subprocess 退出 0 且产出合法 JSON 报告 ④ topcell == testa_opt1（B 真实顶层） "
            "⑤ cellcount == 31（B，非 A 的 29） ⑥ has_auto_pgfill==True 且 auto_pgfill_cells==[testa_via1_auto_pgfill]"
            "（PowerFill marker，A 无） ⑦ bbox == {3530,-21410,1196470,57410} ⑧ precision==4000.0 且 format==GDS 且 units==0.00025 "
            "⑨ pwrnets == [vbb,vdd,vss]（自动发现：M1 排除、vdd!/vdd 折叠） ⑩ text_labels == [M1,vbb,vdd,vdd!,vss]（完整 unique 集合） "
            "⑪ filesize == 243712（B，非 A 的 221184，跨输入数值判别） ⑫ 3 次重跑 topcell/cellcount/has_auto_pgfill/filesize/pwrnets 稳定 "
            "⑬ 跨输入 guard：在 A 上报 testa_via1/29/无 pgfill/221184 且 ≠ B（击败 print-expected/ignore-input/always-B stub）"
        ),
    },
}

lines = open(JSONL, encoding="utf-8").readlines() if os.path.exists(JSONL) else []
out = [l for l in lines if json.loads(l).get("task_id") != CASE]
out.append(json.dumps(entry, ensure_ascii=False))
open(JSONL, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("written", CASE, "->", JSONL, "lines=", len(out))
