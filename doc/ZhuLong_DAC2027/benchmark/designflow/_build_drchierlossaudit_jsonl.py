#!/usr/bin/env python3
"""Build the jsonl entry for EDA-Eval-DesignFlow-DRCHierLossAudit-001 and
append it to EDA-Eval-DesignFlow_C.jsonl.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-DRCHierLossAudit-001"
REF = os.path.join(BENCH, "reference", CASE)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")

check_src = open(os.path.join(REF, "check.py"), encoding="utf-8").read()

PROMPT = """我是 PDK/DRC 工程师 miccao，工作目录 /home/miccao。我有一份 Calibre DRC-H 的 rundrc.log（约 30 万行，路径 /proj/drvsa/V0/ver/drc/drvsa_top/WOWTOP/0906/rundrc.log）。这份 log 我已经知道哪条 rule 总耗时最长，现在我想做的是 **hierarchy（层次化）失效审计**——不是再做一遍耗时排序。

请你写一个 **离线 Python3 脚本（纯标准库，不依赖 Calibre/pyAether/任何 EDA 工具）**，输入一个 rundrc.log 路径，输出一份 JSON 格式的 hierarchy 失效审计报告。脚本要解析 log 里每个图形操作的两行块：

```
<层名> (HIER TYP=1 CFG=1 HGC=120 FGC=130 HEC=10 FEC=12 IGC=0 VHC=T VPC=T)
CPU TIME = 3  REAL TIME = 5  OPS COMPLETE = 1 OF 1  ELAPSED TIME = 5
```

并完成以下审计：

1. **VHC=F 操作检出**：每个操作若 `VHC=F`（放弃了层次压缩），标记为 hierarchy 失效原因 `vhc_false`。
2. **扁平爆炸检出**：若 `HGC>0` 且 `FGC/HGC >= 10`，标记 `flat_explosion`；若 `HGC==0` 且 `FGC>0`，标记 `zero_hgc_flat_output`。任一原因命中即该操作 `hierarchy_loss=True`。
3. **huge cell 清单**：解析 `ARGUS LAYOUT INPUT INFORMATION` 段里每个 `cell: <name>, instance: <N>, box: <B>, polygon: <P>, path: <path>, text: <T>`，筛出 `instance>=1,000,000`（mass_copy）或 `polygon>=100,000`（big_geom）的 cell，按 instance 降序列出，每个标 `kind`（可同时两类）。
4. **CONNECT 冗余检出**：解析每行 `CONNECT <name> completed. NETS = <n> EPINS = <e> CPU TIME = <c> REAL TIME = <r>`，若 `NETS<50` 标 `near_empty_nets`，若 `EPINS==0` 标 `zero_epins`，命中任一即冗余。
5. **每条 RuleCheck 聚合**：按 `DRC RuleCheck <NAME> COMPLETED.` 归属操作，每条 rule 输出 `ops / vhc_false / loss_ops / max_amp / max_fgc / total_real / has_loss / loss_reasons`。
6. **Top-N 操作**：按 `REAL TIME` 降序取前 10 个操作，每个含 `layer / rule / real / hgc / fgc / vhc / amp / hierarchy_loss / loss_reasons`。
7. **总览**：从 `--- TOTAL CPU TIME = X  REAL TIME = Y`、`--- PROCESSOR COUNT = N`、`--- TOTAL RULECHECKS EXECUTED = N`、`--- TOTAL RESULTS GENERATED = M` 提取总览。
8. **verdict**：存在任一 rule `has_loss`、或 huge cell 非空、或任一操作 `VHC=F` → `HAS_HIERARCHY_LOSS`；否则 `OK`。

报告顶层 JSON 键：`verdict / op_count / vhc_false_count / loss_op_count / huge_cells / redundant_connects / connects_all / per_rule / top_ops / total / modules / input`。

我用 `python3 <你的脚本> <log路径> <输出json路径>` 调用（也兼容只给 log 路径、JSON 打到 stdout 的用法）。请把脚本打包成 `outputs/submit.zip` 提交（zip 里一个 .py 文件即可）。附件 `rundrc_A.log` 是一份我脱敏后的小样本 log，供你理解格式和本地自测——**真实判分会用另一份结构不同的隐藏 log**，所以不要硬编码 A 的任何具体数值。

只读参考（不进沙盒）：log 字段含义 HGC=层次图形数 / FGC=扁平图形数 / VHC=层次压缩标志(T 保留 F 放弃) / VPC=平面压缩标志。"""

RATIONALE = (
    "14 条断言："
    "①submit.zip 干净解压且恰含 1 个 .py 且 py_compile 通过且 hidden B/B2/B3 三份 log 齐 "
    "②B 报告顶层键齐全(verdict/op_count/vhc_false_count/loss_op_count/huge_cells/"
    "redundant_connects/per_rule/top_ops/total) "
    "③B verdict==HAS_HIERARCHY_LOSS "
    "④B op_count==20 且与 log 中 HIER 操作头行数独立重计数一致 "
    "⑤B vhc_false_count==6 且与 log 中 VHC=F 行独立重计数一致 "
    "⑥B huge_cells 含 via_array(mass_copy) 与 rf_inductor(big_geom) 且 filler_cell 被排除 "
    "⑦B huge_cells 按 instance 降序且 via_array 居首 "
    "⑧B redundant_connects 含 MT TL VIA(VT)(near_empty_nets) 与 BY DL(zero_epins) 且 TL MT 被排除 "
    "⑨B per_rule 含全部 6 条 rule 且 NW_CL_019_00 has_loss+vhc_false>=3 且 DL_W_004_00/PX_EXT_005_00 干净 "
    "⑩B top_ops 按 real 降序且 top real>=72 且每条含 hgc/fgc/vhc/amp 字段 "
    "⑪B loss_op_count==6 且与 log 独立重计数(vhc_false 或 amp>=10 或 zero_hgc_flat)一致 "
    "⑫B2 跨输入守卫: verdict==OK 且 loss/huge/redundant/vhc_false 全 0(杀 always-HAS_HIERARCHY_LOSS 与硬编码 B) "
    "⑬B3 跨输入守卫: 全 VHC=T 但 loss_op_count==2 且 loss_reasons 仅 flat_explosion(杀仅查 VHC 的 naive) "
    "⑭确定性: B 跑 3 次 md5 字节一致"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": PROMPT,
    "attachments": ["assets/%s/rundrc_A.log" % CASE,
                    "assets/%s/gen_logs.py" % CASE,
                    "assets/%s/hidden_manifest.json" % CASE],
    "metadata": {
        "trace_source": {
            "user": "miccao",
            "host": "hfeg0plg37",
            "session_file": "1788743635326_keqfx.messages.json",
            "match_count": 303,
            "real_task_summary": (
                "miccao 的 calibre-drc-log-analysis skill 开发会话（318 msgs / 16 user_input）。"
                "UI#0『分析这个log rundrc.log 看哪步耗时最长』→ UI#31 /skill-creator 详述："
                "DRC log 拆解、图形计算耗时溯源到 rule、HGC/FGC 比判断 hierarchy 失效、CONNECT 冗余检查、"
                "huge cell 清单 → UI#128『层次化被破坏的运算步骤单独列出，标明步骤名/时间/hgc/fgc 前后变化』→ "
                "UI#294 封装成 skill。本 case 取其 hierarchy 失效审计子任务（区别于 DRCTimeStats 的耗时排序）。"
            ),
        },
        "domain": "physical_verify",
        "test_rationale": RATIONALE,
    },
}

# guard gate: k_rationale == k_check >= 8
import re
k_check = len(set(re.findall(r'_fail\("([a-z])"', check_src)))
# count circled-number marks in rationale
marks = re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]", RATIONALE)
k_rationale = len(marks)
print("k_check=%d k_rationale=%d" % (k_check, k_rationale))
assert k_rationale == k_check, "GATE FAIL: k mismatch"
assert k_check >= 8, "GATE FAIL: k_check < 8"
assert RATIONALE.startswith("14 条断言："), "GATE FAIL: rationale prefix"

# append (idempotency: skip if task_id already present)
existing = []
if os.path.exists(JSONL):
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line)
                if o.get("task_id") == CASE:
                    print("ALREADY PRESENT, skipping append")
                    break
            except Exception:
                pass
        else:
            existing.append(line)  # not used
    # do a clean check
    found = False
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            try:
                if json.loads(line).get("task_id") == CASE:
                    found = True
                    break
            except Exception:
                pass
    if not found:
        with open(JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print("APPENDED to", JSONL)
else:
    with open(JSONL, "w", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("CREATED", JSONL)

# verify roundtrip: last line == entry, and test field bytes == disk check.py
with open(JSONL, encoding="utf-8") as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
assert last["task_id"] == CASE, "roundtrip task_id"
assert last["test"] == check_src, "roundtrip test bytes mismatch"
print("roundtrip OK; jsonl_C lines =", len(lines))
