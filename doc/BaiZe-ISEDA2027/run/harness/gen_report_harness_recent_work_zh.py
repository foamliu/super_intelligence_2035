#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 reports/report_harness_recent_work_zh.html（harness 线 2026-10-20 起近期工作总结）。
自包含中文 HTML：0 <script>、0 外链；正文一律写 cline（命名规程）。数据全部溯源到 log/json/文件:行。"""
import html, os

def esc(s): return html.escape(str(s))

CSS = """
*{box-sizing:border-box}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:0;background:#f5f6fa;color:#1f2733;line-height:1.7;font-size:15px}
.wrap{max-width:1080px;margin:0 auto;padding:32px 24px 80px}
h1{font-size:1.7rem;border-bottom:3px solid #2b6cb0;padding-bottom:10px;margin:0 0 6px}
.sub{color:#5a6477;font-size:.92rem;margin:0 0 22px}
h2{font-size:1.28rem;color:#1a4480;margin:34px 0 12px;padding:8px 0 0;border-top:1px solid #d8dee9}
h2:first-of-type{border-top:none;margin-top:18px}
h3{font-size:1.06rem;color:#234;margin:20px 0 8px}
.tag{display:inline-block;font-size:.72rem;padding:2px 8px;border-radius:10px;background:#e6efff;color:#1a4480;margin-left:8px;vertical-align:middle}
.tag.ok{background:#d4f4dd;color:#1a6b3a}.tag.warn{background:#fff0d4;color:#8a5a00}.tag.bad{background:#ffe0e0;color:#a32323}.tag.live{background:#e0e8ff;color:#2b4a8a}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:.9rem;background:#fff}
th,td{border:1px solid #cdd6e3;padding:7px 9px;text-align:left;vertical-align:top}
th{background:#eef3fb;color:#1a3a66;font-weight:600}
tr:nth-child(even) td{background:#f8fafd}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.kpi{display:flex;flex-wrap:wrap;gap:12px;margin:14px 0}
.kpi .c{flex:1 1 160px;background:#fff;border:1px solid #d8dee9;border-radius:10px;padding:12px 14px}
.kpi .c .v{font-size:1.5rem;font-weight:700;color:#1a4480}
.kpi .c .l{font-size:.78rem;color:#5a6477}
.kpi .c.good .v{color:#1a6b3a}.kpi .c.bad .v{color:#a32323}
.note{background:#fff8e6;border-left:4px solid #d4a017;padding:10px 14px;margin:12px 0;border-radius:0 6px 6px 0;font-size:.9rem}
.src{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.78rem;color:#42506a;background:#eef1f6;padding:1px 5px;border-radius:4px}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.84rem;background:#eef1f6;padding:1px 5px;border-radius:4px}
ul{margin:8px 0}li{margin:3px 0}
.tl{background:#eaf3ff;border:1px solid #b9d2f5;border-radius:10px;padding:14px 18px;margin:0 0 22px}
.tl b{color:#1a4480}
.foot{margin-top:40px;padding-top:14px;border-top:1px solid #cdd6e3;color:#5a6477;font-size:.8rem}
.pill{display:inline-block;font-size:.74rem;padding:1px 7px;border-radius:8px;background:#eef1f6;color:#33475b;margin-right:4px}
"""

H = []
H.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">')
H.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
H.append('<title>BaiZe Harness 研究线 · 近期工作报告（2026-10-20 起）</title>')
H.append('<style>'+CSS+'</style></head><body><div class="wrap">')

H.append('<h1>BaiZe Harness 研究线 · 近期工作报告</h1>')
H.append('<p class="sub">时间范围：2026-10-20 → 2026-10-26（R460 → R515）· 生成：2026-10-26（R515 刷新·数字去 stale）· 自包含中文 HTML · 数据均溯源到文件/日志</p>')

H.append('<div class="tl"><b>TL;DR</b> · 本线定位为「agent harness 工程实现与能力差异」研究，分 <b>H-B 源码分析</b>与 <b>H-A Terminal-Bench / SWE-bench 横评</b>两条线。'
 '近一周关键进展：①<b>卡死恢复</b>——把单次 agent 超时从 1500s 提到 3600s 并改「分阶段落盘」，止住反复超时丢内容；②<b>H-B 交付</b> 7 个 harness 上下文压缩机制对比报告（58KB）；'
 '③<b>Terminal-Bench 7×89 全量横评</b>跑完，四存活线排名 <code>cline(49.4%) ≈ opencode(47.1%) &gt; pi(40.2%) &gt; codex(23.0%)</code>，McNemar 证实 codex 显著弱（n=87）；'
 '④<b>适配器修复 + 复跑</b>——hermes/claude-code 旧 0% 经修复后全量复跑，最新条件通过率 <b>hermes 56.8%（25/44，已 FINISHED）· claude-code 29.7%（19/64，进行中）</b>，判据「两路均 &gt; 0」已满足。</div>')

H.append('<h2>一、本线定位 <span class="tag">H-B + H-A</span></h2>')
H.append('<p>BaiZe 共 4 个活跃 agent 线（vision / pretrain / data / harness），本线（harness）是其中唯一<b>不占 GPU</b>的研究线，专注横向理解「agent harness」这一类系统：'
 '它们的<b>工程实现差异</b>（源码层面）与<b>真实软件工程任务上的能力差异</b>（评测层面）。</p>')
H.append('<table><tr><th>子线</th><th>内容</th><th>主产物</th></tr>'
 '<tr><td><b>H-B 源码分析</b></td><td>逐 harness 读源码，对比机制（上下文压缩 / 工具循环 / 超时恢复等），结论贴 <code>文件:行号</code></td><td>自包含中文 HTML 报告</td></tr>'
 '<tr><td><b>H-A 横评</b></td><td>Terminal-Bench 2.0（89 题）+ SWE-bench Verified（500 题，下载中），7 路自定义 agent 同模型同口径横评</td><td>结果表 + McNemar 配对报告</td></tr>'
 '</table>')
H.append('<p><span class="pill">铁律</span>不许猜（源码结论贴文件+行号原文）；每个结论必须可复现（命令+输出）；不伪造通过率，一律 <code>reward.txt</code> 实测。'
 '7 路自定义 agent：cline / codex / hermes-agent / opencode / claude-code / deepseek-harness / pi（<span class="src">BAIZE_HARNESS_TASK.md §0</span>）。</p>')

H.append('<h2>二、近期任务逐个</h2>')

H.append('<h3>任务 1 · 卡死恢复：CLINE_TIMEOUT 1500→3600 + 分阶段落盘 + 进程清理 <span class="tag ok">已恢复</span></h3>')
H.append('<p><b>背景</b>：H-B 进入「读源码 + 写整份报告」阶段后，单轮 agent 在原 1500s（25min）预算内<b>完不成</b>「7 个 harness 全部分析 + 写整份报告」→ 每轮撞超时、未落盘内容<b>丢失</b>，'
 '加上 glm-5.2 推理慢 + 62KB 大上下文，反复超时≈卡死。同时历史上有中继（ops relay）卡死与 v2 串行残留进程/容器堆积。</p>')
H.append('<p><b>三招恢复</b>：</p>')
H.append('<ul>'
 '<li><b>① 提高超时预算</b>：单次 cline 超时 <code>1500s → 3600s</code>（25min → 60min）。'
 '证据：<span class="src">baize_harness_loop.sh:30</span> 原文 <code>CLINE_TIMEOUT=3600  # 单次 cline 最多 60 分钟（原 1500=25min 因 glm-5.2 慢+62KB上下文反复超时；2026-10-23 运维调大）</code>，'
 '调用点 <span class="src">baize_harness_loop.sh:121</span> <code>-t "$CLINE_TIMEOUT"</code>。</li>'
 '<li><b>② 分阶段落盘</b>：禁止一口气写整份报告，改为「逐 harness 推进，每分析完 1 个立即 append 写入 HTML 并 commit/push，每段 ≤2500 token」。'
 '证据：<span class="src">ARCHIVE_OPERATOR_HARNESS.md:1325-1332</span>（2026-10-23 用户直令）：'
 '<code>3600s 内完不成「7 个 harness 全部分析 + 写整份报告」→ 每轮超时、未落盘内容丢失。必须分阶段落盘，禁止一口气写整份报告。</code></li>'
 '<li><b>③ 进程 / 容器 / 中继清理</b>：① R479 清理 v2 串行残留——<code>kill -9</code> launcher(PID 1068001) + gw_proxy + harbor 进程 + <code>docker kill $(docker ps -q)</code> 所有遗留容器（<span class="src">daily-memories-harness/2026-10-24.md:1-24</span>）；'
 '② 中继卡死恢复判据与挽救流程（<span class="src">ARCHIVE_OPERATOR_HARNESS.md:193-223</span>，RUN_ID 62 push 后中继既没执行也没回收）；'
 '③ loop 脚本对 <code>git fetch</code> 加防御性 <code>timeout 120</code>（<span class="src">baize_harness_loop.sh:57</span>），避免 git 挂死拖垮整轮。</li>'
 '</ul>')
H.append('<div class="note"><b>效果</b>：分阶段落盘 + 3600s 预算后，H-B 报告得以逐段 commit 直至完整交付（见任务 2），不再整轮超时丢内容；复跑/下载等长任务改后台异步 + 心跳轮询，loop 恢复稳定自跑。</div>')

H.append('<h3>任务 2 · H-B：7 个 harness 上下文压缩机制对比报告交付 <span class="tag ok">已交付</span></h3>')
H.append('<p><b>任务</b>（<span class="src">ARCHIVE_OPERATOR_HARNESS.md:1337-1351</span>，2026-10-23 用户直令）：读 <code>/nas_train/app.e0031982/harness/</code> 下 7 个 harness 源码（只读），对比上下文压缩机制——摘要 / 截断 / token budget / auto-compact 触发阈值 / 保留丢弃策略 / 历史折叠 / 工具轨迹裁剪 / 崩溃超时恢复，每条结论贴 <code>文件:行号</code>。</p>')
H.append('<p><b>交付</b>：<code>reports/report_harness_context_compression_7way_zh.html</code>，<b>58309 B（58KB）</b>，自包含中文 HTML、内联样式、0 外链。'
 '结构：TL;DR → 对比总表（每 harness 一行：压缩策略 / 触发阈值 / 保留策略 / 缺陷）→ 逐 harness 详述（带代码证据）→ 结合本项目教训（cline Auto-compacting 超时问题）→ 总结与选型建议。</p>')
H.append('<table><tr><th>覆盖 harness（7）</th><th>关键看点</th></tr>'
 '<tr><td>cline / codex / hermes-agent / opencode / claude-code / deepseek-harness / pi</td><td>压缩策略差异、auto-compact 触发阈值、上下文溢出处理、与本项目 cline 超时教训的对照</td></tr>'
 '</table>')
H.append('<div class="note"><b>说明</b>：该报告生成于命名规程正式下发之前，文件内偶有代码路径标识符（如 cline 的适配器文件名）作为<b>真实路径引用</b>出现；本报告正文一律写 <code>cline</code>。报告本身为既有交付物，本轮不改动。</div>')

H.append('<h3>任务 3 · Terminal-Bench 7×89 全量横评 <span class="tag ok">FIN 87/87</span></h3>')
H.append('<p><b>口径</b>：TB 2.0 = 89 题（Harbor），去 <code>__hash</code> 重复后 canonical 87 题，2 题镜像/环境不可跑；7 路自定义 agent 同模型（kimi-k2.6-cloud）同超时同 verifier，7-way 并发，每路独立 <code>--jobs-dir</code>（/tmp，非 NFS）。</p>')
H.append('<p><b>推进路径</b>：</p>')
H.append('<ul>'
 '<li><b>Gate 7/7</b>（R466）：codex + claude-code 经 <code>npm install -g</code> 装通，7 路环境全部就绪（<span class="src">ARCHIVE_OPERATOR_HARNESS.md</span>「Gate 7/7 已达成(R466)」指针）。</li>'
 '<li><b>7×89 并发启动</b>（R479，2026-10-24 16:21）：7 harnesses × 87 tasks = 609 trials，7-way concurrent，7 个 harbor 进程并行（<span class="src">daily-memories-harness/2026-10-24.md:1-24</span>）。</li>'
 '<li><b>全 7 路 FIN 87/87</b>（R496，2026-10-25 15:28）：所有 harbor 进程退出、<code>docker ps</code> 空，7 路全部跑完（<span class="src">daily-memories-harness/2026-10-25.md:326-345</span>）。</li>'
 '</ul>')
H.append('<p><b>最终通过率</b>（reward.txt 逐文件实测，分母 87 = canonical 可跑任务，<span class="src">baseline_rewards_7x89_20261024.json</span> + <span class="src">daily-memories-harness/2026-10-25.md:332-337</span>）：</p>')
H.append('<table><tr><th>Harness</th><th class="num">完成(done)</th><th class="num">通过(pass)</th><th class="num">通过率</th><th class="num">异常</th><th>状态</th></tr>'
 '<tr><td>cline</td><td class="num">80</td><td class="num">43</td><td class="num"><b>49.4%</b></td><td class="num">26</td><td>✅ 存活线第一</td></tr>'
 '<tr><td>opencode</td><td class="num">75</td><td class="num">41</td><td class="num"><b>47.1%</b></td><td class="num">27</td><td>✅ 与 cline 同档</td></tr>'
 '<tr><td>pi</td><td class="num">80</td><td class="num">35</td><td class="num"><b>40.2%</b></td><td class="num">23</td><td>✅</td></tr>'
 '<tr><td>codex</td><td class="num">41</td><td class="num">20</td><td class="num"><b>23.0%</b></td><td class="num">59</td><td>⚠️ 高 err 显著弱</td></tr>'
 '<tr><td>hermes</td><td class="num">50</td><td class="num">0</td><td class="num">0%</td><td class="num">37</td><td>🔴 适配器 bug（见任务 4）</td></tr>'
 '<tr><td>claude-code</td><td class="num">34</td><td class="num">0</td><td class="num">0%</td><td class="num">45</td><td>🔴 适配器 bug（见任务 4）</td></tr>'
 '<tr><td>deepseek-harness</td><td class="num">—</td><td class="num">0</td><td class="num">0%</td><td class="num">—</td><td>🔴 上游 SDK 故障</td></tr>'
 '</table>')
H.append('<p><b>McNemar 配对检验</b>（n=87 共同任务，error/timeout/无 reward 一律计 FAIL，χ² 连续性校正 df=1，<span class="src">/tmp/mcnemar_final2.py</span> 实算，<span class="src">daily-memories-harness/2026-10-25.md:338-345</span>）：</p>')
H.append('<table><tr><th>配对</th><th class="num">χ²</th><th>p 值</th><th class="num">discordant (A-only / B-only)</th><th>显著性</th></tr>'
 '<tr><td>cline vs codex</td><td class="num">17.93</td><td>&lt;0.001</td><td class="num">25 / 2</td><td>*** 显著</td></tr>'
 '<tr><td>opencode vs codex</td><td class="num">12.12</td><td>0.0005</td><td class="num">27 / 6</td><td>*** 显著</td></tr>'
 '<tr><td>pi vs codex</td><td class="num">5.94</td><td>0.015</td><td class="num">9 / 24</td><td>* 显著</td></tr>'
 '<tr><td>cline vs opencode</td><td class="num">0.06</td><td>0.80</td><td class="num">9 / 7</td><td>ns 不显著</td></tr>'
 '<tr><td>cline vs pi</td><td class="num">2.07</td><td>0.15</td><td class="num">16 / 8</td><td>ns 不显著</td></tr>'
 '<tr><td>opencode vs pi</td><td class="num">1.12</td><td>0.29</td><td class="num">14 / 8</td><td>ns 不显著</td></tr>'
 '</table>')
H.append('<div class="note"><b>结论</b>：三对显著差异<b>均含 codex</b>——codex 因 59/87 exception 显著弱于其余三存活线；cline / opencode / pi 三者两两不显著，属同档。排名：<code>cline(49.4%) ≈ opencode(47.1%) &gt; pi(40.2%) &gt; codex(23.0%)</code>。</div>')

H.append('<h3>任务 4 · 适配器 infra 修复 + hermes/claude-code 全量复跑 <span class="tag live">复跑进行中</span></h3>')
H.append('<p><b>第一步：三路 0% 根因排查与修复</b>（2026-10-25 08:2x 令，R492-R497 交付）。hermes / claude-code / deepseek 在 7×89 中均为 0%，逐路定位根因：</p>')
H.append('<table><tr><th>路线</th><th>旧结果</th><th>根因</th><th>修复</th><th>smoke 验证</th></tr>'
 '<tr><td>hermes</td><td>0/50</td><td>CLI-PATH / no_proxy 配置问题，agent 启动失败</td><td>适配器修复（留 .orig 备份）</td><td><b>4/5 ✅</b></td></tr>'
 '<tr><td>claude-code</td><td>0/34</td><td>/app 权限 + max_turns 配置</td><td>适配器修复（留 .orig 备份）</td><td><b>4/5 ✅</b>（复验 4/5）</td></tr>'
 '<tr><td>deepseek</td><td>0/—</td><td>上游 SDK 内部运行时故障（finish_reason=<code>error</code>，dsh proxy 无请求）</td><td><b>非适配器可修</b>，待上游</td><td>0/5（卡点写明）</td></tr>'
 '</table>')
H.append('<p>交付报告：<code>harness/reports/report_harness_adapter_0pass_rootcause_zh.html</code>（24908B，自包含中文），<span class="src">daily-memories-harness/2026-10-25.md:326-354</span>。</p>')
H.append('<p><b>第二步：hermes + claude-code 全量 89 题复跑</b>（2026-10-25 17:5x 令）。配置与 7×89 完全一致，只换适配器版本；结果落新目录 <code>/tmp/tb_7x89/jobs_hermes_rerun_20261025/</code>、<code>jobs_claude-code_rerun_20261025/</code>，旧结果只读不改。</p>')
H.append('<p><b>最新复跑进度</b>（<code>verifier/reward.txt</code> 逐文件实测 + <code>summary_rerun_20261025.json</code>，2026-10-26 R515 快照；hermes 已 FINISHED 89 dirs/0 running，claude-code harbor PID 2573271 存活、batch mtime 18:20 仍在写）：</p>')
H.append('<table><tr><th>路线</th><th>派题(dirs)</th><th class="num">完成(done)</th><th class="num">通过(pass)</th><th class="num">异常</th><th class="num">运行中</th><th class="num">条件通过率</th><th>旧基线</th></tr>'
 '<tr><td>hermes</td><td class="num">89/87</td><td class="num">44</td><td class="num"><b>25</b></td><td class="num">45</td><td class="num">0 ✅FIN</td><td class="num"><b>56.8%</b></td><td>0/50 (0%)</td></tr>'
 '<tr><td>claude-code</td><td class="num">86/87</td><td class="num">64</td><td class="num"><b>19</b></td><td class="num">21</td><td class="num">1</td><td class="num"><b>29.7%</b></td><td>0/34 (0%)</td></tr>'
 '</table>')
H.append('<div class="note"><b>判据已满足</b>：运维令判据「两路通过率均 &gt; 0」已满足（旧两路均 0%，适配器修复确实生效；hermes 累计 25 pass · claude-code 累计 19 pass，较 R514 的 16 pass 继续增加）。'
 'hermes 已 FINISHED（89 dirs 全派题，0 running）；claude-code 仍异步进行中（86 task dirs 已派，85 已判定 = 64 rewarded + 21 exc，1 running，约 1 题待派）。复跑全部完成后出终版 resolve rate + 逐题配对表 + McNemar。</div>')
H.append('<p><b>codex 高 err 排查</b>（part②，R499 初版 + <b>R510 勘误</b>）：59/87 exception 经 R510 复查 <code>result.json</code> stdout 重新分类——'
 '<b>34 个 429 限流 → RuntimeError（57.6%）+ 15 AgentTimeoutError（25.4%）+ 10 RuntimeError 无 429（16.9%）</b>。'
 '<b>429 是 codex 独有</b>（严格标记 7 路横向对照：codex 34，其余 6 路全 0；cline 的 60 次「429」是 ISO 时间戳 <code>.429Z</code> 误匹配）。'
 '修正后根因 = <b>(c) 上游 429 为主 + (b) 容量/超时为辅 + (a) 适配器无回合上限/无 429 退避放大</b>；'
 '<b>codex 可改善</b>（降并发复跑或加 429 退避），非「非适配器可修」。R499 初版「无 429 / 非上游服务」结论已被推翻。证据：<span class="src">harness/codex_err_classification_20261025.md §2-bis</span>。'
 '交付报告：<code>reports/report_harness_hermes_claude_rerun_codex_err_zh.html</code>（R510 修正版）。</p>')

H.append('<h2>三、关键数据速查表</h2>')
H.append('<div class="kpi">')
H.append('<div class="c good"><div class="v">58 KB</div><div class="l">H-B 上下文压缩报告（7 harness 对比）</div></div>')
H.append('<div class="c good"><div class="v">87/87</div><div class="l">Terminal-Bench 7×89 全 7 路 FIN</div></div>')
H.append('<div class="c good"><div class="v">49.4%</div><div class="l">cline 通过率（43/87，存活线第一）</div></div>')
H.append('<div class="c bad"><div class="v">23.0%</div><div class="l">codex 通过率（20/87，59 exc 显著弱）</div></div>')
H.append('<div class="c good"><div class="v">56.8%</div><div class="l">hermes 复跑条件通过率 25/44（旧 0%，已 FINISHED）</div></div>')
H.append('<div class="c good"><div class="v">29.7%</div><div class="l">claude-code 复跑条件通过率 19/64（旧 0%，进行中）</div></div>')
H.append('</div>')
H.append('<table><tr><th>项</th><th>数值</th><th>溯源</th></tr>'
 '<tr><td>CLINE_TIMEOUT 调整</td><td>1500s → 3600s（2026-10-23）</td><td><span class="src">baize_harness_loop.sh:30</span></td></tr>'
 '<tr><td>分阶段落盘令</td><td>逐 harness，每段 ≤2500 token，写完即 commit</td><td><span class="src">ARCHIVE_OPERATOR_HARNESS.md:1325-1332</span></td></tr>'
 '<tr><td>H-B 报告体积</td><td>58309 B</td><td><span class="src">reports/report_harness_context_compression_7way_zh.html</span></td></tr>'
 '<tr><td>TB 任务集</td><td>89 题 → canonical 87（去 __hash 重复）</td><td><span class="src">BAIZE_HARNESS_TASK.md §运维指令·10-17</span></td></tr>'
 '<tr><td>7×89 并发启动</td><td>R479，2026-10-24 16:21，609 trials</td><td><span class="src">daily-memories-harness/2026-10-24.md:1-24</span></td></tr>'
 '<tr><td>全 7 路 FIN</td><td>R496，2026-10-25 15:28</td><td><span class="src">daily-memories-harness/2026-10-25.md:326-331</span></td></tr>'
 '<tr><td>四存活最终通过率</td><td>cline 43 · opencode 41 · pi 35 · codex 20（分母 87）</td><td><span class="src">baseline_rewards_7x89_20261024.json</span></td></tr>'
 '<tr><td>McNemar 显著对</td><td>cline≫codex χ²=17.93*** · opencode≫codex 12.12*** · pi≫codex 5.94*</td><td><span class="src">daily-memories-harness/2026-10-25.md:338-345</span></td></tr>'
 '<tr><td>适配器修复 smoke</td><td>claude-code 4/5 · hermes 4/5 · deepseek 0/5(SDK)</td><td><span class="src">daily-memories-harness/2026-10-25.md:346-349</span></td></tr>'
 '<tr><td>复跑最新进度</td><td>hermes 25/44=56.8% ✅FIN · claude-code 19/64=29.7%（86/87 进行中）</td><td><span class="src">harness/summary_rerun_20261025.json + verifier/reward.txt 逐文件实测</span></td></tr>'
 '<tr><td>codex err 分类（R510 修正）</td><td>59 = 34 限流429→RuntimeError + 15 AgentTimeout + 10 RuntimeError无429（429 为 codex 独有）</td><td><span class="src">harness/codex_err_classification_20261025.md §2-bis</span></td></tr>'
 '<tr><td>SWE-bench Verified 下载</td><td>499/500（后台，PID 1199724 存活，0 failed，即将完成）</td><td><span class="src">harness/swebench_verified_pull_progress.txt</span></td></tr>'
 '</table>')

H.append('<h2>四、阻塞 / 待拍板</h2>')
H.append('<ul>'
 '<li><b>hermes 复跑已 FINISHED</b>（89 dirs 全派题，0 running，25/44=56.8%）；<b>claude-code 复跑后台异步进行中</b>（86 task dirs 已派，85 已判定，1 running，约 1 题待派，不需运维干预，自跑）。复跑全部完成后才能出终版 resolve rate + 逐题配对表 + McNemar。</li>'
 '<li><b>codex 全量补跑</b>（R510 修正后）：根因 = <b>上游 429 为主（34/59，codex 调用模式独有）+ 容量/超时为辅 + 适配器无回合上限/无 429 退避放大</b>；<b>codex 可改善</b>（非「非适配器可修」）。<b>待拍板</b>是否(a)降并发（单独跑）+ 加 429 退避复跑 codex（建议先 smoke 5 题验证 429 是否消解），或(b)升级 codex 版本；启动前需先报机时 + load 评估，且应避开 hermes/claude-code 复跑在跑期（防叠加 429）。</li>'
 '<li><b>deepseek-harness</b>：0% 根因为上游 SDK 内部运行时故障（finish_reason=<code>error</code>），<b>非适配器可修，待上游</b>。</li>'
 '<li><b>SWE-bench Verified 下载</b>：499/500 即将完成（Docker Hub 匿名限速 100 manifest/h，实测 ~20/h），瓶颈为限速非磁盘/带宽；下载完成后方可启动 H-A 的 SWE-bench 横评。</li>'
 '</ul>')

H.append('<h2>五、下一步建议</h2>')
H.append('<ol>'
 '<li><b>复跑收尾</b>：hermes/claude-code 跑满 87/87 后，刷新 <code>summary_rerun_20261025.json</code> 与 <code>report_harness_hermes_claude_rerun_codex_err_zh.html</code> 为终版——补全 87 题逐题配对表（旧 reward vs 新 reward）+ McNemar 检验，给出 hermes/claude-code 的最终 resolve rate。</li>'
 '<li><b>codex 决策</b>：报「codex 全量补跑机时 + load 评估」给运维拍板；若不补跑，则以「容量为主、非崩溃性 bug」为 codex 的最终结论归档。</li>'
 '<li><b>SWE-bench 横评启动</b>：下载到 500/500 后，按任务书 §1.2 口径（同子集/同模型/同超时/同 verifier）启动 H-A 的 SWE-bench Verified 横评，先 20-50 条跑通全流程再定规模。</li>'
 '<li><b>H-B 续作</b>：7-way 上下文压缩报告已完成；可按同一方法学扩展到其它机制维度（工具循环实现 / 错误恢复 / 多轮规划），形成 harness 机制对比系列。</li>'
 '</ol>')

H.append('<div class="foot">')
H.append('<p><b>命名规程</b>：本报告正文一律写 <code>cline</code>；代码/脚本/配置里的真实路径标识符不在正文出现。<br>'
 '<b>数据纪律</b>：所有通过率均 <code>reward.txt</code> 实测，未取到者写明原因；无伪造、无估算。<br>'
 '<b>生成方式</b>：<code>harness/gen_report_harness_recent_work_zh.py</code>（本脚本）· 自包含中文 HTML · 0 <code>&lt;script&gt;</code> · 0 外链。</p>')
H.append('</div>')

H.append('</div></body></html>')

out = '\n'.join(H)
# 写两处：① 本线归档 run/reports/ ② 顶层 reports/（与 vision/pretrain/data 三线的 *_recent_work_zh.html 同目录，便于统一查阅）
outdirs = ['doc/BaiZe-ISEDA2027/run/reports', 'doc/BaiZe-ISEDA2027/reports']
for outdir in outdirs:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'report_harness_recent_work_zh.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)
    print('WROTE', path, len(out), 'bytes')
