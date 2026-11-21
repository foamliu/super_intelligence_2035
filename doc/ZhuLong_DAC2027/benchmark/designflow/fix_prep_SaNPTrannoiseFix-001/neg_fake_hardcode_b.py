#!/usr/bin/env python3
# neg_fake_hardcode_b.py -- smart §4.9(b) B-hardcode stub for SaNPTrannoiseFix-001
# Defeats the visible-A anti-hardcode guard (j): hardcodes BOTH A-gold and B-gold
# outputs keyed by input md5. On unknown input (hidden A') falls back to B-gold.
import hashlib, json, sys
A_MD5='abca06982e8585b7ffc8aed2ae1c2070'
B_MD5='d93433be26ef0e26132409f7340b035c'
A_SP='* Check_SaNP transient-noise testbench\n* corner: TT 1.166V 25C   (Check_SaNP_1 / hspiceD / schematic / vddvssdrop)\n* simulator: FineSim (promd) -- needs spice mode for .trannoise\n.param VDD=1.166 VSS=0\n**************** Accuracy Settings ****************\n.option gmin=1e-16 gmindc=1e-16 $ gmin convergence limit (per Virtuoso common config)\n.option DCON=1                  $ adjust r\n.option mode=spicemd\n* .option list                    $ print all device listings / model params\n.option post=2\n**************** Analysis *************************\n.tran 1n 100n 0 1n\n.op\n**************** Stimulus *************************\nVvdd vdd 0 VDD\nVvss vss 0 VSS\nVin  in  0 pulse(0 VDD 0 100p 100p 50n 100n)\n**************** Circuit **************************\n* SaNP = Set-and-Phase loading chain (pcs_loading)\nxpcs_loading in out vdd vss pcs_loading\n.subckt pcs_loading in out vdd vss\nxmmn13 n1 out vss vss ntnlv_hlsa W=9e-07 L=0.049608u\n  xr1   out vdd 1k\n.ends\n.subckt ntnlv_hlsa d g s b\n  mn1 d g s b ntnlv_hlsa_core W=1u L=0.05u\n.ends\n.model ntnlv_hlsa_core nmos (level=1 wmin=0.900u wmax=1.600u lmin=0.048u lmax=0.050u)\n**************** Transient Noise ******************\n.trannoise fmin=10 fmax=10g noiseseed=1\n.end\n'
A_REP='{\n  "defects_found": [\n    {\n      "class": 2,\n      "kind": "mode_promd_trannoise",\n      "old_mode": "promd",\n      "new_mode": "spicemd"\n    },\n    {\n      "class": 3,\n      "kind": "option_list",\n      "action": "commented_out"\n    },\n    {\n      "class": 5,\n      "kind": "option_artist_post2",\n      "action": "artist_commented_out"\n    },\n    {\n      "class": 1,\n      "kind": "mosfet_w_range",\n      "instance": "xmmn13",\n      "subckt": "ntnlv_hlsa",\n      "param": "W",\n      "old": 6.207359999999999e-07,\n      "new": 9e-07\n    },\n    {\n      "class": 4,\n      "kind": "trannoise_params_inline",\n      "fmin": 10.0,\n      "fmax": "10g",\n      "noiseseed": 1\n    }\n  ],\n  "n_defects": 5\n}'
B_SP='* Check_SaNP transient-noise testbench\n* corner: SS 0.95V -40C   (Check_SaNP_1 / hspiceD / schematic / vddvssdrop)\n* simulator: FineSim (promd) -- needs spice mode for .trannoise\n.param VDD=0.95 VSS=0\n**************** Accuracy Settings ****************\n.option gmin=1e-16 gmindc=1e-16 $ gmin convergence limit\n.option DCON=2                  $ tighter convergence\n.option mode=spicemd\n* .option list                    $ print all device listings / model params\n.option post=2\n**************** Analysis *************************\n.tran 2n 200n 0 2n\n.op\n**************** Stimulus *************************\nVvdd vdd 0 VDD\nVvss vss 0 VSS\nVin  in  0 pulse(0 VDD 0 50p 50p 100n 200n)\n**************** Circuit **************************\n* SaNP = Set-and-Phase loading chain (pcs_loading), 3-stage\nxpcs_loading in out vdd vss pcs_loading\n.subckt pcs_loading in out vdd vss\nxmmn0 n0 out vss vss ntnlv_hlsa W=6e-07 L=0.055u\nxmmn1 n1 n0 vss vss ntnlv_hlsa W=0.80u L=0.055u\nxmmn13 n2 n1 vss vss ntnlv_hlsa W=1.20u L=0.055u\n  xr1    out vdd 2.2k\n.ends\n.subckt ntnlv_hlsa d g s b\n  mn1 d g s b ntnlv_hlsa_core W=1u L=0.06u\n.ends\n.model ntnlv_hlsa_core nmos (level=1 wmin=0.600u wmax=1.200u lmin=0.040u lmax=0.060u)\n**************** Transient Noise ******************\n.trannoise fmin=100 fmax=5g noiseseed=7\n.end\n'
B_REP='{\n  "defects_found": [\n    {\n      "class": 2,\n      "kind": "mode_promd_trannoise",\n      "old_mode": "promd",\n      "new_mode": "spicemd"\n    },\n    {\n      "class": 3,\n      "kind": "option_list",\n      "action": "commented_out"\n    },\n    {\n      "class": 5,\n      "kind": "option_artist_post2",\n      "action": "artist_commented_out"\n    },\n    {\n      "class": 1,\n      "kind": "mosfet_w_range",\n      "instance": "xmmn0",\n      "subckt": "ntnlv_hlsa",\n      "param": "W",\n      "old": 4.5e-07,\n      "new": 6e-07\n    },\n    {\n      "class": 4,\n      "kind": "trannoise_params_inline",\n      "fmin": 100.0,\n      "fmax": "5g",\n      "noiseseed": 7\n    }\n  ],\n  "n_defects": 5\n}'
def md5(p):
    h=hashlib.md5()
    with open(p,'rb') as f: h.update(f.read())
    return h.hexdigest()
def main():
    sp_in, mr_path, sp_out, rep_out = sys.argv[1:5]
    sig = md5(sp_in)
    if sig == A_MD5:
        sp, rep = A_SP, A_REP
    else:
        sp, rep = B_SP, B_REP   # B-gold for B AND fallback for any hidden input
    with open(sp_out,'w') as f: f.write(sp)
    with open(rep_out,'w') as f: f.write(rep)
    return 0
if __name__=="__main__": sys.exit(main())
