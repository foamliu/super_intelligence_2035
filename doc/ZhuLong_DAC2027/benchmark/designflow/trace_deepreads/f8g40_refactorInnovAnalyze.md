# 深读笔记 — f8g40 (RefactorInnovAnalyze)

- **session**: `1791448973775_f8g40.messages.json` (26 msgs, 674KB)
- **user / host**: rongjiez@hfeg0pkn005
- **match_count**: 27 (eda_other 域)
- **ledger 状态**: claimed (r240) → case `EDA-Eval-DesignFlow-RefactorInnovAnalyze-001`

## U#0 逐字原文 (A档任务说明)

> @runModelQA.pl @runModelQA_new.pl runModelQA_new.pl是我对原始代码runModelQA.pl进行重构得到的新代码，请你仔细分析这两个文件，给出我的新代码到技术突破与创新，例如新的代码支持primesim hspice nanospice finesim多种仿真器

纯目标轮：用户给出旧/新两个 Perl 文件，要求分析重构带来的技术突破与创新，仅举例「多仿真器支持」一个维度，未指明输出格式/结构/具体维度清单 → A档 faithful（用 verbatim 原文作 prompt）。

## 真实 A 文件事实 (grep 验证)

| 文件 | 行数 | 仿真器命中 | sub 数 | 关键结构 |
|---|---|---|---|---|
| `runModelQA.pl` (旧) | 3042 | finesim(12)+primesim(9) | 41 | `generate_*_netlist`(5 个生成器)、`run_simulation`(2 分支 ngspice/finesim)、`read_cfg`、6 层嵌套 main |
| `runModelQA_new.pl` (新) | 1630 | finesim(14)+primesim(7)+hspice(5)+nanospice(4) | 48 | `build_testbench_*`(模块化 builder)、`slurp_cfg`/`getSSD`/`getPVT`、`runSimulation`(统一适配器)、`parse_result_generic` |

新增仿真器：hspice、nanospice（旧文件 0 命中 → 新文件各 5/4 命中）。

## assistant 真实方法论 (msg 序列)

1. U#0 给出两个文件 → assistant 读取并做行/sim/sub 统计
2. 产出 6 维度创新分析：(1) 多仿真器统一适配 (2) 代码精简(3042→1630, 46.4% 缩减) (3) 模块化 testbench builder (4) 配置驱动管线(slurp_cfg/getSSD/getPVT) (5) 通用结果解析(parse_result_generic) (6) 扁平化管线 vs 旧 6 层嵌套
3. 后续轮次产出 PPT 汇报要点（用户接受，无修订要求）

## gold 泛化方法论

assistant 的分析可泛化为一个 config 驱动的 Python 脚本 `analyze_refactor.py`：
- 输入 `config.json = {old_file, new_file, simulators:[names]}`
- 通用统计：行数、sub 计数(`^sub \w+`)、仿真器命中(word-boundary, 从 config 的 simulators 列表检测，**非硬编码**)
- 6 维度创新识别：多仿真器扩展 / 代码缩减 / 模块化 builder / 配置驱动 / 通用解析 / 管线扁平化
- 输出结构化 JSON：`{summary, innovations[], architecture}`

**关键去硬编码**：仿真器名清单由 config 传入，脚本源码不含任何具体仿真器名字 → 满足反硬编码守卫。

## 隐藏输入设计

| 输入 | 旧文件 | 新文件 | 旧 sims | 新 sims | 结构对立点 |
|---|---|---|---|---|---|
| **B** (主判分) | `old_modelqa_b.pl`(112 行, ngspice 单体) | `new_modelqa_b.pl`(106 行, 4 仿真器模块化) | ngspice | ngspice,xyce,qucs,ltspice | ngspice→4 sim, builder 分解, slurp_cfg |
| **B'** (交叉输入守卫) | `old_powercheck_bp.pl`(10 行, spyglass) | `new_powercheck_bp.pl`(28 行, 4 工具) | spyglass | spyglass,joules,lint_erp,skyhawk | 不同域(功耗检查 vs 模型 QA), 不同工具集 |

B' 的新仿真器集 (spyglass/joules/lint_erp/skyhawk) 与 B (ngspice/xyce/qucs/ltspice) 完全不同 → 证明候选非硬编码到某一组答案。

## check.py 14 条独立断言 (a-n)

| # | 条件 | 独立失败点 |
|---|---|---|
| a | submit.zip 合法且含 analyze_refactor.py | zip 损坏/缺文件 |
| b | analyze_refactor.py 经 py_compile 编译通过 | 语法错误 |
| c | [B 子进程] 候选在 config_b.json 上运行 exit 0 且输出合法 JSON | 运行崩溃/非 JSON |
| d | [B] summary.old_lines == 旧文件实际 wc -l | 行数错 |
| e | [B] summary.new_lines == 新文件实际 wc -l | 行数错 |
| f | [B] summary.old_simulators == [ngspice] | 旧 sim 检测错 |
| g | [B] summary.new_simulators == [ngspice,xyce,qucs,ltspice] | 新 sim 检测错 |
| h | [B] summary.simulators_added == [xyce,qucs,ltspice] | 增量算错 |
| i | [B] line_reduction_pct 与 (1-new/old)*100 偏差 ≤0.5 | 缩减率算错 |
| j | innovations 非空 list 且 ≥4 条 | 创新识别不足 |
| k | 每条 innovation 含键 dimension/old_approach/new_approach/evidence | 结构缺键 |
| l | architecture.old_sub_count & new_sub_count 为 int 且 new≥old | sub 计数错 |
| m | 反硬编码：B 的 added sim 名(xyce/qucs/ltspice) 不在候选源码出现 | 硬编码答案 |
| n | [B' 交叉输入守卫] 在 config_bp.json 上重跑, new_simulators == [spyglass,joules,lint_erp,skyhawk] 且异于 B | 跨输入失效 |

k=14 ≥ 8，闸门 PASS。

## 自验结果

- REF `reference_submit.zip` (analyze_refactor.py) → check() PASS 14/14 ✓
- §4.9 三假提交全 FAIL：
  - (a) 空壳 `negative_naive_noop.zip` → FAIL {c,n}
  - (b) 只 print 期望串 `negative_print_expected_stub.zip` → FAIL {m,n}
  - (c) 参考解删核心 `negative_core_deleted.zip` → FAIL {d,e,f,g,h,i,j,n}
- `negative_selftest.py` → PASS, 4 negatives 全 FAIL, 11 distinct conds {a,c,d,e,f,g,h,i,j,m,n} ≥3 ✓
- 额外 negative `negative_missing_script.zip` → FAIL {a}
- test_sha8 = ec068dff
