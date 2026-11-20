# Trace deepread — 1794884513364_46pb5 (zhenglu@hfeg0pkn003, mc42, spice_sim)

- host: hfeg0pkn003 = 10.129.2.12; trace 289KB / 90 msgs / 5 user turns; tools: read_files:8, run_approved_command:14, editor:17.
- PDK dir: /home/zhenglu/dtech_spice/hlmc_cl022ul_spice/ (CXMT 22nm ull, hspice only, bsim6/bsimbulk 106.2, hspice 2022.06-SP2-2).
- Real user task (verbatim):
  - U#1: "/home/zhenglu/dtech_spice/hlmc_cl022ul_spice 这里面有各种器件的vdd vss vt vd vs吗总结一下"
  - U#2: "这个spice能跑吗跑个简单的"
  - U#3: "nmos.spx详细介绍"
  - U#4 (gives exact deck): "+11 -0 / * simple single-nmos test for hlmc_cl022ul model / .option post=2 runlvl=6 / .lib '...topusage_hlmc_cl022ul_io25_spice_v0p12_0d10_for_vodka_shrink0d855.lib' top_tt / .prot VDS/VGS/X1 nrvt_ckt w=0.2u l=0.05u nf=1 .unprot / .dc VDS 0 0.8 0.02 / .probe i(vds) v(d) / .end / 就这个"
  - U#5: "这个模型是经过校准后的吗"
- Agent actions: read readme.txt + topusage .lib (lines 69-200) → wrote /home/zhenglu/Desktop/_scan_lib.py / _check_env.py → wrote nmos.sp (verbatim U#4 deck) → ran hspice via python runner → produced nmos_out.lis / .sw0 → wrote inv.sp inverter deck + ran → calibration check (_calib.py). Editor writes used `path`+`new_text` keys.
- nmos.sp verbatim (i24 editor new_text):
  ```
  * simple single-nmos test for hlmc_cl022ul model
  .option post=2 runlvl=6
  .lib '/home/zhenglu/dtech_spice/hlmc_cl022ul_spice/topusage_hlmc_cl022ul_io25_spice_v0p12_0d10_for_vodka_shrink0d855.lib' top_tt
  .prot
    VDS D 0 0
    VGS G 0 0.8
    X1 (D G 0 0) nrvt_ckt w=0.2u l=0.05u nf=1
  .unprot
  .dc VDS 0 0.8 0.02
  .probe i(vds) v(d)
  .end
  ```
- .lib header (parseable structure): process banner `hlmc 22nm ull 0.8v/2.5v process (for hspice only)`; `release version : v0p12_0d10_for_vodka + v0p5_0d13_pc70_fuse_res`; `release date : 2026-07-09`; `model : bsim6 (bsimbulk 106.2)`; `simulation tool : hspice 2022.06-SP2-2`; corner blocks top_tt/ff/ss/fs/sf + top_ttg/ffg/ssg/fsg/sfg + top_mc; device library list mos_moscap + bjt_dio_res_mom families; body `.lib '...' <prefix>_noise_<corner>` gives device prefixes rvt/hvt/lvt/uhvt/ehvt/ulvt/na08/na25/io25/avt25; example subckt `x1 ( d g s b ) nrvt_ckt`.
- Reframe decision: **portability-reframe** (hspice binary not portable). Two portable parts of the user's ask: (1) parse .lib → structured summary JSON; (2) build parameterized single-NMOS .dc sweep deck in user's verbatim format. layer=L1 (check runs python tool on hidden B, no EDA binary). track=faithful. tier=B.
- asset A = format-faithful (verbatim header + representative body sections of the real .lib). hidden B = smic 28nm hk (7 structural dimensions differ). B2 = gf 55nm bcd (anti-stub).
- Prior zhenglu session qoz23 (mc30) was parked wrong-domain (DES crypto); 46pb5 is genuine spice_sim (hspice:123 dominant, PDK model exploration + NMOS deck) — different session, different task, verified via user msgs (no crypto content).
