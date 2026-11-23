#!/usr/bin/env bash
# baize_posttrain_llamacpp_speed_probe.sh -- G0/G1/G2 speed probe for the
# llama.cpp x Qwen3.5-2B (CPU) route that could unblock the A5 arm.
#
# WHY (2026-11-23 令): wake744 measured ~40 tok/s AGGREGATE on the self-written
# HF server; at -p 8 that is ~5 tok/s per agent -> mean task (12,453 output tok)
# ~2,491s ~= the 2,500s timeout -> 93.75% empty code. The open question is
# whether llama.cpp's real continuous batching lifts the AGGREGATE to >=100
# tok/s (single-stream 30-60 tok/s alone does NOT answer it).
#
# SCOPE: CPU only. No GPU. No 158-task eval. No protocol/task/check.py change.
#        No kill of other lines' processes. nice -n 19. ~45 min.
#
# Usage:
#   bash baize_posttrain_llamacpp_speed_probe.sh            # full probe
#   OUTDIR=/tmp/p1 THREADS_LIST="8 16" bash ...           # smaller sweep
#   MODEL=... GGUF_DIR=... LLAMA_DIR=... bash ...          # overrides
#
# Exit codes: 0 = assemble written; 2 = BLOCKED (convert/binary missing);
#             3 = probe ran but verdict != FEASIBLE (still 0? no: 3 = NOT_FEASIBLE)
set -uo pipefail

RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TS="$(date +%Y%m%d_%H%M%S)"
OUTDIR="${OUTDIR:-/tmp/baize_llamacpp_probe_${TS}}"
SUMMARY="${SUMMARY:-$RUN_DIR/llamacpp_speed_probe_${TS}.json}"
MODEL="${MODEL:-/nas_data/app.e0031982/models/Qwen3.5-2B}"
GGUF_DIR="${GGUF_DIR:-/nas_data/app.e0031982/models/qwen35_gguf}"
THREADS_LIST="${THREADS_LIST:-8 16 32}"
PORT="${PORT:-18097}"
CTX="${CTX:-131072}"
NPROC="$(nproc 2>/dev/null || echo 8)"
JOBS=$(( NPROC < 16 ? NPROC : 16 ))
PY="${PY:-/home/app.e0031982/code/eda_fastmcp/.venv/bin/python}"
[ -x "$PY" ] || PY="$(command -v python3 || echo python3)"
LOAD_PY="$RUN_DIR/baize_posttrain_llamacpp_speed_probe_load.py"

mkdir -p "$OUTDIR"
LOG="$OUTDIR/probe.log"
exec > >(tee -a "$LOG") 2>&1

echo "============================================================"
echo " llama.cpp x Qwen3.5-2B CPU speed probe"
echo " host=$(hostname)  nproc=$NPROC  date=$(date '+%F %T')"
echo " model=$MODEL"
echo " outdir=$OUTDIR"
echo "============================================================"

# ---------- Phase 0: environment ----------
echo "[P0] environment"
lscpu 2>/dev/null | grep -E 'Model name|^CPU\(s\)|Thread|Core|Socket|NUMA' | head -12
free -g 2>/dev/null | head -3
df -h "$GGUF_DIR" 2>/dev/null | tail -1 || true
command -v cmake >/dev/null 2>&1 && cmake --version | head -1 || echo "[P0] WARN cmake missing"
"$PY" -c 'import sys;print("python",sys.version.split()[0])' 2>/dev/null || echo "[P0] WARN python unusable"

F16="$GGUF_DIR/qwen3.5-2b-f16.gguf"
Q4="$GGUF_DIR/qwen3.5-2b-Q4_K_M.gguf"
CONVERT_OK=0
SERVER_UP=0
LLAMA_DIR="${LLAMA_DIR:-}"
LLAMA_REV="unknown"
QUANT_FILE=""
TOOL_SUPPORT="unknown"

# ---------- Phase 1: locate / build llama.cpp (G0 arch gate) ----------
echo "[P1] locate llama.cpp"
if [ -z "$LLAMA_DIR" ]; then
  for c in "$HOME/tools/llama.cpp" /nas_data/app.e0031982/tools/llama.cpp \
           /home/app.e0031982/tools/llama.cpp /nas_train/app.e0031982/tools/llama.cpp; do
    if [ -x "$c/build/bin/llama-server" ]; then LLAMA_DIR="$c"; break; fi
  done
fi
if [ -z "$LLAMA_DIR" ]; then
  BIN_SYS="$(command -v llama-server 2>/dev/null || true)"
  if [ -n "$BIN_SYS" ]; then LLAMA_DIR="$(cd "$(dirname "$BIN_SYS")/.." && pwd)"; fi
fi
if [ -z "$LLAMA_DIR" ]; then
  echo "[P1] no llama.cpp found -> clone + build (needs proxy)"
  export https_proxy="${https_proxy:-http://172.19.92.25:13128}"
  export http_proxy="${http_proxy:-$https_proxy}"
  mkdir -p "$HOME/tools"
  timeout 600 git clone --depth 1 https://github.com/ggml-org/llama.cpp "$HOME/tools/llama.cpp" \
    || echo "[P1] BLOCKED git clone failed"
  LLAMA_DIR="$HOME/tools/llama.cpp"
fi
BIN="$LLAMA_DIR/build/bin"
if [ ! -x "$BIN/llama-server" ] && [ -d "$LLAMA_DIR" ]; then
  echo "[P1] building (GGML_NATIVE=ON, -j$JOBS)"
  cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" -DGGML_NATIVE=ON -DLLAMA_CURL=OFF \
    || echo "[P1] BLOCKED cmake configure failed"
  timeout 1800 cmake --build "$LLAMA_DIR/build" -j "$JOBS" \
      --target llama-server llama-bench llama-quantize \
    || echo "[P1] WARN build incomplete"
fi
[ -x "$BIN/llama-server" ] || BIN="$(dirname "$(command -v llama-server 2>/dev/null || echo /nonexistent/x)")"
"$BIN/llama-server" --version 2>&1 | head -3 || true
if [ -d "$LLAMA_DIR/.git" ]; then
  LLAMA_REV="$(git -C "$LLAMA_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
fi
echo "[P1] LLAMA_DIR=$LLAMA_DIR rev=$LLAMA_REV bin=$BIN"

# ---------- Phase 2: HF -> F16 GGUF (the make-or-break arch gate) ----------
echo "[P2] convert HF -> F16 GGUF"
mkdir -p "$GGUF_DIR" 2>/dev/null || { echo "[P2] WARN cannot mkdir $GGUF_DIR"; GGUF_DIR="$OUTDIR"; F16="$GGUF_DIR/qwen3.5-2b-f16.gguf"; Q4="$GGUF_DIR/qwen3.5-2b-Q4_K_M.gguf"; }
if [ -f "$F16" ]; then
  echo "[P2] F16 exists: $(du -h "$F16" | cut -f1)"
  CONVERT_OK=1
else
  [ -f "$LLAMA_DIR/convert_hf_to_gguf.py" ] || echo "[P2] BLOCKED convert_hf_to_gguf.py missing"
  "$PY" -c 'import gguf' 2>/dev/null || "$PY" -m pip install -q --disable-pip-version-check -U gguf 2>&1 | tail -2
  RC=1
  if [ -f "$LLAMA_DIR/convert_hf_to_gguf.py" ]; then
    timeout 2400 "$PY" "$LLAMA_DIR/convert_hf_to_gguf.py" "$MODEL" \
        --outfile "$F16" --outtype f16 2>&1 | tail -40
    RC=${PIPESTATUS[0]}
  fi
  if [ "$RC" -eq 0 ] && [ -f "$F16" ]; then
    CONVERT_OK=1
    echo "[P2] converted: $(du -h "$F16" | cut -f1)"
  else
    echo "[P2] BLOCKED convert rc=$RC (capture full stderr above; likely unsupported model type qwen3_5)"
  fi
fi

# ---------- Phase 2b: quantize Q4_K_M (throughput variant) ----------
echo "[P2b] quantize Q4_K_M"
if [ "$CONVERT_OK" -eq 1 ] && [ -x "$BIN/llama-quantize" ]; then
  if [ ! -f "$Q4" ]; then
    timeout 1800 "$BIN/llama-quantize" "$F16" "$Q4" Q4_K_M 2>&1 | tail -5
  fi
fi
if [ -f "$Q4" ]; then
  QUANT_FILE="$Q4"
  echo "[P2b] using Q4_K_M: $(du -h "$Q4" | cut -f1)"
elif [ -f "$F16" ]; then
  QUANT_FILE="$F16"
  echo "[P2b] WARN quantize unavailable -> using F16 (slower; decode is bandwidth-bound)"
fi

# ---------- Phase 3: llama-bench thread sweep (G1) ----------
echo "[P3] llama-bench sweep: threads=$THREADS_LIST"
BENCH_ROWS=""
if [ "$CONVERT_OK" -eq 1 ] && [ -x "$BIN/llama-bench" ] && [ -n "$QUANT_FILE" ]; then
  for T in $THREADS_LIST; do
    [ "$T" -le "$NPROC" ] || { echo "[P3] skip -t $T (> nproc $NPROC)"; continue; }
    echo "[P3] -t $T"
    timeout 900 nice -n 19 env OMP_NUM_THREADS=1 "$BIN/llama-bench" \
        -m "$QUANT_FILE" -t "$T" -p 512 -n 128 -r 3 2>&1 | tee "$OUTDIR/bench_${T}.log" | tail -12
  done
else
  echo "[P3] SKIP (no binary/model)"
fi

# ---------- Phase 4: server + 8-way aggregate load (G2) ----------
echo "[P4] start llama-server --parallel 8"
# pick the thread count with the fastest tg128 (single-stream decode) from P3
BEST_T=""
if ls "$OUTDIR"/bench_*.log >/dev/null 2>&1; then
  BEST_T="$("$PY" - "$OUTDIR" <<'PYEOF'
import glob, os, re, sys
best = (0.0, "")
for p in glob.glob(os.path.join(sys.argv[1], "bench_*.log")):
    m = re.search(r"bench_(\d+)", os.path.basename(p))
    if not m:
        continue
    t = m.group(1)
    for line in open(p, errors="replace"):
        mm = re.search(r"\|\s*tg128\s*\|\s*([0-9.]+)", line)
        if mm and float(mm.group(1)) > best[0]:
            best = (float(mm.group(1)), t)
print(best[1])
PYEOF
)"
fi
[ -n "$BEST_T" ] || BEST_T=8
echo "[P4] BEST_T=$BEST_T (from llama-bench tg128)"
# pick threads of the fastest tg128 if parsable later; start with the largest <= nproc
SERVER_PID=""
start_server() {
  local extra="$1"
  echo "[P4] spawn: -t $BEST_T $extra"
  CUDA_VISIBLE_DEVICES="" nice -n 19 "$BIN/llama-server" -m "$QUANT_FILE" \
      -t "$BEST_T" -tb "$BEST_T" -c "$CTX" --parallel 8 --metrics \
      --temp 0 --top-k 1 --seed 1234 --host 127.0.0.1 --port "$PORT" \
      --no-warmup --slots $extra > "$OUTDIR/server.log" 2>&1 &
  SERVER_PID=$!
  for _ in $(seq 1 90); do
    if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then return 0; fi
    kill -0 "$SERVER_PID" 2>/dev/null || return 1
    sleep 2
  done
  return 1
}

if [ "$CONVERT_OK" -eq 1 ] && [ -n "$QUANT_FILE" ] && [ -x "$BIN/llama-server" ]; then
  if ! start_server "--jinja"; then
    echo "[P4] WARN --jinja failed (see server.log); retry without --jinja"
    [ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null
    sleep 5
    for _ in $(seq 1 10); do
      curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || break
      sleep 2
    done
    if start_server ""; then TOOL_SUPPORT="no_jinja"; fi
  else
    TOOL_SUPPORT="jinja"
  fi
  if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    SERVER_UP=1
    echo "[P4] server up (pid=$SERVER_PID)"
    "$PY" "$LOAD_PY" load --port "$PORT" --concurrency 1 --max-tokens 256 \
        --rounds 2 --prompt-words 100 --out "$OUTDIR/load_c1.json"
    "$PY" "$LOAD_PY" load --port "$PORT" --concurrency 8 --max-tokens 256 \
        --rounds 3 --prompt-words 500 --out "$OUTDIR/load_c8.json"
    "$PY" "$LOAD_PY" load --port "$PORT" --concurrency 8 --max-tokens 256 \
        --rounds 2 --prompt-words 3000 --out "$OUTDIR/load_c8_long.json"
  else
    echo "[P4] BLOCKED server never became healthy"
  fi
else
  echo "[P4] SKIP (no server binary/model)"
fi

# ---------- Phase 5: bench parse + env + assemble ----------
echo "[P5] parse bench logs"
"$PY" - "$OUTDIR" <<'PYEOF'
import glob, json, os, re, sys
d = sys.argv[1]
by_t = {}
for path in sorted(glob.glob(os.path.join(d, "bench_*.log"))):
    m = re.search(r"bench_(\d+)", os.path.basename(path))
    if not m:
        continue
    threads = int(m.group(1))
    for line in open(path, errors="replace"):
        mm = re.search(r"\|\s*(pp512|tg128)\s*\|\s*([0-9.]+)", line)
        if mm:
            by_t.setdefault(threads, {"threads": threads})[mm.group(1) + "_tok_s"] = float(mm.group(2))
out = {"rows": [by_t[k] for k in sorted(by_t)]}
with open(os.path.join(d, "bench.json"), "w") as fh:
    json.dump(out, fh, indent=2)
print(json.dumps(out, indent=2))
PYEOF

if [ -n "${SERVER_PID:-}" ]; then
  echo "[P5] stop our llama-server pid=$SERVER_PID"
  kill "$SERVER_PID" 2>/dev/null || true
  sleep 3
  kill -9 "$SERVER_PID" 2>/dev/null || true
fi

export PROBE_HOSTNAME="$(hostname)"
export PROBE_NPROC="$NPROC"
export PROBE_LLAMA_DIR="$LLAMA_DIR"
export PROBE_LLAMA_REV="$LLAMA_REV"
export PROBE_MODEL="$MODEL"
export PROBE_QUANT_FILE="$QUANT_FILE"
export PROBE_THREADS_LIST="$THREADS_LIST"
export PROBE_CTX="$CTX"
export PROBE_CONVERT_OK="$CONVERT_OK"
export PROBE_SERVER_UP="$SERVER_UP"
export PROBE_TOOL_SUPPORT="$TOOL_SUPPORT"
export PROBE_OUTDIR="$OUTDIR"
export PROBE_GGUF_F16_EXISTS=0
[ -f "$F16" ] && export PROBE_GGUF_F16_EXISTS=1
export PROBE_QUANT_EXISTS=0
[ -n "$QUANT_FILE" ] && [ -f "$QUANT_FILE" ] && export PROBE_QUANT_EXISTS=1
"$PY" - "$OUTDIR/env.json" <<'PYEOF'
import json, os, sys
d = {k[6:].lower(): v for k, v in os.environ.items() if k.startswith("PROBE_")}
d["gguf_f16_exists"] = d.get("gguf_f16_exists") == "1"
d["quant_exists"] = d.get("quant_exists") == "1"
d["convert_ok"] = d.get("convert_ok") == "1"
d["server_up"] = d.get("server_up") == "1"
with open(sys.argv[1], "w") as fh:
    json.dump(d, fh, indent=2)
print(json.dumps(d, indent=2))
PYEOF

echo "[P5] assemble verdict"
"$PY" "$LOAD_PY" assemble --dir "$OUTDIR" --out "$SUMMARY"
RC=$?
echo "[P5] summary=$SUMMARY rc=$RC"
echo "============================================================"
echo " DONE $(date '+%F %T')  log=$LOG"
echo "============================================================"
exit "$RC"

