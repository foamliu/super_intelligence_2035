# Deepread: 1794466134962_vjcll — SV 2D packed array flatten (DUALRANK bound fix)

**Session**: 1794466134962_vjcll | **User**: tomtang | **Host**: hfeg0pfn016 (10.129.33.142) | **mc**: 247 | **Domain**: digital
**Scan**: 11/13 (ssh_eda_search_20261113_131349) — NEW scan, fresh candidate
**Keywords**: verilog:3786;netlist:96;systemverilog:87;analog:53;lib.defs:10;cmos:4;aether:4;cadence:3

## User turns
- **U#0**: "/proj/dscqa/V0/simdir/verilog/e0019320/1104rank/verilog.ddr6.dscqa.thf 在这个目录下，使用Regression/pte_test.run进行DUALRANK仿真会出现以下报错，修改TB文件以解决这个问题。建议将ddr6_interface.sv中ONERANK/DUALRANK的变量定义修改，以增加变量使用的兼容性，如wire [1:0][5:0] dq_exp_pte;改成wire [2*6-1:0] dq_exp_pte;，修改所有相关的地方。" + xmelab *SE,BNDBERR bit-select [3]/[4] out of declared bounds [1:0] for 'DQ'
- **U#182-187**: "结束之后，通过执行run这个脚本，观察仿真目录中的xrun.log，如果有*E *SE *F类型的报错，就重新修改，直到没有报错为止。" (repeated)
- **U#239**: compare_tasks.sv 报错, unlink+copy, 修改 compare_tasks.sv
- **U#255**: "你改了compare_tasks.sv吗？改一下。我自己的仿真结果看起来不对，你先不跑run这个仿真脚本。"

## Agent approach (256 msgs, 1.58MB)
1. list_allowed_files + read ddr6_interface.sv, ddr6_package.sv, top.sv, ddr6_test.sv
2. **Root cause** (M89): DUALRANK defines `wire [1:0][5:0] DQ` — 2D packed array, first dim [1:0] = only 2 elements (index 0-1). TB accesses `DQ[3]`, `DQ[4]` → out of bounds. Fix: flatten to `wire [11:0] DQ` (flat [2*6-1:0]) so all bit indices 0-11 valid.
3. cp files to /home/tomtang/ (writable), chmod
4. Python string replacement: flatten 2D packed decls (DQ, dq_exp_pte, dq_exp_pte_flag, DQS) in ddr6_interface.sv; update CONNECT_DIRECT(DQ,...) in top.sv from single-element to slice
5. Iterative xrun simulation, check xrun.log for *E *SE *F, fix until clean
6. Later: compare_tasks.sv fix (separate issue)

## A-faithful assessment
✅ A-faithful: user gives path + symptom + suggested approach (flatten 2D→1D), NOT the exact algorithm/regex/which vars. Agent must discover all 2D packed decls and flatten them.
deliverable = modify private /proj/dscqa/ files → INFEASIBLE → **B档合成**

## B档 case synthesis: EDA-Eval-DesignFlow-SvPackedFlatten-001
- **Archetype**: sv-packed-array-flatten-refactor
- **L1-B**, pure stdlib CLI `--input <sv> --outdir <dir>`
- **Ref**: sv_packed_flatten_ref.py — strip_comments → regex find `(wire|reg|logic) [d1:0][d2:0] name` → flatten to `[(d1+1)*(d2+1)-1:0] name` → output SV + flatten_report.json
- **A**: ddr6_interface_A.sv (DUALRANK: DQ/dq_exp_pte/dq_exp_pte_flag/DQS [1:0][5:0] or [1:0][0:0]; ONERANK: [0:0][5:0]; comment traps)
- **B**: ddr6_interface_B.sv (DUALRANK: DQ [3:0][7:0]→32, dq_obs [3:0][3:0]→16, dq_chk [3:0][1:0]→8, DQ_data logic [3:0][7:0]→32, DQS_n [3:0][7:0]→32; ONERANK variants; comment traps)
- **check.py**: 14 conditions (a-n), independent oracle (strip_comments + regex on stripped, NOT ref's finditer)
  - key traps: ⑩comment trap (2D in comments preserved, not in code); ⑪cross-input guard (A names absent from B); ⑫3-seed stability; ⑭non-2D decls unchanged
- **Self-verify**: ref SELFTEST PASS 14/14; 5neg (naive_empty/print_only/no_flatten/hardcoded_A/partial_flatten) all FAIL; §4.9 fake-submit (empty_zip/garbage/print_string) all FAIL
- **断言闸门**: k_rationale = k_check = 14 ✓ (≥8)
- ledger mark vjcll→case, coverage 258→259/3260≈7.9% (new 11/13 scan target=3260)
