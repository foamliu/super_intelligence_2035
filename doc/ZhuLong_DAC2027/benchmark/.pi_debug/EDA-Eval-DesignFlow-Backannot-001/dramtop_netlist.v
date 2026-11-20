// =========================================================================
// DRAMTOP gate-level netlist fragment  (脱敏合成, Cadence Virtuoso ADE SI
// Verilog Netlister output, full hierarchy kept)
// Source: si.log -> ihnl/ incremental chunks -> DRAMTOP.vp (690934 lines)
// =========================================================================
`timescale 1ns/1ps

module DRAMTOP (
    // ... ports omitted for brevity ...
);

wire [3:0] cm1_ro_ACThLevelA;
wire [3:0] cm1_ro_ACThDefN;
wire [3:0] net0296;        // internal trivial node, kept by Cadence SI
wire [3:0] ACLevelA;
wire [3:0] ACDef;
wire       net023;         // internal trivial node, kept by Cadence SI

    I_Array16GTop I_Array16GTop (
        // ...
    );

endmodule


module I_Array16GTop (
    // ...
);
    I_Array8G_SC1 I_Array8G_SC1 (
        // ...
    );
endmodule


module I_Array8G_SC1 (
    // ...
);
    I_CMAryB_222 I_CMAryB_222 (
        // ...
    );
endmodule


module I_CMAryB_222 (
    input  [3:0] ACLevelA,
    output [3:0] ACDef,
    output [3:0] ACThLevelA,
    output [3:0] ACThDefN
);
    wire [3:0] net0296;     // internal trivial node (Cadence SI keeps full)

    // instance I34_3_ : mx4Lx2 (full hierarchical instance name kept)
    mx4Lx2 I34_3_ (
        .vbp (inh_vbp),
        .vbn (inh_vbn),
        .vcc (inh_vcc),
        .S3  (SetABODefault),
        .A2  (cm1_ro_ACThLevelA[3]),
        .A3  (cm1_ro_ACThDefN[3]),
        .Y   (net0296[3])
    );

    invLx1 I34_1_ (
        .A (net0296[3]),
        .Y (ACLevelA[1])
    );

    // instance I35_2_ : another mx4Lx2 driving ACDef via merged internal node
    mx4Lx2 I35_2_ (
        .vbp (inh_vbp),
        .vbn (inh_vbn),
        .vcc (inh_vcc),
        .S3  (SetABODefault),
        .A2  (cm1_ro_ACThLevelA[2]),
        .A3  (cm1_ro_ACThDefN[2]),
        .Y   (net0296[2])
    );

    invLx1 I35_1_ (
        .A (net0296[2]),
        .Y (ACDef[3])
    );

    // instance I36_4_ : critical (real cross-module driver, NOT a merge node)
    mx4Lx2 I36_4_ (
        .vbp (inh_vbp),
        .vbn (inh_vbn),
        .vcc (inh_vcc),
        .S3  (SetABODefault),
        .A2  (cm1_ro_ACThLevelA[1]),
        .A3  (cm1_ro_ACThDefN[1]),
        .Y   (net023)          // drives an output port directly -> critical
    );

    // ACThLevelA[3] / ACThDefN[3] are outputs consumed by a top-level
    // timing-critical path -> if not annotated, STA signoff cannot close.

endmodule
