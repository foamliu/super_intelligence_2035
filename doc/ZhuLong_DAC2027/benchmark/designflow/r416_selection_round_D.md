# R416 选料复核轮（shard D · 2026-11-08 21:30）· 0 case

## 目标
trace_ledger --shard D next → 候选池 mc≥30 D-domain（waveview|netlist|spectrum|analog|schematic）→ cross-ref ledger_D 排除已动过 → peek fresh 候选 → 判 D-domain synthesizable A-grade seed。

## 扫描源
`/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv`（11-05 快照，已 3 天陈旧）。

## 候选池统计
- mc≥30 D-domain 命中：1607 行 / 1118 unique sids
- top 79 unique sids 中 fresh（不在 ledger_D）：1（puv3q，calibre-dominant physical_verify 非 D）
- 中段（rank 121-320）200 行中 fresh：18（多为 e0014566 meta + 少量真实用户）

## Peek 7 fresh 候选（全部 parked，非 D-domain synthesizable seed）

| sid | user | host | mc | domain | peek 判定 | park 原因 |
|---|---|---|---|---|---|---|
| 1793670518248_ap4dl | e0029495 | hfeg0pkn002 | 303 | schematic_netlist | verification of prior-built xval stdcell 3-way cross-validation tool (CDL+HSPICE vs Verilog+VCS vs Liberty, 432 cells/9-step pipeline) | build 发生在更早 session，本 session 仅跑 /tmp/full_verify.py 验证既有 lib；非干净 build seed；assets private /home/e0029495/xval_tool |
| 1791871316059_iih6g | laryu | hfeg0pkn001 | 265 | analog_context | U#0「使用pyAether，先copy一个view为A，然后以可写模式打开，并将A中的instance个数打印出来」 | trivial L1 pyAether API 单步练习；违反 §5 新 case 只做 L2/L3 |
| 1790083095684_oblxr | e0014566 | hfeg0pkn001 | 274 | analog_context | U#0「新建 OA 数据 BCenterCA，改了 common.config 的 lib/cell name，你看我还有什么要改的」 | config-review Q&A（用户已自行修改后求 review）；非 build 请求；e0014566 meta/auto_qx |
| 1790752052118_r7e7z | yzwang | hfeg0pkn001 | 295 | analog_context | U#0 debug Updata_TechDisplay 的 Python SyntaxError（`def read(filePath,*keys,keyName=False)` py2 不支持） | Python2/3 解释器兼容 env debug，非 EDA design-flow |
| 1789976011359_06htj | mike | hfeg0pkn003 | 275 | waveform | U#0 仅一行路径 `/ai_sandbox/dscqa/V0/agentdir/mike/logic_cosim/d6` | 首 turns 无明确 build 目标；巨量（617 user msgs/1210 total）；assets private |
| 1786349419937_ipbrb | e0014566 | hfeg0pkn001 | 450 | schematic_netlist | U#0「read the prompt.md and do the job in it.」 | agent-driven meta（e0014566 auto_qx/eval harness）；真实任务在 prompt.md 不在 chat；非自然用户请求 |
| 1792675302417_puv3q | xinqiaoz | hfeg0pkn002 | 470 | physical_verify | 工具列 610 calibre / 1 netlist | calibre-dominant → physical_verify 错 shard（C），非 D |

## 结论
- **0 fresh D synthesizable A-grade seed**（7 peek 全部非 seed：meta/Q&A/verification/env-debug/trivial-L1/wrong-shard）。
- 与 #404/#405/#409 一致：fresh D A-grade seed 枯竭。
- ledger_D 1342 → 1349（+7 parked，0 case）。
- D.jsonl 231 不变（0 新 case）。

## 真外部阻塞（需运维，与既有 DEBT 同）
1. **全量 rescan summary.tsv**：当前用 11-05 快照（已 3 天陈旧），无 newer summary.tsv；cron 仅 eda_trace_20261108.log 无新 summary.tsv 产物。
2. **放宽 D-domain 关键词**：现行 `waveview|netlist|spectrum|analog|schematic` 误纳大量 calibre-dominant（physical_verify/shard C）session（netlist 仅 keyword 命中）；真 D（spectre/hspice/cosmos/fsdb/tran）未被强过滤。
3. **跨 shard domain 重分配**：spice_sim/waveform 部分回流 D（运维令 10-31 提及）。
4. **资产权限**：ap4dl/06htj 等真实用户 assets 多在私有 /proj、/ai_sandbox、/home/<u>（e0031982 无读权限无 sudo），即便有 seed 亦只能 B-grade synthesized。

## 产出
- ledger_D：+7 claim + +7 parked（ap4dl/iih6g/oblxr/r7e7z/06htj/ipbrb/puv3q）
- 本选料复核记录：designflow/r416_selection_round_D.md
- _tmp：ledger_D_sids.txt（cross-ref 用，可清理）
- eda_flow session：open + close(keep=false)
- 无新 PII / 无改 D.jsonl / 无动 EDA-Flow-Bench assets+reference

**WAITING: 1 等人工（真外部阻塞同 DEBT①②③）**
