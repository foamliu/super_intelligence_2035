# EDA-LiveFlow-Bench · ICML 2027

论文目录：`EDA-LiveFlow-Bench_ICML2027/`

## 截止时间
- Abstract: 2027-01-16
- Paper: 2027-01-22

## 文件结构
```
EDA-LiveFlow-Bench_ICML2027/
├── main.tex                  # 主文件（ICML 2027 模板）
├── references.bib            # 参考文献
├── sections/
│   ├── 0_abstract.tex        # 摘要
│   ├── 1_intro.tex           # 引言（问题动机 + 贡献）
│   ├── 2_related.tex         # 相关工作（RTLLM/VerilogEval/FlowFixer/SWE-bench）
│   ├── 3_benchmark.tex       # Benchmark 构建（数据源 + task schema + domain 覆盖 + 评测协议）
│   ├── 4_method.tex          # Agent 系统 + 评测 harness + 防泄题 + EDA 桥
│   ├── 5_experiments.tex     # 实验（RQ1 orchestration ceiling / RQ2 domain gap / RQ3 model scaling）
│   ├── 6_analysis.tex        # 分析（failure taxonomy + grounding depth + 分布分析 + threats）
│   ├── 7_conclusion.tex      # 结论 + future work
│   └── 8_appendix.tex        # 附录（task example + keyword filters + full results）
├── figures/                  # 图表（pipeline, grounding depth, domain distribution）
└── README.md                 # 本文件
```

## 编译
```bash
# 需要 ICML 2027 style 文件（从 icml.cc 下载 Author Kit）：
#   icml2027.sty, icml2027.bst → 放到本目录
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## 核心论点
1. **问题**：现有 EDA LLM benchmark 只评单函数代码生成或开源 flow 修复，没人评多步设计流编排
2. **贡献**：EDA-LiveFlow-Bench — 863 任务、13 domain、226 真实用户、65 台工作站，从真实 Cline 交互轨迹构建
3. **方法**：design_flow 契约（submit.zip 交付件）、执行式判分（≥8 断言）、PreToolUse 防泄题 hook
4. **结果**：最佳系统仅 28% Pass@1（远低于单脚本 EDA bench 的 76%），说明多步编排更难
5. **分析**：verification 80% 最易、digital 0% 最难，差距来自 tool-chain grounding depth 非 model size

## 与 DAC 2027 论文（ZhuLong）的区别
| | DAC 2027 (ZhuLong) | ICML 2027 (EDA-LiveFlow-Bench) |
|---|---|---|
| **Benchmark** | EDA-Scripting-Bench (449 tasks, 单脚本) | EDA-LiveFlow-Bench (863 tasks, 多步编排) |
| **Task mode** | 单函数代码生成 | design_flow (submit.zip 交付件) |
| **数据来源** | 厂商文档 + 专家构造 | 真实用户 Cline 交互轨迹 |
| **核心论点** | observation fidelity 是 binding 约束 | tool-chain grounding depth 是 binding 约束 |
| **Pass@1** | 76.5% (单脚本) | 28% (多步编排) |
| **投稿目标** | DAC (EDA 会议) | ICML (ML 会议) |

## 待补内容
- [ ] 下载 ICML 2027 官方 style 文件 (icml2027.sty / icml2027.bst)
- [ ] 扩 cline eval 到全 863 cases（当前仅 89 条，4 domain）
- [ ] 补多模型对比数据 (GLM-5.2 / Kimi-K2.6 / DeepSeek-V4-Flash)
- [ ] 画 pipeline 图 (Figure 1)
- [ ] 画 grounding depth vs Pass@1 图 (Figure 2)
- [ ] 画 domain distribution 饼图 (Figure 3)
- [ ] 补完整的 failure taxonomy 统计
- [ ] 更新 domain 分布表到 863 cases
- [ ] 附录补完整 task example
