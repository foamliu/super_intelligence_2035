# trace_deepread r961 — ciw0o (rose3wang@hfeg0pkn003, mc165)

**session**: 1794989154211_ciw0o.messages.json
**user**: rose3wang @ hfeg0pkn003 (10.129.2.12)
**mc**: 165, keywords verilog:245/rtl:154/synthesis:18/spectre:68 主导 → A-pure digital
**size**: 848KB / 221 msgs (cline lead agent, zhulong)
**scan**: ssh_eda_search_20261121_151844 (r940 POOL_SWITCH 7x expansion)
**fresh**: NOT in any of 4 shard ledgers (4981 unique sids) — confirmed via candidates_mc10.tsv cross-ref

## 用户意图序列 (多任务 session)

- **U#0/1 (msg#0/1)**: 同步 Efuse.v 修改到 DK/release/verilog/EFUSE.v (file copy)
- **U#2 (msg#2)**: 管脚表 (17 端口: VDDA/VSSA/VMEAS/VREF/VD_EN/CHIP_EN/CONV_EN/CLK_IN/TEST_EN/TR<37:0>/RSV<5:0>/DO<10:0>/RDY/TPOD<3:0>/TPOA<0>/TPOA<1>/TPIA<1:0>/TPID<1:0>) + 「写一个verilog壳子」 ← **本 case 选用**
- **U#36 (msg#36)**: vsensor.v 写 TB (只给 clk + 例化, 激励自写)
- **U#92+ (msg#92+)**: psensor mapped netlist cell 提取 → eco_dummy_psensor.v 生成 (D1DBCP51H180L6W25T5SVT library)
- **U#186 (msg#186)**: 4 RTL (cnt_window/gen_process/osc_cnt/top_psensor) 如何加 eco_dummy 不改原文件 → wrapper
- **U#198/200 (msg#198/200)**: 根据 4 RTL 逻辑特点优化 eco dummy cell 配置
- **U#220 (msg#220)**: eco dummy 端口与 mapped netlist 不对应 (未解决, session 结束)

## trace gold (U#2 壳子任务)

assistant 分析: 管脚表 = vsensor/ADC macro 外接口; read_files Efuse.v + CHEFUSE35HDBC4K.v →
1. cp Efuse.v → EFUSE.v (release)
2. 创建 EFUSE_TOP.v: module EFUSE_TOP (pin table 17 端口); 内部例化 Efuse u_efuse; 电源 VDDA/VSSA 直通; 模拟 VMEAS/VREF 顶层留口; 控制 CHIP_EN/CONV_EN/...; 数字 TR/DO/RDY 连接; tie-off 未用端口

## 本 case 提炼

提炼为**通用 Verilog 壳子生成器** (produce-task, S2 范式):
- 输入: 管脚表 TSV (name/width/direction)
- 输出: Verilog module skeleton (正确端口方向 input/output/inout + 总线 [width-1:0] + module/endmodule)
- A = vsensor/ADC 管脚表 17 端口 (可见, trace U#2 原文)
- B = top_psensor 管脚表 17 端口 (隐藏, trace msg#188, 仅共享端口名 TR 但位宽 4 vs 38)
- check.py 15 断言 (a-o): zip+编译+A/B各产.v+端口方向+位宽+endmodule+反硬编码+确定性+反退化
- ref PASS 15/15, 5 neg 全 FAIL (empty/print-only/hardcoded-A/no-direction/wrong-widths)
- §4.9 三假 (empty/print-only/hardcoded-A) 全 FAIL ✓

## 关键判分点

- **反硬编码核心**: B 与 A 仅共享端口名 "TR"(位宽 4 vs 38), 其余 16 端口名全异 → 硬编码 A 端口名的候选在 B 上会泄漏 (neg3 FAIL)
- **位宽正确性**: width 列 = 实际位数, width>1 → [width-1:0] (非 [width:0]), neg5 off-by-one FAIL
- **方向映射**: Power/Ground → inout (非 input/output), neg4 全 wire FAIL
