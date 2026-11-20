* Library : drvqa_cmos_digital
* Cell    : SpineTop_A
* View    : schematic
* emy2netlist hspice/ALPS export (Netlist_Vcap_20261008PM, ~115MB full netlist trimmed sample)
* This file is a self-contained SPICE netlist fragment for the SpineTop_A cell
* and the sub-cells it instantiates.  Line 1 col-1 cards; '+' continuation lines
* join the previous card (SPICE convention).

* ---------------------------------------------------------------------------
* Sub-cell definitions (one level under SpineTop_A)
* ---------------------------------------------------------------------------

* Library : drvqa_cmos_digital
* Cell    : ECC_LbusDrv_A
* View    : schematic
.SUBCKT ECC_LbusDrv_A din<0> din<1> din<2> din<3> dout<0> dout<1> vdd vss
*.PININFO din<0>:I din<1>:I din<2>:I din<3>:I dout<0>:O dout<1>:O vdd:P vss:G
xI0 din<0> n0 vdd vss invLx4
xI1 din<1> n1 vdd vss invLx4
xI2 n0 n2 vdd vss nand2Lx2
xI3 n1 n2 vdd vss nand2Lx2
xI4 n2 dout<0> vdd vss invLx4
xI5 din<2> n3 vdd vss invLx4
xI6 din<3> n4 vdd vss invLx4
xI7 n3 n5 vdd vss nand2Lx2
xI8 n4 n5 vdd vss nand2Lx2
xI9 n5 dout<1> vdd vss invLx4
.ENDS ECC_LbusDrv_A

* Library : drvqa_cmos_digital
* Cell    : BankTopX2_A
* View    : schematic
.SUBCKT BankTopX2_A bl0 br0 bl1 br1 wl vdd vss
*.PININFO bl0:I br0:I bl1:I br1:I wl:I vdd:P vss:G
xDEC wl decA decB vdd vss nand2Lx2
xSA0 bl0 br0 sa0 vdd vss invLx4
xSA1 bl1 br1 sa1 vdd vss invLx4
Mp0 sa0 wl vdd vdd pch W=0.6u L=40n
Mn0 sa0 wl vss vss ntn W=0.4u L=40n
Cc0 sa0 vss 20f
.ENDS BankTopX2_A

* Library : drvqa_cmos_digital
* Cell    : SpineRpt_A
* View    : schematic
.SUBCKT SpineRpt_A in0 in1 in2 in3 out0 out1 out2 out3 vdd vss
*.PININFO in0:I in1:I in2:I in3:I out0:O out1:O out2:O out3:O vdd:P vss:G
xR0 in0 out0 vdd vss invLx4
xR1 in1 out1 vdd vss invLx4
xR2 in2 out2 vdd vss invLx4
xR3 in3 out3 vdd vss invLx4
.ENDS SpineRpt_A

* Library : stdcells_ac
* Cell    : invLx4
* View    : schematic
.SUBCKT invLx4 a y vdd vss
Mp a a y vdd pch W=1.2u L=40n
Mn a a y vss ntn W=0.8u L=40n
.ENDS invLx4

* Library : stdcells_ac
* Cell    : nand2Lx2
* View    : schematic
.SUBCKT nand2Lx2 a b y vdd vss
Mp a b y vdd pch W=1.0u L=40n
Mn a b y vss ntn W=0.6u L=40n
.ENDS nand2Lx2

* ---------------------------------------------------------------------------
* TARGET CELL: SpineTop_A
* ---------------------------------------------------------------------------
* Library : drvqa_cmos_digital
* Cell    : SpineTop_A
* View    : schematic
.SUBCKT SpineTop_A clk rst_n ec bl0 br0 bl1 br1 wl rd0 rd1 rd2 rd3
+ sa_en bg_en vdd vss
*.PININFO clk:I rst_n:I ec:I bl0:I br0:I bl1:I br1:I wl:I rd0:O rd1:O
*.PININFO rd2:O rd3:O sa_en:I bg_en:I vdd:P vss:G
* --- instances (note: X-cards may span '+' continuation lines) ---
xECC0 ec rd0 rd1 vdd vss ECC_LbusDrv_A
xBK0 bl0 br0 bl1 br1 wl vdd vss BankTopX2_A
xBK1 bl0 br0 bl1 br1 wl vdd vss BankTopX2_A
xRP0 rd0 rd1 rd2 rd3 sa0 sa1 sa2 sa3 vdd vss
+ SpineRpt_A
xBG0 bg_en bgp vdd vss invLx4
* a deliberately long X-card spanning three '+' lines:
xRP1 rd0 rd1 rd2 rd3 sa4 sa5 sa6 sa7 vdd vss
+ SpineRpt_A
* primitive devices at this level (must NOT be counted as sub-cells)
MpTop clk rst_n nclk vdd pch W=2u L=40n
MnTop clk rst_n nclk vss ntn W=1u L=40n
Rpull nclk vdd 10k
Cdec nclk vss 5f
.ENDS SpineTop_A

* Library : drvqa_cmos_digital
* Cell    : OtherTop_A
* View    : schematic
.SUBCKT OtherTop_A a b y vdd vss
xO0 a b y vdd vss nand2Lx2
.ENDS OtherTop_A
