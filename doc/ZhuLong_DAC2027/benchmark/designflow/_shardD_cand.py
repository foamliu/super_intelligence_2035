#!/usr/bin/env python3
"""Shard D candidate picker: read summary.tsv on .75, exclude ledger sessions,
score by netlist/schematic/waveform/analog keywords, print top N live candidates.
Exclusion list embedded (68 anchors from trace_ledger_D.tsv as of 2026-11-03 09:41)."""
import sys, re

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 15

EXCL = set("""1784623431472_gvm3g 1785498914896_8du7m 1785725739513_r7ah0 1785735994579_tckme 1785810906841_m2vah 1785846039627_itvhk 1785994889000_x5tcq 1786504317615_fkprl 1786541065533_cgqd1 1786615396051_enh4y 1787569992152_uml8e 1787570565957_i41yw 1787742497412_aneeo 1787798131361_82ybr 1787897609476_ooyxi 1787903140887_314mt 1788172501150_w4x70 1788577896116_33zw1 1788764026073_8hdj3 1788770994295_x4b0p 1788830861723_dnvv4 1788932125428_zqelb 1789092579396_tgs17 1789350621467_fymcr 1789370647360_ukkn7 1789454632664_t1xjg 1789526951493_wa1uw 1789895218929_1xhgy 1789951973902_p3107 1789954294975_4chsl 1789983785169_qqvzo 1790061986818_gpdus 1790064242187_1dh6s 1790142100320_n91pk 1790487462826_wb03t 1790490487765_6dx8f 1790563683904_l7aol 1790584795049_ij4uu 1790658262664_zjzz8 1791425782404_rn6pm 1791526217197_87257 1791526272387_1i0em 1791611498731_wg5u2 1791786108086_vumhg 1791941227075_le1s7 1791944224191_6i6lk 1791958054953_qrb1b 1791958525711_f1fik 1791960706202_66ut5 1791963281932_4a852 1791963948520_hk622 1791966358446_82iou 1792031875998_68gc9 1792055923522_tqmu1 1792056947936_36yj3 1792139236507_7jzqb 1792205753795_x5t0t 1792215355014_rcx51 1792215882223_qv6pl 1792216766099_x89ek 1792297573507_9knot 1792297746172_kyref 1792371248997_fa3cd 1792376698189_1nsgi 1792380576403_uumms 1792389346933_uiykd 1792394864015_10qhm 1792400027384_ahjnv 1792463960005_7frw8 1792487689184_4ybw1 1792488619552_mt7ua 1792551272867_jnf1q 1792570431387_vdqlw 1792573537545_enbl7 1792583307053_mrwvg 1792649635599_u0ke5 1792660810859_l0qrf 1792715254915_8z5a8 1792724929127_2vuso 1792742447012_djml8 1792744168464_n1k2a 1792829537180_vaiob 1792831256137_6qt0a 1792834214357_qky0j 1792977240005_1mvxt 1793001881089_dek1i 1793005343621_45gjq 1793017339067_jhdvn 1793021121702_24h7g 1793067588685_cpv3d 1793070934364_gtyj5 1793078373656_wqhsu 1793078405436_t0aom 1793087996513_u78sz 1793093197648_x2w2z 1793102773959_okq91 1793147699495_as67p 1793155371052_v59v8 """.split())

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
