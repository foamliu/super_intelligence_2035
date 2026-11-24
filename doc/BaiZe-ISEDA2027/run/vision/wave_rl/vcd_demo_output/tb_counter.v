`timescale 1ns/1ps
module tb_counter;
    reg        clk;  reg        rst_n;
    wire [3:0] count; wire       clk_div2;
    counter dut(.clk(clk),.rst_n(rst_n),.count(count),.clk_div2(clk_div2));
    initial begin
        $dumpfile("counter.vcd"); $dumpvars(0, tb_counter);
        clk=0; rst_n=0; #20 rst_n=1; #500 $finish;
    end
    always #10 clk = ~clk;  // 100MHz, period=20ns
endmodule
