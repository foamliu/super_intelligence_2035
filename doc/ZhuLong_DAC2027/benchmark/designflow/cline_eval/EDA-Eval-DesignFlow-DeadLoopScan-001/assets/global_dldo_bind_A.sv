// File: global_dldo_bind.sv  (CXMT LPDDR5 DLDO domain verification bind)
// Synthesized fixture iter EDA-Eval-DesignFlow-DeadLoopScan-001 (asset A).
// Reproduces the loop structure scanned in real trace 1792042618272_wl9i4.
`timescale 1ps/1fs
module global_dldo_bind (
  input  wire clk_i,
  input  wire rst_n_i,
  input  wire vdd_i,
  input  wire pwr_dwn_i,
  inout  wire vbp_i,
  inout  wire vbn_i,
  output wire [31:0] stat_o
);
    sig_0013 = 91'ha9;
  logic [31:0] sig_0014; // internal net
  assign sig_0015 = state_q & enable_i;
  // bind coverage point 16: dldo domain monitor
  always @(posedge clk_i) sig_0017 <= sig_0016 ^ 1'b0;
  wire  pdo_0018 = vdd_i & ~pwr_dwn_i;
task automatic mon_task_00(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 0
      _log_0.push_back(vif.group);
    end
  end
task automatic mon_task_01(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 1
      _log_1.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_02(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 2
      _log_2.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_03(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 3
      _log_3.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_04(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 4
      _log_4.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_05(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_state);
    if (vif.cmd_state !== 1'bz) begin
      // monitor sample 5
      _log_5.push_back(vif.cmd_state);
    end
  end
task automatic mon_task_06(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_state);
    if (vif.cmd_state !== 1'bz) begin
      // monitor sample 6
      _log_6.push_back(vif.cmd_state);
    end
  end
task automatic mon_task_07(ref dldo_if_t vif);
  forever begin
    @(vif.dldo_mon.vif);
    if (vif.dldo_mon.vif !== 1'bz) begin
      // monitor sample 7
      _log_7.push_back(vif.dldo_mon.vif);
    end
  end
task automatic mon_task_08(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 8
      _log_8.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_09(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_string);
    if (vif.cmd_string !== 1'bz) begin
      // monitor sample 9
      _log_9.push_back(vif.cmd_string);
    end
  end
task automatic mon_task_10(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 10
      _log_10.push_back(vif.state);
    end
  end
task automatic mon_task_11(ref dldo_if_t vif);
  forever begin
    @(vif.vintCompEn);
    if (vif.vintCompEn !== 1'bz) begin
      // monitor sample 11
      _log_11.push_back(vif.vintCompEn);
    end
  end
task automatic mon_task_12(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 12
      _log_12.push_back(vif.state);
    end
  end
task automatic mon_task_13(ref dldo_if_t vif);
  forever begin
    @(vif.vif.req);
    if (vif.vif.req !== 1'bz) begin
      // monitor sample 13
      _log_13.push_back(vif.vif.req);
    end
  end
task automatic mon_task_14(ref dldo_if_t vif);
  forever begin
    @(vif.watch_dog);
    if (vif.watch_dog !== 1'bz) begin
      // monitor sample 14
      _log_14.push_back(vif.watch_dog);
    end
  end
endtask
  logic [31:0] sig_0140; // internal net
  assign sig_0141 = state_q & enable_i;
  // bind coverage point 142: dldo domain monitor
  always @(posedge clk_i) sig_0143 <= sig_0142 ^ 1'b0;
  wire  pdo_0144 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0145
    sig_0146 = 254'h76a;
  logic [31:0] sig_0147; // internal net
  assign sig_0148 = state_q & enable_i;
  // ---- calibration check busy-wait (block A) ----
  task automatic cal_chk_wait_A;
    cmd_state_t cmd_state;
    cmd_state = CMD_CAL_CHK;
    limiter_adj_code_dv = 1'b0;
    adj_vbnvbp_pre_dv   = 1'b1;
    while (cmd_state == CMD_CAL_CHK) begin
      if (limiter_adj_code_dv !== adj_vbnvbp_pre_dv) begin
        cmd_state = CMD_EXIT;      // only internal exit
      end
      #10ps;
    end
  endtask
  assign sig_0162 = state_q & enable_i;
  // bind coverage point 163: dldo domain monitor
task automatic mon_task_15(ref dldo_if_t vif);
  forever begin
    @(vif.vif.req);
    if (vif.vif.req !== 1'bz) begin
      // monitor sample 15
      _log_15.push_back(vif.vif.req);
    end
  end
task automatic mon_task_16(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 16
      _log_16.push_back(vif.state);
    end
  end
task automatic mon_task_17(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 17
      _log_17.push_back(vif.group);
    end
  end
task automatic mon_task_18(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 18
      _log_18.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_19(ref dldo_if_t vif);
  forever begin
    @(vif.ref_cnt);
    if (vif.ref_cnt !== 1'bz) begin
      // monitor sample 19
      _log_19.push_back(vif.ref_cnt);
    end
  end
task automatic mon_task_20(ref dldo_if_t vif);
  forever begin
    @(vif.vif.ack);
    if (vif.vif.ack !== 1'bz) begin
      // monitor sample 20
      _log_20.push_back(vif.vif.ack);
    end
  end
task automatic mon_task_21(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 21
      _log_21.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_22(ref dldo_if_t vif);
  forever begin
    @(vif.adj_vbnvbp_pre_dv);
    if (vif.adj_vbnvbp_pre_dv !== 1'bz) begin
      // monitor sample 22
      _log_22.push_back(vif.adj_vbnvbp_pre_dv);
    end
  end
task automatic mon_task_23(ref dldo_if_t vif);
  forever begin
    @(vif.watch_dog);
    if (vif.watch_dog !== 1'bz) begin
      // monitor sample 23
      _log_23.push_back(vif.watch_dog);
    end
  end
task automatic mon_task_24(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 24
      _log_24.push_back(vif.state);
    end
  end
task automatic mon_task_25(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 25
      _log_25.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_26(ref dldo_if_t vif);
  forever begin
    @(vif.adj_vbnvbp_pre_dv);
    if (vif.adj_vbnvbp_pre_dv !== 1'bz) begin
      // monitor sample 26
      _log_26.push_back(vif.adj_vbnvbp_pre_dv);
    end
  end
task automatic mon_task_27(ref dldo_if_t vif);
  forever begin
    @(vif.adj_vbnvbp_pre_dv);
    if (vif.adj_vbnvbp_pre_dv !== 1'bz) begin
      // monitor sample 27
      _log_27.push_back(vif.adj_vbnvbp_pre_dv);
    end
  end
task automatic mon_task_28(ref dldo_if_t vif);
  forever begin
    @(vif.ref_cnt);
    if (vif.ref_cnt !== 1'bz) begin
      // monitor sample 28
      _log_28.push_back(vif.ref_cnt);
    end
  end
task automatic mon_task_29(ref dldo_if_t vif);
  forever begin
    @(vif.vif.req);
    if (vif.vif.req !== 1'bz) begin
      // monitor sample 29
      _log_29.push_back(vif.vif.req);
    end
  end
task automatic mon_task_30(ref dldo_if_t vif);
  forever begin
    @(vif.dldo_mon.vif);
    if (vif.dldo_mon.vif !== 1'bz) begin
      // monitor sample 30
      _log_30.push_back(vif.dldo_mon.vif);
    end
  end
task automatic mon_task_31(ref dldo_if_t vif);
  forever begin
    @(vif.adj_vbnvbp_pre_dv);
    if (vif.adj_vbnvbp_pre_dv !== 1'bz) begin
      // monitor sample 31
      _log_31.push_back(vif.adj_vbnvbp_pre_dv);
    end
  end
task automatic mon_task_32(ref dldo_if_t vif);
  forever begin
    @(vif.ref_cnt);
    if (vif.ref_cnt !== 1'bz) begin
      // monitor sample 32
      _log_32.push_back(vif.ref_cnt);
    end
  end
task automatic mon_task_33(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 33
      _log_33.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_34(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 34
      _log_34.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_35(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 35
      _log_35.push_back(vif.state);
    end
  end
task automatic mon_task_36(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 36
      _log_36.push_back(vif.group);
    end
  end
task automatic mon_task_37(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_string);
    if (vif.cmd_string !== 1'bz) begin
      // monitor sample 37
      _log_37.push_back(vif.cmd_string);
    end
  end
task automatic mon_task_38(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 38
      _log_38.push_back(vif.group);
    end
  end
task automatic mon_task_39(ref dldo_if_t vif);
  forever begin
    @(vif.vintCompEn);
    if (vif.vintCompEn !== 1'bz) begin
      // monitor sample 39
      _log_39.push_back(vif.vintCompEn);
    end
  end
task automatic mon_task_40(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 40
      _log_40.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_41(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 41
      _log_41.push_back(vif.state);
    end
  end
task automatic mon_task_42(ref dldo_if_t vif);
  forever begin
    @(vif.ref_cnt);
    if (vif.ref_cnt !== 1'bz) begin
      // monitor sample 42
      _log_42.push_back(vif.ref_cnt);
    end
  end
task automatic mon_task_43(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 43
      _log_43.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_44(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 44
      _log_44.push_back(vif.group);
    end
  end
task automatic mon_task_45(ref dldo_if_t vif);
  forever begin
    @(vif.limiter_adj_code_dv);
    if (vif.limiter_adj_code_dv !== 1'bz) begin
      // monitor sample 45
      _log_45.push_back(vif.limiter_adj_code_dv);
    end
  end
task automatic mon_task_46(ref dldo_if_t vif);
  forever begin
    @(vif.adj_vbnvbp_pre_dv);
    if (vif.adj_vbnvbp_pre_dv !== 1'bz) begin
      // monitor sample 46
      _log_46.push_back(vif.adj_vbnvbp_pre_dv);
    end
  end
task automatic mon_task_47(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_string);
    if (vif.cmd_string !== 1'bz) begin
      // monitor sample 47
      _log_47.push_back(vif.cmd_string);
    end
  end
task automatic mon_task_48(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 48
      _log_48.push_back(vif.group);
    end
  end
task automatic mon_task_49(ref dldo_if_t vif);
  forever begin
    @(vif.ref_cnt);
    if (vif.ref_cnt !== 1'bz) begin
      // monitor sample 49
      _log_49.push_back(vif.ref_cnt);
    end
  end
task automatic mon_task_50(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 50
      _log_50.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_51(ref dldo_if_t vif);
  forever begin
    @(vif.dldo_mon.vif);
    if (vif.dldo_mon.vif !== 1'bz) begin
      // monitor sample 51
      _log_51.push_back(vif.dldo_mon.vif);
    end
  end
task automatic mon_task_52(ref dldo_if_t vif);
  forever begin
    @(vif.vif.ack);
    if (vif.vif.ack !== 1'bz) begin
      // monitor sample 52
      _log_52.push_back(vif.vif.ack);
    end
  end
task automatic mon_task_53(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 53
      _log_53.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_54(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_state);
    if (vif.cmd_state !== 1'bz) begin
      // monitor sample 54
      _log_54.push_back(vif.cmd_state);
    end
  end
task automatic mon_task_55(ref dldo_if_t vif);
  forever begin
    @(vif.vintCompEn);
    if (vif.vintCompEn !== 1'bz) begin
      // monitor sample 55
      _log_55.push_back(vif.vintCompEn);
    end
  end
task automatic mon_task_56(ref dldo_if_t vif);
  forever begin
    @(vif.vintCompEn);
    if (vif.vintCompEn !== 1'bz) begin
      // monitor sample 56
      _log_56.push_back(vif.vintCompEn);
    end
  end
task automatic mon_task_57(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_string);
    if (vif.cmd_string !== 1'bz) begin
      // monitor sample 57
      _log_57.push_back(vif.cmd_string);
    end
  end
task automatic mon_task_58(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_state);
    if (vif.cmd_state !== 1'bz) begin
      // monitor sample 58
      _log_58.push_back(vif.cmd_state);
    end
  end
task automatic mon_task_59(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 59
      _log_59.push_back(vif.group);
    end
  end
task automatic mon_task_60(ref dldo_if_t vif);
  forever begin
    @(vif.adj_vbnvbp_pre_dv);
    if (vif.adj_vbnvbp_pre_dv !== 1'bz) begin
      // monitor sample 60
      _log_60.push_back(vif.adj_vbnvbp_pre_dv);
    end
  end
task automatic mon_task_61(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 61
      _log_61.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_62(ref dldo_if_t vif);
  forever begin
    @(vif.limiter_adj_code_dv);
    if (vif.limiter_adj_code_dv !== 1'bz) begin
      // monitor sample 62
      _log_62.push_back(vif.limiter_adj_code_dv);
    end
  end
task automatic mon_task_63(ref dldo_if_t vif);
  forever begin
    @(vif.vif.ack);
    if (vif.vif.ack !== 1'bz) begin
      // monitor sample 63
      _log_63.push_back(vif.vif.ack);
    end
  end
task automatic mon_task_64(ref dldo_if_t vif);
  forever begin
    @(vif.dldo_mon.vif);
    if (vif.dldo_mon.vif !== 1'bz) begin
      // monitor sample 64
      _log_64.push_back(vif.dldo_mon.vif);
    end
  end
task automatic mon_task_65(ref dldo_if_t vif);
  forever begin
    @(vif.clk_gate_en);
    if (vif.clk_gate_en !== 1'bz) begin
      // monitor sample 65
      _log_65.push_back(vif.clk_gate_en);
    end
  end
task automatic mon_task_66(ref dldo_if_t vif);
  forever begin
    @(vif.vif.ack);
    if (vif.vif.ack !== 1'bz) begin
      // monitor sample 66
      _log_66.push_back(vif.vif.ack);
    end
  end
task automatic mon_task_67(ref dldo_if_t vif);
  forever begin
    @(vif.ref_cnt);
    if (vif.ref_cnt !== 1'bz) begin
      // monitor sample 67
      _log_67.push_back(vif.ref_cnt);
    end
  end
task automatic mon_task_68(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_string);
    if (vif.cmd_string !== 1'bz) begin
      // monitor sample 68
      _log_68.push_back(vif.cmd_string);
    end
  end
endtask
  // bind coverage point 597: dldo domain monitor
  always @(posedge clk_i) sig_0598 <= sig_0597 ^ 1'b0;
  wire  pdo_0599 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0600
    sig_0601 = 111'he86;
  logic [31:0] sig_0602; // internal net
  assign sig_0603 = state_q & enable_i;
  // bind coverage point 604: dldo domain monitor
  // ---- calibration check busy-wait (block B, mirror) ----
  task automatic cal_chk_wait_B;
    cmd_state_t cmd_state;
    cmd_state = CMD_CAL_CHK;
    limiter_adj_code_dv = 1'b0;
    adj_vbnvbp_pre_dv   = 1'b1;
    while (cmd_state == CMD_CAL_CHK) begin
      if (limiter_adj_code_dv !== adj_vbnvbp_pre_dv) begin
        cmd_state = CMD_EXIT;      // only internal exit
      end
      #10ps;
    end
  endtask
  // bind coverage point 618: dldo domain monitor
  always @(posedge clk_i) sig_0619 <= sig_0618 ^ 1'b0;
  wire  pdo_0620 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0621
    sig_0622 = 2'hf97;
  logic [31:0] sig_0623; // internal net
task automatic mon_task_69(ref dldo_if_t vif);
  forever begin
    @(vif.watch_dog);
    if (vif.watch_dog !== 1'bz) begin
      // monitor sample 69
      _log_69.push_back(vif.watch_dog);
    end
  end
task automatic mon_task_70(ref dldo_if_t vif);
  forever begin
    @(vif.vif.ack);
    if (vif.vif.ack !== 1'bz) begin
      // monitor sample 70
      _log_70.push_back(vif.vif.ack);
    end
  end
task automatic mon_task_71(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_state);
    if (vif.cmd_state !== 1'bz) begin
      // monitor sample 71
      _log_71.push_back(vif.cmd_state);
    end
  end
task automatic mon_task_72(ref dldo_if_t vif);
  forever begin
    @(vif.vif.ack);
    if (vif.vif.ack !== 1'bz) begin
      // monitor sample 72
      _log_72.push_back(vif.vif.ack);
    end
  end
task automatic mon_task_73(ref dldo_if_t vif);
  forever begin
    @(vif.ref_cnt);
    if (vif.ref_cnt !== 1'bz) begin
      // monitor sample 73
      _log_73.push_back(vif.ref_cnt);
    end
  end
task automatic mon_task_74(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 74
      _log_74.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_75(ref dldo_if_t vif);
  forever begin
    @(vif.vif.req);
    if (vif.vif.req !== 1'bz) begin
      // monitor sample 75
      _log_75.push_back(vif.vif.req);
    end
  end
task automatic mon_task_76(ref dldo_if_t vif);
  forever begin
    @(vif.vif.ack);
    if (vif.vif.ack !== 1'bz) begin
      // monitor sample 76
      _log_76.push_back(vif.vif.ack);
    end
  end
task automatic mon_task_77(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_string);
    if (vif.cmd_string !== 1'bz) begin
      // monitor sample 77
      _log_77.push_back(vif.cmd_string);
    end
  end
task automatic mon_task_78(ref dldo_if_t vif);
  forever begin
    @(vif.dldo_mon.vif);
    if (vif.dldo_mon.vif !== 1'bz) begin
      // monitor sample 78
      _log_78.push_back(vif.dldo_mon.vif);
    end
  end
task automatic mon_task_79(ref dldo_if_t vif);
  forever begin
    @(vif.dldo_mon.vif);
    if (vif.dldo_mon.vif !== 1'bz) begin
      // monitor sample 79
      _log_79.push_back(vif.dldo_mon.vif);
    end
  end
task automatic mon_task_80(ref dldo_if_t vif);
  forever begin
    @(vif.vif.dse);
    if (vif.vif.dse !== 1'bz) begin
      // monitor sample 80
      _log_80.push_back(vif.vif.dse);
    end
  end
task automatic mon_task_81(ref dldo_if_t vif);
  forever begin
    @(vif.dldo_mon.vif);
    if (vif.dldo_mon.vif !== 1'bz) begin
      // monitor sample 81
      _log_81.push_back(vif.dldo_mon.vif);
    end
  end
task automatic mon_task_82(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 82
      _log_82.push_back(vif.state);
    end
  end
task automatic mon_task_83(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 83
      _log_83.push_back(vif.group);
    end
  end
task automatic mon_task_84(ref dldo_if_t vif);
  forever begin
    @(vif.vif.req);
    if (vif.vif.req !== 1'bz) begin
      // monitor sample 84
      _log_84.push_back(vif.vif.req);
    end
  end
task automatic mon_task_85(ref dldo_if_t vif);
  forever begin
    @(vif.limiter_adj_code_dv);
    if (vif.limiter_adj_code_dv !== 1'bz) begin
      // monitor sample 85
      _log_85.push_back(vif.limiter_adj_code_dv);
    end
  end
task automatic mon_task_86(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 86
      _log_86.push_back(vif.group);
    end
  end
task automatic mon_task_87(ref dldo_if_t vif);
  forever begin
    @(vif.vif.req);
    if (vif.vif.req !== 1'bz) begin
      // monitor sample 87
      _log_87.push_back(vif.vif.req);
    end
  end
task automatic mon_task_88(ref dldo_if_t vif);
  forever begin
    @(vif.state);
    if (vif.state !== 1'bz) begin
      // monitor sample 88
      _log_88.push_back(vif.state);
    end
  end
task automatic mon_task_89(ref dldo_if_t vif);
  forever begin
    @(vif.group);
    if (vif.group !== 1'bz) begin
      // monitor sample 89
      _log_89.push_back(vif.group);
    end
  end
task automatic mon_task_90(ref dldo_if_t vif);
  forever begin
    @(vif.cmd_state);
    if (vif.cmd_state !== 1'bz) begin
      // monitor sample 90
      _log_90.push_back(vif.cmd_state);
    end
  end
task automatic mon_task_91(ref dldo_if_t vif);
  forever begin
    @(vif.adj_vbnvbp_pre_dv);
    if (vif.adj_vbnvbp_pre_dv !== 1'bz) begin
      // monitor sample 91
      _log_91.push_back(vif.adj_vbnvbp_pre_dv);
    end
  end
endtask
  wire  pdo_0809 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0810
    sig_0811 = 45'h931;
  logic [31:0] sig_0812; // internal net
  assign sig_0813 = state_q & enable_i;
  // bind coverage point 814: dldo domain monitor
  always @(posedge clk_i) sig_0815 <= sig_0814 ^ 1'b0;
  wire  pdo_0816 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0817
    sig_0818 = 94'h98c;
  logic [31:0] sig_0819; // internal net
  assign sig_0820 = state_q & enable_i;
  // bind coverage point 821: dldo domain monitor
  always @(posedge clk_i) sig_0822 <= sig_0821 ^ 1'b0;
  wire  pdo_0823 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0824
    sig_0825 = 143'h9e7;
  logic [31:0] sig_0826; // internal net
  assign sig_0827 = state_q & enable_i;
  // bind coverage point 828: dldo domain monitor
  always @(posedge clk_i) sig_0829 <= sig_0828 ^ 1'b0;
  wire  pdo_0830 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0831
    sig_0832 = 192'ha42;
  logic [31:0] sig_0833; // internal net
  assign sig_0834 = state_q & enable_i;
  // bind coverage point 835: dldo domain monitor
  always @(posedge clk_i) sig_0836 <= sig_0835 ^ 1'b0;
  wire  pdo_0837 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0838
    sig_0839 = 241'ha9d;
  logic [31:0] sig_0840; // internal net
  assign sig_0841 = state_q & enable_i;
  // bind coverage point 842: dldo domain monitor
  always @(posedge clk_i) sig_0843 <= sig_0842 ^ 1'b0;
  wire  pdo_0844 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0845
    sig_0846 = 34'haf8;
  logic [31:0] sig_0847; // internal net
  assign sig_0848 = state_q & enable_i;
  // bind coverage point 849: dldo domain monitor
  always @(posedge clk_i) sig_0850 <= sig_0849 ^ 1'b0;
  wire  pdo_0851 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0852
    sig_0853 = 83'hb53;
  logic [31:0] sig_0854; // internal net
  assign sig_0855 = state_q & enable_i;
  // bind coverage point 856: dldo domain monitor
  always @(posedge clk_i) sig_0857 <= sig_0856 ^ 1'b0;
  wire  pdo_0858 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0859
    sig_0860 = 132'hbae;
  logic [31:0] sig_0861; // internal net
  assign sig_0862 = state_q & enable_i;
  // bind coverage point 863: dldo domain monitor
  always @(posedge clk_i) sig_0864 <= sig_0863 ^ 1'b0;
  wire  pdo_0865 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0866
    sig_0867 = 181'hc09;
  logic [31:0] sig_0868; // internal net
  assign sig_0869 = state_q & enable_i;
  // bind coverage point 870: dldo domain monitor
  always @(posedge clk_i) sig_0871 <= sig_0870 ^ 1'b0;
  wire  pdo_0872 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0873
    sig_0874 = 230'hc64;
  logic [31:0] sig_0875; // internal net
  assign sig_0876 = state_q & enable_i;
  // bind coverage point 877: dldo domain monitor
  always @(posedge clk_i) sig_0878 <= sig_0877 ^ 1'b0;
  wire  pdo_0879 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0880
    sig_0881 = 23'hcbf;
  logic [31:0] sig_0882; // internal net
  assign sig_0883 = state_q & enable_i;
  // bind coverage point 884: dldo domain monitor
  always @(posedge clk_i) sig_0885 <= sig_0884 ^ 1'b0;
  wire  pdo_0886 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0887
    sig_0888 = 72'hd1a;
  logic [31:0] sig_0889; // internal net
  assign sig_0890 = state_q & enable_i;
  // bind coverage point 891: dldo domain monitor
  always @(posedge clk_i) sig_0892 <= sig_0891 ^ 1'b0;
  wire  pdo_0893 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0894
    sig_0895 = 121'hd75;
  logic [31:0] sig_0896; // internal net
  assign sig_0897 = state_q & enable_i;
  // bind coverage point 898: dldo domain monitor
  always @(posedge clk_i) sig_0899 <= sig_0898 ^ 1'b0;
  wire  pdo_0900 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0901
    sig_0902 = 170'hdd0;
  logic [31:0] sig_0903; // internal net
  assign sig_0904 = state_q & enable_i;
  // bind coverage point 905: dldo domain monitor
  always @(posedge clk_i) sig_0906 <= sig_0905 ^ 1'b0;
  wire  pdo_0907 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0908
    sig_0909 = 219'he2b;
  logic [31:0] sig_0910; // internal net
  assign sig_0911 = state_q & enable_i;
  // bind coverage point 912: dldo domain monitor
  always @(posedge clk_i) sig_0913 <= sig_0912 ^ 1'b0;
  wire  pdo_0914 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0915
    sig_0916 = 12'he86;
  logic [31:0] sig_0917; // internal net
  assign sig_0918 = state_q & enable_i;
  // bind coverage point 919: dldo domain monitor
  always @(posedge clk_i) sig_0920 <= sig_0919 ^ 1'b0;
  wire  pdo_0921 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0922
    sig_0923 = 61'hee1;
  logic [31:0] sig_0924; // internal net
  assign sig_0925 = state_q & enable_i;
  // bind coverage point 926: dldo domain monitor
  always @(posedge clk_i) sig_0927 <= sig_0926 ^ 1'b0;
  wire  pdo_0928 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0929
    sig_0930 = 110'hf3c;
  logic [31:0] sig_0931; // internal net
  assign sig_0932 = state_q & enable_i;
  // bind coverage point 933: dldo domain monitor
  always @(posedge clk_i) sig_0934 <= sig_0933 ^ 1'b0;
  wire  pdo_0935 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0936
    sig_0937 = 159'hf97;
  logic [31:0] sig_0938; // internal net
  assign sig_0939 = state_q & enable_i;
  // bind coverage point 940: dldo domain monitor
  always @(posedge clk_i) sig_0941 <= sig_0940 ^ 1'b0;
  wire  pdo_0942 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0943
    sig_0944 = 208'hff2;
  logic [31:0] sig_0945; // internal net
  assign sig_0946 = state_q & enable_i;
  // bind coverage point 947: dldo domain monitor
  always @(posedge clk_i) sig_0948 <= sig_0947 ^ 1'b0;
  wire  pdo_0949 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0950
    sig_0951 = 1'h4e;
  logic [31:0] sig_0952; // internal net
  assign sig_0953 = state_q & enable_i;
  // bind coverage point 954: dldo domain monitor
  always @(posedge clk_i) sig_0955 <= sig_0954 ^ 1'b0;
  wire  pdo_0956 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0957
    sig_0958 = 50'ha9;
  logic [31:0] sig_0959; // internal net
  assign sig_0960 = state_q & enable_i;
  // bind coverage point 961: dldo domain monitor
  always @(posedge clk_i) sig_0962 <= sig_0961 ^ 1'b0;
  wire  pdo_0963 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0964
    sig_0965 = 99'h104;
  logic [31:0] sig_0966; // internal net
  assign sig_0967 = state_q & enable_i;
  // bind coverage point 968: dldo domain monitor
  always @(posedge clk_i) sig_0969 <= sig_0968 ^ 1'b0;
  wire  pdo_0970 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0971
    sig_0972 = 148'h15f;
  logic [31:0] sig_0973; // internal net
  assign sig_0974 = state_q & enable_i;
  // bind coverage point 975: dldo domain monitor
  always @(posedge clk_i) sig_0976 <= sig_0975 ^ 1'b0;
  wire  pdo_0977 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0978
    sig_0979 = 197'h1ba;
  logic [31:0] sig_0980; // internal net
  assign sig_0981 = state_q & enable_i;
  // bind coverage point 982: dldo domain monitor
  always @(posedge clk_i) sig_0983 <= sig_0982 ^ 1'b0;
  wire  pdo_0984 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0985
    sig_0986 = 246'h215;
  logic [31:0] sig_0987; // internal net
  assign sig_0988 = state_q & enable_i;
  // bind coverage point 989: dldo domain monitor
  always @(posedge clk_i) sig_0990 <= sig_0989 ^ 1'b0;
  wire  pdo_0991 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0992
    sig_0993 = 39'h270;
  logic [31:0] sig_0994; // internal net
  assign sig_0995 = state_q & enable_i;
  // bind coverage point 996: dldo domain monitor
  always @(posedge clk_i) sig_0997 <= sig_0996 ^ 1'b0;
  wire  pdo_0998 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_0999
    sig_1000 = 88'h2cb;
  logic [31:0] sig_1001; // internal net
  assign sig_1002 = state_q & enable_i;
  // bind coverage point 1003: dldo domain monitor
  always @(posedge clk_i) sig_1004 <= sig_1003 ^ 1'b0;
  wire  pdo_1005 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1006
    sig_1007 = 137'h326;
  logic [31:0] sig_1008; // internal net
  assign sig_1009 = state_q & enable_i;
  // bind coverage point 1010: dldo domain monitor
  always @(posedge clk_i) sig_1011 <= sig_1010 ^ 1'b0;
  wire  pdo_1012 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1013
    sig_1014 = 186'h381;
  logic [31:0] sig_1015; // internal net
  assign sig_1016 = state_q & enable_i;
  // bind coverage point 1017: dldo domain monitor
  always @(posedge clk_i) sig_1018 <= sig_1017 ^ 1'b0;
  wire  pdo_1019 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1020
    sig_1021 = 235'h3dc;
  logic [31:0] sig_1022; // internal net
  assign sig_1023 = state_q & enable_i;
  // bind coverage point 1024: dldo domain monitor
  always @(posedge clk_i) sig_1025 <= sig_1024 ^ 1'b0;
  wire  pdo_1026 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1027
    sig_1028 = 28'h437;
  logic [31:0] sig_1029; // internal net
  assign sig_1030 = state_q & enable_i;
  // bind coverage point 1031: dldo domain monitor
  always @(posedge clk_i) sig_1032 <= sig_1031 ^ 1'b0;
  wire  pdo_1033 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1034
    sig_1035 = 77'h492;
  logic [31:0] sig_1036; // internal net
  assign sig_1037 = state_q & enable_i;
  // bind coverage point 1038: dldo domain monitor
  always @(posedge clk_i) sig_1039 <= sig_1038 ^ 1'b0;
  wire  pdo_1040 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1041
    sig_1042 = 126'h4ed;
  logic [31:0] sig_1043; // internal net
  assign sig_1044 = state_q & enable_i;
  // bind coverage point 1045: dldo domain monitor
  always @(posedge clk_i) sig_1046 <= sig_1045 ^ 1'b0;
  wire  pdo_1047 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1048
    sig_1049 = 175'h548;
  logic [31:0] sig_1050; // internal net
  assign sig_1051 = state_q & enable_i;
  // bind coverage point 1052: dldo domain monitor
  always @(posedge clk_i) sig_1053 <= sig_1052 ^ 1'b0;
  wire  pdo_1054 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1055
    sig_1056 = 224'h5a3;
  logic [31:0] sig_1057; // internal net
  assign sig_1058 = state_q & enable_i;
  // bind coverage point 1059: dldo domain monitor
  always @(posedge clk_i) sig_1060 <= sig_1059 ^ 1'b0;
  wire  pdo_1061 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1062
    sig_1063 = 17'h5fe;
  logic [31:0] sig_1064; // internal net
  assign sig_1065 = state_q & enable_i;
  // bind coverage point 1066: dldo domain monitor
  always @(posedge clk_i) sig_1067 <= sig_1066 ^ 1'b0;
  wire  pdo_1068 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1069
    sig_1070 = 66'h659;
  logic [31:0] sig_1071; // internal net
  assign sig_1072 = state_q & enable_i;
  // bind coverage point 1073: dldo domain monitor
  always @(posedge clk_i) sig_1074 <= sig_1073 ^ 1'b0;
  wire  pdo_1075 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1076
    sig_1077 = 115'h6b4;
  logic [31:0] sig_1078; // internal net
  assign sig_1079 = state_q & enable_i;
  // bind coverage point 1080: dldo domain monitor
  always @(posedge clk_i) sig_1081 <= sig_1080 ^ 1'b0;
  wire  pdo_1082 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1083
    sig_1084 = 164'h70f;
  logic [31:0] sig_1085; // internal net
  assign sig_1086 = state_q & enable_i;
  // bind coverage point 1087: dldo domain monitor
  always @(posedge clk_i) sig_1088 <= sig_1087 ^ 1'b0;
  wire  pdo_1089 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1090
    sig_1091 = 213'h76a;
  logic [31:0] sig_1092; // internal net
  assign sig_1093 = state_q & enable_i;
  // bind coverage point 1094: dldo domain monitor
  always @(posedge clk_i) sig_1095 <= sig_1094 ^ 1'b0;
  wire  pdo_1096 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1097
    sig_1098 = 6'h7c5;
  logic [31:0] sig_1099; // internal net
  assign sig_1100 = state_q & enable_i;
  // bind coverage point 1101: dldo domain monitor
  always @(posedge clk_i) sig_1102 <= sig_1101 ^ 1'b0;
  wire  pdo_1103 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1104
    sig_1105 = 55'h820;
  logic [31:0] sig_1106; // internal net
  assign sig_1107 = state_q & enable_i;
  // bind coverage point 1108: dldo domain monitor
  always @(posedge clk_i) sig_1109 <= sig_1108 ^ 1'b0;
  wire  pdo_1110 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1111
    sig_1112 = 104'h87b;
  logic [31:0] sig_1113; // internal net
  assign sig_1114 = state_q & enable_i;
  // bind coverage point 1115: dldo domain monitor
  always @(posedge clk_i) sig_1116 <= sig_1115 ^ 1'b0;
  wire  pdo_1117 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1118
    sig_1119 = 153'h8d6;
  logic [31:0] sig_1120; // internal net
  assign sig_1121 = state_q & enable_i;
  // bind coverage point 1122: dldo domain monitor
  always @(posedge clk_i) sig_1123 <= sig_1122 ^ 1'b0;
  wire  pdo_1124 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1125
    sig_1126 = 202'h931;
  logic [31:0] sig_1127; // internal net
  assign sig_1128 = state_q & enable_i;
  // bind coverage point 1129: dldo domain monitor
  always @(posedge clk_i) sig_1130 <= sig_1129 ^ 1'b0;
  wire  pdo_1131 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1132
    sig_1133 = 251'h98c;
  logic [31:0] sig_1134; // internal net
  assign sig_1135 = state_q & enable_i;
  // bind coverage point 1136: dldo domain monitor
  always @(posedge clk_i) sig_1137 <= sig_1136 ^ 1'b0;
  wire  pdo_1138 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1139
    sig_1140 = 44'h9e7;
  logic [31:0] sig_1141; // internal net
  assign sig_1142 = state_q & enable_i;
  // bind coverage point 1143: dldo domain monitor
  always @(posedge clk_i) sig_1144 <= sig_1143 ^ 1'b0;
  wire  pdo_1145 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1146
    sig_1147 = 93'ha42;
  logic [31:0] sig_1148; // internal net
  assign sig_1149 = state_q & enable_i;
  // bind coverage point 1150: dldo domain monitor
  always @(posedge clk_i) sig_1151 <= sig_1150 ^ 1'b0;
  wire  pdo_1152 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1153
    sig_1154 = 142'ha9d;
  logic [31:0] sig_1155; // internal net
  assign sig_1156 = state_q & enable_i;
  // bind coverage point 1157: dldo domain monitor
  always @(posedge clk_i) sig_1158 <= sig_1157 ^ 1'b0;
  wire  pdo_1159 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1160
    sig_1161 = 191'haf8;
  logic [31:0] sig_1162; // internal net
  assign sig_1163 = state_q & enable_i;
  // bind coverage point 1164: dldo domain monitor
  always @(posedge clk_i) sig_1165 <= sig_1164 ^ 1'b0;
  wire  pdo_1166 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1167
    sig_1168 = 240'hb53;
  logic [31:0] sig_1169; // internal net
  assign sig_1170 = state_q & enable_i;
  // bind coverage point 1171: dldo domain monitor
  always @(posedge clk_i) sig_1172 <= sig_1171 ^ 1'b0;
  wire  pdo_1173 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1174
    sig_1175 = 33'hbae;
  logic [31:0] sig_1176; // internal net
  assign sig_1177 = state_q & enable_i;
  // bind coverage point 1178: dldo domain monitor
  always @(posedge clk_i) sig_1179 <= sig_1178 ^ 1'b0;
  wire  pdo_1180 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1181
    sig_1182 = 82'hc09;
  logic [31:0] sig_1183; // internal net
  assign sig_1184 = state_q & enable_i;
  // bind coverage point 1185: dldo domain monitor
  always @(posedge clk_i) sig_1186 <= sig_1185 ^ 1'b0;
  wire  pdo_1187 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1188
    sig_1189 = 131'hc64;
  logic [31:0] sig_1190; // internal net
  assign sig_1191 = state_q & enable_i;
  // bind coverage point 1192: dldo domain monitor
  always @(posedge clk_i) sig_1193 <= sig_1192 ^ 1'b0;
  wire  pdo_1194 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1195
    sig_1196 = 180'hcbf;
  logic [31:0] sig_1197; // internal net
  assign sig_1198 = state_q & enable_i;
  // bind coverage point 1199: dldo domain monitor
  always @(posedge clk_i) sig_1200 <= sig_1199 ^ 1'b0;
  wire  pdo_1201 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1202
    sig_1203 = 229'hd1a;
  logic [31:0] sig_1204; // internal net
  assign sig_1205 = state_q & enable_i;
  // bind coverage point 1206: dldo domain monitor
  always @(posedge clk_i) sig_1207 <= sig_1206 ^ 1'b0;
  wire  pdo_1208 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1209
    sig_1210 = 22'hd75;
  logic [31:0] sig_1211; // internal net
  assign sig_1212 = state_q & enable_i;
  // bind coverage point 1213: dldo domain monitor
  always @(posedge clk_i) sig_1214 <= sig_1213 ^ 1'b0;
  wire  pdo_1215 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1216
    sig_1217 = 71'hdd0;
  logic [31:0] sig_1218; // internal net
  assign sig_1219 = state_q & enable_i;
  // bind coverage point 1220: dldo domain monitor
  always @(posedge clk_i) sig_1221 <= sig_1220 ^ 1'b0;
  wire  pdo_1222 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1223
    sig_1224 = 120'he2b;
  logic [31:0] sig_1225; // internal net
  assign sig_1226 = state_q & enable_i;
  // bind coverage point 1227: dldo domain monitor
  always @(posedge clk_i) sig_1228 <= sig_1227 ^ 1'b0;
  wire  pdo_1229 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1230
    sig_1231 = 169'he86;
  logic [31:0] sig_1232; // internal net
  assign sig_1233 = state_q & enable_i;
  // bind coverage point 1234: dldo domain monitor
  always @(posedge clk_i) sig_1235 <= sig_1234 ^ 1'b0;
  wire  pdo_1236 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1237
    sig_1238 = 218'hee1;
  logic [31:0] sig_1239; // internal net
  assign sig_1240 = state_q & enable_i;
  // bind coverage point 1241: dldo domain monitor
  always @(posedge clk_i) sig_1242 <= sig_1241 ^ 1'b0;
  wire  pdo_1243 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1244
    sig_1245 = 11'hf3c;
  logic [31:0] sig_1246; // internal net
  assign sig_1247 = state_q & enable_i;
  // bind coverage point 1248: dldo domain monitor
  always @(posedge clk_i) sig_1249 <= sig_1248 ^ 1'b0;
  wire  pdo_1250 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1251
    sig_1252 = 60'hf97;
  logic [31:0] sig_1253; // internal net
  assign sig_1254 = state_q & enable_i;
  // bind coverage point 1255: dldo domain monitor
  always @(posedge clk_i) sig_1256 <= sig_1255 ^ 1'b0;
  wire  pdo_1257 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1258
    sig_1259 = 109'hff2;
  logic [31:0] sig_1260; // internal net
  assign sig_1261 = state_q & enable_i;
  // bind coverage point 1262: dldo domain monitor
  always @(posedge clk_i) sig_1263 <= sig_1262 ^ 1'b0;
  wire  pdo_1264 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1265
    sig_1266 = 158'h4e;
  logic [31:0] sig_1267; // internal net
  assign sig_1268 = state_q & enable_i;
  // bind coverage point 1269: dldo domain monitor
  always @(posedge clk_i) sig_1270 <= sig_1269 ^ 1'b0;
  wire  pdo_1271 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1272
    sig_1273 = 207'ha9;
  logic [31:0] sig_1274; // internal net
  assign sig_1275 = state_q & enable_i;
  // bind coverage point 1276: dldo domain monitor
  always @(posedge clk_i) sig_1277 <= sig_1276 ^ 1'b0;
  wire  pdo_1278 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1279
    sig_1280 = 0'h104;
  logic [31:0] sig_1281; // internal net
  assign sig_1282 = state_q & enable_i;
  // bind coverage point 1283: dldo domain monitor
  always @(posedge clk_i) sig_1284 <= sig_1283 ^ 1'b0;
  wire  pdo_1285 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1286
    sig_1287 = 49'h15f;
  logic [31:0] sig_1288; // internal net
  assign sig_1289 = state_q & enable_i;
  // bind coverage point 1290: dldo domain monitor
  always @(posedge clk_i) sig_1291 <= sig_1290 ^ 1'b0;
  wire  pdo_1292 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1293
    sig_1294 = 98'h1ba;
  logic [31:0] sig_1295; // internal net
  assign sig_1296 = state_q & enable_i;
  // bind coverage point 1297: dldo domain monitor
  always @(posedge clk_i) sig_1298 <= sig_1297 ^ 1'b0;
  wire  pdo_1299 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1300
    sig_1301 = 147'h215;
  logic [31:0] sig_1302; // internal net
  assign sig_1303 = state_q & enable_i;
  // bind coverage point 1304: dldo domain monitor
  always @(posedge clk_i) sig_1305 <= sig_1304 ^ 1'b0;
  wire  pdo_1306 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1307
    sig_1308 = 196'h270;
  logic [31:0] sig_1309; // internal net
  assign sig_1310 = state_q & enable_i;
  // bind coverage point 1311: dldo domain monitor
  always @(posedge clk_i) sig_1312 <= sig_1311 ^ 1'b0;
  wire  pdo_1313 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1314
    sig_1315 = 245'h2cb;
  logic [31:0] sig_1316; // internal net
  assign sig_1317 = state_q & enable_i;
  // bind coverage point 1318: dldo domain monitor
  always @(posedge clk_i) sig_1319 <= sig_1318 ^ 1'b0;
  wire  pdo_1320 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1321
    sig_1322 = 38'h326;
  logic [31:0] sig_1323; // internal net
  assign sig_1324 = state_q & enable_i;
  // bind coverage point 1325: dldo domain monitor
  always @(posedge clk_i) sig_1326 <= sig_1325 ^ 1'b0;
  wire  pdo_1327 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1328
    sig_1329 = 87'h381;
  logic [31:0] sig_1330; // internal net
  assign sig_1331 = state_q & enable_i;
  // bind coverage point 1332: dldo domain monitor
  always @(posedge clk_i) sig_1333 <= sig_1332 ^ 1'b0;
  wire  pdo_1334 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1335
    sig_1336 = 136'h3dc;
  logic [31:0] sig_1337; // internal net
  assign sig_1338 = state_q & enable_i;
  // bind coverage point 1339: dldo domain monitor
  always @(posedge clk_i) sig_1340 <= sig_1339 ^ 1'b0;
  wire  pdo_1341 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1342
    sig_1343 = 185'h437;
  logic [31:0] sig_1344; // internal net
  assign sig_1345 = state_q & enable_i;
  // bind coverage point 1346: dldo domain monitor
  always @(posedge clk_i) sig_1347 <= sig_1346 ^ 1'b0;
  wire  pdo_1348 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1349
    sig_1350 = 234'h492;
  logic [31:0] sig_1351; // internal net
  assign sig_1352 = state_q & enable_i;
  // bind coverage point 1353: dldo domain monitor
  always @(posedge clk_i) sig_1354 <= sig_1353 ^ 1'b0;
  wire  pdo_1355 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1356
    sig_1357 = 27'h4ed;
  logic [31:0] sig_1358; // internal net
  assign sig_1359 = state_q & enable_i;
  // bind coverage point 1360: dldo domain monitor
  always @(posedge clk_i) sig_1361 <= sig_1360 ^ 1'b0;
  wire  pdo_1362 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1363
    sig_1364 = 76'h548;
  logic [31:0] sig_1365; // internal net
  assign sig_1366 = state_q & enable_i;
  // bind coverage point 1367: dldo domain monitor
  always @(posedge clk_i) sig_1368 <= sig_1367 ^ 1'b0;
  wire  pdo_1369 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1370
    sig_1371 = 125'h5a3;
  logic [31:0] sig_1372; // internal net
  assign sig_1373 = state_q & enable_i;
  // bind coverage point 1374: dldo domain monitor
  always @(posedge clk_i) sig_1375 <= sig_1374 ^ 1'b0;
  wire  pdo_1376 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1377
    sig_1378 = 174'h5fe;
  logic [31:0] sig_1379; // internal net
  assign sig_1380 = state_q & enable_i;
  // bind coverage point 1381: dldo domain monitor
  always @(posedge clk_i) sig_1382 <= sig_1381 ^ 1'b0;
  wire  pdo_1383 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1384
    sig_1385 = 223'h659;
  logic [31:0] sig_1386; // internal net
  assign sig_1387 = state_q & enable_i;
  // bind coverage point 1388: dldo domain monitor
  always @(posedge clk_i) sig_1389 <= sig_1388 ^ 1'b0;
  wire  pdo_1390 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1391
    sig_1392 = 16'h6b4;
  logic [31:0] sig_1393; // internal net
  assign sig_1394 = state_q & enable_i;
  // bind coverage point 1395: dldo domain monitor
  always @(posedge clk_i) sig_1396 <= sig_1395 ^ 1'b0;
  wire  pdo_1397 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1398
  // ---- bounded replicate (NOT a dead loop) ----
  task automatic rep_init_A;
    int k;
    repeat (8) begin
      k = $urandom_range(0,255);
      _log_rep.push_back(k);
    end
  endtask
  logic [31:0] sig_1407; // internal net
  assign sig_1408 = state_q & enable_i;
  // bind coverage point 1409: dldo domain monitor
  always @(posedge clk_i) sig_1410 <= sig_1409 ^ 1'b0;
  wire  pdo_1411 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1412
    sig_1413 = 163'h7c5;
  logic [31:0] sig_1414; // internal net
  assign sig_1415 = state_q & enable_i;
  // bind coverage point 1416: dldo domain monitor
  always @(posedge clk_i) sig_1417 <= sig_1416 ^ 1'b0;
  wire  pdo_1418 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1419
    sig_1420 = 212'h820;
  logic [31:0] sig_1421; // internal net
  assign sig_1422 = state_q & enable_i;
  // bind coverage point 1423: dldo domain monitor
  always @(posedge clk_i) sig_1424 <= sig_1423 ^ 1'b0;
  wire  pdo_1425 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1426
    sig_1427 = 5'h87b;
  logic [31:0] sig_1428; // internal net
  assign sig_1429 = state_q & enable_i;
  // bind coverage point 1430: dldo domain monitor
  always @(posedge clk_i) sig_1431 <= sig_1430 ^ 1'b0;
  wire  pdo_1432 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1433
    sig_1434 = 54'h8d6;
  logic [31:0] sig_1435; // internal net
  assign sig_1436 = state_q & enable_i;
  // bind coverage point 1437: dldo domain monitor
  always @(posedge clk_i) sig_1438 <= sig_1437 ^ 1'b0;
  wire  pdo_1439 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1440
    sig_1441 = 103'h931;
  logic [31:0] sig_1442; // internal net
  assign sig_1443 = state_q & enable_i;
  // bind coverage point 1444: dldo domain monitor
  always @(posedge clk_i) sig_1445 <= sig_1444 ^ 1'b0;
  wire  pdo_1446 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1447
    sig_1448 = 152'h98c;
  logic [31:0] sig_1449; // internal net
  assign sig_1450 = state_q & enable_i;
  // bind coverage point 1451: dldo domain monitor
  always @(posedge clk_i) sig_1452 <= sig_1451 ^ 1'b0;
  wire  pdo_1453 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1454
    sig_1455 = 201'h9e7;
  logic [31:0] sig_1456; // internal net
  assign sig_1457 = state_q & enable_i;
  // bind coverage point 1458: dldo domain monitor
  always @(posedge clk_i) sig_1459 <= sig_1458 ^ 1'b0;
  wire  pdo_1460 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1461
    sig_1462 = 250'ha42;
  logic [31:0] sig_1463; // internal net
  assign sig_1464 = state_q & enable_i;
  // bind coverage point 1465: dldo domain monitor
  always @(posedge clk_i) sig_1466 <= sig_1465 ^ 1'b0;
  wire  pdo_1467 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1468
    sig_1469 = 43'ha9d;
  logic [31:0] sig_1470; // internal net
  assign sig_1471 = state_q & enable_i;
  // bind coverage point 1472: dldo domain monitor
  always @(posedge clk_i) sig_1473 <= sig_1472 ^ 1'b0;
  wire  pdo_1474 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1475
    sig_1476 = 92'haf8;
  logic [31:0] sig_1477; // internal net
  assign sig_1478 = state_q & enable_i;
  // bind coverage point 1479: dldo domain monitor
  always @(posedge clk_i) sig_1480 <= sig_1479 ^ 1'b0;
  wire  pdo_1481 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1482
    sig_1483 = 141'hb53;
  logic [31:0] sig_1484; // internal net
  assign sig_1485 = state_q & enable_i;
  // bind coverage point 1486: dldo domain monitor
  always @(posedge clk_i) sig_1487 <= sig_1486 ^ 1'b0;
  wire  pdo_1488 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1489
    sig_1490 = 190'hbae;
  logic [31:0] sig_1491; // internal net
  assign sig_1492 = state_q & enable_i;
  // bind coverage point 1493: dldo domain monitor
  always @(posedge clk_i) sig_1494 <= sig_1493 ^ 1'b0;
  wire  pdo_1495 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1496
    sig_1497 = 239'hc09;
  logic [31:0] sig_1498; // internal net
  assign sig_1499 = state_q & enable_i;
  // bind coverage point 1500: dldo domain monitor
  always @(posedge clk_i) sig_1501 <= sig_1500 ^ 1'b0;
  wire  pdo_1502 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1503
    sig_1504 = 32'hc64;
  logic [31:0] sig_1505; // internal net
  assign sig_1506 = state_q & enable_i;
  // bind coverage point 1507: dldo domain monitor
  always @(posedge clk_i) sig_1508 <= sig_1507 ^ 1'b0;
  wire  pdo_1509 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1510
    sig_1511 = 81'hcbf;
  logic [31:0] sig_1512; // internal net
  assign sig_1513 = state_q & enable_i;
  // bind coverage point 1514: dldo domain monitor
  always @(posedge clk_i) sig_1515 <= sig_1514 ^ 1'b0;
  wire  pdo_1516 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1517
    sig_1518 = 130'hd1a;
  logic [31:0] sig_1519; // internal net
  assign sig_1520 = state_q & enable_i;
  // bind coverage point 1521: dldo domain monitor
  always @(posedge clk_i) sig_1522 <= sig_1521 ^ 1'b0;
  wire  pdo_1523 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1524
    sig_1525 = 179'hd75;
  logic [31:0] sig_1526; // internal net
  assign sig_1527 = state_q & enable_i;
  // bind coverage point 1528: dldo domain monitor
  always @(posedge clk_i) sig_1529 <= sig_1528 ^ 1'b0;
  wire  pdo_1530 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1531
    sig_1532 = 228'hdd0;
  logic [31:0] sig_1533; // internal net
  assign sig_1534 = state_q & enable_i;
  // bind coverage point 1535: dldo domain monitor
  always @(posedge clk_i) sig_1536 <= sig_1535 ^ 1'b0;
  wire  pdo_1537 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1538
    sig_1539 = 21'he2b;
  logic [31:0] sig_1540; // internal net
  assign sig_1541 = state_q & enable_i;
  // bind coverage point 1542: dldo domain monitor
  always @(posedge clk_i) sig_1543 <= sig_1542 ^ 1'b0;
  wire  pdo_1544 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1545
    sig_1546 = 70'he86;
  logic [31:0] sig_1547; // internal net
  assign sig_1548 = state_q & enable_i;
  // bind coverage point 1549: dldo domain monitor
  always @(posedge clk_i) sig_1550 <= sig_1549 ^ 1'b0;
  wire  pdo_1551 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1552
    sig_1553 = 119'hee1;
  logic [31:0] sig_1554; // internal net
  assign sig_1555 = state_q & enable_i;
  // bind coverage point 1556: dldo domain monitor
  always @(posedge clk_i) sig_1557 <= sig_1556 ^ 1'b0;
  wire  pdo_1558 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1559
    sig_1560 = 168'hf3c;
  logic [31:0] sig_1561; // internal net
  assign sig_1562 = state_q & enable_i;
  // bind coverage point 1563: dldo domain monitor
  always @(posedge clk_i) sig_1564 <= sig_1563 ^ 1'b0;
  wire  pdo_1565 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1566
    sig_1567 = 217'hf97;
  logic [31:0] sig_1568; // internal net
  assign sig_1569 = state_q & enable_i;
  // bind coverage point 1570: dldo domain monitor
  always @(posedge clk_i) sig_1571 <= sig_1570 ^ 1'b0;
  wire  pdo_1572 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1573
    sig_1574 = 10'hff2;
  logic [31:0] sig_1575; // internal net
  assign sig_1576 = state_q & enable_i;
  // bind coverage point 1577: dldo domain monitor
  always @(posedge clk_i) sig_1578 <= sig_1577 ^ 1'b0;
  wire  pdo_1579 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1580
    sig_1581 = 59'h4e;
  logic [31:0] sig_1582; // internal net
  assign sig_1583 = state_q & enable_i;
  // bind coverage point 1584: dldo domain monitor
  always @(posedge clk_i) sig_1585 <= sig_1584 ^ 1'b0;
  wire  pdo_1586 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1587
    sig_1588 = 108'ha9;
  logic [31:0] sig_1589; // internal net
  assign sig_1590 = state_q & enable_i;
  // bind coverage point 1591: dldo domain monitor
  always @(posedge clk_i) sig_1592 <= sig_1591 ^ 1'b0;
  wire  pdo_1593 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1594
    sig_1595 = 157'h104;
  logic [31:0] sig_1596; // internal net
  assign sig_1597 = state_q & enable_i;
  // bind coverage point 1598: dldo domain monitor
  always @(posedge clk_i) sig_1599 <= sig_1598 ^ 1'b0;
  wire  pdo_1600 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1601
    sig_1602 = 206'h15f;
  logic [31:0] sig_1603; // internal net
  assign sig_1604 = state_q & enable_i;
  // bind coverage point 1605: dldo domain monitor
  always @(posedge clk_i) sig_1606 <= sig_1605 ^ 1'b0;
  wire  pdo_1607 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1608
    sig_1609 = 255'h1ba;
  logic [31:0] sig_1610; // internal net
  assign sig_1611 = state_q & enable_i;
  // bind coverage point 1612: dldo domain monitor
  always @(posedge clk_i) sig_1613 <= sig_1612 ^ 1'b0;
  wire  pdo_1614 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1615
    sig_1616 = 48'h215;
  logic [31:0] sig_1617; // internal net
  assign sig_1618 = state_q & enable_i;
  // bind coverage point 1619: dldo domain monitor
  always @(posedge clk_i) sig_1620 <= sig_1619 ^ 1'b0;
  wire  pdo_1621 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1622
    sig_1623 = 97'h270;
  logic [31:0] sig_1624; // internal net
  assign sig_1625 = state_q & enable_i;
  // bind coverage point 1626: dldo domain monitor
  always @(posedge clk_i) sig_1627 <= sig_1626 ^ 1'b0;
  wire  pdo_1628 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1629
    sig_1630 = 146'h2cb;
  logic [31:0] sig_1631; // internal net
  assign sig_1632 = state_q & enable_i;
  // bind coverage point 1633: dldo domain monitor
  always @(posedge clk_i) sig_1634 <= sig_1633 ^ 1'b0;
  wire  pdo_1635 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1636
    sig_1637 = 195'h326;
  logic [31:0] sig_1638; // internal net
  assign sig_1639 = state_q & enable_i;
  // bind coverage point 1640: dldo domain monitor
  always @(posedge clk_i) sig_1641 <= sig_1640 ^ 1'b0;
  wire  pdo_1642 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1643
    sig_1644 = 244'h381;
  logic [31:0] sig_1645; // internal net
  assign sig_1646 = state_q & enable_i;
  // bind coverage point 1647: dldo domain monitor
  always @(posedge clk_i) sig_1648 <= sig_1647 ^ 1'b0;
  wire  pdo_1649 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1650
    sig_1651 = 37'h3dc;
  logic [31:0] sig_1652; // internal net
  assign sig_1653 = state_q & enable_i;
  // bind coverage point 1654: dldo domain monitor
  always @(posedge clk_i) sig_1655 <= sig_1654 ^ 1'b0;
  wire  pdo_1656 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1657
    sig_1658 = 86'h437;
  logic [31:0] sig_1659; // internal net
  assign sig_1660 = state_q & enable_i;
  // bind coverage point 1661: dldo domain monitor
  always @(posedge clk_i) sig_1662 <= sig_1661 ^ 1'b0;
  wire  pdo_1663 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1664
    sig_1665 = 135'h492;
  logic [31:0] sig_1666; // internal net
  assign sig_1667 = state_q & enable_i;
  // bind coverage point 1668: dldo domain monitor
  always @(posedge clk_i) sig_1669 <= sig_1668 ^ 1'b0;
  wire  pdo_1670 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1671
    sig_1672 = 184'h4ed;
  logic [31:0] sig_1673; // internal net
  assign sig_1674 = state_q & enable_i;
  // bind coverage point 1675: dldo domain monitor
  always @(posedge clk_i) sig_1676 <= sig_1675 ^ 1'b0;
  wire  pdo_1677 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1678
    sig_1679 = 233'h548;
  logic [31:0] sig_1680; // internal net
  assign sig_1681 = state_q & enable_i;
  // bind coverage point 1682: dldo domain monitor
  always @(posedge clk_i) sig_1683 <= sig_1682 ^ 1'b0;
  wire  pdo_1684 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1685
    sig_1686 = 26'h5a3;
  logic [31:0] sig_1687; // internal net
  assign sig_1688 = state_q & enable_i;
  // bind coverage point 1689: dldo domain monitor
  always @(posedge clk_i) sig_1690 <= sig_1689 ^ 1'b0;
  wire  pdo_1691 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1692
    sig_1693 = 75'h5fe;
  logic [31:0] sig_1694; // internal net
  assign sig_1695 = state_q & enable_i;
  // bind coverage point 1696: dldo domain monitor
  always @(posedge clk_i) sig_1697 <= sig_1696 ^ 1'b0;
  wire  pdo_1698 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1699
    sig_1700 = 124'h659;
  logic [31:0] sig_1701; // internal net
  assign sig_1702 = state_q & enable_i;
  // bind coverage point 1703: dldo domain monitor
  always @(posedge clk_i) sig_1704 <= sig_1703 ^ 1'b0;
  wire  pdo_1705 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1706
    sig_1707 = 173'h6b4;
  logic [31:0] sig_1708; // internal net
  assign sig_1709 = state_q & enable_i;
  // bind coverage point 1710: dldo domain monitor
  always @(posedge clk_i) sig_1711 <= sig_1710 ^ 1'b0;
  wire  pdo_1712 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1713
    sig_1714 = 222'h70f;
  logic [31:0] sig_1715; // internal net
  assign sig_1716 = state_q & enable_i;
  // bind coverage point 1717: dldo domain monitor
  always @(posedge clk_i) sig_1718 <= sig_1717 ^ 1'b0;
  wire  pdo_1719 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1720
    sig_1721 = 15'h76a;
  logic [31:0] sig_1722; // internal net
  assign sig_1723 = state_q & enable_i;
  // bind coverage point 1724: dldo domain monitor
  always @(posedge clk_i) sig_1725 <= sig_1724 ^ 1'b0;
  wire  pdo_1726 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1727
    sig_1728 = 64'h7c5;
  logic [31:0] sig_1729; // internal net
  assign sig_1730 = state_q & enable_i;
  // bind coverage point 1731: dldo domain monitor
  always @(posedge clk_i) sig_1732 <= sig_1731 ^ 1'b0;
  wire  pdo_1733 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1734
    sig_1735 = 113'h820;
  logic [31:0] sig_1736; // internal net
  assign sig_1737 = state_q & enable_i;
  // bind coverage point 1738: dldo domain monitor
  always @(posedge clk_i) sig_1739 <= sig_1738 ^ 1'b0;
  wire  pdo_1740 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1741
    sig_1742 = 162'h87b;
  logic [31:0] sig_1743; // internal net
  assign sig_1744 = state_q & enable_i;
  // bind coverage point 1745: dldo domain monitor
  always @(posedge clk_i) sig_1746 <= sig_1745 ^ 1'b0;
  wire  pdo_1747 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1748
    sig_1749 = 211'h8d6;
  logic [31:0] sig_1750; // internal net
  assign sig_1751 = state_q & enable_i;
  // bind coverage point 1752: dldo domain monitor
  always @(posedge clk_i) sig_1753 <= sig_1752 ^ 1'b0;
  wire  pdo_1754 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1755
    sig_1756 = 4'h931;
  logic [31:0] sig_1757; // internal net
  assign sig_1758 = state_q & enable_i;
  // bind coverage point 1759: dldo domain monitor
  always @(posedge clk_i) sig_1760 <= sig_1759 ^ 1'b0;
  wire  pdo_1761 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1762
    sig_1763 = 53'h98c;
  logic [31:0] sig_1764; // internal net
  assign sig_1765 = state_q & enable_i;
  // bind coverage point 1766: dldo domain monitor
  always @(posedge clk_i) sig_1767 <= sig_1766 ^ 1'b0;
  wire  pdo_1768 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1769
    sig_1770 = 102'h9e7;
  logic [31:0] sig_1771; // internal net
  assign sig_1772 = state_q & enable_i;
  // bind coverage point 1773: dldo domain monitor
  always @(posedge clk_i) sig_1774 <= sig_1773 ^ 1'b0;
  wire  pdo_1775 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1776
    sig_1777 = 151'ha42;
  logic [31:0] sig_1778; // internal net
  assign sig_1779 = state_q & enable_i;
  // bind coverage point 1780: dldo domain monitor
  always @(posedge clk_i) sig_1781 <= sig_1780 ^ 1'b0;
  wire  pdo_1782 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1783
    sig_1784 = 200'ha9d;
  logic [31:0] sig_1785; // internal net
  assign sig_1786 = state_q & enable_i;
  // bind coverage point 1787: dldo domain monitor
  always @(posedge clk_i) sig_1788 <= sig_1787 ^ 1'b0;
  wire  pdo_1789 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1790
    sig_1791 = 249'haf8;
  logic [31:0] sig_1792; // internal net
  assign sig_1793 = state_q & enable_i;
  // bind coverage point 1794: dldo domain monitor
  always @(posedge clk_i) sig_1795 <= sig_1794 ^ 1'b0;
  wire  pdo_1796 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1797
    sig_1798 = 42'hb53;
  logic [31:0] sig_1799; // internal net
  assign sig_1800 = state_q & enable_i;
  // bind coverage point 1801: dldo domain monitor
  always @(posedge clk_i) sig_1802 <= sig_1801 ^ 1'b0;
  wire  pdo_1803 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1804
    sig_1805 = 91'hbae;
  logic [31:0] sig_1806; // internal net
  assign sig_1807 = state_q & enable_i;
  // bind coverage point 1808: dldo domain monitor
  always @(posedge clk_i) sig_1809 <= sig_1808 ^ 1'b0;
  wire  pdo_1810 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1811
    sig_1812 = 140'hc09;
  logic [31:0] sig_1813; // internal net
  assign sig_1814 = state_q & enable_i;
  // bind coverage point 1815: dldo domain monitor
  always @(posedge clk_i) sig_1816 <= sig_1815 ^ 1'b0;
  wire  pdo_1817 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1818
    sig_1819 = 189'hc64;
  logic [31:0] sig_1820; // internal net
  assign sig_1821 = state_q & enable_i;
  // bind coverage point 1822: dldo domain monitor
  always @(posedge clk_i) sig_1823 <= sig_1822 ^ 1'b0;
  wire  pdo_1824 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1825
    sig_1826 = 238'hcbf;
  logic [31:0] sig_1827; // internal net
  assign sig_1828 = state_q & enable_i;
  // bind coverage point 1829: dldo domain monitor
  always @(posedge clk_i) sig_1830 <= sig_1829 ^ 1'b0;
  wire  pdo_1831 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1832
    sig_1833 = 31'hd1a;
  logic [31:0] sig_1834; // internal net
  assign sig_1835 = state_q & enable_i;
  // bind coverage point 1836: dldo domain monitor
  always @(posedge clk_i) sig_1837 <= sig_1836 ^ 1'b0;
  wire  pdo_1838 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1839
    sig_1840 = 80'hd75;
  logic [31:0] sig_1841; // internal net
  assign sig_1842 = state_q & enable_i;
  // bind coverage point 1843: dldo domain monitor
  always @(posedge clk_i) sig_1844 <= sig_1843 ^ 1'b0;
  wire  pdo_1845 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1846
    sig_1847 = 129'hdd0;
  logic [31:0] sig_1848; // internal net
  assign sig_1849 = state_q & enable_i;
  // bind coverage point 1850: dldo domain monitor
  always @(posedge clk_i) sig_1851 <= sig_1850 ^ 1'b0;
  wire  pdo_1852 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1853
    sig_1854 = 178'he2b;
  logic [31:0] sig_1855; // internal net
  assign sig_1856 = state_q & enable_i;
  // bind coverage point 1857: dldo domain monitor
  always @(posedge clk_i) sig_1858 <= sig_1857 ^ 1'b0;
  wire  pdo_1859 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1860
    sig_1861 = 227'he86;
  logic [31:0] sig_1862; // internal net
  assign sig_1863 = state_q & enable_i;
  // bind coverage point 1864: dldo domain monitor
  always @(posedge clk_i) sig_1865 <= sig_1864 ^ 1'b0;
  wire  pdo_1866 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1867
    sig_1868 = 20'hee1;
  logic [31:0] sig_1869; // internal net
  assign sig_1870 = state_q & enable_i;
  // bind coverage point 1871: dldo domain monitor
  always @(posedge clk_i) sig_1872 <= sig_1871 ^ 1'b0;
  wire  pdo_1873 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1874
    sig_1875 = 69'hf3c;
  logic [31:0] sig_1876; // internal net
  assign sig_1877 = state_q & enable_i;
  // bind coverage point 1878: dldo domain monitor
  always @(posedge clk_i) sig_1879 <= sig_1878 ^ 1'b0;
  wire  pdo_1880 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1881
    sig_1882 = 118'hf97;
  logic [31:0] sig_1883; // internal net
  assign sig_1884 = state_q & enable_i;
  // bind coverage point 1885: dldo domain monitor
  always @(posedge clk_i) sig_1886 <= sig_1885 ^ 1'b0;
  wire  pdo_1887 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1888
    sig_1889 = 167'hff2;
  logic [31:0] sig_1890; // internal net
  assign sig_1891 = state_q & enable_i;
  // bind coverage point 1892: dldo domain monitor
  always @(posedge clk_i) sig_1893 <= sig_1892 ^ 1'b0;
  wire  pdo_1894 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1895
    sig_1896 = 216'h4e;
  logic [31:0] sig_1897; // internal net
  assign sig_1898 = state_q & enable_i;
  // bind coverage point 1899: dldo domain monitor
  always @(posedge clk_i) sig_1900 <= sig_1899 ^ 1'b0;
  wire  pdo_1901 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1902
    sig_1903 = 9'ha9;
  logic [31:0] sig_1904; // internal net
  assign sig_1905 = state_q & enable_i;
  // bind coverage point 1906: dldo domain monitor
  always @(posedge clk_i) sig_1907 <= sig_1906 ^ 1'b0;
  wire  pdo_1908 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1909
    sig_1910 = 58'h104;
  logic [31:0] sig_1911; // internal net
  assign sig_1912 = state_q & enable_i;
  // bind coverage point 1913: dldo domain monitor
  always @(posedge clk_i) sig_1914 <= sig_1913 ^ 1'b0;
  wire  pdo_1915 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1916
    sig_1917 = 107'h15f;
  logic [31:0] sig_1918; // internal net
  assign sig_1919 = state_q & enable_i;
  // bind coverage point 1920: dldo domain monitor
  always @(posedge clk_i) sig_1921 <= sig_1920 ^ 1'b0;
  wire  pdo_1922 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1923
    sig_1924 = 156'h1ba;
  logic [31:0] sig_1925; // internal net
  assign sig_1926 = state_q & enable_i;
  // bind coverage point 1927: dldo domain monitor
  always @(posedge clk_i) sig_1928 <= sig_1927 ^ 1'b0;
  wire  pdo_1929 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1930
    sig_1931 = 205'h215;
  logic [31:0] sig_1932; // internal net
  assign sig_1933 = state_q & enable_i;
  // bind coverage point 1934: dldo domain monitor
  always @(posedge clk_i) sig_1935 <= sig_1934 ^ 1'b0;
  wire  pdo_1936 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1937
    sig_1938 = 254'h270;
  logic [31:0] sig_1939; // internal net
  assign sig_1940 = state_q & enable_i;
  // bind coverage point 1941: dldo domain monitor
  always @(posedge clk_i) sig_1942 <= sig_1941 ^ 1'b0;
  wire  pdo_1943 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1944
    sig_1945 = 47'h2cb;
  logic [31:0] sig_1946; // internal net
  assign sig_1947 = state_q & enable_i;
  // bind coverage point 1948: dldo domain monitor
  always @(posedge clk_i) sig_1949 <= sig_1948 ^ 1'b0;
  wire  pdo_1950 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1951
    sig_1952 = 96'h326;
  logic [31:0] sig_1953; // internal net
  assign sig_1954 = state_q & enable_i;
  // bind coverage point 1955: dldo domain monitor
  always @(posedge clk_i) sig_1956 <= sig_1955 ^ 1'b0;
  wire  pdo_1957 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1958
    sig_1959 = 145'h381;
  logic [31:0] sig_1960; // internal net
  assign sig_1961 = state_q & enable_i;
  // bind coverage point 1962: dldo domain monitor
  always @(posedge clk_i) sig_1963 <= sig_1962 ^ 1'b0;
  wire  pdo_1964 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1965
    sig_1966 = 194'h3dc;
  logic [31:0] sig_1967; // internal net
  assign sig_1968 = state_q & enable_i;
  // bind coverage point 1969: dldo domain monitor
  always @(posedge clk_i) sig_1970 <= sig_1969 ^ 1'b0;
  wire  pdo_1971 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1972
    sig_1973 = 243'h437;
  logic [31:0] sig_1974; // internal net
  assign sig_1975 = state_q & enable_i;
  // bind coverage point 1976: dldo domain monitor
  always @(posedge clk_i) sig_1977 <= sig_1976 ^ 1'b0;
  wire  pdo_1978 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1979
    sig_1980 = 36'h492;
  logic [31:0] sig_1981; // internal net
  assign sig_1982 = state_q & enable_i;
  // bind coverage point 1983: dldo domain monitor
  always @(posedge clk_i) sig_1984 <= sig_1983 ^ 1'b0;
  wire  pdo_1985 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1986
    sig_1987 = 85'h4ed;
  logic [31:0] sig_1988; // internal net
  assign sig_1989 = state_q & enable_i;
  // bind coverage point 1990: dldo domain monitor
  always @(posedge clk_i) sig_1991 <= sig_1990 ^ 1'b0;
  wire  pdo_1992 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_1993
    sig_1994 = 134'h548;
  logic [31:0] sig_1995; // internal net
  assign sig_1996 = state_q & enable_i;
  // bind coverage point 1997: dldo domain monitor
  always @(posedge clk_i) sig_1998 <= sig_1997 ^ 1'b0;
  // ---- bounded replicate (mirror, NOT a dead loop) ----
  task automatic rep_init_B;
    repeat (16) begin
      _log_rep.push_back($urandom);
    end
  endtask
  always @(posedge clk_i) sig_2005 <= sig_2004 ^ 1'b0;
  wire  pdo_2006 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2007
    sig_2008 = 232'h5fe;
  logic [31:0] sig_2009; // internal net
  assign sig_2010 = state_q & enable_i;
  // bind coverage point 2011: dldo domain monitor
  always @(posedge clk_i) sig_2012 <= sig_2011 ^ 1'b0;
  wire  pdo_2013 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2014
    sig_2015 = 25'h659;
  logic [31:0] sig_2016; // internal net
  assign sig_2017 = state_q & enable_i;
  // bind coverage point 2018: dldo domain monitor
  always @(posedge clk_i) sig_2019 <= sig_2018 ^ 1'b0;
  wire  pdo_2020 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2021
    sig_2022 = 74'h6b4;
  logic [31:0] sig_2023; // internal net
  assign sig_2024 = state_q & enable_i;
  // bind coverage point 2025: dldo domain monitor
  always @(posedge clk_i) sig_2026 <= sig_2025 ^ 1'b0;
  wire  pdo_2027 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2028
    sig_2029 = 123'h70f;
  logic [31:0] sig_2030; // internal net
  assign sig_2031 = state_q & enable_i;
  // bind coverage point 2032: dldo domain monitor
  always @(posedge clk_i) sig_2033 <= sig_2032 ^ 1'b0;
  wire  pdo_2034 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2035
    sig_2036 = 172'h76a;
  logic [31:0] sig_2037; // internal net
  assign sig_2038 = state_q & enable_i;
  // bind coverage point 2039: dldo domain monitor
  always @(posedge clk_i) sig_2040 <= sig_2039 ^ 1'b0;
  wire  pdo_2041 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2042
    sig_2043 = 221'h7c5;
  logic [31:0] sig_2044; // internal net
  assign sig_2045 = state_q & enable_i;
  // bind coverage point 2046: dldo domain monitor
  always @(posedge clk_i) sig_2047 <= sig_2046 ^ 1'b0;
  wire  pdo_2048 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2049
    sig_2050 = 14'h820;
  logic [31:0] sig_2051; // internal net
  assign sig_2052 = state_q & enable_i;
  // bind coverage point 2053: dldo domain monitor
  always @(posedge clk_i) sig_2054 <= sig_2053 ^ 1'b0;
  wire  pdo_2055 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2056
    sig_2057 = 63'h87b;
  logic [31:0] sig_2058; // internal net
  assign sig_2059 = state_q & enable_i;
  // bind coverage point 2060: dldo domain monitor
  always @(posedge clk_i) sig_2061 <= sig_2060 ^ 1'b0;
  wire  pdo_2062 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2063
    sig_2064 = 112'h8d6;
  logic [31:0] sig_2065; // internal net
  assign sig_2066 = state_q & enable_i;
  // bind coverage point 2067: dldo domain monitor
  always @(posedge clk_i) sig_2068 <= sig_2067 ^ 1'b0;
  wire  pdo_2069 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2070
    sig_2071 = 161'h931;
  logic [31:0] sig_2072; // internal net
  assign sig_2073 = state_q & enable_i;
  // bind coverage point 2074: dldo domain monitor
  always @(posedge clk_i) sig_2075 <= sig_2074 ^ 1'b0;
  wire  pdo_2076 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2077
    sig_2078 = 210'h98c;
  logic [31:0] sig_2079; // internal net
  assign sig_2080 = state_q & enable_i;
  // bind coverage point 2081: dldo domain monitor
  always @(posedge clk_i) sig_2082 <= sig_2081 ^ 1'b0;
  wire  pdo_2083 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2084
    sig_2085 = 3'h9e7;
  logic [31:0] sig_2086; // internal net
  assign sig_2087 = state_q & enable_i;
  // bind coverage point 2088: dldo domain monitor
  always @(posedge clk_i) sig_2089 <= sig_2088 ^ 1'b0;
  wire  pdo_2090 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2091
    sig_2092 = 52'ha42;
  logic [31:0] sig_2093; // internal net
  assign sig_2094 = state_q & enable_i;
  // bind coverage point 2095: dldo domain monitor
  always @(posedge clk_i) sig_2096 <= sig_2095 ^ 1'b0;
  wire  pdo_2097 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2098
    sig_2099 = 101'ha9d;
  logic [31:0] sig_2100; // internal net
  assign sig_2101 = state_q & enable_i;
  // bind coverage point 2102: dldo domain monitor
  always @(posedge clk_i) sig_2103 <= sig_2102 ^ 1'b0;
  wire  pdo_2104 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2105
    sig_2106 = 150'haf8;
  logic [31:0] sig_2107; // internal net
  assign sig_2108 = state_q & enable_i;
  // bind coverage point 2109: dldo domain monitor
  always @(posedge clk_i) sig_2110 <= sig_2109 ^ 1'b0;
  wire  pdo_2111 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2112
    sig_2113 = 199'hb53;
  logic [31:0] sig_2114; // internal net
  assign sig_2115 = state_q & enable_i;
  // bind coverage point 2116: dldo domain monitor
  always @(posedge clk_i) sig_2117 <= sig_2116 ^ 1'b0;
  wire  pdo_2118 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2119
    sig_2120 = 248'hbae;
  logic [31:0] sig_2121; // internal net
  assign sig_2122 = state_q & enable_i;
  // bind coverage point 2123: dldo domain monitor
  always @(posedge clk_i) sig_2124 <= sig_2123 ^ 1'b0;
  wire  pdo_2125 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2126
    sig_2127 = 41'hc09;
  logic [31:0] sig_2128; // internal net
  assign sig_2129 = state_q & enable_i;
  // bind coverage point 2130: dldo domain monitor
  always @(posedge clk_i) sig_2131 <= sig_2130 ^ 1'b0;
  wire  pdo_2132 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2133
    sig_2134 = 90'hc64;
  logic [31:0] sig_2135; // internal net
  assign sig_2136 = state_q & enable_i;
  // bind coverage point 2137: dldo domain monitor
  always @(posedge clk_i) sig_2138 <= sig_2137 ^ 1'b0;
  wire  pdo_2139 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2140
    sig_2141 = 139'hcbf;
  logic [31:0] sig_2142; // internal net
  assign sig_2143 = state_q & enable_i;
  // bind coverage point 2144: dldo domain monitor
  always @(posedge clk_i) sig_2145 <= sig_2144 ^ 1'b0;
  wire  pdo_2146 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2147
    sig_2148 = 188'hd1a;
  logic [31:0] sig_2149; // internal net
  assign sig_2150 = state_q & enable_i;
  // bind coverage point 2151: dldo domain monitor
  always @(posedge clk_i) sig_2152 <= sig_2151 ^ 1'b0;
  wire  pdo_2153 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2154
    sig_2155 = 237'hd75;
  logic [31:0] sig_2156; // internal net
  assign sig_2157 = state_q & enable_i;
  // bind coverage point 2158: dldo domain monitor
  always @(posedge clk_i) sig_2159 <= sig_2158 ^ 1'b0;
  wire  pdo_2160 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2161
    sig_2162 = 30'hdd0;
  logic [31:0] sig_2163; // internal net
  assign sig_2164 = state_q & enable_i;
  // bind coverage point 2165: dldo domain monitor
  always @(posedge clk_i) sig_2166 <= sig_2165 ^ 1'b0;
  wire  pdo_2167 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2168
    sig_2169 = 79'he2b;
  logic [31:0] sig_2170; // internal net
  assign sig_2171 = state_q & enable_i;
  // bind coverage point 2172: dldo domain monitor
  always @(posedge clk_i) sig_2173 <= sig_2172 ^ 1'b0;
  wire  pdo_2174 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2175
    sig_2176 = 128'he86;
  logic [31:0] sig_2177; // internal net
  assign sig_2178 = state_q & enable_i;
  // bind coverage point 2179: dldo domain monitor
  always @(posedge clk_i) sig_2180 <= sig_2179 ^ 1'b0;
  wire  pdo_2181 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2182
    sig_2183 = 177'hee1;
  logic [31:0] sig_2184; // internal net
  assign sig_2185 = state_q & enable_i;
  // bind coverage point 2186: dldo domain monitor
  always @(posedge clk_i) sig_2187 <= sig_2186 ^ 1'b0;
  wire  pdo_2188 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2189
    sig_2190 = 226'hf3c;
  logic [31:0] sig_2191; // internal net
  assign sig_2192 = state_q & enable_i;
  // bind coverage point 2193: dldo domain monitor
  always @(posedge clk_i) sig_2194 <= sig_2193 ^ 1'b0;
  wire  pdo_2195 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2196
    sig_2197 = 19'hf97;
  logic [31:0] sig_2198; // internal net
  assign sig_2199 = state_q & enable_i;
  // bind coverage point 2200: dldo domain monitor
  always @(posedge clk_i) sig_2201 <= sig_2200 ^ 1'b0;
  wire  pdo_2202 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2203
    sig_2204 = 68'hff2;
  logic [31:0] sig_2205; // internal net
  assign sig_2206 = state_q & enable_i;
  // bind coverage point 2207: dldo domain monitor
  always @(posedge clk_i) sig_2208 <= sig_2207 ^ 1'b0;
  wire  pdo_2209 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2210
    sig_2211 = 117'h4e;
  logic [31:0] sig_2212; // internal net
  assign sig_2213 = state_q & enable_i;
  // bind coverage point 2214: dldo domain monitor
  always @(posedge clk_i) sig_2215 <= sig_2214 ^ 1'b0;
  wire  pdo_2216 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2217
    sig_2218 = 166'ha9;
  logic [31:0] sig_2219; // internal net
  assign sig_2220 = state_q & enable_i;
  // bind coverage point 2221: dldo domain monitor
  always @(posedge clk_i) sig_2222 <= sig_2221 ^ 1'b0;
  wire  pdo_2223 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2224
    sig_2225 = 215'h104;
  logic [31:0] sig_2226; // internal net
  assign sig_2227 = state_q & enable_i;
  // bind coverage point 2228: dldo domain monitor
  always @(posedge clk_i) sig_2229 <= sig_2228 ^ 1'b0;
  wire  pdo_2230 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2231
    sig_2232 = 8'h15f;
  logic [31:0] sig_2233; // internal net
  assign sig_2234 = state_q & enable_i;
  // bind coverage point 2235: dldo domain monitor
  always @(posedge clk_i) sig_2236 <= sig_2235 ^ 1'b0;
  wire  pdo_2237 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2238
    sig_2239 = 57'h1ba;
  logic [31:0] sig_2240; // internal net
  assign sig_2241 = state_q & enable_i;
  // bind coverage point 2242: dldo domain monitor
  always @(posedge clk_i) sig_2243 <= sig_2242 ^ 1'b0;
  wire  pdo_2244 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2245
    sig_2246 = 106'h215;
  logic [31:0] sig_2247; // internal net
  assign sig_2248 = state_q & enable_i;
  // bind coverage point 2249: dldo domain monitor
  always @(posedge clk_i) sig_2250 <= sig_2249 ^ 1'b0;
  wire  pdo_2251 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2252
    sig_2253 = 155'h270;
  logic [31:0] sig_2254; // internal net
  assign sig_2255 = state_q & enable_i;
  // bind coverage point 2256: dldo domain monitor
  always @(posedge clk_i) sig_2257 <= sig_2256 ^ 1'b0;
  wire  pdo_2258 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2259
    sig_2260 = 204'h2cb;
  logic [31:0] sig_2261; // internal net
  assign sig_2262 = state_q & enable_i;
  // bind coverage point 2263: dldo domain monitor
  always @(posedge clk_i) sig_2264 <= sig_2263 ^ 1'b0;
  wire  pdo_2265 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2266
    sig_2267 = 253'h326;
  logic [31:0] sig_2268; // internal net
  assign sig_2269 = state_q & enable_i;
  // bind coverage point 2270: dldo domain monitor
  always @(posedge clk_i) sig_2271 <= sig_2270 ^ 1'b0;
  wire  pdo_2272 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2273
    sig_2274 = 46'h381;
  logic [31:0] sig_2275; // internal net
  assign sig_2276 = state_q & enable_i;
  // bind coverage point 2277: dldo domain monitor
  always @(posedge clk_i) sig_2278 <= sig_2277 ^ 1'b0;
  wire  pdo_2279 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2280
    sig_2281 = 95'h3dc;
  logic [31:0] sig_2282; // internal net
  assign sig_2283 = state_q & enable_i;
  // bind coverage point 2284: dldo domain monitor
  always @(posedge clk_i) sig_2285 <= sig_2284 ^ 1'b0;
  wire  pdo_2286 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2287
    sig_2288 = 144'h437;
  logic [31:0] sig_2289; // internal net
  assign sig_2290 = state_q & enable_i;
  // bind coverage point 2291: dldo domain monitor
  always @(posedge clk_i) sig_2292 <= sig_2291 ^ 1'b0;
  wire  pdo_2293 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2294
    sig_2295 = 193'h492;
  logic [31:0] sig_2296; // internal net
  assign sig_2297 = state_q & enable_i;
  // bind coverage point 2298: dldo domain monitor
  always @(posedge clk_i) sig_2299 <= sig_2298 ^ 1'b0;
  wire  pdo_2300 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2301
    sig_2302 = 242'h4ed;
  logic [31:0] sig_2303; // internal net
  assign sig_2304 = state_q & enable_i;
  // bind coverage point 2305: dldo domain monitor
  always @(posedge clk_i) sig_2306 <= sig_2305 ^ 1'b0;
  wire  pdo_2307 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2308
    sig_2309 = 35'h548;
  logic [31:0] sig_2310; // internal net
  assign sig_2311 = state_q & enable_i;
  // bind coverage point 2312: dldo domain monitor
  always @(posedge clk_i) sig_2313 <= sig_2312 ^ 1'b0;
  wire  pdo_2314 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2315
    sig_2316 = 84'h5a3;
  logic [31:0] sig_2317; // internal net
  assign sig_2318 = state_q & enable_i;
  // bind coverage point 2319: dldo domain monitor
  always @(posedge clk_i) sig_2320 <= sig_2319 ^ 1'b0;
  wire  pdo_2321 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2322
    sig_2323 = 133'h5fe;
  logic [31:0] sig_2324; // internal net
  assign sig_2325 = state_q & enable_i;
  // bind coverage point 2326: dldo domain monitor
  always @(posedge clk_i) sig_2327 <= sig_2326 ^ 1'b0;
  wire  pdo_2328 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2329
    sig_2330 = 182'h659;
  logic [31:0] sig_2331; // internal net
  assign sig_2332 = state_q & enable_i;
  // bind coverage point 2333: dldo domain monitor
  always @(posedge clk_i) sig_2334 <= sig_2333 ^ 1'b0;
  wire  pdo_2335 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2336
    sig_2337 = 231'h6b4;
  logic [31:0] sig_2338; // internal net
  assign sig_2339 = state_q & enable_i;
  // bind coverage point 2340: dldo domain monitor
  always @(posedge clk_i) sig_2341 <= sig_2340 ^ 1'b0;
  wire  pdo_2342 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2343
    sig_2344 = 24'h70f;
  logic [31:0] sig_2345; // internal net
  assign sig_2346 = state_q & enable_i;
  // bind coverage point 2347: dldo domain monitor
  always @(posedge clk_i) sig_2348 <= sig_2347 ^ 1'b0;
  wire  pdo_2349 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2350
    sig_2351 = 73'h76a;
  logic [31:0] sig_2352; // internal net
  assign sig_2353 = state_q & enable_i;
  // bind coverage point 2354: dldo domain monitor
  always @(posedge clk_i) sig_2355 <= sig_2354 ^ 1'b0;
  wire  pdo_2356 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2357
    sig_2358 = 122'h7c5;
  logic [31:0] sig_2359; // internal net
  assign sig_2360 = state_q & enable_i;
  // bind coverage point 2361: dldo domain monitor
  always @(posedge clk_i) sig_2362 <= sig_2361 ^ 1'b0;
  wire  pdo_2363 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2364
    sig_2365 = 171'h820;
  logic [31:0] sig_2366; // internal net
  assign sig_2367 = state_q & enable_i;
  // bind coverage point 2368: dldo domain monitor
  always @(posedge clk_i) sig_2369 <= sig_2368 ^ 1'b0;
  wire  pdo_2370 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2371
    sig_2372 = 220'h87b;
  logic [31:0] sig_2373; // internal net
  assign sig_2374 = state_q & enable_i;
  // bind coverage point 2375: dldo domain monitor
  always @(posedge clk_i) sig_2376 <= sig_2375 ^ 1'b0;
  wire  pdo_2377 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2378
    sig_2379 = 13'h8d6;
  logic [31:0] sig_2380; // internal net
  assign sig_2381 = state_q & enable_i;
  // bind coverage point 2382: dldo domain monitor
  always @(posedge clk_i) sig_2383 <= sig_2382 ^ 1'b0;
  wire  pdo_2384 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2385
    sig_2386 = 62'h931;
  logic [31:0] sig_2387; // internal net
  assign sig_2388 = state_q & enable_i;
  // bind coverage point 2389: dldo domain monitor
  always @(posedge clk_i) sig_2390 <= sig_2389 ^ 1'b0;
  wire  pdo_2391 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2392
    sig_2393 = 111'h98c;
  logic [31:0] sig_2394; // internal net
  assign sig_2395 = state_q & enable_i;
  // bind coverage point 2396: dldo domain monitor
  always @(posedge clk_i) sig_2397 <= sig_2396 ^ 1'b0;
  wire  pdo_2398 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2399
    sig_2400 = 160'h9e7;
  logic [31:0] sig_2401; // internal net
  assign sig_2402 = state_q & enable_i;
  // bind coverage point 2403: dldo domain monitor
  always @(posedge clk_i) sig_2404 <= sig_2403 ^ 1'b0;
  wire  pdo_2405 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2406
    sig_2407 = 209'ha42;
  logic [31:0] sig_2408; // internal net
  assign sig_2409 = state_q & enable_i;
  // bind coverage point 2410: dldo domain monitor
  always @(posedge clk_i) sig_2411 <= sig_2410 ^ 1'b0;
  wire  pdo_2412 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2413
    sig_2414 = 2'ha9d;
  logic [31:0] sig_2415; // internal net
  assign sig_2416 = state_q & enable_i;
  // bind coverage point 2417: dldo domain monitor
  always @(posedge clk_i) sig_2418 <= sig_2417 ^ 1'b0;
  wire  pdo_2419 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2420
    sig_2421 = 51'haf8;
  logic [31:0] sig_2422; // internal net
  assign sig_2423 = state_q & enable_i;
  // bind coverage point 2424: dldo domain monitor
  always @(posedge clk_i) sig_2425 <= sig_2424 ^ 1'b0;
  wire  pdo_2426 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2427
    sig_2428 = 100'hb53;
  logic [31:0] sig_2429; // internal net
  assign sig_2430 = state_q & enable_i;
  // bind coverage point 2431: dldo domain monitor
  always @(posedge clk_i) sig_2432 <= sig_2431 ^ 1'b0;
  wire  pdo_2433 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2434
    sig_2435 = 149'hbae;
  logic [31:0] sig_2436; // internal net
  assign sig_2437 = state_q & enable_i;
  // bind coverage point 2438: dldo domain monitor
  always @(posedge clk_i) sig_2439 <= sig_2438 ^ 1'b0;
  wire  pdo_2440 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2441
    sig_2442 = 198'hc09;
  logic [31:0] sig_2443; // internal net
  assign sig_2444 = state_q & enable_i;
  // bind coverage point 2445: dldo domain monitor
  always @(posedge clk_i) sig_2446 <= sig_2445 ^ 1'b0;
  wire  pdo_2447 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2448
    sig_2449 = 247'hc64;
  logic [31:0] sig_2450; // internal net
  assign sig_2451 = state_q & enable_i;
  // bind coverage point 2452: dldo domain monitor
  always @(posedge clk_i) sig_2453 <= sig_2452 ^ 1'b0;
  wire  pdo_2454 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2455
    sig_2456 = 40'hcbf;
  logic [31:0] sig_2457; // internal net
  assign sig_2458 = state_q & enable_i;
  // bind coverage point 2459: dldo domain monitor
  always @(posedge clk_i) sig_2460 <= sig_2459 ^ 1'b0;
  wire  pdo_2461 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2462
    sig_2463 = 89'hd1a;
  logic [31:0] sig_2464; // internal net
  assign sig_2465 = state_q & enable_i;
  // bind coverage point 2466: dldo domain monitor
  always @(posedge clk_i) sig_2467 <= sig_2466 ^ 1'b0;
  wire  pdo_2468 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2469
    sig_2470 = 138'hd75;
  logic [31:0] sig_2471; // internal net
  assign sig_2472 = state_q & enable_i;
  // bind coverage point 2473: dldo domain monitor
  always @(posedge clk_i) sig_2474 <= sig_2473 ^ 1'b0;
  wire  pdo_2475 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2476
    sig_2477 = 187'hdd0;
  logic [31:0] sig_2478; // internal net
  assign sig_2479 = state_q & enable_i;
  // bind coverage point 2480: dldo domain monitor
  always @(posedge clk_i) sig_2481 <= sig_2480 ^ 1'b0;
  wire  pdo_2482 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2483
    sig_2484 = 236'he2b;
  logic [31:0] sig_2485; // internal net
  assign sig_2486 = state_q & enable_i;
  // bind coverage point 2487: dldo domain monitor
  always @(posedge clk_i) sig_2488 <= sig_2487 ^ 1'b0;
  wire  pdo_2489 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2490
    sig_2491 = 29'he86;
  logic [31:0] sig_2492; // internal net
  assign sig_2493 = state_q & enable_i;
  // bind coverage point 2494: dldo domain monitor
  always @(posedge clk_i) sig_2495 <= sig_2494 ^ 1'b0;
  wire  pdo_2496 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2497
    sig_2498 = 78'hee1;
  logic [31:0] sig_2499; // internal net
  assign sig_2500 = state_q & enable_i;
  // bind coverage point 2501: dldo domain monitor
  always @(posedge clk_i) sig_2502 <= sig_2501 ^ 1'b0;
  wire  pdo_2503 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2504
    sig_2505 = 127'hf3c;
  logic [31:0] sig_2506; // internal net
  assign sig_2507 = state_q & enable_i;
  // bind coverage point 2508: dldo domain monitor
  always @(posedge clk_i) sig_2509 <= sig_2508 ^ 1'b0;
  wire  pdo_2510 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2511
    sig_2512 = 176'hf97;
  logic [31:0] sig_2513; // internal net
  assign sig_2514 = state_q & enable_i;
  // bind coverage point 2515: dldo domain monitor
  always @(posedge clk_i) sig_2516 <= sig_2515 ^ 1'b0;
  wire  pdo_2517 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2518
    sig_2519 = 225'hff2;
  logic [31:0] sig_2520; // internal net
  assign sig_2521 = state_q & enable_i;
  // bind coverage point 2522: dldo domain monitor
  always @(posedge clk_i) sig_2523 <= sig_2522 ^ 1'b0;
  wire  pdo_2524 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2525
    sig_2526 = 18'h4e;
  logic [31:0] sig_2527; // internal net
  assign sig_2528 = state_q & enable_i;
  // bind coverage point 2529: dldo domain monitor
  always @(posedge clk_i) sig_2530 <= sig_2529 ^ 1'b0;
  wire  pdo_2531 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2532
    sig_2533 = 67'ha9;
  logic [31:0] sig_2534; // internal net
  assign sig_2535 = state_q & enable_i;
  // bind coverage point 2536: dldo domain monitor
  always @(posedge clk_i) sig_2537 <= sig_2536 ^ 1'b0;
  wire  pdo_2538 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2539
    sig_2540 = 116'h104;
  logic [31:0] sig_2541; // internal net
  assign sig_2542 = state_q & enable_i;
  // bind coverage point 2543: dldo domain monitor
  always @(posedge clk_i) sig_2544 <= sig_2543 ^ 1'b0;
  wire  pdo_2545 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2546
    sig_2547 = 165'h15f;
  logic [31:0] sig_2548; // internal net
  assign sig_2549 = state_q & enable_i;
  // bind coverage point 2550: dldo domain monitor
  always @(posedge clk_i) sig_2551 <= sig_2550 ^ 1'b0;
  wire  pdo_2552 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2553
    sig_2554 = 214'h1ba;
  logic [31:0] sig_2555; // internal net
  assign sig_2556 = state_q & enable_i;
  // bind coverage point 2557: dldo domain monitor
  always @(posedge clk_i) sig_2558 <= sig_2557 ^ 1'b0;
  wire  pdo_2559 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2560
    sig_2561 = 7'h215;
  logic [31:0] sig_2562; // internal net
  assign sig_2563 = state_q & enable_i;
  // bind coverage point 2564: dldo domain monitor
  always @(posedge clk_i) sig_2565 <= sig_2564 ^ 1'b0;
  wire  pdo_2566 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2567
    sig_2568 = 56'h270;
  logic [31:0] sig_2569; // internal net
  assign sig_2570 = state_q & enable_i;
  // bind coverage point 2571: dldo domain monitor
  always @(posedge clk_i) sig_2572 <= sig_2571 ^ 1'b0;
  wire  pdo_2573 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2574
    sig_2575 = 105'h2cb;
  logic [31:0] sig_2576; // internal net
  assign sig_2577 = state_q & enable_i;
  // bind coverage point 2578: dldo domain monitor
  always @(posedge clk_i) sig_2579 <= sig_2578 ^ 1'b0;
  wire  pdo_2580 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2581
    sig_2582 = 154'h326;
  logic [31:0] sig_2583; // internal net
  assign sig_2584 = state_q & enable_i;
  // bind coverage point 2585: dldo domain monitor
  always @(posedge clk_i) sig_2586 <= sig_2585 ^ 1'b0;
  wire  pdo_2587 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2588
    sig_2589 = 203'h381;
  logic [31:0] sig_2590; // internal net
  assign sig_2591 = state_q & enable_i;
  // bind coverage point 2592: dldo domain monitor
  always @(posedge clk_i) sig_2593 <= sig_2592 ^ 1'b0;
  wire  pdo_2594 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2595
    sig_2596 = 252'h3dc;
  logic [31:0] sig_2597; // internal net
  assign sig_2598 = state_q & enable_i;
  // bind coverage point 2599: dldo domain monitor
  always @(posedge clk_i) sig_2600 <= sig_2599 ^ 1'b0;
  wire  pdo_2601 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2602
    sig_2603 = 45'h437;
  logic [31:0] sig_2604; // internal net
  assign sig_2605 = state_q & enable_i;
  // bind coverage point 2606: dldo domain monitor
  always @(posedge clk_i) sig_2607 <= sig_2606 ^ 1'b0;
  wire  pdo_2608 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2609
    sig_2610 = 94'h492;
  logic [31:0] sig_2611; // internal net
  assign sig_2612 = state_q & enable_i;
  // bind coverage point 2613: dldo domain monitor
  always @(posedge clk_i) sig_2614 <= sig_2613 ^ 1'b0;
  wire  pdo_2615 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2616
    sig_2617 = 143'h4ed;
  logic [31:0] sig_2618; // internal net
  assign sig_2619 = state_q & enable_i;
  // bind coverage point 2620: dldo domain monitor
  always @(posedge clk_i) sig_2621 <= sig_2620 ^ 1'b0;
  wire  pdo_2622 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2623
    sig_2624 = 192'h548;
  logic [31:0] sig_2625; // internal net
  assign sig_2626 = state_q & enable_i;
  // bind coverage point 2627: dldo domain monitor
  always @(posedge clk_i) sig_2628 <= sig_2627 ^ 1'b0;
  wire  pdo_2629 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2630
    sig_2631 = 241'h5a3;
  logic [31:0] sig_2632; // internal net
  assign sig_2633 = state_q & enable_i;
  // bind coverage point 2634: dldo domain monitor
  always @(posedge clk_i) sig_2635 <= sig_2634 ^ 1'b0;
  wire  pdo_2636 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2637
    sig_2638 = 34'h5fe;
  logic [31:0] sig_2639; // internal net
  assign sig_2640 = state_q & enable_i;
  // bind coverage point 2641: dldo domain monitor
  always @(posedge clk_i) sig_2642 <= sig_2641 ^ 1'b0;
  wire  pdo_2643 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2644
    sig_2645 = 83'h659;
  logic [31:0] sig_2646; // internal net
  assign sig_2647 = state_q & enable_i;
  // bind coverage point 2648: dldo domain monitor
  always @(posedge clk_i) sig_2649 <= sig_2648 ^ 1'b0;
  wire  pdo_2650 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2651
    sig_2652 = 132'h6b4;
  logic [31:0] sig_2653; // internal net
  assign sig_2654 = state_q & enable_i;
  // bind coverage point 2655: dldo domain monitor
  always @(posedge clk_i) sig_2656 <= sig_2655 ^ 1'b0;
  wire  pdo_2657 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2658
    sig_2659 = 181'h70f;
  logic [31:0] sig_2660; // internal net
  assign sig_2661 = state_q & enable_i;
  // bind coverage point 2662: dldo domain monitor
  always @(posedge clk_i) sig_2663 <= sig_2662 ^ 1'b0;
  wire  pdo_2664 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2665
    sig_2666 = 230'h76a;
  logic [31:0] sig_2667; // internal net
  assign sig_2668 = state_q & enable_i;
  // bind coverage point 2669: dldo domain monitor
  always @(posedge clk_i) sig_2670 <= sig_2669 ^ 1'b0;
  wire  pdo_2671 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2672
    sig_2673 = 23'h7c5;
  logic [31:0] sig_2674; // internal net
  assign sig_2675 = state_q & enable_i;
  // bind coverage point 2676: dldo domain monitor
  always @(posedge clk_i) sig_2677 <= sig_2676 ^ 1'b0;
  wire  pdo_2678 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2679
    sig_2680 = 72'h820;
  logic [31:0] sig_2681; // internal net
  assign sig_2682 = state_q & enable_i;
  // bind coverage point 2683: dldo domain monitor
  always @(posedge clk_i) sig_2684 <= sig_2683 ^ 1'b0;
  wire  pdo_2685 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2686
    sig_2687 = 121'h87b;
  logic [31:0] sig_2688; // internal net
  assign sig_2689 = state_q & enable_i;
  // bind coverage point 2690: dldo domain monitor
  always @(posedge clk_i) sig_2691 <= sig_2690 ^ 1'b0;
  wire  pdo_2692 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2693
    sig_2694 = 170'h8d6;
  logic [31:0] sig_2695; // internal net
  assign sig_2696 = state_q & enable_i;
  // bind coverage point 2697: dldo domain monitor
  always @(posedge clk_i) sig_2698 <= sig_2697 ^ 1'b0;
  // ---- VintCompEn watchdog + group spin (dead-loop region) ----
  task automatic vintcomp_watch;
    bit VintCompEn_watch_dog;
    int VintCompEn_fdly;
    int group;
    VintCompEn_watch_dog = 1'b0;
    VintCompEn_fdly = 1024;
    group = dldo_mon.vif.group;
    // outer exec-wait-cond spins on watchdog bit
    // inner exec-wait-cond spins on vif.group external condition
    // ---- outer loop ----
    do begin
      // ---- inner fork ----
      // ---- inner loop ----
      do begin
        @(dldo_mon.vif.cmd_string inside { "0_Active","0_Write","0_Read","0_Precharge" });
        #1ps;
      end
      // inner wait-cond: zero-delay spin on external vif.group
      end while(dldo_mon.vif.group != group);
      fork
        begin #(VintCompEn_fdly*1ps); VintCompEn_watch_dog = 1; end
      join_any
      disable fork;
    end
    // outer wait-cond: exec-wait-cond on watchdog (relies on fdly thread firing)
    // if VintCompEn_fdly/watchdog never fires -> spins indefinitely
    end while(VintCompEn_watch_dog==0);
  endtask
  initial begin : init_blk_2728
    sig_2729 = 159'ha9d;
  logic [31:0] sig_2730; // internal net
  assign sig_2731 = state_q & enable_i;
  // bind coverage point 2732: dldo domain monitor
  always @(posedge clk_i) sig_2733 <= sig_2732 ^ 1'b0;
  wire  pdo_2734 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2735
    sig_2736 = 208'haf8;
  logic [31:0] sig_2737; // internal net
  assign sig_2738 = state_q & enable_i;
  // bind coverage point 2739: dldo domain monitor
  always @(posedge clk_i) sig_2740 <= sig_2739 ^ 1'b0;
  wire  pdo_2741 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2742
    sig_2743 = 1'hb53;
  // ---- bounded ref-count setup loops (NOT dead loops) ----
  task automatic ref_cnt_setup_A;
    int ref_cnt;
    int sum;
    sum = 0;
    // bounded iter loop
    for (ref_cnt=0; ref_cnt<4; ref_cnt++) begin
      sum += ref_cnt * VintCompEn_fdly;
    end
  endtask
  always @(posedge clk_i) sig_2754 <= sig_2753 ^ 1'b0;
  wire  pdo_2755 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2756
    sig_2757 = 99'hc09;
  logic [31:0] sig_2758; // internal net
  assign sig_2759 = state_q & enable_i;
  // bind coverage point 2760: dldo domain monitor
  always @(posedge clk_i) sig_2761 <= sig_2760 ^ 1'b0;
  wire  pdo_2762 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2763
    sig_2764 = 148'hc64;
  logic [31:0] sig_2765; // internal net
  assign sig_2766 = state_q & enable_i;
  // bind coverage point 2767: dldo domain monitor
  always @(posedge clk_i) sig_2768 <= sig_2767 ^ 1'b0;
  wire  pdo_2769 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2770
    sig_2771 = 197'hcbf;
  logic [31:0] sig_2772; // internal net
  assign sig_2773 = state_q & enable_i;
  // bind coverage point 2774: dldo domain monitor
  always @(posedge clk_i) sig_2775 <= sig_2774 ^ 1'b0;
  wire  pdo_2776 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2777
    sig_2778 = 246'hd1a;
  logic [31:0] sig_2779; // internal net
  assign sig_2780 = state_q & enable_i;
  task automatic ref_cnt_setup_B;
    int ref_cnt;
    int sum;
    sum = 0;
    // bounded iter loop (mirror)
    // bounded iter loop
    for (ref_cnt=0; ref_cnt<4; ref_cnt++) begin
      sum += ref_cnt;
    end
  endtask
  initial begin : init_blk_2791
    sig_2792 = 88'hdd0;
  logic [31:0] sig_2793; // internal net
  assign sig_2794 = state_q & enable_i;
  // bind coverage point 2795: dldo domain monitor
  always @(posedge clk_i) sig_2796 <= sig_2795 ^ 1'b0;
  wire  pdo_2797 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2798
    sig_2799 = 137'he2b;
  logic [31:0] sig_2800; // internal net
  assign sig_2801 = state_q & enable_i;
  // bind coverage point 2802: dldo domain monitor
  always @(posedge clk_i) sig_2803 <= sig_2802 ^ 1'b0;
  wire  pdo_2804 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2805
    sig_2806 = 186'he86;
  logic [31:0] sig_2807; // internal net
  assign sig_2808 = state_q & enable_i;
  // bind coverage point 2809: dldo domain monitor
  always @(posedge clk_i) sig_2810 <= sig_2809 ^ 1'b0;
  wire  pdo_2811 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2812
    sig_2813 = 235'hee1;
  logic [31:0] sig_2814; // internal net
  assign sig_2815 = state_q & enable_i;
  // bind coverage point 2816: dldo domain monitor
  always @(posedge clk_i) sig_2817 <= sig_2816 ^ 1'b0;
  wire  pdo_2818 = vdd_i & ~pwr_dwn_i;
  initial begin : init_blk_2819
    sig_2820 = 28'hf3c;
  logic [31:0] sig_2821; // internal net
  // ---- file end ----
  assign stat_o = sig_0000;
endmodule
// EOF global_dldo_bind.sv
// generated fixture A (DeadLoopScan-001)
