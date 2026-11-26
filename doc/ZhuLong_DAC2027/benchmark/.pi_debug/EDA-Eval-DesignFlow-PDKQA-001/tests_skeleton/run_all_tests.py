# run_all_tests.py -- smoke-test runner for the 17 registered DRC checkers.
import os, sys, importlib, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import test_env

import DrcQa
from DrcQa import SUPPORT_FUNCNAMES, TEXT_CHECKERS, PATTERN_CHECKERS


def main():
    case_dir = os.environ.get("CASE_DIR", os.path.join(os.getcwd(), "shared", "0806_zhaowei"))
    qa = DrcQa.DrcQa(case_dir, deck="calibre")
    results = qa.run()
    lines = []
    for name in SUPPORT_FUNCNAMES:
        r = results.get(name, {})
        status = r.get("status", "?")
        lines.append(f"- {name}: {status}")
    report = "# DRC QA smoke report\n\n" + "\n".join(lines) + "\n"
    with open("smoke_report.md", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
