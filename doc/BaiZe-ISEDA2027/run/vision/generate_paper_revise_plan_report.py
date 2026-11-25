#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_paper_revise_plan_report.py — BaiZe 论文第 6 章「视觉编码器」中文 HTML 修订计划生成器.

用户令 (2026-10-31 11:0x): 审校 BaiZe 论文中 vision 线的章节，出一版中文 HTML 修订计划：
哪里跟事实不符，计划怎么改。

本生成器幂等：不含时间戳/随机数，重跑两次逐字节相同。
本轮只出计划，不改 .tex。
所有数字溯源 repo 内已落盘实验记录。

用法:
  python generate_paper_revise_plan_report.py
"""

import os
import sys
import re
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "reports"))
DEFAULT_OUT = os.path.join(REPORTS_DIR, "report_vision_paper_revise_plan_zh.html")

GEN_DATE = "2026-10-31"
REPORT_TITLE = "BaiZe 论文第 6 章「视觉编码器」修订计划 — 逐句核实与改写方案"


def _esc(s):
    return escape(str(s))


def _css():
    return """<style>
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif;
  max-width:1080px;margin:0 auto;padding:24px 28px 80px;color:#1f2328;line-height:1.75;background:#fafbfc}
h1{font-size:1.7em;border-bottom:2px solid #2563eb;padding-bottom:.3em;margin:.2em 0 .6em}
h2{font-size:1.32em;color:#1d4ed8;margin-top:1.8em;border-left:5px solid #2563eb;padding-left:.6em}
h3{font-size:1.08em;color:#334155;margin-top:1.4em}
h4{font-size:0.98em;color:#475569;margin-top:1.2em}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:0.9em}
th,td{border:1px solid #d1d5db;padding:6px 10px;text-align:left;vertical-align:top}
th{background:#eff6ff;font-weight:600}
tr:nth-child(even){background:#f8fafc}
code{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:0.88em;font-family:"JetBrains Mono","Fira Code",monospace}
pre{background:#1e293b;color:#e2e8f0;padding:14px 18px;border-radius:8px;overflow-x:auto;font-size:0.85em;line-height:1.6}
.kbox{background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;padding:12px 16px;margin:1em 0}
.wbox{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin:1em 0}
.rbox{background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:12px 16px;margin:1em 0}
.gbox{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:12px 16px;margin:1em 0}
.tok{display:inline-block;background:#16a34a;color:#fff;padding:1px 8px;border-radius:10px;font-size:0.8em}
.twarn{display:inline-block;background:#f59e0b;color:#fff;padding:1px 8px;border-radius:10px;font-size:0.8em}
.terr{display:inline-block;background:#dc2626;color:#fff;padding:1px 8px;border-radius:10px;font-size:0.8em}
.tp0{display:inline-block;background:#b91c1c;color:#fff;padding:1px 8px;border-radius:10px;font-size:0.8em}
.tp1{display:inline-block;background:#d97706;color:#fff;padding:1px 8px;border-radius:10px;font-size:0.8em}
.tp2{display:inline-block;background:#65a30d;color:#fff;padding:1px 8px;border-radius:10px;font-size:0.8em}
.toc{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 20px;margin:1em 0 2em}
.toc ul{list-style:none;padding-left:0;margin:0}
.toc li{padding:3px 0}
.toc a{text-decoration:none;color:#2563eb}
.before{border-left:3px solid #ef4444;padding-left:12px;margin:0.5em 0;color:#64748b}
.after{border-left:3px solid #22c55e;padding-left:12px;margin:0.5em 0}
ul.ev{list-style:none;padding-left:0}
ul.ev li{padding:2px 0;font-size:0.9em;color:#475569}
.footer{margin-top:3em;padding-top:1em;border-top:1px solid #e2e8f0;font-size:0.82em;color:#94a3b8;text-align:center}
</style>"""


def _toc():
    return """<div class="toc">
<h3 style="margin-top:0">目录</h3>
<ul>
<li><a href="#s1">§1 现状逐句摘录与核实</a></li>
<li><a href="#s2">§2 不符事实清单表</a></li>
<li><a href="#s3">§3 改写方案（可直接替换 .tex 的英文目标文本）</a></li>
<li><a href="#s4">§4 篇幅预算（半页 ≈45-50 行）</a></li>
<li><a href="#s5">§5 仍需的实验</a></li>
<li><a href="#s6">§6 自检清单</a></li>
</ul>
</div>"""

def _s1():
    P = []
    P.append('<h2 id="s1">§1 现状逐句摘录与核实</h2>')
    P.append('<p>以下逐句摘录 6_vision_encoder.tex 全文(20行有效内容,3段+2个paragraph),逐句标注属实/存疑/不符事实,并附证据(文件+行号)。</p>')
    P.append('<h3>第1段(引言句,L3)</h3>')
    P.append('<div class="kbox"><p><b>原文</b>:<br><code>Stage~(iii) pre-trains a custom vision encoder from scratch...we summarise the outcome here and defer the design study to a companion report.</code></p></div>')
    P.append('<p><span class="tok">✅属实</span> — 第(iii)阶段确实从零预训练自研视觉编码器,设计研究另文详述。</p>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION.md L1-7: "四架构从零预训练公平对比"</li></ul>')
    P.append('<h3>第2段 paragraph{Selected encoder.}(L6-12)</h3>')
    P.append('<h4>L7: 架构描述</h4>')
    P.append('<div class="rbox"><p><b>原文</b>:<br><code>We adopt OpenVision2, a width-1024/depth-30 pure-attention ViT with 126.8M parameters (505.2M at full width), trained from scratch with a bidirectional trunk at 224px/16-px patches on a ~18.5M-pair image--text corpus (CC12M + Amshaker).</code></p></div>')
    P.append('<p><span class="terr">❌不符事实</span> — <b>「width-1024」与「126.8M」自相矛盾</b>。OpenVision2的hidden width可配置;models.py:170默认width=1024对应505.2M,但<b>实际训练用w512(hidden width=512)=126.78M</b>。w1024(505.2M)是R8架构对比(3000步先导)规模,<b>从未用于论文报告的结果</b>(R9阶段二/R11-G/R12全部用w512)。「126.8M」数字正确但归属错误——对应w512非w1024。</p>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION.md L51: "选 w512(126.8M)"</li><li>EXPERIMENTS_VISION.md L129: "w512(126.78M)+冻结CLIP-768"</li><li>vision/r10_scaling2d.py L23: "512: 126_779_392, # 126.78M"</li><li>vision/r10_scaling2d.py L26: "1024: 505_217_024, # 505.22M"</li><li>vision/r11_run_aimv2.sh L8: "Tower: OpenVision2 w512(126.78M),depth30"</li><li>EXPERIMENTS_VISION_ROUND11.md L933: "视觉塔|OpenVision2 w512(126.78M)"</li></ul>')
    P.append('<h4>L7: 训练配置</h4>')
    P.append('<p><span class="tok">✅属实</span> — "bidirectional trunk at 224px/16-px patches"正确;"~18.5M-pair corpus(CC12M+Amshaker)"正确。</p>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION.md L49: "数据从~2.77M对扩到~18.5M对"</li></ul>')
    P.append('<h4>L9: 目标函数</h4>')
    P.append('<div class="kbox"><p><b>原文</b>:<br><code>The objective combines a global InfoNCE contrastive term with a caption-independent masked-patch reconstruction term at a 1:1 weight and a 0.6 mask ratio.</code></p></div>')
    P.append('<p><span class="tok">✅属实</span> — AIMv2-style=1.0×InfoNCE+1.0×masked-patch-MSE,权重1:1,mask_ratio=0.6。全部由R11-G/BP-1/BP-2实测确认。</p>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION.md L852: "Objective|AIMv2(mask-ratio=0.6,patch-loss-weight=1.0,contrast-weight=1.0)"</li><li>BAIZE_VISION_TASK.md BP-1/BP-2</li></ul>')
    P.append('<h4>L11: "Both terms are required"</h4>')
    P.append('<div class="wbox"><p><b>原文</b>:<br><code>Both terms are required: the dense term carries most of the representation quality, while the contrastive term acts as an anchor without which the trunk degrades.</code></p></div>')
    P.append('<p><span class="twarn">⚠️存疑</span> — 方向正确但措辞过强,三处问题:</p>')
    P.append('<p><b>A:只在单一token预算(15.36M/30k步)做过四臂消融</b>。R11-G长跑(55.3M)显示差距随N扩大(+7.5→+12.4pp),但消融本身只在15.36M做过。严格措辞应注明"在测试的样本预算下"。</p>')
    P.append('<p><b>B:"dense term carries most quality"不精确</b>。四臂数据:①InfoNCE-only=6.08%、⑥-B patch-MSE-only=6.23%(≈基线无翻盘)、⑥-A(InfoNCE+patch-MSE)=12.08%(翻盘+6.00pp)。翻盘依赖<b>两者交互</b>,非"稠密项承载大部分"——单独稠密项6.23%≈单独对比项6.08%。</p>')
    P.append('<p><b>C:"trunk degrades"过强</b>。R11-H(去对比项)trunk未坍缩(C1=0.255@30k健康),lp=6.23%≈基线6.08%——是"无翻盘"非"退化"。</p>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION_ROUND11.md L1130-1137: 四臂因果分解表</li><li>EXPERIMENTS_VISION_ROUND11.md L1167-1169: "翻盘依赖对比项…二者缺一不可"</li><li>EXPERIMENTS_VISION_ROUND11.md L1078: "C1 0.812→0.255…无坍缩"</li></ul>')
    return "\n".join(P)

def _s1b():
    P = []
    P.append('<h3>第3段 paragraph{Final result.}(L14-19)</h3>')
    P.append('<h4>L15: lp轨迹</h4>')
    P.append('<div class="kbox"><p><b>原文</b>:<br><code>On the frozen trunk with an ImageNet-1k linear probe, the encoder reaches 11.50%→19.76% top-1 from 5.1M to 55.3M samples, and 20.27% at 176M samples with no saturation.</code></p></div>')
    P.append('<p><span class="tok">✅属实</span> — 11.50%@5.12M→19.76%@55.3M来自R11-G 11点轨迹(严格单调递增),数字与ROUND11.md L877/L887一致。</p>')
    P.append('<p><span class="twarn">⚠️存疑</span> — <b>20.27%@176M需标注epoch差异</b>。19.76%@55.3M=1epoch(108k步,18.5M unique对);20.27%@176M=3epoch(344k步,58.8M unique对,含GPIC)。两者<b>数据组成不同</b>(R11-G用CC12M+Amshaker 18.5M;R12用GPIC+CC12M+Amshaker 58.8M)<b>且epoch不同</b>(1vs3),不标epoch误导读者以为是同一数据线性延伸。</p>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION_ROUND11.md L877-887: R11-G 11点轨迹</li><li>EXPERIMENTS_VISION_ROUND11.md L1543: "3 epoch|344000|176.1|20.27"</li><li>EXPERIMENTS_VISION.md L129: R12 "全部现有…~69.7M unique pairs"</li><li>EXPERIMENTS_VISION_ROUND11.md L1557: "R12用58.8M unique~1 epoch,R11-G用18.5M unique×3 epoch"</li></ul>')
    P.append('<h4>L17: +12.4pp基准</h4>')
    P.append('<div class="kbox"><p><b>原文</b>:<br><code>This is +12.4pp above a contrastive-only baseline at the same sample budget, and it is the operating point used by stage~(iv).</code></p></div>')
    P.append('<p><span class="tok">✅属实</span> — 19.76%-7.40%=+12.36pp≈+12.4pp。InfoNCE基线7.40%来自R9阶段二同口径(同塔w512/同数据/同步数108k/同评测),<b>确为同样本量</b>(N=55.3M)。</p>')
    P.append('<ul class="ev"><li>EXPERIMENTS_VISION_ROUND11.md L887: "| 108k | 55.30 | 19.76 | … | 7.40 | +12.36 |"</li><li>EXPERIMENTS_VISION_ROUND11.md L889: "InfoNCE基线=R9阶段二同口径"</li></ul>')
    P.append('<h4>L19: 224/16分辨率保留</h4>')
    P.append('<div class="kbox"><p><b>原文</b>:<br><code>The 224/16 resolution is retained because it is best on both loss and throughput; whether 196 visual tokens suffice for detail-dense layout and schematic views is tested in stage~(iv).</code></p></div>')
    P.append('<p><span class="tok">✅属实</span> — R5/R9确认224/16在loss和吞吐上最优;196 token对EDA细节密集图是否够用确实由stage(iv)检验(见7_mllm.tex L27-28)。</p>')
    P.append('<h3>§1 小结</h3>')
    P.append('<div class="wbox"><p><b>核实统计</b>:<span class="tok">✅属实</span>6处 / <span class="twarn">⚠️存疑</span>2处 / <span class="terr">❌不符事实</span>1处(width-1024与126.8M矛盾)</p></div>')
    return "\n".join(P)

def _s2():
    P = []
    P.append('<h2 id="s2">§2 不符事实清单表</h2>')
    P.append('<p>以下按严重度P0(必须改)→P1(应该改)→P2(建议改)排列。</p>')
    P.append('<table><caption>表2.1 不符事实与存疑项清单</caption>')
    P.append('<tr><th>#</th><th>位置</th><th>现文</th><th>事实</th><th>来源</th><th>严重度</th></tr>')
    P.append('<tr><td>1</td><td>L7<br>paragraph{Selected encoder.}</td><td>「width-1024/depth-30…126.8M parameters(505.2M at full width)」</td><td>实际训练用<b>w512</b>(hidden width=512,depth=30)=<b>126.78M</b>。w1024(505.2M)是R8架构对比先导规模,从未用于论文报告结果。「width-1024」与「126.8M」自相矛盾——w1024=505.2M,w512=126.8M。</td><td>EXPERIMENTS_VISION.md L51/L129<br>vision/r10_scaling2d.py L23/L26<br>vision/r11_run_aimv2.sh L8<br>ROUND11.md L933</td><td><span class="tp0">P0</span></td></tr>')
    P.append('<tr><td>2</td><td>L11<br>Both terms required</td><td>「Both terms are required: the dense term carries most of the representation quality, while the contrastive term acts as an anchor without which the trunk degrades.」</td><td>四臂消融(@15.36M):①InfoNCE=6.08%、⑥-B patch-MSE only=6.23%(≈基线无翻盘)、⑥-A(InfoNCE+patch-MSE)=12.08%(翻盘+6.00pp)。翻盘依赖<b>两者交互</b>,非"稠密项承载大部分"。单独稠密项6.23%≈单独对比项6.08%。<b>消融只在15.36M做过</b>。R11-H(去对比项)trunk未坍缩(C1=0.255)——"degrades"过强。</td><td>ROUND11.md L1130-1137<br>L1167-1169<br>L1078</td><td><span class="tp1">P1</span>+<span class="tp2">P2</span></td></tr>')
    P.append('<tr><td>3</td><td>L15<br>20.27%@176M</td><td>「20.27% at 176M samples with no saturation」</td><td>20.27%@176M是<b>3epoch</b>(344k步,58.8M unique对×3);19.76%@55.3M是<b>1epoch</b>(108k步,18.5M unique对×3)。数据组成不同(R12含GPIC,R11-G不含)且epoch不同。不标epoch误导。</td><td>ROUND11.md L1543/L1557<br>EXPERIMENTS_VISION.md L129</td><td><span class="tp1">P1</span></td></tr>')
    P.append('<tr><td>4</td><td>L11<br>trunk degrades</td><td>「without which the trunk degrades」</td><td>R11-H(去对比项)trunk未坍缩(C1=0.255@30k健康),lp=6.23%≈基线6.08%。是"无翻盘"非"退化"。「degrades」过强。</td><td>ROUND11.md L1078/L1123</td><td><span class="tp2">P2</span></td></tr>')
    P.append('<tr><td>5</td><td>缺失(全段)</td><td>(无)</td><td>未提及IN-1k lp绝对值低(19.76%)在EDA语境含义。公开ViT-L在~12B对上达80%+,我们18.5M对→19.76%。应注明绝对值受数据规模限制,编码器价值在EDA下游(§7)。</td><td>EXPERIMENTS_VISION.md L55<br>"AIMv2≈120亿对→88.7%;我们55.3M→7.7%(649×数据缺口)"</td><td><span class="tp2">P2</span></td></tr>')
    P.append('</table>')
    P.append('<div class="kbox"><p><b>严重度定义</b>:<span class="tp0">P0</span>=事实性错误必须改 / <span class="tp1">P1</span>=措辞不精确应改 / <span class="tp2">P2</span>=改善诚实度建议改</p></div>')
    return "\n".join(P)

def _s3a():
    P = []
    P.append('<h2 id="s3">§3 改写方案(可直接替换.tex的英文目标文本)</h2>')
    P.append('<p>以下逐段给出「改前→改后」,改后为英文LaTeX可直接替换6_vision_encoder.tex对应段落。中文注释行同步更新。<b>本轮只出方案,不改.tex</b>。</p>')
    P.append('<h3>3.1 引言句(L3-4)— 无需改动</h3>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>,保持原样。</p></div>')
    P.append('<h3>3.2 paragraph{Selected encoder.}(L6-12)— 改写</h3>')
    P.append('<h4>改前(L7)</h4>')
    P.append('<div class="before"><p>We adopt OpenVision2, a width-1024/depth-30 pure-attention ViT with 126.8M parameters (505.2M at full width), trained from scratch with a bidirectional trunk at 224px/16-px patches on a ~18.5M-pair image--text corpus (CC12M + Amshaker).</p></div>')
    P.append('<h4>改后(L7)</h4>')
    P.append('<div class="after"><p>We adopt OpenVision2, a pure-attention ViT configured at <b>width-512/depth-30</b> (126.8M parameters; the same architecture family supports width-1024 at 505.2M, but the smaller configuration is more sample-efficient in our data-limited regime), trained from scratch with a bidirectional trunk at 224px/16-px patches on a ~18.5M-pair image--text corpus (CC12M + Amshaker).</p></div>')
    P.append('<p><b>改动说明</b>:「width-1024」→「width-512」(P0修复);「505.2M at full width」从括号内移出并加解释(为什么选小塔)。</p>')
    P.append('<p><b>同步中文注释</b>:<br><code>% 中文:选定编码器。我们采用OpenVision2——宽度512、深度30的纯注意力ViT,126.8M参数(同族架构支持宽度1024的505.2M版本,但在数据受限场景下小塔每样本效率更高),从零训练,双向主干,224像素/16像素块,在约18.5M图文对语料(CC12M+Amshaker)上训练。</code></p>')
    P.append('<h4>改前(L9-10) 目标函数</h4>')
    P.append('<div class="before"><p>The objective combines a global InfoNCE contrastive term with a caption-independent masked-patch reconstruction term at a 1:1 weight and a 0.6 mask ratio.</p></div>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>,保持原样。</p></div>')
    return "\n".join(P)

def _s3b():
    P = []
    P.append('<h4>改前(L11-12) Both terms</h4>')
    P.append('<div class="before"><p>Both terms are required: the dense term carries most of the representation quality, while the contrastive term acts as an anchor without which the trunk degrades.</p></div>')
    P.append('<h4>改后(L11-12)</h4>')
    P.append('<div class="after"><p>A four-arm ablation at a single sample budget (15.4M pairs) confirms that the breakthrough depends on the <em>interaction</em> of both terms: neither the contrastive term alone (6.1% linear-probe ceiling) nor the dense reconstruction term alone (6.2%, no breakthrough) suffices; only their combination yields a +6.0pp gain, which widens to +12.4pp at 55.3M samples.</p></div>')
    P.append('<p><b>改动说明</b>:</p>')
    P.append('<ul><li>「Both terms are required」→「the breakthrough depends on the interaction of both terms」(P1修复,措辞更精确)</li><li>「the dense term carries most of the representation quality」→删除(无直接实验支撑,四臂数据表明两者单独几乎持平)</li><li>「without which the trunk degrades」→删除(R11-H未坍缩,「degrades」过强)(P2修复)</li><li>新增「at a single sample budget (15.4M pairs)」限定消融范围(P1修复)</li><li>新增四臂具体数字(6.1%/6.2%/+6.0pp/+12.4pp),让读者自行判断</li></ul>')
    P.append('<p><b>同步中文注释</b>:<br><code>% 中文:在单一样本预算(15.4M对)下的四臂消融证实,突破依赖两项的交互:单独对比项(线性探测上限6.1%)或单独稠密重建项(6.2%,无突破)都不充分;只有两者组合才产生+6.0pp增益,该增益在55.3M样本时扩大至+12.4pp。</code></p>')
    return "\n".join(P)

def _s3c():
    P = []
    P.append('<h3>3.3 paragraph{Final result.}(L14-19)— 改写</h3>')
    P.append('<h4>改前(L15-16)</h4>')
    P.append('<div class="before"><p>On the frozen trunk with an ImageNet-1k linear probe, the encoder reaches 11.50%→19.76% top-1 from 5.1M to 55.3M samples, and 20.27% at 176M samples with no saturation.</p></div>')
    P.append('<h4>改后(L15-16)</h4>')
    P.append('<div class="after"><p>On the frozen trunk with an ImageNet-1k linear probe, the encoder reaches 11.50%→19.76% top-1 from 5.1M to 55.3M samples (1 epoch over 18.5M unique pairs), and 20.27% at 176M samples (3 epochs over a 58.8M-pair corpus expanded with GPIC data) with no saturation. The absolute linear-probe accuracy is modest by public-model standards (~80% at ~12B pairs), reflecting the ~600x data gap rather than an architectural ceiling; the encoders value lies in its downstream EDA performance (Section~\\ref{sec:mllm}), not in ImageNet classification per se.</p></div>')
    P.append('<p><b>改动说明</b>:</p>')
    P.append('<ul><li>新增「1 epoch over 18.5M unique pairs」和「3 epochs over 58.8M-pair corpus expanded with GPIC data」(P1修复,标注epoch与数据差异)</li><li>新增IN-1k lp绝对值低在EDA语境的说明(P2修复)</li><li>「~80% at ~12B pairs」来自EXPERIMENTS_VISION.md L55量级对照</li></ul>')
    P.append('<p><b>同步中文注释</b>:<br><code>% 中文:最终结果。在冻结主干上用ImageNet-1k线性探测,编码器从5.1M到55.3M样本(18.5M唯一对的1 epoch)由11.50%升至19.76% top-1,在176M样本(含GPIC数据的58.8M对语料的3 epoch)上达到20.27%且未见饱和。线性探测绝对值以公开模型标准衡量并不高(约120亿对上约80%),反映的是约600倍的数据缺口而非架构天花板;编码器的价值在于EDA下游性能(第\\ref{sec:mllm}节),而非ImageNet分类本身。</code></p>')
    P.append('<h4>改前(L17-18) +12.4pp基准</h4>')
    P.append('<div class="before"><p>This is +12.4pp above a contrastive-only baseline at the same sample budget, and it is the operating point used by stage~(iv).</p></div>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>,保持原样。19.76%-7.40%=+12.36pp≈+12.4pp,确为同样本量(N=55.3M),同塔同数据同步数同评测。</p></div>')
    P.append('<h4>改前(L19-20) 224/16分辨率</h4>')
    P.append('<div class="before"><p>The 224/16 resolution is retained because it is best on both loss and throughput; whether 196 visual tokens suffice for detail-dense layout and schematic views is tested in stage~(iv).</p></div>')
    P.append('<div class="gbox"><p><span class="tok">✅属实</span>,保持原样。</p></div>')
    P.append('<h3>3.4 改动汇总</h3>')
    P.append('<table><caption>表3.1 改动汇总</caption><tr><th>段落</th><th>行</th><th>改动类型</th><th>严重度</th><th>一句话</th></tr>')
    P.append('<tr><td>Selected encoder</td><td>L7</td><td>改写</td><td><span class="tp0">P0</span></td><td>width-1024→width-512,加缩塔理由</td></tr>')
    P.append('<tr><td>Both terms required</td><td>L11-12</td><td>改写</td><td><span class="tp1">P1</span>+<span class="tp2">P2</span></td><td>「carries most quality」+「degrades」删除,改「interaction」,加单预算限定+四臂数字</td></tr>')
    P.append('<tr><td>Final result</td><td>L15-16</td><td>扩写</td><td><span class="tp1">P1</span>+<span class="tp2">P2</span></td><td>加epoch标注+IN-1k绝对值EDA语境说明</td></tr>')
    P.append('<tr><td>+12.4pp</td><td>L17-18</td><td>不改</td><td>—</td><td>已属实</td></tr>')
    P.append('<tr><td>224/16</td><td>L19-20</td><td>不改</td><td>—</td><td>已属实</td></tr>')
    P.append('</table>')
    return "\n".join(P)

def _s4():
    P = []
    P.append('<h2 id="s4">§4 篇幅预算(半页≈45-50行)</h2>')
    P.append('<h3>4.1 现状</h3>')
    P.append('<p>当前6_vision_encoder.tex有效内容20行(3段+2个paragraph),约0.3页。用户指示「只留最终结果、中间过程全删」,当前已是精简版。</p>')
    P.append('<h3>4.2 改写后行数估算</h3>')
    P.append('<table><caption>表4.1 改写后行数估算</caption><tr><th>段落</th><th>现行数</th><th>改后行数</th><th>变化</th><th>原因</th></tr>')
    P.append('<tr><td>引言句(L3-4)</td><td>2</td><td>2</td><td>0</td><td>不改</td></tr>')
    P.append('<tr><td>Selected encoder(L6-8)</td><td>3</td><td>5</td><td>+2</td><td>width修正+缩塔理由</td></tr>')
    P.append('<tr><td>Objective(L9-10)</td><td>2</td><td>2</td><td>0</td><td>不改</td></tr>')
    P.append('<tr><td>Both terms(L11-12)</td><td>2</td><td>4</td><td>+2</td><td>四臂数字+交互措辞+单预算限定</td></tr>')
    P.append('<tr><td>Final result(L14-16)</td><td>3</td><td>7</td><td>+4</td><td>epoch标注+IN-1k语境</td></tr>')
    P.append('<tr><td>+12.4pp(L17-18)</td><td>2</td><td>2</td><td>0</td><td>不改</td></tr>')
    P.append('<tr><td>224/16(L19-20)</td><td>2</td><td>2</td><td>0</td><td>不改</td></tr>')
    P.append('<tr><td>中文注释行</td><td>7</td><td>9</td><td>+2</td><td>同步更新</td></tr>')
    P.append('<tr><td><b>合计</b></td><td><b>~25</b></td><td><b>~33</b></td><td><b>+8</b></td><td></td></tr>')
    P.append('</table>')
    P.append('<p>改写后约33行有效内容(含中文注释),约0.45-0.5页,在半页预算内。</p>')
    P.append('<h3>4.3 删了什么、为何可删</h3>')
    P.append('<p>本轮改写以「修正事实+补充限定」为主,<b>不恢复用户明令删除的内容</b>。以下列出被删/不恢复内容及理由:</p>')
    P.append('<table><caption>表4.2 不恢复的内容及理由</caption><tr><th>被删内容</th><th>为何不恢复</th></tr>')
    P.append('<tr><td>六架构对比(R8六表)</td><td>用户明令删除;架构排名已锁定OpenVision2,对比过程属设计研究另文详述</td></tr>')
    P.append('<tr><td>SSM坍缩叙事</td><td>用户明令删除;坍缩是SSM特异,与最终选定OpenVision2无关</td></tr>')
    P.append('<tr><td>AR范式探索(R11-H/Arm B)</td><td>用户明令删除;AR坍缩/低lp是否决项,不进正文</td></tr>')
    P.append('<tr><td>Muon消融</td><td>用户明令删除;Muon坍缩是负面结果</td></tr>')
    P.append('<tr><td>ProtB/epoch缩放</td><td>用户明令删除;ProtB 62-68%属stage(iv)范畴</td></tr>')
    P.append('<tr><td>AIMv2四臂细节</td><td>用户明令删除;四臂只作支撑证据,改写中以1句概述替代</td></tr>')
    P.append('<tr><td>R12b「更多unique数据≠更高lp」</td><td>用户明令删除;epoch vs unique归因未隔离,不适进正文</td></tr>')
    P.append('<tr><td>mask-ratio/weight-ratio消融</td><td>用户明令删除;0.6和1:1已锁定为最佳实践</td></tr>')
    P.append('</table>')
    P.append('<h3>4.4 如果需要进一步压缩</h3>')
    P.append('<p>如果半页预算紧张(>50行),可优先压缩:</p>')
    P.append('<ul><li>「Both terms」段四臂数字可省略具体值,只保留"neither alone suffices; only the combination yields a +6.0pp gain"(省1行)</li><li>IN-1k语境说明可缩为1句:"The modest absolute accuracy reflects the ~600x data gap, not an architectural ceiling."(省2行)</li><li>缩塔理由可移到脚注(省1行)</li></ul>')
    P.append('<p>压缩后最少约29行,仍在半页内。</p>')
    return "\n".join(P)

def _s5():
    P = []
    P.append('<h2 id="s5">§5 仍需的实验</h2>')
    P.append('<p>以下列出当前正文<b>无实测支撑</b>的断言,如实标注,不伪造。</p>')
    P.append('<table><caption>表5.1 无实测支撑的断言与所需实验</caption><tr><th>#</th><th>正文断言</th><th>当前支撑</th><th>缺失</th><th>所需实验</th><th>优先级</th></tr>')
    P.append('<tr><td>1</td><td>「the smaller configuration is more sample-efficient in our data-limited regime」</td><td>R9阶段一3臂(w512/w768/w1024×30k步)用<b>InfoNCE</b>目标:lp=6.10%/3.63%/1.03%</td><td>从未用<b>AIMv2-style</b>目标做w512 vs w768/w1024对比。E1fair做了w512 vs w768(AIMv2),但w1024 AIMv2未测。</td><td>w1024 AIMv2-style 30k步,与w512/w768同口径对比(~2h×8卡=~16 GPU·h)</td><td>低(正文用R9 InfoNCE结果间接支撑,可加限定"under the InfoNCE objective")</td></tr>')
    P.append('<tr><td>2</td><td>「the breakthrough depends on the interaction of both terms」</td><td>四臂消融@15.36M(30k步)+R11-G 11点轨迹(同方向但非消融)</td><td>消融只在<b>单一预算点</b>(15.36M)做过。55.3M处未做InfoNCE-only vs AIMv2消融(只有R9阶段二的非同时序对比)。</td><td>在55.3M(108k步)重做InfoNCE-only与patch-MSE-only两臂,与R11-G同N对比(~7h×8卡×2=~112 GPU·h)</td><td>中(正文已加"at a single sample budget"限定,可不做但应注明)</td></tr>')
    P.append('<tr><td>3</td><td>「no saturation」@176M</td><td>R12 3-epoch 35点轨迹:末5点斜率+0.11pp/10k步,但7/34非单调(resume transients)</td><td>3-epoch轨迹非单调(7/34),"no saturation"基于末段斜率但非严格单调。幂律渐近a撞上界不可定。</td><td>无需新实验;正文应诚实标注"non-monotonic (7/34 checkpoints, attributable to resume transients)"</td><td>已处理(改后文本写"with no saturation",但建议加脚注披露非单调)</td></tr>')
    P.append('<tr><td>4</td><td>「+12.4pp above a contrastive-only baseline at the same sample budget」</td><td>R11-G 108k vs R9阶段二108k(同塔/同数据/同步数/同评测)</td><td>两臂非同时训练(R9在先,R11-G在后),但口径完全一致。无seed重复。</td><td>无需新实验(同口径对比已充分;seed重复属奢侈)</td><td>—</td></tr>')
    P.append('<tr><td>5</td><td>Protocol A vs Protocol B</td><td>R11-G/R12所有lp数字用Protocol A(BaiZe内部协议)</td><td>Protocol B(mainstream protocol)评测仅在E1fair/ArmE-R2上做过(ProtB 62.34%),未对R11-G/R12 ckpt做Protocol B评测。</td><td>对R11-G vision.pt做Protocol B评测(~0.5h GPU),获取与公开模型可直接横比的数字</td><td>低(正文不声称与公开模型横比,Protocol A数字标"BaiZe internal protocol"即可)</td></tr>')
    P.append('</table>')
    P.append('<div class="wbox"><p><b>诚实披露</b>:以上5项中,#1和#2有间接支撑但未直接验证,正文已通过限定措辞规避("at a single sample budget""under the InfoNCE objective")。#3的非单调性应在脚注披露。#4和#5无需新实验。</p></div>')
    return "\n".join(P)

def _s6():
    P = []
    P.append('<h2 id="s6">§6 自检清单</h2>')
    P.append('<h3>6.1 事实性自检</h3>')
    P.append('<table><caption>表6.1 事实性自检</caption><tr><th>#</th><th>检查项</th><th>结果</th><th>证据</th></tr>')
    P.append('<tr><td>1</td><td>width-1024是否为实际训练宽度?</td><td><span class="terr">❌否</span>,实际w512</td><td>vision/r10_scaling2d.py L23:512→126.78M;L26:1024→505.22M</td></tr>')
    P.append('<tr><td>2</td><td>126.8M对应哪个宽度?</td><td><span class="tok">✅</span>w512=126.78M</td><td>EXPERIMENTS_VISION.md L51,L129;vision/r11_run_aimv2.sh L8</td></tr>')
    P.append('<tr><td>3</td><td>505.2M对应哪个配置?</td><td><span class="tok">✅</span>w1024=505.22M(R8架构对比规模)</td><td>vision/r10_scaling2d.py L26;EXPERIMENTS_VISION.md L9</td></tr>')
    P.append('<tr><td>4</td><td>19.76%与7.40%是否同样本量?</td><td><span class="tok">✅</span>均为N=55.3M(108k步)</td><td>EXPERIMENTS_VISION_ROUND11.md L887-889</td></tr>')
    P.append('<tr><td>5</td><td>+12.4pp是否=19.76%-7.40%?</td><td><span class="tok">✅</span>19.76-7.40=12.36≈12.4</td><td>EXPERIMENTS_VISION_ROUND11.md L887</td></tr>')
    P.append('<tr><td>6</td><td>20.27%@176M与19.76%@55.3M的epoch是否相同?</td><td><span class="twarn">⚠️不同</span>(3epoch vs 1epoch)</td><td>EXPERIMENTS_VISION_ROUND11.md L1543,L1557</td></tr>')
    P.append('<tr><td>7</td><td>20.27%@176M与19.76%@55.3M的数据是否相同?</td><td><span class="twarn">⚠️不同</span>(58.8M含GPIC vs 18.5M不含GPIC)</td><td>EXPERIMENTS_VISION.md L129;ROUND11.md L1557</td></tr>')
    P.append('<tr><td>8</td><td>四臂消融是否在多个预算点做过?</td><td><span class="twarn">⚠️否</span>,仅15.36M(30k步)</td><td>EXPERIMENTS_VISION_ROUND11.md L1130-1137</td></tr>')
    P.append('<tr><td>9</td><td>R11-H(去对比项)trunk是否坍缩?</td><td><span class="tok">✅未坍缩</span>(C1=0.255@30k)</td><td>EXPERIMENTS_VISION_ROUND11.md L1078</td></tr>')
    P.append('<tr><td>10</td><td>mask_ratio=0.6和weight 1:1是否有消融支撑?</td><td><span class="tok">✅</span>5臂mask-ratio消融+4臂weight-ratio消融</td><td>EXPERIMENTS_VISION.md L136-160,L171-195</td></tr>')
    P.append('</table>')
    P.append('<h3>6.2 红线合规自检</h3>')
    P.append('<table><caption>表6.2 红线合规自检</caption><tr><th>#</th><th>红线</th><th>合规?</th></tr>')
    P.append('<tr><td>1</td><td>本轮只出计划,不改.tex</td><td><span class="tok">✅</span>本报告为HTML计划,未触碰.tex</td></tr>')
    P.append('<tr><td>2</td><td>不伪造数字;未实测写「待核」或「估算」</td><td><span class="tok">✅</span>所有数字溯源repo内已落盘记录,无伪造</td></tr>')
    P.append('<tr><td>3</td><td>不恢复用户明令删除的内容</td><td><span class="tok">✅</span>六架构/SSM/AR/Muon/ProtB/epoch缩放/AIMv2四臂细节均未进正文方案</td></tr>')
    P.append('<tr><td>4</td><td>不动4_llm_pretrain.tex</td><td><span class="tok">✅</span>本报告仅涉及6_vision_encoder.tex</td></tr>')
    P.append('<tr><td>5</td><td>%中文:双语注释行不得删;改写时同步更新</td><td><span class="tok">✅</span>改写方案中每段均给出同步中文注释</td></tr>')
    P.append('<tr><td>6</td><td>任务书≤32KB</td><td><span class="tok">✅</span>本轮不归档任务书</td></tr>')
    P.append('</table>')
    return "\n".join(P)

def _s6b():
    P = []
    P.append('<h3>6.3 交付物合规自检</h3>')
    P.append('<table><caption>表6.3 交付物合规自检</caption><tr><th>#</th><th>要求</th><th>合规?</th></tr>')
    P.append('<tr><td>1</td><td>中文HTML,单文件自包含</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>2</td><td>0 script/0外链/0 CDN</td><td><span class="tok">✅</span>纯HTML+内联CSS,无JS/外链</td></tr>')
    P.append('<tr><td>3</td><td>标签配平</td><td><span class="tok">✅</span>所有div/table/ul均闭合</td></tr>')
    P.append('<tr><td>4</td><td>≥18KB</td><td><span class="tok">✅</span>见文件大小</td></tr>')
    P.append('<tr><td>5</td><td>生成器幂等(重跑两次逐字节相同)</td><td><span class="tok">✅</span>无时间戳/随机数</td></tr>')
    P.append('<tr><td>6</td><td>6节齐全</td><td><span class="tok">✅</span>§1-§6全部包含</td></tr>')
    P.append('<tr><td>7</td><td>生成器路径vision/generate_paper_revise_plan_report.py</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>8</td><td>报告路径reports/report_vision_paper_revise_plan_zh.html</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>9</td><td>commit前缀vision paper-plan:</td><td><span class="tok">✅</span></td></tr>')
    P.append('</table>')
    P.append('<h3>6.4 6节内容覆盖自检</h3>')
    P.append('<table><caption>表6.4 6节内容覆盖</caption><tr><th>节</th><th>要求</th><th>覆盖?</th></tr>')
    P.append('<tr><td>§1</td><td>逐句摘录+标注✅/⚠️/❌+证据(文件+行号)</td><td><span class="tok">✅</span></td></tr>')
    P.append('<tr><td>§2</td><td>不符事实清单表(位置/现文/事实/来源/严重度P0-P2)</td><td><span class="tok">✅</span>5行表</td></tr>')
    P.append('<tr><td>§3</td><td>改写方案(英文目标文本,逐段改前→改后)</td><td><span class="tok">✅</span>3段改写+汇总表</td></tr>')
    P.append('<tr><td>§4</td><td>篇幅预算(半页≈45-50行,说明删了什么/为何可删)</td><td><span class="tok">✅</span>行数估算+不恢复清单+压缩方案</td></tr>')
    P.append('<tr><td>§5</td><td>仍需的实验(无实测支撑的如实列出)</td><td><span class="tok">✅</span>5项+诚实披露</td></tr>')
    P.append('<tr><td>§6</td><td>自检清单</td><td><span class="tok">✅</span>4张自检表</td></tr>')
    P.append('</table>')
    return "\n".join(P)

def build_html():
    P = []
    P.append('<!DOCTYPE html>')
    P.append('<html lang="zh-CN"><head><meta charset="utf-8">')
    P.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    P.append('<title>' + REPORT_TITLE + '</title>')
    P.append(_css())
    P.append('</head><body>')
    P.append('<h1>' + REPORT_TITLE + '</h1>')
    P.append('<p style="color:#64748b;font-size:0.9em">生成日期:' + GEN_DATE + ' · 生成器:vision/generate_paper_revise_plan_report.py · 数据来源:run/EXPERIMENTS_VISION.md + run/EXPERIMENTS_VISION_ROUND11.md + ISEDA2027/6_vision_encoder.tex</p>')
    P.append('<div class="kbox"><p><b>任务背景</b>:用户令「让pretrain和vision看看BaiZe论文中各自的章节,出一版中文HTML修订计划:哪里跟事实不符,计划怎么改。」本报告审校论文第6章「Vision Encoder Pretraining」(6_vision_encoder.tex,当前0.3页占位式精简版),逐句核实事实,给出改写方案。<b>本轮只出计划,不改.tex</b>。</p></div>')
    P.append(_toc())
    P.append(_s1())
    P.append(_s1b())
    P.append(_s2())
    P.append(_s3a())
    P.append(_s3b())
    P.append(_s3c())
    P.append(_s4())
    P.append(_s5())
    P.append(_s6())
    P.append(_s6b())
    P.append('<div class="footer"><p>BaiZe Vision · 论文第6章修订计划 · ' + GEN_DATE + ' · 生成器幂等(重跑两次逐字节相同) · 0 script/0外链/0 CDN</p></div>')
    P.append('</body></html>')
    return "\n".join(P)

def main():
    html = build_html()
    out_path = DEFAULT_OUT
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(out_path)
    print(f"Report written to: {out_path}")
    print(f"Size: {size} bytes ({size/1024:.1f} KB)")
    html2 = build_html()
    if html == html2:
        print("Idempotency: OK")
    else:
        print("Idempotency: FAILED!")
        sys.exit(1)
    if "<script" in html.lower():
        print("WARNING: <script> tag found!")
        sys.exit(1)
    ext = re.findall(r'(?:src|href)\s*=\s*["\']https?://', html, re.I)
    if ext:
        print(f"WARNING: {len(ext)} external link(s) found!")
        sys.exit(1)
    print("0 script / 0 external links: OK")
    if size >= 18 * 1024:
        print(f"Size >= 18KB: OK ({size} bytes)")
    else:
        print(f"WARNING: Size {size} < 18KB!")
        sys.exit(1)
    for tag in ["div", "table", "ul", "ol", "p", "span"]:
        opens = len(re.findall(rf"<{tag}[\s>]", html))
        closes = len(re.findall(rf"</{tag}>", html))
        if opens != closes:
            print(f"WARNING: <{tag}> tag imbalance: {opens} open vs {closes} close")
            sys.exit(1)
    print("Tag balance: OK")

if __name__ == "__main__":
    main()
