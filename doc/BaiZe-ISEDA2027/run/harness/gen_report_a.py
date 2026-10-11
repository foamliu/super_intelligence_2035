#!/usr/bin/env python3
"""Generate report_harness_lit_ideas.html"""
import html as H
from pathlib import Path

OUT = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/report_harness_lit_ideas.html")

def esc(s): return H.escape(str(s), quote=True)

papers = [
    {"id":"2610.07898","title":"FC-SWE: Failure-Conditioned RL for Long-Horizon Software Engineering Agents","cat":"cs.LG","date":"2026-10-07","badge":"借鉴","areas":["agent harness"],"summary":"让 SWE 智能体在补丁未通过验证后，把「失败补丁 + 验证器反馈」作为上下文再发起一次修复轨迹并纳入策略训练（改造 GRPO：轨迹级奖励 + 活跃集优势估计）。SWE-bench Verified 全 500 题、Qwen3.5-4B + SWE-agent 下 Resolved@1 41.7% / Resolved@2 52.8%（GRPO 基线 38.9% / 48.5%），≤2 次/链训练在 11 次预算下达 Resolved@11 70.7%。","idea":"把「失败补丁 + 验证器反馈」作为条件上下文再发起修复轨迹，并将其纳入 RL 策略训练（轨迹级奖励，不让恢复步偷主轨迹的奖励）。","relation":"直接对应我们的 agent 循环中的 generate→execute→refine 闭环。可在 BaiZe 后训练的 RL reward 设计中采用其轨迹级奖励 + 活跃集优势估计；在 harness 评测中，可把失败后修复作为一条独立轨迹而非简单 retry。","cost":"中（需读原文复现 FC-SWE 的轨迹级 reward 分配；GRPO 改造需适配我们的 backbone）","risk":"低-中（方法已在 SWE-bench Verified 全 500 题验证，但迁移到不同 backbone/harness 需验证）","price":"约 3-5 人日","verified":"仅灵感","rank":1},
    {"id":"2610.07832","title":"Harness Engineering for SE via Modular Executable Dev-Primitives (HERMES)","cat":"cs.SE","date":"2026-10-07","badge":"借鉴","areas":["agent harness"],"summary":"提出可执行的「开发原语」Dev-Primitives（仓库产物 + 常驻 LLM 的 agent 原生接口）与框架 HERMES，用依赖感知动态激活 + 执行证据回检定位待改组件，缓解长程 SE 任务的上下文爆炸与语义漂移；称在四个 SE 基准上优于对齐 baseline harness。","idea":"把上下文管理从 prompt 技巧提升为结构化、可执行的仓库组件（Dev-Primitives），用依赖感知动态激活 + 执行证据回检定位待改组件。","relation":"正对 harness 架构主线。我们的 7×300 横评已证实 harness 架构差异造成 20pp resolve rate 方差——本文的产物自带 agent 接口抽象可直接启发 cline 的工具集设计；执行证据回检对应我们评测中的 f2p test 反馈循环。","cost":"中-高（需设计 Dev-Primitives 接口规范 + 在目标 repo 上实现适配层）","risk":"中（方法新颖，需验证在 EDA 领域 repo 上的适用性）","price":"约 1-2 人周","verified":"仅灵感","rank":2},
    {"id":"2610.10426","title":"CoTrace: Data Recipes for Training Terminal Agents with Harness-Model Co-Evolution","cat":"cs.CL","date":"2026-10-09","badge":"借鉴","areas":["agent harness"],"summary":"直接研究 terminal agent + harness + SWE-bench / Terminal-Bench，提出 harness-model 协同进化的数据配方。核心论断：训练时必须原生地发生在目标 harness 环境中，推理时才引入 harness 会制造训练-部署错配。","idea":"训练必须原生发生在目标 harness 环境中（harness-model co-evolution），用数据配方控制训练轨迹的 harness 多样性。","relation":"直接对应我们的 harness 横评与 agent 训练。7×300 评测显示同一 backbone 在不同 harness 上 resolve rate 差 20pp——正是训练-部署错配的实证。CoTrace 的数据配方思路可用于 BaiZe 后训练的环境多样性控制。","cost":"中（需在训练管线中嵌入 harness 环境采样 + 设计数据配比策略）","risk":"中（harness 环境嵌入训练管线的基础设施成本较高）","price":"约 1-2 人周","verified":"仅灵感","rank":3},
    {"id":"2610.08402","title":"VETTA: Coordinating Turn- and Token-Level Credit Assignment for Multi-Turn LLM Agents","cat":"cs.LG","date":"2026-10-08","badge":"借鉴","areas":["agent harness"],"summary":"多轮 LLM agent 的信用分配：在共享轻量 critic 上接两个头联合学 turn 级与 token 级价值。ALFWorld/WebShop 上相对 PPO 成功率提升 37.5%/22.3%。","idea":"在多轮 agent 的 RL 中，联合学 turn 级（整段回复）与 token 级（段内决策）信用分配，用共享轻量 critic 降低价值学习成本。","relation":"对应 agent RL reward 设计。cline 轨迹显示平均 10-30 步工具调用——turn 级 reward 不区分段内决策质量，token 级又不显式建模每段信用；VETTA 的双层头设计可直接用于 BaiZe 的多轮 agent RL。","cost":"中（需实现共享 critic + 双头架构 + 修改 PPO 更新逻辑）","risk":"低-中（方法在 ALFWorld/WebShop 验证，critic 轻量化设计降低了实现门槛）","price":"约 3-5 人日","verified":"仅灵感","rank":4},
    {"id":"2610.11959","title":"MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement","cat":"cs.CL","date":"2026-10-11","badge":"借鉴","areas":["后训练","RL 扩展","agentic RL","agent harness"],"summary":"沿三个维度扩 RL 算力：(1) 更大 batch + 更高吞吐（异步训练，每步 1,568 样本 / 2.7-3.7B token，上下文最长 1M）；(2) 更多样更复杂的环境（混合多种 agent harness）；(3) 更多 grader 算力（groupwise agentic grading）。冻结 MoE router + 多层反 reward hacking。","idea":"RL 扩算力的三个轴：批/吞吐、环境多样性（混合多种 harness）、grader 算力（groupwise agentic grading 给长程任务更准 reward）。","relation":"直接命中 BaiZe 后训练与 harness 两条线。7×300 横评本身就是环境多样性的实证——7 种 harness 的 20pp 方差证明 harness 选择影响巨大。MiMo 的 groupwise agentic grading 可用于评测 reward 设计。","cost":"高（需异步训练基础设施 + 多 harness 环境集成 + agentic grader 实现）","risk":"中（工业级报告，可行性已验证，但基础设施投入大）","price":"约 2-4 人周","verified":"仅灵感","rank":5},
    {"id":"2610.12274","title":"HarnessSQL: Harness-Native Training for SQL Agents","cat":"cs.CL","date":"2026-10-10","badge":"借鉴","areas":["agent harness"],"summary":"三要素「可执行环境 + 隐藏 oracle + 只留核验轨迹」是 generate-execute-refine 闭环的可训练化版本。训练必须原生发生在目标 harness。","idea":"训练原生发生在目标 harness，用可执行环境 + 隐藏 oracle + 只留核验轨迹三要素构建可训练的 agent 闭环。","relation":"与 CoTrace 同源思路。三要素中的隐藏 oracle 对应我们评测中的 f2p test；只留核验轨迹对应上下文压缩——只保留验证结果而非完整执行输出。","cost":"中","risk":"中","price":"约 1 人周","verified":"仅灵感","rank":6},
    {"id":"2610.08463","title":"UNREAL: Unifying Retrieval and Long-Context with a Single Model","cat":"cs.CL","date":"2026-10-07","badge":"借鉴","areas":["LLM"],"summary":"从冻结 LLM 内部表示编码文本块并派生检索 query，用同一机制统一语料级检索(RAG)与长上下文证据稀疏推理；自 ~32K token 起降低 FLOPs 与首 token 时延。","idea":"用模型原生证据选择统一检索与长上下文，只喂被选中的证据而非全上下文，降低 prefill 成本。","relation":"对应上下文压缩主线。cline 的 Auto Compact 是 per-provider 白名单——UNREAL 的证据稀疏思路可作为压缩策略的替代：不是摘要全部历史，而是选择性保留高证据价值的历史片段。","cost":"中-高","risk":"中","price":"约 1-2 人周","verified":"仅灵感","rank":7},
    {"id":"2610.08527","title":"PHBA: Prefix-State Hybrid Block Attention","cat":"cs.LG","date":"2026-10-08","badge":"借鉴","areas":["LLM"],"summary":"用 top-k 块稀疏检索替换滑窗注意力，让每个被检索块携带紧凑前缀状态，兼得精确远程证据与压缩历史上下文。","idea":"在混合架构中，用 top-k 块稀疏检索 + 紧凑前缀状态替换固定滑窗，使同一层兼得精确远程证据与压缩历史。","relation":"对应 BaiZe 的 Mamba-2×attention 混合架构与上下文管理。agent 场景下长对话历史的精确回忆与长程聚合的分工可参考 PHBA。","cost":"高","risk":"高","price":"约 2-4 人周","verified":"仅灵感","rank":8},
    {"id":"2610.11247","title":"Why On-Policy Distillation Sometimes Fails: Vanishing Learning Signals","cat":"cs.LG","date":"2026-10-11","badge":"借鉴","areas":["后训练","蒸馏"],"summary":"用更大规模教师做 OPD 会出现早期 loss 平台期（200 次更新后仅降 25.1%），而 self-RL 教师可达 96.2%。","idea":"OPD 不是教师越大越好——self-RL 教师给的学习信号远强于大教师；可用学习信号代理做在线诊断预警平台期。","relation":"对应 BaiZe 后训练。如果用 OPD 把教师能力迁到 2B 主干，应先扫教师规模并配 self-RL 教师基线做对照。","cost":"低-中","risk":"低","price":"约 2-3 人日","verified":"仅灵感","rank":9},
    {"id":"2610.11226","title":"DRQ: Distributionally Robust Refinement for Low-Bit LLM Quantization","cat":"cs.AI","date":"2026-10-11","badge":"借鉴","areas":["高效推理","量化"],"summary":"更低的重构 loss 甚至可能让性能更差。DRQ 在受限输入激活分布上最小化最坏情况重构 loss，可插拔叠加在 AWQ/GPTQ 之后。","idea":"量化后处理用 DRQ 精修整数码——可插拔、不增推理开销。评测纪律：重构 loss 更低 ≠ 下游更好。","relation":"对应 BaiZe 高效推理部署。可直接叠加在 AWQ/GPTQ 流程之后；重构 loss ≠ 下游性能的纪律可用于量化方案评估。","cost":"低","risk":"低","price":"约 1-2 人日","verified":"仅灵感","rank":10},
    {"id":"2610.12466","title":"On the estimation and validity of AI time horizons (METR plot critique)","cat":"cs.AI","date":"2026-10-09","badge":"科普","areas":["eval methodology"],"summary":"对 METR AI 时间跨度翻倍曲线的统计质疑：假设太强、区间内近乎平坦。","idea":"对 AI 能力随时间增长的统计声称要审慎——不同时间跨度的翻倍难度不等。","relation":"对应评测方法论。7×300 横评也面临类似问题：30 条子集 vs 300 条全量的 3.3 倍偏差——子集选择本身就是统计声称的陷阱。","cost":"低","risk":"低","price":"约 0.5 人日","verified":"仅灵感","rank":11},
    {"id":"2610.10620","title":"When AI Finds Hidden Messages, Does It Report?","cat":"cs.CR","date":"2026-10-10","badge":"科普","areas":["AI 诚实性","agent 安全"],"summary":"被要求汇报使无害 ROT13 消息的通报率提高 53.1 个百分点。","idea":"agent 透明性可以被简单的被要求汇报指令大幅提升——从被动检测到主动通报的链路设计。","relation":"对应 agent 安全与透明性。cline 的工具调用中可借鉴主动通报机制——检测到潜在风险操作时主动报告而非静默执行。","cost":"低","risk":"低","price":"约 1 人日","verified":"仅灵感","rank":12},
]

css = """:root{--bg:#f6f8fa;--card:#fff;--border:#d0d7de;--text:#1f2328;--muted:#59636e;--primary:#0b3d6e;--accent:#1f6feb;--ok:#1a7f37;--warn:#9a6700;--bad:#cf222e}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:var(--text);background:var(--bg);line-height:1.7;font-size:15px}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
header.hero{background:linear-gradient(135deg,#0b3d6e 0%,#1f6feb 100%);color:#fff;border-radius:14px;padding:30px 32px;margin-bottom:22px;box-shadow:0 8px 24px rgba(11,61,110,.18)}
header.hero h1{margin:0 0 6px;font-size:24px}
header.hero .sub{font-size:15px;opacity:.95}
header.hero .meta{margin-top:14px;font-size:13px;opacity:.9;display:flex;flex-wrap:wrap;gap:8px 18px}
header.hero .meta span{background:rgba(255,255,255,.14);border-radius:999px;padding:2px 12px}
h2.sec{font-size:19px;margin:34px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--border)}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 22px;margin:16px 0;box-shadow:0 1px 3px rgba(27,31,36,.06)}
.card.top5{border-left:4px solid var(--accent)}
.card h3{margin:0 0 4px;font-size:17px;line-height:1.45}
.card .rank-badge{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;margin-right:8px;border-radius:50%;background:var(--accent);color:#fff;font-size:14px;font-weight:700;vertical-align:middle}
.row{display:flex;gap:10px;margin:7px 0;font-size:14px}
.row .k{flex:0 0 88px;color:var(--muted);font-weight:600}
.row .v{flex:1}
.badge{display:inline-block;padding:1px 10px;border-radius:999px;font-size:12.5px;font-weight:700;vertical-align:middle}
.b-jz{background:#dafbe1;color:var(--ok)}.b-kp{background:#ffeef8;color:#a3238e}
.b-idea{background:#fff8ef;color:var(--warn)}
code{background:#eef1f4;border:1px solid #e1e4e8;border-radius:5px;padding:1px 6px;font-family:Consolas,Menlo,monospace;font-size:12.5px;color:var(--primary)}
a{color:var(--accent);word-break:break-all}
.note{background:#fff8ef;border:1px solid #f0d9b5;border-left:4px solid var(--warn);border-radius:8px;padding:10px 16px;font-size:13px;color:#6a4a00}
.ok-box{background:#f0fff4;border:1px solid #b7f0c5;border-left:4px solid var(--ok);border-radius:8px;padding:10px 16px;font-size:13px;color:#0d5c22}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px;background:var(--card)}
th,td{border:1px solid var(--border);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#eef3f8;color:var(--primary);font-weight:600}
tr:nth-child(even) td{background:#fafbfc}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--border);color:var(--muted);font-size:13px}
.tldr{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--ok);border-radius:8px;padding:14px 18px;margin:16px 0;font-size:14px}
.tldr b{color:var(--primary)}"""

top5_cards = ""
other_cards = ""
for p in papers:
    is_top5 = p["rank"] <= 5
    card_class = "card top5" if is_top5 else "card"
    rank_badge = f'<span class="rank-badge">{p["rank"]}</span>' if is_top5 else f'<span class="rank-badge" style="background:var(--muted)">{p["rank"]}</span>'
    card_html = f'''<div class="{card_class}">
  <h3>{rank_badge} {esc(p["title"])}</h3>
  <div class="row"><div class="k">出处</div><div class="v"><code>{esc(p["id"])}</code> · <a href="https://arxiv.org/abs/{esc(p["id"])}">arXiv:{esc(p["id"])}</a> · {esc(p["date"])} · <span class="badge b-jz">{esc(p["badge"])}</span> · <span class="badge b-idea">仅灵感</span></div></div>
  <div class="row"><div class="k">领域</div><div class="v">{esc(p["cat"])} · {esc(", ".join(p["areas"]))}</div></div>
  <div class="row"><div class="k">一句话</div><div class="v"><b>{esc(p["idea"])}</b></div></div>
  <div class="row"><div class="k">摘要</div><div class="v">{esc(p["summary"][:280])}{"…" if len(p["summary"])>280 else ""}</div></div>
  <div class="row"><div class="k">与本线关系</div><div class="v">{esc(p["relation"])}</div></div>
  <div class="row"><div class="k">借鉴成本</div><div class="v">{esc(p["cost"])}</div></div>
  <div class="row"><div class="k">风险</div><div class="v">{esc(p["risk"])}</div></div>
  <div class="row"><div class="k">价签</div><div class="v">{esc(p["price"])}</div></div>
</div>'''
    if is_top5: top5_cards += card_html
    else: other_cards += card_html

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>文献借鉴报告 · harness 线 · 2026-10-11</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header class="hero">
  <h1>文献借鉴报告：可借鉴 idea 精选</h1>
  <div class="sub">harness 研究线 · 从 research 线 10-07~10-11 共 25 篇论文中提取可借鉴 idea</div>
  <div class="meta">
    <span>2026-10-11</span><span>25 篇 → TOP-5 + 7 备选</span><span>关注面：code agent · harness 架构 · 上下文压缩 · agent RL · SWE-bench 评测</span><span>数据源：research 线 daily HTML + papers.jsonl</span>
  </div>
</header>
<div class="tldr">
<b>HERO 一句话结论</b>：25 篇论文中，对 harness 线<b>最有可执行价值的 TOP-5</b> 聚焦在三条技术线——<b>① agent RL 的 reward 设计</b>（FC-SWE 的失败条件化轨迹级奖励、VETTA 的 turn/token 双层信用分配），<b>② harness 架构的结构化</b>（HERMES 的 Dev-Primitives、CoTrace 的 harness-model 协同进化），<b>③ RL 扩展的工程范式</b>（MiMo-V2.6 的三轴扩展）。其中 FC-SWE 与 VETTA 可直接用于 BaiZe 后训练的 reward 设计；HERMES 与 CoTrace 可指导 harness 架构改进；MiMo-V2.6 给出工业级 RL 扩展路线图。<br><b>全部标注「仅灵感」</b>——数字均为论文自报，未复现。
</div>
<h2 class="sec">方法与口径</h2>
<div class="ok-box">
<b>输入</b>：research 线 <code>doc/personal-watch/run/research/daily/2026-10-07.html</code> … <code>2026-10-11.html</code>（共 25 篇）+ <code>papers.jsonl</code>（186 篇全量）+ <code>TAKEAWAYS.md</code>。<br>
<b>关注面</b>：code agent · harness 架构 · 交互轨迹与上下文压缩 · 工具调用与沙箱 · agent RL（reward 设计）· SWE-bench 类评测协议 · 成本-性能。<br>
<b>筛选标准</b>：按可执行价值排序——① 与 harness 线/BaiZe 后训练的关联度 ② 方法的可操作性 ③ 证据强度。<br>
<b>每条 idea 必带</b>：出处（arXiv ID + URL + 日期）· 一句话 · 与本线关系 · 借鉴成本 · 风险 · 价签。<br>
<b>显著区分</b>：已验证 vs 仅灵感（本批全部为仅灵感——数字为论文自报，未复现）。
</div>
<h2 class="sec">TOP-5（按可执行价值排序）</h2>
{top5_cards}
<h2 class="sec">备选 idea（ranked 6-12）</h2>
{other_cards}
<h2 class="sec">25 篇论文全览（按日期 × badge）</h2>
<table>
<tr><th>日期</th><th>借鉴</th><th>科普</th><th>与本线相关度</th></tr>
<tr><td>2026-10-07</td><td>FC-SWE · HERMES · UNREAL</td><td>Building Rome · World Models Physics</td><td>FC-SWE ★★★ · HERMES ★★★ · UNREAL ★★</td></tr>
<tr><td>2026-10-08</td><td>PHBA · VETTA · Circuit Timing</td><td>Bolzano Proof · FoldBack</td><td>VETTA ★★★ · PHBA ★★</td></tr>
<tr><td>2026-10-09</td><td>CoTrace · 量化诊断 · VPS</td><td>METR Time Horizons</td><td>CoTrace ★★★ · METR ★</td></tr>
<tr><td>2026-10-10</td><td>HarnessSQL · MiMo-V2.6 · OPD · DRQ</td><td>10:10 Clock · AI Hidden Messages</td><td>MiMo ★★★ · HarnessSQL ★★ · OPD ★★ · DRQ ★★</td></tr>
<tr><td>2026-10-11</td><td>MiMo(续) · DRQ(续) · OPD(续)</td><td>Subliminal Learning · Scene Text</td><td>(与 10-10 同批)</td></tr>
</table>
<div class="note">
<b>诚实条款</b>：<br>
① 全部 25 篇论文的数字均为<b>作者自报</b>（未复现），本报告只摘录原文结论，不转抄夸大。<br>
② <b>全部标注「仅灵感」</b>——当前未在 BaiZe/harness 线上验证任何 idea；如需验证，先报运维批准。<br>
③ TOP-5 的排序基于与 harness 线/BaiZe 后训练的关联度 + 可操作性，是人工判断，非量化排序。<br>
④ 12 篇借鉴论文中，5 篇与 harness 线直接相关（FC-SWE / HERMES / CoTrace / VETTA / MiMo），其余 7 篇与 BaiZe 后训练/推理更相关但仍有交叉。<br>
⑤ 13 篇科普论文与本线直接关联弱，已略去详细分析（全量信息见 papers.jsonl）。
</div>
<footer>
harness 线 · 文献借鉴报告 · 2026-10-11 · 自包含单文件 · 内联 CSS · 零外链 · 纯分析（不占 GPU）<br>
数据源：research 线 daily HTML (10-07~10-11) + papers.jsonl + TAKEAWAYS.md · 每条 idea 均带出处 + 关系 + 成本 + 风险 + 价签
</footer>
</div>
</body>
</html>'''

OUT.write_text(html_content, encoding="utf-8")
print(f"Written {OUT} ({len(html_content)} bytes, {len(html_content)/1024:.1f} KB)")
