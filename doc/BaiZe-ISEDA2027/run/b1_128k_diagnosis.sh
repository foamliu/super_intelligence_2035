#!/bin/bash
# B1 Step 1: 128K rejection diagnosis for BaiZe Mamba2-hybrid on sglang
# GPU1 only (GPU0 = A v2 eval running). ~15 min time box.
set -uo pipefail

SGLANG_PY=/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python
HF=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_hybrid/hf_iter_5000
PORT=30001
LOG=/tmp/b1_sglang_server.log
RESULTS=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/b1_128k_diagnosis.json

echo "===== B1 Step 1: 128K rejection diagnosis ====="
echo "[$(date)] Model: $HF (max_pos=4096, rope_theta=default, rope_scaling=none)"
echo "[$(date)] GPU1, port $PORT, sglang 0.5.9"
echo ""

export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
export CUDA_VISIBLE_DEVICES=1
echo "[$(date)] Starting sglang on GPU1..."
nohup $SGLANG_PY -m sglang.launch_server \
    --model-path "$HF" --host 0.0.0.0 --port $PORT \
    --context-length 131072 --trust-remote-code \
    --mem-fraction-static 0.85 --attention-backend flashinfer \
    --log-level info --mamba-ssm-dtype float32 \
    > $LOG 2>&1 &
SRV_PID=$!
echo "  PID=$SRV_PID, log=$LOG"

echo "[$(date)] Waiting for health..."
READY=0
for i in $(seq 1 30); do
    sleep 10
    if curl -s http://127.0.0.1:$PORT/health >/dev/null 2>&1; then
        READY=1; echo "  Ready after $((i*10))s"; break
    fi
    if ! kill -0 $SRV_PID 2>/dev/null; then
        echo "  ERROR: Server died. Log:"; tail -30 $LOG; exit 1
    fi
    echo -n " ${i}0s..."
done
echo ""
if [ $READY -eq 0 ]; then
    echo "ERROR: Server not ready after 300s"; tail -30 $LOG
    kill $SRV_PID 2>/dev/null || true; exit 1
fi

echo ""
echo "=== /v1/models ==="
curl -s http://127.0.0.1:$PORT/v1/models 2>&1 | head -10

echo ""
echo "[$(date)] Sending test requests (4K, 64K, 128K)..."
$SGLANG_PY << 'PYEOF'
import json, time, requests
PORT=30001; BASE=f"http://127.0.0.1:{PORT}"
RF="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/b1_128k_diagnosis.json"
sentence="The quick brown fox jumps over the lazy dog. "
results=[]
for target in [4096, 65536, 131072]:
    n_reps=int(target/9)+100
    prompt=sentence*n_reps
    est=len(prompt)//4
    print(f"\n=== target={target}, est_tokens~{est}, chars={len(prompt)} ===")
    try:
        t0=time.time()
        resp=requests.post(f"{BASE}/v1/completions",
            json={"model":"default","prompt":prompt,"max_tokens":16,"temperature":0},
            timeout=300)
        el=time.time()-t0
        print(f"  HTTP {resp.status_code}, {el:.2f}s")
        try:
            body=resp.json()
            pt=body.get("usage",{}).get("prompt_tokens",-1)
            ct=body.get("usage",{}).get("completion_tokens",-1)
            print(f"  prompt_tokens={pt}, completion_tokens={ct}")
            if ct==0 or resp.status_code!=200:
                print(f"  *** REJECTED *** Response:")
                print(json.dumps(body,indent=2,ensure_ascii=False)[:3000])
            else:
                ch=body.get("choices",[])
                if ch: print(f"  Generated: '{ch[0].get("text","")[:80]}'")
            results.append({"target_ctx":target,"est_tokens":est,"http_status":resp.status_code,
                "elapsed_s":round(el,3),"prompt_tokens":pt,"completion_tokens":ct,"response":body})
        except Exception as e:
            print(f"  Non-JSON: {resp.text[:500]}")
            results.append({"target_ctx":target,"est_tokens":est,"http_status":resp.status_code,
                "elapsed_s":round(el,3),"raw":resp.text[:1000]})
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        results.append({"target_ctx":target,"est_tokens":est,"error":str(e)})
out={"experiment":"B1_128k_diagnosis","timestamp":time.strftime('%Y-%m-%d %H:%M:%S'),
    "server":"--context-length 131072 --mem-fraction-static 0.85 --mamba-ssm-dtype float32",
    "model":"p3_hybrid/hf_iter_5000 max_pos=4096 rope_theta=default rope_scaling=none",
    "sglang_version":"0.5.9","results":results}
with open(RF,"w") as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(f"\nSaved to {RF}")
PYEOF

echo ""
echo "[$(date)] Killing sglang (PID=$SRV_PID)..."
kill $SRV_PID 2>/dev/null || true; sleep 5; kill -9 $SRV_PID 2>/dev/null || true

echo ""
echo "===== Server log: context/limit/error lines ====="
grep -i 'context\|token\|limit\|error\|reject\|exceed\|overflow\|max_total\|max_position\|131072\|4096\|too.long' $LOG 2>/dev/null | tail -50
echo ""
echo "===== Server log: last 20 lines ====="
tail -20 $LOG 2>/dev/null
echo ""
echo "[$(date)] B1 Step 1 done. Results: $RESULTS"
