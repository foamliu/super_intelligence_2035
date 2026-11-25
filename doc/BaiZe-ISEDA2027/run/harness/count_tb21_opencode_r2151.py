#!/usr/bin/env python3
"""Count TB-2.1 opencode rerun results from harbor trial result.json files."""
import json, glob, os, sys

RD = sys.argv[1] if len(sys.argv) > 1 else '/tmp/tb21_glm53_jobs/opencode/2026-11-10__14-27-04'
trials = sorted(glob.glob(os.path.join(RD, '*/')))
trials = [t for t in trials if os.path.basename(t.rstrip('/')) != 'lock.json']

passc = 0; failc = 0; errc = 0; running = 0; pend = 0; other = 0
done_tasks = []
for t in trials:
    rj = os.path.join(t, 'result.json')
    if not os.path.exists(rj):
        pend += 1
        continue
    try:
        d = json.load(open(rj))
        finished = d.get('finished_at') is not None
        exc = d.get('exception_info')
        vr = d.get('verifier_result') or {}
        rewards = vr.get('rewards', {}) if isinstance(vr, dict) else {}
        reward = rewards.get('reward', None) if isinstance(rewards, dict) else None
        tname = d.get('task_name', os.path.basename(t.rstrip('/')))
        if not finished:
            running += 1
        elif exc and exc.get('exception_type'):
            errc += 1
        elif reward == 1.0 or reward == 1:
            passc += 1
            done_tasks.append(tname)
        elif reward == 0.0 or reward == 0:
            failc += 1
        else:
            other += 1
    except Exception:
        other += 1

total_done = passc + failc + errc
print('TB-2.1 opencode run-dir: %s' % RD)
print('trial dirs=%d  pass=%d  fail=%d  err=%d  running=%d  pending=%d  other=%d' % (
    len(trials), passc, failc, errc, running, pend, other))
print('done=%d / 89  (pass+fail+err)' % total_done)
