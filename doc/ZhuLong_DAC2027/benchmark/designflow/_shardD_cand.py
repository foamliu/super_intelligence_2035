#!/usr/bin/env python3
"""Shard D candidate picker: read summary.tsv on .75, exclude ledger sessions,
score by netlist/schematic/waveform/analog keywords, print top N live candidates.
Exclusion list embedded (68 anchors from trace_ledger_D.tsv as of 2026-11-03 09:41)."""
import sys, re

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 15

EXCL = set("""1788172501150_w4x70 1792371248997_fa3cd 1791611498731_wg5u2 1793147699495_as67p 1792715254915_8z5a8 1791526272387_1i0em 1790563683904_l7aol 1789454632664_t1xjg 1786541065533_cgqd1 1787742497412_aneeo 1785810906841_m2vah 1787798131361_82ybr 1792297573507_9knot 1791966358446_82iou 1792376698189_1nsgi 1792573537545_enbl7 1793078405436_t0aom 1791963281932_4a852 1789370647360_ukkn7 1790487462826_wb03t 1788770994295_x4b0p 1790142100320_n91pk 1793102773959_okq91 1785725739513_r7ah0 1789951973902_p3107 1792297746172_kyref 1793070934364_gtyj5 1792215882223_qv6pl 1793001881089_dek1i 1792551272867_jnf1q 1792031875998_68gc9 1793067588685_cpv3d 1792583307053_mrwvg 1790584795049_ij4uu 1791941227075_le1s7 1785846039627_itvhk 1792488619552_mt7ua 1790064242187_1dh6s 1793017339067_jhdvn 1792834214357_qky0j 1789895218929_1xhgy 1792977240005_1mvxt 1791944224191_6i6lk 1790061986818_gpdus 1792724929127_2vuso 1793087996513_u78sz 1791960706202_66ut5 1792829537180_vaiob 1792205753795_x5t0t 1788764026073_8hdj3 1792744168464_n1k2a 1791958054953_qrb1b 1788830861723_dnvv4 1785735994579_tckme 1784623431472_gvm3g 1792742447012_djml8 1786504317615_fkprl 1792463960005_7frw8 1789350621467_fymcr 1789954294975_4chsl 1793155371052_v59v8 1793005343621_45gjq 1785498914896_8du7m 1786615396051_enh4y 1785994889000_x5tcq 1792055923522_tqmu1 1791786108086_vumhg 1791526217197_87257 1792380576403_uumms 1788577896116_33zw1 1792831256137_6qt0a 1793174925139_f0vya 1791958525711_f1fik 1792487689184_4ybw1 1792570431387_vdqlw 1789092579396_tgs17 1787569992152_uml8e 1788932125428_zqelb 1791425782404_rn6pm 1785898505302_zfrbu 1790490487765_6dx8f 1787897609476_ooyxi 1792400027384_ahjnv 1793093197648_x2w2z 1787903140887_314mt""".split())

KW = {
    "waveview": 4, "cosmos": 3, "spectrum": 3,
    "netlist": 5, "spiros": 4, "schematic": 5,
    "analog": 4, "skill": 2, "hspice": 5, "spice": 4,
    "cdl": 4, "spectre": 4, "waveform": 5,
}

cands = []
with open(SUMMARY) as f:
    header = next(f, None)
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) < 7:
            continue
        ip, host, user, sf, mc, kws, tools = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
        try:
            mcn = int(mc)
        except ValueError:
            continue
        if mcn < 300:
            continue
        anc = re.sub(r"\.messages\.json$", "", sf)
        if anc in EXCL:
            continue
        toks = (kws + " " + tools).lower()
        if not any(k in toks for k in ("waveview", "cosmos", "spectrum", "netlist",
                                        "spiros", "schematic", "analog", "hspice",
                                        "spice", "cdl", "spectre", "waveform")):
            continue
        score = sum(w for k, w in KW.items() if k in toks)
        cands.append((mcn, score, anc, user, host, kws, tools, ip))

cands.sort(key=lambda c: (-c[1], -c[0]))
for mcn, score, anc, user, host, kws, tools, ip in cands[:N]:
    print(f"{mcn}\t{score}\t{anc}\t{user}\t{host}\t{ip}\t{kws}|{tools}")
print(f"# total eligible: {len(cands)}")
