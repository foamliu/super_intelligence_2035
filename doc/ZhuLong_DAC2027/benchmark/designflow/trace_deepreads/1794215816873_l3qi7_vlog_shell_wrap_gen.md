# Deepread — 1794215816873_l3qi7 (rose3wang @ hfeg0pkn002 / 10.129.2.11)

**Session**: 1794215816873_l3qi7, mc80 (11-16 scan), 83 msgs / 305KB, mtime Nov 16 11:08 (活会话).
**Domain**: digital (verilog:221; rtl:46; primetime:6; tempus:5; synthesis:4 — pure A).
**Case**: EDA-Eval-DesignFlow-VlogShellWrapGen-001 (A.jsonl 366→367).

## 用户意图 (多轮)
- **U#0/U#1**: 同步 `/proj/lacaa/V0/workdir/rose3wang/rtl/efuse/Efuse.v` → `DK/release/verilog/EFUSE.v` (文件同步).
- **U#2** ← 本 case 选取: 给出 18 端口管脚表 (VDDA/VSSA/VMEAS/VREF/VD_EN/CHIP_EN/CONV_EN/CLK_IN/TEST_EN/TR<37:0>(38)/RSV<5:0>(6)/DO<10:0>(10)/RDY/TPOD<3:0>(4)/TPOA<0>/TPOA<1>/TPIA<1:0>(2)/TPID<1:0>(2)) + 「写一个verilog壳子」, 内部例化 Efuse 宏.
- **U#36**: 给 vsensor.v 写一个 tb (只给 clk + 例化端口).
- **U#50/U#52**: 模拟模块上电下电顺序检查能否写成 $setup/$recovery 格式 + lib 是否一一对应 (timing-check spec Q&A).

## 助手行为 (针对 U#2)
1. read_files Efuse.v + DK/release/verilog/ 列表 + CHEFUSE35HDBC4K.v → 对比两文件端口差异.
2. run_approved_command cp Efuse.v → EFUSE.v (完成同步).
3. editor 生成 `/home/rose3wang/EFUSE_TOP.v` (msg#23, 完整 wrapper):
   - `module EFUSE_TOP (...)`: 18 个顶层端口 (管脚表, 方向/宽度正确, TPOA<0>/<1> 合并为 TPOA0/TPOA1).
   - `Efuse u_efuse (...)`: 内部例化, 同名按名连接 (.VDDA(VDDA)/.VSSA(VSSA)/.CLK_IN(clk)/.TEST_EN({5{TEST_EN}})), 异名留空 (.TEST_CK1()/.TEST_CK2()), 部分位选 (.TR(TR[11:0])).
   - 控制 FSM (IDLE/READ/PGM) + DO/RDY/TPOD 输出映射 + TPOA0/1=1'b0.
4. run_approved_command cp EFUSE_TOP.v → DK/release/verilog/.

## produce-task 化 (本 case)
交付 `gen_verilog_shell.py <pin_table.tsv> <inner_module.v> <wrapper_name>`:
通用解析任意管脚表 (TSV: name<width>direction) + 任意内部模块 (regex 解析 module 端口列表) → 结构化 wrapper:
- module 名 = wrapper_name; 顶层端口 = 管脚表 (方向/宽度); 内部例化 u_<inner>; 同名按名连接; 异名内部端口留空 .port(); 管脚表独有端口顶层悬挂.

## A/B 设计
- **A (visible, trace-faithful)**: pin_table_A.tsv (18 真实端口) + inner_A.v (真实 Efuse 15 端口) + example_output_A.v (trace 真实 EFUSE_TOP.v) + prompt.txt (用户原话) + task_brief.md.
- **B (hidden, PLL macro, 完全不同)**: pin_table_B.tsv (10 端口: VDD/GND/CLK_REF/RST_N/BYPASS/TRIM<7:0>(8)/CLK_OUT/LOCK/CLK_MON/SPI_EN) + inner_B.v (PLL_CORE 7 端口, TEST_DIV 内部独有) + wrapper_name=PLL_TOP. 同名 6 (CLK_REF/RST_N/BYPASS/TRIM/CLK_OUT/LOCK), 内部独有 1 (TEST_DIV), 管脚表独有 4 (VDD/GND/CLK_MON/SPI_EN). B 永不进 SUT 沙箱, check.py 内联.

## check.py (12 断言 a-l, self-contained)
a 非空脚本 / b B exit0+module+endmodule / c module==PLL_TOP / d 10 端口名齐 / e 方向正确 / f TRIM[7:0]+标量无总线 / g PLL_CORE 例化 / h 6 同名按名连接 / i TEST_DIV() 留空 / j 管脚表独有不连内部 / k 反硬编码A(无VMEAS/CONV_EN/TPOD/TPID/Efuse/EFUSE_TOP/TPIO/PGM_EN/RDY) / l 空输入探针(反print-expected).

## 自验
- reference_submit.zip (gen_verilog_shell.py) → check.py PASS (12/12).
- 4 negatives 全 FAIL @ 各自首失败断言: neg_empty→a, neg_print_expected→l, neg_core_deleted→g, neg_hardcode_a→c.
- negative_selftest.py OK.
- §4.9 三假提交: fake_empty(neg_empty)→a, fake_print_only(neg_print_expected)→l, fake_core_deleted(neg_core_deleted)→g — 全 FAIL.
- k_check == k_rationale == 12 (①-⑫ 完整).

## 台账
- B shard 于 2026-11-09 误 park 本 session 为 "trivial 5KB spice_sim" (mc=0 旧扫描口径), 实为 305KB/83msg verilog wrapper (A-domain digital). 按 r708 跨 shard 互斥 --force hatch, A mark --force 覆盖, note 记原因.
