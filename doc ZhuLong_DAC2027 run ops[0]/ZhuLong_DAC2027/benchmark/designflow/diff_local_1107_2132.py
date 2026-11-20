import sys
cands = []
content = """TOTAL 37
1635	1574934	ethanw	1789545001824_x0t2m
1227	457631	yuankong	1793611022749_w9aze
1017	1097420	ericw	1793586676522_9kzwd
923	662407	ynbai	1791602435253_66tx9
758	306790	tzuo	1791448400305_kwiij
606	907955	ynbai	1793843849886_hsizo
591	2226511	zjqiao	1791611498731_wg5u2
570	955106	ynbai	1789713740053_1fgo2
441	674521	jianwang	1792479341771_hacfk
417	1110009	zjqiao	1791017602459_fwgyy
411	172024	yuankong	1793867708362_0t51l
336	1901878	kli	1792031875998_68gc9
293	343205	ericw	1789610397098_48m5j
254	194191	zjqiao	1789645120364_2n1bs
246	554788	yuankong	1792042288837_5cigt
241	1945812	yuankong	1791852261815_1pxm7
230	453155	ynbai	1793927469652_3l3yx
206	171822	dandans	1791768325372_g13dw
130	156933	jianwang	1792201122841_ncfk9
101	894629	zjqiao	1792552457905_b4dlx
92	315494	xuebaok	1793260738350_ziy0b
90	327845	zjqiao	1793347412273_nq8l2
85	78381	yuankong	1793865966161_rkdu8
60	2019746	zjqiao	1793243267055_5hjg7
55	45801	yuankong	1792395143753_ai203
54	987264	shanksw	1793864789160_j5z4v
48	894715	zjqiao	1789544872347_mi210
48	894432	zjqiao	1789644585939_3e35z
37	33674	zjqiao	1789723764998_zlqaz
35	1850199	xuebaok	1791446512697_3s3zx
34	1228581	ericw	1789699043373_y91i6
30	1458317	ericw	1790042178493_mrmfn
24	2660431	xuebaok	1791463574990_um5we
16	172193	jianwang	1791955659176_a63u6
12	536400	shanksw	1793877732979_qyroq
9	14335	zjqiao	1789723438003_vefeh
7	21965	ericw	1789633680645_racxm"""
for line in content.splitlines()[1:]:
    parts = line.split('\t')
    if len(parts) >= 4:
        cands.append((int(parts[0]), int(parts[1]), parts[2], parts[3]))
ledger = set()
with open('designflow/trace_ledger_B.tsv') as f:
    for line in f:
        line=line.rstrip('\n')
        if not line: continue
        a = line.split('\t')[0]
        ledger.add(a.replace('.messages.json',''))
print('LEDGER', len(ledger))
unscouted = [c for c in cands if c[3] not in ledger]
print('CANDS', len(cands), 'UNSCOUTED', len(unscouted))
peeked_last = {'w9aze','5cigt','1pxm7','ncfk9'}
remaining = [c for c in unscouted if c[3].split('_')[-1] not in peeked_last]
print('REMAINING (after last round peek 4)', len(remaining))
for sc,sz,user,base in remaining:
    print(f'{sc}\t{sz}\t{user}\t{base}')
