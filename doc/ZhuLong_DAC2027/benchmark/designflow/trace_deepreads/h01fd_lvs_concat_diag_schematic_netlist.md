# Deepread: h01fd (shanliny@hfeg0pkn003, mc15, schematic_netlist)

## Trace provenance
- **session**: `/home/shanliny/.cline/data/sessions/1789713289092_h01fd/` on .75 (10.129.32.75)
- **session_file**: `1789713289092_h01fd.messages.json` (8.16MB, 10 msgs / 5 user / 5 assistant)
- **session.json**: model=glm-5.2, status=failed, started 2026-09-18, ended 2026-09-20
- **cwd**: `/proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/tiling_version/tiling_ver6/svs`
- **scan match_count**: 15 (11-18 snapshot); keywords `lvs:148;schematic:132;netlist:30;transistor:4;aether:4;.cdl:4;calibre:1`
- **domain**: schematic_netlist (LVS debug of CDL/netlist concat logic) — D-shard confirmed

## User intent (verbatim)
**U#0**: `参考lvs.rep告诉我1prf.py拼接的逻辑哪里出了问题`
  — attached: 1prf.py (68.5KB, 1537 lines, SRAMGenerator netlist tiler), netlist_interface.py (35.8KB), HC1P_CXN4S1P2048X144M4B2C1R1W1BW1RE1.cdl (2.6MB), 0_run (0.2KB), CX2048X144M4B2C1.netlist (3.9MB), lvs.rep (1.2MB Calibre LVS report)
**U#1**: `你在说改什么改什么的时候给我把具体在哪个函数里加上`

## Assistant diagnosis (gold standard)
Assistant (glm-5.2) identified **3 concat-logic errors** in 1prf.py:

### Error 1: `build_row()` 第143-144行 — IC_RE2 BL/BLB 误接
- **function**: `build_row(self, iops, name)` (line 90起)
- **problem lines**: 143-144
- **wrong**: `rename_inst_ports(inst_name, "BLB", f"BLB_RED<{self.CM}>")` and `BL` → `BL_RED<{self.CM}>` (CM=1 → BL_RED<1>)
- **correct**: IC_RE2 BL/BLB should share IC_RE1's redundant bitline → `BL_RED<0>` / `BLB_RED<0>`
- **LVS evidence**: VSS net has 253 unmatched instances (`BKB/BK_R/ARRAY/IR63/IC_RE/Ibitcell_4x1[1]` drain → `BL_RED_R_D[0]` vs source `net170[1]`)

### Error 2: `build_top()` bank循环 (~line 912后) — VDDWL 漏改
- **function**: `build_top(self)` (line 833起, bank循环内)
- **problem**: bank循环只rename BL/BLB/FCKB/XB/XC加_U/_D后缀，漏掉VDDWL → 上下bank共用同一VDDWL
- **correct**: `rename_inst_ports(bank_name, "VDDWL", f"VDDWL_{up_or_down}")`
- **LVS evidence**: `BKT/BK_L/WLBUF/BUF0/MVDDWL_HEADER  d: BKT/VDDWL ** VDDWL_U **`

### Error 3: `build_top()` bank循环 — WL_IN 漏改
- **function**: `build_top(self)` (同上bank循环)
- **problem**: 漏改 WL_IN → 上下bank XDEC输出共用同一WL_IN总线 → WL[232]与WL[169]短接
- **correct**: `rename_inst_ports(bank_name, f"WL_IN<{self.rpb-1}:0>", f"WL_IN_{up_or_down}<{self.rpb-1}:0>")`
- **LVS evidence**: `BKT/BK_L/WL[232] ** BKB/BK_L/WL[169] **`

### Summary table (assistant output)
| 错误 | 函数 | 行号 | 漏改的信号 |
|------|------|------|-----------|
| 1 | build_row() | 143-144 | IC_RE2 BL/BLB 应接<0>而非<CM> |
| 2 | build_top() | ~912后 | VDDWL → VDDWL_U/VDDWL_D |
| 3 | build_top() | ~912后 | WL_IN → WL_IN_U/WL_IN_D |

## Case synthesis (A档 trace-faithful, revival-from-parked)
- **旧parked原因** (2026-11-10 11:52): "analysis-debug: user asks 'tell me where 1prf.py concat logic went wrong' per lvs.rep; agent produced PROSE diagnosis" → 旧规则判 analysis-only weak
- **新判** (per 2026-11-15 用户令): debug-Q&A / analysis-only 全部恢复为可造 — 真实用户意图 ✓
- **case_id**: EDA-Eval-DesignFlow-LvsConcatDiagQA-001
- **资产A**: 合成精简 1prf_A.py (~200行, 保留SRAMGenerator class + build_row/build_xdec/build_bk/build_bank/build_top 真实结构签名 + 3 bug位置) + lvs_A.rep (合成精简, 保留3条evidence: VSS 253 extra / VDDWL_HEADER VDDWL vs VDDWL_U / WL_IN shorted)
- **隐藏B**: 1prf_B.py (build_col bug BLB_RED<CM>, build_top漏VSSWL+WL_BUF) + lvs_B.rep — 与A全不同反硬编码
- **隐藏B2**: 1prf_B2.py (build_array bug GBL_RED<CM>, build_top漏VDDWL+FCKB) + lvs_B2.rep — 第三变体
- **隐藏B3**: 1prf_B3.py (clean, 无bug) + lvs_B3.rep (LVS CORRECT) — 真阴性, 期望0 errors
- **reference**: diag_lvs_concat_ref.py (regex扫rename_inst_ports + LVS evidence parse → 结构化JSON: bitline_index_mismatch + missing_per_bank_rename 两类bug)
- **check.py**: 14断言 a-n, 跑候选脚本on B/B2/B3 + 3随机种子一致性 + 跨变体无泄漏
- **自验**: reference_submit.zip 14/14 PASS ✓ + negative_selftest 3 neg (empty壳/只hardcode/删核心) 全FAIL ✓
- **D.jsonl**: 486 → 487
