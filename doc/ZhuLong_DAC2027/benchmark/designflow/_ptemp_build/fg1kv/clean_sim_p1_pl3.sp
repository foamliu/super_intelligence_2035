** **

.inc "/proj/ddgoa/V0/workdir/ghyang/simulation/setup/finesim_option"

** include netlist_yio_ref_l16 **
.inc "./netlist_twistYio"
.inc "/proj/ddgoa/V0/workdir/ytzhu/simulation/setup/mismatch.param"
.inc "./yioloading"
** include power **
.inc "/proj/ddgoa/V0/workdir/ytzhu/simulation/setup/Pattern_Power_CRG.sp"

.param pvintlp=pvblh*0.5
.param pvcc=0.9
.param ORG=8
.param ptemp =-40
.param pvblh=0.9
.param pvcsl=0.88

vint   vint!  0  dc=pvint  power=0
.param pvint=0.65
vintzYsa vintzYsa! 0  dc=pvintzYsa power=0
.param pvintzYsa=0.65
vintcore   vintcore!  0  dc=pvintcore  power=0
**ss-40**
.param pvintcore=0.9
vcslzColCtrl   vcslzColCtrl!  0  dc=pvcslzColCtrl  power=0
.param pvcslzColCtrl=pvcsl
vdd2l   vdd2l!  0  dc=pvdd2l  power=0
.param pvdd2l=pvdd2
vdd2h   vdd2h!  0  dc=pvdd2h  power=0
**ss-40**
.param pvdd2h=0.9
vdd2hs   vdd2hs!  0  dc=pvdd2hs  power=0
.param pvdd2hs=pvdd2
vbpcore   vbpcore!  0  dc=pvbpcore  power=0
.param pvbpcore=pvbp
vbncore   vbncore!  0  dc=pvbncore  power=0
.param pvbncore=pvbn

** include model.env **
.temp -40c
.lib '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t02/model.sp' ss
.lib '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t02/model.sp' ss_array
.lib '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t02/incFile_lp' bjt_ss
.lib '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t02/incFile_lp' res_ss
.lib '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t02/incFile_lp' nicap_ss
.lib '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t02/incFile_lp' diode_ss

** include stimulus **
*.inc './w0w1r1w0r0.sp'
*.inc './stimulus_PatternAll.sp'
.inc './stimulus_Pattern1.sp'
.inc './wr_common.sp'
.inc '/proj/ddgoa/V0/workdir/ytzhu/simulation/setup/ArrayRcSetting_0817.inc'
.param delvto_Ns=0
.param pvpcsga=pvpcsg  pvpcsgb=pvss     pvpcsgc=pvss
.GLOBAL vmwln! vcsl! viso! vkb! vpcsg! vwln! vap2! vcslp! vdd1! vdleq! vad2o! vblh! vss! vcc! vad2e! vbn! vwlp! vint! vintcore!


*********Cell***************
*cc00
.param KCTA='pvblh'
*cc01
.param KCTB='pvblh'
*cc02
.param KCTC='pvblh'
*cc03
.param KCTD='pvblh'

*cc00 
.param KCTE='pvblh'
*cc01 
.param KCTF='pvblh'
*cc02 bl000
.param KCTG='pvss'
*cc03 
.param KCTH='pvblh'

.param KCBGA='pvblh'
.param KCBGB='pvblh'
.param KCBGC='pvblh'
.param KCBGD='pvblh'

*********Bisection**************
*.param trden=90n
.param trden=25n
.param twrite=25n
*.param trden3=96n
.param trden3=31n
.param twrite3=31n
*.param trden4=99n
*.param twrite4=99n
.param trden5=37n
.param twrite5=37n

.probe v(*) level=10
.probe i(*) level=10

*.param tmeas=80n
.param tmeas=16n

.param c_csl=1
.param r_eqio=1
.param f_eqio=1
.param c_rden=1
.param c_rwenn=1
.param r_yioeqn=1
.param f_yioeqn=1

.param c_ysaen=1
.param c_ysaeqn=1

.param c_yiosel=1
vreftrima	treftrima	0 pwl	0	pvcc
vreftrimb	treftrimb	0 pwl	0	pvcc
vreftrimc	treftrimc	0 pwl	0	pvcc

*============================================================
* tCCD measurement - W0(ignore) W1 R1 W0 R0
* All edges at 50% of signal swing
*============================================================

.param c_csl_w1=2   f_eqio_w1=2   r_eqio_w1=2
.param c_csl_w0=4   f_eqio_w0=4   r_eqio_w0=4
.param c_rden_r1=1  f_eqio_r1=3   r_eqio_r1=3
.param c_rden_r0=2  f_eqio_r0=5   r_eqio_r0=5


*============================
*        Write1 tCCD
*============================

.meas tran tcsl_w1   when v(xi_msaq_fbcc_01.cslcon0<0>)  val='0.5*pvcsl'  td=tmeas  rise=c_csl_w1  print=0
.meas tran teqiof_w1 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  fall=f_eqio_w1  print=0
.meas tran tA_w1  param='tcsl_w1 - teqiof_w1'

.meas tran tB_w1  trig  v(xi_msaq_fbcc_01.cslcon0<0>)  val='0.5*pvcsl'  td=tmeas  rise=c_csl_w1
+                 targ  v(net941<0>)-v(net852<0>)   val='0.3*pvblh'  td=tcsl_w1
*+                 targ  abs(v(net941<0>)-v(net852<0>))   val='0.3*pvblh'  td=tcsl_w1

.meas tran teqior_w1 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  rise=r_eqio_w1  print=0
.meas tran tC_w1  trig  v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)               val='0.5*pvdleq'  td=tmeas  rise=r_eqio_w1
+                 targ  abs(v(xi_msaq_fbcc_01.xi_msax384_l.io0l<0>)-v(xi_msaq_fbcc_01.xi_msax384_l.ion0l<0>))  val='0.02*pvintlp'  td=teqior_w1

.meas tran tCCD_W1  param='tA_w1 + tB_w1 + tC_w1'


*============================
*        Write0 tCCD
*============================

.meas tran tcsl_w0   when v(xi_msaq_fbcc_01.cslcon0<0>)  val='0.5*pvcsl'  td=tmeas  rise=c_csl_w0  print=0
.meas tran teqiof_w0 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  fall=f_eqio_w0  print=0
.meas tran tA_w0  param='tcsl_w0 - teqiof_w0'

*.meas tran tB_w0  trig  v(cslmidrc<0>)                 val='0.5*pvcsl'  td=tmeas  rise=c_csl_w0
.meas tran tB_w0  trig  v(xi_msaq_fbcc_01.cslcon0<0>)                 val='0.5*pvcsl'  td=tmeas  rise=c_csl_w0
+                 targ  v(net852<0>)-v(net941<0>)   val='0.3*pvblh'  td=tcsl_w0
*+                 targ  abs(v(net852<0>)-v(net941<0>))   val='0.3*pvblh'  td=tcsl_w0

.meas tran teqior_w0 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  rise=r_eqio_w0  print=0
.meas tran tC_w0  trig  v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)               val='0.5*pvdleq'  td=tmeas  rise=r_eqio_w0
+                 targ  abs(v(xi_msaq_fbcc_01.xi_msax384_l.io0l<0>)-v(xi_msaq_fbcc_01.xi_msax384_l.ion0l<0>))  val='0.02*pvintlp'  td=teqior_w0

.meas tran tCCD_W0  param='tA_w0 + tB_w0 + tC_w0'


*============================
*        Read1 tCCD
*============================

.meas tran teqiof_r1 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  fall=f_eqio_r1  print=0
.meas tran tcslr_r1 when v(xi_msaq_fbcc_01.cslcon0<0>)  val='0.5*pvcsl'  td=tmeas  rise=f_eqio_r1  print=0
.meas tran trden_r1  when v(xi_msaq_fbcc_01.xi_msax384_l.rdenmid)  val='0.5*pvdleq'  td=tmeas  rise=c_rden_r1  print=0
.meas tran tA1_r1  param='tcslr_r1 - teqiof_r1'
.meas tran tA2_r1  param='trden_r1 - tcslr_r1'

.meas tran tB_r1  trig  v(xi_msaq_fbcc_01.xi_msax384_l.rdenmid)  val='0.5*pvdleq'  td=tmeas  rise=c_rden_r1
+                 targ  abs(v(xi_msaq_fbcc_01.xi_msax384_l.yio0p<0>)-v(xi_msaq_fbcc_01.xi_msax384_l.yion0p<0>))            val='0.15'       td=trden_r1

.meas tran teqior_r1 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  rise=r_eqio_r1  print=0
.meas tran tC_r1  trig  v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)               val='0.5*pvdleq'  td=tmeas  rise=r_eqio_r1
+                 targ  abs(v(xi_msaq_fbcc_01.xi_msax384_l.io0l<0>)-v(xi_msaq_fbcc_01.xi_msax384_l.ion0l<0>))  val='0.02*pvintlp'  td=teqior_r1

.meas tran tCCD_R1  param='tA1_r1 + tA2_r1 + tB_r1 + tC_r1'

*============================
*        Read0 tCCD
*============================

.meas tran teqiof_r0 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  fall=f_eqio_r0  print=0
.meas tran tcslr_r0 when v(xi_msaq_fbcc_01.cslcon0<0>)  val='0.5*pvcsl'  td=tmeas  rise=f_eqio_r0  print=0
.meas tran trden_r0  when v(xi_msaq_fbcc_01.xi_msax384_l.rdenmid)  val='0.5*pvdleq'  td=tmeas  rise=c_rden_r0  print=0
.meas tran tA1_r0  param='tcslr_r0 - teqiof_r0'
.meas tran tA2_r0  param='trden_r0 - tcslr_r0'

.meas tran tB_r0  trig  v(xi_msaq_fbcc_01.xi_msax384_l.rdenmid)  val='0.5*pvdleq'  td=tmeas  rise=c_rden_r0
+                 targ  abs(v(xi_msaq_fbcc_01.xi_msax384_l.yio0p<0>)-v(xi_msaq_fbcc_01.xi_msax384_l.yion0p<0>))            val='0.15'       td=trden_r0

.meas tran teqior_r0 when v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)  val='0.5*pvdleq'  td=tmeas  rise=r_eqio_r0  print=0
.meas tran tC_r0  trig  v(xi_msaq_fbcc_01.xi_msax384_l.eqiomid)               val='0.5*pvdleq'  td=tmeas  rise=r_eqio_r0
+                 targ  abs(v(xi_msaq_fbcc_01.xi_msax384_l.io0l<0>)-v(xi_msaq_fbcc_01.xi_msax384_l.ion0l<0>))  val='0.02*pvintlp'  td=teqior_r0

.meas tran tCCD_R0  param='tA1_r0 + tA2_r0 + tB_r0 + tC_r0'


.tran 10p 55n sweep data=yioloading
