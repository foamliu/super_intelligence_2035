* Check_SaNP transient-noise testbench
* corner: FF 1.35V 125C   (Check_SaNP_2 / hspiceD / schematic / vddvssdrop)
* simulator: FineSim (promd) -- needs spice mode for .trannoise
.param VDD=1.35 VSS=0
**************** Accuracy Settings ****************
.option gmin=1e-16 gmindc=1e-16 $ gmin convergence limit (per Virtuoso common config)
.option DCON=3                  $ tightest convergence
.option mode=spicemd
* .option list                    $ print all device listings / model params
.option post=2
**************** Analysis *************************
.tran 0.5n 50n 0 0.5n
.op
**************** Stimulus *************************
Vvdd vdd 0 VDD
Vvss vss 0 VSS
Vin  in  0 pulse(0 VDD 0 80p 80p 30n 60n)
**************** Circuit **************************
* SaNP = Set-and-Phase loading chain (sns_chain), 2-stage
xsns_chain in out vdd vss sns_chain
.subckt sns_chain in out vdd vss
xmson0 n0 out vss vss sns_hv_nmos W=1u L=0.060u
xmson1 out n0 vss vss sns_hv_nmos W=1.50u L=0.060u
  xr1   out vdd 1.5k
.ends
.subckt sns_hv_nmos d g s b
  mn1 d g s b sns_hv_nmos_core W=1u L=0.06u
.ends
.model sns_hv_nmos_core nmos (level=1 wmin=1.000u wmax=2.000u lmin=0.050u lmax=0.070u)
**************** Transient Noise ******************
.trannoise fmin=50 fmax=20g noiseseed=42
.end
