//==============================================================
// tb_cfreq_ctrl.sv - CFREQ_CTRL 定向测试台 (代码覆盖率用)
//
// 策略: 固定 REFCLK=25MHz, 通过不同 FBCLK 频率分别覆盖
//   - FBCLK 偏低(计数<=阈值): 首窗达标 -> ST_IDLE..ST_DONE
//   - FBCLK 偏高(计数>阈值):   逐级 VCODE+1 -> ST_CAP_SETTLE 循环
//   - 中途 LOOP_BREAK 拉低:    触发 abort 回 IDLE
// 导出 VCD 供波形/覆盖率查看。
//==============================================================
`timescale 1ns/1ps

module tb_cfreq_ctrl;

    reg         REFCLK, FBCLK, LOOP_BREAK, RST_N;
    reg  [9:0]  WINDOW_LEN, THRESHOLD;
    wire        RDY;
    wire [4:0]  CAP_CTRL_OUT;

    localparam CLK_HALF = 20;  // 25MHz

    cfreq_ctrl dut (
        .REFCLK      (REFCLK),
        .FBCLK       (FBCLK),
        .LOOP_BREAK  (LOOP_BREAK),
        .RST_N       (RST_N),
        .WINDOW_LEN  (WINDOW_LEN),
        .THRESHOLD   (THRESHOLD),
        .RDY         (RDY),
        .CAP_CTRL_OUT(CAP_CTRL_OUT)
    );

    // REFCLK 25MHz
    initial begin
        REFCLK = 1'b0;
        forever #CLK_HALF REFCLK = ~REFCLK;
    end

    // FBCLK 可调: 用整数分频系数逼近不同频率 (fb_div <1 => 更快)
    real fb_div = 1.0;
    initial begin
        FBCLK = 1'b0;
        forever begin
            #(CLK_HALF * fb_div) FBCLK = ~FBCLK;
        end
    end

    // 简单 VCD 导出
    initial begin
        $dumpfile("tb_cfreq_ctrl.vcd");
        $dumpvars(0, tb_cfreq_ctrl);
    end

    initial begin
        RST_N      = 1'b0;
        LOOP_BREAK = 1'b0;
        WINDOW_LEN = 10'd16;
        THRESHOLD  = 10'd16;
        fb_div     = 1.0;

        // 复位释放
        repeat (10) @(posedge REFCLK);
        RST_N = 1'b1;
        repeat (10) @(posedge REFCLK);

        // 场景1: FBCLK == REFCLK => 首窗达标, 较快 DONE
        fb_div = 1.0;
        @(posedge REFCLK);
        LOOP_BREAK = 1'b1;
        wait (RDY === 1'b1);
        $display("[TB] scenario1 done: CAP_CTRL_OUT=%0d", CAP_CTRL_OUT);
        LOOP_BREAK = 1'b0;
        repeat (20) @(posedge REFCLK);

        // 场景2: FBCLK 更快(计数偏高) => 触发 VCODE 递增
        fb_div = 0.25;   // FBCLK = 100MHz
        @(posedge REFCLK);
        LOOP_BREAK = 1'b1;
        repeat (4000) @(posedge REFCLK);
        LOOP_BREAK = 1'b0;
        repeat (10) @(posedge REFCLK);

        // 场景3: 中途退出 (校准未完成即拉低 LB)
        fb_div = 0.25;
        @(posedge REFCLK);
        LOOP_BREAK = 1'b1;
        repeat (50) @(posedge REFCLK);
        LOOP_BREAK = 1'b0;   // abort
        repeat (20) @(posedge REFCLK);

        $display("[TB] simulation finished, RDY=%b CAP=%0d", RDY, CAP_CTRL_OUT);
        $finish;
    end

    // 看门狗: 防止死循环
    initial begin
        #1000000;  // 1ms
        $display("[TB] timeout watchdog triggered");
        $finish;
    end

endmodule