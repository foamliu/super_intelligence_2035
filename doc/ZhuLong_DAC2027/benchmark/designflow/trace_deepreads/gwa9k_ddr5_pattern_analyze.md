# trace_deepread: gwa9k — DDR5 pattern `csgeardown.v` 分析

- **session**: `1792044781149_gwa9k`（sijialv @ 10.129.32.46, mc=6, 6 msgs, 23KB）
- **scan**: mc59_apure_liveness_r794.tsv（A-pure, ALIVE via subdir liveness r794）
- **domain**: verification（DDR5 testbench pattern task；keywords verilog:7）
- **真实用户意图**：用户在 cline 里贴路径
  `@/proj/drvqa/V0/sim/verilog/ddr5_tb/patterns/cmds_csgeardown/csgeardown.v`
  并说「读一下这个文件」，随后又发「@csgeardown.v」（意图：进一步解读/确认）。
- **agent 实际做了什么**（msg 1-4）：
  1. `get_agent_policy_status` + `read_files` 读 /proj/drvqa/.../csgeardown.v（71 行）
  2. 把全文带行号回显，并给出结构化解读：
     - `task csgeardown()`，DDR5 CS-gate-down / 自刷新测试 pattern
     - 随机地址变量 `cmd_cancel_rand_bg/ba/row/col`（bit[ BG_BITS/BK_BITS/COL_ADDR_BITS/ROW_ADDR_BITS-1:0]）
     - 4 个子 pattern：`SREF_multi`（L17-38，6× Load_Mode(MR13)+Sref(tck_change)）/
       `SRE`（L39-47，2× 裸 Sref()）/ `SREF_SRE`（L48-60，tck_change 与裸 Sref 交替）/
       `SREFoff_SREon_test`（L61-69，SREF off 再 SRE on）
     - 命令序列 Active/Write/Read/Precharge/Load_Mode/Sref
     - **发现第 67 行笔误**：`Active(.bg(cmd_cancel_rand_bg), .ba(cmd_cancel_rand_bg), ...)`
       —— `.ba()` 实参应为 `cmd_cancel_rand_ba`，错写成 `cmd_cancel_rand_bg`
- **可造性判定**：analysis-Q&A（用户「读一下这个文件」= 读+解读），按顶部「任务初衷」属合法
  真实用户意图。/proj/drvqa 对 .75-side e0031982 身份 Permission denied（agent 当年以 sijialv
  本机身份读到的），故采用 §5 produce-task reframe + B档 synthesized hidden-B。
- **case 形态**（EDA-Eval-DesignFlow-Ddr5PatternAnalyze-001，verification，k=17/17）：
  - 交付 = `analyze_ddr5_pattern.py`（stdlib，config 驱动），对一个 DDR5 pattern task
    做静态结构分析，输出 11 字段 JSON 报告（task_name / line_count / pattern_name /
    rand_vars / rand_var_types / sub_patterns / command_counts / command_sequence /
    load_mode_calls / sref_calls / anomalies）。
  - A（trace-faithful）= `csgeardown.v`（71 行原文件，去掉 agent 加的「注：此处实参笔误」
    注释，使笔误必须靠结构检测而非字符串搜索）+ `config_a.json` + prompt（用户原话）+
    task_brief（11 字段规格 + 笔误判定规则）。
  - B（hidden, synthesized）= `csreadtrain.v`（44 行，3 子 pattern READ_TRAIN/WRITE_LVL/ZQCAL，
    不同命令序列、Load_Mode(MR14/MR15) 参数，第 33 行 `.bg(cmd_cancel_rand_col)` 笔误）。
  - check.py 17 独立断言：①zip+脚本 ②py_compile+stdlib ③B 上 exit0+合法 JSON
    ④-⑭ 11 字段 ground-truth ⑮确定性 3seed ⑯反硬编码(B token 必现/A token 必不现)
    ⑰非退化≥200B。
  - ref PASS 17/17 + 4 neg 全 FAIL（empty/print_only/hardcode_a/core_deleted）+ §4.9 a/b/c FAIL。
- **ledger**: gwa9k parked → case（EDA-Eval-DesignFlow-Ddr5PatternAnalyze-001）
