#!/usr/bin/env python3
"""SWE-bench Verified 20-pilot - prediction (run_harness.py) + docker eval."""

from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = "http://172.19.92.25:13128"
DATASET = "princeton-nlp/SWE-bench_Verified"
SPLIT = "test"
MODEL = os.environ.get("HARNESS_MODEL", "kimi-k2.6-cloud")
TIMEOUT_PRED = 1800
TIMEOUT_EVAL = 1800
WORKDIRS = Path("/dev/shm/harness_work/workdirs")
PILOT_DIR = HERE / "swebench_verified_pilot"
PILOT_DIR.mkdir(exist_ok=True)
REPO_MAP = {
    "astropy/astropy": "astropy_astropy",
    "django/django": "django_django",
    "sympy/sympy": "sympy_sympy",
    "matplotlib/matplotlib": "matplotlib_matplotlib",
    "pallets/flask": "pallets_flask",
}
