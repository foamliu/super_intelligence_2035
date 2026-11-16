# Deepread: ujw1y — PRBS_TM 电路项目总结问答

**trace**: `1793792759786_ujw1y` (qiang3xu@hfeg0pkn005 = 10.129.2.14)
**host**: hfeg0pkn005 (10.129.2.14, ssh via .75 eda_flow sandbox)
**shard**: D (analog_context, mc=2921, mixed-signal circuit summary)
**session size**: 85 msgs, 666588 bytes
**ledger**: parked 2026-11-05 as "summarize PRBS_TM circuit; analysis/advice not produce-task" → revived 2026-11-17 per 11-15 mandate → case `EDA-Eval-DesignFlow-PrbsTmCircuitSummaryQA-001` (r792)
**asset reachability**: 原 `/proj/m2701/V0_DDR2/workdir/qiang3xu/MPW_xuq/PRBS_TM` 在 10.129.2.14 上，直接 ssh 超时，经 .75 eda_flow sandbox ssh 可达 ⇒ 从 trace read_files tool_results 重建 asset A（6 文件：prbs_tm_sch.hist / prbs_tm_symbol.hist / tb_prbs_tm_sch.hist / cds.lib / p2s_24b_veriloga.va / library_cells.txt 165 cells）

---

## 用户真实意图（A 档 verbatim U#0）

> `/proj/m2701/V0_DDR2/workdir/qiang3xu/MPW_xuq/PRBS_TM总结一下这个电路`

工程师 qiang3xu 在做 DDR2 测试模式生成器设计时，打开 MPW_xuq/PRBS_TM 电路项目，要求"总结一下这个电路"。**意图类型**：deck-grounded circuit-project summary Q&A（D 域 analog_context，11-15 mandate 复活的 analysis/Q&A 类，此前因旧"must produce runnable deliverable"规则 parked）。

## 金标准（assistant msg#41）

PRBS_TM = **22nm ULL PRBS pseudo-random bit sequence generator for DDR2 test pattern**：

1. **顶层 cell**：`PRBS_TM`（从 `PRBS_v2` 于 Sep_29 Copy 而来），library `MPW_xuq`。
2. **原理图迭代**：PRBS_v2 阶段 9 次 Check&Save（Sep 8 – Sep 23），PRBS_TM 阶段 36 次 Check&Save（Oct 19 – Nov 4），共 45 次。
3. **Testbench 演化链**：`TB_PRBS4` → `TB_PRBS8` → `TB_PRBS` → `TB_PRBS_v2` → `TB_PRBS_TM`（library `TB_MPW_xuq`），完整 5 代演进。
4. **p2s 并串转换器**：VerilogA module `vd_p2s_24b`，`WIDTH=24`，parallel-to-serial：@(cross(ck_ref)) 采样 24-bit vin → @(timer) 逐 bit 串行输出 vout + ck_out。
5. **LFSR 核心**：`LFSR_cell` / `LFSR_cell_v1/v2/v3`（4 代 LFSR cell），`LFSR_din_162/164/165/82162/82164/82165`（数据输入 LFSR），`LFSR_init`（初始化），`Rst_LFSR`（复位），`RdLfsr8/16/23/31` + `RdLsfr7`（读出 LFSR），`Lfsr_dec3_6`。
6. **PRBS 变体**：PRBS4 / PRBS7 / PRBS8 / PRBS15 / PRBS23 / PRBS31（6 种多项式），带 `_Par`（并行）/ `_TM`（test mode）/ `_TM24`（24-bit test mode）后缀，共 40+ 变体。
7. **标准单元**：`and2Fx1_sub` / `aoi21Fx1_sub` / `invFx1_sub..4_sub` / `invenF_sub` / `invhizF_sub` / `nand2Fx1_sub` / `nor2Fx1_sub` / `or2Fx1_sub` / `xor2Lx1rvt` / `xordFx2/3_sub` / `passgtFx2_sub`（组合逻辑）；`DFF_ulvt` / `DFF_PRBS` / `latch_PRBS` / `ffrsqrvtx1` / `ffrsqqnrvtx1` / `ffrqrvtx1`（时序逻辑）；`MUX` / `MUX1111` / `MUX_2T1`（多路选择）。
8. **模块功能总结**：PRBS pseudo-random bit sequence generator，LFSR-core based，for DDR2 test pattern generation。

## 资产重建（asset A）

从 trace read_files tool_results 提取 6 个源文件，逐字保留：

- `prbs_tm_sch.hist`（47 行）：MPW_xuq/PRBS_v2 schematic 9 次 Check&Save + [Copy Info] Sep_29 + MPW_xuq/PRBS_TM schematic 36 次 Check&Save。
- `prbs_tm_symbol.hist`（7 行）：MPW_xuq/PRBS_v2 symbol 2 次 + [Copy Info] + MPW_xuq/PRBS_TM symbol 3 次。
- `tb_prbs_tm_sch.hist`（47 行）：TB_MPW_xuq testbench 演化链 TB_PRBS4→TB_PRBS8→TB_PRBS→TB_PRBS_v2→TB_PRBS_TM，46 次 Check&Save。
- `cds.lib`（5 行）：DEFINE MPW_xuq /proj/m2701/V0_DDR2/workdir/qiang3xu/MPW_xuq + TB_MPW_xuq + ahdlLib。
- `p2s_24b_veriloga.va`（66 行）：module vd_p2s_24b，`define WIDTH 24，parallel-to-serial VerilogA。
- `library_cells.txt`（165 cells）：全库 cell 清单。

## Hidden B（identifier-renamed structural variant）

B = A 的标识符重命名变体，所有 identifier anagram/swap，数字与后缀保留：

| A | B |
|---|---|
| PRBS | PBRS |
| LFSR / Lfsr / LSFR / Lsfr | RLFS / Rlfs / RLSF / Rsfr |
| MPW_xuq | XUQ_MWP |
| qiang3xu | xqiang3 |
| p2s_24b / vd_p2s_24b | p2z_24b / vd_p2z_24b |
| DFF_ulvt / DFF_PRBS / latch_PRBS | DFF_tluv / DFF_PBRS / latch_PBRS |
| and2Fx1_sub / xor2Lx1rvt | adn2Fx1_sub / xro2Lx1rvt |
| Rst_LFSR / RdLfsr / RdLsfr | Rst_RLFS / RdRlfs / RdRsfr |
| TB_MPW_xuq / TB_PRBS_TM | TB_XUQ_MWP / TB_PBRS_TM |

零 A-identifier 泄漏（经 build script sanity check 验证："OK: zero A-identifier leakage into B"）。

## candidate.py（reference solution）

CLI: `python3 candidate.py <deck_dir>`，通用 deck parser（无硬编码标识符）：

1. `find_hist_files`：遍历 *.hist，按 viewtype（schematic/symbol）+ cell 前缀（TB_）分类为 main_sch / main_sym / tb_sch。
2. `top_cell_from_hist`：取最后一条 Checkandsave 的 cell = top_cell；[Copy Info] from_cell = source_cell；lib = library；len(saves) = num_checkandsave。
3. `parse_veriloga`：regex `module\s+(\w+)\s*\(` → p2s_module_name；`\`define\s+WIDTH\s+(\d+)` → p2s_width。
4. `parse_cds_lib`：regex `DEFINE\s+(\S+)\s+(.+)` → dict。
5. `parse_library_cells`：前缀分类 lfsr（lfsr/lsfr/rlfs/rsfr/rlsf）/ prbs（prbs/pbrs）/ stdcells（inv/nand/nor/and/aoi/oai/xor/xnor/ff/latch/mux/passgt/latrq/fbsr）。
6. `extract_cited_identifiers`：从 question_*.txt 路径提取标识符（ASCII only）。
7. `derive_function_summary`：根据 prbs+lfsr+DDR2(cds.lib path) 推导 "pseudo-random bit sequence (PRBS) generator (LFSR-core based), for DDR2 test pattern generation"。
8. 输出 13 顶层键 JSON。

## check.py（14 断言 a-n）

| # | 断言 | 退化覆盖 |
|---|------|---------|
| a | zip 含 candidate.py | empty_zip → FAIL a |
| b | py_compile 通过 | syntax-broken → FAIL b |
| c | 13 必需顶层键 | print_only → FAIL c |
| d | cell_name == PBRS_TM | core_deleted → FAIL d |
| e | source_cell == PBRS_v2 | |
| f | library == XUQ_MWP | |
| g | testbench == TB_PBRS_TM | |
| h | num_checkandsave == 45 | |
| i | p2s_module_name == vd_p2z_24b | |
| j | p2s_width == 24 | |
| k | lfsr_families 非空 + B-grounded (RLFS) | naive_no_lfsr → FAIL k |
| l | prbs_variants 非空 + 含 PBRS_TM | |
| m | anti-hardcode: 无 A-only token | hardcode_a → FAIL m |
| n | 3-run md5 一致 | |

## 自验结果

- ref 14/14 PASS
- 5 neg FAIL distinct labels（empty_zip→a / print_only→c / core_deleted→d / hardcode_a→m / naive_no_lfsr→k）NEG_RC=0
- §4.9 三退化（empty_zip / print_only / core_deleted）全 FAIL
- candidate on A 通用化：产 PRBS_TM / MPW_xuq / vd_p2s_24b / LFSR_cell（A 专属），与 B 输出不同，证明非 canned
- k_rationale = k_check = 14 ≥ 8 GATE PASS

## 复活理由

此 case 于 2026-11-05 因旧"must produce runnable deliverable"规则 parked（判为"summarize PRBS_TM circuit; analysis/advice not produce-task"）。2026-11-15 mandate 明确复活 analysis/Q&A/doc-search 类候选。本 case 正是该类型：用户要求"总结一下这个电路"，gold = 结构化电路项目总结，无产出物要求。按 deck-grounded Q&A 模式（r787/r790/r791 pattern）改造为 design_flow benchmark：candidate.py 解析 deck 元数据 → 结构化 JSON summary。
