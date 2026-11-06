# Deepread — 1785757804161_buv7m (e0014566 @ hfeg0pkn001, mc=182)

**Session**: `/home/e0014566/.cline/data/sessions/1785757804161_buv7m/` (848KB, 128 msgs: 73 user / 55 assistant)
**Tools**: 460 virtuoso + 20 cellview + 12 dbCreateInst + 3 calibre (layout_virtuoso / pg_layout)
**Cell**: `testa` @ libName `austin_rscalc2`, process `cxmt10G4plus`, workDir `/proj/train/AI_Virtuoso/workdir/e0014566`

## User intent (3 text turns; turn 1 = A-faithful task statement)
1. **(意图轮, 用作 A 档 prompt 逐字)** 构建 power-network 电阻优化工作流：分析 3 个 skill（rscalc/autovia/powerfill）→ 把 3 个配置文件合并出共有文件（去重 + 防错）→ rscalc 测电阻 → autovia+powerfill 优化版图降电阻 → 写进 prompt_flow.md → 上一步输出=下一步输入 → 目标降幅 + 最大迭代次数写进配置。
2. powerNets 支持为空，空则从 layout RTEXT 自动读取所有 powerNets。**(根因/修复方向轮 → 不作 A 档, 作 hint)**
3. rundir/workdir 应统一成一个工作目录，不必分开。**(根因/修复方向轮 → 不作 A 档, 作 hint)**

## Assistant tool chain (real, on .75 Virtuoso batch)
- 探查 `/home/e0014566/test_layout_rscalc_flow_2/`（3 skill 目录 + rscalc.config + run_autovia_config.il + run_powerfill_config.il + prompt.md）
- 写 `common.config`（共享参数 + 流控 targetReductionPct=30/maxIterations=5 + pwrNets="" + 单 workDir + 名称映射表注释）
- 写 `scripts/gen_flow_configs.py`（合并器：canonical→tool 名称映射、cell 链 base→_av{N}→_pf{N}、workDir 派生 rscalc/autovia 子目录、pwrNets 空→resolved_nets.txt 自动检测）
- 写 `scripts/extract_nets.py`（基线 RsCalc addNets.txt → resolved_nets.txt）+ `scripts/get_max_resistance.py`（.rvn 第12列 max 电阻）
- 写 `prompt_flow.md`（11KB 工作流文档）
- 多轮验证 gen iter0/1/2、pwrNets 空/自动检测、workDir 统一、3 个 skill generator 适配

## Extracted case
**EDA-Eval-DesignFlow-PwrFlowCfgGen-001** (pg_layout, A-faithful, L1-boundary)
- 抽 turn 1 的「合并配置生成器」子任务：交付 `gen_flow_configs.py`，读 common.config + 3 partial 模板 → 写 generated/{3 配置}，含名称映射/cell 链/workDir 派生/pwrNets 自动检测
- A = 真实 4 配置（testa/cxmt10G4plus/pwrNets=""/maxIter=5）；隐藏 B = 合成（vddopt/cxmt7g2pro/pwrNets="vdd! vss!"/maxIter=8，工具参数全异）
- check.py 自包含 A+B 内嵌，15 条 (a)-(o)；ref PASS 15/15 + 5 neg 全 FAIL + §4.9 三假全 FAIL；k=15/15
- 参考解 = 真实 gen_flow_configs.py（9272B，从 trace 直接取，clean）

## Leakage isolation
- check.py 自包含（A+B 内嵌），不进 SUT workdir
- SUT 只见 A 的 4 配置 + task_brief + prompt（turn 1 逐字）；B/参考解/negative 均在 reference/ 不进沙箱
