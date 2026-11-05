#!/apps/local/bin/python3
#=============================================================
# File Name: drc_auto.py
# Description: Calibre DRC rule deck auto-render driver.
#              Reads a rule template + an EV (env/option) file,
#              renders per-metal-option DRC decks and launches
#              calibre -drc on each.
#=============================================================
import os
import sys
import re
import json
from typing import List, Dict, Tuple

COMMENT_FILE_CACHE: Dict[str, str] = {}
COMMENT_FILE_PATH = os.environ.get("COMMENT_FILE_PATH", "")
EV_VARS: Dict[str, str] = {}


def parse_args(argv: List[str]) -> Tuple[str, int, int, Dict[str, str]]:
    if len(argv) < 3:
        sys.stderr.write("usage: drc_auto.py <rule> <xa> <ya> [key=val ...]\n")
        sys.exit(2)
    rule = argv[1]
    xa = int(argv[2])
    ya = int(argv[3])
    user_vars: Dict[str, str] = {}
    for kv in argv[4:]:
        if "=" in kv:
            k, v = kv.split("=", 1)
            user_vars[k] = v
    return rule, xa, ya, user_vars


def load_ev(ev_path: str) -> Dict[str, str]:
    with open(ev_path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                EV_VARS[k.strip()] = v.strip()
    return dict(EV_VARS)


def render_block(blk: Dict[str, str], dollar: Dict[str, str],
                 user_vars: Dict[str, str], source_map: Dict[str, str]) -> str:
    cond = blk.get("cond", "")
    if cond:
        cond_str = cond
        for k, v in dollar.items():
            cond_str = cond_str.replace("$<" + k + ">", repr(v))
        cond_val = bool(eval(cond_str))
        if not cond_val:
            return ""
    body = blk.get("body", "")
    out = body
    for k, v in dollar.items():
        out = out.replace("$<" + k + ">", str(v))
    return out


def render_template(blocks: List[Dict[str, str]], dollar: Dict[str, str],
                    user_vars: Dict[str, str], source_map: Dict[str, str]) -> List[str]:
    rendered_lines: List[str] = []
    for blk in blocks:
        out = render_block(blk, dollar, user_vars, source_map)
        if out:
            rendered_lines.append(out)
    return rendered_lines


def main() -> None:
    rule, xa, ya, user_vars = parse_args(sys.argv)
    ev_path = user_vars.get("ev", "main.rule")
    load_ev(ev_path)
    dollar = dict(EV_VARS)
    dollar.update(user_vars)
    blocks: List[Dict[str, str]] = []
    with open(rule, "r") as fh:
        for line in fh:
            if line.strip():
                blocks.append({"cond": "", "body": line.rstrip("\n")})
    rendered = render_template(blocks, dollar, user_vars, {})
    out_dir = os.path.join(os.path.dirname(os.path.abspath(rule)), "out")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "rendered.drc")
    with open(out_file, "w") as fh:
        fh.write("\n".join(rendered) + "\n")
    print("rendered -> " + out_file)


if __name__ == "__main__":
    main()
