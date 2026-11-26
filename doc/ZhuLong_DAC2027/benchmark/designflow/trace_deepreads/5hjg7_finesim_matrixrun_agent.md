# Deepread: 5hjg7 — FinesimMatrixrunAgent (zjqiao @ hfhds201)

## Trace
- session: `1793243267055_5hjg7.messages.json` (hfhds201 local, 2.0MB, 612 msgs)
- user: zjqiao
- tools: editor×111, read_files×105, run_approved_command×65, list_allowed_files×10, SandBox_MCP_Server__run_code×3, search_codebase×2, run_commands×1, skills×1
- claim: 2026-11-07 11:3x, mc=612, domain=spice_sim
- source path: `/home/zjqiao/.cline/data/sessions/1793243267055_5hjg7/`

## USER#0 (verbatim, A-档 task statement)
> 这个代码是我进行finesim仿真的代码，现在我希望你能创建一个agent，在用户说明激励文件和网表文件以后，你看可以启动该程序，将激励文件填入激励文件的位置，然后选择网表，再点击运行仿真，你可以做到吗

Attached: `stimulus_manager.py` (137787 bytes, self-contained ASCII-only Tkinter GUI bundle; embeds `stimulus_manager/fields`, `config`, `export`, `ui/main_window` etc. as `\u`-escaped strings reconstructed at runtime).

**A-档 clean-check**: pure request round — gives goal (create automation agent) + method (fill stimulus / select netlist / run sim). No root cause, no fix. ✓

## Assistant flow (real tool products)
1. Read `stimulus_manager.py`, extracted the embedded `__BUNDLE__` modules (8 modules) via `extract_bundle.py` / `analyze_bundle.py` helper scripts; wrote `main_window` source to `/tmp/main_window_src.txt`.
2. Studied `_run_auto_all`, `_run_vecgen`, `_run_matrixrun`, `_build_matrixrun_cmd` to understand the end-to-end finesim sim flow.
3. Built CLI agent `extract_bundle.py` (headless, replaces Tkinter GUI) — persisted settings via same `config.json`, built the `matrixrun` command directly.
4. Many editor struggles (path validation, 6000-char limit) → rewrote in pieces; verified via `run_approved_command` (python-runner) dry-runs repeatedly.
5. Final verified dry-run (msg#576, clean state):
```
[INFO] Config: /home/zjqiao/config.json
[DRY-RUN] matrixrun command:
  $ matrixrun -p drvqa -v V0 -f /tmp/clean.saved -nr Netlist_Vcap_20261103PM_Fullchip -nl netlist -i 8 -q fqueue3_drvqa -s primesim -Y 2025 -array -tdv -c control.finesim_promd_vcap -wica
Pass --no-dry-run to execute.
```

## Gold-standard command structure (build_matrixrun_cmd)
`matrixrun -p <project> -v <version> -f <stim_file> -nr <netlist> -nl netlist -i <cpu> -q <queue> -s <simulator> -Y <simver> -array -tdv -c <control> -wica`

Defaults (from extract_bundle.py):
- DEFAULT_PROJECT=drvqa, DEFAULT_VERSION=V0, DEFAULT_SIMULATOR=primesim, DEFAULT_SIMVER=2025, DEFAULT_CPU=4, DEFAULT_NETLIST_NAME=netlist, DEFAULT_MATRIXRUN=matrixrun
- queue: from config (observed fqueue3_drvqa = fqueue3_<project>)
- control: from config (observed control.finesim_promd_vcap)
- always-on flags: -array -tdv -wica (opt_array/opt_tdv true in config)
- required: stim_file (-f), netlist (-nr) — error to stderr + return None if missing

CLI args (argparse): --stim-file/-f, --netlist/-nr, --queue/-q, --control/-c, --project/-p, --version/-v, --simulator/-s, --simver/-Y, --cpu/-i, --config, --dry-run/-n, --no-dry-run, --list-netlists, --wait-netlist, --topjob, --gui

## Case synthesized
- **EDA-Eval-DesignFlow-FinesimMatrixrunAgent-001** (spice_sim, A-faithful, L1)
- Deliverable: `sim_agent.py` CLI that builds + dry-run-prints the matrixrun command
- A (visible): stim=/tmp/clean.saved, net=Netlist_Vcap_20261103PM_Fullchip, project=drvqa, cpu=8
- B (hidden): stim=/probe/probe_stim_20261107.saved, net=Netlist_Probe_20261107PM_Fullchip, project=probeproj, cpu=6
- A≠B ✓ (different stim/netlist/project/cpu)
- reference: sim_agent_ref.py + check.py (k=19 conds a-s) + 3 negatives (empty_stub/hardcode_A/wrong_flags)
- self-verify: REF PASS on B, 3 negs FAIL, §4.9 trio (empty/hardcode-B/ref-core-deleted) all FAIL
- assertion gate: k_rationale=k_check=19 ≥ 8 ✓
- asset: real stimulus_manager.py (137787 bytes,原文)
