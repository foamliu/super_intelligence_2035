# Deepread: 8orer — schematic hierarchy copy-plan generator

## Trace
- session: `1790236124444_8orer` (lvyy @ hfeg0pkn002, mc165)
- tool signature: schematic 448 / netlist 381 / cellview 327 / pyAether 156 / hspice 12 dominant
- storage: directory-based `/home/lvyy/.cline/data/sessions/1790236124444_8orer/1790236124444_8orer.messages.json` (693 KB)
- ledger status: parked in shard C (layout_aether, note "schematic domain: UI#135 ... belongs schematic_netlist shard D"); parked in shard D shallowly (skill-load note on U#0). Re-claimed by D in #355 via mark (case line added, parked lines kept).

## User turns (7)
- U#0 "skilldev" — skill development context
- U#1 "你现在里面有skill吗" — capability probe
- U#2 "在这个路径下/proj/m2701/V0_DDR4/workdir/haojianh/sim_LP6/dejoa/CA新建文件夹try" — setup
- U#3 "你能做什么呀，你能抽网表吗" — capability probe
- U#4 "你能自己修改电路，然后抽网表，然后跑仿真，然后根据仿真结果再进行电路修改吗" — capability probe
- **U#5** "把这个电路复制 /proj/m2701/V0_DDR4/workdir/lvyy/A_lvyy_lp6_37/CkIbDiffM6 到新的library，你自己在/proj/m2701/V0_DDR4/workdir/lvyy/新建一个叫A_lvyy_lp6_AI的library，把CkIbDiffM6电路复制过去，相关的子电路也都复制过去" — **real produce task**: schematic hierarchy copy with subcircuit closure
- U#6 "能直接你给我复制完吗" — ask to complete the copy directly

## Assistant approach (tool_use counts: 22 list_allowed_files / 21 run_approved_command / 19 editor / 17 RAG search_apis / 6 read_files / 5 get_api_details / 3 search_codebase)
- M136: list_allowed_files on /proj/m2701/V0_DDR4/workdir/lvyy + A_lvyy_lp6_37 (depth 2) → discovered sibling cells (bias_opamp_wckIb, ckbias_Res, CKBiasTopM6, CKCMLBiasM6, ...)
- M139-143: list_allowed_files + read_files on CkIbDiffM6/schematic (cdsinfo.tag, cds.lib, sch.hist) → confirmed Empyrean Aether OA-format library
- M144-149: RAG search "copy cell library across libraries cellCopy" / "cell copy subcells hierarchy copyCellToLib" → found aeCopyCell (similarity 0.66-0.68); get_api_details on aeCopyCell/dbCopyCellView/dbCopyCV/aeCopyLib/dmGuiCopy/dbNewCellView
- M150-151: RAG search "create library dbCreateLib" → found dbCreateLib (similarity 0.87)
- M153: editor wrote create_lib_and_copy.sh (mkdir A_lvyy_lp6_AI + cdsinfo.tag + cds.lib DEFINE entry) → run_approved_command RC=0
- M157-159: RAG search "get instances list hierarchy subcell reference" → found aeGetInstHier
- M160-163: editor wrote copy_CkIbDiffM6_v2.py (pyAether emyInitAether -ADV + aeCopyCell recursive subcircuit copy) + usage instructions (Aether Python Console)
- M166-170: user wanted direct file-system copy → editor wrote copy_direct.sh (cp -r 20 cells: CkIbDiffM6/bias_opamp_wckIb/ckbias_Res/CKBiasTopM6/CKCMLBiasM6/...) → run_approved_command RC=0 → M170 reminder: OA database internal lib-name still records old lib (cp -r doesn't update .oa internal refs)

## A-faithful feasibility
- INFEASIBLE: /proj/m2701/V0_DDR4/workdir/lvyy/* is lvyy-private (e0031982 cannot access); live Aether OA database copy is not portable; the OA internal-lib-name issue means even a file copy isn't a correct schematic copy.
- → B-grade synthesized: extract the offline-verifiable "plan" facet (closure + order + library scaffolding).

## Synthesized facet: schematic hierarchy copy-plan generator
- generator: `gen_sch_copy_plan.py --spec <spec.json> --outdir <dir>`
- spec schema: {source_lib, dest_lib, root_cell, cells: {cell: [subcells]}}
- computes:
  1. transitive subcircuit closure (BFS from root; referenced names not in cells dict = external primitives, excluded)
  2. depth (min distance from root, root=0)
  3. depends_on (direct subcells in closure, sorted)
  4. cycle detection (iterative DFS gray-flag)
  5. topological copy order (Kahn's algorithm, alphabetical tie-break; cyclic → copy_order=-1)
  6. library_setup (cdsinfo_tag + cds_lib_entry "DEFINE <dest_lib> /lib/path/<dest_lib>")
- outputs: copy_plan.json (7 top-level keys) + report.md (4 sections)

## Anti-hardcode (A vs B vs B2)
- A (spec_A.json): CkIbDiffM6 / A_lvyy_lp6_37 → A_lvyy_lp6_AI, 5-cell closure, depth 2, acyclic
- B (spec_B.json): AmpTopM3 / AmpLib_v2 → AmpLib_AI, 6-cell closure, depth 2, acyclic, **vdd_pad external primitive must be excluded**
- B2 (spec_B2.json): PllLoop / PllLib_v1 → PllLib_AI, 4-cell closure, **cyclic** (pfd_cp→lf_stage→vco_div→pfd_cp), has_cycle=true, copy_order=-1
- A_literals (forbidden in candidate source incl. comments): CkIbDiffM6, A_lvyy_lp6_37, A_lvyy_lp6_AI, bias_opamp_wckIb, CKBiasTopM6, CKCMLBiasM6, ckbias_Res

## Check: 16 conditions a-p
a zip+py_compile / b B-run two files / c 7 keys / d B source/dest/root / e n_cells==6(vdd_pad excluded) / f has_cycle==false / g root in closure / h closure set equality / i topo order valid / j copy_order permutation 0..n-1 / k 4 fields types / l depth correct / m library_setup / n report 4 sections / o anti-hardcode(source no A token + A-run + B2-run cycle) / p 3x sha256

## Self-verify
- ref PASS 16/16
- 5 negatives all FAIL at distinct first_fail: empty_shell→(b), hardcode_a→(d), print_expected→(o), ref_core_deleted→(e), naive_stub→(i)
- §4.9 three fakes (empty/print_expected/ref_core_deleted) all FAIL
- 3x sha256 deterministic (cb513ce8618fdf971b1b41961b03273aa9b10a59141e8c047bfdb95670b8af2f)
- assertion gate: k_rationale = k_check = 16 ✓

## Lessons
1. Cross-share parked-with-D-note trace (4th example after #331/#332/#333): 8orer was parked in C with explicit "belongs schematic_netlist shard D" note but no case built; D takes the schematic hierarchy copy facet; mark adds a case line in D.tsv while keeping the parked lines.
2. dependency closure + topological sort + cycle detection is a strong schematic_netlist L1 verifiable facet — 16 conditions naturally rich (counts / set equality / topo validity / permutation / depth / cross-input / determinism), distinct from CdlNetlistGen (CDL text) / FFLatchExtract (feedback loops) / LvsMrcBrknetDiag (LVS report).
3. External-primitive exclusion (B's vdd_pad referenced but not in cells dict) is a strong anti-hardcode axis — a naive generator that includes all referenced names fails (h).
4. B2 cyclic hierarchy is a strong anti-hardcode axis — a generator that doesn't detect cycles fails (o); copy_order=-1 when cyclic is the sound design (Kahn has no ready node).
5. mc>=15 fresh-vs-all D-domain pool is fully exhausted (0 fresh); next rounds must cross-share or wait for a new scan.
6. L1/L2 ratio debt persists (13 rounds): this case is also L1 (static closure computation, no live Aether); the structural scarcity of clean L2 produce in the fresh pool remains.
