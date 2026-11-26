import sys, os
sys.path.insert(0, "/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/default_designflow-shardD-331_shardD-331_0")
import importlib.util
spec = importlib.util.spec_from_file_location("pd", "/tmp/peek_dirbased.py")
pd = importlib.util.module_from_spec(spec); spec.loader.exec_module(pd)

TARGETS = [
    ("1792570431387_vdqlw", "ypzheng", "hfeg0pkn003"),       # analog_context mc335
    ("1792400027384_ahjnv", "zhukaic", "hfeahpc503"),        # analog_context mc397
    ("1787897609476_ooyxi", "sophiaw", "hfeg0plg09"),        # analog_context mc394
    ("1793093197648_x2w2z", "yueliu", "hfeahpc501"),         # waveform mc303
    ("1787903140887_314mt", "sophiaw", "hfeg0plg09"),        # analog_context mc378
    ("1791425782404_rn6pm", "yohannw", "hfeg0pkn003"),       # analog_context mc322
    ("1791958525711_f1fik", "chengleiy", "hfeg0pkn001"),     # schematic_netlist mc504
    ("1792487689184_4ybw1", "yan1zh", "hfeg0plg65"),         # schematic_netlist mc495
]

import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(pd.peek_one, t): t for t in TARGETS}
    for fu in concurrent.futures.as_completed(futs):
        try:
            sid, user, ip, turns, sz = fu.result()
        except Exception as e:
            t = futs[fu]; sid, user, ip, turns, sz = t[0], t[1], t[2], ["EXC:"+str(e)], "?"
        print("### %s | %s@%s | size=%s | nturns=%d" % (sid, user, ip, sz, len(turns)))
        for i, tn in enumerate(turns[:8]):
            print("  [U#%d] %s" % (i, tn[:400].replace("\n", " ")))
        print("---")
