.param Cthin=0.4f Cthick=0.4f CapO=0.4f Cgatein=0.4f
.param pvcc=0.9 pvss=0
.param shrink=0.318
.inc '/proj/m2701/V0_DDR2/workdir/hairuizh/simulation/presim/lvlshft/spice/plat_condtions/G4B_DEJOA/G4B_DEJOA_conditions.sp'

.param Lreal=125n
** thick: real = draw*shrink ; G4B shrink = 0.318
** real swidth: N=250n P=500n ; real L sweep 125n..1u step 25n
.param WNdraw='250e-9/shrink'
.param WPdraw='500e-9/shrink'

.if(sel_case==1)
.param Wsweep=1
.elseif(sel_case==2)
.param Wsweep=1
.endif

.subckt invS A Y inh_vbulkn inh_vbulkp inh_vcc inh_vss WN='WNdraw' LN='Lreal/shrink' nfN=1 WP='WPdraw' LP='Lreal/shrink' nfP=1
XMMN0 Y A inh_vss inh_vbulkn ntk w='WN' l='LN'
XMMP0 Y A inh_vcc inh_vbulkp ptk w='WP' l='LP'
cg1 A 0 c='Cthick*(nfN+nfP)'
cout1 Y 0 c='CapO*(nfN+nfP)'
.ends invS

.subckt invS_lv A Y inh_vbulkn inh_vbulkp inh_vcc inh_vss WN='WNdraw' LN='Lreal/shrink' nfN=1 WP='WPdraw' LP='Lreal/shrink' nfP=1
XMMN0 Y A inh_vss inh_vbulkn ntk_lv w='WN' l='LN'
XMMP0 Y A inh_vcc inh_vbulkp ptk_lv w='WP' l='LP'
cg1 A 0 c='Cthick*(nfN+nfP)'
cout1 Y 0 c='CapO*(nfN+nfP)'
.ends invS_lv

.subckt invSx1_Xdec A Y inh_vbn inh_vbp inh_vcc inh_vss Wfact=1 LNP='Lreal/shrink'
XI0 A Y inh_vbn inh_vbp inh_vcc inh_vss invS WN='WNdraw*Wfact' LN='LNP' WP='WPdraw*Wfact' LP='LNP'
cXI0_1 A 0 c='Cgatein'
.ends invSx1_Xdec

.subckt invSx1_Xdec_lv A Y inh_vbn inh_vbp inh_vcc inh_vss Wfact=1 LNP='Lreal/shrink'
XI0 A Y inh_vbn inh_vbp inh_vcc inh_vss invS_lv WN='WNdraw*Wfact' LN='LNP' WP='WPdraw*Wfact' LP='LNP'
cXI0_1 A 0 c='Cgatein'
.ends invSx1_Xdec_lv

.if(sel_mos==0)
XI4 out net5 vbn! vbp! vcc! vss! invSx1_Xdec Wfact=Wsweep
XI3 out net6 vbn! vbp! vcc! vss! invSx1_Xdec Wfact=Wsweep
XI2 out net7 vbn! vbp! vcc! vss! invSx1_Xdec Wfact=Wsweep
XI0 indrv in vbn! vbp! vcc! vss! invSx1_Xdec Wfact=Wsweep
XI1 in out vbn! vbp! vcc! vss! invSx1_Xdec Wfact=Wsweep
.elseif(sel_mos==1)
XI4 out net5 vbn! vbp! vcc! vss! invSx1_Xdec_lv Wfact=Wsweep
XI3 out net6 vbn! vbp! vcc! vss! invSx1_Xdec_lv Wfact=Wsweep
XI2 out net7 vbn! vbp! vcc! vss! invSx1_Xdec_lv Wfact=Wsweep
XI0 indrv in vbn! vbp! vcc! vss! invSx1_Xdec_lv Wfact=Wsweep
XI1 in out vbn! vbp! vcc! vss! invSx1_Xdec_lv Wfact=Wsweep
.endif

Vvcc vcc! 0 pvwlp
Vvss vss! 0 pvss
Vvbn vbn! 0 pvss
Vvbp vbp! 0 pvwlp
Vvindrv indrv 0 PULSE(pvwlp pvss 40n tr tf tduty tperiod)
.ic V(in)=pvss V(out)=pvwlp

.measure tran meas_tpr_in_out TRIG v(in) VAL=0.5*pvwlp FALL=10 TARG v(out) VAL=0.5*pvwlp RISE=10
.measure tran meas_tpf_in_out TRIG v(in) VAL=0.5*pvwlp RISE=10 TARG v(out) VAL=0.5*pvwlp FALL=10
.measure tran meas_tr_in TRIG v(in) VAL=0.1*pvwlp RISE=10 TARG v(in) VAL=0.9*pvwlp RISE=10
.measure tran meas_tf_in TRIG v(in) VAL=0.9*pvwlp FALL=10 TARG v(in) VAL=0.1*pvwlp FALL=10
.measure tran meas_tr_out TRIG v(out) VAL=0.1*pvwlp RISE=10 TARG v(out) VAL=0.9*pvwlp RISE=10
.measure tran meas_tf_out TRIG v(out) VAL=0.9*pvwlp FALL=10 TARG v(out) VAL=0.1*pvwlp FALL=10
.measure tran iddq find I(Vvcc) at=39n
.measure tran idda AVG I(Vvcc) FROM=40n TO=100n

.if(sel_sweep==0)
.tran 0.1p 100n sweep Lreal 125n 1u 25n
.elseif(sel_sweep==1)
.tran 0.1p 100n sweep Wsweep 1 5 0.2
.endif

.probe i(*) v(*)
