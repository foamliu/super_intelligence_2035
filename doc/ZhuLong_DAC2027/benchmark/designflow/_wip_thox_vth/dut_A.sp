* Thick-oxide NMOS device under test (1.8V IO), variant A
* Device: nthk_a — linear-region Vth target ~0.70V
.model nthk_a nmos level=1 vto=0.70 kp=50u gamma=0.40 phi=0.60 lambda=0.05 theta=0.15
.subckt dut d g s b
  m1 d g s b nthk_a W=10u L=0.35u
.ends
