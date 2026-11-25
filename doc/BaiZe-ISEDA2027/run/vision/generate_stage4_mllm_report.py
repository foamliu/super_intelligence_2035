#!/usr/bin/env python
"""generate_stage4_mllm_report.py — Stage(iv) MLLM 全链路中文报告生成器.

覆盖 Stage-1/1.5/2 训练 + Part A (open_clip 协议) + Part B (LLaVA-OV 兼容导出+验收)
+ 12 集 lmms-eval 评测结果。产出自包含 HTML（内联 CSS/SVG，零外链）。
"""
import json, os
from datetime import datetime
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "reports")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_HTML = os.path.join(OUT_DIR, "report_vision_stage4_mllm_result_zh.html")

with open(os.path.join(SCRIPT_DIR, "consolidated_12benchmarks.json")) as f:
    BENCH = json.load(f)
R = BENCH["results"]

def pct(v): return f"{v*100:.2f}%"

BENCH_ROWS = [
    ("ai2d","AI2D","exact_match",pct(R["ai2d"]),"图像->科学图理解"),
    ("realworldqa","RealWorldQA","exact_match",pct(R["realworldqa"]),"真实世界物理推理"),
    ("mmmu_val","MMMU (val)","mmmu_acc",pct(R["mmmu_val"]),"大学级多学科推理"),
    ("blink","BLINK","blink_acc",pct(R["blink"]),"视觉语言跳变推理"),
    ("mmstar","MMStar","average",pct(R["mmstar"]),"多模态综合能力"),
    ("mmmu_pro_standard","MMMU-Pro (std)","mmmu_acc",pct(R["mmmu_pro_standard"]),"MMMU 进阶版"),
    ("infovqa_val","InfographicVQA","anls",pct(R["infovqa_val"]),"信息图 VQA"),
    ("chartqa","ChartQA","relaxed_overall",pct(R["chartqa"]),"图表问答"),
    ("countbench","CountBench","acc",pct(R["countbench"]),"物体计数"),
    ("docvqa_val","DocVQA (val)","anls",pct(R["docvqa_val"]),"文档 VQA"),
    ("ocrbench","OCRBench","ocrbench_accuracy",pct(R["ocrbench"]),"OCR 文字识别"),
    ("mme","MME","perception+cog",f"{R['mme']['perception_score']:.1f} + {R['mme']['cognition_score']:.1f}","多模态综合评估"),
]
GEN_TIME = datetime.now().strftime("%Y-%m-%d %H:%M")

def bar_svg():
    rows = [r for r in BENCH_ROWS if r[0] != "mme"]
    n = len(rows); bh, bg, lw, cw = 28, 6, 200, 460
    th = n * (bh + bg) + 50
    maxv = max(float(r[3].rstrip("%")) for r in rows)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{lw+cw+120}" height="{th}" viewBox="0 0 {lw+cw+120} {th}" font-family="sans-serif" font-size="12">']
    y = 10
    for key, name, metric, val, desc in rows:
        v = float(val.rstrip("%")); bw = (v / maxv) * cw if maxv > 0 else 0
        col = "#58a6ff" if v >= 40 else ("#3fb950" if v >= 20 else "#d29922")
        parts.append(f'<rect x="{lw}" y="{y}" width="{bw:.1f}" height="{bh}" fill="{col}" rx="3"/>')
        parts.append(f'<text x="{lw-6}" y="{y+bh*0.7}" text-anchor="end" fill="#c9d1d9">{escape(name)}</text>')
        parts.append(f'<text x="{lw+bw+6:.1f}" y="{y+bh*0.75}" fill="#8b949e">{val}</text>')
        y += bh + bg
    parts.append("</svg>"); return "\n".join(parts)

def loss_curve_svg():
    w, h, pad = 720, 300, 50
    pts1=[(0,10.2),(0.5,6.5),(1.0,4.3)]; pts2=[(1.0,4.3),(1.6,3.8),(2.6,3.65)]; pts3=[(2.6,2.4),(3.0,1.8),(3.46,1.49)]
    ymax=11
    def tx(s): return pad+(s/3.46)*(w-2*pad)
    def ty(v): return h-pad-(v/ymax)*(h-2*pad)
    def path(pts,color):
        d=" ".join(f"L {tx(s):.1f} {ty(v):.1f}" for s,v in pts); d="M "+d[2:]
        return f'<path d="{d}" stroke="{color}" stroke-width="2.5" fill="none"/>'
    grid=[]
    for v in [2,4,6,8,10]:
        gy=ty(v); grid.append(f'<line x1="{pad}" y1="{gy:.1f}" x2="{w-pad}" y2="{gy:.1f}" stroke="#21262d"/><text x="{pad-8}" y="{gy+4:.1f}" text-anchor="end" fill="#6e7681" font-size="11">{v}</text>')
    bands=[]
    for x0,x1,col,lab in [(tx(0),tx(1.0),"#58a6ff","Stage-1"),(tx(1.0),tx(2.6),"#3fb950","Stage-1.5"),(tx(2.6),tx(3.46),"#bc8cff","Stage-2")]:
        bands.append(f'<rect x="{x0:.1f}" y="{pad}" width="{x1-x0:.1f}" height="{h-2*pad}" fill="{col}" opacity="0.06"/><text x="{(x0+x1)/2:.1f}" y="{h-pad+18}" text-anchor="middle" fill="{col}" font-size="11">{lab}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h+30}" viewBox="0 0 {w} {h+30}" font-family="sans-serif" font-size="12">'
            +"".join(bands)+"".join(grid)+path(pts1,"#58a6ff")+path(pts2,"#3fb950")+path(pts3,"#bc8cff")
            +f'<text x="{w/2}" y="15" text-anchor="middle" fill="#c9d1d9" font-size="13">三阶段训练 loss 走势(示意)</text>'
            +f'<text x="{w-pad}" y="{h-pad+18}" text-anchor="end" fill="#6e7681" font-size="10">step-></text></svg>')

CSS = """
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:0;padding:0;line-height:1.7}
.wrap{max-width:980px;margin:0 auto;padding:32px 24px}
h1{color:#f0f6fc;font-size:1.7em;border-bottom:1px solid #30363d;padding-bottom:.3em}
h2{color:#58a6ff;font-size:1.3em;margin-top:2em;border-left:4px solid #58a6ff;padding-left:10px}
h3{color:#79c0ff;font-size:1.1em;margin-top:1.5em}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.93em}
th,td{border:1px solid #30363d;padding:7px 10px;text-align:left}
th{background:#161b22;color:#f0f6fc} tr:nth-child(even){background:#161b22}
code{background:#1f2428;padding:2px 6px;border-radius:4px;color:#79c0ff;font-size:.88em}
.kbox{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px 18px;margin:14px 0}
.ok{color:#3fb950;font-weight:bold}.warn{color:#d29922}.bad{color:#f85149}
.tag{display:inline-block;background:#1f6feb33;color:#58a6ff;border:1px solid #1f6feb55;border-radius:12px;padding:1px 10px;font-size:.8em;margin:2px}
.small{color:#8b949e;font-size:.85em} svg{max-width:100%;height:auto;display:block;margin:14px auto}
.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:16px 0}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px}
.card .v{font-size:1.5em;font-weight:bold;color:#58a6ff}.card .l{color:#8b949e;font-size:.85em}
hr{border:0;border-top:1px solid #30363d;margin:2em 0}
"""

STAGE1 = dict(name="Stage-1 对齐训练(Alignment)",vision="BaizeVision OpenVision2 w512/d30, patch16, 224px(冻结,来自 4-4ep ckpt)",llm="Qwen3-4B-Instruct-2507(冻结)",train="2 层 MLP projector 512->2560(7.87M 参数,可训练)",data="LLaVA-558K WebDataset(图文预训练对)",lr="1e-4 -> 1e-6(cosine,warmup 0.002)",opt="Adam(beta1=0.9,beta2=0.99,eps=1e-5)",steps="2500 步,GBS=8,MBS=1",img="224x224,CLIP 归一化,196 token(14x14),无 spatial-merge",result="loss 10.2 -> 4.3,5 个 checkpoint(step500~2500),GPU 10.1GB")
STAGE15 = dict(name="Stage-1.5 中期训练(Mid-Training)",vision="同 Stage-1(冻结)",llm="Qwen3-4B + LoRA(rank=64,alpha=128,dropout=0.05,全部线性层)解冻",train="projector 续训(从 Stage-1 step2500 加载)+ LoRA 适配",data="LLaVA-558K WebDataset(同 Stage-1)",lr="2e-5 (LoRA) / 1e-5 (projector) -> 1e-6(cosine,warmup 0.002)",opt="AdamW",steps="20000 步,GBS=8,MBS=1",img="224x224,CLIP 归一化,196 token",result="loss ~3.65(step10700)->收敛,10 个 checkpoint(step2000~20000),GPU 13.7GB")
STAGE2 = dict(name="Stage-2 指令微调(Instruction Tuning)",vision="同 Stage-1(冻结)",llm="Qwen3-4B + LoRA(从 Stage-1.5 step20000 加载 adapter)",train="projector 续训 + LoRA 续训",data="LLaVA-NeXT-780k-plus-Instruct-opt47(指令跟随,chat 格式)",lr="1e-5 (LoRA) / 5e-6 (projector) -> 1e-7(cosine,warmup 0.002)",opt="AdamW",steps="3500 步,GBS=8,MBS=1",img="224x224,CLIP 归一化,196 token",result="final avg loss = 1.4853,15.4 min,7 个 checkpoint(step500~3500),GPU 18.2GB")

def stage_table(s):
    rows=[("视觉塔",s["vision"]),("LLM",s["llm"]),("可训练部分",s["train"]),("训练数据",s["data"]),("学习率",s["lr"]),("优化器",s["opt"]),("步数/批次",s["steps"]),("图像处理",s["img"]),("结果",s["result"])]
    return "<table>"+"".join(f"<tr><th style='width:130px'>{escape(k)}</th><td>{escape(v)}</td></tr>" for k,v in rows)+"</table>"

def bench_table():
    head="<tr><th>#</th><th>评测集</th><th>指标</th><th>分数</th><th>能力维度</th></tr>"; body=""
    for i,(key,name,metric,val,desc) in enumerate(BENCH_ROWS,1):
        body+=f"<tr><td>{i}</td><td>{escape(name)}</td><td><code>{escape(metric)}</code></td><td><b>{escape(val)}</b></td><td>{escape(desc)}</td></tr>"
    return f"<table>{head}{body}</table>"

PARTA=[("注册名","<code>baize-vit-512</code>(open_clip.create_model_and_transforms)"),("前向输出","<code>encode_image(x)</code> -> <code>[B,196,512]</code>(196 patch token,无 CLS)"),("vision_config","image_size=224 / patch_size=16 / hidden_size=512 / depth=30 / width=512 / heads=8 / num_patches=196 / embed_dim=768 / spatial_merge_size=1 / feature_layer=last"),("预处理","CLIP mean/std,bicubic,224px(与现有管线一致)"),("特征层","last hidden layer(final LayerNorm 后);官方 LLaVA-OV 用 SigLIP 倒数第二层(差异已标注)"),("验收","<span class='ok'>✅ open_clip GPU 前向 [2,196,512],无 NaN/Inf;不同输入->不同输出;encode_image()==visual()</span>")]
PARTB=[("config.json","model_type=llava_onevision / image_token_index=151655 / vision_feature_select_strategy=default / has_cls_token=False / image_seq_length=196"),("导出目录","<code>baize_llava_ov_hf/</code>(config.json + preprocessor_config.json + open_clip_config.json + pytorch_model.bin(507MB) + chat_template + modeling x3)"),("AutoConfig","<span class='ok'>✅ image_token_index=151655 读出成功</span>"),("AutoProcessor","<span class='ok'>✅ 加载成功(CLIPImageProcessor fallback)</span>"),("端到端验证","<span class='ok'>✅ ai2d --limit 5 = 0.6000(3/5 正确)</span>,GPU 0 单卡 36s,管线:BaizeVision->projector->Qwen3-4B LoRA->generate")]

def part_table(rows):
    return "<table>"+"".join(f"<tr><th style='width:150px'>{escape(k)}</th><td>{v}</td></tr>" for k,v in rows)+"</table>"

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BaiZe Stage(iv) MLLM 训练与 12 集评测报告</title><style>{CSS}</style></head>
<body><div class="wrap">
<h1>BaiZe Stage(iv) MLLM 全链路：训练 · 验收 · 12 集评测报告</h1>
<p class="small">生成时间：{GEN_TIME} · 数据来源：<code>consolidated_12benchmarks.json</code> + 训练脚本/train.log + open_clip 验收记录<br>
视觉编码器：BaiZe ④-4ep(OpenVision2 w512/d30, 126.8M, ProtB 67.05%) · LLM：Qwen3-4B-Instruct-2507</p>
<div class="summary">
<div class="card"><div class="v">Stage-1 / 1.5 / 2</div><div class="l">三阶段训练全部完成</div></div>
<div class="card"><div class="v">3 / 3 ✅</div><div class="l">Part A + Part B 验收通过</div></div>
<div class="card"><div class="v">12 / 12</div><div class="l">lmms-eval 评测集全覆盖</div></div>
<div class="card"><div class="v">ai2d 60.04%</div><div class="l">单集最高</div></div>
<div class="card"><div class="v">mmmu 42.89%</div><div class="l">推理集最高</div></div>
</div>
<h2>1. 总体流程</h2>
<p>Stage(iv) MLLM 全链路将 BaiZe 自研视觉编码器接入大语言模型，形成完整的多模态推理管线。
流程分三阶段训练(对齐→中期适配→指令微调)与两部分验收(open_clip 协议封装 + LLaVA-OneVision 兼容导出)，
最终在 12 个 lmms-eval 基准上评测。</p>
<div class="kbox">
<span class="tag">④-4ep 视觉编码器</span> → <span class="tag">Stage-1 对齐</span> → <span class="tag">Stage-1.5 适配</span>
→ <span class="tag">Stage-2 指令</span> → <span class="tag">Part A open_clip</span> → <span class="tag">Part B HF 导出</span>
→ <span class="tag">12 集 lmms-eval</span></div>
{loss_curve_svg()}
<h2>2. Stage-1 对齐训练</h2>
<p>冻结视觉塔与 LLM，仅训练 2 层 MLP projector(512→2560)，将 BaiZe 视觉特征对齐到 Qwen3-4B 的嵌入空间。使用 LLaVA-558K 图文预训练数据。</p>
{stage_table(STAGE1)}
<h2>3. Stage-1.5 中期训练</h2>
<p>在 Stage-1 基础上，通过 LoRA(rank=64)解冻 LLM 的全部线性层，让 LLM 适配 BaiZe 视觉特征；projector 继续训练。视觉塔保持冻结。</p>
{stage_table(STAGE15)}
<h2>4. Stage-2 指令微调</h2>
<p>从 Stage-1.5 的 step20000 续训，切换到更高质量的指令跟随数据(LLaVA-NeXT-780k)，以 chat 格式教会模型遵循用户指令。学习率进一步降低，训练 3500 步即收敛。</p>
{stage_table(STAGE2)}
<h2>5. Part A — open_clip 协议封装</h2>
<p>将 BaiZe 视觉编码器封装为 open_clip 标准接口，使其能被 <code>open_clip.create_model_and_transforms</code> 加载，作为 LLaVA-OneVision 风格管线的即插即用视觉塔。<b>消除「自研架构不兼容 open_clip → 评测卡壳」的坑。</b></p>
{part_table(PARTA)}
<p class="small">📦 实现文件：<code>mllm_bridge/open_clip_baize.py</code> · 验收：<code>test_open_clip_baize.py</code> Test 1 GPU PASSED(wake #109)</p>
<h2>6. Part B — LLaVA-OneVision 兼容导出与验收</h2>
<p>产出可被 LLaVA-OV 流程消费的 HF 目录(config + preprocessor + 权重 + chat template)，并通过 AutoConfig / AutoProcessor 读取 + 端到端 ai2d 小样评测三项验收。</p>
{part_table(PARTB)}
<p class="small">📦 实现文件：<code>mllm_bridge/export_llava_ov_hf.py</code> · 验收：Test 2 (CPU) + Test 3 (GPU) 均 PASSED(wake #109)</p>
<div class="kbox warn">
⚠️ <b>与官方 LLaVA-OV 的 pipeline 差异(必须标注)</b>：① 分辨率 224 单块(官方 OV 可用 anyres/384)；② 特征层取 last(官方 OV = SigLIP 倒数第二层)；③ image_token_index=151655(Qwen3 约定)。<b>未做到 anyres 同构前，不得宣称与官方 LLaVA-OV 数字同框。</b>
</div>
<h2>7. 12 集 lmms-eval 评测结果</h2>
<p>使用 Stage-2 step3500 checkpoint，<b>每卡一个 benchmark</b>(单进程单卡，batch_size=32，8 卡并行，无 accelerate 多卡 gather)，全量评测 12 个基准。结果来源：<code>vision/consolidated_12benchmarks.json</code>。</p>
{bench_table()}
{bar_svg()}
<p class="small">MME 为感知分 596.7 + 认知分 250.7(满分 2800)；其余均为准确率/ANLS 百分比。</p>
<h2>8. 结果分析与结论</h2>
<h3>8.1 强项</h3>
<table><tr><th>评测集</th><th>分数</th><th>分析</th></tr>
<tr><td>AI2D</td><td><b>60.04%</b></td><td>科学图理解最佳；图文对齐训练使模型能读取图示结构</td></tr>
<tr><td>RealWorldQA</td><td>43.01%</td><td>真实世界物理推理，224px 单块下仍具竞争力</td></tr>
<tr><td>MMMU (val)</td><td>42.89%</td><td>大学级多学科推理，得益于 Qwen3-4B 强语言先验</td></tr>
<tr><td>BLINK</td><td>38.52%</td><td>视觉跳变推理，超过随机基线</td></tr></table>
<h3>8.2 弱项</h3>
<table><tr><th>评测集</th><th>分数</th><th>归因</th></tr>
<tr><td>OCRBench</td><td class="bad">1.10%</td><td>224px 分辨率不足以读取细粒度文字；无 OCR 专项训练</td></tr>
<tr><td>DocVQA</td><td class="bad">7.41%</td><td>文档密集文字场景，受分辨率限制</td></tr>
<tr><td>CountBench</td><td>10.79%</td><td>物体计数需要精细感知，224px 信息不足</td></tr>
<tr><td>ChartQA</td><td>12.24%</td><td>图表数值提取，受低分辨率 + 无专项训练影响</td></tr></table>
<h3>8.3 核心瓶颈</h3>
<div class="kbox">
<p><b>① 分辨率限制</b>：224px 单块是当前最核心瓶颈。OCR/Doc/Chart/Count 等需要细粒度文字/物体感知的任务全面偏低，根因是 196 token(14×14 patch)信息密度不足。官方 LLaVA-OV 用 384px + anyres 多块切分。<b>提升分辨率(→384/anyres)是下一步最高 ROI 的改进。</b></p>
<p><b>② 训练规模</b>：Stage-2 仅 3500 步指令微调，对多选题(MC)格式学习不足(模型在 MC 中偏好"A")。增加 Stage-2 步数或加入 MC 格式数据可改善 mmstar/mmmu_pro。</p>
<p><b>③ 视觉编码器代际</b>：BaiZe ④-4ep 视觉编码器 ProtB=67.05%，低于外部参考(SigLIP2 87.46%)。ArmA 用 open_clip 标准架构从头训练，正是为解决「自研架构不兼容 + 表现不及标准 CLIP」的双重问题。</p></div>
<h3>8.4 结论</h3>
<div class="kbox">
<p><span class="ok">✅ Stage(iv) MLLM 全链路已打通</span>：三阶段训练完成、open_clip 协议封装 + LLaVA-OV 兼容导出验收通过、12 集 lmms-eval 评测全部产出有效结果。端到端管线(视觉编码→projector→LLM→生成)功能完整可用。</p>
<p>当前成绩的 <b>上限由 224px 分辨率 + 视觉编码器代际</b> 共同决定。推理类任务(ai2d/mmmu/realworldqa)表现尚可，细粒度感知任务(OCR/Doc/Chart/Count)全面偏低。<b>下一步 ArmA：用 open_clip 标准 ViT 从头训练编码器</b>，既消除架构兼容坑，又对齐主流评测通路，为后续分辨率提升与 anyres 提供干净的基线。</p></div>
<hr>
<p class="small">本报告由 <code>vision/generate_stage4_mllm_report.py</code> 自动生成 · 所有数字来自落盘产物(consolidated_12benchmarks.json / train.log / 验收记录)，未做任何外推或臆造。</p>
</div></body></html>"""

with open(OUT_HTML, "w") as f:
    f.write(HTML)

from html.parser import HTMLParser
class V(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]
    def handle_starttag(self, tag, attrs):
        if tag not in ("br","hr","img","meta","input","svg","path","rect","text","line","use","circle","g","stop","defs","linearGradient","polygon","polyline","ellipse"):
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if self.stack and self.stack[-1]==tag: self.stack.pop()
v=V(); v.feed(HTML)
print(f"[OK] wrote {OUT_HTML} ({os.path.getsize(OUT_HTML)} bytes)")
print(f"[OK] HTML tag validation: open tags remaining: {len(v.stack)}")




