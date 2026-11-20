* dff_A.sp -- master-slave DFF (positive-edge), NAND-based, level-1 Shichman-Hodges
* Port: D CLK Q Qb vdd gnd   (subckt name: dff)
* Master-slave of two NAND SR-latches. Fully boolean -> robust, no TG threshold
* drops. tSU = master transparent delay (D->Qm), tH = master turn-off aperture,
* tCQ = slave transparent delay (Qm->Q). All positive and measurable.
.model nch nmos level=1 kp=50u vto=0.7 lambda=0.05
.model pch pmos level=1 kp=20u vto=-0.7 lambda=0.05
* 2-input NAND
.subckt nd2 out a b vdd gnd
Mn1 out a   n1  gnd nch W=0.5u L=0.13u
Mn2 n1  b   gnd gnd nch W=0.5u L=0.13u
Mp1 out a   vdd vdd pch W=1u  L=0.13u
Mp2 out b   vdd vdd pch W=1u  L=0.13u
.ends
* D-latch: transparent when EN=1 ; holds when EN=0
.subckt dlat D EN Q Qb vdd gnd
XndA  nA D  EN  vdd gnd nd2
XndB  nB nA EN  vdd gnd nd2
XndQ  Q  nA Qb  vdd gnd nd2
XndQb Qb nB Q   vdd gnd nd2
.ends
* Positive-edge master-slave DFF
.subckt dff D CLK Q Qb vdd gnd
Xinv  clk_b CLK CLK vdd gnd nd2
Xmstr D     clk_b Qm  Qmb vdd gnd dlat
Xslv  Qm    clk  Q    Qsb vdd gnd dlat
Xbufn Qb    Q    Q    vdd gnd nd2
Cclkb clk_b 0 10e-15
CL  Q 0 5e-15
.ends
