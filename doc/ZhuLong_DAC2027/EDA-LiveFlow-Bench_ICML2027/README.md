# EDA-LiveFlow-Bench · ICML 2027

论文目录：`EDA-LiveFlow-Bench_ICML2027/`

## 截止时间
- Abstract: 2027-01-16
- Paper: 2027-01-22

## 文件结构

结构遵循 ML 会议惯例（参考 SWE-bench, ICLR 2024）：**Related Work 放在结果之后，Appendix 是命名 section 而非单个 "Appendix" 章节，包含 ICML 强制的 Ethics + Reproducibility Statement**。

```
EDA-LiveFlow-Bench_ICML2027/
├── main.tex                  # 主文件（ICML 2027 模板）
├── references.bib            # 参考文献
├── sections/                 # 主体章节（计入 8 页限制）
│   ├── 0_abstract.tex        # 摘要
│   ├── 1_intro.tex           # §1 引言
│   ├── 2_benchmark.tex       # §2 Benchmark Construction（数据源 + task schema + domain + 评测指标）
│   ├── 3_harness.tex         # §3 Agent System and Evaluation Harness（Cline + MCP + 防泄题 + EDA 桥）
│   ├── 4_experiments.tex     # §4 Experiments（RQ1/RQ2/RQ3 + 主结果）
│   ├── 5_analysis.tex        # §5 Analysis（failure taxonomy + grounding depth + 分布 + threats）
│   ├── 6_related.tex         # §6 Related Work（★ 放结果后，ML 惯例）
│   ├── 7_conclusion.tex      # §7 Discussion and Conclusion
│   ├── 8_ethics.tex          # Ethics Statement（★ ICML 强制）
│   └── 9_reproducibility.tex # Reproducibility Statement（★ ICML 期望）
├── appendix/                 # 附录（不计入页数，放 references 之后）
│   ├── A_benchmark_details.tex   # App. A Benchmark Details（task example + scan pipeline + keywords + full distribution）
│   ├── B_additional_results.tex  # App. B Additional Results（full per-domain + per-model + failure-by-domain + token cost）
│   └── C_experimental_details.tex # App. C Experimental Details（cline config + API + hook impl + judge impl + open-source roadmap）
├── figures/                  # 图表
└── README.md                 # 本文件
```

## 结构对照（vs. SWE-bench ICLR 2024）

| SWE-bench (ICLR 2024) | EDA-LiveFlow-Bench (ICML 2027) | 说明 |
|---|---|---|
| 1 Introduction | §1 Introduction | |
| 2 SWE-bench (Construction/Task/Features/Lite) | §2 Benchmark Construction + §3 Evaluation Harness | 拆成 benchmark 本体 + harness 两节 |
| 3 SWE-Llama (作者方法) | — | 我们没有自研模型，harness 即方法 |
| 4 Experimental Setup | §4 Experiments (含 setup) | setup 并入 experiments |
| 5 Results | §4 Experiments (含 results) | |
| 6 Related Work ★ | §6 Related Work ★ | **放在结果后**（ML 惯例，非 §2）|
| 7 Discussion | §7 Discussion and Conclusion | 合并 |
| 8 Ethics Statement ★ | Ethics Statement ★ | **ICML 强制** |
| 9 Reproducibility Statement ★ | Reproducibility Statement ★ | **ICML 期望** |
| App. A Benchmark Details | App. A Benchmark Details | task example + 构建细节 |
| App. B Training Details | — | 无自研模型 |
| App. C Additional Results | App. B Additional Results | |
| App. D Experimental Details | App. C Experimental Details | hook/judge/API 配置 |
| App. E Societal Impact | 合并进 Ethics | |
| App. F In-depth Analysis | — | 后续可补 |

## 编译
```bash
# 需要 ICML 2027 style 文件（从 icml.cc 下载 Author Kit）：
#   icml2027.sty, icml2027.bst → 放到本目录
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## 核心论点
1. **问题**：现有 EDA LLM benchmark 只评单函数代码生成或开源 flow 修复，没人评多步设计流编排
2. **贡献**：EDA-LiveFlow-Bench — 920 任务、13 domain、268 真实用户、42 台工作站，从真实 Cline 交互轨迹构建
3. **方法**：design_flow 契约（submit.zip 交付件）、执行式判分（≥8 断言）、PreToolUse 防泄题 hook
4. **结果**：最佳系统仅 28% Pass@1（远低于单脚本 EDA bench 的 76%），说明多步编排更难
5. **分析**：verification 80% 最易、digital 0% 最难，差距来自 tool-chain grounding depth 非 model size

## 与 DAC 2027 论文（ZhuLong）的区别
| | DAC 2027 (ZhuLong) | ICML 2027 (EDA-LiveFlow-Bench) |
|---|---|---|
| **Benchmark** | EDA-Scripting-Bench (449 tasks, 单脚本) | EDA-LiveFlow-Bench (920 tasks, 多步编排) |
| **Task mode** | 单函数代码生成 | design_flow (submit.zip 交付件) |
| **数据来源** | 厂商文档 + 专家构造 | 真实用户 Cline 交互轨迹 |
| **核心论点** | observation fidelity 是 binding 约束 | tool-chain grounding depth 是 binding 约束 |
| **Pass@1** | 76.5% (单脚本) | 28% (多步编排) |
| **投稿目标** | DAC (EDA 会议) | ICML (ML 会议) |

## 待补内容
- [ ] 下载 ICML 2027 官方 style 文件 (icml2027.sty / icml2027.bst)
- [ ] 扩 cline eval 到全 920 cases（当前仅 48 条，4 domain）
- [ ] 补多模型对比数据 (GLM-5.2 / Kimi-K2.6 / DeepSeek-V4-Flash)
- [ ] 画 pipeline 图 (Figure 1)
- [ ] 画 grounding depth vs Pass@1 图 (Figure 2)
- [ ] 画 domain distribution 饼图 (Figure 3)
- [ ] 补完整的 failure taxonomy 统计
- [ ] 更新 domain 分布表到 920 cases
- [ ] 附录 A 补完整 task example
