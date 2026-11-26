//==============================================================================
// Recursive CLA - parameterized by adder width (must be power of two)
//==============================================================================
module cla_recursive #(parameter WIDTH = 16) (
    input  [WIDTH-1:0] a, b,
    input              cin,
    output [WIDTH-1:0] sum,
    output             cout,
    output             G, P
);

    generate
        if (WIDTH == 1) begin : base1
            full_adder u (.a(a[0]), .b(b[0]), .cin(cin), .sum(sum[0]), .cout(cout));
            assign G = a[0] & b[0];
            assign P = a[0] ^ b[0];
        end else if (WIDTH == 2) begin : base2
            cla2 u (.*, .sum(sum), .cout(cout), .G(G), .P(P));
        end else if (WIDTH == 4) begin : base4
            cla4 u (.*, .sum(sum), .cout(cout), .G(G), .P(P));
        end else begin : recurse
            localparam BLOCK = WIDTH / 4;   // each sub-block width
            wire [3:0] g, p;
            wire [4:0] c;                  // c[0]=cin, c[4]=cout
            assign c[0] = cin;

            genvar j;
            for (j = 0; j < 4; j = j + 1) begin : blocks
                cla_recursive #(BLOCK) u_block (
                    .a   (a[j*BLOCK +: BLOCK]),
                    .b   (b[j*BLOCK +: BLOCK]),
                    .cin (c[j]),
                    .sum (sum[j*BLOCK +: BLOCK]),
                    .cout(c[j+1]),
                    .G   (g[j]),
                    .P   (p[j])
                );
            end

            assign cout = c[4];
            assign G    = g[3] | (p[3] & g[2]) | (p[3] & p[2] & g[1])
                              | (p[3] & p[2] & p[1] & g[0]);
            assign P    = p[3] & p[2] & p[1] & p[0];
        end
    endgenerate

endmodule
