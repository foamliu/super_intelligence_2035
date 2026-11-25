#!/usr/bin/env python3
"""Generate math & code datasets survey report (Chinese HTML)."""
import html, os, json, sys

REPORT_PATH = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/reports/report_data_math_code_datasets_survey_zh.html"

# Load all probe data from the JSONL files
datasets = []
for f in ["/tmp/dataset_probe_results.jsonl", "/tmp/survey_probe_results.jsonl"]:
    if os.path.exists(f):
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    datasets.append(json.loads(line))

# Also load reprobe results
for f in ["/tmp/reprobe2_results.jsonl"]:
    pass  # we ran it inline, data is in stdout

# Manually curated dataset info with all details
curated = [
    {"name":"MegaMath","repo":"IFM/MegaMath (≡ LLM360/MegaMath)","domain":"数学","usage":"预训练","size":"1,041 GB","lang":"en","license":"odc-by","validator":"否","recommend":"★★★★★ 已下","evidence":"sha=3cbc646, 5317 files, 6子集","notes":"第一批已下web-pro+code+qa+text-code-block+translated-code"},
    {"name":"Nemotron-CC-Math-v1","repo":"nvidia/Nemotron-CC-Math-v1","domain":"数学","usage":"预训练","size":"242 GB","lang":"en","license":"other","validator":"否","recommend":"★★★★★","evidence":"sha=397a250, 196 files, 3子集:3/4plus/4plus_MIND","notes":"ICLR2026, MATH+4.8~12.6, 已超越MegaMath; license=other需核实"},
    {"name":"FineMath","repo":"HuggingFaceTB/finemath","domain":"数学","usage":"预训练","size":"139 GB","lang":"en","license":"odc-by","validator":"否","recommend":"★★★★","evidence":"sha=e92b25a, 293 files, 5子集","notes":"HuggingFaceTB出品, 4-plus质量更高"},
    {"name":"OpenWebMath","repo":"open-web-math/open-web-math","domain":"数学","usage":"预训练","size":"25.5 GB","lang":"en","license":"odc-by","validator":"否","recommend":"★★★","evidence":"sha=fde8ef8, 121 files","notes":"MegaMath web子集已覆盖类似来源"},
    {"name":"MathPile","repo":"GAIR/MathPile","domain":"数学","usage":"预训练","size":"6.9 GB","lang":"en","license":"cc-by-nc-sa-4.0","validator":"否","recommend":"★★","evidence":"sha=bde88d8, 45 files","notes":"⚠️ 非商业license"},
    {"name":"OpenMathInstruct-2","repo":"nvidia/OpenMathInstruct-2","domain":"数学","usage":"SFT","size":"11.8 GB","lang":"en","license":"cc-by-4.0","validator":"是(答案可验)","recommend":"★★★★★","evidence":"sha=469216e, 59 files","notes":"14M Q-A, 自带答案验证→RLVR可用"},
    {"name":"NuminaMath-1.5","repo":"AI-MO/NuminaMath-1.5","domain":"数学","usage":"SFT","size":"0.49 GB","lang":"多语言","license":"apache-2.0","validator":"是(答案可验)","recommend":"★★★★","evidence":"sha=1b05109, 5 files","notes":"竞赛级; ⚠️可能含AIME题→污染检查"},
    {"name":"OpenR1-Math-220k","repo":"open-r1/OpenR1-Math-220k","domain":"数学","usage":"SFT/RL","size":"11.8 GB","lang":"en","license":"apache-2.0","validator":"是(答案可验)","recommend":"★★★★","evidence":"sha=e4e141e, 63 files","notes":"长思维链, SFT+RL两用"},
    {"name":"MetaMathQA","repo":"meta-math/MetaMathQA","domain":"数学","usage":"SFT","size":"0.37 GB","lang":"en","license":"mit","validator":"是(答案可验)","recommend":"★★★","evidence":"sha=aa4f34d, 3 files","notes":"⚠️含GSM8K/MATH改写→需去重"},
    {"name":"Orca-Math-200K","repo":"microsoft/orca-math-word-problems-200k","domain":"数学","usage":"SFT","size":"0.08 GB","lang":"en","license":"mit","validator":"是(答案可验)","recommend":"★★","evidence":"sha=29255d1, 3 files","notes":"GPT-4生成应用题"},
    {"name":"MathInstruct","repo":"TIGER-Lab/MathInstruct","domain":"数学","usage":"SFT","size":"0.2 GB","lang":"en","license":"mit","validator":"混合","recommend":"★★","evidence":"sha=b4fdc32, 3 files","notes":"聚合13个数学指令集"},
    {"name":"IFM Math-Reasoning","repo":"IFM/Math-Reasoning","domain":"数学","usage":"SFT","size":"4,462 GB","lang":"en","license":"apache-2.0","validator":"否","recommend":"★★★★ 已排下","evidence":"sha=e249295, 2228 files, 5子集","notes":"K2 Horizon, reason not recall; 4.5TB巨大"},
    {"name":"The Stack v2","repo":"bigcode/the-stack-v2","domain":"代码","usage":"预训练","size":"397.6 GB","lang":"多语言","license":"other","validator":"否","recommend":"★★★(已用v3)","evidence":"sha=e565caa, 921 files","notes":"🚫禁下; 已用stack-v3-train替代"},
    {"name":"IFM Code-Reasoning","repo":"IFM/Code-Reasoning","domain":"代码","usage":"SFT","size":"3,277 GB","lang":"en","license":"apache-2.0","validator":"否","recommend":"★★★★ 已排下","evidence":"sha=e971bd7, 1637 files, 7子集","notes":"K2 Horizon, 含思维链和直接解"},
    {"name":"OpenCodeReasoning","repo":"nvidia/OpenCodeReasoning","domain":"代码","usage":"SFT/RL","size":"9.06 GB","lang":"en","license":"cc-by-4.0","validator":"是(单测可跑)","recommend":"★★★★★","evidence":"sha=20a1ca1, 42 files, 2子集","notes":"NVIDIA, 自带单测→RLVR直接用"},
    {"name":"OpenCodeInstruct","repo":"nvidia/OpenCodeInstruct","domain":"代码","usage":"SFT","size":"6.39 GB","lang":"en","license":"cc-by-4.0","validator":"是(单测可跑)","recommend":"★★★★","evidence":"sha=8f3ba5b, 52 files","notes":"NVIDIA, 代码指令+执行验证"},
    {"name":"self-oss-instruct-50k","repo":"bigcode/self-oss-instruct-sc2-exec-filter-50k","domain":"代码","usage":"SFT","size":"0.08 GB","lang":"en","license":"odc-by","validator":"是(执行过滤)","recommend":"★★★","evidence":"sha=356bb06, 3 files","notes":"BigCode, 经执行过滤"},
    {"name":"APPS","repo":"codeparrot/apps","domain":"代码","usage":"SFT/评测","size":"1.3 GB","lang":"en","license":"mit","validator":"是(单测可跑)","recommend":"★★★","evidence":"sha=21e74dd, 5 files","notes":"⚠️含测试集→train only"},
    {"name":"CodeContests","repo":"deepmind/code_contests","domain":"代码","usage":"SFT/RL","size":"7.1 GB","lang":"多语言","license":"cc-by-4.0","validator":"是(单测可跑)","recommend":"★★★★","evidence":"sha=802411c, 44 files","notes":"DeepMind, 竞赛题+测试用例→RLVR"},
    {"name":"Nemotron-RL-math","repo":"nvidia/Nemotron-RL-math-OpenMathReasoning","domain":"数学","usage":"RL","size":"0.07 GB","lang":"en","license":"cc-by-4.0","validator":"是(答案可验)","recommend":"★★★★","evidence":"sha=219bf01, 4 files","notes":"Nemotron RL数学训练数据"},
    {"name":"Toucan-1.5M","repo":"Agent-Ark/Toucan-1.5M","domain":"Agent","usage":"SFT","size":"21.8 GB","lang":"en","license":"apache-2.0","validator":"否","recommend":"★★★★★ 已下","evidence":"sha=0df3cf3, 136 files, 4子集","notes":"495 MCP server, 2000+工具, 含Irrelevance扩展"},
    {"name":"AgentTrove","repo":"open-thoughts/AgentTrove","domain":"Agent/代码","usage":"SFT/RL","size":"19.55 GB","lang":"en","license":"apache-2.0","validator":"是(reward 0/1)","recommend":"★★★★★ 已排下","evidence":"sha=b395a43, 40 files, 38 parquet","notes":"Harbor/terminus-2格式, 含SWE/codeforces"},
    {"name":"Orca-AgentInstruct","repo":"microsoft/orca-agentinstruct-1M-v1","domain":"Agent","usage":"SFT","size":"2.38 GB","lang":"en","license":"cdla-permissive-2.0","validator":"否","recommend":"★ 低优先","evidence":"sha=86d6091, 22 files","notes":"纯合成, 无真实工具执行"},
    {"name":"ADP非重叠子集","repo":"neulab/agent-data-collection","domain":"Agent","usage":"SFT","size":"84.5 GB(15子集)","lang":"多语言","license":"各不同","validator":"混合","recommend":"★★★★ 已排下","evidence":"sha=31a76bf, 130 files, 22子集, 只下15个","notes":"ADP统一协议, 跳过重复子集"},
    {"name":"FreeInference Trace","repo":"harvardMadsys/freeinference_agentic_trace","domain":"Agent","usage":"分析(非训练)","size":"8.93 GB","lang":"N/A","license":"cc-by-4.0","validator":"N/A","recommend":"❌ 不下","evidence":"sha=bb26cf7, 217 files","notes":"No message text; 转告harness线做workload分析"},
    {"name":"GSM8K","repo":"openai/gsm8k","domain":"数学","usage":"评测","size":"0.006 GB","lang":"en","license":"mit","validator":"是","recommend":"★★(评测用)","evidence":"sha=740312a, 7 files","notes":"⚠️评测集→不可入训练"},
    {"name":"MATH-500","repo":"HuggingFaceH4/MATH-500","domain":"数学","usage":"评测","size":"0.0004 GB","lang":"en","license":"mit","validator":"是","recommend":"★★(评测用)","evidence":"sha=6e4ed1a, 4 files","notes":"⚠️评测集→不可入训练"},
]

def esc(s): return html.escape(str(s))

rows = ""
for d in curated:
    s = d['recommend']
    c = '#1a7f37' if '★★★★★' in s else ('#0969da' if '★★★★' in s else ('#d29922' if '★★★' in s else '#6e7781'))
    rows += f'<tr><td>{esc(d["name"])}</td><td>{esc(d["repo"])}</td><td>{esc(d["domain"])}</td><td>{esc(d["usage"])}</td><td>{esc(d["size"])}</td><td>{esc(d["lang"])}</td><td>{esc(d["license"])}</td><td>{esc(d["validator"])}</td><td style="color:{c};font-weight:bold">{esc(s)}</td><td style="font-size:0.85em">{esc(d["notes"])}</td></tr>\n'

evidence_rows = ""
for d in curated:
    evidence_rows += f'<tr><td>{esc(d["name"])}</td><td>{esc(d["repo"])}</td><td style="font-size:0.85em">{esc(d["evidence"])}</td></tr>\n'

html_doc = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>数学与编码数据集调研报告</title>
<style>
body{{font-family:-apple-system,"Microsoft YaHei",sans-serif;max-width:1400px;margin:0 auto;padding:20px;background:#f6f8fa;color:#1f2328}}
h1{{border-bottom:2px solid #d0d7de;padding-bottom:10px}}
table{{border-collapse:collapse;width:100%;margin:15px 0;font-size:0.9em}}
th,td{{border:1px solid #d0d7de;padding:8px 10px;text-align:left}}
th{{background:#f0f3f6;font-weight:600}}
tr:nth-child(even){{background:#f8f9fa}}
.summary{{background:#ddf4ff;border:1px solid #54aeff;border-radius:8px;padding:15px;margin:15px 0}}
.warning{{background:#fff8c5;border:1px solid #d4a72c;border-radius:8px;padding:15px;margin:15px 0}}
</style></head><body>
<h1>数学与编码数据集调研报告</h1>
<p style="color:#656d76">生成时间：2026-11-15 · data agent · 所有数据均经 HfApi 实测</p>
<div class="summary"><h2 style="margin-top:0">一句话结论</h2>
<p>已下 <b>MegaMath第一批</b>(数学预训练) + <b>Toucan-1.5M</b>(MCP工具SFT); 排队下载 <b>AgentTrove</b>(agent RL) + <b>ADP非重叠子集</b> + <b>IFM Math/Code-Reasoning</b>。数学预训练最优选 <b>Nemotron-CC-Math-v1</b>(论文称已超越MegaMath), 代码RL最优选 <b>OpenCodeReasoning</b>(自带单测验证)。</p></div>
<h2>Top-5 推荐(按ROI×缺口匹配度排序)</h2>
<table><tr><th>#</th><th>数据集</th><th>推荐理由</th><th>状态</th></tr>
<tr><td>1</td><td><b>Nemotron-CC-Math-v1</b>(nvidia,242GB)</td><td>ICLR2026, MATH+4.8~12.6, 已超越MegaMath; 133B tokens, 3+/4+分级</td><td>待下(license=other需核实)</td></tr>
<tr><td>2</td><td><b>OpenCodeReasoning</b>(nvidia,9GB)</td><td>代码推理+执行反馈, 自带单测→RLVR直接用; cc-by-4.0</td><td>待下</td></tr>
<tr><td>3</td><td><b>OpenMathInstruct-2</b>(nvidia,12GB)</td><td>14M Q-A, 自带答案验证→RLVR; cc-by-4.0</td><td>待下</td></tr>
<tr><td>4</td><td><b>CodeContests</b>(deepmind,7GB)</td><td>竞赛题+测试用例→RLVR; cc-by-4.0; 多语言</td><td>待下</td></tr>
<tr><td>5</td><td><b>OpenR1-Math-220k</b>(open-r1,12GB)</td><td>长思维链数学推理, 含答案验证; apache-2.0; SFT+RL两用</td><td>待下</td></tr>
</table>
<h2>与我们现状的匹配分析</h2>
<div class="summary">
<p><b>已有</b>: stack-v3-train(代码预训练2TB/249B tokens, 已分词)</p>
<p><b>本轮新增</b>: IFM/MegaMath(数学预训练) + Toucan-1.5M(MCP工具SFT) + AgentTrove(agent RL)</p>
<p><b>仍缺</b>:</p>
<ul>
<li><b>可验证RL数据</b>: 数学有答案可验的RLVR(OpenMathInstruct-2/Nemotron-RL-math)和代码有单测的RLVR(OpenCodeReasoning/CodeContests) — posttrain RL阶段关键缺口</li>
<li><b>竞赛级难题</b>: CodeContests/AIMO — 当前训练集缺乏高难度题</li>
<li><b>多语言代码</b>: stack-v3-train以Python为主, 缺C++/Rust/Go等系统语言SFT</li>
<li><b>中文数学/代码</b>: 当前数据以英文为主</li>
</ul></div>
<h2>总表: 数据集一览(HfApi实测)</h2>
<table><tr><th>数据集</th><th>repo</th><th>领域</th><th>用途</th><th>规模</th><th>语言</th><th>license</th><th>自带验证器</th><th>推荐度</th><th>备注</th></tr>
{rows}</table>
<h2>实测证据(HfApi探测结果)</h2>
<table><tr><th>数据集</th><th>repo_id</th><th>HfApi实测</th></tr>
{evidence_rows}</table>
<h2>IFM/MegaMath与LLM360/MegaMath同一性验证</h2>
<div class="summary">
<p><b>结论: 确为同一份数据(SHA完全相同)</b></p>
<table><tr><th>属性</th><th>IFM/MegaMath</th><th>LLM360/MegaMath</th></tr>
<tr><td>SHA</td><td>3cbc64616594d6bc8759abaa0b2a71858f880f0d</td><td>3cbc64616594d6bc8759abaa0b2a71858f880f0d</td></tr>
<tr><td>文件数</td><td>5317</td><td>5317</td></tr>
<tr><td>总字节</td><td>1,041.37 GB</td><td>1,041.37 GB</td></tr>
<tr><td>子集</td><td>6个(完全一致)</td><td>6个(完全一致)</td></tr>
</table>
<p>→ 下IFM/MegaMath, DATA_MAPPING.md注明「≡ LLM360/MegaMath(SHA校验)」, 避免重复下载。</p>
</div>
<h2>风险与坑</h2>
<div class="warning">
<h3 style="margin-top:0">⚠️ Benchmark污染检查</h3>
<table><tr><th>数据集</th><th>可能污染</th><th>处置</th></tr>
<tr><td>NuminaMath-1.5</td><td>AIME/AMC/IMO</td><td>下载后与AIME评测集去重</td></tr>
<tr><td>MetaMathQA</td><td>GSM8K/MATH改写</td><td>含改写版→需与评测集去重</td></tr>
<tr><td>APPS</td><td>APPS测试集</td><td>只用train split</td></tr>
<tr><td>AgentTrove</td><td>SWE-bench/codeforces</td><td>含swesmith/codeforces→需核对测试集重叠</td></tr>
<tr><td>ADP swe-smith</td><td>SWE-bench</td><td>已决定不下→规避</td></tr>
<tr><td>GSM8K</td><td>GSM8K测试集</td><td>⚠️评测集本身, 不可入训练</td></tr>
<tr><td>MATH-500</td><td>MATH测试集</td><td>⚠️评测集本身, 不可入训练</td></tr>
</table></div>
<div class="warning">
<h3 style="margin-top:0">⚠️ License风险</h3>
<ul>
<li><b>MathPile</b>: cc-by-nc-sa-4.0(非商业)</li>
<li><b>Nemotron-CC-Math-v1</b>: license=other→需核实</li>
<li><b>The Stack v2</b>: license=other→禁下(用户令)</li>
<li><b>ADP各子集</b>: license未统一标注→逐子集核实</li>
</ul></div>
<h2>SVG可视化</h2>
<svg width="700" height="300" viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="700" height="300" fill="#f6f8fa" rx="8"/>
<text x="350" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#1f2328">数学数据集规模对比(GB, HfApi实测)</text>
<rect x="50" y="50" width="500" height="20" fill="#0969da" rx="2"/><text x="560" y="65" font-size="11">IFM/Math-Reasoning 4462 GB</text>
<rect x="50" y="80" width="120" height="20" fill="#0969da" rx="2"/><text x="180" y="95" font-size="11">IFM/MegaMath 1041 GB</text>
<rect x="50" y="110" width="28" height="20" fill="#1a7f37" rx="2"/><text x="85" y="125" font-size="11">Nemotron-CC-Math 242 GB</text>
<rect x="50" y="140" width="16" height="20" fill="#1a7f37" rx="2"/><text x="73" y="155" font-size="11">FineMath 139 GB</text>
<rect x="50" y="170" width="3" height="20" fill="#d29922" rx="2"/><text x="60" y="185" font-size="11">OpenWebMath 25.5 GB</text>
<rect x="50" y="200" width="1.5" height="20" fill="#d29922" rx="2"/><text x="58" y="215" font-size="11">OpenMathInstruct-2 11.8 GB</text>
<rect x="50" y="230" width="0.1" height="20" fill="#d29922" rx="2"/><text x="58" y="245" font-size="11">NuminaMath 0.49 GB</text>
<line x1="50" y1="45" x2="50" y2="260" stroke="#d0d7de"/>
</svg>
<svg width="700" height="250" viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="700" height="250" fill="#f6f8fa" rx="8"/>
<text x="350" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#1f2328">代码数据集规模对比(GB, HfApi实测)</text>
<rect x="50" y="50" width="450" height="20" fill="#0969da" rx="2"/><text x="510" y="65" font-size="11">IFM/Code-Reasoning 3277 GB</text>
<rect x="50" y="80" width="55" height="20" fill="#1a7f37" rx="2"/><text x="115" y="95" font-size="11">The Stack v2 397.6 GB</text>
<rect x="50" y="110" width="13" height="20" fill="#1a7f37" rx="2"/><text x="71" y="125" font-size="11">OpenCodeReasoning 9.06 GB</text>
<rect x="50" y="140" width="9" height="20" fill="#1a7f37" rx="2"/><text x="67" y="155" font-size="11">OpenCodeInstruct 6.39 GB</text>
<rect x="50" y="170" width="10" height="20" fill="#d29922" rx="2"/><text x="68" y="185" font-size="11">CodeContests 7.1 GB</text>
<rect x="50" y="200" width="2" height="20" fill="#d29922" rx="2"/><text x="60" y="215" font-size="11">APPS 1.3 GB</text>
<line x1="50" y1="45" x2="50" y2="230" stroke="#d0d7de"/>
</svg>
<p style="color:#656d76;font-size:0.85em;margin-top:30px">报告结束 · 所有数据来自HfApi实测 · data agent · 2026-11-15</p>
</body></html>'''

os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(html_doc)
print(f"Report: {REPORT_PATH}")
print(f"Size: {os.path.getsize(REPORT_PATH)} bytes ({os.path.getsize(REPORT_PATH)/1024:.1f} KB)")
