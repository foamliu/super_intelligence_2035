#!/usr/bin/env python3
"""Precise scan of hermes + claude-code rerun (2026-10-25 17:5x令 part①).
Reads reward.txt / exception.txt from each trial dir, compares to old baseline.
"""
import json, os, glob, sys
from pathlib import Path

BASE = Path('/tmp/tb_7x89')
OLD_BASELINE = Path('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/baseline_rewards_7x89_20261024.json')

RERUN_DIRS = {
    'hermes': BASE / 'jobs_hermes_rerun_20261025',
    'claude-code': BASE / 'jobs_claude-code_rerun_20261025',
}
OLD_DIRS = {
    'hermes': BASE / 'jobs_hermes',
    'claude-code': BASE / 'jobs_claude-code',
}

def classify_trial(tdir):
    """Return (state, reward, err_type).
    state in {done, err, running/pending}"""
    rfile = tdir / 'verifier' / 'reward.txt'
    efile = tdir / 'exception.txt'
    if rfile.exists():
        try:
            rv = rfile.read_text().strip()
        except Exception:
            rv = ''
        # reward.txt may contain '1' or '0' (or float)
        try:
            rfloat = float(rv)
            reward = '1' if rfloat >= 1.0 else ('0' if rfloat == 0.0 else rv)
        except Exception:
            reward = rv
        err_type = ''
        if efile.exists():
            # has exception too (rare) - read first error class
            txt = efile.read_text(errors='replace')
            for line in txt.splitlines():
                if 'Error' in line:
                    err_type = line.strip().split(':')[-1].strip().split(' ')[0]
                    break
        return 'done', reward, err_type
    if efile.exists():
        txt = efile.read_text(errors='replace')
        err_type = 'Unknown'
        for line in txt.splitlines():
            ls = line.strip()
            if ls.endswith('Error') or ls.endswith('Exception') or 'Error:' in ls:
                # extract last token
                for cand in ['AgentTimeoutError','NonZeroAgentExitCode','RuntimeError','TimeoutError','VerifierTimeout','ValueError','ConnectionError','OSError']:
                    if cand in ls:
                        err_type = cand
                        break
                else:
                    err_type = ls.split()[-1].rstrip(':')
                break
        return 'err', None, err_type
    return 'running', None, ''

def scan_rerun(rdir):
    # find the dated subdir
    subs = [d for d in rdir.iterdir() if d.is_dir() and d.name.startswith('2026')]
    if not subs:
        return {'dirs':0,'done':0,'pass':0,'err':0,'running':0,'trials':{}}
    sub = subs[0]
    trials = {}
    for tdir in sorted(sub.iterdir()):
        if not tdir.is_dir():
            continue
        name = tdir.name.split('__')[0]  # strip __RANDOM suffix
        if name in ('config.json','job.log','lock.json','result.json'):
            continue
        state, reward, err_type = classify_trial(tdir)
        trials[name] = {'state':state,'reward':reward,'err_type':err_type,'dir':tdir.name}
    done = sum(1 for v in trials.values() if v['state']=='done')
    err  = sum(1 for v in trials.values() if v['state']=='err')
    run  = sum(1 for v in trials.values() if v['state']=='running')
    passn= sum(1 for v in trials.values() if v['state']=='done' and v['reward']=='1')
    return {'dirs':len(trials),'done':done,'pass':passn,'err':err,'running':run,'trials':trials}

def main():
    baseline = json.loads(OLD_BASELINE.read_text())
    out = {'meta':{'generated_at':'scan','canonical_tasks':87}, 'rerun':{}, 'old_baseline':{}}
    for h in ['hermes','claude-code']:
        rr = scan_rerun(RERUN_DIRS[h])
        out['rerun'][h] = {k:v for k,v in rr.items() if k!='trials'}
        out['rerun'][h+'_detail'] = rr['trials']
        ob = baseline.get(h,{})
        out['old_baseline'][h] = {'total':ob.get('total'),'done':ob.get('done'),'pass':ob.get('pass'),'exception':ob.get('exception')}
    # pairing table
    pair = []
    hermes_t = out['rerun']['hermes_detail']
    cc_t = out['rerun']['claude-code_detail']
    hermes_old = baseline.get('hermes',{}).get('trials',{})
    cc_old = baseline.get('claude-code',{}).get('trials',{})
    alltasks = sorted(set(list(hermes_t)+list(cc_t)+list(hermes_old)+list(cc_old)))
    for t in alltasks:
        row = {'task':t}
        for h, det, old in [('hermes',hermes_t,hermes_old),('claude-code',cc_t,cc_old)]:
            o = old.get(t,{})
            r = det.get(t,{})
            row[h+'_old_reward'] = o.get('reward')
            row[h+'_old_exc'] = o.get('exception')
            row[h+'_rerun_state'] = r.get('state')
            row[h+'_rerun_reward'] = r.get('reward')
            row[h+'_rerun_err'] = r.get('err_type')
        pair.append(row)
    out['pairing'] = pair
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__=='__main__':
    main()
