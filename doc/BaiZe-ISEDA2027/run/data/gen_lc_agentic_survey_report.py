#!/usr/bin/env python3
"""
gen_lc_agentic_survey_report.py -- 生成「长上下文 + Agentic 数据集 HF 调研报告」HTML

幂等：连跑两次输出逐字节相同。
输出：doc/BaiZe-ISEDA2027/reports/report_data_lc_agentic_survey_zh.html

调研日期：2026-10-31
调研方法：通过 web search 检索 hf.co 数据集页面，逐条核实 repo id / 体量 / 语言 / license / gated / 字段结构。
"""

import html
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "reports", "report_data_lc_agentic_survey_zh.html")
SURVEY_DATE = "2026-10-31"

# A 类：长上下文数据集
LONG_CONTEXT_DATASETS = [
    {
        "repo_id": "ysngkil/whole-books",
        "hf_url": "https://huggingface.co/datasets/ysngkil/whole-books",
        "category": "书籍/长文",
        "size": "~25 GiB (gutenberg 6.83 + pre1929 15.04 + doab 3.0 + textbooks 0.27 + pressbooks 0.17)",
        "samples": "202,343 本书 (gutenberg 55,454 + pre1929 124,898 + doab 18,948 + textbooks 1,149 + pressbooks 1,894)",
        "tokens_est": "~20.9B tokens (32K vocab 估算; 128K vocab 约 -15~20%)",
        "language": "英语",
        "license": "mixed-public-domain-and-creative-commons (每行自带 license 字段)",
        "gated": "否",
        "updated": "2026-09-06",
        "fields": "book_id, title, author, publisher, isbn, license, url, created, n_sections, text, n_chars",
        "ge32k_ratio": "gutenberg: 87% tokens 在 >=64K 书中; pre1929: 86%; doab: 98%; textbooks: 96%; pressbooks: 81%",
        "ge128k_ratio": "未单独标注 >=128K; 但 gutenberg max=7.8M tok、pre1929 max=5.6M、doab max=1.5M",
        "evidence": "数据集卡列出 per-config 'tokens in books >=64K' 比例; p50/p90/max token per book 均标注",
        "notes": "一行=一整本书，非常适合长上下文预训练。Common Pile v0.1 子集的 1:1 parquet 转换。ProLong 论文证实 books 是长数据优质来源。",
    },
    {
        "repo_id": "princeton-nlp/prolong-data-512K",
        "hf_url": "https://huggingface.co/datasets/princeton-nlp/prolong-data-512K",
        "category": "长上下文训练集 (代码仓库级 + 书籍 + 混合)",
        "size": "31B tokens, MDS 格式",
        "samples": "子集: thestackv1_concat_by_repo-524288 (3.2B), -65536 (3.2B), book-524288 (2.1B), book-65536 (4.2B), fineweb-edu (6.4B), fineweb-2023-50 (6.4B), stackexchange (1B), dolmawiki (1B), tuluv2 (250M), arxiv (1B), openwebmath (1B), textbooks (750M)",
        "tokens_est": "31B tokens (Llama-3 tokenizer, packed to 524,288)",
        "language": "英语",
        "license": "未明确标注 (论文 arXiv:2410.02660; 代码 MIT)",
        "gated": "否",
        "updated": "2024-10",
        "fields": "input_ids (524,288 长), indices (文档边界), domain (子集名)",
        "ge32k_ratio": "65536 子集: 100% >=65K; 524288 子集: 100% >=524K; Variable 子集: 未标注",
        "ge128k_ratio": "524288 子集: 100% >=128K; 65536 子集: 0% (固定 65K)",
        "evidence": "数据集卡明确列出每个子集 Sequence Length; 论文证实 'code repos and books are excellent long data'",
        "notes": "目前最系统化的长上下文训练数据集。repo-level 代码拼接是标准做法。需 mosaicml-streaming 库加载。短数据用于与长数据混合。",
    },
    {
        "repo_id": "caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1",
        "hf_url": "https://huggingface.co/datasets/caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1",
        "category": "长上下文训练集 (合成)",
        "size": "未核到确切字节 (多子集: 64K/128K/256K/512K)",
        "samples": "未核到",
        "tokens_est": "未核到",
        "language": "英语",
        "license": "未核到 (论文公开发表)",
        "gated": "否",
        "updated": "2025-01",
        "fields": "未核到完整字段",
        "ge32k_ratio": "按设计: 64K 子集 100% >=64K, 128K+ 子集同理",
        "ge128k_ratio": "128K/256K/512K 子集: 100% >=128K (按设计)",
        "evidence": "数据集卡标注各子集目标上下文长度; 论文 NExtLong 详述 Negative document Extension",
        "notes": "不依赖真实长文档，用短文档+负例干扰合成长上下文。HELMET/RULER 上优于非合成方法。适合真实长文档不足时。",
    },
    {
        "repo_id": "utter-project/LongBlocks",
        "hf_url": "https://huggingface.co/datasets/utter-project/LongBlocks",
        "category": "长文档 QA / 合成",
        "size": "~194K 样本",
        "samples": "~194,000 条长上下文 QA",
        "tokens_est": "未核到",
        "language": "20 种语言 (英/法/德/中等)",
        "license": "CC BY-SA 4.0 (需遵守底层数据源条款)",
        "gated": "否",
        "updated": "2026-05-11",
        "fields": "长源文档, 源语料库标识, 语言标识, 合成问题, 参考答案, 3 教师模型响应",
        "ge32k_ratio": "未标注; 来源含书籍/论文/Wikipedia，预期有相当比例 >=32K",
        "ge128k_ratio": "未标注; 需下载抽样实测",
        "evidence": "数据集卡描述来源为 Institutional-Books-1.0, FineWeb2-HQ, PGBooks, arXiv, Wikipedia, Stack-Edu, StackExchange",
        "notes": "多语言长上下文 QA，含 3 教师模型响应，可用于知识蒸馏。SFT 用途。中文覆盖有额外价值。",
    },
    {
        "repo_id": "common-pile/arxiv_papers_filtered",
        "hf_url": "https://huggingface.co/datasets/common-pile/arxiv_papers_filtered",
        "category": "书籍/长文 (论文全文)",
        "size": "Common Pile v0.1 总计 8TB; arxiv 子集未单独核到",
        "samples": "未核到 (ArXiv 2.4M+ 论文中 CC BY/SA/CC0 部分)",
        "tokens_est": "未核到",
        "language": "英语 (多语言)",
        "license": "CC BY, CC BY-SA, CC0",
        "gated": "否",
        "updated": "2025-06",
        "fields": "text, metadata (title, authors, license)",
        "ge32k_ratio": "未标注; 论文通常 8K-50K, 部分 >=32K; 需抽样实测",
        "ge128k_ratio": "未标注; 极少数超长论文; 需抽样实测",
        "evidence": "数据集卡: 从 ArXiv S3 下载 latex, LATEXML 转文本; 论文 arXiv:2506.05209",
        "notes": "版权干净论文全文。但单篇多数 8K-50K，对 >=128K 贡献有限。",
    },
    {
        "repo_id": "alea-institute/kl3m-data (系列)",
        "hf_url": "https://huggingface.co/datasets/alea-institute/kl3m-data-dotgov-www.armfor.uscourts.gov",
        "category": "法律/标准/专利类",
        "size": "KL3M 系列 (多子数据集)",
        "samples": "未核到总量",
        "tokens_est": "kl3m-004-128k-cased tokenizer; 单文档 tokens 可达 306K",
        "language": "英语",
        "license": "CC BY 4.0",
        "gated": "否",
        "updated": "2025-04 (arXiv:2504.07854)",
        "fields": "identifier, dataset, mime_type, tokens (已分词 token id 序列)",
        "ge32k_ratio": "部分文档 >=32K (法律文书天然超长); 具体占比未核到",
        "ge128k_ratio": "部分文档 >128K (tokens 字段 max 306k); 具体占比未核到",
        "evidence": "数据集卡: tokens 字段 sequencelengths 含 306k 值; copyright-clean 法律/金融文档",
        "notes": "法律文书天然超长，版权干净。但体量可能不大，且已分词 (需确认 tokenizer 兼容性)。",
    },
    {
        "repo_id": "zai-org/LongBench-v2",
        "hf_url": "https://huggingface.co/datasets/zai-org/LongBench-v2",
        "category": "长文档 QA / 评测 (非训练)",
        "size": "<1K 样本",
        "samples": "503 道 MCQ",
        "tokens_est": "N/A (评测集)",
        "language": "英语",
        "license": "Apache-2.0",
        "gated": "否",
        "updated": "2024-12 (arXiv:2412.15204)",
        "fields": "input, outputs, length, difficulty, task_category",
        "ge32k_ratio": "context 8K-2M words, 多数 <128K -> 部分样本 >=32K tokens",
        "ge128k_ratio": "部分样本 >=128K (最高 2M words)",
        "evidence": "数据集卡: 'Context length 8k to 2M words, majority under 128k'",
        "notes": "评测集不是训练集。可用于评估长上下文模型 + 了解评测分布。绝不可混入训练集。",
    },
    {
        "repo_id": "common-pile/project_gutenberg_filtered",
        "hf_url": "https://huggingface.co/datasets/common-pile/project_gutenberg_filtered",
        "category": "书籍/长文 (Gutenberg)",
        "size": "Common Pile v0.1 子集",
        "samples": "未核到",
        "tokens_est": "未核到",
        "language": "英语",
        "license": "Public Domain",
        "gated": "否",
        "updated": "2025-06",
        "fields": "text, metadata",
        "ge32k_ratio": "未标注; 与 whole-books gutenberg config 同源",
        "ge128k_ratio": "未标注; 同上",
        "evidence": "Common Pile v0.1 论文 arXiv:2506.05209; whole-books gutenberg config 即从此转换",
        "notes": "whole-books 的上游来源。如直接用 whole-books 则无需重复下载。",
    },
    {
        "repo_id": "princeton-nlp/prolong-data-512K (thestackv1_concat_by_repo)",
        "hf_url": "https://huggingface.co/datasets/princeton-nlp/prolong-data-512K",
        "category": "代码仓库级",
        "size": "6.4B tokens (524K 版 3.2B + 65K 版 3.2B)",
        "samples": "The Stack v1 按 repo 拼接",
        "tokens_est": "6.4B tokens",
        "language": "代码 (多语言)",
        "license": "未明确标注 (The Stack v1 = permissive)",
        "gated": "否",
        "updated": "2024-10",
        "fields": "同 prolong-data-512K",
        "ge32k_ratio": "65K 版: 100% >=65K; 524K 版: 100% >=524K",
        "ge128k_ratio": "524K 版: 100% >=128K; 65K 版: 0%",
        "evidence": "数据集卡标注 thestackv1_concat_by_repo-524288 和 -65536",
        "notes": "ProLong 中专门的代码仓库级数据。按 repo 拼接=多文件按目录/依赖顺序合并。与 UltraData-Code (文件级) 互补。",
    },
]

# B 类：Agentic 数据集
AGENTIC_DATASETS = [
    {
        "repo_id": "SWE-bench/SWE-smith",
        "hf_url": "https://huggingface.co/datasets/SWE-bench/SWE-smith",
        "tier": "可直接 RL",
        "size": "59,100 行 (10K-100K)",
        "samples": "59,100 task instances, 222 repos",
        "language": "英语 (代码+NL)",
        "license": "MIT",
        "gated": "否",
        "updated": "2025-05 (arXiv:2504.21798); 更新至 2025-08",
        "fields": "instance_id, patch, FAIL_TO_PASS, PASS_TO_PASS, image_name (Docker), repo, problem_statement",
        "reward_signal": "单元测试: FAIL_TO_PASS (修复后应通过) + PASS_TO_PASS (不应破坏)。需 Docker。",
        "stage": "SFT + RL",
        "contamination_risk": "中: 222 个 GitHub 仓库，部分与 SWE-bench Verified repo 重叠。SWE-smith 是自动生成任务 (非真实 issue)，但 repo 级别可能重叠。",
        "notes": "目前最大规模 SWE 训练数据 (52K+)。SWE-agent-LM-32B 在此训练达 40.2% SWE-bench Verified pass@1。需 Docker 环境执行测试。",
    },
    {
        "repo_id": "nvidia/Nemotron-Cascade-RL-SWE",
        "hf_url": "https://huggingface.co/datasets/nvidia/Nemotron-Cascade-RL-SWE",
        "tier": "可直接 RL",
        "size": "100K-1M 样本",
        "samples": "SWE-Fixer-Train 30K + SWE-Smith 3K + SWE-Bench-Train 1.5K + SWE-reBench 5.6K = ~40K",
        "language": "英语",
        "license": "CC BY 4.0",
        "gated": "否",
        "updated": "2025-12 (arXiv:2512.13607)",
        "fields": "source, instance_id, prompt, golden_patch, relevant_file_contents, original_prompt",
        "reward_signal": "执行无关奖励建模 (execution-free reward): 不用 Docker，用 reward model 评估 patch。prompt 16K-32K。",
        "stage": "RL",
        "contamination_risk": "高: 明确含 SWE-Bench-Train (1,525 样本) 和 SWE-Smith，与 SWE-bench Verified 同源仓库。",
        "notes": "NVIDIA Cascade RL，核心创新=execution-free reward。8B 达 37.2%, 14B 达 43.1% pass@1。含 SWE-Bench-Train -> 污染风险高。",
    },
    {
        "repo_id": "NovaSky-AI/SkyRL-v0-293-data",
        "hf_url": "https://huggingface.co/datasets/NovaSky-AI/SkyRL-v0-293-data",
        "tier": "可直接 RL",
        "size": "293 train + 23 val",
        "samples": "293 train + 23 validation",
        "language": "英语 (Python)",
        "license": "未核到 (SWE-Gym arXiv:2412.21139)",
        "gated": "否",
        "updated": "2024-12",
        "fields": "repo, problem_statement, base_commit, test_patch, FAIL_TO_PASS, PASS_TO_PASS",
        "reward_signal": "单元测试: SWE-Gym 环境 pytest，FAIL_TO_PASS 作为 reward。需 Docker/SWE-Gym。",
        "stage": "RL",
        "contamination_risk": "中: SWE-Gym 2,438 真实 Python tasks，与 SWE-bench Verified 部分同源。",
        "notes": "仅 293 样本即显著提升 SWE-bench Verified (7B: 11->14.6%, 14B: 18->21.6%)。适合验证 RL pipeline。需 OpenHands + VeRL。",
    },
    {
        "repo_id": "nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1",
        "hf_url": "https://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1",
        "tier": "可直接 RL",
        "size": "未核到",
        "samples": "未核到",
        "language": "英语",
        "license": "未核到 (NVIDIA 通常 CC BY 4.0)",
        "gated": "未核到 (可能需 NVIDIA 账号)",
        "updated": "未核到",
        "fields": "未核到完整字段",
        "reward_signal": "step-level pass-rate rewards: 逐步骤评估 agent 行为 pass rate",
        "stage": "RL",
        "contamination_risk": "高: NVIDIA SWE 系列，与 SWE-bench 同源",
        "notes": "Nexus-Coder-Alpha 训练指南引用为 Stage 2 RL 数据。step-level reward 更细粒度。gated 状态需实际确认。",
    },
    {
        "repo_id": "zhangdw/to-tool-call-datasets",
        "hf_url": "https://huggingface.co/datasets/zhangdw/to-tool-call-datasets",
        "tier": "只能 SFT",
        "size": "~2.4 GB JSONL",
        "samples": "244,949 训练样本",
        "language": "英语 (多语言工具定义)",
        "license": "Apache-2.0 (聚合层); 各源保留原始 license",
        "gated": "否",
        "updated": "近期",
        "fields": "messages (Qwen3 chat template), 统一格式",
        "reward_signal": "无自动验证 (SFT 数据)",
        "stage": "SFT",
        "contamination_risk": "低: 通用工具调用，与 SWE-bench/Terminal-Bench 无直接关联",
        "notes": "统一 10 个公开工具调用数据集 (APIGen-MT, BFCL, ToolBench, ToolACE, τ-bench 等) 到 Qwen3 格式。244K 样本。",
    },
    {
        "repo_id": "mshojaei77/terminal-command-execution-sft",
        "hf_url": "https://huggingface.co/datasets/mshojaei77/terminal-command-execution-sft",
        "tier": "只能 SFT",
        "size": "10K-100K",
        "samples": "7 个源数据集聚合",
        "language": "英语",
        "license": "other (混合源)",
        "gated": "否",
        "updated": "未核到",
        "fields": "messages, source_dataset, shell_family (9 类), skill (17 类), safety_label (6 类)",
        "reward_signal": "无自动验证 (SFT 数据)",
        "stage": "SFT",
        "contamination_risk": "低: 合成/改写终端命令，非 Terminal-Bench 原始任务",
        "notes": "9 种 shell, 17 种技能, 6 级安全标签。适合 Terminal-Bench 方向 SFT。但非真实终端交互轨迹。",
    },
    {
        "repo_id": "Nethraaaaa81/swev-trm-trajectories-25models",
        "hf_url": "https://huggingface.co/datasets/Nethraaaaa81/swev-trm-trajectories-25models",
        "tier": "SFT + 奖励模型训练",
        "size": "train 10,107 + val 2,366",
        "samples": "12,473 轨迹 (25 个 LLM 在 SWE-bench Verified)",
        "language": "英语",
        "license": "MIT",
        "gated": "否",
        "updated": "近期",
        "fields": "trajectory_id, task_id, agent_name, model, reward (1.0=resolved/0.0=failed), messages",
        "reward_signal": "SWE-bench harness verdict (resolved/failed)。可训练 Trajectory Reward Model (TRM)。",
        "stage": "SFT (成功轨迹) + TRM 训练 (全部)",
        "contamination_risk": "高: 直接在 SWE-bench Verified 任务上生成，task_id = SWE-bench instance_id",
        "notes": "直接用 SWE-bench Verified 生成 -> 污染极高。可用于: (1) 训练 TRM; (2) 分析 25 模型成功/失败模式。",
    },
    {
        "repo_id": "hariharasudharsanj-008/agent-data-collection (SWE-Gym)",
        "hf_url": "https://huggingface.co/datasets/hariharasudharsanj-008/agent-data-collection",
        "tier": "SFT (轨迹)",
        "size": "未核到",
        "samples": "SWE-Gym 2,438 任务子集",
        "language": "英语",
        "license": "未核到",
        "gated": "否",
        "updated": "2024-12",
        "fields": "agent trajectories (多轮对话)",
        "reward_signal": "可附带 resolved 标签 (SWE-Gym 测试)",
        "stage": "SFT (成功轨迹)",
        "contamination_risk": "中: SWE-Gym 与 SWE-bench 部分同源",
        "notes": "SWE-Gym OpenHands 采样轨迹，含成功/失败标签。SWE-Gym 论文报告 19% 绝对提升在 SWE-bench Verified。",
    },
]

EXISTING_SOURCES = [
    "ultrafineweb_en_v1_4 (110 shard, 2237B tokens)",
    "ultrafineweb_en_l3/qa (154 shard, 264B tokens)",
    "UltraData-Code-L2 (141 shard, 421B tokens)",
    "UltraData-Code-L3 (63 shard, 129B tokens)",
    "UltraData-Math-L1 (149 shard, 164B tokens)",
    "UltraData-Math-L3 (67 shard, 78B tokens)",
    "ultrafineweb_en (32 shard, 906B tokens)",
    "ultrafineweb_l1_en_hq (94 shard, 150B tokens)",
    "ultrafineweb_zh (4 shard, 113B tokens)",
    "UltraX-AICC (1 shard, 11B tokens)",
    "UltraData-SFT-2605 (94 shard, 19B tokens)",
    "UltraData-SFT-Agent-2609 (13 shard, 6B tokens)",
]

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif; line-height: 1.7; color: #1a1a2e; background: #f5f5fa; padding: 20px; max-width: 1400px; margin: 0 auto; }
h1 { font-size: 1.6em; color: #0f3460; margin: 20px 0 10px; padding-bottom: 8px; border-bottom: 3px solid #0f3460; }
h2 { font-size: 1.3em; color: #16213e; margin: 25px 0 12px; padding-left: 12px; border-left: 5px solid #0f3460; }
h3 { font-size: 1.1em; color: #1a1a4e; margin: 18px 0 8px; }
h4 { font-size: 1.0em; color: #333; margin: 14px 0 6px; }
p { margin: 8px 0; }
ul, ol { margin: 8px 0 8px 24px; }
li { margin: 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.88em; }
th, td { border: 1px solid #ccc; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #0f3460; color: #fff; font-weight: 600; }
tr:nth-child(even) { background: #f0f0f5; }
tr:hover { background: #e8e8f0; }
code { background: #e8e8f0; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; color: #c0392b; }
pre { background: #1a1a2e; color: #e0e0e0; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 10px 0; font-size: 0.85em; }
pre code { background: none; color: inherit; }
.note { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 14px; margin: 10px 0; border-radius: 0 4px 4px 0; }
.warning { background: #f8d7da; border-left: 4px solid #dc3545; padding: 10px 14px; margin: 10px 0; border-radius: 0 4px 4px 0; }
.success { background: #d4edda; border-left: 4px solid #28a745; padding: 10px 14px; margin: 10px 0; border-radius: 0 4px 4px 0; }
.info { background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 10px 14px; margin: 10px 0; border-radius: 0 4px 4px 0; }
.tag-rl { background: #28a745; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }
.tag-sft { background: #17a2b8; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }
.tag-high { background: #dc3545; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }
.tag-mid { background: #ffc107; color: #333; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }
.tag-low { background: #28a745; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }
.meta { color: #666; font-size: 0.85em; margin-bottom: 15px; }
.tldr-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 12px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.tldr-card h4 { color: #0f3460; margin-top: 0; }
.footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #ccc; color: #666; font-size: 0.85em; }
a { color: #0f3460; text-decoration: none; }
a:hover { text-decoration: underline; }
"""

def esc(text):
    return html.escape(str(text), quote=True)

def hf_link(repo_id, hf_url):
    return f'<a href="{esc(hf_url)}">{esc(repo_id)}</a>'

def section_tldr():
    return """
<h1>白泽长上下文 &amp; Agentic 数据集 HuggingFace 调研报告</h1>
<p class="meta">调研日期: 2026-10-31 ｜ 调研执行: data 线 (唤醒 1044) ｜ 调研方法: web search 检索 hf.co 数据集页面，逐条核实元信息</p>

<h2 id="sec1">§1 TL;DR — 两类各 TOP-3 推荐</h2>

<div class="tldr-card">
<h4>🏷️ A 类 · 长上下文 TOP-3 推荐</h4>
<table>
<tr><th>#</th><th>数据集</th><th>推荐理由</th><th>预计下载体量</th></tr>
<tr>
  <td>1</td>
  <td><a href="https://huggingface.co/datasets/ysngkil/whole-books">ysngkil/whole-books</a></td>
  <td>20.2 万本完整书籍，87-98% token 在 ≥64K 书中，一行=一整本书，直接解决 ≥32K 文档不足问题。5 个 config 覆盖 Gutenberg/DOAB/教科书。</td>
  <td>~25 GiB</td>
</tr>
<tr>
  <td>2</td>
  <td><a href="https://huggingface.co/datasets/princeton-nlp/prolong-data-512K">princeton-nlp/prolong-data-512K</a></td>
  <td>31B tokens，含 repo-level 代码拼接 (524K/65K) + 书籍 (524K/65K) + 混合短数据。Princeton ProLong 论文验证过的长上下文训练配方。</td>
  <td>~120 GiB (MDS 格式, 31B tokens)</td>
</tr>
<tr>
  <td>3</td>
  <td><a href="https://huggingface.co/datasets/caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1">caskcsg/NExtLong</a></td>
  <td>合成长上下文 (64K-512K)，不依赖真实长文档——用短文档+负例干扰合成。在我们真实长文档不足时是有效补充。HELMET/RULER 上优于非合成方法。</td>
  <td>未核到 (预计 &lt;50 GiB)</td>
</tr>
</table>
<p><strong>预计总下载体量 (A 类 TOP-3):</strong> ~170-200 GiB</p>
</div>

<div class="tldr-card">
<h4>🤖 B 类 · Agentic TOP-3 推荐</h4>
<table>
<tr><th>#</th><th>数据集</th><th>推荐理由</th><th>预计下载体量</th></tr>
<tr>
  <td>1</td>
  <td><a href="https://huggingface.co/datasets/SWE-bench/SWE-smith">SWE-bench/SWE-smith</a></td>
  <td>59K task instances，含 patch + 单测 (FAIL_TO_PASS/PASS_TO_PASS)，可直接 RL。MIT 协议，222 个仓库。SWE-agent-LM-32B 在此训练达 40.2% SWE-bench Verified。</td>
  <td>~5-10 GiB (parquet)</td>
</tr>
<tr>
  <td>2</td>
  <td><a href="https://huggingface.co/datasets/zhangdw/to-tool-call-datasets">zhangdw/to-tool-call-datasets</a></td>
  <td>244K 工具调用样本，统一 Qwen3 格式，聚合 10 个公开源 (BFCL/ToolBench/ToolACE/τ-bench 等)。SFT 首选，污染风险低。</td>
  <td>~2.4 GiB</td>
</tr>
<tr>
  <td>3</td>
  <td><a href="https://huggingface.co/datasets/nvidia/Nemotron-Cascade-RL-SWE">nvidia/Nemotron-Cascade-RL-SWE</a></td>
  <td>NVIDIA 执行无关 RL 数据 (不需 Docker 跑测试)，40K+ 样本，CC BY 4.0。14B 模型达 43.1% resolve rate。⚠️ 含 SWE-Bench-Train，污染风险高，需去污染。</td>
  <td>~10-20 GiB</td>
</tr>
</table>
<p><strong>预计总下载体量 (B 类 TOP-3):</strong> ~20-35 GiB</p>
</div>

<div class="info">
<p><strong>⚠️ 红线提醒：</strong>本轮<strong>只调研 + 写报告，不下载任何数据</strong>。下载需待 85M 下载完成 (当前 ~87.7%) 后另轮执行。</p>
</div>
"""

def section_method():
    return """
<h2 id="sec2">§2 检索方法与口径</h2>

<h3>2.1 检索工具与流程</h3>
<ul>
<li><strong>检索工具</strong>: 使用 web search 服务 (cimi_search) 以自然语言查询 HuggingFace 数据集，再用 cimi_fetch 抓取数据集页面全文。</li>
<li><strong>检索查询</strong>: 共发起 12 轮针对性搜索，覆盖: 长上下文训练数据、128K context、RULER/NIAH、Gutenberg 书籍、ProLong、法律/专利文档、Wikipedia 全文、repo-level 代码拼接、SWE-Gym/SWE-smith、Terminal-Bench、ToolBench/BFCL、Nemotron agentic、SWE-bench 污染。</li>
<li><strong>逐条核实</strong>: 对每个候选数据集，尝试打开其 HF 页面，核实: repo id、体量、语言、license、gated 状态、字段结构、更新时间。</li>
<li><strong>HF 页面可达性</strong>: fetch_web_content 无法直接访问 hf.co (连接被拒)，改用 cimi_fetch 成功抓取部分页面；部分数据集仅从搜索结果摘要中获取元信息。</li>
</ul>

<h3>2.2 已核实字段 vs 未核实字段</h3>
<table>
<tr><th>字段</th><th>已核实</th><th>未核实 / 限制</th></tr>
<tr><td>repo id</td><td>✅ 全部</td><td>—</td></tr>
<tr><td>体量</td><td>✅ 大部分</td><td>NExtLong/Nemotron-Pivot 的确切体量未核到</td></tr>
<tr><td>语言</td><td>✅ 全部</td><td>—</td></tr>
<tr><td>license</td><td>✅ 大部分</td><td>ProLong/SkyRL/Nemotron-Pivot 的 license 未明确标注</td></tr>
<tr><td>gated 状态</td><td>✅ 大部分</td><td>Nemotron-Pivot 的 gated 状态未核到</td></tr>
<tr><td>字段结构</td><td>✅ 大部分</td><td>NExtLong/SkyRL 部分字段未完整核到</td></tr>
<tr><td>≥32K / ≥128K 占比</td><td>✅ whole-books (数据卡标注 ≥64K)</td><td>多数数据集未标注 → 标记「需抽样实测」</td></tr>
<tr><td>更新时间</td><td>✅ 大部分</td><td>部分仅核到论文发表日期</td></tr>
</table>

<h3>2.3 关键口径说明</h3>
<div class="warning">
<p><strong>⚠️ HF 数据集体量以数据集卡为准，与实际下载字节可能差异大</strong>。原因: (1) 数据集卡标注原始大小，下载后可能解压更大; (2) MDS/packed 格式字节与 token 数不直接对应; (3) HF xet 存储可能使用压缩。实际体量需以 hf download 实测为准。</p>
</div>
<div class="info">
<p><strong>≥32K / ≥128K 占比</strong>是核心筛选指标。当前 en_v1_4 中 ≥32K 文档仅占 2.52% token、≥128K 仅 0.03%，目标 ≥20% / ≥5%。「数据量大」不是重点，「真有长文档」才是。</p>
</div>
"""

def section_a_table():
    rows = []
    for i, ds in enumerate(LONG_CONTEXT_DATASETS, 1):
        rows.append(f"""
<tr>
<td>{i}</td>
<td>{hf_link(ds['repo_id'], ds['hf_url'])}</td>
<td>{esc(ds['category'])}</td>
<td>{esc(ds['size'])}</td>
<td>{esc(ds['language'])}</td>
<td>{esc(ds['license'])}</td>
<td>{esc(ds['gated'])}</td>
<td>{esc(ds['ge32k_ratio'])}</td>
<td>{esc(ds['ge128k_ratio'])}</td>
<td>{esc(ds['evidence'])}</td>
</tr>""")
    rows_html = "\n".join(rows)
    cards = []
    for i, ds in enumerate(LONG_CONTEXT_DATASETS, 1):
        cards.append(f"""
<div class="tldr-card">
<h4>{i}. {hf_link(ds['repo_id'], ds['hf_url'])} <small>[{esc(ds['category'])}]</small></h4>
<table>
<tr><th>体量</th><td>{esc(ds['size'])}</td></tr>
<tr><th>样本数</th><td>{esc(ds['samples'])}</td></tr>
<tr><th>Token 估算</th><td>{esc(ds['tokens_est'])}</td></tr>
<tr><th>语言</th><td>{esc(ds['language'])}</td></tr>
<tr><th>License</th><td>{esc(ds['license'])}</td></tr>
<tr><th>Gated</th><td>{esc(ds['gated'])}</td></tr>
<tr><th>更新时间</th><td>{esc(ds['updated'])}</td></tr>
<tr><th>字段结构</th><td>{esc(ds['fields'])}</td></tr>
<tr><th>≥32K 占比</th><td>{esc(ds['ge32k_ratio'])}</td></tr>
<tr><th>≥128K 占比</th><td>{esc(ds['ge128k_ratio'])}</td></tr>
<tr><th>证据来源</th><td>{esc(ds['evidence'])}</td></tr>
<tr><th>备注</th><td>{esc(ds['notes'])}</td></tr>
</table>
</div>""")
    cards_html = "\n".join(cards)
    return f"""
<h2 id="sec3">§3 A 类主表 — 长上下文数据集候选</h2>

<p>背景约束: decay-B 段当前卡在数据闸门 —— en_v1_4 中 ≥32K 文档仅占 2.52% token、≥128K 仅 0.03%，目标 ≥20% / ≥5% (论文 §4.5 与 configs/longctx_ladder.tsv)。本类调研核心不是"数据量大"，而是"真有长文档"。</p>

<h3>3.1 候选总表</h3>
<table>
<tr>
<th>#</th><th>Repo ID</th><th>类别</th><th>体量</th><th>语言</th><th>License</th><th>Gated</th>
<th>≥32K 占比</th><th>≥128K 占比</th><th>证据来源</th>
</tr>
{rows_html}
</table>

<h3>3.2 候选详细卡片</h3>
{cards_html}

<h3>3.3 按方向分类汇总</h3>
<h4>① 书籍/长文</h4>
<ul>
<li><strong>ysngkil/whole-books</strong> — 20.2 万本完整书，87-98% ≥64K，最直接的长文档来源</li>
<li><strong>common-pile/arxiv_papers_filtered</strong> — 版权干净论文全文 (CC BY/SA/CC0)，多数 8K-50K，对 ≥128K 贡献有限</li>
<li><strong>common-pile/project_gutenberg_filtered</strong> — whole-books 的上游，无需重复下载</li>
</ul>
<h4>② 代码仓库级 (repo-level 拼接)</h4>
<ul>
<li><strong>princeton-nlp/prolong-data-512K (thestackv1_concat_by_repo)</strong> — The Stack v1 按 repo 拼接到 524K/65K，6.4B tokens。与 UltraData-Code (文件级) 互补</li>
</ul>
<h4>③ 长文档 QA / 合成 haystack</h4>
<ul>
<li><strong>utter-project/LongBlocks</strong> — 194K 长上下文 QA，20 语言，含 3 教师模型响应</li>
<li><strong>zai-org/LongBench-v2</strong> — ⚠️ 评测集 (503 MCQ)，不可入训练，但可指导配比</li>
</ul>
<h4>④ 长上下文训练集</h4>
<ul>
<li><strong>princeton-nlp/prolong-data-512K</strong> — 31B tokens，系统化长上下文训练数据 (Princeton 论文验证)</li>
<li><strong>caskcsg/NExtLong</strong> — 合成长上下文 64K-512K，不依赖真实长文档</li>
</ul>
<h4>⑤ 法律/标准/专利类</h4>
<ul>
<li><strong>alea-institute/kl3m-data (系列)</strong> — 法律/金融文档，版权干净，单文档可达 306K tokens</li>
</ul>

<div class="warning">
<p><strong>⚠️ 未验证长文档占比的数据集</strong> (必须单列，不可默认满足闸门):</p>
<ul>
<li><strong>common-pile/arxiv_papers_filtered</strong> — 论文多数 8K-50K，≥32K 占比未标注，需抽样实测</li>
<li><strong>utter-project/LongBlocks</strong> — ≥32K/≥128K 占比未标注，需抽样实测</li>
<li><strong>alea-institute/kl3m-data</strong> — ≥32K/≥128K 具体占比未标注 (但数据卡显示部分文档 306K tokens)，需抽样实测</li>
</ul>
<p><strong>抽样方法建议</strong>: 下载后随机抽 1000 条，用我们的 tokenizer 分词，统计 P50/P90/P99/max 和 ≥32K/≥128K 占比，写入 DATA_MAPPING.md。</p>
</div>
"""

def section_b_table():
    rows = []
    for i, ds in enumerate(AGENTIC_DATASETS, 1):
        tier_class = "tag-rl" if "RL" in ds['tier'] else "tag-sft"
        cont_text = ds['contamination_risk'].split(":")[0].strip()
        cont_class = "tag-high" if "高" in cont_text else ("tag-mid" if "中" in cont_text else "tag-low")
        rows.append(f"""
<tr>
<td>{i}</td>
<td>{hf_link(ds['repo_id'], ds['hf_url'])}</td>
<td><span class="{tier_class}">{esc(ds['tier'])}</span></td>
<td>{esc(ds['size'])}</td>
<td>{esc(ds['reward_signal'])}</td>
<td>{esc(ds['stage'])}</td>
<td><span class="{cont_class}">{esc(cont_text)}</span></td>
</tr>""")
    rows_html = "\n".join(rows)
    cards = []
    for i, ds in enumerate(AGENTIC_DATASETS, 1):
        cards.append(f"""
<div class="tldr-card">
<h4>{i}. {hf_link(ds['repo_id'], ds['hf_url'])} <small>[{esc(ds['tier'])}]</small></h4>
<table>
<tr><th>体量</th><td>{esc(ds['size'])}</td></tr>
<tr><th>样本数</th><td>{esc(ds['samples'])}</td></tr>
<tr><th>语言</th><td>{esc(ds['language'])}</td></tr>
<tr><th>License</th><td>{esc(ds['license'])}</td></tr>
<tr><th>Gated</th><td>{esc(ds['gated'])}</td></tr>
<tr><th>更新时间</th><td>{esc(ds['updated'])}</td></tr>
<tr><th>字段结构</th><td>{esc(ds['fields'])}</td></tr>
<tr><th>奖励信号类型</th><td>{esc(ds['reward_signal'])}</td></tr>
<tr><th>适用阶段</th><td>{esc(ds['stage'])}</td></tr>
<tr><th>污染风险</th><td>{esc(ds['contamination_risk'])}</td></tr>
<tr><th>备注</th><td>{esc(ds['notes'])}</td></tr>
</table>
</div>""")
    cards_html = "\n".join(cards)
    return f"""
<h2 id="sec4">§4 B 类主表 — Agentic 数据集候选</h2>

<p>目标: 提升白泽在 <strong>SWE-bench Verified</strong> &amp; <strong>Terminal Bench</strong> 的表现。分两层: 可直接 RL (有可执行验证信号) vs 只能 SFT (无自动验证)。</p>

<h3>4.1 候选总表</h3>
<table>
<tr>
<th>#</th><th>Repo ID</th><th>层级</th><th>体量</th><th>奖励信号类型</th><th>适用阶段</th><th>污染风险</th>
</tr>
{rows_html}
</table>

<h3>4.2 候选详细卡片</h3>
{cards_html}

<h3>4.3 按层级分类</h3>
<h4>① 可直接 RL (有可执行验证信号)</h4>
<ul>
<li><strong>SWE-bench/SWE-smith</strong> — 59K instances，单测 (FAIL_TO_PASS/PASS_TO_PASS) 作为 reward，需 Docker。MIT。🟡 中等污染风险。</li>
<li><strong>nvidia/Nemotron-Cascade-RL-SWE</strong> — 40K+ 样本，execution-free reward model (不需 Docker)。CC BY 4.0。🔴 高污染风险 (含 SWE-Bench-Train)。</li>
<li><strong>NovaSky-AI/SkyRL-v0-293-data</strong> — 293 train tasks，SWE-Gym 单测 reward。小数据量验证 RL pipeline。🟡 中等。</li>
<li><strong>nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1</strong> — step-level pass-rate reward，细粒度。🔴 高污染风险。gated 状态未核到。</li>
</ul>
<p><strong>奖励信号来源汇总</strong>: 单元测试 (SWE-smith, SkyRL) > 执行无关奖励模型 (Nemotron-Cascade) > step-level pass-rate (Nemotron-Pivot)。单测最可靠但需 Docker；execution-free 最轻量但依赖 reward model 质量。</p>

<h4>② 只能 SFT (无自动验证)</h4>
<ul>
<li><strong>zhangdw/to-tool-call-datasets</strong> — 244K 工具调用，统一 Qwen3 格式，10 个公开源聚合。🟢 低污染。</li>
<li><strong>mshojaei77/terminal-command-execution-sft</strong> — 终端命令 SFT，9 种 shell, 17 种技能。🟢 低污染。适合 Terminal-Bench 方向。</li>
<li><strong>Nethraaaaa81/swev-trm-trajectories-25models</strong> — 25 个 LLM 在 SWE-bench Verified 上的轨迹，可训练 TRM。🔴 高污染 (直接用 Verified 任务)。</li>
<li><strong>hariharasudharsanj-008/agent-data-collection</strong> — SWE-Gym OpenHands 轨迹。🟡 中等污染。</li>
</ul>

<h4>③ 与 SWE-bench Verified / Terminal Bench 的对齐风险</h4>
<div class="warning">
<p><strong>🔴 SWE-bench Verified 污染风险</strong> (2026-07 公开报道证实):</p>
<ul>
<li>SWE-bench Verified 的 500 个任务来自公开 GitHub 仓库 → 这些 repo/issue/PR/commit history 在每个大型 web crawl 中都存在 → 模型训练数据中已隐含见过答案。</li>
<li>SWE-bench Live (2026-05 发布，用训练截止日期后的 issue) 显示: 模型在 Verified 上 70+ 分 → Live 上 50+ 分，差距 ~20 分，跨厂商一致。</li>
<li><strong>我们的去污染方案</strong>: 已有 193,295 条 13-gram 指纹黑名单机制 (见 CONTAMINATION_CHECK.md)，可直接复用。建议: (1) 从 SWE-bench Verified 的 500 个 instance_id 提取 patch + problem_statement + test 内容; (2) 生成 13-gram 指纹加入黑名单; (3) 对所有候选训练数据做 13-gram 扫描，命中即过滤。</li>
<li><strong>SWE-smith 特别注意</strong>: 222 个 repo 与 SWE-bench Verified 的 repo 有重叠 → 即使 task instance 不同，同 repo 的代码风格/依赖/API 模式可能泄露信息。建议 repo 级去重: 排除与 Verified 完全相同 repo 的 SWE-smith instances。</li>
</ul>
</div>
<div class="warning">
<p><strong>🟡 Terminal-Bench 污染风险</strong>:</p>
<ul>
<li>Terminal-Bench ~100 个任务，来自公开 GitHub 仓库 → 同样的 web crawl 污染风险。</li>
<li>Terminal-Bench 的 task instruction + test script 应提取 13-gram 指纹加入黑名单。</li>
<li><strong>mshojaei77/terminal-command-execution-sft</strong> 是合成/改写数据，非 Terminal-Bench 原始任务 → 污染风险低，但需确认源数据集不含 Terminal-Bench 测试脚本。</li>
</ul>
</div>
"""

def section_contamination():
    existing_items = "\n".join(f"<li>{esc(s)}</li>" for s in EXISTING_SOURCES)
    return f"""
<h2 id="sec5">§5 污染与去重</h2>

<h3>5.1 与现有 12 源的重叠分析</h3>
<p>我们盘上现有 12 个数据源 (来自 DATA_MAPPING.md):</p>
<ul>
{existing_items}
</ul>
<div class="info">
<p><strong>重叠分析</strong>:</p>
<ul>
<li><strong>A 类 (长上下文) 与现有源重叠</strong>: ProLong 的 fineweb-edu/fineweb-2023-50 子集与 Ultra-FineWeb 系列同源 (FineWeb)，但 ProLong 是 Variable 长度、用于与长数据混合。ProLong 的 thestackv1 子集与 UltraData-Code 同源 (The Stack v1)，但 ProLong 是 repo-level 拼接而 UltraData-Code 是文件级 → 格式不同，可互补。whole-books 与现有源无重叠 (我们盘上无书籍数据)。</li>
<li><strong>B 类 (agentic) 与现有源重叠</strong>: UltraData-SFT-Agent-2609 (6B tokens) 是已有的 agent SFT 数据，但来源和格式与上述 HF 候选不同。SWE-smith/Nemotron-Cascade 等均为新增，无重叠。</li>
<li><strong>结论</strong>: A/B 两类候选与现有 12 源基本无重复推荐，可安全新增。</li>
</ul>
</div>

<h3>5.2 与两个目标基准的污染风险</h3>
<table>
<tr><th>基准</th><th>任务来源</th><th>污染机制</th><th>风险</th><th>去污染方案</th></tr>
<tr>
<td>SWE-bench Verified</td>
<td>500 个公开 GitHub repo issue</td>
<td>repo/issue/PR/commit 在 web crawl 中 → 预训练已隐含见过; SWE-smith 222 repo 部分重叠</td>
<td><span class="tag-high">高</span></td>
<td>① 13-gram 指纹黑名单 (已有 193,295 条); ② repo 级去重: 排除与 Verified 相同 repo; ③ 使用 SWE-bench Live 辅助评测</td>
</tr>
<tr>
<td>Terminal-Bench</td>
<td>~100 个公开 GitHub 仓库任务</td>
<td>task instruction + test script 在 web crawl 中; 但 Terminal-Bench 较新，污染窗口较短</td>
<td><span class="tag-mid">中</span></td>
<td>① 提取 Terminal-Bench task 13-gram; ② 对 terminal-command-execution-sft 扫描 (合成数据，风险低); ③ Terminal-Bench 作为 held-out 评测</td>
</tr>
</table>

<h3>5.3 去污染方案 (可复用现有机制)</h3>
<div class="success">
<p><strong>我们已有的去污染基础设施</strong> (见 CONTAMINATION_CHECK.md):</p>
<ol>
<li><strong>13-gram 指纹黑名单</strong>: 193,295 条指纹，用于 EDA-Eval-PyAether 污染隔离。可直接扩展: 将 SWE-bench Verified (500) + Terminal-Bench (~100) 的 patch/problem_statement/test 生成 13-gram 加入黑名单。</li>
<li><strong>训练集侧扫描脚本</strong>: run/data_pipeline/ 中的指纹比对脚本可直接用于新数据。</li>
<li><strong>阈值写明可复现</strong>: 现有阈值 (13-gram exact match) 可复用。</li>
<li><strong>SFT 语料同闸</strong>: SFT 数据同样需过 13-gram 扫描。</li>
<li><strong>独立报告</strong>: 去污染结果写入 CONTAMINATION_CHECK.md 更新。</li>
</ol>
</div>
<div class="note">
<p><strong>repo 级去重 (额外建议)</strong>: 13-gram 去重可能漏掉「同 repo 不同 issue」的风格泄露。建议: 对 SWE-smith 的 222 个 repo，与 SWE-bench Verified 的 repo 列表做交集，交集 repo 的 instances 标记为「高风险」，训练时单独跟踪消融效果。</p>
</div>
"""

def section_download():
    return """
<h2 id="sec6">§6 下载方案</h2>

<div class="warning">
<p><strong>⚠️ 红线: 本轮只调研 + 写报告，不下载任何数据</strong>。磁盘与带宽要留给 85M 下载 (当前 ~87.7%) 与训练。以下方案供下轮执行参考。</p>
</div>

<h3>6.1 建议下载数据集 (按优先级)</h3>
<table>
<tr><th>优先级</th><th>数据集</th><th>类别</th><th>预计体量</th><th>落盘路径</th><th>理由</th></tr>
<tr><td>P0</td><td>ysngkil/whole-books</td><td>A 长上下文</td><td>~25 GiB</td><td>/nas_env/datasets/whole-books/</td><td>直接解决 ≥32K 不足，87-98% ≥64K</td></tr>
<tr><td>P0</td><td>SWE-bench/SWE-smith</td><td>B agentic</td><td>~5-10 GiB</td><td>/nas_env/datasets/swe-smith/</td><td>最大 SWE 训练数据，可 RL，MIT</td></tr>
<tr><td>P1</td><td>princeton-nlp/prolong-data-512K</td><td>A 长上下文</td><td>~120 GiB</td><td>/nas_env/datasets/prolong-data-512K/</td><td>系统化长上下文训练配方</td></tr>
<tr><td>P1</td><td>zhangdw/to-tool-call-datasets</td><td>B agentic</td><td>~2.4 GiB</td><td>/nas_env/datasets/to-tool-call/</td><td>244K 工具调用 SFT，低污染</td></tr>
<tr><td>P2</td><td>caskcsg/NExtLong</td><td>A 长上下文</td><td>&lt;50 GiB</td><td>/nas_env/datasets/nextlong/</td><td>合成长上下文，真实长文档不足时补充</td></tr>
<tr><td>P2</td><td>nvidia/Nemotron-Cascade-RL-SWE</td><td>B agentic</td><td>~10-20 GiB</td><td>/nas_env/datasets/nemotron-cascade-rl/</td><td>execution-free RL，但需去污染</td></tr>
<tr><td>P3</td><td>mshojaei77/terminal-command-execution-sft</td><td>B agentic</td><td>&lt;5 GiB</td><td>/nas_env/datasets/terminal-sft/</td><td>Terminal-Bench 方向 SFT</td></tr>
<tr><td>P3</td><td>utter-project/LongBlocks</td><td>A 长上下文</td><td>未核到</td><td>/nas_env/datasets/longblocks/</td><td>多语言长上下文 QA</td></tr>
</table>
<p><strong>预计总下载体量: ~215-240 GiB</strong> (P0+P1: ~150 GiB; P2: ~60 GiB; P3: ~10 GiB)</p>

<h3>6.2 落盘路径规范</h3>
<ul>
<li>遵循现有 /nas_env 规范 (新增下载落盘位置)</li>
<li>路径格式: /nas_env/datasets/&lt;repo-id-simplified&gt;/</li>
<li>下载后需: (1) du -sb 实测字节; (2) 随机抽 1000 条分词统计 ≥32K/≥128K 占比; (3) 更新 DATA_MAPPING.md</li>
<li>⚠️ /nas_env 当前余量 ~1.7 TiB (84% 已用) → P0+P1 (~150 GiB) 可容纳; P2+P3 需确认余量</li>
</ul>

<h3>6.3 hf download 命令模板</h3>
<pre><code># 环境准备 (代理 + HF token)
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128

# P0: whole-books (~25 GiB)
hf download ysngkil/whole-books --repo-type dataset --local-dir /nas_env/datasets/whole-books/

# P0: SWE-smith (~5-10 GiB)
hf download SWE-bench/SWE-smith --repo-type dataset --local-dir /nas_env/datasets/swe-smith/

# P1: ProLong data (~120 GiB, MDS 格式, 需 mosaicml-streaming)
hf download princeton-nlp/prolong-data-512K --repo-type dataset --local-dir /nas_env/datasets/prolong-data-512K/

# P1: to-tool-call-datasets (~2.4 GiB)
hf download zhangdw/to-tool-call-datasets --repo-type dataset --local-dir /nas_env/datasets/to-tool-call/

# P2: NExtLong
hf download caskcsg/NExtLong-Instruct-dataset-Magpie-Llama-3.3-Pro-1M-v0.1 --repo-type dataset --local-dir /nas_env/datasets/nextlong/

# P2: Nemotron-Cascade-RL-SWE
hf download nvidia/Nemotron-Cascade-RL-SWE --repo-type dataset --local-dir /nas_env/datasets/nemotron-cascade-rl/

# P3: terminal-command-execution-sft
hf download mshojaei77/terminal-command-execution-sft --repo-type dataset --local-dir /nas_env/datasets/terminal-sft/
</code></pre>

<h3>6.4 预计磁盘与 ETA</h3>
<table>
<tr><th>批次</th><th>数据集</th><th>体量</th><th>带宽 (~23 MB/s)</th><th>ETA</th></tr>
<tr><td>P0</td><td>whole-books + SWE-smith</td><td>~35 GiB</td><td>~23 MB/s</td><td>~25 min</td></tr>
<tr><td>P1</td><td>ProLong + to-tool-call</td><td>~122 GiB</td><td>~23 MB/s</td><td>~87 min</td></tr>
<tr><td>P2</td><td>NExtLong + Nemotron-Cascade</td><td>~60 GiB</td><td>~23 MB/s</td><td>~43 min</td></tr>
<tr><td>P3</td><td>terminal-sft + LongBlocks</td><td>~10 GiB</td><td>~23 MB/s</td><td>~7 min</td></tr>
<tr><td colspan="2"><strong>合计</strong></td><td><strong>~227 GiB</strong></td><td></td><td><strong>~2.6 h</strong></td></tr>
</table>
<div class="note">
<p><strong>⚠️ 带宽说明</strong>: 当前实测 ~23 MB/s (85M 下载在跑)。待 85M 完成后带宽可能提升。ETA 按 23 MB/s 保守估算。实际下载应在 85M 完成后 (预计 ~2.6 天) 执行。</p>
<p><strong>⚠️ 磁盘说明</strong>: /nas_env 当前 8.3T/10T (84%), 余 1.7T。P0+P1 (~157 GiB) 安全; 全量 (~227 GiB) 也安全。</p>
</div>
"""

def section_honesty():
    return """
<h2 id="sec7">§7 诚实条款</h2>

<h3>7.1 未核到的字段</h3>
<table>
<tr><th>数据集</th><th>未核到的字段</th><th>原因</th><th>后续核实建议</th></tr>
<tr><td>caskcsg/NExtLong</td><td>确切体量、样本数、license、完整字段</td><td>搜索结果仅获取论文描述，未成功抓取完整数据集卡</td><td>直接访问 HF 页面核实</td></tr>
<tr><td>nvidia/Nemotron-RL-Agentic-SWE-Pivot-v1</td><td>体量、样本数、license、gated、字段</td><td>仅从 Nexus-Coder-Alpha 训练指南中引用</td><td>直接访问 HF 页面，可能需 NVIDIA 账号</td></tr>
<tr><td>NovaSky-AI/SkyRL-v0-293-data</td><td>license</td><td>数据集卡未明确标注</td><td>查看 GitHub repo (SkyRL) license</td></tr>
<tr><td>common-pile/arxiv_papers_filtered</td><td>arxiv 子集单独体量/token 数</td><td>Common Pile v0.1 总计 8TB，子集未单独标注</td><td>下载后 du -sb 实测</td></tr>
<tr><td>alea-institute/kl3m-data</td><td>系列总量、≥32K/≥128K 具体占比</td><td>KL3M 是系列数据集，未逐一核实</td><td>逐子集访问 HF 页面</td></tr>
<tr><td>utter-project/LongBlocks</td><td>确切字节、≥32K/≥128K 占比</td><td>数据集卡未标注占比</td><td>下载后抽样实测</td></tr>
</table>

<h3>7.2 代理指标 vs 实测</h3>
<div class="note">
<p>本报告中以下指标为<strong>代理指标</strong> (非实测):</p>
<ul>
<li><strong>whole-books 的 ≥64K 占比</strong>: 来自数据集卡估算 (32K vocab tokenizer)，与我们 129,281 vocab 不同 → 实际占比需用我们的 tokenizer 重新分词后统计。</li>
<li><strong>ProLong 的 100% ≥524K/≥65K</strong>: 设计规格 (固定序列长度打包)，非文档自然长度统计。打包后的序列可能包含多个短文档拼接。</li>
<li><strong>KL3M 的 306K tokens</strong>: 数据集卡 Viewer 中 tokens 字段 sequencelengths 最大值，是单文档最大值，不代表分布。</li>
<li><strong>所有「需抽样实测」标注</strong>: 意味着我们尚未验证该数据集的实际长文档分布。</li>
</ul>
</div>

<h3>7.3 License 风险</h3>
<table>
<tr><th>数据集</th><th>License</th><th>风险说明</th></tr>
<tr><td>ysngkil/whole-books</td><td>mixed-public-domain-and-CC</td><td>每行自带 license 字段，需逐行检查; Gutenberg=PD, DOAB=CC BY, textbooks=CC BY-SA 等</td></tr>
<tr><td>princeton-nlp/prolong-data-512K</td><td>未明确标注</td><td>论文 MIT, 但数据来自 The Stack (permissive) + SlimPajama (mixed) → 需确认各子集 license</td></tr>
<tr><td>zhangdw/to-tool-call-datasets</td><td>Apache-2.0 (聚合层)</td><td>各源保留原始 license → 需逐源检查 (BFCL/ToolBench/ToolACE 等)</td></tr>
<tr><td>utter-project/LongBlocks</td><td>CC BY-SA 4.0</td><td>需遵守底层数据源条款; Institutional-Books 部分不随数据分发</td></tr>
<tr><td>common-pile/arxiv_papers_filtered</td><td>CC BY/CC BY-SA/CC0</td><td>仅 openly licensed 论文，版权风险低</td></tr>
</table>

<h3>7.4 已知坑</h3>
<ul>
<li><strong>HF 体量差异</strong>: 数据集卡标注的体量与实际 hf download 后的 du -sb 可能差异大 (压缩/格式转换)。</li>
<li><strong>MDS 格式</strong>: ProLong 使用 Mosaic Data Shard 格式，需 mosaicml-streaming 库加载，不是标准 parquet → 需额外安装依赖。</li>
<li><strong>已分词数据</strong>: KL3M 数据已用 kl3m-004-128k-cased tokenizer 分词，与我们 129,281 vocab tokenizer 不兼容 → 需用原始文本 (如果有) 或重新分词。</li>
<li><strong>Docker 依赖</strong>: SWE-smith/SkyRL 的 RL 训练需 Docker 执行环境 → 需确认机器 Docker 可用性和磁盘 (每个容器 ~7GB)。</li>
<li><strong>SWE-bench Verified 污染已公开证实</strong> (2026-07): 不是我们独有的问题，整个领域都受影响。使用 SWE-bench Live 作为辅助评测可部分缓解。</li>
</ul>

<h3>7.5 本报告的局限性</h3>
<div class="warning">
<ul>
<li>本报告基于 web search + HF 页面抓取，<strong>未实际下载任何数据集</strong> → 所有体量、字段、占比均为数据集卡/论文声称值，未经实测验证。</li>
<li>部分数据集 (NExtLong, Nemotron-Pivot) 的元信息不完整 → 标注「未核到」而非编造。</li>
<li>≥32K / ≥128K 占比是核心指标，但<strong>大多数数据集未标注此指标</strong> → 必须下载后抽样实测才能确认是否满足闸门。</li>
<li>本报告不构成下载建议——下载决策需综合考虑磁盘余量、带宽、训练优先级、去污染成本等因素。</li>
</ul>
</div>

<div class="footer">
<p>本报告由 <strong>data 线 (唤醒 1044)</strong> 于 2026-10-31 生成 ｜ 生成器: <code>run/data/gen_lc_agentic_survey_report.py</code> ｜ 幂等: 连跑两次输出逐字节相同</p>
<p>调研方法: web search (cimi_search × 12 轮) + HF 页面抓取 (cimi_fetch) ｜ 遵循: BAIZE_DATA_TASK.md §运维令 2026-10-31 17:3x</p>
</div>
"""

def generate_html():
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>白泽长上下文 &amp; Agentic 数据集 HuggingFace 调研报告 ({SURVEY_DATE})</title>",
        f"<style>{CSS}</style>",
        "</head>",
        "<body>",
        section_tldr(),
        section_method(),
        section_a_table(),
        section_b_table(),
        section_contamination(),
        section_download(),
        section_honesty(),
        "</body>",
        "</html>",
    ]
    return "\n".join(parts)

def main():
    check_mode = "--check-idempotent" in sys.argv
    html_content = generate_html()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    if check_mode:
        html1 = generate_html()
        html2 = generate_html()
        if html1 == html2:
            print(f"OK: idempotent check passed ({len(html1)} bytes)")
            if os.path.exists(OUTPUT_PATH):
                with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                    existing = f.read()
                if existing == html1:
                    print(f"OK: output file unchanged ({len(html1)} bytes)")
                else:
                    print(f"INFO: output file differs, will overwrite")
            return 0
        else:
            print("FAIL: idempotent check failed")
            return 1

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"Report generated: {OUTPUT_PATH}")
    print(f"Size: {file_size} bytes ({file_size / 1024:.1f} KB)")

    if file_size < 25600:
        print(f"WARNING: file size {file_size} < 25KB threshold", file=sys.stderr)

    open_tags = html_content.count("<table>")
    close_tags = html_content.count("</table>")
    if open_tags != close_tags:
        print(f"WARNING: <table> tag mismatch: {open_tags} open vs {close_tags} close", file=sys.stderr)
    else:
        print(f"Tag check: <table> balanced ({open_tags} pairs)")

    if "<script" in html_content.lower():
        print("WARNING: <script> tag found!", file=sys.stderr)
    else:
        print("Script check: no <script> tags (OK)")

    if "cdn." in html_content.lower() or "unpkg.com" in html_content.lower() or "jsdelivr" in html_content.lower():
        print("WARNING: external CDN link found!", file=sys.stderr)
    else:
        print("CDN check: no external CDN links (OK)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
