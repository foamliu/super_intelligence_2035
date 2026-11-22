// netlist_a.v -- sample A netlist (visible to SUT)
// Contains 4 modules with cell instantiations.
// Some cells are defined in simlib_a.sv (available), some are NOT (missing).
`timescale 1ps/1ps
`celldefine
module IO_rsnand21nand31_DL_ACT_MERGE_READ (Y, inh_vbn, inh_vbp, inh_vcc, inh_vss, R0, R1, S);
    output Y;
    input R0, R1, S;
    inout inh_vbn, inh_vcc, inh_vss, inh_vbp;
    wire net16;
    parameter string strength1 = "strong1";
    parameter string strength0 = "strong0";

    nand2IOLVx2 I6 (.Y(Y), .vbn(inh_vbn), .vbp(inh_vbp), .vcc(inh_vcc), .vssz(inh_vss), .A(S), .B(net16));
    nand3IOLVx2 I0 (.Y(net16), .vbn(inh_vbn), .vbp(inh_vbp), .vcc(inh_vcc), .vssz(inh_vss), .A(R1), .B(R0), .C(Y));
    fgc_pwrstate_monitor ISPMON (.celltype("nandIOLV"), .sin(S), .sout(Y), .vpwr(inh_vcc), .vgnd(inh_vss), .vblkn(inh_vbn), .vblkp(inh_vbp));
    inv_base Iavail1 #(strength1, strength0) (.Y(R0), .A(R1), .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
endmodule
`endcelldefine

`celldefine
module inv_chain_dl (out, in, inh_vbn, inh_vbp, inh_vcc, inh_vss);
    output out; input in;
    inout inh_vbn, inh_vbp, inh_vcc, inh_vss;
    wire net6, net7;

    ntn_lv MN0 (.B(inh_vss), .D(out), .G(in), .S(inh_vss));
    ptn_lv MP0 (.B(inh_vcc), .D(out), .G(in), .S(inh_vcc));
    invDSx1 I2 (.Y(net6), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(in));
    invDSx1 I1 (.Y(out), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(in));
    invDSx1 I0 (.Y(net7), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(in));
    inven_base Iavail2 (.Y(net6), .A(in), .En(inh_vcc), .EnN(inh_vss), .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
endmodule
`endcelldefine

`celldefine
module D_latqn_ffRdBlk1 (QN, D, Lat, LatF, net9, inh_vbn, inh_vbp, inh_vcc, inh_vss);
    output QN; input D, Lat, LatF, net9;
    inout inh_vbn, inh_vbp, inh_vcc, inh_vss;

    invCS I6 (.Y(net9), .vbulkn(inh_vbn), .vbulkp(inh_vbp), .vcc(inh_vcc), .vss(inh_vss), .A(QN));
    invCS I4 (.Y(LatF), .vbulkn(inh_vbn), .vbulkp(inh_vbp), .vcc(inh_vcc), .vss(inh_vss), .A(Lat));
    invhizCS #(.strength0("pull0"), .strength1("pull1")) I1 (.Y(QN), .vbulkn(inh_vbn), .vbulkp(inh_vbp), .vcc(inh_vcc), .vss(inh_vss), .A(net9), .En(Lat), .EnN(LatF));
    invenCS I7 (.Y(QN), .vbulkn(inh_vbn), .vbulkp(inh_vbp), .vcc(inh_vcc), .vss(inh_vss), .A(D), .En(LatF), .EnN(Lat));
    parasiticRC2 I3 (.MINUS(QN), .inh_vss(inh_vss));
    fbs_base Iavail3 (.Y(QN), .A(D), .EnN(LatF), .En(Lat), .SN(net9), .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
endmodule
`endcelldefine

`celldefine
module mux2_sel_dl (Y, A, B, SelN, Sel, inh_vbn, inh_vbp, inh_vcc, inh_vss);
    output Y; input A, B, SelN, Sel;
    inout inh_vbn, inh_vbp, inh_vcc, inh_vss;
    wire out_int;

    invenLVSx1 I30 (.Y(out_int), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(A), .En(SelN), .EnN(Sel));
    invenLVSx1 I0 (.Y(Y), .vbn(inh_vbn), .vbp(inh_vcc), .vcc(inh_vcc), .vss(inh_vss), .A(B), .En(Sel), .EnN(SelN));
    invhiz_base Iavail4 (.Y(Y), .A(out_int), .En(Sel), .EnN(SelN), .vcc_(inh_vcc), .vss_(inh_vss), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
    passg_base Iavail5 (.Y(out_int), .A(A), .En(Sel), .EnN(SelN), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp));
endmodule
`endcelldefine
