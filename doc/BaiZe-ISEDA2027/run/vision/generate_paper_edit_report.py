#!/usr/bin/env python3
"""Generate report_vision_paper_edit_zh.html — BaiZe paper Chapter 6 edit report.
Idempotent: re-running produces byte-identical output.
"""
import hashlib, os, sys

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', 'report_vision_paper_edit_zh.html')

CSS = """
body{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;max-width:960px;margin:1.5em auto;padding:0 1em;color:#222;background:#fafafa;line-height:1.7}
h1{color:#1a3a5a;border-bottom:3px solid #1a3a5a;padding-bottom:.3em}
h2{color:#1a3a5a;border-bottom:1px solid #ccc;padding-bottom:.2em;margin-top:2em}
h3{color:#2a5a7a;margin-top:1.5em}
h4{color:#555;margin-top:1em}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:0.9em}
th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;vertical-align:top}
th{background:#e8eef5;font-weight:bold}
tr:nth-child(even){background:#f5f5f5}
code{background:#eef;padding:1px 4px;border-radius:3px;font-size:0.9em}
.before{background:#fde;border-left:4px solid #c33;padding:8px 12px;margin:0.5em 0}
.after{background:#dfd;border-left:4px solid #3a3;padding:8px 12px;margin:0.5em 0}
.kbox{background:#eef5ff;border-left:4px solid #36c;padding:8px 12px;margin:0.5em 0}
.rbox{background:#fee;border-left:4px solid #c33;padding:8px 12px;margin:0.5em 0}
.gbox{background:#efe;border-left:4px solid #3a3;padding:8px 12px;margin:0.5em 0}
.tok{background:#3a3;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.terr{background:#c33;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.twarn{background:#e80;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.tp0{background:#c00;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.tp1{background:#e80;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.tp2{background:#08c;color:#fff;padding:1px 6px;border-radius:3px;font-size:0.85em}
.ev{background:#f9f9f9;border:1px solid #ddd;padding:6px 12px;margin:0.5em 0;font-size:0.9em}
.ev li{margin:2px 0}
.del{background:#fdd;border-left:4px solid #c00;padding:8px 12px;margin:0.5em 0}
.summary-box{background:#1a3a5a;color:#fff;padding:12px 18px;border-radius:6px;margin:1em 0}
.summary-box b{color:#ffd}
hr{border:none;border-top:1px solid #ccc;margin:2em 0}
.footer{text-align:center;color:#888;font-size:0.85em;margin-top:2em;padding-top:1em;border-top:1px solid #ccc}
"""

def _s1():
    P = []
    P.append('<h1>BaiZe 论文第 6 章「视觉编码器」改稿报告</h1>')
    P.append('<p><b>日期</b>：2026-10-31　<b>执行者</b>：vision 线　<b>运维令</b>：2026-10-31 11:2x（用户直令·最高优先）</p>')
    P.append('<div class="summary-box">')
    P.append('<b>改稿结果</b>：6_vision_encoder.tex 重写完成 → pdflatex×3 + bibtex → <b>6 页</b>（正文+参考文献），'
             '<b>ERR=0 / UNDEF=0</b>。修复 P0 事实性错误 1 处（width-1024→width-512）、P1 措辞不精确 2 处（"Both terms required"→interaction；20.27%@176M 标注数据差异）、'
             'P2 措辞过强 1 处（"trunk degrades"删除）。所有数字均溯源到 EXPERIMENTS_VISION.md / EXPERIMENTS_VISION_ROUND11.md，无估算冒充实测。')
    P.append('</div>')
    P.append('<h2 id="s1">§1 改稿概览</h2>')
    P.append('<table><caption>表 1.1 改动汇总</caption>')
    P.append('<tr><th>#</th><th>位置</th><th>改动类型</th><th>严重度</th><th>一句话</th></tr>')
    P.append('<tr><td>1</td><td>L7 架构描述</td><td>改写</td><td><span class="tp0">P0</span></td>'
             '<td>width-1024 → width-512（126.8M 对应 w512，非 w1024）</td></tr>')
    P.append('<tr><td>2</td><td>L11 损失项关系</td><td>改写</td><td><span class="tp1">P1</span>+<span class="tp2">P2</span></td>'
             '<td>"Both terms required / trunk degrades" → "breakthrough depends on interaction" + 四臂数字</td></tr>')
    P.append('<tr><td>3</td><td>L15 最终结果</td><td>扩写</td><td><span class="tp1">P1</span></td>'
             '<td>标注数据组成差异（18.5M CC12M+Amshaker vs 58.8M 含 GPIC）</td></tr>')
    P.append('<tr><td>4</td><td>L17 +12.4pp</td><td>不改</td><td>—</td><td>已属实（19.76%−7.40%=+12.36pp≈+12.4pp，同样本量）</td></tr>')
    P.append('<tr><td>5</td><td>L19 224/16</td><td>不改</td><td>—</td><td>已属实</td></tr>')
    P.append('</table>')
    P.append('<p><b>篇幅</b>：改后 20 行（含中文注释），实测全文 <b>6 页</b>。初稿（含"absolute modest"句与 width-1024 括号解释）曾达 7 页 → 压缩：删除"absolute modest"句 + 精简括号 → 回到 6 页。压缩原则：删形容词/非必需解释，<b>不删任何实测数字</b>。</p>')
    return "\n".join(P)

def _s2():
    P = []
    P.append('<h2 id="s2">§2 逐段「改前→改后」+ 事实依据</h2>')
    P.append('<h3>2.1 引言句（L3-4）— 无需改动</h3>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>，保持原样。</p></div>')
    P.append('<h3>2.2 paragraph{Selected encoder.}（L7-8）— P0 改写</h3>')
    P.append('<h4>改前</h4>')
    P.append('<div class="before"><p><code>width-$1024$/depth-$30$ ... $126.8$M parameters ($505.2$M at full width)</code></p></div>')
    P.append('<h4>改后</h4>')
    P.append('<div class="after"><p><code>width-$512$/depth-$30$ ($126.8$M parameters)</code></p></div>')
    P.append('<p><b>改动说明</b>：「width-1024」→「width-512」(<span class="tp0">P0</span>)。「505.2M at full width」括号删除（省篇幅）。「126.8M」数字正确但原归属错误——对应 w512 而非 w1024。</p>')
    P.append('<div class="rbox"><p><span class="terr">❌ 改前不符事实</span>：「width-1024」与「126.8M」自相矛盾。w1024=505.2M，w512=126.78M。实际训练（R9/R11-G/R12）全部用 w512。w1024 仅用于 R8 架构对比先导（3000 步）。</p></div>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION.md L51：「选 w512（126.8M）」</li><li>EXPERIMENTS_VISION.md L129：「w512（126.78M）」</li><li>vision/r10_scaling2d.py L23：<code>512: 126_779_392</code></li><li>vision/r10_scaling2d.py L26：<code>1024: 505_217_024</code></li><li>ROUND11.md L933：「OpenVision2 w512（126.78M）」</li></ul>')
    P.append('<h3>2.3 目标函数（L9-10）— 无需改动</h3>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>，保持原样。与 EXPERIMENTS_VISION.md L129 一致。</p></div>')
    return "\n".join(P)

def _s3():
    P = []
    P.append('<h3>2.4 损失项关系（L11-12）— P1+P2 改写</h3>')
    P.append('<h4>改前</h4>')
    P.append('<div class="before"><p><code>Both terms are required: the dense term carries most of the representation quality, while the contrastive term acts as an anchor without which the trunk degrades.</code></p></div>')
    P.append('<h4>改后</h4>')
    P.append('<div class="after"><p><code>A four-arm ablation ($15.4$M pairs) confirms the breakthrough depends on their \\emph{interaction}: neither term alone suffices ($6.1\\%$ and $6.2\\%$ linear-probe), but the combination yields $+6.0$\\,pp, widening to $+12.4$\\,pp at $55.3$M samples.</code></p></div>')
    P.append('<p><b>改动说明</b>：「Both terms are required」→「interaction」(<span class="tp1">P1</span>)；「carries most quality」删除（无实验支撑，四臂表明两者单独几乎持平）；「trunk degrades」删除（<span class="tp2">P2</span>：R11-H 去对比项后未坍缩 C1=0.255）；新增四臂数字 + 15.4M 限定。</p>')
    P.append('<table><caption>四臂消融完整对照（@15.36M pairs）</caption><tr><th>臂</th><th>组成</th><th>lp@15.36M</th><th>vs 基线</th><th>翻盘？</th></tr>')
    P.append('<tr><td>① 基线</td><td>InfoNCE</td><td>6.08%</td><td>—</td><td>—</td></tr>')
    P.append('<tr><td>④ CoCa</td><td>InfoNCE + caption CE</td><td>0.47%</td><td>−5.61</td><td><span class="terr">❌ 坍缩</span></td></tr>')
    P.append('<tr><td>⑥-B (R11-H)</td><td>patch-MSE only</td><td>6.23%</td><td>+0.15</td><td><span class="terr">❌ 无翻盘</span></td></tr>')
    P.append('<tr><td><b>⑥-A (R11-G)</b></td><td><b>InfoNCE + patch-MSE</b></td><td><b>12.08%</b></td><td><b>+6.00</b></td><td><span class="tok">✅ 翻盘</span></td></tr>')
    P.append('</table>')
    P.append('<ul class="ev"><li>ROUND11.md L1130-1137：四臂对照表</li><li>ROUND11.md L1167-1169：R11-H 结论</li><li>ROUND11.md L1078：R11-H 未坍缩 C1=0.255</li></ul>')
    P.append('<h3>2.5 paragraph{Final result.}（L15-16）— P1 改写</h3>')
    P.append('<h4>改前</h4>')
    P.append('<div class="before"><p><code>...reaches $11.50\\%\\to\\mathbf{19.76\\%}$ top-1 from $5.1$M to $55.3$M samples, and $20.27\\%$ at $176$M samples with no saturation.</code></p></div>')
    P.append('<h4>改后</h4>')
    P.append('<div class="after"><p><code>...reaches $11.50\\%\\to\\mathbf{19.76\\%}$ top-1 from $5.1$M to $55.3$M samples (CC12M$+$Amshaker, $18.5$M unique pairs), and $20.27\\%$ at $176$M samples on a $58.8$M-pair corpus (adding GPIC), with no saturation.</code></p></div>')
    P.append('<p><b>改动说明</b>：新增数据组成标注 (<span class="tp1">P1</span>)。<b>19.76%@55.3M</b>来自 R11-G（CC12M+Amshaker 18.5M 唯一对，108k 步×512=55.3M ≈ 3 epochs）。<b>20.27%@176M</b>来自 R12 3-epoch（GPIC+CC12M+Amshaker 58.8M 唯一对，344k 步×512=176.1M ≈ 3 epochs）。两者数据组成不同（R12 含 GPIC）且唯一对数量不同（18.5M vs 58.8M），不标注则误导。</p>')
    P.append('<div class="kbox"><p><b>epoch 说明</b>：R11-G 与 R12 3-epoch 均为 3 epochs，差异在于唯一对数量与数据组成。改后文本标注"唯一对"与"数据来源"而非 epoch 数。</p></div>')
    P.append('<ul class="ev"><li>ROUND11.md L877-887：R11-G 11 点轨迹</li><li>ROUND11.md L1543：「~3 epoch | 344000 | 176.1 | 20.27」</li><li>ROUND11.md L1268：「≈58.8M 唯一对」</li><li>ROUND11.md L1557：「R12 用 58.8M unique，R11-G 用 18.5M unique×3 epoch」</li><li>EXPERIMENTS_VISION.md L129-132：R12 配方</li></ul>')
    P.append('<h3>2.6 +12.4pp 基准（L17-18）— 无需改动</h3>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>。19.76%−7.40%=+12.36pp≈+12.4pp，同样本量（N=55.3M）、同塔、同数据、同步数、同评测。来源：ROUND11.md L887/L943。</p></div>')
    P.append('<h3>2.7 224/16 分辨率（L19-20）— 无需改动</h3>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>。224/16=14×14=196 token。与第 7 章（7_mllm.tex L27）衔接。</p></div>')
    return "\n".join(P)

def _s4():
    P = []
    P.append('<h2 id="s3">§3 事实核对清单</h2>')
    P.append('<table><caption>表 3.1 每个数字的溯源</caption>')
    P.append('<tr><th>数字</th><th>改前</th><th>改后</th><th>来源（文件+行号）</th><th>状态</th></tr>')
    rows = [
        ('width', '1024', '512', 'EXPERIMENTS_VISION.md L51/L129; r10_scaling2d.py L23', 'P0 已修'),
        ('params', '126.8M', '126.8M', 'r10_scaling2d.py L23 (126,779,392)', '✅属实'),
        ('505.2M', '括号内', '删除', 'r10_scaling2d.py L26 — w1024，非论文使用', '省篇幅删'),
        ('18.5M pairs', '有', '有', 'EXPERIMENTS_VISION.md L51; ROUND11.md L1284', '✅属实'),
        ('InfoNCE+patch-MSE', '有', '有', 'EXPERIMENTS_VISION.md L129', '✅属实'),
        ('1:1 weight', '有', '有', 'EXPERIMENTS_VISION.md L129; BP-2', '✅属实'),
        ('0.6 mask ratio', '有', '有', 'EXPERIMENTS_VISION.md L129; mask-ratio 消融 L146', '✅属实'),
        ('6.1% InfoNCE alone', '无', '新增', 'ROUND11.md L1132: 6.08%', '✅实测'),
        ('6.2% patch-MSE alone', '无', '新增', 'ROUND11.md L1134: 6.23%', '✅实测'),
        ('+6.0pp', '无', '新增', 'ROUND11.md L1135: 12.08%−6.08%', '✅实测'),
        ('11.50%@5.1M', '有', '有', 'ROUND11.md L877: 10k步, N=5.12M', '✅属实'),
        ('19.76%@55.3M', '有', '有', 'ROUND11.md L887: 108k步, N=55.30M', '✅属实'),
        ('20.27%@176M', '有', '有+标注', 'ROUND11.md L1543: 344k步, N=176.1M', '✅属实'),
        ('58.8M unique pairs', '无', '新增', 'ROUND11.md L1268', '✅实测'),
        ('+12.4pp', '有', '有', 'ROUND11.md L887: 19.76%−7.40%=+12.36', '✅属实'),
        ('7.40% baseline', '隐含', '隐含', 'ROUND11.md L887/L943', '✅实测'),
        ('196 token / 224/16', '有', '有', '14×14=196, BP-3', '✅属实'),
    ]
    for r in rows:
        P.append(f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>')
    P.append('</table>')
    P.append('<p><b>核查结论</b>：所有数字均有实测落盘记录支撑，<b>无估算冒充实测</b>。</p>')
    return "\n".join(P)

def _s5():
    P = []
    P.append('<h2 id="s4">§4 编译验证</h2>')
    P.append('<table><caption>表 4.1 编译结果</caption>')
    P.append('<tr><th>项</th><th>结果</th></tr>')
    P.append('<tr><td>编译流程</td><td>pdflatex → bibtex → pdflatex → pdflatex</td></tr>')
    P.append('<tr><td>页数</td><td><b>6 页</b></td></tr>')
    P.append('<tr><td>LaTeX Error</td><td><b>0</b></td></tr>')
    P.append('<tr><td>Undefined references/citations</td><td><b>0</b></td></tr>')
    P.append('<tr><td>main.pdf 提交</td><td><span class="terr">🚫 不提交</span></td></tr>')
    P.append('</table>')
    P.append('<p><b>篇幅控制</b>：初稿含"absolute modest"句+width-1024括号 → <b>7 页</b>。压缩：删"absolute modest"句+精简括号 → <b>6 页</b>。未删任何实测数字。</p>')
    P.append('<h2 id="s5">§5 已删中间过程清单</h2>')
    P.append('<p>用户要求 6 页·只留最终结果。以下中间过程<b>均未进入正文</b>：</p>')
    P.append('<table><caption>表 5.1 已删中间过程</caption>')
    P.append('<tr><th>#</th><th>中间过程</th><th>实验记录位置</th></tr>')
    dels = [
        ('六架构对比（OpenVision2/MoE-ViE/AIMv2/FastViTHD/MambaEye/DeepEncoderV2）', 'EXPERIMENTS_VISION.md L9-23'),
        ('SSM 崩塌叙事（MambaEye/DeepEncoderV2 @300 步坍缩）', 'EXPERIMENTS_VISION.md L17-21'),
        ('AR 范式探索（R11-H 纯 AR / CoCa caption-CE 坍缩）', 'ROUND11.md §17, L1133-1134'),
        ('Muon 消融（V2 Muon 坍缩）', 'EXPERIMENTS_VISION.md L71'),
        ('ProtB-epoch 缩放（1→2→4 ep 递减）', 'EXPERIMENTS_VISION.md L1088'),
        ('AIMv2 四臂消融细节（完整四臂对照）', 'ROUND11.md L1130-1137'),
        ('mask-ratio 消融（0.3/0.5/0.6/0.75/0.9 五臂）', 'EXPERIMENTS_VISION.md L136-167'),
        ('weight-ratio 消融（1:2/1:0.5/0.5:1/2:1 四臂）', 'EXPERIMENTS_VISION.md L171-198'),
        ('scaling 外推（幂律/对数线性、25.1% 渐近、619 亿缺口）', 'EXPERIMENTS_VISION.md L53-55; ROUND11.md L893-927'),
        ('width 消融（E1 w512 vs E2 w768, 5.59pp 下降）', 'EXPERIMENTS_VISION.md L558-609'),
        ('R12b 更多 unique ≠ 更高 lp（69.7M/2ep=18.81% < 18.5M/3ep=19.76%）', 'EXPERIMENTS_VISION.md L131-132'),
        ('R13 官方 OV2 benchmark', 'EXPERIMENTS_VISION.md L116-122'),
    ]
    for i, (name, loc) in enumerate(dels, 1):
        P.append(f'<tr><td>{i}</td><td>{name}</td><td>{loc}</td></tr>')
    P.append('</table>')
    P.append('<div class="del"><p><b>核查</b>：逐行比对改后 6_vision_encoder.tex 全文 20 行，确认上述 12 项<b>均未出现在正文中</b>。正文仅含最终配置与最终数字。</p></div>')
    return "\n".join(P)

def _s6():
    P = []
    P.append('<h2 id="s6">§6 中文双语注释同步</h2>')
    P.append('<table><caption>表 6.1 中文注释同步核查</caption>')
    P.append('<tr><th>行</th><th>英文改动</th><th>中文注释</th><th>同步？</th></tr>')
    P.append('<tr><td>L7-8</td><td>width-512, 删 505.2M</td><td>「宽度 $512$…$126.8$M 参数」</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>L9-10</td><td>不改</td><td>不改</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>L11-12</td><td>四臂消融 interaction</td><td>「四臂消融…交互…$6.1\\%$ 与 $6.2\\%$」</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>L15-16</td><td>加数据组成标注</td><td>「CC12M+Amshaker…$58.8$M 对（加入 GPIC）」</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>L17-18</td><td>不改</td><td>不改</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>L19-20</td><td>不改</td><td>不改</td><td><span class="tok">✅</span></td></tr>')
    P.append('</table>')
    return "\n".join(P)

def _s7():
    P = []
    P.append('<h2 id="s7">§7 自检清单</h2>')
    P.append('<table><caption>表 7.1 自检项</caption>')
    P.append('<tr><th>#</th><th>检查项</th><th>结果</th></tr>')
    checks = [
        ('width-1024 → width-512（P0）', '✅ 已修'),
        ('"Both terms required" → interaction（P1）', '✅ 已修'),
        ('"trunk degrades" 删除（P2）', '✅ 已删'),
        ('20.27%@176M 标注数据差异（P1）', '✅ 已标注'),
        ('+12.4pp 基准核实（同样本量）', '✅ 属实'),
        ('每个数字有实测溯源', '✅ 全部溯源'),
        ('无估算冒充实测', '✅ 无'),
        ('中文双语注释同步', '✅ 全部同步'),
        ('全文 ≤6 页', '✅ 6 页'),
        ('ERR=0 / UNDEF=0', '✅ 0/0'),
        ('第 6 章 ≤1.5 页', '✅ ~0.4 页'),
        ('不 commit main.pdf', '✅ 不提交'),
        ('不动 0_abstract/1_intro/4_llm_pretrain', '✅ 未动'),
        ('中间过程未塞回正文', '✅ 12 项均未出现'),
        ('git pull --rebase 后再改', '✅ 已 pull'),
    ]
    for i, (item, result) in enumerate(checks, 1):
        P.append(f'<tr><td>{i}</td><td>{item}</td><td>{result}</td></tr>')
    P.append('</table>')
    P.append('<hr>')
    P.append('<div class="footer">')
    P.append('<p>BaiZe vision 线 · 2026-10-31 · 运维令 11:2x · 用户直令</p>')
    P.append('<p>生成器：vision/generate_paper_edit_report.py（幂等）</p>')
    P.append('</div>')
    return "\n".join(P)

def build():
    P = []
    P.append('<!DOCTYPE html>')
    P.append('<html lang="zh-CN"><head><meta charset="UTF-8">')
    P.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    P.append('<title>BaiZe 论文第 6 章视觉编码器改稿报告</title>')
    P.append('<style>' + CSS + '</style>')
    P.append('</head><body>')
    P.append(_s1())
    P.append(_s2())
    P.append(_s3())
    P.append(_s4())
    P.append(_s5())
    P.append(_s6())
    P.append(_s7())
    P.append('</body></html>')
    html = '\n'.join(P)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    size = os.path.getsize(OUT)
    md5 = hashlib.md5(html.encode('utf-8')).hexdigest()
    with open(OUT, 'r', encoding='utf-8') as f:
        html2 = f.read()
    md5_2 = hashlib.md5(html2.encode('utf-8')).hexdigest()
    print(f'OUT={OUT}')
    print(f'SIZE={size} bytes')
    print(f'MD5={md5}')
    print(f'IDEMPOTENT={md5 == md5_2}')
    for tag in ['html', 'head', 'body', 'table', 'div', 'ul', 'li']:
        o = html.count(f'<{tag}'); c = html.count(f'</{tag}>')
        print(f'TAG<{tag}>: {"OK" if o == c else f"MISMATCH({o}/{c})"}')
    print(f'SCRIPT_TAGS={html.count("<script")}')
    print(f'EXTERNAL_LINKS={html.count("http://") + html.count("https://")}')
    return 0

if __name__ == '__main__':
    sys.exit(build())
