//==============================================================================
// 2-bit Carry Lookahead Adder
//==============================================================================
module cla2 (
    input  [1:0] a, b,
    input        cin,
    output [1:0] sum,
    output       cout,
    output       G, P
);
    wire [1:0] g, p;
    wire [2:0] c;

    assign g    = a & b;
    assign p    = a ^ b;
    assign c[0] = cin;
    assign c[1] = g[0] | (p[0] & c[0]);
    assign c[2] = g[1] | (p[1] & c[1]);
    assign sum  = p ^ c[1:0];
    assign cout = c[2];
    assign G    = g[1] | (p[1] & g[0]);
    assign P    = p[1] & p[0];
endmodule
