#!/usr/bin/env python3
"""Diff strict/broader spice-dom candidates (from 11-07 00:01 daily cron log)
against ledger B (299 entries). Report NOT-in-ledger candidates."""
import sys

LEDGER = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_B.tsv"

def strip_suffix(s):
    for suf in (".messages.archive.json", ".messages.json", ".json"):
        if s.endswith(suf):
            return s[:-len(suf)]
    return s

# Load ledger sessions (col 0)
ledger = set()
with open(LEDGER) as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if parts and parts[0]:
            ledger.add(strip_suffix(parts[0]))
print(f"LEDGER_UNIQUE_SESSIONS: {len(ledger)}")

# Strict candidates (dedup by session, from 11-07 00:01 daily cron log)
# format: session\tuser@host\ttotal\tspice\tratio
strict_raw = """1793600858808_la00c	e0029308@hfeg0pkn001	8265	5910	0.715
1793338010547_r06g9	clarawu@hfeg0pkn004	4143	2089	0.504
1792372786960_4ujp9	tongni@hfeg0pkn001	1849	1687	0.912
1792135941514_8n60f	adaml@hfeg0pkn002	3566	1643	0.461
1793177580229_11fst	e0030760@hfeg0pkn004	2134	1564	0.733
1793328354943_p7jfx	tongni@hfeg0pkn001	2663	1367	0.513
1792131744105_g48nq	adaml@hfeg0pkn002	1708	1359	0.796
1793791169909_2ka5p	e0030760@hfeg0pkn004	1737	1345	0.774
1793345773037_65daa	tongni@hfeg0pkn001	2593	1287	0.496
1793257968522_mp3us	tongni@hfeg0pkn001	1613	1213	0.752
1793174925139_f0vya	e0030760@hfeg0pkn004	1298	1107	0.853
1793792759786_ujw1y	qiang3xu@hfeg0pkn005	2921	1089	0.373
1793341440302_sqm07	tongni@hfeg0pkn001	1431	945	0.660
1792831256137_6qt0a	harrywu@hfeg0pkn002	2015	834	0.414
1793187913089_e6xdf	e0030760@hfeg0pkn004	1618	810	0.501
1793184645122_t1epq	e0030760@hfeg0pkn004	776	702	0.905
1792829537180_vaiob	harrywu@hfeg0pkn002	1555	686	0.441
1793266803039_g89xb	tongni@hfeg0pkn001	1010	667	0.660
1792720528359_2tuxj	kaixuanx@hfeg0pkn002	1312	498	0.380
1793326532932_fxfox	tongni@hfeg0pkn001	1145	496	0.433
1793757463114_zd8iu	shanliny@hfeg0pkn001	460	460	1.000
1793243641918_xcuds	tongni@hfeg0pkn001	886	413	0.466
1793679618975_i1zyw	e0030760@hfeg0pkn004	1000	412	0.412
1792394413650_b86q7	tongni@hfeg0pkn001	961	381	0.396
1792373056714_2enpk	jasonw@hfeg0pkn004	444	361	0.813
1793596317022_34b72	chapinc@hfeg0pkn005	1011	354	0.350
1792483903326_cllpy	johnl@hfeg0pkn001	389	354	0.910
1792373325953_z6mt7	tongni@hfeg0pkn001	391	351	0.898
1793856196029_7at4j	lvyy@hfeg0pkn002	478	341	0.713
1793270732926_ebmf3	chapinc@hfeg0pkn005	376	339	0.902
1785896968029_vo4gm	e0025768@hfeg0pkn001	440	339	0.770
1785907092176_vdeyi	e0025768@hfeg0pkn001	344	325	0.945
1793155079677_gnmu0	e0030760@hfeg0pkn004	342	293	0.857
1788919426197_cjcn7	ming1w@hfeg0pkn005	566	266	0.470
1793263942286_u8rjq	tongni@hfeg0pkn001	481	262	0.545
1793670518248_ap4dl	e0029495@hfeg0pkn002	598	252	0.421
1793598804317_2swgt	adaml@hfeg0pkn002	269	228	0.848
1793344639876_ig5hm	jiangbaol@hfeg0pkn004	482	219	0.454
1793868970979_6nte7	kaixuanx@hfeg0pkn002	325	211	0.649
1793931174603_tc4yu	lvyy@hfeg0pkn002	405	205	0.506
1792637805938_w2p04	johnl@hfeg0pkn001	167	166	0.994
1793692406403_lcg3v	ronghu@hfeg0pkn005	238	159	0.668
1792459158095_dfaqe	e0045488@hfeg0pkn004	416	148	0.356
1793865540752_5ue0u	chapinc@hfeg0pkn005	298	140	0.470
1793600858808_la00c	e0029308@hfeg0pkn001	140	132	0.943
1793692877234_xlzwr	ronghu@hfeg0pkn005	208	129	0.620
1793792373749_l5r0u	elianaz@hfeg0pkn002	184	125	0.679
1791966728738_ad3nu	zxtu@hfeg0pkn001	173	116	0.671
1792981479658_jh3kb	ronghu@hfeg0pkn005	176	89	0.506
1789451741660_7uwtz	e0016033@hfeg0pkn001	188	80	0.426
1792375032414_3yoit	clarawu@hfeg0pkn004	85	67	0.788
1793929759607_7nm1g	mwxi@hfhds228	66	63	0.955
1788946694927_w5knw	sagequan@hfeg0pnd002	97	58	0.598
1788771111710_mwijd	sagequan@hfeg0pnd002	64	57	0.891
1793370534751_zju83	yh1yang@hfeg0pkn002	58	57	0.983
1793923081404_s6bse	e0030760@hfeg0pkn004	131	53	0.405
1793323487985_ukhbj	tracym@hfeg0pbn14	141	51	0.362
1792045605929_rp1xk	e0029495@hfeg0pkn002	80	51	0.637
1793961380780_eu254	e0030760@hfeg0pkn004	118	50	0.424
1789885303895_nv8gj	jinsongl@hfeg0pkn005	115	43	0.374
1793341820971_f5ser	wzj@hfeg0pkn002	45	42	0.933
1793684231151_ne32u	adaml@hfeg0pkn002	72	40	0.556
1789957560618_7kyrv	mike@hfeg0pkn003	43	40	0.930
1791962616204_7j1bw	caozhang@hfeg0pkn004	46	38	0.826
1791967805126_c084j	caozhang@hfeg0pkn004	46	38	0.826
1793356935781_jqx69	adaml@hfeg0pkn002	46	36	0.783
1793598804317_2swgt	adaml@hfeg0pkn002	46	36	0.783
1793181609220_r08ob	e0018590@hfeg0pkn005	61	33	0.541
1792127794562_r8yj1	e0023936@hfeg0pkn002	49	32	0.653
1789441210558_p8wm1	shaoyou@hfeg0pkn003	32	32	1.000
1791358972656_8fe71	thomasz@hfeg0pkn002	42	31	0.738
1793756918657_hujdg	mwxi@hfhds228	43	30	0.698
1792372024585_wjj8v	ruminji@hfeg0pkn002	70	27	0.386
1792135941514_8n60f	adaml@hfeg0pkn002	39	26	0.667
1793326532932_fxfox	tongni@hfeg0pkn001	74	26	0.351
1793774598225_ydt6x	kaixuanx@hfeg0pkn002	40	16	0.400
1793702742279_izlej	owench@hfeg0pkn002	32	15	0.469
1791447139857_poxvz	johnl@hfeg0pkn001	31	15	0.484
1789614314714_ctu99	rongjiez@hfeg0pkn005	41	15	0.366
1793585625884_wohc2	dsgao@hfeg0pkn002	36	14	0.389
1792378687851_j8vf6	tongni@hfeg0pkn001	37	14	0.378
1792379743340_2y77m	tongni@hfeg0pkn001	37	14	0.378
1793779465508_q9aja	adaml@hfeg0pkn002	30	12	0.400"""

# Broader-only candidates (in broader but not in strict, dedup by session)
broader_only_raw = """1793763970829_iq1bu	lvyy@hfeg0pkn002	2841	872	0.307
1791523486486_ws2bi	irene1li@hfeg0pkn004	1657	542	0.327
1792378687851_j8vf6	tongni@hfeg0pkn001	1067	349	0.327
1790245155745_i5ae7	jiangbaol@hfeg0pkn004	1083	348	0.321
1793344639876_ig5hm	jiangbaol@hfeg0pkn004	985	323	0.328
1793706971126_rsu2w	chapinc@hfeg0pkn005	915	282	0.308
1793861928338_3ijo2	chapinc@hfeg0pkn005	915	282	0.308
1792134251943_q9r9s	lanxinz@hfeg0pkn001	444	144	0.324
1793089887669_4c5ws	e0046913@hfeg0pkn003	131	45	0.344
1792215882223_qv6pl	adaml@hfeg0pkn002	135	44	0.326
1789976011359_06htj	mike@hfeg0pkn003	46	15	0.326
1793356935781_jqx69	adaml@hfeg0pkn002	113	36	0.319
1788871441686_fieju	harrys@hfeg0pkn002	22	14	0.636
1793702295738_4bsmv	owench@hfeg0pkn002	28	13	0.464
1793685165147_ga396	e02141@hfeg0pkn001	23	11	0.478
1789367633495_9uwcw	lorikx@hfeg0pkn004	23	9	0.391
1793244399565_uacot	yh1yang@hfeg0pkn002	23	9	0.391
1792559583345_n36p3	jiangbaol@hfeg0pkn004	26	8	0.308
1793950315023_15w22	jiangbaol@hfeg0pkn004	26	8	0.308
1790044729030_4v3b5	lorikx@hfeg0pkn004	22	8	0.364"""

def parse(raw):
    seen = {}
    for line in raw.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        sess = parts[0]
        key = strip_suffix(sess)
        if key not in seen:
            seen[key] = parts
    return seen

strict = parse(strict_raw)
broader_only = parse(broader_only_raw)

strict_not = {k: v for k, v in strict.items() if k not in ledger}
strict_in = {k: v for k, v in strict.items() if k in ledger}
broader_not = {k: v for k, v in broader_only.items() if k not in ledger}
broader_only_in = {k: v for k, v in broader_only.items() if k in ledger}

print(f"STRICT_UNIQUE: {len(strict)}")
print(f"STRICT_IN_LEDGER: {len(strict_in)}")
print(f"STRICT_NOT_IN_LEDGER: {len(strict_not)}")
print(f"BROADER_ONLY_UNIQUE: {len(broader_only)}")
print(f"BROADER_ONLY_IN_LEDGER: {len(broader_only_in)}")
print(f"BROADER_ONLY_NOT_IN_LEDGER: {len(broader_not)}")

print("\n=== STRICT NOT-IN-LEDGER (sorted by spice desc) ===")
for k, v in sorted(strict_not.items(), key=lambda x: -int(x[1][3])):
    print(f"{v[0]}\t{v[1]}\ttotal={v[2]}\tspice={v[3]}\tratio={v[4]}")

print("\n=== BROADER-ONLY NOT-IN-LEDGER (sorted by spice desc) ===")
for k, v in sorted(broader_not.items(), key=lambda x: -int(x[1][3])):
    print(f"{v[0]}\t{v[1]}\ttotal={v[2]}\tspice={v[3]}\tratio={v[4]}")
