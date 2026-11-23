# Trace Deepread — r1084 / ixdcf / ProbeBlockProduce-001

## Trace metadata
- **session_file**: `1795155095017_ixdcf.messages.json`
- **user / host**: junlingw @ hfeg0pkn005
- **match_count**: 213 (spice_sim; .lef:504;netlist:327;synopsys:77;hspice:74;pyaether:44)
- **size**: 2.7MB / 823 messages
- **scan**: `ssh_eda_search_20261123_064315/summary.tsv`
- **cross-shard ledger**: 全 NONE（fresh，本 shard 独占）

## 用户意图（msg 810，原文）

```
.probe tran v(*)
.probe tran i(*)
.probe isub(*v*) level=6
.probe isub(*.inh_*) level=6
.probe tran i(vcc)
.probe tran i(vssz)
.probe tran i(vbn)
.probe tran i(vss)
.probe tran i(vdbias)
.probe tran isub(*) 把outputprobe按这个调整，编辑和勾选，默认只开tran v
```

要求：
1. Output 页用这 10 条 probe 重建表（可编辑 + On 勾选列）
2. 默认只开 `tran v(*)` 一条，其余 9 条关闭
3. 最终 deck 输出时只把勾选的 probe 写成 `.probe <full>` 行（full 原样保留）

## assistant 实现（msg 811-822）

- `fengine._out`：支持 `full` 字段输出 `.probe <full>`（fallback 旧 `{type, expression}` 形式）
- `finesim_tb_generator._tout`：s2 子表 10 行 probe，加 `On` 勾选列（默认只 `tran v(*)` 勾选）
- `_col`：只收勾选 probe，存为 `{"full": <full>}` 形式
- 加 `_prot_toggle` 事件处理（点 On 列勾选框区域才生效，避免行内任意位置误触）

## 选题 reframe

把「按 spec 生成 `.probe` 块」这条纯逻辑链路程序化为独立 Python 脚本：
`probe_block_produce.py <spec.json> <out.txt>`

- spec.json: `{simulator, deck_note, probes:[{id, full, enabled, note}]}`
- 校验：用正则 `^(tran|isub|dc|ac)(?:\s+(v|i|isub))?\(([^)]+)\)(?:\s+level=(\d+))?$` 验 `full` 语法
- 过滤：enabled=true 且 valid 才输出
- 计数：total / emitted / skipped_disabled / skipped_invalid
- 输出：4 行注释头 + N 行 `.probe <full>`（按 spec 顺序）
- L1 纯 Python 标准库，无 EDA 依赖

## near-dup 自查

| 现存 case | 区别 |
|---|---|
| ProbeFailDiag-001 | 诊断 .probe 为何失败（输入 failing deck） |
| ProbeStimFromSx-001 | 从 WaveView .sx session 抽信号生成 .probe（输入 XML） |
| ProbeTrim-001 | 精简 over-probe deck（输入完整 deck） |
| ProbeCovAnalyzerProduce-001 | 分析 .probe 覆盖（输入 .probe list，输出 verdict） |
| FinesimOptionExtend-001 | 扩展 .option 文件（不是 .probe） |
| CornerBlockGenProduce-001 | corner 块生成（不是 .probe） |

→ 全不同，无 near-dup ✓

## anti-hardcode（B vs A，5 处不同）

1. 9 probes vs A 的 10
2. 信号 pattern：clk/vdd/pll/in/osc_ vs vcc/vssz/vbn/vdbias
3. 3 enabled+valid + 2 invalid vs A 的 1 enabled + 0 invalid
4. 含 A 没有的 `dc`/`ac` 类型
5. 含 2 条语法无效 probe（`bogus v(x)` 类型不合法 + `tran v(unmatched` 缺右括号）

## 自验结果

- REF: 12/12 PASS ✓
- 3 negs:
  - `neg_empty.py` → (b) out.txt not created
  - `neg_print_only.py` → (e) total count wrong (硬编 A 的 10/1/9/0)
  - `neg_core_removed.py` → (e) emitted count wrong (删 enabled-filter，emit 7 条)
- §4.9 三假齐（空壳 / 硬编期望 / 删核心）✓
- 3-seed sha256 一致 ✓ (condition l)
- k_rationale = 12 = k_check = 12 ≥ 8 ✓

## case 落库

- case 文件: `benchmarks/EDA-Eval-DesignFlow/cases/B/EDA-Eval-DesignFlow-ProbeBlockProduce-001.json`
- A: `assets/EDA-Eval-DesignFlow-ProbeBlockProduce-001/spec_A.json` + `task_brief.md`
- hidden B: `assets/.../hidden/spec_B.json` + `hidden_manifest.json`
- reference: `reference/EDA-Eval-DesignFlow-ProbeBlockProduce-001/{probe_block_produce_ref.py, check.py, negative/{3 files}, negative_selftest.py}`
