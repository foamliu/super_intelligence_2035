# deepread: 1793174925139_f0vya — SRAM 6T testbench + PMOS-VDD sweep (e0030760)

- **trace**: `1793174925139_f0vya.messages.json` (e0030760 @ hfeg0plg74, mc=410, 335 msgs, 1.76MB)
  - snapshot path (live file gone): `/home/e0030760/.snapshot/hourly-new.2026-11-02_1100/.cline/data/sessions/1793174925139_f0vya/`
  - tool tally: editor×73, run_approved_command×55, read_files×31, list_allowed_files×13
- **domain**: spice_sim / characterization. HSPICE-dominant (935 hspice hits in scan).
- **user intent (verbatim)**:
  1. `我需要根据现有的model建立简单的一个SRAM 6T单元的testbench，并仿真PMOS不同VDD对Iread和Iwrite的影响，应该怎么做？`
  2. `用中文跟我交流`
  3. `/proj/lacaa/V0/model/current_PF_v0d1_Rev05 读取这个路径的model，对上面的testbench进行修改，仿真PMOS VDD从0.75V减少到0.5V，SRAM WNM、RNM和Iread和Iwrite的影响，新的生成的文件保存在/home/e0030760/Documents/SRAM_6T_testbench 中。不能修改lacaa文件路径中的所有内容。`
- **real agent tool chain (phase 1, level-1 model)**:
  - built `sram_read.sp` / `sram_write.sp` + `run_sram_iv.py`; HSPICE `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice64`.
  - bugs hit & fixed: (a) HSPICE MOSFET pin order `M name D G S B` — wrote `Ma1 bl q wl 0` (gate tied to Q) → read current ~0; fixed to `Ma1 bl wl q 0`. (b) `.STEP PARAM` unsupported by this PrimeSim HSPICE (`unknown command ".step"`) → external Python VDD loop. (c) `.measure` `abs()` not accepted → handle sign in Python. (d) `.mt0` parser dropped `$DATA1`/`.TITLE` header rows. (e) 18-run sweep timed out → 5-point default + incremental CSV.
  - phase-1 result (level-1): VDD 0.8→1.2 V, Iread 101→365 µA, Iwrite 19→100 µA, read-stable (Qpeak<0.17V), write ok.
- **real agent tool chain (phase 2, foundry 35nm GAA BSIM-CMG model at /proj/lacaa/...)**:
  - discovered devices are **subcircuits** (`X` element, not `M`): `.subckt nsvt_fs d g s b wgaa=...` / `psvt_fs`; binned models `nsvt_fs.1/.5`, `psvt_fs.9` selected by geometry. PDF usage doc unreadable (fontconfig broken) → derived syntax empirically.
  - sizing: PD nfin=3, PG nfin=2, PU nfin=1. Iread≈74 µA, Iwrite≈29 µA @0.75V.
  - **WNM/RNM via butterfly VTCs** (`sram_vtc_read.sp` / `sram_vtc_write.sp` + `_parsevtc.py`): each inverter half-cell loaded by its access transistor; DC transfer tables in `.lis` use **engineering suffixes** (`749.9999m`) → needed unit-aware parser.
  - **SNM bug & fix**: first method assumed inscribed square centered on anti-diagonal `q+qb=VDD` → **RNM=0**. Fixed to "largest axis-aligned square in 45°-rotated coords anywhere in the eye". Final RNM≈2.5 mV (tiny — weak nfin=1 PU heavily read-disturbed).
  - final accepted table (PMOS VDD 0.75→0.5 V): Iread 74→~3 µA, Iwrite 28.9→~3 µA, WNM 0.456→~0.3 V, RNM ~0.0025 V, read-stable & write-ok at all points.
- **synthesized subtask (B档, this case `EDA-Eval-DesignFlow-SramSNM-001`)**:
  - focused on the **butterfly SNM (RNM/WNM/hold) vs VDD sweep** — the hardest, most reproducible sub-skill. Uses a **self-contained level-1 model** (portable to .75, no foundry-model dependency) so the case is reproducible.
  - candidate submits `sram_snm.py`: reads `cell.sp` (`.subckt SRAM_INV qout qin wl bl vdd vss` = inverter + access + weak load + level-1 `.model`) and `sweep.json`; per VDD point runs HSPICE DC VTC sweeps for hold (wl=0) / read (wl=VDD,bl=VDD) / write (wl=VDD; A bl=VDD, B bl=0); parses `.lis` DC table (suffix-aware); forms butterfly in (q,qb) using the **mirrored** inverter-B curve `[(qout,qin)]`; computes largest axis-aligned inscribed square per condition.
  - key discriminators: real HSPICE subprocess; suffix-aware DC-table parse; mirrored-VTC butterfly (un-mirrored → eye collapses to 0); inscribed-square eye search; RNM<hold (access degrades); VDD monotonicity; cross-input B (different sizing/Vth/kp/load/VDD).
- **.75 verification (2026-11-02)**: ref `sram_snm_ref.py` run on hidden B (cell_b.sp: W=1.5u/L=0.5u, vto=0.4, kp_n=300/kp_p=100, Rl=5e5; vdd=[0.80,0.70,0.60]) →
  - hold_snm 0.3321 / 0.2407 / 0.1544 ; rnm 0.2871 / 0.2128 / 0.1357 ; wnm 0.2342 / 0.1740 / 0.1138
  - monotonic ✓, rnm<hold ✓, all nonzero ✓, n_runs=18, verdict=pass. **GT embedded in check.py.**
- **DEBT (next round's first task)**: run `negative_selftest.py` on .75 (ref must PASS 14/14, 3 negatives must FAIL); then §4.9 three-fake-submission check; then append `EDA-Eval-DesignFlow_B.jsonl` + `mark --status case`.
- **pitfalls hit during synthesis**:
  1. cross-coupled 6T DC sweep → solver degeneracy (qb stuck ~84 mV, not VDD). Fixed by using the **half-cell** VTC (one inverter + access + explicit 1e6 load, PMOS bulk=vdd) — matches the trace's half-cell approach.
  2. symmetric hold/read conditions: VTC_A and VTC_B decks are identical → **must mirror B's curve** (`[(qout,qin)]`) or the eye is zero. (This is the same class of bug as the trace's RNM=0.)
  3. rotated-frame (u=(q+qb)/2) inscribed-square degenerates for near-symmetric VTCs (u≈const → SNM=0). Switched to direct axis-aligned largest-square in (q,qb) via eye-height profile on a common q-grid — robust.
  4. `write_file` (eda_flow) is safe; `cat <<'EOF'` heredocs in `run_commands` corrupt `0-9`→`d` and `\d`→`d`. Use `write_file` for code.
