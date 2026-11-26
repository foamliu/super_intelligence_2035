.option accurate runlvl=6
.option probe
*.option list
.option GMIN=1e-16 GMINDC=1e-16
.option measdgt=6 numdgt=6 INGOLD=2 post=2 tnom=25 dccap  method=gear
*.option autostop
.option MEASFORM=3 MEASFILE=1
.option seed=40214
.option MAXWARNS=100

.param tperiod=4n tr=0.2n tf=0.2n tduty=1.8n

.param sel_cond=0
** sel_cond: 0 is tt25C; 1 is ss-40C; 2 is ff110C
.param sel_plat=0
** sel_plat: 0 is dejoa; 1 is drcoa; 2 is drgqa; 3 is GL22
.param sel_sweep=0
** sel_sweep: keep only 0 (Lsweep)
.param sel_case=2
** sel_case: keep only 2 (fixed W)
.param sel_mos=0
** sel_mos: 0 is ptk/ntk; 1 is ptk_lv/ntk_lv

.if(sel_plat==0)
.inc 'DEJOA_invs.sp'

.elseif(sel_plat==1)
.inc 'DRCOA_invs.sp'

.elseif(sel_plat==2)
.inc 'DRGQA_invs.sp'

.elseif(sel_plat==3)
.inc 'GL22_invs.sp'

.endif

.alter
.param sel_plat=0 sel_mos=1 sel_cond=0 sel_case=2

.alter
.param sel_plat=0 sel_mos=0 sel_cond=1 sel_case=2

.alter
.param sel_plat=0 sel_mos=1 sel_cond=1 sel_case=2

.alter
.param sel_plat=0 sel_mos=0 sel_cond=2 sel_case=2

.alter
.param sel_plat=0 sel_mos=1 sel_cond=2 sel_case=2

.alter
.param sel_plat=1 sel_mos=0 sel_cond=0 sel_case=2

.alter
.param sel_plat=1 sel_mos=1 sel_cond=0 sel_case=2

.alter
.param sel_plat=1 sel_mos=0 sel_cond=1 sel_case=2

.alter
.param sel_plat=1 sel_mos=1 sel_cond=1 sel_case=2

.alter
.param sel_plat=1 sel_mos=0 sel_cond=2 sel_case=2

.alter
.param sel_plat=1 sel_mos=1 sel_cond=2 sel_case=2

.alter
.param sel_plat=2 sel_mos=0 sel_cond=0 sel_case=2

.alter
.param sel_plat=2 sel_mos=1 sel_cond=0 sel_case=2

.alter
.param sel_plat=2 sel_mos=0 sel_cond=1 sel_case=2

.alter
.param sel_plat=2 sel_mos=1 sel_cond=1 sel_case=2

.alter
.param sel_plat=2 sel_mos=0 sel_cond=2 sel_case=2

.alter
.param sel_plat=2 sel_mos=1 sel_cond=2 sel_case=2

.alter
.param sel_plat=3 sel_mos=0 sel_cond=0 sel_case=2

.alter
.param sel_plat=3 sel_mos=1 sel_cond=0 sel_case=2

.alter
.param sel_plat=3 sel_mos=0 sel_cond=1 sel_case=2

.alter
.param sel_plat=3 sel_mos=1 sel_cond=1 sel_case=2

.alter
.param sel_plat=3 sel_mos=0 sel_cond=2 sel_case=2

.alter
.param sel_plat=3 sel_mos=1 sel_cond=2 sel_case=2

.end
