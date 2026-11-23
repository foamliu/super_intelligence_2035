# r1087 deepread — vmchs (eric1ch) LPDDR6 CS-training case × JEDEC 分解

- session: `1795403697427_vmchs.messages.json`
- user: eric1ch @ hfeg0pkn003 (10.129.2.12)
- match_count: 70；keywords: verilog:648;cadence:6;netlist:1;analog:1 → **A-pure verification**
- 72 msgs / 459KB；agent=lead；2026-11-23

## 用户真实意图（3 轮）

1. **MSG0**：写 LPDDR6 test plan，环境有 3 支 case（cs_training/cst_shmoo/cstm_csp），要把 tb 做的事和 JEDEC feature 对应。给 wrrd_sequence 示例格式（JEDEC ref / feature / description / cover point / sequence / data path / check list: pass criterion + auto check[dq_compare/rdqs_t_compare/rdqs_c_compare/alert_compare/dutmonitor_compare] + eye check）。
2. **MSG21**：把 3 支 case 分解、与 JEDEC 一一对应。例 `cst_ts_scan()` ↔ 4.2.1.4 切频验证。三支共用 `CSTraining()` ↔ 4.2.1 CSTM 三阶段，验证角度不同。
3. **MSG55**：单文件交付 `LPDDR6_cs_training_cases_decomposed.md` 太大打不开，**按章节拆成多个 file 交付**。

## assistant 工具链（真实可溯源）

- skill `lpddr6-jedec-kg`（KG：procedures/commands/timing_parameters/rules.yaml，章节溯源带 Table provenance）+ `continuous-learning`
- read_files：`cs_training.run/.inc`、`cst_shmoo.run`、`cstm_csp.run`、`patterns/function/cmds_cst/*.v/.sv`（cst_ts_scan.sv/cst_pat_err.sv/cmds_cst.inc/38 CST pattern）、`lpddr6_test.sv` task `CSTraining()`（行 10385，CSTM Entry/Sequence/Exit + cs_vref±3 扫描 + dqe_compare 回读）
- editor 写查询脚本 query_wrrd.py/query_commands.py/query_cst_kb.py/grep_cst.py，run_approved_command(python-runner) 跑；用完清理
- 交付：`LPDDR6_cs_training_cases_decomposed.md`（总映射表 + 各 case + 共享 CSTraining + 落回 testplan）→ 拆 7 文件：`CST_分解_00_总纲README/01_总映射表/02_1_cs_training/02_2_cst_shmoo/02_3_cstm_csp/03_共享CSTraining子程序/04_落回testplan`

## 关键事实（造题用）

- `cst_ts_scan()` = 14 档 TS_1600..TS_12800 连调 → 4.2.1.4 切频（FSP 全覆盖）
- `cst_pat_err()` = margin/DCD/随机脉宽注错判成败 → 4.2.1.2 CSTM Sequence fault injection
- `CSTraining()` 共享任务 → 4.2.1 CSTM full flow（Entry 4.2.1.1 / Sequence 4.2.1.2 / Exit 4.2.1.3）
- `cst_shmoo` = cs_vref 扫窗口裕量；`cstm_csp` = cp_cycles 5 相位采样

## 造题形态（A-档 trace-faithful produce-task）

`CstCaseJedecDecomposeProduce-001` [A-domain verification, L2]：把"分解 3 支 case ↔ JEDEC + 按章节拆分交付"沉淀成可复用编排器 `cst_decompose.py`（manifest JSON + KG JSON → mapping.json + 章节拆分 md + submit.zip）。匹配规则 first-match-wins regex（procedure_map 列表顺序）。hidden-B 用 Write-Read training 域（wr_training/wrt_shmoo/wrtm_dqp，WRTraining，4.3.1.x），与 A 零 token 相交。

- k=12 断言（py_compile + exit0 + mapping schema + 条数 + 正确性 oracle + 章节齐全 + index 列表 + master 表 + anti-hardcode 无 A token + shared_task 引用 + determinism 3x md5）
- 自验：ref PASS 12/12；§4.9 三假（empty/print-only/core-deleted）全 FAIL；neg_selftest 3/3 FAIL + ref PASS
- eda_flow：open_session → ssh 10.129.2.12 cat messages.json（subdir 路径 sessions/<sid>/<sid>.messages.json 确认）→ close_session cleaned
- build A 518→519
