// ============================================================================
// AUTO-GENERATED FILE -- DO NOT EDIT MANUALLY
// Generator       : gen1prf_spsram.py (Plan A: self-contained spec table)
// Source template : ./sp_sram.v
// Section         : SPSRAM
// Instance label  : min
// Generated       : 2026-09-09 20:24:30
//
// Applied parameters (overridden in-place on the template):
//   NW  (Number of Words) = 512    -> ADDR_WIDTH    = 9
//   NB  (Number of Bits)  = 8      -> DATA_WIDTH    = 8
//   CM  (Column Mux)      = 4      -> CM            = 4   (SPARE_WIDTH = 1)
//   BK  (Banks)           = 2      -> BK            = 2
//   CD  (Center Decode)   = 1      -> CENTER_DECODE = 1
//   CR  (Column Redund)   = ON     -> EN_COLRED     = 1
//   CR_ADDR_WIDTH         = clog2(NB) - CD = clog2(8) - 1 = 2
//
// Derived (NOT overridden -- recomputed by the template expression):
//   DEPTH = (1 << ADDR_WIDTH) = (1 << 9) = 512
//
// CM effect on CR repair granularity:
//   CM=1  -> SPARE_WIDTH=2, 2-bit group repair (spare col 2-bit wide)
//   CM!=1 -> SPARE_WIDTH=1, 1-bit single repair (original behavior)
//
// Physical-only params (NOT in behavioral model, recorded for traceability):
//   RPB (Rows per Bank)  = 64    (check: RPB*CM*BK = 512)
//   CPS (Cols per Strip) = 16    (check: NB*CM/2   = 16)
//
// Note: TACC and all timing params retain the template defaults (TACC=4.0).
//       FS/DBC variants share identical params in the spec sheet; they differ
//       only in the instance name.
// ============================================================================
// ============================================================================
// sram_sp.sv
// Functional behavioral model for High Density One Port Register File.
// Supports both Side Decode (CENTER_DECODE=0) and Center Decode (CENTER_DECODE=1).
//
// Features:
//   - Read / Write operations (rising edge triggered)
//   - Bit-wise write enable (BWEB, active low); BWEB is don't-care during read
//   - Clock: All operations synchronous to external CLK
//   - TEST mode (Self Time Bypass): TEST=1 bypasses self-timed clock;
//       operations start at CLK posedge, terminate at CLK negedge;
//       Q outputs at negedge + tcdt; write pre-writes at posedge, confirms at negedge.
//   - Center Decode support (left/right memory split)
//   - Column Redundancy (direct-pin interface, EN_COLRED parameter):
//       CRSLE/CRSLA[clog2(DATA_WIDTH)-1:0] = left CR enable + defect IO index
//       CRSRE/CRSRA[clog2(DATA_WIDTH)-1:0] = right CR enable + defect IO index
//       CD=0: only CRSRE/CRSRA used; spare (memoryIO) at LSB side (MEM[0]); down-shift.
//       CD=1: left mem uses CRSLE/CRSLA (spare at MSB, up-shift);
//             right mem uses CRSRE/CRSRA (spare at LSB, down-shift); independent.
//       CR pins are asynchronous (no clock sync); must be stable during R/W.
//   - Behavioral timing constraint checking:
//       Manual $realtime checks (always active)
//       Optional specify block (ifdef TIMING_CHECK_SPECIFY)
//   - Task-based operation: sram_op_exec, timing_check, mem_init
//   - Debug signals as output ports (TIMING_DEBUG) for guaranteed VCS/Verdi visibility
//   - Event-driven output with configurable delays (tcd, thold; tcdt in TEST mode)
//   - Write does NOT update Q (Q only updates on read)
//   - VSS/VDD supply pins (interface only, not used functionally)
//
// Version: 13.0
// Changelog (v13.0):
//   - Pin width changes (pin-only, no internal logic effect):
//     * WT[1:0] -> WT[3:0] (Write Margin Tuning, 4-bit).
//     * RT[1:0] -> RT[4:0] (Read Margin Tuning, 5-bit).
//     * Added BYP (1-bit) bypass pin, placed next to TEST.
//     * All three pins remain functionally inert in the behavioral model
//       (analog/physical features). No buffer layer, no timing checks, no
//       hazard table entries -- pin declarations and FEATURE GUIDE only.
//     * FEATURE GUIDE updated: WT/RT width references corrected; new BYP
//       entry added (no spec reference, "pin-only, no functional logic").
//   - Testbenches (tb_sp_sram.v, tb_cr_corrupt_absorb.v) updated to match:
//     WT/RT regs widened, BYP reg added and connected by name.
//
// Changelog (v12.9):
//   - Internal CR latch logic removed (level-gated CRSxE, no internal latch):
//     * Deleted: crsle_latched, crsre_latched (enable latch registers).
//     * Deleted: crsla_latched, crsra_latched (address latch registers).
//     * CRSxE is now level-gated (=== 1'b1), NOT edge-triggered latched.
//       crsle_eff/crsre_eff use (CRSLE_buf === 1'b1) / (CRSRE_buf === 1'b1).
//     * CRSxA uses live port value for all functional paths (range check,
//       shift mapping). No frozen address — supports MBIST shift and
//       Hard Repair bit-by-bit programming.
//     * Preserved: mem/Q=X corruption on CRSxE edge transitions
//       (cr_corrupt_pending + edge detection via crsle_prev_val/crsre_prev_val).
//       Ensures deterministic output during state transition.
//     * Preserved: CRSxE/CRSxA timing checks (tcrac/tcrca/tcrec/tcrce).
//     * tcrhold_rw gate: (crsle_latched || crsre_latched) changed to
//       ((CRSLE_buf === 1'b1) || (CRSRE_buf === 1'b1)).
//     * R4/R5 hazard gate: !crsle_latched/!crsre_latched changed to
//       (CRSLE_buf !== 1'b1)/(CRSRE_buf !== 1'b1).
//     * tb 14b_zd/14b_tg1/tg2/tg3: rewritten to verify functionally (no
//       internal register inspection). 14b/14b_cd: "CRSxA change while
//       CRSxE=1 followed" (removed latch terminology).
//   - Rationale: Industry standard practice separates the redundancy control
//     domain from the storage clock domain, with no CK-edge latch on redundancy
//     signals. External shift logic + Hard Repair one-time fuse scenario
//     requires internal sync-follow (no freeze). Original latch logic
//     locked wrong values when external input was unstable, providing no
//     benefit over no-latch design.
//
// Changelog (v12.8):
//   - CRSxE address latch annotation (aligns with 2P_SRAM 2026-08-28 fix):
//     * crsla_latched/crsra_latched confirmed as write-only (no functional
//       read path). Shift mapping already uses live CRSRA/CRSLA (v12.7).
//     * Added inline comments marking them as "HW latch model only, NO
//       functional read path" — kept for hardware behavior modeling /
//       waveform observation, not used by any shift/range-check logic.
//     * Updated CR block comment (CRSxE=1 line): shift mapping uses live
//       port, not frozen latched value.
//     * Design confirmation: Q1=live address, Q2=edge-triggered latch,
//       Q3=MBIST early-enable is expected, Q4=entire CRSxE=1 period is CR
//       active. Option A: keep current logic, annotate only.
//
// Changelog (v12.7):
//   - CR effective enable + memory_operator now use live CRSxA port value
//     (MBIST shift fix, aligns with 2P_SRAM):
//     * crsle_eff/crsre_eff range check changed from crsla_latched/crsra_latched
//       (frozen at CRSxE rising edge) to CRSLA/CRSRA (live port value).
//     * memory_operator SD/CD a, a_l, a_r changed from crsxa_latched to CRSxA.
//     * Rationale: MBIST shifts CRSxA while CRSxE=1; latched value would miss
//       the new defect address. Live port allows range check + shift to follow
//       the current CRSxA value. CRSxE still gates the enable (crsle_latched/
//       crsre_latched), so CR is only active when CRSxE was latched high.
//     * tb 14b/14b_cd: "CRSxA change after latch ignored" tests reversed to
//       "CRSxA change after latch followed" (write+read with new defect addr).
//   - mem_init/initial/hazard: memoryIO initialization now width-aware:
//     * 1'bx/1'b0/1'b1 -> {SPARE_WIDTH{1'bx}}/{SPARE_WIDTH{1'b0}}/{SPARE_WIDTH{1'b1}}
//     * Ensures CM=1 (SPARE_WIDTH=2) correctly initializes both spare bits.
//     * Applies to: SD initial, SD mem_init, SD hazard, CD initial, CD mem_init,
//       CD hazard (15+ locations).
//   - colred_write_spare declaration parameterized: reg [1:0] -> reg [SPARE_WIDTH-1:0].
//     Inactive value: 2'bxx -> {SPARE_WIDTH{1'bx}} (aligns with 2P_SRAM pattern).
//
// Changelog (v12.6):
//   - CM=1 (CMUX1) 2-bit group column redundancy repair:
//     * New localparam SPARE_WIDTH = (CM==1) ? 2 : 1 controls spare column
//       width and CR shift granularity.
//     * memoryIO / memoryIO_L / memoryIO_R widened from 1-bit to [SPARE_WIDTH-1:0].
//     * 4 CR shift tasks (CRReadDownShift/CRWriteDownShift/CRReadUpShift/
//       CRWriteUpShift) generalized to operate on SPARE_WIDTH-sized groups.
//       When SPARE_WIDTH=1 (CM!=1), behavior is identical to v12.5.
//     * CRSxA still indexes individual bit (0..N-1); internally converted
//       to group index g = a / SPARE_WIDTH. CRSxA=0 and CRSxA=1 repair the
//       same group pair(0,1) when CM=1.
//     * BWEB mapping updated: defect group covers [g*gs .. g*gs+gs-1];
//       shift step = SPARE_WIDTH.
//     * CM=1 + CD requires even NB2_L/NB2_R (guaranteed by SPEC NB Increment=2);
//       runtime warning added for misconfiguration.
//     * Redundant element count unchanged: CM=1 single-group repair unit = 2 bits,
//       other configs = 1 bit (per spec: total redundant count is config-invariant).
//   - FEATURE GUIDE CM section updated: CM=1 now affects SPARE_WIDTH and CR
//     shift granularity (was "pin only, no logic").
//
// Changelog (v12.5):
//   - Completed CR shift timing parameter set (tr* family):
//     * Added trhold: Q output hold in CR shift mode (was missing; specify
//       block CR shift Q path incorrectly used thold_s instead of trhold_s).
//     * Added trcs/trch: CEB setup/hold in CR shift mode (was missing; CEB
//       behavioral checks used tcs/tch directly, specify block had no CR
//       variant). Behavioral CEB checks now use tcs_eff/tch_eff; specify
//       block has cond_CEB_normal/cond_CEB_cr dual branches.
//     * Added trcdt: TEST+CR mode CLK->Q delay (was missing; TEST+CR reused
//       trcd). Q output now has 4 paths: Q_normal(tcd), Q_cr(trcd),
//       Q_test_cr(trcdt), selected by test_mode && cr_shift_active.
//     * specify Q path: CR shift uses trhold_s (was thold_s); added TEST+CR
//       branch using trcdt_s.
//   - All new tr* params are placeholder values equal to normal equivalents;
//     will be characterized separately.
//
// Changelog (v12.4):
//   - Fixed Q output jump on TEST->Normal mode switch (2psram-reported bug):
//     * Removed Q_test_mode register and Q_test wire (1ps delay path).
//     * Q now uses single path: assign #(tcd) Q_normal = Q_r; assign Q = Q_force_x ? X : Q_normal.
//     * TEST mode negedge: Q_r <= test_read_data (no inline #(tcdt) delay);
//       the tcd delay is provided by assign #(tcd) Q_normal, same as normal mode.
//     * Root cause: dual-path design (Q_test=1ps vs Q_normal=tcd) caused Q to
//       jump when Q_test_mode toggled 1->0, because Q_test showed current Q_r
//       while Q_normal showed Q_r from tcd ago.
//     * Since tcdt==tcd (both = DM*TACC), timing is preserved: negedge+tcd.
//   - Removed Q_test_mode <= 1'b0 from posedge else-branches (SD + CD).
//   - Removed Q_test_mode <= 1'b1 from negedge adjudication (SD + CD).
//
// Changelog (v12.3):
//   - CR timing parameters completely revised:
//     * Removed: tcrae, tcrea, tcrsetup, tcrhold (CRSxE-based checks).
//     * Added: tcrac (CRSxA setup vs CLK?), tcrca (CRSxA hold vs CLK?),
//       tcrec (CRSxE setup vs CLK?), tcrce (CRSxE hold vs CLK?).
//     * All 4 checks run every CLK? (not just first after edge).
//     * Violation -> Q/MEM = X (per-cycle, non-latching).
//   - Removed: crsle_rise/fall_time, crsre_rise/fall_time,
//     tcrsetup_pending/tcrhold_pending, last_CRSLE/CRSRE_rise/fall.
//   - Added: CRSLE_change_time, CRSRE_change_time (for tcrec/tcrce).
//   - Specify block: CRSxA/CRSxE setuphold now vs CLK? (was vs CRSxE edge).
//   - tb: cr_config/cr_disable tasks use tcrac/tcrec/tcrce/tcrca.
//   - tb 14k: tcrec violation test (was tcrsetup).
//   - tb 14l: tcrce violation test (was tcrhold).
//
// Changelog (v12.2):
//   - New parameter tcrhold_rw: CR mode minimum CLK period for R/W cycles.
//     Checked every CLK posedge when CR latched (crsle_latched||crsre_latched).
//     Violation -> Q/MEM = X (same cycle, non-latching).
//   - New tb test 14m: tcrhold_rw violation (CLK period < tcrhold_rw in CR mode).
//   - 14b enhanced: CRSxE high for multiple R/W cycles to verify mapping stability.
//
// Changelog (v12.1):
//   - Column Redundancy latch restored with toggleable semantics:
//     * CRSxE? latches CRSxA (frozen until CRSxE?), mem/Q=X, cr_corrupt_pending.
//     * CRSxE=1: R/W use latched defect index. CRSxA changes ignored.
//     * CRSxE?: clears latch (mapping restored to original), mem/Q=X.
//     * Next CRSxE? re-latches new CRSxA, repeats the cycle.
//   - crsle_eff/crsre_eff now use latched enable + live CRSxA port for range check.
//   - Hazard R4/R5 + tcrae setup gated by !latched (only before latch).
//   - New tb test 14j: verify CRSxA change after latch is ignored.
//
// Changelog (v12.0):
//   - Column Redundancy reworked: removed one-time latch (v10.2), CRSxE now
//     toggleable (Q-RC1:A). Each CRSxE edge (rise or fall) triggers:
//     * mem/Q = X (combinational) + cr_corrupt_pending
//     * tcrsetup check (rise) or tcrhold check (fall) at next CLK posedge
//   - New timing parameters: tcrsetup (CRSxE? to CLK?), tcrhold (CRSxE? to CLK?).
//     Both check only first CLK posedge after edge (Q-RC7:A). Violation -> R/W=X.
//   - CRSxE=1: R/W use CR shift mapping; CRSxE=0: R/W use original mem (Q-RC10).
//   - CRSxA not latched -- read directly when CRSxE=1 (must satisfy tcrae setup).
//   - tcrae setup check no longer gated by !latched (always active when EN_COLRED).
//   - Hazard R4/R5 no longer gated by !latched (always check CRSxE/CRSxA for x/z).
//   - TEST Mode v11.1 parameters retained (ttons/ttofs/tckhtw/tckhtr/tcdt).
//
// Changelog (v11.1):
//   - TEST Mode timing parameters revised per updated spec:
//     * Removed: tckht (single TEST CLK high width), tts (TEST? to CLK?).
//     * Added: ttons (TEST? to CLK?, first CLK only), ttofs (TEST? to CLK?,
//       first CLK only), tckhtw (TEST write CLK high width, longer than tckh),
//       tckhtr (TEST read CLK high width, same as normal tckh).
//     * Kept: tcdt (TEST CLK? to Q).
//   - CLK high width check now operation-specific in TEST mode:
//     * Write (test_op_type=0): tckhtw
//     * Read  (test_op_type=1): tckhtr
//     * Deselect/corrupt: no check (Q-TM3:D)
//   - ttofs check added: TEST 1->0 falling edge to first CLK posedge.
//   - tckhtw violation -> mem = all X (Q-TM4:A); tckhtr violation -> Q = X (Q-TM5:A).
//
// Changelog (v11.0):
//   - TEST mode (Self Time Bypass) implemented per spec ?1.4.3.7 + Table 1.10:
//     * New timing parameters: tckht (TEST CLK high width), tcdt (TEST CLK? to Q),
//       tts (TEST? to CLK? min interval, first CLK only).
//     * TEST=1: operations start at posedge, terminate at negedge.
//     * Posedge: latches signals + pre-writes mem (write) + detects violation flags.
//     * Negedge: adjudicates -- write+violation->mem=all X, read+violation->Q=X,
//       read no violation->Q at negedge+tcdt, deselect+clock violation->mem=all X+Q=X.
//     * tts checked only at first CLK posedge after TEST 0->1 (Q7:A).
//     * tckhtw/tckhtr replace tckh in TEST mode (write vs read); tckl/tcyc/setup/hold retained.
//     * Hazard table (R3-R11) fully applicable in TEST mode.
//     * Column Redundancy works in TEST mode (R/W completion delayed to negedge).
//     * TEST 0->1 and 1->0 take effect immediately (Q8:A).
//     * test_op_type latched at posedge: 0=write, 1=read, 2=deselect, 3=corrupt/hazard.
//     * test_violation_pos (setup/hold/ttons/ttofs) + test_violation_clk (tcyc/tckl/tckhtw/tckhtr) flags.
//     * Placeholder values: tckhtw>tckh, tckhtr~=tckh, tcdt~=tcd, ttons/ttofs~=tcs (need characterization).
//
// Changelog (v10.4):
//   - Fixed tcrea (CRSxA hold) reference edge: was CRSxE posedge, now correctly
//     CRSxE negedge (falling edge). Per timing protocol, tcrea is measured from
//     CRSxE falling edge to CRSxA second data change.
//   - Added last_CRSLE_fall / last_CRSRE_fall tracking (negedge always blocks).
//   - Removed !crsle_latched / !crsre_latched gate from tcrea hold check:
//     the hold check must be active AFTER the latch (falling edge comes after
//     rising edge which triggers the latch).
//   - Specify block: split $setuphold into $setup(posedge) + $hold(negedge)
//     for CRSxA vs CRSxE.
//
// Changelog (v10.3):
//   - CR setup/hold timing violation now always prints WARNING (not gated
//     by TIMING_DEBUG). Behavior unchanged: Q=X + write result X.
//   - Other signals (A/D/CEB/WEB/BWEB) violation behavior unchanged
//     (hazard table, TIMING_DEBUG-gated display).
//
// Changelog (v10.2):
//   - Column Redundancy one-time latch (CRSxE rises once, then frozen):
//     * CRSxE 0->1 rising edge latches CRSxA (frozen for instance lifetime).
//     * On latch: MEM and Q immediately set to all X (combinational CR init).
//       cr_corrupt_pending flag consumed at next CLK in sram_op_exec.
//     * Left (CRSLE/CRSLA) and right (CRSRE/CRSRA) latch independently.
//     * Post-latch: crsle_eff/crsre_eff use latched address; CR operations
//       use crsla_latched/crsra_latched. Further CRSxE/CRSxA changes ignored.
//     * R4/R5 hazard checks gated by !latched (only active before latch).
//     * CRSxA setup/hold timing checks gated by !latched (pre-latch only).
//     * Latch only triggers on CRSxE === 1'b1 (not 0->x/z transition).
//
// Changelog (v10.1):
//   - Timing parameter table integrated:
//     * All 13 existing timing params renamed to match spec table
//       (Taa->tcd, Toh->thold, Tas->tas, Tah->tah, Tds->tds, Tdh->tdh,
//        Tces->tcs, Tceh->tch, Tws->tws, Twh->twh, Thpw->tckh, Tlpw->tckl,
//        Tcyc->tcyc). Twdx removed (unused, not in spec table).
//     * 4 new timing params added: tbws/tbwh (BWEB setup/hold vs CLK),
//       tcrae/tcrea (CRSxA setup/hold vs CRSxE).
//     * BWEB setup/hold manual checks + specify block entries added
//       (per-bit, gate_D gated).
//     * CRSxA setup/hold vs CRSxE manual checks + specify block entries
//       added (per-bit, EN_COLRED gated). Setup reference edge = CRSxE posedge;
//       hold reference edge = CRSxE negedge (falling edge).
//     * TIMING_DEBUG: dbg_BWEB_setup/hold_margin + dbg_BWEB_violation added.
//     * Approximate values: tbws~=tds, tbwh~=tdh, tcrae~=tas, tcrea~=tah.
//
// Changelog (v10.0):
//   - Port cleanup: removed SCLK/SDIN/RSTB/SDOUT (non-functional fuse pins),
//     SD/SLP/BIST (shutdown/sleep/BIST pins and all associated internal logic
//     -- sleep timing checks, SLP handling, sleep condition gating).
//   - CRSLA/CRSRA width changed from fixed CR_ADDR_WIDTH=7 to $clog2(DATA_WIDTH).
//     CR_ADDR_WIDTH is now a localparam derived from DATA_WIDTH (non-overridable).
//
// Changelog (v9.0):
//   - Hazard table (hazard table_0729.xlsx) implemented:
//     R3:  CLK=x/z -> mem=all x, Q=x.
//     R4:  CRSxE=x/z -> mem=all x, Q=x.
//     R5:  CRSxA=x/z (CRSxE=H) -> mem=all x, Q=x.
//     R6:  CEB=x/z -> mem=all x, Q=x (simplified from per-address).
//     R7:  WEB=x/z (CEB=L) -> mem=all x, Q=x (simplified from per-address).
//     R8:  read A=x/z -> Q=x (was Q=hold).
//     R11: write BWEB=x/z -> mem[a*][i]=x for BWEB=x bits (normal + CR paths).
//
// Changelog (v8.0):
//   - Column Redundancy reworked: replaced legacy scan-chain interface
//     with direct pins (CRSLE/CRSLA/CRSRE/CRSRA + CR_ADDR_WIDTH param).
//   - SD (CD=0) spare location moved from MSB to LSB (MEM[0]); down-shift.
//   - CD (CD=1) left/right CR now independent (can be simultaneously active).
//   - Rewrote 4 Colmun tasks -> CRReadDownShift/CRWriteDownShift/CRReadUpShift/
//     CRWriteUpShift with clean shift semantics.
//
// Changelog (v7.0):
//   - Removed fuse shift register (SCLK/SDIN/RSTB/SDOUT pins removed in v10.0),
//     TSCLK2OP constraint, and fuse-cycle hazard handling (old Redundancy Table P2/P3).
//   - Kept: normal R/W core, setup/hold & clock timing checks.
//   - Fixed: CD sram_op_exec was missing an 'end' (dangling ctrl_x_hazard wrapper removed).
// ============================================================================

`timescale 1ns/1ps

// ============================================================================
// [FEATURE GUIDE] Spec 1.4.3 Function -- Feature Toggle Map for Compiler
// ============================================================================
// This section documents how each spec 1.4.3 feature maps to RTL code and
// how the logic changes when the feature is enabled (ON) vs disabled (OFF).
// Compiler software engineers can use this to split the code by feature.
//
// Parameter / macro          | Spec 1.4.3 #   | Feature name
// ---------------------------+----------------+--------------------------------
// (always on)                | 1. Read Op     | Read Operation
// (always on)                | 2. Write Op    | Write Operation
// RA[1:0] pin                | 3. Read assist | Read Assist (RA)
// WA, WAT[1:0], WAV[1:0] pin | 4. Write assist| Write Assist (WA)
// RT[4:0] pin                | 5. Read margin | Read Margin Tuning (RT)
// WT[3:0] pin                | 6. Write margin| Write Margin Tuning (WT)
// TEST pin, tcdt/ttons/...   | 7. Self Time   | Self Time Bypass (TEST mode)
// BYP pin                    | (pin-only)     | Bypass (BYP) -- no functional logic
// BWEB[N-1:0] pin            | 8. Bit Write   | Bit Write (BWEB)
// EN_COLRED param, CRSLE/..  | 9. Col Redund  | Column Redundancy (CR)
// CENTER_DECODE param        | (compiler opt) | Center Decode (CD) vs Side Decode (SD)
// CM param                   | (compiler opt) | Column Mux (CM)
// BK param                   | (compiler opt) | Banks (BK)
//
// ----------------------------------------------------------------------------
// Feature 1: Read Operation (always on, cannot be disabled)
//   Spec: CEB=0, WEB=1 at CLK rising edge -> Q = mem[A]
//   RTL:  Read path in memory_operator task, casez 2'b10 (line ~2150)
//         Q_r <= Q_tmp with assign #(tcd) delay (line ~347)
//   OFF:  Not applicable -- core function always present.
//
// Feature 2: Write Operation (always on, cannot be disabled)
//   Spec: CEB=0, WEB=0 at CLK rising edge -> mem[A] = D
//   RTL:  Write path in memory_operator task, casez 2'b00 (line ~2062)
//   OFF:  Not applicable -- core function always present.
//
// Feature 3: Read Assist (RA) -- spec 1.4.3.3
//   Spec: RA[1:0] != 2'b00 enables lower wordline voltage for read.
//   Pin:  RA[1:0] (port, line 279)
//   RTL:  Pin declared but NOT used functionally (analog/physical feature).
//         Behavioral model: RA is a no-op; read timing/data unchanged.
//   ON (RA != 0):  Pin exists, no behavioral effect. Compiler keeps pin.
//   OFF (RA == 0): Pin may be tied to 2'b00. Compiler can remove pin.
//   Code to strip: port declaration RA[1:0] (line 279). No logic to remove.
//
// Feature 4: Write Assist (WA) -- spec 1.4.3.4
//   Spec: WA=1 enables negative BL/BLB voltage; WAT[1:0] timing, WAV[1:0] voltage.
//   Pin:  WA (line 276), WAT[1:0] (line 277), WAV[1:0] (line 278)
//   RTL:  Pins declared but NOT used functionally (analog/physical feature).
//         Behavioral model: WA/WAT/WAV are no-ops; write timing/data unchanged.
//   ON (WA=1):  Pins exist, no behavioral effect. Compiler keeps pins.
//   OFF (WA=0): Pins may be tied low. Compiler can remove pins.
//   Code to strip: port declarations WA, WAT[1:0], WAV[1:0] (lines 276-278).
//                  No logic to remove.
//
// Feature 5: Read Margin Tuning (RT) -- spec 1.4.3.5
//   Spec: RT[4:0] provides speed/robustness settings. RT=5'b00000 = slowest.
//   Pin:  RT[4:0] (port)
//   RTL:  Pin declared but NOT used functionally (analog/physical feature).
//         Behavioral model: RT is a no-op; read timing uses tcd parameter.
//   ON:  Pin exists, no behavioral effect. Compiler keeps pin.
//   OFF: Pin may be tied to 5'b00000. Compiler can remove pin.
//   Code to strip: port declaration RT[4:0]. No logic to remove.
//
// Feature 6: Write Margin Tuning (WT) -- spec 1.4.3.6
//   Spec: WT[3:0] provides speed/robustness settings. WT=4'b0000 = slowest.
//   Pin:  WT[3:0] (port)
//   RTL:  Pin declared but NOT used functionally (analog/physical feature).
//         Behavioral model: WT is a no-op; write timing uses setup/hold params.
//   ON:  Pin exists, no behavioral effect. Compiler keeps pin.
//   OFF: Pin may be tied to 4'b0000. Compiler can remove pin.
//   Code to strip: port declaration WT[3:0]. No logic to remove.
//
// Feature BYP: Bypass (BYP) -- pin-only, no spec reference
//   Spec: (no spec reference) BYP is a physical/analog bypass control pin.
//   Pin:  BYP (port, 1-bit)
//   RTL:  Pin declared but NOT used functionally (analog/physical feature).
//         Behavioral model: BYP is a no-op; no timing/data effect.
//   ON:  Pin exists, no behavioral effect. Compiler keeps pin.
//   OFF: Pin may be tied to 1'b0. Compiler can remove pin.
//   Code to strip: port declaration BYP. No logic to remove.
//
// Feature 7: Self Time Bypass (TEST mode) -- spec 1.4.3.7
//   Spec: TEST=1 bypasses self-timed clock; Q at negedge+tcdt; write at
//         posedge (pre-write), confirm at negedge.
//   Pin:  TEST (line 275)
//   Param: tcdt, ttons, ttofs, tckhtw, tckhtr (lines 260-264)
//   RTL:  TEST mode state machine (lines 409-490):
//           - test_mode wire, ttons/ttofs edge detection
//           - test_op_type, test_read_data, test_violation flags
//         TEST mode logic in memory_operator (test_read_data capture, line ~2182)
//         TEST mode negedge adjudication block (line ~2580 in gen_sd, ~2590 in gen_cd)
//         Q output: assign #(tcd) Q_normal = Q_r; assign Q = Q_force_x ? X : Q_normal
//         Timing checks: tckhtw/tckhtr in negedge always block (line ~886)
//         ttons/ttofs checks in timing_violation task (line ~1626)
//   ON  (TEST pin exists): Full TEST mode logic active. Q outputs at negedge.
//   OFF (TEST tied to 0):  test_mode=0 always. All TEST-mode blocks become
//         dead code (never execute). Compiler can remove:
//           - TEST port, TEST_buf, test_mode wire
//           - test_rise_time/fall_time, ttons/ttofs state
//           - test_op_type, test_read_data, test_violation flags
//           - Q_test_mode, Q_test path removed in v12.4 (single-path Q_normal)
//           - tcdt/ttons/ttofs/tckhtw/tckhtr parameters
//           - Negedge adjudication always blocks
//           - tckhtw/tckhtr checks in negedge clock monitor
//         Normal-mode behavior: Q at posedge + tcd only.
//
// Feature 8: Bit Write (BWEB) -- spec 1.4.3.8
//   Spec: BWEB[N-1:0] active low; BWEB[i]=0 -> write bit i; BWEB[i]=1 -> hold.
//   Pin:  BWEB[N-1:0] (line 271)
//   RTL:  BWEB used in write path of memory_operator (every `if (BWEB_eff[j] === 1'b0)`
//         branch). BWEB setup/hold timing checks (tbws/tbwh, lines 235-236, ~1060).
//         Specify block BWEB $setuphold (if TIMING_CHECK_SPECIFY).
//   ON  (BWEB pin exists): Per-bit write control active. Each bit independently
//         writable. BWEB=x/z -> mem[a][i]=x (hazard R11).
//   OFF (BWEB tied to all-0): All bits always written (full-word write). The
//         `if (BWEB_eff[j] === 1'b0)` always true. Compiler can remove:
//           - BWEB port, BWEB_buf, BWEB_eff
//           - BWEB setup/hold timing checks (tbws/tbwh)
//           - BWEB specify block entries
//           - All `else if (BWEB_eff[j] === 1'bx || ...)` hazard branches
//         Write path simplifies to: mem[A][j] = D[j] for all j.
//
// Feature 9: Column Redundancy (CR) -- spec 1.4.3.9
//   Spec: CRSLE/CRSLA (left), CRSRE/CRSRA (right) repair defective columns.
//   Pin:  CRSLE (282), CRSLA (283), CRSRE (284), CRSRA (285)
//   Param: EN_COLRED (line 208), CR_ADDR_WIDTH (lines 211-220)
//          tcrac/tcrca/tcrec/tcrce/tcrhold_rw (lines 242-246)
//   RTL:  CR edge detection + corruption (lines ~615-720):
//           - crsle_prev_val/crsre_prev_val (edge tracking for mem/Q=X corruption)
//           - cr_corrupt_pending (CRSxE edge -> mem/Q = X)
//         CR effective enables: crsle_eff/crsre_eff (lines ~1280-1286)
//         CR shift tasks: CRReadDownShift/CRWriteDownShift/CRReadUpShift/
//           CRWriteUpShift (lines ~1305-1410)
//         CR write path in memory_operator (lines ~1518-1545 SD, ~2073-2160 CD)
//         CR read path in memory_operator (lines ~1572-1588 SD, ~2158-2188 CD)
//         CR hazard R4/R5 checks (lines ~1500 SD, ~2067 CD)
//         CR timing checks in timing_violation (lines ~1647-1700)
//         Spare memory: memoryIO (SD), memoryIO_L/memoryIO_R (CD)
//   ON  (EN_COLRED=1): Full CR logic active. CRSxE=1 enables CR (level-gated,
//         no internal latch). CRSxA uses live port value. CRSxE edge triggers
//         mem/Q=X corruption. R/W use shift mapping. Defect column replaced
//         by spare. CR timing checks (tcrac/tcrca/tcrec/tcrce) enforced.
//   OFF (EN_COLRED=0): crsle_eff=crsre_eff=0 always. All CR logic gated by
//         EN_COLRED becomes dead code. Compiler can remove:
//           - CRSLE/CRSLA/CRSRE/CRSRA ports + buf gates
//           - CR_ADDR_WIDTH, tcrac/tcrca/tcrec/tcrce/tcrhold_rw params
//           - CR edge detection always blocks + cr_corrupt_pending
//           - CR shift tasks (CRRead/CRWrite*)
//           - crsle_eff/crsre_eff wires
//           - All CR branches in memory_operator (if crsre_eff / if a_l >= 0)
//           - memoryIO / memoryIO_L / memoryIO_R arrays
//           - CR hazard checks (R4/R5)
//           - CR timing checks in timing_violation
//         R/W path simplifies to direct mem access, no shift.
//
// Feature CD: Center Decode -- compiler option (Table 1.7)
//   Spec: center_decode=TRUE -> two repair elements (left/right), better
//         performance; center_decode=FALSE -> side decode, one repair element.
//   Param: CENTER_DECODE (line 207)
//   RTL:  Two generate blocks: gen_sd (CENTER_DECODE==0, line ~1449) and
//         gen_cd (CENTER_DECODE==1, line ~2008). Each contains its own
//         memory_operator, timing_violation, mem_init tasks.
//         Memory arrays: mem/memoryIO (SD) vs mem_L/mem_R/memoryIO_L/
//         memoryIO_R (CD), declared at module level (lines ~510-515).
//         NB2_L/NB2_R localparams (lines 355-356).
//         CD: left=up-shift (spare at MSB), right=down-shift (spare at LSB).
//         SD: single mem, down-shift only (spare at LSB), CRSLE/CRSLA ignored.
//   ON  (CD=1): gen_cd block compiled. mem_L/mem_R split. Both CRSLE/CRSRE
//         can be active independently. NB2_L=(DW+1)/2, NB2_R=DW/2.
//   OFF (CD=0): gen_sd block compiled. Single mem array. Only CRSRE/CRSRA
//         used. CRSLE/CRSLA pins ignored (crsle_eff gated by CENTER_DECODE==1).
//         Compiler selects one generate block at elaboration; the other is
//         not compiled. Code is already cleanly separated by generate.
//
// Feature CM: Column Mux -- compiler option (Table 1.7)
//   Spec: CM=1/2/4 (1PRF) or CM=4/8/16 (SPSRAM) changes aspect ratio.
//   Param: CM (line 205)
//   RTL:  CM affects Column Redundancy repair granularity (v12.6):
//         * CM=1: SPARE_WIDTH=2. Spare column is 2-bit wide. CR shift operates
//           on 2-bit groups: bits 0&1, 2&3, ... are bound as fixed groups.
//           CRSxA indexes individual bit; group = CRSxA / 2. Any bit in a group
//           fails -> entire group repaired by 2-bit spare. This is required by
//           layout (CM=1 means no column mux, so 2 adjacent BLs share 1 spare).
//           SPEC 1PRF Compiler Range: CM=1 -> NB Increment=2 (even NB only).
//         * CM!=1 (2/4/8/16): SPARE_WIDTH=1. Spare column is 1-bit wide. CR
//           shift operates on 1-bit granularity (original v12.5 behavior).
//           CM=4 means 1 bit maps to 4 BLs via column mux; only the single
//           defective bit is repaired, no group binding needed.
//         memoryIO arrays widened to [SPARE_WIDTH-1:0] to accommodate.
//   ON  (CM=1): 2-bit group repair active. SPARE_WIDTH=2.
//   ON  (CM!=1): 1-bit repair (default). SPARE_WIDTH=1. No behavioral change
//         from v12.5.
//   Note: CM=1 only valid for 1PRF (SPSRAM has no CM=1 option).
//
// Feature BK: Banks -- compiler option (Table 1.7)
//   Spec: BK=1 or 2 splits memory into banks for performance/power.
//   Param: BK (line 206)
//   RTL:  BK is declared but NOT used functionally in the behavioral model.
//         BK affects physical layout (bank count), not behavioral R/W.
//         The behavioral model uses DEPTH = (1 << ADDR_WIDTH) as a flat array.
//   ON:  Parameter exists, no behavioral effect.
//   OFF: Parameter set to 1 (single bank), no behavioral effect.
//   Code to strip: parameter BK declaration (line 206). No logic to remove.
//
// Feature TIMING_VALIDATION: Timing check (compile-time macro)
//   Macro: `TIMING_VALIDATION (defined via +define+TIMING_VALIDATION)
//   RTL:  `DM macro = 1 when TIMING_VALIDATION defined, else 0.
//         All timing parameters (tcd, tcs, tas, ...) = `DM * value.
//         When DM=0: all timing params = 0, all setup/hold checks become
//         no-ops (condition `> 0` fails). Specify block not compiled
//         (gated by `TIMING_CHECK_SPECIFY separately).
//         When DM=1: timing params have real values, checks active.
//   ON  (TV=1): Timing violation detection active. Violation -> Q/mem = X.
//   OFF (TV=0): All timing params = 0, checks skipped. Pure functional mode.
//
// Feature TIMING_DEBUG: Debug output ports (compile-time macro)
//   Macro: `TIMING_DEBUG
//   RTL:  When defined, adds ~20 debug output ports (dbg_*) for VCS/Verdi.
//         Violation margin signals, cumulative counters, per-signal flags.
//   ON  (TD=1): Debug ports compiled, $display messages active.
//   OFF (TD=0): Debug ports not compiled, no $display spam.
// ============================================================================

`ifdef CELL_DEFINE
`celldefine
`endif

`ifdef TIMING_VALIDATION
`define DM      1
`else
`define DM      0
`endif

module CXN4HCSPS512X8M4B2C1R1W1BW1RE1_FS #(
    parameter integer ADDR_WIDTH    = 9,
    parameter integer DATA_WIDTH    = 8,
    parameter integer DEPTH         = (1 << ADDR_WIDTH),
    parameter integer FUSE_BITS     = 20,       // reserved (dormant in v7.0; fuse shift register removed)
    parameter realtime TACC        = 4.0,       // Read access time (ns) -- maps to tcd
    parameter integer INIT_TO_X    = 1,        // 1=init to X, 0=init to 0
    // Performance booster parameters
    parameter integer CM            = 4,       // Column Mux (4/8/16)
    parameter integer BK            = 2,       // Banks (1/2/4/8)
    parameter         CENTER_DECODE = 1,       // 0=Side Decode, 1=Center Decode
    parameter integer EN_COLRED     = 1,       // 1=hardware has column redundancy, 0=none
    // CR_ADDR_WIDTH: clog2(DATA_WIDTH) - CENTER_DECODE
    // SD (CD=0): clog2(NB)       -- full array, one repair element
    // CD (CD=1): clog2(NB) - 1   -- half array per repair element, matches EDA views
    // CRSxA always indexes individual bit (0..NB-1), even when CM=1 (2-bit pair
    // repair); internal shift logic converts to group index via SPARE_WIDTH.
    // max(1, ...) guards against 0-bit wire for very small NB + CD=1.
    // In parameter list so it's visible in port declarations.
    // (Verilog-2001 has no localparam in #(), so this is a parameter; pre-computed by gen1prf_spsram.py)
    parameter integer CR_ADDR_WIDTH = 2,
    // ====================================================================
    // Timing Parameters (per timing spec table)
    // Set to 0 when DM=0 (no timing validation, via `DM = TIMING_VALIDATION)
    // Placeholder values from .ds datasheet (SSG corner); BWEB/CR timing
    // approximated from nearest equivalent signal (see comments).
    // ====================================================================
    parameter realtime tcd   = `DM * TACC,       // CLK to valid Q (data output)
    parameter realtime thold = `DM * 0.272,      // CLK to invalid data output (output hold)
    parameter realtime tcs   = `DM * 0.100,      // CEB setup before CLK
    parameter realtime tch   = `DM * 0.026,      // CEB hold after CLK
    parameter realtime tas   = `DM * 0.021,      // A setup before CLK
    parameter realtime tah   = `DM * 0.038,      // A hold after CLK
    parameter realtime tws   = `DM * 0.010,      // WEB setup before CLK
    parameter realtime twh   = `DM * 0.065,      // WEB hold after CLK
    parameter realtime tbws  = `DM * 0.010,      // BWEB setup before CLK (approx tds)
    parameter realtime tbwh  = `DM * 0.065,      // BWEB hold after CLK  (approx tdh)
    parameter realtime tds   = `DM * 0.010,      // D setup before CLK
    parameter realtime tdh   = `DM * 0.065,      // D hold after CLK
    parameter realtime tcyc  = `DM * 0.591,      // Minimum CLK cycle time
    parameter realtime tckh  = `DM * 0.109,      // Minimum CLK Pulse High
    parameter realtime tckl  = `DM * 0.072,      // Minimum CLK Pulse Low
    parameter realtime tcrac   = `DM * 0.021,   // CRSxA setup before CLK? (approx tas)
    parameter realtime tcrca   = `DM * 0.038,   // CRSxA hold after CLK? (approx tah)
    parameter realtime tcrec   = `DM * 0.021,   // CRSxE setup before CLK? (approx tas)
    parameter realtime tcrce   = `DM * 0.038,   // CRSxE hold after CLK? (approx tah)
    parameter realtime tcrhold_rw = `DM * 0.591,  // CR mode min CLK period (per R/W cycle), approx tcyc

    // ====================================================================
    // Column Redundancy Shift Timing Parameters
    // Active when cr_shift_active (crsle_eff || crsre_eff): column shift is
    // actually happening, so WEB/BWEB/A/D/Q/CEB paths may incur extra delay.
    // Placeholder values equal to normal-mode equivalents; will be
    // characterized separately for CR shift mode.
    //   trws / trwh  : WEB setup / hold vs CLK?
    //   trbws/ trbwh : BWEB setup / hold vs CLK?
    //   tras / trah  : A setup / hold vs CLK?
    //   trds / trdh  : D setup / hold vs CLK?
    //   trcs / trch  : CEB setup / hold vs CLK?  (v12.5 added)
    //   trcd         : CLK? to valid Q
    //   trhold       : Q output hold             (v12.5 added)
    //   trcdt        : TEST+CR mode CLK? to valid Q (v12.5 added; see TEST params)
    // ====================================================================
    parameter realtime trws  = `DM * 0.010,      // WEB setup before CLK (CR shift mode, approx tws)
    parameter realtime trwh  = `DM * 0.065,      // WEB hold after CLK  (CR shift mode, approx twh)
    parameter realtime trbws = `DM * 0.010,      // BWEB setup before CLK (CR shift mode, approx tbws)
    parameter realtime trbwh = `DM * 0.065,      // BWEB hold after CLK  (CR shift mode, approx tbwh)
    parameter realtime tras  = `DM * 0.021,      // A setup before CLK (CR shift mode, approx tas)
    parameter realtime trah  = `DM * 0.038,      // A hold after CLK  (CR shift mode, approx tah)
    parameter realtime trds  = `DM * 0.010,      // D setup before CLK (CR shift mode, approx tds)
    parameter realtime trdh  = `DM * 0.065,      // D hold after CLK  (CR shift mode, approx tdh)
    parameter realtime trcd  = `DM * TACC,       // CLK to valid Q (CR shift mode, approx tcd)
    parameter realtime trhold = `DM * 0.272,     // Q output hold (CR shift mode, approx thold)
    parameter realtime trcs  = `DM * 0.100,      // CEB setup before CLK (CR shift mode, approx tcs)
    parameter realtime trch  = `DM * 0.026,      // CEB hold after CLK  (CR shift mode, approx tch)

    // ====================================================================
    // TEST Mode (Self Time Bypass) Timing Parameters
    // Active when TEST=1. Reference edge for Q output becomes CLK negedge.
    // Placeholder values (approx from nearest normal-mode equivalent);
    // real values must come from characterization of TEST-capable instances.
    //
    // ttons  : TEST? to CLK? min interval (first CLK posedge after TEST rise)
    // ttofs  : TEST? to CLK? min interval (first CLK posedge after TEST fall)
    // tckhtw : TEST mode WRITE -- CLK high min width (longer than tckh)
    // tckhtr : TEST mode READ  -- CLK high min width (same as normal tckh)
    // tcdt   : TEST mode READ  -- CLK? to valid Q delay
    // trcdt  : TEST+CR mode READ -- CLK? to valid Q delay (v12.5 added; CR shift)
    // ====================================================================
    parameter realtime ttons  = `DM * 0.100,      // TEST? to CLK? min interval (approx tcs)
    parameter realtime ttofs  = `DM * 0.100,      // TEST? to CLK? min interval (approx tcs)
    parameter realtime tckhtw = `DM * 0.150,      // TEST mode write CLK high min width (longer than tckh)
    parameter realtime tckhtr = `DM * 0.109,      // TEST mode read  CLK high min width (approx tckh)
    parameter realtime tcdt   = `DM * TACC,       // TEST mode CLK? to valid Q (approx tcd)
    parameter realtime trcdt  = `DM * TACC        // TEST+CR mode CLK? to valid Q (approx tcdt, CR shift)
) (
    input  wire [ADDR_WIDTH-1:0] A,
    input  wire [DATA_WIDTH-1:0] D,
    input  wire                  CLK,        // External clock (used when TEST=1)
    input  wire                  CEB,
    input  wire                  WEB,
    input  wire [DATA_WIDTH-1:0] BWEB,       // Bit-wise write enable (active low); don't-care during read
    output [DATA_WIDTH-1:0] Q,
    input  wire [3:0]            WT,
    input  wire [4:0]            RT,
    input  wire                  TEST,       // Self Time Bypass mode enable (active high)
    input  wire                  BYP,        // Bypass (pin-only, no functional logic)
    input  wire                  WA,
    input  wire [1:0]            WAT,
    input  wire [1:0]            WAV,
    input  wire [1:0]            RA,
    input  wire                  VSS,        // Ground supply (not used functionally)
    input  wire                  VDD,        // Power supply (not used functionally)
    input  wire                  CRSLE,      // Column Redundancy left enable (CD=0: ignored)
    input  wire [CR_ADDR_WIDTH-1:0] CRSLA,   // Column Redundancy left address (defect IO index)
    input  wire                  CRSRE,      // Column Redundancy right enable
    input  wire [CR_ADDR_WIDTH-1:0] CRSRA    // Column Redundancy right address (defect IO index)
`ifdef TIMING_DEBUG
    // Debug output ports -- guaranteed visible in VCS/Verdi (not optimized away)
    // Margin convention: positive = safe, negative = violation
    ,output realtime dbg_ck_period,           // Last measured clock period
    output realtime dbg_ck_high_width,       // Last measured high pulse width
    output realtime dbg_ck_low_width,        // Last measured low pulse width
    output realtime dbg_A_setup_margin,      // min over A bits: (stable_time - tas)
    output realtime dbg_D_setup_margin,      // min over D bits: (stable_time - tds)
    output realtime dbg_CEB_setup_margin,    // (stable_time - tcs)
    output realtime dbg_WEB_setup_margin,    // (stable_time - tws)
    output realtime dbg_BWEB_setup_margin,   // min over BWEB bits: (stable_time - tbws)
    output realtime dbg_A_hold_margin,       // min over changed A bits: (since_ck_rise - tah)
    output realtime dbg_D_hold_margin,       // min over changed D bits: (since_ck_rise - tdh)
    output realtime dbg_CEB_hold_margin,     // (since_ck_rise - tch)
    output realtime dbg_WEB_hold_margin,     // (since_ck_rise - twh)
    output realtime dbg_BWEB_hold_margin,    // min over changed BWEB bits: (since_ck_rise - tbwh)
    output realtime dbg_tsclk2op_margin,     // (elapsed - TSCLK2OP)
    output reg      dbg_violation,           // Any violation this cycle
    output reg [3:0] dbg_violation_type,     // 0=none,1=ck_period,2=ck_width,4=setup_hold
    output reg      dbg_setup_violation,     // Any setup violation this cycle
    output reg      dbg_hold_violation,      // Any hold violation this cycle
    output reg      dbg_A_violation,         // A had any violation this cycle
    output reg      dbg_D_violation,         // D had any violation this cycle
    output reg      dbg_CEB_violation,       // CEB had any violation this cycle
    output reg      dbg_WEB_violation,       // WEB had any violation this cycle
    output reg      dbg_BWEB_violation,      // BWEB had any violation this cycle
    output reg      dbg_ck_violation,        // Clock had any violation this cycle
    output reg      dbg_tsclk2op_violation,  // TSCLK2OP violation this cycle
    output integer  dbg_total_violations,    // Cumulative total violations
    output integer  dbg_setup_violations,    // Cumulative setup violations
    output integer  dbg_hold_violations,     // Cumulative hold violations
    output integer  dbg_ck_violations,       // Cumulative clock violations
    output integer  dbg_tsclk2op_violations  // Cumulative TSCLK2OP violations
`endif
);

    // ========================================================================
    // CR_ADDR_WIDTH is now declared in the parameter list (above port list)
    // so it's visible in port declarations. No clog2 function needed here.
    // ========================================================================

    // ========================================================================
    // Forward declarations: CR shift timing selection + test_mode
    // cr_shift_active, test_mode, and *_eff are assigned later (after
    // crsle_eff/crsre_eff are defined, near line 1530, and after TEST_buf
    // is declared in the Buffer Layer), but declared here so VCS accepts
    // their use in the Q output block and behavioral setup/hold checks below.
    // (VCS requires declare-before-use; iverilog is more permissive.)
    // ========================================================================
    wire cr_shift_active;   // 1 = column shift actually happening (crsle_eff||crsre_eff)
    wire test_mode;         // 1 = TEST pin high (Self Time Bypass); assigned after TEST_buf
    realtime tas_eff, tah_eff, tws_eff, twh_eff, tbws_eff, tbwh_eff, tds_eff, tdh_eff;
    realtime tcs_eff, tch_eff;  // CEB setup/hold effective (CR shift variant)

    // ========================================================================
    // Q output: multi-path delay scheme (v12.5: added TEST+CR path)
    //   Normal read     : Q_r <= Q_tmp (NBA at posedge), assign #(tcd)   -> Q at posedge + tcd
    //   TEST mode read  : Q_r <= test_read_data (NBA at negedge), assign #(tcd)   -> Q at negedge + tcd
    //   CR shift read   : same Q_r, assign #(trcd)  -> Q at posedge + trcd  (when cr_shift_active)
    //   TEST+CR read    : same Q_r, assign #(trcdt) -> Q at negedge + trcdt (TEST && cr_shift_active)
    //   CRSxE edge / violation: Q_force_x=1 -> Q = X immediately (combinational)
    // ========================================================================
    reg  [DATA_WIDTH-1:0] Q_r;
    reg                   Q_force_x;     // 1 = force Q to X immediately (CRSxE edge/violation)

    initial begin
        Q_force_x  = 1'b0;
    end

    // Multi-path: tcd for normal/TEST, trcd for CR shift, trcdt for TEST+CR.
    // (cr_shift_active is forward-declared above; assigned near crsle_eff.
    //  test_mode is a wire = (TEST_buf === 1'b1). When all tr* == t* (placeholder),
    //  all paths are identical.)
    // (v12.4 fix: previously TEST mode used a 1ps Q_test path via Q_test_mode
    //  selector, which caused Q to jump when Q_test_mode toggled 1->0, because
    //  Q_test tracked current Q_r while Q_normal tracked Q_r from tcd ago.)
    // (v12.5 fix: added Q_test_cr path with trcdt for TEST+CR shift mode.
    //  Previously TEST+CR reused trcd (CR shift path), which is correct only
    //  when trcdt==trcd. When trcdt is characterized independently, TEST+CR
    //  must use trcdt, not trcd.)
    wire [DATA_WIDTH-1:0] Q_normal;
    wire [DATA_WIDTH-1:0] Q_cr;
    wire [DATA_WIDTH-1:0] Q_test_cr;
    assign #(tcd)   Q_normal = Q_r;   // Q follows Q_r with tcd delay (normal + TEST)
    assign #(trcd)  Q_cr      = Q_r;   // Q follows Q_r with trcd delay (CR shift, non-TEST)
    assign #(trcdt) Q_test_cr = Q_r;   // Q follows Q_r with trcdt delay (TEST + CR shift)
    assign Q = Q_force_x                            ? {DATA_WIDTH{1'bx}} :
               (test_mode && cr_shift_active)       ? Q_test_cr :
               cr_shift_active                      ? Q_cr :
                                                      Q_normal;

    // ========================================================================
    // Active Calculated Parameters
    // ========================================================================
    localparam integer NB2_L = CENTER_DECODE ? ((DATA_WIDTH + 1) / 2) : DATA_WIDTH;
    localparam integer NB2_R = CENTER_DECODE ? (DATA_WIDTH / 2)       : DATA_WIDTH;

    // v12.6: Spare column width -- CM=1 uses 2-bit group repair (layout req),
    //        all other CM values use 1-bit repair (original behavior).
    //        SPARE_WIDTH controls memoryIO width and CR shift granularity.
    localparam integer SPARE_WIDTH = (CM == 1) ? 2 : 1;

    // v12.6: Runtime warning for CM=1 + CD with odd NB2_L/NB2_R.
    // SPEC 1PRF Compiler Range guarantees NB Increment=2 when CM=1, so NB is
    // always even. With CD=1, NB2_L=(NB+1)/2 and NB2_R=NB/2. When NB is even,
    // NB2_R=NB/2 is even, but NB2_L=NB/2+1 may be odd (e.g. NB=8 -> NB2_L=5... wait,
    // NB=8 -> NB2_L=(8+1)/2=4, NB2_R=4). Actually (NB+1)/2 with even NB gives NB/2
    // (integer division), so both are even when NB is divisible by 4, and both
    // are NB/2 when NB%4==2 (NB2_L=NB/2+1 is odd). This warning catches that case.
    // synthesis translate_off
    initial begin
        if (CM == 1 && CENTER_DECODE == 1) begin
            if ((NB2_L % SPARE_WIDTH) != 0)
                $display("WARNING [%m]: CM=1 with CD=1 requires NB2_L divisible by SPARE_WIDTH; got NB2_L=%0d SPARE_WIDTH=%0d", NB2_L, SPARE_WIDTH);
            if ((NB2_R % SPARE_WIDTH) != 0)
                $display("WARNING [%m]: CM=1 with CD=1 requires NB2_R divisible by SPARE_WIDTH; got NB2_R=%0d SPARE_WIDTH=%0d", NB2_R, SPARE_WIDTH);
        end
        // CR_ADDR_WIDTH underflow: clog2(NB)-CD clamped to 1
        if (CR_ADDR_WIDTH <= 1 && CENTER_DECODE == 1)
            $display("WARNING [%m]: CR_ADDR_WIDTH clamped to 1 (DATA_WIDTH=%0d too small for CENTER_DECODE=1)", DATA_WIDTH);
    end
    // synthesis translate_on

    // ========================================================================
    // Buffer Layer
    // buf gates isolate x/z propagation from input ports
    // ========================================================================
    wire [ADDR_WIDTH-1:0]  A_buf;
    wire [DATA_WIDTH-1:0]  D_buf;
    wire                   CLK_buf;
    wire                   CEB_buf;
    wire                   WEB_buf;
    wire [DATA_WIDTH-1:0]  BWEB_buf;
    wire                   TEST_buf;
    wire                   CRSLE_buf;
    wire [CR_ADDR_WIDTH-1:0] CRSLA_buf;
    wire                   CRSRE_buf;
    wire [CR_ADDR_WIDTH-1:0] CRSRA_buf;

    genvar gi;
    generate
        for (gi = 0; gi < ADDR_WIDTH; gi = gi + 1) begin : gen_Aiso
            buf A_iso (A_buf[gi], A[gi]);
        end
        for (gi = 0; gi < DATA_WIDTH; gi = gi + 1) begin : gen_Diso
            buf D_iso (D_buf[gi], D[gi]);
        end
        for (gi = 0; gi < DATA_WIDTH; gi = gi + 1) begin : gen_BWEBiso
            buf BWEB_iso (BWEB_buf[gi], BWEB[gi]);
        end
    endgenerate

    buf    CLK_iso   (CLK_buf,   CLK);
    buf    CEB_iso   (CEB_buf,   CEB);
    buf    WEB_iso   (WEB_buf,   WEB);
    buf    TEST_iso  (TEST_buf,  TEST);
    buf    CRSLE_iso (CRSLE_buf, CRSLE);
    buf    CRSRE_iso (CRSRE_buf, CRSRE);
    genvar cr_gi;
    generate
        for (cr_gi = 0; cr_gi < CR_ADDR_WIDTH; cr_gi = cr_gi + 1) begin : gen_CRiso
            buf CRSLA_iso (CRSLA_buf[cr_gi], CRSLA[cr_gi]);
            buf CRSRA_iso (CRSRA_buf[cr_gi], CRSRA[cr_gi]);
        end
    endgenerate

    // ========================================================================
    // Effective Clock -- directly uses external CLK
    // In Normal mode (TEST=0): all operations synchronous to CLK posedge.
    // In TEST  mode (TEST=1): operations start at CLK posedge, terminate at
    //   CLK negedge. Q updates at negedge + tcdt.
    // ========================================================================
    wire eff_clk = CLK_buf;

    // ========================================================================
    // TEST Mode (Self Time Bypass) state
    //
    // test_mode      : current mode (TEST=1 -> TEST mode)
    // test_rise_time : time of last TEST 0->1 rising edge (for ttons check)
    // test_fall_time : time of last TEST 1->0 falling edge (for ttofs check)
    // ttons_pending  : set on TEST 0->1, consumed after first CLK posedge check
    // ttofs_pending  : set on TEST 1->0, consumed after first CLK posedge check
    // ttons_violation: latched at first CLK posedge after TEST rise if interval < ttons
    // ttofs_violation: latched at first CLK posedge after TEST fall if interval < ttofs
    // ========================================================================
    assign test_mode = (TEST_buf === 1'b1);
    realtime test_rise_time;
    realtime test_fall_time;
    reg     ttons_pending;
    reg     ttofs_pending;
    reg     ttons_violation;
    reg     ttofs_violation;

    initial begin
        test_rise_time  = 0.0;
        test_fall_time  = 0.0;
        ttons_pending   = 1'b0;
        ttofs_pending   = 1'b0;
        ttons_violation = 1'b0;
        ttofs_violation = 1'b0;
    end

    // Detect TEST edge transitions with previous-value tracking.
    // Prevents spurious X->0 negedge at time 0 (VCS buf gate init).
    reg test_prev_val;
    initial begin
        test_prev_val = 1'b0;
    end

    always @(TEST_buf) begin
        if (test_prev_val !== 1'b1 && TEST_buf === 1'b1) begin
            // 0/x -> 1: rising edge (TEST mode enter)
            test_rise_time  = $realtime;
            ttons_pending   = 1'b1;
            ttons_violation = 1'b0;
        end else if (test_prev_val === 1'b1 && TEST_buf === 1'b0) begin
            // 1 -> 0: falling edge (TEST mode exit)
            test_fall_time  = $realtime;
            ttofs_pending   = 1'b1;
            ttofs_violation = 1'b0;
            `ifdef TIMING_DEBUG
            $display("TIMING_DEBUG: %m ttofs_pending set at %t (test_mode=%b)", $realtime, test_mode);
            `endif
        end
        test_prev_val = TEST_buf;
    end

    // ========================================================================
    // TEST Mode violation flag (latched at posedge, consumed at negedge)
    //
    // Per Q13:A -- posedge detects ttons/ttofs/setup/hold violations, negedge
    // adjudicates consequences (write->mem=X, read->Q=X).
    // tckhtw/tckhtr is checked at negedge (CLK high width only known then).
    // tcyc/tckl are checked at their normal edges; if violated, the
    // clock-level corruption flag is set.
    //
    // test_read_data : data latched at posedge for read, output at negedge+tcdt
    // test_op_type   : operation latched at posedge (0=write, 1=read, 2=deselect, 3=corrupt)
    // test_hazard_x  : hazard (CLK/CEB/WEB/CRS x/z) detected at posedge
    // ========================================================================
    reg test_violation_pos;   // violation detected at posedge (ttons/ttofs + setup/hold)
    reg test_violation_clk;   // clock-level violation (tcyc/tckl/tckhtw/tckhtr)
    reg cr_rw_violation;     // CR mode R/W period violation (tcrhold_rw)
    reg [DATA_WIDTH-1:0] test_read_data;
    reg [2:0]            test_op_type;     // 0=write, 1=read, 2=deselect, 3=corrupt/hazard
    reg                  test_hazard_x;    // hazard (CLK/CEB/WEB/CRS x/z) detected at posedge

    initial begin
        test_violation_pos = 1'b0;
        test_violation_clk = 1'b0;
        cr_rw_violation    = 1'b0;
        test_read_data  = {DATA_WIDTH{1'bx}};
        test_op_type    = 3'd2;            // default deselect
        test_hazard_x   = 1'b0;
    end


    // ========================================================================
    // Condition Wires
    // ========================================================================
    wire gate_A   = ~CEB_buf;
    wire gate_D   = ~CEB_buf & ~WEB_buf;
    wire gate_WEB = ~CEB_buf;
    wire gate_CEB = 1'b1;

    // CR timing check condition (wire for specify block &&& usage)
    wire gate_CR = (EN_COLRED == 1);

    // CRSxE change time tracking (for tcrec/tcrce -- declared early for VCS)
    realtime CRSLE_change_time;
    realtime CRSRE_change_time;
    integer cr_init_i;  // loop var for CR edge mem clear (module-level, before edge blocks)
    integer tcr_i;      // loop var for CRSxA setup/hold checks (tcrac/tcrca)

    // Memory arrays (declared early for CR edge detection blocks -- VCS requirement)
    reg [DATA_WIDTH-1:0] mem        [0:DEPTH-1];  // Main memory (Side Decode)
    reg [NB2_L-1:0]      mem_L      [0:DEPTH-1];  // Left memory (Center Decode)
    reg [NB2_R-1:0]      mem_R      [0:DEPTH-1];  // Right memory (Center Decode)
    reg [SPARE_WIDTH-1:0]  memoryIO   [0:DEPTH-1]; // SD spare column (1-bit or 2-bit group)
    reg [SPARE_WIDTH-1:0]  memoryIO_L [0:DEPTH-1]; // CD left mem spare
    reg [SPARE_WIDTH-1:0]  memoryIO_R [0:DEPTH-1]; // CD right mem spare

    // ========================================================================
    // Fault Injection (stuck-at fault model)
    //   Enable: +define+FAULT_INJ
    //   Select fault via $test$plusargs at runtime:
    //     +defect_bit         -- XOR bit (DATA_WIDTH/2) of mem[0]
    //     +defect_bit_a       -- XOR bit (DATA_WIDTH/2) of mem[0]
    //     +defect_bit_b       -- XOR bit (DATA_WIDTH-1) of mem[0]
    //     +defect_bit_c       -- XOR bit (DATA_WIDTH/2) of mem[0]
    //     +defect_bit_left    -- XOR bit 0 of mem[0] (in left mem for CD mode)
    //     +defect_dual_bit    -- XOR bits (DATA_WIDTH/2) and (DATA_WIDTH-1) of mem[0]
    //   Without FAULT_INJ: sa0=all-1s, sa1=all-0s (no-op, normal reads)
    // ========================================================================
    reg [DATA_WIDTH-1:0] fi_xor_mask [0:DEPTH-1];
    reg [DATA_WIDTH-1:0] fi_and_mask [0:DEPTH-1];
    reg [DATA_WIDTH-1:0] fi_or_mask [0:DEPTH-1];
    reg                   fi_enable;
    reg [DATA_WIDTH-1:0]  fi_result;  // fault-injected mem data (per read)

    initial begin
        fi_enable = 1'b0;
`ifdef FAULT_INJ
        fi_enable = 1'b1;
`endif
        // Initialize fault masks: XOR mode zeros all masks; SA mode sets no-op patterns
        if (fi_enable) begin
            for (cr_init_i = 0; cr_init_i < DEPTH; cr_init_i = cr_init_i + 1)
                fi_xor_mask[cr_init_i] = {DATA_WIDTH{1'b0}};
        end else begin
            for (cr_init_i = 0; cr_init_i < DEPTH; cr_init_i = cr_init_i + 1) begin
                fi_and_mask[cr_init_i] = {DATA_WIDTH{1'b1}};
                fi_or_mask[cr_init_i]  = {DATA_WIDTH{1'b0}};
            end
        end
        // Apply defect pattern to address 0 (XOR mode only)
        // NOTE: $test$plusargs does prefix matching, so "defect_bit" matches
        // "defect_bit_a/b/c" too. Order: most-specific first, generic last.
        if (fi_enable) begin
            if ($test$plusargs("defect_dual_bit"))
                fi_xor_mask[0] = (1'b1 << (DATA_WIDTH-1)) | (1'b1 << (DATA_WIDTH/2));
            else if ($test$plusargs("defect_bit_left")) begin
                fi_xor_mask[0] = (1'b1 << (DATA_WIDTH/2));  // right mem defect (for 18a/18b/18c)
                fi_xor_mask[1] = (1'b1 << 0);               // left mem defect (for 18d)
            end
            else if ($test$plusargs("defect_bit_c"))
                fi_xor_mask[0] = (1'b1 << (DATA_WIDTH/2));
            else if ($test$plusargs("defect_bit_b"))
                fi_xor_mask[0] = (1'b1 << (DATA_WIDTH-1));
            else if ($test$plusargs("defect_bit_a"))
                fi_xor_mask[0] = (1'b1 << (DATA_WIDTH/2));
            else if ($test$plusargs("defect_bit"))
                fi_xor_mask[0] = (1'b1 << (DATA_WIDTH/2));
        end
    end

    // ========================================================================
    // Column Redundancy (v12.9: level-gated CRSxE, no internal latch)
    //
    // CRSxE is used as a live level gate (no edge-triggered latch):
    //   CRSxE=1: CR active. Shift mapping uses LIVE CRSxA (port) for range check
    //            and defect index. CRSxA changes while CRSxE=1 are followed
    //            (supports MBIST shift and Hard Repair bit-by-bit programming).
    //   CRSxE=0: CR inactive. No shift mapping.
    //   CRSxE edge (rise/fall): mem/Q = X immediately (corruption), cr_corrupt_pending.
    //            This corruption is preserved for deterministic output during
    //            state transition (aligns with Hard Repair one-time fuse scenario).
    //
    // No internal latch registers (crsle_latched/crsre_latched/crsla_latched/
    // crsra_latched removed in v12.9). Aligns with industry standard practice:
    // redundancy domain separated from storage clock domain, no CK-edge latch.
    //
    // CR timing checks (vs CLK?, every cycle):
    //   tcrac: CRSxA setup before CLK?
    //   tcrca: CRSxA hold after CLK?
    //   tcrec: CRSxE setup before CLK?
    //   tcrce: CRSxE hold after CLK?
    //   tcrhold_rw: CR mode min CLK period for R/W (gated by CRSxE=1)
    //
    // Left (CRSLE/CRSLA) and right (CRSRE/CRSRA) operate independently.
    // ========================================================================
    reg                      cr_corrupt_pending;  // set by CRSxE edge, consumed at next CLK
    // v12.9: Internal latch registers removed (crsle_latched/crsre_latched/
    // crsla_latched/crsra_latched). CRSxE is now level-gated (=== 1'b1),
    // CRSxA uses live port value. No edge-triggered freeze.
    // Edge detection (crsle_prev_val/crsre_prev_val) retained only for
    // mem/Q=X corruption on CRSxE transitions.

    // CR timing violation flags (per-cycle, set in timing_check task)
    reg tcrac_v_l, tcrac_v_r;   // CRSxA setup violation
    reg tcrca_v_l, tcrca_v_r;   // CRSxA hold violation
    reg tcrec_v_l, tcrec_v_r;   // CRSxE setup violation
    reg tcrce_v_l, tcrce_v_r;   // CRSxE hold violation

    initial begin
        cr_corrupt_pending   = 1'b0;
        tcrac_v_l = 1'b0; tcrac_v_r = 1'b0;
        tcrca_v_l = 1'b0; tcrca_v_r = 1'b0;
        tcrec_v_l = 1'b0; tcrec_v_r = 1'b0;
        tcrce_v_l = 1'b0; tcrce_v_r = 1'b0;
    end

    // CRSxE edge detection with previous-value tracking.
    // Prevents spurious X->0 negedge at time 0 (VCS buf gate init).
    reg crsle_prev_val, crsre_prev_val;
    initial begin
        crsle_prev_val = 1'b0;
        crsre_prev_val = 1'b0;
    end

    // CRSLE edge detection: preserve mem/Q=X corruption, NO latch assignment.
    // CRSxE is level-gated (no internal latch); edge detection only triggers
    // mem/Q=X corruption to ensure deterministic output during state transition.
    // Shift mapping uses live CRSLE/CRSLA port values (see crsle_eff above).
    // CRSxE edge -> mem/Q = X immediately (no CLK wait)
    always @(CRSLE_buf) begin
        if (EN_COLRED) begin
            CRSLE_change_time = $realtime;  // track for tcrec/tcrce
            if (crsle_prev_val !== 1'b1 && CRSLE_buf === 1'b1) begin
                // 0/x -> 1: rising edge -- mem/Q=X corruption (preserve), no latch
                // Read CRSLA (port) directly, not CRSLA_buf: buf gate adds a
                // delta-cycle delay. When CRSLE and CRSLA change simultaneously,
                // CRSLE_buf triggers this block at T+delta, but CRSLA_buf may
                // not have updated yet (race in same delta cycle). CRSLA port
                // has already settled at T, so it gives the correct value.
                cr_corrupt_pending  = 1'b1;
                Q_r = {DATA_WIDTH{1'bx}};
                Q_force_x = 1'b1;  // force Q to X immediately (bypass tcd)
                for (cr_init_i = 0; cr_init_i < DEPTH; cr_init_i = cr_init_i + 1) begin
                    if (CENTER_DECODE) begin
                        mem_L[cr_init_i] = {NB2_L{1'bx}};
                        mem_R[cr_init_i] = {NB2_R{1'bx}};
                        memoryIO_L[cr_init_i] = {SPARE_WIDTH{1'bx}};
                        memoryIO_R[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end else begin
                        mem[cr_init_i] = {DATA_WIDTH{1'bx}};
                        memoryIO[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end
                end
            end else if (crsle_prev_val === 1'b1 && CRSLE_buf === 1'b0) begin
                // 1 -> 0: falling edge -- mem/Q=X corruption (preserve), no latch clear
                cr_corrupt_pending  = 1'b1;
                Q_r = {DATA_WIDTH{1'bx}};
                Q_force_x = 1'b1;  // force Q to X immediately (bypass tcd)
                for (cr_init_i = 0; cr_init_i < DEPTH; cr_init_i = cr_init_i + 1) begin
                    if (CENTER_DECODE) begin
                        mem_L[cr_init_i] = {NB2_L{1'bx}};
                        mem_R[cr_init_i] = {NB2_R{1'bx}};
                        memoryIO_L[cr_init_i] = {SPARE_WIDTH{1'bx}};
                        memoryIO_R[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end else begin
                        mem[cr_init_i] = {DATA_WIDTH{1'bx}};
                        memoryIO[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end
                end
            end
            crsle_prev_val = CRSLE_buf;
        end
    end

    // CRSRE edge detection: preserve mem/Q=X corruption, NO latch assignment.
    // CRSxE is level-gated (no internal latch); edge detection only triggers
    // mem/Q=X corruption to ensure deterministic output during state transition.
    // Shift mapping uses live CRSRE/CRSRA port values (see crsre_eff above).
    // CRSxE edge -> mem/Q = X immediately (no CLK wait)
    always @(CRSRE_buf) begin
        if (EN_COLRED) begin
            CRSRE_change_time = $realtime;  // track for tcrec/tcrce
            if (crsre_prev_val !== 1'b1 && CRSRE_buf === 1'b1) begin
                // 0/x -> 1: rising edge -- mem/Q=X corruption (preserve), no latch
                // Read CRSRA (port) directly, not CRSRA_buf: buf gate adds a
                // delta-cycle delay. When CRSRE and CRSRA change simultaneously,
                // CRSRE_buf triggers this block at T+delta, but CRSRA_buf may
                // not have updated yet (race in same delta cycle). CRSRA port
                // has already settled at T, so it gives the correct value.
                cr_corrupt_pending  = 1'b1;
                Q_r = {DATA_WIDTH{1'bx}};
                Q_force_x = 1'b1;  // force Q to X immediately (bypass tcd)
                for (cr_init_i = 0; cr_init_i < DEPTH; cr_init_i = cr_init_i + 1) begin
                    if (CENTER_DECODE) begin
                        mem_L[cr_init_i] = {NB2_L{1'bx}};
                        mem_R[cr_init_i] = {NB2_R{1'bx}};
                        memoryIO_L[cr_init_i] = {SPARE_WIDTH{1'bx}};
                        memoryIO_R[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end else begin
                        mem[cr_init_i] = {DATA_WIDTH{1'bx}};
                        memoryIO[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end
                end
            end else if (crsre_prev_val === 1'b1 && CRSRE_buf === 1'b0) begin
                // 1 -> 0: falling edge -- mem/Q=X corruption (preserve), no latch clear
                cr_corrupt_pending  = 1'b1;
                Q_r = {DATA_WIDTH{1'bx}};
                Q_force_x = 1'b1;  // force Q to X immediately (bypass tcd)
                for (cr_init_i = 0; cr_init_i < DEPTH; cr_init_i = cr_init_i + 1) begin
                    if (CENTER_DECODE) begin
                        mem_L[cr_init_i] = {NB2_L{1'bx}};
                        mem_R[cr_init_i] = {NB2_R{1'bx}};
                        memoryIO_L[cr_init_i] = {SPARE_WIDTH{1'bx}};
                        memoryIO_R[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end else begin
                        mem[cr_init_i] = {DATA_WIDTH{1'bx}};
                        memoryIO[cr_init_i] = {SPARE_WIDTH{1'bx}};
                    end
                end
            end
            crsre_prev_val = CRSRE_buf;
        end
    end

    // ========================================================================
    // Input Sampling Layer
    // A/D/CEB/WEB/BWEB are sampled on posedge eff_clk (synchronous to internal clock)
    // ========================================================================
    reg [ADDR_WIDTH-1:0]  samp_A;
    reg [DATA_WIDTH-1:0]  samp_D;
    reg                   samp_CEB;
    reg                   samp_WEB;
    reg [DATA_WIDTH-1:0]  samp_BWEB;

    // A_eff etc. are the same as Latch (timing_check may corrupt to X)
    reg [ADDR_WIDTH-1:0]  A_eff;
    reg [DATA_WIDTH-1:0]  D_eff;
    reg                   CEB_eff;
    reg                   WEB_eff;
    reg [DATA_WIDTH-1:0]  BWEB_eff;

    always @(posedge eff_clk) begin
        samp_A    = A_buf;
        samp_D    = D_buf;
        samp_CEB  = CEB_buf;
        samp_WEB  = WEB_buf;
        samp_BWEB = BWEB_buf;
    end

    // ========================================================================
    // Timing Violation Registers (tviol_*)
    // ========================================================================
    reg [ADDR_WIDTH-1:0]  tviol_A;
    reg [ADDR_WIDTH-1:0]  prev_tviol_A;
    reg [DATA_WIDTH-1:0]  tviol_D;
    reg [DATA_WIDTH-1:0]  prev_tviol_D;
    reg                   tviol_CEB;
    reg                   prev_tviol_CEB;
    reg                   tviol_WEB;
    reg                   prev_tviol_WEB;
    reg [DATA_WIDTH-1:0]  tviol_BWEB;
    reg [DATA_WIDTH-1:0]  prev_tviol_BWEB;
    reg [CR_ADDR_WIDTH-1:0] tviol_CRSLA;
    reg [CR_ADDR_WIDTH-1:0] prev_tviol_CRSLA;
    reg [CR_ADDR_WIDTH-1:0] tviol_CRSRA;
    reg [CR_ADDR_WIDTH-1:0] prev_tviol_CRSRA;
    reg                   tviol_CK_PER;
    reg                   prev_tviol_CK_PER;
    reg                   tviol_CK_MINH;
    reg                   prev_tviol_CK_MINH;
    reg                   tviol_CK_MINL;
    reg                   prev_tviol_CK_MINL;

    initial begin
        tviol_A       = {ADDR_WIDTH{1'b0}};
        prev_tviol_A  = {ADDR_WIDTH{1'b0}};
        tviol_D       = {DATA_WIDTH{1'b0}};
        prev_tviol_D  = {DATA_WIDTH{1'b0}};
        tviol_CEB     = 1'b0;
        prev_tviol_CEB= 1'b0;
        tviol_WEB     = 1'b0;
        prev_tviol_WEB= 1'b0;
        tviol_BWEB     = {DATA_WIDTH{1'b0}};
        prev_tviol_BWEB= {DATA_WIDTH{1'b0}};
        tviol_CRSLA     = {CR_ADDR_WIDTH{1'b0}};
        prev_tviol_CRSLA= {CR_ADDR_WIDTH{1'b0}};
        tviol_CRSRA     = {CR_ADDR_WIDTH{1'b0}};
        prev_tviol_CRSRA= {CR_ADDR_WIDTH{1'b0}};
        tviol_CK_PER  = 1'b0;
        prev_tviol_CK_PER = 1'b0;
        tviol_CK_MINH = 1'b0;
        prev_tviol_CK_MINH = 1'b0;
        tviol_CK_MINL = 1'b0;
        prev_tviol_CK_MINL = 1'b0;
    end

    // ========================================================================
    // Debug Signals for Timing Violation Analysis (TIMING_DEBUG)
    //
    // All dbg_* signals are declared as output ports (see module port list)
    // to guarantee visibility in VCS/Verdi -- they cannot be optimized away.
    //
    // Margin convention: positive = safe, negative = violation
    //   setup_margin = (stable_time) - (required_setup)
    //   hold_margin  = (time_since_ck_rise) - (required_hold)
    //
    // Violation flags are per-cycle (cleared at start of timing_check,
    // set if violation detected). Counters are cumulative.
    // ========================================================================
`ifdef TIMING_DEBUG
    // Helper function: minimum of two realtime values
    function realtime min_real;
        input realtime a, b;
        begin
            min_real = (a < b) ? a : b;
        end
    endfunction

    initial begin
        dbg_ck_period        = 0.0;
        dbg_ck_high_width    = 0.0;
        dbg_ck_low_width     = 0.0;
        dbg_A_setup_margin   = 0.0;
        dbg_D_setup_margin   = 0.0;
        dbg_CEB_setup_margin = 0.0;
        dbg_WEB_setup_margin = 0.0;
        dbg_BWEB_setup_margin = 0.0;
        dbg_A_hold_margin    = 0.0;
        dbg_D_hold_margin    = 0.0;
        dbg_CEB_hold_margin  = 0.0;
        dbg_WEB_hold_margin  = 0.0;
        dbg_BWEB_hold_margin = 0.0;
        dbg_tsclk2op_margin  = 0.0;
        dbg_violation        = 1'b0;
        dbg_violation_type   = 4'd0;
        dbg_setup_violation  = 1'b0;
        dbg_hold_violation   = 1'b0;
        dbg_A_violation      = 1'b0;
        dbg_D_violation      = 1'b0;
        dbg_CEB_violation    = 1'b0;
        dbg_WEB_violation    = 1'b0;
        dbg_BWEB_violation   = 1'b0;
        dbg_ck_violation     = 1'b0;
        dbg_tsclk2op_violation = 1'b0;
        dbg_total_violations   = 0;
        dbg_setup_violations   = 0;
        dbg_hold_violations    = 0;
        dbg_ck_violations      = 0;
        dbg_tsclk2op_violations = 0;
    end
`endif

    // ========================================================================
    // Manual Timing Checks (always active)
    // ========================================================================
    realtime last_ck_rise;
    realtime prev_ck_rise;   // previous posedge time (for tcrhold_rw check)
    realtime last_ck_fall;
    realtime last_CRSLE_rise;
    realtime last_CRSRE_rise;
    realtime last_CRSLE_fall;
    realtime last_CRSRE_fall;
    reg      ck_first_edge = 1'b1;

    always @(posedge eff_clk) begin
        if (ck_first_edge) begin
            last_ck_rise = $realtime;
            ck_first_edge = 1'b0;
        end else begin
            // Clock period check
            if (($realtime - last_ck_rise) < tcyc && tcyc > 0) begin
                tviol_CK_PER = ~tviol_CK_PER;
                `ifdef TIMING_DEBUG
                $display("TIMING_DEBUG: %m Clock period violation at %t (period=%0t, required=%0t)", $realtime, $realtime - last_ck_rise, tcyc);
                `endif
            end
`ifdef TIMING_DEBUG
            dbg_ck_period = $realtime - last_ck_rise;
`endif
            prev_ck_rise  = last_ck_rise;  // save before overwrite
            last_ck_rise  = $realtime;
        end
    end

    always @(negedge eff_clk) begin
        if (!ck_first_edge) begin
            // High pulse width check
            // Normal mode: tckh
            // TEST mode write (test_op_type=0): tckhtw (longer than tckh)
            // TEST mode read  (test_op_type=1): tckhtr (same as normal tckh)
            // TEST mode deselect/corrupt: no check (Q-TM3:D)
            if (test_mode) begin
                case (test_op_type)
                    3'd0: begin
                        // Write: check tckhtw
                        if (($realtime - last_ck_rise) < tckhtw && tckhtw > 0) begin
                            tviol_CK_MINH = ~tviol_CK_MINH;
                            `ifdef TIMING_DEBUG
                            $display("TIMING_DEBUG: %m CLK high width (TEST write tckhtw) violation at %t (width=%0t, required=%0t)", $realtime, $realtime - last_ck_rise, tckhtw);
                            `endif
                        end
                    end
                    3'd1: begin
                        // Read: check tckhtr
                        if (($realtime - last_ck_rise) < tckhtr && tckhtr > 0) begin
                            tviol_CK_MINH = ~tviol_CK_MINH;
                            `ifdef TIMING_DEBUG
                            $display("TIMING_DEBUG: %m CLK high width (TEST read tckhtr) violation at %t (width=%0t, required=%0t)", $realtime, $realtime - last_ck_rise, tckhtr);
                            `endif
                        end
                    end
                    // 3'd2 (deselect) and 3'd3 (corrupt): no CLK high check (Q-TM3:D)
                    default: ; // no check
                endcase
            end else begin
                if (($realtime - last_ck_rise) < tckh && tckh > 0) begin
                    tviol_CK_MINH = ~tviol_CK_MINH;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m CLK high pulse width violation at %t (width=%0t, required=%0t)", $realtime, $realtime - last_ck_rise, tckh);
                    `endif
                end
            end
`ifdef TIMING_DEBUG
            dbg_ck_high_width = $realtime - last_ck_rise;
`endif
            last_ck_fall = $realtime;
        end
    end

    always @(posedge eff_clk) begin
        // Low pulse width check (from last fall to this rise)
        if (last_ck_fall > 0 && ($realtime - last_ck_fall) < tckl && tckl > 0) begin
            tviol_CK_MINL = ~tviol_CK_MINL;
            `ifdef TIMING_DEBUG
            $display("TIMING_DEBUG: %m CLK low pulse width violation at %t (width=%0t, required=%0t)", $realtime, $realtime - last_ck_fall, tckl);
            `endif
        end
`ifdef TIMING_DEBUG
        if (last_ck_fall > 0)
            dbg_ck_low_width = $realtime - last_ck_fall;
`endif
    end

    // ========================================================================
    // TEST mode ttons/ttofs check is integrated into timing_check task
    // (below) to ensure correct execution order and one-shot consumption.
    // ========================================================================

    // ========================================================================
    // CR tcrsetup/tcrhold check is integrated into timing_check task
    // (below) to ensure one-shot consumption and correct execution order.
    // ========================================================================

    // ========================================================================
    // Manual Setup/Hold Checks (always active, mirror specify block)
    //
    // Setup: signal must be stable for tas/tds/tcs/tws before clock edge
    // Hold:  signal must remain stable for tah/tdh/tch/twh after clock edge
    //
    // Implementation:
    //   - Track last change time per signal bit
    //   - At posedge eff_clk: check if signal changed within setup window
    //   - On signal change: check if within hold window of last clock edge
    // ========================================================================

    // Per-bit change time tracking
    realtime A_change_time [ADDR_WIDTH-1:0];
    realtime D_change_time [DATA_WIDTH-1:0];
    realtime BWEB_change_time [DATA_WIDTH-1:0];
    realtime CRSLA_change_time [CR_ADDR_WIDTH-1:0];
    realtime CRSRA_change_time [CR_ADDR_WIDTH-1:0];
    realtime CEB_change_time;
    realtime WEB_change_time;
    // CRSLE_change_time / CRSRE_change_time declared earlier (before edge detection)

    reg [ADDR_WIDTH-1:0]  A_prev_sh;
    reg [DATA_WIDTH-1:0]  D_prev_sh;
    reg [DATA_WIDTH-1:0]  BWEB_prev_sh;
    reg [CR_ADDR_WIDTH-1:0] CRSLA_prev_cr;
    reg [CR_ADDR_WIDTH-1:0] CRSRA_prev_cr;
    reg                   CEB_prev_sh;
    reg                   WEB_prev_sh;

    integer sh_i;  // loop variable for setup/hold checks

    initial begin
        for (sh_i = 0; sh_i < ADDR_WIDTH; sh_i = sh_i + 1) begin
            A_change_time[sh_i] = 0.0;
            A_prev_sh[sh_i] = 1'bx;
        end
        for (sh_i = 0; sh_i < DATA_WIDTH; sh_i = sh_i + 1) begin
            D_change_time[sh_i] = 0.0;
            D_prev_sh[sh_i] = 1'bx;
            BWEB_change_time[sh_i] = 0.0;
            BWEB_prev_sh[sh_i] = 1'bx;
        end
        for (sh_i = 0; sh_i < CR_ADDR_WIDTH; sh_i = sh_i + 1) begin
            CRSLA_change_time[sh_i] = 0.0;
            CRSRA_change_time[sh_i] = 0.0;
            CRSLA_prev_cr[sh_i] = 1'bx;
            CRSRA_prev_cr[sh_i] = 1'bx;
        end
        last_CRSLE_rise = 0.0;
        last_CRSRE_rise = 0.0;
        last_CRSLE_fall = 0.0;
        last_CRSRE_fall = 0.0;
        CEB_change_time = 0.0;
        WEB_change_time = 0.0;
        CRSLE_change_time = 0.0;
        CRSRE_change_time = 0.0;
        CEB_prev_sh = 1'bx;
        WEB_prev_sh = 1'bx;
    end

    // --- Address change tracking + hold check ---
    always @(A_buf) begin
`ifdef TIMING_DEBUG
        dbg_A_hold_margin = 0.0;   // reset, will take min across changed bits
`endif
        for (sh_i = 0; sh_i < ADDR_WIDTH; sh_i = sh_i + 1) begin
            if (A_buf[sh_i] !== A_prev_sh[sh_i]) begin
                A_change_time[sh_i] = $realtime;
                A_prev_sh[sh_i] = A_buf[sh_i];
`ifdef TIMING_DEBUG
                // Hold margin: positive=safe, negative=violation
                if (gate_A && tah_eff > 0 && last_ck_rise > 0) begin
                    dbg_A_hold_margin = ($realtime - last_ck_rise) - tah_eff;
                end
`endif
                // Hold violation: signal changed within tah (or trah in CR shift) of last clock edge
                if (gate_A && tah_eff > 0 && last_ck_rise > 0 &&
                    ($realtime - last_ck_rise) < tah_eff) begin
                    tviol_A[sh_i] = ~tviol_A[sh_i];
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m A[%0d] hold violation at %t (after_ck=%0t, tah_eff=%0t, margin=%0t)", sh_i, $realtime, $realtime - last_ck_rise, tah_eff, dbg_A_hold_margin);
                    `endif
                end
            end
        end
    end

    // --- Data change tracking + hold check ---
    always @(D_buf) begin
`ifdef TIMING_DEBUG
        dbg_D_hold_margin = 0.0;
`endif
        for (sh_i = 0; sh_i < DATA_WIDTH; sh_i = sh_i + 1) begin
            if (D_buf[sh_i] !== D_prev_sh[sh_i]) begin
                D_change_time[sh_i] = $realtime;
                D_prev_sh[sh_i] = D_buf[sh_i];
`ifdef TIMING_DEBUG
                if (gate_D && tdh_eff > 0 && last_ck_rise > 0) begin
                    dbg_D_hold_margin = ($realtime - last_ck_rise) - tdh_eff;
                end
`endif
                // Hold violation: signal changed within tdh (or trdh in CR shift) of last clock edge
                if (gate_D && tdh_eff > 0 && last_ck_rise > 0 &&
                    ($realtime - last_ck_rise) < tdh_eff) begin
                    tviol_D[sh_i] = ~tviol_D[sh_i];
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m D[%0d] hold violation at %t (after_ck=%0t, tdh_eff=%0t, margin=%0t)", sh_i, $realtime, $realtime - last_ck_rise, tdh_eff, dbg_D_hold_margin);
                    `endif
                end
            end
        end
    end

    // --- BWEB change tracking + hold check ---
    always @(BWEB_buf) begin
`ifdef TIMING_DEBUG
        dbg_BWEB_hold_margin = 0.0;
`endif
        for (sh_i = 0; sh_i < DATA_WIDTH; sh_i = sh_i + 1) begin
            if (BWEB_buf[sh_i] !== BWEB_prev_sh[sh_i]) begin
                BWEB_change_time[sh_i] = $realtime;
                BWEB_prev_sh[sh_i] = BWEB_buf[sh_i];
`ifdef TIMING_DEBUG
                if (gate_D && tbwh_eff > 0 && last_ck_rise > 0) begin
                    dbg_BWEB_hold_margin = ($realtime - last_ck_rise) - tbwh_eff;
                end
`endif
                // Hold violation: signal changed within tbwh (or trbwh in CR shift) of last clock edge
                if (gate_D && tbwh_eff > 0 && last_ck_rise > 0 &&
                    ($realtime - last_ck_rise) < tbwh_eff) begin
                    tviol_BWEB[sh_i] = ~tviol_BWEB[sh_i];
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m BWEB[%0d] hold violation at %t (after_ck=%0t, tbwh_eff=%0t, margin=%0t)", sh_i, $realtime, $realtime - last_ck_rise, tbwh_eff, dbg_BWEB_hold_margin);
                    `endif
                end
            end
        end
    end

    // --- CRSxA/CRSxE timing checks are now in timing_check task ---
    // (tcrac/tcrca/tcrec/tcrce: setup/hold vs CLK?, checked every cycle)
    // NOTE: Track on CRSLA/CRSRA (port) directly, not CRSLA_buf/CRSRA_buf.
    //   buf gates add a delta-cycle delay; tracking on _buf causes a race
    //   at posedge (timing_check may read stale change_time).
    always @(CRSLA) begin
        for (sh_i = 0; sh_i < CR_ADDR_WIDTH; sh_i = sh_i + 1) begin
            if (CRSLA[sh_i] !== CRSLA_prev_cr[sh_i]) begin
                CRSLA_change_time[sh_i] = $realtime;
                CRSLA_prev_cr[sh_i] = CRSLA[sh_i];
            end
        end
    end

    always @(CRSRA) begin
        for (sh_i = 0; sh_i < CR_ADDR_WIDTH; sh_i = sh_i + 1) begin
            if (CRSRA[sh_i] !== CRSRA_prev_cr[sh_i]) begin
                CRSRA_change_time[sh_i] = $realtime;
                CRSRA_prev_cr[sh_i] = CRSRA[sh_i];
            end
        end
    end

    // --- CEB change tracking + hold check ---
    always @(CEB_buf) begin
        if (CEB_buf !== CEB_prev_sh) begin
            CEB_change_time = $realtime;
            CEB_prev_sh = CEB_buf;
`ifdef TIMING_DEBUG
            if (gate_CEB && tch_eff > 0 && last_ck_rise > 0)
                dbg_CEB_hold_margin = ($realtime - last_ck_rise) - tch_eff;
`endif
            if (gate_CEB && tch_eff > 0 && last_ck_rise > 0 &&
                ($realtime - last_ck_rise) < tch_eff) begin
                tviol_CEB = ~tviol_CEB;
                `ifdef TIMING_DEBUG
                $display("TIMING_DEBUG: %m CEB hold violation at %t (after_ck=%0t, tch_eff=%0t, margin=%0t)", $realtime, $realtime - last_ck_rise, tch_eff, dbg_CEB_hold_margin);
                `endif
            end
        end
    end

    // --- WEB change tracking + hold check ---
    always @(WEB_buf) begin
        if (WEB_buf !== WEB_prev_sh) begin
            WEB_change_time = $realtime;
            WEB_prev_sh = WEB_buf;
`ifdef TIMING_DEBUG
            if (gate_WEB && twh_eff > 0 && last_ck_rise > 0)
                dbg_WEB_hold_margin = ($realtime - last_ck_rise) - twh_eff;
`endif
            if (gate_WEB && twh_eff > 0 && last_ck_rise > 0 &&
                ($realtime - last_ck_rise) < twh_eff) begin
                tviol_WEB = ~tviol_WEB;
                `ifdef TIMING_DEBUG
                $display("TIMING_DEBUG: %m WEB hold violation at %t (after_ck=%0t, twh_eff=%0t, margin=%0t)", $realtime, $realtime - last_ck_rise, twh_eff, dbg_WEB_hold_margin);
                `endif
            end
        end
    end

    // --- Setup checks at posedge eff_clk ---
    always @(posedge eff_clk) begin
        if (!ck_first_edge) begin
`ifdef TIMING_DEBUG
            // Initialize setup margins to large positive (safe) for min-reduction
            dbg_A_setup_margin   = 9999.0;
            dbg_D_setup_margin   = 9999.0;
            dbg_CEB_setup_margin = 9999.0;
            dbg_WEB_setup_margin = 9999.0;
            dbg_BWEB_setup_margin = 9999.0;
`endif
            // Address setup
            if (gate_A && tas_eff > 0) begin
                for (sh_i = 0; sh_i < ADDR_WIDTH; sh_i = sh_i + 1) begin
`ifdef TIMING_DEBUG
                    if (A_change_time[sh_i] > 0) begin
                        dbg_A_setup_margin = min_real(dbg_A_setup_margin,
                                                      ($realtime - A_change_time[sh_i]) - tas_eff);
                    end
`endif
                    if (A_change_time[sh_i] > 0 && ($realtime - A_change_time[sh_i]) < tas_eff) begin
                        tviol_A[sh_i] = ~tviol_A[sh_i];
                        `ifdef TIMING_DEBUG
                        $display("TIMING_DEBUG: %m A[%0d] setup violation at %t (since_change=%0t, tas_eff=%0t, margin=%0t)", sh_i, $realtime, $realtime - A_change_time[sh_i], tas_eff, ($realtime - A_change_time[sh_i]) - tas_eff);
                        `endif
                    end
                end
            end
            // Data setup
            if (gate_D && tds_eff > 0) begin
                for (sh_i = 0; sh_i < DATA_WIDTH; sh_i = sh_i + 1) begin
`ifdef TIMING_DEBUG
                    if (D_change_time[sh_i] > 0) begin
                        dbg_D_setup_margin = min_real(dbg_D_setup_margin,
                                                      ($realtime - D_change_time[sh_i]) - tds_eff);
                    end
`endif
                    if (D_change_time[sh_i] > 0 && ($realtime - D_change_time[sh_i]) < tds_eff) begin
                        tviol_D[sh_i] = ~tviol_D[sh_i];
                        `ifdef TIMING_DEBUG
                        $display("TIMING_DEBUG: %m D[%0d] setup violation at %t (since_change=%0t, tds_eff=%0t, margin=%0t)", sh_i, $realtime, $realtime - D_change_time[sh_i], tds_eff, ($realtime - D_change_time[sh_i]) - tds_eff);
                        `endif
                    end
                end
            end
            // BWEB setup
            if (gate_D && tbws_eff > 0) begin
                for (sh_i = 0; sh_i < DATA_WIDTH; sh_i = sh_i + 1) begin
`ifdef TIMING_DEBUG
                    if (BWEB_change_time[sh_i] > 0) begin
                        dbg_BWEB_setup_margin = min_real(dbg_BWEB_setup_margin,
                                                       ($realtime - BWEB_change_time[sh_i]) - tbws_eff);
                    end
`endif
                    if (BWEB_change_time[sh_i] > 0 && ($realtime - BWEB_change_time[sh_i]) < tbws_eff) begin
                        tviol_BWEB[sh_i] = ~tviol_BWEB[sh_i];
                        `ifdef TIMING_DEBUG
                        $display("TIMING_DEBUG: %m BWEB[%0d] setup violation at %t (since_change=%0t, tbws_eff=%0t, margin=%0t)", sh_i, $realtime, $realtime - BWEB_change_time[sh_i], tbws_eff, ($realtime - BWEB_change_time[sh_i]) - tbws_eff);
                        `endif
                    end
                end
            end
            // CEB setup
            if (gate_CEB && tcs_eff > 0) begin
`ifdef TIMING_DEBUG
                if (CEB_change_time > 0)
                    dbg_CEB_setup_margin = ($realtime - CEB_change_time) - tcs_eff;
`endif
                if (CEB_change_time > 0 && ($realtime - CEB_change_time) < tcs_eff) begin
                    tviol_CEB = ~tviol_CEB;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m CEB setup violation at %t (since_change=%0t, tcs_eff=%0t, margin=%0t)", $realtime, $realtime - CEB_change_time, tcs_eff, ($realtime - CEB_change_time) - tcs_eff);
                    `endif
                end
            end
            // WEB setup
            if (gate_WEB && tws_eff > 0) begin
`ifdef TIMING_DEBUG
                if (WEB_change_time > 0)
                    dbg_WEB_setup_margin = ($realtime - WEB_change_time) - tws_eff;
`endif
                if (WEB_change_time > 0 && ($realtime - WEB_change_time) < tws_eff) begin
                    tviol_WEB = ~tviol_WEB;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m WEB setup violation at %t (since_change=%0t, tws_eff=%0t, margin=%0t)", $realtime, $realtime - WEB_change_time, tws_eff, ($realtime - WEB_change_time) - tws_eff);
                    `endif
                end
            end
        end
    end

    // ========================================================================
    // Output Stage Signals
    // ========================================================================
    reg [DATA_WIDTH-1:0] Q_tmp;
    reg                  q_fast_update;

    initial begin
        Q_tmp               = {DATA_WIDTH{1'bx}};
        q_fast_update             = 1'b1;
    end

    // ========================================================================
    // Column Redundancy (direct-pin interface, v8.0)
    //
    // CRSLE / CRSLA[CR_ADDR_WIDTH-1:0] : left CR enable + defect IO index
    // CRSRE / CRSRA[CR_ADDR_WIDTH-1:0] : right CR enable + defect IO index
    // CR pins are asynchronous (no clock sync); must be stable during R/W.
    //
    // SD (CD=0): only CRSRE/CRSRA used. spare (memoryIO) at LSB side (MEM[0]).
    //   defect IO index a -> IO<0>=memoryIO, IO<i>=mem<i-1> (1<=i<=a), mem<a> skipped.
    //   CRSLE/CRSLA ignored (no spare on left in SD mode).
    //
    // CD (CD=1): left mem uses CRSLE/CRSLA, right mem uses CRSRE/CRSRA, independent.
    //   Left  (up-shift,  spare at MSB of left):
    //       IO<i>=mem_L<i> (i<a); IO<i>=mem_L<i+1> (a<=i<NB2_L-1);
    //       IO<NB2_L-1>=memoryIO_L; mem_L<a> skipped.
    //   Right (down-shift, spare at LSB of right):
    //       IO<0>=memoryIO_R; IO<i>=mem_R<i-1> (1<=i<=a);
    //       IO<i>=mem_R<i> (i>a); mem_R<a> skipped.
    //
    // Out-of-range address (>= actual column count) -> CR ineffective (no shift).
    // When EN_COLRED=0, all CR pins ignored.
    // ========================================================================

    // Effective CR enables (level-gated, no internal latch).
    // CRSxE is used as a live level gate (=== 1'b1), not an edge-triggered latch.
    // Uses live CRSxA port value for range check (MBIST shift: address changes
    // while CRSxE=1, so range check must follow live value). Aligns with 2P_SRAM
    // and industry standard practice (no CK-edge latch on redundancy signals).
    wire crsle_eff = EN_COLRED && (CRSLE_buf === 1'b1) &&
                     (CENTER_DECODE == 1) && (^CRSLA !== 1'bx) &&
                     (CRSLA < NB2_L);
    wire crsre_eff = EN_COLRED && (CRSRE_buf === 1'b1) &&
                     (^CRSRA !== 1'bx) &&
                     (CRSRA < (CENTER_DECODE ? NB2_R : DATA_WIDTH));

    // Column shift is actually happening (defect in range, CRSxE latched).
    // Used to select tr* timing params over t* in behavioral checks and Q path.
    // (cr_shift_active declared earlier, near Q output block, for forward-ref.)
    assign cr_shift_active = (crsle_eff || crsre_eff);

    // Effective timing params: tr* when CR shift active, else t*.
    // Used by behavioral setup/hold checks (always blocks below).
    // (*_eff variables declared earlier, near Q output block, for forward-ref.)
    // (specify block uses separate $setuphold pairs with &&& conditions --
    //  specparam must be constant, so it cannot reference these variables.)
    always @* begin
        tas_eff  = cr_shift_active ? tras  : tas;
        tah_eff  = cr_shift_active ? trah  : tah;
        tws_eff  = cr_shift_active ? trws  : tws;
        twh_eff  = cr_shift_active ? trwh  : twh;
        tbws_eff = cr_shift_active ? trbws : tbws;
        tbwh_eff = cr_shift_active ? trbwh : tbwh;
        tds_eff  = cr_shift_active ? trds  : tds;
        tdh_eff  = cr_shift_active ? trdh  : tdh;
        tcs_eff  = cr_shift_active ? trcs  : tcs;
        tch_eff  = cr_shift_active ? trch  : tch;
    end

    // Integer indices for use in tasks (tasks can't read wire directly in all tools)
    // Decoded into integer regs via continuous assign workaround: use wires + pass
    // directly to tasks as integer via $unsigned.
    // We pass CRSLA_buf / CRSRA_buf directly to the Colmun tasks.

    // ========================================================================
    // Column Redundancy Helper Tasks (v8.0 direct-pin interface)
    //
    // Four shift-direction tasks. Each takes a defect index `a` (the IO index
    // of the defective column, -1 = CR not active) and produces the expanded
    // (read) or compressed (write) mapping. spare storage (memoryIO) is passed
    // in separately.
    //
    // CRReadDownShift : spare at LSB. IO<0..gs-1>=spare, IO<i>=mem<i-gs> (gs<=i<=a).
    //                   Used by SD (CD=0) and CD right mem.
    // CRReadUpShift   : spare at MSB. IO<i>=mem<i> (i<a), IO<i>=mem<i+gs> (a<=i<N-gs),
    //                   IO<N-gs..N-1>=spare. Used by CD left mem.
    // CRWriteDownShift / CRWriteUpShift : inverse of the read tasks.
    // v12.6: gs (group size) = SPARE_WIDTH. CM=1 -> gs=2 (2-bit group repair);
    //        CM!=1 -> gs=1 (1-bit repair, identical to v12.5).
    //        CRSxA indexes individual bit; group g = a / gs.
    // ========================================================================
    reg [DATA_WIDTH-1:0] colred_read_result;

    // --- Down-shift read (spare at LSB group). a = defect IO index. ---
    // gs=1: IO<0>=spare; IO<i>=mem<i-1> (1<=i<=a); IO<i>=mem<i> (i>a); mem<a> skipped.
    // gs=2: IO<0,1>=spare[0,1]; IO<i>=mem<i-2> (2<=i<=2g+1); IO<i>=mem<i> (i>=2g+2);
    //       mem<2g,2g+1> skipped (defect group).
    // General: group 0 = spare; groups 1..g shift by gs; groups g+1..end no shift.
    // N = width (DATA_WIDTH for SD, NB2_R for CD right mem).
    task CRReadDownShift;
        input integer a;                 // defect IO index (-1 = inactive)
        input integer n;                 // width of this mem
        input [DATA_WIDTH-1:0] memdata;  // main memory word (uses [n-1:0])
        input [1:0] sparetap;            // memoryIO spare bits ([SPARE_WIDTH-1:0] used)
        integer i, k;
        integer gs, g;
        reg [DATA_WIDTH-1:0] result;
    begin
        gs = SPARE_WIDTH;
        if (a < 0) begin
            colred_read_result = memdata;
        end else begin
            g = a / gs;  // defect group index
            result = {DATA_WIDTH{1'bx}};
            // Group 0: spare
            for (k = 0; k < gs; k = k + 1)
                result[k] = sparetap[k];
            // Groups 1..g: shift down by gs (IO<i> = mem<i-gs>)
            for (i = gs; i <= g*gs + gs - 1; i = i + 1)
                result[i] = memdata[i-gs];
            // Groups g+1..end: no shift (IO<i> = mem<i>)
            for (i = g*gs + gs; i < n; i = i + 1)
                result[i] = memdata[i];
            // bits [n : DATA_WIDTH-1] stay X (unused for this half)
            colred_read_result = result;
        end
    end
    endtask

    // --- Down-shift write (spare at LSB group). a = defect IO index. ---
    // Inverse of read: spare=D<0..gs-1>; mem<j>=D<j+gs> (0<=j<=g*gs-1);
    //   mem<g*gs..g*gs+gs-1>=skip; mem<j>=D<j> (g*gs+gs<=j<=n-1).
    // N = width (DATA_WIDTH for SD, NB2_R for CD right mem).
    // Returns compressed main-mem word in colred_write_result and spare bits in
    // colred_write_spare ([SPARE_WIDTH-1:0] used).
    reg [DATA_WIDTH-1:0] colred_write_result;
    reg [SPARE_WIDTH-1:0] colred_write_spare;

    task CRWriteDownShift;
        input integer a;
        input integer n;
        input [DATA_WIDTH-1:0] writedata;
        input [DATA_WIDTH-1:0] curmem;
        integer i, k;
        integer gs, g;
        reg [DATA_WIDTH-1:0] result;
    begin
        gs = SPARE_WIDTH;
        if (a < 0) begin
            colred_write_result = writedata;
            colred_write_spare  = {SPARE_WIDTH{1'bx}};
        end else begin
            g = a / gs;
            result = curmem;
            // spare = D<0..gs-1>
            for (k = 0; k < gs; k = k + 1)
                colred_write_spare[k] = writedata[k];
            // mem<j> = D<j+gs> (j < g*gs, shift down)
            for (i = 0; i <= g*gs - 1; i = i + 1)
                result[i] = writedata[i+gs];
            // result[g*gs .. g*gs+gs-1] preserved as curmem (defective group, skip)
            // mem<j> = D<j> (j >= g*gs+gs, no shift)
            for (i = g*gs + gs; i < n; i = i + 1)
                result[i] = writedata[i];
            colred_write_result = result;
        end
    end
    endtask

    // --- Up-shift read (spare at MSB group). a = defect IO index. ---
    // gs=1: IO<i>=mem<i> (i<a); IO<i>=mem<i+1> (a<=i<N-1); IO<N-1>=spare. mem<a> skipped.
    // gs=2: IO<i>=mem<i> (i<2g); IO<i>=mem<i+2> (2g<=i<N-2); IO<N-2,N-1>=spare.
    //       mem<2g,2g+1> skipped (defect group).
    // General: groups 0..g-1 no shift; groups g..ngroups-2 shift by gs;
    //          last group = spare.
    // N = width (NB2_L for CD left mem). mem<N-gs..N-1> unused in main mem (spare in memoryIO).
    task CRReadUpShift;
        input integer a;
        input integer n;                 // width of this mem
        input [DATA_WIDTH-1:0] memdata;  // main memory word (uses [n-1:0])
        input [1:0] sparetap;
        integer i, k;
        integer gs, g;
        reg [DATA_WIDTH-1:0] result;
    begin
        gs = SPARE_WIDTH;
        if (a < 0) begin
            colred_read_result = memdata;
        end else begin
            g = a / gs;
            result = {DATA_WIDTH{1'bx}};
            // Groups 0..g-1: no shift (IO<i> = mem<i>)
            for (i = 0; i < g*gs; i = i + 1)
                result[i] = memdata[i];
            // Groups g..ngroups-2: shift up by gs (IO<i> = mem<i+gs>)
            for (i = g*gs; i < n - gs; i = i + 1)
                result[i] = memdata[i+gs];
            // Last group: spare
            for (k = 0; k < gs; k = k + 1)
                result[n - gs + k] = sparetap[k];
            // bits [n : DATA_WIDTH-1] stay X (unused for this half)
            colred_read_result = result;
        end
    end
    endtask

    // --- Up-shift write (spare at MSB group). a = defect IO index. ---
    // gs=1: mem<i>=D<i> (i<a); mem<a>=skip; mem<i>=D<i-1> (a<i<=n-1); spare=D<n-1>.
    // gs=2: mem<i>=D<i> (i<2g); mem<2g,2g+1>=skip; mem<i>=D<i-2> (2g+2<=i<=n-1);
    //       spare=D<n-2,n-1>.
    // General: groups 0..g-1 no shift; group g skip; groups g+1..ngroups-1 shift;
    //          last group = spare.
    task CRWriteUpShift;
        input integer a;
        input integer n;
        input [DATA_WIDTH-1:0] writedata;
        input [DATA_WIDTH-1:0] curmem;
        integer i, k;
        integer gs, g;
        reg [DATA_WIDTH-1:0] result;
    begin
        gs = SPARE_WIDTH;
        if (a < 0) begin
            colred_write_result = writedata;
            colred_write_spare  = {SPARE_WIDTH{1'bx}};
        end else begin
            g = a / gs;
            result = curmem;
            // spare = D<n-gs..n-1>
            for (k = 0; k < gs; k = k + 1)
                colred_write_spare[k] = writedata[n - gs + k];
            // mem<i> = D<i> (i < g*gs, no shift)
            for (i = 0; i < g*gs; i = i + 1)
                result[i] = writedata[i];
            // result[g*gs .. g*gs+gs-1] preserved as curmem (defective group, skipped)
            // mem<i> = D<i-gs> (i >= g*gs+gs, up-shift)
            for (i = g*gs + gs; i <= n-1; i = i + 1)
                result[i] = writedata[i-gs];
            colred_write_result = result;
        end
    end
    endtask

    // ========================================================================
    // Fault Injection: apply XOR/SA0/SA1 to raw mem data before CR shift.
    //   XOR mode (FAULT_INJ):  fi_result = mem ^ XOR array
    //   SA0/SA1 mode (default):  fi_result = (mem & sa0) | sa1  (no-op)
    // Called from read path in sram_op_exec, before CRReadDownShift/etc.
    // ========================================================================
    function [DATA_WIDTH-1:0] apply_fi;
        input [DATA_WIDTH-1:0] raw_data;
        input [ADDR_WIDTH-1:0] addr;
        begin
            if (fi_enable)
                apply_fi = raw_data ^ fi_xor_mask[addr];
            else
                apply_fi = (raw_data & fi_and_mask[addr]) |
                                        fi_or_mask[addr];
        end
    endfunction

    // ========================================================================
    // Memory Storage & Column Redundancy - generate blocks for hierarchical access
    //
    // All storage arrays are declared at MODULE LEVEL (not inside generate)
    // so that Verdi/FSDB can access them directly as dut.mem, dut.memoryIO, etc.
    // without needing to expand generate-block hierarchy.
    // ========================================================================
    integer i_init;

    // (mem, mem_L, mem_R, memoryIO, memoryIO_L, memoryIO_R declared earlier
    //  for CR edge detection blocks -- VCS declaration order requirement)

    generate if (CENTER_DECODE == 0) begin : gen_sd

        // ---- SD mode: Memory & Shift Register ----
        // (mem, memoryIO declared at module level for Verdi visibility)

        initial begin
            for (i_init = 0; i_init < DEPTH; i_init = i_init + 1) begin
                mem[i_init]      = INIT_TO_X ? {DATA_WIDTH{1'bx}} : {DATA_WIDTH{1'b0}};
                memoryIO[i_init] = INIT_TO_X ? {SPARE_WIDTH{1'bx}} : {SPARE_WIDTH{1'b0}};
            end
        end

        // ---- SD mode: mem_init task ----
        task mem_init;
            input ini_value;
            reg   ini_value;
            integer k;
        begin
            if (ini_value === 1'bx) begin
                for (k = 0; k < DEPTH; k = k + 1) begin
                    mem[k]      <= {DATA_WIDTH{1'bx}};
                    memoryIO[k] <= {SPARE_WIDTH{1'bx}};
                end
            end else if (ini_value === 1'b1) begin
                for (k = 0; k < DEPTH; k = k + 1) begin
                    mem[k]      <= {DATA_WIDTH{1'b1}};
                    memoryIO[k] <= {SPARE_WIDTH{1'b1}};
                end
            end else if (ini_value === 1'b0) begin
                for (k = 0; k < DEPTH; k = k + 1) begin
                    mem[k]      <= {DATA_WIDTH{1'b0}};
                    memoryIO[k] <= {SPARE_WIDTH{1'b0}};
                end
            end
        end
        endtask

        // ---- SD mode: sram_op_exec task ----
        task sram_op_exec;
            integer j;
        begin
            // --- CR latch corruption (CRSxE rose since last CLK) ---
            if (cr_corrupt_pending) begin
                cr_corrupt_pending = 1'b0;
                mem_init(1'bx);
                q_fast_update = 1'b1;
                Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                if (test_mode) test_op_type = 3'd3;  // hazard/corrupt
            end else
            // --- Hazard R4/R5: CRSxE/CRSxA x/z -> all x, Q=x ---
            if ((EN_COLRED && (CRSRE_buf !== 1'b1) && (CRSRE_buf === 1'bx || CRSRE_buf === 1'bz)) ||
                (EN_COLRED && (CRSRE_buf !== 1'b1) && (CRSRE_buf === 1'b1 && (^CRSRA_buf === 1'bx)))) begin
                mem_init(1'bx);
                q_fast_update = 1'b1;
                Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                if (test_mode) test_op_type = 3'd3;  // hazard/corrupt
            end else
            casez({WEB_eff, CEB_eff})
                    // Write Operation
                    2'b00: begin
                        if (test_mode) test_op_type = 3'd0;  // write
                        if (^A_eff === 1'bx) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                            if (test_mode) test_op_type = 3'd3;  // A=x write hazard
                        end else begin
                            if (crsre_eff) begin : sd_cr_wr
                                // --- Column Redundancy active (SD, spare at LSB): down-shift write ---
                                integer bw_idx;
                                integer a;
                                integer gs, g, sk;
                                gs = SPARE_WIDTH;
                                a = CRSRA;  // use live port value (MBIST shift fix)
                                g = a / gs;  // defect group index
                                // 1. Write memoryIO (spare = D[0..gs-1], the LSB group)
                                for (sk = 0; sk < gs; sk = sk + 1) begin
                                    if (BWEB_eff[sk] === 1'b0)
                                        memoryIO[A_eff][sk] = (D_eff[sk] === 1'bx || D_eff[sk] === 1'bz) ? 1'bx : D_eff[sk];
                                end
                                // 2. Compress write data for main memory
                                CRWriteDownShift(a, DATA_WIDTH, D_eff, mem[A_eff]);
                                // 3. Write compressed data with BWEB mapping
                                //    Physical mem<j> stores logical D<j+gs> (j<g*gs) or D<j> (j>=g*gs+gs);
                                //    j in [g*gs, g*gs+gs-1] = defect group (skip).
                                //    BWEB lookup uses logical IO index: j+gs (j<g*gs), j (j>=g*gs+gs).
                                for (j = 0; j < DATA_WIDTH; j = j + 1) begin
                                    if (j >= g*gs && j <= g*gs + gs - 1) begin
                                        // Defective group: write X (not skipped)
                                        mem[A_eff][j] = 1'bx;
                                    end else begin
                                        if (j < g*gs)
                                            bw_idx = j + gs;   // mem<j> = D<j+gs>, check BWEB<j+gs>
                                        else
                                            bw_idx = j;        // mem<j> = D<j>, check BWEB<j>
                                        if (bw_idx >= 0 && bw_idx < DATA_WIDTH &&
                                            BWEB_eff[bw_idx] === 1'b0)
                                            mem[A_eff][j] = (colred_write_result[j] === 1'bx || colred_write_result[j] === 1'bz) ? 1'bx : colred_write_result[j];
                                        else if (bw_idx >= 0 && bw_idx < DATA_WIDTH &&
                                                 (BWEB_eff[bw_idx] === 1'bx || BWEB_eff[bw_idx] === 1'bz))
                                            mem[A_eff][j] = 1'bx;  // hazard R11
                                    end
                                end
                            end else begin
                                // --- No column redundancy: normal BWEB write ---
                                for (j = 0; j < DATA_WIDTH; j = j + 1) begin
                                    if (BWEB_eff[j] === 1'b0) begin
                                        mem[A_eff][j] = (D_eff[j] === 1'bx || D_eff[j] === 1'bz) ? 1'bx : D_eff[j];
                                    end
                                    else if (BWEB_eff[j] === 1'bx || BWEB_eff[j] === 1'bz) begin
                                        mem[A_eff][j] = 1'bx;  // hazard R11: BWEB=x/z -> mem=x
                                    end
                                end
                            end
                            q_fast_update = 1'b1;
                            // Write only stores to mem; Q keeps previous value
                        end
                    end

                    // Read Operation
                    2'b10: begin
                        if (test_mode) test_op_type = 3'd1;  // read
                        if (^A_eff === 1'bx) begin
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)  // A=x/z read: Q=X (hazard R8)
                            if (test_mode) test_op_type = 3'd3;  // A=x read hazard
                        end else begin
                            fi_result = apply_fi(mem[A_eff], A_eff);
                            if (crsre_eff) begin
                                // Column Redundancy active (SD, spare at LSB): down-shift read
                                CRReadDownShift(CRSRA, DATA_WIDTH, fi_result, memoryIO[A_eff]);  // live port (MBIST shift fix)
                                Q_tmp = colred_read_result;
                            end else begin
                                Q_tmp = fi_result;
                            end
                            if (test_mode) begin
                                // TEST mode: store for negedge output (Q updates at negedge + tcdt)
                                test_read_data = Q_tmp;
                            end else begin
                                Q_r <= Q_tmp;  // Normal read
                                Q_force_x <= 1'b0;   // clear force-x
                            end
                            q_fast_update = 1'b1;
                        end
                    end

                    // Chip Unselect (CEB=1): Q holds previous value
                    // No Q assignment -- previous EventQRead/EventQWrite already
                    // scheduled Q; without a new assignment, Q retains naturally
                    2'b01, 2'b11, 2'bx1: begin
                        if (test_mode) test_op_type = 3'd2;  // deselect
                        q_fast_update = 1'b1;
                    end

                    // x/z on CEB or WEB -> memory corruption
                    // x/z on CEB or WEB -> all x (hazard R6/R7)
                    2'bxx, 2'b1x, 2'b0x, 2'bx0: begin
                        if (test_mode) test_op_type = 3'd3;  // hazard/corrupt
                        if (eff_clk === 1'b1) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                        end
                    end
                endcase
        end
        endtask

        // ---- SD mode: timing_check task ----
        task timing_check;
            integer i;
            integer has_violation_flag;
        begin
            // --- CR timing flags: clear and re-check this cycle ---
            // tcrac/tcrca: CRSxA setup/hold vs CLK?
            // tcrec/tcrce: CRSxE setup/hold vs CLK?
            tcrac_v_l = 1'b0; tcrac_v_r = 1'b0;
            tcrca_v_l = 1'b0; tcrca_v_r = 1'b0;
            tcrec_v_l = 1'b0; tcrec_v_r = 1'b0;
            tcrce_v_l = 1'b0; tcrce_v_r = 1'b0;
            // --- TEST mode ttons/ttofs: clear and re-check (one-shot) ---
            ttons_violation = 1'b0;
            ttofs_violation = 1'b0;
            if (ttons_pending && test_mode) begin
                ttons_pending = 1'b0;
                if (test_rise_time > 0 && ($realtime - test_rise_time) < ttons && ttons > 0) begin
                    ttons_violation = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m ttons violation (TEST? to CLK?) at %t (interval=%0t, required=%0t)", $realtime, $realtime - test_rise_time, ttons);
                    `endif
                end
            end
            if (ttofs_pending && !test_mode) begin
                ttofs_pending = 1'b0;
                if (test_fall_time > 0 && ($realtime - test_fall_time) < ttofs && ttofs > 0) begin
                    ttofs_violation = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m ttofs violation (TEST? to CLK?) at %t (interval=%0t, required=%0t)", $realtime, $realtime - test_fall_time, ttofs);
                    `endif
                end
            end
            if (EN_COLRED) begin
                // CRSxE setup vs CLK? (tcrec): check if CRSxE changed within tcrec
                if (tcrec > 0 && CRSLE_change_time > 0 && last_ck_rise > 0 &&
                    ($realtime - CRSLE_change_time) < tcrec)
                    tcrec_v_l = 1'b1;
                if (tcrec > 0 && CRSRE_change_time > 0 && last_ck_rise > 0 &&
                    ($realtime - CRSRE_change_time) < tcrec)
                    tcrec_v_r = 1'b1;
                // CRSxE hold vs CLK? (tcrce): check if CRSxE changed within tcrce after CLK?
                // Uses prev_ck_rise (last CLK?) because last_ck_rise is already updated
                // to current posedge by the time timing_check runs.
                if (tcrce > 0 && CRSLE_change_time > 0 && prev_ck_rise > 0 &&
                    (CRSLE_change_time > prev_ck_rise) &&
                    (CRSLE_change_time - prev_ck_rise) < tcrce)
                    tcrce_v_l = 1'b1;
                if (tcrce > 0 && CRSRE_change_time > 0 && prev_ck_rise > 0 &&
                    (CRSRE_change_time > prev_ck_rise) &&
                    (CRSRE_change_time - prev_ck_rise) < tcrce)
                    tcrce_v_r = 1'b1;
                // CRSxA setup vs CLK? (tcrac): per-bit, any bit changed within tcrac
                for (tcr_i = 0; tcr_i < CR_ADDR_WIDTH; tcr_i = tcr_i + 1) begin
                    if (tcrac > 0 && CRSLA_change_time[tcr_i] > 0 && last_ck_rise > 0 &&
                        ($realtime - CRSLA_change_time[tcr_i]) < tcrac)
                        tcrac_v_l = 1'b1;
                    if (tcrac > 0 && CRSRA_change_time[tcr_i] > 0 && last_ck_rise > 0 &&
                        ($realtime - CRSRA_change_time[tcr_i]) < tcrac)
                        tcrac_v_r = 1'b1;
                end
                // CRSxA hold vs CLK? (tcrca): per-bit, any bit changed within tcrca after CLK?
                // Uses prev_ck_rise (last CLK?) because last_ck_rise is already updated
                // to current posedge by the time timing_check runs.
                for (tcr_i = 0; tcr_i < CR_ADDR_WIDTH; tcr_i = tcr_i + 1) begin
                    if (tcrca > 0 && CRSLA_change_time[tcr_i] > 0 && prev_ck_rise > 0 &&
                        (CRSLA_change_time[tcr_i] > prev_ck_rise) &&
                        (CRSLA_change_time[tcr_i] - prev_ck_rise) < tcrca)
                        tcrca_v_l = 1'b1;
                    if (tcrca > 0 && CRSRA_change_time[tcr_i] > 0 && prev_ck_rise > 0 &&
                        (CRSRA_change_time[tcr_i] > prev_ck_rise) &&
                        (CRSRA_change_time[tcr_i] - prev_ck_rise) < tcrca)
                        tcrca_v_r = 1'b1;
                end
            end

`ifdef TIMING_DEBUG
            // Clear per-cycle violation flags at start of each evaluation
            dbg_violation          = 1'b0;
            dbg_violation_type     = 4'd0;
            dbg_setup_violation    = 1'b0;
            dbg_hold_violation     = 1'b0;
            dbg_A_violation        = 1'b0;
            dbg_D_violation        = 1'b0;
            dbg_CEB_violation      = 1'b0;
            dbg_WEB_violation      = 1'b0;
            dbg_BWEB_violation     = 1'b0;
            dbg_ck_violation       = 1'b0;
            dbg_tsclk2op_violation = 1'b0;
            dbg_tsclk2op_margin    = 0.0;
`endif
            // Clock period/width violation
            if (tviol_CK_PER !== prev_tviol_CK_PER ||
                tviol_CK_MINH !== prev_tviol_CK_MINH ||
                tviol_CK_MINL !== prev_tviol_CK_MINL) begin
                if (test_mode) begin
                    // TEST mode: flag for negedge adjudication (no immediate corrupt)
                    test_violation_clk = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_VIOLATION: %m Clock period/width violation (TEST mode) at %t -- flagged", $realtime);
                    dbg_violation = 1'b1;
                    dbg_violation_type = 4'd1;
                    dbg_ck_violation = 1'b1;
                    dbg_ck_violations = dbg_ck_violations + 1;
                    dbg_total_violations = dbg_total_violations + 1;
                    `endif
                    // Still pre-write via sram_op_exec (Q1:C posedge??)
                    A_eff    = samp_A;
                    D_eff    = samp_D;
                    CEB_eff  = samp_CEB;
                    WEB_eff  = samp_WEB;
                    BWEB_eff = samp_BWEB;
                    sram_op_exec;
                end else if (CEB_buf !== 1'b1) begin
                    `ifdef TIMING_DEBUG
                    $display("TIMING_VIOLATION: %m Clock period/width violation at %t -- mem=all X, Q=X", $realtime);
                    dbg_violation = 1'b1;
                    dbg_violation_type = 4'd1;
                    dbg_ck_violation = 1'b1;
                    dbg_ck_violations = dbg_ck_violations + 1;
                    dbg_total_violations = dbg_total_violations + 1;
                    `endif
                    mem_init(1'bx);
                    q_fast_update = 1'b1;
                    Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                end
            end
            // Clock valid -- check signal setup/hold violations + CR R/W period
            else begin
                has_violation_flag = 0;

                // --- CR mode R/W period check (tcrhold_rw) ---
                // In CR mode (CRSxE=1), every R/W cycle must satisfy
                // tcrhold_rw (min CLK period). Violation -> Q/MEM = X.
                // Skip during cr_corrupt_pending (CRSxE edge cycle, not a real R/W).
                if (EN_COLRED && !cr_corrupt_pending &&
                    ((CRSLE_buf === 1'b1) || (CRSRE_buf === 1'b1)) &&
                    tcrhold_rw > 0 && prev_ck_rise > 0 &&
                    ($realtime - prev_ck_rise) < tcrhold_rw) begin
                    cr_rw_violation = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m tcrhold_rw violation at %t (period=%0t, required=%0t)", $realtime, $realtime - prev_ck_rise, tcrhold_rw);
                    `endif
                end

                for (i = 0; i < ADDR_WIDTH; i = i + 1) begin
                    if (tviol_A[i] !== prev_tviol_A[i]) begin
                        if (!test_mode) samp_A[i] = 1'bx;  // TEST mode: keep actual value for pre-write
                        has_violation_flag = 1;
`ifdef TIMING_DEBUG
                        dbg_A_violation = 1'b1;
`endif
                    end
                end
                for (i = 0; i < DATA_WIDTH; i = i + 1) begin
                    if (tviol_D[i] !== prev_tviol_D[i]) begin
                        if (!test_mode) samp_D[i] = 1'bx;
                        has_violation_flag = 1;
`ifdef TIMING_DEBUG
                        dbg_D_violation = 1'b1;
`endif
                    end
                end
                if (tviol_CEB !== prev_tviol_CEB) begin
                    if (!test_mode) samp_CEB = 1'bx;
                    has_violation_flag = 1;
`ifdef TIMING_DEBUG
                    dbg_CEB_violation = 1'b1;
`endif
                end
                if (tviol_WEB !== prev_tviol_WEB) begin
                    if (!test_mode) samp_WEB = 1'bx;
                    has_violation_flag = 1;
`ifdef TIMING_DEBUG
                    dbg_WEB_violation = 1'b1;
`endif
                end
                for (i = 0; i < DATA_WIDTH; i = i + 1) begin
                    if (tviol_BWEB[i] !== prev_tviol_BWEB[i]) begin
                        if (!test_mode) samp_BWEB[i] = 1'bx;
                        has_violation_flag = 1;
`ifdef TIMING_DEBUG
                        dbg_BWEB_violation = 1'b1;
`endif
                    end
                end
                for (i = 0; i < CR_ADDR_WIDTH; i = i + 1) begin
                    if (tviol_CRSLA[i] !== prev_tviol_CRSLA[i] ||
                        tviol_CRSRA[i] !== prev_tviol_CRSRA[i]) begin
                        has_violation_flag = 1;
                        $display("WARNING: %m CRSxA setup/hold timing violation at %t -- R/W result = X", $realtime);
                    end
                end

                if (test_mode) begin
                    // TEST mode: flag violation, always pre-write via sram_op_exec
                    // (Q1:C: posedge pre-write, Q13:A: negedge adjudicates)
                    if (has_violation_flag || ttons_violation || ttofs_violation || tcrac_v_l || tcrac_v_r || tcrca_v_l || tcrca_v_r || tcrec_v_l || tcrec_v_r || tcrce_v_l || tcrce_v_r || cr_rw_violation) begin
                        test_violation_pos = 1'b1;
                        `ifdef TIMING_DEBUG
                        $display("TIMING_VIOLATION: %m Setup/hold/ttons/ttofs violation (TEST mode) at %t -- flagged", $realtime);
                        dbg_violation = 1'b1;
                        dbg_violation_type = 4'd4;
                        if (dbg_A_setup_margin < 0 || dbg_D_setup_margin < 0 ||
                            dbg_CEB_setup_margin < 0 || dbg_WEB_setup_margin < 0 ||
                            dbg_BWEB_setup_margin < 0)
                            dbg_setup_violation = 1'b1;
                        if (dbg_A_hold_margin < 0 || dbg_D_hold_margin < 0 ||
                            dbg_CEB_hold_margin < 0 || dbg_WEB_hold_margin < 0 ||
                            dbg_BWEB_hold_margin < 0)
                            dbg_hold_violation = 1'b1;
                        if (dbg_setup_violation)
                            dbg_setup_violations = dbg_setup_violations + 1;
                        if (dbg_hold_violation)
                            dbg_hold_violations = dbg_hold_violations + 1;
                        dbg_total_violations = dbg_total_violations + 1;
                        `endif
                    end
                    // Pre-write with actual latched values (not corrupted)
                    A_eff    = samp_A;
                    D_eff    = samp_D;
                    CEB_eff  = samp_CEB;
                    WEB_eff  = samp_WEB;
                    BWEB_eff = samp_BWEB;
                    sram_op_exec;
                end else if (has_violation_flag || ttofs_violation || tcrac_v_l || tcrac_v_r || tcrca_v_l || tcrca_v_r || tcrec_v_l || tcrec_v_r || tcrce_v_l || tcrce_v_r || cr_rw_violation) begin
                    // Normal mode: Timing violation detected -> directly fail: Q=X
                    // (NOT routed through sram_op_exec which would give Q=hold for A=x read)
                    `ifdef TIMING_DEBUG
                    $display("TIMING_VIOLATION: %m Setup/hold violation at %t -- Q forced to X", $realtime);
                    dbg_violation = 1'b1;
                    dbg_violation_type = 4'd4;
                    if (dbg_A_setup_margin < 0 || dbg_D_setup_margin < 0 ||
                        dbg_CEB_setup_margin < 0 || dbg_WEB_setup_margin < 0 ||
                        dbg_BWEB_setup_margin < 0)
                        dbg_setup_violation = 1'b1;
                    if (dbg_A_hold_margin < 0 || dbg_D_hold_margin < 0 ||
                        dbg_CEB_hold_margin < 0 || dbg_WEB_hold_margin < 0 ||
                        dbg_BWEB_hold_margin < 0)
                        dbg_hold_violation = 1'b1;
                    if (dbg_setup_violation)
                        dbg_setup_violations = dbg_setup_violations + 1;
                    if (dbg_hold_violation)
                        dbg_hold_violations = dbg_hold_violations + 1;
                    dbg_total_violations = dbg_total_violations + 1;
                    `endif
                    q_fast_update = 1'b1;
                    Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)

                    // If operation could be a write, also corrupt memory
                    if (CEB_buf !== 1'b1) begin
                        if (WEB_buf === 1'b0) begin
                            // Write operation -> corrupt target address
                            if (^A_buf !== 1'bx) begin
                                mem[A_buf] = {DATA_WIDTH{1'bx}};
                                memoryIO[A_buf] = {SPARE_WIDTH{1'bx}};
                            end else
                                mem_init(1'bx);
                        end else if (WEB_buf !== 1'b1) begin
                            // WEB unknown (x/z) -> worst case, corrupt all
                            mem_init(1'bx);
                        end
                        // Read operation (WEB_buf=1): only Q=X, memory intact
                    end
                end else begin
                    // No violations -- normal operation through sram_op_exec
                    A_eff    = samp_A;
                    D_eff    = samp_D;
                    CEB_eff  = samp_CEB;
                    WEB_eff  = samp_WEB;
                    BWEB_eff = samp_BWEB;

                    sram_op_exec;
                end
            end

            prev_tviol_A       = tviol_A;
            prev_tviol_D       = tviol_D;
            prev_tviol_CEB     = tviol_CEB;
            prev_tviol_WEB     = tviol_WEB;
            prev_tviol_BWEB    = tviol_BWEB;
            prev_tviol_CRSLA   = tviol_CRSLA;
            prev_tviol_CRSRA   = tviol_CRSRA;
            prev_tviol_CK_PER  = tviol_CK_PER;
            prev_tviol_CK_MINH = tviol_CK_MINH;
            prev_tviol_CK_MINL = tviol_CK_MINL;
        end
        endtask

        // ---- SD mode: Main Clock Block ----
        always @(posedge eff_clk) begin
            if ($realtime != 0) begin
                // Clear TEST mode violation flags at start of each cycle
                if (test_mode) begin
                    test_violation_pos = 1'b0;
                    test_violation_clk = 1'b0;
        cr_rw_violation    = 1'b0;
                end
                if (CLK_buf === 1'bx || CLK_buf === 1'bz) begin
                    mem_init(1'bx);
                    q_fast_update = 1'b1;
                    Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                end else begin
                    timing_check;
                end
            end
        end

        // ---- SD mode: TEST Mode Negedge Adjudication Block ----
        // (per Q1:C, Q13:A: posedge pre-writes + flags, negedge adjudicates)
        always @(negedge eff_clk) begin
            if (test_mode && $realtime != 0) begin
                // Check CLK high width violation directly (tckhtw/tckhtr)
                // last_ck_rise was set at posedge; $realtime is negedge time.
                // Cannot rely on tviol_CK_MINH (race between always blocks).
                case (test_op_type)
                    3'd0: begin
                        // Write: check tckhtw
                        if (tckhtw > 0 && ($realtime - last_ck_rise) < tckhtw) begin
                            test_violation_clk = 1'b1;
                            `ifdef TIMING_DEBUG
                            $display("TIMING_DEBUG: %m tckhtw violation at negedge %t (width=%0t, required=%0t)", $realtime, $realtime - last_ck_rise, tckhtw);
                            `endif
                        end
                    end
                    3'd1: begin
                        // Read: check tckhtr
                        if (tckhtr > 0 && ($realtime - last_ck_rise) < tckhtr) begin
                            test_violation_clk = 1'b1;
                            `ifdef TIMING_DEBUG
                            $display("TIMING_DEBUG: %m tckhtr violation at negedge %t (width=%0t, required=%0t)", $realtime, $realtime - last_ck_rise, tckhtr);
                            `endif
                        end
                    end
                    // deselect/corrupt: no CLK high check
                    default: ;
                endcase

                // Adjudicate based on operation type and violation flags
                case (test_op_type)
                    3'd0: begin
                        // Write operation
                        // Q11:B: any violation -> mem = all X
                        if (test_violation_clk || test_violation_pos) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                        end
                        // No violation: mem retains pre-written value (from posedge)
                    end
                    3'd1: begin
                        // Read operation
                        // Q14:A: any violation -> Q = X
                        // Also check cr_corrupt_pending: CRSxE edge between
                        // posedge and negedge invalidates pre-captured data.
                        if (test_violation_clk || test_violation_pos || cr_corrupt_pending) begin
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                        end else begin
                            // No violation: Q outputs at negedge + tcdt
                            // (v12.4: tcdt delay now via assign #(tcd) Q_normal, not Q_r NBA)
                            Q_r <= test_read_data;
                            Q_force_x <= 1'b0;   // clear force-x
                        end
                        q_fast_update = 1'b1;
                    end
                    3'd2: begin
                        // Deselect (CEB=1)
                        // Q12:B: clock-level violation -> all mem = X, Q = X
                        //         setup/hold violation -> no consequence
                        if (test_violation_clk) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                        end
                        // No clock violation: Q holds, mem unchanged
                    end
                    3'd3: begin
                        // Hazard/corrupt (CLK=x, CEB=x, WEB=x, A=x, etc.)
                        // Already handled at posedge in sram_op_exec -- nothing to do
                    end
                    default: begin
                        // Unknown state -- no action
                    end
                endcase
            end
        end

    end else begin : gen_cd

        // ---- CD mode: Memory & Shift Register ----
        // (mem_L, mem_R, memoryIO_L, memoryIO_R declared at module level)

        initial begin
            for (i_init = 0; i_init < DEPTH; i_init = i_init + 1) begin
                mem_L[i_init]      = INIT_TO_X ? {NB2_L{1'bx}} : {NB2_L{1'b0}};
                mem_R[i_init]      = INIT_TO_X ? {NB2_R{1'bx}} : {NB2_R{1'b0}};
                memoryIO_L[i_init] = INIT_TO_X ? {SPARE_WIDTH{1'bx}} : {SPARE_WIDTH{1'b0}};
                memoryIO_R[i_init] = INIT_TO_X ? {SPARE_WIDTH{1'bx}} : {SPARE_WIDTH{1'b0}};
            end
        end

        // ---- CD mode: mem_init task ----
        task mem_init;
            input ini_value;
            reg   ini_value;
            integer k;
        begin
            if (ini_value === 1'bx) begin
                for (k = 0; k < DEPTH; k = k + 1) begin
                    mem_L[k]      <= {NB2_L{1'bx}};
                    mem_R[k]      <= {NB2_R{1'bx}};
                    memoryIO_L[k] <= {SPARE_WIDTH{1'bx}};
                    memoryIO_R[k] <= {SPARE_WIDTH{1'bx}};
                end
            end else if (ini_value === 1'b1) begin
                for (k = 0; k < DEPTH; k = k + 1) begin
                    mem_L[k]      <= {NB2_L{1'b1}};
                    mem_R[k]      <= {NB2_R{1'b1}};
                    memoryIO_L[k] <= {SPARE_WIDTH{1'b1}};
                    memoryIO_R[k] <= {SPARE_WIDTH{1'b1}};
                end
            end else if (ini_value === 1'b0) begin
                for (k = 0; k < DEPTH; k = k + 1) begin
                    mem_L[k]      <= {NB2_L{1'b0}};
                    mem_R[k]      <= {NB2_R{1'b0}};
                    memoryIO_L[k] <= {SPARE_WIDTH{1'b0}};
                    memoryIO_R[k] <= {SPARE_WIDTH{1'b0}};
                end
            end
        end
        endtask

        // ---- CD mode: sram_op_exec task ----
        task sram_op_exec;
            integer j;
        begin
            // --- CR latch corruption (CRSxE rose since last CLK) ---
            if (cr_corrupt_pending) begin
                cr_corrupt_pending = 1'b0;
                mem_init(1'bx);
                q_fast_update = 1'b1;
                Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                if (test_mode) test_op_type = 3'd3;  // hazard/corrupt
            end else
            // --- Hazard R4/R5: CRSxE/CRSxA x/z -> all x, Q=x ---
            if ((EN_COLRED && (CRSLE_buf !== 1'b1) && (CRSLE_buf === 1'bx || CRSLE_buf === 1'bz)) ||
                (EN_COLRED && (CRSRE_buf !== 1'b1) && (CRSRE_buf === 1'bx || CRSRE_buf === 1'bz)) ||
                (EN_COLRED && (CRSLE_buf !== 1'b1) && (CRSLE_buf === 1'b1 && (^CRSLA_buf === 1'bx))) ||
                (EN_COLRED && (CRSRE_buf !== 1'b1) && (CRSRE_buf === 1'b1 && (^CRSRA_buf === 1'bx)))) begin
                mem_init(1'bx);
                q_fast_update = 1'b1;
                Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                if (test_mode) test_op_type = 3'd3;  // hazard/corrupt
            end else
            casez({WEB_eff, CEB_eff})
                    // Write Operation
                    2'b00: begin
                        if (test_mode) test_op_type = 3'd0;  // write
                        if (^A_eff === 1'bx) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                            if (test_mode) test_op_type = 3'd3;  // A=x write hazard
                        end else begin
                            // --- Column Redundancy (CD mode): left=CRSLE/CRSLA, right=CRSRE/CRSRA, independent ---
                            // Left half: up-shift (spare at MSB of left). Right half: down-shift (spare at LSB of right).
                            // Each half handled separately; both can be active simultaneously.
                            begin : cd_cr_wr
                                integer a_l, a_r;
                                integer bw_idx_l, bw_idx_r;
                                integer gs, g_l, g_r, sk;
                                gs = SPARE_WIDTH;
                                a_l = crsle_eff ? CRSLA : -1;  // use live port value (MBIST shift fix)
                                a_r = crsre_eff ? CRSRA : -1;  // use live port value (MBIST shift fix)
                                // --- Left mem ---
                                if (a_l >= 0) begin
                                    g_l = a_l / gs;
                                    // spare = D[NB2_L-gs .. NB2_L-1] (left mem's MSB group)
                                    for (sk = 0; sk < gs; sk = sk + 1) begin
                                        if (BWEB_eff[NB2_L - gs + sk] === 1'b0)
                                            memoryIO_L[A_eff][sk] = (D_eff[NB2_L - gs + sk] === 1'bx || D_eff[NB2_L - gs + sk] === 1'bz) ? 1'bx : D_eff[NB2_L - gs + sk];
                                    end
                                    CRWriteUpShift(a_l, NB2_L, D_eff, mem_L[A_eff]);
                                    // BWEB mapping: physical mem<j> stores D<j> (j<g_l*gs), skip (defect group),
                                    //   D<j-gs> (j>=g_l*gs+gs).
                                    for (j = 0; j < NB2_L; j = j + 1) begin
                                        if (j >= g_l*gs && j <= g_l*gs + gs - 1) begin
                                            // Defective group: write X (skipped)
                                            mem_L[A_eff][j] = 1'bx;
                                        end else begin
                                            if (j < g_l*gs)
                                                bw_idx_l = j;            // mem<j> = D<j>
                                            else
                                                bw_idx_l = j - gs;       // mem<j> = D<j-gs>
                                            if (bw_idx_l >= 0 && bw_idx_l < NB2_L &&
                                                BWEB_eff[bw_idx_l] === 1'b0)
                                                mem_L[A_eff][j] = (colred_write_result[j] === 1'bx || colred_write_result[j] === 1'bz) ? 1'bx : colred_write_result[j];
                                            else if (bw_idx_l >= 0 && bw_idx_l < NB2_L &&
                                                     (BWEB_eff[bw_idx_l] === 1'bx || BWEB_eff[bw_idx_l] === 1'bz))
                                                mem_L[A_eff][j] = 1'bx;  // hazard R11
                                        end
                                    end
                                end else begin
                                    for (j = 0; j < NB2_L; j = j + 1) begin
                                        if (BWEB_eff[j] === 1'b0)
                                            mem_L[A_eff][j] = (D_eff[j] === 1'bx || D_eff[j] === 1'bz) ? 1'bx : D_eff[j];
                                        else if (BWEB_eff[j] === 1'bx || BWEB_eff[j] === 1'bz)
                                            mem_L[A_eff][j] = 1'bx;  // hazard R11
                                    end
                                end
                                // --- Right mem ---
                                if (a_r >= 0) begin
                                    g_r = a_r / gs;
                                    // spare = D[NB2_L .. NB2_L+gs-1] (right mem's local IO<0..gs-1> = global IO<NB2_L..NB2_L+gs-1>)
                                    for (sk = 0; sk < gs; sk = sk + 1) begin
                                        if (BWEB_eff[NB2_L + sk] === 1'b0)
                                            memoryIO_R[A_eff][sk] = (D_eff[NB2_L + sk] === 1'bx || D_eff[NB2_L + sk] === 1'bz) ? 1'bx : D_eff[NB2_L + sk];
                                    end
                                    // Compress: right-mem local data = D_eff >> NB2_L (placed at [NB2_R-1:0])
                                    CRWriteDownShift(a_r, NB2_R, D_eff >> NB2_L, mem_R[A_eff]);
                                    // BWEB mapping: physical mem<j> stores local IO<j+gs> (j<g_r*gs) or IO<j> (j>=g_r*gs+gs).
                                    //   Global BWEB index = NB2_L + local_IO.
                                    for (j = 0; j < NB2_R; j = j + 1) begin
                                        if (j >= g_r*gs && j <= g_r*gs + gs - 1) begin
                                            // Defective group: write X (not skipped)
                                            mem_R[A_eff][j] = 1'bx;
                                        end else begin
                                            if (j < g_r*gs)
                                                bw_idx_r = NB2_L + j + gs;   // mem<j> = D<j+gs>, check BWEB<j+gs>
                                            else
                                                bw_idx_r = NB2_L + j;       // mem<j> = D<j>, check BWEB<j>
                                            if (bw_idx_r >= 0 && bw_idx_r < DATA_WIDTH &&
                                                BWEB_eff[bw_idx_r] === 1'b0)
                                                mem_R[A_eff][j] = (colred_write_result[j] === 1'bx || colred_write_result[j] === 1'bz) ? 1'bx : colred_write_result[j];
                                            else if (bw_idx_r >= 0 && bw_idx_r < DATA_WIDTH &&
                                                     (BWEB_eff[bw_idx_r] === 1'bx || BWEB_eff[bw_idx_r] === 1'bz))
                                                mem_R[A_eff][j] = 1'bx;  // hazard R11
                                        end
                                    end
                                end else begin
                                    for (j = 0; j < NB2_R; j = j + 1) begin
                                        if (BWEB_eff[NB2_L + j] === 1'b0)
                                            mem_R[A_eff][j] = (D_eff[NB2_L + j] === 1'bx || D_eff[NB2_L + j] === 1'bz) ? 1'bx : D_eff[NB2_L + j];
                                        else if (BWEB_eff[NB2_L + j] === 1'bx || BWEB_eff[NB2_L + j] === 1'bz)
                                            mem_R[A_eff][j] = 1'bx;  // hazard R11
                                    end
                                end
                            end
                            q_fast_update = 1'b1;
                            // Write only stores to mem; Q keeps previous value
                        end
                    end

                    // Read Operation
                    2'b10: begin
                        if (test_mode) test_op_type = 3'd1;  // read
                        if (^A_eff === 1'bx) begin
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)  // A=x/z read: Q=X (hazard R8)
                            if (test_mode) test_op_type = 3'd3;  // A=x read hazard
                        end else begin
                            // --- Column Redundancy (CD mode): left=CRSLE/CRSLA up-shift, right=CRSRE/CRSRA down-shift ---
                            begin : cd_cr_rd_outer
                                reg [DATA_WIDTH-1:0] rd_l_full, rd_r_full;
                                reg [DATA_WIDTH-1:0] fi_l, fi_r;
                                integer a_l, a_r;
                                a_l = crsle_eff ? CRSLA : -1;  // use live port value (MBIST shift fix)
                                a_r = crsre_eff ? CRSRA : -1;  // use live port value (MBIST shift fix)
                                // Fault injection on raw mem data before CR shift.
                                // CD: mem_L = low nibble [NB2_L-1:0], mem_R = high nibble [NB2_R-1:0].
                                // Pad mem_L to low position, mem_R to high position of DATA_WIDTH word.
                                fi_l = apply_fi({{(DATA_WIDTH-NB2_L){1'b0}}, mem_L[A_eff]}, A_eff);
                                fi_r = apply_fi({mem_R[A_eff], {(DATA_WIDTH-NB2_R){1'b0}}}, A_eff);
                                if (crsle_eff || crsre_eff) begin
                                    // Left half: up-shift (spare at MSB of left)
                                    CRReadUpShift(a_l, NB2_L, fi_l[NB2_L-1:0], memoryIO_L[A_eff]);
                                    rd_l_full = colred_read_result;
                                    // Right half: down-shift (spare at LSB of right)
                                    CRReadDownShift(a_r, NB2_R, fi_r[DATA_WIDTH-1:DATA_WIDTH-NB2_R], memoryIO_R[A_eff]);
                                    rd_r_full = colred_read_result;
                                    Q_tmp = {rd_r_full[NB2_R-1:0], rd_l_full[NB2_L-1:0]};
                                end else begin
                                    Q_tmp = {fi_r[DATA_WIDTH-1:DATA_WIDTH-NB2_R], fi_l[NB2_L-1:0]};
                                end
                            end
                            if (test_mode) begin
                                // TEST mode: store for negedge output (Q updates at negedge + tcdt)
                                test_read_data = Q_tmp;
                            end else begin
                                Q_r <= Q_tmp;  // Normal read
                                Q_force_x <= 1'b0;   // clear force-x
                            end
                            q_fast_update = 1'b1;
                        end
                    end

                    // Chip Unselect (CEB=1): Q holds previous value
                    2'b01, 2'b11, 2'bx1: begin
                        if (test_mode) test_op_type = 3'd2;  // deselect
                        q_fast_update = 1'b1;
                    end

                    // x/z on CEB or WEB -> memory corruption
                    // x/z on CEB or WEB -> all x (hazard R6/R7)
                    2'bxx, 2'b1x, 2'b0x, 2'bx0: begin
                        if (test_mode) test_op_type = 3'd3;  // hazard/corrupt
                        if (eff_clk === 1'b1) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                        end
                    end
                endcase
        end
        endtask

        // ---- CD mode: timing_check task ----
        task timing_check;
            integer i;
            integer has_violation_flag;
        begin
            // --- CR timing flags: clear and re-check this cycle ---
            // tcrac/tcrca: CRSxA setup/hold vs CLK?
            // tcrec/tcrce: CRSxE setup/hold vs CLK?
            tcrac_v_l = 1'b0; tcrac_v_r = 1'b0;
            tcrca_v_l = 1'b0; tcrca_v_r = 1'b0;
            tcrec_v_l = 1'b0; tcrec_v_r = 1'b0;
            tcrce_v_l = 1'b0; tcrce_v_r = 1'b0;
            // --- TEST mode ttons/ttofs: clear and re-check (one-shot) ---
            ttons_violation = 1'b0;
            ttofs_violation = 1'b0;
            if (ttons_pending && test_mode) begin
                ttons_pending = 1'b0;
                if (test_rise_time > 0 && ($realtime - test_rise_time) < ttons && ttons > 0) begin
                    ttons_violation = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m ttons violation (TEST? to CLK?) at %t (interval=%0t, required=%0t)", $realtime, $realtime - test_rise_time, ttons);
                    `endif
                end
            end
            if (ttofs_pending && !test_mode) begin
                ttofs_pending = 1'b0;
                if (test_fall_time > 0 && ($realtime - test_fall_time) < ttofs && ttofs > 0) begin
                    ttofs_violation = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m ttofs violation (TEST? to CLK?) at %t (interval=%0t, required=%0t)", $realtime, $realtime - test_fall_time, ttofs);
                    `endif
                end
            end
            if (EN_COLRED) begin
                // CRSxE setup vs CLK? (tcrec): check if CRSxE changed within tcrec
                if (tcrec > 0 && CRSLE_change_time > 0 && last_ck_rise > 0 &&
                    ($realtime - CRSLE_change_time) < tcrec)
                    tcrec_v_l = 1'b1;
                if (tcrec > 0 && CRSRE_change_time > 0 && last_ck_rise > 0 &&
                    ($realtime - CRSRE_change_time) < tcrec)
                    tcrec_v_r = 1'b1;
                // CRSxE hold vs CLK? (tcrce): check if CRSxE changed within tcrce after CLK?
                // Uses prev_ck_rise (last CLK?) because last_ck_rise is already updated
                // to current posedge by the time timing_check runs.
                if (tcrce > 0 && CRSLE_change_time > 0 && prev_ck_rise > 0 &&
                    (CRSLE_change_time > prev_ck_rise) &&
                    (CRSLE_change_time - prev_ck_rise) < tcrce)
                    tcrce_v_l = 1'b1;
                if (tcrce > 0 && CRSRE_change_time > 0 && prev_ck_rise > 0 &&
                    (CRSRE_change_time > prev_ck_rise) &&
                    (CRSRE_change_time - prev_ck_rise) < tcrce)
                    tcrce_v_r = 1'b1;
                // CRSxA setup vs CLK? (tcrac): per-bit, any bit changed within tcrac
                for (tcr_i = 0; tcr_i < CR_ADDR_WIDTH; tcr_i = tcr_i + 1) begin
                    if (tcrac > 0 && CRSLA_change_time[tcr_i] > 0 && last_ck_rise > 0 &&
                        ($realtime - CRSLA_change_time[tcr_i]) < tcrac)
                        tcrac_v_l = 1'b1;
                    if (tcrac > 0 && CRSRA_change_time[tcr_i] > 0 && last_ck_rise > 0 &&
                        ($realtime - CRSRA_change_time[tcr_i]) < tcrac)
                        tcrac_v_r = 1'b1;
                end
                // CRSxA hold vs CLK? (tcrca): per-bit, any bit changed within tcrca after CLK?
                // Uses prev_ck_rise (last CLK?) because last_ck_rise is already updated
                // to current posedge by the time timing_check runs.
                for (tcr_i = 0; tcr_i < CR_ADDR_WIDTH; tcr_i = tcr_i + 1) begin
                    if (tcrca > 0 && CRSLA_change_time[tcr_i] > 0 && prev_ck_rise > 0 &&
                        (CRSLA_change_time[tcr_i] > prev_ck_rise) &&
                        (CRSLA_change_time[tcr_i] - prev_ck_rise) < tcrca)
                        tcrca_v_l = 1'b1;
                    if (tcrca > 0 && CRSRA_change_time[tcr_i] > 0 && prev_ck_rise > 0 &&
                        (CRSRA_change_time[tcr_i] > prev_ck_rise) &&
                        (CRSRA_change_time[tcr_i] - prev_ck_rise) < tcrca)
                        tcrca_v_r = 1'b1;
                end
            end

`ifdef TIMING_DEBUG
            // Clear per-cycle violation flags at start of each evaluation
            dbg_violation          = 1'b0;
            dbg_violation_type     = 4'd0;
            dbg_setup_violation    = 1'b0;
            dbg_hold_violation     = 1'b0;
            dbg_A_violation        = 1'b0;
            dbg_D_violation        = 1'b0;
            dbg_CEB_violation      = 1'b0;
            dbg_WEB_violation      = 1'b0;
            dbg_BWEB_violation     = 1'b0;
            dbg_ck_violation       = 1'b0;
            dbg_tsclk2op_violation = 1'b0;
            dbg_tsclk2op_margin    = 0.0;
`endif
            // Clock period/width violation
            if (tviol_CK_PER !== prev_tviol_CK_PER ||
                tviol_CK_MINH !== prev_tviol_CK_MINH ||
                tviol_CK_MINL !== prev_tviol_CK_MINL) begin
                if (test_mode) begin
                    // TEST mode: flag for negedge adjudication (no immediate corrupt)
                    test_violation_clk = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_VIOLATION: %m Clock period/width violation (TEST mode) at %t -- flagged", $realtime);
                    dbg_violation = 1'b1;
                    dbg_violation_type = 4'd1;
                    dbg_ck_violation = 1'b1;
                    dbg_ck_violations = dbg_ck_violations + 1;
                    dbg_total_violations = dbg_total_violations + 1;
                    `endif
                    // Still pre-write via sram_op_exec (Q1:C posedge pre-write)
                    A_eff    = samp_A;
                    D_eff    = samp_D;
                    CEB_eff  = samp_CEB;
                    WEB_eff  = samp_WEB;
                    BWEB_eff = samp_BWEB;
                    sram_op_exec;
                end else if (CEB_buf !== 1'b1) begin
                    `ifdef TIMING_DEBUG
                    $display("TIMING_VIOLATION: %m Clock period/width violation at %t -- mem=all X, Q=X", $realtime);
                    dbg_violation = 1'b1;
                    dbg_violation_type = 4'd1;
                    dbg_ck_violation = 1'b1;
                    dbg_ck_violations = dbg_ck_violations + 1;
                    dbg_total_violations = dbg_total_violations + 1;
                    `endif
                    mem_init(1'bx);
                    q_fast_update = 1'b1;
                    Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                end
            end
            // Clock valid -- check signal setup/hold violations + CR R/W period
            else begin
                has_violation_flag = 0;

                // --- CR mode R/W period check (tcrhold_rw) ---
                // In CR mode (CRSxE=1), every R/W cycle must satisfy
                // tcrhold_rw (min CLK period). Violation -> Q/MEM = X.
                // Skip during cr_corrupt_pending (CRSxE edge cycle, not a real R/W).
                if (EN_COLRED && !cr_corrupt_pending &&
                    ((CRSLE_buf === 1'b1) || (CRSRE_buf === 1'b1)) &&
                    tcrhold_rw > 0 && prev_ck_rise > 0 &&
                    ($realtime - prev_ck_rise) < tcrhold_rw) begin
                    cr_rw_violation = 1'b1;
                    `ifdef TIMING_DEBUG
                    $display("TIMING_DEBUG: %m tcrhold_rw violation at %t (period=%0t, required=%0t)", $realtime, $realtime - prev_ck_rise, tcrhold_rw);
                    `endif
                end

                for (i = 0; i < ADDR_WIDTH; i = i + 1) begin
                    if (tviol_A[i] !== prev_tviol_A[i]) begin
                        if (!test_mode) samp_A[i] = 1'bx;  // TEST mode: keep actual value for pre-write
                        has_violation_flag = 1;
`ifdef TIMING_DEBUG
                        dbg_A_violation = 1'b1;
`endif
                    end
                end
                for (i = 0; i < DATA_WIDTH; i = i + 1) begin
                    if (tviol_D[i] !== prev_tviol_D[i]) begin
                        if (!test_mode) samp_D[i] = 1'bx;
                        has_violation_flag = 1;
`ifdef TIMING_DEBUG
                        dbg_D_violation = 1'b1;
`endif
                    end
                end
                if (tviol_CEB !== prev_tviol_CEB) begin
                    if (!test_mode) samp_CEB = 1'bx;
                    has_violation_flag = 1;
`ifdef TIMING_DEBUG
                    dbg_CEB_violation = 1'b1;
`endif
                end
                if (tviol_WEB !== prev_tviol_WEB) begin
                    if (!test_mode) samp_WEB = 1'bx;
                    has_violation_flag = 1;
`ifdef TIMING_DEBUG
                    dbg_WEB_violation = 1'b1;
`endif
                end
                for (i = 0; i < DATA_WIDTH; i = i + 1) begin
                    if (tviol_BWEB[i] !== prev_tviol_BWEB[i]) begin
                        if (!test_mode) samp_BWEB[i] = 1'bx;
                        has_violation_flag = 1;
`ifdef TIMING_DEBUG
                        dbg_BWEB_violation = 1'b1;
`endif
                    end
                end
                for (i = 0; i < CR_ADDR_WIDTH; i = i + 1) begin
                    if (tviol_CRSLA[i] !== prev_tviol_CRSLA[i] ||
                        tviol_CRSRA[i] !== prev_tviol_CRSRA[i]) begin
                        has_violation_flag = 1;
                        $display("WARNING: %m CRSxA setup/hold timing violation at %t -- R/W result = X", $realtime);
                    end
                end

                if (test_mode) begin
                    // TEST mode: flag violation, always pre-write via sram_op_exec
                    if (has_violation_flag || ttons_violation || ttofs_violation || tcrac_v_l || tcrac_v_r || tcrca_v_l || tcrca_v_r || tcrec_v_l || tcrec_v_r || tcrce_v_l || tcrce_v_r || cr_rw_violation) begin
                        test_violation_pos = 1'b1;
                        `ifdef TIMING_DEBUG
                        $display("TIMING_VIOLATION: %m Setup/hold/ttons/ttofs violation (TEST mode) at %t -- flagged", $realtime);
                        dbg_violation = 1'b1;
                        dbg_violation_type = 4'd4;
                        if (dbg_A_setup_margin < 0 || dbg_D_setup_margin < 0 ||
                            dbg_CEB_setup_margin < 0 || dbg_WEB_setup_margin < 0 ||
                            dbg_BWEB_setup_margin < 0)
                            dbg_setup_violation = 1'b1;
                        if (dbg_A_hold_margin < 0 || dbg_D_hold_margin < 0 ||
                            dbg_CEB_hold_margin < 0 || dbg_WEB_hold_margin < 0 ||
                            dbg_BWEB_hold_margin < 0)
                            dbg_hold_violation = 1'b1;
                        if (dbg_setup_violation)
                            dbg_setup_violations = dbg_setup_violations + 1;
                        if (dbg_hold_violation)
                            dbg_hold_violations = dbg_hold_violations + 1;
                        dbg_total_violations = dbg_total_violations + 1;
                        `endif
                    end
                    // Pre-write with actual latched values (not corrupted)
                    A_eff    = samp_A;
                    D_eff    = samp_D;
                    CEB_eff  = samp_CEB;
                    WEB_eff  = samp_WEB;
                    BWEB_eff = samp_BWEB;
                    sram_op_exec;
                end else if (has_violation_flag || ttofs_violation || tcrac_v_l || tcrac_v_r || tcrca_v_l || tcrca_v_r || tcrec_v_l || tcrec_v_r || tcrce_v_l || tcrce_v_r || cr_rw_violation) begin
                    // Normal mode: Timing violation detected -> directly fail: Q=X
                    `ifdef TIMING_DEBUG
                    $display("TIMING_VIOLATION: %m Setup/hold violation at %t -- Q forced to X", $realtime);
                    dbg_violation = 1'b1;
                    dbg_violation_type = 4'd4;
                    if (dbg_A_setup_margin < 0 || dbg_D_setup_margin < 0 ||
                        dbg_CEB_setup_margin < 0 || dbg_WEB_setup_margin < 0 ||
                        dbg_BWEB_setup_margin < 0)
                        dbg_setup_violation = 1'b1;
                    if (dbg_A_hold_margin < 0 || dbg_D_hold_margin < 0 ||
                        dbg_CEB_hold_margin < 0 || dbg_WEB_hold_margin < 0 ||
                        dbg_BWEB_hold_margin < 0)
                        dbg_hold_violation = 1'b1;
                    if (dbg_setup_violation)
                        dbg_setup_violations = dbg_setup_violations + 1;
                    if (dbg_hold_violation)
                        dbg_hold_violations = dbg_hold_violations + 1;
                    dbg_total_violations = dbg_total_violations + 1;
                    `endif
                    q_fast_update = 1'b1;
                    Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)

                    // If operation could be a write, also corrupt memory
                    if (CEB_buf !== 1'b1) begin
                        if (WEB_buf === 1'b0) begin
                            // Write operation -> corrupt target address
                            if (^A_buf !== 1'bx) begin
                                for (i = 0; i < NB2_L; i = i + 1)
                                    mem_L[A_buf][i] = 1'bx;
                                for (i = 0; i < NB2_R; i = i + 1)
                                    mem_R[A_buf][i] = 1'bx;
                                memoryIO_L[A_buf] = {SPARE_WIDTH{1'bx}};
                                memoryIO_R[A_buf] = {SPARE_WIDTH{1'bx}};
                            end else
                                mem_init(1'bx);
                        end else if (WEB_buf !== 1'b1) begin
                            // WEB unknown (x/z) -> worst case, corrupt all
                            mem_init(1'bx);
                        end
                        // Read operation (WEB_buf=1): only Q=X, memory intact
                    end
                end else begin
                    // No violations -- normal operation through sram_op_exec
                    A_eff    = samp_A;
                    D_eff    = samp_D;
                    CEB_eff  = samp_CEB;
                    WEB_eff  = samp_WEB;
                    BWEB_eff = samp_BWEB;

                    sram_op_exec;
                end
            end

            prev_tviol_A       = tviol_A;
            prev_tviol_D       = tviol_D;
            prev_tviol_CEB     = tviol_CEB;
            prev_tviol_WEB     = tviol_WEB;
            prev_tviol_BWEB    = tviol_BWEB;
            prev_tviol_CRSLA   = tviol_CRSLA;
            prev_tviol_CRSRA   = tviol_CRSRA;
            prev_tviol_CK_PER  = tviol_CK_PER;
            prev_tviol_CK_MINH = tviol_CK_MINH;
            prev_tviol_CK_MINL = tviol_CK_MINL;
        end
        endtask

        // ---- CD mode: Main Clock Block ----
        always @(posedge eff_clk) begin
            if ($realtime != 0) begin
                // Clear TEST mode violation flags at start of each cycle
                if (test_mode) begin
                    test_violation_pos = 1'b0;
                    test_violation_clk = 1'b0;
        cr_rw_violation    = 1'b0;
                end
                if (CLK_buf === 1'bx || CLK_buf === 1'bz) begin
                    mem_init(1'bx);
                    q_fast_update = 1'b1;
                    Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                end else begin
                    timing_check;
                end
            end
        end

         // ---- CD mode: TEST Mode Negedge Adjudication Block ----
         // (per Q1:C, Q13:A: posedge pre-writes + flags, negedge adjudicates)
         always @(negedge eff_clk) begin
            if (test_mode && $realtime != 0) begin
                // Check CLK high width violation directly (tckhtw/tckhtr)
                case (test_op_type)
                    3'd0: begin
                        // Write: check tckhtw
                        if (tckhtw > 0 && ($realtime - last_ck_rise) < tckhtw)
                            test_violation_clk = 1'b1;
                    end
                    3'd1: begin
                        // Read: check tckhtr
                        if (tckhtr > 0 && ($realtime - last_ck_rise) < tckhtr)
                            test_violation_clk = 1'b1;
                    end
                    default: ;
                endcase

                // Adjudicate based on operation type and violation flags
                case (test_op_type)
                    3'd0: begin
                        // Write operation
                        // Q11:B: any violation -> mem = all X
                        if (test_violation_clk || test_violation_pos) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                        end
                        // No violation: mem retains pre-written value (from posedge)
                    end
                    3'd1: begin
                        // Read operation
                        // Q14:A: any violation -> Q = X
                        // Also check cr_corrupt_pending: CRSxE edge between
                        // posedge and negedge invalidates pre-captured data.
                        if (test_violation_clk || test_violation_pos || cr_corrupt_pending) begin
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                        end else begin
                            // No violation: Q outputs at negedge + tcdt
                            // (v12.4: tcdt delay now via assign #(tcd) Q_normal, not Q_r NBA)
                            Q_r <= test_read_data;
                            Q_force_x <= 1'b0;   // clear force-x
                        end
                        q_fast_update = 1'b1;
                    end
                    3'd2: begin
                        // Deselect (CEB=1)
                        // Q12:B: clock-level violation -> all mem = X, Q = X
                        //         setup/hold violation -> no consequence
                        if (test_violation_clk) begin
                            mem_init(1'bx);
                            q_fast_update = 1'b1;
                            Q_r <= {DATA_WIDTH{1'bx}};
                Q_force_x <= 1'b1;  // force Q to X immediately (bypass tcd)
                        end
                        // No clock violation: Q holds, mem unchanged
                    end
                    3'd3: begin
                        // Hazard/corrupt (CLK=x, CEB=x, WEB=x, A=x, etc.)
                        // Already handled at posedge in sram_op_exec -- nothing to do
                    end
                    default: begin
                        // Unknown state -- no action
                    end
                endcase
            end
        end

    end endgenerate


    // ========================================================================
    // Specify block condition wires: split setup/hold into normal vs CR shift
    // (specify &&& requires net expressions; specparam must be constant, so we
    //  use two $setuphold pairs with mutually exclusive conditions.)
    // ========================================================================
    wire cond_A_normal   = gate_A   && !cr_shift_active;
    wire cond_A_cr       = gate_A   && cr_shift_active;
    wire cond_D_normal   = gate_D   && !cr_shift_active;
    wire cond_D_cr       = gate_D   && cr_shift_active;
    wire cond_WEB_normal = gate_WEB && !cr_shift_active;
    wire cond_WEB_cr     = gate_WEB && cr_shift_active;
    wire cond_CEB_normal = gate_CEB && !cr_shift_active;
    wire cond_CEB_cr     = gate_CEB && cr_shift_active;

    // ========================================================================
    // Output: Q updates synchronously on posedge eff_clk (via NBA Q_r <= Q_tmp).
    // No event-driven delay needed.
    // ========================================================================

    // ========================================================================
    // Specify Block (optional -- enabled with +define+TIMING_CHECK_SPECIFY)
    // ========================================================================
`ifdef TIMING_CHECK_SPECIFY
    specify
        specparam tas_s  = tas;
        specparam tah_s  = tah;
        specparam tds_s  = tds;
        specparam tdh_s  = tdh;
        specparam tcs_s = tcs;
        specparam tch_s = tch;
        specparam tws_s  = tws;
        specparam twh_s  = twh;
        specparam tbws_s = tbws;
        specparam tbwh_s = tbwh;
        specparam tcrac_s = tcrac;
        specparam tcrca_s = tcrca;
        specparam tcrec_s = tcrec;
        specparam tcrce_s = tcrce;
        specparam tckh_s = tckh;
        specparam tckl_s = tckl;
        specparam tcyc_s = tcyc;
        specparam tcd_s  = tcd;
        specparam thold_s  = thold;
        // CR shift mode timing params (mirror of tr* parameters)
        specparam tras_s  = tras;
        specparam trah_s  = trah;
        specparam trws_s  = trws;
        specparam trwh_s  = trwh;
        specparam trbws_s = trbws;
        specparam trbwh_s = trbwh;
        specparam trds_s  = trds;
        specparam trdh_s  = trdh;
        specparam trcd_s  = trcd;
        specparam trhold_s = trhold;
        specparam trcs_s  = trcs;
        specparam trch_s  = trch;
        specparam trcdt_s = trcdt;

        // Address setup/hold -- normal mode (t* params)
        genvar si;
        for (si = 0; si < ADDR_WIDTH; si = si + 1) begin : spec_A
            $setuphold (posedge eff_clk &&& cond_A_normal, posedge A[si], tas_s, tah_s, tviol_A[si]);
            $setuphold (posedge eff_clk &&& cond_A_normal, negedge A[si], tas_s, tah_s, tviol_A[si]);
            // Address setup/hold -- CR shift mode (tr* params)
            $setuphold (posedge eff_clk &&& cond_A_cr, posedge A[si], tras_s, trah_s, tviol_A[si]);
            $setuphold (posedge eff_clk &&& cond_A_cr, negedge A[si], tras_s, trah_s, tviol_A[si]);
        end

        // Data setup/hold -- normal + CR shift
        for (si = 0; si < DATA_WIDTH; si = si + 1) begin : spec_D
            $setuphold (posedge eff_clk &&& cond_D_normal, posedge D[si], tds_s, tdh_s, tviol_D[si]);
            $setuphold (posedge eff_clk &&& cond_D_normal, negedge D[si], tds_s, tdh_s, tviol_D[si]);
            $setuphold (posedge eff_clk &&& cond_D_cr, posedge D[si], trds_s, trdh_s, tviol_D[si]);
            $setuphold (posedge eff_clk &&& cond_D_cr, negedge D[si], trds_s, trdh_s, tviol_D[si]);
        end

        // CEB setup/hold -- normal + CR shift (v12.5: added CR shift variant)
        $setuphold (posedge eff_clk &&& cond_CEB_normal, posedge CEB, tcs_s, tch_s, tviol_CEB);
        $setuphold (posedge eff_clk &&& cond_CEB_normal, negedge CEB, tcs_s, tch_s, tviol_CEB);
        $setuphold (posedge eff_clk &&& cond_CEB_cr, posedge CEB, trcs_s, trch_s, tviol_CEB);
        $setuphold (posedge eff_clk &&& cond_CEB_cr, negedge CEB, trcs_s, trch_s, tviol_CEB);

        // WEB setup/hold -- normal + CR shift
        $setuphold (posedge eff_clk &&& cond_WEB_normal, posedge WEB, tws_s, twh_s, tviol_WEB);
        $setuphold (posedge eff_clk &&& cond_WEB_normal, negedge WEB, tws_s, twh_s, tviol_WEB);
        $setuphold (posedge eff_clk &&& cond_WEB_cr, posedge WEB, trws_s, trwh_s, tviol_WEB);
        $setuphold (posedge eff_clk &&& cond_WEB_cr, negedge WEB, trws_s, trwh_s, tviol_WEB);

        // BWEB setup/hold (per-bit, active during write) -- normal + CR shift
        for (si = 0; si < DATA_WIDTH; si = si + 1) begin : spec_BWEB
            $setuphold (posedge eff_clk &&& cond_D_normal, posedge BWEB[si], tbws_s, tbwh_s, tviol_BWEB[si]);
            $setuphold (posedge eff_clk &&& cond_D_normal, negedge BWEB[si], tbws_s, tbwh_s, tviol_BWEB[si]);
            $setuphold (posedge eff_clk &&& cond_D_cr, posedge BWEB[si], trbws_s, trbwh_s, tviol_BWEB[si]);
            $setuphold (posedge eff_clk &&& cond_D_cr, negedge BWEB[si], trbws_s, trbwh_s, tviol_BWEB[si]);
        end

        // CRSxA setup vs CRSxE posedge (tcrae) + hold vs CRSxE negedge (tcrea)
        // Split from $setuphold because setup references posedge and hold
        // references negedge (different edges).
        for (si = 0; si < CR_ADDR_WIDTH; si = si + 1) begin : spec_CRSLA
            $setuphold (posedge eff_clk &&& gate_CR, posedge CRSLA[si], tcrac_s, tcrca_s, tviol_CRSLA[si]);
            $setuphold (posedge eff_clk &&& gate_CR, negedge CRSLA[si], tcrac_s, tcrca_s, tviol_CRSLA[si]);
        end
        for (si = 0; si < CR_ADDR_WIDTH; si = si + 1) begin : spec_CRSRA
            $setuphold (posedge eff_clk &&& gate_CR, posedge CRSRA[si], tcrac_s, tcrca_s, tviol_CRSRA[si]);
            $setuphold (posedge eff_clk &&& gate_CR, negedge CRSRA[si], tcrac_s, tcrca_s, tviol_CRSRA[si]);
        end

        // CRSxE setup/hold vs CLK? (tcrec/tcrce)
        $setuphold (posedge eff_clk &&& gate_CR, posedge CRSLE, tcrec_s, tcrce_s, tviol_CEB);  // reuse tviol
        $setuphold (posedge eff_clk &&& gate_CR, negedge CRSLE, tcrec_s, tcrce_s, tviol_CEB);
        $setuphold (posedge eff_clk &&& gate_CR, posedge CRSRE, tcrec_s, tcrce_s, tviol_WEB);
        $setuphold (posedge eff_clk &&& gate_CR, negedge CRSRE, tcrec_s, tcrce_s, tviol_WEB);

        // Clock width/period
        $width     (posedge eff_clk, tckh_s, 0, tviol_CK_MINH);
        $width     (negedge eff_clk, tckl_s, 0, tviol_CK_MINL);
        $period    (posedge eff_clk, tcyc_s, tviol_CK_PER);

        // Output timing paths -- normal (tcd/thold) + CR shift (trcd/trhold)
        // (v12.5: CR shift path now uses trhold_s instead of thold_s;
        //  TEST+CR path uses trcdt_s/trhold_s. specify path timing is
        //  posedge-referenced for all modes; TEST mode Q actually updates at
        //  negedge via Q_r NBA, so the posedge=>Q path here is a conservative
        //  upper-bound model. Behavioral assign #(trcdt) Q_test_cr provides
        //  the accurate negedge-referenced delay.)
        genvar qi;
        for (qi = 0; qi < DATA_WIDTH; qi = qi + 1) begin : spec_Q
            if (!CEB && WEB && !q_fast_update && !cr_shift_active && !test_mode)
                (posedge eff_clk => (Q[qi] : 1'bx)) = (tcd_s, tcd_s, thold_s, tcd_s, thold_s, tcd_s);
            if (!CEB && WEB && !q_fast_update && cr_shift_active && !test_mode)
                (posedge eff_clk => (Q[qi] : 1'bx)) = (trcd_s, trcd_s, trhold_s, trcd_s, trhold_s, trcd_s);
            if (!CEB && WEB && !q_fast_update && !cr_shift_active && test_mode)
                (posedge eff_clk => (Q[qi] : 1'bx)) = (tcd_s, tcd_s, thold_s, tcd_s, thold_s, tcd_s);
            if (!CEB && WEB && !q_fast_update && cr_shift_active && test_mode)
                (posedge eff_clk => (Q[qi] : 1'bx)) = (trcdt_s, trcdt_s, trhold_s, trcdt_s, trhold_s, trcdt_s);
        end
    endspecify
`endif

endmodule

`ifdef CELL_DEFINE
`endcelldefine
`endif
