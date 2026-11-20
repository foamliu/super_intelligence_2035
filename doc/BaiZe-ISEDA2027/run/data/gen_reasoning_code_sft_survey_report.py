#!/usr/bin/env python3
"""
gen_reasoning_code_sft_survey_report.py -- 生成「复杂推理 + 代码 SFT 数据集 HF 调研报告」HTML

幂等：连跑两次输出逐字节相同。
输出：doc/BaiZe-ISEDA2027/reports/report_data_reasoning_code_sft_survey_zh.html

调研日期：2026-11-04
调研方法：通过 HF API (huggingface.co/api/datasets) + web search 检索数据集页面，
          逐条核实 repo id / 体量 / 语言 / license / gated / 字段结构 / 奖励信号。
"""

import html
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "reports", "report_data_reasoning_code_sft_survey_zh.html")
SURVEY_DATE = "2026-11-04"

REASONING_DATASETS = [
    {"repo_id": "openai/gsm8k", "hf_url": "https://huggingface.co/datasets/openai/gsm8k",
     "category": "数学推理 (GSM8K)", "size": "~7.4K 题 (train 7,473 + test 1,319)", "samples": "8,792",
     "language": "英语", "license": "MIT", "gated": "否", "updated": "2026-03-23", "downloads": 993185,
     "fields": "question, answer (含逐步推理过程, 以 #### 结尾给最终数字答案)",
     "reward_signal": "答案匹配: 最终数值精确匹配 (exact match); 可程序化验证",
     "verifiable": "是 (数值精确匹配)",
     "notes": "GSM8K 是小学数学应用题的标准评测+训练集, 7.4K train 题含 CoT 推理过程。体量小但质量高, 适合作为 RL 验证信号来源和 SFT seed。几乎所有数学推理模型都以其为基线。"},
    {"repo_id": "open-r1/OpenR1-Math-220k", "hf_url": "https://huggingface.co/datasets/open-r1/OpenR1-Math-220k",
     "category": "数学推理 (长链 CoT)", "size": "220K 样本 (10 个 parquet shard)", "samples": "~220,000",
     "language": "英语", "license": "Apache-2.0", "gated": "否", "updated": "2025-02-18", "downloads": 93402,
     "fields": "problem, solution (DeepSeek-R1 生成的长链 CoT), thought, answer, source",
     "reward_signal": "答案匹配: 数值/表达式精确匹配; Open R1 项目提供验证脚本",
     "verifiable": "是 (答案精确匹配 + 验证脚本)",
     "notes": "Open-R1 项目的核心 SFT 数据, 用 DeepSeek-R1 对 220K 数学题生成 CoT 轨迹。含完整 thinking trace, 是训练长链推理的首选。来源含 NuminaMath/DeepScaleR 等, 覆盖竞赛和奥赛级别。Apache-2.0。"},
    {"repo_id": "agentica-org/DeepScaleR-Preview-Dataset", "hf_url": "https://huggingface.co/datasets/agentica-org/DeepScaleR-Preview-Dataset",
     "category": "数学推理 (奥赛/竞赛)", "size": "40K 题 (10K<n<100K)", "samples": "~40,000",
     "language": "英语", "license": "MIT", "gated": "否", "updated": "2025-02-10", "downloads": 38399,
     "fields": "problem, answer, source (AMC/AIME/IMO/PUTNAM/OLYMPIAD 等)",
     "reward_signal": "答案匹配: 数值/表达式精确匹配; 部分题有验证程序",
     "verifiable": "是 (答案精确匹配)",
     "notes": "DeepScaleR-1.5B-Preview 的训练数据, 40K 竞赛级数学题。来源含 AMC/AIME/IMO/Putnam/Olympiad, 难度远超 GSM8K。1.5B 模型用此数据 RL 后在 AIME 2025 达 43.1% (超越 o1-preview)。MIT, 适合高难度数学推理 RL。"},
    {"repo_id": "project-numina/NuminaMath-CoT", "hf_url": "https://huggingface.co/datasets/project-numina/NuminaMath-CoT",
     "category": "数学推理 (大规模 CoT)", "size": "~860K 样本 (5 train + 1 test parquet)", "samples": "~860,000",
     "language": "英语", "license": "Apache-2.0", "gated": "否", "updated": "2024-11-25", "downloads": 169215,
     "fields": "problem, solution (CoT 推理过程), source (合成/改写/翻译/重述), messages",
     "reward_signal": "答案匹配: 部分有精确答案可验证; 但多数为开放式推理",
     "verifiable": "部分 (有明确数值答案的可验证; 推理过程不可自动验证)",
     "notes": "NuminaMath-CoT 是 AIMO 竞赛冠军数据集, 860K 数学 CoT 样本。Numina-1.5 是更新版 (44K downloads)。体量大、质量高, 是数学 SFT 的主力数据之一。Apache-2.0。"},
    {"repo_id": "meta-math/MetaMathQA", "hf_url": "https://huggingface.co/datasets/meta-math/MetaMathQA",
     "category": "数学推理 (数据增强)", "size": "~395K 样本", "samples": "395,000",
     "language": "英语", "license": "MIT", "gated": "否", "updated": "2023-12-21", "downloads": 67109,
     "fields": "query, response (CoT), original_question, type (rephrasing/reordering/FOBAR)",
     "reward_signal": "答案匹配: 基于 GSM8K/MATH 原始答案; 可验证",
     "verifiable": "是 (基于 GSM8K/MATH 答案)",
     "notes": "MetaMath 通过对 GSM8K 和 MATH 进行 4 种数据增强生成 395K QA。MetaMath-7B 在 GSM8K 达 66.4%。MIT, 适合数学 SFT baseline。"},
    {"repo_id": "EleutherAI/hendrycks_math", "hf_url": "https://huggingface.co/datasets/EleutherAI/hendrycks_math",
     "category": "数学推理 (MATH 基准)", "size": "12,500 题 (7,500 train + 5,000 test)", "samples": "12,500",
     "language": "英语", "license": "MIT", "gated": "否", "updated": "2025-01-12", "downloads": 149320,
     "fields": "problem, level (1-5), type (algebra/counting_and_probability/...), solution",
     "reward_signal": "答案匹配: \\boxed{} 格式精确匹配; 有官方评分脚本",
     "verifiable": "是 (\\boxed{} 精确匹配)",
     "notes": "MATH 数据集 (Hendrycks et al.), 12.5K 竞赛级数学题, 含 5 个难度级别。是标准数学评测集, train split 可用于 SFT 但需注意 test split 污染。MIT。"},
    {"repo_id": "open-thoughts/OpenThoughts-114k", "hf_url": "https://huggingface.co/datasets/open-thoughts/OpenThoughts-114k",
     "category": "长链 CoT (多领域)", "size": "114K 样本 (6 parquet shards)", "samples": "~114,000",
     "language": "英语", "license": "Apache-2.0", "gated": "否", "updated": "2025-08-31", "downloads": 103116,
     "fields": "messages (含 system/user/assistant), thoughts (长思考轨迹, DeepSeek-R1 风格)",
     "reward_signal": "答案匹配: 多数有 ground truth 可验证 (数学/代码/科学)",
     "verifiable": "是 (按领域不同有不同验证方式)",
     "notes": "OpenThoughts 是跨领域长链推理 SFT 数据集, 114K 样本覆盖数学、代码、科学、谜题等领域。用 DeepSeek-R1 生成 thinking trace。与 OpenR1-Math 互补 (前者多领域, 后者专注数学)。Apache-2.0, 下载量大 (103K)。"},
    {"repo_id": "open-thoughts/OpenThoughts3-1.2M", "hf_url": "https://huggingface.co/datasets/open-thoughts/OpenThoughts3-1.2M",
     "category": "长链 CoT (大规模)", "size": "~1.2M 样本", "samples": "~1,200,000",
     "language": "英语", "license": "Apache-2.0", "gated": "否", "updated": "2025-06-09", "downloads": 28324,
     "fields": "messages, thoughts (长链推理轨迹), source",
     "reward_signal": "答案匹配: 多数有 ground truth", "verifiable": "是 (按领域验证)",
     "notes": "OpenThoughts v3, 1.2M 大规模长链推理数据。v3 相比 v1 扩大了 10x, 覆盖更广领域。体量大需选择性使用。Apache-2.0。"},
    {"repo_id": "open-r1/Mixture-of-Thoughts", "hf_url": "https://huggingface.co/datasets/open-r1/Mixture-of-Thoughts",
     "category": "长链 CoT (混合推理)", "size": "100K<n<1M (混合多源)", "samples": "未核到确切数",
     "language": "英语", "license": "未核到 (Open-R1 项目, 多源聚合)", "gated": "否", "updated": "2025-05-26", "downloads": 16232,
     "fields": "messages, thoughts (多源混合 CoT)", "reward_signal": "混合: 各源验证方式不同",
     "verifiable": "部分 (取决于来源子集)",
     "notes": "Open-R1 的混合推理数据, 聚合多个 CoT 来源。适合需要多样化推理模式的 SFT。"},
    {"repo_id": "facebook/natural_reasoning", "hf_url": "https://huggingface.co/datasets/facebook/natural_reasoning",
     "category": "科学推理 (大规模)", "size": "1M<n<10M (1.1M+ 样本)", "samples": "~1,100,000",
     "language": "英语", "license": "CC-BY-NC-4.0", "gated": "否", "updated": "2025-02-21", "downloads": 5339,
     "fields": "question, reference_answer, completion (CoT), source (StackExchange/Wikipedia)",
     "reward_signal": "答案匹配: reference_answer 可用于 LLM-as-judge; 非精确匹配",
     "verifiable": "部分 (LLM-as-judge; 非程序化精确验证)",
     "notes": "Meta 出品, 1.1M 科学推理样本, 来源 StackExchange/Wikipedia。CC-BY-NC-4.0 (非商用许可), 若 BaiZe 有商业化计划需谨慎。体量大, 适合科学推理 SFT 补充。"},
    {"repo_id": "qingyangzhang/Natural-Reasoning-STEM-25K", "hf_url": "https://huggingface.co/datasets/qingyangzhang/Natural-Reasoning-STEM-25K",
     "category": "科学推理 (STEM)", "size": "~25K 样本", "samples": "~25,000",
     "language": "英语", "license": "未核到", "gated": "否", "updated": "2025-04-12", "downloads": 859,
     "fields": "question, answer (STEM 推理), source", "reward_signal": "答案匹配: 部分有参考答案",
     "verifiable": "部分",
     "notes": "25K STEM 推理样本, 体量适中。Natural Reasoning 的精选子集。license 未核到, 需直接访问 HF 页面确认。"},
    {"repo_id": "tasksource/proofwriter", "hf_url": "https://huggingface.co/datasets/tasksource/proofwriter",
     "category": "逻辑/符号推理", "size": "未核到确切体量", "samples": "未核到",
     "language": "英语", "license": "未核到", "gated": "否", "updated": "2024-01-08", "downloads": 5482,
     "fields": "context (事实+规则), question, label (true/false/unknown), proof (推导链)",
     "reward_signal": "标签匹配: true/false/unknown 三分类; proof 链可形式化验证",
     "verifiable": "是 (标签精确匹配 + proof 链形式化验证)",
     "notes": "ProofWriter 是逻辑推理数据集, 含事实、规则和推导链。适合训练模型的符号推理和逻辑推导能力。proof 字段可形式化验证, 是少数有严格验证信号的逻辑推理数据集。"},
    {"repo_id": "garage-bAInd/Open-Platypus", "hf_url": "https://huggingface.co/datasets/garage-bAInd/Open-Platypus",
     "category": "逻辑/符号推理 (混合)", "size": "10K<n<100K (~25K 样本)", "samples": "~25,000",
     "language": "英语", "license": "未核到 (聚合多源, 各源 license 不同)", "gated": "否", "updated": "2024-01-24", "downloads": 12155,
     "fields": "instruction, output, data_source (ARC/GSM8K/MATH/Orca/Wikipedia 等)",
     "reward_signal": "混合: 各源验证方式不同", "verifiable": "部分",
     "notes": "Open-Platypus 聚合 11 个开源数据集 (含数学/逻辑/推理), 25K 样本。Platypus 系列模型的基础数据。体量小但来源多样, 适合混合推理 SFT。"},
    {"repo_id": "deepmind/code_contests", "hf_url": "https://huggingface.co/datasets/deepmind/code_contests",
     "category": "竞赛编程 (可验证)", "size": "10K<n<100K (~13K 训练题)", "samples": "~13,328 train + 117 test + 165 valid",
     "language": "英语", "license": "CC-BY-4.0", "gated": "否", "updated": "2023-06-11", "downloads": 71070,
     "fields": "name, description, public_tests, private_tests, generated_tests, source, solutions",
     "reward_signal": "程序执行: public/private/generated tests 单元测试; 程序化验证",
     "verifiable": "是 (单元测试执行验证)",
     "notes": "DeepMind Code Contests, 13K 竞赛编程题, 含测试用例和多种语言解答。AlphaCode 的训练数据。CC-BY-4.0。每题有可执行测试 -> 适合 RL。同时也训练数学/算法推理能力。"},
    {"repo_id": "open-r1/codeforces", "hf_url": "https://huggingface.co/datasets/open-r1/codeforces",
     "category": "竞赛编程 (Codeforces CoT)", "size": "未核到确切字节", "samples": "未核到",
     "language": "英语", "license": "CC-BY-4.0", "gated": "否", "updated": "2025-05-19", "downloads": 44995,
     "fields": "problem (题面), solution (代码+CoT), tests (测试用例), source (Codeforces)",
     "reward_signal": "程序执行: Codeforces 测试用例; 可执行验证",
     "verifiable": "是 (测试用例执行)",
     "notes": "Open-R1 的 Codeforces 子集, 含 CoT 推理轨迹和代码。CC-BY-4.0, 下载量大 (45K)。适合代码+数学混合推理训练。有配套 codeforces-cots (纯 CoT, 5K dl) 和 codeforces-submissions (原始提交, 6K dl)。"},
    {"repo_id": "ByteDance-Seed/Code-Contests-Plus", "hf_url": "https://huggingface.co/datasets/ByteDance-Seed/Code-Contests-Plus",
     "category": "竞赛编程 (增强版)", "size": "10K<n<100K", "samples": "未核到确切数",
     "language": "英语", "license": "CC-BY-4.0", "gated": "否", "updated": "2025-11-06", "downloads": 12943,
     "fields": "problem, solutions, tests, metadata (来源/难度/标签)",
     "reward_signal": "程序执行: 测试用例验证", "verifiable": "是 (单元测试)",
     "notes": "字节跳动出品的竞赛编程增强数据集, 在 Code Contests 基础上增加更多题和更丰富的元数据。CC-BY-4.0。2025-11 更新, 较新。"},
    {"repo_id": "SynthLabsAI/Big-Math-RL-Verified", "hf_url": "https://huggingface.co/datasets/SynthLabsAI/Big-Math-RL-Verified",
     "category": "数学 RL (可验证)", "size": "100K<n<1M (~250K 样本)", "samples": "~250,000",
     "language": "英语", "license": "Apache-2.0", "gated": "是 (auto, 需同意条款)", "updated": "2025-03-25", "downloads": 4414,
     "fields": "problem, answer, source, verified (是否验证通过)",
     "reward_signal": "答案匹配: 精确匹配 + verified 标签",
     "verifiable": "是 (verified 标签 + 答案精确匹配)",
     "notes": "SynthLabs 出品, 250K 已验证数学 RL 数据。gated=auto, 需在 HF 页面同意条款。Apache-2.0。有 open-r1 处理版 (open-r1/Big-Math-RL-Verified-Processed, 非 gated, 768 dl) 可作为替代。适合数学 RL (GRPO/PPO)。"},
]
CODE_SFT_DATASETS = [
    {"repo_id": "nvidia/OpenCodeInstruct", "hf_url": "https://huggingface.co/datasets/nvidia/OpenCodeInstruct",
     "category": "代码合成 (大规模指令)", "size": "1M<n<5M (~2.2M 样本)", "samples": "~2,200,000",
     "language": "代码 (多语言)", "license": "CC-BY-4.0", "gated": "否", "updated": "2025-04-28", "downloads": 46936,
     "fields": "problem (指令), solution (代码), language, test (测试用例, 部分含)",
     "reward_signal": "部分: 含 test 字段的可执行验证; 多数仅 SFT",
     "verifiable": "部分 (有测试用例的子集可执行验证)",
     "stage": "SFT (主) + 部分 RL",
     "contamination_risk": "低: 合成指令数据, 非真实 SWE 仓库; 与 SWE-bench/TB 无直接重叠",
     "notes": "NVIDIA 出品, 2.2M 代码指令-解答对, 是目前最大的开源代码 SFT 数据集之一。CC-BY-4.0。部分样本含测试用例 -> 可做 RL。适合大规模代码 SFT 注入。"},
    {"repo_id": "ise-uiuc/Magicoder-OSS-Instruct-75K", "hf_url": "https://huggingface.co/datasets/ise-uiuc/Magicoder-OSS-Instruct-75K",
     "category": "代码合成 (OSS-Instruct)", "size": "10K<n<100K (75K 样本)", "samples": "75,000",
     "language": "代码 (多语言)", "license": "MIT", "gated": "否", "updated": "2023-12-04", "downloads": 41210,
     "fields": "problem (指令), solution (代码), language, raw_inspect (OSS 片段)",
     "reward_signal": "无自动验证 (SFT 数据)", "verifiable": "否",
     "stage": "SFT",
     "contamination_risk": "低: 从 OSS 片段合成指令, 非真实 issue/PR",
     "notes": "Magicoder 的 OSS-Instruct 数据, 从开源代码片段用 LLM 合成指令-代码对。75K 样本, MIT。Magicoder 系列模型的核心训练数据。简洁高效, 是代码 SFT 的经典基线。"},
    {"repo_id": "ise-uiuc/Magicoder-Evol-Instruct-110K", "hf_url": "https://huggingface.co/datasets/ise-uiuc/Magicoder-Evol-Instruct-110K",
     "category": "代码合成 (Evol-Instruct)", "size": "100K<n<1M (110K 样本)", "samples": "110,000",
     "language": "代码 (多语言)", "license": "Apache-2.0", "gated": "否", "updated": "2023-12-28", "downloads": 25372,
     "fields": "instruction, response (代码), evolution_type",
     "reward_signal": "无自动验证 (SFT 数据)", "verifiable": "否",
     "stage": "SFT",
     "contamination_risk": "低: 合成指令, WizardCoder Evol-Instruct 方法",
     "notes": "Magicoder 的 Evol-Instruct 数据, 用进化策略增强指令复杂度。110K 样本, Apache-2.0。与 OSS-Instruct 互补 (Evol 更复杂, OSS 更多样)。"},
    {"repo_id": "OpenCoder-LLM/opc-sft-stage2", "hf_url": "https://huggingface.co/datasets/OpenCoder-LLM/opc-sft-stage2",
     "category": "代码合成 (多源聚合)", "size": "未核到确切字节", "samples": "未核到 (含多子集)",
     "language": "代码 (多语言)", "license": "MIT", "gated": "否", "updated": "2024-11-24", "downloads": 28947,
     "fields": "messages (chat 格式, 多轮代码对话)",
     "reward_signal": "无自动验证 (SFT 数据)", "verifiable": "否",
     "stage": "SFT",
     "contamination_risk": "低: 多源聚合, 需逐子集核实",
     "notes": "OpenCoder 项目的 SFT stage 2 数据, 聚合多个代码指令源。MIT。有配套 annealing corpus (opc-annealing-corpus, 13K downloads)。"},
    {"repo_id": "bigcode/commitpackft", "hf_url": "https://huggingface.co/datasets/bigcode/commitpackft",
     "category": "代码修复 (commit diff)", "size": "未核到确切字节 (大规模)", "samples": "未核到 (来自 commitpack 子集)",
     "language": "代码 (多语言)", "license": "MIT", "gated": "否", "updated": "2023-08-20", "downloads": 47100,
     "fields": "commit (before/after 代码), lang, diff (代码变更), message (commit message)",
     "reward_signal": "无自动验证 (但 diff 本身是真实修复; 可用后修复代码跑测试间接验证)",
     "verifiable": "否 (需额外测试套件)",
     "stage": "SFT",
     "contamination_risk": "低-中: 来自 GitHub commits, 部分 commit 仓库可能与 SWE-bench 仓库重叠",
     "notes": "BigCode CommitPackFT, 从 GitHub commit 提取代码修复对 (before->after)。是代码修复/bug-fix SFT 的主要数据来源。MIT。来自真实 GitHub 仓库, 部分仓库可能与 SWE-bench 同源 -> 需 13-gram 去污染。"},
    {"repo_id": "nvidia/OpenCodeReasoning", "hf_url": "https://huggingface.co/datasets/nvidia/OpenCodeReasoning",
     "category": "代码推理 (大规模 CoT)", "size": "100K<n<1M (~1.7M 样本)", "samples": "~1,700,000",
     "language": "代码 (多语言)", "license": "CC-BY-4.0", "gated": "否", "updated": "2025-05-04", "downloads": 17192,
     "fields": "problem, solution (含 CoT 推理 + 代码), test (测试用例, 部分), reasoning (推理轨迹)",
     "reward_signal": "部分: 含 test 字段的可执行验证; 推理过程不可自动验证",
     "verifiable": "部分 (有测试用例的子集)",
     "stage": "SFT (主) + 部分 RL",
     "contamination_risk": "低: 合成/竞赛题目, 非真实仓库",
     "notes": "NVIDIA 出品, 1.7M 代码推理样本, 含 CoT 推理轨迹。CC-BY-4.0。是代码+推理交叉训练的主力数据。有 v2 版 (nvidia/OpenCodeReasoning-2, 6K downloads)。适合训练模型「先推理再编码」的能力。"},
    {"repo_id": "google-research-datasets/mbpp", "hf_url": "https://huggingface.co/datasets/google-research-datasets/mbpp",
     "category": "代码生成 (MBPP, 可验证)", "size": "~974 题 (train 374 + test 500 + prompt 100)", "samples": "974",
     "language": "Python", "license": "CC-BY-4.0", "gated": "否", "updated": "2024-01-04", "downloads": 251643,
     "fields": "task_id, text (问题描述), code (参考解), test_list (3 个测试用例), test_imports",
     "reward_signal": "程序执行: test_list 断言验证; 程序化验证",
     "verifiable": "是 (测试用例执行)",
     "stage": "SFT + RL",
     "contamination_risk": "低: 基础编程题, 非真实仓库",
     "notes": "MBPP (Mostly Basic Python Problems), 974 道基础 Python 编程题, 每题 3 个测试用例。是代码生成标准评测+训练集。CC-BY-4.0。体量小但每题可执行验证, 适合代码 RL (pass@k)。MBPP 是评测集, test split 绝不可入训练。"},
    {"repo_id": "SWE-bench/SWE-smith", "hf_url": "https://huggingface.co/datasets/SWE-bench/SWE-smith",
     "category": "仓库级 (合成 SWE 任务)", "size": "10K<n<100K (~60K task instances, 11 parquet shards)", "samples": "~60,000",
     "language": "Python", "license": "MIT", "gated": "否", "updated": "2025-12-14", "downloads": 92332,
     "fields": "instance_id, repo, base_commit, problem_statement, patch (gold patch), test_patch, FAIL_TO_PASS, PASS_TO_PASS",
     "reward_signal": "单元测试: FAIL_TO_PASS + PASS_TO_PASS; 需 Docker 执行",
     "verifiable": "是 (单元测试, 需 Docker)",
     "stage": "SFT (成功轨迹) + RL (单测 reward)",
     "contamination_risk": "中-高: 222 个 GitHub 仓库, 部分与 SWE-bench Verified 同源仓库",
     "notes": "SWE-smith, 60K 合成 SWE 任务实例, 222 个 Python 仓库。MIT。含 gold patch + 单测 -> 可直接 RL。是 SWE-agent-LM-32B (40.2% SWE-bench Verified) 的训练数据。部分仓库与 SWE-bench Verified 同源 -> 需 13-gram 去污染。有配套 SWE-smith-trajectories (轨迹, 11K downloads)。"},
    {"repo_id": "SWE-Gym/SWE-Gym", "hf_url": "https://huggingface.co/datasets/SWE-Gym/SWE-Gym",
     "category": "仓库级 (真实 SWE 任务)", "size": "未核到确切字节 (2,438 任务)", "samples": "2,438",
     "language": "Python", "license": "MIT", "gated": "否", "updated": "2025-05-10", "downloads": 21244,
     "fields": "instance_id, repo, base_commit, problem_statement, patch, test_patch, FAIL_TO_PASS, PASS_TO_PASS",
     "reward_signal": "单元测试: FAIL_TO_PASS + PASS_TO_PASS; 需 Docker/SWE-Gym 环境",
     "verifiable": "是 (单元测试, 需 Docker)",
     "stage": "SFT (成功轨迹) + RL (单测 reward)",
     "contamination_risk": "中: 2,438 真实 Python 任务, 与 SWE-bench Verified 部分同源",
     "notes": "SWE-Gym, 2,438 个真实 Python SWE 任务。MIT。论文报告 19% 绝对提升在 SWE-bench Verified。有配套 OpenHands-SFT-Trajectories (1.5K downloads) 和 OpenHands-Sampled-Trajectories (1.9K downloads)。"},
    {"repo_id": "wentingzhao/commit0_combined", "hf_url": "https://huggingface.co/datasets/wentingzhao/commit0_combined",
     "category": "仓库级 (commit0)", "size": "未核到", "samples": "未核到",
     "language": "Python (多语言)", "license": "未核到", "gated": "否", "updated": "2024-10-28", "downloads": 1851,
     "fields": "repo, commit, task, tests",
     "reward_signal": "单元测试: commit0 环境执行验证",
     "verifiable": "是 (单元测试)",
     "stage": "SFT + RL",
     "contamination_risk": "中: 从 GitHub 仓库提取, 部分与 SWE-bench 同源",
     "notes": "Commit0, 从 GitHub commit 提取仓库级任务。有配套 SWE-bench_Verified_commit0 (130 downloads)。适合仓库级代码生成训练。"},
    {"repo_id": "allenai/rlvr-code-data-python-r1-format-filtered", "hf_url": "https://huggingface.co/datasets/allenai/rlvr-code-data-python-r1-format-filtered",
     "category": "代码 RLVR (Python, 可验证)", "size": "未核到", "samples": "未核到",
     "language": "Python", "license": "未核到 (AllenAI 出品)", "gated": "否", "updated": "2025-07-05", "downloads": 426,
     "fields": "problem, solution, test (测试用例), reward (验证结果)",
     "reward_signal": "程序执行: 测试用例执行验证; RLVR (Reinforcement Learning with Verifiable Rewards)",
     "verifiable": "是 (测试用例执行)",
     "stage": "RL (RLVR)",
     "contamination_risk": "低: 合成/竞赛题, 非真实仓库",
     "notes": "AllenAI 的 RLVR 代码数据 (Python), R1 格式。适合代码 RLVR 训练 (GRPO/PPO + 执行验证)。有配套多语言版 (saurabh5/rlvr-code-data-Rust/JavaScript/Go, 各 200-400 downloads)。"},
    {"repo_id": "princeton-nlp/SWE-bench_Verified (评测集)", "hf_url": "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified",
     "category": "评测集 (污染参照)", "size": "500 个已验证实例", "samples": "500",
     "language": "Python", "license": "MIT", "gated": "否", "updated": "2025-02-18", "downloads": 165609,
     "fields": "instance_id, repo, base_commit, problem_statement, patch, test_patch, FAIL_TO_PASS, PASS_TO_PASS",
     "reward_signal": "单元测试 (评测用, 非训练)",
     "verifiable": "是",
     "stage": "评测集 (绝不可入训练)",
     "contamination_risk": "极高: 评测集本体, 必须用于去污染黑名单",
     "notes": "评测集本体, 绝不可入训练。500 个 SWE-bench Verified 实例。必须用其 instance_id 和 13-gram 指纹构建去污染黑名单。所有 SWE 类训练数据需与此比对去污染。"},
    {"repo_id": "harborframework/terminal-bench-2.1 (评测集)", "hf_url": "https://huggingface.co/datasets/harborframework/terminal-bench-2.1",
     "category": "评测集 (污染参照)", "size": "112+ 个终端任务", "samples": "112+",
     "language": "英语 (Shell/终端)", "license": "Apache-2.0", "gated": "否", "updated": "2026-09-14", "downloads": 187383,
     "fields": "task_id, task_description, setup, evaluation, solution",
     "reward_signal": "脚本断言 (评测用, 非训练)",
     "verifiable": "是",
     "stage": "评测集 (绝不可入训练)",
     "contamination_risk": "极高: 评测集本体, 必须用于去污染黑名单",
     "notes": "Terminal-Bench 2.1 评测集本体, 绝不可入训练。112+ 终端任务。必须用其 task_id 和 13-gram 指纹构建去污染黑名单。所有终端类训练数据需与此比对去污染。"},
]

EXISTING_SOURCES = [
    "ultrafineweb_en_v1_4 (110 shard, 2237B tokens) — 通用英文文本",
    "ultrafineweb_en_l3/qa (154 shard, 264B tokens) — L3 高质量英文",
    "UltraData-Code-L2 (141 shard, 421B tokens) — 代码 L2",
    "UltraData-Code-L3 (63 shard, 129B tokens) — 代码 L3",
    "UltraData-Math-L1 (149 shard, 164B tokens) — 数学 L1",
    "UltraData-Math-L3 (67 shard, 78B tokens) — 数学 L3",
    "ultrafineweb_en (32 shard, 906B tokens) — 英文基座",
    "ultrafineweb_l1_en_hq (94 shard, 150B tokens) — L1 高质量英文",
    "ultrafineweb_zh (4 shard, 113B tokens) — 中文",
    "UltraX-AICC (1 shard, 11B tokens) — 代码/数学混合",
    "UltraData-SFT-2605 (94 shard, 19B tokens) — SFT 指令数据",
    "UltraData-SFT-Agent-2609 (13 shard, 6B tokens) — Agent SFT",
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
<h1>白泽复杂推理 &amp; 代码 SFT 数据集 HuggingFace 调研报告</h1>
<p class="meta">调研日期: 2026-11-04 ｜ 调研执行: data 线 ｜ 调研方法: HF API (huggingface.co/api/datasets) + web search 检索数据集页面, 逐条核实元信息</p>

<h2 id="sec1">§1 TL;DR — 两类各 TOP-3 推荐</h2>

<div class="tldr-card">
<h4>🧠 A 类 · 复杂推理 SFT TOP-3 推荐</h4>
<table>
<tr><th>#</th><th>数据集</th><th>推荐理由</th><th>预计体量</th></tr>
<tr>
  <td>1</td>
  <td><a href="https://huggingface.co/datasets/open-r1/OpenR1-Math-220k">open-r1/OpenR1-Math-220k</a></td>
  <td>220K 数学题, DeepSeek-R1 生成长链 CoT 轨迹, Apache-2.0。覆盖竞赛和奥赛级别, 有答案验证脚本。是长链数学推理 SFT 的首选。</td>
  <td>~3-5 GiB (parquet)</td>
</tr>
<tr>
  <td>2</td>
  <td><a href="https://huggingface.co/datasets/open-thoughts/OpenThoughts-114k">open-thoughts/OpenThoughts-114k</a></td>
  <td>114K 跨领域 (数学/代码/科学/谜题) 长链 CoT, Apache-2.0, 下载量 103K。与 OpenR1-Math 互补 (多领域 vs 专注数学), 训练泛化推理能力。</td>
  <td>~5-8 GiB (parquet)</td>
</tr>
<tr>
  <td>3</td>
  <td><a href="https://huggingface.co/datasets/project-numina/NuminaMath-CoT">project-numina/NuminaMath-CoT</a></td>
  <td>860K 数学 CoT 样本, AIMO 竞赛冠军数据, Apache-2.0。体量大质量高, 是数学 SFT 主力数据。</td>
  <td>~8-12 GiB (parquet)</td>
</tr>
</table>
<p><strong>预计总下载体量 (A 类 TOP-3):</strong> ~16-25 GiB</p>
</div>

<div class="tldr-card">
<h4>💻 B 类 · 代码 SFT (Code-SFT) TOP-3 推荐</h4>
<table>
<tr><th>#</th><th>数据集</th><th>推荐理由</th><th>预计体量</th></tr>
<tr>
  <td>1</td>
  <td><a href="https://huggingface.co/datasets/nvidia/OpenCodeInstruct">nvidia/OpenCodeInstruct</a></td>
  <td>2.2M 代码指令-解答对, CC-BY-4.0。目前最大开源代码 SFT 数据集之一, 部分含测试用例可做 RL。</td>
  <td>~15-20 GiB (parquet)</td>
</tr>
<tr>
  <td>2</td>
  <td><a href="https://huggingface.co/datasets/nvidia/OpenCodeReasoning">nvidia/OpenCodeReasoning</a></td>
  <td>1.7M 代码推理样本 (含 CoT + 代码), CC-BY-4.0。训练「先推理再编码」能力, 部分有测试用例可执行验证。</td>
  <td>~10-15 GiB (parquet)</td>
</tr>
<tr>
  <td>3</td>
  <td><a href="https://huggingface.co/datasets/bigcode/commitpackft">bigcode/commitpackft</a></td>
  <td>从 GitHub commit 提取代码修复对 (before→after), MIT。代码修复/bug-fix SFT 的主要数据来源。需 13-gram 去污染 vs SWE-bench。</td>
  <td>~5-10 GiB (parquet)</td>
</tr>
</table>
<p><strong>预计总下载体量 (B 类 TOP-3):</strong> ~30-45 GiB</p>
<p><strong>值得关注的补充候选:</strong> ise-uiuc/Magicoder-OSS-Instruct-75K (75K, MIT, 代码 SFT 经典基线); ise-uiuc/Magicoder-Evol-Instruct-110K (110K, Apache-2.0, 进化指令); SWE-bench/SWE-smith (60K 仓库级 SWE, MIT, 可 RL, 污染风险中-高); deepmind/code_contests (13K 竞赛编程, CC-BY-4.0, 可执行验证); agentica-org/DeepScaleR-Preview-Dataset (40K 奥赛级数学, MIT); open-r1/codeforces (Codeforces CoT, CC-BY-4.0)</p>
</div>

<div class="info">
<p><strong>红线提醒:</strong> 本轮<strong>只调研 + 写报告, 不下载任何数据</strong>。不占 GPU, 不挤正在跑的长上下文下载。下载需运维另行批准后执行。</p>
</div>
"""


def section_method():
    return """
<h2 id="sec2">§2 检索方法与口径</h2>

<h3>2.1 检索工具与流程</h3>
<ul>
<li><strong>检索工具</strong>: 使用 HF API (huggingface.co/api/datasets) 通过代理 (http://172.19.92.25:13128) 发起针对性搜索查询, 获取数据集元信息 (repo id, downloads, gated, lastModified, license, size_categories, tags)。</li>
<li><strong>检索查询</strong>: 共发起 30+ 轮针对性搜索, 覆盖: math reasoning SFT, code SFT reasoning, chain of thought, GSM8K, MATH olympiad, open-r1, deepscaler, open-thoughts, code repair bugfix, code instruct, repo-level code SFT, science reasoning, logical reasoning, SWE-gym, SWE-smith, codecontests, numina, magicoder, commitpack, metamath, OpenCodeReasoning, RLVR code, terminal-bench, SWE-bench Verified, proofwriter, natural reasoning, big-math 等。</li>
<li><strong>逐条核实</strong>: 对每个候选数据集, 通过 HF API 获取 cardData (license, size_categories), gated 状态, downloads, lastModified, tags。部分数据集额外获取 siblings (parquet 文件结构) 以确认 shard 数量和格式。</li>
</ul>

<h3>2.2 核实的字段</h3>
<table>
<tr><th>字段</th><th>核实方式</th><th>可靠性</th></tr>
<tr><td>repo id</td><td>HF API 搜索结果直接返回</td><td>高 (API 原始数据)</td></tr>
<tr><td>下载量 (downloads)</td><td>HF API 返回的 downloads 字段</td><td>高</td></tr>
<tr><td>gated 状态</td><td>HF API 返回的 gated 字段 (False/auto/manual)</td><td>高</td></tr>
<tr><td>更新时间 (lastModified)</td><td>HF API 返回的 lastModified 字段</td><td>高</td></tr>
<tr><td>license</td><td>HF API cardData.license 字段</td><td>中-高 (由数据集上传者填写, 可能有遗漏)</td></tr>
<tr><td>体量 (size_categories)</td><td>HF API cardData.size_categories 字段 (区间值如 10K&lt;n&lt;100K)</td><td>中 (区间值, 非精确字节)</td></tr>
<tr><td>字段结构</td><td>数据集卡描述 + siblings (parquet 文件名推断)</td><td>中 (部分推断, 非实际读取 parquet schema)</td></tr>
<tr><td>奖励信号</td><td>数据集卡描述 + 论文引用</td><td>中 (基于描述, 非实际执行验证)</td></tr>
<tr><td>确切片片字节数</td><td>HF API siblings.size 字段 (本轮 API 返回 size=0, 可能是权限/版本问题)</td><td>低 (未核到确切字节, 标注「未核到」)</td></tr>
</table>

<h3>2.3 未核到的字段</h3>
<div class="note">
<ul>
<li><strong>确切字节数</strong>: HF API siblings 的 size 字段返回 0, 无法获取确切 parquet 字节数 → 体量基于 size_categories 区间值估算。</li>
<li><strong>部分 license</strong>: saurabh5/open-code-reasoning-sft, qingyangzhang/Natural-Reasoning-STEM-25K, wentingzhao/commit0_combined, allenai/rlvr-code-data-python-r1-format-filtered, tasksource/proofwriter, garage-bAInd/Open-Platypus 的 license 未在 cardData 中标注 → 标注「未核到」。</li>
<li><strong>部分体量/样本数</strong>: open-r1/Mixture-of-Thoughts, open-r1/codeforces 的确切样本数未核到。</li>
</ul>
</div>

<h3>2.4 与已有源的去重口径</h3>
<p>本报告候选不重复推荐已在 <code>DATA_MAPPING.md</code> 中的 12 个源 (见 §5)。已有源含 UltraData-Code-L2/L3 (代码)、UltraData-Math-L1/L3 (数学)、UltraData-SFT-2605 (SFT)、UltraData-SFT-Agent-2609 (Agent SFT) 等, 覆盖了基础代码和数学训练数据。本报告聚焦<strong>增量</strong>候选, 特别是长链 CoT、代码推理、仓库级 SWE 等已有源未覆盖的方向。</p>
"""


def section_a_table():
    rows = []
    for i, ds in enumerate(REASONING_DATASETS, 1):
        verifiable_class = "tag-rl" if ("是" in ds['verifiable'] and "部分" not in ds['verifiable']) else ("tag-mid" if "部分" in ds['verifiable'] else "tag-low")
        gated_class = "tag-high" if ds['gated'] not in ("否",) else "tag-low"
        rows.append(f"""
<tr>
<td>{i}</td>
<td>{hf_link(ds['repo_id'], ds['hf_url'])}</td>
<td>{esc(ds['category'])}</td>
<td>{esc(ds['size'])}</td>
<td>{esc(ds['language'])}</td>
<td>{esc(ds['license'])}</td>
<td><span class="{gated_class}">{esc(ds['gated'])}</span></td>
<td><span class="{verifiable_class}">{esc(ds['verifiable'])}</span></td>
<td>{esc(ds['reward_signal'])}</td>
</tr>""")
    rows_html = "\n".join(rows)
    cards = []
    for i, ds in enumerate(REASONING_DATASETS, 1):
        cards.append(f"""
<div class="tldr-card">
<h4>{i}. {hf_link(ds['repo_id'], ds['hf_url'])} <small>[{esc(ds['category'])}]</small></h4>
<table>
<tr><th>体量</th><td>{esc(ds['size'])}</td></tr>
<tr><th>样本数</th><td>{esc(ds['samples'])}</td></tr>
<tr><th>语言</th><td>{esc(ds['language'])}</td></tr>
<tr><th>License</th><td>{esc(ds['license'])}</td></tr>
<tr><th>Gated</th><td>{esc(ds['gated'])}</td></tr>
<tr><th>更新时间</th><td>{esc(ds['updated'])}</td></tr>
<tr><th>下载量</th><td>{esc(ds['downloads'])}</td></tr>
<tr><th>字段结构</th><td>{esc(ds['fields'])}</td></tr>
<tr><th>奖励信号</th><td>{esc(ds['reward_signal'])}</td></tr>
<tr><th>可验证性</th><td>{esc(ds['verifiable'])}</td></tr>
<tr><th>备注</th><td>{esc(ds['notes'])}</td></tr>
</table>
</div>""")
    cards_html = "\n".join(cards)
    return f"""
<h2 id="sec3">§3 A 类主表 — 复杂推理 SFT 数据集候选</h2>

<p>目标: 强化白泽的复杂推理能力, 覆盖数学推理 (GSM/MATH/奥赛)、逻辑/符号推理、长链 CoT (长思考轨迹)、科学推理。每类标注是否有可验证奖励信号 (答案匹配/程序验证)。</p>

<h3>3.1 候选总表</h3>
<table>
<tr>
<th>#</th><th>Repo ID</th><th>类别</th><th>体量</th><th>语言</th><th>License</th><th>Gated</th><th>可验证性</th><th>奖励信号</th>
</tr>
{rows_html}
</table>

<h3>3.2 候选详细卡片</h3>
{cards_html}

<h3>3.3 按方向分类汇总</h3>
<h4>① 数学推理 (GSM/MATH/奥赛)</h4>
<ul>
<li><strong>openai/gsm8k</strong> — 7.4K 小学数学应用题, 数值精确匹配可验证, MIT。推理模型标准基线。</li>
<li><strong>EleutherAI/hendrycks_math</strong> — 12.5K 竞赛级数学题 (MATH 数据集), 精确匹配, MIT。注意 test split 污染。</li>
<li><strong>meta-math/MetaMathQA</strong> — 395K, 对 GSM8K/MATH 做 4 种数据增强, MIT。</li>
<li><strong>agentica-org/DeepScaleR-Preview-Dataset</strong> — 40K 奥赛级 (AMC/AIME/IMO/Putnam), MIT。DeepScaleR-1.5B RL 后 AIME 2025 达 43.1%。</li>
<li><strong>project-numina/NuminaMath-CoT</strong> — 860K 数学 CoT, AIMO 冠军, Apache-2.0。</li>
</ul>
<h4>② 长链 CoT (长思考轨迹)</h4>
<ul>
<li><strong>open-r1/OpenR1-Math-220k</strong> — 220K, DeepSeek-R1 生成长链数学 CoT, Apache-2.0。首选。</li>
<li><strong>open-thoughts/OpenThoughts-114k</strong> — 114K 跨领域长链 CoT, Apache-2.0。</li>
<li><strong>open-thoughts/OpenThoughts3-1.2M</strong> — 1.2M 大规模长链, Apache-2.0。体量大需选择性使用。</li>
<li><strong>open-r1/Mixture-of-Thoughts</strong> — 混合多源 CoT, 适合多样化推理模式。</li>
</ul>
<h4>③ 科学推理</h4>
<ul>
<li><strong>facebook/natural_reasoning</strong> — 1.1M 科学推理 (StackExchange/Wikipedia), ⚠️ CC-BY-NC-4.0 (非商用)。</li>
<li><strong>qingyangzhang/Natural-Reasoning-STEM-25K</strong> — 25K STEM 精选, license 未核到。</li>
</ul>
<h4>④ 逻辑/符号推理</h4>
<ul>
<li><strong>tasksource/proofwriter</strong> — 逻辑推导, proof 链可形式化验证。少数有严格验证信号的逻辑推理数据集。</li>
<li><strong>garage-bAInd/Open-Platypus</strong> — 25K 聚合 11 源 (含数学/逻辑/推理)。</li>
</ul>
<h4>⑤ 竞赛编程 (可执行验证, 推理+代码交叉)</h4>
<ul>
<li><strong>deepmind/code_contests</strong> — 13K 竞赛编程, 含测试用例, CC-BY-4.0。AlphaCode 训练数据。</li>
<li><strong>open-r1/codeforces</strong> — Codeforces CoT + 代码, CC-BY-4.0。</li>
<li><strong>ByteDance-Seed/Code-Contests-Plus</strong> — 增强版竞赛编程, CC-BY-4.0, 2025-11 更新。</li>
</ul>
<h4>⑥ 数学 RL (有验证信号)</h4>
<ul>
<li><strong>SynthLabsAI/Big-Math-RL-Verified</strong> — 250K 已验证数学 RL 数据, ⚠️ gated=auto。有 open-r1 非 gated 处理版可替代。</li>
</ul>

<div class="info">
<p><strong>奖励信号来源汇总</strong>: 数值精确匹配 (GSM8K/MATH/MetaMath/DeepScaleR/NuminaMath/OpenR1-Math) > 程序执行验证 (code_contests/codeforces) > 标签+proof 链验证 (ProofWriter) > LLM-as-judge (natural_reasoning) > verified 标签 (Big-Math-RL-Verified)。数学推理的验证信号最成熟 (答案精确匹配); 科学推理依赖 LLM-as-judge (非程序化)。</p>
</div>
"""


def section_b_table():
    rows = []
    for i, ds in enumerate(CODE_SFT_DATASETS, 1):
        stage_class = "tag-rl" if "RL" in ds['stage'] else "tag-sft"
        cont_text = ds['contamination_risk'].split(":")[0].strip()
        cont_class = "tag-high" if "高" in cont_text else ("tag-mid" if "中" in cont_text else "tag-low")
        rows.append(f"""
<tr>
<td>{i}</td>
<td>{hf_link(ds['repo_id'], ds['hf_url'])}</td>
<td>{esc(ds['category'])}</td>
<td>{esc(ds['size'])}</td>
<td>{esc(ds['reward_signal'])}</td>
<td><span class="{stage_class}">{esc(ds['stage'])}</span></td>
<td><span class="{cont_class}">{esc(cont_text)}</span></td>
</tr>""")
    rows_html = "\n".join(rows)
    cards = []
    for i, ds in enumerate(CODE_SFT_DATASETS, 1):
        cards.append(f"""
<div class="tldr-card">
<h4>{i}. {hf_link(ds['repo_id'], ds['hf_url'])} <small>[{esc(ds['category'])}]</small></h4>
<table>
<tr><th>体量</th><td>{esc(ds['size'])}</td></tr>
<tr><th>样本数</th><td>{esc(ds['samples'])}</td></tr>
<tr><th>语言</th><td>{esc(ds['language'])}</td></tr>
<tr><th>License</th><td>{esc(ds['license'])}</td></tr>
<tr><th>Gated</th><td>{esc(ds['gated'])}</td></tr>
<tr><th>更新时间</th><td>{esc(ds['updated'])}</td></tr>
<tr><th>下载量</th><td>{esc(ds['downloads'])}</td></tr>
<tr><th>字段结构</th><td>{esc(ds['fields'])}</td></tr>
<tr><th>奖励信号</th><td>{esc(ds['reward_signal'])}</td></tr>
<tr><th>可验证性</th><td>{esc(ds['verifiable'])}</td></tr>
<tr><th>适用阶段</th><td>{esc(ds['stage'])}</td></tr>
<tr><th>污染风险</th><td>{esc(ds['contamination_risk'])}</td></tr>
<tr><th>备注</th><td>{esc(ds['notes'])}</td></tr>
</table>
</div>""")
    cards_html = "\n".join(cards)
    return f"""
<h2 id="sec4">§4 B 类主表 — 代码 SFT (Code-SFT) 数据集候选</h2>

<p>目标: 强化白泽的代码能力, 覆盖代码合成、代码修复 (bug-fix)、代码推理、指令跟随代码、多文件仓库级。每类标注奖励信号 (单测/diff/执行) 与适用阶段 (SFT/RL)。</p>

<h3>4.1 候选总表</h3>
<table>
<tr>
<th>#</th><th>Repo ID</th><th>类别</th><th>体量</th><th>奖励信号</th><th>适用阶段</th><th>污染风险</th>
</tr>
{rows_html}
</table>

<h3>4.2 候选详细卡片</h3>
{cards_html}

<h3>4.3 按类别分类</h3>
<h4>① 代码合成 / 指令跟随</h4>
<ul>
<li><strong>nvidia/OpenCodeInstruct</strong> — 2.2M 代码指令-解答对, CC-BY-4.0。最大开源代码 SFT, 部分含测试用例可 RL。</li>
<li><strong>ise-uiuc/Magicoder-OSS-Instruct-75K</strong> — 75K, OSS-Instruct 合成, MIT。代码 SFT 经典基线。</li>
<li><strong>ise-uiuc/Magicoder-Evol-Instruct-110K</strong> — 110K, 进化指令增强, Apache-2.0。</li>
<li><strong>OpenCoder-LLM/opc-sft-stage2</strong> — 多源聚合 SFT, MIT。</li>
</ul>
<h4>② 代码修复 (bug-fix)</h4>
<ul>
<li><strong>bigcode/commitpackft</strong> — GitHub commit diff (before->after), MIT。代码修复主力数据。⚠️ 部分 commit 仓库与 SWE-bench 同源 -> 需 13-gram 去污染。</li>
</ul>
<h4>③ 代码推理</h4>
<ul>
<li><strong>nvidia/OpenCodeReasoning</strong> — 1.7M 代码推理 (CoT+代码), CC-BY-4.0。训练「先推理再编码」能力。</li>
<li><strong>saurabh5/open-code-reasoning-sft</strong> — Open Code Reasoning SFT 子集, 有 RLVR 配套。</li>
</ul>
<h4>④ 代码生成 (可执行验证)</h4>
<ul>
<li><strong>google-research-datasets/mbpp</strong> — 974 基础 Python 题, 每题 3 测试用例, CC-BY-4.0。⚠️ test split 绝不可入训练。</li>
</ul>
<h4>⑤ 多文件仓库级</h4>
<ul>
<li><strong>SWE-bench/SWE-smith</strong> — 60K 合成 SWE 任务, 222 仓库, MIT。含单测可 RL。⚠️ 中-高污染风险 (与 Verified 同源仓库)。</li>
<li><strong>SWE-Gym/SWE-Gym</strong> — 2,438 真实 SWE 任务, MIT。论文报告 19% SWE-bench Verified 提升。⚠️ 中污染风险。</li>
<li><strong>wentingzhao/commit0_combined</strong> — GitHub commit 仓库级任务。⚠️ 中污染风险。</li>
</ul>
<h4>⑥ 代码 RLVR (有执行验证)</h4>
<ul>
<li><strong>allenai/rlvr-code-data-python-r1-format-filtered</strong> — Python RLVR, R1 格式。有配套多语言版 (Rust/JS/Go)。</li>
</ul>
<h4>⑦ 评测集 (污染参照, 绝不可入训练)</h4>
<ul>
<li><strong>princeton-nlp/SWE-bench_Verified</strong> — 500 实例评测集, 必须用于去污染黑名单。</li>
<li><strong>harborframework/terminal-bench-2.1</strong> — 112+ 终端任务评测集, 必须用于去污染黑名单。</li>
</ul>

<div class="warning">
<p><strong>⚠️ SWE-bench Verified &amp; Terminal-Bench 污染风险:</strong> SWE-smith (222 仓库)、SWE-Gym (2,438 真实任务)、commit0 (GitHub 仓库) 的部分仓库与 SWE-bench Verified 的 500 实例同源 -> 训练前必须用 13-gram 指纹黑名单去污染。commitpackft 来自 GitHub commits, 部分 commit 仓库也可能与 SWE-bench 仓库重叠。详见 §5。</p>
</div>
"""


def section_contamination():
    existing_html = "\n".join(f"<li>{esc(s)}</li>" for s in EXISTING_SOURCES)
    return f"""
<h2 id="sec5">§5 污染与去重</h2>

<h3>5.1 与现有 12 源的重叠</h3>
<p>以下源已在 <code>DATA_MAPPING.md</code> 中, 本报告候选不重复推荐:</p>
<ul>
{existing_html}
</ul>
<p><strong>重叠分析</strong>: 本报告 A 类候选 (OpenR1-Math, NuminaMath-CoT, DeepScaleR 等) 的数学题来源可能与 UltraData-Math-L1/L3 的数学语料有部分重叠 (都来自竞赛/教材数学题), 但 SFT 格式 (CoT 轨迹) 是增量。B 类候选 (OpenCodeInstruct, Magicoder, commitpackft) 的代码内容可能与 UltraData-Code-L2/L3 有部分重叠, 但指令格式和修复对是增量。建议下载后做跨源去重。</p>

<h3>5.2 与 SWE-bench Verified 的污染风险</h3>
<table>
<tr><th>数据集</th><th>污染风险</th><th>原因</th><th>去污染建议</th></tr>
<tr><td>SWE-bench/SWE-smith</td><td><span class="tag-mid">中-高</span></td><td>222 个 GitHub 仓库, 部分与 SWE-bench Verified 的 500 实例同源仓库</td><td>提取 SWE-bench Verified 的 repo 列表, 从 SWE-smith 中移除同源 repo 的 task; 再用 13-gram 指纹黑名单二次过滤</td></tr>
<tr><td>SWE-Gym/SWE-Gym</td><td><span class="tag-mid">中</span></td><td>2,438 真实 Python 任务, 与 Verified 部分同源</td><td>同上: repo 列表过滤 + 13-gram 去污染</td></tr>
<tr><td>wentingzhao/commit0_combined</td><td><span class="tag-mid">中</span></td><td>从 GitHub 仓库提取, 部分与 SWE-bench 同源</td><td>repo 列表过滤 + 13-gram 去污染</td></tr>
<tr><td>bigcode/commitpackft</td><td><span class="tag-low">低-中</span></td><td>来自 GitHub commits, 部分 commit 仓库可能与 SWE-bench 仓库重叠</td><td>提取 commit 仓库列表, 与 SWE-bench repo 列表比对; 重叠部分需 13-gram 去污染</td></tr>
<tr><td>nvidia/OpenCodeInstruct</td><td><span class="tag-low">低</span></td><td>合成指令, 非真实仓库</td><td>无需特殊去污染, 但建议常规跨源去重</td></tr>
<tr><td>nvidia/OpenCodeReasoning</td><td><span class="tag-low">低</span></td><td>合成/竞赛题, 非真实仓库</td><td>无需特殊去污染</td></tr>
<tr><td>ise-uiuc/Magicoder-*</td><td><span class="tag-low">低</span></td><td>从 OSS 片段合成指令, 非真实 issue/PR</td><td>无需特殊去污染</td></tr>
<tr><td>deepmind/code_contests</td><td><span class="tag-low">低</span></td><td>竞赛编程题, 非真实仓库</td><td>无需特殊去污染 (但注意 MBPP/HumanEval 评测集污染)</td></tr>
<tr><td>openai/gsm8k</td><td><span class="tag-low">低</span></td><td>数学题, 非代码仓库</td><td>无需特殊去污染 (但注意 GSM8K test split 不可入训练)</td></tr>
</table>

<h3>5.3 与 Terminal-Bench 的污染风险</h3>
<table>
<tr><th>数据集</th><th>污染风险</th><th>原因</th><th>去污染建议</th></tr>
<tr><td>所有 A 类 (推理 SFT)</td><td><span class="tag-low">低</span></td><td>数学/科学推理, 与终端任务无关</td><td>无需去污染</td></tr>
<tr><td>B 类代码合成 (OpenCodeInstruct/Magicoder)</td><td><span class="tag-low">低</span></td><td>合成指令, 非终端任务</td><td>无需特殊去污染</td></tr>
<tr><td>B 类仓库级 (SWE-smith/SWE-Gym)</td><td><span class="tag-low">低</span></td><td>SWE 任务, 与终端任务类型不同</td><td>低风险, 但建议 13-gram 去污染以防万一</td></tr>
</table>

<h3>5.4 去污染方案 (复用现有 13-gram 指纹黑名单)</h3>
<div class="info">
<p>我们已有 <strong>193,295 条 13-gram 指纹黑名单</strong>机制 (用于 EDA-Eval-PyAether 评测隔离), 可直接复用于本轮:</p>
<ol>
<li><strong>构建评测集黑名单</strong>: 从 SWE-bench Verified (500 实例) 和 Terminal-Bench 2.1 (112+ 任务) 提取 problem_statement/task_description/patch/solution 文本, 生成 13-gram 指纹。</li>
<li><strong>训练集侧扫描</strong>: 对所有 B 类仓库级数据 (SWE-smith, SWE-Gym, commit0, commitpackft) 的 problem_statement/patch/diff 文本做 13-gram 比对, 命中黑名单的样本移除。</li>
<li><strong>repo 列表过滤</strong>: 提取 SWE-bench Verified 的 500 个 repo 名, 从 SWE-smith/SWE-Gym/commit0 的 repo 字段中移除同源 repo 的所有 task。</li>
<li><strong>阈值写明可复现</strong>: 13-gram 命中阈值 (如 >=1 个命中即移除) 写入配置, 确保可复现。</li>
<li><strong>独立报告</strong>: 去污染结果写入 <code>CONTAMINATION_CHECK.md</code>, 记录移除了多少样本、命中率。</li>
</ol>
</div>

<h3>5.5 评测集本身的隔离</h3>
<div class="warning">
<p><strong>🚫 红线</strong>: 以下评测集<strong>绝对不能进入任何训练集</strong>:</p>
<ul>
<li><strong>princeton-nlp/SWE-bench_Verified</strong> (500 实例) — SWE-bench Verified 评测集本体</li>
<li><strong>harborframework/terminal-bench-2.1</strong> (112+ 任务) — Terminal-Bench 2.1 评测集本体</li>
<li><strong>openai/gsm8k</strong> test split (1,319 题) — GSM8K 测试集</li>
<li><strong>EleutherAI/hendrycks_math</strong> test split (5,000 题) — MATH 测试集</li>
<li><strong>google-research-datasets/mbpp</strong> test split (500 题) — MBPP 测试集</li>
</ul>
<p>上述评测集仅用于: ① 构建去污染黑名单 ② 评测白泽推理/代码能力。改写/paraphrase 也不洗白。</p>
</div>
"""


def section_download():
    return """
<h2 id="sec6">§6 下载方案 (建议, 需运维批准后执行)</h2>

<h3>6.1 建议下载的优先级</h3>
<table>
<tr><th>优先级</th><th>数据集</th><th>类别</th><th>预计体量</th><th>理由</th></tr>
<tr><td>P0</td><td>open-r1/OpenR1-Math-220k</td><td>A 数学推理</td><td>~3-5 GiB</td><td>220K 长链数学 CoT, Apache-2.0, 有验证脚本。推理 SFT 首选。</td></tr>
<tr><td>P0</td><td>open-thoughts/OpenThoughts-114k</td><td>A 长链 CoT</td><td>~5-8 GiB</td><td>114K 跨领域长链 CoT, Apache-2.0。与 OpenR1-Math 互补。</td></tr>
<tr><td>P1</td><td>project-numina/NuminaMath-CoT</td><td>A 数学推理</td><td>~8-12 GiB</td><td>860K 数学 CoT, Apache-2.0。数学 SFT 主力。</td></tr>
<tr><td>P1</td><td>nvidia/OpenCodeInstruct</td><td>B 代码合成</td><td>~15-20 GiB</td><td>2.2M 代码指令, CC-BY-4.0。最大代码 SFT。</td></tr>
<tr><td>P1</td><td>nvidia/OpenCodeReasoning</td><td>B 代码推理</td><td>~10-15 GiB</td><td>1.7M 代码推理, CC-BY-4.0。先推理再编码。</td></tr>
<tr><td>P2</td><td>ise-uiuc/Magicoder-OSS-Instruct-75K</td><td>B 代码合成</td><td>~1-2 GiB</td><td>75K, MIT。经典基线, 体量小。</td></tr>
<tr><td>P2</td><td>ise-uiuc/Magicoder-Evol-Instruct-110K</td><td>B 代码合成</td><td>~2-3 GiB</td><td>110K, Apache-2.0。进化指令。</td></tr>
<tr><td>P2</td><td>bigcode/commitpackft</td><td>B 代码修复</td><td>~5-10 GiB</td><td>代码修复主力, MIT。需 13-gram 去污染。</td></tr>
<tr><td>P3</td><td>agentica-org/DeepScaleR-Preview-Dataset</td><td>A 数学推理</td><td>~1-2 GiB</td><td>40K 奥赛级, MIT。高难度数学 RL。</td></tr>
<tr><td>P3</td><td>SWE-bench/SWE-smith</td><td>B 仓库级</td><td>~5-10 GiB</td><td>60K SWE, MIT。需 13-gram 去污染 + Docker。</td></tr>
<tr><td>P3</td><td>deepmind/code_contests</td><td>A/B 竞赛编程</td><td>~3-5 GiB</td><td>13K 竞赛题, CC-BY-4.0。可执行验证。</td></tr>
</table>

<h3>6.2 落盘路径</h3>
<p>遵循现有规范, 落盘到 <code>/nas_inference/app.e0031982/datasets/&lt;repo原名&gt;/</code> (该盘 45T, 已有 17T, 余 29T, 足够)。</p>
<p>下载后按「镜像下载路径」写入 <code>DATA_MAPPING.md</code>。</p>

<h3>6.3 hf download 命令模板</h3>
<pre><code># 代理 (走 .29 的代理直连 hf.co)
P=http://172.19.92.25:13128
export HTTPS_PROXY=$P HTTP_PROXY=$P

# 落盘路径
BASE=/nas_inference/app.e0031982/datasets

# P0: 数学推理 SFT
hf download open-r1/OpenR1-Math-220k --repo-type dataset --local-dir $BASE/open-r1--OpenR1-Math-220k

# P0: 跨领域长链 CoT
hf download open-thoughts/OpenThoughts-114k --repo-type dataset --local-dir $BASE/open-thoughts--OpenThoughts-114k

# P1: 数学 CoT (860K)
hf download project-numina/NuminaMath-CoT --repo-type dataset --local-dir $BASE/project-numina--NuminaMath-CoT

# P1: 代码指令 (2.2M)
hf download nvidia/OpenCodeInstruct --repo-type dataset --local-dir $BASE/nvidia--OpenCodeInstruct

# P1: 代码推理 (1.7M)
hf download nvidia/OpenCodeReasoning --repo-type dataset --local-dir $BASE/nvidia--OpenCodeReasoning</code></pre>

<h3>6.4 预计磁盘与 ETA</h3>
<table>
<tr><th>阶段</th><th>数据集</th><th>预计体量</th><th>ETA (按 ~50 MiB/s 实测带宽)</th></tr>
<tr><td>P0</td><td>OpenR1-Math-220k + OpenThoughts-114k</td><td>~8-13 GiB</td><td>~3-5 min</td></tr>
<tr><td>P1</td><td>NuminaMath-CoT + OpenCodeInstruct + OpenCodeReasoning</td><td>~33-47 GiB</td><td>~11-16 min</td></tr>
<tr><td>P2</td><td>Magicoder OSS/Evol + commitpackft</td><td>~8-15 GiB</td><td>~3-5 min</td></tr>
<tr><td>P3</td><td>DeepScaleR + SWE-smith + code_contests</td><td>~9-17 GiB</td><td>~3-6 min</td></tr>
<tr><td><strong>合计</strong></td><td>P0+P1+P2+P3</td><td><strong>~58-92 GiB</strong></td><td><strong>~20-32 min</strong></td></tr>
</table>

<div class="note">
<p><strong>磁盘说明</strong>: /nas_inference 当前 17T/45T (38%), 余 29T。P0-P3 合计 ~58-92 GiB, 完全安全。</p>
<p><strong>带宽说明</strong>: 当前长上下文 A 类下载 (~286 GiB) 可能仍在进行, 新下载需 <code>nice</code> + 限并发 <=4, 避免挤占带宽。</p>
<p><strong>⚠️ 本轮只调研不下载</strong>: 上述方案为建议, 需运维批准后方可执行。</p>
</div>
"""


def section_honesty():
    return """
<h2 id="sec7">§7 诚实条款</h2>

<h3>7.1 未核到的字段</h3>
<table>
<tr><th>数据集</th><th>未核到的字段</th><th>原因</th><th>后续核实建议</th></tr>
<tr><td>open-r1/Mixture-of-Thoughts</td><td>确切样本数、license</td><td>HF API cardData 未标注 license</td><td>直接访问 HF 页面确认</td></tr>
<tr><td>open-r1/codeforces</td><td>确切字节和样本数</td><td>size_categories 未给出确切值</td><td>下载后 du -sb 实测</td></tr>
<tr><td>tasksource/proofwriter</td><td>体量、样本数、license</td><td>cardData 不完整</td><td>直接访问 HF 页面</td></tr>
<tr><td>garage-bAInd/Open-Platypus</td><td>license (聚合多源)</td><td>各源 license 不同, 聚合层未统一标注</td><td>查看 11 个源各自的 license</td></tr>
<tr><td>qingyangzhang/Natural-Reasoning-STEM-25K</td><td>license</td><td>cardData 未标注</td><td>直接访问 HF 页面</td></tr>
<tr><td>OpenCoder-LLM/opc-sft-stage2</td><td>确切字节和样本数</td><td>含多子集, 未逐一标注</td><td>下载后 du -sb 实测</td></tr>
<tr><td>bigcode/commitpackft</td><td>确切字节和样本数</td><td>来自 commitpack 子集, 未单独标注</td><td>下载后 du -sb 实测</td></tr>
<tr><td>saurabh5/open-code-reasoning-sft</td><td>体量、样本数、license</td><td>cardData 不完整</td><td>直接访问 HF 页面</td></tr>
<tr><td>wentingzhao/commit0_combined</td><td>体量、样本数、license</td><td>cardData 不完整</td><td>直接访问 HF 页面</td></tr>
<tr><td>allenai/rlvr-code-data-python-r1-format-filtered</td><td>体量、样本数、license</td><td>cardData 不完整</td><td>直接访问 HF 页面</td></tr>
<tr><td>SynthLabsAI/Big-Math-RL-Verified</td><td>确切字节 (gated)</td><td>gated=auto, 未实际下载</td><td>同意条款后下载; 或用 open-r1 处理版</td></tr>
<tr><td>所有数据集</td><td>确切 parquet 字节数</td><td>HF API siblings.size 返回 0</td><td>下载后 du -sb 实测</td></tr>
</table>

<h3>7.2 代理指标 vs 实测</h3>
<div class="note">
<p>本报告中以下指标为<strong>代理指标</strong> (非实测):</p>
<ul>
<li><strong>体量 (size_categories)</strong>: HF API 返回区间值 (如 100K&lt;n&lt;1M), 非精确字节。</li>
<li><strong>样本数</strong>: 部分来自数据集卡描述, 非精确 API 返回, 可能有偏差。</li>
<li><strong>字段结构</strong>: 基于数据集卡和 parquet 文件名推断, 非实际读取 schema。</li>
<li><strong>奖励信号</strong>: 基于数据集卡和论文描述, 非实际执行验证。</li>
<li><strong>污染风险</strong>: 基于来源推断 (GitHub vs 合成), 非实际 13-gram 比对结果。</li>
</ul>
</div>

<h3>7.3 License 风险</h3>
<table>
<tr><th>数据集</th><th>License</th><th>风险说明</th></tr>
<tr><td>facebook/natural_reasoning</td><td>CC-BY-NC-4.0</td><td>⚠️ 非商用。若 BaiZe 有商业化计划, 此数据不可使用。</td></tr>
<tr><td>SynthLabsAI/Big-Math-RL-Verified</td><td>Apache-2.0 (gated)</td><td>需同意条款; 有 open-r1 非 gated 处理版可替代。</td></tr>
<tr><td>nvidia/OpenCodeInstruct / OpenCodeReasoning</td><td>CC-BY-4.0</td><td>需署名。商用可用但需标注来源。</td></tr>
<tr><td>deepmind/code_contests / open-r1/codeforces</td><td>CC-BY-4.0</td><td>需署名。竞赛题版权属各平台。</td></tr>
<tr><td>bigcode/commitpackft</td><td>MIT</td><td>数据来自 GitHub commits, 各 commit 保留原作者版权。</td></tr>
<tr><td>garage-bAInd/Open-Platypus</td><td>未核到 (聚合层)</td><td>11 个源各有 license, 需逐源检查。</td></tr>
</table>

<h3>7.4 已知坑</h3>
<ul>
<li><strong>HF 体量差异</strong>: 数据集卡 size_categories 与实际 du -sb 可能差异大。</li>
<li><strong>评测集污染</strong>: GSM8K/MATH/MBPP 都有 test split, 绝不可入训练。hendrycks_math test split (5,000 题) 必须与 train (7,500 题) 严格隔离。</li>
<li><strong>SWE-bench Verified 污染已公开证实</strong> (2026-07): SWE-rebench 揭示 DeepSeek-V3 去污染后从 39.7% 降到 21.3%。使用 SWE-smith/SWE-Gym 前必须 13-gram 去污染。</li>
<li><strong>Docker 依赖</strong>: SWE-smith/SWE-Gym 的 RL 需 Docker, 每容器 ~7GB。</li>
<li><strong>gated 数据集</strong>: Big-Math-RL-Verified 需同意条款; 有 open-r1 处理版可替代。</li>
<li><strong>多语言 vs 单语言</strong>: OpenCodeInstruct/OpenCodeReasoning 覆盖多语言, BaiZe 当前以英文为主, 需筛选。</li>
</ul>

<h3>7.5 本报告的局限性</h3>
<div class="warning">
<ul>
<li>本报告基于 HF API + web search, <strong>未实际下载任何数据集</strong> → 所有体量、字段、奖励信号均为声称值, 未经实测。</li>
<li>确切 parquet 字节数未核到 (HF API siblings.size 返回 0) → 体量基于区间值估算。</li>
<li>部分数据集 license 未核到 → 标注「未核到」而非编造。</li>
<li>污染风险基于来源推断, <strong>非实际 13-gram 比对</strong> → 需下载后做实际去污染验证。</li>
<li>本报告不构成下载建议——下载决策需综合考虑磁盘、带宽、训练优先级、去污染成本、license 风险。</li>
<li>HF 数据集体量以数据集卡为准, 与实际下载字节可能差异大 (已知坑)。</li>
</ul>
</div>

<div class="footer">
<p>本报告由 <strong>data 线</strong> 于 2026-11-04 生成 ｜ 生成器: <code>run/data/gen_reasoning_code_sft_survey_report.py</code> ｜ 幂等: 连跑两次输出逐字节相同</p>
<p>调研方法: HF API (huggingface.co/api/datasets) + web search ｜ 遵循: BAIZE_DATA_TASK.md §运维令 2026-11-04 09:4x</p>
</div>
"""


def generate_html():
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>白泽复杂推理 &amp; 代码 SFT 数据集 HuggingFace 调研报告 ({SURVEY_DATE})</title>",
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
    else:
        print(f"OK: file size {file_size} >= 25KB threshold")

    if "<script" in html_content.lower():
        print("WARNING: <script> tag found in output", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())







