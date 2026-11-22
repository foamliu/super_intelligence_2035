`timescale 1ps/1ps
// simlib_a.sv -- reference library of available physical cells
// (reconstructed from a real DR-VQA netlist-conversion trace, user e0039602)

`celldefine
module inv_base (Y, A, vbulkn_, vbulkp_, vcc_, vss_);
    output Y; input A; inout vbulkn_, vbulkp_, vcc_, vss_;
    parameter string strength1 = "strong1";
    parameter string strength0 = "strong0";
    not (Y, A);
endmodule
`endcelldefine

`celldefine
module invYx_base (Y, A, vbulkn_, vbulkp_, vcc_, vss_);
    output Y; input A; inout vbulkn_, vbulkp_, vcc_, vss_;
    not (Y, A);
endmodule
`endcelldefine

`celldefine
module inven_base (Y, A, EnN, En, vbulkn_, vbulkp_, vcc_, vss_);
    output Y; input A, EnN, En; inout vbulkn_, vbulkp_, vcc_, vss_;
    parameter string strength1 = "strong1";
    parameter string strength0 = "strong0";
    bufif0 (Y, A, EnN);
    notif1 (Y, A, En);
endmodule
`endcelldefine

`celldefine
module invhiz_base (Y, A, EnN, En, vbulkn_, vbulkp_, vcc_, vss_);
    output Y; input A, EnN, En; inout vbulkn_, vbulkp_, vcc_, vss_;
    parameter string strength1 = "strong1";
    parameter string strength0 = "strong0";
    notif0 (Y, A, EnN);
    notif1 (Y, A, En);
endmodule
`endcelldefine

`celldefine
module fbs_base (Y, A, EnN, En, SN, vbulkn_, vbulkp_, vcc_, vss_);
    output Y; input A, EnN, En, SN; inout vbulkn_, vbulkp_, vcc_, vss_;
    parameter string strength1 = "strong1";
    parameter string strength0 = "strong0";
    reg Y; // simplified
endmodule
`endcelldefine

`celldefine
module passg_base (Y, vbulkn_, vbulkp_, A, En, EnN);
    output Y; input A, En, EnN; inout vbulkn_, vbulkp_;
    tranif1 (Y, A, En);
    tranif0 (Y, A, EnN);
endmodule
`endcelldefine

`celldefine
module dlyrc_base (Out, In, vcc_, vss_);
    output Out; input In; inout vcc_, vss_;
    assign Out = In;
endmodule
`endcelldefine

`celldefine
module fgc_pwrstate_monitor (celltype, sin, sout, vpwr, vgnd, vblkn, vblkp);
    input [255:0] celltype; input sin; output sout; inout vpwr, vgnd, vblkn, vblkp;
    assign sout = sin;
endmodule
`endcelldefine

`celldefine
module nn (D, G, S, B);
    inout D, G, S, B;
endmodule
`endcelldefine

`celldefine
module pp (D, G, S, B);
    inout D, G, S, B;
endmodule
`endcelldefine

`celldefine
module alias_short (A, A);
    inout A;
endmodule
`endcelldefine

`celldefine
module switch (in, out);
    parameter position = 1;
    parameter size = 4;
    inout [size-1:0] in; inout out;
endmodule
`endcelldefine
