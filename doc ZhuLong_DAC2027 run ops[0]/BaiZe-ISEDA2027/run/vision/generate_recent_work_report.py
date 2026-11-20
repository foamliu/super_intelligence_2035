#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_recent_work_report.py — BaiZe vision 线「最近工作报告」生成器.

运维令 2026-10-26 08:2x（用户直令「关于最近的工作，安排 BaiZe 4 个 agent 各自写一份报告」）。
产出：reports/report_vision_recent_work_zh.html（中文自包含 HTML）。

约定：0 <script> / 0 外链(href="http) / 0 外链图片 / 标签配平 / ≥15KB。
所有数字均实测可溯源，引用格式为「文件:行」或「文件 §小节」；估算标注「估算」。
覆盖窗：2026-10-20 起（ArmD-R2 → ArmE 发散 → ArmE-R2 修复 → Stage-2 原版 780k → OCR 调研/SFT 方案/10M 合成）。
"""
from __future__ import annotations
import os, sys

REPORTS_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
OUT_NAME = "report_vision_recent_work_zh.html"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def self_check(html):
    issues = []
    n_script = html.count("<script")
    n_ext = html.count('href="http')
    if n_script != 0:
        issues.append(f"<script> 出现 {n_script} 次")
    if n_ext != 0:
        issues.append(f'外链 href="http 出现 {n_ext} 次')
    n_imgext = html.count('src="http')
    if n_imgext != 0:
        issues.append(f'外链图片 src="http 出现 {n_imgext} 次')
    for tag in ["html", "head", "body", "table", "div", "section", "article"]:
        o = html.count(f"<{tag}"); c = html.count(f"</{tag}>")
        if o != c:
            issues.append(f"<{tag}> 开/闭不配平 {o}/{c}")
    size = len(html.encode("utf-8"))
    if size < 15000:
        issues.append(f"体积 {size}B < 15KB")
    return issues, size


CSS = """
*{box-sizing:border-box}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif;
  max-width:1080px;margin:0 auto;padding:24px 28px 80px;color:#1f2328;line-height:1.7;
  background:#fafbfc}
h1{font-size:1.7em;border-bottom:2px solid #2563eb;padding-bottom:.3em;margin:.2em 0 .6em}
h2{font-size:1.32em;color:#1d4ed8;margin-top:1.8em;border-left:5px solid #2563eb;padding-left:.6em}
h3{font-size:1.08em;color:#334155;margin-top:1.4em}
h4{font-size:1.0em;color:#475569;margin:1em 0 .3em}
.meta{color:#64748b;font-size:.88em;margin-bottom:1.2em}
.tag{display:inline-block;font-size:.78em;padding:.05em .5em;border-radius:.4em;
  background:#e0e7ff;color:#3730a3;margin-right:.3em;vertical-align:middle}
.tag.ok{background:#dcfce7;color:#166534}
.tag.warn{background:#fef9c3;color:#854d0e}
.tag.bad{background:#fee2e2;color:#991b1b}
.tag.win{background:#fde68a;color:#7c2d12;font-weight:600}
table{border-collapse:collapse;width:100%;margin:.8em 0;font-size:.9em}
th,td{border:1px solid #cbd5e1;padding:.4em .6em;text-align:left;vertical-align:top}
th{background:#f1f5f9;font-weight:600}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr:hover{background:#f8fafc}
caption{caption-side:top;text-align:left;color:#64748b;font-size:.85em;padding-bottom:.3em}
code,.src{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.86em;
  background:#f1f5f9;padding:.05em .35em;border-radius:.3em;color:#334155}
.src{display:inline-block;color:#64748b;background:transparent;font-size:.8em}
.note{background:#eff6ff;border-left:4px solid #3b82f6;padding:.6em .9em;margin:.8em 0;border-radius:.3em}
.warn{background:#fffbeb;border-left:4px solid #f59e0b;padding:.6em .9em;margin:.8em 0;border-radius:.3em}
.bad{background:#fef2f2;border-left:4px solid #ef4444;padding:.6em .9em;margin:.8em 0;border-radius:.3em}
.win{background:#ecfdf5;border-left:4px solid #10b981;padding:.6em .9em;margin:.8em 0;border-radius:.3em}
ul{margin:.4em 0 .8em}
li{margin:.18em 0}
.small{font-size:.84em;color:#64748b}
.toc{background:#f8fafc;border:1px solid #e2e8f0;border-radius:.5em;padding:.6em 1.1em;margin:.4em 0 1.4em;font-size:.92em}
.toc a{color:#2563eb;text-decoration:none}
.kbd{font-family:ui-monospace,monospace;background:#e2e8f0;border-radius:.3em;padding:.05em .4em;font-size:.85em}
hr{border:0;border-top:1px solid #e2e8f0;margin:1.6em 0}
.foot{color:#64748b;font-size:.82em;margin-top:2em;border-top:1px solid #e2e8f0;padding-top:.8em}
"""

def section_header():
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BaiZe 视觉编码器线 · 最近工作报告（2026-10-20 起）</title>
<style>{CSS}</style>
</head>
<body>
<article>
<h1>BaiZe 视觉编码器线 · 最近工作报告</h1>
<div class="meta">
报告线：<span class="tag">vision</span> · 覆盖窗：<b>2026-10-20 → 2026-10-26</b> ·
生成：<span class="src">vision/generate_recent_work_report.py</span> ·
报告：<span class="src">reports/report_vision_recent_work_zh.html</span> ·
生成于 2026-10-26
</div>
<div class="note">
<b>诚实条款（先读）</b>：本报告全部数字为<b>本项目实测</b>，引用格式为「文件:行」或「文件 §小节」，可逐项溯源。
凡涉及外部论文/榜单的数字均明确标注「论文自报，未在本项目复现」；成本/ETA 标注「估算」。
内部 ProtB/MLLM 口径非官方榜；MLLM 三阶段单 seed；评测为 224px 单块（无 anyres），细粒度任务天然偏低。
</div>
"""


def toc():
    return f"""<div class="toc">
<b>目录</b><br>
1. 本线定位<br>
2. 本窗口完成任务（2026-10-20 起：ArmD-R2 / ArmE 发散 / ArmE-R2 / Stage-2 修复 / OCR 调研·SFT·10M 数据集）<br>
3. 关键数据速查表<br>
4. 阻塞 / 待拍板<br>
5. 下一步建议
</div>"""


def sec1_position():
    return f"""
<h2>1. 本线定位</h2>
<p>
BaiZe 视觉编码器线（vision）负责<b>多模态大模型（MLLM）的视觉塔预训练与对齐评测</b>。目标是用
<b>open_clip 双塔 + AIMv2-style dense objective</b>（InfoNCE 1.0 + masked-patch-MSE 1.0，mask-ratio 0.6，双向注意力）
自研训练视觉编码器，再经 <b>ProtB 线性探针</b>（IN-1k 1.28M train / 50k val，SGD 90 epochs，3 seeds）量化编码器表征质量，
经 <b>MLLM 三阶段对齐</b>（Stage-1 projector → Stage-1.5 LoRA → Stage-2 instruct）+ <b>12 集 lmms-eval</b> 量化下游能力。
最佳实践（BP-1/BP-2/BP-3）见 <span class="src">BAIZE_VISION_TASK.md §最佳实践</span>。
</p>
<p>
<b>最近窗口（2026-10-20 起）的核心主线</b>：把视觉塔从 <b>ViT-B/16（86.2M）</b>升级到 <b>ViT-L/14（304M）</b>，
过程中遭遇 LR 过大导致的<b>训练发散</b>，通过「降 LR + 加长 warmup」修复（ArmE → ArmE-R2）；
同时把 Stage-2 instruct 数据从被删的 opt47 回退到<b>原版 LLaVA-NeXT-780k</b>；
并针对 OCR 类评测偏低的瓶颈，完成「调研报告 → SFT 方案报告 → 10M 合成 OCR 图文对数据集」三步推进。
</p>
<div class="note">
<b>本线与其它三线的关系</b>：vision 与 pretrain / data / harness 三线共用同一 NFS 工作副本
（<span class="src">/nas_train/app.e0031982/code/super_intelligence_2035</span>）；
训练在 <span class="src">10.239.2.12</span>（vision 专属 GPU），重 I/O 须避让 <span class="src">10.239.2.29</span> 上的 pretrain 训练。
本报告只覆盖 vision 线产物，不涉及他线。
</div>
"""

def sec2_tasks_a():
    return f"""
<h3>2.1 ArmD-R2（ViT-B/16，LR 1e-3，6 源数据，3 epoch）· ✅ 全链路 DONE 2026-10-21</h3>
<p>
<b>背景</b>：ArmD 首轮（LR 2e-3）于 step~21820 发散（loss 0.45→9.3，C1 0.589→0.0002），
wake#180 停止保全 ckpt_10000，7 个发散产物留档于
<span class="src">datasets/baize-vision/out/armD_20261019_DIVERGED_archive/</span>
（<span class="src">EXPERIMENTS_VISION.md §14.1:1572</span>）。
用户令（2026-10-20 08:2x）「<b>ArmD 放弃重启。LR=1e-3 min_LR=1e-5。数据保持不变</b>」⇒ ArmD-R2 重起，
输出新目录 <span class="src">armD_r2_20261020_aimv2_openclip_vitb16_224/</span>（杜绝误 resume 发散 ckpt）。
</p>
<p>
<b>变量披露</b>（<span class="src">EXPERIMENTS_VISION.md §14.1:1574</span>）：相对 ArmC，ArmD-R2 的 LR 轴整体回退到 ArmC 档
（LR 2e-3→1e-3、min_lr 2e-5→1e-5，同步变动，<b>不得归因单一 LR 变量</b>）；与 ArmC 的差异仅剩两项 ——
① 预训练数据 3 源→6 源（GPIC 8000 + CC12M 1100 + Amshaker 2250 + WebMix 3886 parquet + wit_base 330 parquet + InternVL 2000 = 14,589 shards / 173,124,248 pairs）；
② epoch 4→3（步数 57,250 → 63,400）。其余（ViT-B/16 224、AIMv2-style、wd 0.01、GBS 8192/MBS 512/accum 2、warmup 2000、cosine、seed 1234、save 10k/keep 2、bf16）全部与 ArmC 相同。
</p>
<p>
<b>训练</b>（<span class="src">§14.2:1578</span>）：T0 10-20 09:20:34 → 完成 10-21 10:02:49，总耗时 ~24.7h，稳态 0.71–0.75 it/s，63,400 步全程 0 nan/inf/oom。
全局 JOINT best = step 43,700：loss 0.1360 / C1 0.8902（全 log awk 确认）；末段硬分片抖动（s58000–63400 loss 0.14–1.07、C1 0.29–0.89），同 ArmC/ArmB 模式非发散。
LR 减半后越过首轮发散点（s16000）<b>零发散</b>，且更早达同等/better 水平（s11160 C1 0.6684 已超上轮 best s15860 C1 0.589）。
</p>
<p>
<b>ProtB</b>（<span class="src">§14.3:1588</span>，<span class="src">vision/armD_r2_20261020_protb_vitb16_224_results.json</span>）：
lp 64.3339 / 64.3360 / 64.3420（seeds 0/1/2）→ <b>lp 64.3373 ± 0.0034%</b> / <b>5-NN 55.956%</b>。
vs ArmC Δlp <b>+2.005pp</b> / Δ5-NN <b>+1.238pp</b>，双双正向 → 编码器质量核心结论 secured。
</p>
<p>
<b>MLLM 三阶段 + 12 集</b>：Stage-2 instruct 首跑因 opt47 数据被 NFS 删除而 FAILED（详见 §2.3），
改用原版 LLaVA-NeXT-780k RE-LAUNCH @ 17:41 → DONE 18:01:45（<span class="src">§14.4:1604</span>）；
12 集 lmms-eval ✅ DONE 18:42:35（12/12 exit 0）。
12 集平均（除 MME）= <b>26.12%</b>（<span class="src">§14.6:1636</span>），vs ArmC +0.34pp / vs ArmB +0.02pp →
<b>不可分辨（边界值）</b>（预注册带 22–26.5%）。
</p>
<div class="warn">
<b>两变量 + 数据版本披露</b>（<span class="src">§14.6:1632</span>）：ArmD-R2 vs ArmC 的 ④Δ 含 data(3→6源)+epoch(4→3) 两变量 +
Stage-2 数据版本（原版 quick-start vs opt47）三重混杂，<b>不是纯编码器对照</b>；编码器纯对照看 ②ProtB（Δlp+2.005pp / Δ5-NN+1.238pp，双双正向，已 secured）。
<b>ProtB→MLLM 传递性再次证伪</b>（<span class="src">§14.6:1640</span>）：ArmD-R2 ProtB lp(64.34%) 显著高于 ArmC(+2.0pp)/ArmB(+2.24pp)，但 MLLM 12 集平均几乎持平（+0.34/+0.02pp）→ 编码器 2pp 的 ProtB 优势未转化为 MLLM 下游优势。
</div>

<h3>2.2 ArmE 发散（ViT-L/14，LR 1e-3）· ❌ step~29200 发散，留档</h3>
<p>
<b>动机</b>：把视觉塔从 ViT-B/16（86.2M）升级到 ViT-L/14（304M，~3.5×），看容量红利能否落到编码器与下游。
</p>
<p>
<b>结果</b>（<span class="src">§15.1:1661</span>）：ArmE（原 LR 1e-3）于 <b>step~29200 发散</b>（C1=0.0014 ≈ 随机水平）。
<b>根因</b> = ViT-L/14（304M）比 ViT-B/16（86M）大 3.5× 却沿用 LR 1e-3，更新幅度过大 → spike 反复、C1 恢复慢。
发散证据留档于 <span class="src">datasets/baize-vision/out/armE_20261021_DIVERGED_archive/</span>（不删除）。
</p>
<div class="bad">
<b>教训</b>：大塔（L/14）不能照搬小塔（B/16）的 LR。这是本窗口最重要的一次「失败留档」——
它直接催生了 ArmE-R2 的「降 LR + 加长 warmup」修复，并固化为后续大塔训练的默认起点。
</div>

<h3>2.3 Stage-2 instruct 改用原版 LLaVA-NeXT-780k · 🔧 2026-10-21 修复</h3>
<p>
<b>事件</b>（<span class="src">§14.4:1604-1605</span>）：ArmD-R2 Stage-2 instruct 首跑 FAILED @ 13:32。
<b>根因</b>：opt47 数据 <span class="src">LLaVA-NeXT-780k-plus-Instruct-opt47-webdataset</span> 被 NFS 删除
（<span class="kbd">glob('data-*.tar')</span> 空 → 0 样本 → StopIteration）。
</p>
<p>
<b>修复</b>（运维令 2026-10-21「让 vision 使用原版」）：脚本 <span class="src">stage2_train_armD_r2.py</span> 两处改
<code>DATA_DIR → LLaVA-NeXT-780k-webdataset</code>、glob <code>data-*.tar → pretrain-*.tar</code>
（原版 quick-start 子集，78 tar / <b>738,588 样本</b>，含真实 instruct：
<code>texts:[&#123;role:user,content:&lt;image&gt;+多选QA&#125;,&#123;role:assistant&#125;]</code>，与 <code>LLaVANeXTInstructDataset</code> 兼容）。
RE-LAUNCH @ 17:41 → DONE 18:01:45（~20 min，3.39 steps/s，loss 4.7107@step50 → 1.5580@step3500，lr 衰减到 min_lr 1e-7，GPU 18MB，ckpt step500~3500 全在）。
独立复核 78 tar 全索引：779111 json / 738590 img / 0 bad。
</p>
<p>
<b>沿用</b>：ArmE-R2 同样使用原版 LLaVA-NeXT-780k quick-start 子集（<span class="src">§15.1:1667</span>），
Stage-2 3500 步 ✅ DONE ~09:50（loss 4.71→1.56，~15min）。
</p>
<div class="warn">
<b>数据版本披露</b>：ArmD-R2 / ArmE-R2 的 Stage-2 用原版 quick-start 子集（非 ArmB/ArmC 的 opt47）→
④12集 Δ 含「视觉塔 + Stage-2 数据」两重混杂，<b>不是纯编码器对照</b>；编码器 ProtB 结论不受影响。
</div>
"""

def sec2_tasks_b():
    return f"""
<h3>2.4 ArmE-R2（ViT-L/14，LR 5e-4，warmup 3000）· ✅ 全链路 DONE 2026-10-24 · 🏆 编码器历史最高</h3>
<p>
<b>修复设计</b>（<span class="src">§15.1:1664</span>）：ArmE-R2 = ArmE 降 LR 重跑。
<b>ArmE-R2 vs ArmE = 仅两变量</b>：peak LR 1e-3→<b>5e-4</b> + warmup 2000→<b>3000</b>
（塔/数据/GBS/steps/loss/mask/wd/seed 全同）→ 干净对照「降 LR+warmup 是否消除 spike」。
<b>ArmE-R2 vs ArmD-R2 = 三变量</b>：① 视觉塔 B/16(86.2M)→L/14(304M) ② LR 1e-3→5e-4 ③ warmup 2000→3000
→ <b>报告中不得归因单一变量</b>。MBS 512→256 是 ViT-L/14 显存约束的强制回退（GBS=8192 + steps=63400 保持，非消融变量）。
</p>
<p>
<b>训练</b>（<span class="src">§15.2:1675</span>）：T0 10-22 17:52 → DONE 10-24 06:57:43，总耗时 ~37h，稳态 0.48 it/s，63,400 步全程 0 nan/inf/oom。
最终 step 63,400：loss ~0.66 / C1~0.80 / lr 1.00e-05（=min_lr）。
</p>
<div class="win">
<b>spike 底连续趋浅证据 + 历史最高 C1</b>（<span class="src">§15.2:1677-1679</span>）：
⭐ <b>C1 历史最高 = 0.9664 @ s45240</b>（全 log awk 确认，全实验最高）。spike25 全闭合，末段 C1~0.80 振荡（同 ArmD-R2 末段抖动模式，非发散）。
vs ArmE 强优：ArmE s29200 C1=0.0014≈发散；ArmE-R2 在同一点 C1~0.86 = <b>690×于 ArmE 发散点</b>。
里程碑（C1 单调爬升）：s2k C1~0.09 → s11k C1~0.67 → s22k C1~0.79 → s33k C1~0.86 → ⭐s45k C1 0.9664(best) → s63k C1~0.80(末段)。
</div>
<p>
<b>config.json 复核</b>（<span class="src">§15.2:1680</span>）：lr=5e-4 / min_lr=1e-5 / wd=0.01 / seed=1234 / mask_ratio=0.6 /
contrast=1.0 / patch=1.0 / n_visual=304,000,000(304M) / warmup=3000 全对。
产物：<span class="src">armE_r2_20261022_aimv2_openclip_vitl14_224/</span>（checkpoint_60000.pt + checkpoint_63400.pt + latest.pt + open_clip_state_dict.pt(1.7GB) + predictor.pt(6.6MB) + config.json）。
</p>
<p>
<b>ProtB</b>（<span class="src">§15.3:1686</span>，<span class="src">vision/armE_r2_20261022_protb_vitl14_224_results.json:13-20</span>）：
lp 68.21199655532837 / 68.25599670410156 / 68.23999881744385（seeds 0/1/2）→ <b>lp 68.236 ± 0.0182%</b> / <b>5-NN 58.904%</b> = 🏆 全实验历史最高。
</p>
<table>
<caption>ProtB 对比（同 Protocol B、同 IN-1k 1.28M train / 50k val）· <span class="src">§15.3:1690-1693</span></caption>
<tr><th>指标</th><th class="num">ArmE-R2</th><th class="num">ArmD-R2</th><th class="num">ArmC</th><th class="num">ArmB</th><th class="num">Δ(vs D-R2)</th><th class="num">Δ(vs C)</th><th class="num">Δ(vs B)</th></tr>
<tr><td>ProtB lp (%)</td><td class="num"><b>68.236</b> 🏆</td><td class="num">64.337</td><td class="num">62.332</td><td class="num">62.093</td><td class="num"><b>+3.899</b></td><td class="num">+5.904</td><td class="num">+6.143</td></tr>
<tr><td>5-NN (%)</td><td class="num"><b>58.904</b> 🏆</td><td class="num">55.956</td><td class="num">54.718</td><td class="num">58.102</td><td class="num"><b>+2.948</b></td><td class="num">+4.186</td><td class="num">+0.802</td></tr>
</table>
<div class="warn">
<b>三变量 + 容量混杂</b>（<span class="src">§15.3:1695</span>）：ArmE-R2 vs ArmD-R2 的 Δlp=+3.899pp / Δ5-NN=+2.948pp 是
<b>塔(B→L, 86→304M) + LR(1e-3→5e-4) + warmup(2000→3000) 三项共同作用</b>，<b>不得归因单一变量</b>；
容量增大 3.5× 是主要混杂因子。核心结论：ViT-L/14 + 降 LR 双因子使线性可分性与近邻检索均大幅改善，全实验历史最高。
</div>
<p>
<b>MLLM 三阶段</b>（<span class="src">§15.4:1699-1704</span>）：复用 ArmD-R2 三阶段脚本，projector 1024→2560（ViT-L/14 输出 256 patch tokens）。
🔧 <b>eval bridge 修复</b>：<span class="src">lmms_eval_baize_llava.py</span> 原硬编码 <code>NUM_IMAGE_TOKENS=196</code>（ViT-B/16），
ViT-L/14 产出 <b>256</b> patch tokens → 8 GPU eval 全崩。修 3 处：
<code>self.num_image_tokens = 256 if vision_backend in ("armE","armE_r2") else 196</code> + <code>_expand_image_tokens</code> + feature buffer。
冒烟 <code>ai2d --limit 32</code> 确认 <code>[inject] img_mask sum=256</code> ✅。
</p>
"""

def sec2_tasks_c():
    return f"""
<p>
<b>12 集 lmms-eval</b>（<span class="src">§15.5:1707-1726</span>，<span class="src">mllm_eval_results_armE_r2_20261022/consolidated_12benchmarks.json</span>）：
Stage-2 step3500，每卡一个 benchmark（batch_size=32，8 卡并行，无 limit，全量），12/12 ✅ DONE 10:05:44。
</p>
<table>
<caption>12 集 ArmE-R2 vs ArmD-R2（主对照）vs ArmC vs ArmB · <span class="src">§15.5:1713-1726</span></caption>
<tr><th>集</th><th class="num">ArmE-R2</th><th class="num">ArmD-R2</th><th class="num">Δ(−D-R2)</th><th class="num">ArmC</th><th class="num">Δ(−C)</th><th class="num">ArmB</th><th class="num">Δ(−B)</th></tr>
<tr><td>ai2d</td><td class="num">60.65</td><td class="num">60.49</td><td class="num">+0.16</td><td class="num">59.03</td><td class="num">+1.62</td><td class="num">60.69</td><td class="num">−0.04</td></tr>
<tr><td>realworldqa</td><td class="num">45.36</td><td class="num">46.41</td><td class="num">−1.05</td><td class="num">44.97</td><td class="num">+0.39</td><td class="num">45.49</td><td class="num">−0.13</td></tr>
<tr><td>mmmu_val</td><td class="num">44.00</td><td class="num">42.67</td><td class="num">+1.33</td><td class="num">42.56</td><td class="num">+1.44</td><td class="num">43.67</td><td class="num">+0.33</td></tr>
<tr><td>blink</td><td class="num">38.88</td><td class="num">39.59</td><td class="num">−0.71</td><td class="num">38.15</td><td class="num">+0.73</td><td class="num">38.94</td><td class="num">−0.06</td></tr>
<tr><td>mmstar</td><td class="num">27.17</td><td class="num">27.07</td><td class="num">+0.10</td><td class="num">28.38</td><td class="num">−1.21</td><td class="num">27.95</td><td class="num">−0.78</td></tr>
<tr><td>mmmu_pro_standard</td><td class="num">23.12</td><td class="num">22.60</td><td class="num">+0.52</td><td class="num">22.60</td><td class="num">+0.52</td><td class="num">22.43</td><td class="num">+0.69</td></tr>
<tr><td>infovqa_val</td><td class="num">16.18</td><td class="num">16.59</td><td class="num">−0.41</td><td class="num">17.09</td><td class="num">−0.91</td><td class="num">16.88</td><td class="num">−0.70</td></tr>
<tr><td>chartqa</td><td class="num">12.16</td><td class="num">12.92</td><td class="num">−0.76</td><td class="num">12.48</td><td class="num">−0.32</td><td class="num">12.52</td><td class="num">−0.36</td></tr>
<tr><td>countbench</td><td class="num">10.59</td><td class="num">9.98</td><td class="num">+0.61</td><td class="num">8.96</td><td class="num">+1.63</td><td class="num">9.57</td><td class="num">+1.02</td></tr>
<tr><td>docvqa_val</td><td class="num">7.35</td><td class="num">7.44</td><td class="num">−0.09</td><td class="num">7.58</td><td class="num">−0.23</td><td class="num">7.36</td><td class="num">−0.01</td></tr>
<tr><td>ocrbench</td><td class="num">1.60</td><td class="num">1.60</td><td class="num">+0.00</td><td class="num">1.80</td><td class="num">−0.20</td><td class="num">1.60</td><td class="num">+0.00</td></tr>
<tr><td><b>平均(除MME)</b></td><td class="num"><b>26.10</b></td><td class="num"><b>26.12</b></td><td class="num"><b>−0.02</b></td><td class="num"><b>25.78</b></td><td class="num"><b>+0.32</b></td><td class="num"><b>26.10</b></td><td class="num"><b>−0.00</b></td></tr>
</table>
<div class="note">
<b>结论 4 条</b>（<span class="src">§15.6:1732-1735</span>）：
<b>① 编码器（最可靠，ProtB）</b>：ArmE-R2 ProtB lp 68.236% / 5-NN 58.904% = 🏆全实验历史最高，vs ArmD-R2 Δlp +3.899pp / Δ5-NN +2.948pp。
<b>② MLLM 下游</b>：ArmE-R2 12 集平均 26.10%，vs ArmD-R2 −0.02pp / vs ArmC +0.32pp / vs ArmB −0.00pp → <b>不可分辨（边界值）</b>；
ViT-L/14(304M) 比 ViT-B/16(86M) 大 3.5×，MLLM 下游却完全持平 → <b>容量不是 MLLM 下游瓶颈</b>（在 224px 单块 + 当前 MLLM 架构下）。
<b>③ ProtB→MLLM 传递性再次证伪（最强烈一例）</b>：ArmE-R2 ProtB lp(68.24%) 比 ArmD-R2(64.34%) 高 +3.9pp、比 ArmC(62.33%) 高 +5.9pp，
但 MLLM 12 集平均几乎持平（−0.02/+0.32pp）→ <b>编码器 4-6pp 的 ProtB 优势完全未转化为 MLLM 下游优势</b>。这是所有实验中 ProtB 差距最大而 MLLM 持平最明确的一例。
<b>④ 降 LR 效果（两变量干净对照）</b>：ArmE(LR 1e-3) s29200 发散(C1=0.0014)；ArmE-R2(LR 5e-4) 全程稳定，C1 最高 0.9664 →
降 LR(1e-3→5e-4)+warmup(2000→3000) 成功消除 ViT-L/14 的 spike 反复与发散。
</div>
<p class="small">
<b>补：A3 ckpt_60000 ProtB 复测</b>（<span class="src">§15.8:1754</span>，wake#266）：检验「换 best-段 ckpt 能否省回 1–2pp」假设。
复测早 3400 步的 ckpt_60000（同 ProtB、同 Protocol B、同 3 seeds），结果 <b>假设证伪</b> —— 末段抖动未损害 s63400 的 ProtB 表现，
ckpt_60000 未带来 1–2pp 增益。s63400 = open_clip_state_dict.pt 仍是该实验的最佳 ProtB ckpt。
</p>
"""

def sec2_tasks_d():
    return f"""
<h3>2.5 OCR 类评测偏低 → 合成数据补强调研报告 · ✅ 2026-10-25 wake#271</h3>
<p>
<b>起因</b>：四臂 12 集评测中 OCR 相关四集（OCRBench / DocVQA / ChartQA / InfoVQA）显著偏低
（ArmE-R2：OCRBench 1.60% / DocVQA 7.35% / ChartQA 12.16% / InfoVQA 16.18%，见 §3 速查表）。
用户令（2026-10-25 17:5x）「vision：现在 OCR 类评测很低，web search 调研一下合成数据补强这块能力的方法，写报告。」
</p>
<p>
<b>交付</b>（<span class="src">§16:1779</span>）：报告 <span class="src">reports/report_vision_ocr_synthdata_zh.html</span>（29177 B / 8 节 / 0 &lt;script&gt; / 0 外链 / 标签配平）+ 生成器 <span class="src">vision/generate_ocr_synthdata_report.py</span>。
调研覆盖 7 类 18 法（SynthTIGER / SynthText / trdg / SynthDoG / UDOP / Pix2Struct / Nougat / mPLUG-DocOwl / dots.ocr / ChartQA / Chart-to-Text / olmOCR / PaddleOCR / Visual-RFT / 自训练 / im2latex），
每条按 5 项（怎么造 / 要什么输入 / 论文报告的效果 / 接入点 / 成本）写；外部效果数字均标「论文自报，未在本项目复现」。
</p>
<p>
<b>结论</b>：给出三条候选接入路线，单一下一步 = <b>路线①低成本合成 OCR 识别对 + 在现有 ckpt 上专项 SFT</b>，判据 OCRBench ≥ +2pp。
</p>

<h3>2.6 路线①细化 · OCR 专项 SFT 执行方案报告 · ✅ 2026-10-25 wake#272</h3>
<p>
<b>用户令</b>（2026-10-25 19:5x）：把路线①细化为可执行方案 ——「中英文什么比例、数学公式怎么办、其他呢」。
</p>
<p>
<b>交付</b>（<span class="src">§17:1810-1831</span>）：报告 <span class="src">reports/report_vision_ocr_sft_plan_zh.html</span>（22706 B / 9 节 + 附录一页纸执行清单 / 0 &lt;script&gt; / 0 外链 / 标签配平 / ≥18KB）+ 生成器 <span class="src">vision/generate_ocr_sft_plan_report.py</span>。
</p>
<ul>
<li><b>配比</b>：基线 英30 / 中20 / 混10 / 版面15 / 图表10 / 公式10 / 低质5；候选 A（英6:中3:混1，默认）/ B（中英1:1，备选），各带可判定判据。</li>
<li><b>数学公式三通道</b>：(a) 纯公式图 im2latex/LaTeX 5% · (b) 正文夹公式 arXiv+KaTeX 3% · (c) 公式+表格混排 2%；总占 ≤10%。</li>
<li><b>SFT 口径</b>（对齐 <span class="src">stage2_train_armE_r2.py</span>）：ArmE-R2 Stage-2 step3500 起始 · LoRA r=64/alpha=128/dropout0.05 · LR 1e-5(lora)+5e-6(proj) · 224px 单块 · 256 tokens · vision 冻结 · 与 780k 混 70%OCR:30%780k 防遗忘。</li>
<li><b>预注册判据</b>：主 OCRBench ≥ +2pp（基线 1.60% → ≥3.60%）；副 DocVQA/ChartQA/InfoVQA 各 ≥ +1pp；回归护栏 MMStar/AI2D/RealWorldQA/MMBench 退化 ≤ 1pp；含决策树（pilot 达标→全量；不达→改一维再试；两次不达→停+负面结论）。</li>
<li><b>成本（估算）</b>：P0 pilot 渲染 ≈20 CPU·核·时 / 训练 ≈2 GPU·卡·时 / 当天内；P1 全量渲染 ≈150 CPU·核·时 / 训练 ≈12-18 GPU·卡·时 / 渲染一宿+训练 ~1 天。</li>
</ul>
<p class="small">本轮只出方案报告，未启训练、未生成全量数据（等用户看完批预算）。trdg 参数经代理检索 GitHub README 核实（2026-10-25）。</p>
"""

def sec2_tasks_e():
    return f"""
<h3>2.7 OCR 10M 合成图文对数据集 · ✅ 全量 DONE 2026-10-26 wake#275</h3>
<p>
<b>用户令</b>（2026-10-25 22:4x）：「vision：生成 10M OCR 数据试试，图文对，我后边把它用在 vision encoder 预训练里边。」
本轮 = 只造数据，不启 encoder 训练（等用户审阅后批预算）。
</p>
<p>
<b>数据本体</b>：<span class="src">/nas_train/app.e0031982/datasets/baize-vision/ocr_synth_10m_full/</span>
（WebDataset tar，每样本 <code>&lt;key&gt;.jpg</code> + <code>&lt;key&gt;.json</code>，
json 含 text/caption/caption_type='short'/lang/cat/w/h/font/src/id/sha1），可被 <span class="src">run/vision/data.py</span> 的
<code>build_gpic_loader</code> / <code>build_mixed_loader</code> 直接加载。
</p>
<table>
<caption>实测计数（STATS.json / VALIDATION.json，全部实测可溯源）· <span class="src">§18:1842-1851</span> · STATS.json 实读</caption>
<tr><th>指标</th><th class="num">目标</th><th class="num">实测</th><th>判定</th></tr>
<tr><td>成功样本</td><td class="num">10,000,000</td><td class="num">9,999,999</td><td><span class="tag ok">✅</span></td></tr>
<tr><td>渲染失败率</td><td class="num">&lt;2%</td><td class="num">0.00% (fail=0)</td><td><span class="tag ok">✅ 通过</span></td></tr>
<tr><td>空/纯色图</td><td class="num">0</td><td class="num">0</td><td><span class="tag ok">✅ 通过</span></td></tr>
<tr><td>文本 sha1 跨 shard 重复率</td><td class="num">&lt;1%</td><td class="num"><b>2.4486%</b>（244,858 多余重复）</td><td><span class="tag warn">⚠ 超标</span></td></tr>
<tr><td>评测泄漏命中</td><td class="num">0</td><td class="num">113（leak_rate=1.16e-5）</td><td><span class="tag warn">⚠ 命中</span></td></tr>
<tr><td>shard tar</td><td class="num">2,000</td><td class="num">2,000</td><td><span class="tag ok">✅</span></td></tr>
<tr><td>总占用</td><td class="num">—</td><td class="num">470.0 GB (0.5046 TB)</td><td>—</td></tr>
<tr><td>吞吐</td><td class="num">—</td><td class="num">893.6 img/s · 3h 6m 30s</td><td>—</td></tr>
</table>
<p>
<b>逐类计数</b>（cat_counts == cat_plan，math 差 1 因 1 条文本 sha1 重复被内联去重丢弃）：
english 3,000,000 / chinese 2,000,000 / mixed 1,000,000 / document 1,500,000 / chart 1,000,000 / math 999,999 / handwrite 300,000 / scene 200,000。
文本长度（n_tokens）：p50=14 / p95=75 / max=99 / mean=25.88。
</p>
"""

def sec2_tasks_f():
    return f"""
<div class="bad">
<b>两处质量偏差（如实记录，未掩盖）</b>（<span class="src">§18:1855-1857</span>）：
<ol>
<li><b>文本去重 2.4486% &gt; 1% 目标</b>：生成器内联去重计数的是<b>图像</b> sha1（数学抖动保证图像唯一 ⇒ dup=0），
而任务书要求的是<b>文本</b> sha1 跨 shard 去重。合成文本（词表+模板）组合空间有限 ⇒ 16,634 个文本 hash 重复、244,858 条多余样本。
真实文本去重率由 <span class="src">postprocess_ocr_synth.py</span> 独立复检得到。
<b>待用户决定</b>：接受（合成数据视觉多样性为主价值）/ 做 index 过滤补救（保留 9,755,141 唯一文本样本）/ 扩语料重生成。</li>
<li><b>泄漏护栏 113 命中</b>：生成器内联护栏 <code>_load_leakage_hashes()</code> 只搜 <code>~/.cache/huggingface</code>
（评测集实位于 <code>/nas_env/app.e0031982/hf_home/hub/</code>）⇒ 内联护栏为<b>空操作</b>。
真实复检由 postprocess 读取 OCRBench/DocVQA/ChartQA parquet 完成。命中的 113 条均为极短归一化串
（如 <code>0.29</code>→029、<code>PP</code>→pp）与评测答案的巧合碰撞，<b>合成图 ≠ 评测图，非真实内容泄漏</b>；
按严格规范应剔除这些 key（InfoVQA parquet 未找到，未参与复检）。</li>
</ol>
</div>
<p>
<b>加载器兼容性验证</b>：<span class="src">vision/ocr_synth/verify_loader_compat.py</span> 真 <code>build_gpic_loader(caption_type='short')</code> + open_clip tokenizer
读 8 个 full-run shard → 1 batch (16,3,224,224) finite normalized，tokenizer 返回 16 条 ids ⇒ <b>FORMAT COMPATIBLE</b>。
</p>
<p>
<b>交付物</b>（<span class="src">§18:1861</span>）：数据本体 + <span class="src">index.jsonl</span>(9,999,999 行) + <span class="src">STATS.json</span> +
<span class="src">VALIDATION.json</span> + <span class="src">DATASET_CARD.md</span> + <span class="src">MANIFEST.sha256</span>(2000 行) +
<span class="src">preview_200.html</span>(自包含预览) + <span class="src">preview_10k.tar</span>(1 万抽样包 510MB) +
报告 <span class="src">reports/report_vision_ocr_synth10m_zh.html</span>(15754 B / 8 节 / 0 &lt;script&gt; / 0 外链 / 标签配平 / ≥15KB)。
生成器/验证器：<span class="src">vision/ocr_synth/&#123;gen_ocr_synth,postprocess_ocr_synth,verify_loader_compat,make_preview,generate_ocr_synth10m_report&#125;.py</span>（固定 seed=20261025，可重放）。
</p>
<p class="small"><b>资源纪律</b>：CPU-only、<code>nice -n 10</code>、一律不占显存；在 .12 运行，避让 .29 分词/训练。语料只用可商用/可再分发来源，逐类 License 见 DATASET_CARD。</p>
"""

def sec3_quickref_a():
    return f"""
<h2>3. 关键数据速查表</h2>
<h3>3.1 四臂编码器 ProtB（Protocol B，IN-1k 1.28M train / 50k val，3 seeds）</h3>
<table>
<caption>来源：<span class="src">EXPERIMENTS_VISION.md §14.3 / §15.3</span> + <span class="src">vision/arm*_protb_*_results.json</span></caption>
<tr><th>臂</th><th>视觉塔</th><th class="num">参数</th><th>LR / warmup</th><th class="num">ProtB lp (%)</th><th class="num">5-NN (%)</th><th>状态</th></tr>
<tr><td>ArmB</td><td>ViT-B/16 224</td><td class="num">86.2M</td><td>1e-3 / 2000</td><td class="num">62.093</td><td class="num">58.102</td><td><span class="tag">基线</span></td></tr>
<tr><td>ArmC</td><td>ViT-B/16 224</td><td class="num">86.2M</td><td>1e-3 / 2000</td><td class="num">62.332</td><td class="num">54.718</td><td><span class="tag">收敛</span></td></tr>
<tr><td>ArmD-R2</td><td>ViT-B/16 224</td><td class="num">86.2M</td><td>1e-3 / 2000</td><td class="num">64.3373</td><td class="num">55.956</td><td><span class="tag ok">✅ DONE</span></td></tr>
<tr><td><b>ArmE-R2</b></td><td><b>ViT-L/14 224</b></td><td class="num"><b>304M</b></td><td><b>5e-4 / 3000</b></td><td class="num"><b>68.236 🏆</b></td><td class="num"><b>58.904 🏆</b></td><td><span class="tag win">✅ 历史最高</span></td></tr>
<tr><td>ArmE（发散）</td><td>ViT-L/14 224</td><td class="num">304M</td><td>1e-3 / 2000</td><td class="num">—</td><td class="num">—</td><td><span class="tag bad">❌ s29200 发散</span></td></tr>
</table>

<h3>3.2 四臂 12 集 lmms-eval（Stage-2 step3500，224px 单块，无 anyres）</h3>
<table>
<caption>来源：<span class="src">mllm_eval_results_arm*/consolidated_12benchmarks.json</span> + <span class="src">EXPERIMENTS_VISION.md §14.6 / §15.5</span></caption>
<tr><th>集</th><th class="num">ArmE-R2</th><th class="num">ArmD-R2</th><th class="num">ArmC</th><th class="num">ArmB</th><th>口径</th></tr>
<tr><td>ai2d</td><td class="num">60.65</td><td class="num">60.49</td><td class="num">59.03</td><td class="num">60.69</td><td>acc</td></tr>
<tr><td>realworldqa</td><td class="num">45.36</td><td class="num">46.41</td><td class="num">44.97</td><td class="num">45.49</td><td>acc</td></tr>
<tr><td>mmmu_val</td><td class="num">44.00</td><td class="num">42.67</td><td class="num">42.56</td><td class="num">43.67</td><td>acc</td></tr>
<tr><td>blink</td><td class="num">38.88</td><td class="num">39.59</td><td class="num">38.15</td><td class="num">38.94</td><td>acc</td></tr>
<tr><td>mmstar</td><td class="num">27.17</td><td class="num">27.07</td><td class="num">28.38</td><td class="num">27.95</td><td>acc</td></tr>
<tr><td>mmmu_pro_standard</td><td class="num">23.12</td><td class="num">22.60</td><td class="num">22.60</td><td class="num">22.43</td><td>acc</td></tr>
<tr><td>infovqa_val</td><td class="num">16.18</td><td class="num">16.59</td><td class="num">17.09</td><td class="num">16.88</td><td>ANLS</td></tr>
<tr><td>chartqa</td><td class="num">12.16</td><td class="num">12.92</td><td class="num">12.48</td><td class="num">12.52</td><td>relaxed</td></tr>
<tr><td>countbench</td><td class="num">10.59</td><td class="num">9.98</td><td class="num">8.96</td><td class="num">9.57</td><td>acc</td></tr>
<tr><td>docvqa_val</td><td class="num">7.35</td><td class="num">7.44</td><td class="num">7.58</td><td class="num">7.36</td><td>ANLS</td></tr>
<tr><td>ocrbench</td><td class="num">1.60</td><td class="num">1.60</td><td class="num">1.80</td><td class="num">1.60</td><td>exact-match</td></tr>
<tr><td><b>平均(除MME)</b></td><td class="num"><b>26.10</b></td><td class="num"><b>26.12</b></td><td class="num"><b>25.78</b></td><td class="num"><b>26.10</b></td><td>—</td></tr>
</table>
<div class="note">
<b>口径说明</b>：OCRBench(exact-match) / DocVQA(ANLS) / ChartQA(relaxed) / InfoVQA(ANLS) 均<b>不需要 LLM judge</b>，
与 MMVet / MathVista 的 <code>OPENAI_API_KEY</code> 阻塞无关，可直接测。MME 因量纲不同（perception/accuracy 分项）不计入平均（除 MME），沿用既有口径。
</div>
"""

def sec3_quickref_b():
    return f"""
<h3>3.3 OCR 10M 合成数据集（STATS.json 实读）</h3>
<table>
<caption>来源：<span class="src">ocr_synth_10m_full/STATS.json</span> + <span class="src">VALIDATION.json</span></caption>
<tr><th>项</th><th class="num">值</th></tr>
<tr><td>ok / fail</td><td class="num">9,999,999 / 0</td></tr>
<tr><td>shards (tar)</td><td class="num">2,000</td></tr>
<tr><td>total_bytes</td><td class="num">504,647,649,280 (470.0 GB / 0.5046 TB)</td></tr>
<tr><td>throughput_img_s</td><td class="num">893.6</td></tr>
<tr><td>elapsed_s</td><td class="num">11,190.2 (3h 6m 30s)</td></tr>
<tr><td>文本 sha1 重复率（postprocess 复检）</td><td class="num"><b>2.4486%</b> ⚠</td></tr>
<tr><td>泄漏命中（postprocess 复检）</td><td class="num">113 (leak_rate=1.16e-5) ⚠</td></tr>
<tr><td>文本长度 n_tokens (p50/p95/mean)</td><td class="num">14 / 75 / 25.88</td></tr>
</table>

<h3>3.4 本窗口交付物清单</h3>
<table>
<caption>2026-10-20 起 vision 线交付物（全在仓库，可 git 溯源）</caption>
<tr><th>类别</th><th>产物</th><th>来源 / 生成器</th></tr>
<tr><td>实验记录</td><td>EXPERIMENTS_VISION.md §14 / §15 / §16 / §17 / §18</td><td><span class="src">run/EXPERIMENTS_VISION.md</span></td></tr>
<tr><td>ArmD-R2 报告</td><td>report_vision_armD_r2_20261020_mllm_stage4_zh.html</td><td><span class="src">vision/generate_armD_r2_mllm_report.py</span></td></tr>
<tr><td>ArmE-R2 报告（完整版 7 节）</td><td>report_vision_armE_r2_20261024_zh.html (25.9KB)</td><td><span class="src">vision/generate_armE_r2_full_report.py</span></td></tr>
<tr><td>下一步方案报告</td><td>report_vision_next_steps_protb_mllm_zh.html (21.1KB)</td><td><span class="src">vision/generate_next_steps_protb_mllm_report.py</span></td></tr>
<tr><td>OCR 调研报告</td><td>report_vision_ocr_synthdata_zh.html (29177B)</td><td><span class="src">vision/generate_ocr_synthdata_report.py</span></td></tr>
<tr><td>OCR SFT 方案报告</td><td>report_vision_ocr_sft_plan_zh.html (22706B)</td><td><span class="src">vision/generate_ocr_sft_plan_report.py</span></td></tr>
<tr><td>OCR 10M 数据集报告</td><td>report_vision_ocr_synth10m_zh.html (15754B)</td><td><span class="src">vision/ocr_synth/generate_ocr_synth10m_report.py</span></td></tr>
<tr><td>OCR 10M 数据本体</td><td>9,999,999 图文对 / 2000 tar / 470GB</td><td><span class="src">datasets/baize-vision/ocr_synth_10m_full/</span></td></tr>
<tr><td>OCR 10M 生成/验证脚本</td><td>5 个 .py（固定 seed=20261025 可重放）</td><td><span class="src">vision/ocr_synth/*.py</span></td></tr>
<tr><td>本报告</td><td>report_vision_recent_work_zh.html</td><td><span class="src">vision/generate_recent_work_report.py</span></td></tr>
</table>
"""

def sec4_blockers():
    return f"""
<h2>4. 阻塞 / 待用户决策</h2>
<table>
<caption>阻塞项与待拍板（按优先级）</caption>
<tr><th>#</th><th>阻塞 / 待决</th><th>当前状态</th><th>需要的输入</th><th>来源</th></tr>
<tr><td>B1</td><td><b>OCR 10M 数据文本去重 2.4486%（超 1% 目标）</b>如何处置</td><td>已实测、已报告、已给三选项</td><td>用户三选一：① 接受（视觉多样性为主）② index 过滤补救(保留 9,755,141 唯一文本) ③ 扩语料重生成</td><td><span class="src">§18.7:1855</span></td></tr>
<tr><td>B2</td><td><b>OCR 10M 泄漏护栏 113 命中</b>是否剔除 key</td><td>已复检、已定性（巧合碰撞非真实泄漏）</td><td>用户裁定：按严格规范剔除 / 保留</td><td><span class="src">§18.7:1856</span></td></tr>
<tr><td>B3</td><td><b>OCR 专项 SFT 是否启动</b>（P0 pilot 还是直接 P1 全量）</td><td>方案报告已交付、判据已预注册</td><td>用户批预算（pilot ≈2 GPU·卡·时 当天 / 全量 ≈12-18 GPU·卡·时 1 天）</td><td><span class="src">§17:1831</span></td></tr>
<tr><td>B4</td><td><b>OCR 10M 用于 vision encoder 预训练</b>的具体口径</td><td>用户口头「我后边把它用在 vision encoder 预训练里边」，未给参数</td><td>用户给定：单塔/双塔 · 224 还是多尺度 · 是否混 GPIC · 预算 steps</td><td><span class="src">§18.1:1838</span></td></tr>
<tr><td>B5</td><td><b>MLLM 下游天花板如何破</b>（容量/分辨率/anyres/Stage-3 优先级）</td><td>四臂 12 集证伪了「容量提升 MLLM」；ProtB→MLLM 传递性亦证伪。下一步方案报告已给三条候选</td><td>用户在「anyres 多块 / Stage-3 SFT / 换塔重训」之间拍板</td><td><span class="src">report_vision_next_steps_protb_mllm_zh.html</span></td></tr>
<tr><td>B6</td><td><b>MMVet / MathVista 评测</b>因 <code>OPENAI_API_KEY</code> 缺失阻塞</td><td>OCR 四集改用非-judge 口径已绕开；MMVet/MathVista 仍阻塞</td><td>用户提供 key，或改用本地 judge（暂不优先）</td><td><span class="src">§14.6</span></td></tr>
</table>
"""


def sec5_nextsteps():
    return f"""
<h2>5. 下一步（vision 线近期规划）</h2>
<p>按「<b>已收敛且高价值</b> → <b>用户已批预算</b> → <b>等用户拍板</b>」分层，每项标判据与成本：</p>
<ol>
<li><b>等用户决策 B1/B2/B3/B4</b>（<b>当前唯一前置</b>）：OCR 10M 去重处置 + 泄漏剔除 + OCR SFT 是否启动 + 10M 预训练口径。在用户回话前 vision 线<b>不主动开新 GPU 训练</b>（数据/报告/调研类 CPU 活可继续）。</li>
<li><b>P0 OCR SFT pilot</b>（待 B3 批准）：渲染 ~5k OCR 对（候选 A 配比，英6:中3:混1，含数学三通道）→ 与 780k 混 70%OCR:30% → ArmE-R2 Stage-2 step3500 起 LoRA SFT → 测 OCRBench。判据：OCRBench ≥ +2pp（1.60% → ≥3.60%）。成本 ≈2 GPU·卡·时 / 当天。决策树见 <span class="src">report_vision_ocr_sft_plan_zh.html</span>。</li>
<li><b>P1 OCR SFT 全量</b>（待 P0 达标）：渲染 ~50-80k OCR 对 → 同口径全量 SFT → 测全 12 集 + 回归护栏。判据：主 OCRBench ≥ +2pp；副 DocVQA/ChartQA/InfoVQA 各 ≥ +1pp；MMStar/AI2D/RealWorldQA/MMBench 退化 ≤ 1pp。成本 ≈12-18 GPU·卡·时 / 渲染一宿 + 训练 ~1 天。</li>
<li><b>OCR 10M 用于 encoder 预训练</b>（待 B4 给口径）：候选 = 在 ArmE-R2 open_clip_state_dict 上继续预训练（OCR+GPIC 混），或单塔 OCR 专项。具体 steps/LR/分辨率待用户定。</li>
<li><b>MLLM 下游天花板突破</b>（待 B5 拍板）：候选三选一 —— ① anyres 多块（336×3=9 块）破分辨率瓶颈；② Stage-3 SFT（指令微调，破 in-context 学习）；③ 换更大塔重训。下一步方案报告已列利弊与成本。</li>
<li><b>持续维护</b>：EXPERIMENTS_VISION.md / MEMORY_VISION.md 体积滚动（≤32KB）；本报告与各子报告保持可由生成器重放（固定 seed / 纯字符串拼接 / 0 &lt;script&gt; / 0 外链）。</li>
</ol>
<div class="note">
<b>纪律</b>：① 任何「下一步」启动前先在 EXPERIMENTS_VISION.md 登记 <code>## §19 ...</code> 节并写实验设计；
② 训练类活避让 <span class="src">10.239.2.29</span>（pretrain 线在跑）；
③ OCR/数据类 CPU 活用 <code>nice -n 10</code>，不占显存；
④ 报告统一中文 / 自包含 / 0 script / 0 外链 / 标签配平 / ≥15KB（10M 数据集报告 ≥15KB）。
</div>
"""

def build():
    """Assemble the full HTML report (pure string concatenation, reproducible)."""
    sec2 = (sec2_tasks_a() + sec2_tasks_b() + sec2_tasks_c()
            + sec2_tasks_d() + sec2_tasks_e() + sec2_tasks_f())
    sec3 = sec3_quickref_a() + sec3_quickref_b()

    body = f"""
{sec1_position()}
{toc()}
<h2>2. 本窗口完成任务</h2>
{sec2}
{sec3}
{sec4_blockers()}
{sec5_nextsteps()}
<hr/>
<p class="small">
本报告由 <span class="src">vision/generate_recent_work_report.py</span> 生成（纯字符串拼接，0 外部依赖，固定可重放）。
所有数据可溯源至 <span class="src">run/EXPERIMENTS_VISION.md §14-§18</span> 与对应 JSON/tar 产物。生成于 2026-10-26。
</p>
</article>
</body>
</html>
"""
    return section_header() + body


def main():
    html = build()
    issues, size = self_check(html)
    print(f"  [self_check] size={size}B ({size/1024:.1f}KB)")
    if issues:
        print("[FATAL] self_check FAILED:")
        for it in issues:
            print(f"  - {it}")
        raise SystemExit(1)
    out_path = os.path.join(REPORTS_DIR, OUT_NAME)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] wrote {out_path} ({size} bytes / {size/1024:.1f}KB)")


if __name__ == "__main__":
    main()
