#!/usr/bin/env python3
"""Build the jsonl entry for EDA-Eval-DesignFlow-ResultMapEntryRemover-001 and
append to EDA-Eval-DesignFlow_A.jsonl."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CASE_ID = "EDA-Eval-DesignFlow-ResultMapEntryRemover-001"
ASSET_DIR = "assets/EDA-Eval-DesignFlow-ResultMapEntryRemover-001"
# HERE = benchmarks/EDA-Eval-DesignFlow/reference/<CASE>
check_py = open(os.path.join(HERE, "check.py"), "r", encoding="utf-8").read()

prompt = """你是 e0039602 这位数字库转换工程师的助手。他在做 Verilog netlist → SV 转换流程（verilog_lib_trans_v2 项目），生成的 result_map 是一份模块目录文件，每个模块条目以一行 header 开头：

```
# ---- module: <模块名> (行 <X>-<Y>) ----
```

后面跟 `## 完整原文` 标记行、模块的 Verilog 源码（`endmodule` / `` `endcelldefine``），再以空行与下一条目分隔。目录里有的条目是**过期/错误的转换**，需要干净地整条删掉，不能影响其余条目。

原话需求：

- 「请你阅读 result_map 这个文件，其中有一个类别的错误，AF_latqn2_CmFsUnit 这种类型的需要：[正确 module 模板，含 clk/clk0/clk1 时钟安全门控、trireg (medium) #(1,1,200)、invhiz_base + passg_base + inv_base 驱动、fgc_pwrstate_monitor、完整 specify 块]」

result_map 里那条 `AF_latqn2_CmFsUnit` 是错的（用了 `vlgTcap #(.tdecay(300))`、`trireg (medium) #(1,1,100)`、没有时钟安全门控），与正确模板不符，需要把这一整条目录条目删掉。注意 `CmFsUnit` 这个串在**别的模块的 body 里**也会出现（wire 名/注释/实例名），但那些条目的 **header 名字**不是 `AF_latqn2_CmFsUnit`，**不能**因为 body 里出现子串就误删。

请编写 `remove_result_map_entry.py`（Python3，仅用标准库），从 result_map 目录里按 **header 行的模块名**精确删除一条命名模块条目。

## 用法
```
python3 remove_result_map_entry.py --input <result_map> --module <目标模块名> --output <修改后文件> --report <report.json>
```

## 行为要求
1. 按 **header 行**的模块名（`# ---- module: <NAME> (行 X-Y) ----` 中 `<NAME>` 与 `--module` 全串相等）定位目标。目标名可能作为**子串**出现在其他模块的 body 里，那些条目**不能**被删——只删 header 名字命中的条目。
2. 删除整块：从目标 header 行到下一条 header 行的前一行（最后一条目则到 EOF）。
3. 边界：删除后相邻条目之间恰好保留一个空行；不出现 ≥2 连续空行；不把两个 header 行粘到相邻；删最后一条目时不留尾随空行。
4. 若多条 header 命中 `--module`，全部删除并在 report 里报 `removed_count`。
5. **找不到**目标时：退出非 0，`--output` 与输入一致（或不写），report 里 `target_found: false`、`removed_count: 0`。

## report.json 字段
```json
{
  "input_file": "<--input>",
  "target_module": "<--module>",
  "before_count": <输入条目数>,
  "after_count": <输出条目数>,
  "removed_count": <删除数>,
  "removed_modules": ["<name>", ...],
  "target_found": <bool>
}
```

## 交付
把 `remove_result_map_entry.py` 打包成 `outputs/submit.zip`（zip 内即该 .py 文件）。可见参考样例 `result_map_A.txt`（8 条目，目标 `AF_latqn2_CmFsUnit` 在中部，body 含 `vlgTcap #(.tdecay(300))`/`trireg #(1,1,100)`）与 `spec.md` 在资产目录。判分会用一份**结构不同的隐藏 result_map B** 跑你的脚本并核验输出与 report。纯标准库、确定性（同输入多次运行字节一致）。"""

test_rationale = (
    "15 条断言："
    "① submit.zip 解出 remove_result_map_entry.py 且无多余文件 "
    "② 脚本 py_compile 通过 "
    "③ 对隐藏 B(--module B_Module_Delta)退出码 0 "
    "④ 输出文件存在且非空 "
    "⑤ report.json 可解析 "
    "⑥ B 目标头 `# ---- module: B_Module_Delta` 在输出中 0 次(独立 line-scan oracle, 非正则) "
    "⑦ B 目标错误签名 `keeperTcap #(.tdecay(500))` 在输出中 0 次 "
    "⑧ 输出 header 行数 == 8(before=9, after=8, 独立 startswith oracle) "
    "⑨ 8 个非目标模块(Alpha/Beta/Gamma/Epsilon/Zeta/Eta/Theta/Iota)header 全保留 "
    "⑩ 子串陷阱模块 Epsilon 完好(其 body `wire B_Module_Delta;` 仍在, 击败 substring-remover) "
    "⑪ 边界干净(无 ≥2 连续空行 + 无尾随空行) "
    "⑫ report 字段正确(before=9/after=8/removed=1/target_found=True/removed_modules=[B_Module_Delta]) "
    "⑬ 跨输入守卫(输出 0 个 A 专属串 AF_latqn2_CmFsUnit / vlgTcap #(.tdecay(300)), 击败 hardcoded_A) "
    "⑭ not-found 处理(--module 不存在时退出非 0 + target_found=False + removed_count=0) "
    "⑮ 确定性(3 次运行输出字节一致)"
)

case = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "%s/result_map_A.txt" % ASSET_DIR,
        "%s/spec.md" % ASSET_DIR,
    ],
    "test": check_py,
    "metadata": {
        "domain": "digital",
        "difficulty": "L1",
        "track": "B",
        "trace_source": {
            "user": "e0039602",
            "host": "hfeg0pkn002",
            "session_file": "1793927996511_kdjt3.messages.json",
            "match_count": 55,
            "real_task_summary": (
                "verilog_lib_trans_v2 数字库转换 session：用户读 result_map 目录文件，"
                "指出 AF_latqn2_CmFsUnit 这一类的错误转换需要按正确 module 模板"
                "(clk/clk0/clk1 时钟安全 + trireg #(1,1,200) + invhiz_base/passg_base/inv_base) 处理，"
                "未给根因。agent 用 run_approved_command(python-runner) 写 6 个临时分析脚本，"
                "定位 279 模块中 1 条 AF_latqn2_CmFsUnit 错误条目(行 1192-1413, vlgTcap #(.tdecay(300)) / "
                "trireg #(1,1,100) / 无 clk 门控)，按 header 名整块删除(非 body 子串匹配, CmFsUnit body 4 occ 仅 1 模块命中)，"
                "验证 279→278 / 0 残留 / 边界干净，清理临时脚本。deliverable=修改后的私有 result_map(26K 行) "
                "→ A-faithful INFEASIBLE → B档合成可复用 catalog-entry-remover 工具。"
            ),
        },
        "test_rationale": test_rationale,
    },
}

jsonl_path = os.path.join(HERE, "..", "..", "EDA-Eval-DesignFlow_A.jsonl")

# verify k_check == 15 (count _cond labels in check.py)
import re
conds = sorted(set(re.findall(r'_cond\("([a-z][0-9]?)"', check_py)))
assert len(conds) == 15, "k_check=%d != 15: %s" % (len(conds), conds)
# verify rationale ①-⑮ count == 15
circled = test_rationale.count("①") + sum(1 for i in range(2, 16) if chr(0x2460 + i - 1) in test_rationale)
# simpler: count the circled markers actually present
import unicodedata
n_marks = sum(1 for ch in test_rationale if 0x2460 <= ord(ch) <= 0x2460 + 15)
assert n_marks == 15, "rationale circled marks=%d != 15" % n_marks
print("GATE: k_rationale=k_check=15 >= 8 PASS")
print("k_check conditions:", conds)

with open(jsonl_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended %s to %s" % (CASE_ID, jsonl_path))
