//==============================================================================
// Top-Level 2^N-bit CLA - parameterized by WIDTH (default 16, must be power of 2)
//==============================================================================
module cla_top #(parameter WIDTH = 16) (
    input  [WIDTH-1:0] a, b,
    input              cin,
    output [WIDTH-1:0] sum,
    output             cout
);

    wire unused_G, unused_P;
    cla_recursive #(.WIDTH(WIDTH)) u (
        .a   (a),
        .b   (b),
        .cin (cin),
        .sum (sum),
        .cout(cout),
        .G   (unused_G),
        .P   (unused_P)
    );

endmodule
