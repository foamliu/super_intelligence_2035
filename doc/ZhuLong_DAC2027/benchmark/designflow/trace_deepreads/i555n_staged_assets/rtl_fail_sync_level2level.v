/* ============================================================================
 * IMPLEMENTATION design - EXPECTED FORMAL FAIL
 * One intentionally injected logic bug vs the golden reference:
 *   the final output stage is now INVERTED (~sync_ff[...]).
 *   Flop states match the reference, but sync_out is functionally inverted,
 *   so the two designs are NOT equivalent => formal FAIL.
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
