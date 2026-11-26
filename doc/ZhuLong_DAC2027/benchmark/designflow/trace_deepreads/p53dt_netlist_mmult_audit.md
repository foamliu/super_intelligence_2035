# Deep-read: p53dt — SPICE netlist m-multiplier audit (147.5 vs 149.5)

- **session**: `1793759635878_p53dt.messages.json`
- **user/host**: rongtaoy @ 10.129.2.10 (mc=223, schematic_netlist)
- **agent**: cline `lead` (deepseek-v4-flash via cxmt-deepseek)
- **TOTAL_MSGS**: 329, USER_TURNS: 20 (real user inputs wrapped in `<user_input mode="act">`)

## U#0 (msg0, verbatim — the produce task)
「我现在需要对netlist进行修改，因此需要你来帮我审核…你帮我看看他这个147.5和149.5的区别体现在哪里，后续我就知道怎么改网表，你也知道如何审核」

Key technical content of U#0:
- target netlist: `…/zzz_DDGOA_SM_Cfringe_sim_7sec_fbcc_spf_v1_config_ALPS/zzz_…_config.netlist`
- hierarchy: `array10Meg_EU_fbcc_spf_v1` → EU has 1184+8 dummy WL → `array0P8Meg_L_fbcc_spf_cfringe_NEW` (0P8=mat size; also 1P6/1P5) → `array1P6Meg_fbcc_spf_cfringe_NEW_spicesimspf` (target, uses spicesimspf not loading) → instance `I_array1P6Meg_fbcc_spf_0`
- two focus instances: `Icell4DLmdl_0` (m-vector `1,149.5,1,149.5,1`) and `I_kcellBLx24BGmdl_fbcc_0` (m-vector `1,147.5,1,147.5,1`)
- inside: `kcellx16Dummdl` / `kcellx96BGmdl_pattern_cfinge_NEW` (x16/x96 BL-related, don't care; focus on `m`)
- each cell has 4 WL internally → expected WL = (1+147.5+1+147.5+1)*4 = 1192 = 1184+8 dummy → 149.5 is "wrong"
- user wants to later modify 147.5, so needs to understand where 147.5 vs 149.5 manifests

## Trace agent toolchain (msg1–msg45, U#0 phase)
1. `get_agent_policy_status` / `list_allowed_files` — policy engine, locate netlist (symlink → `/rundata/ddgoa/V0/simdir/…`)
2. `read_files` (line ranges) — netlist ~45513 logical lines, 104 subckts
3. `editor` write `analyze_netlist.py` (scan/subckt) → `run_approved_command` (python-runner)
4. `editor` write `parse_netlist.py` (full hierarchy parser + m-value analysis) → marker subcommands for `Icell4DLmdl_0`, `I_kcellBLx24BGmdl_fbcc_0`, `array0P8Meg_L…`
5. `editor` write `list_subckts.py` — concise instance summaries (subtype + m=) per subckt
6. `editor` write `scan_m.py` — scan all `147.5`/`149.5` occurrences with subckt context (both `main` and `_for_msaq_spf` netlists identical on these lines)
7. `editor` write `all_m.py` — all distinct m= values + count; dump `kcellx96BGmdl` / `kcellx96BGmdl_pattern_cfinge_NEW` bodies
8. `read_files` (lines 19296–19306) — confirm WL port connections (real WL vs dummy `inh_vwln`)
9. `editor` write `netlist_review.md` — audit report → final answer to U#0

## Key facts discovered (msg24/26/35/36/30)
- **m-vector is the multiset of m= values of the 5 child instances inside each container subckt**:
  - `kcellBLx4BGmdl` (type of `Icell4DLmdl_0`): 5 children `kcellx16Dummdl` with m = {149.5, 1, 1, 149.5, 1} → N=149.5
  - `kcellBLx24BGmdl_fbcc` (uses `kcellx96BGmdl`): 5 children m = {149.5, 1, 1, 149.5, 1} → N=149.5
  - `kcellBLx24BGmdl_fbcc_pattern` (uses `kcellx96BGmdl_pattern_cfinge_NEW`): 5 children m = {147.5, 1, 1, 147.5, 1} → N=147.5
- **m-value distribution** (whole netlist): m=1 (169), m=14 (3), m=17 (3), m=21 (1), m=27 (2), m=32 (2), m=147.5 (4), m=149.5 (4)
- **container children with `m=-`** (kcellx96BGmdl etc.) = no multiplier param (inner 6× kcellx16BGmdl, 4 WL each)
- **WL arithmetic**: each child cell internally exposes 4 WL (Wl<3:0>); container WL = sum(m-vector)×4 = (1+N+1+N+1)×4 = (2N+3)×4 = 8N+12
  - N=147.5 → 8×147.5+12 = 1192 (= 1184 active + 8 dummy) ✓ matches EU budget
  - N=149.5 → 8×149.5+12 = 1208 (16 extra, wrong)
  - diff_N = 2.0, diff_WL = 16
- **149.5 vs 147.5 distinction**: 149.5 used by `kcellx96BGmdl` / `kcellx16Dummdl` (plain model); 147.5 used by `kcellx96BGmdl_pattern_cfinge_NEW` (pattern cfringe model). The "2" = the dummy half-WL accounted differently between the two netlist representations.

## U#1+ (out of scope for this case)
U#1 (msg46) pivots to a DIFFERENT target netlist (`netlist_1184`, 1376+8dummy, RevC-style `VCT_kcellx32mdl`) and a multi-step modification task (arrayPartCP02_R, array1cp_center, array1cp00_cp01, change.log, v1/v2/v3, step3 mesh structure). This is a separate, much larger multi-turn modification flow — not used for this case (would be a separate L2/L3 case).

## Synthesis decision (B-grade)
- Real `/proj` netlists (45513 / 165k lines) are permission-denied / not attachable → **B-grade synthesized**.
- Asset A = synthesized `example_netlist.sp` reproducing the hierarchy shape (14 subckts: VCT leaf → kcellx16 → kcellx96 containers → 3 N-pattern containers `kcellBLx4BGmdl`/`kcellBLx24BGmdl_fbcc`/`kcellBLx24BGmdl_fbcc_pattern` → array0P8/array1P6/array1P5 → array10Meg_EU top) with N1=149.5, N2=147.5 (matching real trace).
- Hidden B = same shape, N1=251.5/N2=247.5, `_revB` suffix on all container/cell names, diff_N=4, diff_WL=32.
- Hidden B2 = N1=77.5/N2=74.5, `_revB2` suffix, diff_N=3, diff_WL=24.
- Deliverable = `netlist_mmult_audit.py` (CLI `<netlist.sp>` → stdout): data-driven parser that auto-detects N-pattern containers {1,1,1,N,N}, computes WL=8N+12, reports the two N values + diff + cell types. Anti-hardcode via A/B/B2 with distinct N values & names.

## Why this trace is a good A-faithful L1 case
- U#0 is a pure "produce an audit" request (user does NOT give root cause or fix) → A-faithful eligible.
- The audit is fully reproducible offline (Python netlist parsing, no EDA tool / license needed) → L1.
- 16 natural check axes: subckt parse / m-distribution / N-pattern detection / per-container N+m-vector / WL arithmetic / diff_N / diff_WL / cell-type association / anti-hardcode A / cross-input B2 / CLI argv / format labels / determinism.
- Hidden B/B2 defeat hardcoded-147.5/149.5 and hardcoded-B stubs (different N values, names, diffs).
