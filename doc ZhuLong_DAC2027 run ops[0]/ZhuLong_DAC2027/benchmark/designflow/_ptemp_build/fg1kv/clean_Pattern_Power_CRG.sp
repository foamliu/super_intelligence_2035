*****Power table****************************
.if ((pvcc  >=0.9v ) && (pvcc <= 0.92v )) 
    .param pvdd1	=   1.6v
    .param pvpcsg   =   1.6v
    .param pvdleq   =   1.13v
    .param pvnoc    =   1.17v
    .param pvtsc    =   1.17v
    .param pvdiv    =   1.17v
    .param pvintlp  =  0.5*pvblh
    .param pvcslp   =   1.45v
    .param pvcsl    =   1.1v
    .if (ptemp==-40)
        .param  pvwlp       =  2.8v
        .param  pvblh       =  0.9v
        .param  pvblhbk     =  0.9v
        .param  pvmwln      =  2.4v
        .param  pviso       =  1.44v
    .elseif (ptemp==98) 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  "pvcc-0.05"
        .param  pvblhbk     =  "pvcc-0.05"
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .else 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  "pvcc-0.05"
        .param  pvblhbk     =  "pvcc-0.05"
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .endif
.elseif ((pvcc>0.92v) && (pvcc<=0.97v))
    .param pvdd1	=   1.6v
    .param pvpcsg   =   1.6v
    .param pvdleq   =   1.13v
    .param pvnoc    =   1.17v
    .param pvtsc    =   1.17v
    .param pvdiv    =   1.17v
    .param pvintlp  =  0.5*pvblh
    .param pvcsl    =   1.1v
    .param pvcslp   =   1.45v
    .if (ptemp==-40)
        .param  pvwlp       =  2.8v
        .param  pvblh       =  0.9v
        .param  pvblhbk     =  0.9v
        .param  pvmwln      =  2.4v
        .param  pviso        =  1.44v
    .elseif (ptemp==98) 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  "pvcc-0.02"
        .param  pvblhbk     =  "pvcc-0.02"
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .else 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.9v
        .param  pvblhbk     =  0.9v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .endif
.elseif ((pvcc>0.97v) && (pvcc<=1.0v))
    .param pvdd1	=   1.6v
    .param pvpcsg   =   1.6v
    .param pvdleq   =   1.13v
    .param pvnoc    =   1.17v
    .param pvtsc    =   1.17v
    .param pvdiv    =   1.17v
    .param  pvintlp     =  0.8v
     .param pvcsl    =   1.16v
     .param pvcslp   =   1.45v
    .if (ptemp==-40)
        .param  pvwlp       =  2.8v
        .param  pvblh       =  "pvcc-0.05"
        .param  pvblhbk     =  "pvcc-0.05"
        .param  pvmwln      =  2.4v
        .param  pviso       =  1.44v
    .elseif (ptemp==98) 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .else 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .endif
.elseif ((pvcc>1.0v) && (pvcc<=1.1v))
    .param pvdd1	=   1.8v
    .param pvpcsg   =   1.6v
    .param pvdleq   =   1.13v
    .param pvnoc    =   1.17v
    .param pvtsc    =   1.17v
    .param pvdiv    =   1.17v
    .param  pvintlp     =  0.8v
        .param pvcsl    =   1.16v
        .param pvcslp   =   1.5v
    .if (ptemp==-40)
        .param  pvwlp       =  2.8v
        .param  pvblh       =  0.99v
        .param  pvblhbk     =  0.99v
        .param  pvmwln      =  2.4v
        .param  pviso        =  1.44v
    .elseif (ptemp==98) 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .else 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .endif
.elseif ((pvcc>1.1v) && (pvcc<=1.2v))   
    .param pvdd1	=   2.0v
    .param pvpcsg   =   1.6v
    .param pvdleq   =   1.13v
    .param pvnoc    =   1.17v
    .param pvtsc    =   1.17v
    .param pvdiv    =   1.17v
    .param  pvintlp     =  0.8v
        .param pvcsl    =   1.22v
        .param pvcslp   =   1.5v
    .if (ptemp==-40)
        .param  pvwlp       =  2.8v
        .param  pvblh       =  1.0v
        .param  pvblhbk     =  1.0v
        .param  pvmwln      =  2.4v
        .param  pviso        =  1.44v
    .elseif (ptemp==98) 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .else 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .endif
.elseif ((pvcc>1.2v) && (pvcc<=1.4v))
    .param pvdd1	=   2.1v
    .param pvpcsg   =   1.6v
    .param pvdleq   =   1.13v
    .param pvnoc    =   1.17v
    .param pvtsc    =   1.17v
    .param pvdiv    =   1.17v
    .param  pvintlp     =  0.8v
        .param pvcsl    =   1.3v
        .param pvcslp   =   1.6v
    .if (ptemp==-40)
        .param  pvwlp       =  2.8v
        .param  pvblh       =  1.0v
        .param  pvblhbk     =  1.0v
        .param  pvmwln      =  2.4v
        .param  pviso        =  1.44v
    .elseif (ptemp==98) 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .else 
        .param  pvwlp       =  2.6v
        .param  pvblh       =  0.95v
        .param  pvblhbk     =  0.95v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .endif

.elseif ((pvcc>1.4v) && (pvcc<1.5v))
    .param pvdd1	=   2.1v
    .param pvpcsg   =   2.1v
    .param pvdleq   =   pvcc
    .param pvnoc    =   pvcc
    .param pvblh    =   0.95v
    .param pvtsc    =   pvcc
    .param pvdiv    =   pvcc
    .param  pvintlp     =  0.8v
        .param pvcsl    =   1.3v
        .param pvcslp   =   1.6v
    .if (ptemp==-40)
        .param  pvwlp       =  2.8v
        .param  pvmwln      =  2.4v
        .param  pviso        =  1.44v
    .elseif (ptemp==98) 
        .param  pvwlp       =  2.6v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .else 
        .param  pvwlp       =  2.6v
        .param  pvmwln      =  2.2v
        .param  pviso       =  1.36v
    .endif

.elseif ((pvcc>=1.5v) && (pvcc<1.55v))
    .param pvwlp    =   3.7v
    .param pvdd1	=   2.52v
    .param pvpcsg   =   2.3v
    .param pvmwln   =   pvwlp
    .param pviso    =   pvdd1
    .param pvdleq   =   pvcc
    .param pvnoc    =   pvcc
    .param pvblh    =   pvcc
    .param pvtsc    =   pvcc
    .param pvdiv    =   pvcc
    .param  pvintlp     =  0.8v
        .param pvcsl    =   pvcc
        .param pvcslp   =   pvcc
.elseif ((pvcc>=1.55v) && (pvcc<=1.65v))
    .param pvwlp    =   3.7v
    .param pvdd1	=   2.6v
    .param pvpcsg   =   2.5v
    .param pvmwln   =   pvwlp
    .param pviso    =   pvdd1
    .param pvdleq   =   pvcc
    .param pvnoc    =   pvcc
    .param pvblh    =   pvcc
    .param pvtsc    =   pvcc
    .param pvdiv    =   pvcc
    .param  pvintlp     =  0.8v
        .param pvcsl    =   pvcc
        .param pvcslp   =   pvcc
.endif

.param  pvdpg       =  pvdiv
.param  pvdd        =  pvcc
.param  vvdd        =  pvdd
.param  vvss        =  pvss
.param  pvpp        =  pvdd1
.param  pvppex      =  pvdd1
.param  pvdd2       =  pvdd
.param  pvdll       =  pvdd
.param  pvddq       =  pvdd
.param  pvss        =  0
.param  pvbn        =  -0.1v
.param  pvkb        =  -0.7v
.param  pvbp        =  pvcc
.param  pvncsgn     =  -0.2v
.param  pvncsgh     =  1.35v
.param  pvad2o      =  pvblh*0.5
.param  pvad2e      =  pvblh*0.5
.param  pvad2       =  pvblh*0.5
.param  pvap2       =  pvblh*0.5
.param  pvwln       =  -0.2v
.if (pvcc >= 1.1v)
    .param  pvrefdq     =  pvddq*0.8
.elseif (pvcc<1.1v)
    .param  pvrefdq     =  "pvddq-0.1"
.endif
.param  pvrefca     =  pvddq*0.75
.param  pvrefcs     =  pvddq*0.75

**.param  pvrefdq     =  pvddq*0.75
***********Fuse Power define************
*.param  pvfsbln                   =  5v
*.param  pvfsblnFsGateUnsel        =  2v
*.param  pvfsblnXGate              =  2.5v
*.param  pvThinfsgdl               =  2.5v
*.param  pvFsRdFsGate              =  1.5v
*.param  pvFsRdXGate               =  1.35v
*.param  pvFsCompRef               =  pvss
*.param  pvfsgt                    =  pvwlp
*.param  pvfsgdl                   =  pvwlp
*.param  pvfsbln                   =  pvcc
*.param  pvfsrdb                   =  pvcc



.param  pvfsxgt                   =1.35v   
.param  pvfsgdl                   =pvwlp 
.param  pvfsrdfsgt                =1.5v
.param  pvfsbln                   =4.8v   
.param  pvfsrdcompgt              =0.25v
.param  pvfsrdb                   =0.46v
.param  pvfsblnfsgtn              =pvdd1


.param  pvfsblnxgt                =2.5v
.param  pvfsrdxgt                 =1.35v 
.param  pvfsrdbp                  =1.5v
**************end fuse define
.param  pvrefse_ck  =  pvddq*0.5
.param  pvrefdqn    =  pvddq*0.7

.param  VIL="pvdd*0.75-0.100"
.param  VIH="pvdd*0.75+0.100"
.param  VILDQ="pvrefdq-0.1"
.param  VIHDQ="pvrefdq+0.1"
.param  VVTT="pvdd"
.param pvad2s = pvblh*0.5
****20250429zguangming.param pvdsag = 1.37v
.param pvibcom  =   0.2v

vdpg     vdpg!    0  dc=pvdpg    power=0
**vdsag     vdsag!    0  dc=pvdsag    power=0
vad2s     vad2s!    0  dc=pvad2s  power=0
vad2e    vad2e!   0  dc=pvad2e   power=0
vad2o    vad2o!   0  dc=pvad2o   power=0
vad2     vad2!    0  dc=pvad2    power=0
vap2     vap2!    0  dc=pvap2    power=0
vblh     vblh!    0  dc=pvblh    power=0
vblhbk   vblhbk!  0  dc=pvblhbk  power=0
vbn      vbn!     0  dc=pvbn     power=0
vcc      vcc!     0  dc=pvcc     power=0
vbp      vbp!     0  dc=pvbp     power=0
vcsl     vcsl!    0  dc=pvcsl    power=0
vcslp    vcslp!   0  dc=pvcslp   power=0
vdd      vdd!     0  dc=pvdd     power=0
vdd1     vdd1!    0  dc=pvdd1    power=0
vdd2     vdd2!    0  dc=pvcc     power=0
vddq     vddq!    0  dc=pvddq    power=0
vddqca   vddqca!  0  dc=pvddq    power=0
vdiv     vdiv!    0  dc=pvdiv    power=0
vdleq    vdleq!   0  dc=pvdleq   power=0
vdll     vdll!    0  dc=pvcc     power=0
viso     viso!    0  dc=pviso    power=0
vkb      vkb!     0  dc=pvkb     power=0
vmwln    vmwln!   0  dc=pvmwln   power=0
vintlp   vintlp!  0  dc=pvintlp  power=0
vncsgh   vncsgh!  0  dc=pvncsgh  power=0
vncsgn   vncsgn!  0  dc=pvncsgn  power=0
vnoc     vnoc!    0  dc=pvnoc    power=0
vpcsg    vpcsg!   0  dc=pvpcsg   power=0
vppex    vppex!   0  dc=pvppex   power=0
vpp      vpp!     0  dc=pvpp     power=0
vss      vss!     0  dc=pvss     power=0
vssz      vssz!     0  dc=pvss     power=0
vccz      vccz!     0  dc=pvcc     power=0
vssdll   vssdll!  0  dc=pvss     power=0
vssq     vssq!    0  dc=pvss     power=0
vssqca   vssqca!  0  dc=pvss     power=0
vtsc     vtsc!    0  dc=pvtsc   power=0
vwln     vwln!    0  dc=pvwln    power=0
vwlp     vwlp!    0  dc=pvwlp    power=0
vibcom   vibcom!  0  dc=pvibcom  power=0

vbulkn   vbulkn!  0  dc=pvbn     power=0
vbulkp   vbulkp!  0  dc=pvbp     power=0
************************fuse  power********************************************


vfsxgt                  vfsxgt!               0  dc=pvfsxgt                       power=0
vfsgdl                  vfsgdl!                0  dc=pvfsgdl                       power=0
vfsrdfsgt               vfsrdfsgt!             0  dc=pvfsrdfsgt                    power=0
vfsbln                  vfsbln!                0  dc=pvfsbln                       power=0
vfsrdcompgt             vfsrdcompgt!           0  dc=pvfsrdcompgt                  power=0
vfsrdb                  vfsrdb!                0  dc=pvfsrdb                       power=0
vfsblnfsgtn             vfsblnfsgtn!           0  dc=pvfsblnfsgtn                  power=0      
**vfsblnxgt               vfsblnxgt!             0  dc=pvfsblnxgt                    power=0
**vfsrdxgt                vfsrdxgt!              0  dc=pvfsrdxgt                     power=0
**vfsrdbp                 vfsrdbp!               0  dc=pvfsrdbp                      power=0
************************vector param*******************************************
.param VIH_TEN  = pvddq*0.8
.param VIL_TEN  = pvddq*0.2
.param Trf_TEN  = 500 
.param VIL_RST = pvddq*0.2
.param VIH_RST = pvddq*0.8
.param Trf_RST = 500 
.param VIH_ALERT  = pvddq
.param VIL_ALERT  = pvss
.param VIH_MIR  = pvddq
.param VIL_MIR  = pvss
.param VIH_CAI  = pvddq
.param VIL_CAI  = pvss
.param VIH_ODT  = pvddq
.param VIL_ODT  = pvss
.param pvinse_ca = 0.1
.param VIL_CA  = 'pvrefca-pvinse_ca'
.param VIH_CA  = 'pvrefca+pvinse_ca'
.param pvindiff_ck = 0.1
.param pvinbase_ck = pvrefca
.param VIL_CK  = 'pvinbase_ck -pvindiff_ck'
.param VIH_CK  = 'pvinbase_ck+pvindiff_ck'
.param pvinse_dq = 0.1
.param Trf_DQ = 80
.param VIL_DQ  = 'pvrefdq-pvinse_dq'
.param VIH_DQ  = 'pvrefdq+pvinse_dq'
.param VIL_TDQ  = pvss
.param VIH_TDQ  = pvdd
.param pvinse_dqs = 0.1
.param Trf_DQS = 80
.param VIL_DQS = 'pvrefdq-pvinse_dqs'
.param VIH_DQS = 'pvrefdq+pvinse_dqs'
.param Trf_CA  = 80
.param Trf_ck  = 80
.param Tdly    = 0

.param VOL_DQ  = (pvddq*0.7)-0.02
.param VOH_DQ  = (pvddq*0.7)+0.02 
.param VOL_DQS  = (pvddq*0.5)-0.2
.param VOH_DQS  = (pvddq*0.5)


**default setting for tDQS2DQ, if not trainned at special corern, latch data will be fail 
.param pVregDqs = 1.5
.param TDQSCK  =  3810

** for pincheck **
**voh voh_sim 0 dc=VOH_DQ power=0
.param pvinse = 0.02
.param VOL_DQtest = 'pvrefdq-pvinse'
.param VOH_DQtest  = 'pvrefdq+pvinse'
vol vol_sim 0 dc=VOL_DQ  power=0
voh voh_sim 0 dc=VOH_DQ  power=0
*************Array parameter and vcap parameter**************
*.inc "./Array_vcap_Param_CRG.sp"

*****X8/X4/X16 force****
.PARAM ORG
.if (ORG == 4)
    VORGX4              XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net015      0 pwl 0 0 79n 0 80n pvcc 
    VORGX8              XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net018      0 pwl 0 0 79n 0 80n 0
    VORGX16             XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net012     0 pwl 0 0 79n 0 80n 0
.elseif (ORG == 16)
    VORGX4              XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net015      0 pwl 0 0 79n 0 80n 0 
    VORGX8              XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net018      0 pwl 0 0 79n 0 80n 0
    VORGX16             XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net012     0 pwl 0 0 79n 0 80n pvcc
.elseif (ORG == 8)
    VORGX4              XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net015      0 pwl 0 0 79n 0 80n 0 
    VORGX8              XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net018      0 pwl 0 0 79n 0 80n pvcc
    VORGX16             XIctop.XI_PERI0.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_OrgX416.net012     0 pwl 0 0 79n 0 80n 0
.endif

*******CL SF 56to42****
**vrdlatencyto56  xi_peri0.xi_bcenter.xi_bcenterca.cm1_fc_rdlatencyto56  0 pvcc
************Alert external resistor****
**XI_ALERT_n   ALERT_n   vddq! IO_DqLdMdl
*******enlarge DQ eye window****
*Vcm1_io_VgaCtleC2 XI_PERI0.XI_BCenter.XI_BCenterDQ.XI_D_DQBYTELOW_0.cm1_io_VgaCtleC<2> 0 "pvdd"
*Vcm1_io_VgaCtleC1 XI_PERI0.XI_BCenter.XI_BCenterDQ.XI_D_DQBYTELOW_0.cm1_io_VgaCtleC<1> 0 "pvdd"
*Vcm1_io_VgaCtleC0 XI_PERI0.XI_BCenter.XI_BCenterDQ.XI_D_DQBYTELOW_0.cm1_io_VgaCtleC<0> 0 "pvdd"
*Vvgactler0        xi_peri0.xi_bcenter.xi_bcenterdq.xi_d_dqbytelow_0.cm1_io_vgactler<0> 0 "pvdd"