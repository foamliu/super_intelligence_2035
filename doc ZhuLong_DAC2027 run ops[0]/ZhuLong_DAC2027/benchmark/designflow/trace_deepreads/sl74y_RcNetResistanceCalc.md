# Deepread: sl74y — RcNetResistanceCalc-001

## Trace
- session_file: `1794374509125_sl74y.messages.json`
- user: shanliny @ hfeg0pkn005 (10.129.2.14)
- mc: 34, keywords: netlist:69;transistor:28;pex:23;lvs:9;rtl:5;calibre:3;pdk:2;mosfet:2
- domain: schematic_netlist (PEX-extracted RC netlist analysis)
- 76 msgs / 3 substantive user turns (act mode)

## User Turns
1. IDX 0: "这是一个由几个晶体管和一段rc走线构成的网表，我想问XBKB.XBK_CNT.XXDEC0.SHARE在整个rc net中和底下几个晶体管是什么位置关系？" + simulation question about 200mV voltage on FCK[0] p管 s极
2. IDX 25: **"我希望你能基于该格式的网表写一个能将这根rc连线，net xxx和底下几根晶体管位置关系可视化的一个脚本，同时该脚本同时能够快速估算指定两个点之间的电阻"** ← PRODUCE-TASK
3. IDX 73-74: Feedback on visualization quality (labels overlapping, configurable transistor selection, resolution control) — session ends with feedback

## Assistant Flow (Turn 2)
- Writes `rc_viz_tool.py`: parses PEX netlist format, visualizes RC wire + transistor positions, computes resistance between two nodes
- Key bug found & fixed (IDX 56): **`*|I` lines have leading `(` in node names** — only stripped trailing `)`, not leading `(`, so device-node names don't match resistor-graph names → fixed by stripping both
- Script runs end-to-end successfully, generates PNG visualization, computes resistance
- IDX 65: delivers complete script with usage summary

## Netlist Format (Star-RC/Calibre PEX)
- `*|NET <name> <cap>PF` — net header
- `*|S (name:seg x y)` — physical segment points with coordinates
- `*|I (node inst pin B 0 x y)` — instance pins connected to net (KEY: leading `(` must be stripped)
- `Cc<id> n1 n2 val` — coupling capacitance
- `Cg<id> node 0 val` — ground capacitance
- `R<id> n1 n2 val` — resistance (RC network, 0.0001Ω near-shorts to 106Ω)
- `X<inst> d g s bulk model params` — transistor subcircuit instance
- `v<id> node 0 val` — voltage source

## B-grade Synthesized Reframe
- Original netlist (test.netlist) attached by user, reachable
- Net: XBKB.XBK_CNT.XXDEC0.SHARE, 3 XBC pull-ups (MPM_XBC) + 4 FCK inverter pairs (XINV_FCK[0-3].MIMP0)
- Simplified A netlist preserves format structure with fewer segments
- B netlist: completely different names (CHIP.CTL_BLK.DEC0.SHARE_BUS, XDRV/XBIAS), different RC values
- B2: minimal single-transistor robustness test
- B3: no-transistor pure RC edge case

## Key "Teeth" (Parsing Challenges)
1. Leading `(` in `*|I` and `*|S` node names must be stripped
2. Node name matching between `*|I` instance pins and R-line nodes
3. Transistor X-line parsing: `X<inst> <d> <g> <s> <bulk> <model> params`
4. Effective resistance via nodal analysis (not simple series addition)
5. Transistor classification: XINV_FCK/XDRV → driver, MPM_XBC/XBIAS → bias
