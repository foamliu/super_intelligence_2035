#!/bin/bash
# vision VQA SSH bridge watchdog — keeps the reverse tunnel (.17 -> 36.15 via :3333) alive.
# Binds on 36.15 loopback: 127.0.0.1:13001/13002/13003 -> .17 127.0.0.1:30001/30002/30003.
# A python forwarder on 36.15 (0.0.0.0:3000x -> 127.0.0.1:1300x) exposes them to bridge
# containers via the docker0 gateway 10.247.64.1. Restart on any exit; reconnect <= ~20s.
LOG=/tmp/vqa_ssh_bridge_watchdog.log
echo "$(date '+%F %T') watchdog START pid=$$" >> "$LOG"
while true; do
  echo "$(date '+%F %T') [launch] ssh -R 13001/13002/13003" >> "$LOG"
  ssh -p 3333 -N \
      -o BatchMode=yes -o StrictHostKeyChecking=no \
      -o ServerAliveInterval=15 -o ServerAliveCountMax=3 \
      -o ExitOnForwardFailure=yes \
      -R 127.0.0.1:13001:127.0.0.1:30001 \
      -R 127.0.0.1:13002:127.0.0.1:30002 \
      -R 127.0.0.1:13003:127.0.0.1:30003 \
      app.e0031982@localhost >> "$LOG" 2>&1
  rc=$?
  echo "$(date '+%F %T') [exited] rc=$rc, restart in 5s" >> "$LOG"
  sleep 5
done
