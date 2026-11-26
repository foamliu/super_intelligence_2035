# orsuk — SimCornerSearch deepread note

- session: `1794819814309_orsuk` · user `thqu` · host `hfhds208` (10.129.32.82) · model deepseek-v4-flash
- mc=117 (hspice:487 netlist:922) · domain spice_sim · shard B · claimed r852
- case: `EDA-Eval-DesignFlow-SimCornerSearch-001` (B.jsonl 399→400)

## Real task (trace msg 0-146)

1. Debug level-shifter netlist `R_fBcc_iso_opt` (msg 0-70, not used for case).
2. **Find PDK model of a reference finesim run** (msg 71-90) → agent read `model.env` → `.lib '/apps/imctf/models/G6/model_local/V1_HK_Model_L5_v0d9_Rev02_t02/...sp' TT/SS/FF` + bjt_tt/res_tt/nicap_tt/diode_tt (these stay `_tt` even for SS/FF — faithful detail).
3. **Find fullchip sim with corner=SS, temp=-40, vcc(pvint/pvcc)=0.68** (msg 91-146) → agent wrote `find_ss_vcc.py` + `find_ss_vcc.sh` walking `/rundata/ddgoa/V0/simdir/finesim/workdir/kejunw/ddgoaF` (291 runs).
   - **Conclusion**: SS/-40 + pvint=0.68 does NOT exist. pvint is corner-scaled:
     - TT/25c → pvint=0.68
     - SS/-40c → pvint=0.83
     - SS/130c → pvint=0.73
     - FF/-40c → pvint=0.70
   - Reason: `common_new.env` binds pvcc to pvint (line 3 `.param pvccsc = pvint`; agent's note said line 67 sets pvcc=pvint — the override semantics are `vcc_eff = pvcc if pvcc else pvint`).

## Verbatim regexes (agent's find_ss_vcc.py msg 105/111)

- corner: `r'\.lib\b[^\n]*\b(SS|TT|FF)\b'` (from model.env)
- temp:   `r'\.temp\s*(-?\d+)'` (from model.env)
- pvint:  `r'\.param\s+pvint\s*=\s*([\d.]+)'` (from hspice.sim)
- pvcc:   `r'\.param\s+pvcc\s*=\s*([\d.]+)'` (from hspice.sim)
- `vcc_eff = pvcc if pvcc else pvint`
- SKIP prune set (from find_ss_vcc.sh msg 125 `-prune`): raw/debugMode/netlist/result/sim_require/vec/log/fsdb/FSDB/wave/out/spice_out

## Verbatim file samples (trace read_file returns)

- `model.env` TT (msg 75): `.temp 25c` / `.param ptemp = 25` / `.param pcorner = 1` / `.lib '.../V1_HK_Model_L5_v0d9_Rev02_t02.sp' TT` + `TT_Array` + bjt_tt/res_tt/nicap_tt/diode_tt
- `model.env` SS (msg 87): `.temp -40c` / `pcorner=2` / `.lib ... SS` + `SS_Array` (bjt/res/nicap/diode STILL `_tt`)
- `hspice.sim` TT0.94v25c (msg 75): line 1 comment `**.../log_kejun/tm_eqsabl_..._DVFSCELowSpeed.x16 0.94v TT;25c X16 tmp.voltage_s_LP5X`; line 2 `.inc ".../hspice0.94v.voltage"`; line 6 `*TT0.94v25c*`; vAdjZqPd5..0 + vAdjZqPu5..0 with `xi_c_top.xI_Channel.xI_ChanRight.xIAnalogChanRightLTop.xi_zqtopm5_63.xi_zqcalibrate_43.net0138/9<N>`; `.param pvth=0.3v pvint=0.68v pvintbus=0.39v pvdbias=0.89972v pVregWck=1.53167 pvregdqs=1.53167 TWCK2DQI=510`
- `hspice.sim` SS0.9v-40c (msg 87): pvth=0.4v pvint=0.83v pvintbus=0.65v pvdbias=0.91415v pVregWck=1.3587 TWCK2DQI=560; instance hierarchy DIFFERS: `xi_c_top.xi_channel.xi_chanedgel_1630.xi_padleft_0.xi_zqtopm5_63.xi_zqcalibrate_43` (note: lowercase `xi_channel`/`xi_chanedgel` vs TT's `xI_Channel`/`xI_ChanRight` — trace quirk, A assets use TT form)
- `hspice.sim` SS0.9v130c (msg 99): pvint=0.73v pvdbias=0.94178v pVregWck=1.6913 TWCK2DQI=480
- `hspice.sim` FF1.25v-40c (msg 99): pvth=0.2v pvint=0.7v pvintbus=0.39v pvdbias=0.86893v pVregWck=1.1702 TWCK2DQI=260; voltage file `hspice1.25v.voltage`
- `common_new.env` (msg 84): line 3 `.param pvccsc = pvint **edit by clzhang yifan request` — the pvcc←pvint binding.

## Case design

- Deliverable: `find_corner_runs.py` (parameterized `--root/--corner/--temp/--vcc`).
- A (visible, trace-verbatim): 4 run dirs under `A_runs/MatrixRun_Netlist_Vcap_20261029PM_kejun/ddgoaF/` — TT0.94v25c/SS0.9v-40c/SS0.9v130c/FF1.25v-40c. **No SS-40+0.68 hit** (trace conclusion).
- Hidden B (structural diff): testcase `tm_othermod_wcktrain_16b_B2`, user `user_thqu_b`, instance hierarchy `xi_top.xi_dqchan.xi_pad0.xi_zqadj_31.net0238/9`, pvint 0.69/0.83/0.74/0.70, + a `nested_proj/sub_run/` depth-3 dir, + **1 PLANTED hit** `...SS0.9v-40c.pvcc068...` with both `.param pvcc=0.68` and `.param pvint=0.83` (vcc_eff=pvcc=0.68).
- check.py 10 assertions (a-j): zip+compile (a,b), run on B exit 0 (c), find planted hit (d — defeats empty/printf/stub/core-deleted/hardcoded-A), no-match returns empty+exit0 (e), `--vcc 0.83` finds flat+nested (f), anti-hardcode-A no `kejunw` (g), pvcc precedence `vcc_eff=0.68` (h), subdir recursion (i), precision `--vcc 0.68` skips pvint=0.83 dirs (j).
- 5 negatives all FAIL (NEG_RC=0); reference PASS 10/10. Verified on .75 + local.

## Disposition

- claimed r852, marked case `EDA-Eval-DesignFlow-SimCornerSearch-001`.
- 3 prior triage rejects (qoz23 wrong-domain eda_other, md9m3 dup of IbisZqCalibMerge-001, hk2q4 eda_other/harness) NOT claimed — remain fresh for A.
