# 1fxvk 深读笔记 — FineSim timing deck .meas 提取 + 多 corner .mt0 解析 + Fail 溯源

- **trace**: `1790660523598_1fxvk` (rongtaoy @ hfeg0pkn001, mc=166, 151 msgs, keywords hspice:62/netlist:370/schematic:5)
- **domain**: spice_sim
- **shard**: B
- **深读日期**: 2026-11-05
- **状态**: 已合成 case EDA-Eval-DesignFlow-MeasExtractCornerTrace-001（2026-11-05，spice_sim，B档 synthesized，L2 真跑 FineSim -spice，k=15，DEBT:0 清零；1fxvk ledger claimed→case）

## 真实流（用户意图逐字）

rongtaoy 单人单 session 对 DDGOA DDR6 column-timing FineSim 仿真体系做**实物取证**（forensics），全程**无 shell**（用户明确「你无 shell，只能用 list_allowed_files/read_files」），agent 仅读文件给结构化报告。

U0 逐字：「你能理解这个目录是干啥的吗 /proj/ddgoa/V0/workdir/ytzhu/simulation/timing/01-column/fullchip_chk/default_1bank」

U1（核心需求轮，A 档合规候选）逐字节录：「【任务：DDGOA column timing 流程实物取证】…【C. 测量语句与数据样例】1. readtiming_default.sp：提取所有 .meas/.tran/.include 行，每行带行号 2. writetiming_default.sp：同上 3. header_read、header_write 全文 4. 任选一个 corner 的 res/*.mt0 全文 + 对应 *.log 最后 20 行 5. 顶层 data.csv 前 5 行原样粘贴…【D. 汇总链路】…」

U3：「【任务：ddgoaF 仿真库命名语法取证】…你无 shell，只能用 list_allowed_files/read_files」

U4（子技能 B 候选）：「【任务：Fail 性质与 error 溯源】1. read sec0/c10-rd_u_far_mat0/res/ 下 ff-40.log、tt25.log 的头部 30 行：是否同样报 unknown variable（ysaenw/ysaeqn/yioselen/yioloc）？——5 个 corner 若同节点全 error → 系统性问题；若仅 ss130 → 单角损坏 2. …判定 Fail = 仿真失败 还是 pincheck 比对超差」

U8：「读一下 readtiming.sp.meas」

U9：「【任务：网表顶层结构取证（WoW 层级导航）】…」

## A 档选轮判定

- U0 = 提出需求（「这个目录是干啥的」），未给根因/修复 → **A 档合规**，但太泛（"干啥的"非可执行子技能）。
- U1 = 提出取证任务，**未给根因/修复** → A 档合规，但任务是「取证/读文件」非「跑仿真」，子技能需 reframe 为可运行 L2。
- U4 = 用户**已给判定方法**（"全 error→系统性 / 仅 ss130→单角"）→ 违反 A 档选轮规则，不可作 A 档任务说明。
- **结论**：U1 可作 A 档但意图偏 read-only forensics；B 档 synthesized 提取**可运行子技能**更合适。

## 子技能（便携 reframe）

**FineSim timing deck `.meas`/`.tran`/`.include` 静态提取 + 多 corner `.mt0` 解析 + per-corner Fail 溯源（unknown-variable 检测）**

三个可便携子技能：
1. **.meas 静态提取器**：解析 FineSim deck，提取所有 `.meas`/`.tran`/`.include` 行（带行号），分类 measure 名/类型(trig-targ/param/when)/目标信号 → 结构化 meas_statements.json。**反**：naive 只 grep `.meas` 不带行号/不分类类型。
2. **多 corner .mt0 解析 + timing 汇总表**：跑 FineSim 多 corner（.alter 或多 deck）→ 解析每 corner `.mtN` → per-measure 数值 → timing_summary.csv（行=corner，列=measure）。**反**：naive 只读单 corner / 不处理 `.mt0` header 跳过 temper/alter# 列。
3. **Fail 溯源器**：扫描 `.mt0`（measure 值为 error/-1）/ `.log`（`unknown variable`/`undefined`）→ per-corner pass/fail 分类 → 判定系统性(全 corner error) vs 单角损坏 → fail_source.json{corner, measure, error_type, systematic}。**反**：naive 只报"有 error"不分类系统性/单角。

便携 reframe：trace 原走 DDGOA foundry PDK + 115MB netlist + LSF + read-only forensics 不可移植 .75 → 保留「.meas 提取 + 多 corner .mt0 解析 + Fail 溯源」子技能，DUT 用 level-1 Shichman-Hodges 反相器链 + FineSim -spice 多 corner `.alter`（.75 已验证 FineSim V-2023.12-1 可用，.mt0 解析见 PVTvarSpecJudge/McRonMismatch）。

## distinct vs 已有 B spice_sim case

- NetlistTranDeck(j8vf6)=网表+measure 拼接静态生成（无 .mt0 解析、无 Fail 溯源）
- CmdEdgeMeasGen(hgfso)=参数化 .measure deck 生成器/运行器（单 corner，无多 corner .mt0 汇总）
- PVTvarSpecJudge(z6mt7)=.alter 多 corner + variation SPEC 合规判定（无 .meas 静态提取、无 Fail 溯源）
- McRonMismatch(r4p2e)=.md0 MC 汇总行陷阱（MC 非 .alter corner，无 Fail 溯源）
- StimLoopComplianceFix(5kcuw)=stimulus loop 合规改写（非 .meas 提取/无 .mt0 汇总）
- FineSimTbAuditFix(q9r9s)=TB 静态审计三类错误 + 修复（无 .meas 提取/无多 corner .mt0）

**本条 = `.meas` 静态提取(带行号+类型分类) + 多 corner .mt0 → timing 汇总表 + Fail 溯源(系统性 vs 单角)**，shard B 首个「.meas 提取 + corner .mt0 汇总 + Fail 溯源」组合 case，distinct ✓。

## case 设计计划（下轮合成）

**EDA-Eval-DesignFlow-MeasExtractCornerTrace-001**（spice_sim, B 档 synthesized, L2 真跑 FineSim -spice, k≥10 计划）

- **A**（visible）：FineSim deck `inv_chain_A.sp`（4 级反相器链，pvcca=1.2, 2 corner=TT25/SS-40 via .alter），含若干 `.meas tran tpd_*` + 1 个引用未声明 `.param` 的 `.meas`（trap：该 corner measure 落 error）
- **B**（hidden）：`nand2_chain_B.sp`（不同拓扑/命名/pvccb=1.0/3 corner=TT25/FF125/SS-40，不同 measure 名 tpdb_*，2 个 corner 含 unknown-variable error）
- 候选 `meas_extract_corner_trace_ref.py`（CLI <deck.sp> <spec.json> <out_dir>：
  1. 静态解析 deck → 提取 `.meas`/`.tran`/`.include` 行(带行号)+分类 measure 类型/名/目标信号 → `meas_statements.json`
  2. subprocess finesim -spice 跑 deck → 解析每 corner `.mtN`（header 跳 temper/alter#）→ per-corner per-measure 数值 → `timing_summary.csv`
  3. 扫 `.mtN` error 值 + `.log` unknown variable → per-corner pass/fail + 系统性(全 corner error) vs 单角判定 → `fail_source.json`
  4. report.json{meas_statements, n_corners, timing_summary, fail_source, finesim_ran, converged}
- **check.py ≥10 条 a-n 计划**：
  (a) zip+meas_extract_corner_trace.py (b) py_compile (c) B finesim 真跑签名+rc (d) meas_statements 含全 `.meas` 行带行号+类型分类 (e) timing_summary 行数=n_corner_B (f) B 各 corner measure 匹配 GT ±10% (g) fail_source 正确标 error corner (h) 系统性 vs 单角判定正确 (i) 跨输入守卫 rerun A (j) name-agnostic B 名齐 A 名不泄 (k) report schema 完整 (l) 确定性重跑 (m) .meas 提取含 `.tran`/`.include` 行 (n) 反 naive grep-only（无类型分类）
- **6 neg + §4.9 三假 + selftest**

## .75 验证待做（下轮第一件事）

1. probe：FineSim -spice `.alter` 多 corner 跑 level-1 反相器链 → 验证产多个 `.mt0`/`.mt1`（每 alter 一个 .mtN）
2. probe：在 deck 里放一个 `.meas tran x param='undefined_var'` → 验证 FineSim 报 `unknown variable` 且 `.mtN` 对应值为 error/-1
3. 标定 A/B GT → 合成 ref/check/neg → selftest → jsonl → mark case → 清 DEBT:1

## 本轮工作（2026-11-05）

- scouting 14 候选 trace（全部 peek 首条用户意图）：1hq6h/0si6a/sr426/c21e8/6pzrm/af6a0/at2ga/3lvd6/pqeal/ztoza/fux29/e0029495/sagequan/chengk/1fxvk/0si6a 等
- 判定：11 条 false-positive/non-spice（Qt C++ configloader、digital ncsim.trn 波形、LSF env-debug、spice model explain-only、email/file-analysis）→ 已 mark parked
- 选定 1fxvk（rongtaoy, FineSim timing forensics）→ claimed + 本深读
- 未合成、未进 jsonl：DEBT:1，下轮第一件事合成 MeasExtractCornerTrace-001
