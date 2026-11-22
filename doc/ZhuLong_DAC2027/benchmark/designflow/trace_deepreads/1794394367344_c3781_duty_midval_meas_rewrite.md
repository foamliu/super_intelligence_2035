# Deepread: c3781 — DutyMidvalMeasRewrite (joeyl @ hfeg0plg53)

- **user**: joeyl (new — no prior cases in shard B)
- **host**: hfeg0plg53 (10.129.35.69), ip also on hfeg0pkn004 (10.129.2.13)
- **session**: `1794394367344_c3781.messages.json` (77 KB, 23 msgs, 22 tool_use)
- **scan**: ssh_eda_search_20261122_172249, mc=4, keywords `netlist:8;hspice:8;schematic:2`
- **domain**: spice_sim / characterization (FineSim/HSPICE duty measure reframe)
- **fetched**: scp 10.129.35.69:/home/joeyl/.cline/data/sessions/1794394367344_c3781/1794394367344_c3781.messages.json

## Real task

用户 joeyl 在 m2701 V0_DDR4 平台 FineSim 仿真下，对 DQS C2C testbench
`/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/3_C2C/4_Tran_RFB.sp`
的 duty 占空比测量块做修改。原 bench 里三个信号（`out1`、`xi_wck_c2c_rfb_2.vout1`、
`xi_wck_c2c_rfb_2.out`）的 duty `.meas` trig/targ 统一用硬编码 `val = 'pvdd/2'` 作穿越电平。
用户要求改成**取该信号在 2n~5.5n 窗口的最大值与最小值相加除以 2** 作为交叉电平（mid-value）。

## Agent 工作（22 tool_use）

1. `read_files` 读 bench（含分页读 measure 块 84-162 行）
2. 尝试 `editor` 直接改原文件 → 被 agent-policy 拦（`/rundata/...` 不在 writableRoots，仅 `/home/joeyl` 可写）
3. `read_files` 读 `agent-policy.json` 确认可写范围
4. 写 Python 脚本 `/home/joeyl/4_Tran_RFB_modify.py`：读原文件（只读）→ 正则替换三个 duty 块 → 写到 `/home/joeyl/4_Tran_RFB_midval.sp`
5. `run_approved_command`（python-runner）执行 → `OK: 3 blocks replaced`
6. `read_files` 验证改写后的 measure 块（153-195 行）
7. 写 `diff_check.py` 做 unified diff → 执行 → 确认只动了 duty 块，其余（stimulus/.tran/.probe/cm_vout AVG/注释 skew 行）逐字不变

## 改写规则（每个 duty 块）

注入三条测量：
```spice
.MEAS max_<leaf>  MAX v(<sig>)  FROM=2n TO=5.5n
.MEAS min_<leaf>  MIN v(<sig>)  FROM=2n TO=5.5n
.MEAS mid_<leaf>  param='(max_<leaf>+min_<leaf>)/2'
```
再把 trig/targ 里的 `val = 'pvdd/2'` 换成 `val = 'mid_<leaf>'`（`<leaf>` = sig 取最后一个 `.` 后片段）。
注释（`*`）的 skew 行不动，`.MEAS cm_vout AVG` 不动。

## 案例化

- **case_id**: `EDA-Eval-DesignFlow-DutyMidvalMeasRewrite-001`
- **reframe**: L1 纯 Python 工具 `duty_midval_rewrite.py --spec <json>`，spec 驱动（bench/window/hardcoded_val/output/report）
- **A（可见）**: 3 信号 DQS C2C bench，window 2n..5.5n，hardcoded `pvdd/2`
- **B（隐藏，不同 scale/values/structure）**: 2 信号 CLK buffer bench（`dqs_p`、`xi_buf.clk_n`），window 1n..4n，hardcoded `pvddq/2`，duty var 用 `tpd/thw` 命名
- **check.py**: 13 条断言（zip/compile/run/report/per-signal MAX/MIN/mid 注入/无残留硬编码 val/duty param 保留/非 duty 行保留/反硬编码 window+val+n_signals/3-seed 确定性）
- **negatives**: empty / print-only / core-removed，三假全 FAIL
- **自验**: ref self-test PASS；3 negatives 全 FAIL
