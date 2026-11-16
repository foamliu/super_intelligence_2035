# r645 deepread: jie23z @ hfeg0pkn002 / 751rt (physical_verify, mc106)

**session**: 1794463125342_751rt (subdir layout, 145 msgs, 773KB, 8 real user turns)
**user**: jie23z (new, not in known clusters)
**scan**: drc:278;calibre:110;cmos:75;analog:18;.gds:9;gdsii:4;pdk:1
**host**: 10.129.2.11 (hfeg0pkn002)
**access**: .ant files in /proj/degpa/V0_CMOS/workdir/jie23z/GL22/ — Permission denied for e0031982 (owned by jie23z). Agent read them via jie23z's own session.

## User intent (逐字)

- UI#0: `/proj/degpa/V0_CMOS/workdir/jie23z/GL22/T7.ant这是参考开发文件` + `/proj/degpa/V0_CMOS/workdir/jie23z/GL22/GL22_4x3y1z.ant这是我的文件，两个区别在哪？`
- UI#1: `Maximum area ratio of Mx or My to upper VlAy in the same net connects to gate with area > 10700um2, and does not connect to AT4]. 找出T7.ant中与上述相似的rule`
- UI#2: pastes VIA3.R.13.2 rule block (NET AREA RATIO IO_GATE...)
- UI#3: `Cumulative Mn top area (n=1~ Top METAL) that cumulatively connected to the gate area (1.0E3 um2 <= gate area <= 3.0E5 um2) 找出T7.ant中与上述相似的rule`
- UI#4: `Ratio of cumulative DNW area to ((NMOS/PCAP core gates) outside DNW)... 找出T7.ant与之相似的rule`
- UI#5: `@ Maximum cumulative area ratio of DNW [area >= ^DNW_R_7_1_A um2]... 这什么意思？详细朴实的语言告诉我`
- UI#6: `!!AREA(RDL_DIO)是什么用法`
- UI#7: `RDL_DIO = NET AREA RATIO RDL DIO >0是什么用法`

## Gold (agent delivered)

### ASST#28 (file comparison)
T7.ant (TSMC 7nm FinFET, CLN7FF_16M_1X3Xa1Ya8Y2Z, 1P16M, 15125 lines, SVRF encrypted #DECRYPT, PRECISION 20000, M1-M16/APi/RDL/CBi layers) vs GL22_4x3y1z.ant (GlobalFoundries 22nm, GL22, 1110 lines, plaintext, DIRECTIVE SECTION, #DEFINE TOP_METAL HLP, #DEFINE IO 1.8, AAi/MOX/POi/CTi/M1-M4/T2M*/T4M*/T8M*/HLV/HLP layers, PRECISION 10000). Completely different foundries/nodes — no comparability. Also found GL22_4x3y1z.ant vs calibreANT.rule differ in T8 stack config (T8M1 vs T2M3 top metal).

### ASST#46 (VIAx.R.13 family extraction) — core produce-task gold
Found **VIAx.R.13 rule family** (16 rules, VIA0.R.13 to VIA15.R.13) matching "Maximum area ratio of Mx to upper VIAx... gate area > 10700... does not connect to OD". Each rule structure:
```
VIA<k>.R.13 { @ Maximum area ratio of M<k> to upper VIA<k> in same net {connects to gate with area > 10700 um2, and doesn't connect to OD} ... <= 350000
  NET AREA RATIO M<k> VIA<k> SF_GATE_VIA DF_GATE_VIA GATE_VIA M<k>_DIO > 350000
  [!AREA(M<k>_DIO)*!~((AREA(SF_GATE_VIA)*SF_GATE_FACTOR + AREA(DF_GATE_VIA)*DF_GATE_FACTOR) -10700)*(AREA(M<k>)/AREA(VIA<k>))]
  RDB VIA<k>.R.13.rep M<k> VIA<k> SF_GATE_VIA DF_GATE_VIA BY LAYER
}
```
Full table of 16 rules with line numbers (2626, 2799, 3052, 3386, 3792, 4270, 4820, 5411, 6039, 6704, 7406, 8145, 8921, 9734, 10584, 11469). "AT4" not found in T7.ant (different naming convention).

### T7.ant structure (from agent's grep results)
- 15125 lines, 806471 chars
- #DECRYPT markers at lines 1, 3, 6, 8 (comments), 153, 2516 (actual encrypted sigs)
- Body is readable plaintext after line 2516
- "AREA RATIO": 1778 hits; "10700": 32 hits (lines 2626,2628,2799,2801,3052,3054,...)
- Rule families: VIAx.R.13 (16 rules), A.R.4/A.R.7 (combined), ACC_VIAx (accumulation defs)
- Variables: SF_GATE_FACTOR, DF_GATE_FACTOR, DIO_FACTOR
- Layer pattern: M<k>, VIA<k>, M<k>_DIO, SF_GATE_VIA, DF_GATE_VIA, GATE_VIA, OD

## B档 mock-behavioral grounded-extraction-tool reframe

**deliverable**: `antenna_rule_family_extract.py <deck.ant> <output.json>`
- Parse Calibre SVRF antenna rule deck
- Extract rule blocks matching VIAx.R.13 family pattern (rule_id, line_number, comment, metal_layer, via_layer, threshold_value, gate_area_filter, dio_exclusion, expression, rdb_output)
- Extract deck metadata (precision, total_lines, decrypt_markers, keyword_counts)
- Group rules by family prefix
- Output structured JSON, deterministic (sort_keys)

**asset A**: synthetic T7-style .ant deck (~120 lines) with 8 VIAx.R.13 rules (VIA0-VIA7), threshold 10700, SF/DF_GATE_FACTOR vars
**hidden B**: same structure, 6 VIAx.R.13 rules (VIA0-VIA5), threshold 8500, different layer names (MT0-MT5, V0-V5), different factor var names
**hidden B2**: anti-hardcode variant, 4 VIAx.R.13 rules, threshold 12000, different RDB naming, different gate area filter

**distinct vs r635/r639/r640**: those parse single SVRF DRC/PG rules; this parses an **antenna rule deck** and extracts a **rule family** (multiple related rules with shared pattern, varying by layer index). New sub-type: `svrf-antenna-rule-family-structured-extract`.
