#!/apps/local/bin/python3
"""gen_preAA_G5_CIP_final_A.py  —  PG dummy + STI DRC flow (BUGGY, fixture context).

Builds deck_STI path, rsyncs calibreSTIcmp.rule into Run_Dir, sed-modifies
LAYOUT PATH/PRIMARY, then runs calibre -drc. Reproduces the OPEN1 error
trace from ellawu/cxmtG5_CIP.  DO NOT run as-is; it is context for fix.py.
"""
import os, sys

CONFIG_FILE = ".PG_DUMMY_for_Logic.config_A.txt"

def load_config(path):
    cfg = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
    return cfg

def compute_precision(processname_new):
    # G5_CIP uses 0.1nm grid -> precision 10000; others default 1000
    if processname_new in ("cxmtG5_CIP", "cxmtG5"):
        return "10000"
    return "1000"

def run_sti_drc(cfg, Run_Dir):
    processname_new = cfg.get("process", "")
    projName = cfg.get("projName", "")
    deckName_STI = "calibreSTIcmp.rule"
    # path construction (matches /apps/imctf/runset/calibre/<proc>/current/<proj>/runset/...)
    deck_STI = "/apps/imctf/runset/calibre/" + processname_new + "/current/" + projName + "/runset/" + deckName_STI
    # BUG 1: rsync return code never checked
    os.system("rsync -avzL " + deck_STI + " " + Run_Dir)
    # BUG 2: only LAYOUT PATH / PRIMARY rewritten; PRECISION computed but never injected
    os.system("sed -i 's,\\(LAYOUT path\\).*,\\1 LP4TOP.gds,' " + Run_Dir + "/" + deckName_STI)
    os.system("sed -i 's,\\(LAYOUT primary\\).*,\\1 LP4TOP,' " + Run_Dir + "/" + deckName_STI)
    precision = compute_precision(processname_new)   # computed but unused
    # BUG 3: no file-existence verification before calibre
    os.system("cd " + Run_Dir + "; calibre -drc -hier -turbo 4 " + deckName_STI + " |& tee run_STI.log")

if __name__ == "__main__":
    cfg = load_config(CONFIG_FILE)
    run_sti_drc(cfg, "/tmp/run_sti")
