# Deepread: vzhk2 — REDBIST broadcast error-address count Q&A

**session**: 1794574783120_vzhk2 | **user**: thomas1w | **host**: hfeg0pkn003 (10.129.2.12) | **mc**: 72 | **domain**: schematic_netlist | **msgs**: 70 | **size**: 49MB netlist (1,042,198 lines)

## 用户真实意图（verbatim）

- **U#0**: 「/proj/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.1029/netlist/V0_WOWTOP_2026Oct29.172927/netlist 这是网表内容，redbist的时候，我测试coltest3，他会产生错误的地址，如果扫描到048C的时候，这四个bank都有错，是会产生几个错误地址」
- **U#66** (澄清): 「braocast是对048c这四个bank同时同时读的，四个bank的section错误地址不一样，那么，产生的错误地址是怎么样的」

用户在做 LPDDR5 DRAM 的 REDBIST（修复/冗余分析 BIST）调试。他想搞清楚：coltest3 扫到列地址 048C、且 broadcast 同时读 4 个 bank、4 个 bank 错在不同的 section 时，会产生几个错误地址。这是 **netlist-grounded mechanism-explain Q&A**（读门级网表理解 REDBIST 错误地址捕获机制）。

## 资产可达性

原 netlist 在 `/rundata/ddgoa/...` 跨用户 **Permission denied**（e0031982 ssh 10.129.2.12 验证）。但 trace 的 read_files tool_results 含**真实网表片段**（RedBistCounter / RedBistBACnt / RedBistRACnt / RedBistRdCACnt / RedLatBistPat / RedBistAddrGen / RedLatBistTop / SerialOutRedFlag / mBistPat 的真实 module 头与端口、关键内部信号）。按 **synth_deck 模式**（r768/r781/r782/r789）从 trace 重建保结构 deck（保留真实 module 名 + 端口 + 关键计数器/比较器），资产可达性 = trace 重建。

## 金标准（assistant msg#69 最终答案，用户接受）

**结论：产生 4 个错误地址**（4 个不同的错误地址）。

机制（网表依据）：
1. **broadcast** 一次同时读 4 个 bank，比较针对每个 bank 各自数据独立做（`CheckErrorMacth` 逐读比对）。
2. 错误按 **(bank, section)** 分别置位记录：`RedBistRACnt` 走 `Cnt[7:0]` 的 section（列段）计数器 + `ColSeg0Sel` 段选择；不是把所有 bank 并成一个全局"坏列"。
3. 错误地址组成 = `{ bank(BA[1:0]) + section + 048C }`。
4. 4 个 bank 的 section **不一样** → 4 个不同错误地址，串行读出（`SerialOutRedFlag` / `fnReadSigSerialOutRedColEn`）抓出 4 条。列冗余按 (bank, section) 分配 spare → 占 4 根列 spare。
5. **只有 4 个 bank 错在同一个 section**（错误地址完全相同）时才归并成 **1 个**。

### 关键网表结构证据（真实，从 trace read_files 提取）

| module | 行号 | 关键端口/信号 | 含义 |
|---|---|---|---|
| `RedBistBACnt` | 424530 | `output [1:0] BA`、`BaCmCntOver`、`input [1:0] BABegin/BAEnd`、`BACntCK` | **2-bit bank 计数器 → 4 个 bank** |
| `RedBistRdCACnt` | 425363 | `output [5:0] CA`、`CACntOver`、`input CACntClk`、`[8:6] RedBistData` | 列地址计数器（6-bit → 64 列） |
| `RedBistRACnt` | 424663 | `output [1:0] ColSeg0Sel`、`output [15:0] RA`、`input SectionBeginSet/SecGBeginSet/SecGEndSet`、`RedRdRACntClk` | 行地址 + **section（列段）选择** |
| `RedBistCounter` | 424226 | `output CheckErrorMacth`、`output [7:6] Cnt_Out`、`input [7:0] BcRABegin/BcRAEnd`、`BcRACntClk`；内部 `wire [7:0] D/E`（`xor2x1 Cnt^Begin/End`）、`BcRACntMatch`、`Cnt[8:0]` | **section 计数器 + 逐读错误比对**（D=Cnt^Begin, E=Cnt^End） |
| `RedBistAddrGen` | 425506 | `BA, BaCmCntOver, CheckErrorMacth, Cnt_Out, RdCACntOverInt, RowRedBcCntOver, BACntCK, BAEnd, BASet`；实例化 `RedBistRdCACnt I_RedBistRdCACnt_3` | 地址生成器（组合 BA+CA+section） |
| `RedLatBistPat` | 426612 | `BaCnt, BcRACntClki, CACntCKi, ColRedBcCntOver, ColRedBistEn, RowRedBcCntOver, BaCntOver, CACntOver, RaSecCnt, RaSecCntOver` | REDBIST pattern（bank/section/column 计数） |
| `RedLatBistTop` | 428138 | `CheckErrorMacth, Cnt_Out, ColSeg0Sel, EvenOddFlag` | REDBIST 顶层 |
| `SerialOutRedFlag` | 416734 | `SerialOutDataOut, SerialOutLoadCkOut, SerialOutShiftOut`、`fnReadSigSerialOutRedColEn, fnReadSigSerialOutRedRowEn` | fail flag 串行读出 |
| `mBistPat` | 431537 | `BACntCK, BACntRst, CACntCK, RACntCK, RASecCntCK` | mBIST pattern（与 REDBIST 分离） |

## 拟造任务

- **case_id**: `EDA-Eval-DesignFlow-RedBistBroadcastErrAddrQA-001`
- **档**: A档（verbatim U#0 + U#66）
- **类型**: netlist-grounded mechanism-explain Q&A（套 #238 v2 / r739 / r729）
- **资产**: synth_deck `redbist_netlist_A.v`（从 trace 重建，真实 module 名/端口/关键计数器）；hidden B = 结构变体（8 banks / BA[2:0] / ColSectSel[2:0] / 重命名标识符，scenario: 8 banks broadcast at 05A0 sections differ → 8 error addresses）
- **candidate.py**: 读 deck + 问题 → 解析 REDBIST module → 提取 BA width/num_banks、section select、error-match signal、地址组成 → 按 broadcast+section-differ 规则算 num_error_addresses → 结构化 JSON
- **check.py**: 12 断言 a-l（B-grounding + anti-hardcode + num_banks=8 + num_error_addresses=8 + 地址组成 + merge_condition + error_capture + serial_readout + found_modules + 3-run 确定性）
- **负样本**: empty_zip / print_only / core_deleted / naive_per_bank_walk / hardcode_A
