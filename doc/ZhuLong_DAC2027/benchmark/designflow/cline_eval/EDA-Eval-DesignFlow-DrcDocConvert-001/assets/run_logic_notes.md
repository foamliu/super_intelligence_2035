# DRC Connect QA Tool - Run Logic and Check Method

Analyzed files (read only, nothing was executed):
- connectivity/run.py        main script, 537 lines, python3.7, needs gdspy + calibre
- connectivity/config        top level config template (ruleType = LVS)
- connectivity/ERC/config    ERC variant
- connectivity/LVS/config    LVS variant
- connectivity/LPE/config    LPE variant

## 1. Purpose

QA harness for the CONNECT part of a real Calibre rule deck (LVS / ERC / LPE).

The tool builds a synthetic GDS full of connectivity patterns with KNOWN
answers, runs calibre twice on it with the real rule deck, extracts the net
id of every marker shape, then filters the results so that only WRONG
answers survive.

- sameNet cell: two markers per pattern that MUST land on the same net.
  Leftover results = missing connectivity (OPEN). Typical cause: a purpose
  variant (CMP / SL / MATCH / CLOSE) that the rule deck forgot to CONNECT
  into its layer net.
- diffNet cell: two markers per pattern that MUST stay on different nets.
  Leftover results = unwanted connectivity (SHORT). Typical cause: CONNECT
  statements or layer definitions that are too broad.

Empty processed RDB files means the rule deck passed this QA.

## 2. Invocation and config

    python run.py <config_file>      # exactly one argument

The config file is python code; run.py exec()s it (lines 451-456).

    rulePath       real rule deck included by the generated connect.drc
    ruleType       LVS / ERC / ANT. Only used by the ANT special case in
                   are_layers_connected (via distance 2 instead of 1)
    topCell        name of the generated GDS and of the output RDB suffix
    connectivity   stack graph. 3 items: [lower, via, upper]; 2 items:
                   direct link. Direction matters: edges are followed only
                   from edge[0].
    conn_layers    per layer list of purposes. First entry = main drawing
                   purpose, the rest are variants that each get a probe.
    bottomLayer    start nodes of path enumeration, e.g. [PG] or [PG, AT4]
    connectOPC011  verbatim calibre lines that tie the marker layer to real
                   conductive layers, e.g. CONNECT OPC011 PGnet
    precision      dbu per micron for gdspy and the RDB header (4000)
    markLayer      GDS layer of the markers (10000, becomes OPC011)

## 3. Stage 1 - build the test GDS (connectivityCheck.gds)

find_all_paths (line 48) is a recursive DFS over the connectivity graph
started at every bottomLayer entry (getPaths, line 77). Via layers are kept
in the path. Dead ends terminate a path. LVS config example:

    PG -> PC2 -> M0C -> PCU -> M0U -> CT -> M1 -> V1 -> M2 -> ... -> M8 -> HSV -> HSP

Two cells are created: sameNet (cell1) and diffNet (cell2). genTotal places
one pattern column per path/layer/purpose; genPattern draws two stack
columns with markers on markLayer 10000. Markers always overlap the bottom
stack layer, so each marker inherits the net of its own stack through the
CONNECT OPC011 lines of the config.

## 4. Stage 2 - generate connect.drc and run calibre twice

create_connect_file (line 415) writes connect.drc:

    #! tvf
    tvf::VERBATIM {
        DRC RESULTS DATABASE  "AAAAA.drc.results"  ASCII
        LAYOUT PATH    "./<topCell>.gds"
        LAYOUT PRIMARY "diffNet"
        include "<rulePath>"
        LAYER OPC011 10000
        <connectOPC011 lines verbatim>
        drc select check test
        test{
            opcid = DFM PROPERTY OPC011 [netidnum = NETID(OPC011,1)]
            DFM RDB opcid "diffNet.rdb"
        }
    }

NETID(OPC011,1) reports, per marker shape, the id of the net the marker
belongs to after the CONNECT statements are applied.

update_connect_file (line 365) patches connect.drc in place: the DFM RDB
opcid line -> target rdb file name; the LAYOUT PRIMARY line -> sameNet or
diffNet (the cell under test).

Run flow (lines 526-529):
    update_connect_file("sameNet.rdb")  then  calibre -drc -hier -turbo connect.drc
    update_connect_file("diffNet.rdb")  then  calibre -drc -hier -turbo connect.drc

Risk: the os.system return codes are never checked, so a missing calibre
binary or a broken rule deck fails silently.

## 5. Stage 3 - RDB post processing (the actual verdict)

main (line 388) + process_net_file (line 198) rewrite the raw calibre RDBs.
The script counts how many groups carry each netidnum value, then drops
every group whose netidnum count equals target_count:

    file name contains same -> target_count = 2  (drops CORRECT pairs)
    file name contains diff -> target_count = 1  (drops CORRECT singles)

What survives is exactly the WRONG answers:
    sameNet_<topCell>.rdb : markers on different nets  -> OPEN suspects
    diffNet_<topCell>.rdb : markers on the same net    -> SHORT suspects

Cleanup (line 537): rm -rf AAAAA* diffNet.rdb sameNet.rdb deletes the raw
RDBs and the AAAAA results/summary; the processed RDBs and the GDS remain.

## 6. Outputs and how to judge them

Per run directory (confirmed in ERC/):
    connectivityCheck.gds        generated patterns
    connect.drc                  generated deck, left in diffNet state
    sameNet_<topCell>.rdb        OPEN suspects;  header only = pass
    diffNet_<topCell>.rdb        SHORT suspects; header only = pass
    AAAAA.drc.results / summary  deleted by the cleanup step

Historical ERC outputs confirm the flow: both processed RDBs contain only
the 5 header lines (calibre had reported 716 and 3634 raw results, all
filtered out), so that run found no wrong answers. An empty RDB means
"config scope passed", not "the CONNECT section is correct".

## 7. Quirks and risks

    1. exec() on the config: the config is arbitrary python code.
    2. calibre failures are silent (os.system status never checked).
    3. bad2 patterns are generated once, hard coded to path index i == 1.
    4. Pattern coordinates are micron; precision 4000 means 0.25 nm dbu in
       the GDS and 4000 dbu per micron in the RDB header.

## 8. Verdict

The tool is a targeted consistency sampler over the stack paths declared in
the config. Inside that scope it reliably catches missing purpose
connectivity and unwanted cross layer CONNECT, and the historical ERC / LVS
/ LPE runs passed clean. But the rule deck connects far more than the config
declares, so an empty RDB means "config scope passed", not "the CONNECT
section is correct".
