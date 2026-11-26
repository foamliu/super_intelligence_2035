# r698 deepread: 7hv1e xrun CUVMUR diagnose

## Trace: 1793172663300_7hv1e (ruisongs@hfeg0pfn087, digital, mc41)

### User intent (verbatim)
U#0: `/rundata/drvqa/V0/simdir/verilog/ruisongs/array_test/verilog.ddr5.drvqa.1026net/build_file/noregression.x8，分析log，error怎么导致的`

### Agent analysis (30 msgs)
1. list_allowed_files → build_noregression.x8/ contains xrun.log, invoke_failure, verilogrun, A_Pattern_Sim.v, etc.
2. read xrun.log (94720+ lines) → search for *E, errors
3. read invoke_failure → xmelab step FAILED
4. xrun.log tail → xmelab: *E,CUVMUR ... of design unit 'R_RaLvlX1_0903' is unresolved
5. Created analyze_1028_x8.py → ran on ruisongs' machine:
   - CUVMUR count: 26880 (all R_RaLvlX1_0903)
   - other codes: W,MSIDFN:1, W,CUVWSI:56, W,CUVWSB:327, W,CUVWSP:7
   - netlist: R_RaLvlX1_0903 DEFINED at line 651055
   - neighbors: R_RaLvlX1_0902/0904/0/R_RaLvlX1 all NOT defined (0)
   - worklib: no "module worklib.R_RaLvlX1_0903" in xrun.log (never compiled)
6. Root cause: module defined in netlist but never compiled into worklib → 26880 CUVMUR → ELBERR

### Case synthesis (B-synthesized, A档不可行: /rundata permission denied)
- case_id: EDA-Eval-DesignFlow-XrunCuvmurDiagnose-001
- domain: digital, track: C-A, level: L2, k=12
- A assets: build_noregression.x8/ (xrun.log excerpt 50 CUVMUR + invoke_failure + verilogrun + netlist with module at line 200)
- B hidden: R_RaLvlX2_1407, CUVMUR=40, netlist line=300, different warnings (anti-hardcode, ≥4 dims differ)
- Deliverable: analyze_xrun_error.py (general log analysis script)
- check: 12 conditions a-l, runs SUT script on B, asserts B-specific values + anti-hardcode
- Self-verify: ref PASS + 4 neg FAIL + §4.9 three fakes FAIL + e2e PASS
