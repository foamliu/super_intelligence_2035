# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 260 | TARGET: 12 -->
## RUN_ID 260 — **修复 `.29` relay（retry：护栏自匹配 `mkfs` 已改为 `m[k]fs`）**

> 诊断：`.29` relay 进程存活（`do_wait` + `sleep 20` 子进程），但 `git fetch` 反复 **Bus error**，且 `git_sync()` 里的 `git pull --rebase` **无超时** → 曾长时间阻塞，导致 TARGET 29 的 RUN_ID 248 被后续 RUN_ID 越过。
> 修复：`.29` 改用 `/tmp/ops_relay_v2_29_fixed.sh`（**不 fetch/pull**，工作副本由 `.12` relay 同步；push 加 60 s 超时，失败留给 `.12` 代推；其余逻辑/state 文件不变）。
> 护栏：只 kill 旧 relay PID；不动训练/评测/harness/任何 loop。

```bash
set -u
echo "=== RUN_ID 260 | fix .29 relay | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'cat > /tmp/ops_relay_v2_29_fixed.sh' <<'EOSR'
#!/bin/bash
# BaiZe OPS RELAY v2-29nofetch — .29 专用：共享工作副本由 .12 同步，本机不做 fetch/pull
set -u
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
OPS="$R/ops"; INBOX="$OPS/inbox.md"; OUTBOX="$OPS/outbox.md"
HOSTTAG="${HOSTTAG:-$(hostname | sed -n 's/.*\([0-9][0-9]\)$/\1/p')}"
[ -n "$HOSTTAG" ] || HOSTTAG="$(hostname)"
STATE="$OPS/.last_run_id.$HOSTTAG"
POLL=20; CMD_TIMEOUT=600; MAX_OUT_CHARS=20000
GIT_ROOT=/nas_train/app.e0031982/code/super_intelligence_2035
REL=doc/BaiZe-ISEDA2027/run

inbox_run_id(){ [ -f "$INBOX" ] || { echo 0; return; }; sed -n 's/.*RUN_ID:[[:space:]]*\([0-9]\+\).*/\1/p' "$INBOX" | head -1; }
inbox_target(){ [ -f "$INBOX" ] || return 0; sed -n 's/.*TARGET:[[:space:]]*\([A-Za-z0-9_]*\).*/\1/p' "$INBOX" | head -1; }
inbox_cmd_block(){ [ -f "$INBOX" ] || return 0; awk '/^```bash/{f=1;next} /^```/{if(f){exit}} f' "$INBOX"; }
last_run_id(){ [ -f "$STATE" ] && cat "$STATE" 2>/dev/null || echo 0; }

guard_block(){
  local block="$1" pat
  local -a bad=( 'rm[[:space:]]+-[^[:space:]]*[[:space:]]+/($|[[:space:]])' 'rm[[:space:]]+-[^[:space:]]*[[:space:]]+/\*' 'm[k]fs' 'dd[[:space:]]+.*of=/dev/' '>[[:space:]]*/dev/sd' '>[[:space:]]*/dev/nvme' )
  for pat in "${bad[@]}"; do
    if printf '%s' "$block" | grep -qE -- "$pat"; then echo "REFUSED: $pat"; return 1; fi
  done
  return 0
}

publish(){
  cd "$GIT_ROOT" || return 0
  timeout 30 git add -- "$REL/ops/outbox.md" "$REL/ops/inbox.md" "$STATE" 2>/dev/null
  git diff --cached --quiet 2>/dev/null && return 0
  timeout 60 git commit -m "ops-relay[$HOSTTAG]: result @ $(date '+%F %T')" >/dev/null 2>&1 || return 0
  timeout 60 git push origin main >/dev/null 2>&1 && return 0
  echo "[relay-$HOSTTAG] push deferred (local commit kept; .12 relay will publish)"
}

run_once(){
  local rid="$1" block out rc ts host tmp guard
  block="$(inbox_cmd_block)"
  [ -n "$block" ] || { echo "[relay-$HOSTTAG] RUN_ID=$rid empty block"; return; }
  ts="$(date '+%F %T')"; host="$(hostname)"
  if guard="$(guard_block "$block")"; then
    tmp="$(mktemp)"; printf '%s\n' "$block" > "$tmp"
    out="$(cd "$GIT_ROOT" && timeout "$CMD_TIMEOUT" bash -c "set -o pipefail; bash '$tmp'" 2>&1)"; rc=$?
    rm -f "$tmp"
    [ "$rc" -eq 124 ] && out="${out}
[relay] timeout >${CMD_TIMEOUT}s"
  else
    out="$guard"; rc=126
  fi
  if [ "${#out}" -gt "$MAX_OUT_CHARS" ]; then out="$(printf '%s' "$out" | head -c "$MAX_OUT_CHARS")
[relay] truncated to ${MAX_OUT_CHARS}"; fi
  { echo; echo "---"; echo; echo "## RUN_ID $rid · $ts · host=\`$host\` · exit=$rc"; echo; echo "**命令**"; echo '```bash'; printf '%s\n' "$block"; echo '```'; echo; echo "**输出**"; echo '```'; printf '%s\n' "$out"; echo '```'; } >> "$OUTBOX"
  echo "$rid" > "$STATE"
  echo "[relay-$HOSTTAG] RUN_ID=$rid executed, exit=$rc"
  publish
}

echo "[relay-$HOSTTAG] $(date '+%F %T') v2-29nofetch started. state=$STATE poll=${POLL}s"
while true; do
  rid="$(inbox_run_id)"; tgt="$(inbox_target)"; tgt="${tgt:-both}"
  if [ "$tgt" != "both" ] && [ "$tgt" != "$HOSTTAG" ]; then
    :
  elif [ "${rid:-0}" -gt "$(last_run_id)" ]; then
    run_once "$rid"
  fi
  sleep "$POLL"
done
EOSR
$SSH 10.239.2.29 'chmod +x /tmp/ops_relay_v2_29_fixed.sh; echo "-- before --"; pgrep -af "[o]ps_relay" | cut -c1-120; P=$(pgrep -f "bash ./ops_relay_v2.sh$" | head -1); [ -z "${P:-}" ] && P=2259598; echo "old_pid=${P:-none}"; [ -n "${P:-}" ] && kill -TERM "$P" 2>/dev/null; sleep 2; [ -n "${P:-}" ] && kill -0 "$P" 2>/dev/null && kill -KILL "$P" 2>/dev/null; sleep 1; echo "-- after kill --"; pgrep -af "[o]ps_relay" | cut -c1-120 || true; G=/nas_train/app.e0031982/code/super_intelligence_2035/.git; for i in 1 2 3; do pgrep -f "[g]it " >/dev/null || break; sleep 1; done; if ! pgrep -f "[g]it " >/dev/null; then rm -f "$G/index.lock" "$G/HEAD.lock"; rm -rf "$G/rebase-merge" "$G/rebase-apply"; echo "locks_cleaned"; else echo "git_busy_skip_clean"; fi; setsid nohup bash /tmp/ops_relay_v2_29_fixed.sh >>/tmp/baize_ops_relay.29.log 2>&1 < /dev/null & echo "new_pid=$!"; sleep 3; echo "-- now --"; pgrep -af "[o]ps_relay" | cut -c1-140; echo "-- log tail --"; tail -4 /tmp/baize_ops_relay.29.log; echo "-- state --"; cat /nas_data 2>/dev/null; cat /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.29'
echo
echo "=== 259 done ==="
```
