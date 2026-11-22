# r996 deepread: qzx4z — vsim framework analyze (LPDDR6 testcase creation Q&A)

## Trace source
- session: 1795055693165_qzx4z (sfeng@hfeg0pkn005, mc73, verilog:1172 dominant, A-pure verification)
- scp from .75 → hfeg0pkn005:/home/sfeng/.cline/data/sessions/1795055693165_qzx4z/1795055693165_qzx4z.messages.json
- 475KB / 37 msgs / 1 clean user turn

## User intent (verbatim, msg#0)
> analyze directory: /proj/dejoa/V0/simdir/verilog/sfeng/lp6_final/
> refer to sim script under bin/vsim
> if I want to create a new testcase, what should I do?

## Session main line
LPDDR6 (dejoa/V0) verification platform structure analysis. User asks how to create a new testcase.
Assistant walks the framework: bin/vsim (perl entry), Regressions/ (.run/.inc/.def), patterns/, A_Pattern_Sim.v, lpddr6_test.sv, config/tbconfig. Delivers structured explanation + concrete steps + run command.

## Trace gold (msg#36 assistant final)
Framework structure:
- **Entry**: `bin/vsim` (perl), driven by `Regressions/<name>.run`
- **3 regression file types**:
  1. `<name>.run` — test body (SV stimulus), copied verbatim → `A_Pattern_Sim.v`
  2. `<name>.inc` — optional `` `include `` list of pattern task files → `Pattern_tasks.v`
  3. `<name>.def` — optional, each `+DEFINE` line = separate sim variant
- **Key vsim flags**: `-p` proj/db, `-a` arch, `-c` create run dir, `-s` run sim, `-r` regression name, `-l` log dir, `-g` seed, `-d` defines, `-b` byte mode, `-q` queue
- **Config** (config/tbconfig): arch=lpddr6, project=dejoa, db=V0, top=LP6TOP, byte=x24
- **Patterns**: `patterns/<group>/<file>.v` defines reusable `task`s
- **Flow**: read .run → A_Pattern_Sim.v; read .inc → Pattern_tasks.v; submit sim job → log/<name>.x24/
- **Run command**: `bin/vsim -p dejoa/V0 -a lpddr6 -s -r my_test -l log -g 42`

## Case synthesis
- **Case ID**: EDA-Eval-DesignFlow-VsimFrameworkAnalyzeProduce-001
- **Domain**: verification (shard A)
- **Archetype**: framework-structure-analyzer produce-task + hidden-B (report-generation)
- **A (visible)**: dejoa/V0 lpddr6 framework files (trace-faithful values)
- **Hidden B**: parallel framework (dscqa/V2 lpddr5) — different script name, config, dir names, test entry
- **ref_solution.py**: <framework_dir> → JSON report (parse entry script, config, regression dir, pattern dir, test entry, testbench, flags, flow, run command)
- **check.py**: ≥8 assertions on B output (B-specific values, anti-hardcode vs A, determinism, §4.9 anti-degradation)
- **Negatives**: 3 fakes (empty/print-only/core-deleted) all FAIL

## Selection notes
- r996 mc≥5 pool (shard_mc.A=5, scan 20261122_172249 4.6x扩池后 r995)
- A-pure filter (a>c, a>bd, a>=10, mc≥5): 2146 cands → 766 unique → 78 fresh (× 4124 ledgered sids)
- qzx4z (sfeng mc73 verilog:1172 A-pure, NEW user, fast host hfeg0pkn005) selected
- No intent-dup: sfeng is a new user, no prior cases
