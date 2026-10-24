#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_next_steps_protb_mllm_report.py
  产出: reports/report_vision_next_steps_protb_mllm_zh.html
  用途: 运维令 2026-10-24 16:1x ——「下一步如何提升 ProtB 和 MLLM 成绩」方案报告。
  纪律: 单文件自包含中文 HTML（无外链 CDN / 无 <script>，标签配平）。
        所有数字可溯源到 EXPERIMENTS_VISION.md / MEMORY_VISION.md / 落盘 JSON。
        推测项一律标「推测·未验证」。本轮只出方案，不启动训练。
  运行: python3 vision/generate_next_steps_protb_mllm_report.py
"""
import os, datetime, re

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "reports", "report_vision_next_steps_protb_mllm_zh.html")
GEN_TS = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

CSS = """
body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
       max-width: 1160px; margin: 0 auto; padding: 20px; color: #222; line-height: 1.62; }
h1 { color: #1a3a5c; border-bottom: 3px solid #1a3a5c; padding-bottom: 8px; }
h2 { color: #2a5a8c; margin-top: 30px; border-left: 5px solid #2a5a8c; padding-left: 10px; }
h3 { color: #345; margin-top: 18px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }
th, td { border: 1px solid #ccc; padding: 5px 8px; text-align: center; }
th { background: #eef4fa; font-weight: 600; }
tr:nth-child(even) { background: #f8fafc; }
td { text-align: right; } td.l { text-align: left; }
.ok { color: #1a7a1a; font-weight: 600; } .bad { color: #c00; font-weight: 600; }
.warn { color: #b80; font-weight: 600; } .key { color: #1a3a5c; font-weight: 700; }
.small { font-size: 12px; color: #666; }
code { background: #f0f0f0; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
.kbox { background: #fffbe6; border: 1px solid #e0d090; border-radius: 6px; padding: 12px 16px; margin: 12px 0; }
.nbox { background: #f0f6fc; border: 1px solid #b0d0e8; border-radius: 6px; padding: 12px 16px; margin: 12px 0; }
.gbox { background: #eef9ee; border: 1px solid #a0d0a0; border-radius: 6px; padding: 12px 16px; margin: 12px 0; }
pre { background: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; padding: 10px; overflow-x: auto; font-size: 12px; }
.pri1 { background:#d6efd6; } .pri2 { background:#eef4fa; } .pri3 { background:#f5f0f0; }
"""

H = []
def w(s): H.append(s)

w(f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BaiZe 视觉编码器 · 下一步如何提升 ProtB 与 MLLM 成绩（方案报告）</title>
<style>{CSS}</style></head><body>
<h1>BaiZe 视觉编码器 · 下一步如何提升 ProtB 与 MLLM 成绩</h1>
<p class="small">方案报告（运维令 2026-10-24 16:1x · 用户直令「vision：下一步如何提升 ProtB 和 MLLM 成绩，写个报告」）· 生成于 {GEN_TS} · 单文件自包含（无外链 CDN / 无 &lt;script&gt;）· 🚫 本轮只出方案、不启动任何训练（等用户批准）· 所有数字可溯源到落盘产物，推测项标注「推测·未验证」</p>
""")

w("""
<h2>1. 摘要</h2>
<div class="kbox"><b>一句话结论</b>：当前 <b>12 集评测已饱和</b>——4 个臂（ArmB/C/D-R2/E-R2）的 ProtB lp 跨度 6.15pp（62.09→68.24），但 MLLM 12 集平均仅跨度 0.34pp（25.78→26.12），逐集最大跨度 1.66pp 且多数在 1 个标准误内。<b>在能证明「评测集对编码器差异敏感」之前，继续堆编码器实验对 MLLM 下游无意义。</b></div>
<div class="gbox"><b>下一步最该做的一件事（单一建议）</b>：<b>用更难 / 更有区分度的评测集（MMBench、MMVet、MathVista，以及 336/anyres 推理变体）在已有的 ArmB（ViT-B/16）与 ArmE-R2（ViT-L/14）Stage-2 ckpt 上重测</b>——纯评测、~0 GPU·h。
<ul>
<li>若 ArmB vs ArmE-R2 在更难集上 Δ 仍 &lt; 2pp ⇒ <b>评测/MLLM 对齐是瓶颈</b>，应转向 Stage-2 数据 / projector / LoRA 全参微调（B1–B3），<b>而非继续放大编码器</b>。</li>
<li>若 Δ &gt; 2pp ⇒ 编码器差异真实存在、只是被当前易集掩盖 ⇒ 再追投 <b>A1 分辨率 224→336</b>（对细粒度/文档任务收益最大）。</li>
</ul>
这是所有候选方向里<b>信息量最大、成本最低</b>的一步：它直接判定「ProtB→MLLM 传递性失效」是真失效还是评测盲区。</div>
<p class="small"><b>报告结构</b>：§2 现状与核心矛盾 · §3 参照系校准（ProtB 还有多少空间）· §4 提升 ProtB 的方向（A1–A5）· §5 提升 MLLM 下游的假设（B1–B5）· §6 全部方向汇总表 · §7 结论与替代评测集方案 · 附录 数据溯源 + 诚实条款。</p>
""")

w("""
<h2>2. 现状与核心矛盾（分析的起点，必须写准）</h2>
<table>
<tr><th>阶段</th><th>结果</th><th>对比</th></tr>
<tr><td class="l"><b>ProtB（编码器）</b></td><td class="l"><b>ArmE-R2 lp 68.236±0.0182 / 5-NN 58.904</b></td><td class="l">🏆 全实验最高（vs ArmD-R2 <b>Δlp +3.899 / Δ5-NN +2.948</b>）</td></tr>
<tr><td class="l"><b>MLLM（12 集）</b></td><td class="l"><b>ArmE-R2 avg 26.10%</b></td><td class="l">vs ArmD-R2 26.12%（<b>−0.02pp</b>）/ vs ArmC 25.78%（+0.32）/ vs ArmB 26.10%（0.00）</td></tr>
<tr><td class="l"><b>裁定</b></td><td class="l"><b>不可分辨（边界值）</b></td><td class="l">落在预注册 22–26.5% 带</td></tr>
</table>
<p class="small">来源：<code>vision/armE_r2_20261022_protb_vitl14_224_results.json</code>（lp_mean 68.236 / lp_sigma 0.0182 / knn5 58.904 / per_seed [68.212, 68.256, 68.240]）+ <code>EXPERIMENTS_VISION.md §15.3 / §15.5</code> + <code>reports/report_vision_armE_r2_20261024_zh.html §4/§6</code>。</p>

<div class="kbox"><b>核心矛盾（报告先讲透）</b>
<ul>
<li><b>编码器涨了 +3.9pp，MLLM 下游却 −0.02pp</b> → <b>ProtB→MLLM 传递性再次证伪</b>（ArmD-R2 时已证伪一次：ArmD-R2 vs ArmC ProtB Δlp +2.005pp 而 MLLM Δavg 仅 +0.34pp；ArmE-R2 用更大的 ViT-L/14 再次印证，且 ProtB 差距更大、MLLM 持平更明确）。</li>
<li><b>ViT-L/14（304M visual）比 ViT-B/16（86M）大 3.5×，MLLM 12 集仍持平 → 容量不是 MLLM 下游瓶颈</b>（在 224px 单块 + 当前 MLLM 架构下）。</li>
</ul></div>

<h3>2.1 关键证据：ProtB 跨度大、MLLM 跨度极小</h3>
<table>
<tr><th>臂</th><th>视觉塔</th><th>ProtB lp (%)</th><th>ProtB 5-NN (%)</th><th>MLLM avg(除MME) (%)</th></tr>
<tr><td class="l">ArmE-R2</td><td class="l">ViT-L/14 (304M)</td><td><b>68.236</b></td><td><b>58.904</b></td><td><b>26.10</b></td></tr>
<tr><td class="l">ArmD-R2</td><td class="l">ViT-B/16 (86M)</td><td>64.337</td><td>55.956</td><td>26.12</td></tr>
<tr><td class="l">ArmC</td><td class="l">ViT-B/16 (86M)</td><td>62.332</td><td>54.718</td><td>25.78</td></tr>
<tr><td class="l">ArmB</td><td class="l">ViT-B/16 (86M)</td><td>62.093</td><td>58.102</td><td>26.10</td></tr>
<tr style="font-weight:700;background:#eef4fa"><td class="l">跨度 (max−min)</td><td class="l">—</td><td>6.143</td><td>4.386</td><td>0.34</td></tr>
</table>
<p class="small">来源：<code>EXPERIMENTS_VISION.md §15.3 / §15.5</code>（同 Protocol B、同 IN-1k 1.28M train / 50k val；MLLM 同 Stage-2 原版 LLaVA-NeXT-780k quick-start 子集）。
<b>读法</b>：编码器线性可分性跨度 6.15pp，近邻检索跨度 4.39pp，但 MLLM 下游跨度仅 0.34pp——<b>编码器的 4–6pp 优势几乎 100% 被吞掉</b>。</p>
""")

w("""
<h3>2.2 逐集跨度：无一集能区分 4 个臂</h3>
<table>
<tr><th>集</th><th>ArmE-R2</th><th>ArmD-R2</th><th>ArmC</th><th>ArmB</th><th>逐集跨度 (pp)</th><th>标准误 (估, pp)</th><th>是否可分辨</th></tr>
<tr><td class="l">ai2d</td><td>60.65</td><td>60.49</td><td>59.03</td><td>60.69</td><td>1.66</td><td>0.88</td><td class="warn">≈1.9σ 边界</td></tr>
<tr><td class="l">countbench</td><td>10.59</td><td>9.98</td><td>8.96</td><td>9.57</td><td>1.63</td><td>1.40</td><td class="bad">&lt;1σ 噪声</td></tr>
<tr><td class="l">realworldqa</td><td>45.36</td><td>46.41</td><td>44.97</td><td>45.49</td><td>1.44</td><td>1.79</td><td class="bad">&lt;1σ 噪声</td></tr>
<tr><td class="l">mmmu_val</td><td>44.00</td><td>42.67</td><td>42.56</td><td>43.67</td><td>1.44</td><td>N/A</td><td class="warn">小集</td></tr>
<tr><td class="l">blink</td><td>38.88</td><td>39.59</td><td>38.15</td><td>38.94</td><td>1.44</td><td>N/A</td><td class="warn">小集</td></tr>
<tr><td class="l">mmstar</td><td>27.17</td><td>27.07</td><td>28.38</td><td>27.95</td><td>1.31</td><td>1.15</td><td class="bad">≈1.1σ 噪声</td></tr>
<tr><td class="l">infovqa_val</td><td>16.18</td><td>16.59</td><td>17.09</td><td>16.88</td><td>0.91</td><td>0.63</td><td class="bad">噪声</td></tr>
<tr><td class="l">chartqa</td><td>12.16</td><td>12.92</td><td>12.48</td><td>12.52</td><td>0.76</td><td>0.66</td><td class="bad">噪声</td></tr>
<tr><td class="l">mmmu_pro</td><td>23.12</td><td>22.60</td><td>22.60</td><td>22.43</td><td>0.69</td><td>N/A</td><td class="bad">小集</td></tr>
<tr><td class="l">docvqa_val</td><td>7.35</td><td>7.44</td><td>7.58</td><td>7.36</td><td>0.23</td><td>0.30</td><td class="bad">噪声</td></tr>
<tr><td class="l">ocrbench</td><td>1.60</td><td>1.60</td><td>1.80</td><td>1.60</td><td>0.20</td><td>0.33</td><td class="bad">噪声</td></tr>
</table>
<p class="small">来源：逐集数值 <code>EXPERIMENTS_VISION.md §15.5</code>；标准误 <code>vision/consolidated_12benchmarks.json</code>（raw_results.*_stderr_clt）。
<b>读法</b>：11 个 benchmark 中<b>无一集</b>的 4 臂跨度超过 ~1.7pp，且多数集的跨度落在 1 个标准误以内 = 纯噪声。<b>这组评测集对「ViT-B/16 vs ViT-L/14」这一量级的编码器差异不敏感</b>。注意 <b>MMStar、RealWorldQA 已在 12 集内</b>（运维令提到的「更难集」），二者跨度分别仅 1.31 / 1.44pp ⇒ 已饱和，换它们无意义，需换<b>更难或对分辨率/细节更敏感</b>的集。</p>
""")

w("""
<h2>3. 参照系校准：ProtB 还有多少空间</h2>
<p class="small">来源：<code>vision/external_protb_results_merged.json</code>（同 Protocol B、同 IN-1k 1.28M train / 50k val、3 seeds、feature=projected）——这是我们用<b>同一评测管线</b>测的外部预训练编码器，<b>口径严格可比</b>。</p>
<table>
<tr><th>编码器</th><th>分辨率</th><th>ProtB lp (%)</th><th>文献/榜参考</th><th>预训练?</th></tr>
<tr><td class="l">SigLIP2-so400m</td><td>384</td><td><b>87.46</b></td><td class="small">~83.1% (hf lp)</td><td>是</td></tr>
<tr><td class="l">AIMv2-1B</td><td>336</td><td>85.22</td><td class="small">~87.6% (AIMv2-L 0.3B@336)</td><td>是</td></tr>
<tr><td class="l">OpenVision2-L/14</td><td>336</td><td>84.97</td><td class="small">79.81% (ProtA R13)</td><td>是</td></tr>
<tr><td class="l">CLIP ViT-L/14</td><td>336</td><td>82.66</td><td class="small">~88.1% (OpenCLIP lp)</td><td>是</td></tr>
<tr><td class="l">RICE-ViT-L</td><td>560</td><td>81.72</td><td class="small">~84.0% (估)</td><td>是</td></tr>
<tr style="font-weight:700;background:#eef4fa"><td class="l">BaiZe ArmE-R2（本仓）</td><td>224</td><td>68.236</td><td class="small">内部 ProtB</td><td>否（从头）</td></tr>
</table>
<div class="nbox"><b>空间估算</b>：
<ul>
<li>vs <b>CLIP ViT-L/14@336（同塔架构，82.66%）</b> = 差 <b>14.42pp</b>。但对方是<b>预训练 + 336 分辨率</b>，本仓是<b>从头 + 224</b> ⇒ 这 14pp 是「预训练 + 分辨率 + 数据 + 目标」的<b>复合差距，不能单归因</b>。</li>
<li>vs <b>SigLIP2-so400m@384（87.46%）</b> = 差 <b>19.22pp</b>（更大模型 + 更多数据 + 384）。</li>
<li><b>结论</b>：ProtB 在「同口径、同 IN-1k」下仍有 <b>~14–19pp 理论空间</b>，但其中相当一部分来自<b>预训练权重</b>（本仓路线是从头训练，不走预训练）。在「从头 + 224」约束下，<b>可争取的现实空间约 +3–8pp</b>（分辨率 + 训练时长 + 更大模型，见 §4）。</li>
</ul></div>
<p class="small">⚠️ <b>口径诚实条款</b>：外部编码器均为<b>大规模预训练</b>（CLIP/SigLIP/AIMv2 用了 100M–10B 级图文对 + 可能的 LAION 等更大数据），本仓 ArmE-R2 仅用 173M 对 / 3 epoch 从头训练。把 68.24% 与 82.66% 直接比「目标函数好坏」是<b>不成立</b>的——差距主因是预训练数据量级，不是 loss 设计。</p>
""")

w("""
<h2>4. A 线 · 如何继续提升 ProtB（编码器）</h2>
<p class="small">现有 best = <b>lp 68.236</b>（ArmE-R2，ViT-L/14@224，从头，173M 对，3 epoch）。下方每条给<b>预期增益 + 成本 + 风险 + 可判定判据</b>。标注「推测·未验证」者为基于文献/历史的推断，非实测。</p>

<h3>4.1 已消融、维持现状（不再作为方向）</h3>
<div class="nbox"><b>BP-2 超参已定</b>（小规模 R11 消融，<code>EXPERIMENTS_VISION.md</code> mask-ratio / weight-ratio 节）：
<ul>
<li><b>mask_ratio = 0.6</b>：5 臂（0.3/0.5/0.6/0.75/0.9）倒 U 形，0.6 最优（lp@30k 13.49%）；0.3–0.75 不敏感，0.5/0.9 显著更差。<b>维持 0.6</b>。</li>
<li><b>contrast:patch = 1:1</b>：4 臂（1:2/1:0.5/0.5:1/2:1）无臂超 +1.5pp 阈值；contrast 过高（2:1）显著有害 −3.28pp，patch 过高（1:2）中性 −0.36pp。<b>维持 1:1</b>。</li>
<li><b>AIMv2-style 稠密目标</b>（InfoNCE + masked-patch-MSE）已优于纯 InfoNCE / CoCa / 纯 AR / SigLIP（BP-1）。<b>维持</b>。</li>
</ul>
<b>注</b>：这些消融在 OpenVision2 w512 / Protocol A / 30k 步的小规模上做的（lp ~13% 档），结论的「排序」在 ArmB–E（62–68% 档）上<b>尚未复验</b>，但作为默认值继续沿用合理；若要在大规模上重验需另开消融（成本高，暂不优先）。</div>

<h3>4.2 A1 · 分辨率 224 → 336</h3>
<div class="nbox">
<b>依据</b>：ViT-L/14 在 336 下的 patch 数 224/14=16×16=256 → 336/14=24×24=576（2.25× tokens）。文献上 CLIP/SigLIP 从 224→336 通常 +3–5pp lp。<b>（推测·未验证，本仓无 224 vs 336 的受控对照——外部参考 clip-vitl14-336=82.66% 是预训练，混入了预训练效应）</b><br>
<b>对 MLLM 的潜在意义</b>：文档/OCR/图表类任务（DocVQA/ChartQA/InfoVQA/OCRBench）在 224 单块下被分辨率硬封顶（4 集均 1.6–16.6% 且跨臂 &lt;1pp），336 推理可能直接解锁这部分——<b>这是 A 线里唯一可能同时帮到 MLLM 下游的方向</b>。<br>
<b>风险</b>：ArmE-R2@224 显存峰值已 77.5GB/80GB（MBS 256），336 需 MBS↓ 或 accum↑；前向 ~2.25× tokens ⇒ 训练时长 ~2×。
</div>

<h3>4.3 A2 · 训练时长 3 → 6 epoch</h3>
<div class="nbox">
<b>依据</b>：ArmE-R2 用 173M 对 × 3 epoch = 63,400 步。R11-G scaling 显示 lp 随 token 仍上升（R²=0.91，渐近 >>25.1%）。但 ④-4ep（748k 步）显示<b>递减</b>（67.05% MODERATE/DIMINISHING）⇒ 长跑有收益但边际递减。<b>（预期增益 +1–3pp，推测·未验证）</b><br>
<b>风险</b>：④-4ep 已证递减；且 ArmE-R2 末段有抖动（spike），更长训练可能放大末段不稳定性。
</div>
""")

w("""
<h3>4.4 A3 · best-ckpt 选择（末段抖动）—— 成本最低，建议先做</h3>
<div class="kbox">
<ul>
<li><b>事实</b>：ArmE-R2 <b>best C1 = 0.9664 @ s45240</b>（全 log 确认，<code>EXPERIMENTS_VISION.md §15.2</code>），但 ProtB 用的是 <code>open_clip_state_dict.pt = latest = s63400</code>（末段，C1~0.85）。</li>
<li><b>问题</b>：取最优点附近的 ckpt 跑 ProtB，是否会高 1–2pp？</li>
<li><b>现实约束</b>：训练代码<b>无 save-best 机制</b>（仅 <code>save_every=10000 + keep_ckpts=2</code> 滚动删，<code>armE_r2_aimv2_openclip_vitl14.py:339-363</code>）；ArmE-R2 的 ckpt 40000 / 50000 <b>已被滚动删除</b>，现仅存 <code>checkpoint_60000.pt</code> + <code>checkpoint_63400.pt</code>（<code>ls</code> 确认）。<b>故 best-段 ckpt 无法回溯评测</b>——只能在<b>未来训练</b>中加 save-best-by-C1 或多 ckpt 评测来捕获。</li>
<li><b>可立即做的零成本验证</b>：对现存的 <code>checkpoint_60000.pt</code> 跑一次 ProtB（s60000 仍在末段，但与 s63400 不同点），对比 s63400 的 68.236%——若已有 1pp 级差异，说明 ckpt 选择敏感、值得加 save-best。<b>（预期增益 +0–2pp，推测·未验证；C1≠lp，R11 weight-ratio 的 0.5:1 臂 C1 最低但 lp 最高，故不保证有效）</b></li>
</ul></div>

<h3>4.5 A4 · 数据质量 / 配比</h3>
<div class="nbox">
<b>依据</b>：现 6 源 173M 对。R11-F 数据源横比显示 GPIC short/medium/short+medium <b>无显著差异</b>（<code>MEMORY_VISION.md</code> R11 节）。<b>（预期增益不确定；R11-F 已示不敏感，优先级低）</b><br>
<b>可能方向</b>：加入更高分辨率 / 更高质量 caption 的源（如 LAION-2B 高分面子集），但与 A1（分辨率）耦合，需一并设计。
</div>

<h3>4.6 A5 · 更大模型 ViT-H/14</h3>
<div class="nbox">
<b>依据</b>：ViT-L/14（304M）→ ViT-H/14（~632M visual）。<b>（预期增益 +2–4pp，推测·未验证）</b><br>
<b>风险</b>：ArmE（LR 1e-3）已证明 ViT-L/14 对 LR 敏感并发散；ViT-H 更大 ⇒ LR 调参更难、显存更紧、训练时长 ~2.5×。<b>成本/风险均高，优先级最低</b>。
</div>
""")

w("""
<h2>5. B 线 · 如何让 MLLM 下游真正提升（更关键）</h2>
<div class="kbox"><b>必须先回答：为什么传递性失效？</b>核心矛盾是「编码器涨 +3.9pp，MLLM 持平」。下面 5 个假设，每个配一个<b>可判定（可证伪）的实验</b>。<b>B4（评测饱和）是关键假设</b>——若成立，则 B1–B3 的改进也<b>测不出来</b>，必须先解 B4。</div>
<p class="small">MLLM 配置（4 臂一致）：LLM = Qwen3-4B-Instruct；Stage-1 projector（2500 步）→ Stage-1.5 LoRA r=64（20000 步）→ Stage-2 instruct（3500 步，原版 LLaVA-NeXT-780k quick-start 子集 738588 样本）；推理 224px 单块（无 anyres）。来源 <code>report_vision_armE_r2_20261024_zh.html §5</code>。</p>

<h3>5.1 B1 · Stage-2 数据太弱 / 太小</h3>
<div class="nbox">
<b>假设</b>：Stage-2 仅用原版 LLaVA-NeXT-780k 的 quick-start 子集（738K 样本）+ 3500 步，可能不足以让 MLLM 学到利用更好编码器特征的能力。<br>
<b>可判定实验</b>：用<b>完整 780k</b> 或 <b>opt47</b> 数据重训 Stage-2（同 ArmE-R2 ckpt），重测 12 集 + 更难集。<b>判据</b>：avg(除MME) Δ &gt; +1pp 且在更难集 Δ &gt; +2pp ⇒ 数据是瓶颈之一。<br>
<b>成本</b>：~1 GPU·h（Stage-2 仅 3500 步 ~17min + 评测）。<b>低成本，可做</b>。
</div>

<h3>5.2 B2 · projector（连接层）训练不足</h3>
<div class="nbox">
<b>假设</b>：Stage-1 projector 仅 2500 步（~7min），1024→2560 维映射可能欠拟合，使编码器的高质量特征在投到 LLM 时被「压扁」。<br>
<b>可判定实验</b>：加长 Stage-1（2500→10000 步）或提高 projector lr，其余不变，重测。<b>判据</b>：Δavg &gt; +1pp。<br>
<b>成本</b>：~1.5 GPU·h。<b>低成本，可做</b>。
</div>

<h3>5.3 B3 · LoRA 容量不足</h3>
<div class="nbox">
<b>假设</b>：Stage-1.5 用 LoRA r=64（仅少量参），可能不足以让 LLM 适配新编码器；尤其编码器换了（B/16→L/14、196→256 token），LLM 需更大调整。<br>
<b>可判定实验</b>：提升 r=64→128/256，或改<b>全参微调</b>（Qwen3-4B 全参）。<b>判据</b>：Δavg &gt; +2pp。<br>
<b>成本</b>：全参 ~3–4× Stage-1.5（~5 GPU·h）；提秩 ~1.5×。<b>中等成本</b>。
</div>
""")

w("""
<h3>5.4 B4 · 12 集 benchmark 本身饱和（关键假设）⭐</h3>
<div class="kbox">
<b>证据（已实测，非推测）</b>：
<ul>
<li>4 臂 ProtB lp 跨度 <b>6.15pp</b>，但 MLLM avg 跨度仅 <b>0.34pp</b>（§2.1）。</li>
<li>逐集最大跨度 <b>1.66pp</b>（ai2d），11 集中<b>无一</b>超过 ~1.7pp；多数集跨度 &lt; 1 个标准误（§2.2）。</li>
<li><b>运维令提到的 MMStar、RealWorldQA 已在 12 集内</b>，二者跨度仅 1.31 / 1.44pp ⇒ <b>已饱和，换它们无意义</b>。</li>
<li>文档/OCR/图表 4 集（DocVQA/ChartQA/InfoVQA/OCRBench）绝对值极低（1.6–16.6%）且跨臂 &lt;1pp ⇒ <b>224px 单块推理对细粒度任务硬封顶</b>，与编码器好坏无关。</li>
</ul>
<b>可判定实验（纯评测，~0 GPU·h）</b>：在<b>已有</b> ArmB（ViT-B/16）与 ArmE-R2（ViT-L/14）Stage-2 ckpt 上，跑<b>更难 / 更有区分度</b>的评测集 + 推理变体：
<ul>
<li><b>MMBench</b>（多能力维度，区分度高于 MMStar）</li>
<li><b>MMVet</b>（开放式综合，对模型能力差异更敏感）</li>
<li><b>MathVista</b>（数学视觉推理，对分辨率/细节敏感）</li>
<li><b>336 / anyres 推理变体</b>（同 ckpt、仅推理分辨率↑）——直接测「224 封顶」假设</li>
</ul>
<b>判据（可证伪）</b>：若 ArmB vs ArmE-R2 在<b>任一更难集</b>上 Δ &gt; 2pp ⇒ 编码器差异真实、只是被易集掩盖 ⇒ 转向 A1（336）；若<b>全部</b>更难集 Δ &lt; 2pp ⇒ <b>评测/MLLM 对齐是瓶颈</b>，转向 B1–B3，<b>停止编码器放大</b>。
</div>

<h3>5.5 B5 · 视觉 token 数（256 vs 196）对 LLM 上下文的影响</h3>
<div class="nbox">
<b>假设</b>：ViT-L/14 产出 256 patch tokens（vs B/16 的 196），更多视觉上下文进入 LLM。<br>
<b>已有反证</b>：ArmE-R2（256 tokens）并未胜过 ArmB（196 tokens）（MLLM avg 26.10 vs 26.10，0.00pp）⇒ <b>token 数不是区分因子</b>（至少在当前 12 集上）。<b>优先级低</b>；可在 B4 的更难集上一并观察。
</div>
""")

w("""
<h2>6. 全部方向汇总表</h2>
<p class="small">列：方向 | 预期增益 | 成本(GPU·h) | 风险 | 可判定判据 | 优先级（P1=先做 / P2=次 / P3=后）。「推测·未验证」者标注 †。</p>
<table>
<tr><th>方向</th><th>预期增益</th><th>成本 (GPU·h)</th><th>风险</th><th>可判定判据（可证伪）</th><th class="l">优先级</th></tr>
<tr class="pri1"><td class="l"><b>B4 更难/anyres 评测</b><br>(已有 ckpt)</td><td>—（判定性，非增益）</td><td><b>≈0</b></td><td>无</td><td class="l">ArmB vs ArmE-R2 在 MMBench/MMVet/MathVista/336anyres 上 Δ&gt;2pp ⇒ 编码器差异真；&lt;2pp ⇒ 评测/对齐瓶颈</td><td class="l key">P1 ⭐最优先</td></tr>
<tr class="pri1"><td class="l"><b>A3 best-ckpt 评测</b><br>(ckpt_60000 vs 63400)</td><td>+0–2pp †</td><td><b>≈0.3</b></td><td>C1≠lp 不保证有效</td><td class="l">ProtB(ckpt@60000) − ProtB(ckpt@63400) &gt; 1pp ⇒ ckpt 选择敏感</td><td class="l key">P1（零成本顺手做）</td></tr>
<tr class="pri2"><td class="l">A1 分辨率 224→336</td><td>+3–5pp †（ProtB）<br>可能解锁文档集（MLLM）</td><td>~75（训练 2×）</td><td>显存 OOM、LR/时长 2×</td><td class="l">受控 @224 vs @336 同 recipe Δlp&gt;2pp；MLLM 文档集 Δ&gt;2pp</td><td class="l">P2（视 B4 结果）</td></tr>
<tr class="pri2"><td class="l">B1 Stage-2 全量数据</td><td>+0–1pp †</td><td>~1</td><td>低</td><td class="l">Δavg&gt;1pp 且更难集 Δ&gt;2pp</td><td class="l">P2</td></tr>
<tr class="pri2"><td class="l">B2 projector 加长</td><td>+0–1pp †</td><td>~1.5</td><td>低</td><td class="l">Δavg&gt;1pp</td><td class="l">P2</td></tr>
<tr class="pri2"><td class="l">B3 LoRA 提秩/全参</td><td>+0–2pp †</td><td>~5（全参）</td><td>中</td><td class="l">Δavg&gt;2pp</td><td class="l">P2</td></tr>
<tr class="pri3"><td class="l">A2 训练 3→6 epoch</td><td>+1–3pp †</td><td>~75</td><td>递减（④-4ep 证）+ 末段抖动</td><td class="l">6-epoch Δlp&gt;1.5pp vs 3-epoch</td><td class="l">P3</td></tr>
<tr class="pri3"><td class="l">A4 数据配比</td><td>不确定 †</td><td>高（重训）</td><td>R11-F 已示不敏感</td><td class="l">换源后 Δlp&gt;2pp</td><td class="l">P3</td></tr>
<tr class="pri3"><td class="l">A5 ViT-H/14</td><td>+2–4pp †</td><td>~180</td><td>高（LR 敏感、显存、时长 2.5×）</td><td class="l">Δlp&gt;2pp vs ViT-L/14 @iso-compute</td><td class="l">P3</td></tr>
</table>
<p class="small">† = 推测·未验证（基于文献/历史外推，非本仓实测）。<b>所有 P1 项均为 ~0 GPU·h 的判定性评测</b>，应在启动任何 P2/P3 训练前先完成。</p>
""")

w("""
<h2>7. 结论与替代评测集方案</h2>

<div class="gbox"><b>下一步最该做的一件事（单一建议）</b>：<br>
<b>先做 B4 —— 用 MMBench / MMVet / MathVista + 336/anyres 推理变体，在已有的 ArmB 与 ArmE-R2 Stage-2 ckpt 上重测（~0 GPU·h）。</b><br>
理由：当前 4 臂 ProtB 跨 6.15pp 而 MLLM 跨 0.34pp，且 12 集逐集无一能区分（§2.2）。<b>在不知道「评测能否分辨编码器差异」之前，任何编码器改进（A1–A5）对 MLLM 目标都是盲投。</b>B4 用 ~0 成本即可判定「传递性失效」是真失效还是评测盲区，<b>信息量最大、成本最低</b>。<br>
顺带做 A3（对 ckpt_60000 跑 ProtB，~0.3 GPU·h）——零成本验证 ckpt 选择是否敏感。
</div>

<div class="nbox"><b>分支决策（基于 B4 结果）</b>：
<ul>
<li><b>若更难集 Δ &lt; 2pp（评测/对齐瓶颈）</b>：说明 12 集（含 MMStar/RealWorldQA）已饱和、当前 MLLM 对齐（Stage-2 数据 / projector / LoRA）是瓶颈。→ 转 <b>B1→B2→B3</b>（低成本递进：先全量 Stage-2 数据，再 projector 加长，再 LoRA 全参），<b>暂不放大编码器</b>。同时把<b>评测集换成 MMBench/MMVet/MathVista + anyres</b> 作为新主指标。</li>
<li><b>若更难集 Δ &gt; 2pp（编码器差异被掩盖）</b>：编码器差异真实但被易集掩盖。→ 追投 <b>A1 分辨率 224→336</b>（A 线里唯一可能同时帮 MLLM 文档/细粒度任务的方向），并在新评测集上验证。</li>
</ul>
</div>

<div class="kbox"><b>若判断「当前 12 集测不出编码器差异」——明确说出来 + 替代评测集方案</b>：<br>
<b>本报告判断：当前 12 集（含 MMStar、RealWorldQA）对「ViT-B/16 vs ViT-L/14」这一量级的编码器差异已饱和</b>（证据见 §2.2，逐集最大跨度 1.66pp、多数 &lt;1σ）。<b>建议替代 / 扩充评测集</b>：
<table>
<tr><th>替代集</th><th>为何更敏感</th><th>成本</th></tr>
<tr><td class="l">MMBench (dev)</td><td class="l">多能力维度 + 选项题，区分度高于 MMStar；标准误更可控</td><td>~0.2 GPU·h</td></tr>
<tr><td class="l">MMVet</td><td class="l">开放式综合评分，对模型整体能力差异更敏感</td><td>~0.3 GPU·h</td></tr>
<tr><td class="l">MathVista</td><td class="l">数学视觉推理，对分辨率/细节敏感（224 封顶假设的直接检验）</td><td>~0.2 GPU·h</td></tr>
<tr><td class="l">336 / anyres 推理变体</td><td class="l">同 ckpt 仅推理分辨率↑——直接测「224 单块是否封顶文档/OCR 任务」</td><td>~0.5 GPU·h</td></tr>
</table>
<b>这比继续堆训练实验更有价值</b>：它能区分「编码器不够好」vs「评测看不见 / 推理被封顶」——三者的下一步完全不同。
</div>
""")

w(f"""
<h2>附录 · 数据溯源与诚实条款</h2>
<h3>A.1 数字溯源</h3>
<table>
<tr><th class="l">数字</th><th class="l">来源</th></tr>
<tr><td class="l">ArmE-R2 ProtB lp 68.236±0.0182 / 5-NN 58.904 / per_seed [68.212,68.256,68.240]</td><td class="l"><code>vision/armE_r2_20261022_protb_vitl14_224_results.json</code></td></tr>
<tr><td class="l">4 臂 ProtB（ArmE-R2 68.236 / ArmD-R2 64.337 / ArmC 62.332 / ArmB 62.093）</td><td class="l"><code>EXPERIMENTS_VISION.md §15.3</code> + 各 <code>arm*_protb_*_results.json</code></td></tr>
<tr><td class="l">4 臂 MLLM 12 集 avg（26.10/26.12/25.78/26.10）+ 逐集</td><td class="l"><code>EXPERIMENTS_VISION.md §15.5</code> + 落盘 <code>consolidated_12benchmarks.json</code></td></tr>
<tr><td class="l">逐集标准误</td><td class="l"><code>vision/consolidated_12benchmarks.json</code> (raw_results.*_stderr_clt)</td></tr>
<tr><td class="l">外部参照（CLIP 82.66 / SigLIP2 87.46 / AIMv2 85.22 / OV2 84.97 / RICE 81.72）</td><td class="l"><code>vision/external_protb_results_merged.json</code></td></tr>
<tr><td class="l">best C1 0.9664@s45240 / 末段抖动 / ckpt 滚动删</td><td class="l"><code>EXPERIMENTS_VISION.md §15.2</code> + <code>armE_r2_aimv2_openclip_vitl14.py:339-363</code> + <code>ls .../armE_r2_20261022_.../</code></td></tr>
<tr><td class="l">mask_ratio 0.6 / weight 1:1 已消融最优</td><td class="l"><code>EXPERIMENTS_VISION.md</code> mask-ratio / weight-ratio 节 + BP-2</td></tr>
<tr><td class="l">MLLM 配置（Qwen3-4B / LoRA r=64 / Stage-2 738588 样本）</td><td class="l"><code>report_vision_armE_r2_20261024_zh.html §5</code></td></tr>
</table>

<h3>A.2 诚实条款</h3>
<div class="nbox">
<ul>
<li>所有「预期增益」均为<b>推测·未验证</b>（基于文献 / 历史实验外推），已在汇总表标注 †，<b>不许混进结论</b>。</li>
<li>外部参照（82–87%）均为<b>大规模预训练</b>编码器，本仓为<b>从头训练</b>；14–19pp 差距主因是预训练数据量级，<b>不能归因 loss/架构</b>。</li>
<li>ArmE-R2 vs ArmD-R2 = <b>塔 + LR + warmup 三变量 + 容量混杂</b>（§15），Δ 不得单归因。</li>
<li>「12 集饱和」是基于<b>已实测的 4 臂跨度 + 标准误</b>的判断，但 4 臂中 3 臂是 ViT-B/16（同塔不同配方），仅 ArmE-R2 是 ViT-L/14——<b>样本量小</b>，B4 的更难集评测是必要的正式验证。</li>
<li>本轮<b>不启动任何训练、不动 ArmB/C/D/E 产物</b>（运维令⑥纪律）。</li>
</ul>
</div>
<hr>
<p class="small">本报告由 <code>vision/generate_next_steps_protb_mllm_report.py</code> 生成 · 所有数字来自落盘产物（ProtB json / 12集 consolidated json / EXPERIMENTS_VISION.md / 外部 encoder json / 训练代码），推测项标注「†推测·未验证」。生成时间 {GEN_TS}。<br>
上下文：ArmE-R2 完整实验报告 <code>reports/report_vision_armE_r2_20261024_zh.html</code>（7 节，已交付）；实验记录 <code>EXPERIMENTS_VISION.md §15</code>。</p>
</body></html>
""")

html = "\n".join(H)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

# ---- sanity checks ----
n_script = len(re.findall(r"<script", html, re.I))
n_ext = len(re.findall(r"https?://", html))
n_h2 = len(re.findall(r"<h2>", html))
n_h2c = len(re.findall(r"</h2>", html))
n_table = len(re.findall(r"<table>", html))
n_tablec = len(re.findall(r"</table>", html))
print(f"WROTE {OUT}  ({len(html)} bytes)")
print(f"  <script>={n_script}  external_links={n_ext}")
print(f"  <h2> open/close = {n_h2}/{n_h2c}   <table> open/close = {n_table}/{n_tablec}")
assert n_script == 0, "FORBIDDEN <script>"
assert n_ext == 0, "FORBIDDEN external link"
assert n_h2 == n_h2c, "h2 unbalanced"
assert n_table == n_tablec, "table unbalanced"
print("  sanity OK (0 script, 0 ext link, tags balanced)")
