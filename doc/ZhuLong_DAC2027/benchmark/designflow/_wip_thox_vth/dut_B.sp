* Thick-oxide NMOS device under test (1.8V IO), variant B
* Device: nthk_b — linear-region Vth target ~0.58V (different tox / sizing / kp)
.model nthk_b nmos level=1 vto=0.58 kp=42u gamma=0.42 phi=0.62 lambda=0.04 theta=0.18
.subckt dut d g s b
  m1 d g s b nthk_b W=14u L=0.50u
.ends
