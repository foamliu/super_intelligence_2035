# 深读：1794299744954_i3u9r — netlist IO PAD CA[3:0] 驱动逻辑追踪

- trace: sfeng @ hfeg0pkn003 (10.129.2.12), mc=192, digital, 157 msgs / 5 user-turns, scan ssh_eda_search_20261113_131349
- 工作目录: `/proj/decqa/V0/simdir/verilog/xfeng/1103_lp6tb/`，netlist 符号链接 → `/rundata/decqa/V0/simdir/verilog/eric1ch/netlist/V0_LP6TOP_2026Oct26.185525/`

## 用户意图（原话）
- U#1: 「请在目录...下分析，找到netlist中IO PAD CA[3:0]的驱动逻辑」
- U#2: 「你还在分析吗？为什么不显示工作中，也没有任何结果输出？」（催促）
- U#3: 「请搜索相关的testcase, task definition, 给出在testbench层对CA0【3：0】的驱动输入」
- U#4/#5: 「这样的驱动形式，如何使CA【3：0】为高阻态，难道要直接load value为z吗？」

## agent 工具链
list_allowed_files(10) + read_files(28) + run_approved_command(31) + editor(7) + SandBox_MCP_run_code(1) + get_agent_policy_status(1)
- editor 产出 7 个 python 搜索脚本: search_ca.py / search_ca2.py / search_ca3.py / search_ca4.py / search_ca5.py / search_tb_ca.py / search_tb_ca2.py（写到 /home/sfeng/，经 python-runner 跑）

## 关键发现（agent 产出）
**netlist 侧（U#1）**:
1. LP6TOP 顶层端口（line 1104975-76）: `input [3:0] CA0;` `input [3:0] CA1;`（各 4-bit input）
2. 内部 `CA[0:3]` 隐式 wire（bit-select 引用，未显式声明）
3. `CaRcvCoreM6_coa I_CaRcv` 实例（line 981921-42）: `.CA0Pad(CA[0]), .CA1Pad(CA[1]), .CA2Pad(CA[2]), .CA3Pad(CA[3]), .CSPad(CS), .CAO(...)`
4. CaRcvCoreM6_coa 模块端口方向（line 827538-41）: `input CA0Pad; input CA1Pad; input CA2Pad; input CA3Pad;` → CA[0:3] 仅接到 **input** 端口
5. 结论: CA[0:3] 在 LP6TOP 体内**无内部驱动**（只接 input，无 assign，非 top output）→ 浮空/由外部 PAD 驱动

**testbench 侧（U#3）**:
- lpddr6_specdef.sv line 4: `parameter int CA_BITS = 4;`
- lpddr6_interface.sv line 13: `logic[CA_BITS-1:0] CA;` → 4-bit
- loadca task / load_cmdR / load_cmdF / load_cmdpinhalfcycle
- PDRIVER.CA[i] <= #(lpddr6.tb_ca[i].tis) ...（line 339-373 驱动逻辑）

**高阻态（U#4/#5）**:
- TYPE_pin.val 是 reg（4 态: 0/1/x/z），可表示 z
- loadca 的 `integer val` 是 2 态，传 z 会丢 → 需走 val 直接赋 'z' 或 force_flag 机制

## A-faithful 判定
合格。用户给路径 + 信号名 + 目标（找驱动逻辑），未给解析算法 / 端口方向判定规则 / 分类规则。

## deliverable 判定
读取/分析私有 `/proj/decqa/.../` + `/rundata/decqa/.../` 文件 → .75 Permission denied → **INFEASIBLE** → **B 档合成**

## 合成方案
**EDA-Eval-DesignFlow-NetlistPadDriverTrace-001**（digital L1-B，archetype=netlist-pad-driver-tracer）
- 单脚本 `netlist_pad_driver_trace_ref.py` 纯 stdlib CLI(--netlist/--signal/--json)
- 解析 Verilog netlist → 顶层模块定位（未被任何模块例化的 = root）→ 端口/线宽声明 → 例化端口连接 .Port(net_expr) 解析 → 子模块端口方向回查 → assign 驱动 → classification(floating_undriven / driven_by_instance_output / driven_by_assign / top_input_port)
- A=netlist_A.v(LP6TOP_A, CA[3:0] 4-bit floating, DQ driven-by-instance-output, flag_a driven-by-assign, CS top-input-port, FakeDecoyA 注释诱饵)
- B=hidden netlist_B.v(MEMTOP_B, CA[5:0] 6-bit floating, DQ driven-by-instance-output, flag_b driven-by-assign, CS top-input-port, DQTOP top-output-driven-by-assign, PhantomDecoyB 块注释诱饵)
- 跨输入守卫: A 名(LP6TOP_A/I_CaRcv/CaRcvCoreM6_coa/flag_a)不出现在 B 输出
