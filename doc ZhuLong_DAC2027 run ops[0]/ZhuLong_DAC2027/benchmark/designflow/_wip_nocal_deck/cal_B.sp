* cal_only.sp : comparator input-offset CALIBRATION (1-bit cap) + post-cal offset measurement
.param vddbx=1.0 vhalfbx=0.5
.model nchb nmos level=1 vto=0.7 kp=50u gamma=0.0 lambda=0.05 nsub=1e16 u0=600 tpg=1
.model pchb pmos level=1 vto=-0.7 kp=20u gamma=0.0 lambda=0.05 nsub=1e16 u0=600 tpg=1
.subckt cmp_dut_b ipb inb outb vddb vssb
Mp1b  n1b  ipb  vddb vddb pchb w=1.5u l=150n
Mn1b  n1b  ipb  vssb vssb nchb w=5u   l=150n
Mp2b  n2b  n1b  vddb vddb pchb w=4u   l=150n
Mn2b  n2b  n1b  vssb vssb nchb w=2u   l=150n
Mp3b  outb n2b  vddb vddb pchb w=8u   l=150n
Mn3b  outb n2b  vssb vssb nchb w=4u   l=150n
Clb   outb vssb 4f
.ends
VVDDb vddb 0  vddbx
VVSSb vssb 0  0
Vipb  ipb  0  pwl(0 0, 8n vddbx)
Vinb  inb  0  vhalfbx
Ccalb cal_nb 0  15f
Rcalb cal_nb 0 1meg
Mcalb outb cal_enb cal_nb vssb nchb w=2u l=150n
Vinitb  initb   0 pulse(vddbx 0 0 1n 1n 4n 10n)
Vclkb   cal_clkb 0 pulse(0 vddbx 6n 1n 1n 2n 16n)
Venb    cal_enb  0 pwl(0 0, 7.5n 0, 8n vddbx)
xcmpb ipb inb outb vddb vssb cmp_dut_b
.tran 10p 10n 0 10p
.measure tran vtrip_at_b find v(ipb) when v(outb)=vhalfbx cross=1
.measure tran offset_b param='vtrip_at_b-vhalfbx'
.end
