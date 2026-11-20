# Deep-read: 1782784000943_pcb1x (e03179 @ 172.16.8.191) — Pin List Extract

- trace_source: user=e03179, host=172.16.8.191 (hfeg0plg19-cluster IP), session_file=1782784000943_pcb1x.messages.json, mc=31
- domain: schematic_netlist / analog_context (cellview pin extraction via SKILL)
- keywords: cellview:182; schematic:38; virtuoso:22; dbget:22; rtl:8; verilog:4; transistor:2; cadence:2 (current scan 20261116)

## Real task (verbatim, trace U#0)
> 请帮我抓取当前打开的电路中所有的Pin List，并输出到本地当前路径下的一个文本中，使用skill语言实现代码并执行。

= "Grab all Pin List from the currently open circuit, output to a local text file in current path, implement in SKILL language and execute."

## Sandbox env
- SandBox_MCP_Server__run_code, lang=skill, encoding=ascii, workdir /proj/train/AI_Virtuoso/workdir/e0025768
- The sandbox rejects non-ASCII (Chinese comments) — key constraint

## Solution evolution (40 msgs)
1. RAG search → schSchemToPinList, geGetEditCellView, dbGetOpenCellViews, geGetEditRep, lmPrintTerm
2. msg[17] first SKILL (Chinese comments) → ERROR "Code contains non-ASCII characters"
3. msg[19] ASCII-only SKILL (getAllPins procedure): geGetEditCellView → fallback getCurrentWindow/geGetWindowCellView → fallback dbGetOpenCellViews; schGetPinOrder for pin list; cv~>terminals for detailed term info (name/direction/ioType/pins); schSchemToPinList/schSymbolToPinList for full pin list; outfile+fprintf+close to ./pin_list.txt → SUCCESS
4. msg[20] result: Current CellView: TECHLIB/MarkSVP/schematic, Total pins: 1 (pin "A"), written to /proj/train/AI_Virtuoso/workdir/e0025768/pin_list.txt (496 bytes)
5. msg[21-38] user wanted LOCAL path; assistant struggled to read back file (infile 2-arg error, gets returning nil, readc undefined, read SYNTAX ERROR) — file existed (fileLength 496) but SKILL text-read APIs misbehaved
6. msg[39] final fix: outfile "/home/e0025768/devops/bundle/pin_list.txt" + geGetEditCellView + schGetPinOrder + fprintf → SUCCESS, "File written to /home/e0025768/devops/bundle/pin_list.txt, Total pins: 1"

## Canonical correct SKILL (msg[39], the essence)
```skill
(let ((outPort (outfile "/home/e0025768/devops/bundle/pin_list.txt" "w"))
      (cv (geGetEditCellView))
      (pinList nil))
  (unless outPort (printf "ERROR: Cannot open local file for writing\n") (return))
  (unless cv (printf "ERROR: No cellview open\n") (close outPort) (return))
  (setq pinList (schGetPinOrder cv))
  (fprintf outPort "Pin List Report\n================\n")
  (fprintf outPort "CellView: %s/%s/%s\n" (getq cv libName) (getq cv cellName) (getq cv viewName))
  (when pinList
    (fprintf outPort "--- Pin List ---\nTotal pins: %d\n\n" (length pinList))
    (let ((i 0)) (foreach pin pinList (setq i (add1 i)) (fprintf outPort "  %d. %s\n" i pin))))
  (close outPort))
```

## Key APIs (the D-domain knowledge)
- geGetEditCellView() — current edited cellview (aliases: geGetEditRep)
- schGetPinOrder(cv) — ordered pin list from schematic cellview
- cv~>terminals — terminal objects; term~>name/~>direction/~>ioType/~>pins
- schSchemToPinList / schSymbolToPinList — full pin list by view type
- dbGetOpenCellViews — all open cellviews (fallback)
- outfile/fprintf/close — file write; gets/infile — text read (fragile)

## Errors observed (negative-test fodder)
- non-ASCII comments → sandbox reject
- infile 2-arg ("path" "r") → "too many arguments (1 expected, 2 given)"
- gets on text file → nil; close on nil → "argument #1 should be an I/O port - nil"
- readc → undefined function
- read on plain text → SYNTAX ERROR

## Case design decision (r850)
Self-contained Python reframe (synth_deck-style, sandbox-free, like PinListExtract-001 / AetherPartialNetlistExtractQA): model the cellview as a JSON snapshot {cellview, pinOrder, terminals[{name,direction,ioType,pins}]}; SUT writes pin_extract.py that loads it, extracts pin_order + terminal metadata (name/direction/ioType/n_pins) + direction classification (input/output/inout counts) + duplicate-pin detection, writes pin_list.txt + JSON report. Hidden B = different cellview (sense_amp) with mixed directions + a duplicate pin. check.py runs candidate on B, 12 assertions, anti-hardcode vs A-only tokens (TECHLIB/MarkSVP/ctrl_a/ctrl_b/data_io/clk_in), 3 degenerate FAILs + 2 negative FAILs, 3-seed determinism. Distinct from PinListExtract-001 (SPICE .sp parsing) — this is cellview-JSON terminal extraction.
