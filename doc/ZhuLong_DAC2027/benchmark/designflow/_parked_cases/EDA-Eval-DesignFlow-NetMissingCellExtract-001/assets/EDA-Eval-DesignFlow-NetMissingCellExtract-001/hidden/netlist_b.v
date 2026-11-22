// netlist_b.v -- hidden B netlist (NOT visible to SUT; used for actual grading).
// 6 modules with mixed available/missing cells; cell names disjoint from sample A.
`timescale 1ps/1ps
`celldefine
module top_clkgen (clk_out, clk_in, vcc, vss);
    output clk_out; input clk_in;
    inout vcc, vss;
    wire net1, net2, net3;

    clkbufLV I0 (.Y(clk_out), .A(clk_in), .vcc(vcc), .vss(vss));
    bufLV_drv I1 (.Y(net1), .A(clk_in), .vcc(vcc), .vss(vss));
    invLVSx2 I2 (.Y(net2), .A(clk_in), .vcc(vcc), .vss(vss));
    andbase_clk I3 (.Y(net3), .A(clk_in), .B(net2), .vcc(vcc), .vss(vss));
endmodule
`endcelldefine

`celldefine
module io_nor_chain (Y, A, B, vcc, vss);
    output Y; input A, B;
    inout vcc, vss;
    wire net10, net11;

    nor2LVx2 I0 (.Y(Y), .A(A), .B(B), .vcc(vcc), .vss(vss));
    nor2LVx2 I1 (.Y(net10), .A(Y), .B(B), .vcc(vcc), .vss(vss));
    ntn_io MN0 (.D(net10), .G(A), .S(vss), .B(vss));
    ptn_io MP0 (.D(net10), .G(A), .S(vcc), .B(vcc));
    invLV I4 (.Y(net11), .A(net10), .vcc(vcc), .vss(vss));
endmodule
`endcelldefine

`celldefine
module latch_keep (Q, D, en, enN, vcc, vss);
    output Q; input D, en, enN;
    inout vcc, vss;
    wire Qn;

    invenIOLV I0 (.Y(Q), .A(D), .En(en), .EnN(enN), .vcc(vcc), .vss(vss));
    keeperRC I1 (.Q(Q), .vcc(vcc), .vss(vss));
    keeper_base I2 (.Q(Q), .vcc(vcc), .vss(vss));
    tg_lv I3 (.P0(D), .P1(Q), .S(en), .SN(enN));
    dff_base I4 (.Q(Qn), .QN(Q), .D(D), .clk(en), .vcc(vcc), .vss(vss));
endmodule
`endcelldefine

`celldefine
module mux4_build (Y, A, B, C, D, S0, S1, vcc, vss);
    output Y; input A, B, C, D, S0, S1;
    inout vcc, vss;
    wire net20, net21, net22;

    mux4IOLV I0 (.Y(Y), .A(A), .B(B), .C(C), .D(D), .S0(S0), .S1(S1), .vcc(vcc), .vss(vss));
    mux2LV I1 (.Y(net20), .A(A), .B(B), .Sel(S0), .vcc(vcc), .vss(vss));
    mux2LV I2 (.Y(net21), .A(C), .B(D), .Sel(S0), .vcc(vcc), .vss(vss));
    mux2LV I3 (.Y(Y), .A(net20), .B(net21), .Sel(S1), .vcc(vcc), .vss(vss));
    invLV I5 (.Y(net22), .A(S0), .vcc(vcc), .vss(vss));
endmodule
`endcelldefine

`celldefine
module delay_line (out, in, vcc, vss);
    output out; input in;
    inout vcc, vss;
    wire net30, net31, net32;

    delayRC3 I0 (.OUT(out), .IN(in), .vcc(vcc), .vss(vss));
    bufLV I1 (.Y(net30), .A(in), .vcc(vcc), .vss(vss));
    bufLV I2 (.Y(net31), .A(net30), .vcc(vcc), .vss(vss));
    bufLV I3 (.Y(out), .A(net31), .vcc(vcc), .vss(vss));
    tie_base I4 (.Y(net32), .vcc(vcc), .vss(vss));
endmodule
`endcelldefine

`celldefine
module pg_monitor_wrap (sout, sin, celltype, vpwr, vgnd);
    input [255:0] celltype; input sin; output sout;
    inout vpwr, vgnd;
    wire net40;

    pgmon_b I0 (.celltype("mux4"), .sin(sin), .sout(sout), .vpwr(vpwr), .vgnd(vgnd));
    nmos_b MN1 (.D(sout), .G(sin), .S(vpwr), .B(vpwr));
    pmos_b MP1 (.D(sout), .G(sin), .S(vpwr), .B(vpwr));
    invLVSx2 I5 (.Y(net40), .A(sin), .vcc(vpwr), .vss(vgnd));
endmodule
`endcelldefine
