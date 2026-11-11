# 深读笔记 — f7v4d（ruisongs @ hfeg0pfn090, mc=96, digital）

- session: `1792113930059_f7v4d`（路径嵌套：`/home/ruisongs/.cline/data/sessions/1792113930059_f7v4d/1792113930059_f7v4d.messages.json`，946KB / 171 msgs / 88 user + 83 assistant）
- 工具：editor×34 + run_approved_command×34（python-runner 跑每个 analyze_*.py）
- 真实场景：DDR5 `dca_m1_reset_sre` 仿真，比较两个 xrun.log（1008 失败 vs 1001_V0 通过），怀疑 `+define+LOW_SPEED / CATM_AUTOCHECK / CSTM_AUTOCHECK` 三个宏导致失败。

## 用户意图（真实原话）
- U#1：`/proj/.../1008/.../xrun.log` 和 `/proj/.../1001_V0/.../xrun.log`，怀疑多了 `LOW_SPEED / CATM_AUTOCHECK / CSTM_AUTOCHECK` 三个 define 导致报错，分析一下。
- U#29：结合 `0915net/.../dca_m1_reset_sre_0916_48`（更早的基线）一起分析。
- U#34：不能定位到真正问题吗？（用户要求根因，不止"相关"）
- U#51：仿真波形第一次 reset 后 MRR，DQ 压根没输出，一直 z 态。
- U#60：在 `1008/ruisong` 下重跑了两个，有一个正在跑，分析跑完的那两个，都是正常的，为什么。
- U#69：只去掉 CSTM_AUTOCHECK，不是跑了？（关键控制实验）
- U#74：跑完了，分析一下。

## agent 工具链（34 个 analyze_*.py 一次性诊断脚本）
analyze_xrun{,2,3}.py → analyze_src{,2}.py → analyze_diff.py → analyze_low.py → analyze_autocheck.py → analyze_pkg.py → final_check.py → analyze_0916.py → deep1-8.py → dq_oe.py / rd_en.py / mrr.py / io_oe.py → analyze_1016{,2}.py → diff_1016.py → short_config.py / short_cfg.py → define_lines.py → configdut.py → find_def.py / grep_cfg.py / pattern_reset.py / find_pattern.py

## 根因链（agent 最终结论）
1. **三个 define 不是编译/elab 报错根源**——两份 log 都能 `$finish`、Job done，无 xmelab `*E`。
2. 真正不同的、只在 1008 出现的：**DQ/DQS Hi-Z 比对失败**（A_Compare `DUT_DQ: z vs Exp_DQ: z10101010`；A_Summary `DQ_Err:18 / DQS_t_Err:12 / DQS_c_Err:12`，Failed Pattern:1）。
3. **三份对比收敛到两个宏**：
   | 运行 | LOW_SPEED | CSTM_AUTOCHECK | CATM_AUTOCHECK | Pattern |
   |---|---|---|---|---|
   | 0916_48 (baseline) | ✗ | ✗ | ✗ | PASS |
   | 1001_V0 | ✗ | ✗ | ✗ | PASS |
   | 1008 (坏) | ✓ | ✓ | ✓ | **FAIL** |
   | 1016_1 (控制：去 CSTM) | ✓ | ✗ | ✓ | **PASS** ← 隔离 CSTM |
4. **CATM_AUTOCHECK 是"死宏"**——TB 源码里没有任何正向 `` `ifdef CATM_AUTOCHECK `` 分支。
5. **LOW_SPEED 是 live 宏但非元凶**——1016_1 带 LOW_SPEED 仍 PASS（被控制实验排除）。
6. **CSTM_AUTOCHECK 是真元凶**——live 宏（`` `ifdef CSTM_AUTOCHECK ``），出现在所有失败 run、缺席所有通过 run；机理：影响 DQ OE 使能 → MRR 阶段 DQ 保持 Hi-Z → 比对失败。代码位置 `compare_tasks.sv:572/680/720`、`ddr5_package.sv:1258`、`timing_load.sv:5796-5896`。

## A_Summary.rpt 真实格式
```
Global_Seed is 2083196418

==================================================
        DQ_Err:18, DQS_t_Err:12, DQS_c_Err:12, DM_Err:0, ..., DCA_ERR:0, PDRTT_Err:0
dca_m1_reset_sre        DQ_Err:18, DQS_t_Err:12, ...
==================================================

            ~~~~~~~~~~~~~~~~~~~~
            Total Pattern:  1
            Failed Pattern: 1
            Passed Pattern: 0
            ~~~~~~~~~~~~~~~~~~~~
```
字段族：`DQ_Err / DQS_t_Err / DQS_c_Err / DM_Err / TDQ_Err / LBDQ_Err / LBDQS_Err / DQODT_Err / DQSODT_Err / DMODT_Err / LBODT_Err / TDQSODT_Err / CACSCKODT_Err / Alert_Err / DCA_ERR / PDRTT_Err`。

## xrun.log +define+ 格式
编译命令块里 `\t+define+NAME` 或 `\t+define+NAME=VALUE`（如 `+define+PROJECTNAME=WOWTOP_1C2A`）。

## case 合成（r409, B档 synthesized）
- **case ID**：`EDA-Eval-DesignFlow-SimDefineDeltaDiag-001`（digital L1 spec-driven-gen / log-parser+cross-check）
- **deliverable**：`sim_define_diag.py`（纯 stdlib，`--case-dir <dir> --out <report.json>`）——从多个 run 的 xrun.log 抽 `+define+` 宏、从 A_Summary.rpt 抽 `<FIELD>_Err:<int>` + Pattern 计数、扫 TB 源文件 `` `ifdef `` 判 live/dead 宏、用"出现在所有失败 + 缺席所有通过"逻辑定 culprit，附 exonerated 原因。
- **A（可见，3 run）**：SLOW_MODE(benign live)/AUX_CHECK(dead)/MAIN_CHECK(culprit)，错误字段 Cmd_Err/CA_Err。
- **B（隐藏，4 run，含 b_confirm 隔离 culprit 单独）**：POWER_DOWN(benign live)/DBG_AUTOCHECK(dead)/PARITY_AUTOCHECK(culprit)，错误字段 Wr_Err/Rd_Err。
- **与 OdtErrStatScan-001 区别**：OdtErrStatScan 是 ODT 字段错误统计 + pin-kind 交叉核对；本 case 是 **+define 增量 + dead-macro 检测 + 控制实验三角定位 culprit**，全新 archetype。
- **k_check = 17**（a-q_rando），断言闸门 k_rationale == 17 ✓。自验：ref PASS 17/17，4 negative 全 FAIL，§4.9(a)(b)(c) FAIL，A/B 不同（run 数/名/define/错误字段/culprit/dead 全不同）。

## 资产/可达性
- 真实 sim 目录在 `/proj/drvsa/...` 与 `/rundata/drvsa/...`（agent 脚本里见 /rundata，用户原话 /proj，疑符号链接）。本 case 为 B档 synthesized，fixture 全部在本仓 `assets/.../base_A` + `hidden/base_B` 下，不依赖 .75 可达性。
