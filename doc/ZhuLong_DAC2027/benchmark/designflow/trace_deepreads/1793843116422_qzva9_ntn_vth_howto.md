# Deep-read: 1793843116422_qzva9 (thqu @ hfeahpc503 / 10.129.8.231)

- mc=253, domain=spice_sim, 355 msgs (185 user / 170 assistant), ~2.0 MB
- Revived from pool_reaudit_B.tsv (旧判 parked "consultation-dominant ntn vth how-to-check" → 新判 可造 per 2026-11-15 令: how-to Q&A is a valid task form)

## Real user intent (trace-faithful, multi-turn)

1. [0] `TECHLIB库中ntn管子的阈值电压这些要怎么查看` — how to view ntn (native NMOS) Vth in TECHLIB
2. [28] `你找一下spice model在哪里` — locate the SPICE model
3. [75] `打开这个xlsx文件` — open the PDK spec xlsx
4. [103] `怎么仿真这个管子的IV特性曲线呢` — how to simulate IV curve
5. [140] `你能直接帮我仿吗` / [216] `你绘制一下这个IV特性曲线` — run the sim / plot
6. [238] `这个vg的电压是不是太少了…要在途中标注出线性区，截至区饱和区` — more sweep points + annotate regions
7. [324] `如何通过仿真得到管子的阈值电压` — how to extract Vth from sim

## Agent's real tool chain & findings

- ask-eda / search_codebase / read_files (aether-tool-qa KB) — KB not hit
- Found SPICE model: `/apps/imctf/models/G6/model_local/V1_HK_Model_L5_v0d9_Rev02_t02/` ; `current` symlink; `incFile_V1_HKMG` (~50000 lines)
- ntn = `.subckt ntn DRN GATE SRC BULK` + `.MODEL ntn.1 nmos level=77 version=107.0` (BSIM6)
- BSIM6 has NO VTH0; Vth from vfb=-1.0032, k0=0.012643, k2=0.01623, **delvto_ntn=0** (user trim), tox=1.55n, tnom=98
- Typical Vth ~0.3-0.5V (native NMOS, low threshold)
- PDK xlsx `V1_LP_PDK_SPEC_TABLE_v0d9_Rev02_t02.xlsx` 9 sheets: ntn Lmin=0.036µm (36nm), W 0.15-2.0, NF 1-100, temp -40..150, tnom 98
- MDE DC guide: create test schematic (place ntn W=1u L=0.036u), vdc×3 (Vg/Vd/Vs), wire, Setup→Netlist/Directory (Hspice), Setup→Model Library (tt), Stimuli (Vd=0.05 linear / 0.94 sat), Analysis→DC sweep Vg 0→0.94 step 0.01, run, iWave
- 4 Vth extraction methods: 恒流法 Iref=(W/L)*1e-7 (.MEASURE FIND v(g) WHEN i(vd)=Iref RISE=1), max-gm 外推 (Vth=Vg_gmpeak - Id/gm), sqrt(Id) 外推 (饱和区), OP 点 (.OP)
- Regions: cutoff Vgs<Vth, linear Vgs>Vth & Vds<Vgs-Vth, saturation Vgs>Vth & Vds>=Vgs-Vth
- Low-vth caveat: ntn Id@Vg=0 ~3e-11A > 2e-12A, so FALL=1 fails → use RISE=1 or higher Iref

## Synthesized case

`EDA-Eval-DesignFlow-NtnVthHowtoGuide-001` (spice_sim, L1, A-faithful):
- Deliverable: `ntn_vth_howto_guide.py(workdir, out_dir)` parses doc/{query.log, model_card.sp, pdk_spec.json, mde_dc_guide.txt, vth_methods.txt} → `ntn_vth_howto_guide.json` (14 top-level keys)
- A=ntn/NMOS (positive sweep, vfb=-1.0032, delvto_ntn, tox=1.55, Lmin=0.036, Wmax=2.0, default W=1.0/L=0.036)
- hidden B=ptn/PMOS (negative sweep, vfb=0.8856, delvto_ptn, tox=1.62, Lmin=0.050, Wmax=2.5, default W=2.0/L=0.050, kb_hit=hit) — cross-input guard on device_name/type/delvto/geometry/Iref numeric/polarity
- check.py: 14 independent conditions (a-n), subprocess real-run on B, 3-seed determinism, A-leak guard
- k_rationale == k_check == 14 (≥8 ✓)
- Self-verify: REF 14/14 PASS; 4 negatives (empty/print-only/hardcode-A/deleted-core) all FAIL
- ledger mark: 1793843116422_qzva9 → case
