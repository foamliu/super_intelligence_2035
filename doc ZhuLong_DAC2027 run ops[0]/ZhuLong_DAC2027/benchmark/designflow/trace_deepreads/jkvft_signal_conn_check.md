# deepread: 1794185877917_jkvft — signal connectivity check (jinhaoli@hfeg0pgn145)

- **trace**: jinhaoli@hfeg0pgn145, session 1794185877917_jkvft.messages.json, 423 msgs / 1.48MB, mc=390, domain schematic_netlist (netlist:1553+verilog:821+cmos:53+schematic:38+analog:12).
- **user intent (U#0 逐字)**: 「/rundata/drgqx/V0/simdir/verilog/jinhaoli/verilog.ddr5.drgqx.1106/s 是所有要检查的test mode 信号列表，…/netlist/V0_WOWTOP_2026Nov8.130107/netlist是对应的网表，请把s文件中的每个信号对应的输出信号找出来并输出到一个文件中，检查其链接性是不是正确」
- **follow-ups**: U#109 (输出+模块, gvim 无乱码), U#142 (列所在模块名), U#157 (终端输出模块+信号名+连接性), U#179 (继续). 3 个 follow-up 均纯需求轮; 选 U#0 (原始最完整, A-faithful).
- **real assets**: s 文件 143 test-mode 信号 (cm1_ro_2StepSenseAdj<3>/cm1_cl_RmwEqIo_Int/cm1_ro_NcAdjB0<0> 等, <n> 尖括号→网表 [n]); 网表 37MB Verilog 门级, Top WOWTOP, 3826 module, cell T_CmFsLatchX6L_Ary/nor2Lx2/invLx1 等. 真实 NFS 不可沙盒.
- **agent tool chain**: 迭代 analyze_netlist.py→sigcheck.py→make_gvim.py→list_modules.py→conn_check_v3.py→full_conn_check.py (多次 editor 拒绝/超时/SIGKILL, 最终收敛). gold: signal_connectivity_detail.txt Total:143 OK:87 ND:0 NL:48 MD:23.
- **reframe**: 紧凑 Verilog 文本 (保留真实文件头/模块名/cell 类型/信号名, cell 输出 pin 由 // cellpinout: 头部声明, 器件正文省略/concat 折叠). A 12 信号 gold {total:12,ok:7,nd:2,nl:2,md:1}; hidden B 10 信号命名不相交 gold {total:10,ok:6,nd:2,nl:1,md:1}.
- **case**: EDA-Eval-DesignFlow-SignalConnCheckProduce-001, produce-script signal_conn_check.py (双参 CLI), check.py 15 断言 a-o, ref 15/15 PASS, 3 neg 全 FAIL. k_check=k_rationale=15.
- **ledger**: jkvft 旧 B-parked (11-09, wrong-shard netlist→A 标注, 实为 D schematic_netlist); 本轮 --force cross-shard-reclaim revival #6, mark case.
