# r871 deepread: exucf — LPDDR6 dejoa/decqa TB task analysis

**session**: 1794963500274_exucf (eva1li@hfeg0plg74, 10.129.8.x, mc123)
**scan**: ssh_eda_search_20261120_145529, verilog:886/netlist:94/analog:168 — A-pure (digital/verification)
**file**: /home/eva1li/.cline/data/sessions/1794963500274_exucf/1794963500274_exucf.messages.json (1.04MB, 236 msgs, ALIVE on plg74)
**status**: DEBT — deepread done, synthesis deferred to next round

## User turns (12 distinct questions/tasks)

| U# | type | intent |
|----|------|--------|
| U#0 | analysis-Q&A | meaning of `proj_voltage_monitors.tbctrlmonitors.errforcebit` |
| U#25 | analysis-Q&A | meaning of `Load_Mode(.ma(MA_Link_ECCEDC_Fault_W),...)` in link_ecc.run |
| U#51 | analysis-Q&A | which MR is `MA_Wr_Link_ECC_SBE_CA_W` |
| U#53/U#105 | produce-task | extract all task names from `*_run` files + usage (2-col table) |
| U#109 | analysis-Q&A | list `deff_sync(...)` full parameters |
| U#113 | produce-task | full task breakdown with per-parameter usage → markdown deliverable |
| U#117 | produce-task | export table to Excel |
| U#127 | produce-task | add all 130 task names (incl long-tail) as 2nd sheet |
| U#139 | produce-task | backfill usage for all 149 tasks in 2nd sheet |
| U#157 | produce-task | extract overlapping keywords from *.run names → Excel |
| U#177 | produce-task | list all *.run names with numbering → Excel |
| U#188 | produce-task | convert task-analysis process into a cline skill |
| U#216+ | debug-Q&A | diagnose link_ecc sim failure (DQ_Err mismatch) |

## Best case candidates (for synthesis)

### A. U#0/U#24 — errforcebit meaning (analysis-Q&A, A档 trace-faithful)
- **gold (A#24)**: `proj_voltage_monitors.tbctrlmonitors.errforcebit` = LPDDR6 验证 TB 中"强制注入 YIO/ECC 错误"的控制变量。通过把该变量设特定值,让 DUT 在 read 时把写入数据位翻转成错误,验证 EDC/on-die ECC/parity 纠错机制。
  - `proj_voltage_monitors` = 顶层 monitor/接口句柄,从 top.sv 经 `.proj_voltage_monitors(A_proj_monitors_if)` 传入 lpddr6_test (top.sv:136/149)
  - `tbctrlmonitors` = 挂在 proj_voltage_monitors 下的子 monitor 实例
  - `errforcebit` = 错误强制注入位
- A档可行性: 需 fixture 含 proj_special.sv 相关片段 (errforcebit 声明 + 错误注入逻辑)。trace agent 用 grep + read_file 定位。fixture 可从 trace 提取真实代码片段自包含。
- hidden B: 改用 DDR4 dejoa TB 同构改名 (proj_voltage_monitors_B/tbctrlmonitors_B/errforcebit_B 等)

### B. U#25/U#50 — Load_Mode MRW meaning (analysis-Q&A, A档)
- **gold (A#50)**: `Load_Mode(.ma(MA_Link_ECCEDC_Fault_W),.op(OP_Link_ECCEDC_Fault_W_A),.op_mark(OP_Link_ECCEDC_Fault_W_BITS))` = MRW 命令,把 LPDDR6 MR99 OP[1] (Link_ECCEDC_Fault_W) 置 1 = 断言写入端 Link ECC/EDC 故障
  - MA_Link_ECCEDC_Fault_W = MR99 (0x63), 定义于 lpddr6_specdef.sv:6853
  - OP_Link_ECCEDC_Fault_W_A = 置 1 值; _BITS = 掩码 (只改 bit[1]); _NA = 置 0
- A档可行性: fixture 含 link_ecc.run + lpddr6_specdef.sv MR99 定义片段,自包含

### C. U#53/U#105 — extract task names from .run files (produce-task, B档 synthesized)
- 用户要: 拆解 Regressions/function 下 `*_run` 调用的 task 名称 + 用法,2列表格
- gold: 275 .run 文件, 130+ task, 按 8 类分组 (上电/时序, MRW, 存储命令, 低功耗/复位, 测试模式/Fuse, 训练/校准, 修复, 速率/DEFF/ZQ)
- B档: 合成 faithful fixture (少量 .run 文件 + TB source 含 task 定义), check.py 验证提取的 task 名集合 + 分类

## Recommendation
- **U#0/U#24 (errforcebit)** 是最快的 A档 analysis-Q&A,同 r870/r869 范式,k≈10-12
- U#25/U#50 (Load_Mode MRW) 也快,可做 sister-turn 同 U#0
- U#53 (produce-task) 更复杂但判分更有牙 (subprocess 跑提取脚本验输出结构)

## 关键路径发现 (infra 教训)
- cline sessions 现存为**子目录** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`,非扁平文件
- scan summary.tsv 记录的 session_file 名 `<sid>.messages.json` 是目录内文件名,非完整路径
- scp 须用完整路径 `<dir>/<sid>.messages.json`,非 `<sid>.messages.json`
- 11-20 14:55 scan 的部分高 mc 候选 .messages.json 已 rotation 蒸发 (sg8o8/aoe57/fjy8k/t5h98/bax7w 等 NOFILE),但 exucf/vgj4f/c8d7b/ff8hl/siev4 等 ALIVE
