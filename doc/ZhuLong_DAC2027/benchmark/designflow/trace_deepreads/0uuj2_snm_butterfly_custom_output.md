# Deepread: 1794297017130_0uuj2 — Solido SNM Butterfly Custom Output

## Trace Source
- **anchor**: 1794297017130_0uuj2
- **user**: e0030760
- **host**: hfeg0pkn001
- **session_file**: 1794297017130_0uuj2.messages.json
- **domain**: spice_sim (characterization)
- **match**: Solido HSV MC SRAM SNM butterfly custom output

## Session Overview (259 messages)

The session spans multiple sub-tasks:

1. **msg0-17**: Desktop file cleanup (chore — move Desktop files to archive folder)
2. **msg18-49**: Analyze Solido HSV MC results (`/proj/lacaa/V0/workdir/e0039809/solido/variation_designer_3/results/HSV-0`)
   - User asks to explain high-sigma MC results
   - Assistant reads summary.txt, full_summary.txt, summary.json, engine.log, ordering_path.txt, task XMLs, testbench
   - Explains HSV methodology: 3000 sims = 2000 initial + 1000 ordered, 1.7G virtual population, 5.612σ for Iread≥16µA spec
   - Writes `.zhulong_verify_sigma.py` to verify sigma/failure calculations (Phi(-N) match)
3. **msg50-61**: User asks to document HSV logic → writes `Solido_HSV_simulation_logic.md` (5735 chars, comprehensive)
4. **msg62-163**: User asks about netlist generation with Aether EDA (techfile, PDK, PCell, schematic, export netlist)
5. **msg164-185**: User wants array-level simulation → assistant produces:
   - `gen_array_netlist.py` — SRAM array netlist generator (4x2, checkerboard pattern, .NODESET)
   - `tb_array_read.sp` — SPICE testbench for array-level read margin (HSPICE .MEASURE)
6. **msg186-252**: **KEY PRODUCE-TASK** — User asks to compute WNM/RNM via Python script integrated into Solido:
   - msg186: "我想要根据仿真结果在solido输出WNM、RNM的值，这个值需要通过py脚本提取，这个功能可以集成到solido软件中吗？"
   - msg198/200: User provides testbench `CH252_FS_6T_SRAM_single_Bitcell.sp`, asks to write HSNM/RSNM butterfly curve script + integrate into Solido
   - msg205: Assistant writes `solido_snm_custom_output.py` (v1, 5103 chars) — Format B only, correct axis-swap
   - msg207: Writes `make_mock_lis.py` — mock .lis0 generator with known VTC params (VDD=0.75, Vm=0.37/0.35/0.36/0.35, s=0.015)
   - msg219: v1 verified on mock data: HSNM=0.321V, RSNM=0.328V ✓
   - msg225: User asks to check against REAL simulation results
   - msg236-238: v1 FAILS on real data (HSNM=0/RSNM=0) — real .lis is Format A (block-per-signal), not Format B
   - msg242: Assistant writes v2 (`solido_snm_custom_output_v2.py`, 6871 chars) — dual-format parsing (A+B)
   - msg248-252: Discovers v2 has axis-swap bug (R curve not swapped → 0 for symmetric cells), about to fix

## Key Deliverable: solido_snm_custom_output_v2.py

**Correct version** = v2's dual-format parsing + v1's axis-swap:
- Parses HSPICE .lis/.lis0 DC sweep tables (Format A: block-per-signal, Format B: combined table)
- Extracts 4 signals: q_rnm, qb_rnm, q_hnm, qb_hnm
- Constructs butterfly curves: RSNM L=(vin,q_rnm) R=(qb_rnm,vin), HSNM L=(vin,q_hnm) R=(qb_hnm,vin)
- Computes SNM = max axis-aligned inscribed square between L and R curves
- Output: `HSNM=value\nRSNM=value` to SIM_DIR/OUTFILE_NAME
- Pure Python stdlib (bisect, glob, os, sys)

## Bug Journey (v1 → v2)
- **v1 bug**: only parses Format B (combined table) → fails on real data (Format A)
- **v2 bug**: dual-format parsing but `snm_from_series` doesn't axis-swap R curve → produces wrong values
- **Correct fix**: v2 parsing + v1's `snm_butterfly` (which correctly does `zip(qb_free_r, vin)` for axis-swap)

## Mock Data Parameters (make_mock_lis.py)
- VDD = 0.75V, 751 points (VIN 0→0.75V, step 1mV)
- q_rnm: VTC Vm=0.37, s=0.015
- qb_rnm: VTC Vm=0.35, s=0.015
- q_hnm: VTC Vm=0.36, s=0.015
- qb_hnm: VTC Vm=0.35, s=0.015
- VTC: vtc(x,vm,s) = VDD / (1 + exp((x-vm)/s))
- Expected: HSNM=0.321V, RSNM=0.328V

## Case Synthesis
- **Case ID**: EDA-Eval-DesignFlow-SnmButterflyCalc-001
- **Track**: synthesized (B-synthesized L1)
- **Domain**: spice_sim
- **Real task summary**: 根据 HSPICE .lis DC 扫描蝴蝶曲线数据计算 6T SRAM 的 HSNM/RSNM，作为 Solido Custom Output 脚本集成到 MC/HSV 仿真流程中
- **Hidden B1**: Format A mock .lis0 (block-per-signal) → HSNM=0.321, RSNM=0.328
- **Hidden B2**: Format B mock .lis0 (combined table) → same values
- **6 negatives**: format_a_only, no_axis_swap, wrong_output_format, mean_n_std, swapped_nodes, no_error_handling
- **k_check**: 15 (≥8 ✓)
