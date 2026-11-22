# Deep-Read: it6n4 — LPDDR5 UVS Regression Submission Script

- **SID**: 1791964914156_it6n4
- **User**: e0039102
- **Host**: hfeg0pkn001 (10.129.2.10)
- **mc**: 134 (verilog:5197; netlist:501; aether:24; analog:15; pt_shell:8; lib.defs:8; .def:7; synopsys:2)
- **Domain**: verification (A) — LPDDR5 Verilog UVS simulation regression
- **Status**: case → EDA-Eval-DesignFlow-VsimRegSubmitProduce-001

## User Intent (verbatim, 3 user_input msgs)

1. (idx 0) `/rundata/ddgoa/V0/simdir/verilog/jason17w/regression/verilog.lpddr5.ddgoa.0812/这个文件夹下找一个提交回归的文件，这个文件提交后产生的log名为log.net0605.0611_UVS_0920`
   → "In this folder, find a regression submission file whose resulting log is named log.net0605.0611_UVS_0920"

2. (idx 8) `./bin/run_vsim_uvs.pl这个路径, 是run_uvs里写的路径`
   → "./bin/run_vsim_uvs.pl is the path written in run_uvs"

3. (idx 85) `./bin/run_vsim_uvs.pl这个文件就是vcim文件，你带我学吧`
   → "This file is a vcim file, teach me to learn it"

## Key Files in Trace

- **run_normal_allconfig_noprobe_xrun_jack_UVS1** (the answer to user #1):
  ```perl
  #!/usr/bin/perl
  system("sleep 5");
  ###-----------------for x16-------------#
  system("./vsim_uvs -sr basiccheck  -d "LPDDR5G    USESDF PWRBC   "  -q bcp_LP1  --ncconfig "+ncnowarn+TRTDECAY +ncnowarn+CSINFI +ncsdf_nocheck_celltype"  -l "log.net0605.0611_UVS_0920" &"); system("sleep 5");
  ```

- **run_normal_allconfig_noprobe_xrun_jack_UVS** (larger variant, 47K chars):
  x16 section with tests: auto, auto_direct, auto_daap, scan_allspeed, basiccheck,
  wrrdfifo, onebank, act1act2, casops, cbt, datacopy — each calling `./vsim_uvs -sr <name> -d "<defines>" --noprobe -q bcp_LP1 --ncconfig "..." -l "log.net0605.0611_UVS_0928_hejian" &` with `system("sleep 5")` between each.
  Also has x8 section with `-b "x8 mrconfig"`.

- **vsim_uvs** (48K chars): Full Perl wrapper using Getopt::Long + Parallel::ForkManager.
  Options: -proj, -arch, -createtb, -byte, -simulation, -regname (-sr), -logname (-l),
  -define (-d), -ncconfig, -queue (-q), -noprobe, -tool, etc.

## Assistant Tool Chain (49 tool calls, 86 msgs)

list_allowed_files → search_codebase → read_files(run_normal_allconfig...UVS1, UVS) →
list_allowed_files(bin/) → run_approved_command(ls run_uvs*) → search_codebase →
read_files(vsim_uvs) → ... extensive searching for run_uvs/run_vsim_uvs.pl reference

## Key Deliverable from Trace

The agent identified `run_normal_allconfig_noprobe_xrun_jack_UVS1` as the file
producing `log.net0605.0611_UVS_0920` (line 7: `-l "log.net0605.0611_UVS_0920"`).

## Synthesized Produce-Task

Since the trace is an analysis/learning task (no gold deliverable produced), I
synthesized a produce-task grounded in the trace domain:

**Task**: Write `gen_regression.py` that reads a JSON regression config and
generates a Perl UVS submission script (`run_regression.pl`).

- **config_A** (visible): x16 tests (auto/auto_direct/auto_daap/scan_allspeed/basiccheck),
  log_tag=UVS_0928_hejian
- **config_B** (hidden): x16 basiccheck (log_tag=UVS_0920, no --noprobe) +
  x8 section (basiccheck/wrrdfifo/onebank/act1act2/casops/cbt/datacopy with -b "x8 mrconfig" --noprobe)

Both configs are trace-faithful: config_A matches the larger UVS file,
config_B matches run_normal_allconfig...UVS1 (the file the user asked about) +
x8 tests from the vsim_uvs script.

**check.py**: 23 assertions including anti-hardcode (A log_tag/test names not in B output),
§4.9 anti-empty/anti-print-only/anti-core-deleted, determinism.
