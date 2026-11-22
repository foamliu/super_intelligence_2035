# r1003 deepread — 1r7vq (PT cell extraction)

- **sid**: `1794808598045_1r7vq.messages.json`
- **user/host**: zhukais @ hfeg0plg54
- **match_count**: 46 (mc≥5 pool entry)
- **domain**: pnr_signoff (shard A)
- **keywords**: synopsys:115 / dc_shell:57 / verilog:39 / innovus:20 / rtl:19
- **case_id**: `EDA-Eval-DesignFlow-PtCellExtractProduce-001`
- **round**: r1003 (2026-11-22)

## Trace summary

Session 含多个子任务：PDF→text（Innovus TCR/UG）、PrimeTime timing 报告 cell
提取、DC 综合、技能查询。本 case 取 cell 提取子任务。

用户原话（逐字）：
> 「inst_rx_top/rdata_reg_14_/D (SDFCNQOPTQD6BWP40P140ULVT)
> 只需要抓取（）内的cell,并进行去重，过滤」

session 概述补充：
> *extract all unique cells from a PrimeTime timing report, deduplicated and
> alphabetically sorted*

trace 中 agent 的 gold 脚本 `extract_cells.py`：
- regex `^\s*(\S+)/([A-Z][A-Z0-9_]*)\s+\(([A-Z][A-Z0-9]\S*)\)`，group(3) = cell 类型
- skip 前缀：`--`/`clock`/`Point`/`Startpoint:`/`Endpoint:`/`Report :`/`Design :`/
  `Warning:`/`*****`/`Version:`/`Date   :` 等 + 含 `(net)` 行
- `set()` 去重 + `sorted(key=str.upper)` 字母序
- 对 75375 行报告匹配 27712 个 timing point，提取 213 个唯一 cell

## Case reframe (faithful produce-task)

把 cell 提取需求泛化为通用 `extract_pt_cells.py <report> <output>` produce-task：

- **A (visible)**: `dram_tester_chip` setup timing 报告，45 cells，附在 `assets/`
- **B (hidden)**: `ddr5_ctrl_chip` setup timing 报告，41 cells，所有 concrete 值
  异于 A（B 特有锚点：EDFD1/AN5D2/XOR3D2/LATQD1；A-only 反硬编码：
  SDFCNQOPTQD6/INVD8/AO22D16/DFKQD1/PRECGD1/XNOR2D2/CLKBUFD8）

## check.py — 15 独立断言

| # | 断言 | 反制 |
|---|---|---|
| ① | submit.zip 含 extract*.py | 空壳 zip |
| ② | py_compile 通过 | 语法坏 |
| ③ | B 运行 exit0 + 非空输出 | 不运行 |
| ④ | stdout 含 Lines:/Matched:/Unique cells: | print-only |
| ⑤ | B cell 数=41（≠A 的 45） | 硬编码 A |
| ⑥ | 字母序排序（大小写不敏感） | 乱序 |
| ⑦ | 无重复（去重） | 不去重 |
| ⑧ | 41 期望 cell 全在输出 | 漏 cell |
| ⑨ | A-only cell 不泄漏进 B | 硬编码 A |
| ⑩ | B-specific 锚点 cell 在输出 | 硬编码 A |
| ⑪ | 输出无 "net" | 不过滤 (net) |
| ⑫ | 行号 1-based 连续 | 编号坏 |
| ⑬ | 3 次运行 md5 一致 | 非确定性 |
| ⑭ | 含 import+def 且 >200B | 空壳 |
| ⑮ | stdout Lines 计数>0 | print-only |

k_check = k_rationale = 15 ≥ 8 ✓

## §4.9 three-fake gate (negative_selftest + jsonl-E2E)

| fake | 期望 | 实际 |
|---|---|---|
| neg_empty.py（空壳） | FAIL | FAIL ✓ (output empty) |
| neg_print_only.py（硬编码 A 的 45 cell） | FAIL | FAIL ✓ (count 45≠41) |
| neg_core_deleted.py（提取逻辑删除） | FAIL | FAIL ✓ (output empty) |

reference solution `extract_pt_cells.py` PASS（in-place + jsonl-E2E 双验证）✓

## Domain verdict

keywords Synopsys:115 / dc_shell:57 / Innovus:20 → Synopsys PT + Innovus PnR
dominant → A-domain `pnr_signoff`（非 C；虽有少量 schematic/virtuoso 但非主轴）。
