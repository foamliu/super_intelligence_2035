#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SignalXrefMap-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os

CID = "EDA-Eval-DesignFlow-SignalXrefMap-001"
BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = os.path.join(BASE, "reference", CID)
ASSET = os.path.join(BASE, "assets", CID)

check_py = open(os.path.join(REF, "check.py"), encoding="utf-8").read()

attachments = [
    {"name": "signals_A.txt", "source": f"benchmarks/EDA-Eval-DesignFlow/assets/{CID}/signals_A.txt", "desc": "可见样本A的信号名清单（cmname_zx），6 个信号，每行一个，# 开头为注释。SUT 用以理解输入格式并离线自测。"},
    {"name": "patterns_A/", "source": f"benchmarks/EDA-Eval-DesignFlow/assets/{CID}/patterns_A", "desc": "可见样本A的 pattern 目录树（cmds_ppr/cmds_mpr/cmds_adjosc 三个子目录，各含 .v pattern 文件）。SUT 递归搜索其中包含信号名的文件。"},
    {"name": "regressions_A/", "source": f"benchmarks/EDA-Eval-DesignFlow/assets/{CID}/regressions_A", "desc": "可见样本A的 Regressions 目录（.inc include 文件 + extra.v + notes.txt）。SUT 在其中找引用 pattern 文件名的 .inc，并直接搜索所有文件中的信号。"},
    {"name": "spec_A.md", "source": f"benchmarks/EDA-Eval-DesignFlow/assets/{CID}/spec_A.md", "desc": "可见样本A的规格书：任务背景、三阶段映射语义（signal→pattern file / pattern file→.inc / signal→regression file 直接）、匹配规则（大小写敏感、整词 word-boundary、注释出现也算文本命中）、report.json schema、A 的预期结果。"},
]

prompt = """[design_flow] 数字验证回归树 信号名 → pattern 文件 → .inc include 交叉引用映射器 (signal cross-reference mapper)

## 背景

eason1z 是一名数字验证工程师，负责 DDR5 验证回归平台。平台目录结构形如：

    /rundata/drgqx/V0/simdir/verilog/zhaoxin/verilog.ddr5.drgqx.1107/
    ├── cmname_zx                 # 一份信号名清单（每行一个信号名，# 注释）
    ├── patterns/
    │   └── cmds_testmode/        # 多个子目录，每个子目录下是若干 .v pattern 文件
    │       ├── cmds_ppr/*.v
    │       ├── cmds_mpr/*.v
    │       └── ...
    └── Regressions/              # 回归脚本目录，含若干 .inc include 文件 + 其他文件

她手上有一个信号名清单 `cmname_zx`，希望有一个工具帮她理清这些信号名、pattern 文件、.inc include 文件三者的对应关系。

eason1z 的原话（trace 摘要）：

> 给你一个文件 .../cmname_zx，里面有很多信号名，你帮我在路径 .../patterns/cmds_testmode/ 下的文件和文件夹中的文件里去找包含这些信号名的文件，然后去路径 .../Regressions/ 下以 .inc 结尾的文件中去找到有包含这些文件名的文件，并记录信号名和文件名的对应关系给我；同时在路径 .../Regressions 下的文件里去找包含这些信号的文件，并记录信号名和文件名的对应关系给我。

## 你要交付什么

写一个**纯 Python stdlib** 命令行工具 `signal_xref_mapper.py`，完成三阶段映射：

1. **信号 → pattern 文件**：递归遍历 patterns 目录下所有文件，找出每个信号出现在哪些文件里（按文件相对路径记录）。
2. **pattern 文件 → .inc include**：对每个含信号的 pattern 文件，在 Regressions 目录下的 **.inc 文件**（仅 .inc）中找出引用了该 pattern 文件名（basename）的 .inc 文件，于是把信号关联到 (pattern 文件, .inc 文件) 对。
3. **信号 → Regressions 文件直接命中**：在 Regressions 目录下的**所有文件**（不限扩展名）里直接搜索信号名，记录命中的文件。

输出一份 `report.json`，至少包含：
- `signals_total`、`signals_with_pattern_match`、`signals_with_inc_ref`、`signals_with_reg_direct`、`signals_unmatched`（在三个阶段都没命中的信号）
- `by_signal`：每个信号 → `{pattern_files:[], inc_refs:[{pattern,inc}], reg_direct:[]}`
- `by_inc`：每个 .inc 文件 → `{pattern_basename: [signals]}` 反向索引
- `by_reg`：每个 regression 文件 → `[signals]` 反向索引

## 匹配规则（必须遵守）

- 信号名匹配**大小写敏感**（`DqOdt` ≠ `dqodt`）。
- 信号名按**整词（word-boundary）**匹配：信号 `CA` 不得命中只含 `CA0` 或 `CASE_mode` 的文件；信号 `RDQ` 不得命中只含 `RDQS` 的文件。`$`、字母、数字、下划线都算单词字符。
- pattern 文件里**注释中的出现也算命中**（做的是文本搜索，与真实 agent 行为一致）。
- 第 2 阶段只看 `.inc` 文件；Regressions 里的 `.v`/`.txt` 等文件即便提到了 pattern 文件名，也**不算** inc 引用。
- 第 3 阶段搜索 Regressions 下**所有文件**（含 .inc/.v/.txt 等），不限扩展名。
- `.inc` 文件对 pattern 的引用按 pattern 文件 basename（如 `FsPgm_FusePrac.v`）出现即算。

## 命令行接口

```
python signal_xref_mapper.py --signals <信号清单> --patterns-dir <patterns目录> \
    --regressions-dir <Regressions目录> --out <report.json>
```

也可支持 `--json` 直接打印到 stdout。输出 JSON 必须是确定性的（键排序、列表排序），多次运行结果一致。

## 自测

可见样本 A（`signals_A.txt` + `patterns_A/` + `regressions_A/` + `spec_A.md`）给你用来理解需求和离线自测；**判分用的隐藏输入 B** 与 A 信号名 / pattern 文件 / .inc 文件**零命名重叠**，且 B 中故意埋了四类陷阱（整词边界、大小写、非-.inc 文件引用 pattern basename、reg_direct 须覆盖非-.inc 文件）。不要把答案写死成 A 的值，工具必须对任意输入都正确。"""

test_rationale = (
    "16 条断言：① submit.zip 可解压且含 signal_xref_mapper.py 且 py_compile 通过且无 check/reference/negative/.jsonl 泄漏 "
    "② SUT 仅用 stdlib（无第三方 import） "
    "③ SUT 在 B 上 CLI exit 0 且产出可解析的 --out JSON "
    "④ report.signals_total == 7（B 信号数） "
    "⑤ report.signals_with_pattern_match == 5 "
    "⑥ report.signals_with_inc_ref == 5 "
    "⑦ report.signals_with_reg_direct == 3 "
    "⑧ report.signals_unmatched == [ts_BackBistMultibnk, ts_ReadSigSkipFlagEn] "
    "⑨ by_signal[cmd_mwr_done].pattern_files == [cmds_wr/TM_Mwr.v, cmds_wr/TM_Mwr_long.v] "
    "⑩ by_signal[RDQ].pattern_files == [cmds_zq/TM_ZqCal.v]（整词 word-boundary：击败 TM_Misc.v 的 RDQS 子串诱饵） "
    "⑪ by_signal[VrefCA].pattern_files == [cmds_wr/TM_Mwr.v]（大小写敏感：击败 TM_Misc.v 的 vrefca 小写诱饵） "
    "⑫ by_signal[cmd_mwr_done].inc_refs 含 (cmds_wr/TM_Mwr.v, tm_wr.inc) 与 (cmds_wr/TM_Mwr_long.v, tm_wr.inc) "
    "⑬ inc_refs 中每个 inc 文件均以 .inc 结尾（log.txt 引用了 TM_Mwr.v basename 但因非 .inc 不计为 inc_ref） "
    "⑭ reg_direct 含非-.inc 文件：zq_cal_start→log.txt、cmd_mwr_done→extra.v（击败「reg_direct 只搜 .inc」bug） "
    "⑮ 跨输入守卫：A 专属信号（fc_MR70AlertnVeriSupt 等）不出现在 B 的 by_signal 且 cmd_mwr_done 出现（击败 hardcoded_A） "
    "⑯ 三次重跑 out.json 的 sha256 一致（确定性）"
)

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "test": check_py,
    "expected_artifacts": ["signal_xref_mapper.py", "submit.zip"],
    "budget": {"max_turns": 30, "timeout_sec": 2400},
    "metadata": {
        "domain": "verification",
        "level": "L1-B",
        "difficulty": "medium",
        "track": "design_flow",
        "task_name": "signal-to-pattern-file-to-inc cross-reference mapper for a digital verification regression tree",
        "scenario": "B档合成 (deliverable=读私有 /rundata/drgqx/ + 写 /home/eason1z/signal_mapping_complete.txt → .75 SUT 沙盒 私有路径 Permission denied + 私有 pattern/.inc 不进沙盒 INFEASIBLE → 纯 Python stdlib CLI 自包含 synthetic 回归树复刻；A 可见 / B 隐藏 命名零重叠 + 四类陷阱)",
        "trace_source": {
            "user": "eason1z",
            "host": "hfeg0plg100",
            "ip": "10.129.8.232",
            "session_file": "1794021023245_u54d9.messages.json",
            "match_count": 108,
            "scan": "ssh_eda_search_20261113_131349",
            "real_task_summary": "U#1-3 核心 produce-task(同一指令重发3次): 给信号清单 cmname_zx，在 patterns/cmds_testmode/ 下找含这些信号名的文件，再去 Regressions/ 下 .inc 文件中找引用这些文件名的文件，并记录信号名↔文件名对应关系；同时在 Regressions/ 下所有文件里直接搜信号名。U#4 续: 在 patterns/ 所有子目录搜未匹配信号。agent(205msgs) list_allowed_files+read_files+run_approved_command(python-runner) 写 search_signals.py(三阶段: signal→pattern file / pattern file→.inc / signal→regression file 直接)，产 /home/eason1z/signal_mapping_complete.txt(~2500行, 56信号/50 pattern匹配/11 .inc引用/5 reg直接/6 未匹配 ts_*)。deliverable=读私有 /rundata/drgqx/ + 写私有 /home/eason1z/ → .75 INFEASIBLE → B档合成。"
        },
        "test_rationale": test_rationale,
    },
}

out = os.path.join(BASE, "EDA-Eval-DesignFlow_A.jsonl")
with open(out, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", CID, "to", out)
print("A.jsonl lines now:", sum(1 for _ in open(out)))
