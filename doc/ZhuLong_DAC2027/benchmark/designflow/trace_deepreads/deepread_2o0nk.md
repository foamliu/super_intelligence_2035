# 深读笔记 · 2o0nk (e0046913@hfeg0pkn003, mc107)

- **session**: 1793859562375_2o0nk.messages.json (1.17MB, 131 msgs, 72 user turns, agent=lead)
- **真实任务**: DC 综合 log 报错分析。USER#0 逐字: "/proj/lacaa/TV1_digital/simdir/yutingq/lowpowerDC_for_IP/logs/dc.log 分析log报错原因及解决方案"
- **设计**: SramPwrTcqGrp0（6 片大 SRAM 宏 + 多电源域 UPF 隔离），DC V-2023.12-SP5
- **核心错误**: dc.log line 888 `Error: A supply net cannot be determined for the power pin VSS on the cell hcsp8kx160cm4b8c1r1_dbc_big_pwr_tcq_g0_i0. (UPF-579)`（ground truth 来自 scan_upf.py 对真实 log 的正则扫描）
- **次要**: SEC-51 license 误用 (line 560, 非致命) + VO-12 未映射 (line 721/723/1314-1351) + WT-7 黑盒 (line 1307) —— 均 UPF-579 下游症状
- **UPF 结构** (log echo line 729-809): create_supply_port VDD/VSS/VDDI0-5/VSSI0-5; create_supply_net VDDN/VSSN/VDDI0-5N/VSSI0-5N; connect_supply_net 绑顶层端口; create_power_domain TOP + PD_I0..I5 (各含 1 SRAM 实例) + set_domain_supply_net PD_Ix VDDIxN/VSSIxN
- **根因**: SRAM 宏 .db/.lib 的 pg_pin VDD/VSS (primary_power/primary_ground) 无法被映射到 UPF 电源域的 supply net（PD_I0 绑 VDDI0N/VSSI0N，但叶子 pg_pin 名 VDD/VSS 与 connect_supply_net 绑的端口 VDDI0/VSSI0 不一致 → compile_ultra 时 supply net 无法确定）
- **agent 诊断**: ASST 首轮叙述误称 UPF-580（实际 log 为 UPF-579，scan_upf 正则仅命中 579）；area/qor report 证实全黑盒（组合/时序 area=0，macro area=6,233,789，macros=12）→ 综合实际失败
- **用户纠偏**: USER#52 指出 .db 是软链接→真实 lib 路径 /proj/lacaa/.../libs/ev/...（agent 勘误后 scan_syml 确认）；USER#60-65 提供 report_supply_net/report_power_domain/get_attribute 交互式 dc_shell 输出
- **金标准 (USER#66 用户接受)**: 解决方案 ① set_app_var dc_allow_rtl_pg true（默认关）② 不读 UPF（改名 upf/ 使 dc 无法 load_upf）③ write -pg -format verilog；验证 result/mapped.v 含 inout VDD/VSS pg pin（check_pg.py: PG_HITS=21, line 8303-8316 inout VSSI0/VDDI0/.../VDD/VSS）
- **资产可取性**: /proj/lacaa 路径 e0031982 无权限（.75 + ssh hfeg0pkn003 均 Permission denied）；真实 dc.log 内容经 trace 内 scan_dc.py/scan_upf.py 工具产物重建（faithful excerpt，含全部真实 error/warning/UPF 行）
- **A-faithful rule2 合规**: USER#0 为干净需求轮（仅"分析log报错原因及解决方案"，未给根因/方案）；USER#52/66 给根因+方案 → 仅作 gold，不进 prompt
- **case 产出**: EDA-Eval-DesignFlow-DcUpfPgDiagnose-001 (digital, A档 faithful, L1-static, 16 conds a-p, 候选=gen_dc_upf_diagnose.py 通用 DC UPF-579 诊断器 CLI)
- **B 档合成隐藏**: DdrPhyPwrGrp0（4 DDR PHY 实例, VDD pin error, VDDP*N/VSSP*N, PD_P0..P3），与 A 零标识符重叠
