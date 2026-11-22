`timescale 1ps/1ps
// simlib_b.sv -- hidden B reference library (cell names disjoint from sample A).
`celldefine
module invLV (Y, A, vcc, vss);
    output Y; input A; inout vcc, vss;
    not (Y, A);
endmodule
`endcelldefine

`celldefine
module bufLV (Y, A, vcc, vss);
    output Y; input A; inout vcc, vss;
    buf (Y, A);
endmodule
`endcelldefine

`celldefine
module mux2LV (Y, A, B, Sel, vcc, vss);
    output Y; input A, B, Sel; inout vcc, vss;
    assign Y = Sel ? B : A;
endmodule
`endcelldefine

`celldefine
module dff_base (Q, QN, D, clk, vcc, vss);
    output Q, QN; input D, clk; inout vcc, vss;
    reg Q; assign QN = ~Q;
    always @(posedge clk) Q <= D;
endmodule
`endcelldefine

`celldefine
module andbase_clk (Y, A, B, vcc, vss);
    output Y; input A, B; inout vcc, vss;
    and (Y, A, B);
endmodule
`endcelldefine

`celldefine
module keeper_base (Q, vcc, vss);
    inout Q, vcc, vss;
endmodule
`endcelldefine

`celldefine
module tie_base (Y, vcc, vss);
    output Y; inout vcc, vss;
    assign Y = 1'b0;
endmodule
`endcelldefine

`celldefine
module clkbufLV (Y, A, vcc, vss);
    output Y; input A; inout vcc, vss;
    buf (Y, A);
endmodule
`endcelldefine

`celldefine
module pgmon_b (celltype, sin, sout, vpwr, vgnd);
    input [255:0] celltype; input sin; output sout; inout vpwr, vgnd;
    assign sout = sin;
endmodule
`endcelldefine

`celldefine
module nmos_b (D, G, S, B);
    inout D, G, S, B;
endmodule
`endcelldefine

`celldefine
module pmos_b (D, G, S, B);
    inout D, G, S, B;
endmodule
`endcelldefine
