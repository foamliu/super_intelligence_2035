#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build & append the phantom case HspiceAlterTrnPredictor-001 to B.jsonl.
r993 §4.9 self-check found this r982 case was never written to B.jsonl
(same phantom pattern as r986/r988/r991). ledger already marks nhj3c→case.
This script only does the missing jsonl append.
"""
import json, os, sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
CASE = "EDA-Eval-DesignFlow-HspiceAlterTrnPredictor-001"
ASSETS = f"{BENCH}/benchmarks/EDA-Eval-DesignFlow/assets/{CASE}"
REF = f"{BENCH}/benchmarks/EDA-Eval-DesignFlow/reference/{CASE}"
BJSONL = f"{BENCH}/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_B.jsonl"

# 1. task_brief.md
task_brief = """# HspiceAlterTrnPredictor-001 — Task Brief

## Background (trace-faithful)
User `hairuizh` on `hfeahpc502` (session `1794893451446_nhj3c`, spice_sim domain,
match_count=9, hspice-dominant) ran HSPICE simulations with `.ALTER` blocks and asked:

> hspice仿真，如何让输出的波形文件.trn名字中附带有alter的信息，方便识别

(HSPICE simulation: how to make the output waveform `.trn` filename carry alter
information, for easy identification.)

Real HSPICE behavior: a `.TRAN` deck with N `.ALTER` blocks produces waveform files
`<root>.tr0` (main), `<root>.tr1`, ..., `<root>.trN` (one per alter, **sequence-based**,
NOT label-based). `<root>` is the `-o` output-root if given, else the design name. The
`.ALTER <label>` only appears in the `.lis` text report, not the `.tr<N>` filename.
`.ALTER` blocks must not contain `.PRINT/.PLOT/.PROBE/.GRAPH/.MEASURE`.

## Reframe (analysis-Q&A → produce)
The user's real intent is "a mapping from filename ↔ alter case so I can identify them."
Reframe: produce a parameterized Python tool `hspice_alter_predictor.py` that parses any
HSPICE deck + config and emits a JSON report mapping each segment (main + alters) to its
predicted `.tr<N>` filename, recording labels and flagging illegal I/O commands inside
`.ALTER`. This gives the user the identification mapping they wanted.

## CLI contract
```
python3 hspice_alter_predictor.py --deck <deck.sp> --config <config.json> [--output-root <name>] --out <predict.json>
```

## Visible A (given to SUT)
- `deck_A.sp` — DDR2 lvlshft deck, `.TRAN 1n 100n`, 3 `.ALTER` (2 named + 1 unnamed), no `-o`
- `config_A.json` — `{design_root: lvlshft_ddr2, cli_output_root: null}`
- `AI_USAGE.md` — full tool spec

## Hidden B (check-only, not in SUT sandbox)
- `deck_B.sp` — vref_buf_opamp deck, 4 `.ALTER` (3 named incl. one with illegal `.PRINT` + 1 unnamed), `-o sim_vref_corner`
- `config_B.json` — `{design_root: vref_buf_opamp, cli_output_root: sim_vref_corner}`
- Anti-hardcode-A: design_root / alter count(4 vs 3) / labels / `-o` override(B has, A doesn't) / B has illegal `.PRINT` segment (A doesn't) — all differ.

## Deliverable
Package `hspice_alter_predictor.py` into `outputs/submit.zip`.

## Difficulty
L1 — offline Python text parsing, no EDA binary, no sandbox run.
"""
with open(f"{ASSETS}/task_brief.md", "w") as f:
    f.write(task_brief)
print("wrote task_brief.md")

# 2. read check.py as test
with open(f"{REF}/check.py") as f:
    check_py = f.read()

# 3. prompt (trace-faithful, hairuizh real scenario)
prompt = """我在做 HSPICE 仿真，deck 里用了多个 `.ALTER` 块做不同 corner。真实工作场景（来自真实 trace，用户 hairuizh @ hfeahpc502 session nhj3c，spice_sim 域）——我之前问的是：

> hspice仿真，如何让输出的波形文件.trn名字中附带有alter的信息，方便识别

也就是每个 `.ALTER` 跑完都会输出一个 `.trn` 波形文件，我想一眼就能把文件名和对应的 alter case 对上号，方便后续识别和处理。

现在请你帮我做一个**参数化 Python 工具 `hspice_alter_predictor.py`**，给定任意一张 HSPICE deck 和它的运行配置，**预测真实 HSPICE 会给每个 segment（主仿真 + 各 `.ALTER`）生成的波形文件名**，并输出一个 JSON 报告，让我拿这个报告当 `filename ↔ alter case` 的映射来用。

CLI 契约（必须精确匹配）：
```
python3 hspice_alter_predictor.py --deck <deck.sp> --config <config.json> [--output-root <name>] --out <predict.json>
```

`--config` 是一个 JSON，字段：
- `design_root` (string)：概念上的 design 名（通常是 deck basename）
- `cli_output_root` (string 或 null)：用户在 hspice 命令行用 `-o <name>` 传的值；null 表示没用 `-o`

`<root>` 解析优先级（决定 `<root>.tr<N>` 里的 `<root>`）：`--output-root` CLI 参数 > `config.cli_output_root`（非 null）> `config.design_root`。

输出 JSON schema：
```json
{
  "design_root": "<从 config 复制>",
  "output_root": "<实际用于文件名的 root，按上面优先级解析>",
  "analysis_type": "<TRAN|DC|AC|IC|...>",
  "segments": [
    {"index": 0, "source": "main", "label": null, "trn_filename": "<root>.tr0", "warnings": []},
    {"index": 1, "source": "alter", "label": "<alter label 或 null>", "trn_filename": "<root>.tr1", "warnings": ["..."]}
  ],
  "summary": {"total_segments": <int>, "alters_with_warnings": <int>}
}
```

必须实现的**真实 HSPICE 命名规则**（ground truth，你的工具必须匹配）：
1. `.TRAN` 产生 `<root>.tr0`（主仿真），然后每个 `.ALTER` 块按源码顺序产生 `<root>.tr1`、`<root>.tr2`、… 序号 N 主仿真为 0，之后每个 `.ALTER` 递增 1。
2. `<root>` 按上面的优先级解析。
3. **`.ALTER <label>` 的 label 不进文件名**——真实 HSPICE 只用序号（label 只在 `.lis` 文本报告里用于识别）。你的工具要把 label 记到 `label` 字段方便我 mapping，但 `trn_filename` 只用序号。
4. `.ALTER` 块内**禁止**出现 `.PRINT/.PLOT/.PROBE/.GRAPH/.MEASURE`；如果某个 `.ALTER` 块里有这些命令，你的工具必须在该 segment 的 `warnings` 里记一条警告（警告文本要提到违规命令名，例如 `"PRINT not allowed inside .ALTER"`）。
5. 主块的 `.OPTION POST` 控制波形输出开关；你的工具无论 POST 设成什么，都按规则预测文件名（不要自作主张跳过）。

附件里有一张可见的 A deck（`deck_A.sp`，DDR2 lvlshft，3 个 `.ALTER`，没用 `-o`）和它的 config（`config_A.json`），以及完整的工具规格 `AI_USAGE.md`。最终把 `hspice_alter_predictor.py` 打包进 `outputs/submit.zip`。判分会在一张**隐藏的 B deck**（不同 design、不同 alter 数量、不同 label、带 `-o` override、且有一个 `.ALTER` 块违规含 `.PRINT`）上跑你的工具，断言预测的文件名、警告和结构都匹配真实 HSPICE 行为。**不要硬编码 A 的任何值**。"""

# 4. metadata
metadata = {
    "domain": "spice_sim",
    "track": "A",
    "layer": "L1",
    "trace_source": {
        "user": "hairuizh",
        "host": "hfeahpc502",
        "ip": "10.129.33.25",
        "session_file": "1794893451446_nhj3c.messages.json",
        "match_count": 9,
        "scan_snapshot": "ssh_eda_search_20261120/summary_1120_reconstructed.tsv (B fresh list; nhj3c r982 取证合成, r982 MEMORY 误报已落库实未入 B.jsonl, 本轮 r993 §4.9 self-check 发现 phantom 补落库)",
        "real_task_summary": "用户 hairuizh @ hfeahpc502 (session nhj3c, mc=9, spice_sim/HSPICE 仿真) 做 HSPICE 多 .ALTER corner 仿真, 用户原话「hspice仿真，如何让输出的波形文件.trn名字中附带有alter的信息，方便识别」(analysis-Q&A→produce reframe). reframe: produce 参数化 hspice_alter_predictor.py(--deck/--config/--out) 预测真实 HSPICE per-alter 波形文件名(sequence-based <root>.tr<N>), 输出 JSON mapping(filename↔alter case)+warnings(违规 I/O 命令). asset A: DDR2 lvlshft/3 .ALTER/无-o; hidden B: vref_buf_opamp/4 .ALTER/-o sim_vref_corner/1 违规 .PRINT→anti-hardcode-A."
    },
    "test_rationale": "13 条断言：①(a) submit.zip 有效且解压后含 hspice_alter_predictor.py ②(b) 脚本 py_compile 通过 ③(c) 在隐藏 B deck 上以指定 CLI 运行 exit 0 且产出合法 JSON 对象 ④(d) JSON schema 含 design_root/output_root/analysis_type/segments/summary 五个必需键 ⑤(e) segments 数量正确（B=5：主 1 + 4 alter），不是 A 的 4 ⑥(f) segments[0].trn_filename == 'sim_vref_corner.tr0'（B 的 -o 自定义根 + 主 sim） ⑦(g) segments[1..4].trn_filename 依次为 'sim_vref_corner.tr1'..'sim_vref_corner.tr4'（sequence-based NOT label-based，核心齿，反 agent 文字里 design.<label>.trn 幻觉） ⑧(h) 至少 1 个 segment 的 warnings 非空且含 'PRINT'（B 的违规 .PRINT 段被检出） ⑨(i) 命名 alter 段的 label 字段保留原 label 文本（即使 label 不进文件名也要记录供 mapping） ⑩(j) analysis_type == 'TRAN'（B deck 主分析是 .TRAN） ⑪(k) -o override：所有 trn_filename 都以 'sim_vref_corner' 开头，不以 B 的 design_root 'vref_buf_opamp' 开头（B 自定义前缀生效） ⑫(l) anti-hardcode-A：predict.json 内不出现 A 的 design_root 'lvlshft_ddr2'、A 的 alter label 'case_vdd_1p2/case_vdd_0p8'、A 的 alter 数 3 ⑬(m) 3-seed 确定性：subprocess 跑 3 次随机化输入顺序 → predict.json 完全相同（禁时间戳/random）",
    "k_rationale": 13,
    "k_check": 13,
    "gold_standard": "assistant 交付: hspice_alter_predictor.py 用 argparse 接 deck/config/output-root/out; 解析 deck 识别主分析类型(.TRAN/.DC/.AC/.IC)、.ALTER 块边界(含可选 label)、.ALTER 块内违规 I/O 命令(.PRINT/.PLOT/.PROBE/.GRAPH/.MEASURE); <root> 按优先级解析(--output-root > config.cli_output_root > config.design_root); 为每个 segment(主+alters)生成 sequence-based trn_filename <root>.tr<N>(N=0 主, 1,2,3… 各 alter, label 不进文件名只记 label 字段); 违规命令记 warnings; 输出 JSON 含 design_root/output_root/analysis_type/segments[]/summary. 参考 hspice_alter_predictor_ref.py.",
    "asset_fidelity": "format_faithful_hspice_deck",
    "reframe_note": "harness-for-teeth reframe: trace 原意图=analysis-Q&A(用户问如何让 .trn 文件名带 alter 信息以便识别), 判分有牙需参数化通用 CLI(任意 deck/design/alter 数/label/-o), 故 reframe 成 produce 参数化 hspice_alter_predictor.py; 核心齿=sequence-based 命名(反 agent 文字里 label-in-filename 幻觉); hidden B 异 design(vref_buf_opamp)+异 alter 数(4 vs 3)+异 label+-o override+1 违规 .PRINT 段 验通用性与反硬编码 A."
}

entry = {
    "id": CASE,
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        f"{ASSETS}/task_brief.md",
        f"{ASSETS}/visible/AI_USAGE.md",
        f"{ASSETS}/visible/config_A.json",
        f"{ASSETS}/visible/deck_A.sp"
    ],
    "task_brief": task_brief,
    "test": check_py,
    "metadata": metadata
}

# sanity: ensure not already present
with open(BJSONL) as f:
    for i, line in enumerate(f, 1):
        line=line.strip()
        if not line: continue
        if json.loads(line).get("task_id") == CASE:
            print(f"ALREADY PRESENT at line {i}, abort"); sys.exit(1)

with open(BJSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# recount
n=0
with open(BJSONL) as f:
    for line in f:
        if line.strip(): n+=1
print(f"appended. B.jsonl now {n} lines")
