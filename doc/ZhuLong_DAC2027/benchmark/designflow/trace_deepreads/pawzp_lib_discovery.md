# Deepread: pawzp (library/file discovery Q&A)

## Trace info
- Session: 1794215078177_pawzp
- User: zlhou @ hfeg0pkn001 (10.129.2.10)
- mc=33, domain=schematic_netlist (analog_context per ledger, reclassified to schematic_netlist for library/cell discovery)
- 33 msgs / 169KB
- Date: 2026-10-16

## User intent (verbatim)
- U#0: "你可以查看/proj/lacaa/TV1_FS/workdir/zlhou中的文件吗"
- U#5: "有一个库，名为lacaa_2prf_420，你能找到吗"

## Real task
Library/file discovery Q&A: user asks if agent can view files in their workdir, then asks to find a specific library named lacaa_2prf_420. The agent must search through cds.lib, lib.defs, and the libs/ directory to locate the library, then cross-verify with PEX config and netlist.mapping.

## Gold standard (assistant msg#32, user-accepted complete answer)
1. **Library location**: `/proj/lacaa/TV1_FS/libs/lacaa_2prf_420` (Aether/OV library with data.dm)
2. **Search path**: NOT in zlhou's cds.lib, NOT in lib.defs (which has LEAFCELL_ZXQ, LEAFCELL_SPSRAM, LEAFCELL_2PRF_LXX, test_zlh), FOUND in `/proj/lacaa/TV1_FS/libs/` public resource directory
3. **Sibling libraries**: lacaa_2prf, lacaa_2prf_bk (backup), lacaa_spsram, lacaa_sram, etc.
4. **Cross-verification**: PEX config (`lacaa_pex_config.json`) references: "Sch Lib"="lacaa_2prf_420", "Lay Lib"="lacaa_2prf_420", "Lay Cell"="CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS_420"
5. **netlist.mapping** (19222 lines) references lacaa_2prf_420 as library name for cellview pin/instance/net mappings: HC2PFS_INVF3D3, HC2PFS_NAND2_DWBL_CTIO, HC2PFS_ROWDEC, HC2PFS_ND2TO4DECODER
6. **Library contents**: 2P (dual-port) SRAM bitcell/peripheral cells (CH420_HCB2P_bitcell_*_FS, Corner/Edge variants), full SRAM macros (CXN4HC2PS*), layout digital function cells (HC2P_CM*_GUT_420, HC2PFS_A_*), metadata (data.dm)

## Asset reachability
All assets trace-internal (file listings + config file contents in read_files tool_results). Rebuilt via synth_deck mode — no external file access needed.

## Case design
- case_id: EDA-Eval-DesignFlow-LibDiscoveryLacaa2prf420QA-001
- A档 verbatim (U#0 + U#5)
- Asset A: 9 files (workdir_listing, cds_lib, lib_defs, libs_dir_listing, lib_dir_listing, pex_config, netlist_mapping, question, task_brief)
- Hidden B: identifier-renamed (lacaa→macec, 2prf→3prf, 420→640, CXN4HC2PS→CXN3HC2PS, CH420→CH640, zlhou→hzhou, TV1_FS→SV2_FS, etc.)
- candidate_ref.py: CLI `python3 candidate.py <asset_dir>`, parses question to extract library name, searches cds.lib/lib.defs/libs_dir_listing, cross-verifies with pex_config/netlist_mapping, classifies library contents, finds siblings → structured JSON
- check.py: 12 assertions (a-l), k_check=k_rationale=12≥8
- Negatives: 4 (empty, print-only with A-hardcode, core-deleted, naive-stub) — all FAIL with distinct labels
- §4.9 degen: empty/print-only/core-deleted — all FAIL

## Self-verification
- ref: 12/12 PASS
- negatives: 4/4 FAIL (NEG_RC=0)
- degen: 3/3 FAIL
- anti-hardcode: 17 A-forbidden tokens checked, zero leakage into B
- candidate on A: correctly finds lacaa_2prf_420 at /proj/lacaa/TV1_FS/libs/lacaa_2prf_420
