// hl22_porting_test_chip.v -- RTL top (rtl_power/, head excerpt, 96 lines)
module hl22_porting_test_chip_v1 (
    TMOut, TMReady, GroupSelect0, GroupSelect1, GroupSelect2, GroupSelect3,
    ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1, CtrlEn, clk, rst_n
);
    output TMOut, TMReady;
    output GroupSelect0, GroupSelect1, GroupSelect2, GroupSelect3;
    output ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1, CtrlEn;
    input  clk, rst_n;

    wire [7:0] data_bus;
    wire [3:0] sel;
    reg  [15:0] cnt;
    reg  [7:0]  acc;

    // frequency divider
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) cnt <= 16'h0;
        else cnt <= cnt + 1'b1;
    end
    assign ClearFreqDiv = (cnt == 16'hffff);
    assign SelByFreq0   = cnt[0];
    assign ModeSel0     = cnt[1];
    assign ModeSel1     = cnt[2];
    assign CtrlEn       = cnt[3];
    assign GroupSelect0 = cnt[4];
    assign GroupSelect1 = cnt[5];
    assign GroupSelect2 = cnt[6];
    assign GroupSelect3 = cnt[7];

    // accumulator
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) acc <= 8'h0;
        else acc <= acc + data_bus[7:0];
    end
    assign TMOut    = acc[7];
    assign TMReady  = (acc == 8'hff);
endmodule
