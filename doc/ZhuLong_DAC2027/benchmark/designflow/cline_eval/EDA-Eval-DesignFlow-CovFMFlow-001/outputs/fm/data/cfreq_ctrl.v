//####################################################
// Description
//####################################################
// Revision History
//  -v1.0  Lorik Xiao  2026-10-19
//      Initial version
//  -v1.1  Lorik Xiao  2026-10-23
//      WINDOW_LEN/THRESHOLD 改为 10bit 输入端口; 删除稳定复验(STABLE_CNT);
//      START_SETTLE 改 10bit; CAP_SETTLE/GATE_SYNC_DLY 改 4bit
//####################################################

// ============================================================================
// cfreq_ctrl.v
// VCO 自动校准模块 (Synthesizable RTL, Verilog-2001)
//
// 功能: 固定 Vctrl=1/2 VDD, 通过单向递增电容阵列码将 VCO 输出校准到 ~10GHz
//       (FBCLK≈25MHz)。采用门控窗法在 REFCLK 域生成使能窗, 用 FBCLK 作计数
//       时钟在窗内统计脉冲数, 窗关闭后 REFCLK 域读值判定。
//
// 本文件为可综合版本。基于 behavior model (../rtl/cfreq_ctrl.v) 改造,
// 与 model 的差异点见下方"改造点"。
// 改造点:
//   - 新增 RST_N 复位端口 (低有效, 异步复位 + 同步释放)
//   - 删除 initial 块 (不可综合)
//   - REFCLK 域 / FBCLK 域各自 2 级同步释放复位
//   - 所有寄存器加异步复位分支, 复位值 = model initial 值
//   - WINDOW_LEN / THRESHOLD 改为外部输入端口 (10bit), 由上层或 TB 配置
//   - 删除稳定复验机制 (STABLE_CNT/stable_cnt/stable_phase):
//     单窗达标 (fb_cnt_latch <= THRESHOLD) 即进 DONE 拉 RDY
//
// Features:
//   - 单向递增搜索: VCODE 从 0 起步, 频率偏高则 +1, 达标则停止
//   - 门控窗计数 (CDC 简化法): REFCLK 域 gate, FBCLK 域同步后计数
//   - 达标即完成: 窗内 FBCLK 计数 <= THRESHOLD 直接拉 RDY (无稳定复验)
//   - LOOP_BREAK 上升沿为校准复位点, 可重新触发
//   - 边界: code=0 已达标保持 0; code=15 仍未达标保持 15 并拉 RDY
//   - 中途退出 (RDY 未高时 LB 拉低): 放弃本次, VCODE 归 0
//   - 复位后: RDY=0, CAP_CTRL_OUT=0, 所有寄存器归零 (与 model 上电等价)
//
// Version: 1.1-synth
// Changelog (v1.1-synth):
//   - WINDOW_LEN/THRESHOLD 由 parameter 改为 10bit 输入端口
//   - 删除 STABLE_CNT 稳定复验: 达标即 RDY
//   - START_SETTLE 位宽 16->10bit; CAP_SETTLE/GATE_SYNC_DLY 位宽 16/8->4bit
// Changelog (v1.0-synth):
//   - 基于 v1.0 model 改造为可综合 RTL, 新增 RST_N, 删除 initial
//
// ============================================================================

`timescale 1ns/1ps

module cfreq_ctrl (
    input  wire        REFCLK,        // 25MHz - 100MHz 参考时钟
    input  wire        FBCLK,         // VCO 输出 divider 分频后的反馈时钟
    input  wire        LOOP_BREAK,    // 上升沿=启动校准/复位点; 拉低=正常模式
    input  wire        RST_N,         // 异步复位 (低有效), 同步释放
    input  wire [9:0]  WINDOW_LEN,    // 比对窗口长度 (REFCLK 周期数, 10bit 外部输入)
    input  wire [9:0]  THRESHOLD,     // 停止阈值: FBCLK 计数<=此值即达标 (10bit, 通常=WINDOW_LEN)
    output reg         RDY,           // 校准完成标志
    output reg  [4:0]  CAP_CTRL_OUT   // 电容控制码, bit[4]恒0, 有效码 0~15
);

    // ----------------------------------------------------------------------
    // Parameters (WINDOW_LEN/THRESHOLD 已改为 10bit 输入端口, 见端口列表;
    //             STABLE_CNT 稳定复验机制已删除, 达标即 RDY)
    // ----------------------------------------------------------------------
    parameter [9:0]  START_SETTLE   = 10'd64;    // 启动后 VCO 起振等待 (REFCLK 周期)
    parameter [3:0]  CAP_SETTLE     = 4'd4;      // 每次 +1 后电容稳定等待 (REFCLK 周期)
    parameter [3:0]  GATE_SYNC_DLY  = 4'd4;      // CAP_WAIT 等待 FBCLK 域同步 gate=0 的拍数

    // 注: gate 高电平 = WINDOW_LEN 个 REFCLK 周期 (不做长度补偿), WINDOW_LEN/THRESHOLD
    //     由外部输入配置; fb_cnt ≈ WINDOW_LEN*(FBCLK_freq/REFCLK_freq), CDC ±1 误差
    //     可接受; THRESHOLD 通常配置为与 WINDOW_LEN 同值 (目标 FBCLK≈REFCLK)

    // ----------------------------------------------------------------------
    // FSM States
    // ----------------------------------------------------------------------
    localparam [3:0]
        ST_IDLE         = 4'd0,   // 等待 LOOP_BREAK 上升沿
        ST_START_SETTLE = 4'd1,   // 启动后等待 VCO 起振
        ST_WIN_COUNT    = 4'd2,   // 比对窗口计数 (gate=1)
        ST_CAP_WAIT     = 4'd3,   // 窗口结束, 等待 FBCLK 域同步 gate=0
        ST_DECIDE       = 4'd4,   // 判定: 达标/偏高/边界
        ST_CAP_SETTLE   = 4'd5,   // VCODE+1 后电容稳定等待
        ST_DONE         = 4'd6;   // 校准完成, RDY=1

    // ----------------------------------------------------------------------
    // Registers & Wires
    // ----------------------------------------------------------------------
    reg  [3:0]  c_st, n_st;
    reg  [9:0]  win_cnt;          // REFCLK 域窗口计数器 (WINDOW_LEN 10bit)
    reg  [9:0]  settle_cnt;       // 通用 settle 计数器 (START/CAP, START_SETTLE 10bit)
    reg  [3:0]  cap_wait_cnt;     // CAP_WAIT 等待计数器 (GATE_SYNC_DLY 4bit)
    reg         calib_done;       // 校准已完成标志 (DONE 后保持)
    reg  [3:0]  vcode;            // 电容控制码 (有效 0~15)

    // LOOP_BREAK 上升沿检测 (REFCLK 域, 两级同步寄存器化, posedge 沿稳定)
    reg         lb_d1;
    reg         lb_d2;
    wire        lb_rise = lb_d1 & ~lb_d2;   // 寄存器化脉冲, 避免组合竞争

    // gate 使能 (REFCLK 域, 组合产生, 跟随寄存器状态无毛刺)
    wire        gate    = (c_st == ST_WIN_COUNT);

    // FBCLK 域: gate 同步器 + 脉冲计数器
    reg         gate_sync_meta;
    reg         gate_sync;
    reg         gate_sync_prev;   // 用于检测 gate_sync 上升沿 (清 fb_cnt)
    reg  [15:0] fb_cnt;           // FBCLK 域脉冲计数器
    reg  [15:0] fb_cnt_latch;     // REFCLK 域锁存的计数值

    // 中途退出条件: 校准未完成 (非 DONE) 时 LOOP_BREAK 被拉低 (基于同步后 lb_d1)
    wire        abort = (c_st != ST_IDLE) && (c_st != ST_DONE) && (~lb_d1);

    // ----------------------------------------------------------------------
    // 0. 复位同步器: REFCLK 域 (异步复位, 同步释放)
    // ----------------------------------------------------------------------
    reg         rst_n_meta_ref;
    reg         rst_n_ref;
    always @(posedge REFCLK or negedge RST_N) begin
        if (!RST_N) begin
            rst_n_meta_ref <= 1'b0;
            rst_n_ref      <= 1'b0;
        end else begin
            rst_n_meta_ref <= 1'b1;
            rst_n_ref      <= rst_n_meta_ref;
        end
    end

    // ----------------------------------------------------------------------
    // 0b. 复位同步器: FBCLK 域 (异步复位, 同步释放)
    //     FBCLK 未起振时 rst_n_fb 保持 0, FBCLK 寄存器维持复位态;
    //     FBCLK 起振后 2 拍释放, 安全。与 model initial 行为等价。
    // ----------------------------------------------------------------------
    reg         rst_n_meta_fb;
    reg         rst_n_fb;
    always @(posedge FBCLK or negedge RST_N) begin
        if (!RST_N) begin
            rst_n_meta_fb <= 1'b0;
            rst_n_fb      <= 1'b0;
        end else begin
            rst_n_meta_fb <= 1'b1;
            rst_n_fb      <= rst_n_meta_fb;
        end
    end

    // ----------------------------------------------------------------------
    // 1. FSM 状态转移 (下一状态组合逻辑)
    // ----------------------------------------------------------------------
    always @(*) begin
        n_st = c_st;
        case (c_st)
            ST_IDLE: begin
                if (lb_rise) n_st = ST_START_SETTLE;
            end

            ST_START_SETTLE: begin
                if (abort) n_st = ST_IDLE;
                else if (settle_cnt >= START_SETTLE) n_st = ST_WIN_COUNT;
            end

            ST_WIN_COUNT: begin
                if (abort) n_st = ST_IDLE;
                else if (win_cnt >= (WINDOW_LEN - 10'd1)) n_st = ST_CAP_WAIT;
            end

            ST_CAP_WAIT: begin
                if (abort) n_st = ST_IDLE;
                else if (cap_wait_cnt >= GATE_SYNC_DLY) n_st = ST_DECIDE;
            end

            ST_DECIDE: begin
                // 判定后立即转移 (纯判定状态, 组合读 fb_cnt_latch)
                if (fb_cnt_latch > THRESHOLD) begin
                    // 频率偏高
                    if (vcode == 4'd15) n_st = ST_DONE;       // 已到最大值, 锁定完成
                    else                n_st = ST_CAP_SETTLE;  // +1 后继续
                end else begin
                    // 达标 -> 直接完成 (无稳定复验, 与 model 的 STABLE_CNT 机制不同)
                    n_st = ST_DONE;
                end
            end

            ST_CAP_SETTLE: begin
                if (abort) n_st = ST_IDLE;
                else if (settle_cnt >= CAP_SETTLE) n_st = ST_WIN_COUNT;
            end

            ST_DONE: begin
                if (lb_rise) n_st = ST_START_SETTLE;  // 重新触发
                // LOOP_BREAK 拉低时保持 DONE (calib_done 锁存, vcode 保持)
            end

            default: n_st = ST_IDLE;
        endcase
    end

    // ----------------------------------------------------------------------
    // 2. FSM 状态寄存器 + 数据通路更新 (REFCLK 域, 异步复位)
    // ----------------------------------------------------------------------
    always @(posedge REFCLK or negedge rst_n_ref) begin
        if (!rst_n_ref) begin
            c_st           <= ST_IDLE;
            win_cnt        <= 10'd0;
            settle_cnt     <= 10'd0;
            cap_wait_cnt   <= 4'd0;
            calib_done     <= 1'b0;
            vcode          <= 4'd0;
            fb_cnt_latch   <= 16'd0;
        end else begin
            c_st <= n_st;

            // LOOP_BREAK 上升沿: 校准复位点 (优先级最高)
            if (lb_rise) begin
                vcode        <= 4'd0;
                calib_done   <= 1'b0;
                win_cnt      <= 10'd0;
                settle_cnt   <= 10'd0;
                cap_wait_cnt <= 4'd0;
            end else if (abort) begin
                // 中途退出: 放弃本次, VCODE 归 0, 回 IDLE
                vcode        <= 4'd0;
                calib_done   <= 1'b0;
                win_cnt      <= 10'd0;
                settle_cnt   <= 10'd0;
                cap_wait_cnt <= 4'd0;
            end else begin
                case (c_st)
                    ST_IDLE: begin
                        // 保持 (vcode/calib_done 由 DONE 进入或重新触发控制)
                        win_cnt      <= 10'd0;
                        settle_cnt   <= 10'd0;
                        cap_wait_cnt <= 4'd0;
                    end

                    ST_START_SETTLE: begin
                        if (settle_cnt >= START_SETTLE) begin
                            settle_cnt <= 10'd0;
                            win_cnt    <= 10'd0;
                        end else begin
                            settle_cnt <= settle_cnt + 10'd1;
                        end
                    end

                    ST_WIN_COUNT: begin
                        if (win_cnt >= (WINDOW_LEN - 10'd1)) begin
                            win_cnt      <= 10'd0;
                            cap_wait_cnt <= 4'd0;  // 进入 CAP_WAIT 前清
                        end else begin
                            win_cnt <= win_cnt + 10'd1;
                        end
                    end

                    ST_CAP_WAIT: begin
                        // 等待 FBCLK 域同步 gate=0, 然后锁存 fb_cnt
                        if (cap_wait_cnt >= GATE_SYNC_DLY) begin
                            fb_cnt_latch <= fb_cnt;   // 读已稳定的 FBCLK 域计数值
                            cap_wait_cnt <= 4'd0;
                        end else begin
                            cap_wait_cnt <= cap_wait_cnt + 4'd1;
                        end
                    end

                    ST_DECIDE: begin
                        // 判定动作 (状态转移在组合逻辑, 此处更新数据通路)
                        // 频率偏高: vcode+1 (若 vcode==15 保持, 锁定)
                        // 达标:     vcode 保持, 状态机直达 ST_DONE (无稳定复验)
                        if (fb_cnt_latch > THRESHOLD) begin
                            if (vcode != 4'd15) vcode <= vcode + 4'd1;
                        end
                        win_cnt      <= 10'd0;
                        settle_cnt   <= 10'd0;
                        cap_wait_cnt <= 4'd0;
                    end

                    ST_CAP_SETTLE: begin
                        if (settle_cnt >= CAP_SETTLE) begin
                            settle_cnt <= 10'd0;
                            win_cnt    <= 10'd0;
                        end else begin
                            settle_cnt <= settle_cnt + 10'd1;
                        end
                    end

                    ST_DONE: begin
                        calib_done <= 1'b1;   // 锁存完成标志
                        // vcode 保持 (校准结果)
                    end

                    default: begin
                        win_cnt      <= 10'd0;
                        settle_cnt   <= 10'd0;
                        cap_wait_cnt <= 4'd0;
                    end
                endcase
            end
        end
    end

    // ----------------------------------------------------------------------
    // 2b. LOOP_BREAK 同步 (REFCLK 域, 异步复位)
    // ----------------------------------------------------------------------
    always @(posedge REFCLK or negedge rst_n_ref) begin
        if (!rst_n_ref) begin
            lb_d1 <= 1'b0;
            lb_d2 <= 1'b0;
        end else begin
            lb_d1 <= LOOP_BREAK;
            lb_d2 <= lb_d1;
        end
    end

    // ----------------------------------------------------------------------
    // 3. FBCLK 域: gate 同步器 + 脉冲计数器 (异步复位 rst_n_fb)
    // ----------------------------------------------------------------------
    always @(posedge FBCLK or negedge rst_n_fb) begin
        if (!rst_n_fb) begin
            gate_sync_meta <= 1'b0;
            gate_sync      <= 1'b0;
            gate_sync_prev <= 1'b0;
            fb_cnt         <= 16'd0;
        end else begin
            // 2 级同步器 (gate 来自 REFCLK 域)
            gate_sync_meta <= gate;
            gate_sync      <= gate_sync_meta;
            gate_sync_prev <= gate_sync;

            // gate_sync 上升沿: 清 fb_cnt (新窗口开始)
            // gate_sync 高电平期间: fb_cnt 计数
            if (gate_sync && ~gate_sync_prev) begin
                fb_cnt <= 16'd1;   // 当前拍即为第 1 个脉冲
            end else if (gate_sync) begin
                fb_cnt <= fb_cnt + 16'd1;
            end
            // gate_sync=0 期间 fb_cnt 保持 (供 REFCLK 域锁存)
        end
    end

    // ----------------------------------------------------------------------
    // 4. 输出生成 (REFCLK 域, 异步复位)
    // ----------------------------------------------------------------------
    always @(posedge REFCLK or negedge rst_n_ref) begin
        if (!rst_n_ref) begin
            RDY <= 1'b0;
        end else begin
            RDY <= calib_done;   // 校准完成后保持高; 重新触发时 calib_done 清 0 -> RDY 清 0
        end
    end

    always @(posedge REFCLK or negedge rst_n_ref) begin
        if (!rst_n_ref) begin
            CAP_CTRL_OUT <= 5'd0;
        end else begin
            CAP_CTRL_OUT <= {1'b0, vcode};   // bit[4] 恒 0, 有效码 0~15
        end
    end

endmodule