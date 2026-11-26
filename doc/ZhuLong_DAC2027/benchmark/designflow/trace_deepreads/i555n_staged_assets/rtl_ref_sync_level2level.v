/* ============================================================================
 * IMPLEMENTATION design - EXPECTED FORMAL PASS
 * Identical logic to golden reference (sync_level2level_ref). Unmodified
 * original RTL => sequential rtl2rtl formal equivalence PASS.
 * Copyright 2019-2021 T-Head Semiconductor Co., Ltd. (Apache-2.0)
 * ==========================================================================*/
module sync_level2level_impl(
  clk,
  rst_b,
  sync_in,
  sync_out
);

parameter SIGNAL_WIDTH = 1;
parameter FLOP_NUM     = 3;

input          clk;
input          rst_b;
input   [SIGNAL_WIDTH-1:0]   sync_in;
output  [SIGNAL_WIDTH-1:0]   sync_out;
