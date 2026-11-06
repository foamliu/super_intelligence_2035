*******hspice option**********
.option PARHIER = LOCAL
.option accurate=1
.option gmin=1e-16 gmindc=1e-16
.option probe=1 post
.option measfile=1 measform=1

*******finesim option**********
.option finesim_mode=spicead

*******netlist***************
.inc '/rundata/drcoa/V0/ver/pex/johnl/T_IsmTop/lpe/T_IsmTop/T_IsmTop.spf_RCC'
.GLOBAL vss! vbn! vbp! vdd1! vcc! vpcsg! vwlp! vcslp! vkb! vddq! vdleq! vfsbln! vdbias!

*****************G4Plus power parameters***************
.param pvdd1=1.8 pvcc=1.3 pvdd2h=pvcc pvdd2hs=pvcc pvdd2l=0.9 pvddq=pvcc pvddqca=pvcc pvdll=pvcc pvss=0 pvssq=pvss pvssdll=pvss
.param pvwlp=2.95  pvpcsg=2 pvcslp=1.5 pvbn=-0.1 pvncsgn=-0.2 pvkb=-0.7
.param pvblh=0.95 pvdleq=1.25 pvnoc=pvdleq pvintlp=0.8 pviso=1.4 pvmwln=2.5 pvad2e='pvblh/2' pvad2o=pvad2e pvap2=pvad2e pvcsl=1.16 pvwln=-0.2
.param pvbp=pvcc pvdiv=1.2 pvtsc=1.25 pvdbias=0.92
.param pvfsbln=5 pvfsgdl=pvwlp pvfsgt=pvwlp pvfsrdb=0.5 pvfsblnfsgateunsel=2 pvfsblnxgate=2.5 pvthinfsgdl=2.5 pvfsrdfsgate=1.5 pvfsrdxgate=1.35 pvfsblnfsgatethin=5

.subckt switch_close POS NEG
R0 POS NEG r=0.001
.ends switch_close

.subckt switch_open POS NEG
.ends switch_open

.subckt brknet MINUS PLUS r=0.001
Rbrknet0 PLUS MINUS r
.ends brknet

.subckt brknetM0 A B
XRRI0 B A brknet r=1e-3
.ends brknetM0

.subckt brknetM1 A B
XRRI0 B A brknet r=1e-3
.ends brknetM1

.subckt brknetM2 A B
XRRI0 B A brknet r=1e-3
.ends brknetM2

.subckt brknetM3 A B
XRRI0 B A brknet r=1e-3
.ends brknetM3

.subckt brknetM4 A B
XRRI0 B A brknet r=1e-3
.ends brknetM4

*****************G4Plus power up***************
vvcc          vcc!           0    pvcc
vvbp          vbp!           0    pvbp
vvss          vss!           0    pvss
vvbn          vbn!           0    pvbn
vvdbias       vdbias!        0    pvdbias

vvdd1         vdd1!          0    pvdd1
vvddq         vddq!          0    pvddq
vvpcsg        vpcsg!         0    pvpcsg
vvwlp         vwlp!          0    pvwlp
vvcslp        vcslp!         0    pvcslp
vvkb          vkb!           0    pvkb
vvdleq        vdleq!         0    pvdleq
vvfsbln       vfsbln!        0    pvfsbln

******stimulus: sweep final edgecnt 16,17,0,1,2 with 1ps step***************
.param stoptime=0.18045n
vIsmStartLat        IsmStartLat          0    PWL( 0 0 2000n  0 2000.1n pvcc)
vIsmStopLat         IsmStopLat           0    PWL( 0 0 '2005.41n+stoptime'  0  'stoptime+2005.51n' pvcc)

.param CapO=0.4f
.param Cgatein=0.4f
.param Cthick=0.2f
.param Cthin=0.4f

VBK0CP30              cm0_ts_Ismsuper          0   dc=pvcc power=0

.tran 1p 4u sweep stoptime 0.18045n 2n 0.001n

****************************************************
* 1) Edge timing
****************************************************
.meas tran t_start WHEN v(IsmStartLat)=0.5*pvcc RISE=1
.meas tran t_stop  WHEN v(IsmStopLat)=0.5*pvcc RISE=1
.meas tran delta_t param='t_stop - t_start'

****************************************************
* 2) Sample bus at 1us after stop edge
****************************************************
.param t_sample_offset = 1u
.meas tran t_sample param='t_stop + t_sample_offset'

.meas tran b0  FIND v(edgecode<0>)   AT=t_sample
.meas tran b1  FIND v(edgecode<1>)   AT=t_sample
.meas tran b2  FIND v(edgecode<2>)   AT=t_sample
.meas tran b3  FIND v(edgecode<3>)   AT=t_sample
.meas tran b4  FIND v(edgecode<4>)   AT=t_sample

.meas tran p0  FIND v(plscntout<0>)  AT=t_sample
.meas tran p1  FIND v(plscntout<1>)  AT=t_sample
.meas tran p2  FIND v(plscntout<2>)  AT=t_sample
.meas tran p3  FIND v(plscntout<3>)  AT=t_sample
.meas tran p4  FIND v(plscntout<4>)  AT=t_sample
.meas tran p5  FIND v(plscntout<5>)  AT=t_sample
.meas tran p6  FIND v(plscntout<6>)  AT=t_sample
.meas tran p7  FIND v(plscntout<7>)  AT=t_sample
.meas tran p8  FIND v(plscntout<8>)  AT=t_sample
.meas tran p9  FIND v(plscntout<9>)  AT=t_sample
.meas tran p10 FIND v(plscntout<10>) AT=t_sample

****************************************************
* 3) Decode with windows
****************************************************
.meas tran vb0  param='min(1, 0.5*(sgn(0.2*pvcc-b0)+1) + 0.5*(sgn(b0-0.8*pvcc)+1))'
.meas tran vb1  param='min(1, 0.5*(sgn(0.2*pvcc-b1)+1) + 0.5*(sgn(b1-0.8*pvcc)+1))'
.meas tran vb2  param='min(1, 0.5*(sgn(0.2*pvcc-b2)+1) + 0.5*(sgn(b2-0.8*pvcc)+1))'
.meas tran vb3  param='min(1, 0.5*(sgn(0.2*pvcc-b3)+1) + 0.5*(sgn(b3-0.8*pvcc)+1))'
.meas tran vb4  param='min(1, 0.5*(sgn(0.2*pvcc-b4)+1) + 0.5*(sgn(b4-0.8*pvcc)+1))'

.meas tran vp0  param='min(1, 0.5*(sgn(0.2*pvcc-p0)+1) + 0.5*(sgn(p0-0.8*pvcc)+1))'
.meas tran vp1  param='min(1, 0.5*(sgn(0.2*pvcc-p1)+1) + 0.5*(sgn(p1-0.8*pvcc)+1))'
.meas tran vp2  param='min(1, 0.5*(sgn(0.2*pvcc-p2)+1) + 0.5*(sgn(p2-0.8*pvcc)+1))'
.meas tran vp3  param='min(1, 0.5*(sgn(0.2*pvcc-p3)+1) + 0.5*(sgn(p3-0.8*pvcc)+1))'
.meas tran vp4  param='min(1, 0.5*(sgn(0.2*pvcc-p4)+1) + 0.5*(sgn(p4-0.8*pvcc)+1))'
.meas tran vp5  param='min(1, 0.5*(sgn(0.2*pvcc-p5)+1) + 0.5*(sgn(p5-0.8*pvcc)+1))'
.meas tran vp6  param='min(1, 0.5*(sgn(0.2*pvcc-p6)+1) + 0.5*(sgn(p6-0.8*pvcc)+1))'
.meas tran vp7  param='min(1, 0.5*(sgn(0.2*pvcc-p7)+1) + 0.5*(sgn(p7-0.8*pvcc)+1))'
.meas tran vp8  param='min(1, 0.5*(sgn(0.2*pvcc-p8)+1) + 0.5*(sgn(p8-0.8*pvcc)+1))'
.meas tran vp9  param='min(1, 0.5*(sgn(0.2*pvcc-p9)+1) + 0.5*(sgn(p9-0.8*pvcc)+1))'
.meas tran vp10 param='min(1, 0.5*(sgn(0.2*pvcc-p10)+1)+ 0.5*(sgn(p10-0.8*pvcc)+1))'

.meas tran valid_bus_l param='vb0*vb1*vb2*vb3*vp0*vp1*vp2*vp3'
.meas tran valid_bus_h param='vp4*vp5*vp6*vp7*vp8*vp9*vp10'
.meas tran valid_bus param='valid_bus_l*valid_bus_h'

.meas tran edge_val_l param='0.5*(sgn(b0-0.8*pvcc)+1)*1 + 0.5*(sgn(b1-0.8*pvcc)+1)*2 + 0.5*(sgn(b2-0.8*pvcc)+1)*4'
.meas tran edge_val_h param='0.5*(sgn(b3-0.8*pvcc)+1)*8 + 0.5*(sgn(b4-0.8*pvcc)+1)*16'
.meas tran edge_val param='edge_val_l + edge_val_h'

.meas tran pls_val_l param='0.5*(sgn(p0-0.8*pvcc)+1)*1 + 0.5*(sgn(p1-0.8*pvcc)+1)*2 + 0.5*(sgn(p2-0.8*pvcc)+1)*4 + 0.5*(sgn(p3-0.8*pvcc)+1)*8 + 0.5*(sgn(p4-0.8*pvcc)+1)*16'
.meas tran pls_val_m param='0.5*(sgn(p5-0.8*pvcc)+1)*32 + 0.5*(sgn(p6-0.8*pvcc)+1)*64 + 0.5*(sgn(p7-0.8*pvcc)+1)*128'
.meas tran pls_val_h param='0.5*(sgn(p8-0.8*pvcc)+1)*256 + 0.5*(sgn(p9-0.8*pvcc)+1)*512 + 0.5*(sgn(p10-0.8*pvcc)+1)*1024'
.meas tran pls_val param='pls_val_l + pls_val_m + pls_val_h'

****************************************************
* 4) Expected delay
****************************************************
.meas tran expected_t param='edge_val*63.9p + pls_val*1150p'

****************************************************
* 5) Error and tolerance
****************************************************
.meas tran error     param='delta_t - expected_t'
.meas tran abs_error param='abs(error)'
.meas tran pass_flag param='valid_bus * (abs_error <= 200p)'

****************************************************
* 6) Pulse effect flag
****************************************************
.meas tran last_pls_pre0 FIND v(XI_T_IsmCntClkGen.LastPlsCntPre<0>) AT=t_sample
.meas tran edge_is_0_or_17 param='min(1, 0.5*(sgn(0.5-abs(edge_val-0))+1) + 0.5*(sgn(0.5-abs(edge_val-17))+1))'
.meas tran last_pls_pre0_high param='0.5*(sgn(last_pls_pre0-0.8*pvcc)+1)'
.meas tran pulse_effect param='edge_is_0_or_17 * last_pls_pre0_high'

.probe v(*)

******pvt: FF 1.3V -40C*******************
******pvt: FF 1.3V -40C*******************


.TEMP -40
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/G5_CIP_Model_D5_v0d9.sp" FF
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" bjt_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" res_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" nicap_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" diode_tt
.alter FF_1p3V_110
.param pvcc=1.3
.TEMP 110
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/G5_CIP_Model_D5_v0d9.sp" FF
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" bjt_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" res_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" nicap_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" diode_tt
.alter TT_1p1V_m10
.param pvcc=1.1
.TEMP -10
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/G5_CIP_Model_D5_v0d9.sp" TT
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" bjt_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" res_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" nicap_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" diode_tt
.alter TT_1p21V_98
.param pvcc=1.21
.TEMP 98
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/G5_CIP_Model_D5_v0d9.sp" TT
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" bjt_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" res_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" nicap_tt
.lib "/apps/imctf/models/10G5/model_local/G5_CIP_Model_D5_v0d9/incFile_G5_CIP" diode_tt
.end
