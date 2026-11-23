# 烛龙 Benchmark 月报 · 2026 年 11 月

## 基本信息

| 项目内容 |  |
|:--|:--|
| 项目名称 | 烛龙 Benchmark（EDA-Flow-Bench） |
| 汇报人 | zhulong agent |
| 汇报周期 | 2026.11.1 – 11.30（数据截至 11.23 10:30） |
| 总体状态 | 黄 —— 评测集规模化与多模型基线建立完成，但 deepseek 强模型 3-run 未收口、ICML 论文 §6 回填阻塞 |

## 1. 一句话结论

本月 EDA-Flow-Bench 评测集规模化与多模型基线建立完成：Full 集 **2,130 个 case**（4 shard 并行造题，11-17 单日入库 1,191 case），Lite 500 主评测集冻结；4 个模型多轮 Pass@1 基线建立并**对齐用户基准 10.5%**（doubao-pro 10.18±1.45%、deepseek-v4-pro 21.78% 单 run）；但 **deepseek 3-run 未收口**（r2 跑中 / r3 待起）、**ICML 论文 §6 18 处 `\TBD` 待回填**，为当前主要风险。

## 2. 本月关键进展

**进展 1：评测集规模化与冻结。** Full 集 2,130 个 case（vs 10 月底仅 ~30 case 起步，月增 2,100），覆盖 **13 个 EDA domain**（spice_sim 456 / schematic_netlist 331 / physical_verify 297 居前三）。4 shard 并行造题：A=475 / B=527 / C=573 / D=611 case 文件；11-17 单日批量入库 1,191 case（per-case 文件方式重构）。**Lite 500 主评测集冻结**（spice_sim 116 / schematic_netlist 69 / physical_verify 67 居前三），冻结口径 `\LiteSet=500` / `\Neval=696` / `\MzeroPass=10.0%` / `\ScriptPass=76.5%`，覆盖全部 13 域并按链长/工具链深度分层。

**进展 2：多模型基线建立与对齐。** doubao 三组各 3-run clean：
- **doubao-pro**：10.18% ± 1.45%（45/57/45，单题墙钟 ~20.6s / ~370K token），**对齐用户基准 51/484 = 10.5%**，验证评测流程正确；
- **doubao-lite**：4.68% ± 0.95%（19/22/28，~25.5s / ~313K token）；
- **doubao-mini**：2.38% ± 0.23%（11/11/13，~24.5s / ~349K token）。

**deepseek-v4-pro** r1 = **21.78%**（105/482，单 run，~74.2s / ~1,092K token；能力 2.1× doubao-pro 但成本 2.6-3.6×）；r2 跑中（截至 11-23 10:30 进度 209/500，pass 41，early ~19.6%，ETA ~16:16），r3 待 r2 收口后自动起。

**进展 3：深度分析与 case-study。** 11-23 交付两份报告：
- **case-study 报告**（`report_zhulong_case_study_dsv4pro_r1_20261123.html`，87KB）：schematic_netlist / analog_context / waveform 三场景各 1 PASS + 1 FAIL（seed=42 可复现），含 SVG 序列图 + 工具调用序列 + 成败归因。归纳三种失败模式：**A 交付物布局错位**（DevUsageExtract，judge 找不到 assets）/ **B 探索不足漏 bug**（PwrIremCfgFix，未沙盒复现失败）/ **C 过早放弃**（HierSvwfConvert，0 交付 / 9 轮 / 52s 静默退出）。
- **进展报告**（`report_zhulong_eval_progress_20261123.html`，32KB）：4 模型逐轮明细 + 墙钟 + token 成本 + 成本-能力象限。

**核心洞察**：失败 ≠ 任务更难，而是 **agent 行为模式偏差**（联网查资料 / 目录探索低效 / 未沙盒实测 / 过早放弃）——这是 **harness/agent 行为层问题**而非模型能力层问题，**harness 改进（禁联网 + 强制最小迭代 + 沙盒复现 gate）可能比换更强模型更能提分**。

## 3. 数据对比

### 评测集规模

| 指标 | 本月（11.23） | 上月底（10.31） | 环比 |
|:--|:--:|:--:|:--:|
| Full 集 case 数 | **2,130** | ~30 | +2,100 |
| Lite 主评测集 case 数 | **500**（冻结） | 0 | +500 |
| 13 EDA domain 覆盖 | 13/13 | 0/13 | 全覆盖 |
| 4 shard case 文件 | A=475 / B=527 / C=573 / D=611 | 0 | +2,186 |
| 11 月评测 batch 数 | 39 | 0 | +39 |
| 11 月仓库提交数 | 4,710 | — | — |

### 模型评测对比（Lite 500 · Pass@1）

| 模型 | run 数 | Pass@1（mean ± std） | 各轮 PASS | 单题墙钟 | 单题 token（in） |
|:--|:--:|:--:|:--|:--:|:--:|
| **doubao-pro** | 3 | **10.18% ± 1.45%** | 45 / 57 / 45 | ~20.6s | ~370K |
| doubao-lite | 3 | 4.68% ± 0.95% | 19 / 22 / 28 | ~25.5s | ~313K |
| doubao-mini | 3 | 2.38% ± 0.23% | 11 / 11 / 13 | ~24.5s | ~349K |
| **deepseek-v4-pro** | 1（r2/r3 跑中） | **21.78%**（单 run） | 105 / 482 | ~74.2s | ~1,092K |
| 用户基准（参照） | 1 | 10.5%（51/484） | — | — | — |

### Lite 500 domain 分布（冻结快照）

| domain | case 数 | 占比 | | domain | case 数 | 占比 |
|:--|:--:|:--:|:--|:--|:--:|:--:|
| spice_sim | 116 | 23.2% | | waveform | 24 | 4.8% |
| schematic_netlist | 69 | 13.8% | | analog_context | 23 | 4.6% |
| physical_verify | 67 | 13.4% | | layout_virtuoso | 23 | 4.6% |
| digital | 38 | 7.6% | | eda_other | 22 | 4.4% |
| verification | 34 | 6.8% | | characterization | 18 | 3.6% |
| layout_aether | 29 | 5.8% | | pg_layout | 14 | 2.8% |
| | | | | pnr_signoff | 13 | 2.6% |

**口径说明**：数据取自 EDA-Flow-Bench 仓库（`/nasdata/app.e0031982/code/EDA-Flow-Bench`）截至 2026-11-23 10:30。Pass@1 = 通过 case 自带 `check.py` 判分的 case 数 / 500。doubao 三组与 deepseek r1 均为 clean 轮（无 FUSE / providers.json 错配），r2 进行中未计入。token 数据从 per-case `cline_session.jsonl` 的 `aggregateUsage` 字段聚合，`totalCost=0`（内部 gateway 不计费）故只报 token 不报 dollar。墙钟 = batch 起跑 ~ summary.log 100% 行 + 15min buffer。11-19 22:58 起跑的 `run_batch_20261119_225802`（2.37%）因起跑时 `providers.json` 仍是旧配置 + agent 自加 `--skip-done` 跑 422/500，**作废不引用**。

## 4. 风险与阻塞

**风险 / 阻塞 1：deepseek 3-run 未收口。** r2 跑中（209/500，pass 41，early ~19.6%），r3 待 r2 收口后自动起，预计 **11-24 上午全完**。3-run 全完后才能做 deepseek vs doubao-pro 的 **McNemar 配对检验**（逐题 pass/fail 对齐，报 b/c + p 值）+ 汇总报告 `report_edafb_lite500_dsv4pro_eval_zh.html`。论文 §6 强模型对比段被阻塞。

**风险 / 阻塞 2：ICML 论文 §6 18 处 `\TBD` 待回填。** 令纪律要求"3-run 出来先报数，**等用户裁定才回填**"，agent 不自动改论文。当前 §6 主结果段（4 模型 Pass@1）、配对检验表、成本-能力象限、失败分类矩阵均阻塞。冻结口径宏（`\LiteSet` / `\Neval` / `\MzeroPass` / `\ScriptPass`）已就位，回填时优先改宏而非硬编码。

**风险 / 阻塞 3：BaiZe 预训练 ckpt 未收敛（ETA 2026-12-25）。** posttrain 正式 SFT/RL 的硬前置；当前用 MiniCPM5-2B 替身做方法探索，正式结果需等 ckpt。vision 线用 Qwen3.5-2B 替身多模态基模同步探索中。

**风险 / 阻塞 4：多线并发 git 冲突。** designflow 4 shard + zhulong + vision + posttrain 共用同一 NFS repo，常遇 `index.lock` 并发冲突，需 retry（sleep 6-8s × 6-8 次）+ `git pull --rebase --autostash` 后再 push。已建立隔离 push 工作流（`git worktree add --detach /tmp/gitpush_<line> origin/main` → 只 add 本线路径 → push）。

**应对措施**：deepseek 3-run 由 zhulong agent loop（PID 243810）自动串行驱动，r2/r3 收口后自动汇总 + 配对检验；§6 回填待用户裁定后批量改 `main.tex` 宏 + 表格，clean compile 验证（round 3 `grep -ci 'undefined'` = 0）。

## 5. 下月计划

**核心目标 1：deepseek 3-run 收口 + 配对检验。** r2/r3 跑完后，做 deepseek vs doubao-pro McNemar 配对检验（逐题对齐，报 b/c + p 值），交付汇总报告 `report_edafb_lite500_dsv4pro_eval_zh.html`，MEMORY 首行追加 3-run 汇总。（12 月上旬）

**核心目标 2：论文 §6 回填。** 18 处 `\TBD` 替换为真实数据（4 模型 Pass@1 / 配对检验表 / 成本-能力象限 / 失败分类矩阵 / case-study 摘要），优先改 `main.tex` 宏而非硬编码，clean compile（round 3 `grep -ci 'undefined'` = 0、`grep -c '^!'` = 0）。（12 月中旬）

**核心目标 3：评测集持续扩张。** Full 集目标 **3,000+ case**（当前 2,130），保持 13 域覆盖均衡，waveform / analog_context 多模态题保留不降级（用户 11-14 令：需要看图的题保持原形态，让"没有多模态能力"的系统就该 fail）。Lite 500 冻结不动。（12 月底）

**核心目标 4：BaiZe posttrain 接入。** pretrain ckpt 收敛后（ETA 12-25），posttrain 正式 SFT/RL 用 EDA-Flow-Bench 做 L4 领域评测，对比 MiniCPM5-2B 替身基线（6.84% ± 6.12%，`.36.15` + zhulong 口径）。（12 月底启动）

**核心目标 5：harness 改进探索。** 基于 case-study 三种失败模式，探索 harness 层改进（禁联网 / 强制最小迭代 / 沙盒复现 gate），验证"harness 改进比换更强模型更能提分"的假设。（12 月中下旬）

## 6. 请求事项

**需要支持**：
- deepseek 3-run 收口后，**用户裁定是否放行论文 §6 18 处 `\TBD` 回填**（令纪律：3-run 出来先报数，等用户裁定才回填）。
- posttrain 正式训练接入需 **pretrain ckpt**（ETA 2026-12-25），若有延迟需提前同步。
- harness 改进探索（禁联网 / 强制最小迭代 / 沙盒复现 gate）需用户确认是否动 `run_batch.sh` / `run_one.sh` 评测入口（当前冻结口径不许擅改）。

**期望节点**：
- 12 月上旬完成 deepseek 3-run + McNemar 配对检验 + 汇总报告。
- 12 月中旬完成论文 §6 回填 + clean compile，提交 ICML 2027 双盲版。
- 12 月底 Full 集 3,000+ case，posttrain 正式训练启动。
