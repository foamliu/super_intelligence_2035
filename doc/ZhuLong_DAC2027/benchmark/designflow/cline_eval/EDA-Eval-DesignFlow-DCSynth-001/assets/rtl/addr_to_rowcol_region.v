//////////////////////////////////////////////////////////////////////////////
// Modular implementation.
// The public top-level interface is unchanged from the original design.
//////////////////////////////////////////////////////////////////////////////

`timescale 1ns/1ps

module addr_region_decode (
    input      [8:0] N,
    output     [1:0] region,
    output           valid
);
    assign region =
        (N <= 9'd79)  ? 2'd0 :
        (N <= 9'd155) ? 2'd1 :
        (N <= 9'd215) ? 2'd2 : 2'd3;

    assign valid = (N <= 9'd295);
endmodule


module addr_region0_calc (
    input      [8:0] N,
    output     [3:0] row,
    output     [4:0] col
);
    wire [7:0] col_full;

    assign row      = N[1:0];
    assign col_full =
        (8'd76 + {8'd0,N[1:0]} - {8'd0,N[7:0]}) >> 2;
    assign col      = col_full[4:0];
endmodule


module addr_region1_calc (
    input      [8:0] N,
    output     [3:0] row,
    output     [4:0] col
);
    wire [8:0] col_full;

    assign row      = 4'd4 + N[1:0];
    assign col_full =
        (9'd152 + {5'd0,N[1:0]} - {9'd0,N[7:0]}) >> 2;
    assign col      = col_full[4:0];
endmodule


module addr_region2_calc (
    input      [8:0] N,
    output     [3:0] row,
    output     [4:0] col
);
    wire [8:0]  M;
    wire [13:0] Pq;
    wire [6:0]  q2;
    wire [2:0]  r2;
    wire [3:0]  row2;
    wire [6:0]  V2;
    wire [13:0] pc;

    assign M  = N - 9'd148;
    assign Pq = {5'd0,M} * 9'd171;
    assign q2 = Pq >> 9;
    assign r2 = M - {5'd0,q2} * 3'd3;

    assign row2 = (r2 == 3'd0) ? 4'd9 :
                  (r2 == 3'd1) ? 4'd10 : 4'd8;

    assign V2  = M - {2'b0,row2};
    assign pc  = {5'd0,V2} * 9'd171;
    assign row = row2;
    assign col = pc[13:9];
endmodule


module addr_region3_calc (
    input      [8:0] N,
    output     [3:0] row,
    output     [4:0] col
);
    wire [8:0] D;
    wire [1:0] m4;
    wire [3:0] row3;

    assign D  = N - 9'd205;
    assign m4 = D[1:0];

    assign row3 = (m4 == 2'd0) ? 4'd12 :
                  (m4 == 2'd1) ? 4'd13 :
                  (m4 == 2'd2) ? 4'd14 : 4'd11;

    assign row = row3;
    assign col = (D - {2'b0,row3}) >> 2;
endmodule


module addr_rowcol_mux (
    input      [1:0] region,
    input      [3:0] row0,
    input      [4:0] col0,
    input      [3:0] row1,
    input      [4:0] col1,
    input      [3:0] row2,
    input      [4:0] col2,
    input      [3:0] row3,
    input      [4:0] col3,
    output reg [3:0] row,
    output reg [4:0] col
);
    always @(*) begin
        case (region)
            2'd0: begin row = row0; col = col0; end
            2'd1: begin row = row1; col = col1; end
            2'd2: begin row = row2; col = col2; end
            default: begin row = row3; col = col3; end
        endcase
    end
endmodule


module addr_to_rowcol_region (
    input  [8:0] RA,
    output [3:0] row,
    output [4:0] col,
    output [1:0] region,
    output       valid
);
    wire [3:0] row0;
    wire [4:0] col0;
    wire [3:0] row1;
    wire [4:0] col1;
    wire [3:0] row2;
    wire [4:0] col2;
    wire [3:0] row3;
    wire [4:0] col3;

    addr_region_decode u_region_decode (
        .N(RA), .region(region), .valid(valid)
    );

    addr_region0_calc u_region0_calc (
        .N(RA), .row(row0), .col(col0)
    );

    addr_region1_calc u_region1_calc (
        .N(RA), .row(row1), .col(col1)
    );

    addr_region2_calc u_region2_calc (
        .N(RA), .row(row2), .col(col2)
    );

    addr_region3_calc u_region3_calc (
        .N(RA), .row(row3), .col(col3)
    );

    addr_rowcol_mux u_rowcol_mux (
        .region(region),
        .row0(row0), .col0(col0),
        .row1(row1), .col1(col1),
        .row2(row2), .col2(col2),
        .row3(row3), .col3(col3),
        .row(row), .col(col)
    );
endmodule
