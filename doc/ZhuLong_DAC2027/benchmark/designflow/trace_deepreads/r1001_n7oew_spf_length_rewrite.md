# r1001 deepread: 1794813263342_n7oew (kaixuanx@hfeg0plg57, mc=25)

## Trace
- user: kaixuanx (NEW user), host: hfeg0plg57, mc=25
- agent: lead, 44 msgs, ~moderate size
- kw: pex:22; transistor:8; aether:4; synopsys:1; pyaether:1; calibre:1
- domain: physical_verify (PEX)

## User intent (organic, 提出需求)
- U#0: "我现在有一个.spf文件，我想把其中的管子的length=39nm 改为36nm，修改后的文件单独保存"
- U#1/U#2: same intent with concrete path `/proj/drgqa/V0/ver/pex/kaixuanx/DL_CDL/DL_CDL.spf_RCC` (repeated 2x — user re-issued after env setup)
- Real task: modify MOSFET transistor length 39nm→36nm in a DSPF 1.3 parasitic netlist (.spf), save to a separate output file (do not overwrite source).

## Agent work
1. Checks policy / readable-writable roots (`/ai_sandbox/drvsa/V0/agentdir/kaixuanx`, `/home/kaixuanx`)
2. read_files the .spf (DSPF 1.3, 50000+ lines) — confirms it is a large DSPF 1.3 file
3. Writes `analyze_spf.py` to count `length`/`l=`/`L=`/`39n` occurrences (probe exact parameter format)
4. Hits Python 3.7.1 locale/PYTHONHOME issue → writes `check_env.sh` wrapper to set PYTHONHOME
5. (session 44 msgs total — moderate; core deliverable is the length-rewrite script + output file)

## Key facts
- File: DSPF 1.3, cell DL_CDL (RCC variant), ~50k lines
- Target parameter: MOSFET `L=39n` (SPICE length suffix `n`=nano=nm) → `L=36n`
- Only transistor instances (M-lines) get rewritten; comments/metadata/parasitics untouched
- Source path `/proj/drgqa/...` readable as kaixuanx, NOT readable by e0031982 (permission denied) → A/B must be SYNTHETIC (faithful DSPF 1.3 format), consistent with A档 rule (real assets inaccessible → faithful synthetic)

## B档 redefinition (offline-synthesizable)
- A (spf_a.spf): synthetic DSPF 1.3, cell `DL_CDL_A`, 4 ports, 6 MOSFETs (4×L=39n to change, 2×decoy L=20n/L=24n), *|HINT comment containing literal `L=39n` (must NOT be altered), parasitic *|R/*|C lines
- B (hidden/spf_b.spf): synthetic DSPF 1.3, cell `RCC_PIPE_B`, 5 ports, 8 MOSFETs (5×L=39n→36n, 3×decoy L=15n/L=22n/L=30n), disjoint net/instance/model names (pmos2/nmos2), *|HINT comment with L=39n
- A and B disjoint in: cell name, port count/names, net names, instance names, model names, MOSFET count, decoy L values. Share ONLY the L=39n→36n transformation + a *|HINT comment carrying literal L=39n.

## Case design (spf_mos_length_rewrite, k=15)
- CLI: `python3 solve.py <input.spf> <output.spf>`
- check.py runs solve on B, 15 assertions: zip+compile, B exit0+nonempty, .SUBCKT/.ENDS preserved, M-line L=39n→0, L=36n==5, decoy counts unchanged, M-count==8, non-M lines byte-identical, *|HINT L=39n comment preserved, line count, .SUBCKT token-exact, deterministic md5, anti-hardcode A demo (4×L=36n, decoys 20n/24n, M=6, hint preserved), 3-seed random M-line mapping
- §4.9 three fakes: empty shell / print-only / delete-core (drop M-lines) — all FAIL
- 3 extra negatives: naive cp (no change), hardcode-A (only rewrite if cell==DL_CDL_A), always-36 (rewrite every L=*n to 36n, corrupts decoys) — all FAIL
- Self-verify: reference_solution PASS 15/15; 6 negatives all FAIL distinct; negative_selftest.py exit 0

## Decision
- A档自包含 (synthetic DSPF, no external dep), B档 disjoint anti-hardcode, k=15≥8, 3 neg + §4.9 三假 all FAIL → quality gate met.
