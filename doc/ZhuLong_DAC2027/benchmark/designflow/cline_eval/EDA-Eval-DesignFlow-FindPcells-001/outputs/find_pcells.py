# find_pcells.py
#
# pyAether script that lists every pcell instance in the current design's
# top block.
#
# It is meant to be executed inside Aether via:
#     import pyAether
#     pyAether.aeOpenDesign(<lib>, <cell>, <view>)
#     exec(open("find_pcells.py").read())
#
# The script prints, to stdout, one line per pcell instance with four fields
# separated by a single space:
#     <instance_name> <master_lib> <master_cell> <master_view>
#
# All diagnostic/error messages go to stderr so stdout stays clean for parsing.

import sys

import pyAether


def _s(value):
    """Return a plain str from an emyString-like value (or None)."""
    if value is None:
        return ""
    return str(value)


def _get_instances(block):
    """Return the instances directly owned by the given block as a list."""
    try:
        insts = block.getInsts()
    except Exception:
        return []
    if insts is None:
        return []
    if hasattr(insts, "__iter__"):
        return list(insts)
    return [insts]


def main():
    cv = pyAether.aeGetCurDesign()
    if cv is None:
        print("ERROR: no current design open", file=sys.stderr)
        return 1

    block = cv.getTopBlock()
    if block is None:
        print("ERROR: cannot get top block of current design", file=sys.stderr)
        return 1

    rows = []
    for inst in _get_instances(block):
        try:
            is_pcell = bool(pyAether.dbCheckIsPCell(inst))
        except Exception:
            is_pcell = False
        if not is_pcell:
            continue
        rows.append((
            _s(getattr(inst, "name", None)),
            _s(getattr(inst, "libName", None)),
            _s(getattr(inst, "cellName", None)),
            _s(getattr(inst, "viewName", None)),
        ))

    for row in rows:
        print(" ".join(row))

    return 0


main()