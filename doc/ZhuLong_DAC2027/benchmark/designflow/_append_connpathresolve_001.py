#!/usr/bin/env python3
"""Build the jsonl entry for EDA-Eval-DesignFlow-ConnPathResolve-001 and append
to EDA-Eval-DesignFlow_C.jsonl."""
import json
import os

REF = "reference/EDA-Eval-DesignFlow-ConnPathResolve-001"
CASE = "EDA-Eval-DesignFlow-ConnPathResolve-001"

check_py = open(REF + "/check.py").read()

prompt = (
    "我是版图/物理验证工程师 xxchen，在 hfeg0pkn001 上开发 DRC connectivity QA 工具"
    "（/home/xxchen/workspace/small_tool/drcConnect/0.2/connectivity/）。"
    "工程师把全连接按 sub-stack 分组拆解，我需要脚本按分组用 findPath 自动解析出所有连接路径并生成 connectPath.rep 报告。\n\n"
    "用户原话（逐字，多轮迭代中提出 bottomLayer 约定）：\n\n"
    "「你理解错了，需要每个分组连接的最底层直接 follow 用户给的最底层。"
    "如：[\"M8\" ,  \"HSV\" ,  \"HSP\"  ], [\"M7\" ,  \"V7\" ,  \"M8\"  ], "
    "[\"M6\" ,  \"V6\" ,  \"M7\"  ], [\"M5\" ,  \"V5\" ,  \"M6\"  ], "
    "[\"M4\" ,  \"V4\" ,  \"M5\"  ], [\"M3\" ,  \"V3\" ,  \"M4\"  ], "
    "[\"M2\" ,  \"V2\" ,  \"M3\"  ], [\"M1\" ,  \"V1\" ,  \"M2\"  ], ], "
    "以 M1 为 bottomLayer，再通过 findPath 把这段连接按照原先的逻辑进行解析。不再包含分组外的层。」\n\n"
    "「我们约定下，以每个分组的最后一个连接的第一个 metal 作为 bottomLayer，"
    "如：[\"M1\",  \"CT\",  \"TCP\", \"M0U\"], bottomLayer 就是 M1 了，TCP 和 M0U 不作为 bottomLayer。"
    "这里就不应该报错了：ERROR: TCP used as the primary target of edge [M1, CT, TCP, M0U] must be declared "
    "in bottomLayer (it becomes a bottom layer). 修改你的脚本。」\n\n"
    "附件 config_A.py 是我真实的 connectivity 配置（5 个 sub-stack group + bottomLayer）作示例输入。"
    "现在请把这条解析逻辑做成独立可复用的单文件脚本 connpath_resolver.py（纯 stdlib），"
    "按上面 bottomLayer 约定逐组用 findPath 解析路径，写 connectPath.rep 报告"
    "（per-group 路径 + shield relations + decomposition check findings）。"
    "具体交付接口见 task_brief.md。"
)

entry = {
    "task_id": "ConnPathResolve-001",
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/EDA-Eval-DesignFlow-ConnPathResolve-001/config_A.py",
        "assets/EDA-Eval-DesignFlow-ConnPathResolve-001/task_brief.md",
    ],
    "test": check_py,
    "metadata": {
        "trace_source": {
            "user": "xxchen",
            "host": "hfeg0pkn001 (10.129.2.10)",
            "session_file": "1793002485489_j9ycq",
            "match_count": 288,
            "real_task_summary": (
                "xxchen 在 /home/xxchen/workspace/small_tool/drcConnect/0.2/connectivity/ "
                "迭代 DRC connectivity QA 工具（conncheck 包）。多轮：connectPath.rep 路径仍是旧路径，"
                "要求按工程师拆解的 sub-stack + findPath 自动解析所有路径；明确 bottomLayer 约定="
                "每个分组最后一条边的首个金属（如 [M1,CT,TCP,M0U] 的 bottom 是 M1，TCP/M0U 不是），"
                "findPath 只在本组边集上解析、不跨组；修复 'TCP used as primary target of edge must be "
                "declared in bottomLayer' 报错；调整 pattern 绘制间距（组间 3x 常规间距）；修复 sameNet "
                "HSP 连接与相邻 group 图形 overlap。gold=graph.resolve_substacks + verify_decomp."
                "check_decomposition + write_path_report。本案聚焦前两条（bottomLayer 约定 + 逐组 findPath + "
                "decomposition check），reframe 为离线单文件 connpath_resolver.py。"
            ),
        },
        "domain": "physical_verify",
        "track": "B",
        "tier": "L1",
        "test_rationale": (
            "17 条断言：①submit.zip 存在且为合法 zip ②zip 含 .py 入口 ③候选在隐藏 B 上 exit0 "
            "④报告文件产出且非空 ⑤首行 'connectPath report - total 7 paths'（B 正确总数）"
            "⑥含 'sub-stack resolution' 段标记 ⑦group 0 段头 (bottomLayer: N1) 存在 "
            "⑧group 0 path 1 精确 'N1 -> W1 -> N2 -> W2 -> N3 -> W3 -> TOP' ⑨group 1 恰 3 条路径 "
            "⑩group 1 含 N1->CV->SX / N1->CV->SY / N1->CV->SZ 三分支 ⑪group 3 段头 (bottomLayer: GND) "
            "⑫group 3 path 精确 'GND -> PX -> N0C -> PU -> N0U' ⑬group 4 path 精确 'GND -> PX -> MX -> PU -> N0U' "
            "⑭shield relations 段含 'N1 CV : SX->SY->SZ' ⑮decomposition check 段存在 "
            "⑯decomposition check 段无 'ERROR:'（B 良构）⑰跨输入闸门：报告不含任何 A 专属层/网 token（防硬编 A）"
        ),
    },
}

out = "EDA-Eval-DesignFlow_C.jsonl"
with open(out, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", out)
print("task_id:", entry["task_id"])
print("prompt len:", len(entry["prompt"]))
print("test bytes:", len(entry["test"]))
print("attachments:", entry["attachments"])
