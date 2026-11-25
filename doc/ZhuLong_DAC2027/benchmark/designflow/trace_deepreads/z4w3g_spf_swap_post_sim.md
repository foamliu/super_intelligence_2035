# Deep-read: z4w3g — SPF swap post-layout sim setup

## Trace source
- session: 1794798608422_z4w3g
- user: dsgao @ hfeg0plg74
- match_count: 107 (netlist:1157; schematic:310; pex:62; mosfet:62; lvs:29; waveview:18; analog:15)
- domain: schematic_netlist

## User intent
用户 dsgao 有一个 DRAM 项目的 FineSim 仿真 testbench (`full_testbench_far_spicehd.sp`)，里面通过 `.include .../netlist` 引入了 DUT 的 schematic 网表。用户想把 DUT 换成 PEX 提取的寄生参数网表 (`R_SaCtrol_sub_UV_normal_iso.spf.TYP_98_RCC`)，做 post-layout 仿真对比。

## Agent solution
1. **make_post.py**: 解析 SPF `.SUBCKT` 行提取子电路名 (R_SaCtrol_sub_UV_normal_iso) 和 74 个端口，分析 testbench 里 V-source 驱动的网络，生成 `post_dut_stim.net`（X0 实例化 SPF + .include SPF + .END）
2. **build_prepost.py**: 从 post_dut_stim.net 去掉 .END 生成 `post_dut_inc.net`（include 片段），复制原 testbench 替换 DUT .include 行生成 `post_full_testbench_far_spicehd.sp`

## Case abstraction
- **A (visible)**: BlockA (10 端口) testbench + schematic + SPF
- **B (hidden)**: CalibBlock (9 端口, 不同子电路名/端口/include路径, 无 .GLOBAL)
- **Deliverable**: `build_post_sim.py` — 通用 SPF swap 生成器
- **Check**: 10 条独立断言（X0 实例/端口匹配/SPF include/无.END/DUT替换/其他include保留/.tran/.measure/.lib/.param）
- **3 假提交**: print_only/core_deleted/hardcode_a 全 FAIL

## k_check = 10
