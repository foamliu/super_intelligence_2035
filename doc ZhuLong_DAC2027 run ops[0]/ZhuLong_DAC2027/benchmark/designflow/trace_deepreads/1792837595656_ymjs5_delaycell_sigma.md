# Trace Deepread — 1792837595656_ymjs5 (harrywu / hfeg0plg99, mc=171)

- **session**: `/home/harrywu/.cline/data/sessions/1792837595656_ymjs5/1792837595656_ymjs5.messages.json` (1.75 MB / 255 msgs)
- **user**: harrywu (NEW for shard B; spice_sim 域)
- **tools** (summary.tsv): 863 netlist + 312 hspice + 214 schematic（真跑 finesim/Solido HSMC + netlist 编辑）
- **status**: ❌ **PARKED**（核心子技能非便携）—— 2026-11-03 10:27 ledger `mark --status parked`。

## 用户轮（A-档候选筛查）

- idx 0: 「请恢复我在 …/LowSigma_Delaycell 的延迟单元 Sigma 优化任务。先运行 checkpoint.py 并阅读 RESUME_GUIDE.md … 按 resume_state.json 继续。」→ **resume 轮（依赖上轮状态），🚫 A-档不合格**（前提缺失类失败模式）。
- idx 146: 「隔三个小时检查一次」→ 调度指令，非需求。
- idx 155: 「将上述所有流程固化为 skill…」→ **skill 固化请求**（同 g48nq/j8vf8 拒绝类：skill 撰写，非真跑仿真）。
- idx 192: 「输入：1.delaycell netlist 2.MOS name 3.目标 measure 4.shmoo size step/range；过程：1.生成 MOS 尺寸组合 2.进行标称仿真，得到所有挡位的 delay value 3.用户选择部分仿真进行 solido 蒙卡仿真；输出：给出 sigma 从小到大的表格，并给出对应的所有挡位的 delay value 以及具体 size」→ **✅ 纯需求轮（IO + 过程 + 输出），A-档合规**。但含「用户选择部分仿真进行 solido 蒙卡」交互段 + Solido 依赖。
- idx 214: 「你贴了 skill 文档… 代码审查… run_hsmc.sh 里 Solido 可执行文件路径重复… 修复：VARDES_HOME 应设为目录」→ **用户给出根因+修复**，🚫 A-档不合格。
- idx 250: 「Current task status detection」→ 状态查询。

## 真实流（trace 内）

任务 = 延迟单元 `R_RasVdbiasDlyStd_gut_MC` 中 4 管 **MP0/MN0/MP10/MN15**（XMMP0/XMMN0/XMMP10/XMMN15，ptn_lv/ntn_lv 模型）的 W/L 尺寸 Monte Carlo sigma 优化。工具链：`delaycell_sigma_sweep.py`（one_at_a_time / latin_hypercube / grid / random / bayes 搜索）→ 参数化网表（W/L → `'MP0_w'` 形式 + `.PARAM`）→ **finesim（经 LSF `bsub` 队列 fqueue2h）+ Solido Variation Designer HSMC**（`$VARDES_HOME/variation-designer hsmc`）→ 测 STD0~STD15 delay sigma → `optimization_report.txt` + `results_db.json`（sigma 升序表）。

**trace 大部分是调试 saga**：agent resume 后发现 sweep_work_hs/lhs5 的 Solido HSMC 产 `Sigma = +infinity` / `Samples simulated: 0`（输出常值）。根因排查链：
1. `mis_flag=1` 理论 → 写 `fix_misflag.py` 注入 → 仍失败。
2. 发现 Solido 转换的 netlist 把 `*.param sigmaflag=4.0` 注释掉、`mis_flag` 覆盖回 0 → 失配不生效。
3. 发现真正的 model 失配开关是 `sigmaflag`（model.sp header），且 `sda_sigma_mis_a2_local` 失配参数需直接注入到 4 个目标管的 instance 上。
4. 对照参考 HSMC-14（产有效 sigma=16.15ps）的 corner testbench 比对 mis_flag/sigmaflag 处理差异。
最终诊断写 `RESUME_DIAGNOSIS_20261024.md`，重跑 lhs5 validation。trace 未达调优终态（用户后续转 skill 固化 + 代码审查）。

## 便携性评估 → ❌ 非便携

| 维度 | trace 真实 | .75 可用 | 便携？ |
|---|---|---|---|
| MC 蒙卡引擎 | Solido Variation Designer HSMC | 无 Solido license | ❌ |
| 失配注入 | foundry model.sp `sigmaflag` + `sda_sigma_mis_a2_local` per-instance | 无 foundry model.sp | ❌ |
| 仿真器 | finesim（经 LSF bsub） | HSPICE V-2023.12-SP1-1（无 LSF） | ⚠ HSPICE 有 `.mc` 但需自建 mismatch 模型 |
| 目标管模型 | ptn_lv/ntn_lv（foundry） | level-1 Shichman-Hodges | ⚠ 可降级 |
| 交互段 | 用户选 subset 进 Solido MC | headless 无交互 | ❌ |

**核心子技能** = "4 管 W/L 尺寸 MC sigma 优化" —— 难点 **全部** 集中在 Solido HSMC + foundry 失配模型，二者均非便携。.75 HSPICE `.mc` 可做降级版（自建 level-1 mismatch 分布），但：
- 失配模型是 trace 难点的载体，降级到 level-1 均匀分布 = 把题目难点掏空；
- 便携切片（标称多角 delay sweep + 排序）= **TaperBufOpt-001 已覆盖的 DOE+排序结构**（PDP→delay-spread 仅目标函数不同），distinct 性不足；
- idx 192 的「sigma」语义来自 MC 失配，去掉 MC 后「sigma」退化为多角 std，语义偏离 trace。

## 决策：PARKED（不可逆，不 revisit）

非便携 + 便携切片 distinct 性不足 + A-档唯一合格轮(idx 192)含交互/Solido 段。**不进 case，不重复捡**。

## 候选池补充（下轮选 fresh trace 参考）

本轮 hspice 密度排序（mc≥100, hspice≥15, 排除台账 + g48nq/j8vf6/ymjs5）前 12 去重：
- 1792373056714_2enpk (jasonw, hspice=356, mc=129, hfeg0plg55) — 首轮 meta（"你可以访问哪些目录"/"bsub 运行 hspice"），真任务在 idx25+ 后，**待深读**
- 1790245155745_i5ae7 (jiangbaol, hspice=314, mc=119, hfeg0plg99) — ssh 超时未窥
- 1792722208192_uqv1k (karlwang, hspice=312, mc=113, hfeg0plg71) — 「生成仿真 nicap 值对上电速度影响的 pattern」→ 激励生成，边缘
- 1793155079677_gnmu0 (e0030760, hspice=293, mc=102, hfeg0plg74) — 「仿真 SRAM 蝴蝶曲线」→ SRAM SNM 表征，**与已交付 Sram6tDcChar 重叠**
- 1788919426197_cjcn7 (ming1w, hspice=266, mc=164, hfeg0plg99) — log error 调试 + noisefmax，调试非表征
- 1792411915181_j8f3i (yutongy, hspice=198, mc=221, hfeg0plg53)
- 1792030774508_515eb (zhukaic, hspice=197, mc=149, hfeg0plg94) — zhukaic=OtaAcReport 用户

**下轮第一件事**：深读 2enpk（jasonw，hspice 最密 356，真任务在 meta 轮之后）；若非真跑仿真则 i5ae7 / j8f3i。
