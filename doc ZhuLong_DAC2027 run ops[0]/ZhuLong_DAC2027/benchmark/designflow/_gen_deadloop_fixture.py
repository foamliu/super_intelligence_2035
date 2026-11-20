#!/usr/bin/env python3
"""Generate synthesized SystemVerilog bind fixtures for DeadLoopScan-001.

Fixture A reproduces the gold loop structure from real trace
1792042618272_wl9i4 (xingx) msg [751]: 2827 lines, 92 forever (intentional
monitor threads), 2 bounded for (ref_cnt<4) at L2751/L2788, 4 while at
L156/L612/L2719/L2727, 2 do-while at L2711/L2714, 2 repeat. Dead-loop
candidates: L156/L612 (CMD_CAL_CHK busy-wait), L2719 (zero-delay spin on
vif.group), L2727 (do-while on VintCompEn_watch_dog).

Fixture B (hidden) is structurally different: 3105 lines, 68 forever, 3 for
(one UNBOUNDED for(;;) -> dead loop), 5 while, 3 do, 1 repeat. Dead-loop
candidates at L204/L880/L2940/L3050 with different patterns + an infinite
for(;;) (not present in A) to test cross-input generalization.
"""
import os, random

random.seed(20261103)

OUT_DIR_A = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/EDA-Eval-DesignFlow-DeadLoopScan-001"
OUT_DIR_B_HIDDEN = os.path.join(OUT_DIR_A, "hidden")
os.makedirs(OUT_DIR_A, exist_ok=True)
os.makedirs(OUT_DIR_B_HIDDEN, exist_ok=True)

# ---------- helpers ----------
def make_forever_monitor(idx):
    """A realistic monitor/driver thread with a forever loop (intentional)."""
    name = f"mon_task_{idx:02d}"
    sig = random.choice(["cmd_string","group","vif.dse","clk_gate_en","vintCompEn",
                         "adj_vbnvbp_pre_dv","limiter_adj_code_dv","ref_cnt","state",
                         "cmd_state","watch_dog","vif.req","vif.ack","dldo_mon.vif"])
    return [
        f"task automatic {name}(ref dldo_if_t vif);",
        "  forever begin",
        f"    @(vif.{sig});",
        f"    if (vif.{sig} !== 1'bz) begin",
        f"      // monitor sample {idx}",
        f"      _log_{idx}.push_back(vif.{sig});",
        "    end",
        "  end",
        "endtask",
    ]

def make_filler(idx):
    """Realistic-ish SV filler lines (declarations, assignments, comments)."""
    style = idx % 7
    if style == 0:
        return f"  logic [31:0] sig_{idx:04d}; // internal net"
    elif style == 1:
        return f"  assign sig_{idx:04d} = state_q & enable_i;"
    elif style == 2:
        return f"  // bind coverage point {idx}: dldo domain monitor"
    elif style == 3:
        return f"  always @(posedge clk_i) sig_{idx:04d} <= sig_{(idx-1):04d} ^ 1'b0;"
    elif style == 4:
        return f"  wire  pdo_{idx:04d} = vdd_i & ~pwr_dwn_i;"
    elif style == 5:
        return f"  initial begin : init_blk_{idx:04d}"
    elif style == 6:
        return f"    sig_{idx:04d} = {(idx*7)%256}'h{((idx*13)%4095):x};"
    return ""

# ---------- FIXTURE A ----------
# anchor line specs (1-based line -> exact text). Gold loop locations.
A_ANCHORS = {
    1:  "// File: global_dldo_bind.sv  (CXMT LPDDR5 DLDO domain verification bind)",
    2:  "// Synthesized fixture for EDA-Eval-DesignFlow-DeadLoopScan-001 (asset A).",
    3:  "// Reproduces the loop structure scanned in real trace 1792042618272_wl9i4.",
    4: "`timescale 1ps/1fs",
    5: "module global_dldo_bind (",
    6: "  input  wire clk_i,",
    7: "  input  wire rst_n_i,",
    8: "  input  wire vdd_i,",
    9: "  input  wire pwr_dwn_i,",
    10: "  inout  wire vbp_i,",
    11: "  inout  wire vbn_i,",
    12: "  output wire [31:0] stat_o",
    13: ");",
    # L156: while CMD_CAL_CHK busy-wait
    150: "  // ---- calibration check busy-wait (block A) ----",
    151: "  task automatic cal_chk_wait_A;",
    152: "    cmd_state_t cmd_state;",
    153: "    cmd_state = CMD_CAL_CHK;",
    154: "    limiter_adj_code_dv = 1'b0;",
    155: "    adj_vbnvbp_pre_dv   = 1'b1;",
    156: "    while (cmd_state == CMD_CAL_CHK) begin",
    157: "      if (limiter_adj_code_dv !== adj_vbnvbp_pre_dv) begin",
    158: "        cmd_state = CMD_EXIT;      // only internal exit",
    159: "      end",
    160: "      #10ps;",
    161: "    end",
    162: "  endtask",
    # L612: while CMD_CAL_CHK busy-wait (block B, mirror)
    606: "  // ---- calibration check busy-wait (block B, mirror) ----",
    607: "  task automatic cal_chk_wait_B;",
    608: "    cmd_state_t cmd_state;",
    609: "    cmd_state = CMD_CAL_CHK;",
    610: "    limiter_adj_code_dv = 1'b0;",
    611: "    adj_vbnvbp_pre_dv   = 1'b1;",
    612: "    while (cmd_state == CMD_CAL_CHK) begin",
    613: "      if (limiter_adj_code_dv !== adj_vbnvbp_pre_dv) begin",
    614: "        cmd_state = CMD_EXIT;      // only internal exit",
    615: "      end",
    616: "      #10ps;",
    617: "    end",
    618: "  endtask",
    # L2711 / L2714: do-while (watchdog + inner group spin)
    2700: "  // ---- VintCompEn watchdog + group spin (dead-loop region) ----",
    2701: "  task automatic vintcomp_watch;",
    2702: "    bit VintCompEn_watch_dog;",
    2703: "    int VintCompEn_fdly;",
    2704: "    int group;",
    2705: "    VintCompEn_watch_dog = 1'b0;",
    2706: "    VintCompEn_fdly = 1024;",
    2707: "    group = dldo_mon.vif.group;",
    2708: "    // outer do-while spins on watchdog bit",
    2709: "    // inner do-while spins on vif.group external condition",
    2710: "    // ---- outer loop ----",
    2711: "    do begin",
    2712: "      // ---- inner fork ----",
    2713: "      // ---- inner loop ----",
    2714: "      do begin",
    2715: "        @(dldo_mon.vif.cmd_string inside { \"0_Active\",\"0_Write\",\"0_Read\",\"0_Precharge\" });",
    2716: "        #1ps;",
    2717: "      end",
    2718: "      // inner while: zero-delay spin on external vif.group",
    2719: "      end while(dldo_mon.vif.group != group);",
    2720: "      fork",
    2721: "        begin #(VintCompEn_fdly*1ps); VintCompEn_watch_dog = 1; end",
    2722: "      join_any",
    2723: "      disable fork;",
    2724: "    end",
    2725: "    // outer while: do-while on watchdog (relies on fdly thread firing)",
    2726: "    // if VintCompEn_fdly/watchdog never fires -> spins indefinitely",
    2727: "    end while(VintCompEn_watch_dog==0);",
    2728: "  endtask",
    # L2751 / L2788: bounded for (ref_cnt<4)
    2745: "  // ---- bounded ref-count setup loops (NOT dead loops) ----",
    2746: "  task automatic ref_cnt_setup_A;",
    2747: "    int ref_cnt;",
    2748: "    int sum;",
    2749: "    sum = 0;",
    2750: "    // bounded for loop",
    2751: "    for (ref_cnt=0; ref_cnt<4; ref_cnt++) begin",
    2752: "      sum += ref_cnt * VintCompEn_fdly;",
    2753: "    end",
    2754: "  endtask",
    2782: "  task automatic ref_cnt_setup_B;",
    2783: "    int ref_cnt;",
    2784: "    int sum;",
    2785: "    sum = 0;",
    2786: "    // bounded for loop (mirror)",
    2787: "    // bounded for loop",
    2788: "    for (ref_cnt=0; ref_cnt<4; ref_cnt++) begin",
    2789: "      sum += ref_cnt;",
    2790: "    end",
    2791: "  endtask",
    # 2 repeat loops (intentional, bounded by n)
    1400: "  // ---- bounded repeat (NOT a dead loop) ----",
    1401: "  task automatic rep_init_A;",
    1402: "    int k;",
    1403: "    repeat (8) begin",
    1404: "      k = $urandom_range(0,255);",
    1405: "      _log_rep.push_back(k);",
    1406: "    end",
    1407: "  endtask",
    2000: "  // ---- bounded repeat (mirror, NOT a dead loop) ----",
    2001: "  task automatic rep_init_B;",
    2002: "    repeat (16) begin",
    2003: "      _log_rep.push_back($urandom);",
    2004: "    end",
    2005: "  endtask",
    2823: "  // ---- file end ----",
    2824: "  assign stat_o = sig_0000;",
    2825: "endmodule",
    2826: "// EOF global_dldo_bind.sv",
    2827: "// generated fixture A (DeadLoopScan-001)",
}

A_TOTAL = 2827

def build_A():
    lines = [""] * A_TOTAL
    # place anchors
    for ln, txt in A_ANCHORS.items():
        lines[ln-1] = txt
    # distribute 92 forever monitor tasks across empty regions
    # place them in blocks between anchors; each monitor = 7 lines with 'forever' on line 2
    forever_targets = []  # line numbers that will contain 'forever'
    mon_count = 0
    # candidate start regions (1-based), avoid anchor lines
    regions = [(20,145),(165,600),(625,1395),(1410,1990),(2010,2695),(2800,2820)]
    placed = []
    for (lo,hi) in regions:
        c = lo
        while c + 7 <= hi and mon_count < 92:
            # check none of the 7 lines are anchors
            if any((c+i) in A_ANCHORS for i in range(7)):
                c += 1; continue
            blk = make_forever_monitor(mon_count)
            for i,t in enumerate(blk):
                lines[c+i-1] = t
            forever_targets.append(c+1)  # 'forever' is line 2 of block (c is line1)
            placed.append(c)
            mon_count += 1
            c += 8  # gap
    # fill remaining empty lines with filler (no loop keywords)
    for i in range(A_TOTAL):
        if lines[i].strip() == "":
            lines[i] = make_filler(i)
    # safety: ensure no stray loop keywords leaked into filler that would distort counts
    # (filler has none of while/for/forever/repeat/do as keywords)
    return lines, forever_targets

A_lines, A_forever_lines = build_A()
# verify counts
def count_kw(lines, kw):
    import re
    pat = re.compile(r"\b"+kw+r"\b")
    return [(i+1) for i,l in enumerate(lines) if pat.search(l)]

print("A forever count:", len(count_kw(A_lines,"forever")), "target 92")
print("A for count:", len(count_kw(A_lines,"for")), "target 2 (bounded)")
print("A while count:", len(count_kw(A_lines,"while")), "target 4")
print("A do count:", len(count_kw(A_lines,"do")), "target 2")
print("A repeat count:", len(count_kw(A_lines,"repeat")), "target 2")
print("A while lines:", count_kw(A_lines,"while"))
print("A for lines:", count_kw(A_lines,"for"))
print("A do lines:", count_kw(A_lines,"do"))
print("A total lines:", len(A_lines))

with open(os.path.join(OUT_DIR_A,"global_dldo_bind_A.sv"),"w") as f:
    f.write("\n".join(A_lines)+"\n")

# ---------- FIXTURE B (hidden) ----------
# structurally different: 3105 lines, 68 forever, 3 for (one for(;;) unbounded dead),
# 5 while, 3 do, 1 repeat. Different module/signal names. Different dead-loop lines.
B_TOTAL = 3105
B_ANCHORS = {
    1:  "// File: pdq_aux_bind.sv  (CXMT PDQ AUX domain verification bind) - fixture B",
    2: "// Synthesized hidden fixture B for DeadLoopScan-001 (structurally != A).",
    3: "`timescale 1ps/1fs",
    4: "module pdq_aux_bind (",
    5: "  input  wire clk_i,",
    6: "  input  wire rst_n_i,",
    7: "  output wire [15:0] aux_stat_o",
    8: ");",
    # L204: while (state == IDLE) zero-delay-ish busy wait
    198: "  // ---- idle busy-wait (block X) ----",
    199: "  task automatic idle_wait_X;",
    200: "    aux_state_t state;",
    201: "    state = IDLE;",
    202: "    req_pending = 1'b1;",
    203: "    // busy-wait depending on concurrent state change",
    204: "    while (state == IDLE) begin",
    205: "      #1ps;",
    206: "    end",
    207: "  endtask",
    # L880: bare while zero-delay spin on external
    874: "  // ---- external gate spin (block Y) ----",
    875: "  task automatic gate_spin_Y;",
    876: "    // bare while: zero-delay spin on external clk_gate_en",
    877: "    // if clk_gate_en never asserts -> never terminates",
    878: "    clk_gate_en = 1'b0;",
    879: "    // classic infinite pocket loop",
    880: "    while (clk_gate_en == 0);",
    881: "  endtask",
    # L100 / L500: bounded for (NOT dead)
    95:  "  // ---- bounded for (NOT dead) ----",
    96:  "  task automatic idx_setup_P;",
    97:  "    int i;",
    98:  "    int s;",
    99:  "    s = 0;",
    100: "    for (i=0;i<8;i++) begin",
    101: "      s += i;",
    102: "    end",
    103: "  endtask",
    495: "  // ---- bounded for (mirror, NOT dead) ----",
    496: "  task automatic idx_setup_Q;",
    497: "    int i;",
    498: "    int s;",
    499:  "    s = 0;",
    500: "    for (i=0;i<16;i++) begin",
    501: "      s += i*i;",
    502: "    end",
    503: "  endtask",
    # L2940: for(;;) UNBOUNDED -> dead loop (pattern NOT in A)
    2934: "  // ---- UNBOUNDED for(;;) (dead loop, pattern absent in A) ----",
    2935: "  task automatic unbounded_for_loop;",
    2936: "    int acc;",
    2937: "    acc = 0;",
    2938: "    // no exit condition -> never terminates",
    2939: "    // infinite for loop",
    2940: "    for(;;) begin",
    2941: "      acc = acc + 1;",
    2942: "      #1ps;",
    2943: "    end",
    2944: "  endtask",
    # L3050: do-while spin on req_pending
    3044: "  // ---- do-while spin on req_pending (block Z) ----",
    3045: "  task automatic req_spin_Z;",
    3046: "    // do-while: spins until req_pending clears",
    3047: "    req_pending = 1'b1;",
    3048: "    // if req_pending never clears -> never terminates",
    3049: "    // do-while on external handshake",
    3050: "    do begin",
    3051: "      @(vif.dse);",
    3052: "      #1ps;",
    3053: "    end",
    3054: "    end while(req_pending != 0);",
    3055: "  endtask",
    # L1600: a third while that is BOUNDED (has internal exit) -> NOT dead
    1594: "  // ---- bounded while with internal exit (NOT dead) ----",
    1595: "  task automatic bounded_while_W;",
    1596: "    int n;",
    1597: "    n = 0;",
    1598: "    // has internal counter exit",
    1599: "    // bounded while",
    1600: "    while (n < 64) begin",
    1601: "      n = n + 1;",
    1602: "      #1ps;",
    1603: "    end",
    1604: "  endtask",
    # 1 repeat (bounded)
    2200: "  // ---- bounded repeat (NOT dead) ----",
    2201: "  task automatic rep_init_R;",
    2202: "    repeat (4) begin",
    2203: "      _aux_log.push_back($urandom);",
    2204: "    end",
    2205: "  endtask",
    3100: "  // ---- file end ----",
    3101: "  assign aux_stat_o = aux_sig_0000;",
    3102: "endmodule",
    3103: "// EOF pdq_aux_bind.sv",
    3104: "// generated fixture B (DeadLoopScan-001 hidden)",
    3105: "// structurally different from A",
}

def make_forever_monitor_B(idx):
    name = f"aux_mon_{idx:02d}"
    sig = random.choice(["vif.dse","clk_gate_en","req_pending","aux_state","vif.ack","n","acc","state"])
    return [
        f"task automatic {name}(ref aux_if_t vif);",
        "  forever begin",
        f"    @(vif.{sig});",
        f"    if (vif.{sig} !== 1'bx) begin",
        f"      _aux_log_{idx}.push_back(vif.{sig});",
        "    end",
        "  end",
        "endtask",
    ]

def make_filler_B(idx):
    style = idx % 6
    if style == 0: return f"  logic [15:0] aux_sig_{idx:04d};"
    elif style == 1: return f"  assign aux_sig_{idx:04d} = aux_state_q & aux_en_i;"
    elif style == 2: return f"  // bind coverage point {idx}: pdq aux domain"
    elif style == 3: return f"  always @(posedge clk_i) aux_sig_{idx:04d} <= aux_sig_{(idx-1):04d};"
    elif style == 4: return f"  wire  pdo_{idx:04d} = vdd_i & ~aux_pwr_dwn_i;"
    elif style == 5: return f"  initial begin : aux_blk_{idx:04d}"
    return ""

def build_B():
    lines = [""] * B_TOTAL
    for ln, txt in B_ANCHORS.items():
        lines[ln-1] = txt
    forever_targets = []
    mon_count = 0
    regions = [(15,90),(110,195),(210,490),(510,870),(885,1590),(1610,2190),(2210,2925),(2950,3040),(3060,3095)]
    for (lo,hi) in regions:
        c = lo
        while c + 7 <= hi and mon_count < 68:
            if any((c+i) in B_ANCHORS for i in range(7)):
                c += 1; continue
            blk = make_forever_monitor_B(mon_count)
            for i,t in enumerate(blk):
                lines[c+i-1] = t
            forever_targets.append(c+1)
            mon_count += 1
            c += 8
    for i in range(B_TOTAL):
        if lines[i].strip() == "":
            lines[i] = make_filler_B(i)
    return lines, forever_targets

B_lines, B_forever_lines = build_B()
print("\nB forever count:", len(count_kw(B_lines,"forever")), "target 68")
print("B for count:", len(count_kw(B_lines,"for")), "target 3 (2 bounded + 1 for(;;))")
print("B while count:", len(count_kw(B_lines,"while")), "target 5")
print("B do count:", len(count_kw(B_lines,"do")), "target 3")
print("B repeat count:", len(count_kw(B_lines,"repeat")), "target 1")
print("B while lines:", count_kw(B_lines,"while"))
print("B for lines:", count_kw(B_lines,"for"))
print("B do lines:", count_kw(B_lines,"do"))
print("B total lines:", len(B_lines))

with open(os.path.join(OUT_DIR_B_HIDDEN,"global_dldo_bind_B.sv"),"w") as f:
    f.write("\n".join(B_lines)+"\n")

print("\nWrote A to", os.path.join(OUT_DIR_A,"global_dldo_bind_A.sv"))
print("Wrote B to", os.path.join(OUT_DIR_B_HIDDEN,"global_dldo_bind_B.sv"))
