# trace_deepread: e5ulv (e0029495 @ hfeg0plg64, mc10)

trace_source: user=e0029495, host=hfeg0plg64, session=1791955851967_e5ulv.messages.json, match_count=10
keywords: netlist:65 .spi:9 .cdl:2 binary:1

## user intent (U#0 verbatim)
> 解释以下文件的作用：
> [Attached file: script.tar.gz → .../uploads/script.tar.gz]

user uploaded script.tar.gz containing 10 Python scripts (char.py, char_script.py,
config_parser.py, fs_to_dbc.py, gen_std_template.py, genTemplate.py, logger.py,
nano_to_dbc.py, SplitNetlist.py, sdp) and asked to explain what the files do.
keywords=netlist dominant (SplitNetlist / fs_to_dbc / nano_to_dbc / .spi) -> D schematic_netlist.

## assistant behavior
extracted tar, read each script, produced a prose explanation of each script role
(characterization driver, format conversion FS/NanoSpice->DBC, netlist splitter,
template generators, config parser, logger, SDP builder). Real EDA flow utility pack.

## synthesized-reframe (why not raw)
real script.tar.gz lives in user uploads on .75 (binary, user-owned, not reproducible
in sandbox). Reframe faithful to intent: agent delivers a reusable static-analysis
TOOL (analyze_scripts.py) that structurally "explains" any such script pack
(imports/functions/classes/argparse/IO/EDA-keywords per script) -> manifest.json.
This honors "explain file purpose" as a deliverable tool, not a one-off prose answer.

## case design
- A (visible): script_pack_A.tar.gz (10 compact scripts, faithful names/roles)
- hidden B: script_pack_B.tar.gz (8 scripts, names completely disjoint from A)
- check(): 16 assertions a-p; independent _gt_parse re-derives B gold via ast;
  anti-hardcode (zero A-only names in B manifest), 3-seed determinism.
- domain: schematic_netlist (netlist utility scripts).
