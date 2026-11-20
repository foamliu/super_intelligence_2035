# tests/drcCountWithinOption/run_test.py -- smoke test skeleton for checker 'drcCountWithinOption'.
import os, sys, importlib, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import test_env
import DrcQa

def run():
    case_dir = os.environ.get("CASE_DIR", os.getcwd())
    qa = DrcQa.DrcQa(case_dir, deck="calibre")
    try:
        r = qa.run(["drcCountWithinOption"])
        print("[0] {}".format(r.get("drcCountWithinOption", {}).get("status", "?")))
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    run()
