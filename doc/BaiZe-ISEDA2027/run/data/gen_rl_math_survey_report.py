#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_rl_math_survey_report.py — 生成「RL+数学+agentic RL 数据集调研报告」中文 HTML。
运维令 2026-11-04 13:2x：调研提升复杂推理/代码/数学/agentic 能力的 SFT+RL 数据集（不含 A+B 类）。
幂等：多次运行产出逐字节一致的 HTML。
输出：doc/BaiZe-ISEDA2027/reports/report_data_rl_math_survey_zh.html
"""
import os, sys, html, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(HERE, "..", "..", "reports")
OUT = os.path.join(REPORT_DIR, "report_data_rl_math_survey_zh.html")

RL_DATASETS = [
    ("open-r1/OpenR1-Math-220k", 11.78, 66, "Apache-2.0", False, "2025-02-18", "100K<n<1M",
     "答案匹配（数学题最终数值验证）", "RL+SFT",
     "OpenR1 项目数学 RL 轨迹，含 R1 风格长链 CoT 推理轨迹 + 可验证答案标签；DAPO/OpenR 类的代表"),
    ("nvidia/OpenMathReasoning", 46.12, 235, "CC BY 4.0", False, "2025-05-27", "1M<n<10M",
     "答案匹配 + CoT 轨迹验证", "RL+SFT",
     "NVIDIA 开放数学推理数据集，含多个子集（code-contests、Math、AIME 等），大规模推理轨迹"),
    ("nvidia/OpenCodeReasoning", 9.06, 44, "CC BY 4.0", False, "2025-05-04", "100K<n<1M",
     "单测/答案匹配（代码执行验证）", "RL+SFT",
     "NVIDIA 开放代码推理数据集，含代码竞赛风格题目 + 推理轨迹 + 可执行验证"),
    ("deepmind/code_contests", 7.10, 45, "CC BY 4.0", False, "2023-06-11", "1K<n<10K",
     "单测（竞赛题目自动评测）", "RL",
     "DeepMind 代码竞赛数据集，含 CF/AtCoder/Codeforces 来源题目 + 测试用例，天然可验证"),
    ("code-search-net/code_search_net", 3.66, 31, "other", False, "2026-02-23", "100K<n<1M",
     "无自动验证（代码理解/检索语料）", "SFT",
     "CodeSearchNet 代码搜索语料，多语言（Python/Java/JS/Go 等），含代码-文档对；适合 SFT 不适合 RL"),
    ("open-thoughts/OpenThoughts-114k", 3.31, 25, "Apache-2.0", False, "2025-08-31", "100K<n<1M",
     "答案匹配（多领域可验证）", "RL+SFT",
     "OpenThoughts 114k 推理数据集，含数学/代码/科学多领域长链 CoT，答案可验证"),
    ("open-thoughts/OpenThoughts3-1.2M", 26.25, 124, "Apache-2.0", False, "2025-06-09", "1M<n<10M",
     "答案匹配（多领域可验证）", "RL+SFT",
     "OpenThoughts3 1.2M 大规模推理数据集，OpenThoughts 系列升级版，覆盖更广"),
    ("nvidia/Llama-Nemotron-Post-Training-Dataset-V1", 121.34, 21, "CC BY 4.0", False, "2025-05-08", "1M<n<10M",
     "答案匹配 + 偏好排序 + 环境奖励", "RL+SFT",
     "NVIDIA Llama-Nemotron 后训练数据集 V1，含 SFT/偏好/RL 多阶段数据；体量巨大（121GiB）"),
    ("Anthropic/hh-rlhf", 0.09, 16, "MIT", False, "2023-05-26", "100K<n<1M",
     "人类偏好排序（chosen/rejected 对）", "RL (RLHF)",
     "Anthropic 经典 RLHF 偏好数据集，含 helpfulness/harmlessness 偏好对；无可执行验证，纯人类偏好"),
    ("HuggingFaceH4/ultrafeedback_binarized", 0.61, 10, "MIT", False, "2024-10-16", "100K<n<1M",
     "LLM 评分偏好（GPT-4 打分二值化）", "RL (RLHF/DPO)",
     "UltraFeedback 二值化偏好数据集，含 chosen/rejected 对；适合 DPO/PPO 训练"),
    ("openbmb/UltraInteract_sft", 0.16, 7, "MIT", False, "2024-04-05", "100K<n<1M",
     "工具调用正确性验证", "SFT+RL",
     "UltraInteract SFT 子集，含工具调用/数学/代码多任务指令对；可提取工具调用正确性作奖励信号"),
    ("nvidia/HelpSteer3", 0.28, 17, "CC BY 4.0", False, "2025-11-16", "10K<n<100K",
     "多维人类评分（helpfulness/correctness/complexity 等）", "RL (RLHF)",
     "NVIDIA HelpSteer3 多维偏好数据集，含多语言（英/中/日/韩/法/西/俄/德）；评分维度细粒度"),
]

MATH_SFT_REASONING = [
    ("nvidia/OpenMathInstruct-2", 11.76, 60, "CC BY 4.0", False, "2024-11-25", "10M<n<100M",
     "答案匹配（数学题验证）", "SFT",
     "NVIDIA OpenMathInstruct-2 大规模数学指令数据集，14M 样本，含 CoT 解题轨迹；适合数学 SFT"),
    ("nvidia/OpenMathInstruct-1", 8.32, 9, "other", False, "2024-02-16", "1M<n<10M",
     "答案匹配（数学题验证）", "SFT",
     "NVIDIA OpenMathInstruct-1 首版数学指令数据集；license=other（NVIDIA 专用许可，需核查条款）"),
    ("project-numina/NuminaMath-CoT", 1.15, 9, "Apache-2.0", False, "2024-11-25", "100K<n<1M",
     "答案匹配（数学题验证）", "SFT",
     "NuminaMath CoT 数学推理数据集，Project Numina 出品；含竞赛级数学题 + CoT 解题过程"),
    ("project-numina/NuminaMath-1.5", 0.49, 6, "Apache-2.0", False, "2026-01-29", "100K<n<1M",
     "答案匹配（数学题验证）", "SFT",
     "NuminaMath 1.5 升级版，更新至 2026-01；Apache-2.0 许可，竞赛数学 CoT"),
    ("TIGER-Lab/WebInstructSub", 3.27, 16, "Apache-2.0", False, "2024-10-27", "1M<n<10M",
     "答案匹配（部分可验证）", "SFT",
     "TIGER-Lab WebInstructSub 网页指令子集，从网页抽取问答/推理对；大规模但质量参差"),
    ("meta-math/MetaMathQA", 0.37, 3, "MIT", False, "2023-12-21", "100K<n<1M",
     "答案匹配（数学题验证）", "SFT",
     "MetaMathQA 元数学问答数据集，基于 GSM8K/MATH 增强（改写/重述）；MIT 许可"),
    ("TIGER-Lab/MATH-plus", 0.31, 5, "MIT", False, "2024-05-21", "100K<n<1M",
     "答案匹配（数学题验证）", "SFT",
     "TIGER-Lab MATH-plus 增强数学数据集；MIT 许可，适合数学 SFT 补充"),
    ("openbmb/UltraChat", 8.65, 12, "MIT", False, "2024-02-22", "100K<n<1M",
     "无自动验证（通用对话）", "SFT",
     "UltraChat 大规模通用对话数据集，OpenBMB 出品；非数学/RL 专用但可做通用 SFT 退火"),
]

BENCHMARKS = [
    ("openai/gsm8k", 0.01, 9, "MIT", False, "2026-03-23", "1K<n<10K", "GSM8K 数学评测基准（去污染黑名单）"),
    ("google-research-datasets/mbpp", 0.00, 12, "CC BY 4.0", False, "2024-01-04", "n<1K", "MBPP 代码评测基准（去污染黑名单）"),
    ("project-numina/aimo-validation-aime", 0.00, 4, "Apache-2.0", False, "2025-05-07", "n<1K", "AIME 验证集（去污染黑名单）"),
]

GATED_REPOS = [
    ("PRIME-RL/Math-Shepherd", "401", "过程奖励模型（PRM）训练数据，数学逐步验证；需授权或已改名"),
    ("competition-math/PRM800K", "401", "OpenAI PRM800K 过程奖励数据，80 万步标注；需授权"),
    ("AgentGym/AgentGym", "401", "AgentGym 智能体环境数据集；需授权或已改名"),
    ("AgentTrek/AgentTrek", "401", "AgentTrek 智能体轨迹数据；需授权"),
    ("openbmb/AgentInstruct", "401", "OpenBMB AgentInstruct 智能体指令数据；需授权或已改名"),
    ("open-r1/OpenR1-Code-100k", "401", "OpenR1 代码 RL 轨迹 100k；需授权或已改名"),
    ("open-r1/OpenR1-Qwen-72B-Traces", "401", "OpenR1 Qwen-72B 推理轨迹；需授权"),
    ("nvidia/OpenReasoning-Math", "401", "NVIDIA 开放推理数学；需授权或 repo 已改名"),
    ("nvidia/OpenReasoning-Code", "401", "NVIDIA 开放推理代码；需授权或 repo 已改名"),
    ("nvidia/OpenMath2-Data", "401", "NVIDIA OpenMath2 数据；需授权或已改名"),
    ("RLHFlow/ultrafeedback_binarized", "401", "RLHFlow 版 UltraFeedback 二值化；需授权或已改名"),
    ("OrcaMathTuning/orca-math", "401", "OrcaMath 数学调优数据；需授权或已改名"),
    ("simplicitylk/Simplicity-Reasoning", "401", "Simplicity 推理数据；需授权或已改名"),
    ("openai/human-eval", "401", "HumanEval 代码评测基准；需授权（用于去污染黑名单）"),
]

COVERED = [
    ("A 类（长上下文）", "report_data_lc_agentic_survey_zh.html §A 类主表",
     "whole-books/prolong-512K/InfLLM-V2/RULER/NExtLong/LongAlign/oellm/pg19/mix-ctx/LongData-Corpus（10 源已落地 /nas_inference）"),
    ("B 类（agentic）", "运维令 13:2x #1 下载清单",
     "SWE-smith/Nemotron-Terminal/SWE-rebench/toolbench/AgentTrove/Orchard/Nemotron-Cascade/terminal-bench 等（下载中 /nas_inference）"),
    ("09:4x（复杂推理+代码 SFT）", "report_data_reasoning_code_sft_survey_zh.html",
     "复杂推理 SFT + Code-SFT 调研报告已交付（77772B），含数学/逻辑/代码 SFT 候选"),
]

ON_DISK_SOURCES = [
    "ultrafineweb_l1_en_hq", "ultrafineweb_zh", "ultrafineweb_en_v1_4",
    "UltraChat (openbmb)", "UltraData-SFT-2605", "UltraData-RL-2609",
    "InternVL-SA1B", "wit_base", "WebMix-38M", "GPIC",
    "code_l3", "math_l3", "math_l1", "ufw_l3", "code_l2", "AICC",
]

def esc(s):
    return html.escape(str(s))

def fmt_size(gib):
    if gib >= 1:
        return f"{gib:.2f} GiB"
    return f"{gib*1024:.1f} MiB"

def table_row_rl(d):
    repo, gib, files, lic, gated, last_mod, size_cat, reward, stage, note = d
    gs = "需授权" if gated else "公开"
    return (f'<tr><td><a href="https://huggingface.co/datasets/{esc(repo)}">{esc(repo)}</a></td>'
            f'<td>{fmt_size(gib)}</td><td>{files}</td><td>{esc(lic)}</td><td>{gs}</td>'
            f'<td>{esc(reward)}</td><td>{esc(stage)}</td><td>{esc(last_mod)}</td><td>{esc(note)}</td></tr>')

def table_row_bench(d):
    repo, gib, files, lic, gated, last_mod, size_cat, note = d
    return (f'<tr><td><a href="https://huggingface.co/datasets/{esc(repo)}">{esc(repo)}</a></td>'
            f'<td>{fmt_size(gib)}</td><td>{files}</td><td>{esc(lic)}</td>'
            f'<td>{esc(last_mod)}</td><td>{esc(note)}</td></tr>')

def table_row_gated(d):
    repo, status, note = d
    return f'<tr><td>{esc(repo)}</td><td>{esc(status)}</td><td>{esc(note)}</td></tr>'

def gen_sec1(rl_total, math_total):
    rl_top3 = [
        ("open-r1/OpenR1-Math-220k", 11.78, "数学 RL 黄金标准，R1 风格 CoT + 可验证答案，Apache-2.0，体量适中"),
        ("nvidia/OpenCodeReasoning", 9.06, "代码 RL 首选，NVIDIA 出品，含可执行验证 + 推理轨迹，CC BY 4.0"),
        ("open-thoughts/OpenThoughts3-1.2M", 26.25, "大规模多领域推理 RL，覆盖数学/代码/科学，Apache-2.0，1.2M 样本"),
    ]
    math_top3 = [
        ("nvidia/OpenMathInstruct-2", 11.76, "最大规模数学 SFT（14M 样本），CC BY 4.0，CoT 解题轨迹齐全"),
        ("project-numina/NuminaMath-CoT", 1.15, "竞赛级数学 CoT，Apache-2.0，Project Numina 出品，质量高"),
        ("TIGER-Lab/WebInstructSub", 3.27, "网页抽取大规模推理指令，Apache-2.0，1M+ 样本补充覆盖面"),
    ]
    pref_top3 = [
        ("HuggingFaceH4/ultrafeedback_binarized", 0.61, "DPO/PPO 标准偏好数据，MIT 许可，社区广泛使用"),
        ("nvidia/HelpSteer3", 0.28, "多维细粒度人类评分，CC BY 4.0，多语言（含中文）"),
        ("Anthropic/hh-rlhf", 0.09, "经典 RLHF 偏好对，MIT 许可，helpfulness+harmlessness"),
    ]
    s = []
    s.append('<section id="sec1"><h2>§1 · TL;DR — 核心结论与 TOP-3 推荐</h2>')
    s.append('<p>本报告调研能够提升 LLM <strong>复杂推理、代码、数学和 agentic 能力</strong>的 SFT 与 RL 数据集，'
             '<strong>排除</strong> 10-31 已调研的 A 类（长上下文）、B 类（agentic 下载中）以及 09:4x 已调研的复杂推理+代码 SFT 数据集。'
             '本令增量聚焦于：<strong>RL（强化学习，有可验证 reward 信号）+ 数学 SFT + 偏好/过程奖励 + agentic RL</strong>。</p>')
    s.append('<h3>RL 数据集 TOP-3（数学 RL / 代码 RL / 通用推理 RL）</h3>')
    s.append('<table><tr><th>排名</th><th>数据集</th><th>体量</th><th>推荐理由</th></tr>')
    for i,(repo,gib,reason) in enumerate(rl_top3,1):
        s.append(f'<tr><td>{i}</td><td><a href="https://huggingface.co/datasets/{esc(repo)}">{esc(repo)}</a></td><td>{fmt_size(gib)}</td><td>{esc(reason)}</td></tr>')
    s.append(f'</table><p>RL 数据集合计 <strong>{rl_total:.2f} GiB</strong>（含 121.34 GiB 巨型集；不含则 {rl_total-121.34:.2f} GiB）。</p>')
    s.append('<h3>数学 SFT TOP-3</h3><table><tr><th>排名</th><th>数据集</th><th>体量</th><th>推荐理由</th></tr>')
    for i,(repo,gib,reason) in enumerate(math_top3,1):
        s.append(f'<tr><td>{i}</td><td><a href="https://huggingface.co/datasets/{esc(repo)}">{esc(repo)}</a></td><td>{fmt_size(gib)}</td><td>{esc(reason)}</td></tr>')
    s.append(f'</table><p>数学 SFT 合计 <strong>{math_total:.2f} GiB</strong>。</p>')
    s.append('<h3>偏好/过程奖励 TOP-3（RLHF / DPO）</h3><table><tr><th>排名</th><th>数据集</th><th>体量</th><th>推荐理由</th></tr>')
    for i,(repo,gib,reason) in enumerate(pref_top3,1):
        s.append(f'<tr><td>{i}</td><td><a href="https://huggingface.co/datasets/{esc(repo)}">{esc(repo)}</a></td><td>{fmt_size(gib)}</td><td>{esc(reason)}</td></tr>')
    s.append('</table><h3>一句话总结</h3>')
    s.append('<p>本次调研核到 <strong>20 个公开可下载</strong>的 RL/数学/偏好数据集（含实测字节数），另有 <strong>14 个</strong>因 401 无法匿名核实。'
             '推荐优先下载：<strong>OpenR1-Math-220k（11.78G）+ OpenCodeReasoning（9.06G）+ OpenMathInstruct-2（11.76G）</strong>，'
             '三者合计 ~32.6 GiB，覆盖数学 RL + 代码 RL + 数学 SFT 三大核心方向，license 均开放。</p>')
    s.append('<div class="warn"><p>⚠️ <strong>巨大项警告</strong>：<code>nvidia/Llama-Nemotron-Post-Training-Dataset-V1</code> 达 <strong>121.34 GiB</strong>，'
             '含 SFT/偏好/RL 多阶段数据。体量巨大，建议选择性下载子集或后置，不默认全量下载。</p></div></section>')
    return '\n'.join(s)


def gen_sec2():
    s = ['<section id="sec2"><h2>§2 · 检索方法与核实口径</h2>']
    s.append('<h3>2.1 检索工具与流程</h3>')
    s.append('<p>本报告所有数据均通过 <strong>HuggingFace API（<code>https://huggingface.co/api/datasets/&lt;repo_id&gt;</code>）</strong> '
             '及 <strong>Tree API（<code>/api/datasets/&lt;repo_id&gt;/tree/main?recursive=true</code>）</strong> '
             '经代理 <code>http://172.19.92.25:13128</code> 实际请求核实，非凭记忆编写。'
             '工具：<code>python3 hf_api_fetch.py</code>（自建脚本）批量请求 HF API，再通过 Tree API 获取每个文件的 <code>size</code> 累加得到<strong>实测字节数</strong>。</p>')
    s.append('<h3>2.2 核实字段清单</h3><table><tr><th>字段</th><th>核实方式</th><th>可靠性</th></tr>')
    rows = [
        ("repo id","HF API id 字段（部分 repo 已改名）","高（API 直返）"),
        ("实测字节","Tree API 递归遍历所有文件 size 累加","高（精确到字节）"),
        ("样本数","HF API size_categories 标签（区间值）","中（仅区间）"),
        ("license","HF API cardData.license 字段","高（数据集卡声明）"),
        ("gated/私有","HF API gated/private 字段","高（API 直返）"),
        ("最后更新","HF API lastModified 字段","高（API 直返）"),
        ("奖励信号类型","从 tags/repo 名/数据集卡描述推断","中（基于推断）"),
        ("字段结构","未下载抽样，仅从 cardData keys 推断","低（未实测字段）"),
    ]
    for f,m,r in rows:
        s.append(f'<tr><td>{esc(f)}</td><td>{esc(m)}</td><td>{esc(r)}</td></tr>')
    s.append('</table>')
    s.append('<h3>2.3 未能核实的数据集（401 状态）</h3>')
    s.append('<p>以下 14 个数据集在匿名请求时返回 HTTP 401，表示<strong>需授权（gated）、已改名或已设为私有</strong>。本轮不编造其体量/license/字段，仅列出 repo id 及已知信息：</p>')
    s.append('<table><tr><th>repo id</th><th>状态</th><th>说明</th></tr>')
    for d in GATED_REPOS:
        s.append(table_row_gated(d))
    s.append('</table><div class="warn"><p>⚠️ 401 不一定意味着 gated —— 也可能是 repo 已改名。本轮仅以匿名 API 能否访问为准。</p></div>')
    s.append('<h3>2.4 排除范围（已覆盖指针）</h3><table><tr><th>类别</th><th>报告/来源</th><th>覆盖内容</th></tr>')
    for cat,src,desc in COVERED:
        s.append(f'<tr><td>{esc(cat)}</td><td>{esc(src)}</td><td>{esc(desc)}</td></tr>')
    s.append('</table>')
    s.append('<h3>2.5 奖励信号分类口径</h3><ul>')
    sigs = [
        ("答案匹配","数学题最终数值/表达式验证（如 GSM8K/MATH 的 answer 字段）"),
        ("单测/执行验证","代码题运行测试用例验证（如 code_contests/MBPP 的 test 字段）"),
        ("diff 匹配","SWE 类任务通过 git diff 与 gold patch 比对"),
        ("人类偏好","RLHF 的 chosen/rejected 对（如 hh-rlhf/UltraFeedback）"),
        ("LLM 评分","GPT-4 或其他 LLM 打分生成偏好（如 UltraFeedback binarized）"),
        ("环境奖励","Agent 在模拟环境中执行后获得反馈（如 Terminal-Bench/SWE-bench 的 PASS/FAIL）"),
        ("过程奖励（PRM）","逐步骤标注正确性（如 PRM800K/Math-Shepherd）"),
    ]
    for sig,desc in sigs:
        s.append(f'<li><strong>{esc(sig)}</strong>：{esc(desc)}</li>')
    s.append('</ul></section>')
    return '\n'.join(s)

def gen_sec3():
    s = ['<section id="sec3"><h2>§3 · RL 数据集主表（数学 RL · 代码 RL · 通用推理 RL · 偏好/过程奖励）</h2>']
    s.append('<p>下表为本次调研核到的 RL 相关数据集，按<strong>奖励信号类型</strong>分层。每条含实测字节数、license、gated 状态、奖励信号来源、适用训练阶段。</p>')
    headers = '<tr><th>repo id</th><th>实测体量</th><th>文件数</th><th>license</th><th>gated</th><th>奖励信号</th><th>适用阶段</th><th>最后更新</th><th>说明</th></tr>'
    # 3.1 数学 RL
    s.append('<h3>3.1 数学 RL（答案匹配验证）</h3><table>'+headers)
    for d in RL_DATASETS:
        if "答案匹配" in d[7] and ("数学" in d[9] or "Math" in d[0] or "数学" in d[7]):
            s.append(table_row_rl(d))
    s.append('</table>')
    # 3.2 代码 RL
    s.append('<h3>3.2 代码 RL（单测/执行验证）</h3><table>'+headers)
    for d in RL_DATASETS:
        if "单测" in d[7] or "代码" in d[9] or ("无自动验证" in d[7] and "code" in d[0].lower()):
            s.append(table_row_rl(d))
    s.append('</table>')
    # 3.3 通用推理 RL
    s.append('<h3>3.3 通用推理 RL（多领域可验证）</h3><table>'+headers)
    for d in RL_DATASETS:
        if "多领域" in d[7]:
            s.append(table_row_rl(d))
    s.append('</table>')
    # 3.4 偏好
    s.append('<h3>3.4 偏好/过程奖励（RLHF / DPO / PRM）</h3><table>'+headers)
    for d in RL_DATASETS:
        if "偏好" in d[7] or "评分" in d[7] or "人类" in d[7]:
            s.append(table_row_rl(d))
    s.append('</table>')
    # 3.5 巨型
    s.append('<h3>3.5 巨型 RL 数据集（体量警告）</h3><table>'+headers)
    for d in RL_DATASETS:
        if d[1] >= 100:
            s.append(table_row_rl(d))
    s.append('</table><div class="warn"><p>⚠️ Llama-Nemotron-Post-Training（121.34 GiB）体量巨大，建议<strong>选择性下载子集</strong>。</p></div></section>')
    return '\n'.join(s)

def gen_sec4():
    s = ['<section id="sec4"><h2>§4 · 数学 SFT + 复杂推理补强 + Agentic RL 主表</h2>']
    headers = '<tr><th>repo id</th><th>实测体量</th><th>文件数</th><th>license</th><th>gated</th><th>奖励信号</th><th>适用阶段</th><th>最后更新</th><th>说明</th></tr>'
    s.append('<h3>4.1 数学 SFT 数据集</h3><table>'+headers)
    for d in MATH_SFT_REASONING:
        s.append(table_row_rl(d))
    math_total = sum(d[1] for d in MATH_SFT_REASONING)
    s.append(f'</table><p>数学 SFT 合计 <strong>{math_total:.2f} GiB</strong>。OpenMathInstruct-2（11.76G / 14M 样本）为体量最大者，适合做数学退火主体。</p>')
    s.append('<h3>4.2 复杂推理补强（长链 CoT 推理轨迹）</h3>')
    s.append('<p>以下数据集已在 §3 RL 主表中列出，此处补充其<strong>复杂推理补强价值</strong>：</p><ul>')
    items = [
        ("OpenThoughts-114k（3.31 GiB）","含数学/代码/科学多领域长链 CoT，R1 风格推理轨迹"),
        ("OpenThoughts3-1.2M（26.25 GiB）","1.2M 样本，覆盖更广；体量适中，可做推理退火主体"),
        ("OpenR1-Math-220k（11.78 GiB）","含 R1 风格长链 CoT + 可验证答案，兼具 SFT 与 RL 价值"),
        ("OpenMathReasoning（46.12 GiB）","含多子集（code-contests/Math/AIME），推理轨迹丰富"),
    ]
    for name,desc in items:
        s.append(f'<li><strong>{esc(name)}</strong>：{esc(desc)}</li>')
    s.append('</ul>')
    s.append('<h3>4.3 Agentic RL（可执行验证信号）</h3>')
    s.append('<p>大部分 agentic RL 数据集（AgentGym/AgentTrek/AgentInstruct 等）返回 401 无法匿名核实。可核到的 agentic RL 相关：</p><table>'+headers)
    for d in RL_DATASETS:
        if "工具" in d[7] or "工具" in d[9]:
            s.append(table_row_rl(d))
    s.append('</table><div class="warn"><p>⚠️ <strong>Agentic RL 可选项受限</strong>：关键 agentic RL 数据集均 401。建议以 B 类下载的 SWE-smith/Nemotron-Cascade-RL-SWE 为主力 agentic RL 源。</p></div>')
    s.append('<h3>4.4 评测基准（去污染参考，不推荐下载训练）</h3><table><tr><th>repo id</th><th>体量</th><th>文件数</th><th>license</th><th>最后更新</th><th>说明</th></tr>')
    for d in BENCHMARKS:
        s.append(table_row_bench(d))
    s.append('</table></section>')
    return '\n'.join(s)


def gen_sec5():
    s = ['<section id="sec5"><h2>§5 · 污染风险与去重方案</h2>']
    s.append('<h3>5.1 与盘上 12 源的重叠分析</h3><p>盘上已有数据源（见 <code>run/data/DATA_MAPPING.md</code>）：</p><table><tr><th>#</th><th>盘上已有源</th><th>与本报告候选重叠</th></tr>')
    for i,src in enumerate(ON_DISK_SOURCES,1):
        overlap = "无直接重叠" if "UltraChat" not in src else "openbmb/UltraChat 已在盘（8.65G），仅列参考不重复推荐"
        s.append(f'<tr><td>{i}</td><td>{esc(src)}</td><td>{esc(overlap)}</td></tr>')
    s.append('</table><p><strong>结论</strong>：本报告推荐的 RL/数学/偏好数据集与盘上 12 源<strong>无直接重叠</strong>。唯一交集是 UltraChat（已列参考不推荐重下）。</p>')
    s.append('<h3>5.2 与 A/B/09:4x 的重叠</h3><table><tr><th>类别</th><th>已覆盖数据集</th><th>与本报告重叠</th></tr>')
    overlaps = [
        ("A 类（长上下文 10 源）","whole-books/prolong/InfLLM-V2/RULER/NExtLong/LongAlign/oellm/pg19/mix-ctx/LongData","无重叠（A 类为长文本，本报告为 RL/数学）"),
        ("B 类（agentic 12 源）","SWE-smith/Nemotron-Terminal/SWE-rebench/toolbench/AgentTrove/Orchard/Nemotron-Cascade 等","部分重叠：SWE-smith B 类已含；本报告不重复推荐 B 类"),
        ("09:4x（复杂推理+代码 SFT）","report_data_reasoning_code_sft_survey_zh.html","本报告刻意避开 09:4x，聚焦 RL 增量"),
    ]
    for cat,srcs,ov in overlaps:
        s.append(f'<tr><td>{esc(cat)}</td><td>{esc(srcs)}</td><td>{esc(ov)}</td></tr>')
    s.append('</table>')
    s.append('<h3>5.3 与 SWE-bench Verified · Terminal Bench 的污染风险</h3><table><tr><th>数据集</th><th>风险等级</th><th>风险说明</th><th>去污染建议</th></tr>')
    risks = [
        ("deepmind/code_contests","中","含 CF/AtCoder 题目，与 HumanEval/MBPP 无直接重叠，但部分竞赛题可能出现在其他评测集","用 13-gram 指纹黑名单交叉比对"),
        ("open-r1/OpenR1-Math-220k","中","基于 MATH/GSM8K 生成，与 GSM8K 评测集有同源风险","下载后用 GSM8K 题面做 13-gram 去重"),
        ("project-numina/NuminaMath-CoT","中","含 AIME/竞赛题，与 aimo-validation-aime 评测集有同源风险","下载后用 AIME 题面做 13-gram 去重"),
        ("nvidia/OpenMathReasoning","中","含 code-contests 子集，与 code_contests 同源","子集级别去重"),
        ("nvidia/OpenCodeReasoning","低","代码推理数据，与 SWE-bench Verified 任务类型不同","常规 13-gram 黑名单扫描"),
        ("open-thoughts/OpenThoughts-114k","低","多领域推理，与 SWE-bench/TB 任务类型不同","常规 13-gram 黑名单扫描"),
        ("Anthropic/hh-rlhf","低","通用偏好对，非 SWE/终端任务","常规扫描"),
        ("HuggingFaceH4/ultrafeedback_binarized","低","通用偏好对，非 SWE/终端任务","常规扫描"),
        ("nvidia/Llama-Nemotron-Post-Training","中","含多阶段数据，部分子集可能含 SWE 类任务","下载后检查子集是否含 SWE-bench 源仓库"),
        ("openbmb/UltraInteract_sft","低","工具调用指令，与 SWE-bench/TB 任务类型不同","常规 13-gram 黑名单扫描"),
    ]
    for ds,lv,desc,fix in risks:
        s.append(f'<tr><td>{esc(ds)}</td><td>{esc(lv)}</td><td>{esc(desc)}</td><td>{esc(fix)}</td></tr>')
    s.append('</table>')
    s.append('<h3>5.4 去污染机制（已有）</h3>')
    s.append('<p>我们已有 <strong>193,295 条 13-gram 指纹黑名单</strong>（见 <code>CONTAMINATION_CHECK.md</code>），覆盖 EDA-Eval-PyAether 158 任务 + SWE-bench/TB 相关指纹。机制包含：</p><ul>')
    mechs = [
        "黑名单指纹：对评测集 prompt/test 断言生成 13-gram 指纹",
        "训练集侧扫描：对训练数据做 13-gram 匹配，命中即剔除",
        "阈值可复现：匹配阈值写明，可复现验证",
        "SFT 语料同闸：SFT 数据同样经过 13-gram 扫描",
        "独立报告：CONTAMINATION_CHECK.md 记录扫描结果",
    ]
    for m in mechs:
        s.append(f'<li>{esc(m)}</li>')
    s.append('</ul><p><strong>本报告推荐的数据集下载后均需经过此 13-gram 黑名单扫描</strong>，特别是数学 RL 数据集。</p></section>')
    return '\n'.join(s)

def gen_sec6():
    s = ['<section id="sec6"><h2>§6 · 下载方案（建议优先级 · 体量 · 落盘 · ETA）</h2>']
    s.append('<h3>6.1 推荐下载清单（按优先级）</h3><p>⚠️ <strong>本令红线：只调研不下载</strong>。以下为建议方案，需运维批准后执行。</p>')
    s.append('<table><tr><th>优先级</th><th>数据集</th><th>实测体量</th><th>license</th><th>理由</th><th>建议落盘路径</th></tr>')
    recs = [
        ("P0","open-r1/OpenR1-Math-220k","11.78 GiB","Apache-2.0","数学 RL 核心源","/nas_inference/app.e0031982/datasets/open-r1/OpenR1-Math-220k/"),
        ("P0","nvidia/OpenCodeReasoning","9.06 GiB","CC BY 4.0","代码 RL 核心源","/nas_inference/app.e0031982/datasets/nvidia/OpenCodeReasoning/"),
        ("P0","nvidia/OpenMathInstruct-2","11.76 GiB","CC BY 4.0","数学 SFT 主体 14M 样本","/nas_inference/app.e0031982/datasets/nvidia/OpenMathInstruct-2/"),
        ("P1","open-thoughts/OpenThoughts3-1.2M","26.25 GiB","Apache-2.0","大规模多领域推理 1.2M","/nas_inference/app.e0031982/datasets/open-thoughts/OpenThoughts3-1.2M/"),
        ("P1","project-numina/NuminaMath-CoT","1.15 GiB","Apache-2.0","高质量竞赛数学 CoT","/nas_inference/app.e0031982/datasets/project-numina/NuminaMath-CoT/"),
        ("P1","HuggingFaceH4/ultrafeedback_binarized","0.61 GiB","MIT","DPO/PPO 标准偏好数据","/nas_inference/app.e0031982/datasets/HuggingFaceH4/ultrafeedback_binarized/"),
        ("P2","nvidia/OpenMathReasoning","46.12 GiB","CC BY 4.0","大规模数学推理含多子集","/nas_inference/app.e0031982/datasets/nvidia/OpenMathReasoning/"),
        ("P2","deepmind/code_contests","7.10 GiB","CC BY 4.0","代码竞赛 RL 天然可验证","/nas_inference/app.e0031982/datasets/deepmind/code_contests/"),
        ("P2","TIGER-Lab/WebInstructSub","3.27 GiB","Apache-2.0","网页抽取推理指令","/nas_inference/app.e0031982/datasets/TIGER-Lab/WebInstructSub/"),
        ("P3","open-thoughts/OpenThoughts-114k","3.31 GiB","Apache-2.0","中等规模推理与 P1 互补","/nas_inference/app.e0031982/datasets/open-thoughts/OpenThoughts-114k/"),
        ("P3","nvidia/HelpSteer3","0.28 GiB","CC BY 4.0","多维偏好含中文","/nas_inference/app.e0031982/datasets/nvidia/HelpSteer3/"),
    ]
    for p,repo,sz,lic,reason,path in recs:
        s.append(f'<tr><td>{esc(p)}</td><td><a href="https://huggingface.co/datasets/{esc(repo)}">{esc(repo)}</a></td><td>{esc(sz)}</td><td>{esc(lic)}</td><td>{esc(reason)}</td><td>{esc(path)}</td></tr>')
    s.append('</table>')
    s.append('<h3>6.2 体量汇总</h3><table><tr><th>优先级</th><th>数据集数</th><th>合计体量</th></tr>')
    sums = [("P0（核心推荐）",3,"32.60 GiB"),("P0+P1（推荐）",6,"60.61 GiB"),("P0+P1+P2（扩展）",9,"117.10 GiB"),("全部（含 P3）",11,"120.69 GiB"),("+ 巨型项",12,"242.03 GiB")]
    for p,n,sz in sums:
        s.append(f'<tr><td>{esc(p)}</td><td>{n}</td><td>{esc(sz)}</td></tr>')
    s.append('</table>')
    s.append('<h3>6.3 磁盘与带宽预估</h3><p>当前磁盘（2026-11-04 实测）：</p><ul>')
    s.append('<li><code>/nas_inference</code>：45T 总 / 17T 已用 / <strong>29T 可用（38%）</strong></li>')
    s.append('<li><code>/nas_train</code>：207T 总 / 179T 已用 / 29T 可用（87%）</li></ul>')
    s.append('<p>P0+P1（60.61 GiB）落盘 /nas_inference 后余量充裕。带宽预估（B 类实测：~1G/分钟）：</p><ul>')
    s.append('<li>P0（32.6G）：~30-40 分钟</li><li>P0+P1（60.6G）：~60-80 分钟</li><li>全部（120.7G）：~2-3 小时</li></ul>')
    s.append('<h3>6.4 hf download 命令模板</h3>')
    s.append('<pre>export HTTPS_PROXY=http://172.19.92.25:13128\nexport HF_HUB_ENABLE_HF_TRANSFER=0\nnice -n 10 hf download &lt;repo_id&gt; --repo-type dataset \\\n  --local-dir /nas_inference/app.e0031982/datasets/&lt;org&gt;/&lt;name&gt; --max-workers 4</pre>')
    s.append('<p>纪律同 B 类下载：setsid 后台 + /tmp 日志 + nice -n 10 + 并发 ≤4 + 限带宽，不挤 S1 训练。</p></section>')
    return '\n'.join(s)


def gen_sec7():
    s = ['<section id="sec7"><h2>§7 · 诚实条款（未核到 · 代理指标 · license 风险）</h2>']
    s.append('<h3>7.1 未核到的字段</h3><table><tr><th>字段</th><th>状态</th><th>说明</th></tr>')
    ufv = [
        ("字段结构（columns/fields）","未核到","本轮未下载抽样，仅从 cardData keys 推断。建议下载后用 datasets.load_dataset() 检查"),
        ("奖励信号类型","推断","从 tags/repo 名/数据集卡描述推断，非 API 直返"),
        ("样本数（精确）","区间值","HF API 仅提供 size_categories 标签，非精确样本数"),
        ("401 数据集体量/license","未核到","14 个数据集返回 401，不编造"),
        ("数据质量/毒性/偏见","未核到","本轮仅做元数据级调研，未做内容质量评估"),
    ]
    for f,st,desc in ufv:
        s.append(f'<tr><td>{esc(f)}</td><td>{esc(st)}</td><td>{esc(desc)}</td></tr>')
    s.append('</table>')
    s.append('<h3>7.2 代理指标 vs 实测</h3><table><tr><th>指标</th><th>代理方式</th><th>实测方式</th><th>差异说明</th></tr>')
    pm = [
        ("体量（字节）","HF API size_categories 标签","Tree API 递归累加 size","本报告主表用实测值"),
        ("样本数","size_categories 区间","需下载数据后 len(dataset)","本报告仅用区间值"),
        ("下载实际字节","Tree API 累加","hf download 实际落盘字节","Tree API 可能不含 LFS 指针，实际可能略大"),
    ]
    for m,p,a,d in pm:
        s.append(f'<tr><td>{esc(m)}</td><td>{esc(p)}</td><td>{esc(a)}</td><td>{esc(d)}</td></tr>')
    s.append('</table>')
    s.append('<h3>7.3 license 风险</h3><table><tr><th>license</th><th>数据集</th><th>风险说明</th></tr>')
    lr = [
        ("CC BY 4.0","OpenMathReasoning/OpenCodeReasoning/OpenMathInstruct-2/HelpSteer3/code_contests","需署名，商业可用但需标注来源"),
        ("Apache-2.0","OpenR1-Math-220k/OpenThoughts*/NuminaMath*/WebInstructSub","最宽松之一，含专利授权，商业可用"),
        ("MIT","MetaMathQA/MATH-plus/hh-rlhf/ultrafeedback/UltraChat/UltraInteract","最宽松，几乎无限制"),
        ("other","OpenMathInstruct-1/code_search_net","非标准 license，需核查具体条款"),
    ]
    for lic,ds,risk in lr:
        s.append(f'<tr><td>{esc(lic)}</td><td>{esc(ds)}</td><td>{esc(risk)}</td></tr>')
    s.append('</table>')
    s.append('<h3>7.4 已知坑</h3><ul>')
    pits = [
        "HF 体量以数据集卡为准，与实际下载字节可能差异大",
        "部分 repo 已改名（如 AI-MO/NuminaMath-CoT → project-numina/NuminaMath-CoT），需以 API 返回的 id 为准",
        "401 不一定 gated —— 也可能是 repo 已改名/已删除/已设私有",
        "Nemotron-Post-Training 121G 巨型集含多阶段数据，子集结构未核到，建议下载前先 hf repo files 查看目录树",
        "AgentGym/AgentTrek/AgentInstruct 等 agentic RL 源不可匿名访问，agentic RL 增量有限",
    ]
    for p in pits:
        s.append(f'<li>{esc(p)}</li>')
    s.append('</ul>')
    s.append('<h3>7.5 报告生成信息</h3><ul>')
    s.append('<li>生成器：<code>run/data/gen_rl_math_survey_report.py</code>（幂等）</li>')
    s.append('<li>数据来源：HF API + Tree API，经代理 172.19.92.25:13128 实际请求（2026-11-04）</li>')
    s.append('<li>核实工具：<code>run/data/hf_api_fetch.py</code>（自建脚本）</li>')
    s.append('<li>约束：0 script / 0 外链（仅 huggingface.co 内链）/ 标签配平 / ≥25KB</li>')
    s.append('</ul></section>')
    return '\n'.join(s)

def generate():
    rl_total = sum(d[1] for d in RL_DATASETS)
    math_total = sum(d[1] for d in MATH_SFT_REASONING)
    css = """<style>
body { font-family: "Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; color: #333; line-height: 1.7; }
h1 { color: #1a5276; border-bottom: 3px solid #2980b9; padding-bottom: 10px; }
h2 { color: #2874a6; border-bottom: 2px solid #5dade2; padding-bottom: 8px; margin-top: 2.5em; }
h3 { color: #2e86c1; margin-top: 2em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.92em; }
th, td { border: 1px solid #bdc3c7; padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: #d4e6f1; font-weight: bold; color: #1a5276; }
tr:nth-child(even) { background: #f8f9fa; }
tr:hover { background: #eaf2f8; }
a { color: #2471a3; text-decoration: none; }
a:hover { text-decoration: underline; color: #1a5276; }
code { background: #f0f3f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 0.88em; color: #c0392b; }
pre { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 12px; overflow-x: auto; font-size: 0.88em; }
pre code { background: none; color: #333; padding: 0; }
.warn { background: #fef9e7; border-left: 4px solid #f39c12; padding: 12px 16px; margin: 1.5em 0; border-radius: 0 5px 5px 0; }
ul { margin: 0.8em 0; padding-left: 2em; }
li { margin: 0.3em 0; }
.meta { color: #7f8c8d; font-size: 0.88em; margin: 1em 0; }
.tldr-box { background: #eafaf1; border: 2px solid #27ae60; border-radius: 8px; padding: 16px 20px; margin: 1.5em 0; }
</style>"""
    body = '\n'.join([gen_sec1(rl_total, math_total), gen_sec2(), gen_sec3(), gen_sec4(), gen_sec5(), gen_sec6(), gen_sec7()])
    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BaiZe RL + 数学 + Agentic RL 数据集调研报告</title>
{css}
</head>
<body>
<h1>BaiZe RL + 数学 + Agentic RL 数据集调研报告</h1>
<p class="meta">运维令 2026-11-04 13:2x · 用户直令 · 最高优先<br>
生成时间：2026-11-04 · 生成器：<code>run/data/gen_rl_math_survey_report.py</code>（幂等）<br>
数据来源：HuggingFace API + Tree API 实测（经代理 172.19.92.25:13128）<br>
范围：RL + 数学 SFT + 偏好/过程奖励 + agentic RL（不含 A+B 类 + 09:4x 已覆盖）</p>
<div class="tldr-box"><p><strong>一句话结论</strong>：核到 20 个公开可下载的 RL/数学/偏好数据集（含实测字节数），14 个 401 不可匿名访问。推荐 P0 三件套：<strong>OpenR1-Math-220k（11.78G）+ OpenCodeReasoning（9.06G）+ OpenMathInstruct-2（11.76G）</strong>，合计 32.6 GiB。</p></div>
{body}
<hr>
<p class="meta">— 报告结束 —<br>由 gen_rl_math_survey_report.py 自动生成，数据来自 HuggingFace API 实测核实。</p>
</body>
</html>"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html_doc)
    size = os.path.getsize(OUT)
    print(f"Generated: {OUT}")
    print(f"Size: {size} bytes ({size/1024:.1f} KB)")
    assert "<script" not in html_doc.lower(), "FAIL: contains <script>"
    assert size >= 25000, f"FAIL: size {size} < 25000"
    import html.parser
    class Chk(html.parser.HTMLParser):
        def __init__(self):
            super().__init__(); self.stk=[]; self.err=[]; self.void={"br","hr","img","input","meta","link","col","area","base","embed","source","track","wbr"}
        def handle_starttag(self,t,a):
            if t not in self.void: self.stk.append(t)
        def handle_endtag(self,t):
            if t in self.void: return
            if self.stk and self.stk[-1]==t: self.stk.pop()
            elif t in self.stk:
                while self.stk and self.stk[-1]!=t: self.err.append(f"unclosed {self.stk[-1]}"); self.stk.pop()
                if self.stk: self.stk.pop()
            else: self.err.append(f"stray {t}")
    c=Chk(); c.feed(html_doc)
    print(f"Tags: errors={len(c.err)} unclosed={len(c.stk)}")
    if c.err: print(f"  errors: {c.err[:5]}")
    if c.stk: print(f"  unclosed: {c.stk}")
    print("OK" if size>=25000 and not c.err and not c.stk else "CHECK NEEDED")

if __name__ == "__main__":
    generate()
