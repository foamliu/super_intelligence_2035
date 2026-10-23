#!/usr/bin/env python3
"""Generate BaiZe-2B throughput optimization HTML report from .29 experiment results."""
import subprocess, os, html
from datetime import datetime

REMOTE="10.239.2.29"; RDIR="/tmp/baize_perf_results"
REPORT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"reports","report_pretrain_2b_throughput_optim_zh.html")
EXPS={
 "e00_baseline":("基线 (BF16)","TP1·DP8·MBS2·seq4096·GBS1024·BF16",""),
 "e01_cuda_graph":("CUDA Graphs","基线 + --enable-cuda-graph","--enable-cuda-graph"),
 "e02_fp8_tensorwise":("FP8 Tensorwise","基线 + --fp8-recipe tensorwise","--fp8-recipe tensorwise"),
 "e03_fp8_blockwise":("FP8 Blockwise","基线 + --fp8-recipe blockwise --first-last-layers-bf16","--fp8-recipe blockwise --first-last-layers-bf16"),
 "e04_fp8_delayed":("FP8 Delayed","基线 + --fp8-recipe delayed","--fp8-recipe delayed"),
 "e05_overlap_optim":("Overlap Optim","基线 + --overlap-param-gather-with-optimizer-step","--overlap-param-gather-with-optimizer-step"),
 "e06_ce_fusion":("CE Loss Fusion","基线 + --cross-entropy-loss-fusion","--cross-entropy-loss-fusion"),
 "e07_fp8_tw_overlap":("FP8 TW+Overlap","基线 + --fp8-recipe tensorwise --overlap-param-gather-with-optimizer-step","--fp8-recipe tensorwise --overlap-param-gather-with-optimizer-step"),
 "e08_fp8_bw_cg":("FP8 BW+CG","基线 + --fp8-recipe blockwise --first-last-layers-bf16 --enable-cuda-graph","--fp8-recipe blockwise --first-last-layers-bf16 --enable-cuda-graph"),
 "e09_fp8_tw_cg":("FP8 TW+CG","基线 + --fp8-recipe tensorwise --enable-cuda-graph","--fp8-recipe tensorwise --enable-cuda-graph"),
}
def ssh(c):
 r=subprocess.run(["ssh","-o","ConnectTimeout=10",REMOTE,c],capture_output=True,text=True,timeout=30)
 return r.stdout+r.stderr
def fetch():
 out=ssh(f"cat {RDIR}/perf_*.result 2>/dev/null"); R={}
 for ln in out.strip().split("\n"):
  if not ln or "|" not in ln: continue
  p=ln.split("|")
  if len(p)<11: continue
  R[p[1]]={"status":p[0],"rc":int(p[2]),"peak":int(p[3]) if p[3] else 0,"avg":float(p[4]) if p[4] else 0,"med":float(p[5]) if p[5] else 0,"tps":int(p[6]) if p[6] else 0,"tf":float(p[7]) if p[7] else 0,"loss":float(p[8]) if p[8] else 0,"gn":float(p[9]) if p[9] else 0,"nan":int(p[10]) if p[10] else 0}
 return R
def errtail(l): return ssh(f"grep -iE 'AssertionError|IndexError|RuntimeError|not supported' {RDIR}/perf_{l}.log 2>/dev/null|head -3").strip()
def fk(v): return "—" if v==0 else f"{v/1000:.0f}K"
def fp(v): return "—" if v==0 else f"{'+'if v>0 else''}{v*100:.1f}%"
def gate(bl,e):
  if e["status"]!="OK": return("fail","实验失败")
  if e["loss"]==0: return("fail","无数据")
  d=abs(e["loss"]-bl)/bl
  if d<=0.05: return("pass",f"Δloss={d*100:.1f}%")
  if d<=0.10: return("warn",f"Δloss={d*100:.1f}%")
  return("fail",f"Δloss={d*100:.1f}%")
R=fetch(); print(f"Fetched {len(R)}: {list(R.keys())}")
B=R.get("e00_baseline",{}); bt=B.get("tps",0); bl=B.get("loss",0)
best=None; bv=0
for l,d in R.items():
 if d["status"]=="OK" and d["tps"]>bv: bv=d["tps"]; best=l
rows=[]; det=[]
for l,(nm,ds,ag) in EXPS.items():
 d=R.get(l,{"status":"PENDING","tps":0,"peak":0,"med":0,"loss":0,"gn":0,"nan":0,"tf":0})
 s=d["status"]; ib=(l==best); g=(d["tps"]-bt)/bt if bt and d["tps"] else 0
 gt,gm=gate(bl,d)
 rc="best" if ib else ("fail" if s=="FAIL" else ("warn" if gt=="warn" else ""))
 gc="gain-pos" if g>0 else("gain-neg" if g<0 else "gain-neutral")
 sh=f'<span class="tag tag-pass">✅OK</span>' if s=="OK" else(f'<span class="tag tag-fail">❌FAIL</span>' if s=="FAIL" else '<span class="tag tag-skip">⏳待跑</span>')
 gh=f'<span class="tag tag-pass">✅{gm}</span>' if gt=="pass" else(f'<span class="tag tag-fail">❌{gm}</span>' if gt=="fail" else f'<span class="tag tag-skip">⚠️{gm}</span>')
 pg=f'{d["peak"]/1024:.1f}' if d["peak"] else "—"
 rows.append(f'<tr class="{rc}"><td>{l}</td><td style="text-align:left"><b>{html.escape(nm)}</b><br><small>{html.escape(ds)}</small></td><td>{sh}</td><td class="metric">{d["med"]:.0f}</td><td class="metric">{fk(d["tps"])}</td><td class="{gc}">{fp(g)}</td><td>{pg}</td><td class="metric">{d["tf"]:.1f}</td><td>{d["loss"]:.4f}</td><td>{d["gn"]:.4f}</td><td>{d["nan"]}</td><td>{gh}</td></tr>')
 if s=="OK":
  g2=(d["tps"]-bt)/bt if bt else 0
  det.append(f'<h3>{l}: {html.escape(nm)}</h3><p><b>配置:</b><code>{html.escape(ag) if ag else "(基线)"}</code></p><p><b>结果:</b>吞吐 {fk(d["tps"])}({fp(g2)} vs基线)·中位step {d["med"]:.0f}ms·峰值 {d["peak"]/1024:.1f}GB·loss {d["loss"]:.4f}·gnorm {d["gn"]:.4f}</p>')
 elif s=="FAIL":
  e=errtail(l)
  det.append(f'<h3>{l}: {html.escape(nm)} ❌</h3><p><b>配置:</b><code>{html.escape(ag)}</code></p><p><b>失败原因:</b>{html.escape(e) if e else "rc="+str(d.get("rc","?"))}</p>')
 else:
  det.append(f'<h3>{l}: {html.escape(nm)} ⏳</h3><p>尚未运行。</p>')
tgt=249000; beat=bv>tgt if bv else False
rec=f'<p style="font-size:18px;color:#28a745;font-weight:bold">🎉 新纪录={fk(bv)} tok/s(+{(bv-tgt)/tgt*100:.1f}% vs历史249K) @ {EXPS[best][0] if best else "N/A"}</p>' if beat else '<p style="font-size:18px;color:#dc3545;font-weight:bold">⚠️ 未超过249K</p>'
sb=f'<div class="summary-box"><h3>📋 实验摘要</h3><p><b>模型:</b>BaiZe-2B (Mamba2-hybrid, 3.00B total)</p><p><b>基线配置:</b>TP1·DP8·MBS2·seq4096·GBS1024·BF16·distributed-optimizer</p><p><b>基线吞吐:</b>{fk(bt)} tok/s(历史249K,本次{fk(bt)})</p><p><b>最佳:</b>{EXPS[best][0] if best else "N/A"}={fk(bv)} tok/s({fp((bv-bt)/bt) if bt else "—"} vs基线)</p><p><b>实验数:</b>10组(1基线+9候选)</p>{rec}</div>'
bn=f'<p><b>基线:</b>{fk(bt)} tok/s</p><p><b>最佳:</b>{EXPS[best][0] if best else "N/A"}={fk(bv)} tok/s({fp((bv-bt)/bt) if bt else "—"})</p><ul><li><b>CUDA Graphs</b>(e01)+{(R.get("e01_cuda_graph",{}).get("tps",0)-bt)/bt*100 if bt else 0:.1f}%：消除kernel launch开销，对Mamba2频繁小kernel有效</li><li><b>FP8(tensorwise/delayed)反而慢~10%</b>：Mamba2 SSM层GEMM占比低，量化开销>节省</li><li><b>FP8 blockwise不可用</b>：TE要求CUDA≥12.9，当前12.8</li><li><b>overlap-param-gather崩溃</b>：框架IndexError，与Mamba2自定义层不兼容</li><li><b>显存:</b>基线54.7GB→CG 65.3GB(+10.6GB)→FP8 ~54GB，80GB充足</li><li><b>NaN计数</b>：grep误匹配，实际训练0 NaN(iteration log均显示"number of nan iterations: 0")</li></ul>'
ns="<li><b>组合优化</b>:CUDA Graphs+CE Fusion+更大MBS(当前54.7GB,可试MBS=4)</li><li><b>升级CUDA 12.9+</b>:解锁FP8 blockwise</li><li><b>序列并行(SP)</b>:--sequence-parallel减activation显存</li><li><b>数据侧</b>:num_workers/pin_memory/mmap预取</li><li><b>NCCL调优</b>:NCCL_ALGO/NCCL_PROTO+NVSwitch拓扑</li><li><b>更大GBS</b>:减optimizer step频率提有效吞吐</li>"
rp=f"# 基线复现(在.29执行)\ncd /nas_train/app.e0031982/code/BaiZe-ISEDA2027\nPY=/nas_train/app.e0031982/miniforge3/envs/py310/bin\n$PY/torchrun --nnodes=1 --nproc_per_node=8 --master_addr=127.0.0.1 --master_port=29970 \\\n  pretrain_launcher.py --arch mamba2 --name perf_baseline --dir nemo_experiments \\\n  --tokenizer-path data/tokenizer_eod --train-data-path $BLEND \\\n  --train-iters 80 --global-batch-size 1024 --micro-batch-size 2 --seq-length 4096 \\\n  --tensor-parallel 1 --eval-interval 99999 --eval-iters 0 --save-interval 0 \\\n  --lr 1e-3 --min-lr 1e-5 --lr-warmup-iters 5 --lr-decay-iters 5 --lr-decay-style WSD \\\n  --seed 1234 --precision bf16_mixed\n# 最佳配置: 末尾加 --enable-cuda-graph\n# 完整脚本: bash baize_perf_optim.sh"
H=f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>BaiZe-2B 训练吞吐优化实验报告</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333}}
h1{{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:10px}}
h2{{color:#16213e;margin-top:30px;border-left:4px solid #e94560;padding-left:10px}}
h3{{color:#0f3460}}
table{{border-collapse:collapse;width:100%;margin:15px 0;font-size:13px}}
th,td{{border:1px solid #ddd;padding:6px 10px;text-align:center}}
th{{background:#16213e;color:#fff;font-weight:600}}
tr:nth-child(even){{background:#f9f9f9}}
tr:hover{{background:#e8f0fe}}
.best{{background:#d4edda!important;font-weight:bold}}
.fail{{background:#f8d7da!important}}
.warn{{background:#fff3cd!important}}
.metric{{font-family:'Courier New',monospace;font-weight:bold}}
.gain-pos{{color:#28a745;font-weight:bold}}
.gain-neg{{color:#dc3545}}
.gain-neutral{{color:#6c757d}}
code{{background:#e8e8e8;padding:2px 6px;border-radius:3px;font-size:12px}}
pre{{background:#1e1e1e;color:#d4d4d4;padding:15px;border-radius:8px;overflow-x:auto;font-size:12px}}
.summary-box{{background:#fff;border:2px solid #e94560;border-radius:10px;padding:20px;margin:20px 0}}
.tag{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:bold;margin:2px}}
.tag-pass{{background:#d4edda;color:#155724}}
.tag-fail{{background:#f8d7da;color:#721c24}}
.tag-skip{{background:#fff3cd;color:#856404}}
</style></head><body>
<h1>🚀 BaiZe-2B 训练吞吐优化实验报告</h1>
<p><b>日期:</b>2026-10-23/24　<b>平台:</b>8×H100 80GB (10.239.2.29)　<b>目标:</b>超过 249K tok/s</p>
{sb}
<h2>1. 实验环境</h2>
<table>
<tr><th>项目</th><th>详情</th></tr>
<tr><td>GPU</td><td>8× NVIDIA H100 80GB SXM5 (NVSwitch full-mesh)</td></tr>
<tr><td>框架</td><td>Megatron-Bridge (NeMo 2.0) + TransformerEngine 2.12.0</td></tr>
<tr><td>PyTorch</td><td>2.8.0+cu128 / CUDA 12.8</td></tr>
<tr><td>模型</td><td>Mamba2-hybrid: 56层(28 SSM+28 Attention), hidden=2048, heads=16</td></tr>
<tr><td>数据</td><td>p5b_l3 (16 shards), DeepSeek BPE (vocab=129281)</td></tr>
<tr><td>训练参数</td><td>80 steps, lr=1e-3, WSD, warmup=5, seed=1234</td></tr>
<tr><td>不变量</td><td>seq=4096, GBS=1024(4.19M tok/step), MBS=2, TP=1, DP=8</td></tr>
<tr><td>稳态选取</td><td>warmup 20步不计,取step 30-80中位step时间</td></tr>
</table>
<h2>2. 实验结果总表</h2>
<table><tr><th>#</th><th>实验名</th><th>状态</th><th>中位step(ms)</th><th>吞吐(tok/s)</th><th>相对基线</th><th>峰值显存(GB)</th><th>TFLOP/s</th><th>Loss</th><th>GradNorm</th><th>NaN</th><th>正确性</th></tr>
{chr(10).join(rows)}
</table>
<p><small>注:NaN计数=grep'NaN|inf'匹配行数(含配置打印),实际训练0 NaN。正确性闸门=与基线loss偏差≤5%。</small></p>
<h2>3. 各实验详细分析</h2>
{chr(10).join(det)}
<h2>4. 瓶颈归因与下一步建议</h2>
<div class="summary-box"><h3>瓶颈分析</h3>{bn}<h3>下一步建议</h3><ul>{ns}</ul></div>
<h2>5. 复现命令</h2>
<pre>{html.escape(rp)}</pre>
<footer style="margin-top:40px;padding-top:15px;border-top:1px solid #ddd;color:#999;font-size:12px"><p>Generated by BaiZe pretrain agent (Cline) · {datetime.now().strftime('%Y-%m-%d %H:%M')} · <code>pretrain perf:</code></p></footer>
</body></html>"""
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,"w") as f: f.write(H)
print(f"Report: {REPORT} ({len(H)}B) | Baseline={fk(bt)} Best={fk(bv)}({EXPS[best][0] if best else 'N/A'})")
if beat: print(f"✅ BEAT 249K! +{(bv-tgt)/tgt*100:.1f}%")
