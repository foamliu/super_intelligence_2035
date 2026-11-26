* cal_only.sp : comparator input-offset CALIBRATION (1-bit cap) + post-cal offset measurement
*------------------------------------------------------------------------------
* DUT: cmp_dut = 3-inverter comparator (inv1 sizing asymmetry -> raw offset)
* Cal apparatus: Ccal switched into out node by Mcal (cal_en driven by DFF)
* Sequence: init=1 (reset) -> init=0 -> cal_clk pulses -> cal_en=1 (cal cap in)
*           -> Vip ramp, measure residual offset
*------------------------------------------------------------------------------
.param vdda=1.2 vhalf=0.6
.model nch nmos level=1 vto=0.7 kp=50u gamma=0.0 lambda=0.05 nsub=1e16 u0=600 tpg=1
.model pch pmos level=1 vto=-0.7 kp=20u gamma=0.0 lambda=0.05 nsub=1e16 u0=600 tpg=1
.subckt cmp_dut ip in out vdda vss
Mp1  n1   ip   vdda vdda pch w=2u   l=180n
Mn1  n1   ip   vss  vss  nch w=4u   l=180n
Mp2  n2   n1   vdda vdda pch w=4u   l=180n
Mn2  n2   n1   vss  vss  nch w=2u   l=180n
Mp3  out  n2   vdda vdda pch w=8u   l=180n
Mn3  out  n2   vss  vss  nch w=4u   l=180n
Cl   out  vss  3f
.ends
VVDD vdda 0  vdda
VVSS vss  0  0
Vip  ip   0  pwl(0 0, 10n vdda)
Vin  in   0  vhalf
Ccal cal_n 0  10f
Rcal cal_n 0 1meg
Mcal out cal_en cal_n vss nch w=2u l=180n
Vinit  init   0 pulse(1.2 0 0 1n 1n 5n 12n)
Vclk   cal_clk 0 pulse(0 1.2 8n 1n 1n 2n 20n)
Ven    cal_en  0 pwl(0 0, 9.5n 0, 10n 1.2)
xcmp ip in out vdda vss cmp_dut
.tran 10p 12n 0 10p
.measure tran vtrip_at find v(ip) when v(out)=vhalf cross=1
.measure tran offset param='vtrip_at-vhalf'
.end
