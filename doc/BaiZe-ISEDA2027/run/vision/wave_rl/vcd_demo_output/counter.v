// synth_vcd_demo: clock divider + counter
// Compile: iverilog -o sim.vvp tb_counter.v counter.v && vvp sim.vvp
module counter(
    input  wire       clk,
    input  wire       rst_n,
    output reg [3:0]  count,
    output wire       clk_div2
);
    assign clk_div2 = count[0];
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) count <= 4'b0000;
        else        count <= count + 1'b1;
    end
endmodule
