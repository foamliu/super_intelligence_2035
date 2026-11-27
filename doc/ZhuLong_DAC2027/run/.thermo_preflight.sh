#!/bin/bash
export PATH=/home/app.e0031982/.local/node-20/bin:$HOME/.bun/bin:$PATH
export https_proxy=http://172.19.92.23:13128
cd /nasdata/app.e0031982/code/EDA-Flow-Bench
{
echo "=== cline in PATH ==="; command -v cline
echo "=== hub port 25463 health ==="; curl -s --max-time 5 http://127.0.0.1:25463/health 2>&1 | head -c 200; echo
echo "=== hub daemon PID 1448806 ==="; ps -p 1448806 -o pid,etime,rss,cmd --no-headers 2>/dev/null || echo "DEAD"
echo "=== providers.json identity ==="
python3 -c "
import json
p=json.load(open('/home/app.e0031982/.cline/data/settings/providers.json'))
s=p['providers']['openai-compatible']['settings']
print('model=',s.get('model'))
print('baseUrl=',s.get('baseUrl'))
k=s.get('apiKey','')
print('key8=',k[-8:] if len(k)>=8 else k)
print('maxTokens=',s.get('maxTokens'))
r=s.get('reasoning')
print('reasoning=',r if not isinstance(r,dict) else r.get('enabled'))
"
KEY=$(python3 -c "import json;print(json.load(open('/home/app.e0031982/.cline/data/settings/providers.json'))['providers']['openai-compatible']['settings']['apiKey'])")
echo "=== curl /cloud/v1/models ==="
curl -s --max-time 10 -o /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/.thermo_models.json -w "http=%{http_code}\n" http://agi-gateway.cxmt.com/cloud/v1/models -H "Authorization: Bearer $KEY"
python3 -c "import json;d=json.load(open('/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/.thermo_models.json'));ms=[m.get('id') for m in d.get('data',[])];print('doubao-pro in models:', 'doubao-seed-2.0-pro-cloud' in ms)" 2>/dev/null
echo "=== repo_commit for r2 ==="; git rev-parse HEAD
echo "=== live_eval_changes lines ==="; wc -l < /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/live_eval_changes.tsv
echo "=== /home disk ==="; df -h /home | tail -1
echo "=== /nasdata disk ==="; df -h /nasdata | tail -1
echo "=== concurrent batch ==="; pgrep -fa run_batch.sh || echo "none"
} > /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/.thermo_preflight.out 2>&1
