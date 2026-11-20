#!/usr/bin/env python3
"""R19 FAST: Analytical power + reduced simulation (<60s)."""
import math, random, statistics, json

def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0))))

def normal_ppf(p):
    if p <= 0.0 or p >= 1.0: return float('-inf') if p <= 0 else float('inf')
    a=[-39.69683028665376,220.9460984245205,-275.9285104469687,138.3577518672690,-30.66479806614716,2.506628277459239]
    b=[-54.47609879822406,161.5858368580409,-155.6989798598866,66.80131188771972,-13.28068155288572]
    c=[-0.007784894002430293,-0.3223964580411365,-2.400758277161838,-2.549732539343734,4.374664141464968,2.938163982698783]
    d=[0.007784695709041462,0.3224671290700398,2.445134137142996,3.754408661907416]
    plow,phigh=0.02425,1.0-0.02425
    if p<plow:
        q=math.sqrt(-2.0*math.log(p)); return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    elif p<=phigh:
        q=p-0.5; r=q*q; return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)
    else:
        q=math.sqrt(-2.0*math.log(1.0-p)); return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)

def sigmoid(x): return 1.0/(1.0+math.exp(-max(-50,min(50,x))))

def gen_diff(seed=42):
    rng=random.Random(seed); d=[]
    for _,n,m,s in [("L",64,0.50,0.15),("S",47,0.65,0.15),("D",24,0.35,0.15),("O",23,0.30,0.15)]:
        for _ in range(n): d.append(max(0.01,min(0.99,rng.gauss(m,s))))
    return d

def cap_for_target(diff,t):
    lo,hi=-5.0,5.0
    for _ in range(100):
        mid=(lo+hi)/2; mp=sum(sigmoid(mid-d) for d in diff)/len(diff)
        if mp<t: lo=mid
        else: hi=mid
    return (lo+hi)/2

def sim_paired(diff,thA,thB,nr=5,sA=42,sB=43):
    rA,rB=random.Random(sA),random.Random(sB); a,b=[],[]
    for d in diff:
        pA,pB=sigmoid(thA-d),sigmoid(thB-d)
        a.append(sum(1 for _ in range(nr) if rA.random()<pA)/nr)
        b.append(sum(1 for _ in range(nr) if rB.random()<pB)/nr)
    return a,b

def mcnemar(rA,rB,th=0.6):
    b=c=0
    for ra,rb in zip(rA,rB):
        ap=ra>=th; bp=rb>=th
        if ap and not bp: b+=1
        elif not ap and bp: c+=1
    if b+c==0: return 0,1,b,c
    chi2=(abs(b-c)-1)**2/(b+c); p=2*(1-normal_cdf(math.sqrt(chi2))) if chi2>0 else 1.0
    return chi2,p,b,c

def pttest(rA,rB):
    n=len(rA); diffs=[rb-ra for ra,rb in zip(rA,rB)]
    md=statistics.mean(diffs); sd=statistics.stdev(diffs)/math.sqrt(n)
    if sd==0: return 0,1,md,sd
    t=md/sd; p=2*(1-normal_cdf(abs(t))); return t,p,md,sd

def pw_mcnemar(diff,thA,thB,nr=5,ns=500,a=0.05,off=1000):
    r=0
    for s in range(ns):
        rA,rB=sim_paired(diff,thA,thB,nr,off+s*2,off+s*2+1); _,p,_,_=mcnemar(rA,rB)
        if p<a: r+=1
    return r/ns

def pw_ttest(diff,thA,thB,nr=5,ns=500,a=0.05,off=10000):
    r=0
    for s in range(ns):
        rA,rB=sim_paired(diff,thA,thB,nr,off+s*2,off+s*2+1); _,p,_,_=pttest(rA,rB)
        if p<a: r+=1
    return r/ns

def main():
    print("=" * 60)
    print("R19 FAST: Statistical Power Analysis")
    print("EDA-Eval-PyAether: 158 tasks x 5 runs")
    print("=" * 60)
    diff = gen_diff()
    targets = {'baseline_36': 0.36, 'M1_50': 0.50, 'M2_65': 0.65, 'M3_75': 0.75, 'M4_85': 0.85}
    thetas = {n: cap_for_target(diff, t) for n, t in targets.items()}
    results = {'n_tasks': 158, 'thetas': {k: round(v, 4) for k, v in thetas.items()}}
    z = normal_ppf(0.975)
    print("\n1. UNPAIRED 95% CI (Wald, n=158):")
    results['unpaired_ci'] = {}
    for n, t in targets.items():
        se = math.sqrt(t * (1 - t) / 158); lo, hi = t - z * se, t + z * se
        results['unpaired_ci'][n] = {'rate': t, 'se': round(se, 4), 'ci_lo': round(lo, 4),
                                     'ci_hi': round(hi, 4), 'width_pp': round((hi - lo) * 100, 1)}
        print(f"   {n}: {t:.0%} +/- {((hi-lo)/2)*100:.1f}pp (CI: [{lo:.1%}, {hi:.1%}])")
    comps = [('baseline_36', 'M1_50', 14), ('M1_50', 'M2_65', 15),
             ('M2_65', 'M3_75', 10), ('M3_75', 'M4_85', 10)]
    results['comparisons'] = {}
    print("\n2. PAIRED TEST POWER (alpha=0.05, n_sims=500):")
    print(f"   {'Comparison':<30} {'Gap':>4} {'McN5':>6} {'McN1':>6} {'tt5':>6} {'MDES':>6}")
    for nA, nB, gap in comps:
        key = f'{nA}_vs_{nB}'; se_A = math.sqrt(targets[nA]*(1-targets[nA])/158)
        se_B = math.sqrt(targets[nB]*(1-targets[nB])/158); mdes = round((z*(se_A+se_B))*100, 1)
        print(f"  {key}...", end='', flush=True)
        pm5 = pw_mcnemar(diff, thetas[nA], thetas[nB], 5, 500)
        pm1 = pw_mcnemar(diff, thetas[nA], thetas[nB], 1, 500)
        pt5 = pw_ttest(diff, thetas[nA], thetas[nB], 5, 500)
        results['comparisons'][key] = {'gap_pp': gap, 'power_mcnemar_5run': round(pm5, 3),
                                        'power_mcnemar_1run': round(pm1, 3),
                                        'power_ttest_5run': round(pt5, 3), 'unpaired_mdes_pp': mdes}
        print(f" McN5={pm5:.2f} McN1={pm1:.2f} tt5={pt5:.2f} MDES={mdes}pp")
    alpha_bonf = 0.05 / 4
    pm5b = pw_mcnemar(diff, thetas['baseline_36'], thetas['M1_50'], 5, 500, a=alpha_bonf)
    results['bonferroni_alpha'] = alpha_bonf
    results['comparisons']['baseline_36_vs_M1_50']['power_mcnemar_5run_bonferroni'] = round(pm5b, 3)
    print(f"\n3. BONFERRONI alpha={alpha_bonf:.4f}, McNemar5(36->50)={pm5b:.3f}")
    print("\n4. EFFECT OF RUNS (36% vs 50%):")
    results['runs_effect'] = {}
    for nr in [1, 3, 5, 10, 20]:
        p = pw_mcnemar(diff, thetas['baseline_36'], thetas['M1_50'], nr, 500)
        results['runs_effect'][f'{nr}_runs'] = round(p, 3); print(f"   {nr} runs: power={p:.3f}")
    print("\n5. DISCORDANT PAIRS:")
    results['discordant'] = {}
    for nA, nB, gap in comps:
        rA, rB = sim_paired(diff, thetas[nA], thetas[nB], 5, 99998, 99999)
        _, _, b, c = mcnemar(rA, rB)
        results['discordant'][f'{nA}_vs_{nB}'] = {'b': b, 'c': c, 'total': b+c, 'net': c-b}
        print(f"   {nA}_vs_{nB}: b={b} c={c} total={b+c} net={c-b}")
    print("\n6. COHEN'S h:")
    results['cohens_h'] = {}
    for nA, nB, gap in comps:
        pA, pB = targets[nA], targets[nB]
        h = 2*math.asin(math.sqrt(pB)) - 2*math.asin(math.sqrt(pA))
        results['cohens_h'][f'{nA}_vs_{nB}'] = round(h, 4)
        cat = 'small' if h < 0.3 else 'medium' if h < 0.5 else 'large'
        print(f"   {nA}_vs_{nB}: h={h:.4f} ({cat})")
    with open('/tmp/pt_r19_power_fast.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print("\nSaved to /tmp/pt_r19_power_fast.json")

if __name__ == '__main__':
    main()
