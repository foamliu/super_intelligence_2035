* zl_base_template.sp — level shifter (vlshft) spice deck (143 lines)
* source: /home/hairuizh/agent_out/2026-11-13-20-00/zl_base_template.sp on 10.129.2.10
* extracted r536 via ssh from .75 (rundata path permission-denied, agent_out readable)

.option accurate runlvl=6
*.option probe
*.option list
.option GMIN=1e-16 GMINDC=1e-16
.option measdgt=6 numdgt=6 INGOLD=2 post=2 tnom=25 dccap  method=gear
*.option autostop
.option MEASFORM=3 MEASFILE=1
.option seed=40214
** spice model



** Paramters definition
*.param mis_flag=1

*.param cthin=0 cthick=0 capo=0 cgatein=0
*.param cthin=0.2f cthick=0.2f capo=0.2f cgatein=0.4f
.param cthin=0.2f cthick=0.4f capo=0.2f cgatein=0.4f
.param outload=8f
.param tperiod=4n tr=0.2n tf=0.2n tduty=1.8n

*** mos select & condition select
*.param sel_nm1=0


.param sel_cond=7

*** voltage domain
.param pvss=0
.param pvcc=1
.param pvbias2=1.256
.param pviso=1.256
.param pvintcore=0.7
.param pvwlp=2.6
.param pvdleq=1.07

*** size
.param piw=340n pil=40n
.param niw=100n nil=40n
.param pow=1260n pol=146n
.param now=700n nol=177n

.param p1w=250n p1l=146n
.param n1w=1000n n1l=177n
.param n2w=2000n n2l=40n



.param n1w=p1w*fbnpratio
.param n2w=p1w*fbnpratio*nkratio
.param intinvixn=1 fbpathxn=1 intinvoxn=1 nkratio=1.5 fbnpratio=5.6

.data myxn
+  intinvixn fbpathxn intinvoxn nkratio fbnpratio
1 1 1 1.5 5.6

.enddata



** cell,load
.inc '/proj/m2701/V0_DDR2/workdir/hairuizh/simulation/presim/lvlshft/spice/plat_condtions/GL22/conditions_new.sp'
.inc '/proj/m2701/V0_DDR2/workdir/hairuizh/simulation/presim/lvlshft/spice/zl_vintcore2vwlp/invdrvs.sp'

.param pvbias2=pviso


Xindrv indrv in vintcorei vss invSxn sxn=1

Xoutdrv out outdrv vwlpo vss invYxn yxn=6

XPMI vintcore in inN vintcore puhvt_ckt w=piw*intinvixn l=pil nf=CEIL(piw*intinvixn/2u)
XNMI inN in vss vss nuhvt_ckt w=niw l=nil nf=CEIL(niw/2u)

XPMO vwlp l1 out vwlp ptk w=pow*intinvoxn l=pol nf=CEIL(pow*intinvoxn/2u)
XNMO out l1 vss vss ntk  w=now*intinvoxn l=nol nf=CEIL(now*intinvoxn/2u)

XPML1 vwlp r1 l1 vwlp ptk w=p1w*fbpathxn l=p1l nf=CEIL(p1w*fbpathxn/2u)
XPMR1 vwlp l1 r1 vwlp ptk w=p1w*fbpathxn l=p1l nf=CEIL(p1w*fbpathxn/2u)
XNML2 l1 vbias2 l2 vss ntk_lv w=n1w*fbpathxn l=n1l nf=CEIL(n1w*fbpathxn/2u)
XNMR2 r1 vbias2 r2 vss ntk_lv w=n1w*fbpathxn l=n1l nf=CEIL(n1w*fbpathxn/2u)
XNML1 l2 in vss vss nuhvt_ckt w=n2w*fbpathxn l=n2l nf=CEIL(n2w*fbpathxn/2u)
XNMR1 r2 inN vss vss nuhvt_ckt w=n2w*fbpathxn l=n2l nf=CEIL(n2w*fbpathxn/2u)

** vcap
cg1 in 0 c='Cthin*(CEIL(piw*intinvixn/2u)+CEIL(niw*intinvixn/2u)+CEIL(n2w*fbpathxn/2u))'
cg2 inN 0 c='Cthin*(CEIL(n2w*fbpathxn/2u))'
cg5 l1 0 c='Cthick*(CEIL(pow*intinvoxn/3u)+CEIL(now*intinvoxn/3u)+CEIL(p1w*fbpathxn/3u))'
cg6 r1 0 c='Cthick*CEIL(p1w*fbpathxn/3u)'
cout1 out 0 c='CapO*(CEIL(pow*intinvoxn/3u)+CEIL(now*intinvoxn/3u))'

cgatein1 in 0 c='Cgatein'
cgatein2 indrv 0 c='Cgatein'
cgatein3 out 0 c='Cgatein'



** power
Vvdleq vdleq 0 pvdleq
Vvwlp vwlp 0 pvwlp
Vvwlpo vwlpo 0 pvwlp
Vvbias2 vbias2 0 pvbias2
Vvss vss 0 pvss
Vvintcore vintcore 0 pvintcore
Vvintcorei vintcorei 0 pvintcore
Vvindrv indrv 0 PULSE(pvintcore pvss 100n tr tf tduty tperiod)

** probe,measure

.ic V(in)=pvss V(inN)=pvintcore V(l1)=pvwlp V(r1)=pvss V(out)=pvss

.tran 0.1p 200n sweep data=myxn

.measure tran meas_tr_in TRIG v(in) VAL=0.1*pvintcore RISE=10 TARG v(in) VAL=0.9*pvintcore RISE=10
.measure tran meas_tf_in TRIG v(in) VAL=0.9*pvintcore FALL=10 TARG v(in) VAL=0.1*pvintcore FALL=10
.measure tran meas_tr_inN TRIG v(inN) VAL=0.1*pvintcore RISE=10 TARG v(inN) VAL=0.9*pvintcore RISE=10
.measure tran meas_tf_inN TRIG v(inN) VAL=0.9*pvintcore FALL=10 TARG v(inN) VAL=0.1*pvintcore FALL=10
.measure tran meas_tr_l2 TRIG v(l1) VAL=0.1*pvwlp RISE=10 TARG v(l1) VAL=0.9*pvwlp RISE=10
.measure tran meas_tf_l2 TRIG v(l1) VAL=0.9*pvwlp FALL=10 TARG v(l1) VAL=0.1*pvwlp FALL=10
.measure tran meas_tr_out TRIG v(out) VAL=0.1*pvwlp RISE=10 TARG v(out) VAL=0.9*pvwlp RISE=10
.measure tran meas_tf_out TRIG v(out) VAL=0.9*pvwlp FALL=10 TARG v(out) VAL=0.1*pvwlp FALL=10

.measure tran meas_tpr_in_l2 TRIG v(in) VAL=0.5*pvintcore FALL=10 TARG v(l1) VAL=0.5*pvwlp RISE=10
.measure tran meas_tpf_in_l2 TRIG v(in) VAL=0.5*pvintcore RISE=10 TARG v(l1) VAL=0.5*pvwlp FALL=10
.measure tran meas_tpr_l2_out TRIG v(l1) VAL=0.5*pvwlp FALL=10 TARG v(out) VAL=0.5*pvwlp RISE=10
.measure tran meas_tpf_l2_out TRIG v(l1) VAL=0.5*pvwlp RISE=10 TARG v(out) VAL=0.5*pvwlp FALL=10
.measure tran meas_tpr_in_out TRIG v(in) VAL=0.5*pvintcore RISE=10 TARG v(out) VAL=0.5*pvwlp RISE=10
.measure tran meas_tpf_in_out TRIG v(in) VAL=0.5*pvintcore FALL=10 TARG v(out) VAL=0.5*pvwlp FALL=10
.measure tran meas_tpr_in_inN TRIG v(in) VAL=0.5*pvintcore FALL=10 TARG v(inN) VAL=0.5*pvintcore RISE=10
.measure tran meas_tpf_in_inN TRIG v(in) VAL=0.5*pvintcore RISE=10 TARG v(inN) VAL=0.5*pvintcore FALL=10

.measure tran iddq_vintcore find I(Vvintcore) at=95n

.measure tran iddq_vwlp find I(Vvwlp) at=95n
.measure tran idda_vintcore AVG I(Vvintcore) FROM=100n TO=200n
.measure tran idda_vwlp AVG I(Vvwlp) FROM=100n TO=200n
.prob i(*) v(*)

.alter
.param sel_cond=8


.end
