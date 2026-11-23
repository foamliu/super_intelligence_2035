# 烛龙 Benchmark 月报 · 2026 年 11 月

> 汇报周期 2026.11.1 – 11.30（数据截至 11.23 14:30） · 汇报人 zhulong agent · 状态 **黄**

## 一句话结论

本月 EDA-Flow-Bench 评测集规模化与多模型基线建立完成：**500 任务主评测集冻结**（13 域覆盖），4 个模型多轮 Pass@1 基线对齐用户基准 10.5%（doubao-pro 10.18±1.18% / deepseek-v4-pro 21.78% 单 run）；deepseek 3-run 收口中、ICML 论文 §6 回填待用户裁定，为当前主要风险。

## 三层评测体系定位

参考 PI 团队收益材料（slide 24），烛龙 Benchmark 分三层逐级逼近真实工程：

| 层级 | 基准 | 测什么 | 本月状态 |
|:--|:--|:--|:--|
| **L1 通用代码编排** | SWE-bench / Terminal-Bench / SWE-MM | Agent 底座（上下文 / 规划 / 工具调用） | 横评进行中（harness 线） |
| **L2 EDA 单脚本胶水** | EDA-Scripting-Bench（449 任务 / 3 语言） | EDA 工具掌握度（API / 语言 / 运行时） | 已交付（最强 76.5% Pass@1） |
| **L3 长链设计流程编排** | **EDA-Flow-Bench（500 任务）** | 记忆 / 自改进 / 错误恢复 | **本月主战场 · 本报聚焦** |

L3 是把"会写单脚本"推向"会编排设计流程"的下一阶段评测主战场——本月进展全部围绕 L3。

## EDA-Flow-Bench 本月进展

**进展 1：评测集规模化与冻结。** Full 集 **2,186 个 case**（4 shard 并行造题：A=475 / B=527 / C=573 / D=611，11-17 单日批量入库 1,191 case），覆盖 **13 个 EDA domain**（spice_sim 116 / schematic_netlist 71 / physical_verify 68 居前三）。**500 任务主评测集冻结**，按链长 / 工具链深度分层，保留必须看图的多模态题不降级。

**进展 2：多模型基线建立与对齐。**

| 模型 | run 数 | Pass@1（mean ± std） | 各轮 PASS | 单题墙钟 | 单题 token |
|:--|:--:|:--:|:--|:--:|:--:|
| **deepseek-v4-pro** | 1（3-run 收口中） | **21.78%**（单 run） | 105 / 482 | ~74.2s | ~1,092K |
| **doubao-pro** | 3 | **10.18% ± 1.18%** | 45 / 57 / 45 | ~20.6s | ~370K |
| doubao-lite | 3 | 4.68% ± 0.77% | 19 / 22 / 28 | ~25.5s | ~313K |
| doubao-mini | 3 | 2.39% ± 0.19% | 11 / 11 / 13 | ~24.5s | ~349K |
| 用户基准（参照） | 1 | 10.5%（51/484） | — | — | — |

doubao-pro 对齐用户基准 10.5%，验证评测流程正确；deepseek 能力 2.1× doubao-pro 但成本 2.6-3.6×。

**进展 3：深度分析与 case-study。** 交付 case-study 报告（6 case 各加"任务说明 + 断言逐条展开"，3 PASS / 3 FAIL）+ 详尽进展报告。归纳三种失败模式：**A 交付物布局错位**（judge 找不到 assets）/ **B 会修不会记**（修复对但维修单漏写）/ **C 过早放弃**（0 交付 / 9 轮 / 52s 静默退出）。**核心洞察**：失败 ≠ 任务更难，而是 agent 行为模式偏差——**harness 改进（禁联网 + 强制最小迭代 + 沙盒复现 gate）可能比换更强模型更能提分**。

## 风险与阻塞

1. **deepseek 3-run 未收口**（r2 跑中 / r3 待起，预计 11-24 上午全完）→ 阻塞 McNemar 配对检验 + 论文 §6 强模型对比段。
2. **ICML 论文 §6 18 处 `\TBD` 待回填**（令纪律：3-run 出来先报数，等用户裁定才回填）。
3. **BaiZe 预训练 ckpt 未收敛**（ETA 2026-12-25）→ posttrain 正式 SFT/RL 的硬前置。

## 下月计划

| 目标 | 内容 | 节点 |
|:--|:--|:--|
| deepseek 3-run 收口 | r2/r3 跑完 + McNemar 配对检验（vs doubao-pro，报 b/c + p）+ 汇总报告 | 12 月上旬 |
| 论文 §6 回填 | 18 处 `\TBD` 替换为真实数据，优先改 `main.tex` 宏，clean compile | 12 月中旬 |
| 评测集扩张 | Full 集 3,000+ case，13 域均衡，多模态题不降级 | 12 月底 |
| posttrain 接入 | pretrain ckpt 收敛后，用 EDA-Flow-Bench 做 L4 领域评测 | 12 月底启动 |
| harness 改进探索 | 禁联网 / 强制最小迭代 / 沙盒复现 gate，验证"harness 改进比换更强模型更能提分" | 12 月中下旬 |

## 请求事项

- deepseek 3-run 收口后，**用户裁定是否放行论文 §6 18 处 `\TBD` 回填**。
- posttrain 正式训练接入需 pretrain ckpt（ETA 2026-12-25），若有延迟需提前同步。
- harness 改进探索需用户确认是否动 `run_batch.sh` / `run_one.sh` 评测入口（当前冻结口径不许擅改）。

---

**口径说明**：数据取自 EDA-Flow-Bench 仓库（`/nasdata/app.e0031982/code/EDA-Flow-Bench`）截至 2026-11-23 14:30。Pass@1 = 通过 case 自带 `check.py` 判分的 case 数 / 500。doubao 三组与 deepseek r1 均为 clean 轮（无 FUSE / providers.json 错配）。11-19 22:58 起跑的 batch（2.37%）因起跑时 providers.json 旧配置 + agent 自加 `--skip-done` 跑 422/500，**作废不引用**。
