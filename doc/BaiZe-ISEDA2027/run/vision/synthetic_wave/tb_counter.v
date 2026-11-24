`timescale 1ns/1ps

module tb_counter;

reg clk;
reg rst_n;
wire [3:0] count;

counter u_counter (
    .clk(clk),
    .rst_n(rst_n),
    .count(count)
);

// Generate 100MHz clock (10ns period)
initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
end

// Reset sequence
initial begin
    rst_n = 1'b0;
    #20 rst_n = 1'b1;
    #200 $finish;
end

// Dump VCD waveform
initial begin
    $dumpfile("counter_wave.vcd");
    $dumpvars(0, tb_counter);
end

endmodule
