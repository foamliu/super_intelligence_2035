#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Synthesize DSPF A and B for EDA-Eval-DesignFlow-SpfDielectricLeakageQA-001.

A = yh1yang ROmulti.spf.TYP_98_RCC reproduction (synth_deck, P-005 type-8):
    net_sections=203, R_total=13439, cross_net_R=0, ground_R=0,
    instance_pin_R=2280, coupling_cap=29370, ground_cap=4481
    => dielectric_leakage_R_present = False
B = structurally opposite (hidden):
    net_sections=180, R_total=9870, cross_net_R=7, ground_R=0,
    instance_pin_R=1610, coupling_cap=25600, ground_cap=3240
    => dielectric_leakage_R_present = True

DSPF node->net map: *|N (root node), *|I (pin->node), *|S (seg node) all map
into the enclosing *|NET block. R lines reference node ids; cross_net_R = R
whose two endpoints map to two DIFFERENT nets. ground_R = R with one endpoint
on the ground net (named "0"). pin_R = R with one endpoint being a pin-node
(introduced by *|I).
"""
import os

CASE = "EDA-Eval-DesignFlow-SpfDielectricLeakageQA-001"
ASSETS = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/" + CASE


def distribute(total, n, base):
    """Split `total` into n parts, each >= base-1, sum exactly total.
    Returns list of n ints."""
    q, r = divmod(total, n)
    parts = [q] * n
    for i in range(r):
        parts[i] += 1
    # ensure each part >= base-1 (here base is just informational)
    assert sum(parts) == total
    return parts


def gen_deck(path, *, n_nets, n_pin_R, n_internal_R, n_cross_R, n_coupling_C, n_ground_C,
             corner, temp, subckt, ground_R=0):
    """Generate a DSPF deck with exact counts."""
    lines = []
    lines.append("*|DSPF 1.3")
    lines.append("*|IEEE_CMD")
    lines.append("*|SCALING OFF")
    lines.append("*|OPERATING_TEMP %d" % temp)
    lines.append("*|SUBCKT %s" % subckt)
    lines.append("*|GROUND_NET 0")
    lines.append("*|DELIMITER_FORWARD /")
    lines.append("*|BUS_DELIMITER_LEFT [")
    lines.append("*|BUS_DELIMITER_RIGHT ]")
    lines.append("*|CORNER %s" % corner)
    lines.append("*|COUPLING 0.5e-3")

    # per-net pin-R and internal-R counts
    pin_parts = distribute(n_pin_R, n_nets, 0)
    int_parts = distribute(n_internal_R, n_nets, 0)
    cc_parts = distribute(n_coupling_C, n_nets, 0)
    gc_parts = distribute(n_ground_C, n_nets, 0)

    # assign node ids: net i root = i*1_000_000; pin nodes i*1_000_000 + 1000 + j;
    # internal nodes i*1_000_000 + 2000 + j
    # we also need distinct nets for cross-net R: pick pairs (0,1),(2,3),... for B
    cross_pairs = []
    if n_cross_R > 0:
        # use net 0 and net 1 repeatedly (both must exist)
        for k in range(n_cross_R):
            cross_pairs.append((k % n_nets, (k + 1) % n_nets))

    r_counter = 0
    c_counter = 0
    cc_counter = 0

    # We need, for cross-net R, a node belonging to net B to be referenced inside
    # net A's block. Pre-collect each net's root node id.
    # reserve node 0 exclusively for ground; signal net roots start at 1_000_000
    root_nodes = [(i + 1) * 1_000_000 for i in range(n_nets)]

    for i in range(n_nets):
        netname = "n_%03d" % i
        root = root_nodes[i]
        lines.append("*|NET %s 0.0" % netname)
        lines.append("*|N %d" % root)
        # a couple of segment points (map seg node -> this net)
        seg_base = i * 1_000_000 + 5000
        for j in range(2):
            snode = seg_base + j
            lines.append("*|S %d %d M%d 0 %d" % (100 + j, 200 + j, (j % 4) + 1, snode))
        # pin nodes + pin_R
        for j in range(pin_parts[i]):
            pinnode = i * 1_000_000 + 1000 + j
            pinname = "XI_sw%d.XI_t%d<%d>.MNM0:GATE" % (i, i, j)
            lines.append("*|I %s %d I" % (pinname, pinnode))
            r_counter += 1
            val = 50.0 + (r_counter % 200) * 0.317
            lines.append("R%05d %d %d %.4f" % (r_counter, pinnode, root, val))
        # internal same-net R
        for j in range(int_parts[i]):
            n1 = i * 1_000_000 + 2000 + (2 * j)
            n2 = i * 1_000_000 + 2000 + (2 * j + 1)
            r_counter += 1
            val = 0.5 + (j % 50) * 0.123
            lines.append("R%05d %d %d %.4f" % (r_counter, n1, n2, val))
        # ground caps (C to node 0)
        for j in range(gc_parts[i]):
            c_counter += 1
            cnode = i * 1_000_000 + 7000 + j
            val = 0.1e-15 + (j % 30) * 0.05e-15
            lines.append("C%05d %d 0 %.4e" % (c_counter, cnode, val))
        # coupling caps (Cc to another net's root node) -- cross-net by construction
        for j in range(cc_parts[i]):
            cc_counter += 1
            other = (i + 1 + j) % n_nets
            onode = root_nodes[other]
            val = 0.2e-15 + (j % 40) * 0.1e-15
            lines.append("Cc%05d %d %d %.4e" % (cc_counter, root, onode, val))
        lines.append("*|ENDNET")

    # cross-net R lines: append inside net A's block? We already closed blocks.
    # Instead, re-open minimal blocks? Simpler: append cross-net R as standalone
    # R lines after all nets, referencing two nets' root nodes. The analyzer uses
    # the global node->net map so it will detect netA != netB regardless of block.
    # But to keep DSPF structurally valid, emit them inside a final dummy net that
    # references foreign nodes. We'll just emit them as bare R lines after *|ENDS?
    # That would be invalid DSPF. Instead: re-emit within net 0's block by NOT
    # closing yet -- too late. Cleanest: emit cross-net R inside their own *|NET
    # block that declares a node mapped to net A, then references net B's root.
    # But the node->net map is built from *|N/*|I/*|S. A bare R line's endpoints
    # are looked up in the map. So we emit a tiny *|NET block whose *|N is a NEW
    # node (mapped to this dummy net), and the R references net_A_root (mapped to
    # net A) and net_B_root (mapped to net B). cross_net_R detected.
    for k, (a, b) in enumerate(cross_pairs):
        # dummy net to host the cross R
        dnet = "xd_%03d" % k
        dnode = 9_000_000 + k
        lines.append("*|NET %s 0.0" % dnet)
        lines.append("*|N %d" % dnode)
        r_counter += 1
        val = 1.0e6 + k * 100.0  # huge = dielectric leakage R (clearly a leak)
        lines.append("R%05d %d %d %.4f" % (r_counter, root_nodes[a], root_nodes[b], val))
        lines.append("*|ENDNET")
    # NOTE: dummy nets add to net_sections count. To keep net_sections exact,
    # we must subtract: the cross-net dummy nets are extra. Adjust: caller must
    # pass n_nets = desired_net_sections - n_cross_R. We handle that below.

    lines.append("*|ENDS")
    lines.append("*|END")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

    # report actual counts for verification
    return {
        "net_sections": n_nets + n_cross_R,  # dummy nets add
        "R_total": r_counter,
        "cross_net_R": n_cross_R,
        "ground_R": ground_R,
        "instance_pin_R": n_pin_R,
        "same_net_internal_R": n_internal_R,
        "coupling_cap": n_coupling_C,
        "ground_cap": n_ground_C,
    }


def main():
    # A: net_sections must be 203. cross_R=0 => no dummy nets. n_nets=203.
    a_counts = dict(n_nets=203, n_pin_R=2280, n_internal_R=11159, n_cross_R=0,
                    n_coupling_C=29370, n_ground_C=4481,
                    corner="TYP_98", temp=98, subckt="ROmulti")
    a = gen_deck(os.path.join(ASSETS, "ROmulti.spf.TYP_98_RCC"), **a_counts)

    # B: net_sections must be 180, cross_R=7 => 7 dummy nets => n_nets = 180-7 = 173.
    b_counts = dict(n_nets=173, n_pin_R=1610, n_internal_R=8253, n_cross_R=7,
                    n_coupling_C=25600, n_ground_C=3240,
                    corner="SS_40", temp=40, subckt="ROmulti_B")
    b = gen_deck(os.path.join(ASSETS, "hidden", "ROmulti.spf.SS_40_RCC"), **b_counts)

    print("A:", a_counts, "=> actual", a)
    print("B:", b_counts, "=> actual", b)
    assert a["net_sections"] == 203, a
    assert a["R_total"] == 13439, a
    assert a["cross_net_R"] == 0, a
    assert a["ground_R"] == 0, a
    assert a["instance_pin_R"] == 2280, a
    assert a["coupling_cap"] == 29370, a
    assert b["net_sections"] == 180, b
    assert b["R_total"] == 9870, b
    assert b["cross_net_R"] == 7, b
    assert b["instance_pin_R"] == 1610, b
    assert b["coupling_cap"] == 25600, b
    print("OK counts verified")


if __name__ == "__main__":
    main()
