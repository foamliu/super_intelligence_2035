//====================================================================
// cfreq_ctrl.mapped.v —— 综合网表占位文件 (PLACEHOLDER)
//
// 说明:
//   本文件仅供 fm/ 流程独立 dry-run / make -n / 结构断言使用,
//   并非真实门级网表。真正运行 rtl2gate 等价性验证前, 请用 syn/
//   流程产出的综合网表覆盖本文件:
//       cp ../syn/flow_cfreq_ctrl/results/cfreq_ctrl.mapped.v data/netlist/
//   或将 Makefile 中 FM_IMPL_NETLIST 指向该 netlist 的绝对路径。
//====================================================================
`timescale 1ns/1ps
module cfreq_ctrl (
    input  wire        REFCLK,
    input  wire        FBCLK,
    input  wire        LOOP_BREAK,
    input  wire        RST_N,
    input  wire [9:0]  WINDOW_LEN,
    input  wire [9:0]  THRESHOLD,
    output wire        RDY,
    output wire [4:0]  CAP_CTRL_OUT
);
    // 占位实现: 仅用于保证 read_verilog 可解析; 与 RTL 不等价, 仅供 dry-run。
    assign RDY          = 1'b0;
    assign CAP_CTRL_OUT = 5'b0;
endmodule