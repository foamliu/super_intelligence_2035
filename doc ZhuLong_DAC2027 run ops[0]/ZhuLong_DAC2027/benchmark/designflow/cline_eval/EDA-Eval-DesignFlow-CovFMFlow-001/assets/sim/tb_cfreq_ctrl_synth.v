//####################################################
// Description
//####################################################
// Revision History
//  -v1.0  Lorik Xiao  2026-10-19
//      Initial version
//  -v1.1  Lorik Xiao  2026-10-23
//      DUT WINDOW_LEN/THRESHOLD 改为 10bit 输入端口, TB 用 win_len/thresh 驱动
//####################################################

// ============================================================================
// tb_cfreq_ctrl_synth.v
// CFREQ_CTRL 可综合版 Testbench (Verilog-2001)
//
// 与 model TB (tb_cfreq_ctrl.v) 对照验证:
//   - 相同 5 个 TC: 正常校准 / code=0达标 / code=15锁定 / 中途退出 / 重新触发
//   - 期望终值与 model TB 一致
//     (synth v1.1 达标即 DONE, 比 model 少一个稳定复验窗, 完成时间更短)
//   - DUT 新增 RST_N 端口, TB 在 TC1 开头执行 do_reset
//   - DUT 的 WINDOW_LEN/THRESHOLD 已改为 10bit 输入端口, 由 TB 寄存器
//     win_len/thresh 驱动 (默认 64/64; FAST_SIM 下 256/256)
//
// VCO 反馈模型 vco_fb_model 由 filelist_synth.f 共用引入 (sim/vco_fb_model.v)
//
// Usage:
//   VCS:      make synth   (默认参数)
//
// ============================================================================

`timescale 1ns/1ps

module tb_cfreq_ctrl_synth;

    // ------------------------------------------------------------------
    // 时钟: REFCLK 25MHz -> 周期 40ns
    // (DUT 的 WINDOW_LEN/THRESHOLD 已改为端口, 由下方 win_len/thresh 驱动)
    // ------------------------------------------------------------------
    localparam real REFCLK_PERIOD = 40.0;   // ns

    // ------------------------------------------------------------------
    // 信号
    // ------------------------------------------------------------------
    reg         REFCLK;
    wire        FBCLK;
    reg         LOOP_BREAK;
    reg         RST_N;
    wire        RDY;
    wire [4:0]  CAP_CTRL_OUT;

    // DUT 窗口/阈值配置 (原 parameter 改为输入端口, 由 TB 驱动)
    reg [9:0]   win_len;    // -> dut.WINDOW_LEN (比对窗宽, REFCLK 周期数)
    reg [9:0]   thresh;     // -> dut.THRESHOLD  (达标门限, 通常 = win_len)

    // VCO 模型控制 (运行时可调, 通过层次引用赋值给 vco_fb_model 内部变量)
    reg         vco_en;

    // 错误计数与用例编号
    integer errors;
    integer tc_id;
    reg [127:0] tc_name;

    // ------------------------------------------------------------------
    // DUT 实例 (可综合版, RST_N + WINDOW_LEN/THRESHOLD 输入端口)
    // ------------------------------------------------------------------
    cfreq_ctrl dut (
        .REFCLK       (REFCLK),
        .FBCLK        (FBCLK),
        .LOOP_BREAK   (LOOP_BREAK),
        .RST_N        (RST_N),
        .WINDOW_LEN   (win_len),
        .THRESHOLD    (thresh),
        .RDY          (RDY),
        .CAP_CTRL_OUT (CAP_CTRL_OUT)
    );

    // WINDOW_LEN/THRESHOLD 端口配置
    // 默认:   64/64   (对方需求: 64 REFCLK 比对窗, 期望 code 与原参数一致)
    // FAST_SIM: 256/256 (量化误差 0.4%, 期望 code 不变)
    initial begin
`ifdef FAST_SIM
        win_len = 10'd256;
        thresh  = 10'd256;
`else
        win_len = 10'd64;
        thresh  = 10'd64;
`endif
        $display("[CFG] DUT WINDOW_LEN=%0d THRESHOLD=%0d (port-driven)", win_len, thresh);
    end

`ifdef FAST_SIM
    // 快速仿真: 缩短 settle 加速
    // (WINDOW_LEN/THRESHOLD 已是端口, 由上方 initial 驱动, 不能再用 defparam)
    defparam dut.START_SETTLE = 50;
    defparam dut.CAP_SETTLE   = 8;
`endif

    // VCO 反馈模型实例 (real 参数通过层次引用赋值: vco.vco_base, vco.vco_step)
    vco_fb_model vco (
        .cap_code   (CAP_CTRL_OUT),
        .vco_enable (vco_en),
        .fbclk      (FBCLK)
    );

    // ------------------------------------------------------------------
    // 时钟生成
    // ------------------------------------------------------------------
    initial REFCLK = 1'b0;
    always #(REFCLK_PERIOD/2.0) REFCLK = ~REFCLK;

    // ------------------------------------------------------------------
    // 波形 dump
    // ------------------------------------------------------------------
    initial begin
`ifdef DUMP_FSDB
        $fsdbDumpfile("waves_synth.fsdb");
        $fsdbDumpvars(0, tb_cfreq_ctrl_synth, "+all");
        $fsdbDumpMDA;
`else
        $dumpfile("waves_synth.vcd");
        $dumpvars(0, tb_cfreq_ctrl_synth);
`endif
    end

    // ==================================================================
    // Tasks
    // ==================================================================

    // 复位: 拉低 RST_N 一段时间, 在 negedge REFCLK 释放
    task do_reset;
        begin
            @(negedge REFCLK);
            RST_N = 1'b0;
            #(REFCLK_PERIOD * 10);
            @(negedge REFCLK);
            RST_N = 1'b1;
            #(REFCLK_PERIOD * 5);
        end
    endtask

    // 设置 VCO 参数 (通过层次引用赋值给 vco_fb_model 内部 real 变量)
    task set_vco;
        input real base;
        input real step;
        begin
            vco.vco_base = base;
            vco.vco_step = step;
        end
    endtask

    // 启动校准: 拉高 LOOP_BREAK (在 negedge 驱动, 确保 posedge 前稳定)
    task start_calib;
        begin
            @(negedge REFCLK);
            LOOP_BREAK = 1'b1;
        end
    endtask

    // 停止校准: 拉低 LOOP_BREAK (在 negedge 驱动)
    task stop_calib;
        begin
            @(negedge REFCLK);
            LOOP_BREAK = 1'b0;
        end
    endtask

    // 等待 RDY 上升沿 (带超时), 返回是否成功
    // 先等 RDY 变低 (确认校准重启/初始态), 再等变高
    reg wait_ok;
    task wait_rdy_rise;
        input integer timeout_us;
        begin : wait_blk
            wait_ok = 1'b0;
            wait (RDY === 1'b0);        // 确认 RDY 已拉低
            fork
                begin
                    wait (RDY === 1'b1);
                    wait_ok = 1'b1;
                    disable wait_timeout;
                end
                begin : wait_timeout
                    #(timeout_us * 1000.0);
                    disable wait_blk;
                end
            join
        end
    endtask

    // 检查 CAP_CTRL_OUT 是否等于期望值
    task check_code;
        input [4:0] exp_code;
        input [127:0] msg;
        begin
            if (CAP_CTRL_OUT === exp_code) begin
                $display("[TC%0d PASS] %s : CAP_CTRL_OUT=%0d (exp %0d)", tc_id, msg, CAP_CTRL_OUT, exp_code);
            end else begin
                errors = errors + 1;
                $display("[TC%0d FAIL] %s : CAP_CTRL_OUT=%0d (exp %0d)", tc_id, msg, CAP_CTRL_OUT, exp_code);
            end
        end
    endtask

    // 检查 RDY 电平
    task check_rdy;
        input exp_rdy;
        input [127:0] msg;
        begin
            if (RDY === exp_rdy) begin
                $display("[TC%0d PASS] %s : RDY=%0d (exp %0d)", tc_id, msg, RDY, exp_rdy);
            end else begin
                errors = errors + 1;
                $display("[TC%0d FAIL] %s : RDY=%0d (exp %0d)", tc_id, msg, RDY, exp_rdy);
            end
        end
    endtask

    // ==================================================================
    // Test Cases
    // ==================================================================
    initial begin
        // 初始化
        errors      = 0;
        tc_id       = 0;
        LOOP_BREAK  = 1'b0;
        RST_N       = 1'b1;     // 上电先拉高, 由 do_reset 控制复位
        vco_en      = 1'b0;
        vco.vco_base    = 12.437;   // 默认: code=0 -> 12.437GHz
        vco.vco_step    = 0.27786;  // 默认: 每档降 0.27786GHz (示例数据拟合)

        // 等待 DUT initial 块完成
        #(REFCLK_PERIOD * 10);

        // --------------------------------------------------------------
        // TC1: 正常校准 (默认 VCO 参数, 期望 code=9)
        // --------------------------------------------------------------
        tc_id   = 1;
        tc_name = "Normal Calib";
        vco_en  = 1'b1;
        set_vco(12.437, 0.27786);
        do_reset;               // 可综合版: 启动前先复位
        #(REFCLK_PERIOD * 20);
        start_calib;
        wait_rdy_rise(2000);   // 超时 2000us
        if (wait_ok) begin
            check_rdy(1'b1, "RDY high after calib");
            check_code(5'd9, "final code");
        end else begin
            errors = errors + 1;
            $display("[TC1 FAIL] Timeout waiting RDY");
        end
        stop_calib;
        #(REFCLK_PERIOD * 20);
        // 拉低后 vcode/RDY 应保持
        check_code(5'd9, "code held after LB low");
        check_rdy(1'b1, "RDY held after LB low");

        // --------------------------------------------------------------
        // TC2: code=0 即达标 (VCO 初始频率低于目标)
        // --------------------------------------------------------------
        tc_id   = 2;
        tc_name = "Code0 Already Match";
        set_vco(9.5, 0.2);     // code=0 -> 9.5GHz < 10GHz, FBCLK<25MHz
        #(REFCLK_PERIOD * 20);
        start_calib;
        wait_rdy_rise(2000);
        if (wait_ok) begin
            check_rdy(1'b1, "RDY high");
            check_code(5'd0, "code=0 match");
        end else begin
            errors = errors + 1;
            $display("[TC2 FAIL] Timeout waiting RDY");
        end
        stop_calib;
        #(REFCLK_PERIOD * 20);

        // --------------------------------------------------------------
        // TC3: code=15 仍未达标 (VCO 一直偏高, 期望锁定 15)
        // --------------------------------------------------------------
        tc_id   = 3;
        tc_name = "Max Code Lock";
        set_vco(15.0, 0.1);    // code=15 -> 13.5GHz 仍>10GHz
        #(REFCLK_PERIOD * 20);
        start_calib;
        wait_rdy_rise(3000);
        if (wait_ok) begin
            check_rdy(1'b1, "RDY high at max");
            check_code(5'd15, "code=15 lock");
        end else begin
            errors = errors + 1;
            $display("[TC3 FAIL] Timeout waiting RDY");
        end
        stop_calib;
        #(REFCLK_PERIOD * 20);

        // --------------------------------------------------------------
        // TC4: 中途退出 (校准未完成时 LB 拉低, 期望 VCODE 归 0)
        // --------------------------------------------------------------
        tc_id   = 4;
        tc_name = "Abort Mid-calib";
        set_vco(12.437, 0.27786);
        #(REFCLK_PERIOD * 20);
        start_calib;
        // 动态等待校准"进行中": 先等 re-trigger 复位把 code 归 0, 再等第一窗
        // 判定完成 code 开始递增 (vcode>=1)。不使用固定延时: WINDOW_LEN 在
        // model(=1024) 与 synth(=64) 中不同, 固定 120us 在 synth 下晚于校准
        // 完成时刻 (~39us 即 DONE), DONE 后 LB 拉低按规格保持结果, 无法触发
        // abort, 导致 TC4 误报 FAIL。
        wait (CAP_CTRL_OUT == 5'd0);
        wait (CAP_CTRL_OUT != 5'd0);
        #(REFCLK_PERIOD * 20);    // 此刻处于窗口计数/稳定阶段, 距 DONE 尚远
        // 拉低 LB 中断校准
        stop_calib;
        #(REFCLK_PERIOD * 20);
        check_rdy(1'b0, "RDY low after abort");
        check_code(5'd0, "code reset to 0 after abort");
        #(REFCLK_PERIOD * 20);

        // --------------------------------------------------------------
        // TC5: 重新触发 (DONE 后再次 LB 上升沿, 重新校准到 code=9)
        // --------------------------------------------------------------
        tc_id   = 5;
        tc_name = "Re-trigger";
        set_vco(12.437, 0.27786);
        // 先完成一次校准
        start_calib;
        wait_rdy_rise(2000);
        if (!wait_ok) begin
            errors = errors + 1;
            $display("[TC5 FAIL] Timeout first calib");
        end
        #(REFCLK_PERIOD * 20);
        check_code(5'd9, "first calib code=9");
        // 拉低 LB 进入正常模式
        stop_calib;
        #(REFCLK_PERIOD * 20);
        check_code(5'd9, "code held after LB low");
        check_rdy(1'b1, "RDY held after LB low");
        // 重新触发
        start_calib;
        #(REFCLK_PERIOD * 5);
        check_rdy(1'b0, "RDY low on re-trigger");
        // 等待重新校准完成
        wait_rdy_rise(2000);
        if (wait_ok) begin
            check_rdy(1'b1, "RDY high after re-calib");
            check_code(5'd9, "re-calib code=9");
        end else begin
            errors = errors + 1;
            $display("[TC5 FAIL] Timeout re-calib");
        end
        stop_calib;
        #(REFCLK_PERIOD * 50);

        // --------------------------------------------------------------
        // 汇总
        // --------------------------------------------------------------
        $display("==================================================");
        if (errors == 0)
            $display("ALL TESTS PASSED");
        else
            $display("TESTS FAILED: %0d errors", errors);
        $display("==================================================");
        $finish;
    end

    // 全局超时保护
    initial begin
`ifdef FAST_SIM
        #(20 * 1000 * 1000);   // 20ms
`else
        #(10 * 1000 * 1000);   // 10ms
`endif
        $display("[ERROR] Global timeout reached");
        $finish;
    end

endmodule

// vco_fb_model 由 filelist_synth.f 引入 (sim/vco_fb_model.v)
