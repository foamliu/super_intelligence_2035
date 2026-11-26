import json
b = open('designflow/_tmp_ledger_sids_iter.b64').read().strip()
WD = '/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/default_designflow_B_shardB_loop_iter_0'
chunk = 3800
cmds = []
for i in range(0, len(b), chunk):
    piece = b[i:i+chunk]
    cmds.append("printf '%s' '" + piece + "' >> " + WD + "/sids.b64")
print('nchunks', len(cmds), 'totlen', len(b))
json.dump(cmds, open('designflow/_tmp_chunk_cmds.json', 'w'))
