//==============================================================================
// 4-bit Carry Lookahead Adder
//==============================================================================
module cla4 (
    input  [3:0] a, b,
    input        cin,
    output [3:0] sum,
    output       cout,
    output       G, P
);
    wire [3:0] g, p;
    wire [4:0] c;

    assign g    = a & b;
    assign p    = a ^ b;
    assign c[0] = cin;
    assign c[1] = g[0] | (p[0] & c[0]);
    assign c[2] = g[1] | (p[1] & c[1]);
    assign c[3] = g[2] | (p[2] & c[2]);
    assign c[4] = g[3] | (p[3] & c[3]);
    assign sum  = p ^ c[3:0];
    assign cout = c[4];
    assign G    = g[3] | (p[3] & g[2]) | (p[3] & p[2] & g[1])
                       | (p[3] & p[2] & p[1] & g[0]);
    assign P    = p[3] & p[2] & p[1] & p[0];
endmodule
