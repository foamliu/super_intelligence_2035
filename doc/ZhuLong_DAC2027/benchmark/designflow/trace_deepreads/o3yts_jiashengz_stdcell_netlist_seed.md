# Deepread seed — o3yts (jiashengz@hfeg0pkn004) — standard cell netlist → schematic

**Session**: `1794885953050_o3yts.messages.json` (jiashengz @ hfeg0pkn004 = 10.129.2.13)
**Size**: 866 KB, 133 msgs. **D-domain hits**: 599 (schematic:237 / netlist:55 / pyAether:159 / cellview:70 / virtuoso:35 / skill:22).
**Trace source**: fresh `eda_trace_20261122.log` (r1119 fresh-log method), live `.messages.json` (not .archive).
**Synthesized**: r1121 → `EDA-Eval-DesignFlow-StdcellNetlistToSchema-001` (schematic_netlist, L1, k=15).

## Real user intent (msg#0 + msg#1 thinking)
User provides a **Standard Cell Netlist report** for variant `NOT_W03_W05_L005`
(regular CMOS inverter: WN=0.3U / WP=0.5U / L=0.05U, 2 transistors 1P+1N,
pins A(QN)/QN, PINORDER `QN A`, `.SUBCKT NOT_W03_W05_L005 A QN`,
`MP1 QN A VDD VDD PMOS W=0.5U L=0.05U`, `MN1 QN A GND GND NMOS W=0.3U L=0.05U`,
parent instances I502/I574/I607/I640 in D_KD145). The user references the skill
`/home/jiashengz/agentdir/train/V0_NCG_HF_Aether/skill_stdcell_from_netlist.md`
and wants the circuit **drawn into library R1b1** (do not touch other libs).

Agent (msg#1): checks agent-policy (profileIds python-runner/shell-runner),
lists allowed files, reads the skill, then proceeds with pyAether/SKILL
dbOpenCellViewByType to create the schematic.

## Why this is a clean D (schematic_netlist) case
- Pure standard-cell schematic-from-netlist flow (D domain: schematic_netlist).
- Clear, structured deliverable: a netlist report → structured schematic manifest.
- The report format is section-structured (header / SIZE PARAMETERS / PIN
  DEFINITION / SPICE NETLIST / TOPOLOGY / INSTANCES) → parseable.
- Real user, real host, real skill path, real parent instances — fully traceable.

## Case design (r1121 synthesized)
- **A (visible)**: `cell_spec_A.txt` = real NOT_W03_W05_L005 report (2 MOS / 2 pins / inverter).
- **Hidden B (check runs here)**: `cell_spec_B.txt` = NAND2_W12_W08_L005
  (4 MOS / 3 pins / parallel-P + series-N / internal net N1 / WN=1.2U WP=0.8U).
  Differs from A in transistor count, pin count, AND topology → defeats an
  A-hardcoded solution.
- **Hidden A' (anti-hardcode cross)**: `cell_spec_Ap.txt` = NOR2_W10_W06_L005
  (4 MOS / 3 pins / series-P + parallel-N / internal net N2 / WN=1.0U WP=0.6U).
  Same pin/instance count as B but OPPOSITE internal-net topology (B's PMOS all
  source=VDD; A' has a PMOS with source=N2 internal) → defeats a B-structure-hardcoded solution.
- **Deliverable**: `submit.zip` containing `gen_manifest.py` (generic report→manifest translator).
- **check.py**: 15 conditions (a-o): zip+script / py_compile / run-on-B exit0 /
  cell_name / subckt_ports / pins / pinorder / supplies / instance-count /
  PMOS W-L-source-bulk / NMOS W-L-bulk+series-stack / QN-drivers / internal-N1 /
  determinism(md5×3) / anti-hardcode-A'(NOR2 series-P cross).
- **Self-verify (r1121)**: ref solution 15/15 PASS; 4 negatives ALL FAIL
  (neg_empty / neg_print_only / neg_hardcode_a / neg_core_deleted).
  §4.9 (a)(b)(c) three fakes all FAIL. D.jsonl 555→556.

## dup-check (r1113 lesson applied)
- jiashengz: 0 prior D cases (not in top case-users) → no same-user dup.
- task family "stdcell netlist → schematic manifest" ≠ r1119 LiberateInstGenQA
  (schematic → .inst, opposite direction) ≠ r1113 DelvtrandAudit (netlist scan).
- session `o3yts` not in any of the 4 shard ledgers before r1121 claim.
→ no dup.

## DEBT carried forward
- pi real-run pending (budget).
- mc-matrix recompute pending.
- D self-owned §4.9 anti-hardcode audit (448 → 447 remaining after this case).
- MEMORY_D.md archive (now ~60 KB, over 32 KB limit).
