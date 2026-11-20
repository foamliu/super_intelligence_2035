* dff_B.sp -- master-slave DFF (positive-edge), NAND-based, level-1 Shichman-Hodges
* Port: D CLK Q Qb vdd gnd   (subckt name: dff)
* Different sizing/corner than A.
.model nch nmos level=1 kp=80u vto=0.6 lambda=0.04
.model pch pmos level=1 kp=30u vto=-0.6 lambda=0.04
.subckt nd2 out a b vdd gnd
Mn1 out a   n1  gnd nch W=0.8u L=0.15u
Mn2 n1  b   gnd gnd nch W=0.8u L=0.15u
Mp1 out a   vdd vdd pch W=1.2u L=0.15u
Mp2 out b   vdd vdd pch W=1.2u L=0.15u
.ends
.subckt dlat D EN Q Qb vdd gnd
XndA  nA D  EN  vdd gnd nd2
XndB  nB nA EN  vdd gnd nd2
XndQ  Q  nA Qb  vdd gnd nd2
XndQb Qb nB Q   vdd gnd nd2
.ends
.subckt dff D CLK Q Qb vdd gnd
Xinv  clk_b CLK CLK vdd gnd nd2
Xmstr D     clk_b Qm  Qmb vdd gnd dlat
Xslv  Qm    clk  Q    Qsb vdd gnd dlat
Xbufn Qb    Q    Q    vdd gnd nd2
Cclkb clk_b 0 15e-15
CL  Q 0 8e-15
.ends
