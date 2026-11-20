#!/usr/bin/env python3
"""Temp script to write report_vision_paper_edit_zh.html (wake#439)."""
import os
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', 'report_vision_paper_edit_zh.html')
CSS = """body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:960px;margin:1.5em auto;padding:0 1em;color:#222;background:#fafafa;line-height:1.7}
h1{color:#1a3a5a;border-bottom:3px solid #1a3a5a;padding-bottom:.3em}
h2{color:#1a3a5a;border-bottom:1px solid #ccc;padding-bottom:.2em;margin-top:2em}
h3{color:#2a5a7a;margin-top:1.5em}h4{color:#555;margin-top:1em}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:0.9em}
th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;vertical-align:top}
th{background:#e8eef5;font-weight:bold}tr:nth-child(even){background:#f5f5f5}
code{background:#eef;padding:1px 4px;border-radius:3px;font-size:0.9em}
.before{background:#fde;border-left:4px solid #c33;padding:8px 12px;margin:0.5em 0}
.after{background:#dfd;border-left:4px solid #3a3;padding:8px 12px;margin:0.5em 0}
.kbox{background:#eef5ff;border-left:4px solid #36c;padding:8px 12px;margin:0.5em 0}
.rbox{background:#fee;border-left:4px solid #c33;padding:8px 12px;margin:0.5em 0}
.gbox{background:#efe;border-left:4px solid #3a3;padding:8px 12px;margin:0.5em 0}
.tok{background:#3a3;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.terr{background:#c33;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.tp0{background:#c00;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.tp1{background:#e80;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.ev{background:#f9f9f9;border:1px solid #ddd;padding:6px 12px;margin:0.5em 0;font-size:0.9em}
.ev li{margin:2px 0}
.summary-box{background:#1a3a5a;color:#fff;padding:12px 18px;border-radius:6px;margin:1em 0}
.summary-box b{color:#ffd}
hr{border:none;border-top:1px solid #ccc;margin:2em 0}
.footer{text-align:center;color:#888;font-size:0.85em;margin-top:2em;padding-top:1em;border-top:1px solid #ccc}"""


P = []
P.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">')
P.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
P.append('<title>BaiZe 论文第 6 章视觉编码器改稿报告</title><style>' + CSS + '</style></head><body>')
P.append('<h1>BaiZe 论文第 6 章「视觉编码器」改稿报告</h1>')
P.append('<p><b>日期</b>：2026-10-31（wake#439）　<b>执行者</b>：vision 线　<b>运维令</b>：2026-10-31 11:2x</p>')
P.append('<div class="summary-box"><b>改稿结果</b>：6_vision_encoder.tex 18行 → pdflatex×3+bibtex → <b>6页</b>，<b>ERR=0/UNDEF=0/Warning=0/Overfull=0</b>。本轮删除四臂消融句（AIMv2消融=中间过程），页数7→6。数字全溯源。</div>')
P.append('<h2 id="s1">§1 改稿概览</h2>')
P.append('<table><tr><th>#</th><th>位置</th><th>类型</th><th>一句话</th></tr>')
P.append('<tr><td>1</td><td>L7架构</td><td>P0改写</td><td>width-1024→width-512（126.8M=w512）</td></tr>')
P.append('<tr><td>2</td><td>原L11四臂消融</td><td><b>删除</b></td><td>属AIMv2消融中间过程，运维令要求不进正文</td></tr>')
P.append('<tr><td>3</td><td>L13结果</td><td>P1扩写</td><td>标注数据差异（18.5M vs 58.8M含GPIC）</td></tr>')
P.append('<tr><td>4</td><td>L15 +12.4pp</td><td>不改</td><td>已属实</td></tr>')
P.append('<tr><td>5</td><td>L17 224/16</td><td>不改</td><td>已属实</td></tr></table>')
P.append('<p><b>篇幅</b>：18行，6页。wake#437版（含四臂消融）7页→wake#439删除后6页。</p>')
P.append('<h2 id="s2">§2 逐段改前→改后+事实依据</h2>')
P.append('<h3>2.1 引言句—不改</h3><div class="gbox"><p>✅属实</p></div>')
P.append('<h3>2.2 Selected encoder（L7-8）P0</h3>')
P.append('<div class="before"><p><code>width-1024...126.8M(505.2M at full width)</code></p></div>')
P.append('<div class="after"><p><code>width-512/depth-30(126.8M parameters)</code></p></div>')
P.append('<div class="rbox"><p>❌改前：w1024=505.2M≠126.8M。w512=126.78M。实验全用w512。</p></div>')
P.append('<ul class="ev"><li>EXPERIMENTS_VISION.md L51:选w512(126.8M)</li><li>r10_scaling2d.py L23:512:126_779_392</li><li>L26:1024:505_217_024</li></ul>')
P.append('<h3>2.3 目标函数（L9-10）—不改</h3><div class="gbox"><p>✅ InfoNCE+1.0×patch-MSE,mask0.6 (L129)</p></div>')
P.append('<h3>2.4 四臂消融（原L11-12）—<span class="tp0">删除</span></h3>')
P.append('<div class="before"><p><code>A four-arm ablation(15.4M pairs)...neither term alone suffices(6.1% and 6.2%)...+6.0pp...+12.4pp at 55.3M</code></p></div>')
P.append('<div class="after"><p><b>整句删除</b>。运维令：中间过程不进正文，AIMv2消融=四臂消融。</p></div>')
P.append('<p>删除理由：①AIMv2消融属中间过程 ②「neither alone suffices」偏强 ③7→6页 ④+12.4pp仍保留在L15</p>')
P.append('<table><tr><th>臂</th><th>lp@15.36M</th><th>翻盘?</th></tr>')
P.append('<tr><td>①InfoNCE</td><td>6.08%</td><td>—</td></tr>')
P.append('<tr><td>④CoCa</td><td>0.47%</td><td>❌坍缩</td></tr>')
P.append('<tr><td>⑥-B patch-only</td><td>6.23%</td><td>❌</td></tr>')
P.append('<tr><td><b>⑥-A combined</b></td><td><b>12.08%</b></td><td>✅</td></tr></table>')
P.append('<ul class="ev"><li>ROUND11.md L1130-1137,L1355</li></ul>')
P.append('<h3>2.5 Final result（L13-14）P1</h3>')
P.append('<div class="before"><p>...19.76%...20.27% at 176M...</p></div>')
P.append('<div class="after"><p>...19.76%(CC12M+Amshaker,18.5M unique)...20.27% on 58.8M-pair(adding GPIC)...</p></div>')
P.append('<p>19.76%@55.3M=R11-G(18.5M×3ep). 20.27%@176M=R12(58.8M×3ep). 数据不同须标注。</p>')
P.append('<ul class="ev"><li>ROUND11.md L877,L1322,L1543,L1557</li></ul>')
P.append('<h3>2.6 +12.4pp（L15-16）—不改</h3><div class="gbox"><p>✅19.76−7.40=+12.36≈+12.4pp</p></div>')
P.append('<h3>2.7 224/16（L17-18）—不改</h3><div class="gbox"><p>✅196 token</p></div>')

# Section 3-5
P.append('<h2 id="s3">§3 事实核对清单</h2>')
P.append('<table><tr><th>数字</th><th>改后</th><th>来源</th><th>状态</th></tr>')
for r in [('width','512','L51/L129','P0已修'),('params','126.8M','r10 L23(126,779,392)','✅'),('18.5M pairs','有','L51;ROUND11 L1284','✅'),('InfoNCE+patch-MSE','有','L129','✅'),('1:1 weight','有','BP-2','✅'),('0.6 mask','有','BP-2;L147','✅'),('四臂6.1%/6.2%','删除','ROUND11 L1355','运维令删'),('+6.0pp@15.4M','删除','ROUND11 L1355','运维令删'),('+12.4pp@55.3M','有','ROUND11 L887(19.76-7.40)','✅'),('11.50%@5.1M','有','ROUND11 L877','✅'),('19.76%@55.3M','有','ROUND11 L877/L1322','✅'),('20.27%@176M','有','ROUND11 L1322/L1489(终点)','✅'),('20.27vs20.32','终点','20.32=峰值step340k,20.27=终点step344k','✅正确'),('58.8M corpus','有','ROUND11 L1268/L1557','✅'),('196 token','有','224/16=14^2','✅'),('depth-30','有','L475(w512/d30)','✅'),('bidirectional','有','BP-1','✅')]:
    P.append(f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>')
P.append('</table>')

P.append('<h2 id="s4">§4 编译验证</h2>')
P.append('<table><tr><th>项</th><th>结果</th></tr>')
P.append('<tr><td>流程</td><td>pdflatex→bibtex→pdflatex→pdflatex</td></tr>')
P.append('<tr><td>页数</td><td><b>6页</b></td></tr>')
P.append('<tr><td>ERR</td><td><b>0</b></td></tr>')
P.append('<tr><td>UNDEF</td><td><b>0</b></td></tr>')
P.append('<tr><td>Warning</td><td><b>0</b></td></tr>')
P.append('<tr><td>Overfull</td><td><b>0</b></td></tr>')
P.append('<tr><td>main.pdf</td><td>🚫不commit</td></tr>')
P.append('<tr><td>BOM</td><td>✅UTF-8 BOM</td></tr></table>')
P.append('<div class="kbox"><p>页数变化：wake#437版(含四臂消融)7页→wake#439删除后6页。</p></div>')

P.append('<h2 id="s5">§5 已删中间过程清单(13项)</h2>')
P.append('<table><tr><th>#</th><th>中间过程</th><th>来源</th><th>出现?</th></tr>')
dels = [('六架构对比','§S3 L344'),('SSM崩塌','§S3'),('AR范式探索','BP-1'),('AR+InfoNCE hybrid','BP-1'),('Muon消融','旧§VI-D'),('ProtB-epoch缩放','L1088'),('四臂消融(本轮删)','ROUND11 L1130'),('SigLIP/LocalLoss','BP-1;L85-86'),('CoCa坍缩','BP-1;L87'),('文本塔LoRA','BP-1;L88'),('mask-ratio消融','L147'),('weight-ratio消融','L180'),('width缩塔先导','L51')]
for i,d in enumerate(dels,1):
    P.append(f'<tr><td>{i}</td><td>{d[0]}</td><td>{d[1]}</td><td><span class="terr">❌未出现</span></td></tr>')
P.append('</table>')

P.append('<h2 id="s6">§6 中文注释同步</h2>')
P.append('<table><tr><th>行</th><th>改动</th><th>同步?</th></tr>')
P.append('<tr><td>L7-8</td><td>width-512</td><td>✅</td></tr>')
P.append('<tr><td>原L11-12</td><td>四臂消融句+注释删除</td><td>✅</td></tr>')
P.append('<tr><td>L13-14</td><td>数据标注</td><td>✅</td></tr></table>')

P.append('<h2 id="s7">§7 自检清单</h2>')
P.append('<table><tr><th>#</th><th>检查项</th><th>结果</th></tr>')
for i,c in enumerate([('width-1024→512(P0)','✅'),('四臂消融删除','✅'),('20.27%标注数据差异','✅'),('+12.4pp属实','✅'),('20.27vs20.32用终点','✅'),('数字全溯源','✅'),('无估算冒充','✅'),('中文注释同步','✅'),('全文≤6页','✅6页'),('ERR=0/UNDEF=0','✅'),('Warning=0/Overfull=0','✅'),('第6章≤1.5页','✅~0.35页'),('不commit main.pdf','✅'),('不动abstract/intro/pretrain','✅'),('中间过程13项未出现','✅'),('git pull --rebase','✅'),('BOM保持','✅')],1):
    P.append(f'<tr><td>{i}</td><td>{c[0]}</td><td>{c[1]}</td></tr>')
P.append('</table>')
P.append('<hr><div class="footer"><p>BaiZe vision线 · 2026-10-31 · wake#439</p></div>')
P.append('</body></html>')

html = '\n'.join(P)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
size = os.path.getsize(OUT)
print(f'OUT={OUT}')
print(f'SIZE={size} bytes')
for tag in ['html','head','body','table','div','ul','li']:
    o = html.count(f'<{tag}'); c = html.count(f'</{tag}>')
    print(f'TAG<{tag}>: {"OK" if o==c else f"MISMATCH({o}/{c})"}')
print(f'SCRIPT={html.count("<script")}')
print(f'EXT_LINKS={html.count("http://")+html.count("https://")}')
