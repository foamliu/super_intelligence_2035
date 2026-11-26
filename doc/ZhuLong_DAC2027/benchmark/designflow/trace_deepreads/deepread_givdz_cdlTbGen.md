# Deepread: givdz — CDL Testbench Generator (CdlTbGen-001)

- **trace**: `1793255447731_givdz.messages.json` (dsgao@hfhds201, mc129, eda_other)
- **session path**: `hfhds201:/home/dsgao/.cline/data/sessions/1793255447731_givdz/1793255447731_givdz.messages.json`
- **size**: 148 msgs, 78 user turns, 74 assistant tool calls
- **selected user turn**: U#1 (verbatim, pure goal, A-eligible)
- **case**: `EDA-Eval-DesignFlow-CdlTbGen-001` (eda_other, L1-offline, A档 faithful)
- **status**: synthesized, self-verified, appended to EDA-Eval-DesignFlow_A.jsonl (#166)

## User's original words (U#1, verbatim — A档 task prompt)

> /proj/drcpa/V0/workdir/dsgao/Ras_Tscodecomp.netlist   xieyige testbench yanzheng zhe ge dian lu

(混合中英: "写一个 testbench 验证这个电路" — pure goal, no implementation hints.
A-eligible: the user states what they want, not how to do it.)

## What the assistant actually did (trace-faithful summary)

1. **Read** `/proj/drcpa/V0/workdir/dsgao/Ras_Tscodecomp.netlist` (226 lines, CDL).
   Top subckt: `.SUBCKT Ras_Tscodecomp A<2> A<1> A<0> B<2> B<1> B<0> C<2> C<1> C<0> HT LT NT vbn! vbp! vcc! vss!`
   (9 inputs: 3-bit A/B/C; 3 outputs: HT/LT/NT; 4 power: vbn!/vbp!/vcc!/vss!).
   Internal subckts: xnor2l, nor2l, nand2Lx1, invLx1.
2. **Wrote** `make_tscodecomp_tb.py` — a config-driven generator that:
   - parses the netlist to locate the top `.SUBCKT` and its port order,
   - emits power supplies (vcc/vbp=dc=pvcc, vss/vbn=dc=pvss),
   - emits a ripple-counter stimulus over the declared inputs
     (bit k: V1=pvss V2=pvcc TD=0 TR=tr TF=tf PW=2^k*ts PER=2^(k+1)*ts),
   - emits `.measure tran out_NNN FIND V(out) AT=n*ts+settle` for every output
     at every input combination (n = 0..2^ninputs-1),
   - emits `.include` of the netlist and an `X1` instantiation using the
     netlist-declared port order.
3. **Wrote** `Ras_Tscodecomp_tb.sp` (1587 lines, 1536 .measure statements:
   512 combos × 3 outputs HT/LT/NT). `.tran 0.5n 1.024e-5`. X1 line uses the
   netlist port order verbatim.
4. **Wrote** `Ras_Tscodecomp_verify.py` — a post-sim checker that reads the
   finesim `.mt0` file and verifies expected logic (HT=high-true, etc.).

## Asset recovery

- `Ras_Tscodecomp.netlist` (226 lines): recovered from in-session
  `read_file` tool_results (the `/proj/drcpa/V0/` path was permission-denied
  via scp, but the assistant had read the full file into the session).
  All 226 lines recovered, no missing content.
- `Ras_Tscodecomp_tb.sp` (71695B): recovered from the eda_flow session workdir
  on .75 (assistant's run output).
- `make_tscodecomp_tb.py` (3979B): recovered from the session workdir.

## Synthesized case (A档 faithful)

- **task_id**: `EDA-Eval-DesignFlow-CdlTbGen-001`
- **domain**: eda_other
- **difficulty**: L1 (offline generator; no real simulation in judging)
- **deliverable**: `make_tb.py` (config-driven finesim testbench generator)
- **gold**: `reference/CdlTbGen-001/make_tb.py` — config-driven, reads
  `config.json{netlist, top_subckt, inputs[], outputs[], power, pvcc, ts,
  settle, outfile, ...}`, parses netlist `.SUBCKT` port order, emits
  ripple-counter stimulus + `.measure FIND` per output per combo.

### Hidden B / B' (cross-guard, anti-hardcoding)

- **B = Blog_EqCmp4** (8 inputs A<3:0>/B<3:0>, 1 output EQ, 256 combos,
  ts=1e-8, pvcc=1.2): xnor2l tree + nand2Lx1 + invLx1. 256 measures.
- **B' = Blog_MagCmp2** (4 inputs A<1:0>/B<1:0>, 2 outputs GT/LT, 16 combos,
  ts=5e-8, pvcc=0.9): and2l + invLx1. 32 measures (16 combos × 2 outputs).
- B and B' differ from A (Ras_Tscodecomp: 9 in, 3 out, 512 combos, ts=2e-8,
  pvcc=1.1) in top subckt name, input count, output count, combo count, ts,
  pvcc — ensuring a hardcoded-to-A generator fails.

### check.py — 14 conditions (a-n)

| # | cond | what it checks |
|---|------|----------------|
| a | zip | submit.zip valid zip containing make_tb.py |
| b | compile | make_tb.py passes py_compile |
| c | [B] run | `python3 make_tb.py config_b.json` exit 0 + writes tb_b.sp |
| d | [B] tran | tb_b.sp has `.tran` line |
| e | [B] include | tb_b.sp `.include netlist_b.cdl` |
| f | [B] X1 ports | X1 instantiates Blog_EqCmp4 with netlist-declared port order |
| g | [B] stimulus | 8 stimulus sources V* (one per input) |
| h | [B] measure count | .measure count == 256 (2^8 × 1) |
| i | [B] AT times | measure AT == n*ts+settle for n=0..255 |
| j | [B] pvcc | .param pvcc == 1.2 |
| k | [B] ts | .param ts == 1e-8 |
| l | anti-hardcode | make_tb.py source has no A literals (Ras_Tscodecomp/HT/LT/NT/512/1536) |
| m | [B'] cross-guard | B' → 32 measures, X1=Blog_MagCmp2, pvcc=0.9, ts=5e-8, 4 src, .include netlist_bp.cdl |
| n | [B] no A ports | tb_b.sp has no A port names (HT/LT/NT/C<2>/C<1>/C<0>) |

### Self-verify results

- **REF PASS**: 14/14 (reference make_tb.py passes all conditions on B + B')
- **Negatives** (all FAIL, distinct):
  - `naive_noop.py` (§4.9a 空壳) → FAIL (c): no tb_b.sp produced
  - `print_expected.py` (§4.9b 只print) → FAIL (e): hardcoded A tb, no .include netlist_b.cdl
  - `core_deleted.py` (§4.9c 删核心) → FAIL (f): parse_top_subckt returns hardcoded A ports, wrong port order
- **§4.9 three-fake**: all FAIL, distinct fail conds = {c, e, f} (3 distinct) ✓
- **k gate**: k_rationale = 14 (circled nums ①-⑭) == k_check = 14 (CONDITIONS) ≥ 8 ✓

## Notes / decisions

- Selected U#1 over later turns (U#1 is the purest goal statement; later
  turns are refinement/fix requests). A档 rule: task prompt = user's verbatim
  original words.
- The real gold `make_tscodecomp_tb.py` was itself config-driven (read a
  config dict), so the synthesized `make_tb.py` is faithful to the trace's
  approach — just generalized to read an external `config.json` file (so the
  hidden B/B' configs can drive it).
- The netlist `/proj/drcpa/V0/workdir/dsgao/Ras_Tscodecomp.netlist` could not
  be scp'd (permission denied), but the full 226-line content was recovered
  from in-session `read_file` tool_results, so the A asset is complete and
  faithful.
- L1 (offline): no real finesim simulator is invoked in judging. The check
  runs the candidate generator and statically analyses the emitted `.sp`
  testbench. This is appropriate because the trace's deliverable is the
  generator + testbench file, not a simulation result.
