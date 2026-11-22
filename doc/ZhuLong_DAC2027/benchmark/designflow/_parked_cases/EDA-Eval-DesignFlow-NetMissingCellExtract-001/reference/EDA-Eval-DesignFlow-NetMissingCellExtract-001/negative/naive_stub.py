#!/usr/bin/env python3
# negative: naive_stub -- only greps for lines containing '(' and counts any
# identifier-before-whitespace as a "cell". No simlib cross-check, no port
# parsing, wrong counts. Fails (g)/(h)/(j)/(m).
import re, json, sys
net = open(sys.argv[1]).read()
cells = re.findall(r'^\s*(\w+)\s+\w+\s*\(', net, re.M)
mi = [{"line": i+1, "cell": c, "instance": "I?", "ports": {}} \
      for i, c in enumerate(cells)]
print(json.dumps({
    "missing_instances": mi,
    "summary": {"total_instances": len(cells), "missing_count": len(cells),
                "available_count": 0, "missing_cells": sorted(set(cells)),
                "available_cells_used": []}
}))
