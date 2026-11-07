# Trace deepread — 1791963944343_p03c8 (tongfanl @ hfhds201)

**Session**: `1791963944343_p03c8` (dir-based, 138 msgs, 984KB, mtime Oct 15 09:03)
**User**: tongfanl · **Host**: hfhds201 (10.129.32.75, .75 本机, cron 盲区)
**Domain**: spice_sim (DDR6 vecgen_local testbench, sim_vector)
**Shard**: B (spice_char) · **Track**: A-faithful · **Level**: L1
**Case**: EDA-Eval-DesignFlow-ZqPatternTimingAnalyze-001

## 选轮 (A-档)
- **U#0 (idx 0) 任务说明轮**（逐字作 prompt）: 用户粘贴完整 `task ZQ001_normal_check(...) ... endtask`，
  开头 `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local`，结尾问「时，是什么时序关系？」
- 用户提出需求（"帮我看下在该环境下，跑pattern … 是什么时序关系"），**无根因/无修复方向** → 符合 A-档选轮 ✓
- 后续轮 U#137 (ODT 修改问题) **不入 prompt**（含修复方向）

## 金标准 (assistant 分析)
assistant 用 read_files + search_codebase + run_approved_command(python grep) 分段读取
vecgen_local 目录与 ddr6_test.sv / ddr6_timing.sv / ddr6_package.sv / ddr6_model.v /
ddr6_tasks.sv / ddr6_interface.sv / timing_table / timing_load.sv，最终在 **A#136** (8389 chars)
给出完整 ZQ001_normal_check 时序关系分析（11 段）：

### 环境基础
- 仿真框架: DDR6 Vector Generator (vecgen), SystemVerilog
- TB timing mode: `tbcontrol.timingcal="auto"`（自动时序计算）
- 时钟频率: 由 `timing.tCK` 决定（典型 250ps=8Gbps / 192ps=10.4Gbps）
- 时序参数: 从 `timing_table` 自动读取（23 个 speedgrade）

### 核心时序机制
1. **DeselectT 时间转换**: `nnop = (n - n%timing.tCK) / timing.tCK` — 绝对时间(ps)→CK 周期数
   - `0.5*1000_000/2 = 250,000ps = 250ns`；`750_000` = 750ns；`1000_000` = 1us
2. **timingcal="auto"**: 每命令前 `cal_nops(.cmd(...))` 调 `X2xxx(enops)` 检查上次各类命令到此命令的最小时序（tMRD/tRAS+tRPpb/RD-to-MRR…），返回需插入的 NOP 周期数
3. **MRSetting 是本地 shadow 寄存器操作**: 不经 CA 总线，不消耗仿真时间，直接更新 `ShareDRIVER.mr_direct`/`mr_page`

### Pattern 逐段时序 (11 段)
- ① CLK_SYNC_OFF + DeselectT 250ns (0.5*1000_000/2)
- ② Load_Mode(MA_func_mode_clr) 清 ZQCAL_Latch (MR6 OP[0]=1) — 等待 tMRD
- ③ Active → Write (tRCD_W 约束, BL24)
- ④ Load_Mode(MR7, op=8'hFF, op_mark=8'b0000_0100) **ZQ Reset (OP[2]=1)** + DeselectT 750ns
  - 自清除: functional_mode_enable 调 MRSetting 清 OP[2]/OP[3]
- ⑤ MRSetting(MR7, op=8'b0000_0011, op_mark=8'b0000_1111) 本地设 ZQ Initiation (OP[0]=1, OP[1]=1) + MRR(MR7) 读 ZQUF
- ⑥ Active → Read — **ZQUF=1 时预期 DQ error** (ZQ 校准未完成，DQ 驱动强度/ODT 可能不正确)
- ⑦ 清 ZQCAL_Latch + Active → Read — **ZQUF=0 时 DQ pass**
- ⑧ MRSetting 清 ZQUF + MRR(MR7) 读 ZQUF=0
- ⑨ Load_Mode(MR7, op_mark=8'b0000_1000) **ZQ Stop (OP[3]=1)** + MRR + 清 Stop + DeselectT 1us (tZQCAL≥1500ns)
- ⑩ MRSetting 设 ZQUF + MRR + 清 Latch + MRR + 清 ZQUF + Active→Read (DQ pass)
- ⑪ 收尾: Load_Mode ZQ Reset/Stop + DeselectT 1us + Load_Mode ZQ Reset

### 关键 ZQ 语义 (MR7)
- **OP[2] = ZQ Reset** (op_mark bit2) — 触发 DRAM 内部 ZQ 校准电阻复位 (~1us)
- **OP[3] = ZQ Stop** (op_mark bit3) — 停止 ZQ 校准; 清除后重新校准需 tZQCAL4_min(1500ns)~tZQCAL16_min(6us)
- **OP[0] = ZQ Initiation / ZQUF** (op_mark bit0) — ZQ Update Flag; ZQUF=1→读期望 DQ error，ZQUF=0→DQ pass
- MRSetting 操作 MR7 为本地零延时；Load_Mode(MRW) 操作 MR7 经 CA 总线消耗 tMRD

## 通用化 (合成)
`analyze_zq_pattern_timing.py <test.sv> -o out.json` — 解析任意 SystemVerilog DDR6 vecgen
pattern `task <NAME>(...) ... endtask`，提取:
- task_name · params[{name,type,width,default,has_default}] · param_count · begin_block_name
- pattern_name (from `pattern_name="..."`) · timingcal (from `tbcontrol.timingcal="..."`)
- command_sequence: 有序(含重复)子任务调用链 (CLK_SYNC_OFF/DeselectT/Load_Mode/Active/Write/Read/MRR/MRSetting…)
- deselectt_waits_ns: 每个 DeselectT(.n(EXPR)) 等待, EXPR 求值(ps)→ns (strip `_` 数字分隔后受限 eval)
- zq_mr7_ops: Load_Mode/MRSetting 调 MR7 的操作, op_mark 解码为 {bit0_zquf, bit2_reset, bit3_stop}
- mrsetting_count · mrr_count · has_endtask · conclusion

跳过 `//` 行注释中 task 伪匹配; 按 `[]/()` 深度切分参数; `.IDENT(` port-arg 排除;
op_mark 支持 `8'b..._...` 二进制与 `8'h..` 十六进制 (bit0=LSB)。

## 资产
- **A** = `A_test.sv`: 真实 ZQ001_normal_check task (用户 U#0 逐字粘贴, 7 参数/begin:ZQ001_normal_check_task/
  11 段命令链/4 个 DeselectT 等待[250,750,1000,1000]ns/10 个 MR7 ZQ op 含 Reset+Stop+ZQUF/endtask)
- **hidden B** = `B_test.sv`: 合成 `task REF_double_refresh_check` (4 参数/begin:REF_double_refresh_check_task/
  pattern_name="REF_double_refresh_check"/timingcal="auto"/DeselectT 等待[200,500]ns/无 CLK_SYNC_OFF 无 Write/
  MR7 op 仅 bit0_zquf 无 Reset/Stop/不含任何 A 标记)

## 判分 (16 断言 a-p)
含交叉输入守卫 (B→task_name/pattern_name=REF_double_refresh_check + waits=[200,500],
A→task_name/pattern_name=ZQ001_normal_check + waits 含 750/1000 + zq_mr7_ops 含 bit2_reset & bit3_stop
+ command_sequence 含全部 8 类命令, 挡硬编码任一答案) +
A-only 泄漏闸门 (ZQ001_normal_check/ZQ001 不入 B 输出) + 幂等 sha256。

## 自验
- ref PASS 16/16 ✓
- 4 negative (naive_hardcode_a FAIL f / always_pass FAIL j / empty_shell FAIL e / core_deleted FAIL i) 全 FAIL distinct ✓
- negative_selftest NEG_RC=0 ✓
- §4.9 三假 (空壳 FAIL e / 打印期望 FAIL j / 删核心 FAIL i) 全 FAIL ✓
- 断言闸门 k_rationale=16 == k_check=16 ≥ 8 ✓
- jsonl test==disk check.py roundtrip sha a598d195ba55 ✓ → 追加 EDA-Eval-DesignFlow_B.jsonl (158→159)
- mark ledger (spice_sim 124→125, case 160→161)

## 11-05 重扫令履行
- 11-08 cron log `eda_trace_20261108.log` (Nov 8 00:00, 2889 qualifying sessions) 解析: 86 strict spice-dom
  候选 (spice≥10, ratio≥0.35, mc≥30) **全部已在 ledgers** (0 新增 from strict filter)
- hfhds201 cron 盲区本地 diff: 258 sessions, 70 in-ledger, 188 NOT-in-ledger → peek top spice-user 候选
- 选 p03c8 (tongfanl, 984KB, spice_sim) 为新候选 from hfhds201 盲区
- 详见 designflow/rescan_1108_0507.md
