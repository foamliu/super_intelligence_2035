# Deepread · 85qew · qinqinl@hfeg0pkn001 (10.129.2.12) · mc=25

## Trace source
- session_file: `1793243276846_85qew.messages.json`
- user: qinqinl, host: 10.129.2.12 (hfeg0pkn001)
- mc=25, keywords: pex:378;netlist:10;lib.defs:3;aether:3;.gds:3;.cdl:3;synopsys:1;schematic:1
- 45 messages, single-turn produce-task + agent self-iteration

## User intent (verbatim, Turn #0)
```
/proj/ddgoa/V0/ver/pex/rongtaoy/msaq_U_CCR_fBcc_int_0930BK/msaq_U_CCR_fBcc_int.spf.TYP_98_CC
/proj/ddgoa/V0/ver/pex/rongtaoy/msaq_U_CCR_fBcc_int_0930BK/sacap_1027.pl
用第二行的脚本处理第一行的数据， 结果放在本地，对他人的文档只读取不修改
```
- Two paths: (1) SPF data file (DSPF netlist, 53MB), (2) Perl script `sacap_1027.pl`
- Task: use the Perl script to process the SPF data, output results locally, read-only on others' files

## Agent workflow (gold standard)
1. **Read sacap_1027.pl** to understand CLI interface:
   - Usage: `sacap_1027.pl -spf <spf_file> -o <output_csv> -num <group_size> [-sig 'sig1 sig2'] [-debug YES/NO]`
   - Script writes `gpmap.txt`, `gpcontain.txt`, `cap.log` to cwd (must run in local dir)
   - Depends on `CXMT::Common` Perl module
2. **Determine `-num` parameter** (the key challenge):
   - Analyzed SPF structure: cn columns cn00-cn15 (16 cols) × bla/blb, cec columns cec00-cec01 (2 cols)
   - Cross-referenced existing `gpcontain.txt` (from prior run by rongtaoy): each group has **6 nets**
     - `cnXXbla<N>` (external pin), `cnXXblb<N>` (external pin)
     - `XI_....Bla_local<N>` (local net), `XI_....Blb_local<N>` (local net)
     - `XI_....SaBla<N>` (sa net), `XI_....SaBlb<N>` (sa net)
   - Group number formula: `cn×256+n` for cn groups, `+320 offset` for cec groups (v1.7a)
   - Total **4416 groups** (4096 cn + 320 cec), 26496 group-net pairs
3. **Run script in local dir** `/home/qinqinl/sacap_run/`:
   ```bash
   cd /home/qinqinl/sacap_run
   perl /proj/ddgoa/.../sacap_1027.pl \
     -spf /proj/ddgoa/.../msaq_U_CCR_fBcc_int.spf.TYP_98_CC \
     -o msaq_U_CCR_fBcc_int_TYP_98_CC_cap_summary.csv \
     -num 6 -debug NO
   ```
   - exitCode 0, stderr "uninitialized value at line 173" (non-fatal, NCS/PCS empty for this corner)
4. **Verify output**:
   - CSV: 31.6 MB, 274371 lines
   - Header: `,BL0,BL1,...` (x-axis BL group numbers)
   - y-axis rows: NCS, PCS, NCSGate, PCSGate, Bla, Blb, total_BL2BL
   - Per-group detail: Net1, Net2, Cap(fF), noise columns
   - Local `gpcontain.txt` vs owner's: 26496 pairs content-identical (only Perl hash order differs)
   - Owner's dir unchanged (read-only compliance verified)

## Key deliverables (what user accepted)
- `msaq_U_CCR_fBcc_int_TYP_98_CC_cap_summary.csv` (31.6 MB) — main result
- `gpmap.txt` (1.7 MB), `gpcontain.txt` (2.1 MB), `cap.log` (122 MB) — script byproducts
- `run_sacap.sh` — reproducible run script

## Domain & case classification
- domain: `analog_context` (post-PEX cap coupling analysis from DSPF netlist)
- Similar to #546 CslBlCouplingExtract (also pex/sacap) but DIFFERENT mechanism:
  - #546: parse existing sacap CSV → extract CSL↔BL edges → output edge list
  - This case: parse DSPF SPF → group BL nets → compute cap couplings → output summary CSV (the *generation* step, not post-parse)
- L1 (offline Python re-implementation, no EDA tool runtime)

## Case design: SacapBlCouplingSummary-001
- **A (visible)**: synthetic DSPF `sample_A.spf` (small, 2 cn cols × 4 bits + 1 cec col × 2 bits = 10 groups × 6 nets = 60 nets) + task_brief describing CSV output format + net naming convention
- **B (hidden)**: `sample_B.spf` (4 cn cols × 3 bits + 1 cec col × 2 bits = 14 groups, different group count)
- **C (embedded in check.py)**: `sample_C.spf` (2 dn cols × 5 bits = 10 groups, different column prefix `dn` instead of `cn`)
- **SUT task**: write Python script that (1) parses DSPF net, (2) identifies BL net groups by name pattern, (3) derives group_size from data, (4) sums cap couplings within each group, (5) outputs CSV
- **Anti-hardcoding**: A/B/C have different column prefixes (cn vs dn), group counts (10/14/10), bit ranges — SUT must generalize
- **check.py**: 16 conditions, independently computes oracle CSV, compares structure + values
