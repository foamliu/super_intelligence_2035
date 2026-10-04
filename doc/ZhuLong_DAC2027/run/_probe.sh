#!/bin/bash
echo "PROBE_START"
date +%F
echo "---DISK---"
df -h /home
echo "---PORTS---"
for p in 8664 8665 8653 8669; do
  (echo > /dev/tcp/10.129.32.75/$p) >/dev/null 2>&1 && echo "port $p OPEN" || echo "port $p DOWN"
done
echo "---PGREP run_cline_script---"
pgrep -af 'run_cline_script' || echo "NO_RESIDUAL"
echo "---PGREP MCP python---"
pgrep -af 'server' || echo "NO_MCP_MATCH"
echo "PROBE_END"