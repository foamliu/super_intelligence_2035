import json, glob
from collections import defaultdict

cnt = defaultdict(lambda: {'total': 0, 'patch': 0, 'no_patch': 0})

def has_patch(path):
    try:
        d = json.load(open(path))
        if isinstance(d, list):
            for item in d:
                if isinstance(item, dict) and item.get('model_patch', '').strip():
                    return True
            return False
        elif isinstance(d, dict):
            return bool(d.get('model_patch', '').strip())
        return False
    except Exception:
        return False

for f in glob.glob('*.json'):
    # exclude gate aggregate files: predictions_<harness>.json
    if f.startswith('predictions_') and '__' not in f:
        continue
    h = f.split('__', 1)[0]
    cnt[h]['total'] += 1
    if has_patch(f):
        cnt[h]['patch'] += 1
    else:
        cnt[h]['no_patch'] += 1

full_h = ['cline-patched', 'opencode', 'pi', 'claude-code', 'codex']
gt = gp = gnp = 0
for h in sorted(cnt):
    c = cnt[h]
    flag = 'FULL' if h in full_h else 'gate'
    print('%-20s %-5s total=%4d patch=%4d no_patch=%4d' % (h, flag, c['total'], c['patch'], c['no_patch']))
    if h in full_h:
        gt += c['total']; gp += c['patch']; gnp += c['no_patch']
print('--- FULL5 TOTAL=%d patch=%d no_patch=%d (%.1f%% of 2500) ---' % (gt, gp, gnp, gt * 100.0 / 2500))

